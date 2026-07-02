# 🌐 超节点标准与开放生态跟踪

> **维护**: 定期跟踪 ODCC/OCP/UALink/CXL/JEDEC 等开放标准进展
> **更新**: 2026-07-02 · 第22次跟踪
> **前置**: 每日跟踪日志见 [01_survey/supernode/](../01_survey/supernode/)

---

## 🏗️ 目录导航

- [🔥 最新动态 (2026-07-02)](#-最新动态-2026-07-02)
- [🔥 最新动态 (2026-06-30)](#-最新动态-2026-06-30)
- [🔥 最新动态 (2026-06-28)](#-最新动态-2026-06-28)
- [🔥 最新动态 (2026-06-27)](#-最新动态-2026-06-27)
- [📅 近期关键活动日历](#-近期关键活动日历)
- [📌 标准进展总览](#-标准进展总览)
- [🔗 引用关联](#-引用关联)
- [📝 修订记录](#-修订记录)

---

## 🔥 最新动态 (2026-07-02)

### ① 🔥 **HBM2e 供应链危机实证 — AMD Versal Premium Gen 2 被迫从 HBM 全面转向 LPDDR5X**

**日期**: 2026-06-30 | **来源**: [ServeTheHome](https://www.servethehome.com/amd-pivots-from-hbm-to-lpddr5x-for-new-versal-premium-gen-2-memory-on-package-chips/) | **影响**: ⭐⭐⭐⭐⭐

**核心内容**:

AMD（前 Xilinx 部门）发布 Versal Premium Gen 2 Memory on Package 系列，标志性决策是**从 HBM 全面转向 LPDDR5X**。这一选择并非技术优化，而是**HBM 供应链枯竭的直接后果**：

| 维度 | 详情 |
|:-----|:------|
| **事件背景** | AI 训练/推理需求爆发 → HBM3/HBM3e 产能被 AI GPU 全部吸收 → HBM2e 产能已被三大原厂（SK hynix/Samsung/Micron）全面停产 |
| **直接结果** | Versal HBM 系列（FPGA+32GB HBM2e）于 **2025年9月宣布停产**；**2026年6月30日为最后下单日** |
| **替代方案** | LPDDR5X on package（堆叠在封装上），非 CoWoS interposer |
| **容量配置** | 未公开细节，但 AMD 强调新方案可实现 **更长产品生命周期**（HBM 方案寿命仅 2-3年 vs DDR/LPDDR 长达 10+ 年） |
| **性能折中** | LPDDR5X 带宽低于 HBM，但能满足 FPGA 类应用的带宽需求 |

**超节点战略启示**: ⚠️ **五级影响分析**

| 层级 | 影响 | 分析 |
|:-----|:-----|:-----|
| **T1 — HBM 供给** | ⚠️ 关键约束 | AI 训练/推理继续吸收 HBM3/HBM3e/4 全部产能，非 AI 芯片（FPGA/DPU/网卡等）的 HBM 供应将持续恶化 |
| **T2 — 超节点内存选择** | 🎯 关键决策 | 超节点内各层（G1~G5）的内存选择受 HBM 供应约束 → G3/G4 层需优先考虑 LPDDR/DDR/CXL 方案，减少对 HBM 的依赖 |
| **T3 — Qualcomm HBC** | ✅ 已验证趋势 | Qualcomm 的 HBC 架构（LPDDR 堆叠在计算 tile 上）与 AMD Versal 的 LPDDR5X 路线形成暗合——**非 HBM 大容量内存方案正在多元化** |
| **T4 — 产品生命周期** | 📊 关键变量 | FPGA 产品标准生命周期长达 10-20 年 vs HBM 产品 2-3 年——**HBM 依赖缩短了超节点组件的有效服役窗口** |
| **T5 — 供应链韧性** | ⚠️ 风险提示 | 超节点设计需纳入 **HBM 替代/降级路径**，避免单一内存方案导致的供应链锁定 |

> **关键洞察**: 这不是个别芯片的路线变更，而是**HBM 作为战略资源的再分配信号**。AI GPU 正在虹吸全球 HBM 产能，非 AI 芯片被迫另寻出路。超节点作为一个**多内存层次系统**，必须在架构设计阶段就内置 HBM 供应的风险缓冲。

---

### ② 🔥 **Supermicro GB300 Super AI Station — DGX Station 桌面级超节点样机解析**

**日期**: 2026-06-27 | **来源**: [ServeTheHome](https://www.servethehome.com/taking-an-up-close-look-at-the-supermicro-gb300-super-ai-station/) | **影响**: ⭐⭐⭐

**核心内容**:

Supermicro 在 Computex 2026 展出 GB300 DGX Station 样机「Super AI Station」，提供了**桌面级超节点的完整架构参考**：

| 规格 | 参数 |
|:-----|:-----|
| **SOC** | NVIDIA Grace Blackwell GB300 — 72核 Grace CPU + Blackwell Ultra GPU |
| **GPU 内存** | 252GB HBM3e（7/8 stacks 启用，7.1 TB/s） |
| **CPU 内存** | 496GB LPDDR5X（4× SOCAMM） |
| **网络** | 2× 400GbE QSFP（NVIDIA ConnectX-8） |
| **散热** | 全液冷（CPU/GPU/内存均液冷板 + 前端散热排） |
| **功耗** | 1,600W TDP（需专用电路） |
| **尺寸** | 桌面式（可装 5U 机架） |
| **价格** | ~$125,000 |
| **图形输出** | 需额外安装 RTX PRO 显卡（GB300 非图形芯片） |

**架构设计要点**:

- **前端散热排 + 3 风扇**：前→后风道，兼顾桌面站和 5U 机架两种部署形态
- **存储**: 4× PCIe Gen5 x4 M.2 2280 插槽
- **额外扩展**: 2× PCIe x16（x8 电气）+ 1× RTX PRO 插槽
- **网络定位**: 2× 400GbE 支持多节点互联或与集群高速回传

**超节点意义**: DGX Station 代表了**最小化超节点**（Single-Node Supernode）的形态边界——
- 合封了超节点的核心要素：大算力 GPU + 大容量内存 + 高速互联 + 全液冷
- **NVLink 仍然是 NVIDIA 生态壁垒**——Supermicro 方案无 UALink/CXL 标准接口
- 提供了与机架级超节点的清晰形态分层：DGX Station（桌面）vs GB300 NVL72（机架）vs 万卡集群

---

### ③ 🔥 **AMD EPYC Venice + HPE Discover 2026 — 81920 核/机架时代的机柜级密度突破**

**日期**: 2026-06-18 | **来源**: [STH: 81920 Cores Per Rack with AMD EPYC Venice at HPE Discover](https://www.servethehome.com/81920-cores-per-rack-with-amd-epyc-venice-at-hpe-discover-2026/) | **影响**: ⭐⭐⭐⭐

HPE Discover 2026 展示了搭载 **AMD EPYC Venice**（96核 Zen 5c）的 **HPE Cray XD670** 高密度节点，单机架可达 **81,920 核**（约 850 节点/机架）。

**超节点意义**: CPU 密度的爆发式增长正在模糊 CPU 节点和 GPU 节点的边界——对于**纯推理/Agent AI 场景**，CPU 机架的 Token/s 收益正在快速追赶 GPU。超节点架构需重新评估**异构算力配比**（CPU:GPU:NPU）的优化模型。

---

## 🔥 最新动态 (2026-06-28)

### ① 🔥 **UALink 正式提出 In-Network Compute 架构 — 定义 AI Scale-Up 新范式**

**日期**: 2026-06-24 | **来源**: [UALink Consortium Blog](https://www.ualinkconsortium.org/blog) | **影响**: ⭐⭐⭐⭐⭐

**核心内容**:

UALink 联盟于 6月24日 发布最新博客《Exploring In-Network Compute: How UALink Is Redefining AI Scale-Up Architecture》，系统阐述了 UALink 架构中 **In-Network Compute（网内计算）** 的设计理念：

| 维度 | 详情 |
|:-----|:------|
| **核心思想** | 将集合通信操作（all-reduce、reduce-scatter）**下沉到互联 Fabric 内部执行**，而非在 Host/GPU 上处理 |
| **竞争对标** | 直接对标 NVIDIA NVLink SHARP（网内规约加速）技术 |
| **架构创新** | UALink 在 Scale-Up 域内同时承载**数据和计算语义**，成为"智能互联" |
| **性能收益** | 减少 GPU 参与集合通信的开销 → 更多计算时间 → 更高 Token/s |
| **生态配合** | 与 UEC（Ultra Ethernet Consortium）Scale-Out 域形成**分层计算架构**：Scale-Up (UALink) + Scale-Out (UEC) |

**超节点意义**:
- UALink 从"纯互联标准"升维为**"互联+计算融合标准"**，这是 NVLink 一直以来的差异化优势
- 在超节点 Scale-Up 域内（LV2~LV3），In-Network Compute 可显著提升训练 MFU
- UALink + UEC 的分层架构意味着超节点互联的「**两层计算**」趋势：Fabric 级别不再仅是"通道"，也是"算力"
- 与 Astera Labs Scorpio 的 In-Network Compute / Hypercast 形成呼应——**整个 Scale-Up 生态都在向 Fabric 内计算演进**

> **延伸关联**: Astera Labs Scorpio 320-lane PCIe 交换机同样内建 Hypercast 数据复制引擎和 In-Network Compute 能力（见下文⑤）。UALink 与 PCIe/CXL 网内计算正在**双线并行**。

---

### ② 🔥 **OCPC 2026 倒计时 11 天 — 字节四线并发，定调国内超节点走向**

**日期**: 2026-07-09（倒计时 11 天） | **来源**: OCPC 官网 | **影响**: ⭐⭐⭐⭐⭐

**核心看点更新**:

距离 OCPC 2026（7月9日·北京）仅剩 11 天，以下是关键议程回顾：

| 字节四线并行 | 论坛 | 主题 |
|:------------|:-----|:-----|
| **主论坛** | 「大禹」AI 基础设施首次公开亮相 | 超节点整体架构与自研进展 |
| **智算基础设施论坛** | OpenBMC 固件可观测性方案 | 国产 BMC 标准与超节点管理 |
| **计算生态论坛** | 云固件方案 | 超节点软硬件协同设计 |
| **绿色计算论坛** | 液冷方案 | 800V DC 供电架构与液冷集成 |

**开放系统设计论坛三路线索**:
- **阿里 ScaleUP 互联**
- **CXL 内存池化**
- **PCIe 光互联**

三条路线同台将决定国内超节点互联技术未来 2 年的选择方向。

---

### ③ 🔥 **Astera Labs Scorpio 320-Lane 智能 PCIe 交换机 — 发货至顶级超大规模客户**

**日期**: 2026-05-05 | **来源**: [ServeTheHome](https://www.servethehome.com/astera-labs-scorpio-320-lane-pcie-switch-update/) | **影响**: ⭐⭐⭐⭐

**核心内容**:

Astera Labs 于 5月发布 Scorpio X-Series **320-lane PCIe 智能 Fabric 交换机**，并已开始向顶级超大规模客户发货：

| 特性 | Scorpio X-Series 320-Lane |
|:-----|:--------------------------|
| **最大端口数** | 320 PCIe Lanes（20 × 16 lanes） |
| **产品系列** | P-Series 覆盖 32 ~ 320 lanes |
| **Hypercast** | 数据复制引擎，支持 all-gather、all-scatter、all-to-all |
| **In-Network Compute** | 支持 all-reduce、reduce-scatter 等集合通信操作 |
| **目标市场** | AI 服务器 Fabric 组网，挑战 Broadcom PCIe Switch 统治地位 |
| **发货状态** | ✅ 已向顶级超大规模客户发货 |

**超节点意义**:
- 320-lane 大端口数交换机意味着可以**单芯片连接 20 颗 GPU**（每颗 PCIe x16），减少多级交换延迟
- Hypercast + In-Network Compute 在 PCIe 层级实现**网内规约加速**——与 UALink 的 In-Network Compute 思路同源
- Astera Labs 从 PCIe Retimer → PCIe Switch → 智能 Fabric 交换机的产品演进，体现了**超节点互联芯片的智能化趋势**
- 与 CXL 交换技术路线形成互补：CXL 负责一致性内存池化，Scorpio 负责高性能 PCIe Fabric 组网

---

### ④ 🔥 **UALink 开放生态下半年活动日历确认 — SC26 落地芝加哥**

**日期**: 2026-06 | **来源**: [CXL Events](https://www.computeexpresslink.org/events) + [UALink Events](https://www.ualinkconsortium.org/industry-events) | **影响**: ⭐⭐⭐

**UALink 下半年参与活动**:

| 活动 | 日期 | 城市 | UALink 参与 |
|:-----|:-----|:-----|:------------|
| **CXL Mini DevCon 2026** | 8月3日 | Santa Clara | 预计有 UALink + CXL 互操作性展示 |
| **FMS 2026** | 8月4-6日 | Santa Clara | UALink 内存语义展示 |
| **AI Infra Summit 2026** | 9月15-17日 | Santa Clara | UALink + UEC 联合展示 |
| **OCP Global Summit 2026** | 10月（预期） | San Jose | UALink @ OCP 联合展台 |
| **Supercomputing 2026 (SC26)** 🆕 | **11月15-20日** | **Chicago** | CXL + UALink 互操作性演示 |

> SC26 确认落地芝加哥（11月15-20日），这是继 SC25 圣路易斯后的首次回归中西部。CXL 4.0 和 UALink 2.0 将在 SC26 进行首次大规模互操作性展示。

---

## 🔥 最新动态 (2026-06-27)

### ① 🔥 **计算机展 2026: Wiwynn 展示800V DC液冷Busbar — 超节点供电架构下一站**

**日期**: 2026-06-26 | **来源**: [ServeTheHome](https://www.servethehome.com/liquid-cooling-a-te-connectivity-800v-dc-busbar-and-more-from-the-wiwynn-booth/) | **影响**: ⭐⭐⭐⭐⭐

**核心内容**:

在 Computex 2026（6月初·台北），Wiwynn 展位展示了 TE Connectivity 的 **800V DC 液冷总线方案**，为下一代 AI 超节点设计提供了关键的供电架构参考：

| 维度 | 详情 |
|:-----|:------|
| **电压转换** | 800V/75A HVDC → 400V ELCON MICRO+ |
| **功耗规模** | 单组件 60kW+（800V × 75A），整机柜级别 |
| **散热方案** | busbar **液冷**（非传统风冷busbar） |
| **组装方式** | 整条预组装 drop-in 设计，支持机器人自动装配 |
| **目标场景** | 下一代 AI 加速器（100+cm² 双加速器 mockup） |

**超节点意义**:
- 超节点功耗密度从传统 1U/2U 服务器跳升至整机柜级
- 800V HVDC 成为超节点配电的必然趋势（ORv3 已铺垫 48V，下一步直跳 800V）
- 液冷从芯片级拓展到 busbar/电源线缆级——**供电链路全液冷**成趋势
- TE Connectivity 的标准化方案意味着 800V DC 正在从概念走向工程化

> **与 ODCC dOCS 的关联**: ODCC dOCS（密集型开放计算服务器标准）2026夏季版草案正在讨论超节点整体供电架构规范，800V HVDC 是供电方案的核心技术方向之一。详见 [2026-06-07 跟踪](../01_survey/bmc-system/2026-06-07.md)。

---

### ② 🔥 **CXL 4.0 规范正式发布 — 为超节点 Scale-Up 互联加码**

**日期**: 2026-06（近期发布） | **来源**: [CXL 联盟官网](https://www.computeexpresslink.org/) | **影响**: ⭐⭐⭐⭐

**核心规格升级**:

| 特性 | CXL 3.X | CXL 4.0 | 提升 |
|:-----|:--------|:--------|:-----|
| **带宽** | 64 GT/s | **128 GT/s** | 2× |
| **端口绑定** | 单端口 | **Bundled Ports**（多端口聚合） | 支持更大规模互联 |
| **内存 RAS** | 基础 RAS | **增强内存 RAS** | 更强的 FI/FRU 级错误恢复 |

**超节点意义**:
- 128 GT/s 带宽配合 PCIe Gen6 物理层，使 CXL 在超节点内 Scale-Up 场景（LV2~LV3 互联）更具竞争力
- Bundled Ports 支持多个 CXL 端口捆绑，适合 GPU 集群中内存池化的大带宽需求
- 增强 RAS 对超节点集群（数千 GPU）尤为重要——故障定位和恢复时间直接影响 MFU

**同场活动**: CXL Mini DevCon 2026 将于 **8月3日·Santa Clara Marriott** 举行，与 FMS 2026（8月4-6日）背靠背。

---

### ③ 🔥 **UALink 生态加速: 互操作性测试 + 首款 Switch IP 验证完成**

**日期**: 2026年4-5月 | **来源**: [UALink Press Room](https://ualinkconsortium.org/news/pressroom/) | **影响**: ⭐⭐⭐⭐

**三线程进展**:

| 线程 | 详情 |
|:-----|:------|
| **ODCC UALink 测试验证服务** (4月2日) | ODCC 发布 UALink 测试验证服务，标志着 UALink 从规格走向**实质性互操作性测试** |
| **Netforward 首款 UALink Switch/IP** (4月24日) | 迅特通信完成全球首款 UALink Switch/IP 产品设计和原型验证 |
| **Keysight 发布 UALink 200G/PCIe 7.0/CXL 3 验证方案** (2月18日) | Keysight 为 Scale-Up 互联同时提供 UALink/PCIe/CXL 三协议的验证平台 |

**超节点意义**:
- UALink 联盟已从规范制定阶段进入**工程化验证阶段**
- ODCC 的测试服务对国内超节点厂商（华为/阿里/字节等）尤其重要——可直接利用本土测试资源
- 三协议（UALink + PCIe + CXL）统一验证平台的出现，意味着超节点内不同类型互联的测试标准化

---

### ④ 🔥 **超大规模厂商通过 CXL 复用退役 DDR4，应对 DDR5 供应约束**

**日期**: 2025-12-08 | **来源**: [ServeTheHome](https://www.servethehome.com/hyper-scalers-are-using-cxl-to-lower-the-impact-of-ddr5-supply-constraints/) | **影响**: ⭐⭐⭐

**核心内容**:

Marvell Structera X/A 系列 CXL 控制器正在被超大规模厂商采用，通过 CXL 接口复用退役服务器的 DDR4 内存：

| 特性 | Structera X 2404 (DDR4) | Structera X 2504 (DDR5) |
|:-----|:------------------------|:------------------------|
| **通道数** | 4通道 DDR4 | 4通道 DDR5 |
| **每控制器容量** | 12根 DDR4 DIMM（3DPC） | DDR5 DIMM |
| **压缩** | LZ4 线速压缩 1.8-2× | LZ4 线速压缩 1.8-2× |
| **典型容量** | 1.5TB（128GB DIMM × 12），压缩后 ~2.75-3TB | — |
| **来源** | 退役服务器回收，"免费" | 新采购 |

**超节点意义**:
- CXL 内存扩展在超节点的 G3.5 层（KV Cache 存储）有直接应用场景
- 利用 CXL 控制器 + 退役 DDR4 构建低成本大容量内存池，可有效降低超节点 TB 级 KV Cache 的存储成本
- LZ4 线速压缩 1.8-2× 意味着 CXL 扩展内存的有效成本仅为原生 DDR5 的一半

---

### ⑤ 🔥 **CXL Chiplet 架构 — 为超节点异构集成铺路**

**日期**: 2026-05-01 | **来源**: [CXL Blog](https://www.computeexpresslink.org/blog/) | **影响**: ⭐⭐⭐

CXL 联盟博客发布「Chiplet Architecture for CXL Solutions」，系统阐述了 CXL 设备如何采用 Chiplet 架构设计：

- **CXL Controller Die** + **Memory Controller Die** 分离设计
- 支持不同代际/类型的存储器接入同一 CXL 设备
- 为超节点内 CXL 交换机和内存池化提供了芯片级可扩展性

---

## 🔥 最新动态 (2026-06-30)

### ① 🔥 **Qualcomm Investor Day 2026 — 发布 Dragonfly C1000 CPU + HBC 架构 + UALink 确认集成**

**日期**: 2026-06-24（报道日: 2026-06-29） | **来源**: [ServeTheHome](https://www.servethehome.com/qualcomm-investor-day-2026-data-center-announcements-cpus-ai-accelerators-and-more/) | **影响**: ⭐⭐⭐⭐⭐

**核心内容**:

Qualcomm 于 6月24日 Investor Day 2026（纽约）全面发布数据中心战略，三大硬件产品线同时披露：

| 产品线 | 详情 | 对超节点的意义 |
|:-------|:-----|:--------------|
| **Dragonfly C1000 CPU** | 250+ 核 Chiplet 设计，PCIe Gen7，CXL，LPDDR，可选 HBC attach，企业级 RAS | 超节点 CPU 节点核心选择 |
| **HBC (High Bandwidth Compute)** | 将 LPDDR 内存直接堆叠在计算晶圆上，消除 HBM over CoWoS interposer 功耗/成本代价，AI250 代（2027）首发 | **颠覆超节点内存层次设计** |
| **UALink 集成路线图** | HBC Gen2 / AI300 代（2027+）**将集成 UALink 和 ESUN 互联 Fabric** | UALink 生态再获重量级硬件厂商承诺 |

**HBC 技术深度解读**:

| 维度 | 传统 HBM 方案 | Qualcomm HBC |
|:-----|:-------------|:-------------|
| **内存位置** | 独立 HBM die 通过 CoWoS interposer 连接 | LPDDR 堆叠在计算 tile 上方 |
| **功耗代价** | HBM PHY + interposer 走线功耗显著 | 消除 interposer 功耗，"最佳每瓦性能" |
| **容量** | HBM3e 单堆 24-36GB | ~768GB LPDDR（估计），但带宽低于 HBM |
| **延迟** | 跨 interposer 延迟 | 极短（近距堆叠） |
| **定位** | 训练主力（高带宽） | 推理/缓存（大容量+高效率） |
| **产品化** | 已成熟 | AI250 (2027) + AI300 (2027+) |

**UALink 路线确认细节**:

> "Alongside HBC Gen2 (AI300?), Qualcomm will integrate fabrics like ESUN and UALink."
> — Qualcomm Investor Day 2026, Tony Pialis

这意味着 UALink 除了 AMD/Intel/Google/Meta 等创始成员外，**Qualcomm 也将成为 UALink 硬件生态的关键玩家**。Qualcomm 在数据中心互联芯片（Alphawave 收购）和 AI 加速器两端的布局，使其成为 UALink 生态中极有价值的"桥梁型成员"。

**战略意义**:

- UALink 生态从 "传统服务器 CPU/GPU 玩家" 向 "移动/AI SoC 巨头" 扩展
- HBC 架构如果成功，将影响超节点内 G3~G4 层（KV Cache 存储 / 推理缓存）的架构设计
- Qualcomm 通过 Modular 收购补全软件栈（对标 CUDA/Dynamo/Triton），使 UALink + HBC 成为完整平台方案
- **Meta 多代协议承诺**使用 Qualcomm 处理器——进一步验证开放 Scale-Up 路线

---

### ② 🔥 **OpenAI Jalapeño Intelligence Platform — Broadcom 定制 AI 芯片，9个月 Tapeout 验证超节点定制化趋势**

**日期**: 2026-06-24 | **来源**: [ServeTheHome](https://www.servethehome.com/openai-jalapeno-intelligence-platform-shown-powered-by-broadcom/) | **影响**: ⭐⭐⭐⭐

**核心内容**:

OpenAI 于 6月24日通过 X 公开首款定制 AI 芯片「Jalapeño Intelligence Platform」：

| 维度 | 详情 |
|:-----|:------|
| **合作伙伴** | Broadcom（芯片设计 + 制造）、Broadcom Tomahawk（网络）、Celestica（机架集成） |
| **设计周期** | 9个月 Tapeout（AI 辅助设计流程） |
| **运行状态** | ✅ 已在实验室运行 GPT-5.3-Codex-Spark |
| **封装** | 两侧共 6 组 HBM 堆叠（估计） |
| **定位** | 推理专用加速器（非训练） |
| **战略意义** | OpenAI 从"芯片采购方"正式变为"芯片设计方" |

**超节点标准影响**:

| 维度 | 分析 |
|:-----|:------|
| **定制化加速** | 超大规模 AI 厂商（OpenAI/Google/Meta/字节）自研芯片成为常态，**开放标准需兼容自有协议** |
| **网络选择** | OpenAI 选择 Broadcom Tomahawk（非 UEC/UALink 专用网络），说明 Scale-Out 互联仍以传统 Ethernet 为主 |
| **机架集成** | Celestica 作为 OCP 生态核心 ODM，暗示了定制芯片 + 开放硬件的混合路线 |
| **设计速度** | 9个月 tapeout 刷新行业记录，AI 辅助设计正在改变 ASIC 研发节奏 |
| **对标准的影响** | 芯片定制化 → 超节点互联标准需提供**足够的灵活性**（非固定拓扑），而非强制统一接口 |

**趋势判断**: OpenAI Jalapeño + Broadcom 的组合，与其说是 NVLink 替代方案，不如说是**推理场景下定制降本的典型案例**。这对超节点标准的启示是：**Scale-Up（训练域）需要统一的高带宽互联标准，Scale-Down（推理域）可能走向高度定制化**。

---

### ③ 🔥 **AMD EPYC 8005 "Sorano" — Zen 5 进入中端 SP6 平台，CXL 2.0 标配化**

**日期**: 2026-06-29 | **来源**: [ServeTheHome](https://www.servethehome.com/amd-epyc-8005-sorano-completely-changes-amd-sp6/) | **影响**: ⭐⭐⭐

**核心内容**:

AMD 发布 EPYC 8005 "Sorano" 系列，与上代 EPYC 8004 "Siena" 同 SP6 插槽但内核架构完全升级：

| 特性 | EPYC 8005 "Sorano" | 相比 EPYC 8004 "Siena" 的变化 |
|:-----|:------------------|:-----------------------------|
| **核心架构** | Zen 5（全缓存版） | Zen 4c → Zen 5，L3 缓存大幅增加 |
| **最大核心** | 84C/168T | 64C → 84C（+31%） |
| **内存** | DDR5-6400 | DDR5-4800 → DDR5-6400（+33% 带宽） |
| **互联** | **CXL 2.0** | CXL 1.1+ → CXL 2.0 |
| **TDP** | 225W（额定额） | +25W（+12.5%，系统级 <10%） |
| **插槽兼容** | ✅ SP6 向下兼容 | Drop-in 替换（BIOS更新即可） |

**超节点意义**:

- CXL 2.0 在 AMD 中端 CPU 平台的标配化意味着 **CXL 内存池化加速进入主流服务器市场**
- 84 核 Zen 5 + DDR5-6400 为超节点管理节点（G1 层）提供充足算力
- SP6 插槽向下兼容降低超节点 CPU 升级门槛

---

## 📅 近期关键活动日历

| 活动 | 日期 | 城市 | 关注点 |
|:-----|:-----|:-----|:-------|
| **OCPC 2026** 🔥 | 7月9日（**8天倒计时**） | 北京 | 字节"大禹"首秀 + 开放系统设计论坛（阿里 ScaleUP / CXL / PCIe光互联） |
| **CXL Mini DevCon 2026** | 8月3日 | Santa Clara | CXL 4.0 技术细节 + 互操作性演示 |
| **FMS 2026** | 8月4-6日 | Santa Clara | CXL 内存展区 + UALink 生态展示 |
| **AI Infra Summit 2026** | 9月15-17日 | Santa Clara | UALink × UEC 分层计算架构展示 |
| **ODCC 2026 开放数据中心大会** | 9月（预期） | 北京 | dOCS/OISA 标准更新、超节点 Token 评价标准 |
| **OCP Global Summit 2026** | 10月（预期） | San Jose | UALink + OCP 联合展示 |
| **Supercomputing 2026 (SC26)** 🆕 | 11月15-20日 | Chicago | CXL 4.0 + UALink 2.0 首次大规模互操作性展示 |

---

## 📌 标准进展总览

| 标准 | 状态 | 最新里程碑 | 对超节点的价值 |
|:-----|:-----|:-----------|:---------------|
| **ODCC dOCS** | 制定中 | 2026夏季版讨论中 · 含"测试方法" | 超节点整体供电/互联/结构规范 |
| **ODCC OISA** | 制定中 | Token评价标准研讨会（6月4日） | 超节点性能衡量从TFLOPS转向Token/s |
| **ODCC 液冷** | 成熟 | 液冷技术白皮书多版发布 | 800V液冷busbar新趋势 |
| **OCP OAM** | 已发布 | V2.0 模块化 | 超节点内部AI加速器形态规范 |
| **OCP DC-MHS** | 已发布 | HPE大规模采用 | 超节点BMC/管理子卡标准 |
| **UALink 1.0/2.0** | ✅ 已发布 | 1.0 (2025.4) · 2.0 (2026.4) · **In-Network Compute** (2026.6) | 超节点 Scale-Up 开放互联 + Fabric 内计算 |
| **PCIe Gen6 + CXL 4.0** | ✅ 规范发布 | 128 GT/s · Bundled Ports · 增强RAS · **Astera Scorpio 320L** | 超节点内存池化/一致性互联 + 智能 Fabric |

---

## 🔗 引用关联

- [超节点每日跟踪](../../01_survey/supernode/) — 每日详细跟踪日志
- [超节点系统架构五维深度分析](../02_rd/03_hardware/06_superpod/supernode-architecture-deep-analysis.md) — 架构体系分析
- [Super POD 四网架构](supernode-architecture-complete.md) — POD规模超节点
- [服务器产品研发全链路知识图谱](../02_rd/00_rd-management/server_design_roadmap.md) — IPD 生命周期矩阵
- [互联层次深度解析](../02_rd/03_hardware/01_hw_core/interconnect-hierarchy-deep-dive.md) — LV0~L5 互联体系
- [ODCC GPU 内存分层空缺分析](../02_rd/03_hardware/05_AIServer/odcc-gpu-memory-hierarchy-gap.md) — 超节点内内存层次

---

## 📝 修订记录

| 日期 | 操作 | 说明 |
|:-----|:-----|:-----|
| 2026-07-02 | ✨ 新增 | 第22次跟踪：HBM2e 供应链危机实证（AMD Versal 被迫从 HBM 全面转向 LPDDR5X）；Supermicro GB300 Super AI Station（DGX Station 桌面级超节点）；AMD EPYC Venice 81920核/机架密度突破 |
| 2026-06-30 | ✨ 新增 | UALink 专题深度分析文档创建 [ualink-deep-analysis.md](./ualink-deep-analysis.md) — 14章全栈分析 |
| 2026-06-30 | ✨ 新增 | 第21次跟踪：Qualcomm Dragonfly C1000 CPU + HBC 架构+ UALink 确认集成（AI300代·2027+）；OpenAI Jalapeño 定制 AI 芯片（Broadcom·9个月tapeout）；AMD EPYC 8005 Sorano 发布（Zen5+CXL2.0 标配化） |
| 2026-06-28 | ✨ 新增 | 第20次跟踪：UALink In-Network Compute 架构发布、OCPC 倒计时11天、Astera Labs Scorpio 320L 智能PCIe交换机发货、SC26确认芝加哥 |
