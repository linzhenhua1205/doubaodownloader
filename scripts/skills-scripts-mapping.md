# 📌 Skills ↔ 脚本映射表

> 快速检索每个 skill 关联的脚本文件，方便批量导出/备份。
>
> 最后更新: 2026-07-27
>
> **📋 分类版本**: 详见 [`README.md`](README.md) — 按 6 大类操作类型组织
>
> **📐 设计架构**: Skills ↔ Scripts 映射的架构设计与合规要求详见 [`spec/design-007-skills-scripts-design.md`](../spec/design-007-skills-scripts-design.md) §4
>   - 1a: 📥 豆包导入 | 1b: 🔗 Web归档 | 2: 📝 专题创建 | 3: 🔄 import提取 | 4: 🔧 格式转换 | 5: ✅ 检查确认 | 6: ⚡ 其他

---

## 分类总览

| 层级 | 位置 | 用途 |
|:-----|:-----|:------|
| 🏗️ **Workspace 通用脚本** | `scripts/` | 独立于任何 skill 的工具，从项目根目录用 `python3 scripts/xxx.py` 调用 |
| 💬 **对话记录脚本** | `conversation-log/` | 导出历史会话记录 |
| 🔧 **Skill 内部脚本** | `skills/<skill-name>/scripts/` | Skill 运行时调用的辅助脚本，紧耦合于 skill 工作流 |

---

## 🏗️ Workspace 通用脚本

> 脚本已按用途分组到子目录，根级 `scripts/*.py` 仅为向后兼容的软链接。新调用优先使用子目录路径。

### `check/` — 质量检测类

| 脚本 (子目录) | 用途 | 备注 |
|:-------------|:-----|:-----|
| `constraint-check.py`（根级） | **新增统一入口** 约束合规检查器（11 类别 × 70 条 C-xxx） | 原生，推荐入口 |
| `check/link-validator.py` | **增强版** 链接有效性扫描 + 5 分类（DEPTH/MOVED/DIR_RENAME/EXTERNAL/MISSING）+ 修复建议 | 原生，推荐入口 |
| `check/link-fixer.py` | **新增** 智能链接修复引擎（规则驱动 + 批量 + 创建 stub） | 原生，配合 link-validator |
| `check/link-augmenter.py` | **新增** 裸文件名引用检测 + 自动添加 markdown 链接 | 原生 |
| `check/md-format.py` | Markdown 格式规范检查（方框字符/块填充/中文混排） | 原生 |
| `check/fix-log-ordering.py` | log.md 时间倒序重整（旧版，一次性脚本） | 原生，已废弃 |
| `check/reformat-log.py` | **增强版** log.md 通用格式化（blockquote/表格/纯列表→标准条目 + 日期排序 + 重复合并 + 校验 + --all） | 原生，推荐入口 |
| `check/index-log-normalizer.py` | **新增** index/log 每目录作用域合规（--check/--fix/--init/--dry-run，幂等，集成于 normalizer 第6阶段） | 原生，v1.0 |
| `check/analyze-index-coverage.py` | **增强版** index.md 覆盖率分析（--all全库/单模块 + --fix自动补全 + JSON输出） | 原生 |
| `check/extract-index-metadata.py` | 批量提取 .md 文件标题和摘要（JSON/MD 输出） | 原生 |
| `check/directory-architect.py` | **新增** 目录架构分析 + index.md 生成（MECE分层/关联矩阵/阅读路径/决策框架） | 原生 |
| `check/subdir-nav-fixer.py` | **新增** 子目录导航一致性修复（添加上层入口链接） | 原生 |
| `check/fix-index-urlencode.py` | index.md URL 编码中文文件名修复 | 原生 |
| `check/kb-health.py` 🔗 | 6维知识库健康扫描（模块列表已更新 + 路径修正） | → skills/knowledge-health-check |
| `check/doc-quality.py` 🔗 | 技术文档质量自检 | → skills/deep-tech-writer |
| `check/doc-review.py` 🔗 | 三层文档审查（结构/逻辑/来源） | → skills/doc-reviewer |
| `check/roadmap-structure.py` 🔗 | 服务器知识图谱结构校验 | → skills/roadmap-maintainer |
| `check/quantitative-check.py` | **量化数据合规检查** — 裸数字/缺来源/缺基线/缺上下文检测 ✅ sr-006 D-03 | 原生，v1.0 |
| `check/strategy-compliance.py` | **新增** 策略合规校验（A/B/C/D/E 五类策略匹配 + 放置决策树合规） | 原生，v1.0 | |
| `check/format-validator.py` | **新增** T1-T7 格式合规校验（自动检测文件类型 + 逐模板检查） | 原生，v1.0 | |
| `check/relation-integrity.py` | **新增** 关系完整性校验（类型校验/目标存在/反向链接） | 原生，v1.0 | |
| `check/content-format-normalizer.py` | **新增** 内容文件五大要素合规（概要/关键词/目录/参考文件/Changelog，--check/--fix/--dry-run/--all，幂等） | 原生，v1.0 |
| `check/extract-content-metadata.py` | **新增** 内容文件元数据提取→JSON（title/summary/keywords/toc/refs/changelog，归档 weekly-reports/07_kb_stat） | 原生，v1.0 |

