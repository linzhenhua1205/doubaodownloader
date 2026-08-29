# 🔀 IETF 三重 AI 网络标准信号：MoE 组播卸载 + MPLS PBT-M 遥测 + AIOps 智能化

> **类型**: 深度专题 | **日期**: 2026-08-11（事件 2026-08-07~10）| **定位**: AI 训练网络标准化的系统性启动——数据面（MoE 组播）+ 可观测面（PBT-M）+ 运维面（AIOps/NORIA）三线并进；衔接 [`switch/2026-08-11.md`](2026-08-11.md)（追踪速记）、[`cluster-training/2026-08-11.md`](../cluster-training/2026-08-11.md)（StrataCL/Incast-Free 互证）
> **数据源**: IETF Datatracker 三 draft 一手抓取（2 个全文 + 1 个摘要）+ 知识库追踪系列 + 第一性原理推导
> **关联文件**: [`switch/2026-08-11.md`](2026-08-11.md)、[`cluster-training/2026-08-11.md`](../cluster-training/2026-08-11.md)、[`moe-hardware/2026-08-11.md`](../moe-hardware/2026-08-11.md)、[`2026-08-10-gb300-nvl72-moe-pretraining-record-deep-analysis.md`](../../02_rd/01_product/00_hardware/01_hw-core/aiserver/2026-08-10-gb300-nvl72-moe-pretraining-record-deep-analysis.md)

---

## 📑 目录

