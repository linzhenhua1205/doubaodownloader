#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kb-log-reorder.py — 知识库 log.md 正序重排工具（2026-08-15 规则变更）

背景（2026-08-15）:
  - 全局 knowledge/log.md 的日期分节从「倒序（newest first）」改为「**正序（oldest first）**」。
  - 修订方式统一为脚本尾部追加（kb-log-append.py），追加即正序，不再需要重排；
    本脚本仅用于**历史存量一次性重排** + 日常校验（--verify）。
  - AI 禁止直接 write/edit 整个 log.md；重排一律走本脚本（含备份、宽容解析、去重）。

用法:
  python3 scripts/tools/kb-log-reorder.py            # 重排 knowledge/log.md（写前备份）
  python3 scripts/tools/kb-log-reorder.py --dry-run  # 只预览统计，不写
  python3 scripts/tools/kb-log-reorder.py --verify   # 只校验是否正序（不写）

行为:
  1. 解析 log.md：头部说明 + `## YYYY-MM-DD` 日期分节 + `## 📝 ...` 归档分节
  2. 合并同日期分节（含带注释分节，如 `## 2026-08-09 (W32 周报)`）
  3. 按日期正序排列（oldest → newest）；归档分节原样保留在文件末尾
  4. 规范空行（分节间 1 空行，分节内条目间 1 空行）
  5. 写前 cp 备份到 tmp/bak/kb-log-reorder-<日期>/
