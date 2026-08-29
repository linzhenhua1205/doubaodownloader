---
name: log-reformatter
description: |-
  Reformat knowledge base log.md files into a consistent changelog format. Use when log.md files have mixed formats (blockquotes, tables, plain bullets, duplicate date headers, out-of-order entries), need standardization, or when verifying format compliance. Triggers: 格式化log、log排序、log重整、changelog格式、log.md修复、reformat log、log格式校验.
metadata:
  requires:
    bins: ["python3"]
  emoji: 🔧
---

# Log.md Reformatter 🔧

> 标准化知识库 `log.md` 文件为统一的 changelog 格式。
>
> ⚠️ **2026-08-03 双轨制**：`02_rd`/`03_AI`/`04_person`/`05_tools`/`06_others`/`07_industry-research` 的分布式 log.md 已废弃，统一为 `knowledge/log.md` 全局日志（用 `scripts/tools/kb-global-log.py` 合并）。**2026-08-19 起无保留目录**：01_survey/ 与 weekly-reports/ 的分布式 log.md 均已移除（历史归档 knowledge/log.old.md），本技能仅处理全局 `knowledge/log.md`。

---

## 格式规范

按工作空间 `RULE.md` 要求，`log.md` 应遵循（全局 log.md 与保留目录 log.md 通用）：

```
# 📝 模块修订记录 `XX/log.md`

> **规则说明**:
> - 记录模块下文档的**新增、更新、修正、重构**
> - 格式：changelog 格式，按时间正序（oldest first，2026-08-15 起），条目化
> - 每条条目格式：`- **操作** 📍 [路径](相对路径) — 说明`
> - **路径必须为 markdown 链接**（2026-08-07 起）：显示文本保留完整路径（如 `knowledge/03_AI/xxx.md`），链接目标为**相对 log.md 所在目录**的路径（如 `03_AI/xxx.md`），点击可跳转定位文件
> - 跨域操作请在根级 `log.md` 中记录
>
> ⚠️ **v1.6（2026-08-15 起）**：全局 `knowledge/log.md` 由 AI 用 `kb-log-append.py` **尾部追加**（append-only，AI 禁止直接编辑）。**日期统一正序（oldest first）**——尾部追加即正序，无需重排；存量已由 `kb-log-reorder.py` 一次性重排。2026-08-19 起无保留目录：01_survey/ 与 weekly-reports/ 均不再维护 log.md（历史统一归档 knowledge/log.old.md）。

---

## 2026-07-14

- **新增** 🆕 [knowledge/03_AI/xxx.md](03_AI/xxx.md) — 说明文字
- **更新** 🔄 [knowledge/02_rd/yyy.md](02_rd/yyy.md) — 说明文字

## 2026-07-13

- **移动** 📍 [knowledge/05_tools/zzz.md](05_tools/zzz.md) — → 新位置/说明
```

> ⚠️ **链接相对基准**：`knowledge/log.md` 中链接目标 = 去掉 `knowledge/` 前缀后的路径（log.md 位于 `knowledge/` 目录内，相对链接以其所在目录为基准）。（2026-08-19 起无保留目录 log.md；知识库内所有日志统一在根 knowledge/log.md 与归档 knowledge/log.old.md。）

### 规则要点

| 规则 | 要求 | 常见违规 |
|:-----|:-----|:---------|
| 日期标题 | `## YYYY-MM-DD`（无后缀） | `## 2026-07-01 — 深度增强` |
| 日期顺序 | 正序（最早在上） | 06-29 出现在 07-07 之后 |
| 条目格式 | `- **操作** emoji [路径](相对路径) — 说明` | `> 🆕 路径 — 说明`（blockquote） |
| 路径链接 | 路径须为 markdown 链接（显示完整路径、链接相对 log.md 目录） | 裸 `\`路径\`` 反引号 |
| 重复日期 | 合并为一个节 | 多个 `## 2026-06-29` |
| 子级标题 | 用 `##` 不用 `###` | `### 2026-07-09` |
| 表格行 | 转为标准条目 | `\| time \| path \| op \| desc \|` |
| 日期范围 | `## YYYY-MM-DD ~ YYYY-MM-DD` 置于末尾 | — |

