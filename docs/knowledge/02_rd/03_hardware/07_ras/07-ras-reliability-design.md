# 07 — RAS 与可靠性设计（扩充版）

> **来源**: `服务器系统RAS功能及相关规范、配套工具研究报告.docx` · `BIOS_RAS规格与实现方案（完整版）.docx` · `超节点计算节点软硬件细化设计方案.docx` · `整机柜_集群节点故障诊断规格书.docx` · `AI服务器整机架构与标准化设计白皮书.docx` · `超节点信号质量评估分析方案（含三方案对比）.docx` · Intel/AMD 官方技术文档 · Linux Kernel RAS Documentation

---

## 1 RAS 核心概念与原理

### 1.1 RAS 定义

RAS (Reliability, Availability, Serviceability) 是面向服务器和数据中心的硬件韧性设计体系：

| 维度 | 定义 | 衡量指标 |
|:-----|:-----|:---------|
| **Reliability (可靠性)** | 系统在全生命周期内稳定运行，抵御硬件故障的能力 | MTBF (Mean Time Between Failures) |
| **Availability (可用性)** | 系统在任意时刻正常运行的概率 | 正常运行时间占比 (如 99.999%) |
| **Serviceability (可服务性)** | 故障发生后快速定位和修复的便捷程度 | MTTR (Mean Time To Repair) |

### 1.2 错误分类体系

RAS 技术建立在精确的错误分类基础上：

| 错误类型 | 缩写 | 定义 | 系统影响 |
|:---------|:-----|:-----|:---------|
| **Correctable Error** | CE | 硬件检测并自动纠正的错误 | 通常透明，应用继续运行 |
| **Uncorrected Error** | UE | 超出纠错能力的错误 | 需根据位置和严重程度处理 |
| **Fatal Error** | - | 发生在关键组件的 UE | 系统 hang 或 reboot |
| **Non-fatal Error** | - | 发生在未使用组件的 UE | 可降级运行或进程终止 |

### 1.3 核心技术架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      RAS 技术架构分层                            │
├─────────────────────────────────────────────────────────────────┤
│  应用层 (Application)      │  业务容错、进程监控                  │
├─────────────────────────────────────────────────────────────────┤
│  操作系统层 (OS)           │  mcelog, edac, AER驱动, hwpoison    │
├─────────────────────────────────────────────────────────────────┤
│  固件层 (Firmware/BIOS)   │  UEFI/APEI, 错误记录, 页面隔离       │
├─────────────────────────────────────────────────────────────────┤
│  硬件层 (Hardware)         │  MCA, AER, ECC, Poison, Scrubbing   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2 CPU 层面 RAS 技术规格

### 2.1 MCA (Machine Check Architecture)

MCA 是 CPU 层面的核心 RAS 机制，通过 MSR (Model Specific Register) 记录错误详情。

#### 2.1.1 MCA 错误类型

| 错误类型 | Intel 标记 | AMD 标记 | 说明 |
|:---------|:-----------|:---------|:-----|
| 内存错误 | MCACOD | - | 内存控制器检测到的错误 |
| CPU 内部错误 | MCACOD | - | 指令执行、缓存等内部错误 |
| 外部总线错误 | - | - | 前端总线、互联总线错误 |

#### 2.1.2 MCA 处理流程

```
错误检测 → 触发 MCE → 读取 MSR → 错误分类(CE/UE) → 上报/恢复
     ↓
CE: CMCI 中断/轮询 → OS 记录日志 → 可选 Memory Scrubbing
     ↓
UE: 尝试恢复 → 成功则继续运行 / 失败则 kernel panic
```

#### 2.1.3 MCA Bank 架构 (Intel vs AMD)

| 平台 | Bank 架构 | 覆盖范围 |
|:-----|:----------|:---------|
| **Intel** | Core MCA + Uncore MCA | IFU/DCU/DTLB/MLC/PCU/UPI/M2M/CHA/IMC |
| **AMD** | 多 Bank 架构 | 命名和分组与 Intel 不同，但覆盖类似 |

### 2.2 CMCI (Corrected Machine Check Interrupt)

| 参数 | Intel 规格 | AMD 规格 |
|:-----|:-----------|:---------|
| 作用 | CE 积累到阈值时触发中断 | 与 Intel 类似 |
| 默认阈值 | MCA bank 控制, 10 个 | MCA 控制, 可配置（常见较低） |
| 优势 | 支持预测性故障分析 | - |

### 2.3 MCE Recovery (Software Error Recovery)

| 参数 | 说明 |
|:-----|:-----|
| 作用 | Software Error Recovery (SER)：允许 OS 从部分不可纠正可恢复错误 (UCR) 中恢复，而非直接 panic |
| 依赖 | 需配合 PCIe Poison 功能 |
| Intel 机制 | MCA 架构处理，OS kernel 优先尝试恢复（如进程终止/页面隔离） |
| AMD 机制 | 类似，MCA bank 架构差异导致覆盖范围不同 |

### 2.4 LMCE (Local Machine Check Exception) - Intel 特有

| 参数 | 规格 |
|:-----|:-----|
| 功能 | 将 MCE 仅路由给消费该错误的逻辑核（Local Machine Check Exception），而非广播到所有线程 |
| 问题解决 | 避免一个 poison line 被多个核消费时背靠背广播 MCE 导致系统关机 |
| 默认状态 | 使能 |

### 2.5 DCU/IFU Error Handling Enhancement - Intel 特有

| 模块 | 说明 |
|:-----|:-----|
| **DCU** (Data Cache Unit) | 指令消隐后记录错误（非指令执行时），提升错误检测覆盖范围 |
| **IFU** (Instruction Fetch Unit) | 提升 MCA Recovery 覆盖范围 |
| 能力 | 可处理 DCU/IFU 收到多个 poison 置位的 back-to-back 交易 |

### 2.6 Complex Instruction Recovery

| 参数 | 说明 |
|:-----|:-----|
| 作用 | 扩展 MCA Recovery 能力，解决复杂指令流程中检测到不可纠正错误的 recovery |

### 2.7 CPU 超时告警机制

| 平台 | 实现方式 |
|:-----|:---------|
| **Intel** | 支持 Time-out Schemes，使能 CPU 内部各 IP 及 PCIe 的 timeout 机制，有错误通过硬件管脚通知 BMC |
| **AMD** | 使能 CPU Watchdog Timer，core 挂死产生 Fatal error，记录到 MCE bank，通过硬件管脚通知 BMC 并触发热复位 |

### 2.8 IVR (Integrated Voltage Regulator) 错误上报

| 平台 | 支持情况 |
|:-----|:---------|
| **Intel** | 支持 Error Reporting For IVR，core/uncore IVR 可产生 IERR，作为 core 或 socket disable 条件 |
| **AMD** | 类似机制 |

### 2.9 Data Fabric 看门狗

| 平台 | 说明 |
|:-----|:-----|
| **AMD** | Data Fabric Watchdog Timer 使能，检测和恢复内部 data fabric 挂死情形 |
| **Intel** | 类似机制通过 UPI/PCU 实现 |

### 2.10 CPU BIST 功能

| 参数 | 说明 |
|:-----|:-----|
| 功能 | 启动阶段 CPU BIST (Built-in Self Test) |
| 后续处理 | 出错 core 隔离并被 BIOS 感知 |
| 上报 | 上报 BMC 产生对应告警 |

### 2.11 MCA MSR 寄存器详解 (Intel SDM 规范)

MCA 架构通过一系列 Model Specific Register (MSR) 实现错误检测和记录。

#### 2.11.1 全局控制寄存器

| 寄存器 | 地址 | 说明 |
|:-------|:-----|:-----|
| **IA32_MCG_CAP** | - | 只读，描述 CPU 支持的 MCA 能力 |
| BIT0-7 | - | 支持的 Bank 数量 |
| BIT8 | - | IA32_MCG_CTL 是否有效 (1=有效) |
| BIT9 | - | IA32_MCG_EXT_CTL 是否有效 (1=有效) |
| BIT10 | - | 支持 CMCI |
| BIT24 | - | 支持 Software Error Recovery |
| BIT25 | - | 支持增强版 MCA |
| **IA32_MCG_STATUS** | - | MCE 发生后 CPU 状态 |
| BIT0 (RIPV) | - | 1=可以从指令指针重启执行 |
| BIT1 (EIPV) | - | 1=当前指令与 MCE 相关 |
| BIT2 (MCIP) | - | 1=当前已触发 MCE |
| **IA32_MCG_CTL** | - | 全局 MCA 使能控制 (写1=禁用) |
| **IA32_MCG_EXT_CTL** | - | 扩展控制 |
| BIT0 (LMCE_EN) | - | 1=使能 Local MCE，仅发送给单核 |

