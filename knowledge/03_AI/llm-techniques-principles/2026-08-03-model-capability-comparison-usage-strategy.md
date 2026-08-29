# 2026-08 大模型能力对比与使用策略深度分析

> **快照日期**: 2026-08-03 | **数据基线**: Artificial Analysis Intelligence Index v4.1（2026-07-31 更新，590 模型）、LLMRank 模型库（2026-08 收录 57 款）、各厂商官方发布
> **分析类型**: 能力对比 × 使用策略 × 演进趋势
> **关联文件**: [`t01-model-evaluation-two-dimensions.md`](2026-07-30-t01-model-evaluation-two-dimensions.md)（上下文视野×注意力利用框架）、[`2026-06-28-llm-comparative-analysis.md`](2026-06-28-llm-comparative-analysis.md)（历史对比）、[`2026-06-26-inference-context-memory-storage.md`](../../02_rd/01_product/00_hardware/06_storage/kv-cache/2026-06-26-inference-context-memory-storage.md)（KV Cache 存储）、[`2026-08-03-agent-composition-and-coding-agent-comparison.md`](../agent-engineering/2026-08-03-agent-composition-and-coding-agent-comparison.md)（Agent 构成）

---

## 📑 目录

- [1. 分析框架与数据基线](#1-分析框架与数据基线)
- [2. 头部 20 模型全景矩阵](#2-头部-20-模型全景矩阵)
- [3. 上下文窗口深度对比](#3-上下文窗口深度对比)
- [4. 推理能力深度对比](#4-推理能力深度对比)
- [5. 多模态能力对比](#5-多模态能力对比)
- [6. 速度与延迟](#6-速度与延迟)
- [7. 成本经济学](#7-成本经济学)
- [8. 开放性与自托管](#8-开放性与自托管)
- [9. 各厂商产品线梯度分析](#9-各厂商产品线梯度分析)
- [10. 模型默认输出特征分析](#10-模型默认输出特征分析)
- [11. 使用策略：分级路由与多模型协作](#11-使用策略分级路由与多模型协作)
- [12. 演进趋势](#12-演进趋势)
- [13. 面临的问题与挑战](#13-面临的问题与挑战)
- [参考文献](#参考文献)
- [Changelog](#changelog)

---

## 1. 分析框架与数据基线

### 1.1 数据来源与方法

本分析以 2026-08-03 为快照点，融合三类数据源：

| 来源 | 性质 | 覆盖 | 说明 |
|:-----|:-----|:-----|:-----|
| **Artificial Analysis** (AA) | 独立实测 | 590 模型 | Intelligence Index v4.1 = 9 项基准加权（GDPval-AA v2 真实工作任务 / 𝜏³-Banking 工具调用 / Terminal-Bench v2.1 终端编码 / SciCode / Humanity's Last Exam / GPQA Diamond / CritPt 物理推理 / AA-Omniscience 知识+幻觉 / AA-LCR 长上下文推理），另有 Coding Index / Agentic Index / AA-Briefcase（长时程知识工作） |
| **LLMRank** | 多源聚合 | 57 款 | 聚合 AA + LMArena + SuperCLUE + OpenRouter 用量 + 价格 + 国内可用性，中文视角 |
| **官方发布** | 一手 | — | 参数、上下文、多模态规格（部分专有模型不披露参数） |

**关键口径说明**：

- AA Intelligence Index 是**每任务成本加权**的复合分，非单一 benchmark 分；不同模型在不同子项差异巨大（后文 §10 展开）
- 速度 = API 实测输出 tokens/s（含推理模型思考时间则单独标注）；延迟 = TTFT（含思考时间）
- 价格统一为官方 API 每百万 tokens（$ / 1M tokens），cache hit 折扣另列
- **推理模型**（reasoning）在 AA 中占比 129/185——2026 年主流模型已普遍内置思考链，非推理变体反而成为"特殊形态"

### 1.2 评价维度体系

对比任何模型，本分析使用**六维 + 两个附加维度**：

```text
+-------------------------------------------------------------+
|  ① 智能(Intelligence)  AA Index v4.1，复合实测              |
|  ② 上下文(Context)     声明窗口 × 有效利用（视野≠理解）      |
|  ③ 推理(Reasoning)     effort 档位 / 思考链 / 数学-逻辑-规划  |
|  ④ 多模态(Multimodal)  输入(图/音/视频) × 输出(文本/生成)     |
|  ⑤ 速度(Speed)         输出 t/s × TTFT × 端到端              |
|  ⑥ 成本(Cost)          价格 × 每任务成本 × 缓存折扣          |
|  ----------------------------------------------------------- |
|  ⑦ 开放性(Openness)    专有 / 开放权重 / 开源 + 许可证        |
|  ⑧ 默认输出倾向        啰嗦度(verbosity) × 风格 × 幻觉率     |
+-------------------------------------------------------------+
```

**为什么不能只看智能分**：AA 官方明示"模型智能大体可迁移，但具体用例需看对应评测"——金融看 𝜏³-Banking、运维看 ITBench、法律看 Harvey LAB、长时程交付看 AA-Briefcase。选型错误的第一根源是"用总分代替场景分"。

### 1.3 与知识库既有框架的衔接

知识库 [`t01`](2026-07-30-t01-model-evaluation-two-dimensions.md) 提出**上下文视野 × 注意力利用**二维正交框架。2026 年该框架依然有效，且新增了实证维度：

| 知识库框架 | 2026 实证工具 |
|:-----------|:--------------|
| 上下文视野（声明 vs 有效） | AA-LCR（长上下文推理）、大海捞针类测试 |
| 注意力利用（噪声过滤/远距依赖） | AA-Omniscience（知识可靠+幻觉惩罚） |
| 逻辑链条维持 | GDPval-AA v2（多步真实工作任务） |

---

## 2. 头部 20 模型全景矩阵

### 2.1 总表（按 AA Intelligence Index 排序）

> 数据：AA v4.1（2026-07-31）；"+"表示 LLMRank 聚合口径；Qwen3.8 为 2026-08-03 当日发布（参数来自官方，评测待收录）

| # | 模型 | 厂商 | 智能 | 上下文 | 输入模态 | 输出速度 | 价格($/M in/out) | 类型 | 发布 |
|:-:|:-----|:-----|:----:|:------:|:---------|:--------:|:-----------------|:-----|:-----|
| 1 | **Claude Opus 5** (max) | Anthropic | **61** | 1M | 文本+图像 | 55 t/s | 5.00 / 25.00 | 专有·推理 | 07-24 |
| 2 | **Claude Fable 5** (max, Opus 4.8 fallback) | Anthropic | **60** | 1M | 文本+图像 | 75 t/s | 10.00 / 50.00 | 专有·推理 | 06-09 |
| 3 | **GPT-5.6 Sol** (max) | OpenAI | **59** | 1M | 文本+图像 | 68 t/s | 5.00 / 30.00 | 专有·推理 | 07-09 |
| 4 | **Kimi K3** (max) | 月之暗面 | **57** | 1M | 文本+图像 | 35 t/s | 3.00 / 15.00 | 开放权重·MoE 2.8T/104B | 07-16 |
| 5 | Claude Opus 4.8 | Anthropic | 56 | 1M | 文本+图像 | — | 5.00 / 25.00 | 专有·推理 | 06-xx |
| 6 | GPT-5.5 | OpenAI | 55 | 1M | 文本+图像 | — | 5.00 / 30.00 | 专有·推理 | 05-xx |
| 7 | GPT-5.6 Terra | OpenAI | 55 | 1M | 文本+图像 | 140 t/s | 5.00 / 15.00 | 专有·推理(均衡) | 07-09 |
| 8 | **Grok 4.5** | SpaceXAI | 54 | 2M | 文本+图像 | 174 t/s | 2.00 / 6.00 | 专有·推理 | 07-08 |
| 9 | Claude Sonnet 5 | Anthropic | 53 | 1M | 文本+图像 | — | 3.00 / 10.00 | 专有·推理 | 06-xx |
| 10 | **GLM-5.2** (max) | 智谱 Z.ai | **51** | 1M | 文本 | 176 t/s | 1.40 / 4.40 | 开放权重·MoE 753B/40B | 06-16 |
| 11 | GPT-5.6 Luna | OpenAI | 51 | 1M | 文本+图像 | 204 t/s | 0.90 / 6.00 | 专有·推理(轻量) | 07-09 |
| 12 | **DeepSeek V4 Flash** 0731 | DeepSeek | **50** | 1M | 文本 | — | **0.14 / 0.28** | 开放权重·MoE 284B/13B·MIT | 07-31 |
| 13 | **Gemini 3.6 Flash** | Google | 50 | 1M | 文本+图像+语音+视频 | **214 t/s** | 1.50 / 7.50 | 专有·推理 | 07-21 |
| 14 | Gemini 3.5 Flash | Google | 50 | 1M | 全模态 | 156-208 t/s | 1.50 / 9.00 | 专有·推理 | 06-xx |
| 15 | Gemini 3.1 Pro | Google | 46 | 1M | 全模态 | 117 t/s | 2.00 / 12.00 | 专有·推理 | 05-xx |
| 16 | **Qwen3.7 Max / Qwen3.8** | 阿里 | 46+ | 1M+ | 多模态 | 200 t/s | 3.75 / 4.42 | 开放权重 | 07-19 / **08-03** |
| 17 | MiMo-V2.5-Pro | 小米 | 42 | 1M | 多模态 | — | 0.87 / 0.87 | 开放权重 | 07-xx |
| 18 | MiniMax M3 | MiniMax | ~45* | 1M | 多模态 | — | 0.20 / 1.00 | 专有·MSA 稀疏注意力 | 06-xx |
| 19 | Grok 4.20 (0309) | SpaceXAI | 37 | **2M** | 文本+图像 | 174 t/s | 2.00 / 6.00 | 专有·已换代 | 04-07 |
| 20 | **Llama 4 Scout** | Meta | ~35* | **10M** | 文本 | — | 0.30 / 0.30 | 开源·MoE | 04-xx |

> \* 为 LLMRank/估算口径；MiniMax M3 官方宣称 BrowseComp 超过 Claude Opus（需独立复测）。**速度之王**（不入智能榜但代表架构前沿）：Celeris-1（celeris.ai，**扩散架构** 2158 t/s）、Mercury 2（Inception Labs，扩散架构 749 t/s）、Step 3.7 Flash（阶跃 410 t/s）、Gemini 2.5 Flash-Lite（TTFT 0.33s）。

### 2.2 梯队划分

| 梯队 | 智能区间 | 代表 | 定位 |
|:-----|:--------:|:-----|:-----|
| **第一梯队** | 55-61 | Opus 5 / Fable 5 / GPT-5.6 Sol / Kimi K3 / Opus 4.8 / GPT-5.5 / Terra | 复杂推理、长时程 Agent、高价值任务 |
| **第二梯队** | 50-54 | Grok 4.5 / Sonnet 5 / GLM-5.2 / Luna / DeepSeek V4 Flash / Gemini 3.6-3.5 Flash | 主力日常、编程、Agent 执行层 |
| **第三梯队** | 40-49 | Gemini 3.1 Pro / Qwen3.7-3.8 / MiMo / MiniMax M3 / Grok 4.20 | 性价比、中文场景、垂类 |
| **特殊位** | — | Llama 4 Scout (10M) / Celeris-1 (2158t/s) / Gemini 2.5 Flash-Lite (0.33s) | 单项冠军：长上下文 / 速度 / 延迟 |

### 2.3 三组关键结构性事实

1. **开放权重已逼近专有**：Kimi K3（57）距 Opus 5（61）仅 4 分，但成本低一个数量级；DeepSeek V4 Flash（50）以 $0.14/$0.28 的"地板价"拿到与 Gemini 3.6 Flash（$1.5/$7.5）同分——**开源模型在性价比象限全面接管中端市场**（AA 开放权重 98/174 个已评估）。
2. **旗舰分化出"能力上限 vs 成本效率"两派**：Anthropic 的 Fable 5（60 分，$10/$50）与 Opus 5（61 分，$5/$25）构成"双旗舰"，OpenAI 用 Sol/Terra/Luna 三档覆盖 51-59 分区间——**同一模型家族内做 effort/规格分档成为标准打法**。
3. **2026-08-03 当日发生市场突变**：阿里发布 Qwen3.8（2.4T 总参数，编程+专业办公双主线，预览版已上线 Token Plan 与 Qoder IDE），国产旗舰正式进入 2.4T 级参数竞赛。

---

## 3. 上下文窗口深度对比

### 3.1 声明容量 vs 有效容量（第一性原理）

知识库 [`t01`](2026-07-30-t01-model-evaluation-two-dimensions.md) 已确立：**上下文窗口的声明容量与有效容量是两回事**。物理机制：

1. **注意力稀释**：窗口扩大 N 倍，同等算力下每个 token 的平均注意力权重被摊薄；长文中段的召回率显著低于首尾（Lost-in-the-Middle）
2. **位置编码退化**：RoPE 在超长距离上旋转角度过大，远距离 token 语义相关性混淆（YaRN/NTK 插值缓解但非根治）
3. **KV Cache 成本线性爆炸**：1M 上下文 ≈ 1500 页 A4；KV 存储随 N 线性增长，推理基础设施成为第一瓶颈（见知识库 [`2026-06-26-inference-context-memory-storage.md`](../../02_rd/01_product/00_hardware/06_storage/kv-cache/2026-06-26-inference-context-memory-storage.md)）

**2026 实测结论**：AA 新增 AA-LCR（长上下文推理）子项后，1M 窗口模型的远距召回普遍打 6-8 折；**"1M 只是入场券，有效利用才是分水岭"**。

### 3.2 全市场上下文分布

| 档位 | 代表模型 | 适用场景 |
|:-----|:---------|:---------|
| **10M** | Llama 4 Scout（Meta 开源，$0.30/M） | 全书级文档、超长代码库全量注入 |
| **2M** | Grok 4.20/4.5（SpaceXAI） | 巨型代码仓、长会话 Agent |
| **1M（主流标配）** | Opus 5 / Fable 5 / GPT-5.6 全系 / Kimi K3 / GLM-5.2 / DeepSeek V4 / Gemini 全系 / Qwen3.7+ / MiniMax M3 / Nemotron 3 Ultra / GPT-5.4 | 长文档、Agent 长循环、全仓检索增强 |
| **128K-512K** | 上一代模型（Opus 4.x 早期 / GPT-4.x / 部分轻量） | 常规业务 |

**结构判断**：1M 已成为 2026 年旗舰/中端模型的**最低入场标准**（连 $0.14/M 的 DeepSeek V4 Flash 都是 1M）；10M 是 Llama 4 Scout 的差异化护城河，但**有效利用 10M 所需的 RAG/摘要预处理成本使其"文档量贩"属性强于"精读"属性**。

### 3.3 长上下文的技术实现路径

| 路径 | 代表 | 原理 | 代价 |
|:-----|:-----|:-----|:-----|
| 标准注意力 + 位置插值 | 1M 主流 | YaRN/NTK 类扩展 RoPE | 有效视野打折 |
| **稀疏注意力 (MSA)** | MiniMax M3 | 稀疏注意力压注意力矩阵 | 质量取决于稀疏 mask 设计 |
| 混合状态空间 | 部分轻量 | SSM 线性复杂度 | 精确检索弱 |
| 检索增强 (RAG) 外挂 | 所有 | 外部索引 + 注入 | 依赖检索质量（见知识库 RAG 专题） |

**MiniMax M3 的 MSA 是 2026 年注意力层的重要信号**：官方称 BrowseComp（浏览器级长任务）超 Claude Opus——稀疏注意力把"长窗口的成本"从 O(N²) 拉到近线性，是 1M+ 窗口向 2M/10M 演进的关键技术变量。

### 3.4 对 RAG / Agent 的影响

- **RAG 的定位变化**：1M 窗口普及后，"整库塞进上下文"成为小知识库的可行选项（<1M token ≈ 数百页）；RAG 退守到**百万级 token 以上的知识库**或**需要实时更新的数据**场景——即 RAG 从"必须"变成"超过窗口才需要"
- **Agent 长循环**：Claude Opus 5 的 1M 窗口 + Adaptive Reasoning 直接支撑 150+ 迭代的长时程任务（与知识库 [`agent-composition`](../agent-engineering/2026-08-03-agent-composition-and-coding-agent-comparison.md) 的 Long Horizon 分析一致）；10M（Scout）为"代码库全量 Agent"打开了空间，但子代理隔离仍是上下文管理的首选工程手段

---

## 4. 推理能力深度对比

### 4.1 推理模型已成为默认形态

AA 数据：129/185 模型是推理模型（reasoning）。2026 年的产品分化不是"要不要推理"，而是：

| 维度 | 代表机制 |
|:-----|:---------|
| **思考深度 (effort 档位)** | Claude Opus 5 Adaptive Reasoning：low → medium → high → xhigh → max 五档；GPT-5.6 Sol/Terra/Luna 三档；DeepSeek V4 Flash Reasoning 档 |
| **思考时长的代价** | Opus 5 (max) TTFT **85.57s**、Fable 5 (max) **131.42s**、GPT-5.6 Sol (max) **130.56s**（中位仅 2.77s）——max effort 是"慢思考"的极致形态 |
| **Fallback 机制** | Claude Fable 5 (Opus 4.8 fallback)：模型不确定时回退到更强基线——推理可靠性工程的前沿实践 |

### 4.2 Adaptive Reasoning：2026 年的标志性设计

Opus 5 的 Adaptive Reasoning 本质是**把"思考预算"变成可调参数**：

```text
低 effort (low)      -> 快速响应，适合日常问答/翻译/分类
中 effort (medium)   -> 常规分析、代码生成
高 effort (high/xhigh) -> 复杂推理、长时程规划
max effort          -> 极限任务（数学竞赛/深度研究），TTFT 85s+，verbosity 100M tokens
```

**第一性原理**：推理质量 ≈ 思考 token 预算的函数，但边际收益递减；合理策略是**按任务难度动态分配 effort**，而非固定最高档。AA 实测 Opus 5 各档位 61/60/59 分——max 比 high 只多 2 分，成本却显著更高。

### 4.3 推理能力分场景画像

| 场景 | 首选 | 依据 |
|:-----|:-----|:-----|
| 数学/科学推理 (GPQA/CritPt) | Opus 5 / GPT-5.6 Sol / Kimi K3 | AA 子项领先 |
| 代码生成 (Terminal-Bench) | Gemini 3.6 Flash / Qwen3.8 / Claude Sonnet 5 | 官方定位 + WebDev 榜 |
| 长时程 Agent (AA-Briefcase) | Fable 5 / Opus 5 / Kimi K3 | Briefcase Elo 前三 |
| 金融/工具调用 (𝜏³-Banking) | Opus 5 / GPT-5.6 系 | 工具调用子项 |
| 终端/运维 (ITBench) | DeepSeek V4 / Claude 系 | ITBench-AA 子项 |
| 中文推理 | GLM-5.2 / Qwen3.7-3.8 / DeepSeek V4 | SuperCLUE 中文榜 |

**注意**：GPT-5.6 Sol 与 Claude 系的差距主要在 Agent 场景；**Gemini 3.1 Pro 的 Agent 编排被 AA 与 LLMRank 双源标记为短板**（"复杂 Agent 编排不是 Gemini 的强项"）——智能总分高 ≠ Agent 可用。

---

## 5. 多模态能力对比

### 5.1 输入模态矩阵

| 模型 | 文本 | 图像 | 语音 | 视频 | 文件 |
|:-----|:----:|:----:|:----:|:----:|:----:|
| Gemini 3.6 Flash / 3.5 Flash / 3.1 Pro | ✅ | ✅ | ✅ | ✅ | ✅ |
| Claude Opus 5 / Fable 5 / Sonnet 5 | ✅ | ✅ | ❌ | ❌ | ❌ |
| GPT-5.6 Sol/Terra/Luna | ✅ | ✅ | ❌* | ❌ | ✅ |
| Kimi K3 / Qwen3.7+ / MiMo / MiniMax M3 | ✅ | ✅ | 部分 | 部分 | ✅ |
| DeepSeek V4 Flash | ✅ | ❌ | ❌ | ❌ | ❌ |
| GLM-5.2 | ✅ | ❌ | ❌ | ❌ | ❌ |

> \* GPT 系列语音/视频能力通过 App 端（实时语音/视频模式）提供，API 输入以文本+图像为主。

**格局判断**：

- **Gemini 是"原生全模态"的唯一完整实现**——LLMRank 明确评价"Gemini 的多模态是独特优势，原生支持图片、视频、音频理解，这是 Claude/GPT 通过插件实现的方式没法比的"
- **Claude/GPT 走"文本+图像核心 + 外挂多模态"路线**——对 Agent 场景够用，但对视频理解、实时语音原生交互有差距
- **国产分化**：Kimi K3/Qwen 系支持图像；DeepSeek V4 Flash 与 GLM-5.2 是**纯文本模型**——这是其"超低价"的结构性来源（不做视觉编码器，省训练与推理成本），也是选型时必须注意的边界

### 5.2 输出模态：生成模型是另一个战场

2026 年文本模型与生成模型**分工明确**，不应混为一谈：

| 类别 | 代表 | 定位 |
|:-----|:-----|:-----|
| 文本生成 | 上述全部 | 对话/代码/分析 |
| 图像生成 | Gemini 3.1 Pro Image / 3 Pro Image、Muse Spark (Meta)、Imagen | 理解复杂指令、参考图改风格 |
| 视频生成 | Seedance 2.0（字节，已接入豆包）、Veo 系 (Google)、Sora 系 (OpenAI) | 文生视频、图生视频 |
| 语音 | Gemini 语音、豆包语音、MiniMax Speech | 实时对话、TTS |

**选型要点**：若业务需要图像生成，**不要用文本模型"生成图片"**（文本模型只输出图片 URL/代码）；图像/视频任务直接选生成模型，文本任务选推理模型——二者是互补工具链而非竞品。

---

## 6. 速度与延迟

### 6.1 输出速度全景（AA 实测）

| 模型 | 输出速度 | 定位 |
|:-----|:--------:|:-----|
| **Celeris-1** | **2158 t/s** | 扩散架构（Diffusion LM），速度之王 |
| **Mercury 2** | 749 t/s | Inception Labs 扩散架构 |
| Step 3.7 Flash | 410 t/s | 国产轻量 |
| Gemini 3.6 Flash | 214 t/s | 旗舰档最快之一 |
| GPT-5.6 Luna | 204 t/s | OpenAI 轻量档 |
| Qwen3.7 Max | 200 t/s | 国产旗舰最快 |
| GLM-5.2 | 176 t/s | 开放权重最快 |
| Grok 4.5 | 174 t/s | 性价比 |
| GPT-5.4 Mini | 179 t/s | 轻量 |
| Gemini 3.5 Flash | 156-208 t/s | 速度主打 |
| Gemini 3.1 Pro | 117 t/s | 旗舰 |
| GPT-5.6 Sol (max) | 68 t/s | 旗舰（思考拖慢） |
| Claude Opus 5 (max) | 55 t/s | 旗舰（最慢档） |
| Kimi K3 (max) | 35 t/s | 开放权重（最慢） |

### 6.2 扩散架构（Diffusion LLM）：速度革命的源头

**Celeris-1 的 2158 t/s 不是"调参优化"，而是推理范式级变革**：

```text
自回归 (Autoregressive)         扩散 (Diffusion)
---------------------          ---------------------
逐 token 顺序生成              并行去噪整个序列
延迟 ∝ 输出长度                延迟近似恒定（迭代去噪轮数）
1 token/s 级                   1k+ token/s 级
```

**第一性原理**：自回归模型的生成延迟与输出长度线性相关（写 1000 token 要 1000 次前向）；扩散模型在推理时对**整段序列并行去噪**（类似 DALL-E/Stable Diffusion 对图像的做法），将延迟从"线性"降为"轮数恒定"。代价是质量仍低于顶级自回归（Celeris-1 智能分未进前 20），且长文本一致性、精确计数等仍待验证。

**产业意义**：扩散 LLM 直接冲击**高吞吐场景**（客服、翻译、代码补全、Agent 子任务 fanout）——这些场景"量大、单次质量要求中等"，正是 2158 t/s 的价值区。

### 6.3 延迟的另一面：TTFT 与思考时间

| 场景 | 代表 | TTFT |
|:-----|:-----|:-----|
| 极致低延迟 | Gemini 2.5 Flash-Lite | 0.33s |
| 低延迟 | Command A+ / Gemini 3.5 Flash | 0.40-0.47s |
| 旗舰快 | GLM-5.2 | 1.50s |
| 旗舰推理 max | Kimi K3 | 2.78s |
| 慢思考 max | Opus 5 / GPT-5.6 Sol / Fable 5 | **85-131s** |

**结论**：max effort 推理模型的 TTFT 是普通模型的 30-50 倍——**"智能"与"响应"是同一枚硬币的两面**。交互式场景用低档位/非推理模型，深度任务才用 max 档。

---

## 7. 成本经济学

### 7.1 价格谱系（$ / 1M tokens）

```text
$0.03  - Nova Micro / Sarvam 30B / Gemma 4 E4B     <- 地板价
$0.14  - DeepSeek V4 Flash ($0.14/$0.28)           <- 开放权重性价比之王
$0.30  - Llama 4 Scout (10M 上下文)
$0.60  - Llama 4 Maverick (400B MoE)
$0.87  - DeepSeek V4 Pro / MiMo-V2.5-Pro
$1.00  - MiniMax M2.7 / Nex-N2-Pro
$1.40  - GLM-5.2 ($1.4/$4.4)
$1.50  - Gemini 3.6 Flash / 3.5 Flash ($1.5/$7.5-9)
$2.00  - Gemini 3.1 Pro / Grok 4.5 ($2/$6)
$3.00  - Kimi K3 ($3/$15)
$5.00  - Claude Opus 5 / GPT-5.6 Sol ($5/$25-30)
$10.00 - Claude Fable 5 ($10/$50)                  <- 高端"经济型"（矛盾定价见 §9.1）
$30    - GPT-5.5 Pro ($30/$180)                    <- 顶配
```

### 7.2 每任务成本（更真实的标尺）

AA 的 **Cost per Task**（每 Intelligence Index 任务加权成本）比裸价格更说明问题，因为考虑了 verbosity（啰嗦度）：

| 模型 | 每任务成本 | 说明 |
|:-----|:----------:|:-----|
| DeepSeek V4 Flash | ~$0.06 | 价格×啰嗦的乘积最小 |
| GLM-5.2 | ~$0.90 | 快+中价 |
| Gemini 3.6 Flash | ~$1.16 | 简洁（59M tokens）拉低任务成本 |
| GPT-5.6 Sol | ~$4.35 | 70M tokens 中等啰嗦 |
| Claude Opus 5 | ~$3.85 | 100M tokens 很啰嗦 |
| Kimi K3 | ~$2.31 | 130M tokens 极啰嗦 |
| Claude Fable 5 | ~$7.70 | 87M + 高价 = 任务成本最高 |

**核心洞察**：**"便宜模型 + 极啰嗦"可能比"贵模型 + 简洁"更贵**。DeepSeek V4 Flash 虽然单价最低，但生成 210M tokens（中位 100M 的 2.1 倍）；反之 Gemini 3.6 Flash 用"简洁"把每任务成本压到与 GLM-5.2 相当。

### 7.3 缓存经济学（Agent 场景的命脉）

| 模型 | Cache Write | Cache Hit | 折扣 |
|:-----|:-----------:|:---------:|:----:|
| DeepSeek V4 Flash | — | $0.003 | **-98%** |
| Claude Opus 5 / GPT-5.6 | $6.25 | $0.50 | -90% |
| Fable 5 | $12.50 | $1.00 | -90% |
| Gemini 3.6 Flash | — | $0.15 | -90% |

**对 Agent 的意义**：Agent 长循环中系统提示词+工具定义+历史反复重发，缓存命中率直接决定成本（知识库 27 天 2.3B tokens 的经验：缓存未命中 58% 是最大成本项）。**选模型时必须把 cache hit 价格与折扣纳入计算**，-98% 的 DeepSeek 与 -90% 的主流折扣差一个数量级。

### 7.4 能力-成本象限（Pareto 前沿）

```text
智能(Index)
 61 | Opus 5
 60 | Fable 5
 59 | GPT-5.6 Sol
 57 | Kimi K3
 54 | Grok 4.5        <- Pareto 线
 51 | GLM-5.2         <- Pareto 线
 50 | DeepSeek V4 Flash <- Pareto 线（最陡性价比）
    +-------------------------------> 1/每任务成本
```

**Pareto 前沿模型**（性价比最优）：DeepSeek V4 Flash → GLM-5.2 → Grok 4.5 → Kimi K3 → GPT-5.6 Sol → Fable 5/Opus 5。**预算敏感选前沿中下部，质量极致选上部**。

---

## 8. 开放性与自托管

### 8.1 开放权重格局

| 梯队 | 模型 | 参数 (总/激活) | 许可证 | 智能 |
|:-----|:-----|:---------------|:-------|:----:|
| 第一 | Kimi K3 | 2800B / 104B MoE | Kimi K3 License（商业需授权） | 57 |
| 第二 | GLM-5.2 | 753B / 40B MoE | MIT | 51 |
| 第三 | DeepSeek V4 Flash | 284B / 13B MoE | MIT | 50 |
| 第四 | Qwen3.7 Max / 3.8 | 2400B / — | 开放 | 46+ |
| 中端 | Llama 4 Maverick | 400B MoE | Llama 4 许可 | ~45 |
| 长文 | Llama 4 Scout | — | Llama 4 许可 | ~35 |
| 黑马 | MiMo-V2.5-Pro (小米) | — | 开放 | 42 |
| 超大 | NVIDIA Nemotron 3 Ultra | 550B MoE | 开放 | — |

### 8.2 关键结论

1. **MIT 协议成为开源性价比标杆**：DeepSeek V4 Flash（MIT、$0.14）与 GLM-5.2（MIT、$1.4）可自由商用/自托管，是私有化部署首选
2. **Kimi K3 的能力与许可错位**：57 分开放第一但商业授权受限——"看得见用不痛快"，选择时要确认商业授权条款
3. **自托管成本公式**：13B 激活（DeepSeek V4 Flash）单卡可跑；40B 激活（GLM-5.2）需多卡；104B 激活（Kimi K3）需整机——**激活参数决定硬件门槛**，总参数是宣传数字
4. **国产开放权重已是主流**：前四开放权重三席国产（Kimi/GLM/DeepSeek/Qwen 系），2026 年"开源追赶专有"格局确立

---

## 9. 各厂商产品线梯度分析

### 9.1 Anthropic：双旗舰 + Fallback 工程

```text
Opus 5 (61分, $5/$25)  <- 能力上限（7-24）
Fable 5 (60分, $10/$50, Opus 4.8 fallback)  <- "经济型"但单价最贵（矛盾定价）
Sonnet 5 (53分, $3/$10)  <- 性价比主力
Opus 4.8 / Sonnet 4.6    <- 上一代仍在服役（开发者主力实测）
```

**结构解读**：Opus 5 是"更便宜更强的 Opus"（比 Fable 5 便宜一半还强 1 分）；Fable 5 定价 $10/$50 反而高于 Opus 5，其价值在 **Opus 4.8 fallback 机制**——面向"必须绝对可靠"的高风险场景（合规/金融/医疗）。Anthropic 的战略是**质量溢价路线**：智能分第一梯队 + 全面 1M + 图片输入，牺牲速度换深度。

### 9.2 OpenAI：规格分档的全家桶

```text
GPT-5.6 Sol (59, $5/$30)   <- 旗舰档（max）
GPT-5.6 Terra (55, $5/$15) <- 均衡档（140 t/s）
GPT-5.6 Luna (51, $0.9/$6) <- 轻量档（204 t/s）
GPT-5.5 (55) / GPT-5.4 (54.3, 105万 ctx) / 5.4 Mini / 5.4 Nano
GPT-5.5 Pro ($30/$180)     <- 顶配（高难度+高风险）
gpt-oss-120b               <- 开源探索（provider 速度榜在列）
```

**结构解读**：OpenAI 用"同一代际三档"覆盖 51-59 分——Sol/Terra/Luna 是 2026 年最清晰的分档产品线。GPT-5.4 的 **105 万上下文**是 OpenAI 对长窗口的回应。**生态+Agent 能力是 GPT 的核心优势**（LLMRank 评价），但价格带整体高于国产开放权重。

### 9.3 Google：速度与多模态，但旗舰缺席

```text
Gemini 3.6 Flash (50, 214t/s, $1.5/$7.5) <- 编程/Agent 新旗舰（7-21）
Gemini 3.5 Flash (50, 156-208t/s, $9)    <- 速度之王
Gemini 3.5 Flash-Lite ($0.3/$2.5)        <- 子代理专用（最低价）
Gemini 3.1 Pro (46, $2/$12)              <- 综合旗舰（当前最高档）
Gemini 3.5 Pro                            <- 未发布（partner 测试中，跳票）
```

**结构解读**：Google 2026 年的节奏是**"先 Flash 后 Pro"**——7-21 连发 3 款 Flash（3.6 Flash / 3.5 Flash-Lite / 3.5 Flash Cyber 网络安全专用），3.5 Pro 持续跳票。**"快+长+全模态"是 Google 三角**，但 Agent 编排能力被多源标记为短板，且**国内可用性不稳定**（无官方节点，生产环境必须 fallback）。

### 9.4 SpaceXAI（原 xAI）：长上下文 + 快速迭代

```text
Grok 4.5 (54, $2/$6, 7-08)  <- 新旗舰
Grok 4.3 (high)             <- 4.20 的接替
Grok 4.20 0309 (37, 2M, 4-07) <- 已换代（2M 上下文遗产）
Grok Build 0.1              <- 开发工具化
```

**结构解读**：xAI 与 SpaceX 整合为 SpaceXAI 后，Grok 保持**2M 上下文（全场最大专有）**与性价比定位（$2/$6）。4.20→4.3→4.5 三个月三代，迭代速度全场最快，但**智能分未进前五**（54 vs Opus 61）——"快迭代补能力"路线。

### 9.5 国产六强全景

| 厂商 | 旗舰 | 智能 | 特色 | 短板 |
|:-----|:-----|:----:|:-----|:-----|
| 月之暗面 | Kimi K3 (57) | 开放权重第一 | 1M / 中文 / 长文 | 慢 (35t/s)、贵、许可受限 |
| 智谱 Z.ai | GLM-5.2 (51) | 开放第二/国内第一 | WebDev 强、176t/s、MIT | 纯文本 |
| DeepSeek | V4 Flash (50) / V4 Pro | 开放第三 | $0.14 地板价、MIT、用量榜第一 | 纯文本、极啰嗦 |
| 阿里 | Qwen3.7 Max / **3.8 (2.4T)** | 46+ | 编程+办公双主线、Token Plan/Qoder | 刚发布待实测 |
| 字节 | Doubao Seed 2.0 | SuperCLUE 第4 | 生态（豆包/Seedance 2.0 视频）、性价比 | 智能分未进 AA 前 20 |
| 小米 | MiMo-V2.5-Pro (42) | 全球第5/中国第2 | $0.87 便宜、黑马 | 能力区间中端 |
| MiniMax | M3 / M2.7 | ~45 | MSA 稀疏注意力、1M、$0.2 地板 | BrowseComp 宣称待复测 |
| 腾讯 | Hy3 (295B MoE) | 用量榜第2 | $0.2/$0.8、免费 tier | 能力中端 |
| 阶跃 | Step 3.7 Flash (410t/s) | 速度档 | 国产速度最快之一 | 能力中端 |

**国产结构性事实**：① **开放权重是国产主战场**（Kimi/GLM/DeepSeek/Qwen/MiMo 全部开放）；② **价格战打到地板**（DeepSeek $0.14、MiniMax $0.2）；③ **纯文本化换取极致性价比**（DeepSeek V4 Flash/GLM-5.2 无视觉输入）；④ 中文场景（SuperCLUE）国产包揽头部。

### 9.6 新势力与专业玩家

| 玩家 | 模型 | 看点 |
|:-----|:-----|:-----|
| Thinking Machines Lab | Inkling / Inkling Small / Agnes 2.5 | 智能体知识工作（AA-Briefcase 前列），Inkling Small 以 1/3 参数追平 |
| Celeris (celeris.ai) | Celeris-1 | **扩散架构** 2158 t/s，速度范式革命 |
| Inception Labs | Mercury 2 | 扩散架构 749 t/s |
| Nex AGI | Nex-N2-Pro | 397B MoE/17B 激活，$1/M 低价推理 |
| Poolside | Laguna XS 2.1 | 代码专精 $0.12/M |
| NVIDIA | Nemotron 3 Ultra | 550B MoE、1M 上下文 |
| Meta | Llama 4 Maverick/Scout、Muse Spark | 开源主力 + 10M 上下文 + 创意生成 |

---

## 10. 模型默认输出特征分析

### 10.1 AA Verbosity 数据（Intelligence Index 输出 token 总量）

| 模型 | 输出 tokens | vs 中位(63M/100M) | 画像 |
|:-----|:----------:|:------------------|:-----|
| DeepSeek V4 Flash | **210M** | 2.1×（开放中位） | 极啰嗦——"思考全输出" |
| Kimi K3 | 130M | 1.3× | 很啰嗦 |
| GLM-5.2 | 140M | 1.4× | 很啰嗦 |
| Claude Opus 5 | 100M | 1.6×（专有中位） | 很啰嗦 |
| Claude Fable 5 | 87M | 1.4× | 较啰嗦 |
| GPT-5.6 Sol | 70M | 1.1× | 中等 |
| Gemini 3.6 Flash | 59M | 0.94× | **简洁** |
| Gemini 3.5 Flash | ~55M | 0.87× | **简洁** |

### 10.2 输出倾向画像（结合 LLMRank/AA 与实测社区反馈）

| 模型 | 默认输出特征 |
|:-----|:-------------|
| **Claude 系** | 结构化强（Markdown/代码块规范）、推理过程透明、**verbose**；Opus 5 max 档"全量思考再回答"，适合审阅型任务 |
| **GPT-5.6 系** | 直接、工具调用规范、Sol 档深度推理；Luna 档倾向简短——"三档=三种表达风格" |
| **Gemini 系** | **最简洁**；官方对 3.6 Flash 的定位是"更少多余编辑、更精炼输出"；适合流式/高频场景 |
| **DeepSeek V4** | 极啰嗦（思考链默认全输出），但**推理过程完整可审计**——适合需要可解释性的场景，成本需按 verbosity 重新核算 |
| **Kimi K3** | 中文表达自然、长文组织好；推理链长 |
| **GLM-5.2** | 代码输出规范、前端工程尤其强（WebDev 第 5） |

### 10.3 对工程的影响

1. **Token 成本 = 价格 × 啰嗦度**：DeepSeek V4 Flash 单价最低但输出 2.1×，**高并发场景务必设置 max_tokens 上限与摘要压缩**
2. **Agent 循环的上下文污染**：verbose 模型每次迭代回填大量思考内容，加速上下文膨胀（知识库已有"token 成本优化"经验：裁剪 description 收益极低，真正杠杆在选模型+限制输出）
3. **风格匹配**：前端/文档生成选 GLM/Gemini（简洁规范）；深度分析/审计选 Claude/DeepSeek（可解释）；流式实时选 Gemini Flash 系

---

## 11. 使用策略：分级路由与多模型协作

### 11.1 任务-模型匹配决策框架

```text
任务分类
+-- 高价值·低频率（架构设计/深度研究/长时程 Agent）
|     -> 旗舰档：Opus 5 / GPT-5.6 Sol / Kimi K3（开放）
+-- 日常·中频率（代码/分析/报告）
|     -> 均衡档：GLM-5.2 / Grok 4.5 / Gemini 3.6 Flash / Qwen3.8
+-- 批量·高频率（子任务/分类/抽取/翻译）
|     -> 轻量档：DeepSeek V4 Flash / GPT-5.6 Luna / Gemini 3.5 Flash-Lite
+-- 实时·交互（客服/流式/补全）
|     -> 速度档：Gemini 3.5 Flash / GLM-5.2 / Step 3.7 Flash
+-- 超长上下文（整库注入/全仓代码）
|     -> Llama 4 Scout (10M) / Grok (2M)
+-- 生成任务（图/视频/语音）
      -> 专用生成模型（Veo/Seedance/Imagen/Gemini Image）
```

### 11.2 高低阶模型配合（LLM Router 模式）

2026 年已形成成熟的**路由分层架构**，直接解决"全用旗舰太贵、全用轻量太笨"：

```text
                 +--------------------+
  用户请求 -----> |  Router (轻量模型    |
                 |  或规则/分类器)      |
                 +---------+----------+
                    难度判定 |
        +------------------+------------------+
        v                  v                  v
  简单任务            中等任务            复杂任务
  DeepSeek V4 Flash   GLM-5.2            Opus 5 / Sol
  Gemini Flash-Lite   Grok 4.5           Kimi K3
  $0.06/任务          $0.9/任务          $2-4/任务
```

**要点**：

- **Router 本身用轻量模型**（如 Gemini 3.5 Flash-Lite），只做意图/难度分类，成本可忽略
- **分级阈值要实测校准**：先小样本跑通 → 统计各档占比 → 核算总成本；原则是"80% 流量走轻量档，20% 走旗舰档"（成本可降 60-80%）
- **失败降级/升级**：轻量档不确定时（低置信度）自动升级到旗舰档（类似 Fable 5 的 Opus fallback 思路）

### 11.3 与脚本/工具配合（把模型当函数）

| 模式 | 做法 | 典型场景 |
|:-----|:-----|:---------|
| **结构化输出** | JSON Schema / 函数调用约束，模型只填字段 | 抽取、分类、表单 |
| **脚本编排** | 模型出决策，Python/Shell 执行重活（文件/网络/DB） | Agent 工具调用 |
| **并行 Fanout** | 一个任务拆 N 个子任务并行调轻量模型 | 批量审稿、批量摘要 |
| **HITL 检查点** | 关键步骤人审再放行 | 高风险自动化 |
| **确定性外壳** | 把反复验证的流程固化成脚本/工作流（见知识库 Agent 构成分析） | 周报、日报、巡检 |

**关键原则**（知识库 [`agent-composition`](../agent-engineering/2026-08-03-agent-composition-and-coding-agent-comparison.md) 的 L2 Loop 章节已论证）：**只有主循环是概率性的，其余全部确定性化**——能用脚本/规则/代码解决的不让模型做，模型只做"判断与生成"。

### 11.4 Agent 场景选型（主 Agent + 子 Agent）

| 角色 | 推荐 | 理由 |
|:-----|:-----|:-----|
| 主 Agent（规划/决策） | Opus 5 / GPT-5.6 Sol / Kimi K3 | 长时程规划、工具调用、可靠 |
| 子 Agent（执行/检索/抽取） | Gemini 3.5 Flash-Lite / DeepSeek V4 Flash | 官方定位"子代理"，跑量大成本低 |
| 编程 Agent | Gemini 3.6 Flash / Qwen3.8 / Claude Sonnet 5 | 官方编程定位 + WebDev 榜 |
| 长文档 Agent | Gemini 3.1 Pro / Llama 4 Scout | 1M-10M 上下文 |
| 多模态 Agent | Gemini 3.6 Flash | 全模态输入 |

**教训**：不要用同一个模型承担所有角色——主 Agent 用旗舰保证质量，子 Agent 用轻量控制成本，这是 2026 年 Agent 架构的标准形态（对应知识库 [`agent`](../agent-engineering/2026-08-03-ai-agent-deep-analysis.md) 分析的"多智能体四模式"）。

### 11.5 成本控制清单

1. **缓存优先**：长提示词/工具定义/系统提示务必复用缓存（选 cache hit 折扣大的模型，-90%~-98%）
2. **verbosity 治理**：max_tokens 上限 + 摘要压缩 + "简洁回答"指令（Gemini 系天然简洁）
3. **effort 分档**：日常用 low/medium，复杂任务才 max（Opus 5 max→high 只差 2 分但省大量思考 token）
4. **本地部署兜底**：高频稳定任务用 DeepSeek V4 Flash/GLM-5.2 自托管（13B/40B 激活，单机可跑）
5. **路由分流**：80/20 原则（§11.2）
6. **监控每任务成本**：不是看单价，是看"每任务 × 啰嗦度 × 调用量"（AA Cost per Task 是现成标尺）

### 11.6 面向本工作空间的推荐配置

结合本知识库运营场景（27 天 2.3B tokens 的经验教训）：

| 场景 | 推荐模型 | 理由 |
|:-----|:---------|:-----|
| 日常对话/轻任务（当前 deepseek-v4-flash） | DeepSeek V4 Flash | 已是最优性价比，$0.14 地板 |
| 深度分析/知识库专题（本文档这类） | Claude Opus 5 / GPT-5.6 Sol | 长时程推理质量 |
| 批量文档处理（多文档提取） | DeepSeek V4 Flash + GLM-5.2 并行 | 便宜 + 快 |
| 代码任务 | Qwen3.8 / Gemini 3.6 Flash | 编程双主线 + 简洁 |
| 超长上下文（知识库全量注入） | Kimi K3（1M）或 Scout（10M） | 长窗口 |
| 降本目标 | 路由：轻量为主 + 旗舰兜底 | 80/20 |

**当前运行时模型 deepseek-v4-flash 的选择是正确的**（智能 50 + 成本地板），若需质量跃迁，按任务升级到 GLM-5.2（开放权重中性价比最优）或旗舰档。

---

## 12. 演进趋势

### 12.1 六大技术趋势

| 趋势 | 代表 | 方向 |
|:-----|:-----|:-----|
| **扩散架构** | Celeris-1 (2158t/s) / Mercury 2 | 推理速度范式革命，向 1k-10k t/s 演进 |
| **Adaptive Reasoning** | Opus 5 五档 effort | 思考预算可调，质量-延迟-成本三方解耦 |
| **Fallback 工程** | Fable 5 + Opus 4.8 | 多模型可靠性编排，不确定时回退 |
| **稀疏注意力** | MiniMax M3 MSA | 长窗口成本从 O(N²) 向近线性演进 |
| **上下文 1M→10M** | 全系 1M、Scout 10M | 整库注入成为可能，RAG 退守超大场景 |
| **开放权重追赶** | Kimi K3 57 分 | 开源距专有 4 分，性价比反超 |

### 12.2 三大市场趋势

1. **分档产品线成为标准**：Sol/Terra/Luna、Opus/Sonnet/Fable、3.6 Flash/3.5 Flash-Lite——用户按"能力-成本"自由选择，单一模型通吃的时代结束
2. **国产价格战打穿地板**：$0.14/M（DeepSeek）与 $0.2/M（MiniMax）使"模型调用"成为边际成本趋零的公共品，**价值上移到编排层（Agent/工作流/知识管理）**——与本知识库"AI 探索是手段、业务沉淀是主线"的判断一致
3. **垂直专用化加速**：编程（Poolside/Qoder/Claude Code）、法律（Harvey）、金融（𝜏³-Banking 评测）、网络安全（Gemini 3.5 Flash Cyber）——通用模型之上长出专用层

### 12.3 对本工作空间的启示

- **基础设施含义**：1M 上下文普及 → KV Cache 分层存储（G3.5）需求更刚性；推理模型慢思考 → 持久化执行环境价值上升（对应知识库 [`G3.5`](../../02_rd/01_product/00_hardware/06_storage/kv-cache/2026-06-26-inference-context-memory-storage.md) 系列分析）
- **选型节奏**：模型 2-3 个月一代（Grok 4.20→4.5 三个月三代），**技术选型应半年级重评一次**，避免"锚定旧旗舰"
- **国产化主线**：服务器/数据中心领域（用户 P0 业务）的模型选择可放心走 Kimi/GLM/DeepSeek/Qwen 路线——能力已进全球前十且成本优势巨大

---

## 13. 面临的问题与挑战

### 13.1 评测与真实能力

1. **Benchmark 饱和/过拟合**：AA v4.1 已是第 4 次方法论升级（加入 GDPval-AA v2、AA-Briefcase 等真实任务评测），但头部模型分差仅 2-4 分，**评测噪声可能大于真实差距**——选型不能只看总分差 1-2 分
2. **发布即翻车风险**：Gemini 3.6 Flash 上线数小时即被曝早期实测问题；Qwen3.8 今日刚发布——**新模型需 2-4 周社区验证后再上生产**
3. **宣称 vs 实测**：MiniMax M3 "BrowseComp 超 Claude Opus"、Kimi K3 登顶设计榜——第三方复测未完全跟上

### 13.2 成本与工程

1. **慢思考成本**：max effort 的 TTFT 85-131s + verbosity 2×——"能力提升以响应变慢为代价"，交互场景与深度场景必须分治
2. **Agent 场景成本爆炸**：长循环 + 全量上下文 + 缓存未命中 → 单任务成本可达直接对话的 15×（知识库已实测 27 天 2.3B tokens）
3. **基础设施跟不上**：1M 上下文普及后，KV Cache/带宽/存储成为新瓶颈（知识库 G3.5 系列正在解决）

### 13.3 生态与可用性

1. **国内可用性断层**：Gemini/Claude/GPT 在国内无官方节点或时好时坏——**生产项目必须国产主力 + 国际 fallback 双轨**
2. **许可证陷阱**：Kimi K3 能力第一但商业授权受限——开源≠自由商用
3. **中文优化不均衡**：部分国际模型（如 Muse Spark）缺中文优化；国产模型在国际通用任务仍落后 4-10 分

### 13.4 战略层面

 1. **迭代速度吞噬选型决策**：Grok 三个月三代、阿里今日 2.4T——**"最佳模型"是移动靶**，工程上应做"模型抽象层"（一次接入、随时切换），而非绑定单一厂商
 2. **开源-专有鸿沟缩小但未消失**：Kimi K3 (57) vs Opus 5 (61)，差距仍在复杂长时程任务上放大（AA-Briefcase 等 agentic 评测差距 > 总分差距）
 3. **价值上移**：模型层趋同（都能接各家 API），**差异化回归编排层**——这与知识库 [`agent`](../agent-engineering/2026-08-03-ai-agent-deep-analysis.md) 的"2026 平台化进行时=基础设施铺设期"判断一致

---

## 参考文献

1. Artificial Analysis — Intelligence Index v4.1 & 模型详情页（2026-07-31 快照）：claude-opus-5 / claude-fable-5 / gpt-5-6-sol / kimi-k3 / glm-5-2 / deepseek-v4-flash / gemini-3-6-flash / grok-4-20
2. LLMRank — 大模型排行库（2026-08 收录 57 款）与 Gemini 3 系列选购指南（2026-05-26）
3. 澎湃/每经/新浪/InfoQ — 阿里 Qwen3.8 发布（2026-08-03，2.4T 参数，编程+专业办公）
4. Google DeepMind — Gemini 3.6 Flash Model Card（2026-07-21）与 The Keyword 博客
5. Celeris (celeris.ai) — Creating the world's fastest LLMs（扩散架构，2158 t/s）
6. 知识库内部：t01 模型评价两维度 / llm-comparative-analysis / agent-engineering 专题 / KV Cache G3.5 系列

## Changelog

| 日期 | 变更 | 说明 |
|:-----|:-----|:-----|
| 2026-08-03 | 创建 v1.0 | 六维对比框架 + 20 模型矩阵 + 分档使用策略 + 演进趋势；数据快照 2026-08-03（AA v4.1 / LLMRank / 官方发布） |
