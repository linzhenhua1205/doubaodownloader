# 从模型到 Harness：WorkBuddy Agent 产品化深度分析

> **类型**: 深度分析 | **日期**: 2026-08-05 | **来源**: 《从模型到Harness：WorkBuddy如何把Agent做成可用产品》（作者 Anne，WorkBuddy 策略产品经理；腾讯新闻转载亿欧网 2026-07-22，原文公众号"Fook的AI记事铺"）
> **关联**: `2026-08-05-five-engineering-claude-code-trae-deep-analysis.md`（五工程横向对比姊妹篇）| `2026-08-03-agent-composition-and-coding-agent-comparison.md`（六层模型）| `2026-08-04-graph-engineering-deep-analysis.md`（编排范式）

---

## 0. 一句话结论

> **WorkBuddy 用"产品抽象"回答了同一个问题：模型是核心推理引擎，但 Agent 的可靠性来自模型之外的工程系统——上下文决定"看到什么"，Harness 决定"能做什么、做对了没"，Loop 决定"怎么长期持续"。其中最有价值的三个设计决策：Memory 只存陈述性记忆（做事方法一律进 Skill）、Harness 按"前馈/反馈 × 计算型/推断型"二维组织、以及"AI 自治度上限"与"Harnessability"两个判定框架。**

本文的价值不在新概念（Context/Harness/Loop 已是共识），而在**一个产品团队把工程原则落地为可执行机制的完整过程**——尤其 Memory 准入判断、熵管理、迭代层这三处是多数工程视角文章（Claude Code/Trae 官方文档）没有展开的盲区。

---

## 1. 原文信息与可信度评估

| 维度 | 评估 |
|:-----|:-----|
| 作者 | Anne，WorkBuddy 策略产品经理，负责研发与办公场景 Agent 的上下文策略设计与落地 |
| 发布渠道 | 公众号"Fook的AI记事铺"→ 腾讯新闻转载（亿欧网，腾讯云 AI 智能体示范伙伴，文末附企业版推广） |
| 性质 | **产品团队自述**（一手，但非中立）——机制描述可信，效果数据缺失（全文无 WorkBuddy 自身量化指标，唯一数字是引用的 OpenAI 实验"100 万行代码"） |
| 引用源 | OpenAI Codex 实验 / Anthropic 两篇长任务 Harness 论文 / LangChain（Ralph Loop）/ Karpathy《Software Is Changing (Again)》/ Addy Osmani / Chad Fowler《Relocating Rigor》——均为真实公开来源 ✅ |
| 与已归档对比 | 与 `2026-08-03` 六层模型、`2026-08-05` 五工程文档交叉验证一致；WorkBuddy 描述的能力（Hooks/Skills/Sub-agents/渐进式加载/Memory 分层）与 Claude Code 官方文档机制同构，无矛盾 |

**⚠️ 诚实标注**：本文作为深度分析，事实判断以原文机制描述为据；原文中"亿欧已率先完成 WorkBuddy 企业版全场景落地验证"为商业推广内容，不纳入分析；WorkBuddy 相关效果量化数据（如其他文章流传的"成功率 72%→90%"）本文未采用，因其来源为第三方公众号且无方法论披露。

---

## 2. 核心内容还原（原文五部分）

### 2.1 模型抽象：两条约束决定一切

原文把模型抽象为一个无状态函数：

```text
output = model(system_prompt + tools + history + other_context + user_instruction)
```

> 注：原文公式为中文表达，此处工程化改写；等价含义 = 模型(系统提示词+工具+会话历史+其他上下文+用户指令)

两条约束：

1. **模型无状态** → 产品可以有状态（对话历史/Memory/进度由产品侧保存并注入）；
2. **知识截止训练日期** → 实时信息需工具查询后放入上下文。

> 推论：持有 API Key、发起请求、修改数据的是 **Agent 不是模型**——权限、审批、参数校验、审计日志必须在模型外部的工程机制执行。这是 Harness 存在的最硬理由。

### 2.2 能力层四概念（用户可感知的四个形态）

