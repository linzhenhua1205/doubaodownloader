# AI Agent 产品设计框架全景：SaaS→Agent 转型场景下的框架体系

> **类型**: 深度分析 | **日期**: 2026-08-19 | **版本**: v1.0
> **来源**: 网络一手（Anthropic《Building Effective Agents》全文 / OpenAI《A Practical Guide to Building Agents》PDF 全文 / Chip Huyen《Agents》AI Engineering 章节全文）+ 知识库姊妹篇（SaaS→AI 引擎 5 模式 / Agent 模式全谱系）+ import 素材（Agent 17 种架构模式 / AI 时代 ToB PMF）+ 经典产品框架（JTBD/HEART/UX 五要素等，公开知识 K）+ 本系统验证（CowAgent）
> **适用范围**: SaaS 产品 AI 化转型 / Agent 产品规划与设计 / 产品经理 AI 能力建设
> **姊妹篇**: [SaaS→AI 引擎 5 大转型模式](./2026-08-18-saas-to-ai-engine-five-transformation-modes.md)（架构视角）· [AI Agent 模式全谱系](./2026-08-18-ai-agent-patterns-taxonomy-methodology-deep-analysis.md)（工程视角）
> **相关**: [Doubao→Agent 实现机制](../agent-engineering/2026-08-14-doubao-to-agent-implementation-mechanism-deep-analysis.md) · [三退化模式](../agent-engineering/2026-08-17-agent-degeneration-modes-harness-architecture-deep-analysis.md) · [AI 产出毛利 vs 净利](./2026-08-05-ai-output-gross-vs-net-entropy.md)

---

## 📑 目录 (TOC)

