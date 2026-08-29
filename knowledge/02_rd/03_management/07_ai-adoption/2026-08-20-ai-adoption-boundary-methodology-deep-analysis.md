# AI 导入替代人工的边界方法论：个例推广 × 80/20 边界 × 人机投入 × 底座复用

> **类型**: 深度技术分析 | **日期**: 2026-08-20 | **版本**: v1.0
> **来源**: 用户洞察（组织级 AI 导入的七个追问）+ 知识库互锁（AI 采用五阶段闭环 / 半件事陷阱 / 三位一体 / 能力放大器 / 产出经济学）+ 第一性原理推导
> **适用范围**: 组织级 AI 导入 / 人工替代评估 / 研发提效 / 底座建设
> **承接**: [`2026-07-08-ai-adoption-in-server-rd.md`](./2026-07-08-ai-adoption-in-server-rd.md)（组织运作的"骨架"，本文补"认知层"）
> **相关**: [`2026-08-17-half-task-trap-end-to-end-delegation-deep-analysis.md`](../../../03_AI/methodology/2026-08-17-half-task-trap-end-to-end-delegation-deep-analysis.md) · [`2026-08-10-system-building-trilogy-goal-path-standard.md`](../../../03_AI/methodology/2026-08-10-system-building-trilogy-goal-path-standard.md) · [`2026-08-19-ai-capability-amplifier-upper-bound-deep-analysis.md`](../../../03_AI/methodology/2026-08-19-ai-capability-amplifier-upper-bound-deep-analysis.md) · [`2026-08-06-ai-adoption-creation-methodology.md`](../../../03_AI/methodology/2026-08-06-ai-adoption-creation-methodology.md)

---

## 📑 目录

