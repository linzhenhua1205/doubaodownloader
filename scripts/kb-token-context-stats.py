#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#================================================================
# kb-token-context-stats.py v1.1 — 上下文 Token 消耗统计器（日报第 6 脚本）
#
# 用途：每日统计三类上下文 token 消耗，供日报「🔤 上下文 Token 监控」
#       模块消费：
#       (1) system tokens —— 系统提示词核心文件（AGENT/USER/RULE/MEMORY）
#                             + 固定框架估算（工具定义/系统结构）
#       (2) skills tokens  —— skills/ 下所有 SKILL.md：
#                             desc（frontmatter description 注入量）
#                             + 文件全量（读取时消耗）
#       (3) file tokens    —— 其他上下文文件：
#                             当日 memory 文件 + knowledge/index+README
#                             + knowledge/ 全量（参考）
#
# 输出：
#   - CSV 追加：knowledge/weekly-reports/07_kb_stat/00.token-consumption-analysis/
#               token-context-daily.csv（每日一行，幂等：同日重复执行不重复追加）
#   - ASCII 趋势图（最近 14 天）→ stdout + tmp/kb-token-context-trend-{date}.md
#   - 告警状态（WARN ≥30K / CRIT ≥80K，阈值可配）
#
# Token 估算方法（无 tiktoken 时的启发式，与 07-28 历史报告口径衔接）：
#   tokens = CJK 字符数 × 0.7 + 非 CJK 字符数 / 4
#   精度说明：中英混合文档估算偏差 ±20%，趋势跟踪用同一口径，相对变化可信；
#   如需精确值，接入真实 tokenizer（tiktoken/cl100k 或模型原生）后替换 est_tokens()
#
# 用法：
#   python3 scripts/kb-token-context-stats.py                # 今天
#   python3 scripts/kb-token-context-stats.py --date 2026-08-14
#   python3 scripts/kb-token-context-stats.py --warn 30000 --crit 80000
#
# 变更日志：
#   2026-08-14 v1.1 口径校正：skills desc 统计改为「压缩后真实注入值」——
#     ① count/desc 只计顶层技能（104，排除 marketing 45 嵌套子技能，与 formatter 注入口径一致）；
#     ② desc 用 formatter 同款压缩逻辑（_condense_desc_for_prompt）后估算；
#     ③ CSV 结构不变，仅值口径变化（历史行已重算，changelog 标注断点）
#   2026-08-14 v1 created（日报 v4.2：上下文 Token 监控模块）
#================================================================

import argparse
import csv
import os
import re
import sys
from collections import OrderedDict
from datetime import datetime, timedelta

WORKSPACE = os.path.expanduser("~/cow")
OUT_DIR = os.path.join(WORKSPACE,
    "knowledge/weekly-reports/07_kb_stat/00.token-consumption-analysis")
CSV_PATH = os.path.join(OUT_DIR, "token-context-daily.csv")

# 系统提示词核心文件（注入上下文的关键全局文件）
SYSTEM_FILES = ["AGENT.md", "USER.md", "RULE.md", "MEMORY.md"]
# 固定系统框架估算 tokens（工具定义 12 个 + 系统结构 + 知识系统描述等，
# 不随文件变化；07-28 报告口径约 14.8K，系统优化后保守取 8K，可 --fixed 调整）
SYSTEM_FIXED_EST = 8000

# 阈值（tokens）：WARN 30K / CRIT 80K，可 --warn/--crit 覆盖
WARN_TOKENS = 30000
CRIT_TOKENS = 80000

# ─────────────────────────────────────────────
# Token 估算
# ─────────────────────────────────────────────
CJK_RE = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\u3000-\u303f\uff00-\uffef]')

def est_tokens(text: str) -> int:
    """启发式 token 估算：CJK 字符 ×0.7 + 非 CJK /4"""
    if not text:
        return 0
    cjk = len(CJK_RE.findall(text))
    other = len(text) - cjk
    return int(round(cjk * 0.7 + other / 4.0))

def file_tokens(path: str):
    """返回 (tokens, bytes)；文件不存在返回 (0, 0)"""
    if not os.path.isfile(path):
        return 0, 0
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception:
        return 0, 0
    return est_tokens(content), len(content.encode("utf-8"))