### `search/` — 搜索与调研（新增）

| 脚本 (子目录) | 用途 | 备注 |
|:-------------|:-----|:-----|
| `search/unified-search.py` | **统一搜索入口** — 搜索计划/增量追踪/源管理/结果汇总 ✅ sr-006 A-01/G-01 | 原生，v1.0 |

### `tools/` — 独立工具类

| 脚本 (子目录) | 用途 | 来源 |
|:-------------|:-----|:-----|
| `tools/classify-questions.py` | 筛选和分类服务器研发相关问题 | backup/classify_server_questions.py（已归档至 `tmp/bak/scripts-backup-cleanup-2026-07-27/`） |
| `tools/extract-user-questions.py` | 遍历项目文件提取用户提问 | backup/extract_user_questions.py（已归档） |
| `tools/html-to-markdown.py` | HTML→Markdown 转换 | backup/html_to_markdown_v3.py（已归档） |
| `tools/extract-chat-content.py` | 从 HTML 提取聊天内容 | backup/extract_chat_content.py（已归档） |
| `tools/fix-align.py` | 修复中文/ASCII 混排对齐 | backup/fix_align.py（已归档） |
| `tools/check-align.py` | 检测字符对齐宽度 | backup/check_align.py（已归档） |
| `tools/chromedriver-setup.py` | ChromeDriver 下载 + 安装检测 | backup/chrome-test/（已归档） |
| `tools/mv-knowledge.py` | **知识库文件迁移 CLI** — mv + index/log 更新 + 交叉引用修复 + 迁移审计 | 原生，v1.0 ✅ sr-006 E-01 |
| `tools/execution-log.py` | **定时任务执行日志** — 状态记录/零产出检测/重试建议/监控报表 | 原生，v1.0 ✅ sr-006 I-01/I-02/I-06 |
| `tools/kb-metadb.py` | **内容元数据库** — 遍历 2100+ .md 文件构建可搜索 JSON 索引 | 原生，v1.0 ✅ sr-006 B-01 |
| `tools/errorcodes.py` | **统一错误码标准** — 0-99 标准化退出码定义 | 原生，v1.0 ✅ sr-006 X-11 |

### `discover/` — AI 批量知识加工脚本（新增）

> **设计规范**: 详见 [`spec/sr-005-discover-dir-req.md`](../spec/sr-005-discover-dir-req.md) §3.5
> **技能入口**: [`skills/discover/`](../skills/discover/SKILL.md)

