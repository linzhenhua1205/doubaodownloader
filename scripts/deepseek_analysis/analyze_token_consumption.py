#!/usr/bin/env python3
"""
🔬 Token 消耗分析脚本 v3.2
===========================
从真实会话数据 + skills_config + system prompt 构造 → 精确估算 Token 消耗分布，
生成图表化的完整分析报告，输出到 knowledge/weekly-reports/07_kb_stat/。

DeepSeek v4 Flash 官方定价 (2026-07-28):
  - 输入缓存命中: ¥0.02/M tokens
  - 输入缓存未命中: ¥1.00/M tokens
  - 输出: ¥2.00/M tokens

使用方法:
  python3 spec/scripts/analyze_token_consumption.py                                # 标准分析 + 8张图表
  python3 spec/scripts/analyze_token_consumption.py --consumption READINGS.json    # 加载真实 API 消耗数据
  python3 spec/scripts/analyze_token_consumption.py --consumption --daily          # 真实数据每日简报
  python3 spec/scripts/analyze_token_consumption.py --no-charts                    # 纯文本，不生成图表

--consumption 数据格式 (从 DeepSeek Platform 获取):
  {
    "total_cost": 214.62,       # 近30日消费 (¥)
    "total_requests": 31141,    # API 请求次数
    "total_tokens": 2345207163, # Token 总量
    "period_days": 30,          # 统计天数
    "daily_breakdown": [        # 可选：每日分解
      {"date": "2026-06-29", "cost": 7.15, "requests": 1038, "tokens": 78173572}
    ]
  }

依赖:
  pip install matplotlib numpy
  (CJK 字体: apt install fonts-wqy-zenhei 或类似)
"""

import json
import math
import os
import re
import sys
import textwrap
from collections import Counter, defaultdict
from datetime import datetime
from xml.sax.saxutils import escape

# ============================================================
# 配置区
# ============================================================
WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONV_LOG_DIR = os.path.join(WORKSPACE, "conversation-log")
SKILLS_CONFIG = os.path.join(WORKSPACE, "skills", "skills_config.json")
OUTPUT_DIR = os.path.join(WORKSPACE, "knowledge", "weekly-reports", "07_kb_stat")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# DeepSeek v4 Flash 官方定价 (¥/M tokens) — 2026-07-28 从官网获取
MODEL = "deepseek-v4-flash"
PRICING = {
    "input_cache_hit": 0.02,     # ¥0.02/百万tokens (缓存命中)
    "input_cache_miss": 1.00,    # ¥1.00/百万tokens (缓存未命中)
    "output": 2.00,              # ¥2.00/百万tokens (输出固定)
}

# 典型会话参数（基于 conversation-log 数据分析）
TYPICAL_SESSION = {
    "user_input_per_round": 5000,    # 每轮用户输入 + 上下文 (tokens)
    "output_per_round": 2000,        # 每轮 AI 输出 (tokens)
    "rounds_per_session": 4,         # 典型会话轮数
}

# Token 估算系数
# 中英文混合 + XML 的平均 token 密度: ~0.65 tokens/char
TOKEN_FACTOR = 0.65
# 纯中文: ~1.8 chars/token; 纯英文: ~3.5 chars/token; 混合约 ~1.54 chars/token = 0.65 tokens/char

# 系统 prompt 各组件固定值（不含 skills XML，该部分动态计算）
SYS_PROMPT_FIXED = {
    "工具系统 (12 工具定义)": 5000,
    "核心指令 (AGENT+USER+RULE+MEMORY)": 5000,
    "项目上下文 (工作空间/运行时/交流规范)": 5000,
    "记忆+知识系统描述": 4000,
    "其他 (头部说明/分隔)": 800,
}

# 真实 API 消耗数据（通过 --consumption 参数加载）
CONSUMPTION = None  # 加载后为 dict 格式
USE_REAL_DATA = False

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT_TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M")


# ============================================================
# 核心分析函数
# ============================================================

