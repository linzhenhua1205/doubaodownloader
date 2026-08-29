# 🗄️ LLM 推理的 Context Memory Storage

> 推理过程中，模型需要存储所有「已看到」的 token 信息——即 **Context Memory**。随着上下文从 4K 扩展到 1M+ tokens，Context Memory 已成为推理基础设施中最大的存储挑战，催生了从 HBM 到 NVMe 的多级存储架构。
>
> **核心驱动力：KV Cache offload to NVMe SSD → 降低 $/Token**。在满足延迟 SLA 的前提下，将温/冷 KV Cache 卸载到低成本 NVMe 存储，以存储成本换取更高的 GPU 利用率和推理吞吐，实现最优的每 Token 总成本。

---

## 0. 驱动力：为什么 KV Cache 要卸载到 NVMe？

### 0.1 根本目标：降低 $/Token

```
$/Token = (GPU 成本 + 存储成本 + 网络成本 + 电力) / 每周期产生的 Token 数

降低 $/Token 的核心杠杆：
  1. ↑ 吞吐量：同一 GPU 服务更多请求
  2. ↓ GPU 闲置成本：更多请求共享 GPU 固定成本
  3. ↓ 存储成本：使用低成本介质管理 KV Cache
```

KV Cache Offload 同时作用于**三个杠杆**：

| 杠杆 | 机制 | 效果 | 典型量化 |
|:----|:----|:----|:--------|
| **↑ GPU 吞吐量** | 卸载 KV Cache 释放 HBM → HBM 容纳更多请求的 KV Cache → 更高 Batch Size | 请求并发量 **2-4x** | 16 → 48 并发 |
| **↓ GPU 闲置成本** | 卸载使更多请求可排队 → GPU 计算单元饱和 → 摊薄每 Token 的 GPU 固定成本 | GPU 利用率 **~60% → 90%+** | 固定成本减半 |
| **↓ 存储成本** | 温/冷 KV 放在 NVMe ($0.15/GB) 而非 HBM (~$80/GB) | 每 GB 存储成本 **500x 差距** | HBM 只放活跃 KV |

### 0.2 哪些工作负载需要 Offload？

KV Cache 卸载到 NVMe 的价值取决于**工作负载特征**——不是所有场景都值得：

| 工作负载 | KV Cache 特征 | Offload 收益 | 说明 |
|:--------|:-------------|:-----------:|:-----|
| **大模型 + 长输入序列** | 单请求 KV 体积大（>1GB） | ⭐⭐⭐⭐⭐ | 1M 上下文 70B ~3.5GB/请求，不舍得卸载就无法做并发 |
| **Agentic AI (多轮推理)** | Agent 调用工具 + 思考 → 大量中间 KV 产生 | ⭐⭐⭐⭐⭐ | Agent 长链思考产生大量 KV，且可能回溯历史回合 |
| **Coding Agent** | 读取大量代码文件作为上下文 | ⭐⭐⭐⭐ | 每个文件加载 + 分析都产生 KV，卸载到 NVMe 是唯一方案 |
| **Chatbots (多会话)** | 大量用户会话保持 KV Cache 用于快速恢复 | ⭐⭐⭐⭐ | 冷会话可以卸载到 NVMe 释放 HBM 给活跃会话 |
| **推理/思考型模型** | 长时间 Chain-of-Thought，KV 持续增长 | ⭐⭐⭐⭐ | DeepSeek R1 类模型推理深度大，KV 累积迅速 |
| **频繁内容复用** | 相同 Prompt 前缀（system prompt） | ⭐⭐⭐ | Prefix Cache 可卸载到 NVMe，跨请求共享 |
| **短上下文 (<4K)** | 单请求 KV 小（<50MB） | ⭐ | 不值得卸载，HBM 放得下 |
| **实时交互 (<100ms TTFT)** | 延迟敏感 | ⭐ | Offload 增加加载延迟，不适合 |

### 0.3 Offload 的经济学：何时该卸载？

```
决策：是否将某个请求的 KV Cache 卸载到 NVMe？

条件 1: 容量不足
  剩余 HBM < 新请求的 KV Cache 体积
  → 必须驱逐，否则无法服务新请求

条件 2: 驱逐成本合适
  ╔══════════════════════════════════════════════════════╗
  ║  Offload 节省                                              ║
  ║  = 免于扩 GPU 的成本 - 增加的 NVMe 成本                    ║
  ║  = (每请求 HBM 占用 × GPU $/GB) - (每请求 NVMe 占用 × SSD $/GB)  ║
  ╚══════════════════════════════════════════════════════╝

示例计算:
  HBM 成本:      ~$80/GB (GPU 总成本 / HBM 容量)
  NVMe 成本:     ~$0.15/GB
  每请求 KV:     4 GB (70B, 128K)

  每请求卸载节省 = 4 × ($80 - $0.15) = $319.40/请求
  → 只要该请求的 KV 被卸载而不是完全拒绝 = 经济上永远值得

条件 3: 延迟预算可接受
  4GB NVMe 加载延迟: ~400-800ms (PCIe 4.0 x4)
  4GB CXL 加载延迟:  ~40ms (CXL 3.0 x16)
  
  如果延迟预算 > 加载延迟 → 卸载到对应层级可行
```

### 0.4 NVMe Offload 的实际 TCO 影响

```
假设: 8× GPU 节点, 80GB HBM/GPU, 70B 模型 (FP8 ~70GB/GPU)
      剩余 HBM ~10GB/GPU, 用于 KV Cache

无 Offload:
  KV Cache 容量:     10GB/GPU = 80GB/节点
  每请求 (128K):     4 GB
  最大并发:           20 请求
  每节点吞吐:         约 400 tok/s
  
有 Offload (NVMe, 4×8TB):
  KV Cache 容量:     10GB HBM (热) + 32TB NVMe (温/冷) / 节点
  每请求 (128K):     4 GB, 热窗口 4096 tokens 留在 HBM
  HBM 活跃容量:      ~8GB → 可容纳 16 请求的完整 KV + 更多部分驻留
  NVMe 可装:         8000+ 请求的冷 KV
  有效并发:           40+ 请求 (HBM 做热 + NVMe 做冷)
  每节点吞吐:         约 800+ tok/s

TCO 对比 (3 年)：
                   无 Offload      有 Offload (NVMe)
  GPU 节点数        10              5 (-50%)
  GPU 成本          $2.4M           $1.2M
  NVMe 成本         —               $20K
  电力              3 年 ~$600K     ~$300K
  总成本            3M              $1.52M
  吞吐              4000 tok/s      4000 tok/s
  $/Token 降幅       基准             **-49%**
```

> **核心洞察**: KV Cache Offload 的经济学优势非常显著——将温/冷 KV 从 HBM (~$80/GB) 迁移到 NVMe (~$0.15/GB) 实现了 **500x+ 的存储成本降幅**。这不仅直接降低存储开销，更重要的是 **释放 HBM 承载更多计算**，使 GPU 利用率从 60% 提升到 90%+，在相同 GPU 投入下实现 1.5-2x 的吞吐量，从而大幅摊薄 $/Token。

---

## 1. Context Memory 到底是什么？

### 1.1 LLM 推理的两类内存

```
                    LLM 推理运行时内存
                           │
          ┌────────────────┴────────────────┐
          │                                 │
    Model Weights                    Context Memory
    (模型权重)                          (上下文内存)
          │                                 │
    ┌─────┴──────┐              ┌───────────┴───────────┐
    │ 静态/只读   │              │    动态/读写          │
    │ 一次加载    │              │  每个请求各自独立      │
    │ 可跨请求共享 │              │  随上下文长度增长      │
    └────────────┘              │  每次 Decode 都访问    │
                                └───────────────────────┘
```

| 类型 | 大小 (70B 模型) | 访问模式 | 共享性 | 存储需求 |
|:----|:--------------:|:--------|:------|:--------|
| **模型权重** | ~140 GB (FP16) | 只读、顺序 | ✅ 多个请求共享 | 一次加载，驻留 HBM |
| **Context Memory** | 每请求 ~448 MB/128K | 读写、随机 Attention | ❌ 每个请求独立 | 随请求数线性增长 |

### 1.2 Context Memory 的构成

Context Memory 不是单一实体，而是多个组件的集合：

```
单个请求的 Context Memory
│
├── KV Cache (95%+ 体积) — Key/Value 对，存储每个 token 的 Attention 投影
│   ├── Key:     [n_layers, n_heads, d_head] — 用于计算注意力分数
│   └── Value:   [n_layers, n_heads, d_head] — 用于加权聚合
│
├── Prefix Cache (可选) — 共享 prompt 前缀的 KV Cache（如 system prompt）
│
├── Intermediate Activations (临时) — FFN 中间激活值（Prefill 后释放）
│
└── Speculative Tree (投机解码) — 投机解码的候选 token KV
```

### 1.3 KV Cache 是绝对主体

```
KV Cache 体积 = 2 (K+V) × num_layers × hidden_dim × precision

示例 (FP16):
  Llama 3 8B:   2 × 32 × 4096 × 2 = 0.5 MB/token
  Llama 3 70B:  2 × 80 × 8192 × 2 = 2.6 MB/token
  DeepSeek V3:  2 × 61 × 7168 × 2 = 1.75 MB/token (dense part)

1M 上下文时:
  8B  → 0.5 MB × 1M   = 512 MB   ✓ 单卡 HBM 可容纳
  70B → 2.6 MB × 1M   = 2.6 GB   ⚠️ 需要卸载
  DeepSeek V3 → 1.75 MB × 1M = 1.75 GB ⚠️ 需要卸载
```

---

## 2. Context Memory 的存储需求特征

### 2.1 访问模式分析

理解 Context Memory 的访问模式是设计存储架构的前提：

| 维度 | Prefill 阶段 | Decode 阶段 |
|:----|:-----------:|:----------:|
| **读写模式** | 写入（构建 KV Cache） | **读取为主**（Attention 读取） |
| **访问粒度** | 逐 token 追加写入 | **整个序列读取**（每个 Step 读全部） |
| **数据局部性** | 顺序写入 | **全量随机读取**（Attention 需所有 token） |
| **带宽需求** | 中 | **极高**（O(C) 读取，C=上下文长度） |
| **延迟敏感度** | 低 | **极高**（每个 token 等 KV 就绪） |
| **数据生命期** | 请求阶段 | 请求阶段（或更久，如 Agent 多轮） |

**关键洞察**：Decode 阶段每个 Step 都需要读取**整个序列**的 KV Cache。这意味着：
- 序列越长 → 每次 Decode 读取量越大 → 带宽需求越高
- KV Cache 是 **带宽敏感** 而非容量敏感（延迟×带宽乘积效应）

### 2.2 多请求聚合的带宽压力

```
N 个并发请求，每个 C token，模型 hidden_dim = D

每步总读取量 = N × C × D × 2 (K+V) × 2 bytes (FP16)
             = N × C × D × 4 bytes

示例: N=32, C=128K, D=8192 (70B)
  每步读取 = 32 × 131072 × 8192 × 4 = 137 GB/step
  HBM 带宽 3.35 TB/s → 每步耗时 ≈ 41ms
  → 解码速率 ≈ 24 tok/s
```

| 并发数 | 上下文 | 每步读取 | HBM (3.35TB/s) | CXL (100GB/s) | NVMe (10GB/s) |
|:-----:|:-----:|:-------:|:--------------:|:-------------:|:-------------:|
| 1 | 128K | 4.2 GB | 1.3ms ✅ | 42ms ❌ | 420ms ❌ |
| 8 | 128K | 33.6 GB | 10ms ✅ | 336ms ❌ | ❌ |
| 32 | 128K | 134 GB | 40ms ⚠️ | ❌ | ❌ |
| 1 | 1M | 33.6 GB | 10ms ✅ | 336ms ❌ | ❌ |
| 8 | 1M | 269 GB | 80ms ❌ | ❌ | ❌ |

> **结论**：Context Memory 的带宽需求极其苛刻。KV Cache **一旦离开 HBM，解码延迟就会急剧恶化**。因此 Context Memory Storage 的核心挑战不是「存哪里」，而是「热数据必须留在 HBM」，存储架构的目标是**管理热/温/冷数据的生命周期**。

### 2.3 容量压力：并发 × 上下文

```
单卡 HBM (80GB) 的容量分配：
  模型权重:     ~50-60 GB (70B, FP8 量化)
  KV Cache:    ~10-20 GB (剩余空间)
  每请求 128K:   448 MB
  最大并发:      22-45 个请求
  
  如果上下文到 1M:
  每请求 1M:     3.5 GB
  最大并发:      3-5 个请求
```

**容量困境的本质**：HBM 容量增长速度（每代 ~1.5x）远落后于上下文增长（2-4x/年）。当上下文到 1M+，**即使单个请求的 KV Cache 也可能超过剩余 HBM**。

---

## 3. Context Memory 存储层级架构

### 3.1 四层存储模型

```
    层级        介质        延迟      带宽       容量        每 GB 成本
  ┌────────┐
  │ T0:    │  GPU HBM    ~50ns    3-8 TB/s    80-192 GB    ~$80/GB
  │ Hot    │
  ├────────┤
  │ T1:    │  CPU DDR5   ~100ns   200-500 GB/s  1-2 TB      ~$10/GB
  │ Near   │
  ├────────┤
  │ T1.5:  │  CXL 内存池  ~300ns   80-120 GB/s  4-32 TB     ~$10/GB
  │ Warm   │
  ├────────┤
  │ T2:    │  NVMe SSD   ~10μs     5-10 GB/s    10-100 TB   ~$0.15/GB
  │ Cold   │
  └────────┘
```

### 3.2 各层级的角色

| 层级 | 存储什么？ | 生命周期 | 管理方式 |
|:----|:---------|:--------|:--------|
| **T0: HBM** | 活跃请求的完整 KV Cache | 请求存活期间 | PagedAttention 块管理 |
| **T1: DDR5** | 溢出 KV Cache（短时换出） | 秒级 | CPU 中转（传统方案） |
| **T1.5: CXL** | 温 KV Cache（等待/预热/复用） | 分钟级 | GDS Direct、memkind 感知 |
| **T2: NVMe** | 冷 KV Cache（Agent 回溯/历史会话） | 小时级 | GDS + NVMe over RDMA |

### 3.3 数据驱逐与加载决策

```
               请求到达
                   │
                   ▼
          KV Cache 在 HBM？
         ┌─────┼─────┐
         │是   │否   │
         │     │     ▼
         │    KV Cache 在 CXL？
         │   ┌───┼───┐
         │   │是  │否 │
         │   │   │   ▼
         │   │   KV Cache 在 NVMe？
         │   │  ┌──┼──┐
         │   │  │是 │否│
         │   │  │   │ │→ 完整 Prefill
         ▼   ▼  ▼   ▼ ▼
        执行推理（从相应层级加载）
              │
              ▼
         推理完成
              │
              ▼
         HBM 空间够？
        ┌───┼───┐
        │是 │否 │
        │   │   ▼
        │   驱逐最旧请求
        │   的 KV Cache → CXL
        │   (或 NVMe, 视优先级)
        ▼
    保留 KV Cache / 等待复用
```

**驱逐策略优先级**：
1. **LRU**: 最近最少使用（通用场景）
2. **LFU**: 最不频繁使用（多轮对话 Agent 场景）
3. **Attention Score**: 根据 Attention 权重保留高价值 token（精度敏感场景）
4. **Prefix Awareness**: 相同前缀的 prompt 优先保留（Chat 场景）

---

## 4. Intel 的 Context Memory Storage 方案

### 4.1 GDS — GPU 直连存储的核心使能

GDS (Gaudi Direct Storage) 是 Context Memory Storage 的关键使能技术：

```
  传统: Storage → CPU Page Cache → CPU DRAM → GPU HBM
              (3 次拷贝, 多次 PCIe 跨越)
  
  GDS:  Storage ─────────────────────→ GPU HBM
              (单跳, DMA 直写)
```

| 维度 | 传统 CPU 中转 | GDS Direct | 收益 |
|:----|:-----------:|:----------:|:----|
| 数据路径副本数 | 3x | **1x** | -67% 带宽消耗 |
| PCIe 跨越次数 | 2x (Storage→CPU, CPU→GPU) | **1x** (Storage→GPU) | -50% PCIe 压力 |
| CPU 占用 | 100% (中断驱动拷贝) | **0%** (硬件 DMA) | CPU 用于推理计算 |
| 延迟 (NVMe→GPU) | ~50-100μs | **~10-20μs** | -80% |
| 4GB 传输时间 | ~400-800ms | ~400ms (受限于 NVMe 带宽) | 延迟降低但带宽瓶颈相同 |

### 4.2 LMCache — 分层 KV Cache 管理

LMCache 是 Context Memory 的分层缓存管理框架：

```
          LMCache Runtime
               │
    ┌──────────┴──────────┐
    │    Cache Policy     │ ← LRU / LFU / Attention-based / Prefix-aware
    └──────────┬──────────┘
               │
    ┌──────────┴──────────┐
    │    Tier Manager     │ ← 感知各层级的延迟/带宽/容量
    └──────────┬──────────┘
               │
    ┌────┬─────┼─────┬────┐
    │    │     │     │    │
    ▼    ▼     ▼     ▼    ▼
   T0   T1    T1.5  T2   ...
  HBM  DDR5  CXL   NVMe
```