- [§0 执行摘要](#§0-执行摘要)
- [§1 问题定位：产品设计框架 ≠ 架构转型模式 ≠ 工程模式](#§1-问题定位产品设计框架--架构转型模式--工程模式)
- [§2 第一类：通用产品设计框架的 Agent 适配](#§2-第一类通用产品设计框架的-agent-适配)
- [§3 第二类：AI Agent 原生设计框架（6 个）](#§3-第二类ai-agent-原生设计框架6-个)
- [§4 第三类：SaaS→Agent 转型专属设计框架（6 个）](#§4-第三类saasagent-转型专属设计框架6-个)
- [§5 框架整合：三层框架的配合逻辑与产品设计流程](#§5-框架整合三层框架的配合逻辑与产品设计流程)
- [§6 案例验证](#§6-案例验证)
- [§7 本系统验证：CowAgent 的产品设计映射](#§7-本系统验证cowagent-的产品设计映射)
- [§8 第一性原理：SaaS→Agent 产品设计的四个本质转变](#§8-第一性原理saasagent-产品设计的四个本质转变)
- [§9 结论与建议](#§9-结论与建议)
- [参考资料](#参考资料)
- [素材边界声明](#素材边界声明)
- [Changelog](#changelog)

---

## §0 执行摘要

**SaaS→Agent 转型中，产品设计框架要回答的不是"AI 放系统第几层"（那是架构问题），也不是"Agent 内部怎么编排"（那是工程问题），而是五个产品问题：做什么任务、怎么交互、能力边界在哪、怎么评测迭代、怎么变现。** 本文把散落在各处的框架体系化整理为三层共 17 个框架：

1. **第一层·通用框架适配（5 个）**：JTBD、HEART、UX 五要素、Double Diamond/设计冲刺、Hooked——经典产品框架没有失效，但设计对象从"界面+流程"变成"行为边界+成果"，每个框架都需要 Agent 化改造。

2. **第二层·AI Agent 原生框架（6 个）**：Anthropic（Workflows vs Agents，5 工作流模式 + 3 原则 + ACI）、OpenAI（Model/Tools/Instructions 三组件 + 编排 + 7 类 Guardrails + HITL）、Chip Huyen（工具三分类 + 规划解耦 + 失效模式 + 评估法）、Google（Model+Tools+Orchestration 认知架构）、Microsoft（AI 设计原则/HAX 人机交互指南）、import 素材 17 种架构模式（6 评估维度 + Agent 设计公式）。

3. **第三层·转型专属框架（6 个）**：交互范式迁移（表单→对话→安静任务）、存量资产映射（工作流→工具集/数据→知识库/权限→护栏/文档→指令）、信任设计（透明/可解释/降级/HITL）、护栏设计（权限边界/操作白名单/审批流/成本护栏）、评测设计（evals-first：回归集/黄金集/生产遥测）、商业模式设计（席位→用量/成果，规避 Vibe Revenue 陷阱）。

**核心判断**：SaaS→Agent 产品设计的本质是**从"设计界面"到"设计行为边界 + 评测"**——产品经理的产出物从 PRD（页面/功能规格，确定性）变为 Agent Spec（任务目标/工具集/护栏/评测集，概率性）。三层框架的配合逻辑是：**通用框架找任务（为什么做）→ 原生框架定能力形态（做什么）→ 转型框架做迁移（怎么迁）→ evals 迭代（怎么验）**。

---

## §1 问题定位：产品设计框架 ≠ 架构转型模式 ≠ 工程模式

### 1.1 三个视角的 MECE 区分

知识库已有两篇姊妹篇分别覆盖"架构"与"工程"视角，本文补充"产品设计"视角，三者互斥且互补：

| 视角 | 核心问题 | 产出物 | 决策者 | 已有/本文文档 |
|:-----|:---------|:-------|:-------|:-------------|
| **架构转型模式** | AI 处在系统第几层？存量系统怎么迁移？ | 迁移路线图（模式二→四） | 架构师/CTO | [08-18 五模式](./2026-08-18-saas-to-ai-engine-five-transformation-modes.md) |
| **工程模式** | Agent 内部怎么组织？用哪个编排模式？ | 技术选型（ReAct/Orchestrator/MemGPT…） | 工程师 | [08-18 模式全谱系](./2026-08-18-ai-agent-patterns-taxonomy-methodology-deep-analysis.md) |
| **产品设计框架** | 做什么任务？怎么交互？边界在哪？怎么评测？怎么赚钱？ | 产品规格（Agent Spec） | 产品经理 | **本文** |

### 1.2 产品设计框架要回答的 5 个问题（MECE）

| # | 产品问题 | 对应框架层 | 典型框架 |
|:-:|:---------|:-----------|:---------|
| 1 | 做什么任务（价值定义） | 通用 | JTBD、Double Diamond |
| 2 | 怎么交互（体验定义） | 通用 + 转型 | UX 五要素、交互范式迁移 |
| 3 | 能力边界在哪（安全/信任） | 原生 + 转型 | OpenAI Guardrails、信任设计、护栏设计 |
| 4 | 怎么评测迭代（质量闭环） | 原生 + 转型 | Chip Huyen 评估法、Evals-first |
| 5 | 怎么变现（商业模式） | 转型 | 席位→成果计费、Vibe Revenue 规避 |

### 1.3 为什么 SaaS→Agent 场景尤其需要产品设计框架

**SaaS 的产品设计有 40 年成熟方法论（表单/菜单/工作流/权限），Agent 产品没有**——Agent 的行为是概率性的、边界是模糊的、失败是复合的 [来源: Chip Huyen《Agents》]。Chip Huyen 明确说："AI-powered agents are an emerging field with no established theoretical frameworks"——这正是需要把散落框架体系化的原因。而 SaaS→Agent 场景叠加了**存量资产复用**（数据/工作流/权限/品牌）与**转型路径约束**（不能一步到位），比绿地 Agent 产品多一层设计复杂度。

---

## §2 第一类：通用产品设计框架的 Agent 适配

> 经典框架本体为公开知识（K），本文只做"Agent 场景适配"分析——**每个框架的适配点都是同一个：设计对象从"界面+流程"变为"行为边界+成果"**。

### 2.1 JTBD（Jobs-to-be-Done）— 从"功能"到"成果"

**核心逻辑**：用户"雇佣"产品完成一个 Job，而非购买功能 [来源: K]。
**SaaS 时代**：JTBD 帮助定位"用户在什么场景下要完成什么任务"，落地为功能清单（feature list）。
**Agent 场景适配**：

- **任务定义升级**：Agent 场景下 Job 必须包含 **目标 + 约束 + 验收标准** 三要素 [来源: Chip Huyen《Agents》："A task is defined by its goal and constraints"]——因为 Agent 是自主执行，约束和验收标准必须前置编码，否则无法判断任务是否完成。
- **成果导向**：SaaS 卖"完成任务的工具"，Agent 卖"任务完成的成果"。JTBD 访谈要问的不是"你用什么功能"，而是"**你希望什么结果自动发生**"——这直接决定 Agent 的任务边界。
- **任务挖掘矩阵**（SaaS→Agent 选任务）：

| 维度 | 适合 Agent 化 | 不适合 |
|:-----|:-------------|:-------|
| 决策复杂度 | 需要判断/异常处理（退款审批） | 固定流程可规则化 |
| 规则可维护性 | 规则集庞大难维护（安全审查） | 简单规则（if-then） |
| 数据结构 | 重度非结构化（文档/对话） | 纯结构化 CRUD [来源: OpenAI 实用指南] |

### 2.2 HEART — 度量体系新增 4 个 Agent 维度

**核心逻辑**：Happiness/Engagement/Adoption/Retention/Task Success 五维度量体验 [来源: K]。
**Agent 场景适配**：五维仍有效，但**Task Success 被大幅强化**，并新增 4 个 Agent 特有维度：

| 新增维度 | 定义 | 度量指标 |
|:---------|:-----|:---------|
| **任务成功率** | Agent 独立完成任务的比例 | 端到端成功率、首次尝试成功率 |
| **自主度** | Agent 自主完成 vs 需人工介入 | 人工介入率（每任务介入次数） |
| **信任度** | 用户对 Agent 输出的采信程度 | 修改率（用户改写 Agent 产出）、降级请求率 |
| **成本效率** | 单位成果的资源消耗 | $/任务、token/任务、步骤/任务 [来源: Chip Huyen] |

> 关键洞察：**SaaS 的 Engagement 是"用户花更多时间"，Agent 的 Engagement 是"用户花更少时间"**——Agent 成功的标志是用户越来越不需要参与。度量哲学从"黏性"转向"解放"。

### 2.3 UX 五要素 — 每一层都被 Agent 重定义

**核心逻辑**：战略→范围→结构→框架→表现五层由抽象到具体 [来源: K]。
**Agent 场景适配**：

| 层 | SaaS 时代 | Agent 时代 |
|:---|:----------|:-----------|
| 战略层 | 产品定位 | **任务边界**（哪些 Job 由 Agent 做，哪些留给用户） |
| 范围层 | 功能清单 | **工具集 + 知识库 + 权限范围** |
| 结构层 | 信息架构/导航 | **编排与控制流**（单 Agent 循环/多 Agent 图） |
| 框架层 | 页面布局/组件 | **对话 + 任务面板 + 结果视图**（多形态外壳） |
| 表现层 | 视觉设计 | **透明度呈现**（计划展示/推理过程/置信度） |

### 2.4 Double Diamond / 设计冲刺 — "发现"阶段变成任务挖掘

**核心逻辑**：发散-收敛-发散-收敛四阶段 [来源: K]。
**Agent 场景适配**：第一个菱形（发现问题）在 Agent 场景的成本急剧上升——**问题空间从"用户痛点"扩展为"任务 + 约束 + 失败模式"三维空间**。设计冲刺的产出从"原型（页面）"变为"**原型（Agent + 评测集）**"——用最小 Agent + 20 条黄金测试用例验证可行性，比做 UI mockup 更有说服力 [来源: OpenAI 实用指南"Start small, validate with real users"]。

### 2.5 Hooked — 从"习惯养成"到"依赖卸载"

**核心逻辑**：Trigger→Action→Reward→Investment 循环养成习惯 [来源: K]。
**Agent 场景适配**：**Agent 产品的 Hooked 是反过来的——用户的 Investment 是"把任务委托给 Agent"，Reward 是"省下的时间"**。触发（Trigger）从"用户想起用产品"变为"**Agent 主动触发**"（事件/定时/上下文感知，即安静模式）——这正好对应知识库 5 模式中的"双模式运行" [来源: 姊妹篇 08-18]。产品设计要考虑的不是"怎么让用户多用"，而是"怎么让用户放心委托更多"——**信任是 Agent 的 Hook**。

---

## §3 第二类：AI Agent 原生设计框架（6 个）

### 3.1 Anthropic《Building Effective Agents》(2024-12) — 最经典的产品形态框架

> 一手全文抓取 [来源: C1]

**核心贡献**：首次把 agentic system 划分为 **Workflows（预定义代码路径）vs Agents（LLM 动态主导）**，并给出 5 种工作流模式 + 自主 Agent：

| 模式 | 机制 | 适用场景 |
|:-----|:-----|:---------|
| Prompt Chaining | 任务分解为固定步骤序列，中间可加 gate | 可干净分解的固定子任务（写大纲→检查→成文） |
| Routing | 分类输入→路由到专用 prompt/模型 | 客服问题分流；简单问题用小模型省钱 |
| Parallelization | Sectioning（拆子任务并行）/ Voting（同任务多跑投票） | 多维度评估；代码安全审查 |
| Orchestrator-Workers | 中央 LLM 动态拆解委派，子任务不可预定义 | 编码（文件改动量取决于任务）；多源搜索 |
| Evaluator-Optimizer | 生成 LLM + 评估 LLM 循环迭代 | 有明确评估标准且迭代有收益（翻译润色） |
| Autonomous Agent | LLM 基于环境反馈自主循环 | 开放问题，步骤不可预测，需信任决策 |

**3 条产品设计原则** [来源: C1]：

1. **Simplicity（保持简单）**：先单 LLM 调用 + retrieval，再逐步加复杂度——"考虑复杂度只在它可证明提升产出时增加"。
2. **Transparency（透明）**：明确展示 Agent 的规划步骤——**这是产品信任设计的起点**。
3. **精心设计 ACI（Agent-Computer Interface）**：工具定义要像 HCI 一样投入——"想想我们投入多少精力在 HCI，就该在 ACI 投入多少"。案例：SWE-bench agent 把相对路径工具改为强制绝对路径（poka-yoke）后模型零失误 [来源: C1]。

**产品设计启示**：这 5+1 模式本质是**"产品复杂度阶梯"**——从 workflow 到 agent 的每一步都是产品决策（可预测性 vs 灵活性、成本 vs 能力），不是纯技术选型。

### 3.2 OpenAI《A Practical Guide to Building Agents》(2025) — 最实操的工程产品框架

> 一手 PDF 全文抓取，已存 tmp/260f6048_a-practical-guide-to-building-agents.pdf [来源: C2]

**三组件定义**（Agent = Model + Tools + Instructions）：

| 组件 | 内容 | 产品设计含义 |
|:-----|:-----|:-------------|
| Model | LLM 推理决策 | 选型原则：先强大模型建性能基线→再换小模型优化成本延迟 |
| Tools | 外部函数/API | 三类：**Data**（取上下文）/ **Action**（写操作）/ **Orchestration**（Agent 当工具） |
| Instructions | 行为指南 + Guardrails | 用现有 SOP/帮助文档生成指令；拆解任务为小步骤；定义明确动作；捕获边界情况 |

**何时该建 Agent**（产品机会筛选）：复杂决策（退款审批）/ 难维护规则集（安全审查）/ 重度非结构化数据（保险理赔）[来源: C2]。

**编排模式**：单 Agent（while loop + exit conditions）→ 多 Agent（Manager 模式：中央 Agent 以 tool call 委派；Decentralized 模式：Agent 间 handoff 转移控制权）。**产品指导原则**：先最大化单 Agent 能力，工具相似性 > 数量是拆分多 Agent 的信号（>15 个清晰工具 OK，<10 个重叠工具就应拆分）[来源: C2]。

**Guardrails 体系（7 类）** [来源: C2]：

| 类型 | 机制 |
|:-----|:-----|
| Relevance classifier | 拦截离题输入 |
| Safety classifier | 检测越狱/提示注入 |
| PII filter | 输出 PII 审查 |
| Moderation | 有害内容过滤 |
| **Tool safeguards** | **按工具风险分级（low/med/high：只读 vs 写、可逆性、财务影响），高风险触发暂停/人工升级** |
| Rules-based | 黑名单/正则/长度限制 |
| Output validation | 品牌一致性校验 |

**Human-in-the-loop 两个触发条件**：① 超过失败阈值（重试次数上限）；② 高风险动作（不可逆/高影响：取消订单、大额退款、支付）[来源: C2]。

### 3.3 Chip Huyen《Agents》(2025-01) — 最完整的原理-失效-评估框架

> 一手全文抓取（AI Engineering 书章节）[来源: C3]

**工具三分类**（决定 Agent 能力边界）：

| 类别 | 作用 | 示例 |
|:-----|:-----|:-----|
| Knowledge augmentation | 上下文构建 | 文本/图片检索、SQL 查询、Web 搜索 |
| Capability extension | 补模型短板 | 计算器、代码解释器、翻译、日历 |
| Write actions | 对环境产生实际影响 | 发邮件、更新数据库、转账 |

**规划方法论**：**规划与执行解耦**——先生成计划→验证（启发式/AI judge）→执行→反思，避免无效执行烧 token [来源: C3]。规划粒度分层（高层计划→子计划），自然语言计划比函数名计划更鲁棒。

**Agent 失效模式分类**（产品评测设计的理论基础）[来源: C3]：

| 失效类别 | 具体模式 |
|:---------|:---------|
| Planning failures | 无效工具 / 有效工具-无效参数 / 有效工具-错误参数值 / 目标失败（没达成目标或违反约束）/ **反思错误（以为完成实际没完成）** |
| Tool failures | 工具本身输出错误 / 翻译层错误 / 缺工具（该有而没有） |
| Efficiency | 步骤过多 / 成本过高 / 单步过慢 |

**评估方法**：识别失效模式 → 测量每个失效模式的频率 → 与基线（其他 agent 或人类操作员）对比。注意**人机效率基准不可直接类比**（人类访 100 页网页不现实，Agent 一次可并行）[来源: C3]。

### 3.4 Google《Agents》(2025) — 认知架构三要素

> 公开知识 [来源: K]（Google Cloud "Agents" 课程/Kaggle 课程）

**核心框架**：Agent = **Model（LLM 推理）+ Tools（外部行动）+ Orchestration Layer（认知架构）**。Orchestration layer 决定：Agent 循环（单 Agent 反思循环）、多 Agent 编排、记忆（短期上下文/长期存储）、规划（思维链/ReAct 等）[来源: K]。

**产品设计启示**：三要素框架是**"最小可设计单元"**——产品经理可以把任何 Agent 需求拆成"模型选择/工具清单/编排方式"三张表来评审，与 OpenAI 三组件（Model/Tools/Instructions）互为印证。

### 3.5 Microsoft — AI 设计原则与 HAX 人机交互指南

> 公开知识 [来源: K]（Microsoft AI 设计指南 + 微软研究院 Guidelines for Human-AI Interaction）

**核心框架**：

- **AI 设计 6 原则**：公平、可靠与安全、隐私与安全、包容、透明、问责 [来源: K]。
- **HAX（Human-AI eXperience）18 条指南**（微软研究院 2019），对 Agent 产品最相关的 5 条：

| HAX 指南 | 产品设计落地 |
|:---------|:------------|
| 让用户知道系统能做什么/不能做什么 | 能力边界明示（onboarding 告知任务范围） |
| 展示系统正在做什么/为什么 | 计划展示 + 推理过程透明（与 Anthropic transparency 一致） |
| 遵循用户最近的行动（可撤销） | Undo/回滚机制 |
| 澄清误解（支持"更正"） | 对话纠错 + 重新规划入口 |
| 高效降级（明确把控制权还给人类） | 失败时优雅移交人工 [来源: K] |

**产品设计启示**：Microsoft 框架是**"信任设计的操作手册"**——SaaS 的信任来自功能确定性，Agent 的信任必须靠设计显式构建。

### 3.6 import 素材：17 种架构模式的 6 评估维度 + 设计公式

> import 素材（cnblogs，素材级，批判使用）[来源: M1]

**6 个设计目标维度**（评估维度，定义优化目标）：推理质量 / 控制流 / 安全与信任 / 任务分解与协作 / 记忆与状态 / 可观测性与评估。

**Agent 设计公式**（设计变量，定义搜索空间）[来源: M1]：

```text
Agent = State x Topology(Routing) x Guards x Sum(Plugins via Hooks) x Tools(ACI) @ Mode
```

- State: 系统快照（对话历史/中间结果/记忆/任务队列）
- Topology: 连接结构（线性链/循环/分叉-汇聚/树/网格）
- Guards: 安全闸门
- Plugins via Hooks: 生命周期扩展
- Tools(ACI): 工具接口
- Mode: 执行模式（对话/安静）

**产品设计启示**：该公式把"Agent 能力"拆成 6 个正交设计变量——产品评审时可以逐项检查"我们的 Agent 状态管理/控制流/护栏/扩展/工具/模式是否都有明确设计"，与 OpenAI 三组件互补。

### 3.7 原生框架对比矩阵

| 框架 | 核心组件 | 侧重 | 产品设计贡献 | 来源 |
|:-----|:---------|:-----|:-------------|:-----|
| Anthropic 5+1 模式 | Workflow vs Agent | 复杂度阶梯 | 产品形态选择（可预测 vs 灵活） | C1 |
| OpenAI 三组件 | Model/Tools/Instructions | 工程落地 | 能力边界 + Guardrails + HITL | C2 |
| Chip Huyen | Tools/Planning/Reflection | 原理与失效 | 失效模式 + 评估方法 | C3 |
| Google | Model/Tools/Orchestration | 认知架构 | 最小可设计单元 | K |
| Microsoft | 6 原则 + HAX | 信任 | 信任设计操作手册 | K |
| 17 模式 6 维度 | State×Topology×Guards×… | 设计空间 | 设计变量检查清单 | M1 |

---

## §4 第三类：SaaS→Agent 转型专属设计框架（6 个）

> 这是本文的核心增量——前两类框架对绿地 Agent 同样适用，第三类只针对"存量 SaaS 转 Agent"。

### 4.1 交互范式迁移框架：表单 → 对话 → 安静任务（三态模型）

**SaaS 的交互是"显式操作"（填表单/点菜单/拖流程），Agent 的交互是"意图委托"** [来源: 姊妹篇 08-18]。产品设计要规划三态共存与切换：

| 状态 | 用户角色 | 触发方式 | 产品设计要点 |
|:-----|:---------|:---------|:-------------|
| 表单态（保留） | 操作者 | 手动 | 兼容存量用户；作为降级路径 |
| 对话态（新增） | 对话者 | 自然语言 | 意图解析 + 澄清 + 计划确认（Anthropic transparency） |
| 安静态（新增） | 委托者 | 事件/定时/webhook | **无人工反馈回路→护栏必须更强**（开环控制）[来源: 姊妹篇公理二] |

**设计要点**：三种状态共用一套任务内核（一套内核双模式），UI 只是适配器——避免维护两套逻辑 [来源: 姊妹篇 08-18 通用原则 2]。

### 4.2 存量资产映射框架：5 类资产的 Agent 化改造

SaaS 转 Agent 最大的优势是存量资产，映射框架如下：

| 存量资产 | Agent 化映射 | 设计动作 | 参考 |
|:---------|:-------------|:---------|:-----|
| 工作流/业务流程 | 工具集（原子化 API） | 把流程拆为原子动作，包装成 Agent 友好工具 | OpenAI 工具三分类；Anthropic ACI |
| 业务数据 | 知识库/RAG | 建立检索索引 + 权限隔离（防越权泄露） | Chip Huyen knowledge augmentation |
| 权限模型 | 护栏/授权边界 | RBAC 映射为工具风险分级 + 操作白名单 | OpenAI Tool safeguards |
| UI/流程文档 | Agent 指令 | 用现有 SOP/帮助文档生成指令（OpenAI 推荐用文档生成 instruction） | OpenAI Instructions |
| 品牌/信任资产 | 输出风格 + 透明度 | 品牌语气约束（output validation）+ 计划展示 | OpenAI Output validation |

**关键风险**：存量 API 为"人"设计，缺 Agent 友好的参数补全/异常/幂等/事务——**老接口直接暴露给 Agent 容易击穿权限与事务边界** [来源: 姊妹篇 08-18 模式二判性]。

### 4.3 信任设计框架：概率性系统的信任构建

**SaaS 信任来自"功能符合预期"，Agent 信任必须显式设计**（Chip Huyen：不应给不可靠 AI 转账权限，就像不给实习生删生产库权限 [来源: C3]）。五要素：

| 要素 | 设计动作 | 参考 |
|:-----|:---------|:-----|
| 透明 | 展示计划/推理/工具调用（不只给结果） | Anthropic 原则 2；HAX 指南 |
| 可解释 | 输出附依据（引用数据源/推理链） | RAG 引用；本系统"断言有出处" |
| 可控 | 用户随时接管/纠正/撤销 | HAX 指南 3；HITL checkpoint |
| 可预期失败 | 明确"什么时候会失败、失败后怎么办" | OpenAI HITL 两触发 |
| 可审计 | 完整操作日志 + 回放 | 本系统 conversation-log/ |

### 4.4 护栏设计框架：四层护栏模型

结合 OpenAI 7 类 Guardrails [来源: C2] 与本系统实践，按"输入→决策→执行→输出"四层组织：

```text
+------------------+  L1 Input Guard:  relevance/safety/PII/moderation/rules-based
|   Input Layer    |     (reject off-topic, jailbreak, injection)
+------------------+
|  Decision Layer  |  L2 Scope Guard:  task boundary / tool whitelist / instruction
+------------------+
|  Execution Layer |  L3 Action Guard: risk-rated tools (read-only vs write,
|                  |     reversibility, financial impact) + approval flow
+------------------+
|   Output Layer   |  L4 Output Guard: format validation / brand tone / PII
+------------------+
```

**产品设计要点**：护栏分级投入——**只读操作轻护栏，写操作/不可逆操作必须审批流**；护栏是产品特性而非技术细节，要进 PRD [来源: C2]。

### 4.5 评测设计框架：Evals-first（Agent 的产品规格 = 评测集）

**这是 SaaS→Agent 产品设计最大的范式转变**：

| SaaS 产品规格 | Agent 产品规格 |
|:--------------|:---------------|
| PRD：页面/功能/流程描述 | Agent Spec：任务目标 + 工具集 + 护栏 + 评测集 |
| 验收=功能是否符合描述（确定性） | 验收=评测集通过率 + 护栏零突破（概率性） |
| Bug=代码缺陷 | 缺陷=失效模式（规划/工具/效率三类）[来源: C3] |

**三层评测体系**：

| 层 | 内容 | 用途 |
|:---|:-----|:-----|
| 回归集 | 历史真实任务 + 已知失败案例 | 防退化（每次改动跑） |
| 黄金集 | 人工标注的高质量任务-预期路径 | 能力基线/模型选型对比 |
| 生产遥测 | 工具调用日志/成功率/人工介入率/成本 | 持续监控 + 新用例回流 [来源: C3] |

**产品设计启示**：Agent 产品经理的日常产出从"画原型"变为"**写评测用例 + 分析失效模式**"——评测集是 Agent 产品的"需求文档"。

### 4.6 商业模式设计框架：从席位到成果 + Vibe Revenue 规避

**SaaS 商业模式**：按席位/功能分层订阅，价值=软件使用权。
**Agent 商业模式**：按用量/成果计费——Anthropic 观察到客服 Agent 公司"usage-based pricing models that charge only for successful resolutions"（只为成功解决计费）[来源: C1]。

**转型设计要点**：

1. **计费锚点迁移**：席位→API 用量→成果（每成功任务/每解决工单）。成果计费是 Agent 自信的信号，也倒逼产品质量。
2. **Vibe Revenue 陷阱**（import 素材，素材级）[来源: M2]：AI Agent 创业的"PMF 幻觉"= FOMO 预算 + 好奇心预算 + AI 焦虑税三笔预算叠加，表现为"决策快、客单价不低、可复制"——**但续费率会说话**。产品设计要防的是"为 AI 而 AI"的任务，用 §2.1 任务挖掘矩阵过滤。
3. **agent-to-agent commerce**：未来 Agent 之间直接交易（采购/结算），产品需要 API 优先 + 机器可读的 SLA/护栏契约 [来源: 前瞻判断，标注为推断]。

---

## §5 框架整合：三层框架的配合逻辑与产品设计流程

### 5.1 三层框架的分工

| 层 | 回答的问题 | 框架 | 输出 |
|:---|:-----------|:-----|:-----|
| L1 通用层 | 为什么做（任务与价值） | JTBD/HEART/UX 五要素/DD/Hooked | 任务清单 + 度量指标 |
| L2 原生层 | 做什么形态（Agent 能力） | Anthropic/OpenAI/Chip Huyen/Google/MS/17 模式 | Agent 形态 + 能力边界 + 评测方法 |
| L3 转型层 | 怎么迁（存量复用与边界） | 交互迁移/资产映射/信任/护栏/评测/商业模式 | 迁移路线 + Agent Spec |

### 5.2 从 PRD 到 Agent Spec 的产品设计流程（六步）

| 步骤 | 框架层 | 动作 | 输出 |
|:-----|:------:|:-----|:-----|
| Step1 任务挖掘 | L1 | JTBD 访谈 + 任务挖掘矩阵 | 候选任务清单 |
| Step2 形态选择 | L2 | Anthropic 复杂度阶梯 | workflow or agent |
| Step3 能力设计 | L2 | OpenAI 三组件 | Model/Tools/Instructions 三张表 |
| Step4 迁移规划 | L3 | 资产映射 + 交互三态 | 存量改造清单 |
| Step5 边界设计 | L3 | 四层护栏 + 信任五要素 | 权限/审批/降级方案 |
| Step6 评测闭环 | L3 | evals-first 三层体系 | 回归集/黄金集/生产遥测 |

### 5.3 关键决策树（SaaS→Agent 选型）

```text
Can the task be solved by rules?
|-- Yes ---------------------> No agent needed (rules/workflow suffice)
`-- No
    |-- Subtasks predefined? --> Workflow (Chaining/Routing/Parallelization)
    `-- Not predefined ------> Agent (Orchestrator / Autonomous)
        |-- Legacy API agent-friendly? --> Wrap as tools
        `-- No ---------------------> Refactor API or use computer-use
            |-- High risk / irreversible? --> Approval flow + HITL
            `-- Low risk / reversible? --> Optimistic execution + audit log
```

---

## §6 案例验证

### 6.1 Salesforce Agentforce — 三层框架的完整印证

> 来源: 知识库姊妹篇 08-18 已抓取的官方架构 [来源: 姊妹篇 C1]

| 框架层 | Agentforce 对应 | 印证 |
|:-------|:----------------|:-----|
| JTBD | 六大预设 Agent 类型（Service/SDR/Sales Coach/Merchandiser/Buyer/Campaign Optimizer）= 任务建模 | 任务先于功能 |
| Anthropic | Atlas Reasoning Engine（拆子任务+动态编排）= Orchestrator-Workers | 5+1 模式产品化 |
| OpenAI | Agent Builder + Agent Script + Observability = Build-Run-Scale 生命周期 | 三组件 + 护栏 + 观测 |
| 信任 | 超范围升级人工（escalate to human agents） | HITL 落地 |
| 商业模式 | 18K+ 公司、按成果计费信号 | 成果导向定价 |

### 6.2 Intercom Fin — 工具代理模式的客服 Agent

> 公开知识 [来源: K]（姊妹篇 08-18 已引用）

- 把客服工作流 API 包装为工具，Agent 调用旧系统处理工单/知识检索/转人工——**资产映射框架（工作流→工具集）的典型落地** [来源: 姊妹篇]。
- HITL：复杂问题升级人工——**信任设计的降级路径**。

### 6.3 反模式：加聊天框伪转型 + Vibe Revenue

- "加聊天框 ≠ AI 引擎化"是姊妹篇第一命题 [来源: 姊妹篇]——产品层面即**交互范式没迁移**（停留在对话态，无安静态、无工具调用）。
- Vibe Revenue：签单快≠PMF，续费率才是 [来源: M2]——商业模式层没把"成果"做实。

---

## §7 本系统验证：CowAgent 的产品设计映射

**CowAgent 本身就是"AI 引擎化 + Agent 产品设计"的活体实证**（姊妹篇已证架构层面=模式四），本文补充产品设计层面映射：

| 产品设计框架 | CowAgent 对应实现 | 验证结论 |
|:-------------|:------------------|:---------|
| JTBD（任务定义=目标+约束+验收） | "深度分析"指令 = 目标 + 铁律约束 + 落盘/commit 验收 | ✅ 任务三要素前置 |
| Anthropic 复杂度阶梯 | 简单问答直接答；深度分析走流水线；调研走 runner 分档 | ✅ 复杂度匹配 |
| Anthropic Transparency | 执行前同步计划/关键步骤告知用户 | ✅ 计划透明 |
| OpenAI 三组件 | 工具集（20+ tools+skills）= Tools；AGENT.md/RULE.md = Instructions；模型=Model | ✅ 三组件齐备 |
| 四层护栏 | L1 输入：意图路由；L3 执行：铁律（永不 rm/改前查标记/破坏性先问）；L4 输出：doc-final-check 门禁 | ✅ 护栏分层 |
| Evals-first | doc-final-check + 日报复盘 + conversation-log 审计 = 回归+遥测 | ✅ 评测闭环 |
| 资产映射 | 知识库（存量数据）→ RAG 事实约束；技能系统 → 工具集；RULE.md → 指令 | ✅ 存量复用 |
| 商业模式 | 个人效率工具（非市场化）——但"成果导向"体现在每次输出=落盘+可复用 | ✅ 成果沉淀 |

**关键洞察**：本系统没有经过"产品设计"流程却天然符合全部框架——因为**框架是从有效实践中提炼的规律，而非先验教条**。这反过来验证了本文框架体系的合理性。

---

## §8 第一性原理：SaaS→Agent 产品设计的四个本质转变

### 8.1 设计对象：从"界面"到"行为边界"（博弈论）

SaaS 产品经理设计的是**界面（用户的操作路径）**；Agent 产品经理设计的是**行为边界（Agent 在什么约束下自主行动）**。本质是**委托-代理关系设计**——用户是委托人，Agent 是代理人，产品设计 = 设计委托契约（任务目标 + 约束 + 奖惩/验收）。这与知识库 08-18 模式谱系的"博弈论透镜"同构 [来源: 姊妹篇谱系]。

### 8.2 产品规格：从"PRD"到"Evals"（信息论）

SaaS 的规格是**确定性编码**（页面长什么样、流程怎么走）；Agent 的行为无法确定性编码，只能编码**验收标准**（评测集 + 护栏）。这是率失真定理的产品层表达——**无法精确传输 Agent 行为，只能传输"可接受行为"的约束** [来源: 姊妹篇谱系信息论透镜]。

### 8.3 信任机制：从"确定性"到"概率性"（控制论）

SaaS 的信任=功能确定（点按钮必然触发）；Agent 的信任=**失败可预期 + 可恢复**（闭环控制：观察→反馈→修正；安静模式=开环，需要更强前馈约束）[来源: 姊妹篇公理二]。

### 8.4 价值锚点：从"功能"到"成果"（经济学）

用户为 SaaS 付"使用费"，为 Agent 付"成果费"（successful resolutions only [来源: C1]）。产品设计必须回答：**每个 Agent 任务能否量化成果**——不能量化成果的任务不适合 Agent 化（Vibe Revenue 的根源就是任务成果不可量化 [来源: M2]）。

---

## §9 结论与建议

### 9.1 框架体系总览（本文核心交付）

**SaaS→Agent 产品设计框架 = 3 层 17 个框架**：

| 层 | 框架 | 用途 |
|:---|:-----|:-----|
| L1 通用适配 | JTBD / HEART / UX 五要素 / Double Diamond / Hooked | 找任务、定度量 |
| L2 AI 原生 | Anthropic 5+1 / OpenAI 三组件 / Chip Huyen 失效法 / Google 认知架构 / Microsoft HAX / 17 模式 6 维度 | 定能力形态 |
| L3 转型专属 | 交互三态 / 资产映射 / 信任五要素 / 四层护栏 / Evals-first / 成果商业模式 | 做迁移、立边界 |

### 9.2 落地建议

1. **产品经理转型**：从"画原型"到"写评测用例 + 设计护栏"——Agent 产品经理的核心技能是任务建模与失效模式分析。
2. **转型路径**：JTBD 找 3-5 个高价值任务 → Anthropic 阶梯选形态 → OpenAI 三组件出 Agent Spec → 四层护栏 + evals 三层体系 → 成果计费验证。
3. **避免三个陷阱**：加聊天框伪转型（交互未迁移）/ Vibe Revenue 幻觉（成果不可量化）/ 老 API 直接暴露（缺 Agent 友好改造）。
4. **与架构决策联动**：产品设计框架（本文）选择的任务边界，直接影响架构转型模式（姊妹篇）的推进节奏——**产品先定任务，架构再定层级**。

---

## 参考资料

[1] Anthropic —《Building Effective Agents》官方工程博客（2024-12-19，全文抓取）：https://www.anthropic.com/engineering/building-effective-agents [来源: C1]

[2] OpenAI —《A Practical Guide to Building Agents》官方 PDF（2025，全文抓取，已存 tmp/260f6048_a-practical-guide-to-building-agents.pdf）[来源: C2]

[3] Chip Huyen —《Agents》（AI Engineering 书章节，2025-01-07，全文抓取）：https://huyenchip.com/2025/01/07/agents.html [来源: C3]

[4] 知识库姊妹篇 —《SaaS→AI 引擎：5 大转型模式》（2026-08-18）：./2026-08-18-saas-to-ai-engine-five-transformation-modes.md [来源: 姊妹篇]

[5] 知识库姊妹篇 —《AI Agent 模式全谱系》（2026-08-18）：./2026-08-18-ai-agent-patterns-taxonomy-methodology-deep-analysis.md [来源: 姊妹篇]

[6] import 素材 —《Agent 17 种架构模式 分析 & 思考》（cnblogs，素材级批判使用）[来源: M1]

[7] import 素材 —《AI 时代的 ToB PMF，还成立吗？》（cnblogs，素材级批判使用）[来源: M2]

[8] Google —《Agents》课程/认知架构定义（公开知识）[来源: K]

[9] Microsoft — AI 设计原则 + 微软研究院 HAX（Guidelines for Human-AI Interaction，公开知识）[来源: K]

[10] JTBD / HEART / UX 五要素 / Double Diamond / 设计冲刺 / Hooked（经典产品框架，公开知识）[来源: K]

## 素材边界声明

- **一手（C1/C2/C3）**：Anthropic 博客全文（web_fetch 抓取）；OpenAI 官方 PDF 全文（34 页下载解析）；Chip Huyen 博客全文（web_fetch 抓取）。
- **知识库姊妹篇**：SaaS→AI 引擎 5 模式 / Agent 模式全谱系（2026-08-18 已归档，其一手来源为豆包对话 + Salesforce 官方页）。
- **import 素材（M1/M2）**：cnblogs 两篇文章，素材级批判使用——M1 的 17 模式为 GitHub 项目总结，M2 的 Vibe Revenue 为个人观点，均未独立核验。
- **公开知识（K）**：Google/Microsoft/经典产品框架为公开常识，未逐条核验。
- **数据条件**：Agentforce 18K+ 为官方宣传；其余为定性框架分析；"agent-to-agent commerce"为前瞻推断。

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-19 | v1.0 | 首次创建：三层 17 框架体系（通用适配 5 + AI 原生 6 + 转型专属 6）+ 三视角 MECE 区分 + 从 PRD 到 Agent Spec 六步流程 + 四第一性原理 + 案例与本系统验证 |
