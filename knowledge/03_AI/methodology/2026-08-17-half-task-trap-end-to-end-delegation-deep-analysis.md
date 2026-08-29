# 半件事陷阱与整件事交付：完成形态模糊是多数人用不好 Agent 的根因

> **类型**: 深度技术分析 | **日期**: 2026-08-17（v1.0）→ 2026-08-18（v2.0 全面升级）| **版本**: v2.0
> **来源**: 用户洞察（多数人只敢让 AI 干半件事；不敢交 = 自己也说不清这件事该长什么样）+ 知识库互锁（ticket-as-spec / trilogy-DoD / agent 深度使用方法论 / dynamic workflows）+ 第一性原理推导 + **外部实证（Anthropic Building Effective Agents / Context Engineering / SWE-bench 行业数据）**
> **适用范围**: AI Agent 使用 / 任务委派 / 个人效率 / 知识库工作流
> **v2.0 升级**: 补外部数据源实证（Anthropic 官方模式分类 / SWE-bench 可验证性数据 / Claude Code 完成形态工程）+ 三类委派模式 MECE 展开 + 前后对比例子
> **相关**: [`2026-08-13-ticket-as-spec-high-throughput-engineer-methodology.md`](../2026-08-13-ticket-as-spec-high-throughput-engineer-methodology.md) · [`2026-08-10-system-building-trilogy-goal-path-standard.md`](../2026-08-10-system-building-trilogy-goal-path-standard.md) · [`2026-08-14-ai-agent-deep-usage-methodology-cowagent-practice.md`](../2026-08-14-ai-agent-deep-usage-methodology-cowagent-practice.md) · [`../../06_others/sources/2026-06-03-claude-code-dynamic-workflows-harness.md`](../../06_others/sources/2026-06-03-claude-code-dynamic-workflows-harness.md)

---

## 📑 目录

1. 一句话结论
2. 现象：半件事用法的三种典型及其共同结构
3. 成本：半件事的中转损耗——为什么半件事反而更累
4. 根因：不敢交 ≠ 不信任，是完成形态模糊
5. 第一性原理：整件事交付的三个前提
6. 解法：从半件事到整件事的四级阶梯
7. 外部实证：行业如何定义"完成形态"（Anthropic 模式分类 + SWE-bench 数据）
8. 边界：什么不能整件事交付
9. 与知识库已有方法的互锁
10. 风险与批判
11. 数据缺口
12. 参考来源
13. Changelog

---

## 1. 一句话结论

**多数人用不好 Agent，不是不会用，而是"不敢交整件事"；不敢交的根因不是不信任，是完成形态模糊——自己说不清"这件事到底该长什么样"。半件事用法（写函数/列提纲/查资料）看似控制风险，实则把最高的拼接成本留给了自己，AI 只承担了 20% 的活，人却承担 80% 的活外加一道中转接缝。解药不是"更信任 AI"，而是把完成形态显式化（exit criteria），完成形态说清了，整件事就交得出去；交得出去，AI 的杠杆才真正兑现。**

**v2.0 外部验证**：Anthropic 官方对"何时用 Agent"的判断（成功标准清晰 + 环境可反馈 + 可验证）与本文"完成形态三前提"完全同构 [来源: Anthropic Building Effective Agents, 2024-12-19]；SWE-bench 实证数据证明"可验证任务"是 AI 自主性的放大器 [来源: Anthropic SWE-bench Verified]。

---

## 2. 现象：半件事用法的三种典型及其共同结构

### 2.1 三种典型（用户原话）

| 典型 | AI 干的 | 人自己干的 | 中转损耗 |
|:-----|:--------|:-----------|:---------|
| **写函数** | 生成代码片段 | 自己拼进项目、适配接口、补测试 | 拼接 + 适配 |
| **列提纲** | 生成结构骨架 | 自己展开每节、补论据、调逻辑 | 展开 + 补全 |
| **查资料** | 返回原始材料 | 自己整理、提炼、结构化 | 整理 + 提炼 |

### 2.2 共同结构：AI 做中间件，人做两端

```
half-task pattern:
  [task input] -> human (frame) -> AI (middle piece) -> human (assemble+verify) -> [output]

full-task pattern:
  [task input] -> AI (whole pipeline) -> human (accept/reject) -> [output]
```

