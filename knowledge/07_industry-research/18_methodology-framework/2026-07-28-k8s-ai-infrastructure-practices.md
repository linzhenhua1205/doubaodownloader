# 🏗️ K8s AI 基础设施实践 · 行业调研报告（2026 H1）

> **专题**: K8s AI Infrastructure Practices
> **创建**: 2026-07-28 | **版本**: v1.0 | **跟踪频率**: 双周
> **关联目录**: [`cloud-native/`](../../01_survey/cloud-native/) · [`cluster-training/`](../../01_survey/cluster-training/) · [`llm-trends/`](../../01_survey/llm-trends/)
> **核心来源**: CNCF Blog · K8s Blog · NVIDIA · KubeCon 2026

---

## 目录

1. [专题概览](#1-专题概览)
2. [技术栈全景](#2-技术栈全景)
3. [调度与资源管理](#3-调度与资源管理)
4. [GPU 编排与设备管理](#4-gpu-编排与设备管理)
5. [AI 训练基础设施](#5-ai-训练基础设施)
6. [AI 推理基础设施](#6-ai-推理基础设施)
7. [AI 网络与可观测性](#7-ai-网络与可观测性)
8. [AI Agent 基础设施](#8-ai-agent-基础设施)
9. [平台工程 2.0](#9-平台工程-20)
10. [行业标准与合规](#10-行业标准与合规)
11. [战略总结与趋势判断](#11-战略总结与趋势判断)
12. [参考资料](#12-参考资料)

---

## 1. 专题概览

### 1.1 核心主题

Kubernetes 作为 AI 基础设施"事实操作系统"的演进路径。关键问题：

- **调度架构**: 从静态 Device Plugin 到 **Dynamic Resource Allocation (DRA) GA**，GPU 从黑盒资源变为可编程可查询的一等公民
- **编排能力**: 从 Web 服务到分布式训练/推理/Agent 的三类工作负载覆盖
- **生态成熟**: CNCF 200+ 项目中的 AI 相关项目从零散到体系化——Kubeflow/Volcano/HAMi/KServe/Kueue 形成完整 AI 工作流
- **平台工程 2.0**: 平台的服务对象从开发者扩展到 ML 工程师、AI Agent

### 1.2 关键数据

| 指标 | 数据 | 来源 |
|:-----|:-----|:------|
| K8s 生产使用率 | 82% 容器用户在生产运行 K8s | CNCF 2025 年度调查 |
| GenAI on K8s | 66% 组织使用 K8s 管理推理负载 | CNCF 2025 年度调查 |
| 日部署模型 | 仅 **7%** 组织每日部署模型 | CNCF 2025 年度调查 |
| K8s 社区 | 150K+ 贡献者 | CNCF 社区统计 |
| AI Conformance 认证 | 18→**31** 个认证平台（6个月） | NVIDIA/CNCF |
| KAI Scheduler 规模 | 已验证 **10,000+ GPU** 集群 | NVIDIA |

### 1.3 关键判断

> **"K8s 已成为 AI 的 de facto OS"** — Erin A. Boyd, NVIDIA Senior Director, CNCF GB Member

AI 基础设施的三个核心挑战正处于架构级拐点：

- ⚡ **调度复杂性**: Device Plugin → DRA (GA in v1.35)，NVIDIA 已将 DRA Driver 贡献至 K8s SIG-Node
- 🔲 **GPU 碎片化**: 静态分配 → DRA CEL 可编程选择器 + HAMi GPU 虚拟化中间件
- 👁️ **可观测性缺失**: Prometheus/OTel → GPU 级 + NCCL 级 + Goodput 级可观测

### 1.4 时间线：2026 H1 关键里程碑

| 时间 | 事件 | 意义 |
|:----|:-----|:------|
| 2026-01 | K8s v1.35 DRA GA | GPU 调度架构级变更 |
| 2026-03 | NVIDIA DRA Driver 进 K8s SIG-Node | GPU 厂商贡献标准化实现 |
| 2026-04 | K8s v1.36 DRA health reporting + Pod-Level Resource | 设备故障与应用故障可区分 |
| 2026-04 | KubeCon EU: KAI Scheduler → CNCF Sandbox | NVIDIA 集群调度器开源 |
| 2026-06 | K8s AI 贡献政策发布 | 首个主流项目完整 AI 治理模板 |
| 2026-06 | K8s AI Gateway WG 成立 | 微软/Google 发起 |
| 2026-07 | HAMi → CNCF Incubating | GPU 虚拟化中间件正式化 |
| 2026-07 | Confidential Containers → CNCF Incubating | GPU 机密计算标准化 |
| 2026-07 | CNCF Japan AI Infra SIG 启动 | 区域 AI Infra 社区组织化 |
| 2026-07 | NVIDIA $4M 捐赠 CNCF CI GPU | 社区 CI/CD 基础设施质变 |

---

## 2. 技术栈全景

### 2.1 K8s AI 基础设施分层架构

```text
+------------------------------------------------------------------+
|  Layer 5: AI Agent 基础设施                                       |
|  +- Agent Sandbox (K8s SIG) · agent-substrate                   |
|  +- Agent Gateway (AAIF) · MCP Gateway                          |
|  +- OTel Agent 追踪 · NGINX Agent 安全边界                      |
+------------------------------------------------------------------+
|  Layer 4: AI 推理服务                                              |
|  +- KServe · vLLM · TGI · NVIDIA NIM / Dynamo                   |
|  +- Gateway API Inference Extension · kgateway · Envoy AI GW    |
|  +- Goodput SLO · Autoscale (VPA/HPA)                           |
+------------------------------------------------------------------+
|  Layer 3: AI 训练编排                                              |
|  +- Kubeflow · Volcano · Kueue · JobSet · LeaderWorkerSet        |
|  +- KubeRay · MPI Operator · PyTorch Elastic                     |
|  +- Training Operator · KAI Scheduler (CNCF Sandbox)             |
+------------------------------------------------------------------+
|  Layer 2: GPU 设备管理                                             |
|  +- DRA (K8s 原生) · NVIDIA DRA Driver GPU                      |
|  +- NVIDIA GPU Operator · HAMi (GPU 虚拟化)                     |
|  +- MIG · Time-Slicing · MPS · ComputeDomains (NVLink 域)       |
|  +- Device Health Reporting · ResourceSlice                      |
+------------------------------------------------------------------+
|  Layer 1: 网络 & 存储 & 可观测性                                    |
|  +- Cilium / eBPF · Hubble · NetworkPolicy · Topology 感知       |
|  +- OpenTelemetry (毕业) · Prometheus · Kepler (GPU 功耗)        |
|  +- Dragonfly (模型分发) · Rook/Ceph · CSI                      |
+------------------------------------------------------------------+
|  Layer 0: 平台工程 (Platform Engineering)                          |
|  +- Backstage · Crossplane · Headlamp · Argo CD                 |
|  +- GPU Provisioning · Cost Gate · Shadow AI 治理               |
|  +- 5 个核心原则 (AI-Native / Multi-Persona / FinOps / 安全 / 可组合) |
+------------------------------------------------------------------+
```

### 2.2 CNCF AI 生态项目成熟度

| 层级 | 项目 | CNCF 状态 | 定位 | 2026 关键进展 |
|:-----|:-----|:---------:|:-----|:-------------|
| 训练编排 | **Kubeflow** | Graduated | ML 工作流平台 | Headlamp 插件发布 |
| 训练编排 | **Volcano** | Graduated | 批调度 AI 作业 | Headlamp 插件发布 |
| 训练编排 | **Kueue** | Incubating | 多租户批作业队列 | AI review 集成 (CodeRabbit) |
| 训练编排 | **KAI Scheduler** | ➡️ Sandbox | 大规模 GPU 集群调度 | KubeCon EU 2026 进入 Sandbox |
| 训练编排 | **JobSet** | ... | 分布式训练作业 | AI review 集成 |
| 推理服务 | **KServe** | Incubating | 模型推理服务平台 | 持续演进 |
| 推理服务 | **kgateway** | Incubating | AI 网关 | LFX mentorship 项目 |
| GPU 管理 | **HAMi** | ➡️ Incubating | GPU 虚拟化中间件 | 2026-07 晋升 |
| GPU 管理 | **NVIDIA GPU Op** | 厂商项目 | GPU Operator 自动化 | DRA Driver v25.12.0 |
| 安全 | **Confidential Cont.** | ➡️ Incubating | 机密容器 (TEE) | 2026-07 晋升 |
| 可观测性 | **OpenTelemetry** | Graduated | 可观测性标准 | Profiling Alpha + 4 方向 |
| 模型分发 | **Dragonfly** | Graduated | P2P 镜像/模型分发 | v2.5 GPU 加速 + HF 直连 |
| 平台工程 | **Backstage** | Graduated | 开发者门户 | AI-Native 规划 |

---

## 3. 调度与资源管理

### 3.1 Dynamic Resource Allocation (DRA) — GPU 调度进入新时代

#### 3.1.1 背景

DRA 是 K8s 社区过去 5 年最重要的调度架构变更。在 v1.26 作为 Alpha 引入，v1.34 GA，到 v1.36 持续深化。

#### 3.1.2 核心架构

| 组件 | 角色 | 说明 |
|:-----|:-----|:------|
| **DeviceClass** | 设备类别定义 | `gpu.nvidia.com` / `mig.nvidia.com` / `vfio.gpu.nvidia.com` |
| **ResourceSlice** | 每节点设备视图 | 自动发现，128 device/对象，超限自动 split Pool |
| **ResourceClaim** | Pod 资源声明 | 声明式指定 GPU 需求和约束 |
| **ResourceClaimTemplate** | 模板化（Deployment） | 每个 Pod 自动获得独立 claim |
| **CEL Selector** | 设备筛选表达式 | 品牌/显存/CUDA 算力的可编程选择 |

#### 3.1.3 DRA vs 传统 Device Plugin 关键差异

| 维度 | Device Plugin | DRA | 影响 |
|:-----|:-------------|:----|:------|
| GPU 分配 | 静态 Node-level 资源计数 | Claim-level 精确匹配 | 无需 nodeSelector/Affinity 复杂规则 |
| 异构选择 | 不支持 | CEL + `firstAvailable` | 品牌优先+异构回退成为原生能力 |
| 显存约束 | 不可编程 | `isGreaterThan(quantity("20Gi"))` | 声明式精确显存控制 |
| 设备健康 | Pod 状态 = Error | 可区分设备故障 vs 应用故障 | v1.36+ 新能力 |
| Time Slicing | 静态 ConfigMap | DRA Config 声明 `strategy: TimeSlicing` | 统一配置入口 |
| Cluster Autoscaler | 不支持 GPU 触发扩缩容 | 支持 GPU 短缺触发的节点扩容 | 未来能力 |

#### 3.1.4 关键实操场景 (来自 CNCF 实测)

| 场景 | DRA 方案 | 对比方案 |
|:-----|:---------|:---------|
| 🅰 两容器共享一 GPU | ResourceClaim + 两容器引用 | Device Plugin 需额外 hack |
| 🅱 A5000 首选 + T10 回退 | `firstAvailable` + CEL `productName` | 传统方案不可能 |
| 🅲 显存 > 20 GiB | CEL `capacity.memory.isGreaterThan("20Gi")` | 需 nodeSelector + 手动管理 |
| 🅳 GPU Time Slicing | `sharing.strategy: TimeSlicing` | 静态 ConfigMap 配置 |

#### 3.1.5 NVIDIA DRA Driver GPU 核心数据

| 属性 | 值 |
|:-----|:----|
| 版本 | v25.12.0 |
| K8s 版本 | v1.35+ |
| 支持的 GPU 属性 | architecture / brand / productName / cudaComputeCapability / memory |
| MIG 支持 | Alpha |
| ComputeDomains (多节点 NVLink) | 可选（本实验室禁用） |
| TimeSlicing | 支持（Feature Gate 开关） |
| Device 上限/ResourceSlice | 128（带 taint/counter 时为 64） |

### 3.2 Kueue — 多租户批调度作业队列

- **状态**: CNCF Incubating
- **定位**: 集群级多租户批调度，管理 GPU 配额的逻辑队列
- **2026 进展**: 已集成 AI CodeRabbit review，AI 贡献政策首批试点项目

### 3.3 KAI Scheduler — 万卡集群专用调度器

| 维度 | 数据 |
|:-----|:------|
| **状态** | CNCF Sandbox (2026-04 KubeCon EU) |
| **定位** | NVIDIA 内部大规模 GPU 集群调度引擎开源版 |
| **核心能力** | Gang scheduling + 预调度模拟 + 层次队列 DRF + 异步绑定 |
| **验证规模** | **10,000+ GPU** 集群 |
| **差异化** | 预调度模拟避免无谓的驱逐，调度器与集群解耦异步绑定 |
| **战略意义** | NVIDIA 将其路线图置于社区治理而非产品时间线 |

### 3.4 Workload-Aware Scheduling (v1.35+)

K8s v1.35 引入的**工作负载感知调度**——调度器可根据工作负载类型（AI 训练 vs 推理 vs Web 服务）和资源需求模式（CPU/GPU burst vs steady）做差异化调度决策。

v1.36 进一步推进了 **Pod-Level Resource Managers** (Alpha) 和 **In-Place Vertical Scaling** (Beta)，使推理服务的资源扩缩不再需要 Pod 重建。

---

## 4. GPU 编排与设备管理

### 4.1 NVIDIA GPU Operator

- **版本**: v26.3.1
- **功能**: GPU Driver 自动安装 + Container Runtime 配置 + Device Plugin/DRA
- **核心变更**: 支持 DRA 模式的 GPU 调度（需关闭 Device Plugin，启用 NVIDIA DRA Driver）

### 4.2 HAMi — GPU 虚拟化中间件

| 维度 | 数据 |
|:-----|:------|
| **状态** | ➡️ CNCF Incubating (2026-07) |
| **定位** | 多厂商 GPU 虚拟化中间件，不特定于 NVIDIA |
| **核心能力** | GPU 分片 / MPS / MIG 兼容 / 多厂商适配 |
| **与 DRA 的关系** | **互补** — DRA 是 OS 层资源标准化分配，HAMi 是实用主义 GPU 虚拟化 |
| **适用场景** | GPU 碎片化严重的多租户共享集群 |

### 4.3 GPU 共享策略对比

| 策略 | 隔离性 | 适用负载 | K8s 集成方式 | 成熟度 |
|:-----|:------|:---------|:------------|:------:|
| Time-Slicing | 弱（时间共享） | 推理 / 低优先级训练 | DRA Config / 设备插件 | ✅ GA |
| MIG (NVIDIA) | 强（硬件分区） | 多租户推理 | DRA / 设备插件 | ✅ GA |
| MPS (NVIDIA) | 中（上下文切换） | 小批量推理 | 设备插件 | ✅ GA |
| ComputeDomain (NVLink) | 强（内存隔离） | 多节点大规模训练 | DRA (Alpha) | 🟡 Alpha |
| HAMi | 中（软件虚拟化） | 推理 / 训练共享 | CRD + 设备插件 | ✅ Incubating |

### 4.4 GPU 集群排障实战

**典型案例**（来自 Adobe × Kubeflow × Cilium 实战，KubeCon India 2026 分享）：

| 排查层 | 方法 | 发现 |
|:-------|:-----|:------|
| GPU 诊断 | `nvidia-smi` + DCGM 指标 | 所有 GPU 利用率均匀低（~40%） |
| 网络吞吐 | Cilium `connectivity test` + Hubble | 部分 Pod 间通信丢包 + 高重传率 |
| 存储 IO | Kubeflow Pipeline IO wait | 无异常（训练数据已本地缓存） |
| 调度拓扑 | `topologySpreadConstraints` | 跨 Node 通信路径过长，NCCL all-reduce 等待 |
| **根因锁定** | Hubble 流分析 + Cilium NetworkPolicy 日志 | **Cilium NetworkPolicy 拦截了 NCCL 动态端口** |

**结论**: GPU 闲置不一定在 GPU 侧。Cilium NetworkPolicy 需显式允许 NCCL 动态端口（TCP 50000-51000）。Hubble 是 GPU 集群网络排障标准工具。**拓扑感知调度**是防止此问题的基础配置。

---

## 5. AI 训练基础设施

### 5.1 分布式训练编排矩阵

| 项目 | CNCF 状态 | 训练类型 | 特色 | 生产验证 |
|:-----|:---------:|:---------|:-----|:--------|
| **Kubeflow** | Graduated | 端到端 ML 工作流 | Pipeline + Notebook + Training Operator | 广泛 |
| **Volcano** | Graduated | 批调度 AI 作业 | Gang-scheduling + 队列管理 | 广泛 |
| **Kueue** | Incubating | 多租户队列调度 | 配额管理 + 优先级 | 中 |
| **JobSet** | ... | 分布式训练作业 | 多 Pod 组声明式管理 | 中 |
| **KAI Scheduler** | Sandbox | 大规模 GPU 集群 | 预调度模拟 + 10K GPU | 大规模 |
| **KubeRay** | Sandbox | Ray 集群 on K8s | Ray 训练/服务/调度的原生 K8s 集成 | 中 |
| **LeaderWorkerSet** | ... | 异构角色训练 | Leader/Worker 分离管理 | 早期 |

### 5.2 Kubeflow + Kubernetes AI 训练现状

- **Kubeflow + Headlamp 插件** (2026-07): 首个 AI/ML Operator 的 Headlamp 插件发布，Pipeline / Notebook / 训练作业可视化
- **Kubeflow + Cilium 排障** (2026-07): 生产级 GPU 集群排障案例，证明网络策略层对训练效率的关键影响
- **Training Operator**: 支持 PyTorch / TensorFlow / MPI / XGBoost 等框架的 K8s Operator

### 5.3 Volcano + Kueue 的差异化分工

| 维度 | Volcano | Kueue |
|:-----|:--------|:------|
| 调度级别 | Pod 级 | 作业（多 Pod）级 |
| 核心能力 | Gang scheduling + Fair-share | 多租户队列 + 配额 + 优先级 |
| 适用 | CPU/GPU 批处理+AI 训练 | 多团队共享集群的作业准入控制 |
| 集成 | 与 Kubeflow 深度集成 | 与 JobSet/Kueue 上层配合 |

### 5.4 KAI Scheduler — 属于社区的万卡集群调度器

KAI Scheduler 是 NVIDIA 将内部集群调度引擎贡献给 CNCF 的项目。其四个核心能力代表了大规模 AI 训练调度的最佳实践：

1. **Gang Scheduling**: 所有 GPU worker 同时满足条件才启动，避免资源死锁
2. **预调度模拟**: 在真正绑定前模拟调度结果，避免无谓的 Pod 驱逐
3. **层次队列 + DRF**: 多团队场景下保障公平性（Dominant Resource Fairness）
4. **异步绑定**: 调度决策与资源绑定的解耦，支持 10,000+ GPU 集群

---

## 6. AI 推理基础设施

### 6.1 推理服务栈

```text
用户请求
    |
    v
+--------------------------------------------+
|  AI Gateway                                |
|  +- kgateway (CNCF Incubating)             |
|  +- Envoy AI Gateway / Envoy Agent         |
|  +- Gateway API Inference Extension        |
+--------------------------------------------+
|  Model Serving Platform                    |
|  +- KServe (CNCF Incubating)                |
|  +- vLLM · TGI · Ollama                    |
|  +- NVIDIA NIM · Dynamo                    |
|  +- llm-d / AIBrix                         |
+--------------------------------------------+
|  Model & Cache Delivery                    |
|  +- Dragonfly (P2P, CNCF Graduated)       |
|  +- Hugging Face / ModelScope              |
+--------------------------------------------+
|  K8s 调度层                                 |
|  +- DRA (GPU 分配) / Cluster Autoscaler     |
|  +- HPA / VPA / In-Place Resize            |
|  +- Topology-Aware Scheduling              |
+--------------------------------------------+
```

### 6.2 Gateway API Inference Extension

- **状态**: K8s SIG Network 推动中，微软/Google 发起
- **定位**: 为 AI 推理流量提供标准化的 K8s 网关接口
- **价值**: 推理特定路由（模型版本/改写/缓存）→ 标准 K8s API，无需专有网关

### 6.3 Goodput vs Throughput：LLM Serving 效率基准

**来源**: CNCF Blog Jul 20 — Akamas

| 指标 | 定义 | 问题 |
|:-----|:-----|:------|
| **Throughput** | 原始每秒请求数 | 容易通过降低精度/缩短输出来提升 |
| **Goodput** | 满足 SLO 的每秒请求数 | 包含首 token 延迟 + token 间延迟 + 质量约束 |
| **Goodput Ratio** | Goodput / Throughput | LLM serving 真实效率衡量 |

**运维影响**: 推理优化的目标应从"推高吞吐"转向"在满足 SLO 前提下最大化 Goodput"。这对 K8s 推理集群的 HPA/VPA 策略设计有直接影响。

### 6.4 推理场景的 DRA 价值

| 推理场景 | DRA 能力 | 传统方案痛点 |
|:---------|:---------|:------------|
| 模型热迁移 | In-Place Pod Resize (Beta v1.36) | 需 Pod 重建 → 连接断开 |
| 推理扩缩容 | Cluster Autoscaler 基于 GPU 短缺触发扩容 | 需手动标注 GPU 节点 |
| 多模型推理 | ResourceClaim 独立声明 → Pod 级隔离 | 节点级 GPU 资源竞争 |
| 推理 SLO 保障 | DeviceClass 按 GPU 型号选择 | 需 nodeSelector 硬约束 |

---

## 7. AI 网络与可观测性

### 7.1 Cilium + eBPF：GPU 集群网络的标配

**关键发现**: Cilium NetworkPolicy 可导致 NCCL 通信降级——60% GPU 闲置的根因可能不是 GPU 本身，而是网络策略拦截了 NCCL side-channel 通信。

| 实践 | 说明 |
|:-----|:------|
| NCCL 动态端口范围 | 建议显式允许 TCP 50000-51000 |
| Hubble 作为诊断工具 | `hubble observe --namespace kubeflow --drop` 快速定位丢包 |
| 拓扑感知调度 | `topologySpreadConstraints` + nodeAffinity 确保 GPU 通信最短路径 |
| 通用模式 | 任何 CNI 策略 + 任何分布式框架都可能遇到相同问题 |

### 7.2 OpenTelemetry：AI 可观测性支柱

| 维度 | 状态 | AI 场景价值 |
|:-----|:-----|:------------|
| Metrics + Traces + Logs | ✅ 毕业 | 分布式训练追踪 |
| **Profiling** | 🟡 Alpha | 补齐 GPU 性能分析缺口 |
| **CI-CD 可观测性** | 🔄 发展中 | 模型部署管线端到端追踪 |
| **Agent 追踪** | 🔄 发展中 | Agent 工作流可观测性 |

**OTel 采用反模式**: "不要包装 OpenTelemetry"——OTel API 本身就是抽象层，在其上再加抽象层导致语义约定丢失、标准集成破坏、维护债务增加。

### 7.3 Kepler：GPU/能耗可观测性

- **定位**: CNCF 项目，GPU/NIC 独立功耗追踪
- **AI 场景**: AI 集群功耗可观测性——每个 Pod 级的 GPU 功耗归因
- **2026 进展**: 重新架构，提升功耗精度

### 7.4 Dragonfly：AI 模型分发

| 版本 | 核心特性 | AI 场景价值 |
|:-----|:---------|:------------|
| v2.5.0 | **Hugging Face + ModelScope 直连** | AI 模型 P2P 分发，节省 95%+ 跨域带宽 |
| v2.5.0 | GPU 加速 P2P | 分布式训练环境模型/数据集预加载 |

---

## 8. AI Agent 基础设施

### 8.1 Agent-Substrate — K8s Agent 运行时新范式

| 维度 | 说明 |
|:-----|:------|
| **状态** | K8s SIG 推动，2026 H1 密集产出 |
| **核心设计** | "Agent 不是 Pod"——多个 Agent 共享一个 Worker Pod 进程模型 |
| **密度** | 6 agents 共享 1 Worker Pod |
| **差异化** | 传统沙箱隔离不足，Agent 需要 K8s 原生运行时安全 |
| **AI Review** | agent-sandbox 使用 CodeRabbit + `needs-human-review` 标签 |

### 8.2 Agent 平台工程

**CNCF 2026-07 核心论点**: 平台工程的核心任务从"抽象基础设施复杂性"扩展到"抽象 Agent 编排复杂性"。Agent 需要：

| 能力 | 实现方式 |
|:-----|:---------|
| GPU/TPU 调度 | DRA + Kueue + KAI Scheduler |
| LLM API 网关 | Gateway API Inference Extension / kgateway |
| 知识库集成 | Vector DB + MCP Protocol |
| 资源配额与访问控制 | K8s RBAC + ResourceQuota + LimitRange |
| Agent 可观测性 | OTel Agent 追踪 + NGINX Agent 安全溯源 |
| 成本追踪 | Kepler + FinOps 仪表盘 |

### 8.3 Agent Gateway

| 项目 | 定位 | 来源 |
|:-----|:-----|:------|
| **agentgateway** | Agent 通信网关 | Agentic AI Foundation (AAIF) |
| **Envoy AI Gateway** | Envoy 扩展的 AI 推理代理 | CNCF 生态 |
| **kgateway** | K8s AI 网关 | CNCF Incubating |
| **MCP Gateway** | 模型上下文协议网关 | 平台工程 2.0 |

---

## 9. 平台工程 2.0

### 9.1 范式演进：1.0 → 2.0

| 维度 | 1.0 (当前) | 2.0 (演进中) | 对 AI 的影响 |
|:-----|:-----------|:-------------|:------------|
| **服务对象** | 开发者 | 开发者 + ML/DS + FinOps + 安全 + **AI Agent** | 平台需治理 Agent |
| **GPU 管理** | 手工/脚本 | 一等公民：GPU 分配 + 模型 serving + MCP Gateway | DRA + vLLM 集成 |
| **FinOps** | 事后报表 | **预部署成本门禁** + 实时成本归因 | 预算管控前置 |
| **安全** | Shift-Left | 运行时下沉 + **Shadow AI 治理** | 模型投毒/推理泄露 |
| **架构** | 单体平台 | 模块化可组合 (CNCF 200+ 项目) | 灵活替换组件 |

### 9.2 五项核心原则

1. **AI-Native**: GPU/TPU 一级支持 + MCP 网关 + Agentic Guardrails
2. **Multi-Persona**: 非人类消费者（AI Agent）的访问/作用域/治理
3. **Embedded FinOps**: 预部署成本门禁 + 实时成本归因 + 人人成本感知
4. **Security Shifts Down**: Shadow AI 治理 + 提示注入防护 + 推理审计
5. **Composable by Design**: API-first 可互换构件

### 9.3 平台成熟度模型

| 级别 | 描述 | AI 能力特征 |
|:-----|:-----|:------------|
| L1 | 探索期 | GPU 手动分配，模型部署靠脚本 |
| L2 | 试点期 | GPU Operator 部署，单场景推理 on K8s |
| L3 | 推广期 | DRA + Kueue 调度，多模型推理平台 |
| L4 | 融合期 | Agent 治理 + FinOps 成本门禁 + 自动扩容 |
| L5 | 引领期 | 可组合平台 + AI 原生运维 + 社区标准贡献 |

### 9.4 Headlamp — K8s 统一操作面

2026 H1 的 5 个插件同期发布标志 Headlamp 从 K8s Dashboard 替代品向统一操作平面的跃迁：

| 插件 | 发布时间 | AI 关联 |
|:-----|:---------|:--------|
| Volcano | Jun 25 | AI 批调度可视化 |
| Kubeflow | Jul 13 | **首个 AI/ML Operator 插件** |
| Cluster API | Jun 25 | 集群声明式管理 |
| Knative | Jun 25 | Serverless 工作负载 |
| Karpenter | 2025 | GPU 节点自动伸缩 |

---

## 10. 行业标准与合规

### 10.1 Kubernetes AI Conformance Program

| 维度 | 数据 |
|:-----|:------|
| **发起** | K8s SIG Architecture + NVIDIA |
| **认证平台** | 18 → **31**（发布后 6 个月增长 72%） |
| **v1.35 新增** | Agentic workflow 支持 + In-Place Pod Resize (inference serving) |
| **定位** | AI Ready K8s 的功能需求定义 & 环境间 API 兼容性验证 |
| **价值** | 避免"各厂商 AI 平台拿 K8s 包装"造成的锁定 |

### 10.2 AI 贡献政策

K8s 项目发布的首个 AI 贡献政策（2026-06），成为云原生项目治理模板：

| 原则 | 具体规则 |
|:-----|:---------|
| **透明度优先** | PR 必须声明 AI 辅助 |
| **人类问责** | AI 不可列为共同作者，CLA 检查也覆盖 co-author |
| **仅限人类交互** | AI 不能代回复评审意见 |
| **验证责任** | 必须验证 AI 生成的内容（理解"为什么"而非仅"能工作"） |

### 10.3 Confidential Containers (CoCo)

| 维度 | 数据 |
|:-----|:------|
| **状态** | ➡️ CNCF Incubating (2026-07) |
| **核心技术** | Kata Containers + TEE (Intel TDX/AMD SEV-SNP/Intel SGX) + KBS |
| **AI 价值** | 多租户 GPU 集群中训练数据/模型权重的机密性保护 |
| **设计原则** | data-in-use protection — 内存中数据不受主机/管理员/云厂商访问 |

### 10.4 AI Gateway Working Group

- **成立时间**: 2026-06
- **发起方**: 微软 + Google
- **定位**: 定义 AI 推理的标准网关 API（与 Gateway API 配合）
- **预期产出**: 推理特定路由 / 模型版本 / 推理缓存 / 请求改写标准

### 10.5 AI 工作负载主权部署 (Sovereign AI)

CNCF 2026-07 提出 AI 工作负载的五个主权要素：

| 要素 | AI 场景关注点 |
|:-----|:-------------|
| **Operational Autonomy** | 训练中断/恢复的自主控制 |
| **Compliance** | 训练数据的地域限制 |
| **Auditability** | 模型推理审计日志 |
| **Portability** | 模型+数据跨云迁移能力 |
| **Resilience** | 训练检查点/故障切换 |

---

## 11. 战略总结与趋势判断

### 11.1 五个架构级判断

| # | 判断 | 证据 | 时间线 |
|:-|:-----|:------|:------|
| **1** | **DRA 将在 2 年内取代 Device Plugin 成为 GPU 调度标准** | NVIDIA DRA Driver 进 K8s SIG-Node + CEL 可编程选择器 + Cluster Autoscaler 联动 | 2026-2028 |
| **2** | **K8s + Agent 运行时融合是下一波架构变革** | Agent-substrate (6:1 共享) + Agent Gateway + AAIF + Agent 追踪 → Agent 成为 K8s 一等公民 | 2026 H2 |
| **3** | **平台工程正被 AI 重构 (PE 2.0)** | 5 项原则系统化 + CNCF PE TCG 追踪 + 服务对象扩展至 Agent | 2026-2027 |
| **4** | **GPU 可观测性从'有'到'优'** | Kepler 功耗追踪 + OTel Profiling + Goodput Ratio + Hubble NCCL 排障，构成 GPU 观测三件套 | 2026 H1 已启动 |
| **5** | **NVIDIA 从'提供 GPU'到'贡献 K8s 标准'的战略转型** | DRA Driver 上游化 + KAI Scheduler 开源 + $4M CI GPU 捐赠 + K8s AI Conformance 推动 | 2026 已确立 |

### 11.2 项目采纳路线图

```text
现在 (2026 H1)                   近期 (2026 H2-2027 H1)          远期 (2027-2028)
----------------------------+  ----------------------------+  ----------------------------+
DRA GA                       ->  DRA MIG + ComputeDomain      ->  DRA Cluster Autoscaler 联动
NVIDIA DRA Driver v25.12     ->  TimeSlicing 标准化           ->  Device Plugin 退役计划
Kueue Incubating             ->  Kueue + KAI 融合/互补        ->  统一批调度 API
HAMi Incubating              ->  HAMi × DRA 正式集成          ->  GPU 虚拟化标准
Agent-substrate Alpha        ->  Agent Gateway GA             ->  Agent 成为 K8s 原生资源
Confidential Containers Inc  ->  GPU Confidential Computing   ->  多租户机密训练标准
AI Conformance 31            ->  50+ 认证平台                  ->  AI Ready K8s 成为必选项
```

### 11.3 需要持续关注的风险

| 风险 | 说明 | 缓解 |
|:-----|:------|:------|
| **DRA 采纳速度低于预期** | 现有 Device Plugin 生态庞大，生产环境迁移成本高 | 关注 NVIDIA 推动力度 + 社区 LTS 计划 |
| **AI Agent 基础设施碎片化** | AAIF / CNCF / K8s SIG 三股力量并行 | 跟踪标准收敛节点 |
| **GPU 机密计算标准模糊** | CoCo 提供容器级 TEE，GPU 级 in-use protection 仍需完善 | 关注 Intel TDX / AMD SEV 的 GPU 集成 |
| **NVIDIA 单一依赖** | K8s for AI 的 NVIDIA GPU 事实垄断 | 关注 AMD/Habana/Intel GPU 的 DRA 实现 |
| **AI Conformance 成为准入门槛** | 可能被大厂控制，形成事实标准壁垒 | 关注社区治理透明度和开放度 |

### 11.4 跟踪计划

| 跟踪项 | 频率 | 数据来源 | 下次更新 |
|:-------|:-----|:---------|:---------|
| K8s 新版本 AI 特性 | 每月 | K8s Blog / KEPs | v1.37 发布 |
| DRA 生态进展 | 双周 | NVIDIA DRA Driver / K8s SIG-Node | - |
| KubeCon Japan 2026 信息 | 一次性 | 7/28-30 横滨 | 本周 |
| CNCF AI Infra SIG 动态 | 双周 | CNCF Japan Chapter | 10/1 首次 Meetup |
| KAI Scheduler / Kueue | 双周 | CNCF Sandbox/Incubating | - |
| Agent Infrastructure | 双周 | K8s SIG / AAIF | - |
| 生产部署案例 | 每月 | CNCF Case Studies / KubeCon | - |

### 11.5 对我方的技术关注建议

根据当前 AI 基础设施技术栈布局，建议重点关注：

| 优先级 | 领域 | 对我方价值 | 投入建议 |
|:------:|:-----|:-----------|:---------|
| **P0** | **DRA** — GPU 调度架构级变革 | 直接影响 GPU 集群的资源利用率和运维模型 | 跟踪 DRA 实操落地，规划迁移路线 |
| **P0** | **KAI Scheduler** — 万卡集群调度 | NVIDIA 内部调度器开源，与超节点集群直接相关 | 评估在超节点集群中的集成可行性 |
| **P1** | **Agent Infrastructure** — Agent 运行时 | Agent 化是 AI 基础设施的下一个浪尖 | 建立 Agent-substrate + Agent Gateway 试点知识 |
| **P1** | **Cilium + Hubble GPU 排障** | 生产级 GPU 利用率偏低的第一排障工具 | 预研 Hubble 在训练集群中的部署方案 |
| **P1** | **Platform Engineering 2.0** | 平台团队面向 AI 的演进路线图 | 制定 AI-Native 平台架构演进计划 |
| **P2** | **Confidential Containers + GPU** | 多租户机密训练 | 跟踪 GPU TEE 标准进展 |
| **P2** | **AI Conformance** | 未来 AI 基础设施的准入门槛 | 确保内部集群通过验证 |

---

## 12. 参考资料

### 12.1 核心来源

| # | 标题 | 来源 | 日期 |
|:-|:-----|:------|:----|
| [1] | [The future of AI is community driven and open](https://www.cncf.io/blog/2026/07/23/the-future-of-ai-is-community-driven-and-open/) | CNCF Blog (NVIDIA) | 2026-07-23 |
| [2] | [Understanding Dynamic Resource Allocation in Kubernetes](https://www.cncf.io/blog/2026/07/01/understanding-dynamic-resource-allocation-in-kubernetes/) | CNCF Blog (Ambassador) | 2026-07-01 |
| [3] | [Evolving Platform Engineering for AI-Native Workloads](https://www.cncf.io/blog/2026/07/06/evolving-platform-engineering-for-ai-native-workloads/) | CNCF Blog (VMware/Broadcom) | 2026-07-06 |
| [4] | [When Kubeflow meets Cilium: Debugging 60% idle GPUs](https://www.cncf.io/blog/2026/07/23/when-kubeflow-meets-cilium-debugging-60-idle-gpus-in-kubernetes/) | CNCF Blog (Adobe) | 2026-07-23 |
| [5] | [Open source maintainership in the age of AI](https://kubernetes.io/blog/2026/06/26/open-source-maintainership-in-the-age-of-ai/) | K8s Blog (Red Hat) | 2026-06-26 |
| [6] | [Launch of the AI Infra SIG under CNCF Japan chapter](https://www.cncf.io/blog/2026/07/23/launch-of-the-ai-infra-sig-under-the-cncf-japan-chapter-first-meetup-and-call-for-speakers/) | CNCF Blog | 2026-07-23 |
| [7] | [Why goodput matters more than throughput for LLM serving](https://www.cncf.io/blog/2026/07/20/why-goodput-matters-more-than-throughput-for-llm-serving/) | CNCF Blog (Akamas) | 2026-07-20 |
| [8] | [Platform engineering for the agentic enterprise](https://www.cncf.io/blog/2026/07/21/platform-engineering-for-the-agentic-enterprise-managing-applications-resources-and-ai-agents/) | CNCF Blog (WSO2) | 2026-07-21 |
| [9] | [Federating clusters for zero-downtime Kubernetes](https://www.cncf.io/blog/2026/07/27/federating-clusters-for-zero-downtime-kubernetes/) | CNCF Blog | 2026-07-27 |
| [10] | [Confidential Containers becomes a CNCF Incubating project](https://www.cncf.io/blog/2026/07/22/confidential-containers-becomes-a-cncf-incubating-project/) | CNCF Blog | 2026-07-22 |

### 12.2 关联知识

- `knowledge/01_survey/cloud-native/` — 持续云原生动态跟踪（含 K8s v1.35/1.36 完整特性、DRA 深度实操、KubeCon 2026 信息）
- `knowledge/01_survey/cluster-training/` — 集群训练基础设施
- `knowledge/01_survey/llm-trends/` — LLM 推理与服务趋势
- `knowledge/07_industry-research/03_server/2026-07-29-nvidia-vera-cpu-olympus-deep-analysis-dup1.md` — NVIDIA Vera CPU 深度分析（§7 NVLink-C2C CPU-GPU 一致性域）
- 本报告跟踪框架：`knowledge/01_survey/cloud-native/TRACKING.md`

### 12.3 开源项目链接

| 项目 | 链接 |
|:-----|:------|
| DRA Driver GPU (NVIDIA) | github.com/NVIDIA/dra-driver-gpu |
| KAI Scheduler | github.com/NVIDIA/kai-scheduler |
| Kueue | github.com/kubernetes-sigs/kueue |
| JobSet | github.com/kubernetes-sigs/jobset |
| HAMi | github.com/Project-HAMi/HAMi |
| KServe | github.com/kserve/kserve |
| KubeRay | github.com/ray-project/kuberay |
| kubeflow-cilium-lab | github.com/ram2valar/kubeflow-cilium-lab |

---

## 变更记录

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-07-28 | v1.0 | 首次创建，K8s AI 基础设施实践全覆盖（含 DRA GA、KAI Scheduler、Agent Infrastructure、PE 2.0） |
