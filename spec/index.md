# spec/ 索引

> **生成**: 2026-08-06 | **文件数**: 43（42 活跃 + 1 归档桩） | **总行数**: ~34,200
>
> spec/ 目录的完整索引表。阅读路线图见 [spec/README.md](README.md)。
>
> **最近优化**: 2026-08-19 — ① +sr-011 CowAgent 工程改进点需求收集；② **spec/ 全面提升（第一批）**：design-001 v3.3 / std-001 v4.0 / sr-003 v1.6 深度提升（结论先行 + 状态字段 + 旧内容备注化）+ 6 文件补 TOC + 3 文件双分隔线修复 + 死链修复 + 结构审计确认；③ **spec/ 全面提升（第二批）**：6 核心文件深度提升（design-003 v2.0 / design-004 v2.0 / std-002 v2.0 / std-003 v3.0 / sr-001 v2.0 / meth-001 v2.0——结论先行 + 旧头部备注化）+ 全部 44 活跃文件补「结论先行（30 秒版）」+ std-003 单轨制残留修正，全库 53/54 文件结论先行覆盖；④ **spec/ 全面提升（第三轮）**：5 核心文件深度提升（design-007 v2.2 / design-008 v2.0 / ar-001 v2.2 / std-004 v1.1 / sr-009 v2.1——旧头部降级「📌 备注」块 + 状态字段 + 提升说明）+ 全库 25 文件补状态字段 + 第三轮提升说明（全库 53/54 状态覆盖）+ 单轨制残留备注化（design-004 §5.4 / design-008 §2.2 / design-011 §97+C6 / meth-003 §6.2~6.4·§9.3 / std-005 STEP3）+ 暴露 check-scheduled-tasks-compliance.py C6 未适配单轨制（待办）；⑤ **spec/ 内容质量提升（第四轮）**：9 处正文章节级备注化（design-001/003/005/007/008/011、meth-006 的过时数据与失效引用标注「2026-07 快照」+ 当前口径，正文未删除）+ 全库死链甄别（21 处：19 示例/历史 + 2 有效）；⑥ **spec/ 需求点补充（第五轮）**：ar-001 v2.3 新增 AR-DOC-001「文档内部闭环与索引友好」锚点（§2.8 分组）+ std-002 v2.1 §3.6 R1-R11 三层规则（内容自包含/log 摘要化/索引头部可提取）。

---

## 📑 目录

