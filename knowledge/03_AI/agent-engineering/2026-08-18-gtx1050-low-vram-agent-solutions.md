# GTX 1050（4GB 显存）上的 AI Agent 方案全景调研

> **版本**: v1.1（v1.0 为 2GB 基线，本次按用户实机 4GB 刷新显存账本/模型矩阵/推荐配置）
> **日期**: 2026-08-18
> **核心问题**: GTX 1050（Pascal 架构，4GB GDDR5，compute capability 6.1）这种 2016 年的入门级老卡上，能跑什么 AI Agent 方案？本地推理的物理边界在哪？哪些方案"方便使用"？
> **概要**: 本文从 GTX 1050 的硬件能力边界出发，用第一性原理（显存账本 + 带宽账本）推算出 **4GB 显存**下本地推理的物理上限（**≤4B 模型全 GPU**、7B 需 -ngl 混合或低量化），确认软件栈现状（Ollama 官方支持 CC 6.1、llama.cpp CUDA arch 61 仍默认编译、CUDA 13 起 Pascal 被移除），并对本地全栈 / 混合 / 纯云端三大类 20+ 个 Agent 方案做对比。结论：**GTX 1050 4GB 上"能用且方便"的本地 Agent = Ollama/llama.cpp + Qwen3-4B（或 Qwen2.5-3B/Qwen3-1.7B）+ Open WebUI/Dify/smolagents；3-4B 模型全 GPU 运行使 tool-calling 可靠性较 2GB 版显著提升，复杂 Agent 任务仍建议混合方案（本地小模型做隐私/离线任务，云端 API 做复杂任务）**。
> **关键词**: GTX 1050 · 4GB 显存 · Pascal · 低显存推理 · Ollama · llama.cpp · Qwen3-4B · Agent 框架 · Open WebUI · smolagents · tool calling
> **适用对象**: 旧显卡/老机器二次利用者、低资源边缘部署者、本地 Agent 选型工程师
> **关联**: [8GB 显存能否跑 8B 模型深度分析](../llm-techniques-principles/2026-08-11-8gb-vram-8b-model-feasibility.md) · [llama.cpp 量化详解](../llm-techniques-principles/2026-06-26-llamacpp-quantization-local-llm.md) · [编码 Agent 全景对比](2026-08-17-coding-agent-landscape-comparison.md) · [量化检测分析](../llm-techniques-principles/2026-08-11-quantization-model-detection.md)

---

## 目录

