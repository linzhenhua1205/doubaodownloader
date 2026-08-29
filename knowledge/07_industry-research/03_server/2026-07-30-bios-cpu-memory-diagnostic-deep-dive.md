# 🧬 BIOS CPU/内存诊断能力深度规格：POST诊断·内存RAS·CPU RAS·诊断接口

> **概要**: 基于可服务性规格说明书 §1.1 (CPU) 和 §1.2 (DIMM) 的深度展开，覆盖BIOS/UEFI在CPU和内存子系统的诊断能力设计——从POST自检到运行时RAS，从CE/UE精确定位到故障隔离，从诊断日志到BMC协同。
>
> **关键词**: BIOS诊断 · CPU RAS · 内存RAS · ECC · POST诊断 · MCA · CMCI · DIMM故障定位 · 内存训练 · 服务器UEFI
>
> **适用范围**: 服务器BIOS/UEFI固件设计·CPU/内存硬件诊断·RAS功能定义
>
> **目标读者**: BIOS固件架构师·硬件诊断工程师·RAS可靠性工程师·系统测试
>
> **关联文档**: [可服务性规格总表](2026-07-30-server-serviceability-specification.md) · [处理器调试能力演进](../../02_rd/01_product/00_hardware/01_hw-core/2026-07-02-processor-debug-capabilities.md) · [GPU故障检测全景](../../02_rd/01_product/00_hardware/05_ras/2026-07-23-gpu-fault-detection-comprehensive-analysis.md)

---

## 📑 目录

