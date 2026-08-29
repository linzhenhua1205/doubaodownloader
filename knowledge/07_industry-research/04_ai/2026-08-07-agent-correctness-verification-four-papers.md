# 🛡️ Agent 正确性验证四连发技术深潜：概率性生成 × 确定性执行的分离架构

> **统一主线**：TNS 2026-08-06 四连发（AWS Dogwood / AWS Kiro / Anthropic git worktree / Todoist 反例）看似四个独立新闻，实为同一架构决策的四个实现层——**把 Agent 系统拆成「概率性生成」（LLM 提出候选动作）与「确定性执行」（运行时验证、承载、调度、执行）两个域，并将正确性责任从模型转移到运行时**。本文在上午趋势性分析（三重落地信号）基础上做技术深潜：技术框架（分层结构）、架构（组件与边界）、底层原理（为什么这样设计、机制是什么）、应用方案（怎么落地）。

- **素材**：TNS 8/6 四篇全文一手抓取（Dogwood `aws-dogwood-agent-policies` / Kiro `kiro-agent-client-protocol` / worktree `agent-native-runtime-branching` / Todoist `doist-ai-automation-code`）
- **日期**：2026-08-07 | **领域**：Agent 工程 / 运行时护栏
- **姊妹篇**：[三重落地信号（趋势版）](2026-08-07-agent-runtime-guardrails-agentic-aiops-800v-hvdc-deep-analysis.md)（同日同目录，本文为技术深潜）

## TOC