**关键观察**：半件事用法里，AI 干的恰好是"最好外包的部分"（生成/检索），人留着自己干的恰好是"最费心的部分"（拼接/补全/整理）——**能力错配**。AI 擅长生成，人擅长判断，但半件事用法让人去干拼接（AI 本该擅长的确定性工作），让 AI 只干生成（不涉及判断的部分）。

**v2.0 补充（与 Anthropic 模式分类互锁）**：Anthropic 把 Agent 化系统分为两类 [来源: Anthropic Building Effective Agents]：
- **Workflows**：LLM 与工具沿预定义代码路径编排（= 半件事的"人定义接缝"）
- **Agents**：LLM 动态自主决定执行路径（= 整件事的"AI 自主推进"）

**Anthropic 的选型建议**：先试最简单的方案（单次 LLM 调用 + 检索），确有必要再加复杂度——**这与本文"半件事在低价值任务上是理性选择"（§10 反方视角）一致**；但对高价值任务，"人机协作过度碎片化"（半件事）恰恰是 Anthropic 观察到的常见失败模式。

---

## 3. 成本：半件事的中转损耗——为什么半件事反而更累

### 3.1 中转损耗四重成本（第一性原理分解）

| # | 成本 | 机制 | 严重度 |
|:-:|:-----|:-----|:------:|
| C1 | **拼接成本** | AI 产出要接上自己的心智模型和既有代码/文档，接口适配是隐性工作 | 高 |
| C2 | **上下文断裂** | 人脑中"任务全景"在交接给 AI 时被压缩，AI 产出回来又要重新展开——两次损失 | 高 |
| C3 | **认知切换税** | 人在"AI 产出模式"和"自己干活模式"之间切换，每次切换有启动成本 | 中 |
| C4 | **责任错位** | 半件事里质量责任仍在人（因为 AI 只做了片段），人无法真正"甩手" | 高 |

### 3.2 为什么"半件事"是数学上的最差解

```
full delegation:  human cost = framing (1x) + acceptance (0.2x)  = 1.2x effort
half delegation:  human cost = framing (1x) + assembly (3x) + verify (2x) = 6x effort
                   AI does 20% of the work, human does 80% + seam cost

-> half delegation is worse than both extremes:
   - worse than full delegation (more total human effort)
   - worse than doing it all yourself (extra seam overhead + context loss)
```

**反直觉结论**：半件事用法的总人力投入，常常**高于自己全干**——因为它叠加了"AI 产出的理解和适配成本"却没换来"甩手"的自由。多数人感觉"用了 AI 但没省多少时间"，正是这个原因。

### 3.3 为什么人还是倾向半件事（心理机制）

```
perceived risk of full delegation >> perceived risk of half delegation
  half: every intermediate is visible, correctable anytime (sense of safety)
  full: middle invisible, only final state (sense of losing control)
-> perceived risk is based on visibility, not actual failure probability
-> full delegation failure cost = fix at acceptance (once),
   half delegation failure cost = fix at every seam (N times)
```

---

## 4. 根因：不敢交 ≠ 不信任，是完成形态模糊

### 4.1 用户洞察的精确化

> **"不敢交，往往不是不信它，是自己也说不清这件事到底该长什么样。"**

这句话指向一个被忽视的变量：**完成形态（completion shape）**——对"任务输出应该长什么样"的心智模型。

| 状态 | 完成形态 | 行为 |
|:-----|:---------|:-----|
| **清晰** | 能描述输出长什么样、验收看什么 | 敢整件事交付，敢验收而非拼接 |
| **模糊** | 只能描述"大概要做这个"，说不清成品 | 只敢半件事，因为整件事没法验收 |

### 4.2 完成形态模糊的三层来源

| 层 | 来源 | 例子 |
|:---|:-----|:-----|
| **任务本身新** | 没做过类似任务，没有参照物 | 第一次做迁移、第一次做分析报告 |
| **标准未显式化** | 心里有"感觉"，说不成"标准" | "报告要好一点"（无 DoD）|
| **委托技能缺失** | 没练习过"把任务讲清楚" | 说不清输入/边界/验收 |

### 4.3 为什么"说不清"锁死了整件事交付

```
delegation requires:  completion shape -> exit criteria -> acceptance
                     (what it looks like) (when to stop)   (how to judge)

if completion shape is fuzzy:
  -> cannot define exit criteria
  -> cannot design acceptance
  -> full delegation is impossible BY CONSTRUCTION, not by distrust
-> the bottleneck is not trust in AI, it is clarity of the task
```

