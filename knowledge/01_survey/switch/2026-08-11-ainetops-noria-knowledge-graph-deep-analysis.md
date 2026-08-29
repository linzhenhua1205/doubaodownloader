# 🧠 AIOps 用例 -02 + NORIA 知识图谱：网络运营智能化 IETF 化加速

> **类型**: 深度专题 | **日期**: 2026-08-11 | **定位**: draft-king-rokui-ainetops-usecases-02（71 页全文）+ draft-tailhardat-nmop-incident-management-noria-05/-01（双文档全文）技术原理深挖——AIOps 用例体系（13 大受益域 + 22 用例 + Agent 可观测性）+ NORIA 知识图谱（ITSM-KG 构建策略/ETL 流水线/开源实现）；衔接 [`2026-08-11-ietf-ai-network-standards-deep-analysis.md`](2026-08-11-ietf-ai-network-standards-deep-analysis.md)（三线总览，此前的「全文待补」已补齐）、[`2026-08-11.md`](2026-08-11.md)（追踪速记）
> **数据源**: IETF Datatracker 全文抓取（AIOps-02 全文 168.7KB + NORIA-05 全文 108.8KB + NORIA-01 全文 107.8KB）+ RFC 8345/9418 一手 + 第一性原理推导
> **关联文件**: [`2026-08-11-ainetops-noria-tech-details-deep-analysis.md`](2026-08-11-ainetops-noria-tech-details-deep-analysis.md)（技术细节篇·双文档体系 v2.0）、[`2026-08-11-ietf-ai-network-standards-deep-analysis.md`](2026-08-11-ietf-ai-network-standards-deep-analysis.md)、[`2026-08-11.md`](2026-08-11.md)、[`2026-08-11-llmmoe-multicast-bier-standard-deep-analysis.md`](2026-08-11-llmmoe-multicast-bier-standard-deep-analysis.md)、[`2026-08-11-mpls-pbt-m-on-path-telemetry-deep-analysis.md`](2026-08-11-mpls-pbt-m-on-path-telemetry-deep-analysis.md)

---

## 📑 目录

