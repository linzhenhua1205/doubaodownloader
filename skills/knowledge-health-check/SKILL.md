---
name: knowledge-health-check
description: |-
  Validate the integrity of the knowledge base (knowledge/) with a comprehensive health check script. Use when the user asks to check/fix/audit knowledge base health, verify link validity, fix log.md ordering, check file location reasonableness, validate markdown table formatting, or scan for format issues. Triggers: 检查知识库、完整性检测、链接检查、格式校验、log排序、知识库健康度、health check、audit knowledge.
metadata:
  requires:
    bins: ["python3"]
  emoji: 🩺
---

# Knowledge Base Health Check 🩺

> **注意**: 本 skill 的脚本已重构为 **两层检查体系**：
> - `kb-health.py` — 六维全景扫描（日志/链接/表格/位置/格式）
> - `link-validator.py` — 链接专项检查（带分类：DEPTH/MOVED/MISSING）
> - `link-fixer.py` — 智能修复引擎（按规则批量修复）

---

## 工具链概览

```
┌──────────────────────────────────────────────────────────────┐
│                    链接检查与修复工具链                          │
├──────────────────────────────────────────────────────────────┤
│  link-validator.py  ← 扫描 + 分类 + 建议 + 残缺检测            │
│        ↓                                                     │
│  link-fixer.py      ← 规则引擎 + 批量修复 + 降级 + stub       │
│        ↓                                                     │
│  link-fix-audit.py  ← 修复后审查验证（diff审计/残缺/降级核查） │
├──────────────────────────────────────────────────────────────┤
│  kb-health.py       ← 六维全景健康检查（含链接检查子集）        │
└──────────────────────────────────────────────────────────────┘
```

## 🔗 链接检查（推荐入口）

### 基础扫描

```bash
# 全量扫描整个 knowledge/
python3 scripts/check/link-validator.py

# 按模块扫描
python3 scripts/check/link-validator.py --module 02_rd/03_hardware

# 扫描单个文件（保留目录 index 或全局 index.md）
python3 scripts/check/link-validator.py --file 01_survey/switch/2026-08-19.md   # 示例：01_survey 已无 index.md（2026-08-19 起）
python3 scripts/check/link-validator.py --file index.md
```

### 带修复建议的报告

```bash
# 详细报告 + 建议
python3 scripts/check/link-validator.py --report --suggest
```

### 智能修复

```bash
# 预览自动修复结果
python3 scripts/check/link-fixer.py --module 02_rd/00_rd-management --dry-run

# 自动应用安全修复（DEPTH/MOVED/DIR_RENAME）
python3 scripts/check/link-fixer.py --module 02_rd/00_rd-management --auto

# 创建 stub 文件（为 MISSING 引用创建占位）
python3 scripts/check/link-fixer.py --module 02_rd/00_rd-management --stub --dry-run
```

### 输入格式

`link-validator.py` 支持多种路径格式：
- `--module 02_rd/03_hardware` — 按模块
- `--file index.md` — 全局文件索引（2026-08-03 起）
- `--file knowledge/01_survey/<module>/YYYY-MM-DD.md` — 01_survey 日期文件（index/log 已移除，2026-08-19 起）

### 链接分类说明

扫描结果将每个断裂链接归类为：

| 类型 | 标识 | 含义 | 自动修复 |
|:-----|:----:|:-----|:--------:|
| **DEPTH** | 🔄 | 相对路径深度错（多/少 `../`）| ✅ 安全 |
| **MOVED** | 📦 | 目标文件被移到知识库其他位置 | ✅ 安全 |
| **DIR_RENAME** | 📁 | 目录已改名（如 `03_hardware/` → `02_firmware/`）| ✅ 安全 |
| **EXTERNAL** | 📝 | 裸 `knowledge/xxx.md` 文本引用（应为链接）| ✅ 安全 |
| **MISSING** | ❌ | 文件在知识库中确实不存在 | ⚠️ 降级(需 `--downgrade`) |
| **TRUNCATED** | ✂️ | `.md)` 前无 `(` 的截断残留（正则误匹配产物）| ❌ 需手动 |

