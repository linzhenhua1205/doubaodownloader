# 🏗️🧊 服务器形态 + 液冷散热动态跟踪 — 2026-06-22（第7波）

> **搜索范围**: ServeTheHome (MiTAC Computex 2026 · HPE Cray GX5000 · Tensordyne Napier) + Tom's Hardware (散热专题) + DIGITIMES Asia (6/22头条·高压供电趋势)
> **本期焦点**: **MiTAC 52U 液冷整机柜 96×MI355X · Diamond Cooling 金刚石散热 · HPE Cray GX5000 Venice 81,920核/机柜**
> **写入时间**: 2026-06-22 10:16

---

## 🔥 核心趋势判断（第7波更新）

| # | 趋势 | 更新内容 | 影响等级 | 来源 |
|:-:|:-----|:---------|:---------|:-----|
| 1️⃣ | **整机柜规格「超标」：52U 成 AI 密度新标准** | MiTAC 推出 52U 液冷整机柜，比传统 42U/48U 机柜更高，装 12 × 4U 服务器 = 96 GPU/rack，宣称密度提升 50% | 🔴 **重大** | STH 6/21 |
| 2️⃣ | **合成金刚石（Diamond Cooling）进入服务器散热市场** | Akash Systems 金刚石导热材料用于 8U G8825Z5 服务器，允许 35°C 进风不降频，数据中心可减少冷却能耗 | 🟡 **中等** | STH 6/21 |
| 3️⃣ | **液冷从 GPU 扩展到 CPU/内存/SSD 全组件覆盖** | HPE Cray GX5000 液冷刀片覆盖 CPU 冷板 + DIMM 液冷 + 顶置 SSD 冷板，1.6MW CDU | 🟡 **中等** | STH 6/17 |
| 4️⃣ | **CPU 密度新高度：81,920 核/机柜** | AMD EPYC Venice 256 核 × 8 路 blade × 36-40 blade = 81,920-81,920 核，单机柜 250-320kW | 🔴 **重大** | STH 6/17 |
| 5️⃣ | **AI 供电架构向更高电压演进** | DIGITIMES 报道 AI 数据中心供电向高压设计转型（DIGITIMES头条） | 🟢 **新兴** | DIGITIMES 6/22 |

---

## 🏗️ 服务器整机柜新形态

### 🔴 MiTAC 52U 液冷整机柜 — AMD MI355X 96-GPU 密度新标杆

> **来源**: ServeTheHome, Ryan Smith, June 21, 2026
> **链接**: https://www.servethehome.com/mitac-computex-2026-booth-tour/

**核心规格**:

| 参数 | 详情 |
|:-----|:------|
| 机柜高度 | **52U**（超标准 42U/48U） |
| 服务器节点 | 12 × **G4826Z5** 4U AI 服务器 |
| GPU | 每节点 8 × **AMD Instinct MI355X** = **96 GPU/rack** |
| CPU | 每节点 2 × AMD EPYC 9xx5 |
| 液冷 CDU | **Nidec** 200kW 液冷分配单元 |
| 网络交换 | **Broadcom Tomahawk 5** 800GbE |
| 存储 | 每节点 8 × U.2 SSD |
| 密度对比 | 比标准空冷配置**提升 50% 密度** |

> **解读**: MiTAC 作为台湾头部服务器厂商（整合 Tyan + Intel 服务器业务），采用 52U 非标高度直接在空间利用率上超越行业惯例。200kW Nidec CDU + Tomahawk 5 800GbE 交换的搭配，表明 AI 整机柜正从"拼 GPU 数量"转向"拼系统集成效率"——整机柜作为 turnkey 产品交付，客户开箱即可用。

**同时展示**: MiTAC 还展出了 **48U OCP ORv3 合规 HPC 液冷机柜**，搭配 C2811Z5 2U AMD EPYC 9555 计算节点（3TB mem/node）和 LE2S01 "Lake Erie" 36×3.5" 存储节点，采用 **250kW Nidec CDU**、Murata 电源架。

---

### 🔴 HPE Cray GX5000 — AMD EPYC Venice 81,920 核/机柜 CPU 超节点

> **来源**: ServeTheHome, Patrick Kennedy, June 17, 2026
> **链接**: https://www.servethehome.com/81920-cores-per-rack-with-amd-epyc-venice-at-hpe-discover-2026/

**核心规格**:

| 参数 | 详情 |
|:-----|:------|
| 计算刀片 | **HPE Cray GX250a** Compute Blade |
| CPU | 每 blade **8 × AMD EPYC Venice**（256 核/Core） |
| 机柜密度 | 36-40 blades/rack = **81,920 CPU 核/rack** |
| 液冷设计 | 全部组件液冷：CPU 冷板（6螺丝固定点）+ **DIMM 液冷**（MRDIMM）+ **Samsung E1.S SSD 冷板（顶置）** |
| 互联 | **Slingshot 400** 双 NIC/节点（未来 Slingshot 800） |
| CDU | **1.6MW** CDU |
| 内存 | 每 blade 16 通道/CPU（全部液冷） |
| 功耗评估 | SP7 Venice 700-1400W/颗 → **单 blade 5.6-11.2kW** → **单 rack 250-320kW** |
| 部署 | Los Alamos **Mission** 超算（与 NVIDIA 合作） |

**技术细节**:
- 电源通过中央母线供电（类似 ORv3 但实现方式不同）
- 侧边热/冷却接口配对液冷回路
- 刀片前端有 **Vanover VP1-01** 标注，表明是真实工作系统而非静态展示
- 侧边模块包含 Slingshot 400 NIC，使用类似 OCP NIC 3.0 的连接器

