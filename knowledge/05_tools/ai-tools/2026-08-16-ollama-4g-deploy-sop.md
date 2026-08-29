# SOP：4G 显存 Ollama 本地大模型部署与配置（Windows）

> **类型**: SOP | **日期**: 2026-08-16 | **版本**: v1.0
> **适用**: Windows + GTX 1050 4G（Pascal，无 Tensor Core）本地推理
> **关联**: `concepts/ollama-windows-qwen3-4b.md`、`concepts/ollama-qwen35-2b-4g.md`、`concepts/ollama-local-deploy-4g.md`

---

## 0. 本 SOP 解决什么

在 4G 显存硬约束下，完成本地大模型（ollama）的：选型 → 安装 → 参数配置 → 验证 → 问题排查的**全流程标准作业**。沉淀自 2026-08-16 实际排查对话。

---

## 1. 设备与环境基线

| 项 | 值 | 说明 |
|:---|:---|:-----|
| GPU | GTX 1050 4G | Pascal 2016，**无 Tensor Core**，FP16 慢 |
| 可用显存 | 3.5-3.8GB | 系统/驱动占 0.3-0.5GB，非 4.0GB |
| OS | Windows (Administrator) | 非 Linux |
| Ollama | 0.17.5 | `ollama --version` 实测 |
| 推理速度预期 | 2-10 tok/s | 量化模型，实测为准 |

---

## 2. 显存预算第一性原理公式（所有决策的根基）

```
总显存 = 权重(模型参数) + KV Cache(上下文) + 运行时(~250MB)
权重   = 参数量 × bpp（Q4_K_M=0.56, Q8=1.05, FP16=2.0 B/param）
KV    = 2(K,V) × 层数 × KV头 × head_dim × 2B × 上下文长度
```

**决定上下文的公式**：
```
可用上下文 ≤ (可用显存 - 权重 - 250MB) ÷ KV_bytes_per_token
```

⚠️ **架构陷阱**：不同模型 KV/token 差异巨大！
- 传统全注意力（qwen3:4b）: 144KB/token → 4G 下 4096 是甜点
- DeltaNet 混合（qwen3.5:2b）: 12KB/token → 4G 下可开 32768
- **选型前必须查 config.json 确认架构，不能套用公式假设**

---

## 3. 模型选型（4G 显存决策树）

```
目标是什么？
├─ 长上下文/agent 任务（≥16K）→ qwen3.5:2b（DeltaNet，KV 1/12，num_ctx 32768）
├─ 通用聊天/轻任务 → qwen3:4b（传统，num_ctx 4096，能力更强）
├─ 最强单次推理 → 云端 API（本地 4G 物理上限）
└─ 注意：7B 模型 Q4 权重 4.1GB > 4G，直接出局
```

实测占用表（4G 可用 ≈3.8GB）：

| 模型 | 量化 | 权重 | 4096 | 8192 | 32768 |
|:-----|:----:|:----:|:----:|:----:|:-----:|
| qwen3:4b | Q4_K_M | 2.3GB | ✅3.1 | ⚠️3.7 | ❌ |
| qwen3.5:2b | Q4 | 2.7GB | ✅ | ✅ | ✅3.4 |

---

## 4. 标准配置流程（Windows）

### Step 1：确认版本
```cmd
ollama --version
```

### Step 2：选配置方式（三层体系，优先级 Modelfile > 环境变量 > /set）

**方式A：Modelfile 固化（推荐，唯一对 API/CowAgent 生效）**
```cmd
notepad %USERPROFILE%\Modelfile-qwen3-4b
```
```dockerfile
FROM qwen3:4b
PARAMETER num_ctx 4096
PARAMETER num_gpu 36
PARAMETER num_predict 1024
PARAMETER temperature 0.3
```
```cmd
ollama create qwen3:4b-ctx4k -f %USERPROFILE%\Modelfile-qwen3-4b
ollama run qwen3:4b-ctx4k
```

