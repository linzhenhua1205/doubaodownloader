---
name: index-deep-analyzer
description: |-
  ⚠️ 已废弃 — 请使用 skills/knowledge-index-manager/SKILL.md（统一索引管理技能）
  原功能（深度分析、规范化流水线、覆盖率/链接/格式检查）已合并至 knowledge-index-manager 的 audit/normalize 模式。
  保留本文件仅用于向后兼容，新操作请使用新技能。
metadata:
  replaces_by: skills/knowledge-index-manager/SKILL.md
  emoji: 🔍
---

# Knowledge Base Normalizer 🔍

> 知识库一站式规范化：index.md 覆盖率补全、log.md 格式化、链接修复、裸引用增强、格式检查。

---

## 快速入口：一站式规范化

**脚本**: `scripts/check/knowledge-normalizer.py`

一键执行完整规范化流水线（5 个阶段），安全默认为 dry-run：

```bash
# 全库 dry-run（预览所有问题，不修改文件）
python3 scripts/check/knowledge-normalizer.py

# 全库应用修复
python3 scripts/check/knowledge-normalizer.py --fix

# 仅处理某个模块
python3 scripts/check/knowledge-normalizer.py --module 02_rd --fix

# 只跑指定阶段
python3 scripts/check/knowledge-normalizer.py --only links,augment --fix

# 跳过某些阶段
python3 scripts/check/knowledge-normalizer.py --skip format
```

**5 个阶段**（按执行顺序）：

| # | 阶段 | 脚本 | 说明 |
|:-:|:-----|:-----|:-----|
| 1 | index | `analyze-index-coverage.py` | index.md 覆盖率分析 + 自动补全 |
| 2 | log | `reformat-log.py` | log.md 格式重排 + 日期排序 |
| 3 | links | `link-validator.py` | 链接有效性检查 + 自动修复 |
| 4 | augment | `link-augmenter.py` | 裸文件名引用 → 自动添加链接 |
| 5 | format | `md-format.py` | Markdown 格式规范检查（只读） |

---

## 工作流程（单模块深度分析）

```
┌─────────────────────────────────────────────────────────┐
│  1. 覆盖率分析          analyze-index-coverage.py       │
│     ↓                                                   │
│  2. 元数据提取          extract-index-metadata.py       │
│     ↓                                                   │
│  3. 深度分析缺失文件    并行 subagent / 手动读取        │
│     ↓                                                   │
│  4. 合并到 index.md     编辑 index.md                   │
│     ↓                                                   │
│  5. 链接检查            link-validator.py               │
│     ↓                                                   │
│  6. 裸引用增强          link-augmenter.py               │
│     ↓                                                   │
│  7. 格式检查            md-format.py + reformat-log.py  │
│     ↓                                                   │
│  8. 验证覆盖率          analyze-index-coverage.py       │
└─────────────────────────────────────────────────────────┘
```

---

## 1. 覆盖率分析（支持全库）

**脚本**: `scripts/check/analyze-index-coverage.py`

```bash
# 单模块分析
python3 scripts/check/analyze-index-coverage.py knowledge/<module>

# 生成可用的 index 条目（含缺失文件的标题和摘要）
python3 scripts/check/analyze-index-coverage.py knowledge/<module> --generate-entries

# 全库扫描（所有模块汇总报告）
python3 scripts/check/analyze-index-coverage.py --all

# 全库自动补全（追加缺失条目到 index.md 末尾）
python3 scripts/check/analyze-index-coverage.py --all --fix

# JSON 输出（便于程序处理）
python3 scripts/check/analyze-index-coverage.py --all --json
```

**输出指标**:
- 内容文件总数（排除 index.md/log.md/README.md）
- 已纳管文件数
- 缺失文件数
- 无效引用数
- 覆盖率百分比

**自动补全机制**:
- `--fix` 模式下，在 index.md 末尾追加「补全条目（自动生成）」章节
- 按顶层目录分组，以表格形式列出缺失文件的标题和摘要
- 自动更新头部的文件总数统计
- ⚠️ 补全条目需要人工审核后归入对应章节

