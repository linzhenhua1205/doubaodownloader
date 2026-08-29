<!-- AUTO-GENERATED: 由 AI 深度分析生成，2026-08-11。修改请走编辑流程并更新 changelog。 -->

# 💰 模型侧降本三路径深度分析：推理经济学的三层杠杆

> **一句话结论**：模型侧降本不是三个并列选项，而是**一条从软件到硬件的降本梯度**——先路由（换便宜模型，零沉没成本、30× 价差立竿见影），再稀疏化（MoE 激活裁剪，结构性降计算量），最后专用化（模型进硅，tokens/W 提升 6-10× 但耦合模型迭代节奏）。中国模型占美企 token 30% + Coinbase 支出砍半是**路径一的实证**；Thinking Machines 41B/975B 激活是**路径二的锚点**；Trainium $25B run-rate 与 Google Frozen v2 是**路径三的商业化与前沿信号**。

---

## 📋 文档信息

| 项目 | 内容 |
|:-----|:-----|
| **主题** | 模型侧降本三路径（便宜替代 / 稀疏定制 / 高效加速器） |
| **日期** | 2026-08-11 |
| **分析者** | 小龙猫 (AI) |
| **主来源** | Geoff Tate《How Data Center AI Can Keep Growing, Despite Supply Chain Bottlenecks》（SemiEngineering, 2026-08-10）|
| **交叉验证** | Thinking Machines Inkling 官方/第三方确认（975B/41B 激活）|
| **关联文档** | [geoff-tate 源文件归档](../../06_others/sources/2026-08-11-geoff-tate-data-center-ai-supply-chain-bottlenecks-opinion.md)、[推理 GPU 容量型 SKU 战略框架](2026-08-11-inference-gpu-capacity-sku-strategy-framework.md)、[模型能力对比与使用策略](../../03_AI/llm-techniques-principles/2026-08-03-model-capability-comparison-usage-strategy.md) |
| **TOC** | ✅ 本文档含目录 |

## 📑 目录