> ⚠️ **MOVED 判定是 basename 启发式（2026-08-06 实战教训）**：它按「文件目录相对」解析链接，而库内规范是「knowledge 根相对」（std-002），因此**所有根相对链接会被误报 MOVED**；且只要 basename 全库存在即报 MOVED——**已指向新路径的正确链接也会被误报**。批量迁移后的链接验证建议用「根相对+文件相对」双基准自定义校验，勿盲目对全部 MOVED 执行 `--auto`（可能"修复"已正确的链接）。

## 📋 全景健康检查

### Quick Start

```bash
# 全量检查
python3 scripts/check/kb-health.py

# 检查特定模块
python3 scripts/check/kb-health.py --path 03_AI

# 仅检查链接（B）+ 表格（C）
python3 scripts/check/kb-health.py --categories B,C

# 简略模式（每文件一行）
python3 scripts/check/kb-health.py --summary
```

### 全景检查维度

| 维度 | 代码 | 检查内容 |
|:-----|:----|:---------|
| **A. Log 排序** | `A1-A4` | log.md 时间正序（oldest first，2026-08-15 起）、条目格式、空节（全局 log.md 为 AI 尾部 append=正序；存量已由 `kb-log-reorder.py` 重排；保留目录维持各自机制） |
| **B. 链接** | `B1` | 本地 markdown 链接有效性 |
| **C. 表格** | `C1-C3` | 列数一致性、分隔符有效性 |
| **D. 文件位置** | `D1` | 文件名 vs 目录匹配 |
| **E. Markdown 格式** | `E1-E6` | Unicode 绘图符、中文混排、TOC/Changelog |
| **F. 关系完整性** | `F1` | index.md 关系记录校验（类型有效/目标存在） |
| **G. 策略合规** | `G1` | 文件策略匹配校验（A/B/C/D/E 各维度要求） |

### 输出格式

```bash
# 详细报告
python3 scripts/check/kb-health.py

# JSON 输出（供程序消费）
python3 scripts/check/kb-health.py --json

# 每文件一行摘要
python3 scripts/check/kb-health.py --summary
```

## 常用工作流

### 1. 写文档后的链接自检

```bash
python3 scripts/check/link-validator.py --file my-new-doc.md --suggest
```

### 2. 整模块链接修复

```bash
# 第一步：扫描报告
python3 scripts/check/link-validator.py --module 02_rd/03_hardware --report --suggest

# 第二步：自动修复安全项
python3 scripts/check/link-fixer.py --module 02_rd/03_hardware --auto

# 第三步：验证修复结果
python3 scripts/check/link-validator.py --module 02_rd/03_hardware
```

### 3. 创建缺失文件 stub

```bash
python3 scripts/check/link-fixer.py --module 02_rd/03_hardware --stub --dry-run
# 确认无误后:
python3 scripts/check/link-fixer.py --module 02_rd/03_hardware --stub
```

### 4. 知识库发布前一致性检查

```bash
python3 scripts/check/kb-health.py --categories A,B,C,E --summary
# 关注 A：log 排序；B：链接完整性；C：表格格式；E：MD 格式
```

### 5. 关系完整性与策略合规检查

```bash
# 全库关系完整性扫描
python3 scripts/check/relation-integrity.py --summary

# 特定模块的关系检查
python3 scripts/check/relation-integrity.py --module 02_rd

# 全库策略合规扫描
python3 scripts/check/strategy-compliance.py --all --summary

# 特定模块格式合规扫描
python3 scripts/check/format-validator.py --module 02_rd --summary
```

## 🔧 批量链接修复（2026-08-05 方法论固化）

> 全库 67,503 处链接问题的实战经验，按此顺序处理可安全批量修复。

### 问题分类与处理策略