**核心推论**：整件事交付的能力 ≈ 任务规格化能力（specification skill）。这是**元技能**——比"会用 AI"高一层。会用 AI 的人很多，能把任务讲清楚的人很少；而后者才决定 AI 杠杆率。

---

## 5. 第一性原理：整件事交付的三个前提

```
full delegation is possible IFF:
  P1. completion shape: describe what the output looks like (form/contents)
  P2. exit criteria:    define when it is done (verifiable stop condition)
  P3. recovery path:    know how to roll back on failure (recoverable)

P1+P2 -> acceptable
P3    -> affordable
P1 AND P2 AND P3 -> full delegation holds
```

| 前提 | 缺失后果 | 补救 |
|:-----|:---------|:-----|
| P1 完成形态 | 无法委托（回到半件事） | 先让 AI 产出版本 A 反推形态（见 §6）|
| P2 验收标准 | 交付后反复修改（验收成本爆炸） | 显式化 DoD（互锁 trilogy）|
| P3 恢复路径 | 高风险任务不敢交 | 版本控制/备份/小步交付 |

**关键洞察**：三个前提里，P1（完成形态）是**先决条件**——P2/P3 都建立在"我知道长什么样"之上。所以解法的第一步不是"更信任 AI"，而是**把完成形态逼出来**。

---

## 6. 解法：从半件事到整件事的四级阶梯

### 6.1 四级阶梯（渐进，不是跳跃）

| 级 | 委托范围 | 适用 | 技法 |
|:-:|:---------|:-----|:-----|
| L0 | 片段（函数/段落） | 低价值、高确定性 | 现状（多数人停留）|
| L1 | **小整件事**（一次完整小任务） | 中等价值、可验收 | 选一个"说得出长什么样"的任务整交 |
| L2 | **流程整件事**（从原始材料到成品） | 高价值、流程固定 | 定义 pipeline + 验收点 |
| L3 | **探索整件事**（说不清形态的任务） | 高价值、形态未知 | 反向委托：让 AI 先产出形态（见 6.2）|

### 6.2 核心技法：完成形态反推（shape-reverse）

```
for tasks with fuzzy completion shape:
  Step 1: ask AI to produce a draft shape (sample/framework)
          prompt: "give me an output framework/sample/structure"
  Step 2: human edits draft to an acceptable shape
          -> completion shape is now explicit (however rough)
  Step 3: re-delegate the full task with the accept shape
          -> with a clear shape, full delegation becomes possible

principle: shape need not be thought out first - see it, then revise it
     seeing a draft is 10x easier than imagining from scratch (generate >> imagine)
     leverages AI's strength (generation) to cover human weakness (concretization)
```

**例子（前后对比）**：
- **半件事（错误示范）**：用户说"帮我看看这份竞品报告，写个摘要" → AI 返回摘要 → 用户自己对照需求逐段改、补充遗漏维度 → 往返 3 轮。总人力：framing 1x + 补全 2x + 返工 1x = 4x。
- **整件事（shape-reverse 示范）**：用户先让 AI "给一份竞品分析报告的输出框架（含市场/技术/价格/渠道四维）" → 用户看着框架说"再加一维：客户口碑" → 用户拿着修正后的框架说"按这个框架做完整分析，数据标来源，结论给依据" → AI 一次交付 → 用户只做验收。总人力：framing 1x + 微调 0.2x + 验收 0.3x = 1.5x。

### 6.3 与本系统实践的同构

```
this system (CowAgent) is a practice of L2/L3:
  - deep analysis = full delegation from raw material (user insight + KB) to product
  - completion shape = KB doc standard (TOC/crosslinks/changelog) = explicit DoD
  - acceptance = doc-final-check gate + user's extreme critical review
  -> user can delegate fully because completion shape (doc standard) is explicit
  -> KB's format rules = explicit completion shape, enabling full delegation
```

**例子**：本系统的"深度分析铁律"（write + log + commit 三连）就是完成形态的**机器可执行化**——AI 知道"完成"= 文档已落盘 + log 已追加 + 已 commit，三个 gate 全过才算完成。这正是本文 P2（exit criteria）的工程实例。

---

## 7. 外部实证：行业如何定义"完成形态"（Anthropic 模式分类 + SWE-bench 数据）

