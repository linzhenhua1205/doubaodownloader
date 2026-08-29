"""任务状态存储 — 支持内存和 Redis 两种后端。"""

from __future__ import annotations

import json
import time
import uuid
from enum import Enum
from typing import Any

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None  # type: ignore[assignment]

from config import settings
from utils import get_logger

log = get_logger("task_store")


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStore:
    """任务状态管理器。生产用 Redis，开发/单机用内存字典。"""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}
        self._redis = None
        self._use_redis = settings.REDIS_URL.startswith("redis://")
        if self._use_redis and aioredis:
            self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    async def create_task(
        self,
        task_type: str,
        user_id: str,
        chat_id: str,
        params: dict[str, Any],
    ) -> str:
        """创建任务并返回 task_id。"""
        task_id = f"task-{uuid.uuid4().hex[:12]}"
        now = time.time()
        task = {
            "task_id": task_id,
            "type": task_type,
            "user_id": user_id,
            "chat_id": chat_id,
            "params": params,
            "status": TaskStatus.PENDING.value,
            "progress": 0.0,
            "result": None,
            "error": None,
            "message_id": None,
            "created_at": now,
            "updated_at": now,
            "completed_at": None,
        }
        if self._redis:
            await self._redis.hset(
                f"task:{task_id}", mapping={k: json.dumps(v) if isinstance(v, dict) else v for k, v in task.items()}
            )
        self._store[task_id] = task
        log.info("task_created", task_id=task_id, task_type=task_type)
        return task_id

    async def get_task(self, task_id: str) -> dict[str, Any] | None:
        """获取任务状态。"""
        if self._redis:
            data = await self._redis.hgetall(f"task:{task_id}")
            if data:
                return {k: json.loads(v) if k == "params" else v for k, v in data.items()}
        return self._store.get(task_id)

    async def update_task(
        self,
        task_id: str,
        *,
        status: str | None = None,
        progress: float | None = None,
        result: Any = None,
        error: str | None = None,
        message_id: str | None = None,
    ) -> None:
        """更新任务状态。"""
        task = await self.get_task(task_id)
        if not task:
            log.warning("task_not_found", task_id=task_id)
            return

        now = time.time()
        if status:
            task["status"] = status
        if progress is not None:
            task["progress"] = progress
        if result is not None:
            task["result"] = result
        if error:
            task["error"] = error
        if message_id:
            task["message_id"] = message_id
        if status in (TaskStatus.COMPLETED.value, TaskStatus.FAILED.value, TaskStatus.CANCELLED.value):
            task["completed_at"] = now
        task["updated_at"] = now

        if self._redis:
            await self._redis.hset(
                f"task:{task_id}",
                mapping={k: json.dumps(v) if isinstance(v, dict) else v for k, v in task.items()},
            )
        self._store[task_id] = task

    async def list_tasks(
        self, user_id: str | None = None, limit: int = 20
    ) -> list[dict[str, Any]]:
        """列出任务（按更新时间倒序）。"""
        tasks = list(self._store.values())
        if user_id:
            tasks = [t for t in tasks if t["user_id"] == user_id]
        tasks.sort(key=lambda t: t["updated_at"], reverse=True)
        return tasks[:limit]


# 全局单例
task_store = TaskStore()