| 问题类型 | 数量级 | 处理方式 | 安全性 |
|:---------|:------:|:---------|:------:|
| TOC 伪锚点 `[标题](标题)` | 62,599 | → `[标题](#slug)`（锚点规则见 optimize_md_files.py:34）| ✅ 批量 |
| MOVED 文件路径 | 2,503 | 全库同名查找 → 修正相对路径 | ✅ 自动 |
| 反斜杠路径 `..\dir\file.md` | 569 | → `../dir/file.md` | ✅ 自动 |
| 死链（目标不存在）| 727 | → 纯文本（保留链接文字）| ⚠️ 需 `--downgrade` |
| notes-summary 超长链接 | 13,640 | 降级为纯文本 | ⚠️ 需确认 |

### 批量修复命令

```bash
# ① 扫描 + 报告（先看清问题分布）
python3 scripts/check/link-validator.py --report --suggest

# ② 自动修复安全项（DEPTH/MOVED/DIR_RENAME/反斜杠）
python3 scripts/check/link-fixer.py --module 02_rd --auto

# ③ 死链降级（有损，需显式授权）+ 修复后审计（推荐一键闭环）
python3 scripts/check/link-fixer.py --module 02_rd --auto --downgrade --audit

# ④ 修复后验证（若未用 --audit）
python3 scripts/check/link-validator.py --module 02_rd
```

> **`--audit` 一键闭环（2026-08-05 集成）**：修复完成后自动调用
> `link-fix-audit.py --working --downgrade`，分析 git diff 验证"只改了链接"。
> 审计发现异常 → 返回码 2 并提示人工核查；通过 → 提示可安全提交。
> 修复已提交后复核：`link-fixer.py --audit --audit-commit <COMMIT>`。

### 防截断铁律（2026-08-05 BUG 教训）

**URL 可能内含括号**（如 `英伟达(NVIDIA)的收购历程.md`），正则 `[^)]+` 会在第一个 `)` 截断，
产生残缺残留（案例：`2026-06-23-product-design-guide.md:1214`）。

- ✅ `LINK_RE` 已升级：`((?:[^()]|\([^)]*\))+)` 支持一层嵌套括号
- ✅ `link-fixer.find_link_end()`：括号平衡定位链接结尾
- ✅ 所有写入带**长度验证**（新 < 原 50% 拒绝写入）

### TOC 伪锚点生成规则

锚点 slug = `re.sub(r'[^\w\u4e00-\u9fff\-]', '-', title).lower().strip('-')`
（与 optimize_md_files.py 一致，GitHub 风格：中文保留、空格/标点转 `-`、转小写）

## 📐 Markdown 内部格式 Lint（markdownlint 工具链，2026-08-05 建成）

> 治理文件**内部**格式（非跨文件链接）。用 GitHub 标准 markdownlint 规则库（MD001-MD063），
> 通过 Node API 直接调用实现"一次到位"。脚本：`scripts/check/markdown-lint-audit.mjs`
> （需 node + markdownlint-cli2；勿用 python 自写规则排查）。

```bash
# 扫描报告（默认只读）
node scripts/check/markdown-lint-audit.mjs

# 备份 + 迭代修复 + 三重验证
node scripts/check/markdown-lint-audit.mjs --fix

# 单目录
node scripts/check/markdown-lint-audit.mjs --dir knowledge/02_rd
```

### 关键坑（实战教训，必须遵守）

1. **markdownlint v0.41 的 `lint()` 不支持 fix 选项**（曾出现"修复"实际没生效）→
   修复必须用官方 `applyFixes(text, issues)` API，并**迭代多轮**到收敛（单轮无法全覆盖）
2. **markdownlint-cli2 的 glob/配置加载有怪癖**（`--config` 不生效、`--verbose` 被当 glob）→
   绕开 CLI，用 Node API 直接 `lint({ files, config })`