---

## 2. 元数据提取

**脚本**: `scripts/check/extract-index-metadata.py`

```bash
# Markdown 表格格式
python3 scripts/check/extract-index-metadata.py knowledge/<module>

# JSON 格式（便于程序处理）
python3 scripts/check/extract-index-metadata.py knowledge/<module> --format json
```

**提取内容**:
- 文件标题（第一个 `# ` 标题）
- 一句话摘要（标题后第一段非元数据文本）
- 行数、文件大小

---

## 3. 深度分析缺失文件

对于覆盖率 < 100% 的模块，对每个缺失文件进行深度分析：

### 方法 A: 并行 Subagent（推荐，适用于大批量）

将缺失文件按子目录分组，每组分配一个 subagent：

```
Agent 1 → 分析 子目录A 的缺失文件
Agent 2 → 分析 子目录B 的缺失文件
Agent 3 → 分析 子目录C 的缺失文件
Agent 4 → 分析 子目录D 的缺失文件
```

每个 subagent：
1. 读取覆盖率报告获取缺失文件列表
2. 读取每个文件的前 30 行
3. 生成 50-80 字中文摘要
4. 输出 markdown 表格格式的补丁文件

### 方法 B: 手动分析（适用于少量文件）

```bash
# 生成覆盖率报告（含条目）
python3 scripts/check/analyze-index-coverage.py knowledge/<module> --generate-entries > _coverage_report.md

# 手动读取缺失文件，编辑 index.md
```

### 摘要质量要求

- **准确**: 基于文件实际内容，不编造
- **简洁**: 50-80 字中文
- **信息量**: 包含文件主题、核心内容、版本（如有）
- **格式**: `[文件名](路径) — 摘要内容`

---

## 4. 合并到 index.md

将补丁内容合并到 index.md 的正确位置：

1. **保留现有条目**: 不删除任何已有的有效条目
2. **按子目录归位**: 新条目放在对应子目录的表格中
3. **新子目录**: 在合适位置创建新章节
4. **清理无效引用**: 删除指向不存在文件的链接
5. **更新统计**: 文件数、日期、目录概览表

### index.md 格式规范

```markdown
# 🔬 模块名 `XX_module/`

> 📅 **文件统计**: 共 **N 个文件**（M 个子目录）
> **规则说明**:
> - 本文件仅维护文件清单，**不记录修订历史**
> - 修订记录请见 [`log.md`](log.md)

---

## 目录结构概览

| # | 子目录 | 文件数 | 说明 |
|:-:|:-------|:-----:|:-----|
| 01 | [`子目录/`](子目录/index.md) | N | 说明 |

---

## 子目录名

N 个文件，简述。

| 文件 | 一句话概述 |
|:-----|:----------|
| [`file.md`](子目录/file.md) | 摘要内容 |
```

---

## 5. 链接检查

**脚本**: `scripts/check/link-validator.py`

```bash
# 检查单个文件
python3 scripts/check/link-validator.py --file <module>/index.md --report

# 检查整个模块
python3 scripts/check/link-validator.py --module <module> --report

# 显示修复建议
python3 scripts/check/link-validator.py --file <module>/index.md --suggest

# 自动修复
python3 scripts/check/link-validator.py --file <module>/index.md --fix --dry-run
python3 scripts/check/link-validator.py --file <module>/index.md --fix
```

**检查类型**:
- DEPTH: 路径深度错误
- MOVED: 文件已移动
- DIR_RENAME: 目录已重命名
- MISSING: 文件不存在

---

## 6. 裸引用增强（自动添加链接）

**脚本**: `scripts/check/link-augmenter.py`

扫描所有 .md 文件，检测文本中出现的文件名/标题（裸引用），自动添加 markdown 链接。

