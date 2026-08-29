#!/usr/bin/env python3
"""
industry-research-tracker.py — 行业调研统一跟踪器 v2.1

三大改进 (v2.0):
  1. 分组支持 — 25 个独立任务合并为 3 组: 硬件组(hardware) / 技术组(tech) / 市场组(market)
  2. 数据源扩展 — 从 13 个 → 22 个，覆盖中英文、学术/产业/市场/政策
  3. 预搜索增强 — 组级批量计划 + 源可靠性 + 自愈 + 交叉验证

v2.1 新增 (备份源体系 + 健康监控):
  4. 备份源推荐引擎 — 按类型三层备份链 + 跨类型兜底 + 通用兜底
  5. 源健康仪表盘 — 实时监控所有源的健康状态 (健康/警告/降级/严重)
  6. 按专题备份建议 — 生成分组级别的源替代方案

用法:
  # 生成某组搜索计划 (AI agent 根据此计划执行 web_fetch)
  python3 scripts/industry-research-tracker.py plan --group hardware

  # 查看某组的所有专题
  python3 scripts/industry-research-tracker.py groups

  # 查看源整体健康度
  python3 scripts/industry-research-tracker.py registry --status

  # 查看降级源的备份推荐
  python3 scripts/industry-research-tracker.py registry --backup

依赖: web_fetch / bash wget/curl 等系统工具
临时文件: tmp/industry-tracker-<group>-<topic>-<date>.json
"""

import sys
import os
import json
import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

WORKSPACE = Path.home() / "cow"
TMP_DIR = WORKSPACE / "tmp"
REGISTRY_FILE = TMP_DIR / "source-registry.json"
KNOWLEDGE_DIR = WORKSPACE / "knowledge"
SURVEY_DIR = KNOWLEDGE_DIR / "01_survey"

NOW = datetime.now()
DATE_STR = NOW.strftime("%Y-%m-%d")
TIME_STR = NOW.strftime("%Y-%m-%d %H:%M")

os.makedirs(TMP_DIR, exist_ok=True)

# ══════════════════════════════════════════════
# 数据源注册表 (22 个, v2.0 扩展版)
# ══════════════════════════════════════════════
# 分级: A=稳定可用, B=有时可用, C=不稳定/付费, D=已知故障


# ══════════════════════════════════════════════
# 备份源体系 (v2.1 新增)
# ══════════════════════════════════════════════
# 按类型分类的备份映射表 — 当主源降级时，自动推荐同级/下级替代源
#
# 设计原则:
# - Tier 1 备份: 同类型的替代源（最相关）
# - Tier 2 备份: 跨类型的次级替代源（保证覆盖）
# - Tier 3 备份: 通用兜底源（所有专题最后一道防线）
#
BACKUP_SOURCES = {
    # ── 硬件类源的备份链 ──
    "hardware": {
        "tier1": ["servethehome", "tomshardware", "anandtech"],
        "tier2": ["semiengineering", "hpcwire", "theregister"],
    },
    # ── 行业/分析类源的备份链 ──
    "industry": {
        "tier1": ["semiengineering", "hpcwire", "datacenterdynamics"],
        "tier2": ["theregister", "techcrunch"],
    },
    "deep-analysis": {
        "tier1": ["the-next-platform", "semiengineering"],
        "tier2": ["servethehome", "hpcwire"],
    },
    # ── 官方源的备份链 ──
    "official": {
        "tier1": ["cncf-blog", "k8s-blog", "ocp-blog"],
        "tier2": ["techcrunch", "theregister"],
    },
    # ── 新闻类源的备份链 ──
    "news": {
        "tier1": ["reuters-tech", "techcrunch"],
        "tier2": ["theregister", "36kr"],
    },
    "tech-news": {
        "tier1": ["techcrunch", "theregister"],
        "tier2": ["reuters-tech"],
    },
    # ── 学术类源的备份链 ──
    "academic": {
        "tier1": ["arxiv", "ieee-spectrum"],
        "tier2": ["semiengineering"],
    },
    "reference": {
        "tier1": ["wikichip", "arxiv"],
        "tier2": ["servethehome"],
    },
    # ── 市场/商业类源的备份链 ──
    "market": {
        "tier1": ["trendforce-news", "reuters-tech"],
        "tier2": ["jiweinet", "36kr"],
    },
    "chinese-industry": {
        "tier1": ["jiweinet", "laoyaoba"],
        "tier2": ["36kr", "reuters-tech"],
    },
    "chinese-business": {
        "tier1": ["36kr", "jiweinet"],
        "tier2": ["techcrunch", "reuters-tech"],
    },
    # ── 开源类的备份链 ──
    "open-source": {
        "tier1": ["github-trending", "techcrunch"],
        "tier2": ["theregister"],
    },
    # ── 通用兜底 (所有类型最后防线) ──
    "universal_fallback": {
        "tier3": [
            "techcrunch",      # 通用科技新闻，覆盖面广
            "theregister",     # IT企业级新闻，覆盖面广
        ],
    },
}

# 跨类型备份映射 — 用于当某类型完全失效时的跨域替代
CROSS_TYPE_BACKUP = {
    "hardware": {         # 硬件源全灭 → 用行业分析源
        "tier1": ["semiengineering", "hpcwire"],
        "tier2": ["theregister", "techcrunch"],
        "tier3": ["arxiv"],
    },
    "industry": {         # 行业源全灭 → 用新闻源
        "tier1": ["reuters-tech", "techcrunch"],
        "tier2": ["theregister"],
        "tier3": ["arxiv"],
    },
    "market": {           # 市场源全灭 → 用新闻源+中文产业
        "tier1": ["reuters-tech", "jiweinet"],
        "tier2": ["techcrunch", "36kr"],
        "tier3": ["arxiv"],
    },
    "academic": {         # 学术源全灭 → 用行业深度分析
        "tier1": ["semiengineering", "the-next-platform"],
        "tier2": ["servethehome"],
        "tier3": [],
    },
    "chinese-industry": { # 中文产业源全灭 → 用英文市场源+科技新闻
        "tier1": ["trendforce-news", "reuters-tech"],
        "tier2": ["techcrunch"],
        "tier3": [],
    },
}

# 通用兜底源（所有专题的最后防线，不依赖类型映射）
UNIVERSAL_FALLBACK_SOURCES = ["arxiv", "techcrunch", "theregister"]

