# Ollama 部署 Qwen3.5-2B：4G 显存启动模板（混合注意力架构红利）

> **类型**: concepts | **日期**: 2026-08-16 | **版本**: v1.0
> **硬件**: GTX 1050 4G | **架构来源**: ModelScope Qwen/Qwen3.5-2B/config.json 实测
> **核心发现**: Gated DeltaNet 混合架构 → KV cache 仅传统模型 1/12 → 4G 显存可开 32K 上下文

---

## 1. 架构实测（ModelScope config.json）

```
Qwen3_5ForConditionalGeneration
text_config:
  24层 = 18线性注意力(DeltaNet) + 6全注意力(每4层1个, full_attention_interval=4)
  全注意力: 8头, head_dim=256, KV头=2 (GQA)
  线性注意力: 16K头×128dim, 16V头×128dim, conv_kernel=4
  max_position_embeddings: 262144 (256K)
  含 vision encoder（多模态）
```

## 2. KV cache 计算（决定性差异）

| 部分 | 计算 | 结果 |
|:-----|:-----|:-----|
| 全注意力层(6层) | 2×6×2×256×2B | **12KB/token**（随序列增长） |
| 线性注意力层(18层) | 16×128×128×4B×18 | **固定 18MB**（不随序列增长） |

对比: Qwen2.5-3B 传统 144KB/token → **12 倍差距**

## 3. 4G 显存预算（权重 2.74GB 实测 + 运行时 250MB）

| 上下文 | KV | 总占用 | 判断 |
|:------:|:--:|:------:|:----:|
| 8192 | 96MB | 3.17GB | ✅ |
| 16384 | 192MB | 3.27GB | ✅ |
| 32768 | 384MB | 3.46GB | ✅ |
| 49152 | 576MB | 3.65GB | ⚠️ |
| 65536 | 768MB | 3.84GB | ⚠️ |

**推荐 num_ctx=32768**（安全甜点），上限 49152

## 4. 启动模板

### 交互式
```bash
ollama run qwen3.5:2b --verbose --num-ctx 32768 --num-gpu 24 --num-predict 1024 --temperature 0.3 --top-p 0.9 --keepalive 30m
```

### Modelfile 固化（API 也生效）
```dockerfile
FROM qwen3.5:2b
PARAMETER num_ctx 32768
PARAMETER num_gpu 24
PARAMETER num_predict 1024
PARAMETER num_keep 256
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.1
```
```bash
ollama create qwen3.5:2b-ctx32k -f ~/Modelfile-qwen35-2b
```

### CowAgent
```bash
export OLLAMA_CONTEXT_LENGTH=32768 && ollama serve
# MODEL=qwen3.5:2b-ctx32k, agent_max_context_tokens ≤ 28000
```

## 5. 注意事项

- num_gpu=24 为上限，OOM 按 24→16→8 递减
- 2B 模型建议关闭 thinking（慢且质量差）
- 多模态 vision encoder 占部分权重，纯文本场景无需额外显存
- DeltaNet 线性注意力计算量低，1050 预期 ≥5 tok/s（实测验证）

---

## Changelog

| 日期 | 变更 |
|:-----|:-----|
| 2026-08-16 | 初版：Qwen3.5-2B 混合架构实测 + KV 计算 + 4G 显存 32K 上下文模板 |
