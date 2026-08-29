# 🛡️ 可靠性治理三条新路径：PLB 受控降级 / Descriptive Dispatch 执行链量化 / Workload Buoyancy 通用抽象——框架与原理

> **概要**: 2026-08-12 arXiv 批次三篇论文从三个方向扩展 AI 系统的可靠性治理边界：① **PLB**（arXiv:2608.11836, SRDS 2026）反驳「弹性=故障后默认恢复路径」假设，提出 **repair-to-target 策略**实现差异化 QoS 降级（Premium/Mixed/Freemium 三角色），把「故障后容量受损期的服务延续方式」变成一等设计对象——**恢复与降级是两条并行路径**；② **Descriptive Dispatch**（arXiv:2608.11524, LLNL）把**执行链自身可靠性**变成可量化测试对象——432 runs 全组合测试（5 特征维度×4 prompt 风格）量化派发 agent 成功率 97.9%，描述性元数据把多集群作业成功执行率 48%→87%、5/10 应用最高 3.3x；③ **Workload Buoyancy**（arXiv:2602.22852, Umeå）提出 **buoyancy 抽象**（船浮水的隐喻）整合应用级指标与共享资源争用系统级洞察，显式刻画多资源 bottleneck/headroom，比传统启发式瓶颈指示准确度 +19.3%，可 drop-in 替代。三条线分别承接 **FT-HSDP/Concordia（恢复容量）→ PLB（受控降级）**、**Workflow Cards（执行 provenance）→ Descriptive Dispatch（执行链量化）**、**ElastiCo（干扰感知编排）→ Workload Buoyancy（通用瓶颈抽象）**，共同揭示可靠性治理对象的三次扩展：**故障域→性能域、系统→执行链、恢复→降级**。
>
> **关键词**: 受控降级 · repair-to-target · 差异化 QoS · 执行链可靠性 · 描述性元数据 · buoyancy 抽象 · 噪声邻居 · 瓶颈识别 · 可靠性治理
>
> **数据源**: arXiv:2608.11836（PLB, 12 Aug 2026）· arXiv:2608.11524（Descriptive Dispatch, 12 Aug 2026）· arXiv:2602.22852v2（Workload Buoyancy, replaced 12 Aug 2026）三篇 HTML 全文精读；08-13 reliability-testing 日报登记
>
> **素材分级**: 🔵 一手论文全文（3 篇 HTML 解析，PLB 62K 字符 / Dispatch 48K / Buoyancy 82K）· 🔵 既有研究线锚点（FT-HSDP/Concordia / Workflow Cards / ElastiCo 均在库）· 🔵 08-13 日报量化登记
>
> **日期**: 2026-08-14 | **领域**: 可靠性测试 × 集群治理 × 故障处理

---

## 📑 目录