- [索引表](#索引表)
- [按前缀统计](#按前缀统计)
- [已归档文件](#已归档文件)
- [去重汇总](#去重汇总)

---

## 索引表

| # | 文件 | 行数 | 前缀 | 核心目标 | 状态 |
|:-:|:-----|:----:|:----:|:---------|:----:|
| 1 | `design-001-system-architecture.md` | 1,346 | design- | 四层架构 + 四阶段数据流（v3.3 提升版：结论先行） | ✅ v3.3 |
| 2 | `design-003-knowledge-directory-design.md` | 1,109 | design- | MECE 分类 + 文件变更 + 工作区全景 | ⚠️ §5/6 废弃（见 design-009） |
| 3 | `design-004-knowledge-strategies.md` | 834 | design- | 5类文件策略五维约束 | ✅ |
| 4 | `design-005-scheduler-reliability.md` | 310 | design- | Fail-Fast + 来源分级 | ✅ |
| 5 | `design-006-token-optimization.md` | 1,170 | design- | 11 组 Token 优化方案（通用方法论+案例验证） | ✅ v3.8 |
| 6 | `design-007-skills-scripts-design.md` | 1,897 | design- | 双引擎设计规范 + 14 类 Skills 分类 + 映射 | ✅ v2.3 |
| 7 | `design-008-knowledge-retrieval-framework.md` | 730 | design- | 知识检索：去重·索引·语义接入·三层方案 | ✅ v2.0 |
| 8 | `design-009-kb-index-log-dual-track.md` | 343 | design- | 索引/日志双轨制：全局 index.md + log.md | ⚠️ DEPRECATED → design-010 |
| 9 | `design-010-kb-index-log-v3.md` | 442 | design- | 索引/日志 V3 v1.1：index.md→README.md + 摘要注入 + 提取/check 脚本 | ✅ 已实施 |
| 10 | `design-011-scheduled-tasks-system-design.md` | 376 | design- | 定时任务体系：三层架构 + 9 项规则 + 时间窗口 + 合规 | ✅ v1.0 |
| 11 | `design-012-daily-weekly-report-pipeline.md` | 480 | design- | 日报/周报/月报生成链路：三层架构 + 8 脚本解读 + 文件全景 + Token 热点(知识库全量20M/97.9%) + 三级优化方案 | ✅ v1.0 |
| 12 | `design-013-scheduled-research-tasks-mechanism.md` | 380 | design- | 定时调研任务机制：39任务三层链 + runner v1.6 九命令九规则 + 读写文件全景 + 修复对话上下文累积(clear_history=True) + Token三级优化 | ✅ v1.0 |
| 13 | `design-014-conversation-context-mechanism.md` | 340 | design- | 对话上下文机制深度解读：三层模型 + 会话生命周期 + 持久化/恢复/裁剪 + 6渠道session体系 + 12场景矩阵 + 定时任务三层保障 | ✅ v1.0 |
| 14 | `meth-001-architecture-methodology.md` | 1,204 | meth- | 六步法架构描述优化 | ✅ |
| 15 | `meth-002-skills-scripts-audit-method.md` | 915 | meth- | Skills/Scripts 深度审计模板 + 七步流水线 + 9段式报告 | ✅ v1.1 |
| 16 | `meth-003-knowledge-information-methodology.md` | 1,039 | meth- | 六域模型·目录边界·分布式/集中式·源维护·元数据体系 | ✅ v1.0 |
| 17 | `meth-004-industry-research-methodology.md` | 820 | meth- | 行业调研完整方法论：22 源体系 + 3 组聚合 + 两阶段流水线 | ✅ v1.0 |
| 18 | `meth-005-system-review-feedback.md` | 1,122 | meth- | 审查结果组织 + 意见修改闭环：20困境(5层) + 7大编写质量提升 | ✅ v1.4 |
| 19 | `meth-006-kb-construction-patterns.md` | 1,160 | meth- | 36种知识库搭建设计模式（6类）+ AI使用模式8种 + 组合场景4 + 反模式6 | ✅ v1.0 |
| 20 | `meth-007-ai-detail-precision-control.md` | 577 | meth- | AI 细节精调三阶段协议：批准基线·不可变区域·回归检测·5失败模式 | ✅ v1.0 |
| 21 | `meth-008-doc-vs-code-systems.md` | 938 | meth- | 文档系统 vs 代码系统：10维全对比 + 8+6模式迁移 + Docs-as-Code | ✅ v1.0 |
| 22 | `meth-009-generate-then-maintain.md` | 502 | meth- | 两阶段知识生产法：生成优先 + 集中维护 + 检查/优化脚本设计 | ✅ v1.0 |
| 23 | `meth-010-knowledge-system-engineering.md` | 855 | meth- | 知识库系统工程方法论：七层框架 | ✅ v1.0 |
| 24 | `meth-011-file-quality-three-layer.md` | 316 | meth- | 文件质量三层模型：L1 产出快检 + L2 专业补齐 + L3 专项深修 | ✅ v1.0 |
| 25 | `meth-012-kb-observability-methodology.md` | 402 | meth- | 知识库可观测性方法论：指标总表 + 六大子系统 + 三层汇总闭环 | ✅ v1.1 |
| 42 | `meth-013-workflow-system.md` | ~460 | meth- | Workflow 体系方法论：静态/动态定义 + 八部件法 + 五类典型 WF 提炼 + 依赖矩阵 + workflow/ 目录规范 | ✅ v1.0 |
| 44 | `meth-014-information-assets-metadata.md` | ~470 | meth- | 信息资产全景认知 SSOT：六类文档元数据契约 + 目录体系（8模块/02_rd矩阵/07_kb_stat）+ 元系统三件套 + 可观测五源 + 数据源8类图谱 + 数据流五阶段 + 元数据速查表 + 20场景操作/审计/加固导航图 | ✅ v1.0 |
| 45 | `meth-015-token-reduction-methodology.md` | ~330 | meth- | **降 Token 方案方法论**：五类杠杆（压缩固定/保历史/减请求/短输出/渠道）+ 预算守恒定理 + 案例库（CASE-001 上下文预算失衡/CASE-002 格式检查冲突）+ 快速通道原则（fast/full 双模/多转 scripts/容忍弹性）+ 持续追加机制 | ✅ v1.0 |
| 46 | `meth-016-system-building-sop.md` | ~500 | meth- | **系统搭建 SOP 手册**：从零搭建「知识驱动型 AI 工作系统」分步操作手册——7 Phase 流水线（决策/地基/知识库/工具化/Agent化/监控治理/持续优化），每阶段含目标/步骤/输出/DoD/配套工具/常见坑；附录 A 工具映射表（SOP→工程资产 14 项）+ 附录 B DoD 检查清单 + 附录 C 踩坑实录（10 条本工程实证）| ✅ v1.0 |
| 47 | `meth-017-web-access-architecture.md` | ~790 | meth- | **Web 访问能力全景与 Skill 调用关系图谱**：四层架构（L0 工具/L1 策略/L2 专项/L3 调度/L4 消费）+ 8 类 skill 逐一剖析 + 调用关系矩阵 + 反爬应对链与稳定源清单 + 数据源分级（知乎/X/微信=中等置信）+ 访问方式查表（source-access-lookup + access_chain 8 级）+ 外部工具控制方法全景（17 工具）+ P0/P1/P2 改进路线 | ✅ v2.0 |
| 50 | `meth-020-quality-evaluation-methodology.md` | ~460 | meth- | **三源质量评估方法论**：内部交叉繁殖四表现诊断 + 外部方法论采样（RAGAS/MT-Bench/Faithfulness）+ 三源评估模型（S1 内部规则/S2 LLM 语义/S3 外部验证）+ sr-007 T5 外部验证维度 + 偏差控制六手段 + POC→重构→稳定演进 + P0/P1/P2 路线图 | ✅ v1.0 |
| 26 | `sr-001-knowledge-system-requirements.md` | 598 | sr- | 用户需求权威来源 | ✅ |
| 27 | `sr-002-system-evolution-constraint-conflicts-analysis.md` | 453 | sr- | 约束衰减分析 | ✅ |
| 28 | `sr-003-system-constraint-registry.md` | 579 | sr- | 87 条 CCLRR 约束 SSOT（v1.6 提升版：结论先行） | ✅ v1.6 |
| 29 | `sr-004-workspace-dir-req.md` | 25 | sr- | 已合并至 design-003 附录 D | 归档桩 |
| 30 | `sr-005-discover-dir-req.md` | 506 | sr- | discover 加工层需求 | ✅ |
| 31 | `sr-006-ai-task-processing-optimization.md` | 935 | sr- | 14类AI任务优化方案 | ✅ |
| 32 | `sr-007-content-quality-standards.md` | 560 | sr- | 四级→8级质量分级 + 四维评估 + 门禁 | ✅ v1.1 |
| 33 | `sr-008-system-challenges-and-practices.md` | 496 | sr- | 9 大挑战 × 36 项改进方案 | ✅ v1.0 |
| 34 | `sr-009-spec-audit-system-design.md` | 1,072 | sr- | 三层审计 + 8 专项域 + 影响评估 + 修复路线图 | ✅ v2.1 |
| 48 | `sr-010-system-attention-points.md` | ~500 | sr- | **系统关注点全景**：14 个关注面（F1-F14 资源源/格式保真/双引擎/目录/check/定时/报告/质量/配套/图谱/挑战/稳定性/分库/安全）× 现状实例/关注要点/现有应对/缺口建议 + P0/P1/P2 路线图 | ✅ v1.0 |
| 49 | `sr-011-cowagent-session-context-improvements.md` | ~360 | sr- | **CowAgent 工程改进点需求收集**：session 定义显式化 / 基于 session 的上下文优化 / 任务特征上下文大小 / 可靠性操作增强（4 方向，代码实证 + 优先级矩阵 P0/P1/P2） | ✅ v1.0 |
| 35 | `std-001-development-rules.md` | 609 | std- | 四阶段工程约束（v4.0 提升版：结论先行 + 索引/日志单轨制对齐） | ✅ v4.0 |
| 36 | `std-002-knowledge-content-format.md` | 441 | std- | 5大要素模板+机器可解析 | ✅ |
| 37 | `std-003-knowledge-operations-guide.md` | 1,105 | std- | 文件操作决策依据（§3.1 决策树已对齐实际目录 2026-08-06） | ✅ |
| 38 | `std-004-knowledge-pipeline-constraints.md` | 413 | std- | 三层流水线约束 + 19 条约束编码 | ✅ v1.1 |
| 39 | `std-005-kb-directory-registry.md` | ~210 | std- | **目录注册表 SSOT**：全库目录性质 + 归档路径判定规则 + 检测脚本 | ✅ v1.0 |
| 40 | `ar-001-sr-ar-mapping.md` | 686 | ar- | SR→AR 双向追溯 + Q/D 行 | ✅ v2.3 |
| 41 | `audit-001-constraint-compliance-audit.md` | 199 | audit- | 51%通过率的约束合规审计 | ✅ |
| 43 | `audit-002-skills-scripts-completeness-closure.md` | ~460 | audit- | Skills/Scripts 完整性与封闭性实证审计：99% 注册覆盖 + 22% 引用断裂 + 39% 路径歧义 + 确定性外壳评估 | ✅ v1.0 |

**总计**: **43** 个文件（42 活跃 + 1 归档桩 sr-004）/ ~29,620 行

---

## 按前缀统计

| 前缀 | 全称 | 数量 | 行数 |
|:----:|:-----|:----:|:----:|
| design- | Architecture Design | 10 | 9,147 |
| meth- | Methodology | 14 | 10,640 |
| sr- | System Requirement | 10² | 6,715 |
| std- | Engineering Standard | 5 | 2,679 |
| ar- | Architecture Mapping | 1 | 657 |
| audit- | Compliance Audit | 2 | 659 |

> ¹ 原注：sr- 系列含 8 个活跃文件 + 1 归档桩（sr-004）。sr-007/sr-008 为活跃文件；`_archive/` 中为历史版本 `sr-008-scripts-mining-report.md`。
> ² sr-010 为 2026-08-12 新增（sr-001~sr-010 共 9 活跃 + 1 归档桩）。
> ³ sr-011 为 2026-08-19 用户指令新增（CowAgent 改进点需求收集，例外于"不再新增 SR 条目"规则——需求收集文档，非单一需求点）。

---

## 已归档文件

| 原文件 | 行数 | 归档原因 | 去向 |
|:-------|:----:|:---------|:-----|
| `design-002-folder-optimization-plan.md` | 480 | 一次性优化报告，非持续性规范 | `_archive/` |
| `sr-008-scripts-mining-report.md` | 344 | 一次性矿脉分析报告 | `_archive/` |
| `sr-004-workspace-dir-req.md` (原版) | 373 | 内容合并至 design-003 附录 D | 保留为归档桩 |
| `sr-003-system-constraint-registry-audit.md` (旧) | 194 | 已重命名并迁出 `_archive/` → `audit-001` | 已删除 |
| `design-006-token-optimization_V3.4/V3.7` | — | 历史版本 | `_archive/` |

---

## 去重汇总

| 操作 | 影响文件 | 精简行数 |
|:-----|:---------|:--------:|
| 移出 3 份报告 → `_archive/` | spec 索引 | 1,018 |
| sr-004 内容合并 → design-003 附录 D | sr-004 (373→24), design-003 (+53) | -296 |
| std-003 §11 格式去重 → std-002 | std-003 (1,267→1,067) | 200 |
| **总计** | 4 文件变动 | ~1,000+ 行精简 |

---

## Changelog

| 日期 | 变更 |
|:-----|:------|
| **2026-08-19** | **spec/ 全面提升（第二批）**：① 6 核心文件深度提升——design-003 v2.0 / design-004 v2.0 / std-002 v2.0 / std-003 v3.0 / sr-001 v2.0 / meth-001 v2.0（结论先行 + 状态字段 + 提升说明 + 旧头部备注化「📌 备注（旧版原文头部）」保留不删除）；design-003 §5/§6 与 std-003 正文单轨制残留备注化（weekly-reports 自维护过时表述修正）；② 全部 44 个活跃文件补「结论先行（30 秒版）」头部块（design-005~014 / meth-002~020 / sr-002/005~011 / std-004/005 / ar-001 / audit-001/002 / README）——全库 53/54 文件结论先行覆盖（仅 sr-004 归档桩除外）；③ 修复 A 档头部替换产生的重复 H1（旧头部降级为备注块）。 |
| **2026-08-19** | **spec/ 全面提升（第一批）**：① design-001 v3.3 / std-001 v4.0 / sr-003 v1.6 深度提升——新增「结论先行（30 秒版）」+ 状态字段 + 提升说明，std-001 §6 对齐索引/日志单轨制（旧内容备注化保留）；② 批量格式修复：6 文件补 TOC、design-012/013/014 双分隔线、design-011 元信息、design-001/sr-003 大小写死链；③ audit-002 §6.5 编号修复；④ 全库结构审计（54 文件代码块外标题干净，1,316 条格式警告 95%+ 为检查器误报） |
| **2026-08-19** | **+meth-020-quality-evaluation-methodology.md — 三源质量评估方法论（~460行）：内部交叉繁殖四表现诊断（评估维度全内部/评估者同源/无外部采样/无外部锚点）→ 外部方法论采样（RAGAS 指标家族 + MT-Bench LLM-as-judge 三大偏差 + Faithfulness 计算原理）→ 三源评估模型（S1 内部规则 + S2 LLM 语义 + S3 外部事实验证）→ sr-007 扩展 T5 外部验证维度（T2 35%→25%）→ 外部采样机制 + LLM-as-judge 偏差控制六手段 → POC→重构→稳定演进 + DoD + P0/P1/P2 路线图** |
| **2026-08-15** | **+meth-019-file-ralph-loop-scheduling.md — 文件级 Ralph Loop 调度方法论（~330行）：现状轮次机制分析（design-014 单命令执行链路/20轮裁剪/30K截断）→ 双层架构（调度器状态机+执行器Ralph循环）→ 每次命令执行协议（STEP 0-4）→ 每文件独立上下文预算（文件间零残留+状态文件交接）→ Ralph Loop 挂载（三组件+Check映射+max_iterations=3）→ 落地（wf-05 workflow.json+状态文件schema+断点续传）+ 集成点/边界/DoD** |
| **2026-08-12** | **+sr-010-system-attention-points.md — 系统关注点全景（~500行）：14 个关注面（F1 资源源/F2 格式保真/F3 双引擎/F4 目录模板/F5 check/F6 定时调研/F7 报告/F8 质量治理/F9 配套/F10 图谱/F11 挑战/F12 稳定性/F13 分库/F14 安全）× 现状实例/关注要点/现有应对/缺口建议 + P0/P1/P2 路线图（磁盘 96%/分库/超时纪律等 P0 项）** |
| **2026-08-12** | **+meth-017-web-access-architecture.md — Web 访问能力全景与 Skill 调用关系图谱（~330行）：四层架构（L0 工具/L1 策略/L2 专项/L3 调度/L4 消费）+ 8 类 skill 逐一剖析 + 调用关系矩阵（搜索→抓取→归档三段式等）+ 反爬应对链 5 层 + 稳定源清单 + 数据源分级（知乎=中等置信）+ P0/P1/P2 改进路线（10 项）** |
| **2026-08-10** | **+meth-016-system-building-sop.md — 系统搭建 SOP 手册（~500行）：7 Phase 流水线（决策→地基→知识库→工具化→Agent化→监控治理→持续优化）+ 每阶段 目标/步骤/输出/DoD/配套工具/常见坑 + 附录 A 工具映射表（14 项）+ 附录 B DoD 检查清单 + 附录 C 踩坑实录（10 条）** |
| **2026-08-07** | **+meth-015-token-reduction-methodology.md — 降 Token 方案方法论（~330行）：五类杠杆 + 预算守恒定理 + 案例库（CASE-001 上下文预算失衡/CASE-002 格式检查规则冲突）+ 快速通道原则（fast/full 双模/多转 scripts/容忍弹性）+ 持续追加机制（CASE 模板）** |
| **2026-08-06** | **+meth-014-information-assets-metadata.md — 信息资产全景认知 SSOT（~470行）：六类文档元数据契约 + 目录体系（8模块/02_rd矩阵/07_kb_stat）+ 元系统三件套 + 可观测五源 + 数据源8类图谱/fallback链 + 数据流五阶段 + 元数据速查表 + 20场景操作/审计/加固导航图** |
| **2026-08-06** | **+meth-013-workflow-system.md — Workflow 体系方法论（~460行）：静态/动态定义 + 八部件法 + 五类典型 WF（discover质量/新文件创建/质量检查/报告体系/统计分析）+ 依赖矩阵 + workflow/ 目录规范（static+dynamic+lib）；workflow/ 目录初始化 + wf-03/wf-04 workflow.json 示范** |
| **2026-08-06** | **+std-005-kb-directory-registry.md — 目录注册表 SSOT（~210行）：全库目录性质 + 归档路径判定 R1-R7 + kb-dir-registry.py 脚本(--tree/--suggest/--diff)；std-003 §3.1 决策树对齐实际目录；design-009 重号修复（scheduled-tasks → design-011）；+meth-012 登记；索引全量对齐** |
| **2026-08-06** | **+meth-012-kb-observability-methodology.md — 知识库可观测性方法论（402行）：目标→指标总表 + 六大子系统实测 + 三层汇总闭环 + 07_kb_stat 专项中心** |
| **2026-08-06** | **+meth-011-file-quality-three-layer.md — 文件质量三层模型（316行）：L1 产出快检 + L2 专业补齐 + L3 专项深修 + 修订建议 R1-R7** |
| **2026-08-03** | **+design-009-kb-index-log-dual-track.md — 索引/日志双轨制设计（343行）：废弃 281 个分布式 index/log → 全局 index.md + log.md；保留 01_survey/weekly-reports** |
| **2026-07-28** | **+meth-005 v1.2→v1.3: E层演进困境 困境16→20项, 矩阵5层 (1,074→1,121行)** |
| **2026-07-28** | **+meth-003-knowledge-information-methodology.md — 六域模型·目录边界·分布式/集中式·源维护·AI扩写·元数据体系 (1,037行)** |
| **2026-07-28** | **P1～P2 批量修复: CCLRR 87 统一、Skills 125 统一、knowledge 2,549 统一、std-001 编号修复、ar-001 去重、meth-002 9段式、sr-004 引用修正、头部版本对齐** |
| **2026-07-29** | **+meth-007-ai-detail-precision-control.md — AI 精确细节控制方法论 (577行)** |
| **2026-07-29** | **+meth-008-doc-vs-code-systems.md — 文档系统 vs 代码系统：10维全对比 (938行)** |
| **2026-07-28** | **+meth-006-kb-construction-patterns.md — 36种设计模式(6类)+8种AI使用模式 (~1,160行)** |
| **2026-07-27** | **+meth-002-skills-scripts-audit-method.md — Skills/Scripts 深度审计模板** |
| **2026-07-27** | **+sr-009-spec-audit-system-design.md — 三层审计 + 8 专项审计域 (v2, ~1,072行)** |
| **2026-07-27** | **B1-B7 溯源断裂修复: 10 文件 × 98 章节添加章节级 AR 溯源标注** |
| **2026-07-27** | **+sr-008-system-challenges-and-practices.md — 9 大挑战 × 36 项改进要点** |
| 2026-07-27 | 初始创建 |
| 2026-07-27 | +sr-007-content-quality-standards.md |
| 2026-07-27 | +sr-008-scripts-mining-report.md → 后移入 _archive/ |
| 2026-07-27 | +std-004-knowledge-pipeline-constraints.md |
| **2026-07-27** | **去重优化**: 3 份报告移入 `_archive/`；sr-004 合并至 design-003；总精简 ~1,000 行 |
