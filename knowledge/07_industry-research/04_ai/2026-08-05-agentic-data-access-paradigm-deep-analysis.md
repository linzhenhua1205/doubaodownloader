# Agentic 数据访问范式：Token-Native Storage × Oasis × TEngineDB-V × CITBench 深度分析

> **基于**: 四篇 arXiv 一手论文（abstract 全量核实，2026-08-05 抓取）
> **分析日期**: 2026-08-05
> **总览**: 数据访问接口正在从"为人设计"（UTF-8/SQL/top-k/单轮指令）系统性迁移到"为模型设计"（token 语义/datapath 直通/large-k 分析检索/多轮交互）。四篇论文分别攻击数据访问成本链的**存储格式层、数据通路层、查询引擎层、评测层**，合流为 Agentic 数据访问范式的完整图景。
> **前置素材**: 08-04/08-05 日报四篇论文简略记录（本专题为其深度升级）

---

## 目录

- [1. 范式转移：数据访问接口从"人读"到"Agent 读"](#1-范式转移数据访问接口从人读到agent-读)
  - [1.1 传统数据栈的隐含假设](#11-传统数据栈的隐含假设)
  - [1.2 Agent 数据栈的四个新假设](#12-agent-数据栈的四个新假设)
  - [1.3 四篇论文在栈中的位置（全景图）](#13-四篇论文在栈中的位置全景图)
- [2. Token-Native Storage：存储格式层的"模型语言化"](#2-token-native-storage存储格式层的模型语言化)
  - [2.1 核心主张与量化数据](#21-核心主张与量化数据)
  - [2.2 技术机制：merge order vs frequency](#22-技术机制merge-order-vs-frequency)
  - [2.3 收益分解：压缩与读取加速](#23-收益分解压缩与读取加速)
  - [2.4 障碍：tokenizer 标准化（类比 ASCII/UTF-8）](#24-障碍tokenizer-标准化类比-asciiutf-8)
  - [2.5 与 TokTier/字节 KV 卸载的呼应](#25-与-toktier字节-kv-卸载的呼应)
- [3. Oasis：数据通路层的"解码入网"](#3-oasis数据通路层的解码入网)
  - [3.1 问题：scan 占查询一半 + Parquet 解码 CPU 瓶颈](#31-问题scan-占查询一半-parquet-解码-cpu-瓶颈)
  - [3.2 方案：SmartNIC 硬件解码器 + DuckDB 集成](#32-方案smartnic-硬件解码器-duckdb-集成)
  - [3.3 收益与边界条件](#33-收益与边界条件)
  - [3.4 与 computational storage / DPU 路线的关系](#34-与-computational-storage-dpu-路线的关系)
- [4. TEngineDB-V：查询引擎层的"向量一等公民"](#4-tenginedb-v查询引擎层的向量一等公民)
  - [4.1 large-k 工作负载：被忽视的 Agent 检索形态](#41-large-k-工作负载被忽视的-agent-检索形态)
  - [4.2 两类现有系统的失败模式](#42-两类现有系统的失败模式)
  - [4.3 方案：索引物化 + IVFPQ 关系化 + DPPQ](#43-方案索引物化-ivfpq-关系化-dppq)
  - [4.4 量化收益与生产验证](#44-量化收益与生产验证)
  - [4.5 行业含义：向量数据库的终局](#45-行业含义向量数据库的终局)
- [5. CITBench：评测层的"多轮交互度量"](#5-citbench评测层的多轮交互度量)
  - [5.1 现有基准的缺口：单轮完全指定](#51-现有基准的缺口单轮完全指定)
  - [5.2 CITBench 设计：4 类 18 任务 1296 实例](#52-citbench-设计4-类-18-任务-1296-实例)
  - [5.3 关键发现：复杂度驱动的性能退化](#53-关键发现复杂度驱动的性能退化)
  - [5.4 与 state-verification 评估范式的呼应](#54-与-state-verification-评估范式的呼应)
- [6. 四者合流：Agentic 数据访问范式的完整图景](#6-四者合流agentic-数据访问范式的完整图景)
  - [6.1 成本链攻击点对照表](#61-成本链攻击点对照表)
  - [6.2 共性洞察：消除翻译层](#62-共性洞察消除翻译层)
  - [6.3 与 GitLake/Bauplan 的栈级拼接](#63-与-gitlakebauplan-的栈级拼接)
  - [6.4 与知识库既有信号的交叉验证](#64-与知识库既有信号的交叉验证)
- [7. 对服务器/AI 基础设施的行业判断](#7-对服务器ai-基础设施的行业判断)
  - [7.1 四层技术成熟度评估](#71-四层技术成熟度评估)
  - [7.2 对存储/网络/计算三方的启示](#72-对存储网络计算三方的启示)
  - [7.3 可证伪预测 P1-P5](#73-可证伪预测-p1-p5)
  - [7.4 行动项与观察点](#74-行动项与观察点)
- [参考文献](#参考文献)
- [Changelog](#changelog)

---

## 1. 范式转移：数据访问接口从"人读"到"Agent 读"

### 1.1 传统数据栈的隐含假设

过去四十年的数据系统（数据库、数仓、数据湖、Lakehouse）为**人类操作员**设计，隐含四层假设：

| 层 | 传统假设 | 具体表现 |
|:---|:---------|:---------|
| 存储格式 | 文本以 UTF-8 存储 | "格式为人类可读"（[1] 原文：UTF-8 is a format built for humans） |
| 查询路径 | CPU 有富余，解码成本可忽略 | 存储/网络带宽曾远慢于 CPU，解码不是瓶颈 |
| 查询语义 | 返回少量精确结果 | top-k 检索、WHERE 过滤、聚合——减少返回量=减少人读负担 |
| 交互模式 | 单轮、完全指定的指令 | SQL 一条语句即完整表达查询意图 |

这些假设在"人读"时代是合理的：人的阅读带宽（约几十 token/秒）远低于任何 IO 环节，因此**优化目标是减少输出量**。

### 1.2 Agent 数据栈的四个新假设

Agent（embedder、reranker、LLM agent）成为存储文本的主要读写者后，四个假设逐一翻转：

| 层 | 新假设 | 翻转逻辑 |
|:---|:-------|:---------|
| 存储格式 | 以模型的 token ID 存储 | 读写方是模型，每次访问都付出"文本↔token"翻译成本 |
| 查询路径 | CPU 解码成为瓶颈 | 存储/网络带宽增速持续超过 CPU 性价比（[2] 原文） |
| 查询语义 | 返回海量候选做分析 | large-k 检索（k=10³-10⁵）用于聚合/过滤/join（[3] 原文） |
| 交互模式 | 多轮、需求演化 | 用户逐步细化需求，Agent 需在受限操作流程中多轮交互（[4] 原文） |

**第一性原理**：Agent 读数据的成本链是——

```text
ObjectStore -> Network -> CPU Decode -> QueryEngine -> Serialize -> tokenize -> LLM Infer
 (Parquet)   (datapath)  (compressed)  (index/op)     (row/col)   (text->ID)  (read tokens)
```

传统栈的优化目标（减少输出）失效了：Agent 的输入带宽是人的数百倍，**瓶颈转移到"翻译与往返"**——格式翻译（解码）、语义翻译（tokenize）、引擎翻译（两套查询系统）、交互翻译（单轮↔多轮）。

### 1.3 四篇论文在栈中的位置（全景图）

```text
+---------------------------------------------------------------+
|  App layer: Interactive Tabular Processing (CITBench)         |
+---------------------------------------------------------------+
|  Query Engine: OLAP-native Vector Search (TEngineDB-V)        |
+---------------------------------------------------------------+
|  Datapath: In-network Parquet Decode (Oasis)                  |
+---------------------------------------------------------------+
|  Storage Format: Token-native (BPE token IDs)                 |
+---------------------------------------------------------------+
         ^                        ^                        ^
   removes text<->token     removes format<->mem     removes vec<->rel
   translation (format+     decode translation       engine translation
   tokenize layer)          (datapath, in-network)   (index materialized)
```

四篇论文不是孤立的单点创新，而是**同一范式转移在不同栈层的投影**。

---

## 2. Token-Native Storage：存储格式层的"模型语言化"

> **论文**: [1] Kumar Shivendu, arXiv:2608.02376 (cs.DB, 2026-08-03)。11 页 5 图 2 表。

### 2.1 核心主张与量化数据

**主张**：搜索引擎和数据库仍以 UTF-8 存储文本（为人类设计的格式），但读写这些文本的系统（embedders、rerankers、LLM agents）用 token ID 工作——每次访问都在为翻译付费。应当**以模型的 BPE token ID 作为存储格式**，这同时更小、更快。

核心量化数据（全部来自原文）：

| 指标 | 数值 | 条件 |
|:-----|:-----|:-----|
| 无压缩压缩比 | **2.25×** | r50k ID 打包为 uint16，英文语料 |
| 熵编码压缩比 | **3.30×** | 同上 |
| 编解码器覆盖 | 6 种 tokenizer × 3 语料（英/代码/印地语） | 匹配或超越**全部**字节编解码器（含语料训练的 zstd 词典） |
| 读取加速 | **10-600×** | 模型直接读 token ID，免每次重新 tokenize |

### 2.2 技术机制：merge order vs frequency

论文最锋利的技术发现是 BPE 词表编号的"错位"：

- **现状**：BPE 按 **merge order**（合并顺序）编号 token——这是训练过程的产物，与使用频率无关
- **问题**：低频 token 占据小 ID，高频 token 占据大 ID，导致 ID 分布与真实文本分布错位，压缩率受损
- **修复（一行代码）**：按**频率重排**词表后，用普通整数编解码器 **streamvbyte** 即可恢复熵编码的大部分压缩比，且解码快 **~7×**

论文公开呼吁：**AI labs 发布词表时应按频率重排**——这是一行代码的改动，却能让下游存储与传输全链路受益。

### 2.3 收益分解：压缩与读取加速

```text
Legacy agent read path:
  UTF-8 bytes -> (net/disk xfer 2.25-3.30x redundant) -> CPU decode -> tokenize (every read) -> token IDs -> LLM

Token-native read path:
  token IDs (compressed 2.25-3.30x) -> (less xfer) -> decode (streamvbyte, ~7x faster) -> token IDs -> LLM (direct)
```

两个独立收益：

1. **存储/传输收益**：token ID 打包即压缩（2.25×），熵编码更高（3.30×）——存储介质与网络带宽直接省 2-3×
2. **计算收益**：免去每次读取的 tokenize（10-600× 读取加速）——这是更本质的收益，因为 tokenize 在 Agent 高频重读场景（RAG 语料、对话历史）会反复发生

### 2.4 障碍：tokenizer 标准化（类比 ASCII/UTF-8）

论文自认的"唯一障碍"：**共享 token ID 需要共享 tokenizer**，而不同模型家族的 tokenizer 并不互通。

```text
ASCII/UTF-8 standardization -> shared char encoding for humans -> portable text
Tokenizer standardization    -> shared token vocab for models  -> portable tokens (paper's call)
```

这正是其激进之处：它把"标准化"从字符层提升到 **token 语义层**。类比历史：ASCII 花了数十年成为事实标准；token 标准化若发生，将重塑存储与传输的底层格式。

### 2.5 与 TokTier/字节 KV 卸载的呼应

本系统 08-04 归档的 TokTier（tokenizer 占 TTFT 64%）与本论文构成**两日连续信号**：

| 信号 | 攻击点 | 结论 |
|:-----|:-------|:-----|
| TokTier（08-04） | 推理侧 tokenize 延迟（TTFT 64%） | tokenize 是推理服务的第一延迟源 |
| Token-Native Storage（08-03） | 存储侧 tokenize 重复成本 | tokenize 也是数据访问的第一重复成本 |
| 字节 KV 卸载（MEMORY 沉淀） | 存储参与 token 生命周期（KV cache） | 存储层已开始"理解"token |

合流判断：**token 级基础设施正成为推理与数据访问的共同优化面**——不是某一层的小优化，而是横跨存储/网络/推理的范式级变化。

---

## 3. Oasis：数据通路层的"解码入网"

> **论文**: [2] Jonas Dann, Luca Tagliavini, Gustavo Alonso（ETH Zurich）, arXiv:2608.02268 (cs.DB + cs.AR, 2026-08-03)。

### 3.1 问题：scan 占查询一半 + Parquet 解码 CPU 瓶颈

**背景数据**（原文引用的生产数仓研究）：

- **scans（含往返存储）约占查询总运行时间的一半**
- 数据湖/lakehouse 通过**每次查询解码**存储优化的压缩格式（如 Parquet）放大此瓶颈
- 关键趋势反转：**存储与网络带宽持续超过 CPU 成本-性能比**——CPU 花在解码上的周期日益侵蚀云的成本效率承诺

```text
Legacy lakehouse query path:
  S3(Parquet) -> network -> CPU (decode: decompress + column decode + assemble) -> query exec
                             ^
                    bottleneck: CPU decode cycles, ~half of query runtime

Oasis query path:
  S3(Parquet) -> network (SmartNIC hardware decode in datapath) -> query exec
                             ^
               decode overlaps with transfer, hidden in network datapath
```

### 3.2 方案：SmartNIC 硬件解码器 + DuckDB 集成

Oasis 是一个**数据处理的 SmartNIC**，把 Parquet 解码卸载到网络数据通路作为自定义硬件加速器。三组件：

1. **硬件解码器架构**：在网卡 datapath 内实现 Parquet 解码（解压缩、列解码等）
2. **软件抽象层**：向查询引擎暴露统一解码接口，屏蔽硬件细节
3. **端到端集成**：与 DuckDB 完整集成（DuckDB 为轻量嵌入式 OLAP 引擎，代表 lakehouse 查询的典型形态）

### 3.3 收益与边界条件

| 指标 | 数值 | 条件 |
|:-----|:-----|:-----|
| 查询吞吐 | **近翻倍（almost doubles）** | 最佳情况（扫描密集、解码占比高） |
| 机制 | 解码与查询执行其余部分重叠 | 扫描成本被"藏"在网络 datapath 后 |
| 开销 | 最小化（minimal overhead） | 硬件解码器在 datapath 内，不占主机 CPU |

**边界条件**（第一性原理推演）：收益上限取决于①扫描在负载中的占比（~50% 是上限空间）；②解码 vs 传输的相对成本（带宽越便宜、CPU 越贵，收益越大）。当查询以点查/索引查找为主（解码占比低）时，收益趋近于零——Oasis 是**扫描密集型**负载的解药。

### 3.4 与 computational storage / DPU 路线的关系

Oasis 属于"**计算下沉到 IO 路径**"的谱系，但位置独特：

| 路线 | 计算位置 | 代表 | 本系统已有沉淀 |
|:-----|:---------|:-----|:---------------|
| Computational Storage | SSD 内 | NGD Systems 等 | GDS/SPDK 专题（[07-29](../../02_rd/01_product/00_hardware/06_storage/2026-07-29-gds-gpu-direct-storage-deep-analysis.md)） |
| **In-network Processing（Oasis）** | **网卡 datapath** | Oasis（ETH） | 本文 |
| DPU 通用卸载 | 网卡 SoC（通用核） | BlueField/DOCA | Supernode CXL/DOCA 专题 |

区别：DPU 用通用核做**通用**网络功能，Oasis 用**专用硬件**做**特定数据格式**的解码。后者牺牲通用性换取解码效率，且直接面向"存储格式"这一确定目标——只要 Parquet 是 lakehouse 事实格式，专用解码器就有确定回报。**Oasis 是"计算存储"的网内变体（in-network computational storage）**。

---

## 4. TEngineDB-V：查询引擎层的"向量一等公民"

> **论文**: [3] Xufei Wu 等 14 人（腾讯 + 清华李国良/周煊赫组）, arXiv:2608.00650 (cs.DB, 2026-08-01)。

### 4.1 large-k 工作负载：被忽视的 Agent 检索形态

**large-k 分析向量检索**：k=10³-10⁵ 的结果检索，用于**分析**（聚合、过滤、join）而非展示 top-10。

新兴来源（原文点名的两个）：

- **LLM 数据管理**：Agent/RAG 需要检索大量候选做下游分析，而非只要少数"最像"的
- **腾讯广告分析**：生产广告分析负载的向量化检索

这颠覆了向量检索的传统定义：传统向量 DB 面向"相似度排序 top-k 展示"（k≤10），large-k 面向"检索集合作分析输入"（k=10³-10⁵）——**检索从"最终输出"变成"中间产物"**。

### 4.2 两类现有系统的失败模式

| 系统类型 | 失败模式 |
|:---------|:---------|
| 专用向量数据库 | 为满足尾延迟把 k 设上限（如 k≤10⁴）；分析支持有限（不能 join/聚合） |
| OLAP 系统 | 每 segment 嵌入向量索引为黑盒 → 严重的读/计算放大（scatter-gather）；无法原生查询优化 |

本质矛盾：**向量检索与分析查询是两套执行模型**（相似度扫描 vs 关系算子），强行拼接导致放大。

### 4.3 方案：索引物化 + IVFPQ 关系化 + DPPQ

TEngineDB-V 让向量检索成为腾讯 OLAP 引擎的**一等公民分析原语**：

1. **全局段解耦索引物化为关系表**：索引不再作为黑盒嵌入 segment，而是物化为关系表 → 消除 scatter-gather 执行、减少放大、支持原生存储优化
2. **IVFPQ 分解为关系算子**：把 IVFPQ（倒排+乘积量化）检索分解为关系算子序列，融入 OLAP 优化器
3. **DPPQ（Direction-aware Product Quantization）**：方向感知量化 + 分层残差细化——提高召回率同时保持关系执行效率
4. **索引感知查询重写 + 分布式感知成本模型**：优化器理解索引语义，跨节点执行有成本模型引导

### 4.4 量化收益与生产验证

| 指标 | 数值 | 对比基线 |
|:-----|:-----|:---------|
| 加速比 | 最高 **145×** | StarRocks 等竞品 |
| 生产部署提升 | **52×** | 腾讯百亿（10-billion）规模生产部署 |

两个数字的解读：145× 是实验室对比（竞品在 large-k 上严重退化），52× 是生产规模验证（百亿级向量）。**large-k 场景下传统系统的退化越严重，新范式的相对收益越大**——这解释了 145× 的量级。

### 4.5 行业含义：向量数据库的终局

TEngineDB-V 的架构选择（向量检索成为 OLAP 原生原语）指向一个行业判断：

```text
Vector DB evolution (3 stages):
  standalone vector DB (Milvus/Pinecone...)  -- search-only, k-limited, weak analytics
  -> lakehouse embedded index (Iceberg Puffin) -- storage-level, engine still black-box
  -> OLAP-native vector (TEngineDB-V)          -- search = relational op, analytics native
                                                       ^ endgame
```

这与本系统 06-05 归档的 "Apache Iceberg Puffin-backed 向量索引" 形成演进序列：先有存储层内嵌，后有**引擎层原生**。**独立向量数据库大概率是过渡态，融合进 OLAP/Lakehouse 是终局**。

---

## 5. CITBench：评测层的"多轮交互度量"

> **论文**: [4] Zihan Nan, Yang Gu, Wei Liu 等 7 人, arXiv:2608.00018 (cs.DB, 2026-06-29)。

### 5.1 现有基准的缺口：单轮完全指定

表格数据处理是数据工作的核心，LLM 助手已展现能力，但现有基准：

- 聚焦**单轮、完全指定指令**下的表格推理
- 低估了**多轮交互、需求演化**的复杂表格处理

真实场景（user-in-the-loop）是：用户逐步细化需求 → Agent 在受限操作流程中多轮执行 → 中间结果反馈 → 需求再演化。评测缺口 = 能力度量缺口。

### 5.2 CITBench 设计：4 类 18 任务 1296 实例

```text
CITBench taxonomy
|-- table matching
|-- table cleaning
|-- table augmentation
`-- table transformation
        `-- 18 task types x cross-domain datasets -> 1296 instances
```

**双模式评测**：

- **离线**：静态任务评估（同传统基准）
- **在线**：模拟多轮交互——受限操作流程 + 结构化任务脚本，捕获 user-in-the-loop 的行为特征

在线模式是 CITBench 的核心增量：它把评测从"一次问答"升级为"一段工作流"。

### 5.3 关键发现：复杂度驱动的性能退化

评测结论（一致趋势，跨开源/闭源模型）：

| 因素 | 影响 |
|:-----|:-----|
| 表格复杂度 ↑ | 性能显著下降 |
| 规则依赖更紧 | 性能显著下降 |
| 噪声多轮交互模拟 | 性能显著下降 |
| 简单表格与规则 | 表现良好（基准面） |

**解读**：模型在"理解、规划、表结构感知"三个能力维度上，在扩展交互式场景中仍有持续挑战——**单轮强 ≠ 多轮强**。这与 08-05 日报的 SWE-Touch（共享工作区状态感知 -7.7pp）是同一现象：**强自主性能 ≠ 交互场景的状态与流程感知**。

### 5.4 与 state-verification 评估范式的呼应

本系统 08-03 归档了 "state-verification 评估范式"（验证 Agent 是否真实改变了系统状态，而非仅输出文本）。CITBench 与其同属 **agentic data 评测方向**：

| 评测范式 | 度量对象 | 共同点 |
|:---------|:---------|:-------|
| state-verification（08-03） | Agent 对系统状态的真实改变 | 从"输出"转向"效果" |
| CITBench 在线模式（08-04） | Agent 多轮表格处理能力 | 从"单轮"转向"工作流" |

合流判断：**Agent 数据能力评测正在从"答案正确性"转向"过程有效性"**——因为 Agent 的生产力取决于多轮工作流中的持续正确，而非单次问答。

---

## 6. 四者合流：Agentic 数据访问范式的完整图景

### 6.1 成本链攻击点对照表

| 论文 | 栈层 | 攻击的成本环节 | 消除的翻译 | 关键量化 |
|:-----|:-----|:---------------|:-----------|:---------|
| Token-Native Storage | 存储格式 | 存储/传输冗余 + 重复 tokenize | 文本↔token | 2.25-3.30× 压缩；10-600× 读取 |
| Oasis | 数据通路 | CPU 解码周期（scan 占查询一半） | 格式↔内存 | DuckDB 吞吐近翻倍 |
| TEngineDB-V | 查询引擎 | 双引擎拼接放大（scatter-gather） | 向量↔关系 | 145× vs StarRocks；52× 生产 |
| CITBench | 评测 | 单轮↔多轮的能力度量鸿沟 | 指令↔工作流 | 4 类 18 任务 1296 实例 |

### 6.2 共性洞察：消除翻译层

四篇论文共享同一个第一性原理：**Agent 数据访问的成本不在数据本身，而在数据与模型之间的翻译层**。翻译层有四种：

1. 格式翻译（UTF-8↔token）→ Token-Native Storage
2. 解码翻译（压缩格式↔内存格式）→ Oasis
3. 引擎翻译（向量检索↔关系查询）→ TEngineDB-V
4. 交互翻译（单轮指令↔多轮工作流）→ CITBench（评测暴露之）

**判断**：未来三到五年数据系统的竞争主线，将从"查询性能"（人读时代的度量）转向"翻译成本"（模型读时代的度量）。

### 6.3 与 GitLake/Bauplan 的栈级拼接

本系统 07-27 归档的 GitLake/Bauplan（Agent-first Lakehouse）覆盖**编程模型/事务层**，与本专题四篇（**数据访问路径层**）拼接为 Agentic Data 完整栈：

```text
+----------------------------------------------+
|  Programming model: GitLake/Bauplan (07-27)  |
|  txn/branch/contract -- safe concurrent write|
+----------------------------------------------+
|  Evaluation: CITBench (this doc) -- multi-    |
|  turn interaction capability measurement      |
+----------------------------------------------+
|  Query engine: TEngineDB-V (this doc) --      |
|  vector-native analytics                      |
+----------------------------------------------+
|  Datapath: Oasis (this doc) -- decode-in-net  |
+----------------------------------------------+
|  Storage format: Token-Native (this doc) --   |
|  store in model's language                    |
+----------------------------------------------+
```

写作/写安全（GitLake）与读效率（本文四篇）合流，才是 Agent 时代数据系统的完整命题：**写要防 Agent 不可信（事务化），读要按 Agent 语义（token 原生）**。

### 6.4 与知识库既有信号的交叉验证

| 知识库信号 | 与本文的印证 |
|:-----------|:-------------|
| TokTier：tokenizer 占 TTFT 64%（08-04） | Token-Native 免 tokenize（10-600×）直击同一成本 |
| 字节 KV 卸载 batch+30%（MEMORY） | 存储参与 token 生命周期已成先例 |
| Agentic Lakehouse 2026 强范式（MEMORY） | 本文四篇 = Agentic Lakehouse 的读路径具体化 |
| Iceberg Puffin 向量索引（06-05） | TEngineDB-V 是"引擎层原生"的深化（Puffin 是存储层） |
| state-verification 评估范式（08-03） | CITBench 在线模式同向（输出→效果） |
| SWE-Touch：共享工作区感知 -7.7pp（08-05） | CITBench：多轮交互退化——同一现象两域验证 |

---

## 7. 对服务器/AI 基础设施的行业判断

### 7.1 四层技术成熟度评估

| 栈层 | 方案 | 成熟度 | 落地障碍 |
|:-----|:-----|:------:|:---------|
| 存储格式 | Token-Native Storage | 🟡 论文/原型 | tokenizer 标准化（最大障碍） |
| 数据通路 | Oasis | 🟡 学术原型 | 专用硬件成本；格式绑定 Parquet |
| 查询引擎 | TEngineDB-V | 🟢 生产验证 | 需 OLAP 引擎深度改造；腾讯内部件 |
| 评测 | CITBench | 🟢 基准发布 | 在线模式成本高，需标准化采纳 |

判断：**TEngineDB-V 最接近落地（生产 52× 已证），Token-Native 最具颠覆性但障碍最大，Oasis 最依赖硬件节奏**。

### 7.2 对存储/网络/计算三方的启示

**存储（对 SSO/存储产品线）**：

- token 语义化存储若成势，SSD 接口可能增加"token 感知"语义（类比 zoned namespace 的演进路径）
- large-k 检索改变 IO 模式：从"随机少量"转向"扫描海量" → 顺序带宽需求上升，与超节点存储网络设计（[07-01 存储带宽专题](../../02_rd/02_project/01_superpod/network/2026-07-01-08-klx-storage-bandwidth.md)）直接相关
- Token-Native 压缩 2.25× 若规模化，等效于存储容量和带宽的免费升级——值得跟踪词表标准化进展

**网络（对互联/网卡产品线）**：

- Oasis 路线（in-network 解码）3-5 年内有望被 DPU 厂商吸收（BlueField/DOCA 的扩展方向之一）
- 网卡从"传输管道"向"数据功能单元"演进——解码/过滤/投影下沉，服务器 CPU 配比可下调
- 观察点：SmartNIC 的专用硬件 vs DPU 通用核之争（专用=效率，通用=灵活）

**计算（对整机/平台）**：

- DuckDB 类轻引擎 + 硬件加速（Oasis 模式）代表"查询引擎小型化 + 加速外置"的新形态
- 向量检索成为 OLAP 原生原语 → 分析服务器的向量指令集/加速器需求上升
- CPU 解码职责外移 → 同规格 CPU 可承载更多查询并发（成本效率↑）

### 7.3 可证伪预测 P1-P5

| # | 预测 | 证伪条件 | 时间窗 |
|:-:|:-----|:---------|:-------|
| P1 | Token-Native 最先落地 **RAG 语料/embedding 管线**（同构 tokenizer 场景，无需跨模型标准化） | 2028H2 前无任何 token-native 检索系统生产部署 | 2026-2028 |
| P2 | in-network 解码（Oasis 路线）被 DPU 厂商**产品化** | 2029 年前无主流网卡厂商提供格式解码加速 | 2026-2030 |
| P3 | **独立向量 DB 份额见顶**，OLAP 原生向量（TEngineDB-V 模式）成主流 | 2029 年前独立向量 DB 仍是 large-k 分析主力 | 2026-2029 |
| P4 | **large-k（10³+）成为 Agent 检索默认配置**，检索系统从"top-k 近似"转向"全候选分析" | 2028 年前主流 RAG 框架仍以 top-k≤100 为默认 | 2026-2028 |
| P5 | **tokenizer 标准化失败**导致 token 语义层碎片化（多家族各自为政） | 2028 年前出现跨家族共享 tokenizer 事实标准 | 2026-2028 |

**P5 是关键风险**：Token-Native 的整个价值建立在共享词表上。若标准化失败，范式退化为"每模型家族一个私有格式"——价值仍在（同族内省 tokenize），但跨模型迁移收益消失。

### 7.4 行动项与观察点

**近期（3 个月）**：

- [ ] 跟踪 tokenizer 标准化动向（AI labs 是否采纳"按频率重排词表"的一行改动呼吁——这是 Token-Native 的投石问路信号）
- [ ] 评估 large-k 检索对存储带宽模型的冲击：超节点/集群存储设计中预留"扫描型"负载带宽
- [ ] 用 CITBench 方法审视本系统 Agent 的表格处理能力（多轮交互场景是短板所在）

**中期（6-12 个月）**：

- [ ] 监测腾讯 TEngineDB-V 是否开源/对外（百亿级验证含金量高）
- [ ] 跟踪 Oasis 后续工作（是否扩展格式支持、与厂商合作）
- [ ] 关注向量 DB 厂商的 OLAP 融合动作（收购/自研/合作），验证 P3

---

## 参考文献

1. Kumar Shivendu. *Token-Native Storage: Read and Write in your Agent's Language*. arXiv:2608.02376 [cs.DB], 2026-08-03. <https://arxiv.org/abs/2608.02376>
2. Jonas Dann, Luca Tagliavini, Gustavo Alonso. *Oasis: Hiding the Cost of Querying Parquet Files in the Datapath*. arXiv:2608.02268 [cs.DB, cs.AR], 2026-08-03. <https://arxiv.org/abs/2608.02268>
3. Xufei Wu et al. *TEngineDB-V: An OLAP-Native Vector Search System for Large-k Workloads at Tencent*. arXiv:2608.00650 [cs.DB], 2026-08-01. <https://arxiv.org/abs/2608.00650>
4. Zihan Nan, Yang Gu, Wei Liu et al. *CITBench: A Comprehensive Benchmark for Interactive Tabular Data Processing with LLMs*. arXiv:2608.00018 [cs.DB], 2026-06-29. <https://arxiv.org/abs/2608.00018>

## Changelog

- **2026-08-05** | 创建。四篇 arXiv 一手论文深度分析（abstract 全量核实）；框架=Agent 读数据成本链四层攻击（格式/通路/引擎/评测）；与 GitLake/Bauplan 拼接为 Agentic Data 完整栈；预测 P1-P5。