def parse_frontmatter_desc(path: str) -> str:
    """提取 SKILL.md frontmatter 中的 description 字段（注入 system prompt 的量）"""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            head = f.read(4000)
    except Exception:
        return ""
    m = re.search(r'^description:\s*["\']?(.+?)["\']?\s*$', head, re.M)
    if m:
        return m.group(1)
    m2 = re.search(r'^description:\s*(.+)$', head, re.M)
    return m2.group(1) if m2 else ""


# ── v1.1：与 CowAgent formatter 对齐的 desc 压缩（口径校正）──────────
# 背景：实际注入 system prompt 的并非 SKILL.md frontmatter 原始 description，
#       而是 agent/skills/formatter.py::_condense_description_for_prompt 压缩后的
#       keyword 级摘要（~300字 → ~100-200字）。v1.1 起 desc 统计采用同一压缩逻辑，
#       使 CSV 的 skills_desc_tok 反映「真实注入量」而非原始文档量。
# 同步基准：/home/lzh/CowAgent/agent/skills/formatter.py (2026-08-14 快照)
_CONDENSE_CORE_MAX = 100   # 核心句最大长度
_CONDENSE_TRIG_MAX = 6     # 触发关键词最多 6 个
_CONDENSE_TOTAL_MAX = 200  # 总长度上限

def _condense_desc_for_prompt(desc: str) -> str:
    """复刻 formatter._condense_description_for_prompt 的压缩逻辑（v1.1）"""
    if not desc:
        return ""
    text = desc.replace("\n", " ").strip()

    # ── 提取触发关键词 ──
    trigger_keywords = []
    for pattern in (
        re.compile(r'(?:Use when|USE WHEN|Triggers?|Trig)[:：]\s*(.*?)$', re.DOTALL),
        re.compile(r'(?:触发词|触发场景|触发)[：:]\s*(.*?)$', re.DOTALL),
    ):
        match = pattern.search(text)
        if match:
            raw = match.group(1).strip()
            parts = re.split(
                r'(?:[,;，；]|(?:\s*[•\-]\s*)|\s+(?=[\(\[ ]?\d+[\)\. ]))\s*',
                raw,
            )
            for p in parts:
                p = p.strip()
                if not p or len(p) < 3:
                    continue
                p = re.sub(r'^[\(\[ ]?\d+[\)\. ]?\s*', '', p).strip()
                if not p or len(p) < 3:
                    continue
                p = re.sub(r'\s*[\(\[ ]\d+[\)\. ]?\s*$', '', p).strip()
                if not p or len(p) < 3:
                    continue
                p = p.rstrip('.。')[:40].strip()
                if p and p not in trigger_keywords:
                    trigger_keywords.append(p)
                if len(trigger_keywords) >= _CONDENSE_TRIG_MAX:
                    break
            break

    # 兜底：「当用户……时」模式
    if not trigger_keywords:
        match = re.search(r'当用户(.*?)时', text)
        if match:
            kw_text = match.group(1).strip()
            parts = re.split(r'[,;，；、](?:\s*(?:\d+[\)\. ])\s*)?', kw_text)
            for p in parts:
                p = p.strip()
                if not p or len(p) < 3:
                    continue
                p = p[:35].strip()
                if p and p not in trigger_keywords:
                    trigger_keywords.append(p)
                if len(trigger_keywords) >= _CONDENSE_TRIG_MAX:
                    break

    # ── 提取核心动作句 ──
    core = text
    for pat in (r'\s+Use when', r'\s+USE WHEN', r'\s+Triggers?',
                r'\s+触发词', r'\s+触发场景'):
        m = re.search(pat, text)
        if m:
            core = text[:m.start()].strip()
            break
    if len(core) > _CONDENSE_CORE_MAX:
        sents = re.split(r'(?<=[。！？.!?])\s+(?=[A-Z\u4e00-\u9fff])', core)
        if len(sents) > 1 and len(sents[0]) <= _CONDENSE_CORE_MAX:
            core = sents[0]
    if len(core) > _CONDENSE_CORE_MAX:
        core = core[:_CONDENSE_CORE_MAX - 3] + '...'

    result = core
    if trigger_keywords:
        result += ' | ' + ', '.join(trigger_keywords)
    if len(result) > _CONDENSE_TOTAL_MAX:
        result = result[:_CONDENSE_TOTAL_MAX - 3] + '...'
    return result


def _is_top_level_skill(dirpath: str, skills_dir: str) -> bool:
    """判断是否为顶层技能目录（含 SKILL.md 的顶层目录）。

    排除嵌套技能（如 marketing/onboarding）：嵌套技能属于技能组内部资产，
    不单独注入 system prompt（formatter 只注入技能组本身）。
    """
    rel = os.path.relpath(dirpath, skills_dir)
    return os.sep not in rel