- [0. 一句话结论](#0-一句话结论)
- [1. 事实基线（一手全文验证）](#1-事实基线一手全文验证)
- [2. AINetOps 定义与受益域全景（13 域）](#2-ainetops-定义与受益域全景13-域)
- [3. 用例深挖：6.1 主动/被动保障 + 6.15 多代理 + 6.17 韧性测试](#3-用例深挖61-主动被动保障--615-多代理--617-韧性测试)
- [4. Agent 可观测性、干预与控制（第 7 节横切）](#4-agent-可观测性干预与控制第-7-节横切)
- [5. NORIA 知识图谱：ITSM-KG 技术框架](#5-noria-知识图谱itsm-kg-技术框架)
- [6. NORIA 构建策略：YANG→KG 双路径 + 对齐 + ETL](#6-noria-构建策略yangkg-双路径--对齐--etl)
- [7. 第一性原理：知识显性化→可计算化的三步](#7-第一性原理知识显性化可计算化的三步)
- [8. 与知识库既有框架互证](#8-与知识库既有框架互证)
- [9. 数据缺口与可证伪预判](#9-数据缺口与可证伪预判)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 0. 一句话结论

> **draft-king-rokui-ainetops-usecases-02（71 页，2026-08-10）把「AI 驱动网络运营（AINetOps）」从零散工具叙事提升为 IETF 需求基线：13 大受益域、22 个用例、外加第 7 节横切的「Agent 可观测性/干预/控制」（ICON 工作）——首次把网络管理 Agent 的轨迹记录、审计归责、回滚终止作为标准需求写入。draft-tailhardat NORIA（-05/-01 双文档并行）则给出落地数据层：用知识图谱（ITSM-KG）把网络事件、拓扑、修复动作结构化，通过 YANG→OWL 转换 + ETL 流水线（事件流/联邦架构/分布式 RDBMS）实现跨运营商知识共享。两文档合起来是 AIOps 标准化的「需求层（用例）+ 数据层（知识图谱）」双基座。**

---

## 1. 事实基线（一手全文验证）

### 1.1 AIOps 用例文档属性

| 维度 | 内容 | 来源 |
|:-----|:-----|:-----|
| 标题 | Artificial Intelligence (AI) for Network Operations | IETF Datatracker 全文 |
| 版本/日期 | -02，2026-08-10（71 页）| 同上 |
| 作者 | King、Rokui 等（待核实完整作者列表）| 同上 |
| 状态 | Active Internet-Draft（individual）| 同上 |
| 结构 | 10 节：Intro / Conventions / AI-ML-DL-GenAI / AINetOps 定义 / 13 受益域 / 22 用例 / Agent 可观测性 / Security / Refs | 同上 |

### 1.2 NORIA 文档属性

| 维度 | 内容 | 来源 |
|:-----|:-----|:-----|
| 标题 | Knowledge Graphs for Cross-Operator Incident Management and Network Design | IETF Datatracker 全文 |
| 版本/日期 | **-05（nmop 版，2026-08-07）+ -01（独立版，2026-08-10）双文档并行** | 同上 |
| 作者 | Tailhardat 等（Orange）| 同上 |
| 状态 | Active Internet-Draft（individual）| 同上 |
| 结构 | 8 节：Intro / Conventions / ITSM-KG 学习共享 / 构建策略（YANG→KG/对齐/ETL）/ Experiments（NORIA/YANG2OWL 开源）/ Security / IANA / Refs | 同上 |
| 开源实现 | NORIA-O 本体（w3id.org/noria）、SMASSIF-RML、ssb-consum-up、grlc、SemNIDS、YANG2OWL | 同上 §5.2 |

---

## 2. AINetOps 定义与受益域全景（13 域）

### 2.1 定义（draft §4）

AINetOps = **将 AI/ML/DL/Gen-AI 应用于网络运营**，从「人工/规则式运维」转向「智能、自动、实时自适应、预测洞察、优化决策」的系统。

### 2.2 13 大受益域（draft §5，一手）

| # | 受益域 | 子域 |
|:--|:-------|:-----|
| 1 | Operator Network Assistance | Gen-AI 虚拟网络工程师（NLP 交互 + 深度学习异常分类 + 上下文理解）|
| 2 | Network Active and Reactive Assurance | 单层/多层（IP over Optical）排障；RCA |
| 3 | Predictive Analytics | 主动保障监控 / 异常检测 / 趋势预测 / 预测性维护 / 容量规划 |
| 4 | Network Operational Insights | 无需进一步分析 / 需进一步分析 |
| 5 | Network Configuration Management | 配置生成/验证/修复 |
| 6 | IP/Optical Multi-layer Planning | 跨层规划 |
| 7 | Cross-Layer and Multi-Layer Optimization | 跨层优化 |
| 8 | Traffic Optimization | 流量优化 |
| 9 | Closed-Loop Automation | 闭环自动化 |
| 10 | Network Maintenance and Cleanup | 维护与清理 |
| 11 | Network API Construction | 网络 API 构建 |
| 12 | AI-Driven Security Monitoring | AI 驱动安全监控 |
| 13 | Multi-Agent Interworking | 多代理协作 |

### 2.3 22 个用例清单（draft §6，一手）

| # | 用例 | 一句话 |
|:--|:-----|:-------|
| 6.1 | Network Active and Reactive Assurance | 单层/多层故障检测与 RCA（图 3/4 闭环）|
| 6.2 | Network Pro-active Assurance | 主动保障（预测性）|
| 6.3 | Network Anomaly Detection | 异常检测 |
| 6.4 | Network Predictive Maintenance | 预测性维护 |
| 6.5 | Detection of Network Misconfiguration | 误配置检测 |
| 6.6 | Generate Node Configuration | 节点配置生成 |
| 6.7 | Cognitive Search On Internal Operator Data | 内部运维数据认知搜索 |
| 6.8 | Network Operator Assistant | 网络运维助手 |
| 6.9 | Gen-AI based Network Operational Insights | 生成式运维洞察 |
| 6.10 | Network Traffic Prediction | 流量预测 |
| 6.11 | Multi-layer Use-case | 多层用例 |
| 6.12 | Multi-layer Network Planning | 多层网络规划 |
| 6.13 | Causality Discovery | 因果发现 |
| 6.14 | Network Clean Up | 网络清理 |
| 6.15 | Multi-Agent Interworking | 多代理协作（5 大挑战）|
| 6.16 | Network Traffic Management | 流量管理（短期/推理/长期三视角）|
| 6.17 | AI-Driven Resilience Testing | AI 驱动韧性测试（故障注入）|
| 6.18 | Energy Efficiency Optimization | 能效优化 |
| 6.19 | AI-Driven Green Energy Optimization | 绿能优化 |
| 6.20 | AI-Driven Policy Enforcement and Compliance Auditing | 策略执行与合规审计 |
| 6.21 | AI-Driven Network Slicing Optimization | 网络切片优化 |
| 6.22 | Other Use Cases | 其他 |

> **方法论亮点**：每个用例都从统一维度审视——requirements（含控制面/数据面交互）、IETF protocols（可复用/可扩展的标准）、AI techniques——这是**把 AI 需求翻译成 IETF 标准语言**的关键机制。

---

## 3. 用例深挖：6.1 主动/被动保障 + 6.15 多代理 + 6.17 韧性测试

### 3.1 6.1 多层保障：Gen-AI 多代理动态工作流（draft Figure 3 一手）

```
                    |-------------------|
     (E) |----------|  Gen-AI based     |
         |          |  Multi-Agent      |
         |          |  Dynamic workflow |
         |          |-------------------|
         v                  ^ (D)
 |---------------|          |
 |  P-PNC(s),    |    |-----------|
 |  O-PNC(s),    |    |   AIOps   |
 |  MDSC         |    | Assistant |
 |---------------|    |-----------|
         ^                ^ (C)
         | (A)            | (B)
 +-------+--------+       |
 | IP/Optical     |       |
 | Network        |
 +----------------+
```

**五步闭环**：
- (A) 故障发生（光纤中断/IP 丢包/TCA 越限）
- (B) 被动：操作员感知；主动：高层控制器自动检测（告警监控/遥测分析/客户报告）
- (C) 启动 AIOps-Assistant（AINetOps 前端）
- (D) Gen-AI 多代理动态工作流诊断 → 定位根因
- (E) 可选：推荐补救动作 + **闭环自动实施**（网络自动恢复）

**关键架构要素**：P-PNC/O-PNC/MDSC 控制器栈 + AIOps Assistant 前端 + Gen-AI 多代理后端——**主动保障 = 控制器自动检测 + AI 自动诊断 + 闭环恢复**，这是 AIOps 从「分析引擎」升级「执行引擎」的标准化表达（呼应 MEMORY「Agentic AIOps」主线）。

### 3.2 6.15 多代理协作：5 大挑战（draft 一手）

| # | 挑战 | 内容 |
|:--|:-----|:-----|
| 1 | Communication and Coordination | 通信频率/粒度平衡——避免过载代理间通信网络，保持足够协调 |
| 2 | Conflict Resolution and Decision Fusion | 多代理决策冲突消解与融合 |
| 3 | Consistency and Stability | 网络动态性下的状态一致性 |
| 4 | Trust and Security | 多代理环境的信任与安全 |
| 5 | Scalability and Management | 代理数量增长 → 通信开销/协调复杂度/管理成本 |

**两种通信模式**：(A) Agent↔Agent 协调通信；(B) H-Agent 人类↔Agent 通信。

### 3.3 6.17 AI 驱动韧性测试（draft 一手）

- **机制**：AI 设计并执行故障注入场景（丢包/时延尖峰/光信号劣化）→ 测试 IP/光网络在模拟故障下的检测/响应/恢复能力
- **数据**：历史故障数据（光纤中断/设备宕机）+ 实时遥测（时延/BER）+ 外部因素（天气/流量激增）
- **闭环**：预测高风险链路（如基于衰减趋势）→ 注入故障 → 监控响应 → 优化恢复策略
- **价值**：真实故障前验证自动恢复机制——**与本地「故障诊断/FTA/容错」P1 主线、可靠性测试（FT-HSDP）同向**

---

## 4. Agent 可观测性、干预与控制（第 7 节横切）

### 4.1 核心论断（draft 一手）

> "AI-native operations may be non-deterministic, network management agents can misbehave or deviate from expected behavior. Static AI guardrails... are insufficient for the full operational lifecycle."

**静态护栏（输入/输出/预动作过滤）不足以覆盖完整运维生命周期**——无法检测/中断/恢复机器速度下的非预期行为。→ 需要**持续可观测性 + 人工干预 + 行为控制**。

### 4.2 关键挑战（draft 一手，ICON 工作）

| # | 挑战 |
|:--|:-----|
| 1 | Agent 规划与决策的透明度有限 |
| 2 | 责任归因困难（具体 Agent 或人）|
| 3 | 缺乏标准化网络管理 Agent 基准测试 |
| 4 | 缺乏对长时自主工作流的人类监督 |
| 5 | 缺乏回滚与终止命令、缺乏人↔Agent 双向交互通道 |

### 4.3 四维解决方案框架（draft 一手）

| 维度 | 内容 |
|:-----|:-----|
| **Architecture** | Agent 行为捕获为**轨迹记录**（trajectory records）：推理序列/动作/观察的结构化痕迹；人类监督通道（监控/注入策略/纠正）|
| **Interfaces/APIs** | 两个互操作接口：遥测接口（轨迹/日志/指标）+ 人-Agent 交互接口（干预/控制）|
| **Protocols** | 遥测协议扩展；优先复用 NETCONF/RESTCONF（供给干预与控制策略）；**与 OpenTelemetry 社区协同** |
| **Data Models** | **共同 schema 缺口**：Agent 行为 trace/log/metric 结构、支持可审计/归责的轨迹记录、干预/控制策略元素——互补 draft-smith-opsawg-ai-network-governance |

**与知识库主线互证**：
- 轨迹记录 = Agent 六层（Prompt→Loop→工具面→Skills→编排→Channel）的可观测化
- 人机监督通道 = 「HITL/授权语义 SDK 级化」的标准侧表达
- OTel 协同 = 带内/带外双轨遥测主线在 Agent 层延伸

---

## 5. NORIA 知识图谱：ITSM-KG 技术框架

### 5.1 动机（draft NORIA §1 一手）

**问题链**：
1. 事件管理需要同时快速关联大量异构技术信息源
2. YANG 广泛用于描述网络状态/配置，但 **YANG 数据模型间关键概念（如拓扑）对齐不足**
3. YANG 范围不覆盖网络生态（物理设备位置/组织/监控系统）与 ITSM 视角（业务流程/设计规则/计划变更/修复动作）
4. 知识资本化被锁在各运营商内部 → **跨运营商共享失败模式与最佳实践受阻**

**解法**：ITSM Knowledge Graph（ITSM-KG）——用语义网技术（RDF/RDFS/OWL/SKOS）把网络部署、异常检测、风险管理结构化。

### 5.2 三层本体架构（draft §4.2 一手）

```
+-------------------------------------------------+
|  ONTO-META (meta-ontology: ops context analysis)|
|  - network lifecycle, events, diagnosis, repair |
+-------------------------------------------------+
|  ONTO-YANG-MODEL (RDFS/OWL equiv of YANG models) |
|  - RFC8345 network / RFC9418 service-assurance   |
+-------------------------------------------------+
|  instance layer: KG data of devices/events/topo  |
+-------------------------------------------------+
```

- **ONTO-META** = 分析运维上下文的元本体（NORIA-O 本体即此层）
- **ONTO-YANG-MODEL** = 每个 YANG 模型翻译成 RDFS/OWL（Figure 2 示例：RFC 8345 "node" → owl:Class）

**对齐示例（draft 一手）**：RFC 8345 的 "node" 概念 ↔ NORIA-O 的 "noria:Resource" 概念断言语义等价——这是把 YANG 数据模型语义接入本体层的桥梁。

### 5.3 关联需求（draft §3.2 SIMAP）

- 与 Service & Infrastructure Maps（SIMAP）相关——核心需求（core）/设计需求（design）/架构需求（architectural）三层
- 衔接网络数字孪生愿景（draft-irtf-nmrg-network-digital-twin-arch）

---

## 6. NORIA 构建策略：YANG→KG 双路径 + 对齐 + ETL

### 6.1 YANG→KG 两条路径（draft §4.1 一手）

| 路径 | 语义 | 工程难度 | 实现性 |
|:-----|:-----|:---------|:-------|
| **EQUIVALENCE** | 目标本体 = YANG 模型精确等价 | 需大量知识工程对齐所有 YANG 模型 | 相对易实现（RML 规则即可）|
| **GENERALIZATION** | 目标本体 = YANG 模型的泛化 | 需转换 YANG→RDFS/OWL + 识别关键概念对齐 | 更具表达力，服务跨模型分析 |

**GENERALIZATION 两步**：
1. 把 YANG 数据模型转换为 RDFS/OWL 等价（一致解释配置数据）
2. 识别这些模型与更富表达力本体（如 NORIA-O）的关键概念对齐

**示例**：把 RFC 8345（Network Topologies）+ RFC 9418（Service Assurance）集成进 NORIA-O 结构化 KG。

> **对齐理论依据**：YANG 模型设计本身依赖概念层级与通用概念复用（如 RFC 8345 的 Abstract Network Model）→ 对齐识别在理论上受益于此。

### 6.2 对齐方法（draft §4.2）

- 两种对齐实现：Ontologies Network 方法 / ONTO-META 显式链接
- 模型间对齐技术超出本文档范围（引用 ONTO-MATCH-2022 文献）——**诚实标注边界**

### 6.3 ETL 流水线（draft §4.3 一手）

**模式一：KG-only 事件流集成（Figure 8/9）**

```
Events -> E.S.B. -> Stream mapping -> S.S.B. -> Stream loader -> K.G.
                          |
              (event/LOG_login_03) => (object/RES/router1)
              events map to ONTO-META, entities map to ONTO-YANG-MODEL
```

**模式二：KG + TSDB 混合（Figure 10/11）**

```
Events -> E.S.B. -> Stream mapping -> S.S.B. -> Stream loader -> K.G.
                        |                              |
                        |                  +--------+ +------+
                        +----> Stream loader ->| TSDB   |
                                               +--------+ +------+
```

- **分工**：KG 做上下文分析，TSDB 做趋势分析
- **双向链接**：KG 聚合数据可下钻 TSDB 原始数据，反之亦然
- **性能**：事件流高速 → 各 DBMS 专用 I/O 优化（TSDB 流式 + 图数据库）

### 6.4 联邦数据架构 + 分布式 RDBMS（draft §4.3.2-4.3.3）

- **联邦数据架构**：跨数据源（工单系统/监控/配置管理数据库）持续集成
- **分布式 RDBMS**：处理动态网络拓扑与 schema 演化
- **核心价值**：KG 隐式持有学习事件上下文（拓扑/状态/事件序列）与修复流程（动作/配置变更）所需的信息

### 6.5 开源实现（draft §5.2 一手）

| 组件 | 作用 | 开源地址 |
|:-----|:-----|:---------|
| **NORIA-O** | IT 网络/事件/运维信息本体（RDF/OWL/SKOS）| w3id.org/noria |
| **SMASSIF-RML** | 语义流处理 + 声明式数据映射 | github.com/Orange-OpenSource/smassif-rml |
| **ssb-consum-up** | Kafka→SPARQL 网关（语义服务总线）| github.com/Orange-OpenSource/ssb-consum-up |
| **grlc** | SPARQL 查询调用/版本化（GitLab 接口）| github.com/Orange-OpenSource/grlc |
| **SemNIDS** | 测试台：流量生成 + NIDS + KG + 流程挖掘 + 一致性检查 | （Orange 开源）|
| **YANG2OWL** | YANG 数据模型 → OWL 本体转换器 | （draft §5.2.2）|

**NORIA-O 应用三路线**（draft 一手）：
- **模型化设计**（SLKG-2023）：查询图检索异常及其上下文
- **统计学习**（SLKG-2023）：基于上下文相似性关联实体 → 告警与修复引导
- **流程挖掘**（GPL-2024）：实体序列对齐活动模型 → 引导修复动作
- **Web UI**（NORIA-UI-2024）：知识图谱探索设计，组合以上技术

---

## 7. 第一性原理：知识显性化→可计算化的三步

### 7.1 AI 运维的价值链

> AI 运维的价值 = **把隐性知识显性化、把显性知识可计算化**。

```
tacit knowledge (expert exp) -> explicit knowledge (use case doc / KG schema)
                           -> computable knowledge (KG query / process mining / stat learning)
                           -> shareable knowledge (cross-operator federation / open ontology)
```

**AIOps 用例文档**定「要解决什么」（需求层），**NORIA 知识图谱**定「知识怎么组织」（数据层）——两者合起来是 AIOps 标准化的「需求层 + 数据层」双基座。

### 7.2 为什么知识图谱而非纯向量/纯规则

| 方案 | 优势 | 局限 |
|:-----|:-----|:-----|
| 规则系统 | 确定、可解释 | 不可扩展、不覆盖未知场景 |
| 向量检索（RAG）| 灵活、语义相似 | 无结构关系、难推理多跳 |
| **知识图谱（KG）** | **结构化关系、多跳推理、可解释、可共享** | 构建成本高（对齐/ETL）|

NORIA 的取舍：KG 构建成本高（YANG 对齐、ETL 流水线），但换来**跨运营商可共享 + 可审计 + 多跳推理**——这是故障诊断场景的核心诉求（知识库「故障诊断/FTA/容错」主线同向）。

### 7.3 与本地「记忆治理」互证

- KG 的「实体-属性-时间」三维 = 与 MindMemOS 自演进记忆（实体-属性-时间三维 + 离线整理）同构
- 事件流 ETL = 「事件 → 结构化知识」的流水线，与知识库「暂存/导入→加工/挖掘→提取/沉淀」受控管线同构
- 跨运营商共享 = 知识共享而非数据共享（只共享模型/本体，不共享原始数据）——隐私友好

---

## 8. 与知识库既有框架互证

| 既有框架 | 互证结论 |
|:---------|:---------|
| MEMORY「Agentic AIOps：分析引擎→执行引擎」| AIOps 用例 6.1 主动保障（自动检测+AI 诊断+闭环恢复）是执行引擎的标准表达 |
| MEMORY「Agent 六层 + 授权语义 SDK 级化」| 第 7 节 Agent 轨迹记录/干预/控制 = 六层可观测化 + HITL 的标准侧 |
| 可靠性测试（FT-HSDP/故障注入）| 6.17 AI 驱动韧性测试 = 故障注入方法论 IETF 化 |
| 带内/带外双轨遥测（OTel/OTLP）| 第 7 节明确「与 OpenTelemetry 社区协同」——Agent 遥测接入统一平面 |
| 记忆研究（MindMemOS 三维/证据标注）| KG 实体-属性-时间三维 + 事件流 ETL 与记忆治理同构 |
| 知识库受控管线（暂存→加工→提取）| NORIA ETL（E.S.B→映射→S.S.B→loader）同构 |
| [`2026-08-11-mpls-pbt-m-on-path-telemetry-deep-analysis.md`](2026-08-11-mpls-pbt-m-on-path-telemetry-deep-analysis.md) | PBT-M 提供网络层逐跳数据 → AIOps/NORIA 消费做诊断——观测面→决策面闭环 |
| [`2026-08-11-llmmoe-multicast-bier-standard-deep-analysis.md`](2026-08-11-llmmoe-multicast-bier-standard-deep-analysis.md) | BIER 优化数据面执行 → AIOps 反馈优化策略——执行面闭环 |

---

## 9. 数据缺口与可证伪预判

### 9.1 数据缺口（诚实标注）

| 缺口 | 说明 |
|:-----|:-----|
| 实验数据 | AIOps 用例文档为需求基线，无实现/评测数据；NORIA 有开源实现但实验为「Implementation Status」（YANG2OWL 转换器 + NORIA 组件），无端到端基准数据 |
| 多代理标准 | 6.15 只列 5 大挑战，无具体协议/接口设计（inter-agent 通信协议未定）|
| Agent 可观测性 schema | 第 7 节明确「common schema 是 key gap」——尚需 draft-smith-opsawg-ai-network-governance 等互补 |
| 对齐技术 | YANG 模型间对齐算法引用外部文献（ONTO-MATCH-2022），本文档不展开 |
| 跨运营商实际部署 | 知识共享的治理/法律/竞争顾虑未展开（只提「共享模型不共享数据」方向）|

### 9.2 可证伪预判（2027 年核验）

| # | 预判 | 核验方式 |
|:--|:-----|:---------|
| H1 | AIOps 用例催生 nmop 新 work item（网络 AI 数据模型/遥测接口标准）| 跟踪 nmop WG 议程 |
| H2 | Agent 可观测性 schema 12 个月内出独立 draft（基于第 7 节需求）| 跟踪 opsawg/nmop 新 draft |
| H3 | NORIA 知识图谱在 2+ 运营商部署或跨运营商试点（Orange 主导）| 厂商/会议发布 |
| H4 | 2027 年 IETF 出现「AI 训练网络」专属 WG/BOF（三线合流组织化）| 跟踪新 WG/BOF |

---

## 参考来源

### 外部一手
- IETF Datatracker: draft-king-rokui-ainetops-usecases-02（2026-08-10，71 页全文）— https://datatracker.ietf.org/doc/draft-king-rokui-ainetops-usecases/
- IETF Datatracker: draft-tailhardat-nmop-incident-management-noria-05（2026-08-07，全文）— https://datatracker.ietf.org/doc/draft-tailhardat-nmop-incident-management-noria/
- IETF Datatracker: draft-tailhardat-incident-management-noria-01（2026-08-10，全文）— https://datatracker.ietf.org/doc/draft-tailhardat-incident-management-noria/
- RFC 8345（Network Topologies）、RFC 9418（Service Assurance）、RFC 6241（NETCONF）、RFC 8040（RESTCONF）
- draft-smith-opsawg-ai-network-governance、draft-irtf-nmrg-llm-nm、draft-irtf-nmrg-network-digital-twin-arch（draft 引用）
- NORIA-O 本体: https://w3id.org/noria/ ；SMASSIF-RML / ssb-consum-up / grlc: github.com/Orange-OpenSource/

### 内部知识库
- [`2026-08-11-ietf-ai-network-standards-deep-analysis.md`](2026-08-11-ietf-ai-network-standards-deep-analysis.md) — 三线总览（此前「全文待补」已补齐）
- [`2026-08-11.md`](2026-08-11.md) — 追踪速记
- [`2026-08-11-mpls-pbt-m-on-path-telemetry-deep-analysis.md`](2026-08-11-mpls-pbt-m-on-path-telemetry-deep-analysis.md) — 观测面对偶
- [`2026-08-11-llmmoe-multicast-bier-standard-deep-analysis.md`](2026-08-11-llmmoe-multicast-bier-standard-deep-analysis.md) — 执行面对偶
- MEMORY.md — Agentic AIOps / Agent 六层 / 带内遥测 / 记忆治理 / 受控管线

---

## Changelog
| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-11 | v1.0 | 创建。draft-king-rokui-ainetops-usecases-02（71 页全文）+ NORIA 双文档（-05/-01 全文）深度分析：AINetOps 13 受益域 + 22 用例清单、6.1 多层保障五步闭环、6.15 多代理 5 大挑战、6.17 韧性测试、第 7 节 Agent 可观测性/干预/控制（ICON + 四维框架）、NORIA ITSM-KG 三层本体架构、YANG→KG 双路径（EQUIVALENCE/GENERALIZATION）、ETL 双模式（KG-only/KG+TSDB）、开源实现全景（NORIA-O/SMASSIF-RML/ssb-consum-up/grlc/SemNIDS/YANG2OWL）、知识显性化三步第一性原理、可证伪预判 H1-H4 |
