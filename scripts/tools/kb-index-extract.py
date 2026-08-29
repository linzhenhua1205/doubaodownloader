#!/usr/bin/env python3
"""
kb-index-extract.py — 从 index.md / README.md 提取文件列表 + 摘要信息（design-010 V3）。

用途:
    获取知识库文件清单 + 摘要，供后续加工：报告生成、去重检查、检索预索引、
    与 log.md 交叉验证、周报素材等。

来源（--source）:
    index  (默认) : knowledge/index.md — 全局文件索引（默认操作对象），
                    全量文件 + 路径 + 摘要（人工摘要优先，缺省 H1）
    readme        : knowledge/README.md — 人工条目库（文件名+摘要·按日期分节），
                    可经 index.md 关联补全路径（--with-path）

用法:
    python3 scripts/tools/kb-index-extract.py                          # 默认 index.md 全量
    python3 scripts/tools/kb-index-extract.py --source readme          # README.md 条目库
    python3 scripts/tools/kb-index-extract.py --source readme --with-path  # 条目库+补路径
    python3 scripts/tools/kb-index-extract.py --format json            # json / csv / md
    python3 scripts/tools/kb-index-extract.py --output /tmp/x.json     # 输出到文件
    python3 scripts/tools/kb-index-extract.py --since 2026-08-01       # 日期过滤（readme 源）
    python3 scripts/tools/kb-index-extract.py --keyword 模型            # 关键词过滤（文件名+摘要）
    python3 scripts/tools/kb-index-extract.py --star-only              # 只高价值条目（readme 源）
    python3 scripts/tools/kb-index-extract.py --module 03_AI           # 模块过滤（index 源）

规则（design-010）:
    - README.md 条目格式: `- [⭐] `file.md` | 摘要`
    - README.md 不写路径 → 路径由 index.md 关联（--source readme --with-path）
    - 同名多命中: 列出全部路径并在 stderr 警告
"""

import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.shared.kb_index_format import (
    Entry, parse_index, load_index_file, is_excluded_rel,
)

# Windows 控制台编码兼容
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, Exception):
        pass

# ── 路径 ──────────────────────────────────────────────────────────────────────
DEFAULT_README = Path(__file__).resolve().parents[2] / "knowledge" / "README.md"
DEFAULT_GLOBAL_INDEX = Path(__file__).resolve().parents[2] / "knowledge" / "index.md"
# index.md 表格行: | [`file.md`](path) | summary |
INDEX_ROW_RE = re.compile(r"^\|\s*\[`([^`]+)`\]\(([^)#]+\.md)\)\s*\|\s*(.*?)\s*\|\s*$")


def parse_global_index(path: Path) -> list:
    """从 index.md 提取全部 (file, path, summary)。index.md 为默认操作对象。"""
    records = []
    if not path.exists():
        return records
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        m = INDEX_ROW_RE.match(line.strip())
        if not m:
            continue
        fname, rel, summary = m.group(1), m.group(2), m.group(3).strip()
        if is_excluded_rel(rel):
            continue
        records.append({
            "date": None, "file": fname, "summary": summary, "star": False,
            "paths": [rel.replace("\\", "/")],
        })
    return records


# ── index.md 路径映射 ─────────────────────────────────────────────────────────

def build_path_map(global_index: Path) -> dict:
    """
    从 index.md 建立 文件名 → [相对路径] 映射。
    index.md 链接格式: [`xxx.md`](02_rd/xxx.md) 或 [xxx.md](path/xxx.md)
    """
    fname_map: dict = {}
    if not global_index.exists():
        return fname_map
    text = global_index.read_text(encoding='utf-8', errors='replace')
    # 匹配 [..](path.md) 形式的链接，路径以 .md 结尾
    for m in re.finditer(r'\[[^\]]*\]\(([^)#]+\.md)\)', text):
        path = m.group(1).strip()
        # 规范化相对路径（去掉 ./ 前缀）
        path = path.replace('\\', '/')
        while path.startswith('./'):
            path = path[2:]
        if path.startswith(('http://', 'https://')):
            continue
        if is_excluded_rel(path):
            continue
        fname = path.split('/')[-1]
        fname_map.setdefault(fname, [])
        if path not in fname_map[fname]:
            fname_map[fname].append(path)
    return fname_map


def resolve_paths(entry: Entry, fname_map: dict) -> list:
    """解析条目的候选路径：优先精确（文件名匹配），其次目录段匹配。"""
    name = entry.file.replace('\\', '/')
    # 含目录段: dir/name.md → 精确路径匹配
    if '/' in name:
        cand = [p for p in fname_map.get(name.split('/')[-1], []) if p == name]
        if cand:
            return cand
        # 允许目录段为部分前缀（如 02_rd/xxx vs 02_rd/01_product/xxx）
        prefix = name.rsplit('/', 1)[0]
        cand = [p for p in fname_map.get(name.split('/')[-1], []) if p.startswith(prefix)]
        return cand
    return fname_map.get(name, [])


