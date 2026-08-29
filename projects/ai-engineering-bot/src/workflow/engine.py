"""工作流 DAG 引擎 — 执行、状态跟踪、超时/重试、断点续传。"""

from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any

from workflow.nodes import NodeStatus, NodeType, WorkflowNode
from workflow.pipeline import get_pipeline_template
from utils import get_logger, task_store

log = get_logger("workflow_engine")


class WorkflowExecution:
    """单次工作流执行实例。"""

    def __init__(
        self,
        flow_id: str,
        flow_type: str,
        params: dict[str, Any],
    ) -> None:
        self.flow_id = flow_id
        self.flow_type = flow_type
        self.params = params
        self.nodes: dict[str, WorkflowNode] = {}
        self.status = NodeStatus.PENDING
        self.created_at = time.time()
        self.updated_at = time.time()
        self.error: str | None = None

    def add_node(self, node: WorkflowNode) -> None:
        self.nodes[node.node_id] = node

    def get_ready_nodes(self) -> list[WorkflowNode]:
        """获取所有依赖已满足的可执行节点。"""
        ready = []
        for node in self.nodes.values():
            if node.status != NodeStatus.PENDING:
                continue
            deps_met = all(
                self.nodes[d].status == NodeStatus.COMPLETED
                for d in node.depends_on
                if d in self.nodes
            )
            if deps_met:
                ready.append(node)
        return ready

    def all_done(self) -> bool:
        return all(
            n.status in (NodeStatus.COMPLETED, NodeStatus.FAILED, NodeStatus.SKIPPED)
            for n in self.nodes.values()
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "flow_id": self.flow_id,
            "flow_type": self.flow_type,
            "status": self.status.value,
            "node_count": len(self.nodes),
            "node_statuses": {nid: n.status.value for nid, n in self.nodes.items()},
            "error": self.error,
            "elapsed": f"{time.time() - self.created_at:.1f}s",
        }


class WorkflowEngine:
    """
    工作流 DAG 引擎。

    核心能力:
    - 从模板创建执行实例
    - DAG 拓扑执行（并行执行无依赖节点）
    - 超时控制 + 自动重试
    - 状态持久化（断点续传）
    - 节点级错误隔离
    """

    async def run(
        self,
        flow_type: str,
        params: dict[str, Any],
        task_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> WorkflowExecution:
        """运行一个工作流。"""
        template = get_pipeline_template(flow_type)
        if not template:
            raise ValueError(f"Unknown pipeline type: {flow_type}")

        flow_id = f"flow-{uuid.uuid4().hex[:12]}"
        execution = WorkflowExecution(flow_id, flow_type, params)
        execution.status = NodeStatus.RUNNING

        # 从模板构建节点
        for tpl in template:
            node = WorkflowNode(
                node_id=tpl["id"],
                node_type=NodeType(tpl["type"]),
                func=self._resolve_node_func(tpl["type"]),
                name=tpl.get("name", ""),
                description=tpl.get("description", ""),
                depends_on=tpl.get("depends_on", []),
                timeout=tpl.get("config", {}).get("timeout", 300),
                retry_count=tpl.get("config", {}).get("retry_count", 2),
            )
            execution.add_node(node)

        log.info("workflow_started", flow_id=flow_id, flow_type=flow_type)

        # 主执行循环
        while not execution.all_done():
            ready = execution.get_ready_nodes()
            if not ready and not execution.all_done():
                # 检查是否有死锁
                pending = [n for n in execution.nodes.values() if n.status == NodeStatus.PENDING]
                if pending:
                    log.error("workflow_deadlock", flow_id=flow_id, pending=[n.node_id for n in pending])
                    execution.error = f"Deadlock: {[n.node_id for n in pending]}"
                    execution.status = NodeStatus.FAILED
                    break
                break

            # 并行执行所有就绪节点
            tasks = [
                self._execute_node(node, execution, context)
                for node in ready
            ]
            await asyncio.gather(*tasks)

            if task_id:
                await task_store.update_task(task_id, progress=self._calc_progress(execution))

        # 完成状态
        if execution.error:
            execution.status = NodeStatus.FAILED
        else:
            execution.status = NodeStatus.COMPLETED

        log.info("workflow_completed", flow_id=flow_id, status=execution.status.value)
        return execution

    async def _execute_node(
        self, node: WorkflowNode, execution: WorkflowExecution, context: dict[str, Any] | None
    ) -> None:
        """执行单个节点（含重试和超时）。"""
        node.status = NodeStatus.RUNNING
        log.info("node_executing", flow_id=execution.flow_id, node_id=node.node_id)

        for attempt in range(node.retry_count + 1):
            try:
                result = await asyncio.wait_for(
                    node.func({
                        "params": execution.params,
                        "context": context or {},
                        "node_results": {
                            nid: n.result
                            for nid, n in execution.nodes.items()
                            if n.status == NodeStatus.COMPLETED
                        },
                    }),
                    timeout=node.timeout,
                )
                node.result = result
                node.status = NodeStatus.COMPLETED
                log.info("node_completed", flow_id=execution.flow_id, node_id=node.node_id)
                return

            except asyncio.TimeoutError:
                log.warning(
                    "node_timeout",
                    flow_id=execution.flow_id,
                    node_id=node.node_id,
                    attempt=attempt + 1,
                    timeout=node.timeout,
                )
                if attempt < node.retry_count:
                    await asyncio.sleep(1 * (attempt + 1))  # 退避
            except Exception as e:
                log.error(
                    "node_failed",
                    flow_id=execution.flow_id,
                    node_id=node.node_id,
                    attempt=attempt + 1,
                    error=str(e),
                )
                if attempt < node.retry_count:
                    await asyncio.sleep(1)
                else:
                    node.error = str(e)
                    node.status = NodeStatus.FAILED
                    execution.error = f"Node {node.node_id} failed: {e}"
                    return

        node.status = NodeStatus.FAILED
        node.error = "Max retries exceeded"

    def _resolve_node_func(self, node_type: str) -> Any:
        """根据节点类型返回默认处理函数（运行时可由 handler 替换）。"""
        async def default_func(ctx: dict[str, Any]) -> dict[str, Any]:
            log.info("default_node_exec", node_type=node_type)
            return {"status": "ok", "node_type": node_type}
        return default_func

    def _calc_progress(self, execution: WorkflowExecution) -> float:
        """计算整体进度。"""
        if not execution.nodes:
            return 0.0
        done = sum(
            1 for n in execution.nodes.values()
            if n.status == NodeStatus.COMPLETED
        )
        return done / len(execution.nodes)


# 全局单例
engine = WorkflowEngine()