| 脚本 | 用途 | 对应 FR | 优先级 |
|:-----|:------|:-------:|:------:|
| `discover/extract-questions.py` | **import 问题提取** — 从 import/ 素材中提取用户问题 | FR-22 | P0 |
| `discover/ai-classify.py` | **AI 分类** — 按分类体系自动归类 | FR-23 | P0 |
| `discover/ai-extract-keywords.py` | **AI 提取关键字** — 提取 5-15 个关键词 | FR-24 | P0 |
| `discover/ai-batch-extract-questions.py` | **AI 批量提取问题** — 从陈述中推理问题 | FR-25 | P0 |
| `discover/ai-batch-gen-docs.py` | **AI 批量从问题生成文档** — 问题→知识卡片 | FR-26 | P0 |
| `discover/ai-batch-enhance.py` | **AI 批量文档治理** — 质量检测+提升 | FR-27 | P1 |
| `discover/import-to-knowledge.py` | **discover→knowledge 导入** — 质量门禁+归档 | FR-28 | P1 |
| `discover/config.py` | 共享配置（路径/分类体系/质量等级） | — | — |

### `autokb/` — 知识库自动化导入管线

| 脚本 | 用途 |
|:-----|:------|
| `autokb/run_pipeline.py` | CLI 入口（--all/--source/--dry-run） |
| `autokb/pipeline.py` | 主编排器（发现→分类→导入→索引） |
| `autokb/discover.py` | 文件发现与去重 |
| `autokb/classify.py` | 内容分类 |
| `autokb/importer.py` | 导入管线 |
| `autokb/index_updater.py` | index.md + log.md 自动追加 |
| `autokb/config.py` | 全局配置（路径/关键词/忽略列表） |

### 🔄 根级兼容别名

以下 `scripts/*.py` 均为软链接，保持旧命令和 SKILL.md 引用有效：

| 根级别名 | 实际链 | 用途 |
|:---------|:-------|:-----|
| `check_links.py` 🔗 | → check/link-validator.py | 链接检测（被 web-archive SKILL 引用） |
| `check_md_format.py` 🔗 | → check/md-format.py | 格式规范（被 3 个 SKILL 引用） |
| `fix_index_links.py` 🔗 | → check/fix-index-urlencode.py | URL 编码修复 |
| `reformat_log.py` 🔗 | → check/reformat-log.py | log 格式化（增强版） |
| `knowledge_health_check.py` 🔗 | → check/kb-health.py | 知识库健康扫描 |
| `check_tech_doc_quality.py` 🔗 | → check/doc-quality.py | 技术文档质量 |
| `review_doc.py` 🔗 | → check/doc-review.py | 文档审查 |
| `validate_structure.py` 🔗 | → check/roadmap-structure.py | 图谱结构 |
| `strategy-compliance.py` 🔗 | → check/strategy-compliance.py | 策略合规校验（v1.0, 2026-07-22） |
| `format-validator.py` 🔗 | → check/format-validator.py | T1-T7 格式合规校验（v1.0, 2026-07-22） |
| `relation-integrity.py` 🔗 | → check/relation-integrity.py | 关系完整性校验（v1.0, 2026-07-22） |

> 🔗 标记表示该脚本是软链接。新旧路径指向同一份实际文件，修改任意一个即同步生效。

## 💬 对话记录脚本

| 脚本 | 用途 | 依赖 |
|:-----|:-----|:-----|
| `conversation-log/export_db_sessions.py` | 从 SQLite 导出历史会话 | python3, sqlite3 |

### `intent_analysis/` — 会话意图分析

| 脚本 | 用途 |
|:-----|:-----|
| `intent_analysis/main.py` | CLI 入口（--step extract/analyze/report/all） |
| `intent_analysis/extract_user_questions.py` | 提取用户问题，去除定时任务 |
| `intent_analysis/analyze_topic_boundaries.py` | 识别话题边界和任务切换 |
| `intent_analysis/generate_intent_report.py` | 生成用户意图分析报告 |

---

## 🔧 Skill 内部脚本

按 skill 名称字母序排列。这些脚本是 skill 内部实现的一部分，**不应**单独使用。

### baidu-baike-data

| 脚本 | 语言 |
|:-----|:----:|
| `skills/baidu-baike-data/scripts/baidu_baike.py` | Python |

### baidu-scholar-search

