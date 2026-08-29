# AI Agent 上下文管理：message 组装、加载时机与 Token 经济学（Claude Code / Trae / DeepSeek Harness / CowAgent 对比）

> **日期**: 2026-08-18 | **分类**: 03_AI/agent-engineering | **专题编号**: AGT-ENG-2026-08
> **一句话**: 七大上下文来源（rule/spec/memory/skills/对话历史/导入文本/用户提示词）在提交给 LLM 的 message 中遵循**三条时序定律**——常驻注入（upfront）、按需检索（JIT）、事后记忆（persist）；四大 Agent 的差异本质不是"有什么来源"，而是**在每个来源上选择哪条时序路径 + 缓存经济学（前缀静态化）**；抛弃上下文的正确姿势是"蒸馏而非删除"（flush 到记忆 + 注入摘要，保真度递增谱系）。
> **来源**: Anthropic 官方《Effective context engineering for AI agents》(2025-09-29, 网页抓取) + Claude Code/Trae 官方文档（2026-08 快照）+ DeepSeek Harness 技术框架分析（2026-08-13）+ CowAgent 源码实证（/home/lzh/CowAgent, 2026-08-18）+ 知识库既有 6 篇专题
> **关联**: [五工程 × 双产品](2026-08-05-five-engineering-claude-code-trae-deep-analysis.md)（本文是其"上下文工程"维度的四产品深化）· [上下文污染与重复执行](../methodology/2026-08-14-context-pollution-repeat-execution-analysis.md)（本文是"何时导入/抛弃"的正向设计视角）· [DeepSeek Harness 技术框架](2026-08-13-deepseek-harness-technical-framework-analysis.md) · [Agent 退化模式](2026-08-17-agent-degeneration-modes-harness-architecture-deep-analysis.md) · [Token 优化五技术](../methodology/2026-08-14-ai-pipeline-token-optimization-five-techniques-deep-analysis.md) · [**CowAgent System Prompt Token 拆解审计**](2026-08-18-cowagent-system-prompt-token-audit.md)（本文"cowagent 实证"维度的量化深化：20,623 tok/轮实测 + 优化收益测算）

---

## 📑 目录

