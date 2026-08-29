---
name: spec-consistency-checker
description: Spec一致性检测器。验证 spec/ 文档体系（AR→Design→Skills/Scripts）的6层层间一致性。Use when: (1) user asks to check spec consistency/一致性检测, (2) user mentions AR mapping/Design trace/Constraint source/Pipeline boundary/Cross-layer refs, (3) running periodic spec audit. Detects layer-level inconsistencies and generates reports.
metadata:
  version: "1.1"
  updated: 2026-07-27
  maintainer: auto
  emoji: 🧩
---

# Spec 一致性检测器 (spec-consistency-checker)

> **版本**: v1.1 | **更新**: 2026-07-27 | **维护**: 自动
>
> **定位**: 验证 spec/ 文档体系（ar→design→skills/scripts）的层间一致性，生成检测报告。
>
> **文档角色**: sr-xxx 为历史参考（记录原始需求），ar-001 为活跃需求文档（当前需求锚点），检测聚焦活跃层 ar/design/std 的内部一致性与上下游追溯。

---

## 描述

对 spec/ 下的文档体系做系统性一致性检测，覆盖 6 个层级：

```
Level 1: AR 映射   ar-001 内部一致性       (check-sr-ar-trace.py)
         (§2↔§3↔§4 三方对齐)
Level 2: AR→Design 回溯验证               (check-ar-design-trace.py)
Level 3: Design→Impl 实现验证              (check-design-impl-trace.py)
Level 4: Constraint Source 来源验证         (check-constraint-source.py)
Level 5: Pipeline Boundary 边界验证         (check-pipeline-boundary.py)
Level 6: Cross-Layer Refs 跨层引用验证      (check-cross-layer-refs.py)
```

每个层级可独立运行，也可全链路一次性执行。

## 触发条件

当用户提到以下任意关键词时触发（优先判断，不需再匹配其他技能）：

- "spec 一致性" / "spec consistency"
- "文档一致性检测" / "层间一致性"
- "检测报告"（上下文中有 spec/ 相关）
- "一致性检查" + "spec" / "需求" / "设计"
- "检查依赖链" / "sr到design" / "sr到脚本"
- 任何关于 "spec/ 下的文档是否一致" 的询问

## 输入

- 无参数：默认运行全部 6 个层级
- 可选参数：指定层级如 "只跑 Level 1 和 Level 3"

## 工作流

### Step 1：确认检测范围

询问用户要检测的范围（全量/指定层级），或直接运行全量。

### Step 2：运行检测脚本

```bash
# 全量运行
python3 scripts/tools/gen-spec-consistency-report.py

# 指定层级
python3 scripts/tools/gen-spec-consistency-report.py --level 1,3,5

# 仅输出到终端
python3 scripts/tools/gen-spec-consistency-report.py --stdout
```

### Step 3：汇报结果

- 先给综合摘要（通过/失败/错误数/警告数）
- 再逐层展示具体问题
- 对 ERROR 项给出修复建议
- 将报告路径告知用户

## 输出

- 检测报告自动写入 `knowledge/weekly-reports/07_kb_stat/YYYY-MM-DD-spec-consistency-report.md`
- 产物用 `kb-log-append.py` 追加摘要到全局 `knowledge/log.md`（2026-08-19 起 07_kb_stat 不再维护独立 index.md）
- 可在对话中直接展示关键发现

## 检查点速查表

| 层级 | 检查内容 | 脚本 | 关键检测项 |
|:----:|:---------|:-----|:-----------|
| L1 | AR 内部一致性 | check-sr-ar-trace.py | §2↔§3↔§4 三方对齐、轮空/孤儿、状态漂移 |
| L2 | AR→Design | check-ar-design-trace.py | 路径注册、design 文件存在性、目录可达 |
| L3 | Design→Impl | check-design-impl-trace.py | skill/script 存在性、mapping 路径、引用精度 |
| L4 | 约束来源 | check-constraint-source.py | 源文件存在、约束可追溯、类别覆盖 |
| L5 | 边界 | check-pipeline-boundary.py | 跨层污染、越级、migration gate |
| L6 | 跨层引用 | check-cross-layer-refs.py | 链接可达、前置阅读、design↔std 互引 |

## 参考文件

### 内部引用

- [ar-001-sr-ar-mapping.md](../../spec/ar-001-sr-ar-mapping.md) — SR→AR 映射表
- [sr-001-knowledge-system-requirements.md](../../spec/sr-001-knowledge-system-requirements.md) — 需求规格
- [sr-003-system-constraint-registry.md](../../spec/sr-003-system-constraint-registry.md) — 约束注册表
- [std-004-knowledge-pipeline-constraints.md](../../spec/std-004-knowledge-pipeline-constraints.md) — 流水线约束
- [design-007-skills-scripts-design.md](../../spec/design-007-skills-scripts-design.md) — Skills/Scripts 设计

### 关联脚本

- `scripts/check/check-sr-ar-trace.py` — Level 1
- `scripts/check/check-ar-design-trace.py` — Level 2
- `scripts/check/check-design-impl-trace.py` — Level 3
- `scripts/check/check-constraint-source.py` — Level 4
- `scripts/check/check-pipeline-boundary.py` — Level 5
- `scripts/check/check-cross-layer-refs.py` — Level 6
- `scripts/tools/gen-spec-consistency-report.py` — 编排器

## Changelog

| 日期 | 版本 | 变更说明 |
|:-----|:-----|:---------|
| 2026-07-27 | v1.0 | 创建 |