| 脚本 | 语言 |
|:-----|:----:|
| `skills/baidu-scholar-search/baidu_scholar_search.sh` | Shell |

### baidu-search

| 脚本 | 语言 |
|:-----|:----:|
| `skills/baidu-search/scripts/search.py` | Python |

### bdpan-storage

| 脚本 | 语言 |
|:-----|:----:|
| `skills/bdpan-storage/scripts/install.sh` | Shell |
| `skills/bdpan-storage/scripts/login.sh` | Shell |
| `skills/bdpan-storage/scripts/uninstall.sh` | Shell |
| `skills/bdpan-storage/scripts/update.sh` | Shell |

### complex-system-function

| 脚本 | 语言 |
|:-----|:----:|
| `skills/complex-system-function/scripts/analyze_system_function.py` | Python |
| `skills/complex-system-function/scripts/check_experience_reuse.py` | Python |

### docx

| 脚本 | 语言 |
|:-----|:----:|
| `skills/docx/scripts/__init__.py` | Python |
| `skills/docx/scripts/accept_changes.py` | Python |
| `skills/docx/scripts/comment.py` | Python |
| `skills/docx/scripts/office/helpers/merge_runs.py` | Python |
| `skills/docx/scripts/office/helpers/simplify_redlines.py` | Python |
| `skills/docx/scripts/office/pack.py` | Python |
| `skills/docx/scripts/office/unpack.py` | Python |
| `skills/docx/scripts/office/soffice.py` | Python |
| `skills/docx/scripts/office/validate.py` | Python |
| `skills/docx/scripts/office/validators/base.py` | Python |
| `skills/docx/scripts/office/validators/docx.py` | Python |
| `skills/docx/scripts/office/validators/pptx.py` | Python |
| `skills/docx/scripts/office/validators/redlining.py` | Python |

### doubao-share

| 脚本 | 语言 |
|:-----|:----:|
| `skills/doubao-share/scripts/slugify.py` | Python |

### feishu-workspace

| 脚本 | 语言 |
|:-----|:----:|
| `skills/feishu-workspace/scripts/feishu_openapi.py` | Python |

### image-generation

| 脚本 | 语言 |
|:-----|:----:|
| `skills/image-generation/scripts/generate.py` | Python |

### pdf

| 脚本 | 语言 |
|:-----|:----:|
| `skills/pdf/scripts/check_bounding_boxes.py` | Python |
| `skills/pdf/scripts/check_fillable_fields.py` | Python |
| `skills/pdf/scripts/convert_pdf_to_images.py` | Python |
| `skills/pdf/scripts/create_validation_image.py` | Python |
| `skills/pdf/scripts/extract_form_field_info.py` | Python |
| `skills/pdf/scripts/extract_form_structure.py` | Python |
| `skills/pdf/scripts/fill_fillable_fields.py` | Python |
| `skills/pdf/scripts/fill_pdf_form_with_annotations.py` | Python |

### pptx

| 脚本 | 语言 |
|:-----|:----:|
| `skills/pptx/scripts/__init__.py` | Python |
| `skills/pptx/scripts/add_slide.py` | Python |
| `skills/pptx/scripts/clean.py` | Python |
| `skills/pptx/scripts/office/helpers/merge_runs.py` | Python |
| `skills/pptx/scripts/office/helpers/simplify_redlines.py` | Python |
| `skills/pptx/scripts/office/pack.py` | Python |
| `skills/pptx/scripts/office/unpack.py` | Python |
| `skills/pptx/scripts/office/validate.py` | Python |
| `skills/pptx/scripts/office/validators/base.py` | Python |
| `skills/pptx/scripts/office/validators/docx.py` | Python |
| `skills/pptx/scripts/office/validators/pptx.py` | Python |
| `skills/pptx/scripts/office/validators/redlining.py` | Python |

### roadmap-maintainer

| 脚本 | 语言 |
|:-----|:----:|
| `skills/roadmap-maintainer/scripts/validate_structure.py` | Python |

### skill-creator

