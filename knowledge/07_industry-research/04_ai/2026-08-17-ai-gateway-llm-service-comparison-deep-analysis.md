# AI 大模型服务提供方式 × AI 网关实现机制 × 产品功能对比深度分析

> **版本**: v1.0
> **日期**: 2026-08-17
> **核心问题**: 大模型服务有哪些提供方式（SaaS/托管推理/私有化/自托管）？AI 网关为何成为混合模型时代的刚需？其 10 大实现机制如何工作？主流产品（LiteLLM/Portkey/One-API/Higress/Envoy AI GW/OpenRouter/Kong/Cloudflare）功能差异在哪、如何选型？
> **概要**: 本文以「部署位置 × 模型权属」两轴建立服务提供方式全景（四种方式各自经济学特征），从第一性原理论证 AI 网关与传统 API 网关的本质分界（网关需"读懂 prompt"而非仅转 URL），拆解 AI 网关 10 大实现机制（协议转换/路由/重试回退/缓存/虚拟 Key/限流/成本追踪/护栏/可观测/MCP-A2A），并基于官方文档对 8 款主流产品做 20+ 维度对比，给出决策树与三阶段落地路径。核心结论：网关正在从"LLM 代理"升级为"Agent 基础设施"（MCP/A2A 成必选项）；延迟竞争白热化（LiteLLM 8ms@1kRPS、Portkey <1ms）；自托管与托管混合是 2026 年主流形态。
> **关键词**: AI 网关 · LLM Gateway · LiteLLM · Portkey · OpenRouter · One-API · Higress · Envoy AI Gateway · Kong · Cloudflare · 语义缓存 · 护栏 · MCP · A2A
> **适用对象**: AI 基础设施/平台团队技术决策者、架构师、模型服务化商业模式从业者
> **关联**: [推理 GPU 容量 SKU 战略](2026-08-11-inference-gpu-capacity-sku-strategy-framework.md) · [单位 token 成本五看三定](2026-08-13-unit-token-cost-five-looks-three-decisions-deep-analysis.md) · [DeepSeek 8T 日 TCO](2026-08-14-deepseek-8t-daily-tco-analysis.md)

---

## 目录

