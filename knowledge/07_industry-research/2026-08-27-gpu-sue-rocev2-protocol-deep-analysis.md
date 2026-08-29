# GPU Scale-up/Scale-out 协议深度分析：SUE vs RoCEv2 与 GPU 型号依赖机理

> **版本**: v1.0
> **日期**: 2026-08-27
> **核心问题**: GPU 支持 SUE 或 RoCEv2 协议为何依赖型号？两者的协议机制、层级定位与方案选择如何？
> **概要**: GPU scale-up/scale-out 协议深度对比——SUE（Broadcom Scale-Up Ethernet）与 RoCEv2 的协议机制与层级定位、"GPU 型号依赖"的机理模型、主流 GPU/XPU 支持矩阵、三种部署架构的选型分析
> **关键词**: SUE, Scale-Up Ethernet, RoCEv2, RDMA, 无损以太网, CBFC, LLR, NVLink, UALink, GPUDirect, 超节点, 协议选型
> **适用范围**: AI 算力基础设施规划 / GPU 平台选型 / 超节点互联架构设计
> 一句话结论: "GPU 支持 SUE 或 RoCEv2、且依赖型号"的本质是——**scale-up 协议（SUE/NVLink/UALink）必须由 GPU 芯片原生集成互联控制器，而 scale-out 协议（RoCEv2）可由外接网卡提供**；因此型号决定了原生 scale-up 协议族，而 RoCEv2 是几乎全型号的公共底座。

## 目录

