# 🤝 AI4AI at Test-Time：测试时强→弱能力转移——技术框架 / 机制归因 / 研究线互证

> **概要**: 传统蒸馏通过更新小模型参数实现强→弱能力转移（训练时）；本文（arXiv:2608.12307，2026-08-12 提交，Salesforce AI Research × UIUC，9 作者）提出**测试时转移**——强 builder 模型为弱 target 模型构建推理时 harness（scaffold），**零参数更新**。在 4 个 Theory-of-Mind（ToM）基准的 3900 条隐藏测试集上：builder 仅用 5%（195 条）验证集迭代精炼 scaffold，使弱目标 GPT-5.4-mini 平均精度 **0.488→0.763（+0.275）**，最佳 run 达 **0.912（+0.423，+86.7%）**，近翻倍。**机制归因（核心）**：收益主要来自①不稳定推理**卸载到确定性代码**、②基准专用路由、③严格答案格式强制——而**非**鼓励目标模型更多推理或更广采样（认知负荷降低 r=0.72）；确定性卸载比例与精度 Pearson r=0.72，代码量仅 r≈0.22。builder 推理 effort 单调提升 scaffold 质量（Spearman ρ=0.77），验证预算与最终质量无关（r=0.17），平台效应二阶且条件性（+0.013 不显著）。**Harness 研究线连续第四天获实证**（08-10 HarnessOpt-Bench → 08-11 SkillProx → 08-13 Evo-Bench v2 → 今日 AI4AI），直接验证本地「AI 概率内核×工程确定性外壳」判断。
>
> **关键词**: 测试时能力转移 · strong-to-weak scaffolding · harness 工程 · 认知负荷降低 · 确定性卸载 · 任务结构编译 · ToM 推理 · 验证高效优化
>
> **数据源**: arXiv:2608.12307 HTML 全文一手精读（含 Algorithm 1、Table 1-5、Figure 1-12、Aspect 0-9 全部分析）
>
> **素材分级**: 🔵 一手论文全文（arXiv HTML 实验版 103,664 字符全文解析）· 🔵 既有研究线锚点（08-10/08-11/08-13 三篇 harness 文档 + 01_survey 登记）· 🔵 本地方法论（AI概率内核×工程确定性外壳）
>
> **日期**: 2026-08-14 | **领域**: Agent 工程 / harness 自进化 / 推理时优化

---

## 📑 目录