# 自动备份推荐的阈值
BACKUP_RECOMMEND_THRESHOLD = 2   # 连续2次失败即开始推荐备份
CRITICAL_DEGRADE_THRESHOLD = 4   # 连续4次失败标记为严重降级
STABLE_SOURCES = {
    # ── Tier 1: 学术前沿 ──
    "arxiv": {
        "name": "arXiv.org",
        "type": "academic",
        "grade": "A",
        "fetch_method": "web_fetch",
        "keywords_transform": lambda kw: kw.replace(" ", "+"),
        "url_template": "https://arxiv.org/search/?query={query}&searchtype=all&start=0",
        "notes": "学术前沿，稳定可用，适合所有技术专题",
    },

    # ── Tier 1: 官方/一手 ──
    "cncf-blog": {
        "name": "CNCF Blog",
        "type": "industry",
        "grade": "A",
        "fetch_method": "web_fetch",
        "url": "https://www.cncf.io/blog/",
        "notes": "云原生一手信息，适合K8s/Agent/平台工程",
    },
    "k8s-blog": {
        "name": "Kubernetes Blog",
        "type": "official",
        "grade": "A",
        "fetch_method": "web_fetch",
        "url": "https://kubernetes.io/blog/",
        "notes": "K8s官方发布，AI特性密集",
    },
    "ocp-blog": {
        "name": "OCP Blog",
        "type": "official",
        "grade": "A",
        "fetch_method": "web_fetch",
        "url": "https://www.opencompute.org/blog",
        "notes": "开放计算标准，服务器/数据中心/液冷标准新发布",
    },

    # ── Tier 1: 产业/市场数据 ──
    "trendforce-news": {
        "name": "TrendForce News",
        "type": "market",
        "grade": "A",
        "fetch_method": "web_fetch",
        "url": "https://www.trendforce.com/news/",
        "notes": "半导体/DRAM/存储/芯片市场数据，中文可用",
    },
    "reuters-tech": {
        "name": "Reuters Technology",
        "type": "news",
        "grade": "A",
        "fetch_method": "web_fetch",
        "url_template": "https://www.reuters.com/technology/",
        "notes": "半导体/AI/芯片行业新闻",
    },

    # ── Tier 1: 技术深度 ──
    "servethehome": {
        "name": "ServeTheHome",
        "type": "hardware",
        "grade": "A",
        "fetch_method": "web_fetch",
        "url_template": "https://www.servethehome.com/?s={query}",
        "notes": "服务器硬件一手评测，电源/散热/架构实测",
    },
    "wikichip": {
        "name": "WikiChip",
        "type": "reference",
        "grade": "A",
        "fetch_method": "web_fetch",
        "url": "https://en.wikichip.org/wiki/WikiChip",
        "notes": "芯片微架构参考，非新闻源但可查最新路线图",
    },
    "techcrunch": {
        "name": "TechCrunch",
        "type": "tech-news",
        "grade": "A",
        "fetch_method": "web_fetch",
        "url_template": "https://techcrunch.com/search/{query}",
        "notes": "AI编程工具/创业/AI Agent/开源动态",
    },

    # ── Tier 2: 行业深度分析 ──
    "the-next-platform": {
        "name": "The Next Platform",
        "type": "deep-analysis",
        "grade": "B",
        "fetch_method": "web_fetch",
        "url_template": "https://www.nextplatform.com/?s={query}",
        "notes": "服务器/AI芯片深度分析，但更新频率低",
    },
    "semiengineering": {
        "name": "SemiEngineering",
        "type": "industry",
        "grade": "B",
        "fetch_method": "web_fetch",
        "url_template": "https://semiengineering.com/?s={query}",
        "notes": "半导体/封装/EDA深度分析",
    },
    "anandtech": {
        "name": "AnandTech",
        "type": "hardware",
        "grade": "B",
        "fetch_method": "web_fetch",
        "url_template": "https://www.anandtech.com/tag/{query}",
        "notes": "硬件评测深度分析，更新量减少但仍可用",
    },
    "ieee-spectrum": {
        "name": "IEEE Spectrum",
        "type": "academic",
        "grade": "B",
        "fetch_method": "web_fetch",
        "url_template": "https://spectrum.ieee.org/search?q={query}",
        "notes": "人工智能/芯片架构深度文章，部分付费",
    },
    "datacenterdynamics": {
        "name": "Data Center Dynamics",
        "type": "industry",
        "grade": "B",
        "fetch_method": "web_fetch",
        "url": "https://www.datacenterdynamics.com/en/",
        "notes": "数据中心建设/液冷/供电/运维一手新闻",
    },
    "hpcwire": {
        "name": "HPCwire",
        "type": "industry",
        "grade": "B",
        "fetch_method": "web_fetch",
        "url_template": "https://www.hpcwire.com/?s={query}",
        "notes": "高性能计算/AI集群/互联技术",
    },
    "theregister": {
        "name": "The Register",
        "type": "tech-news",
        "grade": "B",
        "fetch_method": "web_fetch",
        "url_template": "https://www.theregister.com/search/?q={query}",
        "notes": "IT企业级新闻，服务器/芯片/开源",
    },
    "github-trending": {
        "name": "GitHub Trending",
        "type": "open-source",
        "grade": "B",
        "fetch_method": "web_fetch",
        "url": "https://github.com/trending",
        "notes": "开源项目趋势，适合AI框架/工具追踪",
    },

    # ── Tier 2: 中文产业源 (新增) ──
    "jiweinet": {
        "name": "集微网",
        "type": "chinese-industry",
        "grade": "B",
        "fetch_method": "web_fetch",
        "url": "https://www.jiwei.com/",
        "notes": "中国半导体/芯片产业新闻，国产化/政策追踪",
    },
    "laoyaoba": {
        "name": "老Yaob",
        "type": "chinese-industry",
        "grade": "B",
        "fetch_method": "web_fetch",
        "url_template": "https://www.laoyaoba.com/search?q={query}",
        "notes": "半导体/消费电子中文产业新闻",
    },
    "36kr": {
        "name": "36氪",
        "type": "chinese-business",
        "grade": "B",
        "fetch_method": "web_fetch",
        "url": "https://36kr.com/",
        "notes": "科技商业新闻，AI创业/融资/政策",
    },

    # ── Tier 2: 特定领域焦点 ──
    "tomshardware": {
        "name": "Tom's Hardware",
        "type": "hardware",
        "grade": "B",
        "fetch_method": "web_fetch",
        "url_template": "https://www.tomshardware.com/search?searchTerm={query}",
        "notes": "消费级/服务器硬件评测，GPU/CPU/SSD",
    },
    "nextplatform-ai": {
        "name": "The Next Platform (AI专题)",
        "type": "deep-analysis",
        "grade": "B",
        "fetch_method": "web_fetch",
        "url": "https://www.nextplatform.com/category/artificial-intelligence/",
        "notes": "AI基础设施/训练推理集群深度分析",
    },
}

# ══════════════════════════════════════════════
# 分组定义 — 3 组 × 25 专题
# ══════════════════════════════════════════════
# 硬件组 (01:10): 电源·形态·GPU·互联·液冷·BOM
# 技术组 (02:10): MoE硬件·云原生AI·AI工具·超节点·AI落地·OS·AI框架·集群·BMC·存储
# 市场组 (03:10): 芯片市场·国产化·智算方案·数据中心·产品·大模型·工具追踪·研发管理·项目管理·可靠性
GROUPS = {
    "hardware": {
        "name": "硬件组",
        "time": "01:10",
        "topics": [
            "power-architecture",
            "server-form-factor",
            "gpu-ai-chips",
            "interconnect",
            "liquid-cooling",
            "bom-supply-chain",
        ],
    },
    "tech": {
        "name": "技术组",
        "time": "02:10",
        "topics": [
            "moe-hardware",
            "cloud-native-ai",
            "ai-rd-tools",
            "supernode",
            "ai-infra-case",
            "distributed-os",
            "ai-framework",
            "cluster-training",
            "bmc-system",
            "storage-memory",
        ],
    },
    "market": {
        "name": "市场组",
        "time": "03:10",
        "topics": [
            "chip-market",
            "domestic-substitution",
            "intelligent-computing",
            "datacenter-infra",
            "product-mgmt",
            "llm-dynamics",
            "tools-tracking",
            "rd-mgmt",
            "project-mgmt",
            "reliability-test",
        ],
    },
}

