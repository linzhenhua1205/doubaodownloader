# NVIDIA ConnectX-7 (CX7) 规格解读报告 — 核心规格参数与工作原理

> **元信息**: 文件状态=正式版 v1.0 | 覆盖范围=ConnectX-7 全家族（PCIe stand-up / OCP 3.0 / Socket Direct / 电信版）规格与原理 | 版本=1.0
> **适用范围**: 服务器平台规划 / Scale-Out 网络 BOM / 网卡选型与验证 / 超节点部署

## 目录

- [1. 引言与范围](#1-引言与范围)
- [2. 产品定位与代际演进](#2-产品定位与代际演进)
- [3. 芯片架构与工作原理](#3-芯片架构与工作原理)
- [4. 核心规格参数总表](#4-核心规格参数总表)
- [5. 接口与形态详解](#5-接口与形态详解)
- [6. 协议与速率详解](#6-协议与速率详解)
- [7. 网络加速与软件生态](#7-网络加速与软件生态)
- [8. 电气/热/环境规格](#8-电气热环境规格)
- [9. 应用案例：超节点 Scale-Out 4×CX7](#9-应用案例超节点-scale-out-4cx7)
- [10. 代际与竞品对比](#10-代际与竞品对比)
- [11. BOM 选型建议](#11-bom-选型建议)
- [12. 参考文献](#12-参考文献)
- [13. 变更记录](#13-变更记录)

---

## 1. 引言与范围

### 1.1 文档目的

本文档对 NVIDIA ConnectX-7（下称 CX7）SmartNIC 进行**规格级深度解读**，回答三个问题：

1. **是什么**：CX7 的完整规格参数（型号矩阵、接口、速率、功耗、环境）；
2. **怎么工作**：芯片级数据通路与各卸载引擎的原理（RDMA/RoCE、GPUDirect、SR-IOV、集群体操作、时序）；
3. **怎么用**：在超节点 Scale-Out 网络中的实际部署口径与 BOM 选型要点。

### 1.2 目标读者

服务器/数据中心硬件工程师、网络架构师、BOM 与采购负责人。

### 1.3 覆盖范围

- CX7 全家族 OPN：PCIe stand-up（HHHL）、OCP Spec 3.0（TSFF/SSFF）、Socket Direct Ready、电信增强版
- 不覆盖：BlueField-3（CX7 的 DPU 变体，Arm SoC 版）的软件栈细节

### 1.4 术语表

| 术语 | 含义 |
|:-----|:-----|
| NDR | NVIDIA 400Gb/s InfiniBand（Next Data Rate），4 lane × 100Gb/s PAM4 |
| NDR200 | NDR 的 2-lane 形态，200Gb/s |
| RoCE | RDMA over Converged Ethernet |
| GPUDirect RDMA | GPU 显存↔网卡直接 DMA，绕过 CPU/主机内存 |
| VPI | Virtual Protocol Interconnect，一卡双协议（IB + 以太） |
| OPN | Ordering Part Number，订货型号 |
| HHHL / FHHL | Half-Height Half-Length / Full-Height Half-Length |
| TSFF / SSFF | OCP 3.0 Tall / Small Small Form Factor |
| RHS | Riding Heat Sink（OSFP 笼的散热方式） |

---

## 2. 产品定位与代际演进

### 2.1 ConnectX 家族代际

| 代际 | 发布年 | IB 速率 | 以太速率 | PCIe | 端口形态典型 |
|:-----|:------:|:-------:|:--------:|:----:|:-------------|
| ConnectX-5 | 2016 | EDR 100Gb/s | 100GbE | Gen3 x16 | 2×QSFP28 |
| ConnectX-6 | 2019 | HDR 200Gb/s | 200GbE | Gen4 x16 | 2×QSFP56 |
| **ConnectX-7** | **2022** | **NDR 400Gb/s** | **400GbE** | **Gen5 x16** | **1×OSFP / 2×QSFP112 / 4×SFP56** |
| ConnectX-8 | 2025 | NDR 400Gb/s×2 | 800GbE | Gen6 x16 | 2×OSFP |

CX7 是 Mellanox 被 NVIDIA 收购（2020.04）后**首个完全以 NVIDIA 品牌发布的 ConnectX 代际**，与 BlueField-3（DPU 版）、Quantum-2（NDR 交换机）、Spectrum-4（400GbE 交换机）同代发布（GTC Fall 2021 首秀，2022 量产）[来源: STH ISC 2022 报道]。

### 2.2 在 NVIDIA 网络矩阵中的位置

```
        Scale-Out 网络（AI 集群）
   ┌────────────────────────────────────┐
   │  InfiniBand 路线                    │
   │   Quantum-2 交换机 <──NDR──> CX7   │  ← 本文档主角（VPI）
   │                                    │
   │  Ethernet 路线                     │
   │   Spectrum-4 交换机 <──400GbE──> CX7│
   │                                    │
   │  DPU 变体：BlueField-3（含 Arm）    │
   └────────────────────────────────────┘
```

CX7 的差异化定位：**400Gb/s 时代的旗舰 SmartNIC**，同时覆盖 IB（NDR）与以太（400GbE）两条路线，硬件卸载引擎齐全，是 2022-2024 年 AI 集群 Scale-Out 的事实标准网卡（H100 时代 DGX H100 标配 8×CX7）[来源: 知识库 08-20 superpod 实施设计]。

---

## 3. 芯片架构与工作原理

### 3.1 芯片本体：MT2910

CX7 的 ASIC 为 Mellanox 世代命名 **MT2910**，Linux lspci 识别为 "Mellanox Technologies MT2910 Family [ConnectX-7]" [来源: NVIDIA CX7 User Manual §3.8]。

核心能力分层（第一性原理拆解）：

| 层 | 职责 | CX7 实现 |
|:---|:-----|:---------|
| 物理层 | 信号编解码 | 支持 PCIe Gen5 32GT/s、IB NDR 100G/lane PAM4、400GAUI-4 C2M |
| 数据通路 | 报文收发 | 片上多队列引擎 + DMA 引擎，直连主机内存/GPU 显存 |
| 传输层 | 可靠传输 | IB Transport / RoCEv2（DCQCN 拥塞控制）硬件卸载 |
| 服务层 | 协议终结 | VXLAN/NVGRE 隧道终结、NVMe-oF、MPI 集群体操作 |
| 安全层 | 加密/信任 | Secure Boot、IPsec/MACsec 硬件加密（Crypto SKU）、FW 签名校验 |

### 3.2 数据通路原理（报文从网线到 GPU 显存）

```
 Host/GPU Memory (RDMA 目标)
      ▲
      │ PCIe Gen5 x16 (32GT/s, ~64GB/s 单向)
 ┌────┴─────┐
 │  DMA Eng │   ← 免 CPU 拷贝（PeerDirect 消除中间跳）
 └────┬─────┘
 ┌────┴─────┐
 │ Queue    │   ← 发送/接收队列（WQE/CQE），宿主侧驱动投递
 └────┬─────┘
 ┌────┴─────┐
 │ Offload  │   ← 隧道终结/RDMA 传输/集群体操作/加密
 └────┬─────┘
 ┌────┴─────┐
 │ MAC/PHY  │   ← PAM4 编解码 + RS-FEC
 └────┬─────┘
      ▼
   OSFP/QSFP112 端口
```

关键机制说明：

- **RDMA 直通**：接收端数据由网卡 DMA 直接写入应用缓冲区/GPU 显存，主机 CPU 仅在完成队列（CQ）收到完成通知，**零拷贝、零内核介入**——这是 330-370 Mpps 消息率（RDMA Message Rate）的来源[来源: NVIDIA CX7 User Manual §1.4]；
- **PeerDirect（GPUDirect RDMA）**：GPU↔网卡之间的 PCIe peer-to-peer DMA，消除"GPU→CPU→网卡"的中间拷贝，训练 AllReduce 时梯度同步不再经过主机内存[来源: NVIDIA CX7 User Manual §1.4]。

### 3.3 卸载引擎原理

**（1）集群体操作卸载（In-Network Computing）**

CX7 将 MPI_Allreduce / Alltoall / Barrier 等**集群体操作从 CPU 卸载到网卡**，网卡在数据到达时直接做规约（reduce）再转发，配合 Quantum-2 交换机的 SHARP 引擎实现"计算进网络"，显著缩短多节点梯度同步时间。CX7 支持：

- Collective operations offloads
- Vector collective operations offloads
- MPI_Alltoall offloads
- Rendezvous protocol offload

[来源: NVIDIA CX7 User Manual §1.4]

**（2）拥塞控制（RoCEv2 场景）**

CX7 实现 DCQCN（数据中心量化拥塞通知）硬件机制，结合 PFC（802.1Qbb）/ETS（802.1Qaz）/QCN（802.1Qau）实现无损以太网，保证 RoCEv2 在大规模集群中的低尾延迟——这是超节点 RoCE 方案可用性的物理前提[来源: NVIDIA CX7 User Manual §1.4 + §1.4 QoS]。

**（3）Overlay 卸载**

VXLAN / NVGRE 隧道的封装/解封装由硬件完成，避免 overlay 隐藏 TCP 包导致 host CPU 负载上升[来源: NVIDIA CX7 User Manual §1.4]。

**（4）安全与信任根**

- **Secure Boot**：芯片内置 Root-of-Trust，密钥存于 on-chip FUSES，启动时用非对称密码学校验固件签名；
- **Secure Firmware Update**：固件二进制必须带有效数字签名才可安装（host/网络/BMC 三通道均受限）；
- **Crypto（仅 AC 后缀 SKU）**：硬件加密引擎，支持 IPsec/MACsec（802.1AE）线速加密。

[来源: NVIDIA CX7 User Manual §1.4]

**（5）精确时序（5T / PTP）**

集成 PHC（硬件时钟），PTP（1588v2）精度 **sub-20μs**，支持 master/slave/boundary clock、PPS-in/out（电信 SKU 带 SMA 连接器）、time-triggered scheduling、time-based ASAP²。面向 5G 前传（ORAN）与跨数据中心同步[来源: NVIDIA CX7 User Manual §2.2.6]。

### 3.4 虚拟化与多主机

- **SR-IOV**：每 VM 独占适配器资源与隔离保护；
- **Multi-Host**：单卡最多服务 **4 个 host**（PCIe 拆分/共享）——4U 多节点服务器一卡四用的关键；
- **PCIe 特性**：ATS、PASID、ACS、AER、DPC、TPH、MSI/MSI-X 全支持[来源: NVIDIA CX7 User Manual §2.2.2]。

---

## 4. 核心规格参数总表

### 4.1 PCIe stand-up 家族（官方 OPN 全表）

| NVIDIA SKU | Legacy OPN | 形态 | 速率 | 端口 | PCIe | 功耗¹ |
|:-----------|:-----------|:-----|:-----|:-----|:-----|:-----:|
| 900-9X766-003N-SQ0 | MCX75310AAS-NEAT | HHHL | IB: NDR 400Gb/s（默认）/ 以太: 400GbE | 1×OSFP | Gen4/5 x16 | 24.9W |
| 900-9X766-003N-SR0 | MCX75310AAC-NEAT | HHHL | IB: NDR 400Gb/s（默认）/ 以太: 400GbE | 1×OSFP | Gen4/5 x16 | 25.9W |
| 900-9X766-003N-ST0 | MCX75310AAS-HEAT | HHHL | IB: NDR200 200Gb/s（默认）/ 以太: 200GbE | 1×OSFP | Gen4/5 x16 | 16.7W |
| 900-9X7AO-00C3-STZ | MCX713104AC-ADAT | HHHL | 以太: 50/25GbE | 4×SFP56 | Gen4 x16 | — |
| 900-9X7AO-0003-ST0 | MCX713104AS-ADAT | HHHL | 以太: 50/25GbE | 4×SFP56 | Gen4 x16 | — |

¹ Typical power with passive cables in PCIe Gen 5.0 x16 [来源: NVIDIA CX7 User Manual §9]

### 4.2 OCP Spec 3.0 家族

| NVIDIA SKU | Legacy OPN | 形态 | 速率 | 端口 | 功耗¹ | 备注 |
|:-----------|:-----------|:-----|:-----|:-----|:-----:|:-----|
| 900-9X7A0-... | MCX753436MS-HEBB | OCP3.0 SFF | IB: NDR200 / 以太: 200GbE | 2×QSFP112 | 24.5W | Port Split 可配，Multi-Host |
| 900-9X7A0-... | MCX75343AMS-NEAC | OCP3.0 TSFF | IB: NDR 400Gb/s / 以太: 400GbE | 1×OSFP | 24.4W | Multi-Host + Socket Direct |
| 900-9X7A0-... | MCX75343AMC-NEAC | OCP3.0 TSFF | IB: NDR 400Gb/s / 以太: 400GbE | 1×OSFP | 25.9W | Crypto 版 |

¹ Typical power with passive cables in PCIe Gen 5.0 x16 [来源: NVIDIA CX7 OCP3.0 User Manual §14]

### 4.3 Socket Direct Ready / 电信版

| OPN | 形态 | 速率 | 端口 | 关键特性 |
|:----|:-----|:-----|:-----|:---------|
| MCX715105AS-WEAT | HHHL + Aux 卡 | 400GbE / NDR（默认以太） | 1×QSFP112 | Socket Direct：32-lane 拆 2×x16，双路服务器每 CPU 直连 |
| MCX755106AS-HEAT / AC-HEAT | HHHL + Aux 卡 | 200GbE / NDR200（默认以太） | 2×QSFP112 | Socket Direct，AC= Crypto |
| MCX713114TC-GEAT | FHHL | 50/25GbE | 4×SFP56 | 电信版：PPS In/Out + SMA + SyncE |

Socket Direct 原理：32-lane PCIe 总线拆成两条 x16——一条走卡上 x16 金手指，另一条经 **PCIe Auxiliary 无源扩展卡 + 两条 Cabline SA-II Plus 线缆**连到第二个 PCIe x16 槽，实现双路服务器**每 CPU 各直连 x16**，避免跨 socket 访问的带宽损耗（400GbE 下跨 socket 损耗显著）[来源: NVIDIA CX7 User Manual §1.1.3 + STH PNY Review]。

### 4.4 关键规格速览（全家族共性）

| 维度 | 规格 | 出处 |
|:-----|:-----|:-----|
| 芯片 | MT2910（lspci: Mellanox MT2910 Family） | [来源: User Manual §3.8] |
| PCIe | Gen 5.0 x16 @ 32GT/s（Gen 4.0/3.0 兼容），Socket Direct 下 2×x16 | [来源: User Manual §2.2.2] |
| IB 速率 | NDR 400 / NDR200 200 / HDR 200 / HDR100 100 / EDR 100 / FDR 56.25 / SDR（Gb/s） | [来源: User Manual §1.4] |
| 以太速率 | 400 / 200 / 100 / 50 / 40 / 25 / 10 / 2.5 / 1 GbE | [来源: User Manual §1.4] |
| RDMA 消息率 | 330-370 Mpps | [来源: User Manual §1.4] |
| 端口供电 | OSFP / QSFP112 最大 17W/端口；SFP56 最大 1.5W/端口（均不做热冗余） | [来源: OCP3.0 Manual §14] |
| 管理 | MCTP over SMBus/PCIe，PLDM（DSP0248/026），NCSI | [来源: User Manual §1.4] |
| 存储 | SPI 256Mbit 四口 Flash；FRU EEPROM 128Kbit（I2C 0x50） | [来源: User Manual §1.4] |

---

## 5. 接口与形态详解

### 5.1 网络连接器家族

| 连接器 | 最大速率/端口 | 端口数形态 | 电气通道 | 适用 OPN |
|:-------|:-------------|:-----------|:---------|:---------|
| **OSFP** | 400G（4×100G PAM4） | 单端口 | 400GAUI-4 C2M | MCX75310*（400G SKU）、MCX75343*M-NEAC |
| **QSFP112** | 200G（2×100G PAM4）¹ | 双端口 | 200GAUI-2/4 C2M | MCX753436*、MCX755106*、MCX715105AS |
| **SFP56** | 50G（1×50G PAM4） | 四端口 | 50GAUI-1/2 | MCX713104*、MCX713114TC |

¹ QSFP112 物理上可承载 400G（4×100G），CX7 双口 QSFP112 固件限制 200G/口（合计 400G 恰好匹配 PCIe Gen5 x16 总带宽）；400G/口需 BlueField-3 或固件升级 + 双 PCIe 槽[来源: STH OCP Review 评论区]。

**OSFP vs QSFP-DD 关键差异**（工程采购必须注意）：

- OSFP 允许 15W 光模块（QSFP-DD 为 12W），散热裕量更大——早期 400G 光模块功耗高，NVIDIA 选择 OSFP 是功耗驱动的理性选择[来源: STH PNY Review]；
- CX7 OSFP 版**只支持 RHS（Riding Heat Sink）笼**，且需要 **Flat-top（平顶）OSFP 连接器**——Fin-top（鳍片顶）DAC/光模块无法插入，这是 STH 实测踩坑点[来源: STH PNY Review + 评论]。

### 5.2 Port Splitting（端口拆分）

单物理模块可拆为多逻辑端口，例如：

- 单口 400G OSFP → 可拆出 2×200G（NDR200/200GbE）等配置；
- 双口 QSFP112（200G×2）→ 支持 100G/50G/25G 多速率拆分。

用途：同一块卡适配不同拓扑（如 1:1 无收敛 vs 收敛比部署），降低备件种类[来源: NVIDIA CX7 User Manual §1.1.1 + OCP3.0 Manual §12]。

### 5.3 PCIe 接口能力

- 链路速率：2.5/5/8/16/32 GT/s，x16（Socket Direct 为 2×x16）；
- 自动协商 x32/x16/x8/x4/x2/x1（bifurcation）；
- 400GbE 单端口 ≈ PCIe Gen5 x16 理论带宽（约 64GB/s 单向）的极限占用——**工程上要求 Gen5 x16 槽位才能跑满单口 400G**；
- 双口 200G 合计 400G，同样需要 Gen5 x16（Gen4 x16 会形成瓶颈，STH 实测 200G 双口在 Gen4 x16 下无法同时跑满）[来源: NVIDIA CX7 User Manual §2.2.2 + STH OCP Review]。

### 5.4 LED 与可维护性

- 每端口 2 个 I/O LED（双色+单色）：Beacon（1Hz 黄闪）/ Error（4Hz 黄闪）/ Activity / Link Up；
- OCP 3.0 版默认 Thumbscrew（Pull Tab）拉手，云厂商偏好（免开箱从冷通道更换）[来源: NVIDIA CX7 User Manual §2.2.4 + STH OCP Review]。

---

## 6. 协议与速率详解

### 6.1 InfiniBand 速率家族（IBTA v1.5 合规）

| 协议 | 标准速率 (4x) | 2-lane 形态 | 调制 | 编码/FEC |
|:-----|:-------------:|:-----------:|:-----|:---------|
| NDR / NDR200 | 425 Gb/s | 212.5 Gb/s | PAM4 | 256b/257b + RS-FEC |
| HDR / HDR100 | 212.5 Gb/s | 106.25 Gb/s | PAM4 | 256b/257b + RS-FEC |
| EDR | 103.125 Gb/s | 51.56 Gb/s | NRZ | 64b/66b |
| FDR | 56.25 Gb/s | — | NRZ | 64b/66b |

NDR 每 lane 100G PAM4 + RS-FEC，与以太 400GAUI-4 共用电气层技术[来源: NVIDIA CX7 User Manual §1.4]。

> ⚠️ NVIDIA 在 IBTA 自动协商规范上做了**私有补充**（更低误码率、更长线缆距离），仅在对接另一台 NVIDIA IB 设备时生效——混合 IB 生态（非 NVIDIA 交换机）可能无法获得该增强[来源: NVIDIA CX7 User Manual §9 Notes a]。

### 6.2 Ethernet 协议支持

IEEE 802.3 全谱系：802.3ck（100/200/400G，含 ETC 增强）、802.3cd/bs/cm/cn/cu（50-400G）、802.3by（25/50G）、802.3ba（40G）、802.3ae（10G）、802.3cb（2.5/5G）等；支持 **Jumbo Frame 9.6KB**、VLAN（802.1Q/P）、链路聚合（802.3ad/802.1AX）、MACSec（802.1AE）、PTP 1588v2[来源: NVIDIA CX7 User Manual §1.4]。

### 6.3 与 PCIe 带宽的匹配关系（第一性原理）

```
单口 400G 收发双向 = 2 × 50GB/s = 100GB/s（含开销）
PCIe Gen5 x16 单向 ≈ 64GB/s（32GT/s × 16 lane × 128b/130b）
⇒ 400G 双向流量需要 PCIe Gen5 x16 全带宽；Gen4 x16（≈32GB/s 单向）只能支撑 ~200G 满载
```

推论：**BOM 选型时若主板只给 OCP 槽位 x8 通道，双口 200G CX7 无法同时跑满**——STH 实测强调 "有些服务器只给 OCP NIC 3.0 槽配 x8，要当心"[来源: STH OCP Review]。

---

## 7. 网络加速与软件生态

### 7.1 加速特性清单

| 类别 | 特性 | 价值 |
|:-----|:-----|:-----|
| RDMA | IB RDMA + RoCEv2（DCB/PFC + 高级拥塞控制） | 低延迟高吞吐 |
| GPU 直连 | GPUDirect RDMA / PeerDirect | 训练梯度同步免 CPU 拷贝 |
| 存储 | NVMe-oF offload（target）、NVMe over TCP 加速、块级加密/校验卸载 | 统一存储网络 |
| 集群体 | Allreduce/Alltoall/Barrier/Vector 卸载 | 减少 CPU 占用、缩短同步时间 |
| Overlay | VXLAN / NVGRE 硬件封装解封装 | 云网络免 CPU 卸载 |
| 虚拟化 | SR-IOV、Multi-Host（4 host）、ATS/PASID | 多租户、多节点共享 |
| 安全 | Secure Boot、Secure FW Update、IPsec/MACsec（Crypto SKU） | 信任根与线速加密 |
| 时序 | PHC + PTP sub-20μs、5T、PPS In/Out | 5G 前传/跨域同步 |

[来源: NVIDIA CX7 User Manual §1.4]

### 7.2 管理平面（BMC 集成）

CX7 支持标准服务器管理通道，对 BMC 呈现为标准 PCIe 卡：

- 物理层：SMBus 2.0/I2C（0x50）、PCIe；
- 传输层：RBT、**MCTP over SMBus / MCTP over PCIe**；
- 协议层：**PLDM**（Monitor & Control DSP0248、Firmware Update DSP026）、**NCSI**；
- 管理操作：secured FW update、FW recovery、NIC reset、监控、端口/启动配置。

> 这意味着 CX7 可无缝接入现有 BMC/IPMI/Redfish 管理链路，机柜级固件基线统一刷写可行（对应超节点整柜刷包场景）[来源: NVIDIA CX7 User Manual §1.4]。

### 7.3 驱动与固件生态

| 组件 | 说明 |
|:-----|:-----|
| MLNX_OFED | Linux 官方驱动栈（含内核模块、rdma-core、工具集），RHEL/Ubuntu 内核内置驱动亦可 |
| WinOF-2 | Windows 驱动 |
| VMware ESXi | SR-IOV 支持（nmlx5-core/rdma VIB） |
| mlxup | 固件升级工具；mlxconfig 配置工具（含端口拆分） |
| MFT | 管理固件工具集（Mellanox Firmware Tools） |

固件/驱动基线差异是 CX7 vs CX8 混用部署的主要运维风险（镜像需双基线）[来源: NVIDIA CX7 User Manual §4 + 知识库 08-25 上电文档]。

---

## 8. 电气/热/环境规格

### 8.1 供电

- 电压：12V + 3.3V_AUX（OCP 版为 12V_EDGE + 3.3V_EDGE），最大辅助电流 100mA；
- **模块供电**：OSFP/QSFP112 端口最大 17W/端口、SFP56 最大 1.5W/端口——均标注 "Not thermally supported"（即 17W 是电学上限，散热不保证，高温场景需降额）[来源: NVIDIA CX7 OCP3.0 Manual §14]。

### 8.2 典型功耗（被动铜缆 + PCIe Gen5 x16）

| OPN | 功耗 |
|:----|:----:|
| MCX75310AAS-NEAT（400G 单口，无 Crypto） | 24.9W |
| MCX75310AAC-NEAT（400G 单口，Crypto） | 25.9W |
| MCX75310AAS-HEAT（200G 单口） | 16.7W |
| MCX75343AMS-NEAC（OCP 400G，无 Crypto） | 24.4W |
| MCX75343AMC-NEAC（OCP 400G，Crypto） | 25.9W |
| MCX753436MS-HEBB（OCP 双口 200G） | 24.5W |

[来源: NVIDIA CX7 User Manual §9 + OCP3.0 Manual §14]

> 全家族 24-26W 量级（400G SKU），远低于 BF3 DPU（含 Arm 核，功耗更高）——纯 NIC 形态的低功耗是 CX7 大规模部署优势。

### 8.3 环境与认证

| 维度 | 规格 |
|:-----|:-----|
| 工作温度 | 0°C 至 55°C |
| 存储温度 | -40°C 至 70°C（不含包装） |
| 工作湿度 | 10%-85% RH |
| 存储湿度 | 10%-90% RH |
| 海拔 | 3050m |
| 安全 | CB / cTUVus / CE |
| EMC | CE / FCC / VCCI / ICES / RCM / KC |
| RoHS | 合规 |

[来源: NVIDIA CX7 User Manual §9]

> ⚠️ 官方明确：CX7 **仅设计用于数据中心服务器**（有保证供电与气流），不适用于台式机/工作站；OSFP 版必须配 RHS 笼。安装在不满足供电/气流的系统可能损坏卡并导致保修失效。

---

## 9. 应用案例：超节点 Scale-Out 4×CX7

### 9.1 项目口径（知识库内部结论）

超节点项目（512 GPU / 128 节点）Scale-Out 网络冻结方案：

- **每节点 4×CX7 现役**（2026-08-26 用户拍板，替换原"2 现役 + 2 预留"）[来源: 知识库 08-25 上电 IP 文档 §2.2]；
- 用途：计算网（**RoCEv2**），每节点 4 口，**2 rail × 2 卡**分组（P1/P3 → rail A，P2/P4 → rail B）[来源: 知识库 08-25 上电 IP 文档 §5.5]；
- 拓扑：CX7 **直连 Leaf 交换机**（无 Cable Tray 中间跳）[来源: 知识库 klx-scale-out-network-evaluation]；
- IP 编址：`10.3.<R>.<S>` / `.S+64` / `.S+128` / `.S+192` 四段零重叠，与 Leaf/Spine 设备段互斥[来源: 知识库 08-25 上电 IP 文档 §5.5]；
- 调度服务器：CX7 **2×200G**（400G 一分二接双 TOR）[来源: 知识库 08-20 superpod 实施设计]。

### 9.2 规格口径对照（本文档对项目方案的校验）

| 项目描述 | 本文档规格事实 | 结论 |
|:---------|:---------------|:-----|
| "CX7 400G×2" | CX7 单口 OSFP=400G，双口 QSFP112=2×200G | ⚠️ 需确认采购 SKU：若需 2×400G/卡，应选 2 张 400G 单口或 BlueField-3；若 2×200G 即可，选 MCX753436*（双口 QSFP112） |
| "4×CX7/节点，2 rail×2 卡" | 单卡双口 QSFP112 天然支持 2 口独立编址 | ✅ 与 4 口/节点编址兼容 |
| RoCEv2 | CX7 原生支持 RoCEv2 + DCQCN/PFC | ✅ |
| 整柜固件统一刷写 | MCTP/PLDM 管理通道 + BMC 集成 | ✅ |

> 上表暴露一个**待澄清口径**：知识库多处写作"CX7 400G×2"，而 CX7 双口 QSFP112 规格为 2×200G（合计 400G）。若"400G×2"指**每卡 2×400G**，则需改用双 400G 单口卡或 BlueField-3；若指**每卡总带宽 400G（2×200G）**，则 MCX753436* 系列匹配。**建议与供应商规格书核对后冻结 OPN**（与 08-20 文档"待确认项"一致）。

---

## 10. 代际与竞品对比

### 10.1 代际对比（CX6 → CX7 → CX8）

| 维度 | ConnectX-6 | ConnectX-7 | ConnectX-8 |
|:-----|:-----------|:-----------|:-----------|
| IB | HDR 200Gb/s | NDR 400Gb/s | NDR 400×2 |
| 以太 | 200GbE | 400GbE | 800GbE |
| PCIe | Gen4 x16 | Gen5 x16 | Gen6 x16 |
| 端口典型 | 2×QSFP56 | 1×OSFP / 2×QSFP112 | 2×OSFP |
| 发布 | 2019 | 2022 | 2025 |
| 功耗典型 | ~15W | ~25W | ~30W+ |

[来源: 知识库 08-20 superpod 实施设计（CX8 口径）+ NVIDIA 官方手册]

### 10.2 竞品对比

| 维度 | NVIDIA CX7 | Intel E810（100G） | Broadcom Thor 2（400G） |
|:-----|:-----------|:-------------------|:------------------------|
| 最高以太 | 400GbE | 100GbE | 400GbE |
| IB 支持 | ✅ NDR | ❌ | ❌ |
| RDMA 消息率 | 330-370 Mpps | 约 100 Mpps 级 | — |
| GPUDirect | ✅（NVIDIA 生态原生） | 部分（需验证） | 部分 |
| 集群体卸载 | ✅ | 有限 | 部分 |
| AI 集群生态 | NVIDIA 全栈（NCCL/Quantum） | 通用云 | 以太/ULC 阵营 |

CX7 的核心护城河是 **IB+以太双协议 + NVIDIA 生态闭环（NCCL 深度适配、Quantum-2 SHARP 协同）**；纯以太场景则与 Broadcom 400G NIC 正面竞争[来源: STH/知识库 08-20 实施设计对比]。

---

## 11. BOM 选型建议

### 11.1 按场景选型决策

```
场景判定：
├─ 需要 InfiniBand（HPC/超算/最高性能训练）→ CX7 VPI 400G 单口 OSFP（MCX75310A*）
│    或 NDR200 双口 QSFP112（MCX753436*）
├─ 需要 RoCEv2（以太训练集群）→ CX7 以太双口 QSFP112（2×200G 或拆分 100G）
├─ 双路服务器避免跨 socket → Socket Direct 版（MCX715105AS / MCX755106*）
├─ 高密度多节点共享 → Multi-Host 版（4 host 共享）
├─ 电信/5G 前传 → MCX713114TC-GEAT（PPS/SyncE）
└─ 50G 密度/成本敏感 → MCX713104*（4×SFP56）
```

### 11.2 采购规格清单（RFP 要点）

| 项目 | 要求 | 验证方法 |
|:-----|:-----|:---------|
| OPN 冻结 | 明确 Legacy OPN + NVIDIA SKU 双编号 | 与供应商规格书逐字段核对 |
| 端口能力 | 明确"400G×2"的确切语义（2×400G or 2×200G） | 见 §9.2 待澄清项 |
| PCIe 通道 | 确认主板 OCP/PCIe 槽位是 **x16 通道**（非 x8） | 主板规格书 + lspci 实测 |
| 连接器 | OSFP 版确认 **Flat-top + RHS 笼**；QSFP112 版确认光模块散热 | 实物验证（STH 踩坑点） |
| Crypto | 安全要求高选 AC（Crypto Enabled）后缀 | OPN 后缀规则 |
| 固件基线 | 与 CX8 混用时镜像双基线 | 装机流程核对 |
| 供电 | 单卡 25.9W + 模块 17W×2，核算节点供电裕量 | 功耗表 §8.2 |
| 认证 | CE/FCC/RoHS 等合规 | 证书核查 |

### 11.3 关键风险提示

1. **400G 端口对 PCIe Gen5 x16 的强依赖**：x8 槽位或 Gen4 平台无法跑满，400G SKU 白买；
2. **OSFP 生态兼容**：Flat-top vs Fin-top 连接器、DAC 散热器尺寸——线缆采购前实物验证；
3. **17W 模块供电"不做热保障"**：高功率光模块需额外散热设计，优先 NVIDIA LinkX 线缆；
4. **私有 IB 增强**：非 NVIDIA 交换机下 NDR 长距/低误码增强不生效，混合生态需实测。

---

## 12. 参考文献

[1] NVIDIA, *NVIDIA ConnectX-7 Adapter Cards User Manual*, 官方 PDF（networking-docs.nvidia.com/connectx7hw，114 页）— OPN 全表/规格/特性/接口 [来源: [1]]

[2] NVIDIA, *NVIDIA ConnectX-7 Cards for OCP Spec 3.0 User Manual*, 官方 PDF（networking-docs.nvidia.com/connectx7ocp3hw，62 页）— OCP 版规格/功耗/端口拆分 [来源: [2]]

[3] ServeTheHome, *NVIDIA ConnectX-7 400GbE and NDR Infiniband Adapter Review from PNY*, 2023-05-03 — OSFP 形态/连接器踩坑/双路 socket 问题 [来源: [3]]

[4] ServeTheHome, *NVIDIA ConnectX-7 OCP NIC 3.0 Review 2-port 200GbE and NDR200 IB*, 2024-05-07 — OCP 形态实测/ethool/lspci/200G 性能 [来源: [4]]

[5] 知识库, *2026-08-25-supernode-power-on-sequence-ip-auto-config-deep-analysis*（v1.3）— 4×CX7 拍板/2 rail×2 卡/IP 编址 [来源: [5]]

[6] 知识库, *2026-08-20-superpod-cluster-implementation-design* — 部署设计/CX7 vs CX8 口径 [来源: [6]]

[7] 知识库, *klx-scale-out-network-evaluation* — CX7 直连 Leaf 拓扑 [来源: [7]]

---

## 13. 变更记录

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-28 | v1.0 | 首次创建：基于 NVIDIA 官方 CX7 User Manual（PCIe + OCP3.0 两册 PDF）+ STH 两篇实测 + 知识库超节点口径，输出 CX7 全家族规格解读与工作原理、BOM 选型建议 |