1. [四连发矩阵：四个实现层](#1-四连发矩阵四个实现层)
2. [Dogwood：序列级策略语言（验证层）](#2-dogwood序列级策略语言验证层)
3. [Kiro：ACP 协议边界（边界层）](#3-kiroacp-协议边界边界层)
4. [Anthropic worktree：分层分支原语（承载层）](#4-anthropic-worktree分层分支原语承载层)
5. [Todoist 反例：manifest 编译模式（执行层）](#5-todoist-反例manifest-编译模式执行层)
6. [统一架构：概率生成 × 确定性执行的完整谱系](#6-统一架构概率生成--确定性执行的完整谱系)
7. [底层原理：为什么正确性必须离开模型](#7-底层原理为什么正确性必须离开模型)
8. [应用方案：本系统映射](#8-应用方案本系统映射)
9. [批判性审视](#9-批判性审视)
10. [预测 P1-P5](#10-预测-p1-p5)
11. [参考来源](#11-参考来源)

---

## 1. 四连发矩阵：四个实现层

| 连发 | 主体 | 层 | 核心机制 | 一句话 |
|:--|:--|:--|:--|:--|
| **Dogwood** | AWS | 验证层 | 时序策略语言（Cedar 扩展） | 工具调用"合法但 wrong"→序列级拦截 |
| **Kiro** | AWS | 边界层 | ACP 协议 + Cedar 能力模型 | Agent 从编辑器解耦，向独立服务演进 |
| **worktree** | Anthropic | 承载层 | 分层分支原语（branch-based dev） | 隔离模型有了，承载它的存储/调度还是旧的 |
| **Todoist** | Doist | 执行层 | manifest 编译（AI 生成→代码执行） | "更少的 AI 带来更多产出" |

四层沿 Agent 请求生命周期排列：**生成候选（LLM）→ 验证（Dogwood）→ 边界传输（Kiro/ACP）→ 承载运行（worktree）→ 执行产出（Todoist 的确定性代码）**。前三个是"加护栏"，第四个是"撤模型"——同一个方向的两面：**模型只做它擅长的事（生成意图），其余全部交给确定性系统**。

---

## 2. Dogwood：序列级策略语言（验证层）

### 2.1 技术框架：Cedar → Dogwood 的两级演进

```
Cedar（无状态授权）                Dogwood（有状态时序授权）
─────────────────────            ─────────────────────
单请求决策                        序列级决策
给定相同请求 → 相同决策            参考"之前发生了什么、多久前"
易于分析（纯函数式）               表达前置条件/速率限制/顺序约束
re:Invent 2025 AgentCore Policy  2026-08-06 开源（Apache 2.0）
CNCF sandbox（2025 底捐赠）       任何 Cedar 策略 = 合法 Dogwood 策略
```

**关键设计决策：向后兼容**——Dogwood 不替换 Cedar 而是扩展它。时序条件被翻译成 Cedar 的 context 字段，参考实现从事件历史填充该字段后再交给 Cedar 决策。这意味着现有 Cedar 策略零改写迁移。

### 2.2 架构：AgentCore Gateway 插桩

```
Agent (LLM) ──提出工具调用──► AgentCore Gateway ──验证通过──► 外部工具
                                  │
                                  ▼
                          Dogwood 策略引擎
                          （默认拒绝 + 显式禁止优先）
                                  │
                                  ▼
                          事件历史（时序条件的数据源）
```

- 动作 schema 从 Gateway 的 **MCP manifest 自动生成**——每个工具 = 一个策略可引用的 action；
- 模型被排除在强制循环之外（"keeps the model itself out of the enforcement loop"）——这正是 08-05 Harness 理论「工具收窄把图灵完备输出收窄为可验证接口」的运行时实现。

### 2.3 底层原理：Metric First-Order Temporal Logic（MFOTL）

Dogwood 的时序表达能力构建在 **Metric First-Order Temporal Logic（度量一阶时序逻辑）的子集**上，可表达的操作：

| 操作 | 示例 |
|:--|:--|
| 事件是否发生 | 审批工具对同一股票+股数返回过正值响应吗？ |
| 时间窗口计数 | 过去 1 小时内发起过几次转账？ |
| 计数不同值 | 过去 1 小时涉及几个不同收款人？ |
| 值求和 | 过去 1 小时转账总额？ |

**并发窗口问题**（最锋利的细节）：若策略只统计"已完成"转账，agent 可在第一个 $2,000 完成前连续提交三个 $2,000——检查时已完成总额仍为 0，绕过 $5,000/小时限制。Dogwood 统计**包括正在评估中的请求**，第三个 $2,000 被拒。→ 时序验证必须覆盖"在途请求"而非仅"已确认事件"，这是有状态验证相对无状态验证的本质增量。

### 2.4 应用方案：事件历史的信任问题

AWS 原文点破开源采用的最大障碍：*"the harder question is whether the event history is complete and trustworthy enough to use for authorization."* 生产化清单（repo 明示）：

- 可信时间戳 + 事件认证（防伪造/重放）
- 字段/动作命名一致（防 schema 漂移）
- 轨迹持久化 + 授权决策日志（可审计）
- 租户间历史隔离 + 保留策略（工具调用历史含敏感数据）

**代价**：Dogwood 有状态 = 更贵（保留+搜索事件记录，评估时间依赖历史长度）；开源参考解释器定位为探索/测试工具，**非生产授权引擎**。未来路线：绝对时间规则（午夜重置配额）、liveness 属性（期望动作最终发生）、多 agent 系统（交接/共享锁）。

---

## 3. Kiro：ACP 协议边界（边界层）

### 3.1 技术框架：三 harness → 单进程 + 协议

```
旧架构（三套 harness）              新架构（ACP 统一）
─────────────────────            ─────────────────────
IDE = TypeScript harness         单一独立 agent harness
CLI = Rust harness               （独立进程，与 workspace 并列）
Web = Python harness             ────────►
                                客户端 ⇄ ACP 协议 ⇄ Agent
```

**演进逻辑**（工程史的经典教训）：早期用共享库保持分离失败——客户端逐渐伸手进 agent 内部 API，边界日益多孔。**把 agent 移入独立进程 + 协议通信**解决了这个问题：执行环境成为实现细节（本地工作站 or 云沙箱，客户端无感知）。

### 3.2 架构：标准协议 + 命名空间扩展

- **协议**：ACP（Agent Client Protocol），Zed 起源、JetBrains 联合开发；
- **扩展策略**："协议保持标准，差异化通过扩展"——20+ agent-callable 方法、15 client-callable 方法、20 通知类型，全部 `_kiro/` 命名空间隔离；
- **双传输**：WebSocket（web/iOS 客户端）+ ACP 标准 stdio（本地执行）；
- **统一配置模型**：自定义 agent、生命周期 hooks 在 Kiro 全表面共享。

### 3.3 底层原理：LSP 类比与 N×M → N+M

```
LSP（2016）:  编辑器 ⇄ 语言智能      → 语言服务器可插拔
ACP（2026）:  开发者体验 ⇄ Agent 实现 → Agent 可替换组件
```

集成复杂度从 **N×M（每编辑器 × 每 agent 定制集成）降到 N+M（各接标准协议）**。作者点破结果：*"Once the client-agent boundary is standardized, agents become replaceable components rather than tightly coupled features embedded within individual developer tools."*

**ACP vs MCP**（易混淆）：MCP 标准化 **agent↔外部工具**；ACP 标准化 **客户端↔agent**。互补的两个栈层，非竞争。

### 3.4 底层原理：治理成为新竞争层

协议标准化把差异化逼向别处——**权限/治理成为主战场**：

```
旧：CLI = regex allow/deny 列表；IDE = 前缀匹配（两套不兼容系统）
新：统一 Cedar 能力模型（功能类抽象）
    fs_read / fs_write / shell / web_fetch / mcp / subagent
    （deny fs_read = 阻止所有文件读取，无论哪个工具执行）
多 scope 求值：MDM > user > workspace > agent profile > session
显式 deny 优先
```

能力模型围绕**功能意图**而非单个工具——权限粒度从"工具名"升级到"操作类别"，这是把 Agent 当"身份主体"而非"进程"来治理的架构信号。

### 3.5 生态现状（2026-08 时点）

| 玩家 | 状态 | 信号 |
|:--|:--|:--|
| Microsoft | Intelligent Terminal 0.1（Build 6 月） | 实验性 ACP 客户端，可发现本地 agent CLI |
| JetBrains | Junie 进 ReSharper 2026.2（7 月） | "协议支持的早期步骤" |
| **VSCode** | **未采纳 ACP** | 最大编辑器缺席——"协议靠架构优点而非分发取胜" |

---

## 4. Anthropic worktree：分层分支原语（承载层）

### 4.1 技术框架：问题陈述

Anthropic 文档把 **worktree per session** 作为并行运行 agent 的默认方式。一个开发者监督 4 个 coding agent = 4 个在途变更并行向 merge 推进。这暴露结构性缺口：

> "Coding agents removed the cap. The branch can no longer stop at the code layer." —— 分支在代码层免费，代码层以下全缺。

### 4.2 量化证据：下游到达率未被尺寸化

Faros AI 遥测（**>10,000 开发者**）：

| 指标 | 高 AI 采用团队 |
|:--|:--|
| Merge 的 PR 数 | **+98%** |
| Review 时间 | **+91%** |

→ 代码生成的速度提升，下游（review、staging、数据库、队列）没有按比例扩容。

### 4.3 底层原理：瓶颈 = 变更触碰的第一个共享资源

```
4 个 agent → 4 个 worktree（代码层并行，毫秒级）→ 进入共享层全部排队：
  staging cluster / seed database / message queue / dependent services
                    ↑ 单点串行化
```

**Agent 不会等待**（与人类开发者的关键差异）：被阻塞的 agent 要么空闲持有过期视图，要么用 mock 硬闯验证；监督者上下文切换。等共享环境释放时，agent 视图已过期。

> "The bottleneck isn't code generation, and it isn't review capacity alone. It's the first shared resource a change touches."—— 不能运行的 branch = 不能被信任的 branch。

### 4.4 底层原理：branch-based development（分层分支模式）

出路 = **把 git 的机制推广到每一层**：*"branches are cheap because they share everything unchanged and carry only the delta"*（copy-on-write：共享不变部分，只带增量）。各层各自发现了同一想法：

| 层 | 分支原语 | 成熟度 |
|:--|:--|:--|
| 代码 | git worktree | ✅ 20 年成熟 |
| CI | per-branch pipeline + build cache（copy-on-write 复用未变工件） | ✅ 十年前学会 |
| 前端 | Vercel/Netlify preview deploys（每分支不可变构建+共享托管路由） | ✅ 默认行为 |
| 数据库 | Neon/PlanetScale/Xata（copy-on-write 视图、秒级、迁移在 production-shaped 数据验证） | ✅ 已商用 |
| **微服务运行时** | 环境沙箱（live traffic、service graph、依赖网络） | ⚠️ 抵抗最久 |

金句：*"If the layer with the most state can hand out branches in seconds, statelessness was never the real requirement. Whatever is still unbranched is unbranched by choice."* —— 状态不是借口，未分支是选择。

---

## 5. Todoist 反例：manifest 编译模式（执行层）

### 5.1 技术框架：Automations 的生成-执行分离

```
用户自然语言请求
      │ AI（生成期：理解意图）
      ▼
   manifest（自动化定义）
      │ 触发器/定时任务
      ▼
   普通代码执行（执行期：零 LLM）
```

Doist CTO Gonçalo Silva 的原话直击原理：*"When you create an automation that you expect to run every time and to be consistent and predictable, you already have a problem because AI is not predictable and consistent by design."*

### 5.2 底层原理：为什么执行期必须撤掉模型

1. **可预测性**：自动化要第 10 次、第 100 次运行结果一致——概率模型违背这个要求；
2. **成本**：CPU 跑代码 vs 每次调用昂贵模型；模型不必每次重新发明流程；
3. **配置复杂度归零**："No configuration model, no tool call limits, no temperature settings"——用户只描述意图，得到自动化；
4. **模型不可知**：18 语言 × 每语言数十场景的测试套件检查模型更换是否改变行为；先大模型跑通、再小模型降成本（早期几百用户 beta 产生巨额账单）。

### 5.3 产品哲学：subtraction over addition

- **Goals 退役**（2026-07-13）：投入重但数据不达标；即使只是实验功能也引发社区反弹——"如果一直加东西，很快对谁都不好"；
- **18 个 AI 原型被丢弃**（含 project summarization）——"AI 是新积木，我们还没有足够经验在真实项目中使用它"；
- **专家判断不可外包**："the expert is the expert"——PM 分不清"能用的 PR"与"长期可维护的 PR"，工程师能。AI 降低创作门槛，但不应降低交付质量棒。

### 5.4 与知识库"AI 产出经济学"互证

Todoist 是知识库 [AI 产出经济学](../../03_AI/methodology/2026-08-05-ai-output-gross-vs-net-entropy.md) 的工程化样本：**产出是毛利不是净利**——盲目加 AI 功能 = 毛产出增加但熵增修复（Goals 维护成本、社区反弹、模型切换成本）吃掉净产出。Todoist 用"减法"做净值管理：**功能准入制 + 质量棒不变 + 执行确定性**。而 [AI 采用方法论](../../03_AI/methodology/2026-08-06-ai-adoption-creation-methodology.md) 的"创作优先于修补"在此获得反例维度：**让 AI 创作（生成 manifest），让代码执行（确定性运行）**——AI 的创作价值被确定性外壳放大。

---

## 6. 统一架构：概率生成 × 确定性执行的完整谱系

四连发统一到一个架构决策——**在生成与执行之间建立确定性边界**：

```text
┌────────────────────────── 概率性生成域（LLM） ──────────────────────────┐
│  意图理解 / 候选动作生成 / 方案构思            （模型强项：语义、推理）    │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │ 确定性边界
        ┌───────────────────────┼───────────────────────────┐
        ▼                       ▼                           ▼
  ① Dogwood 验证层        ② Kiro 边界层               ③ worktree 承载层
  时序策略拦截错误调用      ACP 协议传输                分支原语提供隔离
  （MFOTL 断言）            （N+M 集成）                 （copy-on-write）
        └───────────────────────┼───────────────────────────┘
                                ▼
┌────────────────────────── 确定性执行域（运行时） ────────────────────────┐
│  ④ Todoist：manifest 编译后由普通代码执行（零 LLM，可预测、可审计、便宜）  │
└──────────────────────────────────────────────────────────────────────────┘
```

**四连发 = 同一个命题的四个操作化**：模型只负责"决定做什么"，系统负责"保证做得对、隔得开、跑得起、花得值"。这正好完成知识库 08-05 的闭环论断——[Harness 是 Agent 的进程](../../03_AI/agent-engineering/2026-08-05-harness-os-process-boundary-isomorphism.md)：**进程的职责（系统调用验证、地址空间隔离、资源记账）正在被 Agent 运行时逐项补齐**：Dogwood=系统调用验证、worktree=地址空间隔离、Kiro=进程边界、Todoist=进程内确定性执行。与 [Harness 实证化四篇](../../03_AI/agent-engineering/2026-08-07-harness-empirical-four-papers.md) 的 Skill-Use 结论（最强配置 SU 仅 0.613）互证：**模型端正确性已触顶，增长空间在运行时端**。

---

## 7. 底层原理：为什么正确性必须离开模型

### 7.1 三层不可约理由

| 理由 | 机制 | 证据 |
|:--|:--|:--|
| **可验证性** | 概率输出无法形式化断言，时序逻辑可以 | Dogwood 用 MFOTL 表达"审批后 1 小时内、同股票同股数" |
| **可预测性** | 自动化要求第 100 次 = 第 1 次 | Todoist："AI is not predictable by design" |
| **可审计性** | 责任必须落到可配置工程系统 | Kiro 多 scope 策略 + 显式 deny 优先 |

### 7.2 与模型能力平台期的关系

GPT-5.6 Sol「单点提升、他处持平」（同日 TNS）——模型边际收益递减 → Agent 系统质量瓶颈从"模型会不会"转移到"运行时让不让人犯错"。**正确性分层**：模型生成候选、运行时验证候选；验证逻辑从概率世界搬到确定性世界。**责任前移**：出错归因从"模型不够聪明"变为"护栏配置不当"——可配置、可测试、可回滚。

---

## 8. 应用方案：本系统映射

1. **CowAgent 已是 Todoist 模式的实践者**：scheduler（cron 确定性触发）+ 50+ check 脚本（确定性门禁）+ 三同步流程（确定性步骤）——"AI 生成内容、代码执行验证"在本系统已是默认工作流；
2. **技能调用验证（Dogwood 类比）**：参照 [技能评测缺口](../../03_AI/agent-engineering/2026-08-07-skill-use-eval-gap-deep-analysis.md) 的 SKT 双层验证器，给高价值技能调用加"时序断言"（如：归档前必须已运行 index 重建；commit 前必须 link-validator 通过）——把"合法但 wrong"的调用前置拦截；
3. **分层分支意识（worktree 类比）**：知识库 git 已用分支隔离大重构（kb-rename 1019 文件等），但"索引/日志共享层"仍是单点——多分支并行写作时 index/log 冲突是当前真实瓶颈，可探索"索引 per-branch + 合并时重建"；
4. **减法治理（Todoist 类比）**：技能库 40+ 技能可做"功能准入审计"——从未触发的死技能（Skill Coverage 的 38-46% 覆盖率教训）退役或合并；
5. **协议边界意识（Kiro 类比）**：CowAgent 的 Harness 已按协议解耦（五层依赖单向化）——保持"客户端-代理"边界为协议而非内部 API 渗漏，是长期可维护性红线。

---

## 9. 批判性审视

1. **Dogwood 开源版非生产级**：参考解释器定位探索/测试；事件历史可信性（时间戳、认证、保留、租户隔离）是横亘在生产化前的硬问题——AWS 自己的路线图也未给出生产引擎时间表；
2. **Kiro 的"标准化外壳 + 私有扩展"悖论**：20+ `_kiro/` 扩展可能演变为事实私有协议（类似早期 MCP 的教训）；VSCode 缺席意味着生态尚未到临界点；
3. **worktree 的 Faros AI 数据是相关性非因果**：+98% PR / +91% review 时间可能是 AI 采用团队本身规模/节奏差异，非直接因果；"branch-based development" 是愿景，微服务运行时分支尚无成熟产品；
4. **Todoist 单产品经验**：任务管理场景（触发式、短流程）天然适合 manifest 编译，不必然外推到长时程、开放域 Agent（如编码 agent）；manifest 生成本身仍依赖 LLM 质量——错误 manifest = 确定性执行确定性错误；
5. **四连发均为厂商视角**：AWS×2 + Anthropic + Doist，缺第三方独立验证；"正确性从模型转移到运行时"符合厂商利益叙事（可销售护栏产品）；
6. **未覆盖的第三域**：生成域自身的验证（如 SKT 的验证数据、评测基准）在四连发中缺席——正确性不能只靠运行时兜底，生成端质量门控（评测/验证数据）仍是必要补充。

---

## 10. 预测 P1-P5

- **P1（高置信）**：时序策略语言（Dogwood 路线）2027 年成为主流 agent 框架的治理内置组件，MCP 工具清单自动生成策略 schema 成为默认；
- **P2（高置信）**：ACP 成为客户端-代理事实标准（VSCode 或等效编辑器 2027 年前采纳/推出等效协议），"选编辑器与选 agent 独立"成为开发者默认心智；
- **P3（中置信）**：数据库分支 + 环境沙箱成为 agent CI 默认承载（worktree 模式向数据层/运行时层渗透），"每 PR 一个 production-shaped 环境"成标配；
- **P4（中置信）**："生成-执行分离"成为 agent 应用设计模式（Todoist 模式）——"每次运行都调 LLM 的自动化"被明确视为反模式；
- **P5（低置信）**：Agent 承载层（运行时基础设施）成为新赛道（类比 2015 容器化），出现"Agent 运行时即服务"厂商。

## 11. 参考来源

- [AWS Dogwood：Your AI agent's next tool call may be valid but wrong](https://thenewstack.io/aws-dogwood-agent-policies/) — TNS 2026-08-06（全文抓取）
- [AWS Kiro：Free agents — untie agents from editors](https://thenewstack.io/kiro-agent-client-protocol/) — TNS 2026-08-06（全文抓取）
- [Anthropic worktree：Runtime infra makes that a problem](https://thenewstack.io/agent-native-runtime-branching/) — TNS 2026-08-06（全文抓取）
- [Todoist：Why less AI can deliver more](https://thenewstack.io/doist-ai-automation-code/) — TNS 2026-08-06（全文抓取）
- 本地姊妹篇：[三重落地信号（趋势版）](2026-08-07-agent-runtime-guardrails-agentic-aiops-800v-hvdc-deep-analysis.md)
- 本地：[Harness 实证化四篇](../../03_AI/agent-engineering/2026-08-07-harness-empirical-four-papers.md)、[Harness 进程边界](../../03_AI/agent-engineering/2026-08-05-harness-os-process-boundary-isomorphism.md)、[AI 产出经济学](../../03_AI/methodology/2026-08-05-ai-output-gross-vs-net-entropy.md)、[AI 采用方法论](../../03_AI/methodology/2026-08-06-ai-adoption-creation-methodology.md)、[技能使用评测缺口](../../03_AI/agent-engineering/2026-08-07-skill-use-eval-gap-deep-analysis.md)

---

> **诚实标注**：四篇素材均为 TNS 一手报道全文级抓取（非二手转述），但 TNS 为行业媒体非厂商官方文档——Dogwood/Kiro 的技术细节以 TNS 转述为准，未核验 AWS 官方 repo；Faros AI 数据为 TNS 引用，原始研究方法未核验；"概率生成×确定性执行"框架为本文归纳，非四家厂商的官方表述。

---

## Changelog

- 2026-08-07：创建。素材=TNS 8/6 四篇全文一手抓取；框架=四层实现矩阵（验证/边界/承载/执行）+ 统一命题（概率生成×确定性执行分离）；与上午三重落地信号成「趋势-技术深潜」姊妹篇。
