# NVIDIA BlueField-4 (BF4) DPU 规格解读报告 — 核心规格参数与工作原理

> **元信息**: 文件状态=正式版 v1.0 | 覆盖范围=BlueField-4 DPU（Grace 版）+ BlueField-4 STX 存储处理器（Vera 版）全规格（网络/计算/内存/加速引擎/安全/存储/管理/形态）与工作原理（Scale-In 架构/ASTRA/自宿主） | 版本=1.0
> **适用范围**: 服务器平台规划 / DPU BOM 选型 / AI 集群 Scale-In 与 Scale-Out 网络设计 / AI 原生存储（CMX/KV Cache/JBOF）评估 / Vera Rubin 平台理解

## 目录

- [1. 引言与范围](#1-引言与范围)
- [2. 产品定位与代际演进](#2-产品定位与代际演进)
- [3. 芯片架构与工作原理](#3-芯片架构与工作原理)
- [4. 核心规格参数总表](#4-核心规格参数总表)
- [5. 形态与型号矩阵](#5-形态与型号矩阵)
- [6. 与 ConnectX-9 的关系辨析](#6-与-connectx-9-的关系辨析)
- [7. BF4 STX 存储处理器专章](#7-bf4-stx-存储处理器专章)
- [8. 软件生态：DOCA 与 Scale-In 微服务](#8-软件生态doca-与-scale-in-微服务)
- [9. Scale-In 网络架构：第五支柱](#9-scale-in-网络架构第五支柱)
- [10. 电气/热/环境规格](#10-电气热环境规格)
- [11. 应用场景与部署](#11-应用场景与部署)
- [12. 竞品对比](#12-竞品对比)
- [13. BOM 选型建议](#13-bom-选型建议)
- [14. 参考文献](#14-参考文献)
- [15. 变更记录](#15-变更记录)

---

## 1. 引言与范围

### 1.1 文档目的

本文档对 NVIDIA BlueField-4（下称 **BF4**）进行**规格级深度解读**，回答三个问题：

1. **是什么**：BF4 的完整规格参数（网络/计算/内存/加速引擎/形态/管理）——涵盖 BF4 DPU（Grace 版）与 BF4 STX 存储处理器（Vera 版）两个产品线；
2. **怎么工作**：芯片级架构与各卸载引擎的原理（为什么 64 核 CPU 仍要硬件引擎跑 800G 线速、128GB LPDDR5x 的架构含义、Scale-In 与 Scale-Out 如何分工、ASTRA 如何把安全控制延伸到东西向流量）；
3. **怎么用**：在 Vera Rubin 平台、AI 工厂 Scale-In 网络、CMX/KV Cache 存储、JBOF、云多租户场景的部署口径与 BOM 选型要点。

### 1.2 目标读者

服务器/数据中心硬件工程师、网络架构师、BOM 与采购负责人、AI 基础设施规划者、存储架构师。

### 1.3 覆盖范围

- **BF4 DPU（标准版，Grace CPU）**：网络/计算/内存/加速引擎/安全/存储/管理全规格
- **BF4 STX 存储处理器（Vera CPU）**：自宿主存储架构、双 STX 3.2Tb/s 配置、DOCA Memos
- 与 ConnectX-9（网络引擎同源）、BlueField-3（前代）、Xsight Labs E1 / Broadcom Thor Ultra（竞品）的边界关系
- 不覆盖：DOCA 应用开发细节（见 NVIDIA DOCA 文档）、Vera Rubin GPU/CPU 平台本身（另见知识库超节点文档）

### 1.4 术语表

| 术语 | 含义 |
|:-----|:-----|
| DPU | Data Processing Unit，数据中心基础设施处理单元 |
| Scale-In | NVIDIA 第五网络支柱：主机与数据中心之间南北向基础设施加速域（BF4 主场） |
| Scale-Out | 训练/推理集群东西向横向扩展网络（ConnectX-9 SuperNIC + Spectrum-X 主场） |
| ASTRA | Advanced Secure Trusted Resource Architecture，BF4 安全可信资源架构（跨 Scale-In/Scale-Out 统一策略） |
| Vera CPU | NVIDIA 新一代服务器 CPU（Arm Neoverse V2 定制，BF4 STX 存储处理器计算核心） |
| Grace CPU | NVIDIA 上一代 Arm CPU（Neoverse V2，BF4 DPU 标准版计算核心） |
| LPDDR5x | 低功耗 DDR5x 板载内存（BF4 用，4× BF3 内存带宽） |
| DOCA | NVIDIA 数据中心基础设施编程框架（DPU 的 "CUDA"） |
| CMX | NVIDIA Context Memory（KV Cache 上下文内存存储系统，基于 STX 模块化基础） |
| DOCA Memos | DOCA 内存对象存储微服务（KV cache 跨层级智能放置） |
| SNAP | BlueField SNAP，弹性块存储（NVMe/VirtIO-blk 映射） |
| Socket Direct | NVIDIA PCIe 直连技术（CPU↔DPU 免 PCIe switch 直连） |
| OPN | Ordering Part Number，订货型号 |
| PQC | Post-Quantum Cryptography，后量子密码（BF4 STX 支持） |
| SPDM | Security Protocol and Data Model（设备认证，DMTF DSP0274） |
| SuperNIC | NVIDIA 专为 AI 训练网络优化的 ConnectX 网卡品牌 |

---

## 2. 产品定位与代际演进

### 2.1 BlueField 家族代际

| 代际 | 发布年 | 网络速率 | PCIe | Arm 核 | 内存 | 定位 |
|:-----|:------:|:--------:|:----:|:------:|:-----|:-----|
| BlueField-1 | 2019 | 25/100GbE | Gen3 x16 | 8×A72 | 16GB DDR4 | 试水（STH 评论称"trial balloon"） |
| BlueField-2 | 2020 | 100GbE / HDR100 | Gen4 x16 | 8×A72 | 16GB DDR4 | 量产主力（ConnectX-6 + Arm） |
| BlueField-3 | 2022 | 400GbE / NDR 400G | Gen5 x32 | 16×A78 | 16GB DDR5 | 第三代基础设施 on-a-chip（见 BF3 文档） |
| **BlueField-4** | **2025 宣布 / 2026 量产** | **800GbE / 800G per port** | **Gen6 x16** | **64×Neoverse V2（Grace）** | **128GB LPDDR5x** | **AI 原生 Scale-In 基础设施引擎（本文主角）** |
| **BF4 STX** | **2026（2026H2 生态可用）** | **3.2Tb/s（双 STX）** | **Gen6 x96** | **2×84 核 Vera（Neoverse V2）** | **384GB LPDDR5x** | **AI 原生存储处理器（CMX/存储节点 CPU+数据路径引擎）** |

> BF4 于 **GTC DC 2025（2025-10-28）** 正式宣布：800G + ConnectX-9 网络 + 64 核 Arm CPU，**1260 亿晶体管**，作为 Vera Rubin 平台组成部分于 2026 年早期可用 [来源: STH GTC DC 2025 报道 + NVIDIA 官方]。**Hot Chips 2026（2026-08-25）** 公开完整架构规格 [来源: STH Hot Chips 2026 报道]。

> ⚠️ **对 BF3 文档 §11 的数据修正**：BF3 文档的 BF4 预告表（2026-08-28 早先创建）基于旧信息写"16×Arm + 32GB DDR5"。**官方 Datasheet（2026-06 JUN26 版）确认**：BF4 DPU 为 **64×Arm Neoverse V2（Grace）+ 128GB LPDDR5x**；BF4 STX 为 **2×Vera CPU（每颗最多 84 核）+ 384GB LPDDR5x**。本文档为权威口径，BF3 文档 §11 已同步修正。

### 2.2 在 NVIDIA 网络矩阵中的位置：Scale-In 第五支柱

NVIDIA 将 AI 工厂网络划分为**五个基础设施支柱**，BF4 是第五支柱（Scale-In）的载体 [来源: NVIDIA 技术博客 2026-08-24]：

```text
AI Factory Network Pillars (NVIDIA, 2026)
+---------------------------------------------------------------+
| Pillar            | Domain              | Primary HW          |
|-------------------|---------------------|---------------------|
| Scale-Up          | GPU coherent as one | NVLink              |
| Scale-Out         | server-to-server    | ConnectX-9 + Spec-X |
| Scale-Across      | multi-datacenter    | Spectrum-XGS        |
| Context Memory    | shared KV cache     | CMX on STX modular  |
| Scale-In  <==BF4  | host<->DC access    | BF4 + DOCA + Spec-X |
+---------------------------------------------------------------+
```

**Scale-In 的定义**：把传统"南北向"（north-south）网络升级为 AI 工厂的统一加速基础设施域——连接用户/应用/数据源/存储/服务到 AI 算力，承载访问、安全、数据移动、多租户隔离与基础设施运维。BF4 是**主机无关（host-independent）**的基础设施处理器：安全策略、服务状态、遥测都在租户主机之外运行，不消耗主机 CPU [来源: NVIDIA 技术博客 2026-08-24]。

### 2.3 "DPU 为什么需要 64 核 CPU"——架构重心转移

BF3 时代 DPU 的核心矛盾是"硬件引擎做确定性数据面 + Arm 做控制面"（见 BF3 文档 §2.3）。BF4 的架构重心发生**代际转移** [来源: STH Hot Chips 2026 报道]：

| 维度 | BF3 | BF4 | 变化原因 |
|:-----|:----|:----|:---------|
| 通用算力 | 16×A78 | **64×Neoverse V2（6× 算力）** | 安全/存储/遥测服务并发运行，控制面负载剧增 |
| 网络 | 400G | **800G（2× 带宽）** | Vera Rubin 托盘聚合带宽需求 7.2Tb/s |
| 内存带宽 | DDR5 双通道 | **LPDDR5x（4× 带宽）** | 策略/遥测数据集 + 存储服务工作集 |
| 角色 | 可选插卡（bump-in-the-wire） | **co-designed 进每个 Vera Rubin 系统** | 从"给服务器加卡"到"平台级基础设施域" |

> **第一性推论**：BF4 把 DPU 从"网络加速器"升级为"**基础设施主权节点**"（NVIDIA 官方定位：DPU 是平台的**可信实体**——主机前的服务器，隔离主机与数据中心网络，**拥有租户数据路径**）[来源: STH Hot Chips 2026 报道]。算力重心从"卸载"转向"卸载 + 治理"：64 核 CPU 不是为了跑更多网络功能，而是为了在**主机之外**承载安全策略、存储服务与遥测编排。

---

## 3. 芯片架构与工作原理

### 3.1 芯片本体：Grace/ConnectX-9 异构集成（BF4G）与 Vera/ConnectX-9 自宿主（BF4V）

BF4 存在**两个产品线**（STH 建议命名 BF4G/BF4V 以区分）[来源: STH Hot Chips 2026 报道]：

| 产品线 | CPU | 网络 | 内存 | 架构角色 |
|:-------|:----|:-----|:-----|:---------|
| **BF4 DPU（标准版）** | Grace 64×Neoverse V2 | 单 ConnectX-9（800G） | 128GB LPDDR5x | 主机前置基础设施处理器（PCIe Gen6 x16 插卡） |
| **BF4 STX 存储处理器** | 1×或 2×Vera（每颗 ≤84 核） | 多 ConnectX-9（双 STX 3.2Tb/s） | 384GB LPDDR5x（双 STX） | 存储侧 CPU + 数据路径引擎（自宿主，PCIe Gen6 x96） |

> 官方 Datasheet 对两个产品线都使用 "BlueField-4" 品牌，STH 已反馈建议用 BF4G（Grace）/BF4V（Vera）区分 [来源: STH Hot Chips 2026 报道]。本文沿用此命名约定。

核心能力分层（BF4G，第一性原理拆解，与 BF3 §3.1 对照）：

| 层 | 职责 | BF4 实现 | vs BF3 |
|:---|:-----|:---------|:-------|
| 物理层 | 信号编解码 | 以太 **800G per port（200G PAM4 SerDes）**，25G NRZ 兼容；PCIe **Gen6** 64GT/s | 速率 2×，PCIe 代际 +1 |
| 数据通路 | 报文收发 | ConnectX-9 硬件引擎 + DMA + **内联加密** | 内联加密为 BF4 新增 |
| 传输层 | 可靠传输 | RoCEv2、**可编程 RDMA 传输**、**可编程拥塞控制** | RDMA 传输/拥塞控制可编程化 |
| 服务层 | 协议终结 | VXLAN/NVGRE/Geneve、可编程 flexible parser、**DOCA 可编程转向**、服务功能链（SFC） | 原生 SFC 为 BF4 新增 |
| 计算层 | 通用处理 | **Grace 64×Neoverse V2 @1.7GHz** + 可编程数据路径加速器（16 核/256 线程） | 核数 4×，ISA 升级 |
| 安全层 | 加密/信任 | Secure Boot（硬件可信根）、**SPDM 1.1/1.2 设备认证**、AES-GCM 128/256（IPsec/TLS/PSP）、AES-XTS 256/512、有状态防火墙、**实时 AI 威胁检测** | SPDM/威胁检测为 BF4 新增 |
| 存储层 | 存储服务 | SNAP、NVMe-oF、**S3 over RDMA**、NVMe/TCP、T10-Diff、**GDS**、**512GB 板载 SSD** | S3/RDMA、T10-Diff 为 BF4 新增 |

[来源: NVIDIA BF4 DPU Datasheet（2026-06 JUN26）+ STH Hot Chips 2026 报道]

### 3.2 双 OS 独立架构（BF3 延续 + 管理域增强）

```text
 +--------------------------------------------------------------+
 |  BF4 DPU (BF4G) Die                                           |
 |  +----------------------+  +--------------------------------+ |
 |  | Arm Subsystem        |  | NIC Subsystem                  | |
 |  | Grace 64x Neoverse V2|  | ConnectX-9 engine              | |
 |  | 128GB LPDDR5x        |  | (independent RTOS)             | |
 |  | Linux + DOCA         |  | 800G line-rate data plane:     | |
 |  | Control plane /      |  | RX/TX/offload/crypto/storage   | |
 |  | Scale-In services /  |  | /inline encryption             | |
 |  | telemetry / security |  |                                | |
 |  +----------+-----------+  +----------------+---------------+ |
 |             | internal       |                                |
 |             v                v                                |
 |  +-------------------------------------------------------+   |
 |  | PCIe Gen6 x16 host link (Socket Direct) + integrated  |   |
 |  | DPU BMC (1GbE OOB, Redfish, MCTP/PLDM)                |   |
 |  +-------------------------------------------------------+   |
 +--------------------------------------------------------------+
```

**核心机制**（延续 BF3 双 OS 架构）：NIC 子系统与 Arm 子系统各自运行独立操作系统——NIC 跑实时 OS 保证 800G 线速数据面确定性，Arm 跑标准 Linux 承载控制面与 Scale-In 服务 [来源: NVIDIA BF4 Datasheet + STH Hot Chips 2026 报道]。

**BF4 的增强**：集成 **DPU BMC**（带外管理域）——1GbE OOB 管理口、Redfish（HTTPS/TLS）、NSM over MCTP、PLDM over MCTP（FW 更新 DSP0267 / 监控 DSP0248 / Redfish DSP0218 / FRU DSP0257），管理面完全主机无关 [来源: NVIDIA BF4 DPU Datasheet]。

> **工程意义**：BF4 的管理域（BMC 级）+ 控制域（Arm Linux）+ 数据域（NIC RTOS）三域隔离，是"零信任基础设施"的物理基础——主机（含其 OS 被攻破的情况）无法触达策略执行点。这是 BF4 相对 BF3 最大的架构级差异之一。

### 3.3 数据平面范式：硬件引擎 + 可编程旁路（BF3 路线延续 + 可编程化加深）

BF4 延续 BF3 的"**固定硬件引擎 + 可编程旁路**"数据平面范式，但两处深化 [来源: NVIDIA BF4 DPU Datasheet + NVIDIA 技术博客 2026-08-24]：

1. **硬件引擎覆盖面扩大**：新增**内联加密/解密**（data-in-motion 在硅上完成，不再需要 CPU 参与加密路径）、**可编程 RDMA 传输**、**可编程拥塞控制**（DOCA PCC）——把原属软件慢路径的能力下沉到硬件；
2. **服务功能链（SFC）原生化**：BF4 的多服务架构支持**原生服务功能链**——每个流量流按顺序通过所需服务（转向→安全→存储→遥测），避免多服务串行时的重复报文拷贝 [来源: NVIDIA BF4 DPU Datasheet]。

| 数据平面组件 | 执行者 | 性能 | 灵活性 |
|:-------------|:-------|:----:|:------:|
| ConnectX-9 固定硬件引擎 | 硅上专用电路 | 800G 线速 | 低（引擎内） |
| 可编程数据路径加速器 | 16 核/256 线程 | 高（DOCA 编程） | 中（DOCA API 内） |
| Grace CPU（控制面） | 64 核 Neoverse V2 | 控制/慢路径 | 最高（Linux 应用） |

> **第一性推论**：BF4 的"可编程化下沉"方向与 AMD Salina（P4 流水线）趋同但路径不同——NVIDIA 用"硬件引擎 + DOCA 编程模型"而非 P4 语言。本质都是**把灵活性从 CPU 软件层下移到硅上**，以同时获得确定性性能与可演进性 [来源: 知识库 DPU 三方对比 §3.3]。

### 3.4 ASTRA：安全控制的 Scale-Out 延伸（BF4 独有架构）

**ASTRA（Advanced Secure Trusted Resource Architecture）** 是 BF4 的核心架构创新 [来源: NVIDIA BF4 DPU Datasheet + STH Hot Chips 2026 报道 + NVIDIA 技术博客 2026-08-24]：

```text
Vera Rubin NVL72 compute tray (7.2 Tb/s aggregate)
+-------------------------------------------------------------------+
|  Host (Vera CPU + Rubin GPU)                                      |
|    |  scale-in 800Gb/s                    scale-out 4x1.6Tb/s     |
|    v                                                        |     |
| +--------+  policy install/telemetry   +-------------------+      |
| | BF4    |<------ASTRA control-------->| ConnectX-9 x4    |      |
| | (owns  |                             | (SuperNIC,       |      |
| |  data  |  policy enforcement         |  enforce in      |      |
| |  path) |============================>|  data path)      |      |
| +--------+      (links: PCIe-like)     +-------------------+      |
+-------------------------------------------------------------------+
```

**工作原理**：
- **BF4 拥有 Scale-In 数据路径**（南北向 800Gb/s），同时通过 ASTRA 把**安全策略安装/更新与遥测收集**延伸到 Scale-Out 的 ConnectX-9 SuperNIC（东西向 4×1.6Tb/s）；
- ConnectX-9 **在数据路径内直接执行策略**（加密、隔离、零信任），不需要把东西向流量绕经 800G 的 BF4 接口（避免瓶颈）；
- 形成闭环：**策略集中编排（BF4/DOCA）+ 本地线速执行（ConnectX-9）**——7.2Tb/s 的 CSP 级安全与管理，遥测在线速收集、不触碰主机 [来源: STH Hot Chips 2026 报道]。

> **场景价值**：传统方案（无 DPU）下，Scale-Out 流量无法端到端安全隔离；且每块 NIC 需要独立 CPU/内存/管理连接，功耗约 **4×**（NVIDIA 官方口径）[来源: STH Hot Chips 2026 报道]。ASTRA 用一块 BF4 统一治理整个托盘的网络面，这是"平台级"设计而非"插卡级"设计的物证。

### 3.5 内存架构的"指纹"解读

| 维度 | BF3（16GB DDR5） | BF4G（128GB LPDDR5x） | BF4V STX（384GB LPDDR5x） |
|:-----|:-----------------|:----------------------|:--------------------------|
| 内存角色 | 控制平面 + 可编程加速器 | 控制平面 + **Scale-In 服务工作集**（策略/遥测/存储服务）+ 板载 SSD 缓存 | 存储侧 CPU 工作集 + **KV Cache 分级缓存** + 数据路径引擎 |
| 容量逻辑 | 硬件引擎不需要大内存 | 6× 算力 → 更多并发服务 → 更大策略/遥测数据集；**4× 内存带宽**支撑存储/安全服务 | 自宿主存储节点需要大内存做缓存与元数据处理 |
| **架构信号** | "带控制器的网络芯片" | "**带网络的控制平面服务器**" | "**无主机的存储服务器 SoC**" |

[来源: NVIDIA BF4 DPU Datasheet + NVIDIA 技术博客 2026-08-24 + STH Hot Chips 2026 报道]

> **洞察**：BF3→BF4 内存容量 8×、带宽 4×，不是参数堆料，而是**架构角色从"网络芯片"转向"基础设施服务器"**的物证——BF4 要在主机之外独立承载安全策略、存储服务与遥测编排（参考 BF3 文档 §4.5 的"内存指纹"方法论）。而 BF4 STX 的 384GB + 2TB SSD 则直接宣告：它是**存储节点的主机 CPU**，而非网卡。

---

## 4. 核心规格参数总表

> 全部数据来自 NVIDIA 官方 Datasheet（2026-06 JUN26 版，2026-08-28 抓取核实）+ Hot Chips 2026 披露 [来源: NVIDIA BF4 DPU Datasheet + STH Hot Chips 2026 报道]

### 4.1 网络与主机接口（BF4 DPU）

| 维度 | 规格 |
|:-----|:-----|
| 网络协议 | Ethernet + InfiniBand |
| 最大带宽 | **800 Gb/s** |
| 网络速率 | **800G per port**，200G SerDes；支持 200/100/50 Gb/s PAM4 与 25 Gb/s NRZ |
| 端口拆分 | 支持最多 **8 个 split 端口** |
| 主机接口 | **PCIe Gen6 x16**（64GT/s/lane 级）+ **NVIDIA Socket Direct** |

### 4.2 计算与内存（BF4 DPU）

| 维度 | 规格 |
|:-----|:-----|
| CPU | **Grace，64×Arm Neoverse V2 核** @ **1.7GHz**（Hot Chips 披露；频率低于 GB300 系统 Grace，为降功耗） |
| 算力增益 | 官方口径 **6×** BF3 计算能力（支撑多基础设施服务并发） |
| LPDDR5x | 最高 **128GB 板载 LPDDR5x**；带宽约 **275 GB/s**（Hot Chips 披露）；官方口径内存带宽 **4×** BF3 |
| 板载 SSD | 最高 **512GB 板载 SSD** |
| 可编程数据路径加速器 | **16 核 / 256 线程**，DOCA 可编程；重多线程应用加速；通用设备仿真 |
| 晶体管 | **1260 亿**（GTC DC 2025 披露） |

### 4.3 硬件加速清单（BF4 DPU）

| 类别 | 特性 |
|:-----|:-----|
| 网络安全 | 实时 AI 工作负载威胁检测、隔离信任域、有状态防火墙连接跟踪、AES-GCM 128/256（IPsec/TLS/PSP）、Secure Boot（硬件可信根）、安全固件更新、Flash 加密、**SPDM 1.1/1.2 设备认证** |
| AI 网络 | RDMA/RoCEv2、Spectrum-X Ethernet、**可编程 RDMA 传输**、**可编程拥塞控制**、**NIXL（Inference Transfer Library）**、GPUDirect RDMA、网内计算 |
| 云网络 | DOCA 可编程转向与包处理、VXLAN/NVGRE/Geneve 封装、可编程 flexible parser、无状态 TCP offloads |
| 存储发起端 | SNAP（文件系统/块存储仿真）、VirtIO/NVMe 仿真设备、NVMe-oF、**S3 over RDMA**、NVMe/TCP 客户端加速、T10-Diff、AES-XTS 256/512（静态）、实时数据访问控制、GPUDirect Storage |
| 管理控制 | 集成 DPU BMC、1GbE OOB、Redfish（HTTPS/TLS）、**ASTRA**、NSM over MCTP、PLDM over MCTP（DSP0267/0248/0218/0257） |
| 网络启动 | InfiniBand/Ethernet boot、PXE、UEFI |

### 4.4 BF4 STX 存储处理器规格（双 STX 配置）

| 维度 | 规格 |
|:-----|:-----|
| 网络 | **3.2 Tb/s**（双 STX），200/100 Gb/s SerDes PAM4，Spectrum-X 连接 |
| PCIe | **Gen6 x96 lanes** |
| 计算 | **双 Vera CPU，每颗最多 84×Neoverse V2 核**（共 168 核） |
| 内存 | **384GB 板载 LPDDR5x** |
| 板载 SSD | **2TB M.2 SSD + 冗余 M.2 插槽** |
| 数据路径加速器 | **64 核 / 1K 硬件线程**，DOCA 可编程 |
| 架构 | **自宿主（self-hosted）**：既是存储节点 CPU 又是数据路径引擎 |
| 安全 | **PQC + classical 双安全**（Secure Boot/固件更新硬件可信根）、SPDM 1.1/1.2、实时文件访问控制、多租户隔离、AES-GCM 128/256 内联（IPsec/TLS/PSP）、有状态防火墙 |
| 存储 | DOCA Memos（KV cache 智能分层）、NVMe-oF/NVMe-TCP target 加速、S3 over RDMA、T10-Diff、AES-XTS 256/512、实时数据访问控制、GDS |
| 管理 | System 级 + SMM 级 OOB 管理、USB/I2C/PCIe、NSM/PLDM over MCTP、监控/复位/恢复/安全升级 |

[来源: NVIDIA BF4 STX Datasheet（2026-06 JUN26）+ NVIDIA 新闻稿 2026-05-31]

### 4.5 与 BF3 的规格对比速览

| 维度 | BF3 | BF4 DPU | BF4 STX（双） | 倍数 |
|:-----|:----|:--------|:--------------|:----:|
| 网络带宽 | 400Gb/s | 800Gb/s | 3.2Tb/s | 2× / 8× |
| CPU 核 | 16×A78 | 64×Neoverse V2 | 2×84 核 Vera | 4× / 10.5× |
| 内存 | 16GB DDR5 | 128GB LPDDR5x | 384GB LPDDR5x | 8× / 24× |
| PCIe | Gen5 x32 | Gen6 x16（Socket Direct） | Gen6 x96 | — |
| 计算能力 | 基线 | 6× | （Vera 存储优化） | 6× |
| 内存带宽 | 基线 | 4× | — | 4× |

[来源: NVIDIA BF4/BF3 Datasheet + NVIDIA 技术博客 2026-08-24]

> ⚠️ 注意 PCIe 形态差异：BF4 DPU 主机接口是 **Gen6 x16**（相比 BF3 的 Gen5 x32 通道数减少但代际翻倍，总带宽相当——Gen6 x16 ≈ 128GB/s 级 vs Gen5 x32 ≈ 128GB/s 级，设计取舍是**用更高代际换更少通道数**，适配 Vera Rubin 的 Socket Direct 直连架构）。

---

## 5. 形态与型号矩阵

### 5.1 已知形态（官方公开部分）

| 产品线 | 形态 | 端口 | 关键事实 |
|:-------|:-----|:-----|:---------|
| BF4 DPU | PCIe 形态（标准） | 800G（可拆 8 端口） | Datasheet 官方确认 [来源: NVIDIA BF4 Datasheet] |
| BF4 DPU | NVIDIA 项目定制形态 | — | Vera Rubin 平台 co-design 形态（非标准插卡）[来源: NVIDIA BF4 Datasheet] |
| BF4 STX | 存储处理器模块（自宿主） | 单/双 STX（最高 3.2Tb/s） | 双 STX = 2 颗 Vera + 多 ConnectX-9 [来源: NVIDIA BF4 STX Datasheet] |

### 5.2 型号与 OPN

> ⚠️ **数据缺口声明**：NVIDIA 官方 Datasheet **未公开 OPN 矩阵、功耗、工作温度范围**。已知事实：STH 报道指出 BF4 有 "Grace + 单 ConnectX-9" 与 "单/双 Vera + 多 ConnectX-9" 多个版本共用 "BlueField-4" 品牌 [来源: STH Hot Chips 2026 报道]。**采购前必须向 NVIDIA/代理索取官方 OPN 表、功耗规格书与 SKU 级 datasheet 核对**（与 BF3 文档 §5.1 的"待澄清口径"同理）。

### 5.3 形态演进：从插卡到平台组件

BF3 是双宽 PCIe 卡（400G 版）；**BF4 的关键变化是"co-designed 进每个 Vera Rubin 系统"**——在 Rubin NVL72 中，BF4 不是可选加装，而是平台设计的一部分（ASTRA 需要 BF4 作为整个托盘的管理/安全锚点）[来源: STH Hot Chips 2026 报道]。这意味着 BF4 的形态取决于目标平台：
- **存量服务器/通用平台**：PCIe 插卡形态（Gen6 x16 槽位）；
- **Vera Rubin 平台**：定制形态（与托盘一体化设计）。

---

## 6. 与 ConnectX-9 的关系辨析

| 维度 | ConnectX-9（CX9） | BlueField-4（BF4） |
|:-----|:------------------|:-------------------|
| 本质 | SuperNIC（AI 网络加速） | **DPU（网络 + 计算 + 存储 + 安全 + 管理）** |
| Arm 核 | ❌ 无 | ✅ Grace 64×Neoverse V2 / Vera 84×2（STX） |
| 数据路径 | 800G 线速（自身） | 800G 线速（自身）+ **ASTRA 治理 4×1.6Tb/s CX9 流量** |
| PCIe | Gen6（SuperNIC） | Gen6 x16（主机）+ Socket Direct |
| 内存 | 无大内存 | 128GB LPDDR5x（DPU）/ 384GB（STX） |
| 定位 | Scale-Out 训练网主力 NIC | Scale-In 基础设施处理器 + Scale-Out 治理锚点 |
| 软件栈 | 网卡驱动 + DOCA 基础 | **DOCA 全栈 + Linux + Scale-In 微服务** |
| 协同 | — | **ASTRA：BF4 装策略，CX9 在数据路径执行** |

> **关键认知**：BF4 的网络引擎与 **ConnectX-9 同源**（BF4 官方描述 "NVIDIA ConnectX-9 networking"），BF4 的增量是 **Grace/Vera CPU + 大内存 + 安全/存储/管理引擎 + ASTRA 治理能力**。在 Vera Rubin 中二者分工明确：**CX9 跑东西向租户流量（Scale-Out），BF4 跑南北向基础设施流量并治理整个托盘（Scale-In + ASTRA）** [来源: NVIDIA BF4 Datasheet + NVIDIA 技术博客 2026-08-24]。

**工程选型分界**：
- 只要**高性能网络**（训练网 Scale-Out）→ CX9 SuperNIC（低功耗、低成本）；
- 需要**基础设施隔离/治理**（云多租户、安全策略、存储服务、遥测）→ BF4；
- 需要**无主机 AI 存储节点 / CMX KV Cache** → BF4 STX [来源: 知识库 JBOF 复兴文档 + NVIDIA BF4 STX Datasheet]。

---

## 7. BF4 STX 存储处理器专章

### 7.1 定位：AI 原生存储的"主机 CPU"

BF4 STX 是 NVIDIA **STX 参考架构**的核心组件，目标场景为 [来源: NVIDIA BF4 STX Datasheet + NVIDIA 新闻稿 2026-05-31]：

1. **CMX 上下文内存存储**（KV Cache 共享存储）；
2. **AI 数据平台**（训练/推理/分析的数据基础设施）；
3. **AI 工厂高性能存储基础设施**。

架构本质：**自宿主（self-hosted）**——STX 既是存储节点的 CPU（跑元数据、存储服务、对象网关）又是数据路径引擎（NVMe-oF target、压缩/加密、数据移动），把传统"x86 存储服务器 + 网卡 + 控制器"三件套合并为一个 SoC [来源: NVIDIA BF4 STX Datasheet + 知识库 JBOF 复兴文档]。

### 7.2 为什么 Vera CPU 比 x86 快 3.21×

NVIDIA 官方基准：Vera CPU 在多级**压缩 + 加密流水线**上吞吐比 x86 高 **3.21×** [来源: NVIDIA BlueField 平台页 + NVIDIA 技术博客]。原因（第一性拆解）：

| 因素 | 机制 |
|:-----|:-----|
| 指令集与微架构 | Neoverse V2 每核 IPC 高于对标 x86 服务器核，且 **SVE2 向量指令**原生加速加解密/校验算法 |
| 内存带宽 | LPDDR5x 高带宽低延迟，压缩/加密流水线是带宽敏感型（每字节数据都要过 CPU 或引擎） |
| 数据路径集成 | 加密/压缩引擎与网络/NVMe 路径**片上集成**，无 PCIe 往返拷贝 |
| 确定性 | 存储路径延迟可预测，无 x86 中断/调度抖动 |

> **工程意义**：对 KV Cache / 数据加载场景，"存储侧 CPU"的算力直接决定数据路径吞吐。Vera 的 3.21× 意味着**同样功耗预算下存储节点吞吐近 3 倍**，这是 STX 替代 x86 存储服务器（JBOF 控制器）的量化依据 [来源: 知识库 JBOF 复兴文档 §4]。

### 7.3 安全：PQC + 硅内文件级访问控制

BF4 STX 是 NVIDIA 首个支持 **PQC（后量子密码）** 的数据中心处理器（Secure Boot 与固件更新均支持 PQC + 经典算法双轨）[来源: NVIDIA BF4 STX Datasheet]。安全栈（DOCA 三件套，2026-05-31 GTC Taipei 宣布）[来源: NVIDIA 新闻稿 2026-05-31]：

| DOCA 组件 | 功能 | 量化指标 |
|:----------|:-----|:---------|
| DOCA Vault | 文件访问策略（仅授权 AI 工作负载可访问对应文件） | 硅内强制，800Gb/s 级 |
| DOCA Argus | agent 行为可见性 / 运行时威胁检测 | **比现有 agentless 方案快 1,000×** |
| DOCA Flow | 多租户网络隔离与敏感数据保护 | 线速策略执行 |

> **判断**：STX 把"存储安全"从传统存储阵列的访问控制列表提升为**硅内实时策略引擎**——因为 agentic AI 的存储访问是"机器速度"（连续读/写/共享，无人监督），必须用硬件策略点而非软件钩子 [来源: NVIDIA 新闻稿 2026-05-31]。

### 7.4 DOCA Memos：KV Cache 分级

DOCA Memos（Memory Objects Storage）把 KV cache 从 GPU HBM 经系统内存到本地/网络存储做**智能分层放置与移动** [来源: NVIDIA BF4 STX Datasheet + STH Hot Chips 2026 报道]：

| 层级 | 介质 | 延迟特征 | 容量 |
|:-----|:-----|:---------|:-----|
| L1 | GPU HBM | 纳秒级 | 小 |
| L2 | 系统内存（LPDDR5x） | 百纳秒级 | 中（384GB） |
| L3 | 本地 NVMe（2TB 板载 + 外部盘） | 微秒级 | 大 |
| L4 | 网络存储（NVMe-oF） | 十微秒级 | 最大 |

> Hot Chips 2026 实测（双 BF4V）：Storage-Scale 提供 **3.2 Tb/s 存储访问、10× IOPS、5× 能效**（相比传统方案）[来源: STH Hot Chips 2026 报道]。这直接对应知识库 CMX 产业锚定分析中"KV Cache 从概念到产业标准"的硬件载体（见知识库 2026-08-06 KV Cache 文档）。

---

## 8. 软件生态：DOCA 与 Scale-In 微服务

### 8.1 DOCA 3.0 定位

DOCA 从 BF3 时代的"DPU 编程框架"升级为**生产级 Scale-In 服务运行平台**——BF4 原生运行容器化 DOCA 微服务（预构建、即插即用）[来源: NVIDIA BF4 Datasheet + NVIDIA 技术博客 2026-08-24]。

### 8.2 Scale-In 微服务矩阵

| 服务 | 功能 | 对应场景 |
|:-----|:-----|:---------|
| **DOCA Host-Based Networking (HBN)** | 南北向 L3 路由 + 多租户隔离加速 | AI 工厂 VPC |
| **DOCA Flow** | 硬件包处理流水线编程（分类/ACL） | 网络策略 |
| **OVS-DOCA** | OVS 硬件卸载（东西向策略） | 云网络 |
| **DOCA PCC** | 可编程拥塞行为 | 拥塞控制 |
| **DOCA Argus** | 运行时威胁检测 | 安全 |
| **DOCA Vault** | 文件访问策略执行 | 存储安全 |
| **DOCA Telemetry** | 设备/服务健康 + 网络遥测导出 | 可观测性 |
| **DOCA Platform Framework (DPF)** | Kubernetes 原生编排（DPU 发现/配置/部署/更新） | 控制平面 |
| **DOCA Memos** | KV cache 智能分层存储 | 推理上下文 |

[来源: NVIDIA 技术博客 2026-08-24 + NVIDIA 新闻稿 2026-05-31]

### 8.3 平台化与锁定风险

| 维度 | 说明 |
|:-----|:-----|
| 可编程层级 | 数据路径加速器（16 核/256 线程）+ 控制面（Grace Linux）+ 硬件引擎（内联） |
| 开发门槛 | 中（DOCA 库 + SDK，云原生微服务模型） |
| 生态成熟度 | NVIDIA 强推 + 安全/存储伙伴生态（Akamai/Check Point/Cisco/CrowdStrike/F5/Fortinet/Palo Alto/Zscaler；Cloudian/DDN/Dell/HPE/IBM/MinIO/NetApp/VAST/WEKA）[来源: NVIDIA 新闻稿 2026-05-31] |
| **锁定风险** | **高**——DOCA 生态绑定 + ASTRA 需要 BF4/CX9 同栈（与 CUDA 同理，且叠加存储安全域） |

> **判断**：BF4 的锁定比 BF3 更进一步——ASTRA 把"安全治理"也绑入 NVIDIA 栈（BF4 装策略 + CX9 执行），存储侧 STX + CMX + Memos 构成闭环。**选 BF4 即选择 NVIDIA 平台化基础设施栈**，独立使用价值有限 [来源: 知识库 DPU 三方对比 §4.4 + NVIDIA 技术博客]。

---

## 9. Scale-In 网络架构：第五支柱

### 9.1 为什么需要 Scale-In（第一性原理）

AI 工厂与云数据中心的本质差异：**多租户 + 持续交互 + 机器速度**。

| 传统云 | Agentic AI 工厂 |
|:-------|:----------------|
| 可预测、通用负载 | 多租户共享超大规模算力，流量不可预测 |
| 标准接口 | 每服务器多 Tb/s 聚合带宽 |
| 软件定义基础设施够用 | 安全/存储/运维不能靠主机 CPU 软件栈（性能与隔离双不达标） |
| 南北向只是"接入" | 南北向承载数据访问 + 安全 + 上下文存储 = **基础设施主战场** |

结论：Scale-In 把"南北向网络"从传统接入层升级为**统一加速基础设施域**——BF4 主机无关处理，DOCA 统一编程，Spectrum-X 提供高性能以太网载体 [来源: NVIDIA 技术博客 2026-08-24]。

### 9.2 Vera Rubin 中的带宽账本

| 流量方向 | 承载 | 带宽 |
|:---------|:-----|:-----:|
| Scale-In（南北向） | BF4 | **800 Gb/s** |
| Scale-Out（东西向） | ConnectX-9 SuperNIC ×4 | **4 × 1.6 Tb/s** |
| **托盘聚合** | — | **7.2 Tb/s** |

[来源: STH Hot Chips 2026 报道 + NVIDIA 技术博客 2026-08-24]

> NVIDIA 官方论证：无 DPU 的传统方案（每 NIC 独立 CPU/内存/管理）功耗 **4×** 更高，且 Scale-Out 流量无法端到端安全隔离 [来源: STH Hot Chips 2026 报道]。

### 9.3 Scale-In 性能数据（官方口径）

| 指标 | 数值 | 基线 |
|:-----|:-----|:-----|
| 存储访问加速 | **1.45×** 吞吐 | vs 普通以太网（5GB 文件 1.5× / 10GB 1.4× / 50GB 1.3×，Hot Chips 口径） |
| NVMe-oF（BF4G） | **1.6 Tb/s**（8 核）/ **20M IOPS**（16 核） | Rubin GPU 数据路径 2× 加速 |
| Storage-Scale（双 BF4V） | **3.2 Tb/s** / **10× IOPS** / **5× 能效** | DOCA Memos 分层 |
| 威胁检测 | **1,000×** 快 | vs 现有 agentless 运行时方案 |
| 小包线速 | 保持线速转发 + 安全检查 | 小包（控制平面流量）不塌陷 |

[来源: STH Hot Chips 2026 报道 + NVIDIA 技术博客 2026-08-24 + NVIDIA 新闻稿 2026-05-31]

> ⚠️ **测试条件声明**：以上为 NVIDIA 官方口径（Hot Chips 演讲 + 官方博客），**无第三方独立复现**。采购验证需自建基准（见 §13.3 风险提示）。

---

## 10. 电气/热/环境规格

| 维度 | 已知事实 | 状态 |
|:-----|:---------|:-----|
| 供电 | 官方 Datasheet 未公开；BF4G 为 PCIe 插卡（Gen6 x16 槽供电 + 可能的辅助供电）；BF4 STX 为模块化自宿主设计 | ⚠️ 缺口 |
| 功耗 | **官方未公开数字**；知识库 JBOF 文档按早期信息估算 **100-150W/颗**（含 CPU 贡献，需以官方规格书为准）[来源: 知识库 JBOF 技术深潜 §7] | ⚠️ 估算（早期口径，待官方核实） |
| 散热 | 1260 亿晶体管 + 64/84 核 CPU + 800G SerDes → 主动散热（插卡）/平台一体化散热（Rubin 机架液冷） | ⚠️ 推断 |
| 环境 | 数据中心服务器场景（Datasheet 未给温度范围，参考同代 ConnectX-9/CX8：0-55°C 级） | ⚠️ 部分推断 |
| 认证 | CE/FCC/RoHS 级（NVIDIA 数据中心产品标准） | ⚠️ 未逐项核实 |

> **工程提示**：BF4G 的功耗大概率高于 BF3（6× 算力 + 4× 内存带宽 + 800G），**机箱选型与供电预算必须拿到官方 TDP 后单独核算**；BF4 STX 用于 JBOF/存储节点时，功耗与散热设计参考知识库 AIC F2032 JBOF 文档（双 BF4 + 32 盘 2U 的散热难题）[来源: 知识库 JBOF 技术深潜 §7]。

---

## 11. 应用场景与部署

### 11.1 场景矩阵

| 场景 | BF4 角色 | 关键能力 | 状态（2026） |
|:-----|:---------|:---------|:------------|
| **Vera Rubin NVL72** | Scale-In 基础设施处理器（平台 co-design） | 800G Scale-In + ASTRA 治理 7.2Tb/s | 平台标配 [来源: STH Hot Chips 2026] |
| **AI 工厂多租户云（DSX）** | 虚拟化前端 + VPC 隔离 | DOCA HBN + OVS-DOCA + Flow | 云服务商 [来源: NVIDIA 博客] |
| **AI 存储 / CMX KV Cache** | **BF4 STX 存储处理器（存储节点主机）** | Vera CPU + Memos 分层 + GDS | 2026H2 生态可用 [来源: NVIDIA 新闻稿] |
| **JBOF / AI 数据平台** | 自宿主存储控制器 | NVMe-oF target + 压缩/加密 + 3.21× 吞吐 | AIC F2032 等配套 [来源: 知识库 JBOF 文档] |
| **安全网关/零信任** | 可信实体（主机前） | 硅内策略 + SPDM 认证 + Argus/Vault | 企业/边缘 [来源: NVIDIA Datasheet] |
| **Scale-Out 训练网** | ❌ 非主力（CX9 SuperNIC 才是） | ASTRA 治理延伸（装策略） | 与 CX9 协同 [来源: NVIDIA 博客] |

### 11.2 对我方超节点/存储项目的意义（知识库口径对照）

| 我方场景 | BF4 适用性 | 依据 |
|:---------|:-----------|:-----|
| 训练网 Scale-Out（RoCEv2） | ⚠️ 继续用 CX7/CX8 级 NIC；BF4 仅需在"基础设施隔离/治理"时引入 | 网络引擎同源，纯网络场景 NIC 功耗/成本更优（BF3 文档 §9.2 结论延续） |
| 存储网络（KV Cache/数据加载） | ✅ **BF4 STX 是 CMX 路线的硬件载体**（Memos + GDS + NVMe-oF + 3.21×） | 知识库 CMX/KV Cache 系列结论 + JBOF 复兴文档 |
| 无主机存储节点 / JBOF 控制器 | ✅ BF4 STX 自宿主（Vera 替代 x86 存储服务器） | 知识库 AIC F2032 JBOF 文档（BF4 成本 $2000-5000/颗，BOM 占比需核算） |
| 多租户云服务 | ✅ DOCA HBN + ASTRA（南北向 + 东西向统一策略） | NVIDIA Datasheet + 博客 |
| 管理/调度服务器 | ✅ BF4 800G（一分多端口）做管理网 | NVIDIA Datasheet（8 split 端口） |

---

## 12. 竞品对比

### 12.1 800G 时代 DPU/网络处理器对比（2026-08-28 核实）

| 维度 | NVIDIA BF4 | NVIDIA BF3 | Xsight Labs E1 | Broadcom Thor Ultra |
|:-----|:-----------|:-----------|:----------------|:---------------------|
| 发布时间 | 2025 宣布 / 2026 量产 | 2022 / 2023 量产 | 已可购买（2025-2026） | Hot Chips 2026 展示 |
| CPU 核 | **64×Neoverse V2**（STX: 2×84 核 Vera） | 16×A78 | 64×Arm N2 | 无（纯 NIC） |
| 内存 | **128GB LPDDR5x**（STX: 384GB） | 16GB DDR5 | 未披露 | 无 |
| 网络 | **800G**（STX: 3.2Tb/s） | 400G | 2×400G | 800G（Thor2 级） |
| 主机接口 | PCIe Gen6 x16（STX: x96） | Gen5 x32 | 2×16 PCIe Gen5 | PCIe Gen6 |
| 数据平面 | 硬件引擎 + 256 线程可编程 + 内联加密 | 硬件引擎 + 256 线程 | Arm 软件 + 硬件加速 | 硬件引擎（以太 NIC） |
| RDMA | RoCEv2 + 可编程传输 | RoCE 硬件卸载 | — | Ultra Ethernet（UAL 类） |
| AI 原生 | ✅ Scale-In/ASTRA/存储 Scale | ✅ AI 引擎 | ❌ | ⚠️ UEC 生态 |
| 安全 | 硅内策略 + SPDM + PQC（STX） | 全家桶 | 未披露 | 基本 |
| 定位 | **AI 工厂基础设施处理器** | 400G 基础设施平台 | 64 核 Arm DPU（性价比） | 以太训练 NIC |

[来源: STH Hot Chips 2026 + STH GTC DC 2025 + STH 评论（Xsight E1 对比）+ 知识库 DPU 三方对比]

> **竞品结论**：
> - **BF4 vs BF3**：BF4 不是 BF3 的简单升级，而是**从"基础设施插卡"到"AI 工厂平台组件"的范式跃迁**（ASTRA + Scale-In + STX）；
> - **BF4 vs Xsight E1**：E1 是"64 核 Arm DPU"先行者（N2 核、2×400G、现售），STH 预计 BF4 因 V2 核代际优势显著更快；E1 是**非 NVIDIA 生态的 800G 级 DPU 替代选项**（值得监控）；
> - **BF4 vs Broadcom Thor Ultra**：Thor Ultra 是纯以太 NIC（UEC 生态），与 BF4 不同类别——前者争 Scale-Out 训练网，后者主 Scale-In 基础设施域；
> - **国产竞品**：知识库国产 DPU 分析（2026-08-11）显示国产 400G DPU 尚未触及 800G + 64 核 + Scale-In 级别，BF4 在 AI 工厂级基础设施域暂无对等竞品 [来源: 知识库国产 DPU 竞品分析]。

---

## 13. BOM 选型建议

### 13.1 场景决策树

- **Vera Rubin 平台（NVIDIA 生态）** → BF4 为平台组件（随平台交付，无需单独选型）；
- **AI 训练网 Scale-Out（NVIDIA 生态）** → ConnectX-9 SuperNIC（纯网络，低功耗）；BF4 仅在需要**南北向基础设施治理/安全**时引入；
- **AI 原生存储（KV Cache/CMX 路线）** → **BF4 STX**（Vera + Memos + GDS + NVMe-oF）；
- **无主机存储节点 / JBOF 控制器** → BF4 STX 自宿主（对比 x86 存储服务器全生命周期成本）；
- **非 NVIDIA 生态** → 对比 Xsight E1（64 核 Arm 800G 级）等替代；
- **存量 400G 基础设施** → BF3 仍是 400G DPU 主力（BF4 换代期，成本敏感场景用 BF3）。

### 13.2 采购规格清单（RFP 要点）

| 项目 | 要求 | 验证方法 |
|:-----|:-----|:---------|
| 产品线区分 | 明确 **BF4G（Grace DPU）vs BF4V（Vera STX）**，二者规格差异巨大 | NVIDIA/代理官方 SKU 表 |
| OPN 冻结 | 官方 OPN 矩阵（Datasheet 未公开） | 向 NVIDIA 索取 |
| 形态确认 | PCIe 插卡（Gen6 x16 槽）vs 定制形态（Rubin）vs STX 模块 | 目标平台核对 |
| 功耗预算 | **官方 TDP 未公开 → 必须索取**（早期估算 100-150W/颗仅参考） | 机箱供电/散热核算 |
| 内存配置 | 128GB（DPU）vs 384GB（双 STX）SKU 差异 | 规格书核对 |
| DOCA 版本 | DOCA 3.0 级基线 + 目标微服务（HBN/Flow/Argus/Vault/Memos） | NVIDIA DOCA 发布说明 |
| ASTRA 依赖 | 若需 ASTRA 治理，确认配套 ConnectX-9 SuperNIC 与 Rubin 平台 | 平台兼容矩阵 |
| 软件锁定 | 明确接受 DOCA + ASTRA 生态绑定 / 或有开源替代路径 | 生态评估（§8.3） |
| 供货节奏 | 2026H2 生态放量；早期 SKU 供货受限 | NVIDIA 渠道确认 |

### 13.3 关键风险提示

1. **平台绑定**：BF4 价值在 NVIDIA 生态内最大化（Vera Rubin + CX9 + Spectrum-X + DOCA），脱离平台单买价值有限（ASTRA 需要 CX9 配套）；
2. **生态锁定加深**：ASTRA 把安全治理也绑入 NVIDIA 栈；STX/Memos/CMX 形成存储闭环——重大选型前做 PoC；
3. **数据缺口**：官方未公开 TDP/OPN/温度；性能数据（1.45×/3.2Tb/s/20M IOPS）均为 NVIDIA 口径，**无第三方复现**——必须实测（时延/吞吐/CPU 释放/功耗/隔离 5 项）；
4. **换代节奏**：BF4 处于上市初期（2026H2 生态放量），固件/DOCA 栈成熟度待验证；BF3 仍是存量主力；
5. **成本**：BF4 STX 单颗估算 $2000-5000（知识库 JBOF 文档口径），双 STX + 冗余后 DPU 成本占存储节点 BOM 30-50%——需与 x86 存储控制器方案做全生命周期对比 [来源: 知识库 JBOF 技术深潜 §4.3]。

---

## 14. 参考文献

[1] NVIDIA, *NVIDIA BlueField-4 DPU Datasheet*（官方 PDF，2026-06 JUN26 版，2026-08-28 抓取）— 800G/64 核 Grace/128GB LPDDR5x/PCIe Gen6 x16/ASTRA/全部加速引擎清单 [来源: [1]]

[2] NVIDIA, *NVIDIA BlueField-4 STX Storage Processor Datasheet*（官方 PDF，2026-06 JUN26 版，2026-08-28 抓取）— 双 STX 3.2Tb/s/双 Vera 84 核/384GB LPDDR5x/2TB SSD/PQC/SPDM [来源: [2]]

[3] NVIDIA Technical Blog, *NVIDIA BlueField-4 Powers New Scale-In Network Infrastructure for Agentic AI Factories*, 2026-08-24 — 第五支柱定义/组件表/6×4×2× 增益/1.45× 存储/ASTRA 闭环/DOCA 微服务矩阵 [来源: [3]]

[4] NVIDIA Newsroom, *NVIDIA Vera BlueField-4 STX Brings Agentic AI Storage Processing With In-Silicon Security*, 2026-05-31（GTC Taipei）— DOCA Vault/Argus/Flow/1000× 威胁检测/生态伙伴列表/2026H2 可用 [来源: [4]]

[5] ServeTheHome, *NVIDIA BlueField-4 with 64 Arm Cores and 800G Networking Announced for 2026*, 2025-10-28（GTC DC）— 1260 亿晶体管/ConnectX-9/64 核 Grace/KV cache 动机/2026 早期可用 [来源: [5]]

[6] ServeTheHome, *NVIDIA BlueField-4 DPU at Hot Chips 2026*, 2026-08-25 — 64 核 V2 @1.7GHz/LPDDR5x 275GB/s/7.2Tb/s 托盘/ASTRA 7Tb/s/NVMe-oF 1.6Tb/s·20M IOPS/Storage-Scale 3.2Tb/s·10×·5×/BF4G vs BF4V 命名 [来源: [6]]

[7] NVIDIA, *BlueField Networking Platform*（官方平台页，2026-08-28 抓取）— Scale-In 定位/Vera 3.21× 压缩加密/STX= Vera CPU + ConnectX-9 [来源: [7]]

[8] 知识库, *2026-08-28-bluefield3-bf3-spec-deep-analysis*（同目录）— BF3 全规格基线/BF4 对比参照（§11 已修正）[来源: [8]]

[9] 知识库, *2026-07-23-aic-f2032-g6-jbof-technology-deep-dive*（02_rd/01_product/00_hardware/06_storage/）— BF4 在 JBOF/CMX 的 I/O 栈优势/功耗估算 100-150W/成本 $2000-5000/散热难题 [来源: [9]]

[10] 知识库, *2026-08-06-kv-cache-concept-to-industry-standard-cmx-anchoring*（03_AI/train/ai-storage/）— KV Cache 产业锚定 CMX（BF4 STX 为硬件载体）[来源: [10]]

[11] 知识库, *2026-08-11-dpu-three-way-e2100-bf3-salina400*（02_rd/01_product/01_software/04-comm-lib/）— DPU 数据平面三范式/平台化趋势 [来源: [11]]

[12] 知识库, *2026-08-11-domestic-dpu-competitive-analysis*（02_rd/03_management/08_competitive-analysis/）— 国产 DPU 竞品现状（未达 800G+64 核+Scale-In 级别）[来源: [12]]

---

## 15. 变更记录

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-28 | v1.0 | 首次创建：基于 NVIDIA 官方两份 Datasheet（2026-06 JUN26 一手 PDF）+ 官方技术博客（Scale-In 定义）+ 官方新闻稿（STX 安全）+ STH 两篇一手报道（GTC DC 2025 发布/Hot Chips 2026 深度规格）+ 知识库 BF3/JBOF/CMX/DPU 对比文档，输出 BF4 全家族规格解读（BF4G 800G/64 核 Grace/128GB LPDDR5x 与 BF4V STX 3.2Tb/s/双 Vera/384GB）+ 工作原理（Scale-In 第五支柱/ASTRA 闭环/双 OS 三域隔离/内存指纹/STX 自宿主）+ 竞品对比（Xsight E1/Thor Ultra）+ BOM 选型建议；同步修正 BF3 文档 §11 的 BF4 预告数据（32GB DDR5 → 128GB LPDDR5x 等）；功耗/OPN/温度标注为数据缺口 |
