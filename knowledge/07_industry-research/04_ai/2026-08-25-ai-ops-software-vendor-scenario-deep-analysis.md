# AI 应用下的运维业界全景：研究进展 × 软件与服务器厂商功能发布 × 场景运维现状

> **概要**: 本报告以「场景 × 厂商 × 研究」三轴组织，回答 AI 应用背景下「运维正在发生什么」。素材来源：①01_survey 八个运维相关目录 grep 汇总（ops-platform 19 篇 + ops-system 44 篇 + bmc-system/cluster-training/reliability-testing/data-center 等，2026-06~08）；②联网一手源（arXiv API 2026 最新 AIOps 论文、NVIDIA DCGM/Base Command Manager 官方页、The New Stack 分类页）；③知识库既有深度文档（08-20 AI 运维全景、08-07 Agentic AIOps 叙事、08-15 运维工具系列等）。核心结论：①研究侧 RCA 走向「证据链工程化+基准化」，遥测从「人读日志」转向「agent 可消费状态增量」；②软件厂商竞争焦点从「采集-展示」上移到「agent 自主处置」，无人率成为北极星；③服务器厂商以「GPU 集群管理（Base Command/DCGM）+ 带外管理 AI 化 + 故障自治」三线切入，NVIDIA 完成从 GPU 到 AI factory 运营的栈式覆盖；④五大场景（超节点万卡/GPU 云/企业 K8s/传统 DC/边缘推理）运维成熟度差异巨大，故障自治与成本治理是 2026 最陡峭的增量曲线。
> **关键词**: AIOps · Agentic Ops · 运维软件 · 服务器管理软件 · GPU 集群运维 · 场景化运维 · DCGM · Base Command · 故障自治 · 可观测性

> **版本**: v1.0
>
> **日期**: 2026-08-25
>
> **核心问题**: 在 AI 应用大规模落地的 2026 年，运维领域业界研究进展如何？运维软件厂商（Dynatrace/Datadog/PagerDuty 等）与服务器厂商（NVIDIA/Dell/HPE/华为/浪潮）各自发布了什么功能？超节点/万卡集群、GPU 云、企业云原生、传统数据中心、边缘推理等场景下的运维现状分别是什么样？

> **素材分级**: ✅ 一手 arXiv（2026 论文 15+ 篇，API 实测）· ✅ 厂商官方页（NVIDIA DCGM/Base Command）· ✅ 知识库既有深度文档（08-20 全景等 10+ 篇）· 🔵 01_survey 日报 grep（含未验证的搜索摘要类信号，已标注）· 🔵 行业媒体标题级信息（TNS 分类页）

> **适用范围**: 服务器平台规划 / 运维管理产品规划 / AI 基础设施软件栈 / 超节点项目运维设计

---

## 目录

