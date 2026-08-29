# 🔐 Linear Jul 30 批次四连发：agent 产出信任链补全——签名提交 × Copilot for Linear × Guided Reviews GA × mobile 管理面

> **统一主线**: 2026-07-30 Linear Changelog 四连发共同宣告 **agent 产出从「可审查」走向「可审计」**——①**签名提交**（coding sessions 支持 SSH/GPG 签名 + **workspace 管理员可强制**：不上传签名 key 不能用 coding sessions——审查管"改得对不对"，签名管"是谁/什么机制改的"）②**GitHub Copilot for Linear**（从 Linear 直接把 issue 交给 Copilot cloud agent：draft PR + issue 回写——**编排层跨平台化**）③**Guided Reviews GA**（大型 PR 引导式审查转正：更大上下文窗口 + 更低延迟，Business/Enterprise 免费）④**mobile coding sessions**（移动端 review/行级评论/agent 迭代 + delegated issues 状态区——**移动端成 agent 管理面**）。四者构成「产出→审查→审计→监督」的完整信任链闭环。
>
> **关键词**: Linear · signed commits · 签名提交 · 可审计 · Copilot for Linear · 跨平台编排 · Guided Reviews · 引导式审查 · mobile coding sessions · fail closed · 信任链
>
> **数据源**: ✅ Linear Changelog 一手（2026-07-30 整批，官网直抓）+ ✅ GitHub Changelog 一手（[Copilot cloud agent for Linear GA](https://github.blog/changelog/2026-07-23-copilot-cloud-agent-for-linear-is-now-generally-available)，07-23）：
> - [Signed commits for coding sessions](https://linear.app/changelog)（07-30）— 签名提交 + admin 强制
> - [GitHub Copilot for Linear](https://linear.app/changelog)（07-30）— 跨平台 agent 委派
> - [Guided Reviews GA](https://linear.app/changelog)（07-30）— 引导式审查转正
> - [Coding sessions on mobile](https://linear.app/changelog)（07-30）— 移动端管理面
> - 佐证：Support for GitHub teams in reviews（07-30，同批）· Copilot cloud agent for Linear GA（GitHub，07-23）
>
> **素材分级**: ✅ 一手 Changelog 正文 · 🔵 既有知识库锚点（08-01/07-31 Linear 信号登记 / 07-28 Linear Text Attribution 治理三连 / 08-10 GitHub Copilot 治理+ROI 套件 / 08-10 secret scanning / MEMORY 三权回收·编排与工作锚点解耦·fail closed 治理语义）
>
> **日期**: 2026-08-10 | **领域**: 项目管理工具 / Agent 治理 / AI 编程平台

---

## 📑 目录

- [〇、结论概要](#〇结论概要)
- [一、四事件总览](#一四事件总览)
- [二、功能① signed commits：信任链补齐——从「可审查」到「可审计」](#二功能①-signed-commits信任链补齐从可审查到可审计)
  - [2.1 机制：SSH/GPG 签名 + admin 强制准入](#21-机制sshgpg-签名--admin-强制准入)
  - [2.2 语义区分：审查管「改得对不对」，签名管「是谁/什么机制改的」](#22-语义区分审查管改得对不对签名管是谁什么机制改的)
  - [2.3 治理语义：admin 强制 = 准入条件而非建议（fail closed）](#23-治理语义admin-强制--准入条件而非建议fail-closed)
- [三、功能② GitHub Copilot for Linear：编排层跨平台化](#三功能②-github-copilot-for-linear编排层跨平台化)
  - [3.1 机制：Linear 发起 → Copilot cloud agent 执行 → draft PR + issue 回写](#31-机制linear-发起--copilot-cloud-agent-执行--draft-pr--issue-回写)
  - [3.2 与 OpenAI Symphony × Jira 的对照：两种「工作锚点」](#32-与-openai-symphony--jira-的对照两种工作锚点)
- [四、功能③ Guided Reviews GA：审查规模化](#四功能③-guided-reviews-ga审查规模化)
- [五、功能④ mobile coding sessions：移动端成 agent 管理面](#五功能④-mobile-coding-sessions移动端成-agent-管理面)
- [六、统一框架：agent 产出信任链三级演进](#六统一框架agent-产出信任链三级演进)
- [七、与 GitHub 侧治理套件的对照（08-04~07）](#七与-github-侧治理套件的对照08-0407)
- [八、与本地知识库的闭环](#八与本地知识库的闭环)
- [九、批判性审视](#九批判性审视)
- [十、可证伪预测（P1-P4）](#十可证伪预测p1-p4)
- [十一、对本系统的启示](#十一对本系统的启示)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 〇、结论概要

**一句话：Linear 在 07-30 一天内把 agent 产出的信任链补到「可审计」——签名提交让「谁/什么机制改的」有了密码学证据，admin 强制让审计从建议变成准入；Copilot for Linear 把编排层打通到 GitHub 生态；Guided Reviews GA + mobile 分别解决「审查规模化」和「监督可达性」。这是与 GitHub 08-04~07「三权回收」套件同一趋势的 Linear 侧表达。**

1. **签名提交（signed commits）**：coding sessions 支持 SSH/GPG 签名，**workspace admins 可要求用户先上传签名 key 才能使用 coding sessions**。**审查（review）回答「改得对不对」，签名（signature）回答「是谁/什么机制改的」——前者是质量门，后者是问责链；两者缺一，agent 产出的责任归属就不完整。** admin 强制=把审计从「可选实践」变成「系统准入条件」，与 GitHub 08-06 MCP allowlists「policies fail closed」同构——**配置无法满足就拒绝服务，而非降级提醒**。
2. **GitHub Copilot for Linear**：用户可在 Linear 内把 issue 直接委派给 Copilot cloud agent——agent 用自己的开发环境工作、开 draft PR、回写 issue 进展；可选手动配置模型/agent 设置、base/working 分支，通过 Linear 评论持续引导。**编排层从「工具内闭环」走向「跨平台委托」——Linear 是工作锚点（context/意图/状态），GitHub 是执行面（代码/PR），分工明确。**
3. **Guided Reviews GA**：引导式审查把大 PR 切成带解释的聚焦 sections，GA 后支持**更大的 PR、更大的上下文窗口、更好的延迟**，Business/Enterprise 免费。**审查规模化 = 对「agent 产出量 > 人审能力」这一结构性瓶颈的产品级响应。**
4. **mobile coding sessions**：移动端可 review 代码、行级评论、与 Linear Agent 迭代；My Issues → Assigned 新增 delegated issues 区（每个 coding session 的状态可见）。**管理面移动化 = 监督从「坐在工位」扩展到「任何时间地点」——agent 工作流全天候化的治理侧配套。**

**补充发现**：同批还有「Support for GitHub teams in reviews」（评审请求可指派给 GitHub teams，Reviews inbox 专属区段）——审查负载从「个人 inbox」走向「团队 inbox」，与 Guided Reviews 共同构成审查规模化。

---

## 一、四事件总览

| # | 条目 | 类型 | 面向对象 | 一句话 | 信任链环节 |
|:-:|:-----|:-----|:---------|:-------|:---------:|
| 1 | Signed commits for coding sessions | Release | 团队/组织 | 签名提交 + **admin 可强制** | **审计** |
| 2 | GitHub Copilot for Linear | Release | 开发者/团队 | issue 直接委派给 Copilot cloud agent | **编排** |
| 3 | Guided Reviews GA | Release | 团队/组织 | 大 PR 引导式审查转正（更大上下文+更低延迟） | **审查** |
| 4 | Coding sessions on mobile | Release | 个体 | 移动端 review/评论/迭代 + delegated issues 状态 | **监督** |
| + | Support for GitHub teams in reviews | Improvement | 团队 | 评审指派给 GitHub teams（inbox 专属区段） | 审查 |

> 📌 前 3 项是「产出治理」正向建设，第 4 项是「监督可达性」扩展——**建设的是审计与编排能力，扩展的是监督的场景覆盖**，同一叙事（agent 产出可信化）的两面。

---

## 二、功能① signed commits：信任链补齐——从「可审查」到「可审计」

### 2.1 机制：SSH/GPG 签名 + admin 强制准入

| 设计 | 内容 |
|:-----|:-----|
| **签名方式** | Settings 中配置 SSH 或 GPG key 后，coding sessions 的提交自动签名 |
| **admin 强制** | **Workspace admins can also require users to upload a signing key before using coding sessions**——管理员可要求用户先上传签名 key 才能使用 coding sessions |
| **语义** | 签名 = 密码学绑定「这次提交由该 key 对应的身份/机制生成」 |

[来源: Linear Changelog, Jul 30, 2026 原文]

**关键点不是「支持签名」，而是「admin 可强制」**——签名作为可选功能早已是 Git 生态标配（GitHub 原生支持 commit signing），Linear 的增量在治理层：把「签名」从个人习惯升级为**团队准入条件**。

### 2.2 语义区分：审查管「改得对不对」，签名管「是谁/什么机制改的」

```text
Two independent questions before agent output enters the codebase:

  Q1: Is the change correct?   -> Review   -> quality gate -> judged by humans
  Q2: Who/what mechanism made it? -> Audit -> accountability -> proven by crypto

  Review does not answer attribution; signature does not answer quality.
  They are orthogonal:
  - No signature: review passes but no accountability ("which agent wrote this?")
  - No review: signature is trustworthy but correctness is not ("agent wrote it, wrongly")
```

**为什么「机制」而非「人」是审计对象？** Coding sessions 的产出可能来自：用户手动触发、Linear Agent 自动修复（triage 自动化约 30% 的 bug 报告）、Loops 定时/事件触发。签名的 key 绑定到 session 的授权身份，从而**把「代码改动 → 触发机制」的因果链固化**——这正是 07-23 Text Attribution（作者类型 human/agent/loop）在代码层的延伸：文档层已有「谁写的」标注，代码层现在有了「谁的 key 签的」。

### 2.3 治理语义：admin 强制 = 准入条件而非建议（fail closed）

**用户洞察（本轮核心增量）**：admin 强制=准入条件而非建议，与 08-08 MCP allowlists「policies fail closed」同构。

| 维度 | GitHub MCP allowlists（08-06） | Linear signed commits 强制（07-30） |
|:-----|:-------------------------------|:-----------------------------------|
| 管控对象 | agent 能连接的外部 MCP 服务器 | agent 产出进入仓库的提交 |
| 策略形态 | `allowedMcpServers` 白名单 | 签名 key 上传要求 |
| 失败语义 | **fail closed**：配置无法验证则阻止而非放行 | **fail closed**：未上传 key 则无法使用 coding sessions |
| 共同点 | 管控不是「提醒/建议」，而是**服务准入前提**——不满足条件直接不可用 |

[来源: Linear Changelog Jul 30 + GitHub Changelog 08-06 MCP allowlists; 作者对照推理]

**治理语义的跃迁**：传统权限系统是「允许名单之外禁止」（fail closed 已有），但**针对 agent 产出的审计要求是新的**——GitHub 管「agent 能连什么」（连接面），Linear 管「agent 产出以什么身份落地」（产出面）。两者共同宣告：**AI 时代的治理不是「事后抽查」，而是「事前准入」**——与 MEMORY 中「约束脚本化=最高杠杆」同一原则的产品化。

---

## 三、功能② GitHub Copilot for Linear：编排层跨平台化

### 3.1 机制：Linear 发起 → Copilot cloud agent 执行 → draft PR + issue 回写

| 设计 | 内容 |
|:-----|:-----|
| **发起** | 用户在 Linear 内将 issue 直接 assign 给 Copilot's cloud agent |
| **上下文** | Copilot 使用 issue 上下文（描述/评论/关联信息）在自己的开发环境中工作 |
| **产出** | 打开 draft pull requests，随进展更新 issue |
| **控制** | 可选择模型和 agent 设置、设置 base 与 working branches、通过 Linear 评论持续引导（steer ongoing work） |
| **获取** | 安装 GitHub Copilot for Linear（GitHub 侧 07-23 已 GA） |

[来源: Linear Changelog Jul 30 + GitHub Changelog 07-23]

**编排层跨平台化的含义**：这不是「Linear 内置 agent」的竞争叙事，而是**互补委托**——Linear 定位为**工作锚点**（意图/上下文/状态/评论引导），GitHub Copilot 定位为**执行面**（代码环境/draft PR）。用户的评审、引导、状态跟踪全部留在 Linear（团队已有工作流），执行发生在 GitHub（agent 的开发环境）。**「工作对 agent 可读、人对 agent 可问责」的分工界面进一步清晰化。**

### 3.2 与 OpenAI Symphony × Jira 的对照：两种「工作锚点」

| 维度 | OpenAI Symphony × Jira（08-06） | GitHub Copilot for Linear（07-23/30） |
|:-----|:--------------------------------|:---------------------------------------|
| 编排器 | OpenAI Symphony（协调 Codex 执行循环） | GitHub Copilot cloud agent（自身即执行者） |
| 工作锚点 | Jira（System of Record） | Linear（issue 上下文） |
| 执行面 | Codex（隔离 worktrees） | Copilot cloud agent（自身开发环境） |
| 关联方式 | Symphony watch Jira → 找合格工作 → 协调执行 | 用户在 Linear 直接 assign → agent 执行 |
| 回写 | 审查留在 Jira（plans/updates/blockers） | draft PR + issue 进展更新 |

**共同信号（08-06/08 捕获，本期确认）**：**编排层正在从「平台内闭环」走向「跨平台委托」**——Atlassian 说 Jira 是 System of Work 而非 System of Sessions（08-08 已归档），Linear 现在用 Copilot for Linear 表达同一立场：**工作记录留在 PM 工具，执行委派给外部 agent**。两个头部 PM 工具在同一个月选择了同一架构方向，这是「编排与工作锚点解耦」成为行业共识的强证据。

---

## 四、功能③ Guided Reviews GA：审查规模化

| 设计 | 内容 |
|:-----|:-----|
| **核心机制** | 把 diff 切成聚焦 sections，每节带 explainers（改了什么 + 为什么）——先看核心改动，不在一堆代码里找入口 |
| **GA 变化** | **为更大的 pull requests 生成、更大的上下文窗口、更好的延迟** |
| **定价** | Business 和 Enterprise 计划免费（beta 期即免费，GA 延续） |
| **定位** | 05-28 Diffs 发布时的 beta 功能（guided reviews），07-30 转正 |

[来源: Linear Changelog May 28 + Jul 30, 2026]

**为什么 Guided Reviews 是审查瓶颈的结构性响应？**

- **问题**：agent 产生代码的速度远超人类审查能力（06-29 已捕获「review 单线程瓶颈」，08-10 AI 工程经济学文档记录「中位 PR 42→72 行」）
- **Linear 的回答**：不是「让 AI 审 AI」（虽然也提供 agent 辅助），而是**降低人类审查大 PR 的认知负载**——把「从 200 文件里找重点」变成「按 section 引导，先核心后外围」
- **与 GitHub 08-07 effort levels 的互补**：GitHub 管「审查深度可调档」（Lite/Balanced 按风险配预算），Linear 管「审查结构可引导」（大 PR 自动分节）——**审查成本经济学（评估经济学）的两个正交维度在同周被两个平台分别产品化**

---

## 五、功能④ mobile coding sessions：移动端成 agent 管理面

| 设计 | 内容 |
|:-----|:-----|
| **移动能力** | Linear 移动 app：review 代码变更、行级评论、与 Linear Agent 迭代 |
| **交互方式** | 打开任意 diff → Changes tab 审查；点相关行加入消息 → 引导 coding session 方向 |
| **状态区** | My Issues → Assigned 新增 delegated issues 区：显示每个 coding session 状态，快速回到进行中的工作 |
| **平台** | iOS + Android |

[来源: Linear Changelog Jul 30, 2026]

**管理面移动化的两层含义**：

1. **监督可达性**：agent 工作流「全天候化」（07-31 已捕获的信号）需要配套的**监督全天候化**——离开工位仍能 review/评论/迭代，否则 agent 跑得再快也没人接得住。**自主性（autonomy）每提升一档，监督可达性（supervision reachability）就要同步提升一档**，否则失控风险敞口扩大。
2. **状态可见性**：delegated issues 区把「每个 coding session 在哪、进行到哪」变成移动端的一等公民——与 08-07 Agent 安全周更的「假身份/越权」序列对照：**可监督的前提是状态可见**，移动端把可见性从桌面扩展到口袋。

---

## 六、统一框架：agent 产出信任链三级演进

```text
Level 0: Traceable  07-23 Text Attribution   "who wrote it"        -> document layer (human/agent/loop)
Level 1: Reviewable 05-28 Diffs + Guided(beta) "is the change OK"  -> code layer (diff + guidance)
Level 2: Auditable  07-30 Signed commits     "who/what mechanism"  -> commit layer (crypto signature)

Supervision: mobile + delegated issues status (07-30) -> "watch & control anywhere"
Orchestration: Copilot for Linear (07-23/30)          -> "cross-platform delegated execution"
```

**演进逻辑**：每一级回答一个「问责问题」——可追溯回答「内容是谁产生的」，可审查回答「改动是否被认可」，可审计回答「落地提交的身份是否可信」。**Linear 在一个月内（07-23→07-30）把问责链从文档层延伸到提交层，并用移动端+跨平台编排把监督与执行扩展到工具边界之外。** 这不是功能堆叠，而是**「agent 产出要可解释、可归属、可追责」这一需求的系统性产品化**。

---

## 七、与 GitHub 侧治理套件的对照（08-04~07）

| 维度 | GitHub（08-04~07 六连发） | Linear（07-30 四连发） |
|:-----|:--------------------------|:-----------------------|
| 审查 | effort levels GA（深度可调） | Guided Reviews GA（结构可引导） |
| 审计 | usage metrics API 按 agent 计量 | signed commits + admin 强制 |
| 连接管控 | MCP allowlists（fail closed） | Copilot for Linear（跨平台委派） |
| 计量/监督 | impact dashboard ROI 板块 | mobile 管理面 + delegated issues 状态 |
| 共同主线 | **三权回收（判断/预算/集成）** | **信任链补全（追溯/审查/审计/监督）** |

**解读**：两家平台在同一个月把治理叙事推到前台，但切入点不同——GitHub 从「平台持有者」视角回收组织三权，Linear 从「工作流持有者」视角补全产出信任链。**两者叠加 = AI 编程/PM 生态的「治理基线」正在成形**：审查可调、计量可拆、连接可管、签名可强、监督可达。任何新平台若缺失其中一环，将在企业准入评估中被视为不完整。

---

## 八、与本地知识库的闭环

- **与 07-28 治理三连**（Linear Text Attribution）：07-23 文档层溯源 → 07-30 提交层签名，**Linear Agent 能力矩阵「读/写代码+文档」的治理侧补全**（从「能写」到「写的能审计」）
- **与 08-10 GitHub Copilot 治理+ROI 套件**：同日归档，本文为其「Linear 侧镜像」——三权回收（GitHub）× 信任链补全（Linear）双主线互证
- **与 08-08 OpenAI Symphony × Jira**：编排与工作锚点解耦（Atlassian 表述）→ Copilot for Linear 是同一架构方向的 Linear 实现，**跨平台委托成为行业共识的第二份证据**
- **与 MEMORY「约束脚本化=最高杠杆」**：admin 强制签名 = 把「审计要求」从文化期望变成系统准入条件——与「把检查自动化」同构
- **与 MEMORY「自主性可观察」**（08-03）：mobile 管理面 + delegated issues 状态区 = 「自主性保持可观察」的移动端落地
- **与 08-10 secret scanning**：连接管控（allowlists）+ 产出审计（签名）+ 密钥拦截（scanning）= AI 时代平台安全边界的三个拼图

---

## 九、批判性审视

1. **签名 ≠ 溯源到具体 agent**：签名 key 绑定的是「上传 key 的身份/机制」，但一个 key 可能对应多个 session/agent 实例——「到底是哪个 prompt/哪次循环产生的」仍未到内容级粒度（Text Attribution 在文档层做到了段落级，代码层只有提交级）。**审计粒度仍比文档层粗。**
2. **admin 强制的例外路径未说明**：未上传 key 时是「整个 coding sessions 功能禁用」还是「仅禁用提交」？本地开发/手动提交是否受影响？Changelog 未展开，**强制范围边界待文档确认**。
3. **Copilot for Linear 的上下文保真度**：issue 评论引导（steer through comments）依赖评论→agent 的语义传递——复杂意图经评论转述是否有损（「有损转译中介」风险，MEMORY 已记录）？GitHub 侧未披露上下文如何打包给 agent。
4. **一手源局限**：Changelog 正文为产品公告（60s 阅读量级），机制细节（签名 key 存储、审计日志保留、跨平台 token 授权模型）均未公开——本文深度解读（信任链/准入语义）为**笔者框架化推理**，标注推论与事实边界。
5. **Guided Reviews 的「引导」质量未量化**：sections/explainers 由什么模型生成、大 PR 的上下文窗口上限、误引导率均无数据——规模化收益是产品叙事，缺独立验证。

---

## 十、可证伪预测（P1-P4）

- **P1（2026Q4 核验）**：Linear 或 GitHub 在 3 个月内推出「按 coding session 粒度」的签名/溯源（key 绑定 session ID 而非仅用户）——若 Text Attribution 的段落级粒度是产品方向，代码层会跟进
- **P2（2026Q4 核验）**：其他 PM 工具（Asana/Shortcut/Notion）在 2026 年内跟进「跨平台 agent 委派」或「产出签名强制」之一——信任链+跨平台编排成为 PM 工具标配
- **P3（2027 核验）**：Guided Reviews 的「引导式审查」成为大 PR 审查的事实标准（50%+ 头部团队采用），与 GitHub effort levels 合并为「审查即服务」双层结构
- **P4（2026H2 核验）**：Linear 将签名强制从 coding sessions 扩展到文档编辑（与 Text Attribution 合并为统一溯源体系）——「可审计」从代码层回灌文档层

---

## 十一、对本系统的启示

1. **「审计优先于效率」的准入设计**：本系统（CowAgent）的 AI 产出进知识库同样需要「签名」语义——当前有 git commit + [AI] 标识（人工/机制可区分），但**无内容级溯源**。可借鉴 Linear 的三级模型：提交级（git author）✅ → 变更级（diff 归属）部分 → 内容级（段落 attribution）待建。
2. **「编排与工作锚点解耦」落地**：本系统已有 harness（Bridge 枢纽）+ 记忆 + 定时任务的「工作锚点」结构；Copilot for Linear 证明外部执行器可挂接到锚点——**本系统的 scheduler/tasks.json 就是「工作锚点」，任何外部执行器（技能/脚本/API）都可挂接**，架构方向与行业共识一致。
3. **fail closed 的治理原则泛化**：admin 强制签名 = 「不满足条件即不可用」——本系统的约束体系（pipeline-constraint-enforcer）已是此原则的工程化，可进一步把「AI 产出必须带来源标注」从检查项升级为**写入准入**（不满足直接拒写而非事后标记）。
4. **监督可达性扩展**：mobile 管理面提示——本系统定时任务输出推飞书（已实现），下一步「移动端查看 session 状态/干预进行中任务」是可评估的监督面扩展。

---

## 参考来源

- [Linear Changelog — July 30, 2026](https://linear.app/changelog)：Signed commits / GitHub Copilot for Linear / Guided Reviews GA / Coding sessions on mobile / GitHub teams in reviews（一手，官网直抓）
- [GitHub Changelog — Copilot cloud agent for Linear GA](https://github.blog/changelog/2026-07-23-copilot-cloud-agent-for-linear-is-now-generally-available)（一手，07-23）
- [Linear Changelog — Linear Diffs](https://linear.app/changelog)（05-28，Guided Reviews beta 源）
- [Linear Changelog — Text attribution and agent-assisted editing](https://linear.app/changelog)（07-23，文档层溯源基线）
- 知识库交叉引用：[08-10 GitHub Copilot 治理+ROI 套件](../agent-engineering/2026-08-10-github-copilot-governance-roi-suite-deep-analysis.md) · [08-08 project-mgmt Jira Symphony](01_survey/project-mgmt/2026-08-08.md) · [07-28 治理三连](../07_industry-research/19_governance-permissions/2026-07-28-agentic-ai-governance-triad.md) · [08-01 project-mgmt Linear 登记](01_survey/project-mgmt/2026-08-01.md) · [07-31 project-mgmt mobile 登记](01_survey/project-mgmt/2026-07-31.md)

---

## Changelog

- **2026-08-10 v1.0**：创建。四事件总览 + signed commits 信任链分析（可审查→可审计、fail closed 对照）+ Copilot for Linear 跨平台编排（Symphony 对照）+ Guided Reviews GA 规模化 + mobile 管理面 + 统一框架（三级演进）+ 与 GitHub 08-04~07 套件对照 + 批判与预测。一手源：Linear Changelog Jul 30 整批（官网直抓）+ GitHub Changelog 07-23 GA。
