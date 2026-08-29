# OCP 芯片设计规格与技术要点全景

> **概要**: (待补充)
>
> **关键词**: (待补充)

---

## 📑 目录

- [1. 文档结构与阅读指南](#1-文档结构与阅读指南)
  - [1.1 源材料清单](#11-源材料清单)
  - [1.2 芯片设计关注维度](#12-芯片设计关注维度)
- [2. OCP 加速器模块 (OAM) 与 AI 加速芯片](#2-ocp-加速器模块-oam-与-ai-加速芯片)
  - [2.1 Facebook Big Basin Volta](#21-facebook-big-basin-volta)
  - [2.2 加速器形态因子](#22-加速器形态因子)
  - [2.3 加速器芯片对比表](#23-加速器芯片对比表)
- [3. OpenCAPI 架构：开放一致性加速器接口](#3-opencapi-架构开放一致性加速器接口)
  - [3.1 架构定位](#31-架构定位)
  - [3.2 OpenCAPI 架构层次](#32-opencapi-架构层次)
  - [3.3 FPGA 侧 TLx/DLx 资源消耗](#33-fpga-侧-tlxdlx-资源消耗)
  - [3.4 延迟对比](#34-延迟对比)
  - [3.5 带宽实测对比](#35-带宽实测对比)
  - [3.6 内存范式支持](#36-内存范式支持)
  - [3.7 OpenCAPI 关键属性总结](#37-opencapi-关键属性总结)
- [4. Gen-Z 内存语义互联架构](#4-gen-z-内存语义互联架构)
  - [4.1 核心定位](#41-核心定位)
  - [4.2 技术动因：计算-内存平衡退化](#42-技术动因计算-内存平衡退化)
  - [4.3 Gen-Z 核心特性](#43-gen-z-核心特性)
  - [4.4 通信效率对比](#44-通信效率对比)
  - [4.5 虚拟通道与流量分类](#45-虚拟通道与流量分类)
  - [4.6 Gen-Z 规范发布状态](#46-gen-z-规范发布状态)
  - [4.7 Gen-Z 与 OCP 的关系](#47-gen-z-与-ocp-的关系)
- [5. NVIDIA NVLink 2.0 GPU 互联](#5-nvidia-nvlink-20-gpu-互联)
  - [5.1 Zaius/Barreleye G2 集成方案](#51-zaiusbarreleye-g2-集成方案)
  - [5.2 NVLink 加速器形态](#52-nvlink-加速器形态)
- [6. Ampere eMAG ARMv8 服务器 SoC](#6-ampere-emag-armv8-服务器-soc)
  - [6.1 芯片定位与市场](#61-芯片定位与市场)
  - [6.2 芯片规格](#62-芯片规格)
  - [6.3 云优化指标](#63-云优化指标)
  - [6.4 软件生态](#64-软件生态)
  - [6.5 目标市场](#65-目标市场)
  - [6.6 架构理念（Ampere 设计哲学）](#66-架构理念ampere-设计哲学)
- [7. Intel AI 芯片组合：Xeon → NNP → FPGA](#7-intel-ai-芯片组合xeon-nnp-fpga)
  - [7.1 Intel AI 芯片产品矩阵](#71-intel-ai-芯片产品矩阵)
  - [7.2 Intel Xeon Scalable (Skylake-SP) AI 规格](#72-intel-xeon-scalable-skylake-sp-ai-规格)
  - [7.3 Xeon SP AI 性能演进](#73-xeon-sp-ai-性能演进)
  - [7.4 Intel Nervana NNP (Lake Crest)](#74-intel-nervana-nnp-lake-crest)
  - [7.5 Project Brainwave](#75-project-brainwave)
- [8. Intel XDP 硬件加速与 NIC 芯片卸载](#8-intel-xdp-硬件加速与-nic-芯片卸载)
  - [8.1 架构目标](#81-架构目标)
  - [8.2 硬件提示 (HW Hints) 定义](#82-硬件提示-hw-hints-定义)
  - [8.3 硬件提示类型](#83-硬件提示类型)
  - [8.4 性能提升效果](#84-性能提升效果)
  - [8.5 Metadata 传递方案](#85-metadata-传递方案)
- [9. Marvell NVMe SSD 存储控制器芯片组](#9-marvell-nvme-ssd-存储控制器芯片组)
  - [9.1 芯片组产品线](#91-芯片组产品线)
  - [9.2 NVMe SSD Switch (88SNV2414)](#92-nvme-ssd-switch-88snv2414)
  - [9.3 NVMe SSD 控制器 (88SS1098/1099)](#93-nvme-ssd-控制器-88ss10981099)
  - [9.4 模块化构建块架构](#94-模块化构建块架构)
  - [9.5 扩展能力](#95-扩展能力)
  - [9.6 未来芯片演进方向](#96-未来芯片演进方向)
- [10. Microsoft Denali SSD 芯片架构](#10-microsoft-denali-ssd-芯片架构)
  - [10.1 设计动机](#101-设计动机)
  - [10.2 架构演进](#102-架构演进)
  - [10.3 逻辑层次化寻址 (LHA)](#103-逻辑层次化寻址-lha)
  - [10.4 Cache Minimum Write Size (CMWS)](#104-cache-minimum-write-size-cmws)
  - [10.5 关键性能结果](#105-关键性能结果)
- [11. Mellanox / Netronome OCP Mezzanine 网卡芯片](#11-mellanox-netronome-ocp-mezzanine-网卡芯片)
  - [11.1 Mellanox ConnectX-4/5 芯片规格](#111-mellanox-connectx-45-芯片规格)
  - [11.2 Mellanox ConnectX-5 特性 (Zaius 平台)](#112-mellanox-connectx-5-特性-zaius-平台)
  - [11.3 Netronome NFP (Network Flow Processor)](#113-netronome-nfp-network-flow-processor)
- [12. 芯片固件架构与安全](#12-芯片固件架构与安全)
  - [12.1 Open System Firmware (OSF)](#121-open-system-firmware-osf)
  - [12.2 OSF 工作流与所有者](#122-osf-工作流与所有者)
  - [12.3 Intel 固件体系](#123-intel-固件体系)
  - [12.4 平台可信启动 (Platform Attestation)](#124-平台可信启动-platform-attestation)
  - [12.5 PCIe 设备安全增强](#125-pcie-设备安全增强)
  - [12.6 固件配置管理 (Redfish SPMF)](#126-固件配置管理-redfish-spmf)
- [13. 芯片调试基础设施](#13-芯片调试基础设施)
  - [13.1 Intel Direct Connect Interface (DCI)](#131-intel-direct-connect-interface-dci)
  - [13.2 芯片调试能力](#132-芯片调试能力)
  - [13.3 UEFI 芯片初始化的调试断点](#133-uefi-芯片初始化的调试断点)
  - [13.4 芯片调试安全性检查](#134-芯片调试安全性检查)
- [14. Redfish 芯片硬件管理基线](#14-redfish-芯片硬件管理基线)
  - [14.1 规范范围](#141-规范范围)
  - [14.2 芯片管理标准属性](#142-芯片管理标准属性)
- [15. 增量分析与空白标注](#15-增量分析与空白标注)
  - [15.1 与现有知识库的对比](#151-与现有知识库的对比)
  - [15.2 ⭐ 关键发现](#152-关键发现)
  - [15.3 推荐下一步方向](#153-推荐下一步方向)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 1. 文档结构与阅读指南

### 1.1 源材料清单

| # | 文件 | 核心主题 | 芯片设计相关度 |
|:--|:-----|:---------|:------------:|
| 1 | `OCP-2018-AI-Hardware-Infrastructure-at-Facebook-FINAL.md` | Facebook AI 硬件，Big Basin Volta | ⭐⭐⭐ |
| 2 | `OCP-PDF-Adi-Gangidi-Accelerator.md` | Zaius/Barreleye G2 加速器生态，OpenCAPI/NVLink/PCIe Gen4 | ⭐⭐⭐⭐⭐ |
| 3 | `Accelerating-Flash-Memory-with-...OpenCAPI-Interface-...md` | OpenCAPI 3.0/3.1 详细架构，TLx/DLx FPGA 参考 IP | ⭐⭐⭐⭐⭐ |
| 4 | `OCP-GenZ-March-2018-final.md` | Gen-Z 内存语义互联规范 v1.0 | ⭐⭐⭐⭐⭐ |
| 5 | `18150J-Ampere-PPT-OCPSummitAtiq-v2.1-Compressed.md` | Ampere eMAG SoC 云处理器架构理念 | ⭐⭐⭐⭐ |
| 6 | `18150J-Ampere-PPT-OCPSummitKumar-final.md` | Ampere eMAG 详细规格指标 | ⭐⭐⭐⭐⭐ |
| 7 | `Intel-DeepLearning-PlatformJordanPlawner-OCP18.md` | Intel AI 组合：Xeon SP / Nervana NNP / FPGA | ⭐⭐⭐⭐ |
| 8 | `Intel-XDP-AccelerationWaskiewicz-Parikh-OCP18.md` | Intel NIC XDP 硬件加速 | ⭐⭐⭐⭐ |
| 9 | `Intel-System-Firmware-InnovationsMohanKumar-OCP18.md` | 芯片固件体系：Open Firmware/PFR/Redfish | ⭐⭐⭐⭐⭐ |
| 10 | `2018-03-21-Marvell-Nigel-Alvares-OCP-Summit-2018...md` | Marvell NVMe SSD Switch 芯片组 | ⭐⭐⭐⭐⭐ |
| 11 | `2018-03-OCP-Denali.md` | Microsoft Denali Open-Channel SSD 芯片架构 | ⭐⭐⭐⭐⭐ |
| 12 | `2018OCP-OSF-OpenEDKII-Workstream.md` | Open System Firmware 开放芯片固件 | ⭐⭐⭐⭐ |
| 13 | `Debugging_Intel_Firmware_using_DCI___USB_3.0.md` | Intel DCI 芯片级调试技术 | ⭐⭐⭐⭐ |
| 14 | `OCP Baseline Hardware Mgmt v0.2.0.md` | Redfish 芯片硬件管理规范 | ⭐⭐⭐ |
| 15 | `Mellanox_100GbE_Card_User_Manual_OCP_rev_1_0.md` | Mellanox ConnectX-4 NIC 芯片 OCP 规格 | ⭐⭐⭐⭐ |
| 16 | `Netronome 25G-50G OCP Mezzanine Card v1.0.md` | Netronome 网络流处理器 Mezzanine | ⭐⭐⭐⭐ |
| 17 | `Intel-Democratizing-AICarlosMorales-OCP18.md` | Intel AI 芯片战略全景 | ⭐⭐⭐ |
| 18 | `Capri_AMD_1P_OCP ROME SPEC proposal_20210127v2.md` | AMD Rome 1P OCP 平台 | ⭐⭐ |

### 1.2 芯片设计关注维度

本文从以下 9 个维度审视 OCP 生态中的芯片设计：

| 维度 | 关注重点 |
|:----|:---------|
| **🔌 接口协议** | 芯片间 / 芯片到芯片互联的物理层与协议层设计 |
| **⚙️ 架构创新** | 微架构、缓存一致性、内存模型等芯片架构层面 |
| **🧮 计算加速** | AI / 网络 / 存储专用加速器芯片设计 |
| **🔐 安全与可信** | 芯片级 Root-of-Trust、固件安全、设备认证 |
| **📡 SerDes/PHY** | 高速 SerDes 速率、功耗、面积、IP 化 |
| **💾 存储控制** | SSD/NVMe 控制器、FTL、ECC 引擎 |
| **🔧 可调试性** | 芯片级调试接口（JTAG/DCI）与诊断 |
| **🖥️ 固件栈** | 芯片启动、初始化（FSP/AGESA）、运行时固件 |
| **📊 管理标准** | 芯片硬件管理接口（Redfish/IPMI） |

---

## 2. OCP 加速器模块 (OAM) 与 AI 加速芯片

### 2.1 Facebook Big Basin Volta

> **来源**: `OCP-2018-AI-Hardware-Infrastructure-at-Facebook-FINAL.md`

| 参数 | 规格 |
|:----|:-----|
| GPU | NVIDIA Tesla V100 (Volta) SXM2 |
| 架构 | 5120 CUDA Cores, 640 Tensor Cores |
| 显存 | 16 GB HBM2 |
| TDP | 300W |
| 互联 | NVLink 2.0 (100 GB/s 双向) |
| 配套平台 | OCP Tioga Pass |
| 应用 | 计算机视觉、机器翻译、推荐系统 |

**关键设计要点**:

- GPU 通过 NVLink 实现 CPU-GPU 直连（100 GB/s），消除 PCIe 瓶颈
- 支持 FP16 TensorCore，推理吞吐量相比 FP32 大幅提升
- Facebook 内部 2012→2018 演进：HP SL270s → Big Sur → Big Basin(2016) → Big Basin Volta(2018)

### 2.2 加速器形态因子

> **来源**: `OCP-PDF-Adi-Gangidi-Accelerator.md`

OCP 定义了三种加速器物理形态：

| 形态 | 描述 | 适用场景 |
|:----|:-----|:---------|
| **Perpendicular Mount** | PCIe card edge 垂直安装 | 通用 PCIe 加速器 |
| **Perpendicular + Coherent Attach** | PCIe + 25G 线缆一致性连接 | 需要 CPU 缓存一致性的加速器 |
| **Parallel Mount via Mezz** | 并行安装 + 一致性线缆 | GPU/OpenCAPI 高性能加速器 |

**SerDes 速率**: 25.78125 Gbps (OpenCAPI 3.0)
**双向总带宽**: 100 GB/s (800 Gbps) — 4 路 OpenCAPI/NVLink 配置

### 2.3 加速器芯片对比表

| 加速器 | 芯片类型 | 主机接口 | 存储 | 内存 | FPGA LUT |
|:-------|:---------|:---------|:-----|:-----|:---------|
| Alpha Data ADM-9V3 | Xilinx Kintex Ultrascale+ | OpenCAPI x8 25G | — | 4GB DDR4 | 523K |
| Mellanox Innova 2 Flex | Xilinx Kintex US+ & ConnectX-5 | OpenCAPI x8 25G | — | 8GB DDR4 | 522K |
| Nallatech 250S+ | Xilinx Virtex Ultrascale+ | PCIe Gen4 x8 | 12.8TB NVMe | 32GB DDR4 | 394K |
| Molex FSA (Flash Storage Accel) | Xilinx Zynq Ultrascale+ MPSoC | OpenCAPI x8 25G | 16TB NVMe | 64GB DDR4 | 523K |

---

## 3. OpenCAPI 架构：开放一致性加速器接口

### 3.1 架构定位

> **来源**: `Accelerating-Flash-Memory-with-...OpenCAPI-Interface-...md`

OpenCAPI (Open Coherent Accelerator Processor Interface) 是 IBM 贡献给 OCP 的一致加速器接口标准。

| 属性 | 值 |
|:----|:----|
| 版本演进 | CAPI 1.0 (POWER8) → CAPI 2.0 (POWER9) → OpenCAPI 3.0/3.1 |
| SerDes 速率 | 25 Gb/s per lane |
| 宽度 | x8 (8 lanes) |
| 单向带宽 | 22.1 GB/s (实测) |
| 数据类型 | Load/Store 字节寻址 + Block 访问 |
| 一致性 | 全缓存一致性（用户态直接访问） |
| 虚拟寻址 | 支持，无需内核/虚拟化层介入 |

### 3.2 OpenCAPI 架构层次

```text
+-------------------------------------+
|          Application                 |
+-------------------------------------+
|   TLx (Transaction Layer - FPGA)    | <- 400MHz 参考设计
+-------------------------------------+
|   DLx (Data Link Layer - FPGA)      | <- 400MHz 参考设计
+-------------------------------------+
|   PHYx (25G SerDes)                 |
+-------------------------------------+
|   OTL/ODL (Host 侧)                  | <- 不对称设计
+-------------------------------------+
```

**关键设计**: TLx 和 DLx 是**不对称**的——FPGA 侧的 TLx/DLx 与 Host 侧的 OTL/ODL 不同。TLx/DLx 作为参考设计 RTL 提供给联盟成员。

### 3.3 FPGA 侧 TLx/DLx 资源消耗

| 资源 | DLx | TLx |
|:----|:---|:---|
| CLB FlipFlops | 9,392 (1.19%) | 19,026 (4.82%) |
| LUT as Logic | 13,806 (1.75%) | 8,463 (2.14%) |
| LUT Memory | 0 (0%) | 2,156 (1.09%) |
| Block RAM Tile | 7.5 (1.0%) | 0 (0%) |

**平台**: Xilinx VU3P (394k LUTs), 总 Fabric 利用率仅 ~8.1%

| FPGA | 总 kLUTs | OpenCAPI IP 利用率 |
|:-----|:---------|:------------------|
| VU3P | 394 | 8.1% |
| KU15P | 523 | 6.1% |
| VU9P | 1,182 | 2.7% |

### 3.4 延迟对比

```text
PCIe Gen3 (Kaby Lake):  776ns 总延迟 ±31ns 抖动
POWER9 PCIe Gen3:       737ns 总延迟 ±7ns 抖动
POWER9 PCIe Gen4:       <555ns (估计)
POWER9 OpenCAPI 3.0:    378ns 总延迟 ±2ns 抖动  <- 🏆
```

**OpenCAPI 延迟分解**:

- TL/DL/PHY (FPGA 侧): ~80ns (仿真)
- 链路传播: 占比极低
- Host 侧 OTL/ODL: 集成于 CPU，远低于 FPGA 侧

### 3.5 带宽实测对比

| 测试 | CAPI 1.0 (PCIe G3 x8) | CAPI 2.0 (PCIe G4 x8) | OpenCAPI 3.0 (25G x8) |
|:----|:---------------------:|:---------------------:|:---------------------:|
| 128B DMA Read | 3.81 GB/s | 12.57 GB/s | 22.1 GB/s |
| 128B DMA Write | 4.16 GB/s | 11.85 GB/s | 21.6 GB/s |
| 256B DMA Read | — | 13.94 GB/s | 22.1 GB/s |
| 256B DMA Write | — | 14.04 GB/s | 22.0 GB/s |

### 3.6 内存范式支持

| 范式 | OpenCAPI 支持 |
|:----|:-------------|
| 主存直连 (DDR4/5) | ✅ 传统 |
| 存储级内存 (SCM) | ✅ ASIC buffer +5ns, Load/Store 语义 |
| 分层内存 (DDR+SCM) | ✅ OpenCAPI 3.0+3.1 双架构 |
| 加速器直接访问 | ✅ Home Agent Memory (CPU 一致性设备内存) |

### 3.7 OpenCAPI 关键属性总结

| 属性 | 详情 |
|:----|:-----|
| **架构无关** | 适用于任何系统/微处理器架构 |
| **25G 零开销设计** | 无协议转换开销 |
| **一致性** | 设备原生运行于应用用户空间并与 Host 缓存一致 |
| **虚拟寻址** | 无需内核/虚拟化/固件介入 |
| **宽广用例** | Load/Store + Block 访问，经典内存到 SCM 全支持 |

---

## 4. Gen-Z 内存语义互联架构

### 4.1 核心定位

> **来源**: `OCP-GenZ-March-2018-final.md`（Dell EMC CTO Office, Greg Casey）

Gen-Z 是由 50+ 成员公司组成的联盟定义的内存语义互联（Memory-Semantic Fabric），旨在解决计算-内存平衡退化问题。

### 4.2 技术动因：计算-内存平衡退化

| 指标 | 2012 | 2019 |
|:----|:----|:----|
| CPU 核心数 | ~8 | 64+ |
| DDR 通道 | 4 | 8 |
| PCIe Lanes | 40 | 64+ |
| **DRAM 带宽/核** | 基准 | **降至约 1/4** |
| **PCIe 带宽/核** | 基准 | **降至约 1/3** |

**结论**: 处理器内存和 I/O 技术被拉伸到极限，内存带宽/核持续下降。

### 4.3 Gen-Z 核心特性

| 特性 | 规格 |
|:----|:-----|
| **延迟** | 端到端 <250ns 单程，Load-to-Use <100ns (DRAM 介质) |
| **物理层** | 25/32 GT/s SerDes，复用现有电气层 |
| **交换延迟** | 30-50ns 每跳 |
| **虚拟通道** | 32 VCs/链路 |
| **最大载荷** | 256 bytes (效率 >90%) |
| **寻址空间** | 16-bit subnet ID + 12-bit component ID + 64-bit 内存地址 = **~268M 组件理论上限** |
| **拓扑** | 点对点、Daisy-chain、Mesh（任意路由） |
| **路由** | 自适应/分散路由、动态拥塞管理 |

### 4.4 通信效率对比

```text
传统存储软件栈                      Gen-Z + 持久内存
+------------------+               +------------------+
|   Application    |               |   Application    |
+------------------+               +------------------+
|   File System    |               |  --- 0 copies ---|
+------------------+               | Load/Store 指令  |
|   I/O Buffers    |               | 1-3 条指令       |
+------------------+               +------------------+
|   Drivers        |
+------------------+               vs.
|   Controller     |               25,000 条指令
+------------------+               vs. 1-3 条指令
|   Cache          |
+------------------+
|   Media          |
+------------------+
```

### 4.5 虚拟通道与流量分类

| 流量类别 (Traffic Class) | VC 分配 | 用途 |
|:------------------------|:--------|:----|
| Latency Sensitive | VC0-7 | SHMEM, 实时计算 |
| Bandwidth Sensitive | VC8-15 | 检查点, 大块数据 |
| Noise Sensitive | VC16-23 | 集合通信 |
| High-priority | VC24-31 | 管理/控制平面 |

### 4.6 Gen-Z 规范发布状态

| 规范 | 版本 | 发布状态 |
|:----|:----|:---------|
| Core Specification | 1.0 | 2018-02-13 发布 |
| Scalable Connector Spec | 1.0 | 已发布 |
| SFF 8639 2.5-inch Spec | 1.0 | 已发布 |
| SFF 8639 2.5-inch Compact Spec | 1.0 | 已发布 |

**硅化时间线**:

- 2018 Q1: IntelliProp 设计 IP, Avery 验证 IP
- 2018: 开发系统
- 2019-2020: 早期用户系统

### 4.7 Gen-Z 与 OCP 的关系

Gen-Z 联盟贡献了 SFF-TA-1002 连接器机械与电气规范至 SNIA，OCP NIC 3.0 规范后续沿用了此连接器标准。

---

## 5. NVIDIA NVLink 2.0 GPU 互联

### 5.1 Zaius/Barreleye G2 集成方案

> **来源**: `OCP-PDF-Adi-Gangidi-Accelerator.md`

| 参数 | 规格 |
|:----|:-----|
| CPU | POWER9 (双路) |
| GPU | Tesla V100 SXM2 |
| NVLink 版本 | 2.0 |
| 带宽 | 100 GB/s 双向/GPU |
| 物理连接 | 2× SlimSAS 24G 线缆/GPU (SFF-8654) |
| 每 CPU 接口 | 2× "Bricks"，每 Brick 25 GB/s 单向 |
| 总系统带宽 | 4 Bricks → 100 GB/s 单向 = 800 Gbps |

### 5.2 NVLink 加速器形态

| 特性 | 描述 |
|:----|:-----|
| 形态 | SXM2 (特殊插座，非 PCIe) |
| Coherency | NVLink 2.0 实现 CPU-GPU 一致性 |
| 加速比 | 相比 PCIe Gen3 的 CPU-GPU 瓶颈消除 |
| 应用 | 大型深度学习模型、GPU 分析 (Kinectica, MapD, BlazingDB) |
| 未来方向 | JBoG (Just a Bunch of GPUs) 实现 |

---

## 6. Ampere eMAG ARMv8 服务器 SoC

### 6.1 芯片定位与市场

> **来源**: `18150J-Ampere-PPT-OCPSummitKumar-final.md`

Ampere eMAG 是针对云工作负载优化的 ARM 架构服务器处理器。

| 指标 | 数据 |
|:----|:-----|
| 云服务器 CPU 市场 (2021E) | $8B（占整体服务器 CPU >50%） |
| 云市场 CAGR | 11% (2017→2021) |
| 传统 CPU 市场 CAGR | 仅 2% |

### 6.2 芯片规格

| 规格 | eMAG |
|:----|:-----|
| **核心** | Ampere 自研 ARMv8 64-bit 核心 |
| **核心数** | 32 核 |
| **频率** | 最高 3.3GHz (带 Turbo) |
| **内存** | 8× DDR4-2667 通道 |
| **PCIe** | 42 lanes PCIe Gen3 |
| **工艺** | TSMC 16FF+ (成熟工艺) |
| **架构标准** | ARM SBSA/SBBR 合规 |
| **许可模式** | ARMv8 架构授权 |

### 6.3 云优化指标

| 指标 | eMAG vs Intel Xeon Gold 6130 | eMAG vs Intel Xeon Silver 4110 |
|:----|:---------------------------:|:------------------------------:|
| **Perf/Watt** (机架级) | **+15%** | **+10%** |
| **Perf/$** (机架级) | **+35%** | **+20%** |
| **Perf/Rack** | **+20%** | **+35%** |

**测试条件**: 42U 机架, 40× 1U 服务器, 每节点 384GB 内存, 8× SSD, 1× 2×10GE 网络

### 6.4 软件生态

| 层次 | 支持 |
|:----|:-----|
| **OS** | RHELSA 7.3/7.4, CentOS 7.3/7.4, Ubuntu 16.04 LTS, SLES 15, Oracle Linux 7.4 |
| **BIOS** | 标准 UEFI |
| **BMC** | OpenBMC |
| **编译器** | GCC 6.x/7.x, LLVM ≥v3.9 |
| **Windows** | Microsoft Windows Server on eMAG (已演示) |

### 6.5 目标市场

| 层级 | 示例 |
|:----|:-----|
| Web 层 | Apache, NGINX, HAProxy, Drupal, WordPress |
| 大数据/分析 | Hadoop, Spark, Kafka, MapReduce |
| 数据管理 | Memcached, Redis, Cassandra, MongoDB, PostgreSQL, MySQL |
| 存储 | CEPH, GlusterFS, OpenStack Swift/Cinder |

### 6.6 架构理念（Ampere 设计哲学）

> **来源**: `18150J-Ampere-PPT-OCPSummitAtiq-v2.1-Compressed.md`

Ampere 首席架构师 Atiq Bajwa 提出的云处理器设计原则：

| 维度 | 理念 | 芯片设计关注点 |
|:----|:-----|:--------------|
| **Integration** | 智能集成，优化密度与成本 | SoC 的集成粒度 vs 灵活性 |
| **Power Efficiency** | 功率效率驱动密度和 OpEx | 每瓦性能的"云原生"优化 |
| **Memory** | 容量、带宽与延迟 | 8ch DDR4-2667 vs 竞品 6ch |
| **Compute** | 平衡的计算能力 | 32 核心 vs 核心复杂度权衡 |
| **Acceleration** | 工作负载特定加速 | 芯片内加速引擎规划 |
| **Security** | 从设计开始的安全 | ARM TrustZone + 企业级安全 |
| **Open** | 通过开放标准扩展 | SBSA/SBBR/OCP 合规 |
| **Legacy Burdens** | 去除传统包袱 | 去除 x86 遗留兼容性成本 |

---

## 7. Intel AI 芯片组合：Xeon → NNP → FPGA

### 7.1 Intel AI 芯片产品矩阵

> **来源**: `Intel-DeepLearning-PlatformJordanPlawner-OCP18.md`, `Intel-Democratizing-AICarlosMorales-OCP18.md`

```text
               Training                     Inference
                |                            |
   Mainstream  +- Xeon SP (AVX-512, VNNI)    +- Xeon SP (INT8, FP32)
                |                            |
   Intensive   +- Nervana NNP (Lake Crest)   +- Nervana NNP
                |                            |
   Real-time   |                            +- Arria FPGA (Project Brainwave)
                |                            |
   Edge        |                            +- Movidius VPU (1-20W)
```

### 7.2 Intel Xeon Scalable (Skylake-SP) AI 规格

| 参数 | 规格 |
|:----|:-----|
| 核心数 | 28 核 / 56 线程 (Platinum 8180) |
| 内存通道 | 6× DDR4 |
| 二级缓存 | 1MB/核 (中间级缓存) |
| 向量扩展 | Intel AVX-512 (2× 512b FMA) |
| FP32 性能 | 6.9 TFLOPS |
| INT8 性能 | 12 TOPS |
| DL 推理加速 | 2.4× vs 前代 (GoogleNet v1, FP32) |
| DL 训练加速 | 2.2× vs 前代 (ResNet-50) |

### 7.3 Xeon SP AI 性能演进

| 时间 | ResNet-50 推理 (图像/秒) | 优化 |
|:----|:----------------------:|:----|
| 2017-07 (Launch) | 131 | 基线 |
| 2017-12 (Launch+SW) | 226 | +72% (MKL-DNN 优化) |
| 2018-01 (Launch+SW) | 453 | +100% (INT8 量化) |
| 2019+ | 652 | +44% (继续优化) |

### 7.4 Intel Nervana NNP (Lake Crest)

| 特性 | 描述 |
|:----|:-----|
| **架构** | 大规模并行计算引擎 |
| **片上内存** | 大容量 HBM（直接软件控制） |
| **片上互联** | 高速片内 Fabric |
| **芯片间** | 专用芯片间数据传输 |
| **数值格式** | Flexpoint（优化定点） |
| **产品路线图** | 2017 首批硅片，超过性能目标 |
| **管理** | 托管数据流路径 |

### 7.5 Project Brainwave

Intel Arria FPGA 实现实时 AI 推理加速，定位为"灵活性与性能兼备"的云侧推理方案，在 OCP Summit 2018 提出。

---

## 8. Intel XDP 硬件加速与 NIC 芯片卸载

### 8.1 架构目标

> **来源**: `Intel-XDP-AccelerationWaskiewicz-Parikh-OCP18.md`

Intel 提出利用 NIC 硬件解析能力加速 XDP/eBPF 包处理，将 NIC 芯片从"被动转发"升级为"主动加速"。

### 8.2 硬件提示 (HW Hints) 定义

```text
NIC 硬件 Rx 流水线:
+---------+   +---------+   +---------+   +---------+
| Packet  | -> |  Meta   | -> | Switch  | -> |  Table  |
| Parser  |   | Compute |   | Actions |   | Lookup  |
+---------+   +---------+   +---------+   +---------+
                         ↕
                   +----------+
                   | XDP/eBPF |
                   | Program  |
                   +----------+
```

**核心创新**: 通过 ELF 段定义 eBPF 所需的硬件提示，在加载 eBPF 程序时一并配置 NIC 硬件。

### 8.3 硬件提示类型

| 提示类型 | 大小 | 描述 |
|:--------|:----|:-----|
| Packet Type | U16 | 发现的有序头部链的唯一标识 |
| Header Offset | U16 | 特定头部起始位置 |
| Extracted Field Value | 可变 | 如：最内层 IPv6 地址 |
| Hash Fields and Type | 可变 | 选定字段上的哈希 |
| Map Offload Match | U32 | 匹配规则及软件标记 |
| Checksum | U32 | 总包校验和 |
| Packet Hash | U32 | 基于指定字段和键的哈希值 |
| Ingress Timestamp | U64 | 包到达时间戳 |

### 8.4 性能提升效果

| 场景 | 无 Hints | Hints Type 1 | Hints Type 2 | 提升 |
|:----|:--------:|:------------:|:------------:|:----:|
| L4 LB (无状态, 1Q) | ~6M pps | ~10M pps | ~14M pps | **2.3×** |
| L4 LB (无状态, 4Q) | ~7M pps | ~12M pps | ~15M pps | **2.1×** |
| L4 LB (有状态, 1Q) | ~3M pps | ~4M pps | ~5M pps | **1.7×** |

**说明**: Hints Type 1 = 协议类型；Hints Type 2 = Type 1 + 源/目的 IP + 源/目的端口 + RSS 哈希

### 8.5 Metadata 传递方案

| 方案 | 描述 |
|:----|:-----|
| **方案1**: 通用布局 | 独立于底层硬件的公共结构，需社区一致同意 |
| **方案2**: 供应商库 | XDP/eBPF 程序检测底层硬件后调用对应库 |
| **方案3**: 链式 XDP | 轻量 shim 含供应商逻辑，尾调用主程序 |

---

## 9. Marvell NVMe SSD 存储控制器芯片组

### 9.1 芯片组产品线

> **来源**: `2018-03-21-Marvell-Nigel-Alvares-OCP-Summit-2018-Presentation-Final-Version.md`

| 芯片 | 类型 | 关键规格 |
|:----|:----|:---------|
| **88SNV2414** | NVMe SSD Switch | 业界首款 NVMe SSD 交换芯片 |
| **88SS1098/1099** | NVMe 控制器 | 单/双端口 x4，4代 NANDEdge™ ECC |

### 9.2 NVMe SSD Switch (88SNV2414)

| 参数 | 规格 |
|:----|:-----|
| 功能 | 汇聚并虚拟化最多 **4 个** NVMe SSD 控制器 |
| 性能 | 最高 **1.6M IOPS** & **6.4 GB/s** 吞吐量 |
| 主机卸载 | 减轻 Host CPU 负担，实现最优 QoS |
| 典型配置 | 1× Switch + 4× 单端口控制器 = 高性能 U.2 SSD |

### 9.3 NVMe SSD 控制器 (88SS1098/1099)

| 参数 | 规格 |
|:----|:-----|
| NANDEdge™ ECC | 第 4 代，支持 **QLC NAND** |
| SR-IOV | 支持，最多 **64 个虚拟功能** |
| 性能 | 最高 **800K IOPS** & **3.6 GB/s** |
| 端口 | 单端口 (x4) 或 双端口 (x4) |

### 9.4 模块化构建块架构

```text
M.2 2280 SSD          M.2 22110 SSD
+-------------+      +-------------+
| NVMe Ctrlr  |      | NVMe Ctrlr  |
| (88SS1098)  |      | (88SS1098)  |
+-------------+      +-------------+
         ↘                  ↙
     +--------------------------+
     |    NVMe SSD Switch       |
     |    (88SNV2414)           |
     +--------------------------+
               |
          +----+----+
        U.2 SSD (高性能)
```

### 9.5 扩展能力

| 配置 | 控制器 | NAND 封装 | DRAM | IOPS |
|:----|:------|:--------:|:----:|:----:|
| 标准 | 1× 单端口 | 32 pkg | 16 GB | 800K |
| 扩展 | 2× 单端口 | 32 pkg | 16 GB | 1.5M |
| 旗舰 | 4× 单端口 + Switch | 40 pkg | 32 GB | 1.6M |

### 9.6 未来芯片演进方向

| 方向 | 涉及芯片 |
|:----|:--------|
| 新兴内存控制器 | SCM (ReRAM/MRAM) 控制器 |
| 工作负载加速器 | Key-Value, ML, 可编程逻辑 |
| NVMe-oF 桥接 | NVMe over Fabrics |
| Gen-Z/OpenCAPI 接口 | 下一代接口桥接 |

---

## 10. Microsoft Denali SSD 芯片架构

### 10.1 设计动机

> **来源**: `2018-03-OCP-Denali.md`

| 痛点 | Denali 方案 |
|:----|:-----------|
| SSD FTL (Flash Translation Layer) 黑盒 | FTL 上移至 Host 实现 |
| 写放大不可控 | Host 利用工作负载信息优化 WAF |
| QoS 抖动 | 开放通道，Host 直接管理 |
| 供应商锁定 | 供应商中立的硬件抽象 |

### 10.2 架构演进

```text
传统 SSD          开放通道 SSD        Denali SSD
+------+          +------+           +------+
|Host  |          |Host  |           |Host  |
+------+          +------+           +------+
|FTL   |          |Log   |  <-Host    |Log   |
|      |          |Mgmt  |           |Mgmt  |
+------+          +------+           +------+
|Media |          |Media |           |Media |  <-Drive
|Mgmt  |          |Mgmt  |           |Mgmt  |
+------+          +------+           +------+
   ^                  ^                  ^
  全封闭          半开放 (OCSSD 1.2)   全开放 (OCSSD 2.0)
```

### 10.3 逻辑层次化寻址 (LHA)

```text
地址格式: [Group | Parallel Unit | Chunk | Sector]
            v           v           v       v
         SSD通道     NAND Die    multi-   512B/
                                plane    4kB
                                block    区域
```

| 字段 | 对应物理 | 作用 |
|:----|:---------|:-----|
| Group | SSD Channel | 并行通道 |
| Parallel Unit | NAND Die | 并行单元 |
| Chunk | Multi-plane Block | 擦除块聚合 |
| Sector | 512B/4kB | 页内区域 |

### 10.4 Cache Minimum Write Size (CMWS)

**定义**: NAND Flash 物理特性导致的逻辑抽象。由于 MLC/TLC 多比特单元的部分写脆弱性，Drive 暴露 CMWS 给 Host，约束最小写粒度。

| CMWS 值 | 含义 |
|:--------|:-----|
| >0kB | Host 需保证未关闭 Chunk 的悬空单元不超过 CMWS |
| 0kB | Drive 内部缓存处理，Host 无需关注 |

### 10.5 关键性能结果

| 指标 | 结果 |
|:----|:----|
| **WAF (端到端)** | 优于传统 SSD（逻辑驱动优化） |
| **内存** | 1GB DRAM/TB Flash（与传统 SSD 持平） |
| **CPU** | 1 核/Drive（可进一步优化） |
| **读性能** | Top-in-Class |
| **读延迟 (含背景写)** | Top-in-Class (4KB QD1 < 100μs) |

---

## 11. Mellanox / Netronome OCP Mezzanine 网卡芯片

### 11.1 Mellanox ConnectX-4/5 芯片规格

> **来源**: `Mellanox_100GbE_Card_User_Manual_OCP_rev_1_0.md`

| 参数 | ConnectX-4 EN (100GbE) |
|:----|:---------------------|
| 接口类型 | OCP Mezzanine 2.0 |
| PCIe | Gen3 x16 (8 GT/s), 兼容 2.0/1.1 |
| 以太网速率 | 1/10/25/40/50/100 GbE |
| SerDes | 16 lanes @ 8 GT/s (PCIe) + 4 lanes @ 25 Gb/s (100GbE) |
| 典型功耗 | 13.84W (无源线缆) |
| 最大功耗 | 19.53W (有源光缆) |
| 存储 | 16MB Flash + 16MB EEPROM |
| 管理 | NC-SI (Network Controller Sideband Interface) |

**协议支持**:

- 100GBASE-CR4/KR4/SR4/LR4/ER4
- 50GBASE-R2/R4, 40GBASE 全系列
- 25GBASE-R, 10GBASE 全系列
- SGMII, 1000BASE

### 11.2 Mellanox ConnectX-5 特性 (Zaius 平台)

| 特性 | 描述 |
|:----|:-----|
| 速率 | 100GbE (双口) |
| 形态 | OCP Mezzanine 2.0 |
| 主机接口 | PCIe Gen4 x16 |
| 典型应用 | 100G 网络密集部署 |

### 11.3 Netronome NFP (Network Flow Processor)

> **来源**: `Netronome 25G-50G OCP Mezzanine Card v1.0.md`

| 参数 | 25G 版 | 50G 版 |
|:----|:------|:------|
| **网络端口** | 1× SFP28 (25G) | 1× QSFP28 (50G) |
| **主机接口** | PCIe Gen3 x8 | PCIe Gen3 x8 |
| **连接器** | BergStak 0.8mm, 200pos | BergStak 0.8mm, 200pos |
| **功能** | 可编程 NIC, CPU offload | 可编程 NIC, CPU offload |
| **Offload 类型** | SDN, vSwitch, 隧道协议 | SDN, vSwitch, 隧道协议 |

**芯片设计要点**:

- Netronome NFP 是**可编程网络流处理器**（非普通 NIC ASIC）
- 支持 Host 侧 SDN 数据面卸载
- 虚拟交换与隧道协议硬件加速
- 通过 NC-SI 实现 OOB 管理

**连接器信号组** (200-pin BergStak):

| 信号组 | 数量 | 说明 |
|:------|:----|:-----|
| PCIe TX/RX | 16 lanes | Connector A + B 各 8 lane |
| KR TX/RX | 16 lanes | 可选 Backplane KR 信号 |
| NC-SI | 6 信号 | RCLK, TXEN, TXD[1:0], RXD[1:0], CRSDV, RXER |
| SMBus | 2 组 | OOB 管理 (100/400kHz) + Mezz 槽位 EEPROM |
| 100MHz CLK | 4 对 | PCIe 参考时钟 |
| 电源 | 12V/5V/3.3V | Aux + 主电源 |
| 复位 | 4× PERST | 多节点系统 |

**电源预算**:

| 电压轨 | 电流能力 |
|:------|:--------|
| P12V_AUX/12V | 2.4A (conn A) + 1.6A (conn B) = **4.0A max** |
| P5V_AUX | 2.4A |
| P3V3_AUX | 1.6A |
| P3V3 | 6.4A |

---

## 12. 芯片固件架构与安全

### 12.1 Open System Firmware (OSF)

> **来源**: `2018OCP-OSF-OpenEDKII-Workstream.md`

OSF 是由 Microsoft/Google/Facebook 等发起的开放系统固件计划，解决芯片固件封闭问题。

```text
OSF 总体架构:
+--------------------------------------------------+
|                    OS                            |
+--------------------------------------------------+
|              Linux Boot / Bootloader             |
+--------------------------------------------------+
|         Open EDK II DXE Core (开源核心)            |
+--------------------------------------------------+
|    Silicon Interface Firmware Module (SIFM)      |
+----------+----------+----------+------------------+
|  Intel   |  AMD     |  ARM     |  POWER           |
|  FSP     |  AGESA   |  vendor  |  Host Boot       |
|  二进制   |  RC 二进制| 二进制   |                  |
+----------+----------+----------+------------------+
|     ROT / HW Security Module (Cerberus)          |
+--------------------------------------------------+
```

**关键架构创新** — 硅接口固件模块 (Silicon Interface Firmware Module):

- 标准化不同芯片厂商的固件接口
- 向上提供统一接口给 Open EDK II DXE Core
- 向下封装 Intel FSP (二进制), AMD AGESA (二进制), ARM vendor bin, POWER 启动代码
- 目标：消除不同硅厂商启动流程差异造成的固件开发维护低效

### 12.2 OSF 工作流与所有者

| 工作流 | 所有者 |
|:------|:-------|
| PEI | Intel |
| Intel FSP binary | Intel |
| AGESA RC binary | AMD |
| ARM Boot code binary | ARM |
| Power Host boot | OpenPOWER |
| Core Boot | Google, FB, Two Sigma, Horizon |
| Silicon Interface Firmware Module | 芯片厂商 |
| Linux Boot | OS 厂商 |
| Open EDK II DXE core | Two Sigma |
| HW platform modules | Horizon, Google |
| 安全编码规范 | 社区 |

### 12.3 Intel 固件体系

> **来源**: `Intel-System-Firmware-InnovationsMohanKumar-OCP18.md`

```text
Intel 开放 UEFI 固件架构:
+--------------------------------------+
|   Platform Firmware Interface        |
|   (ACPI, UEFI)                       |
+--------------------------------------+
|   Open source UEFI core (EDKII)      | <- github.com/tianocore/edk2
+--------------------------------------+
|   PEIMs + Intel Silicon Init         |
+--------------------------------------+
|   Platform (board) specific code     | <- github.com/tianocore/edk2-platforms
+--------------------------------------+
|   Intel Si code (binary)             | <- github.com/intelfsp
+--------------------------------------+
```

| 组件 | 开源状态 | 存储位置 |
|:----|:--------|:---------|
| UEFI Core (EDKII) | ✅ 完全开源 | tianocore/edk2 |
| Platform 代码 | ✅ 开源 | tianocore/edk2-platforms |
| Silicon 初始化 (FSP) | ❌ 二进制 | github.com/intelfsp |
| OpenBMC | ✅ 开源 | OpenBMC 项目 |

**Mt. Olympus** (Intel Xeon OCP 平台): 首个采用完整 UEFI 开源固件的平台，已可用。

### 12.4 平台可信启动 (Platform Attestation)

Intel PFR (Platform Firmware Resilience) 的实现层次：

| 安全层 | 技术 | 描述 |
|:-------|:-----|:-----|
| **L1** | BIOS/BMC 镜像认证 | 运行前验证固件签名 |
| **L2** | CPU ↔ Root-of-Trust 互认证 | CPU 与平台信任根双向验证 |
| **L3** | 自动恢复 | 检测到固件损坏自动恢复至已知良好状态 |
| **L4** | 冷/热重启均执行 | Warm reset 和 Hard reset 均进行认证 |
| **L5** | SPI 总线运行时监控 | 运行时过滤 SPI 总线流量，抵御攻击 |
| **L6** | 外设固件扩展 | 认证扩展到 PCIe 卡等外设 |

### 12.5 PCIe 设备安全增强

| 特性 | 描述 |
|:----|:-----|
| **Device Firmware Measurement** | 验证不可变和可变固件版本 |
| **Device Authentication** | 查询设备身份（绑定设备私钥） |
| **规范状态** | 已发布提案草案，建立于 USB 认证架构之上 |

### 12.6 固件配置管理 (Redfish SPMF)

Intel 提出基于 Redfish 的 BIOS 配置可扩展模型：

- 替代传统 BIOS Setup 界面
- 支持**远程配置**和**大规模部署**
- JSON Schema: `BIOSAttributeRegistry*.json`
- 支持属性依赖 (Attribute Dependencies)，如 `MinProcIdlePower` 依赖 `PowerProfile`
- 固件版本依赖关系矩阵：`UpdateDependencies` 字段（如 BIOS > =0.6.1, BMC==1.0.1）

---

## 13. 芯片调试基础设施

### 13.1 Intel Direct Connect Interface (DCI)

> **来源**: `Debugging_Intel_Firmware_using_DCI___USB_3.0.md`

Intel DCI 是通过 USB 3.0 实现闭箱 JTAG 调试的芯片级技术。

| 参数 | 规格 |
|:----|:-----|
| 传输介质 | USB 3.0 (Type A-to-A) |
| 调试协议 | JTAG over USB |
| 目标芯片 | 6th Gen Core 及以上 (含 Xeon) |
| 调试范围 | CPU Reset → UEFI SEC/PEI/DXE → OS Boot |
| 硬件附加 | Intel CCA (Closed Chassis Adapter) |

### 13.2 芯片调试能力

| 能力 | 描述 |
|:----|:-----|
| UEFI 固件调试 | 全阶段 (SEC/PEI/DXE/BDS/TSL) 源码级调试 |
| 符号加载 | "LoadThis" 自动搜索 UEFI 模块，加载调试符号 |
| 断点 | `CpuBreakpoint()`, `CpuDeadLoop()`, `CpuIceBreakpoint()` (int1) |
| 多核调试 | SMP 运行控制，多逻辑核显示 |
| Trace | LBR (Last Branch Record), IPT (Intel Processor Trace) |
| CHIPSEC 集成 | 通过 DAL 在调试会话中运行安全分析 |

### 13.3 UEFI 芯片初始化的调试断点

| 断点类型 | 实现 | 适用阶段 |
|:---------|:-----|:---------|
| `CpuBreakpoint()` | EDK II BaseLib, `hlt`/`int3` | SEC/PEI/DXE |
| `CpuDeadLoop()` | EDK II BaseLib, 死循环 | SEC/PEI/DXE |
| `CpuIceBreakpoint()` | `int1` opcode (自定义) | 最佳 Trace 信息 |

### 13.4 芯片调试安全性检查

CHIPSEC 模块 `debugenabled` 检查以下芯片级调试接口状态：

| 检查项 | 寄存器位置 |
|:-------|:----------|
| HDCIEN bit | ECTRL Register (PCH) |
| Debug Enable bit | IA32_DEBUG_INTERFACE MSR |
| Debug Lock bit | IA32_DEBUG_INTERFACE MSR |
| Debug Occurred bit | IA32_DEBUG_INTERFACE MSR |

---

## 14. Redfish 芯片硬件管理基线

### 14.1 规范范围

> **来源**: `OCP Baseline Hardware Mgmt v0.2.0.md`

| 管理资源 | 芯片/设备相关 |
|:---------|:-------------|
| Service Root | 管理服务根 |
| AccountService | Redfish 账户服务 |
| Chassis | 机箱/芯片所属底板 |
| Chassis/Power | 芯片功耗管理 |
| Chassis/Thermal | 芯片温度管理 |
| Managers | BMC/管理控制器 |
| Managers/EthernetInterfaces | 管理网络接口 |
| Managers/ManagerNetworkProtocol | 管理协议配置 |

### 14.2 芯片管理标准属性

**Power 资源**: 实时功率、功耗上限、电源供应器状态
**Thermal 资源**: 温度传感器、风扇、冷却策略
**Manager 资源**: BMC 固件版本、复位、NIC 管理

---

## 15. 增量分析与空白标注

### 15.1 与现有知识库的对比

| 主题 | 现有 KB 覆盖 | 本文件增量 | 建议 |
|:----|:-----------|:-----------|:-----|
| **OpenCAPI** | 少量提及 | ⭐ 首次系统化覆盖架构层次、TLx/DLx FPGA IP 资源、延迟/带宽实测对比、4 种内存范式 | ✅ **新增** |
| **Gen-Z 互联** | 无 | ⭐ 首次系统化覆盖：32 VC 设计、268M 组件寻址、延迟模型、规范时间线 | ✅ **新增** |
| **NVLink 2.0 OCP 实现** | 少量提及 | ⭐ Zaius/Barreleye G2 具体工程实现：2× SlimSAS Brick, 25 GB/s 每路 | ✅ **新增** |
| **Ampere eMAG SoC** | 少量提及 | ⭐ 详细芯片规格、云优化指标、市场定位、软件生态 | ✅ **新增** |
| **Intel NNP/Nervana** | 无 | ⭐ 芯片架构特征、Flexpoint 数值格式、产品路线图 | ✅ **新增** |
| **Intel XDP HW 加速** | 无 | ⭐ NIC 硬件提示定义、3 种元数据传递方案、实测性能数据 | ✅ **新增** |
| **Marvell NVMe Switch** | 无 | ⭐ 业界首款 NVMe 交换芯片规格、QLC ECC、64 虚拟功能 | ✅ **新增** |
| **Denali SSD** | 无 | ⭐ 开放通道 SSD 芯片架构、LHA 地址格式、CMWS 机制 | ✅ **新增** |
| **OSF / 芯片固件** | 少量提及 | ⭐ SIFM 标准化架构、各芯片厂商二进制接口、Mt. Olympus 开源实践 | ✅ **新增** |
| **Intel PFR / Cerberus** | 少量提及 | ⭐ 6 层安全认证体系、PCIe 设备安全增强 | ✅ **新增** |
| **Intel DCI 调试** | 无 | ⭐ USB3-JTAG 芯片级调试、断点类型、CHIPSEC 安全核查 | ✅ **新增** |
| **Mellanox/Netronome NIC 芯片** | 已有 mezzanine 文档 | ⭐ ConnectX-4 芯片级规格、Netronome NFP 可编程流处理器 | ✅ **补充** |

### 15.2 ⭐ 关键发现

1. **OCP 加速器芯片生态多样化**: 从 PCIe → OpenCAPI → NVLink → Gen-Z，OCP 生态覆盖了 2017-2018 年几乎所有主流芯片互联技术，为后来 CXL 等标准奠定了基础
2. **OpenCAPI 的 FPGA 资源效率出色**: TLx/DLx 整套一致性接口仅消耗 8.1% 的 VU3P Fabric，说明 25G SerDes 时代一致性接口的硅代价已可接受
3. **Marvell NVMe Switch 芯片的模块化理念**: 1× Switch + 4× 控制器构建块架构可灵活适配 M.2 → U.2 → EDSFF 多形态
4. **Denali 是 Host-SSD 功能划分的极端实践**: 将 FTL 全部上移至 Host，仅保留 Media Management 在芯片，对 NAND 可靠性的芯片/主机权责划分提出了 CMWS 等新抽象
5. **OSF SIFM 的跨芯片固件标准化**: 用 Silicon Interface Firmware Module 统一 Intel FSP/AMD AGESA/ARM vendor/POWER 的启动接口，是芯片固件生态的关键创新

### 15.3 推荐下一步方向

| # | 方向 | 理由 | 优先级 |
|:--|:-----|:-----|:------|
| 1 | OpenCAPI → CXL 演化追踪 | OCP 时期的 OpenCAPI 是 CXL 的前身之一，追踪其技术继承关系有价值 | ⭐⭐⭐ |
| 2 | Gen-Z 技术遗产分析 | Gen-Z 虽未大规模商用，但其内存语义互联思想直接影响了 CXL.mem 和 UCIe | ⭐⭐⭐ |
| 3 | Marvell NVMe Switch 后续发展 | 检查 88SNV2414 是否成为数据中心 NVMe 交换的标准方案 | ⭐⭐ |
| 4 | OSF → UEFI 开源生态现状 | 追踪 2018 OSF 提案的落地情况，当前 tianocore/edk2-platforms 的成熟度 | ⭐⭐⭐ |
| 5 | Ampere eMAG → AmpereOne 演化 | eMAG (16FF+, 32核) → AmpereOne (5nm, 192核) 架构设计理念的延续 | ⭐⭐ |

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- (无)

### 外部资料引用

- (无)

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-21 | v1.0 | 首次创建，自 `import/work/ocp/` 中提炼芯片设计规格与技术要点，15 章 |
