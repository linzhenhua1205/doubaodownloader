# workflow/ — Workflow 注册表

> **方法论**: [`../spec/meth-013-workflow-system.md`](../spec/meth-013-workflow-system.md)（静态/动态定义 + 八部件法 + 依赖矩阵）
> **原则**: 确定的骨架归代码，不确定的判断归模型；静态优先（省 token），动态只在复杂新任务。
> **强依赖**: spec 规范（行为约束）+ skills（agent 能力）+ scripts（确定性执行）→ 作用于 knowledge/。

---

## 📁 目录结构

```text
workflow/
├── README.md          # 本文件：注册表
├── static/            # 静态 workflow（固化，直接调用 scripts/skills）
│   ├── wf-03-quality-check/   # ✅ 已定义（workflow.json）
│   ├── wf-04-weekly-report/   # ✅ 已定义（workflow.json）
│   └── ...                    # P1+ 待脚本化
├── dynamic/           # 动态 workflow（任务生成脚本）
│   ├── template.md            # 生成模板（八部件齐全）
│   └── <task-id>/             # 按任务生成（执行后归档/删除）
└── lib/               # 共享运行时辅助（phase/log/assert）
```

## 📋 静态 Workflow 清单

| ID | 业务 | 状态 | 定义 | 对应 meth-013 §5 |
|:---|:-----|:----:|:-----|:-----------------|
| wf-01-discover-quality | discover 文件质量提升 | 🟡 待脚本化 | — | WF-01 |
| wf-02-file-creation | 新文件创建（按类型） | 🟡 待脚本化 | — | WF-02 |
| wf-03-quality-check | 质量检查（三层门） | ✅ 已定义 | [workflow.json](static/wf-03-quality-check/workflow.json) | WF-03 |
| wf-04-weekly-report | 日报周报月报体系 | ✅ 已定义 | [workflow.json](static/wf-04-weekly-report/workflow.json) | WF-04 |
| wf-05-kb-statistics | 知识库统计分析 | 🟡 待脚本化 | — | WF-05 |

> 🟡 待脚本化 = 方法论已提炼（meth-013 §5），run.py 执行脚本待建（P1-P2）。

## ▶️ 运行方式

```bash
# 静态 workflow：读 workflow.json → 按 phases 依次执行（脚本化后）
python3 workflow/static/<wf-id>/run.py [--phase scan] [--resume]

# 动态 workflow：复杂新任务 → 按 dynamic/template.md 生成脚本 → 执行
# 手动触发：直接在对话中说明使用哪个 workflow（AI 按 meth-013 执行）
```

## 🔗 与 scheduler 映射

| scheduler 任务 | 对应 workflow |
|:---------------|:--------------|
| Skills-Scripts 周质量检测（周日 7:50） | wf-03-quality-check（L1/L2） |
| 知识库周报（周日 7:00/21:45） | wf-04-weekly-report |
| 知识库月度报告（月末 23:20） | wf-04-weekly-report（monthly 变体） |
| knowledge-special-reports（周日 22:00） | wf-05-kb-statistics |

## Changelog

| 日期 | 变更 |
|:-----|:------|
| 2026-08-06 | v1.0 初始：目录骨架 + 注册表 + wf-03/wf-04 定义（对应 meth-013） |