3. **MD051 对 TOC 锚点链接 100% 误报**（`[标题](#锚点)` 被当引用定义）→ 必须禁用
4. **MD023 有库 bug**（触发内部异常）→ 禁用；**MD060 中文 CJK 宽度误报** → 禁用
5. **>1 万行超大文件（raw 素材，如 notes-summary 71k 行）会卡死** → MAX_LINES 豁免
6. **MD040 残余 = 缩进/引用块内裸围栏**（`> ``` `、`  ``` `）→ 需增强正则，普通 lint 不覆盖
7. 禁用清单：MD013(行长) MD033(内联HTML) MD041(首行H1) MD023 MD051；
   不自动修（语义/锚点风险，需人工）：MD001(跳级) MD025(多H1) MD034(裸URL) MD036(强调当标题) MD055/056(表格)

### 修复纪律（防内容丢失）

- **备份前置**到 `tmp/bak/markdownlint-<日期>/`（曾出现备份发生在修复后的 bug）
- 修复后三重验证：非空白哈希对比 + 逐行对比 + `link-validator.py` 确认零链接破坏
- 每轮提交、可回滚；MD040 为内容级修改，单独验证（只允许 ` ``` ` → ` ```text `）

> 状态：2026-08-05 首轮全库 40,940 → 2,917 问题（1,272 文件，7 提交）；
> 残余需人工判断（MD036 1,705 / MD056 459 / MD055 290 / MD025 236 / MD001 18），备份在 `tmp/bak/markdownlint-2026-08-05/`。

## 🔍 修复后审查验证（link-fix-audit.py）

> 批量修复后必须验证"只改了链接、无内容误修改"。四种模式：

```bash
# ① diff 审计: 行数配对 + 链接剥离对比 + 死链降级自动识别
python3 scripts/check/link-fix-audit.py --diff e4e3105d7

# ①b working 审计: 修复后未提交改动即时验证（link-fixer --audit 内部调用）
python3 scripts/check/link-fix-audit.py --working --downgrade

# ② 全库残缺扫描: `.md)` 前无 `(` 的截断残留
python3 scripts/check/link-fix-audit.py --scan

# ③ 降级目标核查: 被降级链接是否真的不存在（防误降级）
python3 scripts/check/link-fix-audit.py --downgrade --diff e4e3105d7
```

输出示例（真实案例 e4e3105d7）：
```
knowledge/ 文档区: 删除 764 / 新增 764     ← 严格配对
   纯链接变化: 49 处
   死链降级(预期): 713 处
   嵌套链接降级(预期): 1 处
   真异常(需人工): 1 处                     ← TRUNCATED残缺, 需修复
```

**验证标准**：
- knowledge/ 文档区 -/+ 行数**严格配对**（链接修复是成对替换）；
  整文件新增/删除自动豁免（`new file mode` / `deleted file mode` 块不参与配对）
- 剥离 `[text](url)` 后剩余文本一致 → 只改了链接
- 死链降级特征 = 链接文字在 + 行保留（`[文字](死链)` → `文字`）
- 真异常 = 链接文字丢失 或 `.md)` 残缺残留 → 必须人工修复
- `--working` 使用 `git diff HEAD`（覆盖 staged + unstaged 改动）

## 向后兼容

以下根级别名仍然有效（软链接保持）：

| 根级命令 | 实际脚本 |
|:---------|:---------|
| `scripts/check_links.py` | → `check/link-validator.py` |
| `scripts/knowledge_health_check.py` | → `check/kb-health.py` |
| `scripts/reformat_log.py` | → `check/reformat-log.py`（增强版） |
| `scripts/fix_index_links.py` | → `check/fix-index-urlencode.py` |

## 设计说明

- **默认只读**: 所有脚本默认只扫描不写入
- **--dry-run** 预览模式: link-fixer 支持预览变更
- **因果分类**: link-validator 不仅报告断链，还分析原因（DEPTH/MOVED/MISSING/TRUNCATED）
- **写后验证**: link-fixer 所有写入校验长度 ≥50%（防正则误匹配截断）
- **有损操作显式化**: 死链降级需 `--downgrade` 显式授权（默认只修安全项）
- **规则驱动**: link-fixer 使用声明式 FIX_RULES 列表，新增规则即新增修复能力
- **跳过的目录**: `node_modules/`, `.git/`, `__pycache__/`, `bak/`, `site/`, `tmp/`, `.history/`
