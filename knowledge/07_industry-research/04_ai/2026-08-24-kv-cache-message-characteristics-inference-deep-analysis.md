# 推理场景 KV Cache 报文特征深度分析：报文长度 × 发送频率 × 典型组件建模

> **元信息**：知识库深度分析 | 归档：`07_industry-research/04_ai/`
> **版本**：v1.0
> **日期**：2026-08-24
> **触发**：用户要求针对推理场景，对 KV Cache 的报文特征（报文长度、报文发送频率）做深度分析，并针对大模型与典型组件（GPU/NVLink/PCIe/CXL/RDMA/存储）建立建模分析。
> **核心问题**：KV Cache 数据在互联链路上以什么粒度（报文长度）、什么速率（报文频率）流动？如何针对大模型与典型组件建立可复用的量化模型？
> **概要**: 本文从"KV Cache 数据在互联链路上以什么粒度、什么速率流动"出发，建立报文级流量模型。核心结论：KV 报文呈**双峰分布**——稳态写路径是"小报文高频"（每 decode step 产生 KB~几十 KB 分片），事件读/迁移路径是"大报文低频"（每请求/每 block 传输 MB~GB 级）；TP 并行域内 KV 留在本地分片（NVLink 主要承载激活报文），KV 报文真正的主战场是 PD 分离传输、CPU/NVMe offload 与分布式 KV 池。五层组件（HBM→NVLink→PCIe/CXL→RDMA→NVMe）的报文长度跨 4 个数量级（32B flit → GB 级消息），报文频率跨 6 个数量级（0.01 Hz prestage → 10⁴ msg/s TP 集合通信），这一"长度×频率"不对称性是推理网络与存储系统设计的第一约束。
> **关键词**: KV Cache · 报文特征 · message size · message rate · PD 分离 · NVLink · PCIe · CXL · RDMA · offload · TP 并行

## 目录

