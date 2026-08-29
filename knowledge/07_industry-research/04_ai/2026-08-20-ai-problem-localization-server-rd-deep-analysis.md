# AI 在服务器研发问题定位活动中的应用进展（2024-2026）：共性识别、二供排查与疑难定位

> 深度分析 | 2026-08-20 | 素材：arXiv 2025-2026 日志分析/RCA 论文（一手）× 15+、厂商平台官方页（阿里云 SLS / 华为 eSight / NVIDIA DCGM）、既有知识库容错/RAS 分析交叉引用、工程经验推断（已分级标注）
> 主线：**过去两年（2024-2026），AI 在问题定位领域的角色从「规则外挂的统计告警」跃迁为「LLM 语义理解 + Agent 自主执行」的组合能力；在服务器研发侧，共性识别（批量/跨机型共模挖掘）、二供排查（替代料差异定位）、疑难 RCA（偶发跨层故障）三类活动的 AI 应用成熟度依次递增，共性识别最成熟、二供排查最薄弱、疑难定位最具爆发力。**
> **概要**: 梳理 2024-2026 年 AI 在服务器研发问题定位三类活动（共性识别/二供排查/疑难 RCA）的应用进展与成熟度，覆盖日志解析、Agent 诊断、硬件 FA 等一手论文与厂商平台。
> **关键词**: 问题定位 · 根因分析 · 日志分析 · Agentic AIOps · 二供排查 · 共性识别 · 服务器研发

---

## 📑 TOC

