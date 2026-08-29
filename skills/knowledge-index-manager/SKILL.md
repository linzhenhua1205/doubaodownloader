---
name: knowledge-index-manager
description: |-
  统一知识库索引/日志/目录管理。合并了原 index-log-maintainer / index-rebuilder / index-deep-analyzer 三个技能的全部功能，提供 4 种操作模式：
  - audit（审计检查）：index/log 合规、覆盖率、链接、格式
  - rebuild（重建）：全量重建 index.md
  - normalize（规范化）：一站式 6 阶段修复流水线
  - maintain（日常维护）：增量修复、文件迁移
  Triggers: index管理、index重建、日志格式化、索引修复、知识库规范化、文件迁移、目录优化、index覆盖率、log修复
metadata:
  replaces:
    - skills/index-log-maintainer/SKILL.md
    - skills/index-rebuilder/SKILL.md
    - skills/index-deep-analyzer/SKILL.md
  emoji: 📋
---

# Knowledge Index Manager 📋

> **统一的知识库索引管理技能** — 合并了原 index-log-maintainer / index-rebuilder / index-deep-analyzer 三个技能的全部功能，消除功能重叠，统一入口。
>
> ⚠️ **2026-08-03 V3 条目库变更**（替代原双轨制说明）：
> - **全局索引模块**（`02_rd`/`03_AI`/`04_person`/`05_tools`/`06_others`/`07_industry-research`）的分布式 index.md/log.md 已**废弃**（281 个备份于 `tmp/bak/kb-global-index-2026-08-03/`）。
> - **三文件职责（design-010 v1.3）**：`knowledge/README.md`=**人工条目库**（原名 index.md，2026-08-03 更名避免 Windows 大小写冲突；文件名+摘要·按日期追加·无路径）；`knowledge/index.md`=**全局文件索引（默认操作对象）**（`kb-global-index.py` 生成，含路径+摘要，摘要优先注入 README.md 人工摘要）；`knowledge/log.md`=全局变更日志（`kb-global-log.py` 合并）。
> - **单同步纪律（v1.3，2026-08-07 起，取代四同步）**：新增/修改文件后 → ① 把全面摘要（`- **类型：标题** | [knowledge/x.md](x.md) — 说明`）写到 `tmp/` 草稿，用 `python3 scripts/tools/kb-log-append.py --file <草稿>` 追加 `knowledge/log.md` 尾部；② **不更新** README.md/index.md（脚本批量处理）；③ `scripts/git/git-auto-commit.py` 自动提交（AI 身份 + `[AI]` 前缀；人工提交用 `--manual`）。
> - **通用收尾**：本技能所有产生文件变更的模式（audit 修复/rebuild 重建/normalize 修复/maintain 迁移/entry 追加）完成后，一律执行：
>   ```bash
>   python3 scripts/git/git-auto-commit.py -t knowledge -s <scope> \
>       -m "<变更摘要>" -n "<检查结果/修复统计>"
>   ```
> - 本技能的 audit/rebuild/normalize/maintain 各模式**作用于全库根文件**（2026-08-19 起无保留目录：01_survey/ 与 weekly-reports/ 均不再维护 index/log）。全局模块的文件索引维护请直接用工具脚本；**根 README.md 条目追加用本技能「模式 E: entry」或 `kb-index-extract.py`/`kb-index-check.py`**；**查找/加工文件默认基于 `index.md`**（`kb-index-extract.py` 默认源）。

---

## 操作模式总览