1. [结论概要（TL;DR）](#1-结论概要tldr)
2. [问题重构：七个散点 → 一条决策链](#2-问题重构七个散点--一条决策链)
3. [看清：工作全貌识别（全部工作怎么准确识别）](#3-看清工作全貌识别全部工作怎么准确识别)
4. [划清①：个例 → 普遍价值的可借鉴判断](#4-划清个例--普遍价值的可借鉴判断)
5. [划清②：80/20 边界识别与防挖坑](#5-划清8020-边界识别与防挖坑)
6. [算清：人机投入比模型（人来投入能完成多少）](#6-算清人机投入比模型人来投入能完成多少)
7. [跑清：六步法的方法论化与每步判据](#7-跑清六步法的方法论化与每步判据)
8. [复用：底座化——不每个领域处理一遍](#8-复用底座化不每个领域处理一遍)
9. [做活：目标明确 × 方案达成 × 运营机制](#9-做活目标明确--方案达成--运营机制)
10. [落地清单](#10-落地清单)
11. [与知识库已有方法论的互锁](#11-与知识库已有方法论的互锁)
12. [风险与批判](#12-风险与批判)
13. [数据缺口](#13-数据缺口)
14. [参考来源](#14-参考来源)
15. [Changelog](#15-changelog)

---

## 1. 结论概要（TL;DR）

**核心命题**：AI 导入替代人工的成败，不取决于 AI 能力，而取决于四件事是否想清——**全貌看清了吗、边界划清了吗、投入算清了吗、底座建了吗**。多数组织的失败不是"AI 不行"，而是"边界不清 + 底座缺失 + 目标模糊"三重叠加。

**四个核心问题的直接回答**：

| # | 问题 | 直接回答 |
|:-:|:-----|:---------|
| Q1 | 个例数据有多大普遍价值、多少可借鉴 | 个例价值分**结果价值**（这次省了多少）与**结构价值**（模式可迁移）两层。可借鉴性 = 任务结构相似度 × 环境依赖度的函数：**结构相似 + 低依赖 → 可推广；结构相似 + 高依赖 → 只借鉴方法不照搬方案；结构不相似 → 只当启发不当证据**。单一个例永远不构成"规律"，需要 ≥3 个异域案例交叉验证才升级为模式 [来源: 本文推导，方法论互锁 08-06 查新定位论] |
| Q2 | AI 做 80% 时，20% 怎么识别、避免挖坑 | 20% 由四类组成：**判断密集、长尾异常、高风险不可逆、跨上下文整合**。识别方法：逐环节打四标签（确定性/判断密度/风险/频率），**可自动化 = 高确定 × 高频 × 可验证 × 可恢复**，四者缺一即留人。挖坑根因是"看起来能跑"陷阱——毛产出爆炸、净价值为负；防挖坑三件套：验证闭环 + 人类验收点 + 灰度放量 |
| Q3 | 人来投入能完成全部工作的多少 | 人的投入不是"AI 剩下的活"，而是**关键路径判断**：定义层（做什么）≈100% 在人、执行层（怎么做）≈0-20% 在人、验收层（对不对）≈100% 在人、异常层（出事怎么办）≈100% 在人。**组织级替代率天花板约 20-30% 的工时**，但可释放 60-80% 的"定义与验收"时间占比之外的拼接损耗 [来源: 08-19 放大器分析三层剪刀差实证：个体 2-10× / 组织 1.0-1.5×] |
| Q4 | 全部工作怎么准确识别 | 用**产出物反推法 + 工作包画像**：不先列"工作"，先列"交付物"，再反推每件交付物背后的步骤链、输入输出、判断点、异常点。两大盲区必查：隐性工作（沟通/协调/返工）与异常路径（长尾）。产出 = 任务清单 + 自动化潜力三分类标注 |

**七层决策链**（本文骨架）：

```
see the whole -> draw the boundary -> count the cost -> run the path -> reuse the base -> keep it alive
 (Q4)              (Q1+Q2)            (Q3)          (6-step)          (platform)      (goal+ops)
```

---

## 2. 问题重构：七个散点 → 一条决策链

### 2.1 用户散点问题清单（原文提炼）

| # | 原始表达 | 本质问题 |
|:-:|:---------|:---------|
| 1 | "个例的数据是否有普遍价值，多大的可借鉴处理" | 经验的**可迁移性**判断 |
| 2 | "AI 能做完整工作 80%，剩下 20% 怎么识别出来，避免挖坑" | 自动化**边界识别**与风险控制 |
| 3 | "人来投入，能完成全部工作的多少" | 人机**投入比**的量化 |
| 4 | "全部工作怎么进行准确识别" | 工作**全貌识别**（前置问题） |
| 5 | "扫场景→找痛点→跑 PoC→验证→推广→迭代" | 落地**路径**方法论 |
| 6 | "底层系统开发与应用选型专用处理形成底座，形成方法论直接复用" | **底座化**与复用 |
| 7 | "宣传与实现 gap 可以更大点，研发可以距离现场更近一点；做活需要明确目标并确定达成方案" | **运营机制**与目标管理 |

### 2.2 统一框架：七问不是并列问题，是一条决策链

```
[SEE]   full picture      -> without it, substitution rate is a guess
  |
[DRAW]  transferability   -> over-promoting one case = treating luck as law
  |    + boundary         -> missing the 20% = digging a pit
  v
[COUNT] human investment  -> without counting, goals cannot be verified
  |
[RUN]   6-step path       -> skeleton exists, missing per-step criteria
  |
[REUSE] platform base     -> without it, every domain rebuilds the wheel
  |
[ALIVE] goal + mechanism  -> operations without goals die out fast
```

**关键洞察**：链条上**越靠前的问题越被忽视、代价越大**。多数组织在"跑清"层（六步法）投入最多，却在"看清/划清"层欠账——所以 PoC 跑了一堆、推广不了几个。

---

## 3. 看清：工作全貌识别（全部工作怎么准确识别）

### 3.1 为什么全貌识别是第一前置

没有全貌就没有替代率。问"AI 能替代多少"之前，必须先回答"这项工作一共由哪些环节组成、每个环节什么性质"。**替代率的分母模糊，分子再准也没意义** [来源: 本文推导]。

典型反例：只看到"写代码"这个显性环节，估替代率 80%；没算"调试排错（隐性）""评审沟通（隐性）""需求澄清（隐性）"——实际替代率不足 30%。**隐性工作不识别，替代率高估 2-3 倍** [来源: 本文判断性估计，见 §13 数据缺口]。

### 3.2 识别方法一：产出物反推法（不列工作，列交付物）

```
Step 1: list deliverables (this week/month):
        design doc / test report / code commit / review note / meeting note / failure review ...
Step 2: reverse-engineer the production chain of each deliverable:
        deliverable X = input(data/req) -> process(analysis/design/coding) -> verify(self/review) -> output
Step 3: mark human vs machine actions in each step:
        which steps need judgment? which have rework? which depend on others?
```

**原理**：交付物是客观可见的，工作流程是主观模糊的——从客观反推主观，比直接问"你平时干什么"准确得多 [来源: 本文推导，方法上与 ticket-as-spec 的"以产出定规格"同构]。

### 3.3 识别方法二：工作包画像（Work Package Profile）四要素

| 要素 | 内容 | 对 AI 导入的意义 |
|:-----|:-----|:----------------|
| **步骤链** | 完成该工作包的固定步骤序列 | 决定能否流程化（步骤固定 → 可编排）|
| **输入输出** | 依赖什么资料、产出什么形态 | 决定数据/工具是否齐备 |
| **判断点** | 哪些节点需要人做价值/风险判断 | 判断密集处 = AI 边界 |
| **异常点** | 哪些情况会偏离主流程（长尾） | 异常频发处 = 挖坑高发区 |

### 3.4 两大盲区（必查清单）

| 盲区 | 为什么容易漏 | 后果 | 补救 |
|:-----|:------------|:-----|:-----|
| **隐性工作** | 不在任何流程文档里：沟通对齐、协调资源、返工修复、救火 | 全貌失真，替代率虚高 | 用"时间审计"补：连续 1-2 周记录实际时间去向 |
| **异常路径** | 主流程 80% 覆盖的是"正常情况"，异常才是人力的真正消耗点 | AI 只覆盖主流程 → "看起来自动化了，实际人还得兜底" | 画像时强制追问"什么情况会卡住/返工" |

### 3.5 全貌识别的产出：任务清单 + 三分类标注

```
label each work package with automation potential (3 classes):
  [A] automatable: fixed steps + structured I/O + verifiable result
  [B] assistable:  human judges, AI generates/retrieves/drafts (human-AI co-work)
  [C] keep human:  judgment-dense / high-risk / people-heavy / taste-driven

output = full work package list + 3-class labels + share of each class
-> this share is the credible denominator of the substitution rate
```

---

## 4. 划清①：个例 → 普遍价值的可借鉴判断

### 4.1 个例价值的两种成分

| 成分 | 定义 | 例子 | 可迁移性 |
|:-----|:-----|:-----|:---------|
| **结果价值** | 这个个例本身省了多少时间/钱 | "这次用 AI 写测试报告省了 3 天" | 低（只证明这事可行）|
| **结构价值** | 这个个例背后可抽象的模式 | "测试报告 = 数据输入 + 模板生成 + 人工校验" 这个模式 | 高（可迁移到其他报告类）|

**核心判断**：**个例的可借鉴性 = 结构价值，不是结果价值**。推广一个 PoC 时问"它背后的结构是什么"，而不是"它省了多少" [来源: 本文推导]。

### 4.2 可借鉴性判据矩阵：结构相似度 × 环境依赖度

```
                     task structure similarity
                  low                        high
  env dep  high   [QD heuristic only]        [QB borrow method, not solution]
                   (not evidence)            (abstract pattern, re-adapt)
  env dep  low    [QC coincidence]           [QA generalizable (best)]
                   (need more samples)       (pattern + solution reusable)
```

| 象限 | 判定 | 借鉴策略 |
|:----:|:-----|:---------|
| **A 结构相似 × 低依赖** | 模式与实现都可迁移 | **可推广**：直接复制方案 + 本地参数化 |
| **B 结构相似 × 高依赖** | 模式对，实现被环境绑定 | **借鉴方法**：抽模式，重写实现（"方法论可复用，轮子要重造"）|
| **C 结构不相似 × 低依赖** | 偶发巧合 | **暂缓**：等更多异域样本验证 |
| **D 结构不相似 × 高依赖** | 纯个案 | **只当启发**：不构成任何证据 |

**环境依赖度判据**（什么算"依赖"）：数据可得性、工具栈、组织流程、合规约束、人际网络 [来源: 本文推导]。

### 4.3 借鉴的四级阶梯：个例 → 模式 → 方法论 → 底座

```
L1 case:      one successful PoC (evidence strength 1/5)
L2 pattern:   common abstraction of >=3 cross-domain cases (3/5)
L3 method:    pattern + applicable conditions + anti-patterns + criteria (4/5)
L4 platform:  method solidified into platform/tool/process assets (5/5, org level)
```

**升级条件（硬门槛）**：L1→L2 必须 **≥3 个不同领域**的案例验证（同域重复不算）——这是防止"个例崇拜"的最小样本量 [来源: 本文推导，与 08-06"查新从门禁降级为定位工具"的时序观一致]。

### 4.4 借鉴性评估四问（操作工具）

```
Q1 structure similar?  -> are steps / I-O / judgment points isomorphic to mine?
Q2 dependency gap?     -> how different are data/tools/process/compliance? solvable?
Q3 evidence enough?    -> 1 case or >=3 cross-domain cases?
Q4 failure reversible? -> if copied and fails, is the loss controlled? (yes -> try boldly)
```

### 4.5 两个反模式

| 反模式 | 表现 | 代价 | 防治 |
|:-------|:-----|:-----|:-----|
| **个例崇拜** | 1 个 PoC 成功 → 全组织推广 | 环境不同照搬失败，信心受挫 | 强制 L2 门槛（≥3 异域案例）|
| **个例虚无** | 每个 PoC 都是孤例，从不抽象 | 重复造轮子，知识不积累 | 强制"结构价值"提炼环节（跑完即抽象）|

---

## 5. 划清②：80/20 边界识别与防挖坑

### 5.1 那 20% 的组成（四类）

| 类别 | 特征 | 为什么 AI 做不了/不该做 | 例子 |
|:-----|:-----|:----------------------|:-----|
| **判断密集** | 每一步都含价值取舍 | 判断力不可外包（MEMORY 核心原则）| 方案选型、优先级排序、风险接受 |
| **长尾异常** | 低概率高影响，样本稀缺 | 训练数据不足，AI 会"自信地错" | 罕见故障、特殊配置、边界条件 |
| **高风险不可逆** | 出错代价大且无法回滚 | 恢复路径不存在（半件事陷阱 P3）| 删库、量产决策、对外承诺 |
| **跨上下文整合** | 需要综合多个来源的全局理解 | 上下文窗口与全局视角受限 | 跨团队协调、组织级决策 |

### 5.2 边界识别操作法：逐环节打四标签

对 §3 工作包画像的每个环节，打四个标签：

```
tag1 determinism:  are steps fixed? (high/mid/low)
tag2 judgment:     how many human judgments inside? (high/mid/low)
tag3 risk:         cost of error? (high/mid/low) + reversible?
tag4 frequency:    how often does it occur? (high/mid/low)
```

### 5.3 可自动化判定公式（四条件同时满足才自动化）

```
- deterministic: fixed steps, programmable (else AI free-play = uncontrollable)
- frequent:      high frequency justifies investment (low freq = cost > gain)
- verifiable:    result machine-verifiable (else acceptance cost explodes)
- recoverable:   failure can roll back (else high risk)

missing any one -> downgrade to [B] assist or [C] keep human
```

**注意**：这里的"可验证"是**机器可验证**（有测试/对照/量化标准），不是"人看一眼"——人验的高频环节，验证成本本身就把自动化收益吃掉了 [来源: 本文推导，与 08-19 放大器"瓶颈在审阅"互锁]。

### 5.4 挖坑机制解剖："看起来能跑"陷阱

```
typical pit-digging path of AI adoption:
  1. PoC phase:  pick the smoothest scenario, demo looks great (gross effect)
  2. rollout:    feed real full data -> long-tail anomalies flood in
  3. result:     "80% of AI output is fine, but human must 100% backstop the 20% errors"
               -> headcount does not drop, instead "reviewing AI" work is added
               -> net effect negative (high gross, negative net)
```

**与产出经济学互锁**：AI 产出是**毛利非净利**，需二次加工；"看起来能跑" = 只有毛利没有净利 [来源: 08-05 产出毛利 vs 净利熵分析]。挖坑的本质是**把长尾异常风险从"人脑隐性处理"转移成"AI 显性犯错 + 人显性兜底"**——看起来自动化了，实际只是换了犯错的位置。

### 5.5 防挖坑三件套

| 机制 | 内容 | 防什么 |
|:-----|:-----|:-------|
| **验证闭环** | 每个自动化环节有客观验证手段（测试/对照/量化门禁）| 防"自信地错" |
| **人类验收点** | 关键环节保留人工 checkpoint（流程可交、责任不交）| 防责任真空 |
| **灰度放量** | 先 10% 量跑真实验证，再逐步放大；带 kill switch | 防一次性全量爆雷 |

**灰度放量的量化规则（建议）**：PoC → 影子模式（AI 跑但不采信，与人工并行 2-4 周）→ 小流量（10-20%）→ 全量。每阶段有明确的"继续/回退"判据 [来源: 本文推导]。

---

## 6. 算清：人机投入比模型（人来投入能完成多少）

### 6.1 工作四层分解：人到底在哪层投入

| 层 | 内容 | 人的投入占比（典型）| 说明 |
|:---|:-----|:------------------|:-----|
| **定义层** | 做什么、标准是什么、边界在哪 | ~100% | 规格化能力不可外包（半件事陷阱 P1）|
| **执行层** | 从规格到产物的转化 | 0-20% | AI 的主战场；留人的是长尾异常 |
| **验收层** | 对不对、好不好、能不能用 | ~100% | 审阅是零和博弈，AI 不省这个 |
| **异常层** | 出问题怎么处理、谁来负责 | ~100% | 责任与判断不可外包 |

### 6.2 核心洞察：人的投入不是"剩余工作量"，是"关键路径判断"

```
wrong view:  AI substitution 80% = human only invests 20% effort
right view:  human input = define(100%) + accept(100%) + exception(100%) + exec residue(0-20%)
            -> working hours may drop 60-80% (execution outsourced)
            -> but cognitive load rises (from doing to defining + accepting + judging)
```

**这是"AI 解放人力"叙事的最大误读**：解放的是**执行工时**，不是**认知投入**。人的价值重心从"做"迁移到"定义 + 验收 + 判断"——对组织意味着**人必须变得更懂判断，否则 AI 放大的是错误** [来源: 本文推导，互锁 08-19"放大的是执行层不是认知层"]。

### 6.3 替代率天花板公式（组织级）

```
example: exec share 60% of hours, AI covers 90% of exec, exception rate 20%
        -> ceiling = 60% * 90% * 80% = 43% (ideal value)
org evidence: individual 2-10x, org 1.0-1.5x [source: 08-19 amplifier analysis]
inference: org-level net hour substitution realistic band 20-30%
```

**为什么组织级远低于个体级**：个体的 2-10× 是"定义+验收都由同一人完成"的封闭场景；组织级要过"交接/审批/标准化/合规"的过手损耗，放大在过手中被吃掉 [来源: 08-19 三层剪刀差]。

### 6.4 投入决策：什么时候值得人机协同而非纯 AI

| 场景 | 判断 | 决策 |
|:-----|:-----|:-----|
| 高价值 + 形态清晰 + 可验证 | 整件事交付（半件事陷阱 L1/L2）| AI 全跑，人做验收 |
| 高价值 + 形态模糊 | 先 shape-reverse 定形态，再整交 | 人定义形态，AI 执行 |
| 高价值 + 高风险不可逆 | 保留人工 checkpoint | 人机协同，人握最终决策 |
| 低价值 + 形态清晰 | 半件事也值得（framing 成本不划算）| 直接用片段式（L0）|

---

## 7. 跑清：六步法的方法论化与每步判据

### 7.1 六步法 = 已有五阶段闭环的认知升级版

`扫场景→找痛点→跑 PoC→验证→推广→迭代` 与 07-08 文档的五阶段闭环同构 [来源: 07-08 AI 采用方法论 §2.1]。本文的增量是给每步补上**决策判据**——什么条件下进入下一步、什么条件下止损，避免"跑了一堆 PoC 一个都推不出去"。

### 7.2 每步判据表

| 步骤 | 进入下一级的判据 | 止损/回退判据 | 关键产出 |
|:-----|:----------------|:-------------|:---------|
| **扫场景** | 场景清单 ≥ 全貌识别后的全量工作包（不是拍脑袋几个）| 场景列表与业务目标脱节 | 全量场景清单 + 潜力标注 |
| **找痛点** | 痛点 = 高频 × 高痛 × 切得动（07-08 判据）| 全是"想当然"痛点，无一线数据 | 痛点清单（含频次/代价量化）|
| **跑 PoC** | 选 P0 = 价值最高 + 最容易突破 | PoC 超 2-4 周无进展 → 换场景 | 最小可行方案 + 效果数据 |
| **验证** | 效果量化（省时/降错/覆盖）+ 与基线对比 | 净效应为负（毛利高净利负）→ 不推广 | 验证报告（数值+基线+条件）|
| **推广** | 结构价值成立（§4）+ 灰度小流量验证通过 | 长尾异常率超阈值 → 回退影子模式 | 推广方案 + 灰度数据 |
| **迭代** | 使用反馈回流 + 异常案例入库 | 场景已商品化 → 迁移到工具 | 模式升级/方法论沉淀 |

### 7.3 每步常见失败模式

| 步骤 | 失败模式 | 根因 |
|:-----|:---------|:-----|
| 扫场景 | 只扫显性环节，漏隐性工作 | 没做全貌识别（§3）|
| 找痛点 | 痛点来自领导想象而非一线 | 研发距离现场太远（§9.3）|
| 跑 PoC | 挑最简单场景刷 KPI | 没按"价值×可行性"选 P0 |
| 验证 | 只报毛利（省了多少）不报净利（审了多少）| 缺验证闭环 |
| 推广 | 1 个成功案例直接全量推 | 个例崇拜（§4.5）|
| 迭代 | PoC 完事就散，无复盘 | 缺运营机制（§9）|

### 7.4 双轨节奏

```
explore track (fast):   scan -> PoC -> verify      -> share once proven (day/week level)
solidify track (stable): verified -> abstract pattern -> platformize -> rollout (week/month level)
```

探索轨产生"个例"，固化轨把个例升级为"模式/方法论/底座"——两轨缺一不可：只有探索轨 = 一堆散点 PoC；只有固化轨 = 象牙塔底座 [来源: 本文推导，互锁 08-06 播种/收获/固化三阶段]。

---

## 8. 复用：底座化——不每个领域处理一遍

### 8.1 底座的本质：跨域可复用资产

用户洞察的核心是**"不要每个领域都处理一遍"**——底层系统开发与应用选型是跨域的公共需求，应专用化处理形成底座。底座的本质：**把 N 个领域的公共部分抽出来做一次，而不是做 N 次**。

```
no platform:   domain1(data access + model call + verify frame + knowledge mgmt)
               domain2(data access + model call + verify frame + knowledge mgmt)  -> repeated N times
with platform: platform(data access | model call | verify frame | knowledge mgmt) -> built once
               domain1(domain logic only)  domain2(domain logic only)             -> save ~70% setup each
```

### 8.2 进底座三判据（同时满足才底座化）

```
1) cross-domain reuse: >=2 heterogeneous domains clearly need it (not maybe later)
2) standardizable:     interfaces/formats can be unified (else forced abstraction)
3) evolving value:     continuous evolution, not one-off (interlocks with trilogy self-build)
```

**反模式对照**：三条件缺一 → 不要底座化。一次性的需求底座化 = 象牙塔；无标准硬抽象 = 过度工程（56 检查器教训：自研泛滥 = 维护成本 O(n²)）[来源: 08-10 trilogy 自研警示]。

### 8.3 底座四层（按可复用粒度分层）

| 层 | 内容 | 例子 | 沉淀方式 |
|:---|:-----|:-----|:---------|
| **方法论底座** | 判据/流程/反模式（本文即方法论底座）| 80/20 边界识别法、借鉴四问 | 文档 + 评审 |
| **数据底座** | 知识库/数据源/标注规范 | 领域知识库、测试数据池 | 平台 + 治理 |
| **能力底座** | 模型调用/工具链/API 封装 | LLM 网关、RAG 服务、Skill 库 | 平台 + SDK |
| **验证底座** | 验证闭环/门禁/灰度框架 | 效果评估框架、灰度发布器 | 平台 + 自动化 |

### 8.4 反模式：重复造轮子 vs 象牙塔底座

| 反模式 | 表现 | 根因 | 防治 |
|:-------|:-----|:-----|:-----|
| **重复造轮子** | 每域自己接模型/搭 RAG/写验证 | 无底座意识 + 各域封闭 | 底座三判据 + 强制复用审计 |
| **象牙塔底座** | 底座做完没人用（太抽象/太重）| 脱离业务现场设计 | 底座必须由 ≥2 个真实场景"长"出来（先有场景后抽底座）|

**关键纪律**：**底座从场景长出来，不是从架构图里画出来**——先有 2 个异域真实案例，再抽底座；底座每扩展一个领域，都要验证"是否真的省了搭建成本" [来源: 本文推导，互锁 08-10 渐进结晶化]。

### 8.5 研发距离现场更近：底座与现场的耦合机制

用户洞察"研发可以距离现场更近一点"——底座建设的**反向约束**：

```
platform risk: platform team far from business -> platform misses field reality -> nobody uses it
remedy: platform owner must be the abstractor of field scenarios, not an architect
  - platform needs come from frontline PoC reviews (not product planning meetings)
  - platform acceptance: new domain onboarding saves 70% setup time (quantifiable)
  - platform cadence: follow PoCs (weekly), not architecture reviews (monthly)
```

---

## 9. 做活：目标明确 × 方案达成 × 运营机制

### 9.1 目标：单一目标原则（互锁 trilogy）

"做活需要明确目标，并确定达成的方案"——与 trilogy 三位一体完全一致：

| trilogy 维度 | 本文对应 | 判据 |
|:------------|:---------|:-----|
| **目标（为什么）** | AI 导入的目标：提效/降错/覆盖/学习，**一个阶段一个主目标** | 混合目标 = 验收模糊 = 投入无边界 |
| **路径（怎么建）** | 六步法 + 底座化（§7+§8）| commodity 用工具 / integration 加壳 / differentiator 自研 |
| **标准（怎么算好）** | 每步判据 + 验证闭环（§7.2）| L1 核心=可恢复 / L2 生产=SLA / L3 内部=DoD / L4 实验=允许失败 |

**AI 导入的阶段性目标建议**：播种期（先用起来建立价值地图）→ 收获期（做起来形成原创产出）→ 固化期（修补工具化释放资源）[来源: 08-06 三阶段]。

### 9.2 运营五件事（进展同步 / 难点 / 诉求 / 问题探讨 / AI 应用分享）

用户提出的"领域进展快速同步、难点、诉求；问题探讨；AI 应用分享"——落地为**双周例会五件事**（与 07-08 双周例会互锁，本文补充节奏与量化）：

| 环节 | 内容 | 节奏 | 产出 |
|:-----|:-----|:-----|:-----|
| **进展同步** | 各域 PoC/推广状态一览 | 每双周 | 状态看板更新 |
| **难点上报** | 当前卡点（技术/资源/组织）| 每双周 | 卡点清单 + 责任人 |
| **诉求收集** | 对底座/工具/数据的诉求 | 每双周 | 底座需求池（喂给 §8）|
| **问题探讨** | 1-2 个深度问题（边界/方法/选型）| 每双周 | 结论 + 落库 |
| **应用分享** | 1 个跑通案例完整分享（含结构价值提炼）| 每双周 | 个例 → 候选模式 |

**运营铁律**：分享必须包含"结构价值提炼"（§4.1），否则只是炫耀不是借鉴；每个分享案例必须回答"什么条件下可复制"。

### 9.3 宣传与实现的 gap 管理

用户洞察"宣传与实现之间的 gap 可以更大点"——这是一个**反直觉但正确的组织信号**：

```
essence of publicity gap: gap between vision (publicity) and current capability (reality)
cost of small gap:  vision locked by current capability, org afraid to dream big (kills exploration)
value of large gap: vision pulls, sparks exploration (but guard against slogan-only PR)

management rules:
  1) gap can be large, but publicity must be directionally right (vision points to real trend)
  2) large gap -> converge with phased milestones: big vision -> quarterly goals -> biweekly actions
  3) the gap must be backed by progress evidence (DoD + milestones + celebration, MEMORY method)
  4) prevent publicity replacing delivery: tie PR frequency to progress, no progress no PR
```

**一句话**：愿景可以跑在实现前面半步到一步（牵引），但不能跑在实现前面一光年（脱节）。gap 的合理区间 = **组织能承受的探索信心**。

### 9.4 迭代复盘与量化指标

| 指标 | 定义 | 周期 |
|:-----|:-----|:-----|
| **场景覆盖率** | 已扫场景 / 全量工作包 | 月 |
| **PoC 转化率** | 验证通过并推广 / 已跑 PoC | 月（<30% 要查原因）|
| **净效应** | 节省工时 - 审阅/兜底工时 | 季度 |
| **底座复用率** | 接入底座领域数 / 总领域数 | 季度 |
| **个例 → 模式升级数** | 通过 L2 门槛的案例数 | 月 |

---

## 10. 落地清单

```
before start (SEE):
  [ ] run 2-week time audit on target role, fill in hidden work
  [ ] output full work package list + A/B/C class labels
  [ ] compute the denominator of substitution rate (full-picture hours) as baseline

during selection (DRAW):
  [ ] tag each candidate scenario per-step (determinism / judgment / risk / frequency)
  [ ] filter with the automatable formula, mark the 20% boundary
  [ ] assess existing cases with the 4 borrow-questions
  [ ] allow full rollout only with >=3 cross-domain cases

during execution (COUNT + RUN):
  [ ] every PoC defines a verification loop (baseline + numbers + conditions)
  [ ] gray rollout 3 phases: shadow -> small traffic -> full (with kill switch)
  [ ] decide continue / stop / rollout per the 6-step criteria table

during solidification (REUSE):
  [ ] extract structural value from every proven case (pattern abstraction)
  [ ] decide platformization with the 3 platform criteria
  [ ] platform grows from >=2 heterogeneous scenarios, no pure architecture design

during operation (ALIVE):
  [ ] define the single main goal of the phase (seed / harvest / solidify)
  [ ] biweekly meeting with 5 fixed items
  [ ] publicity gap converged by milestones, no progress no PR
  [ ] quarterly review of 5 metrics (scenario coverage / PoC conversion / net effect / platform reuse / pattern upgrade)
```

---

## 11. 与知识库已有方法论的互锁

| 已有文档 | 覆盖 | 本文增量 |
|:---------|:-----|:---------|
| [`07-08 AI 采用方法论`](./2026-07-08-ai-adoption-in-server-rd.md) | 六步法组织运作、双周例会、P0 场景、软件栈 | 每步判据 + 失败模式 + 认知层（全貌/边界/投入）|
| [`08-17 半件事陷阱`](../../../03_AI/methodology/2026-08-17-half-task-trap-end-to-end-delegation-deep-analysis.md) | 委托边界、完成形态、shape-reverse | 组织级 80/20 边界识别操作法 + 防挖坑三件套 |
| [`08-10 三位一体`](../../../03_AI/methodology/2026-08-10-system-building-trilogy-goal-path-standard.md) | 目标×路径×标准、build vs buy、自研三条件 | 底座三判据 + 单一目标原则在 AI 导入的应用 |
| [`08-19 能力放大器`](../../../03_AI/methodology/2026-08-19-ai-capability-amplifier-upper-bound-deep-analysis.md) | 放大上限、三层剪刀差、反软文 | 替代率天花板公式 + 人机投入四层分解 |
| [`08-05 产出经济学`](../../../03_AI/methodology/2026-08-05-ai-output-gross-vs-net-entropy.md) | 毛利 vs 净利 | 挖坑机制 = "看起来能跑"的净利为负 |
| [`08-06 采用方法论`](../../../03_AI/methodology/2026-08-06-ai-adoption-creation-methodology.md) | 先用起来/做起来/创作起来 | 个例→模式升级门槛（≥3 异域案例）|
| [`08-13 ticket-as-spec`](../../../03_AI/methodology/2026-08-13-ticket-as-spec-high-throughput-engineer-methodology.md) | 任务规格化 | 产出物反推法同构 |

---

## 12. 风险与批判

| 风险 | 说明 |
|:-----|:-----|
| **方法论过重** | 全貌识别+画像+标签+判据全套跑起来成本高——本文定位"按需取用"：小团队先用三分类标注 + 四标签两个轻量工具，完整流程用于关键岗位 |
| **替代率公式为推断** | 天花板公式（§6.3）是模型推导，组织实证需自测校准（见 §13）|
| **20% 边界会漂移** | AI 能力快速演进，今天判定的"不可自动化"明天可能可自动化——边界识别需季度复审 |
| **底座化与业务现场的矛盾** | 底座标准化会牺牲领域灵活性——用"底座三判据"和"从场景长出"纪律约束 |
| **宣传 gap 的双刃剑** | gap 过大且无里程碑收敛 = 团队信心透支——用"进度证据"支撑宣传 |
| **反方视角** | 组织规模小、AI 使用尚在个体探索期时，全套方法论是过度工程——先"先用起来"（08-06），方法论滞后半步 |

---

## 13. 数据缺口

| 缺口 | 说明 |
|:-----|:-----|
| 隐性工作占比 | "隐性工作不识别替代率高估 2-3 倍"为判断性估计，无实证测量（可用 2 周时间审计验证）|
| 替代率天花板 | 组织级 20-30% 为推断区间，无本组织实测（可用 §9.4 净效应指标累积）|
| ≥3 异域案例门槛 | 最小样本量的合理性为经验判断，无统计检验 |
| 灰度三阶段时长 | 影子 2-4 周为建议值，依场景复杂度可伸缩（需实际数据校准）|

---

## 14. 参考来源

| # | 来源 | 类型 | 日期 |
|:--|:-----|:-----|:-----|
| 1 | 用户洞察：AI 导入替代人工七问（个例价值/80-20 边界/人机投入/全貌识别/六步法/底座/做活）| 一手 | 08-20 |
| 2 | 07-08 AI 采用方法论（五阶段闭环/双周例会/P0 场景）| 知识库既有分析 | 07-08 |
| 3 | 08-17 半件事陷阱（委托三前提/完成形态/流程可交责任不交）| 知识库既有分析 | 08-17 |
| 4 | 08-10 三位一体（目标×路径×标准/自研三条件/分级标准）| 知识库既有分析 | 08-10 |
| 5 | 08-19 能力放大器（执行层放大/三层剪刀差 2-10x/1.0-1.5x/<0.7%）| 知识库既有分析 | 08-19 |
| 6 | 08-05 产出经济学（毛利非净利/二次加工）| 知识库既有分析 | 08-05 |
| 7 | 08-06 采用与创新引导（探索优先/创造优先/三阶段）| 知识库既有分析 | 08-06 |
| 8 | 08-13 ticket-as-spec（任务规格化/产出定规格）| 知识库既有分析 | 08-13 |

---

## 15. Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-20 | v1.0 | 创建。七层决策链框架（看清→划清→算清→跑清→复用→做活）；工作全貌识别（产出物反推法+工作包画像四要素+两大盲区）；个例可借鉴性判断（结果价值vs结构价值+相似度×依赖矩阵+四级阶梯+借鉴四问）；80/20 边界识别（四类组成+四标签+可自动化公式+防挖坑三件套）；人机投入比模型（四层分解+天花板公式+关键路径判断洞察）；六步法每步判据与失败模式；底座化（三判据+四层+两反模式+从场景长出纪律）；运营机制（双周五件事+宣传 gap 管理+五指标）|
