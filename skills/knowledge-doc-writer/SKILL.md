---
name: knowledge-doc-writer
description: Create deep technical reports/documents for the knowledge base, focused on server hardware and AI infrastructure topics. Use when the user asks to: (1) create or expand a deep technical knowledge document covering server/AI topics (BMC/hardware/interconnect/storage/compute/cluster/RAS/thermal/power/memory/storage), (2) write a knowledge base report that requires extracting information from existing KB entries, import/ directories, and online sources, (3) produce a structured technical document with proper index/log updates, (4) 服务器专题调研/AI专题调研/技术报告/知识库文档撰写, (5) convert scattered notes and imported materials into a consolidated, well-structured knowledge base document. Do NOT use for: quick opinion or recommendations, email/chat writing, creative writing, general web search summarization without deep analysis, simple daily notes or scratchpad content. When user asks to "归档" a URL or share link → use web-archive or doubao-share skills instead.
metadata:
  requires:
    bins: ["python3"]
  emoji: 📘
---

# 知识库技术文档创建技能 (Knowledge Doc Writer)

> **定位**: 本技能是 `server-asset-management-research` 的泛化版本，提炼了"从已有知识库提取 → 联网补充 → 内容编排 → 格式检查 → 索引更新 → 知识复用"的通用工作流，适用于所有**服务器硬件/AI基础设施**专题的知识库文档创建。

## 概述

本技能提供一套**标准化 6 步工作流**，用于创建符合知识库质量标准（Q6）的深度技术文档。

### Q6 质量标准

| # | 原则 | 自检问题 |
|:-:|:-----|:---------|
| **Q1** | **取材优先** | 论文/标准/规范原文 > 官方技术白皮书 > 一线工程报告 > 主流行业分析 > 通用知识 |
| **Q2** | **来源可溯** | 每条关键断言是否有出处？能否追溯到论文/标准/官方文档？ |
| **Q3** | **量化支撑** | 数据是否有数值+单位+对比基线+测试条件四要素？ |
| **Q4** | **强逻辑** | 章节划分是否 MECE？结论是否从数据推导而非先验设定？ |
| **Q5** | **交叉链接** | 是否链接了 knowledge 下已有的相关页面？ |
| **Q6** | **格式规范** | TOC顶部? Changelog底部? 代码块纯ASCII? 通用知识外链化? |
| **Q10** | **信源配比** | 内部知识库引用 ≤60%？外部独立信源 ≥40%？关键可验证断言（链路预算/器件规格/成本/交期/生态）是否有外部出处？收尾时做信源配比自检（内部 vs 外部引用计数） |

> ⚠️ **Q10 信源配比铁律（2026-08-25 用户指令）**：深度分析必须兼顾内部与外部信源，**内部引用占比 ≤60%**（外部 ≥40%），避免因内部信息产生一致性错误（知识库自身可能有系统性错误，纯内部引用会让错误一致性传播）。执行：①关键外部可验证断言必须有外部出处（标准/论文/官方文档/行业报告）；②文档收尾用 `grep -oE "\[来源: [^]]*\]"` 统计并核对配比；③内部引用用于"承接既有结论"，外部引用用于"交叉验证与补强"。

### 创建前准备

```bash
# 1. 检查目标路径和数据源
python3 <base_dir>/scripts/check_paths.py --document <目标路径> --check-sources

# 2. 执行后（格式检查）
python3 <base_dir>/scripts/check_format.py <文档路径>
```

---

## 📍 输出路径规则（强制）

本 skill 创建的深度技术分析文档**一律输出到 `knowledge/07_industry-research/`**。

> ⚠️ **严禁**将深度分析/专题调研文档保存到 `01_survey/` 目录下。`01_survey/` 仅用于存放**每日日跟踪日志**（由增量跟踪流程写入，非本 skill 管辖）。

**输出路径映射**：

