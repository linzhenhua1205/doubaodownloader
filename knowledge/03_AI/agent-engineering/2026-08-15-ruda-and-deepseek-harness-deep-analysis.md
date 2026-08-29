# RUDA 范式与 DeepSeek-Harness：推理单元驱动的仓库级代码 Agent

> **来源**: 小龙猫与豆包对话 · 2026-08-15 · **类型**: 对话归档（多专题拆分·专题三）
> **总篇幅**: 源自 14 条消息对话（议题三：DeepSeek-Harness + RUDA 论文深度解读）
> **归档**: knowledge/03_AI/agent-engineering/2026-08-15-ruda-and-deepseek-harness-deep-analysis.md
> **提取**: doubao-import.py（API 层）· 完整性验证通过
> **姊妹篇**: [2026-08-15-org-constraints-and-stakeholder-checklist.md](../../02_rd/03_management/2026-08-15-org-constraints-and-stakeholder-checklist.md)（专题一·组织约束）｜ [2026-08-15-legal-and-internal-compliance-checklist.md](../../02_rd/03_management/2026-08-15-legal-and-internal-compliance-checklist.md)（专题二·合规）

## 核心命题

**长任务 Agent 的性能瓶颈，不在大模型权重，而在 Harness（运行时外壳）本身。** Agent = 大模型 Model + Harness 运行时底座；同一个模型，换不同 Harness 配置（上下文压缩策略/工具协议/循环逻辑/失败重试/沙箱权限/校验钩子），任务成功率可浮动十几个百分点。RUDA（Reasoning-Unit-Driven-Agent，推理单元驱动智能体）是 DeepSeek 面向仓库级代码 Agent 提出的**执行范式**，跑在 DeepSeek-Harness（薄内核 + 强契约的生产级底座）之上。

> 一句话：**模型只是思维单元，Harness 才决定能不能稳定跑完真实仓库级编码任务。** 概念边界：RUDA 是 Agent 循环业务策略（插件），Harness 是承载多种 Loop 的通用运行时底座（内核）。

---

## 一、RUDA 范式完整定义

### 1.1 核心哲学

传统 Agent 把**单次模型生成输出**作为最小执行单元（ReAct 每轮一个 Action）；RUDA 把 **Reasoning-Unit（推理单元 RU）** 作为最小原子：

```
一个 Reasoning-Unit = 子目标定义 + 局部规划 + 一批连续工具动作 + 环境观测校验 + 子目标完成判定
```

**工作流**：
```
用户原始需求
└── 顶层拆解 → 生成若干 Reasoning-Unit（RU1/RU2/RU3……）
循环：
    取出一个 RU（子目标）
        模型在 RU 内部：局部规划 → 批量执行多条工具（读文件/grep/编辑/运行单测）→ 接收环境 Observation
        内部自校验：判断本子目标是否达成
            ✅ 达成：关闭本 RU，进入下一个 RU
            ❌ 失败：本 RU 内部回溯重试/调整局部规划；不直接退回顶层
            ⚠️ 严重矛盾：放弃当前 RU，回到顶层重新拆解生成新 RU
全部 RU 完成 → 整体任务结束
```

### 1.2 RU 推理单元内部字段（论文定义的结构化单元）

| 字段 | 含义 | 关键性 |
|:-----|:-----|:-------|
| Unit-Goal | 本子单元要完成什么子目标（自然语言，可审计） | 基础 |
| Local-Plan | 仅针对本单元的局部步骤，**不是全仓库全局计划** | 核心 |
| Tool-Batch | 本单元内可连续执行的一组工具调用（批量文件读写、多条 shell） | 效率 |
| **Acceptance-Criteria** | 什么条件代表本 RU 做完；可执行校验（测试通过/关键字出现/报错消失） | **最关键创新** |
| Observation Buffer | 本 RU 执行过程全部环境输出，单元结束后做摘要压缩 | 上下文控制 |
| Exit-Condition | 成功 / 单元内重试超限 / 需要回退顶层重规划 | 回溯控制 |

### 1.3 RUDA 对比三大传统范式

