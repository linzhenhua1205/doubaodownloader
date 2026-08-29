# 📡 MPLS On-Path Telemetry 成 WG 文档：PBT-M 逐跳遥测标准侧推进

> **类型**: 深度专题 | **日期**: 2026-08-11 | **定位**: draft-ietf-mpls-on-path-telemetry-flag-03 技术原理深挖——PBT-M（基于报文标记的明信片式逐跳遥测）的机制设计、MNA 编码格式、开销模型、流量控制与安全模型；衔接 [`2026-08-11-ietf-ai-network-standards-deep-analysis.md`](2026-08-11-ietf-ai-network-standards-deep-analysis.md)（三线总览）、[`2026-08-11.md`](2026-08-11.md)（追踪速记）
> **数据源**: IETF Datatracker 全文抓取（-03 全文 47KB）+ RFC 9994/9789/9197/9326/9259 一手 + 第一性原理推导
> **关联文件**: [`2026-08-11-ietf-ai-network-standards-deep-analysis.md`](2026-08-11-ietf-ai-network-standards-deep-analysis.md)、[`2026-08-11.md`](2026-08-11.md)、[`2026-08-11-llmmoe-multicast-bier-standard-deep-analysis.md`](2026-08-11-llmmoe-multicast-bier-standard-deep-analysis.md)

---

## 📑 目录