- [一、执行摘要](#一执行摘要)
- [二、背景与范围：服务器研发的三类问题定位活动](#二背景与范围服务器研发的三类问题定位活动)
- [三、技术底座演进：2024-2026 发生了什么](#三技术底座演进2024-2026-发生了什么)
- [四、应用一：共性问题识别](#四应用一共性问题识别)
- [五、应用二：二供问题排查](#五应用二二供问题排查)
- [六、应用三：疑难问题定位分析（RCA）](#六应用三疑难问题定位分析rca)
- [七、效果对比矩阵](#七效果对比矩阵)
- [八、后续发展方向](#八后续发展方向)
- [九、对研发团队的落地建议](#九对研发团队的落地建议)
- [十、诚实标注与局限](#十诚实标注与局限)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 一、执行摘要

2024-2026 年，AI 在「问题定位」领域的应用发生了三个可验证的跃迁 [来源: arXiv 论文与厂商官方页，见正文各节]：

1. **日志分析从「统计/深度模型」走向「LLM 语义理解」**：零样本 LLM 日志异常检测 F1 达 0.82-0.91（无需标注，实战可部署）[来源: arXiv:2604.12218]；LLM 合成正则的日志解析将下游误报降低 30% 以上 [来源: arXiv:2604.20553]。
2. **根因分析从「图模型排序」走向「Agent 自主诊断闭环」**：2026 年 Agentic AIOps 成为主流叙事，从「分析引擎」升级为「执行处置引擎」（详见 [agentic-aiops-2026-narrative](../04_ai/2026-08-07-agentic-aiops-2026-narrative-deep-analysis.md)）。
3. **硬件侧从「无 AI」走向「AI 辅助 FA」**：工业异常检测 MLLM 化（零样本准确率 77.31% [来源: arXiv:2608.09789]），器件/缺陷检测的视觉 AI 已规模化商用（Fab 级），但**二供整机级差异定位仍是最薄弱的环节**——数据稀疏 + 物理机理复杂 + 案例库未结构化，是业界共同短板。

**三类活动成熟度排序**：共性识别（★★★★，已有成熟工具链）> 疑难 RCA（★★★，爆发期）> 二供排查（★★，蓝海）。

---

## 二、背景与范围：服务器研发的三类问题定位活动

### 2.1 与运维侧 AIOps 的边界

| 维度 | 研发侧问题定位（本文） | 运维侧 AIOps（已有分析） |
|:-----|:----------------------|:------------------------|
| 时间窗 | 量产前/导入期/退回件 | 运行时/生产环境 |
| 数据 | 试产日志、RMA 件、问题单、器件批次 | 线上遥测、指标、trace |
| 目标 | 找根因→改设计/换料/修固件 | 找根因→恢复服务/防复发 |
| 样本量 | 少（单机/小批量），标签稀缺 | 大（全集群），标注成本高 |
| 典型输出 | ECN/ECO、替代料判定、设计变更 | 告警工单、自动处置动作 |

运维侧 Agentic AIOps 的完整分析见交叉链接 [agentic-aiops-2026-narrative](../04_ai/2026-08-07-agentic-aiops-2026-narrative-deep-analysis.md)，本文不重复。

### 2.2 三类活动的定义与难点

**A. 共性问题识别（Common-issue Identification）**
- 定义：从大批量试产/量产/退回数据中识别「跨批次、跨机型、跨供应商」的共模故障模式，如某批 PCB 焊点不良、某固件版本系统性触发、某器件批次漂移。
- 难点：日志非结构化且海量；共模信号淹没在个例噪音中；跨维度关联（时间×批次×机型×器件）依赖人工经验。
- 对应研发活动：批量退回件分析、试产共模拦截、市场质量问题（MQR）归因。

**B. 二供问题排查（Second-source Issue Diagnosis）**
- 定义：国产化/降本驱动的替代料（second source）导入后，在整机层面暴露的差异性问题定位——替代料本身合格，但与主设计（时序、驱动、兼容矩阵）不匹配导致偶发故障。
- 难点：器件级数据（datasheet/批次/工艺）与整机级数据（日志/信号）跨层隔离；差异往往在应力边界才暴露；历史 FA 案例未结构化，经验难复用。
- 对应研发活动：替代料验证、器件认证（qualification）、失效分析（FA）、BOM 兼容矩阵维护。

**C. 疑难问题定位分析（Hard RCA）**
- 定义：偶发（intermittent）、跨层（硬件×固件×驱动×应用）、依赖特定数据/负载/温度条件的疑难故障定位。
- 难点：不可复现或低复现率；证据分散在日志/指标/trace/配置多源；需要专家领域知识（SI/协议/热/电）推理。
- 对应研发活动：升级遗留问题、竞品对比故障、客户投诉攻坚、RAS 根因分析。

---

## 三、技术底座演进：2024-2026 发生了什么

### 3.1 三阶段演进

```text
Stage 1 (<=2023): Traditional ML log analysis
  Rule+Stats+DNN(DeepLog/LogBERT) | high label cost | poor generalization | alert-centric

Stage 2 (2024-2025): LLM semantic understanding
  Zero/few-shot log anomaly detection | RAG grounding | LLM-based log parsing
  | label-free | high cost | poor calibration

Stage 3 (2025-2026): Agent autonomous closed loop
  Multi-source evidence fusion(RCAgent/AiOpsLab) | tool calling / hypothesis verification
  | distilled lightweight(FAME/LogICL) | calibration(LoRD) | observability-driven repair(ORCA)
```

### 3.2 关键使能技术（每项均可溯源）

| 使能技术 | 代表工作 | 2024 前状态 | 2026 状态 | 来源 |
|:---------|:---------|:-----------|:----------|:-----|
| 日志解析 | Drain（规则聚类） | 复杂变量识别差 | DeepParse：LLM 合成正则，Parsing Acc 97.6% | [arXiv:2604.20553] |
| 异常检测 | DeepLog/LogBERT | 需大量标注 | 零样本 LLM F1 0.82-0.91；消息级 MoE F1 98.16@K=100 | [arXiv:2604.12218][arXiv:2605.22779] |
| 根因分析 | 图/时序模型 | 单源数据 | Agent 多源证据融合 + 工具执行 | [arXiv:2402.09355 类] |
| 知识检索 | — | 无 | RAG 历史案例/日志语义增强（EnrichLog/LogICL） | [arXiv:2512.11997][arXiv:2512.09627] |
| 数据质量 | 人工清洗 | 成本高 | LogPurge LLM 净化：移除 98.74% 异常保留 82.39% 正常 | [arXiv:2511.14062] |
| 可靠性 | — | 过度自信 | LoRD 后处理校准（ICDM 2026） | [arXiv:2608.17965] |

### 3.3 成本约束的现实折中

LLM 逐行推理日志成本不可行 → 2025-2026 的主流工程范式是**「LLM 离线/少量标注 + 轻量模型在线推理」**：
- FAME：LLM 每模板仅标注 K 行，在线 MoE 路由，标注量降 76 倍 [来源: arXiv:2605.22779]
- DeepParse：LLM 推理与执行分离，延迟降 36% [来源: arXiv:2604.20553]
- LogICL：LLM 推理蒸馏到轻量 encoder [来源: arXiv:2512.09627]
- HYVE：混合视图上下文工程，token 用量降 50-90% [来源: arXiv:2604.05400]

---

## 四、应用一：共性问题识别

### 4.1 AI 介入的功能点（研发现场视角）

```text
Input layer : BMC SEL / BIOS log / OS log / system test log / RMA return info
   | unified collection & structuring
Parsing layer: LLM log parsing(Drain+LLM regex) -> template library + variable extraction
   v
Clustering layer: template freq clustering | alert association rule mining | time-series pattern matching
   v
Common-mode layer: cross-dim aggregation(batch x model x FW version x part lot) -> common candidates
   v
Human layer: candidate RCA ranking + similar case RAG retrieval -> engineer confirmation
```

### 4.2 典型软件与功能点

| 类别 | 代表软件/方案 | 功能点 | 成熟度 |
|:-----|:-------------|:-------|:------:|
| 开源日志分析 | LogPAI（微软，DeepLog/LogAnomaly/Drain） | 模板解析、异常检测、聚类 | ★★★★ |
| 云平台 | 阿里云 SLS（日志服务） | 统一采集、百亿行秒级检索、告警/字段分析 | ★★★★ |
| 云平台 | 华为 eSight / FusionDirector | E2E 故障监控、场景化视图、服务器统一管理 | ★★★★ |
| 可观测性 | Datadog / Dynatrace | 日志聚类、Watchdog 自动异常发现、Davis AI 关联 | ★★★★ |
| LLM 解析 | DeepParse / VarParser | 日志解析准确率 97.6%；变量信息保留 | ★★★ |
| LLM 检测 | FAME / EnrichLog / LogICL | 消息级检测 F1 98.16；RAG 增强；跨域迁移 | ★★★ |
| 数据净化 | LogPurge | 污染日志自动清洗，训练数据质量门禁 | ★★★ |

[来源: arXiv:2604.20553 / arXiv:2605.22779 / arXiv:2512.11997 / arXiv:2512.09627 / arXiv:2511.14062；阿里云 SLS 官网；华为 eSight 官网]

### 4.3 服务器场景的典型应用与效果

1. **批量退回件共模分析**：将 RMA 退回原因描述（自然语言）+ 日志特征聚类，自动识别「同批次同故障码」聚集，替代人工翻单。LLM 对问题单的语义聚类可直接降低人工 60-80% 的归类工作量（工程经验推断，非厂商公开数据）。
2. **试产共模拦截**：测试日志实时流式解析，模板级异常检出（如某 pin 电压异常模式在 3 台样机同时出现）→ 触发共模告警。
3. **固件版本回归共模**：跨版本日志对比（A/B 版本模板差异挖掘），定位「新固件引入的系统性告警」，数据支撑：LLM 零样本检测 F1 0.82-0.91 已可实战 [来源: arXiv:2604.12218]。
4. **效果量化锚点**：公共基准（HDFS/BGL/Thunderbird/Spirit）上微调 transformer F1 0.96-0.99、零样本 LLM F1 0.82-0.91 [来源: arXiv:2604.12218]；数据增强 AnomalyGen 使 HDFS 无监督 Transformer 从 0.818 提升至 0.970 [来源: arXiv:2604.11107]。

**成熟度判断**：共性识别是三类中最成熟的——工具链完整（采集→解析→聚类→呈现）、效果有公开量化、服务器厂商/云厂商均已产品化。

---

## 五、应用二：二供问题排查

### 5.1 问题结构：为什么二供排查最难 AI 化

二供排查的本质是**「器件合格 ≠ 整机兼容」**的差异定位，数据特征：
- 样本量极小（单料导入验证通常 ≤ 数十台），异常检测类算法无用武之地
- 证据跨层：器件电参数（datasheet/批次）↔ 整机时序/信号（SI 测试/示波器）↔ 日志现象
- 机理依赖物理（时序裕量、驱动强度、温漂），纯数据驱动难以建模
- 历史 FA 案例以报告/邮件形式散落，未结构化 → LLM 无法检索复用

### 5.2 AI 介入的功能点（按环节）

```text
[1] Part qualification phase
    LLM parses datasheet / vendor docs -> auto parameter extraction & diff vs primary part
    ML reliability prediction (from historical lot / process / stress data)
    AI review of vendor qualification data (document validation, consistency check)

[2] Small-batch validation
    System test log + part parameter joint analysis (LLM cross-source reasoning)
    Auto-designed boundary sweep (temp / voltage / load) -> expose differences

[3] Batch anomaly localization
    RMA root-cause attribution: log pattern + part lot traceability correlation
    FA assistance: X-ray / SAM(acoustic) / thermal imaging AI defect recognition

[4] Knowledge accumulation
    Part failure-mode knowledge graph | FA case RAG retrieval | auto-maintained compat matrix
```

### 5.3 典型软件与功能点

| 类别 | 代表软件/方案 | 功能点 | 成熟度 |
|:-----|:-------------|:-------|:------:|
| 半导体检测（Fab 级） | KLA / Onto Innovation / 应用材料 | 深度学习晶圆缺陷检测、review 分类 | ★★★★★（Fab 内） |
| 工业视觉 | MLLM 异常检测（ADOPD 类） | 零样本 77.31% 准确率（MMAD） | ★★★ |
| 可靠性预测 | 自研 ML（器件批次失效建模） | 批次风险评分、早期失效预警 | ★★ |
| 文档智能 | LLM datasheet 解析/参数比对 | 替代料参数差异自动清单 | ★★★（可用） |
| FA 知识库 | 自研 RAG（历史 FA 报告） | 相似失效案例检索、机理参考 | ★★（数据前提） |
| 失效分析设备 | X-ray/SAM/红外 + AI 图像识别 | 缺陷自动分类 | ★★★ |

[来源: arXiv:2608.09789（ADOPD）；半导体检测为行业公开共识，未取厂商具体数字]

### 5.4 现实效果与瓶颈

- **能做**：器件参数比对、文档核验、视觉缺陷检测（Fab 侧已成熟）、失效案例检索——这些是「单点提效」，可把替代料评估周期缩短 30-50%（工程经验推断，行业报告口径不一，待独立验证）。
- **做不好**：整机级「二供差异疑难定位」——需要物理机理 + 稀疏数据 + 跨层证据的联合推理，目前**没有成熟产品**，业界停留在「LLM 辅助分析 + 专家确认」半自动状态。这也是 AI 在服务器研发问题定位中最值得投入的蓝海。

---

## 六、应用三：疑难问题定位分析（RCA）

### 6.1 技术路线演进

```text
Route A: Time-series/graph anomaly detection + RCA ranking (2022-2024 mainstream)
   metrics/log -> anomaly score -> causal/correlation graph -> root-cause Top-N
   e.g. Microsoft GNN RCA, causal-inference methods | limit: single-source, labeled topology

Route B: LLM multi-source evidence fusion (2024-2025)
   log+metric+trace+config -> LLM context aggregation -> root cause + confidence
   e.g. RCAgent, Eadro, LogPrompt | limit: context window, hallucination, calibration

Route C: Agent autonomous diagnosis loop (2025-2026)
   Agent plan -> call tools(query logs / run cmds / reproduce) -> observe -> iterate -> conclusion+fix
   e.g. AiOpsLab(benchmark), ORCA(observability-driven repair), Dynatrace autonomous SRE
   | limit: trust boundary, execution safety, auditability
```

### 6.2 服务器研发侧的特殊性

与云原生微服务 RCA 相比，服务器硬件疑难定位的差异：
- **复现难**：偶发故障可能数周才复现，Agent 的「主动复现」能力受限 → 更依赖历史案例推理
- **信号域**：除日志外有波形（眼图/抖动）、时序（协议）、热/电参数 → 多模态 Agent 是方向
- **知识封闭**：RCA 专家知识（SI/协议/热）难以外化为可训练数据 → 企业私有 RAG 是关键
- **万卡集群训练故障**（与本行业最相关的新场景）：NVIDIA DCGM 提供 GPU 健康监控/诊断/根因 [来源: NVIDIA DCGM 官方页]；Meta/Google 已公开训练故障分析实践（见容错专题 [fault-tolerance-four-papers](../10_supernode-rack/2026-08-07-fault-tolerance-four-papers-deep-analysis.md)）

### 6.3 典型软件与功能点

| 类别 | 代表软件/方案 | 功能点 | 成熟度 |
|:-----|:-------------|:-------|:------:|
| GPU 集群 | NVIDIA DCGM / Base Command | 主动健康监控、诊断、功率/时钟治理、根因定位 | ★★★★ |
| 可观测性 | Dynatrace Davis / Datadog Bits AI | 因果关联、自动根因、AI 助手问答 | ★★★★ |
| 开源基准 | AiOpsLab（2025） | Agent 运维诊断标准基准 | ★★★ |
| 学术 RCA | RCAgent（2024）类 | 工具增强 LLM Agent 根因分析 | ★★★ |
| 修复闭环 | ORCA（ASE 2026） | 可观测性驱动的微服务故障修复 | ★★★ |
| 服务器管理 | 华为 iBMC/FusionDirector、Dell iDRAC | 带外管理、SEL 告警、预测性分析 | ★★★★ |
| 案例检索 | 企业 RAG（历史问题单/FA 报告） | 相似案例召回、经验复用 | ★★★ |

[来源: NVIDIA DCGM 官方页；arXiv:2608.17018（ORCA）；既有知识库 BMC 专题]

### 6.4 效果量化

- 运维侧 MTTR 缩短是 Agentic AIOps 的核心卖点（Dynatrace 自主 SRE / PagerDuty 2026 年 7 月密集发布，详见 [agentic-aiops-2026-narrative](../04_ai/2026-08-07-agentic-aiops-2026-narrative-deep-analysis.md)），但**研发侧疑难 RCA 的公开量化数据极少**——这是「效果呈现」的最大缺口，多数停留在 case study 层面。
- 可验证锚点：ORCA 面向微服务故障修复（ASE 2026 录用）[来源: arXiv:2608.17018]；DCGM 明确将「识别故障/性能退化/功耗异常及其根因」列为核心能力 [来源: NVIDIA DCGM 官方页]。
- 服务器疑难定位的典型诉求（MTTR 从周级→天级、复现率提升、专家经验数字化）尚缺行业统一度量。

---

## 七、效果对比矩阵

| 维度 | 共性识别 | 二供排查 | 疑难 RCA |
|:-----|:--------|:---------|:---------|
| 技术成熟度 | ★★★★ | ★★ | ★★★ |
| 工具链完整度 | 完整（采集→解析→聚类→呈现） | 单点工具，无整机级方案 | 平台化起步（Agent） |
| 公开量化数据 | 丰富（F1/误报率/标注降本） | 稀缺（Fab 级除外） | 稀缺（运维侧多、研发侧少） |
| 服务器厂商产品化 | 有（SLS/eSight/FusionDirector） | 基本无 | 部分（DCGM/iDRAC 预测性） |
| 主要瓶颈 | 长尾事件/漂移 | 数据稀疏+物理机理 | 复现难+信任边界 |
| 落地 ROI 判断 | 高（立即可做） | 中（做知识库先行） | 高（长期护城河） |
| 代表量化锚点 | 零样本 F1 0.82-0.91；误报 -30% | ADOPD 77.31%；评估周期 -30~50%* | MTTR 缩短（运维侧）* |

> *标注项为工程经验推断/行业口径，未获独立源验证，见第十节。

---

## 八、后续发展方向

### 8.1 技术方向（可证伪预测）

1. **Agent 化自主诊断下沉到硬件层**：BMC 内嵌轻量推理（Tiny LLM + 蒸馏），带外完成 SEL/日志的初步 RCA，云端 Agent 处理疑难——「边缘初筛 + 云端攻坚」两级架构。
2. **多模态故障证据融合**：日志 + 波形（眼图/抖动）+ 热/电遥测 + 器件图像 → 多模态 LLM 统一推理；工业异常检测 MLLM 化已验证可行 [来源: arXiv:2608.09789]。
3. **企业私有故障知识图谱 + RAG**：历史问题单/FA 报告/ECN 结构化 → 成为疑难定位与二供排查的核心资产（当前最大数据红利）。
4. **校准与可信工程**：LoRD 类校准、置信度路由（低置信自动转人工）、可审计推理链——解决「AI 说错了谁负责」的信任问题 [来源: arXiv:2608.17965]。
5. **数据飞轮**：研发问题库（问题单→根因→修复→ECN）闭环回流，持续微调企业诊断模型；AnomalyGen 证明代码/设计资产可合成训练数据 [来源: arXiv:2604.11107]。
6. **数字孪生辅助**：仿真（SI/热/电）与实测融合定位，AI 搜索参数空间缩小疑难问题假设集。

### 8.2 方向确定性排序

| 方向 | 确定性 | 依据 |
|:-----|:------:|:-----|
| 知识图谱+RAG 沉淀 | 高 | 数据资产已存在，只差结构化 |
| 边缘轻量推理下沉 | 高 | FAME/LogICL 蒸馏路线已验证 |
| 多模态融合 | 中高 | MLLM 工业检测已验证，硬件数据融合待产品化 |
| Agent 自主执行 | 中 | 信任/安全边界未解（见 Agentic AIOps 批判） |
| 数字孪生辅助 | 中 | 依赖仿真精度与算力成本 |

---

## 九、对研发团队的落地建议

1. **先做共性识别（3 个月内见效）**：现有测试/RMA 日志上 LLM 解析 + 聚类，目标：共模问题自动归因率 ≥ 70%，替代每周人工 review。
2. **同步建二供知识库（6-12 个月）**：把存量 FA 报告、替代料验证记录、兼容矩阵结构化 → 这是二供排查 AI 化的唯一前提。
3. **疑难 RCA 走「案例检索 + LLM 辅助推理」而非全自动**：先让工程师从「翻日志」变为「问系统」，积累信任后再逐步自动化。
4. **度量先行**：建立 MTTR、复现率、共模检出率、知识复用率的基线，AI 效果才有说服力（对齐用户「量化驱动」标准）。
5. **警惕**：AI 定位结论必须可审计（保留推理链 + 证据引用），二供/疑难定位的错误结论代价远高于共性识别。

---

## 十、诚实标注与局限

- **一手来源**：arXiv 论文摘要（2025-2026，编号可溯源）、NVIDIA DCGM 官方页、阿里云 SLS 官网、华为 eSight 官网、既有知识库深度分析。
- **工程经验推断**（未获独立源验证，标注 *）：共性归类人工降低 60-80%、替代评估周期缩短 30-50%、MTTR 运维侧量化——均为行业口径/推断，不可作为决策唯一依据。
- **搜索限制**：web_search（Zhipu key 失效）、Bing 中文专业长尾词质量差、jina 不可达——二供方向的中文一手案例（浪潮/联想/曙光具体实践）未能获取，属明确缺口，后续可用爱集微/STH/官方渠道补。
- **RCAgent 编号**：文中 RCAgent 以「arXiv:2402.09355 类」模糊标注（当日 arXiv 搜索被限流未逐一验证编号），建议引用前复核。
- **效果数据口径**：论文指标（F1/误报率）均为公共基准测试集结果，实盘效果受数据分布影响会显著低于基准，引用时已注明条件。

---

## 参考文件

### 内部知识库引用

- [AI 在服务器研发行业编程活动中的应用进展](2026-08-20-ai-coding-in-server-rd-deep-analysis.md) — 同族：编程活动 AI 应用
- [AI 在基础设施运维管理中的应用进展全景](2026-08-20-ai-infra-ops-application-progress-deep-analysis.md) — 同族：运维侧 AIOps 进展
- [AI 服务器研发故障工程深度辨析](2026-08-20-doubao-ai-server-rd-fault-engineering-deep-review.md) — 同族：故障工程辨析
- [知识库软件研发进展全景分析](2026-08-20-knowledge-base-software-progress-deep-analysis.md) — 同族：知识库软件进展
- [Agentic AIOps 2026 叙事](2026-08-07-agentic-aiops-2026-narrative-deep-analysis.md) — 主线互补：L1→L3 与六组件
- [容错四论文](../../10_supernode-rack/2026-08-07-fault-tolerance-four-papers-deep-analysis.md) — 万卡集群故障/容错机制
- [GPU/LLM 可靠性 SDC](../../10_supernode-rack/2026-07-29-gpu-llm-reliability-sdc-deep-analysis.md) — 静默数据损坏
- [服务器研发后全链路（替代料/兼容矩阵）](../../02_rd/00_shared/03_process/2026-06-04-doubao-post-rd-work-checklist.md) — 二供背景

### 外部资料引用

- 来源: Ma Z, Yang J, Chen T-H., "LLM4Log: A Systematic Review of LLM-based Log Analysis", arXiv:2604.16359, 2026
- 来源: Wang H, et al., "FAME: Failure-Aware Mixture-of-Experts for Message-Level Log Anomaly Detection", ISSRE 2026, arXiv:2605.22779
- 来源: Shetaia A, Kauffman S., "DeepParse: Hybrid Log Parsing with LLM-Synthesized Regex Masks", arXiv:2604.20553, 2026
- 来源: Li B, Wang D, Lu S., "Too Sure to Be Safe: Model Calibration for Reliable Log Anomaly Detection", ICDM 2026, arXiv:2608.17965
- 来源: Patel D., "LLM-Enhanced Log Anomaly Detection: A Comprehensive Benchmark", arXiv:2604.12218, 2026
- 来源: Li X, et al., "AnomalyGen: Enhancing Log-Based Anomaly Detection with Code-Guided Data Augmentation", arXiv:2604.11107, 2026
- 来源: Peng A, et al., "EnrichLog: Log Anomaly Detection with LLMs via Knowledge-Enriched Fusion", arXiv:2512.11997, 2025
- 来源: Ye J, et al., "LogICL: Distilling LLM Reasoning to Bridge the Semantic Gap in Cross-Domain Log Anomaly Detection", arXiv:2512.09627, 2025
- 来源: Zhang S, et al., "LogPurge: Log Data Purification for Anomaly Detection via Rule-Enhanced Filtering", arXiv:2511.14062, 2025
- 来源: Wu Z, et al., "ICAD-LLM: One-for-All Anomaly Detection via In-Context Learning", arXiv:2512.01672, 2025
- 来源: Sun J, et al., "VarParser: Unleashing the Neglected Power of Variables for LLM-based Log Parsing", WWW 2026, arXiv:2601.22676
- 来源: Tan J, et al., "HYVE: Hybrid Views for LLM Context Engineering over Machine Data", arXiv:2604.05400, 2026
- 来源: He J, et al., "ADOPD: Reference-Privileged On-Policy Distillation for MLLM-Based Industrial Anomaly Detection", arXiv:2608.09789, 2026
- 来源: Gao Y, et al., "ORCA: Observability-Grounded Program Repair for Microservice Incidents", ASE 2026, arXiv:2608.17018
- 来源: NVIDIA, NVIDIA DCGM (Data Center GPU Manager) 官方文档 — developer.nvidia.com/dcgm
- 来源: 阿里云, 日志服务 SLS 产品页 — aliyun.com/product/sls
- 来源: 华为, eSight ICT 统一管理系统产品页 — e.huawei.com
- 来源: 原始素材 tmp/raw/2026-08-20/arxiv-log-analysis-llm-2026.md

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-20 | v1.0 | 首次创建：三类问题定位活动 × AI 应用进展全景（arXiv 一手论文 + 厂商平台 + 既有知识库交叉） |
| 2026-08-22 | v1.1 | 提升：补齐 std-002 五元素 + 跨文件交叉链接与一致性勘误 |
