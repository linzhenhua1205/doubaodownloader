# 🧬 Harness 优化/进化基准全景：HarnessOpt-Bench / Evo-Bench / DarwinX / Meta-Harness / AHE 与 harness-bench 生态

> **概要**: 2026 年 7-8 月，「harness 本身」成为被评测对象——HarnessOpt-Bench、Evo-Bench、Skill-Use、LoopsBench、Harness-IF、DarwinX、Meta-Harness、AHE 等一批「harness 基准/系统」集中爆发。本文定义 harness-bench 概念（评测「模型优化 harness 的能力」与「harness 的安全/遵循/进化属性」的基准群），MECE 分类拆解 8+ 基准与 4 大进化系统，给出横向对比矩阵与对决策者的启示。
>
> **关键词**: Harness-Bench · HarnessOpt-Bench · Evo-Bench · DarwinX · Meta-Harness · AHE · Agentic Harness Engineering · Skill-Use · LoopsBench · Harness-IF · HarnessSafe · harness 进化 · 可观测性
>
> **来源**: arXiv API 论文摘要（2026-08-21 抓取）+ GitHub API/README 一手抓取（2026-08-21）+ 本库 08-10 harness 优化专篇
>
> **归档**: 2026-08-21 v1.0 | **模块**: 03_AI/agent-engineering/
>
> **姊妹篇**: [编码模型评测 Harness 全景对比](2026-08-21-coding-eval-harness-comparison-deep-analysis.md)（评测框架层）· [Harness 优化与自进化门控](2026-08-10-harness-optimization-self-evolution-skill-gating.md)（研究线起点）

---

## 📑 目录