| 脚本 | 语言 |
|:-----|:----:|
| `skills/skill-creator/scripts/init_skill.py` | Python |
| `skills/skill-creator/scripts/package_skill.py` | Python |
| `skills/skill-creator/scripts/quick_validate.py` | Python |

### thesis-helper

| 脚本 | 语言 |
|:-----|:----:|
| `skills/thesis-helper/scripts/script.sh` | Shell |
| `skills/thesis-helper/scripts/thesis.sh` | Shell |

### wechat-article-search

| 脚本 | 语言 |
|:-----|:----:|
| `skills/wechat-article-search/scripts/search_wechat.js` | Node.js |

### xlsx

| 脚本 | 语言 |
|:-----|:----:|
| `skills/xlsx/scripts/recalc.py` | Python |
| `skills/xlsx/scripts/office/helpers/merge_runs.py` | Python |
| `skills/xlsx/scripts/office/helpers/simplify_redlines.py` | Python |
| `skills/xlsx/scripts/office/pack.py` | Python |
| `skills/xlsx/scripts/office/unpack.py` | Python |
| `skills/xlsx/scripts/office/soffice.py` | Python |
| `skills/xlsx/scripts/office/validate.py` | Python |
| `skills/xlsx/scripts/office/validators/base.py` | Python |
| `skills/xlsx/scripts/office/validators/docx.py` | Python |
| `skills/xlsx/scripts/office/validators/pptx.py` | Python |
| `skills/xlsx/scripts/office/validators/redlining.py` | Python |

### 📐 deep-tech-writer（深度技术文档创建）

| 脚本路径 | 类型 |
|:---------|:-----|
| `skills/deep-tech-writer/scripts/check_tech_doc_quality.py` | Python — 六步工作流质量自检 |

### 📘 knowledge-doc-writer（知识库技术文档写作）

| 脚本路径 | 类型 |
|:---------|:-----|
| `scripts/tools/kb-log-search.py` | Python — **log.md 关键字检索（第一线索源，2026-08-25 新增）** 日期+路径+摘要+路径存在性兜底（✅/🔀/❌），支持 AND/OR、时间/模块/操作过滤、--path-only/--json/--stats/--topics |
| `skills/knowledge-doc-writer/scripts/check_paths.py` | Python — 通用路径/数据源验证（含 import/目录提取 + 关键词搜索） |
| `skills/knowledge-doc-writer/scripts/check_format.py` | Python — 通用文档格式规范检查（7规则，含量化数据来源标注R6） |

> **注**: 以上 2 个脚本也被 `server-asset-management-research` 复用（各自有适配版本，见下方）

### 🖥️ server-asset-management-research（服务器资产管理分析）

| 脚本路径 | 类型 |
|:---------|:-----|
| `skills/server-asset-management-research/scripts/check_paths.py` | Python — 服务器资产管理专用路径/数据源验证（BMC/FRU/CMDB 专用搜索路径） |
| `skills/server-asset-management-research/scripts/check_format.py` | Python — 服务器资产管理文档格式规范检查（BMC/资产管理内容特化版本） |

### 🕵️ doc-reviewer（文档审查）

| 脚本路径 | 类型 |
|:---------|:-----|
| `skills/doc-reviewer/scripts/review_doc.py` | Python — 三层自动化结构审查 |

### 🩺 knowledge-health-check（知识库完整性检测）

| 脚本路径 | 类型 |
|:---------|:-----|
| `skills/knowledge-health-check/scripts/knowledge_health_check.py` | Python — 6维知识库健康扫描（链接/表格/格式/日志排序/文件位置） |

### 🔧 log-reformatter（log.md 格式化）

| 脚本路径 | 类型 |
|:---------|:-----|
| `scripts/check/reformat-log.py` | Python — log.md 通用格式化（blockquote/表格/纯列表→标准条目 + 日期排序 + 校验） |

### 📋 knowledge-index-manager（统一索引管理 — 合并技能 v1.0）

> **替代了**原 `index-deep-analyzer` + `index-log-maintainer` + `index-rebuilder` 三个技能的全部功能。