| 文档类型 | 输出路径 | 示例场景 |
|:---------|:---------|:---------|
| **深度技术分析/专题报告** | `knowledge/07_industry-research/` | 协议调研、芯片深潜、方案对比、技术全景、厂商分析 |
| **AI 领域专题**（不涉及服务器硬件） | `knowledge/03_AI/` | AI 框架分析、Agent 评测基准、模型架构解读 |

> 如不确定目标路径，优先选择 `knowledge/07_industry-research/`，不要存入 `01_survey/`。

---

## 6 步工作流

### 第1步：从已有知识库 + import/discovery 中提取

#### 1a — 知识库提取

> 🚀 **2026-08-25 第一线索源：先查 `log.md` 全局账本**。`knowledge/log.md` 是全库
> 「时间序账本」（每条目 = 日期+操作+文件路径+摘要），路径+摘要密度全库最高，
> 覆盖 2026-05 至今全部文件（1316 条目，含历史移动/改名路径兜底）。
> 深度分析启动**先跑 `kb-log-search.py` 关键字检索**拿到候选文件路径+摘要，
> 再决定是否 read 全文——避免全量 read log.md（2952 行≈50KB）浪费 token。
> 检索命中路径已做存在性验证：历史路径自动兜底到当前位置（✅有效/🔀已移动/❌缺失）。

```bash
# ① log.md 第一线索源（必做）——关键字检索，输出 日期+路径+摘要（默认 AND，按日期倒序）
python3 scripts/tools/kb-log-search.py --keyword "<主题关键词>" [--keyword "词2"] [--since 2026-08-01] [--module 07_industry-research] [--limit 15]
# 多词 OR / 只看有效路径 / 账本概况与主题词探测（辅助选关键词）:
python3 scripts/tools/kb-log-search.py --keyword "A" --keyword "B" --any
python3 scripts/tools/kb-log-search.py --keyword "<主题>" --path-only
python3 scripts/tools/kb-log-search.py --stats
python3 scripts/tools/kb-log-search.py --topics

# ② 命中候选后，用 index.md 提取更全摘要（全局文件索引：路径+摘要，机器生成）
python3 scripts/tools/kb-index-extract.py --source index --keyword "<主题>" --limit 15

# ③ 关键词直接 grep 知识库文件内容（补充 log 未覆盖的新文件）
knowledge/02_rd/                    # 服务器全模块 — 03103
knowledge/03_AI/                    # AI 专题 — 03104
knowledge/07_industry-research/     # 深度专题报告 — 03108（首选已有深度内容）
knowledge/01_survey/08_incr_ir/     # 增量日跟踪 — 03102（仅搜索不做写入）
```

**推荐搜索路径**（按优先级排列）：

| 优先级 | 路径 | 内容范围 |
|:------:|:-----|:---------|
| 🥇 | `knowledge/07_industry-research/` | 深度专题报告（协议/芯片/互联/可靠性/数据中心等） |
| 🥇 | `knowledge/02_rd/*reports*/` | 深度专题报告（维护性/可观测性/资产管理/RAS等） |
| 🥇 | `knowledge/02_rd/*hardware*/` | 硬件规格与设计（BMC/内存/存储/互联/散热/供电） |
| 🥇 | `knowledge/03_AI/*tech-research-notes*/` | AI 技术研究笔记 |
| 🥈 | `knowledge/01_survey/08_incr_ir/` | 增量日跟踪（仅搜索参考，不做写入） |
| 🥈 | `knowledge/02_rd/*design*/` | 研发管理/设计文档 |
| 🥉 | `knowledge/02_rd/07_manufacturing/` | 生产制造 |
| 🥉 | `knowledge/02_rd/04_fullstack/` | 全栈/软件分析 |

#### 1b — import/ 目录提取

`import/` 目录下含有大量外部导入的原始材料（⚠️ 素材用途，按 RULE.md §5-6 约束批判性使用）：

```bash
# 搜索 import/ 下与主题匹配的文件
ls import/                    # 外部导入的原始材料（素材级别）
```

