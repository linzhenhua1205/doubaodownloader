# Cursor IDE Code Review 工程化实践

> **概要**: Cursor IDE代码审查工程化实践，提供四步落地SOP与第三方工具联动方案
>
> **关键词**: Cursor · 代码审查 · IDE闭环 · SOP · 跨语言审查

---

## 📑 目录

- [一、方案核心理念](#一方案核心理念)
  - [关键区别](#关键区别)
- [二、四步极速落地 SOP](#二四步极速落地-sop)
  - [步骤一：数据挖掘](#步骤一数据挖掘)
  - [步骤二：规则固化](#步骤二规则固化)
- [审查流程（7步）](#审查流程7步)
- [检查模式](#检查模式)
- [提交信息格式](#提交信息格式)
  - [步骤三：无缝审查](#步骤三无缝审查)
  - [步骤四：数据闭环](#步骤四数据闭环)
- [三、与第三方工具联动](#三与第三方工具联动)
  - [Cursor + CodeReview Agent](#cursor-codereview-agent)
  - [Cursor + WorkBuddy](#cursor-workbuddy)
- [四、落地常见问题](#四落地常见问题)
- [五、跨语言审查能力](#五跨语言审查能力)
- [六、参考资料](#六参考资料)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

---

## 一、方案核心理念

**AI 辅助，人为主导** — 不做"AI 背锅"审查，最终质量责任始终由 Reviewers 承担。

### 关键区别

| 维度 | 旧范式（云端黑盒） | ✅ 新范式（IDE 闭环） |
|:-----|:-----------------|:-------------------|
| 触发时机 | PR 提交后 → AI 审查 → 评论回写 | IDE 内编码 → **AI+人共同审查** → 提交 PR |
| 反馈位置 | GitHub/GitLab 网页 | 编辑器内 |
| 审查责任 | 用户可能盲目信任 AI | 人工确认后再提交 |
| 上下文 | 云端，理解有限 | 本地 Codebase，跨文件 |
| 流程打断 | 需要切换网页 IDE | **零切换** |

---

## 二、四步极速落地 SOP

### 步骤一：数据挖掘

从团队历史 PR 中提取真实评审意见，构建问题库。

```bash
# 脚本：拉取 GitHub 近 1 年 PR 评论
gh pr list --limit 500 --state merged --json number,title,comments |
  jq '.[] | select(.comments | length > 0)' > prs_with_reviews.json

# 提取评论中的常见问题模式
cat prs_with_reviews.json | jq -r '.comments[].body' |
  grep -iE "bug|漏洞|性能|安全|规范|命名|缺少" |
  sort | uniq -c | sort -rn | head -30 > review-log.md
```

**产出**: `review-log.md` — 团队高频问题排行榜，作为 AI 规则优化的数据基础。

### 步骤二：规则固化

编写 Cursor Custom Skill，内置 7 步审查流水线。

**Skill 文件结构**（`.cursor/rules/rule-code-review.mdc`）：

```markdown
---
description: 代码审查：自动审查代码变更，输出结构化审查报告
globs: **/*.{py,js,ts,jsx,tsx,go,java,rs,c,cpp,h,hpp}
---

# Code Review Agent Instructions

你是一个严格、务实的 Code Reviewer。

## 审查流程（7步）

1. **获取代码变更** — 读取当前 Git Diff（staged / unstaged / 特定分支对比）
2. **变更摘要** — 输出文件变更概览（新增/修改/删除行数）
3. **影响评估** — 评估变更影响范围（该函数被谁调用？修改了哪些接口？是否涉及 DB 变更？）
4. **架构评估** — RESTful/模块化/依赖方向是否符合架构约定
5. **逐文件审查** — 按以下维度逐文件检查：
   - 安全漏洞（SQL注入/XSS/硬编码密钥/越权）
   - 性能隐患（N+1查询/资源未释放/同步阻塞）
   - 代码规范（命名/注释/死代码/魔法数字）
   - 业务逻辑（边界条件/竞态条件/异常处理）
6. **格式化输出** — 按严重/一般/建议三级输出，精确到行号
7. **AI 自动修改** — 对"建议"级别问题，确认后可自动修复
```

**Git 提交规则**（`.cursor/rules/rule-git-commit.mdc`）：

```markdown
---
description: 提交前代码审查，自动检查代码质量并格式化 Commit 信息
globs: *
---

# Git Commit Rules

## 检查模式
- 使用 `git diff --cached` 获取暂存区变更
- 按严重/警告/提醒三级输出
- 严重问题：不得提交（建议修复后重新提交）
- 警告问题：确认后可提交
- 提醒问题：仅供参考

## 提交信息格式
type(scope): subject

body（解释为什么做，而非做了什么）

footer（关联 Issue、Breaking Change 标记）
```

### 步骤三：无缝审查

对接 MCP 能力，编辑器内一键审查。

**常用操作**：

| 操作 | 触发方式 | 效果 |
|:-----|:---------|:------|
| 审查当前变更 | Cmd+. → "Review current changes" | 输出 Diff 审查报告 |
| 审查指定文件 | Cmd+K → "Review this file" | 单文件逐行审查 |
| 审查整个 PR | MCP 连接 GitHub → "Review PR #xxx" | 远程 PR 审查（不自动发评论） |
| 提交前审查 | Git 钩子触发 `.cursor/rules/rule-git-commit.mdc` | 提交前自动校验 |

### 步骤四：数据闭环

每月复盘人工评论，反哺优化 Skill 规则。

```mermaid
flowchart LR
    A[真实PR评论] --> B[提炼高频问题]
    B --> C[更新Skill规则]
    C --> D[AIR审查]
    D --> E[对比人工评论]
    E --> B
```

---

## 三、与第三方工具联动

### Cursor + CodeReview Agent

```bash
# 在 Cursor Terminal 中直接调用
codereview-agent review --diff --path . --format json
# 输出 JSON 结构供 Cursor 解析和展示
```

### Cursor + WorkBuddy

Cursor 内完成本地审查，WorkBuddy 处理平台级 WebHook 自动评审（双轨并行策略）。

---

## 四、落地常见问题

| 问题 | 解决方案 |
|:-----|:---------|
| AI 误报率高 | 调整 Skill 规则粒度，减少过于宽泛的检查项；降低置信度阈值 |
| 审查响应慢 | 使用轻量模型做初审（如 GPT-4o mini），复杂问题调高精度模型 |
| 团队不接受 | 从"纯建议"模式开始，让团队体验价值后再逐步收紧 |
| 跨文件理解弱 | 善用 Cursor Codebase 索引，在 Prompt 中指明需要检索的范围 |
| 规则更新不及时 | 建立月度复盘机制，人工评论中有规律的新问题及时加入规则 |

---

## 五、跨语言审查能力

Cursor Skills 支持多语言 Code Review 规则，覆盖以下语言：

| 语言 | 专项检查要点 |
|:-----|:------------|
| **Python** | 可变默认参数、with 资源管理、野 except、import 层级 |
| **Go** | goroutine 泄漏、defer 陷阱、context 传递 |
| **Java** | NullPointer、线程安全、equals/hashCode |
| **JS/TS** | 类型安全、async 异常处理、闭包内存泄漏 |
| **C/C++** | 内存管理、缓冲区溢出、RAII |

> 每门语言的详细检查项 → [代码审查检查清单](2026-06-29-codereview-checklist.md)

---

## 六、参考资料

- `import/doubao/AI_Code_Review最佳实践.md` — 486 行完整方案
- `import/md/本地AI_CodeReview最佳实践_0607150652.md` — 1 年落地经验
- `import/md/AI时代CodeReview左移实战_0606215534.md` — Cursor 规则模板
- [AI CR 方案选型](2026-06-29-ai-codereview-landscape.md) — 三路径对比
- [GitLab WebHook 集成](2026-06-29-gitlab-webhook-integration.md) — 平台级方案

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- [代码审查检查清单](2026-06-29-codereview-checklist.md) — 关联
- [AI CR 方案选型](2026-06-29-ai-codereview-landscape.md) — 关联
- [GitLab WebHook 集成](2026-06-29-gitlab-webhook-integration.md) — 关联

### 外部资料引用

- 来源: import/doubao/AI_Code_Review最佳实践.md`(486行PPT)、`import/md/本地AI_CodeReview最佳实践_0607150652.md`(445行)、`import/md/AI时代CodeReview左移实战_*.md`、`import/doubao/AI_Code_Review_最佳工作流实践.md` (617行)

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
