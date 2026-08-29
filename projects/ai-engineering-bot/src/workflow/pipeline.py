"""6 阶段流水线模板注册 — 预定义常用的工作流模板。"""

from __future__ import annotations

from typing import Any

from workflow.nodes import NodeType, WorkflowNode


def _make_node(
    node_id: str,
    node_type: NodeType,
    name: str,
    description: str,
    depends_on: list[str] | None = None,
) -> WorkflowNode:
    """创建一个空节点（由 workflow engine 在运行时绑定具体 func）。"""
    return WorkflowNode(
        node_id=node_id,
        node_type=node_type,
        func=lambda ctx: {},  # placeholder, 运行时替换
        name=name,
        description=description,
        depends_on=depends_on or [],
    )


# ── 调研流水线 (Research Pipeline) ──────────────────────────────────

RESEARCH_PIPELINE: list[dict[str, Any]] = [
    {
        "id": "input_qa",
        "type": NodeType.INPUT_QA.value,
        "name": "输入质量门",
        "description": "验证调研主题的完整性和清晰度，补全缺失信息",
        "depends_on": [],
        "config": {"required_fields": ["topic", "scope", "depth"]},
    },
    {
        "id": "multi_path_search",
        "type": NodeType.MULTI_PATH.value,
        "name": "多源并行检索",
        "description": "同时搜索知识库、厂商官网、Google、标准规范",
        "depends_on": ["input_qa"],
        "config": {
            "paths": [
                {"source": "knowledge_base", "priority": "high"},
                {"source": "vendor_website", "priority": "high"},
                {"source": "web_search", "priority": "medium"},
                {"source": "standards_body", "priority": "high"},
            ]
        },
    },
    {
        "id": "convergence",
        "type": NodeType.CONVERGENCE.value,
        "name": "信息汇聚",
        "description": "多源信息去重、冲突消解、按可信度加权汇聚",
        "depends_on": ["multi_path_search"],
    },
    {
        "id": "verification",
        "type": NodeType.VERIFICATION.value,
        "name": "验证循环",
        "description": "事实准确性验证、数据交叉核对、逻辑一致性检查",
        "depends_on": ["convergence"],
        "config": {"max_iterations": 3},
    },
    {
        "id": "constraint",
        "type": NodeType.CONSTRAINT.value,
        "name": "约束执行",
        "description": "格式规范、安全红线、术语一致性检查",
        "depends_on": ["verification"],
    },
    {
        "id": "output",
        "type": NodeType.OUTPUT.value,
        "name": "报告生成",
        "description": "生成结构化调研报告 + 归档知识库 + 推送飞书",
        "depends_on": ["constraint"],
    },
]


# ── 代码审查流水线 (Code Review Pipeline) ────────────────────────────

CODE_REVIEW_PIPELINE: list[dict[str, Any]] = [
    {
        "id": "input_qa",
        "type": NodeType.INPUT_QA.value,
        "name": "PR 信息验证",
        "description": "验证 PR ID、获取 diff、检查冲突",
        "depends_on": [],
        "config": {"required_fields": ["pr_id", "repo"]},
    },
    {
        "id": "multi_path_review",
        "type": NodeType.MULTI_PATH.value,
        "name": "多维度并行审查",
        "description": "安全审查、性能审查、架构审查、风格审查",
        "depends_on": ["input_qa"],
        "config": {
            "paths": [
                {"dimension": "security", "priority": "critical"},
                {"dimension": "performance", "priority": "high"},
                {"dimension": "architecture", "priority": "high"},
                {"dimension": "style", "priority": "medium"},
            ]
        },
    },
    {
        "id": "convergence",
        "type": NodeType.CONVERGENCE.value,
        "name": "审查结果汇聚",
        "description": "合并多维审查结果，生成统一 Review Comment",
        "depends_on": ["multi_path_review"],
    },
    {
        "id": "gate",
        "type": NodeType.CONSTRAINT.value,
        "name": "质量门禁",
        "description": "Block/Warn/Pass 三级门禁判定",
        "depends_on": ["convergence"],
        "config": {
            "thresholds": {"block": 30, "warn": 60, "pass": 80},
        },
    },
    {
        "id": "output",
        "type": NodeType.OUTPUT.value,
        "name": "结果输出",
        "description": "提交 Review Comment + 推送飞书通知",
        "depends_on": ["gate"],
    },
]


# ── 问题诊断流水线 (Diagnosis Pipeline) ──────────────────────────────

DIAGNOSIS_PIPELINE: list[dict[str, Any]] = [
    {
        "id": "input_qa",
        "type": NodeType.INPUT_QA.value,
        "name": "问题描述验证",
        "description": "补全问题上下文、症状、环境信息",
        "depends_on": [],
        "config": {"required_fields": ["symptom", "environment"]},
    },
    {
        "id": "fault_analysis",
        "type": NodeType.LLM_CALL.value,
        "name": "根因分析",
        "description": "鱼骨图 + 5W 深度分析",
        "depends_on": ["input_qa"],
    },
    {
        "id": "verification",
        "type": NodeType.VERIFICATION.value,
        "name": "诊断验证",
        "description": "验证推断逻辑、交叉排查",
        "depends_on": ["fault_analysis"],
        "config": {"max_iterations": 3},
    },
    {
        "id": "output",
        "type": NodeType.OUTPUT.value,
        "name": "诊断报告",
        "description": "根因 + 修复步骤 + 预防措施 + 推送飞书",
        "depends_on": ["verification"],
    },
]


# ── 模板注册表 ──────────────────────────────────────────────────────

PIPELINE_REGISTRY: dict[str, list[dict[str, Any]]] = {
    "research": RESEARCH_PIPELINE,
    "code_review": CODE_REVIEW_PIPELINE,
    "diagnosis": DIAGNOSIS_PIPELINE,
}


def get_pipeline_template(name: str) -> list[dict[str, Any]] | None:
    """获取流水线模板。"""
    return PIPELINE_REGISTRY.get(name)
