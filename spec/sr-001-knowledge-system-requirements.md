> 📌 **备注（v1.3 原文头部，2026-08-19 提升时保留，不删除）**: 以下为旧版标题与头部元信息——正文以新版头部（结论先行）为准。
> 
> **旧版标题**: SR-001: Cow 知识库系统用户需求说明书
>
> **版本**: v1.3 | **创建**: 2026-07-21
>
> **来源**: 用户原始需求输入（2026-07-21 对话）
>
> **定位**: 本文件记录 Cow 知识库系统的完整用户需求（SR），作为后续设计规格（design-001-system-architecture.md）和开发规范（std-001-development-rules.md）的需求来源依据。每个 SR 条目对应一个或多个 AR（Architecture Requirements），映射关系见 `ar-001-sr-ar-mapping.md`。
>

# sr-001-knowledge-system-requirements.md — Cow 知识库系统用户需求说明书（v2.0 提升版）

> **版本**: v2.0 | **创建**: 2026-07-21 | **更新**: 2026-08-19 | **状态**: ✅ 生效中（历史需求记录，新需求点直接写入 ar-001）
>
> **结论先行（30 秒版）**:
> 1. **本文定位**：全部用户需求的**权威来源**（SR），design-001（架构）与 std-001（规范）的需求依据；每条 SR 对应一个或多个 AR，映射见 [`ar-001-sr-ar-mapping.md`](./ar-001-sr-ar-mapping.md)。
> 2. **核心目标**：AI 驱动的**自演进知识库系统**，面向产品研发（服务器/AI 基础设施），覆盖技术/工具/概念/企业管理多维知识。
> 3. **五大特点**：C1 AI 驱动构建 · C2 自动优化（自检/自修复/自演进）· C3 创造性验证 · C4 幻觉约束（可信可追溯）· C5 三论指导（MECE + 第一性原理 + 约束辩证法）。
> 4. **总体框架**：四阶段数据流——收集（import/）→ 加工（discover/）→ 优化（knowledge/）→ 使用（浏览/Git/AI 检索）。
> 5. **维护原则（2026-08-19 起）**：**SR 即历史**——不再新增 SR 条目，新需求点直接写入 ar-001；例外：需求收集/盘点性质文档（如 sr-011）可新增。
>
> **来源**: 用户原始需求输入（2026-07-21 对话）
>
> **定位**: 本文件记录 Cow 知识库系统的完整用户需求（SR），作为后续设计规格（design-001-system-architecture.md）和开发规范（std-001-development-rules.md）的需求来源依据。每个 SR 条目对应一个或多个 AR（Architecture Requirements），映射关系见 `ar-001-sr-ar-mapping.md`。
>
> **提升说明（2026-08-19，v1.3 → v2.0）**: ① 新增「结论先行（30 秒版）」+ 状态字段；② 补记「SR 即历史」维护原则（2026-08-19，与 README 流转原则对齐）。**正文旧内容未删除**。

---

## 📑 目录

