#!/usr/bin/env python3
"""
KB Global Log Merger — 合并生成 knowledge/log.md 全局变更日志。

背景（2026-08-03 治理决策）:
  废弃 02_rd/03_AI/04_person/05_tools/06_others/07_industry-research 及其子目录的
  分布式 index.md / log.md（共 281 个文件），统一为:
    - knowledge/log.md   : 全局变更日志（本脚本合并生成）
    - knowledge/index.md : 全局文件索引（kb-global-index.py 生成）
  全库统一根 log.md（2026-08-19 起：01_survey/ 与 weekly-reports/ 分布式 log.md 均已移除，无保留目录；历史内容归档 knowledge/log.old.md）。

合并规则:
  - 收集非保留模块下所有 log.md（递归）+ knowledge/log.md 现有内容
  - 宽容解析 `## YYYY-MM-DD` 分节（容忍重复日期分节、emoji、多行条目）
  - 按日期正序输出（oldest→newest，2026-08-15 起）；日期内按模块分组；条目去重
  - 头部说明与历史归档信息保留在文件顶部

Usage:
  python scripts/tools/kb-global-log.py            # 合并生成 knowledge/log.md
  python scripts/tools/kb-global-log.py --dry-run  # 预览统计
  python scripts/tools/kb-global-log.py --verify   # 校验是否最新
"""
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.shared.workspace import KNOWLEDGE_ROOT

# === 配置 ===
OUTPUT_FILE = KNOWLEDGE_ROOT / "log.md"
# 2026-08-19 起无保留目录：全库统一根 log.md
KEEP_DISTRIBUTED = set()
MODULES = ["02_rd", "03_AI", "04_person", "05_tools", "06_others", "07_industry-research"]
EXCLUDE_DIRNAMES = {"bak", "oldbak", "90-bak", "assets", "images", "media", "files",
                    "_files", ".git", "node_modules", "old", ".venv", "__pycache__"}

MODULE_NAME = {
    "02_rd": "02_rd（研发知识库）",
    "03_AI": "03_AI（AI 架构）",
    "04_person": "04_person（个人）",
    "05_tools": "05_tools（工具）",
    "06_others": "06_others（其他）",
    "07_industry-research": "07_industry-research（行业研究）",
    "__root__": "根目录",
    "早期结构": "早期结构（2026-05~06，旧路径已迁移/废弃）",
}

DATE_RE = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})\s*$")


def collect_log_files():
    """收集非保留模块下所有 log.md 文件路径。"""
    files = []
    for mod in MODULES:
        base = KNOWLEDGE_ROOT / mod
        if not base.is_dir():
            continue
        for f in sorted(base.rglob("log.md")):
            excluded = any(part in EXCLUDE_DIRNAMES for part in f.parts)
            if excluded:
                continue
            files.append(f)
    return files


def parse_log(content: str):
    """宽容解析 log 文本 → [(date, [entries])]。entries 为多行条目（首行+缩进续行）。
    兼容两种格式：新格式（- 开头条目）与旧格式（| 表格行）。"""
    blocks = []  # (date, raw_lines)
    current_date = None
    current_lines = []
    header_lines = []

    for line in content.splitlines():
        m = DATE_RE.match(line)
        if m:
            if current_date is not None:
                blocks.append((current_date, current_lines))
            current_date = m.group(1)
            current_lines = []
        elif current_date is None:
            header_lines.append(line)
        else:
            current_lines.append(line)

    if current_date is not None:
        blocks.append((current_date, current_lines))

    # 组装条目：`- ` 开头为条目首行，后续缩进行为续行；表格行（| 开头且含 |）转条目
    result = []
    for date, lines in blocks:
        entries = []
        cur = None
        for line in lines:
            s = line.strip()
            if not s:
                continue
            # 表格行（旧格式）：| 操作 | 文件 | 说明 |  →  - **操作** | 文件 — 说明
            if s.startswith("|") and s.count("|") >= 3 and not s.startswith("|:"):
                cells = [c.strip() for c in s.strip("|").split("|")]
                if len(cells) >= 3 and cells[0] not in ("操作", "---"):
                    op, fname, desc = cells[0], cells[1], " | ".join(cells[2:])
                    fname = fname.strip("`")
                    entries.append(f"- **{op}** | `{fname}` — {desc}")
                continue
            if line.startswith("- ") or line.startswith("-"):
                if cur:
                    entries.append("\n".join(cur))
                cur = [line]
            else:
                if cur:
                    cur.append(line)
        if cur:
            entries.append("\n".join(cur))
        if entries:
            result.append((date, entries))
    return result, header_lines


def is_placeholder_entry(e: str) -> bool:
    """无效占位条目（如 `- **新增** | \`(本目录)\` — \`(本目录)\` — \` 新增\` —`）。"""
    if "(本目录)" in e or "(待补" in e:
        return True
    # 只有操作符无实际内容的条目
    body = e.lstrip("- ").strip()
    if body.count("—") >= 2 and all(part.strip() in ("", "`") or part.strip().startswith("`") and part.strip().endswith("`") and len(part.strip()) < 6 for part in body.split("—")[1:]):
        return True
    return False


