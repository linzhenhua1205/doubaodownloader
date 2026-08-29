---
name: server-competitor-analysis
description: >
  服务器软硬件固件三维竞品分析框架与工具。基于 knowledge/02_rd/03_management/08_competitive-analysis/
  方法论体系，提供完整的竞品信息采集、维度对比、深度解读与报告生成能力。
  使用场景：(1) AI服务器/GPU服务器竞品对比 (2) 硬件/软件/固件全栈竞品分析
  (3) 竞品战略意图推断与应对策略 (4) 竞品分析报告自动生成
  触发词：竞品分析、竞品对比、竞争对手分析、同类产品分析、对标分析、竞争分析、competitor analysis
metadata:
  requires:
    bins: [bash, python3]
  emoji: 🕵️
---

# 服务器竞品分析 Skill

> 基于三层世界观（硬件·软件·固件）的竞品分析实战框架

## 前置依赖

- **方法论基础**: `knowledge/02_rd/03_management/08_competitive-analysis/`（竞品分析目录，含方法论文档）
- **知识库关联**:
  - `knowledge/02_rd/` 检索已有竞品相关的技术文档
  - `knowledge/02_rd/01_product/` 检索已归档的架构/产品分析

## 脚本工具集

脚本位于本 Skill 的 base_dir `/scripts/` 目录下：

| 脚本 | 功能 | 使用时机 |
|:-----|:-----|:---------|
| `competitor-collect.sh` | 信息采集清单检查 | 开始采集时：列出需采集的信息源并检查完整性 |
| `comparison-data-collector.py` | 维度对比表模板生成+数据验证 | 采集完成后：生成结构化数据模板并验证填充率 |
| `dimension-table.sh` | 对比表渲染 | 数据填充后：从结构化数据生成Markdown对比表 |
| `report-skeleton.sh` | 报告骨架生成 | 分析完成前：生成完整报告框架 |

## 标准执行流程

### Phase 1: 设定分析范围

1. **确定分析目标**：哪个竞品？哪个场景？（AI训练/推理/通用计算/存储）
2. **确定威胁等级**：P0直接对手 / P1重要对手 / P2新兴对手 / P3观察级
3. **确定分析深度**：L1规格层 / L2逻辑层 / L3战略层
4. **生成采集清单**：执行 `bash <base_dir>/scripts/competitor-collect.sh "<竞品名>" <输出目录>`

### Phase 2: 信息采集

按以下顺序采集，每项完成后在清单中勾选：

1. **官方信息** — 官方产品页、Datasheet、白皮书（使用 `web_fetch` 获取）
2. **第三方评测** — ServeTheHome/AnandTech/ChipsandCheese 等拆机评测
3. **性能数据** — MLPerf/SPEC 标准化基准测试
4. **用户反馈** — Reddit/HackerNews/开发者论坛的真实使用体验
5. **代码/社区** — GitHub仓库、Issue列表、commit历史
6. **安全公告** — CVE/PSIRT、漏洞修复记录

**关键原则**：
- 官方数据看**上限**，实测数据看**下限**，用户反馈看**真实**
- 必须至少 3 个独立信源交叉验证
- 采集完成后执行 `bash <base_dir>/scripts/competitor-collect.sh "<竞品名>" <输出目录>` 验证完整性

### Phase 3: 维度对比

1. **生成结构化数据模板**：
   ```bash
   python3 <base_dir>/scripts/comparison-data-collector.py \
     --competitors "我们自己,竞品A,竞品B,竞品C" \
     --output <输出目录>/comparison-data.txt
   ```

2. **填充数据**：在生成的 `comparison-data.txt` 中逐项填写各竞品参数
3. **验证完整性**：
   ```bash
   python3 <base_dir>/scripts/comparison-data-collector.py \
     --validate <输出目录>/comparison-data.txt
   ```
4. **生成对比表**：
   ```bash
   bash <base_dir>/scripts/dimension-table.sh <输出目录>/comparison-data.txt <输出目录>/comparison-table.md
   ```

### Phase 4: 三层深度解读

对每个维度执行 L1→L2→L3 分析递进：

| 层次 | 问题 | 输出 |
|:----:|:-----|:-----|
| L1 规格 | 竞品参数是什么？ | 事实清单 |
| L2 逻辑 | 竞品为什么这么设计？表面优势的背后牺牲了什么？ | 权衡分析 |
| L3 战略 | 竞品这么做意味着什么战略意图？对我们的威胁多大？ | 应对建议 |

**每个维度必问三个问题**：
```
① "竞品这样设计，解决了什么真实用户痛点？"
② "为了解决这个痛点，竞品牺牲了什么？"
③ "如果我们要做，可以采用更优的解决方案吗？"
```

### Phase 5: 生成报告

1. **生成报告骨架**：
   ```bash
   bash <base_dir>/scripts/report-skeleton.sh \
     "<报告标题>" \
     <输出目录>/competitive-analysis-report.md
   ```

2. **填充各章节**：从 Phase 3 的对比表和 Phase 4 的深度解读中提取内容
3. **完成 §9 应对策略**：
   - 确定 5 种策略行为（追赶/超越/差异化/合作回避/放弃）
   - 分配 P0-P2 优先级和责任人
4. **设置跟踪计划**：下次分析的触发条件和关键信号

### Phase 6: 归档

1. 将最终报告归档到 `knowledge/02_rd/03_management/08_competitive-analysis/`
2. 执行归档三件套（**2026-08-07 纪律**：三文件禁止 AI 直接编辑）：
   - 把报告摘要（标题+路径+说明）写到 `tmp/` 草稿，运行 `python3 scripts/tools/kb-log-append.py --file <草稿>` 追加到 `knowledge/log.md`
   - `knowledge/index.md` / `README.md` 不在单次归档时更新，由批量脚本（`kb-global-index.py`）定期刷新
3. 将关键发现写入 `MEMORY.md` 或当日记忆 `memory/`
4. 若有跨领域影响，在 `knowledge/01_survey/industry-research/` 下写入日期文件（`YYYY-MM-DD.md`），不更新 index/log（01_survey 纪律：只写日期文件，索引由脚本批量维护）

## 分析质量自检清单

| # | 检查项 | 标准 |
|:-:|:-------|:-----|
| 1 | ✅ 三层覆盖 | 硬件·软件·固件每层至少 3 个维度 |
| 2 | ✅ L2 逻辑层 | 每个对比维度的"为什么"都有解释 |
| 3 | ✅ L3 战略层 | 有竞品战略意图推断和对我影响评估 |
| 4 | ✅ 三角验证 | 核心数据至少有 2 个独立来源交叉验证 |
| 5 | ✅ 量化数据 | 关键参数有数值+单位+条件（非"差不多"） |
| 6 | ✅ 应对策略 | 必须有 P0/P1/P2 行动项，不纯描述 |
| 7 | ✅ 陷阱检查 | 不自证偏误、不忽略固件层、不唯性能论 |
| 8 | ✅ 归档完整 | 报告+index+log+记忆，一个不落 |