**方式B：环境变量（全局兜底，需重启服务）**
```cmd
setx OLLAMA_CONTEXT_LENGTH 4096
setx OLLAMA_KEEP_ALIVE 30m
taskkill /f /im ollama.exe && start "" "%LOCALAPPDATA%\Programs\Ollama\ollama app.exe"
```

**方式C：交互式 /set（仅当前会话，退出失效）**
```
>>> /set parameter num_ctx 4096
>>> /set parameter num_gpu 36
```

### Step 3：CowAgent 接入
```cmd
:: env_config 配置
OPENAI_API_BASE = http://127.0.0.1:11434/v1
OPENAI_API_KEY  = ollama
MODEL           = qwen3:4b-ctx4k
agent_max_context_tokens = 3000  （≤ num_ctx - system提示词 - 工具定义）
```

### Step 4：验证
```cmd
:: 1. 显存 <3.5GB
nvidia-smi --query-gpu=memory.used --format=csv
:: 2. 参数生效
ollama run qwen3:4b-ctx4k  →  /show  →  确认 num_ctx
:: 3. 长上下文口令测试（答得出口令=生效）
```

---

## 5. 本次排查解决的问题记录（2026-08-16）

| # | 问题 | 根因 | 解决 |
|:--|:-----|:-----|:-----|
| 1 | `ollama run qwen3:4b --num-ctx 4096` → `unknown flag: --num-ctx` | **0.6+ 已从 run 命令移除推理参数 flag**（源码 cmd.go 实测仅剩 keepalive/verbose/format/think 等） | 改用 `/set parameter` 或 Modelfile |
| 2 | `/set parameter num_ctx 4096` 退出后失效 | `/set` 写入的是**当前会话内存 opts**（源码 interactive.go 实测），不持久 | 用 Modelfile 固化（PARAMETER 机制 0.1 就有，全版本兼容） |
| 3 | `/show info` 显示 context length 262144 但跑不动 | 262144 是**模型理论窗口**，非 4G 显存可跑值 | 按 KV 公式算：qwen3:4b 实际 4096 甜点 |
| 4 | 想开 32K 上下文但 qwen3:4b 装不下 | 传统全注意力 KV=144KB/token | 换 qwen3.5:2b（DeltaNet，KV=12KB/token） |
| 5 | 模型文件大小与预期不符（2.74GB） | 含 vision encoder + 默认量化非 Q4 | 用 manifest/bf16 对比推算实际参数量 |

**核心教训**：
1. ollama CLI 版本演进快，**报 unknown flag 先查源码/文档，别猜**
2. 显存/上下文判断**必须按架构算 KV**，不能只信 /show info 的理论窗口
3. 配置持久化三选一：**Modelfile > 环境变量 > /set**（仅调试用）

---

## 6. 常见问题速查

| 问题 | 解决 |
|:-----|:-----|
| unknown flag: --num-ctx | 0.6+ 已移除，用 /set parameter 或 Modelfile |
| 设了环境变量不生效 | 重启 ollama 服务（托盘退出重开） |
| OOM / 闪退 | num_gpu 36→24→12 递减；num_ctx 4096→2048 |
| API 调不到 | 防火墙 11434 端口；`curl http://127.0.0.1:11434/api/tags` |
| agent 记不住 | agent_max_context_tokens 超 num_ctx，砍到 3000 |
| 速度 <2 tok/s | GPU 层数回退 CPU，看 --verbose 输出确认 |
| 2B 模型思考质量差 | 关闭 thinking（--think false 或 /set nothink） |

---

## 7. 参考链接

- Ollama 下载: https://ollama.com/download/windows
- 模型 config 查证: https://modelscope.cn/models/Qwen/Qwen3-4B (config.json)
- Ollama 源码: https://github.com/ollama/ollama (cmd/cmd.go, cmd/interactive.go)

---

## Changelog

| 日期 | 变更 |
|:-----|:-----|
| 2026-08-16 | 初版：4G 显存 ollama 部署全流程 SOP（选型公式+三层配置+5 项问题排查+速查表） |