```text
┌──────────────────────────────────────────────────────────────────┐
│                     knowledge-index-manager                        │
│                                                                    │
│  audit ──▶ index/log 合规检查 · 覆盖率扫描 · 链接验证 · 格式检查    │
│  rebuild ▶ 全量重建 index.md（8 步流程：扫描→提取→校验→写入→验证）  │
│  normalize ▶ 一站式 6 阶段修复（index+log+links+augment+format+scope）│
│  maintain ▶ 增量修复 · 文件迁移 · 裸引用增强 · 定向修复              │
│  entry ──▶ 根 README.md 条目追加（V3 条目库：文件名+摘要·按日期分节）  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 第 1 步：选择操作模式

### 模式 A: audit（审计检查 — 只读，安全）

检查当前知识库目录的 index.md / log.md 健康状况。

**涵盖子项**:

| 检查项 | 脚本 | 说明 |
|:-------|:-----|:-----|
| 🅰️ index/log 合规 | `index-log-normalizer.py --check` | 每目录 index.md/log.md 作用域与格式合规 |
| 🅱️ 覆盖率 | `analyze-index-coverage.py` | index.md 是否涵盖所有文件 |
| 🅲 链接有效性 | `link-validator.py` | 5 类链接失效检测 |
| 🅳 格式规范 | `md-format.py --level R1` | Markdown 格式（方框/对齐） |
| 🅴 log 格式 | `reformat-log.py --verify` | log.md 正序/格式统一 |
| 🅵 文件位置 | 手动 + `directory-architect.py` | 文件归属目录合理性 |

```bash
# 全库审计（推荐入口）
python3 scripts/check/knowledge-normalizer.py          # dry-run 模式，预览所有问题

# 单独检查 index/log 合规
python3 scripts/check/index-log-normalizer.py knowledge/02_rd --check

# 全库检查
python3 scripts/check/index-log-normalizer.py knowledge/ --all --check

# 覆盖率检查
python3 scripts/check/analyze-index-coverage.py knowledge/02_rd

# 链接检查
python3 scripts/check/link-validator.py --module 02_rd

# 格式检查
python3 scripts/check/md-format.py knowledge/02_rd -r --level R1

# log 格式检查
python3 scripts/check/reformat-log.py --verify knowledge/02_rd/log.md

