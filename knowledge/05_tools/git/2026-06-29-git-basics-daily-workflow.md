# Git 基础操作与日常开发场景

> **概要**: Git基础操作与日常开发场景指南，涵盖环境配置、10大日常场景、可视化工具与高级技巧
>
> **关键词**: Git · 基础操作 · 日常场景 · 分支管理 · 可视化工具

---

## 📑 目录

- [一、核心概念速查](#一核心概念速查)
- [二、环境配置](#二环境配置)
  - [2.1 首次配置](#21-首次配置)
  - [2.2 代理配置（国内加速）](#22-代理配置国内加速)
- [三、日常操作场景](#三日常操作场景)
  - [场景 1：初始化与克隆](#场景-1初始化与克隆)
  - [场景 2：日常提交](#场景-2日常提交)
  - [场景 3：分支管理](#场景-3分支管理)
  - [场景 4：合并与变基](#场景-4合并与变基)
  - [场景 5：获取与拉取](#场景-5获取与拉取)
  - [场景 6：查看历史](#场景-6查看历史)
  - [场景 7：撤销与回退](#场景-7撤销与回退)
  - [场景 8：储藏（Stash）](#场景-8储藏stash)
  - [场景 9：挑拣（Cherry-pick）](#场景-9挑拣cherry-pick)
  - [场景 10：标签管理](#场景-10标签管理)
- [四、可视化工具操作](#四可视化工具操作)
  - [VS Code Git 集成](#vs-code-git-集成)
  - [SourceTree 操作要点](#sourcetree-操作要点)
  - [VS 操作要点（.NET 场景）](#vs-操作要点net-场景)
- [五、高级技巧](#五高级技巧)
  - [5.1 差异比较](#51-差异比较)
  - [5.2 搜索与查找](#52-搜索与查找)
  - [5.3 子模块](#53-子模块)
  - [5.4 .gitignore 最佳实践](#54-gitignore-最佳实践)
- [六、常见工作流与操作速查](#六常见工作流与操作速查)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

**交叉引用**: [分支策略与团队协作规范](2026-06-29-git-branch-strategy-and-standards.md) | [提交信息规范与校验](2026-06-29-git-commit-convention-and-validation.md) | [常见错误诊断与排障](2026-06-29-git-common-errors-troubleshooting.md)

---

## 一、核心概念速查

| 概念 | 说明 |
|:-----|:------|
| **工作区 (Working Directory)** | 本地文件系统可见的文件 |
| **暂存区 (Staging/Index)** | `git add` 后的中间区域 |
| **本地仓库 (Local Repo)** | `git commit` 后的本地版本库 |
| **远程仓库 (Remote Repo)** | 托管在 GitHub/GitLab 等的远端版本库 |

```text
工作区 -> git add -> 暂存区 -> git commit -> 本地仓库 -> git push -> 远程仓库
```

---

## 二、环境配置

### 2.1 首次配置

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
git config --global core.editor "vim"
git config --global init.defaultBranch main
```

### 2.2 代理配置（国内加速）

```bash
# HTTP 代理
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

# SSH 代理（~/.ssh/config）
Host github.com
    HostName github.com
    User git
    ProxyCommand nc -X connect -x 127.0.0.1:7890 %h %p
```

---

## 三、日常操作场景

### 场景 1：初始化与克隆

```bash
# 新建仓库
git init
git remote add origin git@github.com:user/repo.git

# 克隆仓库
git clone git@github.com:user/repo.git
git clone --depth 1 git@github.com:user/repo.git   # 浅克隆（只取最新版本）
```

### 场景 2：日常提交

```bash
# 查看状态
git status

# 添加文件
git add file.txt            # 单个文件
git add .                   # 全部
git add -p                  # 交互式分段添加

# 提交
git commit -m "feat: 完成用户登录功能"
git commit -am "fix: 紧急修复"    # add + commit 合并（仅限已跟踪文件）

# 推送
git push origin main
git push -u origin main     # 首次推送关联远程分支
```

### 场景 3：分支管理

```bash
# 创建与切换
git branch feature/login
git checkout feature/login
git checkout -b feature/login    # 创建并切换（一步到位）
git switch -c feature/login      # Git 2.23+ 新语法

# 查看分支
git branch                       # 本地分支
git branch -a                    # 所有分支（含远程）
git branch -vv                   # 显示跟踪关系

# 删除分支
git branch -d feature/login      # 本地删除
git push origin --delete feature/login  # 远程删除

# 重命名分支
git branch -m old-name new-name
```

### 场景 4：合并与变基

```bash
# 合并（Merge）
git checkout main
git merge feature/login          # 将 feature/login 合并到当前分支
git merge --no-ff feature/login  # 保留分支历史（禁用快进合并）

# 变基（Rebase）
git checkout feature/login
git rebase main                  # 将 feature 变基到 main 最新

# 交互式变基（整理提交历史）
git rebase -i HEAD~3             # 整理最近 3 个提交
# 常用命令：pick / squash / reword / edit / drop
```

### 场景 5：获取与拉取

```bash
git fetch origin                 # 获取远程更新但不合并
git pull origin main             # fetch + merge
git pull --rebase origin main    # fetch + rebase（保持线性历史）
```

### 场景 6：查看历史

```bash
git log                          # 完整历史
git log --oneline                # 单行精简
git log --graph --oneline --all  # 分支图
git log -p                       # 查看每次提交的 diff
git log --author="name"          # 按作者过滤
git log --since="2026-01-01"     # 按时间过滤
git log --grep="bugfix"          # 按提交信息过滤
git blame file.txt               # 逐行追溯最后修改者
```

### 场景 7：撤销与回退

```bash
# 工作区撤销
git checkout -- file.txt         # 丢弃工作区修改
git restore file.txt             # Git 2.23+ 新语法

# 暂存区撤销
git reset HEAD file.txt          # 取消暂存
git restore --staged file.txt    # Git 2.23+ 新语法

# 提交撤销
git reset --soft HEAD~1          # 撤销提交，保留修改（回到暂存区）
git reset --mixed HEAD~1         # 撤销提交，保留修改（回到工作区）
git reset --hard HEAD~1          # 彻底丢弃最近一个提交（不可逆！）

# 回退到远程最新
git reset --hard origin/main

# 撤销已推送的提交（推荐用 revert）
git revert HEAD                  # 生成一个新提交来撤销
git revert HEAD~3..HEAD          # 撤销最近 3 个提交
```

### 场景 8：储藏（Stash）

```bash
git stash                        # 暂存当前修改
git stash list                   # 查看暂存列表
git stash pop                    # 恢复最近暂存并删除
git stash apply stash@{2}        # 恢复指定暂存但不删除
git stash drop stash@{0}         # 删除指定暂存
git stash branch new-branch      # 从暂存创建新分支
```

### 场景 9：挑拣（Cherry-pick）

```bash
# 将特定提交应用到当前分支
git cherry-pick <commit-hash>
git cherry-pick <hash1> <hash2>  # 挑拣多个
git cherry-pick A..B             # 挑拣 A 到 B 之间的所有提交（不含 A）
git cherry-pick A^..B            # 挑拣 A 到 B 之间的所有提交（含 A）
```

### 场景 10：标签管理

```bash
# 创建标签
git tag v1.0.0                   # 轻量标签
git tag -a v1.0.0 -m "发布v1.0.0" # 附注标签（推荐）

# 推送标签
git push origin v1.0.0           # 推送单个标签
git push origin --tags           # 推送所有标签

# 删除标签
git tag -d v1.0.0                # 本地删除
git push origin --delete v1.0.0  # 远程删除
```

---

## 四、可视化工具操作

### VS Code Git 集成

VS Code 内置 Git 支持，无需插件即可完成大部分日常操作：

| 操作 | 位置 |
|:-----|:------|
| 创建分支 | 状态栏左下角分支名 → 输入新名称 |
| 提交 | 源码管理面板 → 输入消息 → Ctrl+Enter |
| 推送/拉取 | 状态栏同步按钮 |
| 冲突解决 | 点击冲突文件 → 选择"采用当前/传入/两边合并" |
| 查看历史 | 右键文件 → Git: 查看文件历史 |

### SourceTree 操作要点

1. **创建分支**：切换到目标分支 → 点击"分支"按钮 → 输入名称
2. **删除分支**：切换到其他分支 → 右键目标分支 → 删除（勾选"强制删除"即同步删除远程）
3. **合并**：切换到目标分支 → 右键源分支 → "合并到当前分支"
4. **推送**：创建分支后需手动推送，不会自动推送

### VS 操作要点（.NET 场景）

1. **创建分支**：右下角输入分支名，选择"基于"的分支
2. **删除分支**：切换到其他分支 → 右键目标分支 → 删除
3. **合并**：切换到主干（如 master）→ 右键源分支 → "合并到 Current Branch"
4. **冲突解决**：右键冲突文件 → "合并" → 三栏对比界面（别人的/你的/原版）

---

## 五、高级技巧

### 5.1 差异比较

```bash
git diff                        # 工作区 vs 暂存区
git diff --cached               # 暂存区 vs 本地仓库
git diff HEAD                   # 工作区 vs 本地仓库
git diff main feature           # 两个分支对比
git diff --stat                 # 仅显示统计信息
word-diff                       # 单词级别对比
```

### 5.2 搜索与查找

```bash
git grep "function_name"        # 在版本历史中搜索
git log -S "function_name"      # 搜索添加/删除特定字符串的提交
git log -G "regex_pattern"      # 按正则搜索
git bisect start                 # 二分查找引入 bug 的提交
git bisect bad                   # 标记当前为坏版本
git bisect good v1.0.0          # 标记一个已知好版本
```

### 5.3 子模块

```bash
git submodule add <url> path    # 添加子模块
git submodule update --init     # 初始化子模块
git submodule update --remote   # 更新子模块到最新
git clone --recurse-submodules  # 克隆时同时拉取子模块
```

### 5.4 .gitignore 最佳实践

```gitignore
# 编译产物
*.o
*.obj
*.exe
*.dll
build/
dist/

# 依赖目录
node_modules/
vendor/
.venv/

# IDE 配置
.idea/
.vscode/
*.swp

# 环境变量
.env
.env.local

# 操作系统
.DS_Store
Thumbs.db
```

---

## 六、常见工作流与操作速查

| 目标 | 命令 |
|:-----|:------|
| 撤销工作区修改 | `git restore file.txt` |
| 撤销暂存 | `git restore --staged file.txt` |
| 修改最近 commit 信息 | `git commit --amend` |
| 给最近 commit 加文件 | `git add . && git commit --amend --no-edit` |
| 丢弃本地所有修改 | `git reset --hard HEAD` |
| 将其他分支的某个文件拿过来 | `git checkout feature -- path/file.txt` |
| 查看哪些文件冲突了 | `git diff --name-only --diff-filter=U` |
| 放弃冲突修改（直接采用对方的） | `git checkout --ours/--theirs file.txt` |
| 查看远程分支信息 | `git remote -v` |
| 添加远程仓库 | `git remote add upstream <url>` |
| 同步上游仓库 | `git fetch upstream && git merge upstream/main` |

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- Git版本控制高效管理 - 豆包整理 — 关联

### 外部资料引用

- 来源: [Git实战覆盖98%日常开发场景 - cnblogs](https://www.cnblogs.com/yuxl01/p/19928139)
- 来源: [Pro Git 官方文档](https://git-scm.com/book/zh/v2)
- 来源: --

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
