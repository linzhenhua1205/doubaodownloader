# AI编程范式演进深度调研

> **概要**: AI 编程范式五阶段演进：Completion、Agent、Harness 等深度调研
>
> **关键词**: 编程范式 · Completion · Agent · Harness · FIM

---

## 📑 目录

- [1. 概览：五阶段演进全景](#1-概览五阶段演进全景)
  - [1.1 范式演进图谱](#11-范式演进图谱)
  - [1.2 三个核心驱动力](#12-三个核心驱动力)
  - [1.3 范式跃迁的力学本质](#13-范式跃迁的力学本质)
  - [1.4 各范式核心特征对比](#14-各范式核心特征对比)
- [2. Completion 范式（补齐）](#2-completion-范式补齐)
  - [2.1 定义与原理](#21-定义与原理)
  - [2.2 数学本质：为什么代码适合自回归建模？](#22-数学本质为什么代码适合自回归建模)
  - [2.3 解决的根本问题](#23-解决的根本问题)
  - [2.4 FIM (Fill-in-the-Middle)：补全范式的关键突破](#24-fim-fill-in-the-middle补全范式的关键突破)
    - [2.4.1 因果 LM 的问题](#241-因果-lm-的问题)
    - [2.4.2 FIM 的训练机制](#242-fim-的训练机制)
    - [2.4.3 FIM 的统计本质](#243-fim-的统计本质)
  - [2.5 三种子模式](#25-三种子模式)
  - [2.6 技术限制——信息孤岛瓶颈](#26-技术限制信息孤岛瓶颈)
    - [2.6.1 信息孤岛的三个层次](#261-信息孤岛的三个层次)
    - [2.6.2 量化影响](#262-量化影响)
  - [2.7 里程碑](#27-里程碑)
- [3. Agent 范式（智能体）](#3-agent-范式智能体)
  - [3.1 定义与原理](#31-定义与原理)
  - [3.2 解决的根本问题](#32-解决的根本问题)
  - [3.3 产品演化链](#33-产品演化链)
  - [3.4 Agent 核心能力组件](#34-agent-核心能力组件)
  - [3.5 Agent 的内部架构](#35-agent-的内部架构)
    - [3.5.1 IDE Agent vs CLI Agent：根本架构差异](#351-ide-agent-vs-cli-agent根本架构差异)
    - [3.5.2 Agent 的认知架构：System 1 / System 2](#352-agent-的认知架构system-1-system-2)
  - [3.6 上下文管理：Agent 最被低估的工程挑战](#36-上下文管理agent-最被低估的工程挑战)
    - [3.6.1 上下文的拼接策略](#361-上下文的拼接策略)
  - [3.7 技术限制](#37-技术限制)
  - [3.8 标志性数据](#38-标志性数据)
- [4. Harness 范式（约束框架）](#4-harness-范式约束框架)
  - [4.1 定义与原理](#41-定义与原理)
  - [4.2 解决的根本问题](#42-解决的根本问题)
  - [4.3 三层约束模型（Defense in Depth）](#43-三层约束模型defense-in-depth)
  - [4.4 确定性优先路由（INV-R）](#44-确定性优先路由inv-r)
  - [4.5 Toolformer → MCP → A2A 协议演化](#45-toolformer-mcp-a2a-协议演化)
  - [4.6 代表实现](#46-代表实现)
  - [4.7 深度框架：Agent OS 五种驯服不确定性的范式](#47-深度框架agent-os-五种驯服不确定性的范式)
    - [4.7.1 不确定性的六个来源](#471-不确定性的六个来源)
    - [4.7.2 五种范式映射](#472-五种范式映射)
    - [4.7.3 分布式系统的可直接复用与必须重造](#473-分布式系统的可直接复用与必须重造)
  - [4.8 技术限制](#48-技术限制)
- [5. Loop 范式（循环）](#5-loop-范式循环)
  - [5.1 定义与原理](#51-定义与原理)
  - [5.2 解决的根本问题](#52-解决的根本问题)
  - [5.3 Loop 谱系：从简单到复杂](#53-loop-谱系从简单到复杂)
  - [5.4 五种 Loop 子模式详解](#54-五种-loop-子模式详解)
    - [5.4.1 ReAct (Reason + Act) — 基础循环](#541-react-reason-act-基础循环)
    - [5.4.2 Plan & Solve — 先规划后执行](#542-plan-solve-先规划后执行)
    - [5.4.3 Reflection — 自我审校](#543-reflection-自我审校)
    - [5.4.4 Reflexion — 引入记忆的反射学习](#544-reflexion-引入记忆的反射学习)
    - [5.4.5 LATS (Language Agent Tree Search) — 树搜索](#545-lats-language-agent-tree-search-树搜索)
  - [5.5 性能对比（HumanEval）](#55-性能对比humaneval)
  - [5.6 编程中的典型 Loop 应用](#56-编程中的典型-loop-应用)
  - [5.7 ReAct 的软肋：为什么需要 Dynamic Workflow](#57-react-的软肋为什么需要-dynamic-workflow)
  - [5.8 Dynamic Workflow：把 Loop 从提示词搬进代码](#58-dynamic-workflow把-loop-从提示词搬进代码)
    - [Skill vs Workflow 对比](#skill-vs-workflow-对比)
  - [5.9 收敛问题：Loop 会不会永远不结束？](#59-收敛问题loop-会不会永远不结束)
    - [5.9.1 Loop 的三种终止条件](#591-loop-的三种终止条件)
    - [5.9.2 何时收敛，何时发散？](#592-何时收敛何时发散)
  - [5.10 技术限制](#510-技术限制)
- [6. Graph 范式（图谱）](#6-graph-范式图谱)
  - [6.1 定义与原理](#61-定义与原理)
  - [6.2 解决的根本问题](#62-解决的根本问题)
  - [6.3 核心理论渊源](#63-核心理论渊源)
  - [6.4 三种 Graph 子模式](#64-三种-graph-子模式)
    - [6.4.1 StateGraph (有状态图) — LangGraph 模式](#641-stategraph-有状态图-langgraph-模式)
    - [6.4.2 MultiAgent Graph (多Agent图) — 通信拓扑](#642-multiagent-graph-多agent图-通信拓扑)
    - [6.4.3 Adaptive Graph (自适应图)](#643-adaptive-graph-自适应图)
  - [6.5 代表框架对比](#65-代表框架对比)
  - [6.6 编程场景中的 Graph 应用](#66-编程场景中的-graph-应用)
  - [6.7 Pregel/BSP 模型：LangGraph 的底层理论](#67-pregelbsp-模型langgraph-的底层理论)
    - [6.7.1 BSP 模型的三阶段](#671-bsp-模型的三阶段)
  - [6.8 多 Agent 通信拓扑：三种基本模式](#68-多-agent-通信拓扑三种基本模式)
  - [6.9 状态爆炸：Graph 最大的隐性成本](#69-状态爆炸graph-最大的隐性成本)
    - [6.9.1 状态增长模型](#691-状态增长模型)
    - [6.9.2 解决策略](#692-解决策略)
  - [6.10 技术限制](#610-技术限制)
- [7. 范式跃迁的力学分析](#7-范式跃迁的力学分析)
  - [7.1 跃迁驱动力分析](#71-跃迁驱动力分析)
  - [7.2 跃迁阻力分析](#72-跃迁阻力分析)
  - [7.3 跃迁速度对比](#73-跃迁速度对比)
  - [7.4 范式共存：不是替代关系](#74-范式共存不是替代关系)
- [8. 经济性分析：各范式的成本结构](#8-经济性分析各范式的成本结构)
  - [8.1 成本构成模型](#81-成本构成模型)
  - [8.2 LLM 占比下降趋势](#82-llm-占比下降趋势)
  - [8.3 成本/质量权衡曲线](#83-成本质量权衡曲线)
  - [8.4 成本控制策略](#84-成本控制策略)
- [9. 跨范式对比与选择依据](#9-跨范式对比与选择依据)
  - [9.1 按任务复杂度选择](#91-按任务复杂度选择)
  - [9.2 ROI 分析（从工程实践角度）](#92-roi-分析从工程实践角度)
  - [9.3 组合使用（实际工程中的常态）](#93-组合使用实际工程中的常态)
- [10. 关键时间线与里程碑](#10-关键时间线与里程碑)
  - [10.1 时间线图谱](#101-时间线图谱)
  - [10.2 SWE-bench 关键演进](#102-swe-bench-关键演进)
- [11. 趋势展望与未解决问题](#11-趋势展望与未解决问题)
  - [11.1 确定性趋势：从"LLM核心"到"Harness核心"](#111-确定性趋势从llm核心到harness核心)
  - [11.2 未解决的挑战](#112-未解决的挑战)
  - [11.3 下一阶段：Agent OS（2026+）](#113-下一阶段agent-os2026)
  - [11.4 关键预测](#114-关键预测)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 1. 概览：五阶段演进全景

### 1.1 范式演进图谱

```text
2017-2021    2022-2023      2023-2024      2024-2025      2025-2026
Completion --> Agent -------> Harness ------> Loop ---------> Graph
  |            |              |              |              |
  v            v              v              v              v
 token-pred    multi-tool     struct-const   feedback-loop  DAG
 local-ctx     full-file      det-first      reflect-fix    multi-agent
 stateless     stateful       defense-depth  self-heal      declarative
```

### 1.2 三个核心驱动力

| 驱动力 | 描述 | 效果 |
|:-------|:-----|:-----|
| **模型能力增长** | 从 GPT-3 (175B, 2020) → GPT-4 (推测 1.8T, 2023) → GPT-5.5 (2026)，推理/上下文/指令遵循持续提升 | 每个新范式都建立在更强的模型基座上 |
| **上下文窗口扩展** | 2K (GPT-3) → 128K (GPT-4) → 1M+ (GPT-5.5/Gemini) → 2M (Claude) | 从"感知几行"到"感知整个代码库" |
| **工具接口标准化** | 无工具 → Function Calling (2023.06) → MCP (2024.11) → A2A (2025.04) | Agent与外部世界的交互从"手写胶水代码"到"标准化协议" |

[来源: AI技术演进年度总结, knowledge/03_AI/llm-techniques-principles/2026-06-28-ai-technology-evolution-annual-summary.md]

### 1.3 范式跃迁的力学本质

每个范式跃迁都不是"发明了新东西"，而是**解决了前一个范式的瓶颈**，但同时也**引入了新的约束**：

```text
跃迁        瓶颈 (解决了什么)            新引入的约束
-------     -------------------           ------------------
Completion -> Agent:  信息孤岛             概率性执行不可靠
Agent -> Harness:     概率不稳定            工程复杂度爆炸
Agent -> Loop:        一次性不可修正        收敛不保证 + 成本线性增长
Agent -> Graph:       线性流程不够表达     状态爆炸 + 调试困难
```

**核心洞察**: 没有完美的范式，只有适合不同抽象层次的范式。五种范式本质上是**五个不同抽象层的控制机制**——Completion 在 token 层，Agent 在任务层，Harness 在安全层，Loop 在反馈层，Graph 在拓扑层。生产系统需要它们的组合。

### 1.4 各范式核心特征对比

| 范式 | 核心结构 | 状态管理 | 交互模式 | LLM调用频率 | 确定性与否 | 代表产品/框架 |
|:-----|:---------|:---------|:---------|:-----------|:-----------|:-------------|
| **Completion** | 单次前向 | 无状态 | 一次性 | 1×/请求 | 确定性生成 | TabNine, Copilot 初版 |
| **Agent** | 多步+工具 | 会话状态 | 任务驱动 | 1-10×/任务 | 概率性主导 | Cursor Agent, Trae, Devin |
| **Harness** | 约束层+内核 | 分层状态 | 防御式 | 1-5×/步骤 | **确定性优先** | OpenClaw, Toolformer, MCP |
| **Loop** | 闭环反馈 | 历史记忆 | 迭代收敛 | 5-50×/任务 | 反馈修正 | ReAct, Reflexion, AutoGPT |
| **Graph** | DAG+节点 | 全局共享 | 声明式流水线 | 10-100+×/任务 | 拓扑确定性 | LangGraph, CrewAI, AutoGen |

---

## 2. Completion 范式（补齐）

### 2.1 定义与原理

Completion 范式是 AI 编程的**原点**——本质是语言模型的自回归语言建模任务（Autoregressive Language Modeling）：给定前缀序列，预测下一个或下一段最可能的 token 序列。

**数学本质**:
$$P(y_{t+1}, ..., y_{t+n} | y_1, ..., y_t) = \prod_{i=1}^{n} P(y_{t+i} | y_1, ..., y_{t+i-1})$$

### 2.2 数学本质：为什么代码适合自回归建模？

Completion 的底层数学是**条件概率估计**：给定前缀 token 序列，模型估计下一个 token 的分布。

$$P(t_{n+1} | t_1, ..., t_n) = \text{softmax}(W \cdot h_n)$$

代码之所以成为自回归建模的天然适配场景，源于两个统计特性：

**① Zipf 分布主导**: 代码 token 的分布比自然语言更极端——高频 token（关键字、常用 API、括号/分号）占比远高于自然语言。Top-10% 的 token 覆盖了约 90% 的代码 token 位置，这意味着模型的预测任务大部分时候是"在少数候选中做选择"。

**② 局部强马尔可夫性**: 代码的局部结构极度规则化——`for(` 后面几乎必然是循环变量初始化，`if(x >` 后面必然是 `)`。比自然语言（"今天天气..." 后面可能有几十种合理延续）的预测确定性高得多。这解释了为什么相对小型模型（GPT-2 级别的 1.5B 参数）就能做出实用的代码补全。

### 2.3 解决的根本问题

> **问题**: 开发者在编写重复性代码（样板代码、已知 API 调用、简单逻辑分支）时，耗费大量时间在"模式化"而非"创造性"工作上。

Completion 解决了**局部上下文中的模式匹配与延续**。核心洞察是：大量代码在统计学上具有高度可预测性（`for` 循环结构、标准库调用、getter/setter），是语言模型的自回归建模的自然适配场景。

### 2.4 FIM (Fill-in-the-Middle)：补全范式的关键突破

Completion 范式中最重要的技术突破不是模型变大，而是**训练范式的改变**——从纯因果 LM 到 **FIM (Fill-in-the-Middle)**。

#### 2.4.1 因果 LM 的问题

标准 GPT 风格的自回归模型只能处理"从左到右"的生成：

```text
[prefix] -> for (int i = 0; i < n; i++) { -> 预测下一行
```

但这与代码补全的真实场景错位：开发者常常是在**已有函数体中间位置**编辑，需要模型理解**前后双向**上下文来预测""位置的内容。

#### 2.4.2 FIM 的训练机制

FIM 通过改造训练数据的格式，让模型学会"中间填充"：

```text
原始代码:  def add(a, b): return a + b

训练样本（FIM 格式 PSM 模式）:
  前缀: def add(a, b):  <- 光标前的内容
  后缀:                  <- 光标后的内容（回传部分）
  Middle: return a + b   <- 要生成的部分

输入到模型的实际 token 序列:
  <FIM_PREFIX> def add(a, b): <FIM_SUFFIX> <FIM_MIDDLE> return a + b
```

**三种 FIM 模式对比**:

| 模式 | 全称 | 结构 | 效果 |
|:-----|:------|:-----|:------|
| **PSM** | Prefix-Suffix-Middle | `<PRE>prefix<SUF>suffix<MID>middle` | 标准模式 |
| **SPM** | Suffix-Prefix-Middle | `<SUF>suffix<PRE>prefix<MID>middle` | 变体，增强 suffix 感知 |
| **S/P 随机** | 随机选择 PSM 或 SPM | 混合 | 防止 overfit 到固定格式 |

**标志性实现**: Codex 最早引入 FIM 训练（OpenAI, 2022），StarCoder（BigCode, 2023）将其开源化。DeepSeek Coder（2024）改进了 FIM 的 suffix 长度采样策略，让多行补全成功率提升 12%。

#### 2.4.3 FIM 的统计本质

FIM 将代码补全从**纯因果预测**（只看历史预测未来）升级为**条件完形填空**（看过往+未来预测中间）：

$$P(middle | prefix, suffix) = \prod_{i=1}^{|middle|} P(t_i | prefix, suffix, t_{<i})$$

**这个看似微小的改变带来了两个根本性的收益**:

1. **跨行感知**: 模型能看到"这段函数最终要返回什么"，生成的中间代码与函数签名和 return 语句自洽
2. **API 签名感知**: 调用方和定义方之间的函数签名一致性大幅提升

### 2.5 三种子模式

### 2.6 技术限制——信息孤岛瓶颈

Completion 范式的所有限制都源于同一个根因：**信息孤岛**。模型只看到当前文件的一段文本，看不到项目的完整上下文。

#### 2.6.1 信息孤岛的三个层次

```text
信息孤岛层次        模型能看到的            模型看不到的
--------------     ------------------       ------------------
语法层              当前文件 ~50行           其他文件、类型定义、接口签名
语义层              文本序列                 编译器信息、类型推断、符号解析
运行层              静态代码                 测试结果、运行时行为、性能特征
```

这三个层次的孤岛各自导致一类典型错误：

| 孤岛层次 | 典型错误 | 示例 |
|:---------|:---------|:------|
| **语法层** | 类型/函数名引用错误 | 调用了不存在的方法，因为模型没看到定义文件 |
| **语义层** | 类型不匹配 | 传入了 string 但函数期望 int（但光看当前行语法没错） |
| **运行层** | 逻辑错误/性能问题 | 写了一个 O(n²) 算法替代了已有的排序好的结构 |

#### 2.6.2 量化影响

| 限制 | 原因 | 量化影响 |
|:-----|:-----|:---------|
| **上下文窗口有限** | GPT-3 只有 2K/4K tokens | 只能参考当前文件 ~30-50 行 |
| **无状态** | 每次补全是独立推理 | 同一方法的多次补全可能不一致 |
| **无外部感知** | 无法读文件系统/运行测试/查 API | 生成代码初次编译通过率 ~30-40% |
| **单次无迭代** | 一次生成即结束 | 逻辑错误无法自我修正 |
| **无工具调用** | 模型只生成文本 | 不能自动执行命令、查询数据库 |

**核心洞察**: Completion 范式的根本瓶颈不是模型精度，而是**信息孤岛**——模型只看到光标前文本，看不到整个项目的类型定义、依赖关系、架构约束和运行反馈。要提高代码质量，需要的不是更强的大模型，而是让模型看到更多上下文。这正是 Agent 范式要解决的核心问题。

### 2.7 里程碑

| 时间 | 事件 | 意义 |
|:-----|:-----|:------|
| 2018 | TabNine 发布，基于 GPT-2 的代码补全 | 首个基于语言模型的商用代码补全工具 |
| 2021.06 | GitHub Copilot 预览版，基于 OpenAI Codex | 将代码补全推向主流开发者 |
| 2022.06 | Copilot 正式发布，$19/月 | 验证了 AI 编程的市场可行性 |
| 2023.03 | GPT-4 发布，HumanEval pass@1 达 67.0% | 模型基础能力质变，为下一范式铺路 |

[来源: GitHub Copilot Blog, OpenAI Codex Paper, 参见 [AI技术演进年度总结](../llm-techniques-principles/2026-06-28-ai-technology-evolution-annual-summary.md)]

---

## 3. Agent 范式（智能体）

### 3.1 定义与原理

Agent 范式是 Completion 的**自然进化**——LLM 不再仅仅是"文本生成器"，而是"决策主体"：它能感知环境（读取文件/执行命令）、使用工具（搜索/数据库/编译器），并基于观测采取行动。

**核心洞察**: 编程的本质不是"生成代码"，而是"做出决策"——Agent 范式第一次让 AI 不仅仅是生成工具，而是决策主体。

**与 Completion 的本质区别**:

```text
Completion:   Prompt -> LLM -> Code (one-shot)
Agent:        Task -> [Think -> Tool -> Observe]^k -> Result (multi-step)
```

[来源: ReAct 论文, arXiv:2210.03629]

### 3.2 解决的根本问题

> **问题**: 开发一个功能涉及多个文件、多种工具、多项决策。Completion 只能"打字"，而开发需要"做事"——读下一个文件、查 API 文档、运行测试、修改 import 路径。

Agent 范式解决了**跨文件、跨工具的多步任务执行**。从"辅助打字"跃迁到"辅助做事"。

### 3.3 产品演化链

```text
Copilot Chat (2023.03)          -- Chat only, no actions
        |
Cursor Composer (2024.02)       -- multi-file edit, full project aware
        |
Claude Code (2025.02)           -- CLI Agent, run cmd + edit files
        |
Cursor Agent (2025.06)          -- IDE deep integration, built-in tools
        |
Trae (ByteDance, 2025.12)       -- CN-optimized IDE + cloud + deploy
        |
Devin 2.0 (2026.03)             -- full-autonomous SWE, SWE-bench 89%
        |
Cursor Cloud Agent (2026.06)    -- cloud Agent, Slack/Mobile support
```

### 3.4 Agent 核心能力组件

| 能力 | 原理 | 代表实现 |
|:-----|:-----|:---------|
| **工具调用** | 模型输出结构化工具调用指令 (Function Calling) | OpenAI tool_calls, Anthropic tool_use |
| **文件编辑** | LLM 生成 diff/edits，IDE 应用 | Cursor Composer, Claude Code patch |
| **命令执行** | 模型生成 shell 命令，沙箱执行 | Claude Code, Cursor Cloud |
| **多文件感知** | 自动扫描项目结构，选择性加载上下文 | Cursor @file, 自动索引 |
| **任务分解** | 模型将高层需求拆解为子任务 | Devin planner, Claude Code plan |
| **错误自愈** | 执行错误 → 读取错误输出 → 修正 | Terminal → read errors → re-edit |

### 3.5 Agent 的内部架构

从系统架构角度看，不同 Agent 产品的内部设计差异巨大。最关键的区分维度不是"能力"，而是**环境嵌入方式**。

#### 3.5.1 IDE Agent vs CLI Agent：根本架构差异

| 维度 | IDE Agent (Cursor) | CLI Agent (Claude Code) |
|:-----|:-------------------|:------------------------|
| **代码感知** | 通过 LSP/AST 获取结构化代码 | 纯文本读取 |
| **上下文选择** | 语义索引 + 符号解析定位相关代码 | 模糊搜索 + 文件正则匹配 |
| **编辑方式** | AST 感知的精确替换 | 文本 patch (diff) |
| **执行反馈** | 内嵌终端 + Linter + Type checker 实时反馈 | 子进程执行命令 |
| **多文件操作** | Tree-sitter 解析整个项目 | 逐文件读取+编辑 |
| **对模型依赖** | 中（IDE 分担了结构理解） | 高（模型自行理解文件结构） |

**核心洞察**: IDE Agent 本质上是一个"结构化引擎 + LLM"的混合体——LLM 负责生成代码决策，IDE 负责理解代码结构。CLI Agent 则把所有责任压在模型上，因此对模型能力要求更高。这解释了为什么 Cursor 在 GPT-4 时代就能工作，而 Claude Code 直到 Opus 4 才达到实用水平。

#### 3.5.2 Agent 的认知架构：System 1 / System 2

优秀的 Agent 实际上有两个协同工作的认知系统：

```text
System 1 (快系统) — 模式匹配
   触发: 已知任务模式 (e.g., "排序"、"读文件"、"运行测试")
   动作: 直接执行，无需规划
   成本: 低，1-2 次 LLM 调用
   典型场景: 80% 的日常开发任务

System 2 (慢系统) — 规划推理
   触发: 复杂/模糊任务 (e.g., "重构这个模块"、"设计 API")
   动作: 先规划->拆解->逐步执行
   成本: 高，5-20+ 次 LLM 调用
   典型场景: 20% 的复杂任务
```

**关键设计**: 好的 Agent 不是每次都做完整规划——它应该**默认快系统响应，只在必要时启动慢系统**。这就像人的大脑在走路时不思考每一步（System 1），只有遇到岔路才停下来想（System 2）。

### 3.6 上下文管理：Agent 最被低估的工程挑战

Agent 从 Completion 继承的最大遗留问题是**上下文有限**。但 Agent 多了一个关键能力：**可以选择看什么**。

#### 3.6.1 上下文的拼接策略

| 策略 | 原理 | 成功截断 | 代表产品 |
|:-----|:------|:---------|:---------|
| **全部加载** | 项目全量 → 让模型自己选择关注点 | ❌ 超出上下文窗口 | 早期尝试（失败） |
| **最近文件** | 最近编辑的文件自动加载 | 低 | 最朴素实现 |
| **符号索引** | Tree-sitter/AST 提取函数/类签名 → 按需加载 | 中 | Cursor, Codeium |
| **语义检索** | 向量索引 + 语义搜索相关代码 | 中高 | Cursor Cloud, Sourcegraph Cody |
| **调用图感知** | AST 静态分析导出的函数调用链 | 高 | GitNexus, Cursor Cloud |
| **隐式上下文** | Agent 自动分析 import 链 + 类型引用 | 高 | Cursor Composer |

**关键洞察**: 上下文管理不再是简单的"窗口扩展"问题，而是**代码相关性检索**问题——在有限窗口内放入最相关的代码。这本质上是信息检索（IR）问题，与搜索引擎面临的挑战同构。

### 3.7 技术限制

| 限制 | 原因 | 量化影响 |
|:-----|:-----|:---------|
| **概率性执行** | LLM 本身是非确定性的 | 同一任务两次执行可能完全不同的路径 |
| **长时间崩溃** | Context Window 有限 + LLM 长时间漂移 | 复杂任务失败率 ~30-40% |
| **工具调用不可靠** | API 调用格式错误/参数错误 | Tool call 成功率 ~85-92% |
| **无持久化状态** | Agent 完成任务后状态不持久化 | 中断后无法恢复 |
| **上下文选择偏差** | 选择的代码可能不是最优上下文 | 上下文相关性问题 → 约 15-25% 的生成错误 |
| **无多人协作** | 无共享上下文 | 不适合团队使用 |
| **无审计追溯** | 决策过程不可审计 | 企业合规不满足 |

### 3.8 标志性数据

| 指标 | 值 | 来源 |
|:-----|:---|:-----|
| SWE-bench (真实 GitHub Issue解决率) | Devin 2.0 **89%**, Claude Opus 4.7 **87.6%** | SWE-bench 排行榜, 2026 |
| HumanEval pass@1 | GPT-4 67% → **Agent Loop GPT-3.5 95.1%** | Andrew Ng, Agentic Design Patterns, 2024 |
| 开发者效率提升 | 新手 ×2, 熟手 +55% | GitHub Copilot 用户调查, 2025 |

[来源: SWE-bench Leaderboard, Agentic Design Patterns (DeepLearning.AI), Stack Overflow 2025 Survey, 参见 [Agent OS 五种范式](../agent-engineering/2026-06-26-agent-os-five-paradigms.md)]

---

## 4. Harness 范式（约束框架）

### 4.1 定义与原理

> **Harness Engineering 的诞生源于一个残酷的现实：模型能力不再是瓶颈 → 执行环境才是。**

Harness 范式是**对 Agent 范式的工程化治理**——它不是在 LLM 内部做文章（微调/Prompt），而是在 LLM **外部**构建完整的执行环境约束体系。

**核心架构**:

```text
+------------------------------------------+
|               Harness                     |
|  +----------+ +----------+ +----------+ |
|  |constraint | | router    | | governance| |
|  |(Schema)  | | (INV-R)  | | (audit)  | |
|  +----+-----+ +----+-----+ +----+-----+ |
|       |            |            |        |
|  +----v------------v------------v-----+ |
|  |       LLM Core (probabilistic)       | |
|  +------------------------------------+ |
+------------------------------------------+
```

### 4.2 解决的根本问题

> **问题**: 裸 Agent 太"脆弱"——LLM 输出不稳定、工具调用不可靠、行为不可审计、状态不可恢复。企业级使用需要"工业级防护"。

Harness 范式解决的是**概率性执行主体的可靠性问题**。从"让 AI 做事"升级到"让 AI 正确地、可追溯地、可控地做事"。

### 4.3 三层约束模型（Defense in Depth）

| 约束层 | 可靠性 | 示例 | 可绕过性 |
|:-------|:-------|:-----|:---------|
| **Prompt 约束** | 低 (~60%) | "不要删除文件" | LLM 可忽略 |
| **Schema 约束** | 中 (~85%) | JSON Schema 验证输出格式 | LLM 需遵守格式 |
| **环境约束** | 高 (~99%) | 文件系统只读沙箱 | 无法绕过 |
| **验证约束** | 高 (~99%) | E2E 测试验证结果 | 无法绕过 |
| **人工确认** | 极高 (~100%) | 支付/删除前人工审批 | 绕不过（设计） |

**核心原则**: 能用 Schema 约束的，不用 Prompt。能用环境约束的，不用 Schema。

[来源: Agent OS：五种驯服不确定性的范式, knowledge/03_AI/agent-engineering/]

### 4.4 确定性优先路由（INV-R）

**路径排序**: Rule → API → CLI → MCP → GUI → Free-form LLM

| 路由方式 | 确定性 | 成功率 | 适用场景 |
|:---------|:-------|:-------|:---------|
| **Rule** (规则引擎) | 100% | ~100% | 文件操作白名单、命令黑名单 |
| **API** (专用 API) | ~100% | 99.9% | git status、创建分支、CI 触发 |
| **CLI** (命令行) | 高 | ~99% | 编译、测试、格式化 |
| **MCP** (Model Context Protocol) | 中 | ~95% | 数据库查询、Web 请求 |
| **GUI** (图形界面) | 低 | ~70% | 浏览器操作 |
| **Free-form LLM** (自由文本) | 最低 | ~60% | 开放式推理 |

**实验数据** (PhoneHarness): CLI 成功率 ~99%，MCP ~95%，GUI ~70%——路由策略收益 > 模型能力提升收益。

[来源: Agent OS 五种范式, Agent AI 研究报告]

### 4.5 Toolformer → MCP → A2A 协议演化

```text
Toolformer (2023.02)          -- self-supervised API learning
    v
OpenAI Function Calling      -- structured tool call (2023.06)
    v
OpenAI GPTs Actions          -- visual tool config (2023.11)
    v
MCP (Model Context Protocol) -- general tool protocol (2024.11)
    v
A2A (Agent-to-Agent)         -- cross-Agent protocol (2025.04)
```

| 协议 | 发布方 | 核心贡献 | 局限性 |
|:-----|:-------|:---------|:-------|
| **Toolformer** [arXiv:2302.04761] | Meta | 首次展示LLM可自监督学习使用工具 | 需要微调，非通用 |
| **Function Calling** | OpenAI | 在API层标准化tool_use格式（JSON schema） | 绑定OpenAI生态 |
| **MCP** | Anthropic | 开源工具协议，任意客户端↔任意服务端 | 1:1 通信，不支持多Agent |
| **A2A** | Google | 跨Agent发现与协作，支持能力发布 | 定义粒度较粗，生态未成熟 |

### 4.6 代表实现

| 框架/产品 | 核心特征 | 约束机制 | 适用规模 |
|:----------|:---------|:---------|:---------|
| **OpenClaw** | 企业级 Agent 治理 | 权限 + 审计 + 追溯 + 监控 | 企业团队 |
| **Semantic Kernel** | Microsoft 轻量 Harness | 函数内核 (Plugin) + 拦截器 | 单体应用 |
| **LangChain** | 可组合的链式 Harness | Callback 系统 + 运行时验证 | 中小项目 |
| **OpenAI Assistants API** | 托管 Harness | 内置沙箱 + Code Interpreter | 独立应用 |
| **Vercel AI SDK** | 前端 Harness | 流式渲染 + 工具链绑定 | Web 应用 |

### 4.7 深度框架：Agent OS 五种驯服不确定性的范式

Harness 工程化的最高阶抽象是 **Agent OS**——将 Agent 的执行环境视为一个操作系统，用 70 年计算机科学积累的经典范式来治理 LLM 的固有不确定性。

#### 4.7.1 不确定性的六个来源

| # | 来源 | 性质 | 可消除？ |
|:--|:-----|:-----|:--------|
| ① | **LLM 输出概率性** | 认知不确定性 | 部分（约束/微调） |
| ② | Tool 调用可能失败 | 偶然不确定性 | 部分（重试/冗余） |
| ③ | 环境状态变化 | 外部扰动 | 不可消除 |
| ④ | **Context Window 有限** | 观测约束 | 不可消除（物理极限） |
| ⑤ | 多 Agent 并发 | 竞争条件 | 可管理（协议） |
| ⑥ | **模型升级行为漂移（假设腐化）** | 平台演变 | 不可消除 |

**关键洞察**: 6 个来源中 3 个（①④⑥）在传统软件系统中罕见——传统系统不会因为"换了 CPU 型号"而改变程序行为（⑥），不会突然"记不住 2 分钟前的输入"（④），不会"同样的入参给出不一样的返回值"（①）。这意味着 Harness 面临的是**传统可靠性工程未覆盖的问题**。

#### 4.7.2 五种范式映射

从 10 个领域（通信/分布式系统/数据库/控制论/实时系统/容错计算/网络协议/编译器/蒙特卡洛/量子纠错）中提炼出 5 种可复用范式：

| 范式 | 原理 | Agent OS 应用 | 消除的不确定性 |
|:-----|:------|:-------------|:--------------|
| **冗余 + 投票** | 多副本/采样对冲个体失败 | Best-of-N 投票, 多 Agent Review | ① LLM 概率性 |
| **闭环反馈** | 观测输出 → 修正输入 | 测试→修复→重测循环 | ①+③ 输出+环境 |
| **约束空间** | 限制动作空间，排除非法操作 | Schema 验证, 沙箱 | ① LLM 错误输出 |
| **隔离** | 故障不扩散，影响范围控制 | 独立沙箱, 进程隔离 | ③+⑤ 并发+级联 |
| **分解** | 复杂→简单，降低单点复杂度 | 任务分解, Plan→Execute 分离 | ④ Context 有限 |

#### 4.7.3 分布式系统的可直接复用与必须重造

**可直接复用（8 项）**:

| 分布式中已解决 | Agent OS 映射 | 作用 |
|:--------------|:-------------|:-----|
| Event Sourcing | Session = append-only fact log | 状态可追溯 |
| Idempotency Key | Tool call dedup | 幂等性 |
| Trace ID | Agent trace_id 贯穿 | 可审计 |
| Circuit Breaker | Tool 连续失败→切策略 | 弹性 |
| Sidecar | Agent 的独立监控代理 | 解耦 |
| Control/Data Plane 分离 | Brain（决策）/Hands（执行） | 分离关注点 |
| Graceful Degradation | Context 不足时降级 | 优雅降级 |
| 2PC (两阶段提交) | Grant 确认机制 | 跨 Agent 原子性 |

**必须重新发明（4 项）**— 这些是传统分布式系统做不到、Agent OS 必须自己解决的：

| 传统解法 | 为什么不能直接用 | Agent OS 替代 |
|:---------|:---------------|:-------------|
| **确定性 Replay** | Agent 输出概率性，相同输入未必相同输出 | Fact Log + 投影（状态快照） |
| **自动 Gossip** | Agent Context Window 是单向的，不能被动接收 | 主动 Retrieval（按需拉取） |
| **固定超时重试** | 语义错误不因重试消失（不是网络丢包，是理解错了） | 反馈 + 换策略（不改方案的重试是浪费 Token） |
| **静态配置** | 模型升级导致行为漂移（假设腐化） | Feature Gate + Adaptive 策略 |

> **"4 项必须重造"深刻揭示了 Agent 工程与传统工程的根本差异**——传统工程的失败模式是"执行错误"（可重试可恢复），而 Agent 的失败模式是"理解错误/决策错误/前提过时"（重试无效）。

### 4.8 技术限制

| 限制 | 原因 | 严重程度 |
|:-----|:-----|:---------|
| **Harness 复杂性** | 约束层越多，维护成本指数增长 | 高 ⚠️ |
| **假设腐化** | 模型升级导致 Harness 假设失效——模型变聪明了，但你之前写的约束条件可能被绕过了 | 极高 🚨 |
| **过度约束** | 安全层叠过多时，Agent 失去弹性调度能力 | 中 |
| **确定性路径 ROI 递减** | 第1条路径 ROI 极高，第100条 ROI 趋近于 0 | 中 |
| **诊断困难** | LLM 不遵守约束时，是 Prompt 不够强、Schema 有漏洞，还是模型绕过了？归因模糊 | 高 ⚠️ |

---

## 5. Loop 范式（循环）

### 5.1 定义与原理

Loop 范式的本质是**将单次推理扩展为有反馈的迭代过程**。在编程场景中，这意味着：生成代码 → 运行测试 → 查看错误 → 修正代码 → 重新测试 → ... 直到通过。

**与 Completion 的本质区别**:

```text
Completion:  Prompt -> Code (single, no feedback)
Agent:       Prompt -> [Action]^k -> Result (multi-step, no loop)
Loop:        Prompt -> [Act -> Observe -> Reflect -> Revise]^k -> Result (iterative)
```

### 5.2 解决的根本问题

> **问题**: Agent 可以执行多步任务，但如果某一步出错了，它不会自动修正——"语义错误不因重试而消失"。

Loop 范式解决了**自我修正和迭代收敛**。从"一次性执行"升级到"迭代式逼近正确解"。

### 5.3 Loop 谱系：从简单到复杂

```text
Simple                                    Complex
  |                                           |
  v                                           v
ReAct -> Plan&Solve -> Reflection -> Reflexion -> LATS
(Think-Act)  (Plan-Act)  (Self-Critique) (Memory)  (Tree Search)
```

### 5.4 五种 Loop 子模式详解

#### 5.4.1 ReAct (Reason + Act) — 基础循环

**提出**: Yao et al., ICLR 2023 [arXiv:2210.03629]

**结构**:

```text
Thought:  "fetch user list API"
Action:   [GET /api/users]
Observation: 200 OK, [{id:1, name:"Alice"}, ...]
Thought:  "data received, rendering table..."
Action:   [write users_table.html]
```

**解决的问题**: 将"推理"和"行动"分离，让 LLM 清楚表达每一步的决策理由。

**限制**:

- 无反思机制：错误决策不会自动修正
- 无记忆：每轮从零开始推理
- 线性路径：不能回溯探索其他分支

#### 5.4.2 Plan & Solve — 先规划后执行

**结构**: Plan(分解)→Solve(子步执行)→[验证→修正]→输出

**解决的问题**: 将"任务分解"从隐性（ReAct 隐含）变为显式，减少长任务中的"忘记早期目标"。

**典型编程应用**: "写一个数据处理管道"→ 模型先输出 `[plan: 1.读CSV 2.清洗缺失值 3.标准化 4.聚合统计 5.输出报告]` → 逐步执行。

#### 5.4.3 Reflection — 自我审校

**结构**: Generate → [Self-Critique → Revise]ᵏ

**解决的问题**: 单次生成的质量有限。让模型审视自己的输出可以大幅提升质量。

**编程场景**: 生成代码 → 模型自查 "这段代码未处理空指针" → 修正。

**数据**: Andrew Ng 报告，Reflection 可使 GPT-4 的 HumanEval 准确率从 67% 提升至 80%+。

#### 5.4.4 Reflexion — 引入记忆的反射学习

**提出**: Shinn et al., NeurIPS 2023 [arXiv:2303.11366]

**核心创新**: Agent 不仅仅观察错误，还将错误经验**以自然语言存储到记忆中**，供未来类似场景重用。

**结构**:

```text
[trial1] implement sort -> test fail (OOM)
         | reflect
         "for large datasets, use external sort or chunking"
[trial2] reflect from memory
         -> correct
```

**标志性数据**: Reflexion 在 HumanEval 上实现 **91% pass@1**，超越当时 GPT-4 的 80%。

**解决的问题**: 不仅要修正当前错误，还要**积累经验**来避免未来同类错误。

#### 5.4.5 LATS (Language Agent Tree Search) — 树搜索

**结构**: 将 ReAct 每一步扩展为树搜索：多路径探索 → 启发式评分 → 最优路径回溯。

**解决的问题**: 分支不确定性——当 Agent 面临多个可能路径时，单一决策可能错过更好的方案。

```text
         [Task]
        /      \
  pathA         pathB
  /    \        /    \
A1(ok) A2(better) B1(fail) B2(ok)
```

**限制**: 计算成本高（每步需扩展多个分支），Token 消耗大。

### 5.5 性能对比（HumanEval）

| 方法 | pass@1 | 相对于 GPT-4 基线 | 额外 Token 消耗 |
|:-----|:-------|:-----------------|:---------------|
| GPT-4 zero-shot | 67.0% | — | 基线 |
| GPT-4 + CoT | ~75% | +8pp | ~1.5× |
| GPT-4 + Reflection | ~80% | +13pp | ~2× |
| GPT-3.5 + Agent Loop | 95.1% | +28.1pp | ~5-10× |
| Reflexion (GPT-4) | 91% | +24pp | ~3-5× |

[来源: Andrew Ng Agentic Design Patterns, Reflexion Paper]

### 5.6 编程中的典型 Loop 应用

```python
# pseudo: Coding Loop core logic
while not tests_passed and attempts < max_attempts:
    # 1. generate/fix code
    code = llm.generate(prompt + error_feedback)
    # 2. run tests
    test_output = run_tests(code)
    # 3. check result
    if test_output.passed:
        break
    else:
        # 4. collect error for feedback
        error_feedback = test_output.errors
        attempts += 1
```

**实际产品中的 Loop**:

- **Cursor /loop skill** (2026): 周期执行直到测试通过
- **Claude Code** 的自动运行循环: edit → run → see error → re-edit
- **Devin** 的沙箱循环: code → build → test → fix → retest

### 5.7 ReAct 的软肋：为什么需要 Dynamic Workflow

ReAct 模式看似优雅，但有一个根本问题：**流程全靠模型临场维持**。阶段顺序、工具选择、错误恢复策略——全部由 LLM 在每次调用时重新推理决定。

这种"开放探索"模式带来了三个工程痛点：

| 痛点 | 表现 | 根因 |
|:-----|:------|:------|
| **执行结构不一致** | 同一任务跑10次，10次路径不同 | 模型每次的决策路径不同 |
| **成本不可控** | 简单任务有时跑出巨量 Token 消耗 | 模型在无关路径上过度探索 |
| **复盘困难** | 执行路径在上下文里漂移，难以定位"哪一步偏了" | 无固定的结构化日志 |

**核心观点**: 真正重要的不是某条神奇 Prompt，而是让 Loop 自己跑起来、稳定交付的运行时。
> — Boris Cherny: "I don't prompt Claude anymore. I have loops running that prompt Claude."

### 5.8 Dynamic Workflow：把 Loop 从提示词搬进代码

**核心思想**: 先用强模型把任务拆成一段 **Workflow Script**（脚本里写清楚阶段、并行、循环、分支、验收条件），然后让代码控制流程，模型只在被显式调用的位置出现。

```python
# Dynamic Workflow 的核心抽象
def workflow(task):
    # 阶段1: 扫描（代码控制流程）
    context = phase_scan(task)
    # 阶段2: 规划（模型出方案，代码执行）
    plan = agent("拆解任务: {context}")
    # 阶段3: 并行执行（Promise.all 由代码控制）
    results = Promise.all([
        agent("实现 A 部分", plan.a),
        agent("实现 B 部分", plan.b),
    ])
    # 阶段4: 审查循环（for 循环控制迭代次数）
    for i in range(3):  # 最多3轮
        code = agent(f"基于反馈修正: {results}")
        passed = verify(code)
        if passed: break
    return code
```

**收益**: 强模型只需要在"生成脚本"时出场一次，后续执行可以用更便宜的模型。确定的骨架归代码，不确定的判断归模型。

#### Skill vs Workflow 对比

| 维度 | Skill (自然语言说明) | Dynamic Workflow (代码控制) |
|:-----|:--------------------|:--------------------------|
| 执行路径 | 每次可能不同，模型临场决定 | 阶段/分支/循环显式固定 |
| 对模型要求 | 高，需要持续遵守自然语言说明 | 低，模型只处理被调用的子任务 |
| 复盘方式 | 难以还原完整路径 | 日志、状态和阶段都可追踪 |
| 适合任务 | 探索性强、边界模糊、临时性 | 阶段清楚、有验收标准、反复执行 |
| 成本结构 | 依赖强模型全程维持 | 强模型生成一次，普通模型执行多次 |

### 5.9 收敛问题：Loop 会不会永远不结束？

Loop 范式的核心工程挑战是**终止保证**——LLM 的概率性输出决定了循环不一定会收敛到正确答案。

#### 5.9.1 Loop 的三种终止条件

| 终止条件 | 信号 | 可靠性 | 代价 |
|:---------|:-----|:-------|:----|
| **通过测试**（Test Pass） | 测试全部通过 | 高（如果有好测试） | 运行测试本身有成本 |
| **达到最大轮次**（Halt） | `attempts >= max_attempts` | 100% | 可能未完成就放弃 |
| **模型自判断**"已完成" | LLM 输出完成信号 | 低（LLM 常误判） | 最便宜 |

**实际产品中的策略组合**：

```text
while (attempts < max_attempts && !passed):
    fix(model, test_feedback)
    passed = run_tests()
    if passed: break
    # 连续 3 次无改进 -> 提前终止
    if no_progress(attempts, attempts-1, attempts-2): break
```

#### 5.9.2 何时收敛，何时发散？

| 场景 | 收敛趋势 | 原因 |
|:------|:---------|:------|
| **编译错误** | ✅ 通常在 1-3 轮内收敛 | 错误信息明确，修复路径确定 |
| **运行时异常** | ✅ 通常在 1-5 轮内收敛 | 调用栈+错误消息可操作 |
| **逻辑错误** | ⚠️ 不保证收敛 | 没有明确"错误信号"，LLM 可能反复在错误方案间跳跃 |
| **需求模糊** | ❌ 大概率发散 | LLM 会生成功能不对但语法正确的代码 |
| **多文件冲突** | ❌ 发散 | 改了一个文件导致另一个文件不兼容，来回震荡 |

**关键洞察**: Loop 的质量取决于**反馈信号的质量**。编译器错误 > 运行时错误 > 测试断言失败 > 模型自检。反馈越明确，收敛越快。

### 5.10 技术限制

| 限制 | 原因 | 影响 |
|:-----|:-----|:-----|
| **收敛保证问题** | LLM 概率性输出，循环可能不收敛 | 需要设置最大迭代次数（halt）+ 退化检测 |
| **错误反馈质量** | 编译器错误→可操作；语义错误→难诊断 | 对运行时错误恢复好，对逻辑错误恢复弱 |
| **记忆遗忘** | Loop 过长时，早期目标和决策被稀释 | Context Window 约束 |
| **成本线性增长** | 每步都消耗 tokens | 复杂任务成本 $5-50/次 |
| **不可重入** | Loop 过程中断后无法恢复 | 不支持暂停/恢复，长时间任务需要云端保持 |
| **退化循环** | 模型在同样错误方案间反复跳跃 | 需要无进展检测（no_progress breaker）|
| **ReAct 软肋** | 流程全靠模型临场维持，结构不稳定 | Dynamic Workflow 缓解但未根除 |

---

## 6. Graph 范式（图谱）

### 6.1 定义与原理

Graph 范式是目前**最复杂的 AI 编程范式**——它将整个编程工作流建模为**有向无环图 (DAG)**，其中：

- **节点 (Node)** = 独立处理步骤（代码生成、测试执行、代码审查、部署）
- **边 (Edge)** = 数据/控制流依赖
- **状态 (State)** = 全局共享的上下文对象

**核心洞察**: 编程不是线性过程，而是一个**多分支、多依赖、多反馈的复杂网络**。Loop 范式可以处理线性迭代，但无法处理"同时审查 + 测试"或"A 完成后并行 B 和 C"等分支场景。

**与 Loop 的本质区别**:

```text
Loop:  [A -> B -> C -> A]  -- single loop
Graph:
       +-> B1 ->+
  A -> |      |-> D  -- branched + merged
       +-> B2 ->+
```

### 6.2 解决的根本问题

> **问题**: 复杂软件开发不是线性流水线——多 Agent 需要协作、代码生成和测试可以并行、审查和部署需要按依赖顺序执行。Loop 和 Harness 无法表达这种拓扑结构。

Graph 范式解决了**复杂工作流的拓扑编排和状态共享**。从"单线循环"升级到"多分支有向图"。

### 6.3 核心理论渊源

| 理论来源 | 影响 | 映射到 Agent Graph |
|:---------|:-----|:-------------------|
| **Pregel** (Google, 2010) | 大规模图计算框架，BSP 模型 | LangGraph 的状态同步机制 |
| **Apache Beam** (Google, 2015) | 数据流水线 DAG 编排 | Agent 工作流的有向图调度 |
| **DAG Scheduling** (分布式系统) | 依赖关系拓扑排序 | Agent 节点执行顺序确定 |
| **Actor Model** (Erlang) | 独立 Actor + 消息传递 | 多 Agent 通信模式 |
| **GNN (GCN/GAT)** | 图神经网络消息传递 | Agent 通信拓扑优化 |

[来源: LangGraph 官方文档, AgentVerse 论文 arXiv:2308.10848]

### 6.4 三种 Graph 子模式

#### 6.4.1 StateGraph (有状态图) — LangGraph 模式

**结构**: 单图 + 全局共享状态 + 节点/边定义

```python
# LangGraph core abstraction
graph = StateGraph(AgentState)
graph.add_node("code_gen", generate_code)
graph.add_node("test_run", run_tests)
graph.add_edge("code_gen", "test_run")
# conditional: pass->end, fail->revise
graph.add_conditional_edges("test_run",
    lambda s: "end" if s.tests_passed else "revise")
```

**解决的问题**: 多步骤工作流需要共享状态、条件分支和循环回路。

**代表**: LangGraph, AutoGen

#### 6.4.2 MultiAgent Graph (多Agent图) — 通信拓扑

**结构**: 每个 Agent 是一个独立节点，通过消息通道通信

```python
# CrewAI Agent team
coder = Agent(role="Developer", ...)
tester = Agent(role="QA Engineer", ...)
reviewer = Agent(role="Code Reviewer", ...)
crew = Crew(agents=[coder, tester, reviewer],
            process=Process.hierarchical)
```

**解决的问题**: 不同角色需要不同上下文和工具集，且需要相互通信、审查、接力。

**代表**: CrewAI, AgentVerse, ChatDev, MetaGPT

#### 6.4.3 Adaptive Graph (自适应图)

**结构**: 图的拓扑结构**在运行时动态调整**——添加/删除节点、修剪边

```python
# adaptive graph pruning
AGP(AgentGraph).prune(
    strategy="task_adaptive",
    remove_unnecessary_agents=True
)
```

**解决的问题**: 固定拓扑的 Graph 对某些任务过度消耗（不需要所有的 Agent 参与）。

**代表**: AGP (Adaptive Graph Pruning), FlowReasoner

[来源: FlowReasoner (Gao et al., 2025a)]

### 6.5 代表框架对比

| 框架 | 图类型 | 状态管理 | 通信模式 | 适用场景 | 复杂度 |
|:-----|:-------|:---------|:---------|:---------|:-------|
| **LangGraph** | StateGraph (单图) | 全局共享 State | 节点间隐式依赖 | 复杂工作流编排 | ⭐⭐⭐⭐ |
| **CrewAI** | MultiAgent Graph | 独立 Agent 状态 | 显式消息 + 委派 | 角色分工协作 | ⭐⭐⭐ |
| **AutoGen (Microsoft)** | 对话图 | Agent 会话状态 | 事件驱动 | 多 Agent 讨论 | ⭐⭐⭐⭐ |
| **AgentVerse** | 动态团队图 | 角色+任务队列 | 广播/点对点 | 团队动态调整 | ⭐⭐⭐⭐⭐ |
| **MetaGPT** | 角色协作图 | 文档驱动的共享状态 | SOP 流程 | 软件开发模拟 | ⭐⭐⭐ |
| **Semantic Kernel** | 进程图 | 函数内核 | 链式调用 | 企业集成 | ⭐⭐ |

### 6.6 编程场景中的 Graph 应用

**完整 CI/CD + AI 编程流水线** (DAG 示例):

```text
              +-----------------+
              |  requirements   |
              +--------+--------+
                       |
              +--------v--------+
              |  architecture   |
              +--------+--------+
                       |
           +-----------+-----------+
           |           |           |
     +-----v-----+ +--v--+ +-----v-----+
     | frontend  | | back| | test case |
     | Agent     | |Agent| | Agent     |
     +-----+-----+ +--+--+ +-----+-----+
           |           |           |
           +-----------+-----------+
                       |
              +--------v--------+
              |  code review    |
              +--------+--------+
                       |
              +--------v--------+
              |  deploy Agent   |
              +-----------------+
```

**实际产品示例**:

- **Cursor Cloud Agent**: 多 repo 附着 + hooks (beforeSubmitPrompt, afterAgentResponse)
- **Devin 2.0**: Planner + Coder + Tester + Debugger 多 Agent 协作
- **OpenClaw**: 多 Agent 治理 + 权限控制 + 审计追溯

### 6.7 Pregel/BSP 模型：LangGraph 的底层理论

LangGraph 的核心不是"在 LangChain 上加了个图"，而是**从 Pregel 借用了 Bulk Synchronous Parallel (BSP) 模型**。

#### 6.7.1 BSP 模型的三阶段

```text
超步 (Superstep) 1:
  [Node A] -> 计算 -> 发送消息到 Node B、C
  [Node D] -> 计算 -> 发送消息到 Node A

    v 所有节点完成后，同步屏障 (Barrier Sync)

超步 (Superstep) 2:
  [Node B] -> 收到消息 -> 计算 -> 发送消息到 Node C
  [Node C] -> 收到消息 -> 计算 -> 发送消息到 Node D
```

**LangGraph 对 BSP 的适配**：

| 传统 BSP | LangGraph 映射 |
|:---------|:--------------|
| 超步 (Superstep) | add_node() 的每次执行 |
| 消息传递 | State 更新（节点写入 State） |
| 同步屏障 | 条件边 (conditional_edges) 的判定 |
| 计算节点 | LLM 调用或代码函数 |

**关键意义**: BSP 模型将 Graph 的执行从"流式事件"（难以调试）变成了"步骤化的批处理"（可调试、可 checkpoint、可重放）。这正是 Graph 范式相对于裸 Agent 的核心优势之一。

### 6.8 多 Agent 通信拓扑：三种基本模式

| 模式 | 结构 | 耦合度 | 适用场景 | 代表 |
|:-----|:------|:-------|:---------|:-----|
| **Network（网络）** | 任意 Agent ↔ 任意 Agent | 高 | 开放讨论/头脑风暴 | AutoGen, AgentVerse |
| **Supervisor（主管）** | 中心 Agent 协调所有子 Agent | 中 | 任务分配 + 进度监控 | CrewAI, OpenClaw |
| **Hierarchical（层级）** | 多层 Supervisor 树 | 低 | 大规模团队 | MetaGPT, Devin 2.0 |

```text
Network 模式:          Supervisor 模式:        Hierarchical 模式:
  A <--> B                 Supervisor                CTO
  ↕   ↕                    ↙ v ↘                ↙      ↘
  C <--> D               A   B   C             PM1        PM2
                                              ↙ v ↘      ↙ v ↘
                                            D  E  F    G  H  I
```

**Network 模式的问题**: 通信复杂度 O(n²)——n 个 Agent 相互通信，消息总量随 n 平方增长。4 个 Agent 已经需要 12 条通信路径。这是为什么多数生产系统选择 Supervisor 或 Hierarchical 模式。

### 6.9 状态爆炸：Graph 最大的隐性成本

Graph 范式中最被低估的问题是**共享状态的隐性膨胀**。

#### 6.9.1 状态增长模型

```text
State(t) = State(t-1) + Node1_output + Node2_output + ...

每经过一个节点，State 就增加该节点的输出。
经过 n 个节点后：|State| = Σ|Node_i_output|
```

| 图规模 | 节点数 | 总 State 大小（估计） | 可管理？ |
|:-------|:------|:--------------------|:---------|
| 小型 | 3-5 个节点 | ~5-10K tokens | ✅ |
| 中型 | 10-20 个节点 | ~50-200K tokens | ⚠️ 接近上下文窗口边缘 |
| 大型 | 50+ 个节点 | ~500K-2M tokens | ❌ 超出窗口，需要 State 压缩 |

#### 6.9.2 解决策略

| 策略 | 原理 | 副作用 |
|:-----|:------|:-------|
| **State 裁剪** (Prune) | 定期丢弃不再需要的旧 State | 丢失历史信息，不可回溯 |
| **State 摘要** (Summarize) | LLM 压缩旧 State 为摘要 | 压缩精度损失 |
| **分层 State** | 不同节点只能看到 State 的子集 | 需要显式定义可见性 |
| **增量 State** | 只存储增量变化（类似 Git） | 重构开销大 |
| **Checkpoint → Reset** | 快照保存后重建 State | 实现复杂 |

### 6.10 技术限制

| 限制 | 原因 | 严重程度 |
|:-----|:-----|:---------|
| **状态爆炸** | 全局共享状态随图复杂度线性增长，无压缩时可达 O(n) 每步膨胀 | 高 🚨 |
| **调试困难** | DAG 执行路径不直观，需要 LangSmith 级分布式追踪工具 | 高 ⚠️ |
| **通信开销** | Network 模式 O(n²)，Supervisor 模式 O(n)，多 Agent 消息传递消耗大量 tokens | 中 |
| **拓扑设计** | 需要工程师明确编排节点和边，不像 ReAct 可以"自然涌现" | 高 ⚠️ |
| **不确定性级联** | 一个节点的概率性输出 → 下游节点不稳定 → 级联放大 | 高 🚨 |
| **过杀问题** | 固定 Graph 包含不需要的 Agent 节点，浪费 tokens | 中（Adaptive Graph 可缓解） |

---

## 7. 范式跃迁的力学分析

> **核心问题**: 为什么不是 Completion → Graph 一步到位？每个跃迁的驱动力和阻力是什么？

### 7.1 跃迁驱动力分析

每个范式跃迁都由三个力共同驱动：

| 跃迁 | 拉动力（需求端） | 推动力（供给端） | 使能力（基础设施） |
|:-----|:----------------|:----------------|:------------------|
| Completion → Agent | 复杂任务需要多步执行 | 模型推理能力++ (GPT-4) | Function Calling API |
| Agent → Harness | 概率性输出无法用于生产 | 工程经验积累（分布式/容错） | Schema 约束 + 沙箱 |
| Agent → Loop | 单次生成无法自我修正 | 模型上下文窗口++ (128K→2M) | 测试框架集成 |
| Agent → Graph | 线性流程无法表达并行 | 多 Agent 协作需求 | LangGraph/CrewAI 框架 |

### 7.2 跃迁阻力分析

每个跃迁也面临独特阻力：

| 跃迁 | 主要阻力 | 克服条件 | 过渡期产品 |
|:-----|:---------|:---------|:----------|
| Completion → Agent | 工具调用的可靠性（~85%） | Function Calling API 成熟 + 模型更好的指令遵循 | Copilot Chat (过渡态) |
| Agent → Harness | 工程复杂度 + 约束层的维护成本 | 出现成熟的 Harness 框架（MCP, OpenClaw） | 原始 tool_use + 手动校验 |
| Agent → Loop | 收敛不保证 + 成本线性增长 | Claude Code /loop, Cursor /loop 实践验证 | 手写 retry 循环 |
| Agent → Graph | 拓扑设计复杂 + 状态管理难 | LangGraph 标准化 + 云 Agent 基础设施 | 硬编码的多 Agent 脚本 |

### 7.3 跃迁速度对比

| 跃迁 | 提案→成熟时间 | 标志性事件 | 速度 |
|:-----|:-------------|:-----------|:-----|
| Completion → Agent | 2021.06 → 2025.02 (~3.5年) | Claude Code → 首个生产级 CLI Agent | 慢 |
| Agent → Harness | 2023.02 → 2024.11 (~1.8年) | MCP → 首个通用工具协议 | 中 |
| Agent → Loop | 2022.10 → 2024.12 (~2.2年) | ReAct → 生产化 Loop | 中 |
| Agent → Graph | 2023.08 → 2026.03 (~2.6年) | AgentVerse → Devin 2.0 | 中 |

**关键洞察**: 跃迁速度在加快——从 Completion→Agent 的 3.5 年，到 Agent→Harness 的 1.8 年。这验证了"模型的进步正在加速工程范式的迭代"。

### 7.4 范式共存：不是替代关系

**最重要的事实在文档中容易被忽略**: 每个新范式不是替代旧范式，而是**在旧范式之上叠加新抽象层**。

```text
生产系统中的真实分层：
+-----------------------------+
|  Graph (拓扑编排层)          |  <- Devin 2.0 / LangGraph
+-----------------------------+
|  Loop (迭代反馈层)           |  <- /loop / Reflexion
+-----------------------------+
|  Harness (约束安全层)        |  <- MCP / OpenClaw / 沙箱
+-----------------------------+
|  Agent (任务决策层)          |  <- 工具调用 / 文件编辑
+-----------------------------+
|  Completion (生成执行层)     |  <- Token 预测 / FIM
+-----------------------------+
```

**Devin 2.0 就是一个五层全栈系统**: 用 Graph 编排多 Agent → 每个 Agent 内用 Loop 迭代修正 → Harness 沙箱保障安全 → Agent 调用工具 → Completion 生成代码。

---

## 8. 经济性分析：各范式的成本结构

### 8.1 成本构成模型

每个范式都有不同的成本分布：

$$\text{Cost} = \text{Input Tokens} \times P_{in} + \text{Output Tokens} \times P_{out} + \text{Tool Cost} + \text{Infra Cost}$$

| 范式 | 输入 Token | 输出 Token | 工具成本 | 基础设施 | 单任务典型成本 |
|:-----|:----------|:----------|:---------|:---------|:--------------|
| **Completion** | ~500-5K | ~50-1K | $0 | $0 | **$0.001-0.05** |
| **Agent** | ~10-100K | ~5-50K | $0-0.1 | $0 | **$0.05-2** |
| **Harness** | ~10-50K | ~5-20K | $0-0.5 | $0.01-0.1 | **$0.1-1** |
| **Loop** | ~50-500K | ~25-200K | $0.01-0.5 | $0.01-0.05 | **$0.5-50** |
| **Graph** | ~100-2M | ~50-500K | $0.1-2 | $0.05-0.5 | **$1-200** |

**数据说明**: 基于 GPT-4o 级别模型定价（$2.5/M input, $10/M output），2026 年 7 月市场价。

### 8.2 LLM 占比下降趋势

```text
范式          LLM Token成本   工程/基础设施成本   LLM占比
------        -------------   ----------------   ------
Completion    $0.01-0.05      ~$0                100%
Agent         $0.05-1         ~$0.01             95%
Harness       $0.05-0.5       $0.1-0.5           50%
Loop          $0.5-20         $0.1-0.5           80%
Graph         $1-100          $0.5-10            60%
```

**关键洞察**: 尽管 Loop 和 Graph 的绝对成本更高，但 LLM Token 成本在总成本中的占比从 100% 下降到 60-80%。工程基础设施成本正在成为新的主导成本。这意味着：

1. 优化 Token 消耗带来的收益递减——当 Token 只占总成本的 60%，优化 Token 最多省 60%
2. **确定性路由的 ROI 最高**——每把一条路径从"LLM 决策"切换到"代码控制"，就省掉了 100% 的 LLM 成本

### 8.3 成本/质量权衡曲线

```text
质量
  ^
  |      ★ Graph (90-95% SWE-bench)
  |         |
  |      ★ Loop (85-91% HumanEval)
  |         |
  |      ★ Agent (70-85%)
  |         |
  |      ★ Harness (可靠性保障)
  |         |
  |      ★ Completion (50-67%)
  |
  +-------------------------> Cost/task
        $0.01  $0.1  $1  $10  $100
```

**ROI 最优区间**: 多数团队的最佳 ROI 在 Agent + Loop 组合（$0.5-5/任务），而不是直接上 Graph（$1-200/任务）。Graph 只在"全自动交付"场景下 ROI 合理。

### 8.4 成本控制策略

| 策略 | 适用范式 | 节省 | 副作用 |
|:-----|:---------|:-----|:-------|
| Cache 命中 + 复用 | Completion | 50-80% | 需要精确匹配 |
| 确定性优先路径 | Agent + Harness | 30-70% | 需要预定义路由 |
| 早期终止 (Early Halt) | Loop | 20-50% | 可能牺牲质量 |
| State 裁剪 | Graph | 30-60% | 丢失回溯能力 |
| 模型降级 (强→弱) | Loop + Graph | 40-70% | 质量下降 |
| Adaptive Graph 剪枝 | Graph | 20-40% | 实现复杂度高 |

---

## 9. 跨范式对比与选择依据

### 9.1 按任务复杂度选择

```text
Task Complexity
          |
  complex |    Graph -- multi-Agent / full pipeline
  workflow|        LangGraph/CrewAI/AutoGen
          |
  medium |    Loop + Harness -- single Agent long task
  long   |        ReAct/Reflexion + constraint
          |
  medium |    Agent -- multi-step linear
  multi  |        Cursor Agent/Claude Code
          |
  simple |    Completion -- one-shot code gen
  simple |        Copilot/TabNine
          +----------------------------> width/dependency
```

更多关于 Agent 工程化的深度分析，可参看 [Agent OS 五种范式](../agent-engineering/2026-06-26-agent-os-five-paradigms.md) 和 [AI工程三模式](2026-07-10-ai-engineering-patterns.md)。

### 9.2 ROI 分析（从工程实践角度）

| 范式 | 实现成本 | 效果收益 | ROI | 最佳场景 |
|:-----|:---------|:---------|:---|:---------|
| **Completion** | 极低（API 调用） | 中等（~30% 提速） | ⭐⭐⭐⭐⭐ | 日常编码辅助 |
| **Agent** | 中（工具集成） | 高（5-10× 复杂任务） | ⭐⭐⭐⭐ | 多步开发任务 |
| **Harness** | 高（基础设施） | 极高（可靠性保障） | ⭐⭐⭐⭐ | 企业生产环境 |
| **Loop** | 中（迭代逻辑） | 高（质量提升 20-30%） | ⭐⭐⭐⭐ | 测试驱动开发 |
| **Graph** | 极高（编排系统） | 极高（复杂工作流） | ⭐⭐⭐ | 企业级多Agent流水线 |

### 9.3 组合使用（实际工程中的常态）

在生产环境中，范式不是独占的，而是分层组合的：

```text
[Cursor Agent + Harness + Loop composition]

Harness (OpenClaw governance)
  +- Agent (Cursor Agent decision)
       +- Loop (Claude Code /loop skill iteration)
            +- Graph (multi-Agent collaboration)
```

**实际案例 - CowAgent 系统本身**:

| 层 | 范式 | 实现 |
|:---|:-----|:-----|
| 约束层 | **Harness** | RULE.md + AGENT.md + 安全红线 |
| 决策层 | **Agent** | Skill 匹配 + 工具调度 |
| 执行层 | **Loop** | 审查→修正→再审查迭代 |
| 编排层 | **Graph** | Pipeline Orchestrator (6 阶段) |

[来源: CowAgent 系统架构, 参见 [AI工程三模式](2026-07-10-ai-engineering-patterns.md) 和 [Agent 工具链工程化](../agent-engineering/2026-06-26-agent-toolchain-cli-execution.md)]

---

## 10. 关键时间线与里程碑

### 10.1 时间线图谱

```text
Year  Paradigm Milestone Event                                              Key Capability
----  ------  ----------------------------------------------------------------  -------------
2017  --      Transformer (Attention Is All You Need)                         seq modeling
2018  Compl   TabNine released (based on GPT-2)                              code complete
2020  Compl   GPT-3 (175B) + Codex paper                                    large code model
2021  Compl   GitHub Copilot preview                                       mainstream
2022.10 Loop   ReAct paper [arXiv:2210.03629]                              Think-Act loop
2023.02 Harness Toolformer [arXiv:2302.04761]                             self-supervised tool
2023.03 Loop   Reflexion [arXiv:2303.11366] -> HumanEval 91%              reflect+memory
2023.06 Harness OpenAI Function Calling API release                       structured tool
2023.08 Graph  AgentBench [arXiv:2308.03688]                              Agent benchmark
2023.08 Graph  AgentVerse [arXiv:2308.10848]                              multi-Agent collab
2024.02 Agent  Cursor Composer multi-file edit                            project-level
2024.03 Agent  Devin debut (SWE-bench 13.86%)                            auto engineer
2024.11 Harness MCP protocol (Anthropic)                                 general tool proto
2025.02 Agent  Claude Code CLI Agent                                     terminal Agent
2025.04 Harness A2A protocol (Google)                                    cross-Agent comm
2025.06 Loop   Cursor /loop skill periodic execution                     loop automation
2025.12 Agent  Trae (ByteDance) CN-optimized                            CN-coding Agent
2026.03 Graph  Devin 2.0 -> SWE-bench 89%                               multi-Agent pipe
2026.05 Loop   Claude Opus 4.7 -> SWE-bench 87.6%                       strong coding
2026.06 Graph  Cursor Cloud Agent + Slack/Mobile                         cloud multi-Agent
2026.07 Graph  LangGraph as Agent standard                               DAG mainstream
```

### 10.2 SWE-bench 关键演进

| Time  | Model/System   | Rate  | Paradigm |
|:------|:---------------|:------|:---------|
| 2024.03 | Devin 1.0      | 13.86%| Agent    |
| 2024.06 | Claude 3.5 S   | 24.8% | Agent    |
| 2024.12 | Codex CLI | ~38% | Agent + Loop |
| 2025.02 | Claude Opus 4 | 53.8% | Agent + Loop |
| 2025.06 | GPT-5 | ~72% | Agent + Harness |
| 2025.12 | Devin 2.0 (早期) | ~78% | Agent + Harness + Loop |
| 2026.03 | Devin 2.0 | **89%** | Graph + Harness + Loop |
| 2026.05 | Claude Opus 4.7 | **87.6%** | Agent + Loop |

**趋势**: 从单 Agent → 多 Agent Graph 协作（Devin 2.0 的 Planner + Coder + Tester 团队架构）。

---

## 11. 趋势展望与未解决问题

### 11.1 确定性趋势：从"LLM核心"到"Harness核心"

```text
Completion    -- LLM 100%
Agent         -- LLM 80% + tool 20%
Harness       -- constraint 40% + LLM 30% + route 30%
Loop          -- feedback 40% + LLM 30% + tool 30%
Graph         -- topology 30% + state 25% + LLM 25% + tool 20%
```

**核心洞察**: AI 编程的演进实质上是**LLM 的占比在下降，工程化占比在上升**。最好的 AI 编程系统不是"最聪明的模型"，而是"最好的约束系统 + 够用的模型"。

### 11.2 未解决的挑战

| 挑战 | 描述 | 可能方向 |
|:-----|:-----|:---------|
| **验证问题** | 如何验证 LLM 生成代码的正确性？测试覆盖率永远不够 | 形式化验证 + 运行时监控 + 模糊测试 |
| **归因问题** | 多步 Graph 中，错误由哪个节点导致？ | 追踪传播 + 因果归因 |
| **成本边界** | Graph 的 Token 消耗可能失控 | Token Budget + 动态裁剪 + 确定性优先 |
| **配置复杂度** | Graph 的编排配置远超手写工作流 | 从代码自动生成 Graph + 自适应拓扑 |
| **人机信任** | 开发者在多大程度上信任 AI 生成的生产代码？ | 渐进信任 + 可解释性 + 回滚保证 |

### 11.3 下一阶段：Agent OS（2026+）

**从当前趋势看，下一阶段将是 Agent OS**——不仅仅是 Graph 编排，而是完整的 Agent 操作系统：

| 组件 | 功能 | 类比传统 OS |
|:-----|:-----|:------------|
| Execution (E)     | sandbox + resource limit  | process mgmt |
| Tool Protocol (T) | unified iface + det route | device driver |
| Context (C)       | memory hierarchy + policy | virtual memory |
| Lifecycle (L)     | task state machine + ckpt | process sched |
| Observability (O) | trace + audit + monitor   | system log    |
| Verification (V)  | output verify + constrain | access control|
| Governance (G)    | permission + auth + comp  | security mgmt |

[来源: [Agent OS：五种驯服不确定性的范式](../agent-engineering/2026-06-26-agent-os-five-paradigms.md), [AI技术演进年度总结](../llm-techniques-principles/2026-06-28-ai-technology-evolution-annual-summary.md)]

### 11.4 关键预测

| 预测 | 时间窗口 | 置信度 |
|:-----|:---------|:-------|
| Graph 编排将成为 AI 编程系统的默认架构 | 2026-2027 | 高 |
| Harness Engineering 将成为 AI 工程的核心岗位 | 2026-2027 | 高 |
| 确定性路由 (Rule > API > CLI > MCP) 将取代 Prompt Engineering 成为第一优先级 | 2026-2028 | 中 |
| 单一通用 Agent 将被多 Agent Graph 完全取代 | 2027-2028 | 中 |
| "AI 编程"将不再是一个独立话题——它将成为所有 IDE 的默认基础设施 | 2027+ | 高 |

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- [来源: GitHub Copilot Blog, OpenAI Codex Paper, 参见 [AI技术演进年度总结](../llm-techniques-principles/2026-06-28-ai-technology-evolution-annual-summary.md) — 关联
- [来源: SWE-bench Leaderboard, Agentic Design Patterns (DeepLearning.AI), Stack Overflow 2025 Survey, 参见 [Agent OS 五种范式](../agent-engineering/2026-06-26-agent-os-five-paradigms.md) — 关联
- [AI工程三模式](2026-07-10-ai-engineering-patterns.md) — 关联
- [Agent 工具链工程化](../agent-engineering/2026-06-26-agent-toolchain-cli-execution.md) — 关联

### 外部资料引用

- 来源: **ReAct**: Synergizing Reasoning and Acting in Language Models. Yao et al., ICLR 2023
- 来源: **Reflexion**: Language Agents with Verbal Reinforcement Learning. Shinn et al., NeurIPS 2023
- 来源: **Toolformer**: Language Models Can Teach Themselves to Use Tools. Schick et al., 2023
- 来源: **AgentBench**: Evaluating LLMs as Agents. Liu et al., ICLR 2024
- 来源: **AgentVerse**: Facilitating Multi-Agent Collaboration. Chen et al., 2023
- 来源: **Tree of Thoughts**: Deliberate Problem Solving with LLMs. Yao et al., NeurIPS 2023
- 来源: **Language Agent Tree Search**: LATS. Zhou et al., 2024
- 来源: **FlowReasoner**: Multi-Agent Topology Generation. Gao et al., 2025a
- 来源: --

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-22 | v1 — 初始创建，五大范式基础分析 | 小龙猫 |
