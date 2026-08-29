#!/usr/bin/env python3
"""
unified-search.py — 统一搜索入口 CLI

基于 sr-006 A-01 / G-01 建议实现。统一管理搜索源、增量/去重/重试、
输出标准化。作为 agent 搜索的"策略层"辅助——不直接执行搜索，
而是生成搜索计划和标准化指令供 agent 执行。

核心功能:
  1. plan     — 为指定领域生成搜索计划（源+关键词+时间窗口）
  2. track    — 追踪各领域搜索历史和增量状态
  3. sources  — 列出可用搜索源及状态
  4. summary  — 汇总多个方向的搜索结果到统一报告

用法:
  # 生成搜索计划（单领域）
  python3 scripts/search/unified-search.py plan --domain supernode --hours 48

  # 生成搜索计划（多领域）
  python3 scripts/search/unified-search.py plan --dirs "supernode,cluster-training,llm-trends"

  # 查看搜索追踪状态
  python3 scripts/search/unified-search.py track --domain supernode

  # 列出可用搜索源
  python3 scripts/search/unified-search.py sources

  # 汇总搜索结果
  python3 scripts/search/unified-search.py summary --dirs "supernode,cluster-training" --since 2026-07-25

  # 清理过期的搜索追踪记录（>7天无更新）
  python3 scripts/search/unified-search.py track --prune 7

依赖:
  - knowledge/01_survey/*/ 下的 TRACKING.md 或搜索历史
  - scheduler/tasks.json 中的任务定义
"""
import sys
import os
import json
import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
KNOWLEDGE_DIR = REPO_ROOT / 'knowledge'
SURVEY_DIR = KNOWLEDGE_DIR / '01_survey'
TRACKING_FILE = SURVEY_DIR / '_search-track.json'

sys.path.insert(0, str(REPO_ROOT / 'scripts'))
from tools.errorcodes import EC, exit_with

from scripts.shared.workspace import WORKSPACE_ROOT, KNOWLEDGE_ROOT  # sr-008

NOW = datetime.now()
DATE_STR = NOW.strftime('%Y-%m-%d')

# ── 搜索源注册表 ──
SEARCH_SOURCES = {
    "arxiv": {
        "name": "arXiv",
        "url": "https://arxiv.org/search/?query={query}&searchtype=all",
        "type": "academic",
        "default": True,
        "rate_limit": "30次/分钟",
        "fallback": ["bing", "google"],
    },
    "bing": {
        "name": "Bing",
        "url": "https://www.bing.com/search?q={query}",
        "type": "general",
        "default": True,
        "rate_limit": "无明确限制",
        "fallback": ["google", "baidu"],
    },
    "google": {
        "name": "Google",
        "url": "https://www.google.com/search?q={query}",
        "type": "general",
        "default": False,
        "rate_limit": "需 API 或应对验证码",
        "fallback": ["bing"],
    },
    "baidu": {
        "name": "百度",
        "url": "https://www.baidu.com/s?wd={query}",
        "type": "general",
        "default": False,
        "rate_limit": "需 API Key",
        "fallback": ["bing"],
    },
    "weixin": {
        "name": "微信公众号",
        "url": "https://weixin.sogou.com/weixin?type=2&query={query}",
        "type": "social",
        "default": False,
        "rate_limit": "验证码频繁",
        "fallback": ["bing"],
    },
    "zhihu": {
        "name": "知乎",
        "url": "https://www.zhihu.com/search?type=content&q={query}",
        "type": "social",
        "default": False,
        "rate_limit": "正常",
        "fallback": ["bing"],
    },
}