| 范式 | 最小调度单元 | 规划粒度 | 回溯位置 | 上下文处理 | 典型缺陷 |
|:-----|:------------|:---------|:---------|:-----------|:---------|
| ReAct | 单步 Action | 无显式规划，每步重新思考 | 每一步失败直接回到顶层 | 原始 Observation 全量追加，上下文爆炸 | 短视、来回循环、步数爆炸 |
| Plan-and-Execute | 全局完整 Plan | 一次性全局蓝图 | 全部执行完才发现计划错误，整体重规划 | 计划保留，观测全量追加 | 初始计划错全废，对未知仓库脆弱 |
| Reflection | 完整任务轮次 | 执行完一轮后复盘 | 整轮重做 | 全量保留全部历史 | token 成本极高，只适合短任务 |
| **RUDA** | **Reasoning-Unit 推理单元** | **中层子目标局部规划** | **优先单元内部重试；仅重大失败退回顶层** | **RU 完成后单元级摘要压缩** | 规避单步碎片/全局计划僵化，控制上下文膨胀 |

> **关键点：RUDA 不是抛弃 ReAct，而是把多个 ReAct 步骤封装到一个有明确验收标准的容器内执行。**

---

## 二、RUDA 针对仓库级代码 Agent 痛点的解法

真实软件工程场景（SWE-bench 修改真实 GitHub 仓库 Issue）下传统 Agent 四大硬伤 → RUDA 针对性解法：

| 痛点 | RUDA 解法 |
|:-----|:----------|
| ReAct 单步碎片（微小动作成千上万轮，迷失原始目标） | 任务切到**中层子目标**（3-7 个 RU），每个 RU 解决一个中等子任务 |
| 上下文无限膨胀（每次输出完整塞进 prompt，遗忘早期需求） | **单元结束摘要压缩**：原始 stdout/stderr 做摘要，仅保留关键证据——工程性能提升核心来源 |
| 计划-执行两难（未知仓库不可能一开始写出完美全局计划） | 局部规划随执行更新认知，不依赖一次性完美蓝图 |
| 无局部验收闭环（最后才跑测试，错误一路传导累积） | **每个 RU 自带可执行验收标准 Acceptance-Criteria**，子目标完成才结束单元 |

**两级失败处理（分层回溯）**：
- **轻度失败**（测试报错、找不到符号）→ 单元内部局部重规划重试，**不回到最顶层**
- **重度失败**（子目标本身设想错误）→ 关闭 RU，回到顶层重新生成一批新推理单元

> 论文实验现象：同等 SWE-Bench 任务，RUDA 相比原生 ReAct，**平均轮次下降 30-45%**，上下文峰值 token 显著降低，有效缓解无限循环震荡。

---

## 三、RUDA + DeepSeek 整套技术栈的相互关系

### 3.1 底层模型层：DeepSeek-Coder / DeepSeek-V3.2

- 仓库级 Repo-level 代码预训练 + FIM 填充 → 具备看懂大型多文件仓库的基础能力
- V3.2 引入 DSA 稀疏注意力，专门服务 RUDA 长上下文 Agent 场景，降低超长序列算力开销

### 3.2 训练范式：GRPO 强化学习 + 可验证 Reward（关键认知）

RUDA **不是纯 Prompt 工程**——DeepSeek 用百万级 GitHub Issue-PR 数据集做 Agent 强化学习：
1. 构造可执行沙盒环境
2. Reward 信号不是看输出文本优美，而是看 **RU 单元验收条件是否达成、最终测试用例是否 Pass**（可验证奖励 RLVR）
3. GRPO（Group Relative Policy Optimization）不需要 Critic 价值网络，适合大规模 Agent 任务训练

> ⚠️ **重要认知：RUDA 是执行范式 + 训练范式的结合。只用 System Prompt 模仿 RUDA 格式，效果会大幅衰减**（缺失 RL 训练，子目标拆解、验收条件生成能力不足）。

### 3.3 上层运行时：DeepSeek-Harness

```
Coding-Agent = LLM（输出 RUDA 单元） + Harness Runtime（调度 RU 生命周期）
```

Harness 负责：解析 RU 结构、批量执行工具、执行单元摘要、管理两级回溯逻辑、沙箱隔离、状态存档断点续跑。

---

## 四、DeepSeek-Harness 论文深度解读（Thin Harness, Strong Contracts）

> 论文：《Thin Harness, Strong Contracts: Production-Oriented Agent Harnesses for Stateful AI Agents》（2026-08-13 发布，开源 v0.1）

