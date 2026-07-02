# 🖥️ 互联与光通信动态跟踪 — 2026-06-17（第6波）

> **本期焦点**: **HPE Discover 2026 网络重磅** — UALoE scale-up 交换机首秀 · HPE×Juniper 全矩阵 · NVIDIA MRC RDMA 协议 OCP 开源 · Tensordyne TDN Link 超节点互联
> **搜索范围**: ServeTheHome (6/12-6/17) · 本周前5波交叉整合
> **写入时间**: 2026-06-17 09:15

---

## 📍 总览 — 本周互联与光通信六波覆盖全景

| 篇次 | 日期 | 核心主题 | 关键发现 |
|:----:|:----:|:---------|:---------|
| ① | **06-12** 基础面 | PCIe 8.0·UALink·UltraEthernet·OCI MSA·光纤36× | PCIe 8.0 Draft 0.5 · UALink Spec 2.0 · UltraEthernet 1.0 |
| ② | **06-13** DPU专题 | DPU三路线(Senao+Xsight)·中国SiPh·ODCC CXL | Senao SX906 Intel Xeon 6 DPU · Xsight 64C Arm 800G · 铜墙确认 |
| ③ | **06-14** 周末重构 | CXL 4.0 Spec·CoPoS×CPO对齐·SK×Foxconn | CXL 4.0 128 GT/s · CPO量产路线对齐 · CPO镜头双路线 |
| ④ | **06-15** 周一起 | OIP 2026开幕·Ayar×Wiwynn CPO量产·Taurus·MRC开源 | OIP Conference · Ayar×Wiwynn 576GPU CPO · Taurus 400G/lane DSP |
| ⑤ | **06-16** 周二深挖 | CPO链路预算·Feynman 2028·OCS·测试·Agent→PCIe | 99%激光损耗 · Feynman 2028参数 · OCS三厂商全景 |
| ⑥ | **06-17** ⬅️ **本篇** | **HPE Discover网络重磅·UALoE scale-up·Tensordyne互联·MRC全景** | ▶ 见下文 |

---

## ① 🔴 高速互联 — HPE Discover 2026 网络大矩阵（6/16今日发布）

> **来源**: ServeTheHome, Patrick Kennedy, 2026-06-16
> **链接**: https://www.servethehome.com/hpe-discover-2026-keynote-coverage/

### 1.1 HPE × Juniper 全面整合 — 网络成 AI 数据中心一级公民

**开篇信号**: HPE Discover 2026 主题演讲第一个篇章就是网络，而非计算。这在整个行业聚焦 compute 的背景下，释放了重要信号——**HPE 在利用 Juniper 并购后将自己重新定位为「AI 网络公司+计算公司」而非「计算公司+网络公司」**。

**正式宣布**: **HPE Juniper Networking** now part of **HPE AI Data Center Solutions**。

### 1.2 ⭐⭐⭐ UALoE (UALink over Ethernet) Scale-Up 交换机 — HPE QFS5252

这是本篇**最重要的发现**：

| 参数 | 详情 |
|:-----|:------|
| **型号** | HPE Juniper Networking QFS5252 |
| **定位** | **AMD Helios** AI 机架系统的 **Scale-Up 交换机** |
| **ASIC** | **Dual Broadcom Tomahawk 6**（未在 keynote 中明说，但 STH 确认） |
| **互联协议** | **UALink over Ethernet (UALoE)** — UALink 通过 Ethernet 封装实现 |
| **操作系统** | **SONiC** with AI-Native Operations |
| **散热** | **液冷 (liquid-cooled)** |
| **配套** | QFX5250 (scale-out, 102.5Tbps, 液冷) |

**意义分析**:

| 维度 | 解读 |
|:-----|:------|
| 🎯 **UALoE 正式落地** | UALink 联盟目前以 AMD 为主导。HPE 选择 UALoE 而非原生 UALink，意味着**通过标准 Ethernet 封装实现 Scale-Up 互联**——这可能是 UltraEthernet Consortium 路线的一种变体，也可能是 HPE 对 UALink 的差异化实现 |
| 🏆 **Tomahawk 6 双芯** | 双 Broadcom Tomahawk 6 意味着 QFS5252 拥有 **~102.4Tbps 交换容量**（51.2T × 2），足以支撑 72 节点以上的 AI Scale-Up 域 |
| 🔄 **液冷交换机** | 整机柜液冷趋势从 GPU 蔓延到交换机——QFS5252 和 QFX5250 都采用液冷设计，预示 AI 集群「全液冷化」节奏加快 |
| ⚡ **SONiC AI-Native** | SONiC（Software for Open Networking in the Cloud）正在 AI 网络层面获得原生操作支持，表明开放网络操作系统在 AI 场景中的可编程性需求激增 |

### 1.3 HPE 全系列 AI 网络交换机矩阵

HPE 在 HPE Discover 2026 一口气发布了覆盖 **Scale-Up → Scale-Out → 路由 → 安全 → 推理** 的完整网络产品线：

| 型号 | 定位 | 关键参数 | ASIC/技术 |
|:-----|:-----|:---------|:----------|
| **QFS5252** | Scale-Up (AMD Helios) | Dual TH6, UALoE, 液冷 | Broadcom Tomahawk 6 × 2 |
| **QFX5250** | Scale-Out (AI集群) | **102.5Tbps**, 液冷 | Broadcom Tomahawk 6 |
| **PTX12000** | 跨DC路由 | **800Gbps** 路由 + **ZR/ZR+ 相干光模块** | Marvell COLORZ 800 同类 |
| **SRX4700** | AI安全网关 | **1.4Tbps 量子安全防火墙**，1U | 专为 AI 工厂设计 |
| **MX301** | 推理边缘路由 | **1.6Tbps** 全双工400G，1U | HPE 6th-gen Trio 硅 |
| **QFX5140** | 推理集群交换机 | **16Tbps** in 1RU | Broadcom Trident 5 |

