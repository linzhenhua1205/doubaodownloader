# CowAgent System Prompt Token 拆解审计：每轮固定成本的构成与优化空间

> **日期**: 2026-08-18 | **分类**: 03_AI/agent-engineering | **专题编号**: AGT-ENG-2026-08-A
> **一句话**: 用**真实构建链**（真实工具实例 + 真实 104 个技能 + 真实 context 文件 + 真实 index 摘要）跑出 cowagent system prompt 每轮固定成本 **20,623 tokens**（+ tools schema 3,861 = **24,484 tokens/轮**），其中 **Skills 元数据占 61.8%（12,754 tok）**、**四个 rule 文件全文占 24.0%（4,955 tok）**——两节合计 85.8%，是优化主战场；knowledge/index.md 摘要压缩 99.5%（131.9K→622 tok）设计验证成功；MCP 工具 top-k 注入模式可复用到 skills，预计 system prompt 可再降 ~52%。
> **来源**: 源码实证（/home/lzh/CowAgent/agent/prompt/builder.py + agent/protocol/agent.py + bridge/agent_initializer.py，2026-08-18 实跑）+ 真实工作空间文件（/home/lzh/cow 下 AGENT/USER/RULE/MEMORY.md、skills/ 104 个技能、knowledge/index.md）+ tiktoken cl100k_base 近似
> **关联**: [上下文 message 组装与 Token 经济学](2026-08-18-agent-context-message-assembly-token-economics.md)（本文是其"cowagent 实证"维度的量化深化）· [DeepSeek Harness 技术框架](../train/2026-08-13-deepseek-harness-technical-framework-analysis.md) · [Token 优化五技术](../methodology/2026-08-14-ai-pipeline-token-optimization-five-techniques-deep-analysis.md) · [上下文污染与重复执行](../methodology/2026-08-14-context-pollution-repeat-execution-analysis.md)

---

## 📑 目录

