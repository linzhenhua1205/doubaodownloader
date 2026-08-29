# 文件一致性治理体系：RISC-V 式 Base 共识 × 扩展机制与元层冲突消解

> **类型**: 深度专题分析（知识库治理方法论）
> **版本**: v1.0
> **日期**: 2026-08-28
> **核心问题**: 知识库/大项目在文件规模增长后，如何系统化识别与批量修复一致性问题？如何用"Base 共识 + 扩展"的机制（RISC-V 模式）构建治理体系？治理资产自身成为新的不一致源头（元层冲突）如何消解？大项目目录如何事前规划（手册/流程/决策/引用 base 分类到位）？过程方案如何标识版本、归档隔离、禁止引用归档信息？
> **概要**: 本文提出"文件一致性治理三层架构"：①**Base 共识层**（冻结的目录/命名/格式/索引规范，类比 RISC-V Base ISA）②**扩展规则层**（模块化、独立版本、可组合，类比 Standard Extensions）③**Profile 组合层**（按文档类型组合规则集，类比 RVA Profiles）。给出 meta-level 冲突的四种形态与三条消解原则（SSOT/生成物分离/检查器注册表）；设计 scan→plan→review→apply→verify 五步批量修复流水线与 L1/L2/L3 三层修复分级；给出大项目目录事前规划五仓模型与 ADR 决策机制；定义版本四态与归档隔离强制检测规则。
> **关键词**: 文件一致性 · 批量修复 · Base共识 · RISC-V · 元层冲突 · meta-governance · 检查器注册表 · SSOT · 目录规划 · ADR · 版本管理 · 归档隔离 · codemod
> **适用对象**: 知识库构建者、研发管理者、DevOps/工具链负责人、技术决策者
> **定位**: 与《过程信息对齐与演化治理》(08-25) 互补——该文管"组织过程信息的稳定性分层"，本文管"文件系统/知识库自身的治理机制设计"；本文是《知识库属性深度治理》(08-12) 的工程化落地方案

## 📑 目录