| 概念 | 核心问题 | 主要消费者 | 关键点 |
|:-----|:---------|:-----------|:-------|
| 工具调用 | 模型怎么请求执行动作？ | 模型+Agent | 模型生成结构化请求，Agent 校验/执行/回传 |
| MCP | 外部系统怎么标准化接入？ | Agent/Server | Resources（Agent 驱动）/Tools（模型驱动）/Prompts（用户驱动）三原语；2026 扩展 MCP Apps（交互式 UI 分流，不进上下文） |
| Skill | 一类任务该按什么流程做？ | Agent | 说明+步骤+脚本+命令+**失败分支+完成标准** |
| Plugin | 怎么把一组能力打包分发？ | 用户/团队/产品 | MCP+Skills+Rules+Hooks+Assets 的组合与分发单位 |

**形态选择判据**：能力边界、更新频率、权限风险、上下文成本、执行延迟、跨产品复用价值——"没有一种形态对所有能力最优"。

### 2.3 Context Engineering：模型这一刻该看到什么

**五类动作**（原文强调精确含义，这是全文最精炼的定义）：

1. **写入**（Write）：目标/规则/环境/任务状态显式写进上下文，别让模型猜；
2. **选择**（Select）：从在手候选信息里只挑当前需要的（filter）；
3. **检索**（Retrieve）：不在手的按需捞进来（pull）；
4. **压缩**（Compress）：长内容外置，只留结论与证据位置，清理过期/重复；
5. **隔离**（Isolate）：独立会话/Sub-agent 处理旁支，只带结果回主线。

**Prompt Cache 规则**（前缀稳定性）：System Prompt/基础工具/长期规则放前面且**保持内容与顺序稳定**；对话历史追加不修改；动态内容追加到后面；工具/Skill 按需加载；**只在压缩或纠错时才接受缓存重算**。缓存命中率正在成为被普遍关注的工程指标。

**渐进式加载**：工具定义随能力增多也必须做上下文管理——先暴露名称+简要描述，任务需要时再加载完整说明；工具结果设截断策略（截断时**明确告知"结果未完整"+总量+截断位置+继续读取方法**）；错误不只返回堆栈，还要返回**失败原因+可修正参数+是否可重试+建议下一步**。意图识别是渐进式加载的前置环节（先选对方向，再按需展开）。

### 2.4 Memory：让正确的过去在正确的时候重现

**三类记忆材料**：聊天历史（可作 RAG 源）/ 工作空间工作记忆（项目进度）/ 长期记忆（默认代入上下文）。

**核心设计决策——准入判断**：记忆系统最关键的不是"存什么"，而是**哪些历史信息有资格继续影响未来任务**。

**五类长期记忆**（陈述性 declarative）：

| 类型 | 存什么 | 系统中的作用 |
|:-----|:-------|:-------------|
| 稳定事实 | 去情境化事实/长期偏好/默认假设 | 长期推理前提 |
| 用户知识背景 | 专业背景/知识水平 | 调节解释深度，不改变事实结论 |
| 行为信号 | 多次交互观察到的稳定模式 | 交互策略调节信号（比明确偏好更谨慎） |
| 表达偏好 | 表达方式稳定偏好 | 控制"怎么说"，不影响事实 |
| 会话延续信息 | 目标/决策/进度/未完成项 | 延续讨论和任务 |

**排除 Procedural Memory（程序性记忆）——本文最锋利的决策**：做事方法一旦作为长期记忆注入，会局部经验误升为通用策略、干扰模型按证据选路径、隐性改写 Agent 行为（接近动态 System Prompt 却无版本/评测/审批/回滚）、降低泛化。**结论：用户事实和历史状态进 Memory；经过验证的工作方法保存为 Skill（可版本化、可评审、可测试、可回滚、按需加载）。**

**作用域分层**（作用域越大，晋升门槛越高）：当前轮 → 会话/Thread → 项目/Workspace → 用户级 → 团队/组织。