# ══════════════════════════════════════════════
# 专题定义 (14+ 个已有 + 新增)
# ══════════════════════════════════════════════
TOPICS = {
    # ── 硬件组 6 个 ──
    "power-architecture": {
        "name": "电源架构",
        "output_dir": "01_survey/industry-research/",
        "frequency": "双周",
        "keywords": [
            "800V HVDC data center power supply GaN SiC 2026",
            "server power architecture BBU HVDC PSU efficiency",
            "NVIDIA 800V HVDC power shelf rack-scale power",
            "power shelf server PSU 10kW+ 2026",
            "HVDC 400V 800V data center deployment 2026 new",
        ],
        "fallback_keywords": [
            "data center power distribution 2026 new technology",
            "server power supply 2026 latest",
            "HVDC 800V 2026 data center deployment",
        ],
        "discovery_keywords": [
            "power supply unit server 10kW 2026",
            "GaN SiC power converter 2026 server",
            "data center power architecture 2025 2026",
        ],
        "primary_sources": [
            "servethehome", "semiengineering", "trendforce-news", "datacenterdynamics",
        ],
        "secondary_sources": [
            "ieee-spectrum", "the-next-platform", "techcrunch",
        ],
        "discovery_sources": ["arxiv"],
        "cn_keywords": ["服务器电源 800V HVDC 2026 最新", "数据中心电源架构 GaN SiC"],
    },
    "server-form-factor": {
        "name": "服务器形态",
        "output_dir": "01_survey/industry-research/",
        "frequency": "每月",
        "keywords": [
            "AI server form factor OAM OCP 2026",
            "GPU server chassis liquid cooling rack design 2026",
            "NVIDIA DGX GB300 rack-scale architecture",
            "server form factor open standard OAM 2026",
            "OCP server 2026 new form factor standard",
        ],
        "fallback_keywords": [
            "GPU server 2026 new product",
            "AI server chassis 2026",
            "server rack design 2026 liquid cooling",
        ],
        "discovery_keywords": [
            "AI server 2026 form factor design",
            "GPU server OEM 2026 new",
        ],
        "primary_sources": [
            "servethehome", "semiengineering", "ocp-blog", "tomshardware",
        ],
        "secondary_sources": [
            "anandtech", "the-next-platform", "theregister",
        ],
        "discovery_sources": ["arxiv"],
        "cn_keywords": ["AI服务器 形态 OAM OCP 2026", "GPU服务器 机箱 液冷 设计"],
    },
    "gpu-ai-chips": {
        "name": "GPU与AI芯片",
        "output_dir": "01_survey/industry-research/",
        "frequency": "每周",
        "keywords": [
            "GPU AI accelerator 2026 new architecture",
            "NVIDIA AMD Intel AI chip 2026 roadmap",
            "AI ASML TSMC chiplet packaging HBM 2026",
            "NVIDIA Vera Rubin 2026 GPU architecture",
            "AI chiplet chiplet interconnect UCIe 2026",
        ],
        "fallback_keywords": [
            "AI semiconductor GPU 2026",
            "AI chip 2026 new product announcement",
        ],
        "discovery_keywords": [
            "AI accelerator 2026 latest",
            "GPU architecture 2026 paper",
        ],
        "primary_sources": [
            "wikichip", "servethehome", "semiengineering",
            "trendforce-news", "reuters-tech", "tomshardware",
        ],
        "secondary_sources": [
            "anandtech", "ieee-spectrum", "the-next-platform",
        ],
        "discovery_sources": ["arxiv"],
        "cn_keywords": ["GPU AI芯片 2026 最新架构", "NVIDIA AMD 国产AI芯片 2026 路线图"],
    },
    "interconnect": {
        "name": "互联与光通信",
        "output_dir": "01_survey/industry-research/",
        "frequency": "每周",
        "keywords": [
            "UALink CXL PCIe Gen6 NVLink interconnect 2026",
            "optical interconnect CPO silicon photonics co-packaged 2026",
            "interconnect AI cluster networking 800G 1.6T 2026",
            "NVLink 6 UALink 1.0 2026 progress",
            "CXL 3.2 memory pooling 2026",
        ],
        "fallback_keywords": [
            "AI cluster interconnect 2026 new",
            "optical interconnect 2026 CPO SiPh",
            "CXL 2026 new memory pooling",
        ],
        "discovery_keywords": [
            "high speed interconnect 2026 paper",
            "optical interconnect 2026 datacenter",
        ],
        "primary_sources": [
            "arxiv", "servethehome", "semiengineering", "hpcwire",
        ],
        "secondary_sources": [
            "the-next-platform", "ieee-spectrum", "theregister",
        ],
        "discovery_sources": ["arxiv"],
        "cn_keywords": ["UALink CXL PCIe Gen6 互联 2026", "光互联 CPO 硅光 2026"],
    },
    "liquid-cooling": {
        "name": "液冷散热",
        "output_dir": "01_survey/industry-research/",
        "frequency": "每周",
        "keywords": [
            "liquid cooling data center 2026 immersion direct-to-chip",
            "GPU liquid cooling cold plate 2026 server",
            "coolant distribution unit CDU 2026 data center",
            "single-phase two-phase liquid cooling 2026 comparison",
            "immersion cooling 2026 data center deployment",
        ],
        "fallback_keywords": [
            "data center cooling 2026 new technology",
            "AI server cooling 2026",
        ],
        "discovery_keywords": [
            "liquid cooling 2026 datacenter GPU",
            "data center thermal 2026 new",
        ],
        "primary_sources": [
            "servethehome", "semiengineering", "datacenterdynamics",
        ],
        "secondary_sources": [
            "the-next-platform", "anandtech", "hpcwire",
        ],
        "discovery_sources": ["arxiv"],
        "cn_keywords": ["液冷 数据中心 2026 浸没式 冷板", "GPU液冷 散热 CDU 2026"],
    },
    "bom-supply-chain": {
        "name": "BOM供应链",
        "output_dir": "01_survey/industry-research/",
        "frequency": "双周",
        "keywords": [
            "DXI DRAM price 2026 server supply chain",
            "ABF substrate server BOM cost 2026",
            "semiconductor supply chain 2026 shortage capacity",
            "NAND DRAM price trend 2026 Q3 Q4",
            "server component shortage 2026 lead time",
        ],
        "fallback_keywords": [
            "DRAM price 2026 latest",
            "server supply chain 2026",
        ],
        "discovery_keywords": [],
        "primary_sources": [
            "trendforce-news", "reuters-tech", "jiweinet",
        ],
        "secondary_sources": ["tomshardware"],
        "discovery_sources": [],
        "cn_keywords": ["DXI指数 DRAM 价格 2026", "服务器供应链 BOM成本 2026"],
    },

    # ── 技术组 10 个 ──
    "moe-hardware": {
        "name": "MoE→硬件影响",
        "output_dir": "01_survey/industry-research/",
        "frequency": "双周",
        "keywords": [
            "mixture of experts hardware impact 2026",
            "MoE inference serving GPU memory 2026",
            "sparse MoE LLM routing 2026 architecture",
            "expert parallelism MoE training communication 2026",
        ],
        "fallback_keywords": [
            "MoE LLM 2026 new paper",
            "expert parallelism 2026 optimization",
        ],
        "discovery_keywords": [
            "MoE mixture of experts 2026 arXiv",
        ],
        "primary_sources": ["arxiv"],
        "secondary_sources": ["semiengineering", "techcrunch", "hpcwire"],
        "discovery_sources": ["arxiv"],
    },
    "cloud-native-ai": {
        "name": "云原生AI基础设施",
        "output_dir": "01_survey/industry-research/",
        "frequency": "每周",
        "keywords": [
            "Kubernetes AI GPU DRA 2026",
            "K8s AI inference serving agent infrastructure 2026",
            "CNCF AI workload Kubeflow KServe 2026",
            "Kubernetes GPU scheduling binpack 2026",
        ],
        "fallback_keywords": [
            "Kubernetes AI 2026 latest",
            "CNCF AI 2026 news",
        ],
        "discovery_keywords": [
            "K8s AI infrastructure 2026",
            "cloud native AI 2026",
        ],
        "primary_sources": [
            "cncf-blog", "k8s-blog", "techcrunch",
        ],
        "secondary_sources": ["arxiv", "theregister"],
        "discovery_sources": ["arxiv", "github-trending"],
    },
    "ai-rd-tools": {
        "name": "AI研发工具",
        "output_dir": "01_survey/industry-research/",
        "frequency": "双周",
        "keywords": [
            "AI coding assistant 2026 latest",
            "AI developer tools 2026 new",
            "AI software engineering 2026 agent",
            "AI code generation 2026 productivity benchmark",
        ],
        "fallback_keywords": [
            "AI developer tools 2026 announcement",
            "AI coding 2026 new product",
        ],
        "discovery_keywords": [
            "AI programming tools 2026",
        ],
        "primary_sources": [
            "techcrunch", "github-trending", "theregister",
        ],
        "secondary_sources": ["arxiv"],
        "discovery_sources": ["arxiv"],
    },
    "supernode": {
        "name": "超节点标准",
        "output_dir": "01_survey/industry-research/",
        "frequency": "每月",
        "keywords": [
            "supernode OAM OCP GPU baseboard 2026",
            "rack-scale AI server open standard 2026",
            "AI supernode NVIDIA DGX 2026",
            "OCP AI OAM baseboard 2026 specification",
        ],
        "fallback_keywords": [
            "AI supernode 2026 standard",
            "GPU baseboard 2026 OAM OCP",
        ],
        "discovery_keywords": [
            "supernode GPU rack 2026",
        ],
        "primary_sources": [
            "servethehome", "ocp-blog",
        ],
        "secondary_sources": ["semiengineering"],
        "discovery_sources": ["arxiv"],
    },
    "ai-infra-case": {
        "name": "AI基础设施落地",
        "output_dir": "01_survey/industry-research/",
        "frequency": "每月",
        "keywords": [
            "AI infrastructure deployment 2026 case study",
            "GPU cluster production 2026 experience",
            "AI training inference production 2026 best practice",
            "large scale AI training cluster 2026 operation",
        ],
        "fallback_keywords": [
            "AI infrastructure 2026 production",
            "GPU cluster 2026 deployment",
        ],
        "discovery_keywords": [
            "AI infrastructure 2026 deployment case",
        ],
        "primary_sources": [
            "cncf-blog", "techcrunch", "hpcwire",
        ],
        "secondary_sources": [
            "the-next-platform", "servethehome",
        ],
        "discovery_sources": ["arxiv"],
    },
    "distributed-os": {
        "name": "分布式OS",
        "output_dir": "01_survey/industry-research/",
        "frequency": "每月",
        "keywords": [
            "distributed operating system AI cluster 2026",
            "AI datacenter OS orchestration 2026",
            "cluster management OS AI workload 2026",
        ],
        "fallback_keywords": [
            "distributed OS 2026 new",
            "AI cluster OS 2026",
        ],
        "discovery_keywords": ["distributed system AI 2026"],
        "primary_sources": ["arxiv", "techcrunch"],
        "secondary_sources": ["theregister"],
        "discovery_sources": ["arxiv"],
    },
    "ai-framework": {
        "name": "AI框架追踪",
        "output_dir": "01_survey/industry-research/",
        "frequency": "双周",
        "keywords": [
            "PyTorch TensorFlow JAX 2026 new feature",
            "AI framework distributed training 2026",
            "ML framework compiler 2026 optimization",
        ],
        "fallback_keywords": [
            "AI framework 2026 new release",
            "deep learning framework 2026",
        ],
        "discovery_keywords": ["AI framework 2026 arXiv"],
        "primary_sources": ["arxiv", "github-trending", "techcrunch"],
        "secondary_sources": [],
        "discovery_sources": ["arxiv", "github-trending"],
    },
    "cluster-training": {
        "name": "集群训练优化",
        "output_dir": "01_survey/industry-research/",
        "frequency": "双周",
        "keywords": [
            "distributed training optimization 2026",
            "GPU cluster training efficiency 2026",
            "large model training parallelism 2026",
            "training fault tolerance 2026 checkpoint",
        ],
        "fallback_keywords": [
            "distributed training 2026 new",
            "GPU training 2026 optimization",
        ],
        "discovery_keywords": [
            "distributed training 2026 system",
        ],
        "primary_sources": ["arxiv", "hpcwire"],
        "secondary_sources": ["techcrunch"],
        "discovery_sources": ["arxiv"],
    },
    "bmc-system": {
        "name": "BMC系统",
        "output_dir": "01_survey/industry-research/",
        "frequency": "每月",
        "keywords": [
            "BMC firmware server management 2026",
            "OpenBMC 2026 new features",
            "server management IPMI Redfish 2026",
        ],
        "fallback_keywords": [
            "BMC 2026 new",
            "server management 2026",
        ],
        "discovery_keywords": ["BMC server 2026 management"],
        "primary_sources": ["servethehome"],
        "secondary_sources": ["theregister"],
        "discovery_sources": ["arxiv"],
    },
    "storage-memory": {
        "name": "存储与内存",
        "output_dir": "01_survey/industry-research/",
        "frequency": "双周",
        "keywords": [
            "CXL memory 2026 new product",
            "NVMe SSD 2026 server storage",
            "HBM4 memory 2026 GPU memory",
            "Storage class memory 2026",
        ],
        "fallback_keywords": [
            "server storage 2026 new",
            "memory 2026 CXL HBM",
        ],
        "discovery_keywords": ["memory storage 2026 server"],
        "primary_sources": [
            "trendforce-news", "servethehome", "tomshardware",
        ],
        "secondary_sources": ["anandtech", "theregister"],
        "discovery_sources": ["arxiv"],
    },

    # ── 市场组 10 个 ──
    "chip-market": {
        "name": "芯片市场格局",
        "output_dir": "01_survey/industry-research/",
        "frequency": "每周",
        "keywords": [
            "semiconductor market 2026 TSMC NVIDIA revenue",
            "AI chip market share 2026 competitive landscape",
            "HBM4 memory market SK Hynix Samsung 2026",
            "semiconductor equipment 2026 ASML applied materials",
            "foundry market 2026 TSMC Samsung Intel",
        ],
        "fallback_keywords": [
            "semiconductor industry 2026 Q2 earnings",
            "AI semiconductor market 2026",
        ],
        "discovery_keywords": [
            "semiconductor 2026 revenue market",
            "chip industry 2026 forecast",
        ],
        "primary_sources": [
            "trendforce-news", "reuters-tech", "semiengineering", "jiweinet",
        ],
        "secondary_sources": [
            "techcrunch", "the-next-platform", "36kr",
        ],
        "discovery_sources": [],
        "cn_keywords": ["半导体市场 2026 营收 市场份额", "AI芯片 竞争格局 2026"],
    },
    "domestic-substitution": {
        "name": "国产化替代",
        "output_dir": "01_survey/industry-research/",
        "frequency": "双周",
        "keywords": [
            "China semiconductor domestic substitution 2026",
            "Chinese AI chip 2026 local GPU",
            "China fab equipment 2026 import substitution",
        ],
        "fallback_keywords": [
            "中国半导体 2026 最新进展",
            "China chip 2026 latest",
        ],
        "discovery_keywords": [],
        "primary_sources": [
            "trendforce-news", "reuters-tech", "jiweinet", "36kr",
        ],
        "secondary_sources": ["laoyaoba"],
        "discovery_sources": [],
        "cn_keywords": [
            "国产芯片 国产化替代 2026 最新",
            "中国半导体 AI芯片 自主可控 2026",
            "长鑫 长江存储 国产GPU 2026 进展",
            "华为昇腾 寒武纪 海光 2026",
        ],
    },
    "intelligent-computing": {
        "name": "智算方案",
        "output_dir": "01_survey/industry-research/",
        "frequency": "双周",
        "keywords": [
            "intelligent computing center 2026 China construction",
            "AI computing power 2026 China government project",
            "smart computing 2026 infrastructure",
        ],
        "fallback_keywords": [
            "智算中心 2026 建设",
            "AI computing 2026 China",
        ],
        "discovery_keywords": [],
        "primary_sources": [
            "jiweinet", "36kr", "trendforce-news",
        ],
        "secondary_sources": ["reuters-tech"],
        "discovery_sources": [],
        "cn_keywords": [
            "智算中心 2026 建设 招标",
            "AI算力 基础设施 2026 中国",
        ],
    },
    "datacenter-infra": {
        "name": "数据中心基础设施",
        "output_dir": "01_survey/industry-research/",
        "frequency": "双周",
        "keywords": [
            "data center construction 2026 capacity growth",
            "hyperscaler data center 2026 capex",
            "data center power capacity 2026 shortage",
        ],
        "fallback_keywords": [
            "data center 2026 new construction",
            "hyperscaler 2026 expansion",
        ],
        "discovery_keywords": [],
        "primary_sources": [
            "datacenterdynamics", "trendforce-news", "reuters-tech",
        ],
        "secondary_sources": ["theregister", "hpcwire"],
        "discovery_sources": [],
        "cn_keywords": ["数据中心 建设 2026 容量", "超大规模 数据中心 2026 资本开支"],
    },
    "product-mgmt": {
        "name": "产品与企业管理",
        "output_dir": "01_survey/industry-research/",
        "frequency": "每月",
        "keywords": [
            "product management 2026 best practice",
            "technology company management 2026",
            "R&D organization 2026 agile",
        ],
        "fallback_keywords": [
            "product management 2026 new",
            "tech management 2026",
        ],
        "discovery_keywords": [],
        "primary_sources": ["techcrunch", "36kr"],
        "secondary_sources": [],
        "discovery_sources": [],
    },
    "llm-dynamics": {
        "name": "大模型动态追踪",
        "output_dir": "01_survey/industry-research/",
        "frequency": "双周",
        "keywords": [
            "large language model 2026 new release",
            "GPT Claude Gemini LLaMA 2026 benchmark",
            "open source LLM 2026 new model",
        ],
        "fallback_keywords": [
            "LLM 2026 latest",
            "AI model 2026 new",
        ],
        "discovery_keywords": [
            "LLM 2026 benchmark comparison",
        ],
        "primary_sources": [
            "techcrunch", "arxiv", "theregister",
        ],
        "secondary_sources": ["github-trending"],
        "discovery_sources": ["arxiv"],
    },
    "tools-tracking": {
        "name": "工具追踪(通用)",
        "output_dir": "01_survey/industry-research/",
        "frequency": "每月",
        "keywords": [
            "software development tools 2026 new",
            "DevOps CI CD 2026 new tools",
            "developer productivity 2026 tools",
        ],
        "fallback_keywords": [
            "development tools 2026 new",
            "DevOps tools 2026",
        ],
        "discovery_keywords": [],
        "primary_sources": ["github-trending", "techcrunch"],
        "secondary_sources": [],
        "discovery_sources": [],
    },
    "rd-mgmt": {
        "name": "研发管理",
        "output_dir": "01_survey/industry-research/",
        "frequency": "每月",
        "keywords": [
            "R&D management 2026 best practice",
            "engineering management 2026",
            "software development management 2026",
        ],
        "fallback_keywords": [
            "R&D 2026 management",
            "engineering org 2026",
        ],
        "discovery_keywords": [],
        "primary_sources": ["techcrunch"],
        "secondary_sources": [],
        "discovery_sources": [],
    },
    "project-mgmt": {
        "name": "项目管理追踪",
        "output_dir": "01_survey/industry-research/",
        "frequency": "每月",
        "keywords": [
            "project management 2026 methodology",
            "agile project management 2026",
            "project management tools 2026",
        ],
        "fallback_keywords": [
            "project management 2026 new",
            "PM 2026 tools",
        ],
        "discovery_keywords": [],
        "primary_sources": ["techcrunch"],
        "secondary_sources": [],
        "discovery_sources": [],
    },
    "reliability-test": {
        "name": "可靠性测试",
        "output_dir": "01_survey/industry-research/",
        "frequency": "每月",
        "keywords": [
            "reliability testing server 2026",
            "server hardware reliability 2026",
            "HALT HASS server testing 2026",
        ],
        "fallback_keywords": [
            "reliability test 2026 server",
            "hardware reliability 2026",
        ],
        "discovery_keywords": [],
        "primary_sources": ["servethehome"],
        "secondary_sources": [],
        "discovery_sources": [],
    },
}


# ══════════════════════════════════════════════
# 源可靠性注册表管理
# ══════════════════════════════════════════════

def _load_registry() -> dict:
    if REGISTRY_FILE.exists():
        try:
            return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"version": 3, "sources": {}, "topics": {}, "discovery_log": []}

def _save_registry(data: dict):
    REGISTRY_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

def record_source_result(topic_or_group: str, source: str, success: bool, note: str = ""):
    """记录源使用结果"""
    reg = _load_registry()
    topics = reg.setdefault("topics", {})
    t = topics.setdefault(topic_or_group, {"sources": {}})
    s = t["sources"].setdefault(source, {
        "success_count": 0, "fail_count": 0,
        "last_success": None, "last_fail": None, "consecutive_fails": 0,
    })
    if success:
        s["success_count"] += 1
        s["last_success"] = TIME_STR
        s["consecutive_fails"] = 0
    else:
        s["fail_count"] += 1
        s["last_fail"] = TIME_STR
        s["consecutive_fails"] += 1

    all_sources = reg.setdefault("sources", {})
    g = all_sources.setdefault(source, {
        "total_uses": 0, "total_success": 0, "total_fail": 0,
        "grade": STABLE_SOURCES.get(source, {}).get("grade", "B"),
    })
    g["total_uses"] = g.get("total_uses", 0) + 1
    if success:
        g["total_success"] = g.get("total_success", 0) + 1
    else:
        g["total_fail"] = g.get("total_fail", 0) + 1

    # 自动降级: 连续 5 次失败降一级
    s_fails = s.get("consecutive_fails", 0)
    if s_fails >= 5:
        current_grade = g.get("grade", "B")
        if current_grade in ("A", "B"):
            g["grade"] = "C" if current_grade == "A" else "D"
            g["auto_downgraded"] = True
            g["downgrade_reason"] = f"consecutive_{s_fails}_fails"

    _save_registry(reg)

