# 🧰 知识库质量问题诊断与开源工具补齐方案（实证版 v1.0）

> **来源**: 2026-08-10 全库实证扫描（`kb-health.py` 全量 2,787 文件 + 工具链接口核对 + GitHub API 仓库验证）+ MEMORY.md 既有治理教训
> **触发**: 用户要求「深度分析知识库质量问题，提供解决方案，尽量利用 GitHub 已有开源库补齐完善，而非修改 CowAgent 代码失效」
> **核心原则**: **标准工具优先**——开源标准工具能做的绝不自研；自研只保留「知识库私有语义检查」；全部方案不触碰 CowAgent 本体（`agent_stream.py`/`config.json`），以独立 CLI + `scripts/` 包装层落地
> **归档**: 2026-08-10 v1.0 | **模块**: 02_rd/02_project/03_kb_cowagent

## 📑 目录

- [摘要（TL;DR）](#摘要tldr)
- [一、质量诊断：全库实证数据](#一质量诊断全库实证数据)
- [二、问题根因分层（第一性原理）](#二问题根因分层第一性原理)
- [三、开源方案映射矩阵（核心）](#三开源方案映射矩阵核心)
- [四、分阶段实施计划](#四分阶段实施计划)
- [五、预期收益（量化）](#五预期收益量化)
- [六、风险与边界](#六风险与边界)
- [七、验证方式与可证伪预测](#七验证方式与可证伪预测)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 摘要（TL;DR）

**实证诊断**：知识库 2,787 个 md 文件（100MB）全量健康检查暴露 **15,271 errors + 144,740 warnings**。问题高度集中：
- **代码块内中文 E3：113,399 项（68%）**——早期文档大量把中文内容塞进代码块（对齐错乱 + markdownlint 无法处理）；
- **表格格式 C1+C2+C3：42,499 项（27%）**——列数不一致/无分隔行/分隔符错误；
- **断链 B1：1,137 项 + 外部 URL 11,160 个**（外部 URL 从未系统检查过）；
- **重复文件 15+ 个**（07-29 批量导入产生 `-dup1/-dup2` 副本，内容分叉污染检索）；
- **工具链自身失序**：56 个 check 脚本判定三套各异（同一问题 R1/E3/MD040 三命名）、接口不统一（`format-validator` 无 `--file`）、依赖环境脆弱（`kb-health.py` 需手工 PYTHONPATH）。

**方案核心**：用 **8 个 GitHub 开源库**替换/补齐自研检查器，自研收敛为「私有语义检查」：
| 开源库 | 替代/补齐 | 解决的问题规模 |
|:-------|:---------|:--------------|
| **Prettier**（52K★，markdown 模式）| 自动修复表格 C1/C2/C3 | 42,499（27%）|
| **markdownlint-cli2**（已装，扩 globs + 自定义规则）| MD lint 唯一出口，替代 check_md_format/format-validator | 统一三套判定 |
| **lychee**（3.8K★，Rust）| 外部 URL 死链检查 | 11,160 URL |
| **textlint**（3.2K★）+ zh 规则 | 中文排版/术语/标点 | E3 的正文侧 + 新文档预防 |
| **cspell**（1.7K★）| 英文拼写/术语词典 | 新文档预防 |
| **jscpd**（6K★）| 内容级查重（补 -dup 清理）| 15+ 重复文件 |
| **markitdown**（172K★，已装）| 素材→Markdown 加工管线 | import/ 素材层 |
| **SQLite FTS5 / ripgrep** | 本地全文检索（不耗 LLM token）| 检索层 |

**预期**：格式类 113K+42K 问题可自动化修复 ~90%；断链（外部）首次清零并纳入门禁；重复文件清理消除检索污染；检查器从 56 个收敛到「1 条标准链 + N 个私有语义脚本」——**工具治理本身是最大的质量杠杆**。

---

## 一、质量诊断：全库实证数据

### 1.1 全量健康检查（kb-health.py，2,787 文件）

| 类别 | 数量 | 占比 | 性质 |
|:-----|-----:|:----:|:-----|
| **E3-CJK-IN-CODE**（代码块内中文）| **113,399** | 68% | 内容级，需半自动修复 |
| **C3-NO-SEPARATOR**（表格无分隔行）| 17,000 | 10% | **可全自动** |
| **C2-COL-MISMATCH**（表格列数不一致）| 13,533 | 8% | **可全自动** |
| **C1-BAD-SEPARATOR**（分隔符错误）| 11,966 | 7% | **可全自动** |
| **B1-BROKEN-LINK**（断链）| 1,137 | 0.7% | 本地+外部混合 |
| **A4-ENTRY-FORMAT**（log 条目格式）| 762 | — | 私有规范 |
| **E6-NO-LANG**（代码块无语言标注）| 740 | — | 半自动 |
| **E4-NO-TOC**（无目录）| 589 | — | 自动生成 |
| **E1-BOX-DRAW**（Unicode 绘图符）| 570 | — | 半自动 |
| **E5-NO-CHANGELOG**（无变更日志）| 263 | — | 自动补 |
| **A1/A3/D1 等** | 47 | — | 零星 |
| **合计** | **15,271 errors + 144,740 warnings** | | |

### 1.2 结构性发现

| # | 发现 | 证据 | 影响 |
|:-:|:-----|:-----|:-----|
| F1 | **重复文件 15+**：`-dup1/-dup2/-copy` | 04_chip 4 个 07-29 dup1、18_methodology dup2 等 | 内容分叉、检索污染、索引歧义 |
| F2 | **外部 URL 11,160 个从未系统检查** | B1 仅覆盖本地；外部死链无任何工具覆盖 | 引用失效不可见（违反 SSOT 溯源） |
| F3 | **检查器三套判定**：同一问题三个命名 | E3(kb-health) / R1(check_md_format) / MD040(markdownlint) | 口径污染、日报统计失真（MEMORY 已记 R2 误报 P0）|
| F4 | **工具接口不统一** | `format-validator.py --file` 报 unrecognized arguments | 每次使用都要翻技能文档 |
| F5 | **依赖环境脆弱** | `kb-health.py` 需手工 `PYTHONPATH=/home/lzh/cow` 才可运行 | 定时任务/新人接入即失败 |
| F6 | **markdownlint globs 漏 01_survey** | `.markdownlint.jsonc` ignores 含 `knowledge/01_survey/**` | 保留目录（周报等）无 lint 覆盖 |
| F7 | **日志只记截断摘要** | 工具输出 `result_str[:200]`（08-07 基线已证） | 质量审计缺一手数据（已知，非本次范围） |

### 1.3 历史治理成效（基线）

- 链接问题 67,503 → 0（08-05，link-validator/fixer 自研，有效）
- markdownlint 40,940 → 2,917（08-05，残余 MD036 1,705/MD056 459/MD055 290/MD025 236/MD001 18）
- **结论**：自研工具「查」的能力已达标；「修」的能力（表格/代码块）缺失 → 正是开源库补位点。

---

## 二、问题根因分层（第一性原理）

| 层 | 根因 | 第一性原理 | 解法方向 |
|:---|:-----|:-----------|:---------|
| **内容层** | 早期文档把中文内容放代码块（对齐错觉）| 代码块语义=程序/数据，中文正文该用表格/引用 | 半自动内容迁移 |
| **格式层** | Markdown 表格手写易错 | 表格是正则敏感语法，人手维护必然漂移 | **Prettier 机器格式化（源头免疫）** |
| **链接层** | 外部 URL 无检查工具 | 网络资源失效是熵增，不查则不可见 | lychee 批量+门禁 |
| **工具层** | 检查器自研泛滥、无统一出口 | 每个自研检查器=一个维护负担+一个口径 | **标准工具收敛 + 私有语义保留** |
| **数据层** | 批量导入产生 dup | 导入管线无去重门禁 | jscpd 查重 + 导入前校验 |
| **检索层** | keyword grep 无索引 | 全文检索该用索引结构 | SQLite FTS5 本地索引 |

> 对应 MEMORY.md「修补工具化=确定性外壳释放 AI」「约束脚本化=最高杠杆」——但**修补要站在开源巨人肩上，不重复造轮子**。

---

## 三、开源方案映射矩阵（核心）

> 所有仓库 2026-08-10 GitHub API 验证活跃（star 数/最后 push）。

### 3.1 格式层（占问题 95% 的头号战场）

| 开源库 | 版本/状态 | 解决的问题 | 落地命令 | 与自研的关系 |
|:-------|:---------|:-----------|:---------|:-------------|
| **Prettier**（prettier/prettier，52K★）| 需装 | **C1/C2/C3 表格 42,499 项**：自动对齐列、补分隔行、修分隔符 | `npx prettier --write "knowledge/**/*.md" --parser markdown` | 一次性全量修复 + 新文档格式免疫 |
| **markdownlint-cli2**（DavidAnson，897★）| ✅ 已装 v0.23.2 | MD lint 唯一出口；自定义规则承载 E3/E6/E1 私有规范 | `npx markdownlint-cli2 "knowledge/**/*.md"` | **替代** check_md_format.py / format-validator.py / md-format.py 的重复判定 |
| **textlint**（textlint/textlint，3.2K★）+ `textlint-rule-preset-zh-technical-writing` | 需装 | 中文标点/空格/术语统一（正文侧 E3 的治本） | `npx textlint "knowledge/**/*.md"` | 补齐中文语义检查（自研无） |

### 3.2 链接层

| 开源库 | 状态 | 解决的问题 | 落地 | 与自研的关系 |
|:-------|:-----|:-----------|:-----|:-------------|
| **lychee**（lycheeverse/lychee，3.8K★）| 需装 | **外部 URL 11,160 个**死链检查（并发+限速+远程）| `lychee --no-progress --format markdown "knowledge/**/*.md"` | 补齐外部链接（自研只管本地）|
| **自研 link-validator/fixer** | ✅ 已有 | 本地链接（67,503→0 验证有效）| 保留 | **保留**（开源无对应"修复"能力）|

### 3.3 语义层（新文档预防）

| 开源库 | 状态 | 解决的问题 | 落地 |
|:-------|:-----|:-----------|:-----|
| **cspell**（streetsidesoftware/cspell，1.7K★）| 需装 | 英文拼写 + 服务器领域术语词典（RDMA/NVMe/UALink...）| `npx cspell lint "knowledge/**/*.md"` |
| **textlint**（同上）| 需装 | 术语一致性（同义混用检测）| 自定义规则包 |

### 3.4 去重与加工层

| 开源库 | 状态 | 解决的问题 | 落地 |
|:-------|:-----|:-----------|:-----|
| **jscpd**（kucherenko/jscpd，6K★）| 需装 | 内容级查重（token 级，支持 md）→ 定位 15+ dup 全文相似对 | `npx jscpd "knowledge/**/*.md" --format markdown` |
| **markitdown**（microsoft/markitdown，172K★）| ✅ 已装 | import/ 素材（pdf/docx/pptx）→ Markdown 加工 | `markitdown input.pdf -o output.md` |
| fdupes（文件级 md5）| 系统包 | dup 文件快速候选（配合 git 历史人工确认）| `fdupes -r knowledge/` |

### 3.5 检索层（不改 CowAgent）

| 开源库 | 状态 | 解决的问题 | 落地 |
|:-------|:-----|:-----------|:-----|
| **ripgrep**（rg）| 系统包 | 秒级全库关键词检索（替代 grep 慢扫描）| `rg "UALink" knowledge/` |
| **SQLite FTS5**（Python 内置）| ✅ 系统自带 | 知识库全文索引，检索不耗 LLM token | 一次性建索引脚本（scripts/）|

### 3.6 治理层（门禁）

| 开源库 | 状态 | 解决的问题 | 落地 |
|:-------|:-----|:-----------|:-----|
| **doc-final-check 串联**（自研 wrapper）| 改造 | 归档门禁=一条命令跑完整条标准链 | `scripts/doc-quality-gate.sh` |
| pre-commit（可选）| 需装 | git 提交前自动跑 lint | 后续可选 |

---

## 四、分阶段实施计划

### P0 立即（1-2 天，可全自动，收益最大）

| # | 动作 | 命令/方式 | 预期 |
|:-:|:-----|:---------|:-----|
| 1 | 装 prettier/lychee/textlint/cspell/jscpd | `npm i -g` / 二进制下载 | 工具就绪 |
| 2 | **Prettier 全量格式化表格**（dry-run → diff 审计 → 写回）| `npx prettier` | 表格 42K 清零 |
| 3 | markdownlint globs 扩到 01_survey + 统一出口 | 改 `.markdownlint.jsonc` | 覆盖补齐 |
| 4 | **lychee 全量扫外部 URL**（先 --max-concurrency 限速）| `lychee --format markdown` | 11,160 URL 首查 |
| 5 | jscpd 扫 dup + 人工确认 → `mv` 到 `tmp/bak/` | `npx jscpd` | 15+ dup 清理 |

### P1 一周内（半自动，需人工确认）

| # | 动作 | 方式 | 预期 |
|:-:|:-----|:-----|:-----|
| 6 | E3 代码块中文修复（转表格/text 标注）| markdownlint 自定义规则定位 + 批量脚本 + 人工抽查 | 113K 减 80%+ |
| 7 | E4/E5 TOC+Changelog 补齐 | 现有 add_toc.py 增强 | 589/263 清零 |
| 8 | doc-quality-gate.sh 串联标准链 | 自研 wrapper（不改 CowAgent）| 归档门禁 |
| 9 | SQLite FTS5 索引脚本 | scripts/ 新增 | 检索层落地 |

### P2 持续（月度）

| # | 动作 | 方式 | 预期 |
|:-:|:-----|:-----|:-----|
| 10 | 检查器收敛：废弃 check_md_format/format-validator/md-format 重复判定 | 标准链替代 + 私有语义脚本合并 | 56→~15 个脚本 |
| 11 | textlint/cspell 规则库定制（术语词典）| 规则包维护 | 新文档质量免疫 |
| 12 | markitdown 管线接入 discover | import/ → md → 加工 | 素材层 1.9 万可消化 |

---

## 五、预期收益（量化）

| 指标 | 现状 | 预期（P0+P1 后）| 依据 |
|:-----|:-----|:---------------|:-----|
| 表格格式错误 | 42,499 | **~0**（Prettier 自动）| 机器格式化确定性 |
| 代码块中文 | 113,399 | <20,000（80%+ 修复）| 半自动 + 人工抽查 |
| 外部 URL 死链 | 未检（11,160 个）| 首次清零 + 门禁防回归 | lychee 批量 |
| 重复文件 | 15+ | 0（mv 到 bak）| jscpd + 人工 |
| 检查器数量 | 56 个/三套口径 | ~15 个/单一出口 | 标准工具收敛 |
| 检索速度 | grep 全库分钟级 | rg 秒级 + FTS5 索引 | 索引结构 |

---

## 六、风险与边界

- **Prettier 全量格式化风险**：会重排列表缩进/换行/引用块 → 必须 `--dry-run` + git diff 审计 + 备份到 `tmp/bak/`；限定 `--range` 只修表格更稳（先小范围试点 02_rd/04_chip）。
- **E3 修复是内容级**：把中文从代码块移出可能改变文档结构 → 半自动 + 人工抽查，禁止全自动批改。
- **lychee 网络限速**：11,160 URL 并发检查需限速（`--max-concurrency 8`）防被源站拉黑；仅列 4xx/5xx 为死链，3xx 视策略。
- **textlint 中文规则可能误报**（领域术语）：规则包需按服务器领域裁剪，误报率 >20% 则先降级 WARN。
- **不改 CowAgent 本体**：全部为独立 CLI + scripts/ 包装层；若需 config 变更（如 tool 默认命令）走现有配置通道而非改代码。
- **01_survey 覆盖扩大后**：周报等历史文件可能大量报错 → 先 lint 新文件（`--fix` 后 diff），历史文件分批。

---

## 七、验证方式与可证伪预测

| # | 预测 | 验证窗口 | 证伪条件 |
|:-:|:-----|:--------|:---------|
| P1 | Prettier 格式化后 C1/C2/C3 < 100 项（42,499→~0）| 2026-08-14 | 表格错误仍 >1,000 |
| P2 | lychee 首扫发现外部死链 ≥50 个（从未检查过）| 2026-08-14 | 死链 <10 个 |
| P3 | dup 文件清理后 `rg -dup` 检索结果零污染 | 2026-08-14 | 仍可检索到 -dup 文件 |
| P4 | 新文档门禁接入后，每周新增格式错误 <50 | 2026-08-31 | 每周新增仍 >500 |
| P5 | 检查器收敛到单一出口后，日报口径无「三套判定」冲突 | 2026-09 | 仍出现同一问题多命名 |

---

## 参考来源

### 实证数据（一手，2026-08-10）

- `kb-health.py` 全量扫描（2,787 文件，A/B/C/D/E 五类）：15,271 errors + 144,740 warnings
- 工具链接口核对：`format-validator.py --file` 报错 / `kb-health.py` PYTHONPATH 依赖 / `.markdownlint.jsonc` globs
- 重复文件：`find knowledge -name "*-dup*"` 15+ 项（07-29 批量导入）

### 开源库验证（GitHub API，2026-08-10）

| 仓库 | stars | 最后 push | 用途 |
|:-----|------:|:---------|:-----|
| microsoft/markitdown | 172,720 | 2026-07-29 | 素材→Markdown |
| vitejs/vite（参考）| 82,282 | 2026-08-10 | （前端可视化备选）|
| prettier/prettier | 52,187 | 2026-08-09 | 表格/格式自动修复 |
| squidfunk/mkdocs-material | 27,235 | 2026-08-09 | （站点渲染备选）|
| kucherenko/jscpd | 5,982 | 2026-08-07 | 内容查重 |
| lycheeverse/lychee | 3,824 | 2026-08-09 | 外部链接检查 |
| textlint/textlint | 3,169 | 2026-08-06 | 中文语义 lint |
| streetsidesoftware/cspell | 1,667 | 2026-08-10 | 拼写/术语 |
| DavidAnson/markdownlint-cli2 | 897 | 2026-08-07 | MD lint（已装）|

### 知识库交叉引用

- `skills/knowledge-health-check/SKILL.md`（健康检查工具链 + 08-05 治理教训）
- `2026-08-07-token-consumption-deep-analysis.md`（工具回读/质量基线）
- MEMORY.md「工具/脚本+git+链接治理」段（markdownlint 40,940→2,917 残余、三套判定、R2 误报 P0）

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-10 | v1.0 | 创建。全库实证诊断（15,271 errors/144,740 warnings/dup 15+/外部 URL 11,160）；8 开源库补齐矩阵（Prettier/markdownlint/lychee/textlint/cspell/jscpd/markitdown/FTS5）；P0-P2 三阶段计划；5 项可证伪预测 |
