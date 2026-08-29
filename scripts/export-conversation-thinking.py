#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#================================================================
# export-conversation-thinking.py v1.0 — 历史对话思考过程+简报导出器
#
# 用途：从 conversation-log/db-sessions/ 会话记录中，提取每回合
#       AI 思考过程（💭 思考）与对话处理简报（💬 回复），
#       导出为结构化 Markdown，归档到
#       knowledge/weekly-reports/07_kb_stat/06_conversation/。
#
# 特性：
#   - 按日期分组输出（YYYY-MM.md），思考过程清晰保留原始文本
#   - 单文件 > MAX_SIZE（默认 10MB）自动 gzip 压缩为 .md.gz
#   - 幂等：增量导出（--since 日期），同文件覆盖不重复
#   - 输出质量：会话元数据表 + 回合结构 + 思考/回复分离
#
# 用法：
#   python3 scripts/export-conversation-thinking.py                # 全量导出
#   python3 scripts/export-conversation-thinking.py --since 2026-08-01  # 增量
#   python3 scripts/export-conversation-thinking.py --max-size 10M  # 阈值
#   python3 scripts/export-conversation-thinking.py --dry-run       # 仅统计
#
# 依赖：仅标准库（os/re/gzip/glob/datetime）
#
# 变更日志：
#   2026-08-14 v1.0 created
#================================================================

import argparse
import gzip
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = os.path.expanduser("~/cow")
SRC_DIR = os.path.join(WORKSPACE, "conversation-log", "db-sessions")
INDEX_FILE = os.path.join(SRC_DIR, "index.md")
OUT_DIR = os.path.join(WORKSPACE, "knowledge", "weekly-reports", "07_kb_stat", "06_conversation")

DEFAULT_MAX_SIZE = 10 * 1024 * 1024  # 10MB
CHUNK_SIZE = 1024 * 1024  # 1MB 流式写入阈值


# ─────────────────────────────────────────────
# 会话文件解析
# ─────────────────────────────────────────────

def parse_session_file(file_path: str) -> dict:
    """解析单个会话文件，提取元数据 + 回合序列（思考/回复/工具调用）。"""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # 元数据
    title = "未命名会话"
    m = re.search(r"^# 💬 对话:\s*(.+)$", content, re.M)
    if m:
        title = m.group(1).strip()

    meta = {}
    for key, label in [("id", "会话 ID"), ("channel", "渠道"), ("created", "创建时间"),
                       ("active", "最后活跃"), ("msgs", "消息数")]:
        m = re.search(rf"^> \*\*{label}\*\*:[ \t]*(.*)$", content, re.M)
        if m:
            meta[key] = m.group(1).strip()

    # 按回合切分
    rounds = []
    parts = re.split(r"^## 回合 (\d+) - (\d{2}:\d{2})\s*$", content, flags=re.M)
    # parts[0] = 头部，之后是 (num, time, body) 三元组
    for i in range(1, len(parts), 3):
        if i + 2 >= len(parts):
            break
        num, time_str, body = parts[i], parts[i + 1], parts[i + 2]
        round_data = {"num": int(num), "time": time_str,
                      "think": "", "reply": "", "user": "", "tools": []}

        # 提取 💭 思考
        m = re.search(r"### 💭 思考\s*\n+(.*?)(?=\n### |\n## 回合|\Z)", body, re.S)
        if m:
            round_data["think"] = m.group(1).strip()

        # 提取 💬 回复
        m = re.search(r"### 💬 回复\s*\n+(.*?)(?=\n### |\n## 回合|\Z)", body, re.S)
        if m:
            round_data["reply"] = m.group(1).strip()

        # 提取 🗣️ 用户
        m = re.search(r"### 🗣️ 用户\s*\n+(.*?)(?=\n### |\n## 回合|\Z)", body, re.S)
        if m:
            round_data["user"] = m.group(1).strip()

        # 提取工具调用表
        m = re.search(r"### 🛠️ 工具调用\s*\n+(.*?)(?=\n### |\n## 回合|\Z)", body, re.S)
        if m:
            round_data["tools"] = m.group(1).strip()

        # 只有思考或回复或工具时才有价值
        if round_data["think"] or round_data["reply"] or round_data["tools"]:
            rounds.append(round_data)

    return {"path": file_path, "title": title, "meta": meta, "rounds": rounds,
            "date": _extract_date(file_path, meta)}


