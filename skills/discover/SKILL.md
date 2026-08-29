---
name: discover
description: "AI批量化知识加工与内容提升。Use when: (1) processing import/素材 to extract questions, classify, and extract keywords; (2) batch-enhancing discover/ content quality; (3) generating knowledge documents from extracted questions/insights; (4) importing processed content from discover/ to knowledge/; (5) user mentions '提拉内容'/'加工素材'/'批量处理'/'内容提升'/'知识发现'/'discover' in context of content processing. Do NOT use for: single-article deep research (→ deep-tech-writer), knowledge base writing (→ knowledge-doc-writer), web archiving (→ web-archive)."
---

# Discover — AI 批量化知识加工技能

> **需求规格**: [`spec/sr-005-discover-dir-req.md`](../../spec/sr-005-discover-dir-req.md)
> **设计方案**: [`spec/design-007-skills-scripts-design.md`](../../spec/design-007-skills-scripts-design.md)
> **核心哲学**: 知识库价值 = 有效输出 / 存储量。围绕用来建。
> **方法论基础**: 注意力稀释与分级加工理论 — [`knowledge/methodology/ai-batch-processing-hierarchy.md`](../../knowledge/methodology/ai-batch-processing-hierarchy.md)
>
> 本 skill 的设计天然遵循 L1（文件级）→ L2（汇聚级）→ L3（洞察级）三级流水线，这是基于 Transformer 注意力机制本质的最优处理模式。

---

## 📑 目录

