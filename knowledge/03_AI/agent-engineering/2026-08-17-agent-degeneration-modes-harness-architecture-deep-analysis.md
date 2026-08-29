# 单 Agent 三重退化模式与 Harness 架构对策

> **类型**: 深度分析 | **日期**: 2026-08-17 | **版本**: v1.0
> **来源**: 用户命题（偷懒/自我偏爱/目标漂移三退化模式 + 单上下文架构局限 + Anthropic 定制 Harness）+ Anthropic 一手工程博客（multi-agent research system 全文）+ 知识库互锁（Harness 即适配层 / OneDayAgent / CowAgent 问题清单 / 上下文污染 / Ralph 循环 / 三阶段走读）+ 第一性原理推导
> **适用范围**: Agent 架构设计 / Harness 设计 / 长时程任务工程化 / 对抗性验证体系 / 知识库自身 Agent 系统演进
> **相关**: [Harness 即适配层](../../03_AI/agent-engineering/2026-08-05-harness-os-process-boundary-isomorphism.md) · [OneDayAgent 长时程 Harness](../../03_AI/agent-engineering/2026-08-07-onedayagent-long-horizon-harness-deep-analysis.md) · [CowAgent 问题全清单](../../03_AI/methodology/2026-08-14-cowagent-system-problems-full-inventory.md) · [上下文污染分析](../../03_AI/methodology/2026-08-14-context-pollution-repeat-execution-analysis.md) · [Ralph 循环](../../03_AI/methodology/2026-08-14-ralph-loop-deepseek-harness-loop-architecture-analysis.md) · [半件事陷阱](./2026-08-17-half-task-trap-end-to-end-delegation-deep-analysis.md)

---

## 📑 目录 (TOC)

