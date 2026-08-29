#!/usr/bin/env python3
"""
kb-log-search.py — knowledge/log.md 关键字检索工具（深度分析第一线索源）

背景（2026-08-25 优化）:
    深度分析活动需要先检索知识库已有内容。log.md（全局变更日志）是
    「时间序全局账本」——每条目含 日期+操作类型+文件路径+摘要说明，
    是全库文件路径+摘要密度最高的单文件索引。但此前无工具化访问方式：
      - read 全量 log.md (2952 行 ≈ 50KB+) 浪费 token
      - grep 只能拿行，拿不到日期/操作上下文，且路径命中无法定位文件
    本工具把 log.md 解析为结构化条目，支持关键字检索，输出
    「日期 + 路径 + 摘要」，并验证路径当前是否有效（历史账本路径可能已移动）。

核心能力:
  1. 关键字检索（多词 AND/OR、大小写不敏感、命中摘要/路径/文件名/操作/日期）
  2. 时间/模块/操作类型过滤
  3. 路径存在性验证 + basename 全库兜底（历史路径已移动时给出新位置）
  4. JSON 输出（供 agent/脚本程序化消费）
  5. 账本统计（条目数/日期范围/操作分布/主题词 Top）

用法:
  # 关键字检索（默认 AND，按日期倒序）
  python3 scripts/tools/kb-log-search.py --keyword "CXL"
  python3 scripts/tools/kb-log-search.py --keyword "CXL" --keyword "pooling"
  python3 scripts/tools/kb-log-search.py --keyword "CXL" --any            # OR 模式

  # 过滤与输出控制
  python3 scripts/tools/kb-log-search.py --keyword "RAS" --since 2026-08-01
  python3 scripts/tools/kb-log-search.py --keyword "RAS" --module 07_industry-research
  python3 scripts/tools/kb-log-search.py --keyword "RAS" --action 创建
  python3 scripts/tools/kb-log-search.py --keyword "RAS" --limit 15
  python3 scripts/tools/kb-log-search.py --keyword "RAS" --path-only     # 只输出有效路径
  python3 scripts/tools/kb-log-search.py --keyword "RAS" --json          # JSON 输出

  # 账本统计 / 主题词探测（辅助选关键词）
  python3 scripts/tools/kb-log-search.py --stats
  python3 scripts/tools/kb-log-search.py --topics --limit 30

设计约束:
  - 纯标准库，无第三方依赖
  - 解析结果按 log.md mtime 缓存（模块级），mtime 未变不重复解析
  - 不修改任何文件（只读工具）
"""

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
LOG_PATH = REPO_ROOT / "knowledge" / "log.md"
KNOWLEDGE_DIR = REPO_ROOT / "knowledge"

# Windows 控制台编码兼容
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ── log.md 结构正则 ──────────────────────────────────────────────────────────
DATE_HEAD_RE = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})")          # ## YYYY-MM-DD
SECTION_HEAD_RE = re.compile(r"^###\s+(.+)$")                     # ### 模块/子节
# 条目行: - **操作** | `path` — 说明   （兼容 - **📄 文档：标题** | [path](path) — 说明）
ENTRY_RE = re.compile(r"^-\s+\*\*(.+?)\*\*\s*(?:\|\s*(.+?)\s*)?(?:—|-|–)?\s*(.*)$")
# 路径提取（优先级: 反引号 > markdown 链接 > 裸路径）
BACKTICK_PATH_RE = re.compile(r"`([^`]+\.md)`")
MDLINK_PATH_RE = re.compile(r"\[[^\]]+\]\(([^)#]+\.md)\)")
BARE_PATH_RE = re.compile(r"(?<![`(\w])([\w./-]+\.md)(?![`)\w])")

# 非知识库路径前缀（这些文件不在 knowledge/ 下）
NON_KB_PREFIXES = ("spec/", "scripts/", "skills/", "tmp/", "import/", "memory/",
                   "discovery/", "conversation-log/", "websites/", "candidate", "Candidate")
# 知识库顶层模块（用于 --module 校验）
KB_MODULES = ("02_rd", "03_AI", "04_person", "05_tools", "06_others",
              "07_industry-research", "01_survey", "weekly-reports")


def parse_log(text: str) -> list:
    """解析 log.md → [{date, section, action, path, summary, line_no}]"""
    entries = []
    cur_date = None
    cur_section = None
    for line_no, raw in enumerate(text.splitlines(), 1):
        s = raw.strip()
        if not s:
            continue
        m = DATE_HEAD_RE.match(s)
        if m:
            cur_date = m.group(1)
            cur_section = None
            continue
        m = SECTION_HEAD_RE.match(s)
        if m:
            cur_section = m.group(1).strip()
            continue
        if not s.startswith("- "):
            continue
        em = ENTRY_RE.match(s)
        if not em:
            continue
        action = em.group(1).strip()
        rest = (em.group(2) or "") + " " + (em.group(3) or "")
        path = extract_path(rest)
        summary = clean_summary(rest, path)
        entries.append({
            "date": cur_date or "",
            "section": cur_section or "",
            "action": action,
            "path": path or "",
            "summary": summary,
            "line_no": line_no,
        })
    return entries