**LMCache 的智能策略**：

| 策略 | 触发条件 | 操作 | 适用场景 |
|:----|:--------|:----|:--------|
| **Warm-up Prefetch** | 检测到已知 prompt 前缀 | 从 CXL/NVMe 预加载 KV 到 HBM | 共享 system prompt 场景 |
| **Sliding Window** | 超过活跃窗口的 token | 从 HBM 卸载到 CXL | 超长上下文 (1M+) |
| **Agent Rollback** | Agent 需要回溯历史回合 | 从 NVMe 加载到 CXL/HBM | Agentic AI 多轮推理 |
| **Batch Eviction** | 高并发 HBM 不足 | 按优先级批量驱逐到 CXL | 高负载推理集群 |
| **Lazy Load** | 请求刚到，优先处理 | 仅加载 Attention 需要的部分 KV | 低延迟场景 |

### 4.3 存储后端

| 后端 | 协议 | 延迟 | 典型配置 | 管理方式 |
|:----|:----|:---:|:--------|:--------|
| **AI Server 本地 NVMe** | NVMe over PCIe | ~10μs | 4-8 × 8TB NVMe | GDS Direct |
| **CXL 内存池** | CXL.mem | ~300ns | 4-16 TB DDR5 | GDS + memkind |
| **存储服务器 JBOF** | NVMe over RDMA | ~20-30μs | 64-256 TB | GDS + RDMA |
| **对象存储 (远端)** | S3/NFS | ~ms | PB 级 | CPU 中转接口 |

> 详见 [KV Cache G3.5 存储](intel-kv-cache-g35.md) 和 [CXL KV Cache Pooling](intel-cxl-pooling.md)

### 4.4 KV Cache 生命周期管理

```
                        ┌──────┐
                        │Pre-  │ ← Agent 编写代码、阅读文档
                        │fill  │   生成第一轮 KV Cache
                        └──┬───┘
                           │
                     ┌─────▼─────┐
                     │   Decode   │ ← 逐 token 生成，持续读取 KV Cache
                     │  (多次)    │   KV Cache 增长 (追加写入)
                     └─────┬─────┘
                           │
               ┌───────────┴───────────┐
               │                       │
         ┌─────▼─────┐          ┌──────▼──────┐
         │ Agent     │          │ Request     │
         │ Tool Call  │          │ Complete     │
         │ (思考)     │          │ (等待下一轮) │
         └─────┬─────┘          └──────┬──────┘
               │                       │
         ┌─────▼─────┐          ┌──────▼──────┐
         │ 保留 HBM  │          │ HBM 不够?   │
         │ (复用)    │          ├── 是→CXL 层  │
         └───────────┘          │── 太久→NVMe │
                                └─────────────┘
                                       │
                               Agent 回到会话
                                       │
                               ┌───────▼──────┐
                               │ 从 CXL/NVMe  │
                               │ 加载 KV      │
                               │ 继续 Decode  │
                               └──────────────┘
```

---

## 5. 工程的挑战与权衡

### 5.1 带宽 vs 容量 vs 成本

```
               容量 (GB)
                  ↑
     NVMe SSD ───● (100TB, $0.15/GB)
                  │
                  │
     CXL DDR5 ───● (16TB, $10/GB)
                  │
                  │
     HBM ─────────● (192GB, $80/GB)
                  └─────────────────→ 带宽 (GB/s)
                       3.35 TB/s
```

**不存在的"完美介质"**：
- HBM: 带宽够、容量不够、成本太高
- NVMe: 容量够、成本低、带宽不够
- CXL: 折中方案，但带宽仍远不如 HBM

### 5.2 数据局部性的根本矛盾

```
KV Cache 的访问模式决定了它不适合卸载：

  Decode 阶段的 Attention 计算：
  
  for each head:
      scores = Q @ K^T          ← 需要读取所有 token 的 K
      output = softmax(scores) @ V  ← 需要读取所有 token 的 V
      
  → 每个 Step 都需要读取完整的 KV Cache ← 无法分页/分块
  → 卸载到低速介质 → 每个 Step 都慢 ← 不可隐藏
```

**与训练 Checkpoint 的关键区别**：

