# 🖥️ 三类 KV Cache 推理场景深度分析：负载形态决定机型

> **版本**: v1.0
> **日期**: 2026-08-11
> **核心问题**: LLM 推理的 KV Cache 管理如何按负载形态分为三类场景？每类场景的业务特性、量化数据推导、以及对应的服务器机型设计要点是什么？
> **概要**: 本文按「驱动因素」将 KV Cache 推理场景 MECE 划分为三类：**场景 A 单请求长上下文（容量驱动）**、**场景 B 高并发短请求（吞吐驱动）**、**场景 C MoE 动态路由（结构驱动）**。对每类场景回答四个问题：业务场景长什么样 → 业务特性是什么 → KV 数据如何从第一性原理推导 → 服务器机型应如何设计。核心结论：**负载形态是机型设计的第一输入——容量驱动要分层存储与 CXL 池化，吞吐驱动要 PD 分离与强调度，结构驱动要确定性互联与在网计算；同一 GPU 平台挂不同外围（内存层/互联层/调度层）就是三类不同机型**。
> **关键词**: KV Cache · 推理场景 · 容量驱动 · 吞吐驱动 · 结构驱动 · PD 分离 · CXL 池化 · MoE 路由 · 机型设计 · 长上下文 · Agent
> **适用对象**: LLM 推理平台架构师、服务器产品定义工程师、GPU 集群规划者、技术决策者
> **关联**: [推理显存与 KV Cache 深度分析](2026-08-11-inference-vram-kvcache-deep-analysis.md)（KV 公式与显存矩阵，本文数据基线）· [单节点到多节点推理](2026-08-05-llm-inference-single-to-multi-node-deep-analysis.md)（S1/S2/S3 跨节点场景，本文场景同构）· [KV 压缩全局分配 GraceKV×AoH](2026-08-11-kv-compression-global-allocation-gracekv-aoh-deep-analysis.md)（KV 四层命运论）· [LLM 系统软件成熟化](2026-08-10-llm-system-software-maturity-tensorcast-b300-plora-vibe.md)（CXL 池化/NDP）· [Cascade SLO 调度](2026-08-11-cascade-slo-latency-budget-scheduling-deep-analysis.md)（调度器设计）

---

## 目录

