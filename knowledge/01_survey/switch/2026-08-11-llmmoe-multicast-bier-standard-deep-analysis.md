# 🔀 LLM MoE 组播用例首现 IETF rtgwg：AI 训练网络组播需求正式标准化

> **类型**: 深度专题 | **日期**: 2026-08-11 | **定位**: draft-zhang-rtgwg-llmmoe-multicast-03 技术原理深挖——MoE token 分发的组播本质、四类组播技术对比、BIER 无状态复制机制逐层拆解；衔接 [`2026-08-11-ietf-ai-network-standards-deep-analysis.md`](2026-08-11-ietf-ai-network-standards-deep-analysis.md)（三线总览）、[`2026-08-11.md`](2026-08-11.md)（追踪速记）
> **数据源**: IETF Datatracker 全文抓取（-03 全文 16.7KB）+ RFC 8279/8296/7761 一手 + 第一性原理推导
> **关联文件**: [`2026-08-11-ietf-ai-network-standards-deep-analysis.md`](2026-08-11-ietf-ai-network-standards-deep-analysis.md)、[`2026-08-11.md`](2026-08-11.md)、[`2026-08-11-mpls-pbt-m-on-path-telemetry-deep-analysis.md`](2026-08-11-mpls-pbt-m-on-path-telemetry-deep-analysis.md)

---

## 📑 目录