def _get_source_grade(source_name: str, reg: dict) -> str:
    if source_name in STABLE_SOURCES:
        base = STABLE_SOURCES[source_name].get("grade", "B")
    else:
        base = "B"
    all_sources = reg.get("sources", {})
    if source_name in all_sources:
        return all_sources[source_name].get("grade", base)
    return base

def _get_topic_empty_count(topic: str, reg: dict) -> int:
    topics = reg.get("topics", {})
    t = topics.get(topic, {})
    sources = t.get("sources", {})
    max_fails = 0
    for src_name, src_data in sources.items():
        cf = src_data.get("consecutive_fails", 0)
        if cf > max_fails:
            max_fails = cf
    return max_fails // max(len(sources), 1)


# ══════════════════════════════════════════════
# 分组操作
# ══════════════════════════════════════════════

def show_groups():
    """显示所有分组及包含的专题"""
    print(f"\n{'='*70}")
    print(f"  📋 行业调研分组 · {DATE_STR}")
    print(f"{'='*70}")
    for gname, gcfg in GROUPS.items():
        topics = gcfg["topics"]
        print(f"\n  {'─'*20}")
        print(f"  [{gname}] {gcfg['name']} · 执行时间 {gcfg['time']} · {len(topics)} 专题")
        print(f"  {'─'*20}")
        for t in topics:
            tc = TOPICS.get(t, {})
            freq = tc.get("frequency", "")
            print(f"    • {t:<24} {tc.get('name','?'):<16} [{freq}]")


def generate_group_plan(group: str) -> dict:
    """生成某组的完整搜索计划"""
    gcfg = GROUPS.get(group)
    if not gcfg:
        return {"error": f"未知分组: {group}. 可用: {list(GROUPS.keys())}"}

    reg = _load_registry()
    topics = gcfg["topics"]

    plan = {
        "group": group,
        "group_name": gcfg["name"],
        "timestamp": TIME_STR,
        "topics": [],
        "total_search_tasks": 0,
        "summary": {},
    }

    for tname in topics:
        tc = TOPICS.get(tname)
        if not tc:
            continue

        # 主源（过滤已降级到 D 的）
        primary = [s for s in tc.get("primary_sources", [])
                   if _get_source_grade(s, reg) != "D"]
        secondary = [s for s in tc.get("secondary_sources", [])
                     if _get_source_grade(s, reg) != "D"]

        # 构建搜索任务
        search_tasks = []
        used_sources = set()

        # 主源 × 关键词
        for src in primary:
            if src in used_sources:
                continue
            src_info = STABLE_SOURCES.get(src)
            if not src_info:
                continue
            for kw in tc.get("keywords", [])[:2]:
                used_sources.add(src)
                url = _build_url(src_info, kw)
                search_tasks.append({
                    "source": src, "source_name": src_info["name"],
                    "grade": src_info.get("grade", "?"), "keyword": kw,
                    "url": url, "method": src_info.get("fetch_method", "web_fetch"),
                })

        # 如果主源不够，补充备用源
        if len(search_tasks) < 3:
            for src in secondary:
                if src in used_sources:
                    continue
                src_info = STABLE_SOURCES.get(src)
                if not src_info:
                    continue
                kw = (tc.get("fallback_keywords") or tc.get("keywords", []))[:1]
                if kw:
                    used_sources.add(src)
                    url = _build_url(src_info, kw[0])
                    search_tasks.append({
                        "source": src, "source_name": src_info["name"],
                        "grade": src_info.get("grade", "?"), "keyword": kw[0],
                        "url": url, "method": src_info.get("fetch_method", "web_fetch"),
                    })

        # 中文关键词（若有）
        cn_kws = tc.get("cn_keywords", [])
        if cn_kws and len(search_tasks) < 5:
            for src in ["jiweinet", "36kr", "laoyaoba"]:
                if src in used_sources:
                    continue
                src_info = STABLE_SOURCES.get(src)
                if not src_info:
                    continue
                if cn_kws:
                    used_sources.add(src)
                    url = _build_url(src_info, cn_kws[0])
                    search_tasks.append({
                        "source": src, "source_name": src_info["name"],
                        "grade": src_info.get("grade", "?"), "keyword": cn_kws[0],
                        "url": url, "method": "web_fetch", "cn": True,
                    })

        topic_plan = {
            "topic": tname,
            "name": tc.get("name", ""),
            "frequency": tc.get("frequency", ""),
            "search_tasks": search_tasks,
            "needs_discovery": _get_topic_empty_count(tname, reg) >= 3,
        }
        plan["topics"].append(topic_plan)
        plan["total_search_tasks"] += len(search_tasks)

    plan["summary"] = {
        "total_topics": len(topics),
        "total_search_tasks": plan["total_search_tasks"],
    }
    return plan


