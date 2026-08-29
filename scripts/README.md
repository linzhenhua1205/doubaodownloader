# 🛠️ Scripts 使用手册

> 详细 CLI 使用说明、参数释义、场景示例。
>
> 最后更新: 2026-07-24

---

## 📑 目录

- [统一入口工具](#-统一入口工具)
- [检查类（check/）](#-检查类check)
- [工具类（tools/）](#-工具类tools)
- [导入管线（autokb/）](#-导入管线autokb)
- [Git 类（git/）](#-git类git)
- [根级其他脚本](#-根级其他脚本)

---

## 🔗 统一入口工具

### `constraint-check.py` — 约束合规检查器（Lint）

基于 SR-003 约束注册表（01001-12305）的统一合规检查。11 类别覆盖安全红线、文件操作、格式、路径、代码、质量等。

```bash
# 列出所有检查类别
python3 scripts/constraint-check.py --list-categories

# 全量检查（摘要模式）
python3 scripts/constraint-check.py --category all --summary

# 默认可选：safety + format + index-log + code
python3 scripts/constraint-check.py --category default

# 单类别检查
python3 scripts/constraint-check.py --category safety
python3 scripts/constraint-check.py --category paths
python3 scripts/constraint-check.py --category code

# 多类别组合
python3 scripts/constraint-check.py --category safety,format,code

# 指定检查目标
python3 scripts/constraint-check.py --category format --target knowledge/02_rd/my-doc.md

# 尝试自动修复
python3 scripts/constraint-check.py --category format --target file.md --fix

# JSON 输出（用于脚本集成）
python3 scripts/constraint-check.py --category all --json
```

**支持类别**:

| 类别 | 约束 | 说明 |
|:-----|:-----|:------|
| `safety` | 01001-01010 | 安全红线：rm 禁令、密钥泄露、bak 引用、素材批判使用 |
| `file-ops` | 02101-02108 | 文件操作：命名规范、目录深度、index+log 同步 |
| `paths` | 03101-03108 | 路径映射：路径注册表合规、Skills 硬编码、过时路径 |
| `format` | 04101-04106 | 知识库格式：TOC/Changelog/参考文件/概要/关键词 |
| `index-log` | 05101-05103 | 索引/日志：模块独立维护、目录 scope 合规 |
| `code` | 06101-06105 | 代码/脚本：argparse CLI/命名前缀/pathlib/路径变量 |
| `quality` | 07201-07206 | 质量标准：量化四要素/来源标注/MECE/交叉验证 |
| `skills` | 08201-08205 | Skills 行为：自动记录/自检交付/路径决策树 |
| `kb-write` | 10301-10305 | 知识库写入：存储频率判定/Strategy 合规 |
| `review` | 11301-11305 | 审查验证：五层审查/自检局限/证据闸门 |
| `scheduler` | 12301-12305 | 定时任务：Fail-Fast/来源分级/Token 预算 |
| `all` | 01001-12305 | 全部 11 类别 |

---

## ✅ 检查类（check/）

### `check/link-validator.py` — 链接有效性扫描

扫描 `knowledge/` 中全部 Markdown 链接，按 5 种失效类型分类（DEPTH/MOVED/DIR_RENAME/EXTERNAL/MISSING）。

```bash
# 全量扫描
python3 scripts/check/link-validator.py

# 指定模块
python3 scripts/check/link-validator.py --module 02_rd/03_hardware

# 单文件
python3 scripts/check/link-validator.py --file knowledge/02_rd/index.md

# 附带修复建议
python3 scripts/check/link-validator.py --module 02_rd --report --suggest

# 分类输出
python3 scripts/check/link-validator.py --module 02_rd --classify

# JSON 输出
python3 scripts/check/link-validator.py --module 02_rd --json
```

### `check/link-ref-audit.py` — 引用即契约检测（audit-002 落地）

验证"文档引用的脚本是否真实存在且可无歧义解析"——将文档-脚本引用固化为契约，消灭三类断裂：真实断裂/路径歧义/设计承诺。已接入 system-guardian Guard D。

```bash
# 全量扫描（skills + spec）
python3 scripts/check/link-ref-audit.py

# 仅 skills / 仅 spec
python3 scripts/check/link-ref-audit.py --scope skills
python3 scripts/check/link-ref-audit.py --scope spec

# 列出全部断裂明细
python3 scripts/check/link-ref-audit.py --list

# JSON 输出（供 CI/guardian 解析，退出码 0=无断裂）
python3 scripts/check/link-ref-audit.py --json

# strict 模式（设计承诺/教学引用也计入断裂，用于完整审查）
python3 scripts/check/link-ref-audit.py --strict
```

**配套文件**: `scripts/check/design-promises.json` — 设计承诺豁免清单（已降级/教学/规划的引用，审计时豁免）。

### `check/link-fixer.py` — 链接智能修复

配合 link-validator 进行规则驱动修复。

```bash
# 交互式修复
python3 scripts/check/link-fixer.py

# 指定模块修复
python3 scripts/check/link-fixer.py --module 06_superpod

# 预览修复方案（不修改）
python3 scripts/check/link-fixer.py --dry-run

# 自动执行安全修复
python3 scripts/check/link-fixer.py --auto

# 为缺失文件创建 stub
python3 scripts/check/link-fixer.py --stub

# 生成修复计划报告
python3 scripts/check/link-fixer.py --report
```

### `check/link-augmenter.py` — 裸文件引用链接化

检测文件中的裸文件名引用（如 `xxx.md` 而非 `[xxx](xxx.md)`），自动添加 Markdown 链接。

```bash
# 预览模式
python3 scripts/check/link-augmenter.py --dry-run

# 执行修复
python3 scripts/check/link-augmenter.py --fix

# 指定模块
python3 scripts/check/link-augmenter.py --module 02_rd --fix

# 仅按文件名标题匹配（更精确）
python3 scripts/check/link-augmenter.py --titles-only --fix

# 最小匹配长度（默认 6）
python3 scripts/check/link-augmenter.py --min-len 10 --fix
```

### `check/kb-health.py` — 知识库健康度 6 维扫描

扫描 `knowledge/` 的综合健康检查：日志顺序(A)/链接有效性(B)/表格格式(C)/文件位置(D)/Markdown 格式(E)。

```bash
# 全量检查
python3 scripts/check/kb-health.py

# 指定路径
python3 scripts/check/kb-health.py --path knowledge/03_AI

# 仅特定维度
python3 scripts/check/kb-health.py --categories B,C

# 详细输出（含通过项）
python3 scripts/check/kb-health.py --verbose

# 紧凑报告
python3 scripts/check/kb-health.py --summary

# 自动修复 log.md 排序
python3 scripts/check/kb-health.py --fix-log

# JSON 输出
python3 scripts/check/kb-health.py --json
```

### `check/md-format.py` — Markdown 格式规范检查

检查方框字符、块填充、中文混排等格式问题。三个严重级别：R1(严重)/R2(中等)/R3(轻微)。

```bash
# 检查文件
python3 scripts/check/md-format.py knowledge/02_rd/report.md

# 自动修复 R1 级别问题
python3 scripts/check/md-format.py knowledge/02_rd/report.md --fix

# 递归扫描目录
python3 scripts/check/md-format.py knowledge/ --recursive

# 指定最低报告级别
python3 scripts/check/md-format.py knowledge/ --recursive --level R2
```

### `check/knowledge-normalizer.py` — 一站式知识库规范化

6 阶段流水线：index → log → links → augment → format → scope → content。可单独运行各阶段。

```bash
# 预览（dry-run）全部阶段
python3 scripts/check/knowledge-normalizer.py

# 执行修复
python3 scripts/check/knowledge-normalizer.py --fix

# 仅处理特定模块
python3 scripts/check/knowledge-normalizer.py --module 02_rd

# 仅运行特定阶段
python3 scripts/check/knowledge-normalizer.py --only links,augment

# 跳过特定阶段
python3 scripts/check/knowledge-normalizer.py --skip format
```

### `check/format-validator.py` — 文件类型格式合规校验

按 T1-T7 七种文件类型（index/log/跟踪/深度/框架/周报/来源）逐类型校验。

```bash
# 检查文件
python3 scripts/check/format-validator.py knowledge/02_rd/report.md

# JSON 输出
python3 scripts/check/format-validator.py path/to/file.md --json

# 检查整个模块
python3 scripts/check/format-validator.py --module 02_rd

# 全库扫描汇总
python3 scripts/check/format-validator.py --all --summary

# 修复模式
python3 scripts/check/format-validator.py path/to/file.md --fix
```

### `check/content-format-normalizer.py` — 内容文件五要素合规

检查/修复知识文档的五大要素：**概要**(Summary)、**关键词**(Keywords)、**目录**(TOC)、**参考文件**(References)、**Changelog**。

```bash
# 检查文件
python3 scripts/check/content-format-normalizer.py knowledge/02_rd/report.md --check

# 修复文件
python3 scripts/check/content-format-normalizer.py knowledge/02_rd/report.md --fix

# 预览修复
python3 scripts/check/content-format-normalizer.py knowledge/02_rd/report.md --dry-run

# 全库处理
python3 scripts/check/content-format-normalizer.py knowledge/ --all --fix

# 指定模块
python3 scripts/check/content-format-normalizer.py knowledge/ --module 02_rd --fix
```

### `check/strategy-compliance.py` — 知识库策略合规校验

校验文件是否遵循其位置应有的 Strategy（A/B/C/D/E）要求。含放置决策树合规检查。

```bash
# 检查文件
python3 scripts/check/strategy-compliance.py knowledge/02_rd/report.md

# JSON 输出
python3 scripts/check/strategy-compliance.py knowledge/02_rd/report.md --json

# 修复模式
python3 scripts/check/strategy-compliance.py knowledge/02_rd/report.md --fix

# 全库扫描
python3 scripts/check/strategy-compliance.py --all

# 汇总报告
python3 scripts/check/strategy-compliance.py --all --summary

# 指定模块
python3 scripts/check/strategy-compliance.py --module 02_rd
```

### `check/doc-quality.py` — 技术文档质量自检

对照 deep-tech-writer 质量标准逐项检查：量化四要素、ASCII 代码块、来源标注、交叉引用。

```bash
# 检查文档
python3 scripts/check/doc-quality.py knowledge/02_rd/report.md

# 自动修复部分问题
python3 scripts/check/doc-quality.py knowledge/02_rd/report.md --fix

# 仅输出报告（不检查）
python3 scripts/check/doc-quality.py knowledge/02_rd/report.md --report
```

### `check/quantitative-check.py` — 量化数据标注合规检查 ✅ (sr-006 D-03)

扫描文档中的量化断言，检测：裸数字无单位、断言缺来源、比较级缺基线、百分比缺上下文。

```bash
# 检查单个文件
python3 scripts/check/quantitative-check.py check --file knowledge/07_industry-research/report.md

# 检查整个目录
python3 scripts/check/quantitative-check.py check --dir knowledge/07_industry-research/

# 全量扫描（限前 50 个文件）
python3 scripts/check/quantitative-check.py check --all --max-files 50

# 严格模式（仅报告严重违规）
python3 scripts/check/quantitative-check.py check --file report.md --strict
```

### `check/doc-review.py` — 文档三层结构化审查

自动化结构审查：结构完整性(🔴) → 逻辑谬误(🟡) → 来源可追溯(🔴)。覆盖 13 条逻辑谬误。

```bash
# 审查文件
python3 scripts/check/doc-review.py knowledge/02_rd/report.md

# 指定输出报告路径
python3 scripts/check/doc-review.py knowledge/02_rd/report.md --output review-report.md

# 仅终端输出报告
python3 scripts/check/doc-review.py knowledge/02_rd/report.md --report-only

# 自动修复
python3 scripts/check/doc-review.py knowledge/02_rd/report.md --fix
```

### `check/analyze-index-coverage.py` — index.md 覆盖率分析

分析 `index.md` 中的文件索引是否完整，可自动补全缺失条目。

```bash
# 分析单个模块
python3 scripts/check/analyze-index-coverage.py knowledge/02_rd

# 生成缺失条目（预览）
python3 scripts/check/analyze-index-coverage.py knowledge/02_rd --generate-entries

# 自动补全
python3 scripts/check/analyze-index-coverage.py knowledge/02_rd --fix

# 全库扫描
python3 scripts/check/analyze-index-coverage.py --all

# 全库扫描 + 修复
python3 scripts/check/analyze-index-coverage.py --all --fix

# JSON 输出
python3 scripts/check/analyze-index-coverage.py --all --json
```

### `check/index-log-normalizer.py` — index/log 范围规范化

确保 index.md 只描述本目录直接文件，log.md 只记录本目录变更。支持创建缺失文件。

```bash
# 检查单目录
python3 scripts/check/index-log-normalizer.py knowledge/02_rd --check

# 全库检查
python3 scripts/check/index-log-normalizer.py --all --check

# 修复
python3 scripts/check/index-log-normalizer.py --all --fix

# 仅初始化缺失的 index/log
python3 scripts/check/index-log-normalizer.py --all --init

# 预览修复
python3 scripts/check/index-log-normalizer.py --all --dry-run
```

### `check/reformat-log.py` — log.md 格式统一格式化

将 log.md 统一为标准 changelog 格式（倒序表格）。支持多种源格式。

```bash
# 格式化单文件
python3 scripts/check/reformat-log.py knowledge/02_rd/log.md

# 全库格式化
python3 scripts/check/reformat-log.py --all

# 预览
python3 scripts/check/reformat-log.py knowledge/02_rd/log.md --dry-run

# 仅检查格式问题
python3 scripts/check/reformat-log.py knowledge/02_rd/log.md --verify
```

### `check/relation-integrity.py` — 关系完整性校验

校验 `index.md` 中的关联文件字段（10 种关系类型），校验目标文件存在性、反向链接一致性。

```bash
# 全库扫描
python3 scripts/check/relation-integrity.py

# 指定模块
python3 scripts/check/relation-integrity.py --module 02_rd

# 单文件
python3 scripts/check/relation-integrity.py --file knowledge/02_rd/report.md

# 关系统计
python3 scripts/check/relation-integrity.py --stats

# 关系图谱
python3 scripts/check/relation-integrity.py --graph

# JSON 输出
python3 scripts/check/relation-integrity.py --json
```

### `check/ref-drift-detector.py` — 引用漂移检测

检测 `@ref` 标记的源文件是否已变更（路径漂移/时间漂移/内容漂移）。三级检测。

```bash
# 全库扫描
python3 scripts/check/ref-drift-detector.py

# 指定模块
python3 scripts/check/ref-drift-detector.py --module 02_rd

# 单文件
python3 scripts/check/ref-drift-detector.py --file knowledge/02_rd/report.md

# 仅显示漂移项
python3 scripts/check/ref-drift-detector.py --drifted-only

# 依赖图谱
python3 scripts/check/ref-drift-detector.py --graph

# 保存报告
python3 scripts/check/ref-drift-detector.py --save
```

### `check/directory-architect.py` — 目录架构分析与 index 生成

MECE 分层分析、关联矩阵、阅读路径设计、决策框架索引。可为目录生成结构化 index.md。

```bash
# 分析目录 + 生成 index
python3 scripts/check/directory-architect.py knowledge/02_rd/03_hardware

# 仅分析不生成
python3 scripts/check/directory-architect.py knowledge/02_rd/03_hardware --analyze-only

# JSON 输出
python3 scripts/check/directory-architect.py knowledge/02_rd/03_hardware --json

# 预览不写入
python3 scripts/check/directory-architect.py knowledge/02_rd/03_hardware --dry-run

# 覆盖现有 index.md
python3 scripts/check/directory-architect.py knowledge/02_rd/03_hardware --force

# 指定输出路径
python3 scripts/check/directory-architect.py knowledge/02_rd/03_hardware -o custom-index.md
```

### `check/subdir-nav-fixer.py` — 子目录导航一致性修复

检测子目录是否缺少返回上层的导航链接，自动修复。

```bash
# 预览
python3 scripts/check/subdir-nav-fixer.py knowledge/02_rd --dry-run

# 修复
python3 scripts/check/subdir-nav-fixer.py knowledge/02_rd --fix

# 递归所有子目录
python3 scripts/check/subdir-nav-fixer.py knowledge/02_rd --fix --recursive
```

### `check/roadmap-structure.py` — 服务器知识图谱结构校验

校验服务器设计知识图谱（14 域 × TR1-TR6 矩阵）的结构完整性。

```bash
python3 scripts/check/roadmap-structure.py
```

---

## 🔧 工具类（tools/）

### `tools/session-manager.py` — 通用会话持久化管理器（audit-002 落地）

替代 16 个设计承诺的 session 脚本（init/save/resume/status/list/cancel 及 doc/method/plan/review 变体）。单一入口 + 子命令，会话存 `tmp/sessions/`。

```bash
python3 scripts/tools/session-manager.py init doc:paper1 --context title="..." stage=draft
python3 scripts/tools/session-manager.py save doc:paper1 --context refs="5篇" --note "补充参考文献"
python3 scripts/tools/session-manager.py status doc:paper1
python3 scripts/tools/session-manager.py list
python3 scripts/tools/session-manager.py resume doc:paper1   # 输出恢复上下文
python3 scripts/tools/session-manager.py cancel doc:paper1
```

### `tools/learn-manager.py` — 模式学习暂存管理器（tech-learn 配套）

落地 learn_saver/learn_lister 设计承诺。extract（语义提取）由 LLM 完成，save/list（确定性操作）由脚本完成。模式存 `knowledge/concepts/learned-patterns/`。

```bash
python3 scripts/tools/learn-manager.py save "模式名" --desc "描述" --tag governance
python3 scripts/tools/learn-manager.py list
python3 scripts/tools/learn-manager.py status "模式名"
```

### `tools/depth_score.py` — 内容深度启发式评分器 v1（depth-completer 配套）

落地 depth_score 设计承诺。六维启发式评分（原理/量化/对比/边界/推导/结构），脚本给"线索分"、语义判断留给 LLM/人工。**类型适用性**: 对原理分析/技术调研文档最有效；workflow/审计类 D1 低分属正常特征。

```bash
python3 scripts/tools/depth_score.py <文件.md>            # 六维评分
python3 scripts/tools/depth_score.py <文件.md> --verbose  # 详细诊断
python3 scripts/tools/depth_score.py <目录> --summary     # 目录扫描
```

### `tools/rotate_pdf.py` — PDF 页面旋转工具

落地 skill-creator 建议的 rotate_pdf。依赖 pypdf，纯 Python 无系统依赖。

```bash
python3 scripts/tools/rotate_pdf.py <file.pdf> --angle 90 --pages 1,3-5
python3 scripts/tools/rotate_pdf.py <file.pdf> --inspect  # 仅查看
```

### `tools/html-to-markdown.py` — HTML→Markdown 转换

将 HTML 文件批量转换为 Markdown 格式（注意：当前版本硬编码了旧 Windows 路径，需修改源文件中的输入/输出路径后使用）。

### `tools/check-align.py` — CJK/ASCII 对齐检测

检测 Markdown 文件中中文和 ASCII 混排时的字符对齐宽度问题。

```bash
python3 scripts/tools/check-align.py knowledge/02_rd/report.md
```

### `tools/fix-align.py` — CJK/ASCII 对齐修复

修复中文/ASCII 混排对齐问题（注意：当前版本硬编码了旧 Windows 路径）。

### `tools/chromedriver-setup.py` — ChromeDriver 自动配置

自动检测 Chrome 版本并下载匹配的 ChromeDriver。用于 Selenium 浏览器自动化。

```bash
python3 scripts/tools/chromedriver-setup.py
```

### `tools/extract-chat-content.py` — 聊天内容提取

从 HTML 格式的对话记录中提取有意义的聊天内容。

```bash
python3 scripts/tools/extract-chat-content.py <input.html> <output.md>
```

### `tools/classify-questions.py` — 问题分类

从用户提问汇总文件中筛选和分类问题。

```bash
python3 scripts/tools/classify-questions.py
```

### `tools/extract-user-questions.py` — 用户问题提取

从项目文件中提取用户提出的问题。

```bash
python3 scripts/tools/extract-user-questions.py
```

### `tools/mv-knowledge.py` — 知识库文件迁移 CLI ✅ (sr-006 E-01)

单命令完成文件迁移 + 索引更新 + 日志 + 链接修复。

```bash
# 迁移单个文件
python3 scripts/tools/mv-knowledge.py knowledge/01_survey/old.md knowledge/07_industry-research/

# 批量迁移
python3 scripts/tools/mv-knowledge.py file1.md file2.md knowledge/07_industry-research/

# 预览模式（不实际执行）
python3 scripts/tools/mv-knowledge.py --dry-run src.md dst_dir/
```

### `tools/execution-log.py` — 定时任务执行状态日志 ✅ (sr-006 I-01/I-02/I-06)

记录任务执行状态、零产出检测、重试建议、监控报表。

```bash
# 记录成功执行
python3 scripts/tools/execution-log.py log --task-id ea4db070 --task-name "调研" --status success --lines 42

# 监控全量摘要
python3 scripts/tools/execution-log.py report --summary

# 查看可重试任务
python3 scripts/tools/execution-log.py retry --list
```

### `tools/kb-metadb.py` — 知识库内容元数据库 ✅ (sr-006 B-01)

遍历 knowledge/ 下所有 .md 文件，构建可搜索的元数据 JSON 索引。

```bash
# 全量构建
python3 scripts/tools/kb-metadb.py build

# 增量更新
python3 scripts/tools/kb-metadb.py update

# 关键词查询
python3 scripts/tools/kb-metadb.py query --keyword "CXL" --limit 10

# 目录过滤查询
python3 scripts/tools/kb-metadb.py query --dir "07_industry-research" --keyword "reliability"

# 元数据统计
python3 scripts/tools/kb-metadb.py stats
```

### `tools/errorcodes.py` — 统一错误码标准 ✅ (sr-006 X-11)

定义工程通用退出码（0-99），可被其他脚本 import 使用。

```python
from scripts.tools.errorcodes import EC, exit_with
exit_with(EC.SUCCESS)
exit_with(EC.NO_OUTPUT, "未找到有效信息")
exit_with(EC.FILE_NOT_FOUND, "文件不存在")
```

```bash
# 查看所有错误码
python3 scripts/tools/errorcodes.py
```

---

## 🔍 搜索类（search/）

### `search/unified-search.py` — 统一搜索入口 CLI ✅ (sr-006 A-01/G-01)

统一管理搜索源、关键词预设、增量追踪，生成标准化搜索计划和汇总。

```bash
# 生成超节点领域搜索计划
python3 scripts/search/unified-search.py plan --domain supernode

# 多领域批量计划
python3 scripts/search/unified-search.py plan --dirs "supernode,cluster-training,llm-trends"

# 查看搜索追踪
python3 scripts/search/unified-search.py track

# 查看可用搜索源
python3 scripts/search/unified-search.py sources

# 结果汇总
python3 scripts/search/unified-search.py summary --since 2026-07-25
```

---

## 📊 统计分析类（kb-stat/）

### `kb-stat/conv-log-analyzer.py` — 会话日志通用分析器

将 `conversation-log/db-sessions/` 导出的会话 Markdown 全量解析入 SQLite，产出话题分布/行为分型/处理过程量化/工具模式/迭代纠偏统计与 8 张图表。

```bash
# 全流程（解析+统计+图表）
python3 scripts/kb-stat/conv-log-analyzer.py

# 只解析+统计（纯文本，不生成图表）
python3 scripts/kb-stat/conv-log-analyzer.py --no-charts

# 复用已有 DB 出统计（跳过解析）
python3 scripts/kb-stat/conv-log-analyzer.py --stats-only

# 自定义输入/输出
python3 scripts/kb-stat/conv-log-analyzer.py --src conversation-log/db-sessions --db tmp/convlog.db --out tmp/conv-charts

# 统计结果另存 JSON（tmp/convlog-stats-YYYY-MM-DD.json）
python3 scripts/kb-stat/conv-log-analyzer.py --json
```

**输出**：`tmp/convlog.db`（sessions/rounds/toolcalls 三表）+ 8 图（话题分布/行为分型/月度趋势/工具模式/回合纠偏/渠道对比/话题×行为矩阵/自主放大系数）。
**产出案例**：`knowledge/02_rd/02_project/03_kb_cowagent/2026-08-08-conversation-log-deep-analysis.md`

### `kb-stat/token-consumption-analyzer.py` — 运行日志 Token 消耗通用分析器

将 CowAgent `run.log` 全量事件解析入 SQLite（14 张事件表），产出明细期统计（压缩解剖/会话维度/工具截断/思考/可靠性）+ 官方计费 JSON 拼接的全周期时间线（日费用/星期模式/累计曲线/两期对比/节省情景）。

```bash
# 全流程（解析+统计+全周期+14图）
python3 scripts/kb-stat/token-consumption-analyzer.py

# 纯统计 / 复用 DB / 仅明细期
python3 scripts/kb-stat/token-consumption-analyzer.py --no-charts
python3 scripts/kb-stat/token-consumption-analyzer.py --stats-only
python3 scripts/kb-stat/token-consumption-analyzer.py --no-timeline

# 自定义输入与估算模型参数
python3 scripts/kb-stat/token-consumption-analyzer.py --log tmp/run.log --official spec/scripts/deepseek_consumption.json \
  --sys-pre 118000 --sys-post 18000 --opt-date 2026-08-07 --hist-per-msg 300

# 统计另存 JSON（tmp/token-stats-YYYY-MM-DD.json）
python3 scripts/kb-stat/token-consumption-analyzer.py --json
```

**输出**：`tmp/runlog.db` + 明细期 9 图 + 全周期 5 图。
**产出案例**：`knowledge/02_rd/02_project/03_kb_cowagent/2026-08-07-token-consumption-visual-analysis.md`（明细期 v2.0）· `2026-08-08-token-consumption-full-timeline-analysis.md`（全周期 v3.0）

---

## 📦 导入管线（autokb/）

### `autokb/run_pipeline.py` — 知识库导入管线

从 `import/` 目录到 `knowledge/` 的完整导入管线：发现→分类→导入→索引。

```bash
# 全量导入
python3 scripts/autokb/run_pipeline.py --all

# 指定来源目录
python3 scripts/autokb/run_pipeline.py --source doubao
python3 scripts/autokb/run_pipeline.py --source server

# 单文件导入
python3 scripts/autokb/run_pipeline.py --file import/doubao/xxx.md

# 预览模式（不实际写入）
python3 scripts/autokb/run_pipeline.py --all --dry-run

# 导入后归档源文件
python3 scripts/autokb/run_pipeline.py --all --archive

# 限制处理数量（调试用）
python3 scripts/autokb/run_pipeline.py --all --max 10

# 禁用去重
python3 scripts/autokb/run_pipeline.py --source doubao --no-dedup
```

**管线模块清单**:

| 模块 | 文件 | 职责 |
|:-----|:-----|:------|
| 🎮 CLI | `run_pipeline.py` | 全参数入口 |
| ⚙️ 配置 | `config.py` | 路径/模块映射/忽略列表 |
| 🔍 发现 | `discover.py` | 文件扫描/去重/标题提取 |
| 🏷️ 分类 | `classify.py` | 规则引擎分类 + slug 生成 |
| 📦 导入 | `importer.py` | frontmatter 生成/归档/批量导入 |
| 📋 索引 | `index_updater.py` | index.md + log.md 自动追加 |
| 🔄 编排 | `pipeline.py` | 4 步管线编排 |

---

## 🔗 Git 类（git/）

### `git/git-pull-robust.py` — 可靠拉取

针对 GitHub 网络不稳定场景，提供多策略重试、代理支持、自动 stash 等。

```bash
# 拉取当前分支
python3 scripts/git/git-pull-robust.py

# 拉取指定分支
python3 scripts/git/git-pull-robust.py -b main

# 指定代理
python3 scripts/git/git-pull-robust.py --proxy http://127.0.0.1:7890

# 仅 fetch 不 merge
python3 scripts/git/git-pull-robust.py --fetch

# 使用 rebase 而非 merge
python3 scripts/git/git-pull-robust.py --rebase

# 自动 stash 本地变更
python3 scripts/git/git-pull-robust.py --stash

# 仅诊断网络
python3 scripts/git/git-pull-robust.py --diagnose

# 克隆仓库
python3 scripts/git/git-pull-robust.py --clone https://github.com/user/repo.git -d ~/repo
```

### `git/git-push-robust.py` — 可靠推送

多策略重试推送，支持代理和自动 commit。

```bash
# 推送当前分支
python3 scripts/git/git-push-robust.py

# 推送指定分支
python3 scripts/git/git-push-robust.py -b main

# 自动 add + commit + push
python3 scripts/git/git-push-robust.py --commit -m "update docs"

# 指定代理
python3 scripts/git/git-push-robust.py --proxy http://127.0.0.1:7890

# 强制推送（谨慎使用）
python3 scripts/git/git-push-robust.py --force
```

---

## 📄 根级其他脚本

| 脚本 | 用途 | 调用方式 |
|:-----|:-----|:---------|
| `kb-daily-files.sh` | 大变更文件发现（git-based，>100行过滤，排除01_survey/weekly-reports） | `bash scripts/kb-daily-files.sh [日期]` |
| `knowledge-stats-collector.py` | 知识库统计数据采集（Git 提交/文件/大小） | `python3 scripts/knowledge-stats-collector.py` |
| `knowledge-special-reports-updater.py` | 专项报告自动更新（4 份定期报告） | `python3 scripts/knowledge-special-reports-updater.py` |
| `knowledge-sync-optimizer.py` | 知识库同步优化（分 4 阶段） | `python3 scripts/knowledge-sync-optimizer.py` |
| `fix_skills_paths.py` | Skills 绝对路径检测与修复 | `python3 scripts/fix_skills_paths.py --check` |
| `import_files.py` | 导入 txt/md 到 import 目录 | `python3 scripts/import_files.py <source_dir>` |
| `dedup_import.py` | import 目录去重 | `python3 scripts/dedup_import.py --execute` |
| `convert-to-markdown.py` | 批量转换 PDF/DOC/HTML 为 Markdown | `python3 scripts/convert-to-markdown.py -i ./docs` |
| `fetch_github_skills.py` | 从 GitHub 批量下载 Skill 模板 | `python3 scripts/fetch_github_skills.py` |

---

## 🔗 向后兼容软链接

以下根级 `scripts/*.py` 为软链接，指向 `check/` 子目录中的实际脚本：

| 软链接 | 实际指向 | 用途 |
|:-------|:---------|:-----|
| `scripts/check_links.py` | `check/link-validator.py` | 链接检测 |
| `scripts/check_md_format.py` | `check/md-format.py` | 格式规范 |
| `scripts/knowledge_health_check.py` | `check/kb-health.py` | 知识库健康扫描 |
| `scripts/check_tech_doc_quality.py` | `check/doc-quality.py` | 技术文档质量 |
| `scripts/review_doc.py` | `check/doc-review.py` | 文档审查 |
| `scripts/validate_structure.py` | `check/roadmap-structure.py` | 图谱结构 |
| `scripts/fix_index_links.py` | `check/fix-index-urlencode.py` | URL 编码修复 |
| `scripts/reformat_log.py` | `check/reformat-log.py` | log 排序 |

> **完整分类映射**: 见 [`scripts/skills-scripts-mapping.md`](skills-scripts-mapping.md) — 按 Skill→脚本的传统视图

---

## 📊 总览指标

| 指标 | 数值 |
|:-----|:----:|
| **总脚本数** | **154 个** |
| **Python 脚本** | ~130 个 |
| **Shell/JS/PS1** | ~5 个 |
| **文档/映射表** | 3 个 |
| **backup 历史脚本** | ~80 个（待清理评估） |

---

## 📋 脚本分组总览

| 分组 | 文件数 | 核心脚本 | 职责 |
|:-----|:------:|:---------|:------|
| 🎮 **autokb 导入管线** | 7 | `run_pipeline.py` · `discover.py` · `classify.py` · `importer.py` · `index_updater.py` · `config.py` | import→knowledge 端到端管线 |
| 🔍 **check 质量检查** | 14 | `constraint-check.py` · `kb-health.py` · `link-validator.py` · `link-fixer.py` · `link-augmenter.py` · `md-format.py` · `analyze-index-coverage.py` · `reformat-log.py` · `directory-architect.py` · `subdir-nav-fixer.py` · `ref-drift-detector.py` · `extract-index-metadata.py` · `fix-index-urlencode.py` · `doc-review.py` · `doc-quality.py` · `strategy-compliance.py` | 约束合规/健康度扫描/链接验证/格式检查/索引覆盖/目录架构 |
| 🛠️ **tools 独立工具** | 7 | `html-to-markdown.py` · `chromedriver-setup.py` · `classify-questions.py` · `extract-chat-content.py` · `extract-user-questions.py` · `fix-align.py` · `check-align.py` | 格式转换/浏览器配置/数据分析 |
| 🔄 **git 版本控制** | 2 | `git-pull-robust.py` · `git-push-robust.py` | Git 安全推送/拉取 |
| 📊 **intent_analysis 意图分析** | 5 | `main.py` · `extract_user_questions.py` · `analyze_topic_boundaries.py` · `generate_intent_report.py` | 对话记录语义分析 |
| 🗂️ **backup 历史备份** | ~80 | doubao(50+) / chrome-test(20) / html-classes(17) / other(7) | 历史试验脚本，待评估清理 |
| 📄 **根级别名** | 15+ | 详见 §向后兼容软链接 | 独立功能 + 向后兼容软链接 |

---

## ⚡ 快速命令速查

### 快速操作

```bash
# 约束合规检查（默认 safety + format + index-log + code）
python3 scripts/constraint-check.py

# 全量约束检查
python3 scripts/constraint-check.py --category all --summary

# 导入原始素材到知识库
python3 scripts/autokb/run_pipeline.py --source md --max 10

# 质量自检（写入文档后用）
python3 scripts/check/doc-quality.py <文档.md>

# 完整审查（发布前）
python3 scripts/check/doc-review.py <文档.md>

# 链接检查
python3 scripts/check/link-validator.py

# 格式修复
python3 scripts/check/md-format.py <文档.md>
```

### 分析工具

```bash
# 对话记录导出
python3 scripts/tools/extract-chat-content.py

# 用户输入分析
python3 scripts/tools/extract-user-questions.py

# 意图分析报告
python3 scripts/intent_analysis/generate_intent_report.py

# 会话日志深度分析（话题/行为/过程量化+图表）
python3 scripts/kb-stat/conv-log-analyzer.py

# Token 消耗分析（明细期+全周期时间线）
python3 scripts/kb-stat/token-consumption-analyzer.py
```

### 维护工具

```bash
# index.md URL 修复
python3 scripts/check/fix-index-urlencode.py

# log.md 格式重整
python3 scripts/check/reformat-log.py

# 知识库健康检查
python3 scripts/check/kb-health.py

# Skills 绝对路径检测
python3 scripts/fix_skills_paths.py --check
```

### Web 浏览

```bash
# 启动 Flask 知识库浏览器
python3 flask_dir_browser.py
```

---

## 🔄 Skills + Scripts 双引擎协作矩阵

| 场景 | 用 Skills | 用 Scripts | 协作模式 |
|:-----|:---------|:-----------|:---------|
| 写一份深度报告 | ✅ `deep-tech-writer` | — | 技能驱动，人工审阅 |
| 批量导入文件 | — | ✅ `autokb/run_pipeline.py` | 脚本批量，技能辅助 |
| 文档质量审查 | ✅ `doc-reviewer` | ✅ `check/doc-review.py` + `check/md-format.py` | 脚本先扫格式，技能再审结构 |
| 链接维护 | ✅ `web-archive` | ✅ `check/link-validator.py` + `check/link-fixer.py` | 脚本扫描，技能修复建议 |
| 知识库规范化 | ✅ `index-deep-analyzer` | ✅ `check/knowledge-normalizer.py` | 技能编排5阶段流水线 |
| 定时周报 | ✅ `weekly-report-generator` | — | 技能 + scheduler |
| 对话意图分析 | — | ✅ `intent_analysis/main.py` | 脚本分析，结果反哺技能 |
| 知识库健康检查 | ✅ `knowledge-health-check` | ✅ `check/kb-health.py` | 技能编排，脚本执行 |
| 同步优化 | ✅ `knowledge-sync` | ✅ `knowledge-sync-optimizer.py` | 技能 + 脚本 + scheduler 联动 |
| 约束合规检查 | ✅ `constraint-verifier` | ✅ `constraint-check.py` | 脚本扫描，技能AI解读 |

---

## 📝 变更记录

| 日期 | 变更说明 |
|:----|:---------|
| 2026-08-08 | 新增 `kb-stat/conv-log-analyzer.py` — 会话日志通用分析器（extract→analyze→visualize 一体化，8 图+JSON 输出） |
| 2026-08-08 | 新增 `kb-stat/token-consumption-analyzer.py` — 运行日志 Token 消耗分析器（明细期+官方计费拼接全周期，14 图+JSON 输出） |
| 2026-07-24 | 约束编码重构：C-xxx → 5 位数字 CCLRR（含总览指标、分组总览、速查、协作矩阵）；同步更新 SR-003 编码 |

