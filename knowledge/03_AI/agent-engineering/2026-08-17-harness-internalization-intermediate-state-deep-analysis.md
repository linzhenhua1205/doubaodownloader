# Harness 是中间状态：外部编排逻辑的模型内化规律

> **类型**: 深度技术分析 | **日期**: 2026-08-17 | **版本**: v2.0（质量提升：外部一手源补全 + 量化锚点 + 事实修正）
> **来源**: 用户洞察（Harness ≈ prompt engineering 中间状态假设）+ 论文一手实证（EvoHarness-RL 2608.05446 / Skill-Native LLMs 2608.05139 / Progressive Crystallization 2607.07052 / FLAN 2109.01652 / InstructGPT 2203.02155）+ 知识库实证（harness annealing / 结晶化 / loop 验证）
> **适用范围**: Agent 架构 / Harness 设计 / AI 基础设施规划
> **相关**: [`2026-08-10-harness-optimization-self-evolution-skill-gating.md`](2026-08-10-harness-optimization-self-evolution-skill-gating.md)（annealing 实证）· [`2026-08-10-progressive-crystallization-aiops-deterministic-workflow-deep-analysis.md`](2026-08-10-progressive-crystallization-aiops-deterministic-workflow-deep-analysis.md)（结晶化）· [`2026-08-17-loop-verification-independence-economy-deep-analysis.md`](2026-08-17-loop-verification-independence-economy-deep-analysis.md)（验证独立性）

## 📑 目录

1. 一句话结论
2. 假设提出：Harness ≈ prompt engineering 的中间状态
3. 历史类比：两轮"外部补偿→内化"的完整周期（含量化实证）
4. 内化机制：为什么外部逻辑会被模型吸收（第一性原理）
5. 论文一手实证：2026 年三条独立证据链的统一
6. 内化边界：什么会被吸收，什么永远留在外部（MECE + 实例）
7. 可证伪判据与预测（含观测信号）
8. 工程启示：今天写 Harness 的意义
9. 风险与批判
10. 数据缺口
11. 参考来源
12. Changelog

---

## 1. 一句话结论

**用户的假设成立且已被 2026 年三条独立论文证据链直接支持：Harness（编排层/多 Agent 制衡）与 prompt engineering 同属「外部补偿」机制——模型能力不足时，用人的精巧逻辑补足；模型能力增强后，这些逻辑通过训练被内化为模型自身行为。** 证据链：①历史周期（手写特征→深度学习；few-shot→指令跟随→CoT 涌现）证明内化是规律不是特例，其中 FLAN 指令微调把 137B 模型 zero-shot 推到超越 175B GPT-3（20/25 任务）是量化铁证（[来源: arXiv:2109.01652]）；②EvoHarness-RL 在 Qwen3-8B/ALFWorld 上达到 96.9% success，并实证了 **harness annealing**——训练把重复 harness 使用内化为 policy，agent 从频繁 harness 调用转向选择性外部状态访问（[来源: arXiv:2608.05446, LLA@COLM 2026]）；③Skill-Entropy RL 用技能熵作训练信号，把 Qwen3-4B 的跨技能长程任务得分从 34.4% 提升到 68.4%（[来源: arXiv:2608.05139]）。**但内化有边界：被吸收的是"认知模式"（分解/验证/对抗），留在外部的是"环境接口"（工具/知识库/物理世界）——今天的 Harness 是"模型待内化能力的清单 + 未来接口的雏形"，写 Harness 的经验不会白费。**

---

## 2. 假设提出：Harness ≈ prompt engineering 的中间状态

### 2.1 类比结构（MECE：补偿对象/人的工作/补偿内容/内化结果 四维对齐）