- [1. 结论概要（TL;DR）](#1-结论概要tldr)
- [2. 审计方法与口径](#2-审计方法与口径)
  - [2.1 真实构建链（非静态分析）](#21-真实构建链非静态分析)
  - [2.2 token 统计口径](#22-token-统计口径)
- [3. 总体结果：每轮固定成本结构](#3-总体结果每轮固定成本结构)
  - [3.1 system prompt 九节 token 占比](#31-system-prompt-九节-token-占比)
  - [3.2 tools schema 是隐藏的第二固定成本](#32-tools-schema-是隐藏的第二固定成本)
  - [3.3 固定成本占上下文预算比例](#33-固定成本占上下文预算比例)
- [4. Skills 节深挖：61.8% 从哪来](#4-skills-节深挖618-从哪来)
  - [4.1 节内构成：引导语 vs XML 列表](#41-节内构成引导语-vs-xml-列表)
  - [4.2 top-20 胖技能清单](#42-top-20-胖技能清单)
  - [4.3 condense 已生效的压缩](#43-condense-已生效的压缩)
- [5. ProjectCtx 节深挖：四个 rule 文件的真实成本](#5-projectctx-节深挖四个-rule-文件的真实成本)
- [6. knowledge index 摘要压缩验证](#6-knowledge-index-摘要压缩验证)
- [7. tools schema 明细与胖工具](#7-tools-schema-明细与胖工具)
- [8. 优化建议与量化收益测算](#8-优化建议与量化收益测算)
- [9. 缓存经济学视角的解读](#9-缓存经济学视角的解读)
- [10. 来源与验证](#10-来源与验证)
- [变更记录](#变更记录)

---

## 1. 结论概要（TL;DR）

1. **每轮固定成本 = 24,484 tokens**（system prompt 20,623 + tools schema 3,861），占 `agent_max_context_tokens=160K` 预算的 **15.3%**；对话历史可用空间约 119K（再预留 10% 回复）[来源: 本文 §3 实测，配置见 config.json]。这是**每一轮请求都支付的 prefill 成本**，与对话内容无关——本库 27 天 2.3B tokens 实测中，它是缓存未命中 58% 的最大贡献者之一 [来源: MEMORY.md 08-15 实测]。

2. **帕累托集中度极高**：Skills 节（61.8%）+ ProjectCtx 节（24.0%）两节合计 **85.8%**；其余 7 节合计仅 14.2%。优化主战场不在引导语、不在工具列表，而在 **skills 元数据** 与 **rule 文件全文** [来源: 本文 §3.1 表]。

3. **Skills 元数据是最大可降项**：104 个技能 XML 列表 12,269 tokens，平均 120 tok/技能；最胖 20 个技能占 ~46%。mckinsey-research 的 description 长达 1,640 字符（498 tok），industry-insight 889 字符（722 tok）。**MCP 工具已实现的"embedding 检索 top-k 注入"模式可原样复用到 skills**——若按 top-10 注入，skills 节从 12.5K 降至 ~1.5K tokens，system prompt 总量降 ~52% [来源: 本文 §4.2/§8]。

4. **两个已验证的设计**：① `_condense_skills_prompt` 已省 2,724 tok（17.9%）；② knowledge/index.md 摘要提取把 131,902 tokens 压到 622 tokens（**99.5% 压缩率**），且保住模块概览表——这是"索引注入"形态的教科书级实现 [来源: 本文 §4.3/§6]。

5. **MEMORY.md 是 ProjectCtx 节的最大单项**（2,343 tok，占该节 47%），实测 3,218 字符已超 5KB 管控上限——瘦身到 5KB 可省约 800 tok/轮；Workspace 节存在与 ProjectCtx 的**内容重复**（"AGENT.md 已加载"说明两处出现），是低垂的优化果实 [来源: 本文 §5]。

---

## 2. 审计方法与口径

### 2.1 真实构建链（非静态分析）

审计不是读代码估算，而是**完整模拟 agent_initializer 的初始化链并实际调用 PromptBuilder.build()**，所有输入都是真实数据：

```text
audit pipeline (mirrors bridge/agent_initializer.py):
  ToolManager.load_tools()            -> 14 builtin tools (web_search/evolution_undo skipped per real conditions)
  + MemorySearchTool/MemoryGetTool    -> memory tools (memory_manager as stub, only affects section existence)
  SkillManager(custom_dir=~/cow/skills) -> 104 skills real scan + build_skills_prompt()
  load_context_files(~/cow)           -> AGENT.md / USER.md / RULE.md / MEMORY.md real reads
  runtime_info                        -> dynamic time/model/channel (mirrors _get_runtime_info)
  PromptBuilder.build(...)            -> 41,164 chars / 20,623 tokens
```

**工具加载与真实环境完全一致**（跳过项：`web_search` 无 provider、`evolution_undo` 自进化禁用；MCP 0 个）[来源: 审计脚本实跑输出]。

**已知偏差（诚实披露）**：真实 `MemoryManager` 构造需 asyncio 事件循环驱动（`_sync_memory`），审计场景用 stub 替代——仅影响 Memory 节的"存在性"，不影响其文本内容（builder 只判工具名）；若真实环境 memory 系统初始化失败，Memory 节整体消失（-619 tok），但概率低（生产已长期运行）。

### 2.2 token 统计口径

DeepSeek 无公开离线 tokenizer，采用 **tiktoken cl100k_base 近似**（行业标准替代，对中英文混合文本误差约 ±10%）。所有占比按 token 计；字符数同时给出供交叉验证。**绝对值以近似值标注，相对占比的结构性结论不受 tokenizer 选择影响** [来源: 本文方法说明]。

---

## 3. 总体结果：每轮固定成本结构

### 3.1 system prompt 九节 token 占比

**实测**（2026-08-18 19:05 构建，41,164 chars / 20,623 tokens）：

| # | 节 | chars | tokens | 占比 | 性质 |
|:-:|:----|------:|-------:|-----:|:-----|
| 1 | 🔧 Tooling（工具系统） | 520 | 389 | 1.9% | 静态引导 + 工具一行摘要 |
| 2 | 🧩 Skills（技能系统） | 29,658 | **12,754** | **61.8%** | 引导语 + 104 技能 XML |
| 3 | 🧠 Memory（记忆系统） | 871 | 619 | 3.0% | 记忆检索/写入使用指南 |
| 3.5 | 📚 Knowledge（知识系统） | 2,329 | 1,061 | 5.1% | 自动写入规则 + index 摘要 |
| 4 | 📂 Workspace（工作空间） | 1,012 | 744 | 3.6% | 路径规则 + 已加载文件说明 |
| 5 | 👤 UserIdentity | 0 | 0 | 0% | 真实环境未传参（未启用） |
| 6 | 📋 ProjectCtx（项目上下文） | 6,617 | **4,955** | **24.0%** | AGENT/USER/RULE/MEMORY 全文 |
| 7 | ⚙️ Runtime（运行时信息） | 106 | 66 | 0.3% | 时间/模型/渠道（每轮动态） |
| 8 | 🌐 ResponseLang（回复语言） | 44 | 35 | 0.2% | 语言规则 |
| | **TOTAL** | **41,164** | **20,623** | **100%** | |

[来源: 审计脚本 `audit_system_prompt.py` 实跑输出，2026-08-18]

> **结构性结论**：① 第 2 节单节超其余 8 节总和（61.8% vs 38.2%）；② 第 2+6 节 = 85.8%；③ 动态内容（Runtime）仅 0.3%，被正确放在最末——**前缀静态化设计在 token 分配上是成立的**，问题不在结构而在 Skills 节的体积。

### 3.2 tools schema 是隐藏的第二固定成本

API 请求中 tools 参数（`{"name","description","input_schema"}`）由 14 个工具真实生成，**14,644 chars / 3,861 tokens**——等于 system prompt 的 18.7% [来源: 审计脚本 §8，工具列表见 §7]。

### 3.3 固定成本占上下文预算比例

| 项目 | tokens | 占 160K 预算 |
|:-----|-------:|:------------:|
| system prompt | 20,623 | 12.9% |
| tools schema | 3,861 | 2.4% |
| **每轮固定成本合计** | **24,484** | **15.3%** |
| 预留回复（10%） | ~16,000 | 10.0% |
| 对话历史可用空间 | ~119.5K | 74.7% |

[来源: config.json `agent_max_context_tokens=160000` + 本文 §3.1/§3.2 实测；`_trim_messages` 预留 10% 见 agent_stream.py L1852+]

> **推论**：fixed cost 15.3% 意味着每轮有 1/6.5 的 prefill 是"身份与目录"，不随任务变化。优化 fixed cost 是对**每一轮**的线性收益，杠杆率高于优化单轮对话内容。

---

## 4. Skills 节深挖：61.8% 从哪来

### 4.1 节内构成：引导语 vs XML 列表

| 子项 | tokens | 占 Skills 节 |
|:-----|-------:|:------------:|
| 固定引导语（扫描说明/使用规则） | 243 | 1.9% |
| **104 技能 XML 列表**（name+description+location） | **12,269** | **98.1%** |
| Skills 节合计 | 12,512 | 100% |

技能侧：104 个技能，平均 **120 tok/技能**；XML 格式（`<available_skills>` 包裹）与 description 全文是体积来源 [来源: 审计脚本 skills 深挖]。

### 4.2 top-20 胖技能清单

| 技能 | name+desc+loc tokens | description chars |
|:-----|---------------------:|------------------:|
| industry-insight | 722 | 889 |
| mckinsey-research | 498 | 1,640 |
| web-ppt-builder | 315 | 336 |
| weekly-report-generator | 297 | 766 |
| idea-vault | 297 | 320 |
| pipeline-constraint-enforcer | 296 | 304 |
| kb-effort-churn-diagnosis | 292 | 324 |
| codereview-mantis-security | 290 | 313 |
| pipeline-verification-loop | 266 | 327 |
| pipeline-expert-gate | 263 | 288 |
| system-guardian | 247 | 352 |
| light-venue-matching | 247 | 206 |
| light-frontend-design | 246 | 232 |
| pipeline-orchestrator | 244 | 325 |
| knowledge-doc-writer | 240 | 954 |
| patent-disclosure-writer | 229 | 212 |
| server-competitor-analysis | 223 | 250 |
| xlsx | 219 | 941 |
| light-slides | 219 | 173 |
| light-orchestrator | 209 | 193 |

[来源: 审计脚本实跑。top-20 合计约 5.7K tokens，占 Skills 节 ~46%]

> **根因**：description 不是"一行摘要"而是"营销文案"。mckinsey-research 1,640 chars、knowledge-doc-writer 954、xlsx 941、industry-insight 889——**description 越长，每轮 61.8% 的固定成本越高，但模型每轮真正会用到的技能通常只有 1-3 个**。这是"为可能用到付费"的典型反例。

### 4.3 condense 已生效的压缩

`_condense_skills_prompt`（builder.py L287）实测收益：

| 阶段 | tokens | 节省 |
|:-----|-------:|-----:|
| raw skills prompt | 15,236 | — |
| condensed（去 base_dir + location 相对化 + 空行折叠） | 12,512 | **2,724 tok（17.9%）** |

[来源: 审计脚本实跑]

> 已生效设计确认有效，但 17.9% 只是"格式级"压缩——**结构性压缩（按需注入）还没做**。

---

## 5. ProjectCtx 节深挖：四个 rule 文件的真实成本

| 文件 | chars | tokens | 占该节 |
|:-----|------:|-------:|:------:|
| AGENT.md | 774 | 684 | 13.8% |
| USER.md | 713 | 631 | 12.7% |
| RULE.md | 1,698 | 1,136 | 22.9% |
| **MEMORY.md** | **3,218** | **2,343** | **47.3%** |
| 节引导语 | ~214 | ~161 | 3.2% |
| **ProjectCtx 合计** | **6,617** | **4,955** | 100% |

[来源: 审计脚本 §9 实跑]

**三个发现**：

1. **MEMORY.md 是最大单项且已超限**：2,343 tok（占全 system prompt 11.4%），实测 3,218 chars 超 5KB 管控上限（MEMORY.md 自述 7.4KB）——瘦身到 5KB 约省 800 tok/轮 [来源: MEMORY.md 管控规则 + 实测]。

2. **Workspace 节与 ProjectCtx 节内容重复**：Workspace 节（744 tok）里"以下文件已自动加载：AGENT.md/USER.md/RULE.md/MEMORY.md"的清单说明，与 ProjectCtx 节（紧接着）的全文注入重复——**同一信息两处出现**，可合并省约 300-400 tok [来源: builder.py §4 与 §6 文本对比]。

3. **AGENT.md 中的 USER.md 片段重复**：AGENT.md 内嵌"协作模式(与用户验证有效)"等用户画像信息，与 USER.md 全文有语义重叠——属规则文件设计层面的冗余，非 builder 问题。

---

## 6. knowledge index 摘要压缩验证

`_extract_knowledge_index_summary`（builder.py L485）声称"245KB→4KB"，实测更极端：

| 项 | chars | tokens |
|:---|------:|-------:|
| knowledge/index.md 原始 | 312,401 | **131,902** |
| 提取后（模块一览表 + 二级分组标题） | 1,656 | **622** |
| **压缩率** | **0.5% 保留** | **0.5% 保留（99.5% 压缩）** |

[来源: 审计脚本 §10 实跑]

> **设计验证成功**：131.9K tokens 的知识库目录被压到 622 tokens 且保留模块结构概览（7 模块 × 二级分组），Knowledge 节总成本仅 1,061 tok（5.1%）——这是"**元数据/索引注入形态**"（既有专题 §4.3 三形态）的量化样板，**skills 节应当照此办理**。

---

## 7. tools schema 明细与胖工具

14 个工具 schema 合计 3,861 tokens，top-10 最胖：

| 工具 | tokens |
|:-----|-------:|
| scheduler | 630 |
| browser | 555 |
| search_files | 459 |
| bash | 365 |
| read | 321 |
| env_config | 306 |
| edit | 258 |
| memory_get | 159 |
| memory_search | 153 |
| ls | 137 |

[来源: 审计脚本 §8。完整 14 工具 = read/write/edit/bash/ls/send/search_files/env_config/scheduler/web_fetch/vision/browser/memory_search/memory_get]

> 工具 schema 已实现 MCP 动态 top-k 注入（`_select_tools_for_injection`，>20 时 embedding 检索 top-10）；内置 14 个工具全量注入（3,861 tok）尚可接受，但 scheduler（630）/browser（555）的 params 描述偏长，有压缩空间。

---

## 8. 优化建议与量化收益测算

按"每轮固定成本 24,484 tokens"基线测算（收益 = 每轮节省，线性放大到全生命周期）：

| # | 优化动作 | 机制 | 每轮节省 | 降幅 | 成本 |
|:-:|:---------|:-----|---------:|:----:|:----:|
| 1 | **skills top-k 按需注入**（复用 MCP 模式：embedding 检索 top-10 技能，其余只留 name 一行） | `_select_tools_for_injection` 泛化到 skills | ~10.7K | system prompt **-52%** | 中（需 embedding provider） |
| 2 | **skills description 截断**（≤200 chars，保留触发关键词；全文仍可 read） | `_condense_skills_prompt` 加截断逻辑 | ~3-4K | skills 节 -25~30% | 低 |
| 3 | **MEMORY.md 瘦身**（7.4KB→5KB，历史进 memory.history.md） | 人工治理（仅人工维护） | ~800 | -3.9% | 低 |
| 4 | **Workspace 节去重**（"已加载文件"说明与 ProjectCtx 合并） | builder.py §4 精简 | ~300-400 | -1.5~2% | 低 |
| 5 | **tools schema 描述压缩**（scheduler/browser params 精简） | 工具类 params 治理 | ~300-500 | -1.5~2.5% | 低 |
| 6 | **胖技能 desc 专项治理**（top-6：industry-insight/mckinsey-research/xlsx/knowledge-doc-writer/weekly-report-generator/system-guardian） | SKILL.md frontmatter 改写 | ~800 | -4% | 低 |

**组合测算**：方案 1+2 叠加（top-k 注入 + 描述截断）可把 system prompt 从 20.6K 降至 ~8-9K（-57%），每轮固定成本从 24.5K 降至 ~12-13K（-48%）。按本库 27 天 2.3B tokens 规模粗估，**全程可省 ~0.9-1.1B tokens 的 prefill**（约 40% 总量，含历史已发生的部分按同口径折算）[来源: MEMORY.md 08-15 实测 2.3B/27 天]。

> **优先级建议**：方案 2（description 截断）是最高性价比——纯文本处理、零架构改动、不动技能可用性（全文仍走 read JIT），先做；方案 1（top-k 注入）收益最大但需评估"技能召回率"对行为的影响（漏召回=技能不被使用），建议先做方案 2 实测降幅再决策。

---

## 9. 缓存经济学视角的解读

结合既有专题的缓存经济学（命中 0.02 vs 未命中 1 元/百万 token，50 倍差）[来源: 2026-08-13 harness 分析 §4.2]：

1. **当前结构缓存友好**：8 节顺序固定，静态内容（1-6 节）在前，动态内容（7-8 节 + 历史）在后；skills 变化频率低（安装时变），不会频繁击穿缓存。实测验证了"顺序即缓存设计"在 token 分配上成立 [来源: 本文 §3.1]。

2. **Skills 节是缓存的双刃剑**：体积大（12.7K）但稳定（前缀友好）——它是"高命中率的大前缀"。**任何技能 description 的修改都会使第 2 节之后全部缓存失效**：104 个技能中任一 frontmatter 变动 → 前缀失效 → 后续所有轮次 miss。这是"静态内容也要控制体积"的缓存维度理由 [来源: 本文 4.x + 缓存机制推导]。

3. **动态时间放最末是正确的**：Runtime 节每轮变化（时间戳），但位于第 7 节末尾，失效范围最小（仅第 7-8 节）——若时间戳放第 1 节，则每轮全前缀 miss。**当前布局与缓存定律完全一致** [来源: 本文 §3.1 + 缓存推导]。

---

## 10. 来源与验证

**源码实证（最高可信，实跑）**：
1. `/home/lzh/CowAgent/agent/prompt/builder.py` — 8 节组装顺序、`_condense_skills_prompt`、`_extract_knowledge_index_summary`
2. `/home/lzh/CowAgent/bridge/agent_initializer.py` — 初始化链（工具/技能/记忆/runtime）
3. `/home/lzh/CowAgent/agent/protocol/agent.py` — `get_full_system_prompt`、`_get_model_context_window`
4. `/home/lzh/CowAgent/agent/protocol/agent_stream.py` — `_trim_messages` 10% 预留、tools_schema 组装
5. `/home/lzh/CowAgent/config.json` — model=deepseek-v4-flash、agent_max_context_tokens=160000、channel_type=feishu
6. 审计脚本实跑输出 — `tmp/audit_system_prompt.py`（构建链 + tiktoken 统计，2026-08-18 19:05）

**真实数据输入**：/home/lzh/cow 下 AGENT.md（774 chars）/USER.md（713）/RULE.md（1,698）/MEMORY.md（3,218）；skills/ 104 个技能；knowledge/index.md（312,401 chars）。

**方法与口径**：tiktoken cl100k_base 近似 DeepSeek tokenizer（±10% 误差标注）；MemoryManager 以 stub 替代（仅影响 Memory 节存在性，不影响文本）；`_build_memory_section` 与 `_build_skills_section` 全部走真实代码路径。

**分析性结论标注**：§8 组合收益测算（-52%/-48%、全程 0.9-1.1B tokens）为基于实测基线的**推算**（假设 top-k 召回不影响任务质量）；§9.2"任何 skills 修改导致前缀失效"为缓存机制推导；均非独立实验验证。

**本库既有专题（交叉引用）**：
- [上下文 message 组装与 Token 经济学](2026-08-18-agent-context-message-assembly-token-economics.md) — 本文姊妹篇（四 Agent 机制对比/时序定律/缓存经济学）
- [DeepSeek Harness 技术框架](../train/2026-08-13-deepseek-harness-technical-framework-analysis.md) — 缓存定价 50 倍差
- [Token 优化五技术](../methodology/2026-08-14-ai-pipeline-token-optimization-five-techniques-deep-analysis.md) — token 成本工程
- [上下文污染与重复执行](../methodology/2026-08-14-context-pollution-repeat-execution-analysis.md) — 注意力稀释机制

---

## 变更记录

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-18 | v1.0 | 首次创建：真实构建链 token 拆解审计（system prompt 20,623 + tools schema 3,861 = 24,484 tok/轮）；九节占比（Skills 61.8%/ProjectCtx 24.0%）；skills 内部构成与 top-20 胖技能；MEMORY.md 超限实证；index 摘要 99.5% 压缩验证；六项优化建议与收益测算 |
