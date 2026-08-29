# AMD Family 17h (Zen) 芯片规格与技术要点

> **概要**: AMD Family 17h (Zen) 芯片规格，涵盖 APML 管理接口、PSP 安全架构与 RAS 体系
>
> **关键词**: AMD Zen · APML · PSP · RAS · PPR

---

## 📑 目录

- [1. 文件清单与分类](#1-文件清单与分类)
  - [1.1 源文件总览](#11-源文件总览)
  - [1.2 分类汇总](#12-分类汇总)
- [2. 平台管理接口：APML/SBI](#2-平台管理接口apmlsbi)
  - [2.1 总线特性](#21-总线特性)
  - [2.2 SBI 协议栈](#22-sbi-协议栈)
  - [2.3 SB-RMI 关键功能](#23-sb-rmi-关键功能)
  - [2.4 错误检测与恢复](#24-错误检测与恢复)
  - [2.5 APML v1 (2009) vs APML v2 (2018) 差异](#25-apml-v1-2009-vs-apml-v2-2018-差异)
- [3. 平台安全处理器：PSP 架构](#3-平台安全处理器psp-架构)
  - [3.1 PSP 系统架构](#31-psp-系统架构)
  - [3.2 关键功能](#32-关键功能)
  - [3.3 BIOS ↔ PSP 通信协议](#33-bios-psp-通信协议)
  - [3.4 安全解锁（HDT）](#34-安全解锁hdt)
- [4. RAS 体系架构（核心）](#4-ras-体系架构核心)
  - [4.1 AMD RAS 战略原则](#41-amd-ras-战略原则)
  - [4.2 错误报告架构](#42-错误报告架构)
    - [4.2.1 接口全景](#421-接口全景)
    - [4.2.2 PFEH 处理流程](#422-pfeh-处理流程)
  - [4.3 RAS 特性详解（10 大子系统）](#43-ras-特性详解10-大子系统)
    - [4.3.1 通用特性](#431-通用特性)
    - [4.3.2 CPU Core & Cache](#432-cpu-core-cache)
    - [4.3.3 Memory Controller & DRAM](#433-memory-controller-dram)
    - [4.3.4 Data Fabric & 互连](#434-data-fabric-互连)
    - [4.3.5 PCIe & NBIO](#435-pcie-nbio)
    - [4.3.6 S-Link 接口](#436-s-link-接口)
    - [4.3.7 System Management Network (SMN)](#437-system-management-network-smn)
    - [4.3.8 内部 PCIe 设备](#438-内部-pcie-设备)
  - [4.4 AGESA 固件 RAS 支持](#44-agesa-固件-ras-支持)
  - [4.5 CPM (Customer Platform Module) BIOS 实现](#45-cpm-customer-platform-module-bios-实现)
  - [4.6 配置启用汇总](#46-配置启用汇总)
- [5. RAS 错误注入验证](#5-ras-错误注入验证)
  - [5.1 RAS 错误注入工具 (56478)](#51-ras-错误注入工具-56478)
  - [5.2 测试环境要求](#52-测试环境要求)
  - [5.3 OS 配置要点](#53-os-配置要点)
  - [5.4 推荐注入模式](#54-推荐注入模式)
- [6. 编程参考：PPR 三卷结构](#6-编程参考ppr-三卷结构)
  - [6.1 卷分配](#61-卷分配)
  - [6.2 Vol 1 章节结构](#62-vol-1-章节结构)
  - [6.3 Vol 2 — NBIO 寄存器](#63-vol-2-nbio-寄存器)
  - [6.4 Vol 3 — FCH + 系统 Hub + 补充](#64-vol-3-fch-系统-hub-补充)
  - [6.5 寄存器访问方法](#65-寄存器访问方法)
- [7. 调试与诊断工具](#7-调试与诊断工具)
  - [7.1 BIOSDBG (56303)](#71-biosdbg-56303)
  - [7.2 HDT 安全解锁 (HDT_0_70/56069)](#72-hdt-安全解锁-hdt_0_7056069)
- [8. 增量分析与空白识别](#8-增量分析与空白识别)
  - [8.1 与现有知识库的关系](#81-与现有知识库的关系)
  - [8.2 KB 空白识别](#82-kb-空白识别)
  - [8.3 材料限制提醒](#83-材料限制提醒)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 1. 文件清单与分类

### 1.1 源文件总览

| # | 文件名 | 出版号 | 版本 | 日期 | 行数 | 分类 |
|:-|:-------|:-------|:----|:----|:---:|:-----|
| 1 | `41918_1_03.md` | 41918 | 1.03 | 2009-12 | 1,061 | 📡 APML 早期规范 |
| 2 | `55719_1.06.md` | 55719 | 1.06 | 2018-02 | 5,101 | 📡 APML Family 17h |
| 3 | `55758_1_07.md` | 55758 | 1.07 | 2018-11 | 5,483 | 🔒 PSP BIOS 架构 |
| 4 | `56278_0_90.md` | 56278 | 0.90 | 2018-09 | 12,835 | 🛡️ SP3 RAS 平台指南 |
| 5 | `56303_1_00.md` | 56303 | 1.00 | 2018-04 | 1,912 | 🔧 BIOSDBG 调试器 |
| 6 | `56478_0.71.md` | 56478 | 0.71 | 2018-11 | 1,339 | 🧪 RAS 错误注入工具 |
| 7 | `HDT_0_70.md` | 56069 | 0.70 | 2017-05 | 249 | 🔓 HDT 安全解锁 |
| 8 | `ppr_SSP_A0_nda_1.md` | 55803 | 0.75 | 2018-12 | 71,908 | 📘 PPR Vol 1 |
| 9 | `ppr_SSP_A0_nda_1_1.md` | 55803 | 0.75 | 2018-12 | 72,019 | 📘 PPR Vol 1 (副本) |
| 10 | `ppr_SSP_A0_nda_2.md` | 55803 | 0.75 | 2018-12 | 135,288 | 📘 PPR Vol 2 |
| 11 | `ppr_SSP_A0_nda_2_1.md` | 55803 | 0.75 | 2018-12 | 97,620 | 📘 PPR Vol 2 (副本) |
| 12 | `ppr_SSP_A0_nda_3.md` | 55803 | 0.75 | 2018-12 | 61,696 | 📘 PPR Vol 3 |
| 13 | `ppr_SSP_A0_nda_3_1.md` | 55803 | 0.75 | 2018-12 | 61,388 | 📘 PPR Vol 3 (副本) |

**注**: 带有 `_1` 后缀的文件与原卷内容略有长度差异（可能是不同导出版本或截断版本），但卷划分一致。

### 1.2 分类汇总

| 类别 | 文件 | 行数 | 核心主题 |
|:-----|:-----|:----:|:---------|
| 🛡️ **RAS** | 56278, 56478, PPR Vol1 Ch.3 | ~15,500 | RAS 特性定义、平台实现、寄存器编程、错误注入验证 |
| 📡 **APML/SBI** | 41918, 55719, PPR Vol1 Ch.8 | ~7,000 | 边带管理总线协议(100kHz-400kHz SMBus/I2C) |
| 🔒 **PSP/安全** | 55758, PPR Vol1 Ch.6 | ~5,500 | Platform Security Processor 与 Secure Boot |
| 🔧 **调试工具** | 56303, HDT_0_70 | ~2,200 | BIOS 源码级调试器、安全解锁 |
| 📘 **PPR 全册** | Vol 1/2/3 | ~269,000 | 寄存器级编程参考(RAS/CCX/SMN/NBIO/UMC/DF 等) |

---

## 2. 平台管理接口：APML/SBI

**高级平台管理链接 (APML)** 是 AMD 专用的边带管理总线协议，用于 BMC 与 CPU 之间的板级管理通信。

### 2.1 总线特性

| 参数 | 值 |
|:-----|:---|
| 物理层 | SMBus v1.0/v2.0 兼容, I²C 兼容 |
| 速率 | 100 kHz (标准) / 400 kHz (快速) |
| 地址 | 7-bit SMBus 地址: `0x3A` (写) / `0x3B` (读) |
| 拓扑 | SBI 总线, 多点共享 |
| 器件数 | 最多 4 个 SBI 设备 (CPU0/1 + SB-TSI × 2) |

### 2.2 SBI 协议栈

APML 定义了三层协议，层级递进：

```text
+-------------------------------------+
|  SB-RMI: 远程管理接口                |  <- 最常用, CPU 寄存器访问
|   - 读/写处理器寄存器                 |
|   - 读 CPUID                        |
|   - 读 Boot Code Status             |
|   - Mailbox 服务                    |
+-------------------------------------+
|  SB-TSI: 温度传感器接口               |  <- 板级温度监控
|   - 读取 CPU 温度传感器               |
+-------------------------------------+
|  SBI 传输层                          |  <- 物理传输
|   - Modified Block Write-Block Read  |
|   - 标准 SMBus 协议                  |
+-------------------------------------+
```

### 2.3 SB-RMI 关键功能

通过 `SBRMI` 寄存器空间访问 CPU 内部状态：

- **Processor State Access**: 读/写 x86 寄存器（MSR/PCI config/IO）
- **Mailbox Service**: 与 PSP/SMU 通信的邮箱机制
- **Boot Code Status**: 读取 PSP boot 状态码
- **Register Access**: 块读/写字节寄存器

### 2.4 错误检测与恢复

- **Error Detection**: CRC 错误、NACK 超时、总线冲突
- **Error Recovery**: 软件重试、总线复位、Pass-FET 隔离

### 2.5 APML v1 (2009) vs APML v2 (2018) 差异

| 特性 | v1 (41918) | v2 (55719, Family 17h) |
|:-----|:----------|:----------------------|
| 目标平台 | AMD 早期处理器 | Zen 架构 (Family 17h) |
| 协议结构 | SB-RMI + SB-TSI | SB-RMI + SB-TSI + Mailbox |
| 寄存器空间 | 基础 SBRMI 寄存器 | 扩展 SBRMI 寄存器(含 Mailbox) |
| SB-TSI | 基础温度读取 | 增强温度传感器 |
| 错误恢复 | 基础处理 | 详细错误检测与恢复流程 |

---

## 3. 平台安全处理器：PSP 架构

**Platform Security Processor (PSP)** 是 AMD 处理器中的专用安全协处理器，基于 ARM TrustZone 技术。

### 3.1 PSP 系统架构

```text
PSP 固件栈:
+--------------------------------------+
| PSP Secure OS (基于 TrustZone)        |
+--------------------------------------+
| PSP Boot Loader (ABL)                |
+--------------------------------------+
| On-chip PSP Boot ROM                 |  <- 硬编码, 不可更改
+--------------------------------------+

与 x86 BIOS 交互:
+--------------------------------------+
| BIOS (UEFI) <--> Mailbox <--> PSP       |
|   BIOS-to-PSP Mailbox Commands       |
|   PSP-to-BIOS Mailbox Commands       |
|   MP0_P2C_MSG 共享消息区              |
+--------------------------------------+
```

### 3.2 关键功能

| 功能 | 说明 |
|:-----|:------|
| **Platform Secure Boot** | 验证所有固件映像的签名链 |
| **fTPM (Firmware TPM)** | TPM 2.0 软件实现, 支持 TPM 1.2 兼容模式 |
| **AGESA 运行** | AMD 通用封装软件架构在 PSP 上运行 |
| **Crisis Recovery** | PSP 引导的灾难恢复路径（双 SPI 映像方案） |
| **BIOS 目录管理** | PSP Directory Table + BIOS Directory Table |
| **S3 Resume** | ACPI S3 恢复路径中的 PSP 角色 |

### 3.3 BIOS ↔ PSP 通信协议

- **BIOS-to-PSP**: 固件加载、密钥管理、平台配置
- **PSP-to-BIOS**: 安全事件通知、状态报告
- **Mailbox 命令**: 涵盖所有固件交互
- **Post Code**: PSP 引导阶段输出调试码

### 3.4 安全解锁（HDT）

生产芯片默认锁定安全状态。解锁流程：

1. NDA 账户 → AMD KDS (Key Distribution Server)
2. HDT 硬件调试器连接
3. 经互联网验证身份后解锁
4. 解锁后允许：内存转储、寄存器读写、错误注入

---

## 4. RAS 体系架构（核心）

**Socket SP3 RAS Platform Spec (56278)** 是 AMD Family 17h Models 30h-3Fh (Rome) 的官方 RAS 指南，12835 行，覆盖 10 大子系统 + AGESA 固件 + CPM 平台 BIOS 实现。

### 4.1 AMD RAS 战略原则

1. **RAS 是系统级特性** — 需要 CPU/固件/OS/平台 四方协作
2. **错误管理 vs 故障管理** — 处理错误症状 vs 修复根本原因
3. **分层错误报告** — 硬件 → 固件 → OS → 管理软件
4. **平台优先错误处理 (PFEH)** — 固件先于 OS 处理错误

### 4.2 错误报告架构

#### 4.2.1 接口全景

| 接口 | 类型 | 用途 | 层 |
|:-----|:-----|:-----|:--|
| **Legacy x86 MCA** | MSR 寄存器 | 基本 Machine Check 记录 | CPU |
| **AMD MCA Extensions (MCAX)** | 扩展 MSR | 增强的 MCA 信息 | CPU |
| **Platform First Error Handling (PFEH)** | 固件优先 | 固件拦截错误再通知 OS | 固件 |
| **PCIe AER** | PCIe Capability | PCIe 高级错误报告 | PCIe |
| **APML** | 边带总线 | BMC 通过 SBI 读取错误状态 | 管理 |

#### 4.2.2 PFEH 处理流程

```text
错误发生
  |
  +-- PFEH 关闭 -> OS MCA handler 直接处理
  |
  +-- PFEH 开启:
        |
        +-- 硬件错误 -> MCA bank 记录
        |     +-- Corrected -> 阈值统计 -> 超阈值通知固件
        |     +-- Uncorrected -> 立即通知固件
        |
        +-- 固件 (CPM SMM handler)
        |     +-- 错误登记 -> APEI (HEST/GHES)
        |     +-- 错误记录 -> ERST (NVRAM 持久化)
        |     +-- 错误注入支持 -> EINJ
        |     +-- Boot-time 错误 -> BERT
        |
        +-- OS
              +-- GHES (Generic Hardware Error Source)
              +-- dmesg/Event Viewer
```

### 4.3 RAS 特性详解（10 大子系统）

#### 4.3.1 通用特性

| 特性 | 说明 |
|:-----|:------|
| **FinFET 工艺** | 28nm→14nm FinFET 降低软错误率 (SER) |
| **MCA Thresholding** | 可编程错误阈值, 避免 CE 风暴淹没 OS |
| **MCA Recovery (MCA 恢复)** | 从可恢复错误中恢复执行, 无需重启 |
| **Data Poisoning** | 标记损坏数据, 传播给消费者时触发 MCA |
| **Sync Flood (系统致命错误)** | 不可恢复错误时内部同步屏障 |
| **Alert 信号** | MCE 紧急事件 / 致命事件告警引脚 |
| **Boot Status Indicator** | 引导阶段状态码输出 |

#### 4.3.2 CPU Core & Cache

| 特性 | 保护机制 | 纠正能力 |
|:-----|:---------|:---------|
| L1 Data Cache | **SEC-DED ECC** (64-bit data + 8-bit ECC) | 单纠双检 |
| L1 Data Tag | Parity + Retry | 检错重试 |
| L1 Data TLB | Parity + Retry | 检错重试 |
| L1 Instruction Cache | Parity + Retry | 检错重试 |
| L1 Instruction Tag | Parity + Retry | 检错重试 |
| L1 Instruction TLB | Parity + Retry | 检错重试 |
| L2 Cache Data | **DEC-TED ECC** (128-bit + 16-bit) | 双纠三检 |
| L2 Tag & State | SEC-DED ECC | 单纠双检 |
| L3 Cache Data | **DEC-TED ECC** (128-bit + 16-bit) | 双纠三检 |
| L3 Tag & State | SEC-DED ECC | 单纠双检 |
| CPU Core Array Parity | Parity | 检错 |
| CPU WD Timer | 超时检测 | 触发复位 |
| Boot-time Core Disable | 制造缺陷熔断 | 出厂前屏蔽 |
| Thermal Throttling | 温度触发降频 | 自我保护 |

**关键亮点**: L2/L3 数据阵列采用 **DEC-TED ECC**（双纠错三检错），这是 AMD 区别于 Intel（Intel L3 通常使用 SEC-DED）的显著优势。

#### 4.3.3 Memory Controller & DRAM

| 特性 | 保护机制 | 说明 |
|:-----|:---------|:-----|
| **DRAM ECC** | x4/x8/x16 符号编码 | x4: SSC-DSD, x16: 288-bit ECC word |
| **Corrected Error Counters** | 逐 UMC 计数器 | 跟踪 CE 率, 预测性维护 |
| **Bad Symbol ID** | 软件管理 | 标记故障 DRAM 颗粒 |
| **Patrol Scrubber** | 周期性巡检 | 主动发现并修正内存错误 |
| **Redirect Scrubber** | 重定向 scrub | 更正前转为备选行 |
| **Poison Scrubber** | 毒化数据扫描 | 扫描并清除毒化缓存行 |
| **Addr/Cmd Parity + Replay** | 奇偶 + 自动重发 | 保护地址/命令总线 |
| **Write Data CRC + Replay** | CRC + 自动重发 | 保护写入数据总线 |
| **Uncorrected ECC Retry** | 自动重试 | UE → 重读 → 可能变 CE |
| **Thermal Throttling** | 温度控制 | 高温降频保护 |
| **DDR4 Post Package Repair** | 冗余行替换 | 修复制造/老化缺陷 |
| **Row Hammer Protection** | 邻近行刷新 | 防止 Row Hammer 攻击 |
| **MC SRAM ECC** | SEC-DED | 内存控制器内部 SRAM 保护 |
| **MC Data Fabric Parity** | Parity | 内部数据路径保护 |

**ECC 符号大小对比**:

| 配置 | DRAM 类型 | ECC Word | 数据位 | 校验位 | 纠正能力 |
|:----|:---------|:--------|:-----|:------|:---------|
| x4 | x4 DRAM | 144-bit | 128 | 16 | SSC-DSD (36 个 4-bit 符号) |
| x8 | x8 DRAM | 144-bit | 128 | 16 | SSC-DSD (18 个 8-bit 符号) |
| x16 | x16 DRAM | 288-bit | 256 | 32 | SSC-DSD (18 个 16-bit 符号) |

#### 4.3.4 Data Fabric & 互连

| 特性 | 说明 |
|:-----|:------|
| **On-Chip Data Bus Parity** | 片内数据总线奇偶保护 |
| **On-Package Link CRC + Retry** | 片内跨 Die 互连 (GMI2) CRC + 重传 |
| **Off-Package Link CRC + Retry** | 跨 Socket 互连 (xGMI) CRC + 重传 |
| **Data Fabric WD Timer** | DF 超时检测, 防止死锁 |
| **System Probe Filter ECC** | 探针过滤器 ECC 保护 |
| **Link PHY Controller ECC** | PHY 控制器内部保护 |

#### 4.3.5 PCIe & NBIO

| 特性 | 说明 |
|:-----|:------|
| **NBIO/PCIE/NBIF Parity & ECC** | North Bridge IO 内部路径保护 |
| **Incoming Poison Handling** | 处理外部设备传入毒化数据 |
| **Poison Propagation** | 毒化数据在 PCIe 树中传播控制 |
| **eDPC (Enhanced Downstream Port Containment)** | 下游端口隔离 |
| **ECRC (End-to-end CRC)** | PCIe 端到端 CRC 校验 |
| **PCIe Hotplug** | 热插拔支持 |
| **NMI/Syncflood Pin** | 硬件紧急告警信号 |

#### 4.3.6 S-Link 接口

S-Link 是 AMD 专用接口（连接 FCH 等 South Bridge 设备）：

| 特性 | 说明 |
|:-----|:------|
| **Poison Propagation (to/from)** | S-Link 设备间毒化数据传递 |
| **Read Response Errors** | 读响应错误处理 |
| **Write Response Errors** | 写响应错误处理 |
| **Protocol Error Messages** | 协议层错误消息 |

#### 4.3.7 System Management Network (SMN)

| 特性 | 说明 |
|:-----|:------|
| **SMN Parity** | SMN 网络奇偶保护 |
| **Off-Package Link CRC + Retry** | 跨芯片 SMN 链路保护 |
| **On-Package Link CRC + Retry** | 片内 SMN 链路保护 |
| **SMN Timeouts** | 超时检测 |
| **SMU Parity & ECC** | SMU 内部存储保护 |
| **MP5 Parity & ECC** | MP5 协处理器保护 |
| **PSP Parity & ECC** | PSP 安全处理器保护 |
| **Parameter Block ECC** | 参数块 ECC 保护 |

#### 4.3.8 内部 PCIe 设备

| 特性 | 目标 |
|:-----|:-----|
| **SATA Parity** | Serial ATA 控制器数据路径 |
| **USB ECC** | USB 控制器内部保护 |
| **SMU/PSP/PTDMA WD Timers** | 系统管理单元 Watchdog |
| **FCH Boot Timer** | Fusion Controller Hub 引导超时 |
| **FCH WD Timer** | FCH 通用 Watchdog |
| **FCH A-Link Parity** | FCH 与 CPU 的 A-Link 接口保护 |

### 4.4 AGESA 固件 RAS 支持

| 功能 | 说明 |
|:-----|:------|
| **APEI (ACPI Platform Error Interfaces)** | ACPI 表: HEST/GHES/BERT/ERST/EINJ |
| **FCH SMI Handler** | 系统管理中断处理 |
| **DRAM MCA Address Translation** | DRAM 地址 ←→ MCA 物理地址转换 |
| **ECC Symbol to DRAM Device Translation** | ECC 符号 → 具体 DRAM 颗粒映射 |
| **Error Injection on Secure Parts** | 经 AMD KDS 解锁后支持安全部件的错误注入 |
| **Memory Tester** | AGESA 内置内存测试器 |
| **DDR4 Post Package Repair** | 引导时存储后封装修复配置 |
| **MCA Master Core Setup** | MCA 主核配置 |
| **MCA Re-init for UMC LP Mode** | UMC 低功耗模式下 MCA 重初始化 |

### 4.5 CPM (Customer Platform Module) BIOS 实现

| 阶段 | 关键操作 |
|:-----|:---------|
| **PCD/APCB Settings** | RAS 特性开关配置 (>50 个 PCD token) |
| **PEI (Pre-UEFI)** | 硬件初始化、PPR 配置、MCA 基础设置 |
| **DXE (Driver Execution)** | 错误轮询、CDD/CPM 初始化、PFEH 设置 |
| **SMM (System Management Mode)** | 错误捕获、APEI 表更新、FCH SMI 处理 |

重要 PCD 配置示例:

- `PcdAmdMemEccEnable` — DRAM ECC 使能
- `PcdAmdMemEccSymbolSize` — ECC 符号大小 (x4/x8/x16)
- `PcdAmdPlatformFirstErrorHandling` — PFEH 开关
- `PcdAmdMemDataPoisoningEnable` — 数据毒化使能
- `PcdAmdMemEccRetryEnable` — UE 重试使能

### 4.6 配置启用汇总

| 特性大类 | 特性数 | 需求 BIOS 配置 | 需求 CPU 支持 |
|:---------|:-----:|:--------------:|:------------:|
| 错误报告接口 | 5 | ✅ | ✅ |
| 通用特性 | 7 | ✅(部分) | ✅ |
| CPU Core & Cache | 14 | — | ✅(内置) |
| Memory Controller & DRAM | 14 | ✅(大部分) | ✅ |
| Data Fabric & Links | 6 | — | ✅ |
| PCIe & NBIO | 7 | ✅(部分) | ✅ |
| 内部 PCIe | 6 | — | ✅ |
| S-Link | 5 | — | ✅ |
| SMN & SMU | 9 | ✅(部分) | ✅ |
| AGESA 固件 | 10 | ✅ | ✅ |

---

## 5. RAS 错误注入验证

### 5.1 RAS 错误注入工具 (56478)

**AMD RAS Error Injection Tool v1.4.2** 是验证平台 RAS 响应的官方工具，支持 5 大注入类型：

| 注入类型 | 目标 | 注入模式 | 工具检测方式 |
|:---------|:-----|:---------|:------------|
| **DRAM ECC** | 内存控制器 | Explicit/Implicit(Persistent)/One-Shot | OS dmesg/Event Viewer |
| **NBIO IOHUB** | North Bridge IO hub | Parity/ECC CE/UE/UCP | OS 事件日志 |
| **NBIO nBIF** | North Bridge Interconnect Fabric | Parity CE/UE | OS 事件日志 |
| **SMU/PSP** | 系统管理单元/安全处理器 | Parity CE/UE | OS 事件日志 |
| **GMI2/xGMI2** | Die间/跨Socket互连 | CRC CE | OS 事件日志 |

### 5.2 测试环境要求

- **SUT OS**: CentOS 7.5 / Ubuntu 18.04
- **BIOS**: RomePI_SP3 0.0.6.1+
- **工具**: RAS Error Injection Tool v1.4.2
- **CPU**: 解锁状态 (Secure Unlock via HDT)
- **内存**: ECC R-DIMM

### 5.3 OS 配置要点

```bash
# Linux: 禁用内核 CE 聚合器
grubby --update-kernel=ALL --args="ras=cec_disable"

# Linux: 设置轮询间隔为 1s
echo 1 > /sys/devices/system/machinecheck/machinecheck0/check_interval
```

### 5.4 推荐注入模式

> **AMD 明确推荐使用 Explicitly Addressed (Coherent) Injection** 进行大多数平台测试，因为其结果最具可预测性。Implict (Persistent/One-Shot) 作为备选调试方案。

---

## 6. 编程参考：PPR 三卷结构

**PPR (Processor Programming Reference)** 是 AMD 最底层的寄存器级编程手册，针对 Family 17h Model 30h A0 步进。

### 6.1 卷分配

| 卷 | 章节 | 寄存器类型 | 行数 |
|:--|:-----|:----------|:----:|
| **Vol 1** | Ch.1-11 | MSR + 部分 SMN | ~72K |
| **Vol 2** | Ch.12 | PCICFG (NBIO) | ~135K |
| **Vol 3** | Ch.13-16 | SMN + 补充 + 内存映射 | ~62K |

### 6.2 Vol 1 章节结构

| 章 | 标题 | 核心内容 |
|:--|:-----|:---------|
| 1 | Overview | 文档约定、寄存器格式、访问方法(MSR/PCICFG/BAR/Data Port) |
| 2 | Core Complex (CCX) | Zen 核心复杂体寄存器 |
| **3** | **RAS Features** | **MCA 架构、数据毒化、PFEH、CPU/DF/DRAM/PCIe/NBIO/NBIF RAS 寄存器** |
| 4 | System Management Network (SMN) | SMN 总线协议与地址映射 |
| 5 | Remote System Management Unit (RSMU) | 远程管理单元寄存器 |
| 6 | Security | 安全特性寄存器 |
| 7 | System Management Unit (SMU) | SMU 控制寄存器 |
| 8 | Advanced Platform Management Link (APML) | APML/SBI 相关寄存器 |
| 9 | SB Temperature Sensor Interface (SB-TSI) | 温度传感器接口 |
| 10 | Data Fabric | 数据面配置寄存器 |
| 11 | UMC | Unified Memory Controller 寄存器 |

### 6.3 Vol 2 — NBIO 寄存器

Ch.12 Northbridge IO (NBIO) 是最大的一章，涵盖：

- PCIe Root Port 配置空间
- NBIO 内部寄存器
- IOMMU/SMMU 寄存器
- DxIO (PCIe 控制器) 寄存器
- SMU 与 PSP 通信接口

### 6.4 Vol 3 — FCH + 系统 Hub + 补充

| 章 | 标题 | 内容 |
|:--|:-----|:-----|
| 13 | FCH | Fusion Controller Hub 寄存器 |
| 14 | System Hub (SYSHUB) | 系统 Hub 寄存器 |
| 15 | DXIO | 多路 PCIe I/O 控制器 |
| 16 | Miscellaneous Information | 补充信息 |
| — | Memory Maps | MSR/Main Memory/PCICFG/SMN/SMNCCD/MP0/MP1 |

### 6.5 寄存器访问方法

| 方法 | 适用范围 | 典型用途 |
|:-----|:---------|:---------|
| **MSR** (Model-Specific Register) | x86 核心 | MCA 寄存器, 性能计数器 |
| **PCICFG** (PCI Configuration) | NBIO, PCIe | PCIe 扩展配置空间, AER |
| **SMN** (System Management Network) | SMU, PSP, DF | 内部管理寄存器 |
| **BAR** (Base Address Register) | 特定 IP | 设备特定寄存器 |
| **Data Port** | UMC, DF | 批量数据访问 |

---

## 7. 调试与诊断工具

### 7.1 BIOSDBG (56303)

AMD BIOSDBG Rev 2.0 是 UEFI 源码级调试工具：

| 功能 | 说明 |
|:-----|:------|
| **目标平台** | Family 17h (Zen), 通过 SimNow 仿真器或 Wombat 硬件 |
| **断点** | 硬件断点、软件断点 |
| **内存操作** | Dump/Modify, 文件导入导出 |
| **寄存器** | GPR/PCI/MSR/MTRR/IO |
| **MCA** | 读取 MCA 错误寄存器 |
| **CMOS** | 读/写/清除 |
| **PState** | 处理器性能状态读取 |
| **反汇编** | Unassemble Memory |

### 7.2 HDT 安全解锁 (HDT_0_70/56069)

- **工具**: AMD Hardware Debug Tool (HDT15)
- **目的**: 解锁安全熔断的处理器以允许调试和错误注入
- **流程**: NDA 账户 → KDS 服务器认证 → HDT 连接 → 解锁
- **要求**: 主机须联网访问 `nda.amd.com`

---

## 8. 增量分析与空白识别

### 8.1 与现有知识库的关系

| 现有 KB 文档 | 与 AMD 材料的关系 |
|:-------------|:-----------------|
| `base/2026-06-25-chip-init-recovery-framework.md` (170KB) | 部分重叠(芯片初始化原理), AMD 材料提供 Zen 架构具体实现(APML/PFEH/SP3 RAS) |
| `base/2026-07-01-chip-four-categories-rd-process.md` (65KB) | 低重叠(通用芯片研发流程), AMD 材料不涉及通用流程 |
| `base/2026-07-02-riscv-debug-diagnostic-report.md` | 低重叠(不同指令集架构) |
| `03_hardware/07_ras/2026-07-21-import-ras-extraction.md` | **高度互补**: 该文档覆盖多厂商 RAS, AMD 材料是其中 AMD 部分的主要原始参考 |
| `03_AI/` 任何文档 | 无重叠 |
| `01_survey/` 任何文档 | 无重叠 |

### 8.2 KB 空白识别

| 空白主题 | 重要性 | 材料可用性 | 建议 |
|:---------|:------|:----------|:-----|
| AMD EPYC RAS 全景对比（Naples→Rome→Milan→Genoa 演进） | ⭐⭐⭐ | 含 Rome 级参考, 可推断演进方向 | 已有 `56278` 做 Rome 级基准 |
| AMD PPR 寄存器级分析（选重要 RAS 寄存器深度解析） | ⭐⭐ | 大量原始材料 (270K+ 行) | 按需专题化，非普适需求 |
| AMD vs Intel RAS 全维度对比 | ⭐⭐⭐ | 需结合 Intel 材料 | 可作独立专题 |
| AMD 服务器平台 BMC 集成（APML → IPMI/Redfish 桥接） | ⭐⭐⭐ | 含 APML 详细协议 | 适合服务器设计专题 |
| AMD UMC (Unified Memory Controller) 深度分析 | ⭐⭐ | PPR Ch.11 可用 | 含 ECC/Scrubber/PPR 细节 |
| AMD SMN (System Management Network) 架构 | ⭐⭐ | PPR Ch.4 + Ch.8 可用 | 与 Intel PECI/ NC-SI 形成对比 |

### 8.3 材料限制提醒

1. **时序**: 所有文档基于 2017-2018 年 (Zen 2/Rome 时代)，不覆盖 Zen 3/4/5 的新增特性
2. **NDA**: 原始材料标记 "AMD Confidential — Advance Information"，不可公开引用
3. **寄存器级**: PPR 三卷 ~270K 行是详尽的寄存器列表，本文只提炼架构，具体编程细节以原始 PPR 为准
4. **版本**: PPR Rev 0.75 是 Preliminary (预发布)，非最终正式版本

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
| 2026-07-21 | v1.0 | 初始创建，从 `import/work/amd/` 13 个文件提炼规格与技术要点 |
