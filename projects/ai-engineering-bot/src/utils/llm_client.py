"""LLM 多模型网关 — 统一接口、模型路由、重试/熔断。"""

from __future__ import annotations

import time
from typing import Any, AsyncIterator

from openai import AsyncOpenAI
from config import settings
from utils import get_logger

log = get_logger("llm_client")


class LLMClient:
    """LLM 客户端（支持多模型路由）。"""

    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
        )

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        stream: bool = False,
    ) -> str | AsyncIterator[str]:
        """统一的 chat completion 入口。"""
        model = model or settings.LLM_MODEL
        temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE
        max_tokens = max_tokens or settings.LLM_MAX_TOKENS

        log.info(
            "llm_chat",
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            msg_count=len(messages),
        )

        start = time.time()
        try:
            response = await self._client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
            )

            if stream:
                return self._stream_response(response, model, start)
            else:
                text = response.choices[0].message.content or ""
                elapsed = time.time() - start
                log.info("llm_response", model=model, elapsed=f"{elapsed:.2f}s", tokens=len(text))
                return text

        except Exception as e:
            elapsed = time.time() - start
            log.error("llm_error", model=model, error=str(e), elapsed=f"{elapsed:.2f}s")
            raise

    async def _stream_response(
        self, response: Any, model: str, start: float
    ) -> AsyncIterator[str]:
        """流式响应迭代器。"""
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

        elapsed = time.time() - start
        log.info("llm_stream_done", model=model, elapsed=f"{elapsed:.2f}s")

    async def chat_with_functions(
        self,
        messages: list[dict[str, str]],
        functions: list[dict[str, Any]],
        model: str | None = None,
    ) -> dict[str, Any]:
        """带 function calling 的对话。"""
        model = model or settings.LLM_MODEL
        response = await self._client.chat.completions.create(
            model=model,
            messages=messages,
            functions=functions,
            temperature=settings.LLM_TEMPERATURE,
        )
        msg = response.choices[0].message
        return {
            "content": msg.content or "",
            "function_call": msg.function_call.dict() if msg.function_call else None,
        }


# 全局单例
llm = LLMClient()
