"""
知识库自动化工具集 - 全局配置

存放所有路径、分类映射、忽略列表等可调参数。
"""

import os
from pathlib import Path

# ============================================================
# 基础路径
# ============================================================

WORKSPACE = Path(os.environ.get("COW_WORKSPACE", os.path.expanduser("~/cow")))
IMPORT_DIR = WORKSPACE / "import"
IMPORT_SOURCES = {
    "doubao": IMPORT_DIR / "doubao",
    "doubao20260523": IMPORT_DIR / "doubao20260523",
    "fetched_markdown": IMPORT_DIR / "fetched_markdown",
    "md": IMPORT_DIR / "md",
}
IMPORT_PDF = IMPORT_DIR / "100skill.pdf"
IMPORT_DUPLICATE = IMPORT_DIR / "doubao" / "重复"

KNOWLEDGE_DIR = WORKSPACE / "knowledge"
BAK_DIR = KNOWLEDGE_DIR / "bak"

# ============================================================
# 知识模块分类映射 (关键词 → 目标子目录)
# ============================================================
# 按权重从高到低匹配，第一个命中的优先
# 格式: (权重, [关键词列表], "目标目录/子目录")

CLASSIFICATION_RULES = [
    # --- AI应用 ---
    (90, [
        "AI Agent", "智能体", "Agent框架", "Agent模式", "Agent架构",
        "MCP", "Function Call", "工具调用", "agentic",
    ], "ai-apps"),

    # --- AI框架 ---
    (85, [
        "PyTorch", "TensorFlow", "JAX", "vLLM", "TGI", "TensorRT",
        "推理框架", "训练框架", "DeepSpeed", "Megatron",
    ], "ai-frameworks"),

    # --- 大模型动态 ---
    (80, [
        "大模型", "LLM", "语言模型", "GPT", "Claude", "Gemini",
        "DeepSeek", "Qwen", "通义千问", "文心一言", "GLM",
        "MoE", "混合专家", "Mamba", "transformer",
    ], "llm-trends"),

    # --- 万卡集群与训推优化 ---
    (80, [
        "分布式训练", "集群训练", "万卡", "训推", "KV Cache",
        "推理优化", "高性能计算", "HPC", "训练效率",
    ], "cluster-training"),

    # --- 服务器硬件架构 ---
    (90, [
        "服务器架构", "服务器硬件", "整机设计", "主板", "背板",
        "PCIe", "OAM", "UBB", "SXM", "NVLink", "NVSwitch",
        "机架", "整机柜", "Rack", "服务器电源",
    ], "server-hardware"),

    # --- 超节点专题 ---
    (90, [
        "超节点", "Super POD", "Supernode", "GB200", "NVL72",
        "WSE", "Cerebras", "Atlas 900", "液冷",
        "冷板", "浸没", "散热",
    ], "supernode"),

    # --- BMC与系统管理 ---
    (85, [
        "BMC", "OpenBMC", "Redfish", "IPMI", "固件", "Firmware",
        "BIOS", "UEFI",
    ], "bmc-system"),

    # --- 分布式操作系统 ---
    (80, [
        "NCCL", "RDMA", "GPU Direct", "集合通信", "AllReduce",
        "网络拓扑", "分布式系统", "DPU", "IPU", "SmartNIC",
    ], "distributed-os"),

    # --- 存储 ---
    (85, [
        "SSD", "NVMe", "存储", "HBM", "CXL", "内存池",
        "分布式存储", "文件系统", "Ceph", "Lustre", "GPFS",
        "NAND", "Flash", "DRAM",
    ], "components-storage"),

    # --- 数据中心 ---
    (80, [
        "数据中心", "PUE", "供电", "配电", "UPS", "HVDC",
        "液冷散热", "精密空调", "机柜",
    ], "data-center"),

    # --- 云原生 ---
    (80, [
        "Kubernetes", "K8s", "容器", "Docker", "微服务",
        "Service Mesh", "Istio", "云原生", "CNCF",
        "Serverless",
    ], "cloud-native"),

    # --- 操作系统 ---
    (75, [
        "Linux", "内核", "系统调用", "进程调度", "内存管理",
        "cgroup", "namespace", "eBPF",
    ], "linux-os"),

    # --- 运维运营 ---
    (80, [
        "运维", "监控", "告警", "Prometheus", "Grafana",
        "AIOps", "CMDB", "可观测", "Observability",
    ], "ops-system"),

    # --- 可靠性与测试 ---
    (80, [
        "可靠性", "故障诊断", "FMEA", "测试", "验证",
        "容错", "HA", "高可用", "RAS",
    ], "reliability-testing"),

    # --- 研发管理 ---
    (75, [
        "研发管理", "IPD", "研发流程", "项目管理", "效能",
        "AI辅助研发", "代码生成", "研发效率",
    ], "rd-management"),

    # --- 产品研发 ---
    (80, [
        "产品规划", "产品方案", "产品设计", "需求分析",
        "GTM", "产品定义",
    ], "product-dev"),

    # --- 行业调研 ---
    (70, [
        "市场分析", "行业调研", "竞争格局", "趋势",
        "AI芯片", "GPU对比", "芯片",
    ], "industry-research"),

    # --- 智算方案 ---
    (80, [
        "智算", "算力", "算力中心", "智算中心",
    ], "ai-solutions"),

    # --- 企业管理 ---
    (70, [
        "企业管理", "组织", "战略", "文化", "人才",
        "管理", "领导力",
    ], "enterprise-mgmt"),

    # --- 工具与技术 ---
    (70, [
        "教程", "指南", "速查", "对比", "使用说明",
        "安装", "配置", "调试",
    ], "tools"),

    # --- 概念体系 ---
    (65, [
        "CLI演进", "概念", "方法论", "范式", "命名",
        "信息差", "工程设计",
    ], "concepts"),

    # --- RAG ---
    (80, [
        "RAG", "GraphRAG", "检索增强", "知识图谱",
        "向量数据库",
    ], "rag-technology"),
]

# ============================================================
# 模板路径
# ============================================================

TEMPLATE_PUBLIC = WORKSPACE / "scripts" / "autokb" / "templates" / "public_snippet.md.tpl"


# ============================================================
# 忽略关键词（文件名或内容含这些关键词则跳过）
# ============================================================

IGNORE_KEYWORDS = [
    "重复",
    "duplicate",
    "test",
]

# ============================================================
# 文件名清洗规则
# ============================================================

MAX_FILENAME_LEN = 120
SLUG_SEPARATOR = "-"


# ============================================================
# 日志配置
# ============================================================

LOG_OPERATIONS = True