- [1. 结论概要（TL;DR）](#1-结论概要tldr)
- [2. 第一性框架：上下文是稀缺资源，时序是核心变量](#2-第一性框架上下文是稀缺资源时序是核心变量)
  - [2.1 七大上下文来源的物理属性分类](#21-七大上下文来源的物理属性分类)
  - [2.2 三条时序定律：upfront / JIT / persist](#22-三条时序定律upfront--jit--persist)
  - [2.3 注意力预算：为什么"全量注入"必然失败](#23-注意力预算为什么全量注入必然失败)
- [3. 四大 Agent 的 message 组装机制](#3-四大-agent-的-message-组装机制)
  - [3.1 Claude Code：混合模型（upfront 规则 + JIT 工具 + compaction）](#31-claude-code混合模型upfront-规则--jit-工具--compaction)
  - [3.2 Trae：规则全量 + 技能按需 + 记忆文件自动维护](#32-trae规则全量--技能按需--记忆文件自动维护)
  - [3.3 DeepSeek Harness：阈值压缩 + 检索注入 + KV Cache 复用](#33-deepseek-harness阈值压缩--检索注入--kv-cache-复用)
  - [3.4 CowAgent：八节 system prompt + 按需注入 + trim-flush-摘要](#34-cowagent八节-system-prompt--按需注入--trim-flush-摘要)
  - [3.5 四 Agent 对比矩阵](#35-四-agent-对比矩阵)
- [4. 什么时候导入：加载时机决策框架](#4-什么时候导入加载时机决策框架)
  - [4.1 时机决策的四个层级](#41-时机决策的四个层级)
  - [4.2 缓存经济学：前缀静态化是成本胜负手](#42-缓存经济学前缀静态化是成本胜负手)
  - [4.3 导入的三种形态与保真度](#43-导入的三种形态与保真度)
- [5. 什么时候抛弃：蒸馏而非删除](#5-什么时候抛弃蒸馏而非删除)
  - [5.1 抛弃的四个触发条件](#51-抛弃的四个触发条件)
  - [5.2 抛弃方式谱系：截断 → 裁剪 → 压缩 → 蒸馏](#52-抛弃方式谱系截断--裁剪--压缩--蒸馏)
  - [5.3 抛弃的保真度红线：四类信息不可丢](#53-抛弃的保真度红线四类信息不可丢)
- [6. Session 绑定：上下文生命周期的容器](#6-session-绑定上下文生命周期的容器)
  - [6.1 session × 上下文的生命周期矩阵](#61-session--上下文的生命周期矩阵)
  - [6.2 长驻 session 的上下文膨胀（feishu 实证）](#62-长驻-session-的上下文膨胀feishu-实证)
  - [6.3 会话级隔离：深度分析独立上下文模式](#63-会话级隔离深度分析独立上下文模式)
- [7. 对自建 Agent 的落地清单（cowagent 视角）](#7-对自建-agent-的落地清单cowagent-视角)
- [8. 来源与验证](#8-来源与验证)
- [变更记录](#变更记录)

---

## 1. 结论概要（TL;DR）

1. **七大上下文来源不是平等的**：按"变化频率 × 稳定性 × 作用域"可分为**静态基座**（rule/spec：会话级不变）、**半静态索引**（memory 索引/skills 元数据：请求级微变）、**动态载荷**（对话历史/导入文本/用户提示词/工具结果：每轮都变）。动态载荷是注意力预算的主要消耗者，也是 token 管理的主战场 [来源: 本文 2.1 分析]。

2. **四大 Agent 的 message 组装差异 = 每条时序路径的选择差异**：Claude Code 与 CowAgent 走"**静态常驻 + 动态按需**"（CLAUDE.md/AGENT.md upfront，工具与文件 JIT 检索）；Trae 走"**规则全量 + 技能按需**"（官方明示 token 策略）；DeepSeek Harness 走"**阈值压缩 + 动态检索注入**"。没有一家把 skills 全文/知识库全文塞进 system prompt——**全部采用"元数据常驻 + 全文 JIT"**，这是行业收敛出的共识 [来源: 3.x 各节]。

3. **"什么时候导入"的第一性答案是缓存经济学**：DeepSeek V4 缓存命中 0.02 元 vs 未命中 1 元/百万 token（50 倍差）；本库实测 27 天 2.3B tokens，缓存未命中 58% 是最大成本项 [来源: 4.2]。因此**静态内容必须放最前且顺序稳定**（最长公共前缀命中），动态内容放后面——Prompt 前 4 层静态化是缓存命中率最大化的经验法则 [来源: DeepSeek Harness 分析 §4.2]。

4. **"什么时候抛弃"的正确姿势是蒸馏而非删除**：抛弃谱系 = 截断（工具结果裁剪）→ 裁剪（完整轮次移除）→ 压缩（LLM 摘要）→ 蒸馏（记忆化+索引化），保真度递增、成本递增。四大 Agent 的共同设计是**抛弃前先沉淀**：Claude Code compaction 保留架构决策/未解 bug/实现细节 + 最近 5 个文件；DeepSeek Harness 摘要必须保留**用户诉求/已完成操作/共识/待办**四类信息；CowAgent trim 时 flush_memory + 注入上下文摘要 [来源: 5.2/5.3]。

5. **session 是上下文生命周期的容器，但不是上限**：长驻 session（feishu 实证 141+ messages / 170K tokens）若不主动重置，上下文在超限边缘启动、有效注意力被稀释、质量劣化 [来源: 6.2]。2026-08-17 CowAgent 的修复（"深度分析"前缀 → 独立上下文，旧历史 flush 不丢）验证了**"上下文随任务边界重置 + 信息随记忆持久化"**是可落地的会话级隔离模式 [来源: 6.3]。

---

## 2. 第一性框架：上下文是稀缺资源，时序是核心变量

### 2.1 七大上下文来源的物理属性分类

用户列出的七类输入（rule、spec、memory、skills、对话上下文、导入文本、用户提示词）可归并到三个物理层级：

| 层级 | 来源 | 变化频率 | 稳定性 | 典型规模 | 加载策略 |
|:-----|:-----|:--------|:-------|:---------|:---------|
| **L1 静态基座** | rule（AGENT/USER/RULE.md） | 会话级不变 | 高 | 3-15 KB | **upfront 常驻** |
| **L1 静态基座** | spec（项目规格/约束） | 任务级不变 | 高 | 1-50 KB | upfront 或 @import |
| **L2 半静态索引** | memory（MEMORY.md 索引） | 请求级微变 | 中 | 1-10 KB | upfront（索引）+ 检索（正文） |
| **L2 半静态索引** | skills（SKILL.md 元数据） | 安装时变 | 中 | 5-20 KB（仅元数据） | **upfront 元数据 + JIT 全文** |
| **L3 动态载荷** | 对话上下文（历史消息） | 每轮变 | 低 | 10-200 KB+ | 裁剪/压缩 |
| **L3 动态载荷** | 导入的文本（文件/网页/工具结果） | 每次变 | 低 | 单次 1-100 KB | **JIT 按需** |
| **L3 动态载荷** | 用户提示词（当前消息） | 每轮变 | 低 | 0.1-5 KB | 必载（不可压缩） |

> **关键洞察**：L1 是"身份与契约"，L2 是"索引与目录"，L3 是"工作负载"。Token 管理的本质是**把 L3 的膨胀压力向 L2 转移**（对话历史→记忆索引、工具结果→摘要），而不是消灭 L3。

### 2.2 三条时序定律：upfront / JIT / persist

```text
                +--------------------------------------------+
                |          message assembly timeline         |
                +--------------------------------------------+
  UPFRONT (resident)   JIT (on-demand)          PERSIST (aftermath)
  -----------------    --------------           -----------------
  - every turn loaded  - loaded when needed     - distill before drop
  - rule / spec        - file body / tool result- dialog history -> memory
  - memory index       - skills full text       - tool result -> summary
  - skills metadata    - KB retrieval snippets  - session end -> distill
  - tool schemas       - history summary        - survive across sessions
  cost: fixed prefix   cost: one extra lookup   cost: async + one write
  gain: cache hit      gain: pay only needed    gain: drop without loss
```

- **upfront**：静态/半静态内容，每轮必带。优点是前缀稳定 → 缓存命中率高；缺点是常驻成本（本系统实测 system prompt 12.5K tokens/轮 [来源: context-pollution 分析 §2.1]）。
- **JIT**：动态内容，用多少取多少。缺点是每次检索有失败/延迟风险；优点是不为"可能用到"付费——Anthropic 明确推荐 Claude Code 的混合模式：**CLAUDE.md 前向加载 + glob/grep 即时检索文件**，规避了 stale indexing 问题 [来源: Anthropic context engineering 官方博客]。
- **persist**：抛弃前的保底动作，把"上下文"转成"记忆"（跨会话资产）。这是"何时抛弃"问题的另一半答案——**抛弃必须是可逆的**。

### 2.3 注意力预算：为什么"全量注入"必然失败

Anthropic 官方给出的第一性解释：Transformer 的注意力是 n² 成对关系，上下文越长，模型捕捉关键关系的能力越被稀释——即"attention budget"（注意力预算）稀缺 [来源: Anthropic context engineering 官方博客]。配合两项实证：

- **Lost in the Middle**：长上下文中段信息的召回率显著劣于首尾（本库 context-pollution 分析 v2.0 §3.1 引用）[来源: Liu et al. 2023, 转引自知识库分析]。
- **context rot**：Anthropic 提出的概念——上下文越长，关键信息被无关信息淹没导致指令漂移的概率越高 [来源: context-pollution 分析 v2.0 §3.2]。

> **推论**：上下文管理的目标不是"塞得下"，而是"**在注意力预算内，最大化关键信息的信噪比**"。这直接决定了"什么时候导入/抛弃"的判据——不是窗口余量，而是**边际信息价值**。

---

## 3. 四大 Agent 的 message 组装机制

### 3.1 Claude Code：混合模型（upfront 规则 + JIT 工具 + compaction）

**message 组装结构**（每轮请求 = system prompt + 全量历史 + 当前消息 + 工具 schema）：

| 来源 | 加载路径 | 机制细节 |
|:-----|:---------|:---------|
| rule（CLAUDE.md 三层） | **upfront 全量** | Enterprise Policy（强制）/ `~/.claude/CLAUDE.md`（用户级）/ 项目根 CLAUDE.md；`@import` 拆分子文件按需组装，避免单文件膨胀 |
| spec | @import 或 @-mention | 大规格文档不常驻，`@file.md` 按需引用 |
| memory | 工具化（/memory）+ CLAUDE.md | 长期记忆与指令分离；记忆正文 JIT 读取 |
| skills | **元数据 upfront + 全文 JIT** | SKILL.md 描述常驻，全文由 read 工具按需读取 |
| 对话上下文 | 裁剪 + compaction | 详见下 |
| 导入文本 | @-mention 引用 | 文件/符号级按需读入，不全量塞入 |
| 用户提示词 | 必载 | 不可压缩 |

**上下文管理的三层压缩策略**（Anthropic 官方描述 + 知识库五工程分析 §4.2 归纳）：

1. **工具结果清理（tool result clearing）**：最轻量压缩——历史深处的工具调用与原始结果直接清除。Anthropic 称之为"最安全、最轻触的压缩形式"，已作为官方 feature 推出 [来源: Anthropic 官方博客]。
2. **轮次裁剪**：以"完整轮"为单位裁掉最早一半（保证工具入参与结果成对），每轮只留首条提问+末条回复；溢出兜底时总结后激进截断 [来源: 五工程分析 §4.2]。
3. **compaction（压缩）**：上下文接近窗口上限时，把 message history 交给模型总结——**保留架构决策、未解决 bug、实现细节，丢弃冗余工具输出**；压缩后继续 + **最近访问的 5 个文件**保证连续性 [来源: Anthropic 官方博客]。
4. **Prompt Caching**：前缀缓存 + cache_control 标记，相同前缀多次推理只算增量 token [来源: 五工程分析 §4.2]。

> **设计哲学**：Claude Code 是"**混合检索**"的官方样板——静态规则 naive 前向注入（upfront），文件与环境信息交给 glob/grep 即时检索（JIT），压缩兜底（compaction）。Anthropic 明确表示这是对"预计算索引"路线的否决：JIT 规避了 stale indexing 和复杂语法树的维护成本 [来源: Anthropic 官方博客]。

### 3.2 Trae：规则全量 + 技能按需 + 记忆文件自动维护

| 来源 | 加载路径 | 机制细节 |
|:-----|:---------|:---------|
| rule | **upfront 全量** | 全局规则 + 项目规则 + rules/ 目录最多 3 层嵌套（模块级）；三种生效方式（指定文件/智能判断/#Rule 手动最高优先级）；AGENTS.md/CLAUDE.md 兼容 |
| spec | 文档集理解 | 项目文档作为知识源注入 |
| memory | **文件化自动维护** | `~/.trae-cn/memory/user_profile.md`（跨项目）+ `projects/{path}/project_memory.md`（项目专属）；AI 自动识别偏好写入/更新/删除（四种维护方式），可直接编辑 |
| skills | **元数据 upfront + 全文 JIT** | 官方文档明示："**规则全量加载 vs 技能按需加载**"——先扫描简要描述、仅相关时加载详情 |
| 对话上下文 | IDE 原生上下文 | 当前文件自动可见 + 选中代码片段（带文件名行号）+ `#` 文件引用 |
| 导入文本 | 代码库索引 | codebase-indexing 全仓索引支撑检索型上下文（类似 Claude Code 的 Code Search） |
| 用户提示词 | 必载 | 不可压缩 |

> **设计哲学**：Trae 把"记忆文件化透明可编辑"作为差异化（Claude Code 的 memory 是工具化黑盒，Trae 的 memory 是可见可改的 md 文件）；上下文来源深度绑定 IDE（当前文件/选中片段/代码库索引），这是"AI IDE"基因的自然延伸 [来源: 五工程分析 §4.3 判断]。

### 3.3 DeepSeek Harness：阈值压缩 + 检索注入 + KV Cache 复用

**上下文管理器机制**（DeepSeek Harness 技术框架分析 §3.2）：

1. **阈值触发压缩**：上下文达窗口 80% 触发（200K 窗口 → 167K 触发），预留 min(20K, 窗口/4) 给摘要、min(13K, 窗口/8) 给后续对话 [来源: 2026-08-13 分析 §3.2]。
2. **保留最近 N 轮**：最后 3 轮完整对话（user/assistant/tool_call/tool_result 全保留）不动。
3. **历史摘要化**：保留区之前的历史由 LLM 生成摘要，**必须保留四类信息：用户关键诉求、已完成操作、双方达成的共识、待办事项**。
4. **动态检索注入**：从代码库/历史会话/外部知识源实时抽取相关片段注入 Prompt（RAG 式）。
5. **事实沉淀到长期记忆**：避免摘要压缩丢失关键信息。

**成本侧**：KV Cache 智能复用（避免重复 prefill）+ 缓存定价杠杆（命中 0.02 元 vs 未命中 1 元，50 倍差）。"单次任务约 $0.028"正是缓存机制 + KV 复用 + minimal 上下文共同作用的结果——**成本优势不只是模型便宜，更是 Harness 把便宜结构化放大** [来源: 2026-08-13 分析 §4.2]。

### 3.4 CowAgent：八节 system prompt + 按需注入 + trim-flush-摘要

**源码实证**（/home/lzh/CowAgent/agent/prompt/builder.py，2026-08-18 读取）：

**system prompt 组装顺序（8 节）**——顺序即缓存设计：

```text
build_agent_system_prompt() section order (order == cache design):
 1. Tooling        tool list (one-line summary) + call style
 2. Skills         skill metadata (condensed XML: name/description/location)
 3. Memory         memory system usage guide (memory_search/memory_get)
 4. Knowledge      knowledge/index.md module overview injection
 5. Workspace      workspace description and path rules
 6. User identity  user info
 7. Project context  AGENT.md / USER.md / RULE.md / MEMORY.md / BOOTSTRAP.md full text
 8. Runtime        current time / model / channel
```

| 来源 | 加载路径 | 机制细节（源码行号） |
|:-----|:---------|:---------------------|
| rule | **upfront 全文** | AGENT/USER/RULE/MEMORY 全文注入 system prompt（builder.py §7） |
| spec | 知识库 JIT | knowledge/index.md 注入概览；正文由 memory_search 检索读取 |
| memory | 索引 upfront + 正文 JIT | MEMORY.md 注入；memory/ 每日文件按需 memory_get |
| skills | **元数据 upfront + 全文 JIT** | `_condense_skills_prompt` 压缩 XML：去掉 base_dir、location 缩短为相对路径、**不注入 SKILL.md 全文**（注释明示"agent reads it via the read tool only after selecting a skill"——保持每轮固定成本低） |
| 工具 | **内置全量 + MCP 按需** | `_select_tools_for_injection`：MCP 工具数 > 20 时，用 embedding 检索 top_k=10 个最相关 MCP 工具注入（run 内只增不减，防 schema 中途消失）；内置工具永远全量 |
| 对话上下文 | 裁剪 + flush + 摘要 | `_trim_messages`：见下 |
| 导入文本 | 工具 JIT | read/web_fetch 结果作为 tool_result 进入历史，历史超长时截断（30K→10K） |
| 用户提示词 | 必载 | 深度分析前缀触发独立上下文（见 §6.3） |

**`_trim_messages` 三层策略**（agent/protocol/agent_stream.py L1852）：

```text
_trim_messages() three-layer strategy:
Step 0  truncate historical tool results: 30K -> 10K (keep head+tail)
Step 1  turn limit: > max_context_turns(30) -> remove first half (whole-turn unit)
        -> simultaneously flush_memory(discarded msgs) + inject context summary (async LLM call)
Step 2  token limit: reserve 10% of window for reply, estimate system prompt tokens,
        if over limit keep removing whole turns (discarded -> flush to daily memory)
```

> **设计哲学**：CowAgent 与 Claude Code 同构（静态常驻 + 动态按需 + 裁剪压缩），但有两个本地化差异：① **知识库作为一等公民**（index.md 注入 + memory_search 检索），信息资产可跨会话复用；② **session 长驻模式下任务级上下文重置**（深度分析前缀），对抗 feishu 渠道的上下文无限累积（详见 §6）。

### 3.5 四 Agent 对比矩阵

| 维度 | Claude Code | Trae | DeepSeek Harness | CowAgent |
|:-----|:-----------|:-----|:-----------------|:---------|
| rule 加载 | upfront（三层 CLAUDE.md） | upfront（全局/项目/模块） | 未公开（推测 upfront） | upfront（AGENT/USER/RULE 全文） |
| skills 加载 | 元数据 upfront + 全文 JIT | 元数据 upfront + 全文 JIT（官方明示） | 未公开（生态含 skill 方向） | 元数据 upfront（condensed）+ 全文 JIT |
| memory 形态 | 工具化 /memory | **文件化自动维护** | 跨会话记忆（/clear 只清短期） | 文件化（MEMORY.md + memory/ 每日）+ flush |
| 压缩触发 | 窗口接近上限（auto-compact） | 未公开 | **窗口 80% 阈值** | 轮次 30 + token 预算（预留 10%） |
| 压缩保真 | 架构决策/未解 bug/实现细节 + 最近 5 文件 | 未公开 | 四类信息（诉求/操作/共识/待办） | flush 到每日记忆 + 上下文摘要注入 |
| 检索式上下文 | @-mention + glob/grep + Code Search | 代码库索引 + 选中片段 | 动态检索注入（RAG） | memory_search + knowledge/index.md |
| 缓存工程 | Prompt Caching（cache_control） | 依赖模型侧 | KV Cache 复用 + 命中 0.02 元定价 | 前缀静态化（8 节顺序稳定）+ deepseek_usage 落盘 |
| 任务级隔离 | Subagents（独立上下文） | 子智能体（独立上下文） | Sub-agent（隔离搜索上下文） | 深度分析前缀 → 独立上下文 |

> **共性结论**：四大 Agent 在三个点上高度收敛——① 静态规则 upfront、动态内容 JIT；② skills 全文永不常驻；③ 抛弃前先沉淀。差异集中在**压缩策略的精细度**（Claude/Harness 有显式保真清单，Trae 未公开）与**记忆的维护方式**（工具化 vs 文件化）。

---

## 4. 什么时候导入：加载时机决策框架

### 4.1 时机决策的四个层级

"什么时候导入"不是单一决策，而是**四级过滤**（每级回答一个不同的"何时"）：

| 层级 | 决策问题 | 判据 | 例子 |
|:-----|:---------|:-----|:-----|
| **会话级** | 这个 session 的基座是什么？ | 任务领域/用户画像 | 深度分析 session 不带长驻历史（cowagent） |
| **任务级** | 这个任务的契约是什么？ | spec/rule 相关性 | CLAUDE.md 项目规则、@import 组装 |
| **请求级** | 这一轮模型需要看什么？ | 当前消息的意图 | JIT 读取文件、memory_search 检索、MCP top-k |
| **工具级** | 这个工具结果要不要保留？ | 对后续轮次的边际价值 | tool result clearing（历史深处直接清） |

> **通用判据**：导入的边际价值 > 边际成本（token + 注意力稀释 + 缓存破坏）才导入。**缓存破坏是隐性成本**——在动态内容中插入新静态块，会让之后所有轮次的前缀缓存全部失效 [来源: 本文 4.2 推导]。

### 4.2 缓存经济学：前缀静态化是成本胜负手

**量化锚点**（两条独立实证）：

| 实证 | 数据 | 来源 |
|:-----|:-----|:-----|
| DeepSeek V4 缓存定价 | 命中 0.02 元 vs 未命中 1 元 / 百万 token（**50 倍差**） | DeepSeek Harness 分析 §4.2 |
| 本库 27 天实测 | 2.3B tokens，缓存未命中 58% 为最大成本项 | MEMORY.md（08-15 实测） |
| Anthropic 8/17 新价 | flash miss 输入 1→1.5/3.0、输出 2→4.5/9.0；pro 输出 6→13.5/27.0（同用量 +186%） | MEMORY.md |

**前缀静态化三条规则**：

1. **静态内容最前**：身份/人格/规则/工具 schema 放最前 → 最长公共前缀命中。
2. **顺序永不漂移**：system prompt 节顺序固定（cowagent 8 节顺序即为此设计）；新增静态块只追加到动态区之前固定位置。
3. **动态内容最后**：工具结果/对话历史/当前消息放后面，前缀不受其变化影响。

> **推论**："什么时候导入"的第一性答案 = **让静态内容尽早、尽量稳定地进入前缀**；动态内容越晚进入越好（进入越晚，破坏缓存的机会越少）。这解释了为什么四大 Agent 都坚持"skills 全文 JIT"——全文常驻会把 5-20 KB×N 的变长内容塞进前缀，直接击穿缓存。

### 4.3 导入的三种形态与保真度

| 形态 | 机制 | 保真度 | 成本 | 适用 |
|:-----|:-----|:------:|:----:|:-----|
| **全量注入** | 原文进 context | 100% | 高 | 当前任务核心文件、当前消息 |
| **元数据/索引注入** | 名称+描述+位置进 context | 中（指引级） | 低 | skills 列表、知识库 index、工具清单 |
| **摘要/片段注入** | LLM 生成或检索截取 | 低-中 | 中 | 历史压缩、RAG 片段、compaction 结果 |

> **工程启示**：导入不是二元的（导/不导），而是**三元**（全量/索引/摘要）。四大 Agent 的 Skills 全部用"索引形态"常驻 + "全量形态"JIT——这是把"目录"与"正文"分离的标准做法，自建系统应直接采用。

---

## 5. 什么时候抛弃：蒸馏而非删除

### 5.1 抛弃的四个触发条件

| 触发条件 | 判据 | 典型阈值 | 代表实现 |
|:---------|:-----|:---------|:---------|
| **窗口阈值** | 上下文接近模型窗口上限 | 80%（200K→167K） | DeepSeek Harness |
| **轮次阈值** | 对话轮数超过预算 | 30 轮（cowagent）/ 12 轮（旧版） | CowAgent / 通用 |
| **成本预算** | 每轮 token 成本超限 | 预留 10% 给回复 | CowAgent _trim_messages |
| **任务边界** | 新任务开始，旧任务上下文失效 | 深度分析前缀 | CowAgent 08-17 修复 |

> **关键判据**：抛弃不该等"窗口快满"，而应在**边际信息价值低于保留成本**时发生。轮次阈值与任务边界属于主动抛弃（预防性），窗口阈值属于被动抛弃（兜底性）——主动抛弃优于被动抛弃，因为兜底压缩时注意力已被稀释过一轮。

### 5.2 抛弃方式谱系：截断 → 裁剪 → 压缩 → 蒸馏

```text
drop spectrum (fidelity low <-----------------------------------> high)
truncate (hard delete, no LLM, cost ~0)
  - tool result 30K -> 10K (cowagent)
trim (delete whole turns, no LLM, cost ~0)
  - 30 turns -> 15 turns (cowagent)
compact (LLM summary, cost = 1 LLM call)
  - history -> 4-type summary (harness / claude)
distill (memory + index, cost = 1 LLM call + one write)
  - summary -> memory/ daily file (cowagent flush)
```

- **截断**：同一条消息内删减（工具结果保留首尾）——信息损失可控，成本零。
- **裁剪**：以完整轮为单位删除（保证 tool_use/tool_result 成对，防 LLM 循环）——Anthropic 与 cowagent 共同强调"完整轮"单位 [来源: 五工程分析 §4.2 + agent_stream.py L1852 注释]。
- **压缩**：LLM 生成摘要替换历史——保真度取决于摘要 prompt 质量，Anthropic 建议"先最大化 recall，再迭代 precision" [来源: Anthropic 官方博客]。
- **蒸馏**：把信息写进记忆/知识库（persist），上下文释放但资产保留——**这是唯一"抛弃后仍可恢复"的方式**。

> **工程启示**：四层谱系应按"成本从低到高、信息从粗到精"的顺序组合使用：日常用截断+裁剪（零成本），接近窗口用压缩（一次 LLM 调用），任务边界/会话结束时用蒸馏（写记忆）。CowAgent 的 `_trim_messages` 已实现前三层组合，第四层（蒸馏）由 flush_memory 承担。

### 5.3 抛弃的保真度红线：四类信息不可丢

DeepSeek Harness 的摘要四类信息与 Anthropic compaction 的保留清单高度一致，可归纳为**跨实现的保真度红线**：

| 红线 | 内容 | 丢失后果 |
|:-----|:-----|:---------|
| **用户关键诉求** | 任务目标、原始需求 | 目标漂移、答非所问 |
| **已完成操作** | 已执行的动作/已改的文件 | 重复执行（P2 现象） |
| **双方共识** | 已确认的决策/约定 | 返工、推翻已定方案 |
| **待办事项** | 未完成的任务/下一步 | 任务中断、烂尾 |

> 对照：本库 context-pollution 分析将"重复执行"归因于历史被裁剪后模型无记忆——**保真度红线正是防重复执行的保险丝**：裁剪不是"删掉"，而是"把四类信息提炼后放回记忆"。

---

## 6. Session 绑定：上下文生命周期的容器

### 6.1 session × 上下文的生命周期矩阵

Session 是消息的容器，但**上下文生命周期可以与 session 生命周期解耦**：

| 上下文生命周期 | 与 session 关系 | 代表机制 |
|:--------------|:---------------|:---------|
| **会话级常驻** | 随 session 创建/销毁 | system prompt 基座、CLAUDE.md |
| **任务级重置** | 同一 session 内按任务边界重建 | cowagent 深度分析前缀、Plan Mode |
| **请求级裁剪** | 每轮按预算调整 | _trim_messages、auto-compact |
| **跨会话持久** | 独立于 session 存活 | memory 文件、记忆蒸馏、/clear 只清短期（harness） |

> **核心矛盾**：session 长驻（聊天渠道的默认形态）保证连续性，但上下文无限累积 → 注意力稀释 + 成本线性增长。**session 提供连续性，任务边界提供新鲜度**——两者需要显式的仲裁者（前缀检测/显式命令/自动阈值）。

### 6.2 长驻 session 的上下文膨胀（feishu 实证）

CowAgent feishu 渠道实证（2026-08-17 修复前）：

- **现象**：feishu session 长驻 → 上下文无限累积，实测 **141+ messages / 170K tokens** [来源: agent_stream.py L566-568 注释]。
- **劣化链**：上下文在超限边缘启动 → 有效注意力被稀释 → 深度分析任务 3-6 turns 草草结束 → 质量劣化。
- **根因**：session 生命周期（长驻）与任务生命周期（短）错配——没有在任务边界重置上下文的机制。

### 6.3 会话级隔离：深度分析独立上下文模式

2026-08-17 修复方案（agent_stream.py L571-589 源码）：

```text
detect: user_message.strip().startswith("deep-analysis prefix")
action: 1) take out all old messages -> memory_manager.flush_memory(
            messages=discarded, reason="deep_analysis_fresh_context")
        2) self.messages = []  (keep only system prompt + current message)
        3) log: "Deep-analysis fresh context: discarded N history messages"
effect: context from 170K -> clean start; old info written to daily memory
        (not lost, no longer occupying context)
```

**设计要点**：
1. **丢弃与持久化原子化**：抛弃上下文的同时 flush 到记忆，信息不丢（persist 定律）。
2. **前缀显式声明**：用户消息前缀触发，非隐式启发——避免误伤连续性。
3. **与 session 解耦**：session 本身不重建（feishu 会话 ID 不变），只重建上下文——**session 是持久层，上下文是计算层**。

> **可泛化模式**：任何长驻 session 的 Agent 都应有"**任务级上下文重置**"入口（显式命令或前缀），配合记忆 flush 实现"连续性由 session 保证、新鲜度由任务边界保证"的双轨设计。

---

## 7. 对自建 Agent 的落地清单（cowagent 视角）

结合本文分析与本库既有五层方案（context-pollution 分析 §5），落地优先级：

| # | 动作 | 对应机制 | 预期收益 | 成本 |
|:--|:-----|:---------|:---------|:----|
| 1 | **system prompt 前缀静态化审计** | 8 节顺序固定；新增静态块追加到固定位置 | 缓存命中率提升（本库 58% miss 的最大可降项） | 低 |
| 2 | **skills 元数据瘦身** | `_condense_skills_prompt` 已做；进一步压缩 description 长度 | 每轮固定成本下降 | 低 |
| 3 | **MCP 工具按需注入参数化** | 阈值 20/top_k 10 按模型窗口调整 | 工具 schema 膨胀可控 | 低 |
| 4 | **主动抛弃优于被动兜底** | 轮次阈值 30 下调至 20（对话型任务）；任务边界显式重置 | 注意力稀释前主动换血 | 低 |
| 5 | **保真度红线检查** | trim/压缩前校验四类信息是否已进摘要（诉求/操作/共识/待办） | 防重复执行 P2 | 中 |
| 6 | **缓存破坏监控** | 记录每轮 cache hit/miss 率；静态块变更时告警 | 成本可观测 | 中 |
| 7 | **会话级隔离泛化** | 深度分析前缀模式扩展为配置化（如"新任务"命令） | 长驻 session 通用解药 | 中 |
| 8 | **摘要质量回测** | compaction 摘要与原文的要点召回率抽样评估（Anthropic 建议先 recall 后 precision） | 压缩保真度量化 | 高 |

> **第一性收束**：上下文管理的全部问题可以归结为一句话——**在注意力预算和 token 预算的双重约束下，让模型每轮看到"最该看的东西"**。导入看缓存经济学（前缀静态化），抛弃看保真度红线（蒸馏而非删除），session 负责连续性，任务边界负责新鲜度。

---

## 8. 来源与验证

**官方一手来源**：
1. Anthropic《Effective context engineering for AI agents》— 2025-09-29 发布，2026-08-18 抓取（www.anthropic.com/engineering/effective-context-engineering-for-ai-agents）— compaction/注意力预算/混合检索/工具结果清理/子代理隔离
2. Claude Code 官方文档（docs.anthropic.com，2026-08 快照，转引自五工程分析 §10）
3. Trae 官方文档 13 页（docs.trae.cn，2026-08-05 抓取，转引自五工程分析 §10）— 规则全量 vs 技能按需、记忆文件、代码库索引
4. DeepSeek Harness 技术框架分析（本库 2026-08-13）— 80% 阈值压缩/保留 3 轮/摘要四类信息/动态检索注入/KV Cache 复用
5. CowAgent 源码实证 — `/home/lzh/CowAgent/agent/prompt/builder.py`（8 节组装）、`agent/protocol/agent_stream.py` L566-589（深度分析重置）/L1852+（_trim_messages）、`models/session_manager.py`（Session/SessionManager）

**本库既有专题（交叉引用）**：
- [五工程 × 双产品](2026-08-05-five-engineering-claude-code-trae-deep-analysis.md) — 上下文工程维度对比
- [上下文污染与重复执行](../methodology/2026-08-14-context-pollution-repeat-execution-analysis.md) — 污染机制/五层方案
- [DeepSeek Harness 技术框架](2026-08-13-deepseek-harness-technical-framework-analysis.md) — 缓存经济学 50 倍差
- [Agent 退化模式](2026-08-17-agent-degeneration-modes-harness-architecture-deep-analysis.md) — 长上下文劣化
- [Token 优化五技术](../methodology/2026-08-14-ai-pipeline-token-optimization-five-techniques-deep-analysis.md) — token 成本工程

**素材分级**：Anthropic 官方博客与官方文档 = 高可信一手；Trae 官方文档 = 高可信一手快照（功能随版本演进）；DeepSeek Harness = 官方架构未全公开，部分机制（KV Cache 复用/sub-agent）为社区转述标注为泄露级线索；CowAgent = 源码直接实证（最高可信）；四 Agent 对比结论为本文分析。

**验证状态**：本文"四类信息红线"（诉求/操作/共识/待办）为 DeepSeek Harness 官方口径与 Anthropic compaction 保留清单的归纳，非单一来源；"缓存破坏是隐性成本"为本文从前缀缓存机制推导的分析性结论，未做独立实验验证，标注为推论。

---

## 变更记录

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-18 | v1.0 | 首次创建：七大上下文来源三分类（静态基座/半静态索引/动态载荷）+ 三条时序定律（upfront/JIT/persist）+ 四 Agent message 组装机制对比（含 CowAgent 源码实证）+ 加载时机四级决策 + 缓存经济学前缀静态化 + 抛弃四触发条件与四层谱系 + 保真度红线 + session 绑定与任务级隔离模式 + 落地清单 |