#### 2.11.2 每 Bank 错误记录寄存器

每个 Bank (IA32_MCi_*) 包含四个寄存器：

| 寄存器 | 地址 | 功能 |
|:-------|:-----|:-----|
| **IA32_MCi_CTL** | MSR 400H+N*4 | 使能特定错误类型触发 #MC |
| **IA32_MCi_STATUS** | MSR 401H+N*4 | 错误状态 (64-bit, Write-1-to-Clear) |
| **IA32_MCi_ADDR** | MSR 402H+N*4 | 错误发生地址 (如果适用) |
| **IA32_MCi_MISC** | MSR 403H+N*4 | 错误辅助信息 (如 scrub rate) |
| **IA32_MCi_CTL2** | MSR 280H+N | CMCI 阈值配置 (BIT0-14=阈值, BIT30=使能) |

#### 2.11.3 MCA 错误状态位 (IA32_MCi_STATUS)

| 位 | 名称 | 说明 |
|:---|:-----|:-----|
| BIT0 | Val | 1=记录有效 |
| BIT1 | UC | 0=CE, 1=UE |
| BIT2 | OVER | 1=之前的错误未处理被覆盖 |
| BIT3 | UCNA | Uncorrected Error, No Action Required (不影响执行) |
| BIT4 | SRAO | System Recoverable Action Optional (可后台处理) |
| BIT5 | SRAR | System Recoverable Action Required (需要同步恢复) |
| BIT6 | PCC | 1=Processor Context Corrupt, 不可恢复 |
| BIT56-55 | McaErrorCodeExt | 扩展错误码 |
| BIT31-16 | ErrorCode | 主要错误码 |

#### 2.11.4 UCR (Uncorrected Recoverable) 错误分类

| 类型 | 说明 | 处理方式 |
|:-----|:-----|:---------|
| **UCNA** | 影响较小，通知 OS 记录即可 | 记录日志，继续运行 |
| **SRAO** | 可选恢复操作 | 隔离错误页/结构 |
| **SRAR** | 需要同步恢复 | 进程级恢复或终止 |
| **Fatal** | PCC=1 不可恢复 | 系统重启 |

### 2.12 AMD SMCA (Scalable Machine Check Architecture)

| 组件 | 说明 |
|:-----|:-----|
| **MCA Bank** | 扩展 Bank 数量，支持更多错误源 |
| **Error Status** | 64-bit 错误状态寄存器 |
| **MCA_CONFIG** | 使能/禁用特定错误类型 |
| **MCA_XHIT** | 缓存层次结构错误定位 |

---

## 3 内存层面 RAS 技术规格

### 3.1 内存错误分类

| 错误类型 | 说明 |
|:---------|:-----|
| **Single-bit Error** | 单比特翻转，ECC 可纠正 |
| **Multi-bit Error** | 多比特错误，需 Chipkill/SDDC 纠正 |
| **Ghost Errors** | 重复出现但位置不同的错误，预示即将发生真正故障 |

### 3.2 ECC (Error-Correcting Code) 规格

| 规格 | 说明 |
|:-----|:-----|
| **SEC-DED** | Single Error Correction, Double Error Detection (基本纠错) |
| **Chipkill** | 纠正单个 DRAM 芯片失效导致的多比特错误 (x4/x8 颗粒级别) |
| **SDDC** | Single Device Data Correction，Intel 术语 |
| **DEC-TED** | Double Error Correction, Triple Error Detection (L2/L3 缓存) |
| **ADDDC** | Adaptive Double Device Data Correction，运行时自适应纠错 |

### 3.3 DDR 内存 RAS 特性矩阵

| 特性 | 说明 | 默认状态 | 平台支持 |
|:-----|:-----|:--------:|:---------|
| **ECC** | 错误检测和纠正 | 开启 | Intel/AMD |
| **Chipkill/SDDC** | 单设备多比特纠错 | 开启 | Intel/AMD |
| **ADDDC-MR** | 在不同 bank/rank 间做 2 次失效 region 替换 +1 sparing | 关闭 | Intel (x4 DIMM) |
| **ADDDC-SR** | 单 rank 内 1 次失效 region 替换 +1 sparing | 关闭 | Intel |
| **ADC (Sparing)** | 单通道内 1 次 bank 级别 spare copy | 关闭 | AMD |
| **Memory Mirroring** | 通道级镜像，互为热备 | 关闭 | Intel/AMD |
| **Hot Spare** | 预留内存行/颗粒作为热备 | 关闭 | Intel/AMD |
| **PPR (Post Package Repair)** | 失效行修复 | 关闭 (可选) | Intel/AMD |
| **H-PPR** | 硬 PPR，永久修复 | 菜单可选 | Intel/AMD |
| **S-PPR** | 软 PPR，可逆修复 | 菜单可选 | Intel/AMD |
| **C/A Parity + Retry** | 命令/地址奇偶校验重试 | 开启 | Intel/AMD |
| **Read/Write CRC + Retry** | 读写 CRC 校验重试 | 关闭 | Intel/AMD |
| **Data Scrambling** | 数据随机化，减少 EMI 和错误率 | 开启 | Intel/AMD |

### 3.4 ADDDC 详细规格 (Intel)

| 参数 | Intel 规格 |
|:-----|:-----------|
| 全称 | Adaptive Double Device Data Correction |
| 支持配置 | ADDDC-SR (单 rank), ADDDC-MR (多 rank) |
| 约束 | 仅 x4 DIMM 支持 |
| 能力 | 最多在一个内存通道内做 2 次失效 region 替换 + 1 次 +1 sparing |
| 依赖 | 内存自适应 lockstep 机制 |
| 增强模式 | 可设置触发条件，达标后自动开启 Enhanced ADDDC |

### 3.5 PPR (Post Package Repair) 规格

| 参数 | 说明 |
|:-----|:-----|
| **H-PPR** | 硬 PPR，失效行永久替换为备用行 |
| **S-PPR** | 软 PPR，可逆，触发后可能恢复 |
| **Runtime PPR** | 运行时触发，上报 BMC 产生告警 |
| **OOB PPR** | 带外 PPR，通过 BMC 远程执行（详见 §5.9） |
| 控制方式 | Setup Menu，默认为关闭 |

### 3.6 Memory Scrubbing 技术

| 类型 | 说明 | 周期 | 默认状态 |
|:-----|:-----|:-----|:--------:|
| **Patrol Scrubbing** | 后台巡检，发现 UCE 错误上报 BMC 并降级通知 OS | 24 小时 | 使能 |
| **Demand Scrubbing** | 访问时发现错误并纠正 | 即时 | 使能 |
| **DCU Scrubbing** | DCU 内部错误清理，减少 fatal 错误概率 | 后台 | 使能 |

#### 3.6.1 Patrol Scrubbing 详细机制

Patrol Scrubbing 是后台运行的内存巡检机制，每 24 小时遍历一次 DRAM 全部地址：

| 参数 | 规格 |
|:-----|:-----|
| 周期 | 24 小时完成一次全量扫描 |
| 扫描粒度 | 逐行/逐 bank 巡检 |
| 错误处理 | 发现 UCE → 上报 BMC SEL → 通知 OS |
| BIOS 配置 | 可调整巡检速率 |
| OS 影响 | 低，后台运行 |

#### 3.6.2 Demand Scrubbing 机制

| 参数 | 说明 |
|:-----|:-----|
| 触发条件 | CPU 访问内存时检测到错误 |
| 处理流程 | ECC 纠正 → 写回正确数据 → 继续执行 |
| 延迟影响 | 首次访问有额外延迟 |
| 与 Patrol 关系 | 互补，Patrol 负责空闲时间巡检 |