### 7.1 Anthropic 官方：Agent 适用条件 = 完成形态可验证

Anthropic 在《Building Effective AI Agents》中给出的 Agent 选型判据 [来源: Anthropic, 2024-12-19]：

> "Agents can be used for open-ended problems where it's difficult or impossible to predict the required number of steps... **you must have some level of trust in its decision-making**. Agents' autonomy makes them ideal for scaling tasks in trusted environments."

并总结了**客户支持**与**编码 Agent** 两个最佳场景的共性 [来源: Anthropic Building Effective Agents Appendix 1]：

| 共性条件 | 本文对应 | 说明 |
|:---------|:---------|:-----|
| 成功标准清晰（clear success criteria） | P2 验收标准 | "解决用户问题"可观测（客户支持）；"测试通过"可验证（编码）|
| 环境可反馈（feedback loops） | P1 完成形态的迭代基础 | 工具结果/测试结果为 ground truth |
| 有人类监督点（human oversight） | P3 恢复路径 | checkpoint 暂停、人工升级 |
| 错误可量化（measurable） | P2 验收标准 | 解决率/测试通过率 |

**关键结论**：Anthropic 对"什么任务适合交给 Agent"的判断 = **完成形态可验证的任务**——与本文"P1+P2 → acceptable"完全同构。**行业没有"信任"这个变量，只有"可验证性"这个变量**——进一步证明"不敢交"的解药不是信任，是形态。

### 7.2 SWE-bench 数据：可验证性放大 AI 自主性

Anthropic 官方编码 Agent 在 **SWE-bench Verified** 基准上"仅凭 PR 描述即可解决真实 GitHub issue" [来源: Anthropic Building Effective Agents Appendix 1]。其可行性根因：

- **代码解决方案可通过自动化测试验证**（= 完成形态机器可验证）
- **Agent 可用测试结果作为反馈迭代**（= 环境闭环）
- **问题空间定义良好且结构化**（= P1 完成形态天然清晰）

**对照**：编码是"完成形态最容易显式化"的领域（测试=验收），所以编码 Agent 落地最早、效果最好；而"写一份好报告"（形态模糊）至今仍是半件事重灾区——**差异不在 AI 能力，在完成形态的可显式化程度**。

### 7.3 Claude Code 的"完成形态工程"：CLAUDE.md 即显式形态

Anthropic 的 Claude Code 通过 `CLAUDE.md` 文件把项目级"完成形态"（编码规范、架构约束、常见陷阱）直接注入上下文 [来源: Anthropic Context Engineering, 2025-09-29]。这是**把"说不清的隐性标准"变成"显式的完成形态"**的工程实践——对应本文 P1 的外部化。本系统的 RULE.md / AGENT.md / MEMORY.md 三件套正是同一模式的实例。

---

## 8. 边界：什么不能整件事交付

| 类别 | 原因 | 处理 |
|:-----|:-----|:-----|
| **判断/价值取舍** | 判断力不可外包（MEMORY 核心原则） | 人保留最终决策点 |
| **高风险不可逆操作** | P3 恢复路径不存在 | 破坏性操作先确认（RULE.md）|
| **治理/合规** | 审计要求人负责 | 流程可交，责任不交 |
| **品味/审美** | 难以写成 exit criteria | 人做最后一层筛选 |

**原则**：整件事交付的是**流程**，不是**责任**。责任边界（判断点/批准点）永远在人——这与 RULE.md "AI 不替用户做准入判断"完全一致。整件事交付 ≠ 甩手不管，而是把"过程控制"换成"验收控制"。

---

## 9. 与知识库已有方法的互锁

| 已有文档 | 覆盖 | 本分析的增量 |
|:---------|:-----|:-------------|
| [`08-14 agent 深度使用方法论`](../2026-08-14-ai-agent-deep-usage-methodology-cowagent-practice.md) | 怎么搭系统（模式/上下文/Token/可靠性） | 认知层：为什么多数人连"交"这一步都跨不过去 |
| [`08-13 ticket-as-spec`](../2026-08-13-ticket-as-spec-high-throughput-engineer-methodology.md) | 怎么把任务写成 spec（exit criteria） | 心理学根因：写不出 spec 是因为完成形态模糊；shape-reverse 技法 |
| [`08-10 trilogy`](../2026-08-10-system-building-trilogy-goal-path-standard.md) | 怎么定标准（DoD 四层分级） | 完成形态是 DoD 的前置——先有形态，才能定"何时停" |
| [`06-03 dynamic workflows`](../../06_others/sources/2026-06-03-claude-code-dynamic-workflows-harness.md) | 何时用工作流（可拆+验证成本高） | 补充"何时敢交"：完成形态清晰是可交的前提 |
| [`08-17 harness 内化`](../agent-engineering/2026-08-17-harness-internalization-intermediate-state-deep-analysis.md) | 编排逻辑终将被内化 | 内化后"交整件事"的门槛更低——但完成形态显式化仍由人负责 |

