# 🏗️ 芯片初始化与故障恢复体系：CPU / PCIe Switch / USB / SSD主控 / GPU

> **版本**: v1.0 | **创建**: 2026-06-25
> **核心定位**: 从芯片供电→固件加载→链路训练→监控初始化→异常检测→多层次恢复的**全链路原理级分析**，揭示五类芯片在初始化流程和恢复机制上的共性模式与差异化设计
>
> **关联文档**:
> - [🛡️ RAS 综合设计手册](../07_ras/ras-comprehensive-handbook.md)（RAS 理论基础）
> - [🔌 PCIe 5.0 & 6.0 协议栈深度分析](../../04_fullstack/pcie-protocol-stack-deep-analysis.md)（LTSSM / AER / DPC）
> - [🔌 SerDes 能力全景分析](serdes-comprehensive-analysis.md)（PHY 初始化与均衡）
> - [🛠️ 超节点可维护性与可观测性设计](supernode-maintainability-observability-design.md)（固件管理）
> - [⚡ DMA & RDMA 深度分析](../../04_fullstack/dma-rdma-complete-analysis.md)
> - [📡 信号质量分析体系](signal-integrity-analysis.md)
> - [🎯 地址转换体系](address-translation-supernode.md)
>
> **适用对象**: 芯片固件工程师 · BIOS/BMC 工程师 · 系统架构师 · 可靠性工程师

---

## 📑 目录