- [0. 一句话结论](#0-一句话结论)
- [1. 事实基线（一手全文验证）](#1-事实基线一手全文验证)
- [2. 技术原理：MoE 为什么天然是组播问题](#2-技术原理moe-为什么天然是组播问题)
- [3. 技术原理：四类组播技术对比与 BIER 胜出的机制根源](#3-技术原理四类组播技术对比与-bier-胜出的机制根源)
- [4. BIER 逐层拆解：BitString → BIFT → 无状态复制](#4-bier-逐层拆解bitstring--bift--无状态复制)
- [5. 第一性原理：时间尺度失配是 PIM 出局的根因](#5-第一性原理时间尺度失配是-pim-出局的根因)
- [6. 落地形态：与集合通信/NIC/DDC 的协同](#6-落地形态与集合通信nicddc-的协同)
- [7. 产业信号与标准话语权](#7-产业信号与标准话语权)
- [8. 数据缺口与可证伪预判](#8-数据缺口与可证伪预判)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 0. 一句话结论

> **draft-zhang-rtgwg-llmmoe-multicast-03（ZTE + 中国移动，2026-08-09）把 MoE token 分发定义为「短生命周期、高动态、高扇出的一对多传输」，并从四类组播技术中论证出 BIER（位索引显式复制）是唯一匹配 token 分发时间尺度的方案——因为只有 BIER 把「目的地集合编码进报文头」，让中间交换机零建树时间、零 per-flow 状态完成复制。这是 AI 训练网络数据面需求第一次以 use case 形式进入 IETF 路由工作组，也是「把路由决策从控制面移到数据面」主线的又一落地。**

---

## 1. 事实基线（一手全文验证）

### 1.1 文档属性

| 维度 | 内容 | 来源 |
|:-----|:-----|:-----|
| 标题 | Multicast use case in LLM MoE | IETF Datatracker 全文 |
| 版本/日期 | -03，2026-08-09（-02 于 07 月） | 同上 |
| 作者 | Zheng Zhang（ZTE）、Wei Duan（ZTE）、Xiaohu Xu（中国移动）、Yisong Liu（中国移动） | 同上 |
| 状态 | Active Internet-Draft（individual）| Intended status: Informational | 同上 |
| 过期 | 2027-02-10 | 同上 |
| 结构 | 6 节：Introduction / Use case（tokens dispatching）/ Multicast technologies analysis / IANA / Security / References | 同上 |
| 明确提及模型 | DeepSeek-V2/V3、Gemini 1.5 Pro、xAI Grok-1、Mistral 8×22B、Qwen3 | 同上 |

### 1.2 核心量化数据（draft 一手）

| 模型 | 专家总数 | 每 token 激活 | 说明 |
|:-----|:--------:|:------------:|:-----|
| Mixtral | 8 | 2（1 routed + 1 shared） | 最小激活比 |
| Llama4 Scout | 16 | 2 | |
| Llama4 Maverick | **128** | 2 | 高扇出候选 |
| **DeepSeekV3** | **256** | **9（8 routed + 1 shared）** | **最大扇出，draft 重点分析对象** |

**关键原文**：
> "one token needs to be sent to multiple experts, which is a typical multicast use case."
> "the selection process is very short, leaving no time for multicast technologies like PIM to establish a multicast tree."
> "BIER... allows the source GPU (similar to BFIR in BIER) to directly specify the destination expert group (similar to BFERs in BIER) and encapsulate it into the message, eliminating the time for multicast tree establishment. **Therefore, BIER is the most suitable multicast technology.**"

### 1.3 拓扑背景（draft Figure 1）

```
+-----------+               +-----------+
|  Spine 1  |               |  Spine x  |
+-+------+--+               +-+------+--+
  |      |                    |      |
+--------+      +----------+  +------+-+
|  Leaf 1  |     |  Leaf 2  | ... |  Leaf n  |
+-+--+---+-+     +----------+     +--+--+--+-+
  |  |   |                          |  |  |
GPU1..GPU8     GPU1..GPU8      GPU1..GPU8
  node 1          node 2           node m
```

- intra-node：激活专家都在同一节点（8 GPU/节点）→ 节点内组播
- inter-node：激活专家跨节点 → 跨 Leaf、甚至跨 Spine 组播
- DeepSeekV3 node restricted routing：先选 node group 再选 expert，**最多 4 节点**减少跨节点分发——但 draft 明确指出「it cannot avoid multicast between nodes」

---

## 2. 技术原理：MoE 为什么天然是组播问题

### 2.1 MoE 推理/训练的数据流本质

MoE（Mixture of Experts）的核心是**稀疏激活**：每个 token 只激活全部参数的一小部分（专家子集）。这带来一个数据面事实：

```
        +-----------------------------------------+
        |  source GPU (token producer)            |
        |  token t -> router decision -> experts {E2,E5,E9} |
        +--------------------+--------------------+
                             | same token t must reach 3 experts
          +------------------+------------------+
          v                  v                  v
        E2 (GPU2)          E5 (GPU5)          E9 (GPU9)
        +------ 1-to-N transmission = multicast definition ------+
```

- **Prefill 与 Decode 两阶段**都涉及 token 分发（draft §2 明确 "During the pre-filling and decoding phases"）
- 每 token 的专家组合**逐 token 变化**（DeepSeekV3 每 token 可能发往 9 个不同专家）
- 专家负载均衡要求**难以把专家限制在单节点内**（draft 原文："it is difficult to limit the number of experts to one node even if only two experts are used"）

### 2.2 现状实现：单播复制（ingress replication）的低效

源 GPU 对每个目标专家发送一份独立副本：

| 开销项 | 量化（DeepSeekV3 激活 9 专家） |
|:-------|:-------------------------------|
| 源 GPU 发送负载 | 9×（同一 token 发 9 份）|
| 网络流量 | 9×（跨节点场景）|
| 拥塞风险 | ↑（draft §2.2："the more packets there are, the greater the risk of congestion"）|

### 2.3 draft 提出的优化方向（node restricted routing）

- 先选 node group（≤4 节点）再选专家 → 减少跨节点流量
- 节点内：switch/GPU 收到 token 后**在节点内再分发**（利用高 intra-node 带宽）
- 但**无法完全避免跨节点组播**（draft 明示）

---

## 3. 技术原理：四类组播技术对比与 BIER 胜出的机制根源

### 3.1 四方案对比矩阵（draft §3 + RFC 交叉验证）

| 方案 | 建树/状态 | 带宽效率 | 动态适配 | 可靠性 | draft 结论 |
|:-----|:---------|:---------|:---------|:-------|:----------|
| **单播复制（现状）** | 无 | ❌ 源负载 N×、流量 N× | ✅ 天然动态 | ✅ 逐流可靠 | 低效但可行 |
| **PIM-SM（RFC 7761）** | ❌ 信令建树、接收者变→重建 | 中 | ❌ **选择过程 <ms 级来不及建树** | 树不稳定影响可靠 | **不适用** |
| **PIM-DM** | ❌ 洪泛+剪枝 | ❌ 消耗更多带宽 | 中 | — | 不推荐 |
| **ingress replication** | 无 | ❌ 带宽消耗大 | 中 | — | draft 明确不推荐 |
| **BIER（RFC 8279）** | ✅ **零 per-flow 状态**（BIFT 全局表）| ✅ 交换机级复制一次到位 | ✅ **源直接指定专家组，零建树时间** | 依赖底层（见 §3.2）| **最适** |

### 3.2 可靠性要求：组播可靠 > 单播可靠（draft §2.4）

draft 原文：
> "packet loss, long delays or jitters, and retransmissions during data transmission can impact LLM calculations... if even one destination fails to receive the data in time... the LLM calculation may need to be restarted"

第一性原理推导：LLM 训练/推理的 token 数据是**强同步屏障**——AllReduce 语义要求所有参与方拿到数据才能继续，任一分支丢包→重传→延迟→整批停滞（呼应 MEMORY「FT-HSDP：10 万 GPU 18min 一次故障」）。组播的可靠性难点在于**多分支中最差分支决定整体**（min-of-N 语义），比单播的 max-of-1 更严苛。

---

## 4. BIER 逐层拆解：BitString → BIFT → 无状态复制

### 4.1 核心概念（RFC 8279 一手）

```
BIER domain (multicast domain)
+--------------------------------------------+
|  BFR: Bit-Forwarding Router (one per router)|
|  BFIR: ingress BFR, encapsulate packets     |
|  BFER: egress BFR, de-encapsulate & deliver |
|  BIFT: Bit Index Forwarding Table           |
|    one per BFR, computed globally by IGP/BGP|
+--------------------------------------------+
```

**关键机制——BitString**：
- 域内每个 BFR 分配一个 **bit position**（1, 2, 4, 8...）
- 报文头携带 **BitString** = 目的地 BFR 集合的位图
- 例：BitString `0b000010110` → BFER 编号 {1, 2, 4}（bits 1,2,4 置位）

**转发过程（无状态复制）**：
```
BFIR receives token (target experts on BFR{1,2,4})
  -> encapsulate BIER header (BitString=0b000010110)
  -> lookup local BIFT: bit1->ifaceA, bit2->ifaceB, bit4->ifaceC
  -> when forwarding to ifaceA, clear bits not toward ifaceA (bitmask)
  -> transit BFRs do the same: lookup BIFT -> per-bit copy -> per-hop bitmask
  -> BFER{1,2,4} each receive one copy, de-encapsulate
```

**三个「无」**（BIER 与 PIM 的本质差异）：
1. **无显式建树**：不需要 PIM Join/Prune 信令，BIFT 由 IGP/BGP 全局计算（类似单播路由表）
2. **无 per-flow 状态**：中间 BFR 不保存「这个组播流往哪转发」，只看报文头 BitString
3. **无接收者注册**：BFER 不需要先加入组（SSM/ASM 语义都不需要）

### 4.2 为什么这匹配 MoE token 分发的时间尺度

| 维度 | PIM 模式 | BIER 模式 |
|:-----|:---------|:----------|
| 组变化 → 转发生效 | 信令建树（ms~s 级）| **零**（BitString 即目的）|
| 每 token 专家组合变 | 树要重建（不可能）| 报文头改几个 bit |
| 中间交换机资源 | 每流状态（转发表条目）| **零 per-flow 状态** |
| 源 GPU 角色 | 只能发单播/等树 | **BFIR：直接指定专家组** |

draft 原文：专家可编号为 BFR，源 GPU（BFIR）直接指定专家组（BFER）封装进报文——**Leaf/Spine/GPU 可预建 expert-based 转发表**。

### 4.3 BIER 封装形态（RFC 8296 / BIERin6 / Unmasked BIER）

draft §3 明确三种封装：
1. **RFC 8296**：MPLS 与非 MPLS 网络的 BIER 封装（标准 BIER 头）
2. **BIERin6（draft-ietf-bier-bierin6-13）**：IPv6 网络承载 BIER（对应 AI 网络 RoCEv2/IPv6 趋势）
3. **Unmasked BIER（draft-zzhang-bier-unmasked-bier-01）**：不逐跳掩码、减少处理

### 4.4 控制面前置条件

draft 指出 BIER 应用前需要**控制面协商**（source GPU ↔ experts 的数据传输协商）——即专家编号分配、BIFT 同步、封装协商。这与集合通信库（NCCL/MSCCL）的 rank 分配机制天然衔接。

---

## 5. 第一性原理：时间尺度失配是 PIM 出局的根因

### 5.1 形式化：三类网络操作的时延标尺

```
operational latency scale (log):
1ns -- 10ns -- 100ns -- 1us -- 10us -- 100us -- 1ms -- 10ms -- 100ms
      |        |        |       |        |        |
  forwarding  NIC hw   GPU kernel  PIM Join  IGP conv
  table       process  schedule    (ms)     (s)
                         |
                     token routing
                     (expert select, us)
```

**时间尺度失配**：token 的专家选择发生在 GPU 内部（μs 级），而 PIM 建树需要控制面信令往返（ms 级）——**决策尺度比建树尺度快 2-3 个数量级**。任何「先建树再传输」的机制，在 token 分发场景都输在起跑线。

### 5.2 「把路由决策从控制面移到数据面」主线的又一落地

BIER 的本质：**目的地集合（BitString）成为报文数据的一部分**，转发决策从「查询控制面建立的树」变成「数据面直接读报文头位图」。这与知识库已沉淀的主线同构：

| 既有主线 | 机制 | 与 BIER 的共性 |
|:---------|:-----|:---------------|
| TensorCast 控制面/数据面分离 | 数据面承载转发 | 决策随数据走 |
| Prefix Caching 使 system prompt 稳定 | 缓存命中 | 无状态查表 |
| MoE all-to-all 通信 | 集合通信库调度 | 目的集合在数据中 |

### 5.3 量化收益估算（第一性原理推导，非实测）

以 DeepSeekV3 激活 9 专家、跨节点场景为例：
- 单播复制：源 GPU 需发送 9 份副本，跨节点流量 = 9 × token 大小
- BIER 组播：源 GPU 发送 1 份，中间交换机复制（若 9 专家分布在 3 个节点 → 流量 ≈ 3 × token 大小）
- **流量削减约 3×**（取决于专家分布集中度）
- 更关键的是**源 GPU 发送负载**从 9 份降到 1 份——释放源 GPU 的 NIC 带宽与 DMA 引擎

> ⚠️ 诚实标注：上述为基于扇出的理论估算，无公开实测数据（draft 本身也是 use case 文档，无实现数据）。

---

## 6. 落地形态：与集合通信/NIC/DDC 的协同

### 6.1 draft 明确的三层协同

draft 原文：
> "the multicast approach needs to work in conjunction with the LLM software. It may work in conjunction with the implementation of collective communication and NIC."

| 层 | 角色 | 协同点 |
|:---|:-----|:-------|
| LLM 软件（router）| 决定 token→专家映射 | 把专家组合翻译成 BitString |
| 集合通信库（NCCL/MSCCL）| 管理 rank/通信原语 | All-to-All 中识别可组播子集 |
| NIC | 报文封装/发送 | BIER 头封装、BFIR 角色 |

### 6.2 与 DDC 架构的天然契合

国产 DDC（分布式解耦架构）核心特征 = **集中控制 + 无状态转发**：
- 控制器全局计算 expert-based 转发表（BIFT）
- 转发面无状态复制（BIER）
- 这与新华三 DDC 万卡无损、华为 CloudMatrix 的「控制器 + 白盒转发」范式完全同构

**推论**：BIER 组播卸载是国产 DDC 架构的「标准侧加分项」——硬件形态（集中控制+无状态）已经就绪，只差标准与软件栈。

### 6.3 与学术侧互证

| 信号 | 关系 |
|:-----|:-----|
| StrataCL（华为 fabric-native 通信库）| 软件层下沉 vs 网络层卸载——互补分工 |
| Incast-Free Rate-Based Scheduling | 调度面治理 vs 组播数据面卸载——双线 |
| GB300 MoE 预训练纪录（吞吐=通信决定）| 组播卸载是「通信决定吞吐」的工程化出路 |

---

## 7. 产业信号与标准话语权

### 7.1 中国厂商主导 AI 网络数据面标准

- **ZTE + 中国移动**主导该 use case（数据面）
- 同期 BIER-TE BGP-LS 扩展（draft-cz-bier-bgp-ls-bier-te-ext-07）同为相关方向
- 对比：遥测面（PBT-M）由 Futurewei/Huawei/Cisco 主导——**中国厂商在数据面标准话语权上升，与国产 GPU/DDC 硬件形成「硬件+标准」双轮**

### 7.2 标准路径判断

- use case 文档（Informational）→ 若被 rtgwg 吸收 → 机制文档（Standards Track）
- 12 个月内观察是否转 WG 文档（可证伪预判 H1）

---

## 8. 数据缺口与可证伪预判

### 8.1 数据缺口（诚实标注）

| 缺口 | 说明 |
|:-----|:-----|
| 实测收益 | BIER 组播卸载在真实 MoE 训练网络的端到端收益（对比 ingress replication）无公开实测 |
| 控制面接口 | draft 只提「需与集合通信/NIC 配合」，无具体接口设计（BFIR 角色由谁承担、BitString 如何由 NCCL 生成）|
| 可靠性机制 | draft 提可靠性要求但未给组播可靠传输方案（ARQ/FEC？重传粒度？）|
| intra-node 细节 | 节点内组播由 GPU/switch 承担的具体实现未展开 |

### 8.2 可证伪预判（2027 年核验）

| # | 预判 | 核验方式 |
|:--|:-----|:---------|
| H1 | draft 12 个月内转 WG 文档（rtgwg 吸收或新建）| 跟踪 draft 状态 |
| H2 | BIER 组播卸载 2027 年前在国产 DDC 或头部云厂商 AI 集群有商用部署/测试 | 厂商发布/会议论文 |
| H3 | 出现「集合通信库 + BIER」集成提案（NCCL/MSCCL 对 BIER 的抽象层）| IETF/学术论文 |

---

## 参考来源

### 外部一手
- IETF Datatracker: draft-zhang-rtgwg-llmmoe-multicast-03（2026-08-09，全文）— https://datatracker.ietf.org/doc/draft-zhang-rtgwg-llmmoe-multicast/
- RFC 8279（BIER 架构）、RFC 8296（BIER 封装）、RFC 7761（PIM-SM）
- draft-ietf-bier-bierin6-13、draft-zzhang-bier-unmasked-bier-01（draft §3 引用）

### 内部知识库
- [`2026-08-11-ietf-ai-network-standards-deep-analysis.md`](2026-08-11-ietf-ai-network-standards-deep-analysis.md) — 三线总览
- [`2026-08-11.md`](2026-08-11.md) — 追踪速记
- [`2026-08-11-mpls-pbt-m-on-path-telemetry-deep-analysis.md`](2026-08-11-mpls-pbt-m-on-path-telemetry-deep-analysis.md) — 遥测面对偶
- MEMORY.md — LLM 推理统一框架 / 假存活陷阱 / MoE 组播双线

---

## Changelog
| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-11 | v1.0 | 创建。draft-zhang-rtgwg-llmmoe-multicast-03 全文深度分析：MoE token 分发组播本质、四类组播技术对比、BIER BitString/BIFT/无状态复制逐层拆解、时间尺度失配第一性原理、与集合通信/NIC/DDC 协同、可证伪预判 H1-H3 |