| 维度 | Prompt Engineering | Harness（编排层） |
|:-----|:-------------------|:------------------|
| 补偿对象 | 单次推理的能力不足 | 长程任务的能力不足 |
| 人的工作 | 写提示词（引导输出） | 写编排逻辑（分解/制衡/验证） |
| 补偿内容 | 知识/格式/推理提示 | 任务分解/多 Agent 对抗/验证闭环 |
| 模型变强后 | 提示词被内化（指令跟随原生） | 编排逻辑被内化（任务分解/自验证原生） |
| 内化实证 | FLAN: 137B 指令微调 zero-shot 超 175B GPT-3（20/25 任务）[来源: arXiv:2109.01652] | EvoHarness annealing: Qwen3-8B 训练后 harness 调用频率下降、96.9% success [来源: arXiv:2608.05446] |

### 2.2 为什么这个类比成立：本质都是"能力外部化"

```
First principle:
  model capability C < task requirement R -> gap D = R - C
  two ways to fill the gap:
    A. external compensation: human injects logic at runtime
    B. internal enhancement: training presses logic into weights
  economics: one-time cost of B < per-run cost of A -> B replaces A as model strengthens

-> prompt engineering and harness are both path A, replaced by path B
-> difference is D only: prompt fills short-horizon, harness fills long-horizon
-> falsification: if B never replaces A for a given logic class, that class is
   non-parameterizable (environment interface / human judgment), stays external
```

---

## 3. 历史类比：两轮"外部补偿→内化"的完整周期（含量化实证）

### 3.1 第一轮：手写特征 → 深度学习（2012 前后）

```
pre-DL: feature engineering = manual domain-knowledge encoding (SIFT/HOG/BOW)
  -> features = external compensation (human extracts for model)
DL: representation learning internalizes feature extraction
  -> feature engineering 'internalized' into weights (CNN learns edges/textures)
  -> feature engineer role disappears/transforms (humans design architectures)
```

**规律提取**：**凡"人帮模型做的通用认知活"，最终都会被模型自己学会**——特征是认知活，所以内化。量化佐证：2012 AlexNet 在 ImageNet top-5 error 从 ~26% 降至 15.3%，而此后手工特征（SIFT/HOG）在主流评测中逐步退出——特征提取从"人写代码"变为"权重自学"（[来源: Krizhevsky et al. 2012, NIPS]）。

### 3.2 第二轮：Prompt Engineering → 指令跟随（2022-2024）

```
early LLM: needs elaborate prompts (few-shot/role/format)
  -> prompt = external compensation (human demonstrates 'how')
instruction-following era: few-shot -> 0-shot native
  -> prompt engineering degrades from 'crafting' to 'speaking naturally'
  -> CoT from 'human-designed chains' to 'emergent reasoning'
  -> intermediate state disappears: requirements internalized
```

**规律强化 + 量化铁证**：
- **FLAN（2021）**：137B 模型在 60+ NLP 任务上指令微调后，zero-shot 在 20/25 个 unseen 任务上超越 175B GPT-3，部分任务（ANLI/RTE/BoolQ/AI2-ARC/OpenbookQA/StoryCloze）甚至大幅超越 few-shot GPT-3——"人类示范的指令遵循"被训练压进权重，few-shot 补偿被 zero-shot 原生能力取代（[来源: arXiv:2109.01652]）。
- **InstructGPT（2022）**：1.3B 的 RLHF 模型在人类评估中优于 175B GPT-3——"人类偏好判断"从外部标注（prompt+人工排序）内化为权重中的对齐策略（[来源: arXiv:2203.02155]）。
- prompt 的"认知部分"（怎么推理/怎么组织）被内化，prompt 的"信息部分"（任务内容）永远存在——这一区分就是 §6 边界模型的先声。

### 3.3 第三轮（进行中）：Harness → 原生 Agentic 能力

```
today: Harness provides decomposition/confrontation/verification
  -> long-horizon capability insufficient (drift/unreliable self-eval)
trend (EvoHarness annealing): training internalizes harness usage into policy
  -> 'good harness usage is using harness less' [src: arXiv:2608.05446]
prediction: next-gen models natively support decomposition + confrontation
  -> Harness degrades from 'necessary' to 'optional', like prompt today
```

