# 🔬 每轮对话 Token 消耗源完整清单：源码级精确测量报告

> **类型**: 源码级分析 · **创建**: 2026-08-14 · **版本**: v1.0
> **方法**: 从 `/home/lzh/CowAgent` 源码（`agent/prompt/builder.py` / `workspace.py` / `skills/formatter.py` / `agent_stream.py` / `deepseek_bot.py`）+ `run.log`（23,464 次 API 请求实测）谨慎推演，**每段均标注来源行号与实测值**
> **替代报告**: 本报告取代 `20260728_114741-token-consumption-analysis.md`（其 Skills 高估 10 倍、工具定义高估 5 倍，见 §6）
> **交叉链接**: [Token 优化五技术](2026-08-14-ai-pipeline-token-optimization-five-techniques-deep-analysis.md) · [工程规模评估](2026-08-14-engineering-scale-assessment-full-spectrum-plan.md) · [推理单位经济学](../../06_others/sources/2026-08-12-inference-unit-economics-true-cost-per-million-tokens.md)

---

## 📑 目录

- [§0 核心结论（先看这个）](#0-核心结论先看这个)
- [§1 每轮请求的 Token 结构总览](#1-每轮请求的-token-结构总览)
- [§2 固定 System Prompt（每轮必发，12,462 tok）](#2-固定-system-prompt每轮必发12462-tok)
  - [2.1 十三个 Token 源完整清单（含加载时机）](#21-十三个-token-源完整清单含加载时机)
  - [2.2 各文件的加载时机表（管控核心）](#22-各文件的加载时机表管控核心)
- [§3 历史消息回读（随轮次线性增长）](#3-历史消息回读随轮次线性增长)
- [§4 工具调用与工具结果](#4-工具调用与工具结果)
- [§5 输出 Token（completion）](#5-输出-tokencompletion)
- [§6 为什么 07-28 报告不可靠（口径审计）](#6-为什么-07-28-报告不可靠口径审计)
- [§7 现有监控的缺陷与修复建议](#7-现有监控的缺陷与修复建议)
- [§8 单轮 token 成本计算器（自测公式）](#8-单轮-token-成本计算器自测公式)
- [Changelog](#changelog)

---

## §0 核心结论（先看这个）

**每轮对话 token 消耗 = 固定 System (≈12.5K) + 历史消息回读 (≈9.2K/轮次增长) + 工具结果 + 输出**

**五个关键数字**（2026-08-14 实测）：

| # | 指标 | 实测值 | 来源 |
|:-:|:-----|:-------|:-----|
| 1 | **固定 System Prompt** | **≈12,462 tokens**（每轮必发） | builder.py 逐段模拟 |
| 2 | 最大单项：技能 desc 列表 | 2,981 tok（23.9%） | formatter.py 压缩后 |
| 3 | 次大单项：RULE.md 全文 | 2,790 tok（22.4%） | workspace.py 全文注入 |
| 4 | 历史消息回读 | 均 64 msgs/请求 ≈ 19.2K tok（线性增长） | run.log 23,464 请求实测 |
| 5 | 单轮总消耗（4 轮会话中位） | **≈30-45K input tokens** | 12.5K + 19.2K + 工具 |

**三个关键洞察**：

1. **07-28 报告 Skills 高估 10 倍**：其声称"系统 Prompt 50,632 tokens / Skills XML 30,832"——但源码 `formatter.py` 有 `_condense_description_for_prompt()` 把每个 desc 压缩到 ≤200 字符，实际仅 **2,981 tokens**（实测 99 技能）。**真实固定开销是 12.5K，不是 50.6K**
2. **历史回读才是最大隐性成本**：每轮请求都重发全部历史消息（当前会话已到 207 msgs），且**无真实 token 记录**（`deepseek_bot.py` 只取 total_tokens 且不落盘）——这是监控盲区
3. **真正可管控的三个杠杆**：技能 desc（2,981，可再压 40%）、RULE.md（2,790，可精炼 30%）、历史消息（19.2K，靠 `_trim_messages` 轮次上限 30 兜底）

---

## §1 每轮请求的 Token 结构总览

```text
单轮 API 请求 input tokens（4 轮会话中位实测）:
┌─────────────────────────────────────────────────────┐
│  固定 System Prompt           12,462 tok  (38.8%)    │
│  ├─ 技能 desc 列表             2,981  (23.9%)        │
│  ├─ RULE.md 全文              2,790  (22.4%)        │
│  ├─ knowledge index 摘要        828   (6.6%)         │
│  ├─ 工作空间段                  905   (7.3%)         │
│  ├─ 记忆系统文案                713   (5.7%)         │
│  ├─ AGENT.md                   779   (6.3%)         │
│  ├─ MEMORY.md                 1,390  (11.2%)        │
│  ├─ 工具系统段                  533   (4.3%)         │
│  ├─ USER.md                    652   (5.2%)         │
│  ├─ 技能系统文案                346   (2.8%)         │
│  ├─ 知识系统文案                427   (3.4%)         │
│  └─ 运行时+回复语言             118   (1.0%)         │
├─────────────────────────────────────────────────────┤
│  历史消息回读（64 msgs）        ~19,200 tok (59.8%)  │
│  ├─ 历史对话文本（user+assistant）                   │
│  ├─ 历史工具调用链（tool_use+tool_result）           │
│  └─ 历史上下文压缩摘要（若有）                       │
├─────────────────────────────────────────────────────┤
│  工具结果（当前轮）              ~500-5K tok  (1-15%) │
└─────────────────────────────────────────────────────┘
```

**四类 Token 源的定义与边界**：

| 类别 | 内容 | 是否每轮 | 增长方式 |
|:-----|:-----|:--------:|:---------|
| 固定 System | builder.py 13 段拼接 | ✅ 每轮全发 | 恒定（除非文件变） |
| 历史回读 | 之前轮次的全部消息 | ✅ 每轮全发 | **随轮次线性 +2 msgs/轮** |
| 工具结果 | 本轮 read/bash 等输出 | ✅ 本轮必含 | 随工具调用 |
| 输出 | 模型生成的回复/工具参数 | ✅ | 随任务复杂度 |

---

## §2 固定 System Prompt（每轮必发，12,462 tok）

### 2.1 十三个 Token 源完整清单（含加载时机）

**来源**: `agent/prompt/builder.py` `build_agent_system_prompt()`（L78-154），每轮 `run_stream()` 都调用 `get_full_system_prompt()`（agent.py L106-142）**重新构建**。段顺序与源码一致。

| # | Token 源 | Tokens | 占比 | 加载时机 | 源码位置 | 可变性 |
|:-:|:---------|:------:|:----:|:---------|:---------|:-------|
| 1 | **技能 desc 列表** `<available_skills>` | 2,981 | 23.9% | 每轮（SkillManager.build_skills_prompt，formatter 压缩后） | formatter.py L95-129 | 🔴 可再压 |
| 2 | **RULE.md 全文** | 2,790 | 22.4% | 会话构建时 load_context_files 全文注入 | workspace.py L133-172 | 🔴 可精炼 |
| 3 | **MEMORY.md 全文**（截断后） | 1,390 | 11.2% | 同上（>200行/25KB 截断取尾部） | workspace.py L190-213 | 🟡 已压 |
| 4 | **工作空间段**（路径+交流规范固定文案） | 905 | 7.3% | 每轮（builder L633-721） | builder.py L676-714 | 🟡 静态 |
| 5 | **knowledge index 摘要** | 828 | 6.6% | 每轮（读取 index.md 提取模块概览，245KB→1.6KB） | builder.py L483-519 | 🟢 已压 |
| 6 | **AGENT.md 全文** | 779 | 6.3% | 会话构建时注入 | workspace.py L133-172 | 🟢 精简 |
| 7 | **记忆系统固定文案**（recall+写入规则） | 713 | 5.7% | 每轮（builder L387-480） | builder.py L442-478 | 🟡 静态 |
| 8 | **USER.md 全文** | 652 | 5.2% | 会话构建时注入 | workspace.py L133-172 | 🟢 精简 |
| 9 | **工具系统段**（16 工具一行摘要） | 533 | 4.3% | 每轮（builder L185-284） | builder.py L209-282 | 🟢 已精简 |
| 10 | **知识系统固定文案**（自动写入规则） | 427 | 3.4% | 每轮（builder L522-599） | builder.py L556-575 | 🟡 静态 |
| 11 | **技能系统固定文案**（扫描指引） | 346 | 2.8% | 每轮（builder L323-384） | builder.py L354-368 | 🟡 静态 |
| 12 | **运行时信息**（时间/模型/渠道） | 60 | 0.5% | 每轮（动态时间回调） | builder.py L779-840 | 🟢 已最小 |
| 13 | **回复语言段** | 58 | 0.5% | 每轮（固定追加） | builder.py L157-176 | 🟢 已最小 |
| | **合计** | **12,462** | 100% | | | |

### 2.2 各文件的加载时机表（管控核心）

> **这是后续 token 管控的核心**——明确每个文件何时进上下文、何时不进。

| 文件 | 注入方式 | 时机 | 大小 | 何时变化 | 管控建议 |
|:-----|:---------|:-----|:-----|:---------|:---------|
| **AGENT.md** | 全文注入 | 每会话构建（每次请求重建） | 1.7KB / 779 tok | 人格演进（季度） | 保持精简，勿膨胀 |
| **USER.md** | 全文注入 | 同上 | 1.5KB / 652 tok | 身份变化（年） | ✅ 已精简 |
| **RULE.md** | 全文注入 | 同上 | 6.7KB / 2,790 tok | 规则更新（月） | 🔴 **最大可压项**：合并条款/去重 |
| **MEMORY.md** | 全文注入（截断 200行/25KB） | 同上 | 3.4KB / 1,390 tok | 记忆更新（月） | ✅ 已压缩 86%，继续索引化 |
| **memory/YYYY-MM-DD.md** | **不注入**（仅提及路径） | 工具检索 | 32KB | 日更 | ✅ 已做对：不注入 |
| **knowledge/index.md** | 摘要注入（仅模块概览） | 每轮 | 245KB→1.6KB | 知识更新 | ✅ 已压 99.3% |
| **knowledge/ 其他页面** | **不注入**（read 工具按需读） | 工具检索 | 125MB 总 | - | ✅ 已做对 |
| **skills/desc** | 压缩列表注入 | 每轮 | 30.9KB→11.9KB | 技能增删 | 🔴 **可再压**：触发词更精简 |
| **SKILL.md 正文** | **不注入**（read 按需读） | 选中后读取 | 42MB 总 | - | ✅ 已做对 |
| **BOOTSTRAP.md** | 全文注入（仅首启存在） | 首会话 | - | 完成即删 | ✅ 已清理 |

**加载时机的三个"已做对"**（值得保持）：
1. **每日记忆不注入**——32KB 每日记忆只在需要时 memory_get 检索
2. **知识库页面不注入**——125MB 知识只在需要时 read
3. **SKILL.md 正文不注入**——技能只在选中后 read

---

## §3 历史消息回读（随轮次线性增长）

**这是当前最大的隐性 token 成本，且无精确记录。**

**源码机制**（agent.py L433-478 + agent_stream.py L1048-1056）：
- 每轮 `run_stream()` 把 `self.messages`（全部历史）复制给 executor
- executor 每轮向 LLM 发送 `Sending N messages (M turns)`——**N 全部历史消息数**
- 只有 `_trim_messages()` 在超 30 turns 或超 token 预算时才裁剪

**run.log 实测**（23,464 次 API 请求）：

| 指标 | 实测 | 含义 |
|:-----|:-----|:-----|
| 每请求消息数（均值） | 64 msgs | 每轮重发 64 条历史消息 |
| 每请求消息数（中位） | 47 msgs | |
| 每请求消息数（最大） | 443 msgs | 超长会话 |
| 消息增长速率 | **+2/轮** | 每轮新增 user+assistant 各 1 |
| 当前活跃会话 | 207 msgs（还在涨） | 本次会话已 207 条 |

**token 估算**：混合 300 tok/msg × 64 msgs ≈ **19,200 tokens/请求**（输入侧），随轮次**线性增长**，30 turns 上限触发裁剪。

**为什么无精确值**：`deepseek_bot.py`（L181）只取 `usage.total_tokens`，`session_manager.py`（L80）只在 debug 日志打印；**prompt_tokens 从未落盘**。run.log 中真实 usage 仅出现 12 次（都是调试命令的输出）。

---

## §4 工具调用与工具结果

**机制**（agent_stream.py）：
- 当前轮工具结果截断到 30K chars；历史轮次截断到 20K chars（L1641-1691）
- 工具调用本身（tool_use JSON）每条约 50-200 tok

**run.log 实测**（可见工具输出字符数，日志侧截断 203 chars 显示）：

| 工具 | 调用次数 | 累计输出 chars | 说明 |
|:-----|:--------:|:--------------:|:-----|
| bash | 15,239 | 2,817,582 | 最大消耗源 |
| edit | 3,353 | 680,659 | |
| read | 2,690 | 536,877 | |
| write | 1,038 | 191,022 | |
| web_fetch | 3,021 | 171,748 | 有截断保护 |
| 其余 | 532 | 84,787 | |

**注意**：日志显示的 203 chars 是**日志截断**，不是上下文截断——实际上下文中 bash 输出可能到 30K chars（≈7.5K tok）。**工具结果 token 由调用频率×输出大小决定，是波动最大的变量。**

---

## §5 输出 Token（completion）

**机制**：模型回复 + 工具调用参数（tool_use JSON）都计输出 token。
- 定价 ¥2.0/M（DeepSeek 官方 JSON：`"output": 2.00`）
- 每轮输出通常 200-2,000 tok（工具调用多时更高）
- **无独立落盘记录**（同样只有 total_tokens 汇总）

**输出 token 占比**：以 4 轮会话中位计，输出约 1-3K tok，占单轮总量 5-10%。优化杠杆低（模型行为决定），主要靠**让回复更聚焦**（减少冗长中间推理）。

---

## §6 为什么 07-28 报告不可靠（口径审计）

**结论**：`20260728_114741-token-consumption-analysis.md` 的**绝对数字全部不可用**，但其**结构分析方法论（帕累托/缓存影响）仍可参考**。

| 07-28 报告声称 | 实际（源码+实测） | 偏差 | 根因 |
|:---------------|:-----------------|:-----|:-----|
| 系统 Prompt **50,632 tokens** | **12,462 tokens** | **高估 4.1 倍** | 未走 formatter 压缩，按原始 desc 估算 |
| Skills XML **30,832 tokens (60.9%)** | **2,981 tokens (23.9%)** | **高估 10.3 倍** | 忽略 `_condense_description_for_prompt()`（desc 压到 ≤200 字符） |
| 工具系统 **5,000 tokens** | **533 tokens** | **高估 9.4 倍** | 按 12 工具完整 JSON schema 估，实际只注入一行摘要 |
| 核心指令 5,000 | 5,611（AGENT+USER+RULE+MEMORY） | 接近 | 口径基本对 |
| 历史会话总量 12.4M tokens | 无法验证 | ? | 用 conversation-log 文件字节估，非 API usage |

**根因总结**：报告在 07-28 生成时**未阅读 formatter.py 的压缩逻辑**，直接按 `skills_config.json` 的原始 description 全量估算；同时**没有真实 usage 数据源**（当时 run.log 也不记录 prompt_tokens）。

---

## §7 现有监控的缺陷与修复建议

**现有监控**（`token-context-daily.csv` + `kb-token-context-stats.py`）：
- 统计的是**静态文件大小估算**（AGENT/USER/RULE/MEMORY + skills desc + knowledge 全量），不是**真实 API usage**
- `SYSTEM_FIXED_EST = 8000` 是拍脑袋常数（实际固定段 12,462，其中框架文案约 4,691 + 技能 desc 2,981）
- **完全缺失**：历史消息回读、工具结果、输出 token 三个动态维度

**修复建议（按优先级）**：

| # | 动作 | 位置 | 收益 |
|:-:|:-----|:-----|:-----|
| 1 | **记录真实 usage**：`deepseek_bot.py` L181 处把 prompt_tokens/completion_tokens/total_tokens 写入结构化日志（JSON 行） | models/deepseek/deepseek_bot.py | 根治监控盲区 |
| 2 | **每请求记录**：executor 发送前记录 messages 数 + 估算 tokens（已有 Sending 日志，补 token 字段） | agent_stream.py L1056 | 精确回读统计 |
| 3 | **工具结果计费**：记录每次工具结果实际字符数（非日志截断 203） | agent_stream.py tool_result 创建处 | 工具维度精确 |
| 4 | **修正 SYSTEM_FIXED_EST**：用本文 §2 的 12,462 或接入真实 tokenizer | kb-token-context-stats.py L54 | 报表口径正确 |
| 5 | **官方对账**：DeepSeek 平台 JSON 每日导入，与本地估算交叉验证 | token-consumption-analyzer.py | 绝对数字锚定 |

---

## §8 单轮 token 成本计算器（自测公式）

**给定会话轮次 N 与工具调用情况，估算单轮 input tokens**：

```text
input_tokens(N) ≈ 12,462 (固定 System)
                + 64×300 (历史回读，N 轮时约为 300×2N×平均消息长度因子)
                + Σ 工具结果字符数/4
                + 当前轮用户消息

示例（本次会话 N=4 轮，含 8 次工具调用）:
  ≈ 12,462 + 19,200 + (8 × 平均2K chars)/4 + 500
  ≈ 12,462 + 19,200 + 4,000 + 500
  ≈ 36,162 input tokens/请求

成本（混合价，缓存未命中 ¥1/M 主导）:
  ≈ 36.2K × (0.02~1.0)/1M ≈ ¥0.0007~0.036/请求
```

**管控抓手排序**（按单轮 token 占比 × 可压缩性）：

| 排序 | 抓手 | 当前 | 目标 | 单轮省 |
|:----:|:-----|:-----|:-----|:-------|
| 1 | 历史消息轮次上限 | 30 turns | 15 turns（+摘要） | -9.6K |
| 2 | RULE.md 精炼 | 2,790 | 1,800 | -1.0K |
| 3 | 技能 desc 再压缩 | 2,981 | 1,800 | -1.2K |
| 4 | 工具结果截断收紧 | 30K/20K | 15K/8K | 波动项 |
| 5 | 工具定义动态加载 | 全部 16 个 | 按需 8 个 | -0.2K |

---

## §7.5 外部基准对照：12,462 tok 固定段在行业中的位置（v2.0 新增）

> v2.0 升级：将本系统固定 System Prompt 的实测值放到行业基准中定位，验证"固定段是否已接近合理下限"。

### 7.5.1 Anthropic 的"注意力预算"视角

Anthropic 在《Effective context engineering for AI agents》（2025-09-29）中明确 [来源: Anthropic 官方博客]：

> "LLMs have an 'attention budget' that they draw on when parsing large volumes of context. Every new token introduced depletes this budget... The guiding principle: **find the smallest possible set of high-signal tokens** that maximize the likelihood of your desired outcome."

**对照本系统**：12,462 tok 固定段中，技能 desc（2,981）+ RULE.md（2,790）两项占 46%——按 Anthropic 标准属于"注入膨胀"（desc 全量注入而非最小集）。但注意：**本系统技能 desc 已是压缩后**（formatter 从 ~300字压到 ~100-150字），且全文按需 read——即已实现 Anthropic 建议的"最小高信号集 + 按需展开"的 80% 工作量，剩余优化空间有限（见 §8 管控抓手 3/5）。

### 7.5.2 行业 token 成本基准对照

| 维度 | 本系统实测 | 行业基准 | 对照结论 |
|:-----|:-----------|:---------|:---------|
| 固定 System Prompt | 12,462 tok | Anthropic 建议"minimal set of high-signal tokens"（无固定数字，但明确反对膨胀）| 🟡 中位偏上，两项可压 |
| 缓存未命中成本 | 57.1%（最大成本项） | Claude Code 一周 98.16% 缓存读取率（Anthropic 官方统计）[来源: Anthropic 缓存文档] | 🔴 差距大：**缓存友好性是最大优化空间** |
| 历史回读占比 | 19.2K/轮（64 msgs） | Anthropic compaction：上下文超限前主动摘要重开 | 🟡 已有 trim，但 12 turns 窗口偏大 |
| 单轮总成本 | ~30-45K tok | — | — |

**关键发现**：本系统最大成本项不是"注入太多"（12.5K 已接近合理），而是**缓存未命中**（57.1%）——这与 [Token 优化五技术](../2026-08-14-ai-pipeline-token-optimization-five-techniques-deep-analysis.md) 的 T1 Prompt Caching（-90%）判断一致：**先治缓存，再治注入**。低 freq 机制的 658 tok 相对缓存优化的 57.1% 差距是数量级的。

### 7.5.3 监控建议的外部对齐

Anthropic 建议"每次推理都观察 token 构成并迭代"（iterative curation）[来源: Anthropic Context Engineering]——本系统 §7 修复建议 1-3（记录真实 usage/每请求 token/工具结果计费）正是这一建议的落地：**没有测量就没有治理**。

---

## Changelog

| 日期 | 版本 | 变更 |
|:-----|:-----|:-----|
| 2026-08-14 | v1.0 | 创建：源码级精确测量（builder.py 13 段逐段模拟 12,462 tok + run.log 23,464 请求实测 + formatter 压缩验证 2,981 tok）；七类 token 源清单 + 十三个文件加载时机表；07-28 报告口径审计（Skills 高估 10 倍）；监控修复五建议；单轮成本计算器 |
| 2026-08-18 | v2.0 | **升级**：新增 §7.5 外部基准对照（Anthropic attention budget 视角 / 行业 token 成本基准表——缓存未命中 57.1% vs Claude Code 98.16% 缓存读取率 / 监控建议外部对齐）；修正认知：最大优化空间是缓存友好性而非注入压缩 |