---

## 使用方法

### 基本用法

```bash
# 格式化单个 log.md
python3 scripts/check/reformat-log.py knowledge/02_rd/log.md

# 格式化所有 knowledge/*/log.md
python3 scripts/check/reformat-log.py --all
```

### 预览与校验

```bash
# 预览结果（不写入文件）
python3 scripts/check/reformat-log.py --dry-run knowledge/02_rd/log.md

# 仅检查格式问题（不修改）
python3 scripts/check/reformat-log.py --verify knowledge/02_rd/log.md
```

### 根级别名

```bash
# 向后兼容的别名（指向同一脚本）
python3 scripts/reformat_log.py knowledge/02_rd/log.md
```

---

## 处理能力

脚本自动处理以下格式问题：

### 1. Blockquote 条目 → 标准条目

**输入**:
```
> 🆕 `path/to/file.md` — 说明文字
```

**输出**:
```
- **新增** 🆕 [knowledge/path/to/file.md](path/to/file.md) — 说明文字
```

### 2. 表格行 → 标准条目

**输入**:
```
| 07:40 | path/to/file.md | move | → 新位置 |
```

**输出**:
```
- **移动** 📍 [knowledge/path/to/file.md](path/to/file.md) — → 新位置 (@07:40)
```

> **注意**: 数据对比表（如 `| 升级维度 | 升级前 | 升级后 |`）会被保留为内容块，不会被错误转换。

### 3. 带日期的纯列表 → 标准条目

**输入**:
```
- 2026-07-02: 新增专利交底书 #1 — BMC嵌入式智能问答
```

**输出** (归入 `## 2026-07-02` 节):
```
- **新增** 📝 新增专利交底书 #1 — BMC嵌入式智能问答
```

### 4. 重复日期节合并

多个 `## 2026-06-29 — suffix` 节合并为一个 `## 2026-06-29` 节，条目按原顺序保留。

### 5. 日期顺序排序

所有日期节按正序排列（最早在上，oldest first）。日期范围节置于末尾。

### 6. 无日期条目归类

无法从内容中推断日期的条目归入 `## 未知日期` 节，置于日期范围节之前。

---

## 操作类型映射

| 英文操作 | 中文操作 | Emoji |
|:---------|:---------|:------|
| add / create | 新增 / 创建 | 🆕 |
| update | 更新 | 🔄 |
| move | 移动 | 📍 |
| rename | 重命名 | 📍 |
| merge | 合并 | 🔀 |
| delete | 删除 | 🗑️ |
| archive | 归档 | 📦 |

---

## 常用工作流

### 1. 修复格式混乱的 log.md

```bash
# 第一步：检查问题
python3 scripts/check/reformat-log.py --verify knowledge/02_rd/log.md

# 第二步：预览修复结果
python3 scripts/check/reformat-log.py --dry-run knowledge/02_rd/log.md

# 第三步：应用修复
python3 scripts/check/reformat-log.py knowledge/02_rd/log.md

# 第四步：验证修复
python3 scripts/check/reformat-log.py --verify knowledge/02_rd/log.md
```

### 2. 批量格式化所有模块

```bash
# 预览所有 log.md 的格式问题
for f in knowledge/*/log.md; do
    python3 scripts/check/reformat-log.py --verify "$f"
done

# 批量格式化
python3 scripts/check/reformat-log.py --all
```

### 3. 写入新条目后的快速校验

```bash
# 编辑 log.md 后快速检查
python3 scripts/check/reformat-log.py --verify knowledge/02_rd/log.md
```

---

## 设计说明

- **幂等操作**: 对已格式化的文件再次运行不会产生变化
- **内容保全**: 不删除任何条目内容，仅重新排列和格式化
- **日期推断**: 从文件名路径中的日期（如 `2026-07-14-xxx.md`）自动推断条目日期
- **数据表检测**: 自动区分日志表格（date/path/op/desc）和数据对比表（label/value1/value2）
- **Windows 兼容**: 自动处理 GBK 控制台编码，支持 emoji 输出
- **跳过的目录**: `bak/`, `import-modules/`, `node_modules/`, `.git/`
