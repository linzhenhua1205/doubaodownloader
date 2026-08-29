---
name: monthly-report-generator
description: Generate structured monthly knowledge base reports covering 5 dimensions (KB changes with commit/size/charts, domain focus, quality analysis, key industry insights, todo list). Use when: (1) user asks to generate/create/make a monthly report, (2) user says "生成月报"/"月度报告", (3) it's the last day of the month scheduled at 23:20. Depends on scripts/monthly-report-data-gather.sh for data collection.
---

# Monthly Report Generator — 知识库月度报告

## Overview

生成覆盖 **5 大维度** 的知识库月度报告，保存到 `knowledge/weekly-reports/02_monthly/`。
每月最后一天 23:20 由定时任务触发；也可手动触发（`生成月报` / `月度报告`）。

**执行顺序（强制）**：

```bash
# 1. 先采集数据（产出 tmp/kb-monthly-data-{YYYY-MM}/ 9 个文件）
./scripts/monthly-report-data-gather.sh                # 当月
./scripts/monthly-report-data-gather.sh 2026-07        # 指定月份
# 2. 读取数据文件 → 按本文档模板撰写报告 → 保存到 02_monthly/
```

## 数据源映射（5 大维度）

| 维度 | 数据文件（tmp/kb-monthly-data-{YM}/） | 补充来源 |
|:-----|:-------------------------------------|:---------|
| **① 知识库变更情况** | `00-commits.txt` `01-numstat.txt` `03-new-files.txt` `04-size-stats.txt` | `git log` 当月提交；`07_kb_stat/02-code-commit-analysis.md` |
| **② 领域侧重点** | `02-module-dist.txt` `04-size-stats.txt` | 当月新增文件按模块分布；`07_kb_stat/03-domain-focus-shift.md` |
| **③ 质量报告分析** | `05-quality-snapshot.txt` | `check_md_format.py` / `check_tech_doc_quality.py` 抽样结果；当月 log.md 中修复记录 |
| **④ 月度关键行业洞察** | `06-insights-sources.txt` | 当月 `01_survey/` 跟踪文件、`memory/` 每日记忆、`weekly-reports/01_weekly/` 周报、`07_industry-research/` 专题 |
| **⑤ 待办事务列表** | `07-todo-sources.txt` | 当月 memory 中的待办/下一步/风险；MEMORY.md 行动项；周报遗留 |

## 月度报告模板（5 大维度）

报告文件名：`knowledge/weekly-reports/02_monthly/2026-08-monthly-report.md`（`{YYYY-MM}-monthly-report.md`）

```markdown
# 📅 知识库月度报告 {YYYY-MM}（{MM}月1日 ~ {MM}月{末日}）

> **元信息**: 文件状态=正式 | 覆盖月份=YYYY-MM | 生成方式=monthly-report-generator | 版本=v1.0
> **适用范围**: 知识库月度治理复盘、领域投入审视、质量追踪、行业洞察沉淀、待办跟进

## 目录 (TOC)
（按 §0~§5 + 附录）

## §0 执行摘要
（本月 3-5 条核心结论：规模/领域/质量/洞察/待办各一句话）

## §1 知识库变更情况
### 1.1 提交概况
- 全库提交 X 次 / knowledge/ Y 次（对比上月）
- 新增/删除/重命名文件数、增删行数（numstat）
- 单日提交峰值、工作日分布（如有数据）
### 1.2 规模变化
| 指标 | 上月末 | 本月末 | 变化 |
（md 文件数 / 总行数 / 顶层子目录数 / 各模块文件数）
### 1.3 图表呈现
- 图表 1：月度提交趋势（近 6 个月柱状图）
- 图表 2：模块提交分布（饼图/条形图）
- 图表 3：领域新增文件 TOP（条形图）
- 图表 4：质量通过率变化（如有历史数据）
（用 matplotlib 生成 PNG 保存到 02_monthly/assets/，无历史数据时标注"待积累"）

## §2 领域侧重点
- 当月投入 TOP 模块（提交数/新增文件数）
- 与上月对比的领域漂移
- 解读：投入是否符合业务优先级（AI 基础设施/存储/网络/供电等 P0-P2）

## §3 知识库质量报告分析
### 3.1 格式检查
- 抽样 X 个文件：通过/未通过、典型问题类型（R1/R2/R3）
### 3.2 深度质量检查
- 抽样文档 PASS/FAIL、得分分布、共性问题
### 3.3 质量趋势与改进建议
- 本月修复的质量问题（来自 log.md）
- 遗留质量问题 + 改进建议（3 条以内）

## §4 月度关键行业洞察
- 当月行业跟踪要点（按模块归纳，每条 1-3 句 + 数据来源）
- 3-5 条最重要的洞察（标记 ⭐ 重点）
- 与知识库已有结论的呼应或修正

## §5 待办事务列表
| # | 待办 | 来源 | 优先级 | 状态 |
（来自当月 memory/周报/专项报告的待办 + 新增建议）

## 附录
- 当月新增文件清单（或链接到数据文件）
- 数据来源与方法

## 参考文献 / 变更记录
```

## 后处理（强制）

1. **登记产物**：用 `kb-log-append.py` 追加报告摘要到全局 `knowledge/log.md`（2026-08-19 起 weekly-reports 不再维护独立 index/log）
3. **交叉链接**：关联当月周报（`01_weekly/`）、专项报告（`07_kb_stat/`）
4. **图表归档**：PNG 存 `02_monthly/assets/`（若有）
5. **git 自动提交**（AI 身份 + `[AI]` 前缀）：
   ```bash
   python3 scripts/git/git-auto-commit.py -t knowledge -s weekly-reports \
       -m "月报: <YYYY-MM 知识库月度报告>" -n "覆盖 5 维度; 提交/文件/质量数据"
   ```

## 图表生成要点

- 用 matplotlib（中文字体 SimHei/Noto Sans CJK），PNG 300dpi
- 数据缺失时标注"无历史数据，待积累"，不编造
- 图表作为 §1.3 的补充，报告正文以表格为主

## 注意事项

1. **不编造数据**：所有数字来自数据文件/git/检查脚本实测；无法获取的标注缺口
2. **洞察必须有来源**：每条洞察附文件路径或日期
3. **待办不凭空捏造**：来自 memory/周报/专项报告的实际记录；新增建议标注"建议"
4. **月度 vs 周报边界**：月度聚合不重复周报细节，聚焦趋势/对比/质量/治理
5. 报告生成后运行 `check_md_format.py` / `check_tech_doc_quality.py` 自检