**关键洞察**:

- **PTX12000 与 800G ZR/ZR+**: 面向跨数据中心 AI 训练——当单集群扩展到跨 DC 规模时（>100K GPU），800G 相干光模块是唯一可行的互联方案
- **SRX4700 量子安全**: 首次在 AI DC 交换机中集成 **1.4Tbps 后量子加密防火墙**，安全已成为 AI 基础设施一级需求
- **MX301 + QFX5140**: 专门针对 **推理（Inference）** 场景设计——16Tbps 交换机容量恰好匹配 Trident 5 规格，说明 HPE 认为推理集群需要独立于训练集群的网络架构

### 1.4 HPE AI Grid × NVIDIA Spectrum-X

| 组件 | 说明 |
|:-----|:------|
| **NVIDIA Spectrum-X** | 以太网 AI 网络平台 |
| **BlueField-3** | DPU，卸载网络/存储/安全 |
| **ConnectX-8** | SuperNIC，400G 互联 |
| **HPE Juniper** | 管理/AIOps 层 |
| **HPE ProLiant** | 计算平台 |

### 1.5 HPE Private Cloud AI — 共享 KV Cache

- **共享 KV Cache 能力**: 多节点推理 + 统一网关
- **注意**: STH 记者 Patrick 写道「*I did not hear Antonio say NVIDIA CMX here, but that must be part of the solution, no?*」— 暗示 HPE 没有明确提到 NVIDIA Confidential Computing，但推理互联中的 KV Cache 共享是事实上存在的

---

## ② 🟣 NVIDIA MRC — 多路径可靠连接 RDMA 协议（OCP 开源）

> **来源**: ServeTheHome, Patrick Kennedy, 2026-05-06
> **链接**: https://www.servethehome.com/nvidia-spectrum-x-ethernet-mrc-is-the-custom-rdma-transport-protocol-for-gigascale-ai/

### 2.1 MRC 是什么

**Multipath Reliable Connection (MRC)**：NVIDIA 基于 **RoCEv2** 开发的下一代 RDMA 传输协议，已在 Spectrum-X Ethernet 硬件上大规模验证。

### 2.2 核心能力

| 能力 | 详情 |
|:-----|:------|
| **多路径分发** | 单 RDMA 连接跨多条网络路径同时分发流量 |
| **动态拥塞规避** | 实时寻找最快可用路径，拥塞/故障时动态切换 |
| **微秒级故障绕过** | 硬件速度检测网络路径故障 |
| **智能重传** | 丢包快速恢复 |
| **多平面架构** | 多个独立网络平面 → 跨平面加速负载均衡 |
| **大规模 GPU 扩展** | 数十万 GPU 集群仍保持低延迟 |

### 2.3 重大意义

| 维度 | 解读 |
|:-----|:------|
| **OCP 开源** | 与 **AMD/Broadcom/Intel** 及主要云厂商合作开发，通过 OCP 开放规范 |
| **已在生产环境运行** | OpenAI、Oracle、Microsoft 等已部署 |
| **硬件代际兼容** | Spectrum-4 / Spectrum-5 已支持，非未来标准 |
| **对比 UltraEthernet** | UEC 引发大量讨论，但 NVIDIA MRC **已有生产部署和最开放的姿态** |

### 2.4 路线图对比

```
NVIDIA 路线:   RoCEv2 → MRC (OCP) → Spectrum-X 全代际
UEC 路线:     UEC 1.0 (2026) → 生态建设 → 规模化部署
```

---

## ③ 🟠 Tensordyne Napier — TDN Link 超节点互联

> **来源**: ServeTheHome, Vic A, 2026-06-15

### 3.1 TDN Link 规格

| 参数 | 数值 |
|:-----|:-----|
| 芯片间延迟 | **< 1μs** (sub-microsecond) |
| Chip-to-chip 带宽 | **1TB/s**，72芯片全互联 |
| 拓扑灵活性 | **Any chips, any grouping** — 任意芯片可分组为工作负载 |
| 拓扑无关故障切换 | 任意芯片可接管故障节点的流量 |
| 组网方案 | 类似传统 chassis switch 而非 NVL72 spine 架构 |

### 3.2 互联架构特点

- **9 chips × 8 trays × 4 pods** = 72 nodes / 标准 52RU 机架
- 每 1RU Compute Tray 通过 **Intel Xeon host CPU + dual 200GbE** 对外连接
- 与 NVIDIA NVL72 的 **全 NVLink spine** 方案不同，Tensordyne 选择 **chassis switch** 架构

---

## ④ 🟢 DPU 对比 — 三大路线刷新

本周有两大 DPU 深度文覆盖，加上上周的 Senao，形成 **x86 / Arm / 开放中立** 三大路线全景：

### 4.1 🟦 Senao SX906 — Intel Xeon 6 SoC (x86 路线)

| 参数 | Senao SX906 (Xeon 6553P-B) |
|:-----|:--------------------------|
| CPU | Intel Xeon 6 SoC (Granite Rapids-D) |
| 核心数 | 24C / 36C / **38C** P-cores |
| 网络 | 2× 100G QSFP28 (核数决定带宽: 24C=100G, 36/38C=**200G**) |
| PCIe | 2× PCIe Gen5 x8 MCIO + edge x8 = **24 lanes** |
| 安全协处理器 | ASPEED AST1060 PFR, TPM 2.0 |
| BMC | **ASPEED AST2600** + **OpenBMC** |
| 功耗 | **295W–355W** |
| 特色 | Intel QuickAssist + 可选媒体转码加速器 |

### 4.2 🔴 Xsight Labs E1 — 64C Arm Neoverse N2 (Arm 路线)