**注入分阶段**：冷启动只注入少量高置信摘要 → 请求理解时按 query 激活候选 memory cards（保留来源与置信）→ 执行中需要证据时回查原始会话/文件 → 任务收尾时提取候选记忆做去重、冲突检查、作用域判定。

### 2.5 Harness Engineering：引导、约束与整合

**词源**：马具 → 三类能力——**驾驭（Steer）/ 约束（Constrain）/ 整合（Integrate）**。三者缺一不可：只有引导没有约束→执行不该执行的动作；只有约束没有反馈→出错无法修正；工具多缺编排→长任务难以稳定完成。

**两层结构**（三个同心圆）：核心是模型，外圈是构建者 harness（System Prompt/工具/编排），最外圈是使用者 harness（针对自己系统的前馈/反馈配置）。

**业界三家实践**（原文引用的对照基准）：

- **OpenAI Codex**：3 人小组 5 个月 100 万行代码/1500 PR；AGENTS.md 目录入口+详细知识结构化进 docs；linter+结构测试自动化检查；后台周期性任务扫描代码漂移自动建重构 PR；"Agent 卡住时当作信号——找出缺了什么反哺回仓库，总是让 Codex 自己写这个修复"
- **Anthropic 第一篇**（Effective harnesses for long-running agents）：长任务两种典型失败（一次承担过多/过早判定完成）；200+ 条功能清单 JSON 逐条 pass/fail、禁止删条目降标准；init.sh 统一启动；浏览器自动化端到端验证；进度文件+Git 历史交接恢复
- **Anthropic 第二篇**（Harness design for long-running application development）：**接近上下文上限时模型会降低完成标准；自我评估不可靠**（倾向正面结论）；借鉴 GAN 对抗评估——Planner（展开规格不定实现）/ Generator（逐功能实现+git）/ **Evaluator（独立验收 Agent，Playwright 像真实用户操作，bug 定位到行号打回）**
- **LangChain**：Agent = Model + Harness（最宽定义）；持久状态/给 Agent 一台计算机/自我验证；**Context Rot**（Compaction/Tool Call Offloading/Skills 渐进式加载）；Ralph Loop（Hook 拦截提前结束信号，新上下文重新注入目标）；**模型与 Harness 共同进化——评估对象是"模型+Harness"组合**

**WorkBuddy 五层 Harness**（构建者视角，控制系统隐喻）：

1. **运行环境层**：文件系统/Shell/Sandbox/Browser/MCP/权限边界/Allowlist-denylist（用户感知不到但缺一不可）
2. **引导层（Feedforward）**：执行前提供信息提高首次正确率——项目上下文（早期模型不会主动探索代码库）/环境上下文/规则风格/工具使用规则（改文件前先读、路径不明先搜、长任务先拆 Todo）/Skills/Prompt Cache 结构
3. **反馈层（Feedback）**：执行后验证——工具结果带可纠正信息（文件未找到提示搜索路径、编辑失败提示重读、权限不足提示确认、命令报错返回完整 stderr）；**编辑前时间戳校验**（上次读取时间 vs 文件最后修改时间，读取后被改过则拒绝写入）；外部验证信号（lint/类型检查/测试/构建）；Audit log
4. **编排层**：渐进式加载/意图识别路由/多模型路由/Teams 多 Agent 协作/并行工具调用
5. **迭代层**：Harness 自身持续调整——随模型能力提升精简上下文（新模型会主动 Glob/Grep 探索后初始项目概况可减少）、根据新问题加约束、针对模型适配工具、根据重复反馈加机制（一次失败可能是偶发，同类失败多次或高风险才调整；新增机制要评估副作用）

**前馈/反馈 × 计算型/推断型 二维分类**：

- 计算型控制 = 确定性程序（LSP/类型检查/linter/单测/结构测试/依赖扫描/codemod）：快、便宜、可重复
- 推断型控制 = 模型语义判断（Review Agent/架构审查/AI judge/设计评估）：覆盖"是否过度设计/误解需求"类问题，慢、贵、不确定
- **原则：能用计算型信号解决的优先交给确定性程序；需要语义判断的再交给审查 Agent**