# ─────────────────────────────────────────────
# 采集
# ─────────────────────────────────────────────
def collect_system(fixed_est=SYSTEM_FIXED_EST):
    """系统 token：4 个全局文件 + 固定框架"""
    parts = {}
    for f in SYSTEM_FILES:
        tok, _ = file_tokens(os.path.join(WORKSPACE, f))
        parts[f] = tok
    total = sum(parts.values()) + fixed_est
    return parts, total

def collect_skills():
    """skills token：注入 desc（压缩后真实值）+ 文件全量（读取时消耗）

    v1.1 口径校正：
      - count / desc_tokens 只统计顶层技能（有 SKILL.md 的顶层目录），
        与 formatter 注入口径一致（嵌套技能如 marketing/xxx 不单独注入）；
      - desc_tokens 用 _condense_desc_for_prompt 压缩后估算，
        反映「真实注入 system prompt 的量」（此前为原始 desc 全量，偏大 2-5×）。
      - files_tokens / files_bytes 保持全量（读取时消耗参考口径）。
    """
    skills_dir = os.path.join(WORKSPACE, "skills")
    desc_tokens = 0
    raw_desc_tokens = 0
    file_tokens_total = 0
    file_bytes = 0
    count = 0
    if os.path.isdir(skills_dir):
        for root, _, files in os.walk(skills_dir):
            for fn in files:
                if fn == "SKILL.md":
                    p = os.path.join(root, fn)
                    tok, byt = file_tokens(p)
                    file_tokens_total += tok
                    file_bytes += byt
                    desc = parse_frontmatter_desc(p)
                    # 只统计顶层技能（注入口径）
                    if _is_top_level_skill(root, skills_dir):
                        count += 1
                        raw_desc_tokens += est_tokens(desc)
                        desc_tokens += est_tokens(_condense_desc_for_prompt(desc))
    return {"count": count, "desc_tokens": desc_tokens,
            "raw_desc_tokens": raw_desc_tokens,
            "files_tokens": file_tokens_total, "files_bytes": file_bytes}

def collect_files(today: str):
    """文件 token：当日 memory + knowledge/index+README + knowledge 全量参考"""
    result = {}
    # 当日 memory（若无则找最近一天）
    mem_path = os.path.join(WORKSPACE, "memory", f"{today}.md")
    if not os.path.isfile(mem_path):
        mem_path = ""
        for delta in range(1, 8):
            d = (datetime.strptime(today, "%Y-%m-%d") - timedelta(days=delta)).strftime("%Y-%m-%d")
            cand = os.path.join(WORKSPACE, "memory", f"{d}.md")
            if os.path.isfile(cand):
                mem_path = cand
                break
    result["mem_daily_tokens"], result["mem_daily_bytes"] = file_tokens(mem_path) if mem_path else (0, 0)

    # knowledge/index.md + README.md（常被加载的索引）
    idx_tok = 0
    for f in ["knowledge/index.md", "knowledge/README.md"]:
        t, _ = file_tokens(os.path.join(WORKSPACE, f))
        idx_tok += t
    result["kb_index_tokens"] = idx_tok

    # knowledge/ 全量（参考：知识库总体规模）
    kb_dir = os.path.join(WORKSPACE, "knowledge")
    kb_tok, kb_byt, kb_files = 0, 0, 0
    if os.path.isdir(kb_dir):
        for root, _, files in os.walk(kb_dir):
            for fn in files:
                if fn.endswith(".md"):
                    p = os.path.join(root, fn)
                    t, b = file_tokens(p)
                    kb_tok += t
                    kb_byt += b
                    kb_files += 1
    result.update({"kb_total_tokens": kb_tok, "kb_total_bytes": kb_byt,
                   "kb_files": kb_files})
    return result