- [〇、结论概要](#〇结论概要)
- [一、研究线定位：连续第四天的 Harness 实证](#一研究线定位连续第四天的-harness-实证)
- [二、范式定位：测试时转移 vs 训练时蒸馏](#二范式定位测试时转移-vs-训练时蒸馏)
- [三、方法：递归 scaffold 构建算法（Algorithm 1 精读）](#三方法递归-scaffold-构建算法algorithm-1-精读)
- [四、实验设置全景](#四实验设置全景)
- [五、九大发现（Aspect 0-9）核心原理与数据](#五九大发现aspect-0-9核心原理与数据)
- [六、机制归因：为什么是「确定性卸载」而非「更多推理」](#六机制归因为什么是确定性卸载而非更多推理)
- [七、技术分类学：12 种 scaffold 技术全景](#七技术分类学12-种-scaffold-技术全景)
- [八、认知负荷降低：offloading × structuring 双通道](#八认知负荷降低offloading--structuring-双通道)
- [九、与知识库互证](#九与知识库互证)
- [十、批判性审视](#十批判性审视)
- [十一、可证伪预测](#十一可证伪预测)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 〇、结论概要

**一句话：强模型不必把能力「灌进」弱模型的权重，而是可以在推理时把弱模型的「认知负荷」卸载到确定性代码与严格约束里——builder 是任务能力的编译器，target 是编译后程序的执行器，收益来源是结构性外化而非更多推理。**

1. **范式成立且巨大**：57 个 scaffolded run 全部超越无 scaffold 基线（100%），均值 +0.275；最佳 run（GPT-5.5/GPT Codex）0.912，**超过无 scaffold 的 GPT-5.4 大模型本身（0.619）**——scaffold 一个弱模型有时比直接升级到更强的裸模型收益更大。
2. **收益归因清晰**：增益由「可靠性地板」（格式强制 100%、greedy 98%、路由 95%）+「任务结构利用」（极性/否定逻辑 +0.090、结构化抽取 +0.055、确定性求解）双层驱动；**与「鼓励更多推理」无关**（forced CoT 关联仅 +0.007，采样自一致性 +0.038 且仅 3/57 runs 使用）。
3. **认知负荷降低是机制核心**：确定性卸载比例（det. fraction）与精度 r=0.72，是单个最强解释变量；代码量本身与精度弱相关 r≈0.22——「写更多代码」不是关键，「把正确的认知负荷移出模型」才是。
4. **builder 能力与 effort 主导，平台次要**：builder 推理 effort 四档单调提升（0.711→0.856，Spearman ρ=0.77）；平台原生优势仅 +0.013（p=0.484 不显著），且只在 builder 有足够推理预算时才浮现（platform×effort 交互）。
5. **目标模型由「headroom」而非身份决定**：uplift 与目标在基准上的可提升空间（1−baseline）r=0.75；弱目标受益大（+0.262 vs +0.110），强目标在已饱和任务上会**过度 scaffold 回火**（9/20 个基准-目标组合回退）。
6. **验证高效但假设质量才是瓶颈**：中位数仅 5 次验证评估，best-val 与 full-set r=0.96、乐观偏差仅 0.021；但验证迭代次数与最终精度 r=0.17 无关——**决定质量的是 builder 的假设质量，不是探测次数**。

---

## 一、研究线定位：连续第四天的 Harness 实证

| 日期 | 工作 | 核心主张 | 本地归档 |
|:-----|:-----|:---------|:---------|
| 08-10 | HarnessOpt-Bench / EvoHarness-RL（LLA@COLM）| harness 作为一阶优化对象；EvoHarness 用稀疏奖励 RL 演化 harness 代码 | `2026-08-10-harness-optimization-self-evolution-skill-gating.md` |
| 08-11 | SkillProx（arXiv:2608.07449）| 前向-后向近端框架优化**技能文本**——闭环诊断 + leave-one-out 效用审计 | `2026-08-11-skillprox-proximal-textual-gradient-descent-deep-analysis.md` |
| 08-13 | Evo-Bench v2（arXiv:2608.09096）| 系统化评估 agent「自主优化自身运行 harness」能力，隔离 harness 改进与基础模型能力 | `01_survey/llm-trends/2026-08-13.md` 登记 |
| **08-14** | **AI4AI at Test-Time（arXiv:2608.12307）** | **测试时强→弱转移**：builder 为 target 构建推理时 scaffold，零参数更新，0.49→0.91 | **本文档** |

**四天研究线的演进逻辑**：从「harness 可被优化」（08-10，框架提出）→「harness 的最小单元——技能——可被近端优化」（08-11，单元级机制）→「如何系统评估 harness 进化能力」（08-13，评测隔离）→「harness 本身能实现能力转移、且转移机制可归因」（今日，**效果 + 机制双落地**）。AI4AI 把前三天的「agent 自我优化 harness」扩展为**跨模型**的「强者为弱者造 harness」，并第一次给出**机制级归因**（确定性卸载、路由、格式约束 vs 更多推理），回答了 SkillProx 与 Evo-Bench 遗留的「harness 为什么有用、收益来自哪」问题。

**与本地方法论互证**：本文的「builder 一次性推理预算把任务结构编译进确定性代码」正是本地「**AI 概率内核 × 工程确定性外壳**」判断的论文级实证——概率内核（weak target）保留给无法编译的残差推理，确定性外壳（scaffold 代码/规则）承担可编译的子任务；「认知负荷降低 r=0.72」为本地 harness 架构（Bridge 枢纽、五层依赖单向化、契约探测）提供了量化依据。

---

## 二、范式定位：测试时转移 vs 训练时蒸馏

### 2.1 两条能力路线（论文 §7 高层框架）

```
            +-----------------------------------------------------+
            |        Two complementary routes to better systems   |
            +-----------------------------------------------------+
                              |
             +----------------+----------------+
             v                                 v
  Route A: make model more capable   Route B: make task easier
  - pretraining / SFT / RLHF        - harness / scaffold design
  - distillation (update weights)   - routing / prompt templates /
  - most post-training work           verification / deterministic
  [training-time paradigm]             solvers / format constraints
                                      [test-time paradigm, THIS PAPER]
```

| 维度 | 路线 A：提升模型内部能力 | 路线 B：让任务更容易执行 |
|:-----|:------------------------|:-------------------------|
| 手段 | 预训练 / 指令微调 / RLHF / 蒸馏 | harness / scaffold 设计 / 路由 / 提示模板 / 校验 / 确定性求解 / 格式约束 |
| 载体 | 模型权重（改参数） | 推理环境（零参数更新）|
| 范式 | 训练时 | **测试时（本文）** |
| 主导工作 | 蒸馏 / post-training | 本文 AI4AI（2608.12307）|

### 2.2 与既有能力转移方法的本质区别

| 方法族 | 转移载体 | 是否改参数 | 代表性工作 |
|:-------|:---------|:----------:|:-----------|
| 经典知识蒸馏 | 软化输出分布 | ✅ | Hinton 2015 |
| 分步蒸馏 | 教师生成的 rationale | ✅ | Distilling step-by-step（Hsieh 2023）|
| On-policy 蒸馏 | 自生成轨迹 + 教师反馈 | ✅ | Agarwal 2024 |
| 弱→强泛化 | 弱监督信号 | ✅ | Burns 2023 |
| **强→弱 scaffolding（本文）** | **推理时 harness（代码/规则/路由/格式）** | ❌ **零参数更新** | **AI4AI（2608.12307）** |

**关键区分**：蒸馏改「模型」，scaffolding 改「模型所处的推理环境」。本文的隔离设计保证了转移的不是实例答案而是可复用任务结构——builder 只见过 5% 验证集，最终 scaffold 必须泛化到 95% 隐藏测试集，因此**成功的 scaffold 必然编码了任务结构而非记忆具体答案**。

### 2.3 与单模型推理增强方法的区别

CoT/self-consistency/least-to-most/ToT/GoT/Self-Refine 都是「优化同一模型在单实例上的推理方式」；本文是**跨模型**的持久化过程构造——builder 构建的 scaffold 是一个可对任意隐藏实例执行的程序，其执行者是被 scaffold 的弱模型。

---

## 三、方法：递归 scaffold 构建算法（Algorithm 1 精读）

### 3.1 设置与工作区

对每个基准 𝒟⁽ʲ⁾：随机采样 **5% 作验证集 𝒱**（195 条，固定随机种子），其余为**隐藏测试集 𝒯**（3900 条）。builder 初始工作区由三部分组成：

- `ℛ`：规则文件（任务指令 + 提交格式）
- `𝒞_demo`：目标模型调用演示
- `𝒱`：带标签验证集

**隔离保证**：builder 全程看不到 𝒯；唯一优化信号是验证集精度。搜索目标（隐藏集最优）用验证集代理：

- 理想目标（不可达）：`S* = argmax_S Acc(S, M_tar; 𝒯)`（𝒯 隐藏）
- 实际优化目标：`Ŝ = argmax_S Acc(S, M_tar; 𝒱)`（验证集代理）

### 3.2 递归精炼循环（Algorithm 1 六步）

| 步骤 | 动作 | 细节 |
|:-----|:-----|:-----|
| 1 | 检查任务资源 | builder 读取 ℛ、𝒞_demo、𝒱，理解任务 |
| 2 | 提出/修订 scaffold | builder 实现任意推理时程序（不限制架构）|
| 3 | 验证集评估 | 调 target 模型执行 scaffold，算验证精度 aₖ |
| 4 | 诊断改进 | 收集错误集 ℰₖ={(x,y,ŷ): ŷ≠y}，并入工作区 𝒲ₖ₊₁ |
| 5 | 导出入口点 | 提交可执行入口 f_Ŝ(x; M_tar) |
| 6 | 隐藏评估 | 人类评估者在 𝒯 上运行，报告最终精度 |

**设计要点**：scaffold 空间 𝒮 不受架构约束——builder 可实现提示模板、路由、确定性前后处理、格式强制、校验 pass、few-shot 检索、甚至直接符号求解器。唯一要求是最终入口可泛化到未见实例。

### 3.3 什么是「成功的 scaffold」？

必须满足两个条件：①从 5% 验证切片中识别**可复用任务结构**；②该结构**跨样本迁移**到隐藏测试集。这天然排除了「记住验证集答案」式的过拟合——一个 memorization scaffold 在隐藏集上必然崩溃。论文用「验证集最优精度与隐藏集精度 r=0.96」证明 5% 切片是忠实代理，且「验证-隐藏乐观偏差仅 0.021」证明过拟合轻微。

---

## 四、实验设置全景

### 4.1 任务：4 个 ToM 基准聚合（3900 条隐藏测试集）

| 基准 | 数量 | 内容 | 可编译性（论文实测 det. fraction）|
|:-----|:----:|:-----|:----------------------------------:|
| BigToM | 1200 | 二值 belief/goal/action 问题，基于是否观察到世界变化 | **0.94**（几乎完全可确定性化）|
| Hi-ToM | 1200 | 嵌套信念问题，递归阶 0-4，含欺骗与多房间物体追踪 | 0.51（符号信念状态追踪）|
| MMToM-QA | 600 | 二值贝叶斯 goal/belief 推断（动作轨迹）| 0.44 |
| MuMA-ToM | 900 | 3 选多智能体 belief/social-goal/belief-of-goal | **0.36**（最难编译）|

### 4.2 控制变量设计（72 runs 总计）

| 变量 | 取值 | 说明 |
|:-----|:-----|:-----|
| **Builder 模型** | Opus-4.7（4 档 effort）、Sonnet-4.6、GPT-5.5、GPT-5.4-mini、Codex-5.3、Gemini-3.1-Pro、Gemini-3.5-flash、Grok-0.1（11 个配置）| 除 Opus-4.7 外均用最高 effort |
| **Target 模型** | GPT-5.4-mini（主）、Gemini-3.5-flash（对照）| 弱目标为公共对照组 |
| **平台（builder 自身 harness）** | Cursor（中立第三方）、Claude Code（Claude 原生）、GPT Codex（GPT 原生）| 每 builder 家族有原生平台 |
| **Repeats** | 每个设置 3 次 | 考察 scaffold 稳定性 |
| **主设置 runs** | 57 runs（GPT-5.4-mini 为 target）| 11 builder 配置 × 平台 × 3 repeats |

### 4.3 基线

| 基线 | GPT-5.4-mini | Gemini-3.5-flash | 含义 |
|:-----|:------------:|:----------------:|:-----|
| **Vanilla**（无 scaffold 直调）| 0.488 | 0.761 | scaffold 待超越的下限 |
| **UserHarness**（人类设计的 ToM harness）| 0.939 | 0.941 | 人类 harness 工程的参考上限 |

另加两个参考点：无 scaffold 的 GPT-5.4（0.619，更大模型裸跑）与 GPT-OSS-120B。

---

## 五、九大发现（Aspect 0-9）核心原理与数据

### 5.1 Aspect 0：主结果——大而稳健

| 指标 | 值 |
|:-----|:---|
| GPT-5.4-mini vanilla 基线 | 0.488 |
| 全部 scaffolded runs 均值 | **0.763（+0.275）** |
| 最佳 run（GPT-5.5/GPT Codex）| **0.912（+0.423，+86.7%）** |
| 超越基线的 runs 占比 | **100%**（57/57）|
| 超越裸 GPT-5.4（0.619）的配置 | 多个（scaffold 弱模型 > 升级裸大模型）|
| 接近人类 UserHarness（0.939）| 差 0.027（BigToM 上反而超过：1.00 vs 0.95）|

**builder 排序（图 3a）**：GPT-5.5 (0.875) > Opus-4.7-xhigh (0.856) > Gemini-3.5-flash (0.813) > Sonnet-4.6 (0.810) > Opus-4.7-high (0.807) > Opus-4.7-med (0.793) > Gemini-3.1-Pro (0.713) > Opus-4.7-low (0.711) > GPT-5.4-mini 自建 (0.681) > Codex-5.3 (0.675) > Grok-0.1 (0.563)。**builder 形成清晰纵向排序，平台差异远小于 builder 差异**。

### 5.2 Aspect 1：稳定性——可复现但不确定

- 平均组内标准差 **0.036**，约为主提升（+0.275）的 1/7；最宽组内跨度 0.201。
- **不稳定来源**：确定性求解策略——单条基准专用规则的一个逻辑错误可在 1000+ 条基准上移动数十个百分点；纯提示 scaffold 更稳定但增益小。
- **实操配方**：构建 2-3 个 scaffold 取验证集最优者，低成本捕获设置性能上限。

### 5.3 Aspect 2：验证效率——5% 切片是忠实代理

| 统计量 | 值 | 含义 |
|:-------|:---|:-----|
| 平均验证评估次数 | 4.9（中位数 5，范围 2-15）| builder 用验证很节俭（次要评分标准鼓励）|
| 首轮→最优验证精度增益 | +0.216 | 组内精炼有效 |
| best-val vs full-set 相关 | **r=0.96** | 验证集忠实代理隐藏集 |
| 验证-隐藏乐观偏差 | 均值 0.021 | 过拟合轻微 |
| 验证迭代次数 vs 最终精度 | **r=0.17**（无关）| 假设质量 > 探测次数 |

### 5.4 Aspect 3：scaffold 技术——纪律性任务工程而非奇技淫巧

12 种技术按使用率排序（57 runs）：格式强制 100% > greedy/temp 98% > 基准路由 95% > forced CoT 79% > 极性/否定逻辑 79% > token 预算 75% > hybrid fallback 60% > 确定性求解器 54% > 结构化抽取 51% > few-shot 21% > 验证/仲裁 12% > 自一致性投票 5%。

**解法分布**：BigToM 多为确定性/混合规则（问题暴露 observed/unobserved 区分）；MuMA-ToM 几乎全交给模型（自由对话推理难编译）。**per-benchmark 解法图 = ToM 任务的可编译性排序**。

### 5.5 Aspect 4：平台效应——二阶且条件性

- 原生平台 vs Cursor 匹配比较：仅 **+0.013**（p=0.484 不显著），8 对中 5 对原生胜——无系统性「自家平台最强」规则；GPT 家族效应略大（+0.020，主要由 Codex-5.3 +0.069 驱动）。
- **关键发现是 platform×effort 交互**：Opus-4.7 低 effort 时 Claude Code 落后 Cursor（−0.034），中/高/超高 effort 时反超（+0.045/+0.038/+0.032）——**原生 harness 的 affordance 只在 builder 有足够推理预算时才被利用**。
- 平台边际均值（Claude Code 0.799 > GPT Codex 0.754 ≈ Cursor 0.750）主要是 roster 构成（Opus/Sonnet 扎堆）而非因果平台优势。

### 5.6 Aspect 5：目标模型——headroom 定律

- 弱目标受益大：GPT-5.4-mini +0.262 vs Gemini-3.5-flash +0.110（5 个 builder 方向一致）。
- **Headroom 定律**：uplift 与 1−baseline r=0.75——scaffolding 是「能力回收」机制：回收目标已有但不稳定部署的潜在能力（格式遵循、观察线索追踪、递归状态维护）。
- 强目标增益集中在 BigToM（占其 macro uplift 的 96%）——既有 headroom 且结构最可编译的基准。
- **策略自适应**：scaffold 强目标时 builder 少用确定性机制（MuMA model-only 占比 40%→73%），把重规则干预留给剩余可编译 headroom。
- **过度 scaffold 回火**：Gemini-3.5-flash 上 9/20 个基准-目标组合回退（Hi-ToM −0.04、MuMA −0.02 平均）——目标接近天花板时，额外提示/路由/规则**干扰正确行为多于修复错误**。

### 5.7 Aspect 6：builder 推理 effort——单调杠杆

Opus-4.7 四档 effort × 双平台（target=GPT-5.4-mini）：

| Platform | low | medium | high | extra-high |
|:---------|:---:|:------:|:----:|:----------:|
| Cursor | 0.728 | 0.770 | 0.788 | 0.840 |
| Claude Code | 0.694 | 0.816 | 0.826 | 0.872 |
| **池化** | **0.711** | **0.793** | **0.807** | **0.856** |

- 单调性 Spearman ρ=0.77；extra-high vs high p=0.013，vs low p=0.002——非噪声。
- **最大增益在 low→medium**：中等推理足以发现主要结构装置（路由/格式/确定性求解），更高档位做精化（极性逻辑、信念状态抽取）。
- scaffold 代码量随 effort 增长（510-650 → 1000-1300 LOC）——builder 把更多任务逻辑编译进 harness。
- **对比 Aspect 2 的 r=0.17**：有用的测试时算力不是更多验证探测，而是**更深的假设形成**。

### 5.8 Aspect 7：归因——两层互补机制

**技术关联度（有该技术 vs 无该技术均值差）**：极性/否定逻辑 +0.090、结构化抽取 +0.055、few-shot +0.042、hybrid fallback +0.040、自一致性 +0.038†、路由 +0.033†、确定性求解 +0.026、forced CoT **+0.007**；token 预算 −0.047、验证/仲裁 −0.097、greedy −0.110†（†小对比组不可靠）。

**McNemar 显著性**（最佳 scaffold vs 基线，3900 条）：修复 1717 条基线错误、破坏仅 105 条正确项，χ²≫10⁴，p<10⁻⁴——**增益不是误差再分配，而是从错误到正确的大规模转移**。

**自建 vs 强 builder**：GPT-5.4-mini 为自己建 scaffold 已 +0.17~+0.22（弱模型也能利用验证反馈与任务结构）；但强 builder 在 GPT Codex 上 +0.31 vs 自建 +0.17——**强 builder 是解锁高性能区的必要条件**。

**互补性**：top scaffolds 在易修复错误上重叠，在难例上分化；**并集覆盖 97% 基线错误**，超过任何单个 scaffold——不同 builder 发现部分不同的修复机制。

### 5.9 Aspect 8：认知负荷降低——机制核心

- **确定性卸载比例与精度 r=0.72**（最强解释变量）：scaffold 用代码/规则直接回答的条目占比越高，最终精度越高。
- 基准可卸载性：BigToM 0.94 > Hi-ToM 0.51 > MMToM 0.44 > MuMA 0.36。
- **代码量与精度仅 r≈0.22**——「写更多代码」不重要，「写对代码、移除正确的认知负荷」才重要。

### 5.10 Aspect 9：剩余错误——不可编译核心的边界

- **修复/破坏不对称**：8 个最强 scaffold 平均修复 83% 基线错误、仅破坏 7% 正确项——近似 Pareto 改进。
- BigToM 几乎解决（所有切片 ≥0.95）。
- 残差集中三处：①Hi-ToM 递归深度 order 0=0.999 → order 4=0.700，欺骗使性能再降（0.829→0.772）；②MMToM 贝叶斯目标推断子类型（qtype 2.1 仅 0.680）；③MuMA social_goal（0.872）与 belief_of_goal（0.880）标签。
- **边界含义**：scaffold 成功的边界 = 任务结构可编译性边界；最深的递归信念追踪与贝叶斯目标推断需要**更强的显式信念追踪机制**，而非同一设计的更多变体。

---

## 六、机制归因：为什么是「确定性卸载」而非「更多推理」

### 6.1 排除法证据链（论文多角度交叉验证）

| 候选解释 | 证据 | 结论 |
|:---------|:-----|:-----|
| 更多推理（forced CoT）| 关联仅 +0.007，45/57 runs 使用但区分度≈0 | ❌ 非主因 |
| 更广采样（self-consistency）| 仅 3/57 runs 使用，+0.038 且小样本不可靠 | ❌ 非主因 |
| 更多验证探测 | 迭代次数与精度 r=0.17 无关 | ❌ 非主因 |
| 更多代码 | 代码量与精度 r≈0.22 弱相关 | ❌ 非主因 |
| **确定性卸载 + 任务结构利用** | **det. fraction r=0.72；极性逻辑 +0.090** | ✅ **主因** |
| 可靠性地板（格式/路由/greedy）| 100%/95%/98% 使用率，防可避免错误 | ✅ 必要非充分 |

### 6.2 第一性原理：builder 作为「任务能力编译器」

论文 §6 takeaway 给出了最凝练的机制表述：**builder 花一次性推理预算识别任务结构并编码进推理时 scaffold；编译完成后，弱而便宜的 target 以接近强模型的水平执行任务**。

**编译期（一次性）**：builder 模型从 5% 验证集识别可编译任务结构，编码为确定性代码 / 规则 / 路由 / 约束提示，用验证精度闭环迭代精炼（中位数 5 次）。

**执行期（每次推理）**：scaffold 入口 `f_Ŝ(x; M_tar)` 分流——可编译子任务由确定性代码直接回答（零模型调用）；残差子任务经约束提示 + 格式强制交给弱模型。

**「scaffolding 不替代原始推理能力，它重新分配推理能力」**——builder 做结构性推理（一次），target 处理残差模型依赖推理（每次）。这与本地「AI 概率内核×工程确定性外壳」完全同构：概率内核（target）只在确定性外壳（scaffold）无法覆盖的残差上工作。

### 6.3 认知负荷降低的双通道

1. **Offloading（卸载）**：确定性代码/规则直接回答部分条目——target 零推理负担；可卸载性决定上限（BigToM 0.94 vs MuMA 0.36）。
2. **Structuring（结构化）**：仍需模型时，scaffold 把任务收窄为输入更清晰、输出格式更严格、推理焦点更聚焦的约束提示——降低模型自身的判断负担。

---

## 七、技术分类学：12 种 scaffold 技术全景

### 7.1 按功能分层

**L1 可靠性地板（近通用，防止可避免错误）**：格式强制 100%、greedy/temp 98%、基准路由 95%。

**L2 任务结构利用（区分强弱 scaffold，编译任务规律）**：极性/否定逻辑 79%、结构化抽取 51%、确定性求解器 54%、hybrid fallback 60%。

**L3 复杂策略（少数使用，成本高收益存疑）**：few-shot 21%、验证/仲裁 12%、自一致性 5%。

```
Layer  Role                              Techniques (prevalence)
L1     reliability floor                 format enforcement 100% / greedy 98% / routing 95%
L2     task-structure exploitation       polarity 79% / structured extraction 51% /
                                         deterministic solver 54% / hybrid fallback 60%
L3     complex strategies (rare)         few-shot 21% / verification 12% / self-consistency 5%
```

### 7.2 关键洞察

- **L1 是「使高绩效成为可能」的必要条件**：格式强制（100%）与 greedy（98%）因近乎通用而无法解释 run 间差异（对比组太小），但缺失它们时弱模型会在畸形输出/格式混淆/采样方差上损失精度。
- **L2 是「区分强弱」的充分条件**：极性/否定逻辑（+0.090）直接命中 ToM 基准的 MOST-vs-LEAST 框架错误；结构化抽取（+0.055）命中信念状态追踪；确定性求解（+0.026）把可预测子问题卸载进代码。
- **L3 的负关联不可误读**：token 预算（−0.047）、验证/仲裁（−0.097）、greedy（−0.110）的「负效应」来自小对比组由异常弱 run 构成——是关联性而非因果性。

---

## 八、认知负荷降低：offloading × structuring 双通道

### 8.1 determinism fraction 的量化作用

| Builder | Platform | Det. Frac. | Acc. | Py LOC |
|:--------|:---------|:----------:|:----:|:------:|
| Opus-4.7 (x-high) | Claude Code | 1.00 | 0.879 | 1052 |
| GPT-5.5 | GPT Codex | 0.99 | 0.903 | 1285 |
| GPT-5.5 | Cursor | 0.98 | 0.908 | 1026 |
| GPT-5.5 | GPT Codex | 0.86 | **0.912** | 1288 |
| GPT-5.5 | Cursor | 0.85 | 0.837 | 1107 |
| Codex-5.3 | GPT Codex | 0.31 | 0.746 | 903 |
| Opus-4.7 (med) | Cursor | 0.31 | 0.798 | 796 |

**反直觉案例**：det. frac 0.86 的 run（0.912）超过 det. frac 0.98/0.99 的 run（0.908/0.903）——**不是卸载越多越好**，而是「卸载对的部分」：把可编译结构（BigToM 规则、Hi-ToM 信念状态）卸载，把不可编译部分（MuMA 对话推理）留给模型，才是最优分配。这解释了为什么 r=0.72 是「强关联」而非「完美关联」——线性关系之上存在 benchmark 依赖的最优卸载边界。

### 8.2 与本地 harness 架构的映射

| 本文概念 | 本地系统对应 | 含义 |
|:---------|:-------------|:-----|
| builder 编译期一次性推理 | Bridge 枢纽设计 / 五层依赖单向化 | 结构决策前置，执行期零决策 |
| 确定性卸载（det. code/rules）| 确定性外壳（契约/脚本/检查器）| 可编译逻辑移出模型 |
| 格式强制 + 路由 | 输出 Schema 校验 + 渠道/任务路由 | 防可避免错误的可靠性地板 |
| 残差模型依赖推理 | 概率内核（模型判断）| 保留给不可编译的开放性判断 |
| 验证集闭环（中位数 5 次）| 受控管线（暂存→加工→沉淀）| 少而精的反馈胜过多而杂的探测 |

---

## 九、与知识库互证

### 9.1 Harness 研究线（四天连续实证）

1. **08-10 HarnessOpt-Bench/EvoHarness-RL**：harness 代码是可被稀疏奖励 RL 演化的一阶对象——本文把演化目标从「agent 自身 harness」扩展到「为弱模型造的 scaffold」，且用 72-run 大规模对比给出系统证据。
2. **08-11 SkillProx**：技能文本可用近端约束优化（闭环诊断 + 效用审计）——本文 Aspect 7 的「builder 假设质量 > 探测次数」（r=0.17 vs effort 单调 ρ=0.77）为 SkillProx 的「闭环诊断价值」提供了跨模型证据；两者共同指向**「反馈质量 > 反馈数量」**。
3. **08-13 Evo-Bench v2**：隔离 harness 改进与基础模型能力——本文的 strong-to-weak 设置是这种隔离的极端化：target 完全不参与 harness 构建，harness 收益 100% 可归因于 builder。
4. **今日 AI4AI**：完成从「可优化」→「可评测」→「可归因」→「可转移」的闭环。

### 9.2 本地方法论互证

- **「AI 概率内核×工程确定性外壳」**：本文 det. fraction r=0.72 是「确定性外壳价值」最强的量化实证——AI 系统性能提升的主杠杆是把认知负荷移出概率内核。
- **「验证是唯一把可能性变确定性的操作」**（MEMORY.md 决策方法论）：本文 best-val r=0.96、乐观偏差 0.021 证明验证集代理的有效性；「验证高效（中位数 5 次）+ 假设质量主导」与本地「少而严优于多而松」的防护通胀 S 曲线判断同构。
- **「推理成本第一杠杆」**：scaffold 把每实例推理成本从「弱模型反复思考」降为「确定性代码 + 约束单次调用」，是推理时降本的机制级路径。
- **Token 成本实证**（system prompt 118K→18K 省 85%）：与本文「把任务逻辑编译进确定性代码而非塞进 prompt」是同一原理的不同载体。

### 9.3 与既有深分析文档的链接

- [SkillProx 深分析](2026-08-11-skillprox-proximal-textual-gradient-descent-deep-analysis.md)
- [Harness 优化自进化](2026-08-10-harness-optimization-self-evolution-skill-gating.md)
- [Harness 实证四论文](2026-08-07-harness-empirical-four-papers.md)
- [Harness 成本证据](2026-08-14-harness-cost-evidence-multiagent-safety-plugin-standard-deep-analysis.md)
- [AI 生产流水线 Token 优化五技术](2026-08-14-ai-pipeline-token-optimization-five-techniques-deep-analysis.md)

---

## 十、批判性审视

### 10.1 局限与风险

| 局限 | 说明 | 影响评估 |
|:-----|:-----|:---------|
| **ToM 单一领域** | 4 个基准同属社会推理；可编译性分布可能不具代表性 | 中——需扩展到数学/代码/长程 agentic 任务验证范式普适性 |
| **可编译结构 ≠ 真实能力** | BigToM 被「完全编译」是否算真实 ToM 能力提升存疑——benchmark 捷径与真实推理的边界 | 中——论文自辩：发现可编译结构本身是 builder 能力 |
| **技术归因是关联性** | 12 技术共现，Δ 是均值差而非因果效应；小对比组（<5 runs）不可靠 | 中——作者明示 associational，需随机对照消融 |
| **模型是 2026 年闭源前沿** | builder/target 均为闭源（GPT/Claude/Gemini/Grok），无法复现核验 | 高——依赖作者执行完整性，无开源代码/模型 |
| **平台样本少** | Cursor 是唯一中立平台，Codex/Claude Code 各只服务本家族 + 少数 | 中——platform 效应结论需更多中立平台验证 |
| **5% 验证集的运气依赖** | 固定随机种子，若验证切片代表性与任务结构偏差大则结论可能漂移 | 低——r=0.96 表明切片忠实，但只测了一个种子 |
| **39% 数据未完全展示** | HTML 版 Table 4 部分行截断（0.762 之后若干行缺失）| 低——不影响主结论 |

### 10.2 值得注意的反直觉点

1. **forced CoT 关联仅 +0.007**——与主流「CoT 提升推理」共识冲突：在「scaffold 外化」语境下，让弱模型想更多不如让结构做得更好。
2. **greedy 关联 −0.110（†）**——近通用技术（56/1）的负关联是统计陷阱而非因果，但也提示「temp 控制」本身不是增益来源。
3. **verification/arbiter 关联 −0.097**——「加验证器」在弱目标 + ToM 场景未必有益：验证器本身也是模型，弱模型的验证判断同样不可靠（与本地「验证必须自动化否则边际成本递增」判断互证）。
4. **代码量与精度 r≈0.22**——「写更多代码」诱惑是陷阱；有效的是「对的结构卸载」而非「更多结构」。

---

## 十一、可证伪预测

| # | 预测 | 可证伪条件 | 时间窗 |
|:--|:-----|:-----------|:-------|
| P1 | strong-to-weak scaffolding 在数学/代码基准上同样有效（det. fraction 与精度 r>0.5），但可编译性分布不同（数学 0.7-0.8、代码 0.5-0.6）| 若数学基准 det. fraction <0.3 或 r<0.3 则证伪 | 2027-06 前复现 |
| P2 | 「过度 scaffold 回火」是普遍规律：任何目标在 headroom <0.15 的子任务上，额外 scaffold 干预的净期望为负 | 若强目标在高饱和子任务上 scaffold 平均净正则证伪 | 2026-12 前 |
| P3 | builder effort 单调性（ρ=0.77）在更强 builder（≥Opus-4.7-xhigh）上出现天花板——extra-high 以上增益趋零甚至转负（over-engineering）| 若 effort 更高档位持续线性增益则证伪 | 2027-06 前 |
| P4 | 「假设质量 > 探测次数」（r=0.17）推广为通用定律：任意自动 harness 优化系统，迭代预算超过某阈值后质量不再提升 | 若存在「探测次数与质量强正相关（r>0.5）」的反例系统则证伪 | 2027-12 前 |
| P5 | scaffolding-as-benchmark 成为主流 builder 评估范式之一（论文 §7 提议），至少 1 个独立机构发布同类基准 | 若 2027 年底无任何 follow-up 基准则证伪 | 2027-12 前 |

---

## 参考来源

1. arXiv:2608.12307（cs.LG，2026-08-12 提交，23 页 12 图 6 表）——Cheng Qian, Wenting Zhao, Liangwei Yang, Heng Wang, Jielin Qiu, Heng Ji, Silvio Savarese, Huan Wang, Shelby Heinecke（Salesforce AI Research × UIUC）。HTML 全文精读（含 Algorithm 1、Table 1-5、Figure 1-12、Aspect 0-9）。https://arxiv.org/abs/2608.12307
2. 知识库研究线锚点：`2026-08-10-harness-optimization-self-evolution-skill-gating.md`、`2026-08-11-skillprox-proximal-textual-gradient-descent-deep-analysis.md`、`01_survey/llm-trends/2026-08-13.md`（Evo-Bench v2 登记）、`01_survey/llm-trends/2026-08-14.md`（AI4AI 今日头条登记）

> **溯源标注**：所有量化数据均来自论文原文（Table 1-5 / Figure 2-12 / Aspect 0-9 正文），已在对应位置标注。论文 HTML 版 Table 4 部分行在抓取时截断（det. frac 0.48 之后若干行），不影响主结论。研究线日期与文档路径经知识库索引核验。

---

## Changelog

- **2026-08-14 v1.0**：初版。arXiv:2608.12307 全文精读 → 9 大发现（Aspect 0-9）+ 机制归因（确定性卸载 vs 更多推理）+ 12 技术分类学 + 认知负荷双通道 + 研究线四天互证 + 批判性审视 + 可证伪预测 P1-P5。