**使用者视角四类组件**（借 OpenAI Codex 框架）：上下文工程（分层规则文件+OpenSpec+Skills+Slash 命令）/ 架构约束（规则变可执行检查：本地检查+Git Hooks+CI 门禁+审查 Agent）/ 反馈循环（Post-edit checkpoint+CI+/team:mr 工作流+Dogfood Skill+Agent Browser）/ **熵管理 Garbage Collection**（周期性扫描规则/代码/运行状态漂移：文档与代码一致性、历史违例、重复实现、失效文档、过期依赖；运行时健康传感器：延迟/错误率/SLO/日志异常）

### 2.6 Loop Engineering：任务如何跨时间继续

**四层工程定位**（原文表格，精确）：

| 层次 | 核心问题 | 简单例子 |
|:-----|:---------|:---------|
| Prompt Engineering | 本次请求应如何表达？ | 写清目标、格式、约束 |
| Context Engineering | 这一次决策前模型该看什么？ | 加载文件/工具/历史/记忆 |
| Harness Engineering | Agent 如何被引导、约束、观测、验证、纠正？ | 规则/沙箱/审批/测试/日志/编排 |
| Loop Engineering | 任务如何被触发、流转、验收、继续、停止？ | 定时任务/工作树/子 Agent/记忆/反馈闭环 |

**Loop 至少需要的组件**：触发器 / 独立执行环境（Isolated Workspace/Worktree）/ Skills / Tools-Connectors-MCP / Sub-agents / Memory-Durable Artifacts / Sensors-Evals / 停止条件-Budget。

**Goal ≠ Loop**：长期目标只定义"去哪里/还剩什么"，Loop 还需要触发器、执行环境、工具、验证信号、停止条件——"一个只会保存目标的功能是 Loop 的状态组件，不是完整循环"。

**Loop 不会自动解决**：不会自动产生正确目标（目标错时循环更快朝错方向跑）；不会自动产生可信验收标准（Generator 与 Evaluator 共享同一误解 → "错的实现+全部通过的测试"）；不会承担责任；不会替代工程师形成判断。

### 2.7 未解决的问题（原文的诚实边界）

1. **功能和业务正确性验证缺口**：PRD 覆盖单项功能不覆盖组合行为（"已置顶的会话能不能归档？"）；实现与测试共享同一误解；部分业务正确性无可计算判定标准；业务错误成本高 → **AI 自治度上限表**：一次性脚本/内部工具=高，公开 API/跨系统=中，核心业务逻辑（支付/风控/订单）=低
2. **Harnessability**（代码库可驾驭性）：老系统更难建 Harness 四原因（结构不清/历史违例多/复杂度高/可观测性弱）；务实路径=先清循环依赖和模块边界+补关键链路测试日志指标看板→选结构清晰价值高的子模块验证→先约束新增再处理存量
3. **案例适用边界**：主要案例来自模型厂商和框架团队，实验条件/可复现细节/业务验证方式不完全公开
4. **AI 推动技术方案标准化**：选型会考虑"是否便于 AI 理解/修改/验证"；可能出现"Harness 模板"（围绕常见服务拓扑预组结构约定+技术栈+指引+传感器），WorkBuddy Service Template 已在做
5. **Harness 需要持续投入**：OpenAI 原文"this isn't something you can jump into for quick results"；与 Chad Fowler《Relocating Rigor》一致——工程严谨度从代码编写转移到环境、反馈回路、控制系统设计
6. **人仍负责主线**：Addy Osmani "The danger is stopping having an opinion when loops run autonomously"

---

## 3. 深度分析 A：三产品对照（WorkBuddy × Claude Code × Trae）

与 `2026-08-05-five-engineering-claude-code-trae-deep-analysis.md` 的五工程框架对接，本文补全了 WorkBuddy 的纵切面：