**import 目录结构**（存量的外部原始文件，⚠️ 素材级别 → 按 RULE.md §5-6 约束批判性使用）：

```
import/
├── doubao/           → 豆包对话导出 (500+ .md)
├── server/           → 服务器技术文档 (.docx/.md/.pptx/.xlsx/.csv/.html)
├── cnblogs/          → 博客园文章
├── fetched_markdown/ → 网页抓取转换 (208 files)
├── md/               → 直接导入的 md 文件 (500+ files)
└── 千问/             → 千问对话导出

注意: knowledge/import/ 已不存在 (已迁移/整合到标准模块)。import/ 为 workspace 根目录的素材仓库。
```

**提取策略**：用 `grep -rl` 或 `find` 结合关键词搜索 import/ 下的相关素材文件，找到后先 `read` 内容进行评估，有效内容交叉验证后引用到新文档中。  

> ⚠️ RULE.md §5-6 约束 — import/ 内容为素材/线索，不得作为文档唯一来源随意采纳。关键量化数据必须经至少一种独立源交叉验证。

#### 1c — discovery/ 目录提取

`discovery/` 含有通过扫描发现的外部材料（如 YouTube 转写/文档等）。如果该目录存在且与主题相关，从中提取有效内容。

#### 1d — 已有 Skill 知识提取

`skills/` 目录下的某些 skill 可能包含行业标准文档、参考材料等：

```
skills/knowledge-doc-writer/references/      ← 本 skill 的参考材料
skills/server-asset-management-research/references/  ← 资产管理参考
```

#### 提取示例（以服务器资产管理调研为例）

```bash
# 搜索知识库中已有相关内容
find knowledge/ -name "*.md" | xargs grep -li "FRU\|CMDB\|DCMI\|IPMI\|asset management\|资产管理" 2>/dev/null

# 搜索 import 目录中的相关内容
find import/ -name "*.md" | xargs grep -li "FRU\|CMDB\|asset\|BMC" 2>/dev/null

# 统计知识库中相关文件的分布
for d in knowledge/02_rd/*/ knowledge/01_survey/*/; do
    count=$(find "$d" -name "*.md" | xargs grep -l "资产管理\|FRU\|CMDB" 2>/dev/null | wc -l)
    [ $count -gt 0 ] && echo "  $d → $count files"
done
```

---

### 第2步：联网搜索补充

根据第1步中发现的不足，针对性地联网搜索补充：

#### 2a — 标准/规范类来源

| 来源 | 搜索策略 | 示例关键词 |
|:-----|:---------|:-----------|
| **DMTF/DSP 标准** | `web_fetch` 官方标准页 | `DMTF DSP xxx specification`, `Redfish`, `SMBIOS`, `DCMI` |
| **IEEE/ACM** | 论文搜索 | 主题 + `standard`/`survey`/`analysis` |
| **JEDEC/PCI-SIG/IBTA** | 官方规范 | `JEDEC DDR5`, `PCIe Gen6`, `InfiniBand` |
| **OCP** | OCP 贡献文档 | `OCP server specification`, `OCP OpenBMC` |

#### 2b — 厂商实现类来源

| 供应商 | 搜索策略 |
|:-------|:---------|
| **Dell** | `iDRAC <feature> documentation`, `Dell PowerEdge <model> technical guide` |
| **HPE** | `iLO <feature> user guide`, `HPE ProLiant <model> specification` |
| **Huawei** | `iBMC <feature> technical white paper` |
| **Inspur/浪潮** | `浪潮服务器 <feature> 技术白皮书` |
| **Supermicro** | `Supermicro BMC <feature>`, `Supermicro IPMI guide` |
| **NVIDIA** | `NVIDIA <product> technical brief`, `NVIDIA DGX <feature>` |
| **Intel** | `Intel <platform> technical overview`, `Intel server <feature>` |
| **AMD** | `AMD <platform> architecture`, `AMD server <feature>` |