- [§0 执行摘要](#§0-执行摘要)
- [§1 CPU POST诊断能力](#§1-cpu-post诊断能力)
  - [1.1 CPU检测流程](#11-cpu检测流程)
  - [1.2 CPU故障类型与诊断码](#12-cpu故障类型与诊断码)
  - [1.3 CPU微码诊断](#13-cpu微码诊断)
  - [1.4 CPU缓存诊断](#14-cpu缓存诊断)
  - [1.5 CPU互连(UPI/CCIX)诊断](#15-cpu互连upiccxi诊断)
- [§2 内存POST诊断能力](#§2-内存post诊断能力)
  - [2.1 内存检测流程与训练](#21-内存检测流程与训练)
  - [2.2 内存故障类型与诊断码](#22-内存故障类型与诊断码)
  - [2.3 内存训练回退策略](#23-内存训练回退策略)
  - [2.4 内存参数自动优化](#24-内存参数自动优化)
  - [2.5 内存子系统的边缘诊断](#25-内存子系统的边缘诊断)
- [§3 CPU运行时RAS诊断](#§3-cpu运行时ras诊断)
  - [3.1 MCA (Machine Check Architecture)](#31-mca-machine-check-architecture)
  - [3.2 CMCI (Corrected Machine Check Interrupt)](#32-cmci-corrected-machine-check-interrupt)
  - [3.3 CPU Thermal Control](#33-cpu-thermal-control)
  - [3.4 CPU故障信息上报](#34-cpu故障信息上报)
- [§4 内存运行时RAS诊断](#§4-内存运行时ras诊断)
  - [4.1 ECC错误处理](#41-ecc错误处理)
  - [4.2 Patrol Scrub与Demand Scrub](#42-patrol-scrub与demand-scrub)
  - [4.3 内存故障预测与容错](#43-内存故障预测与容错)
  - [4.4 DDR5新RAS特性](#44-ddr5新ras特性)
- [§5 BIOS诊断日志与BMC协同](#§5-bios诊断日志与bmc协同)
  - [5.1 BIOS诊断日志输出](#51-bios诊断日志输出)
  - [5.2 BIOS-BMC错误通道](#52-bios-bmc错误通道)
  - [5.3 POST失败诊断流程](#53-post失败诊断流程)
  - [5.4 运行时报错流程](#54-运行时报错流程)
- [§6 CPU/内存可服务性规格总表](#§6-cpu内存可服务性规格总表)
- [参考文献](#参考文献)
- [变更记录](#变更记录)

---

## §0 执行摘要

### 0.1 BIOS在CPU/内存诊断中的不可替代性

BIOS/UEFI是硬件上线后**第一道**诊断关卡——在OS启动之前，BIOS已经完成了对CPU和内存子系统的全面检测。诊断能力的强弱决定了：

```text
POST Phase（BIOS的用武之地）
    |
    +-- 检测成功 -> 正常启动 -> OS层运行时RAS继续监控
    |
    +-- 检测失败 -> 以下能力决定问题能否快速定位：
          +-- ❌ 仅报"Memory Error" -> 现场人员排查≥30分钟
          +-- ✅ 报"DIMM_A1, CE count 127, SPD vendor: Samsung" -> 5分钟定位更换
          +-- ✅✅ 再附"建议: 更换DIMM_A1，备件型号M393R4G73Z1-CRC1" -> 直接执行
```

**核心能力目标**:

| 指标 | BIOS POST阶段 | OS运行时阶段 |
|:-----|:-------------:|:------------:|
| 故障定位精度 | 到DIMM槽位/CPU物理Socket | 到DIMM/CPU+准确地址 |
| 故障检测覆盖率 | ≥99%的可检测硬件故障 | ≥95%运行时错误 |
| 诊断输出可读性 | 清晰的POST Code+文本输出 | Redfish/IPMI结构化上报 |
| 自愈能力 | 内存降级/CPU离线核心 | Patrol Scrub+页迁移 |

### 0.2 CPU/内存RAS能力四层模型

```text
L4: 故障预测与自愈
    +-------------------------------------+
    |  CE趋势预测·页迁移·在线核心隔离    |
    +-------------------------------------+
L3: 运行时错误报告
    +-------------------------------------+
    |  MCA/MCE·CMCI·EDAC·PCIe AER        |
    +-------------------------------------+
L2: POST阶段全面诊断
    +-------------------------------------+
    |  CPU缓存测试·内存测试DIMM全覆盖   |
    |  内存训练优化·参数校验             |
    +-------------------------------------+
L1: 基本POST检测
    +-------------------------------------+
    |  CPU识别·微码加载·基本内存训练    |
    |  内存槽在位检测·SPD读取           |
    +-------------------------------------+
```

---

## §1 CPU POST诊断能力

### 1.1 CPU检测流程

BIOS在POST阶段对CPU的检测按以下顺序进行：

```text
POST Sequence
    |
    1. CPU微码更新（Microcode Patch）
       +-- 加载微码补丁
       +-- 校验微码签名（Intel Boot Guard/AMD PSP）
       +-- 验证微码版本≥基线版本
    |
    2. CPU基本信息检测
       +-- CPUID: 提取Family/Model/Stepping
       +-- Brand String: 型号名
       +-- 核心数/线程数 (包括Disable状态)
       +-- 缓存大小 (L1/L2/L3)
    |
    3. CPU功能检测
       +-- 指令集支持检查 (AVX2/AVX-512/AMX/SGX等)
       +-- MSR配置验证
       +-- RAS特性启用(如MCA/CMCI/Poison等)
    |
    4. 多处理器检测（双路/四路）
       +-- Socket在位检测
       +-- UPI链路检测数目
       +-- UPI链路速度协商
       +-- 拓扑一致性检查
    |
    5. CPU缓存测试 (可选，默认跳过)
       +-- L1/L2/L3 Cache功能测试
       +-- 缓存ECC测试(如支持)
    |
    6. CPU计算逻辑的快速测试 (可选)
       +-- BIST (Built-In Self-Test) 执行+读结果
       +-- 数学运算基本验证
```

### 1.2 CPU故障类型与诊断码

| 故障类型 | 硬件原因 | 可检测方式 | POST Code | 影响 |
|:---------|:---------|:----------|:---------:|:-----|
| **CPU缺失** | Socket未安装CPU | 定位信号检测 | D0-D2 | 无法启动 |
| **CPU不匹配** | 多路CPU型号/Stepping不一致 | CPUID比对 | D3-D4 | 无法启动 |
| **CPU损坏** | CPU内部电路失效 | BIST失败 | D5 | 无法启动 |
| **微码失败** | 微码加载失败/不兼容 | 加载状态检查 | D6-D7 | 启动失败 |
| **UPI互联失败** | 双路CPU间链路不通 | UPI Link Training | D8-DA | ×1/×2降级或无法启动 |
| **CPU过热** | 散热器未安装/接触不良 | PECI温度读回 | DB-DC | 过热降频或关机 |
| **CPU VR失效** | 供电模组故障 | PECI电压读回 | DD | 无法启动 |
| **缓存失效** | L3 Cache Controller错误 | Cache测试 | DE | 核心禁用 |
| **BIST失败** | CPU内置自检失败 | JTAG/BIST寄存器 | DF | 替换CPU |
| **CPU(某核心)故障** | 单个核心失效 | CPU内部标记 | E0 | 核心禁用(降级运行) |

**关键POST Code设计原则**:

- POST Code编码体系须与CPU厂商规范一致（Intel/AMD/Ampere各厂商不同）
- POST Code须在板载数字DEBUG卡和BMC LOG双路可见
- POST Code出现频率（停留时间）仅体现瓶颈位置，不能仅凭Code判断故障

### 1.3 CPU微码诊断

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 | 执行部门 |
|:----:|:-------|:---------|:--------:|:---------|:---------|
| BIOS-CPU-MC-001 | 微码版本验证 | BIOS加载前验证微码版本≥基线 | MUST | 过低版本拒绝加载+告警 | BIOS固件 |
| BIOS-CPU-MC-002 | 微码签名验证 | 所有微码更新须通过Intel/AMD签名验证 | MUST | 未签名微码拒绝加载 | BIOS固件 |
| BIOS-CPU-MC-003 | 微码加载日志 | 微码加载结果(成功/失败/版本)记录到BIOS日志+BMC | MUST | 日志含版本号和校验和 | BIOS固件 |
| BIOS-CPU-MC-004 | 微码兼容检查 | 多路CPU的微码版本一致性检查 | MUST | 不一致告警 | BIOS固件 |
| BIOS-CPU-MC-005 | 微码回退 | 新微码导致启动失败时自动回退到上版本 | MUST | 回退成功率>99% | BIOS固件 |

### 1.4 CPU缓存诊断

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BIOS-CPU-CACHE-001 | Cache ECC检测 | L1/L2/L3 Cache ECC错误可通过MCA读取 | MUST | 可读Correctable/Uncorrectable |
| BIOS-CPU-CACHE-002 | Cache自检 | POST阶段可配置使能Cache功能测试(默认关闭以加速启动) | SHOULD | 全缓存测试<30秒 |
| BIOS-CPU-CACHE-003 | 缓存禁用 | 检测到L3 Cache故障时自动禁用该核心/最后一级缓存 | SHOULD | 禁用后系统可降级运行 |
| BIOS-CPU-CACHE-004 | 缓存错误上报 | Cache ECC错误通过MCA上报到BIOS日志+BMC | MUST | — |

### 1.5 CPU互连(UPI/CCIX)诊断

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BIOS-CPU-UPI-001 | UPI链路状态 | BIOS训练后报告每UPI链路状态(Active/Degraded/Inactive) | MUST | 链路数量/n宽度/速度 |
| BIOS-CPU-UPI-002 | UPI链路降级告警 | UPI链路宽数低于预期时记录日志+告警 | MUST | 如×20→×16需告警 |
| BIOS-CPU-UPI-003 | UPI重训练 | 首次训练失败支持自动重训练(最多3次) | MUST | 重训练策略可配置 |
| BIOS-CPU-UPI-004 | UPI拓扑验证 | 多路系统的UPI拓扑与预期一致 | MUST | 拓扑错误记录日志 |

---

## §2 内存POST诊断能力

### 2.1 内存检测流程与训练

BIOS内存检测是POST中最复杂、最耗时的阶段，也是故障最常见的位置：

```text
Memory Initialization Sequence
    |
    1. 内存硬件检测
       +-- DIMM槽位检测 (Presence Detect)
       +-- SPD内容读取 (JEDEC标准)
       |     +-- DDR5: SPD Hub I2C 地址0x50-0x57
       |     +-- 读出容量/速度/时序/制造商/SN/温度
       +-- PMIC (电源管理IC)初始化(DDR5新增)
    |
    2. 内存训练 (Memory Training)
       +-- DDR5: DFE/FFE均衡训练
       +-- DDR5: 写均衡 (Write Leveling)
       +-- DDR5: 读均衡 (Read Leveling)
       +-- DDR5: CA训练(Command/Address)
       +-- DDR5: Vref训练
       +-- DDR5: 延迟训练(RC/RD/WR等)
       +-- 高速模式: ODTS/ALIAS等
    |
    3. 内存控制器配置
       +-- 通道间交织
       +-- Rank/ChipSelect配置
       +-- ECC模式启用
       +-- 内存RAS特性配置(Scrub/Mirror/Sparing)
       +-- Address Mapping(1-way/2-way/3-way)
    |
    4. 内存测试 (可选)
       +-- 快速测试: 基本读写+地址线测试
       +-- 全面测试: 全地址+Walking 1/0
       +-- 连接器测试: DIMM接触不良检测
    |
    5. 内存MAP构建
       +-- 有效内存范围映射
       +-- 坏块标记(Manufacturing Defect或运行时CE)
       +-- 保留区域(BMC/BIOS/SMM专用)
```

**内存训练的超时控制**:

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BIOS-MEM-TRAIN-001 | 训练超时 | 每通道训练超时可配置(默认120秒) | MUST | 超时后跳过该通道继续启动 |
| BIOS-MEM-TRAIN-002 | 训练进度上报 | 训练进度通过POST Code(粒度≤16个Code)上报 | MUST | 每个训练阶段的Code可见 |
| BIOS-MEM-TRAIN-003 | 训练失败回退 | 失败→降低速度/放松时序重训 | MUST | 回退策略自动执行 |
| BIOS-MEM-TRAIN-004 | 训练结果保存 | 成功训练参数保存到NVRAM减少下次训练时间 | MUST | MRC Cache |

### 2.2 内存故障类型与诊断码

| 故障类型 | 硬件原因 | 可检测方式 | POST Code | 故障定位 |
|:---------|:---------|:----------|:---------:|:---------|
| **DIMM缺失** | DIMM槽为空 | Presence信号 | 50 | 精确槽位 |
| **DIMM不匹配** | 同一通道DIMM容量/厂商不一致 | SPD比对 | 51 | 具体槽位 |
| **SPD读取失败** | DIMM SPD损坏/I2C故障 | I2C通信失败 | 52 | 具体DIMM |
| **DIMM损坏** | DIMM物理损坏/芯片失效 | 训练失败 | 53-55 | 具体DIMM |
| **PMIC故障** (DDR5) | PMIC I2C无响应/电压异常 | PMIC寄存器读回 | 56 | 具体DIMM |
| **RCD故障** (DDR5) | 寄存时钟驱动器错误 | RCD状态检查 | 57 | 具体通道 |
| **训练失败-写均衡** | 信号质量问题 | 训练算法 | 58 | 具体Channel/Rank |
| **训练失败-读均衡** | 信号质量问题 | 训练算法 | 59 | 具体Channel/Rank |
| **训练失败-CA** | Command/Address信号问题 | 训练算法 | 5A | Rank级别 |
| **时序无法收敛** | 主板信号完整性差 | 多次重训均失败 | 5B | 整体(检查主板/Dimm) |
| **连接器接触不良** | DIMM槽金手指氧化/变形 | 特定Rank间歇失败 | 5C | 具体DIMM槽 |
| **内存地址冲突** | Reserved Memory重叠 | 地址空间分配冲突 | 5D | 软件配置 |
| **ECC初始化失败** | ECC模式无法启用 | ECC初始化状态 | 5E | 内存控制器 |

### 2.3 内存训练回退策略

**自动回退流程**:

```text
内存训练开始（目标速度: DDR5-5600）
    |
    +-- 成功 -> 保存参数 -> 进入下一步
    |
    +-- 失败 -> 自动回退策略:
          |
          +-- 第一级: 放松时序(CAS Latency+1)
          |     +-- 再尝试 -> 成功->记录降级->告警(Minor)
          |
          +-- 第二级: 降低频率(Data Rate-400MHz)
          |     +-- 再尝试 -> 成功->记录降级->告警(Major)
          |
          +-- 第三级: 仅禁用失败通道
          |     +-- 成功->容量减少->告警(Critical)
          |
          +-- 第四级: 标记DIMM故障->跳过->进入OS(降级模式)
                +-- SEL记录+告警(Critical)+标记DIMM故障

```

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BIOS-MEM-RETRY-001 | 自动回退 | 训练失败自动执行回退策略≥3级 | MUST | 回退策略表中流程正确 |
| BIOS-MEM-RETRY-002 | 回退记录 | 每级回退记录原因+当前参数到BIOS日志 | MUST | 日志含前一次失败的参数 |
| BIOS-MEM-RETRY-003 | 回退告警 | 任何降级回退触发SEL事件+BMC告警 | MUST | 降级精度×频率记录 |
| BIOS-MEM-RETRY-004 | 回退上限 | 最大回退次数(默认3次)后不再自动尝试 | MUST | 超过上限后设为最宽松参数 |

### 2.4 内存参数自动优化

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BIOS-MEM-OPT-001 | MRC Cache | 成功训练参数保存到NVRAM | MUST | 下次启动跳过训练<5秒 |
| BIOS-MEM-OPT-002 | 温度自适应 | 基于DIMM温度传感器动态调整刷新率(温度越高刷新越密集) | MUST | DDR5 FGR/FI功能 |
| BIOS-MEM-OPT-003 | 参数精细调优 | 支持按DIMM颗粒级调优时序参数 | SHOULD | 每DIMM独立参数 |
| BIOS-MEM-OPT-004 | 兼容参数集 | 存储多套参数配置(极限/平衡/兼容) | SHOULD | 可通过BIOS Setup切换 |

### 2.5 内存子系统的边缘诊断

**早期故障检测手段**:

| 诊断项 | 诊断方法 | 可发现的问题 | 建议启动项 |
|:-------|:---------|:-------------|:----------|
| 连接器压痕验证 | 物理目检(DIMM金手指) | 安装不到位/金手指划痕 | 制造环节 |
| 内存地址线测试 | Walking 1/0模式 | 地址线短路/断路 | POST开启(默认关闭) |
| 内存数据线测试 | Prbs模式 | 数据线信号完整性 | POST开启(默认关闭) |
| Bank冲突测试 | 连续多个Bank访问 | 内存控制器内部问题 | 深度诊断 |
| 温度循环测试 | -10°C/+70°C环境 | 温度敏感故障 | 可靠性测试 |

---

## §3 CPU运行时RAS诊断

### 3.1 MCA (Machine Check Architecture)

MCA是CPU报告硬件错误的**标准体系结构**，覆盖CPU内部的所有可检测错误。

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BIOS-CPU-RAS-001 | MCA启用 | BIOS在POST阶段全面启用MCA功能 | MUST | 所有CPU支持的MCA Bank均已使能 |
| BIOS-CPU-RAS-002 | MCA Bank覆盖 | 覆盖CPU所有MCA Bank（Core/Uncore/Memory/Interconnect等） | MUST | Bank列表与CPU厂商规格一致 |
| BIOS-CPU-RAS-003 | MCERR/NMI处理 | 不可恢复MCA错误（MCERR）触发NMI并记录 | MUST | 错误记录包含:Bank/Status/Misc/Addr |
| BIOS-CPU-RAS-004 | MCA恢复 | 支持Recoverable MCA（SRAR/SRAO）的处理和恢复 | MUST | 可恢复错误不导致系统崩溃 |
| BIOS-CPU-RAS-005 | MCA日志 | MCA错误完整记录到BIOS日志(SMBIOS Type 32) | MUST | 日志含完整MCi_STATUS/MCi_ADDR |
| BIOS-CPU-RAS-006 | MCA上报BMC | MCA严重错误(UCNA/SRAR/SRAO)上报BMC SEL | MUST | 上报延迟<1秒 |
| BIOS-CPU-RAS-007 | MCA配置持久化 | MCA相关MSR配置保存并在重置后保持 | MUST | — |

**MCA错误类型速查**:

| MCA错误类型 | 严重级 | 可恢复性 | CPU行为 | OS可见性 |
|:------------|:------:|:--------:|:---------|:---------|
| **Corrected** (CE) | 已纠正 | 完全可恢复 | 继续执行，记录计数 | CMCI通知 |
| **UCNA** (Uncorrected No Action) | 警告 | 数据未损坏但无法纠正 | 继续执行 | SIGBUS/Poison |
| **SRAR** (Software Recoverable Action Required) | 严重 | 可恢复(如隔离页面) | 异常分发 | SIGBUS+恢复处理 |
| **SRAO** (Software Recoverable Action Optional) | 严重 | 可恢复 | 继续执行 | 轮询检查 |
| **UC** (Uncorrected+Fatal) | 致命 | 不可恢复 | Panic/Halt | MCE/Kernel Panic |

### 3.2 CMCI (Corrected Machine Check Interrupt)

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BIOS-CPU-CMCI-001 | CMCI启用 | BIOS使能CMCI功能 | MUST | 所有支持的CPU |
| BIOS-CPU-CMCI-002 | CMCI阈值配置 | CE错误触发CMCI的阈值可配置(默认10次/秒) | MUST | 每MCA Bank独立阈值 |
| BIOS-CPU-CMCI-003 | CMCI代理处理 | CMCI中断由SMI处理→记录SEL→通知OS | MUST | OS可选择接管或由BIOS处理 |
| BIOS-CPU-CMCI-004 | CMCI风暴保护 | CE错误爆发时(>100次/秒)触发风暴抑制 | MUST | 风暴抑制后降级为轮询 |

### 3.3 CPU Thermal Control

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BIOS-CPU-THERM-001 | PROCHOT | CPU PROCHOT(过热)信号触发时BMC记录+告警 | MUST | 告警延迟<10秒 |
| BIOS-CPU-THERM-002 | THERMTRIP | CPU THERMTRIP(热关断)时BMC立即记录+Critical告警 | MUST | 记录含关断前最后传感器读值 |
| BIOS-CPU-THERM-003 | CPU温度监控 | PECI接口读回CPU温度(DTS)，1秒刷新 | MUST | 精度±1°C |
| BIOS-CPU-THERM-004 | 热节流记录 | CPU因过热降频(TM1/TM2)时记录到BIOS日志 | MUST | 记录降频持续时间和程度 |

### 3.4 CPU故障信息上报

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BIOS-CPU-REPORT-001 | CPU信息上报 | BIOS运行时提供CPU信息(Stepping/Microcode/核心数/频率) | MUST | Redfish/SMBIOS可查 |
| BIOS-CPU-REPORT-002 | CPU故障定位 | CPU故障时输出物理Socket编号+核心编号 | MUST | 多路故障明确标识 |
| BIOS-CPU-REPORT-003 | CPU核心禁用 | 故障核心可通过BIOS/BMC禁用(降级运行) | MUST | 禁用后OS可降级运行 |
| BIOS-CPU-REPORT-004 | 核心禁用持久化 | 核心禁用状态保存在BMC NVRAM | MUST | 重启后保持禁用状态 |

---

## §4 内存运行时RAS诊断

### 4.1 ECC错误处理

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BIOS-MEM-RAS-001 | ECC启用 | 所有DIMM ECC功能在POST阶段启用 | MUST | ECC启用后系统日志可见 |
| BIOS-MEM-RAS-002 | CE计数 | 每DIMM的CE(可纠正错误)独立计数 | MUST | EDAC可读/SMBIOS可查 |
| BIOS-MEM-RAS-003 | UE计数 | 每DIMM的UE(不可纠正错误)独立计数 | MUST | UE>0立即上报BMC |
| BIOS-MEM-RAS-004 | CE趋势 | BIOS/OS可查询CE计数历史趋势 | MUST | 趋势数据保存≥24h |
| BIOS-MEM-RAS-005 | CE阈值告警 | CE增速超过阈值时触发告警 | MUST | 默认阈值可配置 |
| BIOS-MEM-RAS-006 | ECC地址记录 | ECC错误关联到物理地址+DIMM+RANK+Bank | MUST | 精确定位>99% |

**ECC错误上报链**:

```text
DIMM 发生CE错误
    |
    +-- 硬件: DDR5 On-Die ECC纠正(芯片级)
    |
    +-- 硬件: DDR5 DQ Error Pinpoint->DRAM颗粒级ECC
    |
    +-- 内存控制器: 记录CE到寄存器
    |     +-- CMCI->SMI->BIOS记录(槽位+地址+计数)
    |
    +-- OS层: EDAC驱动读取->CE计数累加
    |
    +-- BMC: IPMI/Redfish查询CE计数
```

### 4.2 Patrol Scrub与Demand Scrub

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BIOS-MEM-SCRUB-001 | Patrol Scrub | BIOS在POST阶段使能内存巡逻巡检(Patrol Scrub) | MUST | Scrub覆盖全地址空间 |
| BIOS-MEM-SCRUB-002 | Scrub周期 | 巡逻周期可配置(默认24小时全量扫描一次) | MUST | 周期配置通过BIOS Setup |
| BIOS-MEM-SCRUB-003 | Demand Scrub | 读操作时触发一次ECC修正后写回 | MUST | 使能自动开启 |
| BIOS-MEM-SCRUB-004 | Scrub发现记录 | Scrub发现的CE记录到SEL和EDAC | MUST | — |
| BIOS-MEM-SCRUB-005 | Scrub对性能影响 | Patrol Scrub期间对正常访问的性能影响<1% | MUST | — |
| BIOS-MEM-SCRUB-006 | DDR5 Scrubbing增强 | DDR5支持每Die的独立Scrub能力 | MUST | 通过DDR5 MIR/MOR寄存器配置 |

### 4.3 内存故障预测与容错

**分层容错策略**:

| 等级 | 策略 | 触发条件 | 影响 | 恢复方式 |
|:-----|:-----|:---------|:-----|:---------|
| **L1** | CE持续监控 | CE计数>0 | 无 | Patrol Scrub自动修复 |
| **L2** | CE增速预警 | CE增速>10/hour | 记录+预警 | 计划维护窗口更换 |
| **L3** | CE爆发抑制 | CE增速>100/hour | 告警+性能轻微影响 | 标记页→迁移到好区域 |
| **L4** | UE隔离 | 出现UE | 部分内存区域不可用 | PAGE_ISOLATE+告警 |
| **L5** | DIMM禁用 | UE持续增加/DIMM掉线 | 系统容量减少 | 降级运行+计划更换 |

**内存页迁移(Poison Page Migration)**:

```text
OS检测到UE(Page Poison) -> RAS Daemon捕获
    |
    +-- MCA通知: 错误地址+DIMM+Rank
    |
    +-- OS标记该页为Poisoned -> 停止分配使用
    |
    +-- 数据恢复(如可): 通过RAID/ZFS重建
    |
    +-- 通知BMC: 该DIMM CE累计+页迁移事件记录
```

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BIOS-MEM-RAS-101 | CE预测 | 基于CE增速趋势预测DIMM剩余寿命 | MUST | 预测提前≥72小时 |
| BIOS-MEM-RAS-102 | DIMM降级标记 | CE增速超过阈值标记DIMM降级 | MUST | 降级标记持久化 |
| BIOS-MEM-RAS-103 | 故障DIMM保护 | 降级DIMM优先用于非关键工作负载 | SHOULD | 内存分配策略可配置 |
| BIOS-MEM-RAS-104 | 退役DIMM管理 | 退役DIMM不参与OS可用内存池 | SHOULD | — |
| BIOS-MEM-RAS-105 | 内存错误关联 | 关联同一DIMM的CE和UE记录 | MUST | 时间线完整 |

**RAM错误率参考基线**:

| 环境 | CE Rate (每小时每DIMM) | 年故障率(FR) |
|:-----|:----------------------:|:-------------:|
| 理想环境(实验室) | <0.01 | <0.5% |
| 数据中心(正常) | <0.1 | 1-2% |
| 高温/高负载 | <1.0 | 3-5% |
| 故障DIMM(预警) | >10.0 | >50% |

### 4.4 DDR5新RAS特性

DDR5相对DDR4在RAS方面的关键增强：

| DDR5 RAS特性 | 能力描述 | 诊断利用 |
|:-------------|:---------|:---------|
| **On-Die ECC** | 芯片内部ECC，纠正单比特错误 | CE计数覆盖颗粒级 |
| **DQ Error Pinpoint** | 精确定位到DRAM颗粒的哪个DQ(数据线) | 定位PCB/连接器故障 |
| **PMIC监控** | 每DIMM独立PMIC(电压VDD/VDDQ/VPP) | 供电问题精确诊断 |
| **SPD Hub Rev5** | 温度传感器精度±0.5°C+写入耐久性计数 | 精细化温度趋势 |
| **RCD (Register Clock Driver)** | 含温度传感器+错误日志 | 通道级时序诊断 |
| **DDR5 FGR** | 细粒度刷新(Fine Granularity Refresh) | 根据温度动态调整刷新率 |
| **DDR5 MIR/MOR** | Memory Inline Repair/Offline Repair | 芯片级坏行标记 |
| **DDR5 Read/Write Leveling** | 更精细的均衡训练 | 信号完整性诊断 |

---

## §5 BIOS诊断日志与BMC协同

### 5.1 BIOS诊断日志输出

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BIOS-LOG-001 | POST Code | POST过程输出POST Code到LPC/eSPI和BMC | MUST | Code序列完整可捕获 |
| BIOS-LOG-002 | BIOS文本日志 | BIOS关键事件输出到UART串口(可被BMC SOL捕获) | MUST | 含时间戳+事件描述+状态 |
| BIOS-LOG-003 | BIOS错误日志 | BIOS检测到的硬件错误写入NVRAM供OS读取 | MUST | SMBIOS Type 32 |
| BIOS-LOG-004 | 诊断日志分级 | BIOS日志支持Error/Warning/Info/Verbose四级 | MUST | 默认Info及以上输出 |
| BIOS-LOG-005 | 日志持久化 | 诊断日志在POST成功后保存到BMC Flash | MUST | 掉电不丢失 |

### 5.2 BIOS-BMC错误通道

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BIOS-BMC-001 | BIOS→BMC错误推送 | BIOS检测到硬件错误立即通过SMI通知BMC | MUST | 通知延迟<1秒 |
| BIOS-BMC-002 | BMC→BIOS诊断命令 | BMC可通过eSPI/LPC向BIOS发诊断命令 | MUST | 命令响应<10秒 |
| BIOS-BMC-003 | BIOS诊断日志同步 | POST结束后BIOS将诊断日志同步到BMC | MUST | 同步完整率100% |
| BIOS-BMC-004 | POST进度同步 | BIOS将POST阶段/进度/挂起位置同步到BMC | MUST | BMC可通过Redfish查询POST状态 |
| BIOS-BMC-005 | POST失败协同 | POST失败时BIOS+BMC各自故障现场→合并快照 | MUST | 合并快照一致性>99% |

### 5.3 POST失败诊断流程

```text
POST失败
    |
    +-- 1. BIOS捕获故障POST Code（挂起在特定Code）
    |
    +-- 2. BIOS将失败POST Code+上下文写入BMC
    |       +-- 当前阶段(PEI/DXE/BDS)
    |       +-- 最近的10个POST Code序列
    |       +-- 失败部件的寄存器/SPD/状态
    |       +-- BMC当前传感器快照
    |
    +-- 3. BMC标记POST失败事件到SEL
    |
    +-- 4. 诊断建议输出:
    |       +-- 确定故障类型(CPU/内存/PCIe/其他)
    |       +-- 故障定位(具体Slot/DIMM/Socket)
    |       +-- 建议操作(更换/重新安装/清理)
    |
    +-- 5. 尝试自动恢复(如配置):
           +-- BIOS默认设置启动
           +-- 内存最兼容参数启动
           +-- 禁用故障DIMM启动
```

### 5.4 运行时报错流程

```text
OS运行时 内存CE错误
    |
    +-- 1. HW: DDR5 On-Die ECC 纠正
    |
    +-- 2. HW: 内存控制器记录CE计数+地址
    |
    +-- 3. CMCI -> SMI -> BIOS SMI Handler:
    |       +-- 读取CE计数+故障地址
    |       +-- 写入SEL+BMC日志
    |       +-- 清除CE标记
    |
    +-- 4. OS: EDAC驱动通过MCA读取CE计数
    |
    +-- 5. BMC: 轮询/事件驱动获取CE趋势
           +-- 正常 -> 继续监控
           +-- 超标 -> 告警(计划更换DIMM)
```

---

## §6 CPU/内存可服务性规格总表

| 模块 | 规格数 | MUST | SHOULD | 执行部门 |
|:-----|:------:|:----:|:------:|:---------|
| CPU微码诊断 | 5 | 5 | 0 | BIOS固件 |
| CPU缓存诊断 | 4 | 2 | 2 | BIOS固件 |
| CPU UPI诊断 | 4 | 4 | 0 | BIOS固件 |
| CPU MCA | 7 | 7 | 0 | BIOS固件 |
| CPU CMCI | 4 | 4 | 0 | BIOS固件 |
| CPU Thermal | 4 | 4 | 0 | BIOS+BMC |
| CPU上报 | 4 | 4 | 0 | BIOS+BMC |
| 内存训练 | 4 | 4 | 0 | BIOS固件 |
| 内存故障诊断 | 13 | 13 | 0 | BIOS固件 |
| 训练回退 | 4 | 4 | 0 | BIOS固件 |
| 内存参数优化 | 4 | 3 | 1 | BIOS固件 |
| ECC处理 | 6 | 6 | 0 | BIOS+OS |
| Patrol Scrub | 6 | 6 | 0 | BIOS固件 |
| 内存故障预测 | 5 | 4 | 1 | BIOS+BMC |
| DDR5 RAS | — | — | — | 硬件+BIOS |
| BIOS日志 | 5 | 5 | 0 | BIOS固件 |
| BIOS-BMC协同 | 5 | 5 | 0 | BIOS+BMC |
| **合计** | **88** | **80(91%)** | **8(9%)** | |

**验收测试核心用例**:

| 测试项 | 测试方法 | 通过标准 |
|:-------|:---------|:---------|
| POST Code序列验证 | 采集正常启动→故障注入→比较Code差异 | 故障注入后Code明显不同 |
| 内存故障模拟 | 模拟DIMM故障→验证POST回退和告警 | 回退策略执行+告警触发 |
| ECC计数验证 | memtest产生CE→验证EDAC/BIOS/BMC计数一致 | 三路径计数偏差<2% |
| Patrol Scrub验证 | 长时间运行→验证全地址空间被扫描 | 24小时内全地址覆盖 |
| CPU MCA注入 | 使用故障注入工具产生MCA事件→验证上报 | BIOS/BMC/OS三层捕获 |
| DIMM定位精度 | 随机选择DIMM模拟故障→验证定位 | 定位到具体槽位准确率100% |
| 温度压力测试 | 升温环境→验证DDR5 FGR自适应 | 85°C时刷新率≥正常2× |
| POST失败恢复 | 损坏SPD→验证启动 | 自动回退→降级→告警 |

---

## 参考文献

### 内部知识库

- [可服务性需求规格说明书 §1.1-1.2](2026-07-30-server-serviceability-specification.md#11-cpu与散热模组) — CPU/DIMM可服务性基础规格
- [处理器调试能力演进](../../02_rd/01_product/00_hardware/01_hw-core/2026-07-02-processor-debug-capabilities.md) — CPU调试能力全景
- [调试系统设计-BIOS调试方案](../../02_rd/01_product/01_software/2026-07-21-debug-system-design.md#3-biosuefi-调试方案) — BIOS调试体系
- [BMC诊断能力深度规格](2026-07-30-bmc-diagnostic-capabilities-deep-dive.md) — BMC诊断协同

### 行业标准

- [1] Intel: "Intel 64 and IA-32 Architectures Software Developer's Manual — Vol.3B: Machine-Check Architecture"
- [2] AMD: "AMD64 Architecture Programmer's Manual — Vol.2: System Programming, MCA"
- [3] JEDEC: "JESD79-5 DDR5 SDRAM Standard" — DDR5 RAS features
- [4] JEDEC: "JESD401-5 DDR5 SPD Specification" — 内存RAS数据
- [5] Intel: "BIOS Implementation Test Suite (BITS)" — BIOS测试方法
- [6] UEFI Forum: "UEFI Specification — Chapter 35: RAS Features"
- [7] SMBIOS: "DMTF SMBIOS Reference Specification v3.7" — Type 32 System Event Log

---

## 变更记录

| 日期 | 版本 | 变更说明 |
|:-----|:----:|:---------|
| 2026-07-30 | v1.0 | 首次创建，覆盖6章88条BIOS CPU/内存诊断规格 |
