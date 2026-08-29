# 深度分析方法论体系：从问题到结论的完整链路

> **概要**: 把知识库 100+ 天实践中散落的深度分析单点方法（第一性原理 / MECE / 强逻辑五维 / 材料可信度 / 因果分析 / 认识论 JTB）编排为**一条可执行的六阶段流水线**，并补齐两大操作化缺口：① MECE 从"原则"到"可检验程序"；② 实证数据引用与标注从"零散规则"到"统一协议"。输出为后续设计 skills 提供方法论底座（含方法→skill 映射表）。
>
> **关键词**: 深度分析 · MECE 操作化 · 证据链 · 引用标注协议 · 方法论编排 · 失效模式 · Skill 设计
>
> **版本**: v1.0 | **日期**: 2026-08-19 | **类型**: 深度分析（方法论总纲）
>
> **核心问题**: 什么是"深度分析"？如何稳定地产出深度分析？每个环节该用什么方法、防什么失效？
>
> **定位**: 方法论体系的**编排层**（meta-methodology）——单点方法的深度展开见各专题文档（第一性原理 / 强逻辑 / 材料可信度），本文回答"它们如何组合成一条完整链路"，并补齐 MECE 操作化与实证引用协议两个尚未成文的空白。
>
> **来源**: 本知识库 100+ 天深度分析实战（08-17 质量事故教训）+ 已落盘方法论专题 6 篇交叉互证 + 外部经典（McKinsey MECE / Toulmin / Popper）
>
> **相关**: [`2026-08-19-first-principles-analysis-methodology.md`](./2026-08-19-first-principles-analysis-methodology.md)（第一性原理）· [`2026-07-20-strong-logic-fallacy-detection.md`](./2026-07-20-strong-logic-fallacy-detection.md)（强逻辑）· [`2026-07-13-material-credibility-matrix.md`](./2026-07-13-material-credibility-matrix.md)（材料可信度）· [`2026-07-15-causation-correlation-analysis.md`](./2026-07-15-causation-correlation-analysis.md)（因果）· [`2026-08-17-epistemology-synthesis-deep-analysis.md`](../../02_rd/00_shared/02_concepts/epistemology/2026-08-17-epistemology-synthesis-deep-analysis.md)（认识论综合）

## 目录

