# Git 提交信息规范与校验工具

> **概要**: Git提交信息规范与校验工具，涵盖语义化提交、版本号、Tag管理及自动校验
>
> **关键词**: Git提交规范 · 语义化版本 · commitlint · husky · CHANGELOG

---

## 📑 目录

- [一、语义化提交信息规范](#一语义化提交信息规范)
  - [1.1 标准格式](#11-标准格式)
  - [1.2 类型定义](#12-类型定义)
  - [1.3 优秀示例](#13-优秀示例)
  - [1.4 常见错误示例](#14-常见错误示例)
- [二、语义化版本号（SemVer）](#二语义化版本号semver)
  - [2.1 标准格式](#21-标准格式)
  - [2.2 扩展标签](#22-扩展标签)
- [三、Tag 标签管理规范](#三tag-标签管理规范)
- [四、自动校验工具](#四自动校验工具)
  - [4.1 gitru（Rust 零依赖）](#41-gitrurust-零依赖)
  - [4.2 commitlint + husky（Node.js 生态）](#42-commitlint-huskynodejs-生态)
  - [4.3 pre-commit 框架（多语言通用）](#43-pre-commit-框架多语言通用)
- [五、CHANGELOG 自动生成](#五changelog-自动生成)
  - [5.1 standard-version](#51-standard-version)
  - [5.2 semantic-release（全自动化）](#52-semantic-release全自动化)
- [六、综合落地建议](#六综合落地建议)
  - [团队落地步骤](#团队落地步骤)
  - [企业级提交规范总表](#企业级提交规范总表)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

**交叉引用**: [分支策略与团队协作规范](2026-06-29-git-branch-strategy-and-standards.md) | [Git + AI 集成方案](2026-06-29-git-ai-integration.md) | [GitHub Actions CI/CD](2026-06-29-github-actions-cicd.md)

---

## 一、语义化提交信息规范

### 1.1 标准格式

```text
<类型>(模块): <简短描述>

<详细说明（可选）>

<关联工单/需求ID>
```

### 1.2 类型定义

| 类型 | 说明 | 是否影响版本号 |
|:-----|:------|:--------------|
| `feat` | 新功能 | 次版本+ |
| `fix` | 缺陷修复 | 补丁版本+ |
| `refactor` | 代码重构，无功能变化 | 否 |
| `docs` | 文档修改 | 否 |
| `style` | 格式、空格、注释调整 | 否 |
| `test` | 新增/修改测试用例 | 否 |
| `chore` | 构建、CI、依赖、工具调整 | 否 |
| `perf` | 性能优化 | 否 |
| `improvement` | 已有功能增强 | 否 |
| `revert` | 回滚 | 否 |
| `ci` | CI 配置变更 | 否 |

### 1.3 优秀示例

```text
feat(user): 完成用户登录功能 #T123

实现邮箱+密码登录、微信扫码登录
- 新增登录接口 /api/v1/login
- 新增 token 刷新机制
- 新增登录日志记录

关联需求: T123
```

```text
fix(payment): 修复支付回调验签失败 #BUG-567

支付宝异步通知验签因时间戳格式不一致失败
统一为 UTC ISO8601 格式
```

```text
refactor(core): 重构缓存模块，抽离为独立服务

将内嵌缓存逻辑抽离为独立 CacheService
- 支持 Redis/Memory 双后端
- 统一过期策略接口
- 不影响现有业务逻辑
```

### 1.4 常见错误示例

| 错误示例 | 问题 | 正确写法 |
|:---------|:-----|:---------|
| `fix` | 无描述 | `fix: 修复支付回调验签失败` |
| `修改了很多东西` | 模糊 | 按模块拆分多个 commit |
| `feat: 改了登录和支付` | 一个 commit 做两件事 | 拆为两个 commit |
| `修复bug` | 无关联信息 | `fix: 修复登录验证码超时 #BUG-567` |
| `Merge branch` | 自动生成的合并信息应重写 | `chore: 合并 feature/payment 到 dev` |

---

## 二、语义化版本号（SemVer）

### 2.1 标准格式

```text
主版本.次版本.补丁版本
X.Y.Z
```

| 版本位 | 变更场景 | 示例 |
|:-------|:---------|:-----|
| **X** 主版本 | 不兼容 API/架构重构/重大变更 | `v2.0.0` |
| **Y** 次版本 | 新增功能，向下兼容 | `v1.3.0` |
| **Z** 补丁版本 | Bug 修复、小优化 | `v1.3.1` |

### 2.2 扩展标签

```text
v2.1.0-alpha.1    # 内测版
v2.1.0-beta.2     # 公测版
v2.1.0-rc.3       # 候选发布版
v2.0.1-hotfix1    # 线上紧急修复
v2.1.0-SNAPSHOT   # 开发快照版
```

---

## 三、Tag 标签管理规范

```text
# 创建（推荐附注标签）
git tag -a v1.2.0 -m "版本 v1.2.0: 新增支付模块、优化缓存性能"
git push origin v1.2.0

# 查看
git tag -l 'v1.*'              # 按模式搜索
git show v1.2.0                # 查看标签详情

# 从标签创建分支（回滚/热修）
git checkout -b hotfix/v1.2.0-hotfix1 v1.2.0
```

**核心原则**：

1. **仅在稳定可发布节点打 Tag**，禁止随意删除/修改
2. 格式统一：`vX.Y.Z`
3. 每个 Tag 对应一条 CHANGELOG 记录
4. 禁止强制推送 Tag（`git push --force --tags` 是重罪）

---

## 四、自动校验工具

### 4.1 gitru（Rust 零依赖）

**简介**：基于 Rust 编写的零依赖 Git commit-msg Hook 校验工具，单二进制分发，无需 Node/Python。

**安装**：

```bash
# 从 crates.io 安装
cargo install gitru

# 或下载预编译二进制
wget https://github.com/...gitru-linux-x86_64 -O /usr/local/bin/gitru
chmod +x /usr/local/bin/gitru
```

**配置 `.gitru.toml`**：

```toml
[commit]
# 必需前缀
prefixes = ["feat", "fix", "refactor", "docs", "style", "test", "chore", "perf", "ci"]
# 分隔符
separator = ": "
# 最大行长度
max_subject_length = 72
max_body_line_length = 80
# 模块列表（可选校验）
scopes = ["user", "payment", "core", "admin"]

[skip]
# 通过关键字跳过校验（用于自动化提交/紧急修复）
keywords = ["WIP", "SKIP_CI", "AUTO_COMMIT"]

[i18n]
# 中文支持，不会误判中文标点
support_chinese = true
```

**安装到 Git Hook**：

```bash
# 在项目根目录
gitru init
# 或手动创建 .git/hooks/commit-msg
echo 'gitru "$1"' > .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
```

**特点**：

- 🦀 Rust 编写，零依赖二进制分发
- ⚙️ TOML 格式自定义规则
- ⏭️ 支持关键字跳过校验
- 🇨🇳 支持中文提交信息校验
- 🎨 错误信息带颜色输出

### 4.2 commitlint + husky（Node.js 生态）

```bash
# 安装
npm install --save-dev @commitlint/cli @commitlint/config-conventional husky

# 配置 commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'scope-enum': [2, 'always', ['user', 'payment', 'core', 'admin']],
    'subject-case': [0],  # 不限制大小写
  }
}

# 配置 husky
npx husky install
npx husky add .husky/commit-msg 'npx --no-install commitlint --edit "$1"'
```

### 4.3 pre-commit 框架（多语言通用）

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
  - repo: https://github.com/commitizen-tools/commitizen
    rev: v3.13.0
    hooks:
      - id: commitizen
```

---

## 五、CHANGELOG 自动生成

### 5.1 standard-version

```bash
npm install --save-dev standard-version

# 在 package.json 添加脚本
# "release": "standard-version"
npm run release         # 自动升级版本 + 生成 CHANGELOG + 打 Tag
npm run release -- --first-release  # 首次发布
npm run release -- --prerelease alpha  # 预发布
```

### 5.2 semantic-release（全自动化）

```bash
npm install --save-dev semantic-release @semantic-release/git

# 配合 CI 自动执行（GitHub Actions 示例）
# .github/workflows/release.yml
```

**核心能力**：

- 根据 commit 类型自动升级版本号
- 自动生成 CHANGELOG
- 自动打 Tag 并推送
- 自动发布到 npm/GitHub Release

---

## 六、综合落地建议

### 团队落地步骤

1. **Day 1**：统一提交格式规范（召集全员培训）
2. **Day 3**：部署 gitru 或 commitlint（强制校验）
3. **Week 1**：推行 PR Squash and Merge 策略
4. **Week 2**：接入 standard-version / semantic-release
5. **Week 3**：复盘优化（根据团队反馈调整规则）

### 企业级提交规范总表

| 场景 | 提交信息 | 类型 |
|:-----|:---------|:-----|
| 新开发功能 | `feat: 用户登录功能` | 次版本 |
| 修复 bug | `fix: 修复登录超时` | 补丁版 |
| 紧急线上修复 | `fix: 紧急修复支付崩溃 #BUG-888` | hotfix |
| 代码重构 | `refactor: 重构缓存模块` | 不变 |
| 修改文档 | `docs: 更新 API 文档` | 不变 |
| 修改依赖 | `chore: 升级 Spring Boot 版本` | 不变 |
| 性能优化 | `perf: 优化页面首屏加载` | 补丁版 |
| 回滚 | `revert: 回滚支付模块修改` | 补丁版 |

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- Git版本控制高效管理 - 豆包整理 — 关联

### 外部资料引用

- 来源: [gitru：Rust 零依赖 Git 提交信息校验工具 - cnblogs](https://www.cnblogs.com/xiyixiaodao/p/19772549)
- 来源: [Conventional Commits 规范](https://www.conventionalcommits.org/)
- 来源: [SemVer 语义化版本规范](https://semver.org/)
- 来源: --

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