```bash
# 全库 dry-run（预览将添加的链接）
python3 scripts/check/link-augmenter.py --dry-run

# 全库应用
python3 scripts/check/link-augmenter.py --fix

# 仅处理某个模块
python3 scripts/check/link-augmenter.py --module 02_rd --fix

# 仅处理单个文件
python3 scripts/check/link-augmenter.py --file 02_rd/some-page.md --dry-run
```

**匹配规则**:
- 匹配文件名（stem）和文件标题（H1）
- 同一模块内的文件优先匹配
- 跳过代码块、行内代码、已有链接、URL、HTML 标签
- 跳过标题行（不在 H1-H6 中添加链接）
- 仅匹配完整单词（避免部分匹配）

---

## 7. 格式检查

### Markdown 格式

**脚本**: `scripts/check/md-format.py`

```bash
python3 scripts/check/md-format.py <module>/index.md
```

**检查规则**:
- R1 (must-fix): 方框字符、块填充问题
- R2 (should-fix): 中文混排对齐
- R3 (nice): 其他格式优化

### log.md 格式

**脚本**: `scripts/check/reformat-log.py`

```bash
# 检查格式问题
python3 scripts/check/reformat-log.py --verify <module>/log.md

# 预览修复结果
python3 scripts/check/reformat-log.py --dry-run <module>/log.md

# 应用修复
python3 scripts/check/reformat-log.py <module>/log.md
```

---

## 7. 验证覆盖率

```bash
# 最终验证
python3 scripts/check/analyze-index-coverage.py knowledge/<module>
```

**目标**: 覆盖率 100%，无效引用 0 个。

---

## 完整工作流示例

```bash
# 1. 分析覆盖率
python3 scripts/check/analyze-index-coverage.py knowledge/02_rd --generate-entries > knowledge/02_rd/_coverage_report.md

# 2. 查看报告
cat knowledge/02_rd/_coverage_report.md

# 3. 对缺失文件进行深度分析（并行 subagent 或手动）

# 4. 合并到 index.md（编辑文件）

# 5. 链接检查
python3 scripts/check/link-validator.py --file 02_rd/index.md --report

# 6. 格式检查
python3 scripts/check/md-format.py knowledge/02_rd/index.md
python3 scripts/check/reformat-log.py --verify knowledge/02_rd/log.md

# 7. 最终验证
python3 scripts/check/analyze-index-coverage.py knowledge/02_rd

# 8. 清理临时文件
rm knowledge/02_rd/_coverage_report.md
```

---

## 目录与文件位置合理性分析

在纳管文件时，同时分析文件位置的合理性：

1. **主题归属**: 文件内容是否与所在目录的主题一致
2. **层级深度**: 文件是否放在过深的层级（>3 层）
3. **目录平衡**: 子目录文件数是否过于不均
4. **命名规范**: 文件名是否遵循 kebab-case
5. **交叉引用**: 相关文件之间是否有链接

### 常见位置问题

| 问题 | 示例 | 建议 |
|:-----|:-----|:-----|
| 主题错位 | 存储分析文件放在 AI 目录 | 迁移到存储目录 |
| 杂物间化 | 06_others/ 包含各种不相关文件 | 按主题拆分 |
| 层级过深 | a/b/c/d/file.md | 提升到 a/b/file.md |
| 命名不规范 | MyFile.md, my_file.md | 改为 my-file.md |

---

## 脚本清单

| 脚本 | 用途 |
|:-----|:-----|
| `scripts/check/knowledge-normalizer.py` | **一站式入口** — 5 阶段规范化流水线 |
| `scripts/check/analyze-index-coverage.py` | index.md 覆盖率分析（全库/单模块 + 自动补全） |
| `scripts/check/extract-index-metadata.py` | 批量提取文件标题和摘要 |
| `scripts/check/link-validator.py` | 链接有效性检查 + 自动修复 |
| `scripts/check/link-augmenter.py` | 裸文件名引用 → 自动添加链接 |
| `scripts/check/md-format.py` | Markdown 格式规范检查 |
| `scripts/check/reformat-log.py` | log.md 格式化 + 校验（支持 --all） |
