# Agent OS：五种驯服不确定性的范式

> **概要**: Agent OS 驯服不确定性的五种范式与 ETCLOVG 七层架构 [来源: 1]
>
> **关键词**: Agent OS · 不确定性 · 范式 · 状态基石 · 架构

---

## 📑 目录

- [0x00 概要](#0x00-概要)
- [0x01 Part 1：问题空间](#0x01-part-1问题空间)
  - [1.1 不确定性的六个来源](#11-不确定性的六个来源)
  - [1.2 Agent 独有的三个问题](#12-agent-独有的三个问题)
  - [1.3 跨领域经验全景](#13-跨领域经验全景)
  - [1.4 分布式系统深度对标](#14-分布式系统深度对标)
  - [1.5 认知演进四阶段](#15-认知演进四阶段)
- [0x02 Part 2：五种范式（理论核心）](#0x02-part-2五种范式理论核心)
  - [范式一：冗余 + 投票](#范式一冗余-投票)
  - [范式二：闭环反馈](#范式二闭环反馈)
  - [范式三：约束空间](#范式三约束空间)
  - [范式四：确定性优先路由 ⭐ **最高 ROI**](#范式四确定性优先路由-最高-roi)
  - [范式五：不可逆隔离](#范式五不可逆隔离)
  - [2.2 组合策略](#22-组合策略)
- [0x03 Part 3：状态基石](#0x03-part-3状态基石)
  - [3.1 全局不变量](#31-全局不变量)
  - [3.2 系统结构：4 域 10 对象](#32-系统结构4-域-10-对象)
  - [3.3 六维世界模型](#33-六维世界模型)
  - [3.4 可验证性保证](#34-可验证性保证)
- [0x04 Part 4：ETCLOVG 七层架构](#0x04-part-4etclovg-七层架构)
  - [4.1 架构总览](#41-架构总览)
  - [4.2 E – Execution Environment](#42-e-execution-environment)
  - [4.3 T – Tool Interface & Protocol](#43-t-tool-interface-protocol)
  - [4.4 C – Context & Memory](#44-c-context-memory)
  - [4.5 L – Lifecycle & Orchestration（核心层）](#45-l-lifecycle-orchestration核心层)
  - [4.6 O – Observability](#46-o-observability)
  - [4.7 V – Verification & Evaluation](#47-v-verification-evaluation)
  - [4.8 G – Governance & Security](#48-g-governance-security)
- [0x05 Part 5：工程实践](#0x05-part-5工程实践)
  - [5.1 工程原则集（28 条精选）](#51-工程原则集28-条精选)
  - [5.2 操作化参考值](#52-操作化参考值)
- [0x06 Part 6：总结与展望](#0x06-part-6总结与展望)
  - [复杂度隐喻](#复杂度隐喻)
  - [核心结论](#核心结论)
- [🔗 与已有知识库的交叉引用](#与已有知识库的交叉引用)
- [📚 参考来源](#参考来源)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

---

## 0x00 概要

**核心论点**: Agent 面临的不确定性有 **6 个来源**，其中 **3 个**（概率性主体、窗口约束、假设腐化）在传统系统中罕见。但计算机 70 年历史已在 10 个领域积累了对抗经验——可以提炼为 **5 种可复用范式**。

> **终极公式**: Agent OS Engineering = 五种驯服不确定性范式的组合应用，在"执行者概率性 + 观测有限 + 假设腐化"约束下的特化实现

---

## 0x01 Part 1：问题空间

### 1.1 不确定性的六个来源

| # | 来源 | 性质 | 可消除？ |
|:--|:-----|:-----|:--------|
| ① | **LLM 输出概率性** | 认知不确定性 | 部分（约束/微调） |
| ② | Tool 调用可能失败 | 偶然不确定性 | 部分（重试/冗余） |
| ③ | 环境状态变化 | 外部扰动 | 不可消除 |
| ④ | **Context Window 有限** 🚩 | 观测约束 | 不可消除（物理极限） |
| ⑤ | 多 Agent 并发 | 竞争条件 | 可管理（协议） |
| ⑥ | **模型升级行为漂移** 🚩 | 平台演变 | 不可消除 |

### 1.2 Agent 独有的三个问题

| # | 独有问题 | 为什么独有 | 隐喻 |
|:--|:---------|:-----------|:-----|
| A | **概率性执行主体** | 传统程序确定性，"同样输入=同样输出" | "工人可能把图纸看对了但活干错了" |
| B | **观测窗口硬约束** | Context Window 是物理上限 | "只有 128KB 内存的数据库" |
| C | **假设腐化** | 模型升级高频+隐式+行为不可预测 | "每三个月工具手册要重印" |

### 1.3 跨领域经验全景

10 个领域 → 5 种范式映射：

| 领域 | 不确定性 | 范式 |
|:-----|:---------|:-----|
| 通信/编码 | 信道噪声 | 冗余 + 反馈 |
| 分布式系统 | 网络分区/宕机 | 冗余 + 隔离 |
| 数据库事务 | 并发竞争 | 约束 + 隔离 |
| 控制论 | 传感器噪声 | 闭环反馈 |
| 实时系统 | 调度不确定性 | 约束空间 |
| 容错计算 | 硬件故障 | 冗余 + 隔离 |
| 网络协议 | 丢包/乱序 | 反馈 + 约束 |
| 编译器优化 | 分支预测失败 | 反馈 + 隔离 |
| 蒙特卡洛方法 | 采样随机性 | 冗余 |
| 量子纠错 | 退相干 | 冗余 + 约束 |

### 1.4 分布式系统深度对标

**可直接复用（8 项）**:

- Event Sourcing → Session = append-only fact log
- Idempotency Key → Tool call dedup
- Trace ID propagation → Agent trace_id 贯穿
- Circuit Breaker → Tool 连续失败→切策略
- Sidecar Pattern → Agent 的 Sidecar
- Control/Data Plane → Brain（决策）/ Hands（执行）
- Graceful Degradation → Context 不足时降级
- Grant = Agent 版 2PC

**必须重新发明（4 项）**:

| 分布式解法 | 为什么不能直用 | Agent 替代 |
|:-----------|:---------------|:-----------|
| 确定性 Replay | 模型概率性 | Fact Log + 投影 |
| 自动 Gossip | 单向 Context Window | 主动 Retrieval |
| 固定超时重试 | 语义错误不因重试消失 | 反馈 + 换策略 |
| 静态配置 | 假设会腐化 | Feature Gate + Adaptive |

### 1.5 认知演进四阶段

| 阶段 | 时间 | 核心问题 | 焦点 |
|:-----|:-----|:---------|:-----|
| **Prompt Engineering** | 2022-2024 | 给模型什么输入？ | prompt 文本 |
| **Context Engineering** | 2025 | 模型每步看到什么？ | 上下文管理 |
| **Harness Engineering** | 2025-2026 | 整个执行环境如何工程化？ | 完整基础设施 |
| **Agent OS** | 2026- | 如何构建概率性执行者的 OS？ | 平台化治理 |

> **关键转折点**: "模型能力不再是瓶颈 → Harness/OS 成为约束瓶颈"

---

## 0x02 Part 2：五种范式（理论核心）

### 范式一：冗余 + 投票

**原理**: 多个独立副本/采样对冲个体失败

| Agent OS 应用场景 | 设计 |
|:------------------|:-----|
| LLM 输出不稳定 | Best-of-N + 确定性 Verifier 打分 |
| 单模型有盲区 | 多模型 Ensemble |
| 代码正确性 | 多 Agent 交叉 Review |
| Tool 可能失败 | 多路径尝试 + 比对 |

> **R1**: 高价值决策用确定性 Verifier（测试通过率），而非第二个 LLM 做裁判
> **R2**: 冗余上限 = Verifier 质量。无好 Verifier 时退化为浪费

### 范式二：闭环反馈

**原理**: 执行 → 观测 → 比对期望 → 修正

| Agent OS 应用 | 闭环设计 |
|:--------------|:---------|
| 任务执行 | Verify-then-Act Loop |
| Context 管理 | Kalman 式 Retrieval（预测→加载→验证） |
| 工具学习 | 失败→分析→换策略（非简单重试） |
| 成本控制 | Token Budget 实时监控 |

> **F1**: Agent 循环 = Sense-Think-Act-Verify。Verify 不可省略
> **F2**: 反馈信号必须来自外部（测试结果/环境），不能是自我评估
> **F3**: 失败后"换策略"——语义错误不因重试消失

### 范式三：约束空间

**原理**: 让错误不可能发生。缩小行为空间消除不确定性

**约束层级（Defense in Depth）**:

```text
Prompt 约束 -> 结构约束(JSON) -> 环境约束(Sandbox) -> 验证约束(E2E) -> 人确认
(可被忽略)    (中等可靠)       (高可靠)             (高可靠)        (最终)
```

> **C1**: Defense Comes Outside the Model
> **C2**: 能用 Schema 约束的，不用 Prompt。能用环境约束的，不用 Schema
> **C3**: 约束可动态调整——渐进信任

### 范式四：确定性优先路由 ⭐ **最高 ROI**

**原理**: 当确定性和概率性方案都能达成目标时，优先选确定性方案

**路径排序（INV-R）**:

```text
Rule > API > CLI > MCP > GUI > Free-form LLM
(确定性最高)                      (概率性最高)
```

**实验数据（PhoneHarness）**: CLI 成功率 ~99%，MCP ~95%，GUI ~70%——路由策略收益 > 模型能力提升收益

> **D1**: 路径按确定性排序：Rule > API > CLI > MCP > GUI > Free-form LLM
> **D2**: 路由决策不应由 LLM 做——用规则引擎
> **D3**: 每条新确定性路径 = 永久消除不确定性——Tool 建设是最高 ROI 投入

### 范式五：不可逆隔离

**原理**: 把不确定性损害限制在可回滚/可承受范围内

**不可逆度分级**:

```text
可逆 <--------------------------------------------> 不可逆
读取  写文件 发消息  API调用    支付     物理动作
(自动) (快照) (可撤？) (幂等？)  (人确)    (禁止)
```

> **I1**: 按不可逆度分级，越不可逆越需强门控
> **I2**: Agent 默认操作空间 = "完全可逆"
> **I3**: 有界委托——任何任务必须有 Step/Time/Resource Limit

### 2.2 组合策略

| 关键路径 | 范式组合 |
|:---------|:---------|
| 代码生成 | 确定性优先 + 冗余 + 反馈 |
| 不可逆操作 | 隔离 + 约束 + 反馈 |
| 长任务执行 | 反馈 + 隔离 + 约束 |
| 多 Agent 协作 | 约束 + 冗余 + 隔离 |
| Context 管理 | 反馈 + 确定性优先 |

**ROI 排序**: 确定性优先路由 > 约束空间 > 闭环反馈 > 不可逆隔离 > 冗余+投票

---

## 0x03 Part 3：状态基石

### 3.1 全局不变量

| ID | 不变量 | 含义 |
|:---|:-------|:-----|
| **INV-S** | Session = append-only fact log | 唯一事实源，记录发生了什么（facts，非 commands） |
| **INV-C** | Context Window = Session 的有损投影 | 状态估计，非完整状态 |
| **INV-D** | 约束层级: Prompt < Structure < Environment < Verification < Human | 可靠性递增 |
| **INV-R** | 路径排序: Rule > API > CLI > MCP > GUI > Free-form LLM | 确定性递减 |
| **INV-P** | progress.txt 等派生文件 = Session 的缓存，可重建 | 唯一事实源仍是 Session |

### 3.2 系统结构：4 域 10 对象

| 域 | 对象 | 作用 |
|:---|:-----|:-----|
| 执行域 | Agent / Task / Step / Artifact | 谁在做、做什么、做到哪、产出什么 |
| 能力域 | Capability / Context | 能调什么、当前上下文 |
| 治理域 | Grant / Audit | 谁授权、做了什么 |
| 记忆域 | Episode / Observation | 经验回放与多模态观察 |

**Task 9 状态机**: submitted → planning → waiting_grant → running → waiting_external → completed | failed | canceled | rolled_back

### 3.3 六维世界模型

```text
World Model
+-- 1. 环境状态 (Environment)    — 文件系统/应用状态/设备/外部服务
+-- 2. 任务状态 (Task)           — 目标树/进度/依赖/约束
+-- 3. 认知状态 (Epistemic) 🔑   — 确信区域/不确定区域/已知未知/盲区
+-- 4. 用户状态 (User)           — 意图/偏好/信任/注意力
+-- 5. 时间状态 (Temporal)       — 因果链/时间约束/变化率
+-- 6. 社会状态 (Social)         — 其他 Agent/权限/通信拓扑
```

**信念-现实漂移检测（类比 INS + GPS）**:

- INS（惯性导航）= Agent 基于历史的推断
- GPS 校正 = 主动 probing 真实环境
- INS + GPS 融合 = 世界模型的 Kalman 更新

### 3.4 可验证性保证

| ID | 保证 | 含义 |
|:---|:-----|:-----|
| P1 | Output Provenance | 每个输出附带完整证据链 |
| P2 | State Traceability | 状态变更可追溯到意图→Grant→Task→Action |
| P3 | Invariant Monitoring | 5 条 INV 运行时持续校验 |
| P4 | Decision Reproducibility | 给定 fact log 可重建决策依据 |
| P5 | External Auditability | 第三方可独立验证 |

---

## 0x04 Part 4：ETCLOVG 七层架构

### 4.1 架构总览

```text
控制平面: O: Observability | V: Verification | G: Governance
结构核心: E: Execution    | T: Tool         | C: Context | L: Lifecycle
```

**各层 × 范式矩阵**:

| 层 | 冗余 | 反馈 | 约束 | 确定性优先 | 隔离 | 主力范式 |
|:---|:----|:-----|:-----|:----------|:-----|:---------|
| E Execution | △ | △ | ★★★ | ★ | ★★ | 约束 + 隔离 |
| T Tool | ★ | ★★ | ★★★ | ★★★ | △ | **确定性优先** |
| C Context | △ | ★★★ | ★ | ★★ | △ | 闭环反馈 |
| L Lifecycle | ★★ | ★★★ | ★ | ★ | ★★ | **反馈 + 隔离** |
| O Observability | △ | ★★★ | △ | ★★ | △ | 闭环反馈 |
| V Verification | **★★★** | ★★ | ★ | △ | △ | **冗余 + 投票** |
| G Governance | △ | △ | ★★★ | ★ | ★★★ | **约束 + 隔离** |

### 4.2 E – Execution Environment

沙箱隔离 + 资源限制。端上=TEE，云端=容器/VM。
共享接口：`provision(spec) → id` / `execute(id, cmd) → result` / `destroy(id)`

### 4.3 T – Tool Interface & Protocol

统一接口：`execute(name, input) → result`
确定性优先路由（INV-R）：Rule > API > CLI > MCP > GUI > Free-form LLM
Capability Broker：注册/发现/风险标签/affordance 向量检索

### 4.4 C – Context & Memory

**Memory 四类**:

| 类型 | 寿命 | 删除 |
|:-----|:-----|:-----|
| Ephemeral Context | task 结束 | 自动 |
| Episodic Memory | 长期 | 用户主动 |
| Preference Memory | 永久 | GDPR |
| KVCache Memory | 推理周期 | LRU |

**Compaction 4 策略**: Auto / Micro / Reactive / History Snip

**Context Anxiety（窗口焦虑）**——模型接近上限时的行为漂移：

- 症状：提前收工、遗忘早期指令、决策质量下降
- 对抗：插件化压缩策略、Feature Gate 热切换、关键指令末尾锚定、利用率监控 >70%→触发压缩

### 4.5 L – Lifecycle & Orchestration（核心层）

**四层结构**:

| 层 | 变化频率 | 职责 |
|:---|:---------|:-----|
| Meta-Harness/AOC | 季度 | 编排多 Harness |
| Harness | 周/月 | 推理循环 + Context Eng + Feature Gate |
| Runtime | 年 | Session / Tool / Security / Ontology |
| Execution | 随时 | 按需创建销毁 |

**Harness 5 阶段执行流水线**:

```text
Admission -> Prepare -> Execute -> Finalize -> Persist
|           |          |          |          |
|输入校验   |装配数据源 |调用LLM   |结果校验  |写Session
|边界控制   |加载工具   |路由Tool  |证据链检查|写Audit
|Grant预检  |权限注入   |多步推进  |答案溯源  |写Trace
|预算分配   |Context组装|中间状态  |质量评估  |触发回调
^ <- <- <- <- <- <- <- <- 失败时回退到最近成功阶段重试 <- <- <- <- <- <- <- <- <- <- v
```

**Checkpoint 三种粒度**:

| 粒度 | 触发条件 | 恢复方式 |
|:-----|:---------|:---------|
| 全量快照 | 里程碑/人确认后 | 直接加载 |
| 增量快照 | 每步/每 N 步 | 全量 + apply deltas |
| 事件驱动快照 | 进入不可逆区域前 | 事务式恢复 |

**状态写入所有权**:

- Agent **永远不能直接写 Session**（只能通过 Harness 代理追加）
- World Model 更新必须有 provenance 标注
- 任何状态变更在 Session 中有对应 fact 记录

**Trace→Skill 进化闭环** ⭐:

```text
在线执行产生 Trace
       v
离线分析 (批量 Trace 聚合)
+- 高频路径 -> 沉淀为 Skill (固化路由，减少推理)
+- 失败模式 -> 策略优化 (调整路由/工具选择)
+- 小模型路由 -> 训练轻量分类器
+- 评测样本 -> 回灌自动评测 (V 层持续校准)

结果: 确定性路径覆盖率 ~30% -> 运行数月后 ~60-70% (ContextSearch 工程数据)
```

### 4.6 O – Observability

Trace 是一等评估对象，非仅调试材料。全链路 Tracing + Token 成本追踪 + Agent 健康指标 + Session 回放。

### 4.7 V – Verification & Evaluation

测试层级：Unit → API → Browser E2E → 视觉 → Trace-native → 副作用验证

**副作用验证**: 检查预期副作用是否真实发生（如文件是否存在、数据库记录是否写入），比 Agent 自评可靠。

**Feature List 模式**: JSON 枚举所有 features，只允许改 passes 字段。

### 4.8 G – Governance & Security

- **双层 Grant**: 任务级（资源边界）+ 步骤级（单次高风险）
- **Trust Domain 三圈**: A=TEE（不与 LLM 交互）/ B=Runtime / C=External
- **4 道 Prompt Injection 防线**: 输入隔离 → 输出校验 → Capability 白名单 → HITL

---

## 0x05 Part 5：工程实践

### 5.1 工程原则集（28 条精选）

**范式驱动原则（13 条）**:

- R1: 高价值决策用确定性 Verifier 做投票裁判
- R2: 冗余上限 = Verifier 质量
- F1: 执行循环 = Sense-Think-Act-Verify
- F2: 反馈信号来自 Agent 外部
- F3: 失败后换策略，非简单重试
- C1: Defense Comes Outside the Model
- C2: Schema > Prompt; 环境 > Schema
- C3: 约束可动态调整（渐进信任）
- D1: 路径排序: Rule > API > CLI > MCP > GUI > LLM
- D2: 路由决策用规则引擎，不用 LLM
- D3: 每条新确定性路径 = 永久消除不确定性
- I1: 按不可逆度分级门控
- I2: 默认操作空间 = 完全可逆
- I3: 有界委托（Step/Time/Resource Limit）

**架构原则（15 条）**:
A1: Session = 唯一事实源，append-only
A2: Harness 无 long-lived 状态
A3: Tool 接口统一 + Idempotency Key
A4: Context 不足时先跑 Feature（降级而非猜测）
A5: Session Start Protocol 验证环境健康
A6: progress.txt = Session 的派生缓存，可丢弃
A7: Harness 变更 = 系统变更，端到端测试
A8: 每个 intervention 标注移除条件（防假设腐化）
A9: Trace 是一等评估对象
A10: G 层从第一天设计
A13: Context = 状态估计 + 量化丢失
A14: 世界模型信念显式标注不确定度
A15: 信念-现实漂移主动检测

### 5.2 操作化参考值

| 原则 | 触发条件 | 默认动作 |
|:-----|:---------|:---------|
| 冗余投票 | Token 成本 > $0.05/call | Best-of-3 + Verifier |
| 不可逆门控 | 不可逆度 ≥3 (5 级制) | L3→Checkpoint, L4-5→Grant |
| 有界委托 | 默认 20 steps / 5 min / $1 | 超限暂停等 Grant |
| 换策略 | 同一路连续失败 ≥2 次 | 切换至下一级优先策略 |
| 不确定度标注 | 信念置信度 <0.7 | 标注 uncertain, 优先 probing |
| 漂移检测 | 信念年龄 >5min 或关键操作前 | 主动 probing 验证 |

---

## 0x06 Part 6：总结与展望

### 复杂度隐喻

| 系统 | 复杂度 |
|:-----|:-------|
| 传统软件 | 在可靠环境中运行确定性程序 |
| 分布式系统 | 在不可靠环境中运行确定性程序 |
| **Agent OS** | **在不可靠环境中运行概率性程序** ← 最高 |

### 核心结论

> **Agent OS 不需要发明新范式。70 年计算机历史已提供 5 种成熟范式。**
>
> Agent OS 的创新在于：
>
> 1. 在正确的位置（ETCLOVG 七层）
> 2. 以正确的组合（关键路径叠加两种以上）
> 3. 针对新约束特化（概率性 + 窗口 + 腐化）
>
> **谁先把这三件事做对，谁就掌握下一代终端的入场券。**

---

## 🔗 与已有知识库的交叉引用

| 已有内容 | 本文补充 |
|:---------|:---------|
| **Agent CLI 报告**（四产品对比） | **五种范式理论框架**——为什么 CLI > MCP > GUI 有工程依据（INV-R, D1） |
| **自进化五层 L1-L5** | **Trace→Skill 闭环**——自进化机制的 Harness 层工程实现 |
| **工具链工程化 Skill/CLI 分离** | **ETCLOVG T 层 + L 层**——从 Skill+CLI 扩展到完整七层系统架构 |
| **AI Native 竞争力（Agency）** | **概率性执行主体**——Agency 的"不等别人"在 Agent OS 中需要的结构性支撑 |
| **RAG 技术报告**（GraphRAG/Agentic RAG） | **世界模型 + Context Eng**——RAG 作为 Context Engineering 子集的定位 |
| **PKM vs RAG vs Wiki vs Memory** | **C 层 Memory 四类 + INV-C**——Context Window = 有损投影是工程化基石 |

---

## 📚 参考来源

| 内容 | 来源 |
|:-----|:-----|
| Brain/Hands/Session 解耦、Cattle 化 | Anthropic "Scaling Managed Agents" (2025) |
| Event Sourcing、Harness 腐化理论 | 知乎社区 + Claude Code 源码 |
| 双 Agent、Feature List、Session Protocol | Anthropic "Long-Running Agents" (2025) |
| ETCLOVG 分类法、Open Problems | Li et al. "Agent Harness Engineering" (2026, preprint) |
| 混合动作空间、确定性优先路由、副作用验证 | PhoneHarness (腾讯/港中文/清华, 2025, preprint) |
| Harness 5 阶段流水线、Trace→Skill 闭环 | ContextSearch (火山引擎, 2026) |
| 五种驯服不确定性范式 | 跨领域综合（通信/控制论/数据库/实时/量子） |

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- (无)

### 外部资料引用

1. 来源: [博客园 - 罗西的思考](https://www.cnblogs.com/rossiXYZ/p/20296163)

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
