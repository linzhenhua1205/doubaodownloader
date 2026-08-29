# 芯片设计基础 — import/work 归档

> **概要**: (待补充)
>
> **关键词**: (待补充)

---

## 📑 目录

- [1. 概述](#1-概述)
- [2. AMBA 片上互连架构](#2-amba-片上互连架构)
  - [2.1 AMBA AXI4 协议 v2.0](#21-amba-axi4-协议-v20)
    - [2.1.1 协议架构](#211-协议架构)
    - [2.1.2 突发传输（Burst）](#212-突发传输burst)
    - [2.1.3 原子访问与锁定](#213-原子访问与锁定)
    - [2.1.4 低功耗接口](#214-低功耗接口)
    - [2.1.5 顺序与乱序规则](#215-顺序与乱序规则)
    - [2.1.6 芯片设计关键参数](#216-芯片设计关键参数)
  - [2.2 AMBA 3 AHB-Lite 协议](#22-amba-3-ahb-lite-协议)
    - [2.2.1 AHB-Lite vs AHB 差异](#221-ahb-lite-vs-ahb-差异)
    - [2.2.2 AHB-Lite 传输协议](#222-ahb-lite-传输协议)
    - [2.2.3 突发传输（AHB-Lite）](#223-突发传输ahb-lite)
    - [2.2.4 AHB-Lite 芯片实现要点](#224-ahb-lite-芯片实现要点)
- [3. MIPS 处理器架构](#3-mips-处理器架构)
  - [3.1 MIPS32 ISA 概览](#31-mips32-isa-概览)
    - [3.1.1 指令格式](#311-指令格式)
    - [3.1.2 芯片设计约束](#312-芯片设计约束)
    - [3.1.3 CP0 — 系统协处理器](#313-cp0-系统协处理器)
  - [3.2 MIPS64 指令集架构](#32-mips64-指令集架构)
    - [3.2.1 MIPS64 核心特性](#321-mips64-核心特性)
    - [3.2.2 Release 6 架构增强（芯片设计影响）](#322-release-6-架构增强芯片设计影响)
  - [3.3 MIPS64 特权资源架构](#33-mips64-特权资源架构)
    - [3.3.1 特权层级](#331-特权层级)
    - [3.3.2 TLB 架构](#332-tlb-架构)
    - [3.3.3 异常处理机制](#333-异常处理机制)
  - [3.4 MIPS 多核缓存一致性方案](#34-mips-多核缓存一致性方案)
    - [3.4.1 基于 OCP 的 Snoop 一致性架构](#341-基于-ocp-的-snoop-一致性架构)
    - [3.4.2 MESI 协议实现](#342-mesi-协议实现)
    - [3.4.3 Coherence 消息流](#343-coherence-消息流)
    - [3.4.4 多集群扩展](#344-多集群扩展)
- [4. MIPS I6400/I6500 多处理器系统](#4-mips-i6400i6500-多处理器系统)
  - [4.1 I6500 系统架构与特性](#41-i6500-系统架构与特性)
    - [4.1.1 核心架构参数](#411-核心架构参数)
    - [4.1.2 I6500 系统级特性](#412-i6500-系统级特性)
    - [4.1.3 多集群配置](#413-多集群配置)
    - [4.1.4 I6500 Pipeline 架构](#414-i6500-pipeline-架构)
  - [4.2 I6500 内存管理单元](#42-i6500-内存管理单元)
    - [4.2.1 TLB 层次](#421-tlb-层次)
    - [4.2.2 页面大小支持](#422-页面大小支持)
    - [4.2.3 共享 FTLB 机制（I6500 增强）](#423-共享-ftlb-机制i6500-增强)
  - [4.3 I6500 缓存子系统](#43-i6500-缓存子系统)
    - [4.3.1 缓存参数](#431-缓存参数)
    - [4.3.2 L1 D-Cache 双端口设计](#432-l1-d-cache-双端口设计)
    - [4.3.3 缓存一致性协议](#433-缓存一致性协议)
- [5. ASPEED BMC SoC](#5-aspeed-bmc-soc)
  - [5.1 AST2050/AST1100 SoC](#51-ast2050ast1100-soc)
    - [5.1.1 芯片基本信息](#511-芯片基本信息)
    - [5.1.2 芯片级功能模块](#512-芯片级功能模块)
    - [5.1.3 电源上电时序](#513-电源上电时序)
    - [5.1.4 封装与引脚](#514-封装与引脚)
  - [5.2 AST2500 系列](#52-ast2500-系列)
    - [5.2.1 已知规格](#521-已知规格)
- [6. 片上接口与总线标准](#6-片上接口与总线标准)
  - [6.1 eSPI 接口规范](#61-espi-接口规范)
    - [6.1.1 eSPI 基本参数](#611-espi-基本参数)
    - [6.1.2 eSPI 通道类型](#612-espi-通道类型)
    - [6.1.3 芯片设计关键参数](#613-芯片设计关键参数)
    - [6.1.4 Server Addendum 差异](#614-server-addendum-差异)
  - [6.2 DDR2 SDRAM 标准](#62-ddr2-sdram-标准)
    - [6.2.1 DDR2 关键参数](#621-ddr2-关键参数)
    - [6.2.2 芯片级设计约束](#622-芯片级设计约束)
    - [6.2.3 初始化序列](#623-初始化序列)
    - [6.2.4 芯片设计注意事项](#624-芯片设计注意事项)
  - [6.3 LPC 总线](#63-lpc-总线)
- [7. 固件与平台初始化架构](#7-固件与平台初始化架构)
  - [7.1 Intel FSP 架构 v2.0](#71-intel-fsp-架构-v20)
    - [7.1.1 FSP 架构](#711-fsp-架构)
    - [7.1.2 FSP 芯片设计接口](#712-fsp-芯片设计接口)
    - [7.1.3 芯片集成约束](#713-芯片集成约束)
  - [7.2 UEFI PI 规范 v1.7](#72-uefi-pi-规范-v17)
    - [7.2.1 PI 阶段（SEC/PEI/DXE/BDS）](#721-pi-阶段secpeidxebds)
    - [7.2.2 PEI 核心 — Boot Mode 与 HOB](#722-pei-核心-boot-mode-与-hob)
    - [7.2.3 芯片级接口（SEC/PEI）](#723-芯片级接口secpei)
  - [7.3 UEFI 安全启动与芯片级安全](#73-uefi-安全启动与芯片级安全)
    - [7.3.1 Secure Boot 流程](#731-secure-boot-流程)
    - [7.3.2 Intel Boot Guard](#732-intel-boot-guard)
    - [7.3.3 芯片级威胁防护](#733-芯片级威胁防护)
- [8. 芯片安全架构](#8-芯片安全架构)
  - [8.1 Arm Server Base Security Guide](#81-arm-server-base-security-guide)
    - [8.1.1 安全基线](#811-安全基线)
    - [8.1.2 芯片安全架构要求](#812-芯片安全架构要求)
    - [8.1.3 DRTM (Dynamic Root of Trust for Measurement)](#813-drtm-dynamic-root-of-trust-for-measurement)
  - [8.2 芯片级可信启动](#82-芯片级可信启动)
    - [8.2.1 信任根链（参考 UEFI + Arm SBSG）](#821-信任根链参考-uefi-arm-sbsg)
    - [8.2.2 芯片硬件安全特性对照](#822-芯片硬件安全特性对照)
- [9. 增量分析](#9-增量分析)
  - [9.1 与现有知识库对比](#91-与现有知识库对比)
  - [9.2 关键发现](#92-关键发现)
  - [9.3 推荐方向](#93-推荐方向)
- [changelog](#changelog)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 1. 概述

本文覆盖 `import/work/` 中六类芯片设计核心材料，按"架构标准→处理器内核→SoC→接口协议→固件→安全"的芯片设计层次组织，形成从片上互连到系统集成的完整知识链路。

| 分类 | 源文件数 | 覆盖深度 |
|:-----|:--------:|:--------|
| AMBA 片上互连 | 2 | AXI4 v2.0 / AHB-Lite 完整协议规范 |
| MIPS 处理器架构 | 6 | ISA / 特权架构 / 多核一致性 / I6500 系统 |
| ASPEED BMC SoC | 3 | AST2050 寄存器级 / AST2500/AST2600 |
| 片上接口标准 | 3 | eSPI / DDR2 / LPC |
| 固件/平台初始化 | 3 | FSP / PI / UEFI 安全启动 |
| 芯片安全 | 1 | Arm SBSG 安全基线 |

---

## 2. AMBA 片上互连架构

### 2.1 AMBA AXI4 协议 v2.0

**源**: `import/work/amba_axi4.md` | ARM IHI 0022C | 8996 行 | 2010

AMBA AXI（Advanced eXtensible Interface）是 ARM 开发的片上系统总线协议标准，本文基于 v2.0 版本。

#### 2.1.1 协议架构

| 通道 | 方向 | 信号组数 | 关键信号 |
|:-----|:-----|:--------:|:---------|
| **读地址** (AR) | Master→Slave | 10 | ARID[3:0], ARADDR[31:0], ARLEN[3:0], ARSIZE[2:0], ARBURST[1:0] |
| **读数据** (R) | Slave→Master | 6 | RID[3:0], RDATA[31:0], RRESP[1:0], RLAST |
| **写地址** (AW) | Master→Slave | 10 | AWID[3:0], AWADDR[31:0], AWLEN[3:0], AWSIZE[2:0], AWBURST[1:0] |
| **写数据** (W) | Master→Slave | 6 | WID[3:0], WDATA[31:0], WSTRB[3:0], WLAST |
| **写响应** (B) | Slave→Master | 4 | BID[3:0], BRESP[1:0] |

**五个独立通道**分离了读地址、读数据、写地址、写数据和写响应，实现：

- 读写通道完全独立 → 全双工传输
- 地址通道与数据通道解耦 → 支持**outstanding 传输**（未完成时可发起新事务）
- 乱序完成（通过 ID 标识区分不同事务）

#### 2.1.2 突发传输（Burst）

| 参数 | 字段 | 取值范围 | 芯片设计影响 |
|:-----|:-----|:---------|:------------|
| 突发长度 | ARLEN/AWLEN[3:0] | 1-16 (0-15编码) | 数据缓冲深度设计 |
| 突发大小 | ARSIZE/AWSIZE[2:0] | 1/2/4/8/16/32/64/128 bytes | 数据总线宽度匹配 |
| 突发类型 | ARBURST/AWBURST[1:0] | FIXED/INCR/WRAP | 地址生成逻辑复杂度 |

**3 种突发类型**：

- **FIXED** (00): 同一地址重复访问（FIFO 类外设）
- **INCR** (01): 递增地址（常规内存访问）
- **WRAP** (10): 回环地址（Cache Line 填充），回环边界 = 突发大小 × 突发长度

#### 2.1.3 原子访问与锁定

- **Exclusive Access**: `AxLOCK=1` 时启用，Slave 需维护 Exclusive Monitor
- 芯片实现需在 **Slave 侧** 提供 Exclusive Monitor 逻辑（记录地址 + ID）
- Monitor 粒度一般为 **1-byte**，状态为 Open/Accessed
- `RRESP=EXOKAY` 表示 Exclusive 成功，`BRESP=EXOKAY` 表示 Store Conditional 成功

#### 2.1.4 低功耗接口

AXI 定义了 **Q-Channel** 低功耗接口：

- **ACTIVE** → **SLEEP** 状态转换需 Master 发起
- **SLEEP** → **ACTIVE** 唤醒延迟由系统时钟门控设计决定
- 芯片级电源管理可在 AXI 接口处插入时钟门控

#### 2.1.5 顺序与乱序规则

| 规则 | 描述 | 芯片实现约束 |
|:-----|:-----|:------------|
| **写顺序** | 同一 ID 的写事务需按序发出 W 数据 | 写缓冲只能对同 ID 保序 |
| **读顺序** | 同一 ID 的读事务需按序完成 | 读缓冲同理 |
| **写后写** | 不同 ID 的事务可乱序 | 需 ID 分配策略 |
| **读后写** | 无硬件保证，需 Master 自行同步 | 芯片需 W->R 屏障机制 |

#### 2.1.6 芯片设计关键参数

| 参数 | 典型值 | 芯片设计影响 |
|:-----|:------|:------------|
| 地址总线宽度 | 32/64 bits | 地址译码器宽度 |
| 数据总线宽度 | 32/64/128/256/512/1024 bits | Core 到总线桥接 |
| 最大 OUTSTANDING 事务数 | 协议未限制，芯片自定义 | Reorder Buffer 深度 |
| AHB→AXI 桥接 | 需额外 Address Phase FIFO | 透传延迟约 2-3 cycles |

### 2.2 AMBA 3 AHB-Lite 协议

**源**: `import/work/ARM_IHI0033A_AMBA_AHB-Lite_SPEC.md` | 4387 行 | 2006

AHB-Lite 是 AHB 的单 Master 简化版本，适用于**单处理器 SoC** 或**子系统级互连**。

#### 2.2.1 AHB-Lite vs AHB 差异

| 特性 | AHB | AHB-Lite | 芯片设计影响 |
|:-----|:---|:---------|:------------|
| Master 数量 | 多 Master (仲裁) | **单 Master** | 省去 Arbiter，面积减少 5-10% |
| Split/Retry | 支持 | **不支持** | Slave 逻辑简化 |
| Grant 信号 | HGRANTx | 无 | 无仲裁延迟 |
| 锁定传输 | HLOCKx | HBUSREQ，不支持锁定 | 简化总线控制 |

#### 2.2.2 AHB-Lite 传输协议

| 阶段 | 信号 | 时序要求 |
|:-----|:-----|:---------|
| **地址阶段** | HADDR, HWRITE, HSIZE[2:0], HBURST[2:0], HTRANS[1:0] | 1 cycle (HCLK 上升沿采样) |
| **数据阶段** | HWDATA, HRDATA | 1+ cycles (含等待) |
| **响应** | HREADYOUT, HRESP | HREADY=0 插入等待状态 |
| **流水线** | 当前数据阶段 = 下一地址阶段 | **地址/数据流水线**，无 Bubble |

#### 2.2.3 突发传输（AHB-Lite）

| HBURST[2:0] | 类型 | 长度 | 递增模式 |
|:-----------:|:-----|:----:|:---------|
| 000 | SINGLE | 1 | 单次传输 |
| 001 | INCR | 未指定 | 递增，ETC |
| 010 | WRAP4 | 4 | 回环 |
| 011 | INCR4 | 4 | 递增 |
| 100 | WRAP8 | 8 | 回环 |
| 101 | INCR8 | 8 | 递增 |
| 110 | WRAP16 | 16 | 回环 |
| 111 | INCR16 | 16 | 递增 |

#### 2.2.4 AHB-Lite 芯片实现要点

- **地址译码**: Slave 地址映射使用 `HSELx` 信号，译码器在地址阶段完成
- **Slave 接口**: 每个 Slave 提供 HREADYOUT（输出）+ HREADY（输入）
- **默认 Slave**: 未映射地址必须由默认 Slave 返回 ERROR 响应
- **Split 替代**: AHB-Lite 不支持 Split，长延迟 Slave 用 HREADY=0 插入等待

---

## 3. MIPS 处理器架构

### 3.1 MIPS32 ISA 概览

**源**: `import/work/mips/MD00082-2B-MIPS32INT-AFP-06.01.md` | 5024 行 | 2014

#### 3.1.1 指令格式

MIPS32 所有指令为 **32-bit 固定长度**，6 种编码格式：

| 格式 | 适用类型 | 字段结构 |
|:-----|:---------|:---------|
| **R-type** | 寄存器-寄存器运算 | op(6) + rs(5) + rt(5) + rd(5) + sa(5) + func(6) |
| **I-type** | 立即数/分支/加载存储 | op(6) + rs(5) + rt(5) + immediate(16) |
| **J-type** | 跳转 | op(6) + target(26) |
| **FR-type** | 浮点 | op(6) + fmt(5) + ft(5) + fs(5) + fd(5) + func(6) |
| **FI-type** | 浮点立即数 | op(6) + fmt(5) + ft(5) + immediate(16) |
| **Coproc-type** | 协处理器操作 | op(6) + cofun(5~0) + ... |

#### 3.1.2 芯片设计约束

| 约束 | 影响 |
|:-----|:------|
| 固定指令宽度 32-bit | **简化取指、译码逻辑**，无分支预测中指令对齐问题 |
| 32 个通用寄存器 (GPR) | 寄存器文件大小 = 32×32-bit = **128 bytes** |
| 3-操作数 R-type | 需 2-read/1-write 端口（或 3-read/2-write 全双端口） |
| load delay slot (MIPS I/II) | 加载后 1 条指令不能使用加载结果 → 插入流水线冲突检测 |
| branch delay slot | 分支指令后的指令**总会执行** → 分支预测器设计约束 |

#### 3.1.3 CP0 — 系统协处理器

MIPS 通过 CP0 实现系统控制，关键寄存器：

| CP0 寄存器 | 编号 | 芯片功能 |
|:-----------|:----:|:---------|
| Status (SR) | 12 | 中断使能/处理器模式/运行状态 |
| Cause | 13 | 异常原因编码/软件中断 |
| EPC | 14 | 异常返回地址 |
| Compare/Count | 11/9 | 定时器 |
| Context | 4 | 用于快速 TLB 异常处理 |
| BadVAddr | 8 | 出错虚拟地址 |
| EntryHi/EntryLo | 10/2 | TLB 表项 |
| PRId | 15 | 处理器版本/修订号(只读) |

### 3.2 MIPS64 指令集架构

**源**: `import/work/mips/MD00087-2B-MIPS64BIS-AFP-6.06.md` | 19149 行 | 2016

#### 3.2.1 MIPS64 核心特性

| 特性 | MIPS32 | MIPS64 | 芯片设计差异 |
|:-----|:------|:-------|:------------|
| GPR 宽度 | 32-bit | **64-bit** | ALU 数据通路倍宽 |
| 地址空间 | 2³² bytes | 2⁶⁴ bytes | TLB 页表项位数增加 |
| 乘除结果 | HI/LO 各 32-bit | HI/LO 各 **64-bit** | 乘法器位宽加大 |
| 浮点 | CP1 32×32-bit FPR | CP1 **32×64-bit FPR** | 浮点寄存器文件面积 ×2 |

#### 3.2.2 Release 6 架构增强（芯片设计影响）

| 增强 | Release 6 变化 | 解码逻辑影响 |
|:-----|:--------------|:------------|
| **无分支延迟槽** | 取消 branch delay slot | 分支预测复杂**降低** |
| **新条件分支** | BZ/BEQZ/BNEZ 等新格式 | 译码表需新增 I-type 子类 |
| **无 HI/LO 寄存器** | MUL/DIV 直接写 GPR | 省去 HL 寄存器写端口 |
| **无 MIPS16e** | JALC/MICRO... 移除 | 译码不再检查 MIPS16e 前缀 |
| **无 MDMX** | 媒体扩展移除 | 浮点协处理器精简 |

### 3.3 MIPS64 特权资源架构

**源**: `import/work/mips/MD00091-2B-MIPS64PRA-AFP-06.03.md` | 30564 行 | 2015

#### 3.3.1 特权层级

| 模式 | CP0 可用性 | TLB 访问 | 芯片实现要点 |
|:-----|:----------|:---------|:------------|
| **User Mode** | 受限 | 仅读部分寄存器 | 硬件检查每条指令的特权级 |
| **Supervisor Mode** | 部分 | 部分 TLB 操作 | 可选实现，MIPS64 定义了 |
| **Kernel Mode** | **完全** | 全部 | 复位后默认模式 |

#### 3.3.2 TLB 架构

| 参数 | MIPS32 | MIPS64 | 芯片面积影响 |
|:-----|:------|:-------|:------------|
| TLB 条目数 | 可配置 (典型 16-64) | 可配置 | SRAM Array 面积正比于条目数 |
| 页大小 | 4KB-16MB (可变) | 4KB-256MB (可变) | 比较器复杂度增加 |
| TLB 类型 | VTLB + FTLB | VTLB + FTLB (JTLB) | 两级 TLB 设计，VTLB 全相联 |
| TLB 探测方式 | TLBP 指令 | TLBP 指令 | 硬件 CAM 搜索逻辑 |

**VTLB (Vector TLB)**: 全相联，少量条目（典型 4-16），命中延迟 1 cycle
**FTLB/JTLB**: 组相联，大量条目（典型 64-1024），命中延迟 2-3 cycles

#### 3.3.3 异常处理机制

| 异常类型 | Cause 编码 | 入口点(EBase)偏移 |
|:---------|:----------:|:-----------------|
| **硬件中断** | 0x00 | +0x200（通用） |
| **TLB Refill** | 0x02（读）0x03（写） | +0x000/+0x080（特殊） |
| **Cache Error** | 0x18 | +0x100 |
| **Syscall/Break** | 0x08/0x09 | +0x200 |
| **预留指令** | 0x0A | +0x200 |

**芯片约束**: TLB Refill 异常有**专用入口点**（EBase+0x000/0x080），要求硬件在该地址处安排最快的异常处理路径（通常是一片 SRAM cacheable 向量表）。

### 3.4 MIPS 多核缓存一致性方案

**源**: `import/work/mips/cache_coherence_in_mips_multicore_design.md` | MD00888 | 750 行 | 2008

本文档描述 **MIPS32 1004K Coherent Processing System (CPS)** 的缓存一致性实现方案。

#### 3.4.1 基于 OCP 的 Snoop 一致性架构

| 组件 | 功能 | 芯片实现 |
|:-----|:-----|:---------|
| **Coherence Manager (CM)** | 集中式一致性管理器，路由/序列化消息 | **关键路径**，响应延迟决定性能 |
| **Snoop Tags** | L1 Cache Tag 副本，在 L1 之外镜像 | 需**双端口** Tag RAM（CPU 侧 + Snoop 侧） |
| **Intervention Port** | OCP Slave 端口，接收 CM 的 Snoop 请求 | 每个 CPU 需额外 OCP Slave 接口 |
| **I/O Coherence Unit (IOCU)** | DMA 设备地址空间一致性 | 一致性域扩展到外设 |

#### 3.4.2 MESI 协议实现

1004K 使用 **MESI**（Modified/Exclusive/Shared/Invalid）协议：

| 状态 | 含义 | 本 CPU 数据最新？ | 其他 CPU 有副本？ |
|:-----|:-----|:----------------:|:----------------:|
| **M** | Modified，已修改且独占 | ✅ 最新 | ❌ 无 |
| **E** | Exclusive，未修改且独占 | ✅ 与内存一致 | ❌ 无 |
| **S** | Shared，与其他 CPU 共享 | ✅ 与内存一致 | ✅ 有 |
| **I** | Invalid | ❌ | 不确定 |

**芯片实现要点**:

- L1 Data Cache Tag 需**双端口设计**：CPU 运算访问 + CM Snoop 访问
- Snoop Tag 阵列每个 CPU 一份副本（面积 ≈ L1 Tag 大小）
- CM 需包含 Request Unit（多 OCP Slave 输入→序列化） + Response Unit + Snoop Agent
- OCP 扩展了新的**消息类型**命令以支持 Snoop

#### 3.4.3 Coherence 消息流

```text
CPU0 读 Miss -> CM 收到请求
    -> CM 查找地址域（哪些 CPU 可能有此缓存行）
    -> CM 向相关 CPU 发送 Intervention
    -> 相关 CPU 查 Snoop Tag，返回状态 + 数据（若 Modified）
    -> CM 收集响应，返回给发起者 + 更新一致性状态
```

| 干预类型 | 条件 | 数据传输方向 |
|:---------|:-----|:------------|
| **Clean Intervention** | 目标行是 S/E 状态 | 无需传输数据 |
| **Dirty Intervention** | 目标行是 M 状态 | **从目标 CPU→发起 CPU** |
| **Dirty Intervention with Writeback** | M 状态且在写缺失时 | **目标→共享 L2** |

#### 3.4.4 多集群扩展

1004K 支持跨集群一致性（多 CM 级联），但文档指出：

- 集群间延迟显著增加（跨 CM 的远程 Snoop）
- 避免全局广播，使用**目录式过滤**减少跨集群干预
- 多集群一致性性能关键在于**目录压缩**和**延迟隐藏**

---

## 4. MIPS I6400/I6500 多处理器系统

### 4.1 I6500 系统架构与特性

**源**: `import/work/mips/MIPS_Warrior_I6500_Datasheet_MD01174_P_1.00.md` | 2072 行 | 2017
**源**: `import/work/mips/MIPS_Warrior_I6500_ProgrammerGuide_MD01179_P_1.00.md` | 7419 行 | 2017
**源**: `import/work/mips/MIPS_Warrior_I6400_ProgrammerGuide_MD01196_P_1.00.md`

I6500 是 MIPS Warrior 系列高性能多核处理器 IP，面向 SoC 集成。

#### 4.1.1 核心架构参数

| 参数 | I6400 | I6500 | 芯片设计影响 |
|:-----|:------|:------|:------------|
| ISA | MIPS64 Release 5 | **MIPS64 Release 6** | 译码器、分支预测简化 |
| 流水线 | 单发 | **双发(dual-issue)** | 取指宽度 64-bit，寄存器文件端口×2 |
| 多线程 | 2 线程/核 (硬件多线程) | **2-4 线程/核** | 每线程需独立 PC/GPR/CP0 |
| 每集群最大核数 | 6 | 6 | Coherence Manager 端口数上限 |
| 多集群 | 支持 | 支持 (无限) | 跨集群一致性目录 |
| SIMD | MIPS SIMD | MIPS SIMD (整型/浮点定点) | ALU + 浮点 SIMD 数据通路 |
| 虚拟化 | 硬件虚拟化 | 硬件虚拟化 | 二级 TLB + Guest OS 支持 |

#### 4.1.2 I6500 系统级特性

| 特性 | 描述 | 芯片集成要点 |
|:-----|:-----|:------------|
| **CM3.5 Coherence Manager** | 集中式一致性管理器 + 集成 L2 Cache | 关键 IP，决定多核性能 |
| **多集群** | 多个 Cluster 通过 CM 级联 | 缩放至数百核 |
| **GIC (全局中断控制器)** | 芯片级中断路由 | 连接所有核的中断分发 |
| **GCR (全局配置寄存器)** | 系统级配置空间 | 内存映射寄存器 |
| **CPC (集群电源控制器)** | 集群级 DVFS/电源门控 | 电源域设计 |
| **DBU (调试单元)** | 多处理器 JTAG 调试 | 所有核共享调试端口 |
| **ITU (线程间通信)** | 同一 Cluster 内核间通信 | 硬件加速 Interrupt/门铃 |
| **PDtrace** | 程序追踪 | 追踪数据输出带宽 |

#### 4.1.3 多集群配置

```text
Cluster 0                    Cluster N
+----------------+          +----------------+
| Core0  Core1   |          | Core0  Core1   |
| Core2  Core3   |          | Core2  Core3   |
|    ⋮ (至多6核)   |          |    ⋮ (至多6核)   |
| +------------+ |          | +------------+ |
| |  CM3.5+L2  | |          | |  CM3.5+L2  | |
| +------------+ |          | +------------+ |
+--------+-------+          +--------+-------+
         |  Coherent Interconnect    |
         +----------------------------+
                   |
              Memory Controller
```

- 每个 Cluster 的 CM 负责内部一致性 + 向其他 Cluster 发布远程访问
- **IOCU**: 每个 Cluster 最多 8 个（核+IO 总数≤8），DMA 设备通过 IOCU 进入一致性域

#### 4.1.4 I6500 Pipeline 架构

| 流水线阶段 | 描述 | 芯片面积占比 |
|:-----------|:-----|:-----------:|
| 取指 | 32KB L1 I-Cache, 预解码, 分支预测 | ~15% |
| 译码/重命名 | 2-wide, 寄存器重命名 | ~10% |
| 发射 | OoO (128-entry ROB, 64-entry Sched) | ~20% |
| 执行 | 2 ALU + 2 AGU + FPU/SIMD | ~30% |
| 回写/提交 | 2×写端口, 提交队列 | ~5% |
| L1/L2 Cache | L1 D$ 32KB + L2 up to 2MB | ~20% |

### 4.2 I6500 内存管理单元

#### 4.2.1 TLB 层次

| TLB 层级 | 容量 | 类型 | 芯片面积 | 命中延迟 |
|:---------|:----:|:----:|:--------:|:--------:|
| **VTLB** | 4-8 条 | 全相联 | 小 (~0.01mm²) | 1 cycle |
| **FTLB** (JTLB) | 64-1024 条 | 组相联 | 中 (~0.1mm²) | 2-3 cycles |
| **共享 FTLB** | 集群级 | 组相联 | 大 (~0.5mm²) | 3-5 cycles |

#### 4.2.2 页面大小支持

| 页大小 | TLB 条目 | 适用场景 |
|:------|:--------:|:---------|
| 4KB | 1 Entry | 标准页面 |
| 16KB | 1 Entry | 嵌入式 |
| 64KB | 1 Entry | 嵌入式/媒体 |
| 256KB-16MB | 1 Entry | 大页（数据库/HPC） |
| **Superpage** (>16MB) | 特殊处理 | 通过连续页面大小扩展 |

#### 4.2.3 共享 FTLB 机制（I6500 增强）

- 整个 Cluster 的核共享一个更大的 FTLB（减少 TLB Miss）
- 需要硬件在 **VTLB Miss → 查共享 FTLB → 若仍 Miss 查页表** 三级流程
- FTLB 替换策略：**伪 LRU**（避免多核竞争导致的颠簸）

### 4.3 I6500 缓存子系统

#### 4.3.1 缓存参数

| 缓存 | 容量 | 关联度 | 行大小 | 命中延迟 |
|:-----|:----:|:------:|:------:|:--------:|
| L1 I-Cache | 32KB | 4-way | 32B | 1-2 cycles |
| L1 D-Cache | 32KB | 8-way | 32B | 2-3 cycles |
| L2 Cache | 256KB-2MB | 8-16 way | 64B | 8-15 cycles |

#### 4.3.2 L1 D-Cache 双端口设计

- **单端口物理 RAM + 多端口虚拟架构**：通过分时（双倍频）实现伪双端口
- 一个 Cycle 内：前半周期服务 CPU Load/Store，后半周期服务 CM Snoop
- **Snoop Tag** 在 L1 外部镜像，面积 ≈ L1 Tag 阵列大小

#### 4.3.3 缓存一致性协议

I6500 在 CM3.5 中使用增强版 MESI（类似 **MOESI** 变体）：

| 状态 | 本核 | 其他核 | 内存一致性 |
|:-----|:----|:------|:----------|
| Modified (M) | 独占且已改 | Invalid | 不一致 |
| Owner (O) | 数据最新 | 可能有 Shared | 不一致，需回写 |
| Exclusive (E) | 独占且未改 | Invalid | 一致 |
| Shared (S) | 只读 | 可能有 | 一致 |
| Invalid (I) | 无效 | — | — |

**O 状态的优势**: 一个 Modified 行被另一个核读时，状态由 M→O 而不是 M→S，避免立即回写 L2，减少延迟。

---

## 5. ASPEED BMC SoC

### 5.1 AST2050/AST1100 SoC

**源**: `import/work/aspeed/ast2050reg.md` | 22954 行 | 2010

AST2050/AST1100 是 ASPEED Technology 的第二代 BMC（Baseboard Management Controller）SoC。

#### 5.1.1 芯片基本信息

| 参数 | AST2050 | AST1100 | AST2050A3-GP |
|:-----|:--------|:--------|:-------------|
| 封装 | 19×19mm BGA | 19×19mm BGA | 同左 |
| Ball Pitch | 0.8mm | 0.8mm | — |
| Core 电压 | 1.26V | 1.26V | — |
| DDR 电压 | 2.6V (DDR400) | 2.6V | — |
| IO 电压 | 3.3V | 3.3V | — |
| 功耗 | 待补充 | 待补充 | 文档含功耗信息 |

#### 5.1.2 芯片级功能模块

| 模块 | AST2050 规格 | 芯片集成要点 |
|:-----|:------------|:------------|
| **CPU Core** | ARM 内核 @ 可配置 | 集成在 SoC 内部 |
| **DDR/DDR2 控制器** | DDR400, 32-bit 数据总线 | 外部 2.6V 供电，PCB 布局关键 |
| **PCI 接口** | 32-bit PCI (v2.3), 33/66MHz | PCI AD[31:0] 总线可位交换 |
| **LPC 接口** | LPC 1.1 兼容 | 专用 LPC Reset 引脚 |
| **SMBus** | 共享 SMBus/I2C 多通道 | ALT1/ALT2 引脚映射可配置 |
| **USB 2.0** | 2 个 Host + 1 个 Device | USBVRES 引脚需 8.2KΩ 外部电阻 |
| **VUART** | Virtual UART | 软件编程指南中详细说明 |
| **Video** | 视频压缩/显示 | VR054 等视频寄存器 |
| **I2C** | 多路 I2C 总线 | 软件编程指南（第 31 节） |
| **PWM** | 多通道 PWM | 寄存器 PTRC40~PTRC7C 不存在（见勘误） |
| **GPIO** | 多功能引脚复用 | 完整引脚映射表（第 7 节） |

#### 5.1.3 电源上电时序

```text
Vcore (1.26V) -> VDDQ (2.6V) -> VDDIO (3.3V) -> PLL Lock -> Reset de-assert
```

- 严格时序要求：各电压域必须在时序窗口内完成稳定
- Flash Reset 时序在 Rev1.03 中有更新

#### 5.1.4 封装与引脚

| 参数 | 值 |
|:-----|:---|
| 封装尺寸 | 19×19mm |
| Ball Pitch | 0.8mm |
| Ball 类型 | Lead-free |
| 封装类型 | RoHS Green Package |

### 5.2 AST2500 系列

**源**: `import/work/aspeed/ast2500/` | 34 文件

AST2500 是 ASPEED 第三代 BMC SoC。

#### 5.2.1 已知规格

| 项目 | 信息 |
|:-----|:-----|
| SoC 编号 | AST2500 |
| 相关文档 | 寄存器手册、BMC 参考设计 |
| 关注点 | AST2500 基础开发指南、OpenBMC 支持 |

**文件清单**（部分关键）：

- `ast2050reg.md` — 寄存器手册
- `BMR-AST-BMC-SK-pb---.md` — BMC 参考设计简报
- `CAusten-OpenBMC.md` — OpenBMC 适配
- `DSP0261_1.0.0b.md` — DSP0261 管理标准

> ⚠️ 注意: AST2500 文档多为英文/中文混合，需结合 ASPEED 官网最新数据手册验证

---

## 6. 片上接口与总线标准

### 6.1 eSPI 接口规范

**源**: `import/work/std/327432-004_eSPI_Base_Specification_rev1.0.md` | 13526 行 | 2016
**源**: `import/work/std/329957-001_eSPI_Spec_Server_Addendum_Rev0_7.md` | Server 补充

eSPI（Enhanced Serial Peripheral Interface）是 Intel 定义的芯片间串行接口，取代传统 LPC 总线。

#### 6.1.1 eSPI 基本参数

| 参数 | 值 | 相比 LPC 改进 |
|:-----|:---|:-------------|
| 物理层 | 4 线+Sideband | 从 LPC 的 7+ 信号减少 |
| 最大速率 | 66MHz (Client) / 50MHz (Server) | LPC 为 33MHz |
| 带宽 | ~66 MB/s (单 I/O) | LPC 约 16 MB/s |
| 通道 | 8 (每通道独立) | LPC 无通道概念 |
| 电压 | 3.3V/1.8V 可选 | 支持低压接口 |
| 拓扑 | Master↔Slave 或 Multi-Master | LPC 只有单 Master |

#### 6.1.2 eSPI 通道类型

| 通道 | 编号 | 功能 | 芯片集成优先级 |
|:-----|:----:|:-----|:--------------|
| **Peripheral** | 0 | Legacy I/O (替代 LPC) | 必须 |
| **Virtual Wires** | 1 | 中断/复位/电源管理信号 | 必须 |
| **OOB** | 2 | 带外管理消息（OOB = Out-of-Band） | 可选 |
| **Flash** | 3 | 共享 SPI Flash 访问 | 可选 |

#### 6.1.3 芯片设计关键参数

| 参数 | 规格 | 芯片设计影响 |
|:-----|:-----|:------------|
| 最大 PCB 走线长度 | 无显式限制，SI 约束 | 高频时≤2-3 inches |
| 不等长约束 | 差分对同组内≤5% 时钟周期 | 66MHz→~0.75ns 偏差 |
| 终端匹配 | 源端串联 22-33Ω | I/O 缓冲器设计 |
| Cap 负载 | 15pF max per pin | Pin 驱动能力确定 |
| 时钟抖动 | < ±2% of period | PLL 设计约束 |
| Keepout 区域 | 邻近高噪声信号≥5× 信号线宽 | PCB 叠层设计 |

#### 6.1.4 Server Addendum 差异

| 特性 | Client | Server | 影响 |
|:-----|:------|:-------|:-----|
| 最大速率 | 66MHz | **50MHz** | 更长 PCB 走线能力 |
| Flash Channel | 可选 | **推荐** | BMC 共享 SPI Flash |
| 多 Master | 不支持 | **支持** (BMC+CPU) | 仲裁逻辑 |
| Reset 行为 | 统一 | BMC 可独立复位 | 上电时序灵活 |

### 6.2 DDR2 SDRAM 标准

**源**: `import/work/std/JESD79-2E_DDR2_SDRAM.md` | JESD79-2E | 3642 行 | 2008

#### 6.2.1 DDR2 关键参数

| 参数 | DDR2-400 | DDR2-533 | DDR2-667 | DDR2-800 |
|:-----|:--------:|:--------:|:--------:|:--------:|
| 时钟频率 | 200MHz | 266MHz | 333MHz | 400MHz |
| 数据速率 | 400 MT/s | 533 MT/s | 667 MT/s | 800 MT/s |
| 命令/地址总线 | SSTL-18 (1.8V) | SSTL-18 | SSTL-18 | SSTL-18 |
| 数据总线 | SSTL-18 | SSTL-18 | SSTL-18 | SSTL-18 |
| CAS Latency | 3 | 3-4 | 4-5 | 5-6 |
| tRCD | 3 | 3-4 | 4-5 | 5-6 |
| tRP | 3 | 3-4 | 4-5 | 5-6 |

#### 6.2.2 芯片级设计约束

| 约束 | 参数 | 说明 |
|:-----|:-----|:------|
| **VREF** 精度 | ±1% (0.9V) | 需片上电压参考源 |
| **ODT (On-Die Termination)** | 75/150/50Ω | 芯片内部匹配电阻 |
| **OCD (Off-Chip Driver)** | 校准 | 驱动强度可编程 |
| **DQS 延迟** | 90° 相移 | PLL/DLL 生成 |
| **写入均衡** | 支持 | 飞思卡尔等芯片实现复杂读/写均衡 |

#### 6.2.3 初始化序列

```text
上电 -> Reset低保持200μs -> CKE低 -> 时钟稳定-> Reset释放
-> CKE高 -> 等待 400ns -> 发出 NOP -> 预充电所有 Bank
-> EMR(2)-> EMR(3)-> 使能 DLL -> 预充电 -> 刷新(2 cycles)
-> 设置 Mode Register -> ZQ 校准 (200 cycles) -> 开始正常操作
```

#### 6.2.4 芯片设计注意事项

- **DLL 锁定时间**: 上电后需 200 个时钟周期，DLL 才完成锁相
- **写均衡**: 在 Fly-by 拓扑中必须支持（DDR2 用特定 MR 位使能）
- **ODT 动态切换**: 不同操作（读/写/空闲）切换不同 ODT 值
- **自刷新**: 进入自刷新需要特定序列，退出也需要 tXSNR/tXSRD 时序

### 6.3 LPC 总线

**源**: `import/work/LPC/` — 包含 LPC 接口相关资料

LPC（Low Pin Count）总线是 Intel 定义的芯片间接口，主要用于连接 BIOS Flash 和 Super I/O 芯片。

| 参数 | LPC | eSPI（替代者） |
|:-----|:---|:--------------|
| 信号数 | 7 (LAD[3:0], LFRAME#, LCLK, LRST#) | 4+Sideband |
| 时钟 | 33MHz | 50-66MHz |
| 带宽 | ~16 MB/s | ~66 MB/s |
| 地址空间 | I/O @ 0x2E/0x2F 等 | 独立通道编址 |
| 终结状态 | Intel 不再推荐新设计 | ✅ 推荐替代 |

---

## 7. 固件与平台初始化架构

### 7.1 Intel FSP 架构 v2.0

**源**: `import/work/std/fsp-architecture-spec-v2.md` | 3125 行 | 2016

FSP (Firmware Support Package) 是 Intel 提供的芯片初始化二进制模块。

#### 7.1.1 FSP 架构

| 阶段 | 功能 | 代码体积 | 运行位置 |
|:-----|:-----|:--------:|:---------|
| **TempRamInit** | 初始化临时内存（Cache as RAM） | ~30KB | CRAM |
| **CPU Init** | 微码加载、CPU 初始化 | ~100KB | CRAM |
| **Silicon Init** | 芯片组/内存初始化 | ~200KB | CRAM + DRAM |
| **Notify Phase** | 通知固件各阶段完成 | ~10KB | DRAM |

#### 7.1.2 FSP 芯片设计接口

| API | 输入 | 输出 | 用途 |
|:----|:-----|:-----|:-----|
| FspInit() | BootLoader 填充 UPD | FSP 信息结构 | 启动 FSP 流程 |
| FspInitPhase2() | 阶段参数 | 状态码 | 分阶段执行 |
| FspNotifyPhase() | 通知类型 | 状态码 | Boot/Ready-to-Sleep/End-of-Firmware |
| FspMemoryInit() | UPD | HOB 列表 | 内存初始化 |
| FspTempRamExit() | 无 | 状态码 | 退出 CAR |

#### 7.1.3 芯片集成约束

- FSP 运行期间占用**整个 CACHE AS RAM (CAR)** 区域
- BootLoader 必须在 FSP 启动前正确配置 CAR 大小
- FSP 使用 **SMM** 作为运行时服务环境
- 多芯片系统需要每个芯片实例化 FSP

### 7.2 UEFI PI 规范 v1.7

**源**: `import/work/std/PI_Spec_1_7_A_final_May1.md` | 76357 行 | 2020

PI (Platform Initialization) 规范定义 UEFI 固件的芯片级接口标准。

#### 7.2.1 PI 阶段（SEC/PEI/DXE/BDS）

| 阶段 | 全称 | 运行内存 | 芯片依赖 |
|:-----|:------|:---------|:---------|
| **SEC** | Security Phase | Cache-as-RAM | 最少依赖，~1KB CRAM |
| **PEI** | Pre-EFI Initialization | CRAM → DRAM | 依赖芯片的内存控制器 IP |
| **DXE** | Driver Execution Environment | DRAM | 芯片组/外设驱动 |
| **BDS** | Boot Device Selection | DRAM | 启动设备枚举 |

#### 7.2.2 PEI 核心 — Boot Mode 与 HOB

Boot Mode 决定芯片初始化策略：

| Boot Mode | 含义 | 芯片初始化差异 |
|:----------|:-----|:--------------|
| BOOT_WITH_FULL_CONFIGURATION | 冷启动完整初始化 | 全内存 Training |
| BOOT_WITH_MINIMAL_CONFIGURATION | 最小配置 | 跳过非必要外设 |
| BOOT_ASSUMING_NO_CONFIGURATION_CHANGES | S3 恢复 | 跳过内存 Training |
| BOOT_WITH_FULL_CONFIGURATION_PLUS_DIAG | 诊断模式 | 额外测试 |

**HOB (Hand-Off Block)**: 阶段间传递数据结构

- 内存描述 HOB: 告知 DXE 可用内存区域
- 资源描述 HOB: 芯片内设 MMIO 映射
- GUID 扩展 HOB: 芯片特定的私有数据

#### 7.2.3 芯片级接口（SEC/PEI）

| 接口 | 实现芯片 | 功能 |
|:-----|:---------|:-----|
| **SecCore** (汇编) | CPU | 芯片复位向量→C 入口 |
| **PeiCore** | 芯片组 | PEI 调度器 |
| **CPU PEIM** | CPU | 微码/BIST/Cache 初始化 |
| **MRC PEIM** | 芯片组 | 内存参考代码 Training |
| **SB PEIM** | 芯片组 | 芯片组/南桥初始化 |

### 7.3 UEFI 安全启动与芯片级安全

**源**: `import/work/UEFI/` | 19 文件

#### 7.3.1 Secure Boot 流程

| 步骤 | 操作 | 芯片安全功能 |
|:-----|:-----|:------------|
| 1 | 固件镜像数字签名验证 | 芯片内置公钥 Hash（fused） |
| 2 | BootLoader 签名验证 | Secure Boot Key 管理 |
| 3 | OS 内核签名验证 | 平台密钥 (PK) 验证 |
| 4 | 内核模块签名验证 | Key Exchange Key (KEK) |

#### 7.3.2 Intel Boot Guard

- **硬件级信任根**: 芯片 fused 公钥 hash
- **Verified Boot**: CPU 微码验证 BIOS 的 ACM (Authenticated Code Module)
- **Boot Policy**: 支持 measured boot 和 verified boot 两种
- **芯片融合**: 在芯片制造时写入 fuses，不可更改

#### 7.3.3 芯片级威胁防护

| 攻击类型 | 防护机制 | 参考文献 |
|:---------|:---------|:---------|
| BIOS Rootkit | Boot Guard / Secure Boot | 35c3-9561 |
| PCI Rootkit | PCI Option ROM 签名验证 | implementing_detecting_pci_rootkit |
| SMM 攻击 | SMM 保护范围寄存器 (SMRAM) | ACPI/SMI handlers |
| SPI Flash 篡改 | Flash 写保护 / PFR | bmc-bios-security |

---

## 8. 芯片安全架构

### 8.1 Arm Server Base Security Guide

**源**: `import/work/DEN0086-SBSG-1.0.md` | DEN 0086 | 1478 行

#### 8.1.1 安全基线

| 安全域 | 要求 | 芯片实现 |
|:-------|:-----|:---------|
| **可信启动** | Boot ROM → BootLoader → OS 链式验证 | Boot ROM 使用芯片 fused 公钥 |
| **隔离执行** | TrustZone / 安全世界 | 硬件 MMU 隔离 |
| **内存保护** | 非可执行区域标记 | MMU XN bit |
| **外设隔离** | DMA 重映射（SMMU/IOMMU） | IOMMU 页表 |

#### 8.1.2 芯片安全架构要求

```text
Server Platform Security Requirements:
+-- Root of Trust (芯片级)
|   +-- Boot ROM (不可变)
|   +-- OTP Fuses (公钥 Hash)
|   +-- True Random Number Generator (TRNG)
+-- Secure Boot Chain
|   +-- Boot ROM -> BL1 -> BL2 -> BL31 -> BL33
|   +-- 每个阶段签名验证
+-- Runtime Security
|   +-- Trust Zone (安全/非安全世界)
|   +-- SMMU (IO 设备隔离)
|   +-- Secure Watchdog
+-- Debug Security
    +-- JTAG/SWD 认证锁
    +-- 安全调试策略
```

#### 8.1.3 DRTM (Dynamic Root of Trust for Measurement)

| 要素 | 描述 | 芯片需求 |
|:-----|:------|:---------|
| SINIT/ACM | 芯片厂商提供的签名的初始化模块 | 芯片微码或 Boot ROM |
| DLME (Dynamic Launch Measured Environment) | 动态启动后度量环境 | 内存区域隔离 |
| MLE (Measured Launch Environment) | Hypervisor 度量环境 | 芯片 PMR (Protected Memory Region) |

### 8.2 芯片级可信启动

#### 8.2.1 信任根链（参考 UEFI + Arm SBSG）

```text
OTP Fuses (Hash of Root Public Key)
    v 芯片制造时绕写
Boot ROM (不可修改, Mask ROM)
    v 验证签名
BL1 (Boot Loader Stage 1)
    v 验证签名
BL2/BL3x (后续启动阶段)
    v 验证签名
OS Kernel / Hypervisor
```

#### 8.2.2 芯片硬件安全特性对照

| 特性 | Arm 方案 | Intel 方案 | 芯片面积开销 |
|:-----|:---------|:-----------|:-----------:|
| 信任根 | Boot ROM + OTP | Boot Guard (Fused Key) | ~0.01mm² (OTP) |
| 安全隔离 | TrustZone | SMM/SGX | ~0.5mm² |
| 内存加密 | 可选 | TME/MKTME | ~0.3mm² |
| IOMMU | SMMU | VT-d | ~0.8mm² |

---

## 9. 增量分析

### 9.1 与现有知识库对比

| 对比维度 | 现有 KB 状态 | 本文新增 | 增量类型 |
|:---------|:------------|:---------|:---------|
| AMBA AXI 协议 | 无系统文档 | ✅ AXI4 v2.0 完整协议规范（5 通道/突发/Exclusive/低功耗） | **全新** |
| AMBA AHB-Lite | 无 | ✅ 单 Master AHB 简化版本/芯片面积节省 | **全新** |
| MIPS ISA 架构 | 无 | ✅ MIPS32/MIPS64 指令格式/CP0/TLB/异常处理 | **全新** |
| MIPS 多核一致性 | 无 | ✅ OCP 消息模型/MESI/Snoop Tag 双端口 | **全新** |
| I6500 处理器 | 无 | ✅ 双发 OoO 流水线/多集群/共享 FTLB/GIC/CM3.5 | **全新** |
| ASPEED SoC | 无 | ✅ AST2050 寄存器级规格/引脚/封装/电源时序 | **全新** |
| ASPEED AST2500 | 无 | ✅ 管理架构/OpenBMC 关联 | **全新** |
| eSPI 规范 | 已有部分 | ✅ 详细通道类型/Server 差异/SI 约束 | **补充**（首次系统化） |
| DDR2 标准 | 无关（已过时） | ✅ JEDEC 标准时序/初始化/ODT/DLL | **参考**（对比 DDR4/5） |
| LPC 总线 | 无 | ✅ 与 eSPI 对比/替代关系 | **全新** |
| FSP 架构 | 无 | ✅ FSP v2.0 阶段/API/芯片集成约束 | **全新** |
| UEFI PI 规范 | 无 | ✅ SEC/PEI/DXE/BDS 阶段/Boot Mode/HOB | **全新** |
| UEFI Secure Boot | 无 | ✅ Secure Boot 流程/Boot Guard/芯片级威胁 | **全新** |
| Arm SBSG | 无 | ✅ 安全基线/DRTM/信任根/硬件特性对比 | **全新** |

### 9.2 关键发现

1. **MIPS 一致性方案的独特性** — MIPS 1004K 基于 OCP 消息模型的 Snoop 一致性是多核设计的一个独特参考，与 ARM ACE 和 x86 QPI 方案有本质差异：通过 OCP 扩展消息类型而非专用一致性总线。Snoop Tag 双端口设计（分时复用物理 RAM）对**低面积开销**的多核 SoC 有参考价值。

2. **I6500 的 "Release 6" 关键变革** — 取消分支延迟槽意味着流水线设计简化（无需跟踪延迟槽指令的异常）；取消 HI/LO 寄存器意味着乘法器数据通路直接写 GPR 文件；这两项变化对芯片设计**面积和复杂度**的影响显著（估测节省 ~5% 控制逻辑面积）。

3. **ASPEED 芯片演进路线** — AST2050 (2008)→AST2500 (2015?)→AST2600 (2019) 三代演进中，PCI→LPC→eSPI 接口标准的迁移与服务器管理协议栈的标准化进程高度吻合。AST2050 的 22954 行寄存器手册可作为 BMC SoC 设计的**完整参考模板**。

4. **eSPI 取代 LPC 的芯片设计影响** — eSPI 在信号数减少 40% 的同时带宽提升 4×，对 SoC 引脚/PCB 层数/成本均有显著改善。Server Addendum 的 50MHz（非 66MHz）和 Flash Channel 强制需求是服务器 SoC 芯片设计的关键差异化约束。

5. **FSP + PI 的双层固件架构** — Intel FSP（芯片初始化二进制）+ UEFI PI（平台初始化框架）的分离设计，使得芯片 IP 厂商可发布二进制模块而不暴露寄存器细节，同时 BootLoader 开发者可以标准化接口调用。这一模式的芯片设计含义是**需要明确定义 FSP 与 PI 的接口边界——即在芯片设计时就要规划好哪些初始化逻辑应封装在 FSP 中，哪些暴露给 PI 固件**。

### 9.3 推荐方向

1. **将 MIPS 一致性方案与已有 OCP/AMD 文档中的缓存一致性内容做交叉分析**（现有 KB 有 OCP 和 AMD 的一致性专利/方案文档，可做三方对比）

2. **基于 AST2050 的寄存器手册模板，建立 BMC SoC 设计 checklist**（DDR 控制器/PCI/LPC/SMBus/GPIO 引脚复用等模块集成标准模板）

3. **将 eSPI 与现有的 I2C/SPI/NC-SI 接口文档整合为 "服务器板级接口标准速查表"**（信号数/速率/拓扑/适用场景对比）

4. **FSP+PI 固件架构仅为 Intel 方案，建议补充 UEFI+PI 在 AMD/ARM 架构下的芯片集成差异**（AMD 的 AGESA vs Intel FSP，ARM 的 TF-A vs UEFI PI）

5. **安全架构章节建议与已有知识库的 PFR (Platform Firmware Resilience) 和 SPDM 文档联动**，形成芯片安全→固件安全→平台安全的完整安全分析链路

---

## changelog

| 日期 | 变更 |
|:-----|:-----|
| 2026-07-21 | 首次归档，14 个芯片设计主题，增量分析 14 项对比 + 5 发现 + 5 推荐 |

---

**关联文档**:

- `knowledge/02_rd/08_chip/amd/2026-07-21-import-amd-chip-design-overview.md` — AMD 芯片设计
- `knowledge/02_rd/08_chip/ocp/2026-07-21-import-ocp-chip-design-overview.md` — OCP 芯片设计
- `knowledge/02_rd/08_chip/risc-v/2026-07-21-import-risc-v-chip-design-overview.md` — RISC-V 芯片设计

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- (无)

### 外部资料引用

- 来源: import/work/` 中未纳入 amd/ocp/risc-v 专项归档的芯片设计材料

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
