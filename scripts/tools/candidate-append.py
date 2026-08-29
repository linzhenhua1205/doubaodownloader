#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#================================================================
# candidate-append.py v1.0 — Candidate.md 脚本化追加器
#
# 用途：MEMORY.md/RULE.md/AGENT.md/USER.md 的修改提案，统一通过
#       本脚本追加到 Candidate.md（人工审核后导入），禁止直接
#       加载编辑 Candidate.md。
#
# 背景（2026-08-14 用户规则）：
#   - MEMORY.md 控制在 5K 以内；超额内容写入 Candidate.md
#   - Candidate.md 只允许脚本追加，不允许 read+edit 方式修改
#   - 未经人工统一，不再持续修改 MEMORY.md
#
# 用法：
#   python3 scripts/tools/candidate-append.py --target MEMORY.md \
#       --reason "内容超5K需压缩" --content "具体提案内容"
#   python3 scripts/tools/candidate-append.py --target RULE.md \
#       --reason "新增规则" --file /tmp/proposal.md   # 从文件读内容
#   python3 scripts/tools/candidate-append.py --list               # 查看待审议
#
# 输出：追加到 Candidate.md 的「## 待审议」区块（倒序：最新在上）
#================================================================

import argparse
import datetime
import os
import sys

CANDIDATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Candidate.md")

VALID_TARGETS = {"MEMORY.md", "RULE.md", "AGENT.md", "USER.md"}


def load_candidate(path: str) -> str:
    """读取 Candidate.md 全文（仅脚本内部读取，不暴露给 AI 编辑流程）。"""
    if not os.path.exists(path):
        return "# Candidate — 全局文件修改提案\n\n> ⚠️ **用途说明**: 对 `RULE.md` / `AGENT.md` / `USER.md` / `MEMORY.md` 的修改建议，先记录在此，人工审核后再导入。\n>\n> **格式**: `[日期] [目标文件] [原因] → [修改内容摘要]`\n\n---\n\n## 待审议\n\n_（暂无）_\n\n---\n\n## 已采纳\n\n_（暂无）_\n\n---\n\n## 已否决\n\n_（暂无）_\n"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def append_proposal(path: str, target: str, reason: str, content: str) -> None:
    """在「## 待审议」区块顶部插入新提案（最新在上）。"""
    text = load_candidate(path)
    date = datetime.date.today().isoformat()

    entry = (
        f"### {date} · {target} · {reason}\n\n"
        f"```\n{content.strip()}\n```\n\n"
    )

    marker = "## 待审议\n\n"
    if marker in text:
        # 把「_（暂无）_」占位替换为条目；否则在 marker 后插入
        placeholder = "## 待审议\n\n_（暂无）_\n"
        if placeholder in text:
            text = text.replace(placeholder, "## 待审议\n\n" + entry, 1)
        else:
            text = text.replace("## 待审议\n\n", "## 待审议\n\n" + entry, 1)
    else:
        text += "\n## 待审议\n\n" + entry

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"✅ 已追加到 Candidate.md: [{date}] {target} — {reason}")


def list_proposals(path: str) -> None:
    text = load_candidate(path)
    # 提取待审议区的提案标题
    in_pending = False
    for line in text.splitlines():
        if line.startswith("## 待审议"):
            in_pending = True
            continue
        if line.startswith("## "):
            in_pending = False
        if in_pending and line.startswith("### "):
            print(line)


def main() -> None:
    parser = argparse.ArgumentParser(description="Candidate.md 脚本化追加器")
    parser.add_argument("--target", choices=sorted(VALID_TARGETS), help="目标文件（MEMORY.md/RULE.md/AGENT.md/USER.md）")
    parser.add_argument("--reason", help="修改原因（一句话）")
    parser.add_argument("--content", help="提案内容（直接传字符串）")
    parser.add_argument("--file", help="提案内容（从文件读取，与 --content 二选一）")
    parser.add_argument("--list", action="store_true", help="列出待审议提案")
    args = parser.parse_args()

    if args.list:
        list_proposals(CANDIDATE_PATH)
        return

    if not args.target or not args.reason:
        parser.error("--target 和 --reason 必填（或使用 --list）")

    if args.content and args.file:
        parser.error("--content 与 --file 只能选一个")
    if not args.content and not args.file:
        parser.error("--content 或 --file 必填")

    content = args.content if args.content else open(args.file, "r", encoding="utf-8").read()
    append_proposal(CANDIDATE_PATH, args.target, args.reason, content)


if __name__ == "__main__":
    main()
