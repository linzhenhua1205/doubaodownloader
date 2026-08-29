# 五种工程 × 双产品：提示词 / 上下文 / Harness / Loop / Graph 在 Claude Code 与 Trae 中的体现与技术框架

> **日期**: 2026-08-05 | **分类**: 03_AI/agent-engineering | **专题编号**: AGT-ENG-2026-02
> **一句话**: 提示词、上下文、Loop、Harness、Graph 是 Agent 工程的**五维视角**（配方/输入/时间/行动/空间，确定性由软到硬递增）；Claude Code 是五工程完备度最高的参考实现，Trae（字节）2026 年已在 Hooks/Subagent/Skills/工作流上大幅追赶——**两者差距从"能力有无"缩小到"Harness 深度与生态"**。
> **来源**: Anthropic Claude Code 官方文档（2026-08）+ TraeCode/TRAE Work 官方文档 13 页（docs.trae.cn，2026-08-05 抓取）+ 知识库既有 6 篇专题（六层模型/动态工作流/Harness Memory/Graph 工程/编排范式/全链路推理）
> **关联**: [Agent 构成要素六层模型](2026-08-03-agent-composition-and-coding-agent-comparison.md)（本文是其实践视角姊妹篇）· [Graph Engineering](2026-08-04-graph-engineering-deep-analysis.md) · [Claude Code 动态工作流](2026-06-26-claude-code-dynamic-workflows.md) · [Harness Memory 纵深防御](2026-07-13-harness-agent-memory-defense-in-depth.md) · [编排范式](2026-08-03-agent-orchestration-paradigm-deep-analysis.md)

---

## 1. 结论概要（TL;DR）

1. **五种工程不是并列的五个功能，而是五个正交视角**：提示词工程管"怎么想"（配方）、上下文工程管"看什么"（输入）、Loop 工程管"怎么持续想"（时间）、Harness 工程管"怎么安全地做"（行动）、Graph 工程管"怎么把流程固化"（空间）。按确定性谱系排列：**提示词（软）→ 上下文 → Loop → Harness → Graph（硬）**——越靠右越该由代码承担。
2. **Claude Code 是五工程完备度最高的参考实现**：每项工程都有原生、声明式、可版本化的技术载体（CLAUDE.md 分级/Skills/Hooks 7 类/Subagents/Dynamic Workflows/Background Tasks）。
3. **Trae 2026 年实现"五工程全覆盖"**：规则体系（全局/项目/模块级+AGENTS.md 兼容）、SKILL.md 按需加载、全局/项目记忆文件、内置 Agent 主智能体+Subagent 体系、**六类 Hooks（可导入 Claude Code 配置）**、TRAE Work 的 Spec/Plan 工作流与定时任务。**08-03 对比中"Trae Hooks ❌/Subagent ❌"的结论已被官方文档推翻——需修订**。
4. **差异的本质从"能力有无"转为"深度与生态"**：Claude Code 胜在 Harness 深度（7 类 Hooks 的精细度、Background Tasks、Dynamic Workflows 现场生成、MCP 双角色、Checkpoints 恢复）；Trae 胜在 IDE 一体化（代码库索引/文档集/预览/多端调度）与工程化工作流（Spec 三文档组）。
5. **对自建 Agent 系统的可操作结论**：五工程落地清单（§9）——从规则分级、上下文预算、循环终止条件、工具安全边界到流程固化，每一层都有可复制的技术模式。

---

## 2. 五种工程的统一框架：五维视角与确定性谱系

### 2.1 五维视角（第一性定义）

| 工程 | 回答的问题 | 管理对象 | 确定性 | 失效模式 |
|:-----|:-----------|:---------|:------:|:---------|
| **提示词工程** | 模型"怎么想"？ | 指令/人格/约束/能力声明 | 软（概率性） | 指令漂移、上下文膨胀 |
| **上下文工程** | 模型"看什么"？ | 输入空间（窗口/记忆/检索） | 软 | 上下文超限、遗忘、成本失控 |
| **Loop 工程** | 模型"怎么持续想"？ | 推理循环（感知→规划→行动→观察） | 中 | 死循环、目标漂移、提前收工 |
| **Harness 工程** | 模型"怎么安全地做"？ | 工具面/权限/持久化/事件 | 硬（确定性） | 工具滥用、状态丢失、不可审计 |
| **Graph 工程** | "流程怎么固化"？ | 状态/边/检查点/人工介入点 | 最硬 | 过度设计、图腐化、可恢复失败 |

