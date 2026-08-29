# ACPI 6.0 标准规范

> **概要**: ACPI 6.0标准规范定义、目标与系统描述表
>
> **关键词**: ACPI · ACPI 6.0 · 系统描述表 · 电源管理 · 配置接口

---

## 📑 目录

- [1. ACPI概述](#1-acpi概述)
  - [1.1 ACPI定义](#11-acpi定义)
  - [1.2 ACPI目标](#12-acpi目标)
  - [1.3 ACPI 6.0关键更新](#13-acpi-60关键更新)
- [2. ACPI系统描述表](#2-acpi系统描述表)
  - [2.1 表结构概述](#21-表结构概述)
  - [2.2 FADT表](#22-fadt表)
  - [2.3 MADT表](#23-madt表)
- [3. ACPI命名空间](#3-acpi命名空间)
  - [3.1 命名空间结构](#31-命名空间结构)
  - [3.2 预定义对象](#32-预定义对象)
- [4. 电源管理](#4-电源管理)
  - [4.1 全局电源状态](#41-全局电源状态)
  - [4.2 设备电源状态](#42-设备电源状态)
  - [4.3 处理器电源状态](#43-处理器电源状态)
  - [4.4 性能状态](#44-性能状态)
- [5. 热管理](#5-热管理)
  - [5.1 热管理模型](#51-热管理模型)
  - [5.2 热传感器](#52-热传感器)
- [6. 设备配置](#6-设备配置)
  - [6.1 资源描述符](#61-资源描述符)
  - [6.2 资源分配](#62-资源分配)
- [7. ACPI控制方法](#7-acpi控制方法)
  - [7.1 ASL语言](#71-asl语言)
  - [7.2 常用控制方法](#72-常用控制方法)
- [8. ARM平台特殊考虑](#8-arm平台特殊考虑)
  - [8.1 ACPI vs FDT](#81-acpi-vs-fdt)
  - [8.2 ARM特定表](#82-arm特定表)
  - [8.3 PSCI支持](#83-psci支持)
- [9. ACPI合规要求](#9-acpi合规要求)
  - [9.1 平台合规](#91-平台合规)
  - [9.2 OSPM合规](#92-ospm合规)
- [10. 最佳实践](#10-最佳实践)
  - [10.1 ACPI表设计](#101-acpi表设计)
  - [10.2 电源管理优化](#102-电源管理优化)
  - [10.3 调试与验证](#103-调试与验证)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 1. ACPI概述

### 1.1 ACPI定义

ACPI（Advanced Configuration and Power Interface）是一种开放标准，用于操作系统与平台固件之间的电源管理和配置接口。

### 1.2 ACPI目标

- 提供统一的电源管理接口
- 支持设备即插即用配置
- 实现操作系统控制的电源管理
- 支持热插拔和设备管理

### 1.3 ACPI 6.0关键更新

ACPI 6.0版本包含以下重要更新：

- 支持持久内存S4行为
- 支持ARM GICv3/4 ITS
- 支持PCIe 4.0电源管理
- 支持低功耗空闲状态
- 支持Platform Communications Channel (PCC)
- 支持Collaborative Processor Performance Control (CPPC)

## 2. ACPI系统描述表

### 2.1 表结构概述

ACPI通过系统描述表（System Description Tables）提供硬件配置信息。主要表包括：

| 表签名 | 表名称 | 描述 |
|:-------|:-------|:-----|
| RSDP | Root System Description Pointer | 指向RSDT/XSDT的指针 |
| RSDT | Root System Description Table | 32位系统描述表 |
| XSDT | Extended System Description Table | 64位系统描述表 |
| FADT | Fixed ACPI Description Table | 固定硬件描述表 |
| FACS | Firmware ACPI Control Structure | 固件ACPI控制结构 |
| MADT | Multiple APIC Description Table | 多APIC描述表 |
| SRAT | System Resource Affinity Table | 系统资源亲和性表 |
| SLIT | System Locality Distance Information Table | 系统位置距离信息表 |
| CPEP | Corrected Platform Error Polling Table | 修正平台错误轮询表 |
| MSCT | Maximum System Characteristics Table | 最大系统特性表 |
| RASF | ACPI RAS Feature Table | ACPI RAS特性表 |
| MPST | Memory Power State Table | 内存电源状态表 |
| BGRT | Boot Graphics Resource Table | 启动图形资源表 |
| FPDT | Firmware Performance Data Table | 固件性能数据表 |
| GTDT | Generic Timer Description Table | 通用定时器描述表 |
| NFIT | NVDIMM Firmware Interface Table | NVDIMM固件接口表 |

### 2.2 FADT表

FADT（Fixed ACPI Description Table）定义了固定硬件特性，包括：

- 电源管理寄存器地址
- 系统控制中断（SCI）信息
- 睡眠状态支持
- 硬件特性标志

### 2.3 MADT表

MADT（Multiple APIC Description Table）描述了中断控制器配置，包括：

- 本地APIC信息
- I/O APIC信息
- 中断源覆盖
- NMI配置
- 本地APIC地址覆盖
- 本地APIC NMI
- x2APIC信息
- GIC信息（ARM平台）

## 3. ACPI命名空间

### 3.1 命名空间结构

ACPI命名空间是一个分层的树形结构，根节点为`\_SB`（System Bus），包含以下主要节点：

- `\_SB`：系统总线
- `\_AC`：ACPI控制器
- `\_AF`：ACPI固件
- `\_PR`：处理器
- `\_SB.PCI0`：PCI总线

### 3.2 预定义对象

ACPI定义了大量预定义对象，用于设备配置和电源管理：

- `_ADR`：设备地址
- `_HID`：硬件ID
- `_CID`：兼容ID
- `_CRS`：当前资源设置
- `_PRS`：可能的资源设置
- `_SRS`：设置资源
- `_STA`：设备状态
- `_DSM`：设备特定方法

## 4. 电源管理

### 4.1 全局电源状态

ACPI定义了全局系统电源状态（S0-S5）：

- **S0**：工作状态
- **S1**：睡眠状态，CPU停止执行
- **S2**：深度睡眠状态，CPU和缓存关闭
- **S3**：挂起到RAM，内存保持供电
- **S4**：挂起到磁盘，所有设备关闭
- **S5**：软关机，完全断电

### 4.2 设备电源状态

设备电源状态（D0-D3）：

- **D0**：完全开启
- **D1**：低功耗状态
- **D2**：更低功耗状态
- **D3hot**：关闭但电源仍存在
- **D3cold**：完全关闭

### 4.3 处理器电源状态

处理器电源状态（C0-Cn）：

- **C0**：运行状态
- **C1**：停止时钟
- **C2**：停止CPU内部时钟
- **C3**：深度睡眠，缓存刷新

### 4.4 性能状态

性能状态（P0-Pn）：

- **P0**：最高性能
- **Pn**：逐级降低性能，降低功耗

## 5. 热管理

### 5.1 热管理模型

ACPI热管理包括：

- 主动冷却：通过风扇调节
- 被动冷却：通过降频调节
- 热区管理：多个热区的独立管理

### 5.2 热传感器

热传感器提供温度监测，包括：

- 温度阈值设置
- 过热告警
- 冷却策略触发

## 6. 设备配置

### 6.1 资源描述符

ACPI使用资源描述符描述设备资源需求，包括：

- 内存资源
- I/O资源
- 中断资源
- DMA资源

### 6.2 资源分配

操作系统通过以下方法进行资源分配：

- `_CRS`：获取当前资源设置
- `_PRS`：获取可能的资源设置
- `_SRS`：设置资源配置

## 7. ACPI控制方法

### 7.1 ASL语言

ACPI控制方法使用ASL（ACPI Source Language）编写，编译为AML（ACPI Machine Language）执行。

### 7.2 常用控制方法

- `_INI`：初始化设备
- `_REG`：注册操作区域
- `_DSM`：设备特定方法
- `_BBN`：设置总线号
- `_SEG`：设置段号

## 8. ARM平台特殊考虑

### 8.1 ACPI vs FDT

ARM平台支持两种配置方式：

- **ACPI**：符合PC架构的标准配置
- **FDT（Flattened Device Tree）**：ARM传统配置方式

### 8.2 ARM特定表

ARM平台需要的特定ACPI表：

- GTDT：通用定时器描述表
- MADT/GICC：GIC控制器描述
- IORT：I/O路由表
- SPCR：串行端口控制台重定向表

### 8.3 PSCI支持

ARM平台通过PSCI（Power State Coordination Interface）实现电源管理，需要在FADT中声明。

## 9. ACPI合规要求

### 9.1 平台合规

平台必须：

- 正确实现所有必需的ACPI表
- 提供完整的命名空间
- 支持所需的电源管理特性
- 遵循ACPI规范的时序要求

### 9.2 OSPM合规

操作系统电源管理（OSPM）必须：

- 正确解析ACPI表
- 实现电源管理策略
- 支持设备即插即用
- 处理热事件和电源事件

## 10. 最佳实践

### 10.1 ACPI表设计

- 使用最新版本的ACPI规范
- 确保表结构正确
- 提供完整的设备信息
- 遵循命名规范

### 10.2 电源管理优化

- 合理配置睡眠状态
- 优化设备电源状态转换
- 使用CPPC进行性能调节
- 实现低功耗空闲状态

### 10.3 调试与验证

- 使用ACPI调试工具
- 验证表的正确性
- 测试电源管理功能
- 确保热管理正常工作

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
| 2026-07-24 | v1.0 | 初始版本 |
