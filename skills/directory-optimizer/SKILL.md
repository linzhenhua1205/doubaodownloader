---
name: directory-optimizer
description: |-
  Knowledge directory architecture optimization: MECE layering, cross-domain coupling analysis, reading path design, decision framework indexing, and comprehensive index.md generation. Triggers: 目录优化、目录架构、MECE分析、关联矩阵、阅读路径、目录增强、知识目录重构、目录深度分析、index生成、知识库目录设计、跨文件关联.
metadata:
  requires:
    bins: ["python3"]
  emoji: 🏗️
---

# 目录架构优化器 🏗️

> 对知识目录进行深度架构优化：MECE 分层、跨域关联矩阵、阅读路径、决策框架索引，生成结构化的 index.md，强化内容关联性与一致性。

---

## 快速入口

**核心脚本**: `scripts/check/directory-architect.py`

一键生成目录级 index.md（包含 MECE 分层、关联矩阵、阅读路径等）：

```bash
# 分析目录（不生成文件，查看统计）
python3 scripts/check/directory-architect.py knowledge/xx_module/yy_dir --analyze-only

# 预览生成结果（dry-run）
python3 scripts/check/directory-architect.py knowledge/xx_module/yy_dir --dry-run

# 生成 index.md（不存在时创建）
python3 scripts/check/directory-architect.py knowledge/xx_module/yy_dir

# 强制覆盖已有 index.md
python3 scripts/check/directory-architect.py knowledge/xx_module/yy_dir --force

# JSON 输出（便于程序处理）
python3 scripts/check/directory-architect.py knowledge/xx_module/yy_dir --json
```

---

## 工作流程

```
┌──────────────────────────────────────────────────────────────┐
│  1. 元数据提取                                                │
│     ├─ 标题（H1）                                            │
│     ├─ 一句话摘要                                            │
│     ├─ 行数/大小                                             │
│     └─ 头部元数据（定位/关联/版本）                           │
│                              ↓                               │
│  2. MECE 自动分层（L1-L6）                                    │
│     ├─ L1 总纲层：系统观/方法论                              │
│     ├─ L2 专题概述层：领域概览/选型决策                      │
│     ├─ L3 设计指南层：落地方法/选型指南/常见坑                │
│     ├─ L4 审查Checklist层：评审清单/跨域协同                 │
│     ├─ L5 深度分析层：前沿技术/架构权衡                      │
│     └─ L6 归档素材层：历史outline/原始素材                   │
│                              ↓                               │
│  3. 跨领域关联矩阵（关键词共现分析）                          │
│                              ↓                               │
│  4. 阅读路径生成（入门/深潜/实战 三条路径）                   │
│                              ↓                               │
│  5. 决策框架索引（汇总所有方法论/决策工具）                   │
│                              ↓                               │
│  6. 一致性评估（定位/关联/版本覆盖率）                       │
│                              ↓                               │
│  7. 生成 index.md                                            │
└──────────────────────────────────────────────────────────────┘
```

---

## 1. 元数据提取

**脚本**: `scripts/check/extract-index-metadata.py` （已有工具）

```bash
# 批量提取文件标题和摘要
python3 scripts/check/extract-index-metadata.py knowledge/xx_dir
```

**提取内容**:
- 文件标题（第一个 `# ` 标题）
- 一句话摘要（标题后第一段非元数据文本）
- 行数、文件大小

---

## 2. MECE 自动分层

基于文件名和标题关键词，自动将文件归入 6 个层级：

| 层级 | 名称 | 核心特征 | 判断关键词 |
|:----:|:-----|:---------|:-----------|
| L1 | 总纲层 | 系统观、跨域框架、方法论 | 核心、总纲、系统观、方法论、02-core |
| L2 | 专题概述层 | 领域概览——是什么/为什么/怎么选 | 专题、概述、扩充版、行业趋势、供应链、03-/05-/08-/09-/10-/12-/13-/14-/15- |
| L3 | 设计指南层 | 详细指南——怎么做/选型/坑 | 设计指南、设计规范、深潜、剖析、16-~32- |
| L4 | 审查层 | Checklist——不漏项 | checklist、审查、互审、评审、33-/34-/35- |
| L5 | 深度分析层 | 前沿/权衡/芯片级 | 深度解读、权衡分析、spec-analysis、tradeoff |
| L6 | 归档素材层 | `_` 开头的目录 | `_interconnect/`、`_reference/`、`_doubao/` 等 |

> **MECE 原则**：
> - **互斥（ME）**：每篇文件只有一个主层级，不重复归类
> - **穷尽（CE）**：所有文件都被归入某个层级，没有遗漏
> - 人工审核：自动分类后建议人工调整边界文件

---

## 3. 跨领域关联矩阵

基于文件内容的关键词共现分析，自动识别各领域间的耦合关系。

**识别的领域**（可扩展）：
互联、供电、散热、信号、结构、EMC、时钟、内存、DFX、管理

**耦合强度**:
- 🟥 强耦合（███）：≥ 5 个文件同时涉及两个领域
- 🟧 中耦合（██）：≥ 3 个文件同时涉及
- 🟩 弱耦合（█）：≥ 1 个文件同时涉及

**用途**:
- 快速发现跨域依赖关系
- 识别需要重点协同的设计接口
- 指导评审时的跨域检查项

---

## 4. 阅读路径生成

自动生成 3 条推荐阅读路径：