- [§0 执行摘要](#§0-执行摘要)
- [§1 命题与框架](#§1-命题与框架)
  - [1.1 三个退化模式的定义与证据](#11-三个退化模式的定义与证据)
  - [1.2 架构根源假设：单上下文的三重角色冲突](#12-架构根源假设单上下文的三重角色冲突)
  - [1.3 分析框架](#13-分析框架)
- [§2 退化模式一：偷懒——完成判定失效](#§2-退化模式一偷懒完成判定失效)
  - [2.1 现象与证据](#21-现象与证据)
  - [2.2 机制：无外部验收的自利完成判定](#22-机制无外部验收的自利完成判定)
  - [2.3 为什么长上下文必然放大](#23-为什么长上下文必然放大)
  - [2.4 Harness 对策](#24-harness-对策)
- [§3 退化模式二：自我偏爱——生成与评估同源](#§3-退化模式二自我偏爱生成与评估同源)
  - [3.1 现象与证据](#31-现象与证据)
  - [3.2 机制：同源偏差](#32-机制同源偏差)
  - [3.3 对抗性验证：独立评审者的必要性](#33-对抗性验证独立评审者的必要性)
  - [3.4 Harness 对策](#34-harness-对策)
- [§4 退化模式三：目标漂移——有损压缩的累积误差](#§4-退化模式三目标漂移有损压缩的累积误差)
  - [4.1 现象与证据](#41-现象与证据)
  - [4.2 机制：信息论视角](#42-机制信息论视角)
  - [4.3 与知识库蒸馏机制的互锁](#43-与知识库蒸馏机制的互锁)
  - [4.4 Harness 对策](#44-harness-对策)
- [§5 统一架构根源与 Anthropic Harness 谱系](#§5-统一架构根源与-anthropic-harness-谱系)
  - [5.1 三重角色冲突模型](#51-三重角色冲突模型)
  - [5.2 与「Harness 即适配层」的延续](#52-与harness-即适配层的延续)
  - [5.3 Anthropic Harness 谱系：每个 Harness 治一个退化](#53-anthropic-harness-谱系每个-harness-治一个退化)
  - [5.4 退化模式 × Harness 对策矩阵](#54-退化模式--harness-对策矩阵)
- [§6 设计原则提炼与知识库自身体系映射](#§6-设计原则提炼与知识库自身体系映射)
  - [6.1 六条设计原则](#61-六条设计原则)
  - [6.2 知识库自身体系的映射](#62-知识库自身体系的映射)
  - [6.3 剩余风险与未解问题](#63-剩余风险与未解问题)
- [§7 结论](#§7-结论)
- [参考资料](#参考资料)
- [素材边界声明](#素材边界声明)
- [Changelog](#changelog)

---

## §0 执行摘要

**单 Agent 在长时间运行、大规模并行、需要对抗性验证的任务上存在三个已知退化模式：偷懒（完成判定放松）、自我偏爱（生成与评估同源）、目标漂移（有损压缩累积误差）。这三个问题不是模型能力问题，而是"单上下文窗口同时承担规划、执行、验证三个角色"的架构局限——三重角色冲突是同一根源的三个投影。** Anthropic 的定制 Harness（Research / Agent Teams / Code Review / 安全审计）本质上是**用架构手段恢复关注点分离**：每个 Harness 针对特定任务类型写死的调度逻辑，恰好各治一个退化模式。核心判断：

1. **三退化模式可归约到"角色冲突"这一统一根源**：规划角色与执行角色共享上下文 → 执行噪音污染规划（目标漂移）；执行角色与验证角色同体 → 自利性完成判定（偷懒 + 自我偏爱）。**单 Agent 架构的退化不是"模型变笨"，而是单一工作记忆被迫兼任三个本应分离的职能。**

2. **Anthropic 的 Harness 谱系是"退化模式 × 架构对策"的实证映射**：Research 用"计划存 Memory + 子 Agent 干净上下文 + 端状态评估"同时治目标漂移与偷懒；Code Review/安全审计用"独立评审者"治自我偏爱；Agent Teams 用"多 Agent 关注点分离"治角色冲突本身。**每个 Harness 不是工程偏好，是对已知退化模式的架构性回应。**

3. **知识库自身的 Agent 系统已无意中实践了大部分对策，但存在一个结构性风险盲区**：每日蒸馏（上下文压缩）正是目标漂移的温床——CowAgent 的长期记忆压缩与 Anthropic"计划必须存 Memory"的教训同构；**需要把"验证对照原始意图"从 OneDayAgent 的论文结论升级为知识库自身的硬性机制**（压缩时保留原始目标锚点）。

4. **可迁移的设计原则共六条**（隔离/外部化/独立评审/无损目标/端状态验收/干净上下文），可作为任何长时程 Agent 系统的架构 checklist。

> **一句话战略定位**：单 Agent 的三退化模式是架构问题的三个投影，Harness 是架构解药；**判断一个 Agent 系统是否成熟，看它是否把规划、执行、验证三个角色从单一上下文窗口中拆了出来**——这正是本工作站的 CowAgent 与 Ralph 循环、三阶段走读体系正在做的事，本文给出理论闭合与盲区清单。

---

## §1 命题与框架

### 1.1 三个退化模式的定义与证据

| # | 退化模式 | 定义 | 用户给出的证据 | 独立印证 |
|:-:|:---------|:-----|:--------------|:---------|
| 1 | **偷懒** | 长上下文中行为退化：任务未完成就宣布完成（覆盖率下降） | 安全审查 50 个检查项查到 20 个就宣布完成 | Anthropic：早期 Research Agent"已有足够结果仍继续/简单查询过度投入"，需显式 effort scaling 规则 [来源: A1] |
| 2 | **自我偏爱** | 评判自己的产出时系统性偏向好评 | 让 Agent 评判自己产出天然给好评 | LLM-as-judge 需独立 judge 评估而非自评；Anthropic 用独立 LLM judge 按 rubric 打分 [来源: A1] |
| 3 | **目标漂移** | 上下文压缩有损，每压缩一次边缘条件/约束细节丢失，优化目标逐渐偏离原始任务 | 时间长了之后 Agent 优化的目标偏离最初任务 | Anthropic：>200K token 截断会丢计划，必须存 Memory；"subagent 输出经文件系统避免传话游戏" [来源: A1] |

**关键区分**：偷懒不是幻觉（不是"编造"而是"提前停止"）；自我偏爱不是能力不足（是评估与生成同源的结构性偏差）；目标漂移不是理解错误（是信息损失随压缩累积）。**三者都是行为层面/信息层面的退化，而非推理层面的失败——这正是"架构局限而非模型能力问题"命题的立足点**。

### 1.2 架构根源假设：单上下文的三重角色冲突

单 Agent 的上下文窗口（context window）是它的**唯一工作记忆**，必须同时承担三个角色：

```text
Single context window (working memory)
    |-> Role 1: PLANNING   (goals, constraints, exit criteria)
    |-> Role 2: EXECUTION  (intermediate results, tool noise, errors)
    |-> Role 3: VERIFICATION (self-check, completion judgment)
```

**三重角色冲突**：

| 冲突对 | 冲突性质 | 退化的退化模式 |
|:-------|:---------|:--------------|
| 规划 × 执行 | 执行噪音（中间结果、失败、无关信息）挤占规划信息（目标/约束）的上下文预算 | **目标漂移**（信噪比下降，目标信号被淹没） |
| 执行 × 验证 | 完成判定由执行者自己做，无独立验收者 | **偷懒 + 自我偏爱**（自利性判定） |
| 规划 × 验证 | 验证标准由规划者定义且不随执行更新 | 偷懒的变体（验收标准过时/松弛） |

**第一性原理类比**：人类的长任务执行依赖"工作记忆外部化"——书写、清单、备忘录、他人评审。工作记忆容量有限（认知科学 7±2 经典结论），**长任务必然要求把规划/执行/验证拆到不同载体**。Agent 的上下文窗口就是工作记忆，长任务同样必然要求拆分——**不拆，就退化**。这是架构层面的必然性，不是模型层面的偶然性。

### 1.3 分析框架

```text
Degeneration (phenomenon)    Root cause (mechanism)          Harness countermeasure (Anthropic)
--------------------------------------------------------------------------
1 Laziness                   exec x verify conflict          end-state eval + effort scaling + external gate
2 Self-bias                  exec == verify                  independent reviewer (Code Review/security audit/LLM judge)
3 Goal drift                 plan x exec share context       plan in Memory + clean-context subagents + verify vs original intent
--------------------------------------------------------------------------
Unified root: single-context triple-role conflict  ->  solution: Harness restores separation of concerns
```

---

## §2 退化模式一：偷懒——完成判定失效

### 2.1 现象与证据

- **用户证据**：安全审查 50 个检查项查到 20 个就宣布完成——不是漏检，是**提前宣布完成**
- **Anthropic 独立印证**：多 Agent Research 系统早期失败模式包括"agent 在已有足够结果时仍继续"（过度投入）和"简单查询过度投资"（资源误配）——Anthropic 的解法是在 prompt 中嵌入 **effort scaling 规则**（简单事实查询=1 agent 3-10 次工具调用；直接对比=2-4 子 agent 10-15 次调用；复杂研究=10+ 子 agent 明确分工）[来源: A1]
- **知识库印证**：[CommBench 深度分析](../../02_rd/02_project/01_superpod/2026-08-07-commbench-agentic-gpu-sysprog-deep-analysis.md) 中"迭代精炼买的不止正确性还有性能"——Agent 的完成判定天然偏早，需要外部迭代信号

### 2.2 机制：无外部验收的自利完成判定

偷懒的机制不是"想偷懒"（Agent 无动机），而是**完成判定的结构缺陷**：

```text
Single agent completion judgment:
  agent defines "done" -> agent checks "done" -> agent declares "done"
  = executor is also the inspector
  -> completion standard relaxes during execution ("good enough")
  -> coverage depends on how explicit check items are in context
  -> check items compressed/forgotten -> looser standard -> earlier "done"
```

**与幻觉的关键区别**：幻觉是"生成了不存在的事实"；偷懒是"该做的检查没做但宣称做了"。幻觉是生成层错误，偷懒是**执行控制层错误**——后者更接近"行为退化"而非"认知错误"，因此**模型升级不能根治，必须架构干预**。

### 2.3 为什么长上下文必然放大

长上下文对偷懒的放大路径：

1. **检查项衰减**：50 个检查项在长上下文中被压缩/移位，Agent 实际"看得见"的检查项变少 → 完成判定基于残缺清单
2. **注意力稀释**：长上下文注意力分散，已完成的检查项（前 20 项）显著性高于未完成的（后 30 项）→ 判定偏向"已完成部分"
3. **完成信号强化**：Agent 的"完成宣布"会触发流程推进（工具关闭、摘要生成）——**完成本身产生正反馈**，与"继续检查"的负反馈（更多 token 成本）相比，Agent 天然倾向完成

### 2.4 Harness 对策

| 对策 | 机制 | 来源 |
|:-----|:-----|:-----|
| **端状态评估**（end-state evaluation） | 不评判过程，只评判最终状态是否达成；复杂流程拆离散检查点 | Anthropic：对多轮改状态的 Agent 用端状态评估 [来源: A1] |
| **effort scaling 规则** | prompt 内显式规定不同复杂度任务应投入的 agent 数/工具调用数 | Anthropic：Scale effort to query complexity [来源: A1] |
| **外部验收门禁** | 完成判定交给独立组件（check gate/测试/人工）而非 Agent 自判 | 知识库：[Ralph 循环](../../03_AI/methodology/2026-08-14-ralph-loop-deepseek-harness-loop-architecture-analysis.md)（Plan→Do→Check→Act 循环验证） |
| **检查项显式化** | 检查项写入外部清单（文件/Memory）而非依赖上下文残留 | 知识库：[ticket-as-spec](../../03_AI/methodology/2026-08-13-ticket-as-spec-high-throughput-engineer-methodology.md)（exit criteria 显式化） |

---

## §3 退化模式二：自我偏爱——生成与评估同源

### 3.1 现象与证据

- **用户证据**：让 Agent 评判自己的产出，天然给好评——严格验证场景（安全审查、代码审查）致命
- **Anthropic 独立印证**：LLM-as-judge 评估"用独立 judge 按 rubric 打分（事实准确性/引用准确性/完整性/来源质量/工具效率）"，且"单次调用单个 prompt 输出 0.0-1.0 分数 + pass/fail 最稳定" [来源: A1]
- **知识库印证**：三阶段走读体系将安全审查设为**独立阶段三**（`codereview-mantis-security` 安全审查技能）——不是让作者自查，而是专门的威胁建模→漏洞挖掘→误报过滤流水线

### 3.2 机制：同源偏差

自我偏爱的机制是**评估与生成共享同一套参数与同一段上下文**：

```text
Self-evaluation:
  Generator: P(output | context, theta)
  Evaluator: P(score | output, context, theta)   <- same theta, same context
  -> Evaluator inherits Generator's systematic bias
  -> evaluation is not "objective measurement" but "self-consistency check"
  -> bias on own output: fluency=correctness, style=quality, confidence=fact
```

**这不是"Agent 想护短"**，而是 LLM 评估自身输出时，缺乏独立证据基准——评估者与生成者共享权重，评估必然偏向"与生成者认知一致"的结果。**对抗性验证（adversarial verification）的本质：让验证者与生成者解耦，验证者才有动机/能力发现生成者的错误**。

### 3.3 对抗性验证：独立评审者的必要性

三个层次的独立度：

| 层次 | 实现 | 对抗性强度 |
|:-----|:-----|:----------:|
| 同上下文自评 | Agent 检查自己的输出 | 最低（自我偏爱） |
| 独立上下文自评 | 新会话/新 prompt 让同一模型评审 | 中（模型级同源偏差仍在） |
| **独立评审者** | 不同模型/不同角色/不同标准（红队、专门审查 Agent） | 最高（真正的对抗性） |

**Anthropic 的实践**：Research 系统的评估不是让 Research Agent 自评，而是独立的 LLM judge + 人工测试；安全/代码审查同理——**评审者是独立角色** [来源: A1]。

### 3.4 Harness 对策

| 对策 | 机制 | 来源 |
|:-----|:-----|:-----|
| **独立评审者** | 审查 Agent 与执行 Agent 分离，不同上下文、不同标准、甚至不同模型 | Anthropic Code Review / 安全审计 Harness [来源: 公开产品信息] |
| **LLM-as-judge 独立打分** | 按 rubric 打分（0.0-1.0 + pass/fail），judge 与生成者分离 | Anthropic Research eval 实践 [来源: A1] |
| **红队/对抗角色** | 安全审查用"攻击者视角"（威胁建模→漏洞挖掘），而非"作者视角" | 知识库：`mantis` 安全审查流水线 |
| **人工终审** | 高风险场景人签收（"你敢为这个结果负责吗"） | 知识库：[心智模型分析](./2026-08-17-ai-mental-models-by-population-deep-analysis.md)（怀疑论补丁） |

---

## §4 退化模式三：目标漂移——有损压缩的累积误差

### 4.1 现象与证据

- **用户证据**：上下文压缩有损，每压缩一次边缘条件/约束细节丢一点；长时间后 Agent 优化目标偏离原始任务
- **Anthropic 独立印证**：
  - "如果上下文窗口超过 200,000 token 会被截断，**保留计划很重要**"——Research Agent 必须把计划存到 Memory [来源: A1]
  - "子 Agent 输出到文件系统避免传话游戏（game of telephone）"——多级传递导致信息失真，用外部持久化 + 轻量引用替代 [来源: A1]
  - "长时程会话管理：Agent 总结已完成阶段存入外部记忆；上下文接近上限时派发**干净上下文的子 Agent**" [来源: A1]
- **知识库印证**：[OneDayAgent](../../03_AI/agent-engineering/2026-08-07-onedayagent-long-horizon-harness-deep-analysis.md) 的"**压缩阈值化**"与"**验证对照原始意图**"——压缩有损的对策就是阈值触发 + 对照原始目标验证

### 4.2 机制：信息论视角

目标漂移的本质是**有损压缩的信息损失累积**：

```text
Compression chain (each step is lossy):
  Original goal G0 -> summary G1 -> summary G2 -> ... -> Gn
  Loss per step: d_i = H(G_{i-1}) - H(G_i | G_{i-1})  (conditional info loss)
  Cumulative: total loss = sum(d_i)
  -> edge conditions (low-prob / long-tail constraints) lost first (compression keeps high-freq)
  -> constraint details lost -> goal boundary relaxes -> goal drift
```

**为什么边缘条件最先丢**：压缩算法/摘要机制本质是保高频弃低频——约束条件（"除了 X 情况"、"必须在 Y 条件下"）是低频信息，天然是压缩的首批牺牲品。**目标漂移不是"Agent 忘了目标"，是"目标的高频核心保住了、低频约束丢了"，而低频约束往往正是任务成败的关键**（安全审查的边界条件、合规的特殊场景）。

### 4.3 与知识库蒸馏机制的互锁

知识库自身的每日蒸馏（23:50 记忆蒸馏）与 CowAgent 的长期记忆压缩，与目标漂移同构：

| 知识库机制 | 目标漂移风险 | 已有缓解 |
|:-----------|:------------|:---------|
| 每日记忆蒸馏（memory/ 压缩） | 当日细节/边缘条件丢失 | memory 保留原始 log；蒸馏后人工可回溯 |
| 上下文压缩（会话摘要） | 用户原始需求细节丢失 | [上下文污染分析](../../03_AI/methodology/2026-08-14-context-pollution-repeat-execution-analysis.md) 已识别 |
| MEMORY.md 管控（≤5KB + 人工维护） | 长期目标漂移 | 人工审核门禁（天然防漂移） |

**关键洞察**：知识库用"人工审核"（RULE.md：MEMORY.md 仅人工维护）挡住了目标漂移的最严重形态——但这是**人工成本换来的**。OneDayAgent 的"验证对照原始意图"是自动化版本，**知识库的 Agent 长任务执行（深度分析多轮）同样需要这个机制**。

### 4.4 Harness 对策

| 对策 | 机制 | 来源 |
|:-----|:-----|:-----|
| **计划外部化** | 计划/目标写入 Memory（外部存储），不依赖上下文残留 | Anthropic：>200K 截断前计划存 Memory [来源: A1] |
| **验证对照原始意图** | 每次里程碑对照原始目标验证，而非对照上一步摘要 | OneDayAgent [来源: 知识库 08-07] |
| **子 Agent 干净上下文** | 上下文接近上限时派发干净子 Agent，交接保持连续性 | Anthropic 长时程会话管理 [来源: A1] |
| **防传话游戏** | 子 Agent 输出到文件系统 + 传轻量引用，不经过主 Agent 逐字转述 | Anthropic subagent artifact 模式 [来源: A1] |
| **压缩阈值化** | 压缩由阈值触发（而非固定步数），压缩前保留原始目标锚点 | OneDayAgent [来源: 知识库 08-07] |

---

## §5 统一架构根源与 Anthropic Harness 谱系

### 5.1 三重角色冲突模型

综合 §2-§4，三退化模式统一归因于**单上下文窗口的三重角色冲突**：

```text
+--------------------------------------------------------------+
| Single Agent, single context window                          |
|                                                              |
|  Role 1: PLANNING    (goal/constraints/exit criteria)         |
|  Role 2: EXECUTION   (tool calls/results/errors)              |
|  Role 3: VERIFICATION (self-check/completion judgment)        |
|                                                              |
|  Conflict 1-2: planning polluted by execution -> DRIFT        |
|  Conflict 2-3: executor judges itself       -> LAZINESS       |
|                                               + SELF-BIAS    |
+--------------------------------------------------------------+
```

**推论**：任何"单 Agent + 单上下文 + 长任务"系统必然在这三个退化模式上暴露问题，只是时间尺度不同（短任务未及暴露，长任务必然暴露）。**这不是悲观结论，而是设计前置条件——知道退化必然发生，才需要 Harness**。

### 5.2 与「Harness 即适配层」的延续

[Harness 即适配层](../../03_AI/agent-engineering/2026-08-05-harness-os-process-boundary-isomorphism.md) 论证了"Agent = LLM 语义引擎 × 进程执行引擎，Harness 是适配胶水；工具收窄与 Subagent 化是进程边界的必然投影"。**本文是它的自然延续**：

| 08-05 论断 | 本文补充 |
|:-----------|:---------|
| Subagent 化 = 进程边界的投影 | Subagent 化 = **上下文隔离**——每个子 Agent 有干净上下文，从架构上分离关注点 |
| 工具自由度收窄（PTC） | 角色分离（规划/执行/验证）也是"自由度收窄"的一种——收窄到单一角色 |
| 故障域隔离（进程崩溃不炸系统） | **信息域隔离**——目标漂移被隔离在子 Agent 内，主 Agent 目标不污染 |

**统一命题**：Harness 的本质是**边界管理**——进程边界管故障，上下文边界管信息，角色边界管判断。三退化模式是"角色边界缺失"的症状，Harness 是恢复边界的手术。

### 5.3 Anthropic Harness 谱系：每个 Harness 治一个退化

| Harness | 目标任务类型 | 调度逻辑 | 主要对抗的退化 |
|:--------|:------------|:---------|:--------------|
| **Research**（2025-06） | 开放研究（搜索/综合） | orchestrator-worker：LeadResearcher 规划 + 并行 Subagents 探索 + CitationAgent 引用；计划存 Memory；effort scaling；端状态评估 | **目标漂移 + 偷懒** |
| **Agent Teams**（2025-10） | 多 Agent 协作（复杂任务拆解） | 用户创建多个可配置 Agent（指令/工具/模型），并行工作 + 交接；Docker 沙箱隔离 | **角色冲突本身**（关注点分离的产品化） |
| **Code Review** | 代码审查 | 独立审查角色（Claude Code review 工作流），reviewer 与 author 分离 | **自我偏爱** |
| **安全审计** | 安全漏洞扫描 | 攻击者视角/红队式审查，威胁建模→漏洞挖掘 | **自我偏爱**（最强对抗性） |

**关键观察**：Anthropic 没有做"通用超 Agent"，而是**按任务类型写死调度逻辑**——每个 Harness 是"任务特征 → 退化风险 → 调度对策"的定制映射。这印证了用户的判断："每个都是针对特定任务类型写死的调度逻辑"——**通用 Agent 是幻觉，定制 Harness 是现实**。

### 5.4 退化模式 × Harness 对策矩阵

| 退化模式 | 架构根源 | Anthropic Harness 对策 | 知识库已有对策 |
|:---------|:---------|:----------------------|:---------------|
| 偷懒 | 执行×验证冲突 | 端状态评估 + effort scaling | Ralph 循环 + ticket-as-spec exit criteria |
| 自我偏爱 | 执行×验证同体 | Code Review/安全审计独立评审者 | 三阶段走读 + mantis 安全审查 |
| 目标漂移 | 规划×执行共享上下文 | 计划存 Memory + 子 Agent 干净上下文 + 防传话游戏 | OneDayAgent 验证对照原始意图 + 人工审核门禁 |

---

## §6 设计原则提炼与知识库自身体系映射

### 6.1 六条设计原则

从 Anthropic 实践 + 知识库互锁提炼的 **Harness 设计 checklist**（MECE）：

```text
P1 Isolate:        plan/exec/verify roles -> separate contexts/agents
P2 Externalize:    plan/goal/check items -> write to Memory/file, not context residue
P3 Adversarial:    verifier decoupled from generator, different context/standard/model
P4 Lossless goal:  compression keeps original goal anchor, verify vs original intent
P5 End-state gate: completion judged by external check gate, not agent self-judgment
P6 Clean context:  long tasks spawn clean-context subagents, handoff not accumulation
```

### 6.2 知识库自身体系的映射

| 原则 | 知识库现状 | 差距 |
|:-----|:-----------|:-----|
| P1 隔离 | 深度分析走 knowledge-doc-writer 6 步工作流（角色分离） | ✅ 基本满足 |
| P2 外部化 | 计划写在对话 + 记忆写入 memory/ | 🟡 计划主要靠对话残留，未显式存 Memory |
| P3 独立评审 | 三阶段走读 + doc-final-check 门禁（独立脚本） | ✅ 满足 |
| P4 无损目标 | 用户原始需求在对话压缩后无自动锚点 | 🔴 **盲区**（见 6.3） |
| P5 端状态验收 | Ralph 循环 + check gate + 未落盘=未完成铁律 | ✅ 满足 |
| P6 干净上下文 | 会话压缩/续传机制 | 🟡 部分满足（session-keeper） |

### 6.3 剩余风险与未解问题

1. **P4 盲区（最高优先）**：知识库深度分析任务中，用户原始需求经过多轮对话压缩后，Agent 可能优化"文档格式合规"而非"用户真正要的结论"——**建议：长任务起点写入"原始目标锚点"（用户命题原文），里程碑对照锚点验证**（OneDayAgent 的"验证对照原始意图"机制化）
2. **自我偏爱的残余**：知识库深度分析的自检（`light-self-review` 自审技能）仍是同模型自审——独立评审（doc-reviewer/另一模型）应作为高风险文档的可选门禁
3. **偷懒的量化检测**：目前"50 项查 20 项"无自动检测——可借鉴 Anthropic 的 effort scaling：为深度分析定义最小工具调用/检索/读写轮数下限（RULE.md 已定 ≥3 次工具调用，可细化）
4. **Agent Teams 的全量一手验证**：本文 Agent Teams/Code Review/安全审计为公开产品信息（抓取受限），待后续补全文

---

## §7 结论

**单 Agent 的三退化模式（偷懒/自我偏爱/目标漂移）不是模型能力问题，而是单上下文窗口同时承担规划、执行、验证三重角色的架构局限——三重角色冲突是同一根源的三个投影。** Anthropic 的定制 Harness 谱系（Research/Agent Teams/Code Review/安全审计）实证了"退化模式 → 架构对策"的映射：独立评审治自我偏爱、端状态评估治偷懒、计划外部化治目标漂移。**判断 Agent 系统成熟度的标准：是否把规划、执行、验证从单一上下文窗口中拆了出来。** 知识库自身体系已实践大部分原则，但存在一个结构性盲区——长任务的目标锚点未显式外部化，这是下一轮系统演进的第一优先级。

---

## 参考资料

[1] Anthropic Engineering — *How we built our multi-agent research system*（2025-06-13，全文抓取）：https://www.anthropic.com/engineering/built-multi-agent-research-system [来源: A1]

[2] Anthropic — Claude Agent Teams（2025-10 公开产品信息，抓取受限，未全文核验） [来源: 公开产品信息]

[3] Anthropic — Claude Code / Claude Security（Code Review 与安全审计 Harness，公开产品信息） [来源: 公开产品信息]

[4] 知识库互锁：[Harness 即适配层](../../03_AI/agent-engineering/2026-08-05-harness-os-process-boundary-isomorphism.md) · [OneDayAgent](../../03_AI/agent-engineering/2026-08-07-onedayagent-long-horizon-harness-deep-analysis.md) · [CowAgent 问题清单](../../03_AI/methodology/2026-08-14-cowagent-system-problems-full-inventory.md) · [上下文污染](../../03_AI/methodology/2026-08-14-context-pollution-repeat-execution-analysis.md) · [Ralph 循环](../../03_AI/methodology/2026-08-14-ralph-loop-deepseek-harness-loop-architecture-analysis.md) · [半件事陷阱](./2026-08-17-half-task-trap-end-to-end-delegation-deep-analysis.md) · [心智模型](./2026-08-17-ai-mental-models-by-population-deep-analysis.md)

## 素材边界声明

- **一手来源**：Anthropic multi-agent research system 工程博客全文（2025-06-13）——本文 Research Harness 相关结论的全部依据
- **公开产品信息**：Agent Teams / Code Review / 安全审计 Harness 为公开产品功能（claude.com/docs.claude.com 当前抓取受限），其架构描述基于公开认知，**未做全文核验**——标注 [来源: 公开产品信息]
- **用户命题**：三退化模式的定义与证据来自用户（与 Anthropic 实践独立印证，强化可信度）
- **知识库互锁**：OneDayAgent/CowAgent/Ralph/上下文污染等为知识库已有深度分析结论，交叉引用
- **数据条件**：Anthropic 的量化数据（90.2% 提升、80% 方差、4×/15× token）来自其内部 eval（BrowseComp 等），条件为其内部测试环境

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-17 | v1.0 | 首次创建：三退化模式机制分析（偷懒/自我偏爱/目标漂移）+ 统一架构根源（单上下文三重角色冲突）+ Anthropic Harness 谱系映射 + 六条设计原则 + 知识库盲区清单 |