> **解读**: 这是 AMD EPYC Venice 在液冷超算领域的首次批量亮相。较之 2025年11月 SC25 的原型展示（ropped off），HPE 在 HPE Discover 2026 上展示了可工作系统。评论指出每个刀片功耗 5.6-11.2kW、整机柜 250-320kW 的热设计意味着该机柜需液冷方案强制配套。

---

## 🧊 液冷散热新技术

### 🟡 MiTAC Diamond Cooling — 人造金刚石散热进入服务器

> **来源**: ServeTheHome, Ryan Smith, June 21, 2026
> **链接**: https://www.servethehome.com/mitac-computex-2026-booth-tour/2/

**核心信息**:

| 参数 | 详情 |
|:-----|:------|
| 技术供应商 | **Akash Systems** — "Diamond Cooling" |
| 原理 | **合成金刚石**（结构化碳）作为导热介质，利用金刚石远超铜的热导率 |
| 搭载服务器 | MiTAC **G8825Z5**（8U, 8 × MI350X GPU, 双路 AMD） |
| 性能宣称 | **95°F (35°C)** 进风温度下**不降频运行** |
| 对比效益 | 数据中心可提升进风温度 → 减少冷却能耗 → 提高整体能效 |
| 电源 | 系统搭载 **13.2kW** PSU |
| 扩展 | 8 × HHHL PCIe Gen5 + 4 × FHHL PCIe Gen5 + 8 × U.2 |

> **解读**: Diamond Cooling 的本质是通过替换导热界面材料（TIM）来提升散热效率。金刚石热导率（~2000 W/mK）远超铜（~400 W/mK），理论上可显著降低芯片到冷板的温差。但 MiTAC 未在 Computex 现场打开机箱展示实物，**需第三方验证**。如果该技术验证有效，对液冷和空冷场景都有影响——液冷可降低泵功率或提高冷却液温度，空冷则可提升进风温度阈值。
>
> **局限判断**: 金刚石散热主要影响导热介质（TIM），不改变基础散热架构（冷板/风冷散热器的排热能力），因此更可能作为传统散热的**增量增强**而非颠覆性方案。

---

### 🟡 HPE Cray GX5000 全组件液冷设计

见上方服务器形态章节。关键散热细节：
- **CPU 冷板**: 6 螺丝固定点，AMD EPYC Venice 专用冷板
- **DIMM 液冷**: 全部 DIMM（MRDIMM 格式）被液冷覆盖
- **SSD 冷板**: Samsung E1.S SSD 顶部冷板直接覆盖在 CPU 冷板上方
- **CDU**: 1.6MW（整个 GX5000 系统单一 CDU）
- **液冷喷头**: 具备标准化液冷喷嘴连接设计

> **趋势确认**: HPE Cray GX5000 展示了液冷从"GPU 专属"到"全组件覆盖"的演进路径。CPU、内存、SSD 全部液冷意味着液冷不再只是 GPU 的专属方案，而是整个机柜层级的散热基础设施。

---

## ⚡ 供电架构趋势

### 🟢 AI 数据中心供电向更高电压设计演进

> **来源**: DIGITIMES Asia 头条新闻, 2026-06-22 发布
> **链接**: DIGITIMES 主页（付费内容，仅摘要可用）

据 DIGITIMES 报道，"Surging AI power demand pushes data centers toward higher-voltage designs"。AI 数据中心电力需求激增正在推动供电架构向更高电压（800V HVDC 等）演进。该趋势与此前 2026-06-16 数据中心跟踪中记录的 NVIDIA/Google 首批 800V HVDC 采用者、TI GaN 推动 800V 架构等动态相呼应。

> **判断**: 供电架构高压化正在从早期采用阶段进入主流讨论，DIGITIMES 作为供应链权威媒体的头条报道，标志着该趋势已引起产业界广泛关注。

---

## 📋 本周完整回顾（第7波 vs 第6波）

| 维度 | 第6波（06-17） | 第7波（06-22） | 演进判断 |
|:-----|:---------------|:---------------|:---------|
| **整机柜** | Tensordyne Napier 52RU/120kW/空冷 | MiTAC 52U/200kW/液冷 + 48U ORv3 | 52U 非标高度成新趋势 |
| **GPU 密度** | Tensordyne TDN72 72加速器 | MiTAC 96×MI355X/rack | GPU 密度持续竞争 |
| **CPU 密度** | HPE Helios + AMD | HPE Cray GX5000 81,920核 | Venice 液冷超算首秀 |
| **液冷技术** | Frore LiquidJet, Noctua AIO | Diamond Cooling 金刚石+全组件液冷 | 材料创新+覆盖范围扩大 |
| **供电架构** | 800V HVDC 首批采用 | DIGITIMES 头版报道高压趋势 | 从早期采用→主流议题 |
| **空冷空间** | Tensordyne 120kW 空冷 | Diamond Cooling 提升空冷进风阈值 | 空冷仍具差异化空间 |

---

## 📚 专题交叉引用

- 超节点专题: 参见 [`supernode/2026-06-17.md`](../../01_survey/bmc-system/2026-06-17.md)（HPE Helios）
- 电源架构: 参见 [`data-center/2026-06-16.md`](../../01_survey/bmc-system/2026-06-16.md)（800V HVDC首批采用者）
- 上一期跟踪: 参见 [`2026-06-17-form-factor-cooling.md`](2026-06-17-form-factor-cooling.md)
