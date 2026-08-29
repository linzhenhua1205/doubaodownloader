# 历史上下文污染与重复执行：机制根因与分层应对方案

> **类型**: 深度分析 | **日期**: 2026-08-14（v1.0）→ 2026-08-18（v2.0 全面升级）| **状态**: v2.0 完成 | **后续**: 落地清单见 §5
> **v2.0 升级**: 补外部一手实证（Lost in the Middle 论文数据 / Anthropic context rot 概念 / Anthropic 长任务三技术）+ 污染机制与行业研究映射 + 落地效果量化对照
> **相关**: [Token 每轮消耗源清单](2026-08-14-token-per-turn-source-inventory-sourcecode-audit.md) · [Token 优化五技术](2026-08-14-ai-pipeline-token-optimization-five-techniques-deep-analysis.md) · [Lowfreq 机制评估](2026-08-14-lowfreq-mechanism-evaluation-and-solution.md)

---

## 📑 目录 (TOC)

- [摘要](#摘要)
- [1. 现象定义（MECE 三分类）](#1-现象定义mece-三分类)
- [2. 机制根因：源码级链路](#2-机制根因源码级链路)
  - [2.1 请求组装链路](#21-请求组装链路每轮-token-从哪来)
  - [2.2 关键实证：单轮内全量重发（run.log）](#22-关键实证单轮内全量重发runlog)
  - [2.3 历史的三条进入通道](#23-历史的三条进入通道)
  - [2.4 重复执行的三个引擎](#24-重复执行的三个引擎)
  - [2.5 为什么"有时有用有时干扰"](#25-为什么有时有用有时干扰)
- [3. 外部实证：上下文污染是行业共识问题](#3-外部实证上下文污染是行业共识问题)
  - [3.1 Lost in the Middle：中段信息劣化的量化证据](#31-lost-in-the-middle中段信息劣化的量化证据)
  - [3.2 Anthropic context rot：注意力预算稀释](#32-anthropic-context-rot注意力预算稀释)
  - [3.3 Anthropic 长任务三技术与本系统五层方案映射](#33-anthropic-长任务三技术与本系统五层方案映射)
- [4. 现状参数（config.json 实测）](#4-现状参数configjson-实测)
- [5. 应对方案：五层架构](#5-应对方案五层架构)
  - [5.1 会话窗口层](#51-会话窗口层立即见效纯参数)
  - [5.2 上下文净化层](#52-上下文净化层核心system-prompt-改造)
  - [5.3 规则工程层](#53-规则工程层工程修复)
  - [5.4 记忆蒸馏层](#54-记忆蒸馏层已有机制强化方向)
  - [5.5 系统架构层](#55-系统架构层长期)
- [6. 落地清单（ROI 排序）](#6-落地清单roi-排序)
- [7. 数据与证据](#7-数据与证据)
- [Changelog](#changelog)

---

## 摘要

用户观察到的三类 AI 使用现象——**历史信息干扰当前**、**动作反复执行**、**后台回退动作重复**——不是三个独立 bug，而是同一个架构本性的三种表现：

> **LLM 无状态 + 每轮全量重发 = 历史既是记忆也是污染源**

源码审计确认（`/home/lzh/CowAgent`）：
- **每轮 API 请求 = 系统提示词(12.5K) + 全部历史消息 + 当前查询**，历史无上限累积（默认 12 turns 才裁剪）
- **单轮内每次工具调用全量重发**（run.log 实证：19→21→23→25→27 messages，每次 +2）
- **重复执行**有 3 个引擎：规则驱动（RULE.md 工作流）、定时驱动（scheduler）、循环驱动（agent loop 50 steps）
- 历史"有时有用有时干扰"是注意力稀释的必然结果：**模型无法区分"叙述"与"指令"**

应对分五层：会话窗口 → 上下文净化 → 规则工程 → 记忆蒸馏 → 系统架构。落地优先级见 §6。

**v2.0 关键增量**：行业研究（Lost in the Middle / context rot）从注意力机制层面**独立证实**了本系统的污染假设——"历史干扰"不是本系统特有 bug，而是**所有长上下文 LLM 的系统性缺陷**，Anthropic 已给出三技术（compaction / note-taking / sub-agent）与本系统五层方案逐项对应。

---

## 1. 现象定义（MECE 三分类）

| # | 现象 | 用户体感 | 本质 |
|:-:|:-----|:---------|:-----|
| P1 | 历史信息被带下来 | "干扰当前信息" | 上下文污染（信息性干扰） |
| P2 | 历史动作反复执行 | "反复执行，很讨厌" | 指令误判（动作性重复） |
| P3 | 后台回退动作重复 | "后台回退的动作都被反复重复" | 无状态引擎（后台性重复） |

三者共享同一根因链，但应对杠杆不同：
- P1 → 上下文净化（§5.2）——**信息降权**
- P2 → 任务隔离 + 动作台账（§5.2/5.3）——**指令失活**
- P3 → 规则工程 + 幂等（§5.3/5.4）——**状态补全**

---

## 2. 机制根因：源码级链路

### 2.1 请求组装链路（每轮 token 从哪来）

```
user message
  +--> AgentInitializer.create_agent()         [bridge/agent_initializer.py]
  |     +-- system_prompt = PromptBuilder.build() [agent/prompt/builder.py]
  |     |    tools(533) + skill desc(2,981) + memory rules + KB index summary(828)
  |     |    + workspace(905) + AGENT.md(779) + RULE.md(2,790) + MEMORY.md(1,390)
  |     |    + runtime + reply language
  |     |    ~ 12,462 tokens (fixed per turn)
  |     +-- history restore _restore_conversation_history()
  |          SQLite -> text messages only (tool chain stripped)
  |          restore_turns = max(3, agent_max_context_turns // 6) = 3 turns
  +--> Agent.run_stream()                       [agent/protocol/agent.py:383]
  |     messages_copy = self.messages.copy()    <- full history copy
  +--> AgentStreamExecutor loop                 [agent/protocol/agent_stream.py]
        for turn in range(max_steps=50):        <- up to 50 tool calls per turn
            api_request(system + messages + tool result)  <- full resend each time
```

### 2.2 关键实证：单轮内全量重发（run.log）

```
[18:30:37] Sending 19 messages (4 turns) to LLM   <- after 7th tool call
[18:30:44] Sending 21 messages (4 turns) to LLM   <- 8th
[18:30:50] Sending 23 messages (4 turns) to LLM   <- 9th
[18:30:56] Sending 25 messages (4 turns) to LLM   <- 10th
[18:31:01] Sending 27 messages (4 turns) to LLM   <- 11th
```

**推论**：单轮对话若有 N 次工具调用，就发 N+1 次 API 请求，每次都是 `system(12.5K) + 累积历史`。消息数线性 +2/次。这是**比跨轮历史更大的 token 黑洞**——一次深度分析任务（20 次工具调用）仅工具循环就产生 ~20 次全量重发。

### 2.3 历史的三条进入通道

| 通道 | 内容 | 注入方式 | 污染风险 |
|:----:|:-----|:---------|:--------:|
| ① 显式历史 | 旧 user 消息 + 旧 assistant 输出 | messages 数组全量重发 | 🔴 高：旧指令被当新任务 |
| ② 蒸馏注入 | 被裁剪历史的 LLM 摘要 | 注入到保留的第一条 user 消息 | 🟡 中：摘要可能带动作描述 |
| ③ 系统规则 | RULE.md/MEMORY.md 工作流指令 | system prompt 每轮注入 | 🟡 中：规则触发无条件动作 |

### 2.4 重复执行的三个引擎

| 引擎 | 源码位置 | 触发条件 | 后果 |
|:-----|:---------|:---------|:-----|
| **规则驱动** | RULE.md 工作流 4/5 | 每次"调研专题输出后"→ 自动 commit+push | 每轮归档都触发（已改 async） |
| **定时驱动** | scheduler 任务 | 每日/每周 cron 触发 | 日报/周报/专项重复生产 |
| **循环驱动** | agent_stream.py max_steps=50 | 单轮内多次工具调用 | 模型在中间步可能重复同一操作 |
| ~~自进化~~ | agent/evolution/trigger.py | idle≥10min + turns≥6 | **默认关闭**（DEFAULT_ENABLED=False），非主因 |

### 2.5 为什么"有时有用有时干扰"

注意力机制决定：**历史在长上下文中被稀释**（"lost in the middle"现象），且模型对历史消息的**指令/叙述语义无显式区分**——历史里的"git push"是报告还是命令，模型靠上下文猜测。近端强化 + 远端遗忘 → 早期结论被稀释、近期动作被放大 → 同一历史在不同场景下表现为"有用"或"干扰"。

---

## 3. 外部实证：上下文污染是行业共识问题

### 3.1 Lost in the Middle：中段信息劣化的量化证据

Stanford 研究（Liu et al., TACL 2023, arXiv:2307.03172）是上下文污染问题的**奠基性实证** [来源: arXiv:2307.03172]：

- **实验设计**：多文档问答（multi-document QA）+ 键值检索（key-value retrieval）两类任务，变换相关信息在上下文中的位置
- **核心发现**：性能在相关信息位于**开头或结尾**时最高；位于**中段**时显著下降——"U 形曲线"
- **关键推论**：即使显式长上下文模型，也无法稳健利用输入中的全部信息——**上下文越长，中段信息越容易被"淹没"**

**与本系统 P1（历史信息被带下来）的映射**：
- 本系统历史消息堆叠在 system prompt 之后、当前消息之前——**恰好处于"中段"位置**，是 Lost in the Middle 预言的"注意力盲区"
- 这从注意力机制层面解释了为什么"历史有时有用有时干扰"——**不是模型好坏问题，是位置问题**：历史信息天然处于最不利的读取位置
- **应对方向验证**：Anthropic 与本文都指向同一解——**不依赖模型自己从长历史中"捞取"信息，而是主动压缩/外部化/分区**（见 3.3）

### 3.2 Anthropic context rot：注意力预算稀释

Anthropic 在《Effective context engineering for AI agents》（2025-09-29）中正式定义了 **context rot**（上下文腐烂）[来源: Anthropic 官方博客]：

> "as the number of tokens in the context window increases, the model's ability to accurately recall information from that context decreases... Context, therefore, must be treated as a **finite resource with diminishing marginal returns**... LLMs have an **'attention budget'** that they draw on when parsing large volumes of context. Every new token introduced depletes this budget by some amount."

**与本系统的映射**：
- Anthropic 的"attention budget"（注意力预算）= 本系统"历史稀释"的同义表达
- Anthropic 的结论"上下文是有限资源，边际收益递减"= 本系统"历史无上限累积是反模式"的理论依据
- Anthropic 的架构解释（transformer 的 n² 成对注意力 + 训练分布偏短序列）为"为什么不能靠模型自己解决"提供了根因：**注意力模式从训练分布中来，长上下文天然弱于短上下文**——所以必须靠工程手段（外部化/压缩/分区）而非期待模型自适应

### 3.3 Anthropic 长任务三技术与本系统五层方案映射

Anthropic 针对长时程任务提出三技术 [来源: Anthropic Context Engineering]：

| Anthropic 技术 | 机制 | 本系统对应 | 映射结论 |
|:---------------|:-----|:-----------|:---------|
| **Compaction（压缩）** | 对话接近窗口上限时摘要重开 | 记忆蒸馏层（§5.4）Deep Dream 23:50 + 裁剪 flush | 同构：都是"有损压缩+重注入"；本系统多了人工门禁（Candidate.md）防漂移 |
| **Structured note-taking（结构化笔记）** | 定期把关键状态写盘，稍后拉回上下文（NOTES.md / to-do） | 动作台账（§5.3）+ 知识库落盘（write+log+commit） | 同构：都是"上下文外持久化+按需拉回"；本系统动作台账待实施 |
| **Sub-agent 架构** | 子 Agent 独立探索，只返回压缩摘要 | 系统架构层（§5.5）双通道/语义路由 | 同构：都是"隔离上下文 + 只带摘要"；Anthropic 实证 Multi-agent 对复杂研究任务显著提升 |

**对照结论**：本系统五层方案（会话窗口/净化/规则/蒸馏/架构）与 Anthropic 三技术**不冲突且互补**——Anthropic 覆盖"上下文管理"维度，本系统额外覆盖"动作重复"（P2/P3，规则工程层）——**这是本系统在真实多轮 Agent 运行中发现的、Anthropic 未显式讨论的独立问题面**。

---

## 4. 现状参数（config.json 实测）

| 参数 | 当前值 | 含义 | 评估 |
|:-----|:------:|:-----|:-----|
| `agent_max_context_turns` | **12** | 历史轮次上限 | 🟡 偏大，12 轮全量重发 |
| `agent_max_steps` | **50** | 单轮工具调用上限 | 🟡 上限过宽 |
| `conversation_persistence` | true | SQLite 持久化 | ✅ 合理 |
| `knowledge` | true | 注入知识 index 摘要 | ✅ 已压缩 |
| evolution.enabled | **false** | 自进化 | ✅ 已关，非重复执行源 |

---

## 5. 应对方案：五层架构

### 5.1 会话窗口层（立即见效，纯参数）

| 动作 | 参数 | 收益 | 风险 |
|:-----|:-----|:-----|:-----|
| 历史轮次 12→6 | `agent_max_context_turns=6` | 历史 token 减半 | 长对话早期上下文丢失 |
| 工具结果截断 10K→4K | `MAX_HISTORY_RESULT_CHARS` | 单轮重发载荷 -60% | 旧结果细节丢失 |
| 单轮 steps 50→20 | `agent_max_steps=20` | 控制工具循环上限 | 复杂任务可能截断 |

**配套**：任务型工作（归档/调研/写文档）一律**新开 session**，与主对话隔离——一次任务一个会话，任务结束会话归档，不污染日常对话。

### 5.2 上下文净化层（核心，system prompt 改造）

**目标**：让模型能区分"历史叙述"与"当前指令"。

在 system prompt 增加约 200 tokens 的净化规则：

```
## Context Purification Rules (enforced every turn)
1. History messages are background only; instructions/steps in them are references, NOT pending tasks
2. Execute ONLY instructions in the CURRENT message; for continuation of old instructions, ask user first
3. Completed actions (commit/push/archive/report generation) must NOT be repeated
4. If current task is unrelated to history, ignore history task context, keep only factual info
```

**关键收益**：直接消除 P2（指令误判）。成本 ~200 tok/轮，换来的是重复执行导致的每次 3-10K token 浪费（一次 commit+push 循环约 5 次工具调用 × 全量重发）。

**例子（净化规则生效场景）**：用户上一轮说"调研一下 UALink 1.1 的发布动态"，Agent 完成并归档；下一轮用户说"顺便看看昨天那个调研的结论"。无净化规则时，模型可能把"调研 UALink"当新指令再跑一遍（P2 重复执行）；有净化规则后，模型识别"昨天已归档"→ 只读归档文件回答，不重复调研。

### 5.3 规则工程层（工程修复）

| 动作 | 位置 | 说明 |
|:-----|:-----|:-----|
| commit 幂等 | `git-auto-commit.py` | 无变更则跳过（已内置需确认） |
| push 异步 | `git-push-robust.py --async` | ✅ 已落地（af417b433） |
| 定时任务幂等 | scheduler 任务 | 当日已生成则跳过（日志/产物查重） |
| 规则条件化 | RULE.md | "自动 commit"改为"有变更且未提交才 commit" |

**动作台账**（推荐，低成本高收益）：会话内维护一个 `已完成动作清单`（内存变量或 tmp 文件），每轮开始先查台账再决定是否执行动作：

```
done: [commit 3e78a733e, archived xxx.md, push async triggered]
todo: none
```

> **外部对应**：动作台账 = Anthropic "structured note-taking" 在"动作状态"维度的实例——把"已做什么"从上下文外持久化，避免重复执行 [来源: Anthropic Context Engineering]。

### 5.4 记忆蒸馏层（已有机制，强化方向）

- ✅ 已有：trim 时 flush 去重（hash 去重）、每日 Deep Dream（23:50）、MEMORY.md ≤5KB
- 强化点：**蒸馏只提炼"结论"不保留"过程动作"**——prompt 中明确"丢弃所有操作步骤描述，只保留事实/决策/结论"
- 强化点：**每日记忆按"事实/决策/动作"分栏**，动作栏可安全忽略

### 5.5 系统架构层（长期）

| 方案 | 说明 | 复杂度 |
|:-----|:-----|:------:|
| 双通道上下文 | 历史与当前任务分区，separator 强化当前 | 中 |
| 会话摘要归档 | 会话结束→生成摘要（标题+结论+产物路径），跨会话只带摘要 | 中 |
| 语义路由 | 新任务先判定相关历史（embedding 检索），只带相关片段 | 高 |
| 小模型路由 | 本地 7B 处理高频简单任务，云端处理深度分析 | 高 |

> 系统架构层的"子 Agent 干净上下文"与 Anthropic sub-agent 架构同构：**主 Agent 维护高层计划，子 Agent 用干净上下文做深度工作，只返回 1,000-2,000 token 压缩摘要** [来源: Anthropic Context Engineering / Multi-agent research system]。

---

## 6. 落地清单（ROI 排序）

| 优先级 | 动作 | 成本 | 收益 | 落地方式 |
|:------:|:-----|:----:|:----:|:---------|
| **P0-1** | system prompt 加"上下文净化规则"（§5.2） | ~200 tok/轮 | 消除 P2 重复执行（每轮省 3-10K） | 改 builder.py |
| **P0-2** | 历史轮次 12→6 + 工具结果截断 10K→4K | 参数 | 单轮历史 token 减半 | config.json |
| **P0-3** | 任务型工作新开 session 隔离 | 零 | 主对话不被任务污染 | 行为规则 |
| **P1-1** | 动作台账机制（§5.3） | 低 | 幂等防重复 | system prompt + 脚本 |
| **P1-2** | 定时任务幂等去重 | 低 | 日报/周报不重复 | scheduler 改造 |
| **P1-3** | 蒸馏 prompt 去除过程动作 | 低 | 记忆更纯净 | summarizer.py prompt |
| **P2-1** | 会话摘要归档 | 中 | 跨会话只带摘要 | 新脚本 |
| **P2-2** | 自动 compact 周期（每 8 turns 主动压缩） | 中 | 历史主动瘦身 | agent_stream.py |
| **P3** | 双通道上下文 / 语义路由 | 高 | 根治污染 | 架构改造 |

**预期效果**（P0 三项落地后）：
- 每轮固定成本：12.5K → 12.7K（+净化规则）
- 每轮历史成本：19.2K → ~6K（窗口减半 + 任务隔离）
- 重复执行浪费：≈0（净化规则 + 台账）
- **单轮总成本下降 ~50%**

**外部基准对照**：Anthropic 将 compaction 列为长任务第一杠杆（"typically serves as the first lever"）[来源: Anthropic Context Engineering]——本系统 P0-2（窗口减半）与 P2-2（主动 compact）正是 compaction 的落地形态，优先级排序与行业实践一致。

---

## 7. 数据与证据

- 源码：`/home/lzh/CowAgent/bridge/agent_initializer.py`（历史恢复）、`agent/protocol/agent.py`（run_stream）、`agent/protocol/agent_stream.py`（_trim_messages 1827 / 发送 1056 / max_steps 897）、`agent/prompt/builder.py`（system 组装）、`agent/memory/summarizer.py`（flush + Deep Dream）、`agent/evolution/trigger.py`（默认关闭）
- 实测：run.log 2026-08-14 18:30:37-18:31:01，"Sending N messages" 19→27 递增
- 外部源：Liu et al.《Lost in the Middle: How Language Models Use Long Contexts》(TACL 2023, arXiv:2307.03172)；Anthropic《Effective context engineering for AI agents》(2025-09-29)；Anthropic《Building Effective AI Agents》(2024-12-19)
- 配置：config.json `agent_max_context_turns=12, agent_max_steps=50`
- 关联：`knowledge/03_AI/methodology/2026-08-14-token-per-turn-source-inventory-sourcecode-audit.md`（token 构成审计）

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-14 | v1.0 | 初版，源码审计 + run.log 实证，五层应对方案 |
| 2026-08-18 | v2.0 | **全面升级**：补 §3 外部实证（Lost in the Middle U 形曲线与"中段盲区"映射 / Anthropic context rot 注意力预算 / 长任务三技术与五层方案映射表）+ 净化规则生效场景例子 + 动作台账与 note-taking 对应 + 落地效果外部基准对照 |
