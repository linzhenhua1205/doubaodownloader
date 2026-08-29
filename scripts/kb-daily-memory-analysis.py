#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#================================================================
# kb-daily-memory-analysis.py v1 — 日报 记忆/会话 分析器
#
# 用途：对日报时间窗口内 memory 文件（+ 可用的会话记录）做规则
#       提取，输出供日报「记忆与会话综合分析」模块消费的结构化
#       候选清单。AI 在此基础上精炼为洞察。
#
# 提取三类候选：
#   1. 技术要点候选 — 昨日关注的技术主题（分析/调研/深度/信号）
#   2. skills化/scripts化候选 — 可自动化/重复性工作点
#   3. 约束加固候选 — 踩坑/教训/失效/风险点（需加固的约束）
#
# 用法：
#   ./scripts/kb-daily-memory-analysis.py                    # 上一日
#   ./scripts/kb-daily-memory-analysis.py 2026-08-06         # 指定日期
#
# 输出：
#   - stdout：Markdown 片段（供日报直接嵌入）
#   - tmp/kb-daily-memory-analysis-{REPORT_DATE}.md：同内容落盘
#
# 变更日志：
#   2026-08-07 v1 created（日报升级：新增记忆/会话综合分析模块）
#================================================================

import os
import sys
import re
from datetime import datetime, timedelta

WORKSPACE = os.path.expanduser("~/cow")

# 提取规则（关键词 → 归类）
TECH_KEYWORDS = ["核心", "信号", "发现", "深度", "主线", "洞察", "结论", "论文", "专题", "分析", "调研"]
SKILL_KEYWORDS = ["重复", "手动", "每次", "每周", "每月", "自动化", "脚本", "工具", "批量", "流水线", "模板", "待办", "后续", "可考虑", "挂起"]
CONSTRAINT_KEYWORDS = ["注意", "踩坑", "教训", "修复", "失败", "风险", "失效", "问题", "警告", "错误", "bug", "缺陷", "反爬", "拦截"]


def read_memory(report_date):
    """读取指定日期的 memory 文件"""
    path = os.path.join(WORKSPACE, "memory", f"{report_date}.md")
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as f:
        return f.read()


def read_sessions(report_date):
    """读取日期匹配的会话记录（conversation-log/db-sessions/）"""
    sessions_dir = os.path.join(WORKSPACE, "conversation-log", "db-sessions")
    texts = []
    if not os.path.isdir(sessions_dir):
        return texts
    try:
        for fname in os.listdir(sessions_dir):
            if report_date in fname:
                fpath = os.path.join(sessions_dir, fname)
                try:
                    with open(fpath, encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    texts.append(f"## 会话: {fname}\n{content[:3000]}")
                except Exception:
                    pass
    except Exception:
        pass
    return texts


def extract_candidates(memory_text, sessions_text):
    """规则提取三类候选（互斥归类 + 过滤元数据行）"""
    tech, skill, constraint = [], [], []

    # 低价值元数据行（过滤）
    META_PATTERNS = [
        r"index\.md 已登记", r"log\.md 已写入", r"log\.md 已更新",
        r"三同步完成", r"✅ 完成归档", r"完成归档",
        r"校验 \d+/\d+ PASS", r"verify \d+/\d+ PASS",
    ]
    # 高风险信号词（constraint 强触发）
    CONSTRAINT_STRONG = ["踩坑", "教训", "失效", "失败", "修复", "bug", "缺陷",
                          "反爬", "拦截", "验证码", "⚠️", "❌", "连续第N日"]
    # skills化强触发
    SKILL_STRONG = ["自动化", "脚本", "流水线", "批量", "待办", "挂起",
                    "可考虑", "可复用", "工具链", "一条命令", "周期"]
    # 技术要点强触发
    TECH_STRONG = ["核心信号", "关键新发现", "主线", "洞察", "方法论", "本期TOP5",
                   "观察：", "🔴", "🔥", "结论", "专题", "深潜", "SOTA"]

    current_section = ""
    for line in memory_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("## "):
            current_section = line[3:].strip()
            continue
        if line.startswith("#"):
            continue
        if not (line.startswith("-") or line.startswith("*")):
            continue
        # 过滤元数据行
        if any(re.search(p, line) for p in META_PATTERNS):
            continue
        # 过滤过短行
        if len(line) < 25:
            continue
        # 压缩
        short = line.lstrip("-* ")[:170] + ("..." if len(line.lstrip("-* ")) > 170 else "")
        short = f"[{current_section[:20]}] {short}" if current_section else short

        # 互斥归类：constraint > skill > tech
        if any(k in line for k in CONSTRAINT_STRONG):
            if len(constraint) < 10:
                constraint.append(short)
        elif any(k in line for k in SKILL_STRONG):
            if len(skill) < 10:
                skill.append(short)
        elif any(k in line for k in TECH_STRONG):
            if len(tech) < 12:
                tech.append(short)

    # 会话记录补充（取关键行）
    if sessions_text:
        for s in sessions_text[:2]:
            skill.append(f"[会话] {s[:100]}...")
    return tech, skill, constraint


def render(tech, skill, constraint, report_date):
    lines = []
    lines.append(f"### 🧠 记忆与会话综合分析（{report_date}）")
    lines.append("")
    lines.append(f"> 输入: `memory/{report_date}.md`（{len(tech)+len(skill)+len(constraint)} 条候选）+ 会话记录（规则提取，AI 精炼）")
    lines.append("")

    lines.append(f"**昨日技术要点候选（{len(tech)}）**：")
    if tech:
        for t in tech[:12]:
            lines.append(f"- {t}")
    else:
        lines.append("- 无显著技术要点（记忆文件为空或未覆盖）")
    lines.append("")

    lines.append(f"**可 Skills 化 / Scripts 化候选（{len(skill)}）**：")
    if skill:
        for s in skill[:10]:
            lines.append(f"- {s}")
    else:
        lines.append("- 未识别到明显可自动化点")
    lines.append("")

    lines.append(f"**约束需加固候选（{len(constraint)}）**：")
    if constraint:
        for c in constraint[:10]:
            lines.append(f"- {c}")
    else:
        lines.append("- 未识别到明显约束风险")
    lines.append("")

    lines.append("---")
    lines.append("> ⚡ AI 精炼指引：以上为规则提取候选，请结合上下文判断——")
    lines.append("> ①技术要点按主题聚合为 3-6 条；②skills化点标注优先级（P0 高频重复/P1 周期任务/P2 低频）；")
    lines.append("> ③约束加固点标注类型（流程/格式/安全/数据），并说明加固方式（脚本门禁/检查器/规范）。")
    lines.append("")
    return "\n".join(lines)


def main():
    report_date = sys.argv[1] if len(sys.argv) > 1 else (
        datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    memory_text = read_memory(report_date)
    sessions = read_sessions(report_date)
    sessions_text = "\n".join(sessions)
    if not memory_text and not sessions_text:
        print(f"⚠️ 未找到 {report_date} 的记忆/会话文件（memory/{report_date}.md 或 conversation-log）")
        return
    tech, skill, constraint = extract_candidates(memory_text, sessions_text)
    md = render(tech, skill, constraint, report_date)

    os.makedirs(f"{WORKSPACE}/tmp", exist_ok=True)
    out_path = f"{WORKSPACE}/tmp/kb-daily-memory-analysis-{report_date}.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(md)
    print(f"\n<!-- ✅ 已保存: {out_path} -->", file=sys.stderr)


if __name__ == "__main__":
    main()
