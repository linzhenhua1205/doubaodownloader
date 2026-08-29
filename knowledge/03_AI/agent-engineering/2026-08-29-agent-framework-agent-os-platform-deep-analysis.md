# Agent Framework / Agent OS / Agent Platform：定义、组件、运行机制与三者边界

> **概要**: 以"控制流归属 × 抽象层次"两轴拆解 Agent 生态四个高频混用概念——Agent Framework（编程原语库，LangGraph/OpenAI SDK/Claude SDK）、Agent OS（把 Agent 当进程管理的运行时基础设施，ETCLOVG 七层）、Agent Platform（Dify 类可视化编排平台）、微服务（确定性能力层）。逐一展开定义、组件构成（Model/Tools/Memory/Loop/Guardrails/Tracing）、运行过程（Agent Loop 六步循环 / OS 八步调度 / Platform LLMOps 闭环）；给出四者对比矩阵与"分层非替代"结论（微服务=工具面，Framework/Platform=编排层，Agent OS=运行时层）；附选型决策树与五条决策者判断。外部信源 LangChain(2026-07)/OpenAI SDK/Anthropic(2024-12)/Martin Fowler(2026-04)，内部交叉引用 Agent OS 五范式/Harness-OS 同构等 7 篇。
>
> **版本**: v1.0 | **日期**: 2026-08-29
> **核心问题**: ① Agent Framework / Agent OS / Agent Platform(Dify类) / 微服务 四个概念如何精确定义与区分？② 各自包含哪些组件、如何运行（操作过程）？③ 四者边界在哪、如何分层协同而非互斥？
> **元信息**: 文件状态=正式 | 覆盖范围=四概念的定义、组件构成、运行过程与边界对比
> **适用范围**: Agent 技术路线判断、Agent 平台选型、AI 应用架构设计、企业 AI 战略规划
> **关键词**: Agent Framework · Agent OS · Agent Platform · Dify · 微服务 · Agent Loop · Harness · ETCLOVG · 控制流归属 · 抽象层次 · MCP · LangGraph · OpenAI Agents SDK · Claude Agent SDK

## 📑 目录

<!-- TOC -->