- [1. 定位与触发场景](#1-定位与触发场景)
- [2. 工作流总览](#2-工作流总览)
- [3. 脚本工具链](#3-脚本工具链)
- [4. 加工管道详解](#4-加工管道详解)
- [Changelog](#changelog)

---

## 1. 定位与触发场景

### 1.1 系统定位

discover/ 位于 import/（原始素材）和 knowledge/（正式知识库）之间的 AI 批量化加工层：

```
import/ (原始素材)          discover/ (本技能加工层)          knowledge/ (正式库)
┌──────────────┐          ┌──────────────────────┐        ┌──────────────┐
│  不问质量     │  脚本    │  AI 批量提取问题       │  强约束 │  MECE 分类    │
│  不查格式     │ ──────→ │  AI 分类/提取关键字    │ ─────→ │  格式规范     │
│  原始留存     │          │  问题→文档生成         │         │  来源可追溯   │
│  18,895 文件  │          │  质量提升治理          │         │  2,026 文件   │
└──────────────┘          └──────────────────────┘        └──────────────┘
                                │       ↑
                                │       │    退回优化
                                ▼       │
                          ┌──────────────────┐
                          │  质量门禁          │
                          │  不通过 → 退回     │
                          └──────────────────┘
```

### 1.2 触发场景

| 触发词/场景 | 处理方式 | 优先级 |
|:------------|:---------|:------:|
| "提取 import 中的问题" / "从素材中提取问题" | 调用 `extract-questions.py` | P0 |
| "对 discover 内容做分类" / "AI 分类" | 调用 `ai-classify.py` | P0 |
| "提取关键字/关键词" | 调用 `ai-extract-keywords.py` | P0 |
| "批量提取问题" / "从这些文件提取问题" | 调用 `ai-batch-extract-questions.py` | P0 |
| "从问题生成文档/知识卡片" / "问题转文档" | 调用 `ai-batch-gen-docs.py` | P0 |
| "批量质量提升" / "治理 discover" | 调用 `ai-batch-enhance.py` | P1 |
| "归档到 knowledge" / "导入 knowledge" | 调用 `import-to-knowledge.py` | P1 |
| "跑完整 discover 管道" / "全流程加工" | 按 §4 顺序执行 7 步 | P0 |

### 1.3 Don't Use When

- ❌ 单篇深度技术分析 → 用 `deep-tech-writer`
- ❌ 知识库正式文档写作 → 用 `knowledge-doc-writer`
- ❌ URL/网页归档 → 用 `web-archive`
- ❌ 豆包链接归档 → 用 `doubao-share`
- ❌ import/ → knowledge 直接导入（不经过 discover 加工）→ 用 `autokb/run_pipeline.py`

---

## 2. 工作流总览

```
┌─────────────────────────────────────────────────────────────────────┐
│                    discover/ 完整加工管道（7 步）                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  import/ 素材                                                       │
│    ↓                                                                │
│  ① 问题提取 ──────────────────────▶ discover/questions/            │
│    ↓                                                                │
│  ② AI 分类 ───────────────────────▶ 分类标签元数据                  │
│    ↓                                                                │
│  ③ AI 提取关键字 ─────────────────▶ 关键词列表                      │
│    ↓                                                                │
│  ④ AI 批量提取问题 ───────────────▶ discover/questions/ 结构化      │
│    ↓                                                                │
│  ⑤ 问题→文档生成 ─────────────────▶ discover/newwiki2/ 知识卡片     │
│    ↓                                                                │
│  ⑥ AI 批量文档治理 ───────────────▶ discover/ 提升后内容             │
│    ↓                                                                │
│  ⑦ 质量门禁 + discover→knowledge ─▶ knowledge/ 对应模块             │
│     质量标准: sr-007 (四级分级+四维评估)                             │
│     扫描脚本: scripts/check/discover-quality-scan.py                 │
│     质量报告: discover/report/YYYY-MM-DD-quality-scan.md             │
│                                                                    │
└─────────────────────────────────────────────────────────────────────┘

各步骤可独立运行，也可通过 --pipeline 串联执行。
```

### 2.1 数据流转

| 步骤 | 脚本 | 输入 | 输出 | 质量检查点 |
|:-----|:-----|:-----|:-----|:-----------|
| ① | `extract-questions.py` | `import/` 素材 | `discover/questions/` | 问题完整度 > 50% |
| ② | `ai-classify.py` | discover/ 任意文件 | 分类标签 (JSON/Frontmatter) | 分类体系覆盖率 ≥ 80% |
| ③ | `ai-extract-keywords.py` | discover/ 任意文件 | 关键词列表 (JSON) | 关键词数量 5-15 个 |
| ④ | `ai-batch-extract-questions.py` | 目录/文件列表 | `discover/questions/` JSON | 去重率 ≥ 90% |
| ⑤ | `ai-batch-gen-docs.py` | `discover/questions/` | `discover/newwiki2/` | 文档结构完整性 |
| ⑥ | `ai-batch-enhance.py` | discover/ 存量文件 | 提升后内容 | ⭐⭐→⭐⭐⭐ 提升 ≥ 1 级 |
| ⑦ | `import-to-knowledge.py` | discover/ 通过门禁 | `knowledge/` + index+log | Q-03~Q-09 准入条件 |

---

## 3. 脚本工具链

### 3.1 所有脚本

```bash
# ① import 问题提取
python3 scripts/discover/extract-questions.py --source import/doubao/ --output discover/questions/

# ② AI 分类
python3 scripts/discover/ai-classify.py --input discover/newwiki2/ --output tags.json

# ③ AI 提取关键字
python3 scripts/discover/ai-extract-keywords.py --input discover/newwiki2/server-hardware/ --output keywords.json

# ④ AI 批量提取问题
python3 scripts/discover/ai-batch-extract-questions.py --input discover/site/ --output discover/questions/ --batch-size 10

# ⑤ 问题→文档生成
python3 scripts/discover/ai-batch-gen-docs.py --input discover/questions/questions.json --output discover/newwiki2/

# ⑥ 批量文档治理
python3 scripts/discover/ai-batch-enhance.py --input discover/newwiki2/ --min-quality ⭐⭐

# ⑦ discover→knowledge 导入
python3 scripts/discover/import-to-knowledge.py --input discover/newwiki2/server-hardware/ --target knowledge/02_rd/

# 全管道串行执行
python3 scripts/discover/ai-batch-enhance.py --pipeline --input discover/newwiki2/
```

### 3.2 与现存脚本的关系

| 现存脚本 | 本技能脚本 | 关系 |
|:---------|:-----------|:-----|
| `scripts/tools/extract-user-questions.py` | `extract-questions.py` | 继承逻辑，加 argparse + --source/--output/--dedup |
| `scripts/tools/classify-questions.py` | `ai-classify.py` | 继承分类关键词体系，加 AI 语义兜底 |
| `scripts/autokb/discover.py` | `scripts/discover/` 各脚本 | 新脚本更细粒度、可独立调用；autokb 保留旧管道 |
| `discover/batch_*.py` | `ai-batch-enhance.py` | 新脚本吸收历史脚本经验，加 CLI 标准化 |

---

## 4. 加工管道详解

### 4.1 步骤①: import 问题提取

从 `import/` 目录的原始素材中提取用户问题或核心问题点。

```bash
# 全量提取
python3 scripts/discover/extract-questions.py --source import/ --output discover/questions/ --dedup

# 指定素材来源
python3 scripts/discover/extract-questions.py --source import/doubao/ --output discover/questions/doubao/

# 预览不写入
python3 scripts/discover/extract-questions.py --source import/cnblogs/ --dry-run
```

**输出格式**: 每批次一个 JSON 文件，结构如下：
```json
{
  "batch_id": "2026-07-24-001",
  "source": "import/doubao/",
  "questions": [
    {"id": "q-001", "text": "如何优化 PCIe Gen5 信号完整性？", "source_file": "...", "confidence": 0.95},
    {"id": "q-002", "text": "BMC 固件升级失败如何处理？", "source_file": "...", "confidence": 0.88}
  ],
  "stats": {"total_files": 100, "questions_extracted": 350, "dedup_rate": 0.85}
}
```

### 4.2 步骤②: AI 分类

对 discover/ 中的内容按预设分类体系自动归类。

**分类体系**（从 `scripts/tools/classify-questions.py` 继承扩展）:

| 一级分类 | 二级分类 | 关键词 |
|:---------|:---------|:-------|
| 硬件架构 | 服务器/GPU/互联 | server, PCIe, NVLink, GPU, CPU |
| AI 技术 | 大模型/训练/推理 | LLM, training, inference, MoE |
| 系统软件 | BMC/固件/OS | BMC, BIOS, firmware, driver |
| 数据中心 | 供电/散热/网络 | power, cooling, networking, rack |
| 存储 | 分布式/协议 | NVMe, CXL, storage, SSD |
| 运维管理 | 监控/部署 | monitoring, deployment, K8s |
| 方法论 | 架构/设计 | architecture, design, methodology |

```bash
python3 scripts/discover/ai-classify.py --input discover/site/ --output tags.json
python3 scripts/discover/ai-classify.py --input discover/newwiki2/ --output tags.json --apply  # 写入 frontmatter
```

### 4.3 步骤③: AI 提取关键字

从内容中提取 5-15 个代表性关键词。

```bash
# 单文件
python3 scripts/discover/ai-extract-keywords.py --input discover/newwiki2/server-hardware/pcie-gen6.md

# 批量目录
python3 scripts/discover/ai-extract-keywords.py --input discover/newwiki2/server-hardware/ --output keywords.json

# 写入 frontmatter
python3 scripts/discover/ai-extract-keywords.py --input discover/newwiki2/ --apply
```

### 4.4 步骤④: AI 批量提取问题

从陈述性内容中推理可提问的问题（与步骤①互补——步骤①提取已有问题，步骤④生成新问题）。

```bash
# 从 site/ 文章生成问题
python3 scripts/discover/ai-batch-extract-questions.py --input discover/site/AI与机器学习/ --output discover/questions/ai-questions.json --batch-size 5

# 从 newwiki2/ 知识卡片提取可追问点
python3 scripts/discover/ai-batch-extract-questions.py --input discover/newwiki2/ --output discover/questions/followup-questions.json
```

### 4.5 步骤⑤: 问题→文档生成

将提取的问题/亮点转化为结构化知识文档。

```bash
# 从问题 JSON 生成知识卡片
python3 scripts/discover/ai-batch-gen-docs.py --input discover/questions/ai-questions.json --output discover/newwiki2/

# 指定模板类型（技术/观点/数据）
python3 scripts/discover/ai-batch-gen-docs.py --input discover/questions/questions.json --template tech --output discover/newwiki2/
```

**生成模板**:
- **技术类**: 问题背景 → 核心概念 → 技术细节 → 关键数据 → 方案对比 → 参考来源
- **观点类**: 论点 → 论据 → 反方观点 → 结论
- **数据类**: 数据源 → 统计方法 → 关键发现 → 趋势分析

### 4.6 步骤⑥: AI 批量文档治理

对 discover/ 存量内容进行批量质量提升。

```bash
# 提升所有 ⭐⭐ 级别的文件到 ⭐⭐⭐
python3 scripts/discover/ai-batch-enhance.py --input discover/newwiki2/ --min-quality ⭐⭐

# 指定提升模板（摘要增强/结构化/交叉引用）
python3 scripts/discover/ai-batch-enhance.py --input discover/site/ --mode summary --batch-size 20

# 全管道（先分类→关键字→增强）
python3 scripts/discover/ai-batch-enhance.py --pipeline --input discover/newwiki2/
```

**治理检测项**:
- ❌ 模板空壳 — 只有标题没有实质内容
- ❌ 断言无出处 — 核心论断没有来源标注
- ❌ 数据缺失 — 量化数据缺少单位/基线/条件
- ❌ 空洞套话 — "非常重要" "值得关注" 无展开
- ❌ 质量自评虚高 — frontmatter 标记与实际不符

### 4.7 步骤⑦: discover → knowledge 导入

通过质量门禁后，将内容归档到 knowledge/ 正式库。

```bash
# 单文件导入
python3 scripts/discover/import-to-knowledge.py --input discover/newwiki2/pcie-gen6.md --target knowledge/02_rd/

# 批量目录导入 + 自动分类
python3 scripts/discover/import-to-knowledge.py --input discover/newwiki2/server-hardware/ --auto-classify

# 质量门禁检查（不实际导入）
python3 scripts/discover/import-to-knowledge.py --input discover/newwiki2/ --gate-only
```

**准入检查（Q-03~Q-09）**:
1. ✅ 断言可追溯 — 标注来源
2. ✅ 数据四要素 — 数值+单位+基线+条件
3. ✅ 非空摘要 — 开头 2-5 句摘要
4. ✅ 格式合规 — std-002 格式
5. ✅ 已通过验证 — 至少一轮验证
6. ✅ 有明确归入模块 — 7+4 模块之一
7. ✅ 无 bak 引用

---

## 5. 多文档处理最佳实践

> 源自 T07 多文档处理陷阱与分层架构方法论。当面对多个关联文件需要批量处理时，遵循以下模式避免常见陷阱。

### 5.1 多文档处理的四大错误模式

| 模式 | 表现 | 后果 | 避免方法 |
|:-----|:------|:------|:---------|
| **直灌模式** | 8 个专题文件总计 4,183 行全部塞入上下文一次性处理 | 注意力稀释，关键信息遗漏 40%+ | 分步处理 + 每步提取摘要 |
| **清单模式** | 只罗列文件名不读内容，直接生成报告 | 报告只有文件名无实质分析 | 每文件必须至少 read + 提取 ≥3 个要点 |
| **无契约模式** | 多个处理步骤间无中间产物结构约定 | 下游不知上游产出格式 | 每步输出有固定格式（JSON/表格） |
| **缺门禁模式** | 处理结果不验证直接归档 | 质量不达标还需返工 | 设置每步输出质量门禁（至少 ⭐⭐） |

### 5.2 三阶段流水线模式（推荐）

```
阶段一 [采集+预读] → 读取每个文件，提取元信息（标题/版本/核心数据/关键判断）
        输出: 结构化摘要列表（JSON/表格）

阶段二 [交叉分析] → 对比各文件内容，识别重叠/矛盾/互补/缺失
        输出: 交叉分析表 + 合并建议

阶段三 [综合输出] → 基于前两阶段输出，生成完整报告
        输出: 最终文档（含来源交叉引用）
```

### 5.3 单步原则

- **每个 read 调用读 1 个文件** — 不一次性全部加载到上下文
- **每个 write 调用写 1 个章节** — 不一次性写完整报告
- **关键数据读 2 次** — 第一次定位，第二次精确提取数值
- **中间状态显式保存** — 每阶段结束保存中间产物到 `tmp/`（加时间戳标记）

### 5.4 多文档合并决策树

```
判断: 这些文件能否合并为一个文档？
├── 同一主题 + 互补视角 → ✅ 合并，使用交叉引用网络
├── 同一主题 + 互相矛盾 → ⚠️ 先分析矛盾根因再合并
├── 不同主题 + 同一项目 → ⚠️ 创建汇总索引而非合并
└── 不同主题 + 不同项目 → ❌ 保持独立
```

### 5.5 批量处理前检查清单

| # | 检查项 | 判定 |
|:-:|:-------|:----:|
| 1 | 文件总数超过 5 个？ | 若是，启用三阶段流水线 |
| 2 | 单文件超过 500 行？ | 若是，先提取摘要再处理 |
| 3 | 文件间有交叉引用？ | 若是，建立交叉索引表 |
| 4 | 数据可能存在矛盾？ | 若是，预留矛盾分析步骤 |
| 5 | 是否需要保留独立文件？ | 合并 ≠ 删除独立文件 |
| **6** | **脚本执行是否已超 30s 超时？** | 若是，拆分为子批次，每批 ≤3 文件 |
| **7** | **中间产物是否显式保存到 tmp/？** | 若是，加时间戳标记，便于断点恢复 |

### 5.6 异常兜底机制（新增 · 必修）

> 多文档/批量处理时，异常是最常见而非最罕见的情况。必须预设兜底策略。

**典型异常场景与处理**:

| 异常 | 症状 | 兜底策略 |
|:-----|:------|:---------|
| **文件读取失败** | read 返回空/错误 | 跳过该文件，记录到 `tmp/error-log.md`，继续处理其余文件 |
| **单步超时（>60s）** | 工具调用超时 | 将当前步骤拆为子步骤，每子步单独记录中间产物到 `tmp/` |
| **上下文溢出** | 输出截断/遗漏 | 启用三阶段流水线（§5.2），每阶段只处理 ≤3 文件 |
| **中间产物丢失** | session 中断，tmp 无文件 | 从 `conversation-log/` 恢复最后已知状态，重新生成中间产物 |
| **多文档内容矛盾** | 报告中有对立数据 | 不掩盖矛盾，在输出中显式标注 "⚠️ 数据矛盾：来源A vs 来源B" |
| **质量门禁不通过** | discover 产出 < ⭐⭐ | 退回前一步骤，针对性重做（不从头重做） |

**断点续传（三阶段版）**:

```
异常中断
    ↓
Step 1: 检查 tmp/ 下的中间产物（find tmp/ -name "*<task-tag>*"）
Step 2: 确定最后完成的阶段（阶段一 / 阶段二 / 阶段三）
Step 3: 从下一阶段恢复（不重做已完成阶段）
Step 4: 恢复后做一致性校验（交叉验证前后产出是否一致）
```

**兜底原则**: 宁可产出降级也不产出中断。部分结果 + 明确的残缺标注 > 无结果。

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:---------|
| 2026-07-24 | v1.0 | 初始版本：discover/ AI 批量化知识加工技能，覆盖 7 步加工管道，对应 FR-22~FR-28 |

## 参考文件

- [`spec/sr-005-discover-dir-req.md`](../../spec/sr-005-discover-dir-req.md) — discover/ 需求规格
- [`spec/design-007-skills-scripts-design.md`](../../spec/design-007-skills-scripts-design.md) — Skills/Scripts 设计方案
- [`scripts/skills-scripts-mapping.md`](../../scripts/skills-scripts-mapping.md) — 映射表