1. [需求概述](#1-需求概述)
2. [SR 清单](#2-sr-清单)
3. [四阶段数据流需求](#3-四阶段数据流需求)
4. [模块需求](#4-模块需求)
5. [配套系统需求](#5-配套系统需求)
6. [后续优化需求](#6-后续优化需求)

---
>
> **建议前置阅读**: design-001-system-architecture.md — 了解系统架构全貌
>

## 1. 需求概述

### 1.1 系统目标

创建一个具备**自演进能力**的、**主要面向产品研发**（特别是服务器领域与 AI 领域）的知识库系统，同时覆盖工具、概念理解、企业管理、产品产研销等多维度知识。

### 1.2 核心特点

| # | 特点 | 说明 |
|:--|:-----|:------|
| C1 | AI 驱动构建 | 使用 AI 技术搭建，充分发挥 AI 在知识组织/提炼/分析中的创造性 |
| C2 | 自动优化能力 | 系统具备自检、自修复、自演进机制，越用越聪明 |
| C3 | 创造性验证 | 验证 AI 技术在知识库领域的应用，探索 AI 辅助知识生产的最佳实践 |
| C4 | 幻觉约束 | 在发挥创造性的同时约束 AI 幻觉，提供可信、可追溯的输出 |
| C5 | 三论指导 | 在 **MECE + 第一性原理 + 约束辩证法** 三论指导下进行数据处理与系统设计 |

### 1.3 总体框架

系统围绕**数据处理四阶段**构建：

```text
数据收集 → 数据加工 → 数据优化 → 数据使用
  (Phase 1)   (Phase 2)   (Phase 3)   (Phase 4)
```

---

## 2. SR 清单

### 2.1 SR 编号规则

- **SR-xxx**: 用户需求条目，按顺序编号
- 优先级：**P0**（核心/必须）、**P1**（重要/应做）、**P2**（增强/可做）
- 状态：✅ **已实现** | 🚧 **实现中** | 📋 **待规划**

### 2.2 需求列表

| 编号 | 需求描述 | 对应阶段 | 优先级 | 状态 |
|:-----|:---------|:--------:|:------:|:----:|
| SR-001 | 本地 Markdown 文件夹/文件批量导入 | Phase 1 | P0 | ✅ |
| SR-002 | 非 Markdown 文件（PDF/Word/PPT/Excel/图片等）转 Markdown 后导入 | Phase 1 | P0 | ⚠️ **部分实现** |
| SR-003 | 公众号文章、特定网站内容采集后导入（当前外部实现，后续整合） | Phase 1 | P1 | 🚧 |
| SR-004 | 工程文件夹直接导入到 `projects/` 目录 | Phase 1 | P1 | ✅ |
| SR-005 | 导入素材统一存储到 `import/` 目录作为素材库 | Phase 1 | P0 | ⚠️ **台账过时** |
| SR-006 | 使用 AI 对 `import/` 素材进行批量汇总分析 | Phase 2 | P0 | ⚠️ **管线就绪但未规模执行** |
| SR-007 | AI 提炼信息输出到 `discover/` 目录 | Phase 2 | P0 | ⚠️ **discover/ 实际为空** |
| SR-008 | 网站信息通过 AI Skills 生成笔记，归入知识库 | Phase 3 | P0 | ✅ |
| SR-009 | 外部 AI 对话（如豆包/豆包导入）生成笔记归入知识库 | Phase 3 | P1 | ✅ |
| SR-010 | 定时 AI 行业调研，结果保存到 `knowledge/01_survey/` | Phase 3 | P0 | ✅ |
| SR-011 | 定期 AI 系统报告生成，保存到 `knowledge/weekly-reports/` | Phase 3 | P0 | ✅ |
| SR-012 | 日常对话基于 AI 生成主题，对话记录保存到 `conversation-log/` | Phase 3 | P0 | ✅ |
| SR-013 | 知识库配套 Skills 和 Scripts 的系统化管理 | Phase 3 | P0 | ✅ |
| SR-014 | 本地 Web 浏览（Flask 目录浏览器） | Phase 4 | P0 | ✅ |
| SR-015 | Git 提交到 GitHub 远程浏览 | Phase 4 | P0 | ✅ |
| SR-016 | AI 配套的身份文件体系（AGENT.md / USER.md / MEMORY.md / RULE.md） | 配套 | P0 | ✅ |
| SR-017 | 每日记忆系统（memory/ 目录） | 配套 | P0 | ✅ |
| SR-018 | Skills 和 Scripts 功能体系 | 配套 | P0 | ✅ |
| SR-019 | 定时任务处理框架（Scheduler） | 配套 | P0 | ✅ |
| SR-020 | 渠道框架（Feishu 等），实现 Agent 交互功能 | 配套 | P0 | ✅ |
| SR-021 | 整合 RAG 知识（向量化检索） | 后续 | P1 | 📋 |
| SR-022 | 增强可信 AI 输出与配套设施建设 | 后续 | P1 | 🚧 |
| SR-023 | 增强采集过程（公众号/网站采集整合到系统内） | 后续 | P1 | 📋 |
| SR-024 | 系统具备自演进能力，自动识别短板、优化策略 | 全局 | P1 | 🚧 |
| SR-025 | import 素材批量处理管线：自动发现 → 批量分析 → 去重分类 → 写入 discover | Phase 2 | P1 | 📋 |

---

## 3. 四阶段数据流需求

### 3.1 Phase 1：数据收集

**用户需求**：

```
输入：
  1) 本地 Markdown 文件夹导入，本地 Markdown 文件导入，直接导入
  2) 本地非 Markdown 文件（PDF/Word/PPT/Excel/图片/视频/压缩包等），进行 Markdown 化后导入
  3) 公众号文章、特定网站内容，提供采集脚本进行采集后导入（当前在外部实现，后续需整合）
  4) 工程文件夹直接导入到根目录下的 projects/ 下

导入位置：
  - Markdown 素材 → import/
  - 工程文件 → projects/

用途：
  供数据初步加工，作为后续知识库处理的素材库
```

**关键约束**：
- import/ 目录内容仅作为素材，不做为文档唯一来源
- 关键量化数据必须经独立源交叉验证
- 导入后的原文不做修改

**对应 Skills**：
- `markdown-converter`: 非 Markdown → Markdown 转换
- `web-archive`: URL 归档
- `doubao-share`: 豆包对话归档

### 3.2 Phase 2：数据加工

**用户需求**：

```
输入：
  import/ 目录下的内容

加工方式：
  使用 AI 进行批量汇总分析，提炼信息到 discover/ 目录下

用途：
  挖掘素材库的信息，供进一步深加工使用

对应 Skills：
  - light-literature-search：文献调研
  - baidu-scholar-search：学术搜索
  - 其他 AI 分析类 Skills
```

**关键约束**：
- AI 提炼需保留来源引用
- 去重分类，避免冗余
- 标注可信度与不确定性

### 3.3 Phase 3：数据优化

**用户需求**：

```
输入：
  - 网站信息通过 AI Skills 生成笔记
  - 外部 AI 对话（如豆包）导入生成笔记
  - 定时 AI 行业调研 → knowledge/01_survey/
  - 定期 AI 系统报告生成 → knowledge/weekly-reports/
  - 日常对话 AI 生成主题

输出：
  - knowledge/ 目录下的结构化知识
  - 系统配套的 Skills 和 Scripts

加工方法：
  AI 对话、AI 加工为主，进行深度加工，确保数据质量
```

**关键约束**：
- 多层质量门禁（语法/逻辑/格式/来源）
- 断言有出处，数据有基线
- 框架堆名词不深入原理 = 不合格

### 3.4 Phase 4：数据使用

**用户需求**：

```
数据呈现方式：
  1) flask_dir_browser.py — 本地部署，Web 方式浏览
  2) Git 提交到 GitHub — 远程浏览
```

**关键约束**：
- 目录结构清晰，导航完善
- 索引文件完整（index.md + log.md）
- 交叉链接有效

---

## 4. 模块需求

### 4.1 知识库模块

| 模块 | 路径 | 说明 | 优先级 |
|:-----|:-----|:------|:------:|
| 调研跟踪 | `knowledge/01_survey/` | AI 应用/框架/大模型/集群训练/智算方案等 | P0 |
| 研发 | `knowledge/02_rd/` | 服务器硬件设计/全栈分析/软件技术/生产制造等 | P0 |
| AI 技术原理 | `knowledge/03_AI/` | 大模型原理/Agent/GPU 设计/RAG 等 | P0 |
| 工具与行业 | `knowledge/05_tools/` | AI 工具/Git/Go/数据处理/运维 | P0 |
| 行业调研跟踪 | `knowledge/07_industry-research/` | 行业专题研究报告 | P0 |
| 个人 | `knowledge/04_person/` | 企业管理/职业发展/冲突处理等 | P1 |
| 方法论 | `knowledge/methodology/` | 创造手法/分析方法论/架构验证 | P1 |
| 概念原理 | `knowledge/concepts/` | AI 能力边界/系统分析框架/质量工程 | P1 |

### 4.2 技能系统模块

Skills 分为以下几类（当前共 125 个，含 3 个已废弃）：

| 类别 | 典型技能 | 数量 |
|:-----|:---------|:----:|
| 知识管理 | knowledge-wiki, web-archive, depth-completer, doc-reviewer | ~12 |
| 调研分析 | light-literature-search, mckinsey-research, industry-insight, competitor-analysis | ~10 |
| 论文辅助 | light-paper-drafting, light-paper-polishing, light-review-rebuttal, light-venue-matching | ~10 |
| 项目管理 | light-memory-pm, light-orchestrator, session-keeper, weekly-report-generator | ~8 |
| 前端设计 | light-frontend-design, frontend-design | ~4 |
| 后端编码 | light-backend-coding, light-system-design | ~6 |
| 数据处理 | light-data-engineering, light-result-analysis | ~4 |
| 文档生成 | docx, pptx, pdf, xlsx, light-slides, light-typesetting | ~10 |
| 竞争分析 | server-competitor-analysis, competitor-analysis | ~4 |
| 质量审查 | light-self-review, light-research-ethics, constraint-verifier, markdown-format-standards | ~8 |
| 其他 | 每日新闻/天气/娱乐/工具等 | ~42 |

### 4.3 脚本系统模块

| 类别 | 脚本 | 说明 |
|:-----|:-----|:------|
| 同步检查 | knowledge-sync-optimizer.py | 四阶段健康检查 |
| 知识审计 | 链接检查/格式检查/索引重建 | 知识库完整性保障 |
| 数据转换 | 多格式→Markdown | 格式统一 |
| 辅助工具 | 文件批量处理/目录扫描 | 日常运维 |
| Skills 联动 | 通过 Skills 调用脚本 | 双引擎协作 |

### 4.4 配套系统模块

| 模块 | 文件/路径 | 说明 |
|:-----|:----------|:------|
| Agent 身份 | AGENT.md | 人格、行为准则、自检清单 |
| 用户身份 | USER.md | 用户领域/偏好/质量标准 |
| 工作规则 | RULE.md | 文件铁律/存储规则/指令优先级 |
| 长期记忆 | MEMORY.md | 核心原则/方法论/重要洞察 |
| 每日记忆 | memory/YYYY-MM-DD.md | 当天进展/讨论记录 |
| 定时任务 | Scheduler（38 个任务） | 定时调度框架 |
| 渠道框架 | Feishu 等 | Agent 交互渠道 |

---

## 5. 配套系统需求

### 5.1 AI 配套身份文件

| 文件 | 更新频率 | 内容 |
|:-----|:--------:|:-----|
| AGENT.md | 季更 | Agent 人格/行为准则/协作模式/自检清单 |
| USER.md | 年更 | 用户身份/领域/工作风格/质量标准 |
| RULE.md | 季更 | 工作空间规则/文件铁律/存储规则/指令优先级 |
| MEMORY.md | 月更 | 核心原则/方法论/重要洞察/行业趋势 |

### 5.2 记忆系统

| 类型 | 位置 | 变化频率 | 内容 |
|:-----|:-----|:--------:|:-----|
| 长期记忆 | MEMORY.md | 月更 | 核心原则/方法论/重要决策 |
| 每日记忆 | memory/YYYY-MM-DD.md | 日更 | 当天进展/讨论/决策 |
| 知识记忆 | knowledge/ | 不定 | 结构化知识 |

### 5.3 定时任务系统

Scheduler 当前管理 38 个任务（32 个日追踪 + 6 个周报表），包括：
- 每周知识库周报生成
- 知识库同步优化检查
- 行业调研刷新
- 记忆整理与归档

### 5.4 渠道框架

当前渠道：
- **飞书（Feishu）**：主要交互渠道
- 支持 Agent 对话、工具调用、知识查询

### 5.5 资产清单与优化体系

| 资产 | 规模 | 分类 | 管理方式 | 优化需求 |
|:-----|:----:|:-----|:---------|:---------|
| **Scripts 脚本** | 154 个文件 | autokb(7) / check(13) / tools(7) / git(2) / intent_analysis(5) / backup(80+) / 根级(18+) | `scripts/` 目录 + 分类子目录 + 根级别名 | SR-026 (清单) / SR-028 (backup清理) |
| **Skills 技能** | 125（含 3 废弃） | custom(80) / clawhub(13) / cowhub(9) / github(8) / linkai(6) | `skills/` 目录 + `skills_config.json` | SR-027 (清单) / SR-029 (闲置清理) |
| **映射关系** | 2 张映射表 | `scripts/README.md`(6类归纳) + `scripts/skills-scripts-mapping.md`(技能→脚本) | 手写维护 | SR-030 (自动同步) |

#### 5.5.1 Scripts 资产按功能分类

| 分组 | 数量 | 核心脚本 | 用途 |
|:-----|:----:|:---------|:------|
| `autokb/` 导入管线 | 7 | `pipeline.py`/`discover.py`/`classify.py`/`importer.py`/`index_updater.py` | import→knowledge 端到端管线 |
| `check/` 质量检查 | 13 | `knowledge-normalizer.py`/`link-validator.py`/`md-format.py`/`analyze-index-coverage.py` | 知识库健康度/格式/链接/结构 |
| `tools/` 独立工具 | 7 | `html-to-markdown.py`/`chromedriver-setup.py`/`classify-questions.py` | 格式转换/浏览器配置/数据分析 |
| `git/` 版本控制 | 2 | `git-pull-robust.py`/`git-push-robust.py` | Git 操作自动化 |
| `intent_analysis/` 意图分析 | 5 | `main.py`/`extract_user_questions.py`/`analyze_topic_boundaries.py` | 对话记录语义分析 |
| `backup/` 历史备份 | ~80 | doubao(50+)/chrome-test(20)/html-classes(17)/other(7) | 历史试验脚本，待评估 |
| 根级别名 | 15+ | `knowledge-sync-optimizer.py`/`batch_enhance_reports.py`/`convert-to-markdown.py` | 独立功能 + 向后兼容别名 |

#### 5.5.2 Skills 资产按来源分类

| 来源 | 数量 | 说明 | 典型技能 |
|:-----|:----:|:------|:---------|
| **custom** (手写) | 80 | 通过对话逐步封装，核心技能 | `deep-tech-writer`/`knowledge-wiki`/`web-archive`/`doc-reviewer` |
| **clawhub** (导入) | 13 | 从 GitHub 开源项目封装 | `mckinsey-research`/`notion`/`apple-reminders` |
| **cowhub** (生成) | 9 | 系统从对话中自动提取模式生成 | `knowledge-sync`/`light-memory-pm`/`session-keeper` |
| **github** (直接) | 8 | GitHub 仓库直接引用 | `Architecture`/`frontend-design`/`karpathy-guidelines` |
| **linkai** (插件) | 6 | LinkAI 平台插件 | `plugin-antv`/`plugin-chart`/`plugin-bilibili-search` |

#### 5.5.3 Backup 脚本资产明细

| 子目录 | 文件数 | 说明 | 处理建议 |
|:------|:------:|:------|:---------|
| `backup/doubao/` | 50+ | 豆包导出脚本各版本迭代 | 核心功能 → `doubao-share` 已覆盖；废弃版本 → 标注归档 |
| `backup/chrome-test/` | 20 | ChromeDriver 测试与配置 | 核心功能 → `tools/chromedriver-setup.py` 已提炼；保留典型供参考 |
| `backup/html-classes/` | 17 | HTML→Markdown 解析迭代 | 核心功能 → `tools/html-to-markdown.py` 已提炼；其余标注版本 |
| `backup/other/` | 7 | 其他独立脚本 | 评估后分别归档或迁移 |

#### 5.5.4 Skills 闲置清理建议

| 分级 | 标准 | 数量(估算) | 处理方式 |
|:-----|:------|:----------:|:---------|
| **活跃** | 日常/每周使用 | ~40 | 保持，定期维护 |
| **低频** | 月度或以下使用 | ~30 | 评估是否合并到相关技能或标注"低频" |
| **待激活** | 需配置环境变量 | ~11 | 补充 API Key 后激活 |
| **未就绪** | 缺少运行时依赖 | ~4 | 标注状态，待环境就绪 |

---

### 5.6 Skills 和 Scripts 质量验证体系（需求规格）

> **交叉参考**: 本文定义质量验证的**需求规格**（做什么）——列出验证维度和需求。对应的**设计侧验证架构**（怎么做）见 `design-001-system-architecture.md §7.4`（Skills 质量验证）和 `§8.3`（Scripts 质量验证）。SR-031~033 → AR-QSV-001~006 为映射链路。
>
> **职责分工**: sr-001 §5.6 = 需求规格（"要验证什么"） | design-001 §7.4/§8.3 = 设计方案（"怎么验证"） | 附录 D = 速查表（仅汇总，不重复定义）

| 需求 | SR | 说明 | 验证维度 | 验证频率 | 优先级 |
|:-----|:---|:------|:---------|:--------:|:------:|
| Skills 功能可用性验证 | SR-031 | 定期扫描所有 Skills 的可用性 | ① SKILL.md 结构完整性 ② 内部脚本可执行性 ③ 引用的 knowledge 路径有效性 ④ 依赖的工具链可用 | 每周（全量）/ 每日（增量） | P1 |
| Scripts 功能可用性验证 | SR-032 | 定期对脚本做语法 + 基础运行测试 | ① Python 语法（`py_compile`） ② `--help` 参数返回正常 ③ 引用的路径/文件存在 ④ 关键功能路径 dry-run | 每月（全量）/ 每周（增量） | P1 |
| Knowledge 变化自适应 | SR-033 | 当 knowledge 路径变化时自动检测引用失效 | ① skills 中引用的 `knowledge/` 路径 ② scripts 中引用的 `knowledge/` 路径 ③ `scripts/skills-scripts-mapping.md` 中的路径 ④ `skills/` 内脚本引用的 knowledge 路径 | knowledge 变更时触发 | P1 |

**验证架构**:

```text
┌─────────────────────────────────────────────────────────────────┐
│                     Skills/Scripts 质量验证流水线                 │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 定时触发      │  │ 变更触发      │  │ 手动触发      │          │
│  │ Scheduler    │  │ knowledge/   │  │ 用户请求     │          │
│  │ (每周/每月)   │  │ 目录变更      │  │              │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └────────┬────────┴────────┬────────┘                   │
│                  │                 │                            │
│                  ▼                 ▼                            │
│        ┌─────────────────────────────────────┐                 │
│        │      验证执行引擎                      │                 │
│        │                                      │                 │
│        │  ┌─────────────────────────────┐    │                 │
│        │  │ validate-skills.py          │    │                 │
│        │  │  - SKILL.md 解析与完整性    │    │                 │
│        │  │  - 内部脚本路径验证          │    │                 │
│        │  │  - knowledge 路径交叉检查    │    │                 │
│        │  │  - 依赖工具链可用性          │    │                 │
│        │  └───────────┬─────────────────┘    │                 │
│        │              │                       │                 │
│        │  ┌───────────▼─────────────────┐    │                 │
│        │  │ validate-scripts.py         │    │                 │
│        │  │  - Python 语法编译检查      │    │                 │
│        │  │  - --help 参数测试          │    │                 │
│        │  │  - 路径/文件存在性验证      │    │                 │
│        │  │  - 关键路径 dry-run        │    │                 │
│        │  └───────────┬─────────────────┘    │                 │
│        └──────────────┼─────────────────────┘                 │
│                       │                                        │
│                       ▼                                        │
│        ┌──────────────────────────────┐                       │
│        │  验证报告                    │                        │
│        │  validate-report-YYYY-MM-DD  │                        │
│        │  - 通过/失败/告警 统计       │                        │
│        │  - 失败详情（文件名+原因）    │                        │
│        │  - 路径失效清单（供修复）     │                        │
│        └──────────────────────────────┘                       │
│                       │                                        │
│                       ▼                                        │
│        ┌──────────────────────────────┐                       │
│        │  自动修复/告警               │                        │
│        │  - 路径失效 → 自动更新引用    │                       │
│        │  - 脚本语法错误 → 告警        │                       │
│        │  - Skills 不可用 → 标注状态   │                       │
│        └──────────────────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
```

**验证脚本**:

| 脚本 | 功能 | 验证内容 | 输出 |
|:-----|:------|:---------|:------|
| `validate-skills.py` | Skills 可用性扫描 | ① SKILL.md 是否包含必须字段（Description/Workflow） ② 内部 `scripts/` 下文件是否存在 ③ 引用 `knowledge/` 路径的 404 检测 ④ `skills_config.json` 状态一致性 | JSON 报告 + Markdown 摘要 |
| `validate-scripts.py` | Scripts 语法与路径验证 | ① Python 语法编译（`py_compile.compile`） ② 脚本 `--help` 返回非零吗 ③ 脚本中引用的文件/目录存在吗 ④ Shell 脚本语法（`bash -n`） | JSON 报告 + Markdown 摘要 |
| `track-knowledge-refs.py` | Skills/Scripts → Knowledge 引用跟踪 | ① 正则扫描 skills/*/SKILL.md 中 `knowledge/` 引用 ② 正则扫描 scripts/*.py 中 `knowledge/` 引用 ③ 与当前 knowledge/ 目录对比 ④ 输出失效清单 | 引用清单 + 失效报告 |

**验证调度**:

| 验证类型 | 触发方式 | 频率 | 执行脚本 |
|:---------|:---------|:----:|:---------|
| Skills 语法检查 | Scheduler 定时 | 每周一 02:00 | `validate-skills.py --mode=quick` |
| Skills 全量验证 | Scheduler 定时 | 每月 1 日 02:00 | `validate-skills.py --mode=full` |
| Scripts 语法检查 | Scheduler 定时 | 每月 1 日 03:00 | `validate-scripts.py --mode=syntax` |
| Scripts 路径验证 | Scheduler 定时 | 每月 1 日 03:30 | `validate-scripts.py --mode=paths` |
| Knowledge 引用跟踪 | knowledge/ 变更后自动 | knowledge 变更时 | `track-knowledge-refs.py` |
| 映射表一致性检查 | Scheduler 定时 | 每周一 04:00 | `validate-skills.py --mode=mapping` |

---

## 6. 后续优化需求

### 6.1 短期优化（P0 完善）

| SR | 需求 | 说明 |
|:---|:-----|:------|
| SR-025 | import 批量处理管线 | 自动发现 → 批量分析 → 去重分类 → 写入 discover |
| — | index 覆盖率补全 | 所有模块确保 index.md + log.md 完整 |

### 6.2 中期优化（P1 推进）

| SR | 需求 | 说明 |
|:---|:-----|:------|
| SR-021 | RAG 知识集成 | 知识库向量化检索，支持语义搜索 |
| SR-022 | 可信 AI 输出体系 | 增强来源验证、冲突检测、不确定性标注 |
| SR-023 | 采集过程增强 | 公众号/网站采集整合到系统内，打通全链路 |
| SR-024 | 自演进能力 | 系统自动识别短板、优化策略、迭代进化 |
| SR-031 | Skills 功能可用性验证 | 定期扫描 Skills 可用性，含 SKILL.md 完整性、脚本依赖、路径有效性 |
| SR-032 | Scripts 功能可用性验证 | 定期对脚本做语法检查 + 基础运行测试 + 路径有效性验证 |
| SR-033 | Knowledge 变化自适应 | knowledge 路径变更时自动检测 skills/scripts 引用失效并提示修复 |

### 6.3 import 流程缺陷与处理方案

> **现状审计日期**: 2026-07-21
>
> `import/` 目录当前承载 **18,895 个文件**（7 个子目录），自动化管线 `scripts/autokb/` 已搭建（discover→classify→import→index_updater 四步），但实际规模执行极度不足——台账显示仅处理了 **1/7,400+** 的 Markdown 文件，`discover/` 输出目录实际为空。

#### 6.3.1 问题一：导入手工化（SR-034）

**现象**:
- Web 采集（博客园爬虫 `1,953` 文件、微信文章 `619` 文件）通过外部工具完成，结果手动复制到 import/，无自动采集管线
- autokb pipeline 存在但需手动触发，未接入 Scheduler 定时任务
- 无增量检测机制——每次需要人工判断哪些是新文件

**根因**:
- 采集与导入脱节：采集阶段用外部工具（爬虫/手工下载），导入阶段用 AI 技能，中间需人工转接
- pipeline 设计为一次性批量工具，未适配"持续增量导入"场景
- 无变更检测（无文件哈希缓存、无最后处理时间记录）

**处理方案（P1，按优先级排序）**:

| 步 | 动作 | 产出 | 前置条件 |
|:--:|:-----|:-----|:---------|
| ① | `import/` 下建立 `.import_state/` 隐藏目录，记录每个文件的处理时间戳与哈希，支持增量检测 | 增量导入基础 | — |
| ② | `run_pipeline.py` 新增 `--incremental` 模式，仅处理 `.import_state/` 中未记录或已变更的文件 | 增量导入能力 | ① |
| ③ | autokb pipeline 注册到 Scheduler，设定每日 02:00 增量扫描 | 定时自动导入 | ② |
| ④ | 将 cnblogs 爬虫脚本（`scripts/runoob_tools/crawl_runoob.py` 模式）归纳为泛化 web 采集脚本 `scripts/tools/web-collector.py`，支持通用站点配置式采集 | 集成化采集能力 | — |
| ⑤ | Scheduler 注册 web 采集任务，按配置的站点列表定时采集→自动存入 import/ 对应子目录 | 端到端自动采集 | ④ |

---

#### 6.3.2 问题二：海量非 Markdown 数据未转化（SR-035）

**现象**:
- `import/` 下 **4,116 个非 Markdown 文件**未被转化，按类型分布：

| 文件类型 | 数量 | 现有转化工具 | 转化难度 |
|:---------|:----:|:------------|:--------:|
| `.xml` | 1,179 | 有（`html-to-markdown.py` 可扩展） | ⭐⭐ |
| `.hpp` / `.cpp` | 1,247 | 代码文件→按注释提取注释+签名即可 | ⭐ |
| `.json` | 854 | 结构化数据→按 schema 生成摘要 Markdown | ⭐⭐ |
| `.docx` | 222 | 有（`markitdown`） | ⭐ |
| `.pdf` | 44 | 有（`markitdown` + PaddleOCR） | ⭐⭐ |
| `.xlsx` | 17 | 有（`markitdown`） | ⭐ |
| `.pptx` | 7 | 有（`markitdown`） | ⭐ |
| `.jpg/.png` | 56 | 有（`vision` + EXIF） | ⭐⭐⭐ |
| 其他 | 490+ | 逐类评估 | 不定 |

> **注**: 但更根本的问题是——大量 `.md` 文件（14,779 个）本身已含有被 Processing 脚本处理过的标记和数据，其中 `work/`（7,401 文件）和 `cnblogs/`（1,953 文件）内容碎片化严重，**转化只是第一步，真正的难点在后续的内容甄别与提炼**。

**根因**:
- 初始设计采用"先收后理"策略，优先保证收集速度，再逐步处理
- markitdown + 各转化工具虽已就绪，但缺一个**统一调度器**来按类型路由到对应转换器
- 无批次跟踪机制，不能区分"已尝试转化但失败"和"从未尝试转化"

**处理方案（P1，按优先级排序）**:

| 步 | 动作 | 产出 | 前置条件 |
|:--:|:-----|:-----|:---------|
| ① | 编写 `batch-convert-import.py`：扫描 import/ 非 `.md` 文件，按扩展名路由到对应转换器，输出同名 `.md` 文件到 `import/` 同目录并标记 `_converted` | 批量转化脚本 | — |
| ② | 建立 `import/.convert_state/` 记录转化状态（成功/失败/跳过），支持断点续传+增量转化 | 转化状态追踪 | ① |
| ③ | `work/` 目录重点分析：7,401 个文件中含大量个人工作笔记/Processing 输出，需先分类再决定是否值得转化 | work/ 目录处理方案 | ①+② |
| ④ | 将 `batch-convert-import.py` 接到 Scheduler（每月 1 日 01:00），持续处理新导入的非 Markdown 文件 | 定时增量转化 | ② |

---

#### 6.3.3 问题三：import 内容未充分利用（SR-036）

**现象**:
- `discover/` 目录输出为**空**——Pipeline 的 discover→classify→import 链路从未规模执行
- 台账 `import_manifest.md` 中 7 个批次（B1-B7）仅 B1 处理了 **1/826** 文件，其余批次**零处理**
- 当前知识库中有 632 个文件在台账创建后新增，但均通过**人工+AI 对话**逐个处理，非管线批量产出
- import/ 内容未经系统化的去重、分类、提炼——同一主题可能分散在多个文件中未被合并

**根因**:
- autokb pipeline 设计为"先技术搭建，后业务运营"模式——管线代码写了，但**没有投入运营资源**来批量执行
- 处理一个 import 文件需要 AI 多次交互（分析→提炼→写文档→更新索引），在对话模式下单文件处理成本高，没有规模化的动力
- 缺乏优先级信号——18,895 个文件中哪些是高质量、值得优先处理的，无从判断
- 台账维护与管线执行脱节——`import_manifest.md` 是手工维护，不是 pipeline 自动输出

**处理方案（P0，import 管线核心价值在此）**:

| 步 | 动作 | 产出 | 前置条件 |
|:--:|:-----|:-----|:---------|
| ① | **优先级排序**：先对 7 个来源目录做快速质量评估（抽样分析），输出每个目录的"价值/噪声比"评级，确定优先处理顺序（建议：doubao→server→webchat→md→work→千问→cnblogs） | 处理优先级清单 | — |
| ② | **管线批量执行**：按优先级对 top-3 目录（doubao 826 + server 3,783 + webchat 619 ≈ 5,228 文件）启动批量处理 pipeline：`discover.py → classify.py → discover/` | 5,000+ 文件完成初步分类 | ① |
| ③ | **AI 批量提炼**：编写 `batch-analyze-discover.py` 对 discover/ 中已分类文件执行批量 AI 分析——每批 10-20 个文件，输出摘要+关键信息+主题标签+去重建议 | 提炼中间产物 | ② |
| ④ | **人工审核窗口**：提炼产物以 Markdown 报告形式输出，供逐批人工审核→审核通过后导入 knowledge/ | 人工审核流程 | ③ |
| ⑤ | **台账自动化**：`import_manifest.md` 改为 pipeline 自动生成/更新，跟踪每批次已处理/待处理/跳过/失败状态 | 台账自动同步 | ② |
| ⑥ | **跟踪闭环**：添加"from_import"标记到所有源自 import 的知识文档，便于溯源 | 溯源体系 | ④ |

**预期产出（完成 B1+B3+B4 后）**:

| 指标 | 当前 | 目标 |
|:-----|:----:|:----:|
| discover/ 文件数 | 0 (空) | 2,000+（提炼后去重合并预估） |
| 已处理 import 文件数 | 1 | 5,000+ |
| 知识文档产出（源自 import） | ~632（人工） | 400-600（管线批量） |
| 处理覆盖率 | 0.005% | 26% |

---

### 6.4 长期愿景（P2 探索）

| 需求 | 说明 |
|:-----|:------|
| 多 Agent 协作 | 多个专业 Agent 分工协作 |
| 知识图谱构建 | 从结构化知识过渡到知识图谱 |
| 自动报表生成 | 基于知识库自动生成行业分析报告 |

---

## 附录 A：SR 索引

| SR 编号 | 标题 | 阶段 | 优先级 | 状态 |
|:--------|:-----|:----:|:------:|:----:|
| SR-001 | 本地 Markdown 批量导入 | Phase 1 | P0 | ✅ |
| SR-002 | 非 Markdown 文件转换导入 | Phase 1 | P0 | ⚠️ **部分实现** |
| SR-003 | 公众号/网站采集导入（外部工具，未整合） | Phase 1 | P1 | 🚧 |
| SR-004 | 工程文件夹导入 projects/ | Phase 1 | P1 | ✅ |
| SR-005 | import/ 素材库统一管理 | Phase 1 | P0 | ⚠️ **台账过时** |
| SR-006 | AI 批量汇总分析 import 素材 | Phase 2 | P0 | ⚠️ **管线就绪但未规模执行** |
| SR-007 | AI 提炼输出到 discover/ | Phase 2 | P0 | ⚠️ **discover/ 实际为空** |
| SR-008 | 网站信息 AI 生成笔记入知识库 | Phase 3 | P0 | ✅ |
| SR-009 | 外部 AI 对话导入知识库 | Phase 3 | P1 | ✅ |
| SR-010 | 定时 AI 行业调研 | Phase 3 | P0 | ✅ |
| SR-011 | 定期 AI 系统报告生成 | Phase 3 | P0 | ✅ |
| SR-012 | 日常对话主题生成 | Phase 3 | P0 | ✅ |
| SR-013 | Skills 和 Scripts 系统化管理 | Phase 3 | P0 | ✅ |
| SR-014 | 本地 Web 浏览 | Phase 4 | P0 | ✅ |
| SR-015 | Git/GitHub 远程浏览 | Phase 4 | P0 | ✅ |
| SR-016 | AI 配套身份文件体系 | 配套 | P0 | ✅ |
| SR-017 | 每日记忆系统 | 配套 | P0 | ✅ |
| SR-018 | Skills 和 Scripts 功能体系 | 配套 | P0 | ✅ |
| SR-019 | 定时任务处理框架 | 配套 | P0 | ✅ |
| SR-020 | 渠道框架 | 配套 | P0 | ✅ |
| SR-021 | RAG 知识集成 | 后续 | P1 | 📋 |
| SR-022 | 可信 AI 输出体系建设 | 后续 | P1 | 🚧 |
| SR-023 | 采集过程增强 | 后续 | P1 | 📋 |
| SR-024 | 系统自演进能力 | 全局 | P1 | 🚧 |
| SR-025 | import 批量处理管线 | Phase 2 | P1 | 📋 |
| SR-026 | **Scripts 资产清单管理**: 对 `scripts/` 154 个文件建立完整资产清单，按功能分类（autokb/check/tools/git/intent_analysis/根级），含用途说明与优化方案 | 配套 | P1 | ✅ |
| SR-027 | **Skills 资产清单管理**: 对 `skills/` 125 个技能（含 3 废弃）建立完整资产清单，按来源/功能/启用状态分类，含用途说明与优化方案 | 配套 | P1 | ✅ |
| SR-028 | **Backup 脚本清理与归档**: `scripts/backup/` 下 80+ 个历史脚本（doubao/chrome-test/html-classes/other），需评估：有价值→迁移到正式目录；已废弃→标注归档；重复→清理 | 配套 | P2 | 📋 |
| SR-029 | **Skills 闲置清理与优化**: 扫描技能按使用频率分级（活跃/低频/待激活/未就绪），低频技能评估是否合并或移除，待激活技能补充环境变量，未就绪技能标注状态 | 全局 | P2 | 📋 |
| SR-030 | **Skills ↔ Scripts 映射维护**: 保持 `scripts/skills-scripts-mapping.md` 与 `scripts/README.md` 两张映射表与实际资产同步（技能变更时自动更新映射表） | 配套 | P1 | 🚧 |
| SR-031 | **Skills 功能可用性定期验证**: 定期（每周/每月）扫描所有 Skills，验证每个技能是否能正常触发、SKILL.md 是否完整、依赖的脚本是否可用、引用的 knowledge 路径是否有效 | 配套 | P1 | 📋 |
| SR-032 | **Scripts 功能可用性定期验证**: 定期对 `scripts/` 下所有脚本执行语法检查、基础运行测试（dry-run / --help）、关键路径有效性验证（引用的文件/目录是否存在），确保脚本能正常执行 | 配套 | P1 | 📋 |
| SR-033 | **Skills/Scripts → Knowledge 路径自适应**: 当 knowledge 目录结构变更（文件移动/重命名/删除）时，自动检测并提示 skills/scripts 中引用的 knowledge 路径是否失效，支持批量更新引用路径 | 全局 | P1 | 📋 |
| SR-034 | **导入流程自动化集成**: 解决导入手工化问题——① 将 web 采集(cnblogs/公众号等)整合到系统内脚本管线，不再依赖外部操作 ② 将 autokb pipeline 挂接到 Scheduler 定时执行 ③ 支持增量导入（仅处理新增/变更文件）④ 导入完成后自动触发 AI 分析 | Phase 1 | P1 | 📋 |
| SR-035 | **海量非 Markdown 数据批量转化**: 对 import/ 下 4,000+ 非 Markdown 文件（XML/DOCX/PDF/JSON/HPP/CPP/图片等）进行分类识别，按类型调用对应转换器批量转为 Markdown，建立"已转化完成"标记避免重复处理 | Phase 1 | P1 | 📋 |
| SR-036 | **import 内容深度利用管线**: 解决 import 内容利用不充分问题——① 对已转换 Markdown 素材执行批量 AI 分析（摘要/主题分类/关键信息提取）② 自动去重合并（同一主题多文件合并）③ 提炼结果分类写入 discover/ ④ 人工审核后导入 knowledge/ ⑤ 跟踪并更新处理台账 | Phase 2 | P0 | 📋 |

---

> **修订记录**
>
> | 日期 | 版本 | 变更说明 |
> |:-----|:-----|:---------|
> | 2026-07-21 | v1.1 | 新增 SR-026~030（Scripts/Skills 资产清单与优化、Backup清理、映射表维护）及 §5.5 资产清单与优化体系 |
> | 2026-07-21 | **v1.2** | 新增 SR-031~033（Skills/Scripts 质量验证体系、Knowledge 自适应）+ §5.6 质量验证体系（含验证架构图、3个验证脚本设计、6个调度任务） |
> | 2026-07-21 | **v1.3** | 新增 SR-034~036（导入自动化/非Markdown批量转化/内容深度利用）+ §6.3 import 流程缺陷与处理方案（含三个问题的现象、根因、分步处理方案、预期产出指标）；修正 SR-002/SR-005/SR-006/SR-007 状态为 ⚠️（实际未完成） |
