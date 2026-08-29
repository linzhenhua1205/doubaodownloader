#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
llm_client.py — 本地 LLM 客户端（Ollama REST API，零第三方依赖）
=================================================================
设计约束: 32K 上下文上限 → 请求 payload ≤16K tokens, num_ctx 限制 8192。
特性:
  - 模型映射: L1 → 3B, L2 → 7B (自动降级: 7B 失败 → 3B)
  - 超时/重试: 网络超时重试 2 次
  - 结构化输出: 支持 JSON 模式(可选)

用法:
  from llm_client import LLMClient
  client = LLMClient(base_url="http://127.0.0.1:11434")
  out = client.generate(prompt, model_key="L2")
"""
from __future__ import annotations

import json
import time
import urllib.request
import urllib.error


class LLMError(RuntimeError):
    pass


class LLMClient:
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        models: dict | None = None,
        num_ctx: int = 8192,
        timeout: float = 300.0,
        max_retries: int = 2,
    ):
        """
        models: {"L1": "qwen2.5:3b-instruct-q4_K_M", "L2": "qwen2.5:7b-instruct-q4_K_M"}
        """
        self.base_url = base_url.rstrip("/")
        self.models = models or {
            "L1": "qwen2.5:3b-instruct-q4_K_M",
            "L2": "qwen2.5:7b-instruct-q4_K_M",
        }
        self.num_ctx = num_ctx          # KV cache 限制, 8G 显存下 7B 必须 ≤8192
        self.timeout = timeout
        self.max_retries = max_retries

    # ---------- Ollama API ----------
    def _post(self, payload: dict) -> dict:
        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def generate(self, prompt: str, model_key: str = "L2", format_json: bool = False) -> str:
        """调用 LLM, 失败自动降级(7B→3B)。返回文本(或 JSON 字符串)。"""
        candidates = [self.models.get(model_key, self.models["L2"]), self.models["L1"]]
        last_err: Exception | None = None
        for attempt in range(self.max_retries + 1):
            for model in candidates:
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_ctx": self.num_ctx, "temperature": 0.2},
                }
                if format_json:
                    payload["format"] = "json"
                try:
                    resp = self._post(payload)
                    return resp.get("response", "")
                except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError) as e:
                    last_err = e
                    time.sleep(2 * (attempt + 1))  # 退避重试
        raise LLMError(f"LLM 调用失败(已重试并降级): {last_err}")

    def health(self) -> bool:
        """检查 Ollama 是否在线。"""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return "models" in data
        except Exception:
            return False


# ---------- 自测 ----------
if __name__ == "__main__":
    c = LLMClient()
    print(f"Ollama 在线: {c.health()}")
    if c.health():
        out = c.generate("请回复: OK", model_key="L1")
        print(f"测试输出: {out[:50]!r}")
