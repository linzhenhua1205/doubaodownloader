# 🔗 CXL 芯片产业深度调研：协议演进、芯片格局、应用场景与技术进展

> **概要**: CXL（Compute Express Link）芯片产业链全景，覆盖协议架构、交换芯片/控制器芯片厂商、应用场景、学术论文与工业进展
>
> **关键词**: (待补充)

---

## 📑 目录

- [1. CXL 协议架构与演进路线](#1-cxl-协议架构与演进路线)
  - [1.1 协议栈三子协议](#11-协议栈三子协议)
  - [1.2 代际演进：1.0 → 2.0 → 3.0 → 3.1](#12-代际演进10-20-30-31)
  - [1.3 CXL 的物理层基础：PCIe](#13-cxl-的物理层基础pcie)
  - [1.4 CXL 的核心技术挑战](#14-cxl-的核心技术挑战)
- [2. CXL 芯片类型与架构](#2-cxl-芯片类型与架构)
  - [2.1 CXL 控制器（CXL Controller / Host）](#21-cxl-控制器cxl-controller-host)
  - [2.2 CXL 交换芯片（CXL Switch）](#22-cxl-交换芯片cxl-switch)
  - [2.3 CXL 内存控制器（CXL Memory Controller）](#23-cxl-内存控制器cxl-memory-controller)
  - [2.4 CXL Retimer / Redriver](#24-cxl-retimer-redriver)
- [3. CXL 芯片厂商全景](#3-cxl-芯片厂商全景)
  - [3.1 交换芯片厂商](#31-交换芯片厂商)
    - [XConn（xChip）](#xconnxchip)
    - [Broadcom](#broadcom)
    - [Astera Labs](#astera-labs)
    - [Microchip](#microchip)
    - [Rambus](#rambus)
  - [3.2 控制器/Retimer 厂商](#32-控制器retimer-厂商)
    - [澜起科技 (Montage Technology)](#澜起科技-montage-technology)
  - [3.3 CPU/SoC 内置 CXL 支持](#33-cpusoc-内置-cxl-支持)
  - [3.4 厂商定位矩阵](#34-厂商定位矩阵)
- [4. 核心应用场景深度分析](#4-核心应用场景深度分析)
  - [4.1 场景一：内存扩展（Memory Expansion）](#41-场景一内存扩展memory-expansion)
  - [4.2 场景二：内存池化（Memory Pooling）](#42-场景二内存池化memory-pooling)
  - [4.3 场景三：GPU 直连 CXL 内存池](#43-场景三gpu-直连-cxl-内存池)
  - [4.4 场景四：CXL 加速存储（JBOF / Type-C）](#44-场景四cxl-加速存储jbof-type-c)
  - [4.5 场景五：异构计算与加速器互联](#45-场景五异构计算与加速器互联)
  - [4.6 场景六：CXL 在 AI 推理中的杀手场景](#46-场景六cxl-在-ai-推理中的杀手场景)
- [5. 技术论文与学术进展](#5-技术论文与学术进展)
  - [5.1 系统架构类](#51-系统架构类)
    - [Beluga（SIGMOD'26）— CXL 在 AI 推理中最具影响力的论文](#belugasigmod26-cxl-在-ai-推理中最具影响力的论文)
    - [DFabric（USENIX ATC'25）— CXL + 以太网混合架构](#dfabricusenix-atc25-cxl-以太网混合架构)
  - [5.2 性能分析与建模类](#52-性能分析与建模类)
  - [5.3 新型应用类](#53-新型应用类)
- [6. 产业进展与部署现状](#6-产业进展与部署现状)
  - [6.1 2024：CXL 2.0 量产元年](#61-2024cxl-20-量产元年)
  - [6.2 2025：CXL 3.0 芯片上市与池化部署](#62-2025cxl-30-芯片上市与池化部署)
  - [6.3 2026-2027：大规模部署与生态成熟（预测）](#63-2026-2027大规模部署与生态成熟预测)
- [7. 挑战与开放问题](#7-挑战与开放问题)
  - [7.1 延迟墙](#71-延迟墙)
  - [7.2 GPU 侧 CXL 支持不足](#72-gpu-侧-cxl-支持不足)
  - [7.3 一致性与缓存问题](#73-一致性与缓存问题)
  - [7.4 成本悖论](#74-成本悖论)
  - [7.5 软件生态成熟度](#75-软件生态成熟度)
- [8. 总结与展望](#8-总结与展望)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 1. CXL 协议架构与演进路线

### 1.1 协议栈三子协议

CXL 是一个**缓存一致性互联协议**，建立在 PCIe 物理层之上，通过三个子协议提供不同层次的互联语义：

```text
+-------------------------------------------------------+
|                     CXL Protocol Stack                  |
+-------------------------------------------------------+
|  CXL.io    |  CXL.cache  |  CXL.mem                    |
|  (standard IO)|(cache coherence)|  (memory semantics)       |
+------------+-------------+----------------------------+
|                PCIe 6.0/5.0 PHY + Link Layer           |
+-------------------------------------------------------+
|              Electrical / Optical Physical              |
+-------------------------------------------------------+
```

| 子协议 | 功能 | 延迟特征 | 典型场景 | 实现复杂度 |
|:-------|:-----|:--------:|:---------|:---------:|
| **CXL.io** | 标准 PCIe IO 语义，枚举、配置、DMA、中断 | 同 PCIe | 设备发现、控制面通信 | 低（PCIe 兼容） |
| **CXL.cache** | CPU 访问远端设备 Cache，保持一致性 | +50-100ns | CPU↔加速器缓存共享 | 高（一致性协议） |
| **CXL.mem** | CPU/GPU 通过 Load/Store 直接访问远端内存 | +150-300ns | 内存扩展、内存池化、KV Cache | 中（内存映射） |

**关键特点**：

- **CXL.mem 是 CXL 最具颠覆性的子协议**——它使得 Load/Store 语义可以跨越物理边界，程序访问远端内存就像访问本地 DDR5 一样，不需要 RDMA 那样的 send/recv 轮询
- CXL.io 与 PCIe 全兼容，确保现有 PCIe 设备可以无缝接入 CXL 拓扑
- CXL.cache 为加速器提供 CPU 缓存窥探能力，但目前部署较少

### 1.2 代际演进：1.0 → 2.0 → 3.0 → 3.1

| 代际 | 规范发布 | 单链路带宽 (x16) | 延迟增加 | 拓扑支持 | 关键新特性 |
|:----:|:--------:|:---------------:|:--------:|:---------|:----------|
| **1.0/1.1** | 2019/2020 | ~32 GB/s (PCIe 5.0) | +200-300ns | 点对点 | 首个一致性内存语义 |
| **2.0** | 2022 | ~32 GB/s (PCIe 5.0) | +250-350ns | **单层 Switch** | 支持单层交换拓扑，内存池化 |
| **3.0** | 2023 | **~64 GB/s (PCIe 6.0)** | +150-250ns | **多层 Fabric** | 多级交换、端口聚合、双倍带宽 |
| **3.1** | 2024 | ~64 GB/s (PCIe 6.0) | +150-250ns | 多层 Fabric+ | 内存共享、原子操作增强 |
| **4.0** (规划) | 2026+ | ~128 GB/s (PCIe 7.0) | +100-200ns | 大规模 Fabric | 更高带宽、更低延迟 |

**对 CXL 芯片产业的直接影响**：

```text
CXL 1.0/1.1 (2019-2022)    CXL 2.0 (2022-2024)        CXL 3.0/3.1 (2024-2026)
+-----------------+        +-----------------+        +-----------------+
| point-to-point    |        | single-layer Sw   |        | multi-layer Fab   |
| CPU<->CXL mem ext|  ->  | CPU<->CXL Switch |  ->  | GPU<->CXL Fabric |
| CPU built-in    |        | <->mem expansion  |        | <-> multiple servers|
| no switch chip  |        | switch chips appear|        | multi-layer fabric|
+-----------------+        +-----------------+        +-----------------+
  market: small           market: medium          market: large
  chip: Xeon integrated   chip: XConn/Broadcom    chip: full ecosystem
```

### 1.3 CXL 的物理层基础：PCIe

CXL 的战略决策是**基于 PCIe 物理层**运行，而非自建物理层：

| 方面 | CXL 的选择 | 优势 | 代价 |
|:-----|:----------|:-----|:-----|
| 物理层 | PCIe 5.0/6.0 PHY | 复用成熟生态，无需自研 SerDes | 带宽受限于 PCIe 代际 |
| 连接器 | 标准 PCIe 插槽 | 现有背板/线缆兼容 | 物理距离受限（<1m铜缆） |
| 拓扑 | PCIe 树形拓扑扩展 | 继承 PCIe 交换生态 | 树形不如网络拓扑灵活 |

**关键物理约束**：

- **PCIe 5.0 x16**: ~32 GB/s 单向，链路延迟 ~10ns（纯电信号）
- **PCIe 6.0 x16**: ~64 GB/s 单向，引入 **PAM4** 调制和 **FLIT** 编码
- **物理距离**: CXL 基于 PCIe，标准铜缆有效距离 < 1m（PCIe 6.0 甚至 < 0.5m）
- **光扩展**: CXL over Optical 正在标准化，目标将距离扩展至 10-100m

### 1.4 CXL 的核心技术挑战

| 挑战 | 技术描述 | 对芯片设计的影响 |
|:-----|:---------|:----------------|
| **延迟墙** | CXL Switch 每增加一级，额外增加 50-150ns 延迟 | 交换芯片必须极简转发，减少 buffering |
| **一致性扩散** | 多 host 访问同一 CXL 内存时的一致性问题 | CXL 3.1 引入内存共享 (Shared Memory) 协议 |
| **带宽适配** | CXL 带宽远低于 HBM，远高于 NVMe | 需要智能预取和缓存管理 |
| **热插拔** | CXL 内存支持热插拔，需处理内存状态保存/恢复 | 控制器需要支持 graceful shutdown |
| **安全隔离** | 多租户共享 CXL 内存池时的数据隔离 | CXL 3.0 引入 SPDM/IDE 安全协议 |

---

## 2. CXL 芯片类型与架构

### 2.1 CXL 控制器（CXL Controller / Host）

CXL 控制器是**嵌入在 CPU/SoC 中的 CXL 协议处理模块**，负责将内存访问请求封装为 CXL 协议报文并通过 PCIe 链路发送。

**架构示意**：

```text
CPU Core
   |
   |-- L1/L2/L3 Cache
   |
   |-- Memory Controller (iMC)
   |    +-- DDR5 channels (local mem)
   |
   +-- CXL Controller (in PCIe RC)
        |   +-- CXL.io: config, DMA, interrupts
        |   +-- CXL.mem: Load/Store -> CXL protocol
        |   |  +-- addr decode: check CXL address range
        |   |  +-- protocol xlate: internal bus -> CXL.mem
        |   |  +-- transaction queue: ordering, flow ctrl
        +-- CXL.cache: device cache snoop
```

**关键设计参数**：

| 参数 | Xeon 6 (Granite Rapids) | AMD EPYC Turin | NVIDIA Grace |
|:-----|:------------------------|:---------------|:-------------|
| CXL 版本 | 2.0 (快速路径) | 2.0 | 3.0 |
| 通道数 | 2×CXL 2.0 x16 | 2×CXL 2.0 x16 | 4×CXL 3.0 x16 |
| 总带宽 | ~64 GB/s | ~64 GB/s | ~256 GB/s |
| 支持的 CXL 类型 | Type 1/2/3 | Type 1/2/3 | Type 2/3 |
| 延迟增加 | +200-300ns | +200-300ns | +150-250ns |

### 2.2 CXL 交换芯片（CXL Switch）

CXL Switch 是 CXL 2.0+ 的核心组件，本质上是**具备 CXL 协议感知能力的 PCIe 交换机**。

**与传统 PCIe Switch 的差异**：

| 维度 | 普通 PCIe Switch | CXL Switch | 差异根因 |
|:-----|:----------------|:-----------|:---------|
| 转发粒度 | TLP (Transaction Layer Packet) | **FLIT (Flow Control Unit)** 或更细粒度 | 延迟敏感 |
| 缓存一致性 | 无感知 | CXL.mem **地址解码 + 一致性跟踪** | 内存语义支持 |
| 多播支持 | 无 | **CXL 多播/广播**（用于一致性 snoop） | 一致性协议 |
| QoS | 粗粒度 (端口级) | **细粒度 (流级)** | 内存访问优先级关键 |
| 拓扑 | 单根树形 | **多根 Fabric**（CXL 3.0+） | 多 host 共享池 |

**CXL Switch 的内部架构**：

```text
                     +----------------------+
                     |   CXL Switch ASIC    |
                     |                      |
  Upstream Port 0 ---|  +----------------+  |--- Downstream Port 0
  (Host/GPU)         |  |  Crossbar      |  |   (Mem/Device)
                     |  |  (Non-blocking |  |
  Upstream Port 1 ---+  |   full-mesh)   |  +--- Downstream Port 1
  (Host/GPU)         |  |                |  |   (Mem/Device)
|  +----------------+  |
|  +----------------+  |
|  |  CXL Protocol  |  |
|  |  Engine        |  |
|  |  - addr decode |  |
|  |  - coherence   |  |
|  |  - QoS/sched   |  |
|  +----------------+  |
|  +----------------+  |
|  |  Management   |  |
|  |  - config/mgmt|  |
|  |  - telemetry  |  |
|  |  - security   |  |
|  +----------------+  |
                     +----------------------+
```

**CXL Switch 的技术难点**：

1. **延迟控制**: 每级 Switch 增加 50-150ns，多层 Fabric 下延迟累积显著。必须用极简转发设计、直通式（cut-through）交换、减少内部 buffer
2. **一致性域管理**: 多 host 共享内存时，CXL Switch 需要跟踪哪些 host 缓存了哪些内存区域，在写入时发送 snoop 请求
3. **QoS 与隔离**: 多租户共享时，需要按流/按端口做带宽保障和优先级调度
4. **物理层复杂度**: PCIe 6.0 PAM4 + FLIT 编码对 SerDes 设计要求极高，功耗约 10-15pJ/bit

### 2.3 CXL 内存控制器（CXL Memory Controller）

CXL 内存控制器位于 **CXL 内存扩展卡 / CXL 内存节点** 上，负责将 CXL.mem 请求转换为 DDR5 内存访问。

**架构示意**：

```text
             CXL.mem Request In
                    |
              +-----+-----+
              | CXL.mem   | <- CXL protocol decode
              | Protocol   |
              | Decode     |
              +-----+-----+
                    |
              +-----+-----+
              | Address   | <- CXL addr -> DDR5 addr map
              | Translate |    (HPA <-> DPA)
              +-----+-----+
                    |
              +-----+-----+
              | DDR5      | <- DDR5 memory controller
              | Controller|    timing, ECC, refresh
              +-----+-----+
                    |
              +-----+-----+
              | DDR5 DIMMs| <- physical memory
              | (1-8 ch)  |
              +-----------+
```

| 参数 | 典型 CXL 内存扩展卡 |
|:-----|:-------------------|
| 内存类型 | DDR5-4800 ~ DDR5-6400 |
| 容量 | 256 GB ~ 2 TB（单卡） |
| 通道数 | 4-8 通道 |
| 带宽 | ~30-60 GB/s (x8/x16 CXL) |
| 延迟 | 本地 DDR5 + 200-300ns CXL 开销 |

### 2.4 CXL Retimer / Redriver

CXL 基于 PCIe 物理层，PCIe 5.0/6.0 的**信号完整性挑战**（>32 GT/s）决定了中长距离传输需要 Retimer 芯片。

| 器件 | 功能 | PCIe 5.0 (32GT/s) | PCIe 6.0 (64GT/s) |
|:-----|:-----|:------------------:|:------------------:|
| **Redriver** | 信号幅度恢复（无时钟恢复） | 有效距离 ~8-12" PCB | 基本无效 |
| **Retimer** | 信号+时钟恢复（CDR + EQ） | 有效距离 ~12-20" PCB | 每 6-8" 需一颗 |

**对 CXL 部署的实际影响**：

- 标准服务器内 CXL 连接距离 < 12"，通常不需要 Retimer
- 跨机柜 CXL（CXL over Optical）需要 Retimer 或光模块
- 每颗 Retimer 增加 ~5-10ns 额外延迟

---

## 3. CXL 芯片厂商全景

### 3.1 交换芯片厂商

#### XConn（xChip）

| 项目 | 详情 |
|:-----|:------|
| **总部** | 以色列，2021 年成立 |
| **旗舰产品** | XC50256（CXL 2.0 Switch） |
| **接口** | 256 lanes PCIe 5.0，最多 64 端口 |
| **交换容量** | 2 TB/s（双向） |
| **连接能力** | 最多 16 台服务器 + 内存池 |
| **CXL 支持** | CXL 2.0 Type 1/2/3 |
| **量产时间** | 2024 H2 量产 |
| **已公布客户** | 阿里云（Beluga 系统）、多家超大规模 CSP |
| **下一代** | XC3xxxx（CXL 3.0，预计 2026） |

**XC50256 技术参数**：

| 参数 | 值 |
|:-----|:---|
| 端口数 | 最多 64 × PCIe 5.0 x4 / 32 × PCIe 5.0 x8 / 16 × PCIe 5.0 x16 |
| 功耗 | ~25W（典型，16 × x16 配置） |
| 延迟 | ~80ns（直通模式，cut-through） |
| 封装 | 45mm × 45mm BGA |
| 安全 | SPDM + IDE Support |

**市场定位**：XConn 是**目前唯一大规模量产的独立 CXL Switch 芯片**，在 CXL 2.0 交换市场中占据主导地位。其核心竞争力是第一款走向市场的独立 CXL 交换机，获得了阿里云等头部客户的背书。

#### Broadcom

| 项目 | 详情 |
|:-----|:------|
| **产品线** | PEX98000 系列（PCIe 5.0 Switch，支持 CXL 2.0） |
| **产品线** | PEX99000 系列（PCIe 6.0 Switch，原生 CXL 3.0） |
| **市场地位** | PCIe Switch 市场绝对领导者（>60% 份额） |
| **差异化** | 从 PCIe Switch 升级到 CXL Switch，软件兼容 |
| **CXL 支持** | PEX98000: CXL 2.0 | PEX99000: CXL 3.0（2025 采样） |
| **典型产品** | PEX89000 (48 lanes / 96 lanes / 144 lanes) |

**Broadcom 的战略**：不单独做"纯 CXL Switch"，而是在其成熟的 PCIe Switch 产品线中**增量支持 CXL 协议**。这样做的优势是：

- 复用 PCIe Switch 庞大的出货量摊薄芯片成本
- 已在绝大多数服务器 OEM 的设计中占位
- 客户可以无缝从 PCIe Switch 升级到 CXL Switch

#### Astera Labs

| 项目 | 详情 |
|:-----|:------|
| **总部** | 美国，2017 年成立，2023 年上市 |
| **核心产品** | Leo CXL 内存控制器 + 智能内存扩展卡 |
| **交换芯片** | **Leo CXL Switch**（CXL 3.0，2025 发布） |
| **其他产品线** | Ares Retimer、Taurus 智能电缆模块 |
| **CXL 差异化** | Fabric Manager 软件栈 + 端到端 CXL 平台方案 |
| **市场定位** | 从 Retimer 起家，逐步扩展到 CXL 交换和内存控制器 |

**Astera Labs 的独特价值**：

Astera Labs 不只是卖芯片，而是提供**完整的 CXL 平台解决方案**：

```text
Astera Labs CXL Platform:
+------------------------------------------+
|  Software Stack: Cloud Fabric Manager   |
|  - topology discovery, config, health, hotplug  |
+------------------------------------------+
|  Leo CXL Controller (memory-side)       |
|  - CXL protocol controller on memory card   |
|  - ECC, RAS, remote error reporting          |
+------------------------------------------+
|  Leo CXL Switch (fabric)                |
|  - CXL 3.0 multi-port switch            |
|  - deep integration w/ Leo Ctrl         |
+------------------------------------------+
|  Ares Retimer (PHY layer)               |
|  - PCIe 5.0/6.0 signal recovery         |
|  - interacts w/ Leo chip                |
+------------------------------------------+
```

#### Microchip

| 项目 | 详情 |
|:-----|:------|
| **产品** | Switchtec 系列 PCIe 交换（支持 CXL 2.0） |
| **特点** | 强大的可编程性、高级 RAS 功能 |
| **市场** | 存储和企业级应用为主 |
| **CXL 3.0** | 开发中，预计 2026+ |

#### Rambus

| 项目 | 详情 |
|:-----|:------|
| **产品** | CXL 内存控制器 IP（非独立芯片） |
| **模式** | IP 授权给芯片设计公司 |
| **CXL 3.0** | 已推出 CXL 3.0 内存控制器 IP |
| **差异化** | 与 HBM3/4 控制器 IP 组合提供全栈方案 |

### 3.2 控制器/Retimer 厂商

| 公司 | 主要产品 | 核心定位 | 客户类型 |
|:-----|:---------|:---------|:---------|
| **Astera Labs** | Leo CXL Memory Controller | 内存扩展卡核心芯片 | 服务器 OEM、云厂商 |
| **Montage Technology (澜起科技)** | MXC (CXL Memory Controller) | 国产 CXL 内存控制器 | 国产服务器厂商 |
| **Rambus** | CXL Memory Controller IP | IP 授权 | 芯片设计公司 |
| **Astera Labs** | Ares Retimer | PCIe 5.0/6.0 Retimer | 服务器 OEM |
| **Parade Technologies (谱瑞)** | PS-series Retimer | DisplayPort / PCIe Retimer | PC / 服务器 |
| **TI** | PCIe Retimer | 通用 PCIe 信号调整 | 嵌入式 / 通信 |

#### 澜起科技 (Montage Technology)

澜起科技的 **MXC (Memory eXpansion Controller)** 系列是国产 CXL 内存控制器的代表：

| 参数 | MXC 一代 | MXC 二代 |
|:-----|:---------|:---------|
| CXL 版本 | 2.0 | 3.0 (开发中) |
| 接口 | PCIe 5.0 x8 | PCIe 6.0 x16 |
| 内存 | DDR5-4800, 4通道 | DDR5-6400, 8通道 |
| 容量 | 最大 512 GB | 最大 2 TB |
| 延迟增加 | +250-350ns | +200-300ns |
| 量产 | 2024 H1 | 2026 (预期) |

### 3.3 CPU/SoC 内置 CXL 支持

**CXL 的最终普及依赖 CPU 原生支持**——如果 CPU 不支持 CXL 控制器，CXL 生态就无法落地：

| CPU 平台 | CXL 版本 | CXL 通道 | 量产时间 | 地位 |
|:---------|:--------:|:--------:|:--------:|:----|
| **Intel Xeon 6** (Granite Rapids) | CXL 2.0 | 2×x16 | 2024 Q3 | **主要推动者** |
| **Intel Xeon 7** (Diamond Rapids) | CXL 3.0 | 4×x16 | 2026 (规划) | 下一代 |
| **AMD EPYC Turin** | CXL 2.0 | 2×x16 | 2024 H2 | 追赶者 |
| **AMD EPYC Venice** | CXL 3.0 | 4×x16 | 2026 (规划) | 下一代 |
| **NVIDIA Grace** | **CXL 3.0** | 4×x16 | 2024 (有限) | 特殊：ARM 生态 |
| **AmpereOne** | CXL 2.0 | 2×x8 | 2024 | ARM 服务器 |
| **华为鲲鹏 920** | CXL-like (自有) | — | 在产 | 自有协议 |
| **平头哥 倚天 710** | 不支持 CXL | — | 在产 | 基于 ARM Neoverse |

> **关键洞察**：截至 2026 年，Intel 是 CXL 生态的最主要推动者。AMD 支持较晚，NVIDIA 仅 Grace 支持 CXL（且出货量极小）。**没有足够的 CPU 侧 CXL 主机支持，CXL 的普及就受限于 Intel 平台。**

### 3.4 厂商定位矩阵

```text
                    CXL Product Breadth
                    Low  <--------->  High
                    +-------------------------+
              High  |  Broadcom       |  Astera Labs   |
                    |  (HW Giant)     |  (Full Stack)   |
     Market        +-------------------+----------------+
     Influence     |  Microchip        |  XConn         |
              Low  |  (Storage)        |  (Sw Pioneer)   |
                    +-------------------+----------------+
                    |  Rambus          |  Montage Tech   |
                    |  (IP licensing)  |  (China Ctrl)   |
                    +-------------------------+
                     Chip Market Influence
                    Low  <--------->  High
```

---

## 4. 核心应用场景深度分析

### 4.1 场景一：内存扩展（Memory Expansion）

**定位**：CXL 最早落地、最成熟的场景。单台服务器通过 CXL 连接内存扩展卡，增加容量而不增 DIMM 插槽。

**解决的问题**：

- CPU 内存通道数有限（Xeon 6 最大 12 通道 DDR5）
- 高密度服务器需要大内存但物理空间受限
- 某些工作负载需要 TB 级内存但不需要多台服务器

**硬件拓扑**：

```text
+---------------+     CXL 2.0 x16     +-----------------+
|   Xeon 6      |---------------------|  CXL Mem Card   |
|   (Host CPU)  |                     |  Astera Leo     |
|               |                     |  or Montage MXC |
|   DDR5 x12    |                     |  DDR5 x4~8      |
|   (local mem)  |                     |  256GB ~ 2TB    |
+---------------+                     +-----------------+
```

**性能数据**（基于 Astera Labs Leo + DDR5-4800 实测）：

| 指标 | 本地 DDR5 | CXL 内存扩展 | 比例 |
|:-----|:---------:|:-----------:|:----:|
| 延迟 (随机读) | ~90ns | ~280-350ns | +200-290% |
| 带宽 (顺序读) | ~350 GB/s (12ch) | ~32 GB/s (x16) | ~9% |
| 带宽 (顺序写) | ~300 GB/s (12ch) | ~28 GB/s (x16) | ~9% |
| 每 GB 成本 | ~$8-12 | ~$8-12（同 DDR5） | 相同 |
| 总容量上限 | 2 TB (12×16GB) | 4 TB (本地+CXL) | +100% |

**适用工作负载**：

- **内存数据库**（Redis/SAP HANA）：容量优先，延迟增加可接受
- **EDA/芯片验证**：需要数百 GB 内存跑仿真
- **科学计算**：大矩阵运算的场景
- **虚拟化**：更多 VM 的内存密度提升

**芯片需求**：CXL 内存控制器（Astera Leo / 澜起 MXC）+ CPU 内置 CXL 控制器

### 4.2 场景二：内存池化（Memory Pooling）

**定位**：CXL 2.0+ 的核心场景。多台服务器通过 CXL Switch 共享同一组物理内存，实现内存的**分时复用和超分配**。

**解决的问题**：

- 数据中心内存利用率仅 40-60%，大量内存闲置浪费
- 每台服务器独立购买内存导致成本高、粒度固定
- 突发流量无法跨服务器借用内存

**硬件拓扑**：

```text
                    +---------------------+
                    |   CXL Memory Pool   |
                    |   DDR5 x N (~8 TB)  |
                    +----------+-----------+
                               | CXL 2.0 x16
                    +----------+-----------+
                    |  CXL Switch         |
                    |  XConn XC50256 /    |
                    |  Broadcom PEX98K   |
                    +--+---+---+---+-----+
                       |   |   |   |  CXL 2.0 x16
              +--------+   |   |   +--------+
              |            |   |             |
        +-----+   +------+   +------+
        |Server 1 |  |Server 2   |  |Server N  |
        |Xeon 6   |  |Xeon 6     |  |Xeon 6    |
        |8xGPU    |  |8xGPU      |  |8xGPU     |
        +---------+  +-----------+  +----------+
```

**内存池化的三种内存分配策略**：

| 策略 | 描述 | 优势 | 劣势 | 典型场景 |
|:-----|:-----|:-----|:-----|:---------|
| **静态分区** | 每台服务器固定分配一段 CXL 内存 | 隔离性好，无竞争 | 灵活性低 | 生产环境 KV Cache |
| **动态分配** | 按需从池中申请/释放 | 利用率高 | 碎片、延迟不可预测 | 开发测试集群 |
| **超分配** | 分配承诺 > 物理容量，利用统计复用 | 极致利用率 | OOM 风险 | 内存敏感型 |

**部署现状**：

| 部署方 | 芯片 | 池大小 | 服务器数量 | 状态 |
|:-------|:-----|:------:|:----------:|:----|
| 阿里云 Beluga | XConn XC50256 | 8 TB | 16 | ✅ SIGMOD'26 论文，生产级 |
| Intel Crescent Island | XConn / Broadcom | 4-16 TB | 4-16 | ✅ 参考设计，向客户推广 |
| 某大型 CSP（未披露） | Astera Leo 全栈 | 8 TB+ | 8+ | ⚠️ 2025 内部部署 |

### 4.3 场景三：GPU 直连 CXL 内存池

**定位**：CXL 最具革命性的场景。GPU 通过 CXL.mem 协议直接访问远端大容量内存池，**无需 CPU 中转、无需 RDMA 拷贝**。

**解决的问题**：

- GPU HBM 容量有限（80-192 GB）
- 训练大模型时模型参数、优化器状态、KV Cache 无法全部放入 HBM
- 传统 CPU DRAM 卸载方案需要 cudaMemcpy + 同步开销

**GPU 访问 CXL 的数据路径对比**：

```text
RDMA approach (MoonCake/Dynamo):
  GPU HBM -> CPU DRAM (bounce) -> NIC -> RDMA -> remote mem -> NIC -> CPU DRAM -> GPU HBM
  latency: ~5-10us

CXL approach (Beluga):
  GPU HBM -> CXL Switch -> CXL pool mem
  latency: ~1-3us (measured)
```

**实际性能数据（阿里云 Beluga 论文，基于 H20 GPU + XConn Switch）**：

| 操作 | RDMA (16KB) | CXL (Beluga) | 改善 |
|:-----|:-----------:|:------------:|:----:|
| 数据移动 | 2.68μs | 2.15μs | -20% |
| 同步开销 | **~8μs** (占 75%) | **~0.5μs** | -94% |
| 总延迟 (16KB Read) | ~10.7μs | **~2.7μs** | **-75%** |

**对芯片的需求**：

1. **GPU 侧 CXL 支持**：NVIDIA 当前仅 Grace Hopper/Superchip 支持 CXL 3.0。普通 GPU（H100/B200）需要通过 PCIe 间接访问，增加了延迟
2. **CXL 3.0 Switch**：3.0 才能提供足够的带宽（x16 → 64 GB/s vs 2.0 的 32 GB/s）
3. **QoS 保证**：GPU 对内存带宽的饥渴需要 CXL Switch 提供流级别的带宽保障

### 4.4 场景四：CXL 加速存储（JBOF / Type-C）

**定位**：Intel 提出的 **JBOF (Just a Bunch of Flash)** 概念——将 NVMe SSD 通过 CXL 接口暴露为主机内存层级的一部分。

**解决的问题**：

- NVMe SSD 延迟（~10-30μs）仍然远高于 DRAM（~100ns）
- CXL 内存价格高昂（~$8-12/GB vs SSD ~$0.10/GB）
- 需要一个**介于内存和 SSD 之间的存储层级**

**JBOF 的存储层级位置**：

```text
                latency         capacity        $/GB
HBM:            ~50ns          ~80GB       ~$80/GB
DDR5 (local):    ~90ns        ~2TB          ~$8/GB
CXL mem pool:   ~300ns       ~16TB         ~$8/GB
---------------  JBOF (CXL SSD) -----------------
CXL JBOF:        ~5-8us      ~64-256TB     ~$0.15/GB
------------  Traditional Storage  -----------
Local NVMe:     ~10-30us     ~32TB         ~$0.10/GB
Remote storage: ~50-200us     inf           ~$0.05/GB
```

**JBOF 的芯片架构**：

```text
                 CXL 3.0 x16 (64 GB/s)
                      |
                +-----+-----+
                | CXL Ctrl  | <- Intel GNR-D / dedicated CXL Ctrl
                | (GMM)     |    CXL.mem protocol term
                +-----+-----+
                      |
                +-----+-----+
                | PCIe 5.0  | <- Broadcom PEX89K
                | Switch    |
                +--+--+--+--+
                   |  |  |
              +----+  |  +----+
              |       |       |
           +--+  +--+  +--+
           |NVMe | |NVMe | |NVMe |
           |SSD  | |SSD  | |SSD  |
           +-----+ +-----+ +-----+
```

**关键芯片**：

- **CXL 控制器**：Intel GNR-D（Granite Rapids-D），集成 CXL 3.0 控制器 + DSA 加速器，专门为 JBOF 设计
- **IAA 加速器**：Intel In-memory Analytics Accelerator，做 KV Cache 在线压缩/解压
- **PCIe Switch**：Broadcom PEX89000 系列

### 4.5 场景五：异构计算与加速器互联

**定位**：CXL 作为**开放标准的内存语义互联**，连接 CPU、GPU、NPU、FPGA 等异构加速器。

**解决的问题**：

- NVIDIA NVLink 是封闭的，其他加速器无法接入
- PCIe 是消息语义（send/recv），不适合细粒度内存共享
- 多厂商异构场景需要统一的内存一致性协议

**ScalePool（arXiv:2510.14580）提出的架构**：

```text
+-----------------------------------------------------+
|              XLink + CXL Hybrid Fabric               |
|                                                      |
|  intra-group: XLink (direct, low latency)|
|  inter-group: CXL 3.0 Fabric (coherent)  |
|                                                      |
|  Tier 1: latency-critical = local + CXL coherence|
|  Tier 2: capacity = dedicated CXL nodes + pooling|
+-----------------------------------------------------+
```

**芯片需求**：

- **多端口 CXL 3.0 Switch**：支持 16+ 端口，连接 CPU + GPU + NPU + 内存节点
- **CXL 多类型支持**：同时支持 Type 1（加速器）、Type 2（带缓存的加速器）、Type 3（内存设备）
- **QoS 差异化**：不同加速器的内存访问优先级不同

### 4.6 场景六：CXL 在 AI 推理中的杀手场景

**CXL 最确定、最刚性的杀手场景是 LLM 推理的 KV Cache 池化。**

**为什么这个场景'杀手'**：

| 维度 | 说明 |
|:-----|:------|
| **需求刚性** | 长上下文（128K~1M+）使 KV Cache 体积指数增长，HBM 无论如何不够 |
| **成本合理** | CXL 内存 ($8-12/GB) 远低于 HBM (~$80/GB)，且每个推理服务器都需要 |
| **性能可接受** | KV Cache 访问模式为顺序读（Prefill）+ 全量读（Decode），CXL 延迟增加对 TTFT 影响可接受 |
| **部署简单** | 只需在现有推理服务器上加 CXL 扩展卡，无需修改模型代码 |

**Beluga 论文的关键性能数据**（SIGMOD'26）：

| 指标 | RDMA 方案 | Beluga (CXL) | 改善 |
|:-----|:---------:|:------------:|:----:|
| TTFT (Time-To-First-Token) | 基准 | **↓ 89.6%** | 近 10 倍提升 |
| 推理吞吐 (vLLM) | 基准 | **↑ 7.35x** | 超过 7 倍提升 |
| CPU 占用率 | 高（轮询） | 低（Load/Store） | 大幅降低 |
| 编程复杂度 | 高（RDMA API） | 低（mmap + Load/Store） | 透明 |

---

## 5. 技术论文与学术进展

> 交叉链接: [Beluga CXL 内存池架构](../01_product/00_hardware/01_hw-core/2026-06-26-alibaba-beluga.md) | [CXL KV Cache Pooling](../02_project/01_superpod/architecture/2026-07-29-intel-cxl-pooling-dup1.md) | [高速互联全景](../01_product/00_hardware/04_si-signal/2026-07-29-high-speed-interconnect-deep-dive.md)

### 5.1 系统架构类

| 论文 | 来源 | 年份 | 核心贡献 | 对芯片的影响 |
|:-----|:-----|:----:|:---------|:------------|
| **Beluga** | **SIGMOD'26** | 2025 | GPU 通过 CXL Switch 直连内存池；89.6% TTFT 降低、7.35x 吞吐提升 | 验证了 CXL Switch 在 AI 推理中的价值 |
| **DFabric** | **USENIX ATC'25** | 2024 | CXL-Ethernet 双层互联架构；机柜内 CXL Fabric + 机柜间 NIC Pool | 推动 CXL + 以太网混合架构芯片 |
| **ScalePool** | arXiv | 2025 | XLink-CXL 混合 Fabric 用于异构加速器集群 | 推动多协议统一 Switch 芯片 |
| **Distributed Persistence Domain (DPD)** | arXiv | 2026 | 分布式持久性 CXL Switch 架构；带持久性支持的 Switch 设计 | 推动带持久性功能的 CXL Switch |
| **Persistent CXL Switch** | arXiv | 2026 | 在 CXL Switch 中集成持久性，平均加速 33%，读转发加速 36% | 下一世代 Switch 芯片功能方向 |

#### Beluga（SIGMOD'26）— CXL 在 AI 推理中最具影响力的论文

**系统架构**：

- 使用 **XConn XC50256** CXL 2.0 Switch
- 连接 16 台服务器（每台 8×H20 GPU + 2×Xeon 6）
- 共享 8 TB DDR5 内存池（32条 DDR5 4800）
- GPU 通过 **cudaMemcpy P2P** 访问 CXL 内存池

**关键发现**：

1. **同步开销主导延迟**：RDMA 方案中 75% 时间是同步开销，CXL 消除了这一瓶颈
2. **带宽不是问题**：虽然 CXL 2.0 x16 仅 32 GB/s，但推理场景中 KV Cache 访问模式对带宽需求适中
3. **软件透明性**：对 vLLM/SGLang 的修改极小，mmap 映射即可

#### DFabric（USENIX ATC'25）— CXL + 以太网混合架构

**核心思想**：

```text
+------------- Rack 1 -----------------+
|  CXL Fabric (intra-rack)              |
|  +----+ +----+ +----+ +----+   |
|  |GPU | |GPU | |GPU | |GPU |   |
|  +----+ +----+ +----+ +----+   |
|       +--------------+         |
|       | NIC Pool     |         |
|       | (CXL decoupled NIC)|      |
|       +------+-------+         |
+--------------+-----------------+
               | Ethernet
+--------------+-----------------+
|  Rack 2 ...  |                 |
+--------------+-----------------+
```

**对芯片的启示**：

- NIC Pool 需要 CXL Switch 解耦网卡，对交换机端口密度要求更高
- CXL + 以太网的双层互联需要 **CXL 交换机具备 NIC 虚拟化功能**

### 5.2 性能分析与建模类

| 论文 | 来源 | 年份 | 核心贡献 |
|:-----|:-----|:----:|:---------|
| **Heimdall** | arXiv | 2024 | 异构缓存一致性系统性能基准套件；对比 CXL / NVLink-C2C / Infinity Fabric |

**Heimdall 的关键发现**：

| 互联方案 | 实测延迟 (CPU→远端内存) | 带宽 (x16) | 一致性模型 |
|:---------|:----------------------:|:---------:|:----------|
| CXL 2.0 (Xeon 6 + Astera Leo) | ~280ns 读, ~350ns 写 | ~32 GB/s | 完全一致性 |
| NVLink-C2C (Grace Hopper) | **~150ns** | **~256 GB/s** | 完全一致性 |
| AMD Infinity Fabric (MI300A) | ~200ns | ~128 GB/s | 完全一致性 |

**关键洞察**：NVIDIA NVLink-C2C 在延迟和带宽上都显著优于当前 CXL 实现，但它是私有的。CXL 的优势在于开放性和生态深度。

### 5.3 新型应用类

| 论文 | 来源 | 年份 | 核心贡献 |
|:-----|:-----|:----:|:---------|
| **DRAM Cache Prefetch for Pooled Memory** | MEMSYS'24 | 2024 | 利用本地 DRAM 做 CXL 远端内存的预取缓存；7% IPC 提升 |
| **Disaggregation-Native Data Streaming** | HCDS'24 | 2024 | 设备直连数据流，无需 CPU 中转；适用于 CXL 设备间通信 |

---

## 6. 产业进展与部署现状

### 6.1 2024：CXL 2.0 量产元年

| 事件 | 公司 | 影响 |
|:-----|:-----|:-----|
| XC50256 量产 | XConn | 首个独立 CXL Switch 走向市场 |
| Leo CXL 控制器量产 | Astera Labs | 首个"全栈"CXL 平台（Ctrl+Switch+SW） |
| Xeon 6 量产 | Intel | CPU 原生 CXL 2.0 支持，是 CXL 生态的关键推动力 |
| 澜起 MXC 量产 | 澜起科技 | 国产 CXL 内存控制器量产 |
| PEX98000 系列 | Broadcom | PCIe 5.0 Switch + CXL 2.0 可选 |
| Broadcom/VMware CXL 方案 | Broadcom | CXL 内存池化 + vSphere 集成 |

### 6.2 2025：CXL 3.0 芯片上市与池化部署

| 事件 | 公司 | 影响 |
|:-----|:-----|:-----|
| CXL 3.0 Switch 采样 | XConn / Broadcom | 带宽翻倍至 64 GB/s/链路 |
| Beluga 生产部署 | 阿里云 | 学术界→工业界的 CXL 成功案例 |
| 大型 CSP 内部部署 | 多家云厂商 | 内存池化进入生产验证阶段 |
| CXL 3.1 规范发布 | CXL Consortium | 内存共享 + 增强原子操作 |
| Astera Leo 3.0 发布 | Astera Labs | CXL 3.0 全栈方案 |
| CXL JBOF 参考设计 | Intel | CXL 加速存储概念验证 |

### 6.3 2026-2027：大规模部署与生态成熟（预测）

| 事件 | 预期时间 | 前置条件 |
|:-----|:--------|:---------|
| **CXL 3.0 大规模部署** | 2026 H2 | Xeon 7/Diamond Rapids + CXL 3.0 Switch 量产 |
| **GPU 原生 CXL 3.0 支持** | 2026-2027 | NVIDIA 或 AMD 下一代 GPU 增加 CXL 端口 |
| **CXL over Optical 标准化** | 2026 | OCP CXL 光互联规范完成 |
| **CXL 4.0 (PCIe 7.0) 规范** | 2027 | 128 GB/s/链路 |
| **CXL 成为服务器标配** | 2027+ | 主流 CPU 和芯片组全面支持 |

---

## 7. 挑战与开放问题

### 7.1 延迟墙

即使使用 CXL 3.0，每级 Switch 增加 50-150ns 延迟。三层 CXL Fabric 的延迟累积可达 300-500ns，这显著慢于本地 DDR5（~90ns）。

**对芯片的影响**：CXL Switch 需要进一步优化 cut-through 转发，减少内部 buffer 深度，甚至探索**光 CXL Switch** 降低物理层延迟。

### 7.2 GPU 侧 CXL 支持不足

当前主流 GPU（H100/B200）**不支持原生 CXL**。GPU 通过 PCIe 访问 CXL 内存时，需要经过：

1. GPU → PCIe → CPU Root Complex → CXL 控制器 → CXL Switch → 远端内存
2. 这增加了数百 ns 的额外延迟

**解决方向**：NVIDIA/AMD 下一代 GPU 原生集成 CXL 端口，或者通过 CXL over PCIe 优化路径。

### 7.3 一致性与缓存问题

当多个 Host 共享同一块 CXL 内存时，**缓存一致性管理**成为复杂问题：

| 场景 | 问题 | 解决方案 |
|:-----|:-----|:---------|
| 多 CPU 读同一 CXL 区域 | 每个 CPU 本地缓存可能过期 | CXL 3.1 Shared Memory 协议 |
| GPU cache + CXL 内存 | GPU cache 不在 CXL 一致性域内 | GPU 需支持 CXL.cache |
| 写后读一致性 | 一个 Host 写入，另一 Host 需要立即可见 | 需要 Switch 广播/多播 |

### 7.4 成本悖论

CXL 内存使用的仍然是 **DDR5 DIMM**，其每 GB 成本与本地 DDR5 相同。CXL 的节省来自于：

- 池化后更高的利用率（40-60% → 80-90%）
- 按需分配，避免过度配置
- 但需要额外购买 CXL Switch 和控制器芯片

**典型成本分析（单机柜 16 台服务器 + 8 TB CXL 池）**：

| 组件 | 成本 | 占比 |
|:-----|:----:|:----:|
| CXL Switch (XConn XC50256) | ~$5,800 | ~10% |
| 16× CXL 适配卡 | ~$3,360 (16×$210) | ~6% |
| 32× DDR5 DIMM (8TB) | ~$64,000 | ~84% |
| **总 CXL 池化增量成本** | **~$9,160** | **~15%** |

> 池化的 8TB 内存如果每台自配 512GB（共 8TB），成本完全相同。**CXL 池化的 ROI 来自利用率提升而非单 GB 成本下降。**

### 7.5 软件生态成熟度

| 软件层 | 现状 | 缺口 |
|:-------|:-----|:-----|
| **Linux 内核** | ✅ CXL 内存热插拔 + NUMA 感知 | 更好的 page migration 策略 |
| **内存分配器** | ✅ 部分支持（jemalloc/tcmalloc 扩展） | CXL-aware 自动分配策略 |
| **Kubernetes** | ⚠️ 动态内存资源调度 | 缺少 CXL 池化感知的调度器 |
| **AI 框架** | ✅ vLLM/SGLang 支持 | 更智能的 KV Cache CXL 分层策略 |
| **数据库** | ⚠️ SAP HANA 支持 | 广义的内存池化 SQL 引擎优化 |

---

## 8. 总结与展望

**CXL 芯片产业的三个发展阶段**：

```text
Phase 1 (2019-2023): Protocol definition
|-- CXL 1.0/2.0/3.0 standards released
|-- CPU integrated CXL controller (Xeon/EPYC)
|-- first CXL memory expanders (Astera/Montage)
+-- point-to-point only, no switching

Phase 2 (2024-2026): Switch chip landing <- current
|-- CXL 2.0 Switch mass production (XConn lead)
|-- CXL 3.0 Switch sampling (XConn/Broadcom)
|-- first large-scale production (Alibaba Beluga)
|-- CXL 3.1 standard (shared memory support)
+-- GPU direct CXL initial validation

Phase 3 (2027+): Full penetration
|-- CXL becomes server motherboard standard
|-- GPU native CXL 3.0+ support
|-- CXL over Optical breaks distance limits
|-- CXL Fabric becomes 2nd network (scale-up)
+-- CXL replaces some RDMA memory pool scenarios
```

**核心判断**：

1. **CXL Switch 是当前最紧缺的芯片品类**——XConn 暂时领先但 Broadcom 即将大规模进入
2. **AI 推理 KV Cache 是 CXL 最确定的杀手场景**——Beluga 已经证明了数量级的改善
3. **GPU 原生 CXL 支持是下一个关键里程碑**——如果 NVIDIA 下一代 GPU 集成 CXL 3.0 端口，将引爆 CXL 产业
4. **CXL 不会取代 RDMA**，但会在 Scale-Up 域内内存语义场景中**替代 RDMA 的本地内存池角色**
5. **国产 CXL 生态（澜起 MXC）已在跟进**，但 CXL Switch 仍是空白

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- [Beluga CXL 内存池架构](../01_product/00_hardware/01_hw-core/2026-06-26-alibaba-beluga.md) — 关联
- [CXL KV Cache Pooling](../02_project/01_superpod/architecture/2026-07-29-intel-cxl-pooling-dup1.md) — 关联
- [高速互联全景](../01_product/00_hardware/04_si-signal/2026-07-29-high-speed-interconnect-deep-dive.md) — 关联

### 外部资料引用

- 来源: Xinjun Yang et al., "Beluga: A CXL-Based Memory Architecture for Scalable and Efficient LLM KVCache Management", *SIGMOD 2026* (arXiv:2511.20172)
- 来源: Xu Zhang et al., "DFabric: Scaling Out Data Parallel Applications with CXL-Ethernet Hybrid Interconnects", *USENIX ATC 2025* (arXiv:2409.05404)
- 来源: Hyein Woo et al., "ScalePool: Hybrid XLink-CXL Fabric for Composable Resource Disaggregation", arXiv:2510.14580
- 来源: Chandrahas Tirumalasetty et al., "Exploring DRAM Cache Prefetching for Pooled Memory", *MEMSYS 2024* (arXiv:2406.14778)
- 来源: Zixuan Wang et al., "The Hitchhiker's Guide to Programming and Optimizing Cache Coherent Heterogeneous Systems", arXiv:2411.02814 (Heimdall)
- 来源: Khan Shaikhul Hadi et al., "Distributed Persistence Domain for Persistent Memory Pooling", arXiv:2606.07159
- 来源: Nils Asmussen et al., "Towards Disaggregation-Native Data Streaming between Devices", *HCDS 2024* (arXiv:2406.09421)
- 来源: CXL Consortium, "Compute Express Link 3.1 Specification", 2024
- 来源: Intel, "CXL Memory Pooling for AI Inference", 2025
- 来源: XConn, "XC50256 CXL 2.0 Switch Product Brief", 2024
- 来源: Astera Labs, "Leo CXL Memory Controller Family", 2024
- 来源: 澜起科技, "MXC CXL Memory Controller Datasheet", 2024
- 来源: SemiAnalysis, "CXL Memory Pooling: Hype vs Reality", 2025
- 来源: [Beluga: 阿里云 CXL 内存池架构](../01_product/00_hardware/01_hw-core/2026-06-26-alibaba-beluga.md)
- 来源: [CXL KV Cache Pooling 方案](../02_project/01_superpod/architecture/2026-07-29-intel-cxl-pooling-dup1.md)
- 来源: [高速互联技术全景深潜](../01_product/00_hardware/04_si-signal/2026-07-29-high-speed-interconnect-deep-dive.md)
- 来源: --

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
