# 动态 Workflow 生成模板

> **方法论**: [`../../spec/meth-013-workflow-system.md`](../../spec/meth-013-workflow-system.md) §7
> **用途**: 复杂/新任务 → 强模型按此模板现场生成执行脚本（存 `workflow/dynamic/<task-id>/`）→ 执行 → 归档/删除。
> **原则**: 生成的脚本是普通代码——能改、能存、能重跑；验收不过不静默。

---

## 生成 Prompt 骨架

```text
【任务】<任务描述>
【产出】<交付物 + 落盘位置（按 std-005 判定）>
【验收】<可检查的标准：格式/链接/数据/事实，引用具体 check 脚本>

--- 生成要求（八部件齐全，缺一不可）---
1. Trigger: 手动 / 事件
2. Planner: 拆解为 3-7 个 phase（标注可并行 phase）
3. State: 中间结果放 workflow/.state/<task-id>/；报告放目标目录
4. Workers: 标注每 phase 是 agent()（带验收标准）还是纯脚本
5. Evaluator: 每 phase 过关条件（引用 check 脚本或明确规则）
6. Loop: 最多回炉 N 次；失败降级策略（记录 vs 告警）
7. Stop/Resume: phase 级断点，重跑跳过已完成 phase
8. Repeatability: 输出差异记录（日期戳 + 增量）

--- 约束（必须遵守）---
- 只调用 meth-013 §6 依赖矩阵中已有的 scripts/skills；能力缺口 → 记录到报告，不硬造
- 归档路径按 spec/std-005（R1-R7）；创建后三同步 + git-auto-commit 提交
- 可观测性：每 phase 一行日志（phase 名 + 结果摘要）
- 质量门：agent() 内部验收 + assert() 驱动分支，验收不过不进下一 phase
```

## 八部件检查清单（生成后自检）

| # | 部件 | 检查项 | 通过标准 |
|:-:|:-----|:-------|:---------|
| 1 | Trigger | 触发方式明确 | 手动/事件写明 |
| 2 | Planner | 3-7 phase，边界清晰 | 每 phase 有输入输出 |
| 3 | State | 中间结果落盘位置 | workflow/.state/<task-id>/ |
| 4 | Workers | 每 phase worker 类型标注 | agent 带验收，脚本带路径 |
| 5 | Evaluator | 过关条件可执行 | 引用真实 check 脚本 |
| 6 | Loop | 回炉次数 + 失败策略 | ≤3 次，不静默 |
| 7 | Stop/Resume | 断点恢复 | phase 级 progress.json |
| 8 | Repeatability | 差异记录 | 日期戳 + 增量对比 |

## 执行后处理

- ✅ 成功 → 脚本归档 `workflow/dynamic/_archive/<task-id>/`（附结果摘要）
- ⚠️ 部分成功 → 保留脚本 + 失败清单，供二次执行
- ❌ 失败（验收标准本身不清）→ 删除脚本，回到对话模式（本次不该写 workflow）

## Changelog

| 日期 | 变更 |
|:-----|:------|
| 2026-08-06 | v1.0 初始模板 |
