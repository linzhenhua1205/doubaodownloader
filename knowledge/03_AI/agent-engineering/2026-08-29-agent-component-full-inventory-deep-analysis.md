# 🧩 Agent 组件全景解剖：从九组件列举到"十组件四域一核"完整模型

> **概要**: 以用户列举的九类组件（模型配置/操作/Skills/记忆/配套知识库访问/UI/Channel/CLI 管理/运行可观测）为骨架，补全"等"隐含项（Prompt 分级/推理循环/编排/治理评测），组织为 **十组件四域一核** 完整全景模型。每类组件给出定义、子组件清单、生命周期、关键设计问题与内外部实证；对五类新增重点组件（模型配置/知识库访问/UI/CLI 管理/可观测性）深度展开，其余快速引用既有六层模型结论；最后以 Claude Code / DeepSeek Harness / CowAgent 三系统做组件落位对照，并给出十问自检清单用于评估任意 Agent 系统的组件完备度。
>
> **版本**: v1.0
> **日期**: 2026-08-29
> **核心问题**: ① 一个 Agent 系统到底由哪些组件构成？② 每类组件的子组件、生命周期与关键设计问题是什么？③ 如何用组件清单评估/对比真实 Agent 系统？
> **元信息**: 文件状态=正式 | 覆盖范围=Agent 组件全景（模型配置/操作/技能/记忆/知识库/UI/Channel/CLI/可观测/治理）+ 三系统落位 + 自检清单
> **适用范围**: Agent 系统架构设计、Agent 平台选型、自研 Harness 组件规划、Agent 产品完备度评估
> **关键词**: Agent 组件 · 模型配置 · 工具面 · Skills · 记忆 · 知识库访问 · UI · Channel · CLI 管理 · 可观测性 · Guardrails · Harness · 组件完备度
> **相关**: [六层构成模型](./2026-08-03-agent-composition-and-coding-agent-comparison.md) · [Harness 即适配层](./2026-08-05-harness-os-process-boundary-isomorphism.md) · [DeepSeek Harness 技术框架](./2026-08-13-deepseek-harness-technical-framework-analysis.md) · [Agent 退化模式与 Harness 架构](./2026-08-17-agent-degeneration-modes-harness-architecture-deep-analysis.md) · [Agentic Serving 可观测性 Aries](./2026-08-10-aries-agentic-serving-observability-deep-analysis.md) · [Agent 框架/OS/Platform 辨析](./2026-08-29-agent-framework-agent-os-platform-deep-analysis.md) · [CowAgent 系统提示 token 审计](./2026-08-18-cowagent-system-prompt-token-audit.md) · [知识图谱特征与生态](./knowledge-system/2026-08-24-ai-era-knowledge-graph-features-and-github-ecosystem-deep-analysis.md) · [内部外部引用平衡](./knowledge-system/2026-08-25-internal-external-citation-balance-deep-analysis.md)

## 📑 目录

<!-- TOC -->