- [〇、结论概要](#〇结论概要)
- [一、概念框架：harness-bench 是什么](#一概念框架harness-bench-是什么)
  - [1.1 定义与定位](#11-定义与定位)
  - [1.2 为什么 2026 年 7-8 月集中爆发](#12-为什么-2026-年-7-8-月集中爆发)
  - [1.3 与评测 harness（Harbor 类）的区别](#13-与评测-harnessharbor-类的区别)
- [二、harness-bench 生态全景（MECE 三族）](#二harness-bench-生态全景mece-三族)
  - [2.1 能力族：模型优化/进化 harness 的能力](#21-能力族模型优化进化-harness-的能力)
  - [2.2 安全族：harness 的安全与边界](#22-安全族harness-的安全与边界)
  - [2.3 系统族：harness 进化系统（产物即基准）](#23-系统族harness-进化系统产物即基准)
- [三、HarnessOpt-Bench 深度拆解（能力族锚点）](#三harnessopt-bench-深度拆解能力族锚点)
  - [3.1 评测协议](#31-评测协议)
  - [3.2 三个关键发现](#32-三个关键发现)
  - [3.3 设计边界纪律的普适价值](#33-设计边界纪律的普适价值)
- [四、Evo-Bench 深度拆解（多域泛化）](#四evo-bench-深度拆解多域泛化)
  - [4.1 设计：harness-guided 构造框架](#41-设计harness-guided-构造框架)
  - [4.2 结果与发现](#42-结果与发现)
- [五、其他能力族基准速览](#五其他能力族基准速览)
  - [5.1 Skill-Use：技能使用是 harness 条件能力](#51-skill-use技能使用是-harness-条件能力)
  - [5.2 LoopsBench：从 harness 工程到 loop 工程](#52-loopsbench从-harness-工程到-loop-工程)
  - [5.3 Harness-IF：指令遵循表面与反先验准确率](#53-harness-if指令遵循表面与反先验准确率)
- [六、安全族：HarnessSafe / HarnessRisk](#六安全族harnesssafe--harnessrisk)
- [七、harness 进化系统横评：Meta-Harness / AHE / DarwinX / Evo-Harness](#七harness-进化系统横评meta-harness--ahe--darwinx--evo-harness)
  - [7.1 Meta-Harness（Stanford）](#71-meta-harnessstanford)
  - [7.2 AHE（Agentic Harness Engineering）](#72-aheagentic-harness-engineering)
  - [7.3 DarwinX（群体进化）](#73-darwinx群体进化)
  - [7.4 Evo-Harness（skill 编译）](#74-evo-harnessskill-编译)
  - [7.5 四系统对比矩阵](#75-四系统对比矩阵)
- [八、评测基础设施层：Harbor 与 claw-swe-bench 的角色](#八评测基础设施层harbor-与-claw-swe-bench-的角色)
- [九、对 AI 基础设施决策者的启示](#九对-ai-基础设施决策者的启示)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 〇、结论概要

1. **harness-bench 是 2026 年新生的基准类别**：把「harness 优化能力」「harness 安全」「harness 遵循属性」变成可测量、可比较、可复现的受控实验。核心代表 HarnessOpt-Bench（arXiv:2608.06301）首次把「LLM 优化 harness」做成基准；Evo-Bench（2608.09096）自称「第一个测模型内在 harness 进化能力」的基准 [来源: arXiv API 2026-08-21]。

2. **三族格局已成型（MECE）**：能力族（HarnessOpt-Bench/Evo-Bench/Skill-Use/LoopsBench/Harness-IF）测「模型会不会优化/使用 harness」；安全族（HarnessSafe/HarnessRisk）测「harness 会不会被攻破」；系统族（Meta-Harness/AHE/DarwinX/Evo-Harness）是 harness 进化系统，产物本身成为新基准的对照锚点 [来源: arXiv API + GitHub]。

3. **三个贯穿性实证结论**：
   - **模型是 harness 优化能力的主变量**：optimizer 模型差异 > 编码 harness 差异（HarnessOpt-Bench，111 次计分运行）[来源: arXiv:2608.06301]；
   - **harness 进化收益真实且巨大**：DarwinX 四基准平均 +17 分、WebArena-Infinity 43.5→93.0%；AHE 把 GPT-5.4 从 69.7% 抬到 77.0%（10 轮迭代）[来源: arXiv:2608.07545 + GitHub README]；
   - **安全是最脆弱维度**：HarnessRisk 攻击成功率横跨 12.6%-80.9%，且「识别出风险 ≠ 采取安全行动」（检测 >90% 仍保留可观攻击成功率）[来源: arXiv:2608.17597]。

4. **产业信号**：AHE（GPT-5.5）在 Terminal-Bench 2.0 登顶 #3（84.7%）、Meta-Harness 76.4%（Claude Opus 4.6）——**「冻结模型 + 进化 harness」已成为与「换更大模型」并列的提分路径**，且两系统都基于 Harbor 评测框架（KRAFTON Terminus-2 / Stanford）[来源: GitHub README 2026-08-21]。

5. **对决策者**：harness-bench 标志着「评测 → 优化 → 学习」闭环的产业成熟。选型 AI 编码能力时，「该模型的 harness 可进化性」与「harness 安全基线」应纳入评估；自建评测体系应复用 Harbor 类底座并借鉴 HarnessOpt-Bench 的 held-out 边界纪律。

---

## 一、概念框架：harness-bench 是什么

### 1.1 定义与定位

**harness-bench（harness 基准）**：以「agent harness 本身」为评测对象的基准类别，回答三类问题：

| 问题 | 类别 | 代表基准 |
|:-----|:-----|:---------|
| 模型能不能优化/进化 harness？ | 能力 | HarnessOpt-Bench / Evo-Bench / Skill-Use |
| harness 是否安全、是否遵循指令？ | 安全/遵循 | HarnessSafe / HarnessRisk / Harness-IF |
| harness 进化系统能提多少分？ | 系统效能 | Meta-Harness / AHE / DarwinX / LoopsBench |

与「评测 harness」（Harbor/lm-evaluation-harness，上一轮主题）的本质区别：**评测 harness 是被用来测模型/agent 的工具；harness-bench 是把 harness 放到聚光灯下测它自己**。

### 1.2 为什么 2026 年 7-8 月集中爆发

三个必要条件在 2026 年夏天同时成熟：

1. **前提共识化**：「Model + Harness = Agent」成为行业共识（黄仁勋×LangChain 对话、DeepSeek Harness 模型卡披露、Harbor 生态成型）——harness 的重要性不再需要论证 [来源: 本库 08-13 DeepSeek Harness 专篇]；
2. **工具链成熟**：Harbor 提供容器评测/轨迹记录/RL 数据产出，使「harness 优化实验」可复现、成本可控——HarnessOpt-Bench 的 held-out 边界与可信执行环境都建立在 Harbor 类基础设施上 [来源: arXiv:2608.06301 + Harbor README]；
3. **实证拐点**：LangChain 实验（成本 -90% 追平分数）、Meta-Harness/AHE 的 TB 登顶证明「harness 红利」真实存在——值得被系统测量 [来源: GitHub README + 本库 08-13 专篇]。

### 1.3 与评测 harness（Harbor 类）的区别

| 维度 | 评测 harness（Harbor） | harness-bench |
|:-----|:----------------------|:--------------|
| 被测对象 | agent/模型 | harness 本身（或模型优化 harness 的能力） |
| 输出 | 任务分数/轨迹 | harness 优化增益/安全指标/进化系统排名 |
| 用户 | 想评测 agent 的人 | 想改进 harness 的研究者/平台方 |
| 关系 | **是 harness-bench 的执行底座** | 依赖 Harbor 类框架跑实验 |

---

## 二、harness-bench 生态全景（MECE 三族）

### 2.1 能力族：模型优化/进化 harness 的能力

| 基准 | arXiv | 日期 | 规模 | 核心设计 | 关键结论 |
|:-----|:------|:-----|:-----|:---------|:---------|
| **HarnessOpt-Bench** | 2608.06301 | 08-06 | 5 模型×4 任务×111 次计分 | held-out 测试分区不可访问 + 可信执行环境 + 预算约束 | 模型 > 编码 harness；native 不总优；增益波动大 |
| **Evo-Bench** | 2608.09096 | 08-10 | 9 模型×3 域 | harness-guided 构造：auxiliary-task 进化 + sensitivity-aware 分层切分 | 最高绝对增益 16.6 分；Office 任务最弱；合成 harness 可迁移 |
| **Skill-Use** | 2608.04828 | 08-05 | 8 模型×2 harness×79 skills/177 任务 | 渐进披露 + Trigger/Compliance/Boundary 三面 | 最强配置 SU 仅 0.613；技能使用是 harness 条件能力 |
| **LoopsBench** | 2608.00267 | 07-31 | 112 任务×8 语言×9 域 | dependency DAG + flow-aware 运行时 | 最强配置（Opus-4.7+Claude Code）仅 25.00% |
| **Harness-IF** | 2608.11727 | 08-12 | 12 模型×642 规则库/60 任务 | 5 个可配置表面 + AP-Acc 反先验准确率 | 全模型反先验规则更差（均值 -5.81 分） |

### 2.2 安全族：harness 的安全与边界

| 基准 | arXiv | 规模 | 核心设计 | 关键结论 |
|:-----|:------|:-----|:---------|:---------|
| **HarnessSafe** | 2608.06984 | 328 案例×7 持久载体族 | Persistent-Risk Lifecycle 追踪 | 遏制是载体特定的，强依赖 harness-model 配置 |
| **HarnessRisk** | 2608.17597 | 128 案例×6 运营阶段 | Utility/ASR/Persistence/Detection 四指标 | ASR 12.6%-80.9%；配置阶段最脆弱；识别≠行动 |

### 2.3 系统族：harness 进化系统（产物即基准）

| 系统 | 出处 | 规模信号 | 核心方法 | 成绩 |
|:-----|:-----|:---------|:---------|:-----|
| **Meta-Harness** | Stanford iris-lab | 1,181★ | Terminus-KIRA + 环境 bootstrap 注入 | TB2.0 76.4%（Claude Opus 4.6） |
| **AHE** | china-qijizhifeng | 840★，arXiv:2604.25850 | NexAU 七组件分解 + Agent Debugger 轨迹蒸馏 | TB2.0 84.7% #3（GPT-5.5）；GPT-5.4 69.7→77.0% |
| **DarwinX** | arXiv:2608.07545 | 4 基准 | 群体选择：preserve-and-extend + 谱系归档 | 平均 +17 分；WebArena 43.5→93.0% |
| **Evo-Harness** | arXiv:2608.15071 | 5 基准 | context-to-harness skill 编译 | 一次性 skill 编译跨域有效 |

---

## 三、HarnessOpt-Bench 深度拆解（能力族锚点）

> 本库 08-10 专篇已有完整分析，此处补全为独立可读章节并深化 [来源: 本库 2026-08-10-harness-optimization-self-evolution-skill-gating.md 第三节 + arXiv:2608.06301]。

### 3.1 评测协议

| 协议要素 | 设计 | 防什么 |
|:---------|:-----|:-------|
| 输入 | 目标 agent 的 seed harness + 分级评估反馈 + 固定评估预算 | 模拟真实「已有系统想改进」 |
| 动作 | optimizer（LLM+编码 harness）编辑 harness、提名最终候选 | 端到端：改→测→再改 |
| 评估边界 | **held-out 测试分区全程不可访问** + 可信执行环境强制执行 | 评估集泄漏/搜索期过拟合 |
| 资源计量 | 计量 target-agent 资源使用 | 昂贵评估预算 = 真实约束 |
| 打分 | 最终候选相对 seed 的归一化增益 | 排除任务难度差异 |

### 3.2 三个关键发现

1. **optimizer 模型差异 > 编码 harness 差异**——harness 优化能力主要由模型本身的推理/调试能力决定，编码工具是放大器而非决定项；
2. **native harness 不总更优**——「自家 harness 有隐藏加成」是错觉，harness 效果是任务×seed 条件性的；
3. **增益跨任务/seed 波动大**——存在任务亲和与初始状态依赖，不能简单排名。

### 3.3 设计边界纪律的普适价值

held-out 不可访问 + 可信执行环境 + 版本审计，这套「评估边界纪律」对所有自建评测都有借鉴意义——尤其对超节点/集群场景下「评测→训练→评测」闭环，防评估集过拟合是闭环不塌陷的前提。

---

## 四、Evo-Bench 深度拆解（多域泛化）

### 4.1 设计：harness-guided 构造框架

Evo-Bench（arXiv:2608.09096，08-10）针对现有评测无法「把 harness 改进从基础模型强度中分离」的缺陷，提出两阶段构造 [来源: arXiv API 2026-08-21]：

1. **auxiliary-task 进化**：先用辅助任务进化识别「真正对框架改进敏感」的任务——把与 harness 无关的题剔除；
2. **sensitivity-aware 分层切分**：按敏感性分层切训练/测试集，保证跨套件泛化稳健。

三域覆盖：Search（搜索）、Office（办公）、General（通用 agent）。

### 4.2 结果与发现

- 9 个前沿/开源模型评测，最高绝对增益 **16.6 分**，逼近 SOTA 人工设计基线；
- 自主进化在 General 任务超越人工 harness、在 Search 任务表现出色，但**在 Office 任务（高度特定处理流程）挣扎**——领域特定工作流仍是 harness 进化的短板；
- 发现时间异常（早期饱和）；合成的 harness 作为可迁移推理结构，能稳定提升不同 policy 模型 [来源: arXiv:2608.09096]。

---

## 五、其他能力族基准速览

### 5.1 Skill-Use：技能使用是 harness 条件能力

Skill-Use（arXiv:2608.04828，08-05）评测 agent 在渐进披露下自主识别并应用技能的能力：Trigger（是否触发相关技能）/Compliance（是否忠实遵循程序）/Boundary（是否避开禁止操作）三面合成 SU 分数。79 个真实技能 × 177 个可执行任务 × 9 域，Docker 沙箱 + 轨迹评分。**最强配置 SU 仅 0.613**——可靠技能使用仍遥不可及；且「分数和模型排名随 harness 改变」——**技能使用是 harness 条件能力，而非模型固定属性** [来源: arXiv:2608.04828]。

### 5.2 LoopsBench：从 harness 工程到 loop 工程

LoopsBench（arXiv:2608.00267，微软）提出编码 agent 基础设施正从「harness 工程」转向「loop 工程」（长时程持续开发）。112 个真实任务 × 8 语言 × 9 域，每个任务是**依赖 DAG**（源码佐证的前置边），flow-aware 运行时沿就绪前沿发布测试并保留已完成节点作为回归义务。**最强配置 Opus-4.7 + Claude Code + outer continuation 仅解决 25.00%**——长时程 loop 是当前 agent 的最大瓶颈之一 [来源: arXiv:2608.00267]。

### 5.3 Harness-IF：指令遵循表面与反先验准确率

Harness-IF（arXiv:2608.11727，08-12）解决「agent 遵守规则可能只是碰巧」的问题：60 个多轮编码任务 × 642 规则库 × 5 个可配置表面（system prompt/项目文件/用户指令/工具/技能描述）。核心指标 **AP-Acc（Against-Prior Accuracy）**——只统计「与默认行为相悖」的规则，通过撤下规则重跑 9 个探针构建来分离「合规 vs 巧合」。12 个前沿模型 accuracy 72.1-85.9%、AP-Acc 66.1-78.6%，**所有模型在反先验规则上都更差（均值 -5.81 分）**——聚合分数高估合规性 [来源: arXiv:2608.11727]。

---

## 六、安全族：HarnessSafe / HarnessRisk

### 6.1 HarnessSafe：持久载体安全

HarnessSafe（arXiv:2608.06984，08-07）：现代 harness 通过 memory/skills/tools/shared artifacts 跨任务持久状态，产生延迟安全风险。328 个可执行案例 × 7 个持久载体族，用 Persistent-Risk Lifecycle 追踪攻击从进入到触发到违规的完整链路。**遏制是载体特定的，且 harness 与模型后端共同塑造遏制结果**——攻击成功率无法反映生命周期进展模式 [来源: arXiv:2608.06984]。

### 6.2 HarnessRisk：生命周期六阶段

HarnessRisk（arXiv:2608.17597，08-18）：把 harness 安全组织为 6 个运营阶段（配置/能力扩展/运行时/状态持久/动作控制/事件恢复）× 128 个沙箱案例 × 四指标（Utility/ASR/Persistence/Detection）。3 harness × 6 模型 × 14 配置下：**ASR 12.6%-80.9%，Utility 75.0%-97.6%**。两个关键发现：
- **Harness Configuration 是全部 harness 最脆弱阶段**——攻击可通过篡改授权工作流内的安全敏感参数得手；
- **显式风险识别不必然导致安全行动**——部分配置检测率 >90% 仍保留可观攻击成功率 [来源: arXiv:2608.17597]。

> ⚠️ 安全族与能力族叠加的警示：当「模型可以自主优化 harness」（能力族）遇上「harness 配置阶段最脆弱」（安全族），自进化系统可能无意中优化出更易被攻破的配置——harness 进化的安全护栏是 2026 下半年必答题。

---

## 七、harness 进化系统横评：Meta-Harness / AHE / DarwinX / Evo-Harness

### 7.1 Meta-Harness（Stanford）

- **规模**：1,181★ / 165 fork，stanford-iris-lab，2026-03 创建 [来源: GitHub API 2026-08-21]；
- **成绩**：Terminal-Bench 2.0 76.4%（89 任务 × 5 次，Claude Opus 4.6）——Medium 81.1% / Hard 64.7% [来源: GitHub README]；
- **方法**：基于 KRAFTON AI 的 Terminus-KIRA agent + Harbor Terminus-2 框架，核心增强 = **环境 bootstrap**：agent 循环开始前先快照沙箱环境（工作目录/文件列表/可用语言工具/包管理器/内存）注入初始 prompt，省掉 2-5 轮早期探索（ls/which python3 等）[来源: GitHub README]；
- **关键点**：README 明说「The agent was discovered through automated harness evolution」——**它是 harness 自动进化的产物，而非纯手工设计**。

### 7.2 AHE（Agentic Harness Engineering）

- **规模**：840★ / 96 fork，arXiv:2604.25850，2026-04 发布框架/04-28 论文/05-14 登顶 [来源: GitHub README]；
- **成绩**：TB2.0 84.7% 排名 **#3**（GPT-5.5，2026-05-14）；把 GPT-5.4 从 69.7% 抬到 77.0%（10 轮迭代）；冻结 harness 可迁移到 SWE-bench Verified [来源: GitHub README]；
- **方法**：可观测性驱动的自动进化——三观测层：
  1. **组件可观测性**：NexAU 把 harness 分解为 7 个正交文件级组件，每个 git 跟踪可审计可回滚；
  2. **经验可观测性**：Agent Debugger 把 ~10M token 原始轨迹蒸馏为分层带来源的报告；
  3. 优化器读取摘要进行编辑 [来源: GitHub README]；
- **冻结模型假设**：base model 固定，进化的是 system prompts/tool 描述/tool 实现/中间件/skills/子代理/长期记忆。

### 7.3 DarwinX（群体进化）

- **arXiv**：2608.07545（07-31）[来源: arXiv API]；
- **方法**：把自进化当作**种群选择**（模型冻结）：
  - preserve-and-extend 合约：只接受「扩展覆盖且不回归」的变体；
  - archive 保留替代谱系供重组；
  - failure-/teacher-/self-derived 证据共用同一编辑接口；
  - fitness 来自各 benchmark 自己的 verifier——**无 gold solutions、无手工挑选**；
- **成绩**：四基准平均 +17 分——TB2.1 +7.7 至 83.2%（更强基线上 verified frontier 84.7%）；TerminalWorld held-out 68.3%；WebArena-Infinity 43.5→93.0%（audit-clean）；TB2.1 harness 无修改迁移到 SWE-bench Verified。

### 7.4 Evo-Harness（skill 编译）

- **arXiv**：2608.15071（08-15）[来源: arXiv API]；
- **方法**：online harness learning——冻结 agent 通过持续更新结构化 harness 在顺序任务中改进；核心 = context-to-harness skill 编译，把嘈杂的一次性执行蒸馏为可复用 skill harness；
- **成绩**：5 个真实基准（TerminalBench2/SWE-bench/CL-Bench/WebArena-Infinity 等）验证一次性 skill 编译的跨域与跨主题适应。

### 7.5 四系统对比矩阵

| 维度 | Meta-Harness | AHE | DarwinX | Evo-Harness |
|:-----|:-------------|:----|:--------|:------------|
| 进化范式 | 单一产物（自动进化发现） | 组件级可观测迭代 | **群体选择**（种群+谱系） | 在线 skill 编译 |
| 核心创新 | 环境 bootstrap 注入 | NexAU 七组件 + 轨迹蒸馏 | preserve-and-extend + verifier fitness | context→skill 蒸馏 |
| 防回归机制 | — | git 可回滚 | 扩展-不回归合约 | 验证门控 |
| 最强成绩 | TB2.0 76.4% | TB2.0 84.7% #3 | WebArena 43.5→93.0% | 5 基准跨域 |
| 可迁移性 | — | SWE-bench Verified | TB2.1→SWE-bench 无修改 | 跨域 topic 级 |
| 模型策略 | 冻结（Claude Opus 4.6） | 冻结（GPT-5.5） | 冻结 | 冻结 |

**共同范式**：全部「冻结模型、进化 harness」；全部强调可审计（git/合约/门控）；全部在 Terminal-Bench 系或 SWE-bench 上验证。

---

## 八、评测基础设施层：Harbor 与 claw-swe-bench 的角色

### 8.1 Harbor：harness 进化的执行底座

Meta-Harness 明确基于 Harbor 的 Terminus-2 框架（`pip install harbor` + `harbor run --agent-import-path agent:AgentHarness`）[来源: GitHub README]。Harbor 提供的容器隔离/轨迹记录/RL 数据产出正是 harness 进化实验的三要素——**评测基础设施与 harness 进化形成正反馈**：Harbor 让进化可跑，进化让 Harbor 更值钱。

### 8.2 claw-swe-bench：harness 的受控变量评测

claw-swe-bench（opensquilla，95★，arXiv:2606.12344）是「评测 harness 本身」的适配框架：5 种 openclaw 风格 harness（openclaw/hermes/nanobot/zeroclaw/generic）在同一 SWE-bench 上以**相同 prompt/补丁收集/评估**运行，使 harness 成为受控变量。350 实例 × 8 语言（300 SWE-bench Multilingual + 50 Verified-Mini），另有 80 实例 Lite 子集用于低成本迭代 [来源: GitHub README]。

> 设计亮点：`BaseClawAdapter` 接口使「加一个新 harness = 一个新文件 + 一个注册项」——这是 harness 评测工程化的正确抽象。

---

## 九、对 AI 基础设施决策者的启示

1. **选型视角升级**：编码 agent 评估从「看模型分数」升级为「看模型×harness 组合 + harness 可进化性」——Meta-Harness/AHE 证明**同一模型换 harness 可产生 7-15 分的差异**，大于多数模型换代收益 [来源: GitHub README + arXiv:2608.07545]。

2. **进化 harness 是新的提分杠杆**：冻结模型 + 进化 harness（DarwinX 平均 +17 分）的成本结构远优于换模型（无训练成本，只花评测算力）——对算力预算敏感的团队尤其适用。但需注意 Evo-Bench 结论：**领域特定工作流（Office 类）仍是短板**，通用 agent 任务收益最大 [来源: arXiv:2608.09096]。

3. **安全基线必须纳入**：HarnessRisk 证明「配置阶段最脆弱」+「识别≠行动」——若部署支持 harness 自进化的系统，**必须给进化过程加安全护栏**（HarnessSafe/HarnessRisk 可作验收基准）[来源: arXiv:2608.17597 + 2608.06984]。

4. **评测边界纪律是底线**：HarnessOpt-Bench 的 held-out 不可访问设计应成为自建评测的标配——尤其当评测轨迹要反哺训练时（闭环防塌陷）[来源: arXiv:2608.06301]。

5. **基础设施正反馈**：Harbor 类评测底座 + harness 进化系统正在形成「评测→进化→再评测」的自增强飞轮；谁掌握底座与数据，谁就在下一阶段领先——这与超节点/集群场景的「评测→训练→评测」闭环战略直接相关 [来源: 本库 08-21 coding-eval-harness-comparison 专篇]。

---

## 参考文件

**一手来源（2026-08-21 抓取）**：
1. [HarnessOpt-Bench](https://arxiv.org/abs/2608.06301) — arXiv:2608.06301（08-06，含 NVIDIA Yuan Xue）
2. [Evo-Bench](https://arxiv.org/abs/2608.09096) — arXiv:2608.09096（08-10）
3. [DarwinX](https://arxiv.org/abs/2608.07545) — arXiv:2608.07545（07-31）
4. [Skill-Use](https://arxiv.org/abs/2608.04828) — arXiv:2608.04828（08-05）
5. [LoopsBench](https://arxiv.org/abs/2608.00267) — arXiv:2608.00267（微软，07-31）
6. [Harness-IF](https://arxiv.org/abs/2608.11727) — arXiv:2608.11727（08-12）
7. [HarnessSafe](https://arxiv.org/abs/2608.06984) — arXiv:2608.06984（08-07）
8. [HarnessRisk](https://arxiv.org/abs/2608.17597) — arXiv:2608.17597（08-18）
9. [Evo-Harness](https://arxiv.org/abs/2608.15071) — arXiv:2608.15071（08-15）
10. [SemaPLC](https://arxiv.org/abs/2608.18565) — arXiv:2608.18565（08-19，领域类代表）
11. [Meta-Harness](https://github.com/stanford-iris-lab/meta-harness-tbench2-artifact) — GitHub README/API（1,181★）
12. [AHE](https://github.com/china-qijizhifeng/agentic-harness-engineering) — GitHub README/API（840★，arXiv:2604.25850）
13. [claw-swe-bench](https://github.com/opensquilla/claw-swe-bench) — GitHub README/API（95★，arXiv:2606.12344）

**知识库交叉链接**：
- [编码模型评测 Harness 全景对比](2026-08-21-coding-eval-harness-comparison-deep-analysis.md)（评测框架层姊妹篇）
- [Harness 优化与自进化门控](2026-08-10-harness-optimization-self-evolution-skill-gating.md)（HarnessOpt-Bench/EvoHarness-RL 研究线起点）
- [Skill-Use 评测缺口](2026-08-07-skill-use-eval-gap-deep-analysis.md)（Skill-Use 基准前身分析）
- [DeepSeek Harness 技术框架分析](2026-08-13-deepseek-harness-technical-framework-analysis.md)（运行 harness 专篇）
- [Agent 退化模式与 Harness 架构](2026-08-17-agent-degeneration-modes-harness-architecture-deep-analysis.md)

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-21 | v1.0 | 首次创建。harness-bench 生态全景：能力/安全/系统三族 MECE 拆解 + HarnessOpt-Bench/Evo-Bench 深潜 + Meta-Harness/AHE/DarwinX/Evo-Harness 四系统横评 + 决策启示 |
