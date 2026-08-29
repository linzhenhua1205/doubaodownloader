#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kb-log-append.py — 知识库 log.md 尾部追加工具（AI 归档专用）

背景（2026-08-07 规则变更）：
  - README.md / index.md / log.md 三个文件**不允许 AI 直接编辑/优化**（write/edit 禁用）。
  - 新建/修改知识库文件时，AI 只负责把「全面摘要」写到外部临时文件，
    由本脚本完成 log.md 的尾部 append（含备份、格式校验、查重）。
  - index.md / README.md 由脚本批量处理（kb-global-index.py 定期刷新），AI 不碰。

用法：
  python3 scripts/tools/kb-log-append.py --file tmp/kb-log-draft-<date>.md
  python3 scripts/tools/kb-log-append.py --content "待追加内容..."
  # 可选：--section <模块名>（分节头，如 "02_rd/02_project"）--dry-run（预览不写）

行为：
  1. 校验输入内容非空、包含路径链接（[knowledge/x.md](x.md) 或 `knowledge/x.md`）
  2. 若 log.md 尾部不是 `## YYYY-MM-DD`（今天）分节，先追加分节头
  3. 追加内容到文件尾部（正序 oldest→newest；同日分节自动合并，不重复建分节头）
  4. 写前 cp 备份到 tmp/bak/kb-log-append-<日期>/
  5. 简单查重：内容第一行已存在则跳过
