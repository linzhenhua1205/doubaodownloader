---
name: weekly-report-generator
description: "Generate knowledge base daily reports (v4.2 增强版) and weekly reports summarizing activities, extracting insights, and identifying action items for server R&D. Use when: (1) user asks to generate 知识库每日调研日报 / 生成日报 / 日报, (2) user asks to generate/create/make a weekly report or says \"生成周报\", (3) it's time for the daily 08:10 report or the weekly Sunday report. Daily v4.2 workflow consumes 6 scripts (kb-daily-data-gather.sh, kb-daily-git-analysis.py, kb-daily-memory-analysis.py, kb-daily-survey-coverage.py, kb-daily-effort-analysis.py, kb-token-context-stats.py) and writes 00_daily/{日期}.md with Top5 + coverage matrix + Git/memory analysis + 产出四分类(调研输出/系统监控/深度专题/数据源处理) + AI 健康度(目标≥90%) + 用户干预评价 + 内容质量三维评价 + 上下文 Token 监控(system/skills/file 三类 + 30K/80K 告警) modules."
---

# Report Generator（日报 v4.2 增强版 + 周报）

## Overview

Generate daily and weekly knowledge base reports summarizing all tracked activities, extracting key insights, and identifying action items. Reports saved to `knowledge/weekly-reports/`（2026-08-19 起**不再维护分布式 index.md/log.md**：全库统一根 knowledge/index.md + knowledge/log.md，报告自身追加 log 条目用 kb-log-append.py）。

## ⏱ 日报时间窗口与命名（v4 增强版）

```
时间窗口: [(TODAY-1) 08:00 → TODAY 08:10]
```

- **TODAY** = 执行日报的日期（窗口结束日）
- **文件名 = TODAY（窗口结束日）**——在 08-13 早上执行 → 生成 `00_daily/2026-08-13.md`，窗口 = 08-12 08:00 ~ 08-13 08:10。命名不是覆盖日期的前一日
- **日期判定**：若 `{TODAY}.md` 已存在（当天已生成过），以窗口结束日为准确认本次窗口，**切勿覆盖已有文件**；文件名一律 = 窗口结束日

### 各数据源在窗口中的语义

| 数据源 | 窗口语义 | 过滤规则 |
|:-------|:---------|:---------|
| **调研跟踪文件** | 扫描 `01_survey/` 下名称匹配 TODAY* 和 (TODAY-1)* 的文件（覆盖 00:00~08:10） | 文件名匹配 `YYYY-MM-DD*.md` |
| **深度分析文档** | git log 时间窗口内的 knowledge/ 变更 | 仅 `knowledge/`，排除 `01_survey/`、`weekly-reports/`，过滤 >100行；剔除 index/log 治理文件后为实质业务数 |
| **Git 提交** | git log 时间窗口内全仓变更 | 以 `kb-daily-git-analysis.py` 口径为准（含 scripts/skills，非 knowledge/ 子集） |
| **Memory 操作要点** | 消费 `kb-daily-memory-analysis.py` 输出 | 提取 ✅ ✔️ → ## 等标记行 |
| **调研覆盖** | 消费 `kb-daily-survey-coverage.py` 输出 | 覆盖矩阵 N/38 领域 |
| **产出结构/AI健康/干预/质量** | 消费 `kb-daily-effort-analysis.py` 输出 | 产出四分类 / AI 比重(目标≥90%) / 用户干预五维 / 内容质量三维 |
| **原始素材证据** | 扫描 `tmp/raw/{窗口日}/`（web-access 落盘约定） | 关键动态的溯源文件路径（三级证据链：日报 → 01_survey → tmp/raw） |

## Data Gathering Prerequisite（日报/周报共用）

**所有日报/周报生成之前，必须先运行数据采集脚本**。日报模式必须跑满六个脚本：

