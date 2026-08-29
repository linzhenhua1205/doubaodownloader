# 🐄 Cow — AI 驱动的自演进知识库系统

> **版本**: v4.2 | **更新**: 2026-08-16
>
> **核心理念**: 工具如仪器，用好靠功底。AI 搭骨架，人做判断。
>
> **工程定位（三位一体）**:
> 1. 🧪 **AI × 知识管理探索** — 验证 AI 在知识组织/提炼/分析/治理中的创造性应用与边界约束
> 2. 🏭 **服务器"产销研"知识库** — 面向服务器/AI 基础设施产品的研发-市场-研究全链路知识沉淀
> 3. 📒 **个人（家庭）笔记** — 日常生活、家庭事务与个人成长记录
>
> **定位原则**: AI 探索是**手段**，业务知识沉淀与个人记录是**主线**——探索服务于主线，投入可控、不喧宾夺主（工具建设投入占比超 40% 即亚健康，需主动收敛）。
>
> ⚠️ **系统健康告警（2026-08-16）**: 向量索引 `memory/long-term/index.db`（2.2GB）丢失，`memory_search` 语义检索不可用；无异地备份（详见 [`spec/sr-010-system-attention-points.md`](spec/sr-010-system-attention-points.md) F12/F14）。磁盘已用 54.9G / 可用 410.8G（告警已解除）。

---

## 📊 当前状态概览

| 指标 | 数值 | 说明 |
|:----|:----:|:-----|
| 📚 **知识库文件** | **3,693** 个 | `knowledge/` 结构化知识（MD，122 MB） |
| 🧩 **技能系统** | **104 本地 + 33 外部 = 137** | 可复用 AI 能力包（详见 [`skills/README.md`](skills/README.md)） |
| ⚙️ **自动化脚本** | **563 个** | `scripts/` Python 工具链（含 check/autokb/tools 等分组） |
| 📥 **原始素材** | **21,326 个** | `import/` 素材仓（1.16 GB） |
| 🔍 **二次提炼** | **9,674 个** | `discover/` AI 分析产物（1.35 GB） |
| 🧠 **向量索引库** | **丢失 ⚠️** | `memory/long-term/index.db` 不存在，语义检索不可用 |
| 🗂️ **会话记录** | **591 个文件** | `conversation-log/`（含会话/用户问题导出，54.5 MB） |
| 📋 **设计文档** | **62 个** | `spec/` 六类型（sr/ar/design/std/meth/audit，2.1 MB） |
| ⏰ **定时任务** | **49 个** | 24 领域日追踪 + 日报/周报/月报/专项（详见 [`spec/design-011-scheduled-tasks-system-design.md`](spec/design-011-scheduled-tasks-system-design.md)） |
| 🔄 **Git 提交** | **1,418 次** | 主分支（[AI] 自动提交为主） |
| 💾 **总工作空间** | **5.27 GB** | 72,614 文件；磁盘已用 54.9G / 可用 410.8G |

---

## 📑 目录

