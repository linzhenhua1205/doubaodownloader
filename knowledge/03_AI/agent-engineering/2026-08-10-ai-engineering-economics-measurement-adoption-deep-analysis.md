# 💰 AI 工程经济学四维：建 vs 买 / 测 vs 声称 / 采用 vs 使用 / 标准 vs 治理（TNS 8/8-8/9 四文合一）

> **统一主线**: 2026-08-08/09 四篇 TNS 文章从四个维度回答同一个问题——**「AI 时代的工程投入，如何证明价值？」**：①**建 vs 买**（Platform Engineering ROI：自建平台真实成本 $7.5M/年、5 年 $37.5M，RDD 与 12-18 个月创新差距）②**测 vs 声称**（三报告交叉验证：AI 投资 28× 而 velocity 停滞，仅 31% 在测量、26% 声称 >25% 收益——「报收益的人大多不是能证明收益的人」）③**采用 vs 使用**（三层模型：个人 loop 不持久、永久交接人走即失、团队规范唯一经得起 turnover；Goodhart 陷阱 + review 单线程瓶颈）④**标准 vs 治理**（Agent Plugins 1.0.0 五巨头背书统一打包格式，但治理被 defer 给客户端——「write once run anywhere = compromise once run everywhere」）。**四维合一的结论：AI 工程投入正在经历从「信仰驱动」到「证据驱动」的清算期。**
>
> **关键词**: 平台工程 ROI · RDD · DXI · AI 生产力测量 · adoption vs usage · 团队规范 · Agent Plugins · MCP/Skills 打包 · Goodhart
>
> **数据源**: ✅ 4 篇 TNS 全文一手抓取：
> - [Platform Engineering ROI: What it costs to build your own platform](https://thenewstack.io/real-cost-diy-platform/)（Michael Coté, **08-09 12:00pm**）
> - [AI coding got faster. Why didn't engineering?](https://thenewstack.io/ai-productivity-measurement-gap/)（Jennifer Riggins, **08-09 10:00am**）— DX/LinearB/LeadDev 三报告交叉验证
> - [AI adoption isn't the same as AI usage](https://thenewstack.io/ai-adoption-versus-usage/)（Harshal Shah, **08-08 11:00am**，原发于 webflow.com）
> - [Five AI rivals just backed a shared plugin standard](https://thenewstack.io/agent-plugins-open-standard/)（Adrian Bridgwater, **08-08 9:50am**）— Agent Plugins 1.0.0
>
> **素材分级**: ✅ 一手全文 · 🔵 既有知识库锚点（MEMORY AI 悖论/统计铁律/前移后移 / 08-05 AI 产出=毛利非净利 / 08-10 评估治理 / 08-10 技能门控 / 08-03 平台工程）
>
> **日期**: 2026-08-10 | **领域**: AI 工程经济学 / 平台工程 / 开发者体验 / Agent 生态标准

---

## 📑 目录

- [〇、结论概要](#〇结论概要)
- [一、四维总览](#一四维总览)
- [二、维度① 建 vs 买：自建平台的真实成本（Platform ROI, Coté）](#二维度①-建-vs-买自建平台的真实成本platform-roi-coté)
  - [2.1 $7.5M/年从哪来：60 人 × $125K](#21-75m年从哪来60-人--125k)
  - [2.2 「买」的真实人力配比](#22-买的真实人力配比)
  - [2.3 成本为何被系统性低估：RDD + 影子平台团队](#23-成本为何被系统性低估rdd--影子平台团队)
  - [2.4 12-18 个月创新差距：第三年会议](#24-12-18-个月创新差距第三年会议)
  - [2.5 三动作：算全口径 / 诚实看第三年 / build 差异化 buy 商品](#25-三动作算全口径--诚实看第三年--build-差异化-buy-商品)
- [三、维度② 测 vs 声称：AI 生产力测量鸿沟（三报告交叉验证）](#三维度②-测-vs-声称ai-生产力测量鸿沟三报告交叉验证)
  - [3.1 DX：AI 投资 28× 而 velocity 停滞，DXI 首次下跌](#31-dxai-投资-28-而-velocity-停滞dxi-首次下跌)
  - [3.2 线性B：PR 大小与 AI 采用成败强相关](#32-线bpr-大小与-ai-采用成败强相关)
  - [3.3 LeadDev：31% 测量 vs 26% 声称收益](#33-leaddev31-测量-vs-26-声称收益)
  - [3.4 三报告合一的「测量鸿沟」结构](#34-三报告合一的测量鸿沟结构)
- [四、维度③ 采用 vs 使用：三层模型（AI adoption, Shah）](#四维度③-采用-vs-使用三层模型ai-adoption-shah)
  - [4.1 三层采用：个人 loop / 永久交接 / 团队规范](#41-三层采用个人-loop--永久交接--团队规范)
  - [4.2 关键测试：移除工具后什么会坏](#42-关键测试移除工具后什么会坏)
  - [4.3 Goodhart 陷阱与 review 单线程瓶颈](#43-goodhart-陷阱与-review-单线程瓶颈)
  - [4.4 Webflow 实践：prompts 作为共享版本化 artifacts](#44-webflow-实践prompts-作为共享版本化-artifacts)
  - [4.5 三动作](#45-三动作)
- [五、维度④ 标准 vs 治理：Agent Plugins 1.0.0](#五维度④-标准-vs-治理agent-plugins-100)
  - [5.1 事实：五巨头背书 + Vercel 发起](#51-事实五巨头背书--vercel-发起)
  - [5.2 格式：plugin.json manifest + 固定组件位置](#52-格式pluginjson-manifest--固定组件位置)
  - [5.3 冷水：compromise once run everywhere](#53-冷水compromise-once-run-everywhere)
  - [5.4 支持与担忧：减少碎片化 vs lock-in 转移](#54-支持与担忧减少碎片化-vs-lock-in-转移)
- [六、统一框架：AI 工程经济学四维矩阵](#六统一框架ai-工程经济学四维矩阵)
- [七、与本地知识库的闭环](#七与本地知识库的闭环)
- [八、批判性审视](#八批判性审视)
- [九、可证伪预测（P1-P6）](#九可证伪预测p1-p6)
- [十、对本系统的启示](#十对本系统的启示)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 〇、结论概要

**四篇文章从四个维度共同宣告：AI 工程投入进入「证据清算期」——投入可以信仰驱动，但证明价值必须证据驱动。**

1. **建 vs 买（平台 ROI）**：自建内部开发者平台的真实成本 = **60 人 × $125K = $7.5M/年，5 年累计 $37.5M**——且被系统性低估（分散在多个成本中心、影子平台团队无人记账、RDD 激励）。买平台的人力配比低一个数量级（6,500 devs / 16 ops）。**最致命的是 12-18 个月创新差距**：vendor 团队比你大、路线图由所有客户供资，第三年「加 Vendor 上季度已发的 AI 服务」的会议就是 ROI 蒸发点。
2. **测 vs 声称（生产力鸿沟）**：DX 报告 **AI 投资 28× 而 velocity 停滞**、DXI 首次下跌 2 分（maintainability 升但 change confidence 转负）、中位 PR 从 42→72 行；LinearB elite <100 行/PR vs bottom >228 行；LeadDev **仅 31% 在测量、26% 声称 >25% 收益**——「报收益的人大多不是能证明收益的人」。
3. **采用 vs 使用（三层模型）**：三种「采用」价值天差地别——**个人 loop**（不持久，压力下回退）→ **永久交接**（人走即失）→ **团队规范**（唯一经得起 turnover）。关键测试：「如果移除工具，什么会坏？」——答「没有，只是有点烦」= 你只有订阅，没有采用。Webflow 把 prompts 变成共享版本化 artifacts = 团队规范的具体化。
4. **标准 vs 治理（Agent Plugins）**：OpenAI/AWS/Cursor/GitHub/Microsoft 五巨头背书 Vercel 的 Agent Plugins 1.0.0（打包 Agent Skills + MCP servers，plugin.json manifest），是**生态标准化的标志性事件**；但 Grainger 的 Pavan Madduri 泼冷水：「write once run anywhere = compromise once run everywhere」，**治理/安装策略/权限管理被显式 defer 给客户端**——标准赢了战争，治理可能输掉战役。

**一句话**：这四篇是 2026-08「AI 工程泡沫挤出」的媒体侧信号——与 08-05 本地「AI 产出=毛利非净利」、08-10「评估治理」同构：**价值证明从「demo 与声称」转向「测量、归属与治理」。**

---

## 一、四维总览

| 维度 | 文章/作者 | 核心问题 | 关键数据 | 一句话结论 |
|:-----|:----------|:---------|:---------|:-----------|
| **建 vs 买** | Platform ROI（Coté, 08-09） | 平台自建贵不贵？ | $7.5M/年、5 年 $37.5M、12-18 个月差距 | 自建=在公司内部开一家平台厂商，多数人没意识到 |
| **测 vs 声称** | AI productivity（Riggins, 08-09） | AI 真的提升了工程？ | 28× 投资 vs 停滞；31% 测量 vs 26% 声称 | 大多数收益声称无法被测量支持 |
| **采用 vs 使用** | AI adoption（Shah, 08-08） | 采用到底指什么？ | 三层模型；「移除什么会坏」测试 | 80% 活跃度图表掩盖了团队规范从未建立 |
| **标准 vs 治理** | Agent Plugins（Bridgwater, 08-08） | 插件标准化的代价？ | 5 巨头背书；治理 defer 给客户端 | 互操作赢，治理可能成为新的失败点 |

> 📌 四维是同一枚硬币的四个面：**价值证明 = 成本可见（建vs买）× 效果可测（测vs声称）× 采用可持久（采用vs使用）× 生态可治理（标准vs治理）。**

---

## 二、维度① 建 vs 买：自建平台的真实成本（Platform ROI, Coté）

### 2.1 $7.5M/年从哪来：60 人 × $125K

**「周末项目」变成「60 人无限财务承诺」**——按 CNCF 平台参考架构对齐：

| 产品团队（7 个） | 人数 | 说明 |
|:----------------|:-----|:-----|
| infrastructure / operations / deployment | 7-9 人/队 | 平台核心 |
| runtime & middleware / database | 7-9 人/队 | 运行时与数据 |
| security / coaching（developer enablement） | 7-9 人/队 | 安全与赋能 |
| scrum masters + product owners | 若干 | 协调管理 |
| **合计** | **~60 人** | 每个都是「神话般的 two-pizza team」 |

**成本表**（原文）：

| 年度 | 年成本 | 累计 |
|:-----|:-------|:-----|
| Year 1-5 | $7.5M | $7.5M → $37.5M |

> 「Five years in, you've spent **$37.5 million on payroll alone** for the team that builds your platform, not even your apps.」——5 年 $37.5M 只是建平台的工资，还不是应用。

### 2.2 「买」的真实人力配比

买商业平台后，只需要「运营」人力而非「构建+维护」人力：

| 按开发者 | 按团队 | 按应用 |
|:---------|:-------|:-------|
| 6,500 devs / 16 ops | 45 app teams / 5 ops | 350 apps / 7 ops |
| 2,500 devs / 5 ops | 300 app teams / 4 ops | 300 apps / 8 ops |
| 1,200 devs / 6 ops | | |

**比例差距一个数量级**——因为买方的团队**不需要持续构建**：不需要维护 APIs、集成、开发者框架、安全管道、仪表盘、升级工具、下一个 AI 能力、下一个合规制度。

### 2.3 成本为何被系统性低估：RDD + 影子平台团队

| 隐藏成本机制 | 说明 |
|:-------------|:-----|
| **分散成本中心** | license 是一张 PO 上可见的数字；build 人力分散在多个成本中心「看起来像正常招聘」——**没人对这些人跑 =SUM** |
| **影子平台团队** | 每个开发组至少 1 人做平台与应用的胶水工作（构建/流水线集成/安全/部署）——业务案例表里**完全没有** |
| **RDD（résumé-driven development）** | 「我们交付了基于 K8s 的平台」比「我们让所有人用上买来的东西」更适合晋升材料；引用 Fritzsch et al. 2021 实证研究：RDD 导致「复杂甚至不可维护的软件」 |

**RDD 的机制**：当员工按「交付新技术」获得报酬和声望，他们会追逐新技术技能 → 当前工作加薪 + 为跳槽铺路 → 但**不产生运营卓越**。越英雄主义越有回报——自建平台需要大量英雄主义，所以有吸引力。

### 2.4 12-18 个月创新差距：第三年会议

> 「The year-three meeting where someone says 'we need to add the AI services that Vendor X shipped last quarter' is the meeting where the ROI quietly evaporates.」——「我们要加 Vendor X 上季度已发的 AI 服务」的第三年会议，就是 ROI 悄悄蒸发的会议。

**为什么差距只增不减**：vendor 团队比你大 + 路线图由所有客户供资（不只你一家）+ **AI 每季度都在变**——自建团队能跟上「vendor 两季度前就发的能力」已算不错，差距只会扩大。

**经济学根基（200 年历史）**：1817 Ricardo 比较优势——即使你什么都能做好，也应专注最擅长的，其余用贸易换；Wardley maps——已商品化的应买；Abby Bangser（KubeCon NA 2025）：「不是重建市场上能买到的，而是把时间花在组织特有的、重要的东西上」。

**测试**：客户会因为你平台选你吗？Albert Heijn/Jumbo 否；Picnic 只有定制窄体送货车是——**平台是管道（plumbing），不是差异化**。

### 2.5 三动作：算全口径 / 诚实看第三年 / build 差异化 buy 商品

| 动作 | 内容 |
|:-----|:-----|
| **① 算全口径成本** | 60 人上限、30 人下限（偷工减料）；乘以 fully loaded 成本；**放上 PPT**；按 1/3/5 年乘开——license vs engineers 的对比自己就能结束辩论 |
| **② 诚实看第三年** | 计算完整平台 + 持续维护成本（维护/集成/新功能追赶）；问「你的平台团队能跟上 AI 每季度的变化吗？」 |
| **③ build 差异化层，buy 商品层** | 门户/golden paths/业务系统集成 = 差异化 → 建；基础设施/可观测性背板/secrets/证书管理/容器注册表 = 商品 → 买 |

**最终判断**：每个自建内部平台的企业，无论高管是否承认，都在公司内部「开了一家小型平台厂商」——平台厂商的经济学广为人知且大多严酷；多数人没意识到这个选择，因为**这个选择从没被大声做过，是被惯性做的**。

---

## 三、维度② 测 vs 声称：AI 生产力测量鸿沟（三报告交叉验证）

### 3.1 DX：AI 投资 28× 而 velocity 停滞，DXI 首次下跌

**DX《State of AI Impact in Engineering》**（测量速度/有效性/质量/影响四维）：

| DX 发现 | 数据 | 解读 |
|:--------|:-----|:-----|
| **AI 投资** | **28×**（尤其 >99 工程师的公司） | 「唯一呈指数增长的是成本」——DX 副 CTO Justin Reock |
| **velocity** | 停滞甚至下降 | 创新比率（新功能 vs 维护/杂务）持平——**AI 没有释放工程师时间去做新业务** |
| **DXI 首次下跌** | 跌 2 分（行业wide） | DXI = code maintainability + change confidence 两驱动 |
| **分裂** | maintainability ↑ 但 change confidence **转负** | 「更容易理解/改动代码，但更不敢发布」——Reock |
| **PR 大小** | 2025-07 中位 42 行 → 2026-07 **72 行** | AI 时代 PR 变大 |
| **incremental delivery** | 上季度最大跌幅 | 小步增量交付指标崩了——连带 revert/审查/文档/测试全受影响 |

**DXI 的经济价值**：每点 DXI 改善 = 每工程师每年返还 **10 小时**。首次下跌（还是发生在「积极投资 DX 的客户」群体——本该向上的）是强警示信号。

### 3.2 LinearB：PR 大小与 AI 采用成败强相关

**LinearB《AI engineering productivity gap report》**：253 个组织按 AI 使用分 4 桶：

| 桶 | PR 平均大小 |
|:---|:-----------|
| **Elite（top 10%）** | **< 100 行/PR** |
| **Needs focus（底部）** | **> 228 行/PR** |

**小 PR 直接关联成功 AI 采用**——小批量更稳、更易 review、更少回归；AI 放大了「大 PR」问题（一次生成大量代码）。

### 3.3 LeadDev：31% 测量 vs 26% 声称收益

**LeadDev《AI Impact Report 2026》**（8 月底发布）：

| LeadDev 发现 | 数据 |
|:-------------|:-----|
| 团队在测量 AI 影响 | **仅 31%**（测量定义：真实生产力/安全风险/核心技能保留/agentic 治理/团队重组/初级招聘培训） |
| 采用「广泛或完全」 | 70%（自称） |
| 声称 AI 提升生产力 >25% | **26%**（含凭直觉、非确认数据） |

> 「The productivity optimism — 26% seeing big gains — and the measurement gap — only 31% actually tracking it — are two separate findings from two different questions... **most of the people reporting gains aren't the same people who can prove it.**」——LeadDev 主编 Michael Hill：**报收益的人大多不是能证明收益的人。**

### 3.4 三报告合一的「测量鸿沟」结构

```
          Measurement Gap
               |
     +---------+----------+
     |         |          |
   DX       LinearB     LeadDev
 (telemetry)(telemetry) (survey)
 28x vs      elite      only 31%
 stagnant    <100 LOC    measure
 DXI -2      bottom     26% claim
 PR 42->72   >228 LOC    >25% gain
             small PR    claim !=
             = success   proof
```

**三家共同点**：DX/LinearB 用自己的产品客户数据（**自选择偏差：客户都在积极投资 DX/AI**——即便如此数字仍然难看）；LeadDev 是访谈（无客观数据）。**真实行业可能更糟**（Reock：「我们的客户群在上升趋势里还看到下跌，非常令人担忧」）。

**组织规模因素**：小组织从 AI 获益更多——沟通税 n(n−1)/2（Mythical Man-Month）；a2bic.ai 案例：2 人 + 80 年经验 = 100 个初中级工程师的工作量；中型/大型组织在「装修问题」（renovation problem）——**为「写代码贵」时代设计的流程结构，在「写代码免费」时代不再适用**——Davidson：「代码写作现在几乎免费，但我们还抱着旧结构，而它们不便宜」。

---

## 四、维度③ 采用 vs 使用：三层模型（AI adoption, Shah）

### 4.1 三层采用：个人 loop / 永久交接 / 团队规范

| 层 | 定义 | 持久性 | 例子 |
|:---|:-----|:-------|:-----|
| **① 个人 loop** | 个人改变自己的工作回路（写 commit 消息/快速上手陌生代码） | **几乎不持久**——第一次截止日期就回退（压力下取最低不确定性路径） | 个人 prompt 技巧 |
| **② 永久交接** | 某人永久移交一个重复工作：「我不再做这个了，workflow 做，我检查输出」 | **存活过截止日期**（回退=给自己造工作）；**但人走即失** | 个人自动化脚本 |
| **③ 团队规范** | 团队**故意**改变流程：有人决定某步骤现在按某方式跑、写下来、不依赖任何人的热情 | **唯一经得起 turnover 和坏季度** | Webflow prompts 版本化 |

**大多数组织**：庆祝①、偶尔到②、从未到③——因为③不是工具问题：**买 license 是预算对话；改变规范 = 公开说旧方式更差，并在第三周新方式出问题时担责。**

### 4.2 关键测试：移除工具后什么会坏

> 「If you removed these tools tomorrow, what would break? Not what people would complain about. What would break. If the honest answer is 'nothing, people would be mildly annoyed,' you don't have adoption. You have a subscription.」——诚实的答案是「没什么会坏，只是有点烦」→ **你没有采用，你只有订阅。**

### 4.3 Goodhart 陷阱与 review 单线程瓶颈

**Goodhart 陷阱**：token 花费=有人打字；PR 数=commit 落地；「AI 写的代码占比」=自动补全被接受。**没有一项告诉你工作是否变好了**——数字成为目标后停止描述现实、开始描述激励（`expect(true).toBe(true)` 清空覆盖率门禁的经典类比）。

**review 单线程瓶颈（最锋利的洞察）**：

```
blank -> plausible draft   : AI accelerates 10x (leverage at task start)
plausible draft -> shippable: no acceleration (that half is still yours)
```

→ 工程师同时开 5 个任务 → 5 个都回来需要 review → **review 在一个人脑内单线程跑**（还是没写过的代码，要从头重建）→ **他们没有并行化，他们在自己的注意力上串行化，队列深度没人会故意选** → 周末更忙、更不确定 → 悄悄放弃 → 几周后表现为「使用率下降」被诊断为「培训缺口」——**不是培训问题，是工作形状问题**。

> 「Delegating to an agent has the same ceiling as delegating to a person: the review capacity of whoever stays accountable.」——委派给 agent 的天花板与委派给人相同：**问责者的 review 容量**。

### 4.4 Webflow 实践：prompts 作为共享版本化 artifacts

**Webflow 让「prompts 从个人财产变成共享版本化 artifacts」**：

| 之前 | 之后 |
|:-----|:-----|
| prompts 在 scratch 文件、私下调几周、换机器丢失 | 好 prompts 在 repo 里：**owner + 使用时机说明 + 变更 review，和代码一样** |
| 个人悄悄变好 | 新工程师继承好版本；有人改进时**所有人都得到** |

**为什么能持久**：不依赖任何人的热情——新工程师继承好版本而非花一个月重新发现；改进是集体资产而非个人资产。

### 4.5 三动作

| 动作 | 内容 |
|:-----|:-----|
| **① 每人永久杀掉一个重复手工任务** | 不是「试试 AI」——把它从周里拿走，让 workflow 成为 record owner；**一个保持死亡的任务 > 十个实验** |
| **② 每季度让一个团队规范正式化** | 写下来、小到真的能执行、具体到有人能违反它 |
| **③ 停止向上报告 usage** | 报告 usage 本该产生的 **outcome**——包括看起来比 usage 差的季度 |

---

## 五、维度④ 标准 vs 治理：Agent Plugins 1.0.0

### 5.1 事实：五巨头背书 + Vercel 发起

| 要素 | 事实 |
|:-----|:-----|
| 发起 | Vercel（agentic infrastructure 公司，08-06 周四发布） |
| 背书 | **OpenAI / AWS / Cursor / GitHub / Microsoft** 五巨头 |
| 内容 | 开放、厂商中立的标准：**打包 Agent Skills（开放标准目录格式，可移植/模块化/渐进加载）+ MCP servers** 为可分发插件 |
| 动机 | Skills 和 MCP servers 可在多客户端复用，但**各客户端打包/发现方式不同** |

### 5.2 格式：plugin.json manifest + 固定组件位置

> 「A directory with a plugin.json manifest and fixed locations for its components. The format is intentionally small and easy to implement, and it leaves installation, distribution, policy, user experience, and client-specific capabilities to each client.」——Jonathan Hefner（Vercel）

| 设计 | 说明 |
|:-----|:-----|
| **格式刻意小** | plugin.json manifest + 固定组件位置——易实现 |
| **明确留给客户端** | 安装/分发/策略/UX/客户端专属能力 |
| **契约开放** | 作者（构建扩展的开发者）与客户端（加载它们的应用）之间的契约「定义且开放」 |
| **组件类型** | 1.0.0 只覆盖 Skills + MCP servers；commands/hooks/agents 仍留客户端（TSC 未来可能扩展） |
| **治理公开** | 开源许可、维护者/贡献流程/技术决策公开——无单一公司路线图主导 |

### 5.3 冷水：compromise once run everywhere

**Grainger 高级云平台工程师 Pavan Madduri 的批评**：

> 「Standardizing the packaging and discovery of Agent Skills and MCP servers in ChatGPT, Cursor, Copilot, and VS Code would actually be helpful plumbing — but at the same time, a plugin that is now running in six different client applications represents an additional point of failure for permissions management.」

> 「The minute something becomes 'write once, run anywhere' for agents, it automatically becomes '**compromise once, run everywhere**', and this specification specifically defers governance, installation policy, and permissions management to the client application.」

> 「Interoperability without trust and permissions management is not a security architecture; it's just another distribution method for bugs and excessive permissions.」

**核心批评链**：①统一打包解决的是「容易问题」（plumbing）②但一个插件跑在 6 个客户端 = **权限管理的 6 个失败点** ③「write once run anywhere」对 agent =「compromise once run everywhere」④规范**显式 defer** 治理/安装策略/权限管理给客户端——**没有信任与权限管理的互操作不是安全架构，只是另一种分发 bug 和过度权限的方式**。

### 5.4 支持与担忧：减少碎片化 vs lock-in 转移

| 立场 | 人物/组织 | 观点 |
|:-----|:----------|:-----|
| **支持** | Edward Rothschild（Adronite CTO） | 减少跨客户端碎片化=降低企业 AI 采用摩擦；标准让能力可移植同时保留组织治理 |
| **支持+担忧** | Adam Dalloul（EmpirioLabs） | 打包一次跨 Codex/ChatGPT/Cursor/Copilot/Kiro/VS Code 是真赢（「早就该有了」）；**担忧 vendor namespaces**——「有用行为都进厂商命名空间，标准看起来开放，lock-in 只是转移了」 |
| **经验警示** | Dalloul | 「开源 agent 更新在稳定运行数周后破坏生产 workflow」——**版本化/测试/回滚不能是事后才想** |

---

## 六、统一框架：AI 工程经济学四维矩阵

```
AI Engineering Economics = f( cost visibility x effect measurability
                              x adoption durability x ecosystem governance )
                                   |                 |
                          build vs buy        measure vs claim
                          Platform ROI        Productivity
                          $7.5M/yr            28x vs stagnant
                          5yr $37.5M          DXI -2 pts
                          12-18mo gap         31% measure vs 26% claim
                                   |                 |
                          adoption vs usage   standard vs governance
                          Adoption            Agent Plugins
                          3-layer model       5-vendor backing
                          remove-what-breaks  governance deferred
                          review bottleneck   compromise once run everywhere
```

**四维的互相制约（核心洞察）**：

1. **测 vs 声称 是其他三维的前提**：不测量就无法判断建 vs 买（ROI 全是声称）、无法判断采用层（usage 数字掩盖规范缺失）、无法判断标准价值（治理缺失看不见）。**「测量鸿沟」是根问题。**
2. **采用 vs 使用 决定 ROI 是否成立**：$7.5M 建平台若只到「个人 loop」层，turnover 后归零；团队规范层才让平台投资复利。
3. **标准 vs 治理 是生态级的前移后移**：Agent Plugins 把治理**后移**给客户端（defer）——标准赢、治理留白；按本地「前移后移分析」，被后移的治理责任必须有接收方（客户端），否则就是责任真空（本地 08-10 VaG 已证明：无门控的技能准入会污染）。
4. **共同的时代背景**：**AI 投资进入「挤泡沫期」**——投入 28× 而产出停滞、声称大于证明、标准先于治理——2026H2 的工程经济学主题从「敢不敢投」变成「投了证明什么、谁来治理」。

---

## 七、与本地知识库的闭环

| 锚点 | 闭环内容 |
|:-----|:---------|
| **MEMORY：AI 悖论双生 55%/30% 已被 08-05 求证报告否定；工具时间占比稳定 25-35%** | 本批 DX 28× vs 停滞 = **第三次独立证据**（本地实证 + 08-05 报告 + DX/LinearB/LeadDev）——「AI 投入与产出脱钩」从争议变成共识 |
| **MEMORY：AI 产出=毛利非净利；统计铁律=给原始统计由用户聚合** | LeadDev「26% 声称 vs 31% 测量」= 毛利非净利的测量版；本地「统计铁律」要求原始数据——与三报告的自选择偏差批判一致 |
| **08-10 评估治理（AV-AIVAT）** | 「测 vs 声称」是「评估治理」在组织层的投影——AV-AIVAT 管评估成本（统计），测量鸿沟管评估意愿（组织） |
| **08-10 技能生命周期四门（VaG）** | Agent Plugins「治理 defer 给客户端」直接命中 VaG 的 pre-commit 门控——**标准化了打包，没标准化准入**；本地 6 步注册纪律 = 客户端侧应补的治理 |
| **MEMORY：MCP/A2A 双事实标准** | Agent Plugins 是 MCP 生态的「打包层」标准化——**传输标准（MCP）已定，分发标准（Plugins）刚定，治理标准（准入）未定**——三层递进 |
| **MEMORY：前移后移分析** | 「治理 defer 给客户端」= 后移；按本地框架，后移必须有接收方 + 能力补齐——否则责任真空 |
| **MEMORY：State of Teams 漏斗（采用85%→嵌入29%→转型14%）** | 三层模型（个人/交接/规范）与漏斗同构：**采用 ≠ 嵌入 ≠ 转型** |
| **08-03 平台工程** | Platform ROI 的「build 差异化 buy 商品」= 本地平台三态（工具/治理/认知）的经济学化 |
| **MEMORY：DORA 2025（sources 已归档）** | DXI/PR 大小/velocity = DORA 度量体系在 AI 时代的延续；2026-08 数据普遍转差 |

---

## 八、批判性审视

1. **Platform ROI 的 vendor 背景**：Coté 是 VMware Tanzu 员工，数字来自「我帮忙更新的 Tanzu 论文」——**$7.5M 与购买配比天然偏向 buy**；60 人/2-pizza 是结构推演非实证样本；「买」的隐性成本（迁移、定制、vendor 锁定）未计入。
2. **三报告的自选择偏差**：DX/LinearB 只用自家客户数据——**这些客户是「积极投资 DX/AI」的群体**，行业整体可能更糟（文中承认），也可能更好（不投资 DX 的公司测量方法不同）；LeadDev 26% 含直觉判断。
3. **PR 大小因果性存疑**：LinearB「elite <100 行」是相关非因果——小 PR 可能是成功采用的原因，也可能是好团队的既有习惯；DX「PR 42→72 行」跨年对比，混入 AI 之外的因素。
4. **三层模型的简化**：Shah 的三层是理想类型——现实中「团队规范」与「永久交接」会混合；「移除工具会坏什么」测试对已深度嵌入的团队同样有效但答案可能自我强化（「坏了=依赖=成功」的循环论证风险）。
5. **Agent Plugins 的时效性**：1.0.0 刚发布（08-06），五巨头背书是**声明级**非实现级——实际采用率/客户端支持未验证；「治理 defer」批评是基于规范文本的合理推演，客户端实际治理实践未知。
6. **证据等级**：四篇均为观点文/新闻，无一手研究数据——本分析引用的是「报告中的数字」，数字本身来自厂商报告（DX/LinearB/LeadDev），存在方法学差异（定量遥测 vs 访谈）。

---

## 九、可证伪预测（P1-P6）

- **P1（高置信）**：12 个月内 ≥2 家主流厂商发布「AI 工程 ROI 测量」标准/工具（类似 DORA 的 AI 版度量），「31% 测量率」成为行业批评基准并推动测量普及（2027-08 核验）。
- **P2（中置信）**：PR 大小成为 AI 工程治理的默认指标——CI 门禁加入 PR 行数上限（如 >200 行强制拆分），LinearB 的 elite/bottom 分界成为事实标准（2027-08 核验）。
- **P3（中置信）**：Agent Plugins 1.0.0 发布后 6 个月内出现 ≥1 起「跨客户端插件权限事故」被报道（write-once-run-anywhere 的安全兑现），推动 2.0 引入治理层（2027-02 核验）。
- **P4（中置信）**：「团队规范层采用」成为 AI 采用成熟度的默认标尺——出现类似 State of Teams 漏斗的 AI 采用分层报告，团队规范层比例成为行业基准（2027-08 核验）。
- **P5（中置信）**：自建平台 vs 购买的 ROI 讨论在 AI 时代加速倒向购买——12 个月内出现 ≥1 个知名公司公开「关闭自建平台、迁移到商业平台」案例（AI 能力追赶成本是关键）（2027-08 核验）。
- **P6（低置信）**：「DXI 下跌」在 2 个季度内被证明是 AI 转型的暂时阵痛而非长期趋势（DX 客户群恢复上行）——或反之，成为 AI 工程危机的标志性数据（2027-02 核验）。

---

## 十、对本系统的启示

1. **本地「测量优先」是正确姿势**：本系统已实践「统计铁律」（给原始数据、由用户聚合）——LeadDev 的 31% vs 26% 证明这是稀缺且正确的；**继续拒绝「声称驱动」的收益叙事**。
2. **AI 投入的「三层采用」检查**：本地工具/技能的使用应追问：是个人 loop（我顺手用）还是永久交接（流程替人）还是团队规范（写进 RULE/AGENT 的纪律）？——**只有第三层进知识库三件套纪律才算采用**。
3. **Agent 技能治理要补「准入」**：本地 6 步注册纪律（结构/查重/持久化确认）已覆盖 VaG 的部分维度；Agent Plugins 的「治理 defer 给客户端」提示：**本系统作为「客户端」，必须自带准入门控，不能等生态标准施舍**——已在 08-10 技能门禁篇提出升级清单。
4. **「review 单线程瓶颈」是 Agent 工作流的物理定律**：本系统多 agent 并行时，产出最终都汇到用户一人 review——**并行度上限 = 用户 review 容量**；合理设计是「减少需要人 review 的量」（自动化检查）而非无限加 agent。
5. **build vs buy 的本地版本**：本系统自建（知识库/技能/脚本）是**差异化层**（个人皮层），商品层（LLM API/存储/向量库）全部购买——符合 Coté 原则；**警惕 RDD**：技能/脚本的「造轮子」冲动要用「写前 grep 查重」纪律压制（已有）。
6. **PR 大小对本地 git 纪律的提示**：本地 git 提交 message 规范（[AI] type(scope): summary）已控制粒度；AI 大提交（41.6% AI 占比中可能存在超大提交）应关注——与 LinearB 发现同向。

---

## 参考来源

- [Platform Engineering ROI: What it costs to build your own platform](https://thenewstack.io/real-cost-diy-platform/) — Michael Coté，The New Stack，2026-08-09 12:00pm（✅ 全文一手抓取）
- [AI coding got faster. Why didn't engineering?](https://thenewstack.io/ai-productivity-measurement-gap/) — Jennifer Riggins，The New Stack，2026-08-09 10:00am（✅ 全文一手抓取；交叉验证 DX/LinearB/LeadDev 三报告）
- [AI adoption isn't the same as AI usage](https://thenewstack.io/ai-adoption-versus-usage/) — Harshal Shah，The New Stack，2026-08-08 11:00am（✅ 全文一手抓取；原发于 webflow.com 2026-08-05）
- [Five AI rivals just backed a shared plugin standard](https://thenewstack.io/agent-plugins-open-standard/) — Adrian Bridgwater，The New Stack，2026-08-08 9:50am（✅ 全文一手抓取；Agent Plugins 1.0.0）
- 本地：[评估治理深潜（AV-AIVAT + safety test）](2026-08-10-evaluation-governance-av-aivat-and-safety-test-risks.md)（08-10，同日姊妹篇）
- 本地：[Harness 优化与学习 + 技能生命周期四门](2026-08-10-harness-optimization-self-evolution-skill-gating.md)（08-10，VaG 门控）
- 本地：[KubeVirt 跨集群迁移](knowledge/05_tools/devops/2026-08-10-kubevirt-cross-cluster-live-migration-evpn-deep-analysis.md)（08-10，同日）
- 本地：MEMORY.md（AI 悖论双生/统计铁律/前移后移/MCP-A2A/State of Teams 漏斗）
- 引用：Résumé-Driven Development: A Definition and Empirical Characterization（Fritzsch, Wyrich, Bogner, Wagner, 2021-01）— 文中引用

> **诚实标注**：4 篇 TNS 文章均为观点/新闻文体；核心数字来自厂商报告（DX/LinearB/LeadDev），方法学差异（遥测 vs 访谈）存在，且均有自选择偏差；Platform ROI 数字来自 VMware Tanzu 论文（vendor 背景）。Agent Plugins 1.0.0 刚发布，背书为声明级非实现级。本分析为学术解读，非投资或采购建议。

---

## Changelog

- 2026-08-10：创建。素材=4 篇 TNS 全文一手抓取（08-08/09 窗口）；主线=AI 工程经济学四维（建vs买/测vs声称/采用vs使用/标准vs治理），核心证据=$7.5M 年成本/28× vs 停滞/31%vs26% 测量鸿沟/三层模型/Agent Plugins 治理 defer；与本地 AI 悖论实证（第三次独立证据）、评估治理、VaG 门控、MCP 三层递进闭环；P1-P6 可证伪预测。
