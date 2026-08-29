---
name: session-keeper
description: Universal session persistence skill for managing multi-session work progress. Use when: (1) user wants to save task progress for later continuation, (2) user wants to resume a previous task, (3) task spans multiple sessions, (4) user wants to track task status across sessions, (5) 会话持久化、任务保存、进度恢复、跨会话跟踪. Do NOT use for: single-session tasks, trivial changes.
metadata:
  requires:
    bins: ["python3"]
  emoji: 💾
---

# 会话持久化技能 (Session Keeper)

## 概述

本技能用于**管理跨会话工作进度**。基于 ECC-main 的 ck/commands 模板，提供通用的会话持久化能力，支持任务的保存、恢复和状态跟踪。

**核心价值**: 让复杂任务不再因会话中断而丢失进度。

---

## 持久化框架

### 会话状态模型

```
Session State
├── Task Info
│   ├── task_id (UUID)
│   ├── task_name
│   ├── status (pending/in_progress/completed/canceled)
│   ├── created_at
│   ├── updated_at
│   └── completed_at
├── Context
│   ├── current_file
│   ├── current_step
│   ├── notes
│   └── artifacts
├── Progress
│   ├── total_steps
│   ├── completed_steps
│   ├── progress_percent
│   └── estimated_remaining
└── History
    ├── actions[]
    ├── timestamps[]
    └── outcomes[]
```

### 持久化格式

会话状态以 JSON 格式保存：

```json
{
  "task_id": "uuid-xxx",
  "task_name": "分析 PCIe Gen5 信号完整性",
  "status": "in_progress",
  "created_at": "2026-06-27T10:00:00Z",
  "updated_at": "2026-06-27T14:30:00Z",
  "context": {
    "current_file": "knowledge/hardware/signal_integrity/pcie_gen5_analysis.md",
    "current_step": "数据分析",
    "notes": "眼图分析完成，正在进行抖动分解",
    "artifacts": ["si_report.md", "eye_diagram.png"]
  },
  "progress": {
    "total_steps": 5,
    "completed_steps": 3,
    "progress_percent": 60,
    "estimated_remaining": "1小时"
  },
  "history": [
    {
      "action": "开始会话",
      "timestamp": "2026-06-27T10:00:00Z",
      "outcome": "success"
    }
  ]
}
```

---

## 命令接口

### `/dtw:init` — 初始化会话

```bash
python3 <base_dir>/scripts/tools/session-manager.py init dtw --context skill=deep-tech-writer
```

初始化特定技能的会话，生成任务 ID。

**输出**:
```
Session initialized:
- Task ID: abc123-def456
- Skill: deep-tech-writer
- Status: in_progress
- Created: 2026-06-27 10:00:00
```

### `/dtw:save` — 保存会话进度

```bash
python3 <base_dir>/scripts/tools/session-manager.py save dtw --context current-file=knowledge/hardware/signal_integrity/pcie_gen5_analysis.md current-step="数据分析" notes="眼图分析完成，正在进行抖动分解" --note "completed 3/5"
```

保存当前会话进度。

### `/dtw:resume` — 恢复会话

```bash
python3 <base_dir>/scripts/tools/session-manager.py resume dtw
```

恢复之前保存的会话。

**输出**:
```
Session resumed:
- Task ID: abc123-def456
- Task: 分析 PCIe Gen5 信号完整性
- Status: in_progress
- Current Step: 数据分析
- Progress: 3/5 (60%)
- Last Updated: 2026-06-27 14:30:00

Notes:
眼图分析完成，正在进行抖动分解

Artifacts:
- si_report.md
- eye_diagram.png

Continue from: knowledge/hardware/signal_integrity/pcie_gen5_analysis.md
```

### `/dtw:status` — 查询会话状态

```bash
python3 <base_dir>/scripts/tools/session-manager.py status dtw
```

查询特定会话的状态。

### `/dtw:list` — 列出所有会话

```bash
python3 <base_dir>/scripts/tools/session-manager.py list
```

列出所有保存的会话。

**输出**:
```
Active Sessions:
┌──────────────────┬───────────────────────────────┬─────────────┬──────────┐
│ Task ID          │ Task Name                     │ Status      │ Progress │
├──────────────────┼───────────────────────────────┼─────────────┼──────────┤
│ abc123-def456    │ 分析 PCIe Gen5 信号完整性     │ in_progress │ 60%      │
│ ghi789-jkl012    │ RDMA 性能优化                 │ pending     │ 0%       │
│ mno345-pqr678    │ 缓存一致性协议分析             │ completed   │ 100%     │
└──────────────────┴───────────────────────────────┴─────────────┴──────────┘
```

### `/dtw:cancel` — 取消会话

```bash
python3 <base_dir>/scripts/tools/session-manager.py cancel dtw
```

取消会话并标记为 canceled。

---

## 支持的技能

| 技能 | 命令前缀 | 会话目录 |
|:-----|:---------|:---------|
| **deep-tech-writer** | `/dtw:` | `skills/deep-tech-writer/sessions/` |
| **doc-reviewer** | `/dr:` | `skills/doc-reviewer/sessions/` |
| **method-analysis** | `/ma:` | `skills/method-analysis/sessions/` |
| **tech-planner** | `/tech-plan:` | `skills/tech-planner/sessions/` |
| **si-analyzer** | `/si:` | `skills/si-analyzer/sessions/` |
| **rdma-analyzer** | `/rdma:` | `skills/rdma-analyzer/sessions/` |
| **通用** | `/session:` | `skills/session-keeper/sessions/` |

---

## 会话管理工作流

```
用户: "开始分析 PCIe 信号完整性"
→ 系统: 自动调用 `/dtw:init` 初始化会话

用户: "保存进度"
→ 系统: 调用 `/dtw:save` 保存当前状态

[会话中断]

用户: "继续分析 PCIe 信号完整性"
→ 系统: 调用 `/dtw:resume` 恢复会话

用户: "查看进度"
→ 系统: 调用 `/dtw:status` 显示状态

用户: "完成分析"
→ 系统: 调用 `/dtw:save` 更新状态为 completed
```

---

## 质量评分体系

| # | 评分维度 | 检查项 | 权重 |
|:-:|:---------|:-------|:-----|
| 1 | **状态准确性** | 保存的状态是否准确反映实际进度 | 30% |
| 2 | **恢复完整性** | 恢复后是否能继续之前的工作 | 25% |
| 3 | **上下文保留** | 是否保留足够的上下文信息 | 20% |
| 4 | **操作便捷性** | 命令是否简洁易用 | 15% |
| 5 | **文档规范** | 是否符合 changelog/TOC/来源标注规则 | 10% |

**评分等级**：
- **优（85+）**: 可直接使用
- **良（70-84）**: 可使用，建议小修
- **需改进（50-69）**: 需重大修改
- **不合格（<50）**: 需重写