#### 3.6.3 ECS (Error Check and Scrub) - Cisco 术语

| 特性 | 说明 |
|:-----|:-----|
| 功能 | 后台 DRAM 巡检，每 24 小时周期纠正错误 |
| 默认状态 | 使能 |
| 报告 | 提供巡检期间发现的错误计数 |
| BIOS 配置 | 可通过 BIOS 菜单调整 |

#### 3.6.4 DDR5 On-Die ECC

| 特性 | 说明 |
|:-----|:-----|
| 位置 | DRAM 芯片内部 |
| 保护范围 | 芯片内部 bank 级别 |
| 纠错能力 | 单比特错误纠正 |
| 与系统 ECC | 互补，系统 ECC 保护 rank/channel 级别 |

#### 3.6.5 Memory Scrubbing 配置接口

Linux sysfs scrub 控制接口：

```bash
# 查看 scrub 能力
cat /sys/devices/system/edac/mc/mc0/sdram_scrub_rate_max

# 设置 scrub 速率 (MB/s)
echo 65536 > /sys/devices/system/edac/mc/mc0/sdram_scrub_rate

# CXL 设备 patrol scrub 控制
cat /sys/bus/cxl/devices/.../scrub_rate_seconds
echo 86400 > /sys/bus/cxl/devices/.../scrub_rate_seconds
```

---

## 4 PCIe AER/DPC/EDPC 详细规格

### 4.1 AER 扩展能力结构

AER (Advanced Error Reporting) 是 PCIe 设备错误报告的扩展机制：

| 寄存器 | 偏移 | 说明 |
|:-------|:-----|:-----|
| **Capability Header** | 00h | 扩展能力 ID (0x0001), 版本 |
| **Uncorrectable Error Status** | 04h | 不可纠正错误状态 |
| **Uncorrectable Error Mask** | 08h | 不可纠正错误屏蔽 |
| **Uncorrectable Error Severity** | 0Ch | 错误严重性 (Fatal/Non-Fatal) |
| **Correctable Error Status** | 10h | 可纠正错误状态 |
| **Correctable Error Mask** | 14h | 可纠正错误屏蔽 |
| **Advanced Error Capabilities** | 18h | 能力配置 |
| **Header Log** | 1Ch | TLP 头日志 (4 DWORD) |
| **Root Error Command** | 28h | Root Port 命令 |
| **Root Error Status** | 2Ch | Root Error 状态 |
| **Root Error Query** | 30h | 错误查询 |
| **TLP Prefix Log** | 34h | TLP 前缀日志 |

### 4.2 AER 错误分类

#### 4.2.1 Correctable Errors (CE)

| 错误类型 | 说明 | 影响 |
|:---------|:-----|:-----|
| **RCVR_ERR** | Receiver Error | 链路重新训练 |
| **Bad TLP** | TLP 格式错误 | 重传 |
| **Bad DLLP** | DLLP 校验错误 | 重传 |
| **RELAY_NUM Rollover** | 中继计数溢出 | 链路重训练 |
| **Replay Timeout** | 重传超时 | 链路重新训练 |
| **Advisory Non-Fatal** | 建议性非致命错误 | 记录，不中断 |

#### 4.2.2 Uncorrectable Errors (Non-Fatal)

| 错误类型 | 说明 |
|:---------|:-----|
| **Undefined** | 协议未定义错误 |
| **Data Link Protocol Error** | 数据链路层协议错误 |
| **Surprise Down** | 链路意外断开 |
| **Poisoned TLP** | 数据毒药 TLP |
| **Flow Control Protocol Error** | 流控协议错误 |
| **Completion Timeout** | 完成超时 |
| **Completer Abort** | 完成器中止 |
| **Unexpected Completion** | 意外完成 |
| **Receiver Overflow** | 接收器溢出 |
| **Malformed TLP** | 畸形 TLP |
| **ECRC Error** | ECRC 校验失败 |
| **Unsupported Request** | 不支持的请求 |

#### 4.2.3 Uncorrectable Errors (Fatal)

| 错误类型 | 说明 |
|:---------|:-----|
| **Flow Control Timeout** | 流控超时 |
| **Poisoned TLP (Fatal)** | 数据毒药 (致命) |
| **Surprise Down** | 链路意外断开 |
| **Internal Error** | PCIe 设备内部错误 |
| **Malformed TLP (Fatal)** | 畸形 TLP (致命) |

### 4.3 DPC (Downstream Port Containment)

DPC 是 PCIe Root Port 的错误隔离机制：

| 特性 | 说明 |
|:-----|:-----|
| **触发条件** | 检测到 unmasked uncorrectable error |
| **动作** | 停止下游端口流量，防止错误扩散 |
| **恢复** | 软件执行 Containment Error Recovery (CER) |
| **热插拔** | 支持异步移除和 DPC 并发 |

#### 4.3.1 DPC 触发原因

| 原因码 | 说明 |
|:-------|:-----|
| 0x0000 | 软件触发 |
| 0x0001 | unmasked Uncorrectable Error (UCE) |
| 0x0002 | ERR_FATAL |
| 0x0003 | ERR_NONFATAL |
| 0x0004 | RP PIO (Programmed I/O) |

### 4.4 EDPC (Enhanced DPC)

EDPC 是 Intel 对 DPC 的增强，增加了 Root Port Programmed I/O 错误：

| 特性 | 说明 |
|:-----|:-----|
| **扩展** | 增加 RP PIO 错误源 |
| **硬件支持** | Intel 平台特定 |
| **软件要求** | UEFI firmware 配置错误源寄存器 |

### 4.5 AER 恢复流程 (Linux)

```
错误检测 → AER 中断 → 内核处理 → 错误分类 → 恢复策略
                                        ↓
    ┌─────────────────┬─────────────────┬────────────────┐
    ↓                 ↓                 ↓                ↓
  恢复成功         降级运行         设备复位        系统重启
```

### 4.6 AER 配置命令

```bash
# 查看 AER 状态
lspci -vv -s 00:02.0 | grep -i aer

# 启用 AER (需要内核支持)
echo 1 > /sys/bus/pci/devices/0000:00:02.0/aerdrv_enable

# 查看 AER 统计
cat /sys/bus/pci/devices/0000:00:02.0/aer_stats/

# 设置错误阈值
echo 100 > /sys/bus/pci/devices/0000:00:02.0/aer_rootport_thresh

# 触发 EDR 检测 (需要 dmesg)
pciehp pcieport 0000:00:1c.0:pciehp: Slot(01):Link Down
```

---

## 5 BMC 带外管理与硬件监控

### 5.1 BMC 架构概述

BMC (Baseboard Management Controller) 是服务器主板上独立的嵌入式系统，负责硬件监控和管理：

| 组件 | 说明 |
|:-----|:-----|
| **处理器** | 低功耗嵌入式 CPU (500-1000MHz) |
| **内存** | Flash 固件 + NVRAM 日志存储 |
| **网络** | 独立管理网口 (Dedicated/Shared LOM) |
| **接口** | IPMB/I2C 内部总线，IPMI 2.0 对外接口 |
| **固件** | 独立于主机 CPU/OS/BIOS 运行 |

### 5.2 IPMI 架构

IPMI (Intelligent Platform Management Interface) 是 BMC 与主机通信的标准接口：

| 组件 | 说明 |
|:-----|:-----|
| **IPMB** | Intelligent Platform Management Bus，内部 I2C/SMBus |
| **ICMB** | Intelligent Chassis Management Bus (legacy) |
| **SEL** | System Event Log，非易失事件存储 |
| **SDR** | Sensor Data Record，传感器信息库 |
| **FRU** | Field Replaceable Unit，产品信息 |

### 5.3 BMC 核心 RAS 功能

| 功能 | 说明 | 触发条件 |
|:-----|:-----|:---------|
| **传感器监控** | 温度/电压/风扇/电源 24/7 监控 | 阈值超限 |
| **SEL 记录** | 硬件事件持久化存储 | 任何硬件事件 |
| **告警 (Alert)** | 远程告警通知 (SNMP Trap/IPMI Alert) | Critical 事件 |
| **电源管理** | 远程开/关/重启 | 管理员请求 |
| **SOL** | Serial-over-LAN，控制台重定向 | 故障诊断 |
| **故障隔离** | LED 指示/自动禁用故障组件 | 严重故障 |

