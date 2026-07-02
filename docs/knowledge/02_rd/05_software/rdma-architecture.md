# RDMA 技术架构深度解析

> 核心链路：[GPU Direct 技术](gpu-direct-technology.md) → [RDMA 架构] → [NCCL 集合通信](multi-gpu-collective-communications.md) → [拓扑感知调度](network-topology-aware-scheduling.md)
> 来源: [johng.cn](https://johng.cn/ai/rdma-brief) | 归档: 2026-06-04

---

## 🎯 核心定位

**RDMA（Remote Direct Memory Access）** 是远程绕过 OS Kernel 直接访问远端内存的技术，是 **GPU Direct RDMA**、**NCCL 集合通信** 以及 **拓扑感知调度** 的底层通信基石。

三大核心理念：
- ✅ **CPU Offload** — 远端 CPU 不参与，缓存不被填充
- ✅ **Kernel Bypass** — 用户态 Verbs 直通网卡，无需上下文切换
- ✅ **Zero Copy** — 数据直接从应用缓冲区到远端应用缓冲区

---

## 📊 三大实现方案对比

| 维度 | InfiniBand | RoCE v2 | iWARP |
|:-----|:-----------|:--------|:------|
| **标准组织** | IBTA | IBTA | IETF |
| **传输层** | 自有协议（硬件实现） | UDP/IP | TCP/IP |
| **网络层** | L2 LID / L3 GRH | L3 IP | L3 IP |
| **交换机要求** | 专用 IB 交换机 | 无损以太网交换机 | 标准以太网交换机 |
| **性能** | ⚡ 最佳 | ⚡ 与 IB 相当 | 稍差（TCP 开销） |
| **成本** | 高（专用全部硬件） | 中（仅网卡特殊） | 低（仅网卡特殊） |
| **典型延迟** | <1μs | 1~3μs | 5~10μs |
| **广域网支持** | ❌ | ❌ | ✅ |
| **代表产品** | Mellanox NDR 400Gb/s | Mellanox ConnectX | Chelsio T6 |
| **适用规模** | 数万 GPU | 数千 GPU | 存储为主 |

---

## 1️⃣ InfiniBand 架构深度解析

### 历史背景

```
1999: Future I/O (Intel/IBM/HP) vs Next Generation I/O (Compaq/Dell/Sun)
         ↓ 合并
2000: InfiniBand 1.0 Spec发布，目标替代PCI架构
2001: Mellanox推出10 Gbit/s设备
         ↓ 互联网泡沫破裂
Intel → PCIe / 微软 → 停止IB开发
         ↓
Sun/日立坚持研发 → 超算/存储场景广泛应用
         ↓
2010s: 大数据+AI爆发 → IB从超算走向AI
2020: NVIDIA收购Mellanox
2024: NDR 400Gb/s单端口 + PCIe Gen5x16
```

### 架构组成

```
┌─────────────────────────────────────┐
│           Subnet Manager            │ ← 发现拓扑/分配LID/配置转发表
└────────────┬────────────────────────┘
             │ 管理
    ┌────────┴────────┬─────────┐
    │                  │         │
┌───▼────┐   ┌───▼────┐  ┌───▼────┐
│  HCA   │   │  HCA   │  │  TCA   │  ← Channel Adapters
└───┬────┘   └───┬────┘  └───┬────┘
    │            │            │
┌───▼────────────▼────────────▼────┐
│         Switch (L2转发)           │
│   基于 LRH.LID 转发数据包          │
└───────────────────────────────────┘
    │
┌───▼──────────────┐
│  Router (L3转发)  │ ← 跨子网：基于GRH.GUID
└──────────────────┘
```

### 分层协议栈

| 层 | 功能 | 关键协议头 |
|:---|:-----|:-----------|
| **传输层** | 按序交付、MTU分段、4种传输服务(RC/UC/RD/UD) | BTH(12B) + ETH(变长) |
| **网络层** | 跨子网路由 | GRH(40B，类IPv6格式) |
| **链路层** | 交换转发、VL QoS、基于信用的流控、CRC校验 | LRH + ICRC/VCRC |
| **物理层** | 电/光特性、Link聚合 | 8b/10b编码 |

#### 传输层四种服务模式

| 模式 | 可靠 | 连接 | 类比 | 典型用途 |
|:----|:----:|:----:|:-----|:---------|
| **RC** (Reliable Connection) | ✅ | ✅ | TCP | 高可靠GPU通信 |
| **UC** (Unreliable Connection) | ❌ | ✅ | — | 容忍丢包场景 |
| **RD** (Reliable Datagram) | ✅ | ❌ | — | 多对多可靠（硬件昂贵） |
| **UD** (Unreliable Datagram) | ❌ | ❌ | UDP | 多播/控制消息 |

#### 链路层 QoS 机制

- **Virtual Lanes (VL)**：15 个标准 VL + VL15(管理，最高优先级)
- **Service Level (SL)**：16 级，通过 SL→VL 映射实现 QoS
- **基于信用的流控**：发送端根据接收端信用额度发送，避免丢包

### 数据包封装

```
┌──────┬──────┬──────┬──────┬────────┬──────┐
│ LRH  │ GRH  │ BTH  │ ETH  │ Payload│ ICRC │
│(8B)  │(40B) │(12B) │(变长) │ (≤4KB) │(4B)  │
└──────┴──────┴──────┴──────┴────────┴──────┘
                                        ┌──────┐
                                        │ VCRC │
                                        └──────┘
```

- **LRH** (Local Route Header): LID 寻址、VL、SL
- **GRH** (Global Route Header): 跨子网，128-bit GID (类似 IPv6)
- **BTH** (Base Transport Header): QP、操作码、PSN、P_Key
- **ETH** (Extended Transport Header): RDMA/Send/Datagram 操作
- **ICRC/VCRC**: Invariant/Cyclic 校验

---

## 2️⃣ RoCE（RDMA over Converged Ethernet）

### 设计理念
> 复用现有以太网基础设施，仅需特殊网卡，无需专用交换机。

### 协议对比

| 版本 | 承载协议 | 网络层 | 识别 | 典型延迟 |
|:----|:---------|:------|:-----|:--------|
| **RoCE v1** | 以太网直接承载 | L2 二层 | Ethertype 0x8915 | 同 IB |
| **RoCE v2** | **UDP/IP** 承载 | L3 三层（可路由） | UDP端口4791 | 同 IB |

### 协议栈层次

```
   InfiniBand                     RoCE v2
┌─────────────┐           ┌─────────────┐
│  Verbs API  │           │  Verbs API  │
├─────────────┤           ├─────────────┤
│  Transport  │   ← 相同   │  Transport  │
├─────────────┤           ├─────────────┤
│  Network    │           │   UDP/IP    │ ← 替代IB网络层
├─────────────┤           ├─────────────┤
│  Link       │   差异→   │   Ethernet  │ ← 替代IB链路层
├─────────────┤           ├─────────────┤
│  Physical   │   差异→   │  Ethernet   │
└─────────────┘           └─────────────┘
```

### 关键要求
- **无损以太网** — IB 丢包处理机制中，任一报文丢失都导致大量重传
- **ECMP 负载分担** — RoCE v2 支持基于源端口号 hash

---

## 3️⃣ iWARP（Internet Wide Area RDMA Protocol）

### 设计理念
> 基于标准 TCP/IP，无需无损以太网，可在广域网运行。

### 核心优化
- TCP/IP 处理从 CPU 卸载到 iWARP 网卡
- Zero Copy + Kernel Bypass 与其他 RDMA 一致
- **TCP 自身提供流控与拥塞管理**，无需交换机无损支持
- 扩展性好，可在广域网使用

### 性能代价
- TCP 协议栈开销导致延迟高于 RoCE/IB
- 适合存储场景（延迟容忍度高），不适合 GPU 同步（延迟敏感）

---

## 🔗 关联知识

| 模块 | 文件 | 关系 |
|:-----|:-----|:-----|
| 分布式 OS | [GPU Direct 技术体系](gpu-direct-technology.md) | GPU Direct RDMA 是 RDMA 在 GPU 场景的应用 |
| 分布式 OS | [NCCL 集合通信](multi-gpu-collective-communications.md) | NCCL 基于 RDMA Verbs 构建 |
| 分布式 OS | [XCCL 通信库全景](xccl-collective-communication-libraries.md) | 各厂商通信库底层均依赖 RDMA |
| 分布式 OS | [网络拓扑感知调度](network-topology-aware-scheduling.md) | 调度需理解 IB/RoCE/iWARP 差异做最优放置 |
| 分布式 OS | [2026-06-04 跟踪](../../01_survey/bmc-system/2026-06-04.md) | MRC+SRv6(OpenAI/MS生产RDMA)·VCCL开源·NCCL EP |
| 运维系统 | [NFD & GFD](nfd-gfd.md) | RDMA 硬件发现标签（`rdma.capable`/`rdma.available`）|
| 运维系统 | [GPU DCGM Exporter](ops-system/gpu-dcgm-exporter.md) | NVLink 链路监控（CRC/Replay 错误）|