1. [理念与目标](#1-理念与目标)
2. [总体架构](#2-总体架构)
3. [数据流（四阶段闭环）](#3-数据流四阶段闭环)
4. [数据访问与同步方式](#4-数据访问与同步方式)
5. [用户操作方式（Skills/Scripts/路径全映射）](#5-用户操作方式skillsscripts路径全映射)
6. [工程设计参考](#6-工程设计参考)
7. [模块介绍](#7-模块介绍)
8. [Skills 系统（按任务类型组织）](#8-skills-系统按任务类型组织)
9. [脚本系统（按任务支持分组的 CLI 工具链）](#9-脚本系统按任务支持分组的-cli-工具链)
10. [常用命令速查（按任务类型）](#10-常用命令速查按任务类型)
11. [定时任务体系](#11-定时任务体系)
12. [约束说明](#12-约束说明)
13. [后续待办](#13-后续待办)

---

## 1. 理念与目标

### 1.0 定位模型（三位一体）

| 定位 | 内涵 | 对应模块 | 代表产出 |
|:-----|:-----|:---------|:---------|
| 🧪 **AI × 知识管理探索** | 验证 AI 在知识组织/提炼/分析/治理中的创造性应用与幻觉约束，沉淀可复用方法论 | `skills/` `scripts/` `spec/` `scheduler/` `discover/` | 137 Skills · 563 脚本 · 62 设计文档 · 定时调研流水线 |
| 🏭 **服务器"产销研"知识库** | 面向服务器/AI 基础设施产品的**研发-市场-研究**全链路知识 | `knowledge/01_survey/` `02_rd/` `03_AI/` `07_industry-research/` | 超节点/互连/800V HVDC 深度分析 · 行业追踪 · 竞品分析 |
| 📒 **个人（家庭）笔记** | 日常生活、家庭事务、个人成长与长期记忆 | `memory/` `knowledge/04_person/` `conversation-log/` | 每日记忆 · 周报 · 会话档案 |

> **主线与手段的边界**（基于本系统实证经验）:
> - **主线（占产出主体）**: 产销研知识沉淀 + 个人记录——这是系统存在的目的
> - **手段（服务于主线）**: AI 探索与工具建设——只建解决实际问题的能力，不为"追新"而建
> - **投入红线**: 工具建设占比超 40% 即进入亚健康，需主动干预收敛

### 1.1 核心理念

```
三论指导 × AI驱动 × 四阶段闭环
```

- **MECE 原则**: 知识分类相互独立、完全穷尽，确保体系无重复无遗漏
- **第一性原理**: 回归物理极限/经济规律/信息论，不盲从共识
- **辩证法**: SSOT 约束适度，在规范与灵活之间动态平衡

### 1.2 核心目标

| 目标 | 描述 | 当前状态 |
|:-----|:------|:--------:|
| 🎯 **知识体系化** | 从数据到知识的端到端自动化闭环 | ✅ 基础闭环 |
| 🔄 **自演进能力** | 系统自动识别短板、优化策略、迭代进化 | ✅ 基础版（evolver/skill-evolver + 每日 23:50 蒸馏） |
| 🤖 **AI 创造性应用** | 充分发挥 AI 在知识组织/提炼/分析中的创造力 | ✅ 核心能力 |
| 🛡️ **幻觉约束** | 多源交叉验证 + 来源追溯 + 批判性使用 | ✅ 已落地 |
| 📊 **可信输出** | 每条断言可追溯、每个数据可验证 | ✅ 质量内建（sr-007 八级质量门禁） |
| 🧭 **业务价值优先** | AI 探索服务于产销研知识沉淀与个人记录，主线清晰、投入可控 | ✅ 定位收敛 |

### 1.3 能力雷达

```text
知识体系化   ██████████░░  90%
自动采集     █████████░░░  85%
深度分析     ██████████░░  90%
质量审查     █████████░░░  85%
自演进       ██████░░░░░░  60%
RAG 集成     ████░░░░░░░░  40%  (向量索引丢失，需重建)
```

---

## 2. 总体架构

### 2.1 四环数据流架构

整个体系以 **数据收集 → 数据加工 → 数据优化 → 数据使用** 四阶段闭环为骨架，知识库（`knowledge/`）为圆心，Skills + Scripts 双引擎驱动。

```text
┌─────────────────────────────────────────────────────────────────────┐
│                        用户操作层                                     │
│  📥投喂文件  💬分享链接  🔍发起调研  📝对话存档  🗣️技术讨论  🧠定时任务│
└───────────────────────────┬─────────────────────────────────────────┘
                             │
┌───────────────────────────┼─────────────────────────────────────────┐
│          ┌────────────────▼────────────────┐                        │
│          │  Phase 1: 数据收集               │                        │
│          │  ┌──────────┐ ┌───────────────┐ │                        │
│          │  │ import/  │ │ projects/     │ │                        │
│          │  │ 素材仓    │ │ 工程代码      │ │                        │
│          │  │ 21,326   │ │ AI工程等      │ │                        │
│          │  └─────┬────┘ └───────┬───────┘ │                        │
│          │        │              │          │                        │
│          │  本地MD/非MD/公众号/网站/对话     │                        │
│          └────────┼──────────────┼──────────┘                        │
│                   │              │                                   │
│          ┌────────▼──────────────▼──────────┐                        │
│          │  Phase 2: 数据加工               │                        │
│          │  ┌────────────────────────────┐  │                        │
│          │  │  discover/                 │  │                        │
│          │  │  AI批量汇总·提炼·去重·分类  │  │                        │
│          │  │  9,674 个分析产物          │  │                        │
│          │  └────────────┬───────────────┘  │                        │
│          └───────────────┼──────────────────┘                        │
│                          │                                           │
│          ┌───────────────▼──────────────────┐                        │
│          │  Phase 3: 数据优化               │                        │
│          │  ┌────────────────────────────┐  │                        │
│          │  │  🧠  knowledge/           │  │                        │
│          │  │  核心知识库                │  │                        │
│          │  │  3,693 文件 / 122 MB       │  │                        │
│          │  └────────┬────────┬──────────┘  │                        │
│          │           │        │             │                        │
│          │    ┌──────▼──┐ ┌──▼───────┐     │                        │
│          │    │ skills/ │ │ scripts/ │     │                        │
│          │    │ 技能系统 │ │ 自动化脚本 │     │                        │
│          │    │ 137 个  │ │ 563 个   │     │                        │
│          │    └──────┬──┘ └───┬──────┘     │                        │
│          └───────────┼────────┼────────────┘                        │
│                      │        │                                     │
│          ┌───────────▼────────▼────────────┐                        │
│          │  Phase 4: 数据使用               │                        │
│          │  ┌──────────┐ ┌──────────────┐  │                        │
│          │  │ Git→GitHub│ │ FlaskBrowser│  │                        │
│          │  │ 版本同步  │ │ Web浏览     │  │                        │
│          │  └──────────┘ └──────────────┘  │                        │
│          └─────────────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 系统组件关系

```text
┌──────────────────────────────────────────────────────────────┐
│                     Agent 引擎层                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Skills   │  │ Memory   │  │ Scheduler│  │ KnowledgeBase│  │
│  │ 137个    │  │ 三层记忆  │  │ 49个任务  │  │ 知识库引擎   │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  约束体系: SSOT · 多源三角验证 · 批判性使用 · 索引同步   │ │
│  └──────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│                     数据持久化层                                │
│  ┌──────────────────┐  ┌──────────────────┐                  │
│  │  Markdown + Git  │  │  SQLite(index.db)│                  │
│  │  knowledge/      │  │  向量/会话持久化  │  ⚠️ 索引丢失     │
│  └──────────────────┘  └──────────────────┘                  │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. 数据流（四阶段闭环）

### 3.1 阶段总览

```text
输入                             加工                         输出
────                              ──                          ──
                                    ┌────────────┐
本地 .md 文件 ──────────────────▶ │ import/    │
本地非 .md 文件 ── markitdown ──▶ │ 素材仓     │
公众号/网站 ── 采集脚本 ────────▶ │ 21,326个   │
工程文件夹 ─────────────────────▶ │ projects/  │
                                    └──────┬─────┘
                                           │ AI批量分析
                                    ┌──────▼─────┐
                                    │ discover/  │── Phase 2: 数据加工
                                    │ 9,674个    │
                                    └──────┬─────┘
                                           │ AI深度加工
                                    ┌──────▼─────┐
                                    │ knowledge/ │── Phase 3: 数据优化
                                    │ 3,693 个   │
                                    └──────┬─────┘
                                           │ 呈现
                                    ┌──────▼─────┐
                                    │ Web浏览    │── Phase 4: 数据使用
                                    │ Git同步    │
                                    └────────────┘
```

### 3.2 各阶段详情

| 阶段 | 输入 → 处理 → 输出 | 对应 Skills | 对应 Scripts |
|:----:|:--------------------|:------------|:-------------|
| **Phase 1** 数据收集 | 文件/URL/对话 → 格式转换 → `import/` / `knowledge/` | `markdown-converter`, `web-archive`, `doubao-share`, `web-access` | `convert-to-markdown.py`, `import_files.py`, `dedup_import.py` |
| **Phase 2** 数据加工 | `import/` → AI 批量提炼 → `discover/` | `discover` | `discover/*.py`, `autokb/*.py` |
| **Phase 3** 数据优化 | `discover/` / 联网 → 深度分析 → `knowledge/` | `deep-tech-writer`, `knowledge-doc-writer`, `industry-insight`, `doc-reviewer` | `check/*.py`（质量门禁） |
| **Phase 4** 数据使用 | `knowledge/` → 浏览/同步/检索 | `knowledge-wiki`, `memory_search` | `flask_dir_browser.py`, `git/*-robust.py` |

---

## 4. 数据访问与同步方式

| 方式 | 工具 | 说明 | 启动方式 |
|:----|:-----|:-----|:---------|
| 🌐 **本地网页查阅** | `flask_dir_browser.py` | 轻量 Flask 网站，渲染 Markdown、目录导航、全文浏览 | `python3 flask_dir_browser.py` |
| 🔄 **版本同步** | `git` → GitHub | 工作空间 Git 版本控制，推送到远程仓库备份（`cowkb.git`） | `python3 scripts/git/git-push-robust.py --commit -m "msg"` |
| 🧠 **语义检索** | `memory_search` | 向量检索（`memory/long-term/index.db`），AI 对话中自动路由 | ⚠️ 索引丢失，不可用 |

---

## 5. 用户操作方式（Skills/Scripts/路径全映射）

> 每类操作均标注 **使用的 Skill → 调用的 Script → 文件写入路径 → 文件格式**。

### 5.1 核心操作速查表

| # | 操作 | 触发 Skill | 辅助 Skill | 关联 Script | 产出路径 | 文件格式 |
|:-:|:----|:-----------|:-----------|:------------|:---------|:---------|
| 1️⃣ | **投喂文件** 📥 | `light-file-reading`（自动） | `knowledge-wiki` | — | `knowledge/06_others/sources/<slug>.md` | Markdown（TOC + Changelog） |
| 2️⃣ | **分享网页链接** 💬 | `web-archive` | `web-access`（统一搜索路由） | `check/link-validator.py` | `knowledge/06_others/sources/<slug>.md` | Markdown（带来源标注） |
| 3️⃣ | **分享豆包对话** 🫘 | `doubao-share` | `web-access` | `skills/doubao-share/scripts/slugify.py` | `knowledge/06_others/sources/<slug>.md` | Markdown（带对话摘要） |
| 4️⃣ | **深度技术调研** 🔍 | `deep-tech-writer` | `knowledge-doc-writer`, `web-access` | `check/doc-quality.py`, `check/doc-review.py` | `knowledge/07_industry-research/<subdir>/<topic>.md` | 深度分析文档（6 步工作流） |
| 5️⃣ | **行业市场洞察** 📊 | `industry-insight` | `web-access`, `method-analysis` | — | `knowledge/01_survey/industry-research/<date>-<topic>.md` | 五看三定专题报告 |
| 6️⃣ | **学术文献调研** 📚 | `light-literature-search` | `baidu-scholar-search`, `web-access` | — | `knowledge/01_survey/<domain>/YYYY-MM-DD.md` | 文献综述文档 |
| 7️⃣ | **麦肯锡级市场研究** 🏢 | `mckinsey-research` | `web-access` | — | `artifacts/research/<date>-<slug>.html` | HTML 战略报告 |
| 8️⃣ | **竞品分析** 🥊 | `server-competitor-analysis` | `web-access` | — | `knowledge/01_survey/<domain>/` | 竞品对比报告 |
| 9️⃣ | **批量导入素材** 📦 | `discover` (Skill) | `autokb` | `scripts/autokb/run_pipeline.py` | `import/` → `discover/` → `knowledge/` | MD + 索引 + 日志 |
| 🔟 | **对话归档/知识整理** 📝 | `knowledge-wiki` | — | — | `knowledge/concepts/`, `knowledge/methodology/` | 结构化知识文档 |
| 1️⃣1️⃣ | **文档质量审查** ✅ | `doc-reviewer` | `light-self-review`, `depth-completer` | `check/doc-review.py`, `check/doc-quality.py` | 审查报告（终端/文件） | 评审清单 |
| 1️⃣2️⃣ | **知识库健康检查** 🏥 | `knowledge-health-check` | `knowledge-index-manager`, `log-reformatter` | `check/kb-health.py`, `check/link-validator.py` | 扫描报告 + 自动修复 | 6 维健康报告 |
| 1️⃣3️⃣ | **生成周报** 📅 | `weekly-report-generator` | `knowledge-wiki` | `knowledge-stats-collector.py` | `knowledge/weekly-reports/` | 结构化周报文档 |
| 1️⃣4️⃣ | **制 PPT** 🎨 | `light-slides` | `pptx` (Skill) | — | `<output>.pptx`（或路径指定） | PPTX |
| 1️⃣5️⃣ | **写论文** 📄 | `light-paper-drafting` | `light-citation`, `light-typesetting` | — | `knowledge/<paper-dir>/` 或指定路径 | LaTeX / Word |
| 1️⃣6️⃣ | **文件迁移** 🚚 | `directory-optimizer` | `knowledge-index-manager` | `scripts/tools/mv-knowledge.py`, `check/link-fixer.py` | `knowledge/<new-dir>/` | ✅一键自动化 |
| 1️⃣7️⃣ | **定时调研任务** ⏰ | `scheduler` (系统) | 各调研 Skills | `scripts/tools/execution-log.py` | `knowledge/01_survey/<domain>/YYYY-MM-DD.md` | 每日跟踪报告 |
| 1️⃣8️⃣ | **网页/Markdown 格式转换** 🔄 | `markdown-converter` | `qiaomu-markdown-proxy` | `convert-to-markdown.py` | `import/` | Markdown |
| 1️⃣9️⃣ | **故障排查/RCA** 🔧 | `fault-diagnosis` | — | — | `knowledge/02_rd/` / 故障分析文档 | 五层诊断报告 |

### 5.2 数据流与文件的对应关系

```text
用户操作                技能引擎                 脚本工具              持久化位置
────────                ────────               ────────              ────────
投喂文件  ──────────▶  light-file-reading ──────────────────────▶  knowledge/sources/
分享网页  ──────────▶  web-archive ──────▶ link-validator.py ──▶  knowledge/sources/
分享豆包  ──────────▶  doubao-share ──────▶ slugify.py ────────▶  knowledge/sources/
发起调研  ──────────▶  deep-tech-writer ──▶ doc-quality.py ────▶  knowledge/07_industry-research/
                  └──  knowledge-doc-writer                     knowledge/01_survey/
批量导入  ──────────▶  discover (skill) ──▶ autokb/run_pipeline.py ▶ discover/ → knowledge/
归档链接  ──────────▶  knowledge-wiki ─────────────────────────▶  knowledge/concepts/
定时任务  ──────────▶  scheduler ─────────▶ execution-log.py ──▶  knowledge/01_survey/<domain>/
```

---

## 6. 工程设计参考

> `spec/` 目录存放系统的完整设计文档（62 个，六类型：sr/ar/design/std/meth/audit），完整索引见 [`spec/index.md`](spec/index.md)，阅读路线见 [`spec/README.md`](spec/README.md)。下表为核心文档：

| 文档 | 类型 | 说明 |
|:-----|:----:|:------|
| [`sr-001-knowledge-system-requirements.md`](spec/sr-001-knowledge-system-requirements.md) | 需求 | **用户需求说明书** — 完整记录系统用户需求（SR） |
| [`ar-001-sr-ar-mapping.md`](spec/ar-001-sr-ar-mapping.md) | 规格 | **SR→AR 映射表** — 双向映射，含验收标准与实施优先级 |
| [`design-001-system-architecture.md`](spec/design-001-system-architecture.md) | 设计方案 | **系统架构规格** — 总体架构、四阶段数据流、模块设计 |
| [`std-001-development-rules.md`](spec/std-001-development-rules.md) | 规范 | **工程开发规范** — 代码/文档/知识库/管线/Skills/Git 全约束 |
| [`sr-003-system-constraint-registry.md`](spec/sr-003-system-constraint-registry.md) | 规范 | **约束注册表 SSOT** — 87 条 CCLRR 编码约束 |
| [`sr-006-ai-task-processing-optimization.md`](spec/sr-006-ai-task-processing-optimization.md) | 需求 | **AI 任务处理优化需求** — 14 类任务类型痛点分析与优化建议 |
| [`sr-007-content-quality-standards.md`](spec/sr-007-content-quality-standards.md) | 规范 | **内容质量标准** — 八级质量分级 + 四维评估 + 门禁 |
| [`sr-008-system-challenges-and-practices.md`](spec/sr-008-system-challenges-and-practices.md) | 需求 | **系统挑战与实践** — 9 大挑战 × 36 项改进方案 |
| [`sr-009-spec-audit-system-design.md`](spec/sr-009-spec-audit-system-design.md) | 需求 | **Spec 审计体系设计** — 三层审计 + 8 专项域 |
| [`sr-010-system-attention-points.md`](spec/sr-010-system-attention-points.md) | 需求 | **系统关注点全景** ⭐ — 14 关注面（资源源/格式保真/稳定性/分库等）+ P0/P1/P2 路线图 |
| [`design-007-skills-scripts-design.md`](spec/design-007-skills-scripts-design.md) | 设计方案 | **Skills/Scripts 设计要求** — 双引擎 + 映射框架 |
| [`design-008-knowledge-retrieval-framework.md`](spec/design-008-knowledge-retrieval-framework.md) | 设计方案 | **知识检索框架** — 去重/索引/语义接入 |
| [`design-011-scheduled-tasks-system-design.md`](spec/design-011-scheduled-tasks-system-design.md) | 设计方案 | **定时任务体系设计** — 三层架构 + 9 项规则 |
| [`meth-004-industry-research-methodology.md`](spec/meth-004-industry-research-methodology.md) | 方法论 | **行业调研方法论** — 22 源体系 + 两阶段流水线 |
| [`meth-017-web-access-architecture.md`](spec/meth-017-web-access-architecture.md) | 方法论 | **Web 访问能力全景** — 四层架构 + 反爬应对链 + 稳定源清单 |
| [`std-002-knowledge-content-format.md`](spec/std-002-knowledge-content-format.md) | 规范 | **知识内容格式标准** — 5 大要素模板 |
| [`std-003-knowledge-operations-guide.md`](spec/std-003-knowledge-operations-guide.md) | 规范 | **知识库操作指南** — 文件操作决策依据 |
| [`std-005-kb-directory-registry.md`](spec/std-005-kb-directory-registry.md) | 规范 | **目录注册表 SSOT** — 归档路径判定规则 |

**使用场景**：
- 新增功能 → 在 `sr-001` 中补 SR → `ar-001` 补 AR → 在 `design-001` 中补充设计 → 实施
- 系统规划 → 先读 `sr-010`（关注点全景）→ `sr-008`（历史挑战）→ 对应专项文档
- 代码审查 → 对照 `std-001-development-rules.md` 逐项检查
- 任务优化 → 查看 `sr-006` 中对应任务类型的优化建议和优先级

---

## 7. 模块介绍

### 7.1 核心目录结构

| 目录 | 用途 | 规格定义 | 规模概览 | 对应 Skills |
|:-----|:-----|:---------|:--------:|:-----------|
| **根级文件** (`AGENT.md` / `USER.md` / `RULE.md` / `MEMORY.md`) | Agent/用户/规则/记忆 | — | 4 个核心配置文件 | `profile-optimizer` |
| `import/` | 📥 Phase 1 原始素材仓 | [`std-003`](spec/std-003-knowledge-operations-guide.md) | 21,326 文件 / 1.16 GB | `autokb` 管线 |
| `projects/` | 📥 Phase 1 工程代码仓 | 同上 | 1+ 项目 | — |
| `discover/` | 🔧 AI 批量化知识加工层 | [`sr-005`](spec/sr-005-discover-dir-req.md) | 9,674 文件 / 1.35 GB | `discover` (skill) |
| `knowledge/` | 🧠 Phase 3 核心知识库 | [`design-003`](spec/design-003-knowledge-directory-design.md) | 3,693 文件 / 122 MB，8 模块 | 全链 Skills |
| `memory/` | 📝 记忆（每日对话 + 向量索引） | — | 173 文件（每日 MD，1.6 MB）；⚠️ long-term/index.db 丢失 | `knowledge-wiki`, `light-memory-pm` |
| `conversation-log/` | 🗂️ 会话记录与用户问题导出 | — | 591 文件 / 54.5 MB | `session-intent-analysis` |
| `spec/` | 📋 系统设计文档集 | — | 62 文件 6 类型 | — |
| `skills/` | 🧩 AI 技能系统 | [`design-007`](spec/design-007-skills-scripts-design.md) | 104 本地 + 33 外部 | `skill-creator` |
| `scripts/` | ⚙️ 自动化脚本库 | 同上 | 563 个文件 / 30 MB | — |
| `scheduler/` | ⏰ 定时任务配置 | [`design-011`](spec/design-011-scheduled-tasks-system-design.md) | 49 个运行时任务 | — |
| `workflow/` | 🔄 Workflow 定义 | [`meth-013`](spec/meth-013-workflow-system.md) | 7 个静态/动态 WF 定义 | — |
| `templates/` | 📄 文档模板 | — | 4 个模板 | — |
| `websites/` | 🌐 网页产物 | — | 1 个文件 | — |
| `tmp/` | 🗑️ 临时文件 / 回收站 | — | 24,117 文件 / 594 MB | — |
| `_archive/` | 🗄️ 归档区（229M） | — | 历史归档 | — |

### 7.2 关键模块与 Skills/Scripts 关联

| 模块 | 职责 | 核心 Skills | 核心 Scripts | 文件格式标准 |
|:-----|:------|:-----------|:-------------|:------------|
| `import/` | 原始素材仓 | `markdown-converter`, `light-file-reading` | `convert-to-markdown.py`, `import_files.py`, `dedup_import.py` | 保持原始格式 |
| `discover/` | AI 批量分析产物 | `discover` (skill) | `discover/*.py` | MD + 问题/分类/关键词标注 |
| `knowledge/sources/` | 外部源归档 | `web-archive`, `doubao-share`, `knowledge-wiki` | `slugify.py` | Markdown: TOC + Changelog + 来源头 |
| `knowledge/01_survey/` | 行业追踪 | `deep-tech-writer`, `light-literature-search` | `execution-log.py` | Markdown: 日期 + 摘要 + 链接 |
| `knowledge/07_industry-research/` | 深度专题 | `knowledge-doc-writer`, `industry-insight` | `check/doc-quality.py` | 深度文档: 量化四要素 + 来源 + TOC |
| `knowledge/concepts/` | 核心概念 | `knowledge-wiki` | — | 概念文档: 定义 + 原理 + 案例 |
| `knowledge/weekly-reports/` | 周报 | `weekly-report-generator` | `knowledge-stats-collector.py` | 结构化周报: 摘要 + 各维度 + 洞察 |
| `knowledge/methodology/` | 方法论 | `method-analysis` | — | 方法论文档: 框架 + 步骤 + 案例 |

---

## 8. Skills 系统（按任务类型组织）

> 完整使用手册 → [`skills/README.md`](skills/README.md)

### 8.1 按任务类型分类

基于 [`sr-006`](spec/sr-006-ai-task-processing-optimization.md) 任务类型组织 Skills：

| 任务类型 | 核心 Skill | 辅助/关联 Skills |
|:---------|:-----------|:-----------------|
| **A-深度调研** 🔍 | `deep-tech-writer`, `knowledge-doc-writer`, `industry-insight` | `light-literature-search`, `web-access`, `doc-reviewer` |
| **B-内容检索** 🔎 | `memory_search` (系统) | `knowledge-wiki`, `light-file-reading`, `session-keeper` |
| **C-批量操作** 📦 | `discover` | `autokb` (管线), `knowledge-wiki` |
| **D-深度创作/质量提升** 🎯 | `deep-tech-writer`, `doc-reviewer` | `depth-completer`, `light-self-review`, `light-consistency`, `markdown-format-standards` |
| **E-目录治理** 🗂️ | `directory-optimizer`, `knowledge-index-manager` | `log-reformatter`, `knowledge-health-check` |
| **F-常规归档** 📥 | `web-archive`, `doubao-share` | `web-access`, `knowledge-wiki` |
| **G-并行扫描** ⚡ | `scheduler` (系统) | 各调研 Skills, `weekly-report-generator` |
| **H-知识库治理** 🏥 | `knowledge-health-check`, `knowledge-index-manager` | `constraint-verifier`, `profile-optimizer` |
| **I-定时编排** ⏰ | `scheduler` (系统) | `session-keeper`, `light-orchestrator` |

### 8.2 按专业技能域分类

| 类别 | Skills 示例 | 说明 |
|:-----|:-----------|:------|
| 📝 文档处理 | `pdf`, `docx`, `pptx`, `xlsx`, `markdown-converter`, `light-typesetting` | 文档格式创建/编辑/转换 |
| 🔬 深度技术 | `deep-tech-writer`, `fault-diagnosis`, `complex-system-function`, `method-analysis` | 技术分析、方法论 |
| 📊 行业分析 | `mckinsey-research`, `industry-insight`, `server-competitor-analysis` | 市场研究、竞品分析 |
| 📖 论文辅助 | `light-idea-generation`, `light-paper-drafting`, `light-citation`, `light-venue-matching` 等 | 研究全生命周期 |
| 💻 研发编码 | `light-backend-coding`, `light-frontend-design`, `light-system-design`, `open-code-review` | 编码、架构、代码审查 |
| 🧩 硬件分析 | `server-competitor-analysis`, `server-asset-management-research` | 服务器/互联/RDMA 分析 |
| 🔍 质量审查 | `doc-reviewer`, `light-self-review`, `constraint-verifier`, `knowledge-health-check` | 文档/知识库/约束审查 |
| 💡 创新辅助 | `light-idea-generation`, `light-competition`, `light-ip-application`, `patent-disclosure-writer` | 创新、竞赛、知识产权 |
| 🌐 联网工具 | `web-access`（统一搜索路由）, `web-archive`, `wechat-article-search`, `baidu-scholar-search` | 联网搜索、网页归档 |
| 📅 日常工具 | `data-query`, `daily-news-60s`, `hot-topics`, `utility-tools` | 天气/新闻/热搜/工具 |
| 🔧 系统引擎 | `light-orchestrator`, `pipeline-orchestrator`, `skill-creator`, `skill-evolver` | 流水线编排、技能生命周期 |

### 8.3 Skills ↔ 脚本映射

> 完整映射表 → [`scripts/skills-scripts-mapping.md`](scripts/skills-scripts-mapping.md)

| Skill | 关联 Scripts | 协作模式 |
|:------|:------------|:---------|
| `web-access` | `skills/web-access/scripts/search-router.py`（统一搜索路由 L1 专业站→L2 Bing→L3 搜狗系） | Skill 主流程 + Script 执行 |
| `web-archive` | `check/link-validator.py` → 归档后验证链接 | Skill 主流程 + Script 后验 |
| `deep-tech-writer` | `check/doc-quality.py` → 量化四要素自检 | Skill 产出后 Script 校验 |
| `doc-reviewer` | `check/doc-review.py` → 三层结构化审查 | Skill 编排 + Script 自动化审查 |
| `knowledge-health-check` | `check/kb-health.py` → 6 维扫描 | Skill 编排 + Script 执行 |
| `log-reformatter` | `check/reformat-log.py` → 格式统一 | Skill 描述 + Script 执行 |
| `doubao-share` | `skills/doubao-share/scripts/slugify.py` → 文件名生成 | Skill 工作流内嵌 |
| `discover` | `scripts/discover/*.py` → 批量操作 | Skill 入口 + Script 管线 |
| `weekly-report-generator` | `knowledge-stats-collector.py` → 统计数据 | Skill 编排 + Script 数据支撑 |

---

## 9. 脚本系统（按任务支持分组的 CLI 工具链）

> 完整使用手册 → [`scripts/README.md`](scripts/README.md)

### 9.1 场景导向脚本分组

| 分组 | 说明 | 核心脚本 |
|:-----|:-----|:---------|
| 🎮 **导入管线** (`autokb/`) | 批量导入 import/ → knowledge/ | `run_pipeline.py` · `discover.py` · `classify.py` · `importer.py` |
| 🔍 **质量检查** (`check/`) | 格式检查/链接验证/索引覆盖/文档审查/质量门禁 | `constraint-check.py` · `kb-health.py` · `link-validator.py` · `link-fixer.py` · `md-format.py` · `doc-review.py` · `doc-quality.py` · `strategy-compliance.py` |
| 🛠️ **独立工具** (`tools/`) | 格式转换/文件迁移/执行日志/元数据 | `html-to-markdown.py` · `mv-knowledge.py` · `execution-log.py` · `kb-metadb.py` · `slugify.py` |
| 🔍 **搜索/调研** (`search/`) | 统一搜索入口/搜索计划/源管理 | `unified-search.py` |
| 🔄 **版本控制** (`git/`) | 可靠推送/拉取（多策略重试+代理） | `git-pull-robust.py` · `git-push-robust.py` |
| 📊 **意图分析** (`intent_analysis/`) | 会话语义分析/话题边界/报告生成 | `main.py` · `extract_user_questions.py` |
| 🤖 **批量加工** (`discover/`) | import 问题提取/AI 分类/批量文档 | `ai-batch-extract-questions.py` · `ai-batch-gen-docs.py` · `import-to-knowledge.py` |
| 📄 **根级工具** | 每日跟踪/统计/同步/导入/去重 | `kb-daily-files.sh` · `knowledge-stats-collector.py` · `import_files.py` · `dedup_import.py` |
| 🔗 **向后兼容软链接** | 根级兼容旧命令 | `check_links.py` · `check_md_format.py` · `knowledge_health_check.py` 等 |

### 9.2 任务 ↔ 脚本快速检索

| 你要做什么 | 执行命令 |
|:-----------|:---------|
| 统一联网搜索 | `python3 skills/web-access/scripts/search-router.py "关键词"`（L1 专业站→L2 Bing→L3 搜狗系） |
| 约束合规检查 | `python3 scripts/constraint-check.py` |
| 链接扫描+修复 | `python3 scripts/check/link-validator.py && python3 scripts/check/link-fixer.py --auto` |
| 文档质量自检 | `python3 scripts/check/doc-quality.py <文档.md>` |
| 文档三层审查 | `python3 scripts/check/doc-review.py <文档.md>` |
| 全文格式规范 | `python3 scripts/check/md-format.py <文档.md> --fix` |
| log.md 格式重整 | `python3 scripts/check/reformat-log.py <目录/log.md>` |
| index 覆盖率 | `python3 scripts/check/analyze-index-coverage.py <目录>` |
| 知识库健康度 | `python3 scripts/check/kb-health.py` |
| 导入素材到知识库 | `python3 scripts/autokb/run_pipeline.py --source md --max 10` |
| 智能链接修复 | `python3 scripts/check/link-fixer.py --auto` |
| 提交+推送代码 | `python3 scripts/git/git-push-robust.py --commit -m "message"` |
| 启动 Flask 浏览器 | `python3 flask_dir_browser.py` |

### 9.3 统一入口工具

**`constraint-check.py`** 是约束合规检查的统一入口，覆盖 11 类别 × 70+ 条约束（基于 SR-003 约束注册表）：

```bash
python3 scripts/constraint-check.py                    # 默认检查（safety+format+index-log+code）
python3 scripts/constraint-check.py --category all --summary  # 全量检查
python3 scripts/constraint-check.py --category safety        # 仅安全红线
python3 scripts/constraint-check.py --category format --target file.md --fix  # 修复
```

---

## 10. 常用命令速查（按任务类型）

### A-深度调研

```bash
# 搜索文献 + 分析（AI 对话触发 deep-tech-writer / knowledge-doc-writer / industry-insight）
# 搜索后自查
python3 scripts/check/doc-quality.py knowledge/07_industry-research/<dir>/<file>.md
```

### B-内容检索

```bash
# memory_search（向量检索）— AI 对话中自动路由
# grep 文本搜索（手动）
grep -rn "关键词" knowledge/ --include="*.md" | head -30
```

### C-批量文件操作

```bash
# discover 管道（按需调用）
python3 scripts/discover/extract-questions.py          # 问题提取
python3 scripts/discover/ai-batch-gen-docs.py          # 批量生成文档
python3 scripts/discover/import-to-knowledge.py        # 导入知识库

# autokb 管线
python3 scripts/autokb/run_pipeline.py --all --dry-run  # 预览
python3 scripts/autokb/run_pipeline.py --all --max 10   # 限制处理数
```

### D-深度分析质量保障

```bash
python3 scripts/check/doc-quality.py <文档.md>          # 量化四要素检查
python3 scripts/check/doc-review.py <文档.md>           # 三层审查
python3 scripts/check/md-format.py <文档.md> --fix      # 格式修复
```

### E-文件迁移

```bash
python3 scripts/tools/mv-knowledge.py --dry-run <源文件> <目标目录>  # 预览
python3 scripts/tools/mv-knowledge.py <源文件> <目标目录>           # 一键迁移
python3 scripts/check/link-validator.py          # 迁移后扫描断裂链接
python3 scripts/check/link-fixer.py --auto       # 自动修复
```

### G-搜索与批量调研

```bash
# 统一搜索路由（专业站→Bing→搜狗系 自动降级）
python3 skills/web-access/scripts/search-router.py "超节点互联" --json

# 查看搜索源可达性
python3 skills/web-access/scripts/search-router.py --check

# 生成搜索计划（旧版 unified-search）
python3 scripts/search/unified-search.py plan --domain supernode
```

### I-定时任务监控

```bash
python3 scripts/tools/execution-log.py log --task-id <id> --task-name "调研" --status success --lines 42
python3 scripts/tools/execution-log.py report --summary   # 全量监控摘要
python3 scripts/tools/execution-log.py retry --list      # 可重试任务
```

### F-常规归档

```bash
# 网页归档 — AI 对话中触发 web-archive skill
# 豆包归档 — AI 对话中触发 doubao-share skill
python3 scripts/autokb/run_pipeline.py --source md       # import 导入
```

### G/H-知识库治理

```bash
python3 scripts/check/kb-health.py                       # 6 维健康度
python3 scripts/check/link-validator.py                   # 链接扫描
python3 scripts/check/link-fixer.py --auto                # 链接修复
python3 scripts/check/analyze-index-coverage.py --all --fix  # index 覆盖修复
python3 scripts/check/reformat-log.py --all               # log 格式统一
python3 scripts/constraint-check.py --category all        # 全量约束
```

### 运维

```bash
python3 scripts/git/git-push-robust.py --commit -m "update"  # 提交+推送
python3 flask_dir_browser.py                                   # 启动 Web 浏览
```

---

## 11. 定时任务体系

> 完整设计见 [`spec/design-011-scheduled-tasks-system-design.md`](spec/design-011-scheduled-tasks-system-design.md)；运行监控用 `scripts/tools/execution-log.py`。

### 11.1 任务构成（49 个）

| 类别 | 数量 | 说明 | 示例 |
|:-----|:----:|:-----|:-----|
| 🌙 **领域日追踪** | 24 | 每日低负载时段（21:00–06:30）后台联网搜索 | 超节点标准与生态 / 服务器硬件追踪 / 部件存储追踪 / 互联与光通信 / 国产化替代调研 |
| 📅 **日报** | 2 | 每日 07:00 知识库日报；01:50 GitHub 开源活动日报 | 汇总前日沉淀与洞察 |
| 📊 **周报/周检** | 6 | 周日 07:00 周报 + 周质量检测 + 同步检查 + 专项报告 | 知识库周报 / Skills-Scripts 周质量检测 |
| 📆 **月报** | 1 | 每月最后一天 | 知识库月度报告 |
| 🧩 **其他/专项** | 16 | 行业调研组（硬件/技术/市场组）、专项追踪 | 行业调研 / 政策与产业环境追踪 |

### 11.2 可靠性设计（要点）

- **三层架构**: `scheduler/tasks.json`（配置 SSOT）→ 任务执行 → 结果沉淀 + `execution-log.py` 监控
- **Fail-Fast 纪律**: 单源最多 1 次请求，失败快速降级，不重试卡死源
- **来源分级**: 稳定源（TechCrunch/STH/爱集微/NVIDIA 等）优先，反爬源（信通院/Intel/OCP）自动规避
- **输出渠道**: 全部走飞书 web 渠道（避免 session 中断断供）
- **凭证时效**: 访问凭证（cookie/API key）过期即任务失败，需定期巡检

### 11.3 新增任务指南

```bash
# 每天 21:00–06:30 之间，每 10 分钟一个槽位
# scheduler create name="任务名" message="搜索提示词" schedule_type="cron" schedule_value="15 22 * * *"
```

---

## 12. 约束说明

> 全量约束管理见 [`spec/sr-003-system-constraint-registry.md`](spec/sr-003-system-constraint-registry.md)（**约束注册表 SSOT**，87 条 CCLRR 编码约束），合规检查统一入口为 `scripts/constraint-check.py`。本文不再展开，以免与注册表不一致。

**文件操作铁律**（摘录）:
- **永不 rm** — `mv` 到 `tmp/bak/`（回收站）
- **改前查头部约束** — AUTO-GENERATED / DO NOT EDIT / MANAGED_BY 文件用生成工具改
- **破坏性操作先问用户** — rm/覆盖/删除关键文件
- **四个全局文件（RULE/AGENT/USER/MEMORY）修改前三思** — 先写 `Candidate.md` 走人工审核

---

## 13. 后续待办

### 13.1 短期（2026 Q3）— P0 优先

- [x] **知识库三件套纪律**（README/index/log 由脚本批量维护，AI 不直接编辑）
- [x] **Playwright 禁用**（无头服务器环境挂死，代码级门控，`PLAYWRIGHT_ENABLED=1` 可恢复）
- [x] **磁盘清理**：空间已充裕（实测 5.27G / 可用 410.8G，原 96% 告警解除），`discover/` 1.35G / `import/` 1.16G / `.git/` 1.55G 维持观察
- [ ] **向量索引重建** ⚠️：`memory/long-term/index.db`（2.2G）已丢失，恢复 `memory_search` 语义检索为最高优先级
- [ ] **异地备份**：当前无异地备份，磁盘故障 = 全损（告警虽解除，风险仍存）
- [ ] **统一搜索路由验收**：`search-router.py` 自动降级链路最终验证后正式启用
- [ ] **Web 访问 Playwright 重新引入方案**（条件成熟后）

### 13.2 中期（2026 Q4）

- [ ] **check 脚本收敛**：57 个 check 三套判定标准统一（sr-010 F5）
- [ ] **路径注册中心**：消除脚本路径硬编码（sr-010 F3）
- [ ] **MCP 盘点与整合**：资源源统一管理（sr-010 F1）
- [ ] **格式保真清单**：Markdown 化丢失维度与缓解策略落地（sr-010 F2）

### 13.3 长期（2027 H1）

- [ ] **全自动知识生产流水线**: 从采集到归档全链路无人值守
- [ ] **多 Agent 协作知识工厂**: 多个 AI Agent 协作处理不同知识类型
- [ ] **自动关联图谱**: 基于内容相似度构建知识网络

---

## 演进路线

```text
Phase 1 (2025-2026 Q2)     Phase 2 (2026 Q3-Q4)         Phase 3 (2027 H1)
┌──────────────────┐       ┌──────────────────┐         ┌──────────────────┐
│   人工驱动        │ ──▶  │   半自动驱动      │ ────▶  │   自动演化        │
│                  │       │                  │         │                  │
│ ✅ 基础知识库    │       │ 🔄 当前所处阶段   │         │ 🚧 全自动流水线   │
│ ✅ 基本 Skills   │       │ ✅ 批量导入管线   │         │ 🚧 多 Agent 工厂  │
│ ✅ 质量体系      │       │ ✅ 定时调研      │         │ 🚧 自动关联图谱   │
│                  │       │ ✅ 意图分析      │         │                   │
│                  │       │ 🔧 RAG 检索(索引丢失待重建) │ │                   │
└──────────────────┘       └──────────────────┘         └──────────────────┘
```

---

## 相关文档

| 文档 | 位置 | 说明 |
|:-----|:-----|:------|
| **系统关注点全景** ⭐ | [`spec/sr-010-system-attention-points.md`](spec/sr-010-system-attention-points.md) | 14 关注面 + P0/P1/P2 路线图（最新规划入口） |
| **系统架构规格** | [`spec/design-001-system-architecture.md`](spec/design-001-system-architecture.md) | 详细架构、模块框图、数据流 |
| **开发规范** | [`spec/std-001-development-rules.md`](spec/std-001-development-rules.md) | 工程代码/文档/质量规范 |
| **约束注册表** | [`spec/sr-003-system-constraint-registry.md`](spec/sr-003-system-constraint-registry.md) | 87 条约束 SSOT |
| **内容质量标准** | [`spec/sr-007-content-quality-standards.md`](spec/sr-007-content-quality-standards.md) | 八级质量分级 + 门禁 |
| **Skills/Scripts 设计** | [`spec/design-007-skills-scripts-design.md`](spec/design-007-skills-scripts-design.md) | Skills 与 Scripts 设计要求 |
| **定时任务体系** | [`spec/design-011-scheduled-tasks-system-design.md`](spec/design-011-scheduled-tasks-system-design.md) | 49 任务三层架构设计 |
| **Web 访问架构** | [`spec/meth-017-web-access-architecture.md`](spec/meth-017-web-access-architecture.md) | 联网四层架构 + 反爬应对 |
| **行业调研方法论** | [`spec/meth-004-industry-research-methodology.md`](spec/meth-004-industry-research-methodology.md) | 22 源体系 + 两阶段流水线 |
| **Spec 索引** | [`spec/index.md`](spec/index.md) | 62 个设计文档完整索引 |
| **Skills 使用手册** | [`skills/README.md`](skills/README.md) | Skills 详细说明、触发条件、分类索引 |
| **Scripts 使用手册** | [`scripts/README.md`](scripts/README.md) | CLI 命令详细用法、参数、场景示例 |
| **Skills ↔ Scripts 映射** | [`scripts/skills-scripts-mapping.md`](scripts/skills-scripts-mapping.md) | 双向映射表 |
| **身份设定** | `AGENT.md` / `USER.md` | Agent 人格与用户身份 |
| **记忆索引** | `MEMORY.md` / `memory/` | 长期记忆与每日记录 |
| **文件规约** | `RULE.md` | 工作空间使用规则 |
| **知识库设计** | [`spec/design-003-knowledge-directory-design.md`](spec/design-003-knowledge-directory-design.md) | knowledge/ 内部目录设计 |
| **AI 知识库系统建设** | [`knowledge/03_AI/knowledge-system/`](knowledge/03_AI/knowledge-system/) | 技术实现详情 |

---

> **Changelog**:
> - **2026-08-16**: v4.2 — 全量实测刷新：knowledge 3,693 / import 21,326 / discover 9,674 / skills 104+33 / scripts 563 / spec 62 / 会话 591 / git 1,418 / 仓库 5.27G（磁盘告警解除）；⚠️ 标记 `memory/long-term/index.db` 丢失（语义检索不可用）；更新能力雷达/架构图/数据流图/模块表/待办（新增"向量索引重建"P0）；§1.3 RAG 集成降为 40%
> - **2026-08-12**: v4.1 — 全量数据刷新（实测）：knowledge 3,085 / import 18,895 / discover 12,441 / skills 96+33 / scripts 256 活跃 / spec 47 / 定时任务 49 / 仓库 9.3G（磁盘 96% 告警）；新增 sr-010 系统关注点 / design-011 定时任务 / meth-017 web 访问 / std-002~005 等核心文档引用；§11 定时任务由 26 行大表改为 49 任务分类概览 + 可靠性设计；§13 待办区分已完成/进行中；补充 Web 访问统一搜索路由（search-router.py）
> - **2026-07-31**: v4.0 — 定位收敛为"三位一体"：🧪 AI×知识管理探索 + 🏭 服务器"产销研"知识库 + 📒 个人（家庭）笔记；新增 §1.0 定位模型（含主线/手段边界与 40% 投入红线）
> - **2026-07-27**: v3.8 — §5 重写为操作↔Skills↔Scripts↔路径全映射表 + 数据流图；§8 重写为按任务类型分组 + 专业技能域双视图；§9/§10 重写为场景导向分组 + 任务↔脚本速查
> - **2026-07-24**: v3.7 — 新增 [`spec/sr-005-discover-dir-req.md`](spec/sr-005-discover-dir-req.md)
> - **2026-07-24**: v3.6 — 新增 [`spec/design-007-skills-scripts-design.md`](spec/design-007-skills-scripts-design.md)
> - **2026-07-24**: v3.5 — §7.1 核心目录结构压缩为引用表
> - **2026-07-24**: v3.4 — 提取目录结构需求规格 `spec/sr-004-workspace-dir-req.md`
> - **2026-07-24**: v3.3 — §12 约束说明浓缩为引用
> - **2026-07-24**: v3.2 — Skills/scripts 内容合并：§8/§9/§10 浓缩为引用
> - **2026-07-21**: v3.1 — 更新资产清单，新增 Skills↔Scripts 联动表
> - **2026-07-21**: v3.0 重构 — 按四阶段闭环重新组织
> - **2026-07-09**: v2.2 — 架构图增加数据访问与同步层
> - **2026-06-26**: v1.0 初始版本