def _build_url(src_info: dict, keyword: str) -> str:
    """构建搜索URL"""
    if "url_template" in src_info:
        kw = keyword.replace(" ", "+")
        return src_info["url_template"].replace("{query}", kw)
    return src_info.get("url", "")


# ══════════════════════════════════════════════
# 源发现引擎
# ══════════════════════════════════════════════

def discover_sources(topic: str) -> dict:
    """触发专题源发现"""
    topic_cfg = TOPICS.get(topic)
    if not topic_cfg:
        return {"error": f"未知专题: {topic}"}

    reg = _load_registry()
    discovery_log = reg.setdefault("discovery_log", [])

    result = {
        "topic": topic, "timestamp": TIME_STR,
        "attempts": [], "new_sources_found": [],
        "fallback_keywords_used": topic_cfg.get("discovery_keywords", []),
    }

    discovery_keywords = topic_cfg.get("discovery_keywords", [])
    if not discovery_keywords:
        discovery_keywords = topic_cfg.get("fallback_keywords", [])
    if not discovery_keywords:
        discovery_keywords = topic_cfg.get("keywords", [])[:2]

    # 策略1: arXiv
    if "arxiv" in topic_cfg.get("discovery_sources", []):
        for kw in discovery_keywords[:2]:
            result["attempts"].append({
                "source": "arxiv", "keyword": kw,
                "status": "recommended",
                "note": "arXiv 已知稳定可用，建议 web_fetch",
            })

    # 策略2: 跨专题源共享
    shared_sources = _cross_topic_source_sharing(topic)
    for s in shared_sources:
        result["new_sources_found"].append(s)

    # 策略3: 中文源（对可用的专题）
    if topic_cfg.get("cn_keywords") and "jiweinet" not in [s.get("source") for s in result["new_sources_found"]]:
        result["new_sources_found"].append({
            "source": "jiweinet", "success_rate": "未测试",
            "from_topic": "system", "from_name": "中文产业源推荐",
            "note": "集微网——中国半导体产业新闻"
        })

    entry = {
        "timestamp": TIME_STR, "topic": topic,
        "discovery_keywords": discovery_keywords,
        "shared_sources": shared_sources,
    }
    discovery_log.append(entry)
    if len(discovery_log) > 50:
        reg["discovery_log"] = discovery_log[-50:]
    _save_registry(reg)

    result["shared_sources"] = shared_sources
    result["recommended_plan"] = _build_recommended_plan(topic, shared_sources)
    return result


def _cross_topic_source_sharing(topic: str) -> list:
    """跨专题源共享"""
    reg = _load_registry()
    topics = reg.get("topics", {})
    shared = []
    for other_topic, other_data in topics.items():
        if other_topic == topic:
            continue
        other_sources = other_data.get("sources", {})
        for src_name, src_stat in other_sources.items():
            total = src_stat.get("success_count", 0) + src_stat.get("fail_count", 0)
            if total >= 2:
                success_rate = src_stat.get("success_count", 0) / total
                if success_rate >= 0.5 and src_name not in [s.get("source") for s in shared]:
                    shared.append({
                        "source": src_name,
                        "success_rate": f"{success_rate:.0%}",
                        "from_topic": other_topic,
                        "from_name": TOPICS.get(other_topic, {}).get("name", other_topic),
                    })
    return shared


def _build_recommended_plan(topic: str, shared_sources: list) -> dict:
    topic_cfg = TOPICS.get(topic)
    plan = {"primary_recommended": [], "secondary_recommended": [], "notes": []}
    stable_sources = topic_cfg.get("primary_sources", []) + topic_cfg.get("secondary_sources", [])
    for s in stable_sources:
        if s in STABLE_SOURCES:
            grade = STABLE_SOURCES[s].get("grade", "B")
            entry = s
            if grade == "A":
                plan["primary_recommended"].append(entry)
            else:
                plan["secondary_recommended"].append(entry)

    if not plan["primary_recommended"] and not plan["secondary_recommended"]:
        plan["notes"].append("⚠️ 所有源均降级，建议 arXiv + 中文源发现")
    if not plan["primary_recommended"]:
        plan["notes"].append("ℹ️ 无 A 级源可用，将使用 B/C 级源+发现源")
    return plan


# ══════════════════════════════════════════════
# 搜索计划输出 (plan command)
# ══════════════════════════════════════════════

def print_group_plan(group: str):
    """打印分组搜索计划"""
    plan = generate_group_plan(group)
    if "error" in plan:
        print(f"❌ {plan['error']}")
        return

    print(f"\n{'='*70}")
    print(f"  📋 [{plan['group_name']}] 搜索计划 · {DATE_STR}")
    print(f"  专题数: {plan['summary']['total_topics']} | 搜索任务: {plan['summary']['total_search_tasks']}")
    print(f"{'='*70}")

    for tp in plan["topics"]:
        tasks = tp["search_tasks"]
        print(f"\n  ┌─ [{tp['topic']}] {tp['name']} ({tp['frequency']})")
        print(f"  ├─ 搜索任务: {len(tasks)} 个")
        discover_mark = " 🚨自愈!" if tp["needs_discovery"] else ""
        if discover_mark:
            print(f"  ├─{discover_mark}")
        for t in tasks[:5]:
            cn_flag = " [中]" if t.get("cn") else ""
            print(f"  │  • {t['source']:<18} {t['source_name']:<20} ({t['grade']}){cn_flag}")
        if len(tasks) > 5:
            print(f"  │  ... 还有 {len(tasks)-5} 个任务")
        print(f"  └─ 输出: tmp/industry-tracker-{group}-{tp['topic']}-{DATE_STR}.json")


# ══════════════════════════════════════════════
# 搜索任务输出 (collect command)
# ══════════════════════════════════════════════