### 2.2 与六层模型的映射

```text
Five engineering x Six-layer model (08-03) mapping:
Prompt eng    -> L1 cognitive base (Prompt tiers Rule/Agent/User/Memory)
Context eng   -> L1 memory subsystem + context handling (compact/cache/edit)
Loop eng      -> L2 reasoning loop (ReAct / Long Horizon / Workflow Runtime)
Harness eng   -> L3 tool surface + L5 orchestration + L6 channel (deterministic shell)
Graph eng     -> L5 orchestration layer (explicit workflows)
```

> **核心命题**：五种工程的总目标是同一个——**把不确定性限制在模型推理边界内**（概率内核 + 确定性外壳）。越往谱系右侧，越要"从提示词搬进代码"（参考 Boris Cherny："I don't prompt Claude anymore. I have loops running that prompt Claude."）。

---

## 3. 提示词工程（Prompt Engineering）

### 3.1 第一性

提示词工程不是"写更好的 prompt"，而是**分级注入的认知基座设计**：按"稳定性 × 作用域"把信息切分，让高频动态信息不污染低频稳定指令（本库 AGENT/USER/RULE/MEMORY 四文件即此思想）。

### 3.2 Claude Code 的体现与技术框架

| 技术载体 | 机制 | 工程要点 |
|:---------|:-----|:---------|
| **CLAUDE.md 三层分级** | Enterprise Policy（全局强制）/ `~/.claude/CLAUDE.md`（用户级）/ 项目根 CLAUDE.md | 分层覆盖：越近项目越具体 |
| **@import 指令** | CLAUDE.md 拆分子文件按需加载（`@import docs/xxx.md`） | 作用域化组装，避免单文件膨胀 |
| **.claude/commands/（斜杠命令）** | 用户触发的模板化指令（`/review`、`/test`） | 常用操作快捷封装 |
| **Skills（SKILL.md）** | 声明式技能包：触发条件/步骤/产出规范，Agent 按相关性自动加载 | 动态能力（"会做什么"）vs CLAUDE.md 静态规则（"你是谁"） |
| **Output Styles** | 输出风格配置（简洁/详细/自定义模板） | 输出层约束 |
| **Subagent 指令文件** | `.claude/agents/<name>.md`：角色/工具权限/指令声明 | 子代理的"专属提示词" |

### 3.3 Trae 的体现与技术框架（docs.trae.cn 官方）

| 技术载体 | 机制 | 工程要点 |
|:---------|:-----|:---------|
| **全局规则** | 跨项目生效，个性化偏好 | 类似 CLAUDE.md User 级 |
| **项目规则** | 仅当前项目生效；Markdown 编写；**rules/ 目录最多 3 层嵌套**（模块级规则） | 大型项目按模块隔离，避免规则互相干扰 |
| **三种生效方式** | 指定文件生效 / 智能生效（AI 判断相关性）/ **#Rule 手动触发**（优先级最高） | 规则加载的精细控制 |
| **AGENTS.md / CLAUDE.md / CLAUDE.local.md 兼容** | 从 Claude Code 导入项目时一并导入并生效 | **跨 IDE 规则互操作**（AGENTS.md 已成事实标准） |
| **git-commit-message.md** | 为 AI 生成的提交信息设置专用规则 | 垂直场景规则 |
| **自定义智能体提示词** | 智能体配置面板：人设/口吻/工作流程/工具使用时机 | 将提示词封装为可分享单元（掘金社区分享/导入） |
| **Skills（SKILL.md）** | 与 Anthropic 规范一致；**先扫描简要描述、仅相关时加载详情（按需加载）** | 文档明确："规则全量加载 vs 技能按需加载"——Token 节约设计 |

### 3.4 关键对比

| 维度 | Claude Code | Trae |
|:-----|:-----------|:-----|
| 分级 | 三层（Enterprise/User/Project） | 全局/项目/模块（3 层目录嵌套） |
| 跨平台兼容 | CLAUDE.md（自有标准） | **AGENTS.md 生态兼容 + CLAUDE.md 兼容** |
| 加载机制 | 规则常驻 + Skills 按需 | **规则全量 + 技能按需**（官方明示 Token 策略） |
| 触发控制 | 常驻为主 | **三态生效方式 + #Rule 手动最高优先级** |

