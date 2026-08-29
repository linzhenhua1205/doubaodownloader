"""卡片交互回调处理 — 用户点击按钮后的响应逻辑。"""

from __future__ import annotations

from typing import Any

from utils import get_logger, feishu_client, task_store

log = get_logger("callback")


class CardCallbackHandler:
    """卡片回调路由器 — 按 action 前缀分发。"""

    async def handle(self, callback_data: dict[str, Any]) -> dict[str, Any]:
        """
        处理卡片回调。

        callback_data 格式（飞书 card actions）:
        {
            "open_message_id": "om_xxx",
            "open_chat_id": "oc_xxx",
            "operator_id": {"union_id": "..."},
            "action": {"value": "archive:task_xxx", "tag": "button"},
            ...
        }
        """
        action_value = callback_data.get("action", {}).get("value", "")
        chat_id = callback_data.get("open_chat_id", "")
        operator_id = callback_data.get("operator", {}).get("union_id", "")

        log.info("card_callback", action=action_value, chat_id=chat_id)

        # 按 action 前缀路由
        if action_value.startswith("archive:"):
            return await self._handle_archive(action_value, chat_id, operator_id)
        elif action_value.startswith("followup:"):
            return await self._handle_followup(action_value, chat_id, operator_id)
        elif action_value.startswith("cancel:"):
            return await self._handle_cancel(action_value, chat_id, operator_id)
        elif action_value.startswith("detail:"):
            return await self._handle_detail(action_value, chat_id, operator_id)
        elif action_value.startswith("rediagnose:"):
            return await self._handle_rediagnose(action_value, chat_id, operator_id)
        elif action_value.startswith("approve:"):
            return await self._handle_approve(action_value, chat_id, operator_id)
        elif action_value.startswith("reject:"):
            return await self._handle_reject(action_value, chat_id, operator_id)
        elif action_value.startswith("comment:"):
            return await self._handle_comment(action_value, chat_id, operator_id)
        else:
            log.warning("unknown_callback_action", action=action_value)
            # 返回空响应，飞书不会报错
            return {}

    async def _handle_archive(
        self, action: str, chat_id: str, operator_id: str
    ) -> dict[str, Any]:
        """归档到知识库。"""
        task_id = action.replace("archive:", "")
        task = await task_store.get_task(task_id)
        if not task:
            return {"msg": "任务不存在"}

        # TODO: 触发 knowledge-wiki 归档流程
        log.info("archive_triggered", task_id=task_id, operator=operator_id)

        await feishu_client.send_text(
            chat_id,
            f"📚 已触发归档任务 `{task_id}`，完成后将通知您。",
        )
        return {"msg": "归档已触发"}

    async def _handle_followup(
        self, action: str, chat_id: str, operator_id: str
    ) -> dict[str, Any]:
        """追问（记录上下文，等待用户下一句输入）。"""
        task_id = action.replace("followup:", "")
        # TODO: 将 chat_id + operator_id 标记为"等待追问输入"状态
        log.info("followup_requested", task_id=task_id, operator=operator_id)

        await feishu_client.send_text(
            chat_id, "💬 请发送您的追问内容，我会基于原有结果继续分析。"
        )
        return {"msg": "等待追问"}

    async def _handle_cancel(
        self, action: str, chat_id: str, operator_id: str
    ) -> dict[str, Any]:
        """取消任务。"""
        task_id = action.replace("cancel:", "")
        await task_store.update_task(task_id, status="cancelled")
        log.info("task_cancelled", task_id=task_id, operator=operator_id)

        await feishu_client.send_text(chat_id, f"❌ 任务 `{task_id}` 已取消。")
        return {"msg": "已取消"}

    async def _handle_detail(
        self, action: str, chat_id: str, operator_id: str
    ) -> dict[str, Any]:
        """查看完整报告（发送报告摘要或链接）。"""
        task_id = action.replace("detail:", "")
        task = await task_store.get_task(task_id)
        if not task or not task.get("result"):
            await feishu_client.send_text(chat_id, "⚠️ 未找到完整报告。")
            return {"msg": "未找到报告"}

        # TODO: 从 task.result 提取报告内容或跳转链接
        await feishu_client.send_text(
            chat_id, f"📄 完整报告: {task['result'].get('report_url', '')}"
        )
        return {"msg": "已发送报告"}

    async def _handle_rediagnose(
        self, action: str, chat_id: str, operator_id: str
    ) -> dict[str, Any]:
        """重新诊断。"""
        task_id = action.replace("rediagnose:", "")
        log.info("rediagnose_requested", task_id=task_id, operator=operator_id)
        # TODO: 重新触发诊断流水线
        await feishu_client.send_text(chat_id, "🔄 正在重新诊断，请稍候...")
        return {"msg": "重新诊断中"}

    async def _handle_approve(
        self, action: str, chat_id: str, operator_id: str
    ) -> dict[str, Any]:
        """审批通过。"""
        approval_code = action.replace("approve:", "")
        log.info("approval_approved", approval_code=approval_code, operator=operator_id)
        await feishu_client.send_text(chat_id, "✅ 已批准。")
        return {"msg": "已批准"}

    async def _handle_reject(
        self, action: str, chat_id: str, operator_id: str
    ) -> dict[str, Any]:
        """审批驳回。"""
        approval_code = action.replace("reject:", "")
        log.info("approval_rejected", approval_code=approval_code, operator=operator_id)
        await feishu_client.send_text(chat_id, "❌ 已驳回。")
        return {"msg": "已驳回"}

    async def _handle_comment(
        self, action: str, chat_id: str, operator_id: str
    ) -> dict[str, Any]:
        """提意见（等待用户输入意见内容）。"""
        approval_code = action.replace("comment:", "")
        log.info("comment_requested", approval_code=approval_code, operator=operator_id)
        await feishu_client.send_text(chat_id, "📝 请发送您的意见内容。")
        return {"msg": "等待意见"}


# 全局单例
callback_handler = CardCallbackHandler()