- [0. 总览：三类场景与机型设计的第一性原理](#0-总览三类场景与机型设计的第一性原理)
  - [0.1 三类场景 MECE 划分](#01-三类场景-mece-划分)
  - [0.2 核心命题：负载形态决定机型](#02-核心命题负载形态决定机型)
- [1. 场景 A：单请求长上下文（容量驱动）](#1-场景-a单请求长上下文容量驱动)
  - [1.1 业务场景描述](#11-业务场景描述)
  - [1.2 业务特性](#12-业务特性)
  - [1.3 数据推导：KV 容量与分层带宽](#13-数据推导kv-容量与分层带宽)
  - [1.4 技术演进：从全 HBM 到 KV 分层（OasisKV/HiSparse）](#14-技术演进从全-hbm-到-kv-分层oasiskvhisparse)
  - [1.5 机型设计要点](#15-机型设计要点)
- [2. 场景 B：高并发短请求（吞吐驱动）](#2-场景-b高并发短请求吞吐驱动)
  - [2.1 业务场景描述](#21-业务场景描述)
  - [2.2 业务特性](#22-业务特性)
  - [2.3 数据推导：KV 总量与 decode 带宽](#23-数据推导kv-总量与-decode-带宽)
  - [2.4 技术架构：PD 分离与强调度](#24-技术架构pd-分离与强调度)
  - [2.5 机型设计要点](#25-机型设计要点)
- [3. 场景 C：MoE 动态路由（结构驱动）](#3-场景-cmoe-动态路由结构驱动)
  - [3.1 业务场景描述](#31-业务场景描述)
  - [3.2 业务特性](#32-业务特性)
  - [3.3 数据推导：AllToAll 通信量与路由决策](#33-数据推导alltoall-通信量与路由决策)
  - [3.4 技术架构：确定性互联与在网计算（Scorpio）](#34-技术架构确定性互联与在网计算scorpio)
  - [3.5 机型设计要点](#35-机型设计要点)
- [4. 三场景对比矩阵](#4-三场景对比矩阵)
- [5. 内部知识链接图谱](#5-内部知识链接图谱)
- [6. 可证伪预测（P1-P4）](#6-可证伪预测p1-p4)
- [参考文件](#参考文件)
- [变更记录](#变更记录)

---

## 0. 总览：三类场景与机型设计的第一性原理

### 0.1 三类场景 MECE 划分

LLM 推理的 KV Cache 管理压力，按**驱动因素**恰好分为三类（互斥且穷尽）：

| 场景 | 驱动因素 | 典型负载 | 核心矛盾 | 主导资源 |
|:-----|:---------|:---------|:---------|:---------|
| **A 单请求长上下文** | 容量（KV 装不下） | 长文档分析、RAG、多模态长上下文 | KV 总量 > HBM 容量 | 内存容量 + 迁移带宽 |
| **B 高并发短请求** | 吞吐（不够快） | 办公助手、Agent 多轮对话、代码生成 | 并发 KV 总量 × decode 带宽 | KV 带宽 + 调度能力 |
| **C MoE 动态路由** | 结构（模型要求） | DeepSeek V3 类 MoE 推理 | 专家跨节点的 AllToAll 通信 | 互联确定性 + 在网计算 |

**与既有知识库的同构关系**：本文三类场景与 [单节点到多节点推理](2026-08-05-llm-inference-single-to-multi-node-deep-analysis.md) 的 S1/S2/S3 完全对应——S1 容量驱动、S2 吞吐驱动、S3 结构驱动。差异在于：本文聚焦 **KV Cache 视角**（内存与带宽），而非跨节点视角（互联与并行）；且本文落到**机型设计**（服务器产品定义），而非系统架构。两类文档互为表里 [来源: 知识库 单节点到多节点推理 §1.3]。

### 0.2 核心命题：负载形态决定机型

**第一性原理**：KV Cache 管理有三类本质不同的资源瓶颈——容量、带宽、互联。服务器机型的本质是**把 GPU 平台与合适的内存层/互联层/调度层组合**，使瓶颈资源最大化利用：

```text
GPU Compute Platform (same silicon)
   |                    |                    |
   v                    v                    v
+--------+        +--------+        +--------+
| Type A |        | Type B |        | Type C |
| Cap.   |        | Thrput |        | Struct |
| HBM+   |        | PD-Dis |        | Det.   |
| DRAM+  |        | +Sched |        | Inter. |
| CXL+SSD|        | +KV Ch |        | +IN-Net|
+--------+        +--------+        +--------+
 Memory tiers        Sched pools       Comm domains
```

> **一句话主线**：**同一个 GPU 平台，挂不同的外围（内存层/调度层/互联层），就是三类不同机型**。选型先问负载形态，再定外围配置——这是 2026 年推理服务器产品定义的元规则 [来源: 本文推导，结合知识库 KV 四层命运论 + PD 分离 + Scorpio 锚点]。

---

## 1. 场景 A：单请求长上下文（容量驱动）

### 1.1 业务场景描述

**场景画像**：单请求上下文极长（128K~1M token），并发低（个位数~数十），KV Cache 总量远超单卡 HBM 容量。

**典型负载**：
- **长文档智能分析**：整本论文/财报/法律合同一次性读入，问题链式追问
- **深度 RAG**：检索结果全量注入上下文，多跳推理
- **多模态长上下文**：视频/长音频理解（token 数爆炸）
- **Agent 长任务**：长视界 agent 携带完整对话历史持续推理（WorkBuddy/Rovo 类）

**规模感知**：70B 模型（GQA 8:1）KV = 320KB/token（FP16）。128K 上下文 → KV ≈ **41.9GB**；1M 上下文 → KV ≈ **320GB**（[来源: 本文按 KV 公式推导，基线见知识库 KV 深度分析 §3]）。对比：H200 单卡 HBM 141GB、B300 288GB——**128K 上下文的 KV 已吃掉 H200 近 30% 容量，1M 上下文 KV 超过单卡 HBM 总量**。

### 1.2 业务特性

| 特性 | 值 | 影响 |
|:-----|:---|:-----|
| 并发度 | 低（1-32） | 不需要大规模 PD 分离 |
| 上下文长度 | 128K~1M+ | KV 总量线性膨胀 |
| 请求数/天 | 少但单请求价值高 | 容量 > 吞吐 |
| decode 时延 | 首 token 可慢（秒级），逐 token 需稳定 | 稀疏注意力可接受 |
| 注意力模式 | 天然稀疏（重要 token 聚集） | 是 KV 分层的前提 |
| 成本结构 | HBM 容量成本主导 | 分层用便宜容量替换贵 HBM |

**关键业务洞察**：长上下文推理的瓶颈**不是算力而是内存**——"decoding hits a capacity wall long before it runs out of compute"（[来源: OasisKV, arXiv:2608.08097, 2026-08-08]）。这意味着该场景的机型优化方向是**用分层存储扩大 KV 容量池**，而不是堆算力。

### 1.3 数据推导：KV 容量与分层带宽

**① KV 容量公式**（基线见 [推理显存与 KV Cache 深度分析](2026-08-11-inference-vram-kvcache-deep-analysis.md)）：

```text
KV_bytes = batch × seq × 2 × L × D_eff × dtype_bytes
70B (GQA 8:1, L=80, D_eff=8×128=1024, FP16): 320 KB/token
128K ctx:  320KB × 131,072 = 41.9 GB
1M ctx:    320KB × 1,048,576 = 320 GB
```

**② 分层带宽经济性**（第一性推导，本文）：

| 层 | 典型带宽 | 典型容量（/节点） | 带宽/容量比 | 适用 KV 子集 |
|:---|:---------|:------------------|:-----------|:------------|
| L0 HBM | ~8 TB/s（H100 级） | 141-288 GB | 28-57× | 近期/高频 token |
| L1 CPU DRAM | ~400-500 GB/s（12ch DDR5） | 1-2 TB | ~0.3× | 全量驻留候选 |
| L2 CXL 池化 | ~64 GB/s（CXL 2.0 x16） | 4-8 TB（池） | ~0.01× | 冷 KV 批量迁移 |
| L3 NVMe SSD | ~14 GB/s（Gen5） | 数十 TB | ~0.0003× | 休眠 KV/检查点 |

**带宽-容量权衡的数学表达**：decode 每步读取 KV 的带宽需求 = `KV_size × tokens_per_sec`。以 128K 上下文全量读取为例：41.9GB × 20 tok/s = **838 GB/s**——远超 CXL（64GB/s）与 SSD（14GB/s），仅 HBM（8TB/s）与 CPU DRAM（~450GB/s）可支撑。**结论：长上下文下逐 token 全量读 KV 是不可能的，必须依赖注意力稀疏性只读子集**（这正是 OasisKV/HiSparse 的技术前提）[来源: 本文推导]。

**③ 分层迁移的成本模型**：KV 冷热迁移（HBM↔CPU DRAM↔CXL↔SSD）的代价 = 迁移带宽 × 迁移量。320GB（1M ctx）从 SSD 迁回 HBM：320GB ÷ 14GB/s ≈ **23 秒**——只适合离线/低频场景；从 CPU DRAM 迁回 HBM：320GB ÷ 450GB/s ≈ **0.7 秒**——可支撑在线推理的"逐步预热" [来源: 本文按带宽推导]。

### 1.4 技术演进：从全 HBM 到 KV 分层（OasisKV/HiSparse）

**问题**：传统 serving 系统把整个 KV cache 放 HBM（保证任意位置可选），请求内存账单随全文长度线性增长 → 上下文超过 HBM 就无法服务。

**2026-08 两条成熟路线**（均为 arXiv 一手，本文首次归档）：

| 系统 | 核心机制 | 量化收益 | 平台 |
|:-----|:---------|:---------|:-----|
| **OasisKV** (2608.08097) | decode 注意力天然稀疏 → 只用 lookahead tokens（投机解码草稿）预测未来重要 token → 从高层级内存（host/remote）预取重要 KV block 到 HBM | 2048-token KV 预算精度损失仅 **0.7 点**；推理负载吞吐 **1.69×**；多 GPU 长上下文 **2.1×**；PD 分离下每请求 KV 减少 **6.5-9.7×**、decode 节点 host 内存 **-2.2-2.6×** | vLLM 实现 |
| **HiSparse** (2608.07009) | top-k 稀疏注意力：全量 KV 驻留 host 内存，固定小 GPU cache；fused CUDA kernel 在 decode graph 内解决命中/LRU/host-device 取数；跨层共享选择做精确层间预取 | 长上下文峰值吞吐最高 **4.7×**；per-token 延迟相当；TTFT 高负载下改善；已合入上游 SGLang | DSA/NSA/Quest 三族稀疏注意力 × H200/B200/GH200 |

**对机型的含义**：OasisKV/HiSparse 证明——**CPU DRAM 是 KV 的第二主存**（不是缓存），GPU 只需保留"最相关 token"子集。这直接推高机型对 **CPU 内存带宽与容量** 的要求，并让 **CXL 池化内存**成为扩展第二主存的自然选择 [来源: 本文综合 OasisKV/HiSparse 论文 + 知识库 KV 四层命运论]。

### 1.5 机型设计要点

| 设计项 | 配置建议 | 依据 |
|:-------|:---------|:-----|
| **大内存带宽** | 12 通道 DDR5（Genoa/Bergamo 级），≥450GB/s；CPU 直连内存优先于 NUMA 远端 | KV 第二主存带宽 = decode 吞吐上限（OasisKV 实证） |
| **CXL 槽位** | ≥2 个 CXL 2.0/3.0 内存扩展槽（E3.S/CXL AIC），支持池化内存 | CXL 是容量扩展关键（L2 层）；PLoRA 证明池化内存"带宽换容量"正确 |
| **分层存储** | 每 GPU 配 NVMe Gen5（≥1 盘），支持 KV 冷数据落盘 | L3 层兜底；320GB 全量落盘需数十秒，仅低频场景 |
| **CPU 算力** | 高主频 CPU + 大 L3，承担 KV 冷热迁移调度 | CPU 驱动 KV 迁移（OasisKV lookahead 预测也在 CPU/GPU 侧） |
| **GPU 选型** | 高 HBM 容量优先（B300 288GB > H200 141GB），带宽其次 | L0 层容量决定"最相关子集"驻留规模 |
| **软件栈** | vLLM/SGLang + KV 分层插件（OasisKV/HiSparse 已合入） | 硬件能力需软件暴露 |

> **机型画像（场景 A）**：**"大内存"推理机**——GPU 挂大 HBM + 高带宽 CPU 内存 + CXL 扩展 + SSD 分层，本质是把"KV 容量池"做大的存储型推理节点。

---

## 2. 场景 B：高并发短请求（吞吐驱动）

### 2.1 业务场景描述

**场景画像**：请求短（1K~8K token）、并发极高（数百~数千）、多轮交互，KV Cache 总量随**并发度**线性膨胀，系统瓶颈是**聚合 KV 带宽与调度能力**。

**典型负载**：
- **办公 AI**：会议纪要、文档生成、邮件草拟（CSP 办公套件，每秒数千请求）
- **Agent 多轮对话**：编码助手、客服 agent、浏览器 agent（Claude Code/Trae/WorkBuddy 类）
- **在线代码生成**：补全/续写，短上下文但 QPS 极高

**规模感知**：70B 模型 4K 上下文 → KV = 320KB × 4096 = **1.28GB/请求**。1000 并发 → 聚合 KV = **1.28TB**——远超单节点 HBM（288GB）与 CPU DRAM（1-2TB），必须**跨节点池化 + PD 分离** [来源: 本文推导，KV 公式基线见知识库 KV 深度分析]。

### 2.2 业务特性

| 特性 | 值 | 影响 |
|:-----|:---|:-----|
| 并发度 | 极高（数百-数千） | KV 总量 = 并发 × 单请求 KV |
| 上下文长度 | 短（1K-8K） | 单请求 KV 小，但总量巨大 |
| 请求频次 | 极高（QPS 千级） | 调度器是性能关键 |
| 多轮特性 | 每轮保留历史 KV | 前缀缓存/上下文复用收益大 |
| decode 时延 | 逐 token 需低（<100ms） | 带宽必须充足 |
| 成本结构 | 吞吐 × 利用率主导 | 用满硬件是关键 |

**关键业务洞察**：办公/Agent 负载的 KV 特征是**"短而多"**——单请求 KV 仅 1.28GB，但并发乘数让它变成系统最大内存消费者。Agora 生产数据实证：Agentic 负载下 **CPU 中位利用率仅 6-31%、GPU SM 活跃度 <55%**，碎片化执行搁置 0.74 个服务器等效吞吐（[来源: Agora, arXiv:2608.04458, 知识库双全文深读]）——**该场景的优化空间在"把闲置资源聚合起来"而非"堆新硬件"**。

### 2.3 数据推导：KV 总量与 decode 带宽

**① KV 总量随并发线性膨胀**：

```text
KV_total = concurrency x seq x 320KB (70B FP16)
1000 conc x 4K ctx = 1000 x 1.28GB = 1.28 TB
```

**② decode 带宽需求**（第一性推导，本文）：

```text
decode KV read/step = batch x seq x 320KB
H100 HBM BW 8TB/s:
  batch=128, seq=4K: 128 x 1.28GB = 164GB/step -> 8TB/s / 164GB ~ 49 step/s -> 6.3K tok/s
  batch=512, seq=4K: 512 x 1.28GB = 655GB/step -> 8TB/s / 655GB ~ 12 step/s -> 6.3K tok/s
```

> **关键洞察**：decode 的 KV 带宽瓶颈下，**总吞吐受 HBM 带宽约束而非算力**——batch 增大到一定程度后吞吐不再增长（带宽饱和）。这解释了为什么场景 B 需要 **PD 分离**：prefill 阶段（算力密集）与 decode 阶段（带宽密集）对硬件需求不同，合并运行互相拖累 [来源: 本文推导，对照知识库 PD 分离专题]。

**③ PD 分离的 KV 传输成本**：prefill 池算完的 KV 要传给 decode 池：

```text
KV transfer/req = seq x 320KB = 4K ctx -> 1.28GB
1.28GB @ 100Gbps (RDMA) ~ 102ms  [Source: KB single-to-multi-node 7.1]
1.28GB @ 400Gbps (RoCE/IB) ~ 26ms
```

> **含义**：KV 通道带宽直接决定 PD 分离的请求迁移时延——**KV 通道是场景 B 机型的第三大设计项**（GPU 算力、KV 带宽之外）。OasisKV 实证：PD 分离下每请求 KV 减少 6.5-9.7×（稀疏化），decode 节点 host 内存需求 -2.2-2.6×（[来源: OasisKV, arXiv:2608.08097]）——**稀疏 KV 传输是缓解 KV 通道压力的软件路径**。

### 2.4 技术架构：PD 分离与强调度

**PD 分离架构**（Prefill-Decode Disaggregation）：

```text
+---------------+      KV Channel (100-400Gbps)      +---------------+
|  Prefill Pool |  -------------------------->  |  Decode Pool  |
|  Compute-heavy|   KV 1.28GB/req @ 102ms/100G  |  BW-heavy     |
|  Short high   |                                |  Long low-calc|
|  Scale by QPS |                                |  Scale by conc|
+---------------+                                +---------------+
        ^                                                  ^
        +--------------- Scheduler (Cascade) --------------+
             single latency-budget signal: sched x KV mgmt
```

**调度器设计**（场景 B 的灵魂）：
- **传统**：按 deadline 排序，只决定"先服务谁"——不控制资源使用
- **Cascade（2026-08，arXiv:2608.06557）**：per-request 延迟预算（SLO 减去预测剩余服务时间），单一信号同时协调调度与 KV 内存管理（恢复/预取/驻留/重算）——**goodput 提升 2.4×、SLO 违规 -40%**（[来源: 知识库 Cascade 深度分析]）
- **调度三级升级**：排队器 → 编排器 → SLO 预算调度（Cascade/HorizonServe 合流）[来源: 知识库 调度对象三级升级]

**Prefix Caching 收益**：办公/Agent 负载共享 system prompt 与历史前缀 → 前缀缓存复用使 KV 命中率提升 68-75%（Agora 实证），等效减少 KV 总量与 decode 带宽需求 [来源: Agora×GraceKV 双全文深读]。

### 2.5 机型设计要点

| 设计项 | 配置建议 | 依据 |
|:-------|:---------|:-----|
| **两池独立扩缩** | Prefill 机型（算力强/短时高算）+ Decode 机型（KV 带宽强/大 HBM）物理分离，按负载比例独立配置 | PD 分离是场景 B 的架构前提 |
| **调度器 CPU** | 高主频 CPU + 大内存，调度延迟 <1ms；支持 Cascade 类预算调度 | 调度器是系统性能核心（goodput 2.4×） |
| **KV 通道** | 每节点 ≥2×400Gbps RDMA（RoCE/IB），KV 传输时延 <30ms/请求 | 1.28GB/请求 @ 400G = 26ms |
| **Decode 机型 HBM** | 高带宽 HBM（H100 8TB/s / B200 更高），容量次之 | decode 是带宽瓶颈 |
| **Prefix 缓存** | 大 CPU DRAM + 快速检索，跨请求共享前缀 | KV 命中率 +68-75% 等效扩容 |
| **GPU 利用率监控** | 碎片化检测（SM 活跃度 <55% 即触发收割） | Agora 实证：1/3 GPU 可释放 |

> **机型画像（场景 B）**：**"双池"吞吐机**——prefill 机（算力型）+ decode 机（带宽型）+ 强调度 CPU + 高速 KV 通道，本质是"把并发 KV 流量用调度与分池榨干"的吞吐型推理节点。

---

## 3. 场景 C：MoE 动态路由（结构驱动）

### 3.1 业务场景描述

**场景画像**：MoE（Mixture-of-Experts）模型推理，专家（Experts）分布在多节点，每个 token 经 Router 动态选择 top-k 专家——**可能跨节点**——触发 AllToAll 通信。模型结构本身要求跨节点，与场景 A/B 的"装不下/不够快"不同。

**典型负载**：
- **DeepSeek V3/R1 类 MoE 推理**（671B 总参数、37B 激活、256 专家、top-8 路由）
- **大规模 MoE 服务**：混合专家模型的在线推理（Kimi K3 2.8T MoE 等）

**规模感知**：DeepSeek V3 总参数 671B、256 个专家（每个 ~2.7B），单节点（8 GPU）装不下全部专家 → 必须跨节点放置 → 每个 token 路由时可能跨节点访问专家 → **token 级动态 AllToAll** [来源: DeepSeek-V3 Technical Report arXiv:2412.19437 + 知识库 MoE 并行专题]。

### 3.2 业务特性

| 特性 | 值 | 影响 |
|:-----|:---|:-----|
| 路由粒度 | token 级动态 | 通信伙伴运行时才确定，互联无法预配置路径 |
| 通信模式 | AllToAll（非 AllReduce） | 需要交换机硬件多播/重配置能力 |
| 专家放置 | 跨节点（>单节点 GPU 数） | 模型结构强制跨节点 |
| 互联要求 | 确定性 + 低延迟 | 动态路由对延迟敏感 |
| 负载均衡 | 专家热度不均（高频/低频） | 复制/迁移策略 |
| 容量 | 权重全量驻留（671B） | 显存按总参数算，非激活参数 |

**关键业务洞察**：MoE 的 KV Cache 本身不是瓶颈（MLA 压缩后仅 137KB/token），**瓶颈在路由引发的 AllToAll 通信**——"MoE 是结构型跨节点（S3），它的跨节点是模型自己要求的，优化方向是让互联对动态路由友好"（[来源: 知识库 单节点到多节点推理 §2.4]）。DeepSeek V3 推理曾被迫**限制 token 路由到 4 个目标节点**，仅因互联容量约束（[来源: Scorpio 专题，Futurum 披露]）——**互联决定模型结构的表达自由度**。

### 3.3 数据推导：AllToAll 通信量与路由决策

**① AllToAll 通信量**（第一性推导，本文）：

```text
each token routes to top-8 experts:
  per-token send = 8 x hidden_size x dtype_bytes
  DeepSeek V3 (hidden=7168, FP8): 8 x 7168 x 1 = 57.3 KB/token out-of-domain
  batch=512, seq=4K: 512x4096x57.3KB = 120 GB per batch

vs TP AllReduce (70B decode): 2.56MB/token  [Source: KB single-to-multi 2.1]
-> MoE AllToAll traffic is 1 order higher than TP, and more bursty
```

**② 路由决策延迟预算**（第一性推导，本文）：

```text
Router decision (CPU side): pick top-8 experts -> decision latency < interconnect latency
  per-token decision ~ hundreds ns to us (CPU compute)
  if routing on GPU (MLA qk_rope) -> tighter coupling with interconnect
```

**③ 互联容量 vs 路由自由度的数学关系**（关键洞察）：

```text
routable target nodes N ~= fabric agg-BW / (per-token traffic x token rate)
DeepSeek V3 4-node cap -> agg-BW only supports full expert access within 4 nodes
Scorpio Hypercast HW offload: GPU IO -49%, MoE AllToAll 4-6x (vendor claim)
```

### 3.4 技术架构：确定性互联与在网计算（Scorpio）

**问题**：软件减延迟已逼近极限（RDMA ~1-5μs），MoE 动态路由需要**确定性**（路径可预测、延迟有界）与**在网处理**（数据在途完成归约/多播）。

**Scorpio（Astera Labs）——"用交换结构服务 MoE 跨节点"的样本**（[来源: 知识库 SerDes 综合分析 + 单节点到多节点 §6.3]）：

```text
Scorpio Smart Fabric (PCIe Gen5/6, 32-320 lanes, TSMC 7nm)
  |-- Hypercast: HW collective comm (MoE AllToAll 4-6x, vendor claim)
  `-- In-Network Compute: in-transit processing (GPU IO -49%, vendor claim)
        |
        v
  lift DeepSeek V3 4-node routing cap -> fabric no longer constrains model
```

**架构选择**：

| 互联方案 | MoE 适配 | 延迟 | 确定性 | 代表 |
|:---------|:---------|:-----|:-------|:-----|
| NVLink 域内 | ✅ 最佳（域内全对等） | ~565ns | ✅ | NVIDIA |
| UALink 域内 | ✅（Helios 260TB/s scale-up） | 低 | ✅ | AMD |
| RDMA 跨节点 | ⚠️ 可用但延迟高 | ~1-5μs | ❌ | RoCE/IB |
| **交换式 fabric** | ✅ 专门为动态路由设计 | 中 | ✅ | **Scorpio** |

**StrataCL（华为 CloudMatrix384）佐证**：fabric-native 通信库（registration-on-allocation + NPU-core 分区 + SDMA 卸载）在 CM384 上实现 **MoE dispatch/combine 最高 1.4×、LLM 推理吞吐 1.9×**——"把通信库从缓冲搬运工重构为 fabric 原生执行器"（[来源: 知识库 StrataCL 深度分析，arXiv:2607.26444]）。**确定性互联 + 硬件集合通信是 2026 年 MoE 推理的主线**。

### 3.5 机型设计要点

| 设计项 | 配置建议 | 依据 |
|:-------|:---------|:-----|
| **确定性互联** | scale-up 域优先（NVLink/UALink/交换式 fabric），域内全对等；跨域走 DP/PD | token 级路由只能在低延迟域内做 |
| **硬件集合通信** | 支持 Hypercast/SHARP/在网计算的交换结构 | GPU IO 降 49%（Scorpio 厂商值） |
| **路由 CPU** | 高主频 CPU 承担 Router 决策，决策延迟 < 互联延迟；CPU 与 GPU 间低延迟接口 | 路由决策是每 token 的前置步骤 |
| **专家放置** | 高频专家复制到各节点（频率-容量权衡），减少出域 AllToAll | 负载均衡与通信量平衡 |
| **权重显存** | 按总参数（671B）配 HBM，非激活参数（37B） | MoE 推理误区：权重全量驻留 |
| **KV 架构** | MLA 压缩（137KB/token）已足够，无需分层 | MoE 的 KV 非瓶颈，互联才是 |

> **机型画像（场景 C）**：**"确定性互联"路由机**——GPU + 交换式 scale-up fabric + 硬件集合通信 + 路由 CPU，本质是"让动态路由在确定性互联里自由表达"的 MoE 推理节点。

---

## 4. 三场景对比矩阵

| 维度 | A 容量驱动 | B 吞吐驱动 | C 结构驱动 |
|:-----|:----------|:----------|:----------|
| 典型负载 | 长文档/RAG/长上下文 | 办公/Agent/代码生成 | MoE 在线推理 |
| 驱动因素 | KV 装不下 | 并发不够快 | 模型要求跨节点 |
| KV 规模 | 41.9GB@128K / 320GB@1M | 1.28GB×1000 并发 = 1.28TB | 137KB/token（MLA，小） |
| 主导瓶颈 | 内存容量 + 迁移带宽 | KV 带宽 + 调度能力 | 互联确定性 + 在网计算 |
| 核心技术 | KV 分层 HBM→CXL→SSD | PD 分离 + 强调度 + KV 通道 | 确定性互联 + 硬件集合通信 |
| 外部验证 | OasisKV 1.69-2.1× / HiSparse 4.7× | Cascade goodput 2.4× / Agora 收割 | Scorpio 4-6× / StrataCL 1.9× |
| **机型要点** | 大内存带宽 + CXL 槽位 + 分层存储 | 两池独立扩缩 + 调度器强 + KV 通道 | 确定性互联 + 硬件集合通信 + 路由 CPU |
| 软件栈 | vLLM/SGLang + KV 分层插件 | vLLM + PD 分离 + Cascade 调度 | vLLM/SGLang + MoE 路由优化 |

---

## 5. 内部知识链接图谱

| 关系 | 知识点 | 路径 |
|:-----|:-------|:-----|
| depends-on | 推理显存与 KV Cache 深度分析（KV 公式/显存矩阵） | [llm-techniques-principles/2026-08-11-inference-vram-kvcache-deep-analysis.md](2026-08-11-inference-vram-kvcache-deep-analysis.md) |
| extends | 单节点到多节点推理（S1/S2/S3 场景） | [llm-techniques-principles/2026-08-05-llm-inference-single-to-multi-node-deep-analysis.md](2026-08-05-llm-inference-single-to-multi-node-deep-analysis.md) |
| related | KV 压缩全局分配（GraceKV×AoH，KV 四层命运论） | [llm-techniques-principles/2026-08-11-kv-compression-global-allocation-gracekv-aoh-deep-analysis.md](2026-08-11-kv-compression-global-allocation-gracekv-aoh-deep-analysis.md) |
| related | LLM 系统软件成熟化（PLoRA CXL 池化/NDP） | [llm-techniques-principles/2026-08-10-llm-system-software-maturity-tensorcast-b300-plora-vibe.md](2026-08-10-llm-system-software-maturity-tensorcast-b300-plora-vibe.md) |
| related | Cascade SLO 延迟预算调度 | [llm-techniques-principles/2026-08-11-cascade-slo-latency-budget-scheduling-deep-analysis.md](2026-08-11-cascade-slo-latency-budget-scheduling-deep-analysis.md) |
| related | Agora×GraceKV Agentic 服务器 KV（Agora 生产数据） | [agent-engineering/2026-08-11-agora-gracekv-agentic-server-kv-deep-analysis.md](../agent-engineering/2026-08-11-agora-gracekv-agentic-server-kv-deep-analysis.md) |
| related | StrataCL fabric-native 通信（华为 CM384） | [llm-techniques-principles/2026-08-11-stratalc-fabric-native-communication-deep-analysis.md](2026-08-11-stratalc-fabric-native-communication-deep-analysis.md) |
| related | 推理冗余消除（四类冗余 MECE） | [llm-techniques-principles/2026-08-05-llm-inference-redundancy-elimination-deep-analysis.md](2026-08-05-llm-inference-redundancy-elimination-deep-analysis.md) |
| related | KV Cache 带宽与延迟深潜 | [llm-techniques-principles/2026-07-07-kv-cache-bandwidth-latency-deep-dive.md](2026-07-07-kv-cache-bandwidth-latency-deep-dive.md) |
| see-also | 推理上下文存储（KV 分层） | [02_rd/01_product/00_hardware/06_storage/kv-cache/2026-06-26-inference-context-memory-storage.md](../../02_rd/01_product/00_hardware/06_storage/kv-cache/2026-06-26-inference-context-memory-storage.md) |
| see-also | SerDes 综合分析（Scorpio 硬件） | [02_rd/01_product/00_hardware/04_si-signal/2026-06-25-serdes-comprehensive-analysis.md](../../02_rd/01_product/00_hardware/04_si-signal/2026-06-25-serdes-comprehensive-analysis.md) |

---

## 6. 可证伪预测（P1-P4）

| # | 预测 | 核验窗口 | 证伪条件 |
|:-:|:-----|:---------|:---------|
| P1 | 场景 A 的 KV 分层成为长上下文推理标配——2027 年 ≥2 个主流 serving 框架（vLLM/SGLang/TGI）内置 host 内存 KV 层 | 2027-12 | 仍全部 KV 驻留 HBM |
| P2 | 场景 B 的 PD 分离从"两池物理分离"走向"弹性分池"（同一集群动态划分 prefill/decode 比例），2027 年 ≥1 个生产系统实现 | 2027-12 | 仍为静态两池 |
| P3 | 场景 C 的 MoE 路由上限从 4 节点解除到 ≥16 节点——2027 年出现硬件集合通信（Hypercast/SHARP 类）服务 ≥16 节点 MoE 的生产案例 | 2027-12 | 仍 ≤8 节点 |
| P4 | CXL 池化内存从"容量扩展"走向"近存计算"（NDP）在 KV 场景落地——2027 年出现 KV 分层中 CXL 层承载计算的学术/生产证据 | 2027-12 | CXL 仍纯容量扩展 |

---

## 参考文件

### 内部知识库引用

[1] [推理显存与 KV Cache 深度分析](2026-08-11-inference-vram-kvcache-deep-analysis.md)（KV 公式/显存矩阵，本文数据基线）
[2] [单节点到多节点推理](2026-08-05-llm-inference-single-to-multi-node-deep-analysis.md)（S1/S2/S3 场景 + Scorpio/Helios 案例 + PD 分离 102ms）
[3] [KV 压缩全局分配 GraceKV×AoH](2026-08-11-kv-compression-global-allocation-gracekv-aoh-deep-analysis.md)（KV 四层命运论）
[4] [LLM 系统软件成熟化](2026-08-10-llm-system-software-maturity-tensorcast-b300-plora-vibe.md)（PLoRA CXL 池化/NDP：32GB/s 即饱和）
[5] [Cascade SLO 延迟预算调度](2026-08-11-cascade-slo-latency-budget-scheduling-deep-analysis.md)（goodput 2.4×/SLO -40%）
[6] [Agora×GraceKV 双全文深读](agent-engineering/2026-08-11-agora-gracekv-agentic-server-kv-deep-analysis.md)（Agentic 负载 CPU 6-31%/KV 命中 +68-75%）
[7] [StrataCL fabric-native 通信](2026-08-11-stratalc-fabric-native-communication-deep-analysis.md)（MoE dispatch/combine 1.4×、吞吐 1.9×）
[8] [SerDes 综合分析](02_rd/01_product/00_hardware/04_si-signal/2026-06-25-serdes-comprehensive-analysis.md)（Scorpio 32-320 lanes PCIe Gen5/6）

### 外部资料引用

[9] OasisKV, arXiv:2608.08097（2026-08-08）——KV 解耦 HBM + lookahead 稀疏预取；2048-token KV 预算精度 -0.7 点；1.69×/2.1× 吞吐；PD 分离 KV -6.5-9.7×
[10] HiSparse, arXiv:2608.07009（2026-08-07）——层级 KV 管理；host 全量 + GPU 固定 cache；已合入 SGLang；长上下文峰值吞吐 4.7×
[11] DeepSeek-V3 Technical Report, arXiv:2412.19437——MLA 压缩 137KB/token；256 专家 top-8 路由；671B 总参数
[12] Cascade, arXiv:2608.06557——SLO 延迟预算调度
[13] Scorpio（Astera Labs）——Hypercast 硬件集合通信 + In-Network Compute；GPU IO -49%（⚠️ 厂商声称值，未独立验证）
[14] StrataCL, arXiv:2607.26444（华为 CM384）

---

## 变更记录

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-11 | v1.0 | 首次创建：三类 KV Cache 推理场景深度分析（场景描述/业务特性/数据推导/机型设计），聚合知识库 8 篇内部锚点 + 6 项外部验证（OasisKV/HiSparse/Cascade/PLoRA/Scorpio/StrataCL），含三场景对比矩阵 + P1-P4 可证伪预测 |
