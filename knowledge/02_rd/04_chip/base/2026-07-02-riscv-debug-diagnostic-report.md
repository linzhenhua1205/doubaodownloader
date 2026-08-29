# RISC-V 调试诊断功能与 Linux 内核支持专题报告

> **概要**: (待补充)
>
> **关键词**: (待补充)

---

## 📑 目录

- [1. 综述](#1-综述)
- [2. RISC-V 调试体系架构总览](#2-risc-v-调试体系架构总览)
  - [2.1 规范体系](#21-规范体系)
  - [2.2 调试分层架构](#22-调试分层架构)
  - [2.3 调试模式（Debug Mode）](#23-调试模式debug-mode)
- [3. Debug Transport Module (DTM)](#3-debug-transport-module-dtm)
  - [3.1 DTM 职责](#31-dtm-职责)
  - [3.2 支持的物理传输方式](#32-支持的物理传输方式)
  - [3.3 JTAG DTM 详细规范](#33-jtag-dtm-详细规范)
  - [3.4 DMI 总线协议](#34-dmi-总线协议)
- [4. Debug Module (DM)](#4-debug-module-dm)
  - [4.1 DM 核心功能矩阵](#41-dm-核心功能矩阵)
  - [4.2 Hart 状态机](#42-hart-状态机)
  - [4.3 运行控制（Run Control）](#43-运行控制run-control)
  - [4.4 Abstract Commands](#44-abstract-commands)
  - [4.5 Program Buffer](#45-program-buffer)
  - [4.6 System Bus Access (SBA)](#46-system-bus-access-sba)
  - [4.7 Hart 选择与多核调试](#47-hart-选择与多核调试)
- [5. Trigger Module — Sdtrig ISA扩展](#5-trigger-module-sdtrig-isa扩展)
  - [5.1 Sdtrig 概述](#51-sdtrig-概述)
  - [5.2 Trigger 类型](#52-trigger-类型)
  - [5.3 mcontrol6 — 最常用的 Trigger 类型](#53-mcontrol6-最常用的-trigger-类型)
  - [5.4 icount — 指令计数 Trigger](#54-icount-指令计数-trigger)
  - [5.5 itrigger 和 etrigger — 中断/异常 Trigger](#55-itrigger-和-etrigger-中断异常-trigger)
  - [5.6 Trigger 优先级](#56-trigger-优先级)
  - [5.7 Native Trigger — 操作系统可见的触发机制](#57-native-trigger-操作系统可见的触发机制)
- [6. Trace 与性能监控](#6-trace-与性能监控)
  - [6.1 性能计数器 — Zihpm / Zicntr](#61-性能计数器-zihpm-zicntr)
  - [6.2 每个触发器可指定的性能事件](#62-每个触发器可指定的性能事件)
  - [6.3 SBI PMU 扩展](#63-sbi-pmu-扩展)
- [7. E-Trace 与 Processor Trace](#7-e-trace-与-processor-trace)
  - [7.1 RISC-V E-Trace (Nexus Trace)](#71-risc-v-e-trace-nexus-trace)
  - [7.2 Processor Trace (开发中)](#72-processor-trace-开发中)
- [8. RISC-V 调试安全模型](#8-risc-v-调试安全模型)
  - [8.1 Authentication (认证机制)](#81-authentication-认证机制)
  - [8.2 熔断机制](#82-熔断机制)
  - [8.3 调试对安全的影响](#83-调试对安全的影响)
- [9. Linux 内核调试诊断功能总览](#9-linux-内核调试诊断功能总览)
  - [9.1 整体支持状态](#91-整体支持状态)
  - [9.2 调试诊断功能依赖关系](#92-调试诊断功能依赖关系)
- [10. perf_event 子系统与 PMU 支持](#10-perf_event-子系统与-pmu-支持)
  - [10.1 架构](#101-架构)
  - [10.2 支持的 Perf 功能](#102-支持的-perf-功能)
  - [10.3 SBI PMU 内核代码流程](#103-sbi-pmu-内核代码流程)
  - [10.4 快照读取优化](#104-快照读取优化)
- [11. 硬件断点/观测点 — hw_breakpoint](#11-硬件断点观测点-hw_breakpoint)
  - [11.1 概述](#111-概述)
  - [11.2 Linux hw_breakpoint 架构](#112-linux-hw_breakpoint-架构)
  - [11.3 GDB 中使用 hw breakpoint](#113-gdb-中使用-hw-breakpoint)
  - [11.4 限制与注意事项](#114-限制与注意事项)
- [12. KGDB — 内核调试器](#12-kgdb-内核调试器)
  - [12.1 RISC-V KGDB 支持](#121-risc-v-kgdb-支持)
  - [12.2 RISC-V KGDB 调试流程](#122-risc-v-kgdb-调试流程)
- [13. Kprobes/Uprobes — 动态探针](#13-kprobesuprobes-动态探针)
  - [13.1 Kprobes](#131-kprobes)
  - [13.2 Kretprobes](#132-kretprobes)
  - [13.3 Uprobes](#133-uprobes)
  - [13.4 待完善的功能](#134-待完善的功能)
- [14. KASAN/KCOV — 内存错误检测与覆盖率](#14-kasankcov-内存错误检测与覆盖率)
  - [14.1 KASAN (Kernel Address Sanitizer)](#141-kasan-kernel-address-sanitizer)
  - [14.2 KCOV (Coverage-guided Fuzzing)](#142-kcov-coverage-guided-fuzzing)
- [15. Ptrace — 用户态调试接口](#15-ptrace-用户态调试接口)
  - [15.1 RISC-V Ptrace 支持](#151-risc-v-ptrace-支持)
  - [15.2 单步执行实现](#152-单步执行实现)
- [16. RISCV_HWPROBE 与 SBI 调试接口](#16-riscv_hwprobe-与-sbi-调试接口)
  - [16.1 sys_riscv_hwprobe](#161-sys_riscv_hwprobe)
  - [16.2 SBI 调试控制台 (DBCN)](#162-sbi-调试控制台-dbcn)
  - [16.3 SBI Reset & Shutdown](#163-sbi-reset-shutdown)
- [17. Ftrace/Tracepoint — 内核追踪框架](#17-ftracetracepoint-内核追踪框架)
  - [17.1 Ftrace](#171-ftrace)
  - [17.2 Tracepoints](#172-tracepoints)
  - [17.3 Ftrace + Kprobe 联合](#173-ftrace-kprobe-联合)
- [18. 各调试/诊断功能的对比矩阵](#18-各调试诊断功能的对比矩阵)
  - [18.1 硬件调试功能对比 (RISC-V vs ARM vs x86)](#181-硬件调试功能对比-risc-v-vs-arm-vs-x86)
  - [18.2 Linux 内核调试功能对比 (RISC-V vs ARM64 vs x86)](#182-linux-内核调试功能对比-risc-v-vs-arm64-vs-x86)
  - [18.3 RISC-V 调试能力的独特优势](#183-risc-v-调试能力的独特优势)
- [19. 参考规范与文档](#19-参考规范与文档)
  - [知识库交叉链接](#知识库交叉链接)
- [20. 变更记录](#20-变更记录)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 1. 综述

RISC-V 的调试诊断体系在架构设计上有一个关键的**先天优势**：调试功能不是事后补丁，而是从指令集架构层面就被作为一等公民设计的。其调试规范（Debug Specification v1.0，2025年2月批准）与 Privileged 规范共同构成了完整的调试诊断分层架构。

```text
                     +---------------------------------------+
                     |        Debugger (GDB/LLDB/...)         |
                     +------------------+--------------------+
                                        | Debug Protocol
                     +------------------v--------------------+
                     |    Debug Transport Module (DTM)        |
                     |  JTAG / cJTAG / USB / SPI / PCIe       |
                     +------------------+--------------------+
                                        | DMI Bus
                     +------------------v--------------------+
                     |        Debug Module (DM)               |
                     |  Run Control / Abstract Cmd / SBA      |
                     +------+-------------------+------------+
                            |                   |
               +------------v-----+     +------v-----------+
               | Trigger Module   |     | Performance      |
               | (Sdtrig ISA Ext) |     | Monitor (Zihpm)  |
               | HW Breakpoint    |     | Counters + SBI   |
               | Watchpoint/Trace |     |                   |
               +------------------+     +-------------------+
```

该文档以**芯片级硬件调试诊断能力**为第一视角，系统梳理 RISC-V Debug Spec 1.0 规定的各层次功能，然后对照 Linux 内核在各个子系统上的支持状态（基于 Linux v7.2-rc1 / 6.x+ 内核树）。

---

## 2. RISC-V 调试体系架构总览

### 2.1 规范体系

RISC-V 调试诊断相关规范：

| 规范 | 状态 | 批准日期 | 覆盖范围 |
|:-----|:-----|:---------|:---------|
| **RISC-V Debug Specification v1.0** | ✅ 已批准 | 2025-02 | DTM/DM/Sdtrig/Abstract Commands/SBA/Trace |
| **Sdtrig ISA Extension** | ✅ 已批准 | 含于 Debug 1.0 | Trigger Module (硬件断点/观测点/ETrigger/ITrigger) |
| **Zihpm / Zicntr** | ✅ 已批准 | 2023 | 硬件性能计数器/指令计数器 |
| **SBI Debug Extension (DBCN)** | ✅ 已批准 | 2024 | SBI 层调试控制台接口 |
| **E-Trace (Nexus)** | ✅ 已批准 | 2024 | 嵌入式跟踪标准 |
| **Processor Trace** | 🔧 开发中 | — | 高性能指令跟踪 |

[来源: RISC-V International Ratified Specifications, riscv.org/technical/specifications]

### 2.2 调试分层架构

RISC-V 调试体系分为三个逻辑层：

```text
Layer 3: Debugger (GDB/LLDB/OpenOCD/PyOCD)
     | RSP / GDB Remote Serial Protocol
Layer 2: Debug Transport Module (DTM)
     | DMI Bus (Debug Module Interface)
Layer 1: Debug Module (DM) + Trigger Module (TM)
     | CSR/ProgBuf/SBA interaction with hart
Layer 0: Hart (CPU core) — RISC-V ISA execution
```

**各层职责**：

- **DTM**（调试传输模块）：物理传输层的抽象，支持多种物理接口（JTAG/cJTAG/USB/SPI/PCIe），将调试器命令转换成 DMI 总线事务
- **DM**（调试模块）：核心调试引擎，管理 halt/resume、abstract commands、program buffer、system bus access
- **TM**（触发模块，Sdtrig）：实现地址/数据/指令/事件触发，通过 CSR 接口暴露给软件

### 2.3 调试模式（Debug Mode）

RISC-V 为调试定义了一个独立的特权模式 —— **Debug Mode**。当 hart 进入 Debug Mode 时：

- 停止执行用户/监督/机器模式的指令
- 执行来自 Program Buffer 或抽象命令的指令
- 对外表现为 halted 状态
- 此时 DCSR（Debug Control and Status Register）保存进入调试模式的原因

| 原因码 (dcsr.cause) | 含义 | 典型场景 |
|:-------------------|:-----|:---------|
| 1 | `ebreak` 指令 | 软件断点 |
| 2 | trigger 模块触发 | 硬件断点/观测点命中 |
| 3 | halt 请求（debugger 发起的暂停） | 外部调试器 halt |
| 4 | step 完成 | 单步执行 |
| 5 | reset 后 halt-on-reset | 复位后立即停止 |
| 6 | halt group 同步 | 多核调试同步 |

---

## 3. Debug Transport Module (DTM)

### 3.1 DTM 职责

DTM 充当调试器与 DM 之间的桥梁。它**不是** ISA 扩展（即不需要在指令集中反映），而是芯片实现层的硬件模块。DTM 通过 DMI（Debug Module Interface）总线与 DM 通信。

### 3.2 支持的物理传输方式

| 传输方式 | 标准 | 引脚数 | 带宽 | 适用场景 |
|:---------|:-----|:-------|:-----|:---------|
| **JTAG** | IEEE 1149.1 | 4-5 (TCK/TMS/TDI/TDO/TRST) | ~10-100 MHz TCK | 通用标准，所有芯片必选 |
| **cJTAG** | IEEE 1149.7 | 2 (TMSC/TCKC) | 同 JTAG | 减少引脚，适合嵌入式 |
| **USB** | USB 2.0/3.0 | 4 | 480 Mbps / 5 Gbps | 开发板调试 |
| **SPI** | SPI 兼容 | 4 (SCLK/MOSI/MISO/CS) | 灵活 | 低成本调试方案 |
| **PCIe** | PCIe | 参考 PCIe | 高带宽 | 服务器/数据中心芯片 |

### 3.3 JTAG DTM 详细规范

JTAG DTM 是最常见、最基础的实现，其硬件接口寄存器通过 JTAG DR（Data Register）链暴露：

**DTM 状态机**：通过 JTAG TAP（Test Access Port）状态机控制，使用 5 个标准 JTAG 状态。

**JTAG DTM 寄存器映射**：

```text
通过 JTAG IR (指令寄存器) 选择 DR:
  IR = 0x01: 选择 DMI 访问寄存器
  IR = 0x10: 选择 DTM 控制寄存器 (DTMCS)
  IR = 0x11: 选择 IDCODE 寄存器

DMI 访问寄存器 (DR 链长度: 41+ 位):
  Bit [40:34] — op (1: read, 2: write, 3: quick write)
  Bit [33:7]  — address (27位, DMI 地址空间)
  Bit [6:0]   — data (仅在 op=1 时不适用)

DTMCS 寄存器:
  Bit [15:12] — dmireset (DMI复位)
  Bit [11:0]  — dmihardreset
```

[来源: RISC-V Debug Spec v1.0 §3 — DTM, §3.4 — JTAG DTM]

### 3.4 DMI 总线协议

DMI 是 DTM 和 DM 之间的片内总线。DMI 总线事务：

```text
DMI 总线事务时序:
  请求:  DTM --- address + op + data ---> DM
  响应:  DTM <--- resp (0=成功/1=失败/2=忙) + data -- DM

DMI 地址空间:
  0x00-0x11: DM 标准寄存器 (18个 32-bit 寄存器)
  0x12-0x2F: 保留
  0x30-0x3F: Data 寄存器 (用于抽象命令参数传递)
  0x40-0xFF: 可选扩展
```

---

## 4. Debug Module (DM)

### 4.1 DM 核心功能矩阵

DM 是整个调试诊断体系的核心引擎。根据规范，必须实现和可选实现的功能如下：

| 功能 | 要求 | 用途 |
|:-----|:-----|:------|
| 报告实现信息 | ⭐ 强制 | 调试器自发现 |
| 单个 hart halt/resume | ⭐ 强制 | 最基本的运行控制 |
| 提供 halt 状态信息 | ⭐ 强制 | 查询哪些 hart 停止 |
| 访问 halted hart 的 GPR | ⭐ 强制 | 读取/修改寄存器 |
| 复位后立即调试 | ⭐ 强制 | ndmreset + 复位后断点 |
| 复位时立即 halt | ◇ 可选 | resethaltreq |
| 访问非 GPR 寄存器 | ◇ 可选 | CSR/FPR 访问 |
| Program Buffer | ◇ 可选 | 执行任意指令 |
| 多 hart 同时 halt/resume | ◇ 可选 | Hart Array Mask |
| 从 hart 角度访问内存 | ◇ 可选 | Abstract Access Memory |
| 系统总线访问 (SBA) | ◇ 可选 | 不经过 hart 直接访问内存 |
| Halt 组 / Resume 组 | ◇ 可选 | 多核同步调试 |
| 外部触发输入/输出 | ◇ 可选 | 跨域触发 |

**兼容性要求**：至少实现以下一种内存访问机制：

1. Program Buffer（推荐）
2. System Bus Access（SBA，对运行时影响最小）
3. Abstract Access Memory 命令

或：至少实现 Program Buffer，或对 hart 所有可见寄存器提供抽象访问。

"最小调试规范"（Minimal RISC-V Debug Specification）：只需支持 GPR + DCSR + DPC 的抽象访问即可使用更宽松的兼容性标记。

[来源: RISC-V Debug Spec v1.0 §1 — Overview, §2.2 — DM Requirements]

### 4.2 Hart 状态机

每个 hart 在 DM 视角下处于以下四种状态之一：

```text
                  +----------+
                  |  不存在   |  <- 枚举结束或物理不存在
                  | (Nonexist)|
                  +----------+

   上电/存在  ->  +----------+
                 |  不可用   |  <- 复位/下电/热插入中
                 |(Unavail) |
                 +----------+
                      v
              +-------------------+
              |  运行中 (Running)   | <-———+
              |                    |      |
              |  正常执行指令       |      | halt 请求
              |  低功耗/等待中断    |      |
              +--------+----------+      |
                       | halt            |
                  +----v----+            |
                  | 已暂停  |————resume——+
                  |(Halted) |
                  |调试模式 |
                  +---------+
```

DM 通过寄存器位（{dmstatus-allhalted}, {dmstatus-anyhalted} 等）向调试器报告每个 hart 的状态。hart 状态转换必须在**1秒内**完成（典型实现只需几个时钟周期）。

[来源: RISC-V Debug Spec v1.0 §5 — Hart DM States]

### 4.3 运行控制（Run Control）

运行控制是 DM 最核心的功能，通过一组概念状态位实现：

```text
调试器视角的请求/响应机制:

  halt 流程:
  1. +-------------------------------+
     | 调试器写 dmcontrol.haltreq=1   |  -> hart 的 halt 请求位置位
  2. | hart 检测到 halt 请求位        |  -> 停止执行, 进入 Debug Mode
  3. | DM 状态: allhalted=1          |  -> 调试器确认 halt 成功
     +-------------------------------+

  resume 流程:
  1. +-------------------------------+
     | 调试器写 dmcontrol.resumereq=1 |  -> resume ack 清除
  2. | halted hart 收到 resume 请求   |  -> 恢复执行
  3. | resume ack 置位               |  -> 调试器看到 allrunning=1
     +-------------------------------+

  halt-on-reset 流程:
  1. +-------------------------------+
     | 调试器写 setresethaltreq=1     |  -> halt-on-reset 请求位设置
  2. | hart 被复位 (任何原因)          |  -> 复位完成后立即进入 Debug Mode
  3. | dcsr.cause=5 (reset)         |  -> 调试器可以调试从第一条指令开始
     +-------------------------------+
```

### 4.4 Abstract Commands

抽象命令是调试器通过 DM 操作 hart 寄存器/内存的标准途径。所有 DM 必须支持 Access Register 命令。

**命令类型**：

| 命令类型 (cmdtype) | 功能 | 是否必须 |
|:-------------------|:-----|:---------|
| 1 | **Access Register** — 读写 halted hart 的寄存器（GPR/CSR/FPR） | ✅ 强制 |
| 2 | **Quick Access** — halt → 执行 Program Buffer → 恢复，最低侵入 | ◇ 可选 |
| 3 | **Access Memory** — 从 hart 角度读写内存（物理或虚拟地址） | ◇ 可选 |

**Access Register 命令详细格式**：

```text
Command 寄存器 (32-bit):
  Bit [31:28]  — cmdtype = 1 (Access Register)
  Bit [27]     — aarsize (0=8-bit, 1=16-bit, 2=32-bit, 3=64-bit)
  Bit [24]     — aarpostincrement (访问后自动递增)
  Bit [23]     — postexec (完成后执行 Program Buffer)
  Bit [22]     — transfer (1=写入 0=读取)
  Bit [21]     — writeup (写入后更新 hart 状态)
  Bit [16]     — regno (寄存器编号, 见下方表格)

寄存器编号映射 (regno):
  0x0000-0x0FFF: GPR (x0-x31: 0x0000-0x01F)
  0x1000-0x1FFF: 用户 CSRs
  0x2000-0x2FFF: 仅调试可读的 hart 寄存器
  0x3000-0x3FFF: 机器模式 CSRs
  0x4000-0x4FFF: 监督模式 CSRs
  0xC000-0xFFFF: 虚拟/超监督模式 CSRs
```

**数据传输**：参数通过 Data 寄存器（dmi 地址 0x30-0x3F）传递。

- data0-data3：命令参数/返回值
- data4-data11：额外数据（128-bit 操作时）

**命令执行流程**：

```text
调试器                          DM
  |                             |
  +-- 检查 abstractcs.busy=0 --->|
  |                             |
  +-- 写入 data0-data3 (参数) -->|
  |                             |
  +-- 写入 command 寄存器 ------>| <- DM 开始执行命令
  |                             |
  +-- 轮询 abstractcs.busy ---->| <- DM 执行中
  |          <-------------------|
  |                             |
  +-- 读取 abstractcs.cmderr --->|
  |    = 0: 成功                |
  |    = 1: busy (不应该)       |
  |    = 2: 不支持              |
  |    = 3: 异常 (exception)    |
  |    = 4: 错误 (halt/resume)  |
  |                             |
  +-- 读取 data0-data3 (结果) -->|
  |                             |
```

[来源: RISC-V Debug Spec v1.0 §7 — Abstract Commands]

### 4.5 Program Buffer

Program Buffer 允许调试器在 halted hart 上执行任意指令序列——这是**最强大的调试能力**。

**架构**：

```text
Program Buffer 大小: {abstractcs.progbufsize} 个 32-bit 字
  最小: 1 (需要 impebreak 支持)
  典型: 2-16 个
  最大: 由实现决定

ProgBuf 访问方式:
  通过 DMI 寄存器 {progbuf0}..{progbufN-1} 填充
```

**执行流程**：

```text
1. 调试器写 Program Buffer (progbuf0..progbufN-1)
   -> 写入指令序列，必须以 ebreak / c.ebreak 结尾
2. 设置 command 寄存器的 postexec 位 + regno 选择
3. DM 让 hart 从 Program Buffer 执行指令序列
4. ebreak -> 返回 Debug Mode
5. 结果写入 data0-data3 供调试器读取

注意事项:
  - 如果执行序列不终止于 ebreak -> 调试器失去对 hart 的控制 ⚠️
  - 异常发生时 -> cmderr=3 (exception)
  - 支持 impebreak -> prog buf 末尾自动 ebreak (仅需 2 字即可高效调试)
```

**典型用途**：

| 用途 | Program Buffer 指令示例 | 替代方案 |
|:-----|:----------------------|:---------|
| 读 Cache-Line 大小 | `csrr a0, CSR_CACHE_LINE_SIZE; ebreak` | Abstract Access Register |
| 执行 `fence.i` | `fence.i; ebreak` | 无其他方式 |
| 触发 DMA | `write CSR; write MMIO; ebreak` | SBA 方式有限 |
| TLB 操作 | `sfence.vma; ebreak` | 无其他方式 |

### 4.6 System Bus Access (SBA)

SBA 提供了**不经过 hart** 访问系统内存/外设的能力，这在 hart 无法 halt 时尤其关键。

**SBA 核心特征**：

| 特征 | 说明 |
|:-----|:------|
| 地址类型 | 物理地址 |
| 支持宽度 | 8/16/32/64/128-bit (由实现决定) |
| 性能 | 远快于 Abstract Memory 命令（不需 halt hart） |
| 一致性 | 实现相关，可能需要调试器软件维护 |
| 侵入性 | **零侵入**（hart 完全不受影响） |

**SBA 寄存器**：

```text
{SBsbadress0-3}: 地址寄存器 (最多支持 128-bit 地址)
{Sbdata0-3}:     数据寄存器
{Sbcs}:           控制和状态
  sbversion:      SBA 版本
  sbbusy:         忙标志
  sberror:        错误信息
  sbaccess:       访问宽度 (8/16/32/64/128)
  sbaautoread:    自动读模式 (连续读取地址自动递增)
```

**自动读模式**：

```text
启用 sbaautoread -> 读取 sbdata0 -> 自动触发下一次读 -> 地址递增 ->
这是高性能批量内存读取的关键机制，适用于 dump 大块内存。
```

[来源: RISC-V Debug Spec v1.0 §8 — System Bus Access]

### 4.7 Hart 选择与多核调试

DM 支持灵活的多核选择机制：

```text
Hart 选择层级结构:

+-------------------------------------+
|           DM (1个)                    |
|                                      |
|  {hartsel} 寄存器 (20-bit)           |
|  -> 最大支持 2^20 = 1,048,576 harts  |
|                                      |
|  Hart Array Mask (可选)              |
|  -> 通过 hawindowsel + hawindow       |
|  -> 多 bit 同时选择                   |
|  -> hasel 选择是否启用                |
+-------------------------------------+

枚举 harts 的流程:
  1. 确定 HARTSELLEN (写全1读回)
  2. 从 index=0 开始选择
  3. 检查 allnonexistent / anynonexistent
  4. 如果存在: 读取 mhartid (关联物理 hart ID)
  5. 重复直到遇到不存在或到最大索引
```

**多核同步调试**：

```text
Halt Group 机制 (可选):
  group 0: 无组行为 (单个 halt/resume)
  group N: 组内任意 hart halt -> 所有组内 hart 都 halt
  -> 实现多核"停止同步"

Resume Group 机制 (可选):
  group 0: 无组行为
  group N: 组内任意 hart resume -> 所有组内 hart 都 resume

外部触发 (External Triggers):
  可以是跨 RISC-V/非 RISC-V 核的同步机制
  支持 halt/resume 双向触发信号
```

---

## 5. Trigger Module — Sdtrig ISA扩展

### 5.1 Sdtrig 概述

Sdtrig 是 RISC-V ISA 的标准扩展（通过 CSR 访问，而非 DMI），定义了 Trigger Module 的功能。这是操作系统可见的调试功能的核心——Linux 内核的 HW breakpoint/perf 等均基于此。

**Sdtrig 的核心能力**：

```text
Trigger Module 可以:
  1. ✅ 在指定地址执行指令时 -> 断点 (breakpoint)
  2. ✅ 在指定地址加载/存储时 -> 观测点 (watchpoint)
  3. ✅ 按指令计数触发 -> 性能采样
  4. ✅ 在特定中断/异常时触发 -> 事件追踪
  5. ✅ 触发后执行操作: 断点异常 / 进入调试模式 / 追踪输出

Trigger 不限于 halt hart -> action=2 可以只做 trace 标记
```

### 5.2 Trigger 类型

Sdtrig 定义了以下几种 Trigger 类型：

| 类型码 | 名称 | CSR 寄存器 | 功能 |
|:------|:-----|:-----------|:-----|
| 0 | **No Trigger** | — | 该 trigger 槽不存在 |
| 1 | **Legacy Trigger** | — | 兼容旧版本 |
| 2 | **mcontrol** | tdata1~tdata2 | 指令/数据地址匹配 (XLEN 地址) |
| 3 | **icount** | tdata1 | 指令计数触发 |
| 4 | **itrigger** | tdata1 | 中断触发 |
| 5 | **etrigger** | tdata1 | 异常触发 |
| 6 | **mcontrol6** | tdata1~tdata3 | **增强版**地址匹配 (XLEN 地址+全功能) |
| 12 | **tmexttrigger** | tdata1 | 外部触发 |
| 15 | **Chain Trigger** | tdata1 | 链式触发 (组合多个 trigger) |

### 5.3 mcontrol6 — 最常用的 Trigger 类型

mcontrol6 是地址匹配类 Trigger 的最新版本（取代 mcontrol），支持最丰富的配置：

**tdata1 (mcontrol6) 寄存器布局**：

```text
Bit [XLEN-1: XLEN-4] — type = 6
Bit [XLEN-5]          — dmode (仅在 Debug/M-mode 可写)
Bit [XLEN-6]          — maskmax (地址掩码能力)
Bit [26:21]           — hit (自上次读后触发次数)
Bit [20]              — select (0=地址匹配 1=数据匹配)
Bit [19]              — timing (0=执行前触发 1=执行后触发)
Bit [18]              — sizelo, sizehi (数据访问宽度选择)
Bit [17]              — action (0=断点 1=进入调试 2=追踪 3=链式)
                      — chain (链式触发)
                      — match (匹配模式: =/>=/!=/范围等)
                      — m, s, vs, vu, u (各特权级使能位)
Bit [0]               — enable
```

**核心配置能力**：

| 配置项 | 可选值 | 说明 |
|:-------|:-------|:------|
| `action` | 0-3 | 0=断点异常(ebreak-like) 1=进入Debug Mode 2=Trace输出 |
| `timing` | 0-1 | 0=执行前(inst) 1=执行后(store data) |
| `select` | 0-1 | 0=地址匹配 1=数据值匹配 |
| `match` | 0-7 | 0=等于 1=大于等于 2=不等于 4=范围 5=掩码 6=不等掩码 |
| `m/s/vs/vu/u` | 0/1 | 分别在 M/S/VS/VU/U 模式下使能 |

**tdata2 — 地址比较值**：

```text
tdata2 存储匹配地址:
  - 物理/虚拟地址 (根据 mode bit)
  - 必须能保存所有有效地址（包括不完备地址位宽时零扩展）
  - WARL 语义 (写入任意值，读回硬件支持的最近值)
```

**tdata3 — 数据比较掩码 (仅 mcontrol6)**：

```text
tdata3 为 mcontrol6 独有:
  - 数据值比较掩码 (与 select=1 配合)
  - 粒度可低至 byte 级别
```

### 5.4 icount — 指令计数 Trigger

icount 用于**指令执行计数**触发，是性能采样和代码覆盖率的硬件基础：

| 字段 | 说明 |
|:-----|:------|
| `count` | 计数值 (在触发前等待的指令数) |
| `m/s/vs/vu/u` | 各特权级计数 |
| `action` | 触发后操作 |
| `hit` | 触发标记 |

**典型用例**：

```text
perf 采样: 设置 icount.count = 100000
-> 每 100,000 条指令后触发一次
-> action=0 (断点异常) -> perf 记录 PC/Callchain
```

### 5.5 itrigger 和 etrigger — 中断/异常 Trigger

用于调试中断处理和异常处理路径——这是 ARM/x86 难以直接提供的能力：

| Trigger | 触发事件 | 典型用途 |
|:--------|:---------|:---------|
| **itrigger** | 指定中断类型发生时 | 调试中断延迟/嵌套问题 |
| **etrigger** | 指定异常类型发生时 | 调试缺页/非法指令等 |
| **tmexttrigger** | 外部硬件信号 | SoC 级跨核/外设同步调试 |

### 5.6 Trigger 优先级

当多个 trigger 同时触发时，按以下优先级处理（来自 Privileged 规范的异常优先级表）：

```text
优先级 (高->低):
  1. itrigger/etrigger (指令/数据读取阶段)
  2. mcontrol/mcontrol6 指令地址匹配 (执行前)
  3. 地址转换异常 (page fault, access fault)
  4. 地址错位异常
  5. mcontrol/mcontrol6 加载/存储地址匹配 (地址后)
  6. mcontrol/mcontrol6 加载数据匹配 (数据后)
```

### 5.7 Native Trigger — 操作系统可见的触发机制

当 `action=0` 时，trigger 作为**断点异常**（breakpoint exception，exception code=3）触发，这是 Linux 内核利用 Sdtrig 的核心途径：

```text
Native Trigger 异常流:

trigger 条件满足
    v
发生 breakpoint exception (exception code 3)
    v
检查 medeleg[3] 是否已委派
    v
+-- 已委派给 S-mode -> S-mode trap handler
+-- 未委派 -> M-mode trap handler
              v
  M-mode handler: 检查 mtval/mcause -> 喂给 S-mode 或处理
```

**关键注意事项**：

- **重入问题**：如果在断点处理程序中再次触发（如在 `ebreak` handler 中触发 m-mode trigger），会导致 `mepc`/`mcause` 被覆盖 → hart 无法恢复
- **解决方案 A**：硬件在 MIE=0 时禁止 action=0 trigger 匹配
- **解决方案 B**：实现 `tcontrol` CSR（{mte/mpte} 位控制 M-mode 下 trigger 禁止）
- 由于 `tcontrol` 不支持 S-mode 访问，使用方案 A 且需要委派断点给 S-mode 的芯片更常见

[来源: RISC-V Debug Spec v1.0 §10 — Native Triggers]

---

## 6. Trace 与性能监控

### 6.1 性能计数器 — Zihpm / Zicntr

RISC-V 通过两个标准扩展提供硬件性能计数能力：

| 扩展 | CSR | 功能 |
|:-----|:----|:------|
| **Zicntr** | `cycle` / `time` / `instret` | 基本计数器（周期/时间/指令数），所有 harts 必须有 |
| **Zihpm** | `hpmcounter3` ~ `hpmcounter31` | 最多 29 个硬件性能计数器（实际数量由实现定） |

**性能计数器 CSR**：

```text
Machine 模式:
  mcycle      — 64-bit 周期计数器
  minstret    — 64-bit 指令退休计数器
  mhpmcounter3-31 — 64-bit 硬件性能计数器
  mhpmevent3-31 — 性能事件选择寄存器

Supervisor 模式 (通过指令化读取):
  cycle       — 读取 mcycle (通过 time 伪指令)
  instret     — 读取 minstret
  hpmcounter3-31 — 读取对应的 mhpmcounter

Read-only vs. Writable:
  - cycle/instret: 计数器是 read-only (安全原因)
  - mcycle/minstret: M-mode 可写 (用于 OS context save/restore)
  - S-mode 能否访问: 由 mcounteren CSR 控制
```

### 6.2 每个触发器可指定的性能事件

Zihpm 的事件选择由芯片厂商自行定义（不像 ARM PMUv3 有标准化事件集）。Linux 内核通过设备树或 SBI 来枚举性能事件。

**常见的厂商自定义事件** (示例，非标准化)：

| 事件号 | 事件 | 典型用途 |
|:-------|:-----|:---------|
| 0-2 | cycle/instret/time | 基本统计 |
| 3 | L1 I-cache miss | 缓存效率分析 |
| 4 | L1 D-cache miss | 缓存效率分析 |
| 5 | L2 cache miss | 内存层级分析 |
| 6 | TLB miss | 页表效率 |
| 7 | Branch mispredict | 分支预测分析 |
| 8 | Load stall cycles | 内存延迟分析 |
| 9 | Store stall cycles | 写缓冲分析 |
| 10 | ITLB miss | 指令 TLB |
| 11 | DTLB miss | 数据 TLB |

[来源: RISC-V Privileged Spec v1.12 §3.1 — Counters]

### 6.3 SBI PMU 扩展

SBI (Supervisor Binary Interface) 为 OS 提供了标准化的 PMU 配置接口，隔离了芯片差异：

**SBI PMU 功能**：

```text
SBI Extension: PMU (EID: 0x50554D)

功能列表:
  1. sbi_pmu_num_counters()       — 获取 PMU 计数器数量
  2. sbi_pmu_counter_get_info()   — 获取计数器属性（位宽/类型/事件）
  3. sbi_pmu_counter_config_matching() — 配置计数器与事件匹配
  4. sbi_pmu_counter_start()      — 启动计数
  5. sbi_pmu_counter_stop()       — 停止计数
  6. sbi_pmu_counter_fw_read()    — 读取固件计数器
  7. sbi_pmu_snapshot_set_shmem() — 设置快照共享内存 (批量读取优化)
```

**SBI PMU 的优势**：

- OS 不需要知道具体芯片的 MHPMEVENT 编码
- 固件计数器（FW counters）可提供 SBI 层的虚拟化事件
- 快照 (Snapshot) 功能允许一次 SBI 调用读取所有计数器

---

## 7. E-Trace 与 Processor Trace

### 7.1 RISC-V E-Trace (Nexus Trace)

E-Trace 标准已获批准（2024年），定义了嵌入式系统的指令跟踪能力：

```text
E-Trace 核心概念:

  Trace Source (跟踪源)
    -> 监控 hart 的指令退休流
    -> 压缩后输出 Trace Messages

  Trace Encoder (跟踪编码器)
    -> 使用分支追踪编码（BTE）算法
    -> 只记录控制流变化 (分支/跳转/异常)
    -> 通过"最后一个分支地址 + 当前PC"重建执行流

  Trace Output (跟踪输出)
    -> MIPI System Trace Protocol (STP)
    -> Parallel Trace Interface (PTI)
    -> 片外 Trace 端口 / DDR 存储
```

**E-Trace 编码效率**（典型值）：

| 场景 | 压缩率 | 每条指令的 Trace Bits |
|:-----|:-------|:---------------------|
| 全线性执行 | >100:1 | <0.1 bits/inst |
| 密集分支 (SPEC CPU) | 5:1 ~ 30:1 | 0.3-2 bits/inst |
| 中断/异常频繁 | 2:1 ~ 5:1 | 2-5 bits/inst |

[来源: RISC-V E-Trace (Nexus Trace) Specification v1.0, 2024]

### 7.2 Processor Trace (开发中)

针对高性能 CPU 的更先进的指令跟踪方案，对标 Intel PT / ARM ETM：

| 特性 | E-Trace | Processor Trace (开发中) |
|:-----|:--------|:------------------------|
| 目标 | 嵌入式/MCU | 高性能/应用处理器 |
| 压缩率 | 中 | 更高 (使用更复杂的编码) |
| 支持超标量 | 有限 | 全支持 |
| 功耗 | 低 | 较高 |
| 管道数量 | 单发射为主 | 多发射/乱序 |
| 状态 | ✅ 已批准 | 🔧 v0.5 Draft |

---

## 8. RISC-V 调试安全模型

### 8.1 Authentication (认证机制)

DM 支持认证机制，保护 IP 不被未授权访问：

```text
认证状态机:

    +------------+
    | 未认证     | <- 上电/复位默认
    | (authenticated=0)|
    +------+-----+
           | 认证成功 (通过 {authdata} 写入密钥)
    +------v-----+
    | 已认证     | <- 可访问所有 DM 功能
    | (authenticated=1)|
    +------------+

未认证时的限制:
  - 所有 DM DMI 寄存器读回 0（除以下例外）
  - 所有 DMI 写入被忽略（除以下例外）

  可读写的例外寄存器:
  - {dmstatus}.authenticated
  - {dmstatus}.authbusy
  - {dmstatus}.version (tinfo)
  - {dmcontrol}.dmactive
  - {authdata} (用于输入密钥)
```

### 8.2 熔断机制

```text
Fuse 控制:
  - DM 可配置熔丝 (Fuse) 永久禁用调试功能
  - 制造完成后熔断 -> 调试功能永久锁定
  - 不影响正常执行，仅禁用 Debug Mode 进入路径
```

### 8.3 调试对安全的影响

```text
调试功能带来的安全风险:
  1. 通过 SBA 读取任意物理内存 -> 内核/用户数据泄露
  2. 通过 Program Buffer 执行任意指令 -> 完全控制 hart
  3. 通过 halt-on-reset 拦截启动流程 -> Secure Boot 绕过

  缓解措施:
  - 熔断: 量产产品永久禁用 DM
  - 认证: 只在调试会话期间启用
  - 物理安全: JTAG 引脚不暴露/有物理锁
```

---

## 9. Linux 内核调试诊断功能总览

### 9.1 整体支持状态

基于 Linux v7.2-rc1 内核（2026-07），RISC-V 架构的各个调试/诊断功能支持状态如下：

| 子系统 | 状态 | Kconfig | 内核版本支持 |
|:-------|:-----|:--------|:------------|
| **perf_event** | ✅ ok | HAVE_PERF_EVENTS | v5.1+ |
| **PMU (SBI)** | ✅ ok | RISCV_PMU_SBI | v6.0+ |
| **hw_breakpoint** | ✅ ok | HAVE_HW_BREAKPOINT | v6.0+ |
| **KGDB** | ✅ ok | HAVE_ARCH_KGDB | v6.3+ |
| **Kprobes** | ✅ ok | HAVE_KPROBES | v6.7+ |
| **Kretprobes** | ✅ ok | HAVE_KRETPROBES | v6.7+ |
| **Uprobes** | ✅ ok | ARCH_SUPPORTS_UPROBES | v6.10+ |
| **KASAN** | ✅ ok | HAVE_ARCH_KASAN | v6.0+ |
| **KCOV** | ✅ ok | ARCH_HAS_KCOV | v6.4+ |
| **Ftrace** | ✅ ok | HAVE_FUNCTION_TRACER | v5.10+ |
| **Kprobe-on-ftrace** | 🔧 TODO | HAVE_KPROBES_ON_FTRACE | — |
| **Optprobes** | 🔧 TODO | HAVE_OPTPROBES | — |
| **GCOV** | ✅ ok | ARCH_HAS_GCOV_PROFILE_ALL | v6.2+ |
| **Tracehook** | ✅ ok | HAVE_ARCH_TRACEHOOK | v5.0+ |
| **Stackprotector** | ✅ ok | HAVE_STACKPROTECTOR | v5.5+ |
| **Membarrier** | ✅ ok | ARCH_HAS_MEMBARRIER_SYNC_CORE | v6.5+ |
| **Shadow stack** | ✅ ok | — | v7.0+ (Zicfiss) |

[来源: Linux Kernel Documentation — feature-status on riscv architecture]

### 9.2 调试诊断功能依赖关系

```text
用户态调试 (GDB/LLDB)
    v ptrace
+-- Tracehook (arch_ptrace/system_call)
+-- HW breakpoint (perf hw_breakpoint)
|   +-- Sdtrig trigger CSRs
|
内核态调试 (kgdb/kprobes/ftrace)
+-- KGDB (serial-based debugger)
+-- Kprobes (动态插桩)
|   +-- breakpoint 指令插桩
+-- Ftrace (函数追踪)
|   +-- mcount/fentry 调用
|
运行时诊断
+-- KASAN (内存错误检测)
|   +-- shadow memory + compiler instrumentation
+-- KCOV (覆盖率引导的模糊测试)
|   +-- compiler instrumentation
+-- Perf (性能分析)
|   +-- PMU counters + SBI
|
追踪框架
+-- Ftrace events
+-- Tracepoints (静态追踪点)
+-- eBPF (动态追踪程序)
```

---

## 10. perf_event 子系统与 PMU 支持

### 10.1 架构

RISC-V Linux 的 PMU 支持完全基于 SBI 规范（`RISCV_PMU_SBI`），通过 SBI PMU 扩展统一访问各芯片厂商的 PMU 硬件：

```text
perf 用户态 (perf stat/record/report)
    v sys_perf_event_open
Linux perf_event 子系统 (kernel/events/)
    v
RISC-V PMU 驱动 (arch/riscv/kernel/perf_event.c)
    v SBI 调用
SBI PMU 扩展 (M-mode Firmware / OpenSBI)
    v CSR 访问
芯片 PMU 硬件 (Zihpm + 自定义事件)
```

### 10.2 支持的 Perf 功能

**硬件事件**：

```bash
# perf stat -e 循环查看可用的硬件事件
perf list

# 典型可用事件 (通过 SBI PMU 查询):
  cycles                  [Hardware event]
  instructions            [Hardware event]
  cache-references        [Hardware event]
  cache-misses            [Hardware event]
  branch-instructions     [Hardware event]
  branch-misses           [Hardware event]

# 芯片自定义事件 (通过 SBI counter info 获取):
  rNNN                    [Raw hardware event descriptor]
```

**perf 采样模式**：

```bash
# 周期采样 (基于 cycles)
perf record -e cycles -F 1000 ./program

# 指令采样
perf record -e instructions -F 10000 ./program

# 调用链采样 (perf 栈采样 + dwarf 或 fp)
perf record -e cycles --call-graph fp ./program

# 最后分支记录 (LBR 等价功能 — 芯片可选)
# RISC-V 可通过 trigger icount + 记录堆栈实现类似功能
```

### 10.3 SBI PMU 内核代码流程

```text
perf_event_open -> perf_install_in_context
    v
pmu->add(event) -> riscv_pmu_add(event, flags)
    v
event->hw.config -> 映射到 hw counter
    v
pmu->start(event, PERF_EF_START) -> riscv_pmu_start(event, flags)
    v
sbi_pmu_counter_config_matching(counter, config)
    v (SBI 调用)
M-mode 配置 mhpmevent[counter] + mhpmevent[counter]
    v
启动计数 -> 硬件开始累加
    v
perf 中断 或 perf_event_overflow()
    v
pmu->handle_irq() -> 读取计数器 + 记录采样 + 重新配置
```

### 10.4 快照读取优化

SBI PMU 的快照（Snapshot）机制允许批量化读取所有计数器：

```text
传统模式: 每个计数器一次 SBI 调用 -> 29次 SBI 调用 -> 高延迟

快照模式: 一次性映射共享内存 -> M-mode 批量填充
    -> 1次 SBI 调用配置 + 1次内存读取全部 -> 10x+ 加速
    -> 对 perf stat 场景至关重要（减少 profiler 对被测程序的干扰）
```

---

## 11. 硬件断点/观测点 — hw_breakpoint

### 11.1 概述

hw_breakpoint 是 Linux 内核利用 Sdtrig 硬件触发能力实现的高效断点/观测点子系统。

**能力对比**：

| 能力 | x86 | ARM64 | RISC-V (Sdtrig) |
|:-----|:----|:------|:----------------|
| 硬件断点数量 | 4 (DR0-DR3) | 2-16 (BRP) | **实现相关** (min=1, max=2^m) |
| 观测点数量 | 4 (同寄存器) | 2-16 (WRP) | **与断点共享 trigger 槽** |
| 数据观测 | 地址+长度 | 地址+掩码 | **地址+掩码+数据值** |
| 指令断点 | ✅ | ✅ | ✅ |
| 触发后动作 | 只能 #DB | exception 或 halt | **3种: exception/debug/trace** |
| 链式触发 | ❌ | ❌ | ✅ (chain trigger 组合多条件) |

### 11.2 Linux hw_breakpoint 架构

```text
用户: perf_event_open (attr.type = PERF_TYPE_BREAKPOINT)
    v
kernel/events/hw_breakpoint.c (通用层)
    v
arch/riscv/kernel/hw_breakpoint.c (arch 实现)
    v
CSR 操作: tselect -> tdata1 -> tdata2 -> tdata3
    v
Sdtrig Trigger Module 硬件
```

**注册流程**：

```text
1. reserve_bp_slot() -> 检查 trigger 槽是否可用
2. arch_install_hw_breakpoint(bp)
   -> 遍历找到空闲 trigger
   -> 写 tselect 选择 trigger 槽
   -> 写 tdata1 (type=6, mcontrol6 配置)
        - action=0 (breakpoint exception)
        - select=0 (地址匹配) / select=1 (数据匹配)
        - match 模式配置
        - m/s/u 等特权级使能
   -> 写 tdata2 (地址值)
   -> 写 tdata3 (数据掩码, 如果是数据匹配)
   -> 使能 trigger
3. breakpoint exception handler -> deliver_signal(TRAP_TRACE)
4. arch_uninstall_hw_breakpoint(bp) -> 清理 trigger
```

### 11.3 GDB 中使用 hw breakpoint

```bash
# 硬件断点
(gdb) hbreak *0x80200000

# 硬件观测点
(gdb) watch *(int*)0x80600000        # 写入监测
(gdb) rwatch *(int*)0x80600000        # 读取监测
(gdb) awatch *(int*)0x80600000        # 读写监测

# 数据访问范围 (Sdtrig 特有优势 — 掩码匹配)
(gdb) watch -location -mask 0xFF000000 *addr
```

### 11.4 限制与注意事项

| 限制 | 说明 | 影响 |
|:-----|:-----|:------|
| trigger 数量有限 | 芯片实现决定（典型 2-16 个） | 大型调试中可能不够用 |
| CSRs WARL 语义 | 读回值可能与写入值不同 | 调试器必须 read back 验证 |
| 多核 trigger 一致 | 每个 hart 独立 trigger 寄存器 | 需要为每个核单独设置 |
| 数据值匹配精度 | 依赖于芯片实现 | 不是所有 Sdtrig 实现都支持字节粒度数据匹配 |

---

## 12. KGDB — 内核调试器

### 12.1 RISC-V KGDB 支持

KGDB 是 Linux 内核的远程调试器，通过串口或网络（kgdboe）连接到 GDB：

**Kconfig**：

```text
Kernel hacking -> KGDB: kernel debugging with remote gdb
  -> HAVE_ARCH_KGDB (RISC-V: ✅)
```

**支持的 RISC-V KGDB 特性**：

| 特性 | 状态 | 代码位置 |
|:-----|:------|:---------|
| 寄存器读写 | ✅ | arch/riscv/kernel/kgdb.c |
| 软件断点插入 | ✅ | 使用 `ebreak` 指令替换 |
| 单步执行 | ✅ | 使用 Sdtrig icount 或软件单步 |
| 内存读写 | ✅ | 标准内核 API |
| 多核调试 (SMP) | ✅ | 使用 IPI 停止所有核 |
| HW breakpoint | ✅ | 通过 hw_breakpoint 接口 |
| 调试信息输出 | ✅ | gdbstub 实现 |

### 12.2 RISC-V KGDB 调试流程

```text
启动 KGDB 的方法:
  1. 内核参数: kgdbwait kgdboc=ttyS0,115200
  2. 运行时激活: echo ttyS0 > /sys/module/kgdboc/parameters/kgdboc
                  echo g > /proc/sysrq-trigger

多核调试:
  - KGDB 通过 kgdb_roundup_cpus() 发送 IPI
  - 所有核停止 -> 所有核进入 kgdb 断点处理
  - GDB 通过 "info threads" 查看各核状态
  - GDB 通过 "thread N" 切换到指定核
```

**RISC-V 实现细节**：

```text
软件断点（SW breakpoint）:
  替换目标地址的指令为 ebreak (0x00100073)
  触发后 -> exception code=3 (breakpoint)
  内核异常处理 -> kgdb 钩子 -> gdbstub -> GDB session

单步执行:
  方式1: 设置 trigger icount.count=1
  方式2: 替换指令为 ebreak, 执行后在下一指令位再次替换
  -> RISC-V 优先使用 trigger 方式 (更精确)
```

---

## 13. Kprobes/Uprobes — 动态探针

### 13.1 Kprobes

Kprobes 允许在内核运行的任意位置插入动态探针，用于故障诊断和性能分析。

**RISC-V Kprobes 实现原理**：

```text
Kprobe 插入流程:

1. 用户选择目标地址 (如函数入口)
2. kprobe 替换该指令为 ebreak (0x00100073)
   -> 保存原始指令到 p->ainsn
3. 执行到 ebreak 时触发断点异常
4. 异常处理程序:
   - 保存 CPU 上下文
   - 执行 pre_handler (用户注册的回调)
   - 单步执行原始指令 (通过模拟或单步模式)
   - 执行 post_handler
   - 恢复 CPU 上下文
   - 返回到下一条指令

原始指令恢复:
  - RISC-V 应用指令压缩 (C extension) -> 指令长度 2 或 4 字节
  - Kprobes 必须处理混合长度 (使用 ilen 获取指令长度)
  - 替换时需要考虑对齐约束 (ebreak 是 4 字节, c.ebreak 是 2 字节)
```

**Kprobes 性能**（典型值，依赖于实现）：

| 操作 | 延迟 (nsec) | 说明 |
|:-----|:-----------|:-----|
| 未插 kprobe 的执行 | 0 | 无开销 |
| ebreak 触发 → pre handler | ~200-500 | 异常+上下文切换 |
| 单步执行原始指令 | ~100-300 | 模拟执行 |
| Kretprobe 额外开销 | ~200 | 函数返回探测 |

### 13.2 Kretprobes

Kretprobes 捕获函数返回，获取返回值和追踪调用链。

```text
Kretprobe 实现原理:
  1. 在函数入口插入 kprobe
  2. pre_handler: 修改返回地址 -> 指向 trampoline
  3. trampoline 保存真正的返回值
  4. 执行 return_handler (用户回调)
  5. 恢复返回值 -> 返回到真正的调用者
```

### 13.3 Uprobes

Uprobes 是 Kprobes 的用户空间版本，在用户态程序地址插入探针。

```text
Uprobes 流程:
  1. 用户指定: PID + 地址 + 回调
  2. 内核安装 uprobe (替换指令为 ebreak/c.ebreak)
  3. 进程执行到该地址 -> 断点异常 -> mm->mmap_sem -> uprobe handler
  4. 执行用户回调 -> 单步执行原始指令 -> 恢复
```

**RISC-V Uprobes 特殊考虑**：由于 RISC-V 使用压缩指令（C 扩展），uprobes 需要处理 2/4 字节混合长度，并且需要考虑指令对齐约束。

### 13.4 待完善的功能

| 功能 | 状态 | 说明 |
|:-----|:------|:------|
| **Kprobe-on-ftrace** | 🔧 TODO | 利用 ftrace 的 fentry 替代 ebreak, 降低开销 |
| **Optprobes** | 🔧 TODO | 优化探针: 使用直接跳转替代 ebreak |
| **Kprobe 批量** | 🔧 TODO | 一次性插入大量 kprobe 的性能优化 |

---

## 14. KASAN/KCOV — 内存错误检测与覆盖率

### 14.1 KASAN (Kernel Address Sanitizer)

KASAN 使用编译时插桩 + 运行时代理内存检查来检测内核内存错误（越界/UAF）。

**RISC-V KASAN 支持**：

| 项目 | 说明 |
|:-----|:------|
| Kconfig | HAVE_ARCH_KASAN (✅) |
| Shadow 内存映射 | 固定偏移: `KASAN_SHADOW_OFFSET` |
| 映射方法 | 线性映射 (与 x86/arm64 类似) |
| 影子粒度 | 1 byte shadow : 8 bytes 内存 |
| 支持类型 | Generic KASAN (非 HW_TAGS) |

**RISC-V KASAN 内存布局**：

```text
典型的 RISC-V SV39 KASAN 布局:

0xFFFFFFFF  +------------------+  <- 内核空间顶
            |  模块/修复映射    |
            +------------------+
            |  KASAN Shadow    |  <- 影子内存 (1/8 比例)
            +------------------+
            |  直接映射区       |  <- 线性映射
            +------------------+
            |  vmalloc          |
            +------------------+
            |  固定映射         |
0xFFFFFFC0  +------------------+  <- 内核空间底
```

**Shadow 内存计算** (SV39)：

```text
Shadow 基址 = KASAN_SHADOW_START
对每个 8-bytes 的内存访问:
  shadow_index = (addr - DIRECT_MAP_START) >> 3
  shadow_addr = KASAN_SHADOW_START + shadow_index
  如果 shadow[addr] == 0 -> 可访问 ✅
  如果 shadow[addr] != 0 -> 可能非法 ❌ (比较类型)
```

### 14.2 KCOV (Coverage-guided Fuzzing)

KCOV 是 syzkaller 等模糊测试工具使用的覆盖率收集机制：

**RISC-V KCOV 支持**：

```text
Kconfig: HAVE_ARCH_HAS_KCOV (✅, 内核 v6.4+)

实现:
  - 使用编译器 `-fsanitize-coverage=trace-pc` 插桩
  - 运行时记录每个分支的 PC 值到 per-task 缓冲区
  - syzkaller 通过 /sys/kernel/debug/kcov 读取

RISC-V 注意事项:
  - 需要处理压缩指令下的 PC 对齐 (C extension)
  - 对 RV64 的指令 2/4 字节混合编码的支持已验证
```

---

## 15. Ptrace — 用户态调试接口

### 15.1 RISC-V Ptrace 支持

ptrace 是用户态调试器（GDB/LLDB）与内核调试功能之间的桥梁。

**支持的 Ptrace 请求**（RISC-V 相关）：

| Ptrace 请求 | 功能 | 状态 |
|:------------|:-----|:------|
| `PTRACE_PEEKTEXT` / `PTRACE_POKETEXT` | 读写内存 | ✅ |
| `PTRACE_GETREGSET` / `PTRACE_SETREGSET` | 读写寄存器 | ✅ |
| | NT_PRSTATUS: 通用寄存器 | ✅ |
| | NT_FPREGSET: 浮点/向量寄存器 | ✅ |
| | NT_RISCV_VECTOR: RISC-V 向量扩展寄存器 | ✅ v6.5+ |
| | NT_RISCV_CSR: 特殊 CSR 访问 | ✅ v6.7+ |
| `PTRACE_SINGLESTEP` | 单步执行 | ✅ (通过 trigger icount) |
| `PTRACE_CONT` | 继续执行 | ✅ |
| `PTRACE_SYSCALL` | 系统调用追踪 | ✅ |
| `PTRACE_SET_SYSCALL` | 修改系统调用号 | ✅ v6.8+ |
| `PTRACE_GET_SYSCALL_INFO` | 获取系统调用信息 | ✅ v6.8+ |

**RISC-V 独有的 ptrace 能力——CSR 暴露**：

```text
PTRACE_GETREGSET + NT_RISCV_CSR (v6.7+):
  允许调试器直接读取以下 CSR:
  - sstatus, sie, stvec, sscratch, sepc, scause, stval, sip
  - satp (页表根)

  这对调试虚拟内存配置、中断状态和异常处理路径至关重要。
```

**Tracehook 实现**：

```c
// arch/riscv/kernel/ptrace.c 核心流程
static long riscv_syscall_trace(struct pt_regs *regs, long syscall)
{
    // 1. 检查是否被 ptrace 追踪
    // 2. 调用 tracehook_report_syscall_entry/exit
    // 3. 支持 syscall 号的修改 (用于 seccomp)
    // 4. 返回修改后的 syscall 号
}
```

### 15.2 单步执行实现

RISC-V 的单步执行通过 Sdtrig icount trigger 实现：

```text
1. ptrace 请求 PTRACE_SINGLESTEP
2. 内核设置 Sdtrig icount trigger:
   tdata1.type = 3 (icount)
   tdata1.count = 1 (执行一条指令后触发)
   tdata1.action = 1 (进入 Debug Mode)
   tdata1.s = 1 (在 S-mode 下有效)
3. 目标进程执行 1 条指令 -> trigger 触发
4. -> si_code = TRAP_TRACE -> 内核通知 ptracer
5. 清理 trigger
6. ptracer 获得控制权 (waitpid 返回)
```

---

## 16. RISCV_HWPROBE 与 SBI 调试接口

### 16.1 sys_riscv_hwprobe

Linux 内核提供 RISC-V 专用的硬件探测系统调用：

```c
struct riscv_hwprobe {
    __s64 key;    // 探测键 (输入时填充)
    __u64 value;  // 探测值 (内核返回)
};

long sys_riscv_hwprobe(struct riscv_hwprobe *pairs,
                       size_t pair_count,
                       size_t cpusetsize,
                       cpu_set_t *cpus,
                       unsigned int flags);
```

**调试/诊断相关的 HWPROBE Key**：

| Key | 返回值 | 用途 |
|:----|:-------|:------|
| `RISCV_HWPROBE_KEY_MVENDORID` | 厂商 ID (JEDEC 编码) | 调试器识别芯片 |
| `RISCV_HWPROBE_KEY_MARCHID` | 架构 ID | 识别微架构版本 |
| `RISCV_HWPROBE_KEY_MIMPID` | 实现 ID | 识别芯片版本 |
| `RISCV_HWPROBE_KEY_MISALIGNED_SCALAR_PERF` | 未对齐访问性能 | 诊断性能问题 |
| `RISCV_HWPROBE_KEY_ZICBOZ_BLOCK_SIZE` | Cache 块大小 | 优化 cache 操作 |
| `RISCV_HWPROBE_KEY_TIME_CSR_FREQ` | time CSR 频率 | 性能计数器校准 |

**反向探测**（`RISCV_HWPROBE_WHICH_CPUS` flag）：

```text
核心用途: 识别具有特定硬件特性的 CPU 集合
场景: 异构 big.LITTLE 场景下,
  查询支持向量扩展 V 的 CPU -> 只在那些核上调度向量任务
```

### 16.2 SBI 调试控制台 (DBCN)

SBI DBCN (Debug Console) 扩展提供了独立于 UART 的调试输出通道：

```text
SBI Extension DBCN (EID: 0x4442434E)

功能:
  sbi_debug_console_write(enum sbi_dbcn_write_type type,
                          unsigned long *out_ecode,
                          unsigned long *out_len)
  sbi_debug_console_read(unsigned long *out_ecode)

优势:
  - 即使内核崩溃 (panic)，SBI 控制台仍然可用
  - 不依赖 UART 驱动、DMA 控制器等复杂外设
  - 通过 M-mode firmware 保证调试输出通道
  - 适合 KGDB 的早期调试 (kgdboc 可以绑定 SBI DBCN)
```

### 16.3 SBI Reset & Shutdown

SBI System Reset 扩展在诊断故障后用于恢复系统：

```text
sbi_system_reset(uint32_t reset_type, uint32_t reset_reason)

reset_type:
  0: SHUTDOWN (关机)
  1: COLD_REBOOT (冷重启)
  2: WARM_REBOOT (热重启)

reset_reason:
  0: NO_REASON
  1: SYSTEM_FAILURE (系统故障)

用途: watchdog 触发后 -> SBI reset -> 系统恢复
```

---

## 17. Ftrace/Tracepoint — 内核追踪框架

### 17.1 Ftrace

Ftrace 是 Linux 内核的轻量级函数追踪框架。

**RISC-V Ftrace 支持**：

| 功能 | 状态 | 说明 |
|:-----|:------|:------|
| `HAVE_FUNCTION_TRACER` | ✅ | 函数入口 `mcount`/`fentry` + `-pg` 编译 |
| `HAVE_FUNCTION_GRAPH_TRACER` | ✅ | 函数调用图追踪 |
| `HAVE_DYNAMIC_FTRACE` | ✅ | 动态 ftrace (选择性地启用追踪) |
| `HAVE_FTRACE_MCOUNT_RECORD` | ✅ | mcount 记录 (快速查找所有可追踪点) |
| `HAVE_SYSCALL_TRACEPOINTS` | ✅ | 系统调用追踪点 |
| `TRACING_SUPPORT` | ✅ | 全部追踪支持 |

**RISC-V 动态 Ftrace 实现**：

```text
初始化时:
  编译器在所有函数入口插入 2 字节 nop (c.nop) 或 4 字节 nop
  mcount 记录表记录所有函数入口位置

启用追踪时:
  将函数入口 nop 替换为指向 ftrace_caller 的跳转
  RISC-V 使用 auipc + jalr 组合 (单次 8 字节, 2 条指令)

禁用追踪时:
  将跳转指令替换回 nop
```

**ftrace 的典型使用场景**：

```bash
# 开启特定函数的追踪
echo function > /sys/kernel/tracing/current_tracer
echo riscv_pmu_start > /sys/kernel/tracing/set_ftrace_filter
cat /sys/kernel/tracing/trace

# 函数调用图
echo function_graph > /sys/kernel/tracing/current_tracer
echo do_page_fault > /sys/kernel/tracing/set_ftrace_filter
```

### 17.2 Tracepoints

Tracepoints 是内核中的静态追踪点，性能开销远低于 kprobe（启用时 ≈0，采集时 ~ns 级）：

```bash
# 查看所有 tracepoints
ls /sys/kernel/tracing/events/

# 启用 RISC-V 特定 tracepoints
echo 1 > /sys/kernel/tracing/events/syscalls/enable
echo 1 > /sys/kernel/tracing/events/tlb/enable  # TLB 事件
echo 1 > /sys/kernel/tracing/events/irq/enable   # 中断事件
```

### 17.3 Ftrace + Kprobe 联合

利用 ftrace 替代 ebreak 可以大幅降低 kprobe 的开销（但 `KPROBES_ON_FTRACE` 在 RISC-V 上尚为 TODO）：

```text
当前实现: kprobe -> ebreak (4 字节) -> 断点异常 -> handler
                                               ~200-500ns
优化后:   kprobe -> ftrace_caller -> handler
          (在函数入口, 无异常开销)   ~50-100ns
```

---

## 18. 各调试/诊断功能的对比矩阵

### 18.1 硬件调试功能对比 (RISC-V vs ARM vs x86)

| 功能 | RISC-V | ARM64 | x86-64 | 备注 |
|:-----|:-------|:------|:-------|:------|
| 调试传输 | JTAG/cJTAG/USB/SPI/PCIe | JTAG/SWD | JTAG/DCI | RISC-V 无 SWD 等价 |
| 运行控制 | ✅ DM req | ✅ DAP | ✅ | |
| 多核同步halt | ✅ Halt Group | ✅ Cross-halt | 依赖厂商 | |
| 断点(硬件) | ✅ Sdtrig (可指定触发动作) | ✅ BRP (仅异常) | ✅ DR0-3 | RISC-V 可指定进入调试模式 |
| 观测点(硬件) | ✅ mcontrol6 (地址+数据+掩码) | ✅ WRP (地址+掩码) | ✅ DR0-3 (地址+长度) | RISC-V 支持数据值匹配 |
| 数据值观测 | ✅ tdata3 掩码 | ❌ | ❌ | RISC-V 独有能力 |
| 指令计数触发 | ✅ icount | 无直接等价 | 仅PEBS 特定 | |
| 中断/异常触发 | ✅ itrigger/etrigger | ❌ | ❌ | RISC-V 独有的调试能力 |
| 链式触发 | ✅ Chain trigger | ❌ | ❌ | RISC-V 独有 |
| 抽象命令 | ✅ Access Register/Memory | ❌ (依赖 DAP) | ❌ | 简化调试器实现 |
| SBA (系统总线访问) | ✅ 零侵入 | ✅ DAP 内存访问 | ❌ | |
| 认证/锁定 | ✅ DM 认证 | ✅ DAP 认证 | ✅ JTAG 锁定 | 所有架构基本一致 |
| 熔断 | ✅ 永久关闭 | ✅ eFuse | ✅ JTAG Disable | |
| E-Trace | ✅ (标准化) | ✅ ETM (标准化) | ✅ Intel PT | 格式不同 |
| 性能计数器 | ✅ Zihpm (非标准化事件) | ✅ PMUv3 (标准化事件) | ✅ Architectural PMU | RISC-V 事件未标准化 |
| 压缩指令断点 | ⚠️ WARL 语义 | ✅ A32/T32 | ✅ 3-byte 前缀 | RISC-V 需要处理 16/32-bit |

### 18.2 Linux 内核调试功能对比 (RISC-V vs ARM64 vs x86)

| 功能 | RISC-V | ARM64 | x86-64 | 备注 |
|:-----|:-------|:------|:-------|:------|
| perf_event | ✅ | ✅ | ✅ | |
| PMU | ✅ (SBI PMU) | ✅ (PMUv3) | ✅ | 事件标准化 RISC-V 不足 |
| hw_breakpoint | ✅ (Sdtrig) | ✅ (BRP/WRP) | ✅ (DR) | 数量由实现定 |
| KGDB | ✅ | ✅ | ✅ | |
| Kprobes | ✅ (ebreak) | ✅ | ✅ | RISC-V 无 optprobes |
| Kprobes-on-ftrace | 🔧 TODO | ✅ | ✅ | |
| Optprobes | 🔧 TODO | ✅ | ✅ | |
| Uprobes | ✅ | ✅ | ✅ | |
| KASAN | ✅ | ✅ | ✅ | |
| KCOV | ✅ | ✅ | ✅ | |
| Ptrace | ✅ | ✅ | ✅ | |
| Ftrace | ✅ | ✅ | ✅ | |
| Enlightened PEBS | ❌ | ❌ | ✅ | x86 特有 |
| SPE | ❌ | ✅ | ❌ | ARM 特有 |
| CoreSight | ❌ | ✅ | ❌ | ARM 特有 |

### 18.3 RISC-V 调试能力的独特优势

```text
★ RISC-V 调试诊断体系的差异化优势:

1. 数据值匹配观测 (mcontrol6 + tdata3)
   可以设定: "当 addr=X 且 data=0xDEAD 时触发"
   -> 精准捕获特定状态下的内存写入，减少无效触发

2. 多动作选择 (action=0/1/2)
   触发后可以不进异常（CPU 0 开销），仅做 trace 输出
   -> 适合生产环境性能采样的跟踪诊断

3. 中断/异常触发器 (itrigger/etrigger)
   直接在硬件层捕获中断和异常事件
   -> 中断嵌套、中断延迟分析的利器

4. 链式触发 (Chain Trigger)
   组合多个条件（地址+数据+计数）才触发
   -> 复杂诊断场景无需软件层处理

5. 认证阶梯
   从无认证 -> 密钥认证 -> 熔断
   -> 灵活平衡制造调试和生产安全

6. 零侵入系统总线访问 (SBA)
   hart 正常运行时可读取任意物理内存
   -> 生产环境问题诊断不中断业务
```

---

## 19. 参考规范与文档

> **来源标注**: 下文所有引用均已标注对应来源章节/文档名

| 规范/文档 | 来源 | 版本 |
|:----------|:-----|:-----|
| RISC-V Debug Specification v1.0 [DTM/DM/Sdtrig/SBA] | riscv.org/technical/specifications | 2025-02 批准 |
| RISC-V Privileged Architecture Specification v1.12 [Zihpm/Zicntr/CSR] | riscv.org | 2023 |
| RISC-V Unprivileged Architecture Specification v20191213 | riscv.org | 2019 |
| SBI Specification v2.0 [PMU/DBCN/Reset] | riscv.org | 2024 |
| RISC-V E-Trace (Nexus Trace) Specification v1.0 | riscv.org | 2024 |
| RISC-V Processor Trace Specification (Draft) | riscv.org | v0.5 |
| Linux Kernel Documentation: Feature Status on riscv | docs.kernel.org/arch/riscv | v7.2-rc1 |
| Linux Kernel Documentation: RISC-V HWProbe | docs.kernel.org/arch/riscv/hwprobe | v7.2-rc1 |
| SiFive RISC-V Debug Blog | sifive.com/blog | 2025 |
| RISC-V Debug Spec GitHub Repository | github.com/riscv/riscv-debug-spec | v1.0 |

### 知识库交叉链接

- 📄 **[服务器产品研发全链路知识图谱](../../03_management/01_product-management/2026-06-23-server.md)** — 14领域 × TR1-TR6 矩阵，芯片/硬件调试属于 05_debug 领域
- 📄 **缓存一致性分析专题** — RISC-V 缓存一致性协议与调试触发的关系
- 📄 **互联分析专题** — PCIe/CXL 互连上的调试传输层
- 📄 **PCIe 协议深度分析** — PCIe DTM 实现的物理层基础
- 📄 **[Si 信号完整性分析](../../01_product/00_hardware/04_si-signal/2026-06-25-signal-integrity-analysis.md)** — JTAG/调试链路的信号质量
- 📄 **[版本方法与兼容性方案](../../01_product/01_software/2026-06-29-versioning-and-compatibility-methodology.md)** — 调试规范的版本管理方法

---

## 20. 变更记录

| 日期 | 版本 | 变更内容 | 变更人 |
|:----|:----|:---------|:-------|
| 2026-07-02 | v1.0 | 初版撰写：RISC-V 调试体系(DTM/DM/Sdtrig/E-Trace) + Linux 内核支持(perf/hw_breakpoint/KGDB/Kprobes/KASAN/KCOV/Ptrace/Ftrace) + 跨架构对比矩阵 | 小龙猫 |

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- [服务器产品研发全链路知识图谱](../../03_management/01_product-management/2026-06-23-server.md) — 关联
- 缓存一致性分析专题 — 关联
- 互联分析专题 — 关联
- PCIe 协议深度分析 — 关联
- [Si 信号完整性分析](../../01_product/00_hardware/04_si-signal/2026-06-25-signal-integrity-analysis.md) — 关联
- [版本方法与兼容性方案](../../01_product/01_software/2026-06-29-versioning-and-compatibility-methodology.md) — 关联

### 外部资料引用

- (无)

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
