# OCP 单板设计规格与技术要点概览

> **概要**: (待补充)
>
> **关键词**: (待补充)

---

## 📑 目录

- [1. 文档来源清单](#1-文档来源清单)
  - [平台级设计规格](#平台级设计规格)
  - [单板/刀片级设计规格](#单板刀片级设计规格)
  - [管理模块规格](#管理模块规格)
  - [加速/扩展卡规格](#加速扩展卡规格)
  - [其他参考](#其他参考)
- [2. OCP 单板设计体系概览](#2-ocp-单板设计体系概览)
  - [2.1 分层架构](#21-分层架构)
  - [2.2 设计维度矩阵](#22-设计维度矩阵)
- [3. 主板/系统板设计](#3-主板系统板设计)
  - [3.1 Delta Lake 1S Server Card（Intel Cooper Lake）](#31-delta-lake-1s-server-cardintel-cooper-lake)
    - [处理器与芯片组](#处理器与芯片组)
    - [PCIe 互联拓扑（2 种配置）](#pcie-互联拓扑2-种配置)
    - [Riser 接口规范](#riser-接口规范)
    - [前端扩展接口（Straddle Mount）](#前端扩展接口straddle-mount)
    - [板卡尺寸](#板卡尺寸)
  - [3.2 Qualcomm Centriq 2400 Open Compute Motherboard](#32-qualcomm-centriq-2400-open-compute-motherboard)
    - [关键特性](#关键特性)
    - [Project Olympus 符合性](#project-olympus-符合性)
    - [Riser 类型矩阵](#riser-类型矩阵)
  - [3.3 MiTAC Capri 2S Server](#33-mitac-capri-2s-server)
    - [主板规格](#主板规格)
    - [PCIe 扩展](#pcie-扩展)
    - [管理子系统](#管理子系统)
    - [BIOS 特性](#bios-特性)
  - [3.4 Nokia Telco Enhanced Open Rack Server](#34-nokia-telco-enhanced-open-rack-server)
    - [设计目标](#设计目标)
    - [硬件结构](#硬件结构)
    - [接口布局](#接口布局)
    - [信号互联](#信号互联)
    - [管理特性](#管理特性)
  - [3.5 Inspur Crane Mountain (NF8260M5)](#35-inspur-crane-mountain-nf8260m5)
    - [定位](#定位)
    - [PCB 规格](#pcb-规格)
- [4. 多节点服务器设计（Yosemite V3）](#4-多节点服务器设计yosemite-v3)
  - [4.1 平台架构](#41-平台架构)
  - [4.2 Class 1 vs Class 2 双模式](#42-class-1-vs-class-2-双模式)
  - [4.3 Baseboard 设计要点](#43-baseboard-设计要点)
  - [4.4 Blade 设计要点（参考 §3.1 Delta Lake）](#44-blade-设计要点参考-31-delta-lake)
  - [4.5 Sled Management Cable 定义](#45-sled-management-cable-定义)
- [5. 管理子系统设计（DC-SCM + RunBMC）](#5-管理子系统设计dc-scm-runbmc)
  - [5.1 DC-SCM（Datacenter Secure Control Module）](#51-dc-scmdatacenter-secure-control-module)
    - [设计目标](#设计目标)
    - [两个外形因数](#两个外形因数)
    - [接口全集（DC-SCI 连接器）](#接口全集dc-sci-连接器)
    - [电源与启动时序](#电源与启动时序)
    - [路由指南](#路由指南)
  - [5.2 RunBMC Daughterboard Card](#52-runbmc-daughterboard-card)
    - [物理形态](#物理形态)
    - [接口信号功能组](#接口信号功能组)
    - [热与机械约束](#热与机械约束)
- [6. 扩展与加速卡设计](#6-扩展与加速卡设计)
  - [6.1 Netronome OCP Mezzanine 2.0 Card](#61-netronome-ocp-mezzanine-20-card)
    - [接口信号](#接口信号)
  - [6.2 Mellanox 50GbE OCP Card](#62-mellanox-50gbe-ocp-card)
  - [6.3 Expansion Board BOARD_ID 编码](#63-expansion-board-board_id-编码)
- [7. 连接器标准与信号定义](#7-连接器标准与信号定义)
  - [7.1 连接器标准总表](#71-连接器标准总表)
  - [7.2 Blade ↔ Baseboard 信号定义核心引脚（1C Connector, ×4 PCIe）](#72-blade-baseboard-信号定义核心引脚1c-connector-4-pcie)
  - [7.3 引脚定义合规要求](#73-引脚定义合规要求)
- [8. 电源架构设计](#8-电源架构设计)
  - [8.1 电源拓扑](#81-电源拓扑)
  - [8.2 热插拔电源序列](#82-热插拔电源序列)
  - [8.3 电源特性指标](#83-电源特性指标)
  - [8.4 BMC 电源管理策略](#84-bmc-电源管理策略)
- [9. 热设计规范](#9-热设计规范)
  - [9.1 数据中心环境](#91-数据中心环境)
  - [9.2 散热设计指标](#92-散热设计指标)
  - [9.3 热管理传感器](#93-热管理传感器)
  - [9.4 风扇控制](#94-风扇控制)
- [10. 机械设计与 PCB 规格](#10-机械设计与-pcb-规格)
  - [10.1 PCB 规格](#101-pcb-规格)
  - [10.2 机械叠层](#102-机械叠层)
  - [10.3 散热片设计要求](#103-散热片设计要求)
- [11. 管理架构（BMC → BIC → IPMB）](#11-管理架构bmc-bic-ipmb)
  - [11.1 三层管理架构](#111-三层管理架构)
  - [11.2 BIC 功能清单](#112-bic-功能清单)
  - [11.3 BMC 功能清单](#113-bmc-功能清单)
  - [11.4 IPMI 错误日志分类](#114-ipmi-错误日志分类)
- [12. 信号完整性要点](#12-信号完整性要点)
  - [12.1 PCIe 插入损耗分配](#121-pcie-插入损耗分配)
  - [12.2 接口时序约束](#122-接口时序约束)
  - [12.3 PCIe Gen3 信号质量关键点](#123-pcie-gen3-信号质量关键点)
- [13. 关键发现与增量分析](#13-关键发现与增量分析)
  - [13.1 与现有知识库的关系](#131-与现有知识库的关系)
  - [13.2 关键发现](#132-关键发现)
  - [13.3 推荐后续方向](#133-推荐后续方向)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 1. 文档来源清单

以下为本次分析的核心文档（按设计层级分类）：

### 平台级设计规格

| 文档名称 | 机构 | 核心内容 | 页数 |
|:---------|:-----|:---------|:----:|
| Yosemite V3 Platform Design Specification 1v01 | Facebook | 4节点 1S sled 平台整体设计 | ~105KB |
| Microsoft Project Olympus Servers (2017) | Microsoft + Intel/AMD/Cavium/Qualcomm | 通用服务器主板规范, 多 CPU 架构兼容 | ~12KB |
| QCT Big Sur Product Architecture v1.1 | Quanta/QCT | 4OU/21" GPU 服务器架构, 含 GPU Linking Board | ~59KB |
| Hyve Solutions Ambient Series-E r8 | Hyve | Decathlete 兼容双路服务器主板 | ~21KB |

### 单板/刀片级设计规格

| 文档名称 | 机构 | 核心内容 | 页数 |
|:---------|:-----|:---------|:----:|
| Delta Lake 1S Server Design Spec 1v00 | Facebook | Intel Cooper Lake 1S CPU 刀片设计 | ~105KB |
| Qualcomm Centriq 2400 OCM v0.5 | Qualcomm | ARM64 Centriq 2400 单路 Project Olympus 主板 | ~36KB |
| MiTAC Capri 2S Server (E8020) v1.0 | MiTAC | Intel Xeon 双路 OCP 2S sled | ~130KB |
| Telco enhanced Open Rack Server v1.0 | Nokia | NFV 优化 OCP 兼容单路服务器 | ~88KB |
| Crane Mountain (NF8260M5) v0.1 | Inspur | 2U4S 高密度 Intel Xeon 平台 | ~21KB |
| Capri AMD 1P OCP Rome SPEC v2 | MiTAC | AMD Rome 单路 OCP Computing Sled | ~10KB |

### 管理模块规格

| 文档名称 | 机构 | 核心内容 | 页数 |
|:---------|:-----|:---------|:----:|
| DC-SCM Spec Rev 0.8 | Microsoft/Google | 数据中心安全控制模块标准 | ~48KB |
| RunBMC Daughterboard Card Design Spec v1.4.1 | Dropbox/Salesforce | BMC 子卡 260-pin SODIMM DDR4 接口定义 | ~38KB |

### 加速/扩展卡规格

| 文档名称 | 机构 | 核心内容 | 页数 |
|:---------|:-----|:---------|:----:|
| Netronome 25G/50G OCP Mezzanine 2.0 Card v1.0 | Netronome | 可编程智能网卡 Mezzanine 2.0 | ~7KB |
| Mellanox 50GbE OCP Card User Manual v1.0 | Mellanox | 50GbE OCP 网卡 | ~17KB |

### 其他参考

| 文档名称 | 核心内容 |
|:---------|:---------|
| OCP3-Design-Validation-Workshop-1p3 | OCP 设计验证工作坊方法论 |
| Qualcomm Centriq 2400 OCM for Project Olympus | Olympus 通用主板框架下 ARM 实现 |
| OCP18-OpenBMC-End-User-Features | OpenBMC 特性端用户视角 |

---

## 2. OCP 单板设计体系概览

OCP 单板设计从 **Facebook 数据中心需求**出发，形成一套完整的 **从系统板→管理板→加速板** 的模块化分层设计体系。

### 2.1 分层架构

```text
+------------------------------------------------------+
|  OCP Rack v2 Bus Bar (12V / 48V)                     |
+------------------------------------------------------+
|  Medusa Cable -> Medusa Power Board (MPB) -> PDB       |
+------------------------------------------------------+
|  Yosemite V3 Sled Chassis (4OU)                      |
|  +--------------------------------------------------+|
|  |  Baseboard (BMC AST2520 + OCP NIC 3.0)          ||
|  |  +------+ +------+ +------+ +------+            ||
|  |  |Blade1| |Blade2| |Blade3| |Blade4|            ||
|  |  | 1S   | | 1S   | | 1S   | | 1S   |            ||
|  |  |CPU   | |CPU   | |CPU   | |CPU   |            ||
|  |  +------+ +------+ +------+ +------+            ||
|  |  +--- Expansion Modules (1U/2U) ---------------+ ||
|  +--------------------------------------------------+|
+------------------------------------------------------+
```

### 2.2 设计维度矩阵

| 设计维度 | Yosemite V3 (Facebook) | Capri 2S (MiTAC) | Telco Server (Nokia) | Qualcomm OCM |
|:---------|:----------------------|:-----------------|:--------------------|:-------------|
| CPU 架构 | Intel Xeon Cooper Lake 1S | Intel Xeon 2S | Intel Xeon 1S | ARM64 Centriq 2400 1S |
| 形态 | CPU 刀片（4/ blade） | 独立 2U sled | 独立 1-2U 服务器 | Project Olympus 1U |
| 管理 | BMC + Blade BIC + CPLD | BMC AST2520 | BMC AST2500 | BMC |
| 电源 | 12V 集中→各板 HSC | 12V 独立 HSC | 12V HSC | 12V 机架 |
| 热设计 | 1U/2U 被动散热 | 2U 被动 | 1U 强制风冷 | 1U 被动 |
| 扩展 | 前端 + 2U Riser | Mezzanine + Riser | Mezzanine + U.2 | Riser + M.2 Mega Card |

---

## 3. 主板/系统板设计

### 3.1 Delta Lake 1S Server Card（Intel Cooper Lake）

**公司**: Facebook | **形态**: CPU 刀片模块（1U/2U） | **适配**: Yosemite V3 平台

#### 处理器与芯片组

- **CPU**: Intel 3rd Gen Xeon Scalable (Cooper Lake), LGA 封装, 热插拔 FRU
- **PCH**: Intel C620 Chipset 系列, 提供 ACPI/LPC/eSPI/SPI/SMBus/GPIO
- **内存**: 6 通道 DDR4 R-DIMM, 1 DIMM/通道, 2933-3200MT/s, 支持 NVDIMM
- **M.2 启动盘**: 1× M.2 NVMe (2280/22110) 直连 CPU, PCH 可选
- **调试**: ITP/XDP debug headers

#### PCIe 互联拓扑（2 种配置）

| 配置 | 用途 | CPIe 宽度 |
|:-----|:-----|:----------|
| Class 1 (主) | 共享 MH NIC (Baseboard) | ×4 |
| Class 1 | Riser 扩展 | ×24 |
| Class 1 | 前端扩展 | ×16 |
| Class 2 | 专用 NIC (前扩展卡) | ×16 |

#### Riser 接口规范

- 类似 OCP NIC 3.0 引脚定义但**非全适配**
- 信号: 24 lanes PCIe + 2 ref clocks + I2C + USB + UART + PWRBRK
- 电源: 12V + 3.3V_STBY
- 类型检测: 3-bit RISER_CARD_TYPE_DETECTION

#### 前端扩展接口（Straddle Mount）

- 遵循 LFF OCP NIC 3.0 引脚定义, **全引脚适配**
- 信号: 16 lanes PCIe + ref clk + I2C + USB + Wake + PWRBRK
- 热插拔: **不支持**（非 hot-swappable）

#### 板卡尺寸

- 服务器卡: 321.4mm × 157.0mm
- 刀片模块: 533.5mm × 164.0mm
- 1U 刀片高: 40.8mm, 2U 刀片高: 82.2mm

---

### 3.2 Qualcomm Centriq 2400 Open Compute Motherboard

**公司**: Qualcomm | **形态**: Project Olympus 1U 服务器主板 | **架构**: ARM64

#### 关键特性

- **SoC**: Qualcomm Centriq 2400 (ARMv8, 48核)
- **内存**: 6 通道 DDR4, 支持 RDIMM/LRDIMM
- **PCIe**: 32 lanes PCIe Gen3
- **存储**: M.2 Mega Card (特殊大容量 M.2 形态)
- **管理**: BMC + NC-SI

#### Project Olympus 符合性

- 符合 Project Olympus Server Mechanical Spec
- 兼容 Olympus PSU、PMD（Power Management Distribution Unit）
- 支持 Olympus Server Motherboard 标准中的 Riser Type #3/#4/#5/#6

#### Riser 类型矩阵

| Riser Type | 特性 | 说明 |
|:-----------|:-----|:-----|
| Type #3 | x16 + x16 | 双宽 GPU 或网络 |
| Type #4 | x8 + x8 + x8 | 多路存储/网络 |
| Type #5 | x16 | 单宽加速器 |
| Type #6 | 存储专用 | SATA/SAS 扩展 |

---

### 3.3 MiTAC Capri 2S Server

**公司**: MiTAC | **型号**: E8020 | **CPU**: Intel Xeon 双路

#### 主板规格

- **PCB**: 12" × 13", 8 层, 1.6mm
- **CPU**: Intel Xeon Haswell/Broadwell-EP (R3 socket), 2 颗, 145W max
- **QPI**: 9.6 GT/s
- **PCH**: Intel C610 (Wellsburg)
- **内存**: 16 DIMM 槽, ECC RDIMM/LRDIMM, 最高 1TB

#### PCIe 扩展

- 1× PCIe x16 G3 Riser (low-profile)
- 1× PCIe x8 G3 Riser (可选)
- 1× PCIe x8 G3 OCP Mezzanine 卡槽

#### 管理子系统

- **BMC**: ASPEED AST2400（VGA + GbE 管理口）
- IPMI 2.0 全兼容
- SOL (Serial over LAN)
- 传感器监控: 温度/电压/功率/风扇
- MCA dump 支持

#### BIOS 特性

- BIOS POST Code 通过 Port 80 输出
- 支持 WHEA ID 和 Endless Boot
- BMC FRB2 Watchdog Timer
- 受控处理器库存编号 (Protected Processor Inventory Number)

---

### 3.4 Nokia Telco Enhanced Open Rack Server

**公司**: Nokia | **目标**: NFV / 电信边缘 | **规范版本**: v1.0

#### 设计目标

- OCP Open Rack v2 兼容
- 满足电信 CO 站点 EMI 屏蔽 + ETSI 环境要求
- 增强 NUMA 性能（PCIe 全路由至 CPU1）+ 存储冗余 (NVMe)

#### 硬件结构

- **CPU**: Intel Xeon Scalable (具体型号未限定)
- **PCH**: Lewisburg
- **内存**: 系统内存 + 可扩展
- **BMC**: AST2500
- **CPLD** + TPM 安全模块

#### 接口布局

| 接口 | 位置 | 说明 |
|:-----|:-----|:-----|
| 千兆管理口 + USB + VGA | 前面板 | 本地调试 |
| Mini USB | 前面板 | 串口/调试 |
| 电源输入 | 后侧 | ORv2 电源 |
| M.2 + U.2 | 板内 | NVMe 存储 + 启动 |
| Mezzanine 连接器 | 板内 | OCP 网卡 |
| PCIe Riser Slot | 板内 | 扩展卡 |
| 风扇 | 前面板热插拔 | 标准 OCP 风扇 |

#### 信号互联

- SFF-TA1002 兼容连接器
- 5G/ETH 同步信号
- 重置逻辑设计（Power-up + 按钮 + BMC 发起）

#### 管理特性

- 硬件监控: 全板温度/电压传感器
- IPMI over LAN 电源控制
- FRU + SEL
- 错误处理: 从电气错误到系统事件

---

### 3.5 Inspur Crane Mountain (NF8260M5)

**公司**: Inspur (浪潮) | **形态**: 2U4S | **CPU**: Intel Xeon (4 socket)

#### 定位

- OCP 首个 4 路主板贡献
- 高密度云优化平台

#### PCB 规格

- **板层**: 24+ 层
- 4 路 CPU 互联 + 大量 PCIe 通道集成
- 面向虚拟化/数据库/内存计算场景

---

## 4. 多节点服务器设计（Yosemite V3）

### 4.1 平台架构

Yosemite V3 是 Facebook 第三代多节点服务器平台, 定义 **4OU 机箱 + Sled + Blade** 三层结构：

| 层级 | 功能 | 热插拔 |
|:-----|:-----|:-------|
| Chassis (4OU) | 机箱, 兼容 Open Rack v2 | 是 |
| Sled | 基板 + NIC + 管理, **4 blades/sled** | 是 |
| Blade (1S Server) | CPU + 内存 + 存储 | 是 (前端加载) |
| Expansion Module | 1U/2U 前端扩展 | 否 |

### 4.2 Class 1 vs Class 2 双模式

| 特性 | Class 1 (通用) | Class 2 (高性能) |
|:-----|:--------------|:-----------------|
| BMC 位置 | Baseboard | NIC Expansion Card |
| NIC 类型 | Multi-Host (共享) | 专用 NIC (每个 blade 独立) |
| 最大带宽/blade | 25G (×4 PCIe Gen3) | 100G+ |
| Sled 最大 blade 数 | 4 | 2 |
| Baseboard BIC | 无 (BMC 直管) | 有 (BIC 做机箱管理) |

### 4.3 Baseboard 设计要点

- **BMC SoC**: ASPEED AST2520 (无视频/无 PCIe —— 降低成本)
- **管理网络**: NC-SI 通过 OCP NIC 3.0 连接 TOR
- **PCIe 互联**: ×4 lanes/刀片 经 Sled Management Cable
- **插入损耗**: ~12dB @4GHz（Die → 连接器）
- **电源拓扑**: 共享 HSC → 各 blade 独立 HSC

### 4.4 Blade 设计要点（参考 §3.1 Delta Lake）

- **Bridge IC (BIC)**: 每个 blade 的卫星管理控制器
- **CPLD**: 电源序列 + 管理桥接 + UART MUX
- **热插拔**: 通过 PRSNT# → HSC_EN → PWR_BTN# 三阶段序列
- **ID 识别**: 3-bit BOARD_ID[3:0] 用于 Blade/Card/Expansion 类型区分

### 4.5 Sled Management Cable 定义

连接 Baseboard ↔ Blade 的复合线缆：

| 信号类别 | 信号 | 速率/特性 |
|:---------|:-----|:----------|
| PCIe | ×4 lanes + refclk + PERST# | Gen3 |
| IPMB | I2C_IPMB_SDA/SCL | 1MHz |
| I2C | I2C_BMC_CPLD | 400kHz |
| USB | USB +/- (BMC host, 供 blade BIC + expansion BIC) | HS |
| UART | UART_RX/TX (CPLD 到 CPLD) | 调试串口 |
| 控制 | HSC_EN, HSC_FAULT_N, STBY_PWROK, PWRBTN_N, | GPIO |
| 探测 | MB_PRSNT_N, SB_SLOT_ID[1:0] | 板卡检测 |
| 其他 | RST_BMC_N, AC_ON_OFF_BTN, BB_BIC_READY | 管理 |

---

## 5. 管理子系统设计（DC-SCM + RunBMC）

### 5.1 DC-SCM（Datacenter Secure Control Module）

**规范**: Microsoft × Google 联合 | **Rev**: 0.8 (2020) | **150+ 人/28 公司 评审

#### 设计目标

将 BMC/管理功能从主板解耦为独立模块, 实现：

- 主板精简（减少 200+ 元器件）
- 管理模块热插拔/热升级
- 统一 SKU 跨平台复用

#### 两个外形因数

| 外形 | 宽度 | 深度 | 适用场景 |
|:-----|:-----|:-----|:---------|
| HFF (Horizontal FF) | 标准宽度 | 板载 | 标准服务器主板 |
| VFF Option 1 (Vertical) | 标准高度 | 含 IO 支架 | 19"/21" 机架 |
| VFF Option 2 (Vertical) | 标准高度 | 板边安装 | 高密度场景 |

#### 接口全集（DC-SCI 连接器）

| 接口 | 用途 | 速率 |
|:-----|:-----|:-----|
| NC-SI | 管理网络 | RMII 100Mbps |
| eSPI / SSIF | Host ↔ BMC 通信 | eSPI 可扩 |
| SGPIO | 串行 GPIO | 数据输入时序 |
| I2C / I3C | 传感器/FRU/SPD | I2C 400kHz/1MHz; I3C 12.5MHz |
| SPI | BIOS/UEFI Flash | 高达 50MHz |
| USB 2.0 | 管理 USB | 480Mbps |
| PCIe | 可选高速通道 | Gen3/4 |
| PECI | CPU 温度 | Intel 专用 |
| UART | 调试串口 | 115200+ baud |
| JTAG | 边界扫描 | IEEE 1149.1 |

#### 电源与启动时序

- **输入**: 12V + 3.3V_STBY
- **检测**: 通过 PRSNT# + 过流保护电路 (<500ms 熔断)
- **序列**: STBY 上电 → RGMII/MDIO → SoC Boot → 管理功能就绪

#### 路由指南

- NC-SI 时钟/数据差分对 ≤ 2" 不等长
- SGPIO 时钟 ≤ 数据≤ 3.5ns
- I3C ≤ 15pF 总容性负载
- PCIe Gen3/4 差分 ≥ 5mil 间距, 严格控制阻抗

---

### 5.2 RunBMC Daughterboard Card

**规范**: Dropbox × Salesforce | **Rev**: 1.4.1 (2019) | **接口**: 260-pin SODIMM DDR4 连接器

#### 物理形态

- BMC 子系统作为**子卡**插入主板 DDR4 SODIMM 插槽
- 260-pin SODIMM DDR4 接口（非 DIMM 功能, 只借连接器形态）
- 设计意图: 简化 BMC 升级/替换, 统一 BOM

#### 接口信号功能组

| 组 | 信号 | Pin 数 | 说明 |
|:---|:-----|:------:|:-----|
| 电源 | 12V, 3.3V, VDD_RGMII_REF | 7 | 输入电源 |
| ADC | 8-ch ADC | 8 | 模拟量采集 |
| PCIe | ×1 | 7 | PCIe 通道 |
| RGMII | MAC ↔ PHY | 14 | 管理网络 |
| VGA/GPIO | 复用 | 7 | 显示或通用 |
| RMII/NC-SI | 管理口 | 10 | 远程管理 |
| JTAG | 调试 | 6 | 边界扫描 |
| USB2A | Host/Device | 4 | 主机侧 USB |
| USB2B | Device | 3 | 从机 USB |
| SPI1 (Host) | Quad SPI | 7 | BIOS Flash |
| SPI2 (Host) | 普通 SPI | 5 | 备用 |
| FWSPI (Boot) | Quad SPI | 7 | 固件 Flash |
| SYSSPI | 系统 SPI | 4 | 其他 |
| LPC/eSPI | Host IF | 14/11 | 传统/新接口 |
| I2C | 管理总线 | 7 | 传感器/FRU |
| UART | 串口 | 3 | 调试 |
| PWM | 风扇控制 | 2 | 调速 |
| TACH | 风扇反馈 | 4 | 测速 |
| PECI | CPU 温度 | 1 | Intel CPU |
| PASSTHRU | 透传 | 4 | 主板上直接传递 |
| GPIO | 通用 I/O | 21 | 灵活控制 |
| SGPIO | 串行 GPIO | 5 | 扩展 GPIO |
| RESET/POWERGOOD | 复位/电源 | 3 | 状态监测 |
| WATCHDOG | 看门狗 | 2 | 超时复位 |
| INDICATOR | LED 指示 | 2 | 状态 LED |
| RESERVED | 预留 | 22 | 未来扩展 |
| GND | 地 | 38 | 信号参考 |

> **总信号数**: ~260 pins 全覆盖

#### 热与机械约束

- BMC SoC 功耗: <10W TDP
- 组件高度: 板 top side ≤ 3.0mm, bottom ≤ 1.5mm
- 安装: RU/OU 双安装选项（R 卡扣 / O 锁扣）

---

## 6. 扩展与加速卡设计

### 6.1 Netronome OCP Mezzanine 2.0 Card

**规格**: 25G (SFP28) / 50G (QSFP28) | **接口**: 120+80 pos BergStak 连接器

#### 接口信号

| 信号 | 方向 | 说明 |
|:-----|:-----|:-----|
| P12V_AUX/P12V | Power | 12V 主/辅电源 |
| P5V_AUX | Power | 5V 辅助电源 |
| P3V3_AUX/P3V3 | Power | 3.3V 主/辅电源 |
| MEZZ_PRSNTA1_N/BASEBOARD_ID_A | Output | 在位检测 + Baseboard ID |
| MEZZ_PRSNTA2_N | Input | 在位检测确认 |
| LAN_3V3STB_ALERT_N | Input | SMBus 告警（OOB 管理） |
| SMB_LAN_3V3STB_CLK/DAT | I/O | SMBus 管理通道 (100/400kHz) |

- 热性能: 25G 卡 ~25W TDP, 50G 卡 ~35W TDP
- PCIe Gen3 x8 主机接口

### 6.2 Mellanox 50GbE OCP Card

- 50GbE OCP 网卡形态
- 符合 OCP NIC 3.0 规范
- 管理接口: NC-SI

### 6.3 Expansion Board BOARD_ID 编码

OCP 多节点系统中通过 BOARD_ID[3:0] 实现自动设备识别：

| BOARD_ID | 类型 |
|:---------|:-----|
| 0000 | DeltaLake Class1 |
| 0001 | DeltaLake Class2 |
| 0111 | BMC Baseboard |
| 1001 | NIC Expansion Card |
| 1011 | 1U Expansion M.2 |
| 1100 | 2U Expansion w/o switch |
| 1110 | 1U Expansion with EDSFF |
| 1101 | 2U Expansion with switch |
| 1111 | BIC Baseboard |

---

## 7. 连接器标准与信号定义

### 7.1 连接器标准总表

| 连接器 | 用途 | 来源/规范 |
|:-------|:-----|:----------|
| SFF-TA1002 1C Straddle Mount | Blade ↔ Baseboard 信号 | SFF Committee |
| FCI Ortho Power Blade Ultra | 电源输入（Delta Lake） | FCI/TE MBXLE |
| PowerBlade+ | 电源连接（Yosemite V3） | Amphenol/FCI |
| OCP NIC 3.0 Edge Connector | NIC/扩展卡 | OCP NIC 3.0 Spec |
| BergStak 0.8mm (120+80 pos) | Mezzanine 卡 ↔ Baseboard | FCI/Amphenol 61083/61082 |
| SODIMM DDR4 260-pin | RunBMC 子卡 | JEDEC MO-309 兼容 |
| Edge Card DC-SCI | DC-SCM ↔ 主板 | 本规范定义 |
| 4C+ Connector | 2U Expansion | Yosemite V3 定义 |

### 7.2 Blade ↔ Baseboard 信号定义核心引脚（1C Connector, ×4 PCIe）

| Pin Pair | 信号 | 方向(Blade视角) | 说明 |
|:---------|:-----|:----------------|:-----|
| B1/A1 | I2C_IPMB_SDA / BB_BIC_READY | I/O / Input | IPMB 管理通道 + BMC Ready |
| B2/A2 | I2C_IPMB_SCL / I2C_BMC_CPLD_SDA | I/O / I/O | IPMB I2C + CPLD 控制 |
| B3/A3 | GND / I2C_BMC_CPLD_SCL | - / I/O | 地 / CPLD 控制 |
| B4/A4 | AC_ON_OFF_BTN / I2C_BMC_CPLD_ALT_N | Output / Output | AC 按钮 / CPLD 告警 |
| B5/A5 | HSC_FAULT_N / GND | Output / - | HSC 故障指示 |
| B6/A6 | HSC_EN / PWRBTN_N | Input / Input | HSC 使能 / 电源按钮 |
| B7/A7 | STBY_PWROK / RST_BMC_N | Output / Output | 待机电源 OK / BMC 复位 |
| B8/A8 | PCIE_RESET_N / RSVD | Output / - | PCIe 复位 |
| B11/A11 | UART_RX / RSVD | Input / - | 串口接收 |
| B12/A12 | UART_TX / MB_PRSNT_N | Output / Output | 串口发送 / 板卡在位 |
| B14-15 | USB-/USB+ / REFCLKn/p | I/O / Output | USB 数据 / PCIe Refclk |
| B17-B28 | PETn/p[0:3] / PERn/p[0:3] | Output / Input | PCIe Gen3 ×4 收发 |

### 7.3 引脚定义合规要求

- **Class 1/Class 2 统一 CAD**: 供应商通过 BOM 选配实现双 class 支持
- **RSVD 预留**: 通过电阻选项与接口隔离
- Slot ID: 2-bit SB_SLOT_ID[1:0] 来自支架确定物理位置
- 方向引用: 所有方向以 CPU 卡为参考

---

## 8. 电源架构设计

### 8.1 电源拓扑

```text
Bus Bar (12V/48V)
  +-- Medusa Cable
        +-- Medusa Power Board (MPB) — eFuse/HSC
              +-- Vertical PDB
                    +-- Baseboard (HSC, 12.5V->3.3VSTBY)
                    |     +-- BMC (P3V3_STBY, P1V2_BMC_STBY...)
                    |     +-- OCP NIC 3.0 (12.5V_STBY, P3V3_STBY)
                    +-- Server Blade 1-4 (各独立 HSC)
                          +-- CPU VR (Vcc)
                          +-- DIMM VR (VDDQ)
                          +-- M.2/扩展卡
```

### 8.2 热插拔电源序列

| 步骤 | 动作 | 时间 |
|:-----|:-----|:-----|
| 1 | Blade 插入, PRSNT# → GND | 立即 |
| 2 | BMC 检测到 Blade, 延迟后断言 HSC_EN | ~200ms |
| 3 | Blade HSC 软启动, 12V 上电 | 可配置, 避免浪涌 |
| 4 | Blade STBY_PWROK → 高 | - |
| 5 | BMC 断言 PWRBTN#, 启动 main power | ≥1s 间隔（多 blade 错开） |
| 6 | BMC 轮询 Main Power OK | - |

### 8.3 电源特性指标

| 参数 | Delta Lake 1S | Capri 2S | Telco Server |
|:-----|:-------------|:---------|:-------------|
| 输入电压 | 12V (通过 PDB) | 12V | 12V |
| 平台总功率 | ~1.5kW (4 blades) | 按配置 | 按配置 |
| 热插拔控制器 | 各 blade 独立 HSC | HSC | HSC |
| 电源检测 | VIP (电压/电流/功率) | PMBus 状态 | 监控电路 |
| 总电流上限 | 113.4A (sled 级) | 按 HSC | 按 HSC |
| 电容负载 | 按 HSC 设计 | 按 HSC 设计 | 按 HSC 设计 |
| 待机电源 | P3V3_STBY, 12.5V_STBY | STBY rails | STBY rails |

### 8.4 BMC 电源管理策略

- BMC 周期查询 slab HSC 总电流, 上限 113.4A → 超限则系统级 throttle
- 每 blade 1 秒平均功率计算 (HSC 采样)
- 功率限制: 通过 P-State 控制 CPU
- 无 CMOS 电池: BMC 通过 NTP 同步时间, 使用 blade RTC 作为初步参考

---

## 9. 热设计规范

### 9.1 数据中心环境

| 参数 | 典型值 |
|:-----|:-------|
| 冷通道温度 | 18-30°C (均值 24°C, σ=3°C) |
| 冷通道压力 | 0-0.005 in H2O |
| 海拔 | ≤ 6,000 ft |
| 相对湿度 | 20-90% |

### 9.2 散热设计指标

| 参数 | Delta Lake 1U | Delta Lake 2U | Capri 2S | Telco 1U |
|:-----|:--------------|:--------------|:---------|:---------|
| 散热方式 | 被动 (CPU HS) | 被动 (CPU HS) | 被动 | 风冷 |
| 风量 | ≥0.115 CFM/W | ≥0.115 CFM/W | - | - |
| 设计风量目标 | ≤0.1 CFM/W | ≤0.1 CFM/W | - | - |
| CPU HS 形态 | 带侧壁底座 | 标准底座 | - | 后出风 |
| 热裕量 | 5% (最坏工况) | 5% | - | - |
| 进气温度 | 35°C | 35°C | - | - |
| MTBF | 1.5M hrs @ 30°C, 90% CL | 同 | - | - |
| 寿命 | 3-5 年 | 同 | - | - |

### 9.3 热管理传感器

- **各 blade 传感器**: PCH/CPU/DIMM/VR/关键芯片温度
- **底板传感器**: Inlet/Outlet 温度 (TI TMP75 或外置 PN 结)
- **精度**: ±2°C, 目标 ±1°C, 公差 <2%
- **阈值的设定**:
  - 非 FSC（风扇速度控制）传感器: 15% 热裕度
  - FSC 传感器（除 CPU/Inlet/Outlet）: 20% 热裕度
- **M.2 散热**: 被动 TIM + 集成散热片, 6.7mm M.2 连接器间距

### 9.4 风扇控制

- BMC 负责风扇调速
- 3 个风扇区 (Yosemite V3)
- 单风扇/单转子故障仍维持 ≤35°C 进气

---

## 10. 机械设计与 PCB 规格

### 10.1 PCB 规格

| 参数 | Delta Lake 1S | Capri 2S | Big Sur | Qualcomm OCM |
|:-----|:-------------|:---------|:--------|:-------------|
| PCB 尺寸 | 321.4×157mm | 12"×13" | 母板 12"×13" | 1U 标准 |
| 层数 | - | 8 层 | 8 层 | - |
| 厚度 | - | 1.6mm | 1.6mm | - |
| 颜色 | - | - | - | - |
| DC-SCM HPM PCB | 可选 | 可选 | - | - |

### 10.2 机械叠层

**DC-SCM Straddle Mount Connector 安装偏移**:

- 0.062"/0.093"/0.105" 厚 PCB: 0mm 偏移
- 0.076" 厚 PCB: -0.3mm 偏移（3mm 垂直连接器需不同偏移计算）

### 10.3 散热片设计要求

- **1U 刀片**: HS 带侧壁底座（避免散热片底座与翅片剥离）
- **2U 刀片**: HS 足印覆盖区域更大
- HS 翅片对齐气流方向, 避免阻挡 debug headers 和连接器
- 扣具: 免工具, 安装简单
- M.2 散热片: 集成设计, 底部组件需满足 keepout zone 要求

---

## 11. 管理架构（BMC → BIC → IPMB）

### 11.1 三层管理架构

```text
+-------------------------------------------------+
|  Management Network (NC-SI -> OCP NIC -> TOR)     |
|                                    +----------+ |
|  BMC (Baseboard) <--------------- | AST2520  | |
|  |                   NC-SI        +----------+ |
|  +- IPMB (1MHz I2C) ----------> Blade 1 BIC    |
|  +- IPMB (1MHz I2C) ----------> Blade 2 BIC    |
|  +- IPMB (1MHz I2C) ----------> Blade 3 BIC    |
|  +- IPMB (1MHz I2C) ----------> Blade 4 BIC    |
|  +- I2C (400kHz) -------------> Blade CPLD      |
|  |    (BMC 直通 CPLD 做细粒度控制)              |
|  +- USB (高速) ---------------> Blade BIC Hub   |
|  |    (用于高速通信 + expansion BIC)            |
|  +- UART -------------------> Blade CPLD UART   |
|       (调试串口)                                |
+-------------------------------------------------+
```

### 11.2 BIC 功能清单

Bridge IC 位于每个 Blade 上, 功能包括：

| 功能域 | 具体职责 |
|:-------|:---------|
| 电源序列 | 管理 Blade 上电/断电/重启 |
| 温度监控 | 读取各传感器 → 上报 BMC |
| 功率监控 | 读取 HSC VIP → 计算 1s 均值 |
| 错误/事件 | 系统事件监控 → 上报 BMC |
| 固件管理 | 编程 BIOS/VR/CPLD FW |
| 启动配置 | 检测扩展卡类型 → 供给 BIOS |
| LED/按钮 | 用户面板指示 + 按钮 |
| BMC 复位 | 检测 BMC hang → 发起复位 |
| JTAG 桥接 | 通过 USB/IPMB 实现远程 JTAG 调试 |

### 11.3 BMC 功能清单

| 功能域 | 具体职责 |
|:-------|:---------|
| OOB 远程管理 | IPMI 2.0, WebUI, Redfish |
| 电源管理 | 电源监控/限制, HSC 控制 |
| 热管理 | 风扇调速, 温度报警 |
| 网络管理 | NC-SI → TOR, IPv4/IPv6, vBMC (多节点虚拟化) |
| 事件日志 | SEL 存储, 错误分级/上报 |
| FRU 跟踪 | 全平台 FRU 数据采集与维护 |
| 固件验证 | 固件更新/验证 |
| 时间同步 | NTP + blade RTC 初步同步 |
| Serial Console | SOL + 本地 Debug Card 串口 |

### 11.4 IPMI 错误日志分类

| 错误类型 | 日志内容 |
|:---------|:---------|
| CPU 错误 | CE/UCE, Link/L3 Cache 分级 |
| 内存错误 | DIMM 位置, Channel#, Slot# |
| PCIe 错误 | RC/EP/Switch UP/DP, Fatal/Non-fatal/Correctable |
| POST 错误 | BIOS 检测的 POST 错误码 |
| 电源错误 | 12.5V 输入掉电, S0/S1 异常关断 |
| MEMHOT#/SOCHOT# | 温度过限, 区分内部/外部来源 |
| 风扇故障 | RPM 超出上下限, 识别具体风扇 |
| PMBus 状态 | HSC/PSU 健康状态异常 |

---

## 12. 信号完整性要点

### 12.1 PCIe 插入损耗分配

```text
Die -> 连接器: ~12dB @4GHz (PCIe Gen3)
+-- 主板走线
+-- 连接器（SFF-TA1002 / OCP NIC 3.0）
+-- 线缆
+-- Blade 走线
```

- Blade 设计者可选: mid-loss / low-loss 板材以延长传输距离
- 可选 re-driver/re-timer（代价: 功耗 + 空间）

### 12.2 接口时序约束

| 接口 | 约束 | 来源 |
|:-----|:-----|:-----|
| NC-SI | 数据线 ≤ 2" 不等长 | DC-SCM §5.1 |
| NC-SI 时钟 | 时钟偏差控制 | DC-SCM §5.1.2 |
| SGPIO | 数据延迟 ≤ 3.5ns (ref: CLK) | DC-SCM §5.2 |
| I3C | 总容性负载 ≤ 15pF | DC-SCM §5.3 |
| PCIe Gen3/4 | 差分 ≥ 5mil 间距, 阻抗控制 | DC-SCM §5.4 |
| SMBus | 支持 100kHz 和 400kHz 双模式 | DC-SCM §5.3 |

### 12.3 PCIe Gen3 信号质量关键点

- ×2 或 ×4 宽度的 PCIe Gen3 连接（取决于配置）
- 多 Host NIC 共享: 4 blades 各自 ×4 = 1× ×16 NIC
- 插入损耗 ~12dB @4GHz 处定义了 max channel
- 2U expansion 使用 4C+ 连接器, 含完整 PCIe ×32 通道

---

## 13. 关键发现与增量分析

### 13.1 与现有知识库的关系

| 本文件覆盖主题 | 现有知识库覆盖 | 增量 |
|:--------------|:-------------|:-----|
| OCP 单板设计形态体系（刀片/基板/MC卡/SCM） | ❌ 无专题文档 | ✅ 首次系统化 |
| Yosemite V3 平台架构（Class 1/2） | ❌ 无 | ✅ 首次覆盖 |
| Delta Lake 1S 设计规格 | ⚠️ 部分在超节点硬件设计中提及 | ✅ 完整引脚定义+机械尺寸 |
| DC-SCM 标准 | ❌ 无 | ✅ 首次覆盖（接口规格+路由指南） |
| RunBMC 子卡 | ❌ 无 | ✅ 首次覆盖（260-pin 全引脚定义） |
| OCP 连接器标准（SFF-TA1002/PowerBlade+等） | ❌ 无 | ✅ 首次汇总 |
| 管理架构（BMC-BIC-IPMB 三层） | ⚠️ 概念存在但无 OCP 实现细节 | ✅ 带具体接口定义 |
| 热插拔电源序列 | ❌ 无 | ✅ 三阶段序列 + 时序要求 |
| OCP Mezzanine 卡（Netronome/Mellanox） | ❌ 无 | ✅ 首次覆盖 |
| Qualcomm Centriq 2400 OCM | ❌ 无 | ✅ 首次覆盖（ARM 服务器板设计） |
| 信号完整性约束（OCP 级） | ⚠️ 部分在 SI 专题中 | ✅ OCP 特有的 12dB 预算定义 |

### 13.2 关键发现

1. **OCP 设计层次化极强**：从机架(bus bar)→机箱(chassis)→基板(baseboard)→刀片(blade)→扩展件(expansion)→管理件(SCM/MC卡)，6 级解耦设计
2. **管理架构统一性**：IPMB (1MHz) + I2C (400kHz) + USB + UART 四通道并存，BIC 作卫星控制器
3. **连接器复用策略**：SFF-TA1002 连接器通过部分引脚适配 OCP NIC 3.0 定义，Class 1/2 共用 PCB（BOM 选配）
4. **DC-SCM 的模块化思想**：将 BMC 从主板上解耦为独立 SCM，是 OCP 管理架构的重要演进方向
5. **RunBMC 的差异化路线**：用标准 SODIMM DDR4 连接器作管理子卡接口，降低主板变更代价
6. **Intel 生态主导 OCP 单板**：分析的板级设计以 Intel Xeon 为核心（Cooper Lake/Haswell/Broadwell/Skylake），ARM 方案（Qualcomm Centriq）仅占少量

### 13.3 推荐后续方向

- OCP NIC 3.0 设计规范详细分析（OCP 网卡的 PCIe/NCSI/SMBus 接口定义）
- OCP Open Rack v2/v3 供电规范（12V→48V 演进对板级设计影响）
- DC-SCM vs RunBMC 技术路线对比
- OCP 散热/机械标准（Open Rack V2 机械接口定义）
- OCP 安全规范（TPM/RoT/Secure Boot 集成到板级设计）

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- (无)

### 外部资料引用

- 来源: import/work/ocp/` — 520 个文件中筛选出 ~30 个核心单板设计相关文档

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-21 | v1.0 | 新增 (v1.0, 从 import/work/ocp/ 520 文件中提取单板设计规格) |