#### 2c — 开源/工程实现类来源

| 来源 | 搜索策略 |
|:-----|:---------|
| **OpenBMC GitHub** | `openbmc/<repo> code / docs`, `entity-manager`, `phosphor-*` |
| **Linux Kernel** | kernel 源码中相关驱动/子系统 |
| **NetBox/CMDB 方案** | `NetBox documentation <feature>`, `iTop <feature>` |
| **工程报告/论文** | `Google "<topic> datacenter"`, `Facebook "<topic> server"` |

#### 2d — 行业分析类来源

| 来源 | 搜索策略 |
|:-----|:---------|
| **SemiAnalysis** | `SemiAnalysis <topic>` |
| **The Next Platform** | `The Next Platform <topic>` |
| **AnandTech** (archive) | `AnandTech <topic>` |
| **DIGITIMES Research** | `DIGITIMES <topic>` |

---

### 第3步：内容组织与编排

#### 3a — 文档结构模板

```markdown
# 文档标题

> 元信息: 文件状态、覆盖范围、版本
> 适用范围: 服务器平台规划/运维管理/系统设计

## 目录

[TOC]

---

## 1. 引言与范围

- 文档目的
- 目标读者
- 覆盖的技术范围

## 2. 核心概念/基本原理

- 关键概念定义
- 历史背景/演进路线
- 核心原理（第一性原理推导）

## 3. 关键技术细节

- 协议/机制/架构的深度展开
- 量化数据与对比
- 具体实现方案

## 4. 方案对比/供应商实现

- 至少 3 家主流供应商的对比
- 差异分析（架构哲学/设计权衡/商业模式）
- 开源 vs 商业方案

## 5. 运维与工程实践

- 部署/配置/监控/维护
- 常见问题与最佳实践

## 6. 平台规划建议

- 采购/RFP 规格建议
- 架构决策树
- 关键规格参数

## 7. 参考文献

[1] ...
[2] ...

---

## 变更记录

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| YYYY-MM-DD | v1.0 | 首次创建 |
```

> ⚠️ **追加/升级文档时（重要）**：新增内容（附录/新章节）必须插入到「变更记录」**之前**，保持变更记录在文件**末尾**——格式检查要求 changelog 位于文件底部（check_format R3 / check_tech_doc_quality R2_changelog），追加到 changelog 之后会导致检查失败并需移动修复（AMD CPU 路线图 v2.0→v3.0 曾两次踩坑）。

> ⚠️ **两个高频返工点（R4/R5，2026-08-11 再次踩坑，写正文时一次做对）**：
> 1. **ASCII 图/框图必须纯英文**：R4「代码块纯ASCII」为必错项，图内禁止中文（含"来源/输入/输出/模型"等注释），画完即自查，避免门禁返工。
> 2. **内部链接相对路径以文档自身所在目录为基准**：如文档在 `knowledge/07_industry-research/04_ai/` 下，链到 `03_AI/` 需 `../../03_AI/...`，链到同级子目录需 `../10_supernode-rack/...`，链到 `06_others/sources/` 需 `../../06_others/sources/...`——写完用 doc-final-check 验证全部链接，一次性写对。

#### 3b — 逻辑框架选择

| 文档类型 | 推荐结构 | 适用场景 |
|:---------|:---------|:---------|
| **技术全景/综述** | 分层展开（底层→顶层），每层先原理再实现 | 标准/协议/架构调研 |
| **方案对比/选型** | 维度对齐 → 统一量纲 → 对比矩阵 → 决策树 | 技术选型/供应商评估 |
| **原理深潜** | 基础 → 机制 → 实现差异 → 性能影响 → 趋势 | 单一协议的深入分析 |
| **工程实践** | 背景 → 需求 → 设计 → 实现 → 验证 → 运维 | 部署/配置/运维手册 |
| **失效分析** | 数据 → 模式 → 根因 → 影响 → 防范 | 可靠性/故障率分析 |

