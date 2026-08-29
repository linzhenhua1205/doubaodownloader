# 🧬 AI Agent 构成要素深度解剖：从 Loop 到 Channel 的完整架构（含编程场景四 Agent 对比）

> **元信息**: 文件状态=正式 | 覆盖范围=Agent 构成要素（Prompt 分级/记忆/Loop/工具 MCP/CLI/Scripts/Skills/Workflow/Subagent/并行化/旁路调用/上下文处理/Channel）+ 演进路标 + 编程场景四 Agent 对比 | 版本=v1.0
> **适用范围**: Agent 平台架构设计、编程 Agent 选型、Harness 工程实践、AI 产品规划
> **关键词**: Agent 构成 · Prompt 分级 · CLAUDE.md · Memory · Loop · MCP · Skills · Subagent · 并行化 · Background Tasks · Hooks · 上下文处理 · Channel · Claude Code · Trae · Qoder · CodeBuddy · 演进路标

## 目录 (TOC)

- [§0 执行摘要](#0-执行摘要)
- [§1 构成要素总览：六层架构模型](#1-构成要素总览六层架构模型)
  - [1.1 六层模型](#11-六层模型)
  - [1.2 与 Agent OS ETCLOVG 七层的映射](#12-与-agent-os-etclovg-七层的映射)
- [§2 Prompt 与分级体系（Rule / Agent / Memory / User）](#2-prompt-与分级体系rule--agent--memory--user)
  - [2.1 四级 Prompt 的分工原则](#21-四级-prompt-的分工原则)
  - [2.2 Claude Code 的 CLAUDE.md 分层实现](#22-claude-code-的-claudemd-分层实现)
  - [2.3 分级体系的本质：稳定性 × 作用域的二维切分](#23-分级体系的本质稳定性--作用域的二维切分)
- [§3 Memory 记忆子系统](#3-memory-记忆子系统)
  - [3.1 四类记忆的架构定位](#31-四类记忆的架构定位)
  - [3.2 记忆全生命周期：写入/检索/遗忘](#32-记忆全生命周期写入检索遗忘)
  - [3.3 三种典型实现：Claude Code / CowAgent / 知识库记忆](#33-三种典型实现claude-code--cowagent--知识库记忆)
- [§4 Loop 推理循环：Agent 的心脏](#4-loop-推理循环agent-的心脏)
  - [4.1 主循环机制](#41-主循环机制)
  - [4.2 Long Horizon：长视界循环](#42-long-horizon长视界循环)
  - [4.3 循环的工程化：从提示词到运行时](#43-循环的工程化从提示词到运行时)
- [§5 工具面：Tools / MCP / CLI / Scripts](#5-工具面tools--mcp--cli--scripts)
  - [5.1 内置工具集](#51-内置工具集)
  - [5.2 MCP：工具接入的开放协议](#52-mcp工具接入的开放协议)
  - [5.3 面向 Agent 的 CLI 设计](#53-面向-agent-的-cli-设计)
  - [5.4 Scripts：可执行经验沉淀](#54-scripts可执行经验沉淀)
- [§6 Skills 技能子系统](#6-skills-技能子系统)
  - [6.1 SKILL.md 声明式技能](#61-skillmd-声明式技能)
  - [6.2 Skill vs Workflow vs Script vs Command 四者辨析](#62-skill-vs-workflow-vs-script-vs-command-四者辨析)
- [§7 编排层：Workflow / Subagent / 并行化 / 旁路调用](#7-编排层workflow--subagent--并行化--旁路调用)
  - [7.1 Workflow：动态工作流六模式](#71-workflow动态工作流六模式)
  - [7.2 Subagent：子代理与上下文隔离](#72-subagent子代理与上下文隔离)
  - [7.3 并行化处理：Parallel Tool Use / Fanout / 后台任务](#73-并行化处理parallel-tool-use--fanout--后台任务)
  - [7.4 旁路调用（BTW）：Hooks / 事件驱动 / 异步通知](#74-旁路调用btwhooks--事件驱动--异步通知)
- [§8 上下文处理机制](#8-上下文处理机制)
  - [8.1 上下文工程四手段](#81-上下文工程四手段)
  - [8.2 压缩与驱逐策略](#82-压缩与驱逐策略)
  - [8.3 Prompt Caching：上下文的经济学](#83-prompt-caching上下文的经济学)
- [§9 Channel 对外通道](#9-channel-对外通道)
  - [9.1 多通道接入架构](#91-多通道接入架构)
  - [9.2 来源通道路由（Originating Channel）](#92-来源通道路由originating-channel)
  - [9.3 Claude Code 的通道形态演进](#93-claude-code-的通道形态演进)
- [§10 Agent 演进路标与方向](#10-agent-演进路标与方向)
  - [10.1 五层自进化路标](#101-五层自进化路标)
  - [10.2 运行时架构四阶段演进](#102-运行时架构四阶段演进)
  - [10.3 演进方向判断](#103-演进方向判断)
- [§11 当前面临的问题](#11-当前面临的问题)
- [§12 编程场景四 Agent 对比：Claude Code / Trae / Qoder / CodeBuddy](#12-编程场景四-agent-对比claude-code--trae--qoder--codebuddy)
  - [12.1 四 Agent 特征画像](#121-四-agent-特征画像)
  - [12.2 构成要素对照矩阵](#122-构成要素对照矩阵)
  - [12.3 路径演进对比](#123-路径演进对比)
  - [12.4 选型判断](#124-选型判断)
- [§13 结论](#13-结论)
- [参考文献](#参考文献)
- [变更记录](#变更记录)

---

## §0 执行摘要

本报告对 **AI Agent 的构成要素**做逐一解剖，覆盖用户列出的全部 13 项（loop / skills / mcp / scripts / memory / prompt 分级 / workflow / subagent / 并行化 / 旁路调用 / 上下文处理 / channel），并以 Claude Code 特性为基准补齐，最后落到编程场景四 Agent（Claude Code / Trae / Qoder / CodeBuddy）对比。

**核心结论（八大判断）**：

1. **构成要素可组织为六层模型**：Prompt 分级层 → 记忆层 → 推理循环层（Loop）→ 工具层（Tools/MCP/CLI/Scripts）→ 技能层（Skills）→ 编排层（Workflow/Subagent/并行/旁路）→ 通道层（Channel）。**"概率性内核（LLM+Prompt）被确定性外壳（工具/Skill/编排/通道）包裹"是唯一正确的架构姿势**。
2. **Prompt 分级的本质是"稳定性 × 作用域"二维切分**：Rule（全局稳定约束）/ Agent（人格行为）/ Memory（高频动态事实）/ User（静态身份）——Claude Code 的 CLAUDE.md 分层（enterprise/project/user + @import）与本知识库的 AGENT/USER/RULE/MEMORY 四文件是同构设计。
3. **Memory 的胜负手在写入侧**：四类记忆（工作/情景/语义/程序）各有生命周期与风险；Append-only 事件日志 + 受控谓词表 + Provenance 跟随是生产级基线。
4. **Loop 是 Agent 的心脏，但正在被工程化**：从 ReAct（纯提示词维持）→ Long Horizon（单一推理循环）→ Workflow Runtime（循环编译为可执行脚本）——"确定的骨架归代码，不确定的判断归模型"。
5. **工具面三件套各司其职**：内置 Tools（原子操作）/ MCP（开放协议接入）/ CLI（鉴权与执行边界）/ Scripts（可执行经验）——面向 Agent 的 CLI 设计规范是 2026 年最被低估的工程杠杆。
6. **编排层四机制解决"一个上下文不够用"**：Workflow（固定骨架）/ Subagent（上下文隔离）/ 并行化（吞吐）/ 旁路调用（异步与事件驱动）——其中 **Background Tasks + Hooks 是 Claude Code 2025-2026 最具标志性的两个补充**，把 Agent 从"单线程对话"推向"多任务并发系统"。
7. **上下文处理是成本与质量的交汇点**：截断/裁剪/压缩/缓存四层策略 + Prompt Caching 前缀复用——Rovo 第二代"95% 上下文驱逐 + 分层 prompt 组装"是当前最优实践。
8. **编程四 Agent 呈现三种路径**：Claude Code（深度 Harness 路线：子代理/Hooks/后台任务/动态工作流）+ Trae（IDE 一体化路线：Builder 模式 + TRAE Work 多端调度）+ Qoder（Spec 驱动路线：Agent/Quest 模式 + 编程行为预测）+ CodeBuddy（全链路交付路线：构思→发布一站式）。**中国三厂正在从"IDE 补全"向"自主 Agent"集体跃迁，但构成要素的完备度与 Claude Code 仍有代差（尤其在 Subagent/动态工作流/后台任务三项）**。

---

## §1 构成要素总览：六层架构模型

### 1.1 六层模型

综合 Claude Code 工程实践、CowAgent Harness 四层源码实证 [来源: CowAgent Agent Harness 架构深度解读] 与知识库 Agent OS 理论框架，Agent 的构成要素可组织为 **六层（从内到外）**：

```text
+-----------------------------------------------------------------+
| L6 CHANNEL  对外通道（IM/终端/IDE/Web/API/SDK）     —— 消息进出   |
+-----------------------------------------------------------------+
| L5 编排层    Workflow / Subagent / 并行化 / 旁路调用 —— 任务组织   |
+-----------------------------------------------------------------+
| L4 SKILLS    Skills（SKILL.md 声明式技能）          —— 经验复用   |
+-----------------------------------------------------------------+
| L3 工具面    Tools / MCP / CLI / Scripts            —— 行动接口   |
+-----------------------------------------------------------------+
| L2 LOOP     推理循环（感知->规划->行动->观察->反思）     —— 心脏       |
+-----------------------------------------------------------------+
| L1 认知基座  Prompt 分级（Rule/Agent/Memory/User）+ Memory 子系统 |
+-----------------------------------------------------------------+
```

| 层 | 构成要素 | 回答的问题 | 确定性 |
|:---|:---------|:-----------|:------:|
| L1 认知基座 | Prompt 分级（RULE/AGENT/MEMORY/USER）+ Memory | "Agent 是谁、知道什么、受什么约束" | 半确定性 |
| L2 Loop | 主循环、Long Horizon、Workflow Runtime | "如何持续思考与行动" | 概率性（内核） |
| L3 工具面 | 内置 Tools / MCP / CLI / Scripts | "如何与外部世界交互" | 确定性 |
| L4 Skills | SKILL.md 技能包 | "经验如何复用" | 半确定性 |
| L5 编排层 | Workflow / Subagent / 并行化 / 旁路 | "一个上下文不够用时怎么办" | 确定性 |
| L6 Channel | 多通道接入 / 来源路由 | "消息从哪来、回哪去" | 确定性 |

> **核心架构原则**：只有 L2（LLM 推理）是概率性的，其余五层都应尽量确定性化——**把不确定性限制在模型推理边界内**，这是知识库平台工程专题的核心命题在构成要素层面的展开 [来源: Agent 平台工程]。

### 1.2 与 Agent OS ETCLOVG 七层的映射

知识库 Agent OS 专题提出 ETCLOVG 七层 [来源: Agent OS 五种范式]：

| ETCLOVG 七层 | 本报告六层 | 对应构成要素 |
|:-------------|:-----------|:-------------|
| E – Execution Environment | L3 工具面 | 沙箱、bash、文件系统 |
| T – Tool Interface & Protocol | L3 工具面 | MCP、Tools、CLI |
| C – Context & Memory | L1 认知基座 | Memory 四类 + 上下文处理 |
| L – Lifecycle & Orchestration（核心层） | L5 编排层 + L2 Loop | Workflow、Subagent、并行、旁路 |
| O – Observability | 横切 | Hooks 通知、日志、状态行 |
| V – Verification & Evaluation | 横切 | 测试循环、评估基准 |
| G – Governance & Security | 横切 | 权限分级、Action Gate |

---

## §2 Prompt 与分级体系（Rule / Agent / Memory / User）

### 2.1 四级 Prompt 的分工原则

Prompt 不是"一段提示词"，而是一套**分级注入的认知基座**。以本知识库的四文件体系为范式 [来源: 知识库 RULE.md 存储规则 + 自进化五层 L1]：

| 级别 | 文件（本库） | 内容 | 变化频率 | 注入方式 | 违背后果 |
|:-----|:------------|:-----|:--------:|:---------|:---------|
| **Rule** | RULE.md | 铁律、存储规则、安全红线、指令优先级 | 季更 | 每次会话全量 | 违反有明确后果（L2 工程约束） |
| **Agent** | AGENT.md | 人格、行为准则、协作模式、自检清单 | 季更 | 每次会话全量 | 行为漂移 |
| **User** | USER.md | 身份、偏好、质量标准 | 年更 | 每次会话全量 | 服务失配 |
| **Memory** | MEMORY.md + memory/日 | 长期事实/决策 + 当日进展 | 日/月更 | 核心全量 + 日级检索加载 | 遗忘/冲突 |

**分级的第一性原理**：不是"写得越多越好"，而是**按"稳定性 × 作用域"切分，让高频变动的信息不污染低频稳定的指令**——

- 稳定的约束（Rule/Agent/User）→ 常驻系统提示词，保证一致性
- 高频动态的事实（Memory）→ 分层存储 + 检索注入，避免上下文膨胀

### 2.2 Claude Code 的 CLAUDE.md 分层实现

Claude Code 把同一思想实现为 **CLAUDE.md 三明治结构**：

| 层级 | 位置 | 作用域 | 优先级 |
|:-----|:-----|:-------|:------:|
| **Enterprise Policy** | 托管管理（企业级） | 全局强制 | 最高 |
| **User** | `~/.claude/CLAUDE.md` | 跨项目用户偏好 | 中 |
| **Project** | 项目根 `CLAUDE.md` + `@import` 子文件 | 单项目规范 | 随目录层级 |

关键机制：

- **@import 指令**：CLAUDE.md 可拆分为多个子文件（如 `CLAUDE.md` 引用 `docs/2026-07-29-architecture.md`），按需加载——**作用域化的 prompt 组装**
- **分层覆盖**：越靠近项目的规则越具体，用户级与项目级可叠加
- **记忆与规则分离**：Claude Code 另用 Memory 工具管理长期记忆（`/memory`），与 CLAUDE.md（指令）分离——与知识库"MEMORY.md 存事实、RULE.md 存约束"完全同构

### 2.3 分级体系的本质：稳定性 × 作用域的二维切分

```text
        作用域
  全局  +----------------------+
        |  RULE（铁律）         |  USER（身份偏好）
        |  AGENT（人格）        |
        +----------------------+
  项目  |  CLAUDE.md Project    |  CLAUDE.md @import 子模块
        |  企业 Policy          |
        +----------------------+
  会话  |  系统提示词模板        |  Memory 注入（检索命中）
        +----------------------+
            稳定（季/年更）       动态（日/会话级）
                        <- 变化频率 ->
```

> **工程启示**：Agent 化应用的 prompt 体系设计 = 在这张二维表里为每类信息找到格子。最常见的失败模式是"把日更事实写进年更约束"（上下文膨胀、规则失效）或"把铁律写进可被覆盖的会话提示词"（安全失效）。

---

## §3 Memory 记忆子系统

### 3.1 四类记忆的架构定位

知识库 Harness Memory 专题给出四类记忆 [来源: Harness Agent Memory 纵深防御]：

| 类型 | 回答 | 推荐形态 | 主要风险 |
|:-----|:-----|:---------|:---------|
| **Working Memory** | 当前任务做到哪一步？ | Context + 状态表 | 摘要丢失来源 |
| **Episodic Memory** | 过去发生过什么？ | Append-only 事件日志 | 日志含敏感输入 |
| **Semantic Memory** | 当前相信哪些事实？ | 结构化事实 + 向量/全文索引 | 错误事实被持续召回 |
| **Procedural Memory** | 以后应该怎样做？ | 版本化 Skill/模板 | 持久化行为后门 |

**反模式**：把对话、事件、事实、流程全部切片后放进同一个向量集合——同时失去历史不可变性、当前信念一致性、流程版本治理、精确删除能力。

### 3.2 记忆全生命周期：写入/检索/遗忘

**写入侧（胜负手）**：

- Hot Path（同步，仅处理"下一步必须立刻可见"）vs Cold Path（异步，长期事实/流程固化）
- 写入对象必须是**原子事实**（subject-predicate-object 三元组），维护**受控谓词表**避免 `likes_framework`/`favorite_backend` 无法等同
- **Confidence ≠ Trust**：`extraction_confidence=0.99` 只说明模型"看清楚了邮件写了什么"，不说明邮件内容可信

**检索侧**：核心记忆全量注入 + 天级记忆检索加载（本知识库 CowAgent 实现）；向量+关键词加权 + 时间半衰期（30 天衰减仅对 memory/ 前缀）

**遗忘侧**（四机制）：TTL 硬过期 / Invalidation 关闭有效区间 / Decay-Archive 转冷存 / Subject Deletion 按数据主体删除；双时态（Valid Time vs Transaction Time）需区分

### 3.3 三种典型实现：Claude Code / CowAgent / 知识库记忆

| 实现 | 形态 | 特点 |
|:-----|:-----|:-----|
| **Claude Code Memory** | `/memory` 工具 + CLAUDE.md | 工具化记忆管理，用户显式/隐式触发写入；会话间持久 |
| **CowAgent Memory** | MEMORY.md 核心 + memory/日 + 向量库 | 核心全量注入 + 日级检索；L2 上下文超限时总结沉淀；L3 会话后复盘进化 |
| **知识库记忆** | knowledge/ 结构化 + 索引 + 日志 | 跨会话、跨 Agent 共享的长期知识；按主题组织 + 交叉引用 + 变更追踪 |

> 演进方向：**记忆从"附属于会话"走向"独立于 Agent 的基础设施"**——可跨 Agent 共享、带 Provenance、可审计删除（知识库 08-03 索引/日志双轨制正是这一方向的知识管理实例）。

---

## §4 Loop 推理循环：Agent 的心脏

### 4.1 主循环机制

所有 Agent 共享同一心脏——**感知→规划→行动→观察→反思**循环：

```text
+--------------------------------------------+
|  while not done:                            |
|    1. 感知  收集环境状态（工具结果/文件/消息）|
|    2. 规划  基于全量上下文决定下一步          |
|    3. 行动  调用工具/生成文本/发起子任务      |
|    4. 观察  获取工具返回值作为 ground truth  |
|    5. 反思  评估进展，决定继续/终止/求助      |
|  终止条件：任务完成 / 最大迭代 / 人类干预     |
+--------------------------------------------+
```

Claude Code 的实现细节：

- 每轮调用 LLM 时携带全量对话状态 + 可用工具 schema
- **并行工具调用**（Parallel Tool Use）：同一轮可发起多个独立工具调用，显著减少往返
- 工具结果作为环境 ground truth 追加进上下文
- 计划模式（Plan Mode）：只读分析、产出计划，批准后才执行——**把"想"与"做"分离**

### 4.2 Long Horizon：长视界循环

知识库编排范式专题的核心案例 [来源: Agent 编排范式深度技术分析]——Rovo 第二代 Long Horizon 引擎：

- **one LLM, one context, one iterative loop**：单一模型持有全部上下文，循环可达 150 次迭代
- **Adaptive Reasoning Effort**：简单查询几乎零额外开销，复杂任务深入规划——同一架构服务两个极端
- 五项工程机制：flattened tools（工具展平）/ SKILL.md 技能化 / progressive disclosure（元工具按需披露）/ context compaction（95% 驱逐 + offload）/ child instances（并行子实例）/ 分层 prompt 组装 + cache_control 前缀缓存

> **关键洞察**：编排范式的收敛共识是"单一协调上下文 + 按需并行子任务"——Loop 是主心骨，并行是加速器，二者不矛盾。

### 4.3 循环的工程化：从提示词到运行时

知识库 Workflow Runtime 专题 [来源: Agent Workflow Runtime 架构]：

> "I don't prompt Claude anymore. I have loops running that prompt Claude." — Boris Cherny

| 阶段 | 循环的载体 | 特点 | 缺陷 |
|:-----|:-----------|:-----|:-----|
| ReAct（纯提示词） | 模型上下文里维持 | 灵活但结构漂移 | 跑十次结构不同、复盘困难 |
| Harness（框架） | 代码模板 | 结构固定 | 需要人写模板 |
| **Dynamic Workflow** | 模型现场生成的脚本 | 强模型生成一次，弱模型执行多次 | 需要生成能力 |
| **Workflow Runtime** | 编译后的可执行运行时 | 可观察/可恢复/可复用 | 平台化复杂度 |

---

## §5 工具面：Tools / MCP / CLI / Scripts

### 5.1 内置工具集

Claude Code 内置工具是"最小完备行动面"：

| 类别 | 工具 | 说明 |
|:-----|:-----|:-----|
| 文件 | Read / Write / Edit / MultiEdit | 读写改（Edit 用 diff 语义，Anthropic 强调格式贴近模型训练分布） |
| 检索 | Glob / Grep / Code Search | 符号级代码检索（LSP 语义） |
| 执行 | Bash | 终端执行（沙箱 + 权限控制） |
| 网络 | WebSearch / WebFetch | 内置联网 |
| 视觉 | Vision | 看图、设计稿→代码 |
| 记忆 | Memory | 长期记忆读写 |
| 其他 | TodoWrite（任务清单）/ Task（子代理）/ 通知 |

### 5.2 MCP：工具接入的开放协议

**MCP（Model Context Protocol）** 是工具面的"USB 接口"（知识库平台工程专题 [来源: Agent 平台工程 §5.3]）：

```text
+----------+    MCP 协议    +-------------+
|  Agent   | <------------> | MCP Server  |--> 工具/数据源
| (Client) |  工具发现/调用  | (Filesystem/ |    (GitHub/数据库/
+----------+   鉴权/回调     |  Browser/DB) |     浏览器/内部系统)
                            +-------------+
```

Claude Code 同时是 MCP **Client**（配置 `.mcp.json` 接入外部 server）与 MCP **Host**（也可作为 server 被其他 Agent 调用）。生态现状：mcp.so / mcpworld 等目录站点爆发，浏览器自动化（Playwright MCP）、数据库、金融（Banks to AI 12,000+ 机构）等 server 丰富。

### 5.3 面向 Agent 的 CLI 设计

知识库工具链专题的核心规范 [来源: Agent 工具链工程化]——**Skill 负责编排判断、CLI 稳定交付执行**：

| 设计维度 | 要求 | 反面教材 |
|:---------|:-----|:---------|
| 参数 | `--doc`/`--format json` 显式参数，不让模型猜 | 自由文本塞参数 |
| 输出 | 结构化可解析（状态/产物路径/出错位置+下一步建议） | 人类可读但不可解析 |
| 安全 | dry-run 预检 + 确认机制 | 靠提示词拦删除 |
| 失败路径 | 明确失败阶段（鉴权/参数/网络/资源/权限）+ 可恢复动作 | 只丢一句模糊报错 |

### 5.4 Scripts：可执行经验沉淀

- **Scripts = 把经验编译为可执行文件**：输入→输出→失败方式→恢复动作四要素完备的 CLI 脚本
- 与 Skills 的分工：Skill 决定"何时用、怎么组织"，Script 决定"怎么执行、执行不了怎么办"
- 迁移判断标准：任务有明确输入/输出边界 + 会反复执行 + 需要鉴权 → 优先 CLI 化
- 本知识库实践：脚本纪律（try/except 隔离、参数声明必须实现、路径解析勿二次处理）正是"Scripts 面向 Agent 可用性"的经验沉淀

---

## §6 Skills 技能子系统

### 6.1 SKILL.md 声明式技能

**Skills**（Anthropic 2025-10 推出，Claude Code 与 Claude App 通用）是把"过程知识"打包为可复用单元的机制：

```text
.skills/
+-- <skill-name>/
    +-- SKILL.md      # 声明式描述：触发条件/步骤/产出规范/注意事项
    +-- scripts/      # 配套可执行脚本（可选）
```

- **触发机制**：Agent 根据任务相关性自动加载（不是常驻），避免上下文膨胀
- **与 CLAUDE.md 的分工**：CLAUDE.md = 静态规则（"你是谁"），Skills = 动态能力（"你会做什么"）
- **生态**：cow-skill-hub、skills.cowagent.ai 等开放市场，跨平台分发（Claude Code/CowAgent/OpenClaw 通用）

### 6.2 Skill vs Workflow vs Script vs Command 四者辨析

| 机制 | 载体 | 执行主体 | 变化性 | 用途 |
|:-----|:-----|:---------|:-------|:-----|
| **Skill** | SKILL.md 自然语言说明 | 模型理解执行 | 每次可能不同 | 探索性/边界模糊任务 |
| **Workflow** | 脚本控制流（代码） | 代码执行，模型只在节点出手 | 显式固定 | 阶段清楚/有验收/反复执行 |
| **Script** | CLI 可执行文件 | 确定性执行 | 完全固定 | 有明确输入输出边界的原子操作 |
| **Command** | 斜杠命令（`.claude/commands/*.md`） | 用户触发 + 模型执行 | 模板化 | 用户常用操作的快捷封装 |

> **组合模式**：真实场景四者一起出现——"先用 Skill 生成 Workflow，再用 Workflow 编排多个 Agent，Agent 内部调用 Script，用户用 Command 快捷触发"。

---

## §7 编排层：Workflow / Subagent / 并行化 / 旁路调用

### 7.1 Workflow：动态工作流六模式

知识库 Claude Code 动态工作流专题给出六种可复用模式 [来源: Claude Code 动态工作流]：

| 模式 | 机制 | 适用 |
|:-----|:-----|:-----|
| **Classify-and-act** | 先分类再走对应分支 | 输入类型混杂 |
| **Fanout-and-synthesize** | 拆开并行，最后汇总 | 独立子任务 |
| **Adversarial verification** | 独立验证者对抗生成者 | 需要纠错 |
| **Generate-and-filter** | 先生成再筛选 | 候选多、质量参差 |
| **Tournament** | 多方案锦标赛 | 方案择优 |
| **Loop until done** | 直到验收标准满足 | 迭代式交付 |

**关键机制**：Dynamic Workflows 让 Claude **现场生成 Harness**（不再需要人手动搭流程）——流程变成"可存、可改、可重跑"的普通代码。

### 7.2 Subagent：子代理与上下文隔离

**Subagent（子代理）** 是 Claude Code 的核心编排原语：

- **声明式定义**：`.claude/agents/<name>.md`，定义角色/工具权限/指令
- **独立上下文**：子代理持有自己的上下文窗口，只接收父代理传入的任务描述 + 返回结果摘要——**隔离是目的**（避免主上下文被污染）
- **典型子代理**：research（深度调研）/ code review（独立审查）/ security audit

**为什么需要隔离**：单上下文执行有三大失败模式 [来源: Claude Code 动态工作流]——

1. **Agentic laziness**：上下文过长后 Agent 提前"收工"（50 个问题只处理 35 个）
2. **Self-preferential bias**：自我验证漏掉问题（验证与执行共享同一上下文）
3. **Goal drift**：长任务中原始目标保持能力下降

> **注意张力**：子代理隔离解决"上下文污染"，但引入"信息有损交接"（父代理只看摘要）——编排范式专题已证明这是路由式多代理的代价 [来源: Agent 编排范式]。**解法：子代理只用于"边界清晰、结果可摘要"的子任务；深度连续推理留在主循环**。

### 7.3 并行化处理：Parallel Tool Use / Fanout / 后台任务

| 机制 | 粒度 | 说明 | Claude Code 对应 |
|:-----|:-----|:-----|:-----------------|
| **Parallel Tool Use** | 工具调用 | 同一轮并行多个独立工具调用 | ✅ 内置（Claude 4+） |
| **Fanout** | 子任务 | 同一任务拆 N 份并行（动态工作流模式） | ✅ Dynamic Workflow |
| **Background Tasks** | 任务 | 后台运行任务，不阻塞当前对话 | ✅ `/bg`（Claude 4.5 引入） |

**Background Tasks（后台任务）** 是 2025-2026 最有标志性的并行化补充：

- 前台对话继续，后台同时跑长任务（如大规模重构、批量测试）
- 可并行多个后台任务，任务间上下文隔离
- 完成/失败通过 Notification Hook 通知
- **本质**：把 Agent 从"单线程对话"升级为"多任务并发系统"

### 7.4 旁路调用（BTW）：Hooks / 事件驱动 / 异步通知

**Hooks（生命周期钩子）** 是 Claude Code 的"旁路"机制——不进入主推理循环，而是在关键事件点执行外部脚本：

| Hook | 触发时机 | 典型用途 |
|:-----|:---------|:---------|
| `PreToolUse` | 工具调用前 | 拦截高危操作、参数校验 |
| `PostToolUse` | 工具调用后 | 记录、审计、触发联动 |
| `UserPromptSubmit` | 用户消息提交前 | 注入上下文、改写提示 |
| `Stop` | 回复完成 | 通知、落盘 |
| `Notification` | 后台任务完成 | 推送到 IM/桌面 |
| `SessionStart/End` | 会话生命周期 | 初始化/清理 |
| `SubagentStop` | 子代理完成 | 汇总、联动 |

**旁路调用的本质**：把**"与推理无关但必须发生的动作"从主循环剥离**——事件驱动（Event-Driven）而非轮询。知识库另有事件驱动 Agent 故障自愈专题（Prometheus 事件 → Agent 自动修复闭环），是旁路调用在运维场景的延伸。

> **为什么旁路重要**：主循环是"串行 + 概率性"的昂贵资源。把日志、审计、通知、拦截、联动全部塞进主循环 = 上下文膨胀 + Token 浪费 + 失败传播。Hooks 让这些动作**确定性、低成本、可审计**地发生——这是 2026 年 Agent 工程成熟度的重要分水岭。

---

## §8 上下文处理机制

### 8.1 上下文工程四手段

| 手段 | 机制 | 适用 |
|:-----|:-----|:-----|
| **Context Editing** | 主动编辑上下文（删除/替换/追加） | 任务阶段切换 |
| **@-mention 引用** | 按需引用文件/符号，不全量读入 | 大型代码库 |
| **工具结果截断** | 超长结果保留首尾+省略说明（纯字符串） | 第一道防线 |
| **渐进式披露** | meta-tools 按需展开（progressive disclosure） | 工具面规模控制 |

### 8.2 压缩与驱逐策略

知识库自进化五层 L2 的完整策略 [来源: Agent 自进化机制五层]：

```text
工具结果超长 -> 轮次超限裁剪 -> Token超限压缩 -> 溢出兜底
```

| 步骤 | 操作 | 是否调用 LLM | 特点 |
|:-----|:-----|:-----------:|:-----|
| ① 截断超长工具结果 | 保留首尾+省略说明 | ❌ | 第一道防线 |
| ② 按完整轮次裁剪 | 以"一轮完整对话"为最小单位裁掉最早一半 → 提炼总结写天级记忆 | ✅ | 保证工具调用入参/结果成对保留 |
| ③ 按 Token 压缩 | 每轮只留首条提问+末条回复 | ❌ | 精细裁剪 |
| ④ 溢出兜底 | API 抛溢出时总结后激进截断 | ✅ | 最后保险 |

Rovo 第二代的 **context compaction** 更进一步：95% 驱逐 + KV Cache offload——只保留"下一步必须立刻可见"的上下文，其余进分层存储 [来源: Agent 编排范式]。

### 8.3 Prompt Caching：上下文的经济学

- **机制**：前缀缓存——相同的前缀（系统提示词 + 历史上下文）在多次推理间复用，增量成本只算"最新 token"
- **工程实现**：分层 prompt 组装（系统层/会话层/工具层分离）+ `cache_control` 标记
- **量化意义**：Agent 150 次迭代循环中，前缀缓存把每次迭代的 KV 计算从"全量"降到"增量"——**这是 Long Horizon 架构在经济上可行的前提**
- 知识库实测：27 天 2.3B tokens，缓存未命中 58% 是最大成本项 → 缓存命中率是 Agent 推理成本的第一运营指标

---

## §9 Channel 对外通道

### 9.1 多通道接入架构

**Channel** 是 Agent 与外界（人/系统）的消息出入口。CowAgent 的 Harness 架构提供了完整实证 [来源: CowAgent Agent Harness 架构深度解读]：

```text
                    +-------------------------+
  IM (Feishu) ----->|                         |
  终端 Terminal --->|  Channel 层（统一消息）   |
  Web/SSE --------->|  ChatMessage 16 字段     |
  IDE 插件 -------->|  工厂注册制接入          |
  定时任务 -------->|                         |
                    +-----------+-------------+
                                v
                    +-------------------------+
                    | Bridge（能力路由枢纽）    |
                    +-----------+-------------+
                                v
                    +-------------------------+
                    | Agent Core（规划/推理）   |
                    |  + Memory/Knowledge      |
                    |  + Tools/Skills          |
                    +-----------+-------------+
                                v
                    +-------------------------+
                    | Models 层（15+ 厂商）     |
                    +-----------+-------------+
                                v
                    回传走来源通道（originating channel）
```

**统一消息模型**：`ChatMessage` 用字段契约吸收不同平台差异（msg_id/ctype/content/from_user_id/is_group/is_at...），新平台只需映射，核心零改动。

### 9.2 来源通道路由（Originating Channel）

**"回传走来源通道"** 是最易被忽略的细节：消息上下文（Context）携带 `channel_type` 标识贯穿全链路，回传时路由回原通道——这是"多通道接入同一 Agent 而不串台"的基础。

**对多 Agent 系统的延伸**：当 Channel 不限于 IM 而是"任何消息源"（定时任务/事件流/其他 Agent 的 A2A 调用）时，来源路由机制升级为**任务级上下文隔离**——每个任务一个上下文，完成即归档。

### 9.3 Claude Code 的通道形态演进

| 形态 | 时间 | 定位 |
|:-----|:-----|:-----|
| **终端 CLI** | 2025-02 | 原生形态，`claude` 命令 |
| **Headless/SDK** | 2025-06 | Agent SDK，无终端编程调用（CI/CD、服务化） |
| **IDE 集成** | 2025 | VS Code/JetBrains 插件 |
| **Claude Cowork** | 2026-03 | 桌面 GUI 版，面向非开发者办公场景 |
| **Web/Chrome 连接器** | 2026 | Claude in Chrome 浏览器操作 |

> **演进规律**：Channel 从"单一终端"走向"全形态覆盖"——同一 Agent 内核，不同通道适配不同用户场景。这印证了 CowAgent 的架构判断：**Harness 的价值不在推理，而在"任何消息源、任何模型、任何工具都能接入而不改核心"**。

---

## §10 Agent 演进路标与方向

### 10.1 五层自进化路标

知识库自进化专题给出 Agent"在对话中成长"的五层机制 [来源: Agent 自进化机制五层]：

| 层级 | 改进内容 | 触发时机 | 进化深度 |
|:-----|:---------|:---------|:---------|
| **L1 基础记忆维护** | 记忆/知识/提示词 | 每次对话中 | 记录 |
| **L2 上下文智能总结** | 记忆 | 上下文超限时 | 保留 |
| **L3 会话后主动复盘** | 技能/记忆/提示词/任务 | 会话空闲后 | 行动 |
| **L4 梦境记忆整理** | 长期记忆 | 每天定时 | 沉淀 |
| **L5 源代码自更新** | 代码 | 被动/主动触发 | 自我重构 |

> 设计原则：实现修改能力不难，难的是**改得克制、改得可控**（L3 安全可控三原则 + L5 版本冲突问题）。

### 10.2 运行时架构四阶段演进

```text
Harness（执行框架）-> Loop（推理循环）-> Workflow Runtime（循环编译化）-> Agent Substrate（平台化）
     2024                  2025                2025-2026                 2026+
   任务怎么拆/隔离       感知-行动-观察        流程从提示词搬进代码        调度/生命周期/状态/安全/观测平台化
```

| 阶段 | 标志 | 代表 | 解决的问题 |
|:-----|:-----|:-----|:-----------|
| Harness | 组织 Agent 执行 | Claude Code 默认 Harness | 任务拆解/上下文隔离/恢复 |
| Loop | 循环范式确立 | ReAct、Long Horizon | 多步推理的连续性 |
| Workflow Runtime | 循环编译为脚本 | Dynamic Workflow | 流程可观察/可复用 |
| Agent Substrate | 平台化治理 | Google Agent Substrate、"K8s 赢了容器十年" | 多 Agent 的调度/生命周期/安全 |

### 10.3 演进方向判断

1. **上下文连续性为王**：编排范式从"路由式多代理"回归"单一协调上下文 + 按需并行"（Rovo 信号）——**上下文不丢，是 Agent 能力的第一前提**
2. **确定性外壳持续增强**：Subagent/Hooks/Background Tasks/Workflow Runtime 都在把"概率性内核"包进"确定性外壳"
3. **记忆与知识独立化**：Memory 从会话附属走向跨 Agent 基础设施（Provenance/审计/共享）
4. **通道全形态化**：终端 → IDE → 桌面 → Web → 移动端 → 嵌入业务系统
5. **自进化成为标配**：L1-L3（记忆/总结/复盘）已落地，L4-L5（梦境整理/自更新）在途——**进化能力本身需要治理**

---

## §11 当前面临的问题

承接知识库 Agent 深度分析全景报告 [来源: AI Agent 深度分析]，聚焦构成要素层面的具体问题：

| # | 问题 | 构成要素层面表现 | 克服方向 |
|:--|:-----|:-----------------|:---------|
| 1 | **上下文窗口物理极限** | 长任务必然触顶；压缩=信息损失（有损摘要）；驱逐=遗忘 | 分层记忆 + KV offload + 子代理隔离；**接受"上下文是稀缺资源"并做预算管理** |
| 2 | **子代理信息有损交接** | 父代理只看摘要，跨子代理推理链断裂 | 只在边界清晰任务用子代理；深度连续推理留主循环；Agent 间消息带 Provenance |
| 3 | **并行化的正确性** | 并行工具调用竞态（文件冲突/状态覆盖）；后台任务失败难定位 | 依赖图/锁；幂等工具设计；后台任务独立日志 |
| 4 | **Hooks 的复杂性爆炸** | 生命周期钩子多（7+ 类），组合状态空间大；调试困难 | 钩子最小化 + 事件日志 + 可观测性 |
| 5 | **Skill 质量参差** | 声明式技能质量无法自动评估；恶意 Skill 风险 | 技能安全审查（skill-security-vetter）+ 技能评测 + 版本治理 |
| 6 | **MCP 安全面扩大** | 每接入一个 MCP Server = 一个新攻击面（工具注入/凭证泄露） | 最小权限 + 沙箱 + 工具信任分级 + 审计 |
| 7 | **Prompt 分级失守** | 铁律被可覆盖提示词稀释；日更事实污染常驻上下文 | 分级注入 + 变更审计 + 稳定性检测 |
| 8 | **成本失控** | 长上下文 + 多子代理 + 后台任务 = token 线性爆炸 | Prompt Caching + 模型分级 + 上下文预算 + 成本度量进架构决策 |
| 9 | **评估归因困难** | 失败难定位（模型/工具/编排/平台哪层？） | 分层可观测性 + 端到端基准 + 专家终审 |
| 10 | **组织采纳断层** | 79% 入局仅 2% 跑通；工具建设挤压业务深度 | 场景优先 + 先改系统再上 Agent + 预期管理（实习生模型） |

---

## §12 编程场景四 Agent 对比：Claude Code / Trae / Qoder / CodeBuddy

### 12.1 四 Agent 特征画像

**① Claude Code（Anthropic）—— 深度 Harness 路线**

- 形态：终端原生 CLI + IDE 插件 + SDK + Cowork 桌面
- 核心特性：Subagent（.claude/agents 声明式）/ Hooks（7 类生命周期钩子）/ Background Tasks（/bg 多任务并发）/ Dynamic Workflows（现场生成 harness）/ MCP 双角色（Client+Host）/ Skills / CLAUDE.md 分层记忆 / Plan Mode / Checkpoints / Parallel Tool Use / Output Styles
- 构成要素完备度：**最高**（13 项要素全覆盖，Subagent/Hooks/后台任务是独有深度）
- 路径：从"终端编码助手"向"通用 Agent 运行时"演进（Cowork 办公场景 + SDK 服务化）

**② Trae（字节跳动）—— IDE 一体化路线**

- 形态：AI 原生 IDE（VS Code 系）+ TRAE Work（网页/桌面/移动端）+ CLI
- 核心特性：**Builder 模式**（自然语言一键生成项目）/ Agent 模式（对话式自主编程）/ 多模型接入（Claude/GPT-4o/豆包等）/ 代码仓库+终端+联网搜索+文档集理解 / TRAE 移动端=「口袋里的 AI 智能体调度中心」
- 路径：从"AI IDE"向"多端 Agent 调度平台"演进（Builder 降低门槛 → Work 承接任务调度 → 移动端延伸场景）
- 差异化：**面向"非专业开发者也能完成软件开发"的 vibe coding 体验**

**③ Qoder（阿里云）—— Spec 驱动路线**

- 形态：基于 code-oss 的 AI IDE + JetBrains 插件 + CLI + Mobile + QoderWork
- 核心特性：**Agent Mode / Quest Mode（任务模式）/ Spec 工作流（规格驱动开发）/ 编程行为预测 / Repo Wiki（代码库知识库）/ 增强上下文工程 / 知识可视化**
- 路径：从"通义灵码辅助编程"分化出"自主编程"（2025-08 发布）→ 2026-01 全新产品"意图感知"——从"辅助补全"到"独立完成分析-设计-开发"
- 差异化：**Spec 驱动开发**（先规格后编码）+ Repo Wiki（代码库知识沉淀）是其独有工程思想

**④ CodeBuddy（腾讯云）—— 全链路交付路线**

- 形态：IDE 插件 + 独立 IDE + CLI（"从产品构思到产品发布的一站式"）
- 核心特性：基于混元代码大模型 / 代码补全+诊断+优化 / 技术对话 / 国际版集成 GPT-5/Claude-4/Gemini-2.5 / 深度理解代码库
- 路径：从"辅助编码工具"（补全/诊断）向"全流程交付平台"演进
- 差异化：**产品构思→发布的一站式定位**（偏"交付闭环"而非"Agent 架构深度"）

### 12.2 构成要素对照矩阵

| 构成要素 | Claude Code | Trae | Qoder | CodeBuddy |
|:---------|:-----------:|:----:|:-----:|:---------:|
| **Prompt 分级（CLAUDE.md 类）** | ✅ 三层+@import | 🟡 会话级记忆 | 🟡 会话级 | 🟡 会话级 |
| **Memory（长期）** | ✅ /memory 工具 | 🟡 对话记忆 | 🟡 Repo Wiki（知识型） | 🟡 对话记忆 |
| **Loop（自主循环）** | ✅ Long Horizon | ✅ Agent 模式 | ✅ Agent Mode | ✅ Agent 对话 |
| **内置 Tools（文件/终端/检索）** | ✅ 全 | ✅ IDE 集成 | ✅ IDE 集成 | ✅ IDE 集成 |
| **MCP** | ✅ Client+Host | ✅ 支持 | ✅ 支持 | 🟡 部分 |
| **CLI** | ✅ 原生 | ✅ Trae CLI | ✅ Qoder CLI | ✅ CodeBuddy CLI |
| **Scripts** | ✅ bash+脚本 | 🟡 | 🟡 | 🟡 |
| **Skills（SKILL.md）** | ✅ 原生 | 🟡 生态支持 | 🟡 | ❌ |
| **Workflow（动态）** | ✅ Dynamic Workflows | 🟡 任务流 | ✅ Spec 工作流/Quest | 🟡 流程化 |
| **Subagent（子代理）** | ✅ 声明式 | ❌/🟡 | 🟡 多智能体 | ❌ |
| **并行化** | ✅ Parallel+Background | 🟡 多任务 | 🟡 | ❌ |
| **旁路调用（Hooks）** | ✅ 7 类 Hooks | ❌ | ❌ | ❌ |
| **上下文处理** | ✅ 压缩+编辑+缓存 | 🟡 增强上下文 | ✅ 增强上下文工程 | 🟡 |
| **Channel（多端）** | ✅ 终端/IDE/SDK/Cowork | ✅ IDE/Work/移动 | ✅ IDE/插件/CLI/Work | ✅ IDE/CLI |

> 注：✅=原生完备 🟡=部分/生态支持 ❌=缺失。中国三厂信息基于公开资料（2026-08），具体能力随版本快速演进。

### 12.3 路径演进对比

```text
                  2019-2024              2025                    2026
Claude Code:     Claude 模型 ->   终端 Agentic Coding ->   Harness 全面化
                 （无 Agent）    Subagent/Hooks/MCP      (动态工作流/后台任务/
                                                         Cowork 桌面/SDK)
Trae:            ——（2024 立项）  AI IDE（补全+对话） ->   Builder 一键生成 ->
                                                         TRAE Work 多端调度
Qoder:           通义灵码（辅助） -> Qoder 2025-08 自主编程 -> 2026-01 意图感知
                                 Agent/Quest/Spec       + Repo Wiki
CodeBuddy:       腾讯云助手（插件）-> IDE 化（补全/诊断） ->  全链路交付平台
                                                         国际版多模型
```

**三条路径的本质差异**：

- **Claude Code 走"Harness 深度"**：不纠结 IDE 形态，把 Agent 运行时（子代理/钩子/后台任务/动态工作流）做到极致——**路径依赖：模型能力（Claude 4.x 长上下文/并行工具调用）是深度 Harness 的前提**
- **中国三厂走"场景广度"**：Trae 押注 Builder 低门槛 + 多端调度，Qoder 押注 Spec 驱动工程化，CodeBuddy 押注全链路交付——**共同短板：构成要素的"编排深度"（Subagent/Hooks/后台任务）落后一个身位**
- **关键判断**：当模型能力趋同（各家都能接入 GPT-5/Claude-4/Gemini/DeepSeek）时，**差异化将回到 Harness 深度与工作流工程化**——中国厂商从"接模型"到"建 Harness"是下一阶段胜负手

### 12.4 选型判断

| 场景 | 推荐 | 理由 |
|:-----|:-----|:-----|
| 深度编码 + 复杂重构 + 需要自动化（CI/测试） | Claude Code | Subagent/Hooks/后台任务完备度最高 |
| 快速原型 + 非专业开发者 + 多端调度 | Trae | Builder 门槛最低，Work 移动端调度 |
| 企业级规范开发 + 规格先行 | Qoder | Spec 工作流 + Repo Wiki 适合有规范的组织 |
| 腾讯生态 + 全流程交付 + 多模型切换 | CodeBuddy | 构思→发布闭环，国际版多模型 |
| 中文团队 + 合规要求 | Trae/Qoder/CodeBuddy | 数据本地化，Claude Code 需代理 |

---

## §13 结论

1. **Agent 的构成不是功能清单，而是层级架构**：概率性内核（LLM+Prompt）被确定性外壳（工具/Skill/编排/通道）包裹——**所有工程努力都指向"把不确定性限制在模型推理边界内"**。
2. **13 项构成要素中，Claude Code 提供了当前最完整的参考实现**：尤其 Subagent（上下文隔离）、Hooks（旁路调用）、Background Tasks（并行化）、Dynamic Workflows（编排）四项，是 2025-2026 年 Agent 工程成熟度的标志性能力。
3. **演进路标清晰**：运行时从 Harness → Loop → Workflow Runtime → Substrate；自进化从记忆 → 总结 → 复盘 → 梦境整理 → 自更新。方向是**上下文连续性、确定性外壳、记忆独立化、通道全形态、进化可治理**。
4. **编程四 Agent 的差距正在从"模型"转向"Harness"**：中国三厂（Trae/Qoder/CodeBuddy）在场景广度（多端/低门槛/全链路）上各有特色，但在构成要素的编排深度（子代理/钩子/后台任务）上仍与 Claude Code 有代差——**这是未来 1-2 年国产编程 Agent 的竞争焦点**。
5. **对基础设施的含义**：构成要素越完备（子代理/并行/后台/长上下文），对推理基础设施的"持久推理 + 高并发 + KV 分层"需求越强——与知识库 G3.5 分层存储、Long Horizon 150 迭代负载判断一致。

---

## 参考文献

1. [Claude Code 动态工作流深度分析](2026-06-26-claude-code-dynamic-workflows.md) — 知识库 03_AI/agent-engineering
2. [Agent Workflow Runtime 架构拆解](2026-06-26-agent-workflow-runtime-architecture.md) — 知识库
3. [Agent 工具链工程化：Skill 负责编排判断，CLI 稳定交付执行](2026-06-26-agent-toolchain-cli-execution.md) — 知识库
4. [Harness Agent 的 Memory 工程与纵深防御](2026-07-13-harness-agent-memory-defense-in-depth.md) — 知识库
5. [让 Agent 在对话中成长：自进化机制的五层实现](2026-06-26-agent-self-evolution-five-layers.md) — 知识库
6. [Agent OS：五种驯服不确定性的范式](2026-06-26-agent-os-five-paradigms.md) — 知识库
7. [Agent 编排范式深度技术分析](2026-08-03-agent-orchestration-paradigm-deep-analysis.md) — 知识库
8. [Agent 平台工程：设计模式与业界实践](2026-08-03-agent-platform-engineering-deep-analysis.md) — 知识库
9. [AI Agent 深度分析：定义、模式、产业与基础设施全景](2026-08-03-ai-agent-deep-analysis.md) — 知识库
10. [CowAgent Agent Harness 架构深度解读](../../05_tools/ai-tools/2026-08-03-cowagent-agent-harness-architecture-deep-analysis.md) — 知识库 05_tools
11. [PKM/RAG/Wiki/Memory 四类知识系统对比](05_tools/knowledge-management/2026-06-26-pkm-rag-wiki-memory-systems.md) — 知识库
12. Anthropic, [Claude Code Documentation](https://code.claude.com/docs)（特性：Subagents/Hooks/Background Tasks/MCP/Skills/CLAUDE.md）— 联网核实（2026-08）
13. Trae（字节跳动）官方：trae.cn / trae.ai — Builder 模式、TRAE Work、移动端（2026-08 抓取）
14. Qoder（阿里云）官方：qoder.com / qoder.cn / aliyun.com — Agent Mode/Quest Mode/Spec 工作流/Repo Wiki（2026-08 抓取）
15. CodeBuddy（腾讯云）官方：codebuddy.cn / codebuddy.ai — IDE+CLI、混元模型、国际版多模型（2026-08 抓取）
16. 菜鸟教程/CSDN/知乎公开资料：Trae/Qoder/CodeBuddy 教程与评测（2025-2026）

---

## 变更记录

| 日期 | 版本 | 变更 | 说明 |
|:-----|:-----|:-----|:-----|
| 2026-08-03 | v1.0 | 初稿 | 13 项构成要素逐一解剖（六层模型）+ Claude Code 特性补齐 + 演进路标 + 编程四 Agent 对比；整合知识库 11 篇专题 + 联网核实三厂公开资料 |