def backfill_early_log():
    """从 git 历史提取 2026-05-11~06-06 早期 log 条目（旧表格格式 → 新条目格式）。

    数据源: 2026-06-05 知识库备份 commit（cc40098e），其 knowledge/log.md 包含
    5/11 初始导入 ~ 6/05 的全部早期变更记录（旧结构路径，多数已迁移/废弃）。
    """
    import subprocess
    r = subprocess.run(
        ["git", "show", "cc40098e4d6d589497d05f2f2f39615daaaefa0c:knowledge/log.md"],
        capture_output=True, cwd=str(Path(__file__).resolve().parents[2]))
    if r.returncode != 0:
        print("⚠️ 无法从 git 提取早期 log（commit cc40098e 不存在？）")
        return {}
    content = r.stdout.decode("utf-8", errors="replace")
    blocks, _ = parse_log(content)
    result = {}
    for date, entries in blocks:
        # 只保留 6/06 及之前（与现有合并内容衔接）
        if date > "2026-06-06":
            continue
        clean = [e for e in entries if not is_placeholder_entry(e)]
        if clean:
            result[date] = clean
    return result


def merge_all_logs(backfill: bool = False):
    """合并所有 log → {date: {module: [entries]}}，保持条目顺序并去重。"""
    merged = OrderedDict()  # date -> OrderedDict(module -> list)
    seen = set()

    # 1) 各模块 log.md
    for f in collect_log_files():
        rel = f.relative_to(KNOWLEDGE_ROOT).as_posix()
        parts = rel.split("/")
        module = parts[0] if len(parts) > 1 else "__root__"
        if module in KEEP_DISTRIBUTED:
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        blocks, _ = parse_log(content)
        for date, entries in blocks:
            d = merged.setdefault(date, OrderedDict())
            m = d.setdefault(module, [])
            for e in entries:
                key = (date, module, e)
                if key in seen:
                    continue
                seen.add(key)
                m.append(e)

    # 2) 根 log.md 现有内容
    root_log = KNOWLEDGE_ROOT / "log.md"
    if root_log.exists():
        content = root_log.read_text(encoding="utf-8", errors="replace")
        blocks, _ = parse_log(content)
        for date, entries in blocks:
            d = merged.setdefault(date, OrderedDict())
            m = d.setdefault("__root__", [])
            for e in entries:
                key = (date, "__root__", e)
                if key in seen:
                    continue
                seen.add(key)
                m.append(e)

    # 3) 早期历史补齐（--backfill）
    if backfill:
        early = backfill_early_log()
        for date, entries in early.items():
            d = merged.setdefault(date, OrderedDict())
            m = d.setdefault("早期结构", [])
            for e in entries:
                key = (date, "早期结构", e)
                if key in seen:
                    continue
                seen.add(key)
                m.append(e)

    # 4) 过滤无效占位条目
    for date in merged:
        for mod in merged[date]:
            merged[date][mod] = [e for e in merged[date][mod] if not is_placeholder_entry(e)]

    return merged


def build_log(merged) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []
    lines.append("# knowledge 变更日志（全局）")
    lines.append("")
    lines.append("> ⚠️ **全局统一变更日志** — 废弃原 `02_rd/03_AI/04_person/05_tools/06_others/07_industry-research`"
                 " 及各子目录的分布式 log.md，统一记录于此（由 `scripts/tools/kb-global-log.py` 合并）。")
    lines.append("> 全库统一根 log.md（2026-08-19 起：01_survey/weekly-reports 分布式 log.md 已移除，历史归档 knowledge/log.old.md，无保留目录）。")
    lines.append("> **新增条目规范**: `## YYYY-MM-DD` 分节 + `- **操作类型** | \`路径\` — 说明`（oldest-first 正序）。")
    lines.append("")
    lines.append("---")
    lines.append("")

    dates = sorted(merged.keys(), reverse=False)
    for date in dates:
        lines.append(f"## {date}")
        lines.append("")
        modules = merged[date]
        for mod in sorted(modules.keys()):
            entries = modules[mod]
            label = MODULE_NAME.get(mod, mod)
            lines.append(f"### {label}")
            lines.append("")
            for e in entries:
                lines.append(e)
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"> 本文件由 `kb-global-log.py` 合并生成，最后更新: {now}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Merge distributed log.md into knowledge/log.md")
    parser.add_argument("--dry-run", action="store_true", help="preview stats only")
    parser.add_argument("--verify", action="store_true", help="check if log.md is up-to-date")
    parser.add_argument("--backfill", action="store_true",
                        help="include early history (2026-05~06) extracted from git")
    args = parser.parse_args()

    merged = merge_all_logs(backfill=args.backfill)
    content = build_log(merged)

    if args.dry_run:
        n_dates = len(merged)
        n_entries = sum(len(e) for d in merged.values() for e in d.values())
        print(f"[dry-run] {n_dates} 个日期分节, {n_entries} 条记录, {len(content.splitlines())} 行")
        return

    if args.verify:
        if OUTPUT_FILE.exists() and OUTPUT_FILE.read_text(encoding="utf-8") == content:
            print("✅ log.md 已是最新")
            return 0
        print("⚠️ log.md 已过期，请运行 kb-global-log.py 重新合并")
        return 1

    OUTPUT_FILE.write_text(content, encoding="utf-8")
    n_dates = len(merged)
    n_entries = sum(len(e) for d in merged.values() for e in d.values())
    print(f"✅ 已生成 {OUTPUT_FILE}（{len(content.splitlines())} 行，{n_dates} 个日期，{n_entries} 条记录）")


if __name__ == "__main__":
    sys.exit(main())