"""

import argparse
import datetime
import os
import re
import shutil
import sys

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_LOG_PATH = os.path.join(WORKSPACE, "knowledge", "log.md")
LOG_PATH = DEFAULT_LOG_PATH

DATE_RE = re.compile(r"^##\s+(20\d{2}-\d{2}-\d{2})(?:\s*[（(]([^）)]*)[)）])?\s*$")
ARCHIVE_RE = re.compile(r"^##\s+[^2]")  # ## 后不是日期开头（2）→ 归档/特殊分节
SUBSEC_RE = re.compile(r"^###\s+")
LIST_ENTRY_RE = re.compile(r"^-\s+(20\d{2}-\d{2}-\d{2})\s+\d{2}:\d{2}\s*\|")  # - YYYY-MM-DD HH:MM | ...


def parse_log(text: str):
    """解析 log.md → (header_lines, date_sections, archive_sections)。

    date_sections: dict {date_str: {comments: [..], blocks: [ [lines..] ]}}
        blocks 按出现顺序记录每个「同日期分节」的内容（用于合并时保持顺序）。
    archive_sections: list of (title_line, content_lines)
    """
    lines = text.split("\n")

    # 1. 头部：第一个 ## 分节之前（标题 + 说明 + ---）
    body_start = 0
    for i, l in enumerate(lines):
        if l.startswith("## "):
            body_start = i
            break
    header_lines = lines[:body_start]

    # 2. 解析主体
    dates = {}          # date -> {"comments": [...], "blocks": [[lines...]]}
    date_order = []     # 日期首次出现顺序（合并后按此再正序排序）
    archives = []       # (title, content_lines)
    current_date = None
    current_block = None

    def flush():
        nonlocal current_date, current_block
        if current_date is not None and current_block is not None:
            dates[current_date]["blocks"].append(current_block)
        current_date = None
        current_block = None

    i = body_start
    while i < len(lines):
        line = lines[i]

        m = DATE_RE.match(line)
        if m:
            flush()
            date, comment = m.group(1), m.group(2)
            if date not in dates:
                dates[date] = {"comments": [], "blocks": []}
                date_order.append(date)
            if comment:
                dates[date]["comments"].append(comment)
            current_date = date
            current_block = []
            i += 1
            continue

        if line.startswith("## "):
            flush()
            # 归档/特殊分节：收集到下一个 ## 分节前
            title = line
            j = i + 1
            content = []
            while j < len(lines) and not lines[j].startswith("## "):
                content.append(lines[j])
                j += 1
            archives.append((title, content))
            i = j
            continue

        # 普通行（条目/子分节/空行）
        if current_date is not None and current_block is not None:
            current_block.append(line)
        i += 1
    flush()

    # 列表式 log（无 ## 日期分节）：按 `- YYYY-MM-DD HH:MM |` 条目日期分组
    if not dates:
        # body_start 可能为 0（整个文件被当 body）——需重定位：列表条目前的行视为 header
        first_entry = None
        for i, line in enumerate(lines):
            if LIST_ENTRY_RE.match(line.strip()):
                first_entry = i
                break
        if first_entry is not None:
            header_lines = lines[:first_entry]
            list_dates = {}
            list_order = []
            for line in lines[first_entry:]:
                m = LIST_ENTRY_RE.match(line.strip())
                if m:
                    d = m.group(1)
                    if d not in list_dates:
                        list_dates[d] = {"comments": [], "blocks": [[]]}
                        list_order.append(d)
                    list_dates[d]["blocks"][0].append(line)
            if list_dates:
                return header_lines, list_dates, list_order, archives

    return header_lines, dates, date_order, archives


def normalize_section_content(lines: list) -> list:
    """规范分节内容：去首尾空行、连续空行压为 1、去全空白行。"""
    out = []
    prev_blank = False
    for l in lines:
        if not l.strip():
            if prev_blank:
                continue
            prev_blank = True
            out.append("")
        else:
            prev_blank = False
            out.append(l)
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return out


def build_log(header_lines, dates, date_order, archives) -> str:
    """按正序输出完整 log.md（头部说明同步更新为正序规范）。"""
    out = []
    for l in header_lines:
        if "newest-first" in l or "newest first" in l:
            out.append(l.replace("newest-first", "oldest-first（正序）").replace("newest first", "oldest first（正序）"))
        else:
            out.append(l)
    # 保证头部以 --- 结尾（分隔符），合并连续 ---
    cleaned = []
    prev_dash = False
    for l in out:
        if l.strip() == "---":
            if prev_dash:
                continue
            prev_dash = True
        else:
            prev_dash = False
        cleaned.append(l)
    out = cleaned
    while out and not out[-1].strip():
        out.pop()
    if not out or out[-1].strip() != "---":
        out.append("---")
    out.append("")

    # 日期分节正序（oldest → newest）
    for date in sorted(date_order):
        sec = dates[date]
        out.append(f"## {date}")
        out.append("")
        # 合并同日期所有分节内容（条目级去重，保留首次出现）
        merged = []
        seen = set()
        for block in sec["blocks"]:
            nb = normalize_section_content(block)
            for l in nb:
                s = l.strip()
                if s.startswith("- ") and s in seen:
                    continue
                if s.startswith("- "):
                    seen.add(s)
                if merged and not merged[-1].strip() and not l.strip():
                    continue
                merged.append(l)
        out.extend(merged)
        out.append("")

    # 归档分节（末尾）：「待迁移」历史遗留收拢为单一归档节，其余原样保留
    pending = [c for t, c in archives if t.strip().startswith("## 待迁移")]
    other = [(t, c) for t, c in archives if not t.strip().startswith("## 待迁移")]
    if pending:
        out.append("## 📦 待迁移归档（历史遗留 · 2026-08-15 正序重排收拢）")
        out.append("")
        out.append("> 以下为 2026-08-03 分布式 log 合并时的「待人工迁移」占位条目（无日期分节归属），")
        out.append("> 正序重排时收拢于此，保留历史记录，待人工确认迁移去向。")
        out.append("")
        for content in pending:
            nc = normalize_section_content(content)
            if nc:
                out.extend(nc)
                out.append("")
    for title, content in other:
        out.append(title)
        out.append("")
        nc = normalize_section_content(content)
        if nc:
            out.extend(nc)
        out.append("")

    # 尾部空行清理
    while out and not out[-1].strip():
        out.pop()
    out.append("")
    return "\n".join(out)


def verify_order(text: str) -> list:
    """校验日期分节是否正序，返回违规列表。"""
    issues = []
    dates = []
    for i, l in enumerate(text.split("\n"), 1):
        m = DATE_RE.match(l)
        if m:
            dates.append((m.group(1), i))
    for k in range(1, len(dates)):
        if dates[k][0] < dates[k - 1][0]:
            issues.append(
                f"L{dates[k][1]}: 日期 {dates[k][0]} 出现在 {dates[k-1][0]} 之后（应为正序 oldest→newest）"
            )
    return issues


def backup():
    os.makedirs(os.path.join(WORKSPACE, "tmp", "bak"), exist_ok=True)
    stamp = datetime.date.today().strftime("%Y%m%d")
    bak_dir = os.path.join(WORKSPACE, "tmp", "bak", f"kb-log-reorder-{stamp}")
    os.makedirs(bak_dir, exist_ok=True)
    dst = os.path.join(bak_dir, "log.md")
    if not os.path.exists(dst):
        shutil.copy2(LOG_PATH, dst)
    return dst


def main():
    p = argparse.ArgumentParser(description="log.md 正序重排工具（默认全局 knowledge/log.md，可指定任意 log.md）")
    p.add_argument("--path", default="", help="目标 log.md 路径（默认 knowledge/log.md；2026-08-19 起无保留目录 log.md）")
    p.add_argument("--dry-run", action="store_true", help="只预览统计，不写")
    p.add_argument("--verify", action="store_true", help="只校验是否正序，不写")
    args = p.parse_args()

    global LOG_PATH
    if args.path:
        LOG_PATH = args.path if os.path.isabs(args.path) else os.path.join(WORKSPACE, args.path)

    with open(LOG_PATH, encoding="utf-8") as f:
        text = f.read()

    issues = verify_order(text)
    if args.verify:
        if issues:
            print(f"❌ 非正序违规 {len(issues)} 处:")
            for x in issues[:20]:
                print(f"  {x}")
            sys.exit(1)
        print("✅ log.md 日期分节为正序（oldest→newest）")
        sys.exit(0)

    header_lines, dates, date_order, archives = parse_log(text)
    n_dates = len(date_order)
    n_archives = len(archives)
    n_entries = sum(1 for sec in dates.values() for b in sec["blocks"] for l in b if l.strip().startswith("- "))
    dup_sections = len([1 for sec in dates.values() if len(sec["blocks"]) > 1])

    print("=" * 60)
    print("📋 kb-log-reorder 预览")
    print("=" * 60)
    print(f"📅 日期分节: {n_dates} 个不同日期")
    print(f"📦 归档分节: {n_archives} 个（保留在末尾）")
    print(f"📝 条目总数: {n_entries}")
    print(f"🔁 重复分节: {dup_sections} 个日期存在多分节（将被合并）")
    print(f"⚠️  当前倒序违规: {len(issues)} 处（重排后清零）")
    print("-" * 60)

    if args.dry_run:
        print("✅ dry-run：未写文件")
        sys.exit(0)

    new_text = build_log(header_lines, dates, date_order, archives)
    new_issues = verify_order(new_text)
    if new_issues:
        print(f"❌ 重排结果仍有违规 {len(new_issues)} 处，中止写入")
        sys.exit(2)
    if new_text == text:
        print("⏭️  内容无变化（已是正序），跳过")
        sys.exit(0)

    bak = backup()
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write(new_text)
    print(f"✅ 已重排写回: {LOG_PATH}")
    print(f"   {len(text)} → {len(new_text)} 字符")
    print(f"📦 备份: {bak}")


if __name__ == "__main__":
    main()