#### 3c — 编排原则

1. **MECE 划分章节**：同层互斥且穷尽，不自造分类数
2. **结论从数据出**：每章结论应是该章数据的自然推导，而非先验设定
3. **维度对齐比较**：跨方案对比前先确认同一维度，分清"能力 vs 方案"、"事实 vs 假设 vs 期望"
4. **层层递进**：从广到深，每节回答一个具体的 why/how

---

### 第4步：格式检查与质量自检

> 🚀 **2026-08-07 快速通道**：优先使用合一脚本 `scripts/check/doc-final-check.sh`，**默认 fast 模式只拦必错项**（格式 R1 + 链接），3 秒内出结果；深度文档发布前才跑 `--full` 全量门禁。**避免逐个脚本串行 + 全量输出回读**（这是上下文与时间开销的最大来源，见 feishu-vs-web-channel-cost-deep-analysis v1.1 实证）。

```bash
# ✅ 快速通道（默认，日常够用）——只跑必错项，容忍弹性
bash scripts/check/doc-final-check.sh <文档路径>
# 或加 --fix 自动修复 R1 类问题
bash scripts/check/doc-final-check.sh <文档路径> --fix

# 📋 完整门禁（深度文档正式发布前）——4 项全跑
bash scripts/check/doc-final-check.sh <文档路径> --full
```

若快速通道通过（exit=0），即可进入 Q 自检（见下）；`--full` 暴露的 R2/R3/R6 类问题按严重度决定是否修复——**非致命项（如 R6 来源标注缺失）可记录待办而非阻塞交付**。

#### 4a — 路径与数据源检查（full 模式下自动含，单独需要时）

```bash
python3 <base_dir>/scripts/check_paths.py --document <目标路径> --check-sources
```

输出示例：
```
✅ 目标目录: <workspace>/knowledge/02_rd/06_O&M/software/  (参考路径注册表 03103)
✅ index.md 存在
✅ log.md 存在
📚 知识库数据源检查:
  ✅ knowledge/02_rd/03_hardware/
  ✅ knowledge/02_rd/06_O&M/
  ...
```

#### 4b — 格式规范检查（doc-final-check --full 内含）

```bash
python3 <base_dir>/scripts/check_format.py <文档路径>
```

检查项（7 条规则）：

| 规则 | 检查项 | 严重度 |
|:-----|:-------|:------:|
| R1 | TOC 在顶部（>100行必须有） | ⚠️ |
| R2 | 参考文献章节存在 | ⚠️ |
| R3 | 变更记录章节在底部 | ⚠️ |
| R4 | 代码块纯ASCII（无中文） | ⚠️ |
| R5 | 内部交叉链接有效 | ⚠️ |
| R6 | 量化数据有来源标注 | ✅ |
| R7 | 章节 H2/H3 统计 | 统计 |

> 💡 **R6 来源标注格式**：check_format.py 在量化数据前后各 200 字符内查找来源标记，识别 `[来源: ...]`、`[Source: ...]`、`[数字]`（参考文献编号）、`[注...]`、`数据来源`、`source:` 等。⚠️ 引用块写法 `> 来源: ...` **不被识别**，会触发 R6 误报——量化数据统一用行内 `[来源: 出处]` 标注。

#### 4c — 策略合规检查（Strategy Compliance）

```bash
# 检查文件是否符合预期策略（B:深度分析）
python3 scripts/check/strategy-compliance.py <文档路径（相对 knowledge/）>

# 检查格式合规（T4 深度文档格式）
python3 scripts/check/format-validator.py <文档路径（相对 knowledge/）>
```

输出解读：
- **strategy-compliance**: 验证文件是否放在正确目录、内容是否满足深度要求、数据是否有验证
- **format-validator**: 验证 T4 格式（元信息块/TOC/Changelog/交叉链接）
- 合规分数 >= 80% 可进入下一步；< 60% 需修正

