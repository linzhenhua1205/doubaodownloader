# 📚 weekly-reports — 报告与工程分析归档中心

> **定位**: 知识库的"报告层"——存放各类周期性报告（日报/周报/月报/季报/年报）与工程分析文档（git 提交、对话挖掘、输入数据分析、失效分析、AI 历程、知识库演进洞察）。
>
> **在知识库分类中的角色**: 按 `kb-effort-churn-diagnosis` v3.0 分类标准，本目录归为**工具类**（Reporter）——对系统的定期审视与治理报告，属工具投入而非业务产出。
>
> **索引/日志双轨制**: 本目录为**保留目录**（不参与 `scripts/tools/kb-global-index.py` 全局索引），自行维护 `index.md`（导航）+ `log.md`（变更账本）。

---

## 📑 目录

- [一、目录结构总览](#一目录结构总览)
- [二、七大内容类别 → 落盘映射](#二七大内容类别--落盘映射)
- [三、各子目录运作方式](#三各子目录运作方式)
  - [3.1 日报（00_daily/）](#31-日报00_daily)
  - [3.2 周报（01_weekly/）](#32-周报01_weekly)
  - [3.3 月报（02_monthly/）](#33-月报02_monthly)
  - [3.4 季报/年报（03_q/、04_yearly/）](#34-季报年报03_q04_yearly)
  - [3.5 知识库统计专项（07_kb_stat/）](#35-知识库统计专项07_kb_stat)
  - [3.6 记忆/对话/输入分析（06_memory/、06_conversation/、08_ai/）](#36-记忆对话输入分析06_memory06_conversation08_ai)
- [四、技能与脚本全景](#四技能与脚本全景)
- [五、定时任务锚点](#五定时任务锚点)
- [六、优化方向与建议](#六优化方向与建议)
- [七、Changelog](#七changelog)

---

## 一、目录结构总览

| 子目录 | 内容 | 状态 |
|:-------|:-----|:----:|
| [00_daily/](00_daily/index.md) | 每日知识库日报（三支柱结构） | 🟢 运行中（每日 08:10） |
| [01_weekly/](01_weekly/index.md) | 周报/双周报 | 🟢 运行中（每周日） |
| [02_monthly/](02_monthly/index.md) | 月度报告（5 大维度） | 🟢 运行中（每月最后一天） |
| [03_q/](03_q/index.md) | 季度分析 | 🟡 预留（空） |
| [04_yearly/](04_yearly/index.md) | 年度总结 | 🟡 预留（空） |
| [06_memory/](06_memory/index.md) | 记忆机制评估与洞察报告 | 🟢 已有 2 份 |
| [07_kb_stat/](07_kb_stat/index.md) | 知识库统计专项报告（4 核心 + 22 专题 + 8 子目录） | 🟢 运行中 |
| [08_ai/](08_ai/index.md) | AI 演进与用户活动专题 | 🟢 已有 1 份 |
| [09_other/](09_other/index.md) | 其他综合报告 | 🟡 预留（空） |
| [index.md](index.md) | 目录导航（子目录入口） | 🟢 |
| [log.md](log.md) | 全局变更账本 | 🟢 |

> 编号说明：05 号段历史缺失（迁移时未使用），现有编号为历史遗留，新子目录建议按序续号。

---

## 二、七大内容类别 → 落盘映射

| # | 内容类别 | 落盘位置 | 对应技能/脚本 |
|:-:|:---------|:---------|:--------------|
| 1 | 日报 / 周报 / 月报 / 季报 / 年报 | `00_daily/` `01_weekly/` `02_monthly/` `03_q/` `04_yearly/` | weekly-report-generator / monthly-report-generator |
| 2 | git 库提交情况 | `07_kb_stat/02-code-commit-analysis.md`、`07_kb_stat/07_git_footstep/` | knowledge-special-reports + `knowledge-stats-collector.py` |
| 3 | 对话挖掘分析 | `07_kb_stat/06_conversation/`、`06_memory/` | conversation-topic-analyzer / session-intent-analysis |
| 4 | 输入数据的分析情况 | `07_kb_stat/05_kbsys/`（content-metadata 等） | discover 管道 + 元数据提取脚本 |
| 5 | 系统失效分析 + 功能扩展记录 | `07_kb_stat/04_task/`（任务失效 RCA）、`07_kb_stat/05_kbsys/`（Bug 修复/设计归档） | fault-diagnosis 方法论 + 人工分析 |
| 6 | AI 用于知识库搭建的历程 | `08_ai/ai-evolution-and-user-activities.md` | 人工专题（LLM 辅助） |
| 7 | 知识库信息的记录与演进洞察 | `07_kb_stat/01/03/04-*.md`、`06_memory/` | knowledge-special-reports + kb-effort-churn-diagnosis |

---

## 三、各子目录运作方式

### 3.1 日报（00_daily/）

**产出**: 每日知识库日报 `00_daily/YYYY-MM-DD.md`（2026-06-03 起，现约 60+ 份）

**触发**: 📅 定时任务「知识库日报（每日8:10）」`10 8 * * *`；也可手动（"生成日报"）

**输入 → 输出链**:
```
scripts/kb-daily-data-gather.sh [REPORT_DATE]
  ├── scripts/kb-daily-files.sh        → 深度文档（git knowledge/ 排除 01_survey/、weekly-reports/，>100 行）
  └── scripts/kb-daily-survey-scan.sh  → 调研跟踪文件（01_survey/ 下日期匹配 YYYY-MM-DD*.md）
  + git log（knowledge/ 排除 01_survey）· memory/<date>.md 操作要点 · scripts/skills 变更
        ↓
tmp/kb-daily-data-{REPORT_DATE}/  ← 中间数据目录（metadata.json + 6 个 txt）
        ↓
weekly-report-generator 技能按「三支柱」生成日报
        ↓
00_daily/YYYY-MM-DD.md + 更新 00_daily/index.md、log.md
```

**时间窗口**: `[REPORT_DATE 08:00 → (REPORT_DATE+1) 08:10]`，跨两个自然日（覆盖上一日 08:00 至当日 08:10）。

**三支柱结构**: ① 调研跟踪摘要（分领域）② 深度分析文档 ③ Git/记忆/工具变更。日报聚焦**分领域**粒度。

### 3.2 周报（01_weekly/）

**产出**: `01_weekly/2026-WNN.md` 周报 + 双周报变体（如 `2026-W28-W29-biweekly.md`）

**触发**: 定时任务「知识库周报」每周日（07:00 / 21:45 双锚点，历史双轨）+ 手动

**输入 → 输出链**: 复用 `kb-daily-data-gather.sh` 聚合本周数据 → weekly-report-generator 按「核心活动回顾 + 行业跟踪概述」结构生成。

**与日报差异**: 周报把系统当**整体**看待（统计：跟踪文件数/行数/领域覆盖数/深度文档数），日报聚焦分领域。

### 3.3 月报（02_monthly/）

**产出**: `02_monthly/YYYY-MM-monthly-report.md`（2026-07 手动首份，2026-08-31 起自动）

**触发**: 定时任务「知识库月度报告（每月最后一天23:20）」`20 23 28-31 * *` + 脚本内最后一天校验（非最后一天自动退出）

**输入 → 输出链**:
```
scripts/monthly-report-data-gather.sh [YYYY-MM]  → tmp/kb-monthly-data-{YYYY-MM}/（8 类数据）
        ↓
monthly-report-generator 技能 → 5 大维度报告
```

**5 大维度**: ① 知识库变更（提交/规模/图表）② 编辑领域侧重点 ③ 质量报告分析 ④ 月度关键行业洞察 ⑤ 待办事务。

### 3.4 季报/年报（03_q/、04_yearly/）

**状态**: 🟡 预留空目录，仅有 index.md/log.md。

**建议触发时机**: 季报=季度最后一天；年报=12-31。届时由月报数据聚合（`monthly-report-data-gather.sh` 支持指定月份，可循环多个月合并）。

### 3.5 知识库统计专项（07_kb_stat/）

**核心 4 份报告**（knowledge-special-reports 技能维护）:

| 报告 | 频率 | 数据源 |
|:-----|:----:|:-------|
| 01-knowledge-directory-evolution.md（目录变迁 v1.8） | 周 | knowledge-stats-collector.py |
| 02-code-commit-analysis.md（git 提交 v1.8） | 周 | 同上 |
| 03-domain-focus-shift.md（领域漂移 v1.7） | 双周 | 同上 + memory 7-14 天 |
| 04-dimension-completeness.md（维度完备 v1.7） | 双周 | 同上 |

**输入 → 输出链**:
```
python3 scripts/kb-stat/knowledge-stats-collector.py → tmp/knowledge-stats-{date}.json
        ↓
python3 scripts/tools/knowledge-special-reports-updater.py [--collect-only | --report-only]
        ↓
更新 4 份核心报告 + 07_kb_stat/index.md
```

**触发**: 定时任务 3 个锚点——周日 07:55 collect（857f8eb0）、周日 22:00 auto-update（5cc2c5d1）、隔周 21:30 full（ee78b40d）。

**专题子目录**（人工/LLM 驱动的深度分析，非定时）:

| 子目录 | 内容 | 典型产出 |
|:-------|:-----|:---------|
| `00.token-consumption-analysis/` | Token 消耗统计（含图表 PNG） | v3.1 报告 + 8 图 |
| `02_dir_optiz/` | 目录优化方案与执行 | 3 套方案报告 |
| `03_skills_scripts/` | Skills & Scripts 质量/完备度 | 周质量报告 + 深度分析 |
| `04_task/` | 定时任务治理与失效分析 | scheduler RCA、tasks.json 根因 |
| `05_kbsys/` | CowAgent/CowChat 系统分析 | 架构分析、Bug 修复、设计归档、可观测性 |
| `06_conversation/` | 对话主题挖掘 | 主题/意图分析报告 |
| `07_git_footstep/` | Git 足迹周报 | 提交足迹 |
| `08_dir_review/` | 目录全面审查 | 分模块审查 + 汇总 |

### 3.6 记忆/对话/输入分析（06_memory/、06_conversation/、08_ai/）

| 目录 | 内容 | 触发方式 |
|:-----|:-----|:---------|
| `06_memory/` | Dream 机制评估、Memory 全量洞察 | 人工专题（memory_search 检索全量记忆后分析） |
| `07_kb_stat/06_conversation/` | 对话主题深度分析（四大阶段演化/知识维度/操作思维） | conversation-topic-analyzer：输入 `conversation-log/user-questions/` + `conversation-log/db-sessions/` |
| `08_ai/` | AI 2025.06→2026.07 演进 + 用户足迹 | 人工专题 |

**会话意图分析管道**（session-intent-analysis）: `scripts/intent_analysis/main.py --step all` → ① extract（`extract_user_questions.py`，去除定时任务）→ ② analyze（`analyze_topic_boundaries.py`，话题边界/任务切换）→ ③ report（`generate_intent_report.py`，LLM 深度解析）。输出到 `conversation-log/user-questions/` + `user_indent.md`。

---

## 四、技能与脚本全景

| 技能 | 用途 | 关键脚本 |
|:-----|:-----|:---------|
| [weekly-report-generator](../../skills/weekly-report-generator/SKILL.md) | 日报+周报（三支柱/时间窗口定义） | `kb-daily-data-gather.sh` `kb-daily-files.sh` `kb-daily-survey-scan.sh` |
| [monthly-report-generator](../../skills/monthly-report-generator/SKILL.md) | 月报（5 大维度） | `monthly-report-data-gather.sh` |
| [knowledge-special-reports](../../skills/knowledge-special-reports/SKILL.md) | 4 份专项统计报告 | `knowledge-stats-collector.py` `knowledge-special-reports-updater.py` |
| [conversation-topic-analyzer](../../skills/conversation-topic-analyzer/SKILL.md) | 对话主题聚类/时间演化/知识维度 | — |
| [session-intent-analysis](../../skills/session-intent-analysis/SKILL.md) | 会话意图分析（LLM 增强） | `scripts/intent_analysis/*.py` |
| [kb-effort-churn-diagnosis](../../skills/kb-effort-churn-diagnosis/SKILL.md) | 投入统计/治理诊断（分类 v3.0 + A/M/R/D） | 统计脚本（分目录/分月原始表） |
| [github-activity-report](../../skills/github-activity-report/SKILL.md) | GitHub 开源活动日报（写 01_survey/github/，非本目录但同族） | 每日 06:50 |

**中间数据目录**: 所有采集脚本先落 `tmp/`（`kb-daily-data-{date}/`、`kb-monthly-data-{YYYY-MM}/`、`knowledge-stats-{date}.json`），报告生成消费后按需清理。

---

## 五、定时任务锚点

| 任务名 | cron | 产出 |
|:-------|:-----|:-----|
| 📅 知识库日报 | `10 8 * * *` | 00_daily/YYYY-MM-DD.md |
| 知识库周报 | `0 7 * * 0` / `45 21 * * 0`（历史双轨，建议归一） | 01_weekly/2026-WNN.md |
| KB-special-reports-collect | `55 7 * * 0` | 采集（tmp/） |
| knowledge-special-reports-auto-update | `0 22 * * 0` | 4 份专项报告更新 |
| KB-special-reports-full | `30 21 */2 * 0`（隔周） | 全量更新 |
| 📅 知识库月度报告 | `20 23 28-31 * *`（+脚本内校验） | 02_monthly/YYYY-MM-monthly-report.md |
| 📊 GitHub 开源活动日报 | `50 6 * * *` | 01_survey/github/YYYY-MM-DD.md（相关但异目录） |

> ⚠️ 定时任务输出统一走飞书 channel（channel_type 设置见 RULE.md/记忆）。

---

## 六、优化方向与建议

### 结构层面
1. **05 号段缺失**: 目录编号 00/02/03/04/05/06/07/08 中 05 缺失（历史迁移遗留）。建议后续新增主题时优先用 05 或按语义重编号（低优先，避免大迁移）。
2. **周报双锚点归一**: 周日 07:00 与 21:45 两个周报任务并存（历史双轨），建议确认是否保留两份差异版本，否则归一为一份（如 21:45 晚版覆盖当日数据更全）。
3. **预留目录启用**: 03_q/、04_yearly/、09_other/ 为空——建议在 README 或 index 中写明"触发条件 + 模板"，避免出现"空目录无人知道何时用"。

### 内容层面
4. **日报结构历史不齐**: 2026-06 早期日报无「今日核心信号 Top5」结构，07 月后统一。历史文件可保持原样（作为演进证据），新文件严格遵守模板。
5. **报告交叉链接**: 日报→周报→月报为递进聚合关系，建议在报告头部互相链接（如月报引用当月周报、周报引用周内日报），形成可追溯链。
6. **可观测性闭环**（2026-08-06 已沉淀）: 日报聚焦分领域、周报/月报把系统当整体——目标→目录→文件→投入→提交→产出六大子系统全部量化可观测。新报告应接入该框架，避免"考究式分类"。

### 工具层面
7. **季报/年报脚本化**: 月报数据采集已支持指定月份，季报/年报可复用 `monthly-report-data-gather.sh` 多月份循环聚合，不必另写脚本。
8. **索引维护**: 本目录为保留目录，新增/更新报告后须同步：子目录 index.md 追加条目 + 本目录 log.md 记 changelog（倒序）。勿依赖 kb-global-index.py。
9. **Token 成本意识**: 定时报告为 token 消耗大户，优先合并 session、压缩输出；周报/月报尽量复用采集脚本中间产物，避免重复 git 扫描。

---

## 七、Changelog

- **2026-08-06** | 新增 README.md v1.0 — 首次系统化描述目录定位、七大内容类别映射、各子目录运作方式（skills/scripts/定时任务/输入输出链）、优化方向 9 条。
