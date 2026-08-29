# GitHub Actions CI/CD 最佳实践

> **概要**: GitHub Actions CI/CD最佳实践，含多环境配置、矩阵构建与安全实践
>
> **关键词**: GitHub Actions · CI/CD · Workflow · 矩阵构建 · Secrets

---

## 📑 目录

- [一、核心概念](#一核心概念)
  - [基本工作流示例](#基本工作流示例)
- [二、小型网站完整 CI/CD 架构](#二小型网站完整-cicd-架构)
  - [2.1 架构总览](#21-架构总览)
  - [2.2 生产级部署配置](#22-生产级部署配置)
  - [2.3 必需 Secrets 配置](#23-必需-secrets-配置)
- [三、多环境 CI/CD 配置](#三多环境-cicd-配置)
  - [3.1 测试环境](#31-测试环境)
  - [3.2 预发布环境](#32-预发布环境)
  - [3.3 生产环境](#33-生产环境)
- [四、常见踩坑与解决方案](#四常见踩坑与解决方案)
- [五、高级技巧](#五高级技巧)
  - [5.1 矩阵构建（多版本测试）](#51-矩阵构建多版本测试)
  - [5.2 缓存依赖加速](#52-缓存依赖加速)
  - [5.3 定时任务](#53-定时任务)
  - [5.4 条件执行](#54-条件执行)
  - [5.5 自定义环境变量](#55-自定义环境变量)
- [六、安全最佳实践](#六安全最佳实践)
- [七、本地测试 Actions](#七本地测试-actions)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

**交叉引用**: [分支策略与团队协作规范](2026-06-29-git-branch-strategy-and-standards.md) | [GitLab 集成与自动化](2026-06-29-gitlab-integration-automation.md) | [提交信息规范与校验](2026-06-29-git-commit-convention-and-validation.md)

---

## 一、核心概念

| 概念 | 说明 |
|:-----|:------|
| **Workflow（工作流）** | 一个 YAML 文件，放在 `.github/workflows/` 下 |
| **Job（作业）** | 工作流中的一个任务单元，默认并行执行 |
| **Step（步骤）** | Job 中的最小执行单元（运行命令/使用 Action） |
| **Action（动作）** | 可复用的 GitHub Actions 模块 |
| **Runner（运行器）** | 执行工作流的虚拟机 |
| **Event（事件）** | 触发工作流的条件（push、PR、定时等） |

### 基本工作流示例

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: 安装依赖
        run: npm ci

      - name: 运行测试
        run: npm test

      - name: 构建
        run: npm run build
```

---

## 二、小型网站完整 CI/CD 架构

### 2.1 架构总览

```text
git push origin main
        v
GitHub 检测到代码变更
        v
自动 SSH 到生产服务器
        v
执行 git pull + docker compose up -d --build
        v
服务器容器自动更新
```

### 2.2 生产级部署配置

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]
  workflow_dispatch:    # 支持手动触发

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: 运行测试
        run: |
          npm ci
          npm test
          npm run lint

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: 构建 Docker 镜像
        run: docker build -t myapp:${{ github.sha }} .

      - name: 推送到镜像仓库
        run: |
          docker tag myapp:${{ github.sha }} ghcr.io/${{ github.repository }}:latest
          docker push ghcr.io/${{ github.repository }}:latest

      - name: 远程部署
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.DEPLOY_HOST }}
          username: ${{ secrets.DEPLOY_USER }}
          key: ${{ secrets.DEPLOY_KEY }}
          script: |
            cd /app
            docker compose pull
            docker compose up -d --build
            docker system prune -f
```

### 2.3 必需 Secrets 配置

在 GitHub 仓库 Settings → Secrets and variables → Actions 中设置：

| Secret 名称 | 用途 |
|:------------|:------|
| `DEPLOY_HOST` | 服务器 IP/域名 |
| `DEPLOY_USER` | SSH 用户名 |
| `DEPLOY_KEY` | SSH 私钥 |
| `DOCKER_USERNAME` | 镜像仓库用户名 |
| `DOCKER_TOKEN` | 镜像仓库 Token |

---

## 三、多环境 CI/CD 配置

### 3.1 测试环境

```yaml
name: CI

on:
  pull_request:
    branches: [main, dev]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: 代码质量检查
        run: |
          npm run lint
          npm run type-check
      - name: 单元测试
        run: npm run test:coverage
      - name: 构建验证
        run: npm run build
```

### 3.2 预发布环境

```yaml
name: Staging Deploy

on:
  push:
    branches: [dev]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - name: 构建 & 部署到预发布
        run: |
          docker build -t myapp:staging .
          # 部署到 staging 服务器...
```

### 3.3 生产环境

```yaml
name: Production Deploy

on:
  release:
    types: [published]

jobs:
  deploy-production:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - name: 生成版本 Tag
        run: echo "RELEASE_TAG=${GITHUB_REF#refs/tags/}" >> $GITHUB_ENV
      - name: 构建 & 部署
        run: |
          docker build -t myapp:${{ env.RELEASE_TAG }} .
          # 部署到生产服务器...
```

---

## 四、常见踩坑与解决方案

| 问题 | 原因 | 解决方案 |
|:-----|:------|:---------|
| **SSH 连接超时** | 服务器防火墙未放行 Actions IP | 使用 `nektos/act` 本地测试，或配置白名单 |
| **Secrets 为空** | 未正确设置仓库 Secrets | 检查 Settings → Secrets → Actions |
| **Docker 构建缓存失效** | 每次从头构建 | 启用 `docker/build-push-action` 的 cache-from |
| **Runner 磁盘空间不足** | Actions 默认 14GB 磁盘 | 清理步骤：`docker system prune -f` |
| **Workflow 不触发** | 分支/路径过滤不匹配 | 检查 `on.push.paths-ignore` 配置 |
| **Permission denied** | SSH 密钥权限 | `chmod 600` 私钥，确认公钥已添加到服务器 |

---

## 五、高级技巧

### 5.1 矩阵构建（多版本测试）

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node: [18, 20, 22]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
      - run: npm ci && npm test
```

### 5.2 缓存依赖加速

```yaml
- name: 缓存 npm
  uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

### 5.3 定时任务

```yaml
on:
  schedule:
    - cron: '0 2 * * *'    # 每天 UTC 2:00（北京时间 10:00）
  workflow_dispatch:         # 支持手动触发
```

### 5.4 条件执行

```yaml
- name: 仅当 main 分支执行
  if: github.ref == 'refs/heads/main'
  run: echo "Deploying to production"

- name: 仅在 PR 中执行
  if: github.event_name == 'pull_request'
  run: echo "Running PR checks"
```

### 5.5 自定义环境变量

```yaml
env:
  NODE_ENV: production
  API_URL: ${{ secrets.API_URL }}

jobs:
  build:
    env:
      NODE_OPTIONS: --max_old_space_size=4096
    steps:
      - run: echo $API_URL
```

---

## 六、安全最佳实践

1. **不要直接在 YAML 中写敏感信息**，全部使用 `${{ secrets.XXX }}`
2. **限制触发分支**：只在 `main`/`dev` 等受控分支触发生产部署
3. **使用 `actions/checkout` 的 `persist-credentials: false`** 避免 Token 泄露
4. **最小权限原则**：使用 `pull_request: write` 而非默认 Token
5. **定期轮换 Secrets**
6. **启用 OIDC** 替代长期密钥

```yaml
- uses: actions/checkout@v4
  with:
    persist-credentials: false    # 安全实践
```

---

## 七、本地测试 Actions

使用 [`nektos/act`](https://github.com/nektos/act) 在本地运行 Actions：

```bash
# 安装
brew install act

# 运行所有 workflow
act

# 运行特定 job
act -j build

# 模拟 push 事件
act push

# 使用特定 secret 文件
act --secret-file .secrets
```

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- [分支策略与团队协作规范](2026-06-29-git-branch-strategy-and-standards.md) — 关联
- [GitLab 集成与自动化](2026-06-29-gitlab-integration-automation.md) — 关联
- [提交信息规范与校验](2026-06-29-git-commit-convention-and-validation.md) — 关联

### 外部资料引用

- 来源: [GitHub Actions 在小型网站的最佳实践 - cnblogs](https://www.cnblogs.com/pronting/p/20074792)
- 来源: [GitHub Actions 官方文档](https://docs.github.com/en/actions)
- 来源: [nektos/act - 本地运行 GitHub Actions](https://github.com/nektos/act)
- 来源: --

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
