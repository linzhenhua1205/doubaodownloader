# 预研活动的运营机制设计：评价体系 × 技术货架 × 时间投入 × 组织边界

> 元信息: v1.0 | 深度技术分析 | 2026-08-25
> 适用范围: 研发组织技术负责人 / 预研团队 / 研发管理 / 技术货架运营

---

## 目录

- [1. 引言：六个问题是一个问题](#1-引言六个问题是一个问题)
- [2. 核心结论（先给答案）](#2-核心结论先给答案)
- [3. 预研评价体系：期权模型下的六维评价](#3-预研评价体系期权模型下的六维评价)
  - [3.1 第一性原理：预研是买期权，评价的是期权价值](#31-第一性原理预研是买期权评价的是期权价值)
  - [3.2 六维评价框架（MECE）](#32-六维评价框架mece)
  - [3.3 自评-他评机制：预研结论怎么供评价](#33-自评-他评机制预研结论怎么供评价)
  - [3.4 自评报告模板（结论先行）](#34-自评报告模板结论先行)
- [4. 技术货架：预研的资产负债表](#4-技术货架预研的资产负债表)
  - [4.1 货架的本质：把"做过"变成"可复用"](#41-货架的本质把做过变成可复用)
  - [4.2 货架条目三要素：成熟度 + 商业化时间点 + 责任主体](#42-货架条目三要素成熟度--商业化时间点--责任主体)
  - [4.3 货架形成流程与运营规则](#43-货架形成流程与运营规则)
  - [4.4 货架运营 KPI](#44-货架运营-kpi)
- [5. 商业化时间点（TTC）：预研结论的必备项](#5-商业化时间点ttc预研结论的必备项)
  - [5.1 为什么预研必须有 TTC 结论](#51-为什么预研必须有-ttc-结论)
  - [5.2 TTC 的推演方法：TRL 阶段基线 + 关键路径](#52-ttc-的推演方法trl-阶段基线--关键路径)
  - [5.3 TTC 结论的表达格式](#53-ttc-结论的表达格式)
- [6. 跟踪项闭环机制](#6-跟踪项闭环机制)
  - [6.1 跟踪项生命周期状态机](#61-跟踪项生命周期状态机)
  - [6.2 闭环判定的五选一标准](#62-闭环判定的五选一标准)
  - [6.3 跟踪台账与 Review 节奏](#63-跟踪台账与-review-节奏)
- [7. 时间投入机制："白嫖个人时间"困境的破解](#7-时间投入机制白嫖个人时间困境的破解)
  - [7.1 痛点的本质：组织不愿为期权付费](#71-痛点的本质组织不愿为期权付费)
  - [7.2 破解三件套：预算池 + 时间盒 + 成果可见](#72-破解三件套预算池--时间盒--成果可见)
  - [7.3 给个人的现实策略：不空耗、要转化](#73-给个人的现实策略不空耗要转化)
- [8. 组织边界：预研 vs 量产工程 vs 供应链](#8-组织边界预研-vs-量产工程-vs-供应链)
  - [8.1 三层职责划分（MECE）](#81-三层职责划分mece)
  - [8.2 为什么量产工艺不归预研团队](#82-为什么量产工艺不归预研团队)
  - [8.3 内部研发退出机制：支持到可量产后退场](#83-内部研发退出机制支持到可量产后退场)
- [9. 预研运营的季度节奏（PDCA）](#9-预研运营的季度节奏pdca)
- [10. 结论](#10-结论)
- [11. 参考文件](#11-参考文件)
- [变更记录](#变更记录)

---

## 1. 引言：六个问题是一个问题

用户问题可拆为六问，实为**一个机制的六个面**：

```text
(1) how to evaluate pre-research?    -> evaluation system
(2) form technology shelf           -> technology shelf
(3) self-assessment for review      -> self-assessment loop
(4) commercialization timing req    -> TTC (Time-To-Commercialization)
(5) tracking items closed            -> tracking closure loop
(6) time investment dilemma (free personal time) -> resource mechanism
(7) mass-prod/process boundary (pre-research vs supply chain) -> org boundary & exit
```

**一个机制**：预研活动从"启动"到"退场"的全生命周期运营机制——评价什么、沉淀什么、什么时候商业化、谁跟踪、谁投入、谁接手。六问缺一不可：没有评价体系，预研无法被公正衡量；没有货架，预研成果无法复用；没有 TTC，预研永远停在"研究"；没有跟踪闭环，预研转瞬即逝；没有时间机制，预研无法启动；没有边界定义，预研团队被量产消耗殆尽。

本文与库内既有文档的分工：

| 既有文档 | 覆盖层 | 本文补什么 |
|:---------|:-------|:-----------|
| [预研 vs 落地决策分析](2026-08-21-pre-research-vs-landing-decision-analysis.md) | **决策层**：要不要预研、怎么立项、向上管理 | **运营层**：预研启动后怎么评价/沉淀/跟踪/退场 |
| [产品生命周期知识图谱 §3.5](2026-08-11-server-product-lifecycle-org-knowledge-graph.md) | 转化机制三要素（TDT/TR 门禁/路标） | 完整的评价维度、货架机制、TTC 推演、时间投入破解、量产边界 |
| [RD KPI 体系](2026-07-30-server-rd-kpi-system-deep-analysis.md) | 预研转化率 ≥30% 单一指标 | 六维评价框架 + 货架 KPI 体系 |

---

## 2. 核心结论（先给答案）

1. **预研评价的第一性原理是期权模型**：预研是组织用当前资源购买"未来技术选择权"。评价预研不能看"现在赚了多少"（现金流逻辑），要看"期权价值"——决策贡献度、货架贡献度、商业化判断力。用落地尺子丈量预研，是预研被系统性低估的根因 [来源: 库内预研 vs 落地分析 §2.1]。

2. **技术货架是预研的资产负债表**：预研产出 → 货架条目（TRL 成熟度 + 商业化时间点 TTC + 责任主体三要素齐备）→ 按需提取。没有货架的预研 = 做过就忘 = 沉没成本。

3. **商业化时间点是预研结论的必备项**：每个预研结项必须给出 TTC 自评结论（可商业化 / 暂不可 / 不推荐 + 时间区间 + 前提条件）。期权没有行权时间 = 永不行权的期权。

4. **跟踪闭环是预研价值的放大器**：预研结项 ≠ 结束，而是进入跟踪状态机（货架入库 → 挂账 → 跟进 → 落地或关闭）。闭环判定五选一：进入路线图 / 进入立项 / 形成选型基线 / 输出标准提案 / 证伪归档。

5. **"白嫖个人时间"是机制缺陷的表象，不是文化问题**：组织不为期权付费 = 期权永远无法行使。破解靠**小额预算池 + 时间盒 + 成果可见**三件套，而不是喊"鼓励主动投入"的口号。个人层面的现实策略：不空耗，把业余投入转化为可见资产，判断止损。

6. **量产/工艺边界**：预研团队负责"工艺可行性验证"（DFM 验证、样品试制），量产工程负责"量产工艺设计"（产线调配、良率爬坡），供应链负责"量产供货"。内部研发以**能力转移交付物**为退出条件（而非时间），支持到首批量产通过后退场，遗留问题进缺陷库而非靠人盯。

---

## 3. 预研评价体系：期权模型下的六维评价

### 3.1 第一性原理：预研是买期权，评价的是期权价值

```text
Investment logic vs Option logic:

  Investment (landing): invest -> cashflow return, ROI computable
  Option    (pre-research): invest -> gain "future choice right", value at exercise

  Option value = intrinsic value (tech advancement)
               + time value (exercisable within window)
               + volatility value (higher uncertainty = more valuable option)

  Evaluation trap: use investment logic (ROI) to grade options -> 3 errors
    (1) false precision: pre-research return unpredictable, ROI is invented
    (2) narrowed vision: only current business, ignore future options
    (3) attribution error: credit market/timing factors to pre-research
```

预研评价的**正确问题**不是"这个预研赚了多少钱"，而是：

```text
Q1 What do we know now that we did not know before?   (decision value)
Q2 What reusable asset is deposited?                (shelf value)
Q3 How clear is the commercialization judgment?     (TTC quality)
Q4 Did it convert into project/roadmap?             (conversion rate)
Q5 Are tracking items closed?                        (closure rate)
Q6 Was resource spent worth it?                      (efficiency)
```

### 3.2 六维评价框架（MECE）

| 维度 | 评价问题 | 核心指标 | 权重建议 |
|:-----|:---------|:---------|:--------:|
| **D1 决策贡献度** | 是否产出"可决策的选项集合 + 推荐 + 风险"？ | 决策信息增量（是否改变了组织的技术判断） | 25% |
| **D2 货架贡献度** | 是否形成可复用货架条目？TRL 提升几级？ | 入库条目数、TRL 提升幅度 | 20% |
| **D3 商业化判断力** | TTC 结论是否清晰、可推演、有条件？ | TTC 结论完整率（含区间+条件） | 15% |
| **D4 转化成功率** | 是否进入立项/路线图/选型基线？ | 预研转化率 ≥30% [来源: 库内 RD KPI 体系 §3] | 15% |
| **D5 跟踪闭环率** | 跟踪项是否落地到位？ | 闭环率 = 已闭环 / 应闭环 | 15% |
| **D6 投入效率** | 时间盒内是否完成？资源是否浪费？ | 时间盒达成率、单位资源决策信息量 | 10% |

> **权重说明**：D1+D2 合计 45% 锚定"预研的本职"（提供决策信息 + 沉淀资产），D3-D5 合计 45% 锚定"预研的落地"（商业化 + 转化 + 闭环），D6 是效率修正。**D1/D2 是预研区别于落地的核心维度——如果组织只按 D4/D5 打分，等于又拿落地尺子量预研。**

**评分操作**：每维 0-5 分（0=无产出，5=超预期），加权总分作为预研结项评审依据。总分 ≥3.5 结项转货架；2.5-3.5 延期一个时间盒补短板；<2.5 归档（证伪或失败），但**证伪也是有效产出**（避免错误投入）[来源: 库内预研 vs 落地分析 §2.4 退出机制]。

### 3.3 自评-他评机制：预研结论怎么供评价

**自评的意义**：不是自我表扬，而是**把决策信息结构化，降低评价者的校验成本**。评价者（领导/评审委员会）的时间是稀缺资源——自评报告做得好，评价者 10 分钟能完成校验；做不好，评价者只能凭印象打分。

**自评-他评闭环**：

```text
pre-research team
  |-- self-assessment report (conclusion first, incl. TTC)
  |-- submit to review board
  v
review board (external review)
  |-- 3 questions: is conclusion falsifiable? data sourced? TTC derived or guessed?
  |-- score (6 dimensions)
  v
decision output
  |-- to shelf / extend for gap-fill / archive(falsified) / to project
  |-- review comments written back to self-report (audit trail)
```

**他评三问**（评审者最低成本校验）：

```text
Q1 Is the conclusion falsifiable?  -> if not, it is "correct nonsense"
Q2 Does data have a source?        -> key quantified data must have source/baseline/condition
Q3 Is TTC derived or guessed?      -> timing must come from TRL baseline + critical path
```

### 3.4 自评报告模板（结论先行）

```markdown
# Pre-research Self-Assessment Report: <topic>
Date: <YYYY-MM-DD> | Owner: <name> | Period: <start-end> | Effort: <person-month>

## 1. Conclusion (within 300 words, for decision)
- Tech judgment: route [feasible / infeasible / needs-verification], key evidence <...>
- Commercial judgment: [commercializable / not-yet / not-recommended], TTC = <X-Y months>,
  preconditions: <process/cert/supply-chain/ecosystem...>
- Recommendation: [to-shelf / to-project / continue-verify / archive], resource <...>

## 2. Decision value (D1) - what judgment did this change?
- Hypothesis verified: <hypothesis -> result, with data source>
- What was ruled out: <option A excluded, because...>
- Options left: <option set + recommendation>

## 3. Shelf value (D2)
- Entry: <entry name, TRL from X to Y>
- Reusable assets: <design/code/method/data/supplier info>

## 4. Commercialization timing (D3)
- TTC conclusion: <X-Y months>
- Derivation path: TRL<X> -> <stage> -> mass production, critical path: <longest>
- Main risks and preconditions: <...>

## 5. Conversion & tracking (D4/D5)
- Converted: <project/roadmap/selection baseline, link>
- Tracking items: <n items, m closed, blockers: ...>

## 6. Effort & retrospective (D6)
- Actual vs budget: <person-month>
- Timebox met: <yes/no, deviation reason>
- Lessons learned: <within 3 items>
```

---

## 4. 技术货架：预研的资产负债表

### 4.1 货架的本质：把"做过"变成"可复用"

```text
No-shelf mode: pre-research done -> docs archived -> nobody cares -> re-research next time
Shelf mode:   pre-research done -> shelf entry (3 elements) -> new projects check shelf first -> extract on demand

Shelf = balance sheet of pre-research
  Asset side: reusable tech capability (TRL>=4, with deliverables)
  Liability side: unverified assumptions, unresolved risks
```

货架解决的是**组织记忆问题**：预研成果不沉淀为组织可检索的资产，就只是个人经验——人走了知识就没了，人留着知识也不被看见。

### 4.2 货架条目三要素：成熟度 + 商业化时间点 + 责任主体

每个货架条目必须三要素齐备，缺一不可：

| 要素 | 含义 | 表达 |
|:-----|:-----|:-----|
| **成熟度** | 技术验证到什么程度 | TRL 等级（建议 TRL1-9 标尺）+ 验证范围 |
| **商业化时间点** | 从现在到可量产要多久 | TTC 区间（如 12-18 个月）+ 前提条件 |
| **责任主体** | 谁维护、谁答疑、谁负责提取对接 | Owner（个人/团队）+ 支持等级 |

```text
Shelf entry template:
  Entry: <tech name>
  Category: <power/cooling/SI/firmware/compute-platform/process/...>
  Maturity: TRL <X> (verified: <prototype/simulation/mass-prod>, scenarios: <...>)
  TTC: <X-Y months>, precondition: <...>
  Owner: <name>, support level: <A-full/B-consult/C-doc-only>
  Deliverables: <design guide/code base/test report/supplier info/...>
  In-date: <YYYY-MM-DD> | Last review: <YYYY-MM-DD>
```

### 4.3 货架形成流程与运营规则

```text
Flow:
  pre-research closing review passed
    -> fill shelf entry (3 elements complete)
    -> shelf admin registers (category + index)
    -> publish (visible to all, remove info asymmetry)
    -> periodic health check (quarterly: TRL review, expire off-shelf, extraction stats)

Operation rules:
  R1 new project kickoff MUST check shelf first (prevent duplicate pre-research, mandatory)
  R2 entry with no extraction and no progress in 12 months -> downgrade to "reference" or off-shelf
  R3 project that extracts an entry -> feedback extraction effect (write back to entry, close loop)
  R4 shelf is public asset, not personal (Owner is maintainer, not owner)
```

### 4.4 货架运营 KPI

| 指标 | 定义 | 建议基线 |
|:-----|:-----|:---------|
| 入库数 | 季度新增货架条目 | 与预研结项数挂钩（≥80% 结项应入库） |
| **提取率** | 被新项目提取的条目占比 | ≥30% [来源: 对标预研转化率 KPI 基线] |
| 复用成本节省 | 提取条目避免的重复投入 | 每提取一次 ≈ 节省 1-3 人月 |
| 下架率 | 过期下架条目占比 | ≤20%（下架率过高说明货架质量差） |
| 平均货架期 | 条目从入库到被提取的时间 | 目标 <12 个月 |

---

## 5. 商业化时间点（TTC）：预研结论的必备项

### 5.1 为什么预研必须有 TTC 结论

期权理论：**期权价值 = 时间价值，时间价值随行权窗口收窄而衰减**。预研结论不附 TTC，等于买了一个不知道何时能行权的期权——管理层无法决策"要不要等、等多久、值不值得"，预研就沦为"永远在研究"。

TTC 结论的决策用途：

```text
Management questions after getting TTC:
  - usable in 12 months?  -> schedule into next-year roadmap (exercise)
  - usable in 36 months?  -> market window may close (abandon)
  - needs XX process break? -> decide: invest in process validation or give up
```

### 5.2 TTC 的推演方法：TRL 阶段基线 + 关键路径

**第一步：TRL 定位**（当前在几级）

| TRL | 含义 | 典型耗时（服务器硬件） |
|:---:|:-----|:----------------------|
| 1-3 | 概念/实验室验证 | 已发生（预研期） |
| 4 | 部件级原型验证 | 1-2 个季度 |
| 5 | 系统级样机（EVT） | 2-3 个季度 |
| 6 | 工程样机（DVT） | 2-3 个季度 |
| 7 | 可量产（PVT） | 2-4 个季度 |
| 8-9 | 量产爬坡/稳定 | 1-2 个季度 |

**第二步：识别关键路径**（最长环节决定 TTC）

```text
Common critical path candidates:
  - process validation (new material/new process/large package, may take 2-3 quarters)
  - certification (safety/EMC/carrier qualification, may take 1-2 quarters)
  - supply chain (key device lead time/domestic replacement validation, 1-3 quarters)
  - standard/ecosystem (needs standard release or ecosystem maturity, uncontrollable)
  - algorithm/firmware maturity (hidden long path for software pre-research)
```

**第三步：合成 TTC**

```text
TTC = sum of remaining stage durations from current TRL to TRL7
     + longest path after parallelization
     + buffer (10-20%, for uncertainty)

Example: power tech at TRL4, critical path = process validation 2Q, others parallel 3Q
    TTC = 3Q(to PVT) + 1Q(ramp) + 0.5Q(buffer) = 4.5Q ~= 13-15 months
```

### 5.3 TTC 结论的表达格式

```text
Standard format: TTC = <range>, preconditions: <list>, confidence: <high/med/low>

Example:
  TTC = 12-18 months
  Preconditions: (1) 800V HVDC ecosystem devices available in 2026; (2) CDU validation passed
  Confidence: medium (main uncertainty: device mass-prod timing may slip)
```

> **TTC 是自评结论的必备项**：没有 TTC 的自评报告 = 不合格报告，退回补写。这正是用户说的"要有自评的结论存在"——结论不是"做完了"，而是"**多久能商业化、需要什么条件**"。

---

## 6. 跟踪项闭环机制

### 6.1 跟踪项生命周期状态机

```text
+--------+   close    +--------+  periodic   +--------+
| pre-RnD|----------->| to shelf|------------>| tracking|
+--------+             +--------+             +--------+
                                                |  |  |
                      landed (5-choice) <--------+  |  |
                                                |  |  |
                      closed (falsify/giveup) <-----+  |
                                                |     |
                      extended (blocker clear) <-------+  (quarterly review decides)
```

**跟踪项三要素**：owner（谁负责跟进）+ 期限（何时必须落地或关闭）+ 卡点（当前卡在哪、需要什么支持）。

### 6.2 闭环判定的五选一标准

预研跟踪项落地判定（满足任一即闭环）：

```text
(1) entered product roadmap -> listed in next-gen product plan
(2) entered formal project   -> converted to dev project with budget and team
(3) formed selection baseline -> becomes default selection basis for new projects
(4) output standard proposal  -> into industry standard/alliance proposal flow
(5) falsified and archived    -> route clearly negated, archived with trace
```

> **证伪也算闭环**：跟踪的目的不是"必须成功"，而是"必须有一个结论"。[来源: 库内预研 vs 落地分析 §2.4——证伪也是预研的成功产出]

### 6.3 跟踪台账与 Review 节奏

| 节奏 | 动作 | 输出 |
|:-----|:-----|:-----|
| 月度 | 跟踪项自查（owner 更新状态） | 跟踪台账更新 |
| 季度 | 预研运营 Review（评审委员会） | 闭环/延期/关闭裁定 |
| 年度 | 货架体检 + 预研体系复盘 | 货架下架清单 + 预研投入 ROI 复盘 |

**台账字段**：条目、入库日期、owner、目标落地形态（五选一）、期限、状态（挂账/落地/关闭/延期）、卡点、需支持。

---

## 7. 时间投入机制："白嫖个人时间"困境的破解

### 7.1 痛点的本质：组织不愿为期权付费

用户描述的现实："预研很多后续没有固定时间投入，要白嫖个人时间，不占用项目时间，希望个人主动投入，很多活难以开展。"

**第一性分析**：

```text
Essence of "free personal time" = org shifts option cost onto individuals
  - Org view: pre-research return uncertain -> unwilling to invest formal hours -> "encourage personal interest"
  - Individual view: spare-time effort gets no budget/recognition -> effort shrinks -> pre-research shrinks
  - Result: option stays at "verbal value", org claims to value it but does not pay

Harsh conclusion: if the org truly valued pre-research, it would budget it;
                  no budget = org actually judges it unimportant (regardless of words).
                  Cheering "encourage proactive investment" does not change resource allocation.
```

这不是道德问题，是**资源配置信号**问题。破解要从"给资源配置"入手，而不是从"鼓励个人奉献"入手。

### 7.2 破解三件套：预算池 + 时间盒 + 成果可见

**① 小额预算池（定投机制）**——解决"没有固定时间"：

```text
Mechanism: quarterly pre-research budget pool (e.g. 2-4 person-month + small trial fee)
Rules: topic approved -> time quota allocated (e.g. 2 ppl x 10% workload x 1 quarter)
       quota hours are protected (not counted in project assessment)
Effect: "do it when free" -> "quota must be done", pre-research becomes org behavior
Baseline: mature business line pre-research <= 10-15% headcount [KB: pre-research vs landing 2.4]
```

**② 时间盒（强制结项）**——解决"很多活难以开展/无限拖延"：

```text
Mechanism: every topic has a forced timebox (M1 info converge 2-4wk -> M2 direction +4wk
      -> M3 POC validate +8wk -> M4 Go/No-Go) [KB: pre-research vs landing 2.4]
Rules: timebox reached -> MUST close/promote/archive, no "rolling extension"
Effect: small topic concludes within 1 quarter, big topic gets stage conclusion within 2
```

**③ 成果可见（公示机制）**——解决"个人投入不被看见"：

```text
Mechanism: shelf entries published + self-reports published + quarterly result sharing
Effect: personal spare-time effort -> visible shelf entries/sharing -> recognition
      "nobody knows I did it" -> "done is seen", positive feedback for proactive investment
```

### 7.3 给个人的现实策略：不空耗、要转化

如果组织暂时没有预算池机制（现实常态），个人层面可操作的策略：

```text
S1 convert spare-time effort into "visible assets":
   every spare research -> shelf entry / tech note / internal sharing / tool deposit
   key: output must be searchable and citable, not "I studied it"

S2 bind topic to business outlet:
   spare-time topics prioritize product roadmap / known pain points
   (pre-research without landing outlet is unlikely to be recognized) [KB: pre-research vs landing 3.4]

S3 use "decision-oriented pre-research" narrative upward:
   report focuses on "next we do X not Y, because Z", not "I studied Z"

S4 know when to stop (have a view, don't burn out):
   if long-term: no budget + no feedback + no outlet -> route is dead
   rational choice: invest spare time where resources and feedback exist
   (personal time is scarce too - option model applies to individuals as well)
```

---

## 8. 组织边界：预研 vs 量产工程 vs 供应链

### 8.1 三层职责划分（MECE）

用户问题："量产上工艺上的设计与调配，是预研团队，还是供应链处理？内部研发需要支持可量产后，之后退出。"

答案：**三层各司其职，按"能力性质"划分，不按"时间先后"划分**：

| 层 | 职责 | 关键交付物 | 能力性质 |
|:---|:-----|:-----------|:---------|
| **预研团队** | 工艺**可行性**验证（DFM 概念验证、样品试制、工艺窗口评估、工艺路线选型） | DFM 报告、工艺验证报告、可制造性建议、试制样品 | 探索型（验证"能不能做"） |
| **量产工程/制造工程** | 量产**工艺设计**（产线调配、治具设计、工艺参数固化、良率爬坡、SOP） | 量产工艺文件、SOP、良率基线、产线配置 | 运营型（确保"稳定做"） |
| **供应链/采购** | 量产**供货**（物料认证、产能规划、成本、交期、供应商管理） | 供应商认证、产能规划、成本基线 | 商务型（确保"供得上"） |

```text
Boundary map:
  Pre-research team:  process feasible? (can we build it, theoretical yield ceiling)
  Mass-prod engineering: process stable? (how to config line, how to ramp yield to target)
  Supply chain:       supply reliable? (where materials come, cost, lead time)

  Interface pre-research <-> mass-prod eng:
    pre-research outputs "process validation report + manufacturability suggestions"
    mass-prod eng receives and does "mass-prod process design"
  Key: pre-research "manufacturability conclusion" is INPUT to mass-prod eng, not a substitute
```

### 8.2 为什么量产工艺不归预研团队

三个理由（第一性）：

```text
(1) Capability mismatch: pre-research team's scarce capability is "tech judgment"
       (route selection/feasibility), not "line operation" (equipment tuning/yield/on-site)
       -> letting pre-research team do mass-prod process = waste of scarce capability

(2) Rhythm conflict: pre-research is "explore-conclude" rhythm (timebox, ends at conclusion),
       mass-prod process is "continuous operation" rhythm (yield ramp is iterative, no end)
       -> two rhythms cannot coexist in one team

(3) Capability decay: pre-research team bound to mass-prod support -> time consumed
       -> loses exploration capability -> org loses "next-gen tech" source
       (pre-research is an option, consumed by exercise)
```

### 8.3 内部研发退出机制：支持到可量产后退场

用户说"内部研发需要支持可量产后，之后退出"——关键是**退出条件怎么定义**：

```text
Wrong way: exit by time ("pull back after 3 months")
  -> problem: yield not on target after 3 months, nobody takes over, product fails

Right way: exit by "capability transfer complete" (deliverable list as condition)
  -> exit condition = ALL deliverables done:
     [ ] DFM report (manufacturability issue list + suggestions)
     [ ] process validation report (process window + parameter baseline)
     [ ] trial samples and test data
     [ ] tech support doc (FAQ / known issues)
     [ ] on-site support records (key issue resolution trace)
  -> exit ceremony: mass-prod review passed (PPAP / first-batch yield target)
     -> pre-research team unregistered -> into Tier2/3 support (not front line)

Avoid "exit traps":
  - no unlimited support agreement (limit support window, e.g. 1-2 quarters)
  - open issues go to defect tracker (manage by defect flow, not by person)
  - mass-prod eng signs acceptance before exit (clear responsibility transfer point)
```

**边界结论**：

```text
Pre-research team: support until "commercializable" judgment reached (PVT passed / first-batch yield ok)
Mass-prod eng:  take over from "commercializable" (process freeze + yield ramp)
Supply chain:   parallel throughout (material qualification can start early, in parallel)

Exit of internal R&D is not "wash hands", it is "responsibility transfer":
  tech responsibility: pre-research team -> mass-prod eng (acceptance sign-off)
  support mode: full participation -> Tier2/3 Q&A (limited window)
```

---

## 9. 预研运营的季度节奏（PDCA）

把上述机制串成运营节奏：

```text
Q start: kickoff review
  - topic approved (trigger condition check [KB: pre-research vs landing 2.2])
  - allocate budget pool quota (time quota + trial fee)
  - set timebox (M1-M4 milestones)

Q middle: monthly tracking
  - tracking ledger update (owner self-check)
  - blocker report and coordination (what support needed)

Q end: closing review + shelf update + self-assessment
  - 6-dimension scoring (D1-D6)
  - self-report (incl. TTC) -> external 3 questions -> decision
  - to shelf (3 elements) / to project / archive (falsified)
  - un-landed items into tracking ledger
  - shelf health check (extraction stats + expire off-shelf)
  - result sharing session (visibility)

Year: pre-research system retrospective
  - pre-research investment vs conversion ROI review
  - shelf asset inventory (balance sheet)
  - budget pool tuning (add to high-conversion directions)
```

---

## 10. 结论

1. **评价体系**：预研按期权模型评价——六维框架（决策贡献 25% + 货架贡献 20% + 商业化判断 15% + 转化率 15% + 闭环率 15% + 投入效率 10%），自评报告结论先行、他评三问校验、证伪也算有效产出。
2. **技术货架**：预研的资产负债表，条目三要素（TRL + TTC + Owner）齐备才入库，立项先查货架防重复，12 个月无人提取降级下架。
3. **商业化时间点**：TTC 是自评结论的必备项，从 TRL 阶段基线 + 关键路径推演，表达为"区间 + 前提 + 置信度"。
4. **跟踪闭环**：状态机管理（货架入库 → 挂账 → 跟进 → 落地/关闭），闭环五选一标准，月度台账 + 季度 Review。
5. **时间投入**："白嫖个人时间"是资源配置信号问题，破解靠预算池 + 时间盒 + 成果可见三件套；个人层面不空耗、要转化、判断止损。
6. **组织边界**：预研做可行性验证、量产工程做量产工艺设计、供应链做供货，内部研发以"能力转移交付物"为退出条件，支持到首批量产通过后退场，遗留问题进缺陷库。

**一句话总结**：预研管理的本质是把"不确定的探索"变成"可决策、可复用、可商业化、可交接"的确定性资产——评价体系给它标价，货架给它存放，TTC 给它期限，跟踪给它闭环，预算给它燃料，边界给它退路。

---

## 11. 参考文件

1. [预研 vs 落地：技术投入决策、向上管理与组织心理深度分析](2026-08-21-pre-research-vs-landing-decision-analysis.md)（knowledge/02_rd/03_management/）—— 决策层：期权 vs 现金流、触发条件、伪预研、时间盒、退出机制
2. [服务器产品线全生命周期管理知识图谱](2026-08-11-server-product-lifecycle-org-knowledge-graph.md)（knowledge/02_rd/03_management/）—— §3.5 转化机制三要素（TDT/TR 门禁/路标衔接）
3. [服务器产销研BG经营指标体系](2026-07-30-server-rd-kpi-system-deep-analysis.md)（knowledge/07_industry-research/03_server/）—— 技术预研转化率 ≥30% KPI 基线
4. [管理五不对称深度分析](2026-08-25-management-five-asymmetries-deep-analysis.md)（knowledge/04_person/enterprise-mgmt/）—— 时间不对称：不合规遗留→债务台账（跟踪闭环的同源方法论）
5. [CowAgent 系统可复用组件技术货架盘点报告](2026-08-20-cowagent-reusable-components-shelf.md)（knowledge/03_AI/knowledge-system/）—— 货架实践实例（TRL≥7、复用度分级 S/A/B、场景矩阵）
6. TRL（Technology Readiness Level）标准定义 —— NASA/DoD 通用标尺

---

## 变更记录

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-25 | v1.0 | 首次创建：预研活动运营机制设计——六维评价体系（期权模型）+ 技术货架机制（三要素）+ TTC 商业化时间点推演 + 跟踪闭环状态机 + 时间投入困境破解（预算池/时间盒/成果可见）+ 预研/量产/供应链边界与内部研发退出机制 |
