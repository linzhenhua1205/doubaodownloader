# 语义论：何为语义——五大语义族的本质、特征与三级操作接口全景

> **概要**: 从第一性原理定义"语义"为接口行为契约，建立内存/I/O/网络/存储/一致性五大语义族的 MECE 分类，按指令级(L0)/API级(L1)/线格式级(L2)三级操作接口逐族展开特征与接口，并给出对比矩阵、选型决策树与 2026-2030 语义融合演进判断。
> **版本**: v1.0 · 2026-08-19
> **日期**: 2026-08-19
> **核心问题**: 何为语义？内存/IO/网络/存储/一致性五大语义族如何区分？各自特征与操作接口是什么？
> **适用范围**: 服务器/AI 基础设施互联架构设计、协议选型、系统编程模型理解
> **关键词**: 语义(Semantics), 内存语义, I/O语义, 网络语义, 通道语义, 存储语义, 一致性语义, 操作接口, CXL, RDMA, NVMe

---

## 目录

- [1. 何为语义（本体论）](#1-何为语义本体论)
  - [1.1 从语言学到系统协议的"语义"](#11-从语言学到系统协议的语义)
  - [1.2 语义的形式化定义：接口契约](#12-语义的形式化定义接口契约)
  - [1.3 为什么会有不同的语义：物理约束决定语义分化](#13-为什么会有不同的语义物理约束决定语义分化)
  - [1.4 操作接口：语义在现实世界的投影](#14-操作接口语义在现实世界的投影)
- [2. 语义分类学（MECE 五大语义族）](#2-语义分类学mece-五大语义族)
  - [2.1 分类维度](#21-分类维度)
  - [2.2 五大语义族总览](#22-五大语义族总览)
- [3. 内存语义（Memory Semantics）](#3-内存语义memory-semantics)
  - [3.1 定义与本质](#31-定义与本质)
  - [3.2 三种子类型](#32-三种子类型)
  - [3.3 特征量化](#33-特征量化)
  - [3.4 操作接口：指令级 / API级 / 线格式级](#34-操作接口指令级--api级--线格式级)
- [4. I/O 语义（I/O Semantics）](#4-io-语义io-semantics)
  - [4.1 定义与本质](#41-定义与本质)
  - [4.2 子类型：PIO / MMIO / DMA / 中断](#42-子类型pio--mmio--dma--中断)
  - [4.3 特征量化](#43-特征量化)
  - [4.4 操作接口：从 MMIO 到 io_uring / SPDK](#44-操作接口从-mmio-到-io_uring--spdk)
- [5. 网络语义（Network Semantics）](#5-网络语义network-semantics)
  - [5.1 定义与本质](#51-定义与本质)
  - [5.2 IBTA 权威分类：通道语义 vs 内存语义](#52-ibta-权威分类通道语义-vs-内存语义)
  - [5.3 传输服务维度：RC / UC / UD / XRC](#53-传输服务维度rc--uc--ud--xrc)
  - [5.4 特征量化](#54-特征量化)
  - [5.5 操作接口：Socket / MPI / Verbs](#55-操作接口socket--mpi--verbs)
- [6. 存储语义（Storage Semantics）](#6-存储语义storage-semantics)
  - [6.1 定义与本质：持久性保证](#61-定义与本质持久性保证)
  - [6.2 命令队列语义：NVMe SQ/CQ 模型](#62-命令队列语义nvme-sqcq-模型)
  - [6.3 块 / 文件 / 对象三级语义](#63-块--文件--对象三级语义)
  - [6.4 特征量化](#64-特征量化)
  - [6.5 操作接口：VFS / POSIX / io_uring / SPDK](#65-操作接口vfs--posix--io_uring--spdk)
- [7. 一致性语义（Coherence Semantics）](#7-一致性语义coherence-semantics)
  - [7.1 定义与本质：缓存视图的一致性](#71-定义与本质缓存视图的一致性)
  - [7.2 协议族：侦听 / 目录 / 自旋](#72-协议族侦听--目录--自旋)
  - [7.3 CXL.cache 与 CXL 3.0 硬件一致性](#73-cxlcache-与-cxl-30-硬件一致性)
  - [7.4 特征与代价](#74-特征与代价)
- [8. 五大语义族全维度对比](#8-五大语义族全维度对比)
  - [8.1 对比矩阵](#81-对比矩阵)
  - [8.2 选型决策树：场景 → 语义](#82-选型决策树场景--语义)
  - [8.3 语义的"不可能三角"](#83-语义的不可能三角)
- [9. 语义融合与演进（2026-2030）](#9-语义融合与演进2026-2030)
  - [9.1 网络语义的"内存化"：MemSem over Ethernet](#91-网络语义的内存化memsem-over-ethernet)
  - [9.2 内存语义的"域扩张"：CXL Fabric / UALink](#92-内存语义的域扩张cxl-fabric--ualink)
  - [9.3 存储语义的"GPU 化"：GPUDirect Storage](#93-存储语义的gpu-化gpudirect-storage)
  - [9.4 语义融合的本质：物理层趋同，语义层分化](#94-语义融合的本质物理层趋同语义层分化)
- [10. 结论](#10-结论)
- [参考文献](#参考文献)
- [变更记录](#变更记录)

---

## 1. 何为语义（本体论）

### 1.1 从语言学到系统协议的"语义"

"语义"(Semantics) 源于语言学：研究**符号与其所指意义之间的关系**。索绪尔的结构主义语言学将符号拆为**能指**(Signifier，符号本身)与**所指**(Signified，符号指向的意义)——"dog"这个词(能指)与"狗"这种动物(所指)的对应关系，就是语义。

计算机系统借用这个概念时，做了工程化改造：

| 语言学术语 | 系统协议对应物 | 例子 |
|:-----------|:---------------|:-----|
| 能指（符号形式） | **语法（Syntax）**：消息/指令的字节格式 | `0x01 0x00 0x00 0x00` 是一个读请求 |
| 所指（符号意义） | **语义（Semantics）**：该操作的含义、行为保证 | 该读请求会返回 64B 数据并更新缓存 |
| 语用（使用语境） | **时序（Timing）/协议状态机**：何时合法发出 | 读请求只能在链路就绪后发出 |

**关键点**：在计算机系统里，语义不是"含义的哲学探讨"，而是**可验证的行为契约**——它精确回答五个问题：

```text
A data movement / operation contract answers 5 questions:

1. WHO    - who initiates?      (CPU instr / device DMA / paired both sides)
2. WHAT   - what is operated?   (byte / block / message / file)
3. WHERE  - how addressed?      (PA / VA / LBA / handle / path)
4. HOW    - who executes?       (HW direct / DMA engine / driver / protocol stack)
5. GUARANTEE - what is promised?(best-effort / reliable / ordered / coherent / durable / atomic)
```

**在系统语境下，语义 = 一个接口对其行为承诺的完整描述。** 语法告诉你"消息长什么样"，语义告诉你"这件事做完后世界变成了什么样"。

### 1.2 语义的形式化定义：接口契约

工程上可将任一操作的语义形式化为四元组契约：

```text
Semantics(Op) = { Precondition, Effect, Postcondition, FailureMode }

Example 1: read() syscall
  Precondition :  fd open & readable, buf points to valid user memory
  Effect       :  copy min(len, remaining) bytes from file offset to buf
  Postcondition:  return n bytes read, file offset advanced by n;
                  n < len means EOF or EINTR
  FailureMode  :  EIO (HW error) / EFAULT (bad buf) / EAGAIN (nonblock, no data)

Example 2: RDMA Read (ibv_post_send WR=RDMA_READ)
  Precondition :  QP connected, local/remote MR registered, rkey valid
  Effect       :  data at remote address DMA-written into local buffer by RNIC
  Postcondition:  CQE appears in completion queue; remote CPU not involved
  FailureMode  :  QP enters Error state (bad rkey / address out of range)
```

这个形式化视角的价值：**比较两种语义，本质是比较它们的行为契约差异**——尤其是 Postcondition（完成保证）与 FailureMode（失败行为）。例如：

- `memcpy()` 与 `RDMA Read` 的 Postcondition 都是"数据到达目标缓冲区"，但前者由 CPU 保证（同步返回即完成），后者由硬件保证（CQE 出现才完成）——这就是"内存语义 vs 网络内存语义"在接口层的最小差异。
- `write()` 与 `pwrite()` 的差异只在寻址（隐式偏移 vs 显式偏移），语义其余部分相同——说明**寻址方式本身就是语义的一部分**。

### 1.3 为什么会有不同的语义：物理约束决定语义分化

这是全文的第一性原理。**语义不是人为发明的，而是物理约束的投影**。同一份数据搬运需求，在不同物理条件下会收敛到不同的最优语义：

```text
Physical constraints (distance / latency / reliability / cost / energy)
        |
        v  design tradeoff (latency budget x reliability cost x distance cost)
        |
+-------+--------+--------+--------+
|       |        |        |        |
v       v        v        v        v
Memory  I/O      Network  Storage  Coherence
(~100ns)(~1-5us) (~1-100us)(~10us-ms)(support layer)
```

| 物理约束 | 约束值域 | 收敛出的语义 | 推理链条 |
|:---------|:---------|:-------------|:---------|
| **距离** | <1m（板上/域内） | 内存语义 | 延迟预算 ~100ns，只有硬件直通 Load/Store 能达到；软件介入(驱动/协议栈)至少 +1μs，超预算 |
| **距离** | 1m~100m（机架/机房） | I/O 语义、网络语义 | 延迟预算放宽到 μs 级，DMA 卸载和消息传递成为可能；距离越长，可靠性越重要 |
| **距离** | >100m（跨机房/跨地域） | 网络语义（TCP/QUIC） | μs 预算彻底失效，端到端可靠传输(重传/拥塞控制)成为主导 |
| **持久性需求** | 断电后数据必须保留 | 存储语义 | 内存语义天然挥发；持久化需要介质特性(Flash)与命令语义(flush/fence)配合 |
| **多参与者共享** | 多核/多卡读同一数据 | 一致性语义 | 没有缓存一致性，共享内存编程模型直接崩溃；但一致性有带宽放大代价，需按场景取舍 |

推论（重要）：**语义的可移植性受物理约束限制**。一致性语义无法"over"不可靠网络（CXL.cache over Ethernet 不可行，因为一致性协议依赖可靠的保序通道）；内存语义无法跨 100m 距离保持 ~100ns 延迟（光速限制：100m 单程光延迟约 500ns，RTT 1μs 已超预算）。这解释了 [来源: knowledge/02_rd/01_product/00_hardware/01_hw-core/2026-06-25-semantics-and-protocol-over.md §6.2] 中所有 Over 技术的本质困境。

### 1.4 操作接口：语义在现实世界的投影

语义是抽象的（行为契约），操作接口是具体的（如何调用）。**同一个语义族，在不同抽象层有三级操作接口**——这是理解"操作接口"的关键框架：

```text
L0 instruction level (ISA): CPU instructions / HW primitives, closest to HW
                            e.g. LD/ST, MMIO access, CAS, fence

L1 API / syscall level   : library / syscall / user-space framework
                            e.g. memcpy(), read(), send(), ibv_post_send(),
                                 MPI_Send(), io_uring_enter()

L2 wire-format level     : on-wire byte format, contract between HW peers
                            e.g. PCIe TLP, CXL flit, IB BTH packet,
                                 NVMe 64B command, TCP segment header
```

三层接口的关系：**L1 是 L0 的封装，L2 是 L0 的线下表达**。程序员写 `memcpy()`（L1），CPU 翻译为 LD/ST 指令（L0），若目标在远端则硬件打包为 CXL flit（L2）在线路上传输。**"操作接口"的完整图景 = 三层接口的逐层映射**。本文第 3-7 章对每个语义族都按此三级框架展开。

---

## 2. 语义分类学（MECE 五大语义族）

### 2.1 分类维度

为避免"内存语义/IO语义/网络语义"这类日常用语的重叠歧义，本文用 **5 个正交维度** 做分类，每个维度取值互斥：

| 维度 | 取值（互斥） | 说明 |
|:-----|:-------------|:-----|
| **D1 寻址模型** | 地址空间 / 队列+句柄 / 命令+LBA / 文件路径 / 缓存行标签 | 数据如何被指称 |
| **D2 执行主体** | CPU 硬件直通 / DMA 引擎 / 双方软件栈 / 设备固件 / 一致性协议代理 | 谁实际搬运数据 |
| **D3 完成保证** | 指令完成即保证 / 中断或轮询通知 / ACK 确认 / 持久化落盘 / 一致性域收敛 | 何时可以认为操作完成 |
| **D4 一致性** | 无 / 可选 / 强制缓存一致 | 多视图是否统一 |
| **D5 持久性** | 易失 / 断电持久 | 掉电后数据是否保留 |

### 2.2 五大语义族总览

| 语义族 | D1 寻址 | D2 执行 | D3 完成保证 | D4 一致性 | D5 持久 | 代表协议/接口 |
|:-------|:--------|:--------|:------------|:----------|:--------|:--------------|
| **内存语义** | 统一地址空间 | CPU 硬件直通 | 指令完成即完成 | 可选(裸/一致/原子) | 易失 | CXL.mem, NVLink, RDMA R/W |
| **I/O 语义** | 设备寄存器+物理地址 | DMA 引擎 | 中断/轮询通知 | 无 | 易失 | PCIe, NVMe(本地), SATA |
| **网络语义** | 消息句柄(QP/Socket) | 双方协议栈/硬件卸载 | ACK/保序/拥塞控制 | 无 | 易失 | IB, RoCEv2, TCP, MPI |
| **存储语义** | 命令+逻辑块(LBA)/路径 | 设备固件+介质 | 命令完成/持久化确认 | 无 | **持久** | NVMe, SCSI, NFS, S3 |
| **一致性语义** | 缓存行标签 | 一致性协议代理 | 一致性域收敛 | **强制** | 易失 | MESI, CXL.cache, CXL 3.0 HCHC |

> 边界说明：五大族并非互斥实现，而是**正交的语义维度**。RDMA 同时携带内存语义（Read/Write 单侧）与网络语义（跨节点传输）；NVMe-oF 同时携带 I/O 语义（命令队列）、存储语义（持久化）与网络语义（跨网络）。分类的价值在于**识别每个维度上的语义承诺**，而非给协议贴单一标签。

---

## 3. 内存语义（Memory Semantics）

### 3.1 定义与本质

**内存语义：通信双方将对方的内存视为自己物理地址空间的自然延伸，CPU 发起的 Load/Store 指令可直接命中远端内存，无需驱动介入。**

本质特征：**启动者 = 执行者**——CPU 一条指令既是发起也是执行，硬件（内存控制器→互联控制器→远端）自动完成 [来源: knowledge/02_rd/01_product/00_hardware/01_hw-core/2026-06-25-semantics-and-protocol-over.md §2.1]。

```text
CPU view of a unified address space:
  +------------------------------------------------+
  | 0x0000_0000 ... local DRAM       (local MC)      |
  | 0xF000_0000 ... remote GPU HBM   (via NVLink)    |
  | 0xE000_0000 ... remote CXL pool  (via CXL.mem)   |
  +------------------------------------------------+
  LD/ST instructions identical for local & remote; only address range differs
```

### 3.2 三种子类型

| 子类型 | 一致性 | 原子操作 | 代表 | 典型延迟 |
|:-------|:------:|:--------:|:-----|:---------|
| **裸内存语义** (Raw) | ❌ 无 | ❌ | RDMA Read/Write | ~1-3μs (IB), ~3-15μs (RoCEv2) |
| **一致性内存语义** (Coherent) | ✅ 强制 | 部分 | CXL.mem, NVLink 域内 | ~100-300ns (CXL), ~100-200ns (NVLink) |
| **原子内存语义** (Atomic) | 可选 | ✅ CAS/FAA | NVLink CAS, RDMA Atomic | ~300-500ns (NVLink), ~3-8μs (RDMA) |

- 裸内存语义：远端 CPU 零参与，单侧操作（One-sided），地址需预先注册（MR + rkey 保护）。
- 一致性内存语义：增加缓存一致性协议（MESI 变体），保证所有参与者 cache 视图一致。CXL.mem 的 S2M Read / M2S Write / S2M MemInv 是典型操作 [来源: knowledge/02_rd/00_shared/01_architecture/2026-07-22-cxl-chip-industry-deep-dive.md §1.2]。
- 原子内存语义：在硬件内锁定地址执行读-改-写（Compare-And-Swap, Fetch-And-Add），用于分布式锁/计数器，避免网络往返竞态。

### 3.3 特征量化

| 维度 | 数值 | 条件/来源 |
|:-----|:-----|:----------|
| 延迟（CXL.mem Type 3 随机访问） | ~110-210ns | [来源: semantics-and-protocol-over §2.2.2] |
| 延迟（NVLink 5 域内） | ~100-200ns | [来源: semantics-and-protocol-over §2.2.2] |
| 延迟（RDMA Read 4KB, 同机房 400G） | ~3-5μs | [来源: dma-rdma-complete-analysis §8.2] |
| 带宽密度 | TB/s 级（NVLink 5 单端口 ~200GB/s） | [来源: dma-rdma-complete-analysis] |
| CPU 运行时开销 | 零（配置后无系统调用/无中断） | [来源: semantics-and-protocol-over §2.3.2] |
| 距离极限 | <1m（裸），光扩展 ~100m（一致性丢失） | [来源: semantics-and-protocol-over §5.1] |
| 规模极限 | ~72 GPU（NVLink 域）/ ~4096 节点（CXL 3.0 Fabric） | [来源: semantics-and-protocol-over §10.2.1] |

### 3.4 操作接口：指令级 / API级 / 线格式级

**L0 指令级（ISA）**：

```text
Memory semantics instruction-level interface = normal memory ops + atomics + barriers

  LD   R1, [0xF000_0000]   ; load 8B from remote CXL memory
  ST   [0xF000_1000], R2   ; store to remote memory
  CAS  [0xF000_2000], R3   ; atomic compare-and-swap (NVLink domain)
  DMB / fence              ; enforce ordering across coherence domains
```

**L1 API 级**：

```text
C/C++:  memcpy(far_ptr, local_buf, n);   // transparent for remote pointers
        mmap(/dev/cxl/...);              // CXL memory mapping, then normal ptr access
CUDA:   cudaMemcpyPeer / UVM (unified virtual memory);  // cross-node memory semantics
Kernel: DAX / memremap_pages            // direct-mapped persistent memory (famfs)
```

**L2 线格式级**：

```text
CXL.mem protocol messages (inside 528B flit):
  S2M Read Request   : [ReqHeader | Address | Tag | Length] -> device returns Data
  M2S Write          : [ReqHeader | Address | Tag | Data]   -> device acks
  S2M MemInv         : device notifies host of cache-line invalidation

IB RDMA packets (BTH + payload):
  RDMA Read Request  : [Base Transport Header | RKey | VA | Length]
  RDMA Read Response : [BTH | RKey | Data]
```

**接口设计要点**：内存语义 L1 接口的"魔法"在于——`memcpy` 不需要知道目标在本地还是远端，**地址即语义**。这是它与 I/O 语义最根本的接口差异。

---

## 4. I/O 语义（I/O Semantics）

### 4.1 定义与本质

**I/O 语义：CPU 不直接访问目标数据，而是通过控制寄存器配置一个 DMA 引擎，由引擎异步完成搬运，完成后以中断或轮询通知。**

本质特征：**启动者 ≠ 执行者**——CPU 负责发起（写寄存器），DMA 引擎负责执行，中断负责完成通知。这是"中间态"语义：比内存语义多一次寄存器写与一次完成通知，比网络语义少一层协议栈 [来源: semantics-and-protocol-over §4.1]。

```text
CPU --MMIO write--> DMA engine --async transfer--> target device
  | (config desc + start)     | (src -> buffer -> dst)
  +---------- interrupt / poll <-------+ (completion notify)
```

### 4.2 子类型：PIO / MMIO / DMA / 中断

| 子类型 | 机制 | 延迟 | 现状 |
|:-------|:-----|:-----|:-----|
| **PIO** (Programmed I/O) | CPU 逐字节/字搬运到设备寄存器 | ~100ns-1μs | 仅控制面小数据 |
| **MMIO** (Memory-Mapped I/O) | 设备寄存器映射到地址空间，LD/ST 访问 | ~100-500ns | 配置面标准做法 |
| **DMA** (Direct Memory Access) | 引擎按描述符搬运，含 SG 列表 | ~0.5-3μs (PCIe Gen5) | 数据面主流 |
| **MSI-X 中断** | 设备向 CPU 发中断向量 | 通知 ~1-3μs | 完成通知标准 |

### 4.3 特征量化

| 维度 | 数值 | 条件/来源 |
|:-----|:-----|:----------|
| 延迟（PCIe Gen5 DMA） | ~0.5-3μs | [来源: semantics-and-protocol-over §4.2.2] |
| 延迟（NVMe 提交队列） | ~0.3-1μs | [来源: semantics-and-protocol-over §4.2.2] |
| OS 总开销（NVMe 路径） | ~2-5μs（syscall+DMA映射+中断） | [来源: semantics-and-protocol-over §8.2.2] |
| 粒度 | 块级（KB-MB） | [来源: semantics-and-protocol-over §4.3] |
| 一致性 | 无（绕过 CPU cache 或需显式 flush） | [来源: semantics-and-protocol-over §4.3] |
| CPU 每操作开销 | ~500-2000 条指令（描述符构造+中断处理） | [来源: semantics-and-protocol-over §5.1] |

### 4.4 操作接口：从 MMIO 到 io_uring / SPDK

**L0 指令级**：

```text
MMIO access = normal LD/ST hitting device BAR (uncacheable attribute):

  ST  [PCIe_BAR0 + 0x00], 0x1      ; write DMA control reg (start)
  LD  R1, [PCIe_BAR0 + 0x04]       ; read status reg (poll for done)
```

**L1 API 级**（三档，按性能与复杂度）：

```text
Classic syscall path:  read(fd, buf, len)
                       -> VFS -> driver builds DMA desc -> submit SQ -> irq -> done
                       OS overhead ~2-5us, one syscall per I/O

io_uring path:         io_uring_prep_read(sqe, fd, buf, len, 0);
                       io_uring_submit(ring);           // batch submit, fewer syscalls
                       io_uring_wait_cqe(ring);         // poll completion, SQPOLL no irq
                       per-I/O overhead down to ~0.5-1us [Source: io_uring design goal]

User-space direct:     spdk_nvme_ns_cmd_read(ns, buf, lba, blocks, cb, arg);
                       // bypass kernel, drive NVMe SQ/CQ queues directly, poll done
                       // no syscalls, latency close to HW limit
```

**L2 线格式级**：

```text
PCIe TLP (Transaction Layer Packet):
  MWr (Memory Write)      : [TLP Header | Address | Data]    write mem/device
  MRd (Memory Read)       : [TLP Header | Address]           read request
  CplD (Completion w/Data): [TLP Header | Data]              read response

NVMe command (64B, written to SQ):
  [OPC | CID | NSID | ... | PRP1/SGL | ...]
  e.g. OPC=0x02 (Write), NSID=namespace, LBA=start block, NLB=block count
  Doorbell write (MMIO) notifies device "new command available"
```

**接口设计要点**：I/O 语义的 L1 接口经历了三代演进——**同步 syscall（每 I/O 一次内核往返）→ 异步批量（io_uring 削减 syscall 与中断）→ 用户态直通（SPDK 完全绕过内核）**。演进方向与内存语义一致：**不断把软件从数据路径上移走** [来源: semantics-and-protocol-over §10.1.3]。

---

## 5. 网络语义（Network Semantics）

### 5.1 定义与本质

**网络语义：数据在节点之间传递的语义——解决"如何把一段数据从节点 A 可靠/高效地送到节点 B"。**

本质特征：**距离不受限**（是唯一能跨机架、跨数据中心、跨地域的语义族），代价是**延迟预算放宽到 μs-ms 级**，必须引入可靠性机制（确认、重传、保序、拥塞控制）[来源: semantics-and-protocol-over §3.1]。

网络语义内部存在两种本质不同的子语义——这是理解 RDMA 与 TCP 差异的钥匙：

| 子语义 | 模型 | 谁参与 | 典型 | 一句话本质 |
|:-------|:-----|:-------|:-----|:-----------|
| **通道语义** (Channel) | 消息传递：Send/Recv 显式配对 | 两端 CPU 都参与 | IB Send/Recv, TCP, MPI, Socket | "我把消息推给你，你接住" |
| **内存语义** (Memory) | 数据搬运：单侧读写远端内存 | 仅发起端参与 | RDMA Read/Write/Atomic | "我直接读写你的内存" |

### 5.2 IBTA 权威分类：通道语义 vs 内存语义

InfiniBand 架构规范（IBTA）是网络语义分类的权威来源：**IB 的 verbs 操作集明确分为两类语义** [来源: 领域知识, IBTA InfiniBand Architecture Spec Vol.1, verbs 操作分类]：

**通道语义（Channel Semantics）**——对应 Send/Recv 操作：

```text
Sender:  ibv_post_send(qp, WR=SEND, buf=C)    -> data pushed out
Receiver:ibv_post_recv(qp, WR=RECV, buf=D)    -> pre-posted receive buffer
         both sides must explicitly pair; receiver does not know msg size,
         length carried in SEND
         completion: CQE on sender + CQE on receiver (both CPUs notified/polled)

Data semantics: message boundary preserved (IB) or byte stream (TCP);
                explicit coordination required on both ends
Essence: push model, data ownership handed from sender to receiver
```

**内存语义（Memory Semantics）**——对应 RDMA Read/Write/Atomic 操作：

```text
RDMA Write:  ibv_post_send(qp, WR=RDMA_WRITE, remote_addr=B, rkey=K)
             -> local data DMA'd directly to remote address B
             remote CPU not involved; only sender gets CQE

RDMA Read:   ibv_post_send(qp, WR=RDMA_READ, remote_addr=B, rkey=K)
             -> request-response: remote RNIC reads B and returns data
             remote CPU not involved; only initiator gets CQE; latency = RTT

Atomic:      ibv_post_send(qp, WR=ATOMIC_CMP_AND_SWP, remote_addr=X, ...)
             -> remote RNIC performs read-modify-write inside HW
             for dist locks/counters; ~0.5-2us slower than Read [Source: dma-rdma 8.1.4]

Essence: pull/push hybrid; remote memory treated "as if local"
```

**关键洞察**：IBTA 的"内存语义"与本文第 3 章的"内存语义"是同一概念在不同物理域的投影——**RDMA 把内存语义搬上了网络，但丢掉了缓存一致性，保留了单侧零拷贝**。代价是地址需要显式注册（MR/rkey）与密钥保护 [来源: dma-rdma-complete-analysis §8.1]。

### 5.3 传输服务维度：RC / UC / UD / XRC

IB 在通道/内存语义之上，还定义了四种传输服务（可靠性 × 连接性正交）：

| 服务 | 可靠 | 连接 | 保序 | 消息大小 | 典型用途 |
|:-----|:----:|:----:|:----:|:---------|:---------|
| **RC** (Reliable Connection) | ✅ | ✅ | ✅ | 不限（可分段） | GPU 通信、分布式训练 |
| **UC** (Unreliable Connection) | ❌ | ✅ | ❌ | 单包 | 容忍丢包的低延迟场景 |
| **UD** (Unreliable Datagram) | ❌ | ❌ | ❌ | MTU | 多播、控制面、成员发现 |
| **XRC** (eXtended RC) | ✅ | 半连接 | ✅ | 不限 | 多对多消息传递 |

RC 的可靠性机制（PSN 严格递增 + ACK + 重传 + 信用流控）保证了"可靠保序"的通道语义基础；RoCEv2 则在以太网上以 DCQCN（ECN 标记 + 拥塞反馈）实现无损网络 [来源: dma-rdma-complete-analysis §9.2/§9.3]。

### 5.4 特征量化

| 维度 | IB RDMA | RoCEv2 | TCP | 条件/来源 |
|:-----|:--------|:-------|:----|:----------|
| 延迟（小消息） | ~1-2μs | ~2-5μs | ~10-50μs | [来源: semantics-and-protocol-over §3.2] |
| 延迟（RDMA Read 4KB） | ~3-5μs | ~5-15μs | N/A | [来源: dma-rdma §8.2] |
| 原子操作 | ~3-8μs | ~5-15μs | 软件模拟 10-100× 慢 | [来源: dma-rdma §8.2] |
| CPU 参与 | 硬件卸载，用户态直通 | 同左 | 每操作内核参与 | [来源: semantics-and-protocol-over §8.2.3] |
| 距离 | 数据中心级 | 数据中心级 | 全球 | [来源: semantics-and-protocol-over §5.1] |
| 规模 | ~千-万节点 | 同左 | 百万+ | [来源: semantics-and-protocol-over §5.1] |

### 5.5 操作接口：Socket / MPI / Verbs

**L0 指令级**：网络语义没有独立 ISA 指令（由网卡硬件指令/描述符承载，可视为 L2 线格式的一部分）；对 CPU 而言接口起点在 L1。

**L1 API 级**（三套主流，覆盖三个生态）：

```text
Socket API (general / cross-region):
  int fd = socket(AF_INET, SOCK_STREAM, 0);
  connect(fd, &addr, sizeof(addr));
  send(fd, buf, len, 0);          // channel semantics: push
  recv(fd, buf, len, 0);          // channel semantics: receive
  guarantees: reliable ordered byte stream; kernel stack per op

MPI (HPC message passing):
  MPI_Send(buf, len, MPI_BYTE, dest, tag, MPI_COMM_WORLD);
  MPI_Recv(ack, 4, MPI_BYTE, src, tag, MPI_COMM_WORLD, &status);
  guarantees: message boundaries preserved; collectives (AllReduce/AllGather)
              HW-accelerated (SHARP); maps to IB channel or shared-memory semantics

Verbs API (RDMA high performance):
  struct ibv_pd *pd = ibv_alloc_pd(ctx);
  struct ibv_mr *mr = ibv_reg_mr(pd, buf, len,
                                 IBV_ACCESS_LOCAL_WRITE|IBV_ACCESS_REMOTE_WRITE);
  ibv_post_send(qp, &wr, &bad_wr);    // WR=RDMA_WRITE/READ/SEND/ATOMIC
  ibv_poll_cq(cq, n, &wc);            // poll completion queue (no interrupt)
  guarantees: one-sided zero-copy; reliability from RC service;
              remote address authorized by rkey
```

**L2 线格式级**：

```text
IB packet: [LRH | BTH | (RETH + data) | ... | ICRC/VCRC]
  BTH = Base Transport Header: OpCode (SEND/RDMA_WRITE/RDMA_READ/ATOMIC)
                              + PSN + QP number + service type (RC/UC/UD)
  RETH = RDMA Extended Transport Header: remote VA + RKey + length

RoCEv2 encapsulation: [Eth | IP | UDP (port 4791) | IB BTH | Payload | FCS]
  borrows UDP header for routing, preserves IB semantics [Source: RoCEv2 spec]

TCP segment: [IP | TCP (SEQ/ACK/Window/Flags) | Payload]
  semantics by TCP state machine: 3-way handshake, sliding-window flow control,
                                  timeout retransmission
```

**接口设计要点**：网络语义的 L1 接口差异 = **编程模型差异**。Socket 面向"流"，MPI 面向"消息"，Verbs 面向"内存操作"。三者可共存于同一物理网络，但语义承诺不同——**选接口 = 选语义 = 选性能与复杂度的平衡点**。

---

## 6. 存储语义（Storage Semantics）

### 6.1 定义与本质：持久性保证

**存储语义：对持久化介质的访问语义——核心区别在于"持久性保证"（D5 维度）：操作完成后，数据在断电/故障后是否仍然存在。**

这是存储语义与其他语义族的本质分界：内存/I/O/网络语义都是易失的（D5=易失），存储语义承诺 D5=持久。持久性保证通过介质特性（NAND/3D XPoint）+ 命令语义（flush/fence）+ 协议配合实现 [来源: knowledge/02_rd/01_product/00_hardware/06_storage/2026-07-29-network-storage-protocol-evolution.md §6]。

### 6.2 命令队列语义：NVMe SQ/CQ 模型

NVMe 定义了存储访问的现代命令语义——**内存队列 + 门铃通知 + 完成队列**：

```text
NVMe queue model:
  +---------------------+          +---------------------+
  | Submission Queue(SQ)|          | Completion Queue(CQ)|
  |  (host writes cmds) |          |  (device writes done)|
  |  [Cmd0][Cmd1]...    |          |  [Cpl0][Cpl1]...    |
  +----------+----------+          +----------^----------+
             |                                 |
     Doorbell write (MMIO)          MSI-X interrupt or polling
             v                                 |
  +----------+----------+                      |
  | NVMe controller (dev)|----------------------+
  |  parse cmd -> execute |
  +---------------------+

Semantics:
  - queues live in host memory; device reads cmds via DMA -> no per-cmd MMIO
  - multi-queue (up to 64K queues x 64K cmds), per-core queue lock-free
  - vs AHCI (single queue + 4 MMIO per cmd + irq driven) is order-of-magnitude
    improvement [Source: network-storage-protocol-evolution ch.5]
```

### 6.3 块 / 文件 / 对象三级语义

存储语义按"抽象层级"分为三级，每级语义承诺不同 [来源: network-storage-protocol-evolution §2.1]：

| 层级 | 寻址 | 语义承诺 | 代表 | 应用 |
|:-----|:-----|:---------|:-----|:-----|
| **块级** | LBA 逻辑块 | 原始读写，无文件系统语义 | NVMe, SCSI, iSCSI, NVMe-oF | 数据库裸盘、虚拟化存储 |
| **文件级** | 路径+文件名 | POSIX 语义：权限/锁/目录/原子改名 | NFS, SMB/CIFS, Lustre | 共享文件、EDA/HPC |
| **对象级** | Key（对象 ID） | REST 语义：GET/PUT/DELETE，无目录树 | S3, Swift, OSS | 云存储、大数据、AI 数据湖 |

### 6.4 特征量化

| 维度 | 数值 | 条件/来源 |
|:-----|:-----|:----------|
| 延迟（NVMe 本地） | ~5-10μs（QoS 尾延迟受 GC 影响） | [来源: network-storage-protocol-evolution] |
| 延迟（NVMe-oF over RDMA） | ~5-15μs | [来源: semantics-and-protocol-over §7.3.2] |
| 延迟（NVMe-oF over TCP） | ~50-500μs | [来源: semantics-and-protocol-over §7.3.2] |
| IOPS（NVMe 企业级） | 百万级随机读 | [来源: 领域知识, 企业 SSD 规格] |
| 持久性保证 | flush/fsync/fence 命令显式落盘 | [来源: 领域知识, NVMe 规范] |
| OS 路径开销 | ~2-5μs（syscall 路径） | [来源: semantics-and-protocol-over §8.2.2] |

### 6.5 操作接口：VFS / POSIX / io_uring / SPDK

**L0 指令级**：存储语义无独立 ISA 指令，底层是 MMIO（门铃）+ DMA（命令/数据搬运）——I/O 语义的 L0 接口是存储语义的物理载体。

**L1 API 级**：

```text
POSIX/VFS:   open("file", O_RDWR); read(fd, buf, 4096); fsync(fd);
             semantics: byte stream + offset; fsync guarantees durable persist

io_uring:    io_uring_prep_read(sqe, fd, buf, len, offset);
             io_uring_prep_fsync(sqe, fd);          // async durability
             semantics: async batch + polling, fewer syscalls & interrupts

SPDK (user): spdk_nvme_ns_cmd_read(ns, buf, lba, nlb, cb, ctx);
             semantics: bypass kernel to HW, poll completion, no syscalls

GPU direct:  cufileRead(cf, devPtr, size, offset, &stream);  // GPUDirect Storage
             semantics: NVMe -> DMA straight into GPU memory, bypass host
             [Source: knowledge/03_AI/train/ai-storage/2026-08-06-gpu-initiated-io-architecture-scada-cufile-512b.md]
```

**L2 线格式级**：

```text
NVMe command (64B, written to SQ):
  [OPC(1B) | CID(2B) | NSID(4B) | ... | PRP1(8B) | PRP2/SGL(8B) | ...]
  OPC: 0x00=Flush, 0x01=Read, 0x02=Write, 0x04=Write Zeroes
  PRP/SGL: host physical memory page descriptors -> DMA target/source

SCSI CDB (Command Descriptor Block):
  [OPC | LUN | LBA | TransferLength | ...]
  OPC: 0x08=Read(10), 0x0A=Write(10), 0x2A=Write(16)

NFS protocol (RPC messages):
  GETATTR / READ / WRITE / COMMIT / LOCK
  COMMIT semantics: data persisted before returning
```

**接口设计要点**：存储语义的 L1 接口演进与 I/O 语义同构（syscall→io_uring→SPDK），但**多了持久化语义**（fsync/COMMIT/Flush）。现代 GPU 存储接口（cufileRead）把存储语义与内存语义结合——**数据直达显存，持久化保证保留**。

---

## 7. 一致性语义（Coherence Semantics）

### 7.1 定义与本质：缓存视图的一致性

**一致性语义：多参与者共享同一内存时，保证所有参与者缓存视图一致的协议语义。** 它是支撑层——本身不搬运数据，而是保证"搬运后大家看到的一样"。

一致性 ≠ 顺序一致性（Sequential Consistency）。一致性只保证**单地址单值**（同一缓存行只有一个最新值），不保证多地址间的访问顺序。顺序一致性是更强的内存模型（含重排序约束）[来源: 领域知识, 计算机体系结构教材]。

### 7.2 协议族：侦听 / 目录 / 自旋

| 协议族 | 机制 | 规模 | 代表 |
|:-------|:-----|:-----|:-----|
| **总线侦听** (Snooping) | 所有核监听总线，广播失效 | 小（~8-32 核） | MESI, MOESI, MESIF |
| **目录协议** (Directory) | 集中/分布式目录记录缓存行 owner | 大（多路/多芯片） | AMD CCX, Intel Mesh |
| **自旋协议** (Spinning) | 缓存行在参与者间轮转，写者持锁 | 极小/专用 | CXL.cache 的 M2S/S2M 流 |

### 7.3 CXL.cache 与 CXL 3.0 硬件一致性

- **CXL.cache**：允许设备（加速器）缓存主机内存并参与一致性协议，设备侧维护缓存行状态，通过 Snoop/Invalidate/Data 消息与主机交互 [来源: cxl-chip-industry-deep-dive §1.2]。延迟代价 +50-100ns。
- **CXL 3.0 硬件一致性（HCHC, Hardware Coherent Host Cache）**：把一致性域扩展到多主机 + 交换拓扑，支持 4096 节点内存池的硬件一致性（不再依赖软件目录）[来源: semantics-and-protocol-over §10.2.1]。
- **NVLink 域内一致性**：GPU 间缓存一致性（L2 窥探），域内 ~72 GPU，域间不可跨（物理极限）[来源: semantics-and-protocol-over §2.2.2]。

### 7.4 特征与代价

| 维度 | 数值/说明 | 来源 |
|:-----|:----------|:-----|
| 窥探延迟附加 | +50-100ns（CXL.cache） | [来源: cxl-chip-industry-deep-dive §1.2] |
| 带宽放大 | 一致性协议消息使实际带宽需求 ×1.5-3（失效/确认/重放） | [来源: 领域知识, 一致性协议开销分析] |
| 目录内存开销 | 每缓存行 ~8-16B 目录项（大系统） | [来源: 领域知识] |
| 一致性域规模 | 片内 8-32 核 / 板级 ~256 设备 / 域内 ~72 GPU / Fabric 4096 节点 | [来源: semantics-and-protocol-over §5.1] |
| 操作接口 | 协议消息（Snoop/Invalidate/Data/Unlock），对应用透明 | [来源: 领域知识, CXL 规范] |

**关键洞察**：一致性语义是"最贵"的语义（带宽放大+目录开销+协议复杂度），所以系统设计要按需启用——NVLink 域内强制一致（GPU 共享模型需要），RDMA 跨节点不提供一致（应用自管），CXL.cache 可选（仅加速器需要）。**一致性是语义光谱上的"高保真选项"，不是默认选项**。

---

## 8. 五大语义族全维度对比

### 8.1 对比矩阵

| 维度 | 内存语义 | I/O 语义 | 网络语义(通道) | 网络语义(RDMA) | 存储语义 | 一致性语义 |
|:-----|:--------:|:--------:|:--------------:|:--------------:|:--------:|:----------:|
| **基本操作** | LD/ST | MMIO+DMA | Send/Recv | RDMA R/W/Atomic | NVMe 命令 | Snoop/Inv |
| **寻址模型** | 统一地址 | 寄存器+物理地址 | 消息句柄 | 远端 VA+rkey | LBA/路径/Key | 缓存行标签 |
| **延迟** | ~100-300ns | ~0.5-3μs | ~1-10μs | ~1-5μs | ~5-500μs | +50-100ns |
| **粒度** | 字节(1-64B) | 块(KB-MB) | 消息(可变) | 消息(可变) | 块(4K-1M) | 缓存行(64B) |
| **CPU 参与** | 零(硬件直通) | 启动+中断 | 两端每次 | 仅发起端 | 命令提交+完成 | 协议代理 |
| **一致性** | 可选 | 无 | 无 | 无 | 无 | 强制 |
| **原子操作** | 原生 | ❌ | ❌ | ✅(RNIC) | ❌ | 随协议 |
| **持久性** | 易失 | 易失 | 易失 | 易失 | **持久** | 易失 |
| **距离** | <1m~100m | <15m | 全球 | 数据中心级 | 网络相关 | 一致性域内 |
| **编程模型** | memcpy | DMA 描述符 | Socket/MPI | verbs 单侧 | POSIX/对象 | 透明 |
| **代表性协议** | CXL.mem, NVLink | PCIe, NVMe | TCP, MPI, IB Send | IB/RoCE RDMA | NVMe, NFS, S3 | MESI, CXL.cache |

> 注：延迟与带宽数据综合 [来源: semantics-and-protocol-over §5.1 对比矩阵] 与 [来源: dma-rdma §8.2]。

### 8.2 选型决策树：场景 → 语义

```text
Q1: Must data survive power loss?
  +-- YES -> Storage semantics (NVMe / NFS / S3)
  +-- NO  -> Q2

Q2: Access distance?
  +-- cross-region (>100m)   -> Network-channel semantics (TCP / QUIC)
  +-- within DC (1-100m)     -> Q3
  +-- board / domain (<1m)   -> Q4

Q3: Perf-sensitive and one-sided access?
  +-- YES -> Network-memory semantics (RDMA: gradients / param fetch)
  +-- NO  -> Network-channel (RPC / control) or Storage (data plane)

Q4: Need cache coherence or atomics?
  +-- YES -> Memory-coherent/atomic (CXL.mem, NVLink: shared mem / dist locks)
  +-- NO  -> Raw memory (RDMA R/W) or I/O semantics (PCIe DMA)

Cross-cutting: do many cores/cards share the same data?
  +-- YES -> add Coherence semantics (CXL.cache / directory protocol)
  +-- NO  -> stay incoherent, save bandwidth
```

### 8.3 语义的"不可能三角"

所有语义族共享一个根本约束——**低延迟 × 远距离 × 高保证（一致/持久）三者不可兼得**：

```text
                    LOW LATENCY (~100ns)
                        /\
                       /  \
                      /    \
                     /      \
                    /  IMPOSSIBLE  \
                   /  region:       \
                  /  coherence or    \
                 /  durability needs  \
                /  extra round trips,  \
               /  breaking latency     \
    LONG DISTANCE +--------------------+ HIGH GUARANTEE
    (unlimited)   (physics: lightspeed  (coherent + durable)
                   + protocol overhead)
```

- 内存语义选了"低延迟+高一致"，牺牲距离（<1m 域内）。
- 网络语义选了"远距离+可靠"，牺牲延迟（μs-ms 级）。
- 存储语义选了"持久+可靠"，牺牲延迟（μs-ms 级，介质物理特性）。
- 一致性/持久性都是"额外保证"，每个保证都消耗延迟预算——**这是所有 Over 技术失败或妥协的根因** [来源: semantics-and-protocol-over §10.1.2]。

---

## 9. 语义融合与演进（2026-2030）

### 9.1 网络语义的"内存化"：MemSem over Ethernet

- **ESUN/UEC**：Meta/AMD/BCM 推动用开放以太网承载 GPU 域互联（NVLink 类），但延迟代价 20-50×（~100ns → 2-5μs），只有域间场景可行 [来源: semantics-and-protocol-over §7.1.4]。
- **MemSem over Ethernet**（学术界/产业界探索）：把内存语义（Load/Store 单侧）搬到以太网上，本质是 RDMA 语义的再标准化。
- 判断：**网络语义的内存化方向确定，但延迟墙决定其只能覆盖"域间"而非"域内"**；域内 NVLink/UALink 保持内存语义原生 [来源: semantics-and-protocol-over §10.2.3]。

### 9.2 内存语义的"域扩张"：CXL Fabric / UALink

- **CXL 3.0/3.1 Fabric**：一致性内存语义扩展到 4096 节点池化（KV Cache、内存扩展），~200-500ns [来源: semantics-and-protocol-over §10.2.1]。
- **CXL 4.0**：128GT/s（同步 2026-08-12 Synopsys IP 首发），继续压低内存语义的协议附加延迟 [来源: knowledge/06_others/sources/2026-08-12-synopsys-cxl4-0-128gtps-kv-offload.md]。
- **UALink**：AMD 主导的开放 GPU 域互联，直接对标 NVLink，不依赖 over Eth，域内 16+ GPU @ ~100-150ns [来源: semantics-and-protocol-over §9.2.2]。
- 判断：**内存语义沿"域扩张"路线向右扩展，但不会替代网络语义**（全局扩展仍需消息传递）。

### 9.3 存储语义的"GPU 化"：GPUDirect Storage

- **GPUDirect Storage（GDS）**：数据经 DMA 直达 GPU 显存，绕过主机内存与 CPU——存储语义与内存语义的接口融合 [来源: knowledge/03_AI/train/ai-storage/2026-08-03-ai-storage-application-innovation-three-layer.md]。
- **GPU 原生 I/O**：SCADA/cuFile 让 GPU 直接发起 NVMe 读（GPU-initiated I/O），存储命令语义的发起端从 CPU 变成 GPU [来源: gpu-initiated-io-architecture-scada-cufile-512b.md]。
- **CXL 内存语义存储**：把 CXL 内存当存储介质用（持久内存），存储语义与内存语义合流（DAX/famfs 方案）[来源: knowledge/07_industry-research/03_server/2026-07-28-famfs-cxl-memory-filesystem-deep-analysis.md]。

### 9.4 语义融合的本质：物理层趋同，语义层分化

```text
Physical layer converges: unified optical/electrical PHY
                         (Ethernet PHY / PCIe PHY / CPO optical)
        |
        v
Semantic layer diverges: different semantics stacked on same PHY
                         (network / memory / storage semantics)
        |
        v
Interface layer fuses:   programming interfaces borrow from each other
                         (io_uring borrows verbs polling;
                          cufile borrows memory-semantics zero-copy;
                          CXL borrows RDMA-style pooling)
```

**本质判断**：2026-2030 的语义演进不是"一种语义消灭另一种"，而是**物理层趋同（开放以太网+光互联）+ 语义层按场景分化（域内内存语义、域间网络语义、持久存储语义）+ 接口层融合（借鉴彼此的最佳实践）**。五大语义族将长期共存，各自守住自己的物理约束边界 [来源: semantics-and-protocol-over §10.2.3 三层共存结构]。

---

## 10. 结论

1. **何为语义**：语义 = 接口的行为契约（前置条件/操作效果/后置条件/失败行为），由**物理约束（距离、延迟预算、持久性需求、共享需求）**决定，而非人为发明。语法说"怎么说"，语义说"保证什么"。

2. **五大语义族**（MECE）：
   - **内存语义**：统一地址 + Load/Store 直通，~100-300ns，域内最高性能（CXL.mem/NVLink）；
   - **I/O 语义**：寄存器启动 + DMA 执行 + 中断完成，~0.5-3μs，块级搬运（PCIe/NVMe）；
   - **网络语义**：分**通道语义**（Send/Recv 显式配对）与**内存语义**（RDMA 单侧读写）两类，距离无限（IB/RoCE/TCP）；
   - **存储语义**：持久性保证 + 命令队列模型，三级抽象（块/文件/对象）；
   - **一致性语义**：缓存视图统一，最贵的"高保真选项"，按需启用（MESI/CXL.cache）。

3. **操作接口 = 语义的投影**：三级接口（指令级 L0 / API 级 L1 / 线格式级 L2）逐层映射同一语义契约。选接口 = 选语义 = 选性能与复杂度的平衡点。

4. **演进方向**：物理层趋同 + 语义层分化 + 接口层融合。RDMA 是"内存语义上网络"的先例，CXL 是"网络语义回内存"的反向，GDS/cuFile 是"存储语义进 GPU"的合流——**语义融合的本质是让每种数据搬运需求都能找到物理上最优、接口上最简的表达**。

---

## 参考文献

1. PCI-SIG, *PCI Express Base Specification Rev 6.0*, 2022 — PCIe TLP/MMIO/DMA 语义 [来源: 规范原文]
2. CXL Consortium, *Compute Express Link 3.1 Specification*, 2025 — CXL.io/.mem/.cache 三协议语义 [来源: 规范原文]
3. InfiniBand TA, *InfiniBand Architecture Rev 1.7*, 2024 — 通道语义/内存语义分类、RC/UC/UD/XRC [来源: 规范原文]
4. NVM Express Inc., *NVMe Base Specification 2.0*, 2024 — SQ/CQ 命令队列语义、命令集 [来源: 规范原文]
5. IEEE 802.3, *Ethernet Standards (RoCEv2 承载)*, 2024 — RoCEv2 UDP 封装 [来源: 规范原文]
6. OCP, *ESUN Initiative Whitepaper*, 2025 — 以太网承载 Scale-Up 互联 [来源: 行业白皮书]
7. Ultra Ethernet Consortium, *UEC Requirements Specification*, 2026 — AI 网络语义需求 [来源: 行业白皮书]
8. Ultra Accelerator Link Consortium, *UALink 2.0 Specification*, 2026 — 开放 GPU 域互联语义 [来源: 规范原文]
9. Linux Kernel 文档, *io_uring / SPDK / NVMe-oF 内核模块*, 2026 [来源: 开源文档]
10. knowledge/02_rd/01_product/00_hardware/01_hw-core/2026-06-25-semantics-and-protocol-over.md — 互联语义体系（内存·消息·I/O）与 Over 技术全景
11. knowledge/02_rd/01_product/00_hardware/01_hw-core/2026-06-25-dma-rdma-complete-analysis.md — DMA/RDMA 完整体系
12. knowledge/02_rd/00_shared/01_architecture/2026-07-22-cxl-chip-industry-deep-dive.md — CXL 芯片与三协议语义
13. knowledge/02_rd/01_product/00_hardware/06_storage/2026-07-29-network-storage-protocol-evolution.md — 网络存储协议演进与块/文件/对象语义
14. knowledge/03_AI/train/ai-storage/2026-08-06-gpu-initiated-io-architecture-scada-cufile-512b.md — GPU 发起 I/O 与 cuFile
15. knowledge/07_industry-research/2026-08-19-network-protocol-design-patterns-deep-analysis.md — 网络协议设计模式（同批次，语义设计方法论互补）

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- knowledge/02_rd/01_product/00_hardware/01_hw-core/2026-06-25-semantics-and-protocol-over.md — 互联语义体系（内存·消息·I/O）与 Over 技术全景（主参考）
- knowledge/02_rd/01_product/00_hardware/01_hw-core/2026-06-25-dma-rdma-complete-analysis.md — DMA/RDMA 完整体系（RDMA 语义与 verbs 接口）
- knowledge/02_rd/00_shared/01_architecture/2026-07-22-cxl-chip-industry-deep-dive.md — CXL 芯片与 CXL.io/.mem/.cache 语义
- knowledge/02_rd/01_product/00_hardware/06_storage/2026-07-29-network-storage-protocol-evolution.md — 网络存储协议演进与块/文件/对象语义
- knowledge/03_AI/train/ai-storage/2026-08-06-gpu-initiated-io-architecture-scada-cufile-512b.md — GPU 发起 I/O 与 cuFile（GDS）
- knowledge/07_industry-research/2026-08-19-network-protocol-design-patterns-deep-analysis.md — 网络协议设计模式（同批次互补）
- knowledge/07_industry-research/03_server/2026-07-28-famfs-cxl-memory-filesystem-deep-analysis.md — CXL 内存文件系统（famfs/DAX）
- knowledge/06_others/sources/2026-08-12-synopsys-cxl4-0-128gtps-kv-offload.md — CXL 4.0 128GT/s 与 KV offload

### 外部资料引用

- PCI-SIG, *PCI Express Base Specification Rev 6.0*, 2022 — PCIe TLP/MMIO/DMA 语义
- CXL Consortium, *Compute Express Link 3.1 Specification*, 2025 — CXL 三协议语义
- InfiniBand TA, *InfiniBand Architecture Rev 1.7*, 2024 — 通道语义/内存语义、RC/UC/UD/XRC
- NVM Express Inc., *NVMe Base Specification 2.0*, 2024 — SQ/CQ 命令队列语义
- IEEE 802.3, *Ethernet Standards (RoCEv2 承载)*, 2024 — RoCEv2 UDP 封装
- OCP, *ESUN Initiative Whitepaper*, 2025 / UEC, *UEC Requirements Specification*, 2026
- Ultra Accelerator Link Consortium, *UALink 2.0 Specification*, 2026

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-19 | v1.0 | 首次创建：语义本体论 + 五大语义族分类 + 三级操作接口全景 |
