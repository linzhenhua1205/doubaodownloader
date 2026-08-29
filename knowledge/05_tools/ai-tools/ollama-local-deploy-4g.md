# Ollama 本地模型部署：4G 显存启动模板（Qwen2.5-3B）

> **类型**: concepts | **日期**: 2026-08-16 | **版本**: v1.0
> **硬件**: GTX 1050 4G（Pascal 2016，无 Tensor Core）
> **关键**: `ollama run` 命令行参数只对交互会话生效；API/CowAgent 调用须用 Modelfile 固化或环境变量

---

## 1. 选型结论

- 模型: `qwen2.5:3b`（Q4_K_M 权重 1.7GB）
- 上下文: 8192（KV 1.2GB + 权重 1.7GB + 运行时 0.3GB ≈ 3.2GB ✅）
- 速度预期: 5-10 tok/s（1050 无 Tensor Core，INT 量化计算慢）
- 若 OOM: num_gpu 36 → 28 → 20 递减

## 2. Modelfile 模板（推荐，API 也生效）

```dockerfile
FROM qwen2.5:3b
PARAMETER num_ctx 8192
PARAMETER num_gpu 36
PARAMETER num_predict 1024
PARAMETER num_keep 64
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.1
```

```bash
ollama create qwen2.5:3b-ctx8k -f ~/Modelfile-qwen25-3b
ollama show qwen2.5:3b-ctx8k --modelfile  # 验证
```

## 3. 三层调用参数生效范围

| 方式 | num_ctx 生效？ | 说明 |
|:-----|:--------------|:-----|
| `ollama run` 命令行 | ✅ | 仅当前会话 |
| API `/api/chat` options | ✅ | 需显式传 options |
| OpenAI 兼容端点 `/v1` | ❌ | 不解析 num_ctx → **必须 Modelfile 或 OLLAMA_CONTEXT_LENGTH** |

## 4. CowAgent 接入

```bash
export OLLAMA_CONTEXT_LENGTH=8192 && ollama serve
# env_config: OPENAI_API_BASE=http://127.0.0.1:11434/v1, MODEL=qwen2.5:3b-ctx8k
```

## 5. 验证清单

1. nvidia-smi 显存 < 3.8GB
2. 长上下文口令测试（6000+ tokens 后仍能答出口令）
3. 速度基准 ≥ 2 tok/s（低于则 CPU 回退）

---

## Changelog

| 日期 | 变更 |
|:-----|:-----|
| 2026-08-16 | 初版：4G 显存 ollama 部署模板（Modelfile 固化 + 三层生效范围 + 验证清单） |