- [1. 结论概要](#一结论概要)
- [2. 01_survey 运维素材盘点（grep 汇总）](#二01_survey-运维素材盘点grep-汇总)
- [3. 业界研究进展：2026 学术侧四条主线](#三业界研究进展2026-学术侧四条主线)
  - [3.1 RCA 从方法论走向证据链工程化与基准化](#31-rca-从方法论走向证据链工程化与基准化)
  - [3.2 遥测范式转向：从人读日志到 agent 原生状态增量](#32-遥测范式转向从人读日志到-agent-原生状态增量)
  - [3.3 集群容错体系化：从 checkpoint-restart 到故障自治](#33-集群容错体系化从-checkpoint-restart-到故障自治)
  - [3.4 运维成熟度模型：网络 AIOps 五世代与自主运维路线图](#34-运维成熟度模型网络-aiops-五世代与自主运维路线图)
- [4. 运维软件厂商功能发布矩阵](#四运维软件厂商功能发布矩阵)
  - [4.1 国际商业平台（2026 功能发布）](#41-国际商业平台2026-功能发布)
  - [4.2 国内厂商与云](#42-国内厂商与云)
  - [4.3 开源生态](#43-开源生态)
- [5. 服务器厂商管理软件功能发布](#五服务器厂商管理软件功能发布)
  - [5.1 NVIDIA：从 DCGM 到 AI Factory 运营栈](#51-nvidia从-dcgm-到-ai-factory-运营栈)
  - [5.2 国际服务器厂商带外管理](#52-国际服务器厂商带外管理)
  - [5.3 国内服务器厂商](#53-国内服务器厂商)
  - [5.4 开源 BMC 生态：OpenBMC](#54-开源-bmc-生态openbmc)
- [6. 各场景运维现状](#六各场景运维现状)
  - [6.1 超节点/万卡集群场景](#61-超节点万卡集群场景)
  - [6.2 GPU 云/算力租赁场景](#62-gpu-云算力租赁场景)
  - [6.3 企业云原生/K8s 场景](#63-企业云原生k8s-场景)
  - [6.4 传统 x86 数据中心场景](#64-传统-x86-数据中心场景)
  - [6.5 边缘/推理场站场景](#65-边缘推理场站场景)
- [7. 趋势判断与服务器研发启示](#七趋势判断与服务器研发启示)
- [8. 批判性审视](#八批判性审视)
- [9. 参考文件](#参考文件)
- [Changelog](#changelog)

---

## 一、结论概要

**一句话：2026 年 AI 应用下的运维正在经历「三线合流」——研究侧把 RCA/遥测/容错从「论文方法」推向「可评估、可验证、可执行的工程化」；软件厂商把竞争焦点从「采集-展示」上移到「agent 自主处置」（无人率成为北极星）；服务器厂商以 GPU 集群管理 + 带外管理 AI 化 + 故障自治三线切入，把「AI 运维 AI 系统」变成产品化主战场。**

1. **研究侧四条主线**：RCA 证据链工程化（轨迹级评估、25ms 在线 RCA、内核级诊断下沉）、遥测范式转向（Agent-Native Telemetry、双轨融合、O3 可观测性自监控）、集群容错体系化（FT-HSDP 100K GPU 实证有效训练时间 44%→80%、分层 checkpoint <10s、集合通信级故障切换）、网络 AIOps 成熟度模型（五世代演进，组织/信任/知识管理是瓶颈而非模型）[来源: arXiv 2608.14574 / 2605.12729 / 2605.11215 / 2602.00277]。
2. **软件厂商竞争焦点上移**：Dynatrace 自主 SRE agents + Agent Builder、PagerDuty AI-first 调度、Elastic 预测「两年内多数企业将 RCA 交给 AI agents」、Sumo Logic 告警疲劳治理——「采集-展示」能力已商品化，增量在「agent 证据包 + 受治理执行 + 成本结晶」[来源: TNS 07-08/07-24/07-27 / 知识库 08-20]。
3. **服务器厂商从「管理工具」升级为「AI factory 运营栈」**：NVIDIA 以 Base Command Manager 11（免费许可、硬件无关、Cluster on Demand）+ DCGM（主动健康监控）+ Mission Control + Run:ai 完成从单卡到 AI factory 的栈式覆盖；国际厂商（Dell iDRAC/HPE iLO）向预测性维护与 AI 助手演进；国内厂商（华为 iMaster/DME、超聚变 Fusion、浪潮 InManage 类）以「一体化底座 + AIOps」路线切入 [来源: nvidia.com / 知识库 08-15/08-20]。
4. **五大场景运维成熟度梯度分明**：超节点/万卡（故障自治刚起步，MTBF 以小时计，checkpoint 分层化）> GPU 云（利用率/成本治理成为商业模式核心）> 企业 K8s（GPU 资源调度 DRA 化、告警疲劳）> 传统 DC（AIOps 渗透率最高但以监控分析为主，执行自动化保守）> 边缘推理（运维半径大、无人值守需求最刚，成熟度最低）[来源: 知识库 08-14/08-24/08-25 综合]。
5. **对服务器研发的直接含义**：遥测粒度决定 AI 能力上限（事件级+拓扑+时间戳）；「活地图」取代「死台账」；带外管理（BMC）要提供「故障预测信号+快速隔离+恢复接口」三层能力并与上层调度协同；Agent 调用管理面必须套「命令级白名单+变更审计+回滚」确定性外壳 [来源: 知识库 08-20 §8]。

---

## 二、01_survey 运维素材盘点（grep 汇总）

按用户要求，用 grep 方式（关键词：`AIOps|可观测|observability|SRE|运维|监控|故障诊断|故障预测|告警`）对 `knowledge/01_survey/` 39 个子目录全量扫描，命中 8 个核心目录 + 6 个相关目录，汇总如下：

| 目录 | 文件数 | 时间跨度 | 运维相关内容主题 | 信息密度 |
|:-----|:------:|:--------|:-----------------|:--------:|
| `ops-platform/` | 19 | 2026-08 | AIOps/RCA/可观测性学术前沿 + 厂商动态（arXiv 逐日追踪、OTel 官方、TNS 分类页、中文搜索信号） | ★★★★★ |
| `ops-system/` | 44 | 2026-06~07 | 可观测性生态（OTel 毕业/Profiles/OTel-Arrow/GenAI Observability）、SRE 4-Body Problem、BPF 安全运维、PSI Metrics、K8s GPU 监控（HAMi） | ★★★★☆ |
| `bmc-system/` | 38 | 2026-06~08 | OpenBMC 2.18.0 版本静态期（14.8 个月无新正式版）、AI 平台贡献系统（GB200NVL/DC-SCM）、国产 BMC 生态格局 | ★★★☆☆ |
| `cluster-training/` | 20+ | 2026-08 | 训练容错/checkpoint/恢复语义（BSR 恢复工作集、KV 状态恢复）、投机解码与训练调度耦合、HBF 存储介质 | ★★★★☆ |
| `reliability-testing/` | 41 | 2026-06~08 | 容错系统论文（FT-HSDP/ReCoVer/TierCheck/PHOENIX/LUMEN/Concordia）、SDC、集合通信可靠性（VCCL/R²CCL） | ★★★★☆ |
| `data-center/` | 18 | 2026-08 | 机架级供电散热（智能 PDU、液-空 CDU、UPS）、PUE 管控、密度 vs 扇耗决策 | ★★★☆☆ |
| `cloud-native/` | 66 | 2026 | 云原生生态（K8s/OTel/CNCF 项目）中的运维组件 | ★★★☆☆ |
| `switch/` | 15 | 2026-08 | IETF 三重 AI 网络标准（数据面/遥测面/运维面 AIOps 用例）、网络可观测性 | ★★★☆☆ |

**关键发现（grep 过程提炼）**：

1. **ops-platform 是最活跃的运维专项追踪**：2026-08 逐日追踪 arXiv cs.DC/SE/NI 运维论文 + OTel 官方 + 行业媒体，主线从「Agent 可观测性/证据链」到「RCA 基准化（ORCA-bench/CTBench/LongRCA）」再到「自愈实证（K8s 升级 11 分钟零人工）」，与 08-20 全景文档的 L3 判断完全互证 [来源: 01_survey/ops-platform/2026-08-21~25]。
2. **ops-system 记录了可观测性生态的「毕业期」**：OTel 2026-07 正式毕业（Profiles Alpha/OTel-Arrow Phase 2/GenAI Observability 三连击），官方博客进入「生态消化期」（08-14 后零增量确认 4 日），增量转移到厂商与 CNCF 生态实践（Atlassian RCA 全文公开）[来源: 01_survey/ops-platform/2026-08-23~25]。
3. **中文生态信号被安全验证拦截**：08-22~25 百度/Bing 连续触发安全验证，中文厂商一手信息获取受限，仅有搜索摘要级信号（阿里云 AIOps 顶会成果、2026 智能运维选型指南、必示科技四阶段模型、AIOps 市场 193.3 亿美元）——**中文侧量化数据需谨慎对待** [来源: 01_survey/ops-platform/2026-08-22~25]。
4. **服务器侧运维素材分散在硬件/可靠性目录**：BMC（带外管理）、cluster-training（容错）、reliability-testing（RAS 论文）、data-center（供电散热监控）——说明「服务器运维」本身横跨软件栈与硬件层，知识库需要本报告做一次横向整合。

---
## 三、业界研究进展：2026 学术侧四条主线

> 素材：arXiv API 实测（AIOps 关键词 2026-03~08 最新）+ 01_survey/ops-platform 2026-08 逐日追踪 + 知识库既有论文深潜。四条主线互不重叠且覆盖「诊断-观测-恢复-演进」全链路（MECE）。

### 3.1 RCA 从方法论走向证据链工程化与基准化

2026 年 RCA（根因分析）研究的最大变化：**评估对象从「结果对不对」升级为「过程证据足不足」**，且出现面向生产保真度的基准与下探内核/网络的专用工具：

| 论文/基准 | 时间 | 核心贡献 | 量化证据 |
|:---------|:----:|:---------|:---------|
| ORCA-bench v2（oncall RCA 就绪度） | 2026-08 | OTel 插桩微服务 + 6 天真实遥测 + 1079 个 RCA 任务，5 个前沿 Agent 实测 | 最佳 RCA 准确率仅 Medium 25.3% / Hard 10.0%，最弱模型 40% 场景幻觉根因；LLM-judge 与人类评分 κw=0.90 [来源: arXiv 2607.28545] |
| CTBench（电信运维 Agent 排障） | 2026-08 | 专家构建，黄金证据步骤标注 | SOTA Agent 路径恢复端点好但 RCA 整体欠佳，接口/链路/服务管理类故障是共同短板 [来源: arXiv 2608.12002] |
| LongRCA Bench（长时程 Agent 失败归因） | 2026-08 | 5 域 1,140 条无注入错误失败轨迹（中位 145 步），双标签评估 | 填补 agent 运维排障数据集缺口 [来源: arXiv 2608.15242] |
| Beyond Fault Localization（轨迹级 RCA） | 2026-08 | 3,500 条轨迹分析，评估诊断证据基础与故障传播路径 | RCA 评估从端点正确性转向过程证据 [来源: arXiv 2608.21310] |
| KernelDiag（内核崩溃 RCA） | 2026-07 | log-to-code 映射对齐异构证据 + Evidence Graphs 结构化因果 | KGYM 困难场景 Top@k 提升最高 4x/2x，RCA 下沉 OS 内核层 [来源: arXiv 2607.17722] |
| eIRWR（可扩展微服务 RCA） | 2026-08 | power-law teleportation 锐化随机游走 | 12K-25K 节点 MRR 0.75（2.8x 最佳聚合基线）；17K 节点 <25ms 满足在线部署 [来源: arXiv 2608.08073] |
| EvoCause（LLM 引导因果图演化） | 2026-07 | LLM 语义图编辑 + 确定性代码验证环闭 | 发布 TeleRCA 生产电信基准（485,681 告警事件）；Node F1/Case EM/Graph F1 较 PC 基线 +11.59/+9.40/+4.59 pp [来源: arXiv 2607.27290] |
| FailureAtlas（LLM 网关故障分类学） | 2026-07 | 两轴分类（origin layer × detectability） | 核心发现：最具破坏性故障是「静默失败」（HTTP 200 但破坏应用状态），需语义级可观测性 [来源: arXiv 2607.17525] |

**主线判断**：RCA 正在经历「三个下沉」——评估基准下沉到生产保真（ORCA-bench 25.3% 的上限提醒「生产安全托付的下界」）、诊断对象下沉到内核/微架构（KernelDiag/Microflow）、延迟下沉到在线可用（eIRWR <25ms）。对服务器运维的直接含义：**单靠 LLM 读日志做 RCA 的上限已被实测划出（约 25% 准确率），必须叠加拓扑图、因果证据链与专用遥测才能突破** [来源: arXiv 2607.28545 / 2607.17722]。

### 3.2 遥测范式转向：从人读日志到 agent 原生状态增量

| 论文/事件 | 时间 | 核心贡献 | 意义 |
|:---------|:----:|:---------|:-----|
| Agent-Native Telemetry | 2026-08 | 可验证的 state-delta 证据（非日志流），密码学可验证 | 遥测设计从「人读事件流」重构为「agent 可消费、可验证的状态变更流」[来源: arXiv 2608.16178] |
| UModel（agent-ready 观测数据建模） | 2026-06 | 面向 agent 消费的观测数据建模方法，规模化解耦 | agent 化遥测的数据模型层工作 [来源: arXiv 2606.04799] |
| 带内+带外双轨遥测融合 | 2026-08 | OTel Linux 一键部署 + Go 编译时插桩 + NIXT NCCL 导出器 | 服务器侧带外（BMC/Redfish）与带内（OTel）数据打通是 AI 运维前提 [来源: 知识库 08-07 深潜] |
| OpAMP/O3（可观测性自监控） | 2026-07 | Observability of Observability | 可观测性基础设施本身成为关键路径时，其健康必须被监控 [来源: 01_survey/ops-system] |
| OTel 毕业三连击 | 2026-07 | Profiles Alpha（第四信号）+ OTel-Arrow Phase 2 + GenAI Observability | 采集→传输→分析完整演进；GenAI Observability 覆盖 LLM 调用链 [来源: 01_survey/ops-system 07-10] |
| NIXT（NCCL 通信可观测） | 2026-08 | NCCL Inspector profiler 数据导出 | 2048 GPU H100 集群 Nemotron-4 预训练案例：通信阶段量化 + straggler RCA——万卡训练通信层专用工具化 [来源: arXiv 2608.01449] |
| TELLER（LLM 推理跨层 RCA） | 2026-08 | NVTX/CUPTI 追踪重建请求级调用链 | Trace Pair Encoding 压缩 per-step trace 80%+；LLM 推理服务 RCA 基建 [来源: arXiv 2608.01975] |

**主线判断**：遥测的「消费者」正在从人变成 agent。日志从「给人读的散文」变成「给 agent 消费的结构化状态增量」，这一转变影响服务器侧：BMC 事件/SEL/Redfish 订阅需要标准化为 agent 可解析的事件流，且带外/带内双轨必须融合（AI 诊断需要同时看 OS 层与固件层）[来源: 知识库 08-07 双轨遥测 / arXiv 2608.16178]。

### 3.3 集群容错体系化：从 checkpoint-restart 到故障自治

这是「AI 运维 AI 系统」的学术主线，也是 2026 年量化数据最扎实的方向（全部有生产或大规模实验实证）：

| 系统 | 规模/条件 | 核心机制 | 量化效果 |
|:-----|:---------|:---------|:---------|
| FT-HSDP（Meta） | O(100K) GPU 生产 | DP 副本为容错单元 + FTAR 协议 + 非阻塞 catch-up | 故障恢复 stall 10min→3min；有效训练时间 44%→80%；异步恢复零精度损失 [来源: arXiv 2602.00277] |
| ReCoVer | 512 GPU，运行中累计丢失 256 GPU | 容错集合通信 + in-step 细粒度恢复 + microbatch 再分配 | 有效吞吐 2.23x vs checkpoint-restart；234 GPU-hours 多处理 74.9% tokens [来源: arXiv 2605.11215] |
| PHOENIX | 512 A100，65B 参数 | 零开销内存 checkpoint + communicator reconstruction 热插拔 | 错误路径零 checkpoint 开销；永久节点故障恢复 <40s [来源: arXiv 2607.01646] |
| TierCheck | 40B 参数 | 集群感知分层 checkpoint（本地差分 + 远程 base） | 端到端 checkpoint <10s，支持高频 checkpoint [来源: arXiv 2605.17821] |
| RobustRL | 256 GPU，Qwen3-8B，10% 故障注入 | 角色级故障隔离（RL post-training 专用） | 有效时间占比 80%+ vs ByteRobust 60%；端到端 -8.4~17.4% [来源: arXiv 2512.22492] |
| VCCL | 生产集群数月 | 集合通信库级容错（primary-backup QP）+ window-based 监控 | 吞吐最高 +5.28%；NIC 端口故障容忍；O(μs) 级网络异常观测 [来源: arXiv 2510.00991] |
| R²CCL | 8-GPU H100 IB + 仿真 | 多 NIC 快速连接迁移 + 弹性集合算法 | 网络故障浪费 10~15% GPU 小时（问题量化）；训练开销 <1%、推理 <3%；优于 AdapCC 12.18x [来源: arXiv 2512.25059] |
| Concordia | LLM 推理 | device-resident persistent kernel 级 checkpoint | KV/调度器/通信状态不再因单 GPU 故障丢失数分钟工作 [来源: arXiv 2606.23521] |
| LUMEN | 分布式 serving | 负载感知协调恢复（checkpoint 放置/请求分布/容量恢复） | serving 与恢复时间显著改善 [来源: arXiv 2606.17787] |

**主线判断**：容错已经从「作业级重启」细化到「集合通信级故障切换」（代价低几个数量级）与「副本级隔离」（Meta 实证）。关键量化锚点：**网络故障浪费 10~15% GPU 小时、故障恢复 stall 从 10min 压到 3min 有效训练时间即从 44% 升到 80%**——这些数字直接定义了万卡集群运维的 ROI 天花板 [来源: arXiv 2512.25059 / 2602.00277]。

### 3.4 运维成熟度模型：网络 AIOps 五世代与自主运维路线图

2026 年出现的两篇综述/路线图类论文，把散点研究收束为可执行路线：

- **网络 AIOps 五世代成熟度模型**（arXiv:2608.14574，超大规模网络生产经验）：人工排障 → 脚本自动化 → 规则系统 → AI 辅助 → 自主 incident 解决。关键论点：**代际跃迁的瓶颈不是模型而是「工具链 + 信任框架 + 知识管理 + 运维文化」的协同演进**——技术只占一半，组织变革是另一半 [来源: arXiv 2608.14574]。
- **Agentic NetOps/AIOps 综述**（arXiv:2605.12729）：以「自主层级 × 工具范围 × 证据轨迹 × 保障契约」四维组织文献。核心结论：**运维可靠性不主要来自模型本身，而来自模型周围的机制**（权限/策略/检查/回滚）；评估应从端点正确性转向保障契约满足度 [来源: arXiv 2605.12729]。

**与知识库既有判断的互证**：08-20 全景文档的「信任阶梯（crawl-walk-run）+ 六组件架构 + 确定性外壳」与这两篇的「保障契约 + 机制决定可靠性」完全同构；Progressive Crystallization（8 个月生产，确定性执行 0%→45%、成本 -70%）为「从 AI 辅助到自主」提供了成本侧证据 [来源: 知识库 08-10 / arXiv 2607.07052]。

---

## 四、运维软件厂商功能发布矩阵

> 说明：本节聚焦「功能发布」而非公司介绍。国际厂商信息以 2026 官方页/行业媒体为准；国内厂商因中文搜索通道受限（08-22~25 安全验证拦截），部分为搜索摘要级信号，已标注可信度。

### 4.1 国际商业平台（2026 功能发布）

| 厂商 | 2026 关键发布 | 功能要点 | 证据 |
|:-----|:-------------|:---------|:-----|
| **Dynatrace** | 自主 SRE agents（07-27）+ Agent Builder | Agent 直指「AI 运维最难的部分」；无代码自定义 agent；Davis 因果 AI 定位根因 + 受治理执行 | TNS 07-27 [来源: 知识库 08-23] |
| **PagerDuty** | Operations Cloud AI-first | incident 生命周期自动化、AI 升级调度、SRE agents 五方式框架；36,000+ 组织 | TNS 07-26 [来源: 知识库 08-07] |
| **Elastic** | 收购 DeductiveAI（2026-06）+ 自主 incident 解决 | 「两年内多数企业将把 RCA 交给 AI agents」时间表预测 | TNS 07-08 [来源: 知识库 08-24] |
| **Sumo Logic** | 告警疲劳治理方案 | 告警量爆炸（AI 时代遥测膨胀）下的降噪与聚焦 | TNS 07-24 [来源: 知识库 08-23] |
| **Cisco/Splunk** | Splunk AI Toolkit + AppDynamics | CDTSM 深度时序模型 GenAI 异常检测（2026-06）、事件驱动 Ansible 联动自动响应 | [来源: 知识库 08-20] |
| **Datadog** | LLM Observability（2025 持续）+ AI 运维深化 | GenAI 工作负载 token/延迟追踪；2026-06 后向 AI 运维深化 | [来源: 知识库 08-20/08-22] |
| **ServiceNow** | AIOps + ITSM 集成 | 事件→工单→变更自动化，与 Dynatrace 生态联动 | [来源: 知识库 08-20] |
| **Chronosphere** | OpenRCA 开源 + 自建 AI SRE 路线 | 「企业应自建 AI SRE」的可行性论证（数据私有化驱动） | TNS 07-30 [来源: 知识库 08-23] |
| **Honeycomb/New Relic** | AI 分析增强 | 传统可观测厂商 AI 化（告警/分析/根因） | [来源: 08-22 选型指南摘要] |

**共性趋势**：①「采集-展示」能力商品化，增量全部在 **agent 自主处置 + 证据包 + 治理**；②**融资/并购加速**（Coralogix 2 亿美元专攻自主 agent 监控、Elastic 收购 DeductiveAI）[来源: 知识库 08-20]；③「无人率」（永远不需要人的 incident 百分比）成为北极星指标 [来源: 知识库 08-07]。

### 4.2 国内厂商与云

| 厂商 | 产品/路线 | 功能要点 | 证据可信度 |
|:-----|:---------|:---------|:----------|
| **华为** | iMaster NAIE/DME + 云内 AIOps | 数据管理引擎 DME（数据中心管理）+ 云内 AIOps 控制面 | 产品线官方导航确认；功能细节待验证 |
| **阿里云** | 云内嵌 AIOps + 顶会成果 | 「连登顶会，多项研究成果大幅提升运维智能精度」（新闻稿信号） | 🔵 搜索摘要，URL 无法验证 [来源: 01_survey 08-25] |
| **腾讯云** | 云内嵌 AIOps | 与阿里同路线，降低对西方软件依赖 | 🔵 [来源: 知识库 08-20] |
| **必示科技** | 金融 AIOps 四阶段模型 | 「可观测性→告警智能→根因分析→自动止损」跨行业通用模型；受等保 2.0 三级约束 | 🔵 [来源: 01_survey 08-22] |
| **嘉为蓝鲸** | 一体化运维 PaaS | CMDB/ITSM/自动化/Agent 开发平台一体化底座 | 🔵 与纯 AIOps 路线对照 [来源: 01_survey 08-22] |
| **锐捷** | 乐享 3.0 | 资产数字化底座 + 全域 IT 资源一体化 AIOps | 🔵 [来源: 01_survey 08-22] |
| **联想** | TrioXpert | 多模态 incident 管理（异常检测+分诊+RCA 三合一），生产部署 RCL 最高 +163.1% | ✅ arXiv 2506.10043 |

**路线分化**：国内出现「纯 AIOps（Davis AI 类）vs 一体化底座（嘉为蓝鲸类）」两条技术路线——前者强在自动根因分析，后者强在 CMDB/ITSM/自动化闭环；趋势是两者双向夹击融合 [来源: 01_survey/ops-platform/2026-08-22]。

### 4.3 开源生态

- **OpenTelemetry**：2026-07 正式毕业，Profiles Alpha（第四信号）+ OTel-Arrow Phase 2 + GenAI Observability；官方博客进入生态消化期，增量转移至厂商与 CNCF 生态（Atlassian RCA 全文公开）[来源: 01_survey ops-system/ops-platform]。
- **Prometheus/Grafana**：监控底座事实标准；Grafana 数据源插件架构 + 声明式配置持续演进 [来源: 知识库 08-15]。
- **Chronosphere OpenRCA**：开源 RCA 引擎 [来源: 知识库 08-20]。
- **K8s GPU 资源管理**：DRA（Dynamic Resource Allocation）改变 GPU 调度范式——「告别 K8s GPU 之痛」[来源: TNS 08-06 标题级]。
- **HAMi**：CNCF 项目，GPU 可观测性层（Prometheus + Grafana GPU 监控）[来源: 01_survey ops-system 07-15]。

---
## 五、服务器厂商管理软件功能发布

> 核心观察：服务器厂商的运维软件正在从「带外管理工具（BMC/iDRAC/iLO）」升级为「AI 基础设施运营栈」——NVIDIA 是这一转变的领跑者（从 DCGM 到 Base Command/Mission Control），传统厂商以「带外管理 AI 化 + 预测性维护 + 一体化平台」跟进。

### 5.1 NVIDIA：从 DCGM 到 AI Factory 运营栈

NVIDIA 已形成「四层运维栈」，覆盖单卡→集群→AI factory 全尺度（2026 官方页实测）：

```
+--------------------------------------------------------------+
|  Layer 4  Mission Control / Run:ai   AI factory operations   |
|           (workload orchestration + infra automation)        |
+--------------------------------------------------------------+
|  Layer 3  Base Command Manager 11     cluster mgmt           |
|           (provision / monitor / auto-scale / CoD)           |
+--------------------------------------------------------------+
|  Layer 2  DCGM + DCGM-Exporter        GPU health telemetry   |
|           (active health / diagnostics / power mgmt)         |
+--------------------------------------------------------------+
|  Layer 1  GPU / NVSwitch / NVLink     hardware               |
+--------------------------------------------------------------+
```

| 产品 | 2026 状态 | 功能要点 |
|:-----|:---------|:---------|
| **DCGM** | 持续演进 | 主动健康监控（job 运行时低开销非侵入）、全面诊断（失效/性能劣化/功耗低效根因）、遥测（explain job 行为）、电源/时钟治理策略；x86_64 + aarch64；DCGM-Exporter 集成 K8s；开源核心 + 专有诊断模块 [来源: developer.nvidia.com/dcgm] |
| **Base Command Manager 11** | 最新版 | 统一管理 HPC+AI 集群（从数节点到数十万）；Base View 新 UI（安装向导/监控仪表盘/改进可扩展性）；Auto-Scale 动态上下电；Cluster on Demand（云端按需建集群/拆集群控成本）；Slurm 就地更新；JupyterLab 集成；硬件无关（x86/Arm/GPU 混合）；**免费许可（≤8 加速器/系统）**；与 Slurm/Run:ai 集成 [来源: nvidia.com/base-command] |
| **Mission Control** | 运营层 | AI factory 运营自动化（含 Base Command 全部能力 + 配置/验证/运营）[来源: nvidia.com] |
| **Run:ai** | 编排层 | AI 工作负载与 GPU 编排（2024 收购）[来源: nvidia.com] |

**判断**：NVIDIA 的运维栈是「AI 运维 AI 系统」的完整产品化——把学术界的故障自治/利用率优化直接做成商业软件（Base Command 免费策略意在抢占集群管理入口）。对国产服务器厂商：**这既是产品对标基线，也是生态绑定压力**（Base Command 硬件无关但深度绑定 NVIDIA GPU 遥测）。

### 5.2 国际服务器厂商带外管理

| 厂商 | 产品 | AI 化方向（基于知识库既有素材，功能细节待官方验证） |
|:-----|:-----|:---------------------------------------------------|
| **Dell** | iDRAC + OpenManage | 带外管理事实标准；Redfish 支持成熟；AI 化方向为预测性维护与自动诊断（08-20 软件栈需求规格以 InManage 类平台为基线对标过）[来源: 知识库 08-20] |
| **HPE** | iLO + Compute Ops Management | iLO 带外 + COM 云化集中管理；GreenLake 订阅制运维（08-24 收费模式分析有覆盖）[来源: 知识库 08-24] |
| **Supermicro** | BMC/IPMI + SuperCloud Composer | 传统 IPMI 生态 + 云管理平台 [来源: 知识库 OpenBMC 平台列表] |
| **超聚变（xFusion）** | Fusion 三级工具链 | Tools（带外工具）/Online（在线升级调优）/Director（集中管理）三级体系 [来源: 知识库 08-15 Fusion 深潜] |

### 5.3 国内服务器厂商

| 厂商 | 产品 | 要点 |
|:-----|:-----|:-----|
| **华为** | iBMC + iMaster/DME + eSight | 服务器带外（iBMC）+ 数据中心管理（DME）+ ICT 统一管理（eSight）产品线完整；AI 化通过云侧 AIOps 承载 [来源: e.huawei.com 导航实测] |
| **浪潮** | InManage 类管理平台 | 9 域+安全特性的服务器管理平台基线；08-20 需求规格文档已将其作为对标基线展开（12 层 MECE 软件栈 L0 固件带外→L11 交付运维，128 条需求规格）[来源: 知识库 08-20] |
| **中科曙光/新华三/联想** | 各自带外管理+云管平台 | 国内厂商普遍以「带外管理 + 集群管理 + AIOps 平台」三件套切入 |

### 5.4 开源 BMC 生态：OpenBMC

- **版本静态期**：OpenBMC 2.18.0 仍为 Latest（2025-05-30 发布，基于 Yocto 5.2 "walnascar"），截至 2026-08-20 已 **14.8 个月无新正式版**；2.14→2.18 版本号跳跃，正式 tag 仅作里程碑锚点，滚动开发是主流 [来源: 01_survey/bmc-system 08-20]。
- **AI 平台成头部贡献者**：2.18.0 贡献系统清单中 NVIDIA gb200nvl-obmc、Qualcomm qcom-dc-scm-v1、AMD daytonax/ethanolx、Meta yosemite4 系列等 AI/云平台位列第一梯队——**AI 服务器已成 OpenBMC 的主战场** [来源: 01_survey/bmc-system 08-20]。
- **国产生态**：openUBMC（openubmc.cn）定位「大模型训练场服务器智能管理」，但 08-14 后更新停滞（Bing 索引时间戳回退）；国产 BMC 生态格局以 OpenBMC 中文站 + CSDN 科普为主，无重量级新参与者 [来源: 01_survey/bmc-system 08-22]。

---

## 六、各场景运维现状

> 按「部署形态 × 运维对象」MECE 划分五大场景。每场景给出：现状、核心痛点、代表工具、AI 渗透度评级、量化锚点。

### 6.1 超节点/万卡集群场景

**现状**：AI 基础设施的最前沿场景，运维从「服务器运维」升维为「系统级故障自治」。核心矛盾：**集群规模指数增长（O(100K) GPU）而单节点 MTBF 不变，故障成为常态而非异常**。

- **量化锚点**：Meta FT-HSDP 在 O(100K) GPU 生产集群实证——同步训练频繁故障+长恢复，有效训练时间仅 44%，FT 方案提升到 80%（stall 10min→3min）[来源: arXiv 2602.00277]；网络故障浪费 10~15% GPU 小时 [来源: arXiv 2512.25059]。
- **现状特征**：①checkpoint 分层化（本地差分+远程 base <10s）[来源: arXiv 2605.17821]；②集合通信级容错成为新热点（VCCL/R²CCL，NCCL 替代）[来源: arXiv 2510.00991]；③推理侧免重启恢复（ReviveMoE，华为云 MaaS 生产部署）[来源: arXiv 2602.21140]；④AI 原生可观测（NIXT 2048 GPU 通信 RCA、TELLER 推理跨层 RCA）[来源: arXiv 2608.01449]。
- **核心痛点**：任务级自动恢复、租户隔离框架、利用率遥测（08-24 超节点使用角度深度分析的 P0 三项）；上下电/部署过程可观测性（CPLD 状态机+POST code+SEL+BMC SOL 四层上电观测链）[来源: 知识库 08-24/08-25]。
- **AI 渗透度**：★★★★☆（研究最热、产品化最快，但生产验证仍少——万卡真实 MTBF/恢复时长分布未公开）。
- **代表工具**：Base Command Manager、DCGM、Slurm+容错插件、NCCL 替代（VCCL/R²CCL）、分层 checkpoint 系统、NVIDIA Mission Control。

### 6.2 GPU 云/算力租赁场景

**现状**：商业模式驱动运维——**利用率与成本治理直接决定毛利**，运维从「成本中心」变成「商业模式核心」。
- **现状特征**：①按小时计费（RunPod/Lambda/Together/CoreWeave/Vast）+ 订阅制（GreenLake）+ 运维 SLA 三层收费组合拳 [来源: 知识库 08-24 收费模式分析]；②容量决策智能化（FleetSieve 配置 profiling「测关键而非测全」、SLO-Scaler 贝叶斯不确定性量化扩缩容、Safety-Gated Autoscaling 泄漏门控）[来源: 01_survey/ops-platform 08-24/08-25]；③成本可观测（OpenCost/Kubecost/Nixt）成为标配 [来源: 知识库 08-07]。
- **核心痛点**：碎片化利用率、spot 实例弹性（ShuntServe 异构 spot GPU）、静默故障检测（SDC 单比特翻转 <40%）[来源: arXiv 2605.04213 / 2606.18600]。
- **AI 渗透度**：★★★★☆（AI 直接参与容量决策与成本治理，落地最实在）。
- **代表工具**：Run:ai、Kubecost/OpenCost、Slurm+、云厂商 GPU 实例调度。

### 6.3 企业云原生/K8s 场景

**现状**：AIOps 渗透率最高、厂商竞争最激烈的场景——「采集-展示」商品化，增量在 agent 处置。
- **现状特征**：①可观测三支柱标准化（OTel 毕业，采用率 64%）[来源: 知识库 08-20]；②RCA 基准化（ORCA-bench 25.3% 上限）——企业落地 AI RCA 需清醒认识能力边界 [来源: arXiv 2607.28545]；③GPU 调度 DRA 化（K8s DRA 改变 GPU 资源管理）[来源: TNS 08-06]；④告警疲劳成首要痛点（Sumo Logic「告警疲劳击垮 SOC」）[来源: TNS 07-24]；⑤变更安全（Meta 部署健康检查、Semantic Quorum 不安全批准率 18.5%→0.3%）[来源: arXiv 2608.20513 / 2606.08021]。
- **核心痛点**：多集群运维（AWS 跨百万集群 zonal failure 经验）、GPU 资源碎片化、agent 决策可审计性（「每个 agent 决策都要收据」）[来源: TNS 07-10/07-17]。
- **AI 渗透度**：★★★☆☆（分析层成熟，执行层刚起步——护栏/审计是入场券）。
- **代表工具**：OTel/Prometheus/Grafana、Dynatrace/PagerDuty/Datadog、Chronosphere OpenRCA、K8s DRA。

### 6.4 传统 x86 数据中心场景

**现状**：AIOps 最早落地场景，但以「监控分析」为主、「执行自动化」保守——受监管行业（金融等保 2.0）约束明显。
- **现状特征**：①带外管理成熟（iDRAC/iLO/iBMC + Redfish 标准化）[来源: 知识库 08-15 Redfish 深潜]；②AIOps 四阶段模型（可观测性→告警智能→根因分析→自动止损）成为跨行业通用框架 [来源: 01_survey 08-22 必示科技]；③告警降噪最成熟（90% 降噪实证）[来源: 知识库 08-20]；④执行自动化受合规约束（等保 2.0 三级：安全审计/访问控制/数据加密）[来源: 01_survey 08-22]。
- **核心痛点**：告警疲劳、跨系统 RCA、存量系统可观测性改造（遗留系统治理方法论）[来源: 知识库 08-24]。
- **AI 渗透度**：★★★☆☆（分析渗透高，执行渗透受合规压制）。
- **代表工具**：Zabbix/Prometheus+Redfish、Splunk/ServiceNow、必示科技/嘉为蓝鲸类平台。

### 6.5 边缘/推理场站场景

**现状**：运维半径大、无人值守需求最刚、成熟度最低的场景——「K8s at edge 撞墙，fleet management 是出路」[来源: TNS 08-20]。
- **现状特征**：①边缘 K8s 运维成本高，舰队管理（fleet management）成为共识 [来源: TNS 08-20]；②推理场站（能源/制造/零售）与数据中心运维能力差距大；③OTel for Dart/Flutter 等移动/边缘语言覆盖仍在早期 [来源: 01_survey ops-system]；④BPF 安全监控「去 Agent 化」（Tetragon 直接 BPF 发包）对无人值守场景安全监控有直接参考 [来源: 01_survey ops-system]。
- **核心痛点**：远程运维带宽受限、无人值守故障恢复（RMA 物流周期）、安全监控盲区（agent 被杀即失明）。
- **AI 渗透度**：★★☆☆☆（最薄弱，但 AI 边缘推理设备自运维是蓝海）。
- **代表工具**：边缘 K8s 舰队管理、OTel Collector 边缘部署、Tetragon/BPF 安全监控。

---
## 七、趋势判断与服务器研发启示

### 7.1 五条趋势判断

1. **运维软件与服务器管理软件双向合流**：软件厂商（Dynatrace 等）向下够硬件遥测（GPU/服务器指标），服务器厂商（NVIDIA/华为/浪潮）向上够工作负载编排——最终形态是「AI factory 运营平台」，中间层（Cluster on Demand、DRA、任务级容错）是争夺焦点。
2. **「AI 运维 AI 系统」成为最有 ROI 的方向**：容错/恢复的收益直接转化为训练吞吐（44%→80% 实证），比通用 AIOps 的「告警降噪」更可量化——服务器厂商应把故障自治能力做成产品差异点。
3. **无人率取代 MTTR 成为北极星**：厂商叙事从「缩短修复时间」转向「永远不需要人的 incident 百分比」，这要求运维平台内置确定性外壳（结晶）+ 护栏（治理）+ 审计（证据链）三件套。
4. **遥测消费者从人变 agent，带外数据必须标准化**：BMC/SEL/Redfish 事件流需要成为 agent 可解析的结构化状态增量，带内（OTel）+带外（BMC）双轨融合是服务器侧 12-18 个月内必须完成的能力。
5. **中文生态 AIOps 进入平台期，量化数据稀缺**：国内厂商效果宣传多、论文级实证少（仅联想 TrioXpert 等个别），选型判断需以「可验证基准」为准绳。

### 7.2 对服务器研发的六点启示

| # | 启示 | 落地建议 |
|:-:|:-----|:---------|
| 1 | 遥测粒度决定 AI 能力上限 | 带外遥测按「事件级+时间戳+拓扑关系」设计；Redfish 事件订阅下沉 [来源: 知识库 08-20 §8] |
| 2 | 活地图 > 死台账 | 资产管理从静态 FRU/CMDB 走向实时拓扑感知（Smartscape 式自动发现）[来源: 知识库 08-20 §8] |
| 3 | 故障自治三件套 | BMC 侧提供「故障预测信号 + 快速隔离机制 + 恢复接口」，与 K8s/NCCL 容错协同 [来源: 知识库 08-20 §8] |
| 4 | Agent 管理面护栏 | IPMI/BMC 命令被 agent 调用时必须有「命令级白名单 + 变更审计 + 回滚」确定性外壳（Semantic Quorum 18.5%→0.3% 实证）[来源: arXiv 2606.08021] |
| 5 | 成本工程内置 | 「探索-结晶」机制设计进运维平台，高频操作固化脚本，避免 agent 成为永久成本中心（-70% 实证）[来源: arXiv 2607.07052] |
| 6 | 对标 NVIDIA 运维栈 | Base Command/DCGM 是功能基线；免费许可策略提示「管理软件是生态入口不是利润中心」[来源: nvidia.com 实测] |

### 7.3 对超节点项目的直接映射

结合知识库 08-24/08-25 超节点设计文档：运维设计应覆盖「部署过程可观测（四层上电观测链 + 部署流水线状态机）→ 运行期遥测（三网分离 + 控制/数据面分离架构下的遥测管道）→ 故障自治（任务级自动恢复 P0）→ 成本治理（利用率遥测）」四段闭环，与业界「感知→诊断→决策→治理」依赖链对齐 [来源: 知识库 08-24/08-25]。

---

## 八、批判性审视

1. **benchmark 鸿沟仍是最大陷阱**：ORCA-bench 25.3% 与厂商宣传的「90% 降噪/60% MTTR 缩短」之间的落差说明——厂商数字多来自受控环境，生产 RCA 上限远低于宣传；引用效果数字必须带条件与基线（本报告已尽力标注）[来源: arXiv 2607.28545 / 知识库 08-20 §9]。
2. **中文侧数据可信度受限**：08-22~25 百度/Bing 安全验证拦截导致国内厂商一手信息缺口；阿里云「顶会成果」等信号 URL 无法验证，已按规则标注为搜索摘要级；AIOps 市场规模（193.3 亿美元）等数字为二手转载，未交叉验证。
3. **服务器厂商功能细节缺口**：Dell iDRAC/HPE iLO 的 2026 AI 功能未能获取官方一手页（403/404），本报告以知识库既有素材+推断标注「待官方验证」——建议后续用浏览器通道或厂商白皮书补齐。
4. **万卡生产数据未公开**：超节点场景的 MTBF、恢复时长分布等核心运维指标无公开生产数据，Meta FT-HSDP 是唯一 O(100K) 实证但仅覆盖训练场景；推理侧万卡运维仍是空白。
5. **「无人率」叙事的商业成分**：厂商推动的自主运维叙事与其订阅收入模式利益一致，落地节奏可能慢于宣传；Agentic 执行的安全事件无公开统计，「agent 犯错速度」风险被低估。

---

## 参考文件

### 外部资料引用

> 联网实测时间：2026-08-25

[1] NVIDIA DCGM 官方页 [来源: developer.nvidia.com/dcgm]
[2] NVIDIA Base Command Manager 官方页 [来源: nvidia.com/en-us/data-center/base-command/]
[3] arXiv:2608.14574 — From Reactive to Autonomous: Evolution of AI Operations in Cloud Network Infrastructure（网络 AIOps 五世代成熟度模型）
[4] arXiv:2605.12729 — Large Language Models for Agentic NetOps and AIOps: Architectures, Evaluation, and Safety
[5] arXiv:2607.28545 — ORCA-bench v2（oncall RCA 就绪度评测）
[6] arXiv:2608.12002 — CTBench（电信运维 Agent 排障基准）
[7] arXiv:2608.15242 — LongRCA Bench（长时程 Agent 失败归因基准）
[8] arXiv:2608.21310 — Beyond Fault Localization（轨迹级 RCA）
[9] arXiv:2607.17722 — KernelDiag（Agent 内核崩溃根因诊断）
[10] arXiv:2608.08073 — eIRWR（可扩展微服务 RCA）
[11] arXiv:2607.27290 — EvoCause（LLM 引导因果图演化 RCA）
[12] arXiv:2607.17525 — FailureAtlas（LLM 网关故障模式分类学）
[13] arXiv:2608.16178 — Agent-Native Telemetry（可验证状态增量证据）
[14] arXiv:2606.04799 — UModel（agent-ready 观测数据建模）
[15] arXiv:2608.01449 — NIXT（NCCL Inspector 导出工具）
[16] arXiv:2608.01975 — TELLER（LLM 推理跨层 RCA）
[17] arXiv:2602.00277 — FT-HSDP（Meta O(100K) GPU 容错训练）
[18] arXiv:2605.11215 — ReCoVer（容错预训练）
[19] arXiv:2607.01646 — PHOENIX（零开销 checkpoint 热插拔）
[20] arXiv:2605.17821 — TierCheck（分层 checkpoint）
[21] arXiv:2512.22492 — RobustRL（RL 后训练容错）
[22] arXiv:2510.00991 — VCCL（可观测集合通信库）
[23] arXiv:2512.25059 — R²CCL（可靠集合通信）
[24] arXiv:2606.23521 — Concordia（持久 kernel checkpoint）
[25] arXiv:2606.17787 — LUMEN（分布式 serving 协调恢复）
[26] arXiv:2602.21140 — ReviveMoE（MoE 推理免重启恢复，华为云）
[27] arXiv:2606.08021 — Semantic Quorum（agent 变更安全门控）
[28] arXiv:2607.07052 — Progressive Crystallization（AIOps 确定性化）
[29] arXiv:2605.04213 — The Anatomy of Silent Data Corruption
[30] arXiv:2606.18600 — ShuntServe（异构 spot GPU 弹性）
[31] arXiv:2608.20513 — Making Deployments Safe at Meta
[32] TNS: Dynatrace's new agents（07-27）/ Elastic RCA agents（07-08）/ Sumo Logic alert fatigue（07-24）/ Build your own AI SRE（07-30）/ K8s DRA（08-06）/ Edge fleet management（08-20）/ Agent decision receipt（07-17）/ AWS zonal failures（07-10）— 标题级信息
[33] arXiv:2506.10043 — TrioXpert（联想生产部署）
[34] arXiv:2401.13810 — Microsoft GPT-4 cloud incident RCA（基线参照）

### 内部知识库引用

- [AI 在基础设施运维管理中的应用进展全景（2024-2026）](2026-08-20-ai-infra-ops-application-progress-deep-analysis.md)（同目录，演进脉络/六维矩阵/平台清单详版）
- [Agentic AIOps 2026 叙事](2026-08-07-agentic-aiops-2026-narrative-deep-analysis.md)（L1→L3 框架/六组件/无人率）
- [Agent 运行时护栏 × Agentic AIOps × 800V HVDC](2026-08-07-agent-runtime-guardrails-agentic-aiops-800v-hvdc-deep-analysis.md)
- [带内+带外双轨遥测融合](2026-08-07-in-band-out-of-band-dual-track-telemetry-deep-analysis.md)
- [NVIDIA 全栈可观测性选型框架](../../06_others/sources/2026-08-13-nvidia-fullstack-observability-choose.md)
- [超节点使用角度深度分析（运维/维护角色视角）](../02_rd/02_project/01_superpod/2026-08-24-supernode-usage-driven-design-deep-analysis.md)
- [上下电/部署活动全过程保障设计](../02_rd/02_project/01_superpod/2026-08-25-power-deploy-observability-verification-reliability-check.md)
- [运维+算力平台收费模式深度分析](../16_market-competition/2026-08-24-ops-compute-platform-pricing-model-deep-analysis.md)
- [超聚变 Fusion 运维工具链](../../02_rd/03_management/2026-08-15-fusion-ops-toolchain-deep-analysis.md)
- [2026 智能运维目标体系](../../02_rd/03_management/2026-08-15-aiops-2026-goals-deep-analysis.md)
- [Redfish 协议与 Zabbix 服务器硬件监控](../../02_rd/03_hardware/2026-08-15-server-hardware-monitoring-redfish-zabbix-deep-analysis.md)
- [Grafana 可观测平台](../../05_tools/devops/2026-08-15-grafana-observability-deep-analysis.md)
- [Zabbix 监控全景](../../05_tools/devops/2026-08-15-zabbix-monitoring-system-deep-analysis.md)
- [调度×可靠性×可观测性三论文深潜](../02_rd/02_project/01_superpod/2026-08-14-scheduling-reliability-observability-three-papers-deep-analysis.md)
- [Progressive Crystallization 深潜](../../03_AI/agent-engineering/2026-08-10-progressive-crystallization-aiops-deterministic-workflow-deep-analysis.md)
- 01_survey/ops-platform/2026-08-21~25（RCA 基准化/Agent 遥测/自愈实证逐日追踪）
- 01_survey/ops-system/2026-06~07（OTel 毕业期/SRE 4-Body/可观测性生态）
- 01_survey/bmc-system/2026-08-20~22（OpenBMC 版本静态期/国产 BMC 生态）
- 01_survey/cluster-training + reliability-testing/2026-08（容错/checkpoint 论文追踪）
- 01_survey/data-center/2026-08（机架级供电散热/PDU/PUE 管控）

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-25 | v1.0 | 首次创建。AI 应用下的运维业界全景三轴报告（研究进展 × 软件/服务器厂商功能发布 × 场景运维现状）。素材：01_survey 八目录 grep 汇总 + arXiv API 实测 2026 论文 15+ 篇 + NVIDIA DCGM/Base Command 官方页 + TNS 分类页 + 知识库既有深度文档 10+ 篇。差异化于 08-20 全景文档：以场景×厂商为主轴，补充 2026H2 研究增量（RCA 基准化/Agent-Native Telemetry/容错体系化/五世代成熟度模型）与 NVIDIA 四层运维栈。 |
