# std-001-development-rules.md — 工程开发规范（v4.0 提升版）

> **版本**: v4.0 | **更新**: 2026-08-19 | **状态**: ✅ 生效中
> **定位**: Cow 系统工程开发规范的**单一权威来源**——依据「数据收集→数据加工→数据优化→数据使用」四阶段框架，涵盖代码、文档、知识库、管线、技能、Git 工作流的全部开发约束。供审查与复用。
>
> **结论先行（30 秒版）**:
> 1. **溯源铁律**：所有开发工作必须可追溯——SR（需求）→ AR（技术需求）→ design/std（设计/标准）→ 实现，见 [`ar-001-sr-ar-mapping.md`](./ar-001-sr-ar-mapping.md)。
> 2. **索引/日志单轨制（2026-08-19 起）**：知识文件落盘后用 `kb-log-append.py` 追加摘要到**根** `knowledge/log.md`；**全库不再写子目录 index.md/log.md**（三件套禁编辑，根 index 由脚本批量刷新）。
> 3. **文件操作铁律**：永不 `rm`（mv 到 `tmp/bak/<原因>-<日期>/`）· 改前查头部约束标记（AUTO-GENERATED/DO NOT EDIT/MANAGED_BY）· 破坏性操作先问用户。
> 4. **文档质量门禁**：TOC + 交叉链接 + Changelog + 量化四要素（数值+单位+基线+条件）+ 来源标注，缺一不可。
> 5. **优先级**：L1🛑安全红线（否定，不可覆盖）> L2 工程约束 > L3 AGENT.md 行为准则 > L4 系统默认。
>
> **需求溯源**: 所有开发工作应可追溯到对应的 SR（用户需求）和 AR（技术需求），详见 [`sr-001-knowledge-system-requirements.md`](./sr-001-knowledge-system-requirements.md) 和 [`ar-001-sr-ar-mapping.md`](./ar-001-sr-ar-mapping.md)。
>
> **提升说明（2026-08-19，v3.1 → v4.0）**: ① 新增「结论先行（30 秒版）」；② §6 知识库管理对齐 **2026-08-19 索引/日志单轨制**新规则（废除双轨 index/log、无子目录索引、根 log.md 单轨追加），旧规则以「📌 备注（v3.1 原文）」保留；③ Changelog 由引用块改为标准表格；④ 章节 AR/CC 溯源核对。**旧内容未删除**，压缩保留于各章节备注块。

---

## 📑 目录