"""

import argparse
import datetime
import os
import re
import shutil
import sys

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_PATH = os.path.join(WORKSPACE, "knowledge", "log.md")


def parse_args():
    p = argparse.ArgumentParser(description="knowledge/log.md 尾部追加工具")
    grp = p.add_mutually_exclusive_group(required=True)
    grp.add_argument("--file", help="外部临时摘要文件路径（相对 workspace）")
    grp.add_argument("--content", help="直接传入待追加内容")
    p.add_argument("--section", default="", help="分节标题（如 02_rd/02_project），追加在日期分节下")
    p.add_argument("--date", default="", help="日期分节（默认今天 YYYY-MM-DD）")
    p.add_argument("--dry-run", action="store_true", help="只校验与预览，不写文件")
    return p.parse_args()


def read_content(args) -> str:
    if args.content:
        return args.content.strip()
    path = args.file if os.path.isabs(args.file) else os.path.join(WORKSPACE, args.file)
    if not os.path.exists(path):
        print(f"❌ 临时文件不存在: {path}")
        sys.exit(2)
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


def normalize_links(content: str) -> str:
    """链接 URL 规范化：`](knowledge/...` → `](...`（去掉冗余前缀）。

    背景（2026-08-11 修复）：
      knowledge/log.md 位于 knowledge/ 目录，渲染器按 log.md 所在目录解析相对链接。
      URL 若写成 `](knowledge/03_AI/x.md)`，会被解析为 knowledge/knowledge/03_AI/x.md → 失效。
      正确形式 = 不带前缀的相对路径 `](03_AI/x.md)`（与历史分布式 log 一致）。
      仅规范化 URL 部分，显示文本 [knowledge/... 保留不动。
    """
    return re.sub(r"\]\(knowledge/([^)]+)\)", r"](\1)", content)


def validate(content: str) -> list:
    """返回警告列表（不阻塞，但提示）。"""
    warns = []
    if not content:
        warns.append("内容为空")
        return warns
    if len(content) < 20:
        warns.append("内容过短（<20 字符），摘要可能不全面")
    # 路径/链接检查：期望包含 [knowledge/...](...) 或 `knowledge/...`
    if not re.search(r"\[knowledge/[^\]]+\]\([^)]+\)|`knowledge/[^`]+`", content):
        warns.append("未检测到 knowledge/ 路径或链接——摘要应包含路径+链接信息（建议 [knowledge/x.md](x.md) 形式）")
    # 链接 URL 前缀检查：URL 部分不应以 knowledge/ 开头（会导致 knowledge/knowledge/ 双前缀失效）
    if re.search(r"\]\(knowledge/", content):
        warns.append("链接 URL 含冗余 knowledge/ 前缀（会解析为 knowledge/knowledge/... 失效）——已自动规范化为相对路径")
    # 条目风格检查：期望 - **标题** | 链接 — 说明
    if not re.search(r"^- \*\*.+\*\* \|", content, re.M):
        warns.append("条目风格建议: `- **操作类型：标题** | [knowledge/x.md](x.md) — 说明`")
    return warns


def backup():
    os.makedirs(os.path.join(WORKSPACE, "tmp", "bak"), exist_ok=True)
    stamp = datetime.date.today().strftime("%Y%m%d")
    bak_dir = os.path.join(WORKSPACE, "tmp", "bak", f"kb-log-append-{stamp}")
    os.makedirs(bak_dir, exist_ok=True)
    dst = os.path.join(bak_dir, "log.md")
    if not os.path.exists(dst):  # 当天只备份一次
        shutil.copy2(LOG_PATH, dst)
        return dst
    return dst


def append_to_log(content: str, section: str, date_str: str) -> tuple:
    """返回 (是否写入, 说明)。

    正序语义（2026-08-15）：log.md 按日期正序（oldest→newest），追加到文件尾部即正序。
    同日分节合并：若文件中最后一个 `## YYYY-MM-DD` 分节头 == 今天，则直接追加内容，
    不再重复创建分节头（修复历史 bug：08-10 曾产生 68 个重复分节头）。
    """
    with open(LOG_PATH, encoding="utf-8") as f:
        log_text = f.read()

    today_head = f"## {date_str}"
    # 查重：取内容中第一条非标题行（条目行）查重；分节头（# 开头）不参与查重
    # （08-19 修复：tmp 文件含分节头时旧逻辑误判"已存在"导致跳过追加 + 产生重复分节头）
    first_line = ""
    for _line in content.splitlines():
        _s = _line.strip()
        if _s and not _s.startswith("#"):
            first_line = _s
            break
    if first_line and first_line in log_text:
        return False, "内容条目已存在于 log.md（跳过重复）"

    # 找最后一个日期分节头（兼容 `## YYYY-MM-DD (注释)`）
    date_head_re = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})")
    last_date = None
    last_date_idx = -1
    lines_all = log_text.split("\n")
    for idx, line in enumerate(lines_all):
        m = date_head_re.match(line.strip())
        if m:
            last_date = m.group(1)
            last_date_idx = idx
    tail_has_today = last_date == date_str
    # 归档区起点：最后一个日期分节之后的第一个非日期 `## ` 分节（📦/📝 等）
    archive_start = len(lines_all)
    if last_date_idx >= 0:
        for idx in range(last_date_idx + 1, len(lines_all)):
            s = lines_all[idx].strip()
            if s.startswith("## ") and not date_head_re.match(s):
                archive_start = idx
                break

    # 构造待追加块
    block_lines = []
    if section:
        section_head = f"### {section}"
        # 若最后一个分节 == 今天 且 尾部最后一行 == 同 section → 直接追加
        tail_lines = [l for l in log_text.rstrip().split("\n") if l.strip()]
        tail_last = tail_lines[-1].strip() if tail_lines else ""
        if tail_has_today and tail_last == section_head:
            pass  # 同 section 连续，直接追加
        else:
            if not tail_has_today:
                block_lines.append(today_head)
            block_lines.append(f"### {section}")
    else:
        if not tail_has_today:
            block_lines.append(today_head)
    block_lines.append(content)
    block = "\n\n" + "\n".join(block_lines) + "\n"

    # 写入位置：归档区之前（若存在），否则文件末尾
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    if archive_start < len(lines_all):
        head = "\n".join(lines_all[:archive_start]).rstrip() + "\n"
        tail = "\n".join(lines_all[archive_start:])
        new_text = head + block + tail
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            f.write(new_text)
    else:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(block)
    return True, f"已追加 {len(content)} 字符"


def main():
    args = parse_args()
    content = read_content(args)
    content = normalize_links(content)  # URL 规范化（防 knowledge/knowledge/ 双前缀失效）
    warns = validate(content)
    for w in warns:
        print(f"⚠️  {w}")
    date_str = args.date or datetime.date.today().strftime("%Y-%m-%d")

    print("=" * 60)
    print(f"📋 kb-log-append 预览（{date_str}{' / ' + args.section if args.section else ''}）")
    print("=" * 60)
    print(content[:500] + ("..." if len(content) > 500 else ""))
    print("-" * 60)

    if args.dry_run:
        print("✅ dry-run：未写文件")
        sys.exit(0 if not warns else 1)

    # 备份（写前）
    bak = backup()
    written, msg = append_to_log(content, args.section, date_str)
    print(f"{'✅' if written else '⏭️'} {msg}")
    if written:
        print(f"📦 备份: {bak}")
    sys.exit(0 if written else 3)


if __name__ == "__main__":
    main()
