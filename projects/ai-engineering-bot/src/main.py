"""
FastAPI 入口 — 飞书事件订阅 Webhook + 管理 API。

运行:
  python src/main.py

生产部署:
  uvicorn src.main:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI, Request

from bot.callback import callback_handler
from bot.handler import register_handlers
from bot.router import router
from config import settings
from utils import feishu_client, get_logger, llm, task_store

log = get_logger("main")


# ── 生命周期 ──────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动/关闭生命周期。"""
    log.info("server_starting", host=settings.HOST, port=settings.PORT)

    # 注册所有指令处理器
    register_handlers()

    # 验证飞书凭证
    try:
        token = await feishu_client._refresh_token()
        log.info("feishu_token_ok", token_preview=token[:10])
    except Exception as e:
        log.warning("feishu_token_failed", error=str(e))

    yield

    # 关闭资源
    await feishu_client.close()
    log.info("server_shutdown")


app = FastAPI(title="AI Engineering Bot", version="0.1.0", lifespan=lifespan)


# ── 健康检查 ──────────────────────────────────────────────────────────

@app.get("/health")
async def health() -> dict[str, Any]:
    """健康检查端点。"""
    return {
        "status": "ok",
        "version": "0.1.0",
        "feishu_configured": bool(settings.FEISHU_APP_ID and settings.FEISHU_APP_ID != "cli_xxxxxxxxxxxxxxxx"),
    }


@app.get("/metrics")
async def metrics() -> dict[str, Any]:
    """基础指标端点。"""
    tasks = await task_store.list_tasks(limit=100)
    return {
        "total_tasks": len(tasks),
        "active_tasks": sum(1 for t in tasks if t["status"] in ("pending", "running")),
        "recent_completed": sum(1 for t in tasks if t["status"] == "completed"),
        "recent_failed": sum(1 for t in tasks if t["status"] == "failed"),
    }


# ── 飞书事件订阅 Webhook ─────────────────────────────────────────────

@app.post("/webhook/feishu")
async def feishu_webhook(request: Request) -> dict[str, Any]:
    """
    飞书事件订阅入口。

    处理两类事件:
    1. im.message.receive_v1 — 用户发送消息
    2. card.action.trigger — 用户点击卡片按钮
    """
    body = await request.json()
    header = body.get("header", {})
    event_type = header.get("event_type", "")
    event_body = body.get("event", body)

    log.info("feishu_event_received", event_type=event_type)

    # 飞书 URL 验证挑战
    if event_type == "url_verification":
        return {"challenge": body.get("challenge", "")}

    # ── 消息事件 ──────────────────────────────────────────────────
    if event_type == "im.message.receive_v1":
        return await _handle_message(event_body)

    # ── 卡片回调事件 ──────────────────────────────────────────────
    if event_type == "card.action.trigger":
        return await _handle_card_action(event_body)

    log.warning("unhandled_event_type", event_type=event_type)
    return {"msg": "ok"}


async def _handle_message(event: dict[str, Any]) -> dict[str, Any]:
    """处理 im.message.receive_v1 事件。"""
    message = event.get("message", {})
    sender = event.get("sender", {})

    chat_id = message.get("chat_id", "")
    message_id = message.get("message_id", "")
    sender_id = sender.get("sender_id", {}).get("open_id", "")

    # 只处理文本消息
    msg_type = message.get("message_type", "")
    if msg_type != "text":
        return {"msg": "ignore_non_text"}

    # 解析消息内容
    content_str = message.get("content", "{}")
    try:
        content = json.loads(content_str) if isinstance(content_str, str) else content_str
    except json.JSONDecodeError:
        content = {"text": content_str}

    text = content.get("text", "").strip()

    if not text:
        return {"msg": "empty_text"}

    # 通过路由器解析意图
    intent, param, handler = await router.dispatch(text, sender_id, chat_id, message_id)

    if not handler:
        log.warning("no_handler_for_intent", intent=intent)
        return {"msg": "no_handler"}

    # 执行处理器
    try:
        result = await handler(param, sender_id, chat_id, message_id)
    except Exception as e:
        log.error("handler_error", intent=intent, error=str(e))
        result = f"❌ 处理出错: {str(e)}"

    # 发送回复
    if isinstance(result, dict):
        # 卡片消息
        await feishu_client.reply_with_card(message_id, result)
    else:
        # 文本消息
        await feishu_client.reply_with_card(
            message_id,
            {"config": {"wide_screen_mode": True}, "header": {"title": {"tag": "plain_text", "content": "🤖 AI 回复"}, "template": "blue"}, "elements": [{"tag": "div", "text": {"tag": "lark_md", "content": result}}, {"tag": "hr"}, {"tag": "note", "element": {"tag": "plain_text", "content": f"意图: {intent.value}  |  消息ID: {message_id[:12]}..."}}]}
        )

    return {"msg": "ok"}


async def _handle_card_action(event: dict[str, Any]) -> dict[str, Any]:
    """处理 card.action.trigger 事件。"""
    try:
        await callback_handler.handle(event)
    except Exception as e:
        log.error("callback_error", error=str(e))
    return {"msg": "ok"}


# ── 管理 API ──────────────────────────────────────────────────────────

@app.get("/api/tasks")
async def list_tasks(user_id: str | None = None) -> list[dict[str, Any]]:
    """查询任务列表。"""
    return await task_store.list_tasks(user_id)


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str) -> dict[str, Any] | None:
    """查询单个任务。"""
    return await task_store.get_task(task_id)


@app.get("/api/help")
async def get_help() -> dict[str, Any]:
    """获取帮助信息（指令列表）。"""
    from bot.card_builder import help_card
    return {
        "commands": [
            {"cmd": "/ai ask [问题]", "desc": "即问即答"},
            {"cmd": "/ai research [主题]", "desc": "技术调研流水线"},
            {"cmd": "/ai review [PR_ID]", "desc": "代码审查"},
            {"cmd": "/ai doc [主题]", "desc": "生成技术文档"},
            {"cmd": "/ai analyze [问题]", "desc": "问题诊断"},
            {"cmd": "/ai summary [URL]", "desc": "摘要归档"},
            {"cmd": "/ai plan [描述]", "desc": "任务分解"},
            {"cmd": "/ai status [任务ID]", "desc": "查询任务状态"},
            {"cmd": "/ai help", "desc": "帮助信息"},
        ]
    }


# ── 启动 ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )
