# 📋 研发管理与研发提效 — 行业跟踪框架

## 核心跟踪问题
- AI 辅助研发（AI coding agent）最新进展与影响
- 研发效能度量/DevOps 新实践
- 研发流程工具更新（GitHub/GitLab/Jira/Cursor）
- AI 开发框架/平台的演进
- 研发团队组织模式创新

## 搜索关键词
- `AI coding agent productivity 2026` `Cursor AI research`
- `GitHub Copilot` `Claude Code` `Devin AI` `Cursor`
- `DevOps latest trends` `developer experience DX`
- `研发效能` `AI辅助编程 2026` `AI coding 影响`
- `arXiv:2604` `arXiv:2605` (结合 AI coding / software engineering)

## 最新跟踪记录
- **2026-07-08**: Claude Code v2.1.203-204 (30+ 项稳定修复：~7MB binary缩减, ~37% CPU优化, daemon/background agent/网络断连修复), GitHub Enterprise 治理 7 天 7 项 GA (managed-settings.json/Copilot Vision/Browser tools/Kimi K2.7/session streaming/cost centers + per-user budgets + review cycles + time to adoption API + Copilot app全员可用 + rulesets驳回控制 + restrict dismissals), Atlassian Teamwork Lab "AI让工作变大" (1,000人双盲: 92%角色扩大, 高频用户2x跨职能, 但同事连接排最后), Atlassian Agents in Jira 成为一等公民 (assignable/@mentionable/automation + 第三方Agent接入), Cursor 3.10 Team MCPs 治理
- **2026-07-07**: Claude Code v2.1.202 (Dynamic workflow sizing + /review回退快单通), GitHub Copilot Billing Preview App 退役, Atlassian×Dropbox AI转型 (Super User度量, 30%员工达≥40次/周), Atlassian Claude Agent for Jira, HBR绩效管理新指标 + HBR心态比技能重要

## 来源优先级

| 优先级 | 来源 | 说明 |
|:-----:|:-----|:-----|
| 🥇 Tier 1 | **arXiv.org** (cs.SE/cs.HC) | AI 辅助编程学术研究 |
| 🥇 Tier 1 | **GitHub / GitLab / JetBrains 官方研究** | 开发者生态数据 |
| 🥈 Tier 2 | **Cursor / Claude Code / Devin 官方 blog** | 工具演进 |
| 🥈 Tier 2 | **Google Research / MSR 论文** | 大型实证研究 |
| 🥉 Tier 3 | **InfoQ / ThoughtWorks 技术雷达** | 趋势分析 |

## 质量门槛
- ✅ **值得记录**：有数据的实证研究/新工具发布/生产环境效果数据
- ❌ **跳过**：纯观点/无数据支持的趋势预测/工具 PR

## 输出模板

```markdown
# 📋 研发管理与研发提效 — 当日动态 YYYY-MM-DD

> 采集时间: YYYY-MM-DD HH:MM | 来源: {来源列表}

---

## {分类标题}

### {条目标题} ({来源}, {日期})
- {关键发现/数据}
- {影响分析}
- 📌 【深度跟踪】{交叉验证/趋势判断}

---
## 📊 趋势判断
```

## 输出路径
- `knowledge/01_survey/rd-management/YYYY-MM-DD.md`

## 交叉引用
- AI 工具评估 ↔ `tools/` (研发工具链)
- 团队效率 ↔ `enterprise-mgmt/` (组织管理)
- Agentic PR 影响 ↔ `product-dev/` (产品研发)
