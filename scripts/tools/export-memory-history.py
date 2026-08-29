#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export-memory-history.py — 导出 MEMORY.md 全部 git 改动历史，归档到 memory/memory.history.md

背景（2026-08-15）:
  - 用户要求：MEMORY.md 历次改动全量导出归档，可覆盖目标文件。
  - 数据源：git log --follow -- MEMORY.md（含 2026-06-04 首次出现至今全部提交的 diff）。
  - 输出：memory/memory.history.md（头部统计 + 时间线 + 按时间正序的历次 diff）。

用法:
  python3 scripts/tools/export-memory-history.py            # 生成归档（覆盖写）
  python3 scripts/tools/export-memory-history.py --dry-run  # 只预览统计
"""

import argparse
import datetime
import os
import subprocess
import sys

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_PATH = os.path.join(WORKSPACE, "memory", "memory.history.md")
MEMORY_FILE = "MEMORY.md"


def run_git(args: list) -> str:
    r = subprocess.run(["git", "-C", WORKSPACE] + args, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        print(f"❌ git 命令失败: {args} — {r.stderr[:300]}")
        sys.exit(2)
    return r.stdout


def get_commits() -> list:
    """返回按时间正序（oldest→newest）的提交列表 [ (hash, date, subject), ... ]"""
    out = run_git(["log", "--format=%H|%ad|%s", "--date=short", "--follow", "--", MEMORY_FILE])
    commits = []
    for line in out.strip().split("\n"):
        if not line:
            continue
        h, d, s = line.split("|", 2)
        commits.append((h, d, s))
    commits.reverse()  # 正序
    return commits


def get_diff(commit: str, prev: str) -> str:
    """获取该提交对 MEMORY.md 的 diff（对比上一版本）。"""
    if prev:
        out = run_git(["log", "-p", "-1", "--format=commit %H%nDate: %ad%nSubject: %s%n",
                       "--date=short", commit, "--", MEMORY_FILE])
    else:
        # 首次出现：显示完整文件内容
        out = run_git(["show", f"{commit}:{MEMORY_FILE}"])
        out = f"（首次创建，完整内容）\n\n{out}"
    return out


def build_markdown(commits: list) -> str:
    now = datetime.date.today().strftime("%Y-%m-%d")
    n = len(commits)
    first_date = commits[0][1] if commits else "-"
    last_date = commits[-1][1] if commits else "-"

    lines = []
    lines.append("# MEMORY.md 历史归档（历次 git 改动全量导出）")
    lines.append("")
    lines.append("> **说明**: 本文档归档根目录 `MEMORY.md`（长期记忆索引）自 git 首次出现以来的**全部历次改动**，")
    lines.append("> 按时间正序（oldest→newest）排列，含每次提交的完整 diff。")
    lines.append("> **生成时间**: " + now)
    lines.append("> **生成方式**: `git log -p --follow -- MEMORY.md`（export-memory-history.py）")
    lines.append("> **注意**: 归档为只读历史快照，勿直接编辑；当前活跃版请查看根目录 `MEMORY.md`。")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 统计
    lines.append("## 统计")
    lines.append("")
    lines.append("| 维度 | 值 |")
    lines.append("|:-----|:---|")
    lines.append(f"| 提交总数 | {n} |")
    lines.append(f"| 时间跨度 | {first_date} → {last_date} |")
    lines.append(f"| 归档文件 | `memory/memory.history.md` |")
    lines.append("")

    # 时间线
    lines.append("## 提交时间线")
    lines.append("")
    lines.append("| # | 提交 | 日期 | 说明 |")
    lines.append("|:--|:-----|:-----|:-----|")
    for i, (h, d, s) in enumerate(commits, 1):
        short = h[:8]
        s_esc = s.replace("|", "\\|")
        lines.append(f"| {i} | `{short}` | {d} | {s_esc} |")
    lines.append("")

    # 历次改动详情（正序）
    lines.append("## 历次改动详情（时间正序）")
    lines.append("")
    for i, (h, d, s) in enumerate(commits, 1):
        prev = commits[i - 2][0] if i >= 2 else None
        lines.append(f"### {i}. `{h[:8]}`（{d}）— {s}")
        lines.append("")
        diff = get_diff(h, prev)
        # diff 内容缩进为代码块
        lines.append("```diff")
        for dl in diff.rstrip("\n").split("\n"):
            lines.append(dl)
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description="导出 MEMORY.md 全部 git 改动历史")
    p.add_argument("--dry-run", action="store_true", help="只预览统计，不写")
    args = p.parse_args()

    commits = get_commits()
    print("=" * 60)
    print("📋 export-memory-history 预览")
    print("=" * 60)
    print(f"📝 提交总数: {len(commits)}")
    print(f"📅 时间跨度: {commits[0][1]} → {commits[-1][1]}" if commits else "无提交")
    print("-" * 60)

    if args.dry_run:
        print("✅ dry-run：未写文件")
        sys.exit(0)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    md = build_markdown(commits)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"✅ 已生成: {OUT_PATH}")
    print(f"   {len(md)} 字符 / {md.count(chr(10)) + 1} 行")


if __name__ == "__main__":
    main()