| 脚本路径 | 类型 |
|:---------|:-----|
| `scripts/check/knowledge-normalizer.py` | Python — **一站式入口** 6阶段规范化流水线（index+log+links+augment+format+scope） |
| `scripts/check/index-log-normalizer.py` | Python — index/log 每目录作用域合规（--check/--fix/--init/--dry-run，幂等） |
| `scripts/check/analyze-index-coverage.py` | Python — index.md 覆盖率分析（--all全库/单模块 + --fix自动补全 + JSON） |
| `scripts/check/extract-index-metadata.py` | Python — 批量提取 .md 文件标题和摘要（JSON/MD 输出） |
| `scripts/check/link-validator.py` | Python — 链接有效性扫描（5分类：DEPTH/MOVED/DIR_RENAME/EXTERNAL/MISSING） |
| `scripts/check/link-fixer.py` | Python — 智能链接修复引擎（规则驱动 + 批量 + 创建 stub） |
| `scripts/check/link-augmenter.py` | Python — 裸文件名引用检测 + 自动添加 markdown 链接 |
| `scripts/check/md-format.py` | Python — Markdown 格式规范检查（方框字符/块填充/中文混排） |
| `scripts/check/reformat-log.py` | Python — log.md 统一格式化（倒序 + 表格→标准条目 + 去重 + 校验） |
| `scripts/check/directory-architect.py` | Python — 目录架构分析 + index.md 生成（MECE分层/关联矩阵/阅读路径/决策框架） |
| `scripts/check/subdir-nav-fixer.py` | Python — 子目录导航一致性修复（添加上层入口链接） |
| `scripts/tools/mv-knowledge.py` | Python — **文件迁移 CLI（新增）** mv + index/log 更新 + 交叉引用修复 + 迁移审计 |

### 🏗️ directory-optimizer（目录架构优化）

| 脚本路径 | 类型 |
|:---------|:-----|
| `scripts/check/directory-architect.py` | Python — **核心脚本** 目录架构分析 + index.md 生成（MECE分层/关联矩阵/阅读路径/决策框架） |
| `scripts/check/subdir-nav-fixer.py` | Python — 子目录导航一致性修复（添加上层入口链接） |
| `scripts/check/extract-index-metadata.py` | Python — 批量提取 .md 文件元数据（共享工具） |

### 🧠 session-intent-analysis（会话意图分析）

| 脚本路径 | 类型 |
|:---------|:-----|
| `scripts/intent_analysis/main.py` | Python — CLI 入口 |
| `scripts/intent_analysis/extract_user_questions.py` | Python — 提取用户问题 |
| `scripts/intent_analysis/analyze_topic_boundaries.py` | Python — 话题边界分析 |
| `scripts/intent_analysis/generate_intent_report.py` | Python — 意图报告生成 |

### 🛡️ system-guardian（系统守护） 🆕

| 脚本路径 | 类型 |
|:---------|:-----|
| `scripts/system-guardian-runner.py` | Python — 统一入口运行器 |
| `scripts/check/check-tasks-integrity.py` | Python — 定时任务一致性 |
| `scripts/check/check-skills-registration.py` | Python — 注册完整性审计（新） |

---

## 快速导出命令

```bash
# 全部 workspace 脚本
tar czf scripts-workspace.tar.gz scripts/ conversation-log/export_db_sessions.py conversation-log/export_user_questions.py

# 全部 skill 内部脚本
tar czf scripts-skills.tar.gz skills/*/scripts/ skills/*/*.sh skills/*/*.js

# 单个 skill 的脚本
tar czf scripts-skill-docx.tar.gz skills/docx/scripts/

# 脚本总数统计
echo "Workspace: $(find scripts/ -name '*.py' -o -name '*.sh' | wc -l) files"
echo "Conversation-log: $(find conversation-log/ -name '*.py' | wc -l) files"
echo "Skills: $(find skills/*/scripts/ skills/*/*.sh skills/*/*.js -type f | grep -v __pycache__ | wc -l) files"
```
