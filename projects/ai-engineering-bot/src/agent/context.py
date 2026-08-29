"""会话/项目上下文管理 — Agent 间的上下文传递、知识库引用、状态持久化。"""

from __future__ import annotations

import time
import uuid
from typing import Any


class SessionContext:
    """单个会话/项目的上下文容器。"""

    def __init__(
        self,
        session_id: str,
        user_id: str,
        chat_id: str,
        title: str = "",
    ) -> None:
        self.session_id = session_id
        self.user_id = user_id
        self.chat_id = chat_id
        self.title = title
        self.created_at = time.time()
        self.updated_at = time.time()

        # 对话历史（精简版，保留关键消息）
        self.messages: list[dict[str, str]] = []

        # Agent 间共享上下文
        self.shared_context: dict[str, Any] = {}

        # 当前活跃的 task_id
        self.active_task_id: str | None = None

        # 引用过的知识库文档
        self.referenced_docs: list[str] = []

    def add_message(self, role: str, content: str) -> None:
        """追加消息到历史。"""
        self.messages.append({"role": role, "content": content})
        self.updated_at = time.time()

    def set_shared(self, key: str, value: Any) -> None:
        """设置 Agent 间共享上下文。"""
        self.shared_context[key] = value
        self.updated_at = time.time()

    def get_shared(self, key: str, default: Any = None) -> Any:
        """获取 Agent 间共享上下文。"""
        return self.shared_context.get(key, default)

    def add_reference(self, doc_path: str) -> None:
        """记录引用过的知识库文档。"""
        if doc_path not in self.referenced_docs:
            self.referenced_docs.append(doc_path)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "chat_id": self.chat_id,
            "title": self.title,
            "message_count": len(self.messages),
            "active_task_id": self.active_task_id,
            "referenced_docs": self.referenced_docs,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class ContextManager:
    """全局上下文管理器 — 按 chat_id 管理多个会话上下文。"""

    def __init__(self) -> None:
        self._sessions: dict[str, SessionContext] = {}  # chat_id → SessionContext

    def get_or_create(self, user_id: str, chat_id: str) -> SessionContext:
        """获取或创建会话上下文。"""
        if chat_id not in self._sessions:
            self._sessions[chat_id] = SessionContext(
                session_id=f"session-{uuid.uuid4().hex[:12]}",
                user_id=user_id,
                chat_id=chat_id,
            )
        return self._sessions[chat_id]

    def get(self, chat_id: str) -> SessionContext | None:
        """获取指定 chat_id 的上下文。"""
        return self._sessions.get(chat_id)

    def clear(self, chat_id: str) -> None:
        """清空指定会话的上下文。"""
        self._sessions.pop(chat_id, None)

    def list_active(self) -> list[dict[str, Any]]:
        """列出所有活跃会话。"""
        return [
            ctx.to_dict()
            for ctx in sorted(
                self._sessions.values(),
                key=lambda c: c.updated_at,
                reverse=True,
            )
        ]


# 全局单例
context_manager = ContextManager()
