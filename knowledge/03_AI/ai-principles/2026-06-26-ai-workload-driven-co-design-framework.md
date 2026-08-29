# 🏗️ AI 时代的软硬件协同设计方法论：从 Workload 到 Chip 到 System

> **概要**: 从 Workload 到 Chip 到 System 的 AI 软硬件协同设计方法论
>
> **关键词**: 软硬件协同 · Workload · PD 分离 · MoE · Co-Design

---

## 📑 目录

- [一、范式转变：从设备制造商定义到 AI Workload 定义](#一范式转变从设备制造商定义到-ai-workload-定义)
  - [1.1 传统服务器设计的 "组件堆叠" 范式](#11-传统服务器设计的-组件堆叠-范式)
  - [1.2 AI Workload 的 "计算特性级联" 效应](#12-ai-workload-的-计算特性级联-效应)
  - [1.3 核心方法论：计算特性级联分析法](#13-核心方法论计算特性级联分析法)
- [二、AI 计算的金字塔模型：三层 Workload 抽象](#二ai-计算的金字塔模型三层-workload-抽象)
  - [2.1 Layer 1：计算原语（硬件的最直接约束）](#21-layer-1计算原语硬件的最直接约束)
  - [2.2 Layer 2：存储访问模式（系统架构的约束）](#22-layer-2存储访问模式系统架构的约束)
  - [2.3 Layer 3：通信模式（互联拓扑的约束）](#23-layer-3通信模式互联拓扑的约束)
- [三、训练 Workload 对 Chip + System 的约束链](#三训练-workload-对-chip-system-的约束链)
  - [3.1 约束链全景](#31-约束链全景)
  - [3.2 关键权衡：NVSwitch Radix vs 总带宽](#32-关键权衡nvswitch-radix-vs-总带宽)
  - [3.3 新发现：DisagMoE 的硬件含义](#33-新发现disagmoe-的硬件含义)
- [四、推理 Workload 对 Chip + System 的约束链](#四推理-workload-对-chip-system-的约束链)
  - [4.1 约束链全景](#41-约束链全景)
  - [4.2 KV Cache 的硬件路径设计](#42-kv-cache-的硬件路径设计)
  - [4.3 qs 不等式的战略影响](#43-qs-不等式的战略影响)
- [五、PD分离（Workload 分化导致硬件分化）](#五pd分离workload-分化导致硬件分化)
  - [5.1 PD 分离的本质：将一个 GPU 的工作拆成两种芯片做](#51-pd-分离的本质将一个-gpu-的工作拆成两种芯片做)
  - [5.2 对芯片设计的影响](#52-对芯片设计的影响)
  - [5.3 硬件设计的关键权衡：PD融合 vs PD分离](#53-硬件设计的关键权衡pd融合-vs-pd分离)
- [六、MoE Workload 碎片化导致设计范式重构](#六moe-workload-碎片化导致设计范式重构)
  - [6.1 MoE 打破的三个 GPU 基本假设](#61-moe-打破的三个-gpu-基本假设)
    - [假设 ①：计算负载均匀分布](#假设-①计算负载均匀分布)
    - [假设 ②：主导通信原语是 AllReduce](#假设-②主导通信原语是-allreduce)
    - [假设 ③：模型常驻 GPU，零通信成本](#假设-③模型常驻-gpu零通信成本)
  - [6.2 MoE 推理的对偶矛盾](#62-moe-推理的对偶矛盾)
  - [6.3 MoE 的最优硬件路线：3D 异构集成](#63-moe-的最优硬件路线3d-异构集成)
- [七、三级 Co-Design 框架：Chip ↔ Board ↔ System ↔ Cluster](#七三级-co-design-框架chip-board-system-cluster)
  - [7.1 框架总览](#71-框架总览)
  - [7.2 每个层次的交互接口](#72-每个层次的交互接口)
  - [7.3 具体设计约束的传递案例](#73-具体设计约束的传递案例)
    - [案例：MoE AlltoAll 延迟约束的级联传递](#案例moe-alltoall-延迟约束的级联传递)
- [八、具体设计场景推演（3 个完整案例）](#八具体设计场景推演3-个完整案例)
  - [8.1 场景 A：671B MoE 训练集群](#81-场景-a671b-moe-训练集群)
    - [工作负载特征](#工作负载特征)
    - [Chip 层面决策](#chip-层面决策)
    - [Board 层面决策](#board-层面决策)
    - [关键权衡](#关键权衡)
  - [8.2 场景 B：实时推理集群 (PD 分离)](#82-场景-b实时推理集群-pd-分离)
    - [工作负载特征](#工作负载特征)
    - [Chip 层面决策 (Prefill vs Decode 专用)](#chip-层面决策-prefill-vs-decode-专用)
    - [Board 层面决策](#board-层面决策)
  - [8.3 场景 C：约束国产化方案 (全栈自主)](#83-场景-c约束国产化方案-全栈自主)
    - [约束条件](#约束条件)
    - [Workload 适配决策](#workload-适配决策)
    - [特殊设计考量](#特殊设计考量)
- [九、未来 5 年演进路线与设计窗口](#九未来-5-年演进路线与设计窗口)
  - [9.1 各层次的演进时间线](#91-各层次的演进时间线)
    - [Chip 层面](#chip-层面)
    - [System 层面](#system-层面)
    - [Cluster 层面](#cluster-层面)
  - [9.2 设计窗口判断](#92-设计窗口判断)
  - [9.3 关键设计预留建议](#93-关键设计预留建议)
- [十、总结：从"设计一台服务器"到"设计一个AI计算系统"](#十总结从设计一台服务器到设计一个ai计算系统)
  - [10.1 范式转变小结](#101-范式转变小结)
  - [10.2 核心能力要求](#102-核心能力要求)
  - [10.3 最终推荐：三级并行设计策略](#103-最终推荐三级并行设计策略)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 一、范式转变：从设备制造商定义到 AI Workload 定义

### 1.1 传统服务器设计的 "组件堆叠" 范式

```text
客户需求 -> 部件选型(CPU/GPU/内存/存储/网络) -> 架构集成 -> 测试验证 -> 交付
          ^                               ^
    (部件厂商的 roadmap 决定)          (标准/接口决定)
```

**核心特征**：

- 设计自由度集中在**部件选型和组合**层面
- 客户需求通过"规格清单"传递（几核CPU、几块GPU、几个PCIe槽）
- 软件适配是后置的、被动的（BIOS配置→驱动加载→OS安装→应用部署）

**为什么这个范式在AI时代失效？**

### 1.2 AI Workload 的 "计算特性级联" 效应

AI 模型的计算特性不是"规格清单"能描述的，而是通过**多层次计算特性级联**影响整机设计：

```text
模型架构(Transformer/MoE/SSM)
  -> 计算模式(Compute-bound vs Memory-bound vs Communication-bound)
    -> 资源配比(算力:带宽:存储:互联)
      -> 芯片架构(Tensor Core密度/HBM配置/互联接口)
        -> PCB/供电/散热/互联拓扑
          -> 软件栈(框架/通信库/调度器)
```

**关键差异**：

| 维度 | 传统设计范式 | AI Workload 驱动设计 |
|:-----|:------------|:---------------------|
| **需求定义** | "我要一台8卡GPU服务器" | "我要训练671B MoE模型，通信模式是AlltoAll主导" |
| **设计起点** | 部件规格 | 计算特性分析 |
| **瓶颈识别** | CPU利用率/内存带宽 | Y**计算特性级联漏斗**：哪一层最先饱和？ |
| **验证标准** | SPECint/Stream/IOPS | 模型MFU(模型浮点利用率)/TGS(每秒生成token) |
| **成本模型** | BOM价格 | TCO = 算力成本+互联成本+电力成本+时间成本 |

### 1.3 核心方法论：计算特性级联分析法

```text
第一步：模型架构分析
  模型类型(Dense/MoE/SSM) -> 参数规模 -> 上下文长度
        v
第二步：计算特性提取
  Compute-bound (GEMM密集)
  Memory-bound (KV带宽)
  Communication-bound (AllReduce/AlltoAll)
        v
第三步：资源需求量化
  算力需求(TFLOPS) -> 内存需求(HBM/DRAM) -> 互联需求(带宽/延迟)
        v
第四步：架构权衡设计
  Chip: SRAM/HBM配比 -> Tensor Core密度
  Board: 互联拓扑 -> PCIe Lane分配
  System: 散热方案 -> 供电架构
  Cluster: Scale-up/Sclae-out边界
        v
第五步：软件栈适配
  通信库优化(NCCL/RCCL) -> 调度策略(PD分离/EP) -> 量化方案(FP8/FP4)
```

---

## 二、AI 计算的金字塔模型：三层 Workload 抽象

基于最新论文分析，AI计算可以提炼为**三种基本计算模式**的有机组合：

```text
                    +-----------------------+
                    |  Layer 3: 通信模式     |
                    |  AllReduce / AlltoAll   |
                    |  / Point-to-Point       |
                    +-----------------------+
                    |  Layer 2: 存储访问模式  |
                    |  权重读取 / KV读写     |
                    +-----------------------+
                    |  Layer 1: 计算原语     |
                    |  GEMM / GEMV / Attention|
                    +-----------------------+
```

### 2.1 Layer 1：计算原语（硬件的最直接约束）

| 计算原语 | 计算特性 | OI (Operational Intensity) | 典型场景 | 硬件设计含义 |
|:---------|:---------|:---------------------------|:---------|:-------------|
| **GEMM (large batch)** | Compute-bound | > 100 FLOPs/Byte | 训练 Forward/Backward | Tensor Core 密度优先 |
| **GEMV (small batch)** | Memory-bound | < 10 FLOPs/Byte | MoE Expert FFN, batch=1 | 带宽>算力,SRAM缓存 |
| **Attention (Prefill)** | Compute-bound | 50-200 FLOPs/Byte | QKV计算 | Tensor Core+Flash Attn |
| **Attention (Decode)** | Memory-bound | 0.5-2 FLOPs/Byte | KV Cache读取 | HBM带宽第一 |
| **Softmax/激活函数** | Compute-light | — | 路由/Gate | 非瓶颈，通用ALU即可 |

**关键发现（来自 FlatAttention, arXiv:2604.02110）**:

- 在 Wafer-Scale 架构上，Attention 的 on-chip fabric collective 可以比 FlashAttention-3 快 **4.1×** [来源: arXiv:2604.02110]
- HBM 流量降低 **16×**，带宽利用率达 **78%** [来源: arXiv:2604.02110]
- → **Attention 的 Memory-bound 特性可以被片上互联大幅缓解**

### 2.2 Layer 2：存储访问模式（系统架构的约束）

| 存储访问模式 | 特征 | 对系统设计的影响 |
|:-------------|:-----|:----------------|
| **权重读取 (Weights)** | 只读、可预测、大块传输 | HBM优先，量化后带宽需求减半 |
| **KV Cache 读写 (KV)** | 混合读写、随机访问、块大小不固定 | **分离带宽通道**、硬件量化、层级存储 |
| **激活值缓存 (Activations)** | 训练时临时写入，Checkpoint后释放 | SRAM > HBM，减少HBM写回 |
| **优化器状态 (Optimizer)** | 训练专用，FP32累积 | 需要独立HBM区域 |

**关键发现（qs Inequality, arXiv:2603.08960, AMD）**:

- MoE推理时，KV Cache + 驻留 Expert 权重 = 双重 HBM 压力
- 质量匹配的 Dense 模型吞吐比 MoE 高 **4.5×** [来源: arXiv:2603.08960]
- **这从根本上挑战了 MoE 对推理硬件设计的假设**

### 2.3 Layer 3：通信模式（互联拓扑的约束）

| 通信模式 | 特征 | 延迟敏感度 | 带宽需求 | Hardware 含义 |
|:---------|:-----|:-----------|:---------|:--------------|
| **AllReduce (梯度同步)** | 对称、可预测、消息量大 | 中等 | 极高 | NVLink/SHARP 可加速 |
| **AlltoAll (Expert路由)** | 非对称、碎片化、小消息 | **极高** | 中等 | **NVSwitch radix > 带宽** |
| **Point-to-Point (PP通信)** | 管道传输、块大小固定 | 高 | 中-高 | NVLink 直接通信 |
| **KV传输 (PD分离)** | 大块、流式 | 中 | 高 | 需要专用带宽通道(GDA) |

**关键发现（NVIDIA NCCL EP v0.1.0, Jun 2026）**:

- MoE AlltoAll 有两种截然不同的模式：
  - **LL（Low Latency）**：1-128 tokens，ns级延迟是关键 → **硬件AlltoAll加速器**
  - **HT（Hierarchical）**：4096+ tokens，分层聚合为主 → **拓扑感知路由**
- → **单一互联设计无法同时优化两种模式**

---

## 三、训练 Workload 对 Chip + System 的约束链

### 3.1 约束链全景

```text
训练场景 (671B MoE, 1M tokens/step)
  |
  +- [计算特性] Compute-bound (Forward+Backward) + Communication-bound (AlltoAll)
  |
  +- [Chip 层面]
  |   +- Tensor Core 密度: 极高 (GEMM主导)
  |   +- SRAM/Die: 越大越好 (减少激活值HBM写回)
  |   +- HBM容量: 4-6×模型参数 (weight+grad+optimizer+act)
  |   +- HBM带宽: 高但不是第一瓶颈
  |   +- 互联(NVSwitch): AlltoAll延迟优化 > AllReduce带宽优化
  |   +- 精度支持: FP32 accumulate + BF16/FP8 compute + FP4 optional
  |
  +- [Board 层面]
  |   +- GPU数量/域: 8 GPU per domain (TP=8) + 域间Rail拓扑
  |   +- 互联拓扑: 域内全互联 (NVLink) + 域间Rail (RoCE/IB)
  |   +- PCIe配置: Host CPU↔GPU带宽为次要 (训练时几乎不通过PCIe)
  |   +- BMC管理: 批量部署、固件同步、功耗封顶
  |
  +- [System 层面]
  |   +- 散热: 液冷标配 (GPU常年100% TDP, 1000-1500W/GPU)
  |   +- 供电: 48V/800V HVDC (铜损随功率密度指数增长)
  |   +- 网络: 800Gbps/RoCE or IB, Rail拓扑优化
  |   +- 检查点: 聚合带宽100+GB/s (模型保存)
  |
  +- [Cluster 层面]
      +- 调度: 拓扑感知调度 (减少跨域通信)
      +- 容错: 3个9足够 (EEP, MoE天然容错)
      +- 监控: NCCL telemetry + GPU健康度
```

### 3.2 关键权衡：NVSwitch Radix vs 总带宽

**来自最新论文的证据（Rethinking Network Topologies, arXiv:2605.00254）**:

| 拓扑 | 成本效益（相对scale-up） | 适用场景 |
|:-----|:------------------------|:---------|
| Scale-up (NVL72-like) | 基准(1.0×) | NVIDIA 当前路径 |
| 3D Full-Mesh | **+20.6-56.2%** | 开放标准路线 |
| 3D Torus | +5-15% | 超算场景 |
| Dragonfly | -10-30% | 超大集群 |

**硬件含义**：

- 降低 scale-up 带宽 27% → 每美元吞吐 **提升27%**（论文第5.2节） [来源: arXiv:2605.00254]
- → **当前 scale-up 互联普遍过度配置**
- → 对 GPU 芯片设计者的启示：不一定要在片外互联上堆最大带宽

### 3.3 新发现：DisagMoE 的硬件含义

**DisagMoE（arXiv:2605.11005, Meta）**：

- 将 MoE 训练的 Attention 和 FFN 解耦到两个 GPU 组
- 多级流水线 + 单向多对多通信 → **1.8×加速** [来源: arXiv:2605.11005]
- → **Chip design 含义**：Attention Core 和 FFN Expert Core 可以物理分离（异构die设计）

---

## 四、推理 Workload 对 Chip + System 的约束链

### 4.1 约束链全景

```text
推理场景 (671B MoE, 128K上下文, 实时batch)
  |
  +- [计算特性] Memory-bound (KV读取) + Compute-light (少量GEMM) + Communication-sensitive (AlltoAll)
  |
  +- [Chip 层面]
  |   +- Memory Bandwidth: 第一优先级 (解码速率 = 带宽/(参数+KV))
  |   +- KV Cache 专用硬件: 分离读取通道、硬件量化、片上缓存
  |   +- Tensor Core: 不需要极致密度 (利用率仅10-30%)
  |   +- HBM容量: 越大越好 (KV Cache膨胀 + Expert驻留)
  |   +- SRAM 作为 KV Cache: 1-4MB/core缓存热KV
  |   +- 互联优化: 延迟优化 (AlltoAll < 1μs) > 带宽优化
  |
  +- [Board 层面]
  |   +- GPU配置: 1-2GPU per node (延迟敏感的推理无需大域)
  |   +- KV传输: 需要GDA (GPU Direct Access to memory)
  |   +- CXL内存池: 冷KV卸载 -> 扩展上下文容量
  |   +- 形态: 高密度/低功耗 (推理不一定要1000W+ GPU)
  |
  +- [System 层面]
  |   +- 散热: 风冷可行 (300-600W推理GPU), 高密度部署
  |   +- 供电: 标准PSU足够 (推理功耗波动大，需DVFS)
  |   +- 网络: 中等带宽 (AlltoAll消息量小但延迟敏感)
  |   +- 形态: PD分离时Prefill和Decode不同形态
  |
  +- [Cluster 层面]
      +- PD分离: 独立扩缩容Prefill/Decode集群
      +- 调度: 实时路由、请求级负载均衡
      +- 缓存: Prefix Cache、KV Cache层级存储
```

### 4.2 KV Cache 的硬件路径设计

**基于 7 条演进路径的硬件含义（KVCache 架构演进全景）**：

| 技术 | 硬件要求 | 实现难度 | 收益 |
|:-----|:---------|:---------|:-----|
| GQA (分组查询注意力) | 架构级支持，减少KV头 | 低 | 2-8× KV容量提升 |
| MLA (多头潜在注意力) | 矩阵吸收或Kernel解压 | 中 | 96% KV压缩（DeepSeek V3） |
| CSA+HCA (分层压缩) | 稀疏/TopK选择硬件 | 高 | ~90% KV压缩（DS V4） |
| FP8/FP4 KV量化 | 硬件量化单元 | 中 | 2-4× KV带宽节省 |
| Linear Attention (Mamba/DeltaNet) | 全新计算模式 | 极高 | O(1) KV - 根本性变革 |
| PagedAttention | **片上硬件实现** | 低 | 减少碎片化带宽浪费 |
| 层级KV存储(HBM→CXL→NVMe) | CXL控制器+GDS | 中 | 上下文扩展至1M+ |

### 4.3 qs 不等式的战略影响

**qs Inequality（arXiv:2603.08960, AMD）** 提出的矛盾：

```text
MoE 推理的双惩罚:
  P1: Expert路由碎片化 minibatch -> 降低weight reuse
  P2: 大量 resident expert 占HBM -> 挤压 KV Cache

结论: 质量匹配的 Dense 模型，吞吐比 MoE 高 4.5×
```

**对GPU芯片设计的路线冲击**：

```text
+---------------------------------------------------------+
|  路线A (当前主流): MoE 是长期趋势                        |
|  芯片设计投入: Expert预取、KV路径分离、PD分离、AlltoAll优化 |
|  风险: 如果qs正确，白费                                  |
|                                                          |
|  路线B (qs不等式建议): MoE->训练, 蒸馏->Dense部署          |
|  芯片设计投入: HBM带宽、KV Cache路径、Dense推理优化        |
|  风险: 如果qs被证伪，错过MoE推理优化窗口                   |
|                                                          |
|  🟡 建议: 两条路线都留兼容口                              |
|  - 互联不过度AlltoAll特化                                |
|  - 保留Dense推理的"全矩阵"算力优势                        |
|  - 关注KV Cache路径(两条路线都需要)                      |
|  - 关注小batch MatMul效率(两条路线都需要)                 |
+---------------------------------------------------------+
```

---

## 五、PD分离（Workload 分化导致硬件分化）

### 5.1 PD 分离的本质：将一个 GPU 的工作拆成两种芯片做

```text
传统: GPU同时做Prefill(计算密集) + Decode(带宽密集)
           -> 两种负载互相干扰 -> GPU利用率 = Prefill 80% / Decode 20%

PD分离后:
  Prefill集群 -> Compute-optimized GPU (高Tensor Core密度、中等HBM)
  Decode集群 -> Memory-optimized GPU (高HBM带宽、低Tensor Core密度)
```

### 5.2 对芯片设计的影响

| 设计维度 | Prefill-optimized GPU | Decode-optimized GPU |
|:---------|:----------------------|:---------------------|
| **Tensor Core 密度** | 极高 (>90% die) | 中低 (30-50% die) |
| **HBM栈数** | 6-8 stack | **12-16 stack** |
| **HBM带宽/算力比** | ~20 GB/s per TFLOPS | **~80 GB/s per TFLOPS** |
| **SRAM per Core** | 1MB+ | 256-512KB |
| **互联要求** | 高（Prefill后分发KV） | 低（逐token输出） |
| **典型功耗** | 700-1200W | 300-600W |
| **散热** | 液冷必选 | 风冷可行 |
| **单位对比** | 1 P-GPU : 4-8 D-GPU | |

### 5.3 硬件设计的关键权衡：PD融合 vs PD分离

**来自最新论文的分析（FlexNPU, arXiv:2604.03486）**：

- 同一NIC内PD虚拟化 → 吞吐提升 **26.33%** [来源: arXiv:2604.03486]
- 但融合设计复杂度高于分离

**决策框架**：

```text
PD分离决策树：

训练/推理/混合？
+- 纯训练 -> 不需要PD分离（训练不存在Decode瓶颈）
+- 纯推理 -> 需要PD分离（Prefill-Decode特性差异最大化）
+- 混合 -> 看比例
    +- 推理占比 > 70% -> PD分离（两种集群独立扩缩容）
    +- 推理占比 < 30% -> 融合方案或软件调度
```

---

## 六、MoE Workload 碎片化导致设计范式重构

### 6.1 MoE 打破的三个 GPU 基本假设

#### 假设 ①：计算负载均匀分布

**DODOCO（arXiv:2605.20982）证明**：

- MoE 路由 Gini 系数分布在 **0.105~0.38**（取决于架构）
- **路由不均衡是模型架构固有属性**，不能通过系统层优化消除
- MLA/GDN 架构 Gini 高达 0.24-0.38

**硬件影响**：

- GPU 不能假设"所有核心负载均衡"
- 需要 **动态工作负载分配硬件**（而非静态调度）
- SRAM 分配必须是动态的、可迁移的

#### 假设 ②：主导通信原语是 AllReduce

```text
Dense: AllReduce (对称、可预测、大消息)
MoE:   AlltoAll (非对称、碎片化、小消息)
         + AllReduce (梯度同步，仍然保留)
```

**硬件影响**：

- NVSwitch 需要优化**延迟**（面向AlltoAll的ns级消息）而非**带宽**（面向AllReduce的GB级）
- NCCL EP 提供两种模式（LL/HT）需要不同的硬件路径
- **Rethinking Topologies（arXiv:2605.00254）**：3D full-mesh 拓扑成本效益比 scale-up 高 20.6-56.2%

#### 假设 ③：模型常驻 GPU，零通信成本

**MoE 将模型拆分到多个 GPU → AlltoAll 成为新常态**

**NIMBLE（arXiv:2604.00317）量化**：

- Skewed AlltoAllv 比 NCCL/MPI 慢 **5.2×** [来源: arXiv:2604.00317]
- → MoE 场景下 **通信效率比计算效率更关键**

### 6.2 MoE 推理的对偶矛盾

```text
            Expert 路由碎片化
                  v
  每个 GPU 上 Expert 数量 v -> 每个 Expert batch ^
                  v
    Expert权重占用HBM ^ <--> KV Cache 可用HBM v
                  v
          qs Inequality 惩罚显现
```

**硬件缓解方案**：

| 方案 | 源码 | 效果 | 硬件需求 |
|:-----|:-----|:-----|:---------|
| Expert 预取 | MoE-SpeQ (arXiv:2511.14102) | 2.34×加速 | 路由预测器硬件 |
| KV Cache 专路 | 本分析 | 2×有效带宽 | 独立HBM通道 |
| Expert 级别DVFS | PALS (arXiv:2605.21427) | 26.3%能效提升 | **核心级DVFS域** |

### 6.3 MoE 的最优硬件路线：3D 异构集成

**A3D-MoE (arXiv:2507.19142, Georgia Tech)** 提出：

```text
3D 集成 MoE Chiplet 方案:

  +-------------------------------------+
  |  Die 3 (顶部): Expert权重SRAM + HBM控制器 |
  +-------------------------------------+
  |  Die 2: 路由器 + Expert Core × N   |
  +-------------------------------------+
  |  Die 1: Attention Core + KV Cache   |
  +-------------------------------------+
  |  Die 0 (底部): I/O + 互联接口       |
  +-------------------------------------+
```

**收益**：

- 延迟降低 **1.8-2×**
- 能耗降低 **2-4×**
- 吞吐提升 **1.44-1.8×**

---

## 七、三级 Co-Design 框架：Chip ↔ Board ↔ System ↔ Cluster

### 7.1 框架总览

```text
                    +--------------------------------------+
                    |      Level 0: Workload Analysis      |
                    |  计算特性分解 -> 瓶颈识别 -> 量化需求   |
                    +----------------+---------------------+
                                     v
  +-----------------------------------------------------------------+
  |  Level 1: Chip Architecture Co-Design                          |
  +-----------------------------------------------------------------+
  |  Software v                          ^ Chip Design             |
  |  - NCCL EP原语                       - Tensor Core密度         |
  |  - PD分离调度器                       - HBM栈数/带宽           |
  |  - KV量化算法                         - 互联接口延迟优化       |
  |  - Expert路由预测                     - SRAM/KV Cache分配      |
  +-----------------------------------------------------------------+
                                     ↕
  +-----------------------------------------------------------------+
  |  Level 2: Board/System Co-Design                               |
  +-----------------------------------------------------------------+
  |  Chip Design v                    ^ System Design              |
  |  - HBM物理层接口                    - PCB信号完整性             |
  |  - GPU-NVLink/NVSwitch             - 互联拓扑(NVSwitch/PCIe)   |
  |  - 供电接口(SVID/PMBus)            - 液冷散热接口              |
  |  - 管理接口(BMC/NC-SI)             - 供电架构(48V/800V)        |
  +-----------------------------------------------------------------+
                                     ↕
  +-----------------------------------------------------------------+
  |  Level 3: Cluster/Network Co-Design                            |
  +-----------------------------------------------------------------+
  |  System Design v                ^ Cluster Design               |
  |  - GPU-NIC互联                    - Scale域定义                 |
  |  - NCCL通信原语                   - Rail拓扑/Dragonfly         |
  |  - 固件/驱动                       - 全局调度器                 |
  |  - 遥测/监控                       - 容错策略                   |
  +-----------------------------------------------------------------+
```

### 7.2 每个层次的交互接口

| 交互接口 | Level 1→2 | Level 2→3 | Level 3→Cluster |
|:---------|:----------|:----------|:----------------|
| **带宽** | GPU HBM带宽 → 单节点通过PCIe/NVLink输出的带宽 | 每节点NIC数 → 集群总互联带宽 | 集群ToR/spine → 全域带宽 |
| **延迟** | GPU内部Core↔HBM延迟 → 算力利用率 | NVSwitch延迟 → AlltoAll通信效率 | 跨域往返延迟 → 训练步长 |
| **容量** | HBM容量 → 单节点模型规模 | DRAM+SSD → 层级KV存储 | 全局内存池化 → CXL/对象存储 |
| **可靠性** | GPU错误检测 → 检查点策略 | 节点级容错 → EEP/SPARe | 集群级故障恢复 |

### 7.3 具体设计约束的传递案例

#### 案例：MoE AlltoAll 延迟约束的级联传递

```text
[Workload] MoE推理, batch=1, Top-2路由
  v 每步传输 2 expert × 隐藏层维度参数（~MB级）

[Chip] AlltoAll 延迟必须 < 1μs（否则解码等待）
  v NCCL EP LL 模式需要 ns 级互联

[Switch] NVSwitch radix > 总带宽
  v 需要更多端口而非更高端口带宽

[Board] 8 GPU 域内全互联即可（不需要 72 GPU 域）
  v 域间通过 Rail 拓扑连接
  v
[System] 机柜设计可以更紧凑，不需要 NVL72 规模的 NVSwitch
  v
[Cluster] 调度时感知 Expert 放置位置
```

---

## 八、具体设计场景推演（3 个完整案例）

### 8.1 场景 A：671B MoE 训练集群

#### 工作负载特征

| 维度 | 值 |
|:-----|:----|
| 模型 | DeepSeek V3 风格 671B MoE (37B active) |
| 并行策略 | TP=8 + EP=8 + PP=4 + DP=2 |
| 总 GPU | 512 (64域 × 8 GPU) |
| 通信模式 | AllReduce (梯度) + AlltoAll (Expert路由) |
| 每步计算量 | ~100 PFLOPS |

#### Chip 层面决策

```text
Tensor Core 密度: 极高 (BF16/FP8 Tensor Core占die > 80%)
SRAM per Core: 1MB+ (减少激活值HBM写回)
HBM容量: 192GB+/GPU (weight 671B+act+grad+optimizer ≈ 1.2TB/GPU)
HBM带宽: 3.2TB/s+ (HBM3e)
互联: NVLink 5 1.8TB/s + 800Gbps RoCE × 4
特殊要求: NCCL EP LL 模式的 ns 级 AlltoAll 硬件加速
```

#### Board 层面决策

```text
GPU域: 8 GPU per domain (TP=8)
域内互联: NVSwitch (全互联, radix优先 > 带宽)
域间互联: Rail拓扑 (每个GPU直连一个NIC)
PCIe: 只用于启动和BMC, 不参与训练流量
供电: 800V HVDC 输入 -> IBC -> 48V母排 -> GPU
散热: 冷板液冷 (1000W+ GPU, 常年100% TDP)
```

#### 关键权衡

| 权衡 | 选择 | 理由 |
|:-----|:-----|:------|
| NVLink 域大小 | 8 GPU | Rethinking拓扑论文证明域内8 GPU足够，更大的域PP气泡成本>收益 |
| 域间拓扑 | Rail | 比胖树节省50%+交换机成本，NIMBLE软件补偿5.2×不平衡 |
| 液冷 vs 浸没 | 冷板液冷 | 1000W级别冷板已成熟，浸没式维护成本过高 |
| 容错策略 | EEP (3个9) | MoE天然容错，不需要5个9（EEP恢复52s vs 348s） |

### 8.2 场景 B：实时推理集群 (PD 分离)

#### 工作负载特征

| 维度 | Prefill 集群 | Decode 集群 |
|:-----|:-------------|:-------------|
| 负载类型 | Compute-bound | Memory-bound |
| 模型 | 671B MoE (QS 优化后) | 同上 |
| 并行 | TP=4, EP=4 | TP=1, EP=4 |
| 每步 | 1 prompt ~1K tokens | 1 token |
| 典型利用率 | 80-95% | 60-80% |

#### Chip 层面决策 (Prefill vs Decode 专用)

| 设计维度 | Prefill GPU | Decode GPU |
|:---------|:------------|:------------|
| **Tensor Core** | 极高密度 (8× dense) | 中密度 (2× bandwidth-opt) |
| **HBM栈数** | 6-8 | **12-16** |
| **HBM带宽** | 3.2TB/s | **6.4TB/s+** |
| **SRAM** | 1MB/core | 256KB/core |
| **KV Cache硬件** | 可选 | **必须** (量化+专用路径) |
| **功耗/TDP** | 700W | 300-400W |
| **互联** | 高带宽(分发KV) | 中等 |

#### Board 层面决策

```text
Prefill 节点形态:
  - 8 P-GPU per node
  - 液冷 (700W GPU)
  - 高带宽网络 (分发KV到Decode集群)

Decode 节点形态:
  - 4 D-GPU per node (密度优先)
  - 风冷可行 (300-400W)
  - CXL内存池扩展KV容量
  - 网络: 中等带宽但低延迟

PD 分离网络:
  - NVLink/GDA: Prefill分发KV到Decode (ROCE, ~10μs)
  - LMCache/Prefix Cache: 前缀KV复用
```

### 8.3 场景 C：约束国产化方案 (全栈自主)

#### 约束条件

| 约束 | 具体要求 |
|:-----|:---------|
| GPU | 昇腾910C (600+ TFLOPS FP16) |
| 互联 | HCCS (华为自研, 类似NVLink) + 100Gbps RoCE |
| 框架 | CANN + MindSpore |
| 国产化率 | > 90% (BOM) |

#### Workload 适配决策

| 维度 | 方案 | 损失评估 |
|:-----|:-----|:---------|
| **模型** | 优先适配Dense模型 (减少通信依赖) | MoE方案需等待CANN成熟 |
| **并行策略** | DP+TP为主, EP可选 | EP通信延迟可能多30-50% |
| **计算精度** | BF16为主, FP8受限 | 算力利用率~70% of NVIDIA |
| **互联** | 域内8卡HCCS + 域间RoCE | NCCL替代库性能差~20% |
| **调度** | Volcano拓扑感知调度 | 需自研调度器 |

#### 特殊设计考量

```text
双轨策略:
  同一机箱兼容昇腾910C和NVIDIA B300两种GPU方案
  通过PCIe Switch切换
  BMC统一管理

系统级约束:
  - 液冷方案国产化: 国产CDU+冷板已验证
  - 供电方案: 48V OCP + 国产电源模块
  - 网络: 国产100Gbps交换芯片 (盛科)
  - 存储: 国产NVMe SSD + 分布式存储
```

---

## 九、未来 5 年演进路线与设计窗口

### 9.1 各层次的演进时间线

#### Chip 层面

| 年份 | 事件 | 对系统设计的影响 |
|:-----|:-----|:----------------|
| **2026** | NVFP4 量产 (Blackwell) | 推理KV Cache 4×压缩 |
| **2026** | HBM4 256GB/stack | 单GPU可加载1T参数 |
| **2027** | GPU互联从NVLink走向UALink/CXL | 开放生态可混插不同厂商GPU |
| **2027-28** | 推理专用GPU出现 (PD分离) | Decode GPU风冷可行 |
| **2028** | 3D集成MoE Chiplet (A3D方案) | 延迟/能耗降低2-4× |
| **2029-30** | 光互联集成到chip (CPO量产) | GPU间延迟<100ns |

#### System 层面

| 年份 | 事件 | 设计影响 |
|:-----|:-----|:---------|
| **2026** | 800V HVDC 试点 | 供电架构从12V→48V→800V三级转换 |
| **2026** | 液冷成AI标配 | 风冷不再列入AI服务器设计基线 |
| **2027** | PD分离架构普及 | Prefill和Decode用不同硬件 |
| **2027-28** | CXL内存池量产 | KV Cache层级存储成为标配 |
| **2028-30** | 光互联机柜内互联 | CPO取代可插拔光模块 |

#### Cluster 层面

| 年份 | 事件 | 设计影响 |
|:-----|:-----|:---------|
| **2026** | 开放标准(UALink/ODCC) | 生态分化开始 |
| **2027** | ASIC挑战GPU | 非NVIDIA方案可行 |
| **2027-28** | 光交换机(OCS)应用 | 集群拓扑从电→光 |
| **2028-30** | 全光互联集群 | 万卡一致性域可行 |

### 9.2 设计窗口判断

```text
              2026          2027          2028          2029          2030
              ------------------------------------------------------------
PD分离GPU     [探索]----[分化产品]----[主流]----------[标准]
Chiplet 3D    [研究]----[工程样片]--[量产]----------[迭代]
CPO光互联     [POC]-----[NPO过渡]----[CPO量产]------[全光]
800V HVDC     [试点]----[部署]------[标配]----------[迭代]
UALink开放    [标准]----[产品]------[生态]---------[主流]
推理专用GPU   [论文]----[原型]------[产品]---------[迭代]
3nm以下制程   [3nm]----[2nm]------[1.4nm]--------[1nm]

设计策略:
  [立即执行] [兼容预留] [POC验证] [持续跟踪]
```

### 9.3 关键设计预留建议

| 预留项 | 建议 | 代价 | 收益 |
|:-------|:-----|:-----|:------|
| **液冷接口标准化** | 统一冷板/管路接口 | 少量BOM增加 | 跨代液冷升级 |
| **800V供电预留** | 电源仓支持48V/800V双模 | 10-15%空间 | 2027年供电升级不换机箱 |
| **CXL接口预留** | 主板预留CXL连接器 | $5-10/BOM | 2027年内存池化 |
| **光互联兼容** | 机箱预留光纤管理槽位 | 结构设计复杂度 | 2028年CPO升级不换机箱 |
| **双轨GPU兼容** | PCIe Switch + 通用OAM接口 | 15-20% PCB面积 | 国产化快速切换 |
| **PD分离就绪** | Prefill/Decode节点共用机箱 | 少量结构设计 | 2027年PD分离升级 |

---

## 十、总结：从"设计一台服务器"到"设计一个AI计算系统"

### 10.1 范式转变小结

```text
传统设备制造商定义:
  "我的服务器支持8张GPU、24个DIMM、4个PCIe槽"

AI Workload 定义:
  "这个系统以最优效率运行671B MoE推理，
   Prefill吞吐 5000 tok/s, Decode延迟 < 50ms,
   总TCO < $X/百万token"

设计起点从"规格"变为"效率指标"
```

### 10.2 核心能力要求

| 传统设计团队 | AI 时代需要 |
|:------------|:-----------|
| 硬件工程师 + 散热工程师 | + 模型架构师 (理解计算特性) |
| BIOS/UEFI工程师 | + 分布式系统工程师 (NCCL/PD调度) |
| 测试工程师 | + AI性能验证工程师 (MFU/TGS/利用率) |
| 采购/供应链 | + 模型适配团队 (模型×硬件适配) |

### 10.3 最终推荐：三级并行设计策略

```text
+---------------------------------------------+
|  短期 (2026): 紧跟NVIDIA路线                |
|  - NVL72/Vera Rubin形态                     |
|  - 液冷标配，800V供电预留                    |
|  - 双轨设计(NVIDIA+国产备用)                 |
|  - Focus: BOM成本控制 + 供应链管理            |
|                                              |
|  中期 (2027-2028): 开放标准 + 场景分化        |
|  - UALink/CXL开放生态参与                    |
|  - PD分离硬件部署                            |
|  - 推理专用GPU评估                           |
|  - Focus: 生态选择 + 差异化能力               |
|                                              |
|  长期 (2029-2030): 全栈自研 + 光互联         |
|  - Chiplet设计能力建立                        |
|  - 光互联/CPO预研                           |
|  - DSX OS级别全栈软件栈                     |
|  - Focus: 架构定义 + 生态主导权               |
+---------------------------------------------+
```

---

> **关联文档**: [`2026-06-26-gpu-chip-design-analysis.md`](../../02_rd/04_chip/base/2026-06-26-gpu-chip-design-analysis.md) · `server-hardware/2026-07-06-server-design-methodology-framework.md` · `cluster-training/2026-06-26-pd-disaggregation-deployment.md` · `cluster-training/2026-06-26-kvcache-architecture-evolution.md` · `distributed-os/2026-06-04-multi-gpu-collective-communications.md`
> **证据基础**: 80+ arXiv论文 (详见各专题跟踪) · 15+ 工业进展 (NVIDIA/AMD/Intel/华为) · 20+ 篇行业分析 (DIGITIMES/TrendForce)
> **最后更新**: 2026-06-11

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- [`2026-06-26-gpu-chip-design-analysis.md`](../../02_rd/04_chip/base/2026-06-26-gpu-chip-design-analysis.md) — 关联

### 外部资料引用

- (无)

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