#### 4d — 质量自检清单

逐项自检（完成一项打 ✓）：

```
□ Q1-取材优先：关键章节是否引用了论文/标准/官方文档而非二手资料？
□ Q2-来源可溯：每条断言能否说出出处？无出处的已删除或标记？
□ Q3-量化支撑：所有数据是否有数值+单位+对比基线+测试条件？
□ Q4-强逻辑：章节划分 MECE？结论从数据推导还是先验设定？
□ Q5-交叉链接：是否链接了 knowledge 下已有的相关页面？
□ Q6-格式规范：TOC在顶？Changelog在底？代码块纯ASCII？通用知识外链化？
□ 通用知识外链化：背景知识是否已压缩为外部链接一句话带过？
□ 供应商对比：是否覆盖了至少 3 家主流供应商的具体实现？
□ Q7-关系记录：index.md 的关联文件列已填写？反向链接已维护？
□ Q8-策略匹配：创建策略符合 spec/design-004-knowledge-strategies.md 的定义？
   验证: python3 scripts/check/strategy-compliance.py <文档路径>
□ Q9-格式合规：T4 格式通过格式校验器？
   验证: python3 scripts/check/format-validator.py <文档路径>
□ Q10-信源配比：内部引用 ≤60%？外部独立信源 ≥40%？关键断言有外部出处？
   验证: grep -oE "\[来源: [^]]*\]" <文档路径> | 分类计数（内部文档 vs 外部信源）
```

---

### 第5步：索引与日志更新

> ⚠️ **2026-08-03 文件名规范**：全局模块新文档文件名必须符合 `YYYY-MM-DD-英文描述.md`（如 `2026-08-03-knowledge-scale-law.md`，日期=创建日，描述=英文小写-连接）。校验：`python3 scripts/check/kb-index-check.py`（C8）。

> 🚀 **2026-08-07 单同步纪律（取代三同步）**：`knowledge/README.md` / `index.md` / `log.md` 三文件**禁止 AI 直接编辑**。文档创建完成后**只做一件事**——用 `kb-log-append.py` 把全面摘要追加到 `knowledge/log.md` 尾部；**不更新** index.md/README.md（由脚本批量处理）：
>
> ```bash
> # ① 摘要写到草稿（须含标题+路径链接+说明）
> cat > tmp/kb-log-draft-<date>.md <<'EOF'
> - **📄 文档：标题** | [knowledge/<模块>/<文件>.md](<模块>/<文件>.md) — 说明
> EOF
> # ② 脚本追加（自动备份+查重）
> python3 scripts/tools/kb-log-append.py --file tmp/kb-log-draft-<date>.md --section <模块>
> ```
>
> > **01_survey 调研日报（2026-08-14 起）**：调研/追踪类输出只写 `01_survey/<子目录>/YYYY-MM-DD.md` 日期文件，**不更新** index.md/log.md（降 token：索引由脚本批量维护，AI 不手工编辑）。
> 2026-08-19 起**无保留目录**（weekly-reports 分布式 index/log 已移除）：文档落盘后用 `kb-log-append.py` 追加摘要到根 `knowledge/log.md`，**不更新**任何子目录 index.md/log.md。

#### 5a — index.md（仅保留目录）

在目标目录的 `index.md` 中添加条目：

```markdown
- [文档标题](<slug>.md) — 一句话摘要（覆盖范围/规模/核心内容）
```

**格式规范**：
- 基准目录：以 `knowledge/<模块>/` 为基准
- 使用相对路径（相对于 modules index）
- 如果是新模块缺 index.md，创建时参考同级已有 index.md 的格式

#### 5b — log.md（仅保留目录）

```markdown
## YYYY-MM-DD

- **新增** 📘 `<slug>.md` — 文档标题 v1.0（XXKB/XX章），覆盖...，参考来源：...
```

