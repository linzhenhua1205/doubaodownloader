# RISC-V CPU 的市场机会与出路：Agentic AI、边缘 AI 与 CPU Rack 三线分析

> 元信息: v1.0 | 状态: 深度分析 | 覆盖范围: RISC-V 服务器/边缘 CPU 市场机会、Agentic AI 工作负载特性、CPU Rack 密度竞赛、竞争格局
> 适用范围: 服务器/AI 基础设施技术决策、芯片方向研判、产品路线规划
> 日期: 2026-08-21

## 目录

1. [核心判断（TL;DR）](#1-核心判断tldr)
2. [背景：CPU 为何重新成为稀缺资源](#2-背景cpu-为何重新成为稀缺资源)
3. [机会线一：Agentic AI —— 多核与高内存带宽的重新定价](#3-机会线一agentic-ai--多核与高内存带宽的重新定价)
4. [机会线二：边缘 AI —— 出货量主场与控制面渗透](#4-机会线二边缘-ai--出货量主场与控制面渗透)
5. [机会线三：CPU Rack —— 密度竞赛与 Agent 执行平面](#5-机会线三cpu-rack--密度竞赛与-agent-执行平面)
6. [RISC-V 的出路：三线机会 × 竞争位势的综合判断](#6-risc-v-的出路三线机会--竞争位势的综合判断)
7. [参考文献](#7-参考文献)

---

## 1. 核心判断（TL;DR）

**RISC-V CPU 的市场机会不在"替代 x86 的通用计算"，而在 AI 重塑 CPU 价值主张的三个新窗口里卡位。** 2025-2026 年，Agentic AI 把服务器 CPU 从"GPU 的陪衬"重新变成稀缺资源，行业出现了 Meta 抢购数千万 Arm 核、Arm 下场卖整片 CPU 这类标志性事件[来源: STH 2026-04-24]。RISC-V 若能抓住三个窗口，可绕开与 x86 正面硬刚的劣势，在增量市场建立生态位：

| 机会线 | 需求本质 | RISC-V 当前卡位 | 窗口判断 | 风险等级 |
|:-------|:---------|:---------------|:---------|:--------:|
| **Agentic AI** | 多核 × 高内存带宽的确定性执行平面 | SiFive 加入 NVLink Fusion（直连 NVIDIA GPU）[来源: STH 2026-01-15]、Ventana 192 核 chiplet | 2026-2028，Vera Rubin 平台周期 | 中（性能/软件栈差距） |
| **边缘 AI** | 低功耗 × 向量/矩阵 × 极致成本 | SiFive Intelligence 系列、Untether/Esperanto 千核加速器；NVIDIA ConnectX-8 数据路径加速器已用 RISC-V[来源: STH 2025-09-08] | 已发生，出货量主场 | 低（生态位已占） |
| **CPU Rack** | 每机柜核数/内存带宽密度的极限竞赛 | 尚无产品落地，需借 NVLink/CXL/UCIe 生态进入 | 2027+，跟随 Arm AGI CPU 节奏 | 高（需要软件栈成熟） |

**三个窗口的共同逻辑**：Agentic AI 带来的净新增工作负载（Agent 框架、工具调用、确定性脚本执行、机器对机器流量）没有 x86 历史包袱，性能敏感度低于传统 HPC/数据库，而定制化、功耗、成本敏感度更高——这正是开放 ISA 的 RISC-V 相对封闭 x86 的差异化优势区间。

**关键量化锚点**（全文展开）：
- Agentic 工作负载的**每核内存带宽甜点 = 4-6 GB/s**（Arm 在 AGI CPU 上定义，12 通道 DDR5-8800 支撑 136 核）[来源: STH 2026-03-24]
- 单机柜密度基准：风冷 8,848 核/柜（AMD EPYC 9965，<32kW）[来源: STH 2026-06-19]；液冷 >80,000 核/柜（HPE Cray GX5000）[来源: STH 2026-06-19]
- 内存带宽代际跃迁：12ch DDR5-4800 较 8ch DDR4-3200 提升 2.25x；16ch DDR5-12800 较 12ch DDR5-6400 提升 2.67x[来源: STH 2026-06-19 引用数据，计算见 §3.2]

---

## 2. 背景：CPU 为何重新成为稀缺资源

### 2.1 需求信号：AI bot 流量超过人类流量

Cloudflare CEO Matthew Prince 于 2026-06-03 公开表示：**AI bot 流量已超过互联网人类流量**[来源: STH 2026-06-19 转述 Cloudflare Radar]。这一数据点意味着两层含义：

1. **存量基础设施被压垮**：现有服务器/应用是为约 80 亿人设计的；Agent 成为第二类"用户"后，web 服务器、数据库、ERP 系统承受的请求量结构性上升。STH 读者实测：原本 8 核 VM 日常 15%、季末 70% 利用率，如今持续打满 100%[来源: STH 2026-06-19]。
2. **净新增工作负载出现**：Agent 框架本身（OpenClaw/Hermes 等）运行在 CPU 而非 GPU 上，需要"保持存活、随时响应"[来源: STH 2026-06-19]。

### 2.2 供给信号：CPU Land Grab 正式开打

2026 年 4 月，**Meta 向 AWS 采购"数千万" Graviton 核**（AWS 托管，含电力/网络/基础设施），且几周前刚宣布成为 Arm AGI CPU 首发客户[来源: STH 2026-04-24]。STH 将其定性为 "The CPU Land Grab is Officially On"——大厂不再只抢 GPU，开始锁 CPU 资源。

同步发生的结构事件：
- **Arm 下场卖整片 CPU**（2026-03-24，AGI CPU 发布）：Arm 从纯 IP 商变成硅片供应商，客户名单含 Meta、OpenAI、Cloudflare、SAP，联想/ASRock Rack/QCT/Supermicro 出货[来源: STH 2026-03-24]。Arm 直接对标 AMD EPYC 而非 Intel Xeon——竞争参照系的转变。
- **x86 侧密度军备竞赛**：AMD EPYC 9965（192 核/插槽）、Intel Xeon 6 16 通道 MRDIMM 平台，全部指向"每机柜更多核 + 更多内存带宽"。

### 2.3 竞争格局：x86 / Arm / RISC-V 三方的生态位

| 维度 | x86 (Intel/AMD) | Arm (AWS Graviton/Ampere/Arm AGI) | RISC-V (Ventana/SiFive/中国生态) |
|:-----|:----------------|:----------------------------------|:----------------------------------|
| 软件栈 | 最成熟，历史包袱重 | 成熟度追赶中，Linux 生态已通 | 刚过 RVA23 门槛，Debian 2023 年列为官方架构 |
| 定制自由度 | 封闭 ISA | 架构授权门槛高 | **开放 ISA，任意定制，无授权费** |
| 每核性能 | 领先（Zen 5c 等） | Neoverse V3 接近 | 落后 1-2 代（对标 Neoverse N2 级） |
| 功耗/核密度 | 落后 | 领先 | 潜在领先（面积/功耗优势） |
| AI 生态 | CUDA 之外阵营 | NVLink Fusion 成员 | **2026-01 起 NVLink Fusion 成员** |

> RISC-V 的处境：性能落后但自由度最高。关键问题是——**AI 时代哪些工作负载"性能不那么重要，而自由度/功耗/成本重要"？** 本文三线机会正是对这一问题的回答。

---

## 3. 机会线一：Agentic AI —— 多核与高内存带宽的重新定价

### 3.1 Agentic AI 为什么是 CPU 故事（而非纯 GPU 故事）

STH 对 Agentic AI 基础设施的框架拆解[来源: STH 2026-06-19]：

```
+-----------------------------------------------------------------+
| LLM inference (probabilistic, runs on GPU/API)                  |
|     | LLM generates scripts / formatted calls                   |
|     v                                                           |
| Agent frameworks (OpenClaw/Hermes, run on CPU)                  |
|     | tool calls: SSH/API/script exec (deterministic, on CPU)   |
|     v                                                           |
| Legacy apps (web servers / DB / ERP, run on CPU)                |
|     v                                                           |
| KV Cache / memory pool (CXL expansion, BW-sensitive)            |
+-----------------------------------------------------------------+
```

关键机制：
1. **LLM 负责"生成"，CPU 负责"执行"**。要获得确定性、可复现的结果，正确做法是让 LLM 生成脚本/结构化调用，由 CPU 侧工具确定性执行——"把概率性 LLM 工作转移到确定性 CPU 工作流"[来源: STH 2026-06-19]。
2. **工具调用是净新增的 CPU 负载**。实测数据：即便最新模型，仍有约 25% 的 SSH 工作流因引号/格式错误循环修复，烧掉大量 token 和 CPU 时间[来源: STH 2026-06-19]。
3. **存量应用被 Agent 流量放大**：Agent 请求打到前端应用 → 数据库 → 存储 → 网络，全链路都是 CPU 节点。STH 结论：Agentic AI 的 CPU 需求 = 净新增 Agent 负载 + 存量应用负载放大，两条腿[来源: STH 2026-06-19]。

### 3.2 量化基准：Agentic CPU 的两个关键维度

**维度 A：每核内存带宽（关键新指标）**

Arm 在 AGI CPU 发布时给出明确量化判断：**每核 4-6 GB/s 内存带宽是 agentic 工作负载的甜点**[来源: STH 2026-03-24]。推导：
- Arm AGI CPU：136 核 × 2MB L2/核，12 通道 DDR5-8800（理论 ~1,689 GB/s ÷ 136 核 ≈ 12.4 GB/s/核理论值；Arm 指有效可达带宽口径）
- 对照 STH 的 STREAM 分析：内存带宽 ≈ 通道数 × 每通道速率，Agentic 的 in-memory 数据库/工具调用/HPC 类子负载高度带宽敏感[来源: STH 2026-06-19]

**维度 B：内存带宽代际跃迁（单位：GB/s，理论值）**

| 平台 | 配置 | 理论带宽 | 相对基线 |
|:-----|:-----|:--------:|:--------:|
| AMD Milan | 8ch DDR4-3200 | 204.8 | 1.00x |
| AMD Genoa | 12ch DDR5-4800 | 460.8 | **2.25x** |
| 主流现状 | 12ch DDR5-6400 | 614.4 | 1.00x（新基线） |
| 下一代 | 16ch DDR5-8000 | 1024.0 | **1.67x** |
| 下一代+ | 16ch DDR5-12800 (MRDIMM) | 1638.4 | **2.67x** |

> 计算：DDR 单通道带宽 = MT/s × 8 B/transfer；Milan = 3200×8×8；Genoa = 4800×8×12；比例 2.25x 与 STH 引用一致[来源: STH 2026-06-19 配置数据，本文核算]。结论：**未来 2-3 代 CPU 的内存带宽红利将主要由通道数（12→16）和 MRDIMM（DDR5-8000→12800）驱动**，这利好所有 ISA——但 RISC-V 的 chiplet 架构在通道扩展上有后发优势。

**维度 C：核心密度（CPU Rack 视角，见 §5）**

### 3.3 RISC-V 的对应打法：三个结构性动作

**动作 1：SiFive 加入 NVLink Fusion（2026-01-15）——打通 AI 系统的"入场券"**

NVIDIA 的 NVLink Fusion 生态（IP 授权 + 外部 chiplet，支持 NVLink-C2C 全缓存一致性连接）此前已有 Arm、Intel、AWS 加入；SiFive 是**第一家 RISC-V 厂商**[来源: STH 2026-01-15]。意义：
- RISC-V CPU 可直连 NVIDIA GPU（NVLink-C2C 而非 PCIe），进入 Grace/Vera 式高集成 AI 系统
- 时间线指向 Vera Rubin 平台（NVLink 6 代际）
- 叠加 NVIDIA 此前宣布把 CUDA 与驱动带到 RISC-V——**RISC-V 第一次获得进入主流 AI 加速器生态的软件+硬件双通道**[来源: STH 2026-01-15]

**动作 2：Ventana Veyron V2 的 chiplet + DSA 战略（2023-11 发布，前瞻布局）**

- 192 核/插槽：6 × 32 核 chiplet + I/O hub，UCIe 互联[来源: STH 2023-11-07]
- 32 核 cluster：512KB I-cache / 128KB D-cache / 1MB L2，最高 128MB L3[来源: STH 2023-11-07]
- 支持 RVA23（含向量扩展）、AMBA CHI、RAS（ECC/数据中毒）、Secure Boot、IOMMU[来源: STH 2023-11-07]
- 核心战略不是"比 x86 快 5%"，而是**DSA（域特定加速）chiplet 集成**——存储/压缩/CDN 转码加速器直接上封装，改变性能曲线；商业模式可向超大规模客户开放定制[来源: STH 2023-11-07]
- 参考形态：1U 单插槽 192 核服务器，12 通道 DDR5-5600[来源: STH 2023-11-07]

**动作 3：计算内存（NDP）——RISC-V 在 CXL 侧的独特生态位**

XCENA MX1（2025-08 展示，Q4 量产）：PCIe Gen6 的 CXL 3 内存设备，集成"数千个" RISC-V 核，DDR5-8400 控制器，单卡最高 1TB（256GB DIMM × 4）[来源: STH 2025-08-24]。理念：**把计算搬到内存旁，保留内存带宽，offload 任务无需把数据搬回主 CPU**——与 Marvell Structera A（16 Arm 核）同类，但 RISC-V 核数高出两个数量级。这与知识库中 [Plora 池化内存 NDP](../03_server/2026-08-10-plora-pooled-memory-ndp-deep-analysis.md) 的分析方向一致：内存侧计算是 AI 时代的确定性增量。

### 3.4 机会评估

| 评估项 | 结论 |
|:-------|:-----|
| 市场规模 | 大：Agentic CPU 需求双轮驱动（净新增 + 存量放大），Meta 级客户已锁资源 |
| RISC-V 切入难度 | 中高：需要性能接近 Neoverse V3/Zen 5c 的核 + 完整软件栈 + NVLink/CXL 生态位 |
| 差异化空间 | 高：确定性执行负载对单线程性能敏感度低于传统 HPC，对功耗/定制/成本敏感 |
| 窗口期 | 2026-2028：Vera Rubin 周期 + Arm AGI CPU 2026 底量产验证市场需求 |
| 结论 | **主战场，但需要"借道"（NVLink/UCIe/CXL）而非正面硬刚** |

---

## 4. 机会线二：边缘 AI —— 出货量主场与控制面渗透

### 4.1 边缘 AI 的需求特征

边缘 AI 的负载画像与数据中心相反：功耗受限（几瓦到几十瓦）、成本极度敏感、推理模型规模小（1B-13B 级）、强调 TOPS/W 而非绝对性能。这正是 RISC-V 的传统优势区间——嵌入式/物联网出货量是 RISC-V 的基本盘（RISC-V International 公布的累计出货量 2022 年达 100 亿颗量级[来源: RISC-V International 公开数据]），边缘 AI 是这一基本盘的自然升级。

### 4.2 RISC-V 边缘 AI 供给生态

**SiFive Intelligence 第 2 代家族（2025-09-08）**[来源: STH 2025-09-08]：

| 型号 | 定位 | 关键特性 |
|:-----|:-----|:---------|
| X100 | 低功耗控制核 | 32/64 位，加速器控制单元（从宿主 CPU offload 控制任务） |
| X280 | 标量性能 | RVA23 支持（统一 64 位指令基线，软件兼容关键一步） |
| X390 | 高性能标量 | 家族中最高性能标量核 |
| XM | 矩阵引擎 | 4×X300 + 大矩阵引擎，可组大 AI 加速器 |

技术细节：SSCI（标量协处理器接口，自定义指令驱动加速器）与 VCIX（向量协处理器接口，高带宽访问向量寄存器）；指数函数从 15-22 条指令压缩到 1 条；可配置 VLDQ 隐藏已知负载的内存延迟[来源: STH 2025-09-08]。

**历史先例（千核 RISC-V AI 加速器）**：
- Untether.AI Boqueria：1,458 个 RISC-V 核的低功耗 AI 推理加速器（Hot Chips 34，2022）[来源: STH 2022-08-23]
- Esperanto ET-SoC-1：1,092 个 RISC-V 核（Hot Chips 33，2021）[来源: STH 2021]

**中国生态（开放 ISA 的政策红利区）**：XiangShan 开源高性能核（Kunminghu 对标 Neoverse N2，13 级流水线、6-wide、1MB 私有 L2、16MB 共享 L3，合作含 5nm AI 加速芯片与 7nm DPU）[来源: STH 2024-08-27]；玄铁（T-Head）C 系列在 IoT/边缘出货广泛。

### 4.3 控制面渗透：一个被低估的事实

STH 明确指出：**NVIDIA ConnectX-8 智能网卡中的数据路径加速器（DPA）基于 RISC-V**，"RISC-V 已在 NVIDIA 的许多设计中"[来源: STH 2025-09-08]。这意味着：
- RISC-V 已进入全球最大 AI 基础设施厂商的核心器件内部（控制面/数据面辅助计算）
- 与 §3.3 的 NVLink Fusion 形成互补：**RISC-V 先在 NVIDIA 生态内部扎根（DPA/控制面），再向外部主机 CPU 扩展（NVLink-C2C）**——渗透路径清晰

### 4.4 机会评估

| 评估项 | 结论 |
|:-------|:-----|
| 市场规模 | 大且确定：边缘/IoT 是 RISC-V 出货量主场，AI 化升级是确定性增量 |
| RISC-V 切入难度 | 低：生态位已占（控制面/低功耗推理），无需挑战 x86 |
| 差异化空间 | 高：开放 ISA 可做领域专用扩展（向量/矩阵/自定义指令），无授权费 |
| 窗口期 | 正在进行时 |
| 结论 | **基本盘 + 现金流来源，保证 RISC-V 生态"活着"并反哺服务器线** |

---

## 5. 机会线三：CPU Rack —— 密度竞赛与 Agent 执行平面

### 5.1 CPU Rack 是什么：为什么现在出现

CPU Rack（纯 CPU 高密度机柜）是 2026 年出现的新形态：**以整柜为单位部署纯 CPU 算力，专门承载 Agent 执行平面**（Agent 框架、工具调用、沙箱、确定性工作流、Bot 流量处理）。驱动因素[来源: STH 2026-06-19]：
- Cloudflare 数据：AI bot 流量 > 人类流量，web 服务器/应用层 CPU 需求暴涨
- 沙箱化执行：短生命周期 sandbox（创建→执行命令→销毁）成为 Agent 标准操作，天然适合 CPU 池
- 许可证经济学：Oracle/SQL Server 等按核授权，Agent 流量放大后催生"为 Agentic 时代优化授权"的新生意
- 确定性优先：LLM 生成脚本 + CPU 确定性执行（§3.1 机制）意味着执行平面规模与 LLM 推理规模解耦

### 5.2 密度量化基准（2026 年实态）

| 方案 | 形态 | 核数 | 内存 | 功率 | 来源 |
|:-----|:-----|:----:|:-----|:-----|:-----|
| Dell PowerEdge R7725 (2P EPYC 9965) | 2U 双路 ×22 节点/48U 柜 | **8,848 核 / 16,896 线程** | 高带宽 DDR5 | <30-32kW 风冷 | [STH 2026-06-19] |
| HPE Cray GX5000 (液冷) | 液冷整柜 | **>80,000 核/柜** | — | 液冷 100kW+ | [STH 2026-06-19] |
| Arm AGI CPU 参考 | 单插槽多节点，ORv3 36kW 风冷 | **>8,000 核/柜** | 12ch DDR5-8800 | 36kW 风冷 | [STH 2026-03-24] |
| Graviton5 (Meta 采购) | 192 核 V3 单插槽 | 数千万核级采购 | 600MB 缓存总量/片 | — | [STH 2026-04-24] |

密度逻辑：**单插槽核数 × 节点密度 × 机柜功率预算**。x86/Arm 通过 192 核级单插槽 + 液冷把单柜推到 8 万核；内存带宽随通道数/速率同步上涨（§3.2）。

### 5.3 RISC-V 进入 CPU Rack 的路径与障碍

**路径（按确定性排序）**：
1. **CXL 计算内存卡**（XCENA 路线）：RISC-V 核以 CXL 设备形式进入现有 CPU Rack，无需主机侧换 ISA——2025 Q4 已量产[来源: STH 2025-08-24]
2. **NVLink Fusion 主机 CPU**（SiFive 路线）：RISC-V CPU 作为 AI 服务器主机 CPU 进入系统，Vera Rubin 周期（2027+）[来源: STH 2026-01-15]
3. **全 RISC-V CPU Rack**（Ventana 路线）：192 核 chiplet CPU 独立组柜，需软件栈（RVA23/RISE/发行版）成熟，2026-2027 尚无产品落地[来源: STH 2023-11-07 前瞻]

**障碍**：
- **性能差距**：RISC-V 高性能核仍对标 Neoverse N2 级（XiangShan Kunminghu[来源: STH 2024-08-27]），而 Agentic CPU Rack 的基准已抬到 Neoverse V3/Zen 5c 级（Graviton5 192 核 V3[来源: STH 2026-04-24]）
- **软件栈**：RVA23 是"第一步"，但 RISE/发行版/容器生态成熟还需 1-2 年
- **单核性能**：Agentic 负载存在大量单线程受限子负载（STH 明确指出"[整 CPU 跑反而更慢]因完全单线程受限"[来源: STH 2026-06-19]），这是 RISC-V 的相对弱项

### 5.4 机会评估

| 评估项 | 结论 |
|:-------|:-----|
| 市场规模 | 大且新增：CPU Rack 是 2026 年新形态，无存量锁定 |
| RISC-V 切入难度 | 高：性能 + 软件栈 + 系统生态三重门槛 |
| 差异化空间 | 中：核密度是 RISC-V 可追的方向（chiplet 天然适配），但单核性能拖后腿 |
| 窗口期 | 2027+：Arm AGI CPU 2026 底量产验证市场后，RISC-V 跟进 |
| 结论 | **远期主战场，近期以"借道"（CXL/NVLink 设备形态）先渗透** |

---

## 6. RISC-V 的出路：三线机会 × 竞争位势的综合判断

### 6.1 三线机会 × 竞争位势矩阵

```
                Opportunity certainty (market demand validated)
                     high <-------------> low
  high |  2 Edge AI (control plane/infer)   1 Agentic AI (via NVLink)
compete|  - already inside NVIDIA DPA         - needs SiFive NVLink + CUDA
posture|  - volume home turf                  - Ventana DSA chiplet differ
  low  |  - XCENA CXL mem-compute (bridgehead) 3 CPU Rack (standalone rack)
       |                                          - perf/software highest bar
```

**排序**：近期变现能力 ② > ① > ③；长期天花板 ③ > ① > ②。**理性路径是"②养生态、①抢身位、③等窗口"**——用边缘 AI 的现金流与出货量维持生态，用 NVLink/CXL 借道切入 Agentic 数据中心，再在 CPU Rack 成熟时以整柜形态正面竞争。

### 6.2 关键成功要素（按优先级）

1. **单核性能追平 Neoverse V3 级**：Condor Cuzco 的 TBM（时间基微架构，硬件编译指令排序，目标 2x AX65 IPC）[来源: STH 2025-08-25] 与 XiangShan 迭代是两条值得跟踪的技术路线；性能是 RISC-V 一切的瓶颈
2. **软件栈走完"最后 20%"**：RVA23 已解决基线指令统一[来源: STH 2025-09-08]，但发行版/容器/编排/可观测性（OpenBMC/Redfish 侧）仍需 RISE 等联盟推进
3. **生态位纪律**：不追通用 x86 替代叙事，聚焦"确定性执行 + 定制化 + 功耗/成本敏感"的 AI 增量负载
4. **互联入场券**：NVLink Fusion（NVIDIA 生态）、UCIe（chiplet 生态）、CXL（内存生态）三条都要占位——SiFive 已占其一，Ventana 占其二，CXL 侧 XCENA 已量产

### 6.3 时间窗口判断

| 时间 | 事件 | 对 RISC-V 的意义 |
|:-----|:-----|:----------------|
| 2025 Q4 | XCENA MX1 量产 | CXL 计算内存桥头堡落地 |
| 2026-01 | SiFive 加入 NVLink Fusion | 数据中心入场券（软件+硬件） |
| 2026 底 | Arm AGI CPU 量产 | 验证 Agentic CPU 市场，为 RISC-V 探路 |
| 2027 | Vera Rubin 平台周期 | NVLink 6 代际，SiFive NVLink CPU 的窗口 |
| 2027-2028 | RVA23 生态成熟 + 高性能核量产 | 全 RISC-V CPU Rack 首次具备条件 |

### 6.4 对技术决策者的启示（本知识库语境）

1. **跟踪信号清单**：SiFive NVLink CPU 落地产品、Ventana Veyron V3 发布、Condor Cuzco 流片、XCENA MX1S（2026 双 PCIe Gen6 x8 版）[来源: STH 2025-08-24]、RVA23 认证核数量
2. **与知识库已有分析的衔接**：内存带宽敏感负载分析可参考 [HMA 异构内存分解](../03_server/2026-08-10-hma-serve-heterogeneous-memory-disaggregation-deep-analysis.md)；Agentic 基础设施叙事参考 [Agentic AIOps 2026](../04_ai/2026-08-07-agentic-aiops-2026-narrative-deep-analysis.md)；chiplet/scale-up 拓扑参考 [NUNA 多 die scale-up](../03_server/2026-08-10-nuna-multi-die-scaleup-topology-deep-analysis.md)
3. **判断立场**：RISC-V 服务器 CPU 在 2026 年仍是"生态位玩家"而非"主流替代"，但 Agentic AI + NVLink/CXL 借道使其 2027-2028 出现真实放量的概率显著高于 2024 年共识。**对服务器产品规划的意义：CXL 计算内存、NVLink 主机 CPU 兼容性、双 ISA 主板预留，是低成本可先行的布局点。**

---

## 7. 参考文献

[1] Patrick Kennedy, "Building a Dense Agentic AI CPU Rack Today", ServeTheHome, 2026-06-19. https://www.servethehome.com/building-a-dense-agentic-ai-cpu-rack-amd-dell-today/

[2] Ryan Smith, "SiFive To Adopt NVLink Fusion For Future Data Center RISC-V CPU Designs", ServeTheHome, 2026-01-15. https://www.servethehome.com/sifive-to-adopt-nvlink-fusion-for-future-data-center-risc-v-cpu-designs/

[3] Patrick Kennedy, "Arm AGI CPU Launched Establishing Arm as a Silicon Provider", ServeTheHome, 2026-03-24. https://www.servethehome.com/arm-agi-cpu-launched-establishing-arm-as-a-silicon-provider/

[4] Patrick Kennedy, "Meta Buys Tens of Millions of AWS Graviton Arm Cores in a CPU Land Grab", ServeTheHome, 2026-04-24. https://www.servethehome.com/meta-buys-tens-of-millions-of-aws-graviton-arm-cores-in-a-cpu-land-grab/

[5] Cliff Robinson, "XCENA MX1 RISC-V Computational Memory in CXL 3.0", ServeTheHome, 2025-08-24. https://www.servethehome.com/xcena-mx1-risc-v-computational-memory-in-cxl-3-0/

[6] Ryan Smith, "Condor Computing's Cuzco, a High-Perf RISC-V Design at Hot Chip 2025", ServeTheHome, 2025-08-25. https://www.servethehome.com/condor-computings-cuzco-a-high-perf-risc-v-design-at-hot-chip-2025/

[7] John Lee, "SiFive 2nd Gen Intelligence Family Launched", ServeTheHome, 2025-09-08. https://www.servethehome.com/sifive-2nd-gen-intelligence-family-launched/

[8] Patrick Kennedy, "Ventana Veyron V2 RISC-V CPU Launched for the DSA Future", ServeTheHome, 2023-11-07. https://www.servethehome.com/ventana-veyron-v2-risc-v-cpu-launched-for-the-dsa-future/

[9] Patrick Kennedy, "XiangShan High-Performance RISC-V Processors at Hot Chips 2024", ServeTheHome, 2024-08-27. https://www.servethehome.com/xiangshan-high-performance-risc-v-processors-at-hot-chips-2024/

[10] Cliff Robinson, "Untether.AI Boqueria 1458 RISC-V Core AI Accelerator", ServeTheHome, 2022-08-23. https://www.servethehome.com/untether-ai-boqueria-1458-risc-v-core-ai-accelerator-hc34/

[11] RISC-V International, "About RISC-V". https://riscv.org/about/

---

## 变更记录

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-21 | v1.0 | 首次创建。基于 STH 2025-2026 系列报道 + RISC-V International 公开数据，分析 RISC-V CPU 在 Agentic AI / 边缘 AI / CPU Rack 三条线的市场机会与出路 |
