# Rovo Long Horizon Reasoning Engine：素材补录与"五机制"方法论同源辨析

> **素材**：[Atlassian 官方博客《Long Horizon: How Atlassian Built a Reasoning Engine for Complex AI Tasks》](../06_others/sources/2026-08-11-rovo-long-horizon-reasoning-engine.md)（2026-06-17，Sean Culatana 等 8 作者）
> **日期**：2026-08-11 | **领域**：Agent 工程 / 编排范式 / 长时程 harness
> **补录动因**：该素材为知识库"五机制"方法论的**原始出处**（08-03 编排范式文档引用来源[2]），但原文从未归档；且知识库压缩表述存在**两处失真**（六项→五项合并、adaptive reasoning/observability/timeout 三维度缺失）——本次补录同时完成素材归档与方法论溯源校正
> **姊妹篇**：[Agent 编排范式深度技术分析](2026-08-03-agent-orchestration-paradigm-deep-analysis.md)（首次引入 Rovo 转向信号）· [编程 Agent 五项机制](2026-08-03-agent-composition-and-coding-agent-comparison.md)（五机制出处）· [Live Tool-Call Durations](2026-08-11-tool-call-duration-observability-deep-analysis.md)（可观测性下沉互证）

## TOC

1. [补录决策：三证据确认](#1-补录决策三证据确认)
2. [素材全景：原文六项机制完整还原](#2-素材全景原文六项机制完整还原)
3. [核心辨析：知识库"五机制"的两处失真](#3-核心辨析知识库五机制的两处失真)
4. [知识库未收录的三个维度](#4-知识库未收录的三个维度)
5. [同源同构逐项验证](#5-同源同构逐项验证)
6. [与既有知识线互证](#6-与既有知识线互证)
7. [数据推导：迭代预算与缓存经济性](#7-数据推导迭代预算与缓存经济性)
8. [批判性审视](#8-批判性审视)
9. [本系统启示](#9-本系统启示)
10. [可证伪预测 P1-P5](#10-可证伪预测-p1-p5)
11. [参考来源](#11-参考来源)

---

## 1. 补录决策：三证据确认

| # | 证据 | 结论 |
|:-:|:-----|:-----|
| E1 | 全库 grep：`rovo`/`Long Horizon`/`flattened tools` 均无 sources 归档，仅 08-03 编排范式文档参考来源[2]引用 URL | 原文素材**确认未归档** ✅ |
| E2 | MEMORY.md"五机制=flattened tools/渐进披露/context compaction（95% 水位）/child instances/分层 prompt+前缀缓存"与原文对比 | 六项机制被压缩为五项，**SKILL.md 技能化被合并** ⚠️ |
| E3 | 原文含 adaptive reasoning / observability tracing / 20min timeout 三个机制维度，知识库检索无对应条目 | **三个新维度从未收录** ⚠️ |

**结论**：素材具有补录价值——不仅是"补一个 URL 存档"，而是**方法论溯源的完整性校正**：知识库"五机制"作为被反复引用的分析结论（08-03/08-04/08-07 等 6+ 文档引用），其一手出处缺失且表述已失真，本次补录修复溯源链。

---

## 2. 素材全景：原文六项机制完整还原

原文架构核心：**one LLM, one context, one iterative loop**（最多 150 次迭代），取代 Hybrid Orchestrator 的"Coordinator + Specialists"分层路由。六项工程机制（按原文顺序）：

| # | 机制 | 原文要点 | 解决什么问题 |
|:-:|:-----|:---------|:-------------|
| 1 | **Flattened tools**（工具展平） | 每产品能力折叠为单一统一命名工具面（`jira__search_issues`），LLM 直接调用，看原始参数/响应/错误 | 消除 subagent 转述的**有损二手视图**（lossy secondhand view） |
| 2 | **SKILL.md 技能化** | 每个 namespace 附手写产品业务逻辑指南（何时用哪个工具/概念映射/recipes/gotchas） | 编码旧 subagent prompt 内隐的产品专长 |
| 3 | **Progressive disclosure**（渐进披露） | 每 namespace 折叠为 `get_tool_schema` + `invoke_tool` 两个 meta-tools，schema 按需 fetch（每工具每任务一次） | 避免数百工具 schema 每轮全付的成本与精度退化 |
| 4 | **Context compaction**（上下文压缩） | 专用 Compaction Service 每次模型调用前运行；接近 token 上限时旧输出裁剪/摘要化，**被裁输出 offload 可读回**；"95% token limit 显式驱逐" | 150 迭代的窗口压力；不丢已做推理 |
| 5 | **Child instances**（子实例分解） | 宽任务按独立研究线 spawn 自身副本（完整 one-LLM-one-context 循环），并发运行，**最慢 strand 决定响应时间**；父只收成品综合 | 宽任务单 context 超窗；**并行是副作用，动机是 context 聚焦** |
| 6 | **分层 prompt 组装 + 前缀缓存** | 按稳定度分层（static system → stable session → conversation history → turn-dependent），最长前缀 byte-identical；Anthropic 显式 `cache_control` 标记 | 150 迭代数十万 token 的重复处理成本；**成本/延迟随迭代数复利** |

**两代对比关键数据**（原文 "How it compares" 表）：

| 维度 | Hybrid Orchestrator | Long Horizon |
|:-----|:--------------------|:-------------|
| LLM calls per tool | 2（orchestrator + sub-agent） | 1（direct） |
| Iteration budget | Low single-digit | 100+（上限 150） |
| Context management | 无主动管理 | **95% token 上限显式驱逐** |
| Skills system | 无 | 14+ 预置 skills，per-tenant 覆盖 |
| Timeout | 10 分钟 | 20 分钟 |
| Quality gates | 无 | Adaptive reasoning 复杂度感知深度 |

---

## 3. 核心辨析：知识库"五机制"的两处失真

### 3.1 失真一：六项→五项，SKILL.md 技能化被合并

MEMORY.md"五机制"表述（源自 08-03 编程 Agent 对比文档 253 行）：

> "五项工程机制：flattened tools（工具展平）/ SKILL.md 技能化 / progressive disclosure（元工具按需披露）/ context compaction（95% 驱逐 + offload）/ child instances（并行子实例）/ 分层 prompt 组装 + cache_control 前缀缓存"

**注意原文列出了 6 项却自称"五项"**——这是知识库自身的一个计数错误（或有意合并）。核对原文：

- 原文将 SKILL.md 技能系统与 flattened tools / progressive disclosure 放在同一节（"Flattened tool architecture"），且 skills system 有独立章节（"The skills system"）单独展开
- 原文 skills system 的角色远超"工具描述"：它是**领域专长的独立注入通道**（sprint planning/bug triage 等 14+ 预置模板，feature-flagged、per-tenant 配置、运行时加载）——与 Rovo 自己的 SKILL.md（产品命名空间内）是**两级技能体系**：
  - **SKILL.md（namespace 级）**：产品业务逻辑，紧贴工具面
  - **Skills system（任务级）**：研究策略模板，注入 system prompt

**辨析结论**：知识库把两级技能体系压缩为一项"SKILL.md 技能化"且归入工具面机制——**低估了技能系统作为独立机制的架构地位**。正确的 MECE 切分是：

- **工具面三机制（管"怎么调"）**
  1. flattened tools（面本身）
  2. progressive disclosure（面按需披露）
  3. SKILL.md（namespace 业务逻辑：调哪个/怎么调）
- **上下文两机制（管"窗口"）**
  4. context compaction（窗口内压缩）
  5. child instances（窗口外分解）
- **经济性两机制（管"成本"）**
  6. 分层 prompt + 前缀缓存（token 复用）
  7. skills system（质量引导，间接省迭代）← 知识库缺失的独立维度

**这并非咬文嚼字**：技能系统在 Rovo 架构里承担的是"**把经验注入推理循环**"——它与 08-07 OneDayAgent 的"执行记忆压缩"、08-10 WorkBuddy 的"Context 五动作"同属 harness 层知识注入，是**独立于工具面的第二类状态**（知识型 vs 接口型）。

### 3.2 失真二："95% 水位"出处确认与语义精确化

知识库多次引用"context compaction（95% 水位）"，本次核对原文精确表述：

> "Explicit eviction at 95% token limit"（对比表）/ "When the conversation approaches the token limit, older tool outputs are trimmed or summarized while recent results are kept at full resolution. **Pruned outputs aren't discarded — they're offloaded** so the model can read them back on demand"

**精确语义**：
- 95% 是**驱逐触发水位**（approaches token limit 时的显式驱逐点），不是压缩目标水位
- 驱逐动作 = **trim（裁剪）/ summarize（摘要）+ offload（可读回）**——不是删除
- 保留策略 = **最近结果全分辨率**，旧输出降级

**辨析**：知识库"95% 水位压缩"的用法基本正确（触发阈值），但"水位"一词暗示"保持 95% 满载"的持续状态，原文语义是"**到 95% 才触发驱逐**"——这是**阈值不是水位**。精确表述应为"**95% 驱逐阈值 + offload 可读回**"。且 offload 可读回机制与知识库 [推理上下文存储](../../02_rd/01_product/00_hardware/06_storage/kv-cache/2026-06-26-inference-context-memory-storage.md) 的 KV 分层（HBM→DDR→NVMe）在**分层存储哲学**上同构：热数据全分辨率、温数据可读回、冷数据可驱逐。

---

## 4. 知识库未收录的三个维度

### 4.1 Adaptive reasoning（自适应推理深度）——最被低估的机制

原文："The model adapts its reasoning depth based on task complexity. Simple lookups get fast answers; multi-step research gets thorough reasoning."

**本质**：把**推理深度作为可动态调节的资源**，由模型每轮自校准（complexity-aware depth）。这不是 prompt 技巧，而是**推理成本控制的运行时机制**——与知识库 08-04 上下文工程"95% 压缩"的静态阈值不同，这是**按任务复杂度动态分配**的第二维控制。

**与既有知识线的关系**：
- 08-10 Harness 优化（GRPO cost-aware 访问成本）→ adaptive reasoning 是同一思想的**规则版**（模型自我判断，无训练）
- 知识库"任务形状决定范式"（窄深→单循环/宽浅→多代理）→ adaptive reasoning 是在**单循环内部**再按复杂度分级，把"宽浅/窄深"的范式选择**下沉到每轮决策**——这是知识库没有覆盖的新粒度

### 4.2 Observability（轨迹级可观测性）——与 08-11 tool-call duration 的直接互证

原文："structured LLM tracing — capturing every orchestrator decision, tool invocation, latency breakdown, and token cost as a hierarchical trace tree... **debug a 40-step research task the same way you'd debug a distributed microservice call — except the 'services' are LLM reasoning steps and the 'RPCs' are tool calls**"

**辨析**：这条与 [Live Tool-Call Durations 分析](2026-08-11-tool-call-duration-observability-deep-analysis.md) 是**同一趋势的两端**：
- Claude Code（08-11）：时长度量下沉到工具调用层（L0 轮次→L1 工具调用）
- Rovo（06-17）：全轨迹 trace tree（决策+调用+延迟+成本）

**Rovo 提供而 Claude Code 分析未覆盖的增量**：
1. **分层 trace tree**（hierarchical）：orchestrator span → 每迭代 → 每工具调用，可下钻
2. **归因维度更全**：除时长外含 token cost、错误工具选择、静默失败、重试烧预算、context 压力累积
3. **调试范式类比**：分布式微服务调试法（services=推理步骤，RPCs=工具调用）——这是知识库"假存活陷阱/静默必显性化"的**工程化落地**

### 4.3 Timeout 与迭代预算的量化边界

| 维度 | 旧架构 | Long Horizon | 变化 |
|:-----|:------:|:------------:|:----:|
| Iteration budget | 2-5 步 | 100+（上限 150） | **30-75×** |
| Timeout | 10 min | 20 min | 2× |

**辨析**：这是知识库"迭代预算即失败恢复预算"论断的**一手量化支撑**（08-03 已引用"150 次迭代"结论，但未归档原始 timeout/迭代数据）。且 timeout 2× 与迭代预算 30-75× 的**不对称**揭示：timeout 是按用户耐心（20 min 上限）而非按迭代数设定——**用户耐心是硬约束，迭代数是软预算**。

---

## 5. 同源同构逐项验证

知识库"五机制"与 Rovo 原文的逐项溯源（确认同源同构，无第三来源引入的失真）：

| 知识库机制 | Rovo 原文对应 | 同构度 | 验证结论 |
|:----------|:-------------|:------:|:---------|
| flattened tools | "Filter and flatten sub-agent tools into individual top-level actions" | ✅ 完全同构 | 原文直接出处 |
| 渐进披露 | "progressive disclosure — exposing that surface to the model on demand"（meta-tools） | ✅ 完全同构 | 原文直接出处 |
| context compaction（95% 水位） | "Explicit eviction at 95% token limit" + offload | ✅ 同构（语义需精确化） | 阈值 vs 水位用词校正 |
| child instances | "spawns a child instance of itself for each strand" | ✅ 完全同构 | 原文直接出处 |
| 分层 prompt + 前缀缓存 | "layers ordered from most stable to most volatile" + cache_control | ✅ 完全同构 | 原文直接出处 |
| SKILL.md 技能化 | SKILL.md（namespace 级）+ Skills system（任务级） | ⚠️ 部分同构 | **两级体系被压缩为一级** |

**结论**：知识库"五机制"与 Rovo 原文**同源**（直接提炼，无转述失真）+ **同构**（术语/机制一一对应）。唯一失真在 SKILL.md 技能化的合并处理（§3.1）与"水位"用词（§3.2）。

---

## 6. 与既有知识线互证

| 知识线 | 互证内容 |
|:-------|:---------|
| 08-03 编排范式：路由式多代理的失效 = 有损转译中介 | 原文 "made downstream decisions on a lossy, secondhand view of its own work" **直接印证**——本文档为其提供一手原文引用 |
| 08-03：两家收敛于"单一协调上下文 + 按需并行" | 原文 child instances "Parallelism is a side effect; the primary motivation is keeping each context focused" **精确印证**——并行是副作用而非目的 |
| 08-04 上下文工程：95% 压缩 + check 纠偏 | 原文 compaction 95% 阈值 + offload——**同构但语义精确化**（阈值非水位） |
| 08-07 OneDayAgent：执行记忆压缩 | 原文 Context Compaction Service 是同一机制的生产版 |
| 08-10 WorkBuddy：Context 五动作/渐进式加载 | 原文 progressive disclosure 是其原生产品出处（WorkBuddy 五动作包含渐进式加载） |
| 08-11 tool-call duration：可观测性下沉 | 原文轨迹级 trace tree 是**同趋势的更完整实现**（§4.2） |
| 08-05 五工程：Harness 即适配层 | 原文 "multi-agent design wasn't an accident — it was a workaround"——**harness 演进被模型能力驱动**，与"可靠性由 harness 承担，模型可换"完全一致 |
| 本系统技能库：Skill 负责编排判断，CLI 稳定交付 | 原文 SKILL.md（业务逻辑）+ meta-tools（稳定调用面）——**知识库 60+ 技能正是 Long Horizon 式编排的输入资产**（08-03 已述，此处确认到原文） |

---

## 7. 数据推导：迭代预算与缓存经济性

### 7.1 迭代预算的"失败恢复预算"解释

知识库 08-03 断言"迭代预算即失败恢复预算"（第一性原理：复杂任务成功率 = 可尝试次数函数）。用原文数据量化：

设单步成功率 p，任务需 N 步成功：

- P(整体成功) = p^N（无恢复）
- P(150 迭代内成功) = 1 − (1 − p^N)^(150/N 次机会)

取 p=0.9, N=10：

- 无恢复: 0.9^10 ≈ 0.35
- 150 迭代（15 次机会）: 1 − (1−0.35)^15 ≈ 1 − 0.65^15 ≈ 0.994
- **→ 迭代预算把 35% 成功率提升到 99.4%（+64pp）**

**结论**：150 迭代预算不是"更长"的奢侈，是**把指数失败率转为可控成功率的数学必然**——这是 Rovo 从 2-5 步跳到 100+ 的第一性理由（标注：p/N 为合理估算，原文未给单步成功率）。

### 7.2 前缀缓存的成本复利模型

每迭代处理量 = 全量 prompt（稳定前缀 + 增量）：

- 无缓存: 150 迭代 × 全量 token
- 有缓存: 150 迭代 × 增量 token（工具结果 + 推理）

设稳定前缀占 80% 的 token 量：

- 缓存收益 = 150 × 80% = 120 次迭代的全量处理被省
- **→ 收益与迭代数线性正比，任务越长回报越大**（原文 "compounds with the number of iterations" 的数学形式）

**辨析**：这与知识库 08-10 "Prefix Caching 使 system prompt 稳定性转化为推理成本"完全互证——Rovo 的分层组装是**工程化保证前缀稳定性**（byte-identical），不是依赖模型侧缓存命中率。

---

## 8. 批判性审视

1. **自报数据无第三方复现**：+8.5%/+0.83%/+23% 均为内部 LLM judge 评测；77% vs 71% 含 "plus model updates"——**架构与模型升级的贡献未分离**，归因可信度受限
2. **"perceived latency -37%" 是感知非真实**：TTFB 实际略升（原文承认），-37% 是流式进度条的心理效果——**度量口径：主观感知 ≠ 客观延迟**，引用时须标注
3. **child instances 与"单一循环"叙事张力**：宣称 one-LLM-one-context 的架构在宽任务下实际是 N context 并行——原文诚实区分（"并行是副作用"），但**架构命名（Long Horizon 单数）与实现（多实例复数）不一致**，引用时须区分"默认单循环 + 宽任务降级为多实例"
4. **150 迭代上限与 20 min timeout 的冲突**：150 迭代 × 单次 LLM 调用 2-8s = 300-1200s，**超过 20 min timeout**——实际 150 迭代需要每轮 <8s 或并行加速，否则不可达；原文未给迭代时长的分布数据
5. **skills system 的维护成本未披露**：14+ 预置 skills 由谁维护、如何随产品演进更新、per-tenant 覆盖的复杂度——原文只给了收益未给成本
6. **"模型超越了盒子"的时间依赖**：原文承认多代理是 workaround，但**这是 2026 年模型能力下的判断**——若未来模型上下文继续扩大，child instances 的触发阈值会继续上移，"宽任务"定义漂移

---

## 9. 本系统启示

1. **技能库定位校正**：本系统 60+ 技能（文献调研/数据工程/论文写作/知识管理）正是 Rovo "skills system" 的对应物——**技能 = 经验注入通道，独立于工具面**。知识库"五机制"压缩合并的教训：技能系统应作为**独立架构维度**管理（本系统 skills/ 目录已是独立层级 ✅）
2. **分层 prompt 工程化**：本系统 system prompt 118K→18K 的压缩已验证前缀稳定性价值；Rovo 的分层组装（static→stable→history→turn）可作为**自建 Agent 的 prompt 分层规范**：稳定层保证 byte-identical 前缀，适配缓存
3. **95% 驱逐阈值的落地**：本系统 08-04 上下文工程已有"95% 水位压缩"，本次精确化语义（阈值非水位）+ offload 可读回——**驱逐≠删除**，可考虑对本系统会话状态做"压缩 + 可读回"双态
4. **轨迹级可观测性**：Rovo 的 trace tree（决策+调用+延迟+成本分层）是 [tool-call duration 分析](2026-08-11-tool-call-duration-observability-deep-analysis.md) 本系统启示的**增强版**——自建 Agent 遥测应含归因维度（错误工具/静默失败/重试烧预算），而非仅时长
5. **迭代预算即失败恢复预算**（§7.1）：自建 Agent 的 max_steps（本系统 200→40）应基于**任务单步成功率**而非经验值——若单步 p=0.9、任务需 10 步，40 步预算提供 4 次机会（成功率 1-0.65⁴≈82%）

---

## 10. 可证伪预测 P1-P5

| # | 预测 | 核验窗口 | 可证伪条件 |
|:-:|:-----|:---------|:-----------|
| P1 | Rovo Long-running tasks（路线图 1）落地后，child instances 将升级为**可恢复的持久任务单元**（checkpoint + 断线续跑），"宽任务"从同步并行转向异步编排 | 2027-06 | 2027-06 时 Rovo 任务仍为同步轮次、无 checkpoint |
| P2 | Adaptive reasoning 将显式化为**复杂度评估器 + 推理预算分配**（而非模型内隐判断），简单查询走捷径路由 | 2027-06 | 简单查询仍全走完整推理循环且无复杂度分级证据 |
| P3 | 轨迹级可观测性（trace tree）将成为**长时程 Agent 平台的标配**，与 tool-call duration 合并为统一遥测标准 | 2027-12 | 主流 agent 平台无轨迹级 trace、仅轮次级日志 |
| P4 | SKILL.md 两级体系（namespace 级 + 任务级）将在 Rovo 文档中显式化命名，或合并为统一 skill 注册表 | 2027-06 | Rovo 文档仍混用 SKILL.md 与 skills system 且无区分 |
| P5 | 150 迭代 × 20 min timeout 的约束将推动**迭代时长监控**成为标配（每轮 LLM 调用时长告警），否则 150 迭代不可达 | 2027-06 | 无迭代时长监控且 150 迭代任务实际可完成（反驳约束存在） |

---

## 11. 参考来源

1. [Atlassian: Long Horizon: How Atlassian Built a Reasoning Engine for Complex AI Tasks](../06_others/sources/2026-08-11-rovo-long-horizon-reasoning-engine.md)（2026-06-17，一手全文）
2. Atlassian: [Meet the new Rovo Chat: One prompt, multiple steps, zero hand-holding](https://www.atlassian.com/blog/rovo/long-horizon-whats-changed)（2026-07-28）
3. 知识库：[Agent 编排范式深度技术分析](2026-08-03-agent-orchestration-paradigm-deep-analysis.md)（首次引入 Rovo 转向信号）
4. 知识库：[编程 Agent 五项机制](2026-08-03-agent-composition-and-coding-agent-comparison.md)（五机制出处，253 行）
5. 知识库：[Live Tool-Call Durations](2026-08-11-tool-call-duration-observability-deep-analysis.md)（可观测性下沉互证）
6. 知识库：[OneDayAgent 长时程 Harness](2026-08-07-onedayagent-long-horizon-harness-deep-analysis.md)（context compaction 互证）

---

## Changelog

- 2026-08-11: 创建 v1.0。素材补录（Atlassian 官方博客一手全文）+ 五机制方法论溯源校正（六项→五项压缩失真、两级技能体系、95% 阈值语义精确化）+ 三新维度收录（adaptive reasoning / 轨迹级 observability / timeout 迭代边界）+ 数据推导（迭代预算=失败恢复预算、前缀缓存复利模型）+ 5 条可证伪预测。