> **判断**：提示词工程层面两者已基本对齐；Trae 的"模块级规则"与"#Rule 手动触发"在大型仓库场景甚至更细。真正差异转移到"提示词之外的工程层"。

---

## 4. 上下文工程（Context Engineering）

### 4.1 第一性

上下文是**稀缺资源**（窗口物理极限 + token 成本），上下文工程 = 预算管理：哪些必须常驻、哪些按需加载、超限怎么办、成本如何回收（缓存）。量化锚点：本库实测 27 天 2.3B tokens，**缓存未命中 58% 是最大成本项**；Rovo 第二代 compaction 做到 95% 驱逐 + KV offload。

### 4.2 Claude Code 的体现与技术框架

| 技术载体 | 机制 |
|:---------|:-----|
| **@-mention 引用** | 按需引用文件/符号（`@file.ts`），不全量读入 |
| **工具结果截断** | 超长结果保留首尾+省略说明（纯字符串，不调 LLM） |
| **轮次裁剪** | 以"完整轮"为单位裁掉最早一半 + 提炼总结写记忆（保证工具入参/结果成对） |
| **Token 压缩** | 每轮只留首条提问+末条回复 |
| **溢出兜底** | API 抛溢出时总结后激进截断 |
| **Prompt Caching** | 前缀缓存 + `cache_control` 标记：相同前缀多次推理复用，增量只算最新 token |
| **Memory 工具（/memory）** | 长期记忆读写，与 CLAUDE.md（指令）分离 |
| **上下文编辑** | 任务阶段切换时主动删除/替换/追加上下文 |

### 4.3 Trae 的体现与技术框架

| 技术载体 | 机制 |
|:---------|:-----|
| **当前文件自动可见** | 编辑器中正在编辑的代码文件默认可见 |
| **选中内容加入上下文** | 选中代码片段 → 侧边对话（带文件名+行号） |
| **# 文件引用** | 对话中 # 提及文件即纳入上下文（与规则联动） |
| **全局记忆 user_profile.md** | `~/.trae-cn/memory/user_profile.md`：跨项目偏好 |
| **项目记忆 project_memory.md** | `~/.trae-cn/memory/projects/{path}/project_memory.md`：项目专属 |
| **记忆自动维护** | AI 自动识别偏好写入/更新/删除（也支持显式指令"记住…"） |
| **代码库索引（codebase-indexing）** | 全仓索引支撑检索型上下文（类似 Claude Code 的 Code Search） |
| **文档集理解** | 项目文档作为知识源注入 |

### 4.4 关键对比

| 维度 | Claude Code | Trae |
|:-----|:-----------|:-----|
| 记忆形态 | 工具化（/memory）+ CLAUDE.md | **文件化（user_profile.md/project_memory.md，可直接编辑）** |
| 自动维护 | 用户显式/隐式触发 | **AI 自动识别+更新+删除**（文档明示四种维护方式） |
| 引用粒度 | @ 文件/符号 | 当前文件/选中片段/# 文件 |
| 缓存机制 | Prompt Caching（cache_control） | 依赖模型侧缓存（未公开同等级机制） |
| 代码检索 | Grep/Glob/Code Search（LSP 语义） | Codebase Indexing（IDE 原生） |

> **判断**：Claude Code 在"运行时上下文管理"（截断/裁剪/压缩/缓存四层策略）上更工程化；Trae 在"记忆文件化透明可编辑"与"IDE 原生上下文来源"（选中片段/当前文件）上体验更顺。二者对"上下文预算"理念一致（Skills 按需加载即预算管理）。

---

## 5. Loop 工程（Loop Engineering）

### 5.1 第一性

所有 Agent 共享同一心脏——感知→规划→行动→观察循环。Loop 工程的演进：**ReAct（纯提示词维持）→ Harness（代码模板）→ Dynamic Workflow（模型生成脚本）→ Workflow Runtime（编译为可执行运行时）**。工程要点：终止条件、想/做分离、并行化、长视界。

### 5.2 Claude Code 的体现与技术框架

