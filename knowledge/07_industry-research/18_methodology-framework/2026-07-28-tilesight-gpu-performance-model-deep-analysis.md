# 🔬 TileSight 深度分析：第一性原理 Tile 中心 GPU 性能模型

> **分析日期**: 2026-07-28
> **来源**: arXiv:2607.22432 · cs.DC · Jul 24, 2026
> **作者**: Zhiwen Mo 等 15 人（Imperial College London, Peking University, SJTU, Tile-AI, Microsoft Research, University of Edinburgh）
> **代码**: 发表后开源
> **文件类型**: 深度专题分析
> **交叉引用**: [AI 框架动态跟踪 2026-07-28](../../weekly-reports/00_daily/2026-07-28.md)（快速笔记）· [TileSight 论文](https://arxiv.org/abs/2607.22432)

---

## 目录

- [1. 概述与核心问题](#1-概述与核心问题)
- [2. 背景：Tile 编程范式的兴起与性能分析工具的滞后](#2-背景tile-编程范式的兴起与性能分析工具的滞后)
  - [2.1 Tile 成为一等公民](#21-tile-成为一等公民)
  - [2.2 抽象鸿沟：编程范式变革 vs 分析工具原地踏步](#22-抽象鸿沟编程范式变革-vs-分析工具原地踏步)
  - [2.3 为什么现有工具不够](#23-为什么现有工具不够)
- [3. 架构：三层 Tile 执行引擎](#3-架构三层-tile-执行引擎)
  - [3.1 核心设计理念：Tile 从编程原语升维为分析原语](#31-核心设计理念tile-从编程原语升维为分析原语)
  - [3.2 整体框架](#32-整体框架)
  - [3.3 Intra-Tile 层：Tile 资源向量](#33-intra-tile-层tile-资源向量)
  - [3.4 Inter-Tile 层：依赖、并发与顺序](#34-inter-tile-层依赖并发与顺序)
  - [3.5 Pipeline Envelope：Prologue–Steady–Epilogue](#35-pipeline-envelopeprologue–steady–epilogue)
  - [3.6 Tile 重访距离缓存模型](#36-tile-重访距离缓存模型)
  - [3.7 Cross-Device 层：分布式 Tile 扩展](#37-cross-device-层分布式-tile-扩展)
- [4. 核心创新原理分析](#4-核心创新原理分析)
  - [4.1 创新一：三层统一 Tile 抽象](#41-创新一三层统一-tile-抽象)
  - [4.2 创新二：Tile 级 Pipeline 重叠分析](#42-创新二tile-级-pipeline-重叠分析)
  - [4.3 创新三：Tile 重访距离缓存建模](#43-创新三tile-重访距离缓存建模)
  - [4.4 创新四：Placement 驱动的分布式建模](#44-创新四placement-驱动的分布式建模)
- [5. 性能评估](#5-性能评估)
  - [5.1 单 GPU Kernel 延迟预测](#51-单-gpu-kernel-延迟预测)
  - [5.2 L2 Cache 命中率预测](#52-l2-cache-命中率预测)
  - [5.3 分布式 Kernel 预测](#53-分布式-kernel-预测)
  - [5.4 E2E vLLM Serving 预测](#54-e2e-vllm-serving-预测)
  - [5.5 诊断与优化应用](#55-诊断与优化应用)
- [6. 优劣势分析](#6-优劣势分析)
  - [6.1 结构性优势](#61-结构性优势)
  - [6.2 结构性劣势](#62-结构性劣势)
  - [6.3 与现有工具的对比](#63-与现有工具的对比)
- [7. 适用场景与部署考量](#7-适用场景与部署考量)
  - [7.1 核心适用场景](#71-核心适用场景)
  - [7.2 部分适用场景](#72-部分适用场景)
  - [7.3 不适用场景](#73-不适用场景)
- [8. 参考资料](#8-参考资料)
  - [变更日志](#变更日志)

---

## 1. 概述与核心问题

TileSight 是一个**第一性原理的 Tile 中心 GPU 性能模型**，将 Tile 从**编程原语**升维为**分析原语**，实现从单 GPU 核心到多 GPU 集群的统一性能建模。

**核心问题**：Triton、TileLang、CUDA Tile 等新一代编程框架已将 Tile 确立为一等公民，但性能分析工具仍然停留在粗粒度的 roofline bounds、黑箱 ML 预测器和事后 profiler 上。这种**抽象鸿沟**导致 GPU Kernel 开发者无法从 Tile 级别理解性能瓶颈。

**核心答案**：Tile 具有三个适合分析建模的属性——确定性（给定配置，资源使用完全确定）、可组合（Intra→Inter→Cross-device 三层可独立建模后组合）、可移植（跨 A100→B6000→MI210 共享同一抽象），TileSight 正是利用这三点的白盒分析引擎。

---

## 2. 背景：Tile 编程范式的兴起与性能分析工具的滞后

### 2.1 Tile 成为一等公民

| 框架 | 时间 | 地位 |
|:-----|:-----|:------|
| Triton (Tillet et al.) | 2019 | PyTorch 自定义 Kernel 的事实标准 |
| TileLang | 2025 | 在 Tile 级别解耦数据流与调度 |
| CUDA Tile | CUDA 13.1, 2026 | NVIDIA 官方—"近 20 年来最重要的 CUDA 进步" |
| CuteDSL | CUTLASS 生态 | Python DSL 暴露 CUTLASS Tile 抽象 |

Tile 编程的核心优势：开发者用 Tile 形状、Pipeline 深度、内存布局等高层参数描述计算，编译器/运行时将 Tile 映射到硬件执行——**这与传统 CUDA 线程级编程形成了范式的根本性变革**。

### 2.2 抽象鸿沟：编程范式变革 vs 分析工具原地踏步

| 工具类型 | 代表 | 问题 |
|:---------|:-----|:------|
| **Roofline 模型** | Williams et al. 2009 | 单个瓶颈标量无法区分 L2 miss 和 SMEM bank conflict |
| **ML 预测器** | NeuSight, PipeWeave | 每架构需重训练，黑箱不可解释 |
| **事后 Profiler** | Nsight Compute (NCU) | 事后分析改变执行，只能说"发生了什么"而非"改变 Tile 形状会怎样" |
| **模拟器** | SimAI, Vidur | 需要 Kernel 轨迹，无法用于调度搜索 |
| **自动调优** | Triton Autotune | 黑箱搜索数万配置，无解释性 |

**关键缺失**：没有一个工具能以 Tile 为中心的视角，在**不运行 Kernel** 的前提下回答"改变 Tile 形状、Pipeline 深度、块混洗会如何影响性能"。

### 2.3 为什么现有工具不够

以 FlashAttention-3 在 H100 上为例（论文 Fig. 1）：

```text
前向计算涉及 10+ 种异构操作：
  - Tensor Core 上的 2 个 GEMM
  - CUDA Core 上的 Reduction + Softmax
  - SFU 上的特殊函数
这些操作占用不同的硬件资源，且可以重叠执行。
重叠程度取决于调度顺序和 Pipeline 深度。
```

Roofline 模型：只能用算力/带宽比归因于"memory bound"或"compute bound"，完全看不到 10 个操作的重叠结构。

ML 预测器：需要 H100 上提前跑数万个配置训练，换到 B200 重新训练。

NCU：只能分析已经跑完的 Kernel，无法预测"把 Tile 从 64→128 会怎样"。

**TileSight 的动机正是填补这个鸿沟**——用 Tile 级别的分析建模来回答上述所有问题。

---

## 3. 架构：三层 Tile 执行引擎

### 3.1 核心设计理念：Tile 从编程原语升维为分析原语

TileSight 选择 Tile 作为统一分析抽象的三条理据：

| 属性 | 说明 | 对建模的意义 |
|:-----|:------|:------------|
| **确定性 (Deterministic)** | 给定 Tile 形状、Pipeline 深度、内存布局，资源使用完全确定 | 无需仿真即可做分析建模 |
| **可组合 (Composable)** | Intra→Inter→Cross-device 三层可独立建模后组合 | 统一框架覆盖从核心到集群 |
| **可移植 (Portable)** | A100/H100/H200/B200/B6000/MI210 共用 Tile 抽象 | 一次开发多架构适用 |

### 3.2 整体框架

```text
                      Tile 执行计划
+--------------------------------------------------+
|  Workload (算子+张量放置)                         |
|   v                                               |
|  Tile Execution Plan                              |
|   - Tile 形状 / Loop 顺序 / Swizzle               |
|   - Pipeline 深度 / Resident blocks per SM         |
|   - 分布式分区 / 集合通信算法                      |
+----------------------+---------------------------+
                       v
+--------------------------------------------------+
|  TileSight 三层分析引擎                           |
|                                                   |
|  +--------------+ +----------+ +--------------+  |
|  | Intra-Tile   | |Inter-Tile| | Cross-Device |  |
|  | 资源向量分解  | | DAG调度 + | | Placement ->  |  |
|  | (9种资源管线) | | 重访距离  | | α-β通信成本  |  |
|  +------+-------+ +----+-----+ +------+-------+  |
|         +--------------+--------------+           |
|                        v                         |
|              Pipeline Envelope                     |
|        Prologue -> Steady -> Epilogue               |
|         (递归应用于所有嵌套层级)                   |
+--------------------------------------------------+
                       v
+--------------------------------------------------+
|  输出: 延迟预测 / 资源利用率 / Cache命中 / 瓶颈   |
+--------------------------------------------------+
```

### 3.3 Intra-Tile 层：Tile 资源向量

每个 Tile 由三要素刻画：**操作类型**、**足迹 (footprint)**、**源/目标放置描述符**。

**放置描述符**是 TileSight 统一 Fusion 和分布式执行的中心抽象：

- 中间输出标记为 register/TMEM/SMEM 级别 → Fusion（消除全局存储）
- 加载源标记为远程分片 → 分布式（变为跨设备传输）

**资源向量 $\mathbf{u}(o)$** 是最核心的设计：

$$\mathbf{u}(o) = \langle t_{\text{TC}}, t_{\text{CUDA}}, t_{\text{SFU}}, t_{\text{TMEM}}, t_{\text{SMEM}}, t_{\text{L1.5}}, t_{\text{L2}}, t_{\text{DDR}}, t_{\text{Net}} \rangle$$

9 种可独立调度的硬件管线，由校准的硬件速率和 Tile 足迹计算得出：

| 管线 | 覆盖 | 典型占用 |
|:-----|:------|:---------|
| TC (Tensor Core) | Tensor Core GEMM | Pure matmul Tile 只填此条目 |
| CUDA | CUDA Core 计算 | Reduction/Softmax |
| SFU | 特殊函数单元 | Exp/归一化 |
| TMEM | Blackwell Tensor Memory | Softmax 校正加载/存储 |
| SMEM | Shared Memory | 中间结果暂存 |
| L1.5 | L1.5/LRC 缓存级 | H200/B200 中间级 |
| L2 | L2 缓存 | 全局缓存命中 |
| DDR | HBM 主存 | 缓存缺失落地 |
| Net | 跨 GPU 网络 | 远程张量访问 |

**关键设计**：不同管线的 Tile 可以重叠执行，同一管线的 Tile 串行化。覆盖率比 Roofline 的一个"瓶颈标量"高一个维度。

### 3.4 Inter-Tile 层：依赖、并发与顺序

Tile 之间的三种关系：

1. **生产者-消费者依赖**：固定迭代内的合法排序。例：FA-3 的 Q/K 加载 → Q@K GEMM → Softmax → P@V GEMM
2. **并发发射**：无依赖的 Tile 在资源向量不冲突时可以同时运行。例：加载下一个 K-block 的同时计算当前 block
3. **执行顺序**：Loop 迭代和 Tile Grid 的遍历顺序决定缓存复用。例：行面板遍历保持相邻 M-行对 B-tile 的复用

**Tile-Action DAG**：每个 Tile 动作被建模为 DAG 节点，边表示数据依赖。TileSight 枚举满足所有依赖的合法拓扑排序，选择 pipeline 重叠最优的那个。

实际搜索空间很小——FlashAttention 的核心 11 个 Tile 动作在依赖约束下从 $11!$ 缩小到仅 **132 个合法拓扑排序**。

### 3.5 Pipeline Envelope：Prologue–Steady–Epilogue

这是 TileSight 预测性能的核心计算模式：

$$T = T_{\text{pro}} + \max(N - d, 0) \cdot T_{\text{steady}} + T_{\text{epi}}$$

其中有效深度 $d = \text{stages} \times \text{resident\_tiles\_per\_SM} - 1$。

**为什么这是个关键创新？**

- Roofline 模型假设所有计算都在"稳态"进行——它忽略了 Pipeline 填充和排空
- 两个有相同稳态瓶颈的调度可能因为 Loop 短或 wave 少而端到端时间不同
- TileSight 的 Prologue/Epilogue 显式建模边界效应

**稳态重叠计算**：

$$T_{\text{steady}}(\sigma) = \max_r \sum_{o \in \sigma} u_r(o)$$

在合法拓扑排序中取最小的那个作为最优：

$$T_{\text{steady}} = \min_{\sigma \in \text{Topo}(D)} T_{\text{steady}}(\sigma)$$

### 3.6 Tile 重访距离缓存模型

这是 TileSight 中最具原创性的部分。

**核心挑战**：缓存行为取决于 Tile 执行顺序和复用模式。传统的缓存行级重访距离分析太底层，无法嵌入分析模型。

**TileSight 的方案**：将重访距离提升到 Tile 执行计划的层次。

**Tile 复用距离 $D_T$**：两个连续访问同一张量块之间访问的**不同 Tile 大小数据块**的数量。

**为什么 Tile 粒度工作**：

| 维度 | 传统缓存行 | TileSight |
|:-----|:-----------|:----------|
| 跟踪条目数 | 数万~数十万 | 数十~数百（$64\times$ 减少）|
| 粒度 | 128B 缓存行 | 8KB~128KB Tile |
| 调度可见性 | **不可见**（块混洗/遍历顺序信息丢失） | **直接可见**（Tile 顺序就是分析序列）|
| 计算代价 | 离线跟踪分析 | 分析循环内实时计算 |

**精确 SDCM 模型**（Stochastic Distance Cache Model）：

$$P(h \mid D_T) = \sum_{a=0}^{A-1} \binom{D_T}{a} \left(\frac{A}{B_T}\right)^a \left(\frac{B_T - A}{B_T}\right)^{D_T - a}$$

但二项式求和在大型 Tile Grid 上太慢。

**高斯近似 + Zelen-Severo 的加速方案**：

TileSight 使用正态分布近似二项分布，再用 Zelen-Severo 多项式逼近 CDF。结合**沿归约轴采样**（例如 GEMM 的 K 轴从 256 次检查减少到 1 次），**缓存模型评估加速约 5 个数量级**，使缓存建模从"离线痕迹分析"变为"分析循环内置组件"。

**效果验证**：B200 上，块混洗将 L2 命中率从 35% 变为 72%，TileSight 的预测 ~±1 个百分点。

### 3.7 Cross-Device 层：分布式 Tile 扩展

**核心思想**：跨设备执行只是 Tile 放置的一个特例。

- 源或目标指向其他 GPU → 资源向量的 Net 条目非零
- 从生产者-消费者放置推断所需的集合通信或点对点传输
- 每个远程访问分解为按序 stage（如 ring all-reduce 的 reduce-scatter + all-gather）
- 每个 stage 的 $\alpha$–$\beta$ 路由成本填入 Net 条目

**$\alpha$–$\beta$ stage 成本模型**：

$$T_k = \underbrace{\max_{(s,d,b)\in\mathcal{E}_k} \sum_{l\in\mathcal{P}_{sd}} \alpha_l}_{\text{路由 HOP 延迟}} + \underbrace{\max_{l\in\mathcal{L}} \beta_l B_{l,k}}_{\text{瓶颈链路串行化}}$$

同样经过 Pipeline Envelope——跨设备移动与本地计算通过网络径重叠，与三层其他部分共用一个机制。

---

## 4. 核心创新原理分析

### 4.1 创新一：三层统一 Tile 抽象

**不是什么**：三个独立的模型拼在一起。
**是什么**：共享核心抽象（HardwareUsage as per-pipeline time, tile action as composable unit, TileGrid as workload descriptor）的三层联合设计。

**为什么难**：缓存行为、Pipeline 重叠、分布式通信通常被不同社区分别研究。TileSight 证明了 Tile 抽象足以统一表达这三者。

**深度判断**：这是将"硬件加速器的分析模型"从**手工定制**（每个算子/每架构单独建模）推向**统一通用**的关键一步。

### 4.2 创新二：Tile 级 Pipeline 重叠分析

**不是新概念**：软件 Pipelininng 在编译器领域很成熟。
**新在哪里**：

1. 将 Pipeline 分析从指令级提升到 **Tile 级**
2. 同时覆盖**规则软件 Pipeline**（GEMM 的加载-计算重叠）和**复杂融合 Kernel**（FA-3 的 10+ 操作 DAG）
3. 用拓扑排序搜索替代人工指定调度

**深度判断**：Roofline 模型假设 100% 重叠或完全不重叠——都不对。TileSight 的 Prologue–Steady–Epilogue 模型是第一个在分析模型中显式建模重叠结构的实用方案。

### 4.3 创新三：Tile 重访距离缓存建模

**最难的创新**：缓存行为对 GPU kernel 性能影响巨大（图 2 显示 B200 的 L2 带宽随工作集大小从 ~20 TB/s 跌至 ~5 TB/s），但传统方法是跑 trace 或离线分析。

**TileSight 的关键洞察**：不需要跟踪每个缓存行——**Tile 级粒度已经足够**，因为 GPU 调度器本身就以 Tile 为单位分配工作。Tile 的执行顺序就是缓存行为的最优预测信号。

**加速 5 个数量级的秘密**：

1. Tile 粒度：$64\times$ 条目减少
2. 高斯近似：避免二项式求和
3. 归约轴采样：再减少 $256\times$
4. Zelen-Severo 近似：用多项式代替误差函数

**深度判断**：这项创新使"在分析循环中做缓存建模"成为可能。如果没有它，TileSight 要么牺牲精度（用固定命中率），要么慢到无法用于调度搜索。

### 4.4 创新四：Placement 驱动的分布式建模

**不是新内容**：Placement 和 α-β 模型都是成熟技术。
**新在哪里**：同一个 Placement 抽象统一描述 Fusion（register/TMEM/SMEM 级别）和分布式（远程 GPU）。这意味着在 TileSight 框架内，从"我是否应该把这两个 Kernel 融合"到"我是否应该把 TP 改为 EP"都可以用同一套工具分析。

**深度判断**：这个设计的工程价值可能被低估——对于推理框架开发者，在一个模型中同时探索 **Kernel Fusion 决策**和**并行策略决策**的能力是前所未有的。

---

## 5. 性能评估

### 5.1 单 GPU Kernel 延迟预测

| 硬件 | 场景 | 误差 (MAPE) | 对比 SOTA |
|:-----|:-----|:------------|:----------|
| A100/H200/B200/B6000 | 单 GPU GEMM | **12.35% (pooled)** | 优于所有基线 |
| 跨架构迁移 | 无需重新训练 | 优于需要重新训练的 ML 模型 | 移植性更好 |
| MI210 (AMD) | 跨厂商预测 | 可运行 | 架构抽象有效 |

**解释**：12.35% MAPE 的实际意义——对于延迟敏感场景（LLM Decoding），这足以区分"好配置 vs 差配置"（通常差 2-10×）；对于自动调优搜索，它足以修剪 90%+ 的低效配置。

### 5.2 L2 Cache 命中率预测

| 指标 | 数值 |
|:-----|:-----|
| 测试量 | 4,680 个 GEMM persistent-kernel 用例 |
| 误差 | **~±1 个百分点**（各 GPU 均如此）|
| 关键验证 | 块混洗从 35% → 72% 的命中率变化成功预测 |

**解释**：~±1 pp 的精度意味着 TileSight 的缓存模型在分析精度上达到了模拟器级别，但速度快 5 个数量级。

### 5.3 分布式 Kernel 预测

| 设置 | 工作负载 | wMAPE |
|:-----|:---------|:------|
| H200×8 | 纯集合通信（AllGather/AllReduce/ReduceScatter/AlltoAll）| **~5%** |
| B200×8 | 纯集合通信 | **~5%** |
| ≤32 GPU | 融合分布式 Kernel（AllGather+GEMM 等）| **16.18%** |

### 5.4 E2E vLLM Serving 预测

| 设置 | 规模 | wMAPE |
|:-----|:-----|:------|
| vLLM 解码 (TP=8) | ≤32 GPU | **13.52%** |

**这个数据的意义**：首次有性能模型能在一个分析框架内预测端到端的 vLLM serving 延迟，且无需提前运行 Kernel。这为自动配置搜索（TP 度、Pipeline 深度、Tile 形状）提供了可行的 Cost Model。

### 5.5 诊断与优化应用

**FlashAttention-3 建模对比 NCU**：

| 指标 | NCU (ground truth) | TileSight |
|:-----|:-------------------|:----------|
| 延迟 (ms) | 5.58 | 5.73 |
| L2 命中率 (%) | 96.50 | 95.26 |
| L2 利用率 (%) | 38.66 | 35.72 |
| SMEM 利用率 (%) | 51.14 | 43.13 |
| TC 利用率 (%) | 74.78 | 70.30 |
| SFU 利用率 (%) | 38.58 | 35.42 |

**诊断价值**：开发者可以从 TileSight 的输出中看到"瓶颈在 SMEM（利用率 43%）还是 TC（70%）"，然后调整 Tile 形状或 Pipeline 深度。

**优化应用**：TileSight 作为 Cost Model 选择的 Tile 配置与 vendor expert baseline 竞争。

---

## 6. 优劣势分析

### 6.1 结构性优势

1. ✅ **Unity（统一性）+ 白盒（解释性）**——在同一框架内覆盖 intra-GPU→inter-tile→cross-device，且所有输出可分解到 Tile 级别，告诉你"为什么慢"

2. ✅ **无需 Kernel 运行或 ML 训练**——只需一次性每架构微基准校准（带宽扫描、矩阵乘法探测，耗时分钟级）。换 GPU 无需重新训练

3. ✅ **跨架构可移植**——同时在 NVIDIA A100→B6000 和 AMD MI210 上验证。Tile 抽象天然适配不同 GPU 的层次化内存和计算结构

4. ✅ **缓存建模创新**——Tile 级重访距离 + 高斯近似加速 5 个数量级，使缓存行为建模从"事后分析"变为"分析循环原生组件"

5. ✅ **工程实用价值高**：
   - 预测 FA-3 延迟误差 < 3%
   - 预测 L2 命中率误差 ~±1 pp
   - E2E vLLM serving 误差 13.52%
   - Tile 配置选择与 vendor expert 竞争

6. ✅ **来自顶级学术-工业联合团队**——Imperial + PKU + MSR + Tile-AI，开源承诺

### 6.2 结构性劣势

1. ❌ **不建模指令级细节**：不处理 warp 级指令发射、编译器寄存器分配、硬件调度器指令粒度行为。当瓶颈在这些微观层面时，TileSight 会不准确

2. ❌ **依赖完整 Tile 执行计划**：对于非 DSL 的手写 CUDA Kernel，用户需要手动提供 Tile 配置——增加了使用门槛

3. ❌ **分布式扩展到 >32 GPU 的误差待验证**：当前仅在 ≤32 GPU 上验证，更大规模（百卡/千卡）的通信-计算重叠建模可靠性未知

4. ❌ **缓存模型在特殊模式下的退化**：NIAH MultiValue 类多值分散场景（如某些 Attention Pattern），Tile 级重访距离可能不够精细

5. ❌ **代码尚未开源**：发表后开源的承诺意味着当前无法复现验证

6. ❌ **Roofline 简单性丢失**：TileSight 比 Roofline 复杂得多，非 GPU 专家可能难以上手

### 6.3 与现有工具的对比

| 特性 | Roofline | NeuSight | PipeWeave | SimAI | TileSight |
|:-----|:---------|:---------|:----------|:------|:----------|
| 无需 Kernel Profiling/训练 | ✅ | ❌ | ❌ | ❌ | ✅ |
| Pipeline 感知 | ❌ | ❌ | △ | ❌ | ✅ |
| 缓存感知 | ❌ | ❌ | ❌ | ❌ | ✅ |
| 显式融合程序 | ❌ | ❌ | △ | ❌ | ✅ |
| 分布式 | ❌ | △ | △ | ✅ | ✅ |
| 计算-通信重叠 | ❌ | ❌ | ❌ | △ | ✅ |
| 可解释 (白盒) | ✅ | ❌ | △ | ❌ | ✅ |

✅ 完整支持 · △ 部分 · ❌ 不支持

---

## 7. 适用场景与部署考量

### 7.1 核心适用场景 ⭐⭐⭐

| 场景 | 理由 |
|:-----|:------|
| **Triton/TileLang/CUDA Tile Kernel 开发** | 直接提取 Tile 配置，预测延迟，指导优化 |
| **Kernel Fusion 决策** | 通过 Placement 描述符判断 Fusion 收益 |
| **自动调优 Cost Model** | 替代黑箱搜索，修剪 90%+ 无效配置 |
| **推理框架配置搜索**（vLLM/SGLang） | TP 度、Pipeline 深度、Tile 形状联合搜索 |
| **跨架构迁移** | 换 GPU 只需重新跑微基准，无需重新训练 |

### 7.2 部分适用场景 ⭐⭐

| 场景 | 限制 |
|:-----|:------|
| **手写 CUDA Kernel** | 需手动提供 Tile 执行计划 |
| **百卡级集群建模** | >32 GPU 验证不足 |
| **指令延迟敏感场景** | TileSight 不建模微观指令调度 |

### 7.3 不适用场景 ❌

| 场景 | 原因 |
|:-----|:------|
| **CPU 性能分析** | 纯 GPU 模型 |
| **包级网络模拟** | $\alpha$–$\beta$ 模型不处理微秒级拥塞 |
| **单指令性能调试** | 粒度不够——需要 Nsight Compute |
| **训练性能建模** | 论文未覆盖训练场景 |

### 7.4 推荐部署路径

```text
短期 (开源后)：
  +- 集成到 Triton Autotune -> 替代黑箱搜索
  +- 作为 TileLang/TileCUDA 的官方性能诊断工具
  +- 在 vLLM/SGLang 的 CI 中作为回归检测

中期 (6-12月)：
  +- 扩展到训练场景（Backward Pass + 大通信）
  +- 验证 >32 GPU 的大规模扩展性
  +- 提供 Web UI / IDE 插件的易用可视化

长期 (12-18月)：
  +- 支持 AMD MI350+ / Intel Gaudi 等更多架构
  +- 成为 GPU Kernel 开发的"编译时性能分析"标准组件
```

---

## 8. 参考资料

### 论文

1. **TileSight**: Zhiwen Mo et al. "TileSight: A First-Principles Tile-Centric Analytical GPU Performance Model from Cores to Clusters." arXiv:2607.22432, Jul 2026.
2. **Triton**: Tillet et al. "Triton: An Intermediate Language and Compiler for Tiled Neural Network Computations." MAPL 2019.
3. **CUDA Tile**: NVIDIA Corporation. "CUDA 13.1 Programming Guide." 2026.
4. **FlashAttention**: Dao et al. "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness." NeurIPS 2022.

### 关联工作

1. **NeuSight**: Lee et al. 2025. ML-based GPU performance predictor (TileSight 的对比基线)。
2. **PipeWeave**: Zhang et al. 2026. Hybrid analytical-ML predictor。
3. **SDCM**: 随机距离缓存模型 (Stochastic Distance Cache Model) 的原始理论。
4. **α–β 模型**: Thakur et al. "Optimization of Collective Communication Operations in MPICH." 2005.

---

### 变更日志

| 日期 | 变更 |
|:-----|:------|
| 2026-07-28 | 初次创建 |

---

> **维护说明**: 此文档为深度分析文档。TileSight 开源后，应补充代码可用性、社区反馈和实际部署经验。