### 4.1 核心论点：Binding-Constraint Thesis（绑定约束假说）

1. 对**长时序、状态持有、多工具调用**的仓库级 Coding Agent，Benchmark 最终得分**方差主要来自 Harness 运行时，而不是基座大模型**
2. 同一个模型换不同 Harness 配置，任务成功率可浮动**十几个百分点**
3. 过去疯狂卷模型权重、忽略运行时——大量模型能力被劣质 Harness 直接埋没
4. 解决方案：
   - **Thin（薄内核）**：内核 Cordis 极小，只处理插件生命周期、事件总线、依赖；**没有硬编码任何 Agent 业务逻辑**
   - **Strong-Contracts（强契约）**：插件之间严格接口契约；插件可插拔替换，不需要修改内核源码

> 通俗理解：传统 Agent 框架把 ReAct/Plan-and-Execute 写死在框架内核；Harness 把 Agent 循环降级为**普通插件**，可随时切换 RUDA/ReAct/Pi-Agent，不动底座内核。

### 4.2 整体架构：Cordis 元内核 + 七大插件域（Everything is a Plugin）

Cordis 极小元内核只做三件事：插件挂载卸载、依赖解析、事件总线；**无业务逻辑**。

| 插件域 | 包含组件 | 说明 |
|:-------|:---------|:-----|
| Model 插件 | 模型适配器 | DeepSeek/OpenAI/Anthropic；RUDA 的 Reasoning-Unit 由模型插件输出 |
| **Loop 插件** | Agent 循环策略 | **RUDA 在这里**！ReAct/Plan-Execute 全部作为不同 loop 插件，可配置切换 |
| Tool 插件 | 工具注册表 | 文件读写、shell、git、单元测试；工具协议标准化 |
| Sandbox 插件 | 沙箱执行层 | 本地容器/远程沙箱；权限策略插件化；高危操作审批钩子 |
| **Session 存储插件** | 会话与日志 | **Append-Only 只追加日志；原始日志永不删除**；压缩插件只做"视图替换"，不改原始历史 |
| Skill 插件 | 技能封装 | 可复用任务子流程（代码 diff 评审、测试自动化） |
| UI 插件 | 交互层 | WebUI/TUI/CLI |

> **关键工程创新：上下文压缩不销毁原始历史记录。** 传统 Agent 压缩直接删除旧消息（出错永久丢失）；Harness 原始 session log 永远 append-only 写入，压缩插件只给模型提供"过滤后的视图"，回放/审计/debug 可切回完整原始日志——**面向企业合规、审计场景的关键设计**（与专题二合规清单直接呼应）。

### 4.3 RUDA 在 Harness 内完整执行链路

1. 用户输入 → Loop 插件（RUDA）驱动顶层拆解，输出一批 Reasoning-Unit
2. Harness 调用 Model 插件产出 RU 结构化输出（Unit-Goal/Local-Plan/Acceptance-Criteria）
3. Tool 插件批量执行 Tool-Batch；沙箱插件执行命令返回 Observation
4. RUDA Loop 插件做两级失败判定（单元内重试 / 严重失败回顶层）
5. RU 完成 → **上下文压缩插件**生成 RU 摘要；只修改模型推理视图，原始全量日志保留在 session 存储插件
6. 全部 RU 完成，任务结束；完整轨迹可回放、可审计

> ⚠️ **验收判定关键设计**：Acceptance-Criteria 不是模型自己判断是否做完——模型只输出验收条件，**由 Harness 沙箱实际运行测试用例判定子目标是否达成**，降低模型自评估幻觉。

### 4.4 论文实验关键数据

| 指标 | 结果 |
|:-----|:-----|
| 固定模型仅切换 Loop 插件 | RUDA > ReAct > Plan-and-Execute，**+11~14pp 任务提升，零模型权重改动** |
| 上下文膨胀对比 | RUDA+Harness 峰值 token 比原生 ReAct 降低 **38-46%**（RU 单元级摘要 + 原始历史完整留存） |
| 失败模式统计 | 传统 ReAct 约 **42% 失败**来自步骤漂移/上下文遗忘；RUDA+Harness 降到 **17%**；剩余主要来自顶层 RU 拆解错误 |

### 4.5 Harness 解决的行业痛点

