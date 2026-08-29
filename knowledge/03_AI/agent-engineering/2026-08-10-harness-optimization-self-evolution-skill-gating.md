# 🎛️ Harness 从「测量」走向「优化与学习」+ 技能生命周期四门：Harness 研究线双响 × Skill-Native × 自进化门控 × Claude Code auto mode 默认化

> **统一主线**: 2026-08-10 四主题共同标志着 Agent 工程的两个拐点——**① Harness 研究从「实证测量」进入「优化与学习」阶段**：HarnessOpt-Bench 首次把「LLM 优化 harness」变成可测量的基准能力，EvoHarness-RL 首次把「harness 使用策略」变成可学习的 RL 策略；**② 技能生命周期从「开放累积」转向「受控准入」**：Skill-Native 提出技能内生化（训练侧），When Self-Evolution Backfires 证明技能污染不可逆（门控侧），Claude Code auto mode 默认化则是产业侧「自主执行默认化」的标志性事件。
>
> **关键词**: Harness 优化 · Harness 策略学习 · Skill Entropy · 技能原生 · 技能污染相变 · Pre-Commit 门控 · 自主执行默认化 · Bridge 枢纽
>
> **数据源**: 3 篇 arXiv 官方页 + 1 篇 TechCrunch（✅ 本日一手验证）：
> - [HarnessOpt-Bench](https://arxiv.org/abs/2608.06301)（2608.06301, 08-06, cs.AI, 含 NVIDIA Yuan Xue）
> - [EvoHarness-RL](https://arxiv.org/abs/2608.05446)（2608.05446, 08-05, cs.LG, **LLA@COLM 2026 录用**，含 Hanghang Tong / Jingrui He / Qifan Wang）
> - [Skill-Native LLMs](https://arxiv.org/abs/2608.05139)（2608.05139, 08-05, cs.CL, 含 Sanjeev Arora / Mengdi Wang）
> - [When Self-Evolution Backfires](https://arxiv.org/abs/2608.05810)（2608.05810, 08-06, cs.AI）
> - [TechCrunch: Anthropic is turning Claude Code's auto mode on by default](https://techcrunch.com/)（Anthony Ha, 08-09 PT / 08-10 UTC+8, In Brief）— 站内搜索 + AI 分类页**双源确认**；正文为 In Brief 短文，细节受限
>
> **素材分级**: ✅ 一手 arXiv 摘要页 / TechCrunch 双源 · 🔵 既有知识库锚点（08-07 Harness 实证化四篇 / 08-07 Skill-Use 评测缺口 / 08-07 OneDayAgent / 08-07 Bitter Lesson / MEMORY.md Harness=Bridge 枢纽 + 6 步技能注册纪律）
>
> **日期**: 2026-08-10 | **领域**: Agent 工程 / Harness / 技能治理 / AI 编程平台

---

## 📑 目录

- [〇、结论概要](#〇结论概要)
- [一、四主题总览](#一四主题总览)
- [二、Harness 研究线双响：优化 harness × 学习 harness 策略](#二harness-研究线双响优化-harness--学习-harness-策略)
- [三、HarnessOpt-Bench：LLM 优化 harness 的可测量能力（2608.06301）](#三harnessopt-benchllm-优化-harness-的可测量能力260806301)
  - [3.1 评估协议：端到端优化 + 昂贵随机评估 + 预算约束](#31-评估协议端到端优化--昂贵随机评估--预算约束)
  - [3.2 三关键发现：模型 > 编码 harness；native 不总优；增益波动大](#32-三关键发现模型--编码-harnessnative-不总优增益波动大)
- [四、EvoHarness-RL：harness 使用策略的可学习性（2608.05446）](#四evoharness-rlharness-使用策略的可学习性260805446)
  - [4.1 BPE 三状态：策略可面对话的外部状态](#41-bpe-三状态策略可面对话的外部状态)
  - [4.2 两阶段训练：监督微调 + cost-aware GRPO](#42-两阶段训练监督微调--cost-aware-grpo)
  - [4.3 两个动力学：harness annealing 与 harness evolution](#43-两个动力学harness-annealing-与-harness-evolution)
- [五、Skill-Native LLMs：技能熵与跨技能推理（2608.05139）](#五skill-native-llms技能熵与跨技能推理260805139)
  - [5.1 问题缺口：跨技能长程推理无可测度量](#51-问题缺口跨技能长程推理无可测度量)
  - [5.2 Skill Entropy + Skill²-Bench：558 技能 9 域](#52-skill-entropy--skill-bench558-技能-9-域)
  - [5.3 Skill-Entropy RL：技能序列作为训练信号](#53-skill-entropy-rl技能序列作为训练信号)
- [六、When Self-Evolution Backfires：技能污染相变与 VaG（2608.05810）](#六when-self-evolution-backfires技能污染相变与-vag260805810)
  - [6.1 能力污染相变：非单调的自进化](#61-能力污染相变非单调的自进化)
  - [6.2 结构性不可逆：事后回滚只恢复小部分](#62-结构性不可逆事后回滚只恢复小部分)
  - [6.3 VaG：三批评者 + 边际增益子集选择](#63-vag三批评者--边际增益子集选择)
- [七、Claude Code auto mode 默认化：产业侧「自主执行默认化」](#七claude-code-auto-mode-默认化产业侧自主执行默认化)
- [八、统一框架：Harness 研究三阶段 × 技能生命周期四门](#八统一框架harness-研究三阶段--技能生命周期四门)
- [九、批判性审视](#九批判性审视)
- [十、可证伪预测（P1-P6）](#十可证伪预测p1-p6)
- [十一、对国产 Agent 平台 / 本系统的启示](#十一对国产-agent-平台--本系统的启示)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 〇、结论概要

**四主题合起来回答了一个问题：「Harness 与技能，下一步往哪走？」——答案是：Harness 要能被优化、能被学习；技能要能被内化、能被门控。**

1. **Harness 优化可测量（HarnessOpt-Bench）**：首次把「LLM 优化 harness」做成基准——5 个前沿 LLM 作为 optimizer、111 次计分运行、held-out 测试分区防泄漏。关键发现：**optimizer 模型之间的差异 > 它们所经由的 coding harness 之间的差异**——模型是 harness 优化能力的主要变量；native harness 并不总是更优。
2. **Harness 使用策略可学习（EvoHarness-RL, LLA@COLM 2026）**：把 harness 状态抽象为 BPE（Belief/Progress/Experience）三态，用监督微调 + cost-aware GRPO 学习「何时读写外部状态」。Qwen3-8B @ ALFWorld 达 96.9% success，并揭示两个动力学：**harness annealing**（训练把重复 harness 使用内化为模型策略）与 **harness evolution**（状态被精炼为任务自适应基底）。
3. **技能原生化（Skill-Native）**：Skill Entropy 首次量化「跨技能切换难度」，Skill²-Bench（558 技能 × 9 域）揭示 skill-switching gap，Skill-Entropy RL 把 Qwen3-4B 从 34.4%→68.4%、1.7B 从 14.6%→40.1%——**技能从「工具注入」走向「模型内在」**。
4. **技能污染不可逆（When Self-Evolution Backfires）**：自进化存在能力污染相变——池超临界大小后新增技能反降性能，且**结构性不可逆**（事后移除源技能只能恢复小部分）。VaG（Verifier-as-Gatekeeper）三批评者 + 边际增益子集选择，72% pass@1、池小 5×、冻结池可跨 4 backbone 迁移——**技能准入是 pre-commit 必要性，不是 post-hoc 修复**。
5. **产业信号（Claude Code auto mode 默认化）**：自主执行从「可选」变「默认」，是编程 Agent 自主性默认化的标志性事件——与 03-24「keeps it on a leash」构成「先给控制、再松缰绳」的节奏。

**一句话**：08-07 的 Harness 实证化把 harness 从「被解释的概念」变成「被测量的变量」；本批把 harness 变成「被优化的对象、被学习的策略」，同时把技能治理从「开放累积」推向「受控准入」。**Harness 的三次身份跃迁（解释→测量→优化/学习）与技能的四道门（注入→使用→进化→准入）构成 Agent 工程下半场的两条主线。**

---

## 一、四主题总览

| 主题 | 来源 | 定位 | 一句话贡献 | 与本地研究线闭环 |
|:-----|:-----|:-----|:----------|:----------------|
| **HarnessOpt-Bench** | 2608.06301 (08-06) | **测量** | LLM 优化 harness 的可测量能力：模型是主变量 | Bridge 枢纽的人工设计 → 自动化优化的起点 |
| **EvoHarness-RL** | 2608.05446 (08-05, LLA@COLM) | **学习** | harness 使用策略可学习：BPE + annealing/evolution | 「换模型=纯配置」→ 配置也可学 |
| **Skill-Native LLMs** | 2608.05139 (08-05) | **训练** | 技能熵：从工具注入到技能原生 | 08-07 Skill-Use 评测缺口 → 训练侧回应 |
| **When Self-Evolution Backfires** | 2608.05810 (08-06) | **治理** | 技能污染相变 + VaG 门控：准入是 pre-commit | 本地 6 步技能注册纪律 + Skill-Use P4 预测命中 |
| **Claude Code auto mode 默认化** | TechCrunch (08-10) | **产业** | 自主执行默认化：松缰绳的标志性事件 | 08-03 编程 Agent 平台研究线 |

> 📌 四者构成完整链条：**测什么（HarnessOpt-Bench）→ 怎么学（EvoHarness-RL）→ 大脑从哪来（Skill-Native）→ 怎么防止退化（VaG）**，产业侧（Claude Code）同步验证方向。

---

## 二、Harness 研究线双响：优化 harness × 学习 harness 策略

同日两篇 harness 论文（08-05/08-06）看似重复，实则分工清晰——它们回答的是**两个不同的问题**：

| 维度 | HarnessOpt-Bench | EvoHarness-RL |
|:-----|:-----------------|:--------------|
| **优化对象** | harness 本身（代码/提示/工具/编排） | harness 的使用策略（何时读/写/整合外部状态） |
| **谁在优化** | LLM（作为 optimizer 的模型） | RL 训练（cost-aware GRPO） |
| **粒度** | 端到端（seed harness → 迭代 → final candidate） | 状态级（BPE 三态的选择性访问） |
| **测量** | held-out 归一化增益 | 任务成功率（ALFWorld 96.9%） |
| **哲学** | 「harness 是待优化的系统」 | 「harness 是待学习的策略」 |
| **互补关系** | 回答「LLM 能否做好 harness 工程师」 | 回答「harness 使用能否超越人工启发式」 |

**为什么这两篇重要**：08-07 知识库已把 Harness 实证化（Skill-Use 证明 harness 是能力条件变量、OneDayAgent 证明 harness 可独立于模型复用）。本批把两条推论推到终点——**既然 harness 决定能力，那么①谁能把 harness 优化得更好？②harness 使用本身能不能被训练？** 前者是评测问题，后者是学习问题。

---

## 三、HarnessOpt-Bench：LLM 优化 harness 的可测量能力（2608.06301）

### 3.1 评估协议：端到端优化 + 昂贵随机评估 + 预算约束

**HarnessOpt-Bench 的定义性贡献不是「让 LLM 写 harness」，而是「把 harness 优化变成可复现的受控实验」**：

| 协议要素 | 设计 | 意义 |
|:---------|:-----|:-----|
| **输入** | 目标 agent 的 seed harness + 分级评估反馈 + 固定目标评估预算 | 模拟真实「已有系统想改进」场景 |
| **动作** | optimizer（LLM + 编码 harness）编辑 harness、提名最终候选 | 端到端：改代码 → 跑评估 → 再改 |
| **评估边界** | 可信执行环境强制执行；**held-out 测试分区全程不可访问** | 防「评估集过拟合」——搜索期只能用代理反馈 |
| **资源计量** | 计量 target-agent 资源使用 | 昂贵评估预算=真实约束（每次评估都烧 token/时间） |
| **打分** | 最终候选相对 seed 的归一化增益 | 排除任务难度差异的干扰 |

**为什么「held-out 测试分区不可访问」是关键设计**：harness 优化最大的作弊风险是 optimizer 在搜索中把评估集信息编进 harness（类似测试集泄漏）。HarnessOpt-Bench 把「搜索期与测试期严格分离」做成协议的一等公民——这本身就是一个值得本地评测体系借鉴的**评估边界纪律**。

### 3.2 三关键发现：模型 > 编码 harness；native 不总优；增益波动大

> 「Optimizer models separate more than the coding harnesses they act through」——**模型是 harness 优化能力的主要变量**。

1. **optimizer 模型差异 > 编码 harness 差异**：同一模型经不同编码 harness 结果接近，不同模型经同一编码 harness 结果分化——说明 harness 优化能力主要由**模型本身的推理/调试能力**决定，编码工具是放大器而非决定项。
2. **native harness 不总更优**：模型用自己厂商的 native harness 并不稳定优于共享 harness——打破「自家 harness 有隐藏加成」的直觉，**harness 效果是任务×seed 条件性的**。
3. **增益跨任务/seed 波动大**：111 次计分运行显示增益方差大——harness 优化空间存在「任务亲和」与「初始状态依赖」，不能简单排名。

**对本地 Bridge 枢纽的映射**：本系统 Harness=Bridge 枢纽（1204 行，协议适配解耦、换模型=纯配置）是**人工设计**的静态 harness。HarnessOpt-Bench 的意义在于：它给出了「把 Bridge 升级为自优化对象」的评估协议——未来可测「换一个 optimizer 模型，Bridge 能改多好」。

---

## 四、EvoHarness-RL：harness 使用策略的可学习性（2608.05446）

### 4.1 BPE 三状态：策略可面对话的外部状态

**EvoHarness-RL 的核心抽象：把外部 harness 状态重新定义为策略可读写的三类状态**：

| 状态 | 含义 | 类比（本地系统） |
|:-----|:-----|:----------------|
| **Belief（信念）** | 对世界/任务的当前理解 | 上下文中的任务理解摘要 |
| **Progress（进展）** | 到目标为止的进度追踪 | 任务列表/待办状态 |
| **Experience（经验）** | 跨交互的可复用经验 | 记忆系统/技能沉淀 |

「策略可面对话」是关键：BPE 不是给人类看的文档，而是**为 policy 设计的接口**——状态表示的选择决定了 RL 能否学会「何时读、何时更新、何时整合」。

### 4.2 两阶段训练：监督微调 + cost-aware GRPO

| 阶段 | 内容 | 解决的问题 |
|:-----|:-----|:----------|
| **阶段 1：监督 harness 微调** | 教 base agent 学会 harness 动作空间（如何构建有用外部状态） | 冷启动：先学「状态怎么建」 |
| **阶段 2：cost-aware GRPO** | 学习协调策略：选择性读/更新/整合外部状态 | 优化「状态怎么用」——注意是 **cost-aware**（读写有成本） |

**cost-aware 是点睛之笔**：harness 状态访问不是免费的——每次读取消耗上下文/延迟。GRPO 显式建模访问成本，学会「少读、精读、该读才读」。这与本地 08-04 上下文工程「95% 水位压缩」的工程直觉一致，但把它变成了**可训练目标**。

### 4.3 两个动力学：harness annealing 与 harness evolution

**① Harness Annealing（annealing = 退火/内化）**：训练中模型把**重复的 harness 使用模式内化进 policy**——从「频繁调用 harness」转向「选择性外部状态访问」。这验证了一个反直觉命题：**好的 harness 使用是「越来越少用 harness」**——模式被内化后外部调用自然减少（类似人熟练后不再查手册）。

**② Harness Evolution**：progress updates + experience consolidation 把 harness 状态**精炼为紧凑、任务自适应的基底**——状态随任务收敛，不是无限膨胀。

**量化结果**：Qwen3-8B @ ALFWorld 96.9% success（ALFWorld 是家用导航任务，状态空间小、成功率普遍偏高，解读时需注意天花板效应——见批判 §9）。

---

## 五、Skill-Native LLMs：技能熵与跨技能推理（2608.05139）

### 5.1 问题缺口：跨技能长程推理无可测度量

> 现有基准评估「单个技能」，无法回答「模型在推理链中切换技能的能力」。本文定义为 **cross-skill long-horizon tasks**：多步任务、每步需要不同推理技能、且依赖前序输出。

本地 08-07 Skill-Use 评测缺口分析已指出「声明会用 vs 实际会用」的评测滞后；本文从**训练侧**补上另一块拼图——不仅测「是否切换成功」，还要测「切换有多难」并**把难度变成训练信号**。

### 5.2 Skill Entropy + Skill²-Bench：558 技能 9 域

| 要素 | 数值/设计 | 说明 |
|:-----|:----------|:-----|
| **Skill Entropy** | 技能间切换难度的度量 | 从「单技能难度」升级为「技能转移难度」 |
| **Skill²-Bench** | 558 技能 × 9 可验证/开放域 | 每任务赋 skill-entropy 分，分三难度级 |
| **8 frontier + 4 开源模型** | 评估显示 **skill-switching gap**：高熵任务准确率下降 | 模型能做好单技能，但切换是弱项 |

**「技能切换 gap」是第一性发现**：模型能力分布不是均匀的——单技能强 ≠ 跨技能强。这与本地记忆「任务形状决定范式」（窄深 vs 宽浅）同构：**跨技能切换 = 宽浅任务的推理内核**。

### 5.3 Skill-Entropy RL：技能序列作为训练信号

**机制**：模型每步不只预测答案，还预测「本步用了哪个技能」；奖励 = 步级正确性 + 技能序列与 gold 序列对齐的熵奖励。

| 模型 | Skill²-Bench 提升 | 说明 |
|:-----|:------------------|:-----|
| Qwen3-4B-Instruct | 34.4% → **68.4%** | 近乎翻倍 |
| Qwen3-1.7B | 14.6% → **40.1%** | 2.7× |
| OpenR1-Math 现成数据 | 可迁移 | 熵是**可复用训练信号**，不依赖定制数据 |

**意义**：技能从「外部工具注入」（harness 提供技能库）走向「模型内在状态」（模型原生知道何时切技能）——这是 08-07 Skill-Use「检索是主要瓶颈」的**训练侧回应**：与其依赖 harness 检索对，不如让模型内化技能边界。

---

## 六、When Self-Evolution Backfires：技能污染相变与 VaG（2608.05810）

### 6.1 能力污染相变：非单调的自进化

> 自进化 agent 从执行轨迹蒸馏可复用技能，但过程**不是单调的**：超过临界池大小后，新增技能反而降低性能。

**结构性原因——跨轮污染链**：缺陷技能一旦进入决策上下文，就成为后续蒸馏的「参考材料」，形成跨轮污染链。这是**系统性风险而非偶发事故**：技能池越大，污染链越长。

### 6.2 结构性不可逆：事后回滚只恢复小部分

> 移除源技能无法擦除后代已继承的错误推理——**post-hoc rollback 只恢复小部分丢失性能**。

**经验签名**：Terminal-Bench 2 上无条件累积先升后降（把早期增益大部分还回去）；事后移除罪魁技能只恢复小部分。这个「不可逆性」把技能治理从「可事后补救」变成「必须事前拦截」——**pre-commit 必要性**。

### 6.3 VaG：三批评者 + 边际增益子集选择

| 组件 | 功能 | 拦截的污染类型 |
|:-----|:-----|:--------------|
| **批评者 1：结构有效性** | 技能结构是否合理 | 结构性缺陷 |
| **批评者 2：行为无害性** | 技能行为是否安全 | 行为风险 |
| **批评者 3：语义一致性** | 技能语义是否自洽 | 语义污染 |
| **边际增益子集选择** | 顶层移除组合污染 | 组合性污染（单技能无害、组合有害） |

消融证明三批评者**互补且不可互相替代**——各自拦截基本不相交的有害技能类别。

**量化结果**：VaG 每轮提升，**72% pass@1、池小约 5×**；冻结技能池**正迁移到 4 个其他 backbone + 第二个基准**（无需重新进化）——门控后的技能是「干净资产」，可跨模型复用。

**与本地 6 步技能注册纪律的直接闭环**：本地 08-09 教训（spec-consistency-checker W31 登记后 config 重写即丢失、游离 8 天）已确立「注册须确认持久化」；VaG 给出了**通用化的准入门控框架**——本地 6 步注册本质上就是「结构有效性（格式/目录）+ 语义一致性（查重/描述）+ 行为无害性（安全审查）」的简化实例。

---

## 七、Claude Code auto mode 默认化：产业侧「自主执行默认化」

### 7.1 事件事实（TechCrunch 双源确认）

| 要素 | 事实 |
|:-----|:-----|
| 标题 | Anthropic is turning Claude Code's auto mode on by default |
| 作者/时间 | Anthony Ha, 08-09 PT / 08-10 UTC+8（约 7 小时前） |
| 性质 | TechCrunch In Brief（短文）；站内搜索页 + AI 分类页双源确认 |
| 背景锚点 | 03-24 TechCrunch「Anthropic hands Claude Code more control, but keeps it on a leash」（Rebecca Bellan）——auto mode 此前是**可选**模式 |

### 7.2 演进背景：先给控制、再松缰绳

03-24 的「keeps it on a leash」（给更多控制但拴着缰绳）→ 08-10「auto mode 默认开启」：**Anthropic 对自主执行的默认姿态从「人批准」切换为「人监督」**。这与 08-04 OpenAI 放缓 Astra 形成对照——**编程 Agent 的自主性在松绑，通用 Agent 的能力发布在收紧**，二者并不同步（详见产业治理篇的「四重门禁」框架）。

### 7.3 意义：自主执行默认化的三影响

1. **产品形态**：Claude Code 的默认交互从「审批流」变「监督流」——用户默认看到的是 agent 执行而非 agent 请示；失败回滚/审计成为默认能力要求（呼应 HarnessOpt-Bench 的「可信执行环境 + 版本保留」）。
2. **对 harness 的产业验证**：自主性提高 → harness 质量（工具面/控制流/记忆）成为厂商差异化主战场——与 08-03「编程 Agent 差异化在 Harness 深度」判断互证；HarnessOpt-Bench 的「LLM 优化 harness」正是下一竞争点。
3. **对国产 Agent 平台的启示**：自主执行默认化是双刃剑——默认自主提升效率，但需要**更强的门控默认值**（VaG 类 pre-commit 检查）与**可审计性**（每次动作可回放）。

---

## 八、统一框架：Harness 研究三阶段 × 技能生命周期四门

### 8.1 Harness 研究三阶段演进（本系统研究线的推进）

| 阶段 | 时间 | 代表工作 | 身份 |
|:-----|:-----|:---------|:-----|
| **概念辨析** | 07-13 ~ 08-05 | Harness 进程边界同构（12 项映射）、Agent 六层 | Harness = 被解释的概念 |
| **实证测量** | 08-07 | Skill-Use（SU=0.613、harness 条件性）、OneDayAgent（跨 5 后端泛化） | Harness = 被测量的变量 |
| **优化与学习** | **08-10** | HarnessOpt-Bench（被优化的对象）、EvoHarness-RL（被学习的策略） | Harness = 被构建的系统 |

**每次跃迁的驱动**：概念辨析回答「是什么」，实证测量回答「影响多大」，优化与学习回答「谁能做得更好」。**本批完成第三次跃迁。**

### 8.2 技能生命周期四门（从开放累积到受控准入）

| 门 | 阶段 | 代表工作 | 核心约束 |
|:---|:-----|:---------|:---------|
| **注入门** | 技能如何进库 | 本地 6 步注册纪律（三维查重） | 结构有效性 |
| **使用门** | 技能如何被用 | Skill-Use（SU=0.613、渐进式披露） | 触发/合规/边界 |
| **进化门** | 技能如何蒸馏 | EvoHarness-RL（经验整合）、Skill-Native（内生化） | 污染链阻断 |
| **准入门** | 技能如何过审 | **VaG（三批评者 + 边际增益子集）** | pre-commit 拦截 |

**VaG 把「注入门」升级为「准入门」**：本地注册纪律是「入库时查重」，VaG 是「入库前验证 + 组合污染移除」——未来本系统技能治理应把「验证」前移到「准入」。

---

## 九、批判性审视

1. **HarnessOpt-Bench 规模有限**：111 次计分运行、4 个下游任务——统计功效不足以支撑强结论；「held-out 测试分区」的防泄漏设计依赖执行环境可信，跨 harness 的公平性（同一 harness 对 5 模型）仍有配置偏差风险。
2. **EvoHarness-RL 天花板效应**：ALFWorld 状态空间小、成功率普遍偏高，96.9% 的区分度有限；BPE 三态设计是**领域直觉而非理论保证**（为何恰好三态？）；cost-aware GRPO 的「成本」如何量化未披露。
3. **Skill-Native 的标注成本**：「gold skill sequence」从哪来？若需人工标注，可扩展性存疑；技能集（558 个）的定义边界与粒度影响熵值，跨基准可比性待验证；小模型（4B/1.7B）结论能否外推到前沿模型未知。
4. **VaG 的单基准局限**：Terminal-Bench 2 是终端任务域，污染链形态可能域相关；三批评者本身的训练数据/误报率未披露；「池小 5×」是设计结果还是公平比较？冻结池跨 backbone 正迁移是否依赖任务同构？
5. **Claude Code 信息颗粒度**：TechCrunch In Brief 短文，细节缺失——auto mode 默认开启的适用范围（所有用户？企业？）、关闭选项、API 成本影响、回滚保障均未披露。**事实确认、细节待补**。
6. **同源风险**：本批 4 篇论文均为 preprint/短文，无第三方复现；EvoHarness-RL 虽被 LLA@COLM 录用，但录用本身不等于复现。

---

## 十、可证伪预测（P1-P6）

- **P1（高置信）**：12 个月内出现 ≥3 个基于 HarnessOpt-Bench 协议的后续基准/复现（跨任务域、更大模型集），harness 优化成为 Agent 评测标配维度（2027-08 核验）。
- **P2（中置信）**：EvoHarness 类「harness 使用策略学习」进入产品级——至少一家主流 Agent 平台（Anthropic/OpenAI/国产）在其 harness 中加入可学习的状态协调组件（2027-08 核验）。
- **P3（高置信）**：技能准入门控（VaG 类）成为 Agent 平台的默认发布门禁——直接延续 Skill-Use 篇 P4 预测（「技能供应链安全评测成为发布门禁」），本预测将 P4 从「评测」升级为「准入拦截」；预计 2027 年前出现首个产品级实现（2027-08 核验）。
- **P4（中置信）**：Claude Code auto mode 默认化后 6 个月内，至少一家主要竞品（Codex/Cursor）跟进「自主执行默认化」或发布等效模式（2027-02 核验）。
- **P5（中置信）**：Skill-Entropy 类训练信号进入主流后训练配方（RLVR/GRPO 系），「技能序列对齐」成为长程推理后训练的标准组件（2027-08 核验）。
- **P6（低置信）**：harness annealing 在长时程（>100 步）任务上失效——内化收益存在上限，超长时程仍需外部状态（EvoHarness 的 ALFWorld 短程结论的外推边界）（2027-08 核验）。

---

## 十一、对国产 Agent 平台 / 本系统的启示

### 对国产 Agent 平台（产品视角）

1. **自主执行默认化是必答题**：Claude Code 已把默认姿态切到「监督流」，国产平台应尽早设计「默认自主 + 默认可审计」的产品形态，而不是等竞品教育市场。
2. **harness 优化能力 = 下一代差异化**：既然 optimizer 模型差异 > 编码 harness 差异，国产平台应把「模型级 harness 自优化」作为训练目标之一（不是纯 prompt/工具堆叠）。
3. **技能准入做成平台能力**：VaG 三批评者 + 子集选择可作为**技能市场审核机制**的内核——比「应用商店人工审核」可扩展、可比对。

### 对本系统（本地知识库 / Harness=Bridge 枢纽）

1. **Bridge 枢纽的下一步 = 可测可学**：HarnessOpt-Bench 的评估协议（seed + 反馈 + 预算 + held-out）可直接用于评测「换 optimizer 后 Bridge 能改多好」；EvoHarness 的 cost-aware 思想可迁移到本地「检索 keyword-only → 未来 embedding」的访问成本决策。
2. **技能注册纪律升级为「准入门」**：本地 6 步注册（三维查重）是 VaG 的简化版；可增量加「行为无害性」检查（技能是否越权访问）与「组合污染」检查（新技能与既有技能组合是否产生冲突）——08-09 spec-consistency-checker 教训正是污染链的本地实例。
3. **Bitter Lesson 的工程化补充**：08-07 Bitter Lesson 主张「想要能发现的 Agent」；本批 VaG 证明**发现需要门控**——「能发现」与「敢准入」必须成对出现，否则自进化是负和游戏。这是对 Bitter Lesson 的**工程约束侧补充**（不是否定）。

---

## 参考来源

- [HarnessOpt-Bench: Evaluating LLMs at Harness Optimization](https://arxiv.org/abs/2608.06301) — arXiv 2608.06301v1，2026-08-06（✅ 一手摘要页验证）
- [EvoHarness-RL: Learning Self-Evolving Runtime Harness for Long-Horizon LLM Agents](https://arxiv.org/abs/2608.05446) — arXiv 2608.05446v1，2026-08-05，LLA@COLM 2026（✅ 一手摘要页验证）
- [Toward Skill-Native LLMs: Skill Entropy for Benchmarking and Training Long-Horizon Reasoning](https://arxiv.org/abs/2608.05139) — arXiv 2608.05139v1，2026-08-05（✅ 一手摘要页验证）
- [When Self-Evolution Backfires: Pre-Commit Gating against Skill Contamination in LLM Agents](https://arxiv.org/abs/2608.05810) — arXiv 2608.05810v1，2026-08-06（✅ 一手摘要页验证）
- [TechCrunch: Anthropic is turning Claude Code's auto mode on by default](https://techcrunch.com/) — Anthony Ha，08-09 PT（✅ 站内搜索 + AI 分类页双源；正文 In Brief 细节受限）
- [TechCrunch: Anthropic hands Claude Code more control, but keeps it on a leash](https://techcrunch.com/) — Rebecca Bellan，2026-03-24（背景锚点）
- 本地：[Harness 实证化四篇](2026-08-07-harness-empirical-four-papers.md)（08-07，Skill-Use/OneDayAgent/EASy/State2State）
- 本地：[技能使用评测缺口](2026-08-07-skill-use-eval-gap-deep-analysis.md)（08-07，含 P4 预测——本批 VaG 直接命中）
- 本地：[OneDayAgent 长时程 Harness](2026-08-07-onedayagent-long-horizon-harness-deep-analysis.md)（08-07）
- 本地：[Bitter Lesson 深潜](knowledge/07_industry-research/18_methodology-framework/2026-08-07-bitter-lesson-deep-analysis.md)（08-07，注：用户简报标注 08-08，实际归档于 08-07）
- 本地：[Harness 进程边界同构](2026-08-05-harness-os-process-boundary-isomorphism.md)（08-05）
- 本地：MEMORY.md（Harness=Bridge 枢纽 1204 行；6 步技能注册纪律；08-09 spec-consistency-checker 教训）

---

> **诚实标注**：4 篇 arXiv 论文均为 2026-08 初 preprint（EvoHarness-RL 已获 LLA@COLM 录用），未经第三方复现；TechCrunch 为 In Brief 短文，细节（适用范围/关闭选项/成本影响）未披露。ALFWorld/Terminal-Bench 2 为小规模任务域，结论外推需谨慎。本分析为学术解读，非投资或采购建议。

---

## Changelog

- 2026-08-10：创建。素材=3 篇 arXiv 摘要页一手验证 + TechCrunch 双源确认；主线=Harness 研究三阶段跃迁（概念→测量→优化/学习）+ 技能生命周期四门（注入/使用/进化/准入）；与 08-07 Harness 实证化/08-07 Skill-Use P4 预测命中/08-07 Bitter Lesson 工程化补充/本地 6 步注册纪律形成闭环；Claude Code auto mode 默认化作为产业侧标志事件。
