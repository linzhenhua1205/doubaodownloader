# Git 分支策略与团队协作规范

> **概要**: Git分支策略与团队协作规范，涵盖GitFlow/Trunk/GitHub Flow三种策略、命名规范与PR评审机制
>
> **关键词**: Git · 分支策略 · GitFlow · 团队协作 · PR评审

---

## 📑 目录

- [一、核心分支定义](#一核心分支定义)
- [二、三种主流分支策略](#二三种主流分支策略)
  - [方案 1：GitFlow（大中规模稳定业务）](#方案-1gitflow大中规模稳定业务)
  - [方案 2：Trunk Based Development（敏捷/快速迭代）](#方案-2trunk-based-development敏捷快速迭代)
  - [方案 3：GitHub Flow（轻量化）](#方案-3github-flow轻量化)
- [三、分支命名规范](#三分支命名规范)
- [四、代码合并与评审机制](#四代码合并与评审机制)
  - [4.1 强制 PR/MR 流程](#41-强制-prmr-流程)
  - [4.2 评审规则](#42-评审规则)
  - [4.3 合并策略选择](#43-合并策略选择)
  - [4.4 PR 描述模板](#44-pr-描述模板)
- [需求描述](#需求描述)
- [变更内容](#变更内容)
- [测试情况](#测试情况)
- [注意事项](#注意事项)
- [五、Fork 协作模式（开源项目）](#五fork-协作模式开源项目)
  - [流程总览](#流程总览)
  - [配置步骤](#配置步骤)
  - [关键原则](#关键原则)
- [六、版本发布流程](#六版本发布流程)
  - [标准发布流程](#标准发布流程)
  - [紧急修复流程](#紧急修复流程)
- [七、常见协作问题与解决方案](#七常见协作问题与解决方案)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

**交叉引用**: [Git 基础操作](2026-06-29-git-basics-daily-workflow.md) | [提交信息规范与校验](2026-06-29-git-commit-convention-and-validation.md) | [GitHub Actions CI/CD](2026-06-29-github-actions-cicd.md) | [GitLab 集成与自动化](2026-06-29-gitlab-integration-automation.md)

---

## 一、核心分支定义

| 分支名称 | 类型 | 作用 | 权限控制 |
|:---------|:-----|:-----|:---------|
| `main/master` | 生产稳定分支 | 已上线、可直接部署的生产代码 | 禁止直接推送，仅管理员可合并 |
| `dev/develop` | 开发主分支 | 日常开发核心分支，所有功能汇聚于此 | 禁止直接提交，仅通过 PR 合并 |
| `release/vX.Y.Z` | 发布分支 | 预发布、测试专用 | 从 dev 合并，上线后合并 main 并删除 |
| `feature/xxx` | 功能分支 | 新功能开发（临时分支） | 开发人员自行创建，完成后删除 |
| `bugfix/xxx` | 缺陷修复分支 | 修复 bug（临时分支） | 开发人员自行创建，完成后删除 |
| `hotfix/xxx` | 生产紧急修复分支 | 线上紧急 bug | 仅核心开发创建，必须同步合并到 dev 和 main |

---

## 二、三种主流分支策略

### 方案 1：GitFlow（大中规模稳定业务）

**适用场景**：版本节奏明确、需要多版本并行维护的项目（如企业级应用、SDK、操作系统）

**结构**：

```text
main ---o----o-------------------o----o (v1.0)-- (v1.1)
         \  / \                  / \  /
develop--o-o--o-o--------------o--o-o
              \                /
feature/login  o--o--o-------o
                          \
release/v1.0                o--o--o
```

**操作流程**：

```bash
# 1. 创建功能分支（从 develop）
git checkout develop && git pull
git checkout -b feature/user-login

# 2. 开发完成后合并回 develop
git checkout develop
git merge --no-ff feature/user-login
git branch -d feature/user-login

# 3. 创建发布分支
git checkout develop && git pull
git checkout -b release/v1.0.0

# 4. 发布分支修复 bug → 合并回 main 和 develop
git checkout main && git merge --no-ff release/v1.0.0
git tag -a v1.0.0 -m "v1.0.0"
git checkout develop && git merge --no-ff release/v1.0.0
git branch -d release/v1.0.0

# 5. 紧急修复
git checkout main && git pull
git checkout -b hotfix/crash-fix
# 修复后合并到 main 和 develop
```

**优点**：发布、回滚、多版本并行清晰
**缺点**：分支多、流程较重，不适合快速迭代

### 方案 2：Trunk Based Development（敏捷/快速迭代）

**适用场景**：微服务、互联网产品、持续交付、CI/CD 成熟团队

**核心规则**：

- 仅保留 `main/trunk` 主干
- 短生命周期 feature 分支（当天/3 天内合并）
- 持续集成自动校验
- 发布时从 main 打 Tag，不长期保留 release 分支

```bash
# 从 main 拉短生命周期分支
git checkout main && git pull
git checkout -b feat/quick-fix
# 开发... 完成立即 PR 合并

# 发布
git checkout main && git pull
git tag -a v2.3.1 -m "v2.3.1"
git push origin v2.3.1
```

**优点**：分支少、合并冲突低、CI 持续交付
**缺点**：需强自动化测试保障主干稳定性

### 方案 3：GitHub Flow（轻量化）

**适用场景**：开源项目、前端独立小服务、个人项目

**核心规则**：

- 仅 `main` 分支
- 所有改动新建临时分支
- PR 审核通过合并 main
- 合并后立即部署/打 Tag

```bash
git checkout -b fix/typo
# 修改后推送
git push origin fix/typo
# 在 GitHub 创建 PR → 审核通过 → Squash and Merge
git checkout main && git pull
```

---

## 三、分支命名规范

**强制统一格式**：

```text
feature/需求ID-功能简述      # 如 feature/T123-user-login
bugfix/BUGID-问题描述        # 如 bugfix/T456-payment-error
hotfix/线上问题编号           # 如 hotfix/crash-fix
release/vX.Y.Z              # 如 release/v1.3.0
docs/接口文档更新             # 如 docs/api-refactor
chore/构建优化               # 如 chore/ci-upgrade
```

---

## 四、代码合并与评审机制

### 4.1 强制 PR/MR 流程

禁止直接 push 到 `main/develop`，所有代码必须通过 PR 合并。

### 4.2 评审规则

1. **至少 1 名同模块开发**审核通过
2. **CI 流水线全部通过**：编译、单元测试、代码规范扫描、安全检测
3. **代码增量过大拆小**：>1000 行建议拆分多个小 PR
4. **禁止自我 approve**

### 4.3 合并策略选择

| 策略 | 适用场景 | 效果 |
|:-----|:---------|:-----|
| **Squash and Merge** | 迭代功能开发（推荐） | 所有提交压缩为一条干净 commit，主干历史整洁 |
| **Merge Commit** | GitFlow 多版本追溯 | 完整保留分支所有提交 |
| **Rebase and Merge** | TBD 持续迭代 | 保证主干线性历史 |

### 4.4 PR 描述模板

```markdown
## 需求描述
[关联需求/工单链接]

## 变更内容
- [x] 功能 A
- [ ] 功能 B

## 测试情况
- [x] 单元测试通过
- [x] 本地构建成功
- [ ] 集成测试

## 注意事项
[回滚方案、依赖变更等]
```

---

## 五、Fork 协作模式（开源项目）

### 流程总览

```text
主仓库 -> Fork 到个人账号 -> 个人 Fork 仓库
                                      v
                              git clone 到本地
                                      v
                              git remote add upstream
                                      v
                              创建开发分支、编码
                                      v
                              git push 到个人 Fork
                                      v
                              Pull Request -> 主仓库
                                      v
                              Squash and Merge
                                      v
                              同步主仓库到个人 Fork
```

### 配置步骤

```bash
# 1. Fork 主仓库后在本地克隆个人 Fork
git clone git@github.com:yourname/repo.git
cd repo

# 2. 添加上游仓库（主仓库）
git remote add upstream git@github.com:org/repo.git
git remote -v  # 确认：origin=你的Fork, upstream=主仓库

# 3. 同步主仓库最新代码
git fetch upstream
git checkout main
git merge upstream/main

# 4. 从最新 main 创建开发分支
git checkout -b feat/new-feature
```

### 关键原则

- **永远不在个人 Fork 的 main 分支上直接开发**
- 每次开发前同步主仓库最新代码，避免基于旧版本开发
- PR 合并后在个人 Fork 中删除已合并的分支
- 禁止使用 `Create a merge commit` 方式合并（会污染主仓库历史）

---

## 六、版本发布流程

### 标准发布流程

```bash
# 1. 从 dev 创建发布分支
git checkout dev && git pull
git checkout -b release/v1.2.0
git push origin release/v1.2.0

# 2. 测试修复（在 release 分支上）
# bug 修复后同步回 dev
git checkout dev && git merge release/v1.2.0

# 3. 测试通过后上线
git checkout main && git merge --no-ff release/v1.2.0
git tag -a v1.2.0 -m "版本 v1.2.0"
git push origin main --tags

# 4. 删除发布分支
git branch -d release/v1.2.0
git push origin --delete release/v1.2.0
```

### 紧急修复流程

```bash
git checkout main && git pull
git checkout -b hotfix/security-patch
# 修复...
git commit -m "hotfix: 安全补丁"
git push origin hotfix/security-patch
# PR → 合并到 main
git checkout main && git merge hotfix/security-patch
git tag -a v1.2.1 -m "紧急修复 v1.2.1"
git checkout dev && git merge hotfix/security-patch  # 同步到开发分支
git branch -d hotfix/security-patch
```

---

## 七、常见协作问题与解决方案

| 问题 | 原因 | 解决方案 |
|:-----|:-----|:---------|
| 冲突频繁 | 多人修改同一文件 | 加强模块解耦、小 PR 频繁合并 |
| 提交历史混乱 | 无规范约束 | 实施 commitlint + PR 策略强制 |
| 发布分支忘记合并回 dev | 流程缺失 | 建立发布检查清单 |
| hotfix 只修了 main 没修 dev | 流程疏忽 | 在 hotfix SOP 中强制同步 dev |
| 多人 PR 互相阻塞 | 依赖未解耦 | 接口先行，实现后补 |

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- Git版本控制高效管理 - 豆包整理 — 关联

### 外部资料引用

- 来源: [团队 Git 开发协作规范指引 - cnblogs](https://www.cnblogs.com/everfight/p/19805285)
- 来源: [小作坊 GitHub 协作闭环实战指南 - cnblogs](https://www.cnblogs.com/FreakEmbedded/p/19837373)
- 来源: [GitHub Flow 官方文档](https://docs.github.com/en/get-started/using-github/github-flow)
- 来源: --

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
