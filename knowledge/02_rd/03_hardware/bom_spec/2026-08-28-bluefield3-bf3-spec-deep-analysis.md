# NVIDIA BlueField-3 (BF3) DPU 规格解读报告 — 核心规格参数与工作原理

> **元信息**: 文件状态=正式版 v1.0 | 覆盖范围=BlueField-3 DPU 全家族规格（网络/计算/内存/加速引擎/安全/存储/时序/形态）与工作原理 | 版本=1.0
> **适用范围**: 服务器平台规划 / DPU BOM 选型 / AI 集群 Scale-Out 与存储网络设计 / 基础设施卸载评估

## 目录

- [1. 引言与范围](#1-引言与范围)
- [2. 产品定位与代际演进](#2-产品定位与代际演进)
- [3. 芯片架构与工作原理](#3-芯片架构与工作原理)
- [4. 核心规格参数总表](#4-核心规格参数总表)
- [5. 形态与型号矩阵](#5-形态与型号矩阵)
- [6. 与 ConnectX-7 的关系辨析](#6-与-connectx-7-的关系辨析)
- [7. 软件生态：DOCA](#7-软件生态doca)
- [8. 电气/热/环境规格](#8-电气热环境规格)
- [9. 应用场景与部署](#9-应用场景与部署)
- [10. 竞品对比](#10-竞品对比)
- [11. 代际演进与平台化趋势](#11-代际演进与平台化趋势)
- [12. BOM 选型建议](#12-bom-选型建议)
- [13. 参考文献](#13-参考文献)
- [14. 变更记录](#14-变更记录)

---

## 1. 引言与范围

### 1.1 文档目的

本文档对 NVIDIA BlueField-3（下称 **BF3**）DPU 进行**规格级深度解读**，回答三个问题：

1. **是什么**：BF3 的完整规格参数（网络/计算/内存/加速引擎/形态/管理）；
2. **怎么工作**：芯片级架构与各卸载引擎的原理（为什么 400G 线速不消耗 Arm 核、为什么只需 16GB 内存、双 OS 如何隔离）；
3. **怎么用**：在 AI 集群（SuperNIC）、云网络、存储（SNAP/JBOF）、安全、5G 场景的部署口径与 BOM 选型要点。

### 1.2 目标读者

服务器/数据中心硬件工程师、网络架构师、BOM 与采购负责人、AI 基础设施规划者。

### 1.3 覆盖范围

- BF3 DPU 全家族：标准版（B3220 系列）、自宿主版（B3220SH）、400G/200G 端口形态、HHHL/FHHL/双宽/OCP 形态
- 与 ConnectX-7（网络引擎同源）、BlueField-4（下一代）的边界关系
- 不覆盖：BF3 上运行的具体应用软件开发（DOCA 编程细节见 NVIDIA DOCA 文档）

### 1.4 术语表

| 术语 | 含义 |
|:-----|:-----|
| DPU | Data Processing Unit，数据中心基础设施处理单元 |
| NDR | NVIDIA 400Gb/s InfiniBand（Next Data Rate），4 lane × 100Gb/s PAM4 |
| RoCE | RDMA over Converged Ethernet |
| ASAP² | Accelerated Switch and Packet Processing，NVIDIA 硬件 vSwitch/SDN 加速引擎 |
| GPUDirect / GDS | GPU 显存直连网卡 DMA / GPUDirect Storage |
| SNAP | BlueField SNAP，弹性块存储（NVMe/VirtIO-blk 映射） |
| DOCA | NVIDIA 数据中心基础设施编程框架（DPU 的 "CUDA"） |
| Cerberus | OCP 定义的服务器固件可信根标准 |
| NTB | Non-Transparent Bridging，PCIe 非透明桥（多主机/自宿主关键） |
| SH | Self-Hosted，自宿主版（DPU 作为系统主机处理器） |
| OPN | Ordering Part Number，订货型号 |

---

## 2. 产品定位与代际演进

### 2.1 BlueField 家族代际

| 代际 | 发布年 | 网络速率 | PCIe | Arm 核 | 内存 | 定位 |
|:-----|:------:|:--------:|:----:|:------:|:-----|:-----|
| BlueField-1 | 2019 | 25/100GbE | Gen3 x16 | 8×A72 | 16GB（DDR4 单通道） | 试水（STH 评论称"trial balloon"） |
| BlueField-2 | 2020 | 100GbE / HDR100 | Gen4 x16 | 8×A72 | 16GB（DDR4 单通道，带宽反低于 BF1） | 量产主力（ConnectX-6 + Arm） |
| **BlueField-3** | **2022** | **400GbE / NDR 400G** | **Gen5 x32** | **16×A78** | **16GB DDR5 双通道** | **第三代基础设施 on-a-chip（本文主角）** |
| BlueField-4 | 2025-2026 | 800GbE | Gen6 | 64×Neoverse V2（Grace；STX 版=2×84 核 Vera） | 128GB LPDDR5x | 800G Scale-In 平台，gigascale AI 工厂（详见 BF4 文档） |

> BF3 于 GTC 2022 发布、2022-2023 量产（SC22 首见实物，STH 2022-12 报道）[来源: STH SC22/400G Exposed 报道]。BF3 是 Mellanox 被 NVIDIA 收购（2020.04）后**第二代完全 NVIDIA 品牌 DPU**，与 ConnectX-7（SmartNIC）、Quantum-2（NDR 交换机）、Spectrum-4（400GbE 交换机）同代发布。

### 2.2 在 NVIDIA 网络矩阵中的位置

```
       AI Cluster / Cloud DC Infrastructure
   +---------------------------------------+
   |  Scale-Out Training Net                |
   |   Quantum-2 IB <--NDR--> BF3 (SuperNIC)|  <- 400G line-rate + AI native
   |   Spectrum-4 Eth <--400GbE--> BF3      |
   +---------------------------------------+
   |  Scale-In Storage / Mgmt Net           |
   |   BF3 SNAP + NVMe-oF --> JBOF/Storage  |  <- SH self-hosted as host CPU
   +---------------------------------------+
   |  Same engine: ConnectX-7 (pure NIC)    |  <- no-Arm low power form
   +---------------------------------------+
```

BF3 的差异化定位：**"数据中心基础设施 on-a-chip"第三代**——把网络、存储、安全、管理四类基础设施功能从宿主 CPU 卸载到一块 400G 线速的 DPU 上，同时提供 Arm 通用算力与 DOCA 可编程性[来源: NVIDIA BF3 Datasheet]。

### 2.3 "DPU 为什么需要 Arm 核"——第一性原理

DPU 的核心矛盾：网络/存储/安全卸载需要**确定性性能**（硬件引擎），而基础设施服务（虚拟网络、存储栈、安全策略）需要**可演进性**（软件逻辑）。纯硬件 NIC 无法跑服务逻辑，纯 Arm 软件卡性能不足。BF3 的答案是**异构加法**：Mellanox ConnectX-7 硬件引擎做"减法"（线速固定功能），16 核 Arm A78 做"加法"（控制平面/慢路径/管理）[来源: 知识库 DPU 三方对比 §3.3]。

---

## 3. 芯片架构与工作原理

### 3.1 芯片本体：ConnectX-7 网络引擎 + Arm SoC 的异构集成

BF3 的 ASIC 本质是 **ConnectX-7（MT2910 级）网络引擎 + Arm A78 计算子系统 + 专用加速引擎**的片上集成。Linux 下 BF3 的网络功能呈现为 ConnectX-7 设备，Arm 子系统为独立 SoC 域[来源: NVIDIA BF3 Datasheet + 知识库 CX7 文档 §3.1]。

核心能力分层（第一性原理拆解）：

| 层 | 职责 | BF3 实现 |
|:---|:-----|:---------|
| 物理层 | 信号编解码 | 以太 400G PAM4 / IB NDR 100G/lane；PCIe Gen5 32GT/s ×32 lanes |
| 数据通路 | 报文收发 | ConnectX-7 硬件引擎 + DMA，直连主机内存/GPU 显存 |
| 传输层 | 可靠传输 | IB Transport / RoCEv2（DCQCN）硬件卸载、Zero Touch RoCE |
| 服务层 | 协议终结 | VXLAN/GENEVE/NVGRE、ASAP² vSwitch、NVMe-oF、MPI 集群体操作 |
| 计算层 | 通用处理 | 16×Arm A78（Armv8.2+）+ 16 核/256 线程可编程数据路径加速器 |
| 安全层 | 加密/信任 | Secure Boot/PKA 可信根、Cerberus、MACsec/IPsec/TLS、AES-GCM/XTS、RegEx、连接跟踪 |
| 存储层 | 存储服务 | SNAP（NVMe/VirtIO-blk）、NVMe-oF/TCP 加速、解压、纠删码 RAID、M.2/U.2 |

### 3.2 双 OS 独立架构（关键架构特性）

```
 +---------------------------------------------------+
 |  BF3 Die                                           |
 |  +-----------------+  +------------------------+  |
 |  | Arm Subsystem   |  | NIC Subsystem           |  |
 |  | 16x A78 + 16GB  |  | ConnectX-7 engine       |  |
 |  | DDR5            |  | (independent RTOS)      |  |
 |  | Linux (Ubuntu)  |  |                        |  |
 |  | Control plane / |  | 400G line-rate data     |  |
 |  | Mgmt / slow path|  | plane: RX/TX/offload/   |  |
 |  +--------+--------+  | crypto/storage/collect. |  |
 |           | internal  +------------------------+  |
 |           v                                          |
 |  +----------------------------------------------+   |
 |  | PCIe Gen5 x32 (16 downstream + NTB)          |   |
 |  +----------------------------------------------+   |
 +---------------------------------------------------+
```

**核心机制**：NIC 子系统与 Arm 子系统**各自运行独立操作系统**——NIC 跑自己的实时 OS（保证线速数据面确定性），Arm 跑标准 Linux（Ubuntu Server 等）。因此**可以单独重启 Arm 侧而不中断网络数据面**；反之网络侧故障也不影响 Arm 上的管理/控制应用[来源: STH Hot Chips 33 报道]。

> **工程意义**：这一双 OS 隔离是 BF3 可用作"服务器主机 CPU"（SH 版）和"bump-in-the-wire"基础设施节点的前提——数据面与控制面的故障域天然分离。对比：BF2 的 CPU 能力原始，bump-in-the-wire 模式性能损失大；BF3 通过硬件引擎分担消除了该损失[来源: STH Hot Chips 33 报道]。

### 3.3 数据平面范式：固定硬件引擎 + 可编程旁路

BF3 属于三大 DPU 数据平面范式中的**"固定硬件引擎"**路线（与 Intel E2100 的软件数据面、AMD Salina 400 的 P4 硬件流水线并列）：

| 范式 | 执行者 | 性能 | 灵活性 | 代表 |
|:-----|:-------|:----:|:------:|:-----|
| 软件数据面 | Arm 核 + 用户态软件 | 低（200G 封顶） | 最高 | Intel E2100 |
| **固定硬件引擎** | **ConnectX-7 硅上专用电路** | **最高（400G 线速）** | 低（引擎外可编程） | **NVIDIA BF3** |
| 可编程硬件流水线 | P4 match-action 硅流水线 | 高（400G） | 中（P4 语言内） | AMD Salina 400 |

BF3 数据面主体是 **ConnectX-7 固定功能硬件引擎**——RDMA（RoCE 硬件卸载）、ASAP²（vSwitch/SDN）、加密、存储（SNAP/NVMe-oF）均为硅上专用电路，**400G 线速不消耗 Arm 核**；Arm A78 只跑控制平面/管理/慢路径；另有一个**可编程数据路径加速器（16 核/256 线程）**用于 DOCA 编程的灵活数据面任务，弥补硬件引擎覆盖不到的协议[来源: NVIDIA BF3 Datasheet + 知识库 DPU 三方对比 §3.3]。

> **第一性推论**：性能-灵活性是数据平面的根本矛盾。BF3 的取舍是"**常用协议走硬件（确定性），新协议用 DOCA 在 256 线程引擎上跑（灵活性）**"——代价是硬件引擎固化（灵活性最低）与成本最高（ConnectX 引擎 + Arm + 大封装）[来源: 知识库 DPU 三方对比 §3.5]。

### 3.4 各卸载引擎原理

**（1）网络引擎（ConnectX-7 核心）**
- **RoCE + Zero Touch RoCE**：RDMA 硬件卸载 + 自动配置（免手动 PFC/ECN 调优），配合 DCQCN 拥塞控制实现无损以太网低尾延迟——超节点 RoCE 方案可用性的物理前提[来源: NVIDIA BF3 Datasheet + 知识库 CX7 文档 §3.3]；
- **ASAP²**：硬件 vSwitch/SDN 加速（OVS 卸载），将虚拟网络转发从宿主 CPU 挪到 DPU——云多租户场景的 CPU 释放来源（NVIDIA 官方宣称可卸载 25-40% 基础设施开销，行业口径）[来源: 知识库 DPU 三方对比 §5]；
- **Overlay 卸载**：VXLAN/GENEVE/NVGRE 硬件封装/解封装；可编程 flexible parser 支持用户自定义报文分类[来源: NVIDIA BF3 Datasheet]；
- **Stateless TCP offloads + 分层 QoS + 流镜像/采样/统计**：遥测与流量工程硬件化[来源: NVIDIA BF3 Datasheet]。

**（2）AI/HPC 引擎（BF3 差异化，三家中唯一"AI 原生"DPU）**
- **All-to-All 引擎**：集群体通信硬件卸载（Allreduce/Alltoall 等），配合 Quantum-2 交换机 SHARP 实现"计算进网络"；
- **GPUDirect**：GPU 显存↔网卡直接 DMA，训练梯度同步免 CPU/主机内存拷贝（PeerDirect）；
- **GPUDirect Storage (GDS)**：存储↔GPU 直通，训练数据加载绕过主机内存；
- **MPI Tag Matching**：MPI 消息匹配硬件卸载。

[来源: NVIDIA BF3 Datasheet + 知识库 DPU 三方对比 §4.1]

> **场景价值**：在 AI 训练集群中，BF3 的 RoCE 硬件卸载 + GPUDirect + All-to-All 引擎构成结构性优势——梯度同步与数据加载不再消耗主机 CPU/内存带宽，这是纯以太 NIC 与软件 RoCE 方案无法对等的[来源: 知识库 DPU 三方对比 §4.1]。

**（3）存储引擎（SNAP 差异化卖点）**
- **BlueField SNAP**：弹性块存储——把远端 NVMe-oF 盘/VirtIO-blk 设备映射为本地盘呈现给主机，**让网络存储表现得像本地盘**；
- **NVMe-oF / NVMe-TCP 加速**：target 侧硬件加速；
- **解压引擎 + 纠删码/RAID 硬件**：数据缩减与可靠性卸载；
- **M.2/U.2 直连**：DPU 本地可挂 SSD，构成"无主机存储节点"。

[来源: NVIDIA BF3 Datasheet + 知识库 DPU 三方对比 §4.2]

**（4）安全引擎（"安全全家桶"，零信任基础设施）**
- **可信根**：Secure Boot + PKA（公钥加速器）root-of-trust、安全固件更新、Flash 加密、**Cerberus 合规**、功能隔离层；
- **数据加密**：MACsec/IPsec/TLS 线速加密、AES-GCM 128/256-bit（传输中）、AES-XTS 256/512-bit（静态）、PKA（RSA/DH/DSA/ECC/EC-DSA/EC-DH）；
- **威胁检测**：RegEx 匹配处理器（DPI/IDS）、连接跟踪（有状态防火墙）、TRNG。

[来源: NVIDIA BF3 Datasheet]

> **判断**：BF3 安全能力是三家中最全的（云/企业合规导向）；对比 Salina 400 在连接密集型安全场景（500 万连接/秒 P4 流水线）有数量级优势但无 RDMA/AI 原生能力——两者定位不同[来源: 知识库 DPU 三方对比 §4.3]。

**（5）精确时序（5G/电信场景）**
IEEE 1588v2（任意 profile）、G.8273.2 Class C、PTP 硬件时钟（PHC）、**线速硬件时间戳**、SyncE（G.8262.1 eEEC）、可配置 PPS In/Out、时间触发调度、基于时间的 SDN 加速。实物卡带 1PPS + 10MHz 时同步端口（STH 实测确认，用于纳秒级报文时间戳）[来源: NVIDIA BF3 Datasheet + STH 400G Exposed 评论区]。

**（6）PCIe 架构（x32 + NTB——DPU 与 NIC 的分水岭）**
- **32 lanes PCIe Gen5**（普通 NIC 为 x16）：PCIe switch bifurcation 最多 **16 个下游端口** + **NTB**；
- 16 下游端口的意义：**多主机共享**（1 卡服务多台主机）与**自宿主**（SH 版把 SSD/GPU 挂到 DPU 下游，DPU 当系统根）；
- NTB 的意义：双主机间安全内存共享/故障隔离。

[来源: NVIDIA BF3 Datasheet + STH Self-Hosted 报道]

---

## 4. 核心规格参数总表

> 全部数据来自 NVIDIA 官方 Datasheet（2026-08-28 抓取核实）[来源: NVIDIA BF3 Datasheet]

### 4.1 网络与主机接口

| 维度 | 规格 |
|:-----|:-----|
| 网络端口 | Ethernet：1/2/4 端口，最高 **400Gb/s** |
| InfiniBand | 单口 **NDR 400Gb/s**，或双口 NDR200/HDR 200Gb/s |
| PCIe | **32 lanes PCIe Gen5.0**；switch bifurcation 最多 16 下游端口；NTB 支持 |
| 端口形态示例 | 双口 200GbE（合计 400G）FHHL 为标准形态；400G 版为双宽卡 |

### 4.2 计算与内存

| 维度 | 规格 |
|:-----|:-----|
| Arm CPU | 最多 **16×Armv8.2+ A78 Hercules（64-bit）**；8MB L2；16MB LLC 系统缓存 |
| 可编程数据路径加速器 | **16 核 / 256 线程**，DOCA 编程，重多线程应用加速 |
| DDR | **双 DDR5 5600MT/s 控制器**；16GB 板载 DDR5；ECC 支持 |

### 4.3 硬件加速清单

| 类别 | 特性 |
|:-----|:-----|
| 安全 | Secure Boot + PKA 可信根、安全固件更新、Flash 加密、Cerberus、功能隔离层、RegEx、MACsec/IPsec/TLS、AES-GCM 128/256、AES-XTS 256/512、连接跟踪（有状态防火墙）、PKA（RSA/DH/DSA/ECC）、TRNG |
| 存储 | SNAP（NVMe/VirtIO-blk）、NVMe-oF/NVMe-TCP 加速、解压引擎、纠删码 RAID、M.2/U.2 直连 |
| 网络 | RoCE、Zero Touch RoCE、ASAP²、SR-IOV、VirtIO 加速、Overlay（VXLAN/GENEVE/NVGRE）、可编程 flexible parser、连接跟踪（L4 FW）、流镜像/采样/统计、Header rewrite、分层 QoS、Stateless TCP offloads |
| HPC/AI | All-to-All 引擎、GPUDirect、GPUDirect Storage（GDS）、MPI Tag Matching |
| 时序 | IEEE 1588v2、G.8273.2 Class C、PHC、线速硬件时间戳、SyncE（G.8262.1 eEEC）、PPS In/Out、时间触发调度、Time-based SDN |

### 4.4 启动与管理

| 维度 | 规格 |
|:-----|:-----|
| 启动 | Secure Boot（RSA 认证）、远程以太/iSCSI boot、PXE、UEFI |
| 带外管理 | **1GbE OOB 管理口**、NC-SI、MCTP over SMBus/PCIe、PLDM（Monitor&Control DSP0248 / Firmware Update DSP026）、I2C、SPI、eMMC、UART、USB |

### 4.5 内存架构的"指纹"解读（第一性原理）

| 维度 | BF3（16GB DDR5） | 对比：E2100（48GB LPDDR4x） | 对比：Salina 400（128GB DDR5） |
|:-----|:-----------------|:--------------------------|:------------------------------|
| 内存角色 | 控制平面 + 可编程加速器（数据面在硬件引擎内） | 软件数据面工作集（包缓冲/表项/应用） | P4 表项 + 连接状态 + 大规模虚拟化 |
| 容量逻辑 | 硬件引擎不需要大内存 | 16 核软件栈需要大内存 | 500 万连接 × 每连接状态 → 大容量 |
| **架构信号** | **"带控制器的网络芯片"** | "跑软件的机器" | "带大表项的交换芯片" |

> **洞察**：内存大小不是配置差异而是架构指纹。BF3 只需 16GB 恰恰证明其数据面在硬件引擎内完成——这是"硬件引擎数据面"路线最直接的物证[来源: 知识库 DPU 三方对比 §4.5]。

---

## 5. 形态与型号矩阵

### 5.1 已知形态与 OPN（官方公开部分）

| 形态 | 端口 | 型号/OPN | 关键事实 |
|:-----|:-----|:---------|:---------|
| FHHL（标准） | 2×200GbE/NDR200（合计 400G） | B3220 系列（如 MBF2H332A 类） | Datasheet 封面形态：双口 200G FHHL |
| 双宽 400G（HHHL 加宽） | 2×200GbE（合计 400G） | NVIDIA SKU **900-9D3B6** | STH 2022-12 实物：双宽、8-pin 供电、带 1PPS/10MHz 时同步口与背板 |
| OCP 3.0 / 其他 | 1×400G 或 4 端口 | — | Datasheet Portfolio 提到 1/2/4 端口与 HHHL/FHHL |
| **自宿主版（SH）** | 同标准版 | **B3220SH** | 暴露 PCIe root complex，SSD/GPU 可作下游设备挂载，用于存储服务器 |

[来源: NVIDIA BF3 Datasheet + STH 400G Exposed + STH Self-Hosted]

> ⚠️ **数据缺口声明**：NVIDIA 官方 Datasheet 未公开完整 OPN 矩阵与每 SKU 功耗。已知事实：400G 版为**双宽 + 8-pin 辅助供电**（STH 实物确认，功耗显著高于单槽 BF2）；标准 2×200G FHHL 为单宽。**采购前必须向 NVIDIA/代理索取官方 OPN 表与功耗规格书核对**（与 CX7 文档 §9.2 的"待澄清口径"同理）。

### 5.2 形态演进：从单槽到双宽

BF2 是单槽低功耗方案；BF3 400G 版因 Arm 核 + 16GB DDR5 + 硬件引擎 + 高速光模块供电需求，升级为**双宽卡**，散热片偏移设计为 QSFP 光模块留出气流通道，带加固背板（PCB 夹在散热片与背板之间分摊机械应力）[来源: STH 400G Exposed + 评论区]。

---

## 6. 与 ConnectX-7 的关系辨析

| 维度 | ConnectX-7（CX7） | BlueField-3（BF3） |
|:-----|:-----------------|:-------------------|
| 本质 | SmartNIC（纯网络加速） | **DPU（网络 + 计算 + 存储 + 安全）** |
| Arm 核 | ❌ 无 | ✅ 16×A78 + 16GB DDR5 |
| 可编程数据路径 | ❌ | ✅ 16 核/256 线程（DOCA） |
| PCIe | Gen5 x16 | **Gen5 x32（16 下游 + NTB）** |
| 典型功耗 | ~25W（400G SKU） | 更高（双宽 + 8-pin，官方未公开数字） |
| 定位 | 训练网 Scale-Out 主力 NIC | 基础设施卸载 / SuperNIC / 存储节点主机 |
| 软件栈 | 网卡驱动（MLNX_OFED） | **DOCA 全栈 + Linux（Arm 子系统）** |

> **关键认知**：BF3 的**网络引擎与 CX7 同源**（ConnectX-7 技术），因此 CX7 的网络特性（RoCE/DCQCN/GPUDirect/集群体/时序）在 BF3 上全部继承；BF3 的增量是 **Arm 计算 + 大内存 + x32 PCIe + DOCA 可编程性**——即"把基础设施服务跑在网卡上"的能力[来源: NVIDIA BF3 Datasheet + 知识库 CX7 文档]。

**工程选型分界**：
- 只要**高性能网络**（训练网 Scale-Out）→ CX7 即可（低功耗、低成本）；
- 需要**基础设施卸载/隔离**（云虚拟化、存储服务、安全网关、多租户）→ BF3；
- 需要**无主机存储节点/JBOF 控制器** → BF3 SH 版[来源: 知识库 DPU 三方对比 §7 + CX7 文档 §11]。

---

## 7. 软件生态：DOCA

### 7.1 DOCA 定位

NVIDIA 将 DOCA 定义为"DPU 界的 CUDA"——面向 BlueField/ConnectX 的软件开发框架，提供库、驱动、微服务，目标是把基础设施服务（网络/存储/安全）变成可编程的应用[来源: STH Hot Chips 33 报道 + NVIDIA 平台页]。

### 7.2 编程模型与锁定风险

| 维度 | 说明 |
|:-----|:-----|
| 可编程层级 | 数据路径加速器（256 线程）+ 控制面（Arm Linux） |
| 开发门槛 | 中（需学 DOCA API，Linux 工程师基础即可上手） |
| 生态成熟度 | 三家中最成熟（NVIDIA 强推，VS Code 插件/算子库齐全） |
| **锁定风险** | **高**——DOCA 生态绑定（迁移成本高，与 CUDA 同理） |

[来源: 知识库 DPU 三方对比 §4.4]

> **判断**：生态是 DPU 真正的护城河。DOCA 的成熟度是 BF3 的竞争优势，但也是采购方的绑定成本——**选 BF3 即默认接受 NVIDIA 基础设施栈**，与 GPU 平台选型强耦合[来源: 知识库 DPU 三方对比 §4.4 + §6]。

---

## 8. 电气/热/环境规格

| 维度 | 已知事实 | 状态 |
|:-----|:---------|:-----|
| 供电 | 400G 版带 **8-pin 辅助供电**（12V 级），标准 FHHL 由 PCIe 槽供电 | ✅ STH 实物确认 [来源: STH 400G Exposed] |
| 功耗 | 官方 Datasheet **未公开数字**；400G 版为双宽卡，显著高于单槽 BF2（~15-25W 级） | ⚠️ 缺口，需官方规格书 |
| 散热 | 散热片偏移设计（给 QSFP 光模块气流）；推测 vapor chamber；加固背板 | ✅ STH 实物/评论区 |
| 环境 | 数据中心服务器场景（Datasheet 未给温度范围，参考同代 CX7：工作 0-55°C） | ⚠️ 部分推断 |
| 认证 | CE/FCC/RoHS 级（NVIDIA 数据中心产品标准） | ⚠️ 未逐项核实 |

> **工程提示**：BF3 是双宽 + 辅助供电的高功耗板卡，**机箱选型必须预留双槽位 + 8-pin 供电 + 充足气流**；对比 CX7 的 25W 单槽形态，BF3 的部署密度与供电要求显著更高（BOM 规划时功耗预算要单独核算）[来源: STH 400G Exposed + 知识库 CX7 文档 §8]。

---

## 9. 应用场景与部署

### 9.1 场景矩阵

| 场景 | BF3 角色 | 关键能力 | 状态（2026） |
|:-----|:---------|:---------|:------------|
| **AI 集群（NVIDIA 生态）** | SuperNIC（Spectrum-X 组合）/ IB 网卡 | RoCE/GPUDirect/GDS/All-to-All 硬件卸载 | 量产主力 [来源: STH SuperNIC + 平台页] |
| 云网络（多租户） | 虚拟化前端（ASAP² vSwitch 卸载） | 25-40% CPU 释放、租户隔离 | 超大规模云部署 [来源: 知识库 DPU 三方对比] |
| **存储（无主机节点）** | **SH 自宿主版当主机 CPU** | SNAP + NVMe-oF + PCIe root（挂 SSD/GPU） | SC24 展示多款存储服务器采用 [来源: STH Self-Hosted] |
| JBOF/KV Cache | 存储控制器 | NVMe-oF target、解压/纠删码、GDS | AIC F2032 类 JBOF 配套 [来源: 知识库 CMX 文档 + STH] |
| 安全网关 | 零信任基础设施 | Cerberus 可信根 + 线速加密 + 有状态 FW | 企业/边缘 [来源: NVIDIA Datasheet] |
| 5G/电信 | 边缘网关 | 1588v2 G.8273.2 C、PPS/10MHz、时间触发调度 | 电信版 [来源: NVIDIA Datasheet + STH] |

### 9.2 对我方超节点项目的意义（知识库口径对照）

| 我方场景 | BF3 适用性 | 依据 |
|:---------|:-----------|:-----|
| 训练网 Scale-Out（RoCEv2） | ⚠️ CX7 已够用；BF3 仅在需**基础设施卸载/隔离**时增值 | 网络引擎同源，纯网络场景 CX7 功耗/成本更优（CX7 文档 §11） |
| 存储网络（KV Cache/数据加载） | ✅ BF3/BF4 STX 是 AI 存储方向（GDS + NVMe-oF + SH） | 知识库 CMX/KV Cache 系列结论 |
| 调度/管理服务器 | ✅ BF3 2×200G 形态（400G 一分二接双 TOR） | 知识库 08-20 superpod 实施设计 |
| 多租户云服务 | ✅ ASAP² + SR-IOV + 安全隔离 | NVIDIA Datasheet |

---

## 10. 竞品对比

### 10.1 三大 400G 时代 DPU 参数对比（2026-08-11 核实）

| 维度 | NVIDIA BF3 | Intel E2100 | AMD Salina 400 |
|:-----|:-----------|:------------|:---------------|
| 发布时间 | 2022（量产 2023） | 2024-05 正式发布 | 2024-11 曝光 |
| Arm 核 | 16×A78 + 16MB LLC | 16×N1 + 32MB | 16×N1 |
| 内存 | **16GB DDR5（双通道）** | 48GB LPDDR4x | 最高 128GB DDR5 |
| 网络 | **400G 以太 / NDR 400G IB** | 200G 以太 | 双 400GbE |
| 主机接口 | **PCIe Gen5 x32** | PCIe Gen4 x16 级 | PCIe Gen5 x16 |
| 数据平面 | **固定硬件引擎 + 256 线程可编程** | 软件（Arm）+ P4 辅助 | 232×P4 MPU 流水线 |
| RDMA | ✅ RoCE 硬件卸载 | ❌ | ⚠️ P4 RoCEv2 辅助 |
| AI 加速 | ✅ All-to-All/GPUDirect/GDS | ❌ | ❌（Vulcano 分工） |
| 安全 | 全家桶（Cerberus/线速加密/RegEx） | QAT 衍生基础 | P4 可编程（500 万连接/秒） |
| 存储 | SNAP/NVMe-oF/解压/纠删码 | NVMe-oF | 未披露 |
| 软件栈 | **DOCA（最成熟）** | IPDK（开源，社区弱） | P4 生态 |
| 当前状态 | 量产主力（BF4 已发布） | 独立线边缘化→Xeon SoC | Helios 采用 |

[来源: 知识库 DPU 三方对比 §2 参数总表（一手规格：NVIDIA Datasheet/STH/Hot Chips）]

### 10.2 竞品结论

- **AI 集群场景 BF3 结构性领先**（RDMA 硬件卸载 + GPUDirect + AI 原生引擎）；
- **灵活性对比**：E2100 最高（软件）但性能代差；Salina 400 折中（P4 语言边界内）；
- **平台绑定是决定性因素**：三家都在平台化——选型必须与 GPU/CPU 平台绑定看，单卡性能对比脱离平台语境无意义[来源: 知识库 DPU 三方对比 §6-7]。

---

## 11. 代际演进与平台化趋势

```
NVIDIA: BlueField-3 --> BlueField-4 (800G) --> GB system / STX storage
        400G line-rate      +Vera CPU (STX)         (capability folded into
        16GB DDR5           32GB DDR5 / more Arm    GPU platform)
```

> 注：BF4 STX 版 = Vera CPU + ConnectX-9 存储处理器（存储侧 CPU + 数据路径引擎）[来源: NVIDIA 平台页]

| 维度 | BlueField-3 | BlueField-4 | 变化 |
|:-----|:------------|:------------|:-----|
| 网络 | 400Gb/s | **800Gb/s** | 2× |
| 定位 | 400G 基础设施平台 | **Scale-In 网络（agentic AI 工厂）** | 从 Scale-Out 到 Scale-In |
| 计算 | 16×A78 | **64×Neoverse V2（Grace；STX 版=2×84 核 Vera）** | 算力 6× |
| 存储 | SNAP/NVMe-oF | AI 原生存储（压缩+加密流水线，Vera 比 x86 高 3.21×） | AI 存储深化 |

[来源: NVIDIA BlueField 平台页（2026）+ STH BF4 报道]

> **战略判断**：BF3 已进入**成熟期向换代期过渡**（2026 年 NVIDIA 主推 BF4 800G，BF3 退居二线用于存量与成本敏感场景）；但 BF3 的**架构范式（硬件引擎 + Arm + 可编程旁路）与生态（DOCA）在 BF4 完全延续**，本文档规格解读对 BF4 同样适用（速率/核数/内存按比例升级）。可证伪预测：2027 年 BF3 仍是 NVIDIA 在售 400G DPU 主力，但新设计默认选 BF4[来源: 知识库 DPU 三方对比 §8 预测 P2]。**BF4 完整规格与架构（Scale-In/ASTRA/STX）见同目录 [BF4 规格解读报告](2026-08-28-bluefield4-bf4-spec-deep-analysis.md)**。

---

## 12. BOM 选型建议

### 12.1 场景决策树

**场景决策树**：

- **AI 训练网 Scale-Out（NVIDIA 生态）** → CX7（纯网络，低功耗）或 BF3 SuperNIC（需隔离/卸载）
- **需要基础设施卸载**（云虚拟化/多租户/安全）→ BF3 标准版（DOCA 编程）
- **无主机存储节点 / JBOF 控制器** → BF3 SH 自宿主版（B3220SH，PCIe root 挂 SSD/GPU）
- **AI 存储**（KV Cache/数据加载）→ BF3/BF4 STX（GDS + NVMe-oF + 解压/纠删码）
- **电信/5G 边缘** → BF3 电信版（PPS/10MHz/SyncE/时间触发调度）
- **纯以太 400G 训练（非 NVIDIA 生态）** → 对比 Broadcom/国产 400G NIC（无 Arm 溢价）

### 12.2 采购规格清单（RFP 要点）

| 项目 | 要求 | 验证方法 |
|:-----|:-----|:---------|
| OPN 冻结 | 明确 NVIDIA SKU + Legacy OPN 双编号（如 900-9D3B6 类） | 向 NVIDIA/代理索取官方 OPN 表 |
| 形态确认 | 400G 版=双宽+8-pin 供电；2×200G 版=FHHL 单宽 | 实物/规格书核对（STH 已确认双宽） |
| PCIe 通道 | 确认主板槽位 x16（400G 需 Gen5 x16 跑满） | 主板规格书 + lspci |
| 功耗预算 | 官方未公开 → 必须向代理索取 TDP 数字 | 机箱供电/散热核算（双宽 + 8-pin） |
| 时同步 | 电信/边缘场景确认 PPS/10MHz 端口存在 | 实物检查（STH 确认） |
| DOCA 版本 | 与目标应用（vSwitch/存储/安全）匹配的 DOCA SDK 基线 | NVIDIA DOCA 发布说明 |
| 软件锁定 | 明确接受 DOCA 生态绑定 / 或有开源替代路径 | 生态评估（§7） |
| 固件基线 | BF3 与 CX7/BF4 混用时镜像多基线管理 | 装机流程核对 |

### 12.3 关键风险提示

1. **平台绑定**：BF3 价值在 NVIDIA 生态内最大化（GPU + Quantum/Spectrum + DOCA），脱离平台单买不划算；
2. **生态锁定**：DOCA 编程模型绑定，迁移成本高——重大选型前做 PoC；
3. **功耗与形态**：双宽 + 8-pin + 高功耗（数字未公开）→ 机箱/供电/散热三要素预核；
4. **换代节奏**：BF4（800G）已发布，400G 新项目评估 BF3 vs BF4 生命周期；
5. **数据缺口**：无权威第三方统一 DPU 基准（无 MLPerf 类标准）——性能对比停留在规格层，采购必须实测（时延/吞吐/CPU 释放/功耗 4 项）[来源: 知识库 DPU 三方对比 §5]。

---

## 13. 参考文献

[1] NVIDIA, *NVIDIA BlueField-3 DPU Datasheet*（官方 PDF，2026-08-28 抓取）— 网络/计算/内存/加速引擎/启动/管理全规格 [来源: [1]]

[2] ServeTheHome, *NVIDIA BlueField-3 DPU Architecture at Hot Chips 33*, 2021-08-23 — 16×A78/256 线程加速器/双 OS 独立架构/DOCA 定位 [来源: [2]]

[3] ServeTheHome, *NVIDIA BlueField-3 400Gbps DPU Exposed*, 2022-12-09 — 双宽/8-pin/900-9D3B6/时同步口/背板实物 [来源: [3]]

[4] ServeTheHome, *NVIDIA BlueField-3 Self-Hosted Version*, 2024-11-27 — B3220SH/PCIe root complex/存储服务器场景 [来源: [4]]

[5] ServeTheHome, *NVIDIA Goes Ethernet for AI and Copies SuperNIC for BlueField-3 Brand*, 2023-11-20 — SuperNIC 品牌/Spectrum-X 组合 [来源: [5]]

[6] NVIDIA, *BlueField Networking Platform*（官方平台页，2026-08-28 抓取）— BF4 800G/BF4 STX Vera CPU/Scale-In 定位 [来源: [6]]

[7] 知识库, *2026-08-11-dpu-three-way-e2100-bf3-salina400* — 三大 DPU 数据平面范式/参数总表/平台化趋势 [来源: [7]]

[8] 知识库, *2026-08-28-connectx7-cx7-spec-deep-analysis* — CX7 全家族规格（BF3 网络引擎同源，格式模板）[来源: [8]]

[9] 知识库, *2026-08-11-domestic-dpu-competitive-analysis*（03_management/08_competitive-analysis/）— 国产 DPU 竞品与平台化结论 [来源: [9]]

[10] 知识库, *2026-08-11-dpu-platformization-product-plan*（01_product/）— DPU 能力平台化产品规划三路径 [来源: [10]]

---

## 14. 变更记录

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-28 | v1.1 | 数据修正：§2.1/§11 BF4 预告数据按官方 Datasheet 更新（64×Neoverse V2 + 128GB LPDDR5x；STX=2×84 核 Vera + 384GB），§11 增加 BF4 文档交叉链接 |
| 2026-08-28 | v1.0 | 首次创建：基于 NVIDIA 官方 Datasheet（一手）+ STH 四篇一手报道（Hot Chips 33 架构/400G 实物/Self-Hosted/SuperNIC）+ 知识库 DPU 三方对比与 CX7 规格文档，输出 BF3 全家族规格解读（网络/计算/内存/加速引擎/形态）与工作原理（异构架构/双 OS/数据平面范式/内存指纹）、竞品对比、BOM 选型建议；功耗与完整 OPN 矩阵标注为数据缺口 |
