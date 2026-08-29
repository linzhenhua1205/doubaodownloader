---
name: knowledge-special-reports
description: Generate and maintain 4 specialized knowledge base reports: directory evolution, code commit analysis, domain focus shift, and dimension completeness. Use when (1) user asks to generate/update 专项报告/专题报告/special reports, (2) user asks about knowledge base health/directory/commit statistics/dimension coverage, (3) it's time for weekly/biweekly special report updates. Also supports automated periodic updates via cron/定时任务.
---

# Knowledge Special Reports Skill

## Overview

Maintain 4 specialized reports in `knowledge/weekly-reports/07_kb_stat/` that provide quantitative analysis of knowledge base health, evolution, and coverage.

## Report Inventory

| # | Report | File | Purpose | Update Freq |
|:-:|:-------|:-----|:--------|:-----------:|
| 1 | 📁 **目录变迁** | `07_kb_stat/01-knowledge-directory-evolution.md` | 目录结构演变、关键变迁事件 | 周 |
| 2 | 📊 **代码提交** | `07_kb_stat/02-code-commit-analysis.md` | Git commits 统计、频率、分布 | 周 |
| 3 | 🎯 **领域关注** | `07_kb_stat/03-domain-focus-shift.md` | 领域漂移、阶段特征、活跃度 | 双周 |
| 4 | 📐 **维度完备** | `07_kb_stat/04-dimension-completeness.md` | 各模块完备度、薄弱环节、改进路线 | 双周 |

## Workflow

### Step 1: Run automated data collection

```bash
cd ~/cow && python3 scripts/knowledge-stats-collector.py
```

This generates `tmp/knowledge-stats-{date}.json` with:
- Git commit stats (total, daily, monthly, per-module)
- Knowledge base stats (file count, size, directory depth, module breakdown)
- Memory file stats

### Step 2: Read collected stats

```bash
# Check latest stats file
ls -t ~/cow/tmp/knowledge-stats-*.json | head -1
```

Verify the data covers the expected period. If gaps exist, supplement with manual git log queries.

> ⚠️ **当日/最近日统计通常不完整**：采集时点在途提交尚未结算（历史案例：08.07=93→95、08.09=9→13），隔日重算会修正，单日/周数值以 git 重算为准。
> ⚠️ **周分布须统一 author-date 口径**：`git log --since/--until` 用的是 committer date，与 `%ad`（author date）混用会导致周归属错位、各周总和对不上总 commits；用 author date 重算后核验总和吻合再写入报告。

### Step 3: Update each report

For each report, read the current version, then update sections based on new data:

#### Report 1: Directory Evolution
- Update total file/size/dir counts
- Add any new directories since last report
- Add any directory migrations/restructuring events
- Update timeline table with recent events

#### Report 2: Code Commit Analysis
- Update total commits, daily/weekly distribution
- Refresh heatmap and milestone table
- Add new milestone commits

#### Report 3: Domain Focus Shift
- Read recent memory files (last 7-14 days) to identify new focus areas
- Update domain intensity radar
- Add any new stages/phase findings
- Update next-phase predictions

#### Report 4: Dimension Completeness
- Re-check each module's file count and depth
- Update completeness ratings where changed
- Refresh improvement roadmap

### Step 4: Regenerate index

```bash
cd ~/cow && python3 scripts/knowledge-special-reports-updater.py --collect-only
```

Then append a summary entry to global `knowledge/log.md` via `kb-log-append.py`（2026-08-19 起 07_kb_stat 不再维护独立 index.md）。

> ⚠️ **`index.md` 是人工维护的 SSOT**（含各子目录报告版本号的详细索引，当前约 22 条）。
> updater 脚本**不得覆盖它**：`--collect-only` 模式仅采集数据、不写 index.md；完整模式的自动索引（只扫根目录的简化版）输出到 `tmp/` 仅供参考。
> （2026-08-19 起 07_kb_stat 已无 index.md；全局根 index.md 由 kb-global-index.py 批量刷新，勿手工编辑。）

### Step 5: Update knowledge base logs

Append to global `knowledge/log.md` via `kb-log-append.py`（2026-08-19 起 weekly-reports 不再维护独立 log.md）:

```markdown
## {date}
- updated {report-names}
- new stats: {total_files} files, {total_commits} commits, {modules} modules
```

### Step 6: Verify and commit (mandatory)

报告更新后**必须提交并核验落盘**，未提交前不得向用户宣称完成：

1. **核验上次版本真实落盘**：更新前先 `git log --oneline -5 -- <report file>`，确认上一版声称的版本号确实已提交；若发现上次"声称已更新"但实际未提交（git log 显示仍是更早版本），说明该版本号无效，需重做本次更新并修正版本号。
2. **交叉核验关键数据**：总 commits、单日新高、活跃天数等硬指标以 `git log` / `git rev-list` 实际统计为准，不得沿用上一版报告数值；发现上版数据有误（如 47 应为 45）时在报告与 changelog 中标注修正。
3. **排除数据污染**：批量导入的超大文件（如 1.4M 行/个）会严重虚增行数/文件数，识别后单独排除并注明统计口径，避免后续版本继续失真。
4. **提交**：`git add <本次更新的报告/索引/log 文件> && git commit -m "KB special reports update {date}"`，随后 `git log --oneline -1` + `git status` 确认工作区干净。
5. **汇报以事实为准**：向用户汇报时必须基于已提交的内容；若上轮存在"声称完成但未落盘"，主动披露并说明本次已真实提交。

## Automated Updates via Scheduler

Set up cron-style scheduled tasks for periodic updates:

```bash
# Weekly (Sunday 15:00): Run stats collection + update index
scheduler action=create name="KB-special-reports-collect" \
  schedule_type=cron schedule_value="0 15 * * 0" \
  ai_task="运行 knowledge-special-reports skill 采集并生成 4 份专项报告"

# Bi-weekly (every other Sunday 15:30): Full report regeneration
scheduler action=create name="KB-special-reports-full" \
  schedule_type=cron schedule_value="30 15 */2 * 0" \
  ai_task="运行 knowledge-special-reports skill：读取统计数据，逐一更新3份专项报告（领域关注+维度完备），检查目录变迁和代码提交报告的时效性"
```

## Edge Cases

| Scenario | Handling |
|:---------|:---------|
| Stats script fails | Fall back to manual `git log` / `find` commands, extract key metrics |
| Script paths changed | Scripts moved from `knowledge/_scripts/` to `scripts/`. Use `scripts/knowledge-*.py` |
| No new commits in period | Report "no changes" clearly, don't fabricate data |
| New module created mid-period | Add to report with note "newly created, baseline established" |
| Report file doesn't exist yet | Create from template, populate with available data |
| Stats JSON missing | Run `knowledge-stats-collector.py` interactively |
| Huge data diff | Focus on delta (what changed) rather than full re-write |
| 上次声称更新但未落盘 | `git log --oneline -5 -- <report file>` 核验；若最后提交早于声称版本，重做更新并提交（见 Step 6） |
| 数据被批量导入超大文件污染 | 定位大文件（>10万行），排除后重算，报告中注明口径 |
| updater 脚本覆盖了 index.md | index.md 是人工维护的 SSOT（约22条详细索引），脚本不得覆盖；`--collect-only` 已修复为不写 index.md，完整模式索引仅输出到 tmp/。若仍被覆盖：`git checkout --` 恢复后用人工增量更新 |
