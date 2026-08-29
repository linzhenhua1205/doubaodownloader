"""工作流节点类型定义 — DAG 中的各类节点。"""

from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Coroutine


class NodeType(str, Enum):
    """节点类型枚举。"""
    INPUT_QA = "input_qa"                   # 输入质量门
    MULTI_PATH = "multi_path"               # 多路并行
    CONVERGENCE = "convergence"             # 汇聚/冲突消解
    VERIFICATION = "verification"           # 验证循环
    CONSTRAINT = "constraint"               # 约束执行
    EXPERT_GATE = "expert_gate"             # 专家终审
    LLM_CALL = "llm_call"                  # LLM 调用
    TOOL_CALL = "tool_call"                # 工具调用
    CONDITION = "condition"                # 条件分支
    SUB_FLOW = "sub_flow"                  # 子工作流
    OUTPUT = "output"                       # 输出节点


class NodeStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


NodeFunc = Callable[..., Coroutine[Any, Any, Any]]


class WorkflowNode:
    """工作流 DAG 中的一个节点。"""

    def __init__(
        self,
        node_id: str,
        node_type: NodeType,
        func: NodeFunc,
        name: str = "",
        description: str = "",
        timeout: int = 300,
        retry_count: int = 2,
        depends_on: list[str] | None = None,
    ) -> None:
        self.node_id = node_id
        self.node_type = node_type
        self.func = func
        self.name = name or node_id
        self.description = description
        self.timeout = timeout
        self.retry_count = retry_count
        self.depends_on = depends_on or []
        self.status = NodeStatus.PENDING
        self.result: Any = None
        self.error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "name": self.name,
            "status": self.status.value,
            "depends_on": self.depends_on,
        }