- [1. 引言与范围](#1-引言与范围)
  - [1.1 为什么聚焦报文级特征](#11-为什么聚焦报文级特征)
  - [1.2 与既有文档的边界](#12-与既有文档的边界)
- [2. KV Cache 报文特征的第一性原理](#2-kv-cache-报文特征的第一性原理)
  - [2.1 三个数据粒度：token / block / request](#21-三个数据粒度token--block--request)
  - [2.2 每 token KV 字节模型（GQA / MLA / 量化）](#22-每-token-kv-字节模型gqa--mla--量化)
  - [2.3 三类流量方向：写 / 读 / 迁移](#23-三类流量方向写--读--迁移)
  - [2.4 报文长度 × 报文频率的守恒关系](#24-报文长度--报文频率的守恒关系)
- [3. 典型组件链路建模](#3-典型组件链路建模)
  - [3.1 组件 0：GPU HBM↔SM（片内基线）](#31-组件-0gpu-hbmsm片内基线)
  - [3.2 组件 1：NVLink / NVSwitch（TP 域内）](#32-组件-1nvlink--nvswitchtp-域内)
  - [3.3 组件 2：PCIe / CXL（host offload 与内存池）](#33-组件-2pcie--cxlhost-offload-与内存池)
  - [3.4 组件 3：RDMA 网络（PD 分离 / 分布式 KV）](#34-组件-3rdma-网络pd-分离--分布式-kv)
  - [3.5 组件 4：NVMe 存储（远端 offload）](#35-组件-4nvme-存储远端-offload)
  - [3.6 组件报文特征总表](#36-组件报文特征总表)
- [4. 报文长度建模](#4-报文长度建模)
  - [4.1 逻辑消息 vs 物理报文（协议 MTU 切分）](#41-逻辑消息-vs-物理报文协议-mtu-切分)
  - [4.2 各链路报文长度公式与数值表](#42-各链路报文长度公式与数值表)
  - [4.3 报文长度分布特征：双峰与长尾](#43-报文长度分布特征双峰与长尾)
- [5. 报文发送频率建模](#5-报文发送频率建模)
  - [5.1 频率的三个驱动源](#51-频率的三个驱动源)
  - [5.2 稳态流频率：decode 写 + TP 集合通信](#52-稳态流频率decode-写--tp-集合通信)
  - [5.3 事件流频率：prestage / swap / migration](#53-事件流频率prestage--swap--migration)
  - [5.4 长度 × 频率聚合带宽闭合验证](#54-长度--频率聚合带宽闭合验证)
- [6. 典型大模型场景数值实例](#6-典型大模型场景数值实例)
  - [6.1 场景 A：8×H100 单机 TP=8，LLaMA-3 70B 短对话](#61-场景-a8h100-单机-tp8llama-3-70b-短对话)
  - [6.2 场景 B：PD 分离集群，70B 长上下文](#62-场景-bpd-分离集群70b-长上下文)
  - [6.3 场景 C：DeepSeek-V3（MLA + MoE）推理集群](#63-场景-cdeepseek-v3mla--moe推理集群)
  - [6.4 场景 D：GB200 NVL72 超节点推理](#64-场景-dgb200-nvl72-超节点推理)
  - [6.5 场景对比矩阵](#65-场景对比矩阵)
- [7. 工程启示](#7-工程启示)
  - [7.1 对互联选型](#71-对互联选型)
  - [7.2 对网卡 / 交换机 / 协议栈](#72-对网卡--交换机--协议栈)
  - [7.3 对推理引擎与调度](#73-对推理引擎与调度)
  - [7.4 监控与容量规划](#74-监控与容量规划)
- [8. 结论](#8-结论)
- [参考文献](#参考文献)
- [变更记录](#变更记录)

---

## 1. 引言与范围

### 1.1 为什么聚焦报文级特征

推理系统的瓶颈演进路径：

```text
Phase1 (2022-2023): Compute wall    -> model too big to run          -> fix: quantization/distillation
Phase2 (2024-2025): Memory wall     -> KV Cache overflow             -> fix: GQA/MLA/PagedAttention
Phase3 (2025-2026): Bandwidth wall  -> data cannot move (HBM/link)   -> fix: tiered cache / PD split / offload
Phase4 (now):       Message wall    -> message granularity mismatch  -> open: small-msg aggregation / flow ctrl
```

前三个阶段讨论的是"多少字节"（带宽总量），本文讨论的是"字节怎么切、多快发一次"（报文长度 × 报文频率）。二者的工程意义不同：

| 维度 | 带宽总量视角 | 报文特征视角 |
|:-----|:------------|:------------|
| 关注点 | 每秒多少 GB | 每个消息多大、每秒多少个消息 |
| 决定因素 | KV 总量 × 频率 | 数据粒度 + 分片 + 协议 MTU + 事件模式 |
| 影响对象 | 链路速率选型 | 网卡 pps 能力、交换机 buffer、协议开销、调度策略 |
| 典型问题 | 400G 够不够 | 小报文打不满带宽 / 大报文阻塞小报文 / pps 超限 |

关键事实：**同一条链路上，KV Cache 流量不是均匀的字节流，而是"少数大消息 + 海量小消息"的双峰混合体**。300 个 4KB 物理包组成一个 1.2 MB 的 block 消息，与 300 个独立 4KB 小消息，对网卡的 pps（packets per second）压力和交换机 buffer 的需求完全不同。

### 1.2 与既有文档的边界

- [KV Cache 带宽与延迟第一性原理](../../03_AI/llm-techniques-principles/2026-07-07-kv-cache-bandwidth-latency-deep-dive.md) 回答"**多少字节、多快**"（HBM 带宽视角，KV 在 GPU 内部）
- [推理内存前沿五件套](../02_rd/02_project/01_superpod/2026-08-13-kv-cache-frontier-oasiskv-kvgov-spectra-cdb-deep-analysis.md) 回答"**KV 怎么分层搬运/压缩**"（系统机制视角）
- [推理上下文内存存储](../../02_rd/01_product/00_hardware/06_storage/kv-cache/2026-06-26-inference-context-memory-storage.md) 回答"**KV 存哪里**"（存储层级视角）
- **本文**回答"**KV 在链路上怎么切、多快发**"（报文/消息粒度视角，覆盖 HBM→NVLink→PCIe/CXL→RDMA→NVMe 全链路）

适用读者：服务器互联架构师、推理系统工程师、网络/存储方案选型者。

---

## 2. KV Cache 报文特征的第一性原理

### 2.1 三个数据粒度：token / block / request

KV Cache 的报文长度不连续，由三个离散的"原子粒度"决定，分别对应三种流量方向：

```text
+------------------------------------------------------------------+
|                       KV Cache 三粒度金字塔                        |
|                                                                  |
|            +---------------------+                               |
|            |  REQUEST 级 (GB)    |  <-- 迁移/PD分离/prestage     |
|            |  完整上下文 KV       |      一次请求的全部历史        |
|            +----------+----------+                               |
|                       |                                          |
|            +----------+----------+                               |
|            |  BLOCK 级 (MB)      |  <-- offload/预取/换入换出    |
|            |  管理/搬运最小单元   |      PagedAttention 16-512t   |
|            +----------+----------+                               |
|                       |                                          |
|            +----------+----------+                               |
|            |  TOKEN 级 (KB)      |  <-- decode 稳态写路径        |
|            |  每步新增 K/V       |      每 decode step 产生      |
|            +---------------------+                               |
+------------------------------------------------------------------+
```

| 粒度 | 定义 | 典型大小（70B FP16） | 典型大小（8B FP16） | 对应流量方向 |
|:-----|:-----|:-------------------:|:-------------------:|:-------------|
| **token 级** | 1 个 token 的 K+V | 320 KB | 128 KB | decode 写增量 |
| **block 级** | PagedAttention 管理单元（16/32/512 tokens） | 5 / 10 / 160 MB | 2 / 4 / 64 MB | offload、预取、swap |
| **request 级** | 完整上下文（T tokens） | T×320 KB（T=32K → 10 GB） | T×128 KB（T=32K → 4 GB） | PD 分离、migration |

> **第一性原理**：KV 报文长度 = 原子粒度 × 每 token KV 字节。粒度选择是"管理开销 vs 传输效率"的权衡：token 级最灵活但报文太小（KB 级打不满链路）；request 级最粗但一次性占用大带宽窗口；block 级是二者的折中，也是当前推理引擎（vLLM PagedAttention）与分布式 KV 池（Mooncake）共同的选择。 [来源: 知识库 kv-cache-bandwidth-latency-deep-dive 文档]

### 2.2 每 token KV 字节模型（GQA / MLA / 量化）

$$Bytes_{per\_token} = c \times L \times H_{kv} \times d_{head} \times \text{dtype\_bytes}$$

其中 $c=2$（K+V 两组）对 MHA/GQA；MLA 的 K/V 共享 latent，$c=1$。

| 模型 | 注意力架构 | L | H_kv | d_head | dtype | KV/token | 相对 70B 基线 |
|:-----|:----------|:--:|:----:|:------:|:-----:|:--------:|:-------------:|
| LLaMA-3 70B | GQA 8:1 | 80 | 8 | 128 | FP16 | **320 KB** | 1× |
| LLaMA-3 70B | GQA 8:1 | 80 | 8 | 128 | FP8 | **160 KB** | 0.5× |
| LLaMA-3 8B | GQA 8:1 | 32 | 8 | 128 | FP16 | **128 KB** | 0.4× |
| DeepSeek-V3 | MLA (d_c=576) | 60 | — | 576 | FP16 | **67.5 KB** | 0.21× |
| OPT-66B | MHA 64 | 64 | 64 | 128 | FP16 | **2 MB** | 6.4× |

> 注：OPT-66B 为 MHA（无 GQA），KV/token = 2×64×64×128×2 = 2 MB，是 GQA 模型的 6 倍+。这解释了为何 DistServe 论文中 OPT-66B 512-token 请求的 KV 达 1.13 GB（512 × 2 MB ≈ 1 GB，与论文一致）。 [来源: DistServe arXiv:2401.09670]

**量化影响**：FP8 减半、INT4 减到 1/4。报文长度随 dtype 线性缩放，这是 offload 场景最重要的杠杆。

### 2.3 三类流量方向：写 / 读 / 迁移

| 方向 | 触发时机 | 报文粒度 | 关键路径 | 容忍延迟 |
|:-----|:---------|:---------|:---------|:---------|
| **写（W）** | 每 decode step 生成新 token 的 K/V | token 级（KB） | ❌ 可异步 | ~10 ms（step 间隔） |
| **读（R）** | attention 需要访问 KV（本地命中/远端 miss） | block 级（MB） | ✅ 阻塞 decode | 10-100 μs |
| **迁移（M）** | prestage、swap、负载均衡 | request 级（GB） | ⚠️ 可预取 | 100 ms 级（窗口内） |

三方向的不对称性（与 [kv-cache 远程读取分析](../../03_AI/llm-techniques-principles/2026-07-07-kv-cache-bandwidth-latency-deep-dive.md) §10 结论一致，此处从报文视角重述）：

- **报文长度**：写 = token 级（320 KB）；读 = block 级（5-160 MB）；迁移 = request 级（GB）→ 跨度 4 个数量级
- **报文频率**：写 = 每 step 一次（100 Hz 级）；读 = 事件驱动（<1% miss 时低频）；迁移 = 秒级-分钟级
- **延迟预算**：写可异步；读必须在 1 个 ITL 内返回；迁移要在 prefill/调度窗口内完成

> **核心不对称**：KV 的**写**是"小报文高频"（每次只写 1 个新 token），**读/迁移**是"大报文低频"（一次读回全部历史）。单次读取量是单次写入量的 30,000-130,000×（T=32K-128K） [来源: 知识库 kv-cache-bandwidth-latency-deep-dive 文档 §10.1]。

### 2.4 报文长度 × 报文频率的守恒关系

对任意链路，聚合带宽 = 报文长度 × 报文频率（取均值）：

$$BW_{link} = \overline{MsgSize} \times MsgRate \times \text{(利用率系数)}$$

工程设计中的自由度为：**同一带宽需求可以拆成"大报文低频"或"小报文高频"**。但两种形态对系统的影响截然不同：

| 形态 | 例子 | 优点 | 代价 |
|:-----|:-----|:-----|:-----|
| 大报文低频 | request 级 KV 迁移 | 带宽利用率高（RDMA 大消息吞吐接近线速） | 突发占用带宽窗口，阻塞其他流量；延迟敏感 |
| 小报文高频 | decode 每 step KV 写 | 延迟低、粒度细 | 协议头开销占比高；网卡 pps 压力；带宽利用率低 |

**报文墙的本质**：KV 流量天然要求"小报文高频地写 + 大报文低频地读"，而单条链路很难同时完美适配两种模式——这正是推理场景互联设计（而非训练场景）独有的挑战。

---

## 3. 典型组件链路建模

### 3.1 组件 0：GPU HBM↔SM（片内基线）

- **角色**：KV Cache 的主驻地；decode 每步 attention 读取全量 KV
- **传输单元**：cache line（64B）/ 缓存行簇（128B）；非报文语义，但定义了 KV 读的频率上限
- **报文长度**：64-128 B（HBM 突发粒度）
- **报文频率**：每 decode step 读 B×T 个 token 的 KV；以 70B、T=32K、B=16、ITL=10 ms 为例，每 step 读 16×10 GB = 160 GB → 相当于 1.6 TB/s 的 HBM 读流（接近 H100 的 3.35 TB/s 上限的 48%）[来源: 知识库 kv-cache-bandwidth-latency-deep-dive 文档]
- **物理限制**：ITL ≥ KV_Size/HBM_BW（无法通过软件绕过）

> **建模意义**：HBM 定义了 KV 读频率的物理时钟。所有外移（offload/远端）都是在"读"这一侧引入额外跳数，必须以不超 ITL 预算为前提。

### 3.2 组件 1：NVLink / NVSwitch（TP 域内）

- **角色**：GPU 域内高速互联，承载 TP 并行的集合通信 + KV 迁移
- **协议粒度**：flit = 32 B（NVLink 4/5/6），packet = 多 flit（典型 256 B-1 KB 数据包）[来源: NVIDIA NVLink 架构公开资料]
- **带宽**：NVLink 4（H100）900 GB/s/GPU、NVLink 5（B200）1.8 TB/s/GPU、NVLink 6（Rubin）3.6 TB/s/GPU [来源: NVIDIA NVLink 官网]

**TP 并行下 KV 报文的真实分布**（关键澄清）：

标准 TP 实现（如 Megatron 风格）中，KV Cache **按层按 head 分片**驻留在各 rank，decode 时每 rank 只读本地分片 → **常规 decode 不产生跨 rank 的 KV 报文**。NVLink 上每层 2 次集合通信（QKV AllGather + attention 输出 AllReduce）承载的是**激活报文**而非 KV 报文：

| 通信 | 载荷 | 报文长度（70B, TP=8, B=16, hidden=8192, FP16） | 频率 |
|:-----|:-----|:---------------------------------------------|:-----|
| QKV AllGather | 激活（QKV 投影输出） | 3×8192×16×2 / 8 ≈ 98 KB/rank | 每层每 step |
| Attn 输出 AllReduce | 激活（attention 输出） | 8192×16×2 / 8 ≈ 33 KB/rank | 每层每 step |
| **KV 迁移**（负载均衡/context migration） | KV Cache 分片 | T×320KB/TP（T=32K → 1.25 GB） | 事件驱动 |

**KV 报文出现在 NVLink 上的场景**：
1. **KV Cache 迁移**：请求在 GPU 间迁移（负载均衡、GPU 故障恢复），报文 = 该请求的完整 KV 分片
2. **KV 冗余广播**：某些实现（如 Ring Attention 的 decode 变体、或 KV head 分片与 Q 分片错位的配置）需要跨 rank 广播 K/V
3. **MLA latent 广播**：DeepSeek 系 MLA 模型在 TP 下需要广播低维 latent（每 token 仅 576×2 B = 1.1 KB/rank，报文很小）

> **结论**：NVLink 域内，KV 报文以"低频大块迁移"为主、激活报文以"高频小消息"为主。TP 并行度越高，每 rank KV 分片越小，KV 迁移报文越短（与 TP 成反比）。

### 3.3 组件 2：PCIe / CXL（host offload 与内存池）

- **角色**：GPU↔CPU 的 KV offload 通道；CXL 内存池作为温 KV 缓存层
- **协议粒度**：PCIe TLP 最大 4096 B（MPS/MRRS 可配 512 B-4 KB）[来源: PCI-SIG 规范]；CXL 3.0 FLIT = 528 B（16 B 头 + 512 B 负载）[来源: CXL 3.0 规范]
- **带宽**：PCIe Gen5 x16 = 64 GB/s（双向）、Gen6 x16 = 128 GB/s；CXL 内存池单通道 ~64 GB/s

**KV offload 报文建模**（70B FP16，PagedAttention block=16 tokens）：

| 参数 | 数值 | 计算 |
|:-----|:-----|:-----|
| block KV 大小 | 5 MB | 16 × 320 KB |
| PCIe TLP 数/block | 1,280 | 5 MB / 4 KB |
| 单 step 写增量 | 320 KB | 1 token |
| 写频率（B=16, ITL=10ms） | 100 Hz | 1/ITL |
| 写带宽 | 32 MB/s = 0.26 Gbps | 320 KB × 100 Hz |
| 读回带宽（Prestage 突发） | 64 GB/s 封顶 | 5 MB block / 78 μs |

> 关键量级：**KV offload 的稳态写带宽极低（~0.26 Gbps/GPU）**，但**突发读回可瞬时打满 PCIe（64 GB/s）**。PCIe 链路 99% 时间空闲、1% 时间打满——这正是"大报文低频读"形态的典型写照。 [来源: 基于知识库 kv-cache-bandwidth-latency-deep-dive 文档 §10 数值推导]

**CXL 内存池**：KV 以 cacheline（64 B）粒度访问，但软件层（如远端 KV 引擎）以 block 粒度读写 → 实际报文仍是 MB 级块传输，CXL 的 528 B FLIT 只是传输层切分。

### 3.4 组件 3：RDMA 网络（PD 分离 / 分布式 KV）

- **角色**：跨节点 KV 传输的主通道：PD 分离（prefill→decode）、分布式 KV 池（Mooncake 风格）、prestage
- **协议粒度**：RoCE/IB 物理包 MTU 256 B-4 KB [来源: IBTA 规范]；RDMA 逻辑消息可达 MB 级（scatter-gather 多段）
- **带宽**：400 Gbps（50 GB/s）/ 800 Gbps（100 GB/s）[来源: 知识库超节点文档]

**KV 报文建模**：

| 场景 | 逻辑消息 | 报文长度 | 物理包数（4KB MTU） | 频率 | 带宽需求 |
|:-----|:---------|:---------|:-------------------:|:-----|:---------|
| PD 分离（70B, T=32K） | request 级 KV | 10 GB（分块传输） | 2.6M | 请求率 rps | 10 GB × rps |
| PD 分离（DistServe 实测：OPT-66B, 512t） | request 级 KV | 1.13 GB | 295K | 10 rps | **90 Gbps** [来源: DistServe arXiv:2401.09670] |
| 分布式 KV 池（Mooncake, block=512t） | block 级 KV | 160 MB（70B） | 41K | 事件驱动 | — |
| Prestage（70B, T=32K, 500ms 窗口） | request 级 KV | 10 GB | 2.6M | 2 Hz | **160 Gbps/GPU** |

> Mooncake 实测环境为 8×A800 + 800 Gbps RDMA，KV 经 GPUDirect RDMA 以**层级别流式**传输（每层算完即传），单 block（512 tokens）在 70B 模型下约 160 MB [来源: Mooncake arXiv:2407.00079]。

**RDMA 小报文问题**：decode 稳态写（每 step 320 KB/rank）在 800G 链路上只有 0.4% 利用率——如果不做聚合，纯小报文写会把 pps 打到 25K msg/s 以上，且带宽利用率极低。工程上必须**批量聚合**（攒多个 step 或跨请求合并）或**走异步 offload**。

### 3.5 组件 4：NVMe 存储（远端 offload）

- **角色**：最冷 KV 的落地层；block miss 时的读回源
- **协议粒度**：NVMe 命令以 4 KB 扇区为最小单位，实际请求常用 16-64 KB 条带 [来源: NVMe 规范]
- **带宽/延迟**：PCIe Gen5 NVMe 顺序读 ~14 GB/s、随机读延迟 ~50-100 μs（远端经网络则 150-550 μs）[来源: 知识库 kv-cache-bandwidth-latency-deep-dive 文档 §10.4]

**报文建模**（OasisKV 场景：decode 期 KV 越 HBM 的稀疏预取）：

| 参数 | 数值 |
|:-----|:-----|
| 预取粒度 | block 级 5-10 MB |
| 单 block 读延迟（远端 NVMe） | 150-550 μs（P50-P99.9） |
| 对 ITL（10 ms）影响 | 1.5-5.5% |
| miss 频率 | <1%（正常命中率下） |

> 存储链路的报文特征是**"低频、中块、延迟敏感"**——报文不大不小（MB 级），频率低（事件驱动），但延迟预算苛刻（必须 <1 个 ITL）。这与训练场景（checkpoint 大块顺序写）截然不同。

### 3.6 组件报文特征总表

| 组件 | 传输单元 | 报文长度 | 频率量级 | 流量形态 | 对 KV 的角色 |
|:-----|:---------|:---------|:---------|:---------|:-------------|
| HBM↔SM | cache line | 64-128 B | 10³-10⁴ Hz | 稳态流 | KV 主驻地（读） |
| NVLink | flit/packet | 32 B-1 KB（物理）；KB-GB（逻辑消息） | 10²-10⁴ msg/s | 高频小消息（激活）+ 低频大块（KV 迁移） | TP 域内 KV 迁移 |
| PCIe/CXL | TLP/FLIT | 4 KB/528 B（物理）；MB（block 逻辑消息） | 10² Hz 写；突发读 | 稳态小写 + 突发大读 | KV offload/内存池 |
| RDMA | 包/消息 | 4 KB 物理；MB-GB 逻辑消息 | 10⁰-10² msg/s | 大报文低频 + 流式分块 | PD 分离/分布式 KV |
| NVMe | 扇区/条带 | 4-64 KB；MB（block 预取） | 10⁰ Hz | 事件驱动中块 | 冷 KV 落地 |

> **跨组件规律**：从片内到片外，报文长度增大（128 B → GB）、报文频率降低（10⁴ → 10⁰ Hz），"长度×频率"的乘积（带宽）在各层间递减但有数量级跳变——片内 TB/s、域内 GB/s、跨节点 100 GB/s、存储 14 GB/s。

---

## 4. 报文长度建模

### 4.1 逻辑消息 vs 物理报文（协议 MTU 切分）

必须区分两个概念：

```text
Logical Message:  semantic unit of one KV data transfer
                  = granularity x bytes_per_token x (1/TP shard)
Physical Packet:  minimum encapsulation unit on the link
                  = MTU / TLP / FLIT / packet (protocol-defined)
Splitting:        logical message -> N physical packets (N = MsgSize / MTU)
```

| 链路 | 逻辑消息粒度 | 物理报文上限 | 头开销 |
|:-----|:------------|:------------|:-------|
| NVLink | 256 B-1 KB packet | 32 B flit | ~10% |
| PCIe | 512 B-4 KB TLP | 4 KB（MPS） | ~5%（TLP 头） |
| CXL 3.0 | 528 B FLIT | 512 B 负载 | 3% |
| RoCE/IB | 4 KB MTU 包 | 4 KB | ~2%（+以太网帧头） |
| RDMA 消息 | 任意（scatter-gather） | 拆为多个 4 KB 包 | 摊销后可忽略 |

> **工程含义**：KV 逻辑消息（KB-MB-GB）远大于物理报文（≤4 KB），传输层切分后头开销可摊销。真正的问题是**逻辑消息本身的粒度**——若逻辑消息只有 KB 级（token 级写），则 4 KB 包只有 1 个 MTU 长，头开销占比骤升且 pps 需求暴涨。

### 4.2 各链路报文长度公式与数值表

**通用公式**：

$$MsgSize_{KV} = \underbrace{Granularity}_{token/block/request} \times \underbrace{Bytes_{per\_token}}_{§2.2} \times \frac{1}{TP} \times \underbrace{dtype\_scale}_{FP8:0.5, INT4:0.25}$$

**数值表**（70B GQA FP16 = 320 KB/token；8B = 128 KB/token；DSV3 MLA = 67.5 KB/token）：

| 粒度 | 分片 | 70B FP16 | 70B FP8 | 8B FP16 | DSV3 FP16 |
|:-----|:----:|:--------:|:-------:|:-------:|:---------:|
| token（无分片） | 1 | 320 KB | 160 KB | 128 KB | 67.5 KB |
| token（TP=8） | 1/8 | 40 KB | 20 KB | 16 KB | 8.4 KB |
| block 16t（TP=1） | 1 | 5 MB | 2.5 MB | 2 MB | 1.05 MB |
| block 32t（TP=1） | 1 | 10 MB | 5 MB | 4 MB | 2.1 MB |
| block 512t（Mooncake） | 1 | 160 MB | 80 MB | 64 MB | 33.8 MB |
| request T=4K | 1 | 1.25 GB | 625 MB | 512 MB | 270 MB |
| request T=32K | 1 | 10 GB | 5 GB | 4 GB | 2.2 GB |
| request T=32K | 1/8 | 1.25 GB | 625 MB | 512 MB | 270 MB |

> **可操作结论**：
> 1. **dtype 是报文长度的第一杠杆**（FP8 直接减半），先于任何网络优化
> 2. **TP 分片使 KV 迁移报文缩短**，但 PD 分离传输通常发生在**逻辑完整模型**之间（TP 组内聚合后传输），分片收益有限
> 3. **MLA 将 block 级报文压缩到 1-2 MB**，使 NVMe 随机读的延迟占比显著下降——架构级压缩对报文友好的效果大于任何协议优化

### 4.3 报文长度分布特征：双峰与长尾

```text
Message length distribution (log x-axis, schematic)
frequency
 ^
 |          *                              *
 |         * *                            * *
 |        *   *                          *   *
 |       *     *                        *     *
 |      *       *                      *       *
 |     *         *                    *         *
 |    *           *                  *           *
 |   *             *                *             *
 +---*----+--------*----+----------*----+--------*---> length(log)
    4KB   |        KB   |          MB   |        GB
  (phy pkt)    (token write)      (block)      (request)
  Peak1: high-freq small       Peak2: low-freq large
  decode write path            PD-split / migration path
```

| 峰 | 位置 | 频率特征 | 成因 | 承载链路 |
|:---|:-----|:---------|:-----|:---------|
| 峰 1 | KB 级（16-320 KB） | 高频（10²-10⁴ msg/s） | decode 每 step KV 写、TP 激活通信 | NVLink、PCIe、RDMA（小消息） |
| 峰 2 | MB-GB 级（5 MB-10 GB） | 低频（10⁰-10¹ msg/s） | block 预取、PD 分离、prestage | RDMA、NVMe、NVLink（迁移） |
| 尾 | 64 B-4 KB（物理包） | 随消息内切分 | 协议 MTU 切分 | 所有链路 |

> **双峰的本质**：两个峰分别对应 KV 的"增量产生"（写）与"存量消费"（读/迁移）。推理系统所有流量整形（batching、prefetch、chunking）本质上都是在两个峰之间调配报文粒度，使它们适配链路的最优消息区间。

---

## 5. 报文发送频率建模

### 5.1 频率的三个驱动源

| 驱动源 | 时钟 | 特征 | 典型频率 |
|:-------|:-----|:-----|:---------|
| **decode step 时钟** | 1/ITL | 周期稳定，随 B×T 缩放 | 20-300 Hz |
| **请求到达率** | rps | 泊松/突发，决定 PD 分离传输频率 | 1-100 rps |
| **事件驱动** | 调度/容量 | prestage、swap、migration、block miss | 0.01-10 Hz |

三类驱动源叠加产生 KV 报文的完整频谱。

### 5.2 稳态流频率：decode 写 + TP 集合通信

**decode 写频率**（token 级 KV 报文）：

$$f_{write} = \frac{B_{batch}}{ITL} = B \times \frac{1}{ITL}$$

| B | ITL=5 ms | ITL=10 ms | ITL=50 ms |
|:-:|:--------:|:---------:|:---------:|
| 1 | 200 Hz | 100 Hz | 20 Hz |
| 16 | 3.2 kHz | 1.6 kHz | 320 Hz |
| 64 | 12.8 kHz | 6.4 kHz | 1.28 kHz |

**TP 集合通信频率**（激活报文，NVLink 域内；非 KV 但同频共存）：

$$f_{TP} = 2 \times L \times \frac{1}{ITL} \times B \text{(按 rank)}$$

| 模型 | L | ITL=10ms, B=16 | 报文率/rank |
|:-----|:--:|:--------------:|:-----------:|
| 70B | 80 | 2×80×100 = | **16,000 msg/s** |
| 8B | 32 | 2×32×100 = | 6,400 msg/s |

> 16K msg/s 对 NVLink 域内（900 GB/s）毫无压力，但若 TP 跨节点（需 RDMA），16K msg/s × 98 KB/rank ≈ 1.57 GB/s/rank 的激活流量会让 400G 链路的 pps 吃紧——**这正是 TP 不应跨节点（尤其跨机架）的报文级原因**。

### 5.3 事件流频率：prestage / swap / migration

| 事件 | 触发条件 | 单次报文量（70B T=32K） | 频率 | 聚合带宽 |
|:-----|:---------|:------------------------|:-----|:---------|
| Prestage 预加载 | 新请求进入 decode 前 | 10 GB | 2 Hz（500ms 窗口） | 160 Gbps/GPU |
| Context swap | HBM 容量不足逐出/换入 | 10 GB（写）+10 GB（读） | 1-10 次/s | 200-1,000 GB/s 瞬时 |
| GPU migration | 负载均衡/故障 | 1.25 GB（TP=8 分片） | 0.1-1 Hz | 32 GB/s（PCIe 域） |
| Block miss | PagedAttention 冷块 | 5-10 MB | <1% 概率 | 4 GB/s 单次 |

> **突发性量化**：prestage 单次 10 GB 在 400G 链路上需 200 ms（50 GB/s），占满整条链路；若多 GPU 同时 prestage，节点级需求可达 320-640 Gbps——**超过单口 400G 极限**，必须错峰调度 [来源: 知识库 kv-cache-bandwidth-latency-deep-dive 文档 §10.3]。

### 5.4 长度 × 频率聚合带宽闭合验证

以 PD 分离集群（70B, T=32K, 10 rps）为例验证闭合：

| 流量分量 | 报文长度 | 报文频率 | 带宽 | 占比 |
|:---------|:---------|:---------|:-----|:-----|
| PD 分离 KV 传输 | 10 GB（分块） | 10 rps | 100 GB/s = **800 Gbps** | 83% |
| decode 稳态 KV 写（远端） | 320 KB | 100 Hz × 16 | 0.5 GB/s = 4 Gbps | 3% |
| Prestage（25% 请求预取） | 10 GB | 2.5 Hz | 25 GB/s = 200 Gbps | 17% |
| 其他（控制面/心跳） | — | — | <1 Gbps | <1% |
| **合计** | — | — | **~1,000 Gbps** | 100% |

> **闭合验证**：报文长度 × 报文频率的乘积与带宽总量模型一致（10 GB × 10 rps = 100 GB/s），同时揭示了**带宽由哪个报文分量主导**——本例中 PD 分离的大报文低频传输占 83%，decode 稳态写只占 3%。这回答了"带宽预算应该花在哪里"：**优化大报文传输的效率和调度（而非小报文）是 PD 分离架构的第一优先**。 [来源: DistServe 论文 90 Gbps 例子的扩展推导]

---

## 6. 典型大模型场景数值实例

### 6.1 场景 A：8×H100 单机 TP=8，LLaMA-3 70B 短对话

**配置**：8×H100 80GB（NVLink 4，900 GB/s/GPU）、TP=8、B=16、T=4K、ITL=10 ms、FP16

| 链路 | 报文 | 长度 | 频率 | 带宽/利用率 |
|:-----|:-----|:-----|:-----|:-----------|
| HBM | KV 读 | 1.25 GB/step（16×1.25GB=20GB） | 100 Hz | 2 TB/s（60% HBM） |
| NVLink | 激活 AllGather/AllReduce | 33-98 KB/rank | 16,000 msg/s | ~1.6 GB/s（0.2%） |
| NVLink | KV 迁移（罕见） | 156 MB（1.25GB/8） | 事件 | — |
| PCIe | KV offload（未启用） | — | — | 0 |

**结论**：单机 TP 场景 KV 报文几乎全部在 HBM 内部；NVLink 承载激活小报文（利用率 <1%）；KV 报文不出域。**报文压力全在片内带宽**，互联侧轻松。

### 6.2 场景 B：PD 分离集群，70B 长上下文

**配置**：prefill 池 + decode 池，800G RDMA，70B GQA FP8（160 KB/token）、T=32K、10 rps、KV=5 GB/请求

| 链路 | 报文 | 长度 | 频率 | 带宽 |
|:-----|:-----|:-----|:-----|:-----|
| RDMA（prefill→decode） | request 级 KV（分块） | 5 GB | 10 rps | 400 Gbps |
| RDMA（decode 稳态写回） | token 级 | 160 KB | 100 Hz×16 | 2 Gbps |
| RDMA（prestage） | request 级 | 5 GB | 2.5 Hz | 100 Gbps |
| NVLink（decode 域内 TP） | 激活 | 33-98 KB | 16,000 msg/s | — |

**结论**：PD 分离后 KV 报文成为 RDMA 链路的绝对主力（400 Gbps/10rps 单实例对）。FP8 将 KV 减半后，同一 800G 链路可支撑的 rps 翻倍——**dtype 选择直接决定 PD 分离的规模上限**。

### 6.3 场景 C：DeepSeek-V3（MLA + MoE）推理集群

**配置**：MLA（KV/token=67.5 KB）、60 层、EP=16（MoE 专家并行）、T=32K、KV=2.2 GB/请求

| 链路 | 报文 | 长度 | 频率 | 备注 |
|:-----|:-----|:-----|:-----|:-----|
| RDMA（PD 分离） | request 级 | 2.2 GB | 10 rps | **仅为 70B GQA 的 22%** |
| RDMA（MoE EP） | token 激活 | KB 级 | 每 token | 与 KV 报文竞争带宽 |
| NVLink/网络（MLA latent） | latent 广播 | 1.1 KB/rank | 每 step | 小报文高频 |

**结论**：MLA 将 KV 报文长度压缩 ~4.7×（vs GQA 70B），PD 分离传输带宽需求同比降低——**架构级 KV 压缩（MLA）是报文优化的终极手段**，效果超过一切系统级技巧 [来源: 知识库 kv-cache-bandwidth-latency-deep-dive 文档 §2.4]。

### 6.4 场景 D：GB200 NVL72 超节点推理

**配置**：72 GPU NVLink 5 全互联（1.8 TB/s/GPU，域内 130 TB/s）[来源: NVIDIA NVLink 官网]、KV 常驻域内 HBM（13.8 TB）、无 PD 分离

| 链路 | 报文 | 长度 | 频率 | 备注 |
|:-----|:-----|:-----|:-----|:-----|
| NVLink（TP=8/16） | 激活 | 33-98 KB | 16,000 msg/s | 域内充裕 |
| NVLink（KV 迁移） | KV 分片 | 156-625 MB | 事件 | 域内 1.8 TB/s 下 <1 ms |
| 域外 800G（跨 NVL72） | 仅聚合结果 | 小 | 低频 | KV 不出域 |

**结论**：超节点形态把 KV 报文"锁"在 NVLink 域内（带宽高 18× vs 800G），彻底消除 PD 分离的跨节点大报文。**这是 NVL72 在推理场景的报文级价值**：用域内带宽换掉域间 KV 流量。代价是域内 HBM 容量约束（KV 放不下时仍需 offload）。

### 6.5 场景对比矩阵

| 维度 | A: 单机 TP | B: PD 分离 | C: MLA+MoE | D: NVL72 |
|:-----|:----------|:----------|:-----------|:---------|
| KV 报文主战场 | HBM 内部 | RDMA 跨节点 | RDMA（KV+EP 混合） | NVLink 域内 |
| 报文长度峰值 | 1.25 GB（HBM 读） | 5-10 GB（PD 传输） | 2.2 GB | 625 MB（域内迁移） |
| 报文频率峰值 | 10⁴ msg/s（激活） | 10² msg/s（KV） | 10⁴ msg/s（EP） | 10⁴ msg/s（激活） |
| 带宽瓶颈 | HBM（60%） | RDMA（83% KV） | RDMA（KV 占比降） | 域内充裕/域间轻 |
| 报文优化杠杆 | 量化/dtype | FP8+错峰调度 | MLA 压缩 | 容量规划（KV 放不放得下） |
| 主要风险 | 长上下文 HBM 读 | prestage 突发打满链路 | EP 与 KV 争带宽 | KV 容量 → 被迫 offload |

---

## 7. 工程启示

### 7.1 对互联选型

1. **TP 不跨机架（报文级理由）**：TP 集合通信 16K msg/s × KB 级消息在域内（NVLink）无压力，跨节点则对 400G 链路 pps 形成挑战。TP 边界应严格落在 NVLink/域内互联内。
2. **PD 分离带宽按"大报文"规划**：KV 传输是 request 级大消息，链路需求 = KV_per_request × rps。选型公式：`链路带宽 ≥ KV_size × rps × (1+prestage余量)`。70B FP8 T=32K 10rps → ≥400G；20rps → 需 800G 或 2×400G 聚合。
3. **CXL 内存池适合做温 KV 层**：报文为 MB 级 block 读，CXL 的 64 GB/s 带宽 + 300-400 ns 延迟可覆盖 block miss 场景（<1% ITL 影响），且避免 RDMA 链路被 offload 流量污染。

### 7.2 对网卡 / 交换机 / 协议栈

1. **pps 预算按小报文峰计算**：decode 写 + TP 激活可能达 10⁴ msg/s/GPU 量级；网卡 pps 能力需按 `B×f_decode×TP×L×2` 核算，而非只看带宽。
2. **大报文突发需要交换机 buffer**：prestage 10 GB 突发在 400G 链路持续 200 ms，交换机需足够 buffer 吸收微突发（ECN/PFC 配合），否则丢包重传放大延迟。
3. **RDMA 消息聚合是必选项**：decode 稳态写（KB 级/step）必须聚合为 MB 级消息再发，否则带宽利用率 <5%。PD 分离系统应"攒 token 批量传输"或"层级别流式"（Mooncake 做法，与计算重叠）。
4. **优先级/QoS**：KV 读（block miss）延迟敏感（<1 ITL），应高于 prestage 等可预取流量的网络优先级——避免大报文阻塞小报文的关键路径。

### 7.3 对推理引擎与调度

1. **block 大小是报文粒度旋钮**：block=16t（5 MB）vs block=512t（160 MB）——小 block 灵活但报文多，大 block 效率高但浪费。分布式 KV 池（Mooncake 512t）与本地 PagedAttention（16-32t）应使用不同粒度。
2. **错峰调度（staggered prestage）**：多 GPU 同时 prestage 会超链路极限，调度器应打散 prestage 窗口（量化依据：节点级需求 320-640 Gbps vs 单口 400G）。
3. **PD 分离的 KV 传输与计算重叠**：层级别流式传输（每层算完即传）可把传输延迟完全隐藏，报文频率与 prefill 层计算频率对齐（Mooncake 实测有效）。
4. **FP8/INT4 是报文压缩的第一手段**：先量化再谈网络——FP8 直接减半所有 KV 报文的长度与带宽。

### 7.4 监控与容量规划

建议监控指标（按报文特征定制）：

| 指标 | 含义 | 告警阈值建议 |
|:-----|:-----|:------------|
| KV 报文长度分布（P50/P99） | 双峰形态是否健康 | 峰 1 无聚合（KB 级占比 >50%）→ 触发聚合优化 |
| msg/s（各链路） | 报文频率 | 超过网卡 pps 预算 70% |
| prestage 并发度 | 突发风险 | >25% 节点同时 prestage |
| KV 传输带宽占比 | PD 分离链路健康度 | >80% 且持续 → 扩容或降 KV 精度 |
| block miss 率 × 读延迟 | 冷 KV 读路径 | P99.9 > 5% ITL |

---

## 8. 结论

1. **KV 报文呈双峰分布**：decode 稳态写路径是 KB 级小报文高频（10²-10⁴ msg/s），PD 分离/迁移路径是 MB-GB 级大报文低频（10⁰-10¹ msg/s）。两个峰分别对应 KV 的"增量产生"与"存量消费"。

2. **报文长度由三层决定**：原子粒度（token/block/request）× 每 token KV 字节（架构 GQA/MLA × dtype）× TP 分片。MLA 压缩 4.7×、FP8 压缩 2×、TP=8 分片 8×——三者相乘可达 75× 报文缩短。

3. **报文频率由三源驱动**：decode step 时钟（1/ITL × B）、请求到达率（rps）、事件驱动（prestage/swap）。稳态频率可精确建模，突发频率需调度整形。

4. **TP 域内 KV 不出域**：常规 TP decode 的 KV 报文留在 HBM 分片内，NVLink 承载的是激活报文（16K msg/s 级）；KV 报文的真正主战场是 PD 分离传输、CPU/NVMe offload 与分布式 KV 池。

5. **大报文传输效率是 PD 分离第一优先**：带宽闭合验证显示 PD 分离 KV 传输占链路带宽 83%，decode 稳态写仅 3%。优化应聚焦大报文的调度、分块与重叠，而非小报文。

6. **报文视角的统一设计原则**：把"小报文聚合、大报文错峰、读路径优先、dtype 先压缩"作为推理互联与存储系统的四条设计约束，可同时解决带宽利用率与延迟 SLO 两个问题。

---

## 参考文件

### 内部知识库引用
- [KV Cache 对带宽与延迟的需求 — 第一性原理完整论证](../../03_AI/llm-techniques-principles/2026-07-07-kv-cache-bandwidth-latency-deep-dive.md) — KV 字节模型 / ITL / Roofline / 远程读取四场景
- [推理内存前沿五件套深度分析](../02_rd/02_project/01_superpod/2026-08-13-kv-cache-frontier-oasiskv-kvgov-spectra-cdb-deep-analysis.md) — OasisKV 块级预取 / SPECTRA 压缩 / 分层搬运
- [数据控制流与网络分区深度分析](../02_rd/02_project/01_superpod/2026-08-03-data-control-flow-and-network-partition-deep-analysis.md) — 超节点网络分区 / 400G-800G 链路
- [推理上下文内存存储](../../02_rd/01_product/00_hardware/06_storage/kv-cache/2026-06-26-inference-context-memory-storage.md) — KV 多级存储层级
- [服务器互联层次深度解析](../../02_rd/00_shared/01_architecture/2026-06-10-interconnect-hierarchy-deep-dive.md) — 六层互联协议粒度

### 外部资料引用
[1] Ruoyu Qin et al., "Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving", arXiv:2407.00079 (v4, 2025-09) — block=512t、800G RDMA、层级别流式传输、Kimi 负载特征
[2] Yinmin Zhong et al., "DistServe: Disaggregating Prefill and Decoding for Goodput-optimized LLM Serving", OSDI 2024, arXiv:2401.09670 — OPT-66B 512t KV=1.13GB、10rps→90Gbps 传输需求
[3] NVIDIA, "NVLink & NVLink Switch" 官方产品页 (2026) — NVLink 4/5/6 带宽 900/1800/3600 GB/s
[4] PCI-SIG, PCIe Base Specification — TLP 最大 4096 B
[5] CXL Consortium, CXL 3.0 Specification — FLIT 528 B
[6] IBTA, InfiniBand Architecture Specification / RoCE — MTU 256 B-4 KB
[7] NVMe 工作组, NVMe Base Specification — 4 KB 扇区最小粒度

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-24 | v1.0 | 首次创建：报文长度×频率×五组件建模，四场景数值实例，闭合验证 |