- [1. 引言与范围](#1-引言与范围)
- [2. AI 大模型服务的提供方式全景](#2-ai-大模型服务的提供方式全景)
  - [2.1 四种提供方式的坐标轴](#21-四种提供方式的坐标轴)
  - [2.2 各方式深度拆解](#22-各方式深度拆解)
  - [2.3 提供方式演进趋势](#23-提供方式演进趋势)
- [3. AI 网关为什么存在：第一性原理](#3-ai-网关为什么存在第一性原理)
  - [3.1 传统 API 网关 vs AI 网关](#31-传统-api-网关-vs-ai-网关)
  - [3.2 网关的价值公式](#32-网关的价值公式)
- [4. AI 网关的 10 大实现机制](#4-ai-网关的-10-大实现机制)
  - [4.1 协议转换与统一 API](#41-协议转换与统一-api)
  - [4.2 模型路由与负载均衡](#42-模型路由与负载均衡)
  - [4.3 重试与回退（Fallback）](#43-重试与回退fallback)
  - [4.4 缓存：精确缓存 + 语义缓存](#44-缓存精确缓存--语义缓存)
  - [4.5 鉴权与虚拟 Key](#45-鉴权与虚拟-key)
  - [4.6 限流与额度管控](#46-限流与额度管控)
  - [4.7 成本追踪与计量计费](#47-成本追踪与计量计费)
  - [4.8 护栏与数据安全](#48-护栏与数据安全)
  - [4.9 可观测性](#49-可观测性)
  - [4.10 MCP 与 A2A 网关（2025-2026 新增）](#410-mcp-与-a2a-网关2025-2026-新增)
- [5. 产品功能详细对比](#5-产品功能详细对比)
  - [5.1 开源阵营](#51-开源阵营)
  - [5.2 商业/托管阵营](#52-商业托管阵营)
  - [5.3 核心对比矩阵](#53-核心对比矩阵)
  - [5.4 分场景胜出者](#54-分场景胜出者)
- [6. 选型决策框架](#6-选型决策框架)
  - [6.1 决策树](#61-决策树)
  - [6.2 落地路径建议](#62-落地路径建议)
- [7. 趋势研判](#7-趋势研判)
- [8. 参考文件](#参考文件)

---

## 1. 引言与范围

### 1.1 文档目的

2025-2026 年，大模型从"单模型直连"快速走向"多模型混用 + Agent 化 + MCP 工具化"。企业 AI 平台团队面临三个结构性难题：

1. **模型碎片化**：同一应用需要调用 OpenAI/Anthropic/国产模型/自托管 vLLM 等多源，协议、鉴权、计价各不相同；
2. **治理缺失**：缺乏统一鉴权、限流、成本分摊、数据安全边界；
3. **可靠性焦虑**：单一供应商故障 = 业务中断，需要回退/负载均衡。

AI 网关（AI Gateway / LLM Gateway）作为连接层应运而生。本文回答三个问题：
- 大模型服务**有哪些提供方式**？各自经济学特征？
- AI 网关**如何实现**统一接入/路由/治理/成本控制？
- 主流产品**功能差异**在哪？如何选型？

### 1.2 目标读者

- AI 基础设施/平台团队技术决策者
- 需要评估自建网关 vs 商业网关的架构师
- 关注模型服务化商业模式的从业者

### 1.3 范围界定

- 覆盖产品：LiteLLM、Portkey、OpenRouter、One-API、Higress、Envoy AI Gateway、Kong AI Gateway、Cloudflare AI Gateway（截至 2026-08 公开资料）
- 不覆盖：模型训练平台、向量数据库、具体模型评测
- 数据来源：各产品官方文档/GitHub（见参考文献），量化数据均标注来源

---

## 2. AI 大模型服务的提供方式全景

### 2.1 四种提供方式的坐标轴

大模型服务的提供方式可归到两个正交维度上：

| 维度 | 两极 | 含义 |
|:-----|:-----|:-----|
| **部署位置** | 托管（Managed）vs 自托管（Self-hosted） | 模型权重和推理基础设施在谁手里 |
| **模型权属** | 闭源（Proprietary）vs 开源（Open-weight） | 权重是否公开、能否二次开发 |

两轴交叉得到四种提供方式：

```
              Deployment
        Managed        Self-hosted
     +--------------+--------------+
  Closed |  A. SaaS API |  C. Private   |
         |  (OpenAI)    |  Deployment   |
  Weight +--------------+--------------+
  Open   |  B. Managed  |  D. Self-host |
         |  Inference   |  (vLLM+GPU)   |
         +--------------+--------------+
```
（中文释义：A=闭源托管 SaaS API；B=开源托管推理；C=闭源私有化部署；D=开源自托管）

### 2.2 各方式深度拆解

#### A. SaaS API（闭源托管）—— 零运维，最高单价

| 特征 | 说明 |
|:-----|:-----|
| 典型产品 | OpenAI GPT 系列、Anthropic Claude、Google Gemini、DeepSeek 官方 API、国产闭源（豆包/通义/文心） |
| 计费模式 | 按 token 计费（输入/输出分开计价），如 DeepSeek 2026-08 调价后 flash 输入 $1.5/M（缓存未命中）、输出 $4.5/M [来源: 2026-08-13-unit-token-cost-five-looks-three-decisions-deep-analysis.md] |
| 优点 | 零运维、开箱即用、持续更新、SLA 明确 |
| 缺点 | 单价最高、数据出境/合规风险、供应商锁定、无定制权 |

**经济学**：SaaS API 是"买时间"——用钱换掉 GPU 资本开支、运维人力、模型迭代成本。适合：验证期、低延迟要求不高、数据不敏感的场景。

#### B. 托管推理平台（开源模型托管）—— 价格/性能平衡

| 特征 | 说明 |
|:-----|:-----|
| 典型产品 | Together AI、Fireworks AI、Groq、DeepInfra、Novita、OpenRouter（聚合多家）、NVIDIA NIM、火山引擎方舟、硅基流动 |
| 计费模式 | 按 token 或按小时租用 GPU |
| 优点 | 开源模型无需自建 GPU、通常比闭源 SaaS 便宜数倍、可横向对比 |
| 缺点 | 仍受平台限制（无权重控制权）、供应商稳定性风险 |

**关键区分**：托管推理平台的差异化在**推理引擎优化**——如 Groq 用 LPU 实现极低延迟、Together 用 FlashAttention 提升吞吐。平台赚的是"推理优化差价"。

#### C. 私有化部署（闭源模型）—— 合规刚需，高成本

| 特征 | 说明 |
|:-----|:-----|
| 典型产品 | 企业采购闭源模型商用授权（如 Anthropic 企业版、国产大模型一体机） |
| 计费模式 | 授权费 + 硬件成本 + 运维成本 |
| 优点 | 数据不出域、合规、可定制 prompt/微调 |
| 缺点 | 最贵、更新滞后、依赖厂商支持 |

#### D. 开源自托管（Open-weight + 自建 GPU）—— 极致成本，全权控制

| 特征 | 说明 |
|:-----|:-----|
| 典型产品 | Llama/Qwen/DeepSeek 权重 + vLLM/SGLang/llama.cpp + 自有 GPU |
| 计费模式 | 硬件折旧 + 电费 + 运维（边际 token 成本趋近于 0） |
| 优点 | 成本最低、数据全控、可深度定制（量化/投机解码/定制路由） |
| 缺点 | 需要 GPU 资本开支 + 推理工程能力 + 模型迭代自己跟进 |

**经济学测算**：本地 RTX 5060 8G 跑 7B INT4 级别模型（战略收敛期决策参考 [来源: MEMORY.md 08-14 决策]）；大规模则需 H100/H200 集群——这正是 [推理 GPU 容量 SKU 战略](2026-08-11-inference-gpu-capacity-sku-strategy-framework.md) 讨论的核心。

### 2.3 提供方式演进趋势

```
2023 Single SaaS direct connect
  |
  +-- 2024 Multiple SaaS coexist -> unified interface needed (LiteLLM SDK)
  |
  +-- 2025 Open-weight mature -> managed inference + self-hosting rise
  |
  +-- 2026 Agent + MCP -> gateway evolves from "LLM proxy" to "Agent/tool gateway"
```

**结论**：提供方式从"单点"走向"混合"——同一企业往往同时用 SaaS（主力模型）+ 托管推理（性价比模型）+ 自托管（敏感数据/长尾）。**混合使用直接催生了对 AI 网关的刚需**。

---

## 3. AI 网关为什么存在：第一性原理

### 3.1 传统 API 网关 vs AI 网关

| 维度 | 传统 API 网关（Kong/Nginx/APISIX） | AI 网关（LiteLLM/Portkey/Higress 等） |
|:-----|:-----|:-----|
| 理解的数据 | HTTP 请求头/URL/JSON | **Prompt 内容 + Token 消耗 + 模型语义** |
| 核心资源 | 下游服务实例 | **模型/供应商/Token 预算** |
| 限流单位 | QPS | **Token 速率 + 额度** |
| 计费 | 请求数 | **按模型价格表 × token 数** |
| 缓存 | 精确 URL 缓存 | **语义缓存（相似 prompt 命中）** |
| 路由 | 静态/权重 | **语义路由 + 模型能力路由** |
| 新增能力 | 熔断/灰度 | **护栏（Guardrail）+ MCP/A2A** |

> Kong 官方 FAQ 明确定位：如果只是把 LLM API 放在网关后面，只能做 API 级交互；**AI 插件让网关"读懂 prompt"**，从而提供特定 AI 能力 [来源: docs.konghq.com AI Gateway]。这是两类网关的本质分界。

### 3.2 网关的价值公式

网关的存在价值 = 降低的治理成本 + 提升的可靠性收益 − 引入的额外延迟 − 运维成本。

```
Gateway value = (unified access + governance + cost control + reliability)
              - (latency overhead + ops cost + single-point risk)

When #models x #teams x #calls grows, governance benefit rises superlinearly
-> small scale (1 model, 1 team) does NOT need a gateway
-> large scale (multi-model, multi-team) gateway is a MUST
```

**关键设计权衡**：网关是**中心化代理**，天然引入一跳延迟。一流网关把代理开销压到极低：
- LiteLLM：8ms P95 @ 1k RPS（Rust 核心重构后官方 benchmark）[来源: github.com/BerriAI/litellm]
- Portkey：<1ms 延迟、122KB footprint [来源: github.com/Portkey-AI/gateway]
- 这个"延迟税"换回的是治理/成本/可靠性三方面数量级收益

---

## 4. AI 网关的 10 大实现机制

### 4.1 协议转换与统一 API

**问题**：各家 API 格式不同（OpenAI 用 chat/completions、Anthropic 用 /messages、Gemini 用 generateContent、国产各家各有差异）。

**机制**：网关提供 OpenAI 兼容的统一接口，内部做协议翻译。

```
Client (OpenAI format)
    | POST /v1/chat/completions
    v
+----------------------+
|  AI Gateway          |
|  +----------------+  |
|  | Protocol       |  |---> OpenAI native
|  | translation    |  |---> Anthropic /messages
|  | (bidirectional)|  |---> Gemini generateContent
|  +----------------+  |---> Azure OpenAI
|                      |---> vLLM/Ollama/self-hosted
+----------------------+
```

**实现细节**：
- LiteLLM 支持 100+ provider 的 protocol 转换，含 /chat/completions、/responses、/embeddings、/images、/audio、/batches、/rerank 全端点 [来源: github.com/BerriAI/litellm]
- Portkey 支持 250+ LLM、1600+ 模型的多模态（vision/audio/image）[来源: github.com/Portkey-AI/gateway]
- One-API 强调"统一 API 适配"，支持 OpenAI/Claude/Gemini/DeepSeek/豆包/ChatGLM/文心/通义/讯飞等国产全覆盖 [来源: github.com/songquanpeng/one-api]
- Higress 支持 100+ 模型统一协议转换 [来源: higress.cn]

### 4.2 模型路由与负载均衡

**路由维度**：
1. **模型路由**：同一逻辑模型名 → 多个物理模型（如 gpt-4o 可路由到 Azure/OpenAI 两个部署）
2. **条件路由**：按请求特征（用户/团队/上下文长度/是否流式）选模型
3. **语义路由**：按 prompt 语义相似度路由到最合适模型（Kong AI Proxy Advanced 支持语义匹配负载均衡 [来源: docs.konghq.com]）
4. **Provider 优化路由**：按实时价格/延迟自动切换最经济供应商（Portkey provider optimization* [来源: github.com/Portkey-AI/gateway]）

**负载均衡算法**（Kong 明确列出的）：consistent hashing、lowest-latency、usage-based、round-robin、semantic matching [来源: docs.konghq.com]。

### 4.3 重试与回退（Fallback）

**机制**：请求失败 → 自动重试（指数退避）→ 仍失败 → 回退到备用模型/供应商。

```
Request -> Primary model (OpenAI)
             | 429 / 5xx / timeout
             v
           Retry xN (exponential backoff)
             | still failing
             v
           Fallback model 1 (Anthropic)
             | still failing
             v
           Fallback model 2 (self-hosted vLLM)
```

- Portkey：自动重试最多 5 次（指数退避），可按错误码指定触发回退 [来源: github.com/Portkey-AI/gateway]
- One-API：失败自动重试 [来源: github.com/songquanpeng/one-api]
- Cloudflare AI Gateway：请求重试 + 模型回退定义 [来源: developers.cloudflare.com/ai-gateway]
- LiteLLM：Router 内置跨 deployment retry/fallback [来源: docs.litellm.ai]

### 4.4 缓存：精确缓存 + 语义缓存

**精确缓存**：完全相同的请求直接返回缓存结果 → 0 延迟 + 0 token 成本。
**语义缓存**：相似语义的请求（不同表述问同一问题）命中缓存 → 需要 embedding 相似度计算。

| 产品 | 精确缓存 | 语义缓存 | 备注 |
|:-----|:--------:|:--------:|:-----|
| LiteLLM | ✅ | 部分 | 配置级 |
| Portkey | ✅ | ✅ (enterprise) | simple + semantic caching [来源: github.com/Portkey-AI/gateway] |
| Higress | ✅ | ✅ | 精确+语义缓存，节省 Token 减时延 [来源: higress.cn] |
| Cloudflare | ✅ | — | 从 CF 缓存直接服务 [来源: developers.cloudflare.com] |
| Kong | ✅ | ✅ | Semantic caching 插件 [来源: docs.konghq.com] |

> ⚠️ 语义缓存的**正确性风险**：对需要实时性的场景（天气/股价/代码执行）缓存会返回过期结果。实践上建议：缓存仅对幂等问答开启，且设置 TTL。

### 4.5 鉴权与虚拟 Key

**机制**：网关持有真实供应商 Key，向应用签发"虚拟 Key"，应用只认虚拟 Key。

```
App 1 (virtual key A: team X / budget $100 / model set M1)
App 2 (virtual key B: team Y / budget $50 / model set M2)
    |
    v
+----------------------+
|  AI Gateway          | <-- real keys stored ONLY here
+----------------------+     (KMS / Secrets Manager)
    |
    v
Upstream providers (see gateway's key, cannot trace to app)
```

**能力分级**：
- LiteLLM：virtual keys + per-key/team/user budgets [来源: docs.litellm.ai]
- One-API：令牌管理（过期时间/额度/IP 白名单/允许模型）[来源: github.com/songquanpeng/one-api]
- Portkey：secure key management + RBAC [来源: github.com/Portkey-AI/gateway]
- Higress：消费者认证（密钥/第三方登录）
- Kong：Key Authentication 插件 + Konnect Config Store 密钥管理 [来源: docs.konghq.com]

### 4.6 限流与额度管控

**两类限流**：
1. **速率限流**：QPS/RPM（单 IP/单 Key）
2. **额度限流**：Token 预算（按 Key/团队/用户）

One-API 额度公式：`额度 = 分组倍率 × 模型倍率 × (提示token + 补全token × 补全倍率)` [来源: github.com/songquanpeng/one-api]

- One-API：全局速率限制（单 IP 三分钟 180 请求）、兑换码充值、用户分组倍率 [来源: github.com/songquanpeng/one-api]
- Cloudflare：spend limits + rate limiting [来源: developers.cloudflare.com]
- Kong：Rate limiting 插件 + access tiers [来源: docs.konghq.com]
- Higress：Token 管控——超额限制 + 额度分析 [来源: higress.cn]

### 4.7 成本追踪与计量计费

**核心**：网关知道每次调用的 model + token 数 → 按价格表实时计算成本 → 归集到 Key/团队/项目。

- LiteLLM：cost tracking per key/team/user；model_prices_and_context_window.json 维护价格表 [来源: github.com/BerriAI/litellm]
- Portkey：usage analytics（请求量/延迟/成本/错误率）+ Portkey Models 开源定价库（2300+ 模型 40+ 供应商）[来源: github.com/Portkey-AI/gateway]
- Kong：LLM metrics + Metering & Billing（按 token 定价，Stripe/ERP 集成）[来源: docs.konghq.com]
- One-API：额度明细 + 渠道余额更新 [来源: github.com/songquanpeng/one-api]

### 4.8 护栏与数据安全

**护栏（Guardrail）**：对输入/输出做内容校验——敏感词、PII 脱敏、主题过滤、合规检查。

| 产品 | 护栏能力 |
|:-----|:---------|
| Portkey | 50+ 预置 guardrails + 自带 guardrail + 合作伙伴（SOC2/HIPAA/GDPR/CCPA 合规）[来源: github.com/Portkey-AI/gateway] |
| Kong | 全套：AI Prompt Guard、AI Semantic Prompt Guard、AI PII Sanitizer（20 类 9 语言 PII 检测）、Azure Content Safety、AWS Guardrails、GCP Model Armor、AI Lakera Guard、AI Custom Guardrail [来源: docs.konghq.com] |
| LiteLLM | guardrails（content filtering、PII masking）[来源: docs.litellm.ai] |
| Cloudflare | DLP + Guardrails + BYOK [来源: developers.cloudflare.com] |
| Higress | 输入隐私保护 + 输出内容过滤 [来源: higress.cn] |

> 💡 **Kong 的护栏最全**：因为它把第三方护栏服务（Azure/AWS/GCP/Lakera）做成了插件生态，企业可复用已有安全栈。这是"传统网关转型 AI 网关"的差异化优势。

### 4.9 可观测性

- **日志**：输入/输出/延迟/错误全量记录（Portkey Gateway Console 本地日志 [来源: github.com/Portkey-AI/gateway]）
- **指标**：请求量、token 量、成本、错误率、延迟（Kong LLM metrics + OTLP [来源: docs.konghq.com]；Cloudflare analytics [来源: developers.cloudflare.com]）
- **追踪**：OpenTelemetry 集成（Kong Gen AI OTLP span attributes [来源: docs.konghq.com]；LiteLLM callbacks → Langfuse/MLflow/Helicone [来源: docs.litellm.ai]）

### 4.10 MCP 与 A2A 网关（2025-2026 新增）

2025 下半年起，网关从"LLM 代理"升级为"Agent 基础设施"：

- **MCP（Model Context Protocol）网关**：集中管理 MCP server，做统一认证/访问控制/可观测
  - Portkey MCP Gateway：单层认证、团队/用户级访问控制、工具调用全日志、身份转发 [来源: github.com/Portkey-AI/gateway]
  - LiteLLM MCP Gateway：中央 MCP endpoint + per-key 访问控制 [来源: docs.litellm.ai]
  - Higress MCP：MCP 请求协议卸载、统一身份认证/流量调度/参数映射/安全审计（阿里 HSF/Dubbo → MCP 转换）[来源: higress.cn]
- **A2A（Agent2Agent）网关**：治理 Agent 间通信
  - Kong A2A 支持（secure/govern/observe A2A traffic）[来源: docs.konghq.com]
  - LiteLLM A2A Agent 网关 [来源: docs.litellm.ai]

> **趋势判断**：MCP/A2A 正在成为网关的"第二增长曲线"。选择网关时，**MCP 支持深度**应作为 2026 年的必选项而非加分项。

---

## 5. 产品功能详细对比

### 5.1 开源阵营

#### LiteLLM（BerriAI）—— 开发者生态之王

| 维度 | 详情 |
|:-----|:-----|
| 形态 | Python SDK + 自托管 Proxy Server（AI Gateway） |
| 星标 | 56.5k stars / 10.7k forks [来源: github.com/BerriAI/litellm] |
| 架构 | **Rust 核心 + Python SDK**（2025 重构），8ms P95 @1k RPS [来源: github.com/BerriAI/litellm] |
| Provider | 100+ LLM（OpenAI/Anthropic/Bedrock/Azure/Vertex/vLLM/NVIDIA NIM 等） |
| 端点 | /chat/completions、/responses、/embeddings、/images、/audio、/batches、/rerank、/a2a |
| 核心能力 | 虚拟 Key + 预算、成本追踪、guardrails、负载均衡、Admin UI、Terraform（AWS/GCP）、Helm |
| MCP/A2A | ✅ MCP Gateway + A2A Agent |
| 部署 | Docker/Helm/Terraform，托管 Postgres+Redis+对象存储组件化架构 |
| 商业 | Enterprise（SSO/审计日志/优先支持），云托管 Hosted Proxy |
| 采用者 | Netflix 等 [来源: github.com/BerriAI/litellm] |

**优势**：生态最大、文档最全、SDK+网关双形态、Terraform 一键上云。
**劣势**：功能多导致配置复杂度高；企业版能力（SSO 等）需付费。

#### Portkey AI Gateway —— 轻量极速 + 护栏

| 维度 | 详情 |
|:-----|:-----|
| 形态 | 开源网关（Node.js/TypeScript）+ 托管云 |
| 星标 | 12.7k stars / 1.2k forks [来源: github.com/Portkey-AI/gateway] |
| 性能 | <1ms 延迟、122KB footprint、每日处理 10B+ token [来源: github.com/Portkey-AI/gateway] |
| Provider | 250+ LLM、1600+ 模型（含 vision/audio/image 多模态） |
| 核心能力 | 5 次重试/指数退避、fallback、负载均衡、40+ guardrails、简单+语义缓存、RBAC、Agent 框架集成（LangChain/CrewAI/Autogen 等 8+） |
| MCP | ✅ MCP Gateway（认证/访问控制/可观测/身份转发） |
| 商业 | Enterprise（私有云 AWS/Azure/GCP/OpenShift/K8s、SOC2/ISO/HIPAA/GDPR） |
| 许可 | MIT |

**优势**：极低延迟、轻量部署、护栏生态强、Agent 框架适配广。
**劣势**：社区规模小于 LiteLLM；语义缓存/provider optimization 等高级能力在 enterprise 版。

#### One-API（songquanpeng）—— 国产分发之王

| 维度 | 详情 |
|:-----|:-----|
| 形态 | 单可执行文件（Go）+ Docker，开箱即用 |
| 星标 | 36.4k stars / 6.8k forks [来源: github.com/songquanpeng/one-api] |
| Provider | OpenAI/Azure/Claude/Gemini/DeepSeek/豆包/ChatGLM/文心/通义/讯飞/360/混元/Moonshot/百川/MINIMAX/Groq/Ollama/零一/阶跃/Coze/Cohere/硅基流动/xAI 等 [来源: github.com/songquanpeng/one-api] |
| 核心能力 | 令牌管理（过期/额度/IP/模型）、兑换码充值、渠道分组+用户分组+倍率、模型映射、失败自动重试、多机部署（主从+Redis）、额度明细 |
| 适用场景 | **国内个人/小团队/自用分发**：一个 key 分发全家，对接各种 OpenAI 兼容客户端 |
| 许可 | MIT |

**优势**：国产模型覆盖最全、部署最简单（单二进制）、二次分发体系成熟（兑换码/邀请奖励/用户分组）。
**劣势**：路由/缓存/护栏等企业级能力弱于 LiteLLM/Portkey；定位偏"key 管理分发"而非"企业 AI 治理平台"。

#### Higress（阿里开源，CNCF Sandbox）—— 云原生 AI 网关

| 维度 | 详情 |
|:-----|:-----|
| 形态 | 云原生 API 网关（基于 Envoy + Istio 生态），开源 + 企业版 |
| 定位 | "AI Native API Gateway"——传统流量 + AI 流量统一治理 |
| Provider | 100+ 模型统一协议转换、模型级 Fallback [来源: higress.cn] |
| 核心能力 | AI 缓存（精确+语义）、Token 管控、消费者认证、多模型代理、应用防护（输入隐私保护+输出内容过滤）、MCP（协议卸载/认证/调度/审计）[来源: higress.cn] |
| 生态 | wasm 插件体系、集成 Nacos/Spring Cloud Alibaba/Dubbo 等国产中间件 |
| 客户 | 携程、快手、极氪、君润人力、政采云、阿里巴巴（SOFA AI 网关基于 Higress 内核）[来源: higress.cn] |
| 商业 | 企业版：99.95% SLA、性能优化 90%+、节省 50% 资源成本 [来源: higress.cn] |

**优势**：**国内企业落地案例最扎实**（携程/快手等）、云原生（K8s/Envoy）、MCP 落地深入（阿里 HSF/Dubbo → MCP）、国产中间件生态。
**劣势**：上手门槛高于 One-API/LiteLLM（需要 K8s/Envoy 知识）；国际化弱于 LiteLLM。

#### Envoy AI Gateway（CNCF）—— 云原生标准化路线

| 维度 | 详情 |
|:-----|:-----|
| 形态 | 基于 Envoy Gateway 的 K8s 原生 AI 网关 |
| 星标 | 1.9k stars [来源: github.com/envoyproxy/ai-gateway] |
| 架构 | **双层网关**：Tier-1 集中入口（认证/顶层路由/全局限流）+ Tier-2 自托管模型集群入口（端点选择器/推理优化）[来源: github.com/envoyproxy/ai-gateway] |
| Provider | OpenAI/Azure/Gemini/Vertex/Bedrock/Mistral/Cohere/Groq/Together/DeepInfra/DeepSeek/Hunyuan/SambaNova/Grok/Anthropic 等 |
| 定位 | **K8s 平台团队**：让 AI 流量治理进 Service Mesh 体系 |
| 许可 | Apache-2.0 |

**优势**：与 K8s/Envoy 生态天然融合、双层架构适合自托管推理集群、CNCF 治理背书。
**劣势**：功能成熟度低于上述产品（路由/缓存/护栏偏基础）、需要较强 K8s 能力。

### 5.2 商业/托管阵营

#### OpenRouter —— 模型超市 + 自动路由

| 维度 | 详情 |
|:-----|:-----|
| 形态 | 托管聚合平台（SaaS） |
| 定位 | **模型超市**：数百模型一个 API 端点，自动 fallback、自动选最经济模型 [来源: openrouter.ai/docs] |
| 核心能力 | 单 API 访问数百模型、自动 fallback、成本最优选择、免费模型、~alias（gpt-latest 自动解析最新旗舰）、MCP server、SDK（JS/Python）、排行榜 |
| 场景 | 开发者快速对比/切换模型、个人应用聚合 |
| 特点 | **开箱即用无需部署**；是"网关即服务"的消费端形态 |

**与自建网关关系**：OpenRouter 可视为"别人帮你运营的网关"——适合不想运维、追求模型选择灵活性的团队；但它不解决企业内部的成本分摊/审计/数据主权问题。

#### Kong AI Gateway —— 传统 API 网关的 AI 化

| 维度 | 详情 |
|:-----|:-----|
| 形态 | Kong Gateway（开源/企业版 Konnect）上的 AI 插件族 |
| 核心插件 | AI Proxy、AI Proxy Advanced（多目标负载均衡）、AI Prompt Guard、AI Semantic Prompt Guard、AI PII Sanitizer（20 类 9 语言）、AI Prompt Template/Decorator、AI RAG Injector、AI Request/Response Transformer、AI Prompt Compressor、AI LLM as Judge [来源: docs.konghq.com] |
| 路由 | 一致哈希/最低延迟/用量/轮询/语义匹配负载均衡 [来源: docs.konghq.com] |
| 护栏 | Azure Content Safety / AWS Guardrails / GCP Model Armor / Lakera Guard / Custom Guardrail [来源: docs.konghq.com] |
| MCP/A2A | ✅ MCP traffic gateway + A2A traffic gateway |
| 商业化 | 计量计费（Stripe/ERP 集成）、Konnect 控制面、99.95% SLA 级别企业能力 |
| 场景 | **已有 Kong 的企业**：把 AI 治理纳入现有 API 治理体系 |

**优势**：插件生态最全（AI 治理全栈）、与既有 API 网关统一管理、计量计费成熟。
**劣势**：需要已有 Kong 体系才有意义；AI 专项能力（语义缓存/护栏）分散在多个插件，配置面大。

#### Cloudflare AI Gateway —— 全球边缘网络 AI 观测层

| 维度 | 详情 |
|:-----|:-----|
| 形态 | 托管服务（所有套餐可用），一行代码接入 |
| 核心能力 | 分析/日志、缓存、限流、请求重试+模型回退、统一计费、DLP、Guardrails、BYOK、自定义域名、OpenTelemetry [来源: developers.cloudflare.com/ai-gateway] |
| Provider | Workers AI、OpenAI、Anthropic、Gemini、Groq、Mistral、Replicate 等 + OpenRouter 转发 |
| 定位 | **全球边缘**：利用 CF 网络就近接入，统一观测与控制 |
| 场景 | 全球分发应用、已有 CF 生态的团队 |

**优势**：零部署（改 base_url 即可）、全球边缘低延迟、与 Workers/Vectorize 生态整合。
**劣势**：企业内部治理（预算分摊/细粒度 RBAC）弱于自建网关；数据经 CF 网络。

### 5.3 核心对比矩阵

| 维度 | LiteLLM | Portkey | One-API | Higress | Envoy AI GW | OpenRouter | Kong | Cloudflare |
|:-----|:--------:|:-------:|:-------:|:-------:|:-----------:|:----------:|:----:|:----------:|
| 形态 | 自托管 | 自托管+云 | 自托管 | 自托管+企业版 | 自托管(K8s) | 托管SaaS | 自托管+云 | 托管SaaS |
| 开源 | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | 核心✅ | ❌ |
| 许可 | MIT* | MIT | MIT | Apache-2.0 | Apache-2.0 | 商业 | Apache-2.0 | 商业 |
| 星标 | 56.5k | 12.7k | 36.4k | — | 1.9k | — | — | — |
| 延迟 | 8ms@1k RPS | <1ms | — | — | — | — | — | — |
| Provider数 | 100+ | 250+/1600+模型 | 30+ | 100+ | 15+ | 数百模型 | 多 | 10+ |
| 语义缓存 | 部分 | ✅企业 | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ |
| 护栏 | ✅ | 50+ | ❌ | ✅ | ❌ | ❌ | 全栈 | ✅DLP |
| 虚拟Key/预算 | ✅ | ✅ | ✅ | ✅ | — | — | ✅ | — |
| 成本追踪 | ✅ | ✅ | ✅额度 | ✅Token | — | ✅ | ✅计量 | ✅ |
| MCP | ✅ | ✅ | ❌ | ✅ | — | ✅(server) | ✅ | ❌ |
| A2A | ✅ | — | ❌ | — | — | — | ✅ | ❌ |
| 国产模型 | 部分 | 部分 | **全** | **全** | DeepSeek等 | 部分 | 部分 | 部分 |
| 国内落地 | — | — | 广 | **携程/快手等** | — | — | — | — |
| 部署难度 | 中 | 低 | **极低** | 中高 | 高 | 零 | 中 | 零 |

> *LiteLLM 开源核心 MIT，企业功能（SSO/审计）需商业许可。

### 5.4 分场景胜出者

| 场景 | 首选 | 次选 | 理由 |
|:-----|:-----|:-----|:-----|
| 个人/小团队 Key 分发（国产为主） | **One-API** | LiteLLM | 单二进制、国产全覆盖、兑换码体系 |
| 开发者生态/多语言团队 | **LiteLLM** | Portkey | 最大生态、SDK+网关、Terraform |
| 企业级治理（预算/审计/SSO） | **LiteLLM Ent / Portkey Ent** | Kong | 虚拟Key+预算+审计原生 |
| 已有 Kong 的企业 | **Kong AI Gateway** | Higress | 复用现有插件/治理体系 |
| K8s 平台团队（自托管推理集群） | **Envoy AI Gateway** | Higress | 双层架构契合自托管集群 |
| 国内企业（云原生栈） | **Higress** | One-API | 携程/快手案例、国产中间件生态 |
| 全球应用/边缘低延迟 | **Cloudflare** | OpenRouter | 零部署、边缘网络 |
| 快速验证/模型对比 | **OpenRouter** | Cloudflare | 模型超市、零部署 |

---

## 6. 选型决策框架

### 6.1 决策树

```
Q1: Do you want to self-host the gateway?
|-- NO  (managed)
|   |-- Global/edge distribution -> Cloudflare AI Gateway
|   +-- Model compare / quick trial  -> OpenRouter
|
+-- YES (data sovereignty / cost / customization)
    |-- Q2: Existing tech stack
    |   |-- Have Kong        -> Kong AI Gateway
    |   |-- K8s platform     -> Envoy AI Gateway
    |   |-- CN cloud-native  -> Higress
    |   +-- Other
    |       +-- Q3: Team size
    |           |-- Individual/small (CN models) -> One-API
    |           +-- Team/enterprise
    |               |-- Need SSO/audit/support -> LiteLLM Enterprise
    |               +-- Minimal/multimodal/guardrails -> Portkey
    +-- (Hybrid: open-source gateway + managed SaaS, split by env)
```

（中文对照：Q1=是否自运维网关；NO→Cloudflare/OpenRouter；YES→按技术栈与团队规模选型，详见 5.4 分场景胜出者）

### 6.2 落地路径建议

**推荐渐进路线（企业）**：
1. **阶段一（0-3月）**：LiteLLM（或 One-API，若国产为主）单实例部署 → 统一 3-5 个主力模型 → 虚拟 Key 分发给各团队 → 建立成本基线
2. **阶段二（3-6月）**：接入语义缓存 + 护栏 → 按团队预算管控 → 对接可观测（Langfuse/OTel）
3. **阶段三（6月+）**：评估 MCP 网关需求 → 自托管推理集群接入（Envoy AI GW 双层架构或 Higress）→ 逐步将高频流量迁到自托管降本

**关键选型指标**（权重建议）：
| 指标 | 权重 | 理由 |
|:-----|:----:|:-----|
| 协议/Provider 覆盖 | 30% | 决定长期可接入性 |
| 预算/成本治理 | 25% | 混合模型环境成本失控是最大痛点 |
| 延迟开销 | 15% | 网关是每请求必经之路 |
| MCP/Agent 支持 | 15% | 2026 年 Agent 化刚需 |
| 部署运维成本 | 15% | 影响团队负担 |

---

## 7. 趋势研判

1. **网关 = Agent 基础设施**：MCP/A2A 支持从"附加功能"变为"核心能力"，网关将管理的不只是 LLM，还有工具、Agent、上下文（LiteLLM/Portkey/Higress/Kong 均已布局）。
2. **语义化治理**：从"URL 级"到"语义级"——语义缓存、语义路由、语义护栏成为差异化竞争力。
3. **开源 + 企业版双轨**：核心开源、治理能力（SSO/审计/高级缓存）商业化，LiteLLM/Portkey/Higress 均走此路。
4. **自托管与托管的混合**：企业将同时使用"托管主力模型 + 自托管长尾模型"，网关是两者之间的唯一统一层——这正是网关的战略卡位。
5. **延迟竞争白热化**：Rust 化（LiteLLM）、<1ms（Portkey）、边缘化（Cloudflare）——网关自身性能成为选型硬指标。

---

## 参考文件

### 外部资料引用

[1] LiteLLM 官方文档 & GitHub: [docs.litellm.ai](https://docs.litellm.ai) / [github.com/BerriAI/litellm](https://github.com/BerriAI/litellm)（56.5k stars，8ms P95@1kRPS，100+ providers，2026-08 访问）
[2] Portkey AI Gateway: [github.com/Portkey-AI/gateway](https://github.com/Portkey-AI/gateway)（12.7k stars，<1ms，250+ LLM，50+ guardrails，MCP Gateway）
[3] One-API: [github.com/songquanpeng/one-api](https://github.com/songquanpeng/one-api)（36.4k stars，国产全覆盖，单二进制，兑换码体系）
[4] Higress 官网: [higress.cn](https://higress.cn)（100+ 模型协议转换，语义缓存，Token 管控，携程/快手/极氪案例，CNCF Sandbox）
[5] Envoy AI Gateway: [github.com/envoyproxy/ai-gateway](https://github.com/envoyproxy/ai-gateway)（1.9k stars，双层网关架构，Apache-2.0）
[6] OpenRouter 文档: [openrouter.ai/docs](https://openrouter.ai/docs)（数百模型单 API，自动 fallback，~alias）
[7] Kong AI Gateway 文档: [docs.konghq.com/gateway/latest/ai-gateway](https://docs.konghq.com/gateway/latest/ai-gateway/)（AI 插件族，语义路由/缓存，MCP/A2A，计量计费）
[8] Cloudflare AI Gateway: [developers.cloudflare.com/ai-gateway](https://developers.cloudflare.com/ai-gateway/)（一行接入，缓存/限流/重试/回退，DLP，边缘网络）

### 内部知识库引用

[9] [推理 GPU 容量 SKU 战略框架](2026-08-11-inference-gpu-capacity-sku-strategy-framework.md) — 推理容量型 SKU 战略（自托管推理集群硬件底座）
[10] [单位 token 成本五看三定](2026-08-13-unit-token-cost-five-looks-three-decisions-deep-analysis.md) — token 成本定价模型（SaaS API 单价基线）
[11] [DeepSeek 8T 日 TCO 分析](2026-08-14-deepseek-8t-daily-tco-analysis.md) — DeepSeek 8T 模型日成本测算（自托管经济性基线）

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-17 | v1.0 | 首次创建：服务提供方式全景 + 网关 10 大机制 + 8 产品对比 + 选型框架 |