| 路径 | 目标读者 | 组成 |
|:-----|:---------|:-----|
| **A 入门路径** | 新人上手 | 总纲 → 核心专题概述 → 第一个子系统 |
| **B 深潜路径** | 专家方向 | 设计指南 → 深度分析 → 归档专题 |
| **C 实战路径** | 项目流程 | 总纲 → HLD Checklist → 设计指南 → Review Checklist |

---

## 5. 决策框架索引

自动扫描全目录，汇总所有可用于设计决策的方法论和框架：

- 选型决策树
- 权衡分析框架
- Checklist 体系
- 设计原则排序
- 流程方法论

**用途**：快速定位"遇到 XX 问题该看哪个文件"。

---

## 6. 一致性评估

自动评估目录内文件的头部元数据一致性：

| 指标 | 说明 | 建议阈值 |
|:-----|:-----|:--------:|
| 定位说明覆盖率 | 文件头部是否有「定位」/「范围」说明 | ≥ 90% |
| 关联文档覆盖率 | 是否有「关联文档」/上下游引用 | ≥ 80% |
| 版本/日期覆盖率 | 是否标注版本号或更新日期 | ≥ 90% |

---

## 7. 生成的 index.md 结构

自动生成的 index.md 包含以下章节：

```
# 📂 {目录名} 知识目录
├── 元数据（文件数、子目录数、生成时间）
├── 目录导航
├── 1 整体架构图（六层金字塔 ASCII 图）
├── 2 MECE 分层结构
│   ├── L1 总纲层（文件表格）
│   ├── L2 专题概述层（文件表格）
│   ├── L3 设计指南层（文件表格）
│   ├── L4 审查/Checklist 层
│   ├── L5 深度分析层
│   └── L6 归档素材层（子目录列表）
├── 3 跨领域关联矩阵
│   ├── 耦合矩阵表
│   └── 最强耦合对 TOP6
├── 4 推荐阅读路径
│   ├── A 入门路径
│   ├── B 深潜路径
│   └── C 实战路径
├── 5 核心参考速查
│   ├── 最详尽文档 TOP5
│   └── Checklist 汇总
├── 6 决策框架索引
├── 7 一致性评估与规范
│   ├── 元数据一致性统计
│   ├── 交叉引用约定
│   ├── 内容分层原则
│   └── 已知问题与待完善
└── 8 变更记录
```

---

## 完整工作流示例

### 场景：新接手一个知识目录，需要优化架构

```bash
# Step 1: 分析现状
python3 scripts/check/directory-architect.py knowledge/02_rd/03_hardware/01_hw_core --analyze-only

# Step 2: 预览生成的 index
python3 scripts/check/directory-architect.py knowledge/02_rd/03_hardware/01_hw_core --dry-run

# Step 3: 生成 index.md
python3 scripts/check/directory-architect.py knowledge/02_rd/03_hardware/01_hw_core

# Step 4: 运行规范化流水线（链接修复 + 裸引用增强）
python3 scripts/check/knowledge-normalizer.py \
    --module 02_rd/03_hardware/01_hw_core \
    --only links,augment --fix

# Step 5: 人工审核与调整
# - 调整 MECE 分层的边界文件归类
# - 丰富阅读路径描述
# - 补充跨域关联说明
# - 完善已知问题清单
```

### 场景：定期检查目录健康度

```bash
# 快速检查一致性和覆盖率
python3 scripts/check/directory-architect.py knowledge/xx_dir --analyze-only

# 配合知识库规范化工具
python3 scripts/check/knowledge-normalizer.py --module xx_dir
```

---

## 与其他 Skill 的关系

| Skill | 侧重点 | 关系 |
|:------|:-------|:-----|
| **index-deep-analyzer** | index.md 覆盖率、文件纳管、链接修复 | **互补**：先确保覆盖率 100%，再做架构优化 |
| **knowledge-wiki** | 知识条目增删改、索引维护 | **互补**：wiki 管单条知识，本 skill 管目录架构 |
| **knowledge-normalizer** | 一站式规范化（index/log/links/augment/format） | **前置依赖**：规范化后再做架构优化效果更佳 |

> **推荐组合流程**：
> `knowledge-normalizer（规范化）` → `directory-optimizer（架构优化）` → 人工审核

---

## 脚本清单

| 脚本 | 用途 |
|:-----|:-----|
| `scripts/check/directory-architect.py` | **核心脚本** — 目录架构分析 + index.md 生成 |
| `scripts/check/extract-index-metadata.py` | 批量提取文件元数据（标题、摘要、行数） |
| `scripts/check/knowledge-normalizer.py` | 知识库规范化流水线（前置步骤） |
| `scripts/check/link-validator.py` | 链接有效性检查与修复 |
| `scripts/check/link-augmenter.py` | 裸引用检测与链接增强 |

---

## 自定义扩展

### 添加新的分层规则

编辑 `directory-architect.py` 中的 `LAYER_RULES` 列表：

```python
{
    'id': 'Lx',
    'name': '层级名称',
    'name_en': 'English Name',
    'icon': '🎯',
    'description': '一句话说明',
    'keywords_title': ['关键词1', '关键词2'],
    'keywords_filename': ['filename-pattern'],
},
```

### 添加新的领域关键词

编辑 `DOMAIN_KEYWORDS` 字典：

```python
'领域名': ['keyword1', 'keyword2', '中文关键词'],
```