- [1. 引言与范围](#1-引言与范围)
- [2. 全景模型：十组件四域一核](#2-全景模型十组件四域一核)
  - [2.1 模型总览](#21-模型总览)
  - [2.2 与既有六层模型/ETCLOVG 的映射](#22-与既有六层模型etclovg-的映射)
- [3. 域1 认知基座：模型配置 / Prompt 分级 / 记忆](#3-域1-认知基座模型配置--prompt-分级--记忆)
  - [3.1 C1 模型配置层（新增重点）](#31-c1-模型配置层新增重点)
  - [3.2 C2 Prompt 分级体系（引用）](#32-c2-prompt-分级体系引用)
  - [3.3 C3 记忆子系统（引用）](#33-c3-记忆子系统引用)
- [4. 域2 行动能力：操作面 / Skills / 知识库访问](#4-域2-行动能力操作面--skills--知识库访问)
  - [4.1 C4 操作与工具面（引用+ACI 深挖）](#41-c4-操作与工具面引用aci-深挖)
  - [4.2 C5 Skills 技能层（引用）](#42-c5-skills-技能层引用)
  - [4.3 C6 知识库访问层（新增重点）](#43-c6-知识库访问层新增重点)
- [5. 域3 交互接入：UI / Channel](#5-域3-交互接入ui--channel)
  - [5.1 C7 UI 呈现层（新增重点）](#51-c7-ui-呈现层新增重点)
  - [5.2 C8 Channel 通道层（引用）](#52-c8-channel-通道层引用)
- [6. 域4 治理运维：CLI 管理面 / 可观测性 / 横切治理](#6-域4-治理运维cli-管理面--可观测性--横切治理)
  - [6.1 C9 CLI 管理面（新增重点）](#61-c9-cli-管理面新增重点)
  - [6.2 C10 可观测性（新增重点）](#62-c10-可观测性新增重点)
  - [6.3 横切：Guardrails / 权限 / 审计 / 评测](#63-横切guardrails--权限--审计--评测)
- [7. 内核：Loop 推理循环与上下文管理](#7-内核loop-推理循环与上下文管理)
- [8. 组件到真实系统落位：三系统对照矩阵](#8-组件到真实系统落位三系统对照矩阵)
- [9. 组件完备度十问自检清单](#9-组件完备度十问自检清单)
- [10. 结论：给技术决策者的五条判断](#10-结论给技术决策者的五条判断)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 1. 引言与范围

**本文回答一个问题**：一个 Agent 系统由哪些组件构成？

用户给出的清单——模型配置、操作、Skills、记忆、配套知识库访问、UI、Channel、CLI 管理、运行可观测——已经覆盖了绝大部分组件，但"等"字背后还藏着三类容易被遗漏的组件：**Prompt 分级体系**（Agent 的人格/规则/身份）、**推理循环 Loop**（Agent 的心脏）与**治理评测**（防止 Agent 漂移的横切机制）。

本文的贡献不是再列一份清单，而是把清单组织成**有结构的模型**（MECE：四域 + 一核 + 横切），并对每类组件给出三个维度的解剖：

| 维度 | 回答的问题 |
|:-----|:----------|
| **定义与边界** | 这个组件管什么、不管什么（与相邻组件的分工） |
| **子组件与生命周期** | 由哪些部分组成、从创建到退役经历什么 |
| **关键设计问题** | 工程上最容易被踩的坑、最值得投入的点 |

**覆盖范围**：软件架构层面的组件盘点与机制展开，不涉及具体模型推理细节、不涉及训练。外部信源以 Anthropic 工程博客（2024-12）、OpenAI Agents SDK 官方文档（2026）、OpenTelemetry GenAI 语义约定（2026）为主；内部引用知识库既有 14 篇深度文档承接结论。

**目标读者**：需要设计/评估 Agent 系统的架构师与工程师；需要判断"自研 vs 采购 vs 平台"的技术决策者；Agent 平台产品经理。

**术语约定**：文中 "Agent" 指"由 LLM 动态决定自身流程与工具使用的系统"（区别于 Workflow）[来源: Anthropic Building Effective Agents, 2024-12]；"组件"指构成 Agent 系统的最小职能单元，可独立设计/替换/评估。

---

## 2. 全景模型：十组件四域一核

### 2.1 模型总览

把用户列举的九项 + "等"隐含项按**职能域**组织（同域内互斥、跨域穷尽）：

```text
+------------------------------------------------------------------------------+
|  GUARDRAILS (cross-cut)  Security / Permission / Audit / Evaluation          |
+------------------------------------------------------------------------------+
|  Domain 4: OPERATE & GOVERN  (how to run it)                                 |
|    C9 CLI Admin   C10 Observability                                         |
+------------------------------------------------------------------------------+
|  Domain 3: INTERACT  (how to use it)                                         |
|    C7 UI          C8 Channel                                                |
+------------------------------------------------------------------------------+
|  Domain 2: ACT  (how to do things)                                           |
|    C4 Actions/Tools   C5 Skills   C6 Knowledge Base Access                  |
+------------------------------------------------------------------------------+
|  Domain 1: COGNITION  (how it thinks)                                        |
|    C1 Model Config   C2 Prompt System   C3 Memory                           |
+------------------------------------------------------------------------------+
|  CORE: LOOP (perceive -> plan -> act -> observe -> reflect)                 |
|         + Context Management                                                |
+------------------------------------------------------------------------------+
```

| 编号 | 组件 | 用户清单对应 | 回答的问题 | 确定性 |
|:----:|:-----|:------------:|:-----------|:------:|
| C1 | **模型配置层** Model Config | ✅ 模型配置 | 用哪个模型、怎么调、怎么换、怎么省钱 | 确定性 |
| C2 | **Prompt 分级体系** | "等" | Agent 是谁、受什么约束 | 半确定性 |
| C3 | **记忆子系统** Memory | ✅ 记忆 | Agent 记得什么、怎么忘 | 半确定性 |
| C4 | **操作与工具面** Tools/MCP/CLI/Scripts | ✅ 操作 | 怎么与外部世界交互 | 确定性 |
| C5 | **Skills 技能层** | ✅ skills | 经验如何复用 | 半确定性 |
| C6 | **知识库访问层** KB Access | ✅ 配套知识库访问 | 共享知识怎么读、怎么写 | 确定性 |
| C7 | **UI 呈现层** | ✅ UI | 人怎么直观地与 Agent 交互 | 确定性 |
| C8 | **Channel 通道层** | ✅ channel | 消息从哪来、回哪去 | 确定性 |
| C9 | **CLI 管理面** Admin CLI | ✅ cli管理 | 运维者怎么装/配/管 Agent 本身 | 确定性 |
| C10 | **可观测性** Observability | ✅ 运行可观测 | 系统在干什么、为什么这么干 | 确定性 |
| — | **内核 Loop** | "等" | 如何持续思考与行动 | 概率性 |
| — | **横切治理** Guardrails | "等" | 哪些不能做、谁做的、做得对不对 | 确定性 |

> **核心架构原则**（延续既有六层模型结论）：只有 Loop（L2 概率内核）是非确定性的，其余全部组件都应尽量确定性化——**把不确定性限制在模型推理边界内** [来源: 六层构成模型 §1]。组件全景模型是这一原则在"完整系统"层面的展开：十组件 + 横切中，唯一概率性的只有内核 Loop。

### 2.2 与既有六层模型/ETCLOVG 的映射

| 本模型 | 六层模型（08-03）[来源: 六层构成模型 §1.1] | ETCLOVG 七层 [来源: Agent OS 五种范式] | 关系 |
|:-------|:------------------|:----------------|:-----|
| 内核 Loop + C2/C3 | L1 认知基座 + L2 Loop | C – Context & Memory, L – Lifecycle | 本模型把 L1 拆为 C1/C2/C3 三个独立组件 |
| C4/C5 | L3 工具面 + L4 Skills | E, T – Execution & Tool | 一致，C6 为新增 |
| C7/C8 | L6 Channel | （Channel 在 ETCLOVG 未显式分层） | C7 为新增显式组件 |
| C9/C10 | 未显式分层（O 横切） | O – Observability | C9/C10 从横切提升为显式组件 |
| 横切治理 | 未显式分层 | V, G – Verification & Governance | 一致 |

> **与既有模型的关系**：本模型不是推翻六层模型，而是**把"横切/隐含"组件显式化**（模型配置、知识库访问、UI、CLI 管理、可观测性），并把"一核"（Loop）从六层中的 L2 提升为贯穿全部组件的内核。对已有六层覆盖的 C2/C3/C4/C5/C8 本文只做精炼引用，重点展开五个新增组件。

---

## 3. 域1 认知基座：模型配置 / Prompt 分级 / 记忆

### 3.1 C1 模型配置层（新增重点）

**定义**：管理"Agent 用哪个模型、如何调用、如何在不同模型间切换"的组件。这是九组件清单中**最容易被低估**的一项——大多数实现只把它当成"填一个 API key"，但生产级系统里它是独立的配置子系统。

**子组件与生命周期**：

| 子组件 | 职能 | 关键设计问题 |
|:-------|:-----|:------------|
| **Provider 抽象** | 统一多厂商 API（OpenAI/Anthropic/DeepSeek/本地 Ollama…） | 接口契约怎么定才能让"换模型不改代码"？OpenAI 的 Responses API 与 Chat Completions 两套协议并存本身就是教训 [来源: OpenAI Agents SDK 文档, 2026] |
| **模型选择与路由** | 按任务难度/成本/延迟选模型 | Anthropic 建议"简单问题路由到小模型（Haiku 4.5）、难问题到大模型（Sonnet 4.5）"优化成本 [来源: Anthropic Building Effective Agents, 2024-12] |
| **参数配置** | temperature/top_p/max_tokens/stop/thinking 预算 | 深度推理模型（thinking 模式）的参数面与普通模型完全不同，参数面是否按模型类型隔离？ |
| **降级与容错** | 主模型失败→备用模型/重试/降级策略 | 熔断、超时、配额耗尽时的行为是否可配置？ |
| **成本与 token 审计** | 用量统计、成本归因、预算控制 | 固定成本（system prompt + tools schema）与增量成本分别统计？[来源: CowAgent 系统提示 token 审计 §1] |
| **密钥与安全** | API key 管理、加密存储、权限隔离 | key 是否明文入库？是否支持按环境隔离？（本知识库 env_config 即此组件的实现） |

**生命周期**：模型配置是"启动即加载、运行时热更新"的常驻组件——配置变更（换模型/调参数）不应要求重启整个 Agent。OpenAI SDK 将其独立为 `Model settings` 页面与 `Model` 模块（支持 OpenAI Chat Completions / Responses / 多 Provider / 第三方 LiteLLM 适配）[来源: OpenAI Agents SDK 文档, 2026]。

**工程判断**：模型配置层是"组件间耦合度"的试金石——如果换模型要改业务代码，说明 Agent 没有独立的模型配置组件，而是把模型写死进了 Loop。

### 3.2 C2 Prompt 分级体系（引用）

**定义**：按"稳定性 × 作用域"把指令性信息分级注入的认知基座。

精炼结论（详见六层模型 §2）[来源: 六层构成模型 §2.3]：

| 级别 | 内容 | 变化频率 | 注入方式 | 违背后果 |
|:-----|:-----|:--------:|:---------|:---------|
| Rule | 铁律/安全红线/存储规则 | 季更 | 每次会话全量 | 违反有明确后果 |
| Agent | 人格/行为准则/协作模式 | 季更 | 每次会话全量 | 行为漂移 |
| User | 身份/偏好/质量标准 | 年更 | 每次会话全量 | 服务失配 |
| Memory | 长期事实/决策 + 当日进展 | 日/月更 | 核心全量 + 检索加载 | 遗忘/冲突 |

**关键设计问题**：最常见的失败模式是"把日更事实写进年更约束"（上下文膨胀、规则失效）或"把铁律写进可被覆盖的会话提示词"（安全失效）。Claude Code 的 CLAUDE.md 三明治结构（Enterprise Policy → User → Project + @import）与本知识库四文件体系（RULE/AGENT/USER/MEMORY）是同构设计 [来源: 六层构成模型 §2.2]。

> **成本实证**：本知识库实测四 rule 文件（ProjectCtx 节）占 system prompt 24.0%，是仅次于 Skills 节的第二大固定成本 [来源: CowAgent 系统提示 token 审计 §3.1]。

### 3.3 C3 记忆子系统（引用）

**定义**：管理"Agent 知道什么、过去发生过什么、以后该怎么做"的子系统。

精炼结论（详见六层模型 §3）[来源: 六层构成模型 §3.1]：

| 类型 | 回答 | 推荐形态 | 主要风险 |
|:-----|:-----|:---------|:---------|
| Working Memory | 当前任务做到哪一步 | Context + 状态表 | 摘要丢失来源 |
| Episodic Memory | 过去发生过什么 | Append-only 事件日志 | 日志含敏感输入 |
| Semantic Memory | 当前相信哪些事实 | 结构化事实 + 向量/全文索引 | 错误事实被持续召回 |
| Procedural Memory | 以后应该怎样做 | 版本化 Skill/模板 | 持久化行为后门 |

**关键设计问题**：记忆的胜负手在**写入侧**——什么该记、什么该忘、谁来判定重要性。OpenAI SDK 将 `Sessions` 作为"持久化记忆层"内置于运行时，并支持 SQLAlchemy/Redis/MongoDB/加密会话等后端 [来源: OpenAI Agents SDK 文档, 2026]；知识库另有五篇论文的记忆生命周期专题 [来源: Agent 记忆生命周期五论文]./2026-08-07-agent-memory-lifecycle-five-papers-deep-analysis.md。

> **反模式**：把对话、事件、事实、流程全部切片后放进同一个向量集合——同时失去历史不可变性、当前信念一致性、流程版本治理、精确删除能力 [来源: 六层构成模型 §3.1]。

---

## 4. 域2 行动能力：操作面 / Skills / 知识库访问

### 4.1 C4 操作与工具面（引用+ACI 深挖）

**定义**：Agent 与外部世界交互的确定性接口层，含内置 Tools / MCP / CLI / Scripts 四件套。

精炼结论（详见六层模型 §5）[来源: 六层构成模型 §5]：

| 机制 | 定位 | 2026 生态状态 |
|:-----|:-----|:-------------|
| 内置 Tools | 原子操作（文件/搜索/执行） | Anthropic 建议工具定义投入与 HCI 同等的工程精力 [来源: Anthropic Building Effective Agents, Appendix 2, 2024-12] |
| MCP | 开放协议接入第三方能力 | 已成为工具接入的事实标准；OpenAI SDK 内建 MCP server 调用 [来源: OpenAI Agents SDK 文档, 2026] |
| 面向 Agent 的 CLI | 鉴权与执行边界 | 参数显式化/输出可解析/dry-run 预检/失败阶段明确 [来源: Agent 工具链工程化] |
| Scripts | 可执行经验沉淀 | 输入→输出→失败方式→恢复动作四要素 [来源: 六层构成模型 §5.4] |

**ACI 深挖（Agent-Computer Interface）**：Anthropic 明确提出"投资多少精力做 HCI，就该投资多少做 ACI"——工具定义要给出示例用法、边界条件、参数命名直觉化；实测发现模型对相对路径易错，改为强制绝对路径后"模型使用得完美无缺"（SWE-bench 实战）[来源: Anthropic Building Effective Agents, Appendix 2, 2024-12]。

**关键设计问题**：工具面是"概率内核与确定性世界的唯一桥梁"——工具文档质量直接决定 Agent 能力上限；工具 schema 同时是每轮请求的固定成本（本知识库实测 tools schema = 3,861 tokens/轮）[来源: CowAgent 系统提示 token 审计 §1]。

### 4.2 C5 Skills 技能层（引用）

**定义**：把"过程知识"打包为可复用单元（SKILL.md 声明式技能）的机制。

精炼结论（详见六层模型 §6）[来源: 六层构成模型 §6]：

- **触发机制**：Agent 按任务相关性自动加载（不是常驻），避免上下文膨胀
- **与 CLAUDE.md 的分工**：CLAUDE.md = 静态规则（"你是谁"），Skills = 动态能力（"你会做什么"）
- **四者辨析**：Skill（探索性任务）/ Workflow（阶段清楚可验收）/ Script（原子操作）/ Command（用户快捷触发）各司其职
- **组合模式**：先用 Skill 生成 Workflow，再用 Workflow 编排多个 Agent，Agent 内部调用 Script，用户用 Command 快捷触发

> **成本实证**：本知识库 104 个技能 XML 列表占 system prompt 61.8%（12,269 tokens，平均 120 tok/技能），是最大可降项——MCP 的"embedding 检索 top-k 注入"模式可复用到 Skills（top-10 注入可降 ~52%）[来源: CowAgent 系统提示 token 审计 §4]。

### 4.3 C6 知识库访问层（新增重点）

**定义**：Agent 访问**配套知识库**（持久化、结构化、可共享的知识资产）的组件——包括读取（检索）、写入（沉淀）、组织（索引/图谱）三类能力。

**与记忆的分工（第一性辨析）**：这是用户清单中与 C3 记忆最易混淆的组件。区分标准是**知识的性质与生命周期**：

| 维度 | C3 记忆子系统 | C6 知识库访问层 |
|:-----|:-------------|:----------------|
| 内容性质 | 个人私有事实（偏好/决策/进展） | 共享结构化知识（领域文档/方法论/归档） |
| 生命周期 | 小时~天~月级，随对话演化 | 持久化，跨会话/跨 Agent 复用 |
| 写入主体 | Agent 自动写入（记忆机制） | 受控管线（暂存→加工→沉淀）[来源: 知识库 RULE.md 工作流] |
| 一致性要求 | 允许演进覆盖 | 需要版本治理与引用追溯 |
| 典型形态 | 事件日志/事实表/向量库 | 分层目录 + 索引 + 全文/向量检索 + 知识图谱 |

**子组件与关键设计问题**：

| 子组件 | 职能 | 关键设计问题 |
|:-------|:-----|:------------|
| **检索**（读取） | 关键词/向量/混合检索，RAG | 检索质量门禁怎么设？"内部引用一致性错误"如何防？（引用多样性悖论）[来源: 内部外部引用平衡 §1] |
| **写入**（沉淀） | 受控归档：素材→加工→结构化 | 写入是否需要管线门禁（格式检查/死链检查/去重）？[来源: 知识库批量导入质量门禁] |
| **索引**（组织） | 目录/索引/账本三层分离 | 目录变更时索引如何自动刷新？[来源: 知识索引治理] |
| **图谱**（关联） | 实体/概念/交叉链接网络 | 关系标注（related/depends-on/see-also）是否维护？[来源: knowledge-doc-writer 第7步] |
| **信源治理** | 内部/外部引用配比管控 | 内部引用 ≤60%、外部 ≥40%，防"一致的错误"传播 [来源: 内部外部引用平衡, Q10 铁律] |

**为什么是独立组件而非记忆子集**：知识库的可验证性要求（来源+基线+条件）、版本治理、多 Agent 共享这三个特性，使它与"私有记忆"在架构上必须分离——把知识库塞进记忆子系统会同时破坏记忆的轻量与知识的严谨。知识库访问层在 2026 年的趋势是"构建自动化/检索融合化/表示层次化/生命周期实时化/应用场景代码化/生态分层化" [来源: AI 时代知识图谱特征与生态 §1]。

---

## 5. 域3 交互接入：UI / Channel

### 5.1 C7 UI 呈现层（新增重点）

**定义**：人直接与 Agent 交互的可视化界面。它与 C8 Channel 同源（都是"人-Agent 接口"），区别在于：**Channel 管协议与路由（机器视角），UI 管呈现与操作（人视角）**。

**UI 的三层形态（MECE 划分）**：

| 形态 | 载体 | 面向对象 | 关键设计问题 |
|:-----|:-----|:---------|:------------|
| **交互界面** | 终端 CLI / Web 对话框 / IDE 面板 | 用户操作 Agent | 如何让"Agent 在干什么"可见？（Anthropic 三原则之一：transparency，显式展示 planning steps）[来源: Anthropic Building Effective Agents, 2024-12] |
| **呈现界面** | 流式输出/工具调用可视化/产物预览/图表 | 用户理解输出 | Agent 的中间过程（thought/tool/artifact）如何呈现才不干扰主输出？ |
| **管理界面** | 配置面板/用量看板/日志浏览器 | 管理员运维 | 模型配置/技能管理/权限设置在 UI 上是否可操作？（OpenAI SDK 提供 `agent visualization` 可视化 agentic flow [来源: OpenAI Agents SDK 文档, 2026]） |

**形态演进实证**（Claude Code 通道形态即 UI 形态演进史）[来源: 六层构成模型 §9.3]：

| 形态 | 时间 | 定位 |
|:-----|:-----|:-----|
| 终端 CLI | 2025-02 | 原生形态，`claude` 命令 |
| Headless/SDK | 2025-06 | 无终端编程调用（CI/CD） |
| IDE 集成 | 2025 | VS Code/JetBrains 插件 |
| Claude Cowork | 2026-03 | 桌面 GUI，面向非开发者办公 |
| Web/Chrome 连接器 | 2026 | 浏览器操作 |

**关键设计问题**：UI 层最大的工程陷阱是**把 UI 逻辑与 Agent 核心耦合**——正确的架构是"UI 只是 Channel 的一种消费形态"，Agent 核心只输出结构化消息，由 UI 层决定如何呈现（终端纯文本 / Web 富文本 / IDE 内联 diff）。

### 5.2 C8 Channel 通道层（引用）

**定义**：Agent 与外界（人/系统）的消息出入口，负责协议适配与来源路由。

精炼结论（详见六层模型 §9）[来源: 六层构成模型 §9]：

- **统一消息模型**：`ChatMessage` 用字段契约吸收平台差异（msg_id/ctype/content/from_user_id/is_group/is_at…），新平台只需映射，核心零改动（CowAgent Harness 实证）
- **来源通道路由**："回传走来源通道"——消息上下文携带 channel_type 贯穿全链路，是多通道接入同一 Agent 而不串台的基础
- **对多 Agent 系统的延伸**：Channel 不限于 IM，而是"任何消息源"（定时任务/事件流/A2A 调用），来源路由升级为任务级上下文隔离

**与 C7 UI 的边界**：同一 Agent 的终端 UI 与 IM Channel 共用同一套消息模型与来源路由——Claude Code 的形态演进证明 UI 形态可以多样，但 Channel 抽象保持稳定。

---

## 6. 域4 治理运维：CLI 管理面 / 可观测性 / 横切治理

### 6.1 C9 CLI 管理面（新增重点）

**定义**：运维者管理 **Agent 本身**（安装/配置/启停/会话/诊断）的命令行接口。它与 C4 工具面中的"面向 Agent 的 CLI"是**两类完全不同的 CLI**：

| 维度 | C4 工具 CLI（agent-facing） | C9 管理 CLI（admin-facing） |
|:-----|:----------------------------|:----------------------------|
| 使用者 | Agent（模型） | 人（运维者） |
| 目的 | 让 Agent 执行任务 | 管理 Agent 系统本身 |
| 典型命令 | `search_files`/`bash`/`read` | `agent install`/`agent config`/`agent session list` |
| 输出要求 | 结构化可解析（模型消费） | 人类可读 + 结构化混合 |
| 错误处理 | 失败阶段明确 + 可恢复动作 | 诊断信息 + 修复建议 |

**管理面的典型子命令集**：

| 子域 | 命令示例 | 回答的问题 |
|:-----|:---------|:----------|
| 生命周期 | `init`/`start`/`stop`/`status` | Agent 进程怎么管理？ |
| 配置 | `config get/set`/`model list`/`skill install` | 组件如何装配与热更新？ |
| 会话 | `session list/resume/export` | 会话状态如何持久化与恢复？ |
| 诊断 | `doctor`/`log tail`/`trace` | 出问题时怎么定位？ |
| 更新 | `update`/`rollback`/`version` | 版本如何管理、如何回滚？ |

**工程判断**：管理面是"Agent 产品化"的分水岭——只有交互界面没有管理面的 Agent 是"demo"，有完整管理面的 Agent 才是"产品"。DeepSeek Harness 的 "Model + Harness = Agent" 定位中，Harness 即包含"会话持久化/工具编排/沙箱执行"的管理性组件 [来源: DeepSeek Harness 技术框架 §概要]。

### 6.2 C10 可观测性（新增重点）

**定义**：观察 Agent "在干什么、为什么这么干、干得怎么样"的组件，含日志（Logging）、追踪（Tracing）、度量（Metrics）、评测（Evaluation）四支柱。

**为什么是 2026 年组件成熟度的分水岭**：

1. **标准已就位**：OpenTelemetry 发布独立 GenAI 语义约定仓库，包含 **Agent spans**、**MCP（Model Context Protocol）语义约定**与 GenAI spans/metrics/events 三类信号 [来源: OpenTelemetry GenAI Semantic Conventions, 2026]——可观测性从"各家自研"走向"标准协议"。
2. **度量对象正在被纠正**：Aries 实验（arXiv:2607.29069）实证三大发现——①token 中心指标遗漏非推理瓶颈；②保留额外上下文收益递减且降低服务容量；③工具沙箱长空闲/短突发交替使快照式挂起成本高昂——共同指向"度量对象错误"，主张**轨迹级指标**（跨组件 agent 轨迹 + 系统遥测关联）[来源: Agentic Serving 可观测性 Aries §概要]。
3. **工具调用时长成为一等指标**：工具调用耗时/重试/失败率是 Agent 性能的核心观测面 [来源: 工具调用时长可观测性]。

**四支柱与关键设计问题**：

| 支柱 | 观测对象 | 关键设计问题 |
|:-----|:---------|:------------|
| Logging | 事件（消息/工具调用/决策） | 是否 append-only？敏感输入是否脱敏？ |
| Tracing | 一次任务的完整链路（spans） | 是否按 OTel GenAI 语义约定打点？Agent span 与工具 span 是否关联？[来源: OTel GenAI SemConv, 2026] |
| Metrics | 聚合指标（延迟/成本/成功率/上下文利用率） | 是否区分固定成本与增量成本？是否按任务/模型/工具维度聚合？[来源: CowAgent 系统提示 token 审计 §3] |
| Evaluation | 输出质量（Eval 基准/回归测试） | 是否有防污染的评测基准？（harness-bench 生态三族）[来源: harness-bench 生态 §概要] |

**工程判断**：可观测性是"治理横切层"的数据底座——没有可观测性的 Guardrails 是盲人摸象，没有可观测性的评测是黑箱打分。

### 6.3 横切：Guardrails / 权限 / 审计 / 评测

**定义**：贯穿全部组件的安全与质量机制——"哪些不能做、谁做的、做得对不对"。

| 机制 | 职能 | 实证 |
|:-----|:-----|:-----|
| **Guardrails**（输入输出校验） | 在 Agent 执行**之外**并行校验输入/输出，快速失败 | OpenAI SDK 将 Guardrails 列为核心原语，与 Agent 执行并行运行 [来源: OpenAI Agents SDK 文档, 2026] |
| **权限**（Action Gate） | 高危操作拦截/分级授权 | 对应 ETCLOVG 的 G – Governance；Hook 机制（PreToolUse 拦截）是工程实现 [来源: 六层构成模型 §7.4] |
| **审计**（Append-only 记录） | 谁在什么时候做了什么 | 与记忆的 Episodic 层同源但独立（审计不可变、记忆可演进）[来源: 六层构成模型 §3.1] |
| **评测**（Eval 闭环） | 质量回归、退化检测 | 三大退化模式（Agentic laziness/Self-preferential bias/Goal drift）证明**没有评测闭环的 Agent 必然漂移** [来源: Agent 退化模式与 Harness 架构 §概要] |

**关键设计问题**：横切治理的最大工程陷阱是"把治理逻辑塞进主循环"——正确姿势是用 Hooks/旁路把"与推理无关但必须发生的动作"从主循环剥离，确定性、低成本、可审计地发生 [来源: 六层构成模型 §7.4]。

---

## 7. 内核：Loop 推理循环与上下文管理

**定义**：Agent 的心脏——"感知→规划→行动→观察→反思"的持续循环。Anthropic 对 Agent 的定义即"LLM 基于环境反馈循环使用工具" [来源: Anthropic Building Effective Agents, 2024-12]。

**核心事实**：

1. **Loop 是唯一概率性内核**：只有模型推理是非确定的，其余组件都应确定性化 [来源: 六层构成模型 §1.1]。
2. **Loop 正在被工程化**：从 ReAct（纯提示词维持）→ Long Horizon（单一推理循环）→ Workflow Runtime（循环编译为可执行脚本）——"确定的骨架归代码，不确定的判断归模型" [来源: 六层构成模型 §4]。
3. **上下文管理是 Loop 的成本与质量交汇点**：截断/裁剪/压缩/缓存四层策略 + Prompt Caching 前缀复用；上下文组装的经济学决定每轮成本 [来源: Agent 上下文消息组装 token 经济学, 2026-08-18]。
4. **编排是 Loop 的扩展**：Subagent（上下文隔离）/ 并行化（吞吐）/ 旁路（异步）解决"一个上下文不够用" [来源: 六层构成模型 §7]。

> **为何把 Loop 单列为"内核"而非"域内组件"**：Loop 不与其他组件并列——它是**驱动**其他组件的引擎。模型配置决定 Loop 用什么脑子，工具面决定 Loop 能做什么，记忆/知识库决定 Loop 知道什么，可观测性决定我们能否看懂 Loop。任何组件缺失，Loop 仍然能跑（降级），但组件完备度决定 Loop 的能力上限与可靠性。

---

## 8. 组件到真实系统落位：三系统对照矩阵

用十组件全景模型盘点三个代表性系统，验证模型的判别力：

| 组件 | Claude Code（Anthropic） | DeepSeek Harness | CowAgent（本知识库） |
|:-----|:------------------------|:-----------------|:---------------------|
| C1 模型配置 | 多模型 + 多 Provider + 降级（2026 起支持非 Anthropic 模型） | 模型推理 + Harness 分离，KV Cache 复用 [来源: DeepSeek Harness 技术框架] | 15+ 厂商 Models 层 [来源: 六层构成模型 §9.1] |
| C2 Prompt 分级 | CLAUDE.md 三明治（Enterprise/User/Project + @import） | Prompt 分级注入 | RULE/AGENT/USER/MEMORY 四文件 |
| C3 记忆 | `/memory` 工具 + 会话恢复 | 会话持久化 | memory/ 日文件 + MEMORY.md + 每日蒸馏 |
| C4 工具面 | 内置 Tools + MCP Client/Host + Hooks | 工具编排 + 沙箱执行 + MCP | 工具集 + MCP + Scripts（面向 Agent CLI 规范） |
| C5 Skills | SKILL.md 技能包（2025-10 推出） | Skills 插件化 | 104+ 技能（cow-skill-hub）[来源: CowAgent 系统提示 token 审计 §4] |
| C6 知识库访问 | 项目文件系统（读取为主） | — | **最完备**：分层目录 + 索引 + log 账本 + 图谱 + 引用治理 |
| C7 UI | 终端/IDE/桌面（Cowork）/Web | CLI 为主 | 终端 + 飞书（Channel 形态） |
| C8 Channel | 终端/IDE/Web/Chrome 连接器 [来源: 六层构成模型 §9.3] | CLI | Feishu/终端/Web/SSE/定时任务（ChatMessage 16 字段）[来源: 六层构成模型 §9.1] |
| C9 CLI 管理面 | `claude config`/`/doctor` 等 | CLI 框架 | 管理脚本 + 定时任务治理 |
| C10 可观测性 | 内置 tracing/状态行 + Hooks 通知 | 反馈循环 | 日志 + log 账本 + 日报 + token 审计 |
| 横切治理 | Guardrails（SDK）+ 权限钩子 | 沙箱安全 | RULE 红线 + Action Gate + 评测（doc-final-check） |

**判别力结论**：三系统组件完备度差异显著——Claude Code 在 C1/C4/C7/C10 领先（产品化最完整）；CowAgent 在 **C6（知识库访问）与横切治理**上独树一帜（知识库三位一体系统是任何商业 Agent 产品没有的组件）；DeepSeek Harness 在"模型-工具解耦"哲学上最清晰但组件面最薄。**没有哪个系统十项全优——组件完备度是取舍的结果，不是目标本身。**

---

## 9. 组件完备度十问自检清单

评估任意 Agent 系统（自研/采购/平台）时，逐项自检：

| # | 组件 | 自检问题 | 缺失的典型症状 |
|:-:|:-----|:---------|:--------------|
| 1 | 模型配置 | 换模型是否不需要改业务代码？有降级策略吗？ | 模型写死在代码里；主模型挂了系统就瘫 |
| 2 | Prompt 分级 | 约束/人格/身份/事实是否分文件分级？ | 日更事实混进年更约束→上下文膨胀 |
| 3 | 记忆 | 四类记忆是否分型？写入侧有受控机制吗？ | 全塞一个向量库→无法精确删除/演进 |
| 4 | 操作 | 工具面四件套齐了吗？ACI 有人打磨吗？ | 工具文档是摆设；模型不会用工具 |
| 5 | Skills | 过程知识是否可复用打包？触发是否按需？ | 经验全在对话里，换会话就丢 |
| 6 | 知识库 | 读取/写入/索引/图谱/信源治理五件套齐了吗？ | 知识无法跨会话复用；引用无出处 |
| 7 | UI | 交互/呈现/管理三层都覆盖了吗？ | 只能黑盒对话，看不到 Agent 在干什么 |
| 8 | Channel | 多通道是否统一消息模型 + 来源路由？ | 加一个新平台要改核心代码 |
| 9 | CLI 管理 | 有完整生命周期/配置/诊断命令吗？ | 出问题只能重启，无法定位 |
| 10 | 可观测 | 日志/追踪/度量/评测四支柱齐了吗？按 OTel 标准吗？ | 无法回答"它为什么这么做" |

> **使用方式**：≥8 项 ✅ 为组件完备系统；5-7 项为可用但脆弱；<5 项为 demo 级。自检结果应指导投入排序——**短板组件优先**，因为 Agent 系统的可靠性由最弱组件决定。

---

## 10. 结论：给技术决策者的五条判断

1. **组件全景 = 十组件四域一核 + 横切治理**：认知域（模型配置/Prompt/记忆）× 行动域（工具/Skills/知识库）× 交互域（UI/Channel）× 运维域（CLI 管理/可观测性）+ Loop 内核 + Guardrails 横切——用户列举的九项全部落位，且"等"隐含的三类组件（Prompt/Loop/治理）是完整系统不可缺的。

2. **模型配置是最被低估的组件**：它不是"填 API key"，而是 Provider 抽象/路由/降级/成本审计四件套——是"Agent 组件化程度"的试金石 [来源: OpenAI Agents SDK 文档, 2026; CowAgent token 审计]。

3. **知识库访问是记忆的外部化与共享化**：与私有记忆在架构上必须分离——可验证性（来源+基线+条件）、版本治理、多 Agent 共享是它的三个成立理由。

4. **UI 与 Channel 同源、与核心解耦**：Agent 核心只输出结构化消息，UI 是 Channel 的一种消费形态——Claude Code 五种形态演进证明这个架构的稳定性 [来源: 六层构成模型 §9.3]。

5. **可观测性是 2026 组件成熟度的分水岭**：OTel GenAI 语义约定（Agent spans/MCP）就位 + Aries 实证"token 中心指标是错误度量对象"→ 轨迹级遥测成为标准 [来源: OTel GenAI SemConv, 2026; Aries, arXiv:2607.29069]。没有评测闭环的 Agent 必然漂移（三大退化模式）[来源: Agent 退化模式与 Harness 架构]。

---

## 参考文件

### 内部知识库引用

| # | 来源 | 用途 |
|:-:|:-----|:-----|
| [1] | [六层构成模型](2026-08-03-agent-composition-and-coding-agent-comparison.md) | §2-5 Prompt 分级/记忆/Loop/工具面/Skills/编排/Channel 全覆盖 |
| [2] | [CowAgent 系统提示 token 审计](2026-08-18-cowagent-system-prompt-token-audit.md) | §3-4 固定成本 24,484 tokens、Skills 61.8%/ProjectCtx 24% |
| [3] | [DeepSeek Harness 技术框架](2026-08-13-deepseek-harness-technical-framework-analysis.md) | Model + Harness = Agent、会话持久化 |
| [4] | [Agent 退化模式与 Harness 架构](2026-08-17-agent-degeneration-modes-harness-architecture-deep-analysis.md) | laziness/self-preference/goal drift 三大退化模式 |
| [5] | [Agentic Serving 可观测性（Aries 深潜）](2026-08-10-aries-agentic-serving-observability-deep-analysis.md) | 轨迹级遥测、token 中心指标缺陷 |
| [6] | [Agent 记忆生命周期五论文](2026-08-07-agent-memory-lifecycle-five-papers-deep-analysis.md) | §3.3 记忆四类与生命周期 |
| [7] | [工具调用时长可观测性](2026-08-11-tool-call-duration-observability-deep-analysis.md) | §6.2 工具调用时长一等指标 |
| [8] | [harness-bench 生态](2026-08-21-harness-bench-ecosystem-deep-analysis.md) | §6.2 评测基准防污染 |
| [9] | [AI 时代知识图谱特征与生态](2026-08-24-ai-era-knowledge-graph-features-and-github-ecosystem-deep-analysis.md) | §4.3 知识库访问层六特征 |
| [10] | [内部外部引用平衡](2026-08-25-internal-external-citation-balance-deep-analysis.md) | §4.3 信源配比 Q10 铁律 |
| [11] | [Agent 框架/OS/Platform 辨析](2026-08-29-agent-framework-agent-os-platform-deep-analysis.md) | §2-8 Framework/OS/Platform 组件构成 |
| [12] | [Agent 上下文消息组装 token 经济学](2026-08-18-agent-context-message-assembly-token-economics.md) | §7 上下文组装成本 |
| [13] | [Agent 工具链工程化](2026-06-26-agent-toolchain-cli-execution.md) | §5.3 面向 Agent 的 CLI 设计规范 |
| [14] | [Agent OS 五种范式](2026-06-26-agent-os-five-paradigms.md) | §2.2 ETCLOVG 七层映射 |

### 外部资料引用

| # | 来源 | 用途 |
|:-:|:-----|:-----|
| [15] | Anthropic, "Building Effective Agents", 2024-12-19 | augmented LLM 定义、workflows vs agents、ACI 三原则、工具工程化 |
| [16] | OpenAI, "OpenAI Agents SDK" 官方文档, 2026 | Agents/Handoffs/Guardrails/Sessions/Tracing 原语、Sandbox agents、Capabilities（Skills/Compaction/Memory）、Model settings、MCP、agent visualization |
| [17] | OpenTelemetry, "GenAI Semantic Conventions", 1.44.0 | GenAI spans/metrics/events、Agent spans、MCP 语义约定 |
| [18] | Microsoft/Imperial College et al., "Aries: Agentic Serving", arXiv:2607.29069, 2026-07 | 轨迹级遥测、token 中心指标缺陷三大实证 |

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-29 | v1.0 | 首次创建：十组件四域一核全景模型，五类新增组件深挖（模型配置/知识库访问/UI/CLI 管理/可观测性），三系统落位对照 + 十问自检清单 |
