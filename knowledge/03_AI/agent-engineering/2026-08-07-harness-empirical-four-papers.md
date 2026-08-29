# 🔬 Harness 实证化：从「概念辨析」进入「实证测量 + 工程框架」阶段（同日 4 篇）

> **统一主线**: 2026-08-04/05 同日 4 篇 arXiv（OneDayAgent / Skill-Use / State2State / EASy）标志着 Agent Harness 研究从「概念辨析」（Harness 是什么、边界在哪）进入「实证测量 + 工程框架」阶段——**Harness 从被解释的对象变成被测量的自变量与被构建的工程构件**。三篇把 Harness 当测量对象/工程对象，一篇补上 Harness 所需的模型能力供给。
>
> **关键词**: Harness · 实证测量 · 渐进式披露 · 技能使用 · 长时程 · 执行记忆 · 里程碑编排 · 环境学习 · 跨后端泛化
>
> **数据源**: 4 篇 arXiv 官方 HTML 全文（✅ 本日一手抓取，arXiv API 定位 + arxiv.org/html 全文）：
> - [Skill-Use](https://arxiv.org/abs/2608.04828)（2608.04828, 08-05, 华东师大/港科大/复旦/腾讯混元）
> - [OneDayAgent](https://arxiv.org/abs/2608.05013)（2608.05013, 08-04, 浙大/蚂蚁, Ningyu Zhang 组）
> - [EASy](https://arxiv.org/abs/2608.04588)（2608.04588, 08-05, Monash）
> - [State2State](https://arxiv.org/abs/2608.04934)（2608.04934, 08-05, 含 Ya-Qin Zhang 张亚勤）
>
> **素材分级**: ✅ 一手全文 · 🔵 既有知识库锚点（08-05 Harness 进程边界 / WorkBuddy 渐进式加载 / 08-04 编程 Agent 全链路 / 08-03 编排范式）

---

## 📑 目录

- [〇、结论概要](#〇结论概要)
- [一、背景：Harness 概念辨析阶段的遗产](#一背景harness-概念辨析阶段的遗产)
- [二、四篇论文总览](#二四篇论文总览)
- [三、Skill-Use：实证测量——Harness 是能力的条件变量](#三skill-use实证测量harness-是能力的条件变量)
  - [3.1 设计：渐进式披露 + 三分解](#31-设计渐进式披露--三分解)
  - [3.2 关键发现一：可靠技能使用遥不可及（SU 仅 0.613）](#32-关键发现一可靠技能使用遥不可及su-仅-0613)
  - [3.3 关键发现二：Harness 条件性——分数与排名随 harness 变](#33-关键发现二harness-条件性分数与排名随-harness-变)
  - [3.4 关键发现三：检索是主要瓶颈，非执行](#34-关键发现三检索是主要瓶颈非执行)
- [四、OneDayAgent：工程框架——可复用的长时程 Harness](#四onedayagent工程框架可复用的长时程-harness)
  - [4.1 三机制：分解 × 执行记忆 × 验证修复](#41-三机制分解--执行记忆--验证修复)
  - [4.2 跨后端泛化：Harness 独立于模型的实证](#42-跨后端泛化harness-独立于模型的实证)
- [五、EASy：效率工程——成本成为编排的一等公民](#五e-asy效率工程成本成为编排的一等公民)
- [六、State2State：训练供给——环境派生能力](#六state2state训练供给环境派生能力)
- [七、统一框架：Harness 实证化四象限](#七统一框架harness-实证化四象限)
- [八、与知识库理论的闭环：概念辨析 → 实证验证](#八与知识库理论的闭环概念辨析--实证验证)
- [九、批判性审视](#九批判性审视)
- [十、可证伪预测（P1-P5）](#十可证伪预测p1-p5)
- [十一、对国产 Agent 平台/本系统的启示](#十一对国产-agent-平台本系统的启示)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 〇、结论概要

**四篇同日论文合起来回答了一个此前只有理论论证的问题：「Harness 到底影响多大？」——答案是：影响大到足以改变模型排名。**

1. **实证测量（Skill-Use）**：首次把 Harness 作为自变量（同一 8 模型 × 2 Harness 配置），证明**技能使用是 model-harness 配置的属性，不是模型的固定属性**——换 Harness 后分数和排名都变，per-model SU 向量相关性仅中等；最强配置 SU 仅 0.613，「可靠技能使用遥不可及」。
2. **工程框架（OneDayAgent）**：把 Harness 做成可复用工程构件（分解 + 执行记忆 + 验证修复），跨 5 后端 3 模型家族稳定泛化、无需调参（GLM-5.2 后端 0.821 SOTA）——**Harness 可以独立于模型存在并稳定工作**。
3. **效率工程（EASy）**：用 RL 训练 orchestrator 显式建模 executor 成本画像 + milestone-plan-act 并行编排——**成本/效率从工程约束变成可训练目标**。
4. **训练供给（State2State）**：模型能力可从环境交互自生成（state-reaching 任务 + rule-based 验证），无需人类任务设计——**Harness 之上跑的大脑，训练数据可以环境化**。

**一句话**：2026-08 的这 4 篇，把 08-05 知识库「Harness 即适配层/进程边界」的理论命题，从「实践是发现者、进程边界是立法者」的哲学论证，推进到「测量其影响、构建其工程、优化其效率、供给其能力」的实证工程阶段。

---

## 一、背景：Harness 概念辨析阶段的遗产

知识库已沉淀的 Harness 理论层（🔵 均为既有归档）：

| 文档 | 核心论点 | 本批论文的验证关系 |
|:-----|:---------|:------------------|
| 08-05 Harness 即适配层：进程边界同构（12 项映射） | 工具收窄=系统调用面收窄；Subagent=fork/exec；**Harness 约束模型能力** | **Skill-Use 实证**：SU 随 harness 变 = 工具面收窄程度直接改变模型表现 |
| 08-05 WorkBuddy 产品化：Context 五动作/渐进式加载 | 渐进式披露（只暴露名称+描述，按需检索全文） | **Skill-Use 设计直接采用 progressive disclosure**，并实证检索是主要瓶颈 |
| 08-04 编程 Agent 全链路：10 阶段时序流水线 | 上下文工程（95% 水位压缩）/ check 纠偏 | **OneDayAgent**：执行记忆压缩观测 = 上下文工程；验证修复 = check 纠偏 |
| 08-03 Agent 编排范式 / 六层架构 | 单循环 vs 多代理；任务形状决定范式 | **EASy**：可训练 orchestrator = 编排范式的效率维度工程化 |
| 06-26 Agent 技能架构 / MetaSKILL | 技能=结构化文档（何时/何程序/何工具） | **Skill-Use 技能定义一致**（structured documents specifying when/procedure/tools） |
| 07-30 T08 Skill 失效根因 | 上下文丢失/框架实现缺陷 | **Skill-Use 触发瓶颈**：识别"何时适用"失败是独立瓶颈 |
| MEMORY.md 技能经验 | 技能描述裁剪收益极低；换模型后技能效果变化是预期的 | **Skill-Use 实证支撑**：描述质量决定触发率；harness 条件性=换模型效果变化正常 |

---

## 二、四篇论文总览

| 论文 | arXiv | 机构 | 定位 | 一句话贡献 |
|:-----|:------|:-----|:-----|:----------|
| **Skill-Use** | 2608.04828 (08-05) | 华东师大/港科大/复旦/腾讯混元 | **实证测量** | 首个技能使用基准：SU=0.613、harness 条件性实锤 |
| **OneDayAgent** | 2608.05013 (08-04) | 浙大/蚂蚁 (Ningyu Zhang) | **工程框架** | 长时程 harness：分解+记忆+验证修复，跨 5 后端 0.821 SOTA |
| **EASy** | 2608.04588 (08-05) | Monash | **效率工程** | RL 训练成本感知 orchestrator：milestone-plan-act + 并行 |
| **State2State** | 2608.04934 (08-05) | 含张亚勤 | **训练供给** | 环境派生 mid-training：state-reaching 目标 + rule-based 验证 |

> 📌 四篇覆盖 Harness 研究的**完整闭环**：测什么（Skill-Use）→ 怎么建（OneDayAgent）→ 怎么优化（EASy）→ 大脑从哪来（State2State）。

---

## 三、Skill-Use：实证测量——Harness 是能力的条件变量

> ✅ 一手全文（2608.04828），作者含 Yanghua Xiao（肖仰华，复旦知识工场）

### 3.1 设计：渐进式披露 + 三分解

- **问题转向**：已有评测只评「skill 质量」或「对任务成功的贡献」，**不评「agent 能否自己识别相关 skill 并应用」**——这正是知识库 08-05 WorkBuddy「渐进式披露」机制要解决的，但一直无量化
- **设置**：progressive disclosure——agent 只看到 skill 的**名称 + 单行描述 + 文件路径**，必须主动打开文件看到完整 procedure 才能遵循
- **三分解**（Skill-Use 的核心方法论贡献）：
  - **Trigger 触发**：agent 是否调用相关 skill（识别"何时适用"）
  - **Compliance 遵从**：是否忠实遵循规定程序（执行"怎么做"）
  - **Boundary 边界**：是否避免禁止操作（守界"不能做什么"）
  - SU 分数 = 三者的组合，**只在触发后计执行分**
- **规模**：79 个真实 skills + 177 个可执行任务 × 9 域，真实文件落地、Docker 隔离沙箱、轨迹 rubric 评分
- **配置**：8 个 LLM × 2 个 agent harness（Claude Code "CC" / OpenAI Codex）

### 3.2 关键发现一：可靠技能使用遥不可及（SU 仅 0.613）

| 发现 | 数据 | 含义 |
|:-----|:-----|:-----|
| 最强配置 SU | GPT-5.5 under CC = **0.613** | 「可靠技能使用」尚未达成 |
| 触发后最高 Compliance | **0.638** | 触发成功 ≠ 执行到位；执行也是独立瓶颈 |
| Boundary vs Compliance | **Boundary 全类别高于 Compliance** | 模型抑制禁止动作比完成规定流程更可靠（守界易、执行难） |
| 唯一例外 | Security & Compliance 类别 | 遵守步骤但违反禁令——**安全类 skill 恰恰最容易踩边界** |
| 开放权重中端模型 | CC 下仅 ~1/3 任务触发目标 skill | 但条件遵从与 SU 翻倍模型持平 → **缺的是识别不是执行** |

> 📌 对知识库的直接支撑：**「技能描述裁剪收益极低」经验获得实证**——触发瓶颈在识别"何时适用"，描述质量直接决定触发率；同时「守界易、执行难」提示边界检查器（boundary guard）比流程校验器更容易达标。

### 3.3 关键发现二：Harness 条件性——分数与排名随 harness 变

**这是全文最锋利的论断**，直接实证 08-05 的「Harness 约束模型能力」理论：

- **绝对分数和相对排名都随 harness 变**：CC 下头部是 GPT-5.5，Codex 下头部是 Claude Opus 4.8；多个模型在 Codex 下提升、另一些倒退；per-model SU 向量相关性仅中等（Appendix E.1）
- **机制差异**：CC → Codex 压缩 Trigger 分布、拉宽 Compliance 分布——**Codex 降低技能选择门槛，但要求更持续的程序执行**；GPT-5.5 的 Compliance 掉超十分之一
- **结论原文**：*"SU is therefore a property of a model-harness configuration, and rankings under one harness may not transfer to another."*
- **能力画像分化**：强在触发的模型受益于 CC；强在执行的模型在 Codex 下保留更多分数

> 🔵 这为 08-05「Harness 进程边界同构」提供了实证锚点：**工具收窄（系统调用面）的具体实现（CC vs Codex 的工具面设计差异）直接改变模型能力排名**——工具面不是「让模型用工具」，而是「塑造模型能力分布」。

### 3.4 关键发现三：检索是主要瓶颈，非执行

- **注入模式配对实验**（native=只看名称/描述 vs preloaded=全文预载入初始指令）：
  - Preloading 一致提升 Trigger → **检索是 native 注入下主要瓶颈**
  - 但两种模式都触发时，SU 差距很小（点贴近对角线）→ **注入模式只影响技能识别，不影响触发后的规则遵循**
- **技能类型**：文件处理/数据库/数据科学 Compliance 最高（具体程序、命名工具、明确定义操作）；业务分析/软件架构最低（开放规划工作流）
- **库规模**：skill 库 N∈{1,10,20,30} 扩展——触发难度随库增大而上升（识别成本随候选集增长）

---

## 四、OneDayAgent：工程框架——可复用的长时程 Harness

> ✅ 一手全文（2608.05013），浙大张宁豫组 + 蚂蚁；已开源（zjunlp GitHub）

### 4.1 三机制：分解 × 执行记忆 × 验证修复

**问题定义**：日常开放式请求具有 long-horizon（长时程）× cross-environment（跨环境）× multimodal（多模态）三特征，制造三个执行挑战：

| 挑战 | 机制 | 解决 |
|:-----|:-----|:-----|
| **目标漂移**（早期约束被遗忘） | **全局验证修复** | 最终交付物与原始意图 re-align + 局部缺陷 patch |
| **状态丢失**（中间状态跨环境传递失败） | **执行记忆** | 压缩观测 + checkpoint 子任务状态（上下文压力下） |
| **上下文溢出**（交付前预算耗尽） | **任务分解** | 过载请求分解为有界子任务 |

- **统一动作空间**：web / 计算 / 文件 / 多模态工具（= 08-03 六层架构的「工具面」工程化）
- **核心方法论**：三个失败模式会**交互复合**（fixing one in isolation does not suffice）——单一机制不够，必须联合治理

### 4.2 跨后端泛化：Harness 独立于模型的实证

- **AgentIF-OneDay 104 任务**：GLM-5.2 后端 **0.821 新 SOTA**，且**所有任务类型/域/rubric 维度全领先**
- **跨后端稳定性**：同一 harness 跑 5 个后端 LLM × 3 个模型家族，无需后端特定调参
- **执行风格分化**：不同模型在同一 workflow 下产生**不同执行风格**（distinct execution styles）——harness 提供骨架，模型填充风格
- **开源**：harness + 轨迹开源，供社区复现

> 📌 这从工程侧实证了 08-05「Harness = 运行在 LLM 之上的微内核」：**微内核（harness）与运行其上的程序（模型）解耦**——换模型不换 harness，harness 是独立工程资产。

---

## 五、EASy：效率工程——成本成为编排的一等公民

> ✅ 一手全文（2608.04588），Monash（Thuy-Trang Vu / Gholamreza Haffari）

- **问题**：现有 agentic 系统只优化任务成功，忽视执行效率（executor 能力约束 + 计算成本）；router 类方法无法推理**演化中的任务上下文、多步依赖、中间执行反馈**，且对新 executor 泛化差
- **EASy 三组件**：
  1. **成本感知 orchestrator**：LLM orchestrator 显式携带异构 executor 的**能力画像 + 成本画像**（capability and cost profiles）→ 超越纯性能路由的上下文敏感协调
  2. **milestone-plan-act workflow**：分解为 milestones → 构建**依赖感知执行图** → 分配 executor → **并行化独立步骤** → 根据中间结果调整后续决策
  3. **tree-structured rollout 训练**：RL 探索替代 milestone 分解与执行计划；多组件奖励 = 任务正确性 × 执行效率 × 轨迹完整性
- **基准**：数学推理 / 具身决策 / 深度研究——一致的性能-效率权衡优于强基线

> 🔵 与知识库闭环：08-05 五工程「Router=任务分诊」、MEMORY.md「Token 成本=缓存未命中 58% 最大成本」——EASy 把成本意识从**人工工程约束**升级为**可训练目标**（orchestrator 自己学会省成本）。

---

## 六、State2State：训练供给——环境派生能力

> ✅ 一手全文（2608.04934），含 Ya-Qin Zhang（张亚勤）

- **问题**：agent 训练要么 SFT 专家轨迹、要么 RL 人类任务+手工 verifier——都被**外部指定任务和监督信号**瓶颈化，可扩展性/多样性受限
- **State2State 流程**：
  1. 探索策略收集**可复现的 reachable states**
  2. 过滤/采样可学习目标状态 + 配对初始配置 → 构造 **state-reaching 任务**（从初始观测 → 目标观测）
  3. 成功验证 = **rule-based state matching**（无需任务特定测试用例）
  4. 训练 = **GRPO + 动态采样**
- **定位**：agent mid-training（Tu et al. 2025）——在优化特定下游任务前发展环境技能先验
- **结果**：ALFWorld / ScienceWorld 多数设置下独立提升；作为下游 RL 初始化进一步改善最终性能 + 样本效率；**ScienceWorld → ALFWorld 正迁移**（环境派生目标支持更强跨环境泛化）；MobileWorld GUI 独立提升
- **意义**：agent 能力可以**纯从环境自生成**——不需要专家演示、教师模型、人类任务指令，只需要可复现环境状态 + rule-based 验证器

> 📌 对 Harness 的意义：harness 是执行骨架，但骨架上的大脑需要训练。State2State 提供**训练数据环境化**的路径——与 harness 工程化配套，模型侧能力供给也摆脱人类标注瓶颈。

---

## 七、统一框架：Harness 实证化四象限

```
                    Harness 研究阶段演进
  ┌──────────────────────────────────────────────────────┐
  │  概念辨析（2026-06/07，知识库已沉淀）                  │
  │  Harness是什么？边界在哪？= 适配层/微内核/进程边界同构  │
  └───────────────────────┬──────────────────────────────┘
                          │ 2026-08-04/05 转折点
  ┌───────────────────────▼──────────────────────────────┐
  │  实证测量 + 工程框架（本批 4 篇）                       │
  │                                                       │
  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
  │  │ 测什么       │  │ 怎么建       │  │ 怎么优化     │   │
  │  │ Skill-Use   │  │ OneDayAgent │  │ EASy        │   │
  │  │ SU=0.613    │  │ 0.821 SOTA  │  │ cost-aware  │   │
  │  │ harness条件性│  │ 跨5后端泛化  │  │ RL编排       │   │
  │  └─────────────┘  └─────────────┘  └─────────────┘   │
  │                          │                            │
  │  ┌─────────────┐  ┌──────▼──────┐                    │
  │  │ 大脑从哪来   │  │ 执行骨架     │                    │
  │  │ State2State │  │ (Harness)   │                    │
  │  │ 环境派生训练 │  │ 独立于模型   │                    │
  │  └─────────────┘  └─────────────┘                    │
  └──────────────────────────────────────────────────────┘
```

**四篇的互补关系**：Skill-Use 证明 Harness 影响大到改变排名（必须测量）→ OneDayAgent 证明 Harness 可以工程化为独立构件（值得构建）→ EASy 证明 Harness 的效率维度可训练（值得优化）→ State2State 证明 Harness 之上的大脑能力可环境供给（供给可持续）。

---

## 八、与知识库理论的闭环：概念辨析 → 实证验证

| 知识库理论命题（概念辨析阶段） | 本批实证（测量/工程阶段） | 闭环状态 |
|:------------------------------|:--------------------------|:--------:|
| Harness 约束模型能力（进程边界/工具收窄必然性） | Skill-Use：SU 与排名随 harness 变，「model-harness 配置属性」 | ✅ 理论 → 实证 |
| Harness 独立于模型存在（微内核论） | OneDayAgent：跨 5 后端 3 家族稳定泛化、无需调参 | ✅ 理论 → 实证 |
| 渐进式披露是默认机制（WorkBuddy 五动作） | Skill-Use 采用 progressive disclosure + 实证检索是主要瓶颈 | ✅ 机制 → 量化 |
| 技能描述质量决定可用性（描述裁剪收益极低） | Skill-Use：触发率由识别决定，preloading 提升触发 | ✅ 经验 → 数据 |
| 上下文工程 = 压缩 + checkpoint（编程 Agent 全链路） | OneDayAgent：execution memory 压缩观测 + checkpoint 子任务 | ✅ 实践 → 论文 |
| Router = 任务分诊（五工程） | EASy：成本感知 orchestrator + 依赖感知图 + 并行 | ✅ 概念 → 训练 |
| 记忆分层（MindMemOS / 唐杰综述） | OneDayAgent 执行记忆：上下文压力下的状态保持 | ✅ 并行佐证 |

---

## 九、批判性审视

| # | 批判点 | 说明 |
|:-:|:-------|:-----|
| 1 | **Harness 样本太少** | Skill-Use 只有 CC/Codex 2 个 harness——「harness 条件性」结论基于 2 样本，可能放大特定 harness 差异；需 ≥5 harness 复现 |
| 2 | **模型代际混淆** | SU 0.613 的最强配置是 GPT-5.5（当前最强模型），无法区分「模型能力」与「harness 适配度」；开放权重中端模型的表现可能受模型本身限制 |
| 3 | **LLM judge 偏差** | 轨迹 rubric 依赖 LLM judge 评分（Appendix F.3），judge 自身的 harness/模型偏好可能渗入评分 |
| 4 | **OneDayAgent 单基准** | 只有 AgentIF-OneDay 104 任务，SOTA 0.821 缺少跨基准验证；且 GLM-5.2 是浙大/蚂蚁生态，可能有隐性协同 |
| 5 | **EASy 细节缺失** | 成本画像的定义（token 数？延迟？货币？）与具体量化结果在摘要/引言未展开，需要实验章节数字支撑「更强权衡」 |
| 6 | **State2State 环境局限** | 需「可复现状态」+ rule-based 匹配——符号环境（ALFWorld/ScienceWorld）可复现，真实开放环境（网页/软件）的状态不可复现性构成上限；MobileWorld 仅是扩展证据 |
| 7 | **「可靠技能使用」的乐观偏差** | SU=0.613 的「不可靠」部分可能包含任务本身歧义（177 任务的 rubric 是否覆盖所有合法路径？），不全是 agent 缺陷 |

---

## 十、可证伪预测（P1-P5）

| # | 预测 | 时间窗 | 证伪条件 |
|:-:|:-----|:-------|:---------|
| P1 | **Harness 排行榜出现**：≥5 harness × 同模型集的标准化评测成为主流（SU 类指标进入 agent 评测体系） | 2027 | 主流评测仍只看模型不看 harness |
| P2 | **Harness 差异 > 模型差异**在部分能力维度被大规模复现（技能使用/工具遵循），引发「harness 是模型能力的另一半」共识 | 2027 | 复现显示 harness 差异可忽略 |
| P3 | **渐进式披露成为默认设计**：主流 harness（Claude Code/Codex 等）技能只暴露名称+描述+按需检索，全文预载被淘汰 | 2027 | 主流产品仍全文预载技能 |
| P4 | **成本感知编排进入生产**：EASy 类 cost-aware orchestrator 成为 agent 框架标准组件（成本画像 + 里程碑图 + 并行） | 2027 | 生产框架仍只有性能路由 |
| P5 | **环境学习成为标准中间训练阶段**：State2State 类 mid-training 与 SFT/RLVR 并列进入 agent 训练流水线 | 2027 | 训练流水线仍只靠人类任务设计 |

---

## 十一、对国产 Agent 平台/本系统的启示

1. **技能系统设计升级（直接可用）**：Skill-Use 实证「触发瓶颈在识别」——本系统 45+ skills 的**描述质量是第一杠杆**（名称+单行描述决定触发率）；可设计「技能触发率」自检（记录技能被检索/被调用的比率），用数据驱动描述优化（对照 MEMORY.md「描述裁剪收益极低」经验）。
2. **换模型 ≠ 技能退化**：harness 条件性 = 换后端后技能效果变化是**预期的正常现象**（Skill-Use 实证：同一 harness 下模型排名都变）——排查技能问题时先区分「技能本身」与「模型-技能适配」。
3. **执行记忆机制可借鉴**：OneDayAgent 的「压缩观测 + checkpoint 子任务状态」可直接映射到本系统 session 持久化（session-keeper）与每日记忆蒸馏——上下文压力下的状态保持是长会话的工程必修。
4. **边界检查器优先**：Skill-Use「Boundary > Compliance」提示**守界比执行易达标**——安全边界校验（RULE.md 红线/权限）可作为 AI 质量门禁的第一优先级实现，流程遵从校验次之。
5. **成本感知编排（学术支撑）**：EASy 为本系统「token 成本=第一杠杆」提供学术论证——成本意识可以从人工规则升级为可训练组件（若未来自建编排层）。
6. **评测基建**：可参照 Skill-Use 三分解为本系统设计「技能使用基准」（触发/遵从/边界），把「技能是否好用」从主观判断变成可测量指标——与 08-06「AI 产出=毛利非净利」的度量方法论一致。

---

## 参考来源

| # | 来源 | 类型 | 日期 | 用途 |
|:-:|:-----|:----:|:----:|:-----|
| 1 | [arXiv 2608.04828 — Skill-Use: Can LLMs Actually Use Skills in Agentic Harnesses?](https://arxiv.org/abs/2608.04828) | ✅ 一手全文 | 08-05 | §3 全节 |
| 2 | [arXiv 2608.05013 — OneDayAgent: Towards a Long-Horizon Harness for Autonomous Agents](https://arxiv.org/abs/2608.05013) | ✅ 一手全文 | 08-04 | §4 全节 |
| 3 | [arXiv 2608.04588 — EASy: Towards Efficient LLM-Based Agentic System](https://arxiv.org/abs/2608.04588) | ✅ 一手全文 | 08-05 | §5 |
| 4 | [arXiv 2608.04934 — State2State: Environment-Derived Mid-Training for LLM Agents](https://arxiv.org/abs/2608.04934) | ✅ 一手全文 | 08-05 | §6 |
| 5 | 知识库 08-05 Harness 即适配层：进程边界同构（490 行） | 🔵 归档 | 08-05 | §1/§8 |
| 6 | 知识库 08-05 WorkBuddy 产品化（渐进式加载/Context 五动作） | 🔵 归档 | 08-05 | §1/§3.1 |
| 7 | 知识库 08-04 编程 Agent 全链路推理拆解（10 阶段） | 🔵 归档 | 08-04 | §1/§4.1 |
| 8 | 知识库 08-03 Agent 编排范式 / Agent 构成六层 | 🔵 归档 | 08-03 | §1/§5 |
| 9 | 知识库 06-26 Agent 技能架构分解 / MetaSKILL | 🔵 归档 | 06-26 | §1 |
| 10 | 知识库 07-30 T08 Skill 失效根因 | 🔵 归档 | 07-30 | §1 |

**诚实标注**：
- EASy/State2State 全文已抓取，但本分析主要基于摘要+引言+方法关键节，未穷尽实验章节全部数字（EASy 具体成本量化、State2State 具体提升幅度未展开）
- Skill-Use 的附录 E 详细跨 harness 相关性数据未全部提取（仅引用摘要层结论）
- 4 篇均为 preprint（Ongoing work / Work in progress / Preprint），未经同行评审
- web_search 因 API key 失效不可用；论文经 arXiv API 定位 + arxiv.org/html 官方全文抓取

---

## Changelog

- 2026-08-07: 初版。素材 = 4 篇 arXiv 官方 HTML 全文一手抓取（arXiv API 定位 + 全文提取）+ 知识库 Harness 系列 6 个锚点交叉验证；统一主线=Harness 从概念辨析进入实证测量+工程框架；完成三同步（log.md + index.md + git）。