```bash
# ─── 六个脚本全部必须先跑（并行执行，输出在 tmp/ 下供消费）───
bash ~/cow/scripts/kb-daily-data-gather.sh            # 总采集器（内部调用 files + survey-scan，产出 tmp/kb-daily-data-{日期}/）
python3 ~/cow/scripts/kb-daily-git-analysis.py        # Git 综合分析 → tmp/kb-daily-git-analysis-{日期}.md
python3 ~/cow/scripts/kb-daily-effort-analysis.py     # 产出结构/AI健康度/干预/质量（v4 新增）→ tmp/kb-daily-effort-analysis-{日期}.md
python3 ~/cow/scripts/kb-daily-memory-analysis.py     # 记忆/会话分析 → tmp/kb-daily-memory-analysis-{日期}.md
python3 ~/cow/scripts/kb-daily-survey-coverage.py     # 调研覆盖检查 → tmp/kb-daily-survey-coverage-{日期}.md
python3 ~/cow/scripts/kb-token-context-stats.py --date {TODAY}  # 上下文 Token 监控（v4.2 新增）→ CSV + tmp/kb-token-context-trend-{TODAY}.md + stdout 汇总
```

**数据口径（重要，勿混用）**:
- **Git 提交数以 `kb-daily-git-analysis.py` 为准**（全仓统计，含 scripts/skills）；data-gather 的 `00-commits.txt` 仅为 knowledge/ 子集（排除 01_survey/）。两者数字不同是正常的，日报以 git-analysis 口径为准
- 深度文档数 = git log 已提交 + git status 未提交新文件；剔除 index/log 等治理文件后为实质业务数（例：15 个文档 − 2 个治理 = 实质 13）
- 调研跟踪文件数、覆盖领域数以 `kb-daily-survey-coverage.py` 为准（N/38）

**数据质量校验（必做，勿跳过）**:
- 整套管线基于 git log，**检测不到尚未 commit 的工作区文件**。若脚本结果为空/为 0，而定时调研任务恰在窗口内运行过（产出未提交），先交叉核对再下结论：
  ```bash
  git status --porcelain -- knowledge/ | head -50   # 未提交变更
  # 按文件名匹配窗口日期（覆盖 00:00~08:10 的未提交产出）：
  ls knowledge/01_survey/*/{TODAY}*.md {(TODAY-1)}*.md 2>/dev/null
  ```
- **深度文档未提交盲区**（08-06 教训）：git log 只列已 commit 的深度文档。写日报**之前**用 git status 补查深度文档清单完整性，避免写完再补、还要二次同步统计数字：
  ```bash
  git status --porcelain -- knowledge/ | grep -v '^ M' | grep '\.md$'   # 新增/未跟踪文档
  # 重点甄别窗口日期命名的深度文档（YYYY-MM-DD-*.md，排除 01_survey/ 与 weekly-reports/）
  ```
- 完整性检查须兼容 `YYYY-MM-DD-后缀.md` 文件名（如 `08_incr_ir/2026-07-21-xxx.md`），不能只匹配纯日期格式
- `knowledge/log.md` 可能已被其他任务并发追加：用 `kb-log-append.py`（自动备份+查重）追加，勿手工覆盖（2026-08-19 起 weekly-reports 不再有独立 log.md）
- 脚本失败时手动回退：用 git log + memory 文件手动补齐，并在日报中标注「脚本降级」

---

## Daily Report Workflow（日报生成，v4 增强版）

### Step 1: 运行五个数据采集脚本

按 Data Gathering Prerequisite 运行五个脚本（全部必须先跑，确认无降级后再进入下一步）。

### Step 2: 消费脚本输出，确认口径

读取五个脚本输出文件，确认数字口径（git-analysis 与 data-gather 提交数不一致属正常，以 git-analysis 为准；effort-analysis 的产出分类/AI 比重/干预/质量为新口径，独立于 git-analysis）。

### Step 3: 分类阅读关键内容（省 token）

- **调研文件**：read 前 30 行提取核心信号；批量分组读（每批 ~14 个）
- **深度文档**：读标题层级了解主题，不读全文
- **Git/记忆/覆盖三模块**：直接消费脚本输出的结构化统计，AI 只做精炼与判断，**不得编造数字**

