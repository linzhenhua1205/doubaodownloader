# 网络 L1 物理层知识体系全景：标准协议、调制技术、介质与产品实现

> **元信息**: v1.0 | 深度分析 | 覆盖范围: L1 分层模型、物理介质、调制编码、IEEE 802.3/OIF/IBTA/PCI-SIG 标准族、光模块与电芯片产品、SI 测试、AI 集群 L1 工程实践
> **版本**: v1.0
> **日期**: 2026-08-19
> **核心问题**: 网络 L1 物理层有哪些标准协议、调制技术、介质与产品实现？各代际参数与演进路线如何？
> **适用范围**: 服务器/AI 基础设施网络架构师、互联硬件规划、光模块/线缆选型、SI 设计与测试
> **创建**: 2026-08-19 | 参考: IEEE 802.3 工作组官网(2026-08-06)、OIF 官网、NVIDIA 官网、《单通道400G以太网物理层白皮书》(2026-04)、OFC 2026 前瞻调研
>
> **概要**: 建立网络 L1 物理层完整知识体系：PHY 子层模型（PCS/PMA/PMD/MDI）、铜/光介质与连接器、NRZ→PAM4→PAM6 调制与 FEC 编码、IEEE 802.3（至 1.6T/802.3dj）与 OIF CEI/IBTA/PCI-SIG 标准族、可插拔/LPO/CPO 光模块与 DSP/Retimer 产品格局、SI 测试方法、AI 万卡集群 L1 选型与演进趋势（200G/lane→400G/lane）
>
> **关键词**: 物理层, PAM4, SerDes, 光模块, LPO, CPO, 802.3dj, OIF CEI, InfiniBand, PCIe, Retimer, 信号完整性

## 目录