| 技术载体 | 机制 |
|:---------|:-----|
| **主循环** | 每轮携带全量对话状态+工具 schema；工具结果作为 ground truth 追加 |
| **Parallel Tool Use** | 同一轮并行多个独立工具调用，减少往返 |
| **Plan Mode** | 只读分析→产出计划→批准后执行（**把"想"与"做"分离**） |
| **TodoWrite** | 任务清单显式化，缓解 Goal Drift |
| **Long Horizon** | 单一上下文 150 轮迭代（Rovo 第二代同架构） |
| **终止条件** | 任务完成/最大迭代/人类干预 |
| **Checkpoints** | 会话检查点，中断后恢复 |

### 5.3 Trae 的体现与技术框架

| 技术载体 | 机制 |
|:---------|:-----|
| **内置 Agent 主智能体** | 专为自动化项目开发：需求拆解→方案设计→代码实现→重构→修复 |
| **Agent 流水线** | 分析需求 > 生成 PRD 与技术方案 > 生成代码 > 预览成果；按任务难度补环节（读文件/确认改动范围/梳理待办/调用子智能体/检查运行结果/关键决策确认） |
| **确认点（human-in-the-loop）** | 生成 PRD/方案后暂停等确认；关键决策请用户确认 |
| **子智能体调度** | 上下文较长/任务复杂时，Agent 将任务拆分给子智能体（默认内置 Search） |
| **Agent 模式 vs 对话模式** | 对话式问答 vs 自主多步执行的双模式 |
| **Solo 模式** | 轻量对话界面（规则/记忆同源） |

### 5.4 关键对比

| 维度 | Claude Code | Trae |
|:-----|:-----------|:-----|
| 循环形态 | ReAct 主循环（通用） | **工程化流水线**（PRD→方案→代码→预览，面向开发场景） |
| 想/做分离 | Plan Mode（显式模式切换） | 确认点（生成方案后暂停） |
| 并行化 | Parallel Tool Use + Background Tasks | 子智能体并行（粒度更大） |
| 长视界 | Long Horizon（150 轮） | Agent 多步执行（未公开轮数上限） |
| 终止/恢复 | Checkpoints | 任务状态随 Spec 工作流更新（可恢复） |

> **判断**：Claude Code 的 Loop 是"通用引擎"（适用于任意任务），Trae 的 Loop 是"开发专用流水线"（PRD/方案/代码/预览是编码任务的结构化表达）。后者在开发场景更可控，前者在通用场景更灵活。

---

## 6. Harness 工程（Harness Engineering）

### 6.1 第一性

Harness = 让 Agent 更有组织地干活的**确定性外壳**：任务怎么拆、Agent 怎么调用、上下文怎么隔离、结果怎么合并、中断后怎么恢复、动作怎么授权。Harness 的进化方向是把"与推理无关但必须发生的动作"（审计/拦截/通知/持久化）从主循环剥离，用事件驱动（Hooks）确定性执行。

### 6.2 Claude Code 的体现与技术框架

| 技术载体 | 机制 |
|:---------|:-----|
| **工具面** | Read/Write/Edit/MultiEdit/Glob/Grep/Code Search/Bash/Web/Visual/Memory/TodoWrite/Task |
| **权限分级** | 工具调用 Permission 分级（允许/询问/拒绝），高危操作拦截 |
| **Hooks（7 类）** | PreToolUse/PostToolUse/UserPromptSubmit/Stop/Notification/SessionStart/End/SubagentStop——旁路执行外部脚本 |
| **Subagents** | `.claude/agents/*.md` 声明式；独立上下文；隔离目的=防上下文污染 |
| **Background Tasks（/bg）** | 后台长任务并发，不阻塞前台对话 |
| **MCP 双角色** | Client（接外部 server）+ Host（被其他 Agent 调用） |
| **Checkpoints** | 会话级恢复 |
| **CLI/SDK** | 终端原生 + Headless SDK（CI/CD 服务化） |

### 6.3 Trae 的体现与技术框架（★ 2026 重大更新）

