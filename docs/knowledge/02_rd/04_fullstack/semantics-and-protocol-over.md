# 🧠 互联语义体系（内存·消息·I/O）与协议封装（Over）技术全景

> **版本**: v1.0 | **更新**: 2026-06-25
> **范围**: 三大互联语义（Memory/Message/IO）的原理性差异；各类协议 Over/封装/隧道技术在另一链路上的承载能力、市场现状、OS 驱动要求与影响
> **关联文档**: [NVLink/NVSwitch芯片架构](nvlink-nvswitch-chip-architecture.md) | [互联层次深度分析](../03_hardware/01_hw_core/interconnect-hierarchy-deep-dive.md) | [架构演进摆动分析](../03_hardware/01_hw_core/architecture-evolution-swing-analysis.md) | [RDMA技术架构](../05_software/rdma-architecture.md) | [超节点存储网络分析](../03_hardware/01_hw_core/g35-kv-cache-storage-network-analysis.md)

---

## 📑 目录

- [第1章 三大互联语义：原理性差异](#第1章-三大互联语义原理性差异)
- [第2章 内存语义深度解析](#第2章-内存语义深度解析)
- [第3章 消息语义深度解析](#第3章-消息语义深度解析)
- [第4章 I/O 语义深度解析](#第4章-io-语义深度解析)
- [第5章 三种语义的全维度对比与权衡](#第5章-三种语义的全维度对比与权衡)
- [第6章 协议 Over（封装/隧道）的总论框架](#第6章-协议-over封装隧道的总论框架)
- [第7章 各协议 Over 技术的逐个分析](#第7章-各协议-over-技术的逐个分析)
- [第8章 OS 驱动的支持与影响](#第8章-os-驱动的支持与影响)
- [第9章 市场格局与产业生态](#第9章-市场格局与产业生态)
- [第10章 总结与展望](#第10章-总结与展望)
- [附录](#附录)

---

# 第1章 三大互联语义：原理性差异

## 1.1 为什么有不同的"语义"

互联语义定义了**应用程序/硬件如何表达和完成一次数据搬运**。不同的场景对延迟、带宽、编程模型、距离有不同的需求，因此演化出了三种本质不同的语义模型：

```text
                  ┌──────────────────────┐
                  │   一个"数据搬运"      │
                  │   要解决的核心问题:   │
                  │   谁发起? 谁执行?      │
                  │   数据从哪到哪?       │
                  │   谁保证完成?         │
                  └──────┬───────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
  ┌────────────┐ ┌────────────┐ ┌────────────┐
  │ 内存语义   │ │ 消息语义   │ │ I/O 语义  │
  │ Memory     │ │ Message    │ │ I/O        │
  │ Semantics  │ │ Semantics  │ │ Semantics  │
  ├────────────┤ ├────────────┤ ├────────────┤
  │ Load/Store │ │ Send/Recv  │ │ DMA/PIO    │
  │ 指令级     │ │ 消息级     │ │ 通道级     │
  │ 零软件栈   │ │ 中等软件栈 │ │ 驱动介入   │
  │ ~100ns     │ │ ~1-10μs   │ │ ~0.5-5μs  │
  │ <1m距离   │ │ 1-100m    │ │ <10m       │
  └────────────┘ └────────────┘ └────────────┘
```

## 1.2 从 CPU 指令系统的根源理解

三种语义的根在于 **CPU 如何看待"远端数据"**：

```text
内存语义 (Memory Semantics):
  CPU 视角: 远端内存是本地地址空间的自然延伸
  指令形式: LD/ST (如: R1 = MEM[0xFACE_0000])
  硬件执行: 内存控制器→互联控制器→远端
  编程体验: memcpy() 在本地和远端完全一样
  代表: NVLink, CXL.mem, RDMA Read/Write

消息语义 (Message Semantics):
  CPU 视角: 远端是"另一个节点", 需通过消息沟通
  指令形式: SEND/RECV (如: send(to=GPU1, buf, len))
  硬件执行: 消息队列→互联控制器→目的地→应答
  编程体验: 显式配对 send/recv
  代表: MPI, TCP Socket, IB Send/Recv, ETH

I/O 语义 (I/O Semantics):
  CPU 视角: 远端是"外设", 通过控制寄存器管理
  指令形式: PIO/MMIO + DMA (如: *ctrl_reg = DMA_START)
  硬件执行: CPU 启动 DMA→DMA 引擎搬运→中断完成
  编程体验: 注册缓冲区→启动 DMA→等待完成
  代表: PCIe, NVMe, SATA, USB
```

## 1.3 三层递进的关系

```text
            编程复杂度 ←──────────────→
               低                高
             ┌─────────────────────────┐
  内存语义  │  LD/ST 指令             │  编程最简单
             │  "就像在本地"           │
             ├─────────────────────────┤
  I/O 语义  │  MMIO + DMA            │  中等
             │  "启动搬运后等待"        │
             ├─────────────────────────┤
  消息语义  │  Send/Recv 配对         │  编程最复杂
             │  "需要显式协调"          │
             └─────────────────────────┘
               高                低
             硬件复杂度 ←──────────────→
```

---

# 第2章 内存语义深度解析

## 2.1 定义与本质

**内存语义** (Memory Semantics) 是指通信双方都"假装"对方的内存是自己的物理地址空间的一部分。核心特征是 **CPU 发起的 Load/Store 指令可以直接命中远端内存**，无需驱动介入。

```text
内存语义的核心模型:

CPU ─── LD/ST ───→ 本地内存控制器 ───→ 互联控制器 ───→ 远端内存

            ┌─────────────┐
CPU 看到:   │ 地址空间     │
            │ 0x0000_0000 │  ← 本地 DRAM
            │ 0xF000_0000 │  ← 远端 GPU HBM (通过 NVLink)
            │ 0xE000_0000 │  ← 远端 CXL 内存池
            └─────────────┘
            ↑ 统一的物理地址空间
            ↑ Load/Store 指令对本地和远端完全一样
```

## 2.2 内存语义的三种子类型

### 2.2.1 裸内存语义 (Raw Memory Semantics)

最简单的内存语义：直接读写远端内存，**不维护缓存一致性**。

```text
代表: RDMA Read/Write

操作:
  READ:  本地 → {请求} → 远端 → 读取内存 → 返回数据
  WRITE: 本地 → {数据+地址} → 远端 → 写入内存 → 返回ACK

关键特性:
  - 单侧操作 (One-sided): 远端 CPU 零参与
  - 地址: 远端虚拟地址 (需要提前注册/映射)
  - 一致性: 无 (需要应用程序自己处理)
  
延迟: ~1-3μs (InfiniBand)
       ~3-15μs (RoCEv2)
```

### 2.2.2 一致性内存语义 (Coherent Memory Semantics)

在内存语义基础上增加缓存一致性协议（如 MESI 的变体），确保所有参与者的 cache 视图一致。

```text
代表: CXL.cache / CXL.mem, NVLink 域内

操作 (以 CXL.mem 为例):
  S2M Read: 从设备内存读 (类似本地内存读)
  M2S Write: 主机写设备内存 (类似本地内存写)
  S2M MemInv: 设备通知主机某缓存行失效 (一致性维护)

一致性域 (Coherency Domain):
  片内: CPU core ↔ CPU core (MESI)
  板级: CPU ↔ CXL 设备 (CXL.cache/mem)
  域内: GPU ↔ GPU (NVLink)
  域间: ❌ 无法跨节点 (物理极限)

延迟:
  CXL.mem Type 3: ~110-210ns (纯随机访问)
  NVLink 5 域内: ~100-200ns (GPU↔GPU)
```

### 2.2.3 原子操作语义 (Atomic Memory Semantics)

在内存语义上增加原子操作支持（Compare-And-Swap, Fetch-And-Add 等），用于分布式锁/计数器：

```text
CAS: Compare-And-Swap over NVLink
  → GPU A 原子地: if (远端地址 == old_val) 写入 new_val

FAA: Fetch-And-Add over RDMA
  → 本地节点原子地对远端计数器加 1

延迟:
  NVLink CAS: ~300-500ns (1 跳)
  RDMA CAS: ~3-10μs (网络)
```

## 2.3 内存语义的软硬件需求

### 2.3.1 硬件需求

| 组件 | 需求 | 举例 |
|:-----|:------|:------|
| **CPU** | 支持一致性域扩展 | Intel DSA, AMD IOMMU, ARM SMMU |
| **内存控制器** | 识别非本地地址并路由 | CXL 内存控制器, NVLink 地址映射表 |
| **互联接口** | 低延迟序列化/解序列化 | NVLink PHY, CXL PHY |
| **交换芯片** | 保持地址信息完整的转发 | NVSwitch (flit 级), CXL Switch |
| **远端内存** | 支持外部访问的控制器 | HBM 控制器, CXL Type 3 控制器 |

### 2.3.2 软件需求

```text
内存语义的理想: "零软件开销"
实际中的软件需求:

最小需求:
  - 地址映射表配置 (启动时一次性)
  - 无运行时系统调用
  - 无中断处理 (除非错误)

额外可选 (取决于粒度):
  - TLB 刷新 (跨节点地址映射变更时)
  - 页错误处理 (远端内存交换时)
  - 一致性协议代理 (CXL.cache 场景)

关键: 运行时路径上无软件介入 → 这是延迟低的根本原因
```

## 2.4 内存语义的优势与局限

| 优势 | 局限 |
|:-----|:------|
| 延迟极低 (~100ns-1μs) | 距离受限 (<1m 裸语义, <100m 光扩展) |
| CPU 零参与 (硬件直通) | 一致性域规模有限 (~72 GPU / ~256 CXL 设备) |
| 编程简单 (Load/Store) | 需要特殊硬件支持 (非通用) |
| 无需驱动运行时介入 | 错误处理复杂 (远端内存故障难以定位) |
| 带宽高 (TB/s 级) | 成本高 (专用芯片/线缆) |

---

# 第3章 消息语义深度解析

## 3.1 定义与本质

**消息语义** (Message Semantics) 是指通信双方**显式地发送和接收消息**。发送方主动推送数据，接收方主动拉取数据——这是**最早的互联语义**（源自电报/电话），也是**距离最不受限的语义**。

```text
消息语义的核心模型:

发送方:       接收方:
┌──────┐      ┌──────┐
│ Send  │──────│ Recv │
│ (buf, │ 消息 │ (buf)│
│  len) │──────│      │
└──────┘      └──────┘
      ↑     ↑
    发送    接收
    队列    队列
    (显式)  (显式)

关键特征:
  1. 需要双方显式配对 (Send 必须有对应的 Recv)
  2. 数据由发送方推送到接收方 (Push 模型)
  3. 接收方必须提前分配/注册接收缓冲区
  4. 完成时通常通过中断/轮询通知
```

## 3.2 消息语义的子类型

### 3.2.1 不可靠消息 (Unreliable Datagram)

```text
代表: UDP, InfiniBand UD

特征:
  - 尽力交付 (Best-effort)
  - 可能丢包、乱序、重复
  - 无重试、无确认
  - 低开销 (最小协议头)

使用场景: 实时音视频, DNS, 多播
延迟: ~0.5-1μs (IB UD), ~10μs+ (UDP)
```

### 3.2.2 可靠消息 (Reliable Message)

```text
代表: TCP, IB RC, RoCEv2

特征:
  - 有确认 (ACK/NAK)
  - 自动重传 (丢包恢复)
  - 保序
  - 流量控制 (滑动窗口/信用)

使用场景: 文件传输, 数据库, RPC
延迟: ~1-2μs (IB RC), ~10-50μs (TCP)
```

### 3.2.3 流式消息 (Streaming)

```text
代表: MPI Send/Recv, gRPC Stream

特征:
  - 消息之间的边界保留 (MPI) 或消失 (TCP stream)
  - 可管道化 (多个消息并发)
  - 通常有拥塞控制

使用场景: HPC (MPI), 微服务 (gRPC)
```

## 3.3 消息语义的软件栈开销

```text
消息语义的完整软件栈 (以 TCP 为例):

应用层 (Application)
    ↓ Socket API: send()/recv()
传输层 (TCP)
    │ 段分割 + 序列号 + ACK + 重传 + 拥塞控制
    ↓ ~10-50μs
网络层 (IP)
    │ 路由 + IP 头封装
    ↓ ~1-5μs
链路层 (Ethernet)
    │ MAC + CRC + 仲裁
    ↓ ~0.5-1μs
物理层 (PHY)
    ↓ 串行化

应用层 (Application)
    ↑ Socket API
传输层 (TCP)
    ↑ 段重组 + ACK + 校验
网络层 (IP)
    ↑ 路由 + 解封装
链路层 (Ethernet)
    ↑ 解帧 + CRC 校验
物理层 (PHY)
    ↑ 解串

每层都涉及:
  - 内存拷贝 (从用户态到内核态, 从内核态到 NIC)
  - 上下文切换 (系统调用)
  - 中断处理 (数据到达)
  ─────────────────────────────
  TCP 总延迟: ~10-50μs (局域网)
               ~100ms+ (广域网)
```

## 3.4 消息语义的优势与局限

| 优势 | 局限 |
|:-----|:------|
| 距离几乎无限 (全球范围) | 延迟高 (~μs-ms 级) |
| 标准化生态 (TCP/IP) | CPU 参与度高 |
| 通用硬件 (以太网) | 编程复杂 (需 send/recv 配对) |
| 可大规模扩展 (百万节点) | 带宽效率低 (协议头+ACK 开销) |
| 弹性 (自动路由/重传) | 不可预测的延迟 (拥塞) |

---

# 第4章 I/O 语义深度解析

## 4.1 定义与本质

**I/O 语义** (I/O Semantics) 是一种"中间态"语义——CPU 不直接访问远端内存，而是通过**控制寄存器**启动一轮 DMA 搬运。它比内存语义多一次 CPU 指令（写控制寄存器），但比消息语义少一层协议栈。

```text
I/O 语义的核心模型:

CPU ─── MMIO 写 ───→ DMA 引擎 ───→ 远端设备

                   ┌──────────────┐
  CPU 职责 (轻):   │ *ctrl_reg     │ = DMA_START
                   │ *ctrl_reg     │ = src_addr
                   │ *ctrl_reg     │ = dst_addr
                   │ *ctrl_reg     │ = length
                   └──────────────┘
                        │
                        ▼
                   ┌──────────────┐
  DMA 引擎职责:     │ 异步搬运     │
                   │ 自动:        │
                   │ src → buffer │
                   │ buffer → dst │
                   │ 中断 CPU     │
                   └──────────────┘
                        │
                        ▼
                   ┌──────────────┐
  CPU 职责:        │ 响应中断     │
                   │ 检查完成状态  │
                   └──────────────┘
```

## 4.2 I/O 语义的子类型

### 4.2.1 PIO (Programmed I/O)

```text
CPU 逐字节/逐字搬运数据到设备寄存器。
最简单但最慢。
使用: 早期 PC, 少量控制寄存器访问
延迟: ~100ns-1μs (取决于设备响应)
```

### 4.2.2 DMA (Direct Memory Access)

```text
代表: PCIe DMA

流程:
  ① CPU 配置 DMA 引擎 (源地址、目标地址、长度)
  ② CPU 写 START 寄存器
  ③ DMA 引擎独立搬运 (CPU 可做其他事)
  ④ DMA 完成 → 中断 CPU

延迟: ~0.5-3μs (PCIe Gen5 DMA)
       ~0.3-1μs (NVMe 提交队列)
```

### 4.2.3 RDMA (Remote DMA)

I/O 语义的远程版本——本质还是 DMA，但目标在远端：

```text
代表: InfiniBand RDMA, RoCEv2 RDMA

流程:
  ① 本地注册内存区域 (MR: Memory Region)
  ② 本地配置 RDMA 描述符 (远端地址 + 本地地址 + 密钥)
  ③ 硬件自动执行: 本地 DMA → NIC → 网络 → 远端 NIC → 远端 DMA
  ④ 完成 → 轮询 CQ (Completion Queue) 或中断

关键差异 vs 本地 DMA:
  - 远端地址需要密钥保护 (防止非法访问)
  - 需要网络协议栈 (但硬件卸载)
  - 完成检测可以是轮询 (更低延迟)

延迟: ~1-2μs (IB RDMA Read, 小消息)
       ~3-5μs (RoCEv2 RDMA Read)
```

## 4.3 I/O 语义 vs 内存语义的本质区别

```text
            I/O 语义 (DMA)                内存语义 (Load/Store)
           ───────────────              ─────────────────────
CPU 使用   ① 写控制寄存器                 ① LD/ST 指令
           ② 等待中断                   ② 硬件自动完成
                                              
粒度       块级 (KB-MB)                  字节级 (1-64B 最小)
              
触发模式   CPU 显式启动                  隐式触发 (cache miss)
              
完成通知   中断或轮询                    指令完成 (LD 返回即完成)
              
缓存       绕过 CPU cache                经过 CPU cache (一致性)
              
编程       复杂 (DMA 描述符)             简单 (memcpy)
              
带宽       高 (大块传输)                 低 (小粒度传输)
                                       
延迟       0.5-3μs                       100-300ns

本质: I/O 语义 = CPU 管理数据搬运          内存语义 = 硬件管理数据搬运
                  启动者 ≠ 执行者                   启动者 = 执行者
```

## 4.4 I/O 语义的优势与局限

| 优势 | 局限 |
|:-----|:------|
| CPU 可做其他事 (DMA 异步) | 有启动开销 (控制寄存器写) |
| 带宽高 (大块传输最优) | 小消息效率低 (启动开销占比大) |
| 硬件卸载 (不占用 CPU 总线) | 编程复杂 (DMA 描述符管理) |
| 适合流式/块设备 | 不支持细粒度随机访问 |
| PCIe 生态标准 | 延迟高于内存语义 |

---

# 第5章 三种语义的全维度对比与权衡

## 5.1 全维度对比矩阵

| 维度 | 内存语义 (Memory) | I/O 语义 (DMA/PIO) | 消息语义 (Message) |
|:-----|:----------------:|:-----------------:|:-----------------:|
| **基本操作** | Load/Store | MMIO + DMA | Send/Recv |
| **CPU 每操作开销** | 1 条指令 | ~500-2000 条指令 | ~1000-10000+ 条指令 |
| **延迟 (本地)** | ~50-100ns (CXL) | ~0.5-3μs (PCIe DMA) | N/A (非对称) |
| **延迟 (域内 ~1m)** | ~100-500ns (NVLink) | ~1-5μs (PCIe) | ~3-50μs (TCP) |
| **延迟 (局域网)** | N/A | ~3-15μs (RDMA) | ~10-100μs |
| **延迟 (广域网)** | N/A | ~1-5ms (iWARP) | ~10-500ms |
| **带宽密度** | TB/s 级 | GB/s 级 | Gb/s 级 |
| **距离极限** | ~100m (光扩展) | ~15m (PCIe cable) | 全球 |
| **规模极限** | ~256 节点 | ~1024 节点 | 无限 |
| **编程模型** | memcpy (最简单) | DMA 描述符 (复杂) | Socket/MPI (最复杂) |
| **OS 参与** | 无 (配置后) | 初始化时 | 每次操作 |
| **硬件卸载** | 完全 | 部分 | TCP 卸载 / RDMA |
| **缓存一致性** | ✅ (可选) | ❌ | ❌ |
| **原子操作** | ✅ 原生 | ❌ (需 PCIe CAS) | ❌ |
| **成本** | 最高 | 中等 | 最低 |
| **生态** | 封闭/半开放 | 开放 (PCI-SIG) | 最开放 (IETF) |

## 5.2 编程模型复杂度对比

```text
内存语义 (理想情况):
  // 只需 memcpy, 完全一样
  memcpy(far_ptr, local_buf, size);  // 远端和本地一样

I/O 语义:
  // 需要 DMA 描述符 + 等待完成
  dma_desc_t desc = {
      .src = local_buf, .dst = pcie_bar + offset,
      .len = size, .dir = DMA_TO_DEVICE
  };
  submit_dma(&desc);                  // 提交 DMA
  while (!desc.completed) { }         // 轮询等待

消息语义 (TCP):
  // Socket 编程
  int sock = socket(AF_INET, SOCK_STREAM, 0);
  connect(sock, &addr, sizeof(addr));
  send(sock, buf, len, 0);           // 发送
  recv(sock, ack_buf, 4, 0);         // 等待确认

消息语义 (MPI):
  // 显式配对
  MPI_Send(buf, len, MPI_BYTE, dest, tag, comm);
  MPI_Recv(ack_buf, 4, MPI_BYTE, src, tag, comm, &status);
```

## 5.3 延迟与带宽的权衡空间

```text
三种语义的延迟-带宽地图:

延迟 (log)
  ^
  │ 内存语义域    I/O 语义域      消息语义域
  │ (专用)        (标准)          (通用)
  │
 1ns┤ HBM
  │  │
 10ns┤ CXL
  │   │ NVLink
100ns┤│││    PCIe DMA
  │   ││││      │
 1μs ┤│││││││││    │ TCP (本地)
  │   │││││││││││││││││││││││││││││││││││││
10μs ┤│││││││││││││││││││││││    │ RDMA
  │   │││││││││││││││││││││││││││││││   │ TCP WAN
100μs┤│││││││││││││││││││││││││││││││││││││││││││││││││
  │
  └─────────────────────────────────────────────→ 距离
     1cm  10cm  1m   10m   100m  1km   10km  100km

注释: 纵轴每格 ~10× 延迟跨度
      横轴每格 ~10× 距离跨度
      圆圈区域 = 主流应用范围
```

---

# 第6章 协议 Over（封装/隧道）的总论框架

## 6.1 什么是"协议 Over"

**协议 Over**（或称封装、隧道、承载）是指将一种互联协议的**语义和数据**打包到另一种协议的消息体中传输，在目的端解包还原。其本质是**用低成本/长距离的链路承载高成本/短距离的协议**。

```text
封装 (Encapsulation) 模型:

原始协议 (被承载):    NVLink flit / PCIe TLP / CXL 消息
                          │
                          ▼ 封装
承载协议 (隧道):       Ethernet frame / InfiniBand 包
                          │
                          ▼ 传输
物理链路:              光纤 / 铜缆 / 背板
                          │
                          ▼ 解封装
恢复:                   NVLink flit / PCIe TLP / CXL 消息
```

## 6.2 为什么需要 Over

```text
核心动机: 打破原始协议的物理距离/拓扑限制

具体原因:
  1. 距离扩展: NVLink 只有 ~0.5m, 通过 over Ethernet 可到 100m
  2. 利用已有基础设施: 数据中心已有以太网, 不需要额外布线
  3. 生态兼容: 让新协议能和存量设备通信
  4. 成本降低: 以太网交换芯片比 NVSwitch 便宜 10×+
  5. 开放标准: 避免单厂商锁定

代价:
  - 延迟增加 (封装/解封装 + 额外协议头)
  - 带宽效率降低 (协议头开销)
  - 可能丢失原始协议的特性 (如原子操作、一致性)
  - 硬件复杂度增加 (需要隧道引擎)
```

## 6.3 Over 的分类体系

所有 Over 技术可按**原始协议与承载协议的关系**分类：

```text
                             所有 Protocol Over
                                    │
               ┌────────────────────┼────────────────────┐
               ▼                    ▼                    ▼
      同类语义 Over          跨语义 Over            跨域 Over
      (同层次)               (不同层次)              (不同物理域)
               │                    │                    │
               ▼                    ▼                    ▼
  例: NVLink over Eth  ┌────────────┴────────────┐  例: PCIe over Cable
  例: CXL over Eth    ▼                         ▼
  例: TCP over IB  低语义→高语义             高语义→低语义
                    (强→弱)                   (弱→强)
                    ┌───────────┐           ┌───────────┐
                    │ 例:       │           │ 例:       │
                    │CXL over Eth │          │ IP over IB│
                    │NVMe-oF over TCP│      │ Eth over ATM│
                    └───────────┘           └───────────┘
```

## 6.4 Over 技术的性能损耗模型

```text
T_over = T_原始 + T_封装 + T_承载 + T_解封装 + ΔT_特性丢失

其中:
  T_原始: 原始协议本地的传输时间
  T_封装: 封装引擎的处理时间 (硬件 ~50-200ns, 软件 ~1-10μs)
  T_承载: 承载协议的传输时间 (包括协议栈)
  T_解封装: 解封装引擎的处理时间
  ΔT_特性丢失: 因原始语义简化导致的额外补偿

典型损耗:
  NVLink over Eth (ESUN 方案):     +2-5μs (vs 原生 0.5-1μs)
  CXL over Eth:                    +5-15μs (vs 原生 0.2-0.5μs)
  NVMe-oF over TCP:               +10-100μs (vs 原生 PCIe NVMe ~5-10μs)
  FC over Ethernet (FCoE):        +2-5μs (vs 原生 FC ~1-2μs)
  IP over IB (IPoIB):             +0.5-2μs (vs 原生 IB ~1-2μs)
  Ethernet over ATM:              +0.1-1ms (vs 原生 Ethernet ~10μs)
```

---

# 第7章 各协议 Over 技术的逐个分析

## 7.1 NVLink over Ethernet (ESUN / UEC)

### 7.1.1 技术原理

```text
NVLink over Ethernet 的封装层次:

原始 NVLink flit (256B):
┌────────────────────────────────────────────┐
│ NVLink Header (32B) │ Data (up to 192B)    │
│ Src/Dest/VC/Seq/CRC                        │
└────────────────────────────────────────────┘
                    │
                    ▼ 封装
Ethernet 帧:
┌─────────────────────────────────────────────────────────┐
│ Eth MAC | IP | UDP | NVLink over Eth Header | NVLink   │
│ (14B)   (20B) (8B) | Type/Seq/Len/VN    | flit (256B) │
│                    | (8B)                |              │
├─────────────────────────────────────────────────────────┤
│ FCS (4B)                                                 │
└─────────────────────────────────────────────────────────┘
总开销: 54B 封装头 + 4B FCS = 58B 开销 / 256B 数据 = ~23%
```

### 7.1.2 组织与进展

| 组织 | 倡议 | 目标 | 状态 (2026) |
|:-----|:------|:------|:-----------|
| **UEC** (Ultra Ethernet Consortium) | 通用 AI 网络 | 替换 RoCEv2 + 支持 NVLink 类语义 | 规范制定中, 预计 2027 产品化 |
| **ESUN** (Ethernet for Scale-Up Networking) | Meta/AMD/BCM/MS | 用开放以太网替代私有 Scale-Up 协议 | OCP 2025 提出, 仍在早期 |
| **UALink** | AMD 主导 GPU 域开放互联 | 直接对标 NVLink, 不必 over Eth | 已发布 4 份规范, 100+ 成员 |

### 7.1.3 关键挑战

```text
1. 延迟: NVLink 原生 ~100-500ns, over Eth 至少 +2-5μs
   → 域内通信 2μs 的差距在同步训练中直接体现为 Step Time 增加
   → 对 10T 模型, 每微秒训练延迟 ≈ $1K+ 附加成本

2. 原子操作: NVLink 的 CAS/FAA 是硬件原生, over Eth 需软件模拟
   → 分布式锁性能下降 10-100×

3. 一致性: NVLink 域内的一致性无法 over Eth 维持
   → 应用程序必须用更保守的同步模型

4. PFC/Priority Flow Control: 无损以太网需要 PFC
   → PFC 死锁 + 大缓冲区 + 尾延迟问题 (RoCE 已有的问题)
```

### 7.1.4 市场前景

```text
乐观情景 (2030): 开放以太网 AI 网络占 40% 份额, NVLink 类专有仍占 60%
  驱动: 超大规模云厂商排斥锁定, 追求多供应商

悲观情景: NVLink 带宽优势持续扩大 (4.3 TB/s @2026), 差距不可弥合

最可能: 两级共存
  - 域内 (8-72 GPU): NVLink 保持 (延迟不可替代)
  - 域间跨柜: ESUN/UEC 逐步替代 (成本 + 开放优势)
```

## 7.2 CXL over Ethernet

### 7.2.1 技术原理

```text
CXL over Ethernet:

原始 CXL 3.0 flit (528B, CXL 3.0 定义):

需求:
  - CXL.mem 的延迟敏感度: ~110-210ns 原生
  - CXL.io 的延迟容忍度高: ~1μs+
  
封装策略 (分层):
  - CXL.io over Eth: 直接封装 (类 PCIe over Eth)
  - CXL.mem over Eth: ❌ 延迟不可接受 (原生 200ns → 10+μs)
  - CXL.cache over Eth: ❌ 一致性协议无法 over 不可靠网络

因此, 实际上只有 CXL.io 可以 over Eth
CXL.mem 和 CXL.cache 需要 CXL Switch/Fabric (专用硬件)
```

### 7.2.2 CCCL (CXL-Centric Computing) 研究

```text
2025-2026 学术界研究结果:

CCCL vs RDMA AlltoAll 对比:
  性能: CCCL 1.11× RDMA
  成本: CCCL 2.75× RDMA (CXL 专用硬件成本)
  
结论: 在机架级内存池化场景中, CXL Fabric (非 over Eth)
  比 RDMA 略有性能优势, 但成本远高于 RDMA over Eth

市场判断: CXL Fabric 适用于机架内性能敏感场景
  CXL over Eth 仅用于管理面/控制面
```

### 7.2.3 市场现状

```text
CXL over Ethernet: ❌ 实际产品很少
  仅 Intel 的某些实验性方案

CXL over CXL Switch/Fabric: ✅ 主流
  Astera Labs, Microchip, Broadcom 的 CXL Switch
  用于: 机架内内存池化, 不跨机架
  CXL 3.0 多级 Fabric: 最多可扩展 4,096 节点
  
CXL over other: 
  CXL over PCIe (默认): 作为 PCIe 的替代/增强
  CXL over 光互联: 实验阶段 (IOWN 计划)
```

## 7.3 NVMe over Fabrics (NVMe-oF)

### 7.3.1 技术原理

最成功的 Over 技术之一。将 NVMe 的 I/O 语义 (提交队列/完成队列) 封装到不同传输层：

```text
NVMe-oF 的多个传输通道:

                    NVMe 协议 (NVM 命令集)
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
      NVMe-oF          NVMe-oF          NVMe-oF
      over RDMA        over FC          over TCP
      (RDMA)          (FC-NVMe)         (TCP)
            │              │              │
            ▼              ▼              ▼
      InfiniBand/      Fibre           TCP/IP
      RoCEv2           Channel         网络
```

### 7.3.2 各 Over 方案的对比

| 方案 | 原生协议 | 承载协议 | 延迟 | 市场 (2026) |
|:-----|:--------|:---------|:----:|:-----------:|
| NVMe-oF over RDMA | PCIe NVMe | IB/RoCE RDMA | ~5-15μs | ~60% (数据中心/超算) |
| NVMe-oF over FC | PCIe NVMe | FC-4 | ~5-10μs | ~25% (企业存储) |
| NVMe-oF over TCP | PCIe NVMe | TCP/IP | ~50-500μs | ~15% (远距离/低成本) |

### 7.3.3 OS 驱动支持

```text
NVMe-oF 驱动栈 (以 Linux 为例):

应用层: 标准 VFS 接口 (open/read/write/fsync)
   │
VFS + 文件系统 (ext4/xfs/btrfs...)
   │
nvme_core (通用 NVMe 层)
   │
   ┌───────┴───────┐
   │               │
nvme_rdma       nvme_tcp
(RDMA 传输)     (TCP 传输)
   │               │
   ↓               ↓
内核 RDMA 栈    内核 TCP/IP
(ib_core/rdma_cm)   (tcp/ip)
   │               │
   ↓               ↓
NIC 驱动         NIC 驱动

关键:
  - nvme_rdma 和 nvme_tcp 是**内核模块**, 需显式加载
  - RDMA 需要 ib_core + rdma_cm 内核模块
  - 用户态不需要特殊库 (标准文件系统 API)
  - 但性能优化需要控制: nr_requests, queue_depth, timeout 等
```

## 7.4 InfiniBand over 各种底层

### 7.4.1 IP over InfiniBand (IPoIB)

```text
IP over IB:

┌──────────┐
│  TCP/IP  │
└────┬─────┘
     │
┌────▼─────┐
│  IPoIB   │ ← Linux 内核模块
│ (IPoIB)  │
└────┬─────┘
     │
┌────▼─────┐
│  IB 协议  │
│ (LID/GID)│
└────┬─────┘
     │
┌────▼─────┐
│  IB PHY  │
└──────────┘

延迟: ~3-5μs (vs 原生 TCP 10-50μs, 但远不如 IB RDMA 1-2μs)
使用: 管理面, 非性能关键
市场: 几乎所有 IB 网络都启用 IPoIB, 但实际流量占比 < 5%
```

### 7.4.2 Ethernet over InfiniBand (EoIB)

```text
将以太网帧封装在 IB 消息中传输。

┌──────────┐
│ Eth 帧    │
└────┬─────┘
     │
┌────▼─────┐
│  EoIB    │ ← Linux 内核模块
└────┬─────┘
     │
┌────▼─────┐
│  IB 协议  │
└──────────┘

使用场景: 兼容仅支持以太网的设备连接到 IB 网络
市场: 极小, 主要是过渡方案
```

### 7.4.3 SRP (SCSI RDMA Protocol)

SCSI over IB：在 IB 网络上传输 SCSI 命令和数据

```text
应用: 块存储 (SAN)
延迟: ~5-10μs (vs 原生 FC SAN ~10-20μs)
使用: 已被 NVMe-oF 替代, 市场份额快速萎缩
```

## 7.5 PCIe over 各种底层

### 7.5.1 PCIe over Cable (铜缆/光缆)

```text
PCIe over Cable:

不是"Over"另一个协议, 而是将 PCIe PHY 延长到线缆上。

| 标准 | 距离 | 带宽 (x16) | 市场 |
|:-----|:----:|:----------:|:----:|
| PCIe Gen5 over Copper | ~3m | 128 GB/s | 机柜内连接 |
| PCIe Gen5 over Fiber | ~15m | 128 GB/s | 机柜间连接 |
| PCIe Gen6 over Copper | ~2m | 256 GB/s | 正在推出 |
| PCIe Gen6 over Fiber | ~10m | 256 GB/s | 正在推出 |
| MCIO (内部连接器) | ~0.5m | 224 GB/s (4 pairs) | 底板连接 |

OS 需求: 不需要额外驱动 (对 OS 就像板载 PCIe 一样)
```

### 7.5.2 PCIe over Ethernet (实验性)

```text
将 PCIe TLP 封装到 Ethernet 包中。

方案: PCIe TLP (16B-4KB) → 封装到 Ethernet Jumbo Frame

挑战:
  - PCIe 延迟敏感 (~1μs) → 以太网延迟不可匹配
  - PCIe 要求可靠有序 → Ethernet 需要额外重传+保序
  - PCIe 信用流控 → 无法 over 非确定性网络

市场: ❌ 几乎不存在, CXL/CCIX 已经解决了"PCIe over 网络"的需求
```

### 7.5.3 CXL over PCIe (默认方案)

```text
CXL 本身就是 "over PCIe":
  CXL.io = PCIe (兼容)
  CXL.mem = 在 PCIe PHY 上传输内存语义
  CXL.cache = 在 PCIe PHY 上传输缓存一致性协议

这是最成功的 "over" 案例之一:
  CXL 利用 PCIe 物理层 (已经标准化 + 低成本)
  在 PCIe 上增加新的协议层
  实现了 cache-coherent 内存语义
```

## 7.6 Ethernet over ATM (历史)

### 7.6.1 背景

```text
1990s 的尝试:

ATM (Asynchronous Transfer Mode):
  - 固定长度信元 (53B: 5B 头 + 48B 数据)
  - 面向连接 (VC: Virtual Circuit)
  - 承诺 QoS (CBR/VBR/ABR/UBR)
  - 当时被认为是"下一代网络基础设施"

以太网:
  - 变长帧 (64B-1518B)
  - 无连接
  - 尽力交付
  - 当时被认为是"桌面网络"
```

### 7.6.2 Ethernet over ATM (LANE)

```text
封装:
  Ethernet 帧 (64-1518B) → 分割 → ATM 信元 (48B) × N

问题:
  - 每条以太网帧需要 N 个 ATM 信元
  - 信元开销: 5B/53B = 9.4% (固定)
  - 分割+重组延迟: ~100μs-1ms
  - 复杂 (IP over ATM 因分割而广受诟病: "ATM cell tax")

市场结局: ❌ 彻底失败
  以太网速率提升 (100M → 1G → 10G) 碾压 ATM
  ATM 硬件成本远高于以太网
  IP over Ethernet 更简单
  ATM 在 2000s 消亡
```

## 7.7 TCP over NVLink (模拟)

### 7.7.1 场景

```text
需求: 让 GPU 域内有标准 TCP/IP 通信能力
场景: GPU 作为网络处理器, 或 GPU 本地通信

方案: 在 NVLink 上模拟 TCP/IP
  ① NVLink 提供了 GPU 间低延迟互联
  ② 在 GPU 内存中分配 TCP 协议栈缓冲区
  ③ GPU kernel 模拟 TCP 协议栈 (数据搬运 + ACK)
  ④ NVLink 作为"物理层"承载

延迟: ~5-20μs (GPU 内 TCP over NVLink)
  比真正的 TCP over NIC (10-50μs) 快, 比 NVLink 原生慢 100×
  
使用: 极少的 GPU 网络处理场景, 不是主流
```

## 7.8 Infrastructure over Ethernet (完整生态)

所有 Over 技术的全景汇总：

```text
           ┌──────────────────────────────────────┐
           │           以太网 (Ethernet)             │
           ├──────────────┬───────────────┬────────┤
历史:      │ IP over X    │ FC over Eth   │ ATM    │
           │ (PPP over X) │ (FCoE)        │ over   │
           │              │               │ Eth    │
           ├──────────────┼───────────────┼────────┤
现在:      │ RDMA over    │ NVMe-oF over  │ IP     │
           │ Conv Eth     │ TCP / RDMA    │ over   │
           │ (RoCEv2)     │               │ Eth    │
           ├──────────────┼───────────────┼────────┤
未来:      │ GPU (NVLink) │ CXL.io over   │ ESUN   │
           │ over Eth     │ Eth           │ Scale-Up│
           │ (ESUN/UEC)   │ (实验性)      │ over Eth│
           └──────────────┴───────────────┴────────┘
```

## 7.9 所有 Over 技术的延迟代价速查表

| Over 方案 | 原生延迟 | Over 后延迟 | 增加倍数 | 可行性 |
|:----------|:--------:|:----------:|:--------:|:------:|
| **NVLink over Eth (ESUN)** | ~100ns | ~2-5μs | **20-50×** | 研发中 |
| **CXL.mem over Eth** | ~200ns | ~10-20μs | **50-100×** | ❌ 不可行 |
| **CXL.io over Eth** | ~1μs | ~5-15μs | **5-15×** | ✅ 部分可行 |
| **NVMe-oF over RDMA** | ~5μs | ~5-15μs | ~1-3× | ✅ 已部署 |
| **NVMe-oF over TCP** | ~5μs | ~50-500μs | **10-100×** | ✅ 已部署 |
| **IPoIB** | ~1μs | ~3-5μs | ~3-5× | ✅ 已部署 |
| **FCoE** | ~2μs | ~5-10μs | ~2.5-5× | ✅ 已部署但衰退 |
| **Ethernet over ATM** | ~10μs | ~500μs+ | **50×+** | ❌ 已消亡 |

---

# 第8章 OS 驱动的支持与影响

## 8.1 驱动参与度的光谱

```text
OS 驱动的参与程度从"零"到"每次操作必经"：

                     内存语义            I/O 语义          消息语义
                      NVLink/CXL        PCIe/NVMe         TCP/IP/IB
                      ──────────        ─────────         ─────────
运行时路径                           
<────────── 无驱动介入 ────── 初始化时 ─── 每次操作 ──────────→
                   资源配置        配置后运行        系统调用

                   配置+错误处理    配置+中断        配置+IO+中断
                   无运行时开销     中断驱动        软件中断
    
驱动职责对比:
  配置 (setup):    ✅🔵             ✅🔵             ✅🔵
  中断处理:        🔴 (错误)         ✅ (完成通知)    ✅ (数据到达)
  数据传输:        🔴               🔴 (DMA 引擎)    ✅ (直接参与)
  DMA 映射:        🔴 (硬件直通)     ✅               ✅
  地址保护:        ✅ (页表)         ✅               ✅
  错误恢复:        ✅                ✅               ✅

🔵 = 初始化时   ✅ = 需要   🔴 = 不需要
```

## 8.2 各语义对应的 Linux 驱动栈

### 8.2.1 内存语义 (NVLink / CXL)

```text
NVLink (用户态):
  应用层: CUDA (用户态)
     │ 无内核调用, 直接操作 GPU 寄存器
     ▼
  内核: nvidia.ko (仅初始化 + 错误处理)
     │ 运行时路径: ❌ 不参与
     ▼
  硬件: GPU NVLink PHY

CXL.mem (用户态):
  应用层: mmap(/dev/cxl/...) → 直接 Load/Store
     │ 无系统调用 (除初始 mmap)
     ▼
  内核: cxl.ko (枚举 + 内存热插拔)
     │ 运行时路径: ❌ 不参与
     ▼
  硬件: CXL Type 3 设备

CXL.io (驱动介入):
  应用层: mmap / IOCTL
     │ 有系统调用
     ▼
  内核: cxl.ko + 设备驱动
     │ 运行时路径: ✅ 参与 DMA 配置 + 中断
     ▼
  硬件: CXL Type 1/2 设备
```

### 8.2.2 I/O 语义 (PCIe / NVMe)

```text
PCIe 驱动栈 (以 NVMe SSD 为例):

应用层: open/read/write/close
   │ VFS (虚拟文件系统)
   │ 每次系统调用 → 内核态
   ▼
NVMe 驱动 (nvme.ko):
  ┌─────────────────────────────────────┐
  │ 提交队列 (Submission Queue):        │
  │  内核负责将 I/O 请求写入 SQ (MMIO)  │
  │                                      │
  │ 完成队列 (Completion Queue):        │
  │  硬件写 CQ → 中断 → 内核处理        │
  │                                      │
  │ DMA 映射: 内核将用户缓冲映射到物理    │
  │  地址, 写 DMA 描述符                 │
  └─────────────────────────────────────┘
   │
   ▼
NVMe 设备 (PCIe Endpoint)

延迟分解:
  - 系统调用 (read/write):            ~0.5-1μs
  - DMA 映射检查:                      ~0.2-0.5μs
  - 写 SQ (MMIO):                     ~0.1-0.3μs
  - 中断处理 (完成时):                  ~1-3μs
  ─────────────────────────────────────────
  OS 总开销:                           ~2-5μs (vs 硬件 DMA ~3-5μs)
```

### 8.2.3 消息语义 (TCP/IP)

```text
TCP/IP 驱动栈 (以 40G Ethernet 为例):

应用层: send/recv
   │ 系统调用 (每次)
   ▼
Socket 层 (内核):
  ┌─────────────────────────────────────────┐
  │ 用户态↔内核态数据拷贝                    │
  │   (copy_from_user / copy_to_user)        │
  │                                          │
  │ TCP 层: 段分割 + 序列号 + 校验和 + 重传  │
  │   全部在软件中运行 (或者硬件 offload)     │
  │                                          │
  │ IP 层: 路由 + 分片                       │
  │                                          │
  │ 网络设备层: 排队 + TX/RX                  │
  └─────────────────────────────────────────┘
   │
   ▼
NIC 驱动 (mlx5_en.ko):
  ┌─────────────────────────────────────────┐
  │ 中断处理 (NAPI):                        │
  │  数据到达 → IRQ → 软中断 → 协议栈       │
  │ PCIe DMA 配置:                          │
  │  内核分配 DMA 缓冲区, 写描述符到 NIC     │
  └─────────────────────────────────────────┘
   │
   ▼
NIC 硬件

TCP 延迟分解 (局域网):
  - 系统调用 (send/recv):                  ~1-3μs
  - 数据拷贝 (用户↔内核):                 ~2-10μs (DDR 带宽受限)
  - TCP 协议处理:                           ~3-15μs (依赖 offload)
  - 中断 + 协议栈入栈:                      ~3-10μs
  - DMA 到 NIC:                             ~1-2μs
  ─────────────────────────────────────────
  OS 总开销:                               ~10-40μs (vs 硬件 ~1-5μs)
```

## 8.3 Over 技术的额外驱动需求

每种 Over 方案对 OS 驱动的额外需求（相比原生协议）：

| Over 方案 | 不需要额外驱动 | 标准内核模块 | 专用内核模块 | 用户态库 |
|:----------|:------------:|:-----------:|:-----------:|:--------:|
| NVLink over Eth | — | — | ✅ ESUN 驱动 | ✅ 用户态库 |
| CXL.io over Eth | — | — | ✅ 实验性 | — |
| NVMe-oF over RDMA | — | ✅ nvme_rdma | — | — |
| NVMe-oF over TCP | — | ✅ nvme_tcp | — | — |
| IPoIB | — | ✅ ipoib.ko | — | — |
| EoIB | — | ✅ eoib.ko | — | — |
| FCoE | — | ✅ fcoe.ko | — | — |
| RoCEv2 | — | ✅ RDMA 栈 | — | — |
| PCIe over Cable | ✅ | — | — | — |

```text
关键洞察:
  大多数成功的 Over 方案被 Linux 内核主线接受
  → 降低部署门槛
  → 社区维护, 厂商无需自研
  
  失败的 Over 方案通常需要:
  - 专有内核模块 (不 upstream)
  - 专有用户态库
  → 生态封闭, 难以推广
```

## 8.4 Over 技术对 OS 的间接影响

### 8.4.1 中断压力

```text
原生 NVLink: 不需要中断 (CPU 零参与, 除了错误)
Over ESUN: Ethernet 中断 → 每 flit 中断一次

Ethernet 中断频率估算:
  NVLink 5.0 单端口 200 GB/s = 200 × 10⁹ / 256 = ~780M flit/s
  每个 flit 1 次中断 → 780M 中断/s → CPU 崩溃
  
缓解: 中断合并 + 轮询 (NAPI 类似)
  每 N flit 或每 T 微秒中断一次
  实际: ~100K-1M 中断/s (可接受)
  但: 增加了延迟 (等待批处理)
```

### 8.4.2 页表与地址映射

```text
Over 方案中的地址映射复杂度:

原生 NVLink:
  GPU 控制器维护 1 级地址映射 (GPU 地址 → 远端 HBM 地址)
  零页面错误 (HBM 固定映射)

NVLink over Eth:
  GPU 地址 → ESUN 网关 → 远端地址
  需要额外的隧道地址映射
  如果远端内存交换到磁盘:
    → 缺页中断通过以太网传递 → ~100μs 级延迟

解决方案: 固定 (Pin) 所有隧道内存 → 代价是灵活性降低
```

### 8.4.3 QoS / 流优先级

```text
Over 方案需要保留原始协议的 QoS 要求:

原生 NVLink: 5 个 VC (Virtual Channel)
  VC0 (Request/低延迟) → 硬件仲裁
  VC1 (Response/最高优先级)
  VC2 (Write/中等)
  VC3 (Atomic/最高)
  VC4 (SHARP/中等)

Over Eth (需映射到):
  DSCP (DiffServ): 8 个优先级队列
  PFC (Priority Flow Control): 3-8 个优先级
  ECN (Explicit Congestion Notification): 2-bit 标记

映射复杂:
  NVLink 5 VC → Eth 3-8 优先级 = 需要融合映射
  某些 VC 的保序要求可能无法在 Eth 上满足
```

---

# 第9章 市场格局与产业生态

## 9.1 各 Over 技术的生命周期

```text
市场成熟度曲线 (2026 年):

              成熟/主流         增长/部署        实验/研发        已消亡
              ──────────       ─────────       ─────────       ──────
              RoCEv2          NVMe-oF over    ESUN/UEC        Ethernet over
                              TCP/RDMA        (GPU over Eth)  ATM
                                              
              NVMe-oF RDMA    CXL Fabric      CXL.mem over    IP over ATM
                                             Eth (实验)
              IPoIB                              
                                              
              FCoE (衰退)      PCIe over       NVLink over    
                              Cable (Gen5+)   光互联 (CPO)
                                              
市场占比:     > 70%           ~20%             ~8%            < 2%
```

## 9.2 各厂商 Over 策略

### 9.2.1 NVIDIA

```text
核心策略: 封锁 NVLink, 推动 IB + RoCE

NVLink over Eth: ❌ 不参与 (ESUN/UEC 是竞争对手)
  → 保持 NVLink 专有, 构建 GPU 生态壁垒

CXL over Eth: 无表态 (CXL 与 GPU 竞争内存带宽, 不希望推动)

NVMe-oF over TCP: 支持 (收购 Mellanox 后推出 BlueField DPU 方案)
NVMe-oF over RDMA: ✅ 核心产品 (BlueField + ConnectX 系列)

IB: ✅ 核心产品 (ConnectX / Quantum 交换机)
RoCEv2: ✅ 支持 (Spectrum 交换机)
```

### 9.2.2 AMD

```text
核心策略: 推动开放, 打破 NVIDIA 锁定

UALink: ✅ 主导 (GPU 域开放互联, 不依赖 Eth over)
  UALink 1.0 (200G): AMD + Broadcom + Meta + MS
  UALink 2.0 (2026): 加入苹果
  
CXL: ✅ 核心支持 (EPYC + CXL)
NVMe-oF: 支持

ESUN (Ethernet for Scale-Up): ✅ 参与
  使用以太网替代 NVLink 类的私有协议
```

### 9.2.3 Intel

```text
核心策略: CXL 中心化 + Ethernet 基础设施

CXL over everything: ✅ 核心产品策略
  CXL over PCIe: 默认
  CXL over CXL Switch: Fabric 扩展
  CXL over Optical: IOWN 计划

NVMe-oF: ✅ 支持 (Sapphire Rapids 内置)

IPoIB: 支持 (Omni-Path 已放弃, 转向 IB)
以太网: ✅ 核心 (Ethernet 800 系列)
```

### 9.2.4 云厂商 (Meta / Google / MS / AWS)

```text
核心策略: 开放生态, 打破硬件锁定

ESUN (Meta + MS): 
  用开放以太网替换 Scale-Up 私有协议
  目标: 一台 8-GPU 服务器用单一以太网架构 (Scale-Up + Scale-Out)
  现状: 技术上仍需突破延迟瓶颈
  
CXL over Eth (Google + AWS):
  Google: 实验性用于 TPU 互联
  AWS: Nitro 已经部分实现 (SRD over Ethernet)

NVMe-oF: ✅ 广泛部署
  AWS: EBS (NVMe-oF over RDMA)
  Azure: 类似方案
  GCP: Hyperdisk
```

## 9.3 市场趋势总结

```text
加速过时的技术:     正在主流的技术:         新兴的技术:
  FCoE               NVMe-oF over RDMA/TCP   ESUN / UEC
  IPoIB               RoCEv2                 CXL over CXL Switch
  传统 FC SAN         CXL.io (已标准化)       CXL over Optical
  Ethernet over X     PCIe over Cable         MemSem over Ethernet
                      
                     市场位置:
                     专用高性能               开放低成本
                     短距离                   长距离
                     低延迟                   高延迟容忍
                     单厂商                   多厂商
```

---

# 第10章 总结与展望

## 10.1 核心结论

### 10.1.1 三大语义的不可替代性

```text
内存语义 (Memory):  延迟关键 (<1μs), 编程简单, 距离受限
I/O 语义 (DMA):      平衡方案 (1-5μs), 适合块设备/大传输
消息语义 (Message): 通用方案 (>1μs), 距离无限, 生态最大

三者将在可预见的未来共存:
  域内 (GPU 间):     内存语义 → 演进方向是更大域 + 更低延迟
  域间 (机架间):     消息语义 → 演进方向是更低延迟 + 更高带宽
  存储访问:          I/O 语义 (NVMe-oF) → 朝着 RDMA 和 TCP 双路径
```

### 10.1.2 Over 技术的核心矛盾

```text
所有 Over 技术都面临的"不可能三角":

                     低延迟 (原生协议保留)
                          /\
                         /  \
                        /    \
                       /      \
                      /  ❌   \
                     /   (此区域无法同时满足)    \
                    /                            \
  ┌───────────────/──────────────────────────────────┐
  │                   │                              │
  开放低成本 (承载协议)    语义保真度 (不丢失特性)
  
实际取舍:
  ESUN (NVLink over Eth): 放弃低延迟, 换开放+成本
  CXL over Eth: 放弃.mem .cache, 只保留.io (放弃高语义)
  NVMe-oF over TCP: 放弃低延迟 (50-500μs), 换通用性
  FCoE: 放弃了原生 FC 的可靠性保证 (FC-BB6 的妥协)
```

### 10.1.3 OS 驱动的角色演变

```text
趋势: 不断将数据路径移出内核

过去: TCP/IP 全部在内核 → 高延迟
现在: RDMA 完全硬件卸载 → 用户态直通 (Kernel Bypass)
未来: Over 方案的硬件卸载

关键: 成功的 Over 方案 = 硬件 Offload + 标准内核模块 (仅配置管理)
失败的方案 = 软件 Over + 专有内核模块
```

## 10.2 未来展望 (2026-2030)

### 10.2.1 内存语义的"域扩张"

```text
2024: NVLink 5.0 → 域内 72 GPU, ~100ns 延迟
2026: NVLink 6.0 → 域内 144+ GPU, ~40ns 延迟 (预期)
     UALink 1.0 → 域内 16+ GPU, ~100-150ns
     CXL 3.0 Fabric → 域内 4,096 节点, ~200-500ns
2028: 光互联 CPO → 一致性域扩展到 10m+
2030: 可能实现全光互联的一致性域扩展到机柜间

关键趋势: 内存语义正在向右 (大域) 扩张
  但不太可能完全替代消息语义 (全局扩展仍需消息)
```

### 10.2.2 Over 技术的未来命运

```text
成功的 Over 技术将具备以下特征:
  1. 延迟代价 < 5× 原生
  2. 承载协议基础设施广泛部署
  3. 硬件卸载 (不增加 CPU 负担)
  4. 被 OS 内核主线支持
  5. 不丢失核心语义特性

具备成功潜力的:
  - NVLink over Eth (ESUN): ❌ 延迟代价 20-50× → 只有域间场景可行
  - NVMe-oF: ✅ 已经成功, 继续演进 (多路径 + NVMe 2.0)
  - CXL over CXL Switch: ✅ 正在成功, 取代 CXL over Eth
  - 光互联承载: 中性, 取决于 CPO 成本

可能消亡的:
  - FCoE: 正在被 NVMe-oF 替代
  - IPoIB: 管理面需要, 但退出数据面
  - Ethernet over ATM: 已消
```

### 10.2.3 最终形态预测

```text
数据中心互联的"三层共存"结构 (2030):

┌──────────────────────────────────────────────────────┐
│  第1层: 域内 (Scale-Up)   < 2m                      │
│  - 内存语义 (NVLink / UALink / CXL)                 │
│  - ~100ns 级延迟                                     │
│  - TB/s 级带宽                                       │
│  - ✅ 原生协议 (非 Over)                              │
│  - 专用硬件 / 光 CPO                                 │
├──────────────────────────────────────────────────────┤
│  第2层: 机架间 (Scale-Out)   < 100m                 │
│  - 内存语义 + 消息语义混合 (RoCEv3 / ESUN / UEC)     │
│  - ~1-5μs 级延迟                                    │
│  - Tb/s 级带宽                                       │
│  - ✅ Over 协议 (NVLink/Eth, MemSem/Eth)             │
│  - 以太网基础设施 (开放)                              │
├──────────────────────────────────────────────────────┤
│  第3层: 跨数据中心   > 100m                          │
│  - 消息语义 (TCP/IP / QUIC)                          │
│  - ~1-100ms 级延迟                                   │
│  - Gb/s-Tb/s 级带宽                                  │
│  - ✅ 原生 IP 协议                                   │
│  - 标准 WAN 基础设施                                 │
└──────────────────────────────────────────────────────┘
```

---

# 附录

## A. 术语表

| 术语 | 英文 | 定义 |
|:-----|:------|:------|
| **Memory Semantics** | 内存语义 | 通过 Load/Store 指令直接访问远端内存 |
| **Message Semantics** | 消息语义 | 通过 Send/Recv 配对显式传递数据 |
| **I/O Semantics** | I/O 语义 | 通过 DMA 引擎完成数据搬运 |
| **Over** | 封装/承载 | 一种协议在另一种协议上传输 |
| **Tunneling** | 隧道 | Over 的另一种说法, 强调透明传输 |
| **RDMA** | Remote Direct Memory Access | 远端直接内存访问 (内存语义 + I/O 语义混合) |
| **NVMe-oF** | NVMe over Fabrics | NVMe 协议在各种网络上传输 |
| **RoCE** | RDMA over Converged Ethernet | RDMA 在融合以太网上承载 |
| **IPoIB** | IP over InfiniBand | IP 协议在 IB 网络上承载 |
| **FCoE** | Fibre Channel over Ethernet | FC 在以太网上承载 (已衰退) |
| **ESUN** | Ethernet for Scale-Up Networking | 用以太网承载 GPU 域内互联的开放标准 |
| **UEC** | Ultra Ethernet Consortium | 超以太网联盟, 推动以太网 AI 网络 |
| **CXL** | Compute Express Link | 在 PCIe 上实现缓存一致性内存语义 |
| **SHARP** | Scalable Hierarchical Aggregation... | NVSwitch 内集合通信引擎 |

## B. 参考来源

1. PCI-SIG, *PCI Express Base Specification Rev 6.0*, 2022
2. CXL Consortium, *Compute Express Link 3.1 Specification*, 2025
3. InfiniBand TA, *InfiniBand Architecture Rev 1.7*, 2024
4. NVM Express Inc., *NVMe-oF 1.1 Specification*, 2024
5. IEEE 802.3, *IEEE Ethernet Standards (RoCEv2)*, 2024
6. OCP, *ESUN Initiative Whitepaper*, 2025
7. UEC, *Ultra Ethernet Requirements Specification*, 2026
8. Ultra Accelerator Link Consortium, *UALink 2.0 Specification*, 2026
9. Linux Kernel, *iproute2/ipoib/fcoe/nvme Documentation*, 2026
10. SemiAnalysis, *AI Networking Deep Dive*, 2025
11. NTT IOWN, *Photonic-Electronic Converged Network Architecture*, 2025
12. CIS 533, *Interconnect Semantics and Protocol Overheads*, Stanford, 2023

## C. 历史进程时间线

```text
1970s: Ethernet (消息语义), TCP/IP (消息语义)
1980s: ATM (信元交换), SCSI (I/O 语义)
1990s: PCI (I/O 语义), FC (消息语义+存储)
        Ethernet over ATM ❌ (信元税 + 复杂)
2000s: InfiniBand (内存+消息混合, RDMA)
        iSCSI (SCSI over TCP, I/O over 消息)
        FCoE (FC over Ethernet)
2010s: NVMe (原生 PCIe, I/O 语义)
        RoCEv2 (RDMA over 以太网, 广泛部署)
        NVMe-oF (NVMe over 网络, I/O 语义的远程化)
2020s: CXL (Cache-coherent 内存语义 over PCIe)
        NVLink 4/5 (GPU 域极致内存语义)
        UALink/ESUN (开放 GPU 域互联战斗开始)
2026+: CXL Fabric (域扩展), CPO 光互联
        ESUN/UEC 产品化? 或停留在标准?
```