def extract_path(text: str) -> str:
    """从条目文本提取第一个 .md 路径（反引号 > 链接 > 裸路径）"""
    m = BACKTICK_PATH_RE.search(text)
    if m:
        return m.group(1).strip()
    m = MDLINK_PATH_RE.search(text)
    if m:
        return m.group(1).strip()
    m = BARE_PATH_RE.search(text)
    if m:
        return m.group(1).strip()
    return ""


def clean_summary(rest: str, path: str) -> str:
    """清理摘要: 删除 markdown 链接整体/反引号路径/裸路径，去残留符号"""
    s = re.sub(r"\[[^\]]*\]\([^)]*\)", "", rest)   # [text](target) 整体删除
    s = re.sub(r"`[^`]*`", "", s)                  # 反引号路径
    if path:
        s = s.replace(path, "")                    # 裸路径
    s = re.sub(r"^[\s|—–\-]+|[\s|—–\-]+$", "", s)  # 头尾残留符号
    return s.strip()


def normalize_path(path: str) -> str:
    """规范化为 knowledge/ 相对路径；非知识库文件返回 None（标注来源）"""
    p = path.strip().lstrip("./")
    if p.startswith("knowledge/"):
        p = p[len("knowledge/"):]
    if p.startswith(NON_KB_PREFIXES):
        return None
    # 全库相对路径（01_survey/weekly-reports/architectures 等历史根）→ knowledge/ 相对
    return p


@lru_cache(maxsize=1)
def build_filename_index():
    """全库文件名索引（一次性构建，供路径兜底）:
       basename → [相对路径]; stem → [相对路径]（历史文件改名后 slug 匹配）"""
    idx = defaultdict(list)
    for root, dirs, files in os.walk(KNOWLEDGE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if not f.endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(root, f), KNOWLEDGE_DIR)
            idx["name:" + f].append(rel)
            idx["stem:" + Path(f).stem].append(rel)
    return idx


def resolve_path(rel: str):
    """验证 knowledge/<rel> 是否存在；不存在时全库文件名兜底。

    兜底两级（历史路径已移动/改名，MEMORY 经验: 按 basename 全库定位）:
      1. exact — 精确 basename 命中（文件被移动未改名）
      2. fuzzy — slug 包含命中（文件被改名，如 intel-cxl-pooling.md
                 → 2026-06-26-intel-cxl-pooling.md；仅当 stem ≥8 字符且
                 命中 ≤3 个才报告 moved，防误报）

    返回 (status, resolved):
      status: "ok" | "moved" | "missing"
    """
    target = KNOWLEDGE_DIR / rel
    if target.exists():
        return "ok", rel
    fname = Path(rel).name
    stem = Path(rel).stem
    idx = build_filename_index()
    # 1. 精确 basename
    hits = idx.get("name:" + fname, [])
    if hits:
        return "moved", hits[0]
    # 2. slug 包含匹配（防误报: stem 过短或命中过多不采纳）
    if len(stem) >= 8:
        fuzzy = [p for k, paths in idx.items()
                 if k.startswith("stem:") and stem in k
                 for p in paths]
        if 0 < len(fuzzy) <= 3:
            return "moved", fuzzy[0]
    return "missing", rel


@lru_cache(maxsize=1)
def load_entries():
    """按 mtime 缓存解析结果（mtime 未变不重复解析）"""
    mtime = LOG_PATH.stat().st_mtime
    text = LOG_PATH.read_text(encoding="utf-8")
    return mtime, parse_log(text)


def keyword_hit(entry: dict, kws: list, any_mode: bool) -> bool:
    """关键字命中: 摘要/路径/文件名/操作/日期/分节"""
    haystack = " ".join([
        entry["summary"], entry["path"], Path(entry["path"]).name,
        entry["action"], entry["date"], entry["section"],
    ]).lower()
    if any_mode:
        return any(kw.lower() in haystack for kw in kws)
    return all(kw.lower() in haystack for kw in kws)