- [1. 一句话结论](#1-一句话结论)
- [2. 深度分析的定义与判定标准](#2-深度分析的定义与判定标准)
  - [2.1 定义：三层递进](#21-定义三层递进)
  - [2.2 深度阈值：五个硬性判定项](#22-深度阈值五个硬性判定项)
  - [2.3 浅层 vs 深度的信号对照](#23-浅层-vs-深度的信号对照)
- [3. 全流程六阶段总览](#3-全流程六阶段总览)
- [4. 各阶段工具库：方法与已有资产映射](#4-各阶段工具库方法与已有资产映射)
  - [4.1 阶段1 定问题：杠杆筛选与问题类型学](#41-阶段1-定问题杠杆筛选与问题类型学)
  - [4.2 阶段2 集证据：材料可信度与交叉验证](#42-阶段2-集证据材料可信度与交叉验证)
  - [4.3 阶段3 拆结构：MECE 与第一性原理](#43-阶段3-拆结构mece-与第一性原理)
  - [4.4 阶段4 推结论：Toulmin 与五维特征](#44-阶段4-推结论toulmin-与五维特征)
  - [4.5 阶段5 验结论：证伪与反事实](#45-阶段5-验结论证伪与反事实)
  - [4.6 阶段6 沉淀：格式规范与知识复用](#46-阶段6-沉淀格式规范与知识复用)
- [5. MECE 操作化规范（补齐①）](#5-mece-操作化规范补齐)
  - [5.1 四步操作程序](#51-四步操作程序)
  - [5.2 切分维度选择](#52-切分维度选择)
  - [5.3 常见 MECE 模板](#53-常见-mece-模板)
  - [5.4 检验方法](#54-检验方法)
  - [5.5 失效模式](#55-失效模式)
- [6. 实证数据引用与标注协议（补齐②）](#6-实证数据引用与标注协议补齐)
  - [6.1 证据金字塔：取材优先级](#61-证据金字塔取材优先级)
  - [6.2 引用标注格式规范](#62-引用标注格式规范)
  - [6.3 证据强度 → 主张强度映射](#63-证据强度--主张强度映射)
  - [6.4 交叉验证协议与冲突裁决](#64-交叉验证协议与冲突裁决)
  - [6.5 JTB 工程化：引用标注的认识论根基](#65-jtb-工程化引用标注的认识论根基)
- [7. 方法论全景图](#7-方法论全景图)
- [8. 失效模式总表：各阶段典型陷阱](#8-失效模式总表各阶段典型陷阱)
- [9. 方法论选择决策树](#9-方法论选择决策树)
- [10. Skills 设计参考：方法论 → Skill 映射](#10-skills-设计参考方法论--skill-映射)
- [11. 数据缺口与待完善](#11-数据缺口与待完善)
- [12. 参考文件](#12-参考文件)
- [Changelog](#changelog)

---

## 1. 一句话结论

**深度分析 = 把"断言"还原到不可再分的基底（物理/经济/信息），用显式推理链重建结论，用可追溯的证据支撑，经证伪检验后沉淀为可复用知识的过程。** 它不是单一技巧，而是一条**六阶段流水线**（定问题 → 集证据 → 拆结构 → 推结论 → 验结论 → 沉淀），每个阶段有专属工具与专属失效模式。本库 08-17 质量事故（"面面俱到但都不深"）的根因不是缺方法，而是**缺编排**——方法散落、阶段无门禁、深度无判定标准。本文给出编排总纲与两大补齐：**MECE 操作化**（从原则到程序）与**实证引用标注协议**（从零散规则到统一规范），供后续 skill 设计直接引用。

---

## 2. 深度分析的定义与判定标准

### 2.1 定义：三层递进

| 层 | 定义 | 对应问题 | 反面 |
|:--|:-----|:--------|:-----|
| **L0 信息层** | 完整、准确的转述/汇总 | "它说了什么？" | 断章取义、数据失真 |
| **L1 逻辑层** | 在 L0 之上建立显式推理链 | "为什么是这样？" | 跳跃论证、名词堆叠 |
| **L2 原理层** | 推理链落到不可再分的基底（物理/经济/信息论） | "底层机制是什么？" | 停在惯例/共识层，不追问"自然规律还是人为约定" [来源: 知识库 2026-08-19-first-principles-analysis-methodology.md §2.3] |
| **L3 验证层** | 结论可证伪、证据可追溯、条件可复现 | "凭什么信？错了会怎样？" | 自圆其说、无来源、不可证伪 |

**深度分析的最低要求 = L1 起步、L2 落地、L3 收尾**：只有 L0 是"汇总"；L0+L1 是"逻辑文章"；L0+L1+L2+L3 才是"深度分析"。本库 08-17 质量事故正是大量产出停在 L0+L1（"框架堆名词不深入原理"），AGENT.md 因此明确"框架堆名词不深入原理→不合格" [来源: AGENT.md 产出自检清单]。

### 2.2 深度阈值：五个硬性判定项

用于产出交付前的"深度门禁"（与 knowledge-doc-writer Q6 质量标准对齐）：

| # | 判定项 | 合格标准 | 对应质量原则 |
|:-:|:-------|:---------|:------------|
| 1 | **推理链显式** | 结论由 ≥2 个显式中间步骤导出，无"显然/因此"跳步 | Q4 强逻辑 / 五维-完整性 |
| 2 | **还原到基底** | 至少一层落到物理/经济/信息论基底，并声明成立条件 | Q4 强逻辑 / 第一性原理 |
| 3 | **量化可验证** | 关键数据含数值+单位+基线+条件四要素，且带 [来源: ...] | Q3 量化支撑 / R6 |
| 4 | **可证伪** | 明说"什么证据能推翻本结论" | 强逻辑-证伪性测试 |
| 5 | **沉淀可复用** | 落盘 + log 追加 + 交叉链接，结论可被后续文档引用 | Q5 交叉链接 / 铁律-未落盘=未完成 |

> **工程侧补充**（本库实测约束）：深度分析 ≥8 turns 或 ≥3 次工具调用（检索+读+写）才允许完成；调研档产出 ≥30KB 无上限（调研 runner v1.8 deep 档）[来源: RULE.md 深度分析铁律 / MEMORY.md 调研工具]。这些是**过程量**约束，不能替代上述 5 项**质量**判定——先过质量门禁，再查过程量。

### 2.3 浅层 vs 深度的信号对照

| 维度 | 浅层（不合格） | 深度（合格） |
|:-----|:--------------|:------------|
| 结构 | "面面俱到"每节 3 行 | 每节回答一个具体 why/how，层层递进 |
| 名词 | 术语密集但无推理链 | 每个名词回答"它改变了哪个结论？" |
| 数据 | "显著提升/大幅下降" | "在 X 条件下提升 Y%（从 A 到 B，95% CI: [c,d]）" |
| 结论 | 复述已有共识 | 与现状对比，差异点=创新点；完全一致=还原不够深 [来源: 知识库 2026-08-19-first-principles-analysis-methodology.md §4.3] |
| 来源 | 无出处或单一来源 | 关键断言有出处，量化数据多源收敛 |

---

## 3. 全流程六阶段总览

```
Stage 1          Stage 2          Stage 3          Stage 4          Stage 5          Stage 6
DEFINE           COLLECT          DECOMPOSE        REASON           VERIFY           SINK
(scoping)        (evidence)       (structure)      (inference)      (falsify)        (persist)
|                |                |                |                |                |
leverage filter  credibility mx   MECE split       Toulmin model    falsifiability   format rules
problem typology source grading   first-principles 5-dim self-check counterfactual   index + log
scope statement  cross-validate   causality id     arg-chain viz    cross-validate   cross-links
|                |                |                |                |                |
GATE 1:          GATE 2:          GATE 3:          GATE 4:          GATE 5:          GATE 6:
answerable?      sufficient?      MECE & deep?     explicit?        falsifiable?     persisted?
worth it?        independent?     to bedrock?      fallacy-free?    multi-source?    (write+log+commit)
```

**设计原则**：每阶段一个**门禁**（check gate），不合格不得进入下一阶段——这是 08-17 事故后"未落盘=未完成""当轮分析当轮落盘"铁律的流水线化 [来源: RULE.md 深度分析铁律]。门禁是防"跳跃论证"（A2 谬误）的结构性方案：跳过任何一阶段=论证链断点。

---

## 4. 各阶段工具库：方法与已有资产映射

### 4.1 阶段1 定问题：杠杆筛选与问题类型学

**目标**：确认"这个问题值得深度分析吗"——深度分析是高成本武器（第一性原理需数小时~数天），必须按 ROI 部署 [来源: 知识库 2026-08-19-first-principles-analysis-methodology.md §5]。

**三问筛选**（承第一性原理 SCREEN 步骤）：

| 问题 | 判定 | 反例 |
|:-----|:-----|:-----|
| 杠杆够大吗？ | 决策价值 × 重复次数 × 影响范围 | 中午吃啥不值得还原 |
| 有异常信号吗？ | 成本/质量/能力存在差距，现状无法自圆其说 | 无异常=无突破口 |
| 是还原型问题吗？ | 物理/经济/信息类可还原；系统耦合/价值判断类慎用 | 组织动力学纯还原会失真 [来源: 知识库 2026-08-19-first-principles-analysis-methodology.md §5.2] |

**问题类型学**（决定后续方法组合，见 §9 决策树）：

| 类型 | 典型问法 | 主导方法 |
|:-----|:---------|:---------|
| 分类/归因型 | "什么原因导致 X？" | MECE + 反事实 + 交叉验证 |
| 方案选型型 | "A 还是 B 好？" | 正反双向验证 + Toulmin + 证伪 |
| 性能分析型 | "X 比 Y 快多少？" | 第一性原理 + 可复现约束 + 量化四要素 |
| 根因定位型 | "为什么系统挂了？" | MECE + 第一性原理 + 正反验证 |
| 综述调研型 | "领域现状如何？" | 论证链可视化 + 交叉验证 + 预注册 |
| 解释说明型 | "X 如何工作？" | Toulmin + 证伪 [来源: 知识库 2026-07-20-strong-logic-fallacy-detection.md §3.4] |

**输出物**：问题陈述（含边界声明——分析范围、不做的事、时间窗口）。

### 4.2 阶段2 集证据：材料可信度与交叉验证

**目标**：围绕问题收集证据，先判可信度再引用，杜绝"单一来源当真理"。

**工具**：
- **材料可信度矩阵**：15 种材料按四维（事实/方法/意图/断言）评分，官宣=信号不是证据、Datasheet 承诺值可靠典型值存疑、代码=最高可信单一证据 [来源: 知识库 2026-07-13-material-credibility-matrix.md §2.2]
- **来源分级**：论文/标准原文 > 官方白皮书 > 一线工程报告 > 主流行业分析 > 通用知识（Q1 取材优先）[来源: knowledge-doc-writer Q6]
- **交叉验证三原则**：独立来源（无共同利益）+ 不同方法（不同路径验证同一结论）+ 收敛条件（趋势一致即可，不要求数值一致）[来源: 知识库 2026-07-13-material-credibility-matrix.md §5.2]

**门禁2**：关键量化数据 ≥2 个独立源（RULE.md §6 强制）；无法独立验证的数据显式标注"单源，待验证"——**绝不编造来源或百分比** [来源: MEMORY.md 系统治理方法论]。

### 4.3 阶段3 拆结构：MECE 与第一性原理

**目标**：把问题空间拆到"同层互斥且穷尽"（横切），再对每支纵挖到底（还原）。

**组合拳**（两者正交互补）：

```
MECE horizontal split (this layer complete)     First-principles vertical dig (to bedrock)
       problem                                        problem
      /   |   \                                         |
     A    B    C (mutually exclusive + exhaustive)      |  strip assumptions
   each branch can MECE-split further              |  reduce to physics/econ/info
                                                     |  rebuild bottom-up
```

- MECE 保证**不漏不重**（穷尽抑制遗漏、互斥抑制重复论证）[来源: 知识库 2026-07-20-strong-logic-fallacy-detection.md §3.1.1]
- 第一性原理保证**拆到底**（剥离假设 → 还原 → 重建 → 验证，见 §4.3 对应文档四步框架）
- 因果识别补充：区分相关 vs 因果，防 C 类谬误（相关当因果/事后归因/单一原因/逆向因果/混淆基线）[来源: 知识库 2026-07-15-causation-correlation-analysis.md]

**门禁3**：拆解结果通过 MECE 检验（两两交集为空 ∧ 并集=全集，详见 §5.4）；每个"原理"通过 Feynman 检验（能用自己的话解释 + 说出成立条件）[来源: 知识库 2026-08-19-first-principles-analysis-methodology.md §4.2]。

### 4.4 阶段4 推结论：Toulmin 与五维特征

**目标**：从拆解结果构建显式推理链，产出"每一步可单独验证"的论证。

**工具**：
- **Toulmin 六构件**：数据→结论必须有正当理由（Warrant）+ 支援（Backing）+ 限定词（Qualifier）+ 反驳条件（Rebuttal）——抑制"因为 A 所以 B"的隐藏假设 [来源: 知识库 2026-07-20-strong-logic-fallacy-detection.md §3.1.3]
- **五维特征自检**：完整性（步骤密度）、一致性（无矛盾）、有效性（前提真则结论真）、相关性（无无关信息）、精确性（主张强度 ≤ 证据强度）[来源: 知识库 2026-07-20-strong-logic-fallacy-detection.md §2.2]
- **论证链可视化**：有向图表示（节点=命题，边=推理），反链追踪找隐藏假设、环检测找循环论证 [来源: 同上 §3.1.4]

**门禁4**：推理链无 A 类谬误（循环论证/跳跃论证/结论前置/类比当定理/先验分类/二元对立），每步前提有来源。

### 4.5 阶段5 验结论：证伪与反事实

**目标**：主动攻击自己的结论，确认它经得起否定。

**工具**：
- **证伪性测试**："什么可观测证据能证明我错了？"——永远正确的原理没用（波普尔标准）[来源: 知识库 2026-07-20-strong-logic-fallacy-detection.md §3.3.1]
- **正反双向验证**：构建最有说服力的反方论证链，评估哪方更强（抑制确认偏误）[来源: 同上 §3.2.1]
- **反事实推理**："如果没有 X，还是 Y 吗？"（因果主张专用，提供对比基线）[来源: 同上 §3.2.3 / 知识库 2026-07-15-causation-correlation-analysis.md]
- **独立交叉验证**：来源独立/方法独立/路径独立三维度 [来源: 知识库 2026-07-20-strong-logic-fallacy-detection.md §3.3.2]

**门禁5**：结论可证伪且已过至少一轮对抗检验；验证失败 → 回退到阶段3 检查哪个假设没剥干净。

### 4.6 阶段6 沉淀：格式规范与知识复用

**目标**：把分析结论固化为可复用的知识资产，而非一次性输出。

**工具**（承 knowledge-doc-writer 6 步工作流）：
- **格式规范**：TOC 顶部 / Changelog 底部 / 代码块纯 ASCII / 量化数据行内 [来源: ...] 标注（R1-R6）[来源: scripts/check_format.py]
- **索引与日志**：kb-log-append.py 追加根 log.md；不手工编辑 index/README（脚本批量维护）[来源: knowledge-doc-writer 第5步]
- **交叉链接**：related/depends-on/see-also/contrasts/extends/source-of 六类关系，链接到已有相关页面 [来源: knowledge-doc-writer 第7步]

**门禁6**（铁律三件套）：文档已 write + log 已追加 + git 已 commit，三缺一禁止收尾 [来源: RULE.md 深度分析铁律]。

---

## 5. MECE 操作化规范（补齐①）

> **背景**：MECE 在知识库被引用 20+ 次（文档模板默认应用），但只有"互斥且穷尽"六个字的原则，**没有可执行的程序**——导致"声明遵循 MECE 但章节间明显重叠"（A3 声践不一致）成为高频返工点 [来源: 知识库 2026-07-20-strong-logic-fallacy-detection.md §5.2]。本节补齐操作化。

### 5.1 四步操作程序

```
STEP 1 Pick the split dimension
   - decide "split by what" (single dimension, see 5.2)
   - dimension must serve the decision purpose
        |
STEP 2 Enumerate candidate categories
   - bottom-up: derive categories from instances/evidence,
     not fix a count first then force-fit
   - each category gets a membership criterion
        |
STEP 3 Mutual-exclusivity check
   - pairwise intersection test: can one element belong to both A and B?
     yes -> not mutually exclusive
   - cross-table: rows=cat A, cols=cat B, non-diagonal entries = overlap
        |
STEP 4 Collective-exhaustiveness check
   - union = universe test: do all categories cover every possibility?
   - keep an "others" bucket BUT annotate what it captures
     (otherwise it is an escape from exhaustiveness)
```

**两条铁律**：
1. **先定维度、后定类目**——维度=切分依据，类目=该维度下的取值。维度混淆（G5）是类目非 MECE 的头号根因：把"时间"和"空间"两个维度混在一层切，必然交叉 [来源: 知识库 2026-07-20-strong-logic-fallacy-detection.md §4.5 G5]。
2. **每层一个维度**——MECE 是"层内"性质：同一层只能用同一维度切；不同维度放进不同层（分层展开，P0→P1→Pn）[来源: 同上 §3.1.1 分层抑制跳级]。

### 5.2 切分维度选择

| 维度 | 切分依据 | 适用问题 | 示例 |
|:-----|:---------|:---------|:-----|
| 时间 | 阶段/时期 | 演进、流程、生命周期 | 产品生命周期：引入→成长→成熟→衰退 |
| 空间 | 位置/层级 | 部署、架构、组织 | 集群故障域：机架→行→机房→园区 |
| 结构 | 组成部分 | 系统分解 | 服务器：计算/存储/网络/供电/散热 |
| 过程 | 输入-处理-输出 | 流程拆解 | 数据管线：采集→清洗→加工→存储→消费 |
| 属性 | 特征取值 | 分类分级 | 故障：硬件/软件/网络/人为（且互斥穷尽） |
| 决策树二分 | 是/否逐步细分 | 排查、决策 | 故障排查：电源正常？→ 散热正常？→ … |

**维度正交性检查**：候选维度两两是否正交（一个元素改变维度 A 的取值时，维度 B 的取值不变）？不正交→并入同一层会破坏 MECE。

### 5.3 常见 MECE 模板

| 模板 | 结构 | 典型用途 |
|:-----|:-----|:---------|
| 时间轴 | 过去/现在/未来 或 阶段1..N | 演进分析、路线图 |
| 二分递推 | 是/否 → 子问题递归 | 故障排查、决策树 |
| 金字塔 | 总-分-再分（每层单维度） | 报告结构、WBS |
| 属性枚举 | 互斥属性集合 | 分类学、故障域 |
| 矩阵 | 两个正交维度交叉（每格互斥） | 2x2 策略矩阵、优先级 |
| 流程分段 | 输入→处理→输出 | 管线分析、价值链 |

### 5.4 检验方法

| 检验 | 操作方法 | 可自动化程度 |
|:-----|:---------|:------------|
| 互斥性 | 交叉表：两两类目取交集，检查是否存在"既能进 A 又能进 B"的元素 | 🟡 半自动（需语义判断） |
| 穷尽性 | 枚举边界案例：找"不属于任何类目"的元素；找不到→可能未穷尽 | 🟡 半自动 |
| 可推导性 | 检查类目间是否可互相推导或互为特例（命中=G2 伪结构） | 🟢 脚本辅助（关键词+结构） |
| 维度一致性 | 检查同一层是否混用多个维度（命中=G5 维度混淆） | 🔴 依赖人工（需领域知识） |
| 判定标准完备 | 每个类目是否给出"属于/不属于"的判定标准（无标准=S1 歧义定义） | 🟡 半自动 |

**失败时如何处理**：检验不过 → 回到 STEP 1 换维度，或承认该问题域不适合 MECE（创造性/开放式探索的"穷尽"不可达）[来源: 知识库 2026-07-20-strong-logic-fallacy-detection.md §3.1.1 不适用场景]。

### 5.5 失效模式

| # | 失效 | 症状 | 根因 | 对应谬误 |
|:-:|:-----|:-----|:-----|:---------|
| 1 | 先验分类 | "这个问题有三个方面"但第四方面硬塞 | 先定数量再拟合 | A6 |
| 2 | 伪互斥 | 类目间可互相推导/互为特例 | 维度不清 | G2 |
| 3 | 假穷尽 | 有元素无家可归 | 枚举不全、怕"其他" | A6 变体 |
| 4 | 维度混淆 | 同一层混时间+空间+属性 | 未做维度正交性检查 | G5 |
| 5 | 空洞同构 | "都是 PCIe 设备所以电气相同" | 抓共性丢差异 | G3 |
| 6 | 声明-实践不一致 | 宣称 MECE 实际重叠 | 无检验程序 | A3 |

---

## 6. 实证数据引用与标注协议（补齐②）

> **背景**：实证数据的引用规则散落 4 处——Q1 取材优先（knowledge-doc-writer）、R6 来源标注（check_format.py）、四要素（MEMORY.md/AGENT.md）、材料可信度（07-13 文档）、JTB 三层依据（epistemology 系列）。本节合并为**统一协议**：一条数据从"取材"到"标注"到"验证"到"冲突裁决"的完整规则链。

### 6.1 证据金字塔：取材优先级

```
     papers / standards / specs        <- highest priority (Q1)
   official white papers / datasheets
 first-line engineering reports / release notes / open-source code
    mainstream industry analysis (Gartner/IDC/broker)
        general knowledge / second-hand retelling   <- lowest priority
```

**规则**：同一断言有多种来源可选时，取金字塔上层；上层不可得时用下层并标注层级（"行业分析数据，未经独立验证"）。跨层冲突时下层让位上层 [来源: knowledge-doc-writer Q1 / 知识库 2026-07-13-material-credibility-matrix.md §5.4]。

### 6.2 引用标注格式规范

| 标注类型 | 格式 | 示例 | 强制级别 |
|:---------|:-----|:-----|:---------|
| 行内来源 | `[来源: 出处]` | "缓存未命中占最大成本 57.1% [来源: 知识库 2026-08-14-ai-pipeline-token-optimization] " | R6 必检 |
| 参考文献编号 | `[n]` 文末列表 | "……第一原理 [1]" | R2 必检 |
| 量化四要素 | 数值+单位+基线+条件 | "延迟降低 40%（从 5ms 到 3ms，相同负载）" | Q3 必检 |
| 单源标注 | `[单源: 出处, 待验证]` | 无法交叉验证时的显式降级 | 强制（防编造） |
| 分析vs事实 | 分析性结论标注"本文分析综合" | 方法论操作框架为本文综合，非外部原文 [来源: 知识库 2026-08-19-first-principles-analysis-methodology.md 参考文件] | 强制（防张冠李戴） |

**格式要点**（R6 实测踩坑）：量化数据统一用**行内** `[来源: ...]` 标注——引用块写法 `> 来源: ...` 不被 check_format.py 识别，触发 R6 误报 [来源: knowledge-doc-writer §4b]。

### 6.3 证据强度 → 主张强度映射

**核心原则：主张强度 ≤ 证据强度**（说出口的话不能超过证据能撑住的重量）[来源: 知识库 2026-07-20-strong-logic-fallacy-detection.md §2.2.5]。

| 证据强度 | 可支持的主张 | 措辞模板 | 反例 |
|:---------|:-------------|:---------|:-----|
| 严格数学证明 | 必然性 | "必定/一定" | 把模拟当证明 |
| 受控实验（n≥3，独立验证） | 因果性 | "导致/提升" | 单次实验下"导致"结论 |
| 大样本相关分析 | 相关性 | "相关/关联" | 相关数据说"导致"（C1） |
| 单一样本/案例 | 可能性 | "可能/有案例" | 一个案例推广全体（G1） |
| 理论推导（无实证） | 假设性 | "理论上/推测" | 推测写成实证 |

### 6.4 交叉验证协议与冲突裁决

**触发条件**（何时必须交叉验证）[来源: 知识库 2026-07-13-material-credibility-matrix.md §9.3]：
- 性能数值比较（"A 比 B 快 X 倍"）
- 成本/TCO、可靠性/可用性声称
- 技术能力对比、任何涉及投资决策的数字

**三原则**（承 §4.2）：独立来源 / 不同方法 / 收敛条件（趋势一致即可）。

**冲突裁决优先级**（从硬到软）[来源: 知识库 2026-07-13-material-credibility-matrix.md §5.4]：

```
1 open-source code -> 2 own measurement -> 3 third-party benchmark -> 4 certification
-> 5 release notes -> 6 datasheet guaranteed values -> 7 paper methods -> 8 white paper
-> 9 research reports -> 10 tech blogs -> 11 patents -> 12 bug/issue -> 13 press release
   (press release carries the most marketing inflation)
```

**裁决示例**：官宣"3 倍性能"（⑬）vs MLPerf"1.8-2.5 倍"（③）vs 内部 POC"1.7-2.0 倍"（②）→ 以内部 POC 为准，结论写"自身场景下约 1.7-2.0 倍" [来源: 知识库 2026-07-13-material-credibility-matrix.md §7.3]。

### 6.5 JTB 工程化：引用标注的认识论根基

引用标注不是格式洁癖，而是认识论确证标准（JTB）的工程化落地 [来源: 知识库 2026-08-17-epistemology-synthesis-deep-analysis.md §2.2]：

| JTB 要素 | 知识库工程化 | 对应协议条款 |
|:---------|:-------------|:-------------|
| 信念 Belief | 断言必须有出处，不能"相信"无来源信息 | §6.2 行内来源 |
| 真 Truth | 多源交叉验证 + 数据可复现 | §6.4 交叉验证 |
| 确证 Justification | 三层依据：来源 / 基线 / 条件 | §6.2 四要素 |

**推论**：Gettier 反例启示——静态标注（写了来源）不等于确证成立，必须含动态可修正性（版本化+changelog）。引用标注协议因此要求：数据标注测量时间与口径，版本更新时同步修订引用 [来源: 知识库 2026-08-17-epistemology-synthesis-deep-analysis.md §2.1]。

---

## 7. 方法论全景图

```
                 Deep-Analysis Methodology System
                          |
        -------------------+-------------------
        |                  |                  |
  Epistemic Base      Pipeline Layer      Quality Layer
     (why)               (how)             (check)
        |                  |                  |
  epistemology JTB    6-stage pipeline   5-dim self-check
  (source/baseline/   define->sink      (complete/consistent/
   condition)         gate per stage     sound/relevant/precise)
        |                  |                  |
  12 cognitive ops   +- MECE ops       6-class fallacies
  (observe/abstract/  +- first-principles  (A/D/C/G/S/B)
   reduce/iterate..)   +- material credit  3-layer defense
        |               +- Toulmin          (prevent/detect/fix)
  causality id         +- falsify / cf
  (corr != causation)
```

**层间关系**：认知基础层回答"为什么这套方法可信"（认识论根基），流程编排层回答"每一步做什么"（操作程序），质量保障层回答"怎么知道做对了"（检验标准）。三者 MECE——单点方法文档（第一性原理/强逻辑/材料可信度）分别落在编排层与保障层的纵深展开。

---

## 8. 失效模式总表：各阶段典型陷阱

> 单点方法的失效模式（第一性原理 10 种、谬误 6 类 38 种）已在各专题文档展开，本节聚焦**流水线级**失效——即"方法都对但流程错了"的陷阱。

| 阶段 | 失效模式 | 症状 | 药方 |
|:-----|:---------|:-----|:-----|
| 1 定问题 | 问题错置 | 答了没人问的问题 | 三问筛选 + 问题陈述回读 |
| 1 定问题 | 范围漂移 | 分析中途换问题 | 边界声明 + 门禁1 冻结范围 |
| 2 集证据 | 来源污染 | 二手当一手、官宣当证据 | 来源分级 + 单源显式降级 |
| 2 集证据 | 幸存者偏差 | 只看成功案例 | 主动搜反例 + 失败案例 |
| 3 拆结构 | 先验分类 | 定数量再硬凑 | MECE 四步程序 + 自底向上枚举 |
| 3 拆结构 | 还原过度/不足 | 无限下钻 / 惯例当原理 | 还原深度上限 + Feynman 检验 |
| 4 推结论 | 名词堆叠 | 框架堆名词无推理链（08-17 头号事故） | 每个名词回答"改变了哪个结论" |
| 4 推结论 | 结论前置 | 先定结论再找支撑 | 正反双向验证 + 预注册 |
| 5 验结论 | 确认偏误 | 只找支持证据 | 主动构建反方论证链 |
| 5 验结论 | 证伪缺失 | 结论永远"正确" | "什么证据能推翻它"强制作答 |
| 6 沉淀 | 未落盘 | 分析完就结束 | 铁律三件套（write+log+commit） |
| 6 沉淀 | 无交叉链接 | 孤岛文档 | 关系六类标注 + 反向链接 |

**最高频前三**（本库实证，承第一性原理文档 §6）：① 名词堆叠；② 结论前置/循环论证；③ 还原不足（惯例当原理）[来源: 知识库 2026-08-19-first-principles-analysis-methodology.md §6]。

---

## 9. 方法论选择决策树

```
What is the problem type?
|
+- classification / attribution ("what causes X?")
|   -> S3: MECE + first-principles; S5: counterfactual + cross-validation
|
+- option selection ("A or B?")
|   -> S4: dialectical approach + Toulmin; S5: falsifiability test
|
+- performance analysis ("how much faster is X vs Y?")
|   -> S3: first-principles; S6: reproducibility + 4-element quantification
|
+- root-cause diagnosis ("why did the system fail?")
|   -> S3: MECE + first-principles; S4: dialectical verification
|
+- survey / research ("what is the state of the field?")
|   -> S2: credibility matrix + cross-validation; S4: argument-chain viz
|
+- explanation ("what is X / how does it work?")
    -> S4: Toulmin model; S5: falsifiability test
```

[来源: 知识库 2026-07-20-strong-logic-fallacy-detection.md §3.4 决策树，编排为六阶段版本]

**跨阶段原则**：任何类型都必走六阶段（门禁不可跳）；类型只决定各阶段**用哪个工具**，不决定**是否经过该阶段**。

---

## 10. Skills 设计参考：方法论 → Skill 映射

> 用户诉求：本体系供后续设计 skills 参考。下表给出"方法论 → 可落地的 skill 检查项 → 自动化程度"的映射，新 skill 设计时可直接引用对应章节作为约束底座。

| 方法论 | 可落地检查项（skill 内嵌） | 自动化程度 | 参考文档 |
|:-------|:---------------------------|:----------:|:---------|
| MECE 操作化 | 5 项检验（互斥/穷尽/可推导/维度一致/判定标准） | 🟡 半自动 | 本文 §5 |
| 引用标注协议 | 四要素完备 + 行内 [来源: ...] + 单源降级标注 | 🟢 脚本可检 | 本文 §6 |
| 深度门禁 | §2.2 五判定项（推理链/基底/量化/证伪/沉淀） | 🟡 半自动 | 本文 §2 |
| 谬误预检 | 8 项扫描（强断言/模糊词/跳步/预设分类/二选一/类比/基线缺失/全称量词） | 🟢 脚本可检 | 强逻辑文档 §6.5 |
| 数据主张验证 | 数据模式四要素检查 + 范围错配标记 | 🟢 脚本可检 | 强逻辑文档 §6.3 |
| 自矛盾检测 | 跨段实体属性对齐 + 术语漂移追踪 | 🟡 半自动 | 强逻辑文档 §6.4 |
| 论证链追踪 | 命题提取 → 有向图 → 环/断点/隐藏假设 | 🟡 半自动 | 强逻辑文档 §6.2 |
| 材料可信度 | 15 类材料基线 + 冲突裁决优先级 | 🔴 依赖人工（知识） | 材料可信度文档 |

**Skill 设计四原则**（承强逻辑文档 §6.1）：单功能（一个 skill 检一个维度）、可组合（串联成流水线）、自动化优先（脚本>人工）、自检自反（skill 本身接受同类审查）[来源: 知识库 2026-07-20-strong-logic-fallacy-detection.md §6.1]。

---

## 11. 数据缺口与待完善

1. **MECE 操作化的实证频率分布**：六种失效模式（§5.5）在知识库的实测频率为定性排序，缺大样本统计——后续可对存量文档做一次 MECE 失效扫描建立基线
2. **深度判定项的权重**：五个硬性判定项（§2.2）无量化权重，实际应用时建议"推理链 + 还原到基底"为必过项（一票否决），其余三项可降级
3. **引用标注协议的覆盖审计**：存量文档 R6 合规率未统计，可跑 check_format.py 全库扫描建立基线数据
4. **流水线级失效与单点失效的比例**：08-17 事故归因于"缺编排"，但缺编排 vs 缺方法各自贡献多少，无对照数据
5. **方法论 ROI 的量化**：六阶段全走 vs 简化流程（跳过验证/沉淀）对产出质量的边际贡献，无对照实验

---

## 12. 参考文件

### 内部知识库引用

[1] [`2026-08-19-first-principles-analysis-methodology.md`](./2026-08-19-first-principles-analysis-methodology.md)（第一性原理：四步框架/三大基底/10 失效模式）
[2] [`2026-07-20-strong-logic-fallacy-detection.md`](./2026-07-20-strong-logic-fallacy-detection.md)（强逻辑：五维特征/六类谬误/三层防御/检测 skill）
[3] [`2026-07-13-material-credibility-matrix.md`](./2026-07-13-material-credibility-matrix.md)（材料可信度：四维/15 类/交叉验证/冲突裁决）
[4] [`2026-07-15-causation-correlation-analysis.md`](./2026-07-15-causation-correlation-analysis.md)（因果 vs 相关：C 类谬误）
[5] [`2026-08-17-epistemology-synthesis-deep-analysis.md`](../../02_rd/00_shared/02_concepts/epistemology/2026-08-17-epistemology-synthesis-deep-analysis.md)（认识论综合：JTB 工程化）
[6] [`2026-08-16-cognitive-methods-catalog.md`](../../02_rd/00_shared/02_concepts/epistemology/2026-08-16-cognitive-methods-catalog.md)（认知 12 操作）
[7] [`2026-08-17-principle-engineering-gap-deep-analysis.md`](../../04_person/cognition/2026-08-17-principle-engineering-gap-deep-analysis.md)（原理 vs 工程）
[8] [`2026-08-14-ai-pipeline-token-optimization-five-techniques-deep-analysis.md`](../../03_AI/methodology/2026-08-14-ai-pipeline-token-optimization-five-techniques-deep-analysis.md)（token 成本分解案例）
[9] RULE.md 深度分析铁律（五条）· AGENT.md 产出自检清单 · MEMORY.md 系统治理方法论
[10] skills/knowledge-doc-writer/SKILL.md（Q6 质量标准 / 6 步工作流 / R1-R7 格式规则）

### 外部资料引用

[11] Toulmin, S. *The Uses of Argument* (1958).（论证六构件，经 [2] 转述）
[12] Popper, K. *The Logic of Scientific Discovery* (1934/1959).（证伪主义，经 [2] 转述）
[13] Rasiel, E. *The McKinsey Way* (1999).（MECE 方法源头，麦肯锡问题解决框架）

> ⚠️ **来源标注**：[11]-[13] 为公开经典，经本库 [2] 等内部文档转述核对；本文 §5 MECE 操作化四步程序、§6 引用标注协议、§2 深度判定标准为**本文分析综合**（基于知识库 100+ 天实战归纳），非外部原文结论，已在对应章节标注。

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-19 | v1.0 | 首次创建：深度分析方法论体系总纲（六阶段流水线 + 深度判定标准 + MECE 操作化 + 实证引用标注协议 + 失效模式总表 + Skill 映射），编排知识库 6 篇方法论专题并补齐 2 个操作化缺口 |