# ── 输出 ──────────────────────────────────────────────────────────────────────

def to_dict(entry: Entry, paths: list) -> dict:
    return {
        "date": entry.date,
        "file": entry.file,
        "summary": entry.summary,
        "star": entry.star,
        "paths": paths,
    }


def render_md(records: list) -> str:
    """输出 Markdown 表格。"""
    out = io.StringIO()
    out.write("| 日期 | 文件 | 摘要 | 路径 |\n")
    out.write("|:-----|:-----|:-----|:-----|\n")
    for r in records:
        star = "⭐ " if r["star"] else ""
        paths = "; ".join(r["paths"]) if r["paths"] else "(未关联)"
        summary = r["summary"].replace('|', '\\|')
        out.write(f"| {r['date'] or '-'} | {star}`{r['file']}` | {summary} | {paths} |\n")
    return out.getvalue()


def render_json(records: list) -> str:
    return json.dumps(records, ensure_ascii=False, indent=2)


def render_csv(records: list) -> str:
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["date", "file", "summary", "star", "paths"])
    for r in records:
        writer.writerow([
            r["date"] or "", r["file"], r["summary"],
            "1" if r["star"] else "0", "; ".join(r["paths"]),
        ])
    return out.getvalue()


# ── 主流程 ────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="从 index.md / README.md 提取文件列表 + 摘要（design-010 V3）")
    ap.add_argument("--source", choices=["index", "readme"], default="index",
                    help="数据源: index=index.md 全局索引（默认，全量）; readme=README.md 条目库")
    ap.add_argument("--readme", default=str(DEFAULT_README), help="README.md 路径（默认 knowledge/README.md）")
    ap.add_argument("--with-path", action="store_true", help="（readme 源）关联 index.md 补全文件路径")
    ap.add_argument("--global-index", default=str(DEFAULT_GLOBAL_INDEX), help="index.md 路径（默认 knowledge/index.md）")
    ap.add_argument("--format", choices=["md", "json", "csv"], default="md")
    ap.add_argument("--output", help="输出文件（默认 stdout）")
    ap.add_argument("--since", help="只输出 >= 该日期的条目（YYYY-MM-DD，readme 源）")
    ap.add_argument("--until", help="只输出 <= 该日期的条目（YYYY-MM-DD，readme 源）")
    ap.add_argument("--keyword", help="关键词过滤（匹配文件名+摘要，大小写不敏感）")
    ap.add_argument("--star-only", action="store_true", help="只输出高价值（⭐）条目（readme 源）")
    ap.add_argument("--module", help="模块过滤（index 源，如 03_AI）")
    ap.add_argument("--no-exclude", action="store_true", help="路径关联时不过滤 bak/assets 等目录（默认过滤）")
    args = ap.parse_args()

    if args.source == "index":
        # 默认操作对象: index.md 全量（文件 + 路径 + 摘要）
        records = parse_global_index(Path(args.global_index))
        if not records:
            print(f"⚠️ index.md 无条目或不存在: {args.global_index}（请先运行 kb-global-index.py）",
                  file=sys.stderr)
        if args.module:
            records = [r for r in records if any(
                p.startswith(args.module + "/") for p in r["paths"])]
    else:
        # readme 源: 人工条目库
        path = Path(args.readme)
        if not path.exists():
            print(f"错误: 文件不存在 {path}", file=sys.stderr)
            sys.exit(1)
        entries, warnings = load_index_file(path)
        for w in warnings:
            print(f"WARN: {w}", file=sys.stderr)
        fname_map = build_path_map(Path(args.global_index)) if args.with_path else {}
        records = []
        for e in entries:
            if args.since and (e.date or "") < args.since:
                continue
            if args.until and (e.date or "") > args.until:
                continue
            if args.star_only and not e.star:
                continue
            paths = resolve_paths(e, fname_map) if args.with_path else []
            if args.with_path and not args.no_exclude:
                paths = [p for p in paths if not is_excluded_rel(p)]
            if args.with_path and len(paths) > 1:
                print(f"WARN: 文件名多命中 {e.file}: {paths}", file=sys.stderr)
            records.append(to_dict(e, paths))

    # 关键词过滤（两种源通用）
    if args.keyword:
        kw = args.keyword.lower()
        records = [r for r in records
                   if kw in r["file"].lower() or kw in r["summary"].lower()]

    # 渲染
    if args.format == "json":
        out = render_json(records)
    elif args.format == "csv":
        out = render_csv(records)
    else:
        out = render_md(records)

    if args.output:
        Path(args.output).write_text(out, encoding='utf-8')
        print(f"已输出 {len(records)} 条 → {args.output}", file=sys.stderr)
    else:
        print(out, end="" if out.endswith("\n") else "\n")


if __name__ == '__main__':
    main()
