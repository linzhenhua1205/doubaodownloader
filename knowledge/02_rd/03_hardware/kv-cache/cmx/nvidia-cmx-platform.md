# NVIDIA BlueField-4-Powered CMX Context Memory Storage Platform

> **Source**: https://developer.nvidia.com/blog/introducing-nvidia-bluefield-4-powered-inference-context-memory-storage-platform-for-the-next-frontier-of-ai/
> **Archived**: 2026-06-24（完整版重写）
> **Authors**: Moshe Anschel（首席系统架构师）、Einav Zilberstein（DOCA 存储高级产品经理）、Oren Duer（网络存储软件架构师）、Kirill Shoikhet（DGX Cloud 存储架构师，前 Excelero CTO）、Ronil Prasad（数据中心网络高级产品营销经理）
> **Published**: March 16, 2026
> **Tags**: Networking/Communications, BlueField DPU, DOCA, Dynamo, Spectrum-X Ethernet, AI Agent, AI Factory, AI Inference, GTC 2026, Rubin, Storage Networking & Security

---

## 一、核心背景：Agentic AI 带来的存储挑战

### 1.1 四个 AI Scaling Law 驱动存储需求爆炸

随着模型从简单聊天机器人演进为复杂的多轮 agentic 工作流，四类 scaling law 共同驱动推理上下文（KV Cache）容量需求激增：

| Scaling Law | 对存储的影响 |
|:-----------|:-------------|
| **Pretraining**（预训练） | 训练 checkpoint 存储 |
| **Post-training**（后训练） | RLHF/微调中间状态保存 |
| **Test-time scaling**（测试时扩展） | 长链推理中间结果 |
| **Agentic scaling**（智能体扩展） | **跨轮次、跨工具、跨会话的长期记忆** |

### 1.2 KV Cache 的本质转变

> "Agents are no longer stateless chatbots and depend on long-term memory of conversations, tools, and intermediate results, shared across services and revisited over time."

KV Cache 成为 **AI-native data class**，具有独特二重性：
- **Critical for performance**（性能关键）
- **Inherently ephemeral**（本质临时性）

### 1.3 KV Cache 的三种属性（博客原文）

> "Unlike immutable enterprise records, inference context is **derived and recomputable**, demanding a storage architecture that prioritizes power and cost efficiency as well as speed and scale, over traditional data durability."

| 属性 | 含义 | 对存储设计的影响 |
|:-----|:-----|:----------------|
| **Transient**（临时的） | 会话结束后可丢弃 | 不需要持久化保证 |
| **Derived**（派生的） | 从模型+输入计算得出 | 可重新生成 |
| **Recomputable**（可重算的） | 丢失后可重新计算 | 不需要 replication/redundancy |

---

## 二、存储层级体系：G1–G4 与新增 G3.5

### 2.1 传统层级及其局限

| 层级 | 介质 | 延迟 | 用途 | 关键瓶颈 |
|:-----|:-----|:-----|:------|:---------|
| **G1** | GPU HBM | 纳秒级 | 活跃生成中的 hot KV | 容量有限（GB 级），很快耗尽 |
| **G2** | 系统 DRAM | ~100ns | 从 HBM 卸载的 staging/buffering | 容量受限于主机内存 |
| **G3** | 本地 SSD（NVMe） | ~10μs | 短时间复用的 warm KV | **绑死单节点**，难以扩展和管理 |
| **G4** | 共享对象/文件存储 | 毫秒级 | cold 工件、持久化结果 | 为 durability 而非 KV 优化，延迟高、功耗大 |

### 2.2 G3.5 CMX 层（新增）

> "The platform establishes a new **G3.5** layer, an Ethernet-attached flash tier optimized specifically for KV cache."

**定位**: 填补 G1–G3 与 G4 之间的空白容量
**声明**: "CMX fills this missing KV capacity between G1–G3 and G4"

**关键属性**:
| 属性 | 数值 |
|:-----|:------|
| 容量 | **PB 级**（per GPU pod） |
| 互联 | **Spectrum-X Ethernet RDMA** |
| 介质 | 闪存（flash-based） |
| 功耗 | **5× 能效**优于传统存储 |
| 性能 | **5× 更高 TPS** |
| 延迟 | 介于 G3（本地 SSD）和 G4（共享存储）之间 |

### 2.3 G4 的职责重新定义