### 5.4 IPMI/BMC 内存错误检测

#### 5.4.1 内存错误上报路径

```
BIOS/UEFI 检测内存错误 → IPMI SEL 记录 → BMC 存储 → 远程告警
        ↓
    ECC/Chipkill 纠正 → CMCI 中断 → OS mcelog → 管理员告警
```

#### 5.4.2 IPMI SEL 内存事件格式

| 字段 | 说明 |
|:-----|:-----|
| **Record ID** | 日志记录编号 |
| **Timestamp** | 事件发生时间 |
| **Severity** | CRT(严重)/MIN(最小)/MAJ(主要) |
| **Source** | BMC/CPU/SEL 事件源 |
| **Sensor#** | 传感器编号 |
| **Event Detail** | 事件具体描述 |
| **Trigger** | 触发条件 |
| **Event Data** | 原始事件数据 |

#### 5.4.3 常见内存错误 SEL 事件

| SEL 事件 | 含义 | 推荐操作 |
|:---------|:-----|:---------|
| MEM0001 | 不可纠正 ECC 错误 | 更换 DIMM |
| MEM9072 | DIMM 故障隔离 | 检查并更换故障 DIMM |
| MEM8000 | 可纠正 ECC 错误 | 监控，必要时更换 |
| DIMM Presence | DIMM 插拔检测 | 物理检查 |

#### 5.4.4 IPMI 内存诊断命令

```bash
# 查看 SEL 日志
ipmitool sel list
ipmitool sel list | grep -i memory

# 查看传感器状态
ipmitool sensor list | grep -i memory
ipmitool sensor get "Correctable ECC"

# 查看详细传感器信息
ipmitool sensor get "P1_DIMM_A1"

# 清除 SEL
ipmitool sel clear

# 查看 FRU 信息
ipmitool fru list
```

### 5.5 Redfish API

Redfish 是新一代服务器管理 API，基于 RESTful 和 JSON：

| 特性 | 说明 |
|:-----|:-----|
| **标准化** | DMTF 标准，跨厂商兼容 |
| **易用性** | JSON 格式，人类可读 |
| **功能** | 传感器数据、电源控制、固件更新、事件订阅 |
| **安全** | 支持 OAuth 2.0、TLS |

```bash
# Redfish 查询示例
curl -k -u admin:password https://bmc/redfish/v1/Systems/1/LogServices/SEL/Entries
```

### 5.6 BMC 固件双镜像机制

| 特性 | 说明 |
|:-----|:-----|
| **双镜像** | 主镜像 + 备用镜像 |
| **自动恢复** | 主镜像损坏时自动切换到备用镜像 |
| **远程更新** | 支持带外固件更新 |
| **回滚** | 支持固件版本回滚 |

### 5.7 常见 BMC 产品

| 厂商 | 产品 | 特色 |
|:-----|:-----|:-----|
| **Dell** | iDRAC (Integrated Dell Remote Access Controller) | lifecycle controller, virtual console |
| **HPE** | iLO (Integrated Lights-Out) | Gen 10/11, RESTful API |
| **Lenovo** | XClarity Controller (XCC) | 统一管理接口 |
| **Supermicro** | BMC | IPMI 2.0, Redfish |
| **Cisco** | CIMC (Cisco Integrated Management Controller) | UCS 系列 |

### 5.8 RAS Offload

| 参数 | 说明 |
|:-----|:-----|
| 功能 | 硬件错误不触发中断，减少 CPU 中断负载 |
| 实现 | 内存 CE/PCIe CE 等由 BMC 轮询采集 |
| 优势 | 降低系统中断风暴风险 |

### 5.9 OOB PPR (Out-of-Band Post Package Repair)

| 参数 | 说明 |
|:-----|:-----|
| 功能 | 通过带外通道远程执行内存 PPR 修复 |
| 实现 | IPMI/Redfish 命令 → BMC → BIOS 协作 |
| 用途 | 无需进入 OS 即可修复失效行 |

### 5.10 OOB CE 阈值设置

| 参数 | 说明 |
|:-----|:-----|
| 接口 | Redfish/IPMI |
| 功能 | 通过 BMC 远程设置 CPU/内存/PCIe 的 CE 阈值 |

### 5.11 MCA 错误屏蔽 (Error Masking)

| 参数 | 说明 |
|:-----|:-----|
| 功能 | 通过 IA32_MCi_CTL / SMCA CTL 寄存器选择性屏蔽特定 MCA bank 的错误上报 |
| 实现 | BIOS Setup 选项 / BMC 协同配置 |
| 用途 | 调试阶段定位错误源；正式运行时通常全开 |
| 注意 | 屏蔽错误上报不等于错误消失，仅影响日志与中断 |

### 5.12 远程诊断

| 平台 | 方案 | 能力 |
|:-----|:-----|:-----|
| **Intel** | At Scale Debug | 远程寄存器访问/JTAG |
| **AMD** | iHDT | 远程寄存器访问/调试 |

---

## 6 CrashDump 与诊断规格

### 6.1 CrashDump 功能对比

| 特性 | Intel | AMD |
|:-----|:------|:----|
| 触发方式 | BMC 感知系统挂死 | BMC 感知系统挂死 |
| 自动收集 | Auto Crash Dump (ACD) | AMD Crash Dump |
| 手动触发 | 支持 | 支持 |
| 收集内容 | 寄存器信息、内存快照 | 寄存器信息、内存快照 |

### 6.2 UCE Retry

| 参数 | 说明 |
|:-----|:-----|
| 功能 | Uncorrected ECC Retry |
| 机制 | 读请求发现 UCE 时发起 retry |

### 6.3 Data Poison

| 平台 | 机制 |
|:-----|:-----|
| **Intel** | Product 发现 UCE 记录为 UCNA，打上 poison 标记，最终 consumer 发现并触发 MCE |
| **AMD** | Product 发现 UCE 记录为 Deferred Error (DE)，打上 poison 标记，consumer 接收并触发 MCE |

---

## 7 错误阈值汇总表

### 7.1 CE 阈值汇总

| 错误类型 | Intel | AMD | 触发条件 |
|:---------|:-----:|:---:|:---------|
| 内存 CE | 30 个/rank per 24h | 可配置 (BIOS/SMCA) | 通知 BMC |
| PCIe CE | 1000 个 per 24h 或 6000 全局 | 可配置 (OS AER 驱动) | 通知 BMC |
| CPU CE | MCA bank, 默认 10 个 | MCA, 可配置 | 触发中断 |

> 注：AMD 平台 CE 阈值由 BIOS/SMCA 与 OS 共同配置，无统一固定默认值；上表 Intel 值来自 BIOS RAS 规范源文档。

### 7.2 漏斗配置

| 类型 | 默认值 | 控制方式 |
|:-----|:-------|:---------|
| 内存漏斗 | 1 个/秒 | 隐藏菜单 |
| PCIe CE 漏斗 | 关闭 | 菜单控制 |

---

## 8 启动/运行时 RAS 特性汇总

### 8.1 启动阶段 RAS

| 功能 | 说明 | 平台 |
|:-----|:-----|:-----|
| CPU BIST | 启动自检，出错 core 隔离 | Intel/AMD |
| Early Video | 内存未初始化即点亮显示器 | Intel/AMD |
| QuickBoot | 启动时间优化 | Intel/AMD |
| Load Default | 菜单热键/BMC GPIO/RTC 电池掉电恢复 | Intel/AMD |
| CPU Timeout | 超时通知 BMC | Intel/AMD |
| DCU Scrubbing | 减少 DCU 奇偶错误引发的 fatal 错误 | Intel |

### 8.2 运行时 RAS

| 功能 | 说明 | 平台 |
|:-----|:-----|:-----|
| Runtime PPR | 触发后上报 BMC 告警 | Intel/AMD |
| Memory Scrubbing | 后台定期巡检 | Intel/AMD |
| RAS Offload | 带外轮询监控 | Intel/AMD |
| CE Storm Control | 风暴抑制 | Intel/AMD |

