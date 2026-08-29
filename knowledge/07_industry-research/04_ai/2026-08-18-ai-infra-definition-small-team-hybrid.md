# AI Infra 定义深度辨析 × 小团队混合基础设施现状与运行支撑能力分析

> 元信息: 文件状态=已发布 | 覆盖范围=AI 基础设施定义、个人/小团队混合部署（本地 GPU + 云端 API + AI 网关）、大模型部署方式与运行支撑能力 | 版本=v1.0
> 适用范围: 小型研发团队 AI 基础设施规划 / 本地算力与云端协同 / AI 网关选型与落地
> 关联文档: [AI 网关产品对比深度分析](../04_ai/2026-08-17-ai-gateway-llm-service-comparison-deep-analysis.md)（本文件为其"组织内落地视角"的互补篇）
> **概要**: 辨析 AI Infra 三层/四层栈定义，盘点本团队 GTX1050+RTX5060+云 API 混合架构现状、AI 网关落地路线与部署成本评估。
> **关键词**: AI Infra · 小团队混合部署 · 本地推理 · AI 网关 · 量化 · 成本评估 · 算力规划

## 📑 目录

- [1. 引言与范围](#1-引言与范围)
- [2. AI Infra 定义深度辨析](#2-ai-infra-定义深度辨析)
- [3. 当前基础设施搭建现状（本团队实例）](#3-当前基础设施搭建现状本团队实例)
- [4. AI 网关的角色与落地](#4-ai-网关的角色与落地)
- [5. 大模型部署方式与运行支撑能力](#5-大模型部署方式与运行支撑能力)
- [6. 支持小型团队研发的评估](#6-支持小型团队研发的评估)
- [7. 演进路线建议（按优先级）](#7-演进路线建议按优先级)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 1. 引言与范围

### 1.1 文档目的

本文件回答三个递进问题：

1. **AI Infra 到底指什么？**——从第一性原理辨析定义，破除"AI 基础设施 = 买 GPU"的窄化理解，也破除"AI 基础设施 = 只有大厂才配谈"的虚无理解。
2. **一个小型研发团队（3-10 人）当前实际能搭建什么样的 AI 基础设施？**——以本团队为实例，盘点 GTX 1050 4G + RTX 5060 8G + 云端 API 的混合架构现状，如实描述能力边界（含实测数据与未测缺口）。
3. **这套设施如何支撑大模型部署与日常研发？**——覆盖 AI 网关的角色、本地推理引擎（Ollama/llama.cpp）、量化策略、云端 API 协同，以及"够不够用、瓶颈在哪、下一步往哪走"的评估。

### 1.2 目标读者

- 小型研发团队的负责人与技术决策者（如何用有限预算搭起可用 AI 设施）
- 正在做本地算力 + 云端 API 混合方案选型的工程师
- 对"个人级 AI 基础设施"能力边界好奇的技术爱好者

### 1.3 范围界定

- **纳入**：AI 基础设施的定义辨析、硬件/云端/网关/部署引擎四要素、小团队场景的能力与成本评估。
- **不纳入**：数据中心级超节点（已有 [10_supernode-rack 专题](../10_supernode-rack/2026-08-03-data-control-flow-and-network-partition-deep-analysis.md) 覆盖）、模型训练与微调细节（8GB 显存物理上不可行，仅标注边界）、具体厂商 API 的定价细则（以 2026-08-17 峰谷新价为基线做量级估算）。
- **数据口径**：本地硬件数据来自本团队 2026-08-11~16 实测与专项论证；云端数据来自系统运行统计与公开定价；引用处均行内标注来源。

---

## 2. AI Infra 定义深度辨析

### 2.1 定义谱系：从官方定义到工程定义

**官方定义（IBM，2026-04 更新）**：

> AI infrastructure consists of the hardware and software needed to create, deploy and manage AI-powered applications and workloads. [来源: IBM "What is AI Infrastructure?", web_fetch 2026-08-18]

关键短语是 **create（创建）、deploy（部署）、manage（管理）**——AI Infra 不是"训练算力"的代名词，而是覆盖 **AI 全生命周期**（训练→部署→运行→治理）的硬件+软件复合体。IBM 同时给出市场规模锚点：全球 AI 基础设施支出预计从 2025 年 $334B 增至 2029 年 $900B+（Statista 2026-03 预测）[来源: IBM 引 Statista, 2026-03-18]。

**行业理解（NVIDIA/Intel 语境）**：AI Infra 通常被拆为 Compute（加速器与服务器）、Network（互联）、Storage（数据与模型）、Software（框架与平台）四件套——这与知识库中 [Intel Crescent Island 体系](../../06_others/sources/2026-08-11-intel-crescent-island-inference-gpu.md) 的"骨架系统"定位一致：Intel 不自产加速器，而是提供 Host CPU、网络、内存池化、系统集成，构成集群底座。

**工程定义（本文件主张，MECE 三层）**：

> **AI Infra = 支撑 AI 应用从想法到产出的全部资源与服务**，按"资产形态"分为三层：
> - **算力层**（硬件资产）：GPU/CPU/NPU、显存、互联、供电散热——决定"跑得动吗"
> - **平台层**（软件资产）：推理引擎、模型服务框架、调度/网关、向量库——决定"跑得稳吗"
> - **服务层**（消费形态）：云端 API、模型服务、MCP 工具、治理与观测——决定"用得起吗"

这三层构成递归结构：对个人是"显卡 + Ollama + API"，对大型云厂商是"数据中心 + 集群调度 + AIaaS"——**定义不变，量级与复杂度不同**。这正是"小团队也能谈 AI Infra"的立论基础。

### 2.2 AI Infra vs IT Infra：本质差异

| 维度 | IT Infra | AI Infra | 差异根源 |
|:-----|:---------|:---------|:---------|
| 计算形态 | CPU 通用计算，任务短促 | GPU/TPU 并行矩阵计算，任务长时 | 工作负载的并行度差异 |
| 性能瓶颈 | 单核频率、IOPS | **显存容量与带宽**（memory-bound） | LLM decode 是带宽受限的 |
| 生命周期 | 部署即稳定 | 训练→量化→部署→迭代，循环往复 | 模型是"活的资产" |
| 成本结构 | 硬件一次投入 | 硬件折旧 + **token 持续消耗** | 推理成本随用量线性增长 |
| 故障模式 | 服务中断 | 显存 OOM、KV Cache 溢出、量化精度退化 | 资源约束是硬边界 |

核心判据（第一性原理）：**传统 IT 基础设施服务的是"确定性的逻辑"（跑同样的代码得同样的结果），AI 基础设施服务的是"概率性的模型"（同样的输入，结果有分布）**——因此 AI Infra 必须额外解决：模型版本管理、量化与精度权衡、上下文（KV Cache）管理、token 成本计量，这些在 IT Infra 中不存在。

### 2.3 AI Infra 的四层栈模型（本文件框架）

```
+--------------------------------------------------------+
|  L4 Application Layer    apps / agents (coding, QA)     |
+--------------------------------------------------------+
|  L3 Service Layer        cloud APIs, model svc, gateway |
|    - unified access: AI Gateway (routing/fallback/cache)|
|    - consumption: SaaS API / Managed Host / Self-host   |
+--------------------------------------------------------+
|  L2 Platform Layer       engines, frameworks, vec-db    |
|    - llama.cpp / Ollama / vLLM / SGLang                 |
|    - Embedding / Rerank / Vector DB / MCP Server        |
+--------------------------------------------------------+
|  L1 Compute Layer        compute & storage (local+cloud)|
|    - GPU VRAM/BW, CPU RAM, NVMe, network                |
|    - this team: GTX 1050 4G + RTX 5060 8G + cloud APIs  |
+--------------------------------------------------------+
```

- **L1 是物理底座**，决定模型能否加载、速度多快（带宽公式：decode tok/s ≈ 显存带宽 ÷ 每 token 权重读取量）。
- **L2 是效率放大器**，同样的 8GB 显存，引擎与量化选对可提升数倍有效能力（见 §5.2）。
- **L3 是弹性与成本调节器**，云端 API 提供无限算力幻觉，网关提供统一管理与兜底。
- **L4 是价值出口**，一切基础设施最终服务于应用产出。

### 2.4 按组织规模分级：企业级 vs 团队级 vs 个人级

| 维度 | 企业级（超节点/万卡） | 团队级（3-10 人） | 个人级 |
|:-----|:---------------------|:------------------|:-------|
| 算力 | 百~千 GPU，液冷超节点 | 1-4 张消费级/专业级 GPU | 0-1 张消费级 GPU |
| 典型部署 | 超节点（详见 [10_supernode-rack 专题](../10_supernode-rack/2026-08-03-data-control-flow-and-network-partition-deep-analysis.md)） | RTX 5060 + 云 API 混合 | 纯云 API 或单卡小模型 |
| 关注点 | 训练效率、故障恢复、供电散热 | **成本/能力平衡、上手门槛、协作共享** | 零运维、按需付费 |
| 平台软件 | Slurm/K8s+vLLM、全栈可观测 | Ollama/llama.cpp + 轻量网关 | 聊天界面即全部 |
| 关键指标 | MFU、checkpoint 时间 | **tok/s、上下文长度、月成本** | 响应速度、免费额度 |

关键洞察：**团队级 AI Infra 的本质约束不是"算力不足"，而是"每瓦/每元/每小时的产出效率"**。企业级追求 MFU（算力利用率），团队级追求的是 **E$/token（每 token 的有效成本）**与 **上手时间**。这决定了选型哲学完全不同（见 §6）。

### 2.5 边界辨析：AI Infra 与相邻概念

| 概念 | 与 AI Infra 的关系 | 边界 |
|:-----|:------------------|:-----|
| **MLOps** | AI Infra 的"流程层" | MLOps 管模型生命周期流程；AI Infra 管承载这些流程的资源 |
| **LLMOps** | MLOps 在 LLM 场景的特化 | 关注 prompt/上下文/token 成本，属于 AI Infra 平台层的一部分 |
| **AI 网关** | AI Infra 服务层的核心组件 | 网关是"统一接入与管理面"，不提供算力本身（详见 §4） |
| **算力平台**（算力租赁/调度） | AI Infra 算力层的一种供给形态 | 特指 GPU 资源供给，不含模型服务与治理 |
| **AIaaS** | AI Infra 服务层的商业化封装 | 把基础设施能力打包成 API 售卖，是"云侧 AI Infra 的消费者视角" |

**结论**：AI Infra 是最大的集合，其余概念是其子集或消费形态。团队在规划时应先画"四层栈"，再逐层选择供给方式（自建/租用/订阅），而不是直接跳到"买哪张卡"。

---

## 3. 当前基础设施搭建现状（本团队实例）

### 3.1 硬件资产清单

| 资产 | 配置 | 定位 | 状态 |
|:-----|:-----|:-----|:-----|
| **RTX 5060 8G 主机** | 16G 内存 / 20 核 CPU / 512G NVMe / RTX 5060 8G（GB206 + GDDR7 448GB/s）[来源: memory/2026-08-13.md] | 本地主力推理机（7B INT4 目标） | 已购，ollama 4G 档已验证，7B 档待实测 |
| **GTX 1050 4G 主机** | Pascal 2016，无 Tensor Core，FP16 慢，可用显存 3.5-3.8GB，Windows [来源: 2026-08-16-ollama-4g-deploy-sop.md] | 常驻小模型服务（≤4B） | 已部署 Ollama 0.17.5，2-10 tok/s 实测 |
| **云端 API** | DeepSeek（主力运行时）/ Claude Code（自定义端点）/ 豆包 / 其他 | 重活与前沿模型 | 在用，Zhipu key 已失效 [来源: memory/2026-08-18.md] |

### 3.2 混合架构总览

```
                    CLOUD SIDE
+-----------------------------------------------+
|  DeepSeek API    Claude Code    Doubao API     |
|  (main runtime)  (via 3rd-party endpoint)      |
+--------+---------------------+-----------------+
         | REST/OpenAI         | ANTHROPIC_BASE_URL
         | compatible          | (custom endpoint)
+--------v---------------------v-----------------+
|            ACCESS LAYER (evolving)             |
|  current: direct connection per provider       |
|  target : unified AI gateway (routing+key)     |
+--------+---------------------------------------+
         | OpenAI-compatible / MCP
+--------v---------------------------------------+
|         AGENT / APP LAYER                      |
|  CowAgent (Harness) / Agent Reach v1.5.0       |
|  + mcporter / chatgpt-on-wechat (feishu)       |
|  scheduled tasks x49 / daily distill 23:50     |
+--------+---------------------------------------+
         | OLLAMA API (127.0.0.1:11434/v1)
+--------v---------------------------------------+
|         LOCAL COMPUTE LAYER                    |
|  RTX 5060 8G  : target 7B INT4 (GGUF Q4_K_M)   |
|  GTX 1050 4G  : qwen2.5:3b / qwen3:4b /        |
|                qwen3.5:2b (2-10 tok/s real)    |
+-----------------------------------------------+
```

（架构图说明：Access Layer 当前为"按厂商直连"，统一网关为目标态，见 §4；Agent 层通过 OpenAI 兼容协议与本地 Ollama 互通）

### 3.3 各层当前状态与成熟度评估

| 层 | 当前实现 | 成熟度 | 主要缺口 |
|:---|:---------|:------:|:---------|
| L1 算力 | 5060 8G + 1050 4G + 云 | 🟡 可用 | 7B 实测数据未跑；1050 与 5060 分处两台机器 |
| L2 平台 | Ollama + GGUF 量化 | 🟡 可用 | 无 vLLM（8G 用 llama.cpp 系更稳 [来源: 08-14 工程规模评估]）；embedding/向量库未接 |
| L3 服务 | 直连各云 API | 🟠 直连态 | **无统一网关**（key 分散、无路由/回退/计量） |
| L4 应用 | CowAgent + feishu + 定时任务 | 🟢 成熟 | Agent 生态强，但底层模型切换依赖手工改 env |

**一句话现状**：算力层"小马拉小车"已跑通（4G 卡能稳定出活），服务层处于"多 key 直连"的原始阶段——**这正是 AI 网关应该补位的位置**。

---

## 4. AI 网关的角色与落地

### 4.1 网关为什么存在（第一性原理）

AI 网关存在的根因：**模型供给从"单一供应商"走向"多供应商 + 多形态（云/本地）"，而应用层需要稳定的统一接口**。其价值公式已在 [AI 网关深度分析](../04_ai/2026-08-17-ai-gateway-llm-service-comparison-deep-analysis.md) 中展开（协议转换/路由/回退/缓存/鉴权/限流/计量/观测 10 大机制），本文件只强调与团队现状相关的三点：

1. **多端点收敛**：团队成员不需要各自记 DeepSeek/Claude/豆包/本地 Ollama 的 key 与地址，统一到一个 OpenAI 兼容端点。
2. **成本与故障兜底**：云端 API 涨价（8/17 峰谷新价生效后 miss 输入 1→1.5/3.0、输出 2→4.5/9.0 [来源: MEMORY.md 08-15 实测]）或故障时，网关可自动回退到本地小模型——这是小团队"用得起"的关键机制。
3. **计量透明**：小团队预算有限，网关按 key/项目计量 token 消耗，是控制月成本（当前量级 ¥45~126 模拟 [来源: memory/2026-08-16.md]）的前提。

### 4.2 当前形态：多端点直连（阶段 0）

| 消费方 | 接入方式 | 端点 |
|:-------|:---------|:-----|
| CowAgent 主运行时 | 官方 API 直连 | DeepSeek 官方端点 |
| Claude Code | `ANTHROPIC_BASE_URL` 自定义端点 [来源: import CSDN 部署指南 2026-03-21] | 第三方代理 |
| 本地小模型 | OpenAI 兼容端点 `http://127.0.0.1:11434/v1` [来源: ollama-local-deploy-4g.md] | 本机 Ollama |
| 豆包 | 官方 API 直连（分享导入用） | 豆包官方端点 |

**问题**：①key 分散在每台机器/每个工具的环境变量里；②无统一计量与配额；③云端故障时无自动降级；④团队成员接入成本高（需各自配置）。

### 4.3 目标形态：统一网关（阶段 1-2）

基于 [08-17 产品对比](../04_ai/2026-08-17-ai-gateway-llm-service-comparison-deep-analysis.md) 的 8 家产品矩阵，按团队场景（<10 人、需本地+云端混合、预算敏感）排序：

| 候选 | 优势 | 团队适配度 | 备注 |
|:-----|:-----|:----------:|:-----|
| **LiteLLM** | 开发者生态之王，100+ 模型统一接口，Python 直装 | ⭐⭐⭐⭐⭐ | 起步最快，`litellm --config` 即可 |
| **One-API** | 国产分发之王，Web 管理面友好，虚拟 key+计量 | ⭐⭐⭐⭐ | 国内访问友好，配额/计量开箱即用 |
| **Higress** | 云原生 AI 网关，CNCF Sandbox | ⭐⭐⭐ | 适合已有 K8s 的团队，过重 |
| **Portkey** | 轻量极速 + 护栏/缓存 | ⭐⭐⭐ | 观测强，自托管需 Node |
| **OpenRouter** | 模型超市，零自建 | ⭐⭐⭐ | 无需运维，但数据出境与成本需评估 |

**团队落地建议（阶段化）**：

```
Phase 0 (current): direct connection per provider
        |  problem: keys scattered, no fallback, no metering
        ▼
Phase 1: LiteLLM proxy on the 5060 host (or NAS-like box)
        - unify DeepSeek + Claude endpoint + local Ollama
        - one OpenAI-compatible URL for whole team
        - enable fallback: cloud -> local qwen3.5:2b on error
        ▼
Phase 2 (optional): One-API for web UI + virtual keys + quota
        - per-member keys, monthly token budget
        - cost dashboard feeding the token-cost analysis
```

### 4.4 小团队网关选型决策树

```
Does the team run K8s?
+-- yes --> Higress / Envoy AI Gateway
+-- no -->
    Need web admin + quota metering?
    +-- yes --> One-API
    +-- no --> LiteLLM (fastest, single Python process)
         Need zero-ops fully managed?
         +-- yes --> OpenRouter (check data residency first)
```

---

## 5. 大模型部署方式与运行支撑能力

### 5.1 部署方式全景（三维选择）

| 方式 | 代表 | 单价量级 | 能力上限 | 适用 |
|:-----|:-----|:---------|:---------|:-----|
| **SaaS API** | DeepSeek/Claude/GPT | 分/token 计 | 前沿模型、超长上下文 | 主力生产（重活） |
| **托管推理** | SiliconFlow/OpenRouter | 分/token，略低于 SaaS | 开源模型、免运维 | 开源模型快速试用 |
| **本地自托管** | Ollama/llama.cpp | 电费+折旧，≈0 边际 | 受显存硬约束 | 隐私/离线/降级兜底 |

三种方式不是互斥，而是**同一模型服务栈的弹性分层**：本地跑得动且质量够 → 本地；需要更强能力或更长上下文 → 云。选择依据是"任务质量要求 × 数据敏感度 × 成本预算"三因子。

### 5.2 本地推理引擎与量化（8G/4G 甜点区）

**显存预算第一性原理公式** [来源: 2026-08-16-ollama-4g-deploy-sop.md]：

```
total_vram = weights + KV_cache + runtime(~250MB)
weights    = params x bpp  (Q4_K_M=0.56, Q8=1.05, FP16=2.0 B/param)
KV         = 2 x layers x KV_heads x head_dim x 2B x ctx_len
usable_ctx <= (free_vram - weights - 250MB) / KV_bytes_per_token
```

**量化方法论**（承接 [量化分析框架](../../03_AI/llm-techniques-principles/2026-08-17-model-quantization-analysis-framework.md)）：8G 显存下 7B INT4 是甜点区（权重 ~4GB，方案排序 **AWQ > GPTQ > GGUF**，引擎 llama.cpp/vLLM 二选一；本地 8G 起步 **GGUF Q4_K_M + llama.cpp/Ollama**，兼容性最好、支持 offload [来源: knowledge/06_others/ideas/2026-08-18_summary.md]）。

⚠️ **架构陷阱**：KV/token 因模型架构差异巨大——传统全注意力 qwen3:4b 为 144KB/token，DeltaNet 混合 qwen3.5:2b 仅 12KB/token（1/12）[来源: 2026-08-16-ollama-4g-deploy-sop.md]。选型前必须查 config.json，不能套用公式假设。

### 5.3 RTX 5060 8G 能力边界（本地主力）

| 维度 | 数据 | 条件 |
|:-----|:-----|:-----|
| 显存带宽 | 448 GB/s（GDDR7，+65% vs 4060 的 272）[来源: memory/2026-08-11.md] | 官方规格 |
| decode 理论 | ~96 tok/s（7B INT4：带宽 ÷ 权重体积）[来源: 同上，第一性公式] | memory-bound |
| decode 实测预期 | 75-85 tok/s | 待本机实测（08-11 论证值） |
| FP4 原生红利 | Qwen3-FP4 ~4.09GB → 理论 ~109 tok/s | Blackwell 原生 FP4，4060 无此能力 |
| 硬边界 | 不可 INT8、不可 32K+ 长上下文、不可训练/微调 | 8GB 物理上限 [来源: 同上] |

**定位结论**：5060 是"8GB 卡里推理最优选"，速度维度是亮点（decode 逼近 100 tok/s），但容量天花板未变——它是**推理机，不是训练机**；长上下文与强模型仍需云端。

### 5.4 GTX 1050 4G 能力边界（实测数据）

| 模型 | 量化 | 权重 | 上下文 | 实测占用 | 速度 |
|:-----|:----:|:----:|:------:|:--------:|:----:|
| qwen2.5:3b | Q4_K_M | 1.7GB | 8192 | ~3.2GB ✅ | 5-10 tok/s |
| qwen3:4b | Q4_K_M | 2.3GB | 4096（甜点） | ~3.1GB ✅ | 2-10 tok/s |
| qwen3.5:2b | Q4 | 2.7GB | 32768（DeltaNet） | ~3.4GB ✅ | 2-10 tok/s |
| 7B 任意 | — | ≥4.1GB | — | ❌ 超 4G 出局 | — |

[来源: 2026-08-16-ollama-4g-deploy-sop.md 实测占用表]

**关键工程细节**（SOP 沉淀）：`ollama run` 命令行参数只对交互会话生效；**OpenAI 兼容端点 `/v1` 不解析 num_ctx**，必须用 Modelfile 固化或 `OLLAMA_CONTEXT_LENGTH` 环境变量 [来源: ollama-local-deploy-4g.md]。1050 无 Tensor Core，INT 量化计算慢，是"能用但只能做轻活"的定位——适合常驻跑一个 2B/3B 模型做降级兜底与离线任务。

### 5.5 云端 API 支撑能力

| 维度 | 现状 | 数据 |
|:-----|:-----|:-----|
| 主力模型 | DeepSeek（deepseek-v4-flash 运行时） | 本系统实际运行中 |
| 成本量级 | 月 ¥45~126（8/17 峰谷新价模拟）[来源: memory/2026-08-16.md] | 1817 调用/127.8M 输入/cache 命中 95.8%/¥10.53（08-15~16 实测） |
| 缓存红利 | 命中 95.8% 是最大成本杠杆 | 缓存未命中 57.1% 是最大成本项（08-15 实测）[来源: MEMORY.md] |
| 风险 | 8/17 新价 miss+输出 谷+75%/峰+250% | P0 迁移空闲时段 |

**云端定位**：承担"重活"（深度分析、长上下文、前沿模型），配合本地做"轻活"（简单问答、降级兜底），形成成本-能力双优化。

### 5.6 部署决策树（小团队）

```
Task type?
+-- frontier ability / long context / strongest --> cloud API
+-- sensitive data / offline / privacy --> local (5060 7B or 1050 small)
+-- cost sensitive / batch / fallback --> local small model (2B-4B)
+-- cloud outage / price spike --> gateway fallback to local (needs gateway)
```

---

## 6. 支持小型团队研发的评估

### 6.1 场景 × 资源能力矩阵

| 研发场景 | 云端 API | 5060 8G (7B) | 1050 4G (≤4B) | 当前方案 |
|:---------|:--------:|:------------:|:-------------:|:---------|
| 代码补全/Agent 编码 | ✅ 强 | 🟡 中（短 ctx） | ❌ | 云端（Claude Code 等） |
| 文档/深度分析 | ✅ 强 | 🟡 中 | ❌ | 云端 DeepSeek |
| 简单问答/工具调用 | ✅ | ✅ | ✅ 2-10 tok/s | 混合 |
| 知识检索/Embedding | ✅ | ✅ 可跑 | ✅ | 云端为主 |
| RAG 原型 | ✅ | ✅ | 🟡 小库 | 待建（L2 缺口） |
| 本地降级兜底 | — | ✅ | ✅ 常驻 | 1050 常驻小模型 |
| 模型微调/训练 | ✅ 租卡 | ❌ 8G 不可行 | ❌ | 不投入（战略收敛） |
| 推理性能实验 | — | ✅ 主战场 | 🟡 | 5060 专项 |

### 6.2 成本模型（云端 token vs 本地折旧）

| 项 | 云端（月） | 本地（月） | 备注 |
|:---|:----------:|:----------:|:-----|
| token 消耗 | ¥45~126（当前实测外推）[来源: memory/2026-08-16.md] | 本地推理≈0 | 8/17 新价后上浮 |
| 硬件折旧 | — | 5060（~¥2-3K 分 24 月 ≈¥100-125）+ 1050（已折旧） | 一次性投入摊薄 |
| 电费 | — | ~¥15-30（两卡满负荷估） | 实际负载低 |
| **合计** | **¥45~126** | **≈¥115-155** | 量级相当，但本地是"固定成本换确定性" |

**结论**：纯成本上云端略优（尤其 cache 命中 95.8% 的红利）；本地价值不在省钱，而在 **数据主权、离线可用、故障兜底、实验自由**（不限量跑测试）。战略上是"云端为主力、本地为保险"的互补结构。

### 6.3 瓶颈与风险

| 瓶颈/风险 | 影响 | 对策 |
|:----------|:-----|:-----|
| **无统一网关** | key 分散、无回退、无计量 | Phase 1 上 LiteLLM（§4.3） |
| **7B 实测缺失** | 5060 真实能力未验证 | 跑 MMLU 中文子集 vs FP16 基线（08-17 量化文档建议） |
| **8GB 容量天花板** | 长上下文/大模型不可用 | 长文任务走云端，本地只做短 ctx |
| **云端涨价波动** | 8/17 新价 +75~250% miss | 空闲时段调度 + 缓存策略 + 本地降级 |
| **两台机器割裂** | 1050/5060 不互通 | 网关把两台本地端点并入统一入口 |
| **embedding/向量库缺位** | RAG 无法落地 | L2 补 Chroma/Milvus Lite + bge-m3 |

---

## 7. 演进路线建议（按优先级）

```
P0 (this week) : benchmark 5060 with 7B (GGUF Q4_K_M + MMLU subset)
P1 (this month): Phase-1 gateway (LiteLLM: DeepSeek + Claude + local x2)
                 - unified access endpoint for the team
                 - auto fallback to local qwen3.5:2b on cloud outage
                 - central key management + usage logging
P2 (quarter)   : add L2 retrieval stack (embedding bge-m3 + light vec-db)
                 - enables RAG prototype and KB Q&A
P3 (half year) : evaluate One-API virtual keys/quota (multi-user)
                 or Higress (if team adopts K8s)
```

**战略校准**（对齐 08-14 战略收敛期决策）：知识库搭建已达标，后续投入聚焦 Claude Code + 数据源质量 + 本地算力 [来源: MEMORY.md]——本文档 P0/P1 与该战略一致：**本地算力做实（实测+网关），而非继续扩张知识库规模**。

---

## 参考文件

### 内部知识库引用

- [AI 网关产品对比深度分析](2026-08-17-ai-gateway-llm-service-comparison-deep-analysis.md) — 互补篇：本文件为其组织内落地视角
- [推理场景 AI 全栈优化方案深度分析](2026-08-18-inference-fullstack-optimization-deep-analysis.md) — 同族：全栈优化总纲（六层地图）
- [三场景 AI 全栈优化方案深度分析](2026-08-18-three-tier-ai-fullstack-optimization-deep-analysis.md) — 同族：部署形态视角
- [AI 芯片设计知识系统](2026-08-18-ai-chip-design-knowledge-system.md) — 关联：芯片设计与知识沉淀
- [SOP：4G 显存 Ollama 本地大模型部署与配置](../../05_tools/ai-tools/2026-08-16-ollama-4g-deploy-sop.md) — 实测依据
- [Ollama 本地模型部署：4G 显存启动模板](../../05_tools/ai-tools/ollama-local-deploy-4g.md) — 实测依据
- [深度分析论证：8GB 显存能否跑 8B 模型](../../03_AI/llm-techniques-principles/2026-08-11-8gb-vram-8b-model-feasibility.md) — 容量论证
- [模型量化分析框架](../../03_AI/llm-techniques-principles/2026-08-17-model-quantization-analysis-framework.md) — 量化方法论
- [Intel Crescent Island 推理 GPU 分析](../../06_others/sources/2026-08-11-intel-crescent-island-inference-gpu.md) — 行业参照
- [超节点专题](../../10_supernode-rack/) — 数据中心级对照

### 外部资料引用

- 来源: IBM, "What is AI Infrastructure?" (2026-04-08 更新) — https://www.ibm.com/topics/ai-infrastructure
- 来源: Statista, "AI infrastructure spending worldwide 2025/2029" (2026-03-18，经 IBM 引用)
- 来源: CSDN, 《国内 Claude Code 从零到一：本地安装 + 自定义 API 接口全配置指南》(2026-03-21，import/ 素材)
- 来源: 本团队运行统计（deepseek_usage / memory/2026-08-16.md / MEMORY.md，成本与价格数据）

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-18 | v1.0 | 首次创建：AI Infra 定义辨析（三层/四层栈/分级）+ 本团队混合架构现状（1050+5060+云）+ 网关落地路线 + 部署能力与成本评估 |
| 2026-08-22 | v1.1 | 提升：补齐 std-002 五元素 + 跨文件交叉链接与一致性勘误 |