- [§0 执行摘要](#0-执行摘要)
- [§1 问题定义：三层不一致 × 一层元冲突](#1-问题定义三层不一致--一层元冲突)
  - [1.1 用户的五个观察（问题拆解）](#11-用户的五个观察问题拆解)
  - [1.2 第一性原理：一致性治理的物理本质](#12-第一性原理一致性治理的物理本质)
  - [1.3 元层冲突：治病的药本身有病](#13-元层冲突治病的药本身有病)
- [§2 RISC-V 映射：为什么它是对的参照系](#2-risc-v-映射为什么它是对的参照系)
  - [2.1 RISC-V 治理机制提炼（六机制）](#21-risc-v-治理机制提炼六机制)
  - [2.2 映射总表：RISC-V → 文件一致性治理](#22-映射总表risc-v--文件一致性治理)
  - [2.3 为什么"全面对齐"在此同样失败](#23-为什么全面对齐在此同样失败)
- [§3 三层架构：Base 共识 × 扩展 × Profile](#3-三层架构base-共识--扩展--profile)
  - [3.1 Base 共识层（冻结）](#31-base-共识层冻结)
  - [3.2 扩展规则层（模块化）](#32-扩展规则层模块化)
  - [3.3 Profile 组合层（按文档类型）](#33-profile-组合层按文档类型)
  - [3.4 编码空间治理：目录编号与规则编号](#34-编码空间治理目录编号与规则编号)
- [§4 元层冲突消解：治理资产的治理](#4-元层冲突消解治理资产的治理)
  - [4.1 元层冲突四形态（MECE）](#41-元层冲突四形态mece)
  - [4.2 消解三原则](#42-消解三原则)
  - [4.3 检查器注册表设计](#43-检查器注册表设计)
  - [4.4 规则可追溯链](#44-规则可追溯链)
- [§5 批量修改：scan→plan→review→apply→verify](#5-批量修改scanplanreviewapplyverify)
  - [5.1 五步流水线](#51-五步流水线)
  - [5.2 L1/L2/L3 三层修复分级](#52-l1l2l3-三层修复分级)
  - [5.3 修复安全机制](#53-修复安全机制)
  - [5.4 回归验证与 DoD](#54-回归验证与-dod)
- [§6 大项目目录规划：五仓模型 × ADR × 引用 Base](#6-大项目目录规划五仓模型--adr--引用-base)
  - [6.1 五仓分类模型（事前导入）](#61-五仓分类模型事前导入)
  - [6.2 决策信息：ADR 机制](#62-决策信息adr-机制)
  - [6.3 引用 Base：统一引用注册表](#63-引用-base统一引用注册表)
  - [6.4 目录规划的"MECE + 预留 + 迁移"纪律](#64-目录规划的mece--预留--迁移纪律)
- [§7 版本标识与归档隔离](#7-版本标识与归档隔离)
  - [7.1 版本四态模型](#71-版本四态模型)
  - [7.2 归档隔离强制规则](#72-归档隔离强制规则)
  - [7.3 过程方案的版本生命周期](#73-过程方案的版本生命周期)
- [§8 落地路线图与验收标准](#8-落地路线图与验收标准)
  - [8.1 分阶段实施](#81-分阶段实施)
  - [8.2 每阶段验收标准](#82-每阶段验收标准)
  - [8.3 人工投入的最小化策略](#83-人工投入的最小化策略)
- [§9 结论](#9-结论)
- [交叉链接](#交叉链接)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## §0 执行摘要

**问题**：当文件规模达到数千级（本知识库 1962+ 文件、107 技能、90+ 脚本、43+ spec 文档），一致性治理出现四个叠加困境：①检测工具分散（40+ check 脚本、12 个治理技能各自为政）；②批量修改缺乏工程化流水线（只有针对超节点域的 scan+rectify）；③规范文档之间存在规则漂移（spec/RULE.md/技能内嵌规则三处可能不一致）；④**治理资产自身成为新的不一致源头**——这是最隐蔽、最昂贵的元层（meta-level）冲突。

**结论概要**（六条）：

1. **治理体系必须采用"Base 共识 + 扩展 + Profile"三层架构（RISC-V 模式）**。Base 共识层只放全局冻结规则（目录结构、命名、TOC/Changelog、三文件职责），扩展层放模块化规则（各模块特有要求，独立版本），Profile 层按文档类型组合规则集。这解决"规则漂移"——因为每条规则只有一个权威定义点（SSOT），其余位置只引用不复制。

2. **元层冲突的消解靠三条原则**：①**SSOT 单一事实源**（每条规则只有一个权威定义点）；②**生成物与源分离**（index.md 是编译产物由脚本生成、log.md 是流水账由脚本追加、README.md 是人工条目库——三者职责分离后，索引不会与文件系统漂移）；③**检查器注册表**（所有检查器像 RISC-V 操作码表一样登记：规则 ID/范围/严重度/负责人/状态，防止检查器之间互相矛盾）。

3. **批量修改必须流水线化：scan→plan→review→apply→verify 五步**，且按 L1 格式类（全自动）/ L2 结构类（半自动）/ L3 语义类（人工裁决）分级。参考 Facebook codemod 与 Rust clippy --fix 的工程范式——**先全局扫描、再生成修复清单、人工确认类别、批量执行、回归验证到零**。

4. **大项目目录必须事前规划为"五仓模型"**：手册仓（how-to，可演化）/ 流程仓（process，节点稳定）/ 决策仓（ADR，冻结+版本化）/ 引用 Base 仓（只增不改）/ 概念实体仓（持续演化）。**决策信息必须用 ADR 模式**（状态机：proposed→accepted→superseded→deprecated），对应 RISC-V 的"规范冻结需批准"机制。

5. **过程方案必须显式标识版本四态**：`frozen / evolving / deprecated / archived`。归档区（tmp/bak、_archive）**强制禁止引用**——这要作为一条**独立的检查规则**（R-ARCHIVE）而非约定，因为"归档信息被引用"是知识库最大的隐性错误源之一（引用已废弃方案=传播错误）。

6. **人工投入不是"到处灭火"，而是集中在三个高杠杆点**：①裁决 L3 语义类修复（术语统一、数值口径、决策引用）；②审批 Base 共识层的变更（冻结→解冻→重冻结）；③维护检查器注册表与规则到规范的追溯链。其余全部自动化。

**一句话总结**：**文件一致性治理 = RISC-V 式分层（Base 冻结 × 扩展模块化 × Profile 组合）+ 工程化批量修复流水线 + 治理资产自身的 SSOT 治理；元层冲突的解法不是"更严格的规则"，而是"规则只有一个家"。**

---

## §1 问题定义：三层不一致 × 一层元冲突

### 1.1 用户的五个观察（问题拆解）

| # | 用户观察 | 隐含问题 | 本文回答章节 |
|:-:|:---------|:---------|:------------|
| 1 | 大量文件的一致性问题识别与批量修改 | 检测如何系统化？修改如何工程化？ | §3 三层架构 + §5 流水线 |
| 2 | 类似 RISC-V 的方案、有 base 共识、类似索引机制 | 治理架构的参照系与核心机制是什么？ | §2 RISC-V 映射 + §3 |
| 3 | 治理资产自身成为新的不一致源头（元层冲突） | 规则/检查器/索引自身的漂移如何治理？ | §4 元层冲突消解 |
| 4 | 大项目规划好目录，手册/流程/决策/引用 base 分类到位，事先导入 | 目录的事前分类模型是什么？ | §6 五仓模型 |
| 5 | 过程方案标识版本、及时归档、归档信息不引用 | 版本状态机与归档隔离规则？ | §7 版本与归档 |

### 1.2 第一性原理：一致性治理的物理本质

从第一性原理看，文件一致性问题根源于三个物理事实：

```text
Fact 1  INFORMATION DUPLICATION
       Same fact written in N places -> N copies can diverge
       Divergence grows with N x time x writer count
       -> Consistency problem is an entropy problem

Fact 2  RULES ARE THEMSELVES INFORMATION
       Governance rules are also files -> also duplicated -> also diverge
       Rule divergence is COSTLIER than content divergence
       (a wrong rule corrupts every file it governs)
       -> Meta-level problem is unavoidable, must be designed for

Fact 3  DETECTION NEEDS A YARDSTICK
       You cannot detect inconsistency without a frozen reference
       Frozen reference must be SINGLE, or detection results conflict
       -> SSOT is not a preference, it is a precondition
```

**三个推论**：
- 推论 1：一致性问题 = 信息熵增。治理 = 熵减，而熵减需要持续能量输入（人工/工具），所以"投入大量人工"不是缺陷而是物理必然——关键是**把人工投到熵减效率最高的位置**（§8.3）。
- 推论 2：规则漂移比内容漂移贵一个数量级。一条过时规则会让其管辖的 1000 个文件全部"合规地错误"。所以**治理的第一优先级是治理治理者**（§4）。
- 推论 3：检测需要基准，基准必须唯一。多个检查器各自内置规则快照（如 `kb-dir-registry.py` 声明"SSOT: std-005，本脚本内嵌快照，两者需同步更新"）——**"需同步更新"本身就是漂移的温床**，正确做法是检查器只读 SSOT、不内嵌快照（§4.3）。

### 1.3 元层冲突：治病的药本身有病

**元层冲突的定义**：治理资产（规则文档、检查脚本、索引文件、技能定义）之间的一致性冲突。它与内容冲突的本质区别：

| 维度 | 内容冲突 | 元层冲突 |
|:-----|:---------|:---------|
| 例子 | 两篇文档对某参数说法不一 | 两个检查器对"何为合规"判定相反 |
| 影响面 | 局部（读者困惑） | 全局（所有受管辖文件被错误治理） |
| 发现成本 | 低（读文档即发现） | 高（要审计检查器/规则本身） |
| 修复成本 | 中（改一处） | 高（改规则+改检查器+重跑全量） |
| 传播性 | 线性 | 指数（错误规则 × 管辖文件数） |

**本知识库已观测到的元层冲突形态**（基于现状盘点）：
- `kb-dir-registry.py` 内嵌注册表快照，注释明确写着"SSOT: std-005，两者需同步更新"——**双源并存即漂移隐患** [来源: scripts/tools/kb-dir-registry.py 头部注释]
- 12 个治理技能功能重叠（knowledge-index-manager 已合并原 3 个技能，但仍与 log-reformatter、directory-optimizer、knowledge-health-check 存在边界重叠）[来源: skills/ 目录盘点]
- check/ 目录 40+ 脚本与 spec 六层流转体系之间的规则对应关系无统一注册表 [来源: scripts/check/ 目录盘点]
- `consistency-scan.py v2.0` 的规则来源注明"grep 分散于 3 篇文档"——**规则定义分散在多篇裁决文档中，收敛到脚本后原文档仍存活，双源** [来源: scripts/consistency-scan.py 头部注释]

这些不是"将来可能发生"的问题，是**已经发生**的问题。§4 给出系统解法。

---

## §2 RISC-V 映射：为什么它是对的参照系

### 2.1 RISC-V 治理机制提炼（六机制）

RISC-V 是计算机体系结构中**治理最成功的开放标准**（2010 年启动，2023 年已 100 亿+ 核出货）。它解决了与文件治理同构的问题：**如何在开放协作下保持指令集生态的一致性**。其治理机制可提炼为六条 [来源: RISC-V ISA Specification Vol.1, 2024]:

```text
Mechanism 1  FROZEN BASE ISA
       RV32I/RV64I frozen: never change, only errata
       -> Backward compatibility is a HARD promise
       -> Any implementation must implement base first

Mechanism 2  MODULAR EXTENSIONS
       M/A/F/D/C/V... each optional, independently versioned
       -> Add capability WITHOUT touching base
       -> Extension lifecycle: draft -> frozen -> ratified

Mechanism 3  PROFILE COMPOSITION
       RVA20/RVA22 = base + required extensions for a use case
       -> Ecosystem convergence without universal mandate
       -> Profile is a CONFIGURATION, not a new ISA

Mechanism 4  OPCODE SPACE GOVERNANCE
       Encoding space allocated: standard / reserved / custom
       -> Custom space (CUSTOM-0/1) exists, but never pollutes standard
       -> Allocation is registered, not invented

Mechanism 5  SPEC-IMPLEMENTATION SEPARATION
       Spec is normative and frozen; microarchitecture is free
       -> Implementations compete, spec does not change
       -> Compliance test suite validates conformance

Mechanism 6  VERSIONING + DEPRECATION
       Every extension has a version number
       Deprecation has a timeline; removal after major version
       -> Additive change is the only allowed change
```

### 2.2 映射总表：RISC-V → 文件一致性治理

| RISC-V 机制 | 文件一致性治理对应物 | 本知识库现状 |
|:------------|:---------------------|:-------------|
| **Frozen Base ISA** | Base 共识层：目录结构、命名规范、TOC/Changelog 位置、三文件职责 | 部分存在：RULE.md + design-003 + design-010，但分散未收敛为单一"Base 规范" |
| **Modular Extensions** | 扩展规则层：模块特有规则（07_industry-research 的 Q10 信源配比、supernode 的 R 系列规则） | 存在但未版本化、未独立登记（如 R1-R27 无统一版本锚点） |
| **Profile Composition** | Profile 层：文档类型（深度分析/日报/管理文档/过程方案）的规则组合 | 部分存在：check_format.py 按类型检查，但无显式 Profile 定义文件 |
| **Opcode Space Governance** | 编码空间：目录编号预留 + 检查规则 ID 注册表 | 目录编号有（design-003 §2.2）；**规则 ID 注册表缺失** |
| **Spec-Implementation Separation** | 规则文档（规范）与检查脚本（实现）分离，检查器只读 SSOT | **违反**：kb-dir-registry.py 内嵌快照、consistency-scan.py 内置规则副本 |
| **Versioning + Deprecation** | 规范版本化、废弃规则走 deprecation 周期 | 部分存在：spec README v1.21 有版本；规则级版本化缺失 |

**关键洞察**：RISC-V 治理成功的第一性原因是**"冻结"是硬承诺**——Base ISA 冻结后任何实现必须向后兼容。对应到文件治理：**Base 共识层的每一次变更都必须走"冻结→解冻评审→重冻结"流程，而非随改随用**。这正是 §4.2 原则 1（SSOT）和 §7 版本四态要解决的。

### 2.3 为什么"全面对齐"在此同样失败

与 08-25 文档对"全面对齐 IPD"的批判同理 [1]：

- **全面对齐的失败**：如果所有文件（含日报、临时笔记）都强制满足深度文档的全部规则，治理成本爆炸且收益趋零——日报不需要 TOC、过程方案不需要 Q10 信源配比。
- **完全放任的失败**：如果只有零散检查器没有 Base 共识，每次批量修复都是"打地鼠"，修好 A 类引入 B 类（修复工具自身成为新不一致源）。
- **正确解法 = 分层**：Base 共识（全局必守，数量少而稳定）+ 扩展（模块可选，版本化）+ Profile（按类型组合）。**分层让"规则数量"从 O(全部规则×全部文件) 降为 O(全部规则 + 每文件适用规则)**——这是信息论意义上的必然选择。

---

## §3 三层架构：Base 共识 × 扩展 × Profile

### 3.1 Base 共识层（冻结）

**定义**：所有文件（无论类型）都必须遵守的全局规则。类比 RISC-V Base ISA——数量最小、稳定最高、向后兼容硬承诺。

**候选 Base 规则清单**（基于现有 RULE.md/design-003/design-010 收敛，需逐一评审后冻结）：

| Base 规则 | 内容 | 现状来源 |
|:----------|:-----|:---------|
| B-01 目录结构 | 模块目录 MECE 分层，编号预留 | design-003 §2 |
| B-02 文件命名 | `YYYY-MM-DD-英文描述.md`（日期=创建日） | design-003 §2.4 + kb-index-check C8 |
| B-03 头部元数据 | 类型/版本/日期/概要/关键词 五要素 | consistency-scan R22 |
| B-04 TOC/Changelog | 长文 TOC 在顶部、Changelog 在底部 | check_format R1/R3 |
| B-05 三文件职责 | README=人工条目库 / index=脚本生成 / log=脚本追加 | design-010 v1.3 |
| B-06 内部链接 | 相对路径基准、死链禁止 | check_format R5 + link-validator |
| B-07 代码块纯 ASCII | 代码块内禁止中文 | check_format R4 |
| B-08 量化数据来源 | 数值+单位+基线+条件+来源标注 | check_format R6 + Q3 |

**Base 层治理纪律**：
- 数量上限：**Base 规则 ≤ 20 条**（超过则说明把扩展规则错误地塞进了 Base——类比 RISC-V 拒绝把浮点塞进整数 Base）。
- 变更流程：任何 Base 规则变更需走"提案 → 评审 → 冻结 → 更新检查器 → 全量回归"五步。
- 向后兼容：Base 规则只增不减，废弃走 deprecation（加新规则覆盖旧规则，不删除旧规则定义）。

### 3.2 扩展规则层（模块化）

**定义**：特定模块/领域/流程的规则，类比 RISC-V Standard Extensions——可选、独立版本、只影响该域。

| 扩展 | 适用域 | 示例规则 | 现状 |
|:-----|:-------|:---------|:-----|
| X-SUPERNODE | 超节点文档域 | R1-R27 门禁（VLAN 口径/术语/结构/版本引用） | consistency-scan.py 已实现 |
| X-INDUSTRY | 行业研究专题 | Q10 信源配比（内部≤60% 外部≥40%） | knowledge-doc-writer 已内嵌 |
| X-SPEC | spec 文档域 | 6 层流转、结论先行块、状态字段 | spec-consistency-checker 已实现 |
| X-DAILY | 日报/跟踪 | 日期文件、不写 log、轻量格式 | RULE.md 已约定 |
| X-SKILL | 技能定义域 | frontmatter 规范、注册完整性 | check-skills-registration 已实现 |

**扩展层治理纪律**：
- 每条扩展规则必须有：**ID + 版本 + 范围 + 负责人**。
- 扩展规则的变更不影响其他域（隔离性），但变更后必须重跑该域全量检测。
- 扩展之间不允许互相覆盖语义（如 X-SUPERNODE 的"术语"规则与全局术语表冲突时，全局术语表优先——**层级裁决规则**）。

### 3.3 Profile 组合层（按文档类型）

**定义**：把 Base + 若干扩展组合为"文档类型规则集"，类比 RVA20/RVA22 Profile。写文档时按类型加载 Profile，不必关心具体规则。

| Profile | 适用文档 | 组合 | 核心要求 |
|:--------|:---------|:-----|:---------|
| P-DEEP | 深度分析/专题报告 | Base + X-INDUSTRY + X-SPEC | TOC/来源/信源配比/版本 |
| P-MGMT | 管理方法论文档 | Base + X-SPEC 子集 | 结论先行/决策可溯 |
| P-DAILY | 调研日报/跟踪 | Base 子集 + X-DAILY | 轻量，仅日期文件 |
| P-PROCESS | 过程方案 | Base + X-PROCESS（新建） | 版本标识/状态标注/归档隔离 |
| P-SCRATCH | 临时笔记 | Base 最小子集 | 仅命名+头部 |

**Profile 的价值**：①写作者无需记忆全部规则，选类型即得规则集；②检测器按 Profile 检查（`check_format.py` 已按类型分流，可形式化为 Profile 定义）；③新类型文档 = 新增 Profile 而非修改 Base。

### 3.4 编码空间治理：目录编号与规则编号

类比 RISC-V 操作码空间分配（标准/保留/自定义），文件治理需要两个编号空间：

**① 目录编号空间**（已有基础，需正式化）：
- 标准段：`01_survey / 02_rd / 03_AI / 04_person / 05_tools / 06_others / 07_industry-research`（7 个顶层模块）[来源: design-003 §3.1]
- 预留段：编号跳号（如 02_rd 从 00~92 有大量空号）用于未来模块扩展 [来源: design-003 §2.2]
- 自定义段：各模块内部自由子目录（如 02_rd/03_management/ 下 01~08 分仓）
- **纪律**：新目录必须先在 `std-005` 注册表登记再创建；`kb-dir-registry.py --diff` 检测注册表与实际目录漂移 [来源: scripts/tools/kb-dir-registry.py]

**② 规则编号空间**（**当前缺失，本文核心新增**）：

```text
B-xx   Base consensus rules        (global, frozen)
X-XXX  Extension rules per domain  (modular, versioned)
P-XXX  Profile definitions         (composition, reference only)
R-ARCH  Archive isolation rule     (see S7.2)
```

规则注册表字段（类比 RISC-V 扩展登记表）：

| 字段 | 说明 | 示例 |
|:-----|:-----|:-----|
| rule_id | 规则唯一 ID | X-SUPERNODE-R15 |
| version | 规则版本 | v2.0 |
| scope | 适用目录/文件模式 | 02_rd/02_project/01_superpod/** |
| severity | HIGH/MED/LOW/INFO | HIGH |
| source | 规则来源（SSOT 文档章节） | std-006 §4.2 |
| checker | 实现检查器 | consistency-scan.py |
| status | active/deprecated | active |
| owner | 规则负责人 | 小龙猫 |

**规则注册表与 RISC-V 扩展登记表的同构性**：RISC-V 用 ISA extension registry 防止两个扩展占用相同编码位；文件治理用规则注册表防止两个检查器对同一文件给出冲突判定——**注册表是"一致性的一致性"的物理载体**。

---

## §4 元层冲突消解：治理资产的治理

### 4.1 元层冲突四形态（MECE）

| 形态 | 定义 | 本知识库实例 | 检测手段 |
|:-----|:-----|:-------------|:---------|
| **M1 规则冲突** | 两条规则对同一事实判定相反 | RULE.md 与某技能内嵌规则对 log 更新的要求不一致 | 规则注册表交叉比对 + check-cc-consistency.py |
| **M2 实现漂移** | 检查器实现的规则 ≠ 规范声明的规则 | kb-dir-registry.py 内嵌快照 vs std-005 | --diff 检测（已有）+ 全部检查器推广 |
| **M3 技能重叠** | 多个技能覆盖同一职责，边界模糊 | knowledge-index-manager vs log-reformatter vs directory-optimizer | 技能职责矩阵 + check-skills-registration |
| **M4 索引失真** | 索引声称的 ≠ 文件系统实际的 | index.md 覆盖率 < 100% | analyze-index-coverage.py（已有） |

**四形态的共同根因**：**同一份信息被复制到多个位置，且复制件可独立演化**。消解不是逐个修补，而是从机制上消除"复制-演化"条件——即下节三原则。

### 4.2 消解三原则

**原则 1：SSOT 单一事实源（每条规则只有一个家）**
- 规则定义只存在一处（std-xxx 规范文档），其他位置（技能/脚本/文档）只写"引用"，不写"副本"。
- 当前反例：`consistency-scan.py` 内嵌规则副本、`kb-dir-registry.py` 内嵌注册表快照——**改为启动时从 SSOT 读取**。
- 落地：检查器改造为"读规范 → 生成规则对象 → 执行检测"，规则变更只改规范一处。

**原则 2：生成物与源分离（索引是编译产物）**
- 三类文件职责严格分离（design-010 已定义）：README=人工条目库（源）、index=脚本生成（编译产物）、log=脚本追加（流水账）。
- **关键纪律**：index.md 永远不被人工编辑——它由 `kb-global-index.py` 从文件系统+README 重新生成 [来源: design-010 v1.3]。这样"索引 vs 实际"漂移在机制上不可能发生（M4 根治）。
- 类比：编译器输出（.o 文件）不需要与源码同步维护，重编译即可。

**原则 3：检查器注册表（一致性的一致性）**
- 所有检查器在统一注册表登记（§3.4 表格），提供：`governance-check --list` 列出全部规则、`--check M1` 检测规则冲突、`--trace R15` 追溯规则到规范章节。
- 类比 RISC-V extension registry：防止编码空间冲突。

### 4.3 检查器注册表设计

```text
registry (SSOT: std-006-checker-registry.md)
  +-- rules/       rule definitions (B-xx / X-xxx / R-xxx)
  +-- checkers/    checker -> rules mapping
  +-- profiles/    profile -> rule composition
  +-- drift/       drift detection results (M1/M2/M3/M4)

Single entry: scripts/governance-check.py
  --list          list all rules + status
  --check <id>    run single rule
  --profile <P>   run profile rule set on target
  --drift         detect meta-level conflicts (M1-M4)
  --trace <id>    trace rule -> SSOT section -> checker
```

**对现有资产的整合方式**（不推翻，只收敛）：
- 现有 40+ check 脚本保留为"实现"，通过注册表声明各自实现的规则 ID；
- 新增 `governance-check.py` 作为**唯一入口**（类比 `doc-final-check.sh` 已是文档检查唯一入口的成功先例 [来源: knowledge-doc-writer SKILL.md 第4步]）；
- `spec-consistency-checker` 技能负责 M1/M2 检测（已有 check-cc-consistency / check-design-impl-trace 等脚本可复用）。

### 4.4 规则可追溯链

每条规则应可追溯：**规范章节 → 检查器实现 → 违规实例**。这是 RISC-V"规范是规范、实现是实现、符合性测试验证"的翻版：

```text
SSOT section (std-xxx S4.2)
   |  rule definition (the only normative copy)
   ▼
Rule registry entry (rule_id X-R15, version v2.0)
   |  checker: consistency-scan.py
   ▼
Checker implementation (reads SSOT, not a copy)
   ▼
Violation report (file:line, severity, rule_id)
   ▼
Rectify plan -> apply -> verify (consistency-rectify.py)
```

已有基础：`check-ar-design-trace.py` / `check-sr-ar-trace.py` / `check-design-impl-trace.py` 已实现 SR→AR→Design 追溯 [来源: scripts/check/ 目录]——**同一模式推广到规则层即可**。

---

## §5 批量修改：scan→plan→review→apply→verify

### 5.1 五步流水线

参考 Facebook codemod（大规模代码修改工具）与 Rust clippy --fix 的工程范式 [来源: codemod 论文 "Codemod: A Tool for Large-Scale Codebase Refactoring", Facebook 2014; Rust clippy 文档]:

```text
Step 1 SCAN     Run full detection, produce violation report
                (rule_id, file, line, severity, suggested action)
Step 2 PLAN     Generate fix manifest grouped by fix class:
                L1 auto-fixable / L2 needs confirm / L3 needs human
Step 3 REVIEW   Human confirms L2 items, adjudicates L3 items
                (approve / reject / defer with reason)
Step 4 APPLY    Execute approved fixes, backup first (tmp/bak/)
                Each fix = one atomic change, logged
Step 5 VERIFY   Re-run scan -> remaining violations = 0 for fixed rules
                + no new violations introduced (regression check)
```

**现有资产对应**：`consistency-rectify.py` 已实现 scan→plan→apply→verify 四步（缺 review 门禁），其设计原则"通过 subprocess 调用 scan 复用规则引擎、只处理 FAIL 行、绝不全文替换"正是正确范式 [来源: scripts/consistency-rectify.py 头部]。**本文的增量是：①补 review 人工确认环节；②从超节点域推广到全库；③接入规则注册表**。

### 5.2 L1/L2/L3 三层修复分级

| 级别 | 类型 | 修复方式 | 风险 | 示例 |
|:-----|:-----|:---------|:-----|:-----|
| **L1** | 格式类 | 全自动（脚本批量） | 极低 | TOC 缺失/位置错误、Changelog 不在底部、表格未对齐、文件名不规范 |
| **L2** | 结构类 | 半自动（脚本生成候选，人工确认） | 中 | 死链修复（可选目标多时）、目录归属迁移、引用漂移 |
| **L3** | 语义类 | 人工裁决（工具辅助定位） | 高 | 术语统一（同义词合并方向）、数值口径修正、决策引用更新 |

**分级依据**（第一性）：修复风险 ∝ 修复动作对语义的改变程度。L1 只改结构不改语义（安全）；L3 改语义（必须先理解后改）。**"批量"不等于"自动"——只有 L1 可以全自动，L3 批量自动化 = 批量引入错误**。

### 5.3 修复安全机制

1. **备份先行**：apply 前自动备份到 `tmp/bak/rectify-<timestamp>/`（consistency-rectify.py 已有）。
2. **原子变更**：每个文件修复 = 一个独立变更，可单独回滚（git 层面天然支持）。
3. **只改报告行**：只处理 scan 报告的 FAIL 行，绝不全文替换（避免误伤豁免行）。
4. **豁免机制**：规则自带 exempt 正则（合法语境不判违规，consistency-scan.py 已有 R1/R4/R8 豁免先例）。
5. **dry-run 默认**：`--apply` 默认 dry-run 预览，`--yes` 才执行。

### 5.4 回归验证与 DoD

**DoD（完成定义）**：批量修复的完成不是"修完"，而是**验证完**：
- 目标规则的剩余违规数 = 0；
- 全量重跑未引入新违规（其他规则违规数不增加）；
- 备份区存在且可恢复；
- 修复留痕写入 log（谁/何时/改了什么/为何）。

这与 RULE.md"未落盘 = 未完成"及"当轮分析当轮落盘"的纪律同构 [来源: MEMORY.md 深度分析铁律]——**治理动作自身也必须留痕，否则治理动作成为新的不可追溯源**。

---

## §6 大项目目录规划：五仓模型 × ADR × 引用 Base

### 6.1 五仓分类模型（事前导入）

用户要求"大项目规划好目录，把各类手册、项目流程信息、决策信息、引用 base 信息、各类信息分类到位，事先尽量导入好"。据此设计五仓模型（MECE）：

| 仓 | 内容 | 稳定性 | 消费者 | 治理策略 |
|:---|:-----|:-------|:-------|:---------|
| **手册仓** How-to | 操作手册、指南、SOP、最佳实践 | 中（可演化） | 人（执行者） | 版本化 + 变更留痕 |
| **流程仓** Process | 项目流程、阶段门、活动清单、交付物定义 | 高（节点稳定） | 人+系统（多团队） | 公司级模板冻结，项目级裁剪（08-25 L2） |
| **决策仓** Decision | ADR：为什么做此选择、备选方案、后果 | **极高（冻结）** | 人（决策者+新成员） | ADR 状态机 + 不可改写，只追加 supersede |
| **引用 Base 仓** Reference | 标准/规范/数据源/术语表的唯一权威版本 | **极高（只增不改）** | 人+系统（全库引用） | 加新不删旧 + deprecation 周期 |
| **概念实体仓** Concept | 概念定义、实体档案、方法论文档 | 低（持续演化） | 人+AI（检索） | 自由演化 + 交叉链接 |

**关键区分**（这是用户洞察的精确化）：
- **手册 vs 流程**：手册回答"怎么做"（how），流程回答"谁在什么节点做什么"（who/when）。手册可演化，流程节点要稳定。
- **决策 vs 引用 Base**：决策是"当时的判断"（需冻结+留痕，可被 supersede），引用 Base 是"当前的基准"（只增不改，永不删除）。**决策被 supersede ≠ 删除——历史决策是知识资产**（ADR 核心思想 [来源: Michael Nygard, "Documenting Architecture Decisions", 2011]）。
- **错误示范**：把决策混入手册（决策被后续修改抹掉历史）、把引用 Base 混入概念仓（基准被随意演化）。

### 6.2 决策信息：ADR 机制

**ADR（Architecture Decision Record）** 是决策信息的标准载体 [来源: Nygard 2011; 已在本知识库 spec 术语表登记 "ADR": Architecture Decision Record]：

```text
ADR-NNN: <Title>
Status:   Proposed | Accepted | Superseded by ADR-MMM | Deprecated
Date:     YYYY-MM-DD
Context:  What forces are at play? Why is this decision needed?
Decision: What did we choose? (the ONLY normative part)
Consequences: What does this cost/enable? What must now change?
```

**ADR 治理纪律**（对应 RISC-V 规范冻结机制）：
- 已 Accepted 的 ADR **不可改写**——修订只能新增 ADR 并标记 Superseded（类比规范版本化，加新不删旧）。
- Status 字段是状态机唯一入口：proposed→accepted→superseded/deprecated。
- 每个 ADR 关联：触发它的背景文档 + 影响的 Base/扩展规则 + 落地检查器。

**本知识库落地建议**：新建 `02_rd/03_management/` 下 `04_decisions/` 子目录（或 spec 体系内 ADR 序列），将现有散落的决策文档（如 08-14 战略收敛决策、08-17 系统修改策略）迁移为 ADR 格式。

### 6.3 引用 Base：统一引用注册表

**问题**：文档引用外部标准/数据源时，若无统一基准，会出现"同一标准两个版本被同时引用"（引用漂移，consistency-scan R25 已检测跨文档版本引用漂移）。

**方案**：`reference-registry`（引用 Base 注册表，SSOT）：

```text
ref_id   | canonical name      | version | status | official URL        | local archive
REF-001  | IPMI 2.0 Spec       | Rev1.1  | active | <dmtf url>           | import/...
REF-002  | DMTF DSP0266        | v2023.1 | active | <dmtf url>           | import/...
REF-099  | Legacy Spec X        | v1.0    | deprecated | -              | tmp/bak/...
```

**纪律**：
- 文档引用外部信息时，**必须引用注册表中的 canonical 版本**，禁止直接引用散落副本；
- 引用 Base 变更（新版本发布）= 注册表更新 + 批量检测"哪些文档引用旧版本"（R25 已有雏形）+ 按 Profile 决定是否升级；
- 已有 `tmp/source-registry.json` 雏形 [来源: tmp/source-registry.json]，需正式化为 spec/std-xxx。

### 6.4 目录规划的"MECE + 预留 + 迁移"纪律

1. **MECE 分层**：目录先分后建，新文件必须能归入现有目录（design-003 §2.1）；归不进的先走"预留"而非新建（避免目录膨胀）。
2. **编号预留**：模块编号留跳号（design-003 §2.2），新模块用预留号，不重排旧号。
3. **迁移纪律**：迁移文件 = 更新注册表 + 更新引用（死链检测）+ 留痕 log + **旧位置放归档桩（stub）而非直接删除**（防止外部引用断裂）。
4. **事前导入**：新项目启动时先建目录骨架+五仓+引用 Base 注册表+ADR 序列，再导内容——**"先有书架，再上书"**。用户说的"事先尽量导入好"即此意：目录规划是前置动作，不是事后整理。

---

## §7 版本标识与归档隔离

### 7.1 版本四态模型

每个文件（尤其过程方案）显式标识生命周期状态，防止"隐性契约化"（08-25 §3.4 反例3：探索期信息被协作者当契约消费 [1]）：

| 状态 | 含义 | 可被引用？ | 变更方式 |
|:-----|:-----|:----------|:---------|
| **frozen** | 已冻结（基准/契约/承诺） | ✅ 是（作为基准） | 走 A/B/C 变更分级，重冻结后版本+1 |
| **evolving** | 演化中（认知/内部/探索） | ⚠️ 谨慎（须标注未冻结） | 自由变更，留痕即可 |
| **deprecated** | 已废弃（仍存在供追溯） | ❌ 否（标注替代者） | 冻结内容，标注替代路径 |
| **archived** | 已归档（移入归档区） | ❌ **强制禁止** | 移入 tmp/bak 或 _archive，只读 |

**头部标注格式**（作为 Base 规则 B-03 的扩展）：

```markdown
> **状态**: frozen | evolving | deprecated | archived
> **版本**: v1.2 | **冻结日期**: 2026-08-28 | **替代**: [新文件](...)
```

### 7.2 归档隔离强制规则

**核心规则 R-ARCH**：**归档区（tmp/bak、_archive、import 素材区）禁止被活跃文档引用**。理由：
- 归档区内容 = 已废弃/待处理，引用它 = 引用废弃信息 = 传播错误；
- 归档区会被清理由（tmp/bak 是"废弃区，不引用，确认未替代并迁出后方可用"——RULE.md §4）；
- 引用断裂是知识库最大隐性错误源之一。

**检测实现**（注册表新增规则）：
- 规则 ID：`R-ARCH-01`（归档引用检测）/ `R-ARCH-02`（状态标注完整性检测）
- 检测逻辑：扫描活跃文档中的链接/路径引用，命中 `tmp/bak/`、`_archive/`、`import/` 即 FAIL（豁免：文档自身在归档区内）
- 现有工具基础：`link-validator.py`（5 类链接失效检测）+ `kb-log-link-fix.py` 可扩展 [来源: scripts/check/ + scripts/tools/]

### 7.3 过程方案的版本生命周期

过程方案（P-PROCESS Profile）的完整生命周期：

```text
DRAFT (evolving, labeled NOT FROZEN)
  |  review & approve
  ▼
BASELINE v1.0 (frozen, referenced as benchmark/contract)
  |  change needed?
  +-- Class A (no semantic change) -> update v1.0.1, keep frozen
  +-- Class B (single-domain) -> v1.1, notify consumers
  +-- Class C (cross-domain) -> v2.0, full review + all-side sync
  |  superseded by newer approach
  ▼
DEPRECATED (frozen content, pointer to replacement)
  |  archive after grace period
  ▼
ARCHIVED (moved to archive zone, forbidden to reference)
```

**版本标识纪律**：版本号 = `主版本.次版本`（C 类变主、A/B 类变次）；每次冻结发布记录在文件头+log；**归档动作 = 从活跃区移出 + 在活跃区留归档桩**（标注"已归档，见 <路径>"，桩本身指向归档区但**桩的引用豁免 R-ARCH 检测**——因为桩的职责就是指向）。

---

## §8 落地路线图与验收标准

### 8.1 分阶段实施

| 阶段 | 内容 | 关键产出 | 前置条件 |
|:-----|:-----|:---------|:---------|
| **P0 盘点** | 收敛 Base 规则候选、建立规则注册表骨架、登记现有 40+ 检查器 | std-006 注册表 v0.1 + governance-check.py 骨架 | 本文评审通过 |
| **P1 Base 冻结** | 评审并冻结 Base 规则 ≤20 条、规则 SSOT 化（技能/脚本去内嵌副本） | std-005/006 更新、检查器改造为读 SSOT | P0 |
| **P2 流水线** | scan→plan→review→apply→verify 全库化、L1 自动修复上线 | governance-rectify.py v2.0（含 review 门禁） | P1 |
| **P3 目录重构** | 五仓模型落地、ADR 序列建立、引用 Base 注册表正式化 | 02_rd/03_management/04_decisions/ + std-REF | P1 |
| **P4 归档隔离** | R-ARCH 规则上线、全库归档引用扫描与修复 | R-ARCH-01/02 检查器 + 存量修复 | P2 |
| **P5 元层审计** | M1-M4 定期审计自动化、治理报告 | 月度 meta-governance 报告 | P2 |

### 8.2 每阶段验收标准

- **P0**：注册表覆盖 ≥80% 现有 check 脚本；governance-check --list 可用；
- **P1**：Base 规则冻结 ≤20 条；内嵌副本清零（grep 验证"SSOT 需同步"注释消失）；
- **P2**：L1 规则全自动修复通过率 100%；L3 规则修复全部有人工签字；
- **P3**：新文档 100% 归入五仓；ADR 状态机无违规（无人改写 Accepted 记录）；
- **P4**：全库活跃文档归档引用 = 0（R-ARCH-01 零命中）；
- **P5**：连续 2 个月 M1-M4 审计零新增冲突。

### 8.3 人工投入的最小化策略

用户说"要投入大量人工来处理这事"——正确，但人工应**集中在三个高杠杆点**（其余自动化）：

```text
Human leverage point 1: L3 semantic adjudication
  Term unification direction / numerical calibration / decision refs
  ~20% of violations, ~80% of risk -> human owns this
Human leverage point 2: Base consensus change approval
  Freeze-unfreeze-re-freeze reviews, A/B/C change classification
  Rare but high-impact -> human gates this
Human leverage point 3: Registry & trace chain maintenance
  Rule registry accuracy / SSOT sections / checker mapping
  Steady-state 1-2h/week -> human reviews this
Everything else (L1/L2 mechanics, scans, reports) = automated
```

**反直觉结论**：人工投入最大的地方不是"修复文件"（那是 L1 机械劳动，应自动化），而是**"裁决语义 + 审批共识 + 维护注册表"**（高判断力劳动，自动化无法替代）。这正是用户 MEMORY.md 中"AI 是工具非目标、防降智=判断力不可外包"原则在治理领域的应用 [来源: MEMORY.md 用户核心原则]。

---

## §9 结论

回到用户问题，逐条回答：

| 问题 | 回答 |
|:-----|:-----|
| **大量文件一致性识别与批量修改怎么做？** | 三层架构（Base/扩展/Profile）定义"何为一致"，五步流水线（scan→plan→review→apply→verify）+ L1/L2/L3 分级执行批量修改。检测靠规则注册表统一入口，修改靠"只改报告行+备份+dry-run+回归验证"。 |
| **类似 RISC-V、有 base 共识、索引机制怎么构建？** | Base 共识层冻结 ≤20 条全局规则（类比 RV32I 冻结）；扩展层模块化版本化（类比 M/A/F/D/V）；Profile 按文档类型组合（类比 RVA22）；索引 = 生成物与源分离（index 由脚本生成，杜绝漂移）；规则注册表 = 操作码空间治理。 |
| **治理资产自身成为不一致源头（元层冲突）怎么办？** | 消解三原则：SSOT（规则只有一个家）、生成物与源分离（索引是编译产物）、检查器注册表（一致性的一致性）。M1-M4 四形态可检测可审计，P5 阶段月度审计。 |
| **大项目目录怎么事前规划？** | 五仓模型（手册/流程/决策/引用 Base/概念实体），决策用 ADR 状态机（Accepted 不可改写），引用 Base 注册表（加新不删旧），MECE+编号预留+迁移留桩。先有书架再上书。 |
| **过程方案版本标识与归档？** | 版本四态（frozen/evolving/deprecated/archived），头部显式标注；归档区强制禁止引用（R-ARCH 独立检测规则）；版本生命周期 A/B/C 变更分级 + 归档留桩。 |
| **人工投入很多怎么办？** | 人工集中在三个高杠杆点：L3 语义裁决、Base 变更审批、注册表维护。L1/L2 全部自动化。"批量"不等于"自动"——L3 批量自动化=批量引入错误。 |

**一句话总结**：**文件一致性治理不是"加更多检查器"，而是"让每条规则只有一个家（SSOT）、每个检查器只读家（实现分离）、每次修改走流水线（scan→apply→verify）、每个归档不可引用（R-ARCH）"——RISC-V 的启示是：一致性不是靠更多规则，而是靠规则的治理结构。**

---

## 交叉链接

- [过程信息对齐与演化治理](../../02_rd/03_management/02_project-management/2026-08-25-process-info-alignment-stability-governance-deep-analysis.md) — 四层稳定性模型 + 冻结三判据（本文 §2.3/§7 的哲学上层，本文是其文件系统层面落地）
- [超节点跨领域协作基线管理](../../02_rd/02_project/01_superpod/2026-08-25-supernode-cross-domain-collaboration-baseline-review-release-deep-analysis.md) — A/B/C 变更分级（本文 §7.3 版本生命周期的工程机制来源）
- [知识库属性深度治理](./2026-08-12-kb-attribute-deep-governance.md) — 属性元模型（本文 Base 规则 B-03 头部元数据的理论来源）
- [知识库架构设计全链路](./2026-08-12-kb-architecture-overview.md) — 置信度加权检索 + 人机分工（本文 §8.3 人工高杠杆点的架构上下文）
- [知识处理流水线方法论](./2026-08-18-knowledge-processing-pipeline-methodology.md) — 暂存→加工→沉淀管线（本文五仓模型与 P0-P5 路线的方法论平行）
- [索引与日志 v3 设计](../../../spec/design-010-kb-index-log-v3.md) — 三文件职责分离（本文 §4.2 原则 2 的规范来源）
- [知识库目录设计](../../../spec/design-003-knowledge-directory-design.md) — MECE 分层/编号预留（本文 §6.4 的规范来源）
- [spec 一致性检测器](../../../skills/spec-consistency-checker/SKILL.md) — 6 层一致性检测闭环（本文 §4 元层冲突检测的现有基础）
- [知识库健康检查](../../../skills/knowledge-health-check/SKILL.md) — 全库健康度扫描（本文 R-ARCH 规则检测的可扩展载体）

## 参考文件

### 内部知识库引用

[1] 过程信息对齐与演化治理：契约稳定 × 认知演化的双层体系（2026-08-25，知识库深度分析）— 四层稳定性模型/冻结三判据/隐性契约化
[2] 知识库目录设计与文件变更规范 design-003（2026-08-19 更新）— MECE 分层/编号预留/命名规范
[3] 索引与日志三文件职责设计 design-010 v1.3（2026-08-07）— README/index/log 职责分离与单同步纪律
[4] 知识库属性深度治理（2026-08-12，知识库深度分析）— 属性元模型/自运转机制
[5] 超节点跨领域协作基线管理（2026-08-25，知识库深度分析）— A/B/C 变更分级/基线冻结

### 外部资料引用

[6] RISC-V ISA Specification Volume 1: Unprivileged ISA（RISC-V International, 2024）— Base ISA 冻结/扩展模块化/Profile 组合/编码空间治理机制
[7] Nygard, M. (2011). Documenting Architecture Decisions. *Cognitect* — ADR 格式与"Accepted 不可改写"思想
[8] Facebook (2014). Codemod: A Tool for Large-Scale Codebase Refactoring — scan→plan→apply 批量修改工程范式
[9] Rust Clippy 官方文档（rust-lang.github.io/rust-clippy）— lint 分级与 --fix 自动修复机制
[10] March, J.G. (1991). Exploration and Exploitation in Organizational Learning. *Organization Science* — 人工投入聚焦高杠杆点的 explore/exploit 框架（经 [1] 引述）

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-28 | v1.0 | 首次创建。RISC-V 式三层架构（Base/扩展/Profile）+ 元层冲突四形态与消解三原则 + scan→plan→review→apply→verify 五步批量修复流水线 + 五仓目录模型 + ADR 决策机制 + 引用 Base 注册表 + 版本四态与 R-ARCH 归档隔离规则 + P0-P5 落地路线图 |