| 场景 | 数据量 | 访问频率 | 延迟容忍度 | 卸载可行性 |
|:----|:-----:|:-------:|:---------:|:---------:|
| 训练 Checkpoint | ~300 GB | 每小时一次 | 分钟级 | ✅ 完全可行 |
| **KV Cache** | ~4 GB/请求 | **每 token 一次** | **<1ms** | ❌ 极难 |

### 5.3 工程师的核心决策框架

```
Context Memory Storage 方案选型决策树：

Q1: 单请求 KV 能放进 HBM 吗？
├── ✅ 能 → 全部放 HBM，不需要存储方案
│           关注: PagedAttention 碎片管理
│
└── ❌ 不能 → 需要卸载
        │
        Q2: 上下文多长？什么模型？
        ├── 128K, 8B → 单请求 ~64 MB → 几乎全部 HBM
        ├── 1M, 70B → 单请求 ~3.5 GB → 必须部分卸载
        └── 1M+, 671B MoE → 单请求 ~5GB+ → 深度卸载
              │
              Q3: 延迟预算多少？
              ├── TTFT < 3s → CXL 层是卸载上限
              ├── TTFT < 10s → NVMe 可接受
              └── 非实时 → 全部 NVMe
                    │
                    Q4: 并发请求多少？
                    ├── 低并发 (< 16) → 少卸载
                    └── 高并发 (64+) → 必须多层卸载
                          │
                          Q5: KV 复用模式？
                          ├── 高复用 (相同 Prompt) → Prefix Cache + CXL
                          └── 低复用 (随机 Prompt) → 简单的 LRU + NVMe
```

---

## 6. Context Memory Storage 的未来方向

### 6.1 硬件层面

| 方向 | 预期效果 | 时间线 |
|:----|:--------|:------|
| **HBM4 容量提升** (256GB+/stack) | 单卡可容纳更多热 KV | 2026 |
| **CXL 3.0 Fabric 大规模部署** | 跨节点 KV 共享 | 2025-2026 |
| **CXL-attached NAND (JBOF)** | 低成本 G3.5 层 | 2025+ |
| **GPU 内建 KV Cache 管理硬件** | 硬件级 KV 驱逐/预取 | 2027+ |
| **HBM + DRAM 异构封装** | 片上大容量近存 | 2026+ |

### 6.2 软件层面

| 方向 | 解决的问题 | 代表项目 |
|:----|:---------|:--------|
| **智能预取** | 预测下一个需要加载的 KV，提前搬入 | LMCache |
| **KV Cache 量化** | 减少每 token 体积（FP16→FP8→INT4） | vLLM KV Cache Quant |
| **Streaming Attention** | 只保留活跃窗口，历史压缩 | StreamingLLM, Infini-Attention |
| **KV Cache 压缩** | 消除 KV 间的冗余（层间/头间共享） | KVT, ZipKV |
| **投机解码** | 减少每次 Decode 的 KV 读取次数 | SpecInfer, Medusa |
| **Cooperative KV Cache** | 多 GPU 共享/分片 KV Cache | DistAttention, SpotKV |

### 6.3 终极目标：消除存储问题

三种长期路线，使 Context Memory 不再是瓶颈：

| 路线 | 核心思想 | 典型方案 | 成熟度 |
|:----|:--------|:--------|:------:|
| **更大的 HBM** | 让所有 KV 留在 HBM | HBM4 (256GB) | 2026 |
| **更小的 KV** | 减少每 token 的 KV 体积 | 量化 (8x) + 稀疏 (4x) = 32x | 2025 |
| **更好的架构** | 改变 Attention 访问模式 | Linear Attention, Mamba | 研究阶段 |

---

## 7. 总结

```
Context Memory Storage 的核心矛盾：

  容量需求 (随上下文线性增长) + 并发数 → 远超 HBM 容量
                vs
  带宽需求 (每 Step 全量读取) → 不能离开 HBM

  解决方案不是"存哪里"，而是"什么时候存/什么时候加载"
```

**Intel 方案的三层路线**：

| 层次 | 解决什么 | 技术 |
|:----|:--------|:----|
| **使能层** | GPU 直连存储，消除 CPU 瓶颈 | GDS, NVMe over RDMA |
| **管理层** | 智能的 KV 生命周期、分层缓存 | LMCache, memkind |
| **优化层** | 减小每 token 体积、减少读取次数 | KV 量化, 投机解码 |