def main():
    ap = argparse.ArgumentParser(description="knowledge/log.md 关键字检索工具",
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("--keyword", action="append", default=[], metavar="KW",
                    help="检索关键词（可多次指定，默认 AND）")
    ap.add_argument("--any", action="store_true", help="多关键词 OR 模式")
    ap.add_argument("--since", metavar="YYYY-MM-DD", help="起始日期（含）")
    ap.add_argument("--until", metavar="YYYY-MM-DD", help="截止日期（含）")
    ap.add_argument("--module", action="append", default=[], metavar="MOD",
                    help="路径前缀过滤，如 02_rd / 07_industry-research（可多次）")
    ap.add_argument("--action", metavar="ACT", help="操作类型过滤，如 创建/更新/重构/删除")
    ap.add_argument("--limit", type=int, default=20, metavar="N", help="最大输出条数（默认 20）")
    ap.add_argument("--path-only", action="store_true", help="只输出有效知识库路径（去重）")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    ap.add_argument("--stats", action="store_true", help="账本统计模式")
    ap.add_argument("--topics", action="store_true", help="主题词 Top 探测（辅助选关键词）")
    args = ap.parse_args()

    if not LOG_PATH.exists():
        print(f"❌ 找不到 {LOG_PATH}", file=sys.stderr)
        sys.exit(1)

    _, entries = load_entries()

    # ── 统计模式 ──
    if args.stats:
        dates = sorted({e["date"] for e in entries if e["date"]})
        actions = Counter(e["action"] for e in entries)
        print(f"📊 knowledge/log.md 账本统计")
        print(f"  条目总数: {len(entries)}")
        print(f"  日期范围: {dates[0]} ~ {dates[-1]}（{len(dates)} 个分节）")
        print(f"  操作分布: " + ", ".join(f"{k}×{v}" for k, v in actions.most_common(8)))
        # 文件路径有效性
        ok = moved = missing = 0
        for e in entries:
            if not e["path"]:
                continue
            rel = normalize_path(e["path"])
            if rel is None:
                continue
            st, _ = resolve_path(rel)
            ok += st == "ok"
            moved += st == "moved"
            missing += st == "missing"
        print(f"  路径有效性: 有效 {ok} / 已移动 {moved} / 缺失 {missing}")
        return

    # ── 主题词探测 ──
    if args.topics:
        words = Counter()
        for e in entries:
            for w in re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", e["summary"]):
                if w.lower() in {"the", "and", "for", "with", "from", "this", "that",
                                 "into", "v1", "v2", "pdf", "md"}:
                    continue
                words[w.lower()] += 1
        print(f"🔥 主题词 Top {args.limit}（摘要中出现频次，英文词）:")
        for w, c in words.most_common(args.limit):
            print(f"  {w:30s} ×{c}")
        return

    # ── 关键字检索 ──
    if not args.keyword:
        print("❌ 请提供 --keyword（或用 --stats / --topics 查看账本概况）", file=sys.stderr)
        sys.exit(1)

    matched = [e for e in entries if keyword_hit(e, args.keyword, args.any)]

    # 过滤: 日期 / 模块 / 操作
    if args.since:
        matched = [e for e in matched if e["date"] >= args.since]
    if args.until:
        matched = [e for e in matched if e["date"] <= args.until]
    if args.module:
        matched = [e for e in matched
                   if any(e["path"].startswith(m + "/") or e["path"].startswith(m)
                          for m in args.module)]
    if args.action:
        matched = [e for e in matched if args.action in e["action"]]

    # 按日期倒序（最新在前）
    matched.sort(key=lambda e: e["date"], reverse=True)

    # ── 路径解析与验证 ──
    resolved = []
    for e in matched:
        rel = normalize_path(e["path"])
        if rel is None:
            resolved.append({**e, "kb": False, "status": "non-kb"})
            continue
        st, new_rel = resolve_path(rel)
        resolved.append({**e, "kb": True, "status": st, "resolved": new_rel})

    if args.path_only:
        seen = set()
        for r in resolved:
            if r["kb"] and r["status"] in ("ok", "moved") and r["resolved"] not in seen:
                seen.add(r["resolved"])
                print(r["resolved"])
        print(f"\n# 共 {len(seen)} 个有效路径（log.md 命中 {len(matched)} 条）", file=sys.stderr)
        return

    if args.json:
        out = {
            "query": args.keyword,
            "mode": "OR" if args.any else "AND",
            "total_hits": len(matched),
            "entries": resolved[:args.limit],
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    # 文本输出
    print(f"🔍 log.md 检索 [{(' OR ' if args.any else ' AND ').join(args.keyword)}] "
          f"— 命中 {len(matched)} 条（显示前 {min(args.limit, len(matched))}）")
    print("-" * 90)
    for r in resolved[:args.limit]:
        tag = {"ok": "✅", "moved": "🔀", "missing": "❌", "non-kb": "📎"}[r["status"]]
        loc = r["resolved"] if r["status"] == "moved" else r["path"]
        line = f"[{r['date']}] {tag} {r['action']} | {loc}"
        if r["summary"]:
            line += f" — {r['summary'][:110]}"
        print(line)
        if r["status"] == "moved":
            print(f"      ↳ 原路径 {r['path']} 已移动 → 现位于 {r['resolved']}")
    print("-" * 90)
    if not matched:
        print("💡 无命中。试试: --topics 看主题词 / 换更宽泛的关键词 / 直接 grep 全库")
    else:
        print(f"💡 提示: 命中路径可直接 read；需要更详细摘要用 "
              f"`kb-index-extract.py --source index --keyword ...`")


if __name__ == "__main__":
    main()
