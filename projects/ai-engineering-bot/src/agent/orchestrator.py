"""Agent 编排引擎 — 任务分解 → Agent 角色分配 → 结果汇聚。"""

from __future__ import annotations

from typing import Any

from agent.context import SessionContext
from agent.roles import ROLE_REGISTRY, AgentRole
from utils import get_logger, llm

log = get_logger("orchestrator")


class AgentOrchestrator:
    """
    Agent 编排器。

    核心流程:
    1. 接收任务描述
    2. (可选) 任务分解 — 调用 LLM 将大任务拆成子任务
    3. 角色分配 — 为每个子任务匹配最合适的 Agent 角色
    4. 执行 — 按角色 system_prompt 调用 LLM
    5. 结果汇聚 — 合并各 Agent 输出
    """

    async def execute(
        self,
        task: str,
        context: SessionContext,
        roles: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        执行一个任务（自动或指定角色）。

        Args:
            task: 任务描述
            context: 会话上下文
            roles: 指定角色列表，None 则自动分配

        Returns:
            {"result": 汇聚后的结果, "stages": 各阶段输出}
        """
        if roles:
            # 使用指定的角色列表
            agent_roles = [ROLE_REGISTRY[r] for r in roles if r in ROLE_REGISTRY]
        else:
            # 自动分解并分配角色
            agent_roles = await self._decompose_and_assign(task, context)

        # 逐角色执行
        stage_results = {}
        for role in agent_roles:
            log.info("agent_executing", role=role.name, task_preview=task[:60])
            result = await self._execute_role(role, task, context)
            stage_results[role.name] = result

        # 汇聚结果
        final = await self._converge(stage_results, task, context)

        return {"result": final, "stages": stage_results}

    async def _decompose_and_assign(
        self, task: str, context: SessionContext
    ) -> list[AgentRole]:
        """自动分解任务并分配 Agent 角色。"""
        roles_info = "\n".join(
            f"- {r.name}: {r.description}"
            for r in ROLE_REGISTRY.values()
        )
        messages = [
            {
                "role": "system",
                "content": (
                    "你是 Agent 编排器。请分析以下任务，选择最合适的 1-3 个 Agent 角色来执行。\n"
                    f"可用角色:\n{roles_info}\n\n"
                    "请只返回角色名列表（逗号分隔），例如: analyst,architect"
                ),
            },
            {"role": "user", "content": task},
        ]

        response = await llm.chat(messages)
        selected = [
            ROLE_REGISTRY[name.strip()]
            for name in response.split(",")
            if name.strip() in ROLE_REGISTRY
        ]
        return selected or [ROLE_REGISTRY["analyst"]]  # 兜底用 analyst

    async def _execute_role(
        self, role: AgentRole, task: str, context: SessionContext
    ) -> str:
        """让指定角色执行任务。"""
        messages = [
            {"role": "system", "content": role.system_prompt},
        ]

        # 添加上下文
        if context.messages:
            for msg in context.messages[-4:]:  # 最近 4 条
                messages.append(msg)

        messages.append({"role": "user", "content": task})

        return await llm.chat(messages)

    async def _converge(
        self, stage_results: dict[str, str], task: str, context: SessionContext
    ) -> str:
        """汇聚多个 Agent 的输出为统一的最终结果。"""
        if len(stage_results) == 1:
            return list(stage_results.values())[0]

        results_text = "\n\n---\n\n".join(
            f"## {role} 输出:\n{content}"
            for role, content in stage_results.items()
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "你是结果汇聚器。请将以下多个 Agent 的输出整合为一份统一的、"
                    "逻辑连贯的最终报告。去重、互补矛盾、保持 MECE 结构。"
                ),
            },
            {"role": "user", "content": f"原始任务:\n{task}\n\n各 Agent 输出:\n{results_text}"},
        ]

        return await llm.chat(messages)


# 全局单例
orchestrator = AgentOrchestrator()