### Step 4: 生成日报并写入 knowledge/weekly-reports/00_daily/{TODAY}.md

规模可放宽至 ~2000 行（内容充分优先，不为了短而短）。结构：

```
# 📅 知识库日报 — {TODAY}

> **统计窗口**: {TODAY-1} 08:00 ~ {TODAY} 08:10
> **跟踪文件**: N 个 | **深度文档**: N 个 | **Git 提交**: N 个 | **覆盖领域**: N/38

---

## 🔥 今日核心信号 Top 5
（每条标注模块与重要性 🔥，如 🔥🔥🔥）

---

## 📡 调研跟踪摘要（全面覆盖 + 洞察建议）

按「调研覆盖矩阵」组织——每个有产出的领域一个小节，先列关键动态，末尾必须给出「🔍 洞察建议」（1-3 条，指向用户 P0 关注点：超节点/互联/存储/RAS/供电散热/知识库建设，或指向后续行动）。空白领域在矩阵中标注；若为重要领域（如服务器硬件/标准财经媒体）判断是否补采或说明原因。

领域节示例：
### 🖥️ 服务器硬件 📎 knowledge/01_survey/hardware/2026-08-14.md
- 关键动态（bullet，来源标注 URL；**已落盘的关键素材追加 `📎 raw: tmp/raw/2026-08-14/<domain>-<slug>.md`**）
- 🔍 洞察建议：...（如与已有专题的关联、对产品决策的含义、建议后续深挖点）

> **原始文件路径（溯源证据）**：每个有产出领域节必须标注其调研文件路径（📎 knowledge/01_survey/...）；关键动态的原始抓取素材（tmp/raw/）一并标注——证据链：日报条目 → 调研文件 → 原始素材 →（web-access-log.csv URL 台账）。无法定位原始素材时标注「无 raw 落盘」而非省略。

覆盖矩阵（消费 kb-daily-survey-coverage.py 输出，保留空白领域清单）。

---

## 📐 深度文档分析
| 文档 | 路径 | 核心内容 |（消费 git 分析 + files 脚本）

---

## 📊 Git 提交综合分析（消费 kb-daily-git-analysis.py，AI 精炼）
- 总览：总提交 / AI 提交（[AI] 前缀）/ 人工提交 / 变更文件（业务 vs 治理）/ 插入删除行
- AI 提交特征（feat×N/chore×N...，日报型批量产出）与人工提交特征（ingest/fix/chore，归档修复为主，列 3-5 条示例）
- 目录热点 Top 5（02_rd/01_survey/07_industry-research 等，解释热点含义）
- 昨日修改热点：指出 3-5 个最活跃文件/目录，说明为什么热
- 修改特征：提交规模分布、治理 vs 业务占比、AI 占比健康度（>90% 连续高位 → 建议周报新增「AI 深度文档抽检」维度制衡）
- 识别可改进点：采纳脚本建议 + AI 判断（如不规范提交信息/业务型超大提交/无正文比例/目录集中度）

## 🧠 记忆与会话综合分析（消费 kb-daily-memory-analysis.py，AI 精炼）
- 昨日关注技术要点：按主题聚合为 3-6 条（从脚本候选提炼，标注领域）
- 可 Skills 化 / Scripts 化点：标注优先级（P0 高频重复/P1 周期任务/P2 低频），说明自动化方式
- 约束需加固点：标注类型（流程/格式/安全/数据），说明加固方式（脚本门禁/检查器/规范），引用昨日教训

---

## 📈 产出结构与 AI 健康度（v4 新增，消费 kb-daily-effort-analysis.py）
- **产出四分类**（消费脚本表格）：每日调研输出 / 深度分析专题 / 数据源处理 / 系统监控与管理——各列文件数/提交数/行数/占比，解读当日产出重心（专题化 vs 分散）
- **AI 比重**：按提交 + 按文件双口径；健康口径（用户定义 2026-08-14）：**AI 自动提交占比目标 ≥90%**（AI 提交 = [AI] 前缀 + 定时/归档管道提交）
  - 🟢 ≥90% 目标达成；🟡 80-90% 接近；🔴 <80% 提示 AI 未充分接管例行产出，列出人工代劳项
- 超大提交（>300 文件或 >10k 行）已由脚本排除并标注口径，AI 精炼时不再重复统计

## 🧑💻 用户干预评价（v4 新增，消费 kb-daily-effort-analysis.py）
- 五维干预表：① 问题输入（会话数/消息量）② 人工提交 ③ 数据源输入（import/ 素材）④ 工具维护-用户发起 ⑤ 工具维护-AI 自主
- **干预结构**：输入型（问题+素材，健康）vs 代劳型（人工提交+维护，应趋近 0）——健康形态=高自动化率且干预集中于输入型
- 若 AI 比重 <90%：在日报中给出「待 AI 接管项」清单（哪些例行产出仍由人工完成）

## 📐 内容质量评价（v4 新增，消费 kb-daily-effort-analysis.py）
- 三维：① 内容长度（中位/均值/≥10KB 深度占比/≤1KB 碎片）② 单文件修订次数（打磨型 2-10 次 vs churn>10 次；账簿型 index/log/README 高频属正常不计 churn）③ 同目录聚集度（Top1 占比 + 归一化熵：专题化聚集=体系化 ✅）
- 综合分 0-100（0.4×深度 + 0.3×打磨 + 0.3×体系化）；解读质量信号并指向改进（如碎片化/高 churn/分散产出）

## 🔤 上下文 Token 监控（v4.2 新增，消费 kb-token-context-stats.py 输出）
- 三类统计表（消费脚本 stdout）：🧠 系统（AGENT/USER/RULE/MEMORY 4 文件 + 固定框架估算）/ 🛠️ Skills（description 注入 + 文件全量）/ 📄 文件（当日 memory + index+README + knowledge 全量参考）
- **趋势曲线**：引用脚本输出的 14 天 ASCII 趋势（系统 token / skills desc 注入 / skills 文件全量 三线），说明相对变化（如 MEMORY.md 增删、skills 增删对上下文的影响）
- **告警规则**：系统总量 或 skills 注入量 ≥ 30K tokens → 🟡 WARN；≥ 80K tokens → 🔴 CRIT。出现告警时给出削减建议（如 MEMORY.md 精简/技能 description 裁剪/skills 拆分降载），并指向 07_kb_stat/00.token-consumption-analysis/ 的 CSV 数据
- 数据口径：启发式估算（CJK×0.7 + 非CJK/4，偏差±20%，相对趋势可信），精确值需真实 tokenizer；CSV 落盘路径 = knowledge/weekly-reports/07_kb_stat/00.token-consumption-analysis/token-context-daily.csv

---

## 📊 统计概要
| 指标 | 数值 |
（调研跟踪文件/深度文档/覆盖领域/空白领域/Git 提交/AI 提交/人工提交/变更行数/候选条目数/AI 比重/自动化率/质量综合分）
```