---

## 9 温度/环境监控与保护

### 9.1 温度监控三级保护

| 级别 | 温度阈值 | 动作 |
|:----:|:--------:|:-----|
| 告警 | 85°C | 声光 + 远程告警 |
| 降频 | 95°C | 自动降频控温 |
| 紧急断电 | 105°C | 切断整机供电 |

> 注：上表为典型参考值，实际阈值依各 CPU 型号 Tcase/Tjmax 规格与 BIOS 策略而定。

### 9.2 漏液检测三级防护

| 级别 | 检测方式 | 动作 |
|:----:|:---------|:-----|
| 告警 | 感应绳微量渗液 | BMC 告警，记录日志 |
| 降频 | 压力/气泡异常 | 告警 → 自动降频 |
| 紧急 | 漏液确认 | 告警 → 降频 → 紧急停机 → 关闭循环泵 → 切换应急风冷 |

### 9.3 供电保护

| 保护类型 | 触发条件 | 响应时间 | 动作 |
|:---------|:---------|:--------:|:-----|
| SCP 短路保护 (高压侧) | 高压侧短路 | 微秒级灭弧 | 切断供电 |
| SCP 短路保护 (低压侧) | 低压侧短路 | 1μs 关断 | 快速关断 |
| 闪断防护 | 电网短时跌落 | Hold-up ≥20ms | 维持供电 |
| 功率封顶 | 超阈值 | 实时 | 逐级降频 |
| 过压/欠压 | 超 720-880V | 分级 | 告警 → 降频 → 关机 |

---

## 10 可靠性设计红线和验证标准

### 10.1 设计红线

| 序号 | 要求 | 后果 |
|:----:|:-----|:-----|
| 1 | 无 SI 仿真报告 → 112G/224G 高速链路禁止投板 | 高速信号完整性无法保证 |
| 2 | 无热仿真/流体仿真 → 风冷/液冷系统禁止冻结设计 | 散热风险无法评估 |
| 3 | 功耗/电源量化计算未完成 → 禁止选型定案 | 供电能力不足 |
| 4 | 冗余保护覆盖率 <100% → 禁止量产 | 单点故障风险 |
| 5 | 高低温/振动/压力未通过 → 禁止量产 | 可靠性验证不充分 |
| 6 | 国产化替代 → 必须满足电气/散热/高速性能同等指标 | 替代方案存在差距 |

### 10.2 验证准入标准

| 验证项 | 方法 | 标准 |
|:-------|:-----|:-----|
| 热仿真 + 实测 | Ansys Icepak / 6SigmaET | 芯片结温在规格内，散热余量 ≥5°C |
| 供电负载仿真 | PSIM / TI WEBENCH | 冗余测试全覆盖 |
| 流体仿真 | Fluent / 实测 | 无散热死角、无漏液风险 |
| EMC 仿真 + 实测 | CST Studio / 暗室测试 | Class B 标准 |
| 振动测试 | IEC 60068-2-6 | 无器件松动、无功能异常 |
| NCCL 集群测试 | NCCL Bench | 带宽/延迟/一致性达标 |
| 长期稳定性 | 满负载 72h+ | 无故障、无性能衰减 |

---

## 11 芯片级 RAS 实现原理

### 11.1 错误检测机制

| 机制 | 层级 | 说明 |
|:-----|:-----|:-----|
| **ECC** | 芯片/封装 | 错误纠正码，检测和纠正比特错误 |
| **Parity** | 逻辑门/寄存器 | 简单奇偶校验 |
| **CRC** | 链路/事务 | 循环冗余校验 |
| **LRC** | 内存通道 | 纵向冗余校验 |
| **C/A Parity** | 内存命令/地址 | DDR5 命令地址奇偶校验，配合 Retry 重试 |

### 11.2 错误纠正技术

| 技术 | 能力 | 应用场景 |
|:-----|:-----|:---------|
| **SEC-DED** | 单比特纠正，双比特检测 | 基本内存保护 |
| **DEC-TED** | 双比特纠正，三比特检测 | L2/L3 缓存 |
| **Chipkill** | 单设备全失效纠正 | x4/x8 DIMM |
| **ADDDC** | 双设备自适应纠正 | 高级内存保护 |

### 11.3 故障隔离机制

| 机制 | 说明 | 平台 |
|:-----|:-----|:-----|
| **Error Containment** | 错误隔离到单个应用 | NVIDIA GPU |
| **Viral** | CXL 协议层错误隔离 | CXL 3.1 |
| **DPC** | PCIe 下游端口 Containment | PCIe |
| **MCA Recovery** | CPU 核心错误恢复 | Intel/AMD |
| **LMCE** | 局部错误隔离 | Intel |

### 11.4 硬件自我修复

| 技术 | 说明 | 触发条件 |
|:-----|:-----|:---------|
| **PPR** | Post Package Repair，行级修复 | 内存初始化/运行时 |
| **Row Remapping** | 行重映射，替换 degraded 行 | 累计错误 |
| **Channel Repair** | 通道替换 | 通道故障 |
| **Core Disable** | 故障 core 禁用 | 启动自检/运行时 |
| **Sparing** | 热备 rank/row 替换 | 错误累积 |

### 11.5 错误上报架构

```
硬件错误检测 → MSR/AER 寄存器 → 中断/SMI → 固件/BMC
                                    ↓
                              错误记录 (CPER/BERT)
                                    ↓
                              操作系统日志 (mcelog)
                                    ↓
                              监控告警系统
```

---

## 12 Intel Xeon 6 / Granite Rapids RAS 特性

### 12.1 平台 RAS 特性矩阵

| 特性 | Xeon 6 P-core (Granite Rapids) | Xeon 6 E-core (Sierra Forest) | 说明 |
|:-----|:------------------------------:|:-----------------------------:|:-----|
| **DDR5** | 12 通道 (6900P) / 8 通道 (6700P) | 8 通道 | 最高 6400MT/s RDIMM |
| **MRDIMM** | 最高 8800MT/s (6900P) | - | 多 rank DIMM (MCRDIMM) |
| **SDDC** | ✓ | ✓ | 单设备数据纠正 |
| **ADDDC** | ✓ (x4 DIMM) | - | 自适应双设备纠正 |
| **PPR** | ✓ | ✓ | Post Package Repair |
| **MCA** | ✓ | ✓ | Machine Check Architecture |
| **CMCI** | ✓ | ✓ | Corrected Machine Check Interrupt |
| **In-Field Scan** | ✓ | ✓ | 运行时硬件自检 |
| **APEI** | ✓ | ✓ | ACPI Platform Error Interface |

### 12.2 Granite Rapids-AP (6900P) RAS

| 参数 | 规格 |
|:-----|:-----|
| 内存通道 | 12 通道 |
| 内存类型 | DDR5 RDIMM/MRDIMM/3DS RDIMM |
| 每通道 DPC | 1DPC |
| 最大内存带宽 | 最高 8800MT/s (MRDIMM) |
| RAS 特性 | 完整 ECC/Chipkill/ADDDC/PPR 支持 |
| PCIe | Gen 5 (64 通道) |
| CXL | CXL 2.0 (64 通道) |

### 12.3 Sierra Forest-SP (6700E) RAS

| 参数 | 规格 |
|:-----|:-----|
| 内存通道 | 8 通道 |
| 内存类型 | DDR5 RDIMM |
| 每通道 DPC | 2DPC |
| 最大内存容量 | 更高密度配置 |
| RAS 特性 | ECC/PPR/基本 RAS |
| 优势 | 高密度/低功耗 |

---

## 13 AMD EPYC 9005 系列 RAS 特性

### 13.1 平台 RAS 特性

| 特性 | AMD EPYC 9005 | 说明 |
|:-----|:--------------:|:-----|
| **架构** | Zen 5 | 最新一代 |
| **制程** | 4nm (CCD) / 6nm (IOD) | 计算芯片 4nm，I/O 芯片 6nm |
| **最大核心** | 192 核 (Zen 5c, EPYC 9965) / 128 核 (Zen 5) | - |
| **内存通道** | 12 通道 DDR5 | - |
| **PCIe** | Gen 5 | - |
| **CXL** | CXL 2.0 | - |
| **ECC** | ✓ | 完整内存保护 |
| **Chipkill** | ✓ | 单设备失效保护 |
| **ADDDC** | ✓ | 自适应双设备纠正 |
| **PPR** | ✓ | Post Package Repair |
| **Sparing** | ✓ | Hot spare |