> "With a large portion of latency-sensitive, ephemeral KV cache now served from the G3.5 tier, durable G4 object and file storage can be reserved for what truly needs to persist over time."

G4 现在专注于：inactive multiturn KV state、query history、logs、multiturn inference artifacts。

---

## 三、CMX 平台架构

### 3.1 完整软件栈（从上到下）

```
┌─────────────────────────────────────────────────┐
│          Inference Framework Layer               │
│  ┌────────────────┐  ┌────────────────────────┐  │
│  │ NVIDIA Dynamo  │  │   NIXL (Inference      │  │
│  │ KV Block Mgr   │  │   Transfer Library)    │  │
│  └───────┬────────┘  └───────────┬────────────┘  │
├──────────┼───────────────────────┼────────────────┤
│          ▼                       ▼                 │
│  ┌─────────────────────────────────────────────┐  │
│  │          DOCA Memos Framework               │  │
│  │  KV 通信与存储层（first-class resource）     │  │
│  │  - 将 KV block 视为一等公民管理              │  │
│  │  - 开放接口，存储伙伴可扩展                   │  │
│  └───────────────────┬─────────────────────────┘  │
├──────────────────────┼────────────────────────────┤
│                      ▼                              │
│  ┌─────────────────────────────────────────────┐  │
│  │  Topology-Aware Orchestration (Grove)       │  │
│  │  拓扑感知工作负载编排，KV locality 感知      │  │
│  └───────────────────┬─────────────────────────┘  │
├──────────────────────┼────────────────────────────┤
│                      ▼                              │
│  ┌─────────────────────────────────────────────┐  │
│  │  BlueField-4 DPU                            │  │
│  │  KV I/O 平面卸载（NVMe-oF, Object/RDMA）    │  │
│  │  加密/CRC 硬件加速引擎                       │  │
│  └───────────────────┬─────────────────────────┘  │
├──────────────────────┼────────────────────────────┤
│                      ▼                              │
│  ┌─────────────────────────────────────────────┐  │
│  │  Spectrum-X Ethernet                        │  │
│  │  高级拥塞控制 · 自适应路由 · 无损 RoCE      │  │
│  │  深度遥测 · 硬件性能隔离                     │  │
│  └───────────────────┬─────────────────────────┘  │
├──────────────────────┼────────────────────────────┤
│                      ▼                              │
│  ┌─────────────────────────────────────────────┐  │
│  │  NVMe-oF / NVMe KV Extensions              │  │
│  │  标准 NVMe 传输 + KV 扩展                   │  │
│  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 3.2 各层职责详解

#### NVIDIA Dynamo
- 推理调度框架
- 包含 **KV Block Manager**，负责 KV 块在 G1–G3.5–G4 层级间的生命周期管理
- **Prestaging**: 在 decode 阶段开始前，从 CMX 将 KV 块预加载到 G2/G1
  > "KV managers in these frameworks prestage KV blocks, bringing them from CMX into G2 or G1 memory ahead of the decode phase."

#### NIXL（NVIDIA Inference Transfer Library）
- KV 跨层级传输库
- 负责 Dynamo 与底层存储之间的数据传输抽象

#### DOCA Memos
- KV 通信与存储层
- 将 context cache 作为 **first-class resource**（一等公民资源）管理
- 利用 KV block 的独特属性和推理模式进行优化
- BlueField-4 通过 DOCA Memos 在闪存介质与 GPU 之间高效传输 KV Cache
- **支持开放接口**，允许存储合作伙伴扩展 G3.5 解决方案

#### NVIDIA Grove
- 拓扑感知编排层
- 跨机架放置工作负载时感知 KV locality
- 确保工作负载在节点间迁移时仍能重用上下文

### 3.3 KV Tiering 全链路

在计算节点级别，KV 跨越以下层级：
1. **GPU HBM** — 活跃 token 生成的 hot KV
2. **Host Memory** — staging/buffering
3. **Local SSDs** — warm KV（短时间）
4. **CMX（G3.5）** — 共享 KV Cache（新增核心层）
5. **Network Storage（G4）** — 持久化冷数据

---

## 四、BlueField-4 硬件加速

### 4.1 核心能力

| 能力 | 说明 |
|:-----|:------|
| **超高速连接** | 集成多核 NVIDIA CPU + HBM |
| **线速加密** | 专用硬件加速引擎，不降吞吐 |
| **CRC 数据保护** | 端到端数据完整性 |
| **NVMe-oF 终结** | 硬件卸载 NVMe over Fabrics 协议 |
| **Object/RDMA 终结** | 硬件卸载对象存储和 RDMA 协议 |
| **KV I/O 加速** | BlueField-4 同时运行在计算节点 DPU 和 CMX 存储 tray 控制器上 |

### 4.2 卸载价值

> "The architecture uses BlueField-4 to accelerate KV I/O and control plane operations, across DPUs on the Rubin compute nodes and controllers in CMX storage trays, reducing reliance on the host CPU and minimizing serialization and host memory copies."

---

## 五、Spectrum-X 以太网角色

### 5.1 作为 CMX 的网络基础

> "Spectrum-X Ethernet provides the AI-optimized RDMA fabric that links CMX flash enclosures and GPU nodes with predictable, low-latency, high-bandwidth connectivity."

### 5.2 关键网络特性

| 特性 | 作用 |
|:-----|:------|
| **高级拥塞控制** | 避免大规模 RDMA 流量拥塞 |
| **自适应路由** | 动态选择最优路径 |
| **无损 RoCE** | 零丢包保证 |
| **低抖动/尾延迟** | 一致性 KV 访问性能 |
| **深度遥测** | 实时网络可见性 |
| **硬件性能隔离** | 多租户场景下隔离保证 |
| **标准化/互操作** | 兼容开放网络软件 |

---

## 六、能效与性能

### 6.1 为什么 CMX 比传统存储更高效

传统存储的问题：
- 基于 x86 控制器
- 大量功耗花费在 metadata 管理、复制、后台一致性检查
- 这些对 ephemeral、recomputable 的 KV Cache **完全不必要**

CMX 通过**消除这些不必要的开销**实现 5× 能效提升。

### 6.2 性能声明汇总

| 指标 | 数值 | 机制 |
|:-----|:------|:------|
| TPS 提升 | **5× 更高** | Prestaging 消除 decode stall + 更高存储带宽 |
| 能效提升 | **5× 更好** | 移除不必要的 durability/replication 开销 |
| 容量 | **PB 级**（per pod） | 专为 KV Cache 设计的闪存层级 |
| GPU 利用率提升 | **减少空闲** | Prestaging 避免 GPU 等待 KV 数据 |

### 6.3 Tokens-per-watt 作为核心度量

> "every megawatt of power is ultimately judged by how many useful tokens it can deliver."

---

## 七、TCO 影响

> "Together, these gains improve total cost of ownership (TCO) by enabling teams to fit more usable AI capacity into the same rack, row, or data center, extend the life of existing facilities, and plan future expansions around GPU capacity instead of storage overhead."

---

## 八、关键设计原则总结

| 原则 | 说明 |
|:-----|:------|
| **Stateless** | 无状态共享 KV Cache，不绑定特定 GPU 节点 |
| **Open interfaces** | DOCA Memos 支持开放接口 |
| **Standards-based** | 标准 NVMe 和 NVMe-oF 传输 |
| **RDMA 直连** | Spectrum-X RoCEv2 |
| **No redundancy overhead** | 不为 ephemeral 数据做复制/校验 |
| **Pod-level** | 跨节点共享，非单机 |

---

## 九、参考链接

- **CMX 新闻稿**: [Press Release](https://developer.nvidia.com/blog/introducing-nvidia-bluefield-4-powered-inference-context-memory-storage-platform-for-the-next-frontier-of-ai/)
- **解决方案概览**: Solution Overview（NVIDIA 官方）
- **GTC 2026 主题演讲**: Jensen Huang 主题演讲
- **Vera Rubin POD**: [NVIDIA Vera Rubin POD 博客](nvidia-vera-rubin-pod-seven-chips-five-systems.md)
- **G3.5 分析**: [G3.5 KV Cache 共享存储网络性能逐层分析](../../02_rd/03_hardware/01_hw_core/g35-kv-cache-storage-network-analysis.md)

---

## 相关页面

- [NVIDIA Vera Rubin POD: Seven Chips, Five Rack-Scale Systems](nvidia-vera-rubin-pod-seven-chips-five-systems.md) — Vera Rubin POD 硬件体系
- [G3.5 KV Cache 共享存储网络性能逐层分析](../../02_rd/03_hardware/01_hw_core/g35-kv-cache-storage-network-analysis.md) — 带宽逐层计算
- [NVIDIA CMX G3.5 层定义与 KV Cache 综述](../nvidia-cmx-g35-overview.md) — （待建）