**三轮周期共性**：外部补偿的**认知内核**（特征/推理/分解验证）被内化；**接口外壳**（数据/工具/环境）留在外部。

---

## 4. 内化机制：为什么外部逻辑会被模型吸收（第一性原理）

### 4.1 训练目标使然：RL/蒸馏天然奖励"内化"

```
training = making the model do it right with less external help
  RL: reward encourages autonomy -> model internalizes harness behavior
  SFT: supervised on harness traces -> model mimics 'behavior with harness'
  -> training dynamics distill external compensation into weights
```

**实证**：EvoHarness-RL 用两阶段实现内化——①supervised harness fine-tuning 教 base agent "harness 动作空间 + 如何构建有用外部状态"；②cost-aware GRPO 探索协调策略，选择性读写外部状态。训练后 agent 从"频繁 harness 调用"变为"选择性外部状态访问"，**96.9% success（ALFWorld, Qwen3-8B）**——内化直接转化为成功率提升（[来源: arXiv:2608.05446]）。

### 4.2 经济性驱动：内化省每次运行成本

```
external: every run pays LLM inference + harness logic (token + latency)
internalized: one forward pass, no extra overhead
  -> internalization = capex vs opex: one training payment vs recurring
  -> same economics as crystallization: amortization
```

**对照实证（结晶化一侧）**：生产云网络 AIOps 系统 8 个月把确定性执行从 0% 提升到 45%，在 incident 量翻倍的情况下单 incident agent 成本降低 **70%+**——外部逻辑固化（脚本）与内化（权重）共享同一经济逻辑：**一次性沉淀换重复性收益**（[来源: arXiv:2607.07052]）。

### 4.3 信息论视角：harness 是模型的"显式思考"

```
model = parameterized implicit distribution; harness = runtime explicit computation
  harness logic is the model's thinking externalized
  -> externalized thinking = re-parameterizable computation graph
  -> deterministic, enumerable harness logic can be absorbed by training
  -> counterexample: non-parameterizable (environment randomness/taste) stays external
```

**可参数化判据**：一段 harness 逻辑能否被内化，取决于它是否**确定性 + 可枚举 + 与外部世界解耦**。可被"样例化"进训练数据（agent traces）的逻辑即可内化；依赖实时外部状态的逻辑（如"查当前网络拓扑"）不可内化。

---

## 5. 论文一手实证：2026 年三条独立证据链的统一

### 5.1 证据矩阵（v2.0 升级：全部补论文一手数据）

| 证据 | 论文 | 关键量化数据 | 支持点 |
|:-----|:-----|:------------|:-------|
| **harness annealing** | EvoHarness-RL [arXiv:2608.05446] | Qwen3-8B/ALFWorld **96.9% success**；训练后 harness 调用从频繁→选择性 | 训练把重复 harness 使用内化为 policy——"越来越不用 harness" |
| **harness evolution** | 同上 | progress updates + experience consolidation → 紧凑任务自适应基底 | 外部状态被精炼为内部先验 |
| **技能内化（skill-native）** | Skill-Native LLMs [arXiv:2608.05139] | Skill-Entropy RL: Qwen3-4B **34.4%→68.4%**、Qwen3-1.7B **14.6%→40.1%**（Skill^2-Bench, 558 skills/9 domains） | 跨技能切换从"外部编排"变为"训练内化"——技能熵是内化训练信号 |
| **结晶化（外化镜像）** | Progressive Crystallization [arXiv:2607.07052] | 8 个月确定性执行 **0%→45%**；incident 成本 **-70%+**（量翻倍下） | agent 探索结晶为确定性工作流——外部固化（与内化互补） |
| **指令跟随内化** | FLAN [arXiv:2109.01652] | 137B 指令微调 zero-shot 超 175B GPT-3（20/25 任务） | 上一轮内化的量化铁证（few-shot→0-shot） |
| **loop 验证独立性** | LLMs Cannot Self-Correct Reasoning Yet [arXiv:2310.01798, ICLR 2024] | 无外部反馈时自校正失败甚至**性能退化** | 验证依赖外部独立性（当前）→ 可被内化为"模型内部对抗"（未来） |