### 13.2 AMD 内存 RAS 技术

| 技术 | 说明 | 平台支持 |
|:-----|:-----|:---------|
| **ADDDC** | 自适应双设备数据纠正 | EPYC 9005 |
| **ADC** | 设备 spare，bank 级别 spare copy | AMD |
| **Memory Mirroring** | 通道级镜像 | AMD |
| **Lockstep** | 内存锁步模式 | AMD |
| **SDDC** | 单设备数据纠正 | AMD |
| **DEC-TED** | 双比特纠正/三比特检测 | L2/L3 |

### 13.3 AMD 缓存 RAS

| 层级 | 保护机制 |
|:-----|:---------|
| **L1 Data Cache** | ECC |
| **L1 Instruction Cache** | Parity |
| **L2 Cache** | DEC-TED (双比特纠正/三比特检测) |
| **L3 Cache** | DEC-TED |
| **Infinity Fabric** | ECC |

---

## 14 GPU/NPU 芯片 RAS 技术规格

### 14.1 NVIDIA GPU RAS 特性 (Ampere/Hopper/Blackwell)

#### 14.1.1 HBM 内存错误管理

| 特性 | GA100 | GA10x | AD10x | GH100 | GB100 |
|:-----|:-----:|:-----:|:------:|:-----:|:-----:|
| Error Containment | ✓ | - | - | ✓ | ✓ |
| Row Remapping | ✓ | ✓ | ✓ | ✓ | ✓ |
| Dynamic Page Offlining | ✓ | - | - | ✓ | ✓ |
| RAS Repair (GPU Memory) | - | - | - | - | ✓* |

*注: GB100 GPU Memory Repair (RAS Repair) 支持在发生 uncorrectable ECC error 后尝试修复，但并非所有 Blackwell GPU 均保证支持

#### 14.1.2 Error Containment (错误隔离)

| 参数 | 规格 |
|:-----|:-----|
| 架构 | NVIDIA Ampere 引入 (GA100/GH100/GB100 支持) |
| 作用 | 将 uncorrectable ECC 错误影响限制在发生错误的应用程序 |
| 优势 | 其他 workloads 继续运行不受影响，无需 GPU reset |
| 覆盖 | 大多数 uncorrectable errors 可被 contain，罕见情况可能影响所有 workloads |

#### 14.1.3 Dynamic Page Offlining (动态页面离线)

| 参数 | 规格 |
|:-----|:-----|
| 架构 | NVIDIA Ampere 引入 (GA100/GH100/GB100 支持) |
| 功能 | 识别 uncorrectable ECC 错误位置，标记页面为不可用 |
| 效果 | 新旧 workloads 均不会分配该错误页面 |
| 恢复 | 不需要 GPU reset 来从大多数 uncorrectable ECC 错误恢复 |

#### 14.1.4 Row Remapping (行重映射)

| 参数 | 规格 |
|:-----|:-----|
| 架构 | Ampere GA100 及以后 (GA100/GA10x/AD10x/GH100/GB100) |
| 功能 | 用备用行替换 degraded 内存位置，硬件级修复 |
| 能力 | frame buffer 支持最高 512 次 remapping (vs 传统 page retirement 最大 64 次) |
| vs Page Retirement | row-remapping 硬件级修复，不留软件可见空洞；page retirement 软件级，会留下地址空洞 |
| 持久性 | GPU reset 后生效，GPU 生命周期内保持 |
| 限制 | 需要 GPU reset 才能生效；spare 行耗尽后无法继续修复 |

#### 14.1.5 RAS Repair (GPU Memory Repair)

| 参数 | 规格 |
|:-----|:-----|
| 架构 | Blackwell (GB100)，并非所有 Blackwell GPU 均保证支持 |
| 功能 | 用 spare HBM channel 替换失效 channel (HBM Channel Repair) |
| 触发条件 | 同一 bank 发生两次 row remapping 后再次出现 uncorrectable ECC error |
| 效果 | 如果 spare 可用，标记该 channel 为替换 |
| 日志 | XID 160 表示成功标记修复 |
| 要求 | 需要 reboot 才能生效 |

#### 14.1.6 ECC 错误分类

| 类型 | 说明 | 影响 |
|:-----|:-----|:-----|
| **Volatile ECC** | GPU 重启后计数清零 | 易失性错误 |
| **Aggregate ECC** | GPU 生命周期累积，手动重置 | 聚合性错误 |
| **SRAM Correctable** | 芯片内部 SRAM 单比特错误 | 可纠正 |
| **SRAM Uncorrectable** | 芯片内部 SRAM 多比特错误 | 需处理 |
| **DRAM Correctable** | HBM 显存单比特错误 | 可纠正 |
| **DRAM Uncorrectable** | HBM 显存多比特错误 | 不可纠正，需隔离 |

#### 14.1.7 NVIDIA GPU ECC 查询命令

```bash
# 查询 ECC 状态
nvidia-smi -q -d ECC

# 查询指定 GPU ECC 详情
nvidia-smi -i <gpu_id> -q -d ecc

# 查询易失性 ECC 计数
nvidia-smi --query-gpu=ecc.errors.corrected.volatile.device.memory --format=csv

# 查询聚合 ECC 计数
nvidia-smi --query-gpu=ecc.errors.corrected.aggregate.device.memory --format=csv

# 重置 ECC 计数
nvidia-smi --reset-ecc-errors -i <gpu_id>
```

### 14.2 GPU HBM 错误恢复流程

```
错误检测 → ECC 纠正 (SBEs) → 不可纠正错误 → Error Containment 隔离
     ↓
Dynamic Page Offlining → 标记错误页面 → 恢复运行
     ↓ (如果不可恢复)
Row Remapping → 替换 degraded 行 → 需要 GPU reset
     ↓ (如果仍然失败)
RAS Repair (仅 GB100) → 替换 HBM channel → 需要 reboot
     ↓
RMA (如果硬件损坏)
```

### 14.3 DCGM GPU 监控与 RAS

| 功能 | 说明 |
|:-----|:-----|
| **DCGM (Data Center GPU Manager)** | NVIDIA 官方 GPU 监控工具 |
| 健康监控 | 定期轮询 ECC 计数、性能指标、温度 |
| 告警配置 | ECC 错误率超过阈值时触发告警 |
| 遥测数据 | 导出到 Prometheus/InfluxDB/Grafana |
| 远程管理 | 支持远程 GPU 故障诊断和复位 |

### 14.4 AMD GPU RAS 特性

| 特性 | 说明 | 平台 |
|:-----|:-----|:-----|
| **ECC** | HBM 显存错误检测和纠正 | AMD Instinct |
| **DRAM ECC** | 片上 DRAM ECC 保护 | AMD EPYC |
| **Chipkill** | 单设备失效纠正 | AMD EPYC |
| **ADDDC** | 自适应双设备数据纠正 | AMD |
| **PPR** | Post Package Repair | AMD |

### 14.5 AI 训练集群可靠性优化

#### 14.5.1 万卡集群可靠性设计

| 技术 | 说明 | 效果 |
|:-----|:-----|:-----|
| **SPARe** | Stacked Parallelism + Adaptive Reordering，冗余数据 shard 跨并行组堆叠 | 600k GPU 可扩展，time-to-train 降低 40-50% |
| **DisagMoE** | 解耦 MoE 训练，Attention 和 FFN 独立 GPU 组 | 1.8× speedup on 16-node |
| **ReCoVer** | 梯度等价容错，恒等 microbatch 数量不变式 | 256 GPU 丧失后仍保持轨迹 |

#### 14.5.2 故障检测与恢复时间

| 场景 | 恢复技术 | 恢复时间 |
|:-----|:---------|:---------|
| GPU 静默错误 | ECC + Dynamic Page Offlining | <1s (无需 reset) |
| GPU 硬件故障 | GPU 隔离 + 任务重启 | 分钟级 |
| Straggler | 在线负载均衡 (UltraEP) | 秒级 |
| Checkpoint 恢复 | DynaTrain VPS | <2s (70B) |
| 网络故障 | 集合通信容错 | 秒级 |