- [1. 引言与问题定义](#1-引言与问题定义)
- [2. 第一性原理：GPU 互联为何分 scale-up / scale-out](#2-第一性原理gpu-互联为何分-scale-up--scale-out)
- [3. RoCEv2 协议深度剖析](#3-rocev2-协议深度剖析)
- [4. SUE（Scale-Up Ethernet）协议深度剖析](#4-suescale-up-ethernet协议深度剖析)
- [5. "依赖 GPU 型号"的机理与支持矩阵](#5-依赖-gpu-型号的机理与支持矩阵)
- [6. 方案分析与选型](#6-方案分析与选型)
- [7. 趋势展望](#7-趋势展望)
- [8. 结论](#8-结论)
- [9. 参考文件](#参考文件)

---

## 1. 引言与问题定义

### 1.1 分析对象

用户观察："GPU 支持 SUE 或 RoCEv2 协议，依赖 GPU 型号"。本报告回答三个递进问题：

1. **SUE 是什么**？它与 RoCEv2 处于什么协议层级、解决什么问题？
2. **为什么依赖 GPU 型号**？机理是什么、判断规则是什么？
3. **方案上怎么选**？对超节点/万卡集群架构决策有何含义？

### 1.2 术语澄清（消除歧义）

| 术语 | 全称 | 定义 | 协议层级 |
|:-----|:-----|:-----|:---------|
| **SUE** | Scale-Up Ethernet | Broadcom 提出的用于 AI 超节点 **scale-up 域**（XPU-to-XPU 直连/经交换）的以太网互连协议族，含 SUE 与 SUE-Lite 两个规格 | 链路层+传输层优化（基于 802.3 PHY）[来源: ServeTheHome 2025-07-15 Broadcom Tomahawk Ultra Launch] |
| **RoCEv2** | RDMA over Converged Ethernet v2 | IBTA 2014 年发布，将 InfiniBand 传输层（IB GRH+BTH）封装进 UDP/IP/Ethernet，用于 **scale-out 域**（节点间）RDMA 通信 | 传输层（IB 语义 over UDP/IP）[来源: IBTA RoCE 技术规范] |

**关键区分**：SUE 与 RoCEv2 **不是同一层级的竞争关系**——SUE 面向机内/机架内（scale-up，μs 级以下、TB/s 级），RoCEv2 面向机架间（scale-out，μs 级、Gb/s~Tb/s 级）。二者可共存于同一系统（域内 SUE + 域间 RoCEv2），也可互相替代（全 RoCEv2 不建 scale-up 域）。

> 注：业界"SUE"在 2026 年前后语境下无歧义指 Broadcom Scale-Up Ethernet；切勿与"RoCEv2 的 UE（Unreliable Datagram）"等混淆。SUE 亦有被误称为"超以太网"的情形，其与 UEC（Ultra Ethernet Consortium）是**竞合**关系，详见 §4.4。

---

## 2. 第一性原理：GPU 互联为何分 scale-up / scale-out

### 2.1 物理约束驱动三层互联

GPU 集群通信需求呈三个量级分层的物理现实（距离 × 带宽 × 时延的三角约束）：

```
   +-----------------------------------------------------------+
   |  L1 on-die NoC             ~PB/s      ~ns       internal  |
   |  L2 Scale-up (rack)        TB/s   100ns~1us  NVLink/UALink/SUE/HCCS |
   |  L3 Scale-out (inter-rack) Gb~Tb/s  1us~ms    IB/RoCEv2/UEC     |
   +-----------------------------------------------------------+
```

- **带宽**：梯度同步/张量并行的数据量 ∝ 模型参数，而链路带宽受 SerDes 速率 × 并行 Lane 数限制。芯片内可集成数十对高速 SerDes（如 GB300 片上 36 对 224G SerDes = 1.8TB/s 双向 [来源: 新华三《数字化领航》2026-04]），但**成本随距离上升**（铜缆 <4m、光模块价格随速率跃升）。
- **时延**：TP/EP 并行要求同步窗口百纳秒~微秒级；跨机架光纤往返（含 SerDes/FEC/交换）天然 ≥1μs，只能承载对时延不敏感的梯度/数据并行通信。
- **经济性**：TASK UALink 白皮书量化——$100M AI 部署中互联占 $15-25M（15-25%）[来源: TASK Consultancy UALink 白皮书 2026-01]。scale-up 协议复用 802.3 PHY 的直接动机即继承以太网光模块/线缆/交换生态的成本演进红利。

### 2.2 Scale-up 协议的共同技术特征

新华三技术委员会（2026-04）归纳 AI 超节点对 Scale-up 网络的六大核心诉求，各协议均需满足 [来源: 新华三《数字化领航》AI技术专刊]：

| # | 诉求 | 量化指标 |
|:-:|:-----|:---------|
| 1 | 点对点无阻塞高带宽 | ≥200GB/s/链路，112/224GT/s SerDes 为常态 |
| 2 | 内存语义统一空间 | 原生 Load/Store、原子操作；硬件 Cache 一致性（可部分） |
| 3 | 微秒级时延、纳秒级抖动 | 端到端亚 μs，抖动 ≤0.1μs |
| 4 | 高可靠无损 | BER ≤1e-12 |
| 5 | 拓扑适配 | 单级全互联 / 双级胖树 |
| 6 | 生态兼容 | 物理层复用 802.3，兼容既有光模块/线缆/交换机 |

**推论**：scale-up 协议（无论 NVLink/UALink/SUE/HCCS）都必须**芯片级集成**（多通道 SerDes + 流控 + 事务层硬件），这是"协议支持依赖 GPU 型号"的第一性原因——**TB/s 级 scale-up 互联无法靠外插卡实现**。

---

## 3. RoCEv2 协议深度剖析

### 3.1 定位与演进

- InfiniBand（IBTA, 2000）定义了完整 RDMA 语义（QP/WR/完成队列、可靠/不可靠传输、原子操作），但需要专属交换硬件（IB 交换机），成本高、生态封闭。
- **RoCE v1**（2010）：IB GRH+BTH 直接封装进 Ethernet MAC，**无 IP 路由**，仅限 L2 广播域。
- **RoCE v2**（IBTA, 2014）：IB 报文封装进 **UDP/IP**，可路由、可 ECMP 负载均衡，成为 AI 集群 scale-out 事实标准 [来源: IBTA RoCE 技术规范]。
- 2025-2026 语境：RoCEv2 仍是绝大多数 GPU 集群（NVIDIA/AMD/国产）的 scale-out 标准；UEC（Ultra Ethernet）正在定义下一代替代（§7）。

### 3.2 封装格式与帧结构

RoCEv2 报文 = 以太网头 + IP 头 + **UDP 头（目的端口 4791）** + IB 传输头 [来源: IBTA RoCE 规范；RFC 标准以太网封装]：

```
+---------------+----------------+------------+-------------------+-------------+------+
| Ethernet MAC  | IP (IPv4 20B / | UDP (8B)   | IB GRH (40B)      | IB BTH (12B)| Payload + CRC |
| (14B / 18B)   |  IPv6 40B)     | dport=4791 | + payload hdr     | + other IB  |               |
+---------------+----------------+------------+-------------------+-------------+------+
```

设计要点：
- **UDP 目的端口固定 4791** 用于协议识别；**源端口由发送方随机/哈希**生成 → 交换机据此做 ECMP 逐流负载均衡（避免同 QP 乱序）。
- **IB GRH 40B + BTH 12B ≈ 52B 额外头开销**：相比 SUE 的 10B 优化头，RoCEv2 每包头部开销大、小包有效带宽低（这是 SUE 的差异化切入点之一）。
- 依靠 **MTU 高值（典型 4KB）** 摊薄头部开销，但集合通信小包（AllReduce 分段、控制消息）比例高时开销显著。

### 3.3 无损传输三件套（PFC / ECN+DCQCN / ETS）

RDMA 传输层**假设网络不丢包**（丢包即重传风暴、吞吐崩塌），故 RoCEv2 依赖以太网无损机制 [来源: NVIDIA RoCE 白皮书；IEEE 802.1 系列标准]：

| 机制 | 标准 | 作用 | 已知问题 |
|:-----|:-----|:-----|:---------|
| **PFC** | IEEE 802.1Qbb | 按优先级逐跳流控，接收端缓冲将满时暂停上游发送 | HOL 阻塞、死锁风险、多跳不公平、PFC 风暴可致全网瘫痪 |
| **ECN** | RFC 3168 / 802.1Qau | 交换机队列超阈值打 CE 标记，接收端回 CNP 通知发送端降速 | 粒度粗（按流）、CNP 反馈回路慢 |
| **DCQCN** | NVIDIA/Mellanox | ECN 标记 + CNP 通知 + 量化速率降级/恢复（α 算法） | 参数调优复杂（α/g/RPG）；对突发流量反应滞后 |
| **ETS** | IEEE 802.1Qaz | 优先级带宽保障，隔离不同流量等级 | 配置错误会引发 PFC 连锁 |

Intel 在 Xeon + 自研网卡上的 ADQ（Application Device Queues）+ DCQCN 组合可将 RoCEv2 tail latency 降低 **40-60%** [来源: 知识库 intel-cluster-network.md]，印证 RoCEv2 性能高度依赖端到端拥塞控制调优而非协议本身。

**核心矛盾**：RoCEv2 的无损是"网络层补丁式无损"（PFC/ECN 是给 TCP 时代设计的、事后叠加），而 scale-up 协议（SUE/UALink/NVLink）的流控是**原生信用制（CBFC）**——接收端显式授权发送，结构上避免缓冲溢出与 HOL 阻塞 [来源: 新华三《数字化领航》2026-04]。

### 3.4 GPUDirect RDMA：GPU 与 RoCEv2 的结合点

- **GPUDirect RDMA**：NIC 与 GPU 显存直接 DMA（绕过主机内存与 CPU），需 PCIe P2P 或 NVLink-C2C 物理通路 + CUDA 驱动支持 [来源: NVIDIA GPUDirect 技术文档]。
- 意义：RoCEv2 的"GPU 支持"实际由**三件套**决定——①GPU 与 NIC 间物理通路（PCIe 拓扑/C2C）；②NIC 的 RDMA 硬件卸载（ConnectX/Thor/自研）；③软件栈（NCCL/UCX/驱动）。
- **结论**：NVIDIA GPU 的 RoCEv2 能力不来自 GPU 芯片本身，而来自配套 ConnectX 网卡；**"GPU 型号依赖"在这里弱化为"平台依赖"**（HGX 基板+网卡组合）。

### 3.5 RoCEv2 性能边界

| 指标 | 量级 | 条件 |
|:-----|:-----|:-----|
| NIC 单端口 | 100/200/400/800 Gb/s | ConnectX-7/8、Thor Ultra（2026 Hot Chips） |
| 端到端时延（一跳） | ~1-2μs | 典型 400G RoCE 实测 |
| 拥塞收敛 | ms 级（DCQCN 调优后） | 大规模突发时可达数十 ms |
| 有效带宽 | 80-92%（大包） | 小包场景显著下降 |

---

## 4. SUE（Scale-Up Ethernet）协议深度剖析

### 4.1 起源与定位

- **提出方**：Broadcom（交换芯片厂商，无 GPU 业务），2025-07-15 随 **Tomahawk Ultra** 51.2T 交换芯片发布 [来源: ServeTheHome 2025-07-15]。
- **战略动机**：NVIDIA 用私有 NVLink 锁死 scale-up 域 → 非 NVIDIA XPU（Google TPU、Meta MTIA、AMD、国产加速器）需要一个**开放的、基于以太网生态的 scale-up 方案**；Broadcom 借机把其交换芯片打入超节点核心。
- **SWOT 定位**：SUE 是"**今天就能出货的开放 scale-up**"——STH 原话：NVLink 是私有、UALink 交换机尚未量产，而 Tomahawk Ultra 当天出货，且与 Tomahawk 5 pin 兼容、与 102.4T Tomahawk 6 同步 [来源: ServeTheHome 2025-07-15]。

### 4.2 协议栈架构

知识库 CCF 智算超节点互联论坛资料标注 SUE 为"类 AXI 双工、3 层协议栈、支持 1024 XPU" [来源: knowledge/03_AI/train/ai-storage/2026-08-03-ai-storage-application-innovation-three-layer.md]，与主流 scale-up 协议一致的三级架构 [来源: 新华三《数字化领航》]：

```
+-------------------------------------------+
| Transaction layer   memory/message semantics |
| Data Link layer     Flit + CBFC + VC + LLR   |
| Physical layer      802.3 compatible (112/224G) |
+-------------------------------------------+
```

关键设计差异（vs UALink）：
- **地址空间**：UALink 规范层定义 128PB fabric 级统一地址空间（57-bit），跨厂商加速器可直接互访；**SUE 的地址翻译由 XPU 在 SUE 实例外处理**，跨厂商需软件翻译层 [来源: TASK Consultancy UALink 白皮书 2026-01]——SUE 更"轻"、更利于 XPU 各自实现，但牺牲了开箱即用的跨厂内存语义。

### 4.3 关键技术机制（Tomahawk Ultra 实测规格）

STH 2025-07-15 披露的完整机制清单 [来源: ServeTheHome 2025-07-15]：

| 机制 | 规格/说明 | 解决的问题 |
|:-----|:---------|:-----------|
| **小包满速** | 51.2Tbps @ **64B 包**；交换时延 **250ns** | 通用交换机按大包优化，小包吞吐崩塌；AI 集合通信以小包为主 |
| **自适应优化头** | 以太网头 **46B → 10B**（Adaptable Optimized Headers，仍 802.3 兼容） | 降低头部/载荷比，小包有效带宽提升 |
| **CBFC 信用流控** | 接收端有缓冲才授权发送 | 结构性无损，优于 RoCE PFC 的"事后暂停" |
| **链路层重传 LLR** | FEC 检错 + 链路层请求重传，不依赖上层 | 掩蔽物理误码，避免端到端重传的时延抖动 |
| **网内集合通信 INC** | 交换机内做 AllReduce 聚合（对标 NVIDIA SHARP） | 减少节点往返流量，缩短作业完成时间 |
| **拓扑适配** | 针对 HPC/超节点拓扑优化路由 | 全互联/胖树场景性能 |

**端到端量化**：SUE 跨芯片（XPU-to-XPU）通信时延可降至 **400ns 以下**，"足以在以太网架构上模拟 InfiniBand 的无损表现" [来源: 百度聚合《OpenClaw 时代:算力为王》2026-03]。

### 4.4 SUE vs SUE-Lite vs UEC（易混淆概念）

- **SUE**：完整规格，含 CBFC/LLR/优化头等全部机制，需端侧与交换侧协同支持。
- **SUE-Lite**：SUE 的优化/轻量版本，随 Tomahawk Ultra 发布推出 [来源: 纳斯达克 2025-07-15 Broadcom 新闻稿；ServeTheHome 2025-07-15]。
- **UEC（Ultra Ethernet Consortium）**：开放联盟（AMD/Arista/Broadcom/Cisco/Intel/Meta/Microsoft 等），定义面向 scale-out 的下一代以太网（UET 传输层、多路径、包喷洒）。**SUE 与 UEC 是竞合**：STH 读者评论指出 Tomahawk Ultra 初期亦有"UEC 兼容（SUE-Lite）而非完整 SUE"的表述 [来源: ServeTheHome 评论区]——即 Broadcom 用 SUE 打 scale-up、用 UEC 兼容打 scale-out，一鱼两吃。

### 4.5 主流 Scale-up 协议对比

| 维度 | NVLink 5.0 | UALink 1.0 | SUE | UB-Mesh (华为) | ETH-X (腾讯/信通院) |
|:-----|:-----------|:-----------|:----|:---------------|:-------------------|
| 主导方 | NVIDIA（私有） | AMD 联盟 | Broadcom | 华为 | 腾讯+ODCC |
| 物理层 | 私有 SerDes | 802.3 PHY | 802.3 PHY | 私有/兼容 | 802.3 PHY |
| 单 GPU 带宽 | 1.8TB/s | 200G/通道×4 | —（交换侧 51.2T@64B） | — | 50/100/200G 通道 |
| 规模上限 | ≤256（标准 NVSwitch 配置） | 1024 加速器（单层） | 1024 XPU | 层次化 nD-FullMesh | 已发布 1.0 |
| 统一地址空间 | 有（域内） | 有（128PB/57-bit） | **无（XPU 外处理）** | Ownership 机制 | 软件一致性 |
| 成熟度 | 量产 4 代+ | 评估硬件 2026 后期 | **已出货** | 量产 | 早期 |
| 成本/生态 | 封闭、高 | 开放、中 | 开放、复用以太网 | 自主可控 | 开放 |

[来源: ServeTheHome 2025-07-15；TASK UALink 白皮书；新华三《数字化领航》；knowledge/03_AI/train/ai-storage/2026-08-03]

---

## 5. "依赖 GPU 型号"的机理与支持矩阵

### 5.1 机理模型：三层能力解耦

GPU 的协议支持由**三层硬件能力**决定，不同协议依赖的层不同：

```
GPU die native capability (model-dependent)
  |-- integrated scale-up ports (SerDes PHY + txn controller)
  |     -> native NVLink / UALink / SUE / HCCS / CXL support
  |-- integrated RDMA/network engine (e.g. Intel Gaudi RoCE)
  |     -> native RoCEv2 support (no external NIC needed)
  `-- PCIe/CXL host interface
        -> ability to attach external NIC for RoCEv2/IB (generic)

External NIC (platform-dependent, not model)
  `-- ConnectX / Thor / custom RDMA NIC
        -> RoCEv2/IB scale-out capability (NVIDIA GPU normal path)
```

**核心规律**：
1. **scale-up 协议必须芯片原生**（TB/s 带宽 × 数十通道 SerDes 无法外插）→ "支持 SUE" 只能由 GPU 型号决定；
2. **scale-out 协议可外接**（PCIe 4.0/5.0 x16 ≈ 64/128GB/s，可覆盖 1-2×400/800G 网卡）→ RoCEv2 几乎任何型号都"能支持"（经网卡），差异仅在**原生 vs 外接、性能上限与运维复杂度**；
3. 因此用户观察"支持 SUE 或 RoCEv2 依赖型号"**准确且必要**：SUE 是硬绑定型号（芯片集成），RoCEv2 是软绑定（多数型号经网卡可达，但部分入门/推理型号 PCIe 通道数不足）。

### 5.2 主流 GPU/XPU 平台协议支持矩阵

| GPU/XPU | Scale-up 域（原生） | Scale-out 域（RoCEv2/IB） | 型号依赖要点 |
|:--------|:-------------------|:--------------------------|:-------------|
| **NVIDIA H100/H200/B200** | NVLink 4/5（私有） | 经 ConnectX-6/7/8 网卡 RoCEv2/IB（GPUDirect RDMA） | GPU 无以太网 PHY；RoCEv2 全系平台可用 |
| **NVIDIA GB200 NVL72** | NVLink 5 + NVSwitch（129.6TB/s 域） | 经 CX8/Spectrum-X 以太网或 IB | 域外协议由网卡决定 |
| **AMD MI300X/MI350/MI355X** | Infinity Fabric（域内 8 卡）→ MI400 起 UALink | 经 ConnectX 或 AMD Pensando Vulcano 800G RoCEv2/UEC | MI400 原生 UALink 端口（2026） |
| **Intel Gaudi 3** | 无专有域（PCIe） | **芯片集成 24×100G RoCEv2 引擎（原生）** | 罕见"GPU 芯片原生支持 RoCEv2"案例 |
| **华为昇腾 910B/950** | HCCS（域内）/ UB-Mesh（超节点） | 经华为自研网卡/交换 RoCEv2 | 自研全栈，协议族自成体系 |
| **寒武纪思元** | MLU-Link（域内） | RoCEv2（自研/第三方网卡） | 型号间带宽差异大 |
| **国产通用 GPU（摩尔线程/天数/海光）** | 无专有域（PCIe/CXL） | RoCEv2（外接网卡） | 全部依赖外接，无原生 RDMA 引擎 |
| **Google TPU v6/v7** | ICI（私有，芯片原生） | 以太网（自有） | 封闭生态 |
| **SUE 生态 XPU（Broadcom 客户）** | **SUE（芯片原生，待落地）** | RoCEv2/UEC | 2026-2027 新一代 XPU 才可能集成 |

[来源: 知识库 nvidia-gb200-nvl72.md / amd-mi300x-platform.md / huawei-atlas900.md / intel-cluster-network.md；STH 2025-08 多篇]

### 5.3 判断规则（工程可执行）

评估任一 GPU 型号的协议能力，按以下顺序查证：

1. **看芯片规格书"互联端口"章节**：列出的 SerDes 组数 × 速率（112/224G）→ scale-up 域存在性与协议族（NVLink/UALink/SUE/HCCS/私有）；
2. **看是否集成以太网 MAC/PHY**：有 → 原生 RoCEv2（如 Gaudi 3）；无 → RoCEv2 需外接网卡，检查 **PCIe Lane 数 × 代次** 是否够插 1-2 张高速网卡；
3. **看软件栈**：NCCL/集合通信库对该平台的适配度（决定 RoCEv2 实际可用性与性能）；
4. **看超节点参考设计**：OAM/UBB 基板互联走线（scale-up 端口的物理呈现）。

**反直觉点**：NVIDIA 顶级 GPU 反而**不支持 SUE**（NVLink 锁定）；"支持 SUE"的 GPU 只能来自**非 NVIDIA 且新一代**的 XPU 生态——这正是 Broadcom 的商机窗口，也是国产芯片的潜在替代路径。

---

## 6. 方案分析与选型

### 6.1 三种典型部署架构

```
A: NVIDIA full-stack (NVLink intra + RoCEv2/IB inter)
  [GPU]--NVLink-->NVSwitch(intra 130TB/s) --CX8--> Spectrum-X/IB (inter)
  -> best intra-domain, mature inter; closed ecosystem, highest cost

B: Open scale-up domain (UALink/SUE intra + RoCEv2 inter)
  [XPU]--UALink/SUE-->open switch chip(intra) --NIC--> RoCEv2/UEC (inter)
  -> open, reuses Ethernet ecosystem, multi-vendor; weaker intra, immature

C: All-RoCEv2 (no dedicated scale-up domain, PCIe/CXL intra)
  [GPU]--PCIe/CXL--[NIC]--RoCEv2-->Ethernet switch (whole fabric)
  -> simplest, lowest cost; limited TP/EP efficiency; inference/small-scale
```

### 6.2 对比矩阵

| 维度 | A: NVIDIA 全栈 | B: 开放 Scale-up | C: 全 RoCEv2 |
|:-----|:--------------|:-----------------|:-------------|
| 域内带宽 | 1.8TB/s/GPU | 200G~224G×通道（低于 NVLink） | 无/PCIe 级 |
| 域内时延 | ~0.1-0.5μs | <0.4μs（SUE 宣传值） | ~1-2μs |
| 万卡训练效率 | 最高（基准） | 中（线性度 90%+ 目标） | 低（通信占比 30-50%） |
| 生态开放度 | 封闭 | 开放 | 开放 |
| 成本 | $$$$ | $$ | $ |
| 风险 | 供应链/合规（对华） | 协议碎片化、成熟度 | 拥塞控制调优复杂 |
| 适配 GPU | NVIDIA 全系 | 新一代 XPU（含国产） | 几乎所有 |

### 6.3 选型决策树与风险提示

- **决策 1（训练规模）**：≤64 卡单域 → C 可行；≥百卡 TP/EP 密集 → A/B；
- **决策 2（生态绑定容忍度）**：可接受封闭 → A（性能最优）；需多厂商/自主可控 → B（选 UALink 或 SUE 取决于生态成熟度，2026 年两者均处早期，**SUE 已出货、UALink 评估硬件 2026 后期** [来源: STH 2025-07-15；TASK 白皮书]）；
- **决策 3（存量 vs 新建）**：存量 RoCEv2 集群平滑演进到 UEC（同以太网生态）成本最低；新建超节点才值得评估 scale-up 域。

**风险清单**：
1. **协议碎片化**：近 10 种 scale-up 协议并存（NVLink/CXL/UALink/SUE/ESUN/UB/ETH-X/ETH+/Ethlink）[来源: 新华三《数字化领航》]，选错阵营 = 生态锁定或孤儿协议；
2. **SUE 端侧生态待验证**：SUE 是交换侧先行，XPU 端集成进度决定实际可用性（STH 评论质疑 INC 无端侧 NIC 支持难以生效 [来源: ServeTheHome 评论区]）；
3. **地址翻译无统一标准**：SUE 跨厂商内存语义需软件翻译层，削弱"内存语义"卖点 [来源: TASK 白皮书]；
4. **RoCEv2 拥塞控制运维**：PFC 风暴/ECN 参数错误是万卡集群重大事故高发源，需端到端可观测性配套。

---

## 7. 趋势展望

1. **Scale-up 协议物理层以太网化是主线**：UALink、SUE、ESUN、ETH-X 均兼容 802.3 PHY [来源: 新华三《数字化领航》]；448G SerDes（PAM6/PAM8 之争）2026-2027 标准落地，把 scale-up 带宽天花板整体抬高；
2. **UEC 蚕食 RoCEv2 的 scale-out 份额**：UET 传输层 + 多路径 + 包喷洒解决 RoCEv2 拥塞顽疾，Spectrum-X MRC（2026 已商用）是 NVIDIA 对 UEC 的防御 [来源: STH 2026-05-06]；
3. **"一张以太网承载 scale-up+scale-out"**：域内 SUE/UALink + 域间 UEC 同 PHY 同交换生态，运维归一，是开放阵营对抗 NVLink 一体化的终极形态；
4. **国产化窗口**：国产加速器普遍无专有 scale-up 域（仅 HCCS/MLU-Link 小域），SUE/ETH-X 等开放协议是补齐超节点能力的低成本路径；"GPU 型号决定协议支持"将在 2027 新一代国产芯片上成为选型关键参数。

---

## 8. 结论

1. **SUE = Broadcom Scale-Up Ethernet**，是面向超节点 scale-up 域的以太网互连协议（Tomahawk Ultra 交换芯片已出货；51.2T@64B、250ns、优化头 46→10B、CBFC+LLR+INC），与 RoCEv2 不构成同层竞争，而是**域内互补/域外共存**的关系。
2. **"依赖 GPU 型号"的机理**：scale-up 协议必须芯片原生集成（TB/s 物理约束），故 SUE/NVLink/UALink 支持与否由型号硬性决定；RoCEv2 是 scale-out 公共底座，绝大多数型号经外接网卡即可支持，差异在原生 vs 外接与性能上限（Intel Gaudi 3 是罕见的芯片原生 RoCEv2 案例）。
3. **方案含义**：NVIDIA 全系不支持 SUE（NVLink 锁定）；SUE 的客户是新一代非 NVIDIA XPU 与国产加速器生态。选型时先定训练规模与生态容忍度，再在 A（NVLink 全栈）/B（开放 scale-up）/C（全 RoCEv2）间决策，并警惕协议碎片化与 SUE 端侧成熟度风险。

---

## 参考文件

### 内部知识库引用

1. knowledge/03_AI/train/ai-storage/2026-08-03-ai-storage-application-innovation-three-layer.md（CCF 智算超节点互联技术论坛：SUE=Broadcom/1024 XPU/类 AXI 双工/3 层协议栈）
2. knowledge/01_survey/industry-research/supernode-standards.md（TASK UALink 白皮书：SUE 地址翻译由 XPU 在实例外处理）
3. knowledge/01_survey/switch/2026-08-16.md（新华三 Scale-up 技术概述摘要）
4. knowledge/architectures/nvidia-gb200-nvl72.md / amd-mi300x-platform.md / huawei-atlas900.md / intel-cluster-network.md（各 GPU 平台互联架构）
5. knowledge/02_rd/01_product/02_documentation/standards/2026-08-11-task-consultancy-ualink-whitepaper-deep-analysis.md（UALink 白皮书第三方深度分析）

### 外部资料引用

1. ServeTheHome, "Broadcom Tomahawk Ultra Launch for Scale-up Ethernet", 2025-07-15. https://www.servethehome.com/broadcom-tomahawk-ultra-launch-for-scale-up-ethernet/
2. 新华三技术委员会总体规划部 马瑜,《Scale-up 网络技术概述：AI 超节点需要什么样的 Scale-up 网络》,《数字化领航》AI 技术专刊, 2026-04. https://www.h3c.com/cn/d_202604/2824873_233453_0.htm
3. TASK Consultancy (Jimmy Pike), "UALink: An Open, High-Efficiency Scale-Up Interconnect for AI", 2026-01. https://ualinkconsortium.org/wp-content/uploads/2026/01/UALink_White_Paper_Publication_Candidate_FINAL_VERSION.pdf
4. IBTA, "RoCE (RDMA over Converged Ethernet) 技术规范"（RoCEv2 封装与 4791 端口定义）
5. IEEE 802.1Qbb（PFC）/ 802.1Qaz（ETS）/ 802.1Qau（QCN）; RFC 3168（ECN）
6. NVIDIA, "GPUDirect RDMA 技术文档"; NVIDIA RoCE 白皮书
7. Nasdaq/Broadcom, "Broadcom Inc. Unveils Tomahawk Ultra Ethernet Switch, SUE-Lite for AI Scale-Up Networking", 2025-07-15
8. 知乎,"TH5 Ultra 解析"（SUE Adaptable Optimized Headers 机制）; 百度聚合《OpenClaw 时代:算力为王》（SUE XPU-to-XPU <400ns）
9. ServeTheHome, "NVIDIA Spectrum-X MRC", 2026-05-06; "AMD Vulcano 800G NIC / UALink and UEC Scale Plans", 2025-06-13

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-27 | v1.0 | 首次创建：SUE vs RoCEv2 深度对比 + "GPU 型号依赖"机理模型 + 支持矩阵 + 选型方案分析（外部源：STH/新华三专刊/TASK 白皮书/IBTA 规范） |