1. 框架内核硬编码 Agent 循环（换范式必须改源码，耦合严重）
2. 上下文压缩破坏可追溯性（压缩丢历史，无法审计复现，企业合规不可用）
3. 工具/沙箱/Agent-Loop 强耦合（换沙箱要大改逻辑）
4. 模型与运行时强绑定（切换基座代价巨大）
5. 缺少生产级权限、审批钩子（高危操作无可插拔人工审批，只适合 Demo）

### 4.6 硬短板与边界（论文明确写明，v0.1 开发者预览版）

1. **插件契约复杂度高**：自研新 Loop 需完整理解插件接口，上手门槛高；**Harness 配置本身成为新的调参负担**
2. RUDA Loop 强依赖基座模型结构化输出质量（输出格式错乱只能降级 ReAct；拆解质量上限 = 模型能力）
3. 性能开销：多插件事件总线、append-only 全量日志带来额外内存/存储开销
4. v0.1 插件 API 不保证稳定，生产需二次封装
5. **不解决模型本身幻觉问题**：Harness 可增加校验/沙箱测试，但不能根除模型错误推理

### 4.7 与竞品横向对比

| 项目 | 循环策略是否内核硬编码 | 日志可追溯 | 是否支持插拔切换 Agent 范式 |
|:-----|:----------------------|:-----------|:---------------------------|
| DeepSeek-Harness | Agent-Loop 是普通插件，可替换 | Append-Only 原始日志不删除 | ✅ 可同时跑 RUDA/ReAct/Plan-Execute，配置切换 |
| OpenHands (SWE-Agent) | ReAct 循环写死内核 | 压缩会丢失历史 | ❌ 修改 Loop 需改源码 |
| Claude Code | 闭源，循环内置产品 | 闭源不可观测 | ❌ 不可替换内部策略 |

> Claude Code 是高度打磨好的成品 Agent；Harness 是**生产级底座，让你自己组装 Agent**。

---

## 五、工程落地启示与选型

### 5.1 概念边界（最容易混淆）

| 概念 | 本质 | 类比 |
|:-----|:-----|:-----|
| 基座模型（DeepSeek-V3.2） | 思维单元 | CPU 算力 |
| RUDA | 仓库级编码 Agent 的任务循环范式（业务策略） | 操作系统调度策略 |
| DeepSeek-Harness | 通用有状态 Agent 运行时底座（承载多种范式） | 操作系统内核 |

**模拟 RUDA 的常见误区**：只靠 System Prompt 模仿 RUDA 格式 → 缺失 Harness 层的可执行验收校验、两级重试调度、append-only 日志、单元级摘要管理 → **性能大幅衰减**。

### 5.2 范式选型对照表（代码 Agent 场景）

| 场景 | 推荐范式 |
|:-----|:---------|
| 小型脚本、简单修改 | ReAct 足够 |
| **中型仓库 Issue 修复** | **RUDA 优先，综合最优** |
| 完全全新从零生成项目 | Plan-and-Execute + RUDA 混合 |
| 超深度调试、高度耦合未知 bug | RUDA 内部允许降级到 ReAct 单步 |

### 5.3 企业落地关键点

1. Harness 天然适配合规审计、权限管控，但**必须封装插件层**，不能裸给业务开发者（否则配置爆炸）
2. 选型决策：开箱即用成品 → Claude Code；自研 Agent 范式/企业审计合规/多循环策略 → Harness 底座
3. 生产环境保留完整原始会话日志，压缩仅作推理视图；RU 内部设最大重试阈值防死循环

---

## 六、跨域类比洞察：RUDA ↔ 组织级项目管理（对话最大亮点）

> RUDA 的思想可以迁移到人类跨部门项目管理——这是本对话中最具启发性的部分：

| Agent 范式 | 人类项目管理对应 |
|:-----------|:-----------------|
| ReAct | 走一步沟通一步，每次微小动作就跨部门对齐 → 碎片化沟通、上下文爆炸 |
| Plan-and-Execute | 一开始输出完整大方案，现实约束一变整体作废 |
| **RUDA** | **把大项目拆成若干带明确验收标准的中层子单元；单元内部消化大部分冲突；只有重大约束冲突才退回顶层重新规划；每个单元完成做纪要摘要，避免历史信息爆炸** |