### Step 5: 更新索引与日志

```bash
# 1. 日报文件写入 knowledge/weekly-reports/00_daily/{日期}.md（只写报告文件，不写任何 index/log）
# 2. 用 kb-log-append.py 追加一条摘要到全局 knowledge/log.md（深度产出登记）
```

> 2026-08-19 起 weekly-reports 不再维护分布式 index.md/log.md（已移除）：全库统一根 index（kb-global-index.py 批量刷新）+ 根 log（kb-log-append.py 追加）。

### Step 6: git 提交

只提交日报三件套（日报 + index + log），保持与历史一致的提交模式。可用：

```bash
python3 scripts/git/git-auto-commit.py -t knowledge -s weekly-reports \
    -m "日报: <TODAY> 知识库日报" -n "P1 技术要点 + P2 深度文档 + P3 工程汇总"
```

或手动 git 提交（保持 message 规范，AI 提交加 `[AI]` 前缀）。

### 注意事项（日报）

- 当日无任何文件变更 → 输出「无变更，跳过日报」
- 数据采集脚本失败 → 手动回退（git log + memory 补齐）并在日报标注「脚本降级」
- 不消耗过多 token 读每个文件全文——用 head 或 offset/limit 读取关键部分
- Git/记忆/覆盖三模块必须以脚本输出为事实基础，AI 只做精炼与判断，不得编造数字
- 日报质量自检：数字有出处（脚本或文件）、洞察指向行动、改进点可执行

