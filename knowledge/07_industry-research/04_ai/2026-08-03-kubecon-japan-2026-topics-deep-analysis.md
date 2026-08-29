# 🌏 KubeCon + CloudNativeCon Japan 2026 技术主题深度分析

> **元信息**: 文件状态=正式 | 覆盖范围=KubeCon Japan 2026 全量议程（142 sessions / 163 speakers）的主题聚类 × 深度技术解读 × 与 AI 基础设施业务相关性 | 版本=v1.0
> **适用范围**: 云原生技术演进跟踪、AI 基础设施平台层设计、GPU 编排/调度选型、Kubernetes 平台工程规划、技术战略对标
> **关键词**: KubeCon · CloudNativeCon · 横滨 · AI/ML 基础设施 · GPU 调度 · Kueue · DRA · CoHDI · 可组合硬件 · KV Cache 感知调度 · llm-d · Agent · 可观测性 · OpenTelemetry · eBPF · 平台工程 · GitOps · 多集群 · 安全 · 机密计算 · Wasm

## 目录 (TOC)

- [§0 执行摘要](#0-执行摘要)
- [§1 大会概况与数据来源](#1-大会概况与数据来源)
  - [1.1 大会基本信息](#11-大会基本信息)
  - [1.2 议程结构](#12-议程结构)
  - [1.3 数据来源与方法](#13-数据来源与方法)
  - [1.4 主题分布统计](#14-主题分布统计)
- [§2 主题全景：三大主线](#2-主题全景三大主线)
- [§3 AI/ML 基础设施（最大主线）](#3-aiml-基础设施最大主线)
  - [3.1 GPU 调度与共享](#31-gpu-调度与共享)
  - [3.2 推理平台与 KV Cache 感知调度](#32-推理平台与-kv-cache-感知调度)
  - [3.3 广域 GPU Fabric](#33-广域-gpu-fabric)
  - [3.4 AI Agent 平台化](#34-ai-agent-平台化)
  - [3.5 GPU-Centric 基础设施与多租户平台](#35-gpu-centric-基础设施与多租户平台)
- [§4 平台工程与多集群治理](#4-平台工程与多集群治理)
  - [4.1 GitOps 演进：OCI vs Git](#41-gitops-演进oci-vs-git)
  - [4.2 平台原语与抽象](#42-平台原语与抽象)
  - [4.3 多集群规模化与联邦治理](#43-多集群规模化与联邦治理)
  - [4.4 平台工程商业价值](#44-平台工程商业价值)
- [§5 安全：AI 时代的威胁与防御](#5-安全ai-时代的威胁与防御)
  - [5.1 供应链安全](#51-供应链安全)
  - [5.2 运行时安全与取证](#52-运行时安全与取证)
  - [5.3 身份、授权与 AI Agent](#53-身份授权与-ai-agent)
  - [5.4 机密计算](#54-机密计算)
- [§6 可观测性：OpenTelemetry 毕业与 Agentic 可观测](#6-可观测性opentelemetry-毕业与-agentic-可观测)
  - [6.1 OTel 生态成熟与规模化迁移](#61-otel-生态成熟与规模化迁移)
  - [6.2 高基数指标挑战](#62-高基数指标挑战)
  - [6.3 Agentic 可观测性](#63-agentic-可观测性)
  - [6.4 扩展性与 Wasm 化](#64-扩展性与-wasm-化)
- [§7 网络与连接](#7-网络与连接)
  - [7.1 Kubernetes 多网络：跨域共识](#71-kubernetes-多网络跨域共识)
  - [7.2 Envoy 动态模块](#72-envoy-动态模块)
  - [7.3 gRPC 原生拦截](#73-grpc-原生拦截)
  - [7.4 Cilium 大规模迁移](#74-cilium-大规模迁移)
- [§8 存储与数据处理](#8-存储与数据处理)
  - [8.1 存储内计算：Wasm in Storage](#81-存储内计算wasm-in-storage)
  - [8.2 Ceph 生态](#82-ceph-生态)
  - [8.3 数据生命周期管理](#83-数据生命周期管理)
- [§9 运维、性能与可持续](#9-运维性能与可持续)
  - [9.1 DRA 能源效率](#91-dra-能源效率)
  - [9.2 灾难恢复与启动可靠性](#92-灾难恢复与启动可靠性)
  - [9.3 边缘与能源行业实践](#93-边缘与能源行业实践)
  - [9.4 裸金属声明式管理](#94-裸金属声明式管理)
- [§10 新兴与前沿](#10-新兴与前沿)
  - [10.1 CoHDI：可组合硬件与资源解耦（重点）](#101-cohdi可组合硬件与资源解耦重点)
  - [10.2 Kernel-Bypass 网络](#102-kernel-bypass-网络)
  - [10.3 其他新兴信号](#103-其他新兴信号)
- [§11 与 AI 基础设施业务的相关性分析](#11-与-ai-基础设施业务的相关性分析)
  - [11.1 超节点与 GPU 池化映射](#111-超节点与-gpu-池化映射)
  - [11.2 存储映射](#112-存储映射)
  - [11.3 网络映射](#113-网络映射)
  - [11.4 供电与散热映射](#114-供电与散热映射)
  - [11.5 落地行动清单](#115-落地行动清单)
- [§12 关键趋势判断](#12-关键趋势判断)
- [附录A 全部技术 Session 清单（69 个）](#附录a-全部技术-session-清单69-个)
- [附录B Keynote 清单](#附录b-keynote-清单)
- [附录C Co-located Events](#附录c-co-located-events)
- [参考文献](#参考文献)
- [变更记录](#变更记录)

---

## §0 执行摘要

**KubeCon + CloudNativeCon Japan 2026**（7 月 28-30 日 · 横滨 · Pacifico Yokohama）是 CNCF 旗舰大会的亚太站。本次大会**以 AI 为绝对主线**——「Infinite Agents, Finite Kubernetes」「The State of Cloud Native: The Shift Towards AI」等表述贯穿全场，与 2025 年相比，AI 从"新话题"升格为"基础设施默认假设"。

基于一手议程数据（Sessionize API，142 sessions / 163 speakers，2026-08-03 抓取）深度分析，三大核心发现：

1. **Kubernetes 正在成为 GPU 编排的事实标准，且从"调度 GPU"走向"调度拓扑"**：Kueue 拓扑感知调度（Meta Superintelligence Lab 案例）、共享 GPU 调度（1000+ GPU 生产蓝图）、DRA 身份感知治理、跨集群虚拟节点——GPU 资源管理的颗粒度从"单卡"细化到"拓扑域/显存分片/身份授权"。
2. **AI 推理平台工程化是最大增量**：从 vLLM 单实例托管到 KV-Cache 感知调度（llm-d）、推理一致性校验（Conformance for Inference）、多租户推理隔离——推理侧"平台化/多租户化"的成熟度正在快速追赶训练侧。
3. **硬件解耦与可组合性成为新范式信号**：CNCF Sandbox 项目 **CoHDI**（动态硬件组合）与 **Wasm in Storage**（存储内计算）两场新秀，指向"硬件资源从服务器解耦、按需动态挂载"的下一代云原生基础设施方向——与超节点/GPU 池化/CXL 池化趋势同频。

**与服务器/AI 基础设施业务最相关的 6 个 session**：CoHDI 深潜、llm-d 分布式推理（KV Cache 感知）、Nationwide GPU Fabric（NTT/SKT IOWN APN 广域 L2）、Kueue 拓扑感知调度、Wasm in Storage、Multi-Networking RDMA 面板。

---

## §1 大会概况与数据来源

### 1.1 大会基本信息

| 项 | 内容 |
|:---|:-----|
| 名称 | KubeCon + CloudNativeCon Japan 2026 |
| 时间 | 2026-07-28（Co-located Events）～ 07-29/30（主会议） |
| 地点 | 横滨 · Pacifico Yokohama（JST, UTC+9） |
| 规模 | **142 个 session / 163 位 speaker**（一手 API 数据） |
| 主题 | AI 与云原生融合、平台工程、安全、可观测性、多集群、边缘、能源 |
| 后续活动 | KubeCon China 2026（9/8-9 上海）、KubeCon NA 2026（11/9-12 盐湖城）、KubeCon EU 2027（3/15-18 巴塞罗那） |

### 1.2 议程结构

```text
7/28 (Tue) -- CNCF-hosted Co-located Events: ArgoCon / KeycloakCon / Japan Community Day
              + Sponsor-hosted Co-located Events + Registration
7/29 (Wed) -- Keynotes + Breakouts (3F/4F/5F) + Solutions Showcase + Welcome Reception
7/30 (Thu) -- Keynotes + Breakouts + Solutions Showcase
```

- **会场结构**：Main Hall（1F）+ 5 个并行分会场（3F 313-315、4F 411-415、5F 501-503），另有 Foyer 展区与 Offsite Event。
- **Session 形态**：Keynote、Breakout（25-45min）、Lightning Talk（5min）、Project Lightning Talk（7min，PLT 项目专场）、Sponsored Demo、Maintainer Track、Solutions Showcase。

### 1.3 数据来源与方法

- **一手数据**：Sessionize API `t0vgv3tv`（KubeCon Japan 2026 官方议程托管平台）于 **2026-08-03** 抓取，含全部 sessions/speakers/categories/rooms 结构化数据。
- **交叉验证**：LF Events 官网（events.linuxfoundation.org）大会信息页。
- **分析方法**：按 track（类别）聚类 → 逐 session 摘要解析 → 业务相关性映射。
- **边界说明**：本分析基于**议程标题+官方摘要**，不包含演讲现场内容（录播将于会后 2 周内发布至 CNCF YouTube）。部分 session 摘要未提供（Keynote/Service Session），相关判断基于公开项目知识。

### 1.4 主题分布统计

**Track 分布（去除非技术分类后）**：

| Track | Session 数 | 占比 | 热度 |
|:------|:----------:|:----:|:----:|
| AI + ML | 15 | 21.7% | 🔥🔥🔥🔥🔥 |
| Security | 9 | 13.0% | 🔥🔥🔥🔥 |
| Observability | 8 | 11.6% | 🔥🔥🔥🔥 |
| Operations + Performance | 7 | 10.1% | 🔥🔥🔥 |
| Platform Engineering | 5 | 7.2% | 🔥🔥🔥 |
| Connectivity | 4 | 5.8% | 🔥🔥 |
| Data Processing + Storage | 3 | 4.3% | 🔥🔥 |
| Emerging + Advanced | 2 | 2.9% | 🔥 |
| Application Development | 2 | 2.9% | 🔥 |
| Cloud Native Experience / Novice / Community | 14 | 20.3% | 🔥🔥🔥 |
| 合计（技术 session） | 69 | 100% | — |

**观察**：AI + ML 以 15 个 session 独占榜首（21.7%），若加上 AI 相关的 Keynote（4 个）与 Lightning Talk，AI 相关占比接近 **30%**——Kubernetes 生态的 AI 化程度在本次大会达到新高。

---

## §2 主题全景：三大主线

```text
                    +-------------------------------------+
                    |   KubeCon Japan 2026 Topic Map      |
                    +-------------------------------------+
  Mainline 1 (Core)         Mainline 2 (Base)          Mainline 3 (Wings)
 +-----------------+    +-------------------+    +----------------------+
 | AI/ML Infra     |    | Platform Eng      |    | Security x Observab  |
 | (15 sessions)   |    | x Multi-Cluster   |    | (9+8 sessions)       |
 +-----------------+    +-------------------+    +----------------------+
 | GPU Sched/Share |    | GitOps Evolution  |    | Supply Chain(SBOM)   |
 | Inference/KVC   |    | Primitives(kro)   |    | Runtime(eBPF/For)    |
 | Wide-Area Fab   |    | Fleet Governance  |    | Identity(AuthZEN)    |
 | Agent Platform  |    | Biz Value         |    | OTel Grad/Scale      |
 | Topology-Aware  |    | Cluster API       |    | Agentic Obsrv        |
 +-----------------+    +-------------------+    +----------------------+

 Cross-cutting: Connectivity(4) Storage(3) Ops(7) Emerging(2)
 -- HW Disagg(CoHDI/Wasm-in-Storage) -- Energy(DRA/VPP) -- Edge(Sat/EV/Grid) --
```

> 图注：主线一=AI/ML 基础设施（核心驱动）；主线二=平台工程×多集群（承载底座）；主线三=安全×可观测性（信任两翼）；横轴=连接/存储/运维/新兴（贯穿性主题）。

三大主线并非孤立：**AI 是业务驱动，平台工程是承载方式，安全与可观测是 AI 大规模落地的信任前提**。本次大会大量 session 呈现"AI 需求反向重塑既有技术"的特征（如 DRA 因 GPU 而加速、OTel 因 Agent 而提出 Context Fabric、GitOps 因多集群 AI 平台而演进）。

---

## §3 AI/ML 基础设施（最大主线）

15 个 AI+ML track session + 4 个 AI 相关 Keynote，覆盖 GPU 调度、推理平台、广域编排、Agent 平台化四大子域。

### 3.1 GPU 调度与共享

| Session | 关键内容 | 意义 |
|:--------|:---------|:-----|
| **kube-scheduler-evaluator**（Rihito Bannai/Hidehito Yabuuchi） | 在**秒级**评估调度器性能的工具：解决真实作业耗时数天、scheduler_perf 仅支持微基准、kwok/kind 实时运行成本高的问题，支持万级节点规模回放 | AI 调度器研发从"拍脑袋"走向可量化基准 |
| **Shared GPU Scheduling & Proactive Autoscaling: 1000+ GPUs**（SNOW Corp, Jeonghyun Kim/Reza Jelveh） | 运营 1000+ A100 GPU、服务 2 亿用户、3 个头部 GenAI 应用、1200+ AI 工作流。核心痛点：K8s 原生 GPU 调度将 GPU 视为**原子资源**，导致 Train-to-Inference 流水线 2× 过度配置 | 生产级 GPU 分片 + 预测性扩缩容蓝图 |
| **Who's Using That GPU? Identity-Aware Access Control**（Peter ONeill/Kunal Kushwaha） | DRA ResourceClaim 创建拦截的 validating admission webhook：强制身份验证、使用理由、过期时间——现有 DRA 集群中"任何有基础 RBAC 的用户都能无身份声明 GPU" | GPU 资源治理从"容量"走向"身份与合规" |
| **Topology-Aware Scheduling with Kueue**（Michał Woźniak/Wei Huang） | **Meta Superintelligence Lab** 案例：Kueue 提供多租户配额管理 + 高级调度，支撑跨复杂异构 GPU 拓扑的大规模训练/推理，从手工 in-house 调度迁移到 K8s 原生 | 拓扑感知 = AI 调度第一性需求（NUMA/域/机架感知） |
| **Beyond Single-Cluster Limits: Virtual Nodes**（Kunal Das/Esmira Bayramova） | ML 平台团队用 Virtual Nodes 跨云上/本地集群统一 GPU：解决"多 kubeconfig 割裂、Kueue 跨集群队列不可见、工作负载无法故障转移" | 突发弹性 + 本地稳态的混合 GPU 架构 |

**主题判断**：GPU 调度正在经历三层演进——**资源原子化（整卡）→ 资源碎片化（分片/共享）→ 资源拓扑化（拓扑感知+身份治理）**。SNOW 的 2× 过度配置惩罚与 Kueue 的拓扑感知，共同指向"调度器必须理解 GPU 互连拓扑（NVLink 域/NUMA/机架）"这一与超节点 HBD 域设计直接相关的命题。

### 3.2 推理平台与 KV Cache 感知调度

| Session | 关键内容 | 意义 |
|:--------|:---------|:-----|
| **How to Evolve Your LLM Self-Hosting Platform**（Shingo Omura/Yiyang Zhan） | vLLM 最小架构 → 多租户平台演进路径：Envoy AI Gateway + Athenz 鉴权；核心观点是"**过早采用高级推理技术会爆炸性增加部署复杂度**"，给出分阶段引入评估框架 | 推理平台演进方法论（克制 vs 堆料） |
| **llm-d: From Model Serving to Distributed Inference**（Kay Yan/Linbo He） | KAITO（模型上架/GPU 自动供给/OpenAI 兼容端点/vLLM 运行时）之上扩展 **inference-aware scheduling + KV-cache-aware 调度**，将平台从"单实例 serving"升级为"生产级分布式推理" | **KV Cache 感知调度**——与 G3.5 KV Cache 硬件方案直接呼应 |
| **Conformance for Inference**（Aditya Soni/Hrittik Roy） | GPU 推理部署的重复失败模式：错误镜像/制品、CUDA 运行时不匹配、显存不足、资源请求错误、线下通过但真实流量回归——在共享 GPU 平台演变为多租户事故（noisy neighbor/OOMKill/SLO 违约） | 推理侧"部署合规测试"，对标训练侧 CI |
| **Shared Yet Isolated: Multi-Tenant Inference**（Yuto Hiraki/Yusuke Tanaka） | 自托管 LLM 推理平台的共享与隔离平衡：不同团队不同访问模式（仅 API 端点 vs 完整管理权）与安全要求 | 多租户推理平台治理模式 |

**主题判断**：推理平台正在复制"训练平台化"的成熟路径：**serving（单实例）→ platform（多租户+治理）→ distributed inference（KV Cache 感知+拓扑感知调度）**。llm-d 的 KV-cache-aware scheduling 表明 KV Cache 已从"硬件容量问题"上升为"调度器一等公民"——与知识库 G3.5 KV Cache 存储方案（分层梯队、MMG 加速）形成软件/硬件双视角闭环。

### 3.3 广域 GPU Fabric

**Beyond the DC Walls: Building a Nationwide GPU Fabric with KubeVirt and Wide-Area L2**（Kazuki Sato [NTT]/Jian Li）

- **背景**：云原生 AI 基础设施撞上"电力+土地"物理墙。
- **方案**：NTT × SKT 共建"Nationwide GPU Fabric"——用 **IOWN APN**（All-Photonics Network）构建 **1000km+ 高速 L2 网络**（札幌→福冈），将分布式 DC 用 Kubernetes + KubeVirt 编排为**单一集群**。
- **深度要点**：广域 L2（而非 L3）的动机在于**保留 VRF/广播域语义、降低东西向流量路径复杂度**；KubeVirt 承载 VM 形态 GPU 工作负载；挑战包括广域时延下的调度决策、故障域划分、跨 DC 的存储/网络一致性。

**主题判断**：这是本次大会**与超节点议题最直接对撞**的 session——把"单 DC 内的 HBD 高带宽域"外推到"全国尺度的低延迟光网络域"。IOWN APN 的物理层（全光）为 L2 广域提供了延迟预算，但其"把远程 GPU 当本地 GPU"的假设仍需面对光速物理极限（1000km ≈ 3.3ms 单向）。与知识库[网络划分文档](../02_rd/02_project/01_superpod/2026-08-03-data-control-flow-and-network-partition-deep-analysis.md)中"域内 Scale-Up vs 域间 Scale-Out"的分层模型形成对照：**广域 GPU Fabric 本质是把 Scale-Out 网络拉到国家尺度，并尝试用 L2 语义伪装 Scale-Up 体验**。

### 3.4 AI Agent 平台化

| Session | 关键内容 | 意义 |
|:--------|:---------|:-----|
| **From Experiment to Enterprise: AI Agent for Code Review**（Adam Phan） | **Sony Interactive Entertainment**：代码审查 Agent 从实验到生产，覆盖 **400+ PlayStation 内部仓库**，跨越保密性、治理、审查质量、成本四重挑战 | 企业级 Agent 落地的完整路径样本 |
| **Architecting Secure Agentic Workflows**（Vincent Caldeira/Morgan Foster） | 金融行业多 Agent 架构：工具发现、安全访问、流量路由的云原生抽象 | Agent 基础设施安全模式 |
| **The Great Doubt: What Building an AI Agent Taught Us About Trust**（Nicole van der Hoeven） | 可观测性 AI 助手的信任问题：幻觉、上下文遗忘、自信错误答案——需要"系统性怀疑"的评估体系 | Agent 可信度评估方法论 |
| **Sandbox for Agentic Application**（Xu Wang/Yu Hu） | Kata 容器开发者 + 蚂蚁开源团队 + Japan AI 团队：Agent 生成/拉取的代码不可信，用 K8s 沙箱隔离 Agent 与机密数据/控制面 | Agent 运行时隔离（沙箱即安全边界） |
| **Infinite Agents, Finite Kubernetes**（Keynote, Mohammad Mikal Bin Amrul Halim Gan） | 大会开幕定调：Agent 数量无限，Kubernetes 是承载它们的有限底座 | Agent 与 K8s 的关系宣言 |

**主题判断**：Agent 从 Demo 走向生产（PlayStation 400 repos、金融多 Agent、可观测助手），但**信任、治理、隔离**成为比"智能"更硬的约束——这与用户知识库中"AI 交付悖论"（四阶段微笑曲线：Demo 速成→鼓吹→落地差→维护贵）的判断完全吻合。

### 3.5 GPU-Centric 基础设施与多租户平台

- **Keynote: The Next Evolution of Kubernetes: GPU-Centric Infrastructure for AI Workloads**（Takao Indoh）——Kubernetes 下一站演进的 GPU 中心化宣言：从"容器编排"转向"GPU 资源编排"。
- **Keynote: Building a Multi-Tenant AI Platform with the CNCF Ecosystem**（Aya Igarashi）——用 CNCF 项目全家桶（Kueue/Knative/vLLM 等）构建多租户 AI 平台。
- **Keynote: How Subaru Accelerated AI Model Development for Next-Generation EyeSight with Kubernetes**（Ryoji Kobayashi）——汽车 ADAS（EyeSight）AI 模型开发平台化案例。
- **Designing a Hybrid AI Platform on Kubernetes**（Aoi Kamide）——混合 AI 平台：应对 RAG 成本、数据传输开销、敏感数据安全，本地 GPU 选型 + OSS 集成 + 模型/应用生命周期管理。
- **Beyond Single-Cluster Limits**（见 3.1）——虚拟节点跨集群 GPU。

**主题判断**：Keynote 阵容（富士通/Subaru/云厂商）显示**日本产业界（汽车、制造、运营商）正在集体向"Kubernetes + GPU"迁移**，AI 基础设施在日本进入行业落地期。

---

## §4 平台工程与多集群治理

### 4.1 GitOps 演进：OCI vs Git

- **OCI is not Git: Rethinking the GitOps Source of Truth**（Michael Crenshaw/Robin Lieb）：Git 提供历史/blame/diff/PR 审查；OCI 提供内容寻址、可分发、离线（airgap）兼容制品。行业正"像换灯泡一样"用一个替换另一个，但两者能力模型不同——需要按场景选择源真相（source of truth）载体。
- **The Evolution of GitOps in Platform Engineering**（Artem Lajko）：2017 年四原则 → 今日多集群大规模操作的核心；早期做法在规模下失效，everything-as-code 带来自动化同时也带来配置漂移治理难题。

### 4.2 平台原语与抽象

**Evolving Platform Primitives: Beautiful Platforms with kro**（Jakob Möller/Adam Crowder）：优秀平台不是堆工具，而是设计好原语——把裸 K8s 资源 + 模板 + 脚本 + 自定义 controller 的组合，重构为**可组合原语（composable primitives）**，两步法：定义抽象 → 让 Kubernetes 原生执行。

### 4.3 多集群规模化与联邦治理

| Session | 关键内容 |
|:--------|:---------|
| **Don't Start With 500 Clusters**（Nibir Bora/Matt Morrison） | 两家公司独立得出同一结论：Cluster API 作为舰队级 Kubernetes 的声明式基石；100+ 多租户集群 / 每客户隔离集群（SaaS/BYOC/自管） |
| **Scaling In Kubernetes Safely: 1300+ Clusters, 40,000+ Nodes**（Shota Yoshimura） | 私有云 KaaS 的**安全收缩**（scale-in）：自定义 controller 整合欠载 worker 节点，影响硬件采购、机架容量、长期运维 |
| **Score-Driven Multi-Cluster Management**（Kazuma Takeuchi/Joydeep Banerjee） | OCM 新 Add-on：**动态评分框架**，把 GPU 利用率、功耗效率等实时遥测引入多集群放置决策，替代静态策略 |
| **From 5 to 1,300+ Clusters: Declarative Scaling**（Keynote, Shota Yoshimura） | 5 个集群声明式扩展到 1300+ 的私有 Kubernetes 规模化路径 |
| **Out of the Box, at Multi-Region Scale**（Keynote, Jaewoo Choi） | Hyundai 多区域平台规模化经验 |
| **Towards Sustainable Multi-Cluster Management**（Jinwang Mok/ChangHyeon Im） | 学术基础设施：4 裸金属集群 100GbE、2PB Rook-Ceph、22 GPU（7 种型号 L40S/A100）、边缘设备，研究生运维的"ScaleX-POD"统一多集群 |

### 4.4 平台工程商业价值

- **From 165 Days to 30 Minutes**（Aoi Nishijima/Moeka Okamura/Kohei Yamamoto）：JAL Digital，4000 工程师支撑 500 系统，环境搭建需 15 部门 40+ 表单、**165 天**前置时间 → 平台工程压缩至 **30 分钟**。
- **Turning Platform Engineering Work into Business Value**（Danielle Cook/Simon Forster）：平台工程团队如何用领导听得懂的语言证明投资价值。

**主题判断**：平台工程重心从"造平台"转向"规模化治理 + 价值证明"——1300 集群/40000 节点的安全收缩、动态评分放置、Cluster API 舰队化，是 AI 平台规模化后的必然治理课题。

---

## §5 安全：AI 时代的威胁与防御

### 5.1 供应链安全

- **SBOMit: Making SBOMs Accurate with Attestations**（Marco De Vincenzi/Justin Cappos）：SBOM 加速普及但**准确性是盲区**——静态分析/包清单会漏掉动态下载依赖、构建期制品、网络拉取组件；用 attestations（可验证凭证）让 SBOM 可溯源。
- **Scalable Security and Compliance in the Age of AI**（Eddie Knight）：**37,000 条 AI 编程助手依赖升级建议** + **200,000 个恶意 OSS 包**的数据集研究——旧防御策略失效、新攻击模式奏效，给出清晰应对路径。
- **Vulnerability Response for Large OSS Projects**（Jo Guerreiro/Charline Voinot）：Grafana 从 CVE-2023-3128 三年实战到自动化漏洞响应的演进。

### 5.2 运行时安全与取证

- **Detecting Compromised CI with eBPF and Cilium Tetragon**（Liz Rice）：CI/CD 是攻击者首选目标（Trivy workflow 事件），Tetragon 从保护 K8s 工作负载扩展到 GitHub Actions 等 CI 环境。
- **Runtime Security at Scale with eBPF**（Yogeshwara Krishna Kota/Rutuj Waghare）：Sauron eBPF 从内核捕获高保真运行时信号，混合检测 + 根因分析。
- **Container Forensics for Kubernetes**（Jie Wu/Pulkit Garg）：容器被攻陷但 Pod 30 秒内重启——内存/进程/临时文件系统蒸发。云原生生态预防/检测很成熟，**取证是空白**；构建开源证据管道。

### 5.3 身份、授权与 AI Agent

- **User Namespaces in Production**（Kohei Sugihara/Toru Komatsu）：User Namespaces 改善多租户安全（UID/GID 隔离），但生产落地撞上 **ReadWriteMany (RWX) 共享存储墙**——ID-mapped mount 依赖文件系统实现。
- **AuthZEN in Practice**（Yoshiyuki Tabata）：2026 年 1 月 OpenID 基金会发布 AuthZEN 规范，标准化云原生平台与 Agent 的细粒度实时授权；Agent 获得更广 API/基础设施访问权后，"授权"成为安全与治理核心。
- **Behind the CNCF IAM Whitepaper**（Yoshiyuki Tabata/Hiroyuki Wada）：云原生系统 AuthN/AuthZ 全景。
- **Navigating the Identity Abyss in the AI-Native Era**（Keynote, Yuichi Nakamura）：AI 原生时代的身份认证深渊——Agent 的身份、凭证、委派成为新问题域。
- **Identities and Authentication for your Agents with Keycloak**（Takashi Norimatsu/Alexander Schwartz）：用 Keycloak 为 Agent 提供身份与认证。

### 5.4 机密计算

**Sealed for All: Multi-Party Confidential Computing, No Trust**（Ryota Hashimoto/Takahiro Kambara）：跨组织数据协作（联合计算）中，基于硬件 TEE 的多方机密计算（MPCC）——多方数据/代码在不暴露的前提下联合处理。与知识库可靠性测试追踪（见 MEMORY.md「深度洞察」）中"边界向加密/机密计算域延伸"的趋势判断吻合。

**主题判断**：安全主题呈现清晰的**三层结构**——供应链（SBOM/漏洞/恶意包）、运行时（eBPF/取证）、身份授权（AuthZEN/IAM/Agent 身份），其中 **Agent 身份与授权**是 AI 原生时代全新安全域（AuthZEN 规范 2026-01 发布即入选主议程，信号强烈）。

---

## §6 可观测性：OpenTelemetry 毕业与 Agentic 可观测

### 6.1 OTel 生态成熟与规模化迁移

- **Keynote: OpenTelemetry Celebrates Graduation and the Next Era of Agentic Observability**（Alolita Sharma/Ted Young）：OTel 正式毕业（Graduated），进入 Agentic 可观测新纪元。
- **From Statsd to OpenTelemetry**（Iris Grace Endozo/Farzad Vazirnia）：Atlassian 从运行多年的 statsd 定制管道迁移到 OTel——证明"能用的旧系统"也可以系统性迁移。
- **Lessons From Five+ Years of Fluent Bit**（Hiroshi Hatake）：Fluent Bit 从轻量日志转发器成长为全球可观测管道核心组件；**非 UTF-8 输入（GBK/Shift-JIS）是生产基线需求而非边缘场景**（日本市场特色）。
- **Standardizing Industrial IoT Observability**（Alolita Sharma）：OTel 进入工业 IoT：设备监测、预防性维护、质量控制。

### 6.2 高基数指标挑战

**Designing for High-cardinality Metrics**（Walther Lee/Aleksandr Krivoshchekov）：Reddit 实践——K8s 中每个 Pod 都会新增时序序列，一次 rollout+rollback 三倍基数；Prometheus/OTel 的 recording rules、stream aggregation、sharding 都有权衡，Reddit 发现这些不够，自建方案。

### 6.3 Agentic 可观测性

- **From Tool Calls to Context Fabric: Building AI-Native Observability**（Deepak Choudhary/Dheeraj Kapur）：工程师问"服务为什么失败"，答案散落在 Prometheus 指标/Loki 日志/告警信号/runbook 知识中；现有 AI 方案（RAG/Text-to-PromQL/单工具 copilot）各自为政——提出 **AI Context Fabric** 跨域连接信号。
- **Repurposing OpenTelemetry Traces as Test Data**（Yoshiki Fujikane）：把线上 OTel trace 的 request/response 对当作迁移系统的 ground truth 测试数据——Java→Go 迁移 PoC 验证（4 个 CRUD 端点）。

### 6.4 扩展性与 Wasm 化

- **OTel meets Wasm**（Kotaro Inoue/Tsuzuki Tsuchiya）：用 Wasm 重构 OTel Collector 扩展性——contrib 发行版组件过多，团队需要按需裁剪的安全发行版。
- **One Binary, Two Ecosystems: Prometheus Exporters with OCB**（Kyle Eckhart/Arthur Sens）：用 OCB 把 Prometheus exporter 直接嵌入自定义 Collector 发行版，创建新运维模型。

**主题判断**：OTel 毕业是生态成熟标志；可观测性正向 **AI 原生**演进（Context Fabric 把"指标/日志/链路/知识"四层信号统一给 AI 消费），同时日本市场的非 UTF-8 与 Wasm 化扩展反映本地化与轻量化诉求。

---

## §7 网络与连接

### 7.1 Kubernetes 多网络：跨域共识

**Breaking the Single-Network Barrier: A Cross-Domain Look at Kubernetes Multi-Networking**（Lionel Jouin/Sunyanan Choochotkaew/Masaharu Kanda/Surya Seetharaman/Sara Qasmi）——**面板讨论**：

- 核心问题：K8s 原生多网络支持为何如此缓慢复杂？
- 场景：**AI/ML 高性能网络（RDMA）**、电信（telco）、云游戏、安全隔离、多租户合规。
- 与知识库[网络划分文档](../02_rd/02_project/01_superpod/2026-08-03-data-control-flow-and-network-partition-deep-analysis.md)的"五网模型"（Scale-Up/Scale-Out/存储/管理/OAM）直接对应——Kubernetes 侧的多网络需求正是物理多网在软件层的映射。

**相关 Project Lightning Talk**：**Spiderpool Unlocks Fine-Grained RDMA Observability for AI Inference**（Weizhou Lan）——Spiderpool（CNCF 项目）为 AI 推理提供细粒度 RDMA 可观测性。

### 7.2 Envoy 动态模块

**Beyond Wasm: How Dynamic Modules Let You Extend Envoy Proxy in Go, Rust, or Any Language**（Rohit Agrawal/Takeshi Yoneda）：Envoy 扩展痛点——C++ filter = 维护 fork；WASM = 沙箱开销 + 扩展点有限 + 生态停滞。**Dynamic Modules**：用 Go/Rust/任意语言写共享库扩展，已在 **Databricks 和 Netflix** 使用。配套 session：**Dynamic Modules in Envoy Gateway: API Design, Safety, and Operability**（Kota Kimura/Huabing Zhao）。

### 7.3 gRPC 原生拦截

**Pluggable Interception: Using ExtAuthz and ExtProc in gRPC using xDS**（Pawan Bhardwaj）：gRPC 新增服务扩展——ExtAuthz（RPC 处理前实时授权 allow/deny）、ExtProc（side-channel 外部处理），无需外部代理。

### 7.4 Cilium 大规模迁移

**The Road to Cilium: Migrating 150+ Kubernetes Clusters at Airbnb**（Yifei Sun）：Airbnb 从 AWS VPC CNI 迁移到 Cilium（150+ 集群），解锁 eBPF 能力：kube-proxy replacement、集群级网络策略；分享大规模 pod 生命周期性能测试、迁移路径。配套：**A Decade of Cilium Around the World**（Liz Rice/Hiroki Hanada）。

**主题判断**：网络主题聚焦两个方向——**多网络是 AI 时代刚需**（RDMA 需要独立网络路径，与物理五网模型呼应）；**数据平面可扩展性**（Envoy Dynamic Modules 替代 Wasm 成为新范式）。

---

## §8 存储与数据处理

### 8.1 存储内计算：Wasm in Storage

**Running Wasm Inside Your Storage Cluster with CSI and Gateway API**（Ho Kim/SangJoon Park）——**本次大会存储域最值得关注 session**：

- **问题**：云原生早已"计算存储分离"，但 **AI 工作负载暴露新瓶颈：网络本身**。厂商对策有二：① 预处理数据压缩带宽（但预处理期会饱和网络）；② 集成 RDMA/专用硬件（牺牲开放性、锁定硬件）。
- **第三条路**：**把计算下沉到存储集群内**——用 Wasm 在存储侧执行过滤/预处理，CSI + Gateway API 编排。数据无需过网，带宽需求骤降，且保持开放（Wasm 沙箱、多语言）。
- **意义**：这是"存储内计算/近数据计算"的云原生实现，与知识库[AI 存储文档](../../02_rd/01_product/00_hardware/06_storage/2026-08-03-ai-storage-device-interconnect-integration-deep-analysis.md)中"DPU 卸载 + 近存计算"趋势同源。

### 8.2 Ceph 生态

- **Rook: Intro and Deep Dive with Ceph**（Satoru Takeuchi/Deepika Upadhyay/Dan van der Ster）——Rook + Ceph 入门与深潜。
- **Changing the Engine Mid-Flight: Zero-Downtime Ceph Upgrades**（Cuong Nguyen）——电信云（5G Core：AMF/UPF）Ceph 18.x（10-50 节点裸金属）**Reef → Squid 零停机升级**，三个真实失败场景复盘。

### 8.3 数据生命周期管理

**Taming Billions of Rows**（Ruslan Kadyrov）：Mercari 核心 MySQL 表达数十亿行，迁移到云原生分布式数据库（TiDB）过程中发现数据生命周期管理（DLM）是成本与迁移风险的首要驱动——数据只增不减。

**主题判断**：存储 session 数量少但信号强——**近数据计算（Wasm in Storage）**与 **零停机存储升级** 是 AI 与电信两个重负载场景的硬需求。

---

## §9 运维、性能与可持续

### 9.1 DRA 能源效率

**Sustainability by Design: Leveraging DRA for Energy-Efficient Kubernetes Clusters**（Sunyanan Choochotkaew/Faseela Kundattil）：

- 现状：Kubernetes 调度对能耗几乎无感知——工作负载看不到硬件（尤其加速器）的能源特征，更无法映射到用户可见成本。
- 方案：用 **DRA（Dynamic Resource Allocation）** 把能耗特征作为资源属性暴露给调度器，让集群自动选择最清洁/高效的能源来源。

**主题判断**：DRA 从"GPU 资源管理"扩展到"能源资源管理"——与知识库[800V HVDC 文档](../03_server/2026-07-30-800V-HVDC-power-architecture-deep-analysis.md)的供电架构、以及能源感知调度（Power Capping/碳排放感知放置）形成软硬闭环。

### 9.2 灾难恢复与启动可靠性

- **Is Your Kubernetes Disaster Recovery Actually Ready?**（Saiyam Pathak/Saloni Narang）：**68% 组织去年经历过灾难数据丢失，平均损失 450 万美元/次**；2026 DR 调查中 K8s DR 相关问题几乎无人应答——容器工作负载在恢复计划中的覆盖是盲区。
- **Maximizing Launch Reliability**（Hiroshi Hayakawa）：频繁重启应用的启动可靠性——冷启动（缓存初始化/JIT 编译）导致性能退化与启动失败；利用 K8s 新特性 **In-place Pod Resize** 实现 CPU bursting 提升启动可靠性。

### 9.3 边缘与能源行业实践

- **Ground Control to Cloud Native**（Upendra Gurugubelli/Masaya Arai）：Synspective 运营 SAR 卫星星座，地面系统在过境窗口保持有状态连接——错误时机部署会丢失 500km 轨道上的卫星连接；每颗卫星通信窗口不同，标准 rollout 策略失效。
- **Large-Scale Edge Management: 200 EV Chargers**（Keynote, Ryota Yonekura）：200 台 EV 充电桩的 Kubernetes 边缘管理。
- **What is a Virtual Power Plant (VPP)?**（LeRenzo Malcom，两场）：Enpal 运营欧洲最大住宅光伏舰队之一，构建下一代 VPP 平台——把数千分布式 IoT 设备（光伏/电池/EV 充电器）编排为一个协调的云原生资产，**"用软件造电厂"**。
- **How CNCF Projects United Two Countries' Engineers to Solve AI's Power-and-Land Problem**（Keynote, Kazuki Sato）：两个国家工程师用 CNCF 项目解决 AI 的电力与土地问题（与 3.3 广域 GPU Fabric 同源）。

### 9.4 裸金属声明式管理

**Image-Based Bare-Metal Provisioning with Metal3.io, Cluster API and Kubernetes**（Kashif Khan/Ganesh Vasudevan）：裸金属 K8s 传统依赖 PXE 工作流/自定义脚本/人工干预 → 漂移、不一致、高运维开销；用 Metal3.io + Cluster API + Ironic 实现**完全声明式、Kubernetes 原生**的裸金属生命周期管理。

**主题判断**：运维域的特色是**日本/行业垂直场景**（卫星、EV、电网、5G 电信），加上 AI 基础设施的能耗与 DR 硬需求——"可持续 + 可靠"是 2026 运维关键词。

---

## §10 新兴与前沿

### 10.1 CoHDI：可组合硬件与资源解耦（重点）

**CoHDI: A CNCF Sandbox Project for Dynamic Hardware Composability in Kubernetes**（Naoki Oguchi/Hidetsugu Sugiyama/Michele Gazzetti/Jyothsna Deshpande/Kensuke Koda）+ **Project Lightning Talk: CoHDI: Dynamic Hardware Composition for AI-Era Kubernetes Workloads**（Naoki Oguchi）——**一场大会两个 session（深潜 + PLT），本大会新兴技术最大亮点**：

- **全称**：Composable Hardware in Disaggregated Infrastructure（解耦基础设施中的可组合硬件）。
- **核心能力**：在 Kubernetes 云原生环境中**动态挂载/卸载硬件资源（如 GPU）**——资源从服务器解耦，按需组合。
- **定位**：2026 年新晋 **CNCF Sandbox** 项目，标志"灵活高效的基础设施编排"新范式。
- **演讲阵容**：5 位 speaker 联合（含日本团队），涉及 GPU 动态组合的范式与实现。

**主题判断**：CoHDI 与知识库中多个主题共振——① 超节点的**可组合基础设施**趋势（[超节点定义文档](../../02_rd/02_project/01_superpod/architecture/2026-07-28-supernode-definition-and-design-philosophy.md)中"软件定义、资源池化"设计哲学）；② CXL 内存池化/GPU 池化的硬件底座（[AI 存储文档](../../02_rd/01_product/00_hardware/06_storage/2026-08-03-ai-storage-device-interconnect-integration-deep-analysis.md)）；③ 分布式 OS 论文中的"资源远取"（[分布式 OS 论文分析](../02_rd/02_project/01_superpod/2026-07-30-distributed-os-papers-deep-analysis.md)）。**CoHDI 是"资源解耦"在 Kubernetes 软件层的落地载体**，值得持续跟踪其与 CXL/PCIe 池化的对接。

### 10.2 Kernel-Bypass 网络

**A Practical, Research-Backed Introduction to Cloud-Native Kernel-Bypass Networking**（Kenichi Yasukata）：云原生规模化下可预测低延迟/高吞吐的挑战——传统协议栈开销限制延迟敏感工作负载；系统化梳理 kernel-bypass 技术（DPDK/AF_XDP/io_uring 等）从基础到前沿。与知识库[数据流/控制流文档](../02_rd/02_project/01_superpod/2026-08-03-data-control-flow-and-network-partition-deep-analysis.md)中 RDMA/DPU 卸载主题、以及网络划分中的低延迟诉求呼应。

### 10.3 其他新兴信号

- **PLT 项目专场**（11 个）：Argo CD at Scale、k0s、OpenTelemetry 路线图、CoHDI、Kairos（不可变 OS）、Longhorn、Spiderpool（RDMA 可观测）、youki（Rust 容器运行时）、Lima（AI 沙箱化）、Karmada（多集群）、k0s。
- **Emerging + Advanced track**：仅 2 个正式 session（CoHDI、Kernel-Bypass），但 AI 相关 session 大量使用了 Advanced/Intermediate 级别——"新兴"已渗透进各主线。

---

## §11 与 AI 基础设施业务的相关性分析

> 本大会对服务器/AI 基础设施厂商的**平台层启示**：硬件能力（GPU 池化、KV Cache 存储、RDMA 网络、能源供给）正在被 Kubernetes 生态以"资源抽象 + 调度原语"的方式消费。硬件设计必须回答"如何被软件原生编排"。

### 11.1 超节点与 GPU 池化映射

| KubeCon 信号 | 超节点/硬件映射 | 行动建议 |
|:-------------|:---------------|:---------|
| Kueue 拓扑感知调度（Meta） | 调度器需要感知 NVLink 域/HBD 拓扑 | 提供硬件拓扑 API（域/机架/互联带宽）给调度层；超节点设计文档补充"调度可发现性"章节 |
| CoHDI 动态硬件组合 | GPU/CXL 池化、可组合基础设施 | 跟踪 CoHDI 与 CXL 交换机/PCIe 池化对接；评估 GPU 动态挂载对服务器 BMC/固件的需求 |
| SNOW 1000+ GPU 分片 | GPU 显存分片/共享（MIG/vGPU） | 服务器需支持更细颗粒度 GPU 分片硬件原语，并暴露给 DRA |
| Nationwide GPU Fabric（IOWN） | 广域 L2 与超节点域内 Scale-Up 的边界 | 明确"域内高速互联 vs 域间广域"的产品分层；评估对 NTT/SKT 类客户的方案适配 |
| Beyond Single-Cluster Virtual Nodes | 跨集群 GPU 突发 | 服务器需支持快速加入/退出集群的节点生命周期（Metal3 化） |

### 11.2 存储映射

| KubeCon 信号 | 存储映射 | 行动建议 |
|:-------------|:---------|:---------|
| llm-d KV-cache-aware scheduling | KV Cache 分层存储（HBM→DDR→CXL→NVMe） | 把 KV Cache 存储容量/带宽作为调度器可查询的资源属性；与 G3.5 方案联动 |
| Wasm in Storage | 近数据计算/存储内计算 | 评估存储控制器/SSD 侧的 Wasm 执行能力；SPDK 之上的计算卸载路径 |
| Rook/Ceph 零停机升级 | 存储集群可维护性 | 服务器存储方案需提供"无感升级"能力（热替换/滚动升级硬件兼容） |
| Spiderpool RDMA 可观测 | RDMA 网络运维 | RDMA 网络健康度/遥测能力作为服务器方案卖点（与 OAM 网呼应） |

### 11.3 网络映射

- **Multi-Networking RDMA 面板**：K8s 原生多网络支持 RDMA = 物理多网（五网模型）的软件前提。服务器网络方案需提供清晰的**多网络平面抽象**（BMC/管理网独立、数据网可插拔）。
- **Kernel-Bypass**：DPDK/io_uring 与 RDMA/DPU 卸载协同，是"低延迟"卖点的软件侧支撑。
- **Cilium/eBPF 大规模迁移**：eBPF 数据平面（kube-proxy replacement）成为大规模集群网络基线——服务器网卡需考虑对 eBPF 卸载（如 SmartNIC offload）的支持。

### 11.4 供电与散热映射

- **DRA 能源效率**：能源特征（PUE/功耗/碳排放）成为调度输入 → 服务器需暴露**细粒度功耗遥测**（PSU/VRM/芯片级），与 800V HVDC 架构联动。
- **VPP 虚拟电厂**：数据中心作为电网可调度资产（需求响应/削峰）——服务器供电架构需支持**功率上限动态调节**（Power Capping 接口）。
- **Nationwide GPU Fabric 的 Power-and-Land**：AI 基础设施选址受电力/土地约束 → 供电方案（HVDC/BBU）成为集群级卖点。

### 11.5 落地行动清单

1. **跟踪 CoHDI**（CNCF Sandbox）：月度跟进项目路线图，评估与 CXL 池化/GPU 动态组合的产品结合点。
2. **对齐 Kueue 拓扑感知**：在超节点产品资料中补充"调度拓扑可发现性"（topology discovery API）设计。
3. **调研 llm-d**：KV Cache 感知调度若成标准，将直接影响 KV Cache 存储产品的接口设计（容量/带宽可查询）。
4. **关注 Wasm in Storage**：评估存储侧计算卸载与 SPDK 方案的结合（过滤/聚合下沉）。
5. **研究 DRA 能源模型**：服务器功耗遥测的标准化接口（对接 K8s DRA 能源属性）。
6. **复用 OTel 毕业红利**：服务器带外管理/遥测输出对接 OTel 标准（OTLP），降低客户集成成本。

---

## §12 关键趋势判断

1. **Kubernetes = AI 基础设施默认控制面**：从"容器编排"到"GPU 编排"（GPU-Centric 演进），调度器成为 AI 硬件的"操作系统"，硬件必须暴露拓扑/能源/KV Cache 等语义给调度层。
2. **推理平台化追赶训练平台化**：KV Cache 感知调度（llm-d）、推理一致性校验、多租户推理——推理侧正在复制训练侧的成熟路径，**KV Cache 从容量问题升格为调度问题**。
3. **资源解耦成为下一代范式**：CoHDI（GPU 动态组合）+ Wasm in Storage（计算下沉）+ Nationwide GPU Fabric（广域资源池）三路并进，指向"物理资源池化、软件按需组合"的云原生 2.0。
4. **Agent 是 2026 最大应用变量**：从 PlayStation 400 仓库到金融多 Agent，"Agent 信任/治理/隔离/身份"成为新安全域（AuthZEN 规范、Agent 沙箱、Agent 身份）。
5. **能源成为一等公民**：DRA 能源效率、VPP 虚拟电厂、Power-and-Land 三个 session 把"能源"从运维议题升级为架构议题——供电架构（HVDC/BBU）与软件调度必须联动。
6. **日本产业界 AI 落地加速**：富士通/Subaru/NTT/SKT/JAL/Enpal 等传统行业巨头集体登台，AI 基础设施从互联网厂商扩散到汽车/制造/能源/航空。
7. **可观测性 AI 原生**：OTel 毕业 + Context Fabric + traces-as-test-data，可观测数据正在成为 AI 的训练/验证素材，而不仅仅是人类排障工具。

---

## 附录A 全部技术 Session 清单（69 个）

> 数据源：Sessionize API（2026-08-03 抓取）。按主题聚类排列。

### A1. AI + ML（15）

| # | Session | 演讲者 |
|:-:|:--------|:-------|
| 1 | How to Evolve Your LLM Self-Hosting Platform: Advanced Optimizations | Shingo Omura, Yiyang Zhan |
| 2 | kube-scheduler-evaluator: Evaluating Schedulers at Hyperscaler Scale in Seconds | Rihito Bannai, Hidehito Yabuuchi |
| 3 | Manufacturing Alerts to ReActive Agents: Self-Evolving AI Agents for Predictive Maintenance | Seungtae Moon |
| 4 | From Experiment to Enterprise: Scaling an AI Agent for Code Review | Adam Phan |
| 5 | From Model Serving to Distributed Inference: How llm-d Evolves AI Platforms on Kubernetes | Kay Yan, Linbo He |
| 6 | Beyond Single-Cluster Limits: Scaling GPU Workloads Across Kubernetes with Virtual Nodes | Kunal Das, Esmira Bayramova |
| 7 | Designing a Hybrid AI Platform on Kubernetes | Aoi Kamide |
| 8 | Shared GPU Scheduling & Proactive Autoscaling: 1000+ GPUs | Jeonghyun Kim, Reza Jelveh |
| 9 | Conformance for Inference: Reducing Bad Deploys on a GPU Platform | Aditya Soni, Hrittik Roy |
| 10 | Shared Yet Isolated at Scale: Multi-Tenant Inference Platform | Yuto Hiraki, Yusuke Tanaka |
| 11 | Who's Using That GPU? Identity-Aware Access Control for GPU Workloads | Peter ONeill, Kunal Kushwaha |
| 12 | The Great Doubt: What Building an AI Agent Taught Us About Trust | Nicole van der Hoeven |
| 13 | Architecting Secure Agentic Workflows: Financial Sector Case Study | Vincent Caldeira, Morgan Foster |
| 14 | Topology-Aware Scheduling for AI Training & Inference with Kueue | Michał Woźniak, Wei Huang |
| 15 | Beyond the DC Walls: Nationwide GPU Fabric with KubeVirt and Wide-Area L2 | Kazuki Sato, Jian Li |

### A2. Security（9）

| # | Session | 演讲者 |
|:-:|:--------|:-------|
| 1 | User Namespaces in Production: Root in Containers with RWX | Kohei Sugihara, Toru Komatsu |
| 2 | Detecting Compromised CI with eBPF and Cilium Tetragon | Liz Rice |
| 3 | Vulnerability Response for Large Open Source Projects | Jo Guerreiro, Charline Voinot |
| 4 | SBOMit: Making SBOMs Accurate with Attestations | Marco De Vincenzi, Justin Cappos |
| 5 | Scalable Security and Compliance in the Age of AI | Eddie Knight |
| 6 | Runtime Security at Scale with eBPF: Hybrid Detection and Root Cause Analysis | Yogeshwara Krishna Kota, Rutuj Waghare |
| 7 | Sealed for All: Multi-Party Confidential Computing, No Trust | Ryota Hashimoto, Takahiro Kambara |
| 8 | Container Forensics for Kubernetes: Evidence Pipeline with OSS Tools | Jie Wu, Pulkit Garg |
| 9 | AuthZEN in Practice: Standardizing Authorization | Yoshiyuki Tabata |

### A3. Observability（8）

| # | Session | 演讲者 |
|:-:|:--------|:-------|
| 1 | From Tool Calls to Context Fabric: AI-Native Observability for Platform Engineering | Deepak Choudhary, Dheeraj Kapur |
| 2 | Lessons From Five+ Years of Fluent Bit: Global-Scale Observability Agent | Hiroshi Hatake |
| 3 | Standardizing Industrial IoT Observability with OpenTelemetry | Alolita Sharma |
| 4 | From Statsd to OpenTelemetry: Atlassian's Metrics Platform Migration | Iris Grace Endozo, Farzad Vazirnia |
| 5 | Designing for High-cardinality Metrics | Walther Lee, Aleksandr Krivoshchekov |
| 6 | Repurposing OpenTelemetry Traces as Test Data | Yoshiki Fujikane |
| 7 | OTel meets Wasm: Rethinking Collector Extensibility | Kotaro Inoue, Tsuzuki Tsuchiya |
| 8 | One Binary, Two Ecosystems: Embedding Prometheus Exporters with OCB | Kyle Eckhart, Arthur Sens |

### A4. Operations + Performance（7）

| # | Session | 演讲者 |
|:-:|:--------|:-------|
| 1 | Ground Control to Cloud Native: SAR Satellite Constellation Deployments | Upendra Gurugubelli, Masaya Arai |
| 2 | Sustainability by Design: Leveraging DRA for Energy-Efficient Clusters | Sunyanan Choochotkaew, Faseela Kundattil |
| 3 | Running OpenSearch at Scale in High-Traffic Gaming Systems | Siddharth Vijay |
| 4 | Score-Driven Multi-Cluster Management: Dynamic Scoring Framework | Kazuma Takeuchi, Joydeep Banerjee |
| 5 | Maximizing Launch Reliability: Controlled Lift-off for Reliable Startup | Hiroshi Hayakawa |
| 6 | Is Your Kubernetes Disaster Recovery Actually Ready? | Saiyam Pathak, Saloni Narang |
| 7 | Image-Based Bare-Metal Provisioning with Metal3.io, Cluster API | Kashif Khan, Ganesh Vasudevan |

### A5. Platform Engineering（5）

| # | Session | 演讲者 |
|:-:|:--------|:-------|
| 1 | OCI is not Git: Rethinking the GitOps Source of Truth | Michael Crenshaw, Robin Lieb |
| 2 | Scaling In Kubernetes Safely on On-Prem KaaS: 1300+ Clusters, 40,000+ Nodes | Shota Yoshimura |
| 3 | Evolving Platform Primitives: Beautiful Platforms with kro | Jakob Möller, Adam Crowder |
| 4 | From 165 Days to 30 Minutes: Breaking Enterprise Silos with Platform Engineering | Aoi Nishijima, Moeka Okamura, Kohei Yamamoto |
| 5 | The Evolution of GitOps in Platform Engineering | Artem Lajko |

### A6. Connectivity（4）

| # | Session | 演讲者 |
|:-:|:--------|:-------|
| 1 | Pluggable Interception: ExtAuthz and ExtProc in gRPC using xDS | Pawan Bhardwaj |
| 2 | Breaking the Single-Network Barrier: K8s Multi-Networking Cross-Domain Panel | Lionel Jouin, Sunyanan Choochotkaew, Masaharu Kanda, Surya Seetharaman, Sara Qasmi |
| 3 | Beyond Wasm: Dynamic Modules for Envoy Proxy in Go, Rust, Any Language | Rohit Agrawal, Takeshi Yoneda |
| 4 | The Road to Cilium: Migrating 150+ Kubernetes Clusters at Airbnb | Yifei Sun |

### A7. Data Processing + Storage（3）

| # | Session | 演讲者 |
|:-:|:--------|:-------|
| 1 | Running Wasm Inside Your Storage Cluster with CSI and Gateway API | Ho Kim, SangJoon Park |
| 2 | Taming Billions of Rows: Data Lifecycle Management from Cloud-Native DB Migration | Ruslan Kadyrov |
| 3 | Changing the Engine Mid-Flight: Zero-Downtime Ceph Upgrades | Cuong Nguyen |

### A8. Emerging + Advanced / Application Development / Community 等（18）

| # | Session | Track | 演讲者 |
|:-:|:--------|:------|:-------|
| 1 | A Practical, Research-Backed Introduction to Kernel-Bypass Networking | Emerging + Advanced | Kenichi Yasukata |
| 2 | CoHDI: Dynamic Hardware Composability in Kubernetes（深潜） | Emerging + Advanced | Naoki Oguchi et al. |
| 3 | AIOps: (near) Zero-Touch Production Rollout Fixes | Application Development | Kevin Dubois, Carlos Sanchez |
| 4 | What is a Virtual Power Plant (VPP)? Green Tech and Grid Modernization | Application Development | LeRenzo Malcom |
| 5 | Beyond Power and Magic: Forging Stable eBPF Tools | Cloud Native Novice | Kenta Tada, Carla Gaggini |
| 6 | The State of Cloud Native: The Shift Towards AI | Cloud Native Experience | Katie Gamanji |
| 7 | Don't Start With 500 Clusters: Cluster API Fleet Patterns | Cloud Native Experience | Nibir Bora, Matt Morrison |
| 8 | Towards Sustainable Multi-Cluster Management in Academic Infrastructure | Cloud Native Experience | Jinwang Mok, ChangHyeon Im |
| 9 | Sandbox for Agentic Application with Cloud Native Stack | Cloud Native Experience | Xu Wang, Yu Hu |
| 10 | Turning Platform Engineering Work into Business Value | Cloud Native Experience | Danielle Cook, Simon Forster |
| 11 | Beyond the Code: Technical Leadership in CNCF Communities | Cloud Native Experience | Kevin Wang et al. |
| 12 | How Community Infrastructure Helped Grow Taiwan's OSS Contributors | Cloud Native Experience | Ching Kuo, ChengHao Yang |
| 13 | ⚡LT: How Writing a Cluster Inventory API Plugin Led Me to Maintainership | Cloud Native Experience | Kahiro Okina |
| 14 | ⚡LT: From First Contribution to Maintainer: OSS Journey Inside youki | Cloud Native Experience | Yusuke Sakurai |
| 15 | ⚡LT: Learning Kubernetes From Logs | Cloud Native Novice | Kakeru Ishii |
| 16 | ⚡LT: 1 Year, 15 Certs, a Raspberry Pi Home Lab: Golden Kubestronaut | Cloud Native Novice | Yu Misaki |
| 17 | I Tested 7 So You Only Need 1: First Gateway API Migration | Cloud Native Novice | Hoon Jo |
| 18 | Your First Kubernetes Contribution: Documentation Localization | Cloud Native Novice | Ian Y. Choi, Wonyong Hwang |

### A9. Project Lightning Talks（11 个）

Argo CD at Scale（Nitish Kumar）· k0s（Prithvi Raj）· OpenTelemetry Roadmap（Ted Young）· **CoHDI（Naoki Oguchi）** · Kairos Immutable OS（William Rizzo）· Longhorn（Divya Mohan）· **Spiderpool RDMA Observability（Weizhou Lan）** · youki（Yuta Nagai）· Lima AI Sandboxing（Ansuman Sahoo）

---

## 附录B Keynote 清单

**7/29（周三）**：Keep Cloud Native Moving: Building Japan's Platform for Open Innovation（Jonathan Bryce/Chris Aniszczyk）→ Infinite Agents, Finite Kubernetes（Mohammad Mikal Bin Amrul Halim Gan）→ The Next Evolution of Kubernetes: GPU-Centric Infrastructure（Takao Indoh）→ Building a Multi-Tenant AI Platform with CNCF Ecosystem（Aya Igarashi）→ Subaru EyeSight AI Model Development（Ryoji Kobayashi）→ From 5 to 1,300+ Clusters（Shota Yoshimura）→ Hyundai Multi-Region Scale（Jaewoo Choi）

**7/30（周四）**：Where Will Cloud Native Take You?（Jeffrey Sica）→ Golden Kubestronaut（Yu Misaki）→ Cloud Native Community Japan（Ziyi Xie）→ **OpenTelemetry Graduation & Agentic Observability（Alolita Sharma/Ted Young）** → 200 EV Chargers Edge Management（Ryota Yonekura）→ Navigating the Identity Abyss in the AI-Native Era（Yuichi Nakamura）→ VPP: Green Tech and Grid Modernization（LeRenzo Malcom）→ CNCF Projects Solving AI's Power-and-Land Problem（Kazuki Sato）

## 附录C Co-located Events

- **CNCF-hosted**：ArgoCon（Argo 生态专项）、KeycloakCon（身份与访问管理专项）、Japan Community Day（日本社区日）。
- **Sponsor-hosted**：多场厂商合办活动（独立议程）。

---

## 参考文献

1. KubeCon + CloudNativeCon Japan 2026 官方议程，Sessionize API `t0vgv3tv`（2026-08-03 抓取）：<https://sessionize.com/kubecon-cloudnativecon-japan-2026/>
2. LF Events 官网大会页：<https://events.linuxfoundation.org/kubecon-cloudnativecon-japan/>
3. 知识库交叉引用：
   - [超节点/AI训推数据流·控制流与物理网络划分深度分析](../02_rd/02_project/01_superpod/2026-08-03-data-control-flow-and-network-partition-deep-analysis.md)
   - [超节点 HBD（高带宽域）规模选取深度专题](../02_rd/02_project/01_superpod/2026-08-03-hbd-domain-scale-deep-analysis.md)
   - [超节点深度分析：定义、本质与设计哲学](../../02_rd/02_project/01_superpod/architecture/2026-07-28-supernode-definition-and-design-philosophy.md)
   - [分布式 OS 论文密集爆发深度分析](../02_rd/02_project/01_superpod/2026-07-30-distributed-os-papers-deep-analysis.md)
   - [AI 基础设施存储：设备·互联·集成技术全景](../../02_rd/01_product/00_hardware/06_storage/2026-08-03-ai-storage-device-interconnect-integration-deep-analysis.md)
   - [800V HVDC 电源架构深度分析](../03_server/2026-07-30-800V-HVDC-power-architecture-deep-analysis.md)

## 变更记录

- [2026-08-03] v1.0 创建：基于 Sessionize API 一手议程数据（142 sessions）撰写 KubeCon Japan 2026 技术主题深度分析。覆盖 AI/ML 基础设施（15）、安全（9）、可观测性（8）、运维（7）、平台工程（5）、连接（4）、存储（3）、新兴（2）八大主题域 + 相关性分析与趋势判断。
