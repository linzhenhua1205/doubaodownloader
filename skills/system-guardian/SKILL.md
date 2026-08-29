---
name: system-guardian
description: 系统守护 — 统一入口，对工程基础设施执行三重守护检查。task integrity(进程隔离/定时任务一致性) + skill registration(注册完整性/游离检测) + config consistency(config vs 实际目录一致性)。Use when: (1) 用户要求检查任务/定时任务状态 (2) 用户询问Skills注册是否完整 (3) 怀疑有游离Skill (4) 需要做系统审计/健康度检查 (5) 用户说"检查一下系统状态"/"系统守护"/"守护检查"/"健康检查"。Do NOT use: 单次创建Skill(用skill-creator) 单次排查具体Bug(用fault-diagnosis) 知识库健康检查(用knowledge-health-check)。
category: system
user_invocable: true
requires:
  bins: [python3]
---

# 🛡️ System Guardian — 工程系统统一守护

> **核心理念**: 工程系统有 3 个最容易"默默变坏"的维度——定时任务、Skills 注册、Config 同步。本 Skill 提供统一入口做三合一检查，避免每次需要手动分别排查。

---

## 📑 目录

- [1. 快速使用](#1-快速使用)
- [2. 三重守护](#2-三重守护)
  - [2.1 守护 A — Task Integrity](#21-守护-a--task-integrity)
  - [2.2 守护 B — Skills Registration](#22-守护-b--skills-registration)
  - [2.3 守护 C — Config Consistency](#23-守护-c--config-consistency)
- [3. 守护报告格式](#3-守护报告格式)
- [4. 配套脚本](#4-配套脚本)
- [5. 安全红线](#5-安全红线)
- [Changelog](#changelog)

---

## 1. 快速使用

**全量检查（推荐）**:
```bash
python3 scripts/system-guardian-runner.py
```

**单项检查**:
```bash
python3 scripts/check/check-tasks-integrity.py           # 仅 task
python3 scripts/check/check-skills-registration.py       # 仅 skill 注册
```

**AI 自动触发**: 用户说"检查系统"/"守护检查"/"健康检查" → 触发全量检查。

---

## 2. 三重守护

### 2.1 守护 A — Task Integrity

> 核心脚本: `scripts/check/check-tasks-integrity.py`

**检查项**:

| 检查 | 内容 | 通过标准 |
|:-----|:------|:---------|
| A1 进程隔离 | `tasks.json` 中的 `process` 字段是否有重叠? | 无两个任务共用同一 process+path |
| A2 Channel 一致性 | 所有 task 的 `channel_type` 是否与 `RULE.md` 定义一致? | 全部对齐 |
| A3 AI Task 约束 | `ai_task` 字段是否包含明确的质量/约束指令? | 每个定时任务有清晰约束 |
| A4 Session 中断风险 | 是否有 task 的 message 为空(仅 ai_task)? | 非空或注明"仅 AI" |

**自动修复**: 仅修复可安全自动修复的项（如 channel_type 格式），进程隔离违背必须人工确认。

### 2.2 守护 B — Skills Registration

> 核心脚本: `scripts/check/check-skills-registration.py`

**检查项**:

| 检查 | 内容 | 通过标准 |
|:-----|:------|:---------|
| B1 注册完整性 | `skills/` 下所有含 `SKILL.md` 的目录是否在 `skills_config.json` 中？ | 0 游离 |
| B2 Config 残留 | `skills_config.json` 中的条目是否都有对应目录？ | 0 死引用 |
| B3 Description 同步 | Config 与 SKILL.md 的 `description` 是否一致？ | 完全一致 |
| B4 废弃标记 | `skills_archive/` 或 `tmp/bak/` 中的 Skill 是否已从 config 移除？ | 无废弃引用 |

**修复**:
- 游离 Skill → 自动注册（提示用户）
- Config 残留 → 自动移除
- Description 偏差 → 打印差异，人工确认后同步

### 2.3 守护 C — Config Consistency

| 检查 | 内容 | 通过标准 |
|:-----|:------|:---------|
| C1 Git 工作漂移 | 当前工作区是否有关键文件未跟踪/已修改？ | 无意外变更 |
| C2 Scripts 映射 | `scripts/skills-scripts-mapping.md` 映射表是否与 `scripts/` 目录一致？ | 映射表覆盖所有脚本 |
| C3 废弃文件 | `tmp/bak/` 中是否有 >30天 的残余可清理？ | 有则提示清理 |

---

## 3. 守护报告格式

每次全量检查输出统一格式报告：

```markdown
# 🛡️ 系统守护报告 YYYY-MM-DD HH:MM

## 守护 A — Task Integrity    [✅ 通过 / ⚠️ 警告 / 🔴 失败]
- A1 进程隔离: ✅ 无冲突
- A2 Channel:  ⚠️ task-X channel_type 为 feishu 但实际输出为空
- A3 AI Task:  ✅ 全部对齐

## 守护 B — Skills Registration [✅ 通过 / ⚠️ 警告 / 🔴 失败]
- 注册: 94/94 (0 游离)
- Config: 94/94 (0 死引用)
- Description: 1 处偏差

## 守护 C — Config Consistency [✅ 通过 / ⚠️ 警告]
- Git: ✅ 干净
- 映射: ⚠️ 3 个脚本未在映射表中
- 废弃: ✅ 无

## 修复建议
- ⚠️ [P1] task-X 进程有潜在冲突 → 人工确认
- ⚠️ [P2] 3 个脚本映射缺失 → 更新映射表
```

---

## 4. 配套脚本

| 脚本 | 位置 | 说明 |
|:-----|:-----|:------|
| 守护运行器 | `scripts/system-guardian-runner.py` | 一键运行三重守护 |
| Task Integrity | `scripts/check/check-tasks-integrity.py` | 定时任务一致性（已有） |
| Skills Registration | `scripts/check/check-skills-registration.py` | 注册完整性审计 |

---

## 5. 安全红线

- **B1 注册修复要求确认**: 新发现的游离 Skill 注册前，必须人工确认是否真的是"游离"而非"废弃"
- **A1 进程隔离不自动修复**: 进程冲突必须人工评估后再处理
- **不删除文件**: 守护 C 检测到的废弃只做提示，不做自动清理

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-07-30 | v1.0 | 初始创建。覆盖三重守护（Task Integrity + Skills Registration + Config Consistency）。统一 F5/F9 需求为单一入口。 |