| 工程维度 | WorkBuddy（本文） | Claude Code | Trae |
|:---------|:------------------|:-------------|:------|
| **上下文组织** | 五动作（写/选/检/压/隔）+ Prompt Cache 前缀稳定规则 + 渐进式加载 + 意图识别前置 | @引用 + 四层压缩策略 + prompt caching + /memory | 选中片段引用 + 记忆文件化 + Codebase Indexing |
| **Memory 设计** | **最完整**：五类陈述性记忆 + 作用域五级 + 准入判断 + 排除程序性记忆 + 分阶段注入 | /memory 轻量记忆 + CLAUDE.md 项目记忆（无分级论证） | user_profile.md / project_memory.md 自动维护（无准入判断概念） |
| **Harness 结构** | 五层（环境/引导/反馈/编排/迭代）+ 前馈反馈二维 + 计算型/推断型分类 | 7 类 Hooks + Subagents + Background Tasks + Checkpoints（工程能力强，但无"迭代层"显式化） | 六类 Hooks + Subagent（含默认 Search）+ 沙箱（2026 已补齐，见五工程文档修订） |
| **Loop 实现** | 组件清单（触发器/工作树/Skills/Sensors/停止条件）+ Goal≠Loop 辨析 + 依赖安全更新示例 | Long Horizon 150 轮 + Background Tasks + Checkpoints（运行级） | 开发流水线 PRD→方案→代码→预览 + 确认点（流程级） |
| **验证体系** | Planner/Generator/Evaluator 三角色 + 计算型优先原则 + 自治度上限表 | Ralph Loop（LangChain 提出，Claude Code 场景化的提前结束拦截） | Spec checklist.md 逐条核对 |
| **独有概念** | 熵管理（GC）、Harnessability、迭代层、Memory 准入判断 | Context Rot 应对（Compaction/Offloading） | — |

**结论**：三家对"上下文/Harness/Loop"的工程认知高度收敛（这是领域成熟的标志），差异在**抽象层级和显式化程度**——WorkBuddy 作为产品，把 Claude Code 隐式运行的机制（时间戳校验、工具结果截断协议、缓存前缀稳定）显式化为可执行的产品规则；而 Claude Code 作为 IDE 深度嵌入工具，Harness 能力（7 类 Hooks）比 WorkBuddy 文章描述的更细。**WorkBuddy 真正领先的是 Memory 设计和判定框架（§4），Claude Code 领先的是运行深度（Background Tasks 前台并发）。**

---

## 4. 深度分析 B：WorkBuddy 七个独特设计洞察

### 4.1 Memory 准入判断：记忆系统的心脏

多数记忆系统文章讲"怎么存"，本文反问"**什么有资格存**"。把"准入判断"设为记忆系统的核心环节，直接对应本工作空间存储规则（RULE.md 按变化频率分档：日更→memory/、月更→MEMORY.md、低频重要→知识库）——同构验证 ✅。关键洞察：**记忆是隐式权重，比提示词更危险**——因为它默认代入、用户无感、难以审计。

### 4.2 排除 Procedural Memory 的论证（全文最锋利）

"做事方法进 Memory"表面方便，实则是**绕过 Skill 治理体系的隐形提示词**（无版本/评测/审批/回滚）。这个决策与 Claude Code 的 CLAUDE.md vs Skills 分工、与本工作空间"方法论固化进 skills/、事实进 knowledge/"完全同向。**推论：任何 Agent 系统都应把"怎么做"与"是什么"分开治理——前者必须有版本控制和验证，后者可以有置信度衰减。**

### 4.3 前馈/反馈 × 计算型/推断型二维

这是对"验证"问题的 MECE 切分：前馈提高首次正确率（省 token），反馈让错误在人工审查前自愈（省人工）。计算型 vs 推断型回答"用程序还是用模型验证"。**原则"能用计算型信号解决的优先交给确定性程序"** = 第一性原理（确定性程序便宜×1000 且无幻觉），与本工作空间"约束脚本化""check_md_format 自动化"同构 ✅。

### 4.4 迭代层：Harness 是活系统

