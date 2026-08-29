# Git 常用操作速查手册

> **概要**: Git常用操作速查手册，涵盖分支、日志、统计、Rebase与Cherry-pick等
>
> **关键词**: Git速查 · 分支操作 · Rebase · Cherry-pick · Stash

---

## 📑 目录

- [一、分支操作](#一分支操作)
  - [1.1 查看分支](#11-查看分支)
  - [1.2 创建与切换分支](#12-创建与切换分支)
  - [1.3 合并分支](#13-合并分支)
  - [1.4 删除与重命名分支](#14-删除与重命名分支)
  - [1.5 分支间文件操作](#15-分支间文件操作)
- [二、日志查询与修改](#二日志查询与修改)
  - [2.1 查看提交日志](#21-查看提交日志)
  - [2.2 日志格式化](#22-日志格式化)
  - [2.3 按条件过滤日志](#23-按条件过滤日志)
  - [2.4 修改提交历史](#24-修改提交历史)
- [三、近期提交统计分析](#三近期提交统计分析)
  - [3.1 按作者统计](#31-按作者统计)
  - [3.2 按时间统计](#32-按时间统计)
  - [3.3 按文件/目录统计](#33-按文件目录统计)
  - [3.4 代码量贡献排行榜](#34-代码量贡献排行榜)
  - [3.5 实用统计一键脚本](#35-实用统计一键脚本)
- [四、多分支交互](#四多分支交互)
  - [4.1 分支间同步](#41-分支间同步)
  - [4.2 Rebase（变基）](#42-rebase变基)
  - [4.3 Cherry-pick（挑拣）](#43-cherry-pick挑拣)
  - [4.4 Stash（工作区暂存）](#44-stash工作区暂存)
  - [4.5 多分支协同工作流速查](#45-多分支协同工作流速查)
  - [4.6 分支差异对比](#46-分支差异对比)
- [五、快速索引表](#五快速索引表)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

**交叉引用**: [Git 基础操作与日常开发场景](2026-06-29-git-basics-daily-workflow.md) | [分支策略与团队协作规范](2026-06-29-git-branch-strategy-and-standards.md) | [常见错误诊断与排障](2026-06-29-git-common-errors-troubleshooting.md)

---

## 一、分支操作

### 1.1 查看分支

```bash
# 查看本地分支（* 表示当前所在分支）
git branch
# 输出示例：
#   dev
# * feature/login     ← 当前在 feature/login
#   main

# 查看所有分支（含远程跟踪分支）
git branch -a

# 查看分支与远程的跟踪关系
git branch -vv
# 输出示例：
#   dev              a1b2c3d [origin/dev] feat: 更新配置
# * feature/login    e4f5g6h [origin/feature/login: ahead 2] feat: 登录功能
#   main             h7i8j9k [origin/main] chore: 初始化

# 查看已合并到当前分支的分支（准备删除的候选）
git branch --merged

# 查看尚未合并的分支
git branch --no-merged
```

### 1.2 创建与切换分支

```bash
# 创建分支（不切换）
git branch feature/payment

# 切换分支
git checkout feature/payment
# 或新版语法
git switch feature/payment

# 创建并立即切换（最常用）
git checkout -b feature/payment
git switch -c feature/payment    # Git 2.23+

# 基于指定提交/标签创建分支
git checkout -b hotfix/crash v1.0.0
git checkout -b experiment a1b2c3d
```

### 1.3 合并分支

```bash
# 合并（将 feature 合并到当前分支）
# 先切到目标分支，再合并源分支
git checkout main
git merge feature/login

# 禁用快进合并（保留分支历史拓扑）
git merge --no-ff feature/login

# 仅快进可合并，否则放弃（安全合并）
git merge --ff-only feature/login

# 合并后查看哪些文件有冲突
git diff --name-only --diff-filter=U
```

### 1.4 删除与重命名分支

```bash
# 删除本地分支（已合并的分支用 -d，未合并的强制用 -D）
git branch -d feature/login      # 安全删除（检查是否已合并）
git branch -D feature/abandoned  # 强制删除（未合并也删）

# 删除远程分支
git push origin --delete feature/login

# 重命名分支
git branch -m old-name new-name         # 重命名当前分支
git branch -m feature/login feature/auth # 重命名指定分支
```

### 1.5 分支间文件操作

```bash
# 从其他分支拿单个文件过来
git checkout feature/login -- src/auth.js

# 比较两个分支的文件差异
git diff main feature/login -- src/auth.js

# 将其他分支的某个目录覆盖到当前分支
git checkout feature/login -- src/module/
```

---

## 二、日志查询与修改

### 2.1 查看提交日志

```bash
# 基本日志
git log                            # 完整日志
git log --oneline                  # 每行一个提交（最常用）
git log --oneline -10              # 最近 10 条

# 图形化日志（推荐日常使用）
git log --graph --oneline --all
# 输出示例：
# *   a1b2c3d (HEAD -> feature/login) feat: 完成登录表单
# *   b2c3d4e feat: 添加验证码组件
# | * c3d4e5f (origin/main, main) fix: 修复首页样式
# |/
# *   d4e5f6g chore: 初始化项目
```

### 2.2 日志格式化

```bash
# 自定义输出格式
git log --pretty=format:"%h - %an, %ar : %s"
# 输出示例：a1b2c3d - Zhang San, 2 hours ago : feat: 登录功能

# 常用格式占位符
# %h    = 短 hash
# %H    = 完整 hash
# %an   = 作者名
# %ae   = 作者邮箱
# %ar   = 相对时间（2 hours ago）
# %s    = 提交信息第一行
# %d    = 分支/标签引用名

# 带统计信息的日志
git log --stat                     # 显示文件变更统计
git log --shortstat                # 精简统计（+X -Y）
git log --name-only                # 仅显示变更文件列表
```

### 2.3 按条件过滤日志

```bash
# 按作者
git log --author="Zhang"
git log --author="Zhang\|Li"       # 多个作者

# 按时间
git log --since="2026-06-01"
git log --until="2026-06-29"
git log --since="2 weeks ago"
git log --since="2026-06-01" --until="2026-06-15"

# 按提交信息关键词
git log --grep="bugfix"
git log --grep="feat" --grep="payment" --all-match  # 同时匹配多个

# 按文件路径
git log -- src/auth.js             # 只查看某个文件的修改历史
git log -- src/auth/               # 某个目录的修改历史

# 按改动内容（搜索代码变更）
git log -S "function_name"         # 添加/删除了该字符串的提交
git log -G "regex_pattern"         # 正则匹配变更内容

# 按范围
git log main..feature/login        # feature 有但 main 没有的提交
git log --left-right main...feature/login  # 双向对比标记 < >
```

### 2.4 修改提交历史

```bash
# 修改最近一次提交的信息
git commit --amend -m "新的提交信息"

# 给最近一次提交追加文件
git add forgotten-file.txt
git commit --amend --no-edit

# 修改多个提交（交互式变基）
git rebase -i HEAD~3               # 修改最近 3 个提交
# 进入交互界面后，常用命令：
# pick    = 保留该提交
# reword  = 修改提交信息
# squash  = 合并到上一个提交
# edit    = 暂停以便修改内容
# drop    = 删除该提交

# 撤销提交（生成反向提交，适合已推送的情况）
git revert HEAD                    # 撤销最近一次提交
git revert HEAD~3..HEAD            # 撤销最近 3 个提交

# 丢弃最近 N 次提交（仅限未推送的本地提交）
git reset --soft HEAD~2            # 回到暂存区（保留修改）
git reset --mixed HEAD~2           # 回到工作区（保留修改，默认）
git reset --hard HEAD~2            # 彻底丢弃（不可逆！）
```

---

## 三、近期提交统计分析

### 3.1 按作者统计

```bash
# 统计每个作者的提交次数
git shortlog -sn
# 输出示例：
#    42  Zhang San
#    28  Li Si
#    15  Wang Wu

# 按作者统计并显示提交信息
git shortlog -n

# 统计某段时间内的作者贡献
git shortlog -sn --since="2026-06-01" --until="2026-06-29"

# 统计某个文件的作者贡献
git shortlog -sn -- src/core/auth.js

# 统计每个作者的代码行数变更
git log --author="Zhang San" --pretty=tformat: --numstat | awk '{ add += $1; subs += $2; loc += $1 - $2 } END { printf "增加行数: %s, 删除行数: %s, 净增行数: %s\n", add, subs, loc }'
```

### 3.2 按时间统计

```bash
# 每天的提交数
git log --since="2026-06-01" --date=format:"%Y-%m-%d" --pretty=format:"%ad" | sort | uniq -c | sort -rn

# 每周的提交数
git log --since="2026-06-01" --date=format:"%Y-W%V" --pretty=format:"%ad" | sort | uniq -c | sort -rn

# 每小时的提交分布（看团队活跃时段）
git log --since="2026-06-01" --date=format:"%H" --pretty=format:"%ad" | sort | uniq -c | sort -rn

# 统计某天活跃度
git log --after="2026-06-28" --before="2026-06-29" --oneline | wc -l
```

### 3.3 按文件/目录统计

```bash
# 统计目录下提交次数
git log --oneline -- src/module/payment/ | wc -l

# 每个文件的修改次数 Top 10
git log --pretty=format: --name-only | sort | uniq -c | sort -rn | head -10
# 输出示例：
#   23 src/core/payment.js
#   18 src/auth/login.js
#   15 package.json

# 统计代码行数变化（总览）
git log --since="2026-06-01" --shortstat | grep -E "insertions|deletions" | awk '{ins+=$1; del+=$4} END {printf "总增加: %s 行, 总删除: %s 行, 净增: %s 行\n", ins, del, ins-del}'
```

### 3.4 代码量贡献排行榜

```bash
# 一键统计每个作者的代码行数净增
git log --since="2026-06-01" --pretty=tformat: --numstat \
  | awk '{ add[$3]+=$1; subs[$3]+=$2 } END { for (author in add) { net=add[author]-subs[author]; printf "%-20s +%-6s -%-6s net: %+6s\n", author, add[author], subs[author], net } }' \
  | sort -k4 -rn
# 输出示例：
# Zhang San           +1245    -342    net:   +903
# Li Si               +876     -567    net:   +309
# Wang Wu             +234     -112    net:   +122
```

### 3.5 实用统计一键脚本

将以下内容保存为 `git-stats.sh`，每天跑一次即可：

```bash
#!/bin/bash
# Git 提交统计速查

echo "===== 提交统计报表 ====="
echo ""

echo "--- 作者提交次数 ---"
git shortlog -sn --since="7 days ago"

echo ""
echo "--- 每日提交数（近7天）---"
git log --since="7 days ago" --date=format:"%m-%d" --pretty=format:"%ad" | sort | uniq -c | sort -k2

echo ""
echo "--- 代码行数变化（近7天）---"
git log --since="7 days ago" --shortstat | grep -E "insertions|deletions" \
  | awk '{ins+=$1; del+=$4} END {printf "增加: %s 行, 删除: %s 行, 净增: %s 行\n", ins, del, ins-del}'

echo ""
echo "--- 最近 10 条提交 ---"
git log --oneline -10
```

---

## 四、多分支交互

### 4.1 分支间同步

```bash
# 获取远程所有分支更新（不自动合并）
git fetch
git fetch origin
git fetch --prune                   # 同时清理已删除的远程分支引用

# 拉取并合并到当前分支
git pull                            # fetch + merge
git pull --rebase                   # fetch + rebase（推荐，保持线性历史）

# 推送当前分支到远程
git push origin feature/login

# 首次推送并建立跟踪关系
git push -u origin feature/login    # 之后可以直接 git push / git pull
```

### 4.2 Rebase（变基）

```bash
# 将当前分支的提交"移植"到 main 的最新提交之上
git checkout feature/login
git rebase main

# rebase 过程示意图：
# 之前：
#   main:   A---B
#   feature/login: C---D
# rebase main 之后：
#   main:   A---B
#   feature/login:       C'---D'
# 效果：feature/login 基于 main 的最新提交，历史线性

# 交互式变基（整理提交）
git rebase -i HEAD~5                # 整理最近 5 个提交

# 遇到冲突时
git rebase --continue               # 解决冲突后继续
git rebase --skip                   # 跳过当前提交
git rebase --abort                  # 放弃 rebase，回到之前状态

# 从 main 变基并保留合并（--rebase-merges）
git rebase --rebase-merges main
```

### 4.3 Cherry-pick（挑拣）

```bash
# 把其他分支的某个提交捡到当前分支
git checkout main
git cherry-pick a1b2c3d             # 将 a1b2c3d 这个提交挑到 main

# 挑拣多个提交
git cherry-pick a1b2c3d e4f5g6h

# 挑拣一段连续的提交
git cherry-pick A..B                # 挑拣 A 之后到 B 之间的提交（不含 A）
git cherry-pick A^..B               # 挑拣 A 到 B 之间的提交（含 A）

# pick 到其他分支的典型场景
# 场景：hotfix 修复在 main 上做了，需要同步到 dev
git checkout dev
git cherry-pick -x a1b2c3d          # -x 会在提交信息中标注来源

# 挑拣时保留原始提交者信息（默认行为）
# 如果想改作者：
git cherry-pick -n a1b2c3d          # 只捡内容不提交
git commit -m "fix: 移植修复到 dev"
```

### 4.4 Stash（工作区暂存）

```bash
# 场景：正在 feature 上开发，临时需要去 main 修 bug
# 不想提交半成品代码，临时存起来

# 暂存当前工作区修改
git stash
git stash push -m "登录功能未完成"   # 带描述地暂存

# 查看暂存列表
git stash list
# 输出示例：
# stash@{0}: On feature/login: 登录功能未完成
# stash@{1}: On feature/payment: 支付表单

# 恢复暂存（两种方式）
git stash pop                       # 恢复最近的 stash 并删除
git stash apply                     # 恢复但不删除（可在多个分支重复应用）
git stash apply stash@{1}           # 恢复指定的 stash

# 删除暂存
git stash drop stash@{0}            # 删除指定
git stash clear                     # 清空所有 stash

# 从 stash 创建分支（最安全：如果恢复后有冲突，自动帮你建分支）
git stash branch new-feature stash@{0}

# 查看 stash 中的改动内容
git stash show -p stash@{0}
```

### 4.5 多分支协同工作流速查

```bash
# 场景 1：从 main 创建功能分支
git checkout main && git pull
git checkout -b feature/xxx

# 场景 2：开发中同步上游更新
git fetch origin
git rebase origin/main              # 推荐：保持线性历史
# 或
git merge origin/main               # 保留合并记录

# 场景 3：完成开发后合并回 main
git checkout main && git pull
git merge --no-ff feature/xxx
git branch -d feature/xxx

# 场景 4：需要中途切去修紧急 bug
git stash                           # 暂存当前进度
git checkout main && git pull
git checkout -b hotfix/urgent        # 修 bug
# ... 修完合并 ...
git checkout feature/xxx
git stash pop                       # 恢复原来进度

# 场景 5：不小心提交到了 main，应该去 feature 分支
git branch feature/xxx              # 先基于当前提交创建分支
git reset HEAD~1 --hard            # main 回退一个提交
git checkout feature/xxx            # 切到正确的分支继续

# 场景 6：把多个分支的改动合并整理
# 如果你同时在几个分支上工作，想汇总某个功能到 main：
git checkout feature/combined
git merge feature/auth              # 合并登录模块
git cherry-pick a1b2c3d             # 挑拣支付模块的关键提交
git merge feature/optimize          # 合并性能优化
# 统一测试通过后合并到 main
```

### 4.6 分支差异对比

```bash
# 查看两个分支的差异
git diff main feature/login         # 完整 diff
git diff main feature/login --stat  # 仅统计
git diff main feature/login -- src/ # 只看特定目录

# 查看哪些提交在一个分支但不在另一个
git log main..feature/login         # feature 有而 main 没有
git log feature/login..main         # main 有而 feature 没有

# 查看两个分支分叉以来的共同祖先
git merge-base main feature/login

# 查看分支图（最直观的多分支关系）
git log --graph --oneline --all --decorate
# 输出示例（带颜色）：
# * a1b2c3d (HEAD -> feature/login) feat: 登录表单
# * b2c3d4e feat: 验证码组件
# | * c3d4e5f (origin/main, main) fix: 首页样式
# | * d4e5f6g fix: 导航栏崩溃
# |/
# * e5f6g7h chore: 初始化
```

---

## 五、快速索引表

| 想要做什么 | 一句话命令 |
|:-----------|:-----------|
| 查看当前分支 | `git branch` |
| 创建并切换分支 | `git checkout -b <name>` |
| 合并分支到当前 | `git merge <branch>` |
| 删除本地分支 | `git branch -d <branch>` |
| 删除远程分支 | `git push origin --delete <branch>` |
| 查看简洁日志 | `git log --oneline -10` |
| 查看分支图 | `git log --graph --oneline --all` |
| 按作者搜索日志 | `git log --author="name"` |
| 按时间搜索日志 | `git log --since="7 days ago"` |
| 修改最近提交信息 | `git commit --amend -m "新信息"` |
| 撤销已推送的提交 | `git revert HEAD` |
| 撤销本地提交 | `git reset --soft HEAD~1` |
| 作者提交次数统计 | `git shortlog -sn` |
| 每天提交分布 | `git log --since="7 days" --date=format:"%m-%d" --pretty=format:"%ad" \| sort \| uniq -c` |
| 同步上游最新代码 | `git fetch && git rebase origin/main` |
| 从其他分支捡提交 | `git cherry-pick <hash>` |
| 暂存当前修改 | `git stash` |
| 恢复暂存 | `git stash pop` |
| 比较分支差异 | `git diff branch1 branch2 --stat` |

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- [Git 基础操作与日常开发场景](2026-06-29-git-basics-daily-workflow.md) — 关联
- [分支策略与团队协作规范](2026-06-29-git-branch-strategy-and-standards.md) — 关联

### 外部资料引用

- 来源: [Pro Git — git-scm.com](https://git-scm.com/book/zh/v2)
- 来源: --

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