- [0. 一句话结论](#0-一句话结论)
- [1. 事实基线（一手全文验证）](#1-事实基线一手全文验证)
- [2. 技术框架：PBT-M 架构与数据流](#2-技术框架pbt-m-架构与数据流)
- [3. 编码细节：MNA Sub-Stack 三 LSE 结构](#3-编码细节mna-sub-stack-三-lse-结构)
- [4. 核心机制：流路径发现 + 数据关联 + 负载控制](#4-核心机制流路径发现--数据关联--负载控制)
- [5. 开销模型：固定开销 vs in-stack passport](#5-开销模型固定开销-vs-in-stack-passport)
- [6. 安全模型：单信任域 + 三重防线](#6-安全模型单信任域--三重防线)
- [7. 第一性原理：最小代价可观测性](#7-第一性原理最小代价可观测性)
- [8. 与 AI 训练网络的关系](#8-与-ai-训练网络的关系)
- [9. 数据缺口与可证伪预判](#9-数据缺口与可证伪预判)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 0. 一句话结论

> **draft-ietf-mpls-on-path-telemetry-flag-03（Futurewei + Huawei + Cisco，2026-08-10，已转 WG 文档）定义了 PBT-M——用 MPLS MNA 子栈中单个 flag bit 触发「明信片式」逐跳遥测：数据面仅做标记，遥测数据经带外 postcard 通道导出，固定开销 3 个 LSE（12 octets）不随路径长度增长，标记率默认 ≤1/1000、postcard 生成率默认 ≤1000/s 双限速防 DoS。这是 AI 网络端到端可观测性（逐跳时延/丢包定位）在 MPLS/SR-MPLS 侧的标准化基座，与 IPv6 IOAM 构成两大数据面的遥测对偶。**

---

## 1. 事实基线（一手全文验证）

### 1.1 文档属性

| 维度 | 内容 | 来源 |
|:-----|:-----|:-----|
| 标题 | MPLS On-Path Telemetry Network Action Flag for OAM（PBT-M）| IETF Datatracker 全文 |
| 版本/日期 | -03，2026-08-10 | 同上 |
| 作者 | Haoyu Song（Futurewei）、Giuseppe Fioccola（Huawei）、Rakesh Gandhi（Cisco）| 同上 |
| 状态 | **WG 文档（mpls WG）**，Intended: Standards Track | 同上 |
| 评审 | OPSDIR early review（Carlos Pignataro）；RTGDIR review（Bruno Decraene）；shepherd Tony Li | 同上 |
| 机制 | Postcard-Based Telemetry with Packet Marking（明信片式 + 报文标记）| 同上 |
| 触发 | MNA Sub-Stack（RFC 9994）Opcode 1 / Format D LSE 单个 P-flag bit | 同上 |
| 前身/对偶 | SRv6 OAM O-bit（RFC 9259）；IPv6 IOAM trace（RFC 9197）/ DEX（RFC 9326）| 同上 |
| 过期 | 2027-02-11 | 同上 |

### 1.2 核心设计目标（draft §1）

- **数据面可见性**：逐包查看转发路径上的实时状态（路径、每节点时延、丢包位置与原因）
- **低开销**：不增补用户报文大头部，遥测指令走带外
- **高灵活**：可配置采集任意新数据（通过管理面/控制面配置数据集模板）
- **安全部署**：负载控制、DoS 缓解、配置可扩展性、部分升级路径管理

---

## 2. 技术框架：PBT-M 架构与数据流

### 2.1 五组件架构（draft Figure 1）

```
+------------+        +-----------+
| Network    |(------ | Telemetry |
| Management |        | Data      |
+-----:------+        | Collector |
      :               +-----------+
      :configurations      ^
      :                    |postcards (OAM pkts)
......:....................:........
      V                    |
+------+-+     +-----+--+  |  +------+-+
| Head   |====>| Path   |====>| Path   |====>| End    |===>
| Node   |     | Node A |     | Node B |     | Node   |
+--------+     +--------+     +--------+     +--------+
 mark usr pkts  gen postcards  gen postcards  gen postcards
 gen postcards                                unmark usr pkts
```

**数据流五步**：
1. **配置**：管理面配置头部节点标记策略（概率/时间间隔）+ 各节点数据集模板
2. **标记**：头部节点对用户报文打 P-flag（MNA Format D LSE 单 bit）
3. **触发**：每个 PBT-M-aware 节点检测到 P-flag → 按本地配置采集数据
4. **导出**：生成 postcard（专用 OAM 报文）发往 collector（带内或带外通道均可）
5. **关联**：collector 汇聚同一用户报文的所有 postcard → 推断转发路径 + 分析数据集

### 2.2 七个设计优势（draft §2）

| # | 优势 | 含义 |
|:--|:-----|:-----|
| 1 | 不加超大头部，遥测信令留在数据面 | 对用户流量扰动最小 |
| 2 | 可扩展采集任意新数据 | 数据集由管理面配置，无需改协议 |
| 3 | 中转节点零用户报文处理（不编辑/不增补）| 遥测数据与业务转发完全解耦 |
| 4 | 头部节点只提供触发，不指定数据类型 | 各节点可按能力/需求本地决定采集内容 |
| 5 | 数据可加密/认证后再传输 | 防窃听/中间人 |
| 6 | **被监控报文丢包时，前面各跳的 postcard 仍有效** | 精确诊断丢包位置与原因（关键优势）|
| 7 | 原始数据可在数据面聚合/压缩 | 降低导出流量 |

---

## 3. 编码细节：MNA Sub-Stack 三 LSE 结构

### 3.1 MNA 框架（RFC 9789 / RFC 9994）

MPLS Network Action（MNA）扩展了 MPLS 标签栈：
- **in-stack**：MNA Sub-Stack（RFC 9994）——网络动作与辅助数据编码在栈内
- **post-stack**：MNA 后栈头（draft-ietf-mpls-mna-ps-hdr-19）——编码在载荷后

PBT-M 用 **in-stack Sub-Stack** 的最小形态：单 flag bit。

### 3.2 三 LSE 编码（draft Figure 2）

```
 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         MNA-Label = bSPL (4)          | TC  |S|      TTL      | (A)
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Opcode=1   |         Data=0          |R|IHS|S|NASL=1 |U|NAL=1| (B)
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|1|                  Data=0                   |S|P|      0      | (D)
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

| LSE | 作用 | 关键字段 |
|:----|:-----|:---------|
| Format A | MNA Sub-Stack 指示器 | MNA bSPL = 4（特殊标签）|
| Format B | 初始 Opcode LSE | Opcode=1（Flag-Based Network Action Indicators without Ancillary Data）；IHS=01（Hop-by-Hop 范围）；NAL=1（指向一个 Format D）|
| Format D | 承载 P-flag | **P 位（bits 24-31 区域，TBD1 待 IANA 分配）** |

**关键设计约束（RFC 9994 §5.2 + draft §4.1）**：
- P-flag 是**可变位**（同流不同报文可能不同）→ 绝不能放在 LSE 最高 20 位（label value，用于 ECMP hash）
- TC 也参与 hash 时，不能放在最高 23 位
- **必须放在 Format D LSE bits 24-31**（尾部数据位）→ 保证不扰动 ECMP 负载均衡、避免流内乱序
- 具体 bit 位置待 IANA 从「Network Action Flags Without Ancillary Data」注册表分配（IETF Review 流程）

### 3.3 动作定义（draft 按 RFC 9994 §10 格式）

- **Format**: Format A + Format B（Opcode 1）+ Format D；无 Format C、无 Ancillary Data
- **Scope**: Hop-by-Hop（IHS=01）——所有 on-path PBT-M-aware 节点处理；**次末跳不得移除 NAS**（egress 也要发 postcard）
- **Processing**: P-flag=1 且数据采集使能 → 每标记报文生成并导出一个 postcard；不支持该动作的节点 U=0 跳过
- **Interactions**: 不影响其他网络动作，仅触发遥测导出

---

## 4. 核心机制：流路径发现 + 数据关联 + 负载控制

### 4.1 流路径发现（Flow Path Discovery，draft §4.2）

**无需预配置路径**（对比 IOAM DEX 需预配置每个 on-path 节点）：
1. 管理面在头部节点配置标记概率/时间间隔
2. 首个被标记报文 → 各节点导出**基础数据集**（node ID + per-LSE TTL 向量）
3. collector 动态学习流路径
4. 若需更多数据类型 → 管理面再向路径上目标节点下发数据集模板
5. 路径变化（ECMP/动态路由）→ 新路径被快速学习 → 管理面更新新路径节点

**配置抖动缓解**：控制器对陈旧配置采用**优雅老化（graceful aging）**而非每次路径变化都显式撤销——降低配置 churn。

### 4.2 数据关联（Packet Identity for Export Data Correlation，draft §4.3）

**挑战**：postcard 可能乱序到达、可能丢失——collector 需要把同一用户报文的所有 postcard 关联起来并推断跳序。

**MPLS 特有难点**：标签栈中每个 LSE 有独立 TTL，只有栈顶 TTL 逐跳递减；PUSH/POP 改变栈顶 → **单 TTL 值端到端不单调**（POP 后可能增大）。

**解法——per-LSE TTL 向量**：
- PBT-M 节点上报「收到的完整标签栈的每个 LSE TTL」（per-LSE TTL vector）+ node ID
- collector 从 TTL 向量重建跳序，必要时用 IGP 拓扑解析路径上的 PUSH/POP 操作

**两种关联手段**：
| 手段 | 机制 | 条件 |
|:-----|:-----|:-----|
| Flow ID | 标签栈作为流 ID（LSP/FEC 粒度）；若需 5-tuple 粒度则额外采集 | 标记间隔足够大 → 高概率关联 |
| 时间戳 | Flow ID + 各节点时间戳推断归属 | 需要 PTP/NTP 全网时间同步，精度 << 最小跳间时延 |

**保证性关联**：单标记报文在飞约束（at most one marked packet in flight per correlation key）——入口节点间隔标记，间隔 > 网内最大报文寿命 + 最大 postcard 导出延迟 → 无歧义关联（牺牲标记率）。

**硬规则**：无法无歧义关联的 postcard **必须丢弃**而非报为路径的一部分（防污染）。

**多 collector 负载均衡**：同一 correlation key 的所有 postcard 必须哈希到同一 collector（或公共关联函数）——否则路径无法重建。

### 4.3 负载控制（Load Control，draft §4.4）——双限速 + 控制面保护

**双层速率限制（默认值，操作员可调）**：

| 层 | 限制 | 默认值 |
|:---|:-----|:-------|
| 标记率（头部节点）| 单流标记比例 | **≤ 1/1000（0.1%）** |
| postcard 生成率（每个 PBT-M-aware 节点）| token bucket 上限 | **平均 1000/s，burst 2000**，超限跳过并计数 |

**控制面保护（强制性）**：
- postcard 生成不得降级控制面功能（尤其 IS-IS 邻接维护与链路状态洪泛）
- postcard 生成必须在 punt/slow path 上以**严格低于控制面流量**的优先级调度
- 资源争用时，postcard 生成被节流/跳过（计数）以让位控制面

**域边界处理（ingress filtering）**：
- PBT-M 限定单一信任域
- 域边界节点对入域报文**必须清除 P-flag 或丢弃**——防止外部注入标记报文触发 postcard 洪泛
- 保证只有域内自己的头部节点能设置 P-flag

---

## 5. 开销模型：固定开销 vs in-stack passport

### 5.1 形式化模型（draft §4.4 一手公式）

设：
- m = 标记率（默认 1/1000）
- N = 路径上 PBT-M-aware 节点数
- R = 流报文速率
- Sc = 被监控报文平均大小
- Sp = postcard 平均大小（含封装与导出数据）

**推导**：
- 单标记报文触发 ≤N 个 postcard（每节点一个）→ 网络内 postcard 放大 N×
- 每节点 postcard 生成率 ≈ m×R
- 全网 postcard 包率 ≈ m×N×R
- 单链路字节开销 ≈ m×(Sp/Sc)；全网 ≈ m×N×(Sp/Sc)
- collector 摄取 = 所有被监控流的 m×N×R 之和

**工作示例（draft 原例）**：m=1/1000, N=8, R=1,000,000 pkt/s, Sc=1000 octets, Sp=128 octets
- 每节点 ≈ 1000 postcards/s（已达默认单节点上限）
- 全网 ≈ 8000 pkt/s
- **全网字节开销 ≈ 0.1% of flow**

### 5.2 固定开销的本质优势（draft §5.4）

| 维度 | PBT-M | in-stack passport（IOAM trace）|
|:-----|:------|:-------------------------------|
| 报文开销 | **固定 12 octets（3 LSE）**，与路径长度/数据量无关 | 逐跳累积，随路径长度与数据集大小增长 |
| MLD/MSD 消耗 | 固定 3 个 label 位置（与 N 无关）| 随路径增长 |
| PMTU 影响 | 无逐跳 PMTU 影响 | 长路径可能超 PMTU（数十至数百 octets）|
| 丢包诊断 | ✅ 前面各跳 postcard 仍有效 | ❌ 报文丢了数据也丢 |

**MSD 交互**（draft §5.1）：使能 PBT-M 的节点必须在 MSD 广告（RFC 8491）中扣减 PBT-M 消耗的 label 数（最多 3），让控制器正确判断 SID 栈是否支持；PBT-M Sub-Stack 必须在 on-path 节点的可读标签深度（RLD）内。

### 5.3 与 IOAM DEX 的差异

PBT-M 相对 IOAM DEX（RFC 9326）的增量：
1. **MNA flag 编码**（MPLS 专用）
2. **流路径发现机制**（§4.2）——控制器无需预先配置每个 on-path 数据面节点即可开始采集

---

## 6. 安全模型：单信任域 + 三重防线

### 6.1 威胁模型（draft §6）

P-flag 是**可变的、未认证的、逐跳处理**的 bit：
- 被攻陷/误配置的 on-path 节点可 set/clear/flip
- set/spoof → 驱动过量 postcard 生成（对节点与 collector 的 DoS 向量）
- clear/flip → 压制或伪造遥测（不可靠测量）

**不做密码学保护的根因**：对单个逐包可变 bit 做逐跳带内密码保护不现实，且违背低开销目标——与 SRv6 O-bit（RFC 9259）、IOAM DEX 共享此属性。

### 6.2 三重防线（enabled-by-default）

| 防线 | 机制 | 效果 |
|:-----|:-----|:-----|
| 1. 域边界入口过滤 | 入域清除/丢弃 P-flag | 完全缓解外部注入（域内节点不受限）|
| 2. 双限速 | 标记率 + postcard 生成率上限（本地强制）| 构造性界住 DoS 影响——即使全网标记伪造也不能超过配置速率 |
| 3. 计数器 + 限速告警 | 异常标记/postcard 速率检测 | 侦探性措施，暴露异常供操作员响应 |

**残余风险（诚实标注）**：信任域内被攻陷节点仍可 spoof/suppress P-flag——DoS 被限速界住且可检测，但该节点产出的测量完整性无法保证。这是轻量带内标记的固有属性。

---

## 7. 第一性原理：最小代价可观测性

### 7.1 可观测性的本质

> 可观测性的本质 = **用最小代价回答「包在哪跳经历了什么」**。

PBT-M 是这一目标的最优解形式：
- **触发在数据面**（单 bit，零建树）
- **传输在带外**（postcard，与业务转发解耦）
- **配置在管理面**（数据集模板，可动态调整）

三面职责切分 → 遥测收集不干扰业务转发 → 呼应知识库「带内+带外双轨遥测」主线（OTel 主机侧对偶）。

### 7.2 为什么 postcard 优于 in-stack（丢包诊断第一性原理）

```
in-stack passport (accumulate in packet):
  pkt: [data][hop1][hop2][hop3...]
  if hop3 drops -> hop1/hop2 data lost with the packet -> know "dropped" but not "where"

postcard (out-of-band postcard):
  hop1->postcard OK  hop2->postcard OK  hop3->postcard MISS (packet dropped here)
  -> collector gets hop1/hop2 postcards, missing hop3 -> pinpoint drop location
```

**丢包定位是 AI 训练网络 RAS 的关键**——万卡训练中一个丢包链路导致整批停滞（FT-HSDP），PBT-M 逐跳遥测正是「假存活」诊断（NCCL 挂起时 utilization% 仍 100%）的标准侧解法。

### 7.3 与 OTel/OTLP 的统一平面

| 层 | 遥测机制 | 覆盖 |
|:---|:---------|:-----|
| 应用/主机 | OTel/OTLP（Go 编译插桩）| 主机侧指标/链路 |
| 网络设备 | PBT-M（MPLS）/ IOAM（IPv6）| 网络侧逐跳路径/时延/丢包 |
| 统一消费 | 统一 OTLP 平面 | 超节点软件底座 |

PBT-M = 网络设备侧的「带外遥测」标准对偶——统一 OTLP 平面可同时消费主机与网络遥测。

---

## 8. 与 AI 训练网络的关系

### 8.1 三线闭环中的观测面

```
EXECUTION (data plane)    OBSERVATION (obs plane)    DECISION (decision plane)
MoE token dispatch    ->  per-hop latency/drop    ->  fault diagnosis
BIER stateless mcast      PBT-M mark+postcard        AIOps/NORIA KG
```

### 8.2 对超节点/万卡训练的直接含义

1. **慢节点/丢包定位**：PBT-M 逐跳遥测 → 快速定位训练网络中「包在哪跳经历了什么」→ 直接服务 RAS 与故障恢复（训练暂停等恢复的 checkpoint 策略需要快速定位）
2. **SLO 契约执行**：与推理服务 SLO 契约（Cascade/HorizonServe）互证——遥测是 SLO 监控的网络层基座
3. **MPLS/SR-MPLS 存量网络**：AI 数据中心新建多为 IPv6/RoCE，但存量 MPLS 骨干/跨域场景需要 PBT-M——两大数据面（IPv6/SRv6 + MPLS）都有了标准遥测机制

---

## 9. 数据缺口与可证伪预判

### 9.1 数据缺口（诚实标注）

| 缺口 | 说明 |
|:-----|:-----|
| 实现数据 | WG 文档，无实现/测试/部署数据；限速默认值（1/1000、1000/s）标注「starting points intended for calibration by the WG」|
| 与 AI 网络集成 | draft 未提 AI 训练场景（通用 MPLS OAM）；AI 网络集成需厂商实现 |
| 数据面资源 | postcard 生成在 punt/slow path 的具体资源开销无量化数据 |

### 9.2 可证伪预判（2027 年核验）

| # | 预判 | 核验方式 |
|:--|:-----|:---------|
| H1 | PBT-M 12-18 个月内进入 RFC 发布通道（已 WG + 双 review）| 跟踪 IESG 状态 |
| H2 | 2027 年前出现 MPLS/SR-MPLS 网络 PBT-M 商用实现（华为/Cisco 路由平台）| 厂商发布/互操作测试 |
| H3 | AI 集群遥测与 PBT-M 集成提案（IOAM/PBT-M 双栈遥测平面）| IETF/厂商白皮书 |

---

## 参考来源

### 外部一手
- IETF Datatracker: draft-ietf-mpls-on-path-telemetry-flag-03（2026-08-10，全文）— https://datatracker.ietf.org/doc/draft-ietf-mpls-on-path-telemetry-flag/
- RFC 9994（MNA Sub-Stack）、RFC 9789（MNA Framework）、RFC 9197（IOAM trace）、RFC 9326（IOAM DEX）、RFC 9259（SRv6 OAM）、RFC 8491（MSD signaling）、RFC 7011（IPFIX）、RFC 7015（Flow Aggregation）、RFC 5476（PSAMP）

### 内部知识库
- [`2026-08-11-ietf-ai-network-standards-deep-analysis.md`](2026-08-11-ietf-ai-network-standards-deep-analysis.md) — 三线总览
- [`2026-08-11.md`](2026-08-11.md) — 追踪速记
- [`2026-08-11-llmmoe-multicast-bier-standard-deep-analysis.md`](2026-08-11-llmmoe-multicast-bier-standard-deep-analysis.md) — 数据面对偶
- MEMORY.md — 假存活陷阱 / 带内遥测主线 / FT-HSDP

---

## Changelog
| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-11 | v1.0 | 创建。draft-ietf-mpls-on-path-telemetry-flag-03 全文深度分析：PBT-M 五组件架构、MNA 三 LSE 编码（Format A/B/D + P-flag bits 24-31）、流路径发现/per-LSE TTL 向量关联/双限速负载控制、固定 12-octets 开销模型（m×N×R 公式）、单信任域三重防线安全模型、最小代价可观测性第一性原理、与 AI 训练网络三线闭环关系、可证伪预判 H1-H3 |