- [1. 结论先行（30 秒版）](#1-结论先行30-秒版)
- [2. GTX 1050 硬件能力边界](#2-gtx-1050-硬件能力边界)
- [3. 软件栈支持现状（2026-08 实测确认）](#3-软件栈支持现状2026-08-实测确认)
- [4. 显存账本：4GB 到底能跑什么](#4-显存账本4gb-到底能跑什么)
- [5. 推理引擎选型](#5-推理引擎选型)
- [6. Agent 方案全景（MECE 分层）](#6-agent-方案全景mece-分层)
- [7. 方案对比矩阵](#7-方案对比矩阵)
- [8. 推荐配置与部署指南](#8-推荐配置与部署指南)
- [9. 性能预期与局限](#9-性能预期与局限)
- [10. 决策树](#10-决策树)
- [11. 参考文献](#11-参考文献)
- [Changelog](#changelog)

---

## 1. 结论先行（30 秒版）

> **一句话总结**：GTX 1050 的 **4GB 显存**物理上可以全 GPU 跑 **≤4B 量化模型**（Q4 精度），**"能用且方便"的本地 Agent 方案存在且成熟**——Ollama 官方明确支持该卡（compute capability 6.1），配合 Qwen3-4B / Qwen2.5-3B / Qwen3-1.7B 可跑起 Open WebUI、Dify、smolagents 等主流 Agent 栈。**4GB 相对 2GB 的关键跃迁是 3-4B 级模型可全 GPU 运行，tool-calling 可靠性显著提升**；但 4B 弱模型写代码能力仍不足，**编码类 Agent 任务建议走混合或纯云端方案**。

**7 条关键结论**：

1. **硬件天花板明确**：GTX 1050 = Pascal GP107、640 CUDA 核心、**4GB GDDR5（本文按用户实机 4GB 版，非公版/OEM 常见配置；官方 2GB 版结论见 v1.0）、带宽 112 GB/s、compute capability 6.1、无 Tensor Core** [来源: TechPowerUp GPU 数据库（2026-08 抓取被 bot 拦截，规格为公开常识，二级可信）+ 用户实机确认]。
2. **软件栈"意外地"支持良好**：Ollama 官方硬件支持文档明确列出 GTX 1050（CC 6.1 在支持区间），CC 5.0-6.2 需 **NVIDIA 驱动 570+** [来源: docs.ollama.com/gpu，2026-08-18 直连 ✅]；llama.cpp 非 native 构建（CUDA < 13）默认编译 arch 列表**包含 61-virtual** [来源: llama.cpp ggml/src/ggml-cuda/CMakeLists.txt，2026-08-18 直连 ✅]。
3. **CUDA 13 是分水岭**：llama.cpp 源码 `if (CUDAToolkit_VERSION VERSION_LESS "13")` 分支才追加 50/61/70 架构 → **CUDA 13+ 不再编译 Pascal 支持**；因此必须用 CUDA 12.x 工具链或直接用 Ollama 预编译包（其内部 CUDA 库覆盖 CC 5.0+）[来源: llama.cpp CMakeLists.txt 源码注释 + Ollama 官方支持表 ✅]。
4. **显存账本（第一性推导）**：4GB = 4096 MiB，扣除 llama.cpp CUDA context（~200-400 MiB）后可用 **~3.7-3.9 GiB** → **≤4B 级 Q4_K_M（~2.5GB）可全 GPU 运行且余量支持 8K+ 上下文**；**7B 级（~4.7GB）必须 -ngl 部分 CPU offload、低量化（Q3/Q2）或纯 CPU**（公式与方法论同 8GB 显存文档 [来源: knowledge/03_AI/llm-techniques-principles/2026-08-11-8gb-vram-8b-model-feasibility.md]）。
5. **速度可接受但非流畅**：decode 速度 ≈ 带宽/权重字节 → 3-4B Q4 理论上限 ~45-57 tok/s，Pascal 无 Tensor Core + 走 MMQ kernel，实际估 **20-45 tok/s**（聊天级流畅；标注：无实卡实测，理论推导 + 社区量级校准 ±50%）[来源: 第一性推导 + llama.cpp build 文档 MMQ 说明]。
6. **Agent 方案分三层**：本地全栈（Ollama+Open WebUI/Dify/smolagents 等）、混合（本地小模型 + 云 API）、纯云端。**GTX 1050 作为"AI 终端"的现实最优解是混合**——本地 3-4B 模型做隐私敏感/离线/中等复杂度 agent 任务，云端 API 做复杂推理。
7. **弱模型仍是 Agent 的真正瓶颈**：3-4B 模型 tool-calling 可靠性明显优于 1.5B（Qwen3 系列原生支持且较好），但多轮工具调用仍会放大错误率 → **优先选择代码型 Agent 风格（如 smolagents CodeAgent，比 JSON tool-calling 少 30% LLM 调用 [来源: smolagents GitHub README]）**，或减少工具数量、增加人工确认点。

**领导快速判断表**：

| 决策问题 | 30 秒判断 | 依据 |
|:---------|:----------|:-----|
| GTX 1050 能跑本地 LLM 吗？ | ✅ 能，且工具链成熟（Ollama/llama.cpp 官方支持） | §3 |
| 能全 GPU 跑多大模型？ | ≤4B（Q4 量化）；7B 需 -ngl offload 或低量化 | §4 |
| 推荐模型？ | **Qwen3-4B**（tool calling + thinking 兼备）或 Qwen2.5-3B（稳） | §4.3 |
| 能跑正经 Agent 框架吗？ | ✅ Open WebUI / Dify / smolagents 均可接 Ollama | §6 |
| 能当编码 Agent 用吗？ | ❌ 不推荐——4B 写代码能力仍弱，编码走云 API（DeepSeek 等） | §6.3 |
| 最方便的方案？ | Ollama（一键安装）+ Open WebUI（Docker 一条命令） | §8 |
| 性能瓶颈在哪？ | 不是显卡是**模型能力**（tool-calling 可靠性） | §9 |

---

## 2. GTX 1050 硬件能力边界

### 2.1 规格定位（2016 年入门卡，至今仍是存量最多的老卡之一）

| 规格 | GTX 1050 (4GB 版) | GTX 1050 (2GB 版) | GTX 1050 Ti（对比） | 说明 |
|:-----|:--------:|:--------:|:-------------------:|:-----|
| 架构 | **Pascal GP107-300** | Pascal GP107-300 | Pascal GP107-400 | 14nm 三星 |
| CUDA 核心 | 640 | 640 | 768 | |
| 显存 | **4GB GDDR5** | 2GB GDDR5 | 4GB GDDR5 | 1050 另有 3GB 版；4GB 常见于 OEM/后期非公版 |
| 显存位宽 | 128-bit | 128-bit | 128-bit | |
| **显存带宽** | **112 GB/s** | 112 GB/s | 112 GB/s | 三卡相同 |
| **Compute Capability** | **6.1** | 6.1 | 6.1 | 决定 CUDA 兼容性 |
| Tensor Core | ❌ 无 | ❌ 无 | ❌ 无 | 纯 CUDA core 计算 |
| 光追/NVLink | ❌ | ❌ | ❌ | |
| TDP | 75W（免外接供电） | 75W | 75W | 老机器升级友好 |
| 发布 | 2016-10 | 2016-10 | 2016-10 | |

> **注**：显存位宽与带宽相同 → 4GB 版相对 2GB 版**只扩容容量（装得下更大模型），速度不变（112 GB/s）**。若实机为 GTX 1050 Ti 4GB，则多 128 CUDA cores（+20% 计算），显存相同，本文章节 4-10 结论同样适用。

[来源: TechPowerUp GPU 数据库 GTX 1050 条目，2026-08 抓取遇 bot 拦截；规格为多源一致的公开常识，标注二级可信。]

### 2.2 对 LLM 推理的意义（第一性推导）

- **显存 4GB = 容量约束**：决定"装得下什么模型"——可全 GPU 跑 Q4 量化后 ≤4B 的权重（详见 §4 账本），这是相对 2GB 版（≤1.5-2B）最大的能力跃迁。
- **带宽 112 GB/s = 速度约束**：decode 阶段每生成 1 token 需完整读一遍权重（memory-bound），`decode_tok/s ≈ 有效带宽 / 权重字节` [来源: 公式同 8GB 显存文档方法论]。作为对比，RTX 5060 为 448 GB/s（+300%）、RTX 3060 为 360 GB/s [来源: 知识库 2026-08-11-8gb-vram-8b-model-feasibility.md §7.5]。**容量翻倍但速度不变 → 4GB 版跑更大模型时 tok/s 反而下降**（权重更大）。
- **无 Tensor Core = 计算效率约束**：Pascal 无 int8/int4 Tensor Core，量化矩阵乘只能走 CUDA core 上的 MMQ（matrix-multiplication-quantized）kernel，llama.cpp 中 `GGML_CUDA_FORCE_MMQ` 正是为这类卡设计（V100/CDNA/RDNA3+ 同理）[来源: llama.cpp build.md 性能调优表 ✅]。
- **Vulkan 1.0+ 支持**：Pascal 驱动支持 Vulkan，llama.cpp/Ollama 的 Vulkan backend 可作为 CUDA 之外的备选（如 CUDA 工具链无法安装时）[来源: llama.cpp build.md Vulkan 章节 ✅]。

> **定位总结**：GTX 1050 4GB 是"**能跑 4B 级模型推理的嵌入式 GPU**"，不是"能跑 Agent 大脑的算力"。它的价值 = 让 1-4B 模型离线/私密地跑在本地，而 Agent 的"智力"上限由模型决定，不由框架决定。

---

## 3. 软件栈支持现状（2026-08 实测确认）

> 本节全部为 2026-08-18 直连验证的一手事实（✅ = 官方文档直连确认）。**显存容量不影响软件栈结论**（CC 6.1 相同），与 v1.0 一致。

### 3.1 Ollama：官方支持 GTX 1050 ✅

Ollama 官方硬件支持文档（docs.ollama.com/gpu）明确：

- **支持 compute capability 5.0+ 的 NVIDIA GPU**；CC 5.0 到 6.2（Maxwell/Pascal）**需要驱动 570 或更新**。
- CC 6.1 列表明确包含 **GTX 1050 / GTX 1050 Ti / GTX 1060 / GTX 1070 等 Pascal 全家**。
- Ollama 同时提供 **Vulkan backend**（Windows/Linux 默认安装，CC 5.0-6.2 老卡的另一条通路）。
- 老卡显存调度：Ollama 会按 `num_gpu`/`OLLAMA_*` 环境变量控制 GPU 层数，显存不足时可自动降低 GPU offload 层数（跑不了的部分走 CPU）[来源: docs.ollama.com/gpu + Ollama FAQ，2026-08-18 直连 ✅]。

> 这意味着：**Windows/Linux 上一键安装 Ollama，GTX 1050 直接可用，无需编译任何东西**——这是"方便使用"的第一前提。

### 3.2 llama.cpp：CUDA arch 61 仍被默认编译 ✅（但仅限 CUDA < 13）

llama.cpp `ggml/src/ggml-cuda/CMakeLists.txt`（2026-08-18 直连源码）关键逻辑：

```text
# non-native build + CUDA Toolkit < 13: default arch list
#   50-virtual 61-virtual 70-virtual 75-virtual 80-virtual 86-real (+89/90/120 by version)
# 61 == Pascal, __dp4a instruction (per-byte integer dot product)
# if (CUDAToolkit_VERSION VERSION_LESS "13")  <- only CUDA < 13 appends 50/61/70
```

推论（代码直证）：

1. **CUDA 12.x 工具链编译 llama.cpp，默认就支持 GTX 1050**（61-virtual = PTX + 首次运行 JIT），无需手动指定 arch；
2. **CUDA 13+ 不再编译 Maxwell/Pascal/Volta**——这是 NVIDIA 官方淘汰政策在工程层的落地（CUDA 12.9 为最后支持 Pascal 的版本，CUDA 13.0 移除 [来源: llama.cpp 源码注释，间接佐证 NVIDIA 淘汰政策，官方公告未直连标注待验证]）；
3. 手动指定 `-DCMAKE_CUDA_ARCHITECTURES="61"` 可显式覆盖（若 nvcc 检测不到显卡时）[来源: llama.cpp build.md ✅]。

其他已确认能力（llama.cpp README/build.md 直连）：

- **CPU+GPU 混合推理**：`-ngl N` 把前 N 层放 GPU，其余走 CPU——4GB 卡跑 7B 模型的唯一正路；
- **Unified Memory**：Linux 设 `GGML_CUDA_ENABLE_UNIFIED_MEMORY=1`，Windows 在 NVIDIA 控制面板开 System Memory Fallback，显存溢出时 swap 到系统 RAM 而非崩溃（速度骤降但保命）[来源: build.md ✅]；
- **llama-server 提供 OpenAI 兼容 API**：`llama serve -hf <model>` 一条命令起服务，任何 Agent 框架可直接对接 [来源: README ✅]。

### 3.3 其他推理栈的兼容性（评估）

| 推理栈 | Pascal (CC 6.1) 支持 | 说明 |
|:-------|:--------------------:|:-----|
| **vLLM** | ❌ 基本不支持 | 现代 vLLM 要求 CC 7.0+（Turing/V100 起），Pascal 不在支持列表；且 vLLM 默认 CUDA graph 预分配显存策略对 4GB 卡也是负担 [来源: 社区共识，标注待验证] |
| **PyTorch + transformers** | ⚠️ 可用但受限 | CUDA 12.x 的 torch 轮子仍含 sm_61；但 transformers 推理内存开销（CUDA context ~500MB+、激活大）比 llama.cpp 高，4GB 卡上跑 3B 级可尝试、4B 紧张；且需 Python 环境，不如 llama.cpp 直接 [来源: 社区经验] |
| **ONNX Runtime (DML/CUDA EP)** | ⚠️ 可用 | DirectML 会自动溢出到共享内存（慢），CUDA EP 依赖 onnxruntime 构建是否含 sm_61 [来源: 社区经验，标注待验证] |
| **ExLlamaV2** | ❌ | 面向 Turing+，Pascal 不支持 |
| **TensorRT-LLM** | ❌ | 最低 CC 7.0+，且主要面向数据中心卡 |
| **llama.cpp / Ollama / LM Studio** | ✅ | 本文主线 |

> **关键判断**：4GB 老卡的推理栈选择**收敛到 llama.cpp 系（Ollama/LM Studio/llama-server）**——它同时满足"支持 CC 6.1"、"显存开销最小"（CUDA context 比 PyTorch 低一个量级）、"CPU offload 最成熟"三个条件。其他栈要么不支持，要么开销大到浪费显存。

---

## 4. 显存账本：4GB 到底能跑什么

### 4.1 预算与公式

```text
total budget:    4096 MiB (4GB GDDR5)
fixed overhead:  CUDA context + driver mapping ~= 200-400 MiB (llama.cpp CUDA backend)
available:       ~3.7-3.9 GiB
model footprint = weights (GGUF file size) + KV Cache + runtime/activations
KV bytes/token  = 2 x n_layers x n_kv_heads x head_dim x dtype_bytes (FP16)
```

[来源: KV 公式同知识库 2026-08-11-8gb-vram-8b-model-feasibility.md §3（NVIDIA 官方口径）；llama.cpp CUDA context 量级为社区经验值 ±100MiB]

### 4.2 模型 × 显存可行性矩阵（Q4_K_M 口径，4GB 版）

| 模型（Q4_K_M 近似大小） | 权重 | 全 GPU 可行？ | **4GB 卡结论**（vs 2GB 版） |
|:---|:---:|:---:|:-----|
| Qwen2.5-0.5B（~0.4GB） | 0.4 | ✅ 极宽松 | 全 GPU，余量巨大（2GB 版同） |
| Qwen3-0.6B / Qwen2.5-1.5B / Llama-3.2-1B（~0.8-1.1GB） | 0.8-1.1 | ✅ 宽松 | 全 GPU + 32K ctx 无压力（2GB 版甜点区） |
| Qwen3-1.7B / DeepSeek-R1-Distill-Qwen-1.5B（~1.1-1.2GB） | 1.1-1.2 | ✅ 可行 | 全 GPU + 32K ctx 轻松（2GB 版可行） |
| Gemma-2-2B / Gemma-3-1B（~1.4-1.6GB） | 1.4-1.6 | ✅ 可行 | 全 GPU + 16K+ ctx（2GB 版勉强） |
| **Qwen2.5-3B / Llama-3.2-3B（~1.9-2.0GB）** | 1.9-2.0 | ✅ **可行** | **全 GPU + 8-16K ctx**（2GB 版需 -ngl offload） |
| **Qwen3-4B / Phi-3.5-mini（~2.5GB）** | 2.5 | ✅ **可行** | **全 GPU + 8K ctx**（2GB 版只能纯 CPU）——**4GB 最大跃迁点** |
| Qwen2.5-7B / Llama-3.1-8B（~4.7-5.0GB） | 4.7-5.0 | ❌ 超 4GB | **-ngl 28-30 层 GPU + 余层 CPU 混合**；或 Q3_K_M/Q2_K 尝试全 GPU（需实测确认）；或纯 CPU（2-5 tok/s） |

（Q4_K_M 近似大小来自各模型 HF 官方 GGUF 仓库文件大小量级，精确值以实际文件为准；7B=4.68GB 为官方文件实证 [来源: 知识库 8GB 显存文档 §2.2]）

> **关键洞察（4GB vs 2GB 的分水岭）**：2GB 卡的甜点区是 1-1.7B；**4GB 卡把甜点区整体上移到 1.7B-4B**——3B/4B 级模型不仅"装得下"，还保留了 8-16K 上下文余量。而 3-4B 是"具备基本 tool-calling/指令遵循/推理能力"的门槛级尺寸，Agent 任务的实际可用性比 1.5B 上一个台阶。**推荐平衡点：Qwen3-4B（Q4, ~2.5GB，能力最强）或 Qwen2.5-3B（~2.0GB，余量更大）**。

### 4.3 模型能力评估（Agent 场景选型，4GB 版）

| 模型 | 大小(Q4) | 4GB 运行方式 | tool calling | 推理/思考 | Agent 适用性 | 备注 |
|:-----|:---:|:---:|:---:|:---:|:---:|:-----|
| **Qwen3-4B** | ~2.5GB | 全 GPU + 8K ctx | ✅ 原生（4B 级更稳） | ✅ 原生 thinking | ★★★ **首选** | 2025-04 发布，Qwen3 全系支持 tool calling 与 thinking；4B 级指令遵循/工具调用显著优于 1.5B [来源: Qwen 官方模型卡] |
| **Qwen2.5-3B** | ~2.0GB | 全 GPU + 16K ctx | ✅ 原生 | ❌ | ★★★ 最稳 | 社区验证充分的 3B tool-calling 模型，余量大 |
| **Qwen3-1.7B** | ~1.1GB | 全 GPU + 32K ctx | ✅ 原生 | ✅ thinking | ★★ 轻快 | 速度最快的有 thinking 模型 |
| Llama-3.2-3B | 2.0 | 全 GPU | ✅ 支持 | ❌ | ★★ | tool calling 支持一般 |
| Gemma-2-2B / Gemma-3-1B | 1.5/0.9 | 全 GPU | ⚠️ 一般 | ❌ | ★★ | 对话质量好但工具调用支持弱 |
| DeepSeek-R1-Distill-Qwen-1.5B | ~1.1GB | 全 GPU | ⚠️ 弱 | ✅ R1 推理风格 | ★ 特定场景 | 推理/数学强，agent 工具调用弱 |
| **Qwen2.5-7B（-ngl 混合）** | 4.7GB | **-ngl 28-30 混合** | ✅ 强 | ❌ | ★★★ 能力最强 | 牺牲速度换能力；或 Q3/Q2 低量化全 GPU（质量折损） |

[来源: 模型 tool-calling 支持为各模型官方发布说明 + 社区基准常识，标注二级可信；"★★★ 首选"为本文综合判断]

> **选型结论**：4GB 下**首选 Qwen3-4B**——它同时满足"全 GPU 可跑"与"tool-calling 可靠"两个 Agent 硬条件，且有 thinking 模式；追求余量/上下文更长选 Qwen2.5-3B；需要 7B 级能力可接受 8-15 tok/s 则用 -ngl 混合跑 Qwen2.5-7B。

---

## 5. 推理引擎选型

| 引擎 | 安装难度 | CC 6.1 支持 | 4GB 适配 | 特点 |
|:-----|:---:|:---:|:---:|:-----|
| **Ollama** | ★ 一键（官方安装器） | ✅ 官方支持 | ✅ 自动层 offload | 最方便；OpenAI 兼容 API；tool calling 支持；模型库一键拉取 |
| **llama.cpp (llama-server)** | ★★ 编译或下 release | ✅（CUDA<13） | ✅ -ngl 精确控制 | 最灵活；Unified Memory 保命；纯 C++ 零依赖 |
| LM Studio | ★ 一键（GUI） | ✅ | ✅ | Windows 桌面最友好；图形化拖拽 |
| Ollama-Vulkan / llama.cpp-Vulkan | ★★ | ✅ | ✅ | CUDA 装不上的备选；性能略低于 CUDA |
| 纯 CPU（llama.cpp AVX2） | ★ | ✅ N/A | ✅ 完全不占 GPU | 7B 模型的出路之一；速度 2-12 tok/s |

> **引擎结论**：**默认 Ollama**（最省事、官方支持 1050）；需要精确显存控制/Unified Memory/离线二进制时用 **llama.cpp**；Windows 纯小白用 **LM Studio**。三者底层同源（llama.cpp），Agent 侧看到的都是 **OpenAI 兼容 API（http://localhost:11434/v1 或 :8080/v1）**——这是所有 Agent 框架能"方便接入"的根本原因。

---

## 6. Agent 方案全景（MECE 分层）

> 分类原则：按"模型跑在哪"分三层（本地 / 混合 / 云端），层内按"形态"分子类。所有框架均以 OpenAI 兼容 API 为接入标准，故与推理引擎解耦。**框架选型与 2GB 版结论一致，差异仅在"本地模型可用性"上——4GB 下 3-4B 模型使 A 层方案的实际体验明显提升**。

### 6.1 A 层：本地全栈（离线、隐私优先）——GTX 1050 直接驱动

#### A1. 平台型（带 UI 的 Agent 平台，开箱即用）

| 方案 | Stars(约) | 形态 | 与 Ollama 集成 | Agent 能力 | 4GB 卡适配 |
|:-----|:---:|:-----|:---:|:---|:---|
| **Open WebUI** | 149k | Web 应用（Docker/pip） | 原生 | 模型包装成 Agent（自定义指令+工具+知识）、MCP/OpenAPI 工具、RAG、多模型、记忆 [来源: GitHub README 直连 ✅] | ✅ 前端很轻，推理全在 Ollama |
| **Dify** | 70k+ | 自托管 LLMOps 平台 | 原生 | 可视化 Agent 工作流、工具调用、RAG、编排复杂 pipeline | ⚠️ 平台较重（RAM 2GB+），适合有 RAM 的机器 |
| **LobeChat** | 50k+ | Web 应用 | 原生 | 对话 Agent、插件市场、多模型路由 | ✅ 轻量 |
| **AnythingLLM** | 30k+ | 桌面应用 | 原生 | RAG + 简单 Agent + 工作区管理 | ✅ 桌面版最省心 |
| **Jan / GPT4All** | 40k/25k+ | 桌面应用 | 自带引擎 | 本地模型 + 基础 Agent 交互 | ✅ 自带引擎可跑 3-4B，Agent 能力弱 |

> **A1 首选 = Open WebUI**：149k★ 的事实标准，支持 Ollama + OpenAI 兼容 API（可同时接本地和云端）、MCP 工具、RAG、把任意模型包装成 Agent [来源: GitHub README 2026-08-18 直连 ✅]。Docker 一条命令起服务，浏览器访问，显卡完全无压力（推理在 Ollama 侧）。**4GB 下接 Qwen3-4B，Agent 任务（工具调用/多轮）的完成率比 2GB 版（1.5B）明显更稳**。

#### A2. 框架型（代码写 Agent，嵌入自己的应用）

| 方案 | Stars(约) | 模型接入 | 风格 | 4GB 卡适配要点 |
|:-----|:---:|:---|:---|:---|
| **smolagents** (HF) | 29k | Ollama/LiteLLM/OpenAI 兼容 | **CodeAgent：动作=Python 代码** | ★★★ **首选**——比 JSON tool-calling 少 30% LLM 调用 [来源: README 直连 ✅]，弱模型错误累积更少；本地模型官方支持 |
| LangChain / LangGraph | 100k+ | Ollama 官方集成 | 链/图编排 | ★★ 功能全但抽象重，4B 模型下仍易"过度工程" |
| LlamaIndex | 40k+ | Ollama 集成 | RAG 优先 | ★★ RAG agent 场景合适 |
| PydanticAI | 15k+ | OpenAI 兼容 | 类型安全 Agent | ★★ 轻量、结构化输出 |
| Agno (原 Phidata) | 25k+ | Ollama 支持 | 多 Agent 团队 | ★★ |
| CrewAI | 30k+ | Ollama 支持 | 角色协作多 Agent | ★ 多 Agent 对 4B 模型负担重 |
| AG2 (原 AutoGen) | 40k+ | Ollama 支持 | 对话式多 Agent | ★ 多 Agent 会话对弱模型开销大 |

> **A2 首选 = smolagents CodeAgent**：Hugging Face 官方出品，**"agent 用代码思考"**（CodeAgent 把动作写成 Python 代码执行），实测比 JSON tool-calling 少 30% 步骤/LLM 调用 [来源: README 直连 ✅]——这对 4B 弱模型同样关键：**LLM 调用次数越少，错误累积越少**。接入本地模型只需 `OpenAIModel(api_base="http://localhost:11434/v1")` 或 `TransformersModel`。

#### A3. 编码 Agent（代码补全/编辑）

| 方案 | 形态 | 本地模型适配 | 4GB 卡判定 |
|:-----|:-----|:---|:---|
| Cline / Roo Code | VS Code 插件 | 支持 Ollama/OpenAI 兼容 | ❌ **不推荐完整编码 Agent**——4B 模型代码生成质量仍差，多文件编辑/复杂工具调用不现实；简单补全可试 |
| Continue.dev | VS Code 插件 | Ollama 原生 | ⚠️ **补全可用**（Qwen3-4B 做单文件补全/解释可以），整体体验仍逊云 API |
| Aider | CLI | OpenAI 兼容端点 | ⚠️ 同上 |
| OpenHands | 平台 | 需强模型（7B+） | ❌ 4GB 卡无法支撑（-ngl 混合 7B 也吃力） |

> **编码 Agent 结论**：**本地 ≤4B 模型不适合完整编码 Agent**（代码能力是 7B+ 的分水岭 [来源: 知识库 2026-08-17-coding-agent-landscape-comparison.md]）。GTX 1050 机器上要编码 Agent，正确姿势 = **云 API（DeepSeek/Qwen 等便宜 API）+ Cline/Continue**，显卡只做显示。Qwen3-4B 可做代码补全/解释类轻任务。

#### A4. 自动化工作流

| 方案 | 形态 | 集成 | 说明 |
|:-----|:-----|:---|:---|
| n8n | 自托管工作流 | Ollama 节点 | 可视化编排"LLM+工具"流程，可做简单 Agent 链 |
| Home Assistant | 智能家居 | Ollama 集成 | 本地语音/自动化助手（4B 模型意图识别更准） |
| Node-RED | 流程编排 | Ollama 节点 | 轻量备选 |

#### A5. MCP（Model Context Protocol）生态

- MCP 是 2025-2026 Agent 工具接入的事实标准（Open WebUI、Cline、Claude 等全支持）。
- **GTX 1050 上运行 MCP 的正确姿势**：本地跑 **MCP server**（工具执行/文件访问/系统控制，纯 CPU 开销极小），模型 = 本地 3-4B（中等工具调度）或云端 API（复杂任务）[来源: MCP 生态常识 + Open WebUI MCP 支持 ✅]。
- 这是"老机器当 Agent 外设"的最佳路径：**显卡管推理（3-4B 够做工具调度），MCP server 管执行**。

### 6.2 B 层：混合方案（本地 + 云端）——GTX 1050 的现实最优解

| 模式 | 本地角色 | 云端角色 | 典型实现 |
|:-----|:---------|:---------|:-----|
| B1 本地 RAG 检索 + 云推理 | 3-4B 模型 + embedding 做本地文档检索/摘要 | 大模型做综合推理 | Open WebUI 双 provider（本地 Ollama + 云 API 并存）|
| B2 本地意图路由 | 1.5-4B 分类意图/预过滤 | 大模型只处理"值得"的任务 | smolagents/LangGraph 路由节点 |
| B3 云主脑 + 本地工具 | 本地工具执行（MCP/脚本，CPU 即可）| Agent 主脑（规划/工具调用决策） | Cline + DeepSeek API；Dify + 云模型 |
| B4 本地影子模式 | 3-4B 全离线兜底 | 主用 | 断网/隐私场景自动切换 |

> **为什么混合是 GTX 1050 的现实最优解**：4B 模型的"智力"天花板（复杂推理/规划/长链工具调用）仍低于云 API；但本地 3-4B 在**延迟敏感（几十 ms 级响应）、隐私敏感（文档不出机）、成本敏感（免费）**三类任务上反而更优，且比 1.5B 能扛更复杂的本地任务。混合 = 用 1050 的算力干它能干的事，把干不了的交给云。

### 6.3 C 层：纯云端（GTX 1050 不参与推理）

- 任何 Agent 框架（Open WebUI/Dify/smolagents/LangGraph/Cline/OpenHands）+ 任意云 API（DeepSeek、Qwen、OpenRouter、OpenAI...）。
- GTX 1050 机器只当"瘦客户端"，显卡性能无关紧要。
- **这是"最方便、能力最强"的方案**（零硬件门槛），唯一代价 = 网络 + API 费用。DeepSeek/Qwen 等国产 API 价格已低至可忽略（R1/Qwen 系列 $0.1-1/M token 量级 [来源: 各厂商定价页，标注二级]）。

---

## 7. 方案对比矩阵

| 维度 | A1 Open WebUI | A2 smolagents | A1 Dify | A3 Cline+云API | B 混合 | C 纯云端 |
|:-----|:---:|:---:|:---:|:---:|:---:|:---:|
| 离线/隐私 | ✅ 全离线 | ✅ 全离线 | ✅ | ⚠️ 需网络 | 部分 | ❌ 需网络 |
| 安装难度 | ★（Docker 一条命令） | ★★（pip） | ★★（Docker Compose） | ★★ | ★★ | ★ |
| 资源占用 | 低（Web 前端） | 极低 | 中（RAM 2GB+） | 低 | 低 | 最低 |
| Agent 能力上限 | 中-高（工具+MCP+RAG） | 中-高（代码 Agent） | 高（可视化编排） | 高（云模型） | 高 | 最高 |
| **4B 本地模型体验** | ★★★ 可用 | ★★★ 可用 | ★★ 可用 | ★（弱模型） | ★★★ | N/A |
| 费用 | 0 | 0 | 0 | 云 API 费 | 少量 | 云 API 费 |
| 适合场景 | 个人聊天+知识库+轻 Agent | 脚本化/嵌入式 Agent | 业务工作流编排 | 编码 | 隐私+能力平衡 | 追求最强能力 |

> 注：★=差 ★★=中 ★★★=好。Open WebUI 与 smolagents 可组合使用（UI 层 + 框架层）。4GB 版"1.5B 本地模型体验"列整体上移为"4B 本地模型体验"（★★→★★★ 为主）。

---

## 8. 推荐配置与部署指南

### 8.1 默认推荐（最方便，30 分钟跑起来）

```bash
# 1. Install Ollama (one-click official installer, auto-detects GTX 1050, driver >= 570)
#    Windows: download installer; Linux: curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3:4b          # 首选：4B 全 GPU + tool calling + thinking
#    alternative: qwen2.5:3b (余量更大/更稳) / qwen3:1.7b (最快) / qwen2.5:7b (-ngl 混合)

# 2. Start Open WebUI (one Docker command, or pip install open-webui)
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data --name open-webui --restart always \
  ghcr.io/open-webui/open-webui:main
# open http://localhost:3000 -> select qwen3:4b in settings
# optional: attach tools/MCP to the model in Open WebUI to make it an Agent

# 3. Verify GPU acceleration
ollama ps   # expect qwen3:4b with PROCESSOR=GPU (4GB 下应全 GPU)
```

### 8.2 代码级 Agent（smolagents + 本地/云端模型）

```python
# pip install smolagents
from smolagents import CodeAgent, OpenAIModel

# local model: use Ollama's OpenAI-compatible endpoint
local_model = OpenAIModel(
    model_id="qwen3:4b",
    api_base="http://localhost:11434/v1",
    api_key="ollama",          # placeholder, Ollama does not verify
)
# cloud model: switch api_base + key to DeepSeek/Qwen seamlessly

agent = CodeAgent(tools=[], model=local_model)  # attach custom tools
agent.run("List all .md files under tmp/ sorted by mtime")
```

### 8.3 显存紧张时的 llama.cpp 直连（精确控制，7B 场景）

```bash
# 7B model: 4GB 卡需 -ngl 控制 GPU 层数（33 层总，建议 28-30 层 GPU，余层 CPU）
llama-server -m qwen2.5-7b-instruct-q4_k_m.gguf -ngl 28 -c 8192 --port 8080
#   或尝试低量化全 GPU: qwen2.5-7b-instruct-q3_k_m.gguf（~3.7GB，需实测确认）

# lifesaver (swap to RAM instead of crash on VRAM overflow):
#   Linux:   GGML_CUDA_ENABLE_UNIFIED_MEMORY=1
#   Windows: NVIDIA Control Panel -> System Memory Fallback = ON
```

### 8.4 各场景推荐组合速查（4GB 版）

| 场景 | 推荐组合 |
|:-----|:---------|
| 零基础体验本地 Agent | Ollama + **qwen3:4b** + Open WebUI（Docker） |
| 隐私敏感文档问答 | Ollama + qwen2.5:3b + Open WebUI RAG（本地 embedding，16K ctx 够长文档） |
| 开发嵌入 Agent | llama-server 或 Ollama + smolagents CodeAgent（**qwen3:4b**） |
| 业务自动化工作流 | Ollama + Dify（qwen3:4b 或云模型） |
| 编码 Agent | ❌ 不用本地模型做完整编码 → Cline/Continue + DeepSeek API；qwen3:4b 仅补全/解释 |
| 断网环境最强能力 | llama-server -ngl 28 跑 qwen2.5:7b（8-20 tok/s，或 Q3 低量化） |

---

## 9. 性能预期与局限

### 9.1 速度预期（第一性推导，无实卡实测，4GB 版）

| 配置 | 权重介质 | decode 理论上限 | 实际估计 | 体验 |
|:-----|:---|:---:|:---:|:---|
| 1.5B Q4 全 GPU | 112 GB/s 显存 | ~100 tok/s | 40-70 tok/s | 聊天流畅（人类阅读 5-10 tok/s） |
| **3B Q4 全 GPU** | 112 GB/s | ~57 tok/s | **25-45 tok/s** | 流畅（思考/工具调用可接受） |
| **4B Q4 全 GPU** | 112 GB/s | ~45 tok/s | **20-35 tok/s** | 可接受（thinking 模式偏慢） |
| 7B Q4 -ngl 28 混合 | 显存+内存 | ~24 tok/s（受 CPU 拖累） | **8-20 tok/s** | 勉强（等待感强） |
| 7B Q4 纯 CPU（AVX2） | 内存 ~20-40 GB/s | ~6 tok/s | 2-5 tok/s | 勉强（等待感强） |

> 标注：Pascal 无 Tensor Core，量化 GEMM 走 CUDA core MMQ kernel，实际效率约 50-70% 带宽利用率；以上为理论推导 + 社区基准量级，**±50% 不确定度，建议实机跑 `llama-bench` 校准**。4GB 版跑 3-4B 比 2GB 版跑 1.5B 的 tok/s 低（权重更大），但能力提升远大于速度损失。

### 9.2 能力局限（比速度更重要的约束）

1. **模型能力天花板**：3-4B 模型的推理/规划/复杂工具调用能力有限，多轮 Agent 任务（>8 步工具调用）错误率仍会上升。**实测建议：单 Agent 任务控制在 5-10 步内**（2GB 版建议 3-5 步，4GB 放宽）。
2. **上下文受限**：4GB 下 3-4B 模型建议 ≤8-16K ctx（KV 与模型权重争夺显存）；长文档 RAG 需分块。
3. **并发=0**：单模型单请求，无法多用户并发（Agent 平台的多人使用需换大显存/云端）。
4. **Tool calling 质量**：Qwen3-4B 可用且比 1.5B 稳，但偶发格式错误；生产级 Agent 建议对工具输出加 schema 校验 + 重试。
5. **编码类任务不建议本地**：4B 无法胜任完整代码 Agent（§6.3），仅补全/解释。
6. **CUDA 13 后新库兼容风险**：未来新工具链默认不再含 Pascal，需固定 CUDA 12.x 或依赖 Ollama 预编译包。

### 9.3 与 8GB 卡（RTX 5060）对比

| 维度 | GTX 1050 (4GB) | RTX 5060 (8GB) |
|:---|:---:|:---:|
| 全 GPU 模型上限 | **4B**（2GB 版为 1.5-2B） | 7B-8B（Qwen2.5-7B 32K） |
| 带宽 | 112 GB/s | 448 GB/s（+300%） |
| Tensor Core | 无 | FP4/FP16 原生 |
| Agent 可用性 | 中等 Agent（5-10 步，3-4B） | 完整 Agent + 编码（7B 级） |
| 定位 | 入门/边缘/隐私兜底 | 消费级本地 Agent 甜点 |

[来源: 5060 数据同知识库 2026-08-11-8gb-vram-8b-model-feasibility.md §7.5]

---

## 10. 决策树

```text
GTX 1050 4GB machine wants an Agent?
|
+-- Need offline/privacy? ---- yes --> Local full-stack (Layer A)
|     |                               +-- beginner/chat/light-agent -> Ollama + qwen3:4b + Open WebUI
|     |                               +-- dev/embedded/scripting   -> llama-server + smolagents (qwen3:4b)
|     |                               +-- business workflow        -> Ollama + Dify (qwen3:4b)
|     +-- no
+-- Coding agent? ---------- yes --> do NOT use local model for full coding -> Cline/Continue + DeepSeek API (Layer C)
|                                    (qwen3:4b 仅可做补全/解释类轻任务)
|
+-- Capability first, network ok? -- yes --> pure cloud (Layer C): Open WebUI/Dify + cloud API
|
+-- Both capability and privacy? ---> Hybrid (Layer B): local 3-4B for private/offline + cloud API for complex
```

---

## 11. 参考文献

[1] Ollama 官方硬件支持文档 — https://docs.ollama.com/gpu（2026-08-18 直连 ✅：CC 5.0+ 支持、CC 5.0-6.2 需驱动 570+、GTX 1050 在 CC 6.1 列表、Vulkan backend）
[2] llama.cpp GitHub README — https://github.com/ggml-org/llama.cpp（2026-08-18 直连 ✅：CUDA/Vulkan 后端、CPU+GPU 混合、llama-server OpenAI 兼容 API）
[3] llama.cpp build.md — https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md（2026-08-18 直连 ✅：CUDA arch 覆盖、GGML_CUDA_FORCE_MMQ、Unified Memory、Vulkan 构建）
[4] llama.cpp ggml-cuda CMakeLists.txt — https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-cuda/CMakeLists.txt（2026-08-18 直连源码 ✅：默认 arch 列表含 61-virtual、CUDA<13 分支、61=Pascal __dp4a 注释）
[5] Open WebUI GitHub — https://github.com/open-webui/open-webui（2026-08-18 直连 ✅：149k★、Ollama+OpenAI 兼容、Agent/MCP/RAG/工具）
[6] smolagents GitHub — https://github.com/huggingface/smolagents（2026-08-18 直连 ✅：29k★、CodeAgent 代码执行、30% fewer LLM calls、本地 transformers/ollama 支持）
[7] 知识库：8GB 显存能否跑 8B 模型深度分析 — knowledge/03_AI/llm-techniques-principles/2026-08-11-8gb-vram-8b-model-feasibility.md（KV 公式、GGUF 大小、带宽账本方法论）
[8] 知识库：llama.cpp 量化详解 — knowledge/03_AI/llm-techniques-principles/2026-06-26-llamacpp-quantization-local-llm.md（量化格式与质量）
[9] 知识库：编码 Agent 全景对比 — knowledge/03_AI/agent-engineering/2026-08-17-coding-agent-landscape-comparison.md（编码 Agent 模型要求）
[10] TechPowerUp GPU 数据库 GTX 1050 — https://www.techpowerup.com/gpu-specs/geforce-gtx-1050.c2879（2026-08 抓取遇 bot 拦截；规格为多源一致公开常识，二级可信）
[11] 用户实机确认 — GTX 1050 4GB（2026-08-18，本知识库 v1.1 刷新依据）

**数据可信度总表**：

| 数据 | 来源 | 可信度 |
|:-----|:-----|:------:|
| Ollama 支持 CC 6.1 / 驱动 570+ | docs.ollama.com/gpu 直连 | ★★★ 一手 |
| llama.cpp 默认含 61-virtual / CUDA<13 | 源码直连 | ★★★ 一手 |
| Open WebUI / smolagents 能力与 star | GitHub 直连 | ★★★ 一手 |
| GTX 1050 规格（4GB/112GB/s/CC 6.1） | TechPowerUp（bot 拦截）+ 公开常识 + 用户实机 | ★★ 二级 |
| GGUF 模型大小（3B≈2.0GB / 4B≈2.5GB / 7B=4.68GB） | HF 官方仓库量级 + 7B 实证 | ★★ 量级可信 |
| 速度估计（20-45 tok/s 等） | 第一性推导 + 社区量级 | ★ 估算（无实卡） |
| 7B Q3_K_M ~3.7GB 全 GPU 可行性 | 量化大小量级推导 | ★ 待实测验证 |
| CUDA 12.9 最后支持 Pascal | llama.cpp 源码间接佐证 | ★★ 高置信待官方公告 |

**局限声明**：本文无 GTX 1050 实卡实测，速度/显存余量基于第一性公式推导（方法与 8GB 显存文档一致），实际值受驱动、CPU 型号（AVX2/AVX512）、后台进程影响浮动；模型 tool-calling 能力评级为社区常识综合判断，非标准化评测；未覆盖的操作系统差异（Windows/Linux 驱动行为）以官方文档为准；7B 低量化（Q3/Q2）全 GPU 可行性为量级推导，建议实机验证。

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:-----|:-----|:---------|
| 2026-08-18 | v1.1 | **按用户实机 4GB 刷新**：显存账本 2048→4096 MiB；可行性矩阵 3B/4B 级升为"全 GPU 可行"（甜点区 1.7B-4B）；推荐模型 Qwen3-1.7B→**Qwen3-4B**（Qwen2.5-3B 备选）；7B 改 -ngl 混合/低量化策略；速度预期、决策树、对比矩阵、部署指南同步更新；保留 2GB 版对比（v1.0 内容见 git 历史） |
| 2026-08-18 | v1.0 | 首次创建（2GB 基线）：GTX 1050 硬件边界 + 软件栈实测确认（Ollama/llama.cpp 官方支持、CUDA 13 分水岭）+ 2GB 显存账本 + 三层 Agent 方案全景（20+ 方案）+ 对比矩阵 + 推荐配置与部署指南 |
