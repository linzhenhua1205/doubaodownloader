# NVIDIA CMX 软件架构深度分析 — 算力·调度·存储三维拆解与非NVIDIA等价实现指南

> **版本**: v1.0 · **日期**: 2026-06-29 · **类型**: 技术深度分析
> **素材来源**: NVIDIA 官方 CMX 白皮书/博客 + 东兴证券超节点专题报告 + 豆包深度对话
> **核心目的**: 以 CMX 软件架构为蓝本，为非 NVIDIA GPU（昇腾、AMD MI、寒武纪等）提供分层可复现的等价实现技术路线
>
> **关键参考**:
> - [NVIDIA BF4 CMX Introduction](https://developer.nvidia.com/blog/introducing-nvidia-bluefield-4-powered-inference-context-memory-storage-platform-for-the-next-frontier-of-ai/)
> - [NVIDIA Research: Improving Inference with CMX](https://developer.nvidia.com/blog/research-note-improving-inference-nvidias-inference-context-memory-storage-platform/)
> - [NVIDIA STX CMX Infrastructure for Agentic AI](https://developer.nvidia.com/blog/nvidia-stx-cmx-infrastructure-for-agentic-ai-context-storage/)
> - [What is CMX Context Memory Storage](https://docs.nvidia.com/what-is-cmx-context-memory-storage.html)
> - [source archive](./2026-06-29-nvidia-cmx-software-architecture.md)

---

## 🧭 1. CMX 全景定位

### 1.1 解决了什么核心问题？

Transformer 自回归推理中，**KV 缓存随上下文线性增长**，远超单 GPU HBM（G1）容量：

| 模型参数量 | 上下文长度 | 单层 KV 大小 | 全部层 | 所需 HBM |
|:----------|:----------|:-------------|:------|:--------|
| 70B | 128K | ~1.8 MB/层 | 约 144 MB | ~144 MB |
| 70B | 1M | 约 14 MB/层 | 约 1.1 GB | >1 GB |
| 1T MoE | 1M | 约 40 MB/层 | 约 3.2 GB | >3 GB |

**CMX（Context Memory X）的本质**：在 G3（CPU DRAM，~100ns-1μs）与 G4（对象存储，ms 级）之间插入一个 **G3.5 层**——Pod 级分布式 KV 缓存层，延迟 1~5 μs，采用 **DPU (BlueField-4) 全卸载 + NVMe SSD 池化** 架构。

### 1.2 四层内存层次

```
G1: GPU HBM          ─── 热 KV，数十 ns    ─── GPU 算力本地
G2: CPU DRAM         ─── 温 KV，数百 ns    ─── 主机侧缓冲
──── CMX 核心 ─────
G3.5: DPU+NVMe 池   ─── 冷 KV，1~5 μs    ─── Pod 共享层
G4: 对象存储 (S3)    ─── 归档，ms 级       ─── 离线持久化
```

**关键判断**：CMX 不是 SSD 阵列，是 **软硬件深度耦合的 AI 原生存储栈**，所有软件栈围绕 KV 块设计。

---

## 🔧 2. 算力维度架构拆解

### 2.1 异构双算力模型

```
┌─────────────────────────────────────────────────┐
│  GPU (XPU) 侧                                    │
│  ┌─────────────────────┐  ┌──────────────────┐   │
│  │ Transformer Compute  │  │ NIXL Transport   │   │
│  │ (SM 主力计算)        │  │ (空闲 SM 零拷贝)   │   │
│  └─────────────────────┘  └──────────────────┘   │
│         ▲                     │                    │
│         │ KV Block            │ RDMA              │
│         ▼                     ▼                    │
├─────────────────────────────────────────────────┤
│  DPU (BF4) 侧                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │  X-Memos 存储引擎                             │  │
│  │  · NVMe 队列管理（硬件卸载）                   │  │
│  │  · 数据完整性校验（硬件流水线）                 │  │
│  │  · AES-GCM 加密（硬件）                       │  │
│  │  · RDMA 协议处理（ROCEv2/NVMe-oF）           │  │
│  │  · 板载 LPDDR 一级缓存                        │  │
│  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### 2.2 NIXL — GPU 侧零拷贝传输层

**与 CUDA Kernel 深度融合的运行时库**，驻留 GPU 显存：

| 特性 | NVIDIA NIXL | X-CMX XIXL (等价实现) |
|:----|:-----------|:---------------------|
| 调用方式 | CUDA Kernel 内直接调用 | HIP/CANN Kernel 内调用 |
| 数据传输 | 闲置 SM 并发搬运，不抢占计算 SM | 拆分专用计算 SM 与传输 SM |
| 拷贝路径 | GPU↔CMX 直通，零主机拷贝 | GPU↔DPU 直通，零主机拷贝 |
| 地址语义 | CUDA 驱动扩展远端内存寻址 | XPU 统一虚拟内存层扩展远端存储空间 |

**关键设计**：
- 数据流全程规避主机内存拷贝，GPU 可直接远端寻址 G3.5 共享 KV 池
- Decode 算力流水线与数据搬运流水线完全并行解耦

### 2.3 BF4 DPU — 存储面专用算力

BF4 提供 **完全隔离的存储算力**：

1. **KV 块硬件管理引擎**：DPU 硬件加速 KV 块分配、回收、引用计数、一致性校验 → **元数据算力开销降低 90%**
2. **NVMe 队列优先级隔离**：划分低延迟热 KV 队列、批量冷 KV 队列
3. **RDMA 多链路调度**：拥塞自动切换低负载通道，动态调整传输块大小
4. **本地一级缓存**：BF4 板载 LPDDR 作为 CMX 一级缓存

### 2.4 非 NVIDIA 算力等价实现要点

```
最难复刻的部分: CUDA + BF4 双异构卸载 → Cache 数据移动/元数据/协议完全隔离主机 CPU
等价策略:
  1. XIXL (XPU IXL): 基于开源 HIP/昇腾 CANN 实现 Device 侧传输内核
  2. 通用 DPU 兜底: SPDK + RDMA 软件卸载，选择带硬件 RDMA 引擎的通用 DPU
  3. XPU 统一虚拟内存层: 扩展远端存储寻址语义，远端 X-CMX 与本地 HBM 寻址一致
```

---

## ⚙️ 3. 调度维度架构拆解

### 3.1 三层调度体系

```
┌──────────────────────────────────────────────────────────┐
│ L1: X-Grove（全局调度 — 控制面）                          │
│  · 运行在集群控制节点，对接 K8s                            │
│  · 调度决策：会话级（新建/迁移/恢复）                       │
│  · 拓扑感知：XPU/DPU/SSD 三重亲和调度                      │
│  · 故障迁移：KV 元数据全局副本，迁移后直接读取远端缓存       │
│  · 多租户配额：Namespace 硬隔离                            │
│  调度周期: ~5s（节点心跳上报）                              │
├──────────────────────────────────────────────────────────┤
│ L2: X-Dynamo（本地调度 — 数据面）                          │
│  · 运行于主机侧推理进程，XIXL 上层调度中枢                   │
│  · 调度决策：KV Block 级（<1ms）                           │
│  · 冷热打分：LRU + 访问频次权重混合                         │
│  · 预取预测：基于 Decode 序列预测，Decode 前 1~2ms 异步拉取 │
│  · 驱逐策略：HBM 容量不足时后台推送至 CMX                    │
├──────────────────────────────────────────────────────────┤
│ L3: X-Memos（硬件调度 — 执行面）                            │
│  · 运行于 DPU 裸机，SPDK 标准接口                           │
│  · SSD 分片均衡：哈希打散 + 后台迁移                         │
│  · NVMe 队列隔离：热队列低延迟 / 冷队列批量                   │
│  · RDMA 链路负载：拥塞切换 + 动态块大小                      │
└──────────────────────────────────────────────────────────┘
```

### 3.2 三条独立调度流水线

```
时间线 → ────────────────────────────────────────────────
                    Decode Step N           Decode Step N+1
                    ↓                       ↓
Prefetch ──────▶  [拉取 KV Block] ──────▶  [计算] ──────▶
                      │                       │
Evict  ────────▶  [推送冷 KV] ────────▶  [释放 HBM] ──▶
                      │                       │
Share ─────────▶  [前缀匹配] ─────────▶  [只读引用] ──▶
                      │                       │
              ▲ 三条流水线独立执行，GPU 计算与数据搬运完全并行 ▲
```

### 3.3 X-Grove 全局调度算法

**调度输入**（每 5s 全集群上报）：
```
每台 XPU 主机: 算力利用率、HBM 容量、PCIe 拓扑、RDMA 端点
每台 CMX DPU: 已用/总容量、NVMe 盘数量、RDMA 带宽利用率、健康状态
```

**调度决策矩阵**：

| 调度场景 | 策略 | 目标 |
|:--------|:-----|:-----|
| **新建会话** | 优先分配同 namespace 已有 DPU 分片 | 最大化前缀缓存复用 |
| **推理任务调度** | 同机架/低延迟 RDMA 链路 DPU | 降低预取延迟 |
| **高并发在线** | 低延迟同机架 DPU | 延迟 SLA |
| **离线批量** | 跨机架大容量存储节点 | 吞吐优先 |
| **故障迁移** | 全局匹配替代 XPU + 有副本的 DPU | 无上下文丢失 |
| **负载均衡** | 均匀打散到多 DPU 节点 | 避免单盘 SSD IO 瓶颈 |

### 3.4 非 NVIDIA 调度等价实现

| 层级 | NVIDIA | 开源替代 | 差距 | 解决策略 |
|:----|:-------|:---------|:-----|:---------|
| L1 | Dynamo | **LMCache** | 缺少全局调度 | 自研 X-Grove 对接 K8s |
| L2 | NIXL 调度 | vLLM Prefix Cache | 无跨节点预取 | XIXL + 预测预取 |
| L3 | DOCA NVMe | **SPDK** | 无热冷队列隔离 | SPDK 队列优先级扩展 |

**基准验证方法**：
1. 单机 XPU → 冷 KV 缓存至本地 DPU SSD（验证 XIXL 零拷贝）
2. 多机 Pod → KV 全局共享（验证 X-Grove 调度）
3. 故障场景 → 会话迁移上下文连续（验证高可用）

---

## 💾 4. 存储维度架构拆解

### 4.1 核心设计哲学

> 抛弃通用文件系统，KV Block 为唯一最小存储单元，去中心化分布式元数据，裸 NVMe 直通。

```
┌─────────────────────────────────────────────────┐
│  1. 客户端 GPU 侧存储抽象                         │
│     · CUDA 驱动扩展：远端内存寻址语义               │
│     · XPU 统一虚拟地址：远端 X-CMX == 本地 HBM     │
│     · 容量透明聚合：G1+G2+G3.5 统一返回             │
├─────────────────────────────────────────────────┤
│  2. DPU 存储数据平面 (X-Memos)                    │
│     · 裸 NVMe 直通（无 FS 层）                     │
│     · KV Block 固定 64K Token 粒度对齐 HBM        │
│     · 块地址直接映射 NVMe LBA                     │
│     · 板载 LPDDR 一级缓存                          │
├─────────────────────────────────────────────────┤
│  3. 分布式元数据层                                 │
│     · 去中心化哈希分片                              │
│     · DPU 本地缓存元数据，无中心化单点              │
│     · 元数据字段：KV_ID·Session·Hot·Shard·Ref·Comp│
└─────────────────────────────────────────────────┘
```

### 4.2 KV Block 生命周期

```
[Prefill]
  输入上下文计算 HBM 占用
  ↓ 溢出 → 触发 CMX 异步预分配
  ↓ 未溢出 → NIXL 写入 G1 HBM

[Decode loop]
  Prefetch: 提前 1~2ms 预测 → XIXL 异步拉取 → Device 回调 → 计算
  Evict:    HBM 挤占 → X-Dynamo 选冷 KV → XIXL 推送至 X-Memos
  Share:    L2 前缀匹配 → 多会话只读引用同一 KV Block

[Session End]
  TTL 自动回收 → X-Memos 批量释放 SSD 空间
  可选持久化 → G4 对象存储（S3-over-RDMA）
```

### 4.3 一致性模型

| 操作 | 一致性级别 | 策略 |
|:----|:----------|:-----|
| KV Block 只读共享 | **最终一致性** | 多 GPU 只读引用同一副本 |
| 写入新 KV Block | **DPU 本地强一致性** | 单 DPU 内保证写入原子性 |
| 传输校验 | CRC 校验 | 自动校验，单盘故障自动迁移 |

### 4.4 非 NVIDIA 存储等价实现

| NVIDIA 组件 | 开源替代 | 功能差距 | 补充开发 |
|:-----------|:---------|:---------|:---------|
| CMX G3.5 分层 | - | 无直接开源替代 | 自研 X-CMX 分层架构 |
| NIXL 零拷贝 | - | GPU Kernel 传输库 | 基于 HIP/CANN 开发 XIXL |
| DOCA NVMe 卸载 | **SPDK** | 功能完整 | 直接可用，无差距 |
| CMX 分布式元数据 | - | 无成熟方案 | 自研去中心化 KV 元数据集群 |
| Dynamo kv 调度 | **LMCache** | 缺少全局调度 | 二次开发补充冷热调度+引用计数 |
| NCCL CMX 通信 | **MCCL 自研** | NVLink 私有原语 | 自研集合通信库 |
| CMX 监控 | Prometheus | 标准 | 直接复用 |

**硬件依赖约束**：

| 需求 | NVIDIA BF4 | 通用 DPU (Intel IPU/AMD DPU) | 策略 |
|:----|:----------|:----------------------------|:----|
| NVMe 队列卸载 | ✅ 硬件 | ⚠️ 弱于 BF4 | SPDK 软件卸载兜底 |
| RDMA 引擎 | ✅ 硬件 | ✅ 可选配备 | 选型强制要求 |
| 板载 LPDDR | ✅ 16GB+ | ⚠️ 容量小 | 缓冲区缩小，依赖 SSD |
| AES-GCM 卸载 | ✅ 硬件 | ⚠️ 部分支持 | 软件加密兜底 |

---

## 🔗 5. NVLink 与 UB 协议分析

### 5.1 NVLink 体系回顾

| 版本 | 带宽/链路 | 发布 | 典型拓扑 |
|:----|:---------|:-----|:---------|
| NVLink 1.0 | 40 GB/s | 2016 (P100) | GPU↔GPU 点对点 |
| NVLink 2.0 | 50 GB/s | 2017 (V100) | DGX-1: 8×V100 all-to-all |
| NVLink 3.0 | 75 GB/s | 2020 (A100) | DGX-A100: NVSwitch |
| NVLink 4.0 | 100 GB/s | 2022 (H100) | NVLink-Network + NVLink-C2C |
| NVLink 5.0 | 200 GB/s | 2025 (GB300) | GB300 NVL72 |


### 5.2 UB 协议的不可替代性

UB（Ultra Ethernet 或通用开放互联协议）虽然在协议栈完整性、物理层兼容性、带宽指标上已达到甚至部分超越 NVLink，但存在 **三个根本性技术壁垒**：

```
壁垒 1: PHY 层
  NVLink 是 NVIDIA 私有 PHY → 物理层面无法互通
  → UB 只能作为开放芯片的互联，不能接入 NVIDIA GPU
  
壁垒 2: NVSwitch SHARP
  SHARP (Scalable Hierarchical Aggregation and Reduction Protocol)
  是 AllReduce 等集合通信的关键硬件加速引擎
  → UB 生态无对等实现
  
壁垒 3: 缓存一致性
  NVLink 提供硬件级强一致性
  → UB 与 NVLink 的缓存一致性模型存在语义差距
```

**结论**：
- **对 NVIDIA 系统**: UB 无法取代 NVLink
- **对非 NVIDIA AI 芯片**（昇腾/AMD MI/寒武纪）: **UB 完全可作为 NVLink 功能等价替代方案**，甚至在统一协议栈、开放生态、全对等架构方面具备结构性优势

---

## 🏗️ 6. X-CMX 非 NVIDIA 等价实现框架

### 6.1 四大模块定义

| 模块 | 对标 | 角色 | 关键接口 |
|:----|:-----|:-----|:---------|
| **XIXL** | NIXL | XPU 传输库 | 零拷贝异步传输 + Device 端回调 |
| **X-Dynamo** | Dynamo | KV 调度 | 冷热淘汰 + 预测预取 + 驱逐策略 |
| **X-Memos** | CMX Storage | DPU 引擎 | 裸 NVMe + 分片均衡 + RDMA 调度 |
| **X-Grove** | CMX Scheduler | 全局调度 | 会话调度 + 配额管理 + 故障迁移 |

### 6.2 全链路时序（标准 Decode 预取流程）

```
Step 1: X-Dynamo 预测解码所需 KV 块
         ↓ topic 等) 调用 XIXL 发起异步预取请求
Step 2: X-Dynamo 调用 XIXL 发起异步预取请1→2ms 前)
         ↓
Step 3: XIXL (GPU 侧) → RDMA 发送 → X-Memos (DPU 侧)
         ↓
Step 4: X-Memos 查询分布式元数据 → 定位目标 KV 块所在 SSD
         ↓
Step 5: NVMe 直接读取 KV Block → RDMA send → GPU HBM
         ↓
Step 6: Device 回调通知 X-Dynamo 预取完成 → 启动 Transformer 解码计算
```

### 6.3 实现路线图

| 阶段 | 目标 | 工作量 | 验收标准 |
|:----|:-----|:------|:---------|
| **短期** | 基础等价 | 2-3 月 | G3.5 分层 + XIXL 零拷贝 + 单机 DPU |
| **中期** | 调度等价 | 3-4 月 | KV 冷热预取/驱逐 + Pod 级 Grove + SSD 分片均衡 |
| **长期** | 全局等价 | 4-6 月 | KV 全局共享 + 多租户隔离 + 全链路监控 |

### 6.4 性能基线

| 指标 | 目标值 |
|:----|:------|
| G3.5 远端 KV 预取延迟 | **1~5 μs** |
| KV 复用率提升（长上下文/多并发） | **40%~80%** |
| 跨节点 RDMA 流量下降 | **60%+** |
| 集群硬件综合利用率提升 | **30%+** |
| 元数据算力开销降低（DPU 硬件卸载） | **90%** |
| Session 迁移恢复时间 | **<10ms** |
| 推理吞吐抖动衰减 | **<5%** |

---

## 📊 7. 竞争格局与战略启示

### 7.1 NVIDIA CMX 的定位

CMX 是 NVIDIA 从"算力领先"向"**全栈推理基础设施**"延伸的关键拼图：
- **算力** → CUDA + Tensor Core
- **网络** → NVLink + NVSwitch
- **存储** → CMX (G3.5)
- **管理** → 全局调度

### 7.2 对非 NVIDIA 生态的启示

1. **CMX 的价值不仅仅是存储** — 它是**算力-网络-存储三维协同的系统工程**，单一维度跟进无法等价
2. **最难的壁垒不在存储，在算力卸载** — CUDA + BF4 双异构卸载是将存储协议栈完全移出主 CPU，非 NVIDIA 生态的最大差距在 DPU 与 GPU 的耦合深度
3. **UB 协议是弯道超车的机会** — 开放互联标准 + 统一协议栈是非 NVIDIA 生态的潜在结构性优势
4. **可以先做调度层的开源实现** — LMCache + SPDK 已经覆盖底层基础，缺的是全局调度编排

---

## 📋 8. 总结

| 维度 | NVIDIA CMX 核心能力 | 非 NVIDIA 等价策略 | 难度 |
|:----|:-------------------|:------------------|:----:|
| **算力** | CUDA+BF4 双异构卸载 | XIXL (基于 HIP/CANN) + 通用 DPU | 🔴 高 |
| **调度** | 三层全局拓扑感知调度 | LMCache 基础 + 自研 X-Grove | 🟠 中 |
| **存储** | 抛弃 FS 的裸 NVMe KV 池 | SPDK + 自研分布式元数据 | 🟠 中 |
| **互联** | NVLink + SHARP | UB 协议（开放生态优势） | 🟡 可 |

---

> **CHANGELOG**
>
> | 日期 | 版本 | 变更 |
> |:----|:----|:-----|
> | 2026-06-29 | v1.0 | 初始版本，基于豆包深度对话 + NVIDIA 官方文档 + 行业报告综合整理 |
