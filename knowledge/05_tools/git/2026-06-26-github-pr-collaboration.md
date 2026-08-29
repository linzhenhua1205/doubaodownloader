# GitHub PR 代码多人协作

> **概要**: GitHub PR多人协作技巧，详解Reviewer直接Push到贡献者分支的方案
>
> **关键词**: GitHub PR · 代码协作 · 代码审查 · 分支Push · Reviewer

---

## 📑 目录

- [问题场景](#问题场景)
- [解决方案：直接 Push 到贡献者分支](#解决方案直接-push-到贡献者分支)
  - [第一步：拉到本地](#第一步拉到本地)
  - [第二步：修改代码](#第二步修改代码)
  - [第三步：Push 回对方分支](#第三步push-回对方分支)
  - [效果](#效果)
- [注意事项](#注意事项)
- [关联工具与概念](#关联工具与概念)
- [适用场景](#适用场景)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

---

## 问题场景

Code Review 时，如果 Reviewer 想直接帮助 PR 贡献者**修改一些小问题**，常规做法是：

1. Fork 同样的仓库
2. 基于对方的修改分支创建独立分支
3. 提交 PR 到对方仓库
4. 对方合并后原 PR 自动更新

流程**繁琐**，沟通成本高。有没有更高效的方式？

---

## 解决方案：直接 Push 到贡献者分支

GitHub 允许 Reviewer（有仓库写权限的用户）**直接 Push 到 PR 源分支**，无需对方合并。步骤：

### 第一步：拉到本地

```bash
# 基于主分支创建同名的本地分支
git checkout -b feature/add-get-meta-tag main

# 拉取对方的 PR 分支代码
git pull https://github.com/PandaPy/gf feature/add-get-meta-tag
```

### 第二步：修改代码

在本地自由修改、优化代码。

### 第三步：Push 回对方分支

```bash
git push git@github.com:PandaPy/gf feature/add-get-meta-tag
```

> ⚠️ 使用 SSH 地址（`git@github.com:`），GitHub 新版本不再支持 HTTPS 方式 Push 到他人仓库。

### 效果

- ✅ PR 页面**自动更新**，显示 reviewer 的新提交
- ✅ 对方 fork 仓库中也能看到 reviewer 的 commit
- ✅ 贡献者不需要做任何额外操作

---

## 注意事项

| 问题 | 说明 |
|:-----|:------|
| Diff 展示过多 | 如果本地分支是从主分支拉出时包含了最新主分支代码，PR diff 可能显示过多变更。等待 GitHub diff 重新计算，或关闭/重新打开 PR |
| Squash/Rebase Merge 后 commit 归属 | 若 PR 合并时使用了 **squash merge** 或 **rebase merge**，reviewer 的 commit 不会出现在主仓库历史中。最终贡献者只显示为 PR 提交者，reviewer 的 commit 会被压缩成一个 |
| 权限要求 | 需要有目标仓库（对方 fork）的写权限。通常 fork 仓库默认允许 upstream 的 collaborator Push |
| SSH vs HTTPS | GitHub 已废弃 HTTPS 方式向他人仓库 Push，必须使用 `git@github.com:` SSH 地址 |

---

## 关联工具与概念

- Git Worktree 使用指南 — 多分支同时工作的另一种方式
- [GitNexus 代码知识图谱引擎](2026-06-26-gitnexus.md) — 大型代码库的理解与分析
- **GitHub 协作相关**：Fork 工作流、PR Review、Code Owner、Branch Protection

---

## 适用场景

| 场景 | 推荐做法 |
|:-----|:---------|
| Reviewer 需要修小问题（拼写/格式化/变量名） | ✅ **直接 Push PR 分支**（最快捷） |
| Reviewer 需要做较大重构 | ❌ 建议提 Comment 让贡献者自己改，或在原 PR 基础上提新 PR |
| 贡献者不活跃，Reviewer 代为完成 | ✅ 直接 Push 并合并 |
| 团队内的协作 PR | ✅ 直接 Push，省去来回沟通 |

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- Git Worktree 使用指南 — 关联
- [GitNexus 代码知识图谱引擎](2026-06-26-gitnexus.md) — 关联

### 外部资料引用

- 来源: [johng.cn 博客](https://johng.cn/notes/github-pr-collaboration)

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