| 技术载体 | 机制 |
|:---------|:-----|
| **内置工具** | 终端（运行命令+获取状态结果）/ 预览（前端结果预览入口）/ MCP Server 工具 |
| **Hooks（六类事件）** | SessionStart（注入环境变量/上下文）/ UserPromptSubmit（拦截/附加上下文）/ PreToolUse（校验/拦截/修改工具参数/要求确认）/ PostToolUse（检查产出、阻断停止继续优化）/ Notification（工具调用等待确认时通知）/ AgentStop（智能体完成任务时）——**全局+项目 Hook** |
| **Hooks 生命周期** | SessionStart → UserPromptSubmit → PreToolUse →（工具循环）→ PostToolUse → Notification |
| **Claude Code Hook 兼容** | **支持导入 Claude Code 的 Hook 配置**（同名事件参数可能有差异，导入后需按 TraeCode 规范调整） |
| **沙箱执行** | Hook 命令可配置沙箱内/沙箱外执行（沙箱外有风险提示） |
| **Subagent 体系** | 默认内置 Search 子智能体；Markdown 文件定义 Subagent（同 Claude Code 模式）；自定义智能体可被"Agent"调用（独立上下文）；**仅内置 Agent 可调用自定义智能体** |
| **TRAE Work 远程环境** | Web/桌面/移动端远程 Agent 环境 + sandbox + 隐私模式 |
| **CLI** | Trae CLI（含 Agent Client Protocol 支持） |

### 6.4 关键对比（★ 修订 08-03 结论）

| 维度 | Claude Code | Trae（2026-08 官方文档） |
|:-----|:-----------|:------------------------|
| Hooks | 7 类（含 SubagentStop/Stop） | **六类**（SessionStart/UserPromptSubmit/PreToolUse/PostToolUse/Notification/AgentStop） |
| Hooks 互操作 | 自有标准 | **可导入 Claude Code Hook 配置** |
| Subagent | 声明式文件 + 任意编排 | 声明式文件 + **默认 Search** + 仅主 Agent 可调用 |
| 后台任务 | Background Tasks（/bg 多任务并发） | TRAE Work 定时任务/自动化（粒度不同） |
| 沙箱 | Bash 权限分级 | Hook 沙箱选项 + Work Sandbox |
| MCP | Client+Host 双角色 | Client（工具接入）+ 远程 MCP（Work） |

> **⚠️ 重要修订**：08-03《四 Agent 对比》标注 Trae"Subagent ❌/Hooks ❌"——**已被 TraeCode 官方文档（2026-08 抓取）推翻**：Trae 现具备六类 Hooks、声明式 Subagent（含默认 Search 子智能体）、SKILL.md 技能体系与 AGENTS.md 兼容。差距从"能力有无"缩小为"深度与精细度"（如 Claude Code 的 SubagentStop 钩子、Background Tasks 前台并发、MCP Host 角色 Trae 暂无）。

---

## 7. Graph 工程（Graph Engineering）

### 7.1 第一性

Graph 工程 = **代码约束 + 模型推理**：用图（节点/边/状态/检查点/人工介入点）把概率性隔离在节点内，让控制流恢复确定性。约束五层级（从硬到软）：状态 schema → 拓扑 → 边条件 → 运行时（重试/超时/interrupt）→ 输出校验。适用判据：有明确状态转换/需人工介入/需可恢复/需可观测 → 用图；窄深单一推理 → 单循环；为图而图是反模式。

### 7.2 Claude Code 的体现与技术框架

| 技术载体 | 机制 | 对应图概念 |
|:---------|:-----|:-----------|
| **Dynamic Workflows** | Claude 现场生成 Harness（可存/可改/可重跑的代码） | 图结构由模型生成（动态图） |
| **六种工作流模式** | Classify-and-act（分类分支）/ Fanout-and-synthesize（并行汇聚）/ Adversarial verification（对抗验证）/ Generate-and-filter（生成筛选）/ Tournament（锦标赛）/ Loop until done（迭代验收） | 节点模式库 |
| **Subagent 拓扑** | `.claude/agents/*.md` 定义的可编排子代理 | 节点（隔离上下文） |
| **SubagentStop Hook** | 子代理完成后触发联动 | 边上的副作用 |
| **Checkpoints** | 会话/任务检查点 | 可恢复状态 |
| **TodoWrite** | 任务清单显式状态 | 状态 schema 的轻量版 |

### 7.3 Trae 的体现与技术框架（★ TRAE Work Spec/Plan 工作流）