def analyze_skills_config() -> dict:
    """分析 skills_config.json 的真实 token 消耗"""
    with open(SKILLS_CONFIG, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    total = len(cfg)
    enabled_names = [k for k, v in cfg.items() if v.get("enabled", True)]
    disabled_names = [k for k, v in cfg.items() if not v.get("enabled", True)]

    # 模拟 formatter.py 的 XML 渲染
    lines = []
    for name in enabled_names:
        info = cfg[name]
        desc = info.get("description", "")
        location = info.get("location", f"skills/{name}/SKILL.md")
        base_dir = info.get("base_dir", f"skills/{name}")
        lines.append("  <skill>")
        lines.append(f"    <name>{escape(name)}</name>")
        lines.append(f"    <description>{escape(desc)}</description>")
        lines.append(f"    <location>{escape(location)}</location>")
        lines.append(f"    <base_dir>{escape(base_dir)}</base_dir>")
        lines.append("  </skill>")

    rendered_xml = "<available_skills>\n" + "\n".join(lines) + "\n</available_skills>"
    raw_json = json.dumps(cfg, ensure_ascii=False, indent=2)

    # Description 统计
    desc_lens = {k: len(v.get("description", "").strip()) for k, v in cfg.items()}
    desc_vals = sorted(desc_lens.values())
    n = len(desc_vals)

    def percentile(data, p):
        idx = int(len(data) * p / 100)
        return data[min(idx, len(data) - 1)]

    # 按 use-case 标签分组统计（从 description 中提取关键词分类）
    category_map = _categorize_skills(cfg)

    return {
        "total_skills": total,
        "enabled_count": len(enabled_names),
        "disabled_count": len(disabled_names),
        "disabled_names": disabled_names,
        "enabled_names": enabled_names,
        "raw_json_chars": len(raw_json),
        "raw_json_tokens": int(len(raw_json) * TOKEN_FACTOR),
        "rendered_xml_chars": len(rendered_xml),
        "rendered_xml_tokens": int(len(rendered_xml) * TOKEN_FACTOR),
        "avg_desc_chars": sum(desc_vals) / len(desc_vals) if desc_vals else 0,
        "median_desc_chars": desc_vals[len(desc_vals) // 2] if desc_vals else 0,
        "max_desc_chars": max(desc_vals) if desc_vals else 0,
        "min_desc_chars": min(desc_vals) if desc_vals else 0,
        "p25_desc_chars": percentile(desc_vals, 25),
        "p75_desc_chars": percentile(desc_vals, 75),
        "p90_desc_chars": percentile(desc_vals, 90),
        "desc_lens": desc_lens,  # dict: name → length
        "desc_lens_sorted": sorted(desc_lens.items(), key=lambda x: -x[1]),
        "category_map": category_map,
        "top5_longest": sorted(
            desc_lens.items(), key=lambda x: -x[1]
        )[:5],
    }


def _categorize_skills(cfg: dict) -> dict:
    """将 skills 按功能类别分组"""
    categories = defaultdict(list)
    keyword_map = {
        "论文/学术": ["paper", "thesis", "论文", "学术", "citation", "参考文献",
                      "research", "审稿", "review", "rebuttal", "literature", "文献",
                      "publication"],
        "数据处理/分析": ["data", "数据", "分析", "analysis", "统计", "statistics",
                         "engineering"],
        "代码/开发": ["code", "coding", "backend", "前端", "frontend", "design",
                     "programming", "软件", "software", "refactor"],
        "文档/写作": ["doc", "writing", "文档", "markdown", "report", "报告",
                     "knowledge", "知识", "writer"],
        "商业/市场": ["market", "business", "商业", "marketing", "competitor",
                      "竞品", "mckinsey", "industry", "行业", "insight"],
        "系统/运维": ["server", "系统", "system", "fault", "故障", "diagnosis",
                     "运维", "ops", "deploy"],
        "AI/ML": ["AI", "ML", "machine learning", "deep learning", "模型",
                  "model", "training", "训练", "agent", "pipeline"],
        "创意/内容": ["creative", "design", "slide", "PPT", "图片", "image",
                     "营销", "话题", "hot topic", "news"],
        "工具/效率": ["tool", "utility", "转换", "convert", "pdf", "xlsx",
                     "docx", "pptx", "scheduler", "cron", "定时"],
        "其他": [],
    }

    for name, info in cfg.items():
        desc = info.get("description", "").lower()
        categorized = False
        for cat, keywords in keyword_map.items():
            if cat == "其他":
                continue
            if any(kw.lower() in desc or kw.lower() in name.lower() for kw in keywords):
                categories[cat].append(name)
                categorized = True
                break
        if not categorized:
            categories["其他"].append(name)

    return dict(categories)


def analyze_conversation_data() -> dict:
    """分析 conversation-log 中的真实会话数据"""
    if not os.path.isdir(CONV_LOG_DIR):
        return {"error": f"目录不存在: {CONV_LOG_DIR}"}

    all_files = []
    total_chars = 0
    total_lines = 0
    file_count = 0

    for root, dirs, files in os.walk(CONV_LOG_DIR):
        for fname in files:
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", errors="ignore") as f:
                    content = f.read()
                lines = content.count("\n") + 1
                chars = len(content)
                cat = "user_questions" if "user-questions" in root else (
                    "db_sessions" if "db-sessions" in root else "other"
                )
                # 提取日期信息
                date_match = re.search(r"(\d{4}-\d{2}-\d{2})", fname)
                fdate = date_match.group(1) if date_match else "unknown"
                all_files.append({
                    "path": os.path.relpath(fpath, WORKSPACE),
                    "fname": fname,
                    "date": fdate,
                    "lines": lines,
                    "chars": chars,
                    "tokens": int(chars * 0.6),  # 会话文件中文多，~0.6 tokens/char
                    "size": os.path.getsize(fpath),
                    "category": cat,
                })
                total_chars += chars
                total_lines += lines
                file_count += 1
            except Exception as e:
                continue

    if not all_files:
        return {"error": "未找到会话文件"}

    sorted_chars = sorted([f["chars"] for f in all_files])
    sorted_lines = sorted([f["lines"] for f in all_files])
    n = len(sorted_chars)

    # 按分类统计
    by_cat = defaultdict(list)
    for f in all_files:
        by_cat[f["category"]].append(f)

    cat_stats = {}
    for cat, files in by_cat.items():
        chars_list = [f["chars"] for f in files]
        tokens_list = [f["tokens"] for f in files]
        cat_stats[cat] = {
            "count": len(files),
            "avg_chars": sum(chars_list) / len(chars_list),
            "median_chars": sorted(chars_list)[len(chars_list) // 2],
            "avg_tokens": sum(tokens_list) / len(tokens_list),
            "total_tokens": sum(tokens_list),
        }

    # 按日/周/月聚集
    by_date = defaultdict(list)
    for f in all_files:
        by_date[f["date"]].append(f)

    # 找出活跃天
    active_days = sorted(by_date.keys())
    daily_tokens = {d: sum(f["tokens"] for f in files) for d, files in by_date.items()}

    # TOP10 largest
    top10 = sorted(all_files, key=lambda x: -x["chars"])[:10]

    def percentile(data, p):
        idx = int(len(data) * p / 100)
        return data[min(idx, len(data) - 1)]

    return {
        "total_files": file_count,
        "total_lines": total_lines,
        "total_chars": total_chars,
        "total_tokens": sum(f["tokens"] for f in all_files),
        "total_size_kb": sum(f["size"] for f in all_files) / 1024,
        "avg_chars": total_chars / file_count,
        "avg_lines": total_lines / file_count,
        "avg_tokens": int(sum(f["tokens"] for f in all_files) / file_count),
        "median_chars": sorted_chars[n // 2] if n else 0,
        "median_tokens": int(sorted_chars[n // 2] * 0.6) if n else 0,
        "median_lines": sorted_lines[n // 2] if n else 0,
        "percentiles": {
            f"P{p}": {
                "lines": percentile(sorted_lines, p) if sorted_lines else 0,
                "chars": percentile(sorted_chars, p) if sorted_chars else 0,
                "tokens": int(percentile(sorted_chars, p) * 0.6) if sorted_chars else 0,
            }
            for p in [10, 25, 50, 75, 90, 95, 99]
        },
        "category_stats": cat_stats,
        "all_files": all_files,
        "active_days_count": len(active_days),
        "active_days": active_days,
        "daily_tokens": daily_tokens,
        "top10_largest": [
            {"path": f["path"], "lines": f["lines"], "chars": f["chars"],
             "tokens": f["tokens"]}
            for f in top10
        ],
    }


def calc_system_prompt_structure(skills_data: dict) -> dict:
    """计算系统 prompt 的详细结构"""
    skills_tokens = skills_data["rendered_xml_tokens"]

    components = {
        f"Skills XML ({skills_data['enabled_count']} skills)": skills_tokens,
    }
    components.update(SYS_PROMPT_FIXED)

    total = sum(components.values())
    components_with_pct = {
        k: {"tokens": v, "pct": round(v / total * 100, 1)}
        for k, v in components.items()
    }

    return {
        "total_sys_prompt_tokens": total,
        "skills_xml_tokens": skills_tokens,
        "skills_xml_pct": round(skills_tokens / total * 100, 1),
        "components": components_with_pct,
    }


def calc_cost_scenarios(skills_data: dict, sys_prompt: dict) -> dict:
    """计算不同优化场景和缓存模式下的成本"""
    base_sys_tokens = sys_prompt["total_sys_prompt_tokens"]
    skills_tokens = skills_data["rendered_xml_tokens"]

    # --- 场景定义 ---
    scenarios = {}

    # S0: 当前现状
    scenarios["baseline"] = {
        "name": "当前现状",
        "desc": f"{skills_data['enabled_count']} skills, description 未裁剪",
        "sys_tokens": base_sys_tokens,
        "skills_tokens": skills_tokens,
    }

    # S1: 裁剪 description 到中位数
    median_chars = skills_data["median_desc_chars"]
    reduced_skills_tokens = int(
        skills_data["enabled_count"] * (median_chars + 40) * TOKEN_FACTOR
    )
    s1_sys = base_sys_tokens - skills_tokens + reduced_skills_tokens
    scenarios["trim_desc"] = {
        "name": "描述裁剪到中位数",
        "desc": f"描述从 avg {skills_data['avg_desc_chars']:.0f}→{median_chars} chars",
        "sys_tokens": s1_sys,
        "skills_tokens": reduced_skills_tokens,
    }

    # S2: 归档低频 skills (保留 60 个)
    core60 = 60
    s2_ratio = core60 / skills_data["enabled_count"]
    s2_skills = int(skills_tokens * s2_ratio)
    s2_sys = base_sys_tokens - skills_tokens + s2_skills
    scenarios["archive_60"] = {
        "name": f"归档至 {core60} 核心 skills",
        "desc": f"归档 {skills_data['enabled_count'] - core60} 个低频技能",
        "sys_tokens": s2_sys,
        "skills_tokens": s2_skills,
    }

    # S3: 裁剪 + 归档 (保留 60, 描述到中位数)
    s3_skills = int(reduced_skills_tokens * s2_ratio)
    s3_sys = base_sys_tokens - skills_tokens + s3_skills
    scenarios["trim_archive"] = {
        "name": "组合优化 (归档60+描述裁剪)",
        "desc": f"{core60} skills + 中位数描述长度",
        "sys_tokens": s3_sys,
        "skills_tokens": s3_skills,
    }

    # S4: 极端精简 (保留 25 个核心)
    core25 = 25
    s4_ratio = core25 / skills_data["enabled_count"]
    s4_skills = int(skills_tokens * s4_ratio)
    s4_sys = base_sys_tokens - skills_tokens + s4_skills
    scenarios["minimal"] = {
        "name": "极端精简 (25 核心 skills)",
        "desc": "只保留绝对必要的技能",
        "sys_tokens": s4_sys,
        "skills_tokens": s4_skills,
    }

    # 计算每个场景在不同缓存模式下的成本
    for key, sc in scenarios.items():
        sys_t = sc["sys_tokens"]
        user_per_round = TYPICAL_SESSION["user_input_per_round"]
        out_per_round = TYPICAL_SESSION["output_per_round"]
        rounds = TYPICAL_SESSION["rounds_per_session"]

        # 单轮成本 (input + output)
        def round_cost(sys_t, cache_mode):
            """cache_mode: 'hit', 'miss', or 'mixed_first' (首轮未命中后续命中)"""
            if cache_mode == "hit":
                input_cost = (sys_t + user_per_round) * PRICING["input_cache_hit"]
            elif cache_mode == "miss":
                input_cost = (sys_t + user_per_round) * PRICING["input_cache_miss"]
            else:  # mixed_first — 用于首轮
                input_cost = (sys_t + user_per_round) * PRICING["input_cache_miss"]
            output_cost = out_per_round * PRICING["output"]
            return (input_cost + output_cost) / 1_000_000

        # 全命中
        hit_ps = rounds * round_cost(sys_t, "hit")
        # 全未命中
        miss_ps = rounds * round_cost(sys_t, "miss")
        # 混合 (首轮未命中, 后续命中)
        mixed_ps = round_cost(sys_t, "mixed_first") + (rounds - 1) * round_cost(sys_t, "hit")

        sc["daily_5"] = round(mixed_ps * 5, 4)
        sc["daily_10"] = round(mixed_ps * 10, 4)
        sc["daily_20"] = round(mixed_ps * 20, 4)
        sc["daily_30"] = round(mixed_ps * 30, 4)
        sc["cost_per_session_hit"] = round(hit_ps, 4)
        sc["cost_per_session_mixed"] = round(mixed_ps, 4)
        sc["cost_per_session_miss"] = round(miss_ps, 4)

    # 基于基线的节省比例
    baseline_mixed = scenarios["baseline"]["cost_per_session_mixed"]
    for key, sc in scenarios.items():
        if key == "baseline":
            sc["vs_baseline_pct"] = 0
        else:
            savings = baseline_mixed - sc["cost_per_session_mixed"]
            sc["vs_baseline_pct"] = round(savings / baseline_mixed * 100, 1)

    return scenarios


def calc_cache_impact(scenarios: dict) -> dict:
    """计算缓存策略的详细影响"""
    baseline = scenarios["baseline"]

    # 缓存完全命中的理想成本
    hit_cost = baseline["cost_per_session_hit"]
    # 缓存完全未命中的成本
    miss_cost = baseline["cost_per_session_miss"]
    # 混合成本
    mixed_cost = baseline["cost_per_session_mixed"]

    # cache miss penalty = 修改 prompt 的代价
    miss_penalty = miss_cost - mixed_cost
    miss_penalty_ratio = miss_cost / max(hit_cost, 0.001)

    # 如果每天修改 1 次 system prompt (导致多个会话 miss)
    # 假设修改后前 N 个会话 miss, 后续命中
    daily_sessions = 20

    def daily_cost_with_modifications(modifications_per_day):
        """给定每天修改次数时的日成本"""
        if modifications_per_day == 0:
            return round(mixed_cost * daily_sessions, 4)

        # 每次修改导致首轮全价，但后续会话如果 prompt 稳定则命中
        # 简化模型: 每次修改使当次及之后 1 个会话的缓存失效
        miss_sessions_per_mod = 2  # 修改当次 + 下一个会话
        total_miss = min(modifications_per_day * miss_sessions_per_mod, daily_sessions)
        total_hit = daily_sessions - total_miss
        return round(
            total_miss * miss_cost + total_hit * hit_cost, 4
        )

    return {
        "hit_per_session": hit_cost,
        "miss_per_session": miss_cost,
        "mixed_per_session": mixed_cost,
        "miss_vs_hit_ratio": round(miss_penalty_ratio, 1),
        "miss_penalty_per_session": round(miss_penalty, 4),
        "daily_zero_mod": daily_cost_with_modifications(0),
        "daily_one_mod": daily_cost_with_modifications(1),
        "daily_three_mod": daily_cost_with_modifications(3),
        "daily_five_mod": daily_cost_with_modifications(5),
    }


# ============================================================
# 图表生成
# ============================================================

def _init_plot(width=12, height=7):
    """初始化 matplotlib 绘图环境"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # 设置中文字体
    plt.rcParams["font.sans-serif"] = ["WenQuanYi Zen Hei", "SimHei", "Noto Sans CJK SC"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"] = 150

    fig, ax = plt.subplots(figsize=(width, height))
    return fig, ax, plt


def _save_chart(fig, plt, name):
    """保存图表到输出目录"""
    fname = f"{TIMESTAMP}-{name}.png"
    fpath = os.path.join(OUTPUT_DIR, fname)
    fig.tight_layout()
    fig.savefig(fpath, bbox_inches="tight", dpi=150)
    plt.close(fig)
    return fname, fpath


def chart_system_prompt_composition(sys_prompt: dict):
    """图1: 系统 prompt 构成饼图"""
    fig, ax, plt = _init_plot(10, 8)
    comp = sys_prompt["components"]
    labels = [k for k in comp.keys()]
    sizes = [v["pct"] for v in comp.values()]
    tokens = [v["tokens"] for v in comp.values()]
    colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD"]

    wedges, texts, autotexts = ax.pie(
        sizes, labels=None, autopct="%1.1f%%",
        colors=colors[:len(labels)],
        startangle=90, pctdistance=0.75,
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
    )
    for t in autotexts:
        t.set_fontsize(9)

    # 图例 + 数量
    legend_labels = [
        f"{l}  ({t:,} tokens, {s}%)"
        for l, t, s in zip(labels, tokens, sizes)
    ]
    ax.legend(
        wedges, legend_labels,
        title="系统 Prompt 组件",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        fontsize=9,
    )
    ax.set_title(
        f"系统 Prompt Token 构成\n总量: {sys_prompt['total_sys_prompt_tokens']:,} tokens/会话",
        fontsize=13, fontweight="bold", pad=15
    )
    return _save_chart(fig, plt, "01-system-prompt-composition")


def chart_description_distribution(skills_data: dict):
    """图2: Skills description 长度分布 (Top 30)"""
    fig, ax, plt = _init_plot(14, 8)

    top_n = skills_data["desc_lens_sorted"][:30]
    names = [t[0] for t in top_n]
    lengths = [t[1] for t in top_n]

    bars = ax.barh(range(len(names)), lengths, color="#45B7D1", edgecolor="white", height=0.7)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("Description 长度 (chars)", fontsize=10)
    ax.set_title(
        f"Skills Description 长度分布 (Top 30 / {skills_data['enabled_count']} skills)\n"
        f"中位数: {skills_data['median_desc_chars']} | "
        f"平均: {skills_data['avg_desc_chars']:.0f} | "
        f"最长: {skills_data['max_desc_chars']} chars",
        fontsize=12, fontweight="bold"
    )

    # 在条上标注数值
    for bar, length in zip(bars, lengths):
        ax.text(bar.get_width() + 10, bar.get_y() + bar.get_height() / 2,
                str(length), va="center", fontsize=7, color="#333")

    # 中位数线
    ax.axvline(x=skills_data["median_desc_chars"], color="#FF6B6B",
               linestyle="--", linewidth=1, label=f"中位数 ({skills_data['median_desc_chars']})")
    ax.legend(fontsize=9)

    return _save_chart(fig, plt, "02-description-distribution")


def chart_conversation_size_distribution(conv_data: dict):
    """图3: 会话文件大小分布直方图"""
    if "error" in conv_data:
        return None, None

    fig, ax, plt = _init_plot(12, 7)

    all_files = conv_data["all_files"]
    chars_list = [f["chars"] for f in all_files]

    # 对数分箱更好展示偏态分布
    bins = 40
    ax.hist(chars_list, bins=bins, color="#4ECDC4", edgecolor="white",
            alpha=0.8, log=True)

    # 百分位线
    pc = conv_data["percentiles"]
    colors = {"P25": "orange", "P50": "red", "P75": "purple", "P90": "brown"}
    for p_name, color in colors.items():
        val = pc[p_name]["chars"]
        ax.axvline(x=val, color=color, linestyle="--", linewidth=1.5,
                   label=f"{p_name} = {val:,} chars ({pc[p_name]['tokens']:,} tokens)")

    ax.set_xlabel("文件大小 (chars)", fontsize=10)
    ax.set_ylabel("文件数量 (对数尺度)", fontsize=10)
    ax.set_title(
        f"会话文件大小分布 (n={conv_data['total_files']})\n"
        f"P50: {pc['P50']['chars']:,} chars (~{pc['P50']['tokens']:,} tokens) | "
        f"P75: {pc['P75']['chars']:,} chars (~{pc['P75']['tokens']:,} tokens)",
        fontsize=12, fontweight="bold"
    )
    ax.legend(fontsize=9)

    # 添加分类统计文字
    cat_info = []
    for cat, stats in conv_data["category_stats"].items():
        cat_info.append(f"{cat}: {stats['count']} 文件, "
                        f"中位数 {stats['median_chars']:,.0f} chars")
    textstr = "\n".join(cat_info)
    ax.text(0.98, 0.95, textstr, transform=ax.transAxes, fontsize=8,
            verticalalignment="top", horizontalalignment="right",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    return _save_chart(fig, plt, "03-conversation-size-distribution")


def chart_optimization_scenarios(scenarios: dict):
    """图4: 优化场景成本对比 (分组柱状图)"""
    fig, ax, plt = _init_plot(14, 7)

    names = [s["name"] for s in scenarios.values()]
    hit_costs = [s["cost_per_session_hit"] for s in scenarios.values()]
    mixed_costs = [s["cost_per_session_mixed"] for s in scenarios.values()]
    miss_costs = [s["cost_per_session_miss"] for s in scenarios.values()]
    sys_tokens = [s["sys_tokens"] for s in scenarios.values()]

    x = range(len(names))
    width = 0.25

    bars1 = ax.bar([i - width for i in x], hit_costs, width,
                   label="全缓存命中", color="#4ECDC4", edgecolor="white")
    bars2 = ax.bar(x, mixed_costs, width,
                   label="混合 (首轮未命中)", color="#45B7D1", edgecolor="white")
    bars3 = ax.bar([i + width for i in x], miss_costs, width,
                   label="全未命中 (无缓存)", color="#FF6B6B", edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=9, rotation=15, ha="right")
    ax.set_ylabel("每会话成本 (¥)", fontsize=10)
    ax.set_title(
        "优化场景成本对比 (每会话, 4轮交互)\n¥0.02/M (缓存命中) | ¥1.00/M (未命中) | ¥2.00/M (输出)",
        fontsize=12, fontweight="bold"
    )
    ax.legend(fontsize=9)

    # 在柱上标注 tokens
    for bar, tokens in zip(bars2, sys_tokens):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.0002,
                f"{tokens:,}T", ha="center", va="bottom", fontsize=8,
                color="#333", rotation=0)

    # 添加节省百分比标注
    baseline_mixed = list(scenarios.values())[0]["cost_per_session_mixed"]
    for i, (key, sc) in enumerate(scenarios.items()):
        if key == "baseline":
            continue
        pct = sc["vs_baseline_pct"]
        y_pos = mixed_costs[i] + 0.0004
        ax.annotate(
            f"-{pct}%",
            (i, y_pos),
            fontsize=9, fontweight="bold", color="green",
            ha="center", va="bottom",
        )

    return _save_chart(fig, plt, "04-optimization-scenarios")


def chart_session_cost_impact(scenarios: dict):
    """图5: 会话数对日成本的影响"""
    fig, ax, plt = _init_plot(12, 7)

    session_counts = [1, 3, 5, 10, 15, 20, 25, 30, 40, 50]

    colors = ["#FF6B6B", "#E67E22", "#F1C40F", "#2ECC71", "#3498DB"]
    for (key, sc), color in zip(scenarios.items(), colors):
        costs = [sessions * sc["cost_per_session_mixed"] for sessions in session_counts]
        ax.plot(session_counts, costs, marker="o", linewidth=2,
                color=color, label=sc["name"], markersize=4)

    ax.set_xlabel("每日会话数", fontsize=10)
    ax.set_ylabel("日成本 (¥)", fontsize=10)
    ax.set_title(
        "每日会话数对成本的线性影响\n(混合缓存模式, 基于当前定价 ¥0.02/¥1.00/¥2.00/M)",
        fontsize=12, fontweight="bold"
    )
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.set_xlim(0, 52)

    # 标注典型区域
    ax.axvspan(10, 30, alpha=0.08, color="gray", label="典型范围 (10-30 会话)")
    ax.text(20, ax.get_ylim()[1] * 0.95, "← 典型范围 →",
            ha="center", fontsize=9, color="gray", fontstyle="italic")

    return _save_chart(fig, plt, "05-session-cost-impact")


def chart_cache_impact_analysis(skills_data: dict, sys_prompt: dict):
    """图6: 修改频率对缓存成本的影响"""
    fig, ax, plt = _init_plot(12, 7)

    base_sys = sys_prompt["total_sys_prompt_tokens"]
    daily_sessions = 20
    hit_cost = (
        (base_sys + TYPICAL_SESSION["user_input_per_round"])
        * PRICING["input_cache_hit"] + TYPICAL_SESSION["output_per_round"]
        * PRICING["output"]
    ) / 1_000_000 * TYPICAL_SESSION["rounds_per_session"]

    miss_cost = (
        (base_sys + TYPICAL_SESSION["user_input_per_round"])
        * PRICING["input_cache_miss"] + TYPICAL_SESSION["output_per_round"]
        * PRICING["output"]
    ) / 1_000_000 * TYPICAL_SESSION["rounds_per_session"]

    mixed_cost_no_mod = hit_cost  # 不修改时全部命中
    # 实际上不修改时也是首轮可能未命中，后续命中
    mixed_cost_no_mod = (
        miss_cost + (TYPICAL_SESSION["rounds_per_session"] - 1) * hit_cost
    )

    # 不同修改次数
    mod_counts = list(range(0, 11))
    daily_costs = []
    for mods in mod_counts:
        miss_sessions = min(mods * 2, daily_sessions)  # 每次修改影响 2 个会话
        hit_sessions = daily_sessions - miss_sessions
        cost = (miss_sessions * miss_cost + hit_sessions * hit_cost) / daily_sessions * daily_sessions
        daily_costs.append(cost)

    ax.bar(mod_counts, daily_costs, color="#45B7D1", edgecolor="white", width=0.7)

    # 零修改基线
    ax.axhline(y=daily_costs[0], color="#2ECC71", linestyle="--", linewidth=1.5,
               label=f"不修改: ¥{daily_costs[0]:.4f}/天")

    ax.set_xlabel("每天 System Prompt 修改次数", fontsize=10)
    ax.set_ylabel("日成本 (¥, 20会话)", fontsize=10)
    ax.set_xticks(mod_counts)
    ax.set_title(
        "System Prompt 修改频率对缓存成本的影响\n"
        f"每次修改导致 ~2 个会话缓存失效 (¥{miss_cost:.4f}/会话 vs ¥{hit_cost:.4f}/会话)",
        fontsize=12, fontweight="bold"
    )
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis="y")

    # 标注风险区域
    ax.axhspan(daily_costs[0], max(daily_costs), alpha=0.1, color="red")
    for i, cost in enumerate(daily_costs):
        ax.text(i, cost + 0.0002, f"¥{cost:.4f}", ha="center", fontsize=8)

    return _save_chart(fig, plt, "06-cache-impact")


def chart_category_distribution(skills_data: dict):
    """图7: Skills 按功能类别分布"""
    fig, ax, plt = _init_plot(12, 7)

    cat_map = skills_data["category_map"]
    categories = list(cat_map.keys())
    counts = [len(v) for v in cat_map.values()]

    colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
              "#DDA0DD", "#98D8C8", "#F7DC6F", "#85C1E9", "#E8DAEF"]
    bars = ax.barh(range(len(categories)), counts, color=colors[:len(categories)],
                   edgecolor="white", height=0.6)

    ax.set_yticks(range(len(categories)))
    ax.set_yticklabels(categories, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Skills 数量", fontsize=10)
    ax.set_title(
        f"Skills 按功能类别分布 (总计: {skills_data['enabled_count']} skills)",
        fontsize=12, fontweight="bold"
    )

    for bar, count, cat in zip(bars, counts, categories):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{count} ({count/skills_data['enabled_count']*100:.0f}%)",
                va="center", fontsize=9)

    return _save_chart(fig, plt, "07-category-distribution")


def chart_conversation_timeline(conv_data: dict):
    """图8: 会话时间线 (按日期聚集的 token 量)"""
    if "error" in conv_data or conv_data["active_days_count"] == 0:
        return None, None

    fig, ax, plt = _init_plot(14, 6)

    days = conv_data["active_days"]
    daily_tokens = conv_data["daily_tokens"]
    values = [daily_tokens[d] for d in days]

    if len(days) <= 1:
        # 数据不足，跳过
        plt.close(fig)
        return None, None

    ax.fill_between(range(len(days)), values, alpha=0.3, color="#4ECDC4")
    ax.plot(range(len(days)), values, marker="o", color="#45B7D1",
            linewidth=1.5, markersize=3)

    # 标注关键日期
    if len(days) > 5:
        # 按一定间隔标注
        step = max(1, len(days) // 10)
        tick_positions = list(range(0, len(days), step))
        ax.set_xticks(tick_positions)
        ax.set_xticklabels([days[i] for i in tick_positions], rotation=45, fontsize=8)

    ax.set_xlabel("日期", fontsize=10)
    ax.set_ylabel("Token 量", fontsize=10)
    ax.set_title(
        "每日会话 Token 量时间线\n"
        f"共 {conv_data['active_days_count']} 个活跃日, "
        f"总计 ~{conv_data['total_tokens']:,} tokens",
        fontsize=12, fontweight="bold"
    )
    ax.grid(True, alpha=0.3, linestyle="--")

    return _save_chart(fig, plt, "08-conversation-timeline")


# ============================================================
# 报告生成
# ============================================================

def _fmt_cost(val):
    """格式化金额"""
    if val < 0.01:
        return f"¥{val:.4f}"
    if val < 1:
        return f"¥{val:.3f}"
    return f"¥{val:.2f}"


def generate_report(skills_data: dict, conv_data: dict, sys_prompt: dict,
                    scenarios: dict, cache_impact: dict,
                    chart_files: list) -> str:
    """生成完整的 Markdown 报告"""
    lines = []
    def w(s=""):
        lines.append(s)

    # Count by category for the report
    cat_counts = {k: len(v) for k, v in skills_data["category_map"].items()}
    top_category = max(cat_counts, key=cat_counts.get) if cat_counts else "N/A"

    w(f"# 📊 Token 消耗量化分析报告")
    w(f"> **自动生成**: {REPORT_TIMESTAMP}")
    w(f"> **模型**: {MODEL} | **定价**: 缓存命中 ¥{PRICING['input_cache_hit']}/M, "
      f"未命中 ¥{PRICING['input_cache_miss']}/M, 输出 ¥{PRICING['output']}/M")
    w(f"> **数据源**: `skills_config.json` ({skills_data['enabled_count']} en skills) + "
      f"`conversation-log/` ({conv_data.get('total_files', 'N/A')} 文件)")
    w()

    # ========== 1. Summary ==========
    w("## 1. 🎯 核心摘要")
    w()
    w(f"| 指标 | 数值 |")
    w(f"|:-----|:----:|")
    w(f"| 系统 Prompt 总量 | **{sys_prompt['total_sys_prompt_tokens']:,} tokens**/会话 |")
    w(f"| Skills XML 占比 | **{sys_prompt['skills_xml_tokens']:,} tokens ({sys_prompt['skills_xml_pct']}%)** |")
    w(f"| 每会话成本 (混合) | {_fmt_cost(scenarios['baseline']['cost_per_session_mixed'])} |")
    w(f"| 日成本 (20会话, 混合) | {_fmt_cost(scenarios['baseline']['daily_20'])} |")
    w(f"| 缓存命中 vs 未命中倍数 | **{cache_impact['miss_vs_hit_ratio']}x** |")
    w(f"| 缓存失效代价/次修改 | {_fmt_cost(cache_impact['daily_one_mod'] - cache_impact['daily_zero_mod'])}/天 |")
    w(f"| 最大节省潜力 (组合优化) | **-{max(s['vs_baseline_pct'] for k,s in scenarios.items() if k != 'baseline')}%** |")
    w(f"| 历史会话总量 | {conv_data.get('total_files', 'N/A')} 文件, "
      f"~{conv_data.get('total_tokens', 0):,} tokens |")

    # 帕累托分析
    w()
    w("**帕累托分析** (Top 3 消耗源 → ~80%):")
    w()
    w(f"1. **Skills XML 系统 prompt** ({sys_prompt['skills_xml_pct']}%) → 固定成本, 影响缓存")
    w(f"2. **会话层固定成本** (64% 系统 prompt 占比) → 减少会话数等比减少")
    w(f"3. **缓存失效成本** ({cache_impact['miss_vs_hit_ratio']}x 惩罚) → 稳定性 > 极致优化")
    w()

    # ========== 2. System Prompt Breakdown ==========
    w("## 2. 🧩 系统 Prompt 构成分析")
    w()
    w(f"![系统 Prompt 构成]({chart_files[0]})" if chart_files[0] else "")
    w()
    w("| 组件 | Tokens | 占比 |")
    w("|:-----|:------:|:----:|")
    comp = sys_prompt["components"]
    for name, data in comp.items():
        w(f"| {name} | {data['tokens']:,} | {data['pct']}% |")
    w()

    total_tokens = sum(v["tokens"] for v in comp.values())
    skills_tokens = comp.get(
        list(comp.keys())[0], {}  # Skills XML is first key
    )
    # Recalculate ratios properly
    w(f"> **当前系统 prompt 总量**: ~{total_tokens:,} tokens/会话。"
      f"占总 Token 消耗的 ~{total_tokens/(total_tokens + TYPICAL_SESSION['rounds_per_session']*(TYPICAL_SESSION['user_input_per_round']+TYPICAL_SESSION['output_per_round']))*100:.0f}%"
      f" (以 {TYPICAL_SESSION['rounds_per_session']} 轮会话计)")

    # ========== 3. Skills Analysis ==========
    w()
    w("## 3. 📦 Skills 配置深度分析")
    w()

    # 3.1 基础统计
    w("### 3.1 基础统计")
    w()
    w(f"| 指标 | 数值 |")
    w(f"|:-----|:----:|")
    w(f"| Skills 总数 | {skills_data['total_skills']} |")
    w(f"| Enabled | **{skills_data['enabled_count']}** |")
    w(f"| Disabled | {skills_data['disabled_count']} |")
    w(f"| Raw JSON 大小 | {skills_data['raw_json_chars']:,} chars ≈ ~{skills_data['raw_json_tokens']:,} tokens |")
    w(f"| 渲染后 XML 大小 | {skills_data['rendered_xml_chars']:,} chars ≈ **~{skills_data['rendered_xml_tokens']:,} tokens** |")
    w()

    # 3.2 Description 长度分析
    w("### 3.2 Description 长度分析")
    w()
    w(f"![Description 分布]({chart_files[1]})" if chart_files[1] else "")
    w()
    w(f"| 统计量 | 长度 (chars) | 估算 Token |")
    w(f"|:-------|:-----------:|:----------:|")
    w(f"| 最短 | {skills_data['min_desc_chars']} | ~{int(skills_data['min_desc_chars']*TOKEN_FACTOR)} |")
    w(f"| P25 | {skills_data['p25_desc_chars']} | ~{int(skills_data['p25_desc_chars']*TOKEN_FACTOR)} |")
    w(f"| **中位数** | **{skills_data['median_desc_chars']}** | **~{int(skills_data['median_desc_chars']*TOKEN_FACTOR)}** |")
    w(f"| 平均 | {skills_data['avg_desc_chars']:.0f} | ~{int(skills_data['avg_desc_chars']*TOKEN_FACTOR)} |")
    w(f"| P75 | {skills_data['p75_desc_chars']} | ~{int(skills_data['p75_desc_chars']*TOKEN_FACTOR)} |")
    w(f"| P90 | {skills_data['p90_desc_chars']} | ~{int(skills_data['p90_desc_chars']*TOKEN_FACTOR)} |")
    w(f"| 最长 | {skills_data['max_desc_chars']} | ~{int(skills_data['max_desc_chars']*TOKEN_FACTOR)} |")
    w()

    w("**TOP5 最长 Description:**")
    w()
    for name, length in skills_data["top5_longest"]:
        w(f"1. **{name}**: {length} chars (~{int(length*TOKEN_FACTOR)} tokens) — "
          f"需要裁剪到 ≤300 chars 可省 ~{int((length-300)*TOKEN_FACTOR)} tokens/会话")
    w()

    # 3.3 功能类别分布
    w("### 3.3 功能类别分布")
    w()
    w(f"![类别分布]({chart_files[6]})" if chart_files[6] else "")
    w()
    w("| 功能类别 | 数量 | 占比 |")
    w("|:---------|:----:|:----:|")
    for cat, skills_list in sorted(skills_data["category_map"].items(),
                                    key=lambda x: -len(x[1])):
        w(f"| {cat} | {len(skills_list)} | {len(skills_list)/skills_data['enabled_count']*100:.0f}% |")
    w()

    # 3.4 裁剪建议
    w("### 3.4 Description 裁剪建议")
    w()
    w(f"目标: 将全部 description 裁剪到 **≤300 chars**")
    w()
    over_300 = [(n, l) for n, l in skills_data["desc_lens_sorted"] if l > 300]
    w(f"当前超过 300 chars 的 skills: **{len(over_300)}** 个")
    w()
    if over_300:
        w("| Skill | 当前长度 | 裁剪后 | 节省 tokens/会话 |")
        w("|:------|:--------:|:------:|:---------------:|")
        saving_total = 0
        for name, length in over_300[:15]:  # 只列前15个
            save = int((length - 300) * TOKEN_FACTOR)
            saving_total += save
            w(f"| {name} | {length} | 300 | ~{save} |")
        if len(over_300) > 15:
            w(f"| ... 还有 {len(over_300)-15} 个 | ... | ... | ... |")
        w()
        w(f"> 全部裁剪到 300 chars 可节省 **~{saving_total:,} tokens/会话**, "
          f"约 **¥{saving_total * PRICING['input_cache_hit'] / 1_000_000:.4f}/会话 (命中时)**")
    w()

    # ========== 4. 历史会话分析 ==========
    w("## 4. 💬 历史会话数据分析")
    w()
    if "error" in conv_data:
        w(f"> ⚠️ {conv_data['error']}")
    else:
        w(f"![会话大小分布]({chart_files[2]})" if chart_files[2] else "")
        w()
        w("### 4.1 基础统计")
        w()
        w(f"| 指标 | 数值 |")
        w(f"|:-----|:----:|")
        w(f"| 总文件数 | {conv_data['total_files']} |")
        w(f"| 总行数 | {conv_data['total_lines']:,} |")
        w(f"| 总字符数 | {conv_data['total_chars']:,} |")
        w(f"| 总 Token (估) | ~{conv_data['total_tokens']:,} |")
        w(f"| 总磁盘 | {conv_data['total_size_kb']:.0f} KB |")
        w(f"| 活跃天数 | {conv_data['active_days_count']} 天 |")
        w(f"| 平均文件大小 | {conv_data['avg_chars']:,.0f} chars (~{conv_data['avg_tokens']:,} tokens) |")
        w(f"| 中位数文件大小 | {conv_data['median_chars']:,} chars (~{conv_data['median_tokens']:,} tokens) |")
        w()

        w("### 4.2 文件大小百分位分布")
        w()
        w("| 百分位 | 行数 | 字符数 | Token (估) |")
        w("|:------:|:----:|:-----:|:----------:|")
        for p, vals in conv_data["percentiles"].items():
            w(f"| {p} | {vals['lines']:,} | {vals['chars']:,} | ~{vals['tokens']:,} |")
        w()

        w("### 4.3 按分类统计")
        w()
        w("| 类别 | 文件数 | 平均 chars | 中位数 chars | 总 Token |")
        w("|:-----|:------:|:----------:|:------------:|:--------:|")
        for cat, stats in sorted(conv_data["category_stats"].items(),
                                  key=lambda x: -x[1]["count"]):
            w(f"| {cat} | {stats['count']} | {stats['avg_chars']:,.0f} | "
              f"{stats['median_chars']:,.0f} | ~{stats['total_tokens']:,} |")
        w()

        w("### 4.4 会话时间线")
        w()
        if chart_files[7]:
            w(f"![会话时间线]({chart_files[7]})")
        w()

        # 日均会话估算
        daily_avg_sessions = round(conv_data["total_files"] / max(conv_data["active_days_count"], 1), 1)
        w(f"> **关键洞察**: 日均约 **{daily_avg_sessions}** 个会话文件。"
          f"用户交互会话 (user-questions/) 中位数 ~{conv_data['category_stats'].get('user_questions', {}).get('median_chars', 0):,.0f} chars，"
          f"非常简短。定时任务会话 (db-sessions/) 中位数 "
          f"~{conv_data['category_stats'].get('db_sessions', {}).get('median_chars', 0):,.0f} chars，"
          f"是体积最大的类型。")
        w()

    # ========== 5. 定价与成本模型 ==========
    w("## 5. 💰 定价与成本模型 (DeepSeek v4 Flash)")
    w()
    w(f"> **官方定价** (2026-07-28): `https://api-docs.deepseek.com/zh-cn/quick_start/pricing`")
    w()
    w("| 计费项 | ¥/M tokens | 相对比例 |")
    w("|:-------|:----------:|:--------:|")
    w(f"| 输入缓存命中 | ¥{PRICING['input_cache_hit']} | 1x (基准) |")
    w(f"| 输入缓存未命中 | ¥{PRICING['input_cache_miss']} | **{PRICING['input_cache_miss']/PRICING['input_cache_hit']:.0f}x** |")
    w(f"| 输出 | ¥{PRICING['output']} | **{PRICING['output']/PRICING['input_cache_hit']:.0f}x** |")
    w()
    w("### 5.1 缓存效应深度分析")
    w()
    w(f"![缓存影响]({chart_files[5]})" if chart_files[5] else "")
    w()

    w(f"| 缓存场景 | 每会话成本 | 日成本 (20会话) | 月成本 (30天) |")
    w(f"|:---------|:----------:|:---------------:|:-------------:|")
    w(f"| 🟢 全缓存命中 | {_fmt_cost(cache_impact['hit_per_session'])} | "
      f"{_fmt_cost(cache_impact['hit_per_session'] * 20)} | "
      f"{_fmt_cost(cache_impact['hit_per_session'] * 20 * 30)} |")
    w(f"| 🟡 混合 (首轮未命中) | {_fmt_cost(cache_impact['mixed_per_session'])} | "
      f"{_fmt_cost(cache_impact['mixed_per_session'] * 20)} | "
      f"{_fmt_cost(cache_impact['mixed_per_session'] * 20 * 30)} |")
    w(f"| 🔴 全未命中 (无缓存) | {_fmt_cost(cache_impact['miss_per_session'])} | "
      f"{_fmt_cost(cache_impact['miss_per_session'] * 20)} | "
      f"{_fmt_cost(cache_impact['miss_per_session'] * 20 * 30)} |")
    w()

    w("### 5.2 修改频率对成本的影响")
    w()
    w(f"| 每日修改次数 | 日成本 (20会话) | 月成本 | vs 不修改 |")
    w(f"|:----------:|:---------------:|:------:|:---------:|")
    w(f"| 0 (稳定) | {_fmt_cost(cache_impact['daily_zero_mod'])} | "
      f"{_fmt_cost(cache_impact['daily_zero_mod'] * 30)} | 基准 |")
    w(f"| 1 次 | {_fmt_cost(cache_impact['daily_one_mod'])} | "
      f"{_fmt_cost(cache_impact['daily_one_mod'] * 30)} | +{_fmt_cost(cache_impact['daily_one_mod'] - cache_impact['daily_zero_mod'])}/天 |")
    w(f"| 3 次 | {_fmt_cost(cache_impact['daily_three_mod'])} | "
      f"{_fmt_cost(cache_impact['daily_three_mod'] * 30)} | +{_fmt_cost(cache_impact['daily_three_mod'] - cache_impact['daily_zero_mod'])}/天 |")
    w(f"| 5 次 | {_fmt_cost(cache_impact['daily_five_mod'])} | "
      f"{_fmt_cost(cache_impact['daily_five_mod'] * 30)} | +{_fmt_cost(cache_impact['daily_five_mod'] - cache_impact['daily_zero_mod'])}/天 |")
    w()

    # ========== 6. 优化场景对比 ==========
    w("## 6. 🎯 优化场景对比分析")
    w()
    w(f"![优化场景]({chart_files[3]})" if chart_files[3] else "")
    w(f"![会话数影响]({chart_files[4]})" if chart_files[4] else "")
    w()

    w("| 场景 | 系统 Prompt | Skills XML | 每会话(混合) | 日成本(20) | 月成本 | 节省 vs 基线 |")
    w("|:-----|:----------:|:----------:|:------------:|:----------:|:-----:|:----------:|")
    for key, sc in scenarios.items():
        monthly = sc["daily_20"] * 30
        vs_str = "-{}%".format(sc['vs_baseline_pct']) if sc['vs_baseline_pct'] > 0 else "基准"
        w(f"| {sc['name']} | {sc['sys_tokens']:,}T | {sc['skills_tokens']:,}T | "
          f"{_fmt_cost(sc['cost_per_session_mixed'])} | {_fmt_cost(sc['daily_20'])} | "
          f"{_fmt_cost(monthly)} | {vs_str} |")
    w()

    # 会话数缩减的量化
    daily_session_scenarios = {
        "5 会话 (极简)": 5,
        "10 会话 (轻量)": 10,
        "20 会话 (中等)": 20,
        "30 会话 (重度)": 30,
        "50 会话 (密集)": 50,
    }
    baseline_mixed = scenarios["baseline"]["cost_per_session_mixed"]
    w("**会话数缩减的独立影响** (基于当前现状):")
    w()
    w("| 场景 | 会话数/天 | 日成本 | 月成本 | vs 20会话 |")
    w("|:-----|:---------:|:------:|:------:|:---------:|")
    for sname, sessions in daily_session_scenarios.items():
        daily = baseline_mixed * sessions
        monthly = daily * 30
        vs_20_pct = round((1 - sessions / 20) * 100, 0) if sessions != 20 else 0
        w(f"| {sname} | {sessions} | {_fmt_cost(daily)} | {_fmt_cost(monthly)} | "
          f"{f'{int(abs(vs_20_pct))}%' if vs_20_pct else '基准'}{' ↓' if vs_20_pct > 0 else ''} |")
    w()

    # ========== 7. 推荐行动 ==========
    w("## 7. 📋 优先级推荐 (基于量化分析)")
    w()

    # 计算不同策略的节省
    savings = []
    # ① Description裁剪
    trim_save_tokens = sys_prompt["skills_xml_tokens"] - max(
        s["skills_tokens"] for s in scenarios.values() if s["name"] != "当前现状"
    )
    trim_save_cost = trim_save_tokens * PRICING["input_cache_hit"] / 1_000_000 * 20  # 日
    savings.append({
        "priority": "P0 🚨",
        "action": "确定 skills 配置后冻结 → 最大化缓存命中",
        "estimate": f"{_fmt_cost(cache_impact['daily_zero_mod'] - cache_impact['daily_one_mod'])}/天",
        "rationale": f"每天修改 1 次导致缓存失效 2 个会话，多付 "
                     f"{_fmt_cost(cache_impact['daily_one_mod'] - cache_impact['daily_zero_mod'])}/天（~¥{round((cache_impact['daily_one_mod'] - cache_impact['daily_zero_mod'])*30,2)}/月）",
    })

    # 计算描述裁剪节省
    over_300 = [(n, l) for n, l in skills_data["desc_lens_sorted"] if l > 300]
    trim_total = sum(int((l - 300) * TOKEN_FACTOR) for n, l in over_300)
    trim_cost_daily = trim_total * PRICING["input_cache_hit"] / 1_000_000 * 20
    savings.append({
        "priority": "P1 🟠",
        "action": f"批量裁剪 {len(over_300)} 个 description 到 ≤300 chars",
        "estimate": f"{_fmt_cost(trim_cost_daily)}/天 (缓存命中)",
        "rationale": f"节省 ~{trim_total:,} tokens/会话，约 ¥{round(trim_cost_daily*30, 2)}/月。一次性改完可避免缓存失效",
    })

    # 会话数缩减
    current_sessions = daily_avg_sessions if "daily_avg_sessions" in dir() else 10
    savings.append({
        "priority": "P1 🟠",
        "action": "减少会话数 (定时任务 batch 化/会话复用)",
        "estimate": f"每减 5 会话省 {_fmt_cost(baseline_mixed * 5)}/天",
        "rationale": f"每会话固定成本 {_fmt_cost(baseline_mixed)}，会话数直接等比放大总成本。"
                     f"当前历史日均约 {daily_avg_sessions if 'daily_avg_sessions' in dir() else '~10'} 会话",
    })

    savings.append({
        "priority": "P2 🟡",
        "action": "归档低频 skills (当前 93 → 保留 60 核心)",
        "estimate": f"{_fmt_cost(scenarios['baseline']['daily_20'] - scenarios['archive_60']['daily_20'])}/天",
        "rationale": f"保留 60 个核心 skills 节省 "
                     f"{scenarios['baseline']['sys_tokens'] - scenarios['archive_60']['sys_tokens']:,} tokens/会话",
    })

    w("| 优先级 | 行动 | 日节省估算 | 依据 |")
    w("|:------:|:-----|:----------:|:-----|")
    for s in sorted(savings, key=lambda x: {"P0 🚨": 0, "P1 🟠": 1, "P2 🟡": 2}[x["priority"]]):
        w(f"| {s['priority']} | {s['action']} | {s['estimate']} | {s['rationale']} |")
    w()

    # ========== 8. 原始数据 ==========
    w("## 8. 📎 附录：原始数据")
    w()
    w(f"| 字段 | 值 |")
    w(f"|:-----|:---|")
    w(f"| 报告生成时间 | {REPORT_TIMESTAMP} |")
    w(f"| 模型 | {MODEL} |")
    w(f"| 定价缓存命中 | ¥{PRICING['input_cache_hit']}/M tokens |")
    w(f"| 定价缓存未命中 | ¥{PRICING['input_cache_miss']}/M tokens |")
    w(f"| 定价输出 | ¥{PRICING['output']}/M tokens |")
    w(f"| Token 系数 | {TOKEN_FACTOR} tokens/char |")
    w(f"| 典型会话轮数 | {TYPICAL_SESSION['rounds_per_session']} |")
    w(f"| 每轮用户输入 | {TYPICAL_SESSION['user_input_per_round']:,} tokens |")
    w(f"| 每轮输出 | {TYPICAL_SESSION['output_per_round']:,} tokens |")
    w(f"| Skills 总数 | {skills_data['total_skills']} |")
    w(f"| Enabled | {skills_data['enabled_count']} |")
    w(f"| Disabled | {skills_data['disabled_count']} |")
    w(f"| 系统 Prompt Token | {sys_prompt['total_sys_prompt_tokens']:,} |")
    w(f"| Skills XML Token | {skills_data['rendered_xml_tokens']:,} |")
    w(f"| 历史会话文件数 | {conv_data.get('total_files', 'N/A')} |")
    w(f"| 历史会话总 Token | ~{conv_data.get('total_tokens', 0):,} |")
    if "error" not in conv_data:
        w(f"| 活跃天数 | {conv_data['active_days_count']} |")
        w(f"| 用户交互会话 | {conv_data['category_stats'].get('user_questions', {}).get('count', 0)} |")
        w(f"| 定时任务会话 | {conv_data['category_stats'].get('db_sessions', {}).get('count', 0)} |")

    # 图表清单
    w()
    w("### 生成图表")
    w()
    w("| # | 文件名 | 说明 |")
    w("|:-:|:-------|:-----|")
    chart_descs = [
        (0, "系统 Prompt 构成饼图"),
        (1, "Skills Description 长度分布 (Top 30)"),
        (2, "会话文件大小分布直方图"),
        (3, "优化场景成本对比"),
        (4, "会话数对日成本影响"),
        (5, "System Prompt 修改频率对缓存成本影响"),
        (6, "Skills 按功能类别分布"),
        (7, "每日会话 Token 时间线"),
    ]
    for idx, desc in chart_descs:
        if idx < len(chart_files) and chart_files[idx]:
            w(f"| {idx+1} | {chart_files[idx]} | {desc} |")
    w()

    w("---")
    w()
    w(f"> **脚本**: `spec/scripts/analyze_token_consumption.py` | "
      f"**下一轮**: 运行 `python3 spec/scripts/analyze_token_consumption.py` 更新此报告")

    return "\n".join(lines)


def write_report_to_file(report: str):
    """将报告写入 knowledge/weekly-reports/07_kb_stat/"""
    fname = f"{TIMESTAMP}-token-consumption-analysis.md"
    fpath = os.path.join(OUTPUT_DIR, fname)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(report)
    return fname, fpath


# ============================================================
# 真实消耗数据支持
# ============================================================

def load_consumption_data(filepath: str) -> dict:
    """加载 DeepSeek Platform 真实 API 消耗数据"""
    global CONSUMPTION, USE_REAL_DATA
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    CONSUMPTION = data
    USE_REAL_DATA = True

    # 推导关键指标
    days = data.get("period_days", 30)
    total_cost = data["total_cost"]
    total_req = data["total_requests"]
    total_tok = data["total_tokens"]

    data["daily_cost_avg"] = total_cost / days
    data["daily_requests_avg"] = total_req / days
    data["daily_tokens_avg"] = total_tok / days
    data["cost_per_request"] = total_cost / total_req
    data["tokens_per_request"] = total_tok / total_req
    data["blended_cost_per_m"] = total_cost / (total_tok / 1_000_000)

    # 估算缓存命中率 (基于总成本反推)
    # Cost = I_hit×0.02 + I_miss×1.00 + O×2.00 (per M)
    # I_hit + I_miss + O = total_tok
    # 设输出占比 r, 缓存命中率 h
    # total_M × [(1-r)(1-0.98h) + 2r] = total_cost
    total_M = total_tok / 1_000_000
    # 假设输出占比 ~2% (典型 AI 对话)
    r = 0.02
    rhs = total_cost / total_M - 2 * r
    h = (1 - rhs / (1 - r)) / 0.98

    data["estimated_output_ratio"] = r
    data["estimated_cache_hit_rate"] = max(0, min(1, h))
    data["estimated_input_hit_M"] = total_M * (1 - r) * h
    data["estimated_input_miss_M"] = total_M * (1 - r) * (1 - h)
    data["estimated_output_M"] = total_M * r

    # 按请求类型估算
    first_round_pct = 0.10
    follow_round_pct = 0.60
    tool_call_pct = 0.25
    retry_pct = 0.05

    sys_tokens = 50632
    user_per_round = total_tok / total_req - sys_tokens - 1500  # 估算
    out_per_round = 1500

    data["request_breakdown"] = {
        "会话首轮": {"pct": first_round_pct,
                     "requests": int(total_req * first_round_pct),
                     "cost_per": (sys_tokens * 0.02 + user_per_round * 1.00 + out_per_round * 2.00) / 1_000_000},
        "多轮后续": {"pct": follow_round_pct,
                     "requests": int(total_req * follow_round_pct),
                     "cost_per": (user_per_round * 1.00 + out_per_round * 2.00) / 1_000_000},
        "定时任务/工具调用": {"pct": tool_call_pct,
                             "requests": int(total_req * tool_call_pct),
                             "cost_per": (user_per_round * 1.00 + out_per_round * 2.50) / 1_000_000},
        "错误重试/空跑": {"pct": retry_pct,
                         "requests": int(total_req * retry_pct),
                         "cost_per": (sys_tokens * 1.00 + user_per_round * 1.00 + out_per_round * 2.00) / 1_000_000},
    }

    print(f"✅ 加载真实消耗数据: ¥{total_cost} / {total_req:,}请求 / {total_tok:,}tokens ({days}天)")
    return data


def chart_real_vs_model(conv_data: dict):
    """图9: 真实 API 消耗 vs 旧模型预测对比"""
    if not USE_REAL_DATA or "error" in conv_data:
        return None, None

    fig, ax, plt = _init_plot(12, 7)

    labels = ["月成本 (¥)", "日均请求数", "系统 prompt 成本占比 (%)"]
    if not CONSUMPTION:
        plt.close(fig)
        return None, None

    c = CONSUMPTION
    old_values = [45.0, 20, 64]  # v3.0 旧模型预测
    real_values = [c["total_cost"], c["daily_requests_avg"], 14]

    x = range(len(labels))
    width = 0.35

    bars1 = ax.bar([i - width / 2 for i in x], old_values, width,
                   label="旧模型 (v3.0)", color="#FF6B6B", edgecolor="white")
    bars2 = ax.bar([i + width / 2 for i in x], real_values, width,
                   label="真实数据 (v3.2)", color="#4ECDC4", edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_title(
        "真实 API 消耗 vs 旧模型预测对比\n"
        f"真实: ¥{c['total_cost']}/月, {c['daily_requests_avg']:.0f}请求/天 | "
        f"旧模型: ¥45/月, 20会话/天",
        fontsize=12, fontweight="bold"
    )
    ax.legend(fontsize=10)

    # 标注数值
    for bar, val in zip(bars1, old_values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                str(val), ha="center", fontsize=9, fontweight="bold")
    for bar, val in zip(bars2, real_values):
        txt = f"{val}" if val == int(val) else f"{val:.0f}"
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                txt, ha="center", fontsize=9, fontweight="bold", color="#2ECC71")

    # 差异标注
    for i, (old, real) in enumerate(zip(old_values, real_values)):
        diff_pct = (real - old) / old * 100
        color = "red" if abs(diff_pct) > 20 else "orange"
        ax.annotate(
            f"{'+' if diff_pct > 0 else ''}{diff_pct:.0f}%",
            (i, max(old, real) + 5),
            fontsize=10, fontweight="bold", color=color,
            ha="center",
        )

    return _save_chart(fig, plt, "09-real-vs-model")


def chart_cost_structure():
    """图10: 成本结构分解 (基于真实消耗数据)"""
    if not USE_REAL_DATA or not CONSUMPTION:
        return None, None

    fig, ax, plt = _init_plot(12, 7)

    c = CONSUMPTION
    # 成本结构: 来自分析
    total = c["total_cost"]
    output_cost = c["estimated_output_M"] * 2.00
    input_miss_cost = c["estimated_input_miss_M"] * 1.00
    input_hit_cost = c["estimated_input_hit_M"] * 0.02
    history_hit_cost = input_hit_cost * 0.48  # 历史缓存约占系统的一半
    sys_prompt_cost = input_hit_cost * 0.52  # 系统 prompt 缓存

    components = {
        "AI 输出 (¥2.00/M)": output_cost,
        "用户输入未命中 (¥1.00/M)": input_miss_cost,
        "系统 prompt 缓存命中 (¥0.02/M)": sys_prompt_cost,
        "历史对话缓存命中 (¥0.02/M)": history_hit_cost,
    }

    labels = list(components.keys())
    values = list(components.values())
    colors = ["#FF6B6B", "#E67E22", "#4ECDC4", "#96CEB4"]

    wedges, texts, autotexts = ax.pie(
        values, labels=None, autopct="%1.1f%%",
        colors=colors, startangle=90, pctdistance=0.75,
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
    )
    for t in autotexts:
        t.set_fontsize(9)

    legend_labels = [
        f"{l}  (¥{v:.0f}/月, {v/total*100:.1f}%)"
        for l, v in zip(labels, values)
    ]
    ax.legend(wedges, legend_labels, title="成本结构",
              loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9)
    ax.set_title(
        f"真实 API 成本结构分解\n"
        f"基线: ¥{total:.0f}/月 | 混合成本: ¥{c['blended_cost_per_m']:.4f}/M tokens",
        fontsize=13, fontweight="bold", pad=15
    )

    return _save_chart(fig, plt, "10-cost-structure")


# ============================================================
# 主入口
# ============================================================

def run_full_analysis(generate_charts=True):
    """执行完整分析"""
    ver = "v3.2 (真实消耗)" if USE_REAL_DATA else "v3.2"
    print(f"🔬 Token 消耗分析 {ver} — {REPORT_TIMESTAMP}")
    print(f"  模型: {MODEL} | 定价: 缓存¥{PRICING['input_cache_hit']}/¥{PRICING['input_cache_miss']}/M, 输出¥{PRICING['output']}/M")
    print(f"  工作空间: {WORKSPACE}")
    print()

    # 1) 分析 skills_config
    print("📦 分析 skills_config.json...", end=" ")
    skills = analyze_skills_config()
    print(f"完成 ({skills['enabled_count']} enabled, {skills['rendered_xml_tokens']:,} XML tokens)")

    # 2) 分析会话数据
    print("💬 分析 conversation-log/...", end=" ")
    conv = analyze_conversation_data()
    if "error" in conv:
        print(f"⚠️ {conv['error']}")
    else:
        print(f"完成 ({conv['total_files']} 文件, ~{conv['total_tokens']:,} tokens)")

    # 3) 系统 prompt 结构
    print("🧩 计算系统 prompt 结构...", end=" ")
    sys_prompt = calc_system_prompt_structure(skills)
    print(f"完成 (~{sys_prompt['total_sys_prompt_tokens']:,} tokens/会话)")

    # 4) 优化场景
    print("🎯 计算优化场景...", end=" ")
    scenarios = calc_cost_scenarios(skills, sys_prompt)
    print("完成")

    # 5) 缓存影响
    print("⚡ 分析缓存效应...", end=" ")
    cache_impact = calc_cache_impact(scenarios)
    print("完成")

    # 6) 生成图表
    chart_files = [None] * 10
    if generate_charts:
        print("📊 生成图表...")
        try:
            results = [
                chart_system_prompt_composition(sys_prompt),
                chart_description_distribution(skills),
                chart_conversation_size_distribution(conv),
                chart_optimization_scenarios(scenarios),
                chart_session_cost_impact(scenarios),
                chart_cache_impact_analysis(skills, sys_prompt),
                chart_category_distribution(skills),
                chart_conversation_timeline(conv),
                chart_real_vs_model(conv),
                chart_cost_structure(),
            ]
            for i, (fname, fpath) in enumerate(results):
                if fname:
                    chart_files[i] = fname
                    print(f"  ✅ {i+1}/10: {fname}")
                else:
                    print(f"  ⚠️ {i+1}/10: 跳过 (数据不足)")
        except Exception as e:
            print(f"  ❌ 图表生成出错: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("📊 图表: 跳过 (--no-charts)")

    # 7) 生成报告
    print("📝 生成报告...", end=" ")
    report = generate_report(skills, conv, sys_prompt, scenarios, cache_impact, chart_files)
    fname, fpath = write_report_to_file(report)
    print(f"完成")
    print()

    # 输出摘要
    print("=" * 60)
    print("✅ 分析完成")
    print(f"   报告: {os.path.relpath(fpath, WORKSPACE)}")
    if chart_files[0]:
        print(f"   图表: {OUTPUT_DIR}/")
        for cf in chart_files:
            if cf:
                print(f"         {cf}")
    print()
    print("📋 核心数字:")
    print(f"   系统 Prompt: ~{sys_prompt['total_sys_prompt_tokens']:,} tokens/会话")
    print(f"   Skills XML: ~{sys_prompt['skills_xml_tokens']:,} tokens ({sys_prompt['skills_xml_pct']}%)")
    print(f"   每会话成本 (混合): {_fmt_cost(scenarios['baseline']['cost_per_session_mixed'])}")
    print(f"   日成本 (20会话, 混合): {_fmt_cost(scenarios['baseline']['daily_20'])}")
    print(f"   缓存未命中惩罚: {cache_impact['miss_vs_hit_ratio']}x")
    print(f"   最大节省潜力: -{max(s['vs_baseline_pct'] for k,s in scenarios.items() if k != 'baseline')}%")
    print("=" * 60)

    return report


def run_daily():
    """每日简报模式"""
    skills = analyze_skills_config()
    sys_prompt = calc_system_prompt_structure(skills)
    scenarios = calc_cost_scenarios(skills, sys_prompt)

    print(f"📊 Token 每日简报 — {REPORT_TIMESTAMP}")
    print(f"  {'指标':<30} {'数值':<20}")
    print(f"  {'─'*50}")
    print(f"  {'系统 Prompt (总)':<30} {sys_prompt['total_sys_prompt_tokens']:>8,} tokens")
    print(f"  {'Skills XML':<30} {sys_prompt['skills_xml_tokens']:>8,} tokens ({sys_prompt['skills_xml_pct']}%)")
    print(f"  {'每会话成本 (混合)':<30} {_fmt_cost(scenarios['baseline']['cost_per_session_mixed']):>10}")
    for n in [5, 10, 20, 30]:
        print(f"  {'日成本 (' + str(n) + '会话, 混合)':<30} {_fmt_cost(scenarios['baseline']['daily_' + str(n)]):>10}")
    print(f"  {'最大节省潜力':<30} {'-' + str(max(s['vs_baseline_pct'] for k,s in scenarios.items() if k != 'baseline')) + '%':>10}")


if __name__ == "__main__":
    # 检查 --consumption 参数
    consumption_file = None
    filtered_argv = []
    i = 0
    while i < len(sys.argv):
        if sys.argv[i] == "--consumption" and i + 1 < len(sys.argv):
            consumption_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--consumption":
            # 下一个参数可能是 --daily 或不存在
            consumption_file = True  # 标记为需要默认路径
            i += 1
        else:
            filtered_argv.append(sys.argv[i])
            i += 1
    sys.argv = filtered_argv

    if consumption_file:
        if consumption_file is True:
            # 尝试默认路径
            default_path = os.path.join(WORKSPACE, "spec", "scripts", "deepseek_consumption.json")
            if os.path.exists(default_path):
                consumption_file = default_path
            else:
                print("⚠️ 未指定 consumption 文件，尝试默认路径失败。请提供文件路径")
                print("   用法: --consumption path/to/readings.json")
                sys.exit(1)
        load_consumption_data(consumption_file)

    if "--daily" in sys.argv:
        run_daily()
    elif "--no-charts" in sys.argv:
        run_full_analysis(generate_charts=False)
    else:
        run_full_analysis()