- [1. 引言与范围](#1-引言与范围)
- [2. L1 分层模型与第一性原理](#2-l1-分层模型与第一性原理)
- [3. 物理介质体系（铜/光/连接器）](#3-物理介质体系铜光连接器)
- [4. 信号调制与线路编码体系](#4-信号调制与线路编码体系)
- [5. 以太网物理层标准族（IEEE 802.3）](#5-以太网物理层标准族ieee-8023)
- [6. 其他 L1 标准体系（InfiniBand/PCIe/CXL/OIF/ITU）](#6-其他-l1-标准体系infinibandpciecxloifitu)
- [7. 产品实现：光模块、电芯片与交换机](#7-产品实现光模块电芯片与交换机)
- [8. L1 信号完整性与测试验证](#8-l1-信号完整性与测试验证)
- [9. AI 集群中的 L1 工程实践与选型](#9-ai-集群中的-l1-工程实践与选型)
- [10. 演进趋势：200G/lane → 400G/lane 与 CPO/LPO 路线之争](#10-演进趋势200glane--400glane-与-cpolpo-路线之争)
- [11. 参考文献](#11-参考文献)

---

## 1. 引言与范围

### 1.1 文档目的

网络 L1（物理层）是承载一切通信的物理基础：从 CPU/GPU 芯片的 SerDes 引脚，到 PCB 走线、连接器、线缆、光模块，再到跨数据中心的光纤。L2 以上的所有协议（以太网 MAC、IP、RoCE、NCCL）最终都依赖 L1 把比特可靠地搬过物理介质。本文档建立**网络 L1 层级的完整知识体系**，回答四个问题：

1. **L1 内部如何分层**——IEEE 802.3 PHY 的 MDI/PMD/PMA/PCS/FEC 子层各自职责（原理层）；
2. **介质与调制如何决定速率极限**——铜 vs 光、NRZ vs PAM4/PAM6、每通道速率演进（物理层）；
3. **标准协议如何定义 L1**——IEEE 802.3、OIF CEI、IBTA、PCI-SIG 的规范体系与代际参数（标准层）；
4. **产品如何实现 L1**——光模块（可插拔/LPO/CPO）、电芯片（DSP/Retimer/SerDes IP）、交换机 ASIC 的厂商格局（产品层）。

### 1.2 目标读者

- 服务器/AI 基础设施网络架构师（万卡集群 L1 选型）
- 互联硬件与 SI 工程师（光模块/线缆/背板设计测试）
- 标准跟踪工程师（IEEE 802.3/OIF/IBTA 演进研判）

### 1.3 取材优先级（Q1）

关键断言以 **IEEE 802.3 工作组官网**（2026-08-06 抓取）、**OIF 官网**、**NVIDIA 官网**为一级来源；《单通道400G以太网物理层白皮书》深度解读（2026-04）与 OFC 2026 前瞻调研为行业佐证；速率/编码等基础参数来自公开标准知识并标注来源；无法确认的量化数据明确标注 [来源: 行业估算] 或 [来源: 待验证]。

### 1.4 与既有文档的关系

- 本文聚焦 **L1 物理层**；上层协议设计模式见同日文档 `2026-08-19-network-protocol-design-patterns-deep-analysis.md`（协议哲学与演进设计），二者构成"底层物理 + 上层范式"互补。
- GPU 网络通信前沿见 `03_server/2026-08-01-gpu-network-communication-frontier-deep-analysis.md`（L2-L4 流量编排与容错），本文是其物理层下探。

---

## 2. L1 分层模型与第一性原理

### 2.1 分层模型：OSI L1 与 IEEE 802.3 PHY 子层

OSI 七层模型中 L1（物理层）负责原始比特流的传输。IEEE 802.3 以太网标准把 L1 进一步细分为五个子层（自下而上）[来源: IEEE Std 802.3 体系]：

```
+----------------------------------------------------------+
|                 MAC (Media Access Control)                |  L2
+----------------------------------------------------------+
|       Reconciliation Sublayer (RS) + xMII interface       |
|  (GMII/XLGMII/CGMII/200GMII/400GMII/800GMII...)           |
+----------------------------------------------------------+
|  PCS  Physical Coding Sublayer: block coding/FEC/scramble |
|  PMA  Physical Medium Attachment: SerDes/CDR/PAM mapping  |
|  PMD  Physical Medium Dependent: electrical/optical TX/RX |
|  MDI  Medium Dependent Interface: connector & media spec  |
+----------------------------------------------------------+
|           Physical medium (copper/fiber/backplane)        |
+----------------------------------------------------------+
```

各子层职责与设计动机（第一性原理）：

| 子层 | 核心职责 | 为什么存在 |
|:-----|:---------|:-----------|
| **PCS** | 块编码（64b/66b、128b/130b）、扰码、FEC 编解码、lane 分配 | 将 MAC 数据流转换为适合物理信道传输的码型；加冗余对抗噪声 |
| **PMA** | SerDes 串并转换、时钟恢复（CDR）、PAM 电平映射 | 把并行数据变成单路高速差分信号；在接收端恢复时钟与数据 |
| **PMD** | 电信号驱动（TX）与接收（RX）、调制格式（NRZ/PAM4）、光/电转换 | 实际驱动介质；PMD 定义了速率、距离、波长等物理参数 |
| **MDI** | 连接器机械/电气规范（如 QSFP-DD cage、RJ45） | 保证互操作性——不同厂商器件可插拔互换 |

> **L1 vs L2 边界判据**：凡是"在介质上传输比特所需"的机制（编码、时钟、均衡、调制、FEC 的物理层部分）属于 L1；凡是"帧的封装、寻址、错误检测"属于 L2。FEC 横跨两者：物理层 FEC（如 RS-FEC）编解码在 PCS 内完成，属 L1 范畴。

### 2.2 第一性原理：L1 的三个物理极限

L1 的一切设计都受三个物理规律约束 [来源: 香农定理/奈奎斯特采样定理，通用知识]：

1. **香农容量**：信道容量 C = B·log₂(1+SNR)。带宽 B 与信噪比 SNR 共同决定速率上限——这解释了为什么速率提升要么加带宽（更宽频谱/更多通道），要么提 SNR（更短距离、更好介质）。
2. **奈奎斯特/波特率限制**：波特率（符号率）受介质带宽限制，提升波特率必然加剧码间干扰（ISI）。从 25GBaud NRZ 到 100GBaud PAM4 再到 200GBaud PAM4，每一代都在逼近介质物理极限。
3. **功耗-距离-速率三角**：速率↑ → 功耗↑（DSP 均衡、FEC 计算）；距离↑ → 功耗↑↑（需更强发射功率与均衡）。这是 LPO/CPO/相干技术路线分野的根本原因。

### 2.3 为什么 AI 时代 L1 成为战略焦点

AI 训练集群的通信开销占比可达 60%（训练时长构成）[来源: 《单通道400G以太网物理层白皮书》解读, 2026-04]，单集群核心交换机容量需求预计 2027 年突破 400 Tbps [来源: 同上]。L1 直接决定：

- **每端口带宽**（100G/400G/800G/1.6T）→ 决定交换机端口数与集群规模上限；
- **每比特功耗**（可插拔 DSP 模块 vs LPO vs CPO）→ 决定数据中心 PUE 与运营成本；
- **成本结构**（光模块占 AI 网络投资约 30-50%，行业估算）→ 决定 TCO。

---

## 3. 物理介质体系（铜/光/连接器）

### 3.1 MECE 分类：L1 介质全景

```
L1 physical media
+-- Electrical (copper)
|   +-- Board level: PCB traces/backplane/connectors
|   +-- Cable: DAC/ACC/AEC (direct attach / active)
|   +-- Feature: short reach(<2-7m), low cost, SI challenge
+-- Optical (fiber)
|   +-- MMF: OM3/OM4/OM5 (VCSEL, <100m)
|   +-- SMF: OS2 (EML/SiPh, 500m-10km+)
|   +-- Feature: long reach, low loss, higher cost
+-- Hybrid: electrical-optical conversion (module DSP/driver)
```

### 3.2 铜介质：DAC/ACC/AEC 三兄弟

| 类型 | 全称 | 信号处理 | 典型距离(400G/800G 时代) | 功耗 | 成本 |
|:-----|:-----|:---------|:------------------------|:-----|:-----|
| **DAC** | Direct Attach Cable | 无源直连，无放大 | 1-2m（800G）；3-5m（400G） | 近 0 | 最低 |
| **ACC** | Active Copper Cable | 仅放大（线性），无 CDR | 3-5m | 低 | 低 |
| **AEC** | Active Electrical Cable | 重定时+均衡（含 CDR） | 5-7m，可到 8m | 中 | 中 |

> 选择依据（工程经验）：**rack 内（<2m）用 DAC**（成本最低、功耗近零）；**rack 内跨机柜顶部（2-5m）用 ACC/AEC**；**rack 间（>5m）用光模块**。DAC 与 AEC 在主机侧 SerDes 接口完全一致，区别仅在缆内是否带放大/重定时 [来源: import 素材《为什么你用光模块测试FPGA IBERT不通》]。

### 3.3 光纤介质：多模 vs 单模

| 维度 | 多模 MMF（OM3/OM4/OM5） | 单模 SMF（OS2） |
|:-----|:------------------------|:----------------|
| 纤芯直径 | 50μm | 9μm |
| 光源 | VCSEL（850nm） | EML/SiPh 激光器（1310nm/1550nm） |
| 典型距离 | 100m 内（OM4 100G 达 150m） | 500m-2km（DR/LR），DCI 40-120km（相干） |
| 每通道成本 | 低（VCSEL 便宜） | 高（但 400G/lane+ 时代差距缩小） |
| 适用场景 | 数据中心内短距（TOR 到服务器） | 机柜间/楼宇间/DCI |

> 关键趋势：**800G 时代多模已近极限，单模成为主流**。800G 光模块几乎全部为单模（DR8/FR8/LR8 均基于 SMF）；多模 VCSEL 停留在 100G/lane（OM4 用 50GBaud PAM4 传输 100G），200G/lane 起多模无对应方案——IEEE P802.3ds 正在定义 200 Gb/s per Wavelength MMF PHYs [来源: IEEE 802.3 官网, 2026-08]，但产业主流已转向单模。

### 3.4 连接器与可插拔封装（MSA）

| 封装 | 通道数 | 应用速率 | 形态 |
|:-----|:------:|:---------|:-----|
| **QSFP-DD** | 8 通道电 | 400G（8×50G）/ 800G（8×100G）/ 1.6T（8×200G） | 双密度 QSFP，当前主力 |
| **OSFP** | 8 通道电 | 400G/800G/1.6T | 略大于 QSFP-DD，散热更好，交换机侧主流 |
| **QSFP** | 4 通道电 | 100G/400G（4×100G） | 经典四通道 |
| **CFP2/CFP4** | 10/4 通道 | 100G/400G 相干 | 电信级，大尺寸 |
| **ELSFP** | 外置光源 | CPO 配套 | 为共封装光学供光 |

光纤连接器：LC（双工，单模标准）、MPO/MTP（多芯，8/16/32 芯，DR 系列光模块标配）、SN/CS（高密度新一代）。

> 端口密度推演（第一性原理）：交换机 ASIC 封装面积与散热决定可承载 SerDes 数量上限。1.6T 时代若用 8×200G 方案，单芯片可做 64×1.6T = 102.4Tbps（如 Broadcom Tomahawk 6 级别）；但 ASIC 引脚/功耗受限，业界转向"单通道速率提升"（200G/lane→400G/lane）而非"加通道数"——这正是 3.2T 以太网的技术逻辑 [来源: 《单通道400G以太网物理层白皮书》解读]。

---

## 4. 信号调制与线路编码体系

### 4.1 调制格式演进：NRZ → PAM4 → PAM6

```
Rate and modulation generations (per-lane electrical/optical):
 1G~10G     25G       50G       100G      200G      400G(plan)
 NRZ       NRZ      PAM4     PAM4      PAM4      PAM4/PAM6
 1bit/sym  1bit     2bit     2bit      2bit      2~2.585bit
 1.25GBaud 25GBaud  25GBaud  50GBaud   100GBaud  200GBaud(or ~140GBaud PAM6)
```

| 调制 | 每符号比特 | 优势 | 劣势 | 应用代际 |
|:-----|:---------:|:-----|:-----|:---------|
| **NRZ（PAM2）** | 1 | 实现简单、SNR 裕量高、功耗低 | 波特率=比特率，带宽需求高 | ≤25G/lane（PCIe Gen5 及以下） |
| **PAM4** | 2 | 同波特率带宽翻倍；技术成熟 | 3 个眼图、SNR 损失 ~9.5dB；需更强 FEC | 50G-200G/lane（当前主流，800G/1.6T 全覆盖） |
| **PAM6** | 2.585 | 波特率可降 ~29%（200G→~140GBaud），SI 裕量大 | 眼图更复杂、FEC 开销与时延更高 | 400G/lane 候选方案（3.2T 时代） |

> **PAM4 成为绝对主流的根因**：200G/lane 若用 NRZ 需 200GBaud，远超介质与 SerDes 可实现带宽；PAM4 只需 100GBaud。800G 以太网（802.3df）、1.6T（802.3dj）、NDR/XDR InfiniBand、PCIe Gen6/7 全部采用 PAM4 [来源: IEEE 802.3 系列标准公开参数]。

> **400G/lane 的 PAM4 vs PAM6 之争**（3.2T 以太网的关键技术决策）：PAM4 走 200GBaud 高波特率路线，复用现有设计但 SI 挑战极大；PAM6 走 ~140GBaud 低波特率路线，SI 裕量好但 FEC/算法复杂度与时延上升 [来源: 《单通道400G以太网物理层白皮书》解读, 2026-04]。OIF 已针对 448Gbps/lane 信号举办专题研讨（448Gbps Signaling for AI Workshop, 2025-04）[来源: OIF 官网]，该速率对应的正是 200GBaud PAM4。

### 4.2 线路编码与 FEC

| 编码/FEC | 开销 | 用途 | 说明 |
|:---------|:----:|:-----|:-----|
| **8b/10b** | 25% | PCIe Gen1-3、1G/10G 以太网 | 保证 DC 平衡与时钟嵌入；低速时代方案 |
| **64b/66b** | 3% | 10G-100G 以太网 PCS | 经典块编码，配合扰码 |
| **128b/130b** | 1.5% | PCIe Gen4/5、100G/lane 以太网 | 更低开销 |
| **RS-FEC（KP4, RS(544,514)）** | ~6.7% | 100G/lane+ 以太网（400G/800G/1.6T）、PCIe Gen6/7 | Reed-Solomon 纠错，纠正长突发错误，PAM4 时代必备 |
| **RS(272,256)** | ~6.25% | 200G/lane 以太网（802.3dj） | 更低时延 FEC 选项 |
| **Fire Code/BCH** | 低 | InfiniBand 链路 | IB 轻量 FEC（HDR 起）+ 主机侧 RS |

> **为什么 PAM4 时代 FEC 不可或缺**：PAM4 相比 NRZ 的信噪比损失约 9.5dB（眼图从 1 个变 3 个、电平间距减半），单纯依赖信道均衡无法达到 BER<1e-15 的链路目标，必须靠 RS-FEC 把原始误码率（约 1e-4~1e-6 量级）纠到 1e-15。代价是 ~100-200ns 的 FEC 时延与功耗——这是低时延场景（如 AI 集合通信）的隐形成本。

### 4.3 SerDes 架构：从并行到串行

```
Modern SerDes data path (TX direction):
 MAC data -> PCS(64b/66b coding + FEC) -> PMA(parallel-serial) -> TX EQ(FFE)
   -> medium(PCB/cable/fiber) -> RX EQ(CTLE+DFE) -> CDR clock recovery
   -> PMA(serial-parallel) -> PCS(decode + FEC correction) -> MAC data
```

关键组件与演进：

| 组件 | 功能 | 代际参数 |
|:-----|:-----|:---------|
| **TX FFE**（前馈均衡） | 预加重/去加重，补偿信道高频损耗 | 每代 tap 数增加 |
| **RX CTLE**（连续时间线性均衡） | 放大高频、压低低频 | 与信道损耗曲线匹配 |
| **RX DFE**（判决反馈均衡） | 消除 ISI（码间干扰）后光标 | PAM4 需 1-tap 以上 |
| **CDR**（时钟数据恢复） | 从数据流恢复时钟 | 波特率越高越难 |
| **DSP-based RX** | 全数字均衡（含 MLSD/最大似然） | 200G/lane 起成为标配 |

> 光模块内的 DSP 本质上是一颗完整 SerDes RX/TX 处理器：它完成 CDR + 均衡 + FEC（部分）+ PAM 映射。**去掉 DSP 就是 LPO（线性驱动可插拔光模块）**——把均衡责任交还给交换机 ASIC 的 SerDes，省电但缩短传输距离、限制互操作性 [来源: OFC 2026 前瞻调研 + 行业公开共识]。

---

## 5. 以太网物理层标准族（IEEE 802.3）

### 5.1 速率代际总表（以太网物理层演进）

| 以太网速率 | 标准 | 每通道 | 通道数 | 调制 | 波长/介质 | 距离等级 |
|:----------|:-----|:------:|:------:|:----:|:----------|:---------|
| 10G | 802.3ae (2002) | 10G | 1 | NRZ | 1310nm SMF | 10km (LR) |
| 25G | 802.3by (2016) | 25G | 1 | NRZ | 1310nm SMF | 100m-10km |
| 100G | 802.3ba (2010) | 25G | 4 | NRZ | 1310/1550nm | 500m-40km |
| 200G | 802.3bs (2017) | 50G | 4 | PAM4 | 1310nm | 500m-2km |
| 400G | 802.3bs (2017) | 50G | 8 | PAM4 | 1310nm | 500m-2km |
| 400G (4×100G) | 802.3cn (2019) | 100G | 4 | PAM4 | 1310nm | 500m-2km |
| 800G | 802.3df (2024) | 100G | 8 | PAM4 | 1310nm | 100m-2km |
| 800G (4×200G) | 802.3dj (进行中) | 200G | 4 | PAM4 | 1310nm | 100m-2km |
| 1.6T | 802.3dj (进行中) | 200G | 8 | PAM4 | 1310nm | 100m-2km |

### 5.2 802.3dj：1.6T 以太网的物理层架构

IEEE P802.3dj "200 Gb/s, 400 Gb/s, 800 Gb/s, and 1.6 Tb/s Ethernet" Task Force 为当前主力项目（截至 2026-08 仍在推进）[来源: IEEE 802.3 官网, 2026-08-06]：

| PHY | 架构 | 说明 |
|:----|:-----|:-----|
| 200GBASE-DR1/FR1/LR1 | 1×200G | 单通道 200G，50m/2km/10km |
| 400GBASE-DR4/FR4/LR4 | 4×200G | 四通道 200G |
| 800GBASE-DR4/FR4/LR4 | 4×200G | 四通道 200G 组成 800G |
| 1.6TBASE-DR8/FR8/LR8 | 8×200G | 八通道 200G 组成 1.6T |

关键技术参数：100GBaud PAM4（200G/lane = 100GBaud × 2bit）；接收侧 DSP 均衡成为必选项；FEC 提供 RS(272,256) 低时延选项。

### 5.3 802.3 体系中的 L1 相邻项目（2026-08 状态）

从 IEEE 802.3 官网工作清单提取的与 L1 直接相关的活跃项目 [来源: IEEE 802.3 官网, 2026-08-06]：

| 项目 | 内容 | L1 意义 |
|:-----|:-----|:--------|
| **P802.3dj** | 200/400/800G 与 1.6T 以太网 | 200G/lane 时代主标准 |
| **P802.3ds** | 200 Gb/s per Wavelength MMF PHYs | 多模光纤 200G/lane 补位 |
| **400 Gb/s/Lane Signaling Study Group** | 400G/lane 信令研究组（新成立） | 3.2T 以太网预研（PAM4 200GBaud 或 PAM6） |
| **New Ethernet Applications Ad Hoc: Ethernet for AI Assessment** | 以太网用于 AI 的评估 | AI 工作负载对 L1/L2 的需求定义 |
| **Channel Operating Margin (COM) Open Source Project** | COM 开源项目 | SI 设计方法学标准化（见 §8） |

> 判断（推理）：400G/lane 研究组的成立意味着 IEEE 在 802.3dj（200G/lane）尚未完成时就启动了 3.2T 预研，节奏与单通道 400G 白皮书（2026-04 发布）吻合——产业对 2027-2028 年 3.2T 的需求预期已经明确。

---

## 6. 其他 L1 标准体系（InfiniBand/PCIe/CXL/OIF/ITU）

### 6.1 InfiniBand 物理层（IBTA 规范）

InfiniBand 物理层与以太网同源（同为串行差分信号 + PAM4），但速率命名按链路代际划分：

| 代际 | 每 lane 速率 | 调制 | 端口速率（4 lane） | 代表产品 |
|:-----|:-----------:|:----:|:------------------|:---------|
| **EDR** (2014) | 25 Gb/s | NRZ | 100 Gb/s | ConnectX-4/5、Quantum-1 |
| **HDR** (2018) | 50 Gb/s | PAM4 | 200 Gb/s | ConnectX-6/7、Quantum-2 |
| **NDR** (2022) | 100 Gb/s | PAM4 | 400 Gb/s（双口 800G） | ConnectX-7/8、Quantum-X800 |
| **XDR** (规划) | 200 Gb/s | PAM4 | 800 Gb/s（双口 1.6T） | ConnectX-9（路线图） |

> NVIDIA Quantum-X800 InfiniBand 为当前旗舰平台，面向超大 AI 集群（官网定位 "High-bandwidth InfiniBand switching for giant AI clusters"）[来源: NVIDIA 官网, 2026-08]。NDR/XDR 的物理层本质与 802.3dj 的 200G/lane 一致（100GBaud PAM4），说明以太网与 InfiniBand 的 L1 技术正在趋同——差异主要在 L2 以上（无损网络、SHARP 网络内计算、自适应路由）。

### 6.2 PCIe/CXL 电气层（PCI-SIG 规范）

PCIe 是服务器内部 L1 的另一大体系（芯片到芯片、芯片到外设）：

| 代际 | 每 lane 速率 | 调制 | 编码 | 发布 |
|:-----|:-----------:|:----:|:----:|:-----|
| Gen1 | 2.5 GT/s | NRZ | 8b/10b | 2003 |
| Gen2 | 5 GT/s | NRZ | 8b/10b | 2007 |
| Gen3 | 8 GT/s | NRZ | 128b/130b | 2010 |
| Gen4 | 16 GT/s | NRZ | 128b/130b | 2017 |
| Gen5 | 32 GT/s | NRZ | 128b/130b | 2019 |
| Gen6 | 64 GT/s | **PAM4** | 128b/130b + 轻量 FEC | 2022 |
| Gen7 | 128 GT/s | PAM4 | + FEC 增强 | 2025 发布 v0.5，正式版推进中 |

- **CXL** 直接复用 PCIe 物理层：CXL 2.0/3.x 基于 PCIe 5.0/6.0 PHY（32/64GT/s），CXL 4.0 规划基于 PCIe 7.0 PHY（128GT/s）[来源: 知识库 06_others/sources/2026-08-12-synopsys-cxl4-0-128gtps-kv-offload.md]。
- **Gen6/Gen7 采用 PAM4 的意义**：PCIe 从 NRZ 转向 PAM4 后，其 L1 挑战（均衡、FEC、信号完整性）与以太网 100G/lane 完全同构，SerDes IP 可跨协议复用。

### 6.3 OIF CEI：芯片间电接口的"通用语言"

OIF（Optical Internetworking Forum）定义**芯片到芯片/芯片到模块**的电接口标准（CEI），是 SerDes IP 与 Retimer 产品的互操作基准：

| 项目 | 覆盖 | 状态 |
|:-----|:-----|:-----|
| CEI-112G (XSR/VSR/MR/LR) | 112G/lane 芯片内/芯片间/芯片到模块/背板 | 已发布 |
| CEI-224G (XSR/VSR/MR/LR) | 224G/lane 四个 reach 档位 | 已发布（2022 启动，2024-2025 陆续完成） |
| CEI-448G 研讨 | 448Gbps/lane for AI | 2025-04 专题研讨会 |

> 核心概念 **Reach 档位**（第一性原理：距离决定均衡复杂度与功耗）：
> - **XSR**（Extra Short Reach，on-package）——芯片封装内/近封装，<50mm，功耗最低；
> - **VSR**（Very Short Reach，chip-to-module）——芯片到可插拔模块，<100mm；
> - **MR**（Medium Reach，chip-to-chip）——PCB 板上芯片间，<500mm；
> - **LR**（Long Reach，backplane）——背板/长铜缆，>1m，均衡与功耗最高。
>
> [来源: OIF 官网 CEI 项目描述, 2026-08]

### 6.4 相干光传输（ITU-T / OIF，DCI 场景）

数据中心互联（DCI）超过 10km 后进入相干光域：

| 项目 | 速率 | 场景 |
|:-----|:-----|:-----|
| 800G 相干 (OIF) | 800Gbps 相干线路 | campus/DCI |
| **1600ZR / 1600ZR+** (OIF) | 1600Gbps 相干接口 | 数据中心互联（功率优化） |

> 相干技术（QPSK/QAM 调制 + DSP 色散补偿）与短距 IM-DD（强度调制直接检测）是 L1 光的两个分支：**短距（<2km）用 IM-DD 可插拔光模块，长距（>10km）用相干**。OIF 1600ZR 项目标志 DCI 进入 1.6T 相干时代 [来源: OIF 官网 Hot Topics, 2026-08]。

### 6.5 L1 标准体系全景图

```
              L1 standards organizations and scope
+---------------------------------------------------------------+
|  IEEE 802.3     Ethernet PHY(1G~1.6T)  full PCS/PMA/PMD stack |
|  OIF CEI        chip-to-chip / chip-to-module elec (112/224G)  |
|  IBTA           InfiniBand PHY(EDR~XDR, 25G~200G/lane)         |
|  PCI-SIG        PCIe/CXL electrical layer(2.5~128GT/s)         |
|  ITU-T/OIF      coherent transport (OTN/ZR/ZR+, 400G~1.6T)     |
|  MSA            QSFP-DD/OSFP/CFP mechanical & electrical spec  |
|  CMIS (OIF)     module management interface (CMIS 5.3)         |
+---------------------------------------------------------------+
```

---

## 7. 产品实现：光模块、电芯片与交换机

### 7.1 光模块产品谱系（可插拔 → LPO → CPO）

```
Optical module technology evolution (by integration & power):
Pluggable(DSP) -> Pluggable(LPO) -> NPO -> CPO
high power/flex  mid power/limited  low    lowest
long reach/intop  reach-limited     board  custom switch
```

| 路线 | 原理 | 功耗 | 互操作性 | 商用状态 |
|:-----|:-----|:----:|:--------|:---------|
| **可插拔 DSP 模块** | 模块内 DSP 完成 CDR/均衡/FEC | 基准（800G ~15W 级，行业估算） | 好（标准 MSA 互换） | 主流（800G/1.6T 放量中） |
| **LPO**（Linear Pluggable Optics） | 去 DSP，线性驱动，均衡交给主机 SerDes | 较 DSP 降 ~40-50%（行业估算） | 受限（依赖主机 SerDes 能力） | 2025-2026 商用导入，OFC 共识"近期更优方案" |
| **NPO**（Near-Package Optics） | 光引擎靠近 ASIC 但仍在板上 | 低 | 中 | 过渡方案 |
| **CPO**（Co-Packaged Optics） | 光引擎与交换 ASIC 共封装 | 最低（每端口 <5W 级，行业估算） | 差（需定制交换机+ELSFP 外置光源） | 2026 开始样品，**放量预期 2029-2030** |

> 产业节奏判断（OFC 2026 前瞻）：CPO 落地普遍预期 2029/2030 年；当前 LPO 是兼顾省电与可落地性的现实方案；可插拔与 CPO 将**长期并存**（"不是非黑即白"，五年甚至十年生命周期内共存）[来源: OFC 2026 前瞻调研, import 素材]。英伟达已公告共封装硅光网络交换机（"Co-Packaged Silicon Photonic Networking Switches to Scale to Millions of GPUs"）[来源: NVIDIA 官网, 2026-08]，博通亦在推进 CPO 交换机。

### 7.2 光模块核心器件与厂商格局

**光域三大调制器平台**（单通道 400G 白皮书口径）[来源: 《单通道400G以太网物理层白皮书》解读, 2026-04]：

| 平台 | 技术 | 优势 | 劣势 | 代表厂商 |
|:-----|:-----|:-----|:-----|:---------|
| **InP**（磷化铟） | EML 激光器 | 技术最成熟、性能优越 | 成本高、产能受限 | Coherent、Lumentum、源杰 |
| **SiPh**（硅光子） | CMOS 工艺集成 | 高集成度、成本可控、适合量产 | 激光器仍需外置/混合集成 | Intel、Marvell、中际旭创 |
| **TFN**（薄膜铌酸锂） | 调制器超宽带 | 超高带宽、超低功耗 | 工艺与封装不成熟 | 待产业化（2026 前沿） |

**光模块厂商格局**（2026 产业状态）：中国厂商（中际旭创、新易盛、光迅、华工正源等）为全球数据中心光模块主力供应方，800G/1.6T 同步放量带动光芯片涨价与上游景气 [来源: OFC 2026 前瞻调研]；Coherent 在光模块与 CPO 多路径技术领先，与英伟达签署 20 亿美元级供货协议 [来源: OFC 2026 前瞻调研]。

### 7.3 电芯片产品谱系（DSP/Retimer/SerDes IP）

| 产品类别 | 功能 | 代表厂商 | 关键产品 |
|:---------|:-----|:---------|:---------|
| **光模块 DSP** | 模块内 CDR+均衡+FEC | Marvell（收购 Inphi）、Broadcom、Credo、MaxLinear | 800G/1.6T DSP（7nm/5nm） |
| **Retimer（重定时器）** | 恢复信号+重发，延长走线距离 | **Astera Labs**（Aries）、Marvell（Alaska）、Broadcom、Parade | PCIe 5.0/6.0 Retimer；224G 以太网 Retimer |
| **AEC 线缆芯片** | 缆内重定时 | Credo（AEC 开创者）、Marvell | 400G/800G AEC |
| **SerDes IP** | 芯片内 PHY 授权 | Synopsys、Cadence、Alphawave、Rambus | 112G/224G SerDes IP |
| **LPO 线性驱动/接收芯片** | 无 DSP 的线性 TIA/Driver | Macom、Semtech、MaxLinear | 800G LPO 配套 |

> Retimer 与 Redriver 的区别（工程要点）：**Redriver 只做模拟补偿（CTLE/DFE），无 CDR**，时延低但补偿能力有限；**Retimer 含 CDR，彻底重构信号**，可跨板/跨连接器长距离传输。PCIe 6.0/7.0 时代 Retimer 成为服务器平台标配（插卡/板载），对应 Astera Labs 与 Marvell 的核心业务。

### 7.4 交换机 ASIC 与平台（L1 的集成者）

| 厂商 | 芯片/平台 | 端口能力 | L1 特点 |
|:-----|:----------|:---------|:--------|
| **Broadcom** | Tomahawk 5/6、Trident 5 | 51.2T（800G×64）/ 102.4T（1.6T×64） | 内置 SerDes + PAM4 DSP 均衡；CPO 版本在研 |
| **NVIDIA** | Spectrum-4/5（以太网）、Quantum-X800（IB） | 51.2T / 800G 端口 | 硅光 CPO 交换机新公告；SHARP 网络内计算 |
| **Marvell** | Teralynx 10 | 51.2T | 低时延 AI 交换机 |
| **Cisco** | Silicon One G 系列 | 51.2T+ | 相干光模块核心供应商 |

> 判断：**L1 的竞争焦点正从"速率"转向"功耗与集成"**——当所有厂商都能做 800G/1.6T SerDes 时，每比特功耗（LPO/CPO/硅光）与端口密度成为差异化核心，这与 OIF 成立"Energy Efficient Interfaces"专项的动因一致 [来源: OIF 官网]。

---

## 8. L1 信号完整性与测试验证

### 8.1 核心 SI 指标（第一性原理：误码率的物理来源）

| 指标 | 定义 | 工程意义 |
|:-----|:-----|:---------|
| **BER**（误码率） | 错误比特/总比特 | L1 最终裁决指标；目标 <1e-15（含 FEC 后） |
| **眼图** | 叠加所有符号的电平-时间轨迹 | 直观评估信号质量；PAM4 有三个眼 |
| **抖动 Jitter（RJ/DJ/TJ）** | 信号边沿偏离理想位置的随机/确定性/总抖动 | 决定时序裕量；BER=1e-12 处 TJ 为设计基准 |
| **插入损耗 IL** | 信道对信号幅度的衰减（dB） | 随频率上升；决定均衡需求 |
| **回波损耗 RL** | 阻抗不连续导致的反射 | 影响噪声与眼图闭合 |
| **串扰（NEXT/FEXT）** | 相邻通道耦合噪声 | 高密度连接器的关键杀手 |
| **COM**（Channel Operating Margin） | IEEE 802.3 定义的信道综合裕量（dB） | **SI 设计的标准化判据**，替代经验法则 |

### 8.2 测试验证方法

```
L1 verification stack:
 Simulation: channel S-param (EM) -> statistical eye (COM calc)
 Chip level: SerDes built-in BIST / eye scan (self-test)
 Board:      BERT + scope(real-time/sampling) + TDR(impedance)
 System:     PRBS long-run (PRBS31 24h+) -> temp/volt sweep -> mate cycle
```

| 方法 | 工具 | 用途 |
|:-----|:-----|:-----|
| **PRBS 测试** | BERT（如 Keysight/Anritsu）、FPGA IBERT | 伪随机码型测 BER；IBERT 可测眼图与误码定位 [来源: import 素材《为什么你用光模块测试FPGA IBERT不通》] |
| **眼图/抖动分析** | 实时示波器 + 时钟恢复 | 看眼高/眼宽/抖动分布 |
| **COM 计算** | IEEE 802.3 COM 开源工具（2026 有官方开源项目） | 快速评估信道是否达标 [来源: IEEE 802.3 官网] |
| **链路训练** | PCIe/以太网 LT 日志 | 协商速率/均衡参数 |
| **模块诊断** | CMIS 5.3（OIF）管理接口 | 光功率/温度/电压/误码遥测 [来源: OIF 官网] |

> 工程铁律：**L1 问题 90% 在物理连接**——连接器虚接、线缆弯折半径超限、光纤端面污染（脏污导致插损剧增）是现场 BER 恶化的三大主因。PAM4 时代光纤端面洁净度要求比 NRZ 严格一个数量级（IEC 61300-3-35 标准），维护手册必须纳入端面检测仪（如 EXFO 光纤端面仪）流程。

---

## 9. AI 集群中的 L1 工程实践与选型

### 9.1 三域 L1 选型矩阵（scale-up / scale-out / DCI）

```
AI cluster L1 topology:
 [GPU node] --SerDes--> [board/backplane] --copper DAC/AEC--> [TOR]
     TOR --SMF optics(DR/FR)--> [Leaf] --optics--> [Spine]
     Spine --coherent(ZR)--> [DCI remote cluster]
```

| 域 | 距离 | 首选 L1 介质 | 速率代际 | 关键约束 |
|:---|:-----|:------------|:---------|:---------|
| **scale-up**（节点内） | <1m | PCB + 背板（NVLink/PCIe/CXL PHY） | 64-128GT/s | 功耗密度、SI 裕量 |
| **scale-out 叶脊**（rack 内/间） | 1-100m | DAC/AEC（<5m）→ 单模光模块（>5m） | 400G/800G/1.6T | 每比特功耗、成本 |
| **DCI**（跨数据中心） | >10km | 相干光 | 800G/1.6T ZR | 色散、放大、可靠性 |

### 9.2 万卡集群 L1 数量级估算（工程推演）

以 10 万卡集群（2×800G 每卡）为例：

```
per card 2 ports x 800G = 1.6Tbps/card
100k cards -> 200k links @ 800G
optical module demand ~ 400k pcs (incl. switch side)
link power ~ 400k x 15W (pluggable DSP) = 6MW
              with LPO(-50%) -> 3MW, significant saving
```

> 数字为基于公开单端口功耗区间的推演 [来源: 行业估算]，用于说明 L1 选型对集群 TCO 的量级影响——光模块功耗与成本是万卡集群的**第一梯队变量**，这也是 CPO/LPO 被 AI 基础设施全力推动的根本原因。

### 9.3 工程选型决策树

```
Q1: distance <2m?          -> DAC (lowest cost)
Q2: 2-5m?                  -> ACC/AEC (passive or active copper)
Q3: 5-100m & DSP OK?       -> pluggable optics (DR/FR series)
Q4: power sensitive + strong host SerDes? -> LPO (verify compat)
Q5: custom switch ASIC + scale>10k cards? -> evaluate CPO (2027+)
Q6: cross data center?     -> coherent ZR optics
```

### 9.4 L1 运维与可靠性要点

- **光纤端面维护**：IEC 61300-3-35 洁净度标准，插拔前必检（PAM4 高灵敏度）；
- **链路遥测**：CMIS 5.3 提供光功率/温度/偏置电流/误码率实时读数，接入带外管理（BMC/Redfish）；
- **故障分级**：光功率低→端面脏/衰减器错；BER 高→连接器虚接/线缆弯折；无光→模块故障/链路协商失败；
- **备件策略**：光模块失效率高于铜缆，万卡集群需 2-5% 备件池（行业经验值）；
- **线缆管理**：最小弯曲半径（光缆 ~10 倍外径）、拉力控制、标签规范。

---

## 10. 演进趋势：200G/lane → 400G/lane 与 CPO/LPO 路线之争

### 10.1 速率演进主线（2024-2030 路线图）

```
2024  2025  2026  2027  2028  2029  2030
+--+  +--+  +--+  +--+  +--+  +--+  +--+
100G/lane  ->  200G/lane(802.3dj mass)  ->  400G/lane(3.2T study)
| 800G mass     | 1.6T commercial         | 3.2T planning
| 400G main     | 800G ramping            |
+--+  +--+  +--+  +--+  +--+  +--+  +--+
pluggable DSP main -> LPO adoption -> CPO samples -> CPO ramp (2029-30 exp)
```

关键判断（推理链）：

1. **200G/lane 是 2026-2028 确定主线**：802.3dj 量产 + NDR/XDR 同步，800G 光模块进入放量期 [来源: OFC 2026 前瞻调研"800G/1.6T 同步放量"]；
2. **400G/lane 预研已启动**：IEEE 400G/lane 研究组 + OIF 448G 研讨 + 单通道 400G 白皮书三信号叠加，3.2T 时代技术路线（PAM4 200GBaud vs PAM6）尚未定论 [来源: IEEE/OIF 官网 + 白皮书解读]；
3. **功耗成为第一竞争维度**：OIF Energy Efficient Interfaces 专项 + 英伟达/博通 CPO 交换机公告 + LPO 商用导入，三者共同指向"每比特功耗"是下一个战场 [来源: OIF/NVIDIA 官网]；
4. **可插拔与 CPO 长期共存**：不是替代关系，而是按场景分工（可插拔=通用灵活，CPO=超大规模定制）[来源: OFC 2026 前瞻调研]。

### 10.2 对服务器/AI 基础设施的启示（行动建议）

| 角色 | 建议 |
|:-----|:-----|
| **平台规划** | 800G 光模块纳入 2026-2027 服务器/交换机 RFP；预留 1.6T 演进位（OSFP/QSFP-DD 双形态评估） |
| **SI 设计** | 全面引入 COM 方法学替代经验法则；224G SerDes 走线提前做电磁仿真与损耗预算 |
| **供应链** | 光模块双源策略（中国主力厂商 + Coherent 等海外二供）；关注光芯片（EML/SiPh）产能与涨价 |
| **功耗治理** | 评估 LPO 在 rack 内短距场景的适用性；跟踪 CPO 交换机 2027+ 商用节奏 |
| **标准跟踪** | 盯 802.3dj 最终发布、400G/lane 研究组结论、OIF CEI-448G 项目启动 |

---

## 参考文件

### 内部知识库引用

- [网络协议设计模式全景](../07_industry-research/2026-08-19-network-protocol-design-patterns-deep-analysis.md) — 上层协议设计范式，与本文 L1 物理层互补
- [GPU 网络通信前沿](../07_industry-research/03_server/2026-08-01-gpu-network-communication-frontier-deep-analysis.md) — L2-L4 流量编排与容错，本文为其物理层下探
- [光互联演进路线（NPO/CPO）](../02_rd/02_project/01_superpod/2026-08-14-optical-interconnect-roadmap-npo-cpo-consensus-deep-analysis.md) — 光互联封装路线共识
- [CXL 4.0 128GT/s（Synopsys 报道）](../06_others/sources/2026-08-12-synopsys-cxl4-0-128gtps-kv-offload.md) — CXL 4.0 基于 PCIe 7.0 PHY

### 外部资料引用

[1] IEEE 802.3 Ethernet Working Group, 官网工作项目清单, 2026-08-06 抓取. https://www.ieee802.org/3/
[2] IEEE Std 802.3-2022 及 802.3bs/df/dj 系列标准公开参数（速率/编码/PHY 定义）.
[3] OIF（Optical Internetworking Forum）官网: CEI-112G/224G、1600ZR、CMIS 5.3、Energy Efficient Interfaces, 2026-08 抓取. https://www.oiforum.com/
[4] NVIDIA 官网: Quantum InfiniBand 平台、Quantum-X800、共封装硅光交换机公告, 2026-08 抓取. https://www.nvidia.com/en-us/networking/
[5] 《单通道400G以太网物理层白皮书》深度解读（全球首份, 2026-04，行业公开材料；素材原稿存于 workspace 素材库）— PAM4/PAM6 路线、InP/SiPh/TFN 平台、无源通道决定性作用.
[6] OFC 2026 前瞻调研《电子掘金-直击北美AI前线》（2026-03，行业公开材料；素材原稿存于 workspace 素材库）— CPO/LPO 节奏、Coherent 订单、800G/1.6T 放量、光芯片涨价.
[7] 《为什么你用光模块测试FPGA IBERT不通》（行业技术博客，素材原稿存于 workspace 素材库）— PRBS/IBERT/DAC/AOC 工程实践.
[8] PCI-SIG 规范公开参数（PCIe 1.0-7.0 速率/调制/编码）.
[9] IBTA InfiniBand 规范公开参数（EDR/HDR/NDR/XDR 链路速率）.

---

## Changelog

| 版本 | 日期 | 变更说明 |
|:----:|:----:|:---------|
| v1.0 | 2026-08-19 | 首次创建：L1 分层模型、介质体系、调制编码、802.3/OIF/IBTA/PCI-SIG 标准族、光模块/电芯片产品、SI 测试、AI 集群 L1 工程实践与演进趋势 |


