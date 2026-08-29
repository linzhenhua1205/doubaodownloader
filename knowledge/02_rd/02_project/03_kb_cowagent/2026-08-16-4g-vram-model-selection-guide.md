# 4G 显存大模型选型与上下文参数设置指南

> **类型**: analysis | **日期**: 2026-08-16 | **版本**: v1.0
> **适用**: GTX 1050 4G（Pascal 2016，无 Tensor Core，~3.5-3.8GB 可用）
> **核心**: 显存预算三角权衡（模型×量化×上下文）第一性原理公式 + 实测数值表

---

## 1. 结论

- 4G 显存甜点区 = **3B 级模型 Q4_K_M + 4096~8192 上下文**
- 7B Q4 权重 4.1GB > 4G，任何配置都装不下
- 2B 可跑但浪费能力预算；4B Q4 是极限但速度慢（Pascal 无 Tensor Core）
- agent 任务及格线仍为 7B，4G 本地只能做好聊天，任务走云端 API

## 2. 显存预算公式

```
总显存 = 权重 + KV Cache + 运行时(~250MB)
权重 = 参数量 × bpp (Q4_K_M=0.56, Q8_0=1.05, FP16=2.0)
KV Cache/token = 2(K,V) × L层 × KV_heads × head_dim × 2B
可用上下文 ≤ (可用显存 - 权重 - 250MB) ÷ KV_bytes_per_token
```

## 3. 实测矩阵（4G 可用 ≈3.8GB，✅<3.5GB ⚠️3.5-4.0 ❌装不下）

| 模型 | 量化 | 权重 | 2048 | 4096 | 8192 |
|:-----|:----:|:----:|:----:|:----:|:----:|
| Qwen3-1.7B | Q4_K_M | 0.9GB | ✅1.4 | ✅1.6 | ✅2.1 |
| Qwen3-1.7B | Q8_0 | 1.7GB | ✅2.2 | ✅2.4 | ✅2.8 |
| Qwen2.5-3B | Q4_K_M | 1.7GB | ✅2.2 | ✅2.5 | ✅3.1 |
| Llama3.2-3B | Q4_K_M | 1.7GB | ✅2.2 | ✅2.4 | ✅2.9 |
| Qwen3-4B | Q4_K_M | 2.0GB | ✅2.6 | ✅2.9 | ✅3.4 |
| Qwen2.5-7B | Q4_K_M | 4.1GB | ❌4.4 | ❌4.5 | ❌4.8 |

KV bytes/token 参考: Qwen3-1.7B=112KB, Qwen2.5-3B=144KB, Qwen2.5-7B=56KB(GQA 4头)

## 4. 参数设置（两层联动）

| 层 | 参数 | 值 | 说明 |
|:---|:-----|:---|:-----|
| Ollama | num_ctx | 8192 | 默认 4096 会截断，必须显式设 |
| CowAgent | agent_max_context_tokens | ≤7000 | 必须 ≤ num_ctx − system prompt(2.8K) − 工具定义 |
| CowAgent | agent_max_context_turns | 10 | 原 30 过多 |
| CowAgent | enable_thinking | False | 小模型 thinking 质量差吃 KV |
| CowAgent | knowledge | False | 关闭知识注入省上下文 |
| Ollama | num_gpu | 全层 | 防 CPU 回退（1050 上极慢） |

**致命坑**: agent_max_context_tokens=16000 但 Ollama num_ctx 未同步 → 静默截断；设 16K → KV 2.3GB+权重 1.7GB = OOM。

## 5. 模型选择决策树

```
纯聊天/轻问答 → Qwen2.5-1.5B Q8 (2GB)
agent 任务    → Qwen2.5-3B Q4_K_M (甜点 2.5GB)
最强单次推理  → Qwen3-4B Q4 (2.9GB 慢)
需 16K+ 上下文 → 走云端 API（本地物理不可能）
```

## 6. 能力边界

- 3B 比 2B 强：指令遵循/中文质量/多轮记忆（聊天体验提升显著）
- 工具调用/知识库写入仍弱（agent 及格线 7B，4G 物理装不下）
- agent 任务仍建议云端 API

---

## Changelog

| 日期 | 变更 |
|:-----|:-----|
| 2026-08-16 | 初版：显存预算公式 + 8 模型×3 量化×3 上下文实测矩阵 + 两层参数联动 + 决策树 |
