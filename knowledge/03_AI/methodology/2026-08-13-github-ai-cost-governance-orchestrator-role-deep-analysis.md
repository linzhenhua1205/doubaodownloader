# 🎯 GitHub 2026-08 上旬批次深度分析：AI 成本可解释性四层 + 私有化推理一等公民 + Orchestrator 角色叙事

> **类型**：官方更新深度分析（一手来源核对）
> **日期**：2026-08-13
> **来源批次**：GitHub Changelog 2026-08-03 ~ 08-12 + GitHub Blog 2026-08-11
> **关键词**：AI成本治理 / credit 计量 / per-model token / BYOK 私有化推理 / rulesets / agent 编排 / 角色演进
> **互证文档**：[Token 经济学：计费单位裂变（腾讯新闻）](../06_others/sources/2026-08-12-token-economics-billing-unit-fission-tencent-news.md) · [Token 经济模型（超节点 Token/s·Token/Watt·Token/$）](../../02_rd/02_project/01_superpod/evaluation/2026-07-08-05-token-economics-model.md) · [Ticket 即 Spec 方法论（Atlassian）](2026-08-13-ticket-as-spec-high-throughput-engineer-methodology.md)

---

## 📑 目录

- [1. 批次全景：GitHub 8 月上旬的治理主题](#1-批次全景github-8-月上旬的治理主题)
- [2. 主题一：成本可解释性四层——从组织 ROI 到模型级 Token](#2-主题一成本可解释性四层从组织-roi-到模型级-token)
  - [2.1 四层全景图](#21-四层全景图)
  - [2.2 L1 组织 ROI：Copilot impact dashboard](#22-l1-组织-roicopilot-impact-dashboard)
  - [2.3 L2 桌面 Credit：Copilot App 请求级明细](#23-l2-桌面-creditcopilot-app-请求级明细)
  - [2.4 L3 个人 Per-message：请求级成本可见](#24-l3-个人-per-message请求级成本可见)
  - [2.5 L4 模型级 Token 细分：Usage Report](#25-l4-模型级-token-细分usage-report)
  - [2.6 四层原理：治理粒度 × 归因完备性 × 决策主体](#26-四层原理治理粒度--归因完备性--决策主体)
  - [2.7 与腾讯 Token 经济学互证：卖方裂变 → 平台归因 → 预算语言重写](#27-与腾讯-token-经济学互证卖方裂变--平台归因--预算语言重写)
- [3. 主题二：私有化推理成为一等公民](#3-主题二私有化推理成为一等公民)
  - [3.1 三个落地信号](#31-三个落地信号)
  - [3.2 原理：执行边界与治理边界分离](#32-原理执行边界与治理边界分离)
  - [3.3 与成本可解释性的张力：影子计算缺口](#33-与成本可解释性的张力影子计算缺口)
- [4. 主题三：《From coder to orchestrator》官方角色叙事](#4-主题三from-coder-to-orchestrator官方角色叙事)
  - [4.1 原文要点](#41-原文要点)
  - [4.2 Agentic Flow 架构原理](#42-agentic-flow-架构原理)
  - [4.3 确定性边界：三层控制模型](#43-确定性边界三层控制模型)
  - [4.4 与 Ticket 即 Spec 互锁](#44-与-ticket-即-spec互锁)
- [5. 治理机制演进：branch protection → rulesets](#5-治理机制演进branch-protection--rulesets)
  - [5.1 机制对比](#51-机制对比)
  - [5.2 治理范式跃迁：从布尔属性到策略对象](#52-治理范式跃迁从布尔属性到策略对象)
  - [5.3 与成本治理演进同构：粒度下钻 + 层级上移](#53-与成本治理演进同构粒度下钻--层级上移)
- [6. 第一性原理提炼](#6-第一性原理提炼)
- [7. 应用场景与落地建议](#7-应用场景与落地建议)
- [8. 对比矩阵](#8-对比矩阵)
- [9. 诚实标注](#9-诚实标注)
- [10. 📝 修订记录](#10--修订记录)

---

## 1. 批次全景：GitHub 8 月上旬的治理主题

2026-08-03 ~ 08-12 的 GitHub 官方更新（changelog + blog）围绕一条清晰主线：**当 AI 从"个人效率工具"变成"组织级生产资产"时，治理体系必须同步升级**。本批六个关键条目构成完整证据链：

| 条目 | 日期 | 类型 | 治理维度 |
|:-----|:-----|:-----|:---------|
| Copilot impact dashboard 增加 ROI 段 | 08-07 | Improvement | 成本：组织级 ROI |
| Copilot App：Auto 显示模型 + AI credit + cache 明细 | 08-07 | Release | 成本：桌面请求级 |
| Per-model token breakdown in usage report | 08-11 | Improvement | 成本：模型级 token 细分 |
| MAI-Code-1.1-Flash 上线（-73% 定价、0.25× 乘数） | 08-11 | Release | 成本：模型定价杠杆 |
| Ollama BYOK + Copilot memory（JetBrains） | 08-11 | Release | 主权：私有化推理一等公民 |
| 自动迁移 branch protection → rulesets | 08-11 | Release | 治理：策略对象化 |
| 《From coder to orchestrator》 | 08-11 | Blog | 角色：开发者叙事重构 |

其中**成本治理**与**执行治理**是两条并行主链，交汇于"治理粒度下钻 + 治理层级上移"这一共同范式（详见 §5.3）。

---

## 2. 主题一：成本可解释性四层——从组织 ROI 到模型级 Token

### 2.1 四层全景图

用户信息源所称"成本可解释性四层到顶"，对应 GitHub 本批三个更新 + 既有机制，构成从宏观到微观的完整归因栈：

```text
L1  Org ROI          Copilot impact dashboard (08-07)
    decision maker: CFO / procurement / eng mgmt
    attribution:    dev cohorts (Passive/Phase1 vs Phase2/Phase3)
    metrics:        Cost/dev/month, % Payroll/month, PR/month
        |
        v
L2  Desktop Credit  Copilot App Auto request details (08-07)
    decision maker: individual developer
    attribution:    per completed request
    metrics:        model + AI credits + cache details
        |
        v
L3  Per-message     Copilot for individuals usage report
    decision maker: individual subscriber
    attribution:    per conversation / request
    metrics:        request-level AI credits + premium request multiplier
        |
        v
L4  Per-model Token Usage report per-model breakdown (08-11)
    decision maker: org admin / finance
    attribution:    per model
    metrics:        input / output / cache read / cache write tokens + credits
```

**四层不是并列功能，而是同一条归因链上的四个粒度断面**：组织层回答"钱花得值不值"（ROI），桌面层回答"我这个请求花了多少"（即时反馈），个人层回答"我的订阅在烧什么"（自省），模型层回答"钱被哪些模型吃掉了"（优化抓手）。

### 2.2 L1 组织 ROI：Copilot impact dashboard

原文要点（changelog 08-07）：

- 新增 "Potential return on investment" 段，把 **Copilot 支出 ↔ PR 产出** 直接并排；
- 两张卡片对比两类开发者：**Passive users / Phase 1**（chat + code completion 为主） vs **Phase 2 / Phase 3**（agent-first）；
- 每张卡片三个指标：**Cost/dev/month**（由实际 AI credit 消耗推导）、**% Payroll/month**（占薪酬比例）、**Pull requests/month**（人均 PR 数）；
- **Salary selector**：可调薪酬档位，成本衍生指标即时重算——即"对账你自家的薪酬假设"；
- 明确注明：成本为估算（基于 AI credit consumption），salary selector 是建模输入而非真实薪酬数据。

**原理分析——ROI 锚从"座位价"切换到"用量归因"**：

传统 seat-based 计费下，组织能算的只有"席位单价 × 席位数量"，与产出无关。本更新的关键跃迁是 **Cost/dev/month 由实际 AI credit 消耗推导**——即每个开发者的成本 = 其真实调用量 × 各模型单价。这使"投入-产出"首次在同一主体（开发者）上闭合：

```text
ROI(dev g)   = PR_output(g) / cost(g)
cost(g)      = SUM_over_requests AI_credits(g) x price(model, cache, req_class)
```

由此产生三个管理杠杆：
1. **分层归因**：Passive vs Agent-first 两组的 Cost/dev 与 PR/dev 对比，量化"深层采用是否值得"——回答"继续投还是收敛"；
2. **薪酬锚定**：% Payroll 把 AI 支出放进薪酬语境，用"人力成本占比"统一比较轴——这正是腾讯文"预算语言重写"的组织侧落地（§2.7）；
3. **定向 enablement**：成本-产出差异暴露"还有 headroom 的阶段"，enablement 预算投向边际收益最大的群体。

### 2.3 L2 桌面 Credit：Copilot App 请求级明细

原文要点（weekly releases 08-03 / 发布 08-07）：

> "Auto now shows which model handled each completed request, plus AI credit and cache details when they're available."

**原理分析——把成本感知放进工作流内部**：

传统成本报告是"事后、离线、汇总"的（月度账单），开发者对单次操作的成本无感知。桌面层把**模型名 + AI credits + cache 明细**直接贴到每次完成的请求上，实现：
- **即时反馈闭环**：开发者立刻知道"这个 agent 任务烧了多少 credit、命中多少缓存"，行为可被成本信号调节（如改用更省的模式）；
- **缓存可见性**：cache details 让开发者/团队意识到 prompt 缓存复用率——这是 AI 成本中杠杆最大的单一维度（见 §2.5 token 四分类）；
- **模型透明**：Auto 模式自动选模型时，用户终于知道"实际跑的是哪个模型"——这是多模型路由时代的信任前提。

### 2.4 L3 个人 Per-message：请求级成本可见

支撑证据（两条 changelog 交叉确认）：

- per-model token breakdown 明确 "**available to anyone on Copilot for individuals**"——个人订阅者同样可下载 AI usage report；
- MAI-Code-1.1-Flash："**For annual GitHub Copilot subscribers, the model is charged at a 0.25× premium request multiplier**"——即 Copilot 对个体用户按请求类别（premium request）施加模型乘数，模型选择直接决定单条消息的 credit 消耗。

**原理分析——"请求"成为个人计费的最小结算对象**：

个人层把成本单位从"月度订阅费"（不可拆）细化到 **per-message / per-request**。premium request multiplier 本质是**模型级价格向量**：

```text
cost(message) = base_credit x multiplier(model) x (1 + cache/tool adjust)
```

0.25× 意味着同一请求选 MAI-Code-1.1-Flash 比选旗舰模型便宜 75%——模型选择器从"质量偏好"变成了"成本决策"。这与腾讯文"Model router 在悄悄决定整张账单的结构"完全互证：**路由即预算**。

### 2.5 L4 模型级 Token 细分：Usage Report

原文要点（changelog 08-11）：

- usage report 新增 **per-model breakdown**：每个模型展示 **input / output / cache read / cache write** 四类 token，连同其消耗的 AI credits；
- 此前报告只有 credits 总额、没有 token 明细，"难以解释一笔费用或找到降低它的方法"；
- 现在可以精确追踪"input/output/缓存 token 如何加总成每个模型的成本"，并可分享给 stakeholders；
- 适用范围：Copilot Business / Enterprise 的管理员 + Copilot for individuals 所有用户。

**原理分析——token 四分类为何是成本治理的最小完备集**：

这四类 token 不是随意切分，而是覆盖了 LLM 推理成本的全部结构性来源：

| Token 类别 | 成本性质 | 优化杠杆 |
|:-----------|:---------|:---------|
| input tokens | 每请求必付（prefill） | 精简 prompt、系统提示压缩、检索裁剪 |
| output tokens | 生成量决定 | 控制生成长度、减少废话 token |
| cache read | 命中缓存，成本最低 | **提高前缀复用率**（同一系统提示/工具定义/上下文前缀） |
| cache write | 首次写入缓存，成本介于两者 | 缓存策略、TTL、会话长度管理 |

对应腾讯文引用的 Anthropic "三档缓存乘数 + session runtime"——**平台终于把价格页上裂变的维度，标准化成可对账、可下载、可分享的结构化数据**。这正是 §2.7 互证闭环的落点。

### 2.6 四层原理：治理粒度 × 归因完备性 × 决策主体

从第一性原理看，四层成本可解释性不是功能罗列，而是**成本治理成熟度的四个阶段**，沿两个正交轴演进：

```text
Axis A: attribution granularity down  org cohort -> desktop req -> message -> model token
Axis B: decision subjects expand       CFO/procurement -> dev -> individual -> admin/finance
```

核心定理：**支出的可优化性 ∝ 归因粒度 × 归因完备性**。

- 粒度决定"能定位到谁/什么"：总额只能看到"贵"，per-model 才能看到"哪个模型贵"；
- 完备性决定"能不能闭环优化"：只有 input/output/cache read/cache write 四类齐备，才能定位"是缓存命中率低，还是输出过长"——缺一类，优化就缺一个把手；
- 归因的**可干预性**决定治理是否成立：能归因但不能干预（如模型选择被锁死、缓存策略不可控），成本解释只是报表不是治理。

据此四层各自对应一个"可干预单元"：

| 层 | 可干预单元 | 干预动作 |
|:---|:-----------|:---------|
| L1 组织 ROI | 开发者群体结构 | enablement 预算、采用策略、模型策略 |
| L2 桌面 credit | 单次请求行为 | 换模型、改模式、缓存友好 prompt |
| L3 个人 per-message | 模型选择 | 模型 picker、premium multiplier 权衡 |
| L4 模型级 token | 模型+缓存策略 | 模型准入策略、缓存配置、token 预算 |

### 2.7 与腾讯 Token 经济学互证：卖方裂变 → 平台归因 → 预算语言重写

腾讯文（2026-08-12 归档）核心论点：**计费单位已从单一 Token 裂变为 search / runtime / cache / seat / outcome 多单位并存**，企业预算语言被迫重写。GitHub 本批更新恰是同一趋势的**平台侧治理响应**，形成完整闭环：

```text
Seller side (Tencent article)          Platform side (GitHub this batch)
price-page fission (multi items) -->   usage report normalized attribution (4 token classes)
                                       ^
budget language rewrite (multi-dim) <-- ROI panel (% Payroll) + salary selector
                                       ^
cost down / value up             <--   model pricing down (MAI-Code-1.1-Flash -73%)
```

三点互证细节：

1. **"token 不再是唯一主角"的落地**：腾讯文说对账单"不再是一列 Token 的累加，而是一组互相叠加的价格对象"。GitHub 的四类 token 细分 + credits 换算，正是把"叠加的价格对象"重新组织成**可解释的归因树**——买方终于能回答"这钱到底花在哪"；
2. **"预算口径一维→多维"的治理工具化**：腾讯文呼吁买方重写预算框架；GitHub 的 ROI 面板（Cost/dev 与 % Payroll 并排、薪酬档位建模）提供了现成的多维核算工具——**平台先于买方准备好了治理基础设施**；
3. **"成本在下沉、价值在上移"的供给侧佐证**：MAI-Code-1.1-Flash 比前代 **-73% list price、0.25× multiplier**，是"工作层模型持续商品化"的最新实证——与腾讯文"前沿能力集中 + 工作层商品化"的判断方向一致。

**反向观察（诚实标注）**：腾讯文指出"卖方价格页变化 ≠ 卖方收入结构变化，需等数据说话"——GitHub 的 token 细分同样只是**成本归因**而非**收入披露**；Copilot 的成本是否真由 token 结构驱动，仍需公开财务数据验证。此外四层覆盖的是 **Copilot 生态内**的用量，BYOK 本地推理（§3）的 token 消耗不进 usage report——**成本可解释性存在"影子计算"盲区**（§3.3）。

---

## 3. 主题二：私有化推理成为一等公民

### 3.1 三个落地信号

本批 changelog 中"私有化推理"并非单点发布，而是三个独立信号同时出现：

| 信号 | 载体 | 内容 |
|:-----|:-----|:-----|
| 本地模型进官方支持 | Copilot for JetBrains (08-11) | **Ollama 成为 BYOK provider**，支持 provider 配置与模型选择贯穿 JetBrains 全流程 |
| 端侧推理默认化 | VS Code 1.132 (08-07) | 听写改用 **multilingual on-device model**，音频不出设备 |
| 上下文主权 | Copilot memory (08-11) | 跨会话记忆可保留/召回项目信息，由 Copilot Memory 开关管理 |

### 3.2 原理：执行边界与治理边界分离

私有化推理"成为一等公民"的本质，是平台承认并制度化了一条边界切分原则：

```text
Execution boundary (localizable)     Governance boundary (must be central)
----------------------               ----------------------------
model inference execution <----->    policy / compliance / audit / metering
data residency / privacy  <----->    managed settings distribution
latency-sensitive ops     <----->    model allowlist
offline availability      <----->    OpenTelemetry observability
```

- **BYOK 是"执行本地化、治理集中化"的标准模式**：Ollama 把推理跑在开发者机器/内网（数据主权、零额外延迟、离线可用），但 provider 准入、模型选择、企业策略仍由云端 managed settings 控制（同批 changelog 明确 enterprise managed settings 覆盖 MCP 访问、权限绕过行为、OpenTelemetry 设置）；
- **on-device 模型是隐私边界的极限压缩**：音频数据不出设备 = 把"数据出境"从架构上消灭，而非靠合规条款兜底；
- **Copilot memory 是上下文主权**：会话记忆从"云端黑盒"变为"用户可管理资产"（开关 + 设置门户），与 Ollama 同属"把 AI 的驻留物还给用户"的叙事。

### 3.3 与成本可解释性的张力：影子计算缺口

私有化推理与 §2 的成本可解释性存在结构性张力，这是本批更新**未解决**的问题：

- Ollama 本地推理产生的 token **不计入云端 credit、不进 usage report、不参与 ROI 面板**；
- 组织若大规模 BYOK，其真实 AI 支出 = 云端 credit + 本地算力（电费 + 硬件摊销 + 维护），而 ROI 面板只看得见前者；
- 后果：**影子计算**（shadow compute）——与影子 IT 同构的治理缺口。四层成本栈若只覆盖云端，组织会系统性低估本地推理的真实 TCO。

**推断与建议**：成本可解释性四层若要"到顶"，下一步需要把 BYOK/本地推理纳入统一计量（本地 token 也按等价 credit 折算，或至少单列"本地推理支出"科目），否则"私有化推理一等公民"与"成本治理到 token 粒度"会各说各话。此为分析推断，非官方承诺。

---

## 4. 主题三：《From coder to orchestrator》官方角色叙事

### 4.1 原文要点

GitHub Blog 2026-08-11（Natalie Guevara，GitHub Universe 2026 预热）：

- 开篇对比："**one-prompt demo**"（一次性输出） vs "**wired workflow**"（可靠、安全的可重复交付）——后者才是开发者的工作；
- "You still write code, sure, but you also design the system: how code is proposed, validated, reviewed, and shipped"；
- GitHub Copilot 定位为"**control plane for building software that gets wired up**"；
- Agentic flow：仓库事件/触发器（label、scheduled workflow）→ Actions workflow 调用 agent 执行已划定范围的任务 → 产出进入 PR → **确定性检查接管**（lint、tests、security scanning、build verification）→ CODEOWNERS / required reviews / branch protections 治理合入；
- 核心论断："**Agents are flexible, but within a deterministic boundary that is rule-based and predictable. The deterministic side is what makes teams trust the system.**"；
- 开发者新职责：定义触发器、划定 agent 权限、设计交接（handoffs）、**决定人类判断必须留在环内的位置**；
- MCP 等扩展是"同一成熟度路径上的实现选项"，而非独立哲学。

### 4.2 Agentic Flow 架构原理

把原文的叙事翻译成系统架构，agentic flow 是一条**明确分阶段的流水线**：

```text
Event layer   issue label / schedule / comment (08-03: comment-triggered automations)
   |
   v
Orchestration GitHub Actions workflow -> invoke agent (Copilot cloud agent / CLI)
   |          (scope: defined by ticket/task)
   v
Execution     agent produces code/changes (MCP extends tools & external context)
   |
   v
Check layer   PR deterministic checks: lint / tests / security / build  <-- rules take over
   |
   v
Governance    CODEOWNERS / required reviews / branch protections/rulesets
   |
   v
Merge         (human judgment kept for high-risk changes)
```

关键设计：**agent 的自由度只存在于"事件→PR"这一段**，一旦进入 PR，控制权移交给规则系统。这使：
- **错误可拦截**：agent 输出再离谱，也会被 lint/test/security 的确定性信号拦住；
- **责任可追溯**：每次合入都有 PR + checks + reviewer 记录，审计链完整；
- **信任可构建**：团队信任的不是"agent 不会犯错"，而是"错误无法穿过检查层"——信任对象从模型质量迁移到规则完备性。

### 4.3 确定性边界：三层控制模型

将原文思想抽象为三层控制模型（与 [AI 工程熵与约束](../03_AI/methodology/2026-07-10-ai-engineering-entropy-and-constraint.md) 的方法论同源）：

| 层 | 执行者 | 特性 | 失败模式 |
|:---|:-------|:-----|:---------|
| 意图层 | 人类（开发者/管理者） | 定义 scope、权限、判断点 | 边界不清 → agent 越权 |
| 弹性层 | Agent | 处理模糊、上下文密集任务 | 幻觉、漂移、过度自信 |
| 确定性层 | CI / rules / review | 规则化、可预测、可重复 | 规则缺漏 → 绕过 |

**第一性原理：信任 = 可预测性**。系统被信任的程度取决于其行为可预测的程度；agent 天然不可完全预测，因此必须在弹性层与合入点之间插入确定性层作为**信任缓冲**。这正是 §5 rulesets 迁移的动机之一：确定性层本身也需要更强的表达力。

### 4.4 与 Ticket 即 Spec 互锁

与同日归档的 [Atlassian ticket-as-spec](../03_AI/methodology/2026-08-13-ticket-as-spec-high-throughput-engineer-methodology.md) 形成跨厂商互锁：

- GitHub 说 agent 需要"task that you **scoped**"（你划定范围的任务）——范围从哪来？从 ticket/spec 来；
- Atlassian 说"ticket = agent 可执行的 spec"（83% agent-ready 产出 5×）——正是为 GitHub 的 scoped task 提供输入；
- 两者共同指向同一结论：**agent 经济中稀缺输入是规格，不是执行**。执行供给已被 agent 推向近乎无穷，瓶颈上移到"定义要写什么 + 在何处保留人类判断"；
- 差异在于：Atlassian 聚焦**输入侧**（ticket 质量决定执行上限），GitHub 聚焦**控制侧**（确定性边界决定交付可信度）——合起来才是完整的编排闭环。

---

## 5. 治理机制演进：branch protection → rulesets

### 5.1 机制对比

changelog 08-11：仓库设置中可一键 **Convert to ruleset**，把经典 branch protection（required reviews / status checks / push restrictions）映射为等价 ruleset 规则。

| 维度 | branch protection（经典） | repository rulesets（新） |
|:-----|:--------------------------|:--------------------------|
| 作用域 | 单仓库、单分支 | 多分支 **pattern matching**（正则/通配） |
| 组合能力 | 单层规则 | **多层 rulesets 叠加**，细粒度策略控制 |
| 管理层级 | 仓库级 | 组织 / 企业级统一下发 |
| 绕过权限 | 粗粒度（admin 全放行） | **细粒度 bypass：user / team / app 分别授权** |
| 迁移成本 | — | 一键 Convert（自动映射既有配置） |

### 5.2 治理范式跃迁：从布尔属性到策略对象

branch protection 是"**仓库的一个布尔属性**"（开/关 + 少量开关项），rulesets 是"**独立于仓库的策略对象**"：

```text
classic: repo.branch_protection = { required_reviews: true, ... }   # attribute
new:     ruleset[] = [ {match: "main", require: reviews, bypass: {app: CI}}, ... ]
         # object: named, composable, definable & distributable at org/enterprise
```

跃迁的治理学意义：
1. **治理对象可复用**：同一套策略在 org 内所有仓库生效，而不是逐仓库重复配置（消除漂移）；
2. **治理粒度分离**：规则（what）与豁免（who）分离——bypass 授权到 user/team/app 级，实现"CI bot 可绕过 review、人必须 review"这类精细语义；
3. **治理层级上移**：策略定义从仓库（执行层）上移到组织/企业（治理层），执行与治理解耦——与 §3.2 的"执行边界与治理边界分离"是同一原理的不同实例。

### 5.3 与成本治理演进同构：粒度下钻 + 层级上移

把两条主线并排，发现惊人同构：

| 维度 | 成本治理（§2） | 执行治理（§5） |
|:-----|:---------------|:---------------|
| 旧形态 | seat 总额（不可归因） | branch protection（per-repo 布尔） |
| 新形态 | org ROI → token 四分类 | org 级 rulesets + 细粒度 bypass |
| 粒度方向 | **下钻**：org → 请求 → message → token | **下钻**：repo → 分支 pattern → user/team/app |
| 层级方向 | **上移**：个人决策 → 组织策略 | **上移**：仓库配置 → org/enterprise 策略对象 |
| 共同原理 | 可归因 + 可干预 = 可治理 | 可匹配 + 可豁免 = 可治理 |

**结论：2026 年平台治理的统一范式 = 粒度下钻（到最小可干预单元）× 层级上移（到策略层）**。成本治理把"钱"归因到 token，执行治理把"规则"匹配到分支与身份——两者共享同一个治理几何。

---

## 6. 第一性原理提炼

1. **归因完备性定理**：支出的可优化性 = 归因粒度 × 归因完备性 × 可干预性。粒度决定定位能力，完备性决定闭环能力，可干预性决定治理是否成立——缺一不可（§2.6）。

2. **执行边界与治理边界分离原理**：AI 系统的执行（推理/存储/延迟敏感操作）可本地化以换取主权与性能，治理（策略/审计/计量）必须集中以换取一致性与可解释性。BYOK、on-device 模型、rulesets 层级上移都是该原理的实例（§3.2、§5.2）。

3. **信任 = 可预测性**：agent 弹性必须被确定性层约束，人类判断保留在规则无法覆盖的高风险点；信任对象从"模型不犯错"迁移到"错误无法穿过检查层"（§4.3）。

4. **计量单位即治理语言**：卖方裂变计价（腾讯文）、平台标准化归因（token 四分类）、买方预算重写（ROI 面板）是同一件事的三端——计量单位定义了治理能说什么、不能说什么（§2.7）。

5. **稀缺输入决定瓶颈**：agent 供给执行近乎无穷后，规格（ticket/spec）与编排（triggers/权限/判断点）成为稀缺输入——价值从"写代码"上移到"设计交付系统"（§4.4）。

---

## 7. 应用场景与落地建议

| 场景 | 适配机制 | 落地动作 |
|:-----|:---------|:---------|
| 组织 AI 支出审计 | L1 ROI 面板 + L4 token 细分 | 按薪酬档位建模 ROI；用 per-model 数据定位"贵在哪个模型/哪类 token" |
| 个体成本自省 | L2 桌面 credit + L3 per-message | 开启请求级明细；对高频任务用 0.25× 级模型（MAI-Code-1.1-Flash 类） |
| 缓存优化 | L4 cache read/write 细分 | 提高前缀复用率（统一系统提示、工具定义），缓存命中率成为 KPI |
| 数据主权敏感团队 | Ollama BYOK + on-device | 本地推理 + 云端策略；评估影子计算缺口，单列本地 TCO |
| agent 规模化交付 | Orchestrator 流水线 | 事件触发 → scoped task → PR → 确定性检查 → rulesets 治理合入 |
| 多仓库策略统一 | rulesets 迁移 | 一键 Convert 存量 branch protection；组织级下发 + 细粒度 bypass |

**知识库迁移**：成本治理的"归因→优化→治理"闭环可直接迁移到知识库建设——(a) 归因：每次归档记录来源/耗时（粒度=文档）；(b) 优化：按来源类型分析投入产出（等价于 per-model 分析）；(c) 治理：制定归档策略对象（等价于 rulesets），而非逐文件手工规则。这与 [Ticket 即 Spec 分析](2026-08-13-ticket-as-spec-high-throughput-engineer-methodology.md) §8.2 的"会话即归档"建议衔接。

---

## 8. 对比矩阵

| 维度 | GitHub 本批 | Atlassian 本批 | 腾讯 Token 经济 |
|:-----|:------------|:---------------|:----------------|
| 视角 | 平台供给侧治理 | 组织内部方法论 | 行业定价结构 |
| 核心问题 | 钱花哪了 / 谁有权合入 | ticket 如何喂给 agent | 账单怎么构成的 |
| 治理单位 | token / ruleset | ticket / spec | 计费单位裂变 |
| 共同主题 | 粒度下钻 + 层级上移 | 规格稀缺 | 计量语言重写 |

关联文档：
- [Ticket 即 Spec：高吞吐工程师方法论](2026-08-13-ticket-as-spec-high-throughput-engineer-methodology.md)（同日批次，输入侧）
- [Token 经济学：计费单位裂变（腾讯新闻）](../06_others/sources/2026-08-12-token-economics-billing-unit-fission-tencent-news.md)（卖方定价侧）
- [Token 经济模型：Token/s + Token/Watt + Token/$](../../02_rd/02_project/01_superpod/evaluation/2026-07-08-05-token-economics-model.md)（基础设施侧）
- [AI 工程熵与约束](../03_AI/methodology/2026-07-10-ai-engineering-entropy-and-constraint.md)（确定性边界方法论）

---

## 9. 诚实标注

- **一手来源**：所有数字与功能均来自 GitHub Changelog / Blog 原文核对（见 §1 表格，含 URL 可溯源）；
- **分析推断**：§2.6 治理成熟度模型、§3.3 影子计算缺口、§5.3 同构结论、§6 第一性原理为本文分析，非官方表述；
- **数据边界**：ROI 面板成本为估算（基于 AI credit consumption），salary selector 为建模输入；-73% 定价与 0.25× multiplier 为官方数字；per-model token breakdown 仅覆盖 Copilot 生态内用量；
- **未验证项**：Copilot 真实收入结构是否由 token 驱动（腾讯文同样指出"需等数据说话"）；BYOK 本地推理是否纳入未来计量（官方未承诺）。

---

## 10. 📝 修订记录

| 日期 | 变更 |
|:-----|:-----|
| 2026-08-13 | 创建：GitHub 2026-08 上旬批次四主题深度分析（成本可解释性四层 / 私有化推理 / Orchestrator 角色 / rulesets 迁移），含与腾讯 Token 经济互证闭环 |