def _extract_date(file_path: str, meta: dict) -> str:
    """从文件名或创建时间提取日期（YYYY-MM-DD）。"""
    base = os.path.basename(file_path)
    m = re.match(r"(\d{4}-\d{2}-\d{2})", base)
    if m:
        return m.group(1)
    if meta.get("created"):
        m = re.search(r"(\d{4}-\d{2}-\d{2})", meta["created"])
        if m:
            return m.group(1)
    return "0000-00-00"


# ─────────────────────────────────────────────
# Markdown 渲染
# ─────────────────────────────────────────────

def render_session(sess: dict) -> str:
    """渲染单个会话为 Markdown 块。思考过程完整保留，回复保留（可截断）。"""
    lines = []
    lines.append(f"## 💬 {sess['title']}")
    lines.append("")
    # 元数据表
    meta = sess["meta"]
    lines.append("| 属性 | 值 |")
    lines.append("|:-----|:---|")
    lines.append(f"| 文件 | `{os.path.basename(sess['path'])}` |")
    if meta.get("id"):
        lines.append(f"| 会话ID | `{meta['id']}` |")
    if meta.get("channel"):
        lines.append(f"| 渠道 | {meta['channel']} |")
    if meta.get("created"):
        lines.append(f"| 创建 | {meta['created']} |")
    if meta.get("active"):
        lines.append(f"| 活跃 | {meta['active']} |")
    if meta.get("msgs"):
        lines.append(f"| 消息数 | {meta['msgs']} |")
    lines.append("")

    # 有思考的回合才需要详细展示
    think_rounds = [r for r in sess["rounds"] if r["think"]]
    reply_rounds = [r for r in sess["rounds"] if r["reply"]]

    if think_rounds:
        lines.append(f"### 🧠 思考过程（{len(think_rounds)} 回合）")
        lines.append("")
        for r in think_rounds:
            lines.append(f"**回合 {r['num']} · {r['time']}**")
            lines.append("")
            lines.append("> " + r["think"].replace("\n", "\n> "))
            lines.append("")
            if r["tools"]:
                # 工具调用摘要（只保留首行表格标题+前几行）
                tool_lines = r["tools"].split("\n")
                if len(tool_lines) > 3:
                    lines.append("工具调用：")
                    lines.append("")
                    for tl in tool_lines[:6]:
                        lines.append("  " + tl if tl.strip() else "")
                    lines.append("")
    else:
        lines.append("_（本会话无思考记录）_")
        lines.append("")

    if reply_rounds:
        lines.append(f"### 📋 对话处理简报（{len(reply_rounds)} 条回复）")
        lines.append("")
        for r in reply_rounds:
            lines.append(f"**回合 {r['num']} · {r['time']}**")
            lines.append("")
            lines.append(r["reply"])
            lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ─────────────────────────────────────────────
# 输出：按月分组 + 10MB 压缩
# ─────────────────────────────────────────────

def ensure_out_dir() -> str:
    os.makedirs(OUT_DIR, exist_ok=True)
    return OUT_DIR