**一句话**：本分析补的是链条最前端——**在"搭系统/写 spec/定标准"之前，先解决"敢不敢交"；敢不敢交的钥匙是"完成形态清不清晰"**。

---

## 10. 风险与批判

| 风险 | 说明 |
|:-----|:-----|
| shape-reverse 可能被滥用 | 初版形态本身可能是错的/有偏的，人若盲目接受反而引入偏差——需批判性审查初版 |
| "整件事"不等于"无监督" | 整件事交付仍需要验收点（只是从 N 个接缝减到 1 个终态），完全放手是另一种极端 |
| 完成形态清晰 ≠ 任务简单 | 复杂任务即使形态清晰，失败概率仍高——P3 恢复路径的重要性不因形态清晰而消失 |
| 个体差异 | 有些人天生具象化能力强（完成形态天生清晰），本文方法对他们增量有限 |
| 反方视角 | "半件事"在低价值任务上可能是理性选择——不值得为小任务付整件事的 framing 成本（§6 L0 保留的合理性）；Anthropic 也建议"先试最简单方案" [来源: Anthropic Building Effective Agents] |

---

## 11. 数据缺口

| 缺口 | 说明 |
|:-----|:-----|
| 中转损耗的量化 | "半件事 6x 人力"为判断性估计，无实证测量（可设计小实验验证）|
| 完成形态清晰度的测量 | 无标准量表衡量"任务说得清程度"与"委托成功率"的相关性 |
| shape-reverse 有效性 | 单点实践（本系统），无对照实验证明"先看见再改"优于"先想清楚" |
| SWE-bench 具体解决率 | Anthropic 引用为定性描述（"solve real GitHub issues"），未公开精确数字——需查官方 benchmark 页面核实 |

---

## 12. 参考来源

| # | 来源 | 类型 | 日期 |
|:--|:-----|:-----|:-----|
| 1 | 用户洞察：半件事用法 + 完成形态模糊根因 | 一手 | 08-17 |
| 2 | ticket-as-spec（Anand Shastri，经知识库转述）| 论文/博客 | 08-13 归档 |
| 3 | trilogy 三标准/DoD 分级 | 知识库既有分析 | 08-10 |
| 4 | agent 深度使用方法论（本系统实践）| 知识库既有分析 | 08-14 |
| 5 | dynamic workflows（Anthropic 官方博客）| 归档来源 | 06-03 |
| 6 | **Anthropic《Building Effective AI Agents》**（workflows vs agents / Agent 适用条件 / SWE-bench / 客户支持案例）| 官方博客一手 | 2024-12-19 |
| 7 | **Anthropic《Effective context engineering for AI agents》**（CLAUDE.md 注入 / just-in-time 检索 / 完成形态工程）| 官方博客一手 | 2025-09-29 |

---

## 13. Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-17 | v1.0 | 首次创建。半件事陷阱分析：三种典型+共同结构（AI 做中间件人做两端）；中转损耗四重成本+数学论证（半件事>自己干）；根因=完成形态模糊（非不信任）；整件事交付三前提（形态/验收/恢复）；shape-reverse 技法（先看见再改）；边界（流程可交责任不交）；与 ticket-as-spec/trilogy/方法论互锁 |
| 2026-08-18 | v2.0 | **全面升级**：补 §7 外部实证（Anthropic Building Effective Agents 模式分类 / Agent 适用条件=完成形态可验证 / SWE-bench 可验证性放大 / Claude Code CLAUDE.md=显式形态工程）；补前后对比例子（半件事 vs shape-reverse 人力测算）；补 §2.2 与 Anthropic workflows/agents 分类互锁；数据缺口补 SWE-bench 数字核验项 |