| 技术载体 | 机制 | 对应图概念 |
|:---------|:-----|:-----------|
| **Spec 工作流**（复杂系统级） | AI 生成**三阶段文档组**：`spec.md`（大纲）+ `tasks.md`（任务列表）+ `checklist.md`（验收清单），存项目根目录按任务分组 | 状态 schema + 节点清单 + 验收条件（输出约束） |
| **Spec 人工确认点** | 文档首次创建后 AI **暂停执行等确认**；可编辑或用自然语言修改 | human-in-the-loop / interrupt |
| **Spec 状态自动更新** | 任务列表与验收清单状态随执行进度自动更新 | 状态持久化 + 进度追踪 |
| **Spec 版本控制** | 文档作为项目知识资产长期保留 | 可恢复/可审计（checkpoint） |
| **Plan 工作流**（中小型） | 生成 `plan.md` 计划文档，确认后逐项执行 | 轻量图（线性任务序列） |
| **内置工作流 Plan/Spec/Goal** | TraeCode 预置三类工作流模板 | 图模板库 |
| **定时任务（TRAE Work）** | 固定时间/间隔/定时策略（工作日 9 点）自动执行预设任务+执行记录 | 时间触发节点（调度层） |

### 7.4 关键对比

| 维度 | Claude Code | Trae |
|:-----|:-----------|:-----|
| 图生成者 | **模型现场生成**（Dynamic Workflows，动态图） | 预置模板（Plan/Spec/Goal，静态图）+ 定时任务 |
| 状态载体 | 代码（可存可改可重跑） | **文档（spec/tasks/checklist，人可读可编辑）** |
| 人工介入 | Plan Mode / 确认点 | Spec 文档确认点（首次创建暂停） |
| 验收约束 | Loop until done 模式 | **checklist.md 显式验收清单**（更强） |
| 恢复机制 | Checkpoints | 文档版本控制 + 状态自动更新 |

> **判断**：Claude Code 的 Graph 是"动态生成派"（强模型生成一次、弱模型执行多次），Trae 的 Graph 是"文档驱动派"（spec/tasks/checklist 三文档作为人和 AI 的共同契约）——后者与 Qoder 的 Spec 工作流同构，是国产 Agent 的工程化偏好；前者更接近"流程即代码"的工程师文化。

---

## 8. 五工程 × 双产品总矩阵与差异本质

### 8.1 总矩阵

| 工程 | Claude Code 技术框架 | Trae 技术框架 | 差距方向 |
|:-----|:--------------------|:-------------|:---------|
| 提示词 | CLAUDE.md 三层+@import / Commands / Skills / Output Styles | 全局/项目/模块规则+3 层嵌套 / AGENTS.md 兼容 / #Rule / Skills 按需 | 已对齐（Trae 模块级更细） |
| 上下文 | @引用 / 四层压缩策略 / Prompt Caching / /memory | 文件引用 / 记忆文件自动维护 / Codebase Indexing | Claude 运行时管理更深 |
| Loop | 通用 ReAct + Plan Mode + Parallel + Long Horizon | 开发流水线（PRD→方案→代码→预览）+ 确认点 | 通用 vs 场景专用 |
| Harness | 7 类 Hooks / Subagents / Background Tasks / MCP 双角色 / Checkpoints | 6 类 Hooks（兼容导入）/ Subagent / 沙箱 / Work 远程环境 | Claude 深度+精细度领先 |
| Graph | Dynamic Workflows 六模式（模型生成） | Spec 三文档组 + Plan + 定时任务（文档驱动） | 动态生成 vs 文档契约 |

### 8.2 差异的本质

1. **路径依赖**：Claude Code 从"终端 Agent 运行时"长出来（Harness 深度是基因）；Trae 从"AI IDE"长出来（IDE 集成度与工作流工程化是基因）。
2. **模型前提**：Claude Code 的 Dynamic Workflows/Background Tasks 依赖 Claude 4.x 的强推理与长上下文；Trae 的多模型接入（Claude/GPT/豆包）决定了其更依赖**确定性的工作流模板**（Spec/Plan）来补偿模型能力差异——**这是"动态生成派 vs 文档驱动派"的深层原因**。
3. **生态位**：Claude Code 面向"工程师+深度自动化"，Trae 面向"开发者+多端调度+低门槛 Builder"；当模型能力趋同，差异化回到 Harness 深度与工作流工程化——**中国厂商从"接模型"到"建 Harness"是下一阶段胜负手**（与 08-03 判断一致，但差距已缩小）。