def write_grouped(month: str, content: str, max_size: int, dry_run: bool = False) -> str:
    """写入月份文件，超阈值则 gzip。返回实际写入路径。"""
    out_dir = ensure_out_dir()
    md_path = os.path.join(out_dir, f"conversation-thinking-{month}.md")
    gz_path = md_path + ".gz"

    if dry_run:
        size = len(content.encode("utf-8"))
        suffix = " (gzip)" if size > max_size else ""
        return f"[dry-run] {os.path.basename(md_path)}{suffix} ~{size/1024:.0f}KB"

    data = content.encode("utf-8")
    if len(data) > max_size:
        with gzip.open(gz_path, "wt", encoding="utf-8") as f:
            f.write(content)
        # 删除旧的未压缩文件（若存在）
        if os.path.exists(md_path):
            os.remove(md_path)
        return gz_path
    else:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(content)
        # 删除旧的压缩文件（若存在）
        if os.path.exists(gz_path):
            os.remove(gz_path)
        return md_path


def build_header(total_sessions: int, since: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        f"# 🧠 历史对话·AI思考过程与处理简报导出\n\n"
        f"> **生成时间**: {now}\n"
        f"> **数据源**: `conversation-log/db-sessions/`（{total_sessions} 个会话文件）\n"
        f"> **范围**: {'全量' if not since else f'自 {since} 起'}\n"
        f"> **说明**: 每回合提取 AI 思考过程（💭）与对话处理简报（💬）；单文件超 10MB 自动 gzip 压缩\n\n"
        f"---\n\n"
    )


# ─────────────────────────────────────────────
# 主流程
# ─────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="历史对话思考过程+简报导出器")
    parser.add_argument("--since", help="只导出该日期（含）之后的会话，YYYY-MM-DD")
    parser.add_argument("--max-size", default="10M", help="单文件压缩阈值，默认 10M（支持 K/M/G）")
    parser.add_argument("--dry-run", action="store_true", help="仅统计不写文件")
    parser.add_argument("--src", default=SRC_DIR, help="会话文件目录（默认 conversation-log/db-sessions）")
    args = parser.parse_args()

    # 解析大小
    size_str = args.max_size.upper()
    mult = {"K": 1024, "M": 1024**2, "G": 1024**3}.get(size_str[-1], 1)
    max_size = int(size_str[:-1]) * mult if size_str[-1] in "KMG" else int(size_str)

    # 扫描会话文件
    files = sorted(Path(args.src).glob("*.md"))
    files = [f for f in files if f.name != "index.md"]
    sessions = []
    skipped = 0
    for f in files:
        sess = parse_session_file(str(f))
        if args.since and sess["date"] < args.since:
            skipped += 1
            continue
        # 过滤无思考无回复的空会话
        if not any(r["think"] or r["reply"] for r in sess["rounds"]):
            skipped += 1
            continue
        sessions.append(sess)

    if args.dry_run:
        # 统计输出
        months = {}
        for s in sessions:
            months.setdefault(s["date"][:7], []).append(s)
        print(f"📊 会话文件总数: {len(files)}")
        print(f"📦 本次导出: {len(sessions)} 个（跳过 {skipped} 个空/过期会话）")
        for m in sorted(months):
            print(f"  - {m}: {len(months[m])} 个会话")
        # 估算每个月份文件大小
        for m in sorted(months):
            content = build_header(len(sessions), args.since)
            for s in sorted(months[m], key=lambda x: x["date"]):
                content += render_session(s)
            size = len(content.encode("utf-8"))
            flag = "⚠️>10M需压缩" if size > max_size else "✅"
            print(f"  - {m}: ~{size/1024:.0f}KB {flag}")
        return

    # 按月份分组写入
    months = {}
    for s in sessions:
        months.setdefault(s["date"][:7], []).append(s)

    written = []
    for m in sorted(months):
        content = build_header(len(sessions), args.since)
        for s in sorted(months[m], key=lambda x: x["date"]):
            content += render_session(s)
        path = write_grouped(m, content, max_size)
        written.append(path)

    # 汇总信息
    print(f"✅ 导出完成: {len(sessions)} 个会话 → {len(written)} 个文件")
    for w in written:
        size = os.path.getsize(w) if os.path.exists(w) else 0
        print(f"  📄 {os.path.basename(w)} ({size/1024:.0f}KB)")


if __name__ == "__main__":
    main()
