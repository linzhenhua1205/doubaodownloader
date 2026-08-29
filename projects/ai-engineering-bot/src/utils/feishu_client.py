"""飞书 API 客户端 — 封装认证、消息发送、卡片交互、审批流调用。"""

from __future__ import annotations

import time
from typing import Any

import httpx
from config import settings
from utils import get_logger

log = get_logger("feishu_client")


class FeishuClient:
    """飞书 API 客户端（非官方 SDK，轻量封装，便于理解和定制）。"""

    BASE = "https://open.feishu.cn/open-apis"

    def __init__(self, app_id: str, app_secret: str) -> None:
        self._app_id = app_id
        self._app_secret = app_secret
        self._token: str = ""
        self._token_expires_at: float = 0.0
        self._client = httpx.AsyncClient(timeout=30.0)

    # ── 认证 ──────────────────────────────────────────────────────────

    async def _refresh_token(self) -> str:
        """获取 tenant_access_token（带缓存）。"""
        if time.time() < self._token_expires_at:
            return self._token

        resp = await self._client.post(
            f"{self.BASE}/auth/v3/tenant_access_token/internal",
            json={"app_id": self._app_id, "app_secret": self._app_secret},
        )
        data = resp.raise_for_status().json()
        self._token = data["tenant_access_token"]
        self._token_expires_at = time.time() + data.get("expire", 7200) - 60
        log.info("feishu_token_refreshed", expires_in=data.get("expire"))
        return self._token

    async def _headers(self) -> dict[str, str]:
        token = await self._refresh_token()
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # ── 消息发送 ──────────────────────────────────────────────────────

    async def send_text(
        self, chat_id: str, text: str, msg_type: str = "text"
    ) -> dict[str, Any]:
        """发送纯文本 / 富文本消息。"""
        headers = await self._headers()
        content = {"text": text} if msg_type == "text" else text
        resp = await self._client.post(
            f"{self.BASE}/im/v1/messages",
            headers=headers,
            json={
                "receive_id": chat_id,
                "receive_id_type": "chat_id",
                "msg_type": msg_type,
                "content": content if isinstance(content, str) else text,
            },
        )
        return resp.raise_for_status().json()

    async def send_card(
        self, chat_id: str, card: dict[str, Any]
    ) -> dict[str, Any]:
        """发送消息卡片。"""
        headers = await self._headers()
        resp = await self._client.post(
            f"{self.BASE}/im/v1/messages",
            headers=headers,
            json={
                "receive_id": chat_id,
                "receive_id_type": "chat_id",
                "msg_type": "interactive",
                "content": __import__("json").dumps(card),
            },
        )
        return resp.raise_for_status().json()

    async def update_card(
        self, token: str, card: dict[str, Any]
    ) -> dict[str, Any]:
        """更新已发送的卡片（用于进度更新 / 交互响应）。"""
        headers = await self._headers()
        resp = await self._client.patch(
            f"{self.BASE}/im/v1/messages/{token}",  # token 即 message_id
            headers=headers,
            json={"content": __import__("json").dumps(card)},
        )
        return resp.raise_for_status().json()

    async def reply_with_card(
        self, message_id: str, card: dict[str, Any]
    ) -> dict[str, Any]:
        """回复消息（带卡片）。"""
        headers = await self._headers()
        resp = await self._client.post(
            f"{self.BASE}/im/v1/messages/{message_id}/reply",
            headers=headers,
            json={
                "msg_type": "interactive",
                "content": __import__("json").dumps(card),
            },
        )
        return resp.raise_for_status().json()

    # ── 文档操作 ──────────────────────────────────────────────────────

    async def get_document_content(self, doc_token: str) -> str:
        """读取飞书文档内容。"""
        headers = await self._headers()
        resp = await self._client.get(
            f"{self.BASE}/docx/v1/documents/{doc_token}/raw_content",
            headers=headers,
        )
        return resp.raise_for_status().json()["data"]["content"]

    async def create_document(
        self, title: str, folder_token: str | None = None
    ) -> dict[str, Any]:
        """创建飞书文档。"""
        headers = await self._headers()
        body: dict[str, Any] = {"title": title}
        if folder_token:
            body["folder_token"] = folder_token
        resp = await self._client.post(
            f"{self.BASE}/docx/v1/documents",
            headers=headers,
            json=body,
        )
        return resp.raise_for_status().json()

    # ── 多维表格操作 ──────────────────────────────────────────────────

    async def append_bitable_record(
        self, app_token: str, table_id: str, fields: dict[str, Any]
    ) -> dict[str, Any]:
        """向多维表格添加一行记录。"""
        headers = await self._headers()
        resp = await self._client.post(
            f"{self.BASE}/bitable/v1/apps/{app_token}/tables/{table_id}/records",
            headers=headers,
            json={"fields": fields},
        )
        return resp.raise_for_status().json()

    # ── 审批操作 ──────────────────────────────────────────────────────

    async def create_approval_instance(
        self, approval_code: str, form_data: dict[str, Any]
    ) -> dict[str, Any]:
        """创建审批实例。"""
        headers = await self._headers()
        resp = await self._client.post(
            f"{self.BASE}/approval/v4/instances",
            headers=headers,
            json={
                "approval_code": approval_code,
                "form": [{"name": k, "value": v} for k, v in form_data.items()],
            },
        )
        return resp.raise_for_status().json()

    # ── 资源清理 ──────────────────────────────────────────────────────

    async def close(self) -> None:
        await self._client.aclose()


# 全局单例
feishu = FeishuClient(settings.FEISHU_APP_ID, settings.FEISHU_APP_SECRET)