### 14.6 Intel Gaudi/Max GPU RAS

| 特性 | 说明 |
|:-----|:-----|
| **HBM ECC** | 高带宽内存错误检测和纠正 |
| **芯片级错误处理** | MCA 类错误处理机制 |
| **RAS Offload** | 减少 CPU 中断负载 |
| **故障隔离** | 防止故障扩散 |

---

## 15 AI 大规模训练可靠性

### 15.1 大规模训练故障分类

| 故障类型 | 说明 | 影响 |
|:---------|:-----|:-----|
| **Straggler** | 慢节点，拖慢整体进度 | 集群效率下降 |
| **Silent Data Corruption** | 静默数据错误 | 计算结果错误 |
| **Hardware Failure** | GPU/网络/存储故障 | 任务中断 |
| **Transient Fault** | 瞬态故障 | 可恢复 |
| **Memory HW Errors** | HBM/显存错误 | 计算中断或错误 |
| **Interconnect Errors** | NVLink/PCIe 链路错误 | 通信失败 |

### 15.2 检查点 (Checkpoint) 技术

| 方案 | 特点 | 适用场景 |
|:-----|:-----|:---------|
| **TierCheck** | 存储分层 | 大规模训练 |
| **LLMTailor** | 内容裁剪 | LLM 训练 |
| **MoEvement** | 专家子集 | MoE 模型 |
| **BatchWeave** | 数据管线一致恢复 | 批处理训练 |
| **DynaTrain** | Virtual Parameter Space (VPS) 抽象，亚秒级在线并行度切换 | 70B dense <2s，235B MoE <5s 重配置 |
| **LiveR** | 零回滚实时重配置，bounded-memory handoff | 99% goodput 在 volatile 资源环境 |

### 15.3 集合通信容错

| 方案 | 特点 |
|:-----|:-----|
| VCCL | 可观测 |
| OptCC | 理论下界 |
| R²CCL | 工程实现 |
| SHIFT | 理论边界 |
| **ReCoVer** | 梯度等价容错预训练，恒等 microbatch 不变式，2.23× effective throughput |
| **SPARe** | 600k GPU 可扩展，time-to-train 降低 40-50% |

### 15.4 Straggler 检测与缓解

| 技术 | 说明 | 量化数据 |
|:-----|:-----|:---------|
| **FEPLB** | 利用 NVLink Copy Engine 无成本重分发 expert/token | token straggler 降低 51-70% |
| **UltraEP** | RSN-native 精确负载均衡，force-balanced 吞吐 | 94.3% 理想吞吐，1.49× vs no-balancing |
| **动态 timeout** | 检测慢节点并动态调整 | 集群效率提升 |

### 15.5 GPU 故障检测与恢复

| 技术 | 说明 |
|:-----|:-----|
| NVIDIA DCGM | GPU 监控和诊断 |
| 预测性故障检测 | 基于历史数据预测故障 |
| 自动修复 | 故障 GPU 隔离/替换 |
| **ECC 纠错** | HBM 单比特错误自动纠正 |
| **Error Containment** | 错误隔离到单个应用，不影响其他任务 |
| **Dynamic Page Offlining** | 故障页面隔离，不影响整体运行 |
| **Row Remapping** | 硬件级行修复，替换 degraded 存储位置 |

---

## 16 服务器 RAS 验证与测试标准

### 16.1 内存 RAS 验证方法

| 测试方法 | 说明 | 工具 |
|:---------|:-----|:-----|
| **ECC 功能验证** | 注入单比特/多比特错误验证纠错能力 | mce-inject, EDAC |
| **ADDDC 验证** | 模拟双比特失效验证自适应纠正 | 厂商工具 |
| **PPR 验证** | 触发行错误验证修复机制 | BIOS POST, 内存测试 |
| **Mirroring 验证** | 主通道故障测试切换到镜像通道 | 厂商工具 |
| **Scrubbing 验证** | 长时间运行验证巡检功能 | memtester, 监控日志 |
| **温度 Stress** | 高温环境下 RAS 稳定性测试 | 环境舱 |

### 16.2 CPU/MCA 验证方法

| 测试方法 | 说明 |
|:---------|:-----|
| **BIST** | 启动自检验证核心功能 |
| **MCA 注入** | 通过 MSR 注入模拟错误 |
| **CMCI 验证** | 触发 CE 验证中断上报 |
| **UCR 恢复** | 验证 SRAR/SRAO 恢复机制 |
| **LMCE 验证** | 验证 Local MCE 仅发送单核 |
| **Watchdog 验证** | 触发 timeout 验证超时机制 |

### 16.3 PCIe RAS 验证

| 测试方法 | 说明 |
|:---------|:-----|
| **AER 功能测试** | 注入各种错误验证上报 |
| **DPC/EDPC 测试** | 触发错误验证 Containment |
| **Hot Plug 测试** | 动态插拔验证错误处理 |
| **Surprise Down 测试** | 模拟链路断开验证系统行为 |
| **EDR 测试** | 验证错误检测和恢复 |

### 16.4 BMC/IPMI RAS 验证

| 测试方法 | 说明 |
|:---------|:-----|
| **SEL 功能** | 触发事件验证 SEL 记录 |
| **传感器监控** | 触发阈值验证告警 |
| **电源控制** | 验证远程开/关/重启 |
| **SOL** | 验证串口重定向 |
| **Redfish** | 验证 REST API 功能 |
| **固件更新** | 验证带外固件更新 |

### 16.5 行业 RAS 验证标准

| 标准 | 说明 |
|:-----|:-----|
| **Intel RASPP** | Intel Reliability, Availability, Serviceability Platform Properties |
| **AMD RAS** | AMD EPYC RAS 功能验证套件 |
| **CIP** | Critical Infrastructure Protection |
| **NEBS** | Network Equipment Building System (电信设备) |
| **OCP** | Open Compute Project RAS 规范 |

### 16.6 可靠性测试方法

| 测试类型 | 说明 | 持续时间 |
|:---------|:-----|:---------|
| **HALT** | Highly Accelerated Life Test | 72-168h |
| **ALT** | Accelerated Life Test | 1000h+ |
| **ESS** | Environmental Stress Screening | 24-48h |
| **Burn-in** | 老化测试 | 24-72h |
| **MTBF 验证** | 平均故障间隔时间验证 | 统计模型 |

---

## 17 服务器系统级 RAS 设计

### 17.1 系统级 RAS 架构

| 层级 | 组件 | 职责 |
|:-----|:-----|:-----|
| **硬件层** | CPU/Memory/PCIe/CXL | 错误检测、局部纠正 |
| **固件层** | BIOS/UEFI/BMC | 错误记录、恢复决策、带外告警 |
| **驱动层** | OS Kernel, mcelog, edac | 错误处理、中断响应 |
| **应用层** | 业务软件 | 容错、CheckPoint |

### 17.2 错误传播与隔离

| 机制 | 说明 |
|:-----|:-----|
| **Poison** | 数据毒药位标记，阻止错误扩散 |
| **Viral** | CXL 协议层错误隔离 |
| **DPC** | PCIe 下游端口 Containment |
| **LMCE** | Local MCE 错误隔离 |
| **Error Containment** | GPU 错误隔离到单个应用 |
| **Page Offline** | 故障内存页隔离 |

### 17.3 故障恢复路径

```
故障检测 → 错误分类 → 恢复决策 → 执行恢复 → 业务继续
    ↓
┌──────────────────────────────────────────────────────┐
│ CE: 自动纠正 → 继续运行                               │
│ UCR(SRAO): 隔离错误结构 → 继续运行                    │
│ UCR(SRAR): 进程级恢复/终止 → 继续运行                 │
│ UCE(Fatal, PCC=1): 系统重启/带外重启                 │
└──────────────────────────────────────────────────────┘
```

### 17.4 MTTR 优化策略

