# Live Tool-Call Durations 深度分析：可观测性下沉到工具调用层——agent 的"慢"首次可归因到具体工具调用

> **元信息**：Claude Code 官方 CHANGELOG（github.com/anthropics/claude-code，v2.1.7→2.1.218，2025→2026-08 持续演进）+ GitHub Copilot usage metrics API（08-07 批次）+ ARIES agentic serving 可观测性（arXiv，08-10 归档）
> **对象**：Claude Code 的 tool-call 时长度量体系——live elapsed-time counter（2.1.210）/ progress heartbeat（2.1.214）/ `duration_ms` hooks（2.1.119）/ Task metrics（2.1.30）/ MCP 超时与后台化联动（2.1.187/2.1.212）/ monotonic clock 修正（2.1.218）
> **核心主张**：可观测性从"轮次级"（turn duration："Cooked for 1m 6s"）下沉到"工具调用级"（live tool-call durations），使 agent 的"慢"**首次可归因到具体工具调用**——这是"度量制→治理制"链条（08-08 usage metrics 的度量地基）在会话内粒度的延续：先能测到单个工具调用的时长，才谈得上超时策略/后台化/自动化决策
> **关联**：[GitHub Copilot governance/ROI](2026-08-10-github-copilot-governance-roi-suite-deep-analysis.md)（usage metrics 度量地基）· [ARIES agentic serving 可观测性](2026-08-10-aries-agentic-serving-observability-deep-analysis.md) · [Claude Code IO 特征](2026-08-05-claude-code-io-characteristics-deep-analysis.md)（§2.7 会话持久化/Checkpoint IO、§2.5 Bash 同步等待）· [Claude Code 五工程](2026-08-05-five-engineering-claude-code-trae-deep-analysis.md)（Harness 工程视角）

---

## 📑 目录

