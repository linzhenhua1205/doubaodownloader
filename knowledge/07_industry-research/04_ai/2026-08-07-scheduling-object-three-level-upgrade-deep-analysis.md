# 🎛️ 调度对象三级升级技术深潜：请求 → GPU 共享态 · 专家副本 · 前缀 KV（平台从排队器到结构感知资源编排器）

> **概要**: 2026-08 三篇调度论文（HorizonServe/TAOT/PrefixPlace）揭示同一演进：调度对象从「请求」逐级细化为 GPU 共享态、专家副本、前缀 KV，平台从排队器升级为结构感知资源编排器。
>
> **统一主线**：2026-08 三篇调度论文（HorizonServe / TAOT / PrefixPlace）展示同一个演进方向——**调度对象从「请求」这个原子单元，逐级细化为请求内部的「GPU 共享态」、模型内部的「专家副本」、数据内部的「前缀 KV」**。平台的角色随之从「排队器」（何时执行）进化为「**结构感知资源编排器**」（在哪里执行、占多少资源、与谁共享）。三篇分别回答编排器的三个维度：**时间×空间联合**（HorizonServe 单 GPU 共享调度）、**拓扑×负载联合**（TAOT 多节点专家放置）、**计算×传输联合**（PrefixPlace 异构 KV 放置）。
>
> **关键词**: 调度对象 · 结构感知编排 · GPU 共享 · MoE 专家放置 · 最优传输 · 前缀 KV 放置 · 异构成本 · 排队器
>
> **数据源分级**: ✅ 3 篇 arXiv 官方 HTML 全文一手抓取：
> - [HorizonServe](https://arxiv.org/abs/2608.01785)（2608.01785, cs.DC, 单 GPU omni-model serving）
> - [TAOT](https://arxiv.org/abs/2608.03676)（2608.03676, cs.DC, 腾讯, 动态专家副本放置）
> - [PrefixPlace](https://arxiv.org/abs/2608.01655)（2608.01655, cs.DC, Wang & Buyya, 前缀 KV 放置）

---

## 📑 目录

- [〇、结论概要](#〇结论概要)
- [一、统一主线：调度对象三级升级](#一统一主线调度对象三级升级)
- [二、HorizonServe：请求 → GPU 共享态](#二horizonserve请求--gpu-共享态)
- [三、TAOT：专家副本 → 拓扑感知放置](#三taot专家副本--拓扑感知放置)
- [四、PrefixPlace：前缀 KV → 异构放置](#四prefixplace前缀-kv--异构放置)
- [五、统一框架：从排队器到结构感知资源编排器](#五统一框架从排队器到结构感知资源编排器)
- [六、与知识库理论的闭环](#六与知识库理论的闭环)
- [七、批判性审视](#七批判性审视)
- [八、可证伪预测 P1-P5](#八可证伪预测p1-p5)
- [九、本系统启示](#九本系统启示)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 〇、结论概要

**调度是 AI 基础设施的「隐藏操作系统」，而调度对象的粒度定义平台的能力上限。** 传统 serving 平台把「请求」当作不可分割的调度原子——本质是**排队器**（决定请求何时执行）。2026-08 三篇论文把调度对象逐级向下钻取：

| # | 论文 | 调度对象 | 感知维度 | 平台角色升级 | 关键量化 |
|:-:|:--|:--|:--|:--|:--|
| 1 | **HorizonServe** | 请求 → **GPU 共享态**（共享阶段 SM/带宽配额） | 时间 × 空间（SLO × GPU 共享） | 排队器 → **共享态协调器** | SLO 达标率 **+4.9×/7.0×**；首响应延迟 **-38.4~63.7%** |
| 2 | **TAOT**（腾讯） | 请求 → **专家副本**（MoE 热专家跨 rank 放置） | 负载 × 拓扑（通信成本矩阵） | 均衡器 → **拓扑感知放置器** | 训练加速 **+42.82%**；通信成本 **-74%** |
| 3 | **PrefixPlace** | 请求 → **前缀 KV**（前缀树上的 KV 块放置） | 计算 × 传输（异构 GPU 成本画像） | 缓存器 → **可证明近似编排器** | **99.84%** of optimum；RAG 节省 **+40.3%** vs vLLM-APC |

**一句话**：三篇合起来定义了「结构感知资源编排器」的三个剖面——**调度对象从原子请求细化为「请求内结构」（共享态）、「模型内结构」（专家）、「数据内结构」（前缀树）**，平台竞争力从「排得多快」转向「排得多懂结构」。

---

## 一、统一主线：调度对象三级升级

```
    Scheduling Object Granularity Evolution (2026-08, 3 papers)
  +-----------------------------------------------------------+
  |  Legacy: request = atomic unit                              |
  |  platform = queue manager (when to run)                     |
  |  +-------------------------------------------------------+ |
  |  | L1: request -> GPU shared state  (HorizonServe)        | |
  |  |   sees: shared-stage SM quota x bandwidth x SLO        | |
  |  |   role: shared-state coordinator (time x space)        | |
  |  +-------------------------------------------------------+ |
  |  | L2: request -> expert replica  (TAOT)                  | |
  |  |   sees: MoE expert load x cross-node topology cost     | |
  |  |   role: topology-aware placer (load x topology)        | |
  |  +-------------------------------------------------------+ |
  |  | L3: request -> prefix KV  (PrefixPlace)                | |
  |  |   sees: prefix tree x heterogeneous compute/transfer   | |
  |  |   role: provable approx orchestrator (comp x transfer) | |
  |  +-------------------------------------------------------+ |
  |  End state: structure-aware resource orchestrator          |
  |  (where to run x how much x with whom to share)            |
  +-----------------------------------------------------------+
```

- **三个维度的共同语法**：调度对象从「请求」细化到「请求内部的结构单元」——stage（阶段）、expert（专家）、prefix（前缀块）——每一个都携带独立的成本/收益特征，需要独立决策；
- **从时间到空间的范式跃迁**：排队器只回答「何时」，编排器必须回答「**在哪里**（拓扑/worker）、**占多少**（SM/带宽/内存预算）、**与谁共享**（GPU 共享/副本复用/KV 复用）」；
- **结构 → 可优化性**：一旦调度对象结构化（前缀树/通信矩阵/成本画像），调度问题就从「队列策略」变成「组合优化问题」——TAOT 用最优传输、PrefixPlace 用设施选址近似，都有可证明的保证。

---

## 二、HorizonServe：请求 → GPU 共享态

> ✅ 一手全文（2608.01785, cs.DC）

### 2.1 问题背景：单 GPU omni-model serving

**Omni-model（全模态模型）serving** = 单 GPU 上同时服务文本/音频/图像等多模态请求。关键特征：**异构请求路径共享同一个 GPU**：

- 不同模态请求走**不同执行路径**（text-generation 短路径 vs audio/video 长路径）；
- 共享**中间阶段（shared stage）**——多模态 token 处理共用 GPU 计算与内存带宽；
- SLO 高度异构（首响应延迟目标相差数量级）。

### 2.2 三大动机问题

| 问题 | 现象 | 量化 |
|:--|:--|:--|
| **SLO 异质性** | 各请求类型单独运行时 p95 首响应延迟已差数量级 | Figure 2：orders-of-magnitude gaps |
| **Goodput Collapse（好吞吐塌缩）** | 长路径流量增加时，**短路径请求 SLO 达标率先崩**——同负载下 SLO-satisfied goodput 下降 | 长路径占比 0%→60%，短路径达标率骤降 |
| **跨阶段带宽争用** | 下游生成器激活后，共享阶段内存带宽利用率飙升，短文本 TTFT 尖峰 | 带宽利用率 **76%→93%**；TTFT 尖峰 **90-200ms**（基线 2ms，**+118% 退化**） |

> 📌 核心洞察：**调度对象不能是「请求」**——因为一个请求在共享阶段的延迟由**同时运行的其它路径的带宽消耗**决定。必须先拆出「共享态」作为调度单元。

### 2.3 技术架构：HorizonServe 三组件

```
  +----------------------------------------------------------+
  |  离线预处理          在线调度循环                         |
  |  +----------+      +--------------------------------+    |
  |  | SLO 表    |      | ① 共享阶段路径轮转             |    |
  |  | (每类孤立 |      |    + 长路径准入上限             |    |
  |  | 测量p95)  |      | ② 带宽引导 SM 节流             |    |
  |  +----------+      |    (SM配额=带宽控制旋钮)         |    |
  |                    | ③ 近截止请求绕过路径过滤          |    |
  |                    +--------------------------------+    |
  +----------------------------------------------------------+
```

1. **Offline Preprocessing + Request Signals**：离线测每类请求孤立 p95 首响应延迟生成 SLO 表；在线跟踪进度信号——**近截止请求可绕过普通路径过滤**（紧急优先）；
2. **Shared-Stage Path Rotation（共享阶段路径轮转）**：长路径准入设上限，防止长路径突发**独占共享阶段槽位**、限制未来下游激活——旋转让短路径在共享阶段获得确定性份额；
3. **Bandwidth-Guided SM Throttling（带宽引导 SM 节流）**：把 SM（Streaming Multiprocessor）分配当作**带宽控制旋钮**——选择有界的共享阶段上限，保护紧 SLO 短路径请求而不扩大共享阶段（带宽已近饱和 93% 时，多给 SM 反而加剧争用）。

### 2.4 底层原理

- **好吞吐塌缩的根因**：异构路径共享 GPU 时，下游生成器消耗内存带宽 → 共享阶段变慢 → 短路径（紧 SLO）先受冲击——**延迟不是单个请求的属性，而是 GPU 共享态下的系统属性**；
- **SM 即带宽阀门**：GPU 内存带宽利用率逼近峰值时，计算资源（SM）与带宽资源解耦——调度器必须把 SM 分配当作带宽控制手段而非单纯计算分配；
- **联合控制时间×空间**：admission（何时进）+ GPU allocation（占多少 SM）= 单一控制环路，这是与既有 serving 系统（只优化 token 进度或输入侧处理）的本质区别。

### 2.5 实验量化

| 指标 | 结果 | 基线 |
|:--|:--|:--|
| SLO attainment（到达率扫描） | **最高 +4.9×** | 最优基线 |
| SLO attainment（下游重流量） | **最高 +7.0×** | 最优基线 |
| 每类 p95 首响应延迟 | **-38.4%~-63.7%**（Qwen2.5-Omni -57.1% / MiMo-Audio -42.1% / BAGEL -38.4%，RTX 6000 Ada） | 各类最优基线 |
| 具体案例（到达率 0.45） | **71.9%** SLO attainment | 最优基线 14.6% |
| 共享阶段 TPOT | 保留（不损害 token 流式） | — |
| 端到端吞吐开销 | **<1%** | — |

- **Workloads**：Qwen2.5-Omni / MiMo-Audio / BAGEL；**平台**：RTX 6000 Ada / RTX PRO 6000。

---

## 三、TAOT：专家副本 → 拓扑感知放置

> ✅ 一手全文（2608.03676, cs.DC, 腾讯：Lingyun Zhang / Henghua Zhang / Dou Shen 等）

### 3.1 问题背景：MoE 训练的负载失衡与副本代价

MoE 是 LLM 扩展的关键架构，但**动态路由导致专家并行（EP）训练严重负载失衡**。现有动态副本方法把热专家复制到空闲 rank 共享计算，但**只优化负载平衡、忽略跨节点拓扑的权重移动成本**——结果跨节点通信可能超过均衡收益、反而抬高训练成本。

### 3.2 形式化：放置目标 = 残差失衡 + 加权副本通信

```
min_{z in {0,1}}  rho(z) [residual imbalance] + mu * sum_{e,r} z_{er} * W_re       (1)
```

- `rho(z)`：负载失衡率 = (max − mean)/mean；
- `z_{er}`：专家 e 是否在 rank r 放副本；
- `W_re`：跨拓扑的加权副本通信成本——**拓扑敏感**（intra-node 便宜、inter-node 贵）；
- `mu`：平衡收益 vs 通信代价的权衡系数。

### 3.3 技术架构：三阶段拓扑感知最优传输（TAOT）

```
  Phase 1                     Phase 2                    Phase 3
  +----------------------+   +----------------------+   +------------------+
  | Sinkhorn-Knopp        |   | Column-Priority      |   | Lagrangian       |
  | 拓扑感知流规划         | → | 迭代匹配             | → | Auction 令牌分配 |
  | (rank-level OT)       |   | (integer replica)     |   | (token exact)    |
  | comm-cost matrix      |   | cold rank per-round    |   |                  |
  +----------------------+   +----------------------+   +------------------+
  system: overlap guest-weight transfer with home-expert compute
```

1. **Phase 1：Sinkhorn-Knopp 拓扑感知流规划**——把「热 rank 过载 + 冷 rank 空闲」建模为**带通信成本矩阵的平衡最优传输（OT）问题**，Sinkhorn-Knopp 迭代求解（熵正则化），产出 rank 级流提示（flow hints）——**全局参考**，避免局部贪心导致不合理通信路径；
2. **Phase 2：Column-Priority 迭代匹配**——按列（冷 rank）优先迭代，把流提示转成**整数副本分配**；关键设计：**冷 rank 每轮独立竞争机会**（若按行=热专家优先，热专家会贪心占满所有空槽，残差失衡 7-10%；列优先降到 1-2%）；
3. **Phase 3：Lagrangian Auction 令牌分配**——token 级用 Lagrange auction 完成各 rank 到空槽的精确分配；
4. **系统级重叠**：guest-weight 传输与 home-expert 计算重叠，隐藏通信开销。

### 3.4 底层原理

- **最优传输（Optimal Transport）正是「负载再分配」的数学语言**：热专家的过载流量（mass）向冷 rank 运输（transport），成本矩阵 = 通信拓扑——Sinkhorn 求解的是「**最少通信代价下最均衡的流量分配**」；
- **平衡 ≠ 最优**：1pp 失衡差异 ≈ 7% 通信成本差异——计算尾部代价可被通信节省抵消；TAOT 的策略是**用可忽略的残差失衡换取显著的通信下降**；
- **列优先（column-first）的博弈论直觉**：把稀缺资源（空槽）的分配权优先给「缺机会的一方」（冷 rank），避免强势方（热专家）垄断——类似拍卖里的**防垄断机制**；
- **分层决策**：rank 级（宏观流量）→ 副本级（整数分配）→ token 级（精确指派）——**先粗后细**，各层用最合适的算法（OT / 匹配 / 拍卖）。

### 3.5 实验量化

| 指标 | 结果 | 对比 |
|:--|:--|:--|
| 端到端训练加速（Qwen3-30B-A3B） | **+42.82%** | vs Megatron-LM |
| 加权专家通信成本 | **最低**（最高 **-74%**） | vs LPLB/ECHO/LLE |
| EP 扩展（EP4→EP16） | 加速 **最高 1.79×** | — |
| 初始失衡 30%→90% | 加速 **1.21×→1.75×**（强适应高失衡） | — |
| EP=32 时 | **平衡质量与通信成本双领先** | vs 全部基线 |
| 在线规划开销 | **<1%** forward time（不随失衡线性增长） | — |
| 消融：列优先 | 残差失衡 **7-10% → 1-2%** | 行优先对照 |
| 消融：Phase 1 流提示 | 失衡 2.00%→1.48% + 通信成本下降 | 无全局参考对照 |

---

## 四、PrefixPlace：前缀 KV → 异构放置

> ✅ 一手全文（2608.01655, cs.DC, Zhiyu Wang & Rajkumar Buyya）

### 4.1 问题背景：前缀 KV 复用的本地 miss 代价

前缀 KV 复用避免重复 prefill（系统提示/检索文档/few-shot/对话历史共享时），但**本地 miss 需要重算（compute）或远程取（transfer）**——而计算与传输成本在**异构 GPU（T4/L4/A100）间差异巨大**，现有 APC（Automatic Prefix Caching）不做异构感知的跨 worker 放置。

### 4.2 形式化：前缀 KV 作为放置对象

- **前缀树（prefix tree）**：共享前缀的 KV 块构成树结构；
- **prefix-complete 可行性**：保留一个 chunk 必须同时保留其前缀路径上的所有可缓存祖先（树结构约束）；
- **成本模型**：worker m 上块 b 的物化成本 `Λ_m(b)`；传输成本 `w_m(b)`；重算成本 `f_m(b)`；
- **节省分解**：以全重算为基线，本地价值 `a_m(b) = Λ_m(b)·min{w_m(b), f_m(b)}`——**远程副本只对「传输成本 < 重算成本」的请求创造价值**；
- **源依赖传输成本**：传输代价取决于 KV 从哪个源 worker 来（source-dependent），不止 requester 侧摘要。

### 4.3 技术架构：epoch 级规划器

```
  input                          planner                        output
  +--------------+     +----------------------------+   +------------+
  | prefix tree  |     | single-worker oracle       |   | per-worker |
  | demand matrix| --> |   (O(nk) exact)            |-->| resident   |
  | mem budget   |     | WorkerGreedy (1/2-approx)  |   | prefix     |
  | profiled cost|     | + coordinate refinement    |   | target     |
  +--------------+     | + order-diverse starts     |   +------------+
                       | + comparator safeguards    |
                       +----------------------------+
```

- **单 worker oracle**：给定 budget，最优子集在 **O(nk)** 时间精确求解（n=块数，k=容量），产生**共享根树 oracle**——每个 worker 的精确边际值对树节点可加；
- **联合放置（Joint）**：**强 NP-hard**（单调设施选址目标）→ **WorkerGreedy**：固定序 **1/2-approximation**（对两个目标均成立）；
- **PrefixPlace = guaranteed 初始化 + 坐标精化 + order-diverse starts**：在保持 1/2 界的同时逼近最优——坐标精化 + 顺序多样化 + 比较器保护（safeguards）。

### 4.4 底层原理

- **前缀 KV 放置 = 设施选址问题（facility location）**：worker 是设施、KV 块是需求点、物化成本是开设成本、传输/重算是服务成本——经典组合优化问题，因此有可证明的近似保证；
- **树结构带来可加性**：prefix-complete 约束 + 共享根树 → 边际价值对树节点可加 → **单 worker 问题可精确解**（O(nk)），联合问题才需近似；
- **异构成本是核心变量**：profiled 数据（T4/L4/A100 × Qwen2.5 系列，CV ≤0.51% 稳定）证明**worker 特定决策必要**——统一策略在混合 GPU 集群上损失显著；
- **epoch 级规划**：调度不是逐请求的微观决策，而是**周期性（epoch）重规划**——需求漂移时可快速重算（50,000 节点 12.3s）。

### 4.5 实验量化

| 指标 | 结果 | 对比 |
|:--|:--|:--|
| 最优性（432 requester-side 实例，精确 MILP） | **平均 99.84%**（从不低于 98.02%） | exact optimum |
| 最优性（45 source-dependent 实例） | **平均 99.62%**（不低于 97.90%） | exact optimum |
| RAG replay 物化成本节省 | **+40.3%**（WikiQA +40.4%） | vs vLLM-APC |
| RAG replay 物化成本节省 | **+6.3%**（WikiQA +5.3%） | vs 最优离线基线 |
| 混合 GPU（T4/L4/A100）有效 KV 好吞吐扫描 | 增益 **1.1%→10.0%**（峰值 8.9% @3Gb/s） | vs 最强基线 |
| 内存预算 5%/10%/20%/30% | 平均增益 **7.34%/6.24%/3.10%/1.24%** | — |
| 重规划（50,000 节点 16 worker） | **12.3s** 单 CPU | 及时重规划 |
| 需求漂移（100% 路由转移） | 中位增益 **23.74%**，**251 请求**内回本 | — |

---

## 五、统一框架：从排队器到结构感知资源编排器

```
            Scheduling Paradigm Evolution (queue -> orchestrator)
  +--------------------------------------------------------------+
  |                                                              |
  |  Legacy serving: scheduling object = request (atomic)        |
  |    +----------+  when to run? -> queue manager               |
  |    | request  |     (FCFS / priority)                        |
  |    +----------+                                              |
  |                                                              |
  |  2026-08: scheduling object = structural unit                |
  |    (carrier of independent cost/benefit)                     |
  |                                                              |
  |  +--------------+  GPU shared state   time x space  -> shared-state coordinator
  |  | shared stage |  (SM quota/bandwidth)(HorizonServe)        |
  |  +--------------+  expert replica      load x topo   -> topology-aware placer
  |  | expert       |  (cross-rank copy)  (TAOT)                 |
  |  +--------------+  prefix KV          compute x trans -> provable approx orchestrator
  |  | prefix KV    |  (tree placement)   (PrefixPlace)          |
  |  +--------------+                                            |
  |                                                              |
  |  common: structured object -> combinatorial optimization ->  |
  |          provable guarantees for the platform                |
  |  role: queue manager (when) -> orchestrator                  |
  |        (where x how much x with whom to share)               |
  +--------------------------------------------------------------+
```

| 维度 | 排队器（传统） | 编排器（2026-08 三篇） |
|:--|:--|:--|
| 调度对象 | 请求（原子） | 请求内/模型内/数据内的结构单元 |
| 决策变量 | 执行顺序 | 放置位置 + 资源配额 + 共享关系 |
| 目标 | 队列延迟 | SLO 达标率 × 拓扑成本 × 异构成本 |
| 方法 | 启发式队列策略 | 组合优化（最优传输/设施选址/拍卖） |
| 保证 | 无 | 可证明（1/2-近似、99.8% of optimum） |
| 平台竞争力 | 排得多快 | **排得多懂结构** |

---

## 六、与知识库理论的闭环

| 知识库命题 | 本批实证 | 闭环状态 |
|:--|:--|:--:|
| 稀缺排序：HBM 带宽 > 容量 > FLOPs（[LLM 推理冗余消除](../../03_AI/llm-techniques-principles/2026-08-05-llm-inference-redundancy-elimination-deep-analysis.md)） | HorizonServe：带宽利用率 93% 饱和时 SM 节流成为唯一旋钮——带宽是第一瓶颈的调度侧实证 | ✅ 佐证 |
| KV Cache 是产品定义词、内存分层（[ai-storage 系列](../../03_AI/train/ai-storage/2026-08-06-kv-cache-concept-to-industry-standard-cmx-anchoring.md)） | PrefixPlace：前缀 KV 作为一等放置对象 + 异构成本建模——KV 层从「存储」升级为「调度资产」 | ✅ 深化 |
| MoE 硬件实现与专家通信（[MoE 硬件实现深度调研](../../02_rd/01_product/01_software/04-comm-lib/2026-07-24-moe-hardware-implementation-deep-analysis.md)） | TAOT：专家副本放置的最优传输解——MoE 通信成本可被调度算法显式最小化 | ✅ 补充 |
| GPU 网络通信前沿（[NCCL EP+GIN 等](../../07_industry-research/03_server/2026-08-01-gpu-network-communication-frontier-deep-analysis.md)） | TAOT 的拓扑成本矩阵 = 通信前沿的调度侧应用 | ✅ 连接 |
| 超节点 Scale-Up/Scale-Out 资源分配（[HBD 规模](../../02_rd/02_project/01_superpod/2026-08-03-hbd-domain-scale-deep-analysis.md)） | 三篇都是「结构感知」的资源分配——与 HBD 域规模选择的「拓扑决定配额」同构 | ✅ 同构 |
| 平台竞争力 = 编排而非模型（[模型能力对比与分级路由](../../03_AI/llm-techniques-principles/2026-08-03-model-capability-comparison-usage-strategy.md)） | 三篇证明调度对象粒度决定平台上限——「结构感知编排器」是新的竞争叙事 | ✅ 扩展 |

---

## 七、批判性审视

| # | 批判点 | 说明 |
|:-:|:--|:--|
| 1 | **HorizonServe 单 GPU 场景** | omni-model serving 限定单 GPU——多 GPU/多节点下的共享态协调未覆盖；GPU 间带宽争用问题可能更复杂 |
| 2 | **TAOT 是训练场景** | 专家副本放置针对训练（静态拓扑已知）；推理场景（动态路由 + 在线请求）的副本放置未覆盖；40%+ 加速基于单模型（Qwen3-30B-A3B），泛化待验证 |
| 3 | **PrefixPlace 的最优性依赖 profile 质量** | 99.84% of optimum 是「给定 profiled 成本」下的最优；profile 漂移（CV ≤0.51% 是稳定性证据，但长期漂移未测）会侵蚀最优性；12.3s 求解 5 万节点是单处理器，更大规模未验证 |
| 4 | **三篇均未开源（或未验证开源）** | TAOT 提及实现细节但未确认开源；HorizonServe/PrefixPlace 未见代码链接——复现性存疑 |
| 5 | **调度对象升级的商业叙事偏差** | 「排队器→编排器」是本文归纳框架；三篇论文本身聚焦具体问题（SLO/通信/KV 放置），平台叙事是知识库的抽象，需在真实平台验证 |
| 6 | **异构感知的普适性** | 三篇都依赖「结构可观测」（路径分类/专家负载/前缀树）——结构不可观测或动态剧变时（如前缀树频繁重建），编排收益可能消失 |

---

## 八、可证伪预测 P1-P5

| # | 预测 | 时间窗 | 证伪条件 |
|:-:|:--|:--|:--|
| P1 | **调度对象结构化成为 serving 平台默认设计**：主流平台（vLLM/SGLang）把 KV 放置/GPU 共享态纳入调度决策而非纯队列 | 2027 | 平台仍只有请求级队列调度 |
| P2 | **拓扑感知放置进入 MoE 训练默认配置**：TAOT 类方法成为 Megatron/DeepSpeed 的专家副本标准组件 | 2027 | 训练框架仍只用负载均衡启发式 |
| P3 | **异构成本画像成为 KV 缓存调度输入**：PrefixPlace 类 epoch 规划器 + profile 驱动成为混合 GPU 集群标配 | 2027 | 混合 GPU 集群仍用统一 APC |
| P4 | **「结构感知编排器」成为平台竞争叙事**：编排器（placement/scheduling 深度）与模型能力并列成为平台竞争力指标 | 2028 | 平台竞争仍只看模型与吞吐 |
| P5 | **三篇技术融合**：共享态协调（时间空间）× 专家放置（拓扑）× KV 放置（异构）整合进统一编排框架 | 2028 | 三类调度仍各自独立 |

---

## 九、本系统启示

1. **KV Cache 放置 = 本系统存储议题的调度侧**：PrefixPlace 的「前缀树 + 异构成本」与知识库 ai-storage 系列（KV 分层/CMX/EDSFF）互补——KV 层不只是容量问题，还是**放置优化问题**；
2. **「结构感知」是通用方法论**：三篇共同的语法「调度对象结构化 → 组合优化」可迁移到本系统的任务编排——技能调用（Skill-Use 触发/边界）也可视为「技能放置」（何时/何地/与谁共享上下文）；
3. **带宽是第一稀缺资源的调度实证**：HorizonServe 佐证 MEMORY.md「HBM 带宽 > 容量 > FLOPs」——本系统推理成本优化（prefix caching/连续批处理）的底层逻辑得到论文支撑；
4. **MoE 通信成本显式化**：TAOT 的「1pp 失衡 ≈ 7% 通信」权衡公式，可用于本系统评估集合通信优化 ROI（通信优化 vs 均衡性取舍）；
5. **可证明保证 > 启发式**：PrefixPlace 的 1/2-近似 + 99.8% 实证提示——本系统任何「最优调度」类脚本应优先选择有理论保证的算法，而非纯贪心。

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- [LLM 推理冗余消除统一框架](../../03_AI/llm-techniques-principles/2026-08-05-llm-inference-redundancy-elimination-deep-analysis.md) — 带宽 > 容量 > FLOPs 稀缺排序的本文件调度侧实证
- [KV Cache 从概念到产业标准](../../03_AI/train/ai-storage/2026-08-06-kv-cache-concept-to-industry-standard-cmx-anchoring.md) — KV 层从存储升级为调度资产
- [MoE 硬件实现深度调研](../../02_rd/01_product/01_software/04-comm-lib/2026-07-24-moe-hardware-implementation-deep-analysis.md) — MoE 通信成本可被调度算法显式最小化
- [GPU 网络通信前沿](../../07_industry-research/03_server/2026-08-01-gpu-network-communication-frontier-deep-analysis.md) — TAOT 拓扑成本矩阵的通信前沿应用

### 外部资料引用

- 来源: HorizonServe: Coordinating Request Scheduling with GPU Sharing for Omni-Model Serving, arXiv:2608.01785, https://arxiv.org/abs/2608.01785
- 来源: TAOT: Topology-Aware Optimal Transport for Dynamic Expert Replica Placement in MoE Training, arXiv:2608.03676, https://arxiv.org/abs/2608.03676
- 来源: PrefixPlace: Provable Prefix Key–Value Placement for LLM Serving under Heterogeneous Compute and Transfer Costs, arXiv:2608.01655, https://arxiv.org/abs/2608.01655

**诚实标注**：
- 三篇均为 arXiv 官方 HTML 全文一手抓取；量化数字取自摘要/实验节直接提取，未逐表穷尽（HorizonServe 各负载具体曲线、TAOT 消融方差、PrefixPlace 全 600 设置扫描未全量展开）；
- 三篇均为 preprint（cs.DC），未经长期同行评审；TAOT 为腾讯团队，可能与内部平台有隐性协同；
- 「排队器→结构感知编排器」叙事为知识库归纳框架，非论文官方表述；
- web_search API key 失效，素材经 arXiv 官方页面（abs + html 全文）直连获取。

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-08-07 | v1.0 | 素材 = 3 篇 arXiv 官方 HTML 全文一手抓取（HorizonServe / TAOT / PrefixPlace）；统一主线 = 调度对象三级升级，平台角色从排队器进化为结构感知资源编排器 |
| 2026-08-22 | v1.1 | 提升：补齐 std-002 五元素 + 跨文件交叉链接与一致性勘误 |