# ── 领域预设 ──
DOMAIN_PRESETS = {
    "supernode": {
        "name": "超节点/AI服务器",
        "keywords": [
            "AI server supernode GPU cluster 2026",
            "NVIDIA DGX GB200 NVL72 rack-scale",
            "超节点 AI服务器 大规模训练集群",
        ],
        "sources": ["arxiv", "bing"],
        "output_dir": "01_survey/supernode/",
        "hours_window": 48,
    },
    "cluster-training": {
        "name": "集群训练",
        "keywords": [
            "distributed training 10K GPU fault tolerance",
            "NCCL RDMA AllReduce performance optimization",
            "万卡集群 分布式训练 故障恢复",
        ],
        "sources": ["arxiv", "bing"],
        "output_dir": "01_survey/cluster-training/",
        "hours_window": 48,
    },
    "llm-trends": {
        "name": "大模型动态",
        "keywords": [
            "large language model MoE 2026 new architecture",
            "GPT Llama 4 training efficiency scaling law",
            "大模型 MoE 推理优化 新架构",
        ],
        "sources": ["arxiv", "bing", "weixin"],
        "output_dir": "01_survey/llm-trends/",
        "hours_window": 24,
    },
    "interconnect": {
        "name": "互联与通信",
        "keywords": [
            "UALink CXL PCIe Gen6 NVLink interconnect",
            "optical interconnect co-packaged silicon photonics",
            "互联 UALink CXL 硅光 高速互连",
        ],
        "sources": ["arxiv", "bing"],
        "output_dir": "01_survey/interconnect/",
        "hours_window": 72,
    },
    "data-center": {
        "name": "数据中心",
        "keywords": [
            "data center 800G HVDC liquid cooling 2026",
            "AI data center power thermal management",
            "数据中心 液冷 HVDC 供电 散热 800G",
        ],
        "sources": ["bing", "arxiv"],
        "output_dir": "01_survey/data-center/",
        "hours_window": 72,
    },
    "storage-memory": {
        "name": "存储/内存/HBM",
        "keywords": [
            "HBM4 CXL memory fabric storage class memory",
            "NAND SSD CXL attached memory tier",
            "HBM CXL 存储级内存 SSD 国产存储",
        ],
        "sources": ["arxiv", "bing"],
        "output_dir": "01_survey/storage-memory/",
        "hours_window": 72,
    },
    "bmc-firmware": {
        "name": "BMC/固件",
        "keywords": [
            "BMC OpenBMC Redfish IPMI server management",
            "firmware security UEFI secure boot TPM",
            "BMC OpenBMC Redfish 固件安全",
        ],
        "sources": ["arxiv", "bing"],
        "output_dir": "01_survey/bmc-firmware/",
        "hours_window": 72,
    },
    "reliability": {
        "name": "可靠性与测试",
        "keywords": [
            "server RAS reliability availability serviceability",
            "fault tolerance predictive maintenance AIOps",
            "服务器可靠性 RAS 故障预测 AIOps",
        ],
        "sources": ["arxiv", "bing"],
        "output_dir": "01_survey/reliability/",
        "hours_window": 72,
    },
    "power-thermal": {
        "name": "供电/散热",
        "keywords": [
            "HVDC 800V liquid cooling immersion cooling power supply",
            "data center power efficiency PUE carbon neutral",
            "HVDC 液冷 浸没式 供电效率 PUE",
        ],
        "sources": ["bing", "arxiv"],
        "output_dir": "01_survey/power-thermal/",
        "hours_window": 72,
    },
    "chip-market": {
        "name": "芯片与市场格局",
        "keywords": [
            "GPU AI accelerator semiconductor 2026 market share",
            "NVIDIA AMD Intel AI chip roadmap competitive",
            "AI芯片 GPU 市场份额 半导体 竞争格局",
        ],
        "sources": ["bing", "arxiv", "weixin"],
        "output_dir": "01_survey/chip-market/",
        "hours_window": 48,
    },
}

# ── 搜索追踪 ──

def _load_track():
    """加载搜索追踪数据"""
    if not TRACKING_FILE.exists():
        return {"version": 1, "domains": {}}
    try:
        with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"version": 1, "domains": {}}


