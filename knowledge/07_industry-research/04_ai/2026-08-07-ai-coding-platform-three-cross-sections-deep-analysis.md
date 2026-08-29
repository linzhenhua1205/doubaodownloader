# AI 编程平台三横切：可审查性 × 成本治理 × 协议边界

> 深度分析 | 2026-08-07 | 素材：GitHub 官方文档 + Changelog ×4、Cursor 官方 Blog ×3（含 Router 技术原文）、JetBrains 官方 Blog ×2 + AI Credits 条款
> 主线：**AI 编程平台从「生成工具」走向「交付系统」的三个横切面——产出可审查（质量维度）、用量可治理（成本维度）、能力可组合（边界维度）**

---

## 📑 TOC

- [一、执行摘要](#一执行摘要)
- [二、可审查性：AI 交付的新质量维度](#二可审查性ai-交付的新质量维度)
  - [2.1 问题：审查成本成为新的稀缺](#21-问题审查成本成为新的稀缺)
  - [2.2 三层递进：工具化 → 配置即代码 → 结构内建](#22-三层递进工具化-配置即代码-结构内建)
  - [2.3 GitHub 的「可审查性内建」全景](#23-github-的可审查性内建全景)
- [三、成本治理：三平台收敛于四段式闭环](#三成本治理三平台收敛于四段式闭环)
  - [3.1 四段式框架：度量 → 归属 → 配额 → 优化](#31-四段式框架度量-归属-配额-优化)
  - [3.2 GitHub：credits 池 + 成本中心 + 三层预算](#32-githubcredits-池-成本中心-三层预算)
  - [3.3 Cursor：Router（Compass + Taxonomy）与双池](#33-cursorroutercompass-taxonomy与双池)
  - [3.4 JetBrains：AI Credits 计量 + 双轨 + 每用户配额](#34-jetbrainsai-credits-计量-双轨-每用户配额)
  - [3.5 三平台对比与收敛本质](#35-三平台对比与收敛本质)
- [四、协议边界：开放 vs 垂直集成的能力划界](#四协议边界开放-vs-垂直集成的能力划界)
  - [4.1 能力边界由协议而非产品划定](#41-能力边界由协议而非产品划定)
  - [4.2 JetBrains Goes LSP：智能外溢](#42-jetbrains-goes-lsp智能外溢)
  - [4.3 Cursor 插件生态：MCP + Skills 捆绑](#43-cursor-插件生态mcp-skills-捆绑)
  - [4.4 GitHub 开放 Agent 自动化](#44-github-开放-agent-自动化)
  - [4.5 开放与集成的辩证](#45-开放与集成的辩证)
- [五、三横切的统一第一性原理](#五三横切的统一第一性原理)
- [六、对服务器 / AI 基础设施领域的启示](#六对服务器-ai-基础设施领域的启示)
- [七、交叉链接](#七交叉链接)
- [八、诚实标注](#八诚实标注)
- [Changelog](#changelog)

---

## 一、执行摘要

2026 年 7 月下旬到 8 月初的三周内，AI 编程平台（GitHub Copilot、Cursor、JetBrains）密集发布了一批看似互不相关的功能更新。把它们放在一起看，三条清晰的横切主线浮现出来：

1. **可审查性成为 AI 交付的新质量维度**：GitHub 把 code review 从「手动请求」升级为「可配置的自动 Agent」（自定义指令、防火墙、独立 runner、head-branch 读取），把 code scanning 的扫描策略做成「配置即代码」（`codeql-analysis.yml` + `codeql-config.yml`），用 **stacked PR** 把「大变更拆分」内建为平台原语（2026-07-30 公开预览），并在 Issues 自动化中加入 **Approvals / Confidence / Rationale** 三件套（2026-07-23）。平台不再只是「产出代码」，而是把「AI 产出可审查」写进交付结构本身。
2. **AI 成本治理收敛于四段式闭环**：GitHub（AI credits 池 + 成本中心 + 三级预算）、Cursor（Agent Router：Compass 复杂度预测 + 任务分类路由，Auto Intelligence 降本 68%）、JetBrains（AI Credits 计量 + 预付/后付双轨 + 每用户配额）——三个平台不约而同地实现了「**度量 → 归属 → 配额 → 优化**」的完整治理回路。AI 编程从「订阅制固定成本」彻底转向「计量制可变成本」，成本治理从可选功能变成平台标配。
3. **能力边界由协议而非产品划定**：JetBrains 把 IntelliJ IDEA 的 Java/Kotlin 智能以 **LSP** 形式开放给 VS Code、Cursor 和 agentic 流程（2026-08）；Cursor 用 **MCP + Skills 捆绑**的插件生态连接工具栈（2026-02 上线 Marketplace，03 月 +30 插件）；GitHub 通过 **automations、REST/GraphQL API、Copilot SDK** 把 cloud agent 开放为可编程自动化（评论触发、issues 意图、第三方集成）。协议（LSP/ACP/MCP/API）成为能力流通的通用货币，产品边界让位于协议边界。

**统一判断**：AI 编程平台正在经历从「生成器」（帮你写代码）到「交付系统」（帮你把代码安全、可控、可审计地交付）的跃迁。可审查性解决「AI 产出如何被信任」，成本治理解决「AI 产出如何被计量」，协议边界解决「AI 能力如何被组合」——三者共同回答一个问题：**当 AI 承担越来越多的实现工作，平台如何让组织仍然拥有判断力、预算权和集成权。**

---

## 二、可审查性：AI 交付的新质量维度

### 2.1 问题：审查成本成为新的稀缺

传统软件工程中，「写代码」与「审代码」的成本大致同量级；AI 编程把「写」的成本压到接近零后，**审查成为唯一的稀缺环节**。这个转移带来两个后果：

- **审查瓶颈**：TED CTO Andy Merryman 在 stacked PR 公告中的观察极具代表性——「AI 让 TED 的开发者生产力大幅提升，但这创造了新瓶颈：PR 大到审阅者难以消化。」（*AI has made TED's developers dramatically more productive, but that created a new bottleneck: PRs were growing large enough that reviewers were struggling.*）
- **审查质量**：大 PR 的审查是「走过场式」的——审阅者无法在小块逻辑里真正理解变更。Next.js 负责人 Tim Neutkens 的结论是 stacked PR 帮助 Vercel「引入更小的独立变更，同时交付更大的功能，让 PR 更容易审查」。

> **第一性原理**：AI 产出的单位价值 = 生成成本 / (生成成本 + 审查成本)。当生成成本趋近于零，审查成本决定价值的全部。因此「降低审查成本」成为 AI 交付系统最重要的优化目标——而降低审查成本最有效的方式不是让审查工具更好用，而是**改变交付的结构**，让变更天然以「可审查单元」的形态存在。

### 2.2 三层递进：工具化 → 配置即代码 → 结构内建

可审查性在 GitHub 生态中沿三层递进展开：

| 层级 | 机制 | 本质 | 关键证据 |
|:--|:--|:--|:--|
| **L1 工具化** | Copilot code review | AI 作为「审阅者」加入 PR 流程，替代一部分人工初审 | 请求审查 <30 秒；只留 Comment 不 Approve/Request changes（不阻塞合并、不计入必需审批） |
| **L2 配置即代码** | code scanning 工作流 + 审查指令文件 | 扫描策略、审查准则、环境配置全部版本化进仓库 | `codeql-analysis.yml`、`codeql-config.yml`、`copilot-instructions.md`、`AGENTS.md`、`REVIEW.md` |
| **L3 结构内建** | stacked PR + Issues 自动化三件套 | 变更拆分、AI 行为的置信度与理由成为平台原语 | stacked PR 公开预览（2026-07-30）；Approvals/Confidence/Rationale（2026-07-23） |

三层的关键差异在于**审查的「发生方式」**：L1 是「人主动请求 AI 审查」（pull 模式），L2 是「策略写进仓库、自动执行」（声明式），L3 是「平台把可审查性编进变更与 Agent 行为的 DNA」（结构性）。

### 2.3 GitHub 的「可审查性内建」全景

**① Copilot code review：从手动请求到可配置自动审查**

- **请求方式**：PR 侧边栏一键 Request（<30 秒出结果）；`gh pr create --reviewer @copilot`；REST API `copilot-pull-request-reviewer[bot]`。
- **审查语义**：只留「Comment」类型，不 Approve 也不 Request changes——**AI 不拥有批准权**，这保证审查权威仍在人（与 08-05「Harness 即适配层」的权限收窄哲学同源）。
- **可配置性**（2026-07-17 大版本更新）：
  - 指令从 **head branch** 读取（`copilot-instructions.md` / `*.instructions.md` / agent skills / `AGENTS.md`）——可以在特性分支里测试审查指令而无需先合并；
  - 新增读取 `REVIEW.md` / `GEMINI.md` / `CLAUDE.md`——团队已有的审查准则、模型专属指令自动被吸收；
  - **`copilot-code-review.yml`** 工作流文件定义审查环境（安装依赖、独立于 cloud agent 的 runner 配置）；
  - **防火墙默认启用**：审查期间限制网络访问，仓库/组织级独立配置（注意：self-hosted runner 暂不支持防火墙）；
  - 组织级 runner 配置与 cloud agent **拆分独立**。
- **MCP 与 agent skills**（2026-07-29 GA）：审查可使用仓库配置的 MCP 服务器（GitHub MCP、Playwright MCP 默认启用）与 `code-review` 技能目录；每条评论底部显示**归因**（用了哪个 skill/MCP），可从 PR timeline 打开会话日志核对工具调用——**审查本身的审查**。

**② code scanning：配置即代码的完整形态**

- 扫描策略以 `codeql-analysis.yml`（触发事件：push / pull_request / schedule）+ `codeql-config.yml`（查询集、packs、paths 排除、威胁模型）版本化进仓库；
- 查询集分层：`security`（默认）→ `security-extended`（+低严重度）→ `security-and-quality`（+可维护性/可靠性）；
- 外部仓库可引用共享配置 `remote=OWNER/REPO@REF:FILEPATH`——**跨仓库的扫描策略复用**；
- 结果以 **SARIF** 标准格式输出，`category` 区分 monorepo 多分析；merge protection 用 ruleset 把「指定严重度的 code scanning 告警」变成合并门禁。
- 意义：扫描策略从「管理员的 UI 操作」变成「仓库里的 YAML 文件」——**可 review、可版本化、可审计、可跨仓库复用**，与代码同生命周期。

**③ stacked PR：把「变更拆分」内建为平台原语**（2026-07-30 公开预览）

- **机制**：`gh extension install github/gh-stack`；每个 PR 是变更的一个「层」（layer），层与层之间以「下层的 PR 作为目标分支」串成有序栈；`gh pr create` 一次创建整栈。
- **审查**：打开栈中任一 PR 只看该层 diff；PR 顶部有 **stack map** 展示当前层在整个变更中的位置；不同成员可并行审查不同层，互不阻塞。
- **合并**：合并最上层就一键落地它及以下所有未合并层；只落地部分时，上方 PR 自动 rebase 并 retarget。merge queue 支持正在滚动上线。
- **AI 协同**：GitHub Copilot 可用 `gh-stack` skill 直接创建/维护栈——**AI 生成的大变更被强制切成可审查单元**（jQuery 作者 John Resig：「用 merge queue 一次性落地 5 个 stacked PR！移除了大量摩擦（gh CLI 工具 + agent skill 帮了大忙）」）。
- 定位：这是「可审查性内建」的最强信号——GitHub 不再只是提供「AI 审代码」，而是提供「AI 写的东西以人类可审的粒度存在」的结构保证。

**④ Issues 自动化三件套：Approvals / Confidence / Rationale**（2026-07-23 公开预览）

这是「AI 行为可审查」在 issue 域的落地，三件套互为表里：

| 机制 | 含义 | 设计意图 |
|:--|:--|:--|
| **Approvals** | 自动化可配置为「建议」（suggest）而非「直接应用」（apply）；建议进入 issue 面板等待接受/拒绝 | 把「AI 改了什么」从隐式变显式，人决定自动化程度 |
| **Confidence** | Agent 对每个动作标注 high / medium / low 置信度；**high 自动应用，medium/low 保留为建议** | 用置信度做「自动化与人工」的自动分级，人只花时间在最可能需要复查的变更上 |
| **Rationale** | 每个动作记录理由（无论自动应用还是等待审查），形成「改了什么 + 为什么」的审计追踪 | 可追溯性：AI 行为变成可审计的决策记录 |

- 技术细节：`issue-intents: true` 写入 Agentic Workflows frontmatter（向后兼容）；REST / GraphQL API 可用；`has:suggestions` 搜索过滤待审建议；管理员可设 confidence 阈值。
- **重要免责声明（GitHub 原文）**：*Approvals are a workflow convenience, not a security control*——建议机制不是服务器端安全边界，有权限的 agent 可以直接应用而非建议。**「可审查」是工作流便利，不是安全控制**——这个边界诚实标注得非常好。

---

## 三、成本治理：三平台收敛于四段式闭环

### 3.1 四段式框架：度量 → 归属 → 配额 → 优化

AI 编程成本从「订阅制固定成本」转向「计量制可变成本」后，治理必须形成闭环。三个平台在 2026 年 7 月的发布不约而同覆盖了同一四段式：

```
Measure -> Attribute -> Enforce -> Optimize
   |            |             |            |
 credits      cost center   budget      Router/
 visible      accountable  per-user     self-hosted
                       limit        model
```

- **度量**：AI credits 用量对用户可见（GitHub 2026-07-20：即使无个人预算也能看到本月 credits 用量，此前只有预算百分比、无法语境化 token 用量）。
- **归属**：成本中心（cost center）把用量映射到业务单元/项目。
- **配额**：用户级 / 成本中心级 / 企业级三级预算；达到上限可「停止用量」而非仅告警。
- **优化**：路由器把请求分给性价比最优的模型；自研模型压低单位成本。

### 3.2 GitHub：credits 池 + 成本中心 + 三层预算

（来源：GitHub Docs *Managing your company's spending on GitHub Copilot*）

- **计量单位**：每个 Copilot 许可证包含 **AI credits 池**（企业内共享）；池耗尽后额外用量按 **$0.01 / credit** 计费，受预算控制约束。
- **度量**：Billing & licensing > AI usage 可按 **user / model / organization / cost center** 过滤并导出分析。
- **归属**：**cost center** 把支出映射到业务单元（如试点项目组独立预算）；Metered usage 支持 `cost_center:ce-pilot-group` 查询、按 SKU 分组对比 Business/Enterprise 差异。
- **配额**：三级预算——**user-level**（单个用户每计费周期从共享池+额外用量的总上限）、**cost center 预算**、**enterprise spending limit**（池耗尽后的计量费用上限）。关键开关：**「Stop usage when budget limit is reached」**——未开启则达到上限只发通知、不阻断、费用继续累积。
- **许可治理**：识别能发许可的组织 owner（预算影响的源头）；API 识别 inactive user 回收许可；自服务领许可模式（GitHub 建议的 rollout 方式）。

### 3.3 Cursor：Router（Compass + Taxonomy）与双池

**① Agent Router：用真实流量学出来的模型路由**（2026-07-22 发布，08-06 技术原文）

Cursor Router 是成本治理「优化」环节的极致形态——**在模型层面做按需分配**：

- **效果**（相对 Opus 4.8）：Auto Intelligence 达到 Fable 级满意度、成本 **-68%**（发布后再降 18%）；Auto Balance 满意度优于 Opus 4.8、成本 **-41%**（再降 8%，满意度再 +3%）。
- **核心思想**：模型选择应该**从模型在真实开发者工作上的表现学习**，而不是从 benchmark 分数推断。
- **两阶段路由算法**：

```
route(x) = { price-efficient model (Grok),   Compass >= tau  (simple task stays cheap)
           { task router (frontier choose),  Compass <  tau  (complex task picks strong)
```

- **Compass（复杂度预测器）**：预测用户是否满意（性能信号从行为推断——继续下一任务=正信号，纠正 agent=负信号），得分 0~1 作为复杂度的代理。实测校准：Compass 判为最可能成功的 turn 有 **96% 正信号**，判为最不可能的有 71%——强预测力。**阈值 τ 是成本-质量旋钮**：调低留更多流量在便宜模型，调高更多升级到 frontier。
- **Taxonomy（任务分类）**：从真实流量学到三维分类——**domains**（backend / database schemas / frontend）、**tasks**（修 bug / 跑命令 / 写测试）、**modifiers**（bounded edits / product questions / visual-heavy）。**没有模型在所有类别都占优**：
  - **Grok**：常规宽泛工作（Git 命令、通用数据库操作），低推理成本；
  - **Sol**：规划与代码库理解，低成本下实现任务也强；
  - **Opus**：执行密集型（devops、数据库查询、性能优化）；
  - **Fable**：调试与视觉实现，质量增益在高复杂度任务上值回票价。
- **两条路由规则**：
  1. **只在性能明显更好时路由**：候选模型对该任务标签的观测表现需通过**单侧 75% uplift 阈值**（≈75% 置信度提升是真实的）；
  2. **预算内最优混合**：从合格候选中选「流量加权组合」，在模式预算内最大化性能增益。
- **数据与验证**：数十万 turns 的实时流量数据集（含上下文、模型切换效应、**切换模型导致的 cache miss 成本**——benchmark 常忽略）；离线交叉验证调参 + 留出集评估 + 在线流量实测（能捕获 token 用量、缓存、切换成本等离线难建模效应）。
- **演进**：已加入 Opus 5 到路由池；愿景是预测每个模型的期望质量与成本、从生产结果持续学习。

**② 双池计量：First-party 池 + API 池**（2026-02-11）

- 两个 usage pools：**first-party models pool**（Auto / Composer 1.5，限额显著更高，Composer 1.5 = Composer 1 的 3 倍，限时 6 倍）与 **API pool**（个人版每月至少含 $20 用量，更高档更多，可付费加量）。
- **自研模型（Composer 1.5）是成本治理的供给侧杠杆**：Terminal-Bench 2.0 上超过 Sonnet 4.5、低于顶级 frontier——「训练自己的模型让我们能以可持续方式提供显著更多的用量」。
- 需求侧（路由器）+ 供给侧（自研模型）双管齐下，是 Cursor 成本治理的完整拼图。

### 3.4 JetBrains：AI Credits 计量 + 双轨 + 每用户配额

（来源：JetBrains AI Credits Terms v1.0，2025-08-25 生效；business 客户 2026-07-07 后适用新版）

- **计量单位**：**AI Credits** = 一次性获得的 credits（付费或免费），用于兑换**超过订阅计划配额**的 JetBrains AI 服务；需活跃订阅才能使用；**非货币、非法定货币、不可在 JetBrains AI 外兑换**。
- **双轨**：
  - **预付（pre-paid）**：购买后 **12 个月有效期**，到期作废；
  - **后付（post-paid）**：企业可激活后付 credits，用户从**共享配额**兑换，企业**可为每个用户设置可兑换共享配额的上限**（*set limits for the shared AI Credits quota that can be redeemed by each User*）——这就是「每用户配额」治理的直接实现。
- **约束**：不可退款（法律要求除外）、不可转让到其他 JetBrains 账户。
- **2026.2 的 AI 侧配套**（2026-07）：native GitHub Copilot 集成、agent skills、第三方 provider 的 AI 补全支持——成本/计量/提供商选择在 IDE 层打通。

> 说明：用户主线提到的「JetBrains 10x 控本」中「10x」的具体出处未在官方源中确认（详见 §八 诚实标注）；本文以可确证的一手事实（AI Credits 条款 + 2026.2 发布）为准。

### 3.5 三平台对比与收敛本质

| 维度 | GitHub Copilot | Cursor | JetBrains AI |
|:--|:--|:--|:--|
| **计量** | AI credits（池内免费，超额 $0.01/credit） | 双池：first-party 池 + API 池（$20/mo 起） | AI credits（订阅配额 + 超额 credits） |
| **归属** | cost center → 业务单元 | （企业按团队/席位管理） | 共享配额（后付） |
| **配额** | 用户 / 成本中心 / 企业三级预算 + stop-usage 开关 | 池限额 + 付费加量 | 每用户可兑换共享配额上限 |
| **优化** | 模型选择（自带 + BYOK） | **Agent Router**（Compass + Taxonomy）+ 自研 Composer | 模型/提供商可选（第三方 provider 补全） |
| **可见性** | 用户可见每周期 credits 用量（2026-07-20） | 编辑器内双池用量监控页 | 账户内 credits 余额 |

**收敛本质**：三个平台在完全独立的产品线上，实现了同一套治理抽象——**用量可见（度量）→ 成本可记账（归属）→ 超额可拦截（配额）→ 单价可压低（优化）**。这不是巧合，而是「AI 成本从固定订阅变为按量计费」这一经济结构变化的必然产物：**当成本变得可计量且可变动，治理就必须变得可配置且可编程**。这与此前知识库中「AI 产出经济学（毛利 vs 净利）」的判断互为印证——平台侧把成本治理做成标配，正是承认「净产出 = 毛产出 − 治理成本」的行业共识。

---

## 四、协议边界：开放 vs 垂直集成的能力划界

### 4.1 能力边界由协议而非产品划定

AI 编程平台的核心资产从「编辑器功能」迁移到「智能 + 工具连接」。随之而来的结构性变化是：**能力边界从「产品界面」迁移到「协议界面」**——LSP（语言智能）、ACP（Agent Client Protocol，agent 连接）、MCP（工具连接）、REST/GraphQL API（平台能力开放）成为能力流通的通用货币。

> **第一性原理**：垂直集成（把能力绑进自家产品）获得的是体验控制权；协议开放（把能力用标准协议暴露）获得的是生态连接权。当 AI 生成成为主流、能力需要被任意编辑器/agent/自动化消费时，**协议覆盖的产品边界 > 产品覆盖的协议边界**——但两者不是替代关系，而是「体验层垂直、连接层水平」的分层。

### 4.2 JetBrains Goes LSP：智能外溢

JetBrains 2026-08 的「IntelliJ IDEA Goes LSP」是三个平台中最激进的协议开放信号：

- **动机**：agentic 开发让开发者手动编辑的时间越来越少，「可能只需要窄功能集——导航到声明、查找引用、简单补全、重命名」，而这些 LSP 全覆盖；**甚至 agent 也能用 LSP server——更快更确定的结果，最终减少 token 消耗**。
- **产品**：「Java & Kotlin by IntelliJ IDEA」扩展上架 VS Code Marketplace / Open VSX，把 IDEA 的 Java/Kotlin 语言技术以 **LSP** 形式提供给 VS Code 及其 fork（含 Cursor）：DAP 调试、智能补全/导航/分析、重构、Maven/Gradle/Bazel、大型 monorepo 性能。
- **许可**：预览期免费（每 build 30 天评估期）；预览后需 **IntelliJ IDEA Ultimate 订阅**——同一把许可证覆盖桌面 IDE、VS Code 系、其他受支持环境。
- **Kotlin LSP** 保持 **Apache-2.0 开源**、免费。
- **Agent 化**：内部试验显示同一 LSP 功能**显著改善终端 agentic 工作流（Claude Code / Codex）**，结果即将公布；「agent plugins」已在路上。
- **战略意义**：JetBrains 承认「最好的 Java/Kotlin 开发在 IDEA 内」，但同时把核心智能**外溢**到所有编辑器与 agent——**智能成为协议商品，IDEA 的护城河从「独占智能」转向「最优体验 + 协议标准制定权」**。这与 NVIDIA 把 CUDA 之外的推理智能开放、或 AMD 用 UALink 定义互联标准的逻辑同构。

### 4.3 Cursor 插件生态：MCP + Skills 捆绑

- **Cursor Marketplace**（2026-02 上线，2026-03 首批 +30 插件）：Atlassian / Datadog / GitLab / Glean / Hugging Face / monday.com / PlanetScale 等合作伙伴。
- **关键设计**：插件 = **MCP（能力）+ Skills（如何使用该能力的指令）捆绑**。官方观察：「这种组合比单独用 MCP 强大得多」——纯 MCP 只给 agent 工具，skills 给 agent 使用工具的方法。
- **分发包**：社区共享 + **Teams/Enterprise 的 team marketplace**（管理员分发管理私有插件）。
- **Automations**：cloud agents 可被定时/事件触发（Cursor Automations），配合 Datadog MCP 调查日志等——**agent 从交互式变成常驻式**。
- **意义**：Cursor 没有把工具集成做进自家产品（垂直集成），而是开放插件协议（水平连接）——工具栈的深度由生态决定，而非产品团队。

### 4.4 GitHub 开放 Agent 自动化

GitHub 走的是「平台原语开放」路线——cloud agent 的能力以可编程方式开放：

- **Automations**（2026-08-03）：**评论触发** cloud agent 自动化——issue/PR 评论满足指定文本即触发（生成文档、调查错误、创建跟进任务）；Agents tab → Automations 面板配置。
- **Agent automation controls**（2026-07-23）：Approvals / Confidence / Rationale 三件套，**REST / GraphQL API** 可用——第三方工具可以编程读取/设置 agent 动作的置信度与理由。
- **Agentic Workflows**：`issue-intents: true` frontmatter 让 workflow 的 safe outputs 携带意图信息（向后兼容）——**工作流本身是版本化的 YAML，AI 行为可声明**。
- **Copilot SDK / CLI / MCP Server**：cloud agent 可经 API、GitHub CLI、GitHub MCP Server 被 Jira / Slack / Teams / Linear / Azure Boards / Raycast 等外部系统调用（docs 侧边栏可见完整集成清单）。
- **Copilot CLI 的 LSP servers**：CLI 可配置 LSP server 增强确定性（与 JetBrains LSP 叙事同向）。
- **意义**：GitHub 把「AI 编程能力」开放成**平台级自动化基础设施**——不只是 IDE 里的补全，而是 issue 编排、CI 触发、外部系统集成都可通过公开协议编程。能力边界由 **API + 协议** 划定，而不是「GitHub 产品内部」。

### 4.5 开放与集成的辩证

| 平台 | 开放的协议面 | 保留的垂直面 | 护城河策略 |
|:--|:--|:--|:--|
| **JetBrains** | LSP（Java/Kotlin 智能）、ACP（外部 agent）、Kotlin LSP（Apache-2.0） | IDEA 桌面体验、调试器深度、IDE 生态 | 智能协议化 + 体验垂直化（许可证复用锁定） |
| **Cursor** | MCP + Skills 插件、Marketplace、Automations、CLI | Agent Router、自研 Composer 模型、编辑器 | 路由/模型供给侧 + 生态连接侧双轮 |
| **GitHub** | automations、REST/GraphQL、SDK、CLI、MCP Server、Agentic Workflows | PR/Issue 数据模型、审批/审计、成本中心 | 把「协作平台」变成「AI 自动化平台」，数据与治理闭环是护城河 |

**辩证结论**：三平台都在「协议开放」与「垂直集成」之间走中间路线——**把能力层开放（协议覆盖更多消费方），把体验/治理层垂直（自家产品保留最优体验与最深控制）**。纯开放（无差异化）与纯封闭（无生态）都是死路，差异在于各自把「开放面」选在哪儿：JetBrains 开放语言智能、Cursor 开放工具连接、GitHub 开放平台原语。

---

## 五、三横切的统一第一性原理

三条横切主线共享同一个底层结构：**AI 编程平台的价值链从「生成」向「交付」迁移**。

| 横切 | 解决的稀缺 | 平台动作的本质 | 统一原理 |
|:--|:--|:--|:--|
| 可审查性 | 审查成本（生成趋零后的唯一稀缺） | 把审查编进交付结构（stacked PR、confidence、rationale） | **结构决定审查成本**：改变交付形态比优化审查工具更有效 |
| 成本治理 | 计量与拦截能力（可变成本需要治理回路） | 度量→归属→配额→优化四段式标配化 | **可计量的成本必须可治理**：计量制必然催生治理制 |
| 协议边界 | 集成权（能力需被任意消费方使用） | 智能/工具/平台能力协议化 | **能力边界 = 协议边界**：谁定义协议，谁定义生态 |

三者的共同对手是「**AI 时代组织的三权回收**」：判断权（可审查性保证人仍能判断）、预算权（成本治理保证钱仍能管住）、集成权（协议开放保证系统仍能组合）。**平台竞争的下半场，不是比谁生成得更好，而是比谁把这三权交还给组织交得更彻底**——这与知识库中「AI 是毛利不是净利」「约束脚本化是最高杠杆」的判断完全一致：平台的职责从「替你做」升级为「让你能审、能控、能接」。

---

## 六、对服务器 / AI 基础设施领域的启示

1. **可审查性 → 硬件研发的 AI 质量门禁**：GitHub 的 Approvals/Confidence/Rationale 三件套可移植到服务器研发的 AI 辅助流程——例如 AI 生成的 BMC/BIOS 代码审查、AI 诊断结论，都可以用「置信度分级 + 理由强制 + 建议而非应用」的机制，把「AI 产出可审查」内建到研发流水线（对应本知识库 code-review 专项与「文档承诺即契约」纪律）。
2. **成本治理 → 算力 FinOps 的模型路由**：Cursor Router 的「Compass 复杂度预测 + 任务分类路由」是**推理成本治理的参考架构**——与 08-07 可观测性文档中 OpenCost × llm-d 的 per-token FinOps 互补：一个是模型选择层的路由优化，一个是集群成本层的计量归属。服务器/超节点场景的 KV Cache 分层、prefill/decode 分离池正是同构的成本治理（见 08-05 推理冗余消除统一框架）。
3. **协议边界 → 开放标准的产业逻辑**：JetBrains LSP 开放智能、GitHub 开放平台原语，与服务器领域 UALink/OCP/ODCC 的开放标准逻辑同构——**能力协议化者得生态**。对设备制造商：定义协议（如超节点标准）比定义产品更能占据价值链位置（呼应「Intel IPU 策略：自我吞噬的标准化悖论」与「接口即权力」）。
4. **结构内建 > 工具修补**：stacked PR 的启示是——**与其让工具更好用，不如改变产出物的结构**。对应到硬件：与其事后修故障，不如把 RAS 特性（错误记录、置信度标注、理由追溯）内建到芯片/固件设计（对应 FTA→设计可追溯性与 PHM 三支柱）。

---

## 七、交叉链接

- [`2026-08-05-five-engineering-claude-code-trae-deep-analysis.md`](../../03_AI/agent-engineering/2026-08-05-five-engineering-claude-code-trae-deep-analysis.md) — 五种工程 × Claude Code/Trae：AGENTS.md/SKILL.md/Hooks 上下文工程（本次是平台侧交付结构）
- [`2026-08-05-harness-os-process-boundary-isomorphism.md`](../../03_AI/agent-engineering/2026-08-05-harness-os-process-boundary-isomorphism.md) — Harness 即适配层：工具收窄 PTC 同源安全（可审查性与权限边界）
- [`2026-08-03-agent-composition-and-coding-agent-comparison.md`](../../03_AI/agent-engineering/2026-08-03-agent-composition-and-coding-agent-comparison.md) — 编程四 Agent 对比（Claude Code/Trae/Qoder/CodeBuddy）
- [`2026-08-05-ai-output-gross-vs-net-entropy.md`](../../03_AI/methodology/2026-08-05-ai-output-gross-vs-net-entropy.md) — AI 产出经济学：毛利 vs 净利（成本治理的治理成本视角）
- [`2026-08-05-llm-inference-redundancy-elimination-deep-analysis.md`](../../03_AI/llm-techniques-principles/2026-08-05-llm-inference-redundancy-elimination-deep-analysis.md) — 推理冗余消除统一框架（token 成本的结构性来源）
- [`2026-08-05-agentic-data-access-paradigm-deep-analysis.md`](../../07_industry-research/04_ai/2026-08-05-agentic-data-access-paradigm-deep-analysis.md) — Agentic 数据访问（写要事务化、读要 token 原生——LSP 减少 token 消耗同向）
- [`2026-08-07-observability-depth-nixt-opencost-otel-kubeflow-cilium.md`](./2026-08-07-observability-depth-nixt-opencost-otel-kubeflow-cilium.md) — 可观测性纵深：OpenCost × llm-d per-token FinOps（集群层成本治理）
- [`2026-08-07-agent-runtime-guardrails-agentic-aiops-800v-hvdc-deep-analysis.md`](./2026-08-07-agent-runtime-guardrails-agentic-aiops-800v-hvdc-deep-analysis.md) — Agent 运行时护栏（Dogwood 确定性执行与 GitHub 可审查机制同构）
- [`2026-07-29-ai-coding-open-source-impact-deep-analysis.md`](../../03_AI/ai-principles/2026-07-29-ai-coding-open-source-impact-deep-analysis.md) — AI 编程工具对开源生态的冲击
- [`2026-08-04-coding-agent-fullchain-inference-deep-analysis.md`](../../03_AI/agent-engineering/2026-08-04-coding-agent-fullchain-inference-deep-analysis.md) — 编程 Agent 全链路推理（KV 容量=第一瓶颈，token 成本的硬件根源）

## 八、诚实标注

1. **「JetBrains 10x 控本」的「10x」出处未确认**：本次抓取 JetBrains 官方源（AI 主页、AI Credits Terms、IntelliJ 2026.2 发布、Goes LSP）中未见「10x」具体表述；文档以可确证事实（AI Credits 计量 + 双轨 + 每用户配额）为准。若「10x」指其他官方材料（如 AI 页面营销语），待补充源后修订。
2. **Cursor Router 数据为厂商自报**：Auto Intelligence -68% 成本、Auto Balance -41% 成本等均为 Cursor 官方 Blog 自报，基于其内部流量与满意度代理信号（「用户继续下一任务=正信号」），未独立复现。
3. **JetBrains LSP 扩展为预览版**：30 天评估期、功能集为「窄集」（导航/引用/补全/重命名），调试深度与完整 IDEA 体验的差异未量化；「agent 工作流减少 token 消耗」的结果标注为「即将公布」。
4. **stacked PR 为公开预览**：merge queue 支持「正在滚动上线」；gh-stack 为社区扩展生态（github/gh-stack），稳定性与 GitLab/Graphite 等既有方案的对比未评估。
5. **成本治理仅覆盖平台侧**：组织实际的总成本（人力审查成本、切换成本、治理成本）未在平台数据中体现；「度量→归属→配额→优化」四段式为本文归纳框架，非平台官方命名。

---

## Changelog

- **2026-08-07** | 初稿：AI 编程平台三横切深度分析（可审查性 × 成本治理 × 协议边界），素材=GitHub Docs ×3 + Changelog ×4、Cursor Blog ×3（Router 技术原文全文）、JetBrains Blog ×2 + AI Credits Terms v1.0 全文