- [0. 一句话结论](#0-一句话结论)
- [1. 事实基线（一手验证）](#1-事实基线一手验证)
- [2. 第一性原理：三条标准线的物理动因](#2-第一性原理三条标准线的物理动因)
- [3. 三线合流：AI 网络"执行-观测-决策"闭环](#3-三线合流ai-网络执行-观测-决策闭环)
- [4. 产业信号解读](#4-产业信号解读)
- [5. 与知识库既有框架互证](#5-与知识库既有框架互证)
- [6. 结论与可证伪预判](#6-结论与可证伪预判)
- [7. 数据缺口与下一步](#7-数据缺口与下一步)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 0. 一句话结论

> **IETF 一周内三线并进：MoE 组播用例进入路由工作组（数据面卸载）、MPLS PBT-M 成为 WG 文档（遥测面标准化）、AIOps/NORIA 推进（运维面智能化）——AI 训练网络从"厂商私有优化"进入"开放标准定义"阶段。三条线分别对应万卡训练网络的执行面、观测面、决策面，构成"数据面卸载 + 端到端可观测 + 知识化运维"的完整闭环，是中国厂商（ZTE/中国移动）主导数据面标准、欧美厂商主导遥测标准的格局分水岭。**

---

## 1. 事实基线（一手验证）

### 1.1 draft-zhang-rtgwg-llmmoe-multicast-03（数据面：MoE 组播）

| 维度 | 内容 | 来源 |
|:-----|:-----|:-----|
| 标题 | Multicast use case in LLM MoE | IETF Datatracker（全文抓取）|
| 版本/日期 | -03，2026-08-09 | 同上 |
| 作者 | Zheng Zhang（ZTE）、Wei Duan（ZTE）、Xiaohu Xu（中国移动）、Yisong Liu（中国移动）| 同上 |
| 状态 | Active Internet-Draft（individual）、Intended status: Informational | 同上 |
| 核心用例 | **tokens dispatching**：MoE 推理/训练中一个 token 需发送到多个专家 = 典型组播 | 同上 |
| 关键数据 | Mixtral 8 专家/激活 2；Llama4 Scout 16、Maverick **128 专家**/激活 2；DeepSeekV3 **256 专家/激活 9**（8 routed + 1 shared）| 同上 |
| 拓扑优化 | DeepSeekV3 node restricted routing：先选 node group 再选 expert，**最多 4 节点**减少跨节点分发 | 同上 |
| 动态性需求 | 每个 token 的专家组合不同且选择过程极短 → **PIM 建树来不及** | 同上 |
| 可靠性需求 | 极高可靠性：任一分支丢包/延迟/抖动都可能导致 LLM 计算重启 | 同上 |
| 技术结论 | **BIER 最适**：无中间路由器 per-flow 状态、无显式建树；专家可编号为 BFR，源 GPU（BFIR）直接指定专家组（BFER）封装进报文，**消除建树时间**；Leaf/Spine/GPU 可预建 expert-based 转发表；PIM-SM/PIM-DM/ingress replication 均不适用 | 同上 |
| 协同要求 | 网络层组播需与 LLM 软件、集合通信实现、NIC 配合 | 同上 |

**一手原文引用**：
> "The use of multicast may be intra-node or inter-node... the selection process is very short, leaving no time for multicast technologies like PIM to establish a multicast tree."
> "BIER... allows the source GPU (similar to BFIR in BIER) to directly specify the destination expert group... eliminating the time for multicast tree establishment. **Therefore, BIER is the most suitable multicast technology.**"

### 1.2 draft-ietf-mpls-on-path-telemetry-flag-03（可观测面：MPLS PBT-M）

| 维度 | 内容 | 来源 |
|:-----|:-----|:-----|
| 标题 | MPLS On-Path Telemetry Network Action Flag for OAM（PBT-M）| IETF Datatracker（全文抓取）|
| 版本/日期 | -03，2026-08-10，**WG 文档（mpls WG）**，Intended: Standards Track | 同上 |
| 作者 | Haoyu Song（Futurewei）、Giuseppe Fioccola（Huawei）、Rakesh Gandhi（Cisco）| 同上 |
| 机制 | Postcard-Based Telemetry with Packet Marking：头部节点用 **MNA Sub-Stack（RFC 9994）单个 flag bit**（Opcode 1 / Format D LSE P-flag）标记报文 → 每个 PBT-M-aware 节点生成 postcard 发往 collector | 同上 |
| 前身/对偶 | 类似 SRv6 OAM O-bit（RFC 9259）；与 IPv6 IOAM 互补（passport=IOAM trace RFC 9197，postcard=IOAM DEX RFC 9326）| 同上 |
| 开销模型 | **固定 3 LSE（12 octets）**，不随路径长度/数据量增长（对比 in-stack passport 逐跳增长）；网络级开销 ≈ m×N×R（标记率×节点数×包速率）| 同上 |
| 默认限速 | 标记率 ≤ **1/1000（0.1%）**；postcard 生成率默认 **1000/s（burst 2000）**，防 DoS | 同上 |
| 流路径发现 | 无需预配置：首包标记 → 各节点导出基础数据（node ID + per-LSE TTL vector）→ collector 动态学习路径 | 同上 |
| 数据关联 | flow ID + TTL vector（per-LSE，因 PUSH/POP 后单 TTL 非单调）/ 时间戳（PTP/NTP 同步）；无法唯一关联的 postcard 必须丢弃 | 同上 |
| ECMP 保护 | P-flag 必须位于 Format D LSE **bits 24-31**（前 23 bits 参与 ECMP hash，可变位不得影响负载均衡）| 同上 |
| 安全 | 单信任域 + 入口过滤（域边界清除/丢弃 P-flag）+ 双限速 + 计数器/告警；P-flag 本身不加密（与 SRv6 O-bit/IOAM DEX 同限制）| 同上 |
| 资源交互 | 消耗 3 个 label 位置 → 须在 MSD 广告中反映（RFC 8491）；须在 RLD 内可见 | 同上 |
| 状态 | WG Document；OPSDIR early review（Carlos Pignataro）；RTGDIR review 8/11 到期；shepherd Tony Li | 同上 |

### 1.3 draft-king-rokui-ainetops-usecases-02 + NORIA（运维面：AIOps/知识图谱）

| 维度 | 内容 | 来源 |
|:-----|:-----|:-----|
| draft-king-rokui-ainetops-usecases-02 | Artificial Intelligence (AI) for Network Operations（2026-08-10，**71 页**）：AI 驱动网络规划/排障/优化的 IETF 需求基线 | switch 追踪（未抓全文⚠️）|
| draft-tailhardat-nmop-incident-management-noria-05/-01 | 知识图谱（Knowledge Graphs）用于跨运营商事件管理与网络设计（2026-08-07/10 双文档并行）| switch 追踪（未抓全文⚠️）|
| 含义 | 网络故障诊断知识结构化、AI 运维用例需求基线 IETF 化 | 同上 |

### 1.4 数据缺口（诚实标注）

| 缺口 | 说明 |
|:-----|:-----|
| AIOps/NORIA 全文 | 未抓取（datatracker 可访问但本轮聚焦前两 draft），细节待补 |
| draft 早期状态 | 均为 individual/informational 或早期 WG 文档，无实现/测试/部署数据 |
| BIER 实测 | 组播卸载在真实 MoE 训练网络的端到端收益无公开实测（华为/中移动可能有内部数据）|
| 组播与集合通信协同 | draft 只提"需与集合通信/NIC 配合"，无具体接口设计 |

---

## 2. 第一性原理：三条标准线的物理动因

### 2.1 数据面：MoE all-to-all 是"一对多"天然组播，却用"一对一"复制的低效方式传输

**物理事实**：MoE 中一个 token 需同时到达 2-9 个（甚至 128 个候选）专家。传统实现 = 源 GPU 发 N 份单播副本（ingress replication），或依赖 PIM 建树。

**三组量化对比（draft 一手数据 + 第一性原理推导）**：

| 方案 | 建树/状态开销 | 带宽效率 | 动态适配（token→专家组合逐 token 变化）| 结论 |
|:-----|:-------------|:---------|:----------------------------------------|:-----|
| 单播复制（现状）| 无 | ❌ 源 GPU 负载 N×、网络流量 N× | ✅ 天然动态 | 低效但可行 |
| PIM-SM | ❌ 信令建树、接收者变化需重建 | 中 | ❌ **选择过程极短（<ms 级）来不及建树** | 不适用 |
| ingress replication | 无 | ❌ 带宽消耗大 | 中 | draft 明确不推荐 |
| **BIER** | ✅ **无 per-flow 状态**（BitString 即转发表索引）| ✅ 交换机级复制一次到位 | ✅ **源 GPU 直接指定专家组，零建树时间** | **draft 结论：最适** |

**第一性原理推论 1**：MoE token 分发的本质是 **"短生命周期、高动态性、高扇出"的一对多传输**。它的目的地集合（专家组合）在报文生成瞬间才确定、下个 token 就变——任何"先建树再传输"的机制（PIM 类）都输在时间尺度上。BIER 把"目的地集合"编码进报文头（BitString），让**中间交换机无状态复制**，正好匹配 token 分发的时间尺度。**这是"把路由决策从控制面移到数据面"的又一次落地**（呼应 TensorCast 控制面/数据面分离主线）。

### 2.2 可观测面：AI 训练网络需要"逐跳、按需、低开销"的丢包/时延定位

**物理事实**：万卡训练中一个慢节点/丢包链路会导致整批训练停滞（FT-HSDP：10 万 GPU 18 分钟一次故障）；但**传统 OAM 无法回答"包在哪一跳丢了、为什么"**。

**PBT-M 的第一性原理优势**：
1. **开销恒定**：12 octets 固定，不随路径长度/数据量增长——in-stack passport 模式逐跳累积，在长路径（跨 Leaf/Spine 多跳）会撑爆 PMTU；
2. **按需触发**：默认 1/1000 标记率 + 1000/s postcard 上限，把遥测对训练流量的扰动压到 0.1% 以下——**遥测本身不能成为训练网络的负担**；
3. **丢包诊断**：即使被监控报文在某跳丢失，前面各跳的 postcard 仍有效 → 精确定位丢包位置和原因（解决"假存活"——监控看不到命令完成率的问题）；
4. **与 IOAM 互补**：IPv6 网络用 IOAM（passport/DEX），MPLS/SR-MPLS 网络用 PBT-M——**两大数据面（IPv6/SRv6 + MPLS）都有了标准遥测机制**。

**第一性原理推论 2**：可观测性的本质是"**用最小代价回答'包在哪跳经历了什么'**"。PBT-M 的"标记触发 + 带外 postcard + 固定开销"是这一目标的最优解形式——它在**数据面（触发）+ 带外通道（传输）+ 管理面（配置）**之间做了清晰的职责切分，让遥测收集不干扰业务转发（呼应带内遥测主线 OTel/OTLP 的"带内+带外双轨"设计）。

### 2.3 运维面：故障诊断从"专家经验"走向"知识图谱+AI 用例"

**物理事实**：网络故障诊断（尤其 AI 训练网络的多故障叠加）依赖专家经验，不可扩展、不可复用。

**AIOps 用例（71 页）+ NORIA（知识图谱）的含义**：
- AIOps 用例文档 = 把"AI 驱动网络规划/排障/优化"的需求**基线化**，为后续数据模型/接口标准提供需求锚点；
- NORIA = 把故障诊断知识**结构化**（知识图谱），跨运营商共享——诊断从"人肉经验"走向"可查询的图结构"。

**第一性原理推论 3**：AI 运维的价值 = **把隐性知识显性化、把显性知识可计算化**。用例文档定"要解决什么"，知识图谱定"知识怎么组织"，两者合起来是 AIOps 标准化的"需求层+数据层"。

---

## 3. 三线合流：AI 网络"执行-观测-决策"闭环

```text
+----------------------+      +----------------------+      +----------------------+
|   EXECUTION (数据面)  |      |  OBSERVATION (观测面) |      |  DECISION (决策面)    |
|  MoE token dispatch    |      |  per-hop latency/drop |      |  fault diagnosis/path  |
|  BIER stateless mcast  |      |  PBT-M mark+postcard  |      |  AIOps use-case base   |
|  draft-zhang -03       |      |  draft-ietf-mpls -03  |      |  NORIA knowledge graph |
+----------------------+      +----------------------+      +----------------------+
         |                             |                             |
         | 1. token dispatch via mcast | 2. per-hop latency/drop    | 3. diagnosis feeds back
         +-----------------------------+-----------------------------+
              loop: better execution -> observability -> smart decision -> optimize execution
```

**三线的时间逻辑**：IETF 先立**用例**（MoE 组播 use case、AIOps use cases）→ 再立**机制**（BIER/PBT-M）→ 再立**应用**（NORIA 知识图谱）。这不是巧合，而是标准化的自然路径：**需求 → 机制 → 应用**，每层都有 use case 文档锚定需求基线。

**对照万卡训练网络的分层**：
- **数据面**（执行）：MoE all-to-all 是训练吞吐关键路径（GB300 已证：吞吐由通信而非计算决定）→ 组播卸载直接提升训练效率；
- **可观测面**（观测）：PBT-M 逐跳遥测 → 慢节点/丢包定位 → 直接服务 RAS 与故障恢复（训练暂停等恢复的 checkpoint 策略需要快速定位）；
- **运维面**（决策）：AIOps/NORIA → 故障诊断知识化 → 缩短 MTTR。

---

## 4. 产业信号解读

### 4.1 中国厂商主导数据面标准，欧美厂商主导遥测标准——格局分水岭

| draft | 主导机构 | 区域 |
|:------|:---------|:-----|
| llmmoe-multicast（数据面）| **ZTE + 中国移动** | 🇨🇳 |
| MPLS PBT-M（遥测面）| Futurewei + Huawei + Cisco | 🌍（中/美混合）|
| AIOps use cases | King/Rokui（待查全文）| — |
| NORIA | Tailhardat（待查全文）| — |

**解读**：
1. **中国厂商在"AI 网络数据面"标准上抢得先机**——MoE 组播用例由中国运营商/设备商提出，且 BIER 结论直接服务于国产 DDC/无损网络叙事（新华三万卡 DDC、华为 CloudMatrix）；
2. 遥测面由华为（Fioccola 常驻 MPLS/IOAM 领域）+ Futurewei/Cisco 主导——中国厂商在遥测标准亦有席位；
3. **对比**：NVIDIA Spectrum-X/Quantum 走厂商私有无损方案，IETF 走开放标准——**双轨并存**，未来 AI 网络设备需同时兼容（开放标准是长期确定性，私有方案是短期性能）。

### 4.2 与厂商叙事/学术前沿互证

| 信号 | 关系 | 含义 |
|:-----|:-----|:-----|
| StrataCL（华为，fabric-native 通信库）| **软件层下沉** vs **网络层卸载** | 分工：通信库管 buffer/算子，网络层管复制/转发——两层互补而非竞争 |
| Incast-Free Rate-Based Scheduling（Technion/Berkeley）| **调度面治理** vs **组播数据面卸载** | 双线：调度消除 incast（速率级公平），组播削减流量本身（一对多复制）——MoE 网络优化从"流量避让"走向"流量重塑+卸载" |
| IETF rtgwg MoE 组播用例 | 标准侧里程碑 | 与集群训练学术线（StrataCL/Incast-Free）构成"学术-标准"双轮 |
| 新华三 DDC 万卡无损 / UniPoD | 厂商叙事呼应 | 国产 DDC 架构是 BIER 组播卸载的天然载体（无状态转发+集中控制）|
| IEEE 802.1 TSN 无损三支柱（PFC 增强/源端流控/直通转发）| 链路层互补 | IETF 管网络层（组播/遥测），802.1 管链路层（无损/确定性）——AI 网络标准在两层并行推进 |
| 带内遥测主线（OTel/OTLP，Go 编译插桩）| 主机侧对偶 | PBT-M = 网络设备侧遥测；OTel = 主机/应用侧遥测——统一 OTLP 平面（超节点软件底座）在网络层有了标准对偶 |

### 4.3 对超节点/万卡训练的直接含义

1. **数据面**：MoE all-to-all 组播卸载（BIER）若落地，直接削减训练关键路径流量——对 130TB/s NVLink 域内与跨机架场景均有收益（draft 覆盖 intra-node/inter-node 两场景）；
2. **可观测面**：PBT-M 逐跳遥测 → "假存活"诊断（B300 现场报告：NCCL 挂起时 utilization% 仍 100%）的标准化解法——遥测数据可定位丢包/延迟跳，配合命令完成率监控形成完整 RAS 视图；
3. **运维面**：AIOps/NORIA → 故障诊断知识图谱 → 与本地"故障诊断/FTA/容错"P1 主线同向，且标准化后跨厂商可互操作。

---

## 5. 与知识库既有框架互证

| 既有框架 | 互证结论 |
|:---------|:---------|
| MEMORY「LLM 推理统一框架：跨节点判决量=延迟×层数；KV 搬家 320KB/token」| MoE 组播卸载直接削减跨节点判决量的传输成本（一对多复制 → 一次复制）|
| MEMORY「MoE 组播标准化=IETF 里程碑；Incast-Free 与组播构成'数据面卸载+调度面治理'双线」| 本分析将双线扩展为三线（+遥测面+运维面）闭环 |
| [`cluster-training/2026-08-11.md`](../cluster-training/2026-08-11.md)（StrataCL/Incast-Free）| 学术侧双证：fabric-native 通信库（软件）+ 速率级公平调度（调度）与 BIER 组播卸载（网络）构成三层优化栈 |
| [`switch/2026-08-11.md`](2026-08-11.md)（DDC 万卡/BIER-TE BGP-LS 扩展）| BIER-TE 的 BGP-LS 扩展（-07）与 MoE 组播用例同周出现——组播复制面在 IETF 全面加码 |
| [`moe-hardware/2026-08-11.md`](../moe-hardware/2026-08-11.md)（MoE 硬件叙事收敛期）| 训练侧 MoE 硬件叙事从"论文驱动"转向"标准驱动"——IETF 成为 MoE 网络需求的新锚点 |
| [`GB300 纪录`](../../02_rd/01_product/00_hardware/01_hw-core/aiserver/2026-08-10-gb300-nvl72-moe-pretraining-record-deep-analysis.md)（吞吐由通信决定）| 组播卸载是"通信决定吞吐"结论的工程化出路之一 |
| 可靠性测试（FT-HSDP 故障率/假存活陷阱）| PBT-M 逐跳遥测是"假存活"诊断的标准侧解法 |
| 带内遥测主线（OTel/OTLP/带内+带外双轨）| PBT-M 是网络设备侧的"带外遥测"标准对偶——统一 OTLP 平面可同时消费主机与网络遥测 |

---

## 6. 结论与可证伪预判

### 6.1 结论

1. **AI 网络标准化进入系统性启动期**：一周内数据面（MoE 组播）+ 遥测面（PBT-M）+ 运维面（AIOps/NORIA）三线并进，且遵循"用例 → 机制 → 应用"的标准化路径——**需求锚点（use case）先行**是 IETF 的成熟打法，也说明 AI 网络需求已被标准组织正式承认；
2. **BIER 成为 MoE 组播的事实技术选择**：draft 明确"BIER is the most suitable"——无状态复制+零建树时间匹配 token 分发的时间尺度；这对国产 DDC/无损网络设备是**直接的标准机遇**（BIER 已在 BGP-LS/BIER-TE 侧同步加码）；
3. **遥测标准化补齐 AI 网络可观测性短板**：PBT-M 的固定开销+按需触发+丢包定位能力，是"假存活"诊断、慢节点定位、SLO 契约执行的网络层基座；
4. **中国厂商在 AI 网络标准话语权上升**：ZTE+中国移动主导数据面用例，华为参与遥测——与国产 GPU/DDC 硬件叙事形成"硬件+标准"双轮。

### 6.2 可证伪预判（2027 年核验）

| # | 预判 | 核验方式 |
|:--|:-----|:---------|
| H1 | draft-zhang-llmmoe-multicast 12 个月内转 WG 文档（rtgwg 吸收或新建 WG）| 跟踪 draft 状态 |
| H2 | BIER 组播卸载 2027 年前在国产 DDC 或头部云厂商 AI 集群有商用部署/测试 | 厂商发布/会议论文 |
| H3 | MPLS PBT-M 12-18 个月内进入 RFC 发布通道（已 WG + 双 review）| 跟踪 IESG 状态 |
| H4 | AIOps 用例催生 nmop 新 work item（网络 AI 数据模型/遥测接口标准）| 跟踪 nmop WG 议程 |
| H5 | 2027 年 IETF 出现"AI 训练网络"专属 WG 或 BOF（三线合流后的组织化）| 跟踪 IETF 新 WG/BOF 公告 |

---

## 7. 数据缺口与下一步

### 7.1 待补数据
1. **AIOps/NORIA 全文**：抓取 draft-king-rokui-ainetops-usecases-02（71 页）与 NORIA 双文档，提取 AIOps 用例清单与知识图谱 schema；
2. **BIER 实测**：跟踪是否有厂商/学术组在 MoE 训练网络实测 BIER 组播卸载（对比 ingress replication 的带宽/延迟收益）；
3. **draft 演进**：llmmoe-multicast -04+、PBT-M -04+ 的更新（尤其是否转 WG、是否加入训练场景细节）。

### 7.2 跟踪节奏（与 MEMORY 事件窗口对齐）
- **OCP APAC（8/11-12 台北）**：AI 网络标准与 UALink 交叉信号；
- **Hot Interconnects（8/19-21）**：BIER/组播在 AI 网络的学术侧呼应；
- **AI Infra Summit（9/15-17）**：IETF AI 网络标准与产业落地对照；
- **switch 专题常规节奏**：IETF 周更 + 事件驱动增量。

---

## 参考来源

### 内部知识库引用
- [`switch/2026-08-11.md`](2026-08-11.md) — 追踪速记（24 条信息，含三个 draft 摘要 + DDC/厂商动态）
- [`cluster-training/2026-08-11.md`](../cluster-training/2026-08-11.md) — StrataCL/Incast-Free 学术互证
- [`moe-hardware/2026-08-11.md`](../moe-hardware/2026-08-11.md) — MoE 硬件叙事收敛观察
- [`2026-08-10-gb300-nvl72-moe-pretraining-record-deep-analysis.md`](../../02_rd/01_product/00_hardware/01_hw-core/aiserver/2026-08-10-gb300-nvl72-moe-pretraining-record-deep-analysis.md) — MoE 训练吞吐=通信决定
- MEMORY.md — LLM 推理统一框架 / 假存活陷阱 / 带内遥测主线 / MoE 组播双线

### 外部资料引用（一手抓取）
- IETF Datatracker: draft-zhang-rtgwg-llmmoe-multicast-03（2026-08-09，全文）— https://datatracker.ietf.org/doc/draft-zhang-rtgwg-llmmoe-multicast/
- IETF Datatracker: draft-ietf-mpls-on-path-telemetry-flag-03（2026-08-10，全文）— https://datatracker.ietf.org/doc/draft-ietf-mpls-on-path-telemetry-flag/
- IETF Datatracker: draft-king-rokui-ainetops-usecases-02（摘要，全文待补）— https://datatracker.ietf.org/doc/draft-king-rokui-ainetops-usecases/
- IETF Datatracker: draft-tailhardat-nmop-incident-management-noria-05（摘要，全文待补）— https://datatracker.ietf.org/doc/draft-tailhardat-nmop-incident-management-noria/
- 引用规范：RFC 7761（PIM-SM）、RFC 8279（BIER）、RFC 9994（MNA Sub-Stack）、RFC 9197/9326（IOAM trace/DEX）、RFC 9259（SRv6 OAM）、RFC 9789（MNA Framework）

---

## Changelog
| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-11 | v1.0 | 创建。IETF 三重 AI 网络标准深度分析：draft-zhang llmmoe-multicast-03（BIER 组播卸载，ZTE+中国移动）+ draft-ietf-mpls PBT-M-03（固定开销逐跳遥测，Futurewei/Huawei/Cisco）+ AIOps/NORIA 运维面；第一性原理三推论（动态高扇出匹配无状态复制/最小代价可观测/知识显性化）+ 三线闭环（执行-观测-决策）+ 中国厂商标准话语权分析 + 可证伪预判 H1-H5 |