# ─────────────────────────────────────────────
# 输出
# ─────────────────────────────────────────────
def load_history():
    """读取已有 CSV（若无则空列表），返回行 dict 列表"""
    if not os.path.isfile(CSV_PATH):
        return []
    rows = []
    try:
        with open(CSV_PATH, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
    except Exception:
        return []
    return rows

CSV_HEADER = [
    "date",
    "sys_agent_tok", "sys_user_tok", "sys_rule_tok", "sys_memory_tok",
    "sys_fixed_est", "system_total_tok", "sys_total_bytes",
    "skills_count", "skills_desc_tok", "skills_files_tok", "skills_bytes",
    "mem_daily_tok", "kb_index_tok",
    "kb_total_tok", "kb_total_bytes", "kb_files",
    "grand_total_tok", "warn_level",
]

def write_csv(today, sys_parts, sys_total, sys_bytes, sk, fl, warn_level):
    """幂等写入：同日已存在则更新该行，否则追加"""
    rows = load_history()
    row = OrderedDict()
    row["date"] = today
    for k, v in sys_parts.items():
        row[f"sys_{k.replace('.md','').lower()}_tok"] = v
    row["sys_fixed_est"] = SYSTEM_FIXED_EST
    row["system_total_tok"] = sys_total
    row["sys_total_bytes"] = sys_bytes
    row["skills_count"] = sk["count"]
    row["skills_desc_tok"] = sk["desc_tokens"]
    row["skills_files_tok"] = sk["files_tokens"]
    row["skills_bytes"] = sk["files_bytes"]
    row["mem_daily_tok"] = fl["mem_daily_tokens"]
    row["kb_index_tok"] = fl["kb_index_tokens"]
    row["kb_total_tok"] = fl["kb_total_tokens"]
    row["kb_total_bytes"] = fl["kb_total_bytes"]
    row["kb_files"] = fl["kb_files"]
    row["grand_total_tok"] = sys_total + sk["desc_tokens"] + fl["mem_daily_tokens"] + fl["kb_index_tokens"]
    row["warn_level"] = warn_level

    # 幂等：同日替换
    rows = [r for r in rows if r.get("date") != today]
    rows.append(row)
    # 按日期排序（CSV 追加，旧→新）
    rows.sort(key=lambda r: r.get("date", ""))

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    return rows

def ascii_sparkline(values, width=28):
    """把数值序列渲染成 ASCII 折线（字符高度 5 级），保留 1 位小数语义"""
    if not values:
        return "(无数据)"
    vmin, vmax = min(values), max(values)
    if vmax == vmin:
        span = 1.0
    else:
        span = vmax - vmin
    levels = "▁▂▃▄▅▆▇█"
    out = []
    for v in values:
        idx = int((v - vmin) / span * 7)
        out.append(levels[min(7, max(0, idx))])
    return "".join(out)

def render_trend(rows, days=14):
    """渲染最近 N 天趋势表（ASCII）"""
    recent = rows[-days:]
    if not recent:
        return "(暂无历史数据，需累计 ≥2 天)"
    dates = [r["date"] for r in recent]
    sys_vals = [int(r.get("system_total_tok", 0)) for r in recent]
    sk_desc = [int(r.get("skills_desc_tok", 0)) for r in recent]
    sk_files = [int(r.get("skills_files_tok", 0)) for r in recent]

    lines = []
    lines.append(f"最近 {len(recent)} 天趋势（单位 K tokens；▁→█ 表示相对大小）")
    lines.append("")
    lines.append(f"日期区间: {dates[0]} → {dates[-1]}")
    lines.append("")
    lines.append("系统 token:")
    lines.append(f"  {ascii_sparkline(sys_vals)}  {min(sys_vals)/1000:.1f}K → {max(sys_vals)/1000:.1f}K")
    lines.append("Skills desc 注入:")
    lines.append(f"  {ascii_sparkline(sk_desc)}  {min(sk_desc)/1000:.1f}K → {max(sk_desc)/1000:.1f}K")
    lines.append("Skills 文件全量:")
    lines.append(f"  {ascii_sparkline(sk_files)}  {min(sk_files)/1000:.1f}K → {max(sk_files)/1000:.1f}K")
    lines.append("")
    lines.append("| 日期 | 系统tok | skills注入 | skills全量 | 文件(当日mem+idx) | 告警 |")
    lines.append("|:-----|:-------:|:----------:|:----------:|:-----------------:|:----:|")
    for i, r in enumerate(recent):
        mem = int(r.get("mem_daily_tok", 0)) + int(r.get("kb_index_tok", 0))
        warn = r.get("warn_level", "")
        lines.append(f"| {r['date']} | {int(r.get('system_total_tok',0)):,} | "
                     f"{int(r.get('skills_desc_tok',0)):,} | {int(r.get('skills_files_tok',0)):,} | "
                     f"{mem:,} | {warn} |")
    return "\n".join(lines)

def main():
    ap = argparse.ArgumentParser(description="上下文 Token 消耗统计（日报第 6 脚本）")
    ap.add_argument("date_pos", nargs="?", default=None,
                    help="统计日期（位置参数，兼容 data-gather 调用；默认今天）")
    ap.add_argument("--date", default=None, help="统计日期（默认今天）")
    ap.add_argument("--warn", type=int, default=30000, help="警告阈值 tokens（默认 30000）")
    ap.add_argument("--crit", type=int, default=80000, help="严重阈值 tokens（默认 80000）")
    ap.add_argument("--fixed", type=int, default=8000,
                    help="固定系统框架估算 tokens（默认 8000）")
    args = ap.parse_args()

    today = args.date or args.date_pos or datetime.now().strftime("%Y-%m-%d")
    warn_tok, crit_tok = args.warn, args.crit

    # 采集
    sys_parts, sys_total = collect_system(fixed_est=args.fixed)
    sk = collect_skills()
    fl = collect_files(today)
    sys_bytes = sum(
        os.path.getsize(os.path.join(WORKSPACE, f)) for f in SYSTEM_FILES
        if os.path.isfile(os.path.join(WORKSPACE, f))
    )

    # 告警判定：系统总量 或 skills 注入量 超过阈值
    if sys_total >= crit_tok or sk["desc_tokens"] >= crit_tok:
        warn_level = "🔴 CRIT"
    elif sys_total >= warn_tok or sk["desc_tokens"] >= warn_tok:
        warn_level = "🟡 WARN"
    else:
        warn_level = "🟢 OK"

    # 写 CSV（幂等）
    rows = write_csv(today, sys_parts, sys_total, sys_bytes, sk, fl, warn_level)

    # 输出汇总（stdout → 日报消费）
    print(f"# 🔤 上下文 Token 监控（{today}）")
    print("")
    print(f"**统计口径**: 启发式估算（CJK×0.7 + 非CJK/4），偏差±20%，相对趋势可信；精确值需真实 tokenizer")
    print("")
    print("| 类别 | 指标 | Tokens | 说明 |")
    print("|:-----|:-----|:------:|:-----|")
    print(f"| 🧠 系统 | AGENT+USER+RULE+MEMORY | {sys_total - args.fixed:,} | 4 全局文件 |")
    print(f"| 🧠 系统 | 固定框架（估算） | {args.fixed:,} | 工具定义+结构（常量，--fixed 可调） |")
    print(f"| 🧠 系统 | **合计** | **{sys_total:,}** | **{warn_level}** |")
    print(f"| 🛠️ Skills | description 注入（压缩后真实值） | {sk['desc_tokens']:,} | {sk['count']} 个顶层技能（原始 desc 共 {sk['raw_desc_tokens']:,} tok，压缩率 {100*(1-sk['desc_tokens']/max(1,sk['raw_desc_tokens'])):.0f}%） |")
    print(f"| 🛠️ Skills | 文件全量（读取时） | {sk['files_tokens']:,} | {sk['files_bytes']/1024:.0f} KB |")
    print(f"| 📄 文件 | 当日 memory | {fl['mem_daily_tokens']:,} | memory/{today}.md |")
    print(f"| 📄 文件 | index+README | {fl['kb_index_tokens']:,} | knowledge/ 索引 |")
    print(f"| 📚 参考 | knowledge/ 全量 | {fl['kb_total_tokens']:,} | {fl['kb_files']} 文件 / {fl['kb_total_bytes']/1024/1024:.0f} MB |")
    print("")
    print(f"**上下文合计（系统+skills注入+当日文件+索引）**: {int(rows[-1]['grand_total_tok']):,} tokens")
    print("")

    # 趋势图（最近 14 天）
    print("## 趋势（最近 14 天）")
    print("")
    print(render_trend(rows))
    print("")
    print(f"**告警阈值**: WARN ≥ {warn_tok/1000:.0f}K tokens / CRIT ≥ {crit_tok/1000:.0f}K tokens")
    print(f"**CSV 数据**: knowledge/weekly-reports/07_kb_stat/00.token-consumption-analysis/token-context-daily.csv")

    # 趋势图落盘供日报引用
    os.makedirs("tmp", exist_ok=True)
    with open(os.path.join(WORKSPACE, "tmp", f"kb-token-context-trend-{today}.md"), "w",
              encoding="utf-8") as f:
        f.write(f"# 🔤 上下文 Token 监控（{today}）\n\n")
        f.write(render_trend(rows))
        f.write("\n")

if __name__ == "__main__":
    main()