五层中"迭代层"最容易被忽略：Harness 不是一次配置，要随模型能力提升**精简**（新模型会主动探索 → 减少初始上下文）、随新问题**增约束**、按重复反馈**加机制**——且用证据门槛（一次失败是偶发，同类多次或高风险才调）和副作用评估（更严审批↔更多打断）约束迭代节奏。这与我方"迭代打磨"准则和"约束体系四层防治"呼应。

### 4.5 熵管理（Garbage Collection）

反馈循环治"本次执行"，熵管理治"跨任务积累的漂移"——规则/代码/运行状态会自然腐化。四类传感器（文档与代码一致性、历史违例、重复实现/失效文档/过期依赖、运行时健康 SLO）。这是工程视角文章少有的**治理维度**，与本工作空间"系统腐化驱动力=认知局部优先性，防治四层"同构 ✅。

### 4.6 AI 自治度上限表 + Harnessability

两个判定框架提供了可操作的决策工具：

- **自治度上限**：一次脚本=高 / 公开 API=中 / 核心业务=低——"AI 的自治程度需随风险提高而降低"，把"该不该让 AI 干"从感觉变成查表
- **Harnessability 四问**（判断工作是否适合 AI）：有无明确完成标准？结果能否验证？失败是否易发现可回滚代价可控？是否重复发生值得建 Harness？——这四问直接可用

### 4.7 "接近上下文上限模型会降低完成标准"（Anthropic 第二篇）

与"过早判定完成"是长任务两大隐性失败。机制：模型在窗口将满时倾向快速收尾（可能是注意力稀释+压缩压力的行为学后果）。应对：显式任务清单状态+Evaluator 独立验收。**对本工作空间的启示：Agent 长任务应设"上下文水位警戒"（如 95% 触发 compaction，与已有 context compaction 机制一致）。**

---

## 5. 深度分析 C：产品视角 vs 工程视角

| 维度 | 产品视角（本文 WorkBuddy） | 工程视角（Claude Code/Trae 官方文档） |
|:-----|:---------------------------|:--------------------------------------|
| 抽象对象 | 用户可感知的能力形态（Tool/Skill/Plugin）与机制（前馈/反馈） | 运行机制（Hooks/Checkpoints/Subagents）与配置项 |
| 组织方式 | 同心圆（构建者/使用者）+ 五层 + 四类组件 | 能力清单 + 配置参考 |
| 验证语言 | 判定框架（自治度表/Harnessability 四问） | 参数与日志 |
| 叙事重心 | "为什么这样设计"（决策论证） | "能做什么"（功能枚举） |
| 盲区 | 运行深度细节（Background Tasks 并发、Checkpoint 粒度） | Memory 治理、熵管理、迭代层的显式化 |

**结论**：产品视角的价值在**决策论证**（为什么 Memory 排除程序性记忆、为什么计算型优先、为什么 Harness 要迭代），工程视角的价值在**运行细节**（怎么配、怎么调）。对技术决策者，前者定方向，后者定实现——两者互补，不可替代。

---

## 6. 对本工作空间与服务器 AI 基础设施的借鉴

### 6.1 直接可落地的五条

1. **Memory 准入判断显式化**：本工作空间已有按频率分档的存储规则（✅ 同构），可补充"准入检查单"：这条信息会影响未来任务吗？置信度多少？作用域哪一级？——与 `light-memory-pm` 技能合并
2. **做事方法一律 Skill，事实才进知识**：已符合（方法论→skills/，事实→knowledge/），WorkBuddy 论证可作为该纪律的 SSOT 引用
3. **计算型优先原则**：凡能用脚本/检查器验证的（格式/链接/索引完整性），绝不依赖模型二次判断——已符合（check_md_format/kb-index-check.py）
4. **上下文水位警戒**：长任务设 95% 压缩阈值 + 显式任务状态清单（todo），防"接近上限降低完成标准"
5. **熵管理周期化**：文档与代码一致性、历史违例、失效链接的周期性扫描——weekly-report/monthly-report 已有雏形，可加"知识库漂移传感器"

### 6.2 与服务器 AI 基础设施的映射