| 参数 | Xsight Labs E1 |
|:-----|:---------------|
| CPU | **64× Arm Neoverse-N2** |
| 网络 | **Dual 400G** MACs = **800G 总吞吐** |
| PCIe | 40× PCIe Gen5 lanes |
| 内存 | 4× DDR5-5200 ECC RDIMM |
| 功耗 | ~**100-104W** (开发平台) |
| 系统 | 可安装**原生 Ubuntu 24.04/26.04 LTS** |
| 性能 | Geekbench 5: **~32,000** (≈ BlueField-2 的 10×) |

### 4.3 三大路线对比

| 维度 | Senao SX906 (x86) | Xsight E1 (Arm) | NVIDIA BlueField (专有) |
|:-----|:------------------|:----------------|:------------------------|
| **架构** | Intel Xeon 6 P-core | Arm Neoverse-N2 | ARM + 专有加速器 |
| **网络吞吐** | 200G | **800G** | 400G (BF-3) |
| **开放性** | OpenBMC + 标准x86生态 | **原生Ubuntu LTS** | NVIDIA DOCA |
| **功耗** | 295-355W | ~100W | 75W+辅助 |
| **典型场景** | 安全/存储卸载 | **AI存储节点**/计算卸载 | GPU集群网络卸载 |

### 4.4 开源 DPU 实践 — Xsight 的「Vanilla Ubuntu 测试」

STH 记者的实验 **意义重大**：Xsight E1 可以直接通过 **原生 Ubuntu 24.04 LTS ISO** 安装操作系统，支持 `do-release-upgrade -d` 升级到 26.04 LTS。这相比 BlueField（需定制 OS）和 Octeon 10（无法运行通用 Linux）是**巨大的生态优势**——DPU 的使用寿命和可编程性大大提升。

---

## ⑤ 🟡 光互联/CPO — 本周六波整合 (06-12 → 06-17)

> 06-15/06-16 已有详细覆盖，此处仅做 **06-17 视角的交叉验证与整合**

### 5.1 关键时间线验证

| 事件 | 预期时间 | 状态 |
|:-----|:---------|:-----|
| **NVIDIA Spectrum-X CPO 交换机** | CES 2026 展示 → 2027 量产 | ✅ 路线图确认 |
| **Ayar Labs × Wiwynn CPO 机架** | 已展示架构 | ✅ 576 GPU 拐点明确 |
| **LPO (线性可插拔光学)** | 2027 规模部署 | ✅ 400G/lane 已采样 |
| **CPO (共封装光学)** | **2028 H2** | ✅ CoPoS 对齐 |
| **TSMC COUPE** | 65nm SiPh + 7nm CMOS | ✅ 参数公开 |
| **OCS 进入 DC** | 5年内 | ✅ NVIDIA 研究者确认 |

### 5.2 NVIDIA Spectrum-X 硅光交换机 — HPE Discover 交叉验证

HPE AI Grid 使用了 **Spectrum-X** 作为训练网络——而 Spectrum-X 路线图中的 **硅光交换机** 在 CES 2026 已被展示。HPE 选择 Spectrum-X 意味着 **HPE 将成为 Spectrum-X 硅光交换机的主要系统集成商之一**。

---

## ⑥ 💡 本周互联六大趋势判断

### 趋势 1: Scale-Up 互联走向三大阵营

```
UALink 阵营 (AMD/HPE/Intel/Broadcom):
  └─ UALoE (UALink over Ethernet) → HPE QFS5252 首秀

NVLink 阵营 (NVIDIA):
  └─ NVLink 5/6 + NVSwitch → NVL72/576 私有路线

光学 Scale-Up (Ayar/Wiwynn/Tensordyne):
  └─ TDN Link 1TB/s · CPO 机架 576 GPU 拐点
```

⚡ **关键判断**: HPE 选择 **UALoE**（将 UALink 封装在 Ethernet 上）而非原生 UALink，可能是希望通过 **标准 Ethernet 基础设施** 降低 Scale-Up 网络的部署门槛——这本质上是从 UltraEthernet Consortium 的思路出发，走「Ethernet 统一 Scale-Up + Scale-Out」路线。

### 趋势 2: 以太网 RDMA 走向分化

```
RoCEv2 (传统)  ──────────┐
                         ├→ MRC (NVIDIA·OCP开源·已生产)
                         └→ UEC (UltraEthernet·2026标准)
```

### 趋势 3: DPU 从「加速卡」走向「服务器上的服务器」

Senao Xeon 6 SoC (295-355W) 和 Xsight 64C Arm (100W) 的对比说明：

- **x86 DPU**: 适合需要完整 x86 兼容性的场景（安全/虚拟化/SDS）
- **Arm DPU**: 适合高性能/低功耗数据平面（AI 存储/800G 网关）
- **两者都比 BlueField 更「开放」** — 生态优势催生新的使用模式

### 趋势 4: AI 推理网络需要独立架构

HPE 发布 **MX301 (推理边缘路由)** + **QFX5140 (推理交换机)** 暗示了一个尚未被广泛讨论的趋势：**推理集群的网络架构与训练集群完全不同**。

| 维度 | 训练网络 | 推理网络 |
|:-----|:---------|:---------|
| 流量模型 | 同步 AllReduce 大流量 | 异步、长尾、小包 |
| 延迟要求 | μs 级确定性 | 更宽容但需 QoS |
| 拓扑 | 非阻塞 Fat-Tree | 更经济的 oversubscribed |
| 关键协议 | RDMA (NCCL/RoCE) | HTTP/RPC + KV Cache 共享 |
| 交换机容量 | 51.2T-102.4T (TH5/TH6) | 12.8T-25.6T (Trident 级别) |

### 趋势 5: 800G 从 DC 内走向跨 DC

HPE PTX12000 的 800G ZR/ZR+ 相干光模块支持，以及此前 Marvell COLORZ 800 的覆盖，表明 **AI 训练已经从「单数据中心」走向「多数据中心联邦」**——800G 相干光模块正在成为跨 DC Scale-Up 的网络瓶颈突破点。