def _save_track(data):
    """保存搜索追踪"""
    SURVEY_DIR.mkdir(parents=True, exist_ok=True)
    with open(TRACKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _update_track(domain: str, results_count: int, sources_used: list, status: str):
    """更新领域搜索追踪"""
    data = _load_track()
    domains = data.setdefault("domains", {})
    d = domains.setdefault(domain, {
        "first_search": DATE_STR,
        "total_searches": 0,
        "total_results": 0,
        "last_search": None,
        "last_results": 0,
        "last_status": None,
        "sources_used": [],
    })
    d["total_searches"] = d.get("total_searches", 0) + 1
    d["total_results"] = d.get("total_results", 0) + results_count
    d["last_search"] = NOW.strftime('%Y-%m-%d %H:%M')
    d["last_results"] = results_count
    d["last_status"] = status
    d["sources_used"] = list(set(d.get("sources_used", []) + sources_used))
    _save_track(data)
    return d


# ══════════════════════════════════════════════════════════
#  搜索计划生成
# ══════════════════════════════════════════════════════════

def generate_plan(domain: str = "", dirs: str = "", hours: int = 48):
    """为指定领域生成搜索计划"""
    domains_to_plan = []

    if domain:
        if domain in DOMAIN_PRESETS:
            domains_to_plan = [domain]
        else:
            # 尝试匹配子目录
            candidates = [d for d in DOMAIN_PRESETS if domain in d]
            if candidates:
                domains_to_plan = candidates
            else:
                exit_with(EC.INVALID_ARGS,
                          f"未知领域: {domain}。可用: {', '.join(DOMAIN_PRESETS.keys())}")
    elif dirs:
        domains_to_plan = [d.strip() for d in dirs.split(",") if d.strip() in DOMAIN_PRESETS]
        if not domains_to_plan:
            exit_with(EC.INVALID_ARGS, f"未找到匹配的领域预设。可用: {', '.join(DOMAIN_PRESETS.keys())}")
    else:
        domains_to_plan = list(DOMAIN_PRESETS.keys())

    track = _load_track()

    print(f"\n📋 搜索计划 (生成于 {NOW.strftime('%Y-%m-%d %H:%M')})")
    print(f"{'='*60}")

    for dom in domains_to_plan:
        cfg = DOMAIN_PRESETS[dom]
        search_hours = hours if hours != 48 else cfg.get("hours_window", 48)

        # 检查追踪状态
        d_track = track.get("domains", {}).get(dom, {})
        last_search = d_track.get("last_search", "从未搜索")
        last_results = d_track.get("last_results", 0)
        total_results = d_track.get("total_results", 0)

        print(f"\n  🔍 [{dom}] {cfg['name']}")
        print(f"     窗口: 最近 {search_hours} 小时")
        print(f"     上次: {last_search} ({last_results} 条结果)")
        print(f"     累计: {total_results} 条")
        print(f"     源:   {', '.join(cfg['sources'])}")
        print(f"     关键词:")
        for i, kw in enumerate(cfg.get("keywords", []), 1):
            print(f"       {i}. {kw}")

        # 增量检测
        if d_track.get("last_search"):
            try:
                last_dt = datetime.strptime(d_track["last_search"], '%Y-%m-%d %H:%M')
                hours_since = (NOW - last_dt).total_seconds() / 3600
                if hours_since < search_hours * 0.5:
                    print(f"     ⏭️  距上次搜索仅 {hours_since:.0f}h，推荐跳过")
            except ValueError:
                pass

        print(f"     输出: knowledge/{cfg['output_dir']}{DATE_STR}.md")

    # 汇总
    print(f"\n{'─'*60}")
    print(f"📊 共 {len(domains_to_plan)} 个领域，建议并行搜索组:")
    # 按时间窗口分组
    by_window = {}
    for dom in domains_to_plan:
        w = DOMAIN_PRESETS[dom].get("hours_window", 48)
        by_window.setdefault(w, []).append(dom)
    for w, doms in sorted(by_window.items()):
        print(f"  ⏱️  {w}h 窗口: {', '.join(doms)}")


# ══════════════════════════════════════════════════════════
#  搜索追踪查看
# ══════════════════════════════════════════════════════════

def show_track(domain: str = "", prune_days: int = 0):
    """查看搜索追踪状态"""
    if prune_days:
        data = _load_track()
        domains = data.get("domains", {})
        before = len(domains)
        cutoff = (NOW - timedelta(days=prune_days)).strftime('%Y-%m-%d')
        to_delete = [d for d, info in domains.items()
                     if info.get("last_search", "").startswith(tuple([""]))
                     and info.get("last_search", "")[:10] < cutoff]
        for d in to_delete:
            del domains[d]
        _save_track(data)
        print(f"🗑️  清理前 {before} 个领域，清理后 {len(domains)} 个，删除 {before - len(domains)} 个过期记录")
        return

    data = _load_track()
    domains = data.get("domains", {})

    if domain:
        if domain not in domains:
            print(f"📭 领域 '{domain}' 无搜索记录")
            return
        d = domains[domain]
        print(f"\n📊 [{domain}] 搜索追踪")
        print(f"  首次搜索: {d.get('first_search', '?')}")
        print(f"  累计搜索: {d.get('total_searches', 0)} 次")
        print(f"  累计结果: {d.get('total_results', 0)} 条")
        print(f"  最近搜索: {d.get('last_search', '从未')}")
        print(f"  最近结果: {d.get('last_results', 0)} 条")
        print(f"  最近状态: {d.get('last_status', '?')}")
        print(f"  使用源:   {', '.join(d.get('sources_used', []))}")
        return

    # 全量展示
    print(f"\n📊 搜索追踪汇总 (共 {len(domains)} 个领域)")
    print(f"{'='*60}")
    print(f"{'领域':<20} {'累计搜索':<10} {'累计结果':<10} {'最近搜索':<16} {'状态':<8}")
    print(f"{'─'*60}")
    for dom in sorted(domains.keys()):
        d = domains[dom]
        name = DOMAIN_PRESETS.get(dom, {}).get("name", dom)
        total_s = d.get("total_searches", 0)
        total_r = d.get("total_results", 0)
        last = (d.get("last_search") or "?")[:16]
        status = d.get("last_status", "?")
        emoji = {"success": "✅", "empty": "⚠️", "fail": "❌"}.get(status, "❓")
        print(f"  {name:<18} {total_s:<10} {total_r:<10} {last:<16} {emoji}")


# ══════════════════════════════════════════════════════════
#  搜索源列表
# ══════════════════════════════════════════════════════════

def show_sources():
    """列出可用搜索源"""
    print(f"\n📡 可用搜索源 ({len(SEARCH_SOURCES)} 个)")
    print(f"{'='*60}")
    print(f"{'源':<12} {'类型':<12} {'默认':<8} {'频率限制':<20} {'回退':<20}")
    print(f"{'─'*60}")
    for key, src in SEARCH_SOURCES.items():
        default = "✅" if src.get("default") else ""
        fallback = ", ".join(src.get("fallback", []))[:20]
        print(f"  {key:<10} {src['type']:<12} {default:<8} {src['rate_limit']:<20} {fallback:<20}")
    print(f"\n💡 建议优先级: arXiv/Bing → Google/Baidu(备用) → 微信/知乎(深度)")


# ══════════════════════════════════════════════════════════
#  搜索结果汇总
# ══════════════════════════════════════════════════════════

def generate_summary(dirs: str = "", since: str = ""):
    """汇总多个方向的搜索结果"""
    domains = [d.strip() for d in dirs.split(",")] if dirs else list(DOMAIN_PRESETS.keys())
    since_date = since or (NOW - timedelta(days=7)).strftime('%Y-%m-%d')

    print(f"\n📊 搜索结果汇总 ({since_date} 至今)")
    print(f"{'='*60}")

    track = _load_track()
    total_domains = 0
    total_results = 0

    for dom in domains:
        if dom not in DOMAIN_PRESETS:
            continue
        cfg = DOMAIN_PRESETS[dom]
        d_track = track.get("domains", {}).get(dom, {})

        # 统计该领域在 since 后的产出文件
        output_dir = SURVEY_DIR / cfg["output_dir"] if cfg["output_dir"].startswith("01_survey/") \
            else SURVEY_DIR / cfg["output_dir"]

        recent_files = []
        if output_dir.exists():
            for f in sorted(output_dir.glob("????-??-??.md")):
                fdate = f.stem
                if fdate >= since_date and f.name not in ('index.md', 'log.md'):
                    recent_files.append(f)

        recent_results = d_track.get("total_results", 0)
        output_count = len(recent_files)

        if output_count > 0 or recent_results > 0:
            total_domains += 1
            total_results += recent_results
            status = d_track.get("last_status", "?")
            emoji = {"success": "✅", "empty": "⚠️", "fail": "❌"}.get(status, "❓")
            print(f"  {emoji} [{dom}] {cfg['name']}")
            print(f"     产出: {output_count} 个文件, ~{recent_results} 条结果")
        else:
            print(f"  ⚪ [{dom}] {cfg['name']} — 无产出")

    print(f"\n{'─'*60}")
    print(f"📈 共 {total_domains}/{len(domains)} 个领域有产出，约 {total_results} 条结果")


# ══════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='统一搜索入口 CLI — 生成搜索计划、追踪状态、汇总结果',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # plan
    p_plan = subparsers.add_parser("plan", help="生成搜索计划")
    p_plan.add_argument("--domain", default="", help="领域名（单个）")
    p_plan.add_argument("--dirs", default="", help="领域列表（逗号分隔）")
    p_plan.add_argument("--hours", type=int, default=48, help="搜索时间窗口（小时）")

    # track
    p_track = subparsers.add_parser("track", help="查看/管理搜索追踪")
    p_track.add_argument("--domain", default="", help="领域名（为空则显示全部）")
    p_track.add_argument("--prune", type=int, default=0, help="清理过期记录（天数）")

    # sources
    p_src = subparsers.add_parser("sources", help="列出可用搜索源")

    # summary
    p_sum = subparsers.add_parser("summary", help="汇总搜索结果")
    p_sum.add_argument("--dirs", default="", help="领域列表（逗号分隔，默认全部）")
    p_sum.add_argument("--since", default="", help="起始日期 (YYYY-MM-DD)，默认7天前")

    args = parser.parse_args()

    if args.command == "plan":
        generate_plan(domain=args.domain, dirs=args.dirs, hours=args.hours)
    elif args.command == "track":
        show_track(domain=args.domain, prune_days=args.prune)
    elif args.command == "sources":
        show_sources()
    elif args.command == "summary":
        generate_summary(dirs=args.dirs, since=args.since)
    else:
        parser.print_help()
        exit_with(EC.INVALID_ARGS, "请指定子命令")


if __name__ == "__main__":
    main()