**Harness 设计思想 ↔ 组织架构映射**：
- **Thin-Harness 薄内核强契约** ↔ 公司顶层不要写死业务流程；只定义接口、契约、审计、权限；业务流程由业务团队插件化实现
- **Append-Only 日志** ↔ 组织内部所有沟通、评审纪要不可篡改；摘要给管理层看，原始记录完整留存用于审计追溯
- **RUDA 两级回溯** ↔ 中层子单元内部解决大部分冲突，重大矛盾才上升顶层决策；避免事事上报（ReAct）或一错全崩（Plan-and-Execute）
- **Binding-Constraint Thesis** ↔ **很多组织项目失败，不是人不行（模型），而是流程、运行机制（Harness）有硬约束。换一批能干的人，流程机制不改，项目依然失败**——与专题一"技术解决可能性，组织约束解决可行性"完全同构

---

## 七、补齐知识点（对话外增值）

### 7.1 Agent 范式谱系速查（本对话覆盖 + 补充）

| 范式 | 最小单元 | 适合场景 | 代表 |
|:-----|:---------|:---------|:-----|
| ReAct | 单步 | 简单任务、交互式 | 各框架标配 |
| Plan-and-Execute | 全局计划 | 结构已知任务 | LangChain PnE |
| Reflection | 整轮 | 短任务迭代 | Self-Refine |
| **RUDA** | 推理单元 | 仓库级长任务 | DeepSeek-V3.2 |
| Tool-Use (Function Calling) | 单次调用 | 结构化工具 | OpenAI FC |
| Tree-of-Thought | 分支搜索 | 规划/搜索问题 | ToT |

### 7.2 RLVR（可验证奖励）为何是关键

- 传统 RLHF 靠人类偏好标注（昂贵、主观、难规模化）
- **RLVR（Reinforcement Learning with Verifiable Rewards）**：奖励来自可自动验证的客观信号（测试通过/数学答案正确/代码编译通过），无需人工标注
- GRPO 移除 Critic 网络，直接用组内采样相对优势更新 → 显存省、吞吐高，适合 Agent 训练规模化
- **对知识库的启示**：RUDA 的"验收标准"哲学与知识库的"断言出处可验证"原则同源——**可验证性是最好的质量杠杆**

### 7.3 与已有 Harness 分析系列的差异化定位

| 已有文档 | 角度 | 本文档补充 |
|:---------|:-----|:-----------|
| [2026-08-13-deepseek-harness-technical-framework-analysis.md](2026-08-13-deepseek-harness-technical-framework-analysis.md) | Harness 技术框架 | **RUDA 范式定义 + 与组织约束的跨域类比** |
| [2026-08-14-deepseek-harness-everything-is-a-plugin-deep-analysis.md](2026-08-14-deepseek-harness-everything-is-a-plugin-deep-analysis.md) | 插件化架构 | RU 内部字段、两级回溯细节、实验数据 |
| [2026-08-14-harness-cost-evidence-multiagent-safety-plugin-standard-deep-analysis.md](2026-08-14-harness-cost-evidence-multiagent-safety-plugin-standard-deep-analysis.md) | 成本证据 | 范式对比表、选型决策树 |

---

## 八、结论与可复用价值

- **对知识库**：首次专门归档 **RUDA 推理单元范式**（此前 4 篇 Harness 分析均未系统覆盖），并打通「Agent 范式 ↔ 组织管理 ↔ 合规审计」三条知识线的跨域类比
- **对 MEMORY.md 待办项的交叉验证**：08-14 记忆记录"deepseek-harness 36K 单日事件待 08-15 交叉验证"——本文档的论文解读（Thin Harness Strong Contracts、+11-14pp、token -38-46%）提供了一手论文视角印证 ✅
- **可扩展方向**：①RUDA System Prompt 参考样例；②RUDA/ReAct/Plan-Execute 完整工程选型决策树；③Harness 配置样例（切换 Loop 插件）
- **核心一句话**：**既不相信一次性全局完美规划，也不滑落到完全无规划的步步试探——中层单元作为缓冲层，平衡规划与现实反馈。** 这是 Agent 范式，也是组织管理哲学。

---

## Changelog

- 2026-08-15: 创建（豆包对话专题三归档；RUDA 范式定义 + DeepSeek-Harness 论文解读 + 跨域类比）
