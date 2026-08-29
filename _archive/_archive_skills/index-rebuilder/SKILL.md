---
name: index-rebuilder
description: |-
  ⚠️ 已废弃 — 请使用 skills/knowledge-index-manager/SKILL.md（统一索引管理技能）
  原功能（index.md 重建 8 步工作流）已合并至 knowledge-index-manager 的 rebuild 模式。
  保留本文件仅用于向后兼容，新操作请使用新技能。
---

# Index Rebuilder

重建 knowledge/ 下某目录（如 `02_rd/`）的 index.md 文件，确保所有文件被覆盖、链接有效、文件位置合理。

## 流程总览

```
① 扫描清单 → ② 提取内容 → ③ 校验匹配 → ④ 判断位置 → ⑤ 迁移修复 → ⑥ 写入索引 → ⑦ 验证链接 → ⑧ 记录日志
```

---

## ① 扫描文件清单

列出目标目录下所有 `.md` 文件，包括子目录：

```bash
cd knowledge/<target-dir> && find . -name "*.md" -type f | sort
```

同时读取当前 `index.md` 中已有的链接清单：

```bash
grep -oP '\(\K[^)]+\.md(?=\))' index.md | sort -u
```

对比找出**索引中缺失的文件**：

```bash
while IFS= read -r f; do clean="${f#./}"; if ! grep -q "$clean" /tmp/index_links.txt; then echo "  NOT FOUND: $clean"; fi; done < /tmp/all_files.txt
```

---

## ② 提取文件头部摘要

批量为每个目录读前 3 行，提取标题和概述：

```bash
for f in <目录>/*.md; do echo "--- $(basename $f) ---"; head -3 "$f"; echo ""; done
```

关键提取内容：
- 第 1 行 `# 标题` — 作为文件名匹配依据
- 第 2-3 行 `> 概述` 或 `> **来源**` — 作为一句话概述依据
- 无标题则用文件名中关键词推断

---

## ③ 文件名-内容匹配校验

校验规则：

| 检查项 | 方法 | 不合格标准 |
|:-------|:-----|:----------|
| 文件名反映内容 | 文件名 vs 第一行标题 | 标题主题与文件名完全无关 |
| 内容一致 | 读取前 10 行关键词 | 核心关键词与所在目录主题不符 |

```bash
for f in <目录>/*.md; do
  head -1 "$f" | grep -qi "文件名关键词" || echo "⚠️ 文件名-标题不匹配: $f"
done
```

---

## ④ 位置合理性判断

依据内容关键词判断文件归属：

| 目录 | 应含关键词 | 不应含关键词 |
|:-----|:----------|:------------|
| `01_basic-concepts/` | 方法论·概念·定义·框架·思维 | IPD·硬件设计·BMC |
| `02_rd-management/` | IPD·管理·流程·组织·采购·项目·SR | BMC·散热·信号·拓扑·DRAM |
| `03_hardware/01_hw_core/` | 架构·拓扑·RAS·散热·供电·SI·存储·国产化 | 管理·方法论(纯概念) |
| `03_hardware/02_firmware/` | BMC·BIOS·OpenBMC·Redfish·固件 | 散热·信号·项目 |
| `05_software/operations/` | 运维·诊断·故障·管理·监控·模块 | 架构·散热·设计 |
| `06_O&M/` | 报告·分析·O&M文档·调研 | (按子目录归入对应领域) |

如果判断需要迁移，先进行**引用影响分析**：

```bash
grep -rl "被迁移文件名" . --include="*.md"
```

---

## ⑤ 文件迁移与交叉引用修复

**移动文件**：

```bash
mv <旧路径/文件.md> <新目录/>
```

**修复引用**（从引用方文件的旧相对路径→新相对路径）：

```bash
# 示例：从 03_hardware/01_hw_core/ 移到 02_rd-management/
# 引用方 server_design_roadmap.md: ../03_hardware/01_hw_core/X.md → X.md (同目录)
# 引用方 03_hardware/README.md: X.md → ../02_rd-management/X.md
```

核心原则：修复所有引用该文件的跨文件链接。

---

## ⑥ 写入索引文件

index.md 格式规范：

```markdown
# 目录标题

> 文件统计信息

## 目录结构概览

| # | 子目录 | 文件数 | 说明 |

## 子目录名

N 个文件，简要说明。

### 分组名（可选）

| 文件 | 一句话概述 |
|:-----|:----------|
| [`文件名`](路径/文件名.md) | 一句话概述 |
```

每行的"一句话概述"从文件头部 `# 标题` + `> 描述` 综合提炼，≤ 25 字为宜。

覆盖原则：**目标目录下所有 `.md` 文件必须在 index 中有对应条目**。

---

## ⑦ 验证链接

```python
from pathlib import Path
from check_links import scan_file

v, b, s = scan_file(BASE / '<target>/index.md')
assert len(b) == 0, f"Broken links: {b}"
```

---

## ⑧ 记录日志

在 `knowledge/<target>/log.md` 追加：

```
- **index重建** 📋 `<target>/index.md` **vX版本**：覆盖文件数变更详情
- **文件迁移** 📦 迁移明细（哪几个文件从哪移到哪）
- **交叉引用修复** 🔧 修复详情
```