def collect_group_tasks(group: str) -> dict:
    """生成某组所有专题的搜索任务并写入 tmp/"""
    plan = generate_group_plan(group)
    if "error" in plan:
        return plan

    result = {
        "group": group,
        "group_name": plan["group_name"],
        "timestamp": TIME_STR,
        "topics": [],
        "total_tasks": 0,
    }

    for tp in plan["topics"]:
        topic_data = {
            "topic": tp["topic"],
            "name": tp["name"],
            "search_tasks": tp["search_tasks"],
            "needs_discovery": tp["needs_discovery"],
        }
        result["topics"].append(topic_data)
        result["total_tasks"] += len(tp["search_tasks"])

        # 写中间文件
        tmp_file = TMP_DIR / f"industry-tracker-{group}-{tp['topic']}-{DATE_STR}.json"
        tmp_file.write_text(
            json.dumps(topic_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return result


# ══════════════════════════════════════════════
# 注册表状态
# ══════════════════════════════════════════════

def show_registry_status():
    reg = _load_registry()
    print(f"\n{'='*70}")
    print(f"  📊 源可靠性注册表 v{reg.get('version','?')} · {DATE_STR}")
    print(f"{'='*70}")

    all_sources = reg.get("sources", {})
    if not all_sources:
        print("\n  📭 尚无源使用记录。")
        return

    print(f"\n  {'源':<22} {'使用':<6} {'成功':<6} {'失败':<6} {'成功率':<8} {'等级':<6}")
    print(f"  {'─'*54}")
    for sname, sdata in sorted(all_sources.items()):
        total = sdata.get("total_uses", 0)
        success = sdata.get("total_success", 0)
        fail = sdata.get("total_fail", 0)
        rate = f"{success/total:.0%}" if total > 0 else "-"
        grade = sdata.get("grade", "?")
        downgraded = "⬇" if sdata.get("auto_downgraded") else " "
        print(f"  {sname:<22} {total:<6} {success:<6} {fail:<6} {rate:<8} {grade}{downgraded:<5}")

    # 按等级汇总
    grade_count = {}
    for sname, sdata in all_sources.items():
        g = sdata.get("grade", "?")
        grade_count[g] = grade_count.get(g, 0) + 1
    print(f"\n  源健康度: {' '.join([f'{k}={v}' for k,v in sorted(grade_count.items())])}")

    # 分组源健康度
    print(f"\n  {'分组':<12} {'总源数':<8} {'A级':<8} {'B级':<8} {'C/D级':<8}")
    print(f"  {'─'*44}")
    src_by_type = {}
    for sname, sdata in all_sources.items():
        info = STABLE_SOURCES.get(sname, {})
        stype = info.get("type", "unknown")
        g = sdata.get("grade", "?")
        if stype not in src_by_type:
            src_by_type[stype] = {"total": 0, "A": 0, "B": 0, "C": 0, "D": 0}
        src_by_type[stype]["total"] += 1
        src_by_type[stype][g] = src_by_type[stype].get(g, 0) + 1
    for stype, counts in sorted(src_by_type.items()):
        print(f"  {stype:<12} {counts['total']:<8} {counts.get('A',0):<8} {counts.get('B',0):<8} {counts.get('C',0)+counts.get('D',0):<8}")


# ══════════════════════════════════════════════
# 备份源推荐引擎 (v2.1 新增)
# ══════════════════════════════════════════════

def get_source_type(source_name: str) -> str:
    """获取源的类型标识"""
    info = STABLE_SOURCES.get(source_name, {})
    return info.get("type", "tech-news")


def get_backup_for_source(source_name: str, reg: dict) -> dict:
    """
    为指定源生成备份推荐。

    返回:
    {
        "source": str,
        "grade": str,
        "consecutive_fails": int,
        "backup_tier1": [list of backup sources],
        "backup_tier2": [list of backup sources],
        "backup_tier3": [list of universal fallback sources],
        "cross_type_fallback": [跨类型备份],
    }
    """
    all_sources = reg.get("sources", {})
    sdata = all_sources.get(source_name, {})
    grade = sdata.get("grade", STABLE_SOURCES.get(source_name, {}).get("grade", "B"))
    consecutive_fails = 0

    # 从各专题统计中提取连续失败次数
    topics = reg.get("topics", {})
    for tname, tdata in topics.items():
        src_data = tdata.get("sources", {}).get(source_name, {})
        cf = src_data.get("consecutive_fails", 0)
        if cf > consecutive_fails:
            consecutive_fails = cf

    source_type = get_source_type(source_name)
    backup = BACKUP_SOURCES.get(source_type, {})

    # 过滤已降级到 D 级的备份源
    def filter_grade(sources_list: list) -> list:
        return [s for s in (sources_list or [])
                if s != source_name and _get_source_grade(s, reg) != "D"]

    result = {
        "source": source_name,
        "grade": grade,
        "consecutive_fails": consecutive_fails,
        "backup_tier1": filter_grade(backup.get("tier1", [])),
        "backup_tier2": filter_grade(backup.get("tier2", [])),
        "backup_tier3": filter_grade(UNIVERSAL_FALLBACK_SOURCES),
    }

    # 如果当前类型没有备份链（或备份全部降级），尝试跨类型备份
    if not result["backup_tier1"] and not result["backup_tier2"]:
        cross = CROSS_TYPE_BACKUP.get(source_type, {})
        result["cross_type_fallback"] = filter_grade(
            cross.get("tier1", []) + cross.get("tier2", [])
        )
    else:
        result["cross_type_fallback"] = []

    return result


def get_source_health_trend(source_name: str, reg: dict) -> dict:
    """
    分析源的健康趋势。

    返回:
    {
        "source": str,
        "grade": str,
        "total_uses": int,
        "success_rate": float,
        "consecutive_fails": int,
        "status": "healthy" | "warning" | "degraded" | "critical" | "unknown",
        "last_activity": str / None,
        "backup_available": bool,
    }
    """
    all_sources = reg.get("sources", {})
    sdata = all_sources.get(source_name, {})
    total = sdata.get("total_uses", 0)
    success = sdata.get("total_success", 0)
    fail = sdata.get("total_fail", 0)
    grade = sdata.get("grade", STABLE_SOURCES.get(source_name, {}).get("grade", "B"))

    # 提取各专题中该源的最大连续失败数
    consecutive_fails = 0
    last_activity = None
    topics = reg.get("topics", {})
    for tname, tdata in topics.items():
        src_data = tdata.get("sources", {}).get(source_name, {})
        cf = src_data.get("consecutive_fails", 0)
        if cf > consecutive_fails:
            consecutive_fails = cf
        last_s = src_data.get("last_success")
        last_f = src_data.get("last_fail")
        last = last_s or last_f
        if last and (last_activity is None or last > last_activity):
            last_activity = last

    success_rate = success / total if total > 0 else None

    # 健康状态判定
    if grade == "D":
        status = "critical"
    elif grade == "C":
        status = "degraded"
    elif consecutive_fails >= CRITICAL_DEGRADE_THRESHOLD:
        status = "degraded"  # 连续Fails多但还没自动降级
    elif consecutive_fails >= BACKUP_RECOMMEND_THRESHOLD:
        status = "warning"
    elif success_rate is not None and success_rate >= 0.5:
        status = "healthy"
    elif total > 0:
        status = "warning"
    else:
        status = "unknown"

    # 是否有可用备份
    backup_info = get_backup_for_source(source_name, reg)
    has_backup = bool(
        backup_info.get("backup_tier1") or
        backup_info.get("backup_tier2") or
        backup_info.get("backup_tier3") or
        backup_info.get("cross_type_fallback")
    )

    return {
        "source": source_name,
        "grade": grade,
        "total_uses": total,
        "success_rate": success_rate,
        "consecutive_fails": consecutive_fails,
        "status": status,
        "last_activity": last_activity,
        "backup_available": has_backup,
    }


def show_source_health():
    """显示所有源的健康状态仪表盘"""
    reg = _load_registry()
    all_sources = reg.get("sources", {})
    if not all_sources:
        print("\n  📭 尚无源使用记录。")
        return

    # 收集所有已知源的健康数据
    known_sources = set(STABLE_SOURCES.keys()) | set(all_sources.keys())
    health_data = []
    for sname in sorted(known_sources):
        h = get_source_health_trend(sname, reg)
        health_data.append(h)

    # 统计
    status_count = {}
    for h in health_data:
        s = h["status"]
        status_count[s] = status_count.get(s, 0) + 1

    print(f"\n{'='*70}")
    print(f"  🏥 源健康仪表盘 · {DATE_STR}")
    print(f"  合计: {len(health_data)} 源 | 健康: {status_count.get('healthy',0)} | "
          f"警告: {status_count.get('warning',0)} | 降级: {status_count.get('degraded',0)} | "
          f"严重: {status_count.get('critical',0)} | 未知: {status_count.get('unknown',0)}")
    print(f"{'='*70}")

    # 仪表盘表格
    print(f"\n  {'源':<22} {'等级':<6} {'使用':<6} {'成功率':<8} {'连续失败':<8} {'状态':<10} {'有备份':<6}")
    print(f"  {'─'*66}")
    for h in health_data:
        status_icon = {
            "healthy": "✅", "warning": "⚠️", "degraded": "🔴",
            "critical": "⛔", "unknown": "❓",
        }.get(h["status"], "❓")
        rate = f"{h['success_rate']:.0%}" if h['success_rate'] is not None else "-"
        backup_icon = "✅" if h["backup_available"] else "❌"
        cf = h["consecutive_fails"]
        cf_str = f"{cf}×" if cf > 0 else "-"
        last = h["last_activity"][-16:-9] if h["last_activity"] else "从未"
        print(f"  {status_icon} {h['source']:<20} {h['grade']:<6} {h['total_uses']:<6} "
              f"{rate:<8} {cf_str:<8} {last:<10} {backup_icon:<6}")

    # 需要关注的源
    need_attention = [h for h in health_data if h["status"] in ("warning", "degraded", "critical")]
    if need_attention:
        print(f"\n  🔔 需要关注 ({len(need_attention)} 个):")
        for h in need_attention:
            backup_info = get_backup_for_source(h["source"], reg)
            backups = (backup_info.get("backup_tier1", []) +
                       backup_info.get("backup_tier2", []) +
                       backup_info.get("cross_type_fallback", []) +
                       backup_info.get("backup_tier3", []))
            backup_str = ", ".join(backups[:4]) if backups else "⚠️ 无可用备份!"
            print(f"    • {h['source']:<20} [{h['grade']}/{h['status']}] → 建议替补: {backup_str}")


def show_backup_recommendations(group: str = None):
    """
    显示所有降级源的备份推荐。

    参数:
        group: 可选，只显示某分组的专题
    """
    reg = _load_registry()
    all_sources = reg.get("sources", {})

    if not all_sources:
        print("\n  📭 尚无源使用记录。")
        return

    print(f"\n{'='*70}")
    print(f"  🔁 备份源推荐 · {DATE_STR}")
    print(f"{'='*70}")

    # 收集所有已知源的健康状态
    known_sources = set(STABLE_SOURCES.keys()) & set(all_sources.keys())

    # 按状态分组展示
    degraded_sources = []
    for sname in sorted(known_sources):
        h = get_source_health_trend(sname, reg)
        if h["status"] in ("degraded", "critical", "warning"):
            degraded_sources.append(h)

    if not degraded_sources:
        print("\n  ✅ 所有源健康，暂无备份推荐。")
        return

    print(f"\n  {len(degraded_sources)} 个源需要备份替代:\n")

    for h in degraded_sources:
        backup_info = get_backup_for_source(h["source"], reg)
        tier1 = backup_info.get("backup_tier1", [])
        tier2 = backup_info.get("backup_tier2", [])
        tier3 = backup_info.get("backup_tier3", [])
        cross = backup_info.get("cross_type_fallback", [])

        status_icon = {"warning": "⚠️", "degraded": "🔴", "critical": "⛔"}.get(h["status"], "❓")
        print(f"  {status_icon} {h['source']:<20} [等级={h['grade']} 连续失败={h['consecutive_fails']}]")
        if tier1:
            print(f"       Tier 1 → {', '.join(tier1)}")
        if tier2:
            print(f"       Tier 2 → {', '.join(tier2)}")
        if cross:
            print(f"       跨类型 → {', '.join(cross)}")
        if tier3:
            print(f"       通用兜底 → {', '.join(tier3)}")

    # 按分组的备份摘要（如果指定分组）
    if group and group in GROUPS:
        gcfg = GROUPS[group]
        print(f"\n  📋 [{gcfg['name']}] 按专题的备份建议:\n")
        for tname in gcfg["topics"]:
            tc = TOPICS.get(tname)
            if not tc:
                continue
            primary = tc.get("primary_sources", [])
            degraded_primaries = [s for s in primary
                                   if get_source_health_trend(s, reg)["status"] in
                                   ("degraded", "critical", "warning")]
            if degraded_primaries:
                backups = []
                for s in degraded_primaries:
                    bi = get_backup_for_source(s, reg)
                    backups.extend(bi.get("backup_tier1", [])[:2])
                all_backups = list(dict.fromkeys(backups))[:3]
                print(f"    • {tname:<24} {tc.get('name','?')} — "
                      f"降级: {','.join(degraded_primaries)} → 替补: {','.join(all_backups)}")
            else:
                print(f"    • ✅ {tname:<24} {tc.get('name','?')} — 所有主源健康")


# ══════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="行业调研统一跟踪器 v2.0 — 分组·源扩展·预搜索增强",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command")

    # groups
    p_groups = subparsers.add_parser("groups", help="显示所有分组")

    # plan
    p_plan = subparsers.add_parser("plan", help="生成搜索计划")
    p_plan.add_argument("--group", required=True, help="分组名 (hardware/tech/market)")
    p_plan.add_argument("--topic", default="", help="单个专题名（覆盖--group）")

    # collect
    p_collect = subparsers.add_parser("collect", help="生成并保存搜索任务到 tmp/")
    p_collect.add_argument("--group", required=True, help="分组名")

    # register
    p_reg = subparsers.add_parser("register", help="记录源使用结果")
    p_reg.add_argument("--group", required=True, help="专题或分组名")
    p_reg.add_argument("--source", required=True, help="源名")
    p_reg.add_argument("--success", action="store_true", help="成功")
    p_reg.add_argument("--fail", action="store_true", help="失败")
    p_reg.add_argument("--note", default="", help="备注")

    # registry
    p_registry = subparsers.add_parser("registry", help="源注册表管理")
    p_registry.add_argument("--status", action="store_true", help="查看状态")
    p_registry.add_argument("--backup", action="store_true", help="查看降级源的备份推荐")
    p_registry.add_argument("--group", default="", help="按分组过滤备份推荐")
    p_registry.add_argument("--reset", action="store_true", help="重置注册表")

    # health
    p_health = subparsers.add_parser("health", help="源健康仪表盘 + 备份推荐")

    # discover
    p_disc = subparsers.add_parser("discover", help="触发源发现")
    p_disc.add_argument("--topic", required=True, help="专题名")

    args = parser.parse_args()

    if args.command == "groups":
        show_groups()

    elif args.command == "plan":
        if args.topic:
            # 单专题计划
            from pprint import pprint
            result = generate_group_plan(args.group)
            for tp in result["topics"]:
                if tp["topic"] == args.topic:
                    print(json.dumps(tp, ensure_ascii=False, indent=2))
                    return
            print(f"❌ 专题 {args.topic} 不在分组 {args.group} 中")
        else:
            print_group_plan(args.group)

    elif args.command == "collect":
        result = collect_group_tasks(args.group)
        if "error" in result:
            print(f"❌ {result['error']}")
        else:
            print(f"✅ [{result['group_name']}] {result['total_tasks']} 个搜索任务已保存到 tmp/")
            for tp in result["topics"]:
                print(f"  • {tp['topic']:<24} ({len(tp['search_tasks'])} tasks)")

    elif args.command == "register":
        if not args.success and not args.fail:
            print("❌ 请指定 --success 或 --fail")
            return
        record_source_result(
            args.group, args.source,
            success=args.success, note=args.note,
        )
        print(f"✅ 已记录: {args.group}/{args.source} = {'成功' if args.success else '失败'}")

    elif args.command == "registry":
        if args.reset:
            _save_registry({"version": 3, "sources": {}, "topics": {}, "discovery_log": []})
            print("✅ 源注册表已重置 v3")
        elif args.backup:
            show_backup_recommendations(group=args.group if args.group else None)
        elif args.status:
            show_registry_status()
        else:
            show_registry_status()

    elif args.command == "health":
        show_source_health()

    elif args.command == "discover":
        result = discover_sources(args.topic)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
