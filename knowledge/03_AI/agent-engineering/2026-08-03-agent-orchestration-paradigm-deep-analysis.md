# 🧭 Agent 编排范式深度技术分析：multi-agent routing → Long Horizon 单一推理循环

> **元信息**: 文件状态=正式 | 覆盖范围=Agent 编排范式（orchestration paradigm）谱系、架构权衡与行业演进信号 | 版本=v1.0
> **适用范围**: Agent 平台架构设计、AI 产品编排层选型、推理基础设施规划、多代理系统评估
> **关键词**: Agent 编排 · multi-agent routing · Long Horizon · 单一推理循环 · hybrid orchestrator · flattened tools · progressive disclosure · context compaction · child instances · prompt caching · orchestrator-worker · 上下文连续性 · 工具面 · 迭代深度 · Rovo · Anthropic · Claude

## 目录 (TOC)

- [§0 执行摘要](#0-执行摘要)
- [§1 问题域：Agent 编排在解决什么](#1-问题域agent-编排在解决什么)
  - [1.1 编排的对象与三个核心张力](#11-编排的对象与三个核心张力)
  - [1.2 编排光谱：从单一循环到全路由](#12-编排光谱从单一循环到全路由)
- [§2 案例拆解：Rovo Chat 从路由回归单一推理循环](#2-案例拆解rovo-chat-从路由回归单一推理循环)
  - [2.1 第一代：Hybrid Orchestrator（2025-12）](#21-第一代hybrid-orchestrator2025-12)
  - [2.2 三个失效模式](#22-三个失效模式)
  - [2.3 第二代：Long Horizon 推理引擎（2026-07）](#23-第二代long-horizon-推理引擎2026-07)
  - [2.4 五项关键工程机制](#24-五项关键工程机制)
  - [2.5 量化结果](#25-量化结果)
  - [2.6 两代架构对比表](#26-两代架构对比表)
- [§3 对照案例：Anthropic 多代理研究系统](#3-对照案例anthropic-多代理研究系统)
  - [3.1 orchestrator-worker 模式](#31-orchestrator-worker-模式)
  - [3.2 量化证据：token 是性能第一变量](#32-量化证据token-是性能第一变量)
  - [3.3 适用边界：什么任务适合多代理](#33-适用边界什么任务适合多代理)
- [§4 两大案例的调和：范式本质澄清](#4-两大案例的调和范式本质澄清)
  - [4.1 否定的是"路由式多代理"，不是"并行分解"](#41-否定的是路由式多代理不是并行分解)
  - [4.2 任务形状决定范式](#42-任务形状决定范式)
  - [4.3 收敛趋势：单一协调上下文 + 按需并行子任务](#43-收敛趋势单一协调上下文--按需并行子任务)
- [§5 编排范式全景谱系](#5-编排范式全景谱系)
  - [5.1 五类范式定位](#51-五类范式定位)
  - [5.2 框架生态映射](#52-框架生态映射)
- [§6 范式选择的第一性原理分析](#6-范式选择的第一性原理分析)
  - [6.1 上下文连续性 vs 隔离](#61-上下文连续性-vs-隔离)
  - [6.2 工具面规模经济学](#62-工具面规模经济学)
  - [6.3 迭代深度与推理预算](#63-迭代深度与推理预算)
  - [6.4 Token 成本结构](#64-token-成本结构)
  - [6.5 可观测性与故障恢复](#65-可观测性与故障恢复)
  - [6.6 模型能力演进假设](#66-模型能力演进假设)
- [§7 对 AI 基础设施的影响](#7-对-ai-基础设施的影响)
  - [7.1 长上下文推理负载成为新常态](#71-长上下文推理负载成为新常态)
  - [7.2 Prompt Caching 的工程与硬件含义](#72-prompt-caching-的工程与硬件含义)
  - [7.3 对知识库与记忆系统的启示](#73-对知识库与记忆系统的启示)
- [§8 结论与预测](#8-结论与预测)
- [参考文献](#参考文献)
- [变更记录](#变更记录)

---

## §0 执行摘要

2026 年 7 月，Atlassian 宣布 Rovo Chat 架构转向：**用 Long Horizon 单一推理循环取代 multi-agent routing**（2025-12 引入的 hybrid orchestrator）。这是 Agent 编排范式演进的重要行业信号——**一家曾全力押注多代理路由的企业，在真实生产流量下回头拥抱"单模型 + 全上下文 + 迭代循环"**。

**核心结论（六大判断）**：

1. **编排范式不是"多代理 vs 单代理"的二选一，而是三个张力的平衡**：上下文连续性 vs 隔离、工具面规模 vs 可达性、迭代深度 vs 延迟。Rovo 的转向本质是**在这三个张力上重新校准**，而非范式全盘否定。
2. **路由式多代理的根本代价是"信息有损交接"**：每次 agent 间 handoff 都是 LLM 上下文到上下文的摘要转述（lossy paraphrase），中间推理、原始工具输出、错误详情在每一跳被压缩或丢弃——这是 Rovo 第二代放弃路由架构的直接原因。
3. **真正的收敛共识是"单一协调上下文 + 按需并行子任务"**：Rovo Long Horizon 保留了 child instances 并行分解，Anthropic 多代理系统的 lead agent 也持有全任务上下文——**两家的架构在本质上是同一模式的两端**。
4. **范式选择的决定性变量是"任务形状"**：宽而并行（breadth-first 研究）→ 多代理并行收益大；窄而深（跨产品多步操作）→ 单一循环上下文连续性强。Anthropic 与 Atlassian 的差异正是任务形状差异。
5. **量化规律**：token 用量解释多代理性能方差的 80%（Anthropic BrowseComp）；多代理 token 消耗是 chat 的 **15×**——编排范式是推理成本的第一杠杆，成本结构必须进入架构决策。
6. **对基础设施的含义**：150 次迭代推理循环 + 长上下文 = KV Cache 与 prompt caching 需求陡增；分层 prompt 组装 + 前缀缓存把增量成本降到"每次迭代仅处理最新 token"——**这直接呼应 G3.5 分层存储与 KV Cache 工程**。

---

## §1 问题域：Agent 编排在解决什么

### 1.1 编排的对象与三个核心张力

Agent 编排（orchestration）回答一个根本问题：**当任务需要多步推理、多工具调用、跨数据源操作时，如何组织模型的上下文与调用序列？**

编排架构围绕三个不可同时最优的张力展开：

| 张力 | 两端 | 失衡的代价 |
|:-----|:-----|:-----------|
| **上下文连续性 vs 隔离** | 单一长上下文（全知但拥挤） vs 多上下文（干净但割裂） | 拥挤→注意力稀释/超限；割裂→交接信息损失 |
| **工具面规模 vs 可达性** | 全部工具常驻（精确但贵） vs 按需披露（省但多一跳） | 常驻→schema token 成本随工具数线性增长；按需→发现延迟 |
| **迭代深度 vs 延迟** | 长迭代（深入但慢） vs 短迭代（快但浅） | 短→复杂任务触顶；长→简单查询体验劣化 |

任何编排架构都是这三者上的一个折中配置。Rovo 的两代架构是**同一折中空间里的两次截然不同的配置**——这是本文的核心分析对象。

### 1.2 编排光谱：从单一循环到全路由

```text
Single reasoning loop <------------------------> Full routing multi-agent
   |                                                    |
   |  Long Horizon (Rovo gen2)                          |  Hybrid Orchestrator (Rovo gen1)
   |  Claude Code single loop                           |  Anthropic Research (Opus lead)
   |  ChatGPT single agent + tools                      |  LangGraph supervisor
   |                                                    |  AutoGen / CrewAI / Swarm
   |     +----------------------------------+           |
   |     | convergence: single coord ctx    |           |
   |     | + on-demand parallel subtasks    |           |
   |     | (child instances)                |           |
   |     +----------------------------------+           |
```

光谱左端：一个模型持有全部上下文与工具，自主迭代；右端：协调者把任务分解给多个领域专家代理，各自持有独立上下文。**业界 2024-2025 年主流叙事偏右端（多代理），2026 年开始出现左端回归信号（见 §2-§4）**。

---

## §2 案例拆解：Rovo Chat 从路由回归单一推理循环

### 2.1 第一代：Hybrid Orchestrator（2025-12）

2025 年 12 月 Atlassian 引入 Rovo hybrid orchestrator，是典型的**分层多代理（hierarchical multi-agent）**：

```text
user query
   |
   v
Orchestrator LLM -- decompose query
   |  +--> JiraAgent (own context)
   |  +--> ConfluenceAgent (own context)
   |  +--> SlackAgent (own context)
   |        each subagent picks its product actions
   |  <-- each returns summary
   v
merge results -> answer
```

设计逻辑（当时合理）：早期 LLM 无法稳定处理大上下文与长工具目录，**把问题切给领域专家代理可保持上下文可控、工具选择准确**；对 1-2 次工具调用的聚焦问答非常高效。

### 2.2 三个失效模式

真实使用中（用户问"Find the bugs Jenny logged last month and remind me of the context from Slack"这类跨产品问题），三个架构约束逐一暴露：

| # | 失效模式 | 机制 | 后果 |
|:--|:---------|:-----|:-----|
| 1 | **有损上下文（lossy context）** | 每个 subagent 独立 LLM context；orchestrator 只收到摘要，**看不到原始工具输出、中间推理、错误详情** | 下游决策基于"二手有损视图"：跨产品连接丢失、重复搜索、故障时无法优雅恢复 |
| 2 | **迭代深度受限** | 系统优化 2-5 步任务（search→read→answer），iteration budget 低、timeout 保守 | "分析三个季度 sprint 速度"类任务频繁触顶，产出不完整 |
| 3 | **模型能力超出容器** | multi-agent 本是早期 LLM 的 workaround；新 frontier 模型能 hold 长上下文 + 大工具面 + 多步推理 | 旧架构**把新模型需要的思考上下文切碎了**——两代能力都无法利用 |

**关键洞察**：第三个失效模式是前两个的根因。当模型能力不足时，切分是必要的；当模型能力跨越阈值后，切分从"解决方案"变成"天花板"——**编排范式是模型能力的函数**（见 §6.6）。

### 2.3 第二代：Long Horizon 推理引擎（2026-07）

Long Horizon 的核心设计：**one LLM, one context, one iterative loop**。命名含义——"horizon"指 agent 能向前规划/推理/执行多远；旧架构是短视 horizon（单轮问答），新架构为长 horizon 设计（数百次迭代不丢思路）。

```text
Build system prompt (org/timezone/session state/skill templates)
   |
Select & prepare tools (filter + flatten to top-level actions)
   |
Loop (up to 150 iterations):
   +-- Call LLM (full conversation state + available tools)
   +-- tool call(s) -> execute in parallel -> add results to context -> continue
   +-- final answer -> deliver (with citations)
   |
Adaptive reasoning effort: minimal for lookups / deeper for multi-step research
```

**运作节奏**：大多数问题 3-8 次迭代解决；简单查询（"PROJ-123 状态？"）几乎零额外开销；复杂多步研究任务（"对比三个季度 sprint 速度并识别趋势"）深入规划。**adaptive reasoning effort** 让同一架构同时服务两个极端，避开"快而浅 / 深而慢"的一刀切。

### 2.4 五项关键工程机制

#### ① Flattened Tool Architecture（工具展平）— 最大架构变化

旧架构把每个产品包成 subagent（JiraAgent/ConfluenceAgent/...）；新架构把**每个产品能力展平为统一命名的顶层动作**，orchestrator LLM 直接调用：

```text
jira__search_issues
google_calendar__list_events
confluence__get_page
slack__lookup
...
```

- LLM 看到每个工具的**原始参数、原始响应、原始错误**——不是 subagent 的转述
- **失败恢复成为推理循环的一部分**：同一个 LLM 决定调用→读到失败→决定重试/换工具/向用户披露，不再经过"另一个 agent 转述发生了什么"
- **模型迁移从 N-way 变 1 次**：旧架构每次升级模型要逐 subagent 重新调优评估；新架构只评估 orchestrator 一次，所有产品工具随行

#### ② Progressive Disclosure（渐进式披露）— 工具面成本控制

几百个展平工具的 schema 每次迭代全发 = token 爆炸 + 工具选择准确率下降。方案：每个产品 namespace 折叠为两个 meta-tool：

```text
{product}__get_tool_schema  - on-demand full schema for one tool (desc has one-line summary of every tool in namespace)
{product}__invoke_tool      - execute a tool in that namespace by name
```

每个 namespace 配一份 **SKILL.md**（手写产品业务逻辑：何时用哪个工具、产品概念如何映射用户意图、常用多步 recipe、gotchas）——**旧架构藏在 subagent prompt 里的领域专长，被显式编码为技能文件**。最常用工具（search/todo/文件读写/实体链接/记忆检索）保持顶层常驻。

代价明确且接受：未用过的工具先 `get_tool_schema` 再 `invoke_tool`（每任务每工具一次）；SKILL.md 通常让模型直接 `invoke_tool` 跳过 schema 获取。

#### ③ Context Compaction Service（上下文压实）

150 次迭代对 context window 压力巨大。方案：**每次模型调用前运行压实服务**——接近 token 上限时修剪/总结旧工具输出，最近结果保持全分辨率；被剪输出不丢弃而是 offload，**模型需要细节时可按需读回**。长多步运行不丢已完成的推理。

#### ④ Task Decomposition via Child Instances（子实例分解）

宽任务（"调查上周结账错误激增：incidents + payment bugs + design docs + PRs + 客户反馈"= 5 条独立研究线索）不适合塞进单 context。方案：**为每条线索 spawn 一个 child instance**——同样是 one-LLM-one-context 循环，独立干净 context + 最相关 skill，并行运行；**最慢线索决定响应时间（非总和）**；父 orchestrator 只收每个 child 的完整结果并综合。

> ⚠️ **与旧 subagent 的本质区别**：旧 subagent 是"路由路径上的产品专家"（每次工具调用都经过它，orchestrator 永远看不到它看到的东西）；child instance 是**按需生成的完整推理循环**，独立拥有并完成一块研究后返回成品。并行是副作用，**主要动机是让每个 context 专注它需要思考的内容**。

#### ⑤ Prompt Assembly & Caching（分层组装 + 前缀缓存）

150 次迭代 × 相同 system prompt/skill/增长的历史 = 每次都要重新 tokenize 数十万 token。方案：**prompt 按稳定性分层**：

| 层 | 内容 | 变化频率 |
|:---|:-----|:---------|
| Static system prompt | 每次运行相同 | 恒定 |
| Stable session context | org/user/timezone/skill 指令 | 会话期稳定 |
| Conversation history | 早期轮次不可变 | 单调增长 |
| Turn-dependent context | 当前迭代工具结果与推理状态 | 每轮变 |

最长可能前缀在调用间 **byte-identical**：OpenAI/Gemini 隐式前缀缓存；Anthropic 在 system/stable-context/历史边界放显式 `cache_control` 标记。结果：**大多数迭代只需从头处理最新 token（通常是一个工具结果 + 下一步推理）**——成本与延迟收益随迭代数复利增长。

### 2.5 量化结果

| 指标 | 结果 | 口径 |
|:-----|:-----|:-----|
| 离线答案质量 | **+8.5%** | 硬性多工具查询集，LLM judge 对照参考答案 |
| Confluence 任务完成 | **+23%**（相对） | find page / retrieve content / create & edit 全流程 |
| 在线 Chat 成功率 | **+0.83%** | 高推理配置下 A/B（thumbs + 改写率 + 会话结果） |
| 端到端准确率 | **77% vs 71%**（+6pp） | 2+ 工具调用跨产品查询，LLM judge 评分 |
| 感知延迟 | **-37%** | 实时流式展示推理步骤替代静默等待 |

**质量-延迟权衡的再平衡**：简单无工具查询 TTFB 略升（但已较早期工程迭代大幅优化）；复杂查询"宁可多等几秒也要可信高质量"是用户共识。**感知延迟 -37% 的机制是透明度**——把模型的思考过程流式暴露给用户，等待从"黑盒沉默"变成"可见进展"。

### 2.6 两代架构对比表

| 维度 | Hybrid Orchestrator（1代） | Long Horizon（2代） |
|:-----|:--------------------------|:--------------------|
| 架构 | Coordinator + Specialists（LLM 选 agent → agent 选动作） | One LLM + 全部展平工具（直接调用） |
| 每工具调用 LLM 次数 | 2（orchestrator + subagent） | 1（直接） |
| 迭代预算 | 低个位数 | **100+（上限 150）** |
| 工具披露 | 每轮全量 | 展平 + 渐进披露（meta-tools + SKILL.md） |
| 质量门控 | 无 | **adaptive reasoning（复杂度感知深度）** |
| 上下文管理 | 无主动管理 | **95% token 水位显式驱逐 + offload** |
| 技能系统 | 无 | **14+ 预写 skill，per-tenant 可覆盖** |
| 超时 | 10 分钟 | 20 分钟 |
| 模型迁移成本 | N-way（逐 subagent 重调） | 1 次（orchestrator 单点） |

---

## §3 对照案例：Anthropic 多代理研究系统

### 3.1 orchestrator-worker 模式

Anthropic Claude Research（2025-06 发布）用**多代理**做开放域研究：lead agent（Opus）规划策略 → spawn 并行 subagents（Sonnet）分头搜索 → 各自返回精炼发现 → lead 综合、决定是否继续 → CitationAgent 做引用归位。这是**教科书式 orchestrator-worker**，与 Rovo 1 代同属"协调者+专家"家族。

关键设计（与 Rovo 1 代失效模式形成对照）：

- **Subagent 是"智能过滤器"**：并行探索后把最重要 token 压缩回 lead——本质是"以并行 context 窗口做压缩"，解决"信息超出单 context 窗口"的问题
- **Lead 持有全任务上下文**：把研究计划写入 Memory 持久化（context >200K 会被截断，必须保住计划）
- **子代理输出直写文件系统**：避免"telephone game"——不是所有结果都经 lead 转述，结构化产出（代码/报告/可视化）直接落盘，传引用而非拷贝

### 3.2 量化证据：token 是性能第一变量

| 数据点 | 数值 | 含义 |
|:-------|:-----|:-----|
| 多代理 vs 单代理（内部 research eval） | **+90.2%**（Opus 4 lead + Sonnet 4 subagents vs 单 Opus 4） | 宽而并行的研究任务，多代理显著胜出 |
| BrowseComp 方差解释 | token 用量 **80%**；+工具调用数+模型选择共 **95%** | **"花够 token"是性能第一杠杆** |
| 模型升级效应 | Sonnet 4 升级 > 双倍 token 预算（Sonnet 3.7） | 模型效率乘数 > 预算乘数 |
| 成本结构 | agents ≈ **4×** chat tokens；multi-agent ≈ **15×** chat tokens | 多代理烧 token 极快，需高价值任务才经济 |

### 3.3 适用边界：什么任务适合多代理

Anthropic 明确定义了**多代理的适用条件与不适用场景**：

**适合**（研究类）：① 高价值任务（值得 15× token）；② 可重度并行（breadth-first，多方向同时探索）；③ 信息量超出单 context 窗口；④ 需接入大量复杂工具。

**不适合**：① 需要所有 agent 共享同一 context 的域（状态强耦合）；② agent 间依赖多的任务；③ **大多数编码任务**（可并行子任务少，LLM 实时协调/委派能力仍不足）；④ 低价值任务（token 经济账算不过来）。

工程教训（对任何编排范式通用）：教 orchestrator 如何委派（objective + 输出格式 + 工具指引 + 边界）、按查询复杂度缩放 effort（简单=1 agent 3-10 calls；对比=2-4 subagents 10-15 calls；复杂=10+ subagents 分工）、工具描述质量决定成败（工具测试 agent 重写描述 → 后续任务完成时间 **-40%**）、并行工具调用（复杂查询时间 **-90%**）、extended thinking 作为可控草稿纸。

---

## §4 两大案例的调和：范式本质澄清

### 4.1 否定的是"路由式多代理"，不是"并行分解"

表象：Rovo 从多代理 → 单循环（否定）；Anthropic 从单代理 → 多代理（肯定）。看似矛盾，实则指向同一结论：

- Rovo 否定的**不是多代理，而是"路由路径上的领域专家代理"**——每次工具调用都要经过一个中间 agent，orchestrator 永远看不到原始数据。它否定的是一层**有损转译中介**。
- Rovo **保留了并行分解**：child instances 就是按需 spawn 的完整推理循环——与 Anthropic 的 subagents 本质同构（独立 context、并行、返回成品）。
- Anthropic 的 lead agent 也**持有全任务上下文与全部决策权**——它不是"丢给子代理就完事"，而是"用子代理扩展并行 token 预算"。

**结论**：业界真正的分水岭不是"几个模型"，而是**"原始信息是否直通决策者"**——凡是中间层做有损转述的（routing specialists），都在被淘汰；凡是"单一决策上下文 + 按需并行执行体"的，都在收敛。

### 4.2 任务形状决定范式

| 任务形状 | 特征 | 最优范式 | 代表 |
|:---------|:-----|:---------|:-----|
| **窄而深** | 跨产品多步操作、状态强耦合、上下文连续性强 | 单一推理循环 | Rovo Long Horizon（跨 Jira/Confluence/Slack 工作流） |
| **宽而浅/并行** | breadth-first 研究、多方向独立探索 | 并行多代理 | Claude Research（10+ subagents 分头搜索） |
| **窄而浅** | 单工具查询 | 直接调用（绕开循环） | Rovo 简单查询自适应降级 |
| **宽而深** | 多线索 × 每线索多步 | 单协调上下文 + child instances | Long Horizon child 分解（5 线索并发） |

Rovo 的场景（企业协作工具间的连续多步操作）本质是"窄而深"——**路由架构为"窄而浅"优化，自然在"窄而深"上失败**；Anthropic 的场景（开放域研究）本质是"宽而浅"——多代理并行是天然匹配。**两家都没有选错范式，只是任务形状不同**。

### 4.3 收敛趋势：单一协调上下文 + 按需并行子任务

综合两案，编排架构的**2026 收敛形态**是：

```text
Single coordinating context (full task view + all decisions)
   +-- call flattened tools directly (raw in/out/error)
   +-- spawn parallel subtasks on demand (own context, return finished)
   +-- layered prompt + prefix caching (min incremental cost)
   +-- compaction/eviction + offload (keep reasoning across long loops)
```

这与知识库 [Agent 平台工程四层框架](2026-08-03-agent-platform-engineering-deep-analysis.md) 的结论同构：执行层有状态沙箱 + 接口层稳定契约 + 平台层 Substrate——编排层正在从"路由拓扑"简化为"上下文管理 + 工具面 + 并行调度"三件事。

---

## §5 编排范式全景谱系

### 5.1 五类范式定位

| 范式 | 核心机制 | 优势 | 短板 | 代表 |
|:-----|:---------|:-----|:-----|:-----|
| **A. 单一推理循环** | 一模型全上下文迭代 | 上下文零损失、恢复内建、迁移 1 次 | 长任务 context 压力、宽任务低效 | Rovo LH · Claude Code |
| **B. 路由多代理** | 协调者按域路由给专家 | 领域隔离、prompt 简单 | 有损交接、N 路迁移、迭代浅 | Rovo 1代 · LangGraph supervisor |
| **C. 并行委派（orchestrator-worker）** | 协调者 spawn 并行执行体 | token 扩展、宽任务快 | 15× token 成本、协调复杂度 | Claude Research · Long Horizon child |
| **D. 分层编排** | 多级 agent 树 | 大组织级任务拆解 | 层级越多损失越大 | AutoGen group chat · MetaGPT |
| **E. 工作流脚本化** | 循环搬进代码（非模型临场） | 可执行/可观察/可复用 | 灵活度低、需预知路径 | [Loop Engineering](2026-06-26-agent-workflow-runtime-architecture.md) · LangChain chain |

### 5.2 框架生态映射

| 框架 | 默认范式 | 2026 动向 |
|:-----|:---------|:----------|
| LangGraph | B/D（supervisor + 状态图） | 状态机 + 检查点，可配任意拓扑 |
| OpenAI Agents SDK | B/C（handoff + 并行） | 从 Swarm 教学框架升级为生产 SDK |
| AutoGen / AG2 | D（group chat） | 会话式多代理，研究导向 |
| CrewAI | B（角色 crew） | 角色化路由，营销叙事强 |
| Google ADK | A/B（循环 + 子代理） | 与 Vertex AI 深度绑定 |
| Magentic-One | C（orchestrator + workers） | 微软通用任务编排 |

**趋势**：主流框架都在向"**可配置拓扑 + 循环内核**"演进——底层是单一循环运行时，上层可选配子代理/路由/并行。这与 §4.3 的收敛结论一致。

---

## §6 范式选择的第一性原理分析

### 6.1 上下文连续性 vs 隔离

**第一性原理**：LLM 的全部能力来自其上下文——**信息只要脱离当前上下文，对模型就是不存在**。编排的每一跳转述都是信息熵增：

```text
raw tool output (100% fidelity)
   -> subagent summary (~30-50%, loses detail/errors/intermediate state)
   -> orchestrator re-summary (~15-25%)
```

Rovo 1 代跨产品查询失败的直接原因：**orchestrator 在"自己工作的有损二手视图"上做下游决策**。隔离的价值只在"单 context 装不下"时成立（Anthropic 场景）；能装下时，连续性 > 隔离。

**设计判据**：任务状态能否被压缩进单 context（<200K token 量级）？能 → 优先单一循环；不能 → 用 child instances 按"可独立完成的块"切，而不是按"领域"切。

### 6.2 工具面规模经济学

**第一性原理**：工具 schema 是模型每轮都要"读"的 token；工具选择准确率随候选工具数下降（注意力稀释）。

```text
full-disclosure cost = SUM(schema tokens per tool) x iterations x cache-miss rate
progressive-disclosure cost = SUM(one-line summary tokens x iterations) + on-demand schema fetches
```

Rovo 的 meta-tool 方案（`get_tool_schema` + `invoke_tool` + SKILL.md）把成本从"工具数 × 迭代数"降为"工具数 + 实际使用工具 × 迭代数"——**常驻摘要 + 按需明细**是工具面规模化的标准解。注意与 [Agent 平台工程](2026-08-03-agent-platform-engineering-deep-analysis.md) 的"稳定契约 + Schema 即编译期类型"呼应：工具契约质量直接决定编排效率。

### 6.3 迭代深度与推理预算

**第一性原理**：复杂任务的成功率是"可尝试次数"的函数——迭代预算即失败恢复预算。Rovo 1 代"2-5 步优化"意味着**第 3 步后的失败无法恢复**；Long Horizon 150 次迭代意味着"试错 + 回退 + 换路"成为循环内建能力。

adaptive reasoning effort 的实质：**把推理预算变成模型可自我调节的变量**（简单查询 1 次推理、复杂查询 50 次）——避免"一刀切"的固定预算浪费。

### 6.4 Token 成本结构

**第一性原理**：编排范式是推理成本的第一杠杆——同一任务，多代理（15× chat）vs 单循环（~4× chat）差近 4 倍。

| 成本来源 | 单循环 | 路由多代理 | 并行多代理 |
|:---------|:-------|:-----------|:-----------|
| 基础对话 | 1× | 1× | 1× |
| 工具调用循环 | ~4× | ~6-8×（双重调用） | ~15×（子代理独立循环） |
| 前缀缓存收益 | 高（分层组装） | 低（每 subagent 独立 prompt） | 中 |
| 每迭代增量成本 | 仅最新 token（缓存后） | 全量重发（subagent 切换） | 子代理各付各的 |

**结论**：当任务价值不足以覆盖 15× token 时，多代理是负 ROI——这是 Rovo 转向的隐藏经济理由；当任务价值极高（研究/尽调）时，15× 买 90% 性能提升是划算的。

### 6.5 可观测性与故障恢复

- **单循环**：同一 LLM 决策→执行→读错→恢复，恢复路径最短；轨迹级 tracing 可把 40 步研究任务当分布式微服务调试（orchestrator span → 迭代 span → 工具 span）
- **路由多代理**：失败发生在 subagent 内部，orchestrator 只能靠"猜 subagent 看到了什么"恢复——**恢复决策基于有损信息，等于蒙着眼睛修**
- **Anthropic 的工程实践**：rainbow deployment（新老版本并行灰度，不打断运行中 agent）、checkpoint 恢复、端状态评估（不逐轮校验，看最终状态）——这些对任何范式都适用

### 6.6 模型能力演进假设

**核心规律：编排范式是模型能力的函数。**

```text
weak model (small ctx/poor tools)  -> split to compensate  -> multi-agent routing (workaround)
strong model (long ctx/big tools)   -> merge to benefit    -> single loop
```

Rovo 明确承认："multi-agent 设计不是意外，是 workaround——早期 LLM 处理不了大共享上下文和长工具目录"。Anthropic 同样承认多代理的"实时协调委派"瓶颈会随模型能力提升而缓解。

**推论**：随着 frontier 模型上下文与推理能力继续增长，**单一循环的适用域将持续扩大**；多代理将收缩到"纯并行扩展 token 预算"这一种理由（信息超单窗口 + 可并行）。未来 2-3 年编排架构的默认起点应是单一循环，多代理只在任务形状证明需要时引入。

---

## §7 对 AI 基础设施的影响

### 7.1 长上下文推理负载成为新常态

150 次迭代 × 每次迭代追加工具结果 = **单任务上下文可达数十万 token**，且并发用户 × 并发任务：

```text
per-task token traffic ~ iterations x delta-per-iteration x cache-miss rate
example: 150 iter x 2K tokens x 20% miss ~ 60K tokens from scratch + 240K cache reads
```

对推理基础设施的含义（呼应 [G3.5 分层存储](../../02_rd/01_product/00_hardware/06_storage/kv-cache/2026-08-03-g35-storage-software-architecture-jbof-deepseek-v4-pro.md)）：

- **KV Cache 压力陡增**：长会话 = KV 巨大，前缀复用是唯一救赎——**前缀感知的 KV 缓存池（PagedAttention 类）是单循环范式的必备件**
- **Prompt Caching 是成本命脉**：Rovo 的"分层组装 + byte-identical 前缀"在 Anthropic 侧用显式 `cache_control` 实现——**缓存命中率直接决定 150 迭代任务的经济性**（见 [KV Cache 硬件深度分析](../../02_rd/01_product/00_hardware/06_storage/2026-07-29-kv-cache-hardware-deep-analysis.md)）
- **热/温/冷分层**：会话活跃 KV（HBM）→ 前缀缓存（DRAM/CXL）→ 历史 offload（NVMe）——与 [AI 基础设施存储三维全景](../../02_rd/01_product/00_hardware/06_storage/2026-08-03-ai-storage-device-interconnect-integration-deep-analysis.md) 的四层梯队完全同构

### 7.2 Prompt Caching 的工程与硬件含义

Rovo 的实践揭示了基础设施层面的三个杠杆：

| 杠杆 | 机制 | 基础设施含义 |
|:-----|:-----|:-------------|
| 分层稳定性 | 按"最稳定→最易变"排序 prompt 层 | 长稳定前缀 = 高缓存命中 = KV 复用 |
| 显式 cache 标记 | Anthropic cache_control 边界 | 推理服务需暴露缓存控制 API |
| 工具面压缩 | meta-tools 减少每轮 schema token | 降低每迭代增量，间接降 KV 增长速率 |

### 7.3 对知识库与记忆系统的启示

- **Skills 系统**：Rovo 把领域专长编码为 SKILL.md（产品逻辑/recipe/gotchas）注入 system prompt——与 [Agent 工具链工程化](2026-06-26-agent-toolchain-cli-execution.md) 的"Skill 负责编排判断，CLI 稳定交付执行边界"完全同构；**知识库的"技能化"正是 Long Horizon 式编排的输入资产**
- **Context Compaction ≈ 知识蒸馏**：长任务的旧上下文压实 + offload 按需读回——与 [Agent 自进化五层](2026-06-26-agent-self-evolution-five-layers.md)、知识库分层（索引/摘要/原文）同构
- **可观测性**：轨迹级 tracing 是长循环任务调试的必需品——对服务器侧意味着 Agent 平台的遥测要升级到"推理步骤级"

---

## §8 结论与预测

**结论**：Rovo Chat 的架构转向不是孤例，而是**编排范式从"路由式多代理"向"单一推理循环 + 按需并行"迁移的标志性事件**。它的本质是对"有损转译中介"的否定，和对"原始信息直通决策者"的回归。

**六大预测**（2026-2028）：

1. **单一循环成为编排默认起点**：新 Agent 产品默认单模型循环 + 展平工具，多代理只在任务形状证明需要时引入
2. **"路由式多代理"（按域切分）加速退场**：被"按任务块切分的并行子任务"取代——child instances 而非领域专家
3. **工具面标准化（MCP + SKILL.md 式技能）成为编排层核心资产**：谁的工具契约质量高，谁的编排质量高
4. **Prompt Caching 从优化项变必需项**：150 迭代任务的经济性依赖前缀缓存命中率——推理基础设施的缓存能力成为竞争维度
5. **KV Cache 分层存储与编排深度绑定**：长上下文 Agent 负载是 G3.5/KV 分层存储的第一增长场景
6. **模型能力持续扩大单一循环适用域**：多代理收缩至"纯并行 token 扩展"，且随模型变强进一步收窄

---

## 参考文献

1. Atlassian: [Meet the new Rovo Chat: One prompt, multiple steps, zero hand-holding](https://www.atlassian.com/blog/rovo/long-horizon-whats-changed) (2026-07-28)
2. Atlassian: [Long Horizon: How Atlassian Built a Reasoning Engine for Complex AI Tasks](https://www.atlassian.com/blog/how-we-build/rovo-long-horizon-reasoning-engine) (2026-06-17)
3. Anthropic: [How we built our multi-agent research system](https://www.anthropic.com/engineering/built-multi-agent-research-system) (2025-06-13)
4. 知识库调研：项目管理动态跟踪 [2026-08-02](../../01_survey/project-mgmt/2026-08-02.md)（首次捕获 Rovo 转向信号）
5. 交叉引用：[Agent 平台工程](2026-08-03-agent-platform-engineering-deep-analysis.md) / [Agent OS 五种范式](2026-06-26-agent-os-five-paradigms.md) / [Loop Engineering](2026-06-26-agent-workflow-runtime-architecture.md) / [Claude Code 动态工作流](2026-06-26-claude-code-dynamic-workflows.md) / [工具链工程化](2026-06-26-agent-toolchain-cli-execution.md) / [KV Cache 硬件](../../02_rd/01_product/00_hardware/06_storage/2026-07-29-kv-cache-hardware-deep-analysis.md)

---

## 变更记录

| 日期 | 版本 | 变更 |
|:-----|:----:|:-----|
| 2026-08-03 | v1.0 | 创建；Rovo Long Horizon 两代架构拆解 + Anthropic 多代理对照 + 范式谱系 + 第一性原理权衡 + 基础设施影响 + 六大预测 |
