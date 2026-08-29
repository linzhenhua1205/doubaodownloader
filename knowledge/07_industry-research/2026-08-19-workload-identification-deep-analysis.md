# 工作负载识别（Workload Identification）— 从遥测到决策的完整方法论

> **元信息**: 深度分析 · 状态: 完成 · 覆盖: 数据中心/AI 集群工作负载识别的方法论、算法、工程链路与生产实证
> **适用范围**: AI 算力基础设施规划 / 集群调度优化 / 容量规划 / 成本治理 / 可观测性建设

---

## 📑 目录

- [1. 引言与范围](#1-引言与范围)
- [2. 第一性原理：为什么识别是基础设施优化的起点](#2-第一性原理为什么识别是基础设施优化的起点)
  - [2.1 问题的本质：高维连续遥测 → 低维可决策标签](#21-问题的本质高维连续遥测--低维可决策标签)
  - [2.2 核心矛盾：利用率与 QoS 的张力](#22-核心矛盾利用率与-qos-的张力)
  - [2.3 识别 ≠ 预测 ≠ 调度：三者分层](#23-识别--预测--调度三者分层)
  - [2.4 经典量化基线：为什么"平均利用率"这么低](#24-经典量化基线为什么平均利用率这么低)
- [3. 识别对象：工作负载的维度体系（MECE）](#3-识别对象工作负载的维度体系mece)
  - [3.1 业务形态维度](#31-业务形态维度)
  - [3.2 资源画像维度](#32-资源画像维度)
  - [3.3 时间模式维度](#33-时间模式维度)
  - [3.4 AI 负载细分维度](#34-ai-负载细分维度)
  - [3.5 SLA/优先级维度](#35-sla优先级维度)
- [4. 识别方法论：从遥测到决策的完整链路](#4-识别方法论从遥测到决策的完整链路)
  - [4.1 遥测采集层（四级数据源）](#41-遥测采集层四级数据源)
  - [4.2 特征工程：把时序变成判别信号](#42-特征工程把时序变成判别信号)
  - [4.3 识别算法谱系](#43-识别算法谱系)
  - [4.4 架构设计：离线 vs 在线、粒度与闭环](#44-架构设计离线-vs-在线粒度与闭环)
- [5. 生产级实证：业界大规模工作负载表征成果](#5-生产级实证业界大规模工作负载表征成果)
  - [5.1 微软第一方工作负载大规模表征（2024）](#51-微软第一方工作负载大规模表征2024)
  - [5.2 阿里 ServeGen：LLM 推理负载表征（NSDI'26）](#52-阿里-servegenllm-推理负载表征nsdi26)
  - [5.3 Google Borg trace 无监督聚类（2.4TB）](#53-google-borg-trace-无监督聚类24tb)
  - [5.4 深度推荐系统跨栈表征](#54-深度推荐系统跨栈表征)
  - [5.5 实证结论汇总](#55-实证结论汇总)
- [6. AI 集群场景深潜：训练/推理识别与调度闭环](#6-ai-集群场景深潜训练推理识别与调度闭环)
  - [6.1 GPU 利用率现实：识别是降本前提](#61-gpu-利用率现实识别是降本前提)
  - [6.2 训练 vs 推理：可识别的特征差异](#62-训练-vs-推理可识别的特征差异)
  - [6.3 识别驱动的调度：MoE / PD 分离 / 弹性扩缩容](#63-识别驱动的调度moe--pd-分离--弹性扩缩容)
  - [6.4 遥测基建：双轨融合与可观测性栈](#64-遥测基建双轨融合与可观测性栈)
- [7. 工程落地框架](#7-工程落地框架)
  - [7.1 设计决策树](#71-设计决策树)
  - [7.2 指标体系](#72-指标体系)
  - [7.3 常见陷阱](#73-常见陷阱)
  - [7.4 最小可行落地路径（MVP）](#74-最小可行落地路径mvp)
- [8. 挑战与趋势](#8-挑战与趋势)
- [9. 结论与行动建议](#9-结论与行动建议)
- [参考文献](#参考文献)
- [变更记录](#变更记录)

---

## 1. 引言与范围

**工作负载识别（Workload Identification / Characterization）** 指：从系统运行时遥测数据（利用率、延迟、吞吐、事件序列等）出发，识别、分类并量化刻画"当前/历史在这台机器、这个集群上跑的是什么负载、以什么模式在跑"的过程。

它与三个相邻概念严格区分：

| 概念 | 回答的问题 | 时间指向 | 输出 |
|:-----|:-----------|:--------:|:-----|
| **负载识别**（本文） | 这是什么负载？ | 现在/过去 | 类别标签 + 特征画像 |
| **负载预测** | 接下来负载会怎样？ | 未来 | 数值/分布预测 |
| **负载调度** | 负载放哪里跑最合适？ | 决策 | 放置/优先级动作 |

三者的依赖关系：**识别是预测与调度的前置条件**——不认识负载类型，就无法选择正确的预测模型与调度策略。

**为什么现在值得系统性研究**：AI 集群（万卡级 GPU 集群）的单卡成本数百万元级、供电散热约束强、利用率与性能表现高度依赖负载形态与调度匹配 [来源: 本知识库 AI 基础设施专题]。负载识别从"拍脑袋分类"升级为"数据驱动的自动分类"，是利用率提升、成本治理、SLA 保障的第一块地基。本文覆盖：第一性原理 → 识别维度 → 方法链路 → 生产实证 → AI 场景落地 → 工程框架。

> 与知识库已有文档的关系：本文聚焦"识别运行时负载"，`18_methodology-framework/2026-07-13-workload-estimation-methodology.md` 聚焦"评估软件开发工作量"，两者名字相近但对象完全不同（运行时负载 vs 开发工作量），仅在"方法论分层"层面可互参。

---

## 2. 第一性原理：为什么识别是基础设施优化的起点

### 2.1 问题的本质：高维连续遥测 → 低维可决策标签

从信息论视角看，工作负载识别是一个**有损压缩问题**：

```text
Input:    High-dim telemetry stream (CPU/MEM/IO/NET/GPU/PWR x time)
              |  noise + redundancy + high-dim (dozens of metrics, sec-level)
              v
Target:   Low-dim semantic labels (train / infer / batch / interactive / ...)
              |  executable & interpretable
              v
Action:   Scheduling / capacity planning / pricing / RAS intervention
```

压缩的**不可逆性**决定了识别的根本局限：任何标签体系都会丢失细节。因此识别的设计核心不是"追求完美分类"，而是**保证标签粒度与决策需求匹配**——为定价做的识别不需要区分 prefill/decoding，为调度做的识别必须区分。

### 2.2 核心矛盾：利用率与 QoS 的张力

基础设施优化的核心矛盾是：**资源越被充分复用，负载间干扰越大，QoS 越难保障**。识别负载的价值正是在这个矛盾点上：

| 决策场景 | 不识别负载的后果 | 识别负载后的收益 |
|:---------|:-----------------|:-----------------|
| 混部/超卖 | 干扰不可控，在线服务延迟劣化 | 只让"兼容"的负载共置（批处理+在线） |
| 弹性扩缩容 | 按固定阈值触发，反应滞后 | 按负载类型预测性伸缩 |
| 容量规划 | 按峰值叠加，过度配置 | 按画像聚合，统计复用 |
| 定价 | 按规格统一计价，优质客户流失 | 按特征差异化定价 |

### 2.3 识别 ≠ 预测 ≠ 调度：三者分层

```text
Layer 3  Scheduling/Orchestration (decision)  placement, priority, scaling, migration
Layer 2  Prediction               (forward)   future load value / distribution / class
Layer 1  Identification           (cognition) current load class + profile   <-- this doc
Layer 0  Telemetry                (perception) raw metric collection
```

每一层都依赖下层。识别层是"认知层"，负责把感知层的数据转化为语义；这一层的质量直接决定上层决策的天花板。

### 2.4 经典量化基线：为什么"平均利用率"这么低

| 数据点 | 数值 | 条件 | 来源 |
|:-------|:-----|:-----|:-----|
| 典型服务器平均利用率 | **10–30%** | 2007 年 Google 研究，峰值设计 vs 平均运行的巨大落差 | Barroso & Hölzle, "The Case for Energy-Proportional Computing", IEEE Computer, 2007 |
| Google 生产集群平均 CPU 利用率 | **~60%** | Borg 系统通过准入控制+紧打包+超卖+共享实现的高利用率 | Verma et al., "Large-scale cluster management at Google with Borg", EuroSys 2015 |
| Google 单集群规模 | 数万台机器 / 数十万作业 | 负载异构性极大，识别是调度的前提 | 同上 |

**第一性原理推论**：从 10–30% 到 60%，Google 用"调度+共享"做到了 2–6 倍的利用率提升，而这一切的前提是**Borg 能理解每个作业的资源特征**（Borg 论文明确将"负载特征感知"列为高利用率的关键机制之一 [来源: Verma et al., EuroSys'15]）。利用率不是靠硬件堆出来的，是靠"认知+调度"挤出来的——这正是识别战略价值的量化锚点。

---

## 3. 识别对象：工作负载的维度体系（MECE）

工作负载不是一维的。一个完整的识别体系必须覆盖以下互斥且穷尽的五个维度：

### 3.1 业务形态维度

| 形态 | 典型特征 | 识别信号 | 典型调度策略 |
|:-----|:---------|:---------|:-------------|
| 在线服务 | 延迟敏感、请求驱动、长驻 | 持续低 CPU、高 QPS、尾延迟敏感 | 独占/低超卖、就近放置 |
| 批处理 | 吞吐导向、可抢占、有时限 | 高 CPU/GPU 利用、长任务、可中断 | 混部、夜间填充、抢占 |
| 流式处理 | 持续数据摄入、窗口计算 | 稳定吞吐、内存/IO 波动 | 数据局部性优先 |
| 交互式 | 用户触发、短时突发 | 短请求、高并发、低利用率 | 快速扩缩容 |

### 3.2 资源画像维度

| 画像 | 判别特征（典型值） | 识别要点 |
|:-----|:------------------|:---------|
| CPU 密集 | CPU% 高、内存/IO 低 | 看 CPU 时间占比 vs 等待占比 |
| 内存密集 | 内存占用高、换页频繁 | 看 RSS、page fault、swap |
| IO 密集 | 磁盘吞吐高、IO 等待高 | 看 iowait、IOPS、带宽 |
| 网络密集 | 网卡吞吐高、小包多 | 看 pps、带宽、重传率 |
| GPU 密集 | SM 占用高、显存压力大 | 看 DCGM SM 利用率、显存带宽 |
| 混合型 | 多维同时高 | 聚类分析才能分离 |

### 3.3 时间模式维度

| 模式 | 数学特征 | 识别方法 |
|:-----|:---------|:---------|
| 稳态 | 均值方差稳定，自相关平稳 | 统计检验（ADF） |
| 周期性 | 频谱有显著峰值（日/小时） | FFT / 自相关函数 |
| 突发性 | CV >> 1，间歇尖峰 | 变点检测、极值分析 |
| 潮汐性 | 长期趋势+周期叠加 | 时序分解（STL） |
| 一次性 | 事件驱动、无规律 | 异常检测 |

### 3.4 AI 负载细分维度

AI 集群场景特有的细分（详见第 6 章）：

| 细分 | 特征 | 识别意义 |
|:-----|:-----|:---------|
| 训练 vs 推理 | 训练=长时占卡+吞吐导向；推理=短请求+延迟敏感 | 调度、分时、定价完全不同 |
| 语言/多模态/推理模型 | 输入输出长度分布差异显著 | prefill/decoding 资源配比 |
| prefill 密集 vs decoding 密集 | 计算型 vs 访存型阶段 | PD 分离决策 |
| 微调 vs 全量训练 | 显存占用、时长 | 抢占优先级 |

### 3.5 SLA/优先级维度

| 等级 | 特征 | 识别价值 |
|:-----|:-----|:---------|
| 金级（延迟敏感） | 严格 P99 目标 | 永不混部、优先保障 |
| 银级 | 中等目标 | 受限混部 |
| 铜级（可抢占） | 尽力而为 | 作为混部填充资源 |

> **MECE 自检**：五个维度分别回答"什么业务形态（why）、消耗什么资源（what）、什么时间模式（when）、什么 AI 阶段（which）、什么服务等级（how much）"，互不重叠且覆盖了识别的全部决策输入。

---

## 4. 识别方法论：从遥测到决策的完整链路

### 4.1 遥测采集层（四级数据源）

| 层级 | 工具/标准 | 关键指标 | 粒度 | 采集成本 |
|:-----|:----------|:---------|:-----|:---------|
| 硬件级 | BMC/IPMI/Redfish | 功耗、温度、风扇、传感器 | 秒~分钟 | 低（带外） |
| GPU 级 | NVIDIA DCGM / NVML | SM 利用率、显存带宽、温度、功耗、NCCL 通信量 | 100ms~s | 低 |
| OS 级 | /proc、perf、eBPF、sar | CPU/内存/IO/网络、系统调用、阻塞事件 | ms~s | 中（eBPF 低开销） |
| 容器/K8s 级 | node_exporter、cAdvisor、Kube-state-metrics | 容器资源用量、Pod 状态 | 15s~1min | 低 |
| 应用级 | OpenTelemetry、vLLM metrics、NCCL exporter | 请求特征、prefill/decoding 耗时、集合通信模式 | 请求级 | 中 |

**选型原则**：识别精度与采集成本存在权衡——硬件级指标只能区分"忙不忙"，应用级指标才能区分"在忙什么"。生产实践推荐**双轨融合**：带外（BMC/DCGM）保证全覆盖与故障场景可用，带内（eBPF/OTel）保证细粒度与语义（详见 6.4 与本库遥测专题）。

### 4.2 特征工程：把时序变成判别信号

原始遥测是时序数据，直接喂给分类器效果差。核心特征族：

| 特征族 | 典型特征 | 判别力 | 计算成本 |
|:-------|:---------|:------:|:---------|
| 统计特征 | 均值、方差、P50/P95/P99、偏度、峰度 | 中 | 极低 |
| 时序特征 | 自相关系数、CV、趋势斜率、变点数 | 高 | 低 |
| 频谱特征 | FFT 主频、周期强度、谱熵 | 高（周期模式） | 中 |
| 分布特征 | 直方图形状、拟合分布参数（Pareto/Exp） | 高（长度类） | 中 |
| 组合特征 | 资源利用率比值（CPU/IO、GPU/内存） | 高（画像分离） | 低 |

> **ServeGen 实证**：LLM 请求的输入长度分布可用 **Pareto + Log-normal 混合**建模（长尾），输出长度分布可用 **Exponential** 建模（无记忆性）[来源: Xiang et al., "ServeGen", arXiv:2505.09999, NSDI'26]。这组先验分布可以直接作为特征工程的先验注入。

### 4.3 识别算法谱系

| 算法族 | 代表方法 | 适用场景 | 优点 | 缺点 |
|:-------|:---------|:---------|:-----|:-----|
| 规则/阈值 | 专家规则、决策表 | 冷启动、可解释性优先 | 透明、零训练 | 脆弱、难维护 |
| 无监督聚类 | K-means、GMM、DBSCAN、层次聚类 | 无标签冷启动、画像发现 | 无需标注、可发现新类别 | 簇数难定、结果需人工解读 |
| 监督分类 | RF、XGBoost、SVM | 有标签后精分类 | 精度高、可解释（SHAP） | 依赖标注质量 |
| 深度时序 | LSTM、Transformer、TSC 模型 | 复杂时序模式、序列分类 | 自动特征学习、精度上限高 | 数据量大、可解释性差 |
| 在线学习 | 增量聚类、ADWIN 漂移检测 | 负载演化场景 | 适应概念漂移 | 实现复杂 |

**生产实证（无监督聚类）**：IEEE CLOUD 2023 用无监督聚类框架分析 Google **2.4TB、8 个 Borg cell** 的负载 trace，基于 CPU/内存用量质心与波动特征聚类，得到 7 条关键观察（作业类型多样性、资源利用模式、分配效率等）[来源: Suleiman et al., "A Framework for Characterizing Very Large Cloud Workload Traces with Unsupervised Learning", IEEE CLOUD 2023]。**结论：无监督聚类是"无标签冷启动"场景的默认起点**——先聚类发现类别，再人工打标，最后升级监督模型。

### 4.4 架构设计：离线 vs 在线、粒度与闭环

```text
                    +-------------------------------------------+
                    |      Workload Identification Stack        |
                    +-------------------------------------------+
   Collect              Feature               Identify            Decide
+----------+      +--------------+      +------------+      +------------+
| DCGM     |      | statistical  |      | cluster /  |      | scheduler  |
| eBPF     | ---> | temporal     | ---> | classify   | ---> | capacity   |
| OTel     |      | spectral     |      | drift det. |      | pricing    |
+----------+      +--------------+      +------------+      +------------+
       ^                                                     |
       |_______________ feedback loop (label backfill) ______|
```

关键设计决策：

| 决策点 | 选项 | 权衡 |
|:-------|:-----|:-----|
| 离线 vs 在线 | 离线批处理（天级画像）vs 在线流式（分钟级） | 精度 vs 时效 |
| 识别粒度 | 请求级 / 容器级 / 节点级 / 集群级 | 精度 vs 开销 |
| 标签体系 | 固定标签 vs 动态聚类 | 可解释 vs 自适应 |
| 反馈机制 | 人工标注回填 / 调度结果回报 | 冷启动 vs 闭环 |

---

## 5. 生产级实证：业界大规模工作负载表征成果

### 5.1 微软第一方工作负载大规模表征（2024）

微软对第一方（first-party）工作负载做了首次大规模实证研究，回答三个问题：①哪些负载特征影响效率与可靠性？②特征如何随负载变化？③如何规模化地表征所有负载？[来源: Parayil et al., "Towards Cloud Efficiency with Large-scale Workload Characterization", arXiv:2405.07250, 2024]

**核心贡献**：
- 识别出影响云平台效率与可靠性的**关键负载特征集合**（6 图 13 表）
- 证明人工表征不可扩展 → 必须自动化
- 直接服务于 Spot VM / Harvest VM / Burstable VM、超卖、功耗回收等效率特性设计

**对自建集群的启示**：即使没有微软的规模，同一套"特征→效率机制"的映射逻辑完全适用——先定义"影响我效率的特征有哪些"，再自动化采集与分类。

### 5.2 阿里 ServeGen：LLM 推理负载表征（NSDI'26）

**规模**：阿里云 Model Studio，**4 个月、12 个模型（310B/72B/14B 语言模型 + 多模态 + DeepSeek-R1 推理模型）、35.4 亿请求**，O(10K) GPU、数十个 region [来源: Xiang et al., "ServeGen", arXiv:2505.09999, NSDI'26]。

| 发现 | 量化数据 | 对识别系统的意义 |
|:-----|:---------|:-----------------|
| 到达模式突发 | CV >> 1，Gamma/Weibull/Exponential 无一普适 | 单一分布假设不可靠，需客户端分解 |
| 突发性漂移 | 同一负载 M-large 周一/周二持续突发，周四/周五转稳 | 识别模型必须在线更新（概念漂移） |
| 长度分布漂移 | 输入平均长度日内漂移最高 **1.63×**、输出 **1.46×** | 画像必须有时效性 |
| 客户端异质性 | M-small 的 **2,412 客户端中 top 29 贡献 90% 请求**；top 客户端行为稳定 | 客户端级分解是因果建模的关键 |
| 推理模型 | reason tokens 平均是 answer 的 **4×**；reason/answer 比例呈双峰 | 推理负载需单独画像（decoding 压力） |
| 多轮对话 | 多轮请求占 ~10%，inter-turn 间隔集中在 ~100s | 到达模型需会话感知 |
| 生成失真代价 | Naive 生成负载导致实例**欠供给 50%**（需 25 实例只配了 12） | 识别/生成的准确性直接转化为成本 |

**ServeGen 方法论贡献**：以**客户端（client）为中心**的负载建模——先按客户端分解（保留异质性），再按客户端参数化生成（Gamma 到达 + 分布采样），最后聚合。这纠正了"整体统计建模"的失真，是当前 LLM 负载表征的 SOTA 范式。

### 5.3 Google Borg trace 无监督聚类（2.4TB）

见 4.3。补充：CLOSER 2022 对 Google cluster-usage-traces-v3 的表征聚焦负载异质性、作业时长分布、资源消耗与集群可用性 [来源: van Loo et al., CLOSER 2022]。Google trace 系列（v2/v3）是学术界最常用的负载识别研究数据集——自建集群可借鉴其**数据schema设计**（作业级 + 事件级 + 资源级分层记录）。

### 5.4 深度推荐系统跨栈表征

IISWC 2020 对 8 个工业级深度推荐模型做算法层/系统层/微架构层三层表征，发现**部署选择（CPU vs GPU、batch 粒度）可带来最高 15× 性能差** [来源: Hsia et al., "Cross-Stack Workload Characterization of Deep Recommendation Systems", IISWC 2020]。

**启示**：同样的算法负载，部署形态不同 → 资源画像完全不同 → **"算法类型"不等于"资源负载类型"**，识别必须基于实际运行遥测而非静态声明。

### 5.5 实证结论汇总

| # | 结论 | 支撑证据 |
|:-:|:-----|:---------|
| 1 | 大规模负载表征必须自动化 | 微软（人工不可扩展）、Google（2.4TB） |
| 2 | 负载是异质且漂移的，静态建模必失真 | ServeGen（CV 漂移、长度漂移 1.63×） |
| 3 | 客户端/作业级分解优于整体统计 | ServeGen（top 29 客户端=90% 请求） |
| 4 | 无监督聚类是冷启动标配 | IEEE CLOUD 2023（2.4TB 聚类） |
| 5 | 识别失真直接转化为真金白银 | ServeGen（欠供给 50%） |

---

## 6. AI 集群场景深潜：训练/推理识别与调度闭环

### 6.1 GPU 利用率现实：识别是降本前提

AI 集群的核心资产是 GPU，但 GPU 利用率长期偏低且波动大：训练任务虽可达到高 MFU（Model FLOPs Utilization），但集群层面的平均利用率受调度碎片、任务间隙、故障恢复、排队等待拖累；推理负载的利用率更低且随请求潮汐剧烈波动。MFU 与集群利用率是两回事——**识别要回答的不是"单卡多满"，而是"这张卡上现在跑的是什么、值不值得这样跑"**（详见本库 MFU 专题：[MFU 功耗代理 × HeteroPanacea 四路推理分解](04_ai/2026-08-07-mfu-power-proxy-heteropanacea-deep-analysis.md)）。

### 6.2 训练 vs 推理：可识别的特征差异

| 特征维度 | 训练 | 推理 | 识别信号 |
|:---------|:-----|:-----|:---------|
| 任务时长 | 小时~周（长驻） | 毫秒~分钟（短请求） | 进程生命周期 |
| GPU 利用率曲线 | 稳态高（70-95%） | 突发波动（0-100% 剧烈） | SM 利用率方差 |
| 显存占用 | 分配后基本不变 | 随 batch 波动 | 显存时间序列 |
| 通信模式 | NCCL 集合通信周期性密集 | 稀疏/无 | 网卡流量模式 |
| 请求特征 | 无请求概念 | QPS、TTFT、TBT | 应用层指标 |

**识别规则示例（可落地）**：SM 利用率 >70% 且持续 >30 分钟 + 显存占用平稳 → 训练；SM 利用率方差 >0.5 + 存在 QPS 指标 → 推理；两者皆非 → 排队/空闲/故障，需要 RAS 侧确认。

### 6.3 识别驱动的调度：MoE / PD 分离 / 弹性扩缩容

识别结果直接喂给三类调度决策（详见本库调度专题：[调度对象三级升级技术深潜](04_ai/2026-08-07-scheduling-object-three-level-upgrade-deep-analysis.md)）：

| 调度场景 | 识别输入 | 决策输出 |
|:---------|:---------|:---------|
| MoE 专家调度 | 请求的专家激活模式（如 16-of-896） | 专家副本放置、负载均衡 |
| PD 分离 | prefill/decoding 负载占比 | 计算节点 vs 访存节点配比、独立扩缩容 |
| 弹性扩缩容 | 到达率 CV、长度分布漂移 | 预测性扩容、提前缩容 |
| 混部 | 负载兼容性画像 | 批处理填充在线低谷 |

> **闭环要点**：调度决策执行后，实际效果（延迟/利用率）回填为标签修正信号——识别与调度构成持续进化的闭环，而不是一次性的离线分析。

### 6.4 遥测基建：双轨融合与可观测性栈

识别系统的地基是遥测。知识库已有完整专题（[带内+带外双轨遥测融合](04_ai/2026-08-07-in-band-out-of-band-dual-track-telemetry-deep-analysis.md)、[可观测性纵深：NCCL 集合级 × Token 成本级](04_ai/2026-08-07-observability-depth-nixt-opencost-otel-kubeflow-cilium.md)），核心要点：

- **带外轨**（BMC/DCGM）：故障场景可用、零侵入，覆盖全部节点
- **带内轨**（OTel/eBPF/NCCL exporter）：语义丰富、请求级精度
- 双轨数据需**时间对齐 + 实体关联**（节点/GPU/容器统一 ID），否则识别特征无法融合

---

## 7. 工程落地框架

### 7.1 设计决策树

```text
Q1: labeled data available?
+-- none        -> unsupervised clustering (K-means/GMM) -> human interpretation -> label
+-- few         -> semi-supervised + clustering assisted
+-- sufficient  -> supervised classification (XGBoost/LightGBM), SHAP explainability

Q2: decision latency?
+-- minute-level (scheduling) -> online identification, lightweight features, incremental model
+-- day-level (capacity)      -> offline batch, full features, deep model

Q3: granularity?
+-- request-level (LLM inference) -> app-layer metrics
+-- node/cluster-level            -> HW + OS metrics

Q4: interpretability?
+-- high (pricing/customer)   -> rules + tree models, avoid black box
+-- medium (internal sched)   -> clustering + rules
```

### 7.2 指标体系

| 指标 | 定义 | 目标 |
|:-----|:-----|:-----|
| 分类准确率/宏 F1 | 标签级指标 | 按业务形态分别考核 |
| 漂移检测率 | 概念漂移被捕获的比例 | 识别模型更新的及时性 |
| 画像时效 | 画像刷新周期 vs 负载变化周期 | 画像滞后 < 负载变化尺度 |
| 决策增益 | 识别前后利用率/SLA 改善 | 绑定业务收益 |
| 误分类代价 | 错分导致的 SLO 违约/浪费 | 加权评估而非平均 |

### 7.3 常见陷阱

| 陷阱 | 表现 | 对策 |
|:-----|:-----|:-----|
| 标签=声明而非行为 | 按"作业名"分类，实际负载形态不同 | 基于遥测聚类验证标签 |
| 静态画像 | 模型训练一次用一年，负载已漂移 | 在线更新 + 漂移检测 |
| 平均指标掩盖异质 | 用均值代表一切 | 分位数 + 分布刻画 |
| 忽略客户端分解 | 整体统计被 top 客户端主导 | 按客户端/作业分解 |
| 识别与决策脱节 | 画像做了但调度不用 | 从决策需求反推识别设计 |

### 7.4 最小可行落地路径（MVP）

```text
Week 1:   baseline telemetry   -- deploy DCGM + node_exporter + OTel, unified timeline
Week 2-3: cold-start profiling -- unsupervised clustering on 2-4 weeks data, interpret 3-8 classes
Week 4:   rule-ify            -- translate clusters into interpretable rules / light classifier
Week 5-6: hook scheduler      -- pilot closed loop on 1 high-value scenario (colocation/scaling)
Week 7-8: evaluate & iterate  -- metrics per section 7.2, backfill labels
```

---

## 8. 挑战与趋势

| 挑战 | 本质 | 现状 |
|:-----|:-----|:-----|
| 标注稀缺 | 负载标签需专家人工打标，成本高 | 无监督聚类 + 半监督为主流 |
| 概念漂移 | 负载模式随业务演化 | 在线学习 + 漂移检测仍不成熟 |
| 隐私约束 | 应用级数据敏感（ServeGen 只能发布参数化数据） | 联邦学习 / 差分隐私方向 |
| 异构硬件 | CPU/GPU/NPU/DPU 指标语义不一致 | 统一指标模型（OTel 语义约定） |
| 跨层关联 | 应用语义 ↔ 硬件信号难对应 | eBPF + 双轨融合逐步解决 |

| 趋势 | 方向 | 信号 |
|:-----|:-----|:-----|
| LLM 负载表征成为新热点 | 语言/多模态/推理模型分别画像 | ServeGen（NSDI'26）代表 |
| 时序基础模型 | 预训练时序模型零样本分类 | TimesFM/Chronos 等方向 |
| eBPF 统一观测 | 内核级语义信号低成本采集 | Cilium/Pixie 生态 |
| 识别→AIOps 闭环 | 识别结果驱动自治运维 | 本库 agentic-aiops 专题 |

---

## 9. 结论与行动建议

**核心结论**：

1. **识别是利用率提升的地基**：Google 从 10-30% 到 60% 利用率的关键机制之一就是负载特征感知调度；识别失真直接造成 50% 级供给误差（ServeGen 实证）。
2. **识别是多维压缩问题**：业务形态 × 资源画像 × 时间模式 × AI 阶段 × SLA 五维 MECE 覆盖，标签粒度必须匹配决策需求。
3. **方法路线明确**：无监督聚类冷启动 → 人工打标 → 监督分类精化 → 在线更新防漂移；客户端/作业级分解优于整体统计。
4. **AI 集群是最大增量场景**：训练/推理识别 → MoE/PD/弹性调度闭环，是万卡集群降本增效的核心杠杆。

**对技术决策者的行动建议**：

| 优先级 | 动作 | 预期收益 |
|:------:|:-----|:---------|
| P0 | 建立统一遥测基线（DCGM+带内带外双轨） | 识别的数据地基 |
| P0 | 用 2-4 周存量数据做无监督聚类画像 | 3-8 类负载画像，冷启动完成 |
| P1 | 选择混部/弹性 1 个场景试点识别→调度闭环 | 利用率提升的直接验证 |
| P1 | 引入漂移检测，画像按周更新 | 防止模型失效 |
| P2 | 建立"识别→定价/容量"的量化评估体系 | 把识别收益算成钱 |

---

## 参考文献

1. **Xiang Y, Li X, Qian K, et al. "ServeGen: Workload Characterization and Generation of Large Language Model Serving in Production"**, arXiv:2505.09999, NSDI 2026 — LLM 推理负载表征 SOTA（35.4 亿请求、12 模型、客户端分解）
2. **Parayil A, Zhang J, Qin X, et al. "Towards Cloud Efficiency with Large-scale Workload Characterization"**, arXiv:2405.07250, 2024 — 微软第一方负载大规模实证（6 图 13 表）
3. **Suleiman B, Fulwala M M, Zomaya A Y. "A Framework for Characterizing Very Large Cloud Workload Traces with Unsupervised Learning"**, IEEE CLOUD 2023 — Google 2.4TB Borg traces 无监督聚类
4. **van Loo T, Jindal A, Benedict S, et al. "Scalable Infrastructure for Workload Characterization of Cluster Traces"**, CLOSER 2022 — Google cluster-usage-traces-v3 表征
5. **Verma A, Pedrosa L, Korupolu M, et al. "Large-scale cluster management at Google with Borg"**, EuroSys 2015 — Borg 架构与高利用率机制
6. **Barroso L A, Hölzle U. "The Case for Energy-Proportional Computing"**, IEEE Computer, 2007 — 服务器平均利用率 10-30% 基线
7. **Hsia S, Gupta U, Wilkening M, et al. "Cross-Stack Workload Characterization of Deep Recommendation Systems"**, IISWC 2020 — 跨栈表征、15× 部署差异
8. **Cortez E, et al. "Resource Central: Understanding and Predicting Workloads for Improved Resource Management"**, OSDI 2017 — Azure 遥测驱动的工作负载建模与预测（方法论参照）

---

## 变更记录

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-19 | v1.0 | 首次创建：工作负载识别方法论深度分析（第一性原理→维度体系→方法链路→生产实证→AI 集群落地） |