1. [执行摘要](#1-执行摘要)
2. [原始信息介绍（数据点 → 来源映射）](#2-原始信息介绍数据点--来源映射)
3. [路径一：便宜模型替代——模型路由经济学](#3-路径一便宜模型替代模型路由经济学)
4. [路径二：稀疏化与定制——MoE 激活与任务裁剪](#4-路径二稀疏化与定制moe-激活与任务裁剪)
5. [路径三：高效加速器——专用芯片与模型进硅](#5-路径三高效加速器专用芯片与模型进硅)
6. [统一框架：三路径的 $/token 分解](#6-统一框架三路径的-token-分解)
7. [对服务器产品线的含义](#7-对服务器产品线的含义)
8. [可证伪预测](#8-可证伪预测)
9. [数据源注册表与缺口声明](#9-数据源注册表与缺口声明)
10. [Changelog](#10-changelog)

---

## 1. 执行摘要

### 1.1 三路径全景（数据锚点）

| 路径 | 机制 | 关键数据 | 成本结构影响 | 沉没成本 |
|:-----|:-----|:---------|:-------------|:--------:|
| **① 便宜模型替代** | 模型路由：简单任务 → 便宜模型 | GPT-5.5 $30/M vs DeepSeek V4 <$1/M（**>30× 价差**）；Coinbase 换中国模型支出**砍半**；中国模型占美企 token **30%**；OpenRouter top10-by-tokens 中国占 **8/10** | 每 token 单价 ↓ | 低（API 层切换） |
| **② 稀疏化/定制** | MoE 激活裁剪 + SLM 任务定制 | Thinking Machines 975B 总参仅 **41B active**（<5%）；SLM 可本地跑（2028 Mac Studio M7 Ultra 支持 >1T 参数） | 每任务计算量 ↓ | 中（模型层） |
| **③ 高效加速器** | 专用芯片 + 模型进硅 | Trainium 收入 run-rate **>$25B/年**；Google Frozen v2 硬编码 Gemini 进硅，**6-10× tokens/W**，目标 2028 | 每 token 硬件+电力成本 ↓ | 高（硬件层） |

### 1.2 核心洞察

1. **三路径是嵌套梯度而非并列选项**：先路由（软件，零沉没成本）→ 再稀疏化（模型结构）→ 最后专用化（硬件）。越往下游边际成本越低，但灵活性越差、耦合越深
2. **路径一已被市场用脚投票**：中国模型占美企 token 30% 是**地缘逆风下的纯经济行为**——30× 价差压过一切非经济顾虑；这是国产模型"软件侧出海"的硬证据
3. **路径三是兵家必争之地**：Trainium $25B（对 NVIDIA DC $193.7B 约 **13%** 占位）+ Frozen v2"模型进硅"= 定制芯片从"补充"走向"主战场"；但**模型进硅有一个致命时差**：2028 发布的 Frozen v2 固化的是 2027 年的 Gemini——模型迭代快于硅片流片
4. **对服务器厂商**：三路径共同指向**推理 SKU 分化**（容量型/带宽型/通用型）+ **tokens/W 成为推理芯片第一指标**（比 FLOPS 更贴业务）

---

## 2. 原始信息介绍（数据点 → 来源映射）

> 主来源为 Geoff Tate（前 Rambus/Flex Logix CEO）2026-08-10 SemiEngineering 专栏，全文已归档。以下为"模型侧降本三路径"相关数据点的完整映射与可信度分级。

### 2.1 数据点映射表

| # | 数据点 | 原文出处 | 一手/二手 | 可信度 |
|:--|:-------|:---------|:---------:|:------:|
| 1 | GPT-5.5 $30/M、GPT-5.4 $15/M、DeepSeek V4 <$1/M | OpenRouter（Tate 引用） | 二手（可公开验证） | 🟢 高 |
| 2 | Coinbase CEO Brian Armstrong 6 月在 X：默认模型=智谱 GLM 5.2 + 月之暗面 Kimi K2.7 → 内部 AI 支出砍半 | Tate 转述 Armstrong X 帖 | 二手（原始 X 帖可查） | 🟢 高 |
| 3 | OpenRouter 估值 $1.3B | Tate | 二手 | 🟡 中 |
| 4 | OpenRouter Leaderboard（7 月下旬）top10-by-tokens 中国占 8 席（另 2 席=NVIDIA Nemotron 3 + Anthropic Claude Opus 4.8） | OpenRouter Leaderboard（Tate 引用） | 二手（可公开验证） | 🟢 高 |
| 5 | 中国模型占美企 token 30%（自 2 月起） | William Blair（Tate 引用） | 二手（投资机构报告） | 🟡 中（口径未披露） |
| 6 | Thinking Machines 首个模型近 1T 参数仅 41B active | Wall Street Journal（Tate 引用） | 二手 | 🟢 已交叉验证：Inkling=975B/41B 激活（datalearner/36kr/官方） |
| 7 | Thinking Machines 定制工具 Tinker | Tate | 二手 | 🟢 高（官方产品） |
| 8 | SLM 本地化：未来 iPhone/Mac（2028 Mac Studio M7 Ultra 支持 >1T 参数模型） | Tate | 二手（Apple 路线图传闻） | 🟡 中 |
| 9 | Amazon 财报电话会：Trainium 收入 run-rate 超 $25B/年 | Amazon 财报（Tate 引用） | 一手（财报电话会） | 🟢 高 |
| 10 | Google Frozen v2：硬编码 Gemini 部分进硅，目标 2028，6-10× tokens/W | The Information（Tate 引用） | 二手（付费媒体独家） | 🟡 中（细节未公开） |
| 11 | NVIDIA $20B 许可 Groq 技术；Cerebras 上市 $42B 市值 | Tate | 二手 | 🟡 中 |
| 12 | Anthropic ARR/MW 9 个月 4× | SemiAnalysis（Tate 引用） | 二手 | 🟡 中 |

### 2.2 交叉验证记录

| 数据点 | 验证动作 | 结果 |
|:-------|:---------|:-----|
| Thinking Machines 41B active | 抓取 datalearner/36kr/腾讯新闻（2026-07-16） | ✅ **Inkling = 975B 总参 / 41B 激活** MoE 多模态开放权重，1M 上下文，训练 45 万卡时——用户描述"~1T/41B"与官方一致 |
| GPT-5.5 vs DeepSeek V4 价差 | 知识库 [2026-08-03 模型能力对比](../../03_AI/llm-techniques-principles/2026-08-03-model-capability-comparison-usage-strategy.md) 有 AA 价格基线 | ✅ 价格量级一致（DeepSeek V4 显著低于头部闭源） |
| 中国模型 8/10 top-tokens | OpenRouter Leaderboard 公开页面 | ⚠️ 未能直连（网络限制），依赖 Tate 转述 + 记忆锚点（OpenRouter top10-by-tokens 中国占 8 席已在 MEMORY.md） |

### 2.3 作者与立场披露

Geoff Tate 为前 Rambus CEO（内存接口 IP 公司）、前 Flex Logix CEO（AI 推理芯片公司）——**立场偏向"效率优化"与"大厂受益"叙事**，且作为芯片老兵对定制芯片赛道有产业视角。潜在偏差：低估中小企业资源获取难度、将结构性瓶颈（电力/地缘）轻描淡写为"效率可解"、未充分讨论模型替换的性能折损与迁移成本（源文件 L94 自评）。

---

## 3. 路径一：便宜模型替代——模型路由经济学

### 3.1 机制：任务-模型匹配取代"一刀切用最强模型"

前沿模型对简单任务是**过杀（overkill）**。Tate 原话："The more expensive models give better results on the toughest tasks, but not all tasks need the best models."

```
Task-Model Matching (model routing):

  request --> router --> GPT-5.5 ($30/M)  for hardest tasks (agentic, coding, reasoning)
              (rules     |--> GPT-5.4 ($15/M)  for standard tasks
               or ML)    |--> DeepSeek V4 (<$1/M) for high-volume simple tasks
                         `--> SLM (local, ~$0)  for fixed repetitive tasks
```

### 3.2 数据实证：价格梯度就是需求梯度

| 层级 | 模型 | 价格（$/M tokens） | 相对 GPT-5.5 | 适用 |
|:-----|:-----|:------------------:|:------------:|:-----|
| 顶级 | GPT-5.5 | $30 | 1× | 最难任务 |
| 次顶级 | GPT-5.4 | $15 | 0.5× | 标准任务 |
| 开源高性价比 | DeepSeek V4 | <$1 | <1/30× | 高频简单任务 |
| 本地 | SLM | ~0（硬件成本） | ~0 | 固定重复任务 |

**价差 >30× 是需求迁移的物理驱动力**——当两个模型在目标任务上表现可接受，理性企业必然选便宜者。

### 3.3 标志性案例：Coinbase

> Coinbase CEO Brian Armstrong 6 月在 X 透露：**将工程师默认模型设为智谱 GLM 5.2 和月之暗面 Kimi K2.7 后，内部 AI 支出近乎砍半**。

**案例解剖**：
- **决策层**：CEO 亲自定默认模型——降本已上升到公司级战略，非团队级优化
- **选型逻辑**：GLM 5.2 / Kimi K2.7 是**中国开源模型**（vs DeepSeek V4 也上榜）——选择标准是"能力达标 × 价格 × 可用性"而非地缘偏好
- **量化**：支出砍半 ≈ 内部 token 量不变（或增长）前提下单价降 ~50%——与 30× 价差相比仍保守（说明部分任务仍需闭源模型，混合路由）
- **信号**：美国上市公司公开采用中国模型 = **经济理性压倒地缘顾虑的公开背书**

### 3.4 市场级证据：中国模型占美企 token 30%

| 证据 | 数值 | 解读 |
|:-----|:-----|:-----|
| 中国模型占美企 token 份额（William Blair，自 2 月） | **30%** | 美国企业每 10 个 token 有 3 个由中国模型产生 |
| OpenRouter top10-by-tokens（7 月下旬） | **8/10 中国模型** | 头部流量几乎被中国开源模型垄断（另 2 席：NVIDIA Nemotron 3、Anthropic Claude Opus 4.8） |
| OpenRouter 估值 | $1.3B | 模型路由中间层获资本认可 |

**第一性原理解读**：token 份额迁移的本质是**"能力/价格"比率的市场竞争**——中国开源模型以接近前沿的能力、1/30 的价格、开放权重（可自托管规避数据出境），在"够用即可"的大多数任务上形成碾压性性价比。这不是补贴或倾销，是**成本结构优势**（训练成本、工程效率、无闭源垄断定价）。

### 3.5 边界与风险

1. **性能折损**：最硬任务仍需顶级闭源——30% 份额是"够用"任务的天花板，不是全面替代
2. **地缘政策风险**：美国对华 AI 政策（如 FCC 光模块禁令的先例）可能限制中国模型 API 使用——企业需评估合规敞口
3. **路由复杂度**：多模型运维（质量波动、供应商锁定）需要 OpenRouter 类中间层——自研路由器的成本常被低估
4. **价格粘性**：$30/M 是"思维链成本"定价（推理 token 消耗大），简单任务路由省的是**总账单**而非单模型价格

---

## 4. 路径二：稀疏化与定制——MoE 激活与任务裁剪

### 4.1 机制：从"全量计算"到"按需激活"

```
Dense model:  1T params, EVERY query activates ALL 1T    (compute = f(params))
MoE model:    975B params, only 41B "active" per query   (compute = f(active))
SLM:          task-specific small model, only what you need (compute = f(task scope))
```

### 4.2 锚点案例：Thinking Machines Inkling（41B/975B）

| 维度 | 数据 | 来源 |
|:-----|:-----|:-----|
| 总参数量 | 975B（近 1T） | Thinking Machines 官方 + 第三方 |
| 激活参数 | **41B（<5%）** | WSJ（Tate 引用）+ datalearner/36kr 交叉验证 |
| 架构 | 多模态 MoE（文本/图像/音频） | 官方 |
| 上下文 | 1M tokens | 官方 |
| 训练规模 | ~45 万卡时 | 36kr |
| 定制工具 | Tinker（易微调） | 官方 |
| 创始人 | Mira Murati（前 OpenAI CTO） | — |
| 定位 | "balancing cost and performance over raw power"（平衡成本性能，非堆绝对算力） | Tate/WSJ |

**为什么 41B active 是降本利器**（第一性原理）：
- 推理计算量 ≈ 激活参数 × token 数（前向传播只走 active 路径）
- 975B 总参的**知识容量**（容量在权重里，支持 1M 上下文）几乎不损失
- 单 query 计算成本 ≈ 41B 模型的成本——**"大模型的知识，小模型的单价"**
- 代价：MoE 路由开销 + 专家间通信（All-to-All）+ 内存驻留（权重全量驻留，975B 需 ~2TB bf16 或 ~500GB NVFP4）——**容量型 SKU（大内存）的直接需求来源**

**与 MEMORY 的互证**：Inkling 借鉴 DeepSeek 和 Kimi 架构（36kr）——中国模型的 MoE 工程（DeepSeek V4、Kimi K2.7）已成为全球开源新范式；"稀疏化"路径本质是**中国模型工程方法论的世界性扩散**。

### 4.3 SLM 本地化：任务的极端裁剪

Tate 案例：虚拟助手只处理英西双语电话 + 简单任务 → SLM 只训练所需 → 模型大幅缩小 → **本地运行**（未来 iPhone/Mac 甚至 2028 Mac Studio M7 Ultra 支持 >1T 参数模型）。

**本地化的三重降本**：
1. 推理成本归零（无 API 费，仅硬件+电费）
2. 延迟最低（无网络往返）
3. 数据不出域（合规收益）

**产业含义**：SLM 本地化 + 端侧算力提升（M7 Ultra）→ 推理从"云端集中"向"端云分层"演进——**这直接改变服务器推理市场结构**：大量简单任务不再上云，服务器推理聚焦中高复杂度任务。

### 4.4 边界与风险

1. **容量-激活矛盾**：41B active 需驻留 975B 权重——内存带宽/容量成为新瓶颈（与 MEMORY「KV 四层命运论」互证）
2. **路由开销**：MoE 的 expert routing 本身有计算+通信成本（小 batch 时不划算——NVIDIA 明确 dense 在端侧更优，见 Meta Glimmer 30B dense 官方解读）
3. **定制成本**：Tinker/SLM 需要数据+工程投入，小企业未必回本
4. **生态锁定**：MoE 权重结构与硬件（NVFP4、稀疏内核）强耦合——换硬件=重优化

---

## 5. 路径三：高效加速器——专用芯片与模型进硅

### 5.1 机制：从"通用 GPU 兜底"到"专用芯片降本"

```
GPU (general-purpose): runs any model, but designed for worst case (generic = redundant)
TPU/Trainium (purpose-built): optimized for specific training/inference patterns,
                              better throughput/$ and throughput/W
Frozen v2 (model-in-silicon): hard-codes parts of Gemini into silicon, 6-10x tokens/W
```

### 5.2 商业化验证：Trainium run-rate >$25B/年

| 维度 | 数据 | 意义 |
|:-----|:-----|:-----|
| Trainium 收入 run-rate | **>$25B/年**（Amazon 财报电话会） | 定制芯片从"内部自用"走向"独立收入引擎" |
| 对比 NVIDIA DC 收入 | $193.7B（FY2026，知识库实测） | Trainium ≈ NVIDIA DC 的 **13%** 占位 |
| AWS 内部负载声明 | 自研芯片 throughput/$ 和 throughput/watt 更优 | 定制化的核心论据：只为自家负载优化 |
| 对外销售 | Google×Anthropic/Meta；Amazon×Anthropic/OpenAI | **定制芯片外销成为新商业模式**——hyperscaler 从"卖云"到"卖算力+卖芯片" |
| Google TPU | 十年积累，全面 ramp | 与 Trainium 形成双雄 |

**为什么 $25B 重要**：这是**定制芯片商业闭环的第一个公开大数**——证明"为特定模型/负载定制硬件"的商业模式跑通了。13% 占位看似小，但在 NVIDIA 垄断的推理市场，这是从 0 到 1 的突破（对比 AMD MI 系列长期 <10%）。

### 5.3 前沿信号：Google Frozen v2——模型进硅

| 维度 | 数据 | 来源 |
|:-----|:-----|:-----|
| 代号 | Frozen v2 | The Information（Tate 引用） |
| 机制 | 把 Gemini 模型**部分硬编码进硅**（hard-code parts of the model into silicon） | The Information |
| 目标 | **6-10× tokens/W** vs 当前硬件 | The Information |
| 发布窗口 | 最早 2028 | The Information |
| 战略意图 | 对跑在 Gemini 架构上的负载大幅降本降耗；**最大化 TSMC wafer 分配的 compute 产出** | Tate |

**"模型进硅"的三层解读**：
1. **技术层**：把推理热路径（attention、FFN 的固定部分、量化矩阵）固化为专用电路——类似"软件 2.0 的终极形态"（模型即硬件）
2. **战略层**：Google 的算力瓶颈不是设计而是 **TSMC wafer 分配**——同样的晶圆产出，tokens/W 提升 6-10× = 等效 wafer 供给放大 6-10×（对给定 Gemini 负载）——**这是对供应链约束的硬件级回应**（呼应 Tate 全文主线"supply chain bottlenecks → efficiency"）
3. **风险层**：**模型-硅片时差**——2028 流片的芯片固化 2027 年的模型结构；若 Gemini 架构大改（如新注意力机制），Frozen v2 即过时。这正是"硬编码"的代价：**把可迭代的软件锁进不可迭代的硅**

### 5.4 生态全景（Tate 列举）

| 玩家 | 动作 | 数据 |
|:-----|:-----|:-----|
| NVIDIA | 每代 GPU 更高效；Vera Rubin 更多 tokens/$ 和 tokens/W；Vera CPU 为 agentic AI 优化 | 黄仁勋"Rubin 推理成本 -10×"（知识库实测） |
| NVIDIA×Groq | $20B 许可 Groq 技术 | SRAM 无 HBM 架构 |
| Cerebras | 上市，$42B 市值（7 月底） | 无 HBM + 大量 SRAM，高响应 |
| OpenAI | 自研加速器（Broadcom 合作） | 模型厂自研芯片第二家 |
| Anthropic | 传闻探索自研芯片 | 第三家 |
| 自研 CPU | NVIDIA Vera、Amazon Graviton | 声称比 x86 高效 20-50% |
| 创业公司 | FuriosaAI / Nuvacore / D-Matrix / Etched（$1B 预购）/ Tenstorrent / Sambanova / Mat-X / Positron / Majestic Labs | 多数难获 wafer，或被大厂收购 |
| 光计算 | Neurophos（声称 250× Blackwell 200）/ Lumai | 需真实系统验证 |

**趋势判断**：模型厂商（OpenAI/Anthropic）+ hyperscaler（Google/Amazon/Microsoft）+ 自研浪潮 = **"模型-芯片-云"三位一体的垂直整合**——这与 MEMORY「模型厂商全面芯片化（Anthropic 自研 AI 芯片=OpenAI 后第二家）」完全互证。

---

## 6. 统一框架：三路径的 $/token 分解

### 6.1 第一性原理：$/token 的三因子分解

```
Cost-per-token = Price-per-token         (path 1: route to cheaper models/APIs)
               OR
                 Hardware + Power cost   (path 3: more efficient HW, tokens/W up)
                 ----------------------
                   tokens produced       (path 2: fewer tokens per task via sparse)

Three levers:
  1 lower unit price : routing/substitution (software layer, zero sunk cost, instant)
  2 lower usage      : sparse activation + SLM tailoring (model layer, structural)
  3 lower unit cost  : custom chips + model-in-silicon (HW layer, high sunk cost, long-term)
```

### 6.2 三路径的决策梯度

| 维度 | ① 路由 | ② 稀疏化 | ③ 专用芯片 |
|:-----|:-------|:---------|:-----------|
| 生效时间 | 天级 | 月级（模型迁移/微调） | 年级（流片） |
| 沉没成本 | 低（API 切换） | 中（权重/工具链） | 高（硅片不可逆） |
| 降本幅度 | 30×（价差上限） | 5-20×（active 比例） | 6-10×（tokens/W） |
| 灵活性 | 高（随时切回） | 中（结构固定） | 低（锁死模型代际） |
| 谁受益 | 所有企业 | 高 token 量企业 | 大厂/模型厂/hyperscaler |

**核心判断**：**三路径不是替代关系而是先后关系**——企业按 token 规模从小到大依次启用：小企业先用 ①；中等企业叠加 ②；大厂/hyperscaler 最终走 ③。**Token 规模决定路径深度**。

### 6.3 供给侧的镜像：效率提升 = 等效供给放大

Tate 全文主线：**供应链瓶颈（Foundry/存储/供电/激光）→ 效率是 2-5 年的核心策略**。三路径本质是"用更少的物理资源产出更多 token"：

```
Frozen v2 6-10x tokens/W = equivalent wafer supply x6-10 (for Gemini workloads)
Trainium customization = equivalent DC capacity gain (for AWS workloads)
Model routing = frees "compute" from overkill tasks for more tasks
```

这与 MEMORY「软件杠杆 ≥ 硬件（GB300 MoE 预训练 1,648 TFLOPs/GPU + 软件 6 个月 1.5×）」、以及「模型侧降本三路径」研究线一脉相承。

---

## 7. 对服务器产品线的含义

| # | 含义 | 可操作动作 | 优先级 |
|:--|:-----|:-----------|:------:|
| 1 | **推理 SKU 分化加速**：模型路由 → 同一服务器承载多模型混合负载 → "容量型"（大内存驻留 MoE 权重 + CXL）与"带宽型"（高 tokens/W）分化是必然 | 与上午[容量型 SKU 战略框架](2026-08-11-inference-gpu-capacity-sku-strategy-framework.md)合并执行；C5 立项条件补充"MoE 权重驻留比"指标 | P0 |
| 2 | **tokens/W 成为推理芯片第一指标**：Trainium/Frozen v2 以 tokens/W 定价——服务器整机宣传应从 FLOPS 转向 tokens/W（含 PUE/散热联动） | 推理机型规格书增加 tokens/W 指标（含整机级，非仅芯片级） | P1 |
| 3 | **国产对标新维度**：中国模型（GLM/Kimi/DeepSeek）被美企大规模采用 = 国产模型生态已过"能用"门槛 → 国产推理芯片的瓶颈在**框架/生态兼容**而非模型能力 | 推理芯片选型评估增加"对国产开源模型（GLM/Kimi/DeepSeek）的 vLLM/SGLang 兼容度"权重（与上午 C5 互证） | P1 |
| 4 | **推理服务器出口机会**：美企采用中国模型 = 软件侧出海 → 国产推理服务器（搭载国产芯片）存在"模型+硬件"组合出海窗口 | 建立"中国模型生态出海"跟踪线：GLM/Kimi/DeepSeek 海外 API 用量、被采用企业清单 | P2 |
| 5 | **MoE 权重驻留的内存需求**：975B 权重需 ~2TB bf16 / ~500GB NVFP4 驻留 → "容量型"SKU（大内存+CXL+风冷）需求有真实模型锚点 | 容量型 SKU 的内存配置按 MoE 1T 级权重驻留设计（如 2TB+ DRAM + CXL 池） | P1 |
| 6 | **模型进硅的时差风险**：Frozen v2 2028 固化 2027 模型——服务器厂商不应押注"模型进硅"成为主流（3-5 年内），通用+可编程仍是推理服务器主赛道 | 监控 Etched/Frozen v2 路线图；推理服务器保持"可编程 GPU/加速器优先" | P3 |
| 7 | **供应链联动**：Frozen v2/Trainium 放量抢占 TSMC wafer + HBM → 推理服务器出货的 wafer/HBM 竞争加剧 | 供应链约束全景图（八线同紧）加入"定制芯片放量"因子 | P2 |

**与 MEMORY 研究线互证**：
- 「AI 产业四重门禁（安全/成本/财务/物理）」→ 本报告是**成本门禁**的供给侧实证（模型侧降本 + 定制芯片 + 模型进硅都是成本门禁的应对）
- 「模型厂商全面芯片化」→ 本报告补充 hyperscaler 侧（Trainium 外销、Frozen v2）
- 「中国模型占美企 token 30%」已入 MEMORY → 本报告给出机制与案例（Coinbase）的完整链条

---

## 8. 可证伪预测

| # | 预测 | 验证窗口 | 证伪条件 |
|:--|:-----|:---------|:---------|
| P1 | 中国模型占美企 token 份额 2027 年维持 ≥25%（地缘政策不逆转经济动力） | 2027-08-11 | 份额 <25% 或因政策强制切换 |
| P2 | Trainium 收入 run-rate 2027 年达 $50B+（翻倍，受外销驱动） | 2027-08-11 | run-rate <$40B |
| P3 | Frozen v2 按 2028 窗口发布，tokens/W 实现 ≥6× | 2028-12-31 | 跳票或实测 <6× |
| P4 | "模型进硅"类产品（Frozen v2/Etched）2028 年前不占主流推理份额（<5%） | 2028-12-31 | 任一产品推理 token 份额 ≥5% |
| P5 | 推理服务器 SKU 分化：2027 年主流厂商（≥3 家）提供"容量型"（大内存+CXL+风冷）推理 SKU | 2027-12-31 | 少于 3 家跟进 |
| P6 | 中国开源模型（GLM/Kimi/DeepSeek）中至少 1 家 2027 年在美企 token 份额单独 ≥10% | 2027-12-31 | 无一达到 |

---

## 9. 数据源注册表与缺口声明

### 9.1 数据源清单

| # | 来源 | 类型 | 访问状态 | 贡献数据 |
|:--|:-----|:-----|:---------|:---------|
| 1 | SemiEngineering Geoff Tate 专栏（2026-08-10） | 一手原文 | ✅ 已归档 | 全部三路径数据点 |
| 2 | Thinking Machines Inkling 官方（thinkingmachines.ai） | 一手 | ⚠️ 未直连（经第三方转述） | 975B/41B、1M 上下文 |
| 3 | datalearner.com Inkling 模型页 | 第三方聚合 | ✅ 搜索确认 | 975B/41B 激活 MoE 交叉验证 |
| 4 | 36kr/腾讯新闻 Inkling 解读 | 第三方 | ✅ 搜索确认 | 训练 45 万卡时、借鉴 DeepSeek/Kimi |
| 5 | Amazon 财报电话会（2026-07-30） | 一手 | ⚠️ 经 Tate 转述 | Trainium run-rate >$25B/年 |
| 6 | OpenRouter Leaderboard | 一手数据源 | ⚠️ 未直连 | top10 中国 8 席 |
| 7 | William Blair 报告 | 投资机构 | ⚠️ 未直连 | 中国模型 30% 份额 |
| 8 | The Information | 付费媒体 | ⚠️ 未直连 | Frozen v2 细节 |
| 9 | Wall Street Journal | 付费媒体 | ⚠️ 未直连 | Thinking Machines 41B active |

### 9.2 数据缺口（诚实声明）

1. **OpenRouter leaderboard 未直连验证**：8/10 中国席位依赖 Tate 转述 + MEMORY 锚点，未独立抓取当前榜单
2. **Frozen v2 细节匮乏**：The Information 付费墙，仅知"硬编码 Gemini 部分 + 6-10× tokens/W + 2028"；具体固化哪些模型组件、工艺节点、与 TPU 关系未知
3. **William Blair 30% 口径未披露**：统计范围（API 直连？含开源自托管？）、时间窗（自 2 月起）、模型归属（中国公司 vs 中国训练）均需澄清
4. **Trainium $25B 口径**："run-rate"是年化推算（季度×4 或最新月×12），非已实现收入；外销与内部使用的拆分未知
5. **Coinbase 支出砍半**：X 帖未直连（仅 Tate 转述），"支出"口径（API 账单？含推理硬件？）未明

---

## 10. Changelog

| 日期 | 变更 | 说明 |
|:-----|:-----|:-----|
| 2026-08-11 | 初稿创建 | 基于 Geoff Tate SemiEngineering 原文 + Thinking Machines Inkling 交叉验证；与容量型 SKU 战略、模型能力对比文档交叉链接 |

---

> **一句话带走**：**推理降本从"换便宜的模型"（30× 价差，零成本生效）起步，沿"稀疏化"（41B active 撬动 975B 知识）深入，最终在"模型进硅"（6-10× tokens/W）封顶——三层杠杆共同把"每 token 成本"推向物理极限，而服务器厂商的机会在中间层：用容量型/带宽型 SKU 分化承接每一层降本带来的负载形态变化。**