1. [总体设计规范](#1-总体设计规范)
2. [四阶段数据规范](#2-四阶段数据规范)
3. [文档规范](#3-文档规范)
4. [代码规范](#4-代码规范)
5. [资产清单管理规范](#5-资产清单管理规范)
6. [知识库管理规范](#6-知识库管理规范)
7. [自动化管线规范](#7-自动化管线规范)
8. [技能系统规范](#8-技能系统规范)
9. [Git 工作流规范](#9-git-工作流规范)
10. [质量审查规范](#10-质量审查规范)
11. [沟通与协作规范](#11-沟通与协作规范)

---
>
> **建议前置阅读**: sr-003-system-constraint-registry.md — 了解约束体系
>

## 1. 总体设计规范

> **实现 AR**: `AR-SYS-001`（身份文件体系）→ `AR-SYS-006`（约束体系引擎）→ `AR-SYS-007`（SSOT 治理）
> **对应约束**: `CC-01`（01001-01010 安全红线）→ `CC-02`（02101-02104 文件操作约束）

### 1.1 四阶段框架

```text
Phase 1 (收集)      Phase 2 (加工)      Phase 3 (优化)      Phase 4 (使用)
────────────────    ──────────────      ──────────────      ──────────────
import/             discover/           knowledge/           Web浏览
projects/           AI批量分析           Skills深度加工       Git同步

规则:
  素材仅存储          AI提取信息           多层质量门禁        索引完整
  不修改原文          去重分类              源可追溯            版本控制
```

### 1.2 MECE 分层原则

| 层次 | 应用 | 自检方法 |
|:-----|:------|:---------|
| 目录分类 | 同层互斥、完全穷尽 | 检查文件能否明确归入唯一目录 |
| 模块职责 | 每个模块有清晰边界 | 模块间不重叠、不依赖交叉引用 |
| Skills 定位 | 每个 Skill 有唯一定位 | 触发条件不冲突 |

### 1.3 指令优先级

| 优先级 | 类型 | 说明 |
|:------:|:-----|:------|
| **L1** 🛑 | 安全红线（否定指令） | 绝不触碰，不可覆盖 |
| **L2** 📋 | 工程约束 | 违反有明确后果 |
| **L3** 🧠 | AGENT.md 行为准则 | 人格设定 |
| **L4** 🤖 | 系统 prompt 默认行为 | 最底层默认 |

---

## 2. 四阶段数据规范

> **实现 AR**: `AR-P1-001`～`AR-P4-004`（全阶段数据规范）
> **对应约束**: `CC-05`（10301-10305 知识库写入约束）→ `CC-02`（03101-03108 路径映射约束）

### 2.1 Phase 1: 数据收集规范

| 输入类型 | 处理规范 | 目标位置 | 注意事项 |
|:---------|:---------|:---------|:---------|
| 本地 .md 文件/文件夹 | 直接复制，保留原始内容 | `import/` | 不修改原文 |
| 本地非 .md 文件 | 使用 markitdown / python-pptx / PaddleOCR 转为 .md | `import/` | 原文同时保留 |
| 公众号/网站内容 | 采集脚本 → 标准化后导入 | `import/` | 标注来源 URL |
| 工程文件夹 | 完整复制 | `projects/` | 保持目录结构 |
| 用户分享 URL | `web-archive` / `doubao-share` Skills | `knowledge/06_others/sources/` | 自动归档 |

### 2.2 Phase 2: 数据加工规范

| 加工方式 | 规范 | 产出要求 |
|:---------|:-----|:---------|
| AI 批量分析 | 每次分析记录来源路径、分析时间、AI 模型 | `discover/` 下注明分析元数据 |
| 去重审计 | 标题/摘要/关键段落三级去重 | 记录去重率与去重依据 |
| 分类推荐 | 基于知识库分类体系语义匹配 | 提供 Top-3 推荐目录 + 置信度 |

### 2.3 Phase 3: 数据优化规范

| 优化方式 | 规范 | 质量门禁 |
|:---------|:-----|:---------|
| 深度技术分析 | 六步工作流（数据→原理→对比→分析→结论→审查） | doc-reviewer 审查通过 |
| 文档归档 | TOC + 交叉链接 + Changelog 完整 | 格式检查通过 |
| 日常对话 → 知识 | 自动判断写入位置（sources/analysis/concepts/entities） | index.md + log.md 同步更新 |

### 2.4 Phase 4: 数据使用规范

| 使用方式 | 规范 | 要求 |
|:---------|:-----|:-----|
| Flask Web 浏览 | 目录导航 + Markdown 渲染 | 链接有效、渲染正确 |
| Git 同步 | 规范提交信息 | `feat/fix/docs/refactor/chore: 描述` |

---

## 3. 文档规范

> **实现 AR**: `AR-P3-001`～`AR-P3-004`（知识库写入流程）
> **对应约束**: `CC-04`（04101-04106 知识库格式约束）

### 3.1 文件命名

| 类型 | 命名规则 | 示例 |
|:-----|:---------|:-----|
| 知识文档 | `领域-子主题.md` | `ras-comprehensive-handbook.md` |
| 日跟踪日志 | `YYYY-MM-DD.md` | `2026-07-21.md` |
| 调研报告 | `领域-调研主题.md` | `ai-solutions-TRA.md` |
| 周报 | `weekly-report-YYYY-MM-DD.md` | `weekly-report-2026-07-20.md` |
| 技能文件 | `SKILL.md` | 固定名称 |
| 脚本 | `动词_名词.py` | `check_links.py` |
| 对话记录 | `YYYY-MM-DD.md` | `2026-07-21.md` |

**spec/ 文件前缀命名体系**（SSOT，所有文件引用此表）：

| 前缀 | 全称 | 用途 | 示例 |
|:----:|:-----|:-----|:-----|
| `design-` | Architecture Design | 架构设计方案 | `design-001-system-architecture.md` |
| `meth-` | Methodology | 方法论设计文档 | `meth-001-architecture-methodology.md` |
| `sr-` | System Requirement | 系统需求规格 | `sr-003-system-constraint-registry.md` |
| `std-` | Engineering Standard | 工程标准规范 | `std-002-knowledge-content-format.md` |
| `ar-` | Architecture Mapping | 架构需求映射 | `ar-001-sr-ar-mapping.md` |
| `audit-` | Compliance Audit | 合规审计报告 | `audit-001-constraint-compliance-audit.md` |
| `_archive/` | Archived Reports | 归档（非持续性规范） | `_archive/design-006-token-optimization_V3.7.md` |

### 3.2 文档结构规范

**长文档（>200 行）必须包含**：

1. **TOC 目录** — 置于文件顶部，使用锚点链接
2. **Changelog** — 置于文件底部，条目化、时间倒序
3. **交叉链接** — 覆盖 knowledge/ 下已有相关文件
4. **代码块纯 ASCII** — 图表用纯英文 ASCII，中文说明在外
5. **出处标注** — 每条关键断言有来源引用

### 3.3 内容质量标准

| 要求 | 说明 | 自检 |
|:-----|:-----|:-----|
| **量化四要素** | 数值 + 单位 + 对比基线 + 测试条件 | `吞吐提升 28.9%（vs BF16, A100, batch=32）` |
| **来源标注** | 关键数据/判断须附带来源 | 来源能说出来吗？ |
| **交叉验证** | 关键结论至少经 2 个独立来源验证 | 换渠道查同样数据，一致吗？ |
| **数据时效性** | 科技类数据优先引用 2025-2026 年最新 | 数据年份？有更新来源？ |
| **调研材料优先级** | 论文/标准 > 官方白皮书 > 一线报告 > 行业分析 > 技术博客 > 自媒体 | 按优先级降序选择 |

### 3.4 修改约束规则

**修改文件前，先检查文件头部（前 10 行）是否有约束标记**：

| 标记模式 | 含义 | 应对方式 |
|:---------|:-----|:---------|
| `> ⚠️ 注意：该文件由 X 自动生成` | 自动生成文件 | 优先通过生成工具修改 |
| `# DO NOT EDIT` | 不可编辑 | 不要修改 |
| `<!-- AUTO-GENERATED -->` | 自动生成 | 同自动生成文件处理 |
| `<!-- TEMPLATE: ... -->` | 基于模板生成 | 优先修改模板源文件 |
| `<!-- MANAGED_BY: ... -->` | 由外部工具管理 | 优先通过指定工具修改 |

---

## 4. 代码规范

> **实现 AR**: `AR-P3-008`～`AR-P3-009`（Skills 版本管理）
> **对应约束**: `CC-02`（06101-06105 代码/脚本约束）→ `CC-03`（08201-08205 Skills 行为约束）

### 4.1 语言与工具

- **Python**: 脚本/自动化管线首选语言，Python 3.10+
- **Shell**: Linux 环境批处理
  
### 4.2 Python 规范

```python
#!/usr/bin/env python3
"""模块级 docstring：一句话描述功能，详细说明另起段落。

用法:
  python script.py --arg1 value1

环境变量:
  ENV_VAR    说明
"""

# 标准库
import os
import sys
import argparse
from pathlib import Path

# 第三方库
import requests

# 本地模块


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="...")
    parser.add_argument("--flag", action="store_true", help="...")
    args = parser.parse_args()


if __name__ == "__main__":
    main()
```

**要求**：
- 每个脚本有 `argparse` 命令行接口
- 关键函数有 docstring
- 路径操作使用 `pathlib.Path`
- 外部 API 调用有重试机制和超时设置
- 错误信息输出到 stderr

### 4.3 脚本命名前缀

| 前缀 | 用途 | 示例 |
|:-----|:------|:------|
| `check_*` | 检查/验证 | `check_links.py` |
| `fix_*` | 修复 | `fix_index_links.py` |
| `generate_*` | 生成 | `generate_intent_report.py` |
| `import_*` | 数据导入 | `import_files.py` |
| `export_*` | 数据导出 | `export_db_sessions.py` |
| `reformat_*` | 格式重整 | `reformat_log.py` |

### 4.4 脚本命名与分类规范

| 目录/前缀 | 用途 | 命名示例 |
|:----------|:------|:---------|
| `autokb/` | 知识库导入管线 | `run_pipeline.py` / `importer.py` |
| `check/` | 质量检查/验证 | `link-validator.py` / `md-format.py` / `analyze-index-coverage.py` |
| `tools/` | 独立工具类 | `html-to-markdown.py` / `chromedriver-setup.py` |
| `git/` | 版本控制工具 | `git-push-robust.py` / `git-pull-robust.py` |
| `intent_analysis/` | 意图分析 | `main.py` / `generate_intent_report.py` |
| `backup/` | 历史脚本（待清理） | 不新增，仅评估现有 |
| `knowledge-sync-optimizer.py` | 同步优化器 | 根级独立功能 |

**约束**：
- 新脚本归入对应子目录，不放在 `scripts/` 根级
- 禁止在 `backup/` 中新增文件，仅用于历史存档
- 根级别名只用于向后兼容，新调用使用子目录路径

---

## 5. 资产清单管理规范

> **实现 AR**: `AR-ASM-001`～`AR-ASM-006`（所有资产清单 AR）
> **对应约束**: `CC-02`（06101-06105 代码/脚本约束）

### 5.1 Scripts 资产规范

| 规范项 | 要求 |
|:-------|:------|
| 自动生成清单 | 新脚本创建后自动更新 README.md §9 的脚本分类表（AR-ASM-001） |
| Backup 清理 | 每季度评估 `scripts/backup/`，有价值→迁移/废弃→标注（SR-028） |
| 根级别名维护 | 文件移动后在 `scripts/` 根目录创建软链接并记录在别名表 |
| 映射同步 | Skills 引用的脚本变更时更新 `scripts/skills-scripts-mapping.md`（SR-030） |

### 5.2 Skills 资产规范

| 规范项 | 要求 |
|:-------|:------|
| 来源标注 | 每个技能在 `skills_config.json` 中标注来源（custom/clawhub/cowhub/github/linkai） |
| 状态管理 | 新技能默认 enabled=true；缺依赖的标注 missing 状态 |
| 使用频率 | 每季度统计一次 Skills 调用频率（AR-ASM-004），输出活跃/低频/闲置分类 |
| 闲置处理 | 低频技能评估合并或移除，移除前告知用户（SR-029） |
| 环境变量 | 待激活技能（需 API Key）在 `skills_config.json` 中标注缺失环境变量名 |

### 5.3 映射表维护规范

| 规范项 | 要求 |
|:-------|:------|
| 维护位置 | `scripts/skills-scripts-mapping.md`（按技能→脚本） + `scripts/README.md`（按操作类型） |
| 更新触发 | 技能创建/安装/更新/删除后同步更新两张映射表 |
| 自动同步 | 🚧 待开发 AR-ASM-005 |
| 最少频率 | 每季度至少一次全量同步 |

---

## 6. 知识库管理规范

> **实现 AR**: `AR-P3-011`（Index+Log 自动维护）→ `AR-SYS-007`（SSOT 治理）
> **对应约束**: `CC-04`（05101-05103 索引/日志约束）

### 6.1 写入规则

> 🆕 **2026-08-19 更新**: 索引/日志由「双轨制」（全局 index.md + log.md）改为**单轨制**（根 log.md 单轨追加，无子目录索引/日志）。本节已对齐新规则，旧规则见文末备注。

**必须做**：
- 技术材料 → 立即归档 `knowledge/`（无需征求确认），按存储规则先判频率再定位置（>1 周不放 memory/，<1 月不放 MEMORY.md）
- 学到知识后主动写入，交叉引用已有相关文件
- 知识文件落盘后更新**根** `knowledge/log.md`（单轨，见下方 §6.2）

**索引/日志单轨制（2026-08-19 起）**：
- 知识文件 → 摘要写 `tmp/kb-log-draft-<date>.md`（不含分节头）→ `python3 scripts/tools/kb-log-append.py --file <draft> --section <模块>` 追加到**根** `knowledge/log.md`（自动备份+查重）
- **全库无子目录 index.md/log.md**——不再写任何子目录索引/日志；子目录 `README.md` 保留（描述长期内容）
- 根 `README.md` / `index.md` / `log.md` 三件套**禁止 AI 直接编辑**：根 index 由 `kb-global-index.py` 批量刷新，根 log 只经 kb-log-append.py 追加

**禁止做**：
- 不要直接删除文件——使用 `mv` 移动到 `tmp/bak/<原因>-<日期>/`（**永不 rm**）
- 不要在 index 中混入日志内容
- 不要引用尚未创建的文件
- 不要将 `tmp/bak/` 中的内容作为参考来源
- 不要写任何子目录 `index.md`/`log.md`

> 📌 **备注（v3.1 原文，2026-08-19 已废弃）**: 旧规则要求「每次写入知识库同步更新 `index.md` 和 `log.md`」，维护全局 index.md/log.md 双轨。2026-08-19 起废弃双轨制（RULE.md「三件套」决策：三职责分离——README 条目库 + index 自动生成 + log 全局账本；AI 只经脚本追加根 log），旧文保留备查。

### 6.2 索引规范（单轨制，2026-08-19 起）

```text
根 knowledge/log.md 格式（唯一写入点，经 kb-log-append.py 追加）:
| 日期 | 操作 | 文件 | 说明 |
|:----|:-----|:-----|:------|
| 2026-08-19 | 新增 | <模块>/<文件>.md | 说明内容 |

根 knowledge/index.md：由 kb-global-index.py 批量刷新，AI 不手工编辑。
子目录：无 index.md/log.md（2026-08-19 起全库统一），保留 README.md 描述长期内容。
```

> 📌 **备注（v3.1 原文，已废弃）**: 旧规范展示 `knowledge/index.md`（文件|标题|摘要|日期）与 `knowledge/log.md`（日期|操作|文件|说明）双轨格式。双轨制 2026-08-19 废弃，根 index 交由脚本自动生成，AI 仅经 kb-log-append.py 追加根 log。

### 6.3 质量审计

| 审计项 | 频率 | 工具 |
|:-------|:-----|:------|
| 链接有效性 | 每月 | `check_links.py` |
| 索引完整性 | 每月 | `knowledge_health_check.py` |
| 格式规范 | 文档写入时 | `check_md_format.py` |
| 目录 MECE 审计 | 每季度 | 人工 + AI 辅助 |

---

## 7. 自动化管线规范

> **实现 AR**: `AR-SYS-004`（定时任务调度框架）
> **对应约束**: `CC-05`（12301-12305 定时任务约束）

### 7.1 管线架构

```text
Phase 1      Phase 2       Phase 3        Phase 4
数据获取 →  数据加工 →   知识生成 →    专题产出
  │            │            │            │
  ▼            ▼            ▼            ▼
import/      autokb/      Skills       weekly-reports/
采集脚本      去重/分类     深度分析     专题报告
```

### 7.2 调度任务规范

- 日跟踪任务：21:00–06:15 之间，每 30 分钟一个槽位
- 周报生成：每周日 07:00 自动生成
- 文件链接检查：每月定期运行
- 新增任务：避开已有时间槽（见 README.md §10 定时任务体系）

### 7.3 自动化原则

- 先完成自动化，再向自动演化方向演进
- 每个自动化脚本有独立可运行的能力
- 失败时输出明确的错误信息

---

## 8. 技能系统规范

> 📎 **补充规范**: Skills 设计层面的详细要求（分类体系、合规审计、映射关系等）见 [`design-007-skills-scripts-design.md`](./design-007-skills-scripts-design.md)。本文件 §8 聚焦工程规范视角（注册、匹配、加载），design-007 聚焦设计合规视角（版本管理、映射验证、质量验证）。

> **实现 AR**: `AR-P3-008`～`AR-P3-009`（Skills 版本管理与自动安装）

### 8.1 技能目录结构

```text
skill-name/
├── SKILL.md              # 技能描述 + 触发条件 + 执行流程（核心）
├── scripts/              # 技能专用脚本
│   └── tool.py
├── resources/            # 技能资源文件
│   └── template.md
└── README.md             # 技能说明
```

### 8.2 SKILL.md 规范

SKILL.md 必须包含以下结构：

```markdown
# Skill Name

## Description
技能描述（触发条件、使用场景）

## Usage
使用方法和触发词

## Workflow
执行流程步骤

## Inputs
需要的输入参数

## Outputs
产出物和存储位置
```

### 8.3 技能开发规范

- 每个技能有独立的目录
- 技能内部脚本保持在 `skills/<name>/` 目录下
- 创建 → 审查 → 迭代闭环
- 关键数据必须在 Skill 内部交叉验证

### 8.4 Skills 质量验证规范

| 验证项 | 触发条件 | 验证方式 | 违规处理 |
|:-------|:---------|:---------|:---------|
| SKILL.md 完整性 | 创建/更新 Skill 后 | `validate-skills.py` 检查必须字段（Description/Workflow/Inputs/Outputs） | 缺失字段须补充后才能标记为可用 |
| 内部脚本路径 | 创建/更新 Skill 后 | `validate-skills.py` 检查 `skills/<name>/scripts/` 下引用文件存在 | 路径修正或创建占位脚本 |
| Knowledge 引用 | 创建/更新 Skill 后 | `validate-skills.py` 检查 SKILL.md 中 `knowledge/` 路径可达 | 标红提示，需人工确认 |
| skills_config.json | 创建/删除/更新 Skill 后 | 自动审计 enabled 字段与实际状态一致性 | 自动同步不一致项 |
| 映射表同步 | 创建/删除/更新 Skill 后 | 验证 `scripts/skills-scripts-mapping.md` 与实际一致 | 自动触发映射表更新流程 |
| 定期全量验证 | 每周一 02:00 / 每月 1 日 02:00 | `validate-skills.py --mode=full` | 生成验证报告，异常项写入 `tmp/validate/` |
| 工具链可用性 | 每周 | 检查脚本依赖的 Python 包/系统命令 | 标注缺失依赖到验证报告 |

### 8.5 Scripts 质量验证规范

| 验证项 | 触发条件 | 验证方式 | 违规处理 |
|:-------|:---------|:---------|:---------|
| Python 语法 | 创建/修改脚本后 | `py_compile.compile()` 编译检查 | 语法错误必须修复 |
| Shell 语法 | 创建/修改 `.sh` 文件后 | `bash -n` 检查 | 语法错误必须修复 |
| CLI 接口 | 创建/修改脚本后 | `--help` 参数返回 0 | 补充 argparse 入口 |
| 路径有效性 | 创建/修改脚本后 | 正则扫描脚本中 `knowledge/` `import/` 等路径，验证存在性 | 失效路径标红 |
| Knowledge 引用 | 创建/修改脚本后 | 路径存在性 + 与当前目录结构匹配 | 引用失效须修正 |
| 定期语法检查 | 每月 1 日 03:00 | `validate-scripts.py --mode=syntax` | 生成语法检查报告 |
| 定期路径检查 | 每月 1 日 03:30 | `validate-scripts.py --mode=paths` | 生成路径失效清单 |

### 8.6 Knowledge 变化自适应规范

当 knowledge 目录结构有变更时（文件移动/重命名/删除）：

| 步骤 | 操作 | 工具 |
|:-----|:------|:------|
| 1 | 扫描所有 skills/*/SKILL.md 中引用的 `knowledge/` 路径 | `track-knowledge-refs.py` |
| 2 | 扫描所有 scripts/*.py 中引用的 `knowledge/` 路径 | `track-knowledge-refs.py` |
| 3 | 扫描 `scripts/skills-scripts-mapping.md` 中的路径 | `track-knowledge-refs.py` |
| 4 | 与当前 `knowledge/` 目录对比，输出失效清单 | 自动比对 |
| 5 | 失效路径分类：可自动修正（路径变更）vs 需人工确认（内容已移除） | 生成修复建议 |
| 6 | 批量更新确认的路径变更 | 脚本自动执行 |

---

## 9. Git 工作流规范

> **实现 AR**: `AR-P4-002`（Git 同步体系）

### 9.1 分支策略

- `main` — 主分支，保持稳定
- 直接在 `main` 上工作（个人项目，无需 feature 分支）

### 9.2 提交规范

**格式**: `<type>: <简短描述>`

| Type | 说明 |
|:-----|:------|
| `feat` | 新功能 |
| `fix` | 修复 |
| `docs` | 文档变更 |
| `refactor` | 重构 |
| `chore` | 杂项（脚本、配置等） |

**示例**：
```
feat: 添加 RAS 综合设计手册第 8 章
fix: 修复自动化率公式错误
docs: 更新 README 四阶段数据流架构
```

### 9.3 安全原则

- 不提交敏感文件（.env, credentials, tokens）
- 不执行 `git push --force` 到 main
- 不运行 `git reset --hard` 等破坏性命令

---

## 10. 质量审查规范

> **实现 AR**: `AR-QSV-001`～`AR-QSV-006`（所有质量验证 AR）
> **对应约束**: `CC-05`（11301-11305 审查验证约束）→ `CC-03`（07201-07206 质量标准）

### 10.1 三层审查体系

| 层级 | 检查内容 | 严重度 |
|:-----|:---------|:------:|
| **结构层** | 章节编号、TOC 一致性、链接有效性、跨文件引用完整性 | 🔴 阻断 |
| **逻辑层** | 13 条逻辑谬误扫描、论证完整性、数据一致性、维度对齐 | 🟡 警告 |
| **来源层** | 信息来源可追溯性、数据时效性、交叉验证 | 🔴 阻断 |

### 10.2 13 条逻辑谬误预防清单

> **SSOT**: 本清单的权威版本见 `RULE.md §F`（系统约束谬误对应表）。此处为摘要引用，内容以 RULE.md 为准。

1. 声明-实践不一致 → 穿行测试
2. 先验分类 → 溯源追问
3. 模型几何不相容 → 画空间结构
4. 术语漂移 → 术语溯源
5. 类比当定理 → 措辞诚实化
6. 内部冲突未检视 → 集中陈列法
7. 伪结构/假密度 → 合并测试
8. 空洞同构 → 差异优先法
9. 维度混淆 → 再分类法
10. 诠释学循环 → 证伪性自检
11. 假精确 → 单位追问
12. 结论前置 → 论证优先
13. 二元对立 → 多元方案表

### 10.3 审查工具

| 工具 | 用途 | 运行方式 |
|:-----|:------|:---------|
| `check_tech_doc_quality.py` | 技术文档质量自检 | `python3 scripts/check_tech_doc_quality.py <file>` |
| `review_doc.py` | 文档审查脚本 | `python3 scripts/review_doc.py <file>` |
| `check_links.py` | 链接有效性检测 | `python3 scripts/check_links.py` |
| `check_md_format.py` | 格式规范检查 | `python3 scripts/check_md_format.py <file>` |

### 10.4 产出质量门禁

每次交付前自检：
- [ ] 断言有出处？来源可追溯？
- [ ] 数据：数值 + 单位 + 基线 + 条件，缺一不可？
- [ ] 文档：TOC + 交叉链接 + Changelog？
- [ ] 框架堆名词不深入原理 → 不合格
- [ ] 数据无法获取时：标注缺口 + 说明尝试了哪些源 + 给出替代估算？
- [ ] 有无编造数据/引用/百分比？

---

## 11. 沟通与协作规范

> **实现 AR**: `AR-SYS-001`（身份文件体系）

### 11.1 提问规范

**提问前三问**：
1. 我最想要什么？（目标）
2. AI 不知道什么？（约束）
3. 输出要什么形式？（格式）

### 11.2 反馈闭环

输出 → 接收反馈 → 修正 → 复盘，迭代速度决定成长速度。

### 11.3 存储规则（根据内容频率匹配位置）

| 信息类型 | 存放位置 | 变化频率 |
|:---------|:---------|:--------:|
| Agent 人格/行为 | AGENT.md | 季更 |
| 用户身份/偏好 | USER.md | 年更 |
| 长期事实/决策/教训 | MEMORY.md | **月更** |
| 当天进展/讨论记录 | memory/YYYY-MM-DD.md | 日更 |
| 行业新闻/竞争动态/调研 | knowledge/01_survey/ | 日/周更 |
| 技术文章/文档归档 | knowledge/06_others/sources/ | 一次性 |
| 方法论/质量原则 | knowledge/concepts/ | 月/季更 |
| 临时草稿/中间产物 | tmp/ | 随用随删 |

**判据**: 写之前判"多久更新一次？" → 超1周不该放 memory/，少1个月不该放 MEMORY.md

---

## 附录：关键文件索引

| 文件 | 用途 |
|:-----|:------|
| [AGENT.md](../AGENT.md) | AI 助理身份与性格设定 |
| [USER.md](../USER.md) | 用户基本信息 |
| [RULE.md](../RULE.md) | 工作空间规则 |
| [MEMORY.md](../MEMORY.md) | 长期记忆索引 |
| [README.md](../README.md) | 项目总体架构与规划 |
| [spec/design-001-system-architecture.md](design-001-system-architecture.md) | 系统架构规格说明 |
| [spec/design-003-knowledge-directory-design.md](design-003-knowledge-directory-design.md) | Knowledge 目录设计与文件变更规范 |
| [scripts/skills-scripts-mapping.md](../scripts/skills-scripts-mapping.md) | Skills ↔ 脚本映射表 |

---

## Changelog

| 日期 | 版本 | 变更 |
|:-----|:----:|:-----|
| 2026-08-19 | **v4.0** | **全面提升**：① 头部新增「结论先行（30 秒版）」+ 状态字段；② §6 知识库管理对齐 2026-08-19 索引/日志单轨制（根 log.md 单轨追加 + kb-log-append.py + 无子目录 index/log），旧双轨规则以「📌 备注」保留；③ Changelog 引用块 → 标准表格；④ 文件操作铁律对齐 tmp/bak 回收机制（永不 rm）；⑤ 修正 v3.1 变更记录中的章节号引用（§9.4→§8.4 等，与当前章节一致） |
| 2026-07-21 | v3.1 | 新增 Skills 质量验证规范（7 项检查）、Scripts 质量验证规范（7 项检查）、Knowledge 变化自适应规范（6 步流程）（现 §8.4/§8.5/§8.6） |
| 2026-07-21 | v3.0 | 新增 §5 资产清单管理规范（Scripts/Skills 资产 + 映射表维护），新增 §4.4 脚本命名与分类规范，section 编号全面更新（§5→§7, §6→§8, ..., §10→§12）以容纳新章节 |
| 2026-06-27 | v1.0 | 初始版本 |