**格式规范**：
- 日期行：`## YYYY-MM-DD`
- 条目：`- **操作** emoji 路径 — 说明`
- 操作类型：`新增`/`更新`/`重构`/`删除`
- 放在对应日期的**最**新条目（同日期多个条目按时间顺序，最新的放最上面）

---

### 第6步：创建可复用的知识入口

如果该文档涉及的知识可在未来任务中复用：

1. **关键概念提取** → 如果文档中定义了新的概念/术语，在 `knowledge/concepts/` 或对应模块下创建独立的页面
2. **实体信息提取** → 如果涉及重要的公司/产品/人物，更新或创建 `knowledge/entities/` 下对应页面
3. **交叉链接补充** → 检查是否有已有页面应反向链接到新文档，补充这些反向链接

---

### 第7步：关系记录（Strategy E）

文档创建后必须记录与周边文件的关系，为后续知识图谱构建做准备：

1. **识别关联文件**
   搜索 knowledge/ 中与本文档主题相关、依赖、对比的文件，列出候选列表

2. **整理关系类型**
   使用 `spec/design-004-knowledge-strategies.md §7` 标准关系分类：
   - `related` — 内容相关，平行关系
   - `depends-on` — 本文依赖该文件作为前提
   - `see-also` — 建议一起阅读（互补）
   - `contrasts` — 与本文对比
   - `extends` — 本文扩展了该文件
   - `source-of` — 本文来源于外部资料

3. **写入索引的关系信息**
   - 全局模块（02_rd/03_AI/...）: **不更新** README.md/index.md（2026-08-07 起脚本批量处理）；关系信息只靠文档内交叉链接维护（见下）
   - 2026-08-19 起无保留目录：全局模块与 weekly-reports 均不再维护子目录 index.md（关联关系靠文档内交叉链接维护）
   格式: `关系标签1:路径1, 关系标签2:路径2, ...`
   路径: 相对 knowledge/ 目录
   
   示例:
   ```markdown
   | [`my-report.md`](my-report.md) | 深度分析报告 | 2026-07-22 | `related:03_hardware/related-topic.md, depends-on:01_basic-concepts/prerequisite.md` |
   ```

4. **反向链接维护**
   对于 bidirectional 关系（`related`/`see-also`/`contrasts`），
   在关联文件的 index.md 条目中也追加对应关系（保留目录）；全局模块文档内用交叉链接维护。
   如果关联文件所在模块的 index.md 还没有「关联文件」列，只需要在新文件的关联字段记录即可（反向链接后续由批量脚本处理）。

---

## 完整工作流速查

```
1️⃣ 提取
   │  ├── log.md 第一线索源检索 (kb-log-search.py 关键字→日期+路径+摘要)
   │  ├── index.md 摘要提取 (kb-index-extract.py --source index)
   │  ├── 知识库搜索 (02_rd/03_AI/07_industry-research/ grep)
   │  ├── import/ 目录 grep
   │  └── discovery/ 目录提取
   ▼
2️⃣ 补充
   │  ├── 标准/规范 (DMTF/JEDEC/IEEE)
   │  ├── 厂商实现 (Dell/HPE/Huawei/NVIDIA)
   │  ├── 开源工程 (OpenBMC/NetBox)
   │  └── 行业分析 (SemiAnalysis/NextPlatform)
   ▼
3️⃣ 编排
   │  ├── 选择逻辑框架（全景/对比/深潜/实践）
   │  ├── 按模板组织结构
   │  └── MECE 自检
   ▼
4️⃣ 检查
   │  ├── check_paths.py --document <path> --check-sources
   │  ├── check_format.py <path>
   │  └── Q6 自检清单
   ▼
5️⃣ 索引
   │  ├── kb-log-append.py 追加 log.md（全局模块）；保留目录 index.md 添加条目
   │  └── index.md/README.md 不更新（脚本批量处理）
   ▼
6️⃣ 复用
   │  ├── 概念页/实体页
   │  ├── 反向链接补充
   │  └── 交叉引用网络
   ▼
7️⃣ 关系
      ├── 识别关联文件（related/depends-on/see-also）
      ├── index.md 追加关联文件列
      └── 反向链接维护
```