- [第1章 总论：芯片初始化的共性框架与恢复层次](#第1章-总论芯片初始化的共性框架与恢复层次)
  - [1.1 芯片初始化的五个层次](#11-芯片初始化的五个层次)
  - [1.2 故障恢复的四级模型](#12-故障恢复的四级模型)
  - [1.3 电源域与复位层次的芯片设计原理](#13-电源域与复位层次的芯片设计原理)
  - [1.4 固件加载与安全启动的共性架构](#14-固件加载与安全启动的共性架构)
  - [1.5 监控子系统的共性构成](#15-监控子系统的共性构成)
- [第2章 CPU 初始化与故障恢复](#第2章-cpu-初始化与故障恢复)
  - [2.1 CPU 供电初始化原理](#21-cpu-供电初始化原理)
  - [2.2 固件启动流程：从 Reset Vector 到 UEFI](#22-固件启动流程从-reset-vector-到-uefi)
  - [2.3 内存子系统初始化（Memory Training）](#23-内存子系统初始化memory-training)
  - [2.4 PCIe 总线初始化与枚举](#24-pcie-总线初始化与枚举)
  - [2.5 监控子系统：PECI / MCA / CMCI](#25-监控子系统peci--mca--cmci)
  - [2.6 CPU 异常检测与故障恢复](#26-cpu-异常检测与故障恢复)
- [第3章 PCIe Switch 初始化与故障恢复](#第3章-pcie-switch-初始化与故障恢复)
  - [3.1 供电与时钟域](#31-供电与时钟域)
  - [3.2 固件初始化与配置空间填充](#32-固件初始化与配置空间填充)
  - [3.3 链路初始化：LTSSM 全流程](#33-链路初始化ltssm-全流程)
  - [3.4 监控子系统：per-port 错误计数与温度](#34-监控子系统per-port-错误计数与温度)
  - [3.5 PCIe Switch 故障恢复](#35-pcie-switch-故障恢复)
- [第4章 USB 控制器初始化与故障恢复](#第4章-usb-控制器初始化与故障恢复)
  - [4.1 供电与时钟](#41-供电与时钟)
  - [4.2 固件初始化](#42-固件初始化)
  - [4.3 USB PHY 初始化与校准](#43-usb-phy-初始化与校准)
  - [4.4 链路训练与枚举：USB 2.0 / 3.x / USB4](#44-链路训练与枚举usb-20--3x--usb4)
  - [4.5 USB 异常检测与恢复](#45-usb-异常检测与恢复)
- [第5章 SSD 主控初始化与故障恢复](#第5章-ssd-主控初始化与故障恢复)
  - [5.1 供电与上电时序](#51-供电与上电时序)
  - [5.2 Boot ROM → 固件加载：从 NAND 到 SRAM 的原理](#52-boot-rom--固件加载从-nand-到-sram-的原理)
  - [5.3 NAND 通道初始化与介质探测](#53-nand-通道初始化与介质探测)
  - [5.4 FTL（闪存转换层）初始化与重建](#54-ftl闪存转换层初始化与重建)
  - [5.5 PCIe EP 链路初始化](#55-pcie-ep-链路初始化)
  - [5.6 NVMe 控制器初始化](#56-nvme-控制器初始化)
  - [5.7 监控子系统：SMART / Thermal / Power Loss](#57-监控子系统smart--thermal--power-loss)
  - [5.8 SSD 异常检测与恢复](#58-ssd-异常检测与恢复)
- [第6章 GPU 初始化与故障恢复](#第6章-gpu-初始化与故障恢复)
  - [6.1 GPU 供电与上电时序](#61-gpu-供电与上电时序)
  - [6.2 VBIOS / GPU 固件初始化](#62-vbios--gpu-固件初始化)
  - [6.3 显存初始化（HBM / GDDR 训练）](#63-显存初始化hbm--gddr-训练)
  - [6.4 PCIe 链路初始化](#64-pcie-链路初始化)
  - [6.5 计算子系统初始化](#65-计算子系统初始化)
  - [6.6 监控子系统：温度 / 电压 / 功耗 / ECC](#66-监控子系统温度--电压--功耗--ecc)
  - [6.7 GPU 异常检测与恢复](#67-gpu-异常检测与恢复)
- [第7章 跨芯片协同与系统级恢复](#第7章-跨芯片协同与系统级恢复)
  - [7.1 整机上电时序：CPU→BMC→PCIe→GPU 的依赖链](#71-整机上电时序cpubmcpciegpu-的依赖链)
  - [7.2 故障传播路径与隔离策略](#72-故障传播路径与隔离策略)
  - [7.3 系统级恢复方案：从链路重训到整机复位](#73-系统级恢复方案从链路重训到整机复位)
  - [7.4 恢复决策树](#74-恢复决策树)
- [附录A：各芯片初始化关键时序参数表](#附录a各芯片初始化关键时序参数表)
- [附录B：固件加载对比表](#附录b固件加载对比表)
- [附录C：关键术语表](#附录c关键术语表)

---

## 第1章 总论：芯片初始化的共性框架与恢复层次

### 1.1 芯片初始化的五个层次

所有芯片（CPU / PCIe Switch / USB / SSD / GPU）的初始化都可以分解为以下五个层次，每层有明确的输入条件和输出产物：

```text
层次 1: 供电与复位 (Power & Reset)
  ┌──────────────────────────────────────────────────┐
  │ 输入: 主电源 (12V/3.3V/1.8V), 时钟源              │
  │ 动作: 各电源轨依序上电 → PLL 锁定 → 复位信号释放   │
  │ 输出: 芯片内部时钟稳定, 复位撤销, 开始取指          │
  │ 共性: 所有芯片必备, 时序依赖最严格                 │
  └──────────────────────────────────────────────────┘
                 ▼
层次 2: 固件加载 (Firmware Loading)
  ┌──────────────────────────────────────────────────┐
  │ 输入: 稳定的供电 + 时钟 + 复位释放                │
  │ 动作: Boot ROM 执行 → 加载固件到 SRAM/DRAM        │
  │ 输出: 固件开始执行 (主控程序/调度器入口)           │
  │ 差异: 固件存储介质不同 (Flash/ROM/NAND/SPI)       │
  └──────────────────────────────────────────────────┘
                 ▼
层次 3: 内部子系统初始化
  ┌──────────────────────────────────────────────────┐
  │ CPU: 内存训练, Cache 初始化                       │
  │ PCIe Sw: 端口配置, 路由表初始化                   │
  │ USB: PHY 校准, 控制器配置                         │
  │ SSD: NAND 通道检测, FTL 加载                      │
  │ GPU: HBM/GDDR 训练, SM 初始化                     │
  │ 共性: 都需要校准内部模拟电路 (ADC/DAC/PLL/DLL)    │
  └──────────────────────────────────────────────────┘
                 ▼
层次 4: 外部接口初始化 (Link Bring-up)
  ┌──────────────────────────────────────────────────┐
  │ PCIe: LTSSM 训练 (速率/宽度/EQ 协商)             │
  │ USB: LFPS 握手, 速率协商                          │
  │ SSD: NVMe 控制器就绪, PCIe EP 训练               │
  │ GPU: PCIe + NVLink/HCCS 训练                     │
  │ 共性: 与对端芯片双向交互, 包含训练/协商阶段        │
  └──────────────────────────────────────────────────┘
                 ▼
层次 5: 监控子系统初始化
  ┌──────────────────────────────────────────────────┐
  │ 温度传感器校准, 电压监视阈值设置                   │
  │ ECC/CRC 计数器清零, 告警使能                      │
  │ 看门狗配置, 故障注入接口初始化                     │
  │ 与 BMC/管理控制器握手 (IPMI/Redfish/MCTP)         │
  └──────────────────────────────────────────────────┘
```

### 1.2 故障恢复的四级模型

故障恢复的粒度决定了系统的可用性。所有芯片的恢复机制都可以映射到以下四级模型：

```text
                    恢复范围与影响
                    ──────────────
Level 1: 单链路恢复 (Single Link Recovery)
  ├─ 范围: 一个物理链路 (PCIe Lane, USB Port, NVLink Sub-Lane)
  ├─ 动作: 链路重训练 / 速率降级 / Lane 替换
  ├─ 影响: 该链路瞬时中断 (~ms 级)
  ├─ 适合: 瞬时性错误 (CRC 突发, 信号噪声, 电源毛刺)
  └─ 举例: PCIe Recovery 状态, USB 端口复位, NVLink 链路重训

Level 2: 业务/功能级恢复 (Functional Recovery)
  ├─ 范围: 一个功能单元 (PCIe Function, USB 设备, NVMe Queue)
  ├─ 动作: Function-Level Reset (FLR), 队列重置, 设备复位
  ├─ 影响: 该功能单元不可用 (~ms~s 级)
  ├─ 适合: 功能卡死但芯片其他部分正常
  └─ 举例: GPU FLR, NVMe Controller Reset, PCIe DPC

Level 3: 局部芯片恢复 (Partial Chip Recovery)
  ├─ 范围: 芯片的一个子域 (GPU GPC, CPU Core, SSD Channel)
  ├─ 动作: 子域电源关断重启 / 固件子模块热加载
  ├─ 影响: 该子域不可用 (~s 级), 芯片其他部分继续工作
  ├─ 适合: 硬错误但可隔离 (永久性故障)
  └─ 举例: CPU Core Offline, GPU GPC 隔离, SSD Bad Block

Level 4: 全芯片恢复 (Full Chip Recovery)
  ├─ 范围: 整颗芯片
  ├─ 动作: Warm Reset → Firmware Reload → 全初始化
  ├─ 影响: 芯片完全不可用 (~s~10s 级)
  ├─ 适合: 固件崩溃, 电源异常, 不可恢复错误
  └─ 举例: PCIe Secondary Bus Reset, Warm Reboot, POR
```

### 1.3 电源域与复位层次的芯片设计原理

#### 1.3.1 电源域划分的芯片设计原则

现代芯片的内部供电远不止一根电源线——它们被划分为多个**电源域 (Power Domain)**，每个域有独立的电压、上电时序和关断控制。

```text
芯片电源域的典型划分:

                              芯片封装
┌──────────────────────────────────────────────────────┐
│  ┌──────────Vcore(0.7-0.9V)───────────────────────┐ │
│  │  V域1: 数字核心 (Core Logic)                     │ │
│  │  · CPU Core / GPU SM / SSD CPU                 │ │
│  │  · 最高功耗, 最大电流 (~100-500A)               │ │
│  │  · 需要 VR 精确稳压 ±1%                         │ │
│  └──────────────────────────────────────────────────┘ │
│  ┌──────────Vdd_io(1.0-1.8V)──────────────────────┐ │
│  │  V域2: I/O 接口                                 │ │
│  │  · SerDes PHY (1.0V/0.9V)                      │ │
│  │  · DDR/HBM PHY (1.1V/1.8V)                     │ │
│  │  · 通用 GPIO (1.8V/3.3V)                        │ │
│  │  · 快速上电要求, 大摆幅驱动                      │ │
│  └──────────────────────────────────────────────────┘ │
│  ┌──────────Vdd_aux(0.9-3.3V)─────────────────────┐ │
│  │  V域3: 常开域 (Always-On / Standby)             │ │
│  │  · 唤醒逻辑, RTC, 安全引擎                       │ │
│  │  · 主域断电时仍需供电                            │ │
│  │  · 超低功耗, 微漏电设计                          │ │
│  └──────────────────────────────────────────────────┘ │
│  ┌──────────Vdd_pll(0.9-1.0V)─────────────────────┐ │
│  │  V域4: 模拟 PLL / CDR                          │ │
│  │  · 对电源噪声最敏感                             │ │
│  │  · 独立 LDO 去耦                                │ │
│  │  · 锁定后才能释放其他域的复位                     │ │
│  └──────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘

电源域设计的关键原则:
  1. 噪声隔离: 模拟域 (PLL/VCO) 必须与数字域 (Core) 物理隔离
  2. 电压独立: 不同工艺要求的电压 (1.8V I/O vs 0.7V Core) 必须分离
  3. 功耗管理: 每个域可独立关断 → 实现细粒度功耗门控
  4. 上电顺序: 必须按域逐级上电, 防止闩锁 (Latch-Up)
```

#### 1.3.2 复位层次

与电源域对应，复位也有严格的层次结构：

```text
芯片内部复位层次:

POR (Power-On Reset) ── 最底层
  ├─ 由 Power Good 信号触发
  ├─ 复位所有寄存器到默认态
  ├─ 初始化 PLL 和时钟树
  └─ 有些芯片是内置 POR 电路, 有些需要外部 POR 信号

Cold Reset (硬复位)
  ├─ 由 POR# 引脚触发 (主板拉低)
  ├─ 复位所有状态, 重新加载固件
  ├─ 但不切断电源 (保留 DRAM 内容)
  └─ 比 POR 快 (PLL 不需要重新锁定)

Warm Reset (软复位)
  ├─ 由软件写入复位寄存器触发
  ├─ 复位数字逻辑但不影响 PLL/PHY
  ├─ 保留部分寄存器配置
  └─ 最快, ~μs-ms 级

Function Reset (功能复位)
  ├─ 仅复位某个功能单元
  ├─ PCIe FLR: 复位特定 Function 的配置空间
  ├─ GPU GPC Reset: 复位单个 GPC
  ├─ SSD Queue Reset: 复位某个 NVMe Queue
  └─ 不影响其他功能单元

Sub-domain Reset (子域复位)
  ├─ 复位电源域内的某个子模块
  ├─ 最细粒度
  ├─ 由固件或硬件 FSM 控制
  └─ 例如: 复位单个 SerDes Lane
```

### 1.4 固件加载与安全启动的共性架构

所有芯片的固件加载遵循相似的模式，差异在于存储介质、安全校验粒度和加载路径：

```text
固件加载的共性架构:

┌────────────────────────────────────────────────────────────┐
│  Step 1: Boot ROM (芯片内部掩膜 ROM)                        │
│  ├─ 芯片出厂时固化, 不可更改                               │
│  ├─ 最基本的初始化: 时钟、Stack Pointer、Watchdog           │
│  ├─ 读取 Boot Device (SPI Flash / NAND / eMMC / I2C)      │
│  └─ 加载 Primary Bootloader 到内部 SRAM                    │
│                                                            │
│  Step 2: Primary Bootloader (PBL / L0/L1)                  │
│  ├─ 初始化 DRAM 控制器 (如果需要 >SRAM 容量的固件)          │
│  ├─ 验证 Secondary Bootloader 的签名 (Security)            │
│  ├─ 初始化基本的外设 (SPI / I2C / UART for debug)          │
│  └─ 加载 Secondary Bootloader 到 DRAM                      │
│                                                            │
│  Step 3: Secondary Bootloader (L2/L3 / UEFI)               │
│  ├─ 完整的运行时初始化                                     │
│  ├─ 加载芯片固件 (Microcode / Firmware Image)              │
│  ├─ 加载厂商配置 (Calibration Data / OTP)                  │
│  └─ 跳转到主固件入口                                       │
│                                                            │
│  Step 4: Main Firmware / Runtime                            │
│  ├─ 芯片全功能初始化                                       │
│  ├─ 启动调度器 / 任务管理器                                │
│  ├─ 建立通信通道 (PCIe / USB / NVMe Admin Queue)           │
│  └─ 进入正常操作模式                                        │
└────────────────────────────────────────────────────────────┘

安全启动 (Secure Boot) 链:
  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
  │ Boot ROM │ →→→ │ PBL sig │ →→→ │ SBL sig  │ →→→ │ Firmware │
  │ (可信根)  │     │ 验证     │     │ 验证      │     │ 加载     │
  └──────────┘     └──────────┘     └──────────┘     └──────────┘
                        ↑                ↑                ↑
                   Root Public Key  Key Hash in OTP   FW Signature
                   (fused in OTP)   (硬件保护不可改)   (ECDSA/RSA)

  信任链: 每一级在加载下一级之前, 先验证其数字签名
  如果任何一级验证失败 → 停止启动, 进入 Recovery Mode
```

### 1.5 监控子系统的共性构成

芯片的监控子系统负责检测异常情况，触发告警或恢复动作：

```text
芯片监控子系统的共性构成:

┌─────────────────────────────────────────────────────────────┐
│  传感器层 (Sensor Layer)                                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │ 温度     │ │ 电压     │ │ 电流     │ │ 错误计数器    │   │
│  │ Sensor  │ │ Monitor  │ │ Monitor  │ │ (ECC/CRC/FEC)│   │
│  │ (TSMC)  │ │ (VMON)   │ │ (IMON)   │ │              │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘   │
│       │            │            │              │           │
│  ┌────┴────────────┴────────────┴──────────────┴───────┐   │
│  │  阈值比较 / 滤波 / 去抖                               │   │
│  │  · 温度超过 Tj_max → 降频/关机                        │   │
│  │  · ECC 计数超过阈值 → 告警                            │   │
│  │  · CRC 突发错误 → 链路重训                            │   │
│  └─────────────────────────┬───────────────────────────┘   │
│                            ▼                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  告警与动作层 (Alert & Action Layer)                  │   │
│  │  · Error Interrupt → 中断处理器                       │   │
│  │  · SMI/SERR → 系统管理中断                           │   │
│  │  · GPIO toggle → 通知 BMC                            │   │
│  │  · MCA → Machine Check Architecture (CPU)            │   │
│  │  · XID → NVIDIA GPU Error Log                        │   │
│  │  · SMART → SSD Self-Monitoring                       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 第2章 CPU 初始化与故障恢复

### 2.1 CPU 供电初始化原理

#### 2.1.1 CPU 供电架构

Modern CPU 的供电是服务器主板设计中最复杂、最严格的部分：

```text
CPU 供电链:

服务器 PSU (12V)
       │
       ▼
┌──────────────────────────────┐
│  VR (Voltage Regulator)      │
│  Multi-Phase Buck Converter  │
│  ┌──────┐ ┌──────┐ ┌──────┐ │
│  │Phase1│ │Phase2│ │PhaseN│ │  ← 6-16 相
│  └──┬───┘ └──┬───┘ └──┬───┘ │
│     │        │        │     │
│     └────────┴────────┴─────┘ │
│           Vout (0.6-1.5V)     │
└──────────────┬────────────────┘
               │
               ▼
┌──────────────────────────────┐
│  CPU Socket / Package         │
│  ┌──────────────────────────┐│
│  │  Vcore: Core Logic       ││  ← 最大电流 ~300-500A
│  │  VccSA: System Agent     ││     1.0V
│  │  VccIO: I/O              ││     1.0-1.2V
│  │  VccGT: Graphics (if)    ││     0.8-1.2V
│  │  Vddq: DDR5 PHY          ││     1.1V
│  │  Vpp: DDR5 VPP           ││     1.8V
│  │  Vaux: Standby           ││     1.8V/3.3V (always-on)
│  └──────────────────────────┘│
└──────────────────────────────┘
```

#### 2.1.2 CPU 上电时序原理

CPU 对供电时序有极其严格的要求，违反时序可能导致芯片损坏：

```text
Intel Xeon CPU 上电时序 (VR 输出必须满足 T1 < T2 < T3 ...):

VR_EN 信号 (由 BMC/BIC 控制)
  │
  ├─ T0: Vccin (1.8V) → Core 供电准备好
  │    └─ Power Good 反馈 → 允许下一域
  │
  ├─ T1: Vcore → 核心逻辑供电
  │    └─ VCC_SENSE 反馈
  │
  ├─ T2: VccSA / VccIO → 内存控制器 + I/O
  │    └─ VR_PG (Power Good 信号)
  │
  ├─ T3: Vddq / Vpp → DDR5 PHY 供电
  │    └─ DDR_PG
  │
  ├─ T4: Vaux → Standby 域
  │
  ├─ T5: PCH 发出 PLTRST# (复位释放)
  │    └─ CPU 开始执行第一条指令 (Reset Vector)
  │
  └─ T6: CPU 自身 PLL 锁定 → 内部时钟稳定
       └─ 全部供电正常 → 开始固件加载

时序约束:
  T1-T5: 总时序差 < 100ms (Intel VR 规范)
  相邻两个电源轨延时: >1ms (防止同时上电冲击)
  PLL 锁定时间: ~50-200μs (取决于 PLL 类型)
```

**芯片设计原理**: 为什么需要如此严格的时序？

```text
核心原因: 闩锁效应 (Latch-Up) 预防

  CMOS 芯片内部有寄生 PNPN 结构 (SCR):
    VDD ─┬─ P+ ── Nwell ── Psub ── N+ ── GND
         │    │              │
         │   P+/Nwell      N+/Psub
         │   (寄生 BJT)    (寄生 BJT)
         └──────────────────────┘
           SCR 晶体管 (可控硅结构)

  正常情况: SCR 是阻断的
  闩锁情况: 如果某域上电时 I/O 引脚已有电压（其他域先上电）
             → SCR 被触发导通
             → 形成 VDD→GND 的低阻通路
             → 大电流烧毁芯片

  预防措施:
    1. 严格的上电顺序: I/O 域必须在 Core 域之前或同时上电
    2. ESD 钳位二极管: 反向偏置防止电流倒灌
    3. Power Rail Sequencing: 硬件定时器确保够大延时
```

### 2.2 固件启动流程：从 Reset Vector 到 UEFI

#### 2.2.1 CPU 复位后第一条指令

```text
CPU 复位后, 硬件自动完成的动作:

1. Reset Vector:
   ┌──────────────────────────────────────────────┐
   │  复位释放后, CPU Core 执行以下硬件操作:        │
   │  1. CS:IP = F000:FFF0 (x86 实模式)            │
   │     或 0xFFFF_FFF0 (x86 保护模式)              │
   │  2. 读第一条指令 → 通常是一条 JMP 指令         │
   │  3. JMP 到 BIOS/UEFI 基地址 (通常是 SPI Flash) │
   └──────────────────────────────────────────────┘

2. BIOS/UEFI 启动流程 (x86 服务器):

   ┌────────────────────────────────────────────────────┐
   │  SEC (Security Phase)                               │
   │  · 第一条指令入口                                  │
   │  · 建立临时内存 (Cache-as-RAM, CAR)                │
   │  · 初始化栈指针 (SS:SP)                            │
   │  · 验证下一阶段 (PEI) 签名 → 安全启动链开始        │
   │  · 设置早期异常处理向量                             │
   ├────────────────────────────────────────────────────┤
   │  PEI (Pre-EFI Initialization)                      │
   │  · 初始化早期平台硬件 (CPU msr, Chipset, PCH)      │
   │  · 处理器微代码 (Microcode Patch) 加载             │
   │  · 内存控制器初始化 → 内存训练 (Memory Training)   │
   │  · 找到 PEI 模块后, 加载 DXE IPL                   │
   ├────────────────────────────────────────────────────┤
   │  DXE (Driver Execution Environment)                │
   │  · 全部内存可用 → 加载各种 UEFI Driver             │
   │  · PCIe 总线枚举 + 配置空间分配                    │
   │  · ACPI 表构造 / SMBIOS 填充                       │
   │  · Setup Menu 显示 (如果按 Del/F2 进设置)          │
   ├────────────────────────────────────────────────────┤
   │  BDS (Boot Device Selection)                       │
   │  · 扫描引导设备顺序 (HDD/NVMe/USB/PXE)            │
   │  · 加载引导加载器 (bootx64.efi / grub)            │
   │  · ExitBootServices() → 移交控制权给 OS            │
   ├────────────────────────────────────────────────────┤
   │  OS 启动后                                        │
   │  · CPU Driver 接管 (Linux: acpi_cpufreq / intel_pstate)│
   │  · ACPI 表解析 → 电源管理 / 中断路由               │
   │  · MCA 注册 → Machine Check 错误处理初始化         │
   │  · SMM 初始化 (System Management Mode)            │
   └────────────────────────────────────────────────────┘
```

#### 2.2.2 微代码 (Microcode) 加载原理

```text
CPU Microcode Patch 加载机制:

CPU 出厂时内置微代码 ROM, 但处理器发布后可能发现勘误 (Errata)
→ 需要通过微代码补丁修正

加载流程:
  1. BIOS/UEFI 在 SEC/PEI 阶段
  2. 从 SPI Flash 读取 Microcode Patch (二进制 blob)
  3. 检查 Patch 签名 (RSA 验签, 使用 CPU 内置的公钥)
  4. 通过 WRMSR 指令(IA32_BIOS_SIGN_ID MSR 0x8B)
     将 Patch 加载到 CPU 内部的微代码 RAM
  5. Patch 生效, 替换 ROM 中的微指令序列

关键原理:
  - 微代码 Patch 存储在芯片内部 SRAM (不是修改 ROM)
  - 每次开机必须重新加载 (SRAM 是易失性存储)
  - 不同 Stepping 的 CPU 需要不同的 Patch
  - 更新失败 → CPU 回到 ROM 微代码 (兼容性降级, 不是死机)

验证安全:
  Patch 文件头包含:
  ┌─────────────────────────┐
  │ Header Version           │
  │ Patch Revision (版本号)   │
  │ Date (YYYYMMDD)          │
  │ Processor Signature      │ ← 匹配 CPU ID
  │ Checksum (CRC32)         │
  │ Loader Revision          │
  │ Processor Flags          │
  │ Data Size                │
  │ Total Size               │
  │ RSA 256-bit Signature    │ ← CPU 内置公钥验证
  └─────────────────────────┘
```

#### 2.2.3 Cache-As-RAM (CAR) 原理

PEI 阶段的一个关键设计：在内存初始化之前如何运行 C 代码？

```text
问题: UEFI PEI 阶段需要运行 C 代码 (需要 Stack + Heap)
      但此时 DDR5 内存尚未初始化 (Memory Training 还没做)
      怎么办?

答案: Cache-As-RAM (CAR)
  利用 CPU 内部的 L2/L3 Cache 的 SRAM 作为临时内存

原理:
  1. CPU 初始化时, L2/L3 Cache 的 SRAM 已经可用 (内置在CPU中)
  2. 设置 MTRR (Memory Type Range Register):
     - 将某个地址区域标记为 "Write-Back" 缓存类型
  3. 写入该地址 → 数据存储在 Cache Line 中 (不在 DRAM, 因为没有)
  4. 读取该地址 → 从 Cache Line 中读取
  5. 效果: Cache 被当作 SRAM 使用

  但有限制:
  - CAR 大小受限于 L2/L3 Cache 大小 (通常 256KB-2MB)
  - 不能运行复杂代码 (栈溢出 = 死机)
  - 内存训练完成后, 必须将 CAR 内容迁移到真正的 DRAM
  - 迁移完成前, 所有中断必须屏蔽

深度理解:
  为什么 Cache 在没有 DRAM 的时候可以工作?
  → Cache 本身是 SRAM (静态随机存取存储器), 独立于 DRAM
  → Cache Controller 在 CPU 内部, 不需要 DRAM 来操作
  → 设置 MTRR 后, CPU 对指定地址的访问直接被 Cache Controller 接管
  → 所以: 在没有 DRAM 的情况下, Cache 就是 CPU 的"内存"
```

### 2.3 内存子系统初始化（Memory Training）

这是 UEFI PEI 阶段最耗时、最复杂的初始化步骤。

#### 2.3.1 DDR5 内存初始化的层次

```text
内存训练不是"插上就能用", 而是主板 + CPU + DIMM 三方配合的精密校准:

┌─────────────────────────────────────────────────────────────┐
│  Level 1: SPD (Serial Presence Detect) 读取                 │
│  ├─ CPU/内存控制器通过 I2C (SMBus) 读取 DIMM 上的 SPD ROM  │
│  ├─ SPD 包含: DRAM 时序参数 (CL/tRCD/tRP/tRAS/tRFC...)    │
│  ├─ 容量 × 等级 (Rank) × 组织 (x4/x8)                      │
│  ├─ 制造商信息, 工作温度范围                                 │
│  └─ BIOS 读取后确定: DIMM 类型, 是否匹配, 时序基线          │
│                                                             │
│  Level 2: DRAM Init Sequence                                │
│  ├─ RESET# 释放 (复位)                                      │
│  ├─ CKE (Clock Enable) → 使能时钟                          │
│  ├─ ZQ Cal (阻抗校准) → 校准 ODT/DQ 驱动强度               │
│  └─ MRS (Mode Register Set) → 配置工作模式 (Burst Length等)│
│                                                             │
│  Level 3: Training (校准)                                    │
│  ├─ Write Leveling → 补偿 DQS 与 CK 的相位差               │
│  ├─ Read DQS Training → 找到 DQS 的采样窗口                 │
│  ├─ DQ/DQS 延时校准 → 精确调整每根数据线延时               │
│  ├─ CA (Command/Address) Training → 命令/地址总线校准       │
│  ├─ ODT (On-Die Termination) Training → 校准终端电阻        │
│  └─ Vref (参考电压) Training → DQ/DQS 参考电压优化         │
│                                                             │
│  Level 4: Verification (验证)                                │
│  ├─ 写入已知模式 → 读取验证                                 │
│  ├─ 多温度点校准 (最耗时间)                                 │
│  ├─ Margin 测试 → 确定每个 bit 的建立/保持时间裕量          │
│  └─ 如果 Margin 不足 → 调整 Phase Interpolator 或 Vref     │
└─────────────────────────────────────────────────────────────┘
```

#### 2.3.2 Write Leveling 的物理原理

```text
问题: DDR5 时钟 (CK) 与数据选通 (DQS) 在 PCB 走线长度不同

  CPU/内存控制器 →→→→ CK 走线 →→→→ DIMM
                →→→→ DQS 走线 →→→→ DIMM
  
  CK 和 DQS 到达 DIMM 的时间不同 (由于走线长度差)
  → DIMM 不知道何时应该用 DQS"捕获"控制器发来的数据

解决方案: Write Leveling
  1. 控制器在 CK 的上升沿附近发出 DQS "脉冲" (连续的 DQS 信号)
  2. DIMM 将收到的 DQS 与自己收到的 CK 比较
  3. DIMM 反馈相位差: "DQS 比 CK 快/慢了 XXX ps"
  4. 控制器调整 DQS 的延时, 直到 DQS 的上升沿与 CK 的上升沿对齐
  5. 每次调整步进: ~5-20ps (取决于 PLL Phase Interpolator 精度)

芯片设计实现:
  · 每个 DDR5 通道的每个 Rank 独立进行 Write Leveling
  · 需要 DDR5 PHY 内的 Phase Interpolator (精度 < 1/256 UI)
  · 在一个 8 通道的 CPU 上: 8×2Rank = 16 次 Write Leveling
  · 总耗时: ~10-50ms (取决于步进数量和频率)
```

#### 2.3.3 DDR5 内存训练失败的处理

```text
内存训练失败 (无法完成 Level 3) → 恢复方案:

Level 1 恢复: 降速
  如果设定 4800 MT/s 训练失败 → 降到 4400 MT/s → 再降到 4000 MT/s
  原理: 更低速率 = 更大的时序裕量
  成功概率: 高 (大多数是 PCB SI 问题)
  耗时: +30-60s (每次降速包含完整的 Training)

Level 2 恢复: 关闭部分通道
  如果 8 通道中有 1-2 个通道训练失败
  → 关闭失败的通道, 用剩余通道启动
  → BIOS 通过 Memory Map 隐藏失败的通道
  代价: 带宽下降 25-50%

Level 3 恢复: 替换备用 Row/Bank
  DDR5 内置行修复:
  · MBIST 发现 bad cell → 触发 Post-Package Repair
  · 硬件自动用备用 Row 替换
  · 对操作系统透明

Level 4 恢复: Retry
  如果温度变化 → 重训 (Re-training)
  BIOS 选项: "Memory Retrain on Temperature Change"
```

### 2.4 PCIe 总线初始化与枚举

CPU 作为 Root Complex，负责整个 PCIe 拓扑的枚举和配置空间分配。

#### 2.4.1 PCIe 枚举原理

```text
UEFI DXE 阶段: PCIe 总线枚举

Enumeration 本质上是一个"深度优先搜索"的递归过程:

┌─────────────────────────────────────────────────────────────┐
│  Step 1: Root Port 探测                                    │
│  ┌─ CPU Root Port #0 → 读 Vendor/Device ID                 │
│  │  有设备 → 分配 Bus Number                               │
│  │  无设备 → 标记为空端口, 跳过                             │
│  │                                                          │
│  Step 2: 配置空间扫描                                       │
│  ├─ 读 Bus 0 下所有 Device/Function                        │
│  ├─ 发现 Type 1 Header (PCIe-PCIe Bridge) → 递归进入下级 Bus│
│  ├─ 发现 Type 0 Header (Endpoint) → 分配 BAR 资源           │
│  └─ 递归直到所有设备枚举完成                                 │
│                                                          │
│  Step 3: 资源分配                                          │
│  ├─ Memory Base/Limit: 为每个桥分配 Memory 窗口             │
│  ├─ BAR 分配: 写全1 → 读回 → 确定 BAR 大小                 │
│  ├─ 64-bit BAR: 0xFFFFFFF_FFFFFFFF → 读高32位              │
│  └─ 中断路由: INTx → IRQ 映射                              │
│                                                          │
│  Step 4: 链路训练触发                                      │
│  └─ 配置完配置空间后, 各 Endpoint 开始 LTSSM 训练           │
│     · Root Port 发送 TS1/TS2 训练序列                       │
│     · Endpoint 响应 → 协商速率/宽度                         │
│     · PHY EQ Phase 1-4 → 确定均衡系数                      │
└─────────────────────────────────────────────────────────────┘

枚举中的关键硬件/固件交互:
  1. BIOS 写配置空间寄存器 → 硬件(PCIe Controller)处理
  2. 硬件返回 "Configuration Retry Status (CRS)" = 等待中
  3. BIOS 轮询直到不再返回 CRS
  4. 超时: 如果设备 1s 内不响应 → 标记为 "device not found"
```

#### 2.4.2 资源分配中的 BAR 冲突处理

```text
BAR (Base Address Register) 分配: 写全1检测大小的原理

例子: 一个 1MB 的 BAR
  1. BIOS 写入 0xFFFF_FFFF 到 BAR
  2. 硬件检查 BAR 地址位的实现宽度:
     - 1MB BAR → 低 20 位是实现的 (2^20 = 1MB)
     - 写入 0xFFFF_FFFF → 低 20 位被丢弃 (硬件忽略)
     - 读回: 0xFFF0_0000 (高 12 位全1, 低 20 位为 0)
  3. BIOS 计算: 从读回的最低 1 位置开始, 向上找第一个 0
     0xFFF0_0000 = 1111_1111_1111_0000_0000_0000_0000_0000
     → 第一个 0 在第 20 位 (bit 20)
     → BAR 大小 = 2^20 = 1MB
  
  如果 BAR 冲突 (两个设备需要重叠的地址空间):
  → BIOS 尝试重新分配 (移动 BAR 到不冲突的位置)
  → 如果无法解决: 禁用冲突设备或报错
```

### 2.5 监控子系统：PECI / MCA / CMCI

#### 2.5.1 PECI (Platform Environment Control Interface)

```text
PECI 是 Intel CPU 与 BMC 之间通信的专用接口:

┌────────────┐        PECI (单线)       ┌────────────┐
│  BMC       │ ◄──────────────────────► │  CPU       │
│  (PECI 主) │                          │  (PECI 从) │
└────────────┘                          └────────────┘

PECI 能做什么?
  · 读 CPU 温度 (各 Core 温度, Package 温度)
  · 读 CPU 功率 (Package Power, Core Power)
  · 调整 CPU 频率/电压 (通过 MSR 接口)
  · 错误日志读取 (MCA bank)
  · CPU 复位控制
  
原理:
  PECI 是单线双向通信 (类似 I2C 的简化版)
  数据率: ~2 Mbps
  物理层: 开漏, 需上拉
  协议: 主机发起, 从机应答
  · BMC 周期轮询 CPU 温度 (~100ms 间隔)
  · 主动告警: CPU 也可以主动通知 BMC (通过热中断信号)
```

#### 2.5.2 MCA (Machine Check Architecture)

MCA 是 CPU 检测硬件错误的最高级别机制：

```text
MCA 寄存器架构:

┌──────────────────────────────────────────────────────────┐
│  CPU Core #0                    CPU Core #1              │
│  ┌─────────────────────┐       ┌─────────────────────┐   │
│  │ MC Bank 0 (Core)    │       │ MC Bank N (Core)    │   │
│  │ MCG_STATUS MSR      │       │ MCG_STATUS MSR      │   │
│  │ IA32_MCi_CTL MSR    │       │ IA32_MCi_CTL MSR    │   │
│  │ IA32_MCi_STATUS MSR │       │ IA32_MCi_STATUS MSR │   │
│  │ IA32_MCi_ADDR MSR   │       │ IA32_MCi_ADDR MSR   │   │
│  │ IA32_MCi_MISC MSR   │       │ IA32_MCi_MISC MSR   │   │
│  └─────────────────────┘       └─────────────────────┘   │
│                                                            │
│  Uncore (共享)                                             │
│  ┌─────────────────────┐       ┌─────────────────────┐   │
│  │ MC Bank 1 (Cache)  │       │ MC Bank 2 (Memory)  │   │
│  │ ...                 │       │ ...                 │   │
│  └─────────────────────┘       └─────────────────────┘   │
└──────────────────────────────────────────────────────────┘

MCA Bank 类型 (Intel Xeon 6):
  · Bank 0:   Core #0 内部错误
  · Bank 1:   L1/L2 Cache
  · Bank 2:   L3 Cache (LLC)
  · Bank 3-5: 内存控制器通道
  · Bank 6:   PCIe Root Port
  · Bank 7-8: 互联 (UPI/IIO)
  · Bank 9:   Power Control
  · Bank 10+: Integrated Memory Controller (IMC)

错误严重性分类:
  MCA_ERROR_CODE 字段决定恢复策略:
  0x0 = No Error
  0x1 = Uncorrected (Fatal) → 立即触发 Machine Check Exception
  0x2 = Uncorrected (Non-Fatal) → 触发 SMI 或 CMCI
  0x3 = Corrected → 仅计数, 可不处理
  0x4 = Deferred → 可延迟处理
```

#### 2.5.3 CMCI (Corrected Machine Check Interrupt)

```text
CMCI 是 MCA 的"低优先级"扩展:

┌────────────────────────────────────────────────────────────┐
│  传统方式: CPU 轮询 MC Bank → 浪费 CPU 时间               │
│  CMCI: 硬件在 CE 计数超过阈值时触发中断                     │
│                                                              │
│  配置流程:                                                   │
│  1. OS 驱动设置 CMCI 阈值 (IA32_MCi_CTL)                   │
│  2. 当某个 MC Bank 的可修正错误计数 > 阈值                  │
│  3. 硬件触发 CMCI 中断 (APIC 向量)                         │
│  4. OS MCA 驱动读取 MC Bank 状态                           │
│  5. 记录日志 + 重置 CMCI 阈值                               │
│  6. 如果 CE 持续快速增长 → 可能预测到 UE → 主动迁移        │
│                                                              │
│  CMCI vs MCE:                                                │
│  ┌────────────┬──────────────────┬──────────────────────┐  │
│  │            │ CMCI             │ MCE                   │  │
│  ├────────────┼──────────────────┼──────────────────────┤  │
│  │ 触发条件   │ CE > 阈值        │ Uncorrected Error     │  │
│  │ 严重性     │ 警告 (INFO)      │ 致命 (PANIC/Shutdown) │  │
│  │ 恢复       │ 不需要 (硬件已恢复)│ 必须 RMA/Crash Dump  │  │
│  │ 中断优先级 │ 低 (APIC I/O)    │ 最高 (Machine Check)  │  │
│  │ 典型处理   │ 计数 + 日志      │ 操作系统 PANIC       │  │
│  └────────────┴──────────────────┴──────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

### 2.6 CPU 异常检测与故障恢复

#### 2.6.1 CPU 故障类型与检测方法

| 故障类型 | 检测机制 | 严重性 | 典型表现 |
|:---------|:---------|:------|:---------|
| **Cache CE** | MCA Bank 1/2, ECC | 可修正 | CMCI 计数增加 |
| **Cache UE** | MCA MCE (不可修正) | **致命** | Machine Check Exception, 系统 PANIC |
| **内存 CE** | MCA Bank 3-5, DDR5 ECC | 可修正 | CMCI, 内存修复 (若支持) |
| **内存 UE** | MCA MCE | **致命** | 系统 PANIC (除非是 Poisoned Data) |
| **PCIe AER** | MCA Bank 6, AER 寄存器 | 可恢复 | 链路重训练, DPC 隔离 |
| **总线协议错** | BINIT (Bus Initialization) | 不可恢复 | 全局复位 |
| **温度过高** | PECI 热传感器 | 可恢复 | 降频 (Throttling) → 关机 |
| **供电异常** | VR Alert / IMON | 可恢复 | 降频 → 关机 |
| **看门狗超时** | 内部 Watchdog Timer | 可恢复 | CPU 硬复位 |
| **固件崩溃** | BIOS Boot Failure | 可恢复 | 重启 → 恢复模式 |

#### 2.6.2 CPU 恢复机制层级

```text
Level 1: 指令级恢复 (μ-architectural Recovery)
  ┌──────────────────────────────────────────────────────┐
  │ 适用: 瞬时性错误 (glitch, soft error)                 │
  │ 机制: CPU 内部 Replay / Retry                        │
  │ 原理:                                                │
  │  · Load 操作检测到 parity/ECC 错误                   │
  │  · CPU 内部流水线 Replay (从 Load 指令重新执行)       │
  │  · 如果第二次成功 → 无察觉恢复                       │
  │  · 如果第二次失败 → 升级到 MCA                       │
  │ 影响: 完全透明, ~10-100ns 额外延迟                   │
  │                                                      │
  │ Intel: Replay (SVN 检测到错误自动重放)               │
  │ AMD: 类似 Replay + Retry                             │
  │ Arm: 某些实现支持 Replay (如 Neoverse V2)            │
  └──────────────────────────────────────────────────────┘

Level 2: Core 级恢复
  ┌──────────────────────────────────────────────────────┐
  │ 适用: Core 内部的永久性故障                           │
  │ 机制: CPU Core Offline                               │
  │ 原理:                                                │
  │  · MCA 检测到 Core 内部 Cache/ALU 故障               │
  │  · MCA Handler 标记该 Core 为 "offline"              │
  │  · OS 调度器不再向该 Core 派发任务                   │
  │  · 不影响其他 Core 的正常工作                        │
  │                                                      │
  │ 触发条件:                                            │
  │  · 连续的 CE 超过阈值 (CMCI) → Core 降级             │
  │  · UE 但可隔离 (如仅该 Core 的 L1 Cache) → Core Offline│
  │                                                      │
  │ Linux mcelog 处理流程:                               │
  │  1. MCE 发生 → CPU 进入 Machine Check Handler       │
  │  2. mcelog 读取 MC Bank 状态                         │
  │  3. 判定: 是否能隔离?                               │
  │  4. 是 → 写 /sys/devices/system/cpu/cpuN/online = 0 │
  │  5. 否 → PANIC                                       │
  └──────────────────────────────────────────────────────┘

Level 3: Package 级恢复 (CPU 整体复位)
  ┌──────────────────────────────────────────────────────┐
  │ 适用: CPU 整体卡死 / 固件崩溃                        │
  │ 机制: CATERR (Catastrophic Error) → BMC 干预        │
  │ 原理:                                                │
  │  · CPU 检测到不可恢复错误 → 拉低 CATERR# 引脚        │
  │  · BMC 收到 CATERR 信号                              │
  │  · BMC 通过 PECI 读取 MCA bank 获取故障原因          │
  │  · BMC 决定恢复策略:                                 │
  │    a) Warm Reset: 通过 PECI 或 SIO 触发系统复位      │
  │    b) Cold Reset: 断电再上电 (POR)                  │
  │    c) 整机断电: 如果故障在电源域无法隔离             │
  ├──────────────────────────────────────────────────────┤
  │ SMI (System Management Interrupt) 恢复路径:          │
  │  · MCA 也可触发 SMI (通过 MCi_CTL 配置)              │
  │  · CPU 进入 SMM (System Management Mode)             │
  │  · SMI Handler 在 SMRAM 中执行恢复操作               │
  │  · 退出 SMM 后, OS 无察觉                            │
  │  · SMM 可做: 记录错误 → 修复 → RSM (返回)           │
  └──────────────────────────────────────────────────────┘

Level 4: 系统级恢复 (BMC 主导)
  ┌──────────────────────────────────────────────────────┐
  │ BMC 检测到 CPU 异常 (CATERR / PECI 超时 / Watchdog)  │
  │ → BMC 启动恢复流程:                                  │
  │  1. BMC 记录错误到 SEL (System Event Log)           │
  │  2. BMC 尝试 Warm Reset (不切断供电)                │
  │  3. 如果 Warm Reset 后 BIOS 启动失败                 │
  │  4. BMC 切换 BIOS Slot (A/B 冗余)                   │
  │  5. 尝试 Cold Reset (断电重上电)                    │
  │  6. 如果仍然失败 → BMC 拉高 POWER_FAIL 告警          │
  │  7. 通知管理平台 (IPMI / Redfish)                    │
  │  8. 等待人工介入或自动 RMA                            │
  └──────────────────────────────────────────────────────┘
```

---

## 第3章 PCIe Switch 初始化与故障恢复

### 3.1 供电与时钟域

PCIe Switch 的供电比 CPU 简单，但链路数量多导致总功耗不小：

```text
PCIe Switch (Broadcom PEX88000) 供电域:

┌──────────────────────────────────────────────────────┐
│  12V 主电源                                           │
│      │                                                │
│      ├─ Vdd_core (0.85V) → 数字核心逻辑               │
│      │   · Crossbar, Routing Logic                    │
│      │   · 管理处理器 (内部ARM/RISC-V)                │
│      │   · 功耗: ~5-15W                               │
│      │                                                │
│      ├─ Vdd_serdes (1.0V) → SerDes PHY               │
│      │   · 所有 PCIe Lane 的 TX/RX PHY               │
│      │   · 80-100 lanes × ~20mW/lane = ~1.6-2W       │
│      │   · 需要低噪声 LDO                             │
│      │                                                │
│      ├─ Vdd_io (1.8V) → I/O 接口                     │
│      │   · Management (SMBus/I2C/GPIO)                │
│      │   · 参考时钟输入                               │
│      │   · JTAG/调试接口                              │
│      │                                                │
│      └─ Vdd_pll (0.9V) → PLL 时钟产生               │
│          · 独立 LDO 供电 (电源噪声隔离)               │
│          · PLL 锁定后 SerDes 才能开始训练             │
└──────────────────────────────────────────────────────┘

上电时序:
  1. 主 12V 到达 VR
  2. Vdd_core 上电 → Power Good
  3. Vdd_pll 上电 → PLL 锁定 (~100μs)
  4. Vdd_serdes 上电 → PHY 就绪
  5. Vdd_io 上电 → 管理接口可用
  6. PERST# (PCIe Reset) 信号释放 → 开始 LTSSM
```

### 3.2 固件初始化与配置空间填充

#### 3.2.1 Switch 固件加载

大多数 PCIe Switch 使用内部嵌入式处理器 (ARM/RISC-V) 运行固件：

```text
PCIe Switch (PEX88000) 固件加载:

Boot ROM (内部 ROM)
   ├─ 基本初始化: Stack, Watchdog, Clock
   ├─ 读取 BOOT_CFG 引脚 (决定启动源)
   │   ├─ SPI Flash (主启动)
   │   ├─ I2C EEPROM (备选)
   │   └─ 内部 ROM（默认最小固件）
   ├─ 从 SPI Flash 加载 Primary Loader
   └─ 验签 (如果 Secure Boot 使能)

Primary Loader
   ├─ 配置 Internal Memory Controller (SRAM)
   ├─ 解压 Main Firmware (如果有压缩)
   ├─ 初始化 Port Config (端口数量/宽度/极性)
   ├─ 初始化 Routing Table (路由表)
   └─ 跳转到 Main Firmware

Main Firmware
   ├─ 启动实时任务调度器 (FreeRTOS/ThreadX)
   ├─ 初始化 Management Interface (SMBus/I2C)
   ├─ 配置 Error Handling (AER/DPC 寄存器)
   ├─ 初始化 Virtualization (SR-IOV/Multi-Function)
   └─ 进入 IDLE 状态, 等待 Link 训练

固件升级:
  · 支持 In-Band Flash Update (通过 PCIe BAR 访问 Flash)
  · 双镜像 (Dual Image) 支持: A/B 分区, 启动失败自动回滚
  · BMC 可通过 SMBus 触发固件升级
```

#### 3.2.2 配置空间初始化

Switch 的配置空间初始化是芯片固件+硬件协同的关键过程：

```text
PCIe Switch 初始化配置空间:

难度核心:
  · 一个 Switch 包含 1 个 Upstream Port + N 个 Downstream Port
  · 每个 Port 需要配置为准确 Type 0/Type 1 Header
  · 路由表必须和拓扑信息一致

初始化步骤:
  ┌──────────────────────────────────────────────────────┐
  │  1. 端口类型配置 (Port Type Assignment)                │
  │  Firmware 根据 GPIO 或 EEPROM 配置确定:                │
  │  · Port 0: Upstream (面向 Root Complex)               │
  │  · Port 1-N: Downstream (面向 Endpoint)               │
  │  · 每个 Port 分配唯一 Bus Number (但 BIOS 会覆盖)      │
  │                                                        │
  │  2. 端口宽度配置 (Port Width Configuration)             │
  │  Firmware 设置:                                        │
  │  · Port 0: x16 → SerDes lanes 0-15 分配给 Upstream   │
  │  · Port 1: x8 → SerDes lanes 16-23                    │
  │  · ...                                                  │
  │  Lane Reversal (反转) + Polarity (极性) 配置           │
  │                                                        │
  │  3. 配置空间分配                                        │
  │  每个 Port 生成:                                       │
  │  · PCIe Type 0/1 Header (256B)                        │
  │  · Capability List (PCIe Cap, PM Cap, MSI/MSI-X...)   │
  │  · Extended Cap (AER, DPC, VC, ACS, SR-IOV)           │
  │  · 这些在硬件复位时初始化, 固件只做微调               │
  │                                                        │
  │  4. 路由表初始化                                        │
  │  · 基于端口-Bus 映射初始化内部路由表                   │
  │  · 如果使用 NTB (Non-Transparent Bridge)              │
  │  · 配置地址转换映射 (Address Translation)              │
  └──────────────────────────────────────────────────────┘
```

### 3.3 链路初始化：LTSSM 全流程

PCIe Switch 的链路初始化与 CPU Root Port 类似，但作为中间节点需要处理两端：

```text
PCIe Switch 链路训练 (Upstream + 每个 Downstream 独立):

┌─────────────────────────────────────────────────────────┐
│  PERST# 释放 (复位释放)                                  │
│      │                                                   │
│      ▼                                                   │
│  LTSSM: Detect → Polling → Configuration → L0           │
│      │                                                   │
│  每阶段详述:                                             │
│      │                                                   │
│  [1] Detect Phase                                        │
│  ├─ TX 发送 Detect 信号 (RD-0000)                        │
│  ├─ RX 检测: 是否有对端终端阻抗 (~50Ω @差分接收端)       │
│  ├─ 无: 该 Port 状态标记为 "Link Down"                  │
│  ├─ 有: 进入 Polling                                     │
│      │                                                   │
│  [2] Polling Phase                                       │
│  ├─ TX 发送 TS1 序列                                     │
│  ├─ RX 接收 TS1 → 位锁定 (Bit Lock) + 符号锁定          │
│  ├─ 交换 Port Number / Lane Number                       │
│  ├─ 确定 Lane-to-Lane 映射 (Lane Polarity + Reversal)    │
│  └─ Lane Deskew: 接收所有 Lane 的 TS2 → 对齐到最慢 Lane │
│      │                                                   │
│  [3] Configuration Phase                                 │
│  ├─ 宽度协商: TX 发送 TS1 包含"要协商的宽度"             │
│  ├─ 两边互相看到对方的请求后, 双方同意 → 锁定宽度       │
│  └─ 进入 L0                                              │
│      │                                                   │
│  [4] L0 → Equalization (PCIe Gen5/6)                     │
│  ├─ Phase 1: TX Preset 交换 (TX 能力宣告)               │
│  ├─ Phase 2: RX 测量信道 → 请求 TX 调整 EQ 系数        │
│  ├─ Phase 3: TX 按请求调整系数 → 下发调整后的 TS1       │
│  ├─ Phase 4: RX 最终确认 → EQ Done                      │
│  └─ 如果任何 Phase 失败 → 降速到 Gen4/3/2/1 重训        │
│                                                        │
│  工作状态 (L0):                                          │
│  · 正常数据收发                                           │
│  · Switch 内部 Crossbar 根据路由表转发 TLP               │
│  · 无需 CPU 参与——纯硬件转发                             │
└─────────────────────────────────────────────────────────┘
```

### 3.4 监控子系统：per-port 错误计数与温度

PCIe Switch 提供 per-port 的详细错误监控：

```text
PCIe Switch 每个 Port 的监控机制:

┌──────────────────────────────────────────────────────────┐
│  Port 0 (Upstream)                                       │
│  ┌────────────────────────────────────────────────────┐  │
│  │ AER 寄存器组:                                       │  │
│  │  · Uncorrectable Error Status (7 种)                │  │
│  │  · Correctable Error Status (14 种)                 │  │
│  │  · Error Source Identification                      │  │
│  │  · TLP Prefix Logging                               │  │
│  ├────────────────────────────────────────────────────┤  │
│  │ CRC 计数器:                                         │  │
│  │  · RX CRC Error Count (32-bit 计数器)              │  │
│  │  · TX Replay Count （重传次数）                     │  │
│  │  · LCRC Error / ECRC Error                         │  │
│  ├────────────────────────────────────────────────────┤  │
│  │ FEC 计数器 (Gen6):                                  │  │
│  │  · Lightweight FEC Corrected                        │  │
│  │  · RS-FEC Corrected Symbol Count                    │  │
│  │  · RS-FEC Uncorrectable Count                       │  │
│  ├────────────────────────────────────────────────────┤  │
│  │ 链路质量:                                            │  │
│  │  · Current Link Speed (32/16/8 GT/s)                │  │
│  │  · Negotiated Link Width (x16/x8/x4/x2/x1)         │  │
│  │  · Lane Error Count per Lane                         │  │
│  │  · RX Signal Detect Status                           │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  Switch 内部温度传感器:                                   │
│  ┌────────────────────────────────────────────────────┐  │
│  │  · Die 温度 (中心点)                                 │  │
│  │  · Hotspot 温度 (SerDes 区域, Crossbar 区域)        │  │
│  │  · 阈值: Warning (85°C) → Critical (105°C)         │  │
│  │  · 温度过高 → 风扇提速 / 链路降速 / 告警            │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘

SMBus 管理接口:
  · BMC 通过 SMBus 读取每个 Port 的状态寄存器
  · 读取 CRC 错误计数器 (per port per direction)
  · 读取温度数值
  · 无需 I2C 读写每个 Port — Switch 提供统计汇总寄存器
```

### 3.5 PCIe Switch 故障恢复

#### 3.5.1 链路级恢复

```text
Level 1: 单链路恢复 (Single Port Recovery)

触发条件:
  · CRC 错误计数器超过阈值 (每 port 可配置)
  · AER Correctable Error (如 Replay Timer Timeout)
  · Link 质量下降 (RX 信号丢失)

恢复流程:
  ┌────────────────────────────────────────────────────┐
  │  1. 硬件自动恢复: LTSSM Recovery                  │
  │  · 从 L0 进入 Recovery 状态                        │
  │  · 重新训练: Detect → Polling → Config → EQ      │
  │  · 重训期间: 该 Port 无数据转发                    │
  │  · 重训时间: ~1-100ms (取决于 Gen/EQ 复杂度)      │
  │                                                     │
  │  2. 如果重训失败: 降速                             │
  │  · Gen6 (64G) → Gen5 (32G) → Gen4 (16G) → ...    │
  │  · 每次降速后重训                                   │
  │  · 如果降到 Gen1 仍失败: 标记 Link Down            │
  │                                                     │
  │  3. 如果为瞬时: 恢复 L0 继续工作                   │
  │  · 记录 AER 可修正错误                              │
  │  · 计数不重置 → 累计到阈值触发 DPC                 │
  └────────────────────────────────────────────────────┘
```

#### 3.5.2 DPC (Downstream Port Containment)

DPC 是 PCIe Switch 最关键的故障隔离机制：

```text
Level 2: DPC 隔离 (Port Containment)

DPC 原理:
  ┌──────────────────────────────────────────────────────┐
  │  DPC 触发条件:                                      │
  │  · Uncorrectable Non-Fatal Error (如 Completion      │
  │    Timeout, Unexpected Completion)                   │
  │  · 连续的 Correctable Error (超过阈值)               │
  │  · Poisoned TLP 收到                                 │
  │                                                       │
  │  DPC 触发后的硬件行为:                               │
  │  1. Switch 自动将 Downstream Port 置于 "DPC Triggered"│
  │  2. 该端口:                                         │
  │     · 丢弃所有后续 TLP (不再转发任何包)              │
  │     · 返回 Configuration Retry Status (CRS)          │
  │     · 对端设备看到的: "设备不见了"                    │
  │  3. Switch 向 Upstream (CPU) 发送 AER Interrupt     │
  │  4. OS/AER 驱动读取 DPC 状态寄存器                   │
  │                                                       │
  │  DPC 恢复流程:                                       │
  │  1. OS/驱动确定: 需要 DPC 恢复?                      │
  │  2. 写 DPC Control Register: Trigger +4              │
  │     (触发 RP Bus Hot Reset)                          │
  │  3. Switch 向隔离的端口发送 Hot Reset (LTSSM Hot Reset)│
  │  4. 端口重新训练, 设备重新枚举                        │
  │  5. DPC 状态恢复为 "Ready"                           │
  │                                                       │
  │  超时保护:                                           │
  │  · DPC Trigger Timeout: 如果 1s 内不恢复              │
  │  · 升级到: DPC ERST (Enhanced Recovery)              │
  │  · ERST: 通知 BMC 该 Port 永久故障                   │
  │  · BMC 记录到 SEL + 标记该设备不可用                  │
  └──────────────────────────────────────────────────────┘
```

#### 3.5.3 端口重映射 (Port Remapping)

当某个 Downstream Port 物理故障，Switch 可动态重映射：

```text
Level 3: 端口重映射 (Port Remapping)

前提: Switch 的 SerDes Lane 支持 "Lane Pooling"
  · 一个物理 SerDes Lane 可以配给任意逻辑 Port
  · 实现: Configurable Lane Mapper (硬件 MUX)

场景: Port 7 (x8) 物理损坏
  1. Firmware 检测到 Port 7 的 SerDes Lane 17-24 有硬故障
  2. Firmware 检查是否有空闲 Lane
  3. 有: 从 Lane Pool 中分配备用 Lane
  4. 无: 将 Port 7 降为 x4 (使用 Lane 17-20)
  5. 重新触发链路训练
  6. 更新配置空间 (Link Capabilities 反映新宽度)
  
  代价:
  · 重映射期间: ~100ms-1s 端口中断
  · 如果 Lane 不够 → 带宽降级 (x16→x8→x4)
```

#### 3.5.4 全芯片恢复

```text
Level 4: Switch 全芯片恢复

触发条件:
  · 内部处理器固件崩溃
  · 多端口同时故障 → 可能是芯片内部错误
  · Watchdog 超时
  · 温度超过临界值 + 降频无效

恢复流程:
  ┌──────────────────────────────────────────────────────┐
  │  BMC 检测条件:                                       │
  │  · SMBus 超时 (MCU 不响应)                           │
  │  · Watchdog 超时 (GPIO)                              │
  │  · 温度传感器读到 Critical 值                        │
  │                                                       │
  │  恢复动作 (由 BMC 执行):                              │
  │  1. 拉低 PERST# 信号 (保持 100ms)                   │
  │  2. 等待 100ms (放电)                               │
  │  3. 释放 PERST#                                      │
  │  4. Switch 重新执行完整的固件加载 + 链路训练          │
  │  5. BMC 等待链路上线 → 检查温度是否恢复正常          │
  │  6. 成功后: 记录 SEL + 通知管理平台                  │
  │  7. 失败: 判断芯片永久故障                             │
  │                                                       │
  │  PERST# 复位的优势:                                   │
  │  · 所有 SerDes 链路重置 (清除瞬态故障)              │
  │  · 固件重新加载 (如果固件损坏, 启动备份镜像)          │
  │  · 比断电快 (~500ms vs ~5s)                          │
  └──────────────────────────────────────────────────────┘
```

---

## 第4章 USB 控制器初始化与故障恢复

### 4.1 供电与时钟

USB 控制器（集成在 PCH/Southbridge 或 SoC 内）的供电相对简单：

```text
USB 3.x 控制器供电域 (xHCI) — 集成在 PCH:

┌──────────────────────────────────────────────────────┐
│  PCH (Platform Controller Hub)                        │
│  ┌────────────────────────────────────────────────┐   │
│  │  Vcc_core (0.85V): PCH 数字逻辑域              │   │
│  │  ├─ xHCI Controller (USB 3.x MAC)              │   │
│  │  ├─ EHCI Controller (USB 2.0 MAC)              │   │
│  │  └─ 调度器/队列管理                             │   │
│  │                                                 │   │
│  │  Vdd_usb (1.0V): USB PHY 供电域                │   │
│  │  ├─ USB 2.0 PHY (FS/LS/HS 模拟前端)           │   │
│  │  ├─ USB 3.x PHY (SS Gen1/Gen2 PAM-N 串行器)   │   │
│  │  └─ PLL (480MHz USB2, ~2.5GHz USB3)            │   │
│  │                                                 │   │
│  │  Vdd_io (1.8V): I/O 接口                       │   │
│  │  ├─ USB D+/D- (3.3V 域通过 LDO 转 1.8V)       │   │
│  │  └─ USB SS TX/RX 差分对 (交流耦合)             │   │
│  └────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘

上电时序:
  1. PCH Vcc_core 上电 → 控制器复位释放
  2. PLL 锁定 (PCH 内部的 100MHz 参考时钟)
  3. USB PHY 供电 + 校准
  4. 等待 USB VBUS 检测 (设备插入触发)
```

### 4.2 固件初始化

#### 4.2.1 xHCI (eXtensible Host Controller Interface) 初始化

USB 3.x 主控遵循 xHCI 规范，一个统一的主机控制器接口：

```text
xHCI 控制器初始化 (由 UEFI 或 OS 驱动执行):

┌─────────────────────────────────────────────────────────┐
│  xHCI 初始化步骤:                                        │
│                                                         │
│  1. 电源管理初始化                                       │
│  ├─ 确保控制器处于 D0 (全供电) 状态                      │
│  ├─ 清除任何遗留的电源状态                               │
│  └─ 确保 USB2 时钟稳定 (48MHz) + USB3 PLL 锁定          │
│                                                         │
│  2. 控制器复位 (HCRST)                                  │
│  ├─ 写 USBCMD RST bit = 1                               │
│  ├─ 硬件复位所有内部状态机                               │
│  ├─ 等待 RST bit 硬件清除 (约 10ms)                     │
│  └─ 所有寄存器回到默认值                                 │
│                                                         │
│  3. 配置 Capability Registers                            │
│  ├─ 读取 HCSPARAMS1: 支持的 Port 数, Interrupter 数     │
│  ├─ 读取 HCSPARAMS2: Scratchpad Buffer 大小             │
│  └─ 读取 HCCPARAMS1: 支持的特性 (64-bit, xECP, etc)     │
│                                                         │
│  4. 内存分配                                             │
│  ├─ 分配 Device Context Base Address Array (DCBAA)      │
│  ├─ 分配 Scratchpad Buffers                             │
│  └─ 初始化 Command Ring (TRB 队列)                      │
│                                                         │
│  5. 设置 Operational Registers                           │
│  ├─ 写 DCBAAP (DCBAA 的物理地址)                        │
│  ├─ 写 CONFIG (Max Device Slots Enabled)               │
│  ├─ 写 CRCR (Command Ring Control Register)             │
│  └─ 写 USBCMD Run/Stop = 1 → 控制器开始运行             │
│                                                         │
│  6. 路由初始化 (Root Hub Port)                          │
│  ├─ 读取 PORTSC 寄存器 → 检测是否有设备连接             │
│  └─ 如果有: 启动 Port Reset → 设备枚举                  │
└─────────────────────────────────────────────────────────┘
```

### 4.3 USB PHY 初始化与校准

USB PHY 的初始化相当复杂，包含多个模拟校准步骤：

```text
USB 3.x PHY 初始化与校准:

┌─────────────────────────────────────────────────────────┐
│  USB 3.0 PHY 初始化 (Gen1: 5 Gbps, Gen2: 10 Gbps)      │
│                                                         │
│  Step 1: PLL 锁定                                       │
│  · 参考时钟: 通常是 100MHz 或 125MHz (来自 PCH)         │
│  · PLL 倍频到: 2.5GHz (Gen1) 或 5GHz (Gen2)            │
│  · 锁定时间: ~100μs                                    │
│  · 必须稳定后才能进行 PHY 操作                          │
│                                                         │
│  Step 2: TX 校准                                        │
│  · Impedance Calibration: 校准 TX 驱动阻抗 (45Ω ±5%)  │
│  · Output Swing 校准: 调整输出摆幅 (400-1200mV)         │
│  · Pre-Emphasis 校准: 补偿信道损耗                      │
│  · 校准参考: 外部精密电阻 (Rext, 精度 ±1%)              │
│                                                         │
│  Step 3: RX 校准                                        │
│  · CTLE Calibration: 校准均衡器 (增益/零极点)           │
│  · CDR Calibration: 锁定 CDR 中心频率                   │
│  · Squelch Detection 阈值校准                           │
│  · LFPS (低频周期信号) 检测器校准                       │
│                                                         │
│  Step 4: SSC (扩频时钟) 处理                            │
│  · USB 3.0 支持 -5000 ppm SSC (Spread Spectrum)        │
│  · CDR 必须跟踪 SSC 的频率变化                          │
│  · CDR 环路带宽必须 > SSC 调制频率 (~33kHz)             │
│                                                         │
│  USB 2.0 PHY (480 Mbps):                                │
│  · 简单得多: 只有阻抗校准 + 摆幅校准                    │
│  · 无 PLL (从 48MHz 时钟直接分频)                       │
│  · 无 CTLE/CDR (USB2 使用源同步时钟)                   │
└─────────────────────────────────────────────────────────┘
```

### 4.4 链路训练与枚举：USB 2.0 / 3.x / USB4

USB 的链路训练是一个"握手→速率协商→均衡"的多阶段过程：

#### 4.4.1 USB 3.0 链路训练

```text
USB 3.0 (SS, SuperSpeed) 链路训练全流程:

┌─────────────────────────────────────────────────────────┐
│  Step 1: 设备连接检测 (由 USB 2.0 完成)                 │
│  · 设备插入后, USB 2.0 D+ 上拉到 3.3V                  │
│  · 主机检测到 D+ > 2.0V → 设备连接                     │
│  · USB 2.0 线先完成设备枚举 (获取设备描述符)            │
│  · 设备描述符指示: "我支持 SuperSpeed"                   │
│                                                         │
│  Step 2: LFPS 握手 (SuperSpeed 链路启动)                │
│  ┌─────────────────────────────────────────────────┐   │
│  │  主机              设备                        │   │
│  │   │                     │                       │   │
│  │   │──── Polling LFPS ───→│ (主机发起, 33-50ms)  │   │
│  │   │←─── TSEQ/TS1 ───────│ (设备响应)            │   │
│  │   │──── TS2 ────────────→│                       │   │
│  │   │←─── 训练完成 ────────│                       │   │
│  │   │══════════════════════│ U0 正常操作           │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Step 3: 均衡 (Equalization, Gen2 10Gbps)               │
│  · TX Preset Handshake: 交换预加重能力                  │
│  · Frequency Sweep: 频率扫描 → 估计信道频率响应         │
│  · Coefficient Update: 主机调整 TX 系数                  │
│  · Final Equalization: 锁存最优系数                     │
│  · 如果不通过 → 降速到 Gen1 (5Gbps)                    │
│                                                         │
│  Step 4: U0 状态 (正常操作)                             │
│  · 开始正常数据收发 (Bulk/Isochronous/Interrupt/Control)│
│  · 电源管理: U0→U1(待机)→U2(睡眠)→U3(挂起)            │
└─────────────────────────────────────────────────────────┘
```

#### 4.4.2 USB 2.0 高速检测握手 (Chirp)

```text
USB 2.0 高速 (HS, 480Mbps) 的检测过程:

USB 2.0 设备插入 → 主机检测 D+ 拉高

                        ┌─────────┐
  D+ (主机侧) ──────────┤ 1.5kΩ  ├──── Vbus
                        ├─────────┤
                        └─────────┘  3.3V → 主机检测到"设备连接"

  主机响应: 复位 (Reset) — 拉低 D+/D- 保持 10ms
  设备检测到 Reset → 进入 Chirp 流程:

  ┌─────────────────────────────────────────────────────┐
  │  Chirp 流程:                                        │
  │                                                     │
  │  1. 主机: 拉低 D+/D- 保持 10ms (Reset)              │
  │                                                     │
  │  2. 设备: 如果支持 HS, 在 D+ 上发送 Chirp K         │
  │     (设备: "我支持高速, 可以更快的")                 │
  │     Chirp K: D+ 高, D- 低, 持续 1ms                 │
  │                                                     │
  │  3. 主机: 如果支持 HS, 交替发送 Chirp K/J           │
  │     (主机: "好的, 我也支持高速, 我们开始吧")         │
  │     Chirp K: D+高 D-低 (1ms)                        │
  │     Chirp J: D+低 D-高 (1ms)                        │
  │     → 交替共持续 ~2-6ms                             │
  │                                                     │
  │  4. 双方切换到 HS 模式 (480MHz)                     │
  │     · 终结电阻从 1.5kΩ → 45Ω                       │
  │     · 电流源模式驱动                                 │
  │     · 开始 SOF (Start of Frame) 同步               │
  │                                                     │
  │  5. 如果 Chirp 失败 (设备没回应) → 降级到 FS (12Mbps)│
  │     · 使用 D+/D- 差分信号 (非电流源)                │
  │     · 较慢, 但容错性更好                            │
  └─────────────────────────────────────────────────────┘
```

### 4.5 USB 异常检测与恢复

#### 4.5.1 USB 错误类型

| 错误类型 | 检测机制 | 影响 | 恢复方式 |
|:---------|:---------|:-----|:---------|
| **CRC 错误** | 数据包 CRC16/CRC5 校验失败 | 该包丢弃, 需重传 | 硬件自动重传 |
| **Timeout** | 无响应超时 (USB 3.0: ~500ms) | 事务失败 | 取消事务 → 重新发送 |
| **Link 错误** | LFPS 检测失败 / 信号丢失 | Link 状态降级 | 链路重训练 (LFPS 重新握手) |
| **Babble** | 设备超时未释放总线 | 主机中断事务 | 端口复位 |
| **Stall** | 设备返回 STALL 握手包 | 端点不可用 | 驱动清理端点 → 重新配置 |
| **过电流** | VBUS 电流检测 > 5A | 端口关闭 | 硬件自动断开, 需手动恢复 |
| **热插拔** | D+ 电平跳变 | 设备断开 | 清理资源 → 等待新连接 |
| **复位** | SE0 (D+/D- 同时拉低) | 设备复位 | 重新枚举 |

#### 4.5.2 USB 多层次恢复

```text
USB 恢复机制 (从浅到深):

Level 1: 硬件自动重传 (包级恢复)
  ┌─────────────────────────────────────────────────────┐
  │ USB 3.0 支持硬件级 CRC 错误重传:                     │
  │  · RX 检测到 Header CRC 错误                         │
  │  · 硬件自动: NAK → 等待重传                          │
  │  · 如果重传成功: 完全透明                             │
  │  · 如果连续 N 次失败 → 升级到链路恢复                │
  │  USB 2.0 类似: ACK/NAK 协议                          │
  └─────────────────────────────────────────────────────┘

Level 2: 端口复位 (设备级恢复)
  ┌─────────────────────────────────────────────────────┐
  │ 触发条件:                                           │
  │  · 主机检测到 Link 错误                             │
  │  · 设备返回连续的 NAK/STALL (软件判定)              │
  │  · Timeout 超时                                     │
  │                                                     │
  │ 复位流程:                                           │
  │  1. 主机写 PORTSC (Port Status and Control)         │
  │     置位 Port Reset                                 │
  │  2. 硬件拉低 D+/D- (SE0) 保持 ~10ms                │
  │  3. 释放 SE0 → 设备检测到复位结束                   │
  │  4. 设备重新: Chirp → 速率协商 → 枚举               │
  │  5. 驱动重新: 获取描述符 → 配置端点                 │
  │  6. 恢复数据传输                                     │
  │                                                     │
  │ 影响: ~100ms-1s (取决于设备复位后的枚举时间)        │
  └─────────────────────────────────────────────────────┘

Level 3: xHCI 控制器复位 (控制器级恢复)
  ┌─────────────────────────────────────────────────────┐
  │ 触发条件:                                           │
  │  · xHCI 内部状态机卡死 (环形缓冲区溢出等)           │
  │  · 所有端口同时故障                                 │
  │  · 固件崩溃                                         │
  │                                                     │
  │ 复位流程:                                           │
  │  1. 写 USBCMD RST = 1                               │
  │  2. 控制器 Flush 所有正在执行的事务                  │
  │  3. 寄存器回到默认值                                 │
  │  4. OS 驱动重新初始化                                │
  │     (重新分配 DCBAA, 设置 CRCR, 重启调度器)        │
  │  5. 重新检测所有端口                                 │
  │  6. 重新枚举设备                                     │
  │                                                     │
  │ 影响: ~1-3s (控制器复位 + 设备重枚举)               │
  │                                                     │
  │ 恢复成功率: 高 (~80%) — 大多数 USB 控制器异常      │
  │ 是软件/状态机问题, 不是硬损坏                       │
  └─────────────────────────────────────────────────────┘

Level 4: 芯片/系统级恢复 (PCH/SoC 复位)
  ┌─────────────────────────────────────────────────────┐
  │ 触发条件:                                           │
  │  · PCH 内部 PCIe/USB 控制器失效                     │
  │  · PCH 温度过高                                     │
  │  · USB PHY 供电异常                                 │
  │                                                     │
  │ 恢复: PCH Warm Reset (不整机断电)                   │
  │  1. 操作系统关机                                     │
  │  2. 主板触发 PCH 复位                               │
  │  3. PCH 加载固件 → 初始化 USB → xHCI 重新可用      │
  │  4. 系统重启                                         │
  │                                                     │
  │ 影响: 整机重启 (~10-30s)                            │
  └─────────────────────────────────────────────────────┘
```

---

## 第5章 SSD 主控初始化与故障恢复

### 5.1 供电与上电时序

SSD 主控的供电比 GPU/CPU 简单，但对电源时序和掉电保护有特殊要求：

```text
NVMe SSD 供电域 (以典型 PCIe Gen4 SSD 为例):

┌──────────────────────────────────────────────────────┐
│  主电源 (PCIe Slot 3.3V / 或 M.2 3.3V)               │
│      │                                                │
│  ┌───┴────────────────────────────────────────────┐   │
│  │  板载 PMIC (Power Management IC)                │   │
│  │  ┌────────────────────────────────────────────┐ │   │
│  │  │  Vcc_core (0.8-0.9V): 主控数字核心         │ │   │
│  │  │  · 处理器 (ARM Cortex-R5/R8 + DSP)        │ │   │
│  │  │  · 加密引擎, ECC引擎, DMA引擎              │ │   │
│  │  │  · 功耗: ~0.5-2W (随机读写)                │ │   │
│  │  ├────────────────────────────────────────────┤ │   │
│  │  │  Vcc_io (1.8V): I/O 接口                  │ │   │
│  │  │  · PCIe PHY (1.0V/1.8V)                   │ │   │
│  │  │  · NAND 接口 (1.2V/1.8V, 取决于 NAND 类型)│ │   │
│  │  │  · 调试接口 (UART/JTAG)                   │ │   │
│  │  ├────────────────────────────────────────────┤ │   │
│  │  │  Vcc_nand (3.3V/1.8V): NAND Flash 供电    │ │   │
│  │  │  · 多个 NAND Die 共享                      │ │   │
│  │  │  · 每通道独立电源控制 (通道级关断)         │ │   │
│  │  │  · 功耗: ~1-3W (持续读写)                 │ │   │
│  │  ├────────────────────────────────────────────┤ │   │
│  │  │  Vcc_pll (0.9V): PLL 时钟                │ │   │
│  │  │  · PCIe SerDes PLL                        │ │   │
│  │  │  · NAND Controller PLL                    │ │   │
│  │  └────────────────────────────────────────────┘ │   │
│  │                                                │   │
│  │  掉电保护:                                      │   │
│  │  ┌────────────────────────────────────────────┐ │   │
│  │  │  保持电容 (Hold-up Capacitors)              │ │   │
│  │  │  · 通常是钽电容或超级电容                    │   │
│  │  │  · 存储电量: ~10-40mJ (足够完成最后的刷写) │   │
│  │  │  · 检测到掉电 → PMIC 切换为电容供电        │   │
│  │  │  · 主控有 ~1-10ms 时间完成最后的 FTL 更新  │   │
│  │  └────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘

上电时序:
  1. PCIe 3.3V 供电 → PMIC 启动
  2. PMIC 产生 Vcc_core → 主控复位释放
  3. Boot ROM 开始执行
  4. PMIC 产生 Vcc_io + Vcc_pll → PCIe PHY 可用
  5. PMIC 产生 Vcc_nand → NAND 控制器可用
  6. 等待 PERST# 释放 (PCIe 链路可训练)
```

### 5.2 Boot ROM → 固件加载：从 NAND 到 SRAM 的原理

这是 SSD 初始化最关键的阶段——在 NAND 还未初始化时如何加载固件：

```text
SSD 主控 (Phison E26 / Silicon Motion / 华为) 的 Boot 流程:

┌─────────────────────────────────────────────────────────┐
│  Step 0: 硬件复位释放                                    │
│  · PMIC 完成 Vcc_core 上电                              │
│  · PLL 锁定 → 内部时钟稳定                              │
│  · 主控的 ARM/RISC-V 内核复位释放 → 从 Boot ROM 取指   │
│                                                         │
│  Step 1: Boot ROM (掩膜 ROM, ~32-64KB)                  │
│  ┌─────────────────────────────────────────────────────┐│
│  │  Boot ROM 内置 (不可修改) 代码:                     ││
│  │  1. 初始化栈指针 (SP = SRAM 顶部)                  ││
│  │  2. 初始化 Cache 作为临时内存 (类似 CPU CAR)       ││
│  │  3. 设置最小 Watchdog (防止无限等待)                ││
│  │  4. 扫描可能的 Boot Device:                        ││
│  │     a. SPI ROM (外部 SPI Flash, 存固件)             ││
│  │     b. NAND (某个预留的 Boot Partition)             ││
│  │     c. I2C EEPROM (极少用)                         ││
│  │  5. 从 Boot Device 读取 Primary Boot Loader (PBL)   ││
│  │     到内部 SRAM (~256KB-1MB)                       ││
│  │  6. 验证 PBL 签名 (如果 Secure Boot 使能)           ││
│  │  7. 跳转到 PBL 入口                                 ││
│  └─────────────────────────────────────────────────────┘│
│                                                         │
│  Step 2: Primary Boot Loader (PBL)                      │
│  ┌─────────────────────────────────────────────────────┐│
│  │  PBL 在 SRAM 中执行:                                ││
│  │  1. 初始化 NAND 控制器 (最低配置: 单通道, 单 Die)   ││
│  │  2. 扫描 NAND 的 Boot Partition:                    ││
│  │     · 读取 NAND 的 ID (制造商, 类型, 规格)          ││
│  │     · 加载 Main Firmware (完整固件)                  ││
│  │     · 从 NAND 读取固件镜像 (通常 1-4MB)             ││
│  │  3. 需要 NAND 坏块管理                              ││
│  │     · PBL 必须知道 NAND 的 Bad Block Table 位置     ││
│  │     · 跳过坏块, 从好块读取                          ││
│  │  4. 验证 Main FW Signature                          ││
│  │  5. 解压 Main FW (如果压缩存储)                     ││
│  │  6. 将 Main FW 加载到 SRAM/DRAM                    ││
│  │  7. 跳转到 Main FW 入口                              ││
│  └─────────────────────────────────────────────────────┘│
│                                                         │
│  Step 3: Main Firmware                                  │
│  ┌─────────────────────────────────────────────────────┐│
│  │  Main FW 开始完整初始化:                             ││
│  │  1. 初始化 DRAM 控制器 (如果有板载 DRAM)            ││
│  │  2. 全功能 NAND 控制器初始化 (所有通道)             ││
│  │  3. 加载 FTL 映射表 (从 NAND 到 DRAM)                ││
│  │  4. 初始化 PCIe EP (作为 Endpoint 响应 LTSSM)       ││
│  │  5. 初始化 NVMe Admin Queue                         ││
│  │  6. 等待 Host 发送 NVMe Admin Commands               ││
│  └─────────────────────────────────────────────────────┘│
│                                                         │
│  关键难点: PBL 在不完整的 NAND 初始化下读取能力有限     │
│  · 只支持最低 NAND 速率 (通常 100-200 MT/s vs 全速     │
│    1200-2400 MT/s)                                     │
│  · 只使用单通道 (vs 全功能 4-8 通道)                   │
│  · 只使用简单 ECC (BCH, 非 LDPC)                       │
│  · 必须依赖 NAND Bad Block Table 的可靠性              │
└─────────────────────────────────────────────────────────┘
```

### 5.3 NAND 通道初始化与介质探测

#### 5.3.1 NAND 通道初始化原理

```text
SSD 主控的 NAND 通道初始化 (假设 8 通道):

┌─────────────────────────────────────────────────────────┐
│  NAND 通道初始化流程:                                    │
│                                                         │
│  1. 通道时序校准 (DQS Training)                        │
│  · 每个通道独立校准 NAND 接口的 DQS/DQ 时序             │
│  · Write DQS Training: 主控发出 DQS, NAND 锁存         │
│  · Read DQS Training: NAND 返回 DQS, 主控锁存          │
│  · 调整 per-pin 的 Delay Cell (步进 ~10ps)              │
│  · 找到最优采样窗口                                     │
│                                                         │
│  2. NAND ID 读取                                        │
│  · 发送 NAND Reset 命令 (FFh)                           │
│  · 发送 Read ID 命令 (90h)                              │
│  · 每个 Die 返回 4-8 字节的 ID 数据:                   │
│    - Byte 0: Manufacturer (Samsung/Micron/Kioxia/WDC)  │
│    - Byte 1: Device Configuration                      │
│    - Byte 2: NAND Type (SLC/MLC/TLC/QLC)               │
│    - Byte 3-4: Page Size, Block Size, Plane Count       │
│    - Byte 5-7: Feature Support (如 ONFI/Toggle)         │
│                                                         │
│  3. NAND 参数配置                                       │
│  · 根据 ID 查表: 时序参数 (tR, tPROG, tCCS, tBERS)     │
│  · 配置 ECC 强度 (取决于 NAND 类型: TLC 需要更强 ECC) │
│  · 配置 Read Retry Table (不同温度/磨损的读电压偏移)    │
│                                                         │
│  4. 坏块扫描                                            │
│  · 读 NAND 的 Bad Block Table (BBT, 通常是 NAND 的第   │
│    一块或最后一块的预留区域)                            │
│  · 标记已知坏块 (避免后续使用)                         │
│  · 如果 BBT 丢失或损坏: 全盘扫描 (需要 ~5-30s)        │
│                                                         │
│  5. 写入/擦除验证                                       │
│  · 写入已知模式 → 擦除 → 读回 → 验证                   │
│  · 检测 NAND 基本功能正常                               │
└─────────────────────────────────────────────────────────┘
```

### 5.4 FTL（闪存转换层）初始化与重建

FTL (Flash Translation Layer) 是 SSD 的核心——将 Host 的 LBA 映射到 NAND 的 PBA：

```text
FTL 初始化: 映射表恢复是关键挑战

问题:
  · FTL 映射表需要保存在 NAND (因为掉电不丢失)
  · 但 NAND 读取慢 (比 DRAM 慢 1000×)
  · 映射表大小: 典型 1TB SSD 需要 ~1-4GB 映射表
  · 全部从 NAND 读取 → 需要 ~1-10s

FTL 初始化策略:

┌─────────────────────────────────────────────────────────┐
│  策略 A: 全加载 (Full Load)                            │
│  · 将整个映射表从 NAND 读到主控的 DRAM                 │
│  · 优点: 加载后 FTL 操作最快                           │
│  · 缺点: 初始化慢 (~1-10s), 需要大 DRAM               │
│  · 适合: 企业级 SSD (不在乎启动速度, 在乎性能)        │
│                                                         │
│  策略 B: 需求加载 (Demand-based / Lazy Load)           │
│  · 只加载映射表的索引 (~4KB)                           │
│  · 实际 I/O 请求到来时按需加载对应页的映射             │
│  · 优点: 极快初始化 (~10ms)                            │
│  · 缺点: 初始访问有额外延迟 (page fault 式)           │
│  · 适合: 消费级 SSD (在乎首次响应速度, 不太在乎峰值)  │
│                                                         │
│  策略 C: 混合 (Hybrid)                                 │
│  · 加载热点映射表 (经常访问的 LBA 范围)                │
│  · 冷数据用需求加载                                     │
│  · 优点: 兼顾启动速度 + 常用性能                       │
│  · 缺点: 实现复杂                                       │
└─────────────────────────────────────────────────────────┘

FTL 损坏恢复:
  如果上次未正常关机 (掉电/崩溃)
  → FTL 映射表可能不一致

  检测: FTL Checksum (每次刷写时计算)
  恢复: 回放日志 (Replay Journal / Transaction Log)

  NAND 中有一个 "Journal Area":
  · 每次 FTL 更新, 先写 Journal (事务日志)
  · 写 NAND 数据 (真正的写入)
  · 标记 Journal 完成 (Commit)

  恢复时:
  · 扫描 Journal Area
  · 找到 "未完成" 的事务
  · 回滚 (Rollback) 或补全 (Roll-forward)
  · 重建映射表的一致性

  如果 Journal 也损坏:
  · 全盘扫描: 扫描每个 Block 的 Page Metadata
  · 重建 LBA→PBA 映射
  · 代价: ~30s-5min (取决于 SSD 容量)
  · 最坏情况: FTL 无法恢复 → SSD 完全不可用
```

### 5.5 PCIe EP 链路初始化

SSD 作为 PCIe Endpoint，链路训练是被动响应：

```text
SSD 的 PCIe EP 链路训练:

SSD 上电后:
  1. 固件初始化 PCIe EP Core
  2. 等待 PERST# 释放 (主机侧)
  3. 等待 Root Port 发送 TS1 训练序列

训练流程:
  ┌──────────────────────────────────────────────────────┐
  │  LTSSM (SSD EP 侧):                                 │
  │                                                       │
  │  Detect: 等待 TX 检测信号                             │
  │  → Polling: 发送 TS1 响应 Root Port                  │
  │  → Configuration: 协商宽度/速度                       │
  │  → L0: 进入正常操作                                   │
  │  → Equalization (Gen4+): 主机主导均衡                 │
  │                                                       │
  │  等 SSD EP 进入 L0 后:                               │
  │  1. 主机 (Root Port) 完成枚举                         │
  │  2. 主机写 NVMe BAR → 分配 MMIO 空间                  │
  │  3. 主机读 Vendor/Device ID → 识别 NVMe 控制器        │
  │  4. 主机初始化 NVMe Admin Queue                       │
  │  5. 主机发送 Identify Namespace 命令                  │
  │  6. SSD 响应: 容量, 特性, Format                      │
  │  7. 主机配置: 创建 I/O Queue Pair                    │
  │  8. SSD 可用 → 开始 I/O                               │
  └──────────────────────────────────────────────────────┘

PCIe Link 问题导致 SSD 不识别:
  · PERST# 时序问题: SSD 还没就绪主机就开始训练
  · Link 速率不匹配: SSD 只支持 Gen4, 主机降速协商
  · Equalization 失败: 信道损耗太大 (常见于 PCIe 扩展线)
```

### 5.6 NVMe 控制器初始化

```text
NVMe 控制器初始化 (由主机 OS 驱动执行):

┌──────────────────────────────────────────────────────────┐
│  1. 配置空间初始化                                       │
│  · 读取 PCIe Vendor/Device ID → 识别 NVMe 设备          │
│  · 使能 Bus Master (PCIe CMD: BusMaster=1)              │
│  · 使能 Memory Space (PCIe CMD: MemSpace=1)            │
│  · 映射 BAR0/1 (NVMe 寄存器基地址)                      │
│                                                         │
│  2. NVMe 控制器复位                                      │
│  · 写 NVMe CC.EN = 0 (控制器禁用)                       │
│  · 等待 NVMe CSTS.RDY = 0 (控制器确认关闭)              │
│  · 写 NVMe CC.EN = 1 (控制器使能)                       │
│  · 等待 NVMe CSTS.RDY = 1 (控制器就绪)                  │
│  · 设定: CC.IOCQES (I/O CQ Entry Size)                 │
│  · 设定: CC.IOSQES (I/O SQ Entry Size)                 │
│                                                         │
│  3. Admin Queue 初始化                                  │
│  · 分配 Admin Submission Queue (ASQ) 内存               │
│  · 分配 Admin Completion Queue (ACQ) 内存               │
│  · 写 ASQ: Admin SQ Base Address + Size                 │
│  · 写 ACQ: Admin CQ Base Address + Size                 │
│                                                         │
│  4. I/O Queue 创建                                      │
│  · 发 Create I/O Submission Queue (CNS=0x01)            │
│  · 发 Create I/O Completion Queue (CNS=0x05)            │
│  · 设置 Queue Depth (典型: 128-1024)                   │
│  · 多个 Queue 可以绑定到同一个 CQ                       │
│                                                         │
│  5. 识别命令                                             │
│  · 发 Identify: CNS=0x00 (Identify Namespace)          │
│  · 读回: 容量, EUI64, LBA Format, 区块大小             │
│  · 发 Identify: CNS=0x01 (Identify Controller)         │
│  · 读回: 控制器特性, 支持的 Feature                     │
│                                                         │
│  6. 设置特性 (Set Features)                              │
│  · Number of Queues (Number of I/O Queues)              │
│  · Interrupt Coalescing                                  │
│  · Power Management                                      │
│  · Temperature Threshold                                 │
│                                                         │
│  7. 设备可用 → 开始 I/O                                  │
│  · I/O SQ Tail Doorbell 写入 → SSD 开始执行命令         │
│  · 完成 → 写入 I/O CQ + 触发 MSI-X 中断                 │
│  · 驱动处理完成 → 更新 CQ Head Doorbell                  │
└──────────────────────────────────────────────────────────┘
```

### 5.7 监控子系统：SMART / Thermal / Power Loss

SSD 的监控系统比 CPU/GPU 更关注磨损和老化：

```text
SSD SMART (Self-Monitoring, Analysis and Reporting Technology):

NVMe 规范定义的 SMART 日志页:

┌──────────────────────────────────────────────────────────┐
│  Critical Warning (字节 0)                              │
│  · Bit 0: Temperature > Critical Threshold              │
│  · Bit 1: Spare Space < Threshold                       │
│  · Bit 2: NAND Reliability Degraded                     │
│  · Bit 3: Media in Read-Only Mode                       │
│  · Bit 4: Volatile Memory Backup Failed                 │
│                                                         │
│  Temperature (字节 1-3): 当前温度 (开尔文)              │
│  Available Spare (字节 5): 剩余备用块百分比              │
│  Percentage Used (字节 6): 磨损程度 (0-100%)            │
│  Data Units Read/Written (字节 32-47): 总读写量         │
│  Media Errors (字节 128-131): 不可修正错误计数           │
│  Number of Error Info Log Entries                       │
│  Power Cycles / Power On Hours                          │
│  Unsafe Shutdowns (不安全关机计数)                       │
│  Media and Data Integrity Errors                        │
│  Number of Error Information Log Entries                │
│                                                         │
│  Thermal Management:                                     │
│  · 2 个温度传感器: 主控温度 + NAND 温度                 │
│  · Throttling 阈值: ~65-85°C                           │
│  · Shutdown 阈值: ~95-105°C                            │
│  · Thermal Throttle: 降低 NAND 速率 (减少 30-70% 性能) │
└──────────────────────────────────────────────────────────┘

掉电保护 (Power Loss Protection, PLP):

┌──────────────────────────────────────────────────────────┐
│  企业级 SSD 内置掉电保护电路:                            │
│                                                         │
│  1. PLP 检测: PMIC 检测到主电源跌落 < 2.7V              │
│  2. PMIC 切换为保持电容供电                              │
│  3. 主控收到 "Power Loss" 中断                           │
│  4. 主控:                                               │
│     a. 中止正在执行的 NAND 写入 (不完整写入)            │
│     b. 将 FTL Map 快写入 NAND (紧急刷写)                │
│     c. 标记 "Clean Shutdown" 标志位                     │
│  5. 保持电容耗尽 → 主控掉电                             │
│  6. 下次开机: 检测到 Clean Shutdown 标志                 │
│     → 无需 FTL Recovery → 快速启动                      │
│                                                         │
│  普通 SSD (无 PLP):                                      │
│  · 突然掉电 → FTL 映射表可能不完整                      │
│  · 下次开机: 必须扫描 NAND Journal 重建 FTL             │
│  · 重建时间: ~1-10s                                     │
│  · 极端情况: 数据损坏, FTL 不可恢复                      │
└──────────────────────────────────────────────────────────┘
```

### 5.8 SSD 异常检测与恢复

#### 5.8.1 NAND 介质故障类型

| 故障类型 | 机制 | 严重性 | 恢复方式 |
|:---------|:-----|:------|:---------|
| **Read Disturb** | 多次读同一页, 电荷泄漏影响相邻页 | 数据错误 | Read Retry (重读 + 偏移读电压) |
| **Program Disturb** | 写数据时影响同一 Block 的其他页 | 写入错误 | 更新坏块表 → 重写入新块 |
| **Data Retention** | 长时间掉电后 NAND Cell 电荷丢失 | 数据过期 | 刷新 (Scrub → Re-write) |
| **Wear-out (Endurance)** | P/E 循环达到寿命极限 | **不可逆** | 标记只读 → 更换 SSD |
| **ECC Uncorrectable** | Bit 错误超过纠错能力 | **数据丢失** | 如果有 RAID/RAISE: 重构; 否则汇报不可恢复 |
| **Read Retry Fail** | 多次 Read Retry 均无法恢复 | **坏块** | 标记坏块 → 重映射 |

#### 5.8.2 SSD 多层次恢复

```text
Level 1: ECC 纠错 (硬件自动)
  ┌──────────────────────────────────────────────────────┐
  │  · 每次 NAND 读取, 硬件 ECC 引擎自动纠错             │
  │  · TLC NAND: LDPC (低密度奇偶校验码)                │
  │    · 每 1KB 数据 ~60-200 位纠错能力                  │
  │    · 解码延迟: ~5-20μs                              │
  │  · 如果一次 ECC 失败, 自动触发 Read Retry            │
  └──────────────────────────────────────────────────────┘

Level 2: Read Retry (读重试)
  ┌──────────────────────────────────────────────────────┐
  │  Read Retry 的原理:                                  │
  │  · NAND 使用不同的读参考电压重试读取                 │
  │  · TLC: 有 7 个读电压需要精确控制                    │
  │  · NAND 控制器提供 Read Retry 表 (vendor-specific)   │
  │  · 默认读电压 → 偏移 ±1 → ±2 → ...                  │
  │  · 最多重试: 40-80 次                                │
  │  · 重试成功: 记录该电压偏移 → 下次默认使用           │
  │  · 全部失败: 标记坏块                                │
  └──────────────────────────────────────────────────────┘

Level 3: 坏块管理 (Bad Block Management)
  ┌──────────────────────────────────────────────────────┐
  │  SSD 内部预留 ~2-10% 的备用块 (Spare Blocks)        │
  │                                                       │
  │  当 NAND Block 发生永久性故障:                        │
  │  1. 硬件的 ECC 引擎报告不可修正                       │
  │  2. FTL 标记该 Block 为 BAD                           │
  │  3. FTL 从 Spare Pool 中分配一个好块                  │
  │  4. 将坏块中的数据 (如果有) 搬到新块                  │
  │  5. 更新 FTL 映射表                                  │
  │  6. 更新 Bad Block Table (NAND 中的 BBT)             │
  │                                                       │
  │  当 Spare Pool 耗尽:                                 │
  │  · SSD 进入 "Read-Only" 模式                          │
  │  · 主机 NVMe 驱动检测到: Available Spare < Threshold  │
  │  · 触发 NVMe Critical Warning (需备份数据)           │
  └──────────────────────────────────────────────────────┘

Level 4: 固件崩溃恢复
  ┌──────────────────────────────────────────────────────┐
  │  SSD 主控固件也可能崩溃:                              │
  │                                                       │
  │  1. Watchdog 超时 → 硬件触发 CPU Reset               │
  │  2. Boot ROM 重新加载 PBL → 重新加载固件             │
  │  3. 固件检测到 Crash 日志 → 写入 NAND 的 Log Area    │
  │  4. 检测: 是否是"软崩溃" (固件 Bug)                  │
  │     还是"硬崩溃" (NAND 控制器异常)                   │
  │  5. 软崩溃: 恢复 NAND 状态 → 继续服务                │
  │  6. 硬崩溃: 标记 SSD 为故障 → 汇报 Fatal Status      │
  │                                                       │
  │  固件 A/B 镜像:                                      │
  │  · 如果当前固件 (A) 连续崩溃 N 次                    │
  │  · 自动切换到备份固件 (B)                            │
  │  · 启动后标记: "回滚到固件版本 B"                    │
  │  · 如果 B 也崩溃: 固态盘进入安全模式 (只读)         │
  └──────────────────────────────────────────────────────┘

Level 5: NVMe 控制器重置 (主机驱动侧)
  ┌──────────────────────────────────────────────────────┐
  │  主机驱动检测到 SSD 无响应:                           │
  │  · Admin Command Timeout (默认 60s)                  │
  │  · I/O Command Timeout                               │
  │  · Doorbell 写入后无 Completion 返回                  │
  │                                                       │
  │  恢复: NVMe Controller Reset:                        │
  │  1. 写 CC.EN = 0 (禁用控制器)                        │
  │  2. 等待 CSTS.RDY = 0 (超时: 10s)                    │
  │  3. 如果 CSTS.RDY 一直为 1 → SSD 完全卡死            │
  │     → PCIe DPC / Hot Reset / Slot Power Cycle        │
  │  4. 写 CC.EN = 1 (重新使能)                          │
  │  5. 等待 CSTS.RDY = 1                                │
  │  6. 重新 Admin Queue → Identify → 恢复 I/O           │
  └──────────────────────────────────────────────────────┘
```

---

## 第6章 GPU 初始化与故障恢复

### 6.1 GPU 供电与上电时序

GPU 的供电复杂度在所有芯片中最高——因为它同时有超大功率和严格的噪声要求：

```text
NVIDIA B200 GPU 供电域 (典型 AI 训练 GPU):

┌──────────────────────────────────────────────────────┐
│  12V 主电源 (PSU → 主板 VR → GPU)                    │
│      │                                                │
│  ┌───┴────────────────────────────────────────────────┐│
│  │  GPU 板卡 PMIC / VR 控制器                        ││
│  │                                                    ││
│  │  V域1: Vdd_gpu (0.7-1.0V) — 核心逻辑              ││
│  │  ├─ 所有 SM (Streaming Multiprocessors) 核心       ││
│  │  ├─ 最大电流: ~500-800A                           ││
│  │  ├─ 供电: 12-16 相 VR, 每相 60A                  ││
│  │  ├─ 电压精度: ±1% (对噪声极其敏感)                ││
│  │  └─ 功耗: ~400-700W (B200 TDP)                   ││
│  │                                                    ││
│  │  V域2: Vdd_hbm (1.2-1.35V) — HBM 供电            ││
│  │  ├─ HBM3e 堆叠 (8-Hi) 每层 1.2V                  ││
│  │  ├─ 每 HBM 栈 ~10-15W                            ││
│  │  ├─ 独立 LDO 去耦 (HBM 对电源噪声极其敏感)        ││
│  │  └─ 总 HBM 功耗: ~40-80W                         ││
│  │                                                    ││
│  │  V域3: Vdd_pll (0.9V) — PLL 模拟域               ││
│  │  ├─ SerDes PLL (PCIe + NVLink)                    ││
│  │  ├─ Memory PHY PLL (HBM PHY)                      ││
│  │  └─ 独立 LDO + 低噪声供电                        ││
│  │                                                    ││
│  │  V域4: Vdd_io (1.0V/1.8V) — I/O                  ││
│  │  ├─ NVLink SerDes PHY (1.0V)                      ││
│  │  ├─ PCIe SerDes PHY (1.0V)                        ││
│  │  ├─ HBM PHY (1.0V/1.8V)                           ││
│  │  └─ Management I2C/GPIO (1.8V)                   ││
│  │                                                    ││
│  │  V域5: Vaux (1.8V/3.3V) — 常开域                 ││
│  │  ├─ GPU VBIOS 寄存器 (S3 保留)                    ││
│  │  ├─ GPU 监控 (温度/电压)                          ││
│  │  └─ PCIe 配置空间 (D3cold 保留)                  ││
│  └────────────────────────────────────────────────────┘│
│                                                         │
│  上电时序 (NVIDIA GPU):                                 │
│  1. 12V 主电源 → GPU VR 开始工作                       │
│  2. Vaux 先上电 → VBIOS 常开域就绪                      │
│  3. Vdd_pll 上电 → PLL 锁定 (~100μs)                  │
│  4. Vdd_hbm 上电 → HBM PHY 可用                       │
│  5. Vdd_gpu 上电 → 核心逻辑复位释放                     │
│  6. Vdd_io 上电 → SerDes PHY 可用                      │
│  7. PERST# 释放 → PCIe 链路开始训练                     │
│                                                         │
│  (所有电压必须在 ~50ms 内达到稳态)                      │
└──────────────────────────────────────────────────────────┘
```

### 6.2 VBIOS / GPU 固件初始化

#### 6.2.1 VBIOS 功能与加载

```text
GPU VBIOS (Video BIOS) — 不仅仅是"显示 BIOS":

VBIOS 负责:
  · GPU 核心初始化 (频率/电压表)
  · PCIe 配置空间初始化
  · HBM/GDDR 内存训练
  · 风扇控制策略表
  · Power/Thermal Management 阈值
  · BOOT 显示 (如果是图形卡)

存储: SPI Flash (8-32MB), 通过 GPU SPI 控制器访问

加载流程:
  ┌──────────────────────────────────────────────────────┐
  │  GPU 上电后:                                         │
  │  1. GPU 内部 Boot ROM (~64KB)                        │
  │     · 初始化最小配置: Stack, Watchdog, PLL          │
  │     · 读取 SPI Flash → 加载 VBIOS 到 GPU SRAM      │
  │     · 验证 VBIOS 签名 (NVIDIA Secure Boot)          │
  │     · 跳转到 VBIOS 入口                              │
  │                                                       │
  │  2. VBIOS 初始化                                      │
  │     · 读取 GPU Strapping Pins (配置板卡类型/功率)    │
  │     · 初始化 GPU PMIC (电压/频率配置表)              │
  │     · HBM/GDDR 训练 (见 6.3)                        │
  │     · 初始化 PCIe EP Core                            │
  │     · 配置温度传感器/风扇曲线                         │
  │     · 初始化 GPU 核心频率/电压查找表 (P-State)       │
  │                                                       │
  │  3. VBIOS 完成后 → GPU 进入 "BIOS Handoff" 状态     │
  │     · 等待 Host PCIe 枚举                            │
  │     · 等待 OS GPU 驱动加载 (nvidia.ko/nvlddmkm.sys)  │
  └──────────────────────────────────────────────────────┘
```

#### 6.2.2 GPU 固件架构 (Modeset / PMU / SEC2)

Modern GPU 内部运行多个独立的固件：

```text
NVIDIA GPU (Blackwell) 的固件架构:

┌─────────────────────────────────────────────────────────┐
│  GPU Die 内部运行的固件:                                 │
│                                                         │
│  1. PMU (Power Management Unit) Firmware                │
│  · 运行在 GPU 内部的独立微控制器                         │
│  · 职责: 动态电压/频率调谐 (DVFS)                       │
│  · 温度监控 + 风扇控制                                  │
│  · 电源状态管理 (P0-P12)                               │
│  · 独立于 GPU Core — PMU 自己有独立的 SRAM + ROM       │
│                                                         │
│  2. SEC2 (Security Processor) Firmware                  │
│  · GPU 安全协处理器                                     │
│  · 密钥管理 + 加密/解密加速                             │
│  · 负责: Secure Boot 链, 固件签名验证                    │
│  · 管理 GPU 内部的内存隔离                               │
│                                                         │
│  3. FLCN (Falcon) Firmware 系列                        │
│  · GPU 内部的通用微控制器 (Falcon Core)                 │
│  · 多种用途:                                            │
│    - Display Engine FW (显示输出管理)                   │
│    - Video Engine FW (视频编解码)                       │
│    - NVENC (编码) FW                                    │
│    - Optical Flow FW                                    │
│    - GSP (GPU System Processor, Blackwell 新增)        │
│                                                         │
│  4. GSP (GPU System Processor) — Blackwell 新引入      │
│  · 替代部分 nvidia.ko 驱动的功能                        │
│  · 运行在 GPU 内部的 RISCV 核心                         │
│  · 处理: PCIe 配置空间访问, 电源管理, 错误处理          │
│  · 目标: 减少 GPU 驱动对内核的依赖                       │
│  · 可以独立更新 (不依赖驱动版本)                         │
│                                                         │
│  固件加载顺序:                                          │
│  Boot ROM → VBIOS → PMU FW → SEC2 FW → FLCN FW → GSP  │
│  (下级固件依赖上级固件初始化好的资源)                    │
└─────────────────────────────────────────────────────────┘
```

### 6.3 显存初始化（HBM / GDDR 训练）

HBM 内存训练的复杂度远超普通 DDR——因为它涉及 TSV (硅通孔) 和多层堆叠：

#### 6.3.1 HBM 初始化流程

```text
HBM3e (B200: 8-Hi × 8 栈 × 1024-bit) 初始化:

┌──────────────────────────────────────────────────────────┐
│  HBM 初始化是 GPU 启动中最复杂的部分之一:                 │
│                                                         │
│  Step 1: HBM PHY 供电 + PLL 锁定                        │
│  · 每个 HBM 栈的 PHY 需要独立的 PLL                     │
│  · 锁定时间: ~100-200μs                                │
│  · 锁定后 PHY 时钟稳定                                  │
│                                                         │
│  Step 2: HBM 内部初始化                                 │
│  · 发送 HBM Reset 命令 (通过 TSV 接口)                  │
│  · 设置 HBM Mode Register:                              │
│    - Row/Column Address Mux                             │
│    - Burst Length (HBM3e: BC8/BC16)                    │
│    - Read/Write Latency                                 │
│    - Temperature Controlled Refresh (TCR)               │
│    - Pseudo Channel Mode                               │
│  · ZQ Cal (256 阶阻抗校准)                             │
│  · 每颗 HBM 独立完成                                    │
│  · 8 栈 × 每栈 ~2ms = ~16ms                            │
│                                                         │
│  Step 3: HBM PHY Training (最耗时)                     │
│  ┌───────────────────────────────────────────────────┐  │
│  │  HBM PHY Training (每个栈独立进行):                 │  │
│  │                                                     │  │
│  │  a) Write Leveling                                  │  │
│  │     · 校准 DQS 与 CK 的相位差                       │  │
│  │     · 按 byte lane 独立进行                          │  │
│  │     · HBM3e: 1024-bit = 128 byte lanes × 8 bits    │  │
│  │     · 每 byte lane 耗时 ~100μs                      │  │
│  │     · 总计: 128 × 100μs = ~12.8ms                  │  │
│  │                                                     │  │
│  │  b) Read DQS Training                               │  │
│  │     · HBM 返回 DQS 信号 → GPU PHY 找到采样窗口     │  │
│  │     · 每个 byte lane 独立                            │  │
│  │     · 总计: ~10ms                                   │  │
│  │                                                     │  │
│  │  c) DQ/DQS Deskew                                   │  │
│  │     · 精确调整每个 DQ 信号相对于 DQS 的延时          │  │
│  │     · 8-bit per byte lane 独立调整                   │  │
│  │     · 步进: ~5ps                                    │  │
│  │     · 总计: ~20ms                                   │  │
│  │                                                     │  │
│  │  d) Vref Training                                   │  │
│  │     · 调整 DQ 的参考电压                             │  │
│  │     · 找到最优采样点 (最大化眼高)                    │  │
│  │     · 总计: ~10ms                                   │  │
│  │                                                     │  │
│  │  e) AC Timing Training                              │  │
│  │     · 校准 CA (命令/地址) 总线的建立时间              │  │
│  │     · 总计: ~5ms                                    │  │
│  │                                                     │  │
│  │  总计: 每栈 ~60ms × 8 栈 = ~480ms                  │  │
│  │  (但可以并行训练, 实际 ~60-100ms)                   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  Step 4: Memory Test                                    │
│  · 写入 0x5A5A → 读取验证                               │
│  · 写入 0xA5A5 → 读取验证 (互补模式)                   │
│  · 写全 0 → 写全 1 → 写入 Walking 0/1                  │
│  · 检测 bad bit → 触发 HBM 内建修复 (Post-Package Repair)│
│  · 如果有 bad bit:                                      │
│    - HBM 自动用备用 Row/Column 替换 (对 GPU 透明)       │
│    - 如果备用耗尽 → GPU 标记该 "显存区域" 不可用       │
│  · 总计: ~20-50ms                                      │
│                                                         │
│  HBM 初始化总时间: ~150-300ms                           │
└──────────────────────────────────────────────────────────┘
```

#### 6.3.2 HBM 训练失败处理

```text
HBM 训练失败的恢复策略:

1. 降速重训
   · HBM3e 默认: 6.4 Gbps
   · 失败 → 降到 5.6 Gbps → 5.2 Gbps → 4.8 Gbps
   · 每一步包含完整的 PHY Training
   · 代价: 每降速一次 + ~100ms (需要重新校准)

2. 降宽
   · 默认: 8-Hi, 1024-bit
   · 关闭失败通道 → 使用剩余好通道
   · 但 HBM 必须全通道初始化 (无部分通道模式)
   · 所以: HBM 栈要么全好, 要么全坏 → 替换整颗 HBM

3. HBM 栈替换
   · B200 的 8 个 HBM 栈: GPU 到 HBM 的互联是独立的
   · 某一栈训练失败 → VBIOS 标记该栈为 "BAD"
   · GPU 用剩余的 HBM 栈工作 (容量下降, 但不完全死)
   · 8→7: 容量降 12.5%, 带宽降 12.5%
   · 如果关键栈 (stack 0) 损坏 → GPU 完全不可用
```

### 6.4 PCIe 链路初始化

GPU 的 PCIe 链路训练与标准 PCIe EP 一致，但有一个关键差异——NVLink 链路训练：

```text
GPU 的 PCIe + NVLink 双协议链路训练:

PCIe (Host 通信):
  与 CPU Root Port 标准的 PCIe LTSSM
  · B200: PCIe Gen5 ×16 (64 GB/s)
  · 训练在 PERST# 释放后自动进行
  · 不需要 GPU 驱动干预——LTSSM 是硬件状态机

NVLink (GPU 间互联):
  · B200: NVLink 5.0, 18 链路 × 200 GT/s
  · 训练比 PCIe 更灵活 (NVIDIA 私有):
    · 链路宽度: 动态分配 (根据可用链路数)
    · 速率固定: 200 GT/s (不支持协商降速)
    · 没有 PERST# 等效信号

NVLink 训练步骤:
  ┌─────────────────────────────────────────────────────┐
  │  1. GPU 内部 NVLink PHY 初始化                       │
  │     · SerDes PLL 锁定                               │
  │     · TX/RX 校准                                     │
  │     · RS-FEC 引擎初始化                              │
  │                                                       │
  │  2. NVLink 链路发现                                    │
  │     · 每个 Link 的 TX 发出 "Presence Detect" 信号    │
  │     · RX 检测对端是否存在 (是否连接到另一个 GPU)     │
  │     · 检测拓扑: 直连 NVSwitch / 直连 GPU             │
  │                                                       │
  │  3. Link 训练                                         │
  │     · 位锁定: TX 发送训练序列 → RX 找位对齐         │
  │     · 块锁定: 找到 128-bit 的块边界                   │
  │     · Lane Deskew: 4 sub-lanes 对齐                   │
  │     · PHY Equalization: TX 调整 FFE → RX 锁定 CTLE   │
  │                                                       │
  │  4. 链路聚合                                           │
  │     · 将所有训练的 Link 聚合成统一的 NVLink 接口      │
  │     · 建立链路级信用流控                                │
  │     · 通知 GPU 驱动 (NCCL/RDMA 可用)                  │
  │                                                       │
  │  5. 总时间: ~10-50ms (取决于链路数)                  │
  └─────────────────────────────────────────────────────┘
```

### 6.5 计算子系统初始化

```text
GPU 计算子系统 (SM / Tensor Core) 初始化:

GPU 完成显存训练 + PCIe 训练后, 还需要初始化计算核心:

┌─────────────────────────────────────────────────────────┐
│  Step 1: SM (Streaming Multiprocessor) 初始化           │
│  · 每个 SM 的 L1/Shared Memory 清零                     │
│  · 寄存器文件初始化                                      │
│  · Wrapper (线程调度器) 初始化                           │
│  · SM 数量: B200 ~132 SM                               │
│  · 每个 SM 独立完成                                      │
│  · 时间: ~1-2ms (全并行)                               │
│                                                         │
│  Step 2: Tensor Core 初始化                              │
│  · Tensor Core 是 SM 内的专用矩阵计算单元                │
│  · 初始化: 加载常量表, 校准模拟计算路径                    │
│  · Tensor Core 不需要特殊校准 (纯数字逻辑)               │
│                                                         │
│  Step 3: 内存子系统初始化                                │
│  · L2 Cache 初始化 (B200: ~80MB)                        │
│  · L2 Cache ECC 初始化 (所有 L2 行标记为 Invalid)       │
│  · Memory Partition 初始化                               │
│                                                         │
│  Step 4: 驱动接管                                        │
│  · OS 加载 nvidia.ko / nvlddmkm.sys                     │
│  · 驱动初始化 CUDA 运行时环境                             │
│  · 分配 GPU 上下文 (Channel)                             │
│  · 提交 GPU 任务: F32 矩阵乘法 → 验证计算能力            │
│  · 完成 → GPU 进入 "Ready" 状态                          │
└─────────────────────────────────────────────────────────┘
```

### 6.6 监控子系统：温度 / 电压 / 功耗 / ECC

GPU 拥有最复杂的监控子系统之一：

```text
GPU 监控子系统 (B200 Blackwell):

温度监控:
  ┌──────────────────────────────────────────────────────┐
  │  GPU Die 内置 ~20+ 温度传感器:                       │
  │  · Core Sensor (x4): SM 群组温度                     │
  │  · HBM Sensor (x8): 每 HBM 栈温度                   │
  │  · Memory PHY Sensor (x4): PHY 区域温度              │
  │  · SerDes Sensor (x2): NVLink/PCIe PHY 温度          │
  │  · VR Sensor (x2): GPU VR/VID 温度                   │
  │  · Hotspot Sensor: 芯片最热点                         │
  │                                                       │
  │  阈值 (可编程):                                       │
  │  · Tj_max: 95-105°C (取决于工艺)                    │
  │  · Throttle: 85°C (开始降频)                         │
  │  · Warning: 75°C (告警)                              │
  │  · Shutdown: 105°C (紧急关机)                        │
  └──────────────────────────────────────────────────────┘

电压/电流/功耗监控:
  ┌──────────────────────────────────────────────────────┐
  │  · VMON: 各电压域独立监控                             │
  │  · IMON: 各域电流传感器 (±3% 精度)                   │
  │  · Power Sensor: GPU 总功耗 + HBM 功耗               │
  │  · 功耗采样率: ~1ms                                  │
  │  · 报告: nvidia-smi 显示 (通过 PMU FW)               │
  │                                                       │
  │  GPU 功耗限制:                                        │
  │  · PL1 (Long Duration): ~700W (B200)                 │
  │  · PL2 (Short Duration): ~800W (~10ms burst)         │
  │  · PL3 (Peak): ~900W (~1ms)                          │
  │  · 超过 PL1 → PMU 逐步降频                           │
  │  · 超过 PL2 → PMU 快速降频 (<1ms 响应)              │
  │  · 超过 PL3 → 硬件门控 (Power Brake, <1μs 响应)    │
  └──────────────────────────────────────────────────────┘

ECC 监控 (HBM + L2 Cache):
  ┌──────────────────────────────────────────────────────┐
  │  HBM ECC (B200 支持 HBM3e ECC):                     │
  │  · SECDED (Single Error Correct, Double Error Detect)│
  │  · 每 32-bit 数据 + 8-bit ECC                       │
  │  · 可修正错误: 硬件自动修正, 寄存器计数              │
  │  · 不可修正错误: 触发 GPU XID (nv-fatal)            │
  │  · 计数器: 驱动可读 (nvidia-smi -q)                  │
  │                                                       │
  │  L2 Cache ECC:                                        │
  │  · 每 Cache Line (128B) 有 8-byte ECC               │
  │  · CE: 硬件修正 + 计数                                │
  │  · UE: 触发 MCE → GPU 挂起                           │
  └──────────────────────────────────────────────────────┘
```

### 6.7 GPU 异常检测与恢复

#### 6.7.1 GPU XID 错误系统

```text
NVIDIA GPU 的错误报告: XID (eXtended IDentifier)

XID 是 NVIDIA 驱动定义的错误代码, 通过 nvidia-smi 或 dmesg 输出:

常见 XID:
  ┌───────┬──────────────────────────────────────────────┐
  │ XID   │ 含义                                         │
  ├───────┼──────────────────────────────────────────────┤
  │ 13    │ HBM CE 超过阈值 → GPU 降频                   │
  │ 31    │ 温度过高 → GPU 降频/关机                      │
  │ 43    │ GPU 挂起 → TDR (超时检测与恢复)              │
  │ 45    │ GPU 不再响应 PCIe → SBR (Secondary Bus Reset)│
  │ 48    │ NVLink AER 错误 → NVLink 链路重训练           │
  │ 56    │ PCIe AER 错误 → DPC 或链路重训               │
  │ 61    │ Power Brake 触发 → 电源过载                  │
  │ 62    │ GPU 内部固件崩溃 → PMC Reset                 │
  │ 63    │ HBM ECC UE → 不可修正内存错误                │
  │ 64    | GPU 掉 TDR 时间线 → 驱动判断是否重置        │
  │ 69    │ GPU 固件集成的错误处理事件                    │
  │ 79    │ NVLink 链路训练失败 → 链路不可用              │
  │ 94    │ 软件 Stall 超时 → GPU 被硬件 Watchdog 复位   │
  │ 109   │ GPU 内部总线错误 → FLR 或 SBR                │
  │ 119   │ GPU 过热关机                                  │
  │ 120   │ GPU 供电不足 → 降频或关机                     │
  └───────┴──────────────────────────────────────────────┘
```

#### 6.7.2 GPU 多层次恢复

```text
Level 1: HBM ECC 修正 (硬件自动, 透明)
  ┌──────────────────────────────────────────────────────┐
  │  HBM CE: 硬件 ECC 引擎在读取时自动修正               │
  │  · 对 SM/CUDA 程序完全透明                           │
  │  · 仅驱动记录计数 (nvidia-smi 可查看)                 │
  │  · 如果 CE 计数增长过快 → 驱动触发内存 Scrubbing     │
  └──────────────────────────────────────────────────────┘

Level 2: NVLink 链路恢复 (Link Level)
  ┌──────────────────────────────────────────────────────┐
  │  NVLink AER 检测到 CRC 错误:                         │
  │  1. NVSwitch 或 GPU 的 NVLink PHY 检测到 CRC 错     │
  │  2. 硬件自动: FLIT 级重传 (类似 PCIe Gen6)          │
  │  3. 如果重传成功 → 透明恢复                          │
  │  4. 如果持续失败 → NVLink 链路重训练                  │
  │  5. 重训后仍然失败 → 关闭该链路 (带宽降级)          │
  │                                                       │
  │  影响: 18 链路中坏 N 条 → 带宽下降 N/18             │
  │  驱动需重新配置 NCCL 通信拓扑                         │
  └──────────────────────────────────────────────────────┘

Level 3: GPU TDR (Timeout Detection and Recovery)
  ┌──────────────────────────────────────────────────────┐
  │  这是 GPU 恢复最典型的机制:                           │
  │                                                       │
  │  触发条件: GPU 在 N 秒内未完成某个任务                │
  │  (默认: ~5-10s, 可通过 nvidia-smi 调整)             │
  │                                                       │
  │  TDR 流程:                                            │
  │  1. OS 调度器发现 GPU 无响应                          │
  │     (GPU 未完成一个 Kernel 执行)                      │
  │  2. OS 通知 nvidia.ko 驱动                           │
  │  3. 驱动触发 GPU FLR (Function Level Reset)          │
  │     ┌───────────────────────────────────────────┐    │
  │     │  FLR:                                     │    │
  │     │  · 写 PCIe FLR 寄存器 (PCI Express Cap)  │    │
  │     │  · GPU 内部: 重置所有 SM + L1/L2 Cache   │    │
  │     │  · GPU 内部: 保持 HBM 内容不丢失          │    │
  │     │  · GPU 内部: 保持 PCIe 配置空间           │    │
  │     │  · GPU 内部: PMU 不重置 (保持电源状态)    │    │
  │     │  · 完成时间: ~100ms                       │    │
  │     └───────────────────────────────────────────┘    │
  │  4. 驱动等待 FLR 完成 (约 2s)                        │
  │  5. 驱动重新初始化 GPU 状态:                          │
  │     · 重新加载 CUDA 上下文                            │
  │     · 重建 GPU 页表                                    │
  │     · 恢复显存分配                                    │
  │  6. 继续未完成的任务                                   │
  │                                                       │
  │  如果 FLR 后 GPU 仍然挂起:                            │
  │  → 升级到 SBR (Secondary Bus Reset, 见 Level 4)     │
  │                                                       │
  │  TDR 成功概率: ~70-80% (多数是瞬时故障)              │
  │  TDR 影响: ~2-5s 应用不可用                          │
  └──────────────────────────────────────────────────────┘

Level 4: SBR (Secondary Bus Reset) / Hot Reset
  ┌──────────────────────────────────────────────────────┐
  │  SBR = PCIe Secondary Bus Reset:                     │
  │  · 比 FLR 更强的复位                                  │
  │  · 复位 GPU 整个 PCIe Function (包括配置空间)         │
  │  · 保持 GPU 供电 (不丢显存)                           │
  │                                                       │
  │  流程:                                                 │
  │  1. OS/驱动写 Bridge Control: Secondary Bus Reset     │
  │  2. GPU 看到: LTSSM 进入 Hot Reset 状态              │
  │     · 复位 PCIe 配置空间 → 寄存器回到默认值          │
  │     · 不复位 GPU 内部逻辑 (SM/Memory 保持)           │
  │  3. 热复位持续 ~50ms (标准要求)                       │
  │  4. 复位结束, GPU 重新开始 LTSSM 训练                 │
  │  5. PCIe 链路重新建立                                 │
  │  6. OS 重新枚举 GPU (重新分配 BAR)                    │
  │  7. 驱动重新初始化 (但显存内容可保留)                  │
  │                                                       │
  │  如果 SBR 也失败:                                     │
  │  → 升级到系统级: Warm Reset / Power Cycle            │
  └──────────────────────────────────────────────────────┘

Level 5: GPU 断电重启 (Cold Reset)
  ┌──────────────────────────────────────────────────────┐
  │ 由 BMC 或主板电路执行:                               │
  │                                                       │
  │  1. BMC 拉低 GPU 12V 使能 (或通过 GpuPowerGood)      │
  │  2. 保持断电 ~5s (确保电容完全放电)                  │
  │  3. 重新供电 → GPU 完全重新初始化:                    │
  │     · VBIOS 重新加载                                  │
  │     · HBM 重新训练 (需要 ~300ms)                     │
  │     · PCIe 重新训练                                   │
  │     · NVLink 重新训练                                 │
  │     · 所有固件重新加载                                │
  │  4. 驱动重新初始化                                     │
  │  5. 显存内容全部丢失                                   │
  │                                                       │
  │  影响: ~10-30s GPU 不可用                             │
  │  显存内容丢失 → 需要应用/框架重新加载模型             │
  └──────────────────────────────────────────────────────┘

Level 6: GPU 永久隔离
  ┌──────────────────────────────────────────────────────┐
  │ 如果多次 Cold Reset 后 GPU 仍无法工作:                │
  │ 1. BMC 通知管理平台: "GPU slot N 永久故障"          │
  │ 2. 标记 GPU 为 "RMA Required"                        │
  │ 3. NCCL/框架重新配置拓扑: 跳过此 GPU                │
  │ 4. 训练任务: 使用其他 GPU 继续 (需要检查点恢复)     │
  └──────────────────────────────────────────────────────┘
```

---

## 第7章 跨芯片协同与系统级恢复

### 7.1 整机上电时序：CPU→BMC→PCIe→GPU 的依赖链

```text
AI 服务器 (8×GPU) 的整机启动时序:

时间线 (典型值):
  0ms      PSU 供电 (+12V SB) → BMC 启动
  50ms     BMC Boot ROM → BMC 固件加载
  100ms    BMC 固件运行 → 初始化 SDR/FRU
  200ms    BMC 使能 CPU 供电 VR → 发出 VR_EN
  250ms    CPU 各组电压上升到稳态
  300ms    CPU PLL 锁定
  350ms    BIOS SEC/PEI 阶段开始 → 内存训练
  500ms    DDR5 内存训练完成
  800ms    BIOS DXE 阶段 → PCIe 枚举开始
  850ms    GPU 检测到 PERST# 释放 → 开始 LTSSM
  950ms    GPU-PCIe 训练完成 → GPU 被枚举
  1000ms   BIOS 枚举完所有 PCIe 设备
  1100ms   OS 加载 → GPU 驱动加载 (nvidia.ko)
  1200ms   GPU 驱动初始化 → NVLink 训练
  1300ms   NVLink 聚合完成 → NCCL 可用
  1400ms   CUDA Runtime 初始化完成
  1500ms   GPU 可用 → 开始运行训练任务

各芯片依赖关系:
  BMC ⟹ CPU (BMC使能CPU VR)
  CPU ⟹ PCH (CPU通过DMI连接PCH)
  CPU ⟹ PCIe Switch (CPU通过PCIe Root Port连接Switch)
  PCIe Switch ⟹ GPU (PERST# 由主板控制)
  GPU ⟹ NVSwitch (Grace-Hopper: NVSwitch 须先于 GPU 初始化)
```

### 7.2 故障传播路径与隔离策略

```text
故障传播 (由近到远):

GPU 故障 → PCIe 链路 → PCIe Switch → CPU → OS → 应用

每个层级都可以选择:
  a) 向上报告 (传播故障)
  b) 本地恢复 (隔离故障)

隔离策略:

┌──────────────────────────────────────────────────────────┐
│  NVLink 链路故障:                                        │
│  隔离边界: NVLink 链路                                   │
│  恢复: 链路重训练 (Level 1)                             │
│  传播: 不传播 (Switch 或 GPU 内部处理)                  │
│                                                         │
│  GPU PCIe AER 错误:                                      │
│  隔离边界: PCIe Downstream Port (DPC 隔离)              │
│  恢复: DPC 触发 + SBR (Level 3-4)                      │
│  传播: 如果 DPC 恢复失败 → PCIe 枚举失败 → OS 报错     │
│                                                         │
│  GPU 过热:                                               │
│  隔离边界: GPU 本身                                      │
│  恢复: 降频 → 关机 (Level 5)                            │
│  传播: 不影响其他 GPU (供电/散热共享则可能有影响)       │
│                                                         │
│  CPU MCA UE:                                             │
│  隔离边界: 如果可隔离 → 单个 Core Offline                │
│  恢复: Core Offline → 内存页隔离                          │
│  传播: 不可隔离 → System PANIC                            │
│                                                         │
│  SSD FTL 损坏:                                           │
│  隔离边界: SSD 本身                                      │
│  恢复: FTL 重建 → NVMe 重置                              │
│  传播: 如果 FTL 不可恢复 → SSD 丢失 → 文件系统报错      │
└──────────────────────────────────────────────────────────┘
```

### 7.3 系统级恢复方案：从链路重训到整机复位

完整的恢复决策框架：

```text
┌──────────────────────────────────────────────────────────┐
│  故障识别 (Detection):                                   │
│  · CPU: MCA/CMCI/PECI/CATERR                            │
│  · PCIe Switch: AER/DPC/CRC/Port Status                 │
│  · USB: xHCI Event Ring / Port Change / LFPS            │
│  · SSD: NVMe Error Log / Async Event / Completion Error  │
│  · GPU: XID/nvidia-smi/dmesg/DCGM                      │
│                                                         │
│  BMC 汇总所有来源 → 分析"故障影响范围"                   │
│                                                         │
│  ┌──────────────────────────────────────────────────────┐│
│  │  恢复决策 (由 BMC/Orchestrator 执行):                 ││
│  │                                                       ││
│  │  if (故障为瞬时性 && 影响为单链路):                    ││
│  │     执行 Level 1: 链路重训练                          ││
│  │     例: PCIe Recovery, NVLink Retrain, USB Port Reset ││
│  │                                                       ││
│  │  elif (故障为永久性 && 影响为单功能):                  ││
│  │     执行 Level 2: 功能重启                            ││
│  │     例: GPU FLR, NVMe Controller Reset, CPU Core Off  ││
│  │                                                       ││
│  │  elif (故障影响多个功能/端口):                         ││
│  │     执行 Level 3: 局部芯片复位                         ││
│  │     例: PCIe Switch Port Remap, GPU Cold Reset        ││
│  │                                                       ││
│  │  elif (故障影响整颗芯片):                              ││
│  │     执行 Level 4: 全芯片复位                           ││
│  │     例: PCIe SBR, CPU Warm Reset, PCH Reset          ││
│  │                                                       ││
│  │  elif (多芯片级联故障):                                ││
│  │     执行 System Reset: BMC 拉低 SIO RST              ││
│  │     例: 整机 Warm Reboot                              ││
│  │                                                       ││
│  │  elif (故障影响供电/散热):                             ││
│  │     执行 Emergency Shutdown: BMC 拉低 PSU Inhibit    ││
│  │     例: GPU 短路, CPU 过热, 液冷漏液                  ││
│  └──────────────────────────────────────────────────────┘│
│                                                           │
│  恢复后验证 (Verification):                               │
│  · 链路训练成功? (LTSSM L0)                               │
│  · 寄存器自检通过? (Read-after-Write)                     │
│  · FEC/BER 恢复基线?                                     │
│  · 应用层: NCCL 通信测试 / CUDA 简单 Kernel               │
│  · 如果验证失败 → 升级恢复级别                            │
│                                                           │
│  日志记录 (Logging):                                      │
│  · BMC 写入 SEL (System Event Log)                       │
│  · 记录: 芯片类型, 错误类型, 恢复级别, 恢复结果, 时间戳  │
│  · 如果恢复失败 → 标记 "需人工介入"                      │
└──────────────────────────────────────────────────────────┘
```

### 7.4 恢复决策树

单颗 GPU 故障场景的完整恢复决策流：

```text
GPU XID 43 (GPU Hang) 出现:
  │
  ├─1. 驱动尝试 GPU FLR (Function-Level Reset)
  │   ├─ 成功 ⟹ GPU 恢复, 任务重发 (~2-5s)
  │   └─ 失败 ⟹ 
  │
  ├─2. BMC 尝试 SBR (Secondary Bus Reset, PCIe Hot Reset)
  │   ├─ 成功 ⟹ 驱动重初始化, 显存保留 (~10s)
  │   └─ 失败 ⟹
  │
  ├─3. BMC 尝试 GPU Cold Reset (断电再上电)
  │   ├─ 成功 ⟹ HBM 重训练 + 驱动重初始化 (~30s)
  │   └─ 失败 ⟹
  │
  ├─4. BMC 判断 GPU 永久故障
  │   ├─ 标记 GPU Slot BAD
  │   ├─ 通知 Orchestrator: 从此 GPU 排走负载
  │   ├─ 通知管理员: RMA 该 GPU
  │   └─ 系统以 N-1 卡继续运行
  │
  其他因子影响决策:
  · 如果任务有 Checkpoint (每 10min): 从 Checkpoint 恢复
  · 如果无 Checkpoint: 放弃该任务 → 重训
  · 如果多 GPU 同时故障: 可能机柜级故障 → 整机排查
  · 如果 GPU 温度正常但反复 Hang: 可能是驱动 Bug → 回滚驱动
```

---

## 附录A：各芯片初始化关键时序参数表

| 芯片类型 | 供电稳定 | PLL 锁定 | 固件加载 | 内存训练 | 链路训练 | 总初始化 | 主要耗时项 |
|:---------|:-------:|:--------:|:--------:|:--------:|:--------:|:--------:|:----------|
| **CPU (Xeon 6)** | ~50ms | ~100μs | ~200ms | ~100-500ms | ~100ms | ~500ms-1s | 内存训练 |
| **PCIe Switch** | ~20ms | ~100μs | ~100-500ms | N/A | ~50-100ms | ~200ms-1s | 固件加载 |
| **USB xHCI** | ~10ms | ~50μs | ~10ms | N/A | ~10-100ms | ~30-200ms | 链路训练 |
| **SSD 主控** | ~10ms | ~50μs | ~100-500ms | N/A | ~50-100ms | ~200ms-1s | FTL 重建 |
| **GPU (B200)** | ~50ms | ~200μs | ~200ms | ~150-300ms | ~50-100ms | ~500ms-1s | HBM 训练 |
| **NVSwitch** | ~20ms | ~100μs | ~100-200ms | N/A | ~10-50ms | ~200-300ms | NVLink 训练 |

## 附录B：固件加载对比表

| 维度 | CPU | PCIe Switch | SSD 主控 | GPU |
|:-----|:---|:-----------|:---------|:---|
| **存储介质** | SPI Flash (8-32MB) | SPI Flash (4-16MB) | NAND Reserved Area | SPI Flash (8-32MB) |
| **Boot ROM 大小** | ~128KB (Cache) | ~32-64KB | ~32-64KB | ~64KB |
| **Boot ROM 位置** | CPU Die 内部 ROM | ASIC 内部 ROM | 主控 Die 内部 ROM | GPU Die 内部 ROM |
| **安全启动** | Intel Boot Guard | 可选 (Secure Boot) | 可选 (OEM 实现) | NVIDIA Secure Boot |
| **签名算法** | RSA 2048/3072 | RSA 2048 | RSA/ECC 256 | ECDSA |
| **固件大小** | ~8-32MB (UEFI) | ~1-4MB | ~1-4MB | ~4-8MB |
| **双镜像支持** | ✅ BIOS A/B | 可选 | 几乎所有 | ✅ VBIOS A/B |
| **In-Band 升级** | ✅ 通过 OS | ✅ 通过 PCIe BAR | ✅ 通过 NVMe FW Download | ✅ 通过 nvidia-smi |
| **OOB 升级** | ✅ BMC 通过 SPI | ✅ BMC 通过 SMBus | ✅ 通过 NVMe-MI | ✅ BMC 通过 I2C |
| **升级失败回滚** | ✅ 自动回滚 | ✅ 自动回滚 | ✅ 自动回滚 | ✅ 自动回滚 |
| **固件崩溃恢复** | Watchdog + BMC | Watchdog + 硬件FSM | Watchdog + Boot ROM | Watchdog + PMU |

## 附录C：关键术语表

| 缩写 | 全称 | 说明 |
|:-----|:-----|:------|
| **AER** | Advanced Error Reporting | PCIe 扩展错误报告能力 |
| **ASPM** | Active State Power Management | PCIe 链路电源管理 |
| **BAR** | Base Address Register | PCIe 设备地址空间配置 |
| **BMC** | Baseboard Management Controller | 基板管理控制器 |
| **CAR** | Cache-as-RAM | 用 CPU Cache 做临时内存 (内存初始化前) |
| **CATERR** | Catastrophic Error | CPU 致命错误信号 |
| **CDR** | Clock Data Recovery | 时钟数据恢复 (SerDes RX) |
| **CE** | Correctable Error | 可修正错误 |
| **CMCI** | Corrected Machine Check Interrupt | CPU 可修正错误中断 |
| **DPC** | Downstream Port Containment | PCIe 端口故障隔离 |
| **ECC** | Error Correcting Code | 纠错码 |
| **FLR** | Function-Level Reset | PCIe 功能级复位 |
| **FTL** | Flash Translation Layer | SSD 闪存转换层 (LBA→PBA) |
| **GSP** | GPU System Processor | Blackwell GPU 系统处理器 |
| **HBM** | High Bandwidth Memory | 高带宽内存 (GPU 显存) |
| **LDPC** | Low-Density Parity-Check | NAND 使用的纠错码 |
| **LFPS** | Low Frequency Periodic Signaling | USB 3.0 链路训练信令 |
| **LTSSM** | Link Training and Status State Machine | PCIe 链路训练状态机 |
| **MCA** | Machine Check Architecture | CPU 硬件错误检测架构 |
| **MCE** | Machine Check Exception | CPU 硬件致命异常 |
| **NVLink** | NVIDIA GPU 高速互联 | 私有 GPU 间互联 |
| **PBL** | Primary Boot Loader | 芯片一级引导加载器 |
| **PECI** | Platform Environment Control Interface | Intel CPU-BMC 通信接口 |
| **PERST** | PCIe Reset | PCIe 复位信号 |
| **PLL** | Phase-Locked Loop | 锁相环 (时钟发生器) |
| **PLP** | Power Loss Protection | SSD 掉电保护 |
| **PMU** | Power Management Unit | GPU 电源管理单元 |
| **POR** | Power-On Reset | 上电复位 |
| **SBR** | Secondary Bus Reset | PCIe 二级总线复位 |
| **SEL** | System Event Log | BMC 系统事件日志 |
| **SM** | Streaming Multiprocessor | GPU 计算核心单元 |
| **SMI** | System Management Interrupt | CPU 系统管理中断 |
| **TDR** | Timeout Detection and Recovery | GPU 超时检测与恢复 |
| **TSV** | Through-Silicon Via | 硅通孔 (HBM 层间互联) |
| **UE** | Uncorrectable Error | 不可修正错误 |
| **VBIOS** | Video BIOS | GPU 核心固件 |
| **VR** | Voltage Regulator | 电压调节器 |
| **xHCI** | eXtensible Host Controller Interface | USB 3.x 主机控制器标准 |
| **XID** | Extended IDentifier | NVIDIA GPU 错误代码 |

---

> **创建**: 2026-06-25 | **版本**: v1.0
> 
> **引用说明**: 本文内容综合自 PCI-SIG Base Spec, UEFI PI Spec, NVMe Spec, NVIDIA GPU 公开文档, xHCI Spec, OpenBMC 源码, Linux 内核 MCA 子系统和大量芯片厂商技术文档。具体引用见各关联文档。