### 5.2 统一框架：双向运动 + 一条主线

```
externalization (crystallization): trace -> deterministic workflow (-70% cost)
    | reverse
internalization (annealing): deterministic logic -> weights (less harness)

-> both isomorphic: 'chaos to order', one in scripts, one in weights
-> weak model externalizes (scripts); strong model internalizes (weights)
-> now: externalization mature (proven), internalization starting (new)
-> main line: same economics (amortization) drives both directions
```

**v2.0 新增判断**：三条 2026 论文证据链（annealing / skill-native / crystallization）不是孤立现象，而是**同一"沉淀-复用"经济规律在三个层面的表现**：script 层（结晶化）、policy 层（annealing）、benchmark 层（skill entropy）。这显著强于 v1.0 仅靠单篇论文 + 历史类比的论证强度。

---

## 6. 内化边界：什么会被吸收，什么永远留在外部

### 6.1 MECE 切分：认知模式 vs 环境接口（四象限，互斥穷尽）

| 类别 | 内容 | 内化趋势 | 理由（第一性原理） | 实例 |
|:-----|:-----|:---------|:------------------|:-----|
| **认知模式**（会被吸收） | 任务分解 / 验证闭环 / 对抗制衡 / 迭代修正 | ✅ 内化 | 通用、确定性、可参数化（§4.3）；有 2026 annealing 实证 | 多步任务分解（EvoHarness BPE 状态） |
| **领域知识**（部分吸收） | 服务器拓扑 / NCCL 语义 / 行业惯例 | ⚠️ 部分 | 高频可内化（skill entropy 训练），低频冷知识内化不经济，外部检索更优 | 技能切换（Skill^2-Bench 的 558 skills） |
| **环境接口**（留在外部） | 工具 API / 知识库 / 物理执行 / 实时数据 | ❌ 留在外部 | 外部世界不在权重里，接口永远需要 | MCP 协议 / 知识库检索 / 物理执行 |
| **人类判断**（留在外部） | 价值取舍 / 风险偏好 / 最终批准 | ❌ 留在外部 | 判断力不可外包（MEMORY 核心原则） | 准入审批 / 预算决策 |

### 6.2 例子：今天的 Harness 组件分类（CowAgent 实例）

```
example: this system (CowAgent):
  |- task decomposition (12 ops) -> cognitive pattern -> native (predicted)
  |- verification loop -> cognitive pattern -> internal (predicted)
  |- KB retrieval -> environment interface -> external forever
  |- tool invocation -> environment interface -> external forever
  +- user decision points -> human judgment -> external forever

counter-example (what internalization does NOT cover):
  |- 'git push --force to production' -> governance -> external forever
  |- 'current GPU cluster utilization' -> realtime data -> external forever
```

**关键判断：今天 Harness 里"最精巧的部分"（分解/验证/对抗）恰恰是最可能被内化的部分；"最朴素的部分"（调工具/查库）反而最持久。** 这反直觉但符合历史：特征工程里最精巧的 SIFT 被内化，而"拍照"这个朴素动作永远是外部输入。**治理类逻辑（§6.2 反例）是另一个持久层——不是因为它不可参数化，而是因为制度要求它外部化（可审计）。**

---

## 7. 可证伪判据与预测

### 7.1 预测（可证伪，附观测信号）