- [〇、结论概要](#〇结论概要)
- [一、研究线定位：三条承接链](#一研究线定位三条承接链)
- [二、PLB：故障处理从「恢复容量」转向「受控降级」](#二plb故障处理从恢复容量转向受控降级)
- [三、Descriptive Dispatch：执行链自身成为可量化可靠性对象](#三descriptive-dispatch执行链自身成为可量化可靠性对象)
- [四、Workload Buoyancy：干扰/瓶颈诊断的通用抽象](#四workload-buoyancy干扰瓶颈诊断的通用抽象)
- [五、三条线的共性原理：可靠性治理对象的三次扩展](#五三条线的共性原理可靠性治理对象的三次扩展)
- [六、与知识库互证](#六与知识库互证)
- [七、批判性审视](#七批判性审视)
- [八、可证伪预测](#八可证伪预测)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 〇、结论概要

**一句话：三篇论文共享同一演进逻辑——可靠性不再只是「故障发生后恢复系统」，而是「在容量受损、执行链路、资源争用三种场景下，把系统行为的边界条件设计成可量化、可控制、可诊断的对象」。**

1. **PLB 补上恢复之外的降级维度**：FT-HSDP/Concordia 回答「故障后多久恢复」，PLB 回答「恢复之前如何服务」——替换副本需置备+同步才有容量，固定预算下容量恢复不是即时路径；**受控降级（differentiated degradation）是与恢复并行的一等设计路径**，不是临时状态。
2. **repair-to-target 是降级控制的机制核心**：三角色（Premium/Mixed/Freemium）规范化 → 按幸存集计算目标角色向量（比例缩放+边界特例）→ 修复角色分配——**「目标不是满容量配置，而是当前容量下的最优分配」**，Mixed 角色吸收残差、跨类移动受 floor 保护。
3. **执行链可靠性 = 可量化测试对象**：Descriptive Dispatch 给出**组合式可靠性测试方法论模板**（特征维度×风格全组合 + 成功率基线 + 工具调用审计），把「agent 派发是否可靠」从轶事变成 432 runs 的统计事实——97.9% 成功率、元数据 48%→87%。
4. **描述性元数据是低成本高杠杆抓手**：48%→87% 的跃升来自「消除架构不匹配」（让 job 转换后的语义与目标集群能力对齐），不是更强的推理或更多采样——与 AI4AI「结构化信息 > 更多推理」同构。
5. **buoyancy 是干扰诊断的通用抽象**：从「ElastiCo 式专用干扰感知」走向「通用瓶颈/余量刻画」——应用级指标与系统级争用整合、无需先验 profiling、可 drop-in 替代传统启发式；**「噪声邻居导致隐性性能故障」的识别从专用方案走向通用抽象**。

---

## 一、研究线定位：三条承接链

| 承接链 | 既有锚点 | 新论文 | 演进方向 |
|:-------|:---------|:-------|:---------|
| 故障处理 | FT-HSDP（10 万 GPU 18min 故障×10min 恢复 44%→80%）、Concordia（恢复时延秒级）| **PLB**（arXiv:2608.11836）| 恢复容量 → **受控降级**（两条并行路径）|
| 执行链可靠性 | Workflow Cards（08-12 执行 provenance 文档化）| **Descriptive Dispatch**（arXiv:2608.11524）| 执行链文档化 → **执行链可量化测试** |
| 干扰诊断 | ElastiCo（08-11 干扰感知编排，共享 GPU 池隔离 MPS→ElastiCo→eIRWR）| **Workload Buoyancy**（arXiv:2602.22852v2）| 专用干扰感知 → **通用瓶颈抽象** |

**三篇论文的共同身份**：都不是新模型或新算法，而是**治理方法论文献**——它们回答「AI 系统变复杂后，可靠性/性能问题如何被系统性地发现、度量、控制」。这与本地「可靠性测试」研究线（FTA/容错/故障诊断）完全同向。

---

## 二、PLB：故障处理从「恢复容量」转向「受控降级」

### 2.1 反驳的默认假设（论文第一性起点）

> "Elasticity is commonly presented as the **default response** to capacity loss after failures, since replacement replicas can compensate for failed nodes and restore pre-incident service levels. **Replacement capacity entails both delay and additional resource commitment**, as replicas must be provisioned and synchronized before they can serve traffic."

**逻辑链**：
1. 故障后系统进入 **post-fault regime**（幸存集缩小、重定向需求/重连/重试造成瞬时压力）——即使名义可用，尾延迟也可能放大
2. 弹性（加副本）不是即时路径：**置备+同步**需要时间与额外资源
3. 固定预算/受限条件下，容量恢复不可作为默认假设
4. 因此：**故障处理必须定义「容量受损时服务如何延续」**——这就是受控降级的出场

### 2.2 问题形式化（§II）

| 元素 | 形式化 | 含义 |
|:-----|:-------|:-----|
| 副本集 | ℛ = {r₁,…,r_K}，固定预算 K | 故障处理期不替换 |
| 会话 | 持久连接上的查询序列，class(s) ∈ {P, F} | 会话级、非迁移路由 |
| 健康状态 | h(r,t) ∈ {Healthy, Down} | 幸存集 ℛ⁺(t)，K⁺(t) < K |
| 故障事件 | I = ⟨e₁,…,e_m⟩，e=(t,r,a)，a ∈ {Down, Rejoin} | 单故障/级联故障统一表示 |
| 策略 | Γ(class(s), Σ(t), ℛ⁺(t)) → ℛ⁺(t) | 在线选择目标副本 |
| 评估 | Inflation_c = L_c^I/L_c^base；Retention_c = G_c^I/G_c^base | 延迟膨胀、吞吐保留率 |

**关键设计约束**：会话级非迁移路由（连接建立时定目标、终生不动）——避免迁移复杂度，把问题聚焦在「新会话如何分配」上。

### 2.3 三种候选策略的张力（§II-B 核心论证）

```
策略 A：priority-agnostic 共享    → 保留共享，失去差异化（高优/尽力混杂同池）
策略 B：静态 per-class 隔离       → 保留隔离，非对称故障下滞留健康容量
策略 C：PLB 共享 + 差异化         → 共享幸存集 + 保留服务等级差异化（本文目标）
```

**第一性洞察**：非对称故障下，「隔离」与「共享」各有死穴——隔离把故障侧的损失放大（健康侧容量滞留），共享把等级差异抹平（无明确服务目标）。**PLB 要同时拿到两者的好处：共享池 + 差异化路由**。

### 2.4 repair-to-target 策略（§III，机制核心）

```
                    ┌─────────────────────────────────────────┐
                    │  Reference split (full capacity):        │
                    │  (K_P^0, K_M^0, K_F^0), K_0 = K           │
                    └──────────────────┬──────────────────────┘
                                       │  fault / rejoin events
                                       ▼
                    ┌─────────────────────────────────────────┐
                    │  Step 1: Canonicalize survivor set       │
                    │  R+ = R_P ∪ R_M ∪ R_F  (mutually excl.)  │
                    │  - replica with both classes -> Mixed    │
                    │  - borrowed states returned to roles     │
                    └──────────────────┬──────────────────────┘
                                       ▼
                    ┌─────────────────────────────────────────┐
                    │  Step 2: Compute target role vector      │
                    │  K^I(K+) = (K_P^I, K_M^I, K_F^I)         │
                    │  - boundary: K+(1)=(0,1,0), K+(2)=(1,0,1)│
                    │             K+(3)=(2,0,1)                │
                    │  - K+>=4: proportional scaling of ref    │
                    │    K~_P = max(1, round(K+ * K_P^0/K_0))  │
                    │    K~_F likewise (if K_F^0 > 0)          │
                    │  - Mixed gets residual: K_M^I = K+ - K_P^I - K_F^I
                    └──────────────────┬──────────────────────┘
                                       ▼
                    ┌─────────────────────────────────────────┐
                    │  Step 3: Repair role assignment          │
                    │  - below-target roles borrow from Mixed  │
                    │    (Mixed is the flexible role)          │
                    │  - cross P/F moves only if floor protected│
                    │  - running sessions remain pinned        │
                    └─────────────────────────────────────────┘
```

**设计原理逐条解构**：

| 机制 | 原理 | 解决的问题 |
|:-----|:-----|:-----------|
| **参考分配不变** | (K_P⁰,K_M⁰,K_F⁰) 记录原始部署平衡，不受单次故障/借用影响 | 目标随故障漂移 |
| **规范化** | 借用状态先归位，每副本恰属一类 | 修复动作可判定 |
| **比例缩放目标** | 按幸存集比例重建角色结构 | 小容量下保结构比例 |
| **边界特例** | K⁺=1→Mixed 独存（双类可访问）；K⁺=2→每类一席；K⁺=3→多的一席给 Premium | 严重级联损失下策略良定义 |
| **Mixed 收残差** | K_M^I = K⁺ − K_P^I − K_F^I | 共享池语义保留 |
| **floor 保护** | 跨 P/F 边界移动仅当角色底线受保护 | 防止降级演变为删除某类 |
| **会话钉住** | 修复只影响后续 admission | 不打断在途会话 |

### 2.5 三个设计目标（§II-D）

- **G1 保高优先**：Premium 在容量损失下保持接近故障前行为（更低延迟膨胀、更高 goodput 保留）
- **G2 避免滞留 + 适配故障形状**：非对称故障下健康副本不因「故障前属于另一类」而闲置；按 K⁺(t) 重组，含顺序故障
- **G3 低优先影响可测可控**：不隐藏 Freemium 的成本，而是通过服务级指标保持可观察、可评估其是否仍推进

### 2.6 量化结果（§IV）

| 指标 | 结果 | 对照 |
|:-----|:-----|:-----|
| Premium goodput 保留 | **+26-28 个百分点**（median）| Premium 侧故障 |
| CPU 利用率 | **+18 个百分点**（Premium-heavy 负载）| 可用副本 |
| 级联故障最严重阶段 Premium goodput | **>2×** | 共享轮询 |
| Premium p95 延迟 | **−18.2%** | 共享轮询 |
| 副本不平衡 | 基本消除 | 静态隔离 |

### 2.7 对 GPU 集群的映射（本地视角）

FT-HSDP/Concordia 处理的是「训练中断→恢复」，PLB 处理的是「恢复之前的服务等级」——对超节点集群的启示：
- **训练**：故障后降级路径 = 梯度压缩/检查点降频/关键节点保活，与恢复（重路由/重放）并行设计
- **推理**：故障后降级路径 = 服务等级感知路由（SLO 高的请求优先保活），与扩容/故障转移并行
- **原则**：降级策略要有「目标」（target），而不是「尽力而为」——目标随幸存容量变化（比例缩放），与 PLB 的 repair-to-target 同构

---

## 三、Descriptive Dispatch：执行链自身成为可量化可靠性对象

### 3.1 背景：执行链可靠性（承接 Workflow Cards）

Workflow Cards（08-12）把「执行 provenance 文档化」作为治理手段；Descriptive Dispatch 更进一步——**把「派发这个动作本身」变成可量化的可靠性测试对象**。派发（dispatch）= 接收请求 → 为 workload manager 转换 → 成功提交，是 agent 化编排的入口环节，其可靠性此前无系统度量。

### 3.2 框架：派发链与 agent 契约（§II）

```
User intent (textual) -> Secretary Agent -> workload manager (Flux) -> execution
        |                    |                      |
        |                    +-- negotiate / select / dispatch (this paper: dispatch)
        |                    +-- MCP server: discover providers, expose tools
        |                    +-- provider vocabulary: exact / descriptive /
        |                       verbatim / discovery (4 prompt styles)
```

**Agent 行为契约**（可靠性测试的观测锚点）：
- 至少 **2 次系统观测**（提交 + 查状态）——防幻觉（不观测就返回 = 幻觉信号）
- 最多 **10 次尝试**完成整个编排
- 必须用 **validation tool 检查 LAMMPS 参数**后再提交
- 返回 **submission receipt**（有效 job id + reasoning）
- 程序化核验：Flux Python SDK 验证 job 存在/状态/成功/日志

### 3.3 组合测试方法论（432 runs，核心贡献）

**5 特征维度**（manager、nocite flag、resources、application config、affinity）× **4 prompt 风格**（exact/descriptive/verbatim/discovery）= 组合矩阵 432 条 prompt。

| 风格 | 定义 | 示例（Flux）|
|:-----|:-----|:-------------|
| **Exact** | 镜像客户端语法 | `flux run` |
| **Descriptive** | 自然语言描述 | using the Flux workload manager |
| **Verbatim** | 混合（自然语言+命令名）| using `flux run` |
| **Discovery** | 故意模糊，需探索环境 | run LAMMPS |

**为什么是组合测试（原理）**：
- 每种 prompt 关联一个 ground-truth 命令（正确提交），可算 odds ratio——**哪种「意图表达方式」最不容易出错**
- nocite flag 是**无功能影响的代理标志**——专测「agent 是否忠实执行任意指令」，隔离「功能正确」与「指令遵循」
- 全组合（而非抽样）→ 可定位到「哪一维 × 哪一风格」的组合失败
- 每次实验清空 Flux 队列 + 程序化核验 job id → 结果可复现

### 3.4 多集群实验：描述性元数据的杠杆效应（§II-B/III）

| 指标 | 无元数据 | 有描述性元数据 | 增益 |
|:-----|:--------:|:-------------:|:----:|
| 成功执行率（220 jobs）| 48% | **87%** | +39pp |
| 架构不匹配 | 存在 | **消除** | — |
| 应用性能（10 个可测）| — | 5 个最高 **3.3x** | — |

**原理**：多集群异构环境下，job 转换（transformation）是主要失效率来源——目标集群的能力（架构/库/调度器）与转换后语义不匹配时，job 提交成功但执行失败。**描述性元数据 = 把「目标集群能做什么」显式传达给转换环节**，消除架构不匹配。这与 AI4AI 的「结构化信息 > 更多推理」、本地「元数据完整性是低成本高杠杆抓手」判断完全同构。

### 3.5 方法论文献价值

Descriptive Dispatch 提供了**组合式可靠性测试模板**，可复制到任何 agent 化链路：
1. 定义特征维度 × prompt 风格矩阵（全组合）
2. 每组合关联 ground-truth 结果（odds ratio 分析）
3. 行为契约（观测次数/尝试上限/验证工具/回执）
4. 程序化核验（不依赖 agent 自报）
5. 基线成功率 + 归因（哪些维度导致失败）

---

## 四、Workload Buoyancy：干扰/瓶颈诊断的通用抽象

### 4.1 背景：从专用方案到通用抽象（承接 ElastiCo）

ElastiCo（08-11）提供干扰感知编排的专用方案；buoyancy 的目标是**通用化**——不针对特定资源或工作负载，而是提供一个可扩展、可泛化的性能刻画抽象。

### 4.2 问题：启发式指标的失败模式（§I/II）

```
传统方法: CPU utilization / application-level metrics
  - CPU 利用率高 ≠ 应用性能差（应用对共享资源敏感度不同）
  - 应用级指标（如延迟）与分配资源（核/内存）不直接相关
  - 隐藏的瓶颈可能在任何共享资源: LLC / memory bandwidth / network / disk I/O
  - 硬件异构（CPU 代际差异/NUMA/缓存配置）被虚拟化掩盖
  -> 简单启发式无法捕捉 resource contention 与 noisy-neighbor 的复杂动态
```

**第一性起点**：工作负载性能永远由**一个或多个瓶颈**决定（bottleneck = limiting factor）。瓶颈可以是资源（计算/内存带宽/IO/网络）、负载、或共置干扰。**瓶颈可能随时间/负载/争用变化，且多资源可并发/相互依赖地限制性能**——所以需要「显式刻画多资源瓶颈与余量」的抽象，而非单一启发式。

### 4.3 buoyancy 抽象（§I 图 1 隐喻 + 定义）

> "The application is represented by a **ship** floating on a body of water. The goal is to keep the ship afloat (workload within its performance limits). Additional load or interference may cause the ship to **sink** (performance collapse), while adding resources **increases the buoyancy**. A ship with greater buoyancy has more margin and can withstand larger increases in load or interference."

**抽象要素映射**：

| 隐喻 | 系统概念 |
|:-----|:---------|
| 船 | 应用（workload）|
| 水面 | 共享资源容量 |
| 浪/载荷 | 负载/干扰（noisy neighbor）|
| 浮力（buoyancy）| 距性能崩溃的余量（margin/headroom）|
| 沉没 | 性能崩溃（SLO 违约）|

**定义三要素**：
1. **显式瓶颈指示**：每个共享资源上是否逼近瓶颈（bottleneck）
2. **显式余量/headroom**：每个资源上还有多少余量
3. **整合应用级指标**：资源级洞察 × 应用级性能 → 全景视图

**关键设计原则**：
- **无需先验 profiling**（without prior profiling）——通用化前提
- **可扩展**（新资源可加入）、**可泛化**（跨异构平台）
- **直观**（船浮水的隐喻，应用所有者/管理员都能理解）
- **drop-in 替代**（可替换传统启发式，不动编排系统）

### 4.4 量化结果（§VI）

| 指标 | 结果 |
|:-----|:-----|
| 瓶颈指示准确度（vs 传统启发式）| 平均 **+19.3%** |
| 部署形态 | Kubernetes 云原生原型 |
| 应用形态 | drop-in 替代常规性能指标，支持资源感知+应用感知编排 |

### 4.5 与 ElastiCo 的承接关系

```
ElastiCo (08-11):  专用方案——特定干扰模型的检测与规避
  ↓ 演进
Buoyancy (08-13):  通用抽象——「任何共享资源都可能成为瓶颈」的通用刻画
  ↓ 意义
「噪声邻居导致隐性性能故障」从「检测特定干扰」走向
「刻画任意资源上的瓶颈与余量」——诊断通用化
```

---

## 五、三条线的共性原理：可靠性治理对象的三次扩展

```
                    ┌───────────────────────────────────────────┐
                    │     Reliability governance expansion       │
                    └───────────────────────────────────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        ▼                              ▼                              ▼
 1. 故障域 → 性能域             2. 系统 → 执行链             3. 恢复 → 降级
 FT-HSDP/Concordia             Workflow Cards               FT-HSDP/Concordia
 (故障检测/恢复)                 (执行 provenance 文档化)     (恢复容量)
        │                              │                              │
        ▼                              ▼                              ▼
 Workload Buoyancy              Descriptive Dispatch         PLB
 (性能瓶颈/余量刻画)              (执行链可量化测试)          (受控降级)
 「隐性性能故障」                  「编排动作本身」              「恢复前如何服务」
```

**共性原理一：把「边界条件」变成「设计对象」**——三篇论文都在问「系统在非理想状态下如何被描述、度量、控制」：容量受损时（PLB）、执行链路出错时（Dispatch）、资源争用时（Buoyancy）。

**共性原理二：目标不是「恢复原状」，而是「当前约束下的最优」**——PLB 的目标角色向量随幸存集变化；Dispatch 用元数据让转换对齐目标集群能力（而非强求同构）；Buoyancy 显式刻画余量（而非假设资源无限）。

**共性原理三：可度量是可控的前提**——PLB 的 goodput retention/latency inflation、Dispatch 的 432 runs 成功率基线、Buoyancy 的瓶颈指示准确度，都是「先度量、后治理」。

**共性原理四：结构化信息 > 更多算力**——PLB 的 repair-to-target（结构重组而非加副本）、Dispatch 的元数据（结构对齐而非重试）、Buoyancy 的抽象（结构刻画而非堆指标）——与 AI4AI「确定性卸载 > 更多推理」、本地「约束脚本化=最高杠杆」判断同构。

---

## 六、与知识库互证

| 知识库锚点 | 互证点 |
|:-----------|:-------|
| [Cascade SLO 延迟预算](2026-08-11-cascade-slo-latency-budget-scheduling-deep-analysis.md) | PLB 的服务等级差异化降级 = Cascade 的 SLO 预算会计在故障场景的延伸；「降级可测可控」与 Cascade 六分位 JFI 同源 |
| FT-HSDP（MEMORY）| 10 万 GPU 18min 故障×10min 恢复 44%→80%——恢复路径的量化；PLB 补上恢复之前的降级路径 |
| Workflow Cards（08-12 登记）| 执行 provenance 文档化 → Dispatch 把执行链可靠性量化——「文档化」到「测试化」的演进 |
| ElastiCo（08-11 登记）| 共享 GPU 池隔离（MPS→ElastiCo→eIRWR）→ Buoyancy 通用瓶颈抽象——专用到通用的演进 |
| AI4AI 深分析（今日）| 「结构化信息 > 更多推理」在 Dispatch 元数据 48%→87% 处再次实证 |
| 本地方法论 | 「验证是唯一把可能性变确定性的操作」——Dispatch 432 runs 组合测试、PLB goodput retention、Buoyancy 19.3% 都是验证动作的规模化 |

---

## 七、批判性审视

### 7.1 三篇论文各自的局限

| 论文 | 局限 | 影响 |
|:-----|:-----|:-----|
| PLB | ①复制数据库场景（非 GPU/训练）——映射到超节点需要重新验证；②会话级非迁移路由简化了问题（迁移被排除）；③仅单故障/顺序双故障，未测任意故障模式；④评估无第三方审计 | 中——机制可迁移但量化不直接适用 |
| Dispatch | ①单 workload manager（Flux）+ 单应用（LAMMPS），泛化性未证；②48%→87% 来自 220 jobs 单实验，无跨场景复现；③agent 固定（未测不同 LLM 的派发可靠性差异）；④元数据「消除架构不匹配」的机制解释较粗 | 中——方法论价值 > 具体数值 |
| Buoyancy | ①19.3% 是「瓶颈指示」改进，非端到端 SLO 达成改进；②Kubernetes CPU 场景为主，GPU/异构加速器场景未验证；③「无需先验 profiling」的边界条件未量化（冷启动多快收敛？）；④drop-in 替代的兼容性细节有限 | 中——抽象价值清晰，落地证据偏弱 |

### 7.2 共性风险

1. **场景鸿沟**：三篇都是通用分布式系统文献（数据库/调度/云原生），**直接映射到 GPU 集群需要二次验证**——本地应保持「机制借鉴、量化重测」的态度。
2. **治理成本**：降级策略（PLB）、组合测试（Dispatch）、新抽象（Buoyancy）都引入额外复杂度——「治理的治理成本」未被讨论（防护通胀风险，本地 S 曲线判断）。
3. **单一作者/机构**：Dispatch（LLNL 两人）、Buoyancy（Umeå 四人）为小团队工作，缺乏大型系统验证。

---

## 八、可证伪预测

| # | 预测 | 可证伪条件 | 时间窗 |
|:--|:-----|:-----------|:-------|
| P1 | 超节点/GPU 集群开始出现「故障后降级路径」设计（服务等级感知路由/检查点降频），与恢复路径并列 | 若 2027 年底主流训练框架仍只有恢复路径（无降级概念）则证伪 | 2027-12 |
| P2 | 「受控降级」术语进入主流可靠性文献（至少 3 个独立工作组采用）| 若 PLB 成为孤立工作无 follow-up 则证伪 | 2027-06 |
| P3 | 执行链组合测试方法论被至少 1 个非 LLNL 机构复制（agent 派发/编排可靠性测试）| 若 432 runs 组合测试仍是唯一实例则证伪 | 2027-12 |
| P4 | 描述性元数据的杠杆效应在 GPU 作业派发场景复现（成功执行率提升 ≥20pp）| 若异构 GPU 集群中元数据收益 <10pp 则证伪 | 2027-06 |
| P5 | buoyancy 类抽象在 GPU 共享池场景落地（LLC/带宽争用刻画），替代 CPU-only 启发式 | 若 GPU 池仍用显存占用/利用率启发式且无抽象替代则证伪 | 2027-12 |

---

## 参考来源

1. arXiv:2608.11836《Enabling Differentiated QoS Degradation for Replicated Databases under Failures》（Belkis Djeffal, Pierre Bourhis, Romain Rouvoy, SPIRALS/CRIStAL, SRDS 2026, 12 Aug 2026）——[HTML 全文精读](https://arxiv.org/abs/2608.11836)
2. arXiv:2608.11524《Descriptive Dispatch of Computational Work》（Vanessa Sochat, Daniel Milroy, LLNL, 12 Aug 2026）——[HTML 全文精读](https://arxiv.org/abs/2608.11524)
3. arXiv:2602.22852v2《Workload Buoyancy: Keeping Apps Afloat by Identifying Shared Resource Bottlenecks》（Oliver Larsson, Thijs Metsch, Cristian Klein, Erik Elmroth, Umeå University, v2 replaced 12 Aug 2026）——[HTML 全文精读](https://arxiv.org/abs/2602.22852)
4. 知识库登记：`knowledge/01_survey/reliability-testing/2026-08-13.md`（三篇登记+当日趋势）

> **溯源标注**：所有量化数据均来自三篇论文原文（PLB §IV / Dispatch §II-III / Buoyancy §VI），已在对应位置标注。FT-HSDP/Concordia/Workflow Cards/ElastiCo 锚点来自知识库既有登记（reliability-testing 与 distributed-os 目录）。

---

## Changelog

- **2026-08-14 v1.0**：初版。三篇论文 HTML 全文精读 → 三条承接链（PLB→FT-HSDP/Concordia、Dispatch→Workflow Cards、Buoyancy→ElastiCo）+ 三套框架与原理（repair-to-target 三角色机制/组合测试方法论/buoyancy 船浮水抽象）+ 共性原理（治理对象三次扩展：故障域→性能域、系统→执行链、恢复→降级）+ 批判性审视 + 可证伪预测 P1-P5。