- [1. 引言与范围](#1-引言与范围)
- [2. 术语坐标：一次定位四个概念](#2-术语坐标一次定位四个概念)
  - [2.1 四概念一句话定义](#21-四概念一句话定义)
  - [2.2 一维坐标轴：抽象层次 × 控制权归属](#22-一维坐标轴抽象层次--控制权归属)
- [3. Agent Framework 深度展开](#3-agent-framework-深度展开)
  - [3.1 定义：LLM 决定控制流](#31-定义llm-决定控制流)
  - [3.2 自主性光谱：六档分级](#32-自主性光谱六档分级)
  - [3.3 组件构成：四核心 + 两支撑](#33-组件构成四核心--两支撑)
  - [3.4 运行过程：Agent Loop 的六步循环](#34-运行过程agent-loop-的六步循环)
- [4. 主流 Agent Framework 全景对比](#4-主流-agent-framework-全景对比)
  - [4.1 六大框架速览](#41-六大框架速览)
  - [4.2 框架设计的两种哲学](#42-框架设计的两种哲学)
  - [4.3 框架之外的 Harness：Agent = Model + Harness](#43-框架之外的-harnessagent--model--harness)
- [5. Agent OS 深度展开](#5-agent-os-深度展开)
  - [5.1 定义：Agent 作为一等公民的系统抽象](#51-定义agent-作为一等公民的系统抽象)
  - [5.2 为什么叫 OS：进程模型的结构同构](#52-为什么叫-os进程模型的结构同构)
  - [5.3 ETCLOVG 七层架构](#53-etclovg-七层架构)
  - [5.4 五种驯服不确定性的范式](#54-五种驯服不确定性的范式)
  - [5.5 Agent OS 的运行过程](#55-agent-os-的运行过程)
- [6. Agent Platform（Dify 类）深度展开](#6-agent-platformdify-类深度展开)
  - [6.1 定义：面向应用开发的托管编排层](#61-定义面向应用开发的托管编排层)
  - [6.2 组件构成](#62-组件构成)
  - [6.3 运行过程与 LLMOps 闭环](#63-运行过程与-llmops-闭环)
- [7. 微服务范式回顾（对比基线）](#7-微服务范式回顾对比基线)
  - [7.1 核心特征](#71-核心特征)
  - [7.2 与 Agent 的本质差异：控制流与状态](#72-与-agent-的本质差异控制流与状态)
- [8. 四者对比：Framework × Platform × 微服务 × Agent OS](#8-四者对比framework--platform--微服务--agent-os)
  - [8.1 对比矩阵](#81-对比矩阵)
  - [8.2 两两边界辨析](#82-两两边界辨析)
  - [8.3 分层关系：不是替代，是上下层](#83-分层关系不是替代是上下层)
- [9. 演进趋势与选型决策](#9-演进趋势与选型决策)
  - [9.1 演进趋势](#91-演进趋势)
  - [9.2 选型决策树](#92-选型决策树)
  - [9.3 给技术决策者的五条判断](#93-给技术决策者的五条判断)
- [10. 参考文献](#10-参考文献)
- [变更记录](#变更记录)

---

## 1. 引言与范围

**本文回答一个问题**：当业界同时谈论 "Agent Framework"（LangGraph/OpenAI Agents SDK/Claude Agent SDK）、"Agent OS"（智能体操作系统）、"Agent Platform"（Dify 等可视化平台）与 "微服务" 时，它们分别指什么、由哪些组件构成、运行时如何运作，以及彼此之间到底是什么关系。

**写作动机**：这四个词常被混用——把 Dify 叫 "框架"、把框架叫 "平台"、把微服务架构说成 "没有智能体的 Agent 系统"。概念的混乱直接导致选型错误：用平台的能力边界去要求框架、用框架的开发成本去评估平台、把微服务当 Agent 的反义词。本文用**控制流归属**和**抽象层次**两个第一性维度把它们拆开，再逐层展开组件与运行机制。

**覆盖范围**：本文聚焦软件架构层面的概念辨析与机制展开，不涉及具体模型的推理细节、不涉及训练。外部信源以 2024-12 至 2026-08 的官方文档与权威工程文章为主。

**目标读者**：需要做 Agent 技术选型或架构设计的工程师/架构师；需要判断"自研框架 vs 低代码平台 vs 微服务改造"的技术决策者。

**术语约定**：文中 "Agent" 指"由 LLM 动态决定自身流程与工具使用的系统"（区别于 Workflow）[来源: Anthropic Building Effective Agents, 2024-12]。中文语境下 "智能体" 与 "Agent" 混用，本文统一用 "Agent"。

---

## 2. 术语坐标：一次定位四个概念

### 2.1 四概念一句话定义

| 概念 | 一句话定义 | 回答的核心问题 | 典型代表 |
|:-----|:-----------|:---------------|:---------|
| **Agent Framework** | 提供 Agent 编程原语（Agent/Tool/Memory/Loop/Handoff）的**代码库**，让开发者用代码构建 Agent | "怎么写一个 Agent？" | LangGraph、OpenAI Agents SDK、Claude Agent SDK、Google ADK、CrewAI |
| **Agent OS** | 把 Agent 当作操作系统管理的一等公民（进程/调度/内存/权限）的**运行时基础设施** | "Agent 如何在系统里被调度、隔离、治理？" | ETCLOVG 架构（概念）、各类 Agent Runtime（概念演进中） |
| **Agent Platform** | 提供可视化编排、托管运行时与 LLMOps 的**应用开发平台**，让业务人员不写代码组装 Agent 应用 | "怎么不写代码就搭一个 Agent 应用并运营？" | Dify、Coze、Flowise、LangFlow、n8n |
| **微服务** | 将业务能力拆分为**确定性**、独立部署、契约通信的分布式服务架构 | "业务能力如何确定性地拆分与扩展？" | Spring Cloud、Go Micro、K8s 上的服务网格 |

### 2.2 一维坐标轴：抽象层次 × 控制权归属

四个概念可以用两个正交维度定位：

```
Dimension A: who owns the control flow (who decides next step)
  code-fixed <--------------------+------------------> model at runtime
  Microservice / WF   Dify(manual)|  Agent Framework        Agent OS
                                  |        (code+LLM)       (system sched)
Dimension B: abstraction level (what granularity of problem)
  business capability < app assembly < programming primitives < sys resource mgmt
  Microservice          Dify           Framework                Agent OS
```

**核心论点**：
- **控制流归属**是 Agent 与非 Agent 的分水岭——代码路径定死的是 Workflow，模型在运行时决定下一步的是 Agent [来源: Anthropic, 2024-12; LangChain, 2026-07]。
- **抽象层次**是 Framework / Platform / OS 三者的分水岭——Framework 是"原语层"（给程序员），Platform 是"组装层"（给应用开发者），OS 是"资源管理层"（给系统运行时）。
- 微服务与 Agent **不在同一竞争维度**：微服务是"能力提供者"，Agent 是"能力消费者+编排者"。两者是上下层关系而非替代关系（详见 §8.3）。

---

## 3. Agent Framework 深度展开

### 3.1 定义：LLM 决定控制流

LangChain 在 2026-07-31 的官方定义：**An AI agent is a system that uses a large language model to decide the control flow of an application**（AI Agent 是用 LLM 决定应用控制流的系统）[来源: LangChain Blog, 2026-07-31]。

Agent 化程度取决于模型拥有多少控制权：一端是简单的 LLM Router，另一端是自主选择工具、跨长周期运行的系统。控制权越大，对可观测性、评估、记忆、权限与安全执行的基础设施要求越高 [来源: LangChain Blog, 2026-07-31]。

**Framework 的本质**：它是让开发者"以代码方式表达 Agent 控制流"的工具库。核心价值有三：
1. **封装 Agent Loop**（推理循环），免去手写 while 循环 + 工具分发的样板代码；
2. **提供原语组合**（Agent 作为工具、Handoff、Guardrail、Session），把复杂多 Agent 关系用少量抽象表达；
3. **内置可观测性**（Tracing），因为 Agent 的非确定性使调试成为首要工程问题。

### 3.2 自主性光谱：六档分级

LangChain 提出用"谁决定输出、谁决定下一步、谁决定可用步骤"三个决策来划分 6 级自主性（类比自动驾驶 L2-L5 的分级思路）[来源: LangChain Blog, 2026-07-31]：

| 级别 | 形态 | 输出决策 | 下一步决策 | 步骤可用性决策 |
|:----:|:-----|:--------:|:----------:|:--------------|
| L0 | 单一 LLM 调用 | 模型 | 代码 | 代码 |
| L1 | Chain（链式） | 模型 | 代码 | 代码 |
| L2 | Router（路由） | 模型 | 模型（从代码预设路由中选） | 代码 |
| L3 | State Machine（状态机） | 模型 | 模型（在状态转移图中） | 代码 |
| L4 | Agent（工具自主） | 模型 | 模型 | 模型（从工具集中选） |
| L5 | Autonomous Agent | 模型 | 模型 | 模型（可自建工具/记忆） |

> Voyager 论文（Minecraft 技能自举）是 L5 的典型：Agent 在跨次运行中学会新技能并复用 [来源: LangChain Blog 引用 Voyager]。

**工程含义**：不必争论"某个系统是不是真 Agent"，而应问"它处于哪个自主级别，该级别需要哪些基础设施"。多数生产系统落在 L2-L4 之间。

### 3.3 组件构成：四核心 + 两支撑

LangChain 归纳 Agent 内部必有四个组件 [来源: LangChain Blog, 2026-07-31]；加上生产化必需的支撑组件，共六类：

```
+--------------------------------------------------------+
|                 Agent (Framework Instance)             |
|                                                        |
|  +----------+  +-----------+  +-----------+  +------+  |
|  |  Model   |  |  Tools    |  |  Memory   |  | Loop |  |
|  +----------+  +-----------+  +-----------+  +------+  |
|       ^              ^              ^                  |
|  +----+-----+  +-----+-----+  +----+-----+             |
|  |Guardrails|  |    MCP    |  | Sessions |             |
|  +----------+  +-----------+  +----------+             |
|       ^                                                |
|  +----+-----+   Tracing (observability) crosscuts all  |
|  | Sandbox  |                                          |
|  +----------+                                          |
+--------------------------------------------------------+
```

| 组件 | 作用 | 典型实现/示例 |
|:-----|:-----|:-------------|
| **Model 模型抽象** | 决定下一步动作的大脑；封装多模型切换、结构化输出 | frontier LLM、Responses/Chat Completions 抽象、LiteLLM 适配 |
| **Tools 工具集** | 让 Agent 读取/改变外部世界；函数工具、托管工具、Agent-as-tool | API、数据库、代码执行、检索、其他 Agent、MCP server [来源: LangChain Blog] |
| **Memory 记忆** | 跨轮次/跨任务保持上下文 | 会话历史、长期状态存储、可编辑指令文件；OpenAI SDK 的 Sessions [来源: OpenAI Agents SDK docs] |
| **Loop 推理循环** | 串起 perceive→reason→act→observe→update | ReAct、Reflexion、plan-and-execute、orchestrator-worker [来源: LangChain Blog] |
| **Guardrails 护栏**（支撑） | 输入/输出并行校验、快速失败 | OpenAI SDK 的 input/output guardrails [来源: OpenAI Agents SDK docs] |
| **Tracing 可观测**（支撑） | 可视化/调试/评估 Agent 流 | LangSmith、OpenAI Tracing、Langfuse |

OpenAI Agents SDK 用"极少数原语"表达全部能力：**Agents**（带指令与工具的 LLM）、**Agents as tools / Handoffs**（Agent 间委托）、**Guardrails**（输入输出校验），配内置 Tracing [来源: OpenAI Agents SDK docs, 2026-08]。

### 3.4 运行过程：Agent Loop 的六步循环

Agent 的运行本质是"一个 LLM 跑在循环里" [来源: LangChain Blog, 2026-07-31]：

```
                  +--------------------------------+
                  |           Agent Loop           |
                  |                                |
   User Task      v                                |
 ----------> +----------+  +----------+  +---------+ |
             |  Read    |->|  Select  |->|  Invoke  | |
             |  State   |  |  Action  |  |  Tool    | |
             +----------+  +----------+  +----+----+ |
                 ^                          |         |
                 |        +-----------------+         |
                 |        v                           |
             +----------+  +----------+  +----------+ |
             |  Update  |<-|  Observe |<-|  Result  | |
             |  Memory  |  |  Result  |  |          | |
             +----------+  +----------+  +----------+ |
                 |                                     |
                 +--- Continue? -- No --> Final Output
```

**六步语义**（每轮迭代）：
1. **Read State**：读取当前状态（用户目标 + 会话上下文 + 记忆中的相关信息）；
2. **Select Action**：模型基于状态决定下一步动作（继续推理/调用工具/输出结果/委托子 Agent）——这是"模型拥有控制流"的关键一步；
3. **Invoke Tool**：执行所选动作，工具结果成为环境反馈（ground truth）[来源: Anthropic]；
4. **Observe Result**：观察执行结果，评估是否达成目标；
5. **Update Memory**：把本轮观察写入记忆（会话历史/长期状态），供后续轮次读取；
6. **Decide Continue**：判断任务是否完成，否则回到步骤 1 继续循环（可设最大迭代数作为停止条件 [来源: Anthropic]）。

**Anthropic 的关键工程建议**：Agent 实现通常很简单——"就是基于环境反馈在循环中使用工具的 LLM"；真正的复杂度在**工具集的设计与文档**（ACI，Agent-Computer Interface），而不是循环本身 [来源: Anthropic, 2024-12]。

---

## 4. 主流 Agent Framework 全景对比

### 4.1 六大框架速览

| 框架 | 出品方 | 核心抽象 | 设计取向 | 特点 |
|:-----|:-------|:---------|:---------|:-----|
| **LangGraph** | LangChain | 图（StateGraph 节点+边）、持久化 checkpoint、Human-in-loop | 低层控制、生产级 | 显式状态机、可中断/恢复、与 LangSmith 深度集成 [来源: LangChain 官网] |
| **OpenAI Agents SDK** | OpenAI | Agent / Handoff / Guardrail / Session | 轻量、Python 原生 | Swarm 的正式版；原语极少、上手快；内置 Tracing [来源: OpenAI docs] |
| **Claude Agent SDK** | Anthropic | Agent / Tool / Subagent / Skill | 简洁、与 Claude 深度绑定 | 强调简单组合模式；支持 Skills、沙箱 |
| **Google ADK** | Google | Agent / Tool / Flow / Session | 企业级、多 Agent | 与 Vertex AI / Gemini 生态集成 |
| **CrewAI** | 社区 | Crew / Agent / Task / Process | 角色扮演式多 Agent | "团队"隐喻，任务流程可编排 |
| **AutoGen / AG2** | Microsoft | ConversableAgent / GroupChat | 对话式多 Agent | 多 Agent 对话协议研究出身 |

### 4.2 框架设计的两种哲学

**哲学一：显式编排（低层控制）** —— LangGraph 为代表。开发者显式定义图结构（节点=处理步骤、边=转移条件），状态通过 checkpoint 持久化。适合需要精细控制、可中断恢复的生产系统，代价是学习曲线陡。

**哲学二：隐式自主（轻量原语）** —— OpenAI Agents SDK 为代表。开发者只需定义 Agent（指令+工具）与 Runner，循环由运行时托管；通过 Handoff 实现委托。适合快速构建、对控制流要求不苛刻的场景。

**Anthropic 的第三条立场**（2024-12，至今仍被广泛引用）：**"最成功的实现用的是简单可组合模式，而非复杂框架"**——建议先用 LLM API 直接起步，用框架务必理解底层代码，避免抽象层掩盖 prompt 与响应导致难调试 [来源: Anthropic, 2024-12]。这句话并非否定框架，而是提醒：框架的价值在"封装"，风险也在"封装"。

> ⚠️ 2026 年的市场修正：随着 Agent 进入生产，业界已从"追求框架特性"转向"框架+Harness+可观测"三位一体（见 §4.3）。LangChain 自身也强调框架无关的可观测（LangSmith 支持任意框架或裸代码）[来源: LangChain Blog, 2026-07]。

### 4.3 框架之外的 Harness：Agent = Model + Harness

Martin Fowler（Thoughtworks 杰出工程师 Birgitta Böckeler，2026-04-02 更新）给出生产级 Agent 的关键框架：**Agent = Model + Harness**——Harness 是"Agent 中除模型外的一切" [来源: Martin Fowler / Harness Engineering, 2026-04]。

```
Harness = Guides (feedforward) + Sensors (feedback) + Steering Loop
  |- Guides:  before-action steering -- AGENTS.md, Skills, scaffolds, arch rules
  |- Sensors: after-action observation & self-correction
  |           -- tests, linters, LLM-as-judge, structural checks
  `- two execution classes:
       Computational: deterministic, fast, cheap
                      -- tests/type-check/static analysis (ms-s)
       Inferential:   semantic, slow, expensive, non-deterministic
                      -- LLM review / LLM-as-judge (GPU/NPU)
```

核心概念：
- **Feedforward + Feedback 必须成对**：只有反馈没有前馈 → Agent 反复犯同样错误；只有前馈没有反馈 → 规则永远不知道是否生效 [来源: Martin Fowler]。
- **Steering Loop（转向循环）**：人类通过迭代 Harness 来引导 Agent——同一问题反复出现时，就强化对应的 guide/sensor。这是"人在环"的正确姿势：不是逐条审批，而是改进系统本身 [来源: Martin Fowler]。
- **Harnessability（可约束性）**：不是每个代码库都同样可被 harness——强类型语言天然有类型检查作 sensor；模块边界清晰才有架构约束规则可写 [来源: Martin Fowler]。
- **Ashby 必要多样性定律**：调节器必须具有至少与受控系统相当的多样性；Agent 能产出几乎任何东西，所以需要拓扑模板（topology）来收窄可能性空间，使 harness 可覆盖 [来源: Martin Fowler]。

**对本文的意义**：Framework 提供的是"循环与原语"，但生产 Agent 的成败更多取决于 Harness（引导与反馈体系）。这也是为什么 Framework 之间最终趋同（见 §5.2 的收敛现象）——差异化转移到 Harness 层。

---

## 5. Agent OS 深度展开

### 5.1 定义：Agent 作为一等公民的系统抽象

**Agent OS**（智能体操作系统）是把 Agent 当作操作系统管理的一等公民的运行时抽象：像进程一样管理 Agent 的生命周期、调度、资源、隔离、权限与通信。其动机来自一个根本观察——**单个 Agent 无法靠"更大的模型"解决所有问题，系统必须把多个 Agent 编排为可治理的整体**。

知识库已有文档给出终极公式：

> **Agent OS Engineering = 五种驯服不确定性范式的组合应用，在"执行者概率性 + 观测有限 + 假设腐化"约束下的特化实现** [来源: 知识库 agent-os-five-paradigms]

Agent 面临的不确定性有 6 个来源：LLM 输出概率性、Tool 调用失败、环境状态变化、**Context Window 有限**、多 Agent 并发、**模型升级行为漂移** [来源: 知识库 agent-os-five-paradigms]。其中"上下文窗口物理上限"与"模型升级导致的假设腐化"是 Agent 独有的、传统系统罕见的约束——这决定了 Agent OS 不能照搬传统 OS 设计。

### 5.2 为什么叫 OS：进程模型的结构同构

知识库另一篇深度文档论证了 **Harness 是 Agent 针对操作系统的适配层**，进程模型与 Agent 模型存在 12 项结构同构 [来源: 知识库 harness-os-process-boundary-isomorphism]。核心映射：

| 进程模型概念 | Agent 模型对应 | 约束来源 |
|:-------------|:---------------|:---------|
| 系统调用面 | 工具面（PTC 收窄） | Agent 只能通过有限工具访问世界，如同进程只能通过 syscall |
| 地址空间 | Context Window | 单进程装不下整个任务 → 需要分页/换出 |
| fork/exec | Subagent 派生 | 子 Agent 独立上下文、独立故障域 |
| 进程调度 | Subagent 调度 | 长任务需要抢占、恢复、生命周期管理 |
| 权限模型 | 工具权限/降权执行 | Subagent 可降权运行，最小权限原则 |
| 内存层级 | KV Cache 层级（HBM→DRAM→NVMe） | 上下文成本约束（见知识库 inference-context-memory-storage） |
| 微内核 | Harness = 运行在 LLM 之上的微内核 | 最小特权、消息传递、策略外置 |

**关键推论**："工具自由度收窄（PTC）"与"Subagent 化"这两个看似来自实践经验的规约，本质是进程边界的必然投影——**实践是发现者，进程边界是立法者** [来源: 知识库 harness-os-process-boundary-isomorphism]。

### 5.3 ETCLOVG 七层架构

知识库的 Agent OS 文档提出七层架构 [来源: 知识库 agent-os-five-paradigms]：

```
+--------------------------------------------+
| G - Governance & Security                   |
+--------------------------------------------+
| V - Verification & Evaluation               |
+--------------------------------------------+
| O - Observability                           |
+--------------------------------------------+
| L - Lifecycle & Orchestration  <-- core     |
+--------------------------------------------+
| C - Context & Memory                        |
+--------------------------------------------+
| T - Tool Interface & Protocol               |
+--------------------------------------------+
| E - Execution Environment                   |
+--------------------------------------------+
```

各层职责（浓缩）：
- **E 执行环境**：Agent 代码跑在哪（沙箱/容器/VM），隔离与资源配额；
- **T 工具接口协议**：工具如何被描述、发现、调用（MCP 是这一层的标准化尝试）[来源: Anthropic 提出 MCP]；
- **C 上下文与记忆**：Context Window 的管理——压缩、检索、分页、层级记忆；
- **L 生命周期与编排（核心）**：Agent 的创建/暂停/恢复/终止、子 Agent 调度、多 Agent 协作协议——对应传统 OS 的进程管理；
- **O 可观测性**：trace、日志、指标——Agent 非确定性下的调试基础设施；
- **V 验证与评估**：离线/在线 evals、LLM-as-judge、轨迹评估（trajectory eval）[来源: LangChain Blog]；
- **G 治理与安全**：权限、审计、合规、人类审批点（HITL）。

> 对照 LangChain 的自主性光谱：ETCLOVG 的 L 层对应"调度与控制"，C 层对应"上下文资源管理"，V/G 层对应"护栏与治理"——两套话语体系描述的是同一问题的不同侧面。

### 5.4 五种驯服不确定性的范式

Agent OS 从计算机 70 年历史的 10 个领域提炼出 5 种可复用范式 [来源: 知识库 agent-os-five-paradigms]：

| 范式 | 机制 | 适用不确定性 | 来源领域 |
|:-----|:-----|:-------------|:---------|
| **冗余 + 投票** | 多次执行取多数/最优 | LLM 输出概率性 | 通信编码、容错计算、量子纠错 |
| **闭环反馈** | 观测结果回注决策 | Tool 失败、环境变化 | 控制论、网络协议 |
| **约束空间** | 把可选项收窄到可验证集合 | Context 有限、权限 | 实时系统、数据库事务 |
| **确定性优先路由** ⭐ | 能确定性处理的路由绝不交给模型 | 高价值/可验证步骤 | 编译器、网络协议（最高 ROI） |
| **不可逆隔离** | 破坏性操作与主流程隔离 | 多 Agent 并发、故障扩散 | 分布式系统、数据库隔离 |

**组合策略**：生产系统通常是多范式组合，例如"确定性路由（范式四）负责流程骨架 + 闭环反馈（范式二）修正模型偏差 + 冗余投票（范式一）兜底关键决策"。

### 5.5 Agent OS 的运行过程

Agent OS 视角下的任务执行（对比 §3.4 的单 Agent Loop，这里是**系统级**循环）：

```
1. Admission      -> new task enters; OS allocates Agent instance + ctx quota
2. Scheduling     -> decide main Agent strategy; fork Subagents if needed
3. Execution      -> main/sub Agents run their own Loop (sec 3.4); tools via T layer
4. Resource mgmt  -> context exhausted: compress/swap (KV tier), throttle, quota
5. Observability  -> traces span all subtasks; O layer records in real time
6. Verification   -> V layer checks key outputs (offline/online eval)
7. Governance     -> sensitive ops trigger HITL approval; audit trail
8. Reclaim        -> task ends; reclaim Agent instances & resources (process reaping)
```

**与传统 OS 的对应**：受理≈进程创建、调度≈CPU 调度、资源管理≈内存管理、回收≈进程终止。差异在于——传统 OS 调度的是确定性程序，Agent OS 调度的是概率性执行体，因此 V/G 层（验证与治理）成为 Agent OS 独有的高权重层 [来源: 知识库 agent-os-five-paradigms]。

---

## 6. Agent Platform（Dify 类）深度展开

### 6.1 定义：面向应用开发的托管编排层

**Agent Platform** 是面向"应用开发者/业务人员"的 Agent 应用开发与运营平台：可视化编排工作流、托管运行时、内置模型网关、RAG 工具链与 LLMOps（观测/评估/版本管理）。Dify（GitHub ~153k★，2026-08 数据）是开源代表 [来源: 知识库 knowledge-base-software-progress-deep-analysis, 2026-08-20]。

**Platform 与 Framework 的本质区别**：
- Framework 卖给**程序员**：给原语，你写代码控制；
- Platform 卖给**应用开发者**：给画布与组件，你拖拽配置，运行时被平台托管。
- Framework 是 Platform 的**底层实现手段**之一（Dify 内部可挂载 LangChain/自研引擎）；Platform 是 Framework 的**上层封装**。

### 6.2 组件构成

Dify 类平台的典型组件（知识库已有 Dify 工作流深度分析 [来源: 知识库 dify-workflow-ai-app-deep-analysis, 2026-08-15]）：

| 组件 | 作用 |
|:-----|:-----|
| **可视化编排画布** | 拖拽式搭建 Workflow/Agent 流程（节点：LLM、知识检索、工具、代码、条件分支、Agent 节点） |
| **模型网关** | 统一接入多家 LLM（OpenAI/Anthropic/国产模型），可切换/降级 |
| **知识库/检索组件** | 文档解析、分段、向量索引、混合检索、ReRank |
| **工具市场** | 内置/自定义工具接入（HTTP 工具、MCP 工具、代码工具） |
| **Agent 节点/会话** | 对话式 Agent 运行（多轮、工具调用循环）、会话管理 |
| **LLMOps** | 日志、标注、评估、Prompt 版本管理、A/B、发布 |
| **应用形态输出** | WebApp/API/嵌入（嵌入到现有系统） |

### 6.3 运行过程与 LLMOps 闭环

Platform 的运行过程 = **编排图实例化 + Agent 循环托管 + 运营闭环**：

```
1. Design    -> business users draw the orchestration graph
                (workflow or agent nodes), config model/KB/tools
2. Deploy    -> platform generates a runnable app; expose API/WebApp
3. Run       -> agent nodes run the Agent Loop (sec 3.4);
                workflow nodes follow deterministic orchestration
4. Observe   -> logs/traces collected (platform-hosted, no self-build)
5. Evaluate  -> online evals on production traces, human annotation
6. Iterate   -> tune prompt/flow/KB -> redeploy (LLMOps loop)
```
+-----------------------------------------------------+
| Application layer (business semantics)              |
|   Agent apps / Chatbots / KB assistants / automation|
+-----------------------------------------------------+
| Orchestration layer (decision)                      |
|   Agent Platform (Dify-like): canvas + LLMOps       |
|   Agent Framework: Agent Loop + primitives + Harness|
+-----------------------------------------------------+
| Runtime layer (scheduling / resource / governance)  |
|   Agent OS: lifecycle / sched / ctx resource /      |
|             permission / verification               |
+-----------------------------------------------------+
| Capability layer (deterministic execution)          |
|   Microservices: business APIs / data / tx /        |
|                  integration                        |
+-----------------------------------------------------+
```
+-----------------------------------------------------+
| Application layer (business semantics)              |
|   Agent apps / Chatbots / KB assistants / automation|
+-----------------------------------------------------+
| Orchestration layer (decision)                      |
|   Agent Platform (Dify-like): canvas + LLMOps       |
|   Agent Framework: Agent Loop + primitives + Harness|
+-----------------------------------------------------+
| Runtime layer (scheduling / resource / governance)  |
|   Agent OS: lifecycle / sched / ctx resource /      |
|             permission / verification               |
+-----------------------------------------------------+
| Capability layer (deterministic execution)          |
|   Microservices: business APIs / data / tx /        |
|                  integration                        |
+-----------------------------------------------------+
```

**读图要点**：
1. 微服务在最底层——Agent 的工具面（Tools）绝大多数是微服务 API；
2. Framework 与 Platform 是编排层的两种形态：Framework 偏"代码编排"，Platform 偏"画布编排"，可共存（Platform 内部可调 Framework）；
3. Agent OS 是编排层之下的运行时层——它不管"业务逻辑怎么写"，只管"Agent 怎么跑得稳、隔离、可治理"；
4. 一个完整栈的典型形态：**微服务提供能力 → Framework/Platform 构建 Agent → Agent OS 调度治理 → 应用交付**。

---

## 9. 演进趋势与选型决策

### 9.1 演进趋势

**趋势一：从 Workflow 到 Agent 再到多 Agent（已发生）**
生产系统正沿着"确定性工作流 → 带 Agent 节点的混合编排 → 多 Agent 协同"演进。Anthropic 明确：能用 Workflow 就不用 Agent，能用单一 Agent 就不用多 Agent——**上下文溢出、能力蔓延、团队边界**才是升级到多 Agent 的正当理由 [来源: Anthropic, 2024-12; LangChain Blog]。

**趋势二：Harness Engineering 成为生产化主线（进行中）**
框架趋同后，竞争转移到 Harness：引导（Skills/AGENTS.md）、传感器（测试/linter/LLM-judge）、转向循环。Martin Fowler 判断这是"持续工程实践而非一次性配置" [来源: Martin Fowler, 2026-04]。

**趋势三：Agent OS 从概念走向工程化（萌芽期）**
行业数据佐证基础设施需求：McKinsey 2025-11 调查显示 **62% 的组织在实验 Agent，但任何业务职能中规模化的不超过 10%**；Gartner 预测 **2027 年底前 >40% 的 Agentic AI 项目将因成本失控/价值不清/风险控制不足被取消** [来源: LangChain Blog 引用 McKinsey/Gartner]。规模化瓶颈（可观测、评估、沙箱、权限）正是 Agent OS 的战场。

**趋势四：工具协议标准化（MCP/A2A）**
MCP 统一"Agent-工具"接口，A2A 统一"Agent-Agent"通信——这些标准是 Agent OS 的 T 层与 L 层的"事实协议"，将加速 Agent OS 形态收敛 [来源: Anthropic 提出 MCP; 知识库 .NET A2A 素材]。

### 9.2 选型决策树

```
What is your need?
|
|-- Standard agent apps (RAG/support/KB), business users involved?
|     `-> Agent Platform (Dify/Coze) -- fast start, built-in LLMOps
|
|-- Deep customization, complex control flow, deep codebase integration?
|     `-> Agent Framework (LangGraph / OpenAI SDK / Claude SDK)
|         criteria: explicit state machine + resume -> LangGraph
|                   lightweight + Python-native     -> OpenAI Agents SDK
|                   Claude-deep-binding + Skills    -> Claude Agent SDK
|
|-- Existing microservices, want to add Agents?
|     `-> keep microservices; Agents consume them via MCP/API
|         (layering, not rewriting)
|
|-- Agent count scaling up (>10, org-level)?
|     `-> design Agent OS capabilities early: unified scheduling /
|          context resource mgmt / permission / verification / HITL
|         (2026: assemble via platform-eng + mesh + policy engine + obs)
|
`-- Mixed scenario (most common)?
      `-> Platform for app layer + Framework for custom nodes
          + Microservices for capability layer + reserve OS governance
```

### 9.3 给技术决策者的五条判断

1. **概念先于选型**：先问"控制流归谁"，再问"用什么工具"。控制流需要运行时决策 → Agent 路线；可定死 → 别用 Agent（成本与不确定性都是负资产）[来源: Anthropic]。
2. **框架会趋同，Harness 是护城河**：选择框架时把 40% 的评估权重放在"它能否接好你的 Harness 体系"（可观测/评估/引导注入），而非框架特性清单。
3. **Platform 与 Framework 不是竞争是分层**：Dify 类平台的最佳实践是"画布管常规、自定义节点下沉框架、能力走微服务"——三者共存是常态而非例外。
4. **微服务是 Agent 的地基不是对手**：Agent 的每个工具调用背后几乎都是一个确定性服务；把 Agent 引入现有微服务体系是"叠加决策层"而非"推翻重构"。
5. **为 Agent OS 留接口**：即便今天只做 3 个 Agent，也按"可调度、可隔离、可治理、可审计"四个属性设计——这是未来规模化时不用推倒重来的最小投资。

---

## 参考文件

### 内部知识库引用

| # | 来源 | 用途 |
|:-:|:-----|:-----|
| [1] | [Agent OS：五种驯服不确定性的范式](2026-06-26-agent-os-five-paradigms.md) | §5.1-5.4 ETCLOVG 七层架构、六来源不确定性、五范式 |
| [2] | [Harness 即适配层：Agent 与操作系统进程的边界同构](2026-08-05-harness-os-process-boundary-isomorphism.md) | §5.2 进程模型 12 项结构同构、PTC 必然性、微内核 |
| [3] | [AI Agent 深度分析：定义、模式、产业与基础设施全景](2026-08-03-ai-agent-deep-analysis.md) | §3 Agent 定义与判定维度基线 |
| [4] | [Agent 平台工程：设计模式与业界实践深度专题](2026-08-03-agent-platform-engineering-deep-analysis.md) | §6-8 平台四层架构（执行/接口/平台/生态） |
| [5] | [Agent 编排范式深度技术分析](2026-08-03-agent-orchestration-paradigm-deep-analysis.md) | §9.1 multi-agent routing → Long Horizon 编排演进 |
| [6] | [Dify 工作流与 AI 应用开发深度分析](2026-08-15-dify-workflow-ai-app-deep-analysis.md) | §6 Dify 可视化编排/Agent 节点/LLMOps |
| [7] | [知识库软件研发进展全景（2024-2026）](../../07_industry-research/04_ai/2026-08-20-knowledge-base-software-progress-deep-analysis.md) | §6.1 Dify 153k★、平台形态演进 |
| [8] | [LLM 推理的 Context Memory Storage](../../02_rd/01_product/00_hardware/06_storage/kv-cache/2026-06-26-inference-context-memory-storage.md) | §5.5 KV Cache 层级与 Agent 长上下文约束 |

### 外部资料引用

| # | 来源 | 用途 |
|:-:|:-----|:-----|
| [9] | LangChain Blog, "What is an AI agent?", 2026-07-31 | §3.1-3.4 Agent 定义、自主性光谱、四组件、ADLC、McKinsey/Gartner 数据 |
| [10] | OpenAI Agents SDK 官方文档, 2026-08 | §3.3-4.2 原语设计（Agent/Handoff/Guardrails）、Sessions、Sandbox agents |
| [11] | Anthropic, "Building Effective Agents", 2024-12-19 | §3.1/3.4/7.2 Workflow vs Agent 判据、增广 LLM、五种 workflow 模式、ACI |
| [12] | Martin Fowler / Birgitta Böckeler, "Harness Engineering for Coding Agent Users", 2026-04-02 | §4.3 Agent=Model+Harness、前馈/反馈控制、Computational/Inferential、Ashby 定律 |
| [13] | McKinsey, "State of AI Survey", 2025-11（经 [9] 引用） | §9.1 62% 组织实验 Agent、≤10% 规模化 |
| [14] | Gartner 预测 2026（经 [9] 引用） | §9.1 2027 底 >40% Agentic AI 项目被取消 |
| [15] | Voyager 论文（经 [9] 引用） | §3.2 L5 自主 Agent 示例（Minecraft 技能自举） |
| [16] | 素材：AI Agent 走出 Demo 幻觉的唯一解药：Harness Engineering（cnblogs 转载） | §4.3 Harness 工程化背景（素材级，与 [12] 交叉验证） |

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-29 | v1.0 | 首次创建。四概念（Agent Framework / Agent OS / Agent Platform / 微服务）的定义、组件、运行机制与边界对比；外部信源 LangChain(2026-07)/OpenAI SDK/Anthropic(2024-12)/Martin Fowler(2026-04) + 内部 agent-os-five-paradigms / harness-os-process-boundary-isomorphism 等交叉引用；给出对比矩阵、分层模型与选型决策树 |