# 目录架构分析
python3 scripts/check/directory-architect.py knowledge/02_rd/03_hardware --analyze-only
```

### 模式 B: rebuild（全量重建 index.md）

当目录结构发生重大变更（新增/删除大量文件、目录重组）时，从头重建 index.md。

**8 步工作流**:

```text
① 扫描清单 → ② 提取内容 → ③ 校验匹配 → ④ 判断位置 → ⑤ 迁移修复 → ⑥ 写入索引 → ⑦ 验证链接 → ⑧ 记录日志
```

**步骤详解**:

#### ① 扫描文件清单

```bash
cd knowledge/<target-dir> && find . -name "*.md" -type f | sort
```

对比当前 index.md 找出**缺失/多余**的文件：

```bash
grep -oP '\(\K[^)]+\.md(?=\))' index.md | sort -u > /tmp/index_links.txt
find . -name "*.md" -type f | sed 's|^\./||' | sort > /tmp/all_files.txt
diff /tmp/index_links.txt /tmp/all_files.txt
```

#### ② 提取文件头部摘要

```bash
for f in <目录>/*.md; do echo "--- $(basename $f) ---"; head -3 "$f"; echo ""; done
```

#### ③ 文件名-内容匹配校验

| 检查项 | 方法 | 不合格标准 |
|:-------|:-----|:----------|
| 文件名反映内容 | 文件名 vs 第一行标题 | 标题主题与文件名完全无关 |
| 内容一致 | 读取前 10 行关键词 | 核心关键词与所在目录主题不符 |

#### ④ 位置合理性判断

依据内容关键词判断文件归属（详见下方 §4 位置合理性判断）。

如果判断需要迁移，先做**引用影响分析**：

```bash
grep -rl "被迁移文件名" . --include="*.md"
```

#### ⑤ 文件迁移与交叉引用修复

```bash
# 移动文件
mv <旧路径/文件.md> <新目录/>

# 修复交叉引用（使用专用工具）
python3 scripts/check/link-fixer.py --dry-run    # 预览修复
python3 scripts/check/link-fixer.py --auto       # 自动修复
```

#### ⑥ 写入 index.md

index.md 格式规范：

```
# 目录标题

> 文件统计信息

## 目录结构概览

| # | 子目录 | 文件数 | 说明 |

## 子目录名

| 文件 | 一句话概述 |
|:-----|:----------|
| [`文件名`](路径/文件名.md) | 一句话概述 |
```

覆盖原则：**目标目录下所有 `.md` 文件必须在 index 中有对应条目**。

#### ⑦ 验证链接

```bash
python3 scripts/check/link-validator.py --file <target>/index.md
```

#### ⑧ 记录日志

在 `knowledge/<target>/log.md` 追加：

```
- **index重建** 📋 `<target>/index.md` **vX版本**：覆盖文件数变更详情
- **文件迁移** 📦 迁移明细（哪几个文件从哪移到哪）
- **交叉引用修复** 🔧 修复详情
```

### 模式 C: normalize（规范化 — 一站式修复）

全自动 6 阶段修复流水线，安全默认为 dry-run。

```bash
# 预览所有问题（不修改）
python3 scripts/check/knowledge-normalizer.py

# 全库应用修复
python3 scripts/check/knowledge-normalizer.py --fix

# 仅处理某个模块
python3 scripts/check/knowledge-normalizer.py --module 02_rd --fix

# 仅特定阶段
python3 scripts/check/knowledge-normalizer.py --only links,augment --fix

# 跳过某些阶段
python3 scripts/check/knowledge-normalizer.py --skip format
```

**6 阶段流水线**（执行顺序）：

| # | 阶段 | 脚本 | 说明 |
|:-:|:-----|:-----|:-----|
| 1 | `index` | `analyze-index-coverage.py` | index.md 覆盖率补全 |
| 2 | `log` | `reformat-log.py` | log.md 格式重排 + 日期排序 |
| 3 | `links` | `link-validator.py` | 链接有效性检查 + 修复 |
| 4 | `augment` | `link-augmenter.py` | 裸文件名引用 → 自动链接 |
| 5 | `format` | `md-format.py` | Markdown 格式规范检查 |
| 6 | `scope` | `index-log-normalizer.py` | 每目录作用域与格式合规 |

### 模式 D: maintain（日常维护 — 增量修复）

不需要全量重建时，执行定向修复。

```bash
# 链接修复（最常用）
python3 scripts/check/link-fixer.py --auto              # 自动修复断裂链接
python3 scripts/check/link-augmenter.py --fix            # 裸文件引用链接化
python3 scripts/check/link-validator.py --module 02_rd --fix --dry-run

# log 格式修复
python3 scripts/check/reformat-log.py knowledge/02_rd/log.md --dry-run
python3 scripts/check/reformat-log.py knowledge/02_rd/log.md

# index 覆盖率修复
python3 scripts/check/analyze-index-coverage.py knowledge/02_rd --fix

# index/log 合规修复（有备份）
python3 scripts/check/index-log-normalizer.py knowledge/02_rd --dry-run
python3 scripts/check/index-log-normalizer.py knowledge/02_rd --fix

# 子目录导航修复
python3 scripts/check/subdir-nav-fixer.py knowledge/02_rd --dry-run
python3 scripts/check/subdir-nav-fixer.py knowledge/02_rd --fix --recursive

# 文件迁移（使用 mv-knowledge CLI）
python3 scripts/tools/mv-knowledge.py <源路径> <目标目录>
```

> ⚠️ 上述示例路径 `knowledge/02_rd` 等为**保留目录/旧示例**；全局模块（6 主题模块）已无分布式 index/log，相关修复命令对其不适用（正常应被跳过）。

---

### 模式 E: entry（根 log.md 追加 — 单同步入口）

> **v1.3（2026-08-07）**：原「README.md 条目追加」改为「log.md 尾部追加」。README.md/index.md **不再由 AI 直接更新**（脚本批量处理）；新增/重要文件后用 `kb-log-append.py` 追加 log.md：

```bash
# ① 摘要写到草稿（含标题+路径链接+说明）
cat > tmp/kb-log-draft-<date>.md <<'EOF'
- **📄 文档：标题** | [knowledge/<模块>/<文件>.md](<模块>/<文件>.md) — 说明
EOF

# ② 脚本追加（自动备份+查重+预览）
python3 scripts/tools/kb-log-append.py --file tmp/kb-log-draft-<date>.md --section <模块>

# ③ 2026-08-19 起无保留目录：全库统一根 index.md/log.md（weekly-reports 分布式机制已移除）
python3 scripts/tools/kb-index-extract.py --source readme --with-path   # 仅供查看既有条目
python3 scripts/check/kb-index-check.py                                  # 批量健康检查（脚本模式）
```
#    格式: - [⭐] `文件名.md` | 摘要（≤120字符，无路径）
#    高价值加 ⭐；新增日期分节追加在末尾（oldest first 正序，2026-08-15 起）

# ④ 单同步收尾（v1.3）
# 用 kb-log-append.py 在 knowledge/log.md 尾部追加变更条目（含路径链接）；index/README 不更新（脚本批量）

# ⑤ 复核
python3 scripts/check/kb-index-check.py           # 应 PASS
python3 scripts/tools/kb-index-extract.py --with-path --since $(date +%F)  # 确认条目可提取

# ⑥ git 自动提交（区分 AI/人工，规范 message）
python3 scripts/git/git-auto-commit.py -t knowledge -s meta -m "条目库/索引同步: <摘要>" -n "kb-index-check 应 PASS"
```

**条目追加检查清单**：文件名拼写与真实文件一致？摘要 ≤120 字符且非纯文件名？日期分节在正确位置（oldest first 正序）？高价值是否加 ⭐？index.md 是否已刷新（C6）？

### 模式 F: 文件名规范（YYYY-MM-DD-英文描述.md — design-003 命名规范）

> 全局模块（`02_rd`/`03_AI`/`04_person`/`05_tools`/`06_others`/`07_industry-research`）所有活跃 .md 文件名必须符合 **`YYYY-MM-DD-英文描述.md`**（如 `2026-07-03-knowledge-scale-law.md`）。
> 排除：`01_survey/`、`weekly-reports/`（2026-08-19 起均无 index/log，仅产出文件）、`index.md`/`log.md`/`README.md`/`index.md`（管理文件）、`oldbak/`、`*-bak/`（废弃归档区）。

**规范要点**：
- 日期 = 内容创建/归档日（优先级：头部元信息 → 正文头部独立日期行 → **git 最早提交时间** → mtime 兜底）
- 描述 = 英文小写，单词用 `-` 连接；中文文件名需翻译为英文 slug
- 重复内容文件加 `-dupN` 后缀消歧（保留最早日期原件）

```bash
# ① 检查 (C8: 文件名规范)
python3 scripts/check/kb-index-check.py

# ② 批量规范化 (dry-run 审查映射表 → apply 执行 git mv + 全库引用更新)
python3 scripts/tools/kb-rename-normalize.py --dry-run
python3 scripts/tools/kb-rename-normalize.py --apply

# ③ 单同步收尾（v1.3）
# 用 kb-log-append.py 在 knowledge/log.md 尾部追加更名记录；index/README 不更新（脚本批量）

# ④ 复核
python3 scripts/check/kb-index-check.py           # 应 PASS (C8 全过)
```

**单文件手动改名纪律**：`git mv` 改名 → 全库搜索旧名引用并替换（`grep -rn 旧文件名 knowledge/` 排除 log.old.md 历史归档）→ 运行 kb-global-index.py 刷新根 index.md → 根 log.md 追加记录。**禁止**直接 `mv`（丢失 git 历史）。

---

## 第 2 步：脚本清单（统一引用）

| 脚本 | 用途 | 模式 |
|:-----|:------|:----:|
| `scripts/tools/kb-global-index.py` | 🆕 **全局索引生成器** — 扫描 6 个全局模块生成 knowledge/index.md | 全局模块维护 |
| `scripts/tools/kb-global-log.py` | 🆕 **全局日志合并器** — 合并分布式 log.md（`--backfill` 含 5 月起 git 补齐）到 knowledge/log.md | 全局模块维护 |
| `scripts/check/knowledge-normalizer.py` | **统一入口** — 6 阶段规范化流水线（仅保留目录） | audit, normalize |
| `scripts/check/index-log-normalizer.py` | index/log 每目录作用域+格式合规（自动跳过全局模块） | audit, maintain |
| `scripts/check/analyze-index-coverage.py` | index.md 覆盖率分析+自动补全 | audit, rebuild, maintain |
| `scripts/check/extract-index-metadata.py` | 批量提取文件标题和摘要 | rebuild |
| `scripts/check/link-validator.py` | 链接有效性扫描（5 分类） | audit, maintain |
| `scripts/check/link-fixer.py` | 智能链接修复 | maintain, 迁移后 |
| `scripts/check/link-augmenter.py` | 裸文件名引用→自动链接 | maintain |
| `scripts/check/md-format.py` | Markdown 格式规范检查 | audit, normalize |
| `scripts/check/reformat-log.py` | log.md 格式重排+日期排序 | audit, maintain, normalize |
| `scripts/check/directory-architect.py` | 目录架构分析+MECE 分层 | audit, rebuild |
| `scripts/check/subdir-nav-fixer.py` | 子目录导航一致性修复 | maintain |
| `scripts/check/content-format-normalizer.py` | 五大要素合规（概要/关键词/TOC/参考/Changelog） | audit, maintain |
| `scripts/tools/mv-knowledge.py` | **文件迁移 CLI** — 移动+索引+日志+链接修复一站完成 | maintain |
| `scripts/tools/kb-rename-normalize.py` | 🆕 **文件名规范化** — 批量 git mv 为 YYYY-MM-DD-英文描述.md（git 溯源日期+引用更新） | audit, normalize, maintain |

---

## 第 3 步：深度分析（进阶用法）

当需要对新模块做完整的深度分析时，使用此流程：

```bash
# 1. 覆盖率分析
python3 scripts/check/analyze-index-coverage.py knowledge/<module> --generate-entries

# 2. 对缺失文件进行分析（手动读取前 30 行，生成摘要）

# 3. 合并到 index.md

# 4. 链接检查
python3 scripts/check/link-validator.py --file <module>/index.md --report

# 5. 格式检查
python3 scripts/check/md-format.py knowledge/<module>/index.md
python3 scripts/check/reformat-log.py --verify knowledge/<module>/log.md

# 6. 最终验证覆盖率
python3 scripts/check/analyze-index-coverage.py knowledge/<module>
```

---

## 第 4 步：位置合理性判断

文件是否放在正确的目录？依据内容关键词判断：

| 目录 | 应含关键词 | 不应含关键词 |
|:-----|:----------|:------------|
| `01_survey/` | 调研·追踪·行业·市场·趋势 | 深度技术·设计·代码 |
| `07_industry-research/` | 深度·专题·分析·原理·技术 | 追踪·日报·周报 |

> ⚠️ **`01_survey/` 是调研时间序保留目录**（2026-08-19 起不再维护分布式 index/log，仅按日期文件组织）：**禁止把主题/深度文件迁入 `01_survey/`**（2026-08-06 实战教训：v1 移动建议 78 条「目标=01_survey/*」被用户判定完全不合理——会破坏时间序组织与全局索引机制，且与 `07_industry-research/` 重复分析）。主题文件归位目标只能是 `07_industry-research/` 等全局模块。
>
> ⚠️ 迁移建议/报告中的目标路径**常省略模块前缀**（如 `01_product/01_software` 实为 `02_rd/01_product/01_software`）：执行迁移前必须补全前缀并预检（源存在+目标目录存在+无同名冲突），防止文件丢失。
| `concepts/` | 方法论·概念·定义·框架·思维 | 硬件设计·BMC·代码 |
| `methodology/` | MECE·第一性原理·SSOT·框架 | 产品·硬件·软件实现 |
| 硬件子目录 | 架构·拓扑·RAS·散热·供电·SI | 管理·方法论(纯概念) |
| 固件子目录 | BMC·BIOS·OpenBMC·Redfish·固件 | 散热·信号·项目 |

### 常见位置问题

| 问题 | 示例 | 建议 |
|:-----|:-----|:-----|
| 主题错位 | 存储分析文件放在 AI 目录 | 迁移到存储目录 |
| 杂物间化 | `06_others/` 包含各种不相关文件 | 按主题拆分 |
| 层级过深 | a/b/c/d/file.md | 提升到 a/b/file.md |
| 命名不规范 | MyFile.md, my_file.md | 改为 my-file.md |

### 迁移后必做

使用 `scripts/tools/mv-knowledge.py` 自动完成以下步骤，手动迁移则逐一操作：

1. `mv <src> <dst>`
2. 更新源目录 `index.md`（删除条目）
3. 更新源目录 `log.md`（添加迁移记录）
4. 更新目标目录 `index.md`（添加条目）
5. 更新目标目录 `log.md`（添加迁移记录）
6. 若跨 knowledge/ 模块，更新 `knowledge/README.md` 导航/条目库（统计信息在 index.md 由脚本维护）
7. `python3 scripts/check/link-fixer.py --auto` — 自动修复交叉引用
8. 记录迁移到 `knowledge/MIGRATIONS.md`

> ⚠️ **迁移/去重到 `tmp/bak` 后必查引用重定向**（2026-08-06 去重实战教训：36 个副本移入 bak 后，16 类被移除副本仍被 48 个活动文档以 markdown 链接引用，直接移除即产生死链）：
> - 迁移前先 `grep -rl "被移文件名" knowledge/ --include="*.md"`（排除 index.md/log.md/历史快照）判断是否被引用；被引用则把链接**重定向到保留位置**（去重场景）或新位置（迁移场景），不能只移文件。
> - **重定向映射必须从 REMOVE/KEEP 一一对应关系自动生成**（如从预检脚本的 REMOVE/KEEP 数组导出），勿手工编写映射——手工方向极易写反（本次曾把指向保留位的正确链接误改到移除位，需撤销重做）。
> - 修复后验证须用**归一化路径精确匹配**（链接解析后 ∈ 被移除集合才算真死链），勿用 basename 匹配（会把指向保留位的合法链接误报为残留）。

---

## 模式选择决策树

```text
用户需求
├── "检查 index/log" → audit
│   ├── 检查合规 → index-log-normalizer.py --check
│   ├── 检查覆盖率 → analyze-index-coverage.py
│   └── 检查链接 → link-validator.py
├── "目录结构大变" → rebuild
│   ├── 扫描→提取→校验→写入→验证→记录（全量 8 步）
│   └── 配套: directory-architect.py (位置分析)
├── "修复全部问题" → normalize
│   └── knowledge-normalizer.py --fix (6 阶段一键)
└── "修单个问题" → maintain
    ├── 链接断裂 → link-fixer.py --auto
    ├── 裸引用 → link-augmenter.py --fix
    ├── log 乱 → reformat-log.py
    ├── index 缺文件 → analyze-index-coverage.py --fix
    └── 文件位置不对 → mv-knowledge.py <src> <dst>
```

---

## 安全约束

- **dry-run before fix**: `knowledge-normalizer.py` 默认 dry-run；`index-log-normalizer.py` 先 `--dry-run` 再 `--fix`
- **自动备份**: `index-log-normalizer.py --fix` 自动备份到 `tmp/bak/index-log-fix-<date>/`
  <!-- bak/引用规则 — 备份目标路径，非引用 bak 内容 -->
- **幂等**: 运行两次 `--fix` 第二次无变更
- **排除目录**: `bak/`, `oldbak/`, `import-modules/` 等始终跳过
- **保留信息**: 旧 index.md 中的 log 信息合并到 log.md，不丢弃

---

## 文本编辑操作

当需要直接编辑 index.md/log.md 时，遵循以下规则：

### index.md 格式

```markdown
# 🔬 模块名 `XX_module/`

> 📅 **文件统计**: 共 **N 个文件**（M 个子目录）
> **规则说明**:
> - 本文件仅维护文件清单，不记录修订历史
> - 修订记录请见 [`log.md`](log.md)

---

## 目录结构概览

| # | 子目录 | 文件数 | 说明 |
|:-:|:-------|:-----:|:-----|

---

## 子目录名

| 文件 | 一句话概述 |
|:-----|:----------|
| [`file.md`](子目录/file.md) | 摘要内容 |
```

### log.md 格式

```
## YYYY-MM-DD

- **操作** | `file` — 说明
```

- 时间正序（最早在前，oldest first，2026-08-15 起）
- 纯文本，无表格，无 emoji
- 仅记录本目录的变更

---

## Changelog

- **2026-08-06**: 三同步升级为**四同步**（+git 自动提交）；新增「通用收尾」规范（所有变更模式完成后调用 `git-auto-commit.py`，AI 身份 + `[AI]` 前缀，人工用 `--manual`）；模式 E 收尾加 ⑥ 自动提交步骤。
- **2026-08-03**: v1.1 新增「模式 F: 文件名规范」（YYYY-MM-DD-英文描述.md，配套 kb-rename-normalize.py + C8 检查）；脚本清单补充规范化工具。
- **2026-07-27**: v1.0 初始版本。合并原 index-log-maintainer / index-rebuilder / index-deep-analyzer 的全部功能，统一为 4 模式管理体系（audit/rebuild/normalize/maintain），消除功能重叠。