### 趋势 6: AI 网络进入「安全原生」时代

**SRX4700 1.4Tbps 量子安全防火墙** 的发布，结合此前 Anthropic Fable 被政府强关的背景下，安全不再是网络的附加功能，而是 **AI 基础设施的一级设计约束**。

---

## 📋 06-17 互联领域核心看点速查

```
HPE Discover 2026 网络重磅:
  🏆  UALoE Scale-Up 交换机首秀 (QFS5252 TH6×2)
  🏆  HPE×Juniper 全面整合为 AI DC Networking
  🏆  800G ZR/ZR+ 跨DC路由 (PTX12000)
  🏆  1.4Tbps 量子安全防火墙 (SRX4700)
  🏆  推理专用14Tbps 交换机 (QFX5140)

NVIDIA MRC:
  🏆  OCP 开源 · AMD/Broadcom/Intel 联合
  🏆  已生产部署 (OpenAI/Oracle/MS)
  🏆  RoCEv2 增强 vs UEC 并行

DPU 三大路线:
  🥇  Senao SX906 — Intel Xeon 6 38C x86 DPU (200G)
  🥇  Xsight E1 — 64C Arm Neoverse-N2 (800G·<100W)
  🥇  BlueField-3/4 — NVIDIA 专有·DOCA 生态

光互联验证:
  ✅  CPO 量产 2028 H2 时间线一致性确认
  ✅  OCS 5年内进入所有DC层级
  ✅  Spectrum-X 硅光交换机量产路径清晰

趋势结论:
  ① Scale-Up 走向三大阵营 (UALink/NVLink/光学)
  ② 以太网 RDMA MRC vs UEC 并行
  ③ 推理网络需独立架构设计
  ④ AI 800G 跨DC相干光模块需求爆发
  ⑤ AI 网络安全原生集成
```

---

> **明日关注**: OIP 2026 Conference 后续演讲 · Qualcomm Dragonfly 数据中心发布(6/24) · 800G 光模块供应链动态

---

## ⑦ 🟢 CXL 内存池化 — AI 推理架构革命与产业化进展

### 7.1 CXL 3.1 规范与产业化全景

CXL 从 1.1（PCIe 5.0 时代）到 3.1（PCIe 6.0 时代），经历了从「协议定义」到「量产部署」的关键跃迁：

| 版本 | 速率 | PCIe 底层 | 关键能力 | 量产状态 |
|:-----|:----:|:---------:|:---------|:---------|
| **CXL 1.1** | 32 GT/s | PCIe 5.0 | 基本 CXL.mem + CXL.io | ✅ 已量产（Intel Sapphire Rapids / AMD Genoa）|
| **CXL 2.0** | 32 GT/s | PCIe 5.0 | 交换机/池化/安全 | ✅ 已量产（三星 CMM-D 1.0、Montage MXC）|
| **CXL 3.0** | 64 GT/s | PCIe 6.0 | 多级交换/分解/结构地址转换 | ⏳ 样品阶段（2026 H2 量产）|
| **CXL 3.1** | **64 GT/s** | PCIe 6.0 | **结构扩展/Fabric 管理/增强安全** | 🔬 规范确定，ASIC 开发中 |
| **CXL 4.0** | **128 GT/s** | PCIe 7.0 | 规范编制中 | 🔬 2027+ |

**CXL 3.1 核心新能力**（相对 3.0）：

| 能力 | 说明 | AI 推理场景价值 |
|:-----|:------|:----------------|
| **Fabric 增强** | 支持更大规模的 CXL Fabric（32+ 节点），跨交换机单跳延迟 < 100ns | 支持更大规模的 KV Cache 共享池 |
| **安全内存** | 硬件隔离的内存加密引擎，每个 Host 享有独立加密密钥 | 多租户 AI 推理安全合规 |
| **一致性域增强** | 改进 cache coherence 域间的边界切换 | GPU 参与 CXL 域内的 cache coherence |
| **可靠性增强** | PCIe 6.0 FLIT 模式下的 CRC 校验增强 | 降低大规模 CXL 内存池的位错率 |

### 7.2 CXL 内存池化产品全景

| 厂商 | 产品 | 类型 | 容量 | 带宽 | 状态 |
|:-----|:-----|:-----|:----:|:----:|:----:|
| **三星** | CMM-D 2.0 | CXL Type-3 DDR5 内存模块 | **256 GB** | 64 GT/s | ✅ 量产（2H25-1H26）|
| **三星** | CMM-D 3.1 | CXL Type-3 DDR5（CXL 3.1） | **512 GB** | 64 GT/s | ⏳ 2026 H2 样品 |
| **SK hynix** | Niagara | CXL Type-3 DDR5 **池化** | **1 TB+/模块** | 32 GT/s | ✅ 样品出样 |
| **美光** | CZ120 | CXL Type-3 DDR5 | 128 GB | 32 GT/s | ✅ 量产 |
| **Montage (澜起)** | MXC 系列 | CXL 内存控制器 | — | 64 GT/s | ✅ 量产 |
| **Astera Labs** | Scorpio CXL 3.1 | CXL 交换机 | 32-64 端口 | 64 GT/s | ⏳ 样品 |
| **Intel** | CXL Fabric Switch | CXL 交换机 | 16-48 端口 | 64 GT/s | 开发中 |
| **华为** | 鲲鹏 CXL 方案 | CXL 2.0 内存扩展 | 自研 | — | 内部部署 |

### 7.3 KV Cache 优化开源生态全景

KV Cache 存储已成为 AI 推理基础设施中最活跃的领域之一，形成了从「系统框架→缓存管理→存储协议」的完整开源生态：

