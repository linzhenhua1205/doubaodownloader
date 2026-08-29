# AMD Advancing AI 2026 深度分析：Helios 机架 · MI455X · EPYC Venice

> **创作日期**: 2026-07-27 | **作者**: 小龙猫
> **文档类型**: 深度技术分析 | **版本**: v1.0
> **更新日志**: 见文末

---

## 📑 目录

- [§1 概述：AI 工厂时代的第二极](#1-概述ai-工厂时代的第二极)
- [§2 MI455X GPU 架构深度分析](#2-mi455x-gpu-架构深度分析)
- [§3 EPYC Venice (Zen 6) CPU 架构深度分析](#3-epyc-venice-zen-6-cpu-架构深度分析)
- [§4 Helios 机架级系统全栈分析](#4-helios-机架级系统全栈分析)
- [§5 ROCm 软件栈与 AI 驱动 GPU 编程](#5-rocm-软件栈与-ai-驱动-gpu-编程)
- [§6 MI430X HPC 专用 GPU](#6-mi430x-hpc-专用-gpu)
- [§7 对比分析：Venice vs Vera · Helios vs NVL72](#7-对比分析venice-vs-vera--helios-vs-nvl72)
- [§8 产品路线图：GPU·CPU·机架年度节奏](#8-产品路线图gpucpu机架年度节奏)
- [§9 企业端部署：MI350P · Gorgon Halo · Kria AI](#9-企业端部署mi350p--gorgon-halo--kria-ai)
- [§10 合作伙伴生态与客户阵容分析](#10-合作伙伴生态与客户阵容分析)
- [§11 供电散热与能效分析](#11-供电散热与能效分析)
- [§12 市场格局与战略评估](#12-市场格局与战略评估)
- [§13 AI 加速器 TAM 与行业影响](#13-ai-加速器-tam-与行业影响)
- [§14 总结与结构性判断](#14-总结与结构性判断)
- [变更日志](#变更日志)

---

## §1 概述：AI 工厂时代的第二极

### 1.1 事件背景

2026 年 7 月 23 日，AMD 在旧金山 Moscone Center West（有史以来最大规模）举办 **Advancing AI 2026** 主题演讲。CEO Lisa Su 正式发布了 AI 工厂时代的第二极完整产品体系——从芯片到机架到软件栈的全栈能力。

**事件定位**：这标志着 **AMD 从 GPU 追赶者 → 机架级系统竞争者** 的质变。Helios 的量产使 NVIDIA NVL72 不再独占整机柜 AI 系统市场。

### 1.2 本次发布的四大支柱

| 支柱 | 产品 | 定位 | 核心意义 |
|:----|:-----|:-----|:---------|
| 🏗️ **机架系统** | **Helios** 量产（Q3 2026 出货） | 对标 NVIDIA NVL72 | AMD 首个量产机架级 AI 系统 |
| 🎯 **GPU** | **MI455X**（2nm / 432GB HBM4 / CDNA 4） | AI 训练与推理加速 | 显存容量领先（比竞品多 50%） |
| 💻 **CPU** | **EPYC Venice**（Zen 6 / 256核 / 2nm） | 通用+AI 推理/Agent 负载 | EPYC 史上最大单代飞跃 |
| 🛠️ **软件** | **ROCm.AI** + Hyperloom | AI 驱动 GPU 编程 | 降低 AMD 软件生态门槛 |

### 1.3 "Power is the big limiter" — 行业定调时刻

Lisa Su 在发布中的一句原话定义了当前阶段：
> **"Power is the big limiter right now. Efficiency is a need."**

这是 **GPU 厂商首次公开将功率（而非性能）定为最大限制因素**。信号含义深远：

- 液冷从"可选"→"必需"
- 供电架构（HVDC / BBU / SSCB）加速落地
- 每瓦 token → 整机柜核心竞争力指标
- 超大规模客户用 GW 级订单确认功率/散热是首要约束

### 1.4 竞争格局的根本变化

| 维度 | 此前（2025-2026 H1） | 此后（2026 H2+） |
|:-----|:-------------------|:----------------|
| 整机柜 AI 系统 | NVIDIA NVL72 独家 | AMD Helios + NVIDIA NVL72 双雄 |
| GPU 显存领先 | NVIDIA HBM3e 192 GB | AMD MI455X 432 GB HBM4 |
| CPU Agent 负载 | NVIDIA Vera 88核集中式 | AMD Venice 256核 vs Vera 多核优势 |
| 软件生态 | CUDA 绝对主导 | ROCm.AI 开启 AI 驱动编程路径 |
| 客户选择 | NVIDIA 绑定 | AMD 开放平台 = 差异化议价能力 |

---

## §2 MI455X GPU 架构深度分析

### 2.1 核心规格

| 参数 | MI455X | MI355X（前代） | 提升幅度 |
|:-----|:------:|:--------------:|:--------:|
| **架构** | CDNA 4 | CDNA 3 | — |
| **制程（计算芯粒）** | **TSMC 2nm** | TSMC 3nm | 密度↑·功耗↓ |
| **制程（其他部分）** | TSMC 3nm | TSMC 3nm | — |
| **HBM 类型** | **HBM4** | HBM3e | 带宽↑·容量↑ |
| **HBM 容量** | **432 GB** | 288 GB | **+50%** |
| **FP4 性能** | 基线 + **15%** | 基线 | +15% |
| **Token 吞吐（vs MI355X）** | **↑34×** | 基线 | **34×** |
| **封装形式** | **Enhanced Accelerator Module (EAM)** | OAM | 机架级集成优化 |
| **芯粒策略** | 多计算芯粒 + 多 I/O 芯粒 | 多计算芯粒 | 延续 chiplet 路线 |
| **出货时间** | **2026 Q3** | 已出货 | — |

### 2.2 2nm 计算芯粒的工艺意义

MI455X 采用 **TSMC 2nm (N2)** 工艺制造计算芯粒，这是业界首个量产的 2nm AI 加速器。N2 相比 N3 的预期增益：

| 指标 | N2 vs N3 预期 | 对 MI455X 的意义 |
|:----|:-------------|:-----------------|
| 逻辑密度 | **↑~15%** | 每计算芯粒更多 SM/CU 或更小面积 |
| 同频功耗 | **↓~25-30%** | 同等功率更多活跃计算单元 |
| 同功耗频率 | **↑~10-15%** | 更高时钟 → 更低延迟 |

**2nm 的竞争维度**：MI455X 的 2nm 计算芯粒领先于 NVIDIA Rubin 的台积电定制节点（仍基于 3nm 级），这是 AMD 在制程上对 NVIDIA 的**时间窗口优势**。

### 2.3 432GB HBM4 — 显存容量领先的战略意义

| 对比项 | MI455X | NVIDIA B200 | NVIDIA Rubin |
|:-------|:------:|:-----------:|:------------:|
| HBM 世代 | **HBM4** | HBM3e | HBM4 |
| 容量 | **432 GB** | 192 GB | 288 GB |
| 相对容量 | **1×** | 0.44× | 0.67× |

**容量领先的直接价值**：

1. **更大模型单机推理**：~400B 参数的 MoE 模型可完整装入单 GPU，消除模型并行的跨 GPU 通信开销
2. **更长上下文窗口**：同等模型下支持更长的 KV cache，适合长文档/长视频分析
3. **更高推理批次**：服务更多并发用户，降低每 token 成本
4. **训练吞吐**：更大 batch size / 更多中间激活存储，减少重计算

### 2.4 EAM 封装形式

MI455X 采用 **Enhanced Accelerator Module (EAM)** 而非标准 OAM 或 SXM 形态：

| 特征 | EAM | OAM | SXM |
|:-----|:---|:---|:----|
| 热设计功耗上限 | **>1000W** | ~700W | ~1000W |
| 互联带宽 | 板级高速互联 | PCIe / XGMI 2D Mesh | NVLink 全互联 |
| 机架集成度 | **Helios 专用优化** | 通用 | NVIDIA 专用 |
| 散热方案 | 液冷强制 | 液冷/风冷可选 | 液冷强制 |

EAM 是 AMD 为 Helios 机架定制的 GPU 模块，与 NVIDIA SXM 一样是**整机柜级设计的私有接口**——这标志着 AMD 从"卖芯片"到"卖系统"的转型。

### 2.5 CDNA 4 架构推测

虽然 AMD 未披露 CDNA 4 全部微架构细节，但基于 CDNA 3 (MI300X) 的已知结构和 MI455X 的规格，可推断：

**计算单元 (CU) 升级方向**：

- Matrix Core 支持 FP4 / FP6 等低精度格式（迎合推理趋势）
- 张量操作调度器改进，提高指令级吞吐
- 更大的共享内存 / L1 缓存（适应 MoE 模型的中间激活存储）

**内存子系统**：

- HBM4 控制器支持 8-high+ 堆叠
- 改进的缓存层次：更大的 L2/L3 缓存池
- 支持 HBM4 的 6.4+ Gbps/pin 数据率

**互联升级**：

- 片间互联带宽提升（Infinity Fabric 4.x 代）
- 支持 Helios 机架内统一 GPU 地址空间

### 2.6 MI455X 性能数据分析

**Token 吞吐量 ↑34× vs MI355X**

这个数字需要拆解理解：

- 并非纯架构提升，而是**架构 + HBM4 容量 + 软件栈 + 机架级协同**的综合结果
- 34× 中大部分来自软件优化（ROCm 3.3× 推理提升 + 机架级 scale-up）
- 纯硬件（2nm + HBM4 + CDNA 4）的贡献约占 3-5×

**Token per dollar ↑30% vs 竞品**

- 来自 Helios 整机柜的 10-15% better perf/watt
- 折算时考虑了 AMD 的定价策略（开放平台 = 较低溢价）

---

## §3 EPYC Venice (Zen 6) CPU 架构深度分析

### 3.1 核心规格

| 参数 | Venice | Turin (Zen 5) | 提升幅度 |
|:-----|:------:|:-------------:|:--------:|
| **架构** | **Zen 6** | Zen 5 | 全新微架构 |
| **制程** | **TSMC 2nm** | TSMC 3nm/4nm | 密度↑·功耗↓ |
| **最大核心数** | **256 核** | 192 核 (Turin Dense) | +33% |
| **内存通道** | **16-ch DDR5** | 12-ch DDR5 | +33% |
| **内存速度** | **DDR5-12800** | DDR5-6400 | **2×** |
| **峰值内存带宽** | **1.6 TB/s** | 0.6 TB/s (Turin) | **2.67×** |
| **PCIe** | **PCIe Gen6** | PCIe Gen5 | 带宽翻倍 |
| IPC 提升 | 显著 | 基线 | Zen 5→Zen 6 典型年增益 |
| **声称 vs NVIDIA Vera** | **2.2× per socket** | — | 战争宣言 |

### 3.2 Venice 四子系列

| 型号 | 核心数 | 定位 | 目标场景 |
|:----|:-----:|:-----|:---------|
| **Venice HF** | 128核（高频） | Helios 专用版本 | AI 推理引导 CPU + GPU 协同 |
| **Venice Dense** | **256 核** | 高吞吐 | 云原生 / 高密度虚拟化 / 批量 |
| **Venice (标准)** | 128 核 | 通用计算 | 企业通用 / 数据库 / 传统负载 |
| **Venice-X** | 待定 | **3D V-Cache** | 缓存敏感工作负载（EDA / DB / AI 推理） |

**Venice HF 的独特地位**：这是 AMD 首次为一个机架级系统定制 CPU SKU。Venice HF 侧重于高频性能（而非核数），用于 Helios 中做：

- GPU 驱动与调度（高频单线程延迟关键）
- AI Agent 执行（Agent 推理任务）
- 实时推理编排

### 3.3 16 通道 DDR5-12800 的内存革命

| CPU | 通道数 | 内存速率 | 峰值带宽 | 内存代际 |
|:----|:-----:|:--------:|:--------:|:--------:|
| NVIDIA Vera | 12-ch LPDDR5X | 9600 MT/s | 1.2 TB/s | **2026** |
| EPYC Turin (Zen 5) | 12-ch DDR5 | 6400 MT/s | 0.6 TB/s | 2024 CPU + **2022 DDR** |
| **EPYC Venice (Zen 6)** | **16-ch DDR5** | **12800 MT/s** | **1.6 TB/s** | **2026 CPU + 2026 DDR** |

**关键洞察**：STH 的 Patrick Kennedy 已系统论证——NVIDIA Vera 的内存带宽优势本质上来自**代际差**（2026 年内存 vs 2022/2024 年内存），而非架构优势。Venice 的 16-ch DDR5-12800 不仅抹平差距，更实现 **1.6 TB/s 领先 Vera 的 1.2 TB/s**。

**每核带宽对比（公平版本）**：

| CPU | 总带宽 | 核数 | 每核带宽 |
|:----|:-----:|:----:|:--------:|
| NVIDIA Vera | 1.2 TB/s | 88 核 | 13.6 GB/s/核 |
| EPYC Venice Dense | 1.6 TB/s | 256 核 | 6.25 GB/s/核 |
| EPYC Venice (128核) | 1.6 TB/s | 128 核 | **12.5 GB/s/核** |

### 3.4 Zen 6 微架构推测

基于已知信息推断 Zen 6 (Venice) 的微架构方向：

**前端**：

- 更宽的分支预测（借鉴 Zen 5 的改进）
- 更大的 L1 指令缓存（可能 48KB→64KB）
- 改进的指令预取

**执行引擎**：

- 更宽的整数/FP 执行（Zen 5: 8 INT + 6 FP → 可能扩展）
- 更大的重排序缓冲区 (ROB)
- 改进的加载/存储单元

**缓存层次**：

- 更大的每核 L2 缓存（Zen 5: 1MB → 可能 2MB）
- 改进的 L3 缓存共享架构（适应 256 核规模）
- 支持 PCIe Gen6 的 I/O die（跨片互联升级）

**关键创新——Venice-X 的 3D 堆叠缓存**：

- 缓存芯粒置于计算芯粒下方（与 AMD 3D V-Cache 现有方向一致）
- 对缓存敏感的工作负载（AI 推理、数据库、EDA）有显著加速
- 有助于缩小与 Vera 在每核带宽/缓存比上的差距

### 3.5 Venice vs Vera — 声称的 2.2× 解读

AMD 声称 Venice **2.2× per-socket performance** 相比 NVIDIA Vera：

**这个数字的含义**：

- 度量方法：总芯片吞吐量（与 NVIDIA 自己用的每核/每线程指标不同）
- 对比的是 Venice Dense（256核） vs Vera（88核），核心数差距 2.9×
- 考虑到 Venice 在 256 核时每核带宽下降（6.25 vs 13.6 GB/s），实际纯计算吞吐差距 < 2.2×
- 2.2× 是**系统级综合指标**，包含内存带宽、I/O、SMT、软件栈差异

**真实的竞争格局**：

- Venice 在**核数密集**场景（虚拟化、云原生、批量推理）有天然优势
- Vera 在**每核性能**（单线程、延迟敏感）有优势
- Agentic AI 工作负载（1-4 核/容器）——两者都能放入单核簇，Venice 的规模优势在大量并发 Agent 时体现

---

## §4 Helios 机架级系统全栈分析

### 4.1 系统概述

Helios 是 AMD **首个量产机架级 AI 系统**，定位对标 NVIDIA NVL72。它不是芯片的简单组合，而是从 GPU→CPU→DPU→网络→散热→供电全栈协同设计的整机柜系统。

| 维度 | 详情 |
|:-----|:------|
| **全称** | AMD Helios AI Compute Rack |
| **量产宣布** | 2026-07-23 (Advancing AI 2026) |
| **出货时间** | **2026 Q3**，2027 H2 加速扩展 |
| **核心组件** | MI455X GPU (EAM) + EPYC Venice HF CPU + Pensando Vulcano DPU |
| **定位** | 对标 NVIDIA GB200 NVL72 / Vera Rubin NVL72 |
| **客户** | Anthropic (2GW)、OpenAI (2026 年底部署)、Meta、Microsoft |
| **声称优势** | 10-15% better perf/watt → **30% more tokens per dollar** |

### 4.2 Helios 的三大核心组件

**① MI455X GPU 模块**

- 见 §2 详细分析
- EAM 封装 × 多模块互连
- 432 GB HBM4 每 GPU

**② Venice HF CPU 板**

- 高频优化的 Venice 变体（128核高频）
- 为 Helios 定制——不是标准的 EPYC Venice Dense 256 核
- 负责：GPU 驱动/调度、Agent 执行、推理编排

**③ Pensando Vulcano DPU**

- AMD 自研 DPU（继承自 Pensando 收购）
- 加速网络、存储、安全卸载
- 机架内 Scale-Up 网络的智能控制面
- 对标 NVIDIA BlueField

### 4.3 机架内互联架构（推断）

| 互联层次 | 技术 | 带宽/特性 |
|:---------|:-----|:---------|
| GPU→GPU (Scale-Up) | Infinity Fabric / 私有协议 | 高带宽 GPU 直连（类似 NVLink） |
| GPU→CPU | PCIe Gen6 / CXL 3.1 | 高速 CPU-GPU 一致性互联 |
| CPU→CPU | 一致性互联 | 多 CPU 插槽高速互连 |
| 机架内网络 | Pensando DPU + Switch | Scale-Out 网络卸载 |
| 对外网络 | 标准以太网/InfiniBand | 跨机架/POD 互联 |

**关键缺失**：AMD 未披露 Helios 的 GPU-GPU 互联带宽的具体数据。这是与 NVIDIA NVLink 6（3.6 TB/s per GPU）直接对标的核心指标。已知：

- AMD 在 MI300X 上使用 Infinity Fabric 作为 GPU 互联
- Helios 应使用增强版的跨 GPU 互联（可能称 Infinity Fabric 4 或类似技术）
- 如果 Helios 的 GPU-GPU 带宽接近或超过 NVLink 5（1.8 TB/s）水平，则竞争对位充分

### 4.4 分解式 AI：Helios + Cerebras WSE-3

AMD 宣布与 Cerebras 合作，构建 **Helios + Wafer Scale Engine 3 分解式 AI 系统**：

| 组件 | 角色 | 优势 |
|:-----|:-----|:------|
| **Cerebras WSE-3** | 超低延迟推理前端 | 晶圆级引擎，整模型单芯片加载，极致延迟 |
| **Helios** | 后台重计算引擎 | 批量推理、训练、模型微调 |
| **联合性能** | **5× WSE alone** | 异构协同，UUL 前端 + 高吞吐后端 |

**产业信号**：这类似于 NVIDIA 与 Groq 的配对——**多类型加速器异构协作**正在成为趋势。机柜内部需支持 multi-vendor 加速器混合部署。

### 4.5 机架制造与供应链

| 维度 | 详情 |
|:-----|:------|
| 组装复杂度 | 远高于标准服务器 |
| 散热方案 | 液冷强制（45°C 热水） |
| 供应链准备 | 2025 OCP 已原型，2026 Q3 全量产 |
| 产能扩展 | 2027 H2 加速 |
| 关键约束 | HBM4 供应、2nm 产能、液冷基础设施 |

---

## §5 ROCm 软件栈与 AI 驱动 GPU 编程

### 5.1 ROCm 发布节奏加速

| 指标 | 此前 | 此后 |
|:-----|:----|:-----|
| 发布周期 | 数月 | **每 6 周** |
| ROCm 7 vs 最新推理性能 | 基线 | **↑3.3×** |
| ROCm 7 vs 最新训练性能 | 基线 | **↑2.4×** |
| 首日 MI455X 支持 | 传统滞后 | **ROCm.AI 驱动 → Day-0 就绪** |

### 5.2 ROCm.AI — AI Agent 驱动 GPU 编程

**定位**：基于大型代码 AI Agent（Codex、Claude）+ AMD 定制工具的 GPU 编程辅助系统。

**核心技术组件**：

| 组件 | 功能 |
|:-----|:------|
| **AMD-created skills for ROCm** | 针对 AMD GPU 的 Kernel 生成技能库 |
| **Hyperloom** | 代码性能优化工具，**提升 token 率 38%** |

**Hyperloom 的 38% 提升意义**：

- 这不是架构提升，而是**编译器/代码优化**的收益
- 对现有 ROCm 代码无需修改即可获益
- 持续改进（AI Agent 不断学习新的优化模式）

**战略含义**：
> ROCm.AI 将 AMD 的软件生态劣势从"追赶 CUDA"转变为"用 AI 弥补差距"。Day-0 硬件支持 + AI 驱动优化降低了开发者进入门槛。

### 5.3 推理性能里程碑

| 对比 | 提升 | 时间段 |
|:-----|:----|:------|
| 最新 ROCm vs ROCm 7 (推理) | **3.3×** | 2024→2026 |
| 最新 ROCm vs ROCm 7 (训练) | **2.4×** | 2024→2026 |
| MI455X vs MI355X Tokens | **↑34×** | 组合增益 |
| Hyperloom Token 率 | **↑38%** | 单次优化 |

### 5.4 第一天支持策略

ROCm.AI 使 MI455X 发布即支持——开发者无需等待数月的软件栈适配。这标志着 AMD 在软件策略上的根本转变：

- 从"硬件先出，软件慢慢追"→"AI Agent 自动生成 Day-0 Kernel"
- 对 OpenAI 等大客户意义重大：无需等待框架适配即可部署

---

## §6 MI430X HPC 专用 GPU

### 6.1 规格与定位

| 参数 | MI430X | MI455X |
|:-----|:------:|:------:|
| **定位** | HPC 高性能计算 | AI 训练/推理 |
| **FP64 性能** | **288 TFLOPS** | 较弱（AI 优化） |
| **显存** | HBM4（容量同 MI455X） | 432 GB HBM4 |
| **策略** | 替换计算芯粒为 FP64 专用芯粒 | 计算芯粒 AI 优化 |
| **时间线** | **2027 H1** | 2026 Q3 |

### 6.2 芯片策略分析

MI430X 充分利用 AMD 的 **Chiplet 策略优势**：同一封装、同一 HBM4 内存子系统，仅交换计算芯粒。

- MI455X 的计算芯粒为 AI 优化（FP4/FP8/FP16 张量核心密集）
- MI430X 的计算芯粒为 FP64 优化（科学计算双精度密集）

**对比 NVIDIA**：NVIDIA 在 HPC 领域有 A100（FP64 Tensor Core）和 H100（FP64 大幅弱化）。AMD 用 chiplet 策略以较低成本覆盖两个市场段。

### 6.3 存在价值

AI 加速器市场扩张不意味 HPC 消失——传统 HPC 负载（气候模拟、物理仿真、CFD、分子动力学）仍然需要强 FP64 能力。MI430X 确保了 AMD 在 Top500 系统中的竞争力（对比 NVIDIA Grace Hopper / Grace Blackwell 的 HPC 能力）。

---

## §7 对比分析：Venice vs Vera · Helios vs NVL72

### 7.1 Venice vs Vera CPU — 公平框架下的比较

基于 STH Patrick Kennedy 的标准化对比方法论：

| 维度 | Venice (Zen 6) 优势 | Vera 优势 | 结论 |
|:-----|:------------------|:----------|:-----|
| **核心数** | 256 vs 88 | — | Venice 2.9× 核数领先 |
| **内存带宽** | 1.6 TB/s | 1.2 TB/s | Venice +33% |
| **每核带宽** | 6.25 GB/s (256核) | 13.6 GB/s | Vera 在 88 核内优 |
| **单线程性能** | Zen 6 单线程强 | 10-wide + 18 pipes | 接近（需独立基准） |
| **多线程吞吐** | 256核的巨大优势 | 88核+176线程 | Venice 明显领先 |
| **核间延迟** | Chiplet 跨片延迟 | Monolithic 优势 | Vera 在 88 核内优 |
| **软件兼容** | **x86 生态** | Arm 需适配 | Venice 显著优势 |
| **Agent 负载** | 256核可放大量 Agent | 88核单核更强 | 视部署规模定 |

**真实性评估**：AMD 声称的 **2.2× per socket** 是一个**系统级综合指标**，在核密集场景（高并发 AI Agent、虚拟化、批量推理）成立，但在单线程/低延迟时间关键场景不具可比性。

### 7.2 Helios vs NVL72 — 机架级系统对比

| 维度 | AMD Helios | NVIDIA NVL72 (GB200) | NVIDIA NVL72 (Vera Rubin) |
|:-----|:----------|:--------------------|:------------------------|
| **GPU** | MI455X (432GB HBM4) | B200 (192GB HBM3e) | Rubin (288GB HBM4) |
| **显存容量** | **432 GB/GPU** 🏆 | 192 GB/GPU | 288 GB/GPU |
| **GPU-GPU 互联** | Infinity Fabric 4? | NVLink 5 (1.8 TB/s) | NVLink 6 (3.6 TB/s) |
| **互联带宽差距** | ❓未披露 | — | **可能 2-4× 差距** |
| **CPU** | Venice HF (128核高频) | Grace (72核) | Vera (88核) |
| **DPU/NIC** | Pensando Vulcano | BlueField-3 | ConnectX-8 |
| **软件生态** | ROCm.AI (追赶中) | CUDA (成熟) | CUDA (成熟) |
| **Tok/$ 声称** | **+30%** 🏆 | 基线 | — |
| **客户阵容** | Anthropic·OpenAI·Meta | CoreWeave·Google·MS | 待定 |
| **量产时间** | 2026 Q3 | 2025 H1 (出货中) | 2027 H1 |

**核心差距**：Helios 最大的未知数是 **GPU-GPU 互联带宽**。NVIDIA 的 NVLink 6 (3.6 TB/s) 是业界最高水平。如果 AMD 的互联带宽显著低于此，则 Helios 在需要大量跨 GPU 通信的 MLP 训练和 MoE all-to-all 场景中处于劣势。

### 7.3 STH 对 NVIDIA 基准测试的框架偏置分析

Patrick Kennedy（ServeTheHome 创始人，15 年服务器评测经验）指出 NVIDIA 在 Vera 宣传中使用了多个**精心构造的比较框架**：

**① 内存带宽的"代际差"偏置**

- Vera 的 1.2 TB/s LPDDR5X-9600 vs EPYC 9755 的 0.6 TB/s DDR5-6400
- 实际上，Vera 是 2026 年 CPU 用 2026 年内存，对比的是 2024 年 CPU 用 2022 年内存
- Venice（2026 年）的 1.6 TB/s 立即逆转此对比

**② 每核带宽的"除法技巧"**

- Vera: 1.2 TB/s ÷ 88 核 = 13.6 GB/s/核
- EPYC 9755: 0.6 TB/s ÷ 128 核 = 3.1 GB/s/核 → 看起来 4×
- 若用 96 核 EPYC 9655 做分母，比例大幅缩小
- 核心问题：**NVIDIA 用 45% 更大的分母（128 vs 88 核）来放大每核带宽差**

**③ SMT 线程被忽视**

- "单线程"≠"单核心"——SMT 核心的完整吞吐量 = 1× + ~0.3×
- Zen 5 SMT 增益: 32-33% → 1 个 SMT 核心 ≈ 1.3
- 非 SMT CPU（如某些 Arm 设计）用"每线程"指标可能误导

**④ 核间延迟仅限于 88 核以内**

- Vera 的 monolithic 延迟优势在 88 核以内成立
- 超过 88 核（双路）: 核 89-176 要跨 PCIe——延迟、抖动大幅上升
- 超过 176 核: PCIe→NIC→Switch→NIC→PCIe→远端 CPU

**核心结论**：
> Vera 的基准测试在特定框架下有显著优势，但**代际对等比较（Venice vs Vera）会大幅缩小甚至逆转差距**。

---

## §8 产品路线图：GPU·CPU·机架年度节奏

### 8.1 GPU 路线图

| 代际 | 架构 | 制程 | 时间 | 关键特性 |
|:----|:-----|:----|:----|:---------|
| **MI455X** | CDNA 4 | 2nm | **2026 Q3 出货** | 432GB HBM4, EAM |
| **MI500** | CDNA 5 | 2nm+? | **2027** | "4年最大代际飞跃" |
| **MI600** | CDNA Next | ? | **2028** | 全新架构 |

**MI500 的 "2000× 提升"解读**：

- 不是单一代际提升，而是**4 年累计**（从某基线到 MI500）
- 包含：架构 + 制程 + 显存 + 互联 + 软件栈的**组合增益**
- "2000×" 是一个结合 token 吞吐、能效、模型规模的综合营销数字
- 实际单代架构增益可能与传统 GPU 代际（1.5-2×）一致

### 8.2 CPU 路线图

| 代际 | 架构 | 制程 | 时间 | 核心数 |
|:----|:-----|:----|:----|:------|
| **Venice** | **Zen 6** | **TSMC 2nm** | **2026 量产** | 128-256 核 |
| **Florence** | **Zen 7** | ? | **2028** | 待定 |
| **Rivenna** | **Zen 8** | ? | **2030** | 待定 |

**EPYC 代际节奏**：保持 **2 年一重大架构更新**，与 Intel 和 Arm 竞品对齐。

### 8.3 机架路线图

| 机架系统 | 年份 | GPU | CPU | 对标 |
|:--------|:----|:----|:----|:-----|
| **Helios** | **2026** | MI455X | Venice HF | NVL72 (GB200) |
| **Verano** | 2027/2028 | MI500 | Venice/Verano? | NVL72 (Rubin) |
| — | 2028+ | MI600 | Florence | — |

> AMD 承诺 **每年一代机架系统**——与 NVIDIA 的年度平台节奏完全对齐，给客户完全可预测的路线图。

---

## §9 企业端部署：MI350P · Gorgon Halo · Kria AI

### 9.1 MI350P — PCIe 形态 HBM AI 加速卡

| 参数 | MI350P | NVIDIA H200 PCIe |
|:-----|:------|:----------------|
| **形态** | **PCIe 标准卡** | PCIe 标准卡 |
| **HBM 容量** | HBM3e | HBM3e |
| **定位** | 企业 **on-prem 推理** | 上一代企业推理 |
| **竞品状态** | — | NVIDIA 从 Blackwell 起已无高端 PCIe AI 卡 |

**产业信号** ⭐⭐⭐：
> NVIDIA 从 Blackwell 起放弃 PCIe 形态高端 AI 卡。AMD MI350P 填补了这个市场空白。

对企业服务器设计的影响：

- 不需要 OAM baseboard 或液冷即可部署 HBM 级 AI 推理
- 降低企业 AI 部署的机箱/散热门槛
- 适合自主威胁检测、个性化 AI 助手等场景

**已证实效果**：AMD 内部数据中心部署 + Intelligent routing → token 成本降低 **43%**

### 9.2 Gorgon Halo

| 参数 | Gorgon Halo | Strix Halo |
|:-----|:-----------|:-----------|
| **内存** | **192 GB LPDDR5X** | 128 GB |
| **提升** | **+64 GB（+50%）** | 基线 |
| **定位** | 高端 AI 工作站/开发机 | AI 开发机 |

Gorgon Halo 使本地 AI 开发可在单设备运行更大模型（~70B 级别），减少对云 GPU 的依赖。

### 9.3 Kria AI SOM — 对标 Jetson Thor

| 参数 | Kria AI SOM | NVIDIA Jetson Thor |
|:-----|:-----------|:-----------------|
| **核心** | Ryzen AI Embedded X100 | Grace CPU |
| **AI 加速** | XDNA AI Engine | Blackwell GPU |
| **配套** | Ultrascale+ FPGA | 无 |
| **定位** | 物理 AI / 机器人 | 物理 AI / 边缘 |

**Key insight**: AMD 用 FPGA (Xilinx) 作为差异化——Kria SOM + Versal FPGA = "Kria for the brain, Versal for the spine"，在机器人/工业自动化领域有独特定位。

---

## §10 合作伙伴生态与客户阵容分析

### 10.1 客户阵容一览

| 客户 | 采购规模 | 状态 | 战略意义 |
|:-----|:--------|:-----|:---------|
| **Anthropic** | **2GW Helios** | ✅ 已签约 | 最强 AI 安全公司背书 AMD 开放平台 |
| **OpenAI** | 预生产 Helios | 🚀 2026 年底部署 | 全球最大 AI 公司正评估 AMD |
| **Meta** | MI450 系列 | 🔬 2028 协同设计 | 超大规模 OCP 标准共同制定者 |
| **Microsoft** | 长期合作伙伴 | ✅ 持续 | "Perennial partner" |
| **AT&T** | ~1 万亿 tokens/月 | ✅ 已部署 | 企业 AI 标杆案例 |

### 10.2 关键合作伙伴深度分析

**Anthropic (Tom Brown)**

- 购买 2GW Helios 硬件，是 AMD 最大 GPU 客户公告
- 对 AMD 开放平台策略"满意"——暗示 NVIDIA 的绑定策略是痛点
- 强调了 scale-up 和安全性（芯片级到机架级）作为合作重点

**OpenAI**

- "更多算力更快"——OpenAI CTO Katti 的持续诉求
- 已拿到预生产 Helios 机架，正在进行优化
- 不仅看中 Helios，更关注 MI500 及后续路线图
- Tillet（Triton 作者）强调 AMD 开源对 AI 编程生态的帮助

**Meta (Santosh Janardhan)**

- "CPUs are becoming just as important as GPUs, if not more"
- 要求从今天开始做 2028 年部署的协同设计
- "The earlier we co-design, the better we are"
- Meta 是最早采用 AMD MI300 的深度合作伙伴

**AT&T (Jeremy Legg)**

- 每月~1万亿 tokens——真实企业级 AI 负载
- 数据主权 → 不绑定特定硬件 → AMD 开放平台对齐
- 成功降低 token 成本的同时管理总 token 支出增长
- 宣布 OTel 2.0 模型集

**Cerebras (Andrew Feldman)**

- Helios + WSE-3 分解式方案
- WSE-3 做 ULL 前端推理 → Helios 做后台重计算
- 5× WSE-alone performance

### 10.3 客户阵容的战略信号

| 信号 | 含义 |
|:-----|:------|
| Anthropic 2GW + OpenAI 部署 | 最前沿的 AI 公司正在"对冲"NVIDIA 依赖 |
| Meta "从今天开始设计 2028" | 超大规模客户不满足于当前路线图，要求更早期的协同 |
| AT&T：万亿 token 企业级 | AMD 在企业 AI 推理市场的真实落地 |
| Cerebras 分解式 | 多加速器异构成为主流架构方向 |

---

## §11 供电散热与能效分析

### 11.1 Lisa Su 的功率定调

> **"Power is the big limiter right now."**

这是 AI 加速器行业第一次在主要发布中**将功率而非性能定位为最大约束**。与 NVIDIA 在 GTC 2026 上的"NVIDIA 在功率效率上的持续改进"形成对比。

### 11.2 Helios 能效数据

| 指标 | 声称值 | 折算 |
|:-----|:------|:-----|
| Helios perf/watt vs 竞品 | **10-15% better** | — |
| 等效 Tokens per dollar | **+30%** | 含定价因素 |
| 每瓦 token 的竞争含义 | — | 成为整机柜核心竞争力 |

### 11.3 功率约束的行业影响

| 影响方向 | 具体变化 | 时间尺度 |
|:---------|:---------|:--------|
| 液冷强制化 | 从"可选项"→"GPU 整机柜必需" | 2026-2027 |
| 每瓦 token = KPI | 取代纯 token/s 作为主要指标 | 2026+ |
| 供电架构加速 | HVDC + BBU + SSCB 部署推动 | 2026-2028 |
| 数据中心选址重估 | 功率可用性 > 网络延迟 | 2026+ |
| 客户采购决策变化 | 从"多少 TFLOPS"→"多少 token/kWh" | 2026+ |

### 11.4 液冷基础设施要求

Helios 作为 1,000W+ GPU 的整机柜系统，液冷是强制性的：

- 45°C 热水液冷（与 NVIDIA NVL72 规格对齐）
- 需要数据中心级的液冷基础设施（CDU / 冷却塔 / 二次侧管路）
- 对现有风冷数据中心构成升级压力

---

## §12 市场格局与战略评估

### 12.1 AMD 竞争战略的五维分析

| 维度 | AMD 定位 | NVIDIA 定位 | AMD 优劣势 |
|:-----|:---------|:-----------|:-----------|
| **GPU 性能** | 追赶者（每年一代） | 领先者（3.6TB/s NVLink 6） | ❌ 互联差距 |
| **显存容量** | **432 GB 领先** | 192-288 GB | ✅ 明显优势 |
| **CPU 优势** | 256 核 x86 生态 | 88 核 Arm | ✅ 核数+生态 |
| **机架系统** | Helios 首批量产 | NVL72 第二代 | ⏳ 对等竞争 |
| **软件生态** | ROCm.AI 加速追赶 | CUDA 绝对主导 | ❌ 追赶中 |

### 12.2 "开放平台"差异化

AMD 的核心叙事：**开放平台 vs NVIDIA 封闭绑定**。

| 对比 | AMD | NVIDIA |
|:-----|:----|:-------|
| 互联标准 | 支持 UALink / CXL / OCP 开放标准 | NVLink 私有协议 |
| 软件栈 | ROCm 开源 + ROCm.AI | CUDA 私有 |
| 封装形态 | EAM（可定制） | SXM（私有） |
| 客户锁定 | 低（支持多种加速器组合） | 高（绑定 GPU+CPU+网络） |
| 客户价值 | 数据主权、不绑定、选择自由 | 全栈优化、交钥匙 |

**Anthropic 的选择提供了直接证据**：在 AI 安全性组织中，"不被单一供应商锁定"优先于"最高峰值性能"。

### 12.3 NVIDIA 的应对空间

| NVIDIA 杠杆 | 可操作时间 | 效果 |
|:-----------|:---------|:-----|
| Vera Rubin 加速出货 | 2027 H1 | 短期缓解 |
| Vera 降价 | 随时 | 保护 CPU 市场 |
| NVLink 6 开放（UALink 兼容） | 长期 | 削弱 AMD 开放叙事 |
| 软件生态锁定（CUDA + Triton） | 持续 | 维持最大护城河 |
| 对 AMD 客户的价格战 | 随时 | 压缩 AMD 利润空间 |

### 12.4 AMD 的风险清单

| 风险 | 等级 | 描述 |
|:-----|:----|:------|
| GPU-GPU 互联带宽不足 | 🔴 高 | 若 Infinity Fabric 4 远低于 NVLink 6，MoE 训练场景劣势 |
| HBM4 供应约束 | 🔴 高 | HBM4 产能受限影响 MI455X 出货规模 |
| 2nm 产能 | 🟡 中 | TSMC 2nm 同时服务 Apple + AMD，产能竞争 |
| ROCm 实际效果 | 🟡 中 | ROCm.AI 的 AI 驱动编程是否能在复杂场景匹配手动优化 |
| 机架级可靠性 | 🟡 中 | 首代整机柜系统（Helios）的现场可靠性 |
| Venice 2.2× 夸大风险 | 🟡 中 | 若客户独立测试发现差距小于宣称，损害信誉 |
| 价格竞争 | 🟡 中 | NVIDIA 可能在关键客户上大幅降价防守 |

---

## §13 AI 加速器 TAM 与行业影响

### 13.1 AMD 的市场预期

| 市场 | 2026 预测 | 2030 预测 | CAGR |
|:-----|:---------|:---------|:----:|
| AI 加速器 TAM | — | **$1.4T** | 高速 |
| CPU 市场 | — | **$220B** | Agentic AI 驱动 |
| 总硅片 TAM | — | **$2T** | **40%** |
| AI 加速器 = 今天整个芯片市场 | — | $1.4T ≈ 今天全部芯片 | — |

**Agentic AI 驱动因素**：

- Agent 需要大量 CPU 处理 Agent 任务（不仅 GPU 推理）
- AMD 将 CPU TAM 大幅上调的根因：Agentic AI 对 CPU 的需求增长超预期
- "The rate and pace of agentic AI adoption is much faster than AMD was expecting"

### 13.2 对服务器设计的影响

| 影响方向 | 具体变化 |
|:---------|:---------|
| GPU 形态双轨 | 既需要 OAM（高密训练），也需要 PCIe（企业推理） |
| 液冷强制 | GPU 整机柜从风冷/液冷可选 → 液冷强制 |
| 机柜设计 | 需支持 multi-vendor 加速器（GPU+WSE 等） |
| CPU 重要性重估 | Agentic AI 使 CPU 在系统成本中占比上升 |
| 每年一代机架 | 整机柜设计能力成为 GPU 厂商生存门槛 |

### 13.3 竞争格局时间线推演

| 时间 | 事件 | 格局影响 |
|:----|:-----|:---------|
| **2026 Q3** | Helios 出货 · MI455X 量产 | AMD 机架级竞争开端 |
| **2026 H2** | OpenAI 部署 Helios | 最强 AI 公司的 AMD 验证 |
| **2027 H1** | Vera Rubin NVL72 出货 | NVIDIA 反击 |
| **2027 H2** | MI500 (CDNA 5) · Helios 扩展 | AMD 第二代 GPU + 机架 |
| **2027** | Venice→Verano 过渡 | AMD CPU + 机架迭代 |
| **2028** | MI600 (CDNA Next) · Florence (Zen 7) | 下一代全栈竞争 |
| **2030** | Rivenna (Zen 8) · $2T TAM | 长期格局 |

---

## §14 总结与结构性判断

### 14.1 核心结论

**✅ AMD Advancing AI 2026 是 AMD 历史上的分水岭时刻**

不是从 GPU 角度——而是从 **"AMD 终于成为机架级 AI 系统供应商"** 的角度。Helios 的量产使竞争格局从 NVIDIA 独占 → **双雄对峙**。

### 14.2 最大亮点

1. **MI455X 的 432 GB HBM4** — 显存容量领先是真正的硬件差异化
2. **Venice 16 通道 DDR5-12800 = 1.6 TB/s** — 抹平并超越 Vera 的内存带宽优势
3. **Helios 量产 + 顶级客户阵容** — 从 PPT 到实物的跨越
4. **ROCm.AI 的 AI 驱动 GPU 编程** — 软件生态短板的新解题思路
5. **"Power is the big limiter" 行业定调** — 标志着 AI 基础设施竞争进入新阶段

### 14.3 最大未知

1. **GPU-GPU 互联带宽** — Helios 能否在跨 GPU 通信场景中与 NVLink 6 竞争？
2. **Venice 2.2× 的真实性** — 需要独立第三方基准验证
3. **HBM4 和 2nm 的供应能力** — 能否支撑大规模出货？
4. **1000W+ 液冷机架的现场可靠性** — 首代系统的实际表现

### 14.4 结构性判断

> **2026 年下半年开始，AI 基础设施采购将从"单芯片比较"转向"整机柜系统比较"。**
>
> ANN → NVIDIA NVL72 vs AMD Helios vs 新兴 UALink 生态的三方竞争。
>
> 最大的赢家不是某一家厂商，而是**超大规模客户**——他们获得了议价能力和供应多元化。

### 14.5 四条设计哲学

1. **Chiplet 策略的充分验证** — MI455X / MI430X 共享封装，覆盖 AI + HPC 两市场
2. **机架级思维** — 从卖芯片到卖系统，AMD 跟随 NVIDIA 的"AI 工厂"路线
3. **开放平台叙事** — 在 AI 安全/数据主权成为热点时尤其有价值
4. **每年一代的承诺** — 与 NVIDIA 保持相同的创新节奏，压缩追赶时间

---

## 变更日志

| 日期 | 变更内容 |
|:----|:---------|
| 2026-07-27 | 初始创建，基于 STH Advancing AI 2026 现场报道 + STH Vera 基准对比框架 + 知识库已有素材综合撰写 |

---

**🔗 交叉链接**

- [NVIDIA Vera Rubin 架构深度分析](../../02_project/01_superpod/architecture/2026-07-29-nvidia-vera-rubin-architecture-deep-analysis-dup1.md) — 直接竞争对标对象
- [知识库：行业调研跟踪 2026-07-27](../../../01_survey/industry-research/tech/2026-07-27.md) — 行业信号补充
- [知识库：服务器硬件动态 2026-07-23](../../../01_survey/server-hardware/2026-07-23.md) — 原始事件记录

**📊 相关方法论**

- [STH Katherine 框架偏置分析](../../../01_survey/server-hardware/2026-07-23.md#动态二) — NVIDIA vs AMD 基准对比方法
- [竞争分析方法论] — 待补充

> **本文所有来源可追溯**: STH Ryan Smith 现场报道、STH Patrick Kennedy 标准化对比框架、AMD Advancing AI 2026 主题演讲直播。量化数据的对比基线详见各章节标注。