| # | 预测 | 时间窗 | 可证伪方式 | 观测信号 |
|:-:|:-----|:-------|:-----------|:---------|
| P1 | 模型越强，生产 Harness 的编排复杂度越低（同任务） | 12-24 月 | 对比同任务不同代模型的 harness 代码量 | EvoHarness 类论文中 annealing 后的 harness 调用频率曲线 |
| P2 | "任务分解/自验证"成为模型基准测试项（agentic 基准） | 6-12 月 | 观察新基准是否含原生分解/验证维度 | Skill^2-Bench 已被 8 frontier + 4 开源模型采用 = 信号已出现 [来源: arXiv:2608.05139] |
| P3 | 多 Agent 制衡被"单模型内部对抗"部分取代 | 18-36 月 | 观察主流 agent 框架的架构图 | 独立验证子 agent → 模型内部 self-critique 的迁移 |
| P4 | 环境接口层（工具/检索）保留且标准化（MCP 类协议） | 长期 | MCP 类生态持续扩张 | Agent Plugins 1.0（AWS/OpenAI/Microsoft/Google 联合，2026-08-06 发布）[来源: GitHub Changelog] |
| P5 | Harness 的"认知模式"部分代码量占比下降，"接口"部分占比上升 | 12 月 | 统计开源 harness 代码结构变化 | opencode（198.5k stars）等开源 agent 的 tools/MCP 占比 |

### 7.2 反例（证伪条件）

```
if any of the following occurs, the hypothesis weakens:
  A. model capability jumps (e.g. 10x cheaper) but harness complexity rises
  B. trained on harness traces, model still cannot internalize decomposition (arch limit)
  C. persistent reason external beats internal (e.g. auditability requires external)
```

**注**：情况 C 是最强的反例候选——**企业治理/合规可能要求验证逻辑留在外部（可审计）**，即使模型已能内化。这与 RULE.md "AI 不替用户做准入判断"同源。因此更精确的表述是：**内化是技术趋势，外部化保留是治理选择**——两者可以并存（§6.2 治理反例层）。

---

## 8. 工程启示：今天写 Harness 的意义

### 8.1 写 Harness 不是浪费：它是"待内化能力的清单"

```
every orchestration component = one annotation of model deficiency
  -> deficiency list = training target list for next-gen models
  -> harness-writing experience = distillation data production
analogy: handcrafted features = initialization priors for DL nets
  -> features not wasted: they define 'what to learn'
  -> concrete: EvoHarness supervised fine-tuning uses human-designed
     harness traces - what we write today becomes tomorrow's training data
     [src: arXiv:2608.05446, "supervised harness fine-tuning"]
```

### 8.2 分层策略（面向未来）

| 层 | 现在 | 未来（内化后） | 今天应做什么 |
|:---|:-----|:---------------|:-------------|
| 认知模式层 | 写精巧编排（分解/验证/对抗） | 模型原生 | **做薄**：保持最小必要，记录为"待内化清单" |
| 接口层 | 工具/知识库/执行 | 长期存在 | **做稳**：标准化、可复用（MCP / Agent Plugins 类） |
| 治理层 | 人类判断点 | 长期存在 | **做清晰**：边界显式化（哪些不外包） |

### 8.3 与用户系统协作模式同构

```
user today: human designs process (RULE/AGENT/MEMORY) + AI executes + KB accumulates
  -> this IS 'external compensation': necessary while AI weak
future: as AI strengthens, process details internalized
  -> but KB (interface) + judgment points (governance) remain
  -> KB/governance long-lived; process details migratable
  -> KB = interface-layer investment (long-term); orchestration = cognitive (transitional)
```

---

## 9. 风险与批判

| 风险 | 说明 | 应对/证据 |
|:-----|:-----|:---------|
| 内化非线性 | 模型变强不一定自动内化（需要训练数据包含 harness 轨迹）——P2 可能滞后 | EvoHarness 表明需要显式两阶段训练（SFT+GRPO），不是自然涌现 [来源: arXiv:2608.05446] |
| 治理反例 | 合规/审计可能强制外部化验证逻辑（§7.2 C）——内化趋势被制度性抵消 | 治理层独立于技术层，两者并存（§6.2） |
| 认知模式 ≠ 全部 | 任务分解等可能部分内化而非完全内化（模型"会"但"不稳"，仍需外部兜底） | Skill^2-Bench 显示 8 个 frontier 模型仍有 skill-switching gap [来源: arXiv:2608.05139] |
| 类比过度 | prompt 内化发生在"单轮短程"，harness 处理"长程多轮"——长程内化难度更高，时间窗可能更长 | 长程任务状态管理（BPE）刚有首个 annealing 实证，样本仅 ALFWorld 单环境 |
| 生态惯性 | Harness 工具链已形成生态（LangGraph/CrewAI），即使技术可内化，生态迁移有惰性 | 迁移成本 vs 内化收益的赛跑，P5 观测 |