---

## 常见场景速查

| 场景 | 第1步重点路径 | 第2步重点来源 | 第3步模板 |
|:-----|:--------------|:--------------|:---------|
| **协议调研** (PCIe/CXL/UALink) | `02_rd/03_hardware/`, `import/*.md` | IEEE/PCI-SIG/IBTA 规范 | 原理深潜 |
| **硬件规格** (BMC/CPU/GPU/HBM) | `02_rd/03_hardware/`, `import/server/` | 厂商白皮书/Datasheet | 技术全景 |
| **互联架构** (NVLink/InfiniBand/Ethernet) | `02_rd/03_hardware/`, `03_AI/` | 论文/厂商白皮书 | 方案对比 |
| **可靠性/RAS** | `02_rd/03_hardware/`, `02_rd/06_O&M/` | IEEE/Google/Facebook 论文 | 失效分析 |
| **散热/供电** | `02_rd/03_hardware/` | 工程报告/行业分析 | 技术全景 |
| **集群训练** | `03_AI/`, `02_rd/` | NVIDIA/Meta 论文 | 工程实践 |
| **资产管理** | `02_rd/06_O&M/software/` (已创建) | DMTF/Dell/HPE/OpenBMC | 技术全景 |
| **AI 基础设施** | `03_AI/`, `02_rd/` | SemiAnalysis/NVIDIA | 方案对比 |

---

## 与相关技能的关系

| 技能 | 定位 | 与本 skill 的关系 |
|:-----|:-----|:------------------|
| **`deep-tech-writer`** | 深度技术文档写作（协议/芯片级） | 互补。`deep-tech-writer` 关注原理深度，本 skill 关注知识库文档的全流程（提取→索引→复用） |
| **`doc-reviewer`** | 三层文档审查 | 下游。文档完成后可用 `doc-reviewer` 进行结构/逻辑/来源审查 |
| **`knowledge-wiki`** | 知识库日常管理 | 重叠。本 skill 是面向专题文档的强化版工作流 |
| **`knowledge-health-check`** | 知识库健康度扫描 | 下游。批量检查时使用 |
| **`server-asset-management-research`** | 资产管理专题 | 本 skill 的**实例化**（先例），从中泛化出通用工作流 |
| **`markdown-format-standards`** | 格式规范检查 | 重叠。本 skill check_format.py 覆盖基本格式检查 |

---

## 参考链接

- 工作流来源: `skills/server-asset-management-research/SKILL.md` — 实例模板
- 质量标准来源: `skills/deep-tech-writer/SKILL.md` — Q6 质量原则
- 知识库管理: `skills/knowledge-wiki/SKILL.md` — index/log 规范
- 文档审查: `skills/doc-reviewer/SKILL.md` — 下游审查
- 格式规范: `skills/markdown-format-standards/SKILL.md` — 格式细则
- 策略合规: `scripts/check/strategy-compliance.py` — 策略匹配自检脚本
- 格式校验: `scripts/check/format-validator.py` — T1-T7 格式合规脚本
- 关系校验: `scripts/check/relation-integrity.py` — 关系完整性校验脚本
- log 检索: `scripts/tools/kb-log-search.py` — log.md 关键字检索（第一线索源）
- 索引提取: `scripts/tools/kb-index-extract.py` — index.md/README.md 摘要提取

## 变更记录

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-25 | v1.1 | 1a 知识库提取新增「log.md 第一线索源」：先跑 kb-log-search.py 关键字检索（日期+路径+摘要+路径存在性兜底），再 index.md 提取摘要，最后 grep 文件内容；更新工作流速查与参考链接 |
| 2026-06-26 | v1.0 | 首次创建，从 `server-asset-management-research` 泛化提炼 |
