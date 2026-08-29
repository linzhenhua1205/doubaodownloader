# Git 跨仓库操作、变更报表与高级操作指南

> **概要**: Git跨仓库操作、Submodule与变更报表生成的实战指南
>
> **关键词**: 跨仓库合并 · Git Submodule · 变更报表 · GitPython · Cherry-pick

---

## 📑 目录

- [一、跨 Git 仓库合并改动](#一跨-git-仓库合并改动)
  - [1.1 两种主流场景](#11-两种主流场景)
    - [场景 A：临时性「拉取对方仓库某个分支的某次提交」](#场景-a临时性拉取对方仓库某个分支的某次提交)
    - [场景 B：长期跟踪对方仓库的某个分支](#场景-b长期跟踪对方仓库的某个分支)
  - [1.2 跨仓库 merge 的本质](#12-跨仓库-merge-的本质)
- [二、Git Submodule 完整教程](#二git-submodule-完整教程)
  - [2.1 核心概念](#21-核心概念)
  - [2.2 添加子模块](#22-添加子模块)
  - [2.3 子模块操作](#23-子模块操作)
  - [2.4 克隆时包含子模块](#24-克隆时包含子模块)
- [三、Git 提取指定时间段变更文件并生成报表](#三git-提取指定时间段变更文件并生成报表)
  - [3.1 Shell 一键输出 CSV](#31-shell-一键输出-csv)
  - [3.2 Python 完整方案（GitPython）](#32-python-完整方案gitpython)
  - [3.3 提取昨日/当日的快捷命令](#33-提取昨日当日的快捷命令)
- [四、Git 实用操作速查](#四git-实用操作速查)
  - [4.1 推送异常排查](#41-推送异常排查)
  - [4.2 大文件清理（已提交到历史）](#42-大文件清理已提交到历史)
  - [4.3 恢复误删除文件](#43-恢复误删除文件)
  - [4.4 查看文件历史](#44-查看文件历史)
  - [4.5 软链接（Symbolic Link）处理](#45-软链接symbolic-link处理)
  - [4.6 查找所有冲突文件](#46-查找所有冲突文件)
  - [4.7 查看远程仓库分支](#47-查看远程仓库分支)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

---

## 一、跨 Git 仓库合并改动

### 1.1 两种主流场景

#### 场景 A：临时性「拉取对方仓库某个分支的某次提交」

```bash
# 1. 把对方仓库添加为远程
git remote add other-repo https://github.com/other-org/other-repo.git

# 2. 拉取对方分支（不自动合并）
git fetch other-repo target-branch

# 3. cherry-pick 所需提交
git cherry-pick <commit-sha>

# 4. 用完可删除远程（可选）
git remote remove other-repo
```

#### 场景 B：长期跟踪对方仓库的某个分支

```bash
# 1. 添加远程
git remote add upstream https://github.com/other-org/other-repo.git

# 2. 创建跟踪分支
git checkout -b track-upstream-main upstream/main

# 3. 定期拉取上游更新
git fetch upstream
git merge upstream/main
```

### 1.2 跨仓库 merge 的本质

跨仓库 merge 本质上和同仓库不同分支 merge **没有区别**——Git 只关心 commit 对象，不关心它们来自哪个仓库。关键差异在于:

- GitHub / GitLab 的 PR/MR UI 只支持**同仓库**或**同平台 fork**
- 纯 Git 命令行可以做任意跨仓库 merge
- CI/CD 触发器只识别同一仓库的 MR/Push，跨仓库需手动触发

---

## 二、Git Submodule 完整教程

### 2.1 核心概念

`git submodule` 可以把另一个 Git 仓库嵌入当前仓库的指定目录，保持独立版本控制。

### 2.2 添加子模块

```bash
# 添加子模块到指定路径
git submodule add https://github.com/user/library.git lib/library

# 初始化并拉取（新 clone 仓库时）
git clone --recurse-submodules https://github.com/org/main-repo.git
# 或后续拉取
git submodule update --init --recursive
```

### 2.3 子模块操作

```bash
# 查看子模块状态
git submodule status

# 更新子模块到最新 commit
git submodule update --remote

# 在子模块内操作后提交
cd lib/library
git checkout v1.2.3
cd ../..
git add lib/library
git commit -m "Update library to v1.2.3"
```

### 2.4 克隆时包含子模块

```bash
# 方式一：克隆时直接拉取
git clone --recurse-submodules <url>

# 方式二：已克隆后补拉
git submodule update --init --recursive

# 方式三：使用 gh CLI
gh repo clone <repo> -- --recurse-submodules
```

---

## 三、Git 提取指定时间段变更文件并生成报表

### 3.1 Shell 一键输出 CSV

```bash
#!/bin/bash
# 提取指定日期范围的变更文件，输出 CSV
SINCE="2026-06-01"
UNTIL="2026-06-23"

git log --since="$SINCE" --until="$UNTIL" --name-status \
  --pretty=format:"%H,%an,%ae,%ai,%s" --reverse \
  | awk 'BEGIN {print "COMMIT_HASH,AUTHOR,EMAIL,DATE,MSG,CHANGE_TYPE,FILE_PATH"}
         /^[0-9a-f]{40},/ {commit=$0; next}
         /^[AMDR]/ {print commit "," $0}'
```

### 3.2 Python 完整方案（GitPython）

```python
from git import Repo
import csv
from datetime import datetime

def get_changes_between(repo_path, since_date, until_date, output_file):
    """提取指定时间段的Git变更文件并生成CSV报表"""
    repo = Repo(repo_path)

    # 遍历提交
    commits = list(repo.iter_commits(
        'main',
        since=since_date,
        until=until_date
    ))

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Commit Hash', 'Author', 'Email', 'Date',
            'Message', 'Change Type', 'File Path', 'Added', 'Deleted'
        ])

        for commit in commits:
            # 获取该 commit 的变更文件
            if commit.parents:
                diffs = commit.parents[0].diff(commit)
            else:
                # 首次提交
                diffs = commit.diff(None)

            for diff_item in diffs:
                change_type = {
                    'A': 'Added', 'M': 'Modified',
                    'D': 'Deleted', 'R': 'Renamed'
                }.get(diff_item.change_type, diff_item.change_type)

                writer.writerow([
                    commit.hexsha,
                    commit.author.name,
                    commit.author.email,
                    datetime.fromtimestamp(commit.committed_date).isoformat(),
                    commit.message.split('\n')[0],
                    change_type,
                    diff_item.b_path or diff_item.a_path,
                    diff_item.insertions or 0,
                    diff_item.deletions or 0,
                ])

    return output_file
```

### 3.3 提取昨日/当日的快捷命令

```bash
# 当日提交的所有文件
git log --since="midnight" --name-only --pretty=format:"" | sort -u

# 昨日提交的所有文件
git log --since="yesterday" --until="midnight" --name-only --pretty=format:"" | sort -u

# 含变更类型（A=新增, M=修改, D=删除）
git log --since="yesterday" --until="midnight" \
  --name-status --pretty=format:"" | sort -u

# 指定时间段
git log --since="2026-01-01" --until="2026-06-23" \
  --name-status --pretty=format:"COMMIT: %h %ai %an" --reverse
```

---

## 四、Git 实用操作速查

### 4.1 推送异常排查

| 错误 | 原因 | 解决 |
|:-----|:-----|:-----|
| `src refspec master does not match any` | 默认分支名为 `main`，非 `master` | 使用 `git push origin main` |
| `non-fast-forward` | 远程有本地没有的提交 | `git pull --rebase origin main` |
| `failed to push some refs` | 远程有未拉取的变更 | `git pull origin main --allow-unrelated-histories` |
| **文件 > 100MB** | GitHub 禁止单个文件超 100MB | 使用 `git filter-branch` / `BFG` 删除 |
| **HTTP 413 / 超时** | 推送内容过大或网络不稳定 | 分批次推送 / 使用 SSH |

### 4.2 大文件清理（已提交到历史）

```bash
# 方案一：git filter-branch（重写历史）
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch <大文件路径>" \
  --prune-empty --tag-name-filter cat -- --all

# 方案二：BFG Repo-Cleaner（推荐，更快）
java -jar bfg.jar --delete-files <文件名> .git

# 清理后推送
git push origin --force --all
git push origin --force --tags
```

### 4.3 恢复误删除文件

| 场景 | 命令 |
|:-----|:-----|
| 未提交（工作区） | `git restore <file>` |
| 已暂存 | `git restore --staged <file>` |
| 已提交未推送 | `git checkout HEAD~1 -- <file>` |
| 已推送 | `git revert <commit-hash>` |
| 不确定在哪个 commit | `git log --all --diff-filter=D -- <file>` |

### 4.4 查看文件历史

```bash
# 查看单个文件最后一次提交
git log -1 --oneline -- <file>

# 查看文件所有提交（含作者、时间）
git log --all --follow -- <file>

# 查看文件每次提交的作者
git blame <file>

# 查看某作者对文件的修改
git log --author="name" -- <file>
```

### 4.5 软链接（Symbolic Link）处理

```bash
# 创建软链接并提交
ln -s ../target/file.txt link.txt
git add link.txt
git commit -m "Add symlink to target/file.txt"

# Git 存储时标记模式为 120000
# 检出的链接指向文本文件中记录的目标路径
```

### 4.6 查找所有冲突文件

```bash
# 查找目录下所有包含冲突标记的文件
grep -r "<<<<<<<" --include="*.lua" --include="*.py" --include="*.md" -l

# 查看 Git 冲突状态
git status

# 查看冲突的详细 diff
git diff --name-only --diff-filter=U
```

### 4.7 查看远程仓库分支

```bash
# 查看所有远程分支
git branch -r

# 查看远程分支详情（含上游跟踪）
git branch -vv

# 查看远程仓库的分支列表
git ls-remote --heads origin

# 查看远程 VS 本地差异
git log --oneline origin/main..HEAD
```

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- (无)

### 外部资料引用

- 来源: 豆包对话（flashnet → 豆包）
- 来源: Git 实战经验提炼

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
