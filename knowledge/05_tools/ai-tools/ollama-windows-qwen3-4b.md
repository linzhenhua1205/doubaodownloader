# Ollama Windows 设置：qwen3:4b（4G 显存）

> **类型**: concepts | **日期**: 2026-08-16 | **版本**: v1.0
> **硬件**: GTX 1050 4G (Windows) | **架构来源**: ModelScope Qwen/Qwen3-4B/config.json 实测 + 用户 /show info 实测

---

## 1. 架构确认（与 qwen3.5:2b 的关键区别）

- qwen3:4b = **传统全注意力** Qwen3ForCausalLM：36层, GQA 8KV头, head_dim=128
- KV = **144KB/token**（随上下文线性增长，非 DeltaNet）
- 用户 /show info 实测: Q4_K_M, 4.0B, context 262144(理论窗口)
- ⚠️ 理论窗口 262144 ≠ 4G 显存可跑值

## 2. 4G 显存预算（权重 2.29GB Q4_K_M + 运行时 250MB）

| 上下文 | KV | 总占用 | 判断 |
|:------:|:--:|:------:|:----:|
| 2048 | 288MB | 2.8GB | ✅ 保守 |
| 4096 | 576MB | 3.1GB | ✅ 甜点 |
| 8192 | 1.15GB | 3.7GB | ⚠️ 极限 |
| 16384 | 2.3GB | 4.8GB | ❌ |

**推荐 num_ctx=4096**；要 32K → 换 qwen3.5:2b（DeltaNet，见 ollama-qwen35-2b-4g.md）

## 3. Windows 四种设置方式

### 方式1: 交互式
```cmd
ollama run qwen3:4b --verbose --num-ctx 4096 --num-gpu 36 --temperature 0.3 --keepalive 30m
```

### 方式2: 环境变量（服务级，需重启 ollama）
```cmd
setx OLLAMA_CONTEXT_LENGTH 4096
setx OLLAMA_KEEP_ALIVE 30m
taskkill /f /im ollama.exe && start "" "%LOCALAPPDATA%\Programs\Ollama\ollama app.exe"
```

### 方式3: Modelfile 固化（对 API 生效，推荐）
```dockerfile
FROM qwen3:4b
PARAMETER num_ctx 4096
PARAMETER num_gpu 36
PARAMETER num_predict 1024
PARAMETER temperature 0.3
PARAMETER top_p 0.9
```
```cmd
ollama create qwen3:4b-ctx4k -f %USERPROFILE%\Modelfile-qwen3-4b
```

### 方式4: CowAgent
- OPENAI_API_BASE=http://127.0.0.1:11434/v1, MODEL=qwen3:4b-ctx4k
- agent_max_context_tokens ≤ 3000

## 4. Windows 问题速查

| 问题 | 解决 |
|:-----|:-----|
| 环境变量不生效 | 重启 ollama 服务 |
| OOM | num_gpu 36→24→12；num_ctx 4096→2048 |
| API 不通 | 防火墙 11434；curl /api/tags |
| agent 记不住 | agent_max_context_tokens > num_ctx，砍到 3000 |
| 速度 <2 tok/s | GPU 层数回退 CPU |

---

## Changelog

| 日期 | 变更 |
|:-----|:-----|
| 2026-08-16 | 初版：qwen3:4b 传统架构确认 + 4G 预算 + Windows 四种设置 + 问题速查 |
