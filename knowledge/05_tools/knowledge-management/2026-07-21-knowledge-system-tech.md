# 🏗️ 知识库搭建技术要点

> **概要**: 记录 Cow 知识库系统搭建过程中使用的技术点、工程实践、质量保障机制与后续优化方向。
>
> **关键词**: (待补充)

---

## 📑 目录

- [1. 技术选型与决策](#1-技术选型与决策)
  - [1.1 存储选型](#11-存储选型)
  - [1.2 处理引擎选型](#12-处理引擎选型)
  - [1.3 关键架构决策](#13-关键架构决策)
- [2. 四阶段数据体系建设](#2-四阶段数据体系建设)
  - [2.1 Phase 1: 数据收集技术要点](#21-phase-1-数据收集技术要点)
  - [2.2 Phase 2: 数据加工技术要点](#22-phase-2-数据加工技术要点)
  - [2.3 Phase 3: 数据优化技术要点](#23-phase-3-数据优化技术要点)
  - [2.4 Phase 4: 数据使用技术要点](#24-phase-4-数据使用技术要点)
- [3. AI 驱动的知识生产管线](#3-ai-驱动的知识生产管线)
  - [3.1 Skills 智能化加工流程](#31-skills-智能化加工流程)
  - [3.2 五种知识生产方式](#32-五种知识生产方式)
  - [3.3 生产流水线（Pipeline Orchestrator）](#33-生产流水线pipeline-orchestrator)
- [4. 幻觉约束与可信机制](#4-幻觉约束与可信机制)
  - [4.1 四层幻觉防护](#41-四层幻觉防护)
  - [4.2 来源优先级体系](#42-来源优先级体系)
  - [4.3 量化四要素规则](#43-量化四要素规则)
  - [4.4 关键数据不可获取时的处理](#44-关键数据不可获取时的处理)
- [5. 质量保障体系](#5-质量保障体系)
  - [5.1 自动化质量检查](#51-自动化质量检查)
  - [5.2 Skill 级质量审查](#52-skill-级质量审查)
  - [5.3 索引完整性保障](#53-索引完整性保障)
- [6. 技术实现细节](#6-技术实现细节)
  - [6.1 Skills 匹配机制](#61-skills-匹配机制)
  - [6.2 记忆系统检索](#62-记忆系统检索)
  - [6.3 定时任务调度](#63-定时任务调度)
  - [6.4 代码块格式规范](#64-代码块格式规范)
- [7. 后续技术优化方向](#7-后续技术优化方向)
  - [7.1 RAG 系统集成](#71-rag-系统集成)
  - [7.2 采集系统整合](#72-采集系统整合)
  - [7.3 自进化引擎](#73-自进化引擎)
  - [7.4 可信 AI 输出体系](#74-可信-ai-输出体系)
  - [7.5 import 素材批量处理](#75-import-素材批量处理)
- [参考文档](#参考文档)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 1. 技术选型与决策

### 1.1 存储选型

| 方案 | 选型 | 理由 | 替代方案 |
|:-----|:-----|:------|:---------|
| 知识库存储 | **Markdown + Git** | 纯文本、Git diff 友好、可读性高、工具链成熟 | Notion(外部依赖)、Obsidian(封闭格式)、Wiki(迁移成本高) |
| 会话持久化 | **SQLite** | 嵌入式、无外部依赖、结构化查询、事务支持 | MySQL(运维成本)、MongoDB(复杂度) |
| 记忆存储 | **Markdown 文件系统** | 与知识库统一格式、管理简单 | 向量库(过度设计) |

### 1.2 处理引擎选型

| 处理类型 | 工具选型 | 说明 |
|:---------|:---------|:------|
| Agent 运行时 | DeepSeek / Claude | AI 对话与工具调用 |
| 文件格式转换 | markitdown (Microsoft) | PDF/Word/PPT/Excel → Markdown |
| PPT 处理 | python-pptx | PPT 逐页提取文本和图表 |
| OCR | PaddleOCR | 图片/扫描件文字识别 |
| Web 浏览 | Flask + 自定义渲染 | 目录浏览 + Markdown 渲染 |

### 1.3 关键架构决策

| 决策 | 方案 | 理由 |
|:-----|:------|:------|
| Skills 匹配机制 | description 语义匹配 | 灵活、可扩展、无需硬编码 |
| 定时任务调度 | 内置 Scheduler | 共享 Agent 上下文、动态管理 |
| 数据流架构 | 四阶段闭环 | 清晰的输入/输出边界、便于质量控制 |
| 内容审查 | 三层（结构+逻辑+来源） | 覆盖不同粒度问题 |
| SSOT 适度原则 | 25% 松弛规则 | 避免过度约束导致无法产出 |

---

## 2. 四阶段数据体系建设

### 2.1 Phase 1: 数据收集技术要点

```text
输入类型 -> 处理工具 -> 存储位置 -> 用途
----------------------------------------
本地 .md  -> read          -> import/    -> 素材
PDF/Word  -> markitdown   -> import/    -> 素材
PPT       -> python-pptx  -> import/    -> 素材
图片      -> PaddleOCR    -> import/    -> 素材
URL       -> web_fetch    -> knowledge/ -> 笔记
豆包链接   -> doubao-share -> knowledge/ -> 笔记
```

**技术要点**:

- **markitdown 管线**: 支持 PDF、.docx、.pptx、.xlsx、HTML、CSV、JSON、XML、图片(EXIF/OCR)、音频(转录)、ZIP、EPub → Markdown
- **python-pptx**: 逐页遍历幻灯片，提取文本框/表格/图表标注
- **web_fetch**: 网页全文提取 + 跳转处理 + 文档文件直链解析
- **autokb 管线**: `run_pipeline.py` 端到端批量导入

### 2.2 Phase 2: 数据加工技术要点

```text
import/ 素材
   |
   +- > 格式统一（编码 UTF-8、统一换行符）
   +- > 内容去重（标题/摘要/关键段落三级相似度对比）
   +- > AI 摘要生成（LLM 提取关键信息 + 主题标签）
   +- > 分类推荐（基于知识库分类体系的语义匹配）
   |
   v
discover/ 提炼产物
```

**技术要点**:

- **去重策略**: 先对比文件名，再对比内容级摘要的语义向量相似度
- **摘要生成**: 使用 LLM 对素材做结构化摘要（主题 + 关键点 + 数据引用）
- **分类推荐**: 基于 knowledge/ 目录名和索引描述的语义匹配，提供 Top-3 推荐

### 2.3 Phase 3: 数据优化技术要点

```text
discover/ -> Skills 加工 -> 质量控制 -> knowledge/
  |            |             |
  |            +- web-archive: 8步工作流
  |            +- doubao-share: 链接解析 + 内容提取
  |            +- knowledge-doc-writer: 多源融合写作
  |            +- deep-tech-writer: 六步深度分析
  |            +- industry-insight: 五看三定行业分析
  |            +- knowledge-wiki: 对话提炼 + 自动归档
  |
  +- 量化四要素检查（数值+单位+基线+条件）
  +- 来源可追溯性校验
  +- 格式规范检查（TOC+交叉链接+Changelog）
  +- 索引与日志同步更新（index.md + log.md）
```

**技术要点**:

- **index.md 自动更新**: 每次文件创建/更新后，向 index.md 追加一行索引
- **log.md 变更记录**: 时间倒序记录所有操作
- **交叉链接验证**: 文档内所有 `](path)` 链接可用性自动检查

### 2.4 Phase 4: 数据使用技术要点

```text
knowledge/ -> Flask 浏览 / Git 同步 / AI 检索
  |
  +- flask_dir_browser.py:
  |    +- 目录树导航（左侧面板）
  |    +- Markdown 渲染（右侧面板）
  |    +- 全文搜索
  |
  +- Git 同步:
  |    +- git add -> commit -> push
  |    +- 提交规范: <type>: <描述>
  |    +- .gitignore 排除敏感文件
  |
  +- AI 检索:
       +- memory_search: 语义搜索知识库
       +- memory_get: 精确读取文件
       +- 上下文自动引用: 对话中自动读取相关文件
```

---

## 3. AI 驱动的知识生产管线

### 3.1 Skills 智能化加工流程

```text
用户输入
   |
   +- 扫描 available_skills 描述
   |
   +- 匹配 Skill ->
   |    +- read SKILL.md
   |    +- 按工作流执行
   |    +- 调用工具（web_fetch/bash/read/write）
   |    +- 产出写入 knowledge/
   |
   +- 不匹配 ->
        +- 通用工具处理
        +- 对话记录 -> 后台意图分析
        +- 可能触发 tech-learn 技能提取新模式
```

### 3.2 五种知识生产方式

| 方式 | 触发条件 | 产出位置 | 典型场景 |
|:-----|:---------|:---------|:---------|
| 🔗 **外部导入** | 用户分享 URL/豆包链接 | `knowledge/06_others/sources/` | 网页归档、对话导入 |
| 🔍 **专题调研** | 用户发起"调研XX" | `knowledge/02_rd/` 等 | 深度技术分析 |
| ⏰ **定时追踪** | Scheduler 定时触发 | `knowledge/01_survey/` | 行业每日追踪 |
| 💬 **对话提炼** | 深度讨论产出结论 | `knowledge/concepts/analysis/entities/` | 日常技术讨论 |
| 📊 **周期性报告** | 每周日 Scheduler | `knowledge/weekly-reports/01_weekly/` | 周报自动生成 |

### 3.3 生产流水线（Pipeline Orchestrator）

```text
Stage 1: 输入质量门 (input-qa)
  - 检查输入完整性和可靠性
  - 补充缺失信息

Stage 2: 多路并行 (multi-path) [可选]
  - 多视角同时处理
  - 独立上下文、独立 Token 预算

Stage 3: 汇聚 (convergence)
  - 多路结果合并
  - 权重来源可信度冲突消解

Stage 4: 验证循环 (verification-loop)
  - Plan->Do->Check->Act 迭代
  - 达到客观验证标准后退出

Stage 5: 约束执行 (constraint-enforcer)
  - SSOT 合规检查
  - 术语一致性/中间文件污染等约束

Stage 6: 专家把关 (expert-gate)
  - 生成专家审查清单
  - 标注需人类判断的维度
```

---

## 4. 幻觉约束与可信机制

### 4.1 四层幻觉防护

```text
L1: 来源约束 -- 每条断言标注来源（厂商/标准/论文）
               禁止无来源断言

L2: 交叉验证 -- 关键结论至少经 2 个独立源验证
               素材与验证源不一致时以验证源为准

L3: 质量审查 -- 三层审查（结构/逻辑/来源）
               13 条逻辑谬误扫描

L4: 拒绝编造 -- 数据不可获取时标注缺口
               不编造百分比/引用/未开源链接
```

### 4.2 来源优先级体系

```text
可信度                        来源类型                         使用方式
高     ⭐⭐⭐⭐⭐  标准规范/原始论文 (IEEE/JEDEC/PCI-SIG)    权威引用
       ⭐⭐⭐⭐   官方白皮书/技术博客 (NVIDIA/Intel)       主要信息源
       ⭐⭐⭐    行业分析报告 (IDC/Gartner/Omdia)         参考 + 交叉验证
       ⭐⭐     技术博客/论坛 (知乎/CSDN/公众号)           线索、不能单独引用
低     ⭐       AI 对话/会议纪要                         思想来源、需验证

关键原则: import/ 素材（L4/L5）不作为文档唯一来源
```

### 4.3 量化四要素规则

每个数据呈现必须包含：

```text
   数值       +     单位       +   对比基线    +    测试条件
   -----          -----          -------         ---------
   "28.9%"       "TB/s"        "vs H100"       "batch=32, FP8"
   "1.8"         "ns"          "vs PCIe Gen5"  "单次 64B 传输"
   "$3.5M"       "USD"         "vs 2025年"     "8-GPU 节点×1000"
```

### 4.4 关键数据不可获取时的处理

1. 标注数据缺口
2. 说明已尝试的源（如：NVIDIA 官网、IDC 报告、arXiv 论文、SEC 文件）
3. 给出基于已有数据的最保守替代估算
4. 附估算公式和假设条件

---

## 5. 质量保障体系

### 5.1 自动化质量检查

| 检查项 | 脚本 | 运行时机 | 检查内容 |
|:-------|:-----|:---------|:---------|
| 格式检查 | `check_md_format.py` | 文档写入后 | 编码、换行符、代码块格式 |
| 链接检查 | `check_links.py` | 每月 | 所有交叉链接有效性 |
| 文档质量 | `check_tech_doc_quality.py` | 技术文档交付前 | 量化四要素、来源标注 |
| 结构审查 | `review_doc.py` | 文档发布前 | 三层审查 |
| 健康检查 | `knowledge_health_check.py` | 每月 | 索引完整性、文件结构 |

### 5.2 Skill 级质量审查

| Skill | 审查范围 | 输出 |
|:------|:---------|:-----|
| `doc-reviewer` | 结构层 + 逻辑层 + 来源层 | 审查报告 + 严重度标记 |
| `light-self-review` | 十类失效模式（A-J） | 自检清单 + 修复建议 |
| `depth-completer` | 内容深度检测 | 深度补全方案 |
| `light-consistency` | 术语/风格/逻辑一致性 | 不一致清单 |
| `light-research-ethics` | 科研伦理/学术规范 | 合规审查报告 |
| `constraint-verifier` | 约束文件遵守度 | 约束偏离报告 |

### 5.3 索引完整性保障

```text
知识库索引体系:
  knowledge/index.md           - 顶层导航（7 大模块概览）
  knowledge/01_survey/index.md - 模块级索引（文件清单）
  knowledge/01_survey/log.md   - 模块级变更日志

保障机制:
  +- 每次写入新文件 -> 同步追加到 index.md
  +- 每次修改/删除 -> 同步记录到 log.md
  +- 自动化脚本: index_updater.py
  +- 健康检查: knowledge_health_check.py（验证覆盖率）
```

---

## 6. 技术实现细节

### 6.1 Skills 匹配机制

```text
available_skills 列表结构:
  +- name: 技能名称（大小写敏感）
  +- description: 自然语言描述（匹配依据）
  +- location: SKILL.md 路径
  +- base_dir: 技能目录路径

匹配流程:
  用户输入 -> 扫描所有 description -> 语义匹配 -> 选择最匹配的 Skill
  -> read SKILL.md -> 按指令执行

不匹配时: 使用通用工具，对话记录 -> 意图分析 -> 可能触发 skill-creator
```

### 6.2 记忆系统检索

```text
三层记忆 + 知识库构成完整上下文:

  1. MEMORY.md: 长期记忆（自动加载到上下文）
  2. memory/YYYY-MM-DD.md: 每日记忆（按需检索）
  3. conversation-log/: 完整会话记录（按需检索）
  4. knowledge/: 结构化知识库（按需检索）

检索策略:
  - 领域外/不确定 -> memory_search（语义检索）
  - 已知位置 -> memory_get（精确读取）
  - 当日事件 -> memory_get memory/YYYY-MM-DD.md
```

### 6.3 定时任务调度

```text
Scheduler API:
  create: action="create", name="任务名", message/schedule_type/schedule_value
  list: action="list"
  delete: action="delete", task_id="..."

调度类型:
  - cron: cron 表达式（如 "0 21 * * *" 每天21点）
  - interval: 固定间隔秒数
  - once: 一次性（相对时间 +5s/+10m/+1h 或 ISO 时间）

执行流程:
  Scheduler 触发 -> 执行任务 -> 产出写入 knowledge/ -> index.md + log.md 更新
```

### 6.4 代码块格式规范

Markdown 代码块中的 ASCII 图表必须对齐：

```text
规范:
  1. 代码块内的图表使用纯英文 ASCII 字符
  2. 中文说明标注在代码块外部
  3. 使用等宽字体对齐（空格 vs 全角字符）
  4. 运行 check_md_format.py 验证对齐

检查工具:
  python3 scripts/check_md_format.py <文件.md>
```

---

## 7. 后续技术优化方向

### 7.1 RAG 系统集成

```text
目标: 知识库向量化检索，提升问答准确率

技术选型:
  向量数据库: FAISS（本地轻量） -> 未来可扩展至 Milvus
  嵌入模型: BGE-M3 / text-embedding-3-small
  检索策略: Hybrid (向量 + BM25) + Rerank
  切分策略: RecursiveCharacterTextSplitter (chunk=512, overlap=64)

实施步骤:
  1. scripts/rag/build_index.py — 构建索引
  2. scripts/rag/query.py — 查询接口
  3. Skill: rag-search — Agent 检索入口
```

### 7.2 采集系统整合

```text
目标: 将公众号/网站外部采集脚本统一接入系统

架构:
  Scheduler -> collection_manager.py -> 公众号采集器/网站采集器/RSS订阅
                                    -> import/ -> autokb 管线

实施步骤:
  1. scripts/collection/ 目录 + 统一调度入口
  2. 各采集器实现
  3. 集成到 Scheduler
  4. 采集后自动触发导入管线
```

### 7.3 自进化引擎

```text
目标: 系统自动识别短板、优化策略、迭代进化

监控指标:
  - 知识库增长率（文件/月）
  - 内容更新频率（超 6 个月未更新文件占比）
  - Skills 使用频率（按触发次数）
  - 质量审查通过率
  - 索引完整性（覆盖率 %）

实施路径:
  1. 数据采集层: 收集各项指标
  2. 分析层: 识别短板和优化机会
  3. 执行层: 自动优化 Skills/脚本/目录结构
```

### 7.4 可信 AI 输出体系

```text
目标: 增强来源验证、幻觉检测、质量门禁

组件:
  1. 来源验证器: 自动验证引用来源的可访问性和准确性
  2. 幻觉检测器: 多路验证回路检测事实性错误
  3. 质量门禁: 阻止不合格内容进入知识库

实施:
  - pipeline-verification-loop（已有验证循环）-> 增强来源验证能力
  - 新增 source_validator.py — 来源可访问性自动检查
```

### 7.5 import 素材批量处理

```text
目标: 按 import_manifest.md 计划处理 ~7,400 个文件

路线:
  Phase 1: 文件分类 + 去重（dedup_import.py + AI 分析）
  Phase 2: 格式标准化 + 摘要生成（autokb 管线）
  Phase 3: 写入 knowledge/ + 索引更新（index_updater.py）
```

---

## 参考文档

| 文档 | 位置 | 说明 |
|:-----|:-----|:------|
| AI 知识库系统建设方案与实践 | [`05_tools/knowledge-management/2026-07-19-ai-knowledge-base-system-report.md`](05_tools/knowledge-management/2026-07-19-ai-knowledge-base-system-report.md) | 全流程方法论 |
| 知识体系文档 | [`05_tools/knowledge-management/2026-06-26-knowledge-system.md`](05_tools/knowledge-management/2026-06-26-knowledge-system.md) | 52,001 行完整知识体系 |
| AI 知识库综合指南 | [`05_tools/knowledge-management/2026-06-26-ai-knowledge-guide.md`](05_tools/knowledge-management/2026-06-26-ai-knowledge-guide.md) | 使用与构建指南 |
| 知识图谱报告 | [`05_tools/knowledge-management/2026-06-26-knowledge-graph-report.md`](05_tools/knowledge-management/2026-06-26-knowledge-graph-report.md) | 关联关系分析 |
| 高价值洞察 100 条 | [`2026-06-26-insights-100.md`](2026-06-26-insights-100.md) | 精选高价值结论 |
| 核心知识点萃取 | [`2026-06-26-essence.md`](../../02_rd/01_product/00_hardware/01_hw-core/2026-06-26-essence.md) | 2,088 文件精华提炼 |

---

> **Changelog**:
>
> - **2026-07-21**: v2.0 创建 — 按四阶段数据体系重构技术要点，新增幻觉约束机制、质量保障体系、技术实现细节（Skills 匹配机制、记忆系统检索、定时任务调度、代码块格式规范）、后续技术优化方向（RAG/采集整合/自进化/可信输出/批量处理），Align with design-001-system-architecture.md v3.0。

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- [`05_tools/knowledge-management/2026-07-19-ai-knowledge-base-system-report.md`](05_tools/knowledge-management/2026-07-19-ai-knowledge-base-system-report.md) — 关联
- [`05_tools/knowledge-management/2026-06-26-knowledge-system.md`](05_tools/knowledge-management/2026-06-26-knowledge-system.md) — 关联
- [`05_tools/knowledge-management/2026-06-26-ai-knowledge-guide.md`](05_tools/knowledge-management/2026-06-26-ai-knowledge-guide.md) — 关联
- [`05_tools/knowledge-management/2026-06-26-knowledge-graph-report.md`](05_tools/knowledge-management/2026-06-26-knowledge-graph-report.md) — 关联
- [`2026-06-26-insights-100.md`](2026-06-26-insights-100.md) — 关联
- [`2026-06-26-essence.md`](../../02_rd/01_product/00_hardware/01_hw-core/2026-06-26-essence.md) — 关联

### 外部资料引用

- (无)

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
