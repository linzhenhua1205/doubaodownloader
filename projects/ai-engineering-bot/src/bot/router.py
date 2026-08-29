"""
飞书机器人指令路由 — 解析消息 → 匹配指令 → 分发到处理器。

指令格式:
  /ai ask [问题]
  /ai research [topic]
  /ai review [pr_id]
  /ai doc [topic]
  /ai analyze [issue]
  /ai summary [url]
  /ai plan [description]
  /ai status [task_id]
  /ai help

也支持 @机器人 自然语言。
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Callable, Coroutine

from utils import get_logger

log = get_logger("router")


class Intent(str, Enum):
    ASK = "ask"                 # 即问即答（RAG）
    RESEARCH = "research"       # 技术调研流水线
    REVIEW = "review"           # 代码审查流水线
    DOC = "doc"                 # 生成技术文档
    ANALYZE = "analyze"         # 问题诊断流水线
    SUMMARY = "summary"         # 摘要归档
    PLAN = "plan"               # 任务分解
    STATUS = "status"           # 查询任务状态
    CANCEL = "cancel"           # 取消任务
    STATS = "stats"             # 使用统计
    FEEDBACK = "feedback"       # 反馈
    HELP = "help"               # 帮助
    CHAT = "chat"               # 自由对话（兜底）


HandlerFunc = Callable[..., Coroutine]

# ── 指令模式匹配 ──────────────────────────────────────────────────────

# 优先级从高到低
COMMAND_PATTERNS: list[tuple[re.Pattern, Intent]] = [
    (re.compile(r"^/ai\s+ask\s+(.+)$", re.IGNORECASE), Intent.ASK),
    (re.compile(r"^/ai\s+research\s+(.+)$", re.IGNORECASE), Intent.RESEARCH),
    (re.compile(r"^/ai\s+review\s+(.+)$", re.IGNORECASE), Intent.REVIEW),
    (re.compile(r"^/ai\s+doc\s+(.+)$", re.IGNORECASE), Intent.DOC),
    (re.compile(r"^/ai\s+analyze\s+(.+)$", re.IGNORECASE), Intent.ANALYZE),
    (re.compile(r"^/ai\s+summary\s+(.+)$", re.IGNORECASE), Intent.SUMMARY),
    (re.compile(r"^/ai\s+plan\s+(.+)$", re.IGNORECASE), Intent.PLAN),
    (re.compile(r"^/ai\s+status\s*$", re.IGNORECASE), Intent.STATUS),
    (re.compile(r"^/ai\s+status\s+(.+)$", re.IGNORECASE), Intent.STATUS),
    (re.compile(r"^/ai\s+cancel\s+(.+)$", re.IGNORECASE), Intent.CANCEL),
    (re.compile(r"^/ai\s+stats\s*$", re.IGNORECASE), Intent.STATS),
    (re.compile(r"^/ai\s+stats\s+(.+)$", re.IGNORECASE), Intent.STATS),
    (re.compile(r"^/ai\s+feedback\s+(.+)$", re.IGNORECASE), Intent.FEEDBACK),
    (re.compile(r"^/ai\s+help\s*$", re.IGNORECASE), Intent.HELP),
]


class MessageRouter:
    """消息路由器 — 解析指令/意图 → 派发到处理器。"""

    def __init__(self) -> None:
        self._handlers: dict[Intent, HandlerFunc] = {}

    def register(self, intent: Intent, handler: HandlerFunc) -> None:
        """注册指定意图的处理器。"""
        self._handlers[intent] = handler
        log.info("handler_registered", intent=intent.value)

    async def dispatch(
        self, text: str, user_id: str, chat_id: str, message_id: str
    ) -> tuple[Intent, str, HandlerFunc | None]:
        """解析消息 → 返回 (intent, parameter, handler)。"""
        # 1. 尝试匹配指令模式
        text_stripped = text.strip()
        for pattern, intent in COMMAND_PATTERNS:
            match = pattern.match(text_stripped)
            if match:
                param = match.group(1).strip() if match.lastindex else ""
                handler = self._handlers.get(intent)
                return intent, param, handler

        # 2. 兜底: 自由对话模式
        handler = self._handlers.get(Intent.CHAT)
        return Intent.CHAT, text_stripped, handler


# 全局单例
router = MessageRouter()