- **Harness = 服务器管理平面**：引导层≈配置基线/固件三线，反馈层≈RAS 传感器/告警，约束层≈权限/安全边界，编排层≈集群调度——"Agent 的 Harness 工程"与"超节点的管控平面"是同一套控制论思想（前馈+反馈+约束+编排）在不同尺度上的实例
- **AI 自治度上限表 → 运维自治分级**：一次性巡检脚本=高自治，配置变更=中（需审批），生产故障自愈（支付级风险）=低——可直接映射为超节点 AI O&M 的权限分级
- **Harnessability → 老系统改造优先级**：先清循环依赖+补可观测性，再上 AI 治理——与现有 POC 分级（L0→L3）方法一致

---

## 7. 可证伪预测与行动项

| # | 预测/行动 | 证伪条件 | 时间窗 |
|:-:|:----------|:---------|:-------|
| P1 | 更多产品会跟进"Memory 排除程序性记忆"（做事方法入 Skill 体系） | 主流 Agent 产品将程序性内容注入长期记忆且无版本治理，仍被证明更优 | 2026Q4 |
| P2 | "缓存命中率"成为 Agent 产品公开的工程指标（类似 GPU 利用率） | 2027 年前无主流产品公开该指标 | 2027H1 |
| P3 | Harness 模板化（Service Template）成为企业 Agent 落地标配 | 无厂商跟进预组 harness 模板 | 2027H1 |
| P4 | Evaluator 独立验收成为长任务 Agent 默认架构（对抗评估扩散） | 主流产品仍依赖自评+人工 | 2027H1 |
| A1 | 本工作空间落地"上下文水位警戒"（长任务 95% 压缩阈值+显式 todo） | — | 2 周内 |
| A2 | 补充"Memory 准入检查单"到 light-memory-pm 技能 | — | 2 周内 |
| A3 | 把自治度上限表映射为超节点 AI O&M 权限分级草案 | — | 1 月内 |

---

## 8. 局限性与诚实标注

1. **单一来源自述**：机制描述来自产品团队自述，无第三方中立验证；WorkBuddy 自身效果数据全文缺失
2. **商业推广成分**：亿欧为腾讯云示范伙伴，文末推广语已识别并排除
3. **案例外推限制**：OpenAI/Anthropic 实验案例来自引用，实验条件不完全公开（原文自己也承认）
4. **领域边界**：文章偏编码/办公 Agent，对服务器基础设施 Agent（RAS/运维）的适用性为本文 §6.2 的第一性原理外推（⚠️ 分级：推断），非原文内容
5. **交叉验证状态**：机制描述与 Claude Code/Trae 官方文档、六层模型文档一致（✅ 已验证）；"1300 万 DAU"等第三方流传数字未采信（⚠️ 未验证）

---

## 参考资料

1. Anne.《从模型到Harness：WorkBuddy如何把Agent做成可用产品》. 亿欧网/腾讯新闻, 2026-07-22. [原文链接](https://news.qq.com/rain/a/20260722A025CH00)
2. Anthropic. *Effective harnesses for long-running agents*（长任务两种失败/功能清单 JSON/跨会话交接）
3. Anthropic. *Harness design for long-running application development*（上下文上限降标准/Planner-Generator-Evaluator 对抗评估）
4. LangChain. Ralph Loop / Context Rot / Agent = Model + Harness
5. Karpathy. *Software Is Changing (Again)*（Agent 作为新的数字信息消费者）
6. Chad Fowler. *Relocating Rigor*（严谨度从代码编写转移到环境/反馈/控制设计）
7. Addy Osmani（"The danger is stopping having an opinion when loops run autonomously"）
8. 关联文档：`2026-08-05-five-engineering-claude-code-trae-deep-analysis.md` / `2026-08-03-agent-composition-and-coding-agent-comparison.md` / `2026-08-04-graph-engineering-deep-analysis.md`

---

## Changelog

- 2026-08-05：初稿（深度分析，含三产品对照/七洞察/借鉴/预测；原文全文要点还原 §2）