---

## 9. 对自建 Agent 系统的启示：五工程落地清单

| # | 工程 | 落地检查项（自建系统逐条对照） |
|:--|:-----|:------------------------------|
| 1 | 提示词 | 是否按"稳定性×作用域"分级（全局约束/项目约束/会话事实）？是否支持模块级规则隔离？ |
| 2 | 上下文 | 是否有四层压缩策略（截断→裁剪→压缩→兜底）？缓存命中率是否作为运营指标？记忆是否文件化可编辑？ |
| 3 | Loop | 是否有显式终止条件？是否支持"想/做分离"（Plan Mode 或确认点）？长任务是否防 Goal Drift（TodoWrite）？ |
| 4 | Harness | 工具是否有权限分级+沙箱？关键事件是否用 Hooks 旁路（不占主循环）？是否支持会话恢复（Checkpoint）？ |
| 5 | Graph | 是否有任务清单+验收清单（spec/tasks/checklist 或等价物）？是否有确认点/恢复点？是否避免为图而图？ |

> **工程顺序建议**：先做 1+2（让模型"想对、看对"）→ 再做 4（安全边界，防止"做错"）→ 3 提供循环骨架 → 5 在最需要确定性/合规/可恢复的场景按需引入（图是最后手段，不是默认架构）。

---

## 10. 来源与验证

**Claude Code 侧**（Anthropic 官方文档 + 知识库既有专题）：

1. [Agent 构成要素六层模型](2026-08-03-agent-composition-and-coding-agent-comparison.md)（13 项要素/四 Agent 对比）
2. [Claude Code 动态工作流](2026-06-26-claude-code-dynamic-workflows.md)（Harness 定义/三大失败模式/六模式）
3. [Harness Agent Memory 纵深防御](2026-07-13-harness-agent-memory-defense-in-depth.md)（四类记忆/写入侧/Action Gate）
4. [Graph Engineering](2026-08-04-graph-engineering-deep-analysis.md)（约束五层级/适用边界/LangGraph 六坑位）
5. [编排范式深度技术分析](2026-08-03-agent-orchestration-paradigm-deep-analysis.md)（Long Horizon/context compaction 95%）
6. [编程 Agent 全链路推理](2026-08-04-coding-agent-fullchain-inference-deep-analysis.md)（KV/缓存量化）

**Trae 侧**（docs.trae.cn 官方文档，2026-08-05 抓取，13 页）：

- ide_rules（全局/项目/模块规则、AGENTS.md/CLAUDE.md 兼容、3 层嵌套）
- ide_automate-actions-with-hooks（六类 Hook 事件、生命周期、导入 Claude Code Hook、沙箱）
- ide_built-in-agent / ide_agent / ide_agent-overview（内置 Agent 流水线、自定义智能体、Subagent 声明）
- ide_skills（SKILL.md、按需加载、.agents/skills/ 生态、find-skills CLI）
- ide_memories（全局/项目记忆文件、四种维护方式）
- ide_basic-usage-of-context（上下文指定、选中片段、行号）
- ide_model-context-protocol / ide_codebase-indexing（MCP、代码库索引）
- work_spec-and-plan（Spec 三文档组/Plan 工作流）
- work_automated-tasks（定时任务：时间/间隔/策略/模板）
- work_what-is-trae-work（远程环境/隐私模式）

**素材分级**：Claude Code 特性基于官方文档+既有深度分析（高可信）；Trae 特性基于官方文档一手抓取（高可信，2026-08-05 快照，功能随版本演进）；"差距缩小"判断为本文分析；08-03"Trae Hooks ❌"结论已按最新官方文档修订。

---

## Changelog

- 2026-08-05 | 初版：五工程五维框架（配方/输入/时间/行动/空间 + 确定性谱系）+ Claude Code/Trae 双产品逐工程对照 + 8.2 差异本质（动态生成派 vs 文档驱动派）+ §9 落地清单 + 修订 08-03 Trae Hooks/Subagent 结论 | 数据源：Trae 官方文档 13 页一手抓取 + 知识库 6 篇专题
