# GitLab 集成与自动化

> **概要**: GitLab集成与自动化，涵盖WebHook、Jenkins集成、CI/CD与GitOps实践
>
> **关键词**: GitLab · WebHook · Jenkins · GitLab CI · GitOps

---

## 📑 目录

- [一、GitLab WebHook 配置与集成](#一gitlab-webhook-配置与集成)
  - [1.1 配置入口](#11-配置入口)
  - [1.2 WebHook 核心 Payload 字段](#12-webhook-核心-payload-字段)
- [二、GitLab + Jenkins 集成](#二gitlab-jenkins-集成)
  - [2.1 前置准备](#21-前置准备)
  - [2.2 自由风格项目配置](#22-自由风格项目配置)
  - [2.3 Pipeline（Jenkinsfile）方式](#23-pipelinejenkinsfile方式)
  - [2.4 手动调用 API 回写状态](#24-手动调用-api-回写状态)
- [三、GitLab Notes 折叠实现](#三gitlab-notes-折叠实现)
  - [3.1 原理](#31-原理)
  - [3.2 格式模板](#32-格式模板)
  - [执行结果](#执行结果)
  - [3.3 API 调用写入](#33-api-调用写入)
- [四、GitLab CI/CD 基础配置](#四gitlab-cicd-基础配置)
  - [4.1 基本流水线](#41-基本流水线)
  - [4.2 流水线触发规则](#42-流水线触发规则)
- [五、GitLab CI 与 GitOps 集成](#五gitlab-ci-与-gitops-集成)
  - [5.1 MR 自动部署环境](#51-mr-自动部署环境)
  - [5.2 自动打 Tag 与 Release](#52-自动打-tag-与-release)
- [六、GitLab vs GitHub 核心差异](#六gitlab-vs-github-核心差异)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

**交叉引用**: [GitHub Actions CI/CD](2026-06-29-github-actions-cicd.md) | [分支策略与团队协作规范](2026-06-29-git-branch-strategy-and-standards.md) | [Git + AI 集成方案](2026-06-29-git-ai-integration.md)

---

## 一、GitLab WebHook 配置与集成

### 1.1 配置入口

项目/群组 → 设置 → 集成 → WebHook

| 参数 | 配置值 |
|:-----|:--------|
| **URL** | AI CodeReview 服务的公网接口 |
| **触发事件** | Merge request events + Push events |
| **Secret Token** | 自定义密钥，校验请求来源防伪造 |
| **SSL 校验** | 生产环境强制开启 |
| **内容格式** | `application/json` |

### 1.2 WebHook 核心 Payload 字段

```json
{
  "object_kind": "merge_request",
  "object_attributes": {
    "diff": "--- a/src/main.py\n+++ b/src/main.py\n@@ -1,5 +1,7 @@",
    "iid": 123,
    "source_branch": "feature/login",
    "target_branch": "main"
  },
  "project": {
    "id": 456,
    "git_url": "git@gitlab.example.com:group/repo.git"
  }
}
```

| 字段 | 用途 |
|:-----|:------|
| `object_kind` | 区分 `merge_request` 还是 `push` 事件 |
| `object_attributes.diff` | 本次变更的代码 Diff 片段 |
| `project.id` | 项目 ID，用于 API 调用 |
| `git_url` | 仓库克隆地址，拉取完整代码 |
| `iid` | MR 编号，用于后续回写评论 |

---

## 二、GitLab + Jenkins 集成

### 2.1 前置准备

```bash
# 1. Jenkins 安装 GitLab Plugin
# 2. GitLab 生成 Personal Access Token（权限: api + read/write repository）
# 3. Jenkins → 系统配置 → GitLab → 添加 GitLab Server
#    - URL: https://gitlab.example.com
#    - Credentials: GitLab API Token
```

### 2.2 自由风格项目配置

**源码管理**：选择 Git → 仓库 URL → GitLab 凭证

**构建触发器**：

- 勾选 "Build when a change is pushed to GitLab"
- 配置 Secret Token 和触发事件（Push/MR）

**构建后操作**：

```text
Add post-build action -> Publish build status to GitLab
  - Name: jenkins (自定义标识)
  - State: 自动 (pending -> success/failed)
  - Target URL: ${BUILD_URL}
```

### 2.3 Pipeline（Jenkinsfile）方式

```groovy
pipeline {
    agent any

    options {
        gitLabConnection('my-gitlab')
    }

    stages {
        stage('Build') {
            steps {
                echo 'Building...'
                // 构建过程
            }
        }
        stage('Test') {
            steps {
                echo 'Testing...'
                // 测试过程
            }
        }
    }

    post {
        success {
            updateGitlabCommitStatus name: 'jenkins', state: 'success'
        }
        failure {
            updateGitlabCommitStatus name: 'jenkins', state: 'failed'
        }
    }
}
```

### 2.4 手动调用 API 回写状态

```bash
# 更新 Commit 状态
curl --request POST \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  --header "Content-Type: application/json" \
  --data '{"state": "success", "target_url": "https://jenkins.example.com/job/1"}' \
  "https://gitlab.example.com/api/v4/projects/:id/statuses/:commit_sha"
```

---

## 三、GitLab Notes 折叠实现

### 3.1 原理

GitLab Notes 支持 `<details> + <summary>` HTML 标签，外部 WebHook 写入 Note 时包装成折叠格式即可。

### 3.2 格式模板

```html
<details>
<summary>🔍 查看详细内容</summary>

### 执行结果
- 状态：成功
- 耗时：2.3s

```json
{"foo": "bar", "data": [1, 2, 3]}
```

</details>
```

**关键要点**：

- `<summary>` 后**必须空一行**，否则内容渲染异常
- 支持嵌套折叠
- 支持代码块、日志、长文本折叠
- 支持 Markdown 渲染

### 3.3 API 调用写入

```bash
# 创建 Issue/MR 评论
curl --request POST \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  --header "Content-Type: application/json" \
  --data '{
    "body": "<details>\n<summary>🔍 代码审查报告</summary>\n\n### 发现的问题\n- 共发现 3 个问题\n- 2 个警告，1 个严重\n\n```\nWARNING: 未处理的异常\nERROR: SQL注入风险\n```\n\n</details>"
  }' \
  "https://gitlab.example.com/api/v4/projects/:id/merge_requests/:iid/notes"
```

---

## 四、GitLab CI/CD 基础配置

### 4.1 基本流水线

```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - deploy

variables:
  DOCKER_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA

build:
  stage: build
  image: node:20
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/

test:
  stage: test
  image: node:20
  script:
    - npm ci
    - npm test
    - npm run lint
  coverage: /All files[|]\s*([\d.]+)/

deploy:
  stage: deploy
  image: alpine:latest
  script:
    - apk add --no-cache openssh-client
    - scp -r dist/ user@server:/app/
  only:
    - main
  environment:
    name: production
    url: https://example.com
```

### 4.2 流水线触发规则

```yaml
# 仅当特定路径变更时触发
build:
  only:
    changes:
      - src/**/*
      - package.json
      - Dockerfile

# 排除某些路径
test:
  except:
    changes:
      - docs/**/*
      - README.md
```

---

## 五、GitLab CI 与 GitOps 集成

### 5.1 MR 自动部署环境

```yaml
review:
  stage: deploy
  script:
    - kubectl apply -f k8s/
  environment:
    name: review/$CI_MERGE_REQUEST_IID
    on_stop: stop_review
  only:
    - merge_requests

stop_review:
  stage: deploy
  script:
    - kubectl delete -f k8s/
  when: manual
  environment:
    name: review/$CI_MERGE_REQUEST_IID
    action: stop
  only:
    - merge_requests
```

### 5.2 自动打 Tag 与 Release

```yaml
release:
  stage: deploy
  script:
    - echo "Creating release $CI_COMMIT_TAG..."
  release:
    name: "Release $CI_COMMIT_TAG"
    description: "生成变更说明"
    tag_name: $CI_COMMIT_TAG
  only:
    - tags
```

---

## 六、GitLab vs GitHub 核心差异

| 维度 | GitLab | GitHub |
|:-----|:-------|:-------|
| 部署方式 | 自托管/SaaS | 仅 SaaS |
| CI/CD | 内置 CI/CD（.gitlab-ci.yml） | GitHub Actions |
| 免费私有仓库 | 无限制 | 无限制 |
| Pages 静态站点 | 支持 | 支持 |
| 内置容器注册表 | 支持 | 需 GitHub Packages |
| 评审能力 | 代码所有者 + 审批规则 | CODEOWNERS + 分支规则 |
| 项目规划 | 史诗/里程碑/看板 | Projects (Beta) |
| 安全扫描 | 内置 SAST/容器扫描 | 高级版支持 |
| 最大文件限制 | CI 运行器配置 | 100MB（推荐 Git LFS） |

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- GitLab WebHook + AI CodeReview 集成 - 豆包整理 — 关联
- Jenkins 回写 GitLab 状态 - 豆包整理 — 关联
- GitLab Notes 折叠实现 - 豆包整理 — 关联

### 外部资料引用

- 来源: [GitLab CI/CD 官方文档](https://docs.gitlab.com/ee/ci/)
- 来源: [windows 装 gitlab 服务器 - cnblogs](https://www.cnblogs.com/windows装gitlab服务器)
- 来源: --

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