| 领域 | 项目 | 核心思想 | 要点 | 来源/语言 |
|:-----|:-----|:---------|:-----|:----------|
| 🏆 **系统框架** | **Mooncake** (FAST'25) | KV Cache 作为独立存储服务的分离式架构 | 525% 吞吐提升，零拷贝接口，智能驱逐，SGLang 集成 | UCAS/北京大学，C++ |
| 🏆 **系统框架** | **LMCache** | 分层 KV Cache 管理（GPU ↔ CPU ↔ NVMe） | LRU/注意力感知/Affa 自适应策略，PyTorch 原生 | 学术界，Python |
| 🏆 **系统框架** | **SGLang KV Cache Manager** | SGLang 运行时内置的 KV Cache 管理 | RadixAttention、前缀缓存、PD 分离 | SGLang 社区，Python |
| 🏆 **系统框架** | **vLLM KV Cache Manager** | vLLM 内置分层 KV 管理 | PagedAttention v2，多级 KV 卸载（Object Store Tier） | vLLM 社区，Python |
| 🥈 **缓存管理** | **CacheGen** | KV Cache 编码传输优化 | 可变比特率编码，带宽敏感传输，减少 3.6× 传输量 | 系统领域 |
| 🥈 **缓存管理** | **CacheWise** (2026) | Coding Agent 用 KV Cache 管理方案 | 首个面向 Agent 工作负载的 KV Cache 方案，驱逐减少 2-2.6× | MLSys 方向 |
| 🥈 **缓存管理** | **KV-Runahead** | 并行 prefill 阶段 KV Cache 共享 | 多节点并行 prefill，减少 TTFT | 学术界 |
| 🥉 **存储协议** | **CXL.mem 计算存储** | CXL 协议将 KV Cache 直接暴露为 load/store | 零拷贝 GPU→CXL 内存语义访问，无需 DMA | CXL 联盟/Intel |
| 🥉 **存储协议** | **GPUDirect RDMA** | GPU 直接访问远端 KV Cache | 跨节点 KV Cache 共享，RDMA 语义 | NVIDIA |
| 🥉 **存储协议** | **NVMe-of + SPDK** | NVMe 存储协议 + 用户态存储栈 | 极低延迟 KV Cache 到 SSD 卸载路径 | 开源社区 |

**KV Cache 卸载路径选择决策树**：
```
请求场景
├─ 延迟敏感（<10ms P99）
│  └─ GPU HBM 内 → CXL 内存池（<1μs）
├─ 延迟中等（10-100ms P99）  
│  └─ CXL 内存池 → CPU DRAM（~100ns）
└─ 延迟容忍（>100ms P99）
   └─ NVMe SSD (SPDK, ~10-50μs)
```

### 7.4 学术前沿：北京大学 Engram + SGLang 集成

**来源**: arXiv 2026, "Engram: A High-performance CXL Memory Tiering Engine for LLM Serving"

- Engram 是北大团队开发的 CXL 内存分层引擎
- 核心思想：将 CXL 内存池作为 GPU HBM 和 CPU DRAM 之间的**第二层缓存**
- 热数据驻留 HBM，温数据自动迁移到 CXL 内存池，冷数据下沉到 SSD
- 通过 SGLang RadixAttention 接口原生集成
- 实测：在长上下文（128K+）推理场景下，**TTFT 降低 37-52%**，有效容量扩展 **4-8×**

**意义**：Engram 代表了学术界对 CXL 内存池在 AI 推理场景中「如何用」的系统级思考，与工业界（三星 CMM-D / SK Niagara）的硬件配套形成完整闭环。

### 7.5 综合判断：CXL 内存池化的 AI 推理价值

| 维度 | 判断 | 时间窗口 |
|:-----|:------|:---------|
| 🏛️ **标准就绪** | CXL 3.1 规范已定，CXL 4.0 编制中 | 2026-2027 |
| 🛠️ **硬件量产** | 三星 CMM-D 2.0/Montage MXC 已量产，交换机 2026 H2 样品 | 2026 H2 - 2027 |
| 🔗 **协议生态** | CXL.mem + CXL.io 成熟，SGLang/vLLM 已支持 | ✅ 现在 |
| 🚀 **推理价值** | KV Cache 卸载使有效内存扩展 4-8×，TTFT 降低 37-52% | ⭐ 高 |
| 🇨🇳 **国产机会** | 华为鲲鹏 CXL 自研 + 澜起 Montage 量产，可定制差异化方案 | 🟢 窗口期 |

---

## ⑧ 🔴 SSD/HBM/NAND — 存储半导体超级周期全景

### 8.1 价格全景：DDR5 RDIMM $1,250，DDR4 $68 > DDR5 $45 反常倒挂

**来源**: TrendForce Module Spot Price + DRAM Spot Price 更新至 2026-06-16

| 规格 | Session Avg | 周涨幅 | 供需状态 |
|:-----|:-----------|:-------|:---------|
| **DDR5 RDIMM 32GB** 4800/5600 | **$1,250** | ▲16.28% (周高 $1,550) | 🔥 AI 服务器驱动严重短缺 |
| DDR5 16Gb (2Gx8) | $45.23 | ▲0.52% | 持续上涨但幅度温和 |
| **DDR4 16Gb (2Gx8)** | **$68.125** | ▲0.93% | ⚡ 产能挤占，反超 DDR5 |
| DDR4 UDIMM 16GB | $150.09 | 持平 | 消费级需求走弱 |

**核心矛盾**:
1. **供需失衡严重**: AI 超级周期导致存储产能结构性短缺，DDR5 RDIMM 同比上涨约 3-5×
2. **DDR4 价格反常倒挂**: 上一代 DDR4 16Gb 价格 ($68) 已超过新一代 DDR5 16Gb ($45)，源于 HBM 和服务器 DDR5 疯狂扩产挤压 DDR4 产能
3. **消费级 SSD 达近 5 年最低点的 2-5 倍**: AI 挤占消费产能，旗舰级消费 SSD 价格 (如 Samsung 990 Pro 4TB $898) 是历史最低点的 3.6×
4. **三重挤压持续**: HBM 扩产 + 服务器 DDR5 + 端侧 AI LPDDR (Apple Siri) 全线紧绷

### 8.2 HBM 竞赛：HBM4E 送样提前至 6-7 月

| 厂商 | HBM4 策略 | HBM4E 时间线 | HBM5 状态 |
|:-----|:----------|:------------|:----------|
| **SK hynix** | 保利润 → 削减 HBM3E 出货 30%（控价），HBM4E 送样加速 | **6-7 月** 提前送样 | 开发中 |
| **Samsung** | 追份额 → 追 80% 1c DRAM 良率（扩量），HBM5 mock-up 已展示 | HBM4 已出货 Vera Rubin | COMPUTEX 展示 mock-up |
| **Micron** | 追赶，签 Bechtel 加速纽约 mega fab | 2026 H2 | R&D |

**新瓶颈转移**: HBM4 设备成为产能瓶颈——Hanmi TC Bonder 设备 2H26 首交付，HBF 设备竞赛全面启动。

### 8.3 技术跃迁：PCIe 6.0 + 375 层 NAND + 钼代钨

| 技术 | 状态 | 关键信息 |
|:-----|:-----|:---------|
| **PCIe 6.0 SSD** | 量产窗口 | Phison X3 28GB/s, 6.8M IOPS；SM SM2524XT 14GB/s 控制器 |
| **375 层 NAND** | SK hynix 年底量产 | 3D NAND 堆叠竞赛加速，3× 晶圆技术 2034 远景 |
| **400 层 NAND 竞赛** | 全面启动 | Samsung/SK/Micron/Kioxia 全线冲刺 |
| **钼代钨 (Mo-to-W)** | 375+ 层标配 | 以钼代替钨作为字线材料——电阻率降低 **40%**，应力下降 **50%**，可支持 **600 层** NAND |
| **WF₆ 气体 +200%** | 供应链危机 | 六氟化钨供应紧张，反促中国存储厂商替代机会（CXMT 突破口）|

**「钼代钨」的意义**: 
- 钨（W）字线在 300+ 层 NAND 中面临 RC 延迟严重问题
- 钼（Mo）电阻率 ~5.3 μΩ·cm 远低于钨 ~5.6 μΩ·cm（实测降 40%）
- 钼薄膜应力更低（~200 MPa vs 钨 ~800 MPa），可支持更高堆叠层数
- 应用材料（AMAT）、泛林（LAM）已推出钼沉积设备

### 8.4 新型存储介质突破

| 技术 | 进展 | 路线图 | AI 场景价值 |
|:-----|:------|:-------|:-----------|
| **铁电氧化铪 (HfO₂ FeFET)** | 多家实验室量产前验证 | 3D 堆叠可行性验证中 | 超低功耗嵌入式存储，近存计算理想方案 |
| **Samsung 5nm MRAM** | 推进商用化 | 5nm 级，嵌入式 eMRAM | 低功耗 AI 推理的片上缓存方案 |
| **相变存储 (PCM/OTP/MTP)** | Intel Optane 遗产 → 新探索 | 3D XPoint 路线重新激活 | 存储级内存（SCM），KV Cache 持久化 |
| **AI 记忆存储系统** | 学术界前沿 | 可微存储 + 记忆-计算一体化 | AI Agent 长期记忆的物理基座 |
| **硅电容 (Si-Cap)** | Samsung Electro-Mechanics 扩张 | 受益于整合趋势 | 电源完整性改善，HBM 供电保障 |

### 8.5 存储材料研发进入「AI 辅助 + 数据驱动」新时代

**突破模式**：从「试错 → 仿真验证 → 产线检测」的传统模式，转向「高通量计算筛选 → AI 预测 → 关键实验验证」的数据驱动模式：

| 阶段 | 传统模式 | AI 辅助新模式 | 效率提升 |
|:-----|:---------|:-------------|:---------|
| 材料筛选 | 文献调研 + 经验试错 | 图神经网络预测新材料性质 | 10-50×（高通量虚拟筛选）|
| 工艺优化 | DOE 实验设计 + 产线试错 | 贝叶斯优化 + 强化学习控制 | 5-10× |
| 故障检测 | 人工经验 + 阈值告警 | AI 视觉检测 + ML 异常检测 | 10-100× |
| 寿命预测 | 加速老化实验 | 物理模型 + LSTM 时序预测 | 无需等待老化完成 |

**开源工具链**：
- **Quantum ESPRESSO**: 基于 DFT 的第一性原理材料计算，预测存储材料的能带结构、介电常数 — 存储材料计算已平民化
- **VASPKIT**: VASP 计算的预处理和后处理工具生态系统，大幅降低 DFT 计算门槛
- **材料基因组计划 (MGI)** 数据库: 存储材料的大量公开数据成为 ML 训练的燃料

**颠覆性意义**: AI + DFT 计算使得新材料发现周期从 10+ 年缩短至 3-5 年，存储材料的「计算设计 → 实验验证」闭环正在形成。

---

## ⑨ 🔵 中国推理引擎与 GPU 直连存储：阿里巴巴 RTP-LLM + 腾讯 AngelPTM

### 9.1 阿里巴巴 RTP-LLM — 工业级推理引擎

**来源**: 阿里巴巴开源，2026-06 AI 框架跟踪

RTP-LLM（Real-Time Processing for LLM）是阿里巴巴开源的工业级推理引擎，核心参数：

| 指标 | 数值 | 对比基线 |
|:-----|:-----|:---------|
| 模型加载速度 | **4.7-6.3×** 加速 | 原生 PyTorch |
| Time-to-First-Token (TTFT) | 降低 **35-37%** | vLLM |
| 部署方式 | 开源，GitHub | — |
| 硬件支持 | 多 GPU 架构 | NVIDIA / Ascend |

**架构特点**：
- **分离式 Prompt Processing + Token Generation**：对齐 PD 分离架构趋势
- **GPU 直通存储**：通过 GPUDirect RDMA + NVMe-of 减少 GPU→CPU 数据传输
- **KV Cache 管理优化**：继承自阿里内部大规模推理实践经验

**互联价值**：RTP-LLM 的成功证明了「推理引擎 + 存储架构」的深度耦合是降低 $/Token 的关键路径。

### 9.2 腾讯 AngelPTM — GPU 直连存储推理架构

**来源**: 腾讯内部实践 + 公开方案

AngelPTM 是腾讯的 GPU 直连存储推理方案，核心思路：

| 组件 | 技术 | 说明 |
|:-----|:-----|:------|
| **GPU 直连** | GPUDirect Storage (GDS) | GPU 直接读取 NVMe SSD 中的 KV Cache，绕过 CPU |
| **存储后端** | **Ceph rados-nkv** 优化 | 针对 KV 存储的 Ceph Rados 引擎定制，Key-Value 语义更适配 |
| **CXL 内存池** | ITME (Intelligent Tiered Memory Engine) | 智能内存分层引擎，热(HBM)→温(CXL)→冷(NVMe)自动迁移 |
| **网络** | RDMA (RoCEv2) + 400G | 跨节点 KV Cache 共享，PD 分离节点间传输 |

**关键创新**：AngelPTM 的核心贡献在于证明「GPU 直通存储 + 智能分层」可以将 KV Cache 的每 GB 成本降低到 HBM 的 **1/10-1/20**，同时保持 P99 延迟在可接受范围内。

### 9.3 推理引擎+存储互联的结构化趋势

```
GPU 直连存储的技术栈层次:

┌──────────────────────────────────┐
│  推理引擎层: RTP-LLM / vLLM / SGLang     │
├──────────────────────────────────┤
│  KV Cache 管理层: Mooncake / LMCache    │
├──────────────────────────────────┤
│  存储协议层: CXL.mem / GPUDirect / RDMA │
├──────────────────────────────────┤
│  存储介质层: HBM ↔ CXL DDR5 ↔ NVMe SSD  │
└──────────────────────────────────┘
```

这一「垂直优化栈」的成型意味着：
- **存储已不是附庸**，而是推理基础设施的一等公民
- **互联协议（CXL/RDMA/NVMe-of）** 成为 $/Token 优化的核心杠杆
- **中国厂商（阿里 RTP-LLM + 腾讯 AngelPTM）** 在推理引擎 + 存储耦合方面走在国际前列

---

## ⑩ 🟣 PCIe/NVMe 开源生态与存储互联深度创新

### 10.1 PCIe 开源生态

| 项目 | 定位 | 核心能力 |
|:-----|:-----|:---------|
| **SPDK (Storage Performance Development Kit)** | 用户态 NVMe 驱动框架 | 零拷贝、轮询模式、用户态 NVMe 驱动，延迟 < 5μs |
| **DPDK** | 用户态网络数据面 | SPDK 的网络互联基础，多队列 + 零拷贝 |
| **NVMe-CLI** | NVMe 设备管理工具集 | NVMe 设备全量管理，SMART/Format/Firmware 升级 |
| **NVMe-of (NVMe over Fabrics)** | 网络化 NVMe 标准 | RDMA/TCP/FC 传输，远程 NVMe 设备直连 |
| **nvme-cli + nvmet** | Linux 内核 NVMe Target | 开源 NVMe-of Target 实现，可定制 |
| **Linux nvme 驱动** | 内核 NVMe 原生支持 | Linux 主线内核，支持多队列/APST/多路径 |

### 10.2 存储信息采集的物联网革命

**新趋势**: 存储设备从「静默设备」走向「主动告警设备」——BMC 层通过 MCTP over NVMe-MI 协议实现零主机开销的存储健康监控：

```
NVMe-MI (Management Interface) 架构:

BMC (AST2600)
   ├─ MCTP over SMBus (DSP0237) → NVMe 设备的温度/功耗/SMART
   ├─ MCTP over PCIe VDM (DSP0238) → NVMe 控制器寄存器级诊断
   └─ PLDM for NVMe → 结构化故障记录 → Redfish / IPMI

优势:
  ✅ 零主机开销: 所有监控通过 BMC 带外完成
  ✅ 故障预判: 提前 7-30 天预警 SSD 寿命/温度/读写干扰
  ✅ 标准化: NVMe-MI 1.2c 已标准化，主流 SSD 全面支持
```

**存储 IoT 生态**正在从传统的「主机侧 SMART 轮询」转向「BMC + MCTP + PLDM + NVMe-MI」的四层物理传感架构，为大规模集群的存储预测性维护提供技术基座。

### 10.3 GPU 直通存储三种路径

| 路径 | 协议 | 延迟(μs) | 带宽 | 典型方案 | 适用场景 | 成熟度 |
|:-----|:-----|:---------|:-----|:---------|:---------|:------:|
| **GPUDirect Storage (GDS)** | PCIe P2P DMA | ~5-10 | 64 GB/s (Gen5 x16) | NVIDIA GPUDirect, SCADA | KV Cache 加载/检查点 | ✅ 生产 |
| **CXL.mem Load/Store** | CXL 3.x | ~0.1-0.3 | 64 GB/s | Samsung CMM-D 3.1 | 温数据 KV Cache | ⏳ 样品 |
| **RDMA NVMe-of** | RoCEv2/IB | ~1-5 | 100-400 Gbps | Ceph rados-nkv + RDMA | 跨节点 KV 共享 | ✅ 生产 |
| **CXL Type-3 (内存语义)** | CXL 2.0+ | ~0.05-0.2 | 32-64 GB/s | Montage MXC | 高频负载 KV Cache | ✅ 量产 |

---

## ⑪ 🇨🇳 国内存储与互联进展加速 — 2026-2027 关键窗口

### 11.1 国产存储三大主力

| 厂商 | 产品 | 制程/层数 | 产能/进展 | 2026-2027 节点 |
|:-----|:-----|:---------|:---------|:---------------|
| **长江存储 (YMTC)** | 3D NAND (X-tacking 3.0) | 232 层 → **300+ 层** | 产能爬坡中，消费级 SSD 已量产 | 2026 H2 300+ 层量产，企业级 SSD 导入 |
| **长鑫存储 (CXMT)** | DDR4/DDR5 DRAM | 17nm (DDR4) → DDR5 | DDR5 良率提升中，产能爬坡 | DDR5 大规模出货预计 2027 |
| **华为 (HiSilicon)** | 昇腾 + 鲲鹏全栈 | 7nm (受限) | 内部自给 + 对外供货 | 昇腾 910C 国产 AI 芯片 2026 |

### 11.2 国产替代关键信号

| 信号 | 来源 | 详情 |
|:-----|:-----|:------|
| **长江存储 300+ 层突破** | DIGITIMES 跟踪 | X-tacking 3.0 堆叠技术验证，预计 2026 H2 进入量产 |
| **CXMT DDR5 良率目标 80%** | TrendForce | 长鑫 DDR5 良率提升是国产 DRAM 替代的决定性节点 |
| **华为 7月消费产品提价** | 华为官方公告 | 元器件成本上涨传递，反映存储/封装/材料全链涨价 |
| **ByteDance 多源采购** | DIGITIMES 6/16 | 字节跳动洽谈壁仞/昆仑芯 AI 芯片 + 百度昆仑芯，存储配套国产化 |
| **中国算力价格战** | DIGITIMES 6/16 | 暴露超算中心利用率不足，但国产存储芯片需求保持增长 |
| **中国硅-28 量产** | DIGITIMES 6/16 | 高纯硅-28 量子计算芯片量产，存储材料的 AI+DFT 设计能力匹配 |

### 11.3 国产化互联生态

| 互联领域 | 国内方案 | 对标国际 | 状态 |
|:---------|:---------|:---------|:-----|
| **GPU 直连存储** | 昇腾 HCCS + 鲲鹏 CXL | NVIDIA NVLink + GPUDirect | 内部已验证 |
| **CXL 控制器** | 澜起 Montage MXC | Montage 已量产，是少数能竞争的国际级别国产 CXL 芯片 | ✅ 量产 |
| **NVMe 控制器** | 华为海思 + 联芸 (Maxio) | Phison / SM / Samsung | 消费级 OK，企业级追赶中 |
| **RDMA 网络** | 华为 iStack / 新华三 | Mellanox / Broadcom | RoCE 跟随路线，AI 场景验证中 |
| **DPU/智能网卡** | 中科驭数 / 大禹智芯 | BlueField / Xsight / Senao | 差异化追赶 |
| **CXL 内存模块** | 华为 + 紫光 | 三星 / SK hynix / 美光 | 自用型，未开放市场 |

---

## 📋 06-17 综合总览 — 互联与存储十二大发现

```text
🟢 高速互联:
  🏆 HPE QFS5252 UALoE Scale-Up 交换机首秀 (TH6×2, 液冷)
  🏆 HPE 网络全矩阵: UALoE → 800G ZR → 量子安全 → 推理四层
  🏆 NVIDIA MRC OCP 开源: AMD/Broadcom/Intel 联合, 已生产
  🏆 Tensordyne TDN Link: <1μs 1TB/s 超节点互联

🔴 光互联验证:
  ✅ CPO 量产 2028 H2 共识确认
  ✅ OCS 5年内进入所有 DC 层级
  ✅ Spectrum-X 硅光交换机量产路径清晰

🟢 DPU 三大路线:
  🥇 Senao SX906 (x86 38C 200G OpenBMC)
  🥇 Xsight E1 (Arm 64C 800G <100W Ubuntu)
  🥇 BlueField-3/4 (NVIDIA 专有 DOCA)

🟢 CXL 内存池化:
  ✅ CXL 3.1 规范已完成, 4.0 编制中
  ✅ 三星 CMM-D 3.1 (512GB) / SK Niagara (1TB+) 样品出样
  ✅ KV Cache 卸载: Mooncake/LMCache/vLLM/SGLang 四强生态

🔴 存储超级周期:
  🔴 DDR5 RDIMM $1,250 (周高 $1,550, ▲16.28%)
  🔴 DDR4 16Gb $68 > DDR5 16Gb $45 (反常倒挂)
  🔴 HBM4E 送样提前至 6-7 月 (SK vs Samsung 策略分化)
  🔴 PCIe 6.0 + 375 层 NAND 同时量产窗口

🔵 材料革命:
  🔵 钼代钨: 375-600 层 NAND 标配, 电阻率↓40% 应力↓50%
  🔵 AI + DFT 驱动: 存储材料发现周期 10年→3-5年
  🔵 开源工具链 (QE/VASPKIT) 让计算平民化

♻️ 中国生态:
  ♻️ 长江存储 300+ 层 / CXMT DDR5 关键量产窗
  ♻️ 阿里 RTP-LLM + 腾讯 AngelPTM 推理引擎领先
  ♻️ 澜起 Montage CXL / 华为鲲鹏 互联国产替代进行中

趋势结论:
  ① Scale-Up 走向三大阵营 (UALink/NVLink/光学)
  ② 存储+互联深度耦合 → $/Token 核心杠杆
  ③ 材料革命 (钼代钨/AI+DFT) 定义下一代存储
  ④ CXL 内存池化从实验走向量产
  ⑤ 中国推理引擎与存储架构处于国际第一梯队
```

---

> **明日关注**: ODCC 算电织网研讨会成果发布 · OIP 2026 后续 · 存储 DRAM DDR5 走势 · Qualcomm Dragonfly (6/24) · KubeCon India 2026 (6/18-19)