- [1. 结论概要（TL;DR）](#1-结论概要tldr)
- [2. 背景与第一性原理：为什么"慢"必须可归因](#2-背景与第一性原理为什么慢必须可归因)
- [3. 演进时间线：从 turn duration 到 tool-call duration](#3-演进时间线从-turn-duration-到-tool-call-duration)
- [4. 技术框架：三层度量模型与下沉路径](#4-技术框架三层度量模型与下沉路径)
- [5. 具体实现机制（live counter/heartbeat/duration_ms/超时联动）](#5-具体实现机制live-counterheartbeatduration_ms超时联动)
- [6. 测量正确性：时钟/归属/排除语义](#6-测量正确性时钟归属排除语义)
- [7. 数据推导：度量链/阈值/收益量化](#7-数据推导度量链阈值收益量化)
- [8. 与度量地基的承接（08-08 usage metrics/ARIES/本系统实证）](#8-与度量地基的承接08-08-usage-metricsaries本系统实证)
- [9. 与知识库既有结论互证](#9-与知识库既有结论互证)
- [10. 批判性分析（局限与边界）](#10-批判性分析局限与边界)
- [11. 可证伪预判（H1-H5）](#11-可证伪预判h1-h5)
- [12. 来源与验证](#12-来源与验证)
- [Changelog](#changelog)

---

## 1. 结论概要（TL;DR）

1. **"慢"的可归因性是一次可观测性的粒度跃迁**：Claude Code 的时长度量从**轮次级**（整轮 turn："Cooked for 1m 6s"，2.1.7 起）下沉到**工具调用级**（每个 tool call 的实时计时：live elapsed-time counter，2.1.210）——用户第一次能**看见"卡"在哪一个具体工具调用上**，而不是只看到整轮花了多久。
2. **下沉路径是四层递进的**：UI 层（live counter/heartbeat，让人看见）→ Hook 层（`duration_ms` 进 PostToolUse/PostToolUseFailure，2.1.119，让程序拿到）→ 聚合层（Task tool results 的 duration metrics，2.1.30，让子任务可统计）→ 策略层（MCP >2min 自动后台化 2.1.212 / 5min idle 中止 2.1.187，让度量驱动自动化）。**度量只有进入策略层才闭环**。
3. **测量正确性是工程化的硬约束**：monotonic clock（2.1.218，系统时钟调整不再产生负时长/错时长）、归属正确性（subagent 显示自己的时长而非父 agent 的，2.1.181）、排除语义（`duration_ms` 不含 permission prompts 与 PreToolUse hooks，2.1.119）——三个修复证明"时长"不是一个简单的时间戳差值，而是一套**带边界定义的测量契约**。
4. **承接 08-08 usage metrics 的度量地基**：Copilot 把 agent 活动从"单桶"拆到"按 agent 计量"（组织级），Claude Code 把会话时长从"整轮"拆到"按工具调用计量"（会话内）——**同一"计量制→治理制"逻辑的两个粒度**。度量对象决定治理结论：组织级计量支撑许可/ROI 决策，工具级计量支撑超时/后台化/自动化决策。
5. **对本系统（CowAgent）的可操作结论**：工具调用层时长是**最可操作的优化信号**——本系统实证过"enable_thinking 串行 9.6s/次×40步"的拖慢，若当时有 tool-call duration 面板，问题一眼可见；自建 Agent 应把"每工具调用的 duration_ms + 归属（哪个 agent/子任务）+ 排除语义"作为基础遥测三件套。

---

## 2. 背景与第一性原理：为什么"慢"必须可归因

### 2.1 agent 的"慢"是复合体，不可归因则不可优化

一次 agent 任务的墙钟时间由多个成分叠加：

```text
total wall time = sum over turns of (
    model think time      (API round-trip + generation)
  + tool call time        (Bash/Read/Edit/MCP... execution)
  + permission wait       (awaiting human approval)
  + harness overhead      (hooks, compaction, cache assembly)
  + scheduling wait       (queueing behind other work)
)
```

没有工具调用级度量时，用户只能看到"这轮花了 1m 6s"（turn duration）——**五个成分混在一起，无法判断慢在哪**。第一性追问：如果不知道"慢"的构成，任何优化（换模型/加缓存/改提示词）都是盲射。

### 2.2 为什么是"工具调用"而非其他粒度

| 粒度 | 可归因性 | 可操作性 | 用户感知 | 结论 |
|:-----|:--------:|:--------:|:--------:|:----:|
| 整轮 turn | ❌（五成分混合） | 低（只能整体调） | 有（"Cooked for 1m 6s"） | 起点 |
| **工具调用 tool call** | ✅（就是执行本身） | **高（超时/后台化/重试/降级）** | **强（看到卡在哪个工具）** | **目标粒度** |
| 单系统调用 | 过细 | 低（不在 agent 控制面） | 无 | 过头 |

工具调用是 **agent 自己能观察、能干预的最小执行单元**——这正是它成为可观测性下沉目标的第一性理由。

### 2.3 与 08-08 usage metrics 的同构性

```
08-08 Copilot usage metrics (org level):  agent activity single-bucket -> split by agent
this topic (in-session):                 turn duration whole-turn -> split by tool call

common structure: split aggregate metric down to the smallest attributable unit,
                  so governance/optimization has a data foundation
```

"计量制必然催生治理制"（本地 MEMORY 判断）：组织级计量支撑 MCP 白名单/预算/许可（08-08 实证）；工具级计量支撑超时策略/后台化/自动化（本文实证）。

---

## 3. 演进时间线：从 turn duration 到 tool-call duration

| 版本 | 能力 | 层级 | 意义 |
|:-----|:-----|:----:|:-----|
| 2.1.7 | `showTurnDuration` setting（隐藏 "Cooked for 1m 6s" 消息） | 轮次 | 轮次时长成为标准显示，且**可配置** |
| 2.1.30 | Task tool results 加 token count / tool uses / **duration** metrics | 聚合 | 子任务结果携带耗时数据，**程序可读** |
| 2.1.41 | 修复 permission wait time 计入 subagent elapsed time | 正确性 | 排除语义第一次出现（等待审批≠执行时间） |
| 2.1.79 | "Show turn duration" toggle 进 `/config` menu | 轮次 | 从 env/配置升级为运行时开关 |
| 2.1.119 | PostToolUse/PostToolUseFailure hooks 输入加 **`duration_ms`**（不含 permission prompts 与 PreToolUse hooks） | **Hook** | **时长成为可编程事件负载**——下游自动化（告警/统计/重试）由此打开 |
| 2.1.139 | `/goal` 命令 overlay 显示 live elapsed/turns/tokens | 会话 | 长任务（跨轮）有实时进度面板 |
| 2.1.144 | background subagent 完成通知加 elapsed duration（"Agent completed · 3h 2m 5s"） | 聚合 | 后台任务完成时报告耗时 |
| 2.1.181 | 修复 subagent "Thinking" duration 显示父 agent 的 elapsed 而非自己的 | 正确性 | **归属正确性**（谁执行谁计时） |
| 2.1.187 | remote MCP 挂起 5 分钟自动中止（`CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT`） | 策略 | 超时策略=时长度量的第一消费方 |
| 2.1.210 | **live elapsed-time counter 加到 collapsed tool summary line** | **UI 实时** | **核心跃迁：长工具调用"看得见地在走"而非"看起来卡死"** |
| 2.1.212 | MCP 调用 >2min 自动后台化（`CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS`） | 策略 | 时长阈值驱动执行模式切换（前台→后台） |
| 2.1.214 | periodic progress heartbeat for long-running tool calls | UI 实时 | 超长调用持续心跳（配合 live counter 消除"假死"） |
| 2.1.218 | monotonic clock 修正负/错误 turn duration | 正确性 | **测量基座**：系统时钟调整不再污染时长数据 |

**演进逻辑**：显示（2.1.7）→ 程序可读（2.1.30）→ 正确性（2.1.41/181/218）→ 可编程（2.1.119）→ 实时（2.1.210/214）→ 策略闭环（2.1.187/212）。**每一层都是下一层的前提**：没有 duration_ms 就没有超时自动化；没有 monotonic clock，所有上层数据在时钟跳跃时都是错的。

---

## 4. 技术框架：三层度量模型与下沉路径

### 4.1 三层度量模型

```text
L0 turn layer (turn duration)      "Cooked for 1m 6s"          -- user-facing entry
   |
   v  drill down (to smallest intervention unit)
L1 tool-call layer (tool-call duration)
   |   - live elapsed counter (2.1.210)
   |   - progress heartbeat (2.1.214)
   |   - duration_ms in hooks (2.1.119)
   |   - MCP timeout / auto-background (2.1.187/2.1.212)
   |
   v  aggregate (subtask view)
L2 subtask layer (Task metrics)   token count + tool uses + duration (2.1.30)
   |   - background subagent completion duration (2.1.144)
   |   - /goal overlay: elapsed/turns/tokens (2.1.139)
   |
   v  foundation (measurement integrity)
L3 measurement layer
       - monotonic clock (2.1.218)
       - ownership attribution (2.1.181)
       - exclusion semantics (2.1.41/2.1.119)
```

### 4.2 四条下沉路径（度量如何变成行动）

| 路径 | 载体 | 消费者 | 闭环动作 |
|:-----|:-----|:-------|:---------|
| **UI 路径** | live counter / heartbeat | 人类用户 | 看见"卡在哪个工具"→ 手动干预（Ctrl+C/判断） |
| **Hook 路径** | `duration_ms` 进 PostToolUse/PostToolUseFailure | 开发者（hooks 脚本） | 告警/统计/重试策略/成本核算 |
| **聚合路径** | Task tool results duration / subagent completion duration | 上层编排（父 agent/用户） | 子任务耗时比较 → 任务级决策 |
| **策略路径** | MCP idle timeout / auto-background | 运行时 | 超阈值自动中止 / 自动转后台（无需人） |

**核心洞察**：四条路径中只有**策略路径**是"度量→自动行动"的完全闭环（无人介入）；其余三条仍需人或代码消费。**一个成熟的可观测性体系 = 度量可达 + 至少一条自动闭环路径**。

---

## 5. 具体实现机制（live counter/heartbeat/duration_ms/超时联动）

### 5.1 live elapsed-time counter（2.1.210）——核心跃迁

**原文**：*"Added a live elapsed-time counter to the collapsed tool summary line so long-running tool calls visibly tick instead of looking stuck."*

- **位置**：collapsed tool summary line（工具调用折叠后的摘要行）。
- **行为**：长工具调用期间，该行显示**实时递增的计时器**（每秒 tick），而非静态文案。
- **解决的问题**：此前长调用（如慢编译、挂起的 MCP 请求）在折叠视图显示静态"Running..."，用户无法区分"正在工作"与"卡死"——**静默等待的认知负担**。
- **本质**：把"工具调用是否存活"从**推断**（看输出变化）变为**直接可见**（计时器在走 = 进程活着）。

### 5.2 periodic progress heartbeat（2.1.214）

**原文**：*"Added a periodic progress heartbeat for long-running tool calls that previously went silent."*

- 与 live counter 互补：counter 显示累计时长（时间维度），heartbeat 周期性地确认"仍在执行"（活性维度）。
- **消除"假死"的双保险**：计时器走 + 心跳持续 = 确认存活；两者都停 = 可判定卡死。
- 对应本系统 MEMORY 中的教训：*"假存活陷阱——监控须看命令完成率/队列深度"*——UI 层同样要防"假存活"。

### 5.3 `duration_ms` 进 hooks（2.1.119）——可编程化

**原文**：*"Hooks: `PostToolUse` and `PostToolUseFailure` hook inputs now include `duration_ms` (tool execution time, excluding permission prompts and PreToolUse hooks)."*

- **负载结构**：每次工具调用完成后，PostToolUse/PostToolUseFailure 的 hook 输入携带 `duration_ms`。
- **排除语义**（三个"不算"）：不算 permission prompts（等待用户批准不是执行）、不算 PreToolUse hooks（harness 前置开销不是工具执行）、只算工具本体执行时间。
- **意义**：时长从"给人看的字符串"变成"给程序的结构化字段"——下游可做：超时告警、按工具类型统计耗时分布、把慢工具调用写进日志/追踪、成本核算（慢 = 占轮次 = 占 token）。
- **版本归属**：2.1.119（早于 live counter 的 2.1.210 约 3 个月）——**程序可读先于人类可见**，符合"数据先行、展示后置"的工程顺序。

### 5.4 Task tool results metrics（2.1.30）——聚合层

**原文**：*"Added token count, tool uses, and duration metrics to Task tool results."*

- Task 工具（subagent 调用）的结果里带三件套：**token count**（成本）、**tool uses**（活动量）、**duration**（耗时）。
- 这是**子任务级**的度量（L2），让父 agent/用户可以比较"哪个子任务最耗时/最烧 token"——与 08-08 usage metrics 的 `totals_by_3rd_party_agent`（按 agent 拆分的活动计数）同构：**把聚合指标按责任主体拆分**。

### 5.5 MCP 超时与后台化联动（2.1.187/2.1.212）——策略闭环

| 机制 | 阈值 | 行为 | 配置 |
|:-----|:-----|:-----|:-----|
| remote MCP idle timeout（2.1.187） | 5 分钟无响应 | 中止调用，报错而非无限阻塞 | `CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT` |
| MCP auto-background（2.1.212） | >2 分钟 | 调用自动转后台，会话保持可用 | `CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS` |

- **设计动机**：长 MCP 调用曾阻塞整个会话（用户无法同时做别的）——2.1.212 用时长阈值触发"前台→后台"模式切换；5 分钟无响应的直接中止（2.1.187）。
- **度量→策略的完整示例**：先有 duration 可测（度量）→ 发现长调用阻塞（分析）→ 设阈值自动后台化/中止（策略）。**没有度量，阈值就是拍脑袋；有了度量，阈值有数据依据。**
- 相关修复链：per-server `request_timeout_ms`（2.1.202 附近）、`MCP_TOOL_TIMEOUT` 提升 fetch timeout（2.1.147 附近）、sub-1000ms 配置被 watchdog 误杀（2.1.166 附近）——超时策略的**参数正确性**本身也在持续修复。

---

## 6. 测量正确性：时钟/归属/排除语义

### 6.1 monotonic clock（2.1.218）——测量基座

**原文**：*"Fixed rare negative or incorrect turn duration measurements after a system clock adjustment by timing turns with a monotonic clock."*

- **问题**：墙钟（wall clock）可被 NTP/用户手动调整（回拨/跳变）→ 用墙钟差算时长会得到**负数或错误值**。
- **修复**：改用**单调钟**（monotonic clock，只增不减，不受系统时钟调整影响）。
- **第一性**：时长测量必须使用单调时间源——这是所有计时系统的第一原则（与数据库事务时间戳、性能剖析器的要求一致）。

### 6.2 归属正确性（2.1.181）——谁执行谁计时

**原文**：*"Fixed subagent 'Thinking' duration showing the parent agent's elapsed time instead of the subagent's own."*

- 子 agent 的思考时长曾错误显示父 agent 的累计时间——**归属错误**。
- 修复后：每个执行主体（父/子 agent）显示**自己的** elapsed time。
- 与 2.1.41（permission wait 不计入 subagent elapsed）同属"**时长必须绑定正确的责任主体和语义边界**"。

### 6.3 排除语义（2.1.41/2.1.119）——什么算"执行时间"

| 成分 | 是否计入 `duration_ms` | 理由 |
|:-----|:----------------------:|:-----|
| 工具本体执行 | ✅ | 就是被测量的对象 |
| permission prompts（等用户批准） | ❌ | 等待用户 ≠ 工具执行；计入会污染"工具慢"的判断 |
| PreToolUse hooks（前置检查） | ❌ | harness 开销 ≠ 工具执行；计入会让 hook 慢显得工具慢 |
| PostToolUse hooks（后置处理） | 不计（2.1.119 原文只排除 permission 与 PreToolUse） | 边界定义随版本演进 |

**设计原则**：`duration_ms` 是"**工具调用自身耗时**"的纯净度量——所有等待/开销都被排除，保证"慢"归因到正确环节。这使 hook 消费者可以放心做阈值判断（如"Bash 调用 >30s 告警"），而不会被审批等待误触发。

---

## 7. 数据推导：度量链/阈值/收益量化

### 7.1 度量链的传递损失模型

设一次工具调用的真实执行时间为 t，各层传递：

```text
t_measured = t_exec + e_clock + e_attribution + e_boundary

e_clock:       wall-clock jump error (could be negative before fix; -> 0 with monotonic)
e_attribution: ownership error (subagent showed parent elapsed before fix; -> 0)
e_boundary:    boundary ambiguity (permission wait counted before fix; excluded now)

conclusion: the three fixes remove three systematic error classes, t_measured -> t_exec
```

### 7.2 策略阈值的推导依据（2.1.212 的 2 分钟从哪来）

```
design constraints:
  C1 typical MCP tool call < 2s (sub-second to seconds)
  C2 user "wait tolerance" ~ 1-3 min (beyond that, suspicion of hang)
  C3 session-blocking cost: foreground block prevents parallel work

inference: threshold T should satisfy C1 < T < C2
  take T = 2 min: covers 99%+ of normal calls (no false positives),
                  stays under user patience boundary (no hang perception)
  companion: >5 min no response -> abort (hard upper bound of C2)
```

（阈值推导为基于公开机制的合理估算，非官方口径——官方只给了默认值 2min/5min。）

### 7.3 可观测性下沉的收益量化

```
scenario: user reports "agent is slow", suspected stuck MCP call

before fix (turn duration only):
  triage path: see whole turn 1m6s -> cannot locate -> try tools one by one -> minutes to hours
  information: 1 aggregate value

after fix (live counter + duration_ms + timeout):
  triage path: collapsed line shows "stuck on MCP X for 3m" -> locate immediately
               -> trigger auto-background / abort
  information: per-tool duration + ownership + exclusion semantics + live liveness

MTTR improvement: from "whole-turn guessing" to "tool-level locating", at least 1 order of magnitude
```

### 7.4 与 Task metrics 的组合分析

```
subtask A: 12 tool calls, 3.2k tokens, 45s
subtask B: 38 tool calls, 9.1k tokens, 4m 12s   <- cost/duration hotspot

combined metrics answer: "which subtask is most expensive (token) x slowest (duration)
                          x most active (tool uses)"
-- isomorphic to usage-metrics agent split (which agent is used), granularity to subtask
```

---

## 8. 与度量地基的承接（08-08 usage metrics/ARIES/本系统实证）

### 8.1 从组织级到会话内的"计量制"延续

| 维度 | 08-08 usage metrics（Copilot） | 本主题（Claude Code tool-call duration） |
|:-----|:------------------------------|:----------------------------------------|
| 粒度 | 组织/用户 × agent | 会话 × 工具调用 |
| 拆分对象 | agent 活动单桶 → 按 agent | 轮次时长 → 按工具调用 |
| 稳定键 | `agent_id` | `duration_ms` + 工具名 + 归属 |
| 治理消费 | 许可/ROI/rollout 决策 | 超时/后台化/告警/优化 |
| 共同逻辑 | **"计量制必然催生治理制"**（本地 MEMORY 判断的两处实证） | 同左 |

### 8.2 与 ARIES 的对照：度量对象决定治理结论

ARIES 核心发现：**token 中心指标遗漏非推理瓶颈**（token 只度量模型侧，遗漏沙箱/等待/调度）。

本主题是 ARIES 结论在 CLI 会话内的镜像：
- ARIES 证明：**只看 token/推理指标，看不到沙箱挂起、上下文保留成本**——需要补"等待/执行"维度。
- 本主题证明：**只看 turn duration，看不到具体卡在哪个工具**——需要下沉到 tool-call duration。
- 共同第一性：**度量的粒度必须匹配决策的粒度**。决策是"要不要中止这个 MCP 调用"，度量就必须到这个调用。

### 8.3 与本系统（CowAgent）实证的对接

本系统 MEMORY 中的成本实证：
- *"enable_thinking 串行 9.6s/次×40步最坏 360s+"*——若当时有 tool-call duration 面板，能直接看到"每轮 thinking 9.6s"而不是靠人工推断。
- *"embedding key 无效致 282 次 batch 失败"*——工具调用级 duration + 失败计数能立即暴露"每次调用都失败"的模式。
- *"56 个 check 三套判定各异"*——check 脚本的时长/失败率若进统一度量，能支撑收敛决策。

**可操作结论**：自建 Agent（CowAgent）应把 **tool-call duration + 归属 + 结果状态** 三件套作为基础遥测；策略层（超时/重试/降级）以它为输入。

---

## 9. 与知识库既有结论互证

| 知识库结论 | 本文互证点 |
|:-----------|:-----------|
| **静默必显性化**（快速路径六准则） | live counter + heartbeat 让"卡死"显性化——静默等待不再需要用户猜测 |
| **"假存活"陷阱**（监控须看命令完成率/队列深度） | heartbeat 机制 = UI 层的"假存活"防护（计时器在走 ≠ 一定在干活，但心跳停 = 一定卡死） |
| **AI 自报收益不可靠**（仅 31% 测量，报收益的人大多不是能证明的人） | `duration_ms` 进 hooks = 让"慢"变成可验证的客观数据，而非模型自述"我花了很久" |
| **度量制→治理制**（08-08 usage metrics 实证） | 工具级时长 → 超时/后台化策略闭环 = 会话内粒度的同一逻辑 |
| **ARIES：token 中心指标遗漏非推理瓶颈** | turn duration → tool-call duration 的下沉 = CLI 版的"补非推理维度" |
| **五工程模型（Harness 工程=怎么安全地做）** | 时长度量是 Harness 的"可观测外壳"——确定性外壳的一部分（管理/隔离/回滚/度量） |
| **成本实证：enable_thinking 9.6s×40** | tool-call duration 是最直接的优化信号源（见 8.3） |
| **Claude Code IO 特征**（§2.5 Bash 同步等待/§2.7 持久化） | tool-call duration 把 IO 特征的"延迟敏感"列从定性变为可测 |

---

## 10. 批判性分析（局限与边界）

1. **"计时器在走"不等于"在有效工作"**：live counter 只证明进程活着，不证明产出在前进（死循环的 Bash 也会 tick）——heartbeat 缓解但未根除"表面活性"问题；真正需要的是**进度事件**（如每 N 输出字节心跳）而非仅时间心跳。
2. **`duration_ms` 的边界定义随版本演进**：2.1.119 只排除 permission 与 PreToolUse；PostToolUse hooks 时间是否计入未明确——hook 消费者需警惕边界漂移。
3. **策略阈值是启发式**：2min/5min 默认值缺乏公开的分布数据支撑（§7.2 为合理估算）；不同工具类型（Read vs MCP vs Bash）的最优阈值应不同，当前是全局一刀切（虽有 env 可配）。
4. **度量只在 CLI 会话内**：跨会话聚合（组织级 tool-call 时长统计）不在本功能范围——企业要从多会话中识别"哪个工具普遍慢"仍需外部遥测管道。
5. **UI 可见性有折叠/展开状态依赖**：collapsed tool summary line 才有 live counter；展开视图/print 模式（`-p`）/SDK 模式的可观测性不同（2.1.210 只提 collapsed line）。
6. **归属正确性修复的滞后**：2.1.181 之前 subagent duration 长期错误，说明"归属"这类正确性问题易被忽视——**度量正确性需要专项测试**而非顺带。
7. **MCP 超时中止的副作用**：5 分钟中止可能杀掉"慢但合法"的调用（如超大文件上传、长查询）——`idle` 语义（无响应）与 `elapsed` 语义（总时长）不同，配置需区分。
8. **对模型侧时长的不可见**：tool-call duration 覆盖工具执行，但"模型思考时长"（think time）不在此列——慢的另一个大头（API 往返+生成）仍只能靠 turn 级或外部观测。

---

## 11. 可证伪预判（H1-H5）

- **H1**：`duration_ms` 将扩展为更完整的**工具遥测结构**（含 input/output 字节数、重试次数、cache 命中标志），而非仅时长标量——若 2027-06 前未出现，说明时长已足够支撑消费方。**核验窗口**：2027-06。
- **H2**：策略阈值将从"全局 env"演进为**按工具类型/按 MCP server 的差异化阈值配置**（Read 短、Bash 中、MCP 可配）——若 2027-03 前未出现，说明一刀切被证明足够。**核验窗口**：2027-03。
- **H3**：将出现**跨会话的工具时长聚合视图**（`claude insights` 或统计面板：哪些工具最慢/最频繁/最长尾），与 `/insights` 命令（2.1.168 附近已有）合并——若 2027-06 前未出现，则 CLI 不打算做聚合层。**核验窗口**：2027-06。
- **H4**：`duration_ms` 将进入 **SessionStart/Stop 或专用遥测 hook**（会话级汇总时长），供企业管道收集——若 2027-06 前未出现，说明企业遥测依赖外部管道而非内置。**核验窗口**：2027-06。
- **H5**：live counter 将从"工具调用"扩展到"**子任务/agent 级**"（subagent 运行时折叠行也实时 tick）——若 2027-03 前未出现，说明 agent 级活性显示被判定为低价值。**核验窗口**：2027-03。

---

## 12. 来源与验证

### 参考文献与一手来源
- **Claude Code CHANGELOG**（github.com/anthropics/claude-code，raw.githubusercontent.com 抓取，v2.1.7→2.1.218，2026-08-11 验证）：全部版本锚点、功能描述、修复条目引自本文档，逐条标注版本号。
- **GitHub Copilot Changelog**（08-07 批次 usage metrics API agent app activity）：经知识库归档文档交叉引用（[GitHub Copilot governance/ROI](2026-08-10-github-copilot-governance-roi-suite-deep-analysis.md)）。

### 内部知识库（交叉验证）
- [GitHub Copilot governance/ROI suite](2026-08-10-github-copilot-governance-roi-suite-deep-analysis.md)：usage metrics 度量地基（§4）
- [ARIES agentic serving 可观测性](2026-08-10-aries-agentic-serving-observability-deep-analysis.md)：token 中心指标遗漏非推理瓶颈
- [Claude Code IO 特征](2026-08-05-claude-code-io-characteristics-deep-analysis.md)：§2.5 Bash 同步等待、§2.7 会话持久化
- [Claude Code 五工程](2026-08-05-five-engineering-claude-code-trae-deep-analysis.md)：Harness 工程框架

### 验证说明
- 所有版本锚点（2.1.7/2.1.30/2.1.41/2.1.79/2.1.119/2.1.139/2.1.144/2.1.181/2.1.187/2.1.210/2.1.212/2.1.214/2.1.218）均从 CHANGELOG 原文逐条提取，未做推断。
- §7.2 的阈值推导标注为"合理估算"（官方只给默认值未给分布数据）；79x/9.6s 等本系统数据引自 MEMORY.md 实证记录。
- MCP 超时修复链（request_timeout_ms/MCP_TOOL_TIMEOUT/sub-1000ms）的版本标注为"附近"（位于对应版本区间，精确版本以 git blame 为准）。

---

## Changelog

- 2026-08-11：初版 v1.0——CHANGELOG 一手源深度分析（三层度量模型 + 四条下沉路径 + live counter/heartbeat/duration_ms/超时联动 + 测量正确性三原则 + 承接 08-08 usage metrics 度量地基 + 8 项局限 + 5 条可证伪预判）