| 策略 | 说明 | 效果 |
|:-----|:-----|:-----|
| **BMC 监控** | 实时硬件状态监控 | 故障预判 |
| **自动化告警** | 事件触发自动通知 | 快速响应 |
| **LED 指示** | 物理故障定位 | 现场快速定位 |
| **远程诊断** | SOL/Redfish 远程排查 | 减少现场出勤 |
| **自动化修复** | 脚本自动故障恢复 | 无人值守 |
| **热备切换** | 故障组件自动切换 | 业务不中断 |

### 17.5 常见服务器 RAS 配置

| 厂商 | RAS 特性 | 特色功能 |
|:-----|:---------|:---------|
| **Dell PowerEdge** | ECC/Chipkill/ADDDC/PPR/Mirroring | iDRAC 远程管理, Lifecycle Controller |
| **HPE ProLiant** | ECC/Advanced ECC/Mirroring | iLO 远程管理, Intelligent Provisioning |
| **Lenovo ThinkSystem** | ECC/Chipkill/PPR | XClarity 管理, 预测性故障分析 |
| **Cisco UCS** | ECC/ADDDC/PPR/VLS | CIMC 管理, 服务配置文件 |
| **Inspur** | ECC/Chipkill/PPR | BMC/IPMI, 远程运维 |

### 17.6 超融合/智算中心 RAS 设计

| 场景 | RAS 方案 |
|:-----|:---------|
| **虚拟化平台** | VM 迁移、HA、DRS、vMotion |
| **容器平台** | 容器重启、健康检查、资源限制 |
| **AI 训练** | Checkpoint、Straggler 检测、容错集合通信 |
| **分布式存储** | 多副本、EC、故障域隔离 |
| **数据库** | 主备复制、故障转移、自动切换 |

---

## 18 关键交叉引用

### 18.1 相关章节索引

| 主题 | 本文章节 |
|:-----|:---------|
| RAS 核心概念 | §1 |
| CPU MCA/MSR | §2, §11 |
| 内存 ECC/Chipkill | §3, §11 |
| 内存 Scrubbing | §3.6 |
| PCIe AER/DPC/EDPC | §4 |
| CXL RAS (散见) | §3.6.5, §11.3, §12 |
| 带外管理/BMC/IPMI | §5 |
| CrashDump | §6 |
| 错误阈值汇总 | §7 |
| 启动 RAS | §8.1 |
| 运行时 RAS | §8.2 |
| 环境监控 | §9 |
| 设计红线 | §10 |
| 芯片级 RAS 原理 | §11 |
| Intel Xeon 6 RAS | §12 |
| AMD EPYC 9005 RAS | §13 |
| GPU/NPU RAS | §14 |
| AI 训练可靠性 | §15 |
| RAS 验证测试 | §16 |
| 系统级 RAS 设计 | §17 |

### 18.2 关联文档

| 关联文件 | 内容衔接 |
|:---------|:---------|
| [06-BIOS/固件](../02_firmware/06-bios-firmware-design.md) | RAS 功能通过固件实现 |
| [08-散热](../01_hw_core/08-cooling-thermal-design.md) | 温度监控阈值衔接 |
| [09-供电](../01_hw_core/09-power-supply-architecture.md) | 供电保护机制 |
| [10-SI](../01_hw_core/10-signal-integrity-high-speed.md) | SI 仿真验证标准 |
| [11-测试](../03_sit/11-testing-validation.md) | 可靠性测试方案 |

### 18.3 核心参数速查

| 参数 | Intel | AMD |
|:-----|:------|:----|
| MCA Bank 数量 | 多 Bank (Core + Uncore) | 多 Bank (SMCA) |
| CMCI 默认阈值 | 10 | 可配置 |
| 内存 CE 阈值 (24h) | 30/rank | 可配置 (BIOS/SMCA) |
| PCIe CE 阈值 (24h) | 1000 | 可配置 (OS AER) |
| DDR5 通道数 (Xeon 6 / EPYC 9005) | 12 (6900P) / 8 (6700P) | 12 |
| 最大内存带宽 | 8800 MT/s (MRDIMM) | DDR5 RDIMM |
| ADDDC 支持 | ✓ (x4 DIMM) | ✓ |
| PPR 支持 | ✓ | ✓ |
| CXL 支持 | CXL 2.0 | CXL 2.0 |

### 18.4 错误代码映射

| 错误类型 | Intel MCACOD | AMD SMCA |
|:---------|:----------|:--------|
| 内存错误 | 0x01xx | MCACOD=0x0140 (MemCtlr) |
| 缓存错误 (DCache) | 0x02xx | MCACOD=0x0240 |
| TLB 错误 | 0x03xx | MCACOD=0x0340 |
| 互联错误 | 0x08xx | MCACOD=0x0800Ex (Gen Bus) |

> 注：AMD SMCA 通过 MCA_IPID 寄存器区分错误源 (CPU/DF/NBIO等)，错误码含义与 Intel 编码不完全一致；详细映射见 AMD PPR。

### 18.5 Linux RAS 命令

```bash
# MCA 错误日志
dmesg | grep -i mce
cat /var/log/mcelog

# EDAC 内存错误
cat /sys/devices/system/edac/mc/mc0/ce_count
cat /sys/devices/system/edac/mc/mc0/ue_count

# PCIe AER
lspci -vv -s 00:02.0 | grep -i aer

# IPMI SEL
ipmitool sel list | head -20

# GPU ECC
nvidia-smi -q -d ECC

# 查看 BMC 传感器
ipmitool sensor list
```

---

## 参考资料

1. Linux Kernel RAS Documentation: https://www.kernel.org/doc/html/next/admin-guide/RAS/main.html
2. Intel SDM Vol. 3B: Machine-Check Architecture
3. AMD Software Development Manual (SMCA)
4. Intel EMCA 2.0 Specification
5. AMD ROCm RAS Documentation
6. Cisco UCS M7 and M8 Compute Servers Memory Technical Overview — Memory RAS Features White Paper (2026)
7. Dell EMC PowerEdge YX4X Memory RAS White Paper (2022)
8. CSDN: x86架构MCA与MCE机制深度解析
9. Minzkn MCE (Machine Check Exception) 技术详解
10. Intel In-field Scan RAS 方案 (内部文档)
11. NVIDIA GPU Memory Error Management (R575): https://docs.nvidia.com/deploy/pdf/NVIDIA-GPU-Memory-Error-Management.pdf
12. Intel Xeon 6 处理器 RAS 特性技术白皮书 (2026): https://www.intel.cn/content/dam/www/central-libraries/cn/zh/documents/2026-04/26-dco-ras-technology-brief-white-book.pdf
13. Lenovo ThinkSystem Intel Servers RAS Features (LP1711, 2025): https://lenovopress.lenovo.com/lp1711-ras-features-of-the-lenovo-thinksystem-intel-servers
14. CXL 3.1 RAS Whitepaper (An Overview of RAS for Compute Express Link 3.1, 2024-03): https://computeexpresslink.org/wp-content/uploads/2024/08/An-Overview-of-RAS-for-Compute-Express-Link-3.1-Whitepaper.pdf
15. AMD 5th Gen EPYC Architecture White Paper (2024-10): https://www.amd.com/content/dam/amd/en/documents/epyc-business-docs/white-papers/5th-gen-amd-epyc-processor-architecture-white-paper.pdf
16. Kingston Intel Xeon 6 Guide: https://kingston.com/en/blog/servers-and-data-centers/intel-xeon-6-guide-features-benefits-use-cases
17. Linux Kernel EDAC (Error Detection and Correction)
18. Linux Kernel PCI AER documentation
19. IPMItool User Guide
20. Redfish API Specification (DMTF DSP0266)
21. ACPI Specification (APEI/HEST/BERT/EINJ)
22. 大规模分布式训练论文: DynaTrain, LiveR, SPARe, ReCoVer, UltraEP, DisagMoE
23. MCE 调试与故障排查: perf, ftrace, eBPF
24. 内存错误与服务器 RAS: memtester, mce-inject
25. CXL RAS Capabilities (2024): https://computeexpresslink.org/blog/understanding-cxl-ras-capabilities-enhancing-performance-and-reliability-across-modern-data-centers-2947/
26. GPU闲置与物理极限应对策略 (Keysight KAI): https://m.sohu.com/a/912277614_122014422/