---

## 周报生成前置流程（Pre-flight，强制）

> 周报更新前**必须先完成以下四步**（缺失则周报数据不完整）。2026-08-14 起固化。

### Pre-0: 本地 commit + push

1. `git status --porcelain` 检查未提交/未跟踪变更
2. 有未提交 → commit（`[AI]` 前缀 + body 清单），与历史模式一致
3. `python3 scripts/git/git-push-robust.py --async` 后台异步触发一次 push（0.1s 返回，不等待、不重试、不报告结果；日志见 `tmp/git-push-async.log`）
4. 确认工作区干净后再进入下一项

### Pre-1: 06_memory 材料更新

- 基于本周 `memory/YYYY-MM-DD.md` 生成/更新 `knowledge/weekly-reports/06_memory/` 下的 memory 洞察材料（周度或增量）
- 提炼维度：核心关注主题、阶段演变信号、判断得失、可 Skills/脚本化点、约束加固点
- 产物登记：用 kb-log-append.py 追加摘要到全局 `knowledge/log.md`（06_memory 不再维护独立 index/log）

### Pre-2: 周意图分析更新（06_conversation）

- 运行一键管道（导出会话 → CSV → 报告骨架）：
  ```bash
  bash scripts/intent_analysis/run_all.sh --since <本周一>
  ```
- Agent 补 LLM 深度解析五块：意图分布解读 / 决策模式洞察 / 技术关注演化 / 对话主线提炼 / 优化建议增强
- 输出 `knowledge/weekly-reports/07_kb_stat/06_conversation/conversation-intent-analysis-{TODAY}.md`，产物用 kb-log-append.py 登记到全局 log.md（不写子目录 index）

### Pre-3: 03_skills_scripts 周报告确认

- 检查 `knowledge/weekly-reports/07_kb_stat/03_skills_scripts/` 是否存在本周 `YYYY-WNN-skills-scripts-quality-report.md`
- 没有 → **补充触发**：按 WNN-1 模板手动生成（①注册检查 `check-skills-registration.py` → ②本周 Skills 变更 git log → ③本周 Scripts 变更 → ④无用文件排查 → ⑤memory 痛点分析 → ⑥映射更新 → ⑦优化建议 → ⑧自检清单）
- 已有 → 读取确认内容完整、数字口径正确
- 完成后用 kb-log-append.py 登记产物摘要到全局 `knowledge/log.md`（07_kb_stat 不再维护独立 index/log）

---

## Weekly Report Workflow（周报生成）

### Step 1: Run data gathering script

先运行数据采集脚本获取整周的变更数据基底：

```bash
# 对上周的每一天运行数据采集
for d in $(seq 0 6); do
  date_str=$(date -d "last monday -${d} day" +%Y-%m-%d)
  ./scripts/kb-daily-data-gather.sh "$date_str"
done
```

### Step 2: Gather supplementary data sources

Read the following files:

```bash
# Read each day's memory file for last week
# Monday through Sunday, e.g. 2026-06-22.md through 2026-06-28.md
```

Also check:
- `MEMORY.md` — long-term summary and key takeaways
- `knowledge/index.md` — default knowledge base index (full file list + summaries) to count new/modified files; `knowledge/README.md` — curated entries (manual)
- `knowledge/log.md` — operation logs
- Knowledge files in `knowledge/01_survey/` — daily tracking files for the week

### Step 3: Extract structured information

For each memory file, extract:

