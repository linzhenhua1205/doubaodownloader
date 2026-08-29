# ⚔️ RL Post-training 成为算力平台调度主战场：MISA-T × TideRL × RoutePack 三线齐发

> **类型**: 深度专题（三篇论文联动） | **日期**: 2026-08-14
> **定位**: 2026-08-11~08-12 公告窗口内，三篇独立工作同日解决 RL post-training 管线中**调度 × KV × 打包**三个耦合问题——范式确认信号。本文延续知识库 goodput 记忆线（Cascade→MARS→TideRL），并以 **RoutePack 首次全文深度** + **三线耦合关系第一性原理分析**为差异化增量；TideRL/MISA-T 的单篇全文细节已在 08-13 工作流文档深度收录，本文做框架级重述 + 交叉引用，不重复。
> **数据源**: arXiv 一手抓取——TideRL [arXiv:2608.10402](https://arxiv.org/abs/2608.10402)（摘要全文）、MISA-T [arXiv:2608.11152](https://arxiv.org/abs/2608.11152)（摘要全文）、RoutePack [arXiv:2608.12146](https://arxiv.org/abs/2608.12146)（**HTML 全文精读，89KB**，Ant Group）
> **数据分级**: 🟢 论文一手（摘要/全文） · 🟡 论文自述未量化项 · 🔴 知识库合流判断（组合收益为估算非实测）
> **关联文件**: [`2026-08-13-rl-training-toolchain-tiderl-misa-workflow-cards-deep-analysis.md`](../../02_rd/02_project/01_superpod/2026-08-13-rl-training-toolchain-tiderl-misa-workflow-cards-deep-analysis.md)（TideRL/MISA-T 单篇全文深度）、[`2026-08-11-cascade-slo-latency-budget-scheduling-deep-analysis.md`](2026-08-11-cascade-slo-latency-budget-scheduling-deep-analysis.md)（Cascade）、[`../../02_rd/01_product/01_software/02-distributed-os/2026-08-11-mars-mcts-adaptive-scheduler-deep-analysis.md`](../../02_rd/01_product/01_software/02-distributed-os/2026-08-11-mars-mcts-adaptive-scheduler-deep-analysis.md)（MARS）、[`2026-08-05-llm-inference-redundancy-elimination-deep-analysis.md`](2026-08-05-llm-inference-redundancy-elimination-deep-analysis.md)（四类冗余 MECE）、[`2026-08-10-llm-system-software-maturity-tensorcast-b300-plora-vibe.md`](2026-08-10-llm-system-software-maturity-tensorcast-b300-plora-vibe.md)（HorizonServe/调度升级）

---

## 📑 目录

- [0. 一句话结论](#0-一句话结论)
- [1. 背景：为什么 RL post-training 成为调度主战场](#1-背景为什么-rl-post-training-成为调度主战场)
- [2. 全景：三个耦合问题 × 三条独立战线](#2-全景三个耦合问题--三条独立战线)
- [3. MISA-T：路由层准入——KV 容量竞争治理（框架级重述）](#3-misa-t路由层准入kv-容量竞争治理框架级重述)
- [4. TideRL：就绪感知弹性调度（框架级重述）](#4-tiderl就绪感知弹性调度框架级重述)
- [5. RoutePack：专家放置 × 注意力打包联合优化（首次全文深度）](#5-routepack专家放置--注意力打包联合优化首次全文深度)
- [6. 三线耦合关系：为什么必须分开解、又如何合起来用](#6-三线耦合关系为什么必须分开解又如何合起来用)
- [7. goodput 记忆线：Cascade→MARS→TideRL 的范式演进](#7-goodput-记忆线cascademarstiderl-的范式演进)
- [8. 产业信号与可证伪预判](#8-产业信号与可证伪预判)
- [9. 数据缺口与诚实标注](#9-数据缺口与诚实标注)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 0. 一句话结论

> **RL post-training 的瓶颈已从"算力够不够"转移为"调度好不好"**：2026-08-11~08-12 公告窗口内，MISA-T（路由层准入，吞吐 +53.3%）、TideRL（就绪感知弹性调度，goodput 5.6×）、RoutePack（专家放置×注意力打包，+14.89%）三篇独立工作同日解决 RL 管线中**调度 × KV × 打包**三个耦合问题——与 08-11 期 Cascade（SLO 预算）、MARS（MCTS 前瞻）共同确认：**调度器 = RL 效率的第一杠杆，度量哲学从"GPU 占用率"全面转向"goodput（产出率）"**。三篇共享一个信息杠杆：**agentic/RL 工作负载的异构性与训练前可知性（routing replay / 就绪信号）把调度从"黑盒反应"变成"白盒规划"**。

---

## 1. 背景：为什么 RL post-training 成为调度主战场

### 1.1 工作负载形态的三个剧变（第一性原理）

传统 LLM 训练（预训练/微调）的调度问题接近"齐整的长方体"：样本长度近似、计算模式同质、同步屏障规整。**RL post-training 打破了全部三个假设**：

| 传统假设 | Agentic RL 现实 | 后果 |
|:--|:--|:--|
| 样本长度近似均匀 | 多轮 agent 轨迹**反复暂停等外部环境**、恢复时上下文增长、完成时间高度可变 | 同步 barrier 成为最大浪费源（TideRL 动机）|
| 计算模式同质 | RLVR / RLHF / agentic rollout **三种范式共享同一推理服务**，序列结构、交互模式、KV 驻留时间迥异 | prefix 路由不足以治理 KV 竞争（MISA-T 动机）|
| 路由行为稳定 | MoE 专家流行度**随策略更新快速漂移**（rapidly changing expert popularity）| 静态放置/长度打包失效（RoutePack 动机）|

### 1.2 调度问题为何"提前可知"（关键信息杠杆）

三篇论文共享一个此前未被利用的事实：**RL 的 rollout 与训练消费同一份 token 序列**。

- TideRL：rollout 任务的**就绪状态**（何时暂停、何时恢复、何时完成）在训练前可观测 → 变成调度信号；
- MISA-T：rollout session 的**序列结构与 KV 驻留时间**可预估 → 变成准入与容量分配依据；
- RoutePack：rollout-time **routing replay**（R3/ReLibra 已有机制）精确暴露每个样本的序列长度与逐层专家需求 → 把"数据布局"从 routing-blind 的预处理变成负载均衡控制。

> **总纲**：调度从"对不确定性的反应"变成"对已知信息的规划"——这是三篇同窗口爆发的方法论地基。

---

## 2. 全景：三个耦合问题 × 三条独立战线

### 2.1 问题的形式化：RL 管线中的三资源域

RL post-training 的训练步同时消费三种资源，分别由三个"域"决定：

```
+------------------------------------------------------------------+
|              RL post-training pipeline                           |
|                                                                  |
  rollout phase          training phase                           |
  +----------+   replay  +----------------------------------+      |
  | sampling |---------->| batch sealed -> plan -> execute  |      |
  | mixed    |  routing  |                                  |      |
  | sessions |   replay  | (1) sequence mix -> DP microbatch|      |
  +----------+           |     -> dense attention work      |      |
      |                  | (2) token routing -> EP rank     |      |
      |                  |     -> sparse expert work        |      |
      |                  | (3) session residency -> KV      |      |
      |                  |     -> prefill / hit rate        |      |
      +------------------+----------------------------------+      |
            +-- MISA-T: KV domain (routing layer / serving)       |
            +-- TideRL: time domain (rollout <-> training)        |
            +-- RoutePack: space domain (DP x EP layout)          |
+------------------------------------------------------------------+
```

| 资源域 | 决策变量 | 优化目标 | 战线 |
|:--|:--|:--|:--|
| **KV 容量（服务域）** | session 准入 / KV 容量分配 / 驻留记账 | 吞吐 × 前缀命中率 × 负载配比 | MISA-T |
| **时间（训练域）** | rollout-训练资源分配 / 批处理形状 | goodput（有效训练吞吐）| TideRL |
| **空间（布局域）** | 专家放置 / 样本打包 | 最慢 shard 的联合代价 | RoutePack |

### 2.2 三线齐发的信号强度

- **同日窗口**：TideRL 提交 08-10（公告 08-11）、MISA-T 提交 08-11、RoutePack 提交 08-12——72 小时内三篇独立论文（作者、机构、技术路线互不重叠）指向同一结论；
- **耦合而非并列**：三者解决的不是同一问题的三个版本，而是**同一个管线中相互耦合的三个瓶颈**——单解任何一个都会把瓶颈转移到另外两个（§6 展开）；
- 类比：知识库已记录"旋转×量化三支柱同日发布 = 学术范式确认信号"，本次"调度×KV×打包三战线"是同构信号，且发生在 **RL 训练侧**（此前记忆线集中在推理侧）。

---

## 3. MISA-T：路由层准入——KV 容量竞争治理（框架级重述）

> **单篇全文深度**：[08-13 RL 训练工具链三件套深度分析 §5](../../02_rd/02_project/01_superpod/2026-08-13-rl-training-toolchain-tiderl-misa-workflow-cards-deep-analysis.md)
> **arXiv**: [2608.11152](https://arxiv.org/abs/2608.11152)（cs.DC/cs.LG，2026-08-11 提交）

### 3.1 框架

MISA-T 是**路由层准入策略**（routing-layer admission policy），三件套：

| 组件 | 作用 | 解决的失效模式 |
|:--|:--|:--|
| **自适应 session 准入**（adaptive session admission）| 在进入推理服务前决定"放行/暂缓" | 异构 session 无差别涌入，KV 被长驻 session 挤占 |
| **负载感知 KV 容量分配**（workload-aware KV-capacity allocation）| 按工作负载类型（RLVR/RLHF/agentic）差异化分配 KV 容量 | 统一池化导致短驻留负载饿死 |
| **驻留时间感知 KV 记账**（residency-time-aware KV accounting）| 按 session 的预期 KV 驻留时长计价/配额 | prefix 命中率高但 KV 周转率低的隐性浪费 |

### 3.2 原理（第一性原理展开）

**MISA-T 的核心论点：prefix locality 不足**。Prefix-aware routing 优化"cache reuse + load balancing"，但它**不控制异构 rollout session 如何竞争 KV-cache 容量**——KV 驻留时间不同的 session 混跑时，即使命中率高，长驻 session 也在物理上占住容量、挤压其他 session 的 prefill 空间。

- 类比：这是**显存/内存的"会计"问题**——不做容量会计的系统，无论调度多聪明都会出现"看似满负荷、实则周转率低"；
- 与知识库主线互证：Cascade 的"SLO 预算会计"（B = S_TTFT − L）、"准入即承诺"哲学（08-13 工具链文档提炼）——MISA-T 是同一会计思想在 **KV 资源**上的落地；
- **不扭曲负载配比**：训练器规定的 RLVR/RLHF/agentic 混合比例是契约，调度不得为效率牺牲配比（这与 Cascade 的 SLO 是契约、TideRL 的 workload mixture 是契约同构）。

### 3.3 量化结果（🟢 一手）

| 实验 | 基线 | 结果 |
|:--|:--|:--|
| Rollout-only 消融（Step3.7）| sweep-tuned cache-aware vLLM Router | 吞吐 **+53.3%**，保持高前缀命中率 |
| Rollout-only 消融（Qwen3.6-35B-A3B）| 同上 | 吞吐 **+43.6%** |
| 匹配 50 迭代 Step3.7 | 同上 | 吞吐 +35.6%、**平均迭代时间 -22.8%**、负载配比接近训练器目标、任务分数相当 |

---

## 4. TideRL：就绪感知弹性调度（框架级重述）

> **单篇全文深度**：[08-13 RL 训练工具链三件套深度分析 §4](../../02_rd/02_project/01_superpod/2026-08-13-rl-training-toolchain-tiderl-misa-workflow-cards-deep-analysis.md)
> **arXiv**: [2608.10402](https://arxiv.org/abs/2608.10402)（cs.LG/cs.DC，2026-08-10 提交，08-11 公告）

### 4.1 框架

TideRL 是**就绪感知弹性 RL 系统**，三件套：

| 组件 | 全称 | 机制 |
|:--|:--|:--|
| **CTB** | Continuous Task Batching（连续任务批处理）| 保留有用 rollout 状态，不让暂停的任务在 barrier 处丢失进度 |
| **RA²P** | Resource-Aware Ref-Actor Pipelining（资源感知 Ref-Actor 流水）| 根据就绪积压（ready backlog）与到达间隔（arrival interval）在**解耦流式**（decoupled streaming）与**共置聚合**（colocated aggregation）之间选择 |
| **ERS** | Elastic Resource Scaling（弹性资源缩放）| 用同一组就绪信号在 rollout 与训练之间**移动 rank**（不重启、不改拓扑）|

### 4.2 原理（第一性原理展开）

**TideRL 的核心论点：RL training goodput（训练吞吐）比 GPU 占用率重要——GPU 等待和重复 prefill 重算是纯开销。**

- 传统异步 RL 的隐藏成本：任务暂停时，其已算的 rollout 状态若未保留则作废；恢复时上下文增长导致 prefill 重算；完成时间高度可变导致同步 barrier 空转；
- **readiness 信号**（RWT/TWT 类）统一三件事：CTB 决定批处理形状、RA²P 决定流水模式、ERS 决定资源分配——"**资源随就绪度而非占用率流动**"；
- 与知识库互证：SCOUT 的"同步点即观测点"哲学（同步屏障处交换签名定位故障）→ TideRL 把同步点从**故障诊断锚点**升级为**调度决策锚点**；
- 与 MARS 的对照：MARS 是"对未来的规划"（向前模拟），TideRL 是"对当下的反应"（就绪信号驱动）——**前者解决作业级不确定性，后者解决微秒/秒级运行不确定性**，两层级不冲突。

### 4.3 量化结果（🟢 一手）

| 指标 | 结果 |
|:--|:--|
| RL 训练 goodput（vs 同步基线）| 最高 **5.6×** |
| RL 训练 goodput（vs 异步基线）| **+33%**（文本+多模态 agentic 负载）|
| KV cache 命中率 | **1.58×** |
| 单步训练时间 | -44.3% |
| 总等待时间 | -77.6% |
| 任务性能 | 与基线相当 |

---

## 5. RoutePack：专家放置 × 注意力打包联合优化（首次全文深度）

> **arXiv**: [2608.12146](https://arxiv.org/abs/2608.12146)（cs.DC/cs.LG，2026-08-12 提交）| **作者**: Yibo Shen, Xudong Han, Xiaowei Zhu, Gen Li, Zhenxuan Pan（**Ant Group 蚂蚁集团**）| **模型**: Ling-3.0-Tiny / Ling-3.0-Flash（KDA+MLA 混合线性注意力栈）

### 5.1 问题定义：MoE RL 的双源 straggler 耦合

MoE 模型训练步暴露**两个独立的负载不均衡来源**：

1. **Dense attention 不均衡**：在 DP（数据并行）副本内独立执行，其尾部取决于每个 microbatch 打包序列的**长度与组成**——注意：等 token 数 ≠ 等工作量（见下）；
2. **Sparse expert 不均衡**：经 EP（专家并行）分发，dispatch/grouped GEMM/combine 的节奏由**收到最多路由 token 的物理 rank** 决定。

**耦合本质**：把样本 Sᵢ 从 cell A 移到 cell B，会同时改变它的 token 长度、二次注意力贡献、以及每一 MoE 层的路由向量——"只按长度移动"可能在改善 dense 尾部的同时，把激活同一物理 rank 的样本聚到一起；"只按专家代价打包"可能消除路由峰值却制造注意力离群。**耦合是结构性的，不是某个启发式的缺陷。**

### 5.2 关键信息杠杆：routing replay 把布局变成控制

Rollout 与训练处理同一 token 序列 → routing replay 在训练步调度**之前**精确暴露每个样本的：

```
Input: {(t_i, A_i) : i = 1..N},  A_i = [a_i,l,e]  (routing counts of
       sample i, MoE layer l, logical expert e)
```

这个信息把"数据布局"从 routing-blind 的预处理（FFD 长度打包）升级为**负载均衡控制**：系统可以协调"专家住在哪里"与"哪些样本一起执行"。

### 5.3 框架：层级规划器（hierarchical planner）

RoutePack **不做全局联合优化**，而是分层决策（每层在前一层结果上优化），这是刻意的架构选择：

```
+------------------------------------------------------------------+
| Stage 0: optimizer-step batch sealed (before training)           |
+------------------------------------------------------------------+
| Stage 1: layer-wise expert placement (LPT)                       |
|   - each MoE layer independent: aggregate demand L_l,e = sum a   |
|   - LPT greedy: experts desc by demand -> least-loaded rank      |
|   - lowers optimizer-window expert skew that packing cannot fix  |
+------------------------------------------------------------------+
| Stage 2: fix row count (R* = min feasible rows)                  |
|   - capacity efficiency before load balance (requirement 1)      |
+------------------------------------------------------------------+
| Stage 3: EDP-shard-aware packing (population annealing)          |
|   - objective: joint attention(DP cell) x expert(EP rank) cost   |
|   - lexicographic: (slowest shard, total work, worst row tail)   |
|   - solver: diverse seeds + parallel fixed-temp anneal + resample|
+------------------------------------------------------------------+
| Stage 4: state-consistent materialization (commit at step edge)  |
|   - expert state co-materialized, dispatcher inverse map, DeepEP |
+------------------------------------------------------------------+
```

### 5.4 原理深度：四个关键机制

**(a) Packing 不变量 → 为什么 placement 必须先行（式 3-4）**

固定放置 πₗ 后，样本重排只改变专家需求"何时被暴露"，不改变 optimizer 窗口内分配给物理 rank p 的总需求：

```
L_agg_{l,p}(pi_l) = sum_i sum_{e: owner(pi_l(e))=p} a_{i,l,e}   (window-level aggregate invariant)

sum_r sum_g max_p W_{r,g,l,p}(x; pi_l) >= max_p L_agg_{l,p}(pi_l)   (packing load lower bound)
```
（注释：第一式 = 窗口级聚合不变量；第二式 = 打包的负载下界）

→ 窗口级路由分布偏斜时，**必须先改专家物理映射，打包才能越过这个下界**。反之，placement 只控制聚合下界，不保证行内均衡（路由向量相关的样本可能被包进同一行）——**两个控制互不替代，必须协调**（图 3 给出了 12-vs-4 → 8-vs-8 → 4-vs-4 的级联改善示例）。

**(b) 注意力工作的两项代理（式 2/11/12）**

```
F_A(B) = alpha_A * sum(t_i) + beta_A * sum(t_i^2)
```
（注释：α = token 线性项，β = token 对二次项）

| 注意力类型 | α | β | 物理含义 |
|:--|:--:|:--:|:--|
| KDA / Gated DeltaNet（线性注意力）| >0 | **0** | 只有投影/循环项 |
| MLA / Gated Attention（全注意力）| >0 | **>0** | 含 token 对交互 |
| CSA / HCA（压缩稀疏注意力）| 校准 | 降阶 β | 固定窗归 α，长度比例压缩序列贡献降阶 β |

**关键洞察**：等总 token 固定第一个统计量，但**不固定第二个**——这就是"固定 token 打包仍可能保留长上下文 DP straggler"的原因（与知识库 KV 带宽/延迟主线、Libra 的注意力工作模型互证）。Ling-3.0 用 KDA（β=0）与 MLA（β>0）混合栈，两类 stage 分开取 max 再累加。

**(c) 正确的作用域：DP cell vs EDP shard（设计需求 3）**

- 注意力代价按 **DP cell**（每个 DP slot 的 microbatch）独立评估；
- 专家负载只在**同一 EDP shard**（投影到同一物理 EP communicator 的 DP slot 集合）内聚合；
- **跨不相关 communicator 的 rank 一起均衡，是在优化一个没有集体执行的数量**——物理 rank 抽象（UltraEP 同构）：先按 rank 汇总本地专家负载，再取 shard 内最大 rank 负载，而非单独均衡 rank 内专家。

**(d) 字典序目标：容量效率 > 负载均衡（式 15）**

```
Score(x; pi) = ( max_g U_g,  sum_g U_g,  max_{r,g} J_{r,g} )   lexicographic min
```
（注释：①最慢 EDP shard ②总投影工作 ③最差行尾（决胜），按字典序）

①控制整个 optimizer step 窗口的最慢 shard（U_g = 累积行代价）——因为独立 EDP shard 跨行累积速率不同；②打破平局；③最终决胜。**先固定 R⋆ 再优化布局**，防止"通过增加 microbatch 降低峰值"的假收益（增加总工作与 step 延迟）。

### 5.5 求解器：多样种子 + 并行 population annealing

固定 R⋆/π 后布局问题仍高度非凸，RoutePack 用：

1. **多样可行种子**：WindowShuffle（扰动长度降序）、RandomizedBestFit（token 占用降序采样）、EDPAwarePair（按路由 token 峰值配对 cell 到空槽，插入键 = 逐层 EDP rank 峰值增量）；
2. **Population annealing**：P_pop 条**独立固定温度链**并行跑（映射到 host CPU worker），逐级降温，**系统性重采样**（Boltzmann，只用终态）把并行预算导向更强 basin；trajectory-best 单调归档提供最终验证计划（非回归保证）；
3. **精确字典序评分**做最终选择——退火能量只是搜索代理，不替代精确赢家准则；
4. **canonicalization**：消除 cell 内样本顺序/行顺序/EDP shard 内可交换 DP slot 等无关置换，用 Sliced-Wasserstein sketch 度量计划间距离（quality 门控先于 diversity 选择）。

### 5.6 状态一致性物化（工程关键）

专家重放置最危险的是破坏训练语义。RoutePack 的契约：

- **训练步边界提交**：专家 FC 参数复制进目标 slot 的既有张量（不替换参数对象、不重建梯度缓冲描述符）；分布式优化器先跨 EP rank 传输源 range，再在目标 EDP 组内重分区，写入既有目标 range——**EDP gbuf 分区与 slot 所有权保持固定**；
- **逻辑路由不变**：路由器继续输出逻辑序 top-k 分数，仅 dispatcher 应用逆列置换把逻辑专家 e 送到物理 slot πₗ(e)；布尔路由图无需梯度，路由概率索引保持可微并把梯度送回原逻辑列；
- **保留 DeepEP 后端**：只改变呈现给 dispatcher 的物理专家索引，不改 collective API/communicator 拓扑；重排导致浮点加法非结合 → 允许 ULP 尺度漂移（视为数值重排非语义失配），要求逻辑输出与梯度在 dtype 容差内一致；
- **并行性正交**：TP/SP/CP/DP/EP/EDP/PP 拓扑、1F1B 流水、激活重算、混合精度（专家级 FP8/FP4 元数据随专家状态 co-materialize）全部不变——**step-boundary 契约 = 不改变张量形状、communicator 成员、参数对象或调度依赖**。

### 5.7 量化结果（🟢 一手）

| 模型 | 专家重路由 | +路由感知打包 | **总计** |
|:--|:--:|:--:|:--:|
| Ling-3.0-Tiny | +3.80% | +4.86% | **+8.85%** |
| Ling-3.0-Flash | +10.50% | +3.98% | **+14.89%** |

（trainer-measured token throughput；在线 trace 显示 EP 峰值累积、最差行峰值、联合瓶颈一致下降。另有 CPU 打包不扩展训练准入关键路径的充分条件推导——🟡 理论结果未实测。）

### 5.8 与相关工作谱系（RoutePack 的位置）

| 系统 | 专家控制 | 数据控制 | 缺口 |
|:--|:--|:--|:--|
| AReaL/slime/veRL/OpenRLHF | 无 | 长度封顶打包 | 不看路由向量 |
| Libra | 无 | 注意力 tile 调度 | 不优化稀疏专家 |
| ReLibra（最接近）| 批量重排+节点内复制 | 源 GPU 分配+token 切分 | sample 重排是通信局部性细化，不构造容量高效执行行 |
| UltraEP/MoonEP/FineMoE/ForeMoE | 冗余专家/重路由 | token 级重分配 | microbatch 级变化，需复制协议 |
| **RoutePack** | **逐层 LPT 放置** | **整序列打包进同步行** | 填补：routing replay 协调 placement × packing |

---

## 6. 三线耦合关系：为什么必须分开解、又如何合起来用

### 6.1 三个瓶颈的独立性（为何不能一个系统全解）

| 瓶颈 | 决策频率 | 资源域 | 信息需求 |
|:--|:--|:--|:--|
| KV 竞争（MISA-T）| session 级（秒~分钟）| 显存/KV cache | session 驻留预估 |
| 就绪调度（TideRL）| 任务级（毫秒~秒）| GPU 时间 | 就绪信号 |
| 布局优化（RoutePack）| step 级（分钟）| DP×EP 空间 | routing replay |

三者的**时间尺度、资源域、信息源均不同**——合并成一个全局优化器会引入难以求解的耦合（这也是 RoutePack 刻意选层级规划而非全局联合优化的原因）。同日独立出现 = 分工的正确性被自然选择验证。

### 6.2 组合视角：三线如何形成闭环

```
 MISA-T (admission) controls which sessions enter the serving pool
   |   determines KV hit rate and prefill load
   v
 TideRL (scheduling) controls rollout <-> training resource split
   |   determines whether ready tasks execute in time, state kept
   v
 RoutePack (layout) controls DP x EP balance inside each training step
   |   determines actual throughput of every step
   v
 Combined: RL iteration time (MISA-T -22.8% / TideRL -44.3% per-step
           / RoutePack +8.85~14.89%)
```

**组合收益为 🟡 估算**（用户原始框架）：若三线正交，理论乘性上限约 1.53×1.44×1.15 ≈ **2.5×**；但存在交互冲突（TideRL 的弹性移 rank 会改变 RoutePack 的 EDP shard 拓扑；MISA-T 的准入会改变 TideRL 看到的就绪分布）——现实组合落在 1.5~2.0× 区间是更诚实的估计。**此值未经任何系统实测，仅为判断**。

### 6.3 与知识库四类冗余 MECE 的映射

| 冗余类型 | 对应战线 | 消除手段 |
|:--|:--|:--|
| 时间冗余（等待）| TideRL | 就绪感知批处理 + 弹性缩放 |
| 空间冗余（KV 占用）| MISA-T | 驻留记账 + 容量分配 |
| 计算冗余（重算/不均衡）| RoutePack | 联合布局优化 |
| IO 冗余 | （推理侧记忆线）| prefix caching 等 |

→ 三篇论文是"四类冗余 MECE"在 **RL 训练侧**的逐一落地，此前该框架主要应用于推理侧。

---

## 7. goodput 记忆线：Cascade→MARS→TideRL 的范式演进

### 7.1 记忆线全景（知识库既有 + 本次扩展）

| 系统 | 日期 | 领域 | 核心思想 | 度量 |
|:--|:--|:--|:--|:--|
| Cascade | 08-11 | 推理调度 | SLO 预算会计：B = S_TTFT − L，JFI 六分位 | 预算不超支 |
| MARS | 08-11 | HPC 作业调度 | MCTS 前瞻：世界模型+树搜索替代启发式 | 尾等待/利用率 |
| TideRL | 08-11 | RL 训练调度 | 就绪感知弹性：CTB/RA²P/ERS | **goodput** |
| MISA-T | 08-11 | RL rollout 服务 | 路由层准入 + KV 驻留记账 | rollout 吞吐/迭代时间 |
| RoutePack | 08-12 | RL 训练布局 | 专家放置×注意力打包联合优化 | trainer token 吞吐 |

### 7.2 范式演进的三个台阶

1. **从占用率到 goodput**（TideRL 最明确）："GPU 忙"不等于"在产出"——等待与重算是纯开销；MISA-T 用 rollout 吞吐/迭代时间而非请求吞吐评估；RoutePack 用 trainer-measured 吞吐（训练器测的，非系统自报）——**三篇全部拒绝用 GPU 占用率当 KPI**；
2. **从反应到规划**：MARS 向前模拟（作业级）、TideRL 就绪信号（运行级）、RoutePack routing replay（step 级）——**不确定性越高、可知信息越多的环节，规划收益越大**；
3. **从单域到耦合域**：Cascade/MARS 各自单域，本次三线齐发首次把**服务域（KV）× 时间域（就绪）× 空间域（布局）**同时摆上桌面——调度问题从"一个域内的效率"升维为"跨域耦合的治理"。

### 7.3 一个反直觉的观察

**收益越大的系统，工程改动越小**：MISA-T 是纯准入策略（路由层，vLLM Router 之上加一层）；TideRL 改批处理/流水/缩放但不动模型与拓扑；RoutePack 是训练前规划 + step-boundary 物化（不改变任何内核）。**三篇都没有动 GPU kernel、通信库或模型结构**——再次印证"调度是软件栈中最便宜的杠杆"（与 Cascade 的"预算会计优于硬件升级"同构）。

---

## 8. 产业信号与可证伪预判

### 8.1 信号解读

- **RL post-training 进入"调度红利期"**：当模型能力边际收益递减、硬件单价高企时，平台侧把效率杠杆从"换卡"转向"调度"——这与知识库"调度范式→goodput"记忆线、Gartner 2026 AI IaaS +96%（推理支出首超训练）互证；
- **蚂蚁用自家 Ling 模型发 RoutePack**：国内大厂已把 MoE RL 调度当作内部效率战场（Ling-3.0 公开了 KDA+MLA 混合栈，说明线性注意力架构已在生产落地并催生配套调度研究）——"国产模型 × 国产调度系统"的组合正在成形；
- **routing replay 成为标准信息源**：R3→ReLibra→RoutePack 三代复用同一机制，说明"rollout 轨迹 = 免费的先验"已成为 RL 系统设计的公共资产；
- 与知识库 08-13 观察互证："Agentic/RL 负载成为调度研究主战场"——本次三线齐发把这个判断从"观察"升级为"范式确认"。

### 8.2 可证伪预判（🟡 判断，非论文断言）

- **P1**：2026H2-2027 将出现"准入 × 弹性 × 布局"三合一的 RL 调度系统（或三家分别的产品化），其组合收益若公开会落在 1.5~2.0×（§6.2 估算区间）；
- **P2**：RoutePack 式 routing-replay 布局优化将成为主流 RL 训练框架（veRL/OpenRLHF/NeMo RL 线）的标配组件（12 个月内），因为其信息成本为零、收益确定；
- **P3**：KV 驻留记账（MISA-T 式）将进入推理 serving 的显存管理规范（vLLM/SGLang 路线图），与 HiSparse 合入 SGLang 的"KV 分层"主线汇合。

---

## 9. 数据缺口与诚实标注

| 项 | 状态 | 说明 |
|:--|:--|:--|
| MISA-T 内部机制细节 | 🟡 | 仅摘要级（session 准入/容量分配/驻留记账的具体算法与阈值未公开）；全文深度见 08-13 文档（其基于 HTML 全文）|
| TideRL 内部机制细节 | 🟡 | 同上；全文深度见 08-13 文档 |
| RoutePack 组合收益 | 🟢 | 论文一手（+8.85%/+14.89%）|
| 三线组合收益 2.5×/1.5-2.0× | 🔴 | **本文估算，非任何系统实测**；且存在交互冲突（弹性移 rank vs EDP 拓扑、准入 vs 就绪分布）|
| 三篇未互引 | 🟢 | 作者/机构互不重叠，同日独立（TideRL 提交 08-10 公告 08-11，MISA-T 提交 08-11，RoutePack 提交 08-12）|
| RoutePack 实验规模 | 🟡 | 仅 Ling-3.0-Tiny/Flash 两个小模型；未验证到 70B+ 级生产规模 |
| RoutePack CPU 打包充分条件 | 🟡 | 理论推导，未实测（论文自述）|

---

## 参考来源

1. **TideRL**: Yanyu Ren et al., "TideRL: Boosting Agentic RL Goodput with Readiness-Aware Scheduling", arXiv:2608.10402, 2026-08-10 提交. https://arxiv.org/abs/2608.10402
2. **MISA-T**: Zetao Hong et al., "Scheduling Mixed RL Rollouts Beyond Prefix Locality", arXiv:2608.11152, 2026-08-11 提交. https://arxiv.org/abs/2608.11152
3. **RoutePack**: Yibo Shen et al. (Ant Group), "RoutePack: Expert Placement and Attention-Aware Data Packing for MoE Reinforcement Learning", arXiv:2608.12146, 2026-08-12 提交. https://arxiv.org/abs/2608.12146 （HTML 全文精读）
4. [08-13 RL 训练工具链三件套深度分析](../../02_rd/02_project/01_superpod/2026-08-13-rl-training-toolchain-tiderl-misa-workflow-cards-deep-analysis.md)（知识库，TideRL/MISA-T 全文深度）
5. [Cascade SLO 预算调度深度分析](2026-08-11-cascade-slo-latency-budget-scheduling-deep-analysis.md)（知识库）
6. [MARS MCTS 自适应调度器深度分析](../../02_rd/01_product/01_software/02-distributed-os/2026-08-11-mars-mcts-adaptive-scheduler-deep-analysis.md)（知识库）
7. [LLM 推理四类冗余消除深度分析](2026-08-05-llm-inference-redundancy-elimination-deep-analysis.md)（知识库）

---

## Changelog

- **2026-08-14 v1.0**: 初稿。三线齐发（MISA-T/TideRL/RoutePack）× 耦合问题框架；RoutePack 全文深度（层级规划/两项注意力代理/字典序目标/population annealing/状态一致物化）；goodput 记忆线扩展；三线组合收益 🔴 估算标注。