---

## 10. 数据缺口

| 缺口 | 说明 |
|:-----|:-----|
| 内化实证范围 | EvoHarness-RL 仅 ALFWorld 单环境 + Qwen3-8B 单模型，跨环境/跨规模代表性待扩展 |
| 编排复杂度量化 | "模型越强 harness 越简单"无跨代模型的直接对比数据（P1 待观测） |
| 内化 vs 治理并存 | 无企业级"治理强制外部化"的系统实证 |
| 时间窗估计 | P1-P5 的 12-36 月窗口为判断估计，无历史锚点 |
| Skill^2-Bench 具体任务样本 | 558 skills/9 domains 的任务分布细节未读原文附录 |

---

## 11. 参考来源

| # | 来源 | 类型 | 日期 |
|:--|:-----|:-----|:-----|
| 1 | [EvoHarness-RL: Learning Self-Evolving Runtime Harness for Long-Horizon LLM Agents](https://arxiv.org/abs/2608.05446)（Ning et al., LLA@COLM 2026） | 论文一手 | 2026-08-05 |
| 2 | [Toward Skill-Native LLMs: Skill Entropy for Benchmarking and Training Long-Horizon Reasoning](https://arxiv.org/abs/2608.05139)（He et al., 含 Sanjeev Arora） | 论文一手 | 2026-08-05 |
| 3 | [Progressive Crystallization: Turning Agent Exploration into Deterministic, Lower-Cost Workflows in Production](https://arxiv.org/abs/2607.07052)（Arun Malik） | 论文一手 | 2026-07-08 |
| 4 | [Finetuned Language Models Are Zero-Shot Learners (FLAN)](https://arxiv.org/abs/2109.01652)（Wei et al., Google） | 论文一手 | 2021-09 |
| 5 | [Training language models to follow instructions with human feedback (InstructGPT)](https://arxiv.org/abs/2203.02155)（Ouyang et al., OpenAI） | 论文一手 | 2022-03 |
| 6 | [Large Language Models Cannot Self-Correct Reasoning Yet](https://arxiv.org/abs/2310.01798)（Huang et al., ICLR 2024） | 论文一手 | 2023-10 |
| 7 | [Agent Plugins 1.0（GitHub Changelog 2026-08-12）](https://github.blog/changelog/2026-08-12-agent-plugins-1-0-in-vs-code-copilot-cli-and-the-copilot-app/) | 官方一手 | 2026-08-12 |
| 8 | 特征工程→深度学习 / prompt→指令跟随（通用发展史） | 通用知识 | — |
| 9 | 用户洞察（Harness ≈ prompt engineering 中间状态假设） | 一手 | 08-17 |

---

## 12. Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-17 | v2.0 | **质量提升**：①论文一手实证升级——EvoHarness 补 96.9% success/两阶段训练细节、Skill-Native 修正内涵（skill entropy 训练信号而非简单"技能注入"）并补 34.4→68.4% 数据、Crystallization 补 0→45%/-70% 数据、新增 FLAN/InstructGPT/LLMs-Cannot-Self-Correct 三篇经典锚点；②边界模型补治理反例层（制度性外部化）；③预测补观测信号（Skill^2-Bench 采用、Agent Plugins 1.0）；④数据缺口更新（明确单环境局限） |
| 2026-08-17 | v1.0 | 首次创建。Harness 中间状态假设论证：三轮内化周期（特征/指令/编排）+ 内化三机制（训练目标/经济性/信息论）+ 散落实证统一（annealing/结晶化/Skill-Native）+ 内化边界 MECE（认知模式内化/接口保留）+ 五条可证伪预测 |