1. **Key Activities** — major research tasks, document creations, knowledge updates
2. **Structural Changes** — directory reorganization, index rebuilding, path migrations
3. **Attention Points** — issues found, warnings, data corrections, broken systems
4. **Server R&D Value** — for each industry research item, distill what matters for server product R&D

### Step 4: Compile report sections

The report should follow this structure:

```
# 本周知识库周报（2026-WXX: YYYY-MM-DD ~ YYYY-MM-DD）

总览: 一句话概述本周活动规模

---

## 一、核心活动回顾

主要活动分组概述，按类型组织：
- 知识库结构变更
- 深度文档创建/更新
- 日常跟踪调研

## 二、行业与技术跟踪概述

对调研报告，提供行业信息概述，重点提炼对服务器研发有价值的点。
按领域分类，每个领域下只列核心发现和服务器研发价值。

### 2.1 [领域1]
| 方向 | 核心发现 | 对服务器研发价值 |
|:-----|:---------|:----------------|

### 2.2 [领域2]
...

## 三、结构变更与技能约束

知识库结构调整描述：
- 目录重组
- 索引重建
- 技能更新
- 约束提醒（skills和memory中对应的约束点）

## 四、重点关注与待办事务

提炼本周需要关注的问题和下周待办。

| # | 类型 | 事项 | 关联 | 优先级 |
|:-:|:----|:-----|:-----|:------|

## 五、服务器研发价值总结

一句话总结本周对服务器研发最有价值的 3-5 个信号。

---

统计：文件数、行数、覆盖方向数
```

### Step 5: Format constraints

- Code blocks must use pure ASCII (no Chinese characters inside code blocks)
- Add cross-links to relevant knowledge base files
- For quantified data, ensure sources are traceable
- Use tables for structured comparisons
- Save to `knowledge/weekly-reports/2026-WXX.md`

### Step 6: Save and update index

```bash
# Save report
# Update knowledge/weekly-reports/ index if exists
# Update knowledge/log.md
```

## Output

Report saved to `knowledge/weekly-reports/2026-WXX.md` following the structure above.

---

## Changelog

| 日期 | 版本 | 变更 |
|:-----|:-----|:-----|
| 2026-08-14 | v4.2 | 日报新增「🔤 上下文 Token 监控」模块 + 第 6 脚本 `kb-token-context-stats.py`：三类统计（系统 AGENT/USER/RULE/MEMORY+固定框架 / Skills desc 注入+文件全量 / 文件 当日 memory+index+knowledge 全量参考），CSV 落盘 `07_kb_stat/00.token-consumption-analysis/token-context-daily.csv`（幂等按日追加），14 天 ASCII 趋势三线，30K/80K 两级告警；已并入 `kb-daily-data-gather.sh` Step 6b 一体运行 |
| 2026-08-14 | v4.1 | 日报「调研跟踪摘要」增加**原始文件路径（溯源证据）**：领域节标注调研文件路径（📎 knowledge/01_survey/...），关键动态带 tmp/raw 原始素材路径，形成三级证据链（日报→调研文件→原始素材→URL台账）；新增「原始素材证据」数据源（web-access 落盘约定）；配套：source-access-lookup.py 访问方式查表（token 优先） |
| 2026-08-14 | v4 | 新增第 5 脚本 `kb-daily-effort-analysis.py`：产出四分类（调研输出/系统监控/深度专题/数据源处理）、AI 比重健康口径（目标≥90%，AI 提交=[AI]前缀+定时/归档管道提交）、用户干预五维评价（问题输入/人工提交/数据源输入/工具维护）、内容质量三维（长度/修订次数/聚集度）；日报新增 📈🧑💻📐 三模块；超大提交（>300 文件或 >10k 行）单独口径排除 |
| 2026-08-07 | v3 | 四脚本管线（data-gather/git-analysis/memory-analysis/survey-coverage）；Top5+覆盖矩阵+Git/记忆模块 |
| 2026-07-29 | v2 | 时间窗口 [上一日 08:00 → 今日 08:10]；调研覆盖矩阵 N/38 |
| 2026-07-25 | v1 | 日报基础版 |
