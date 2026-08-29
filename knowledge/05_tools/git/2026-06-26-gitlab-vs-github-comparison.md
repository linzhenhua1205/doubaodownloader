# GitLab vs GitHub 全面功能对比（2026）

> **概要**: GitLab与GitHub全面功能对比（2026），含代码托管、CI/CD、安全与选型建议
>
> **关键词**: GitLab · GitHub · 功能对比 · CI/CD · 选型建议

---

## 📑 目录

- [一、核心定位差异](#一核心定位差异)
- [二、代码托管](#二代码托管)
- [三、PR/MR](#三prmr)
- [四、CI/CD](#四cicd)
- [五、安全](#五安全)
- [六、项目管理](#六项目管理)
- [七、GitLab GLQL（GitLab Query Language）](#七gitlab-glqlgitlab-query-language)
- [八、Deploy 模式](#八deploy-模式)
- [九、GitLab GLFM vs GitHub GFM (Markdown)](#九gitlab-glfm-vs-github-gfm-markdown)
- [十、选型建议](#十选型建议)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

---

## 一、核心定位差异

| 维度 | GitHub | GitLab |
|:-----|:-------|:-------|
| **定位** | 全球最大代码托管 + 开源协作社区 + CI/CD 市场 | 一体化 DevSecOps 平台，全链路内置 |
| **商业模式** | SaaS 第一，GitHub Enterprise Server 第二 | Self-hosted / SaaS 同等重要 |
| **核心优势** | 社区生态、Actions 市场、Copilot AI | 完整内置（含安全扫描/制品仓库/项目管理） |
| **AI 能力** | Copilot（代码补全 + 聊天 + PR 总结） | GitLab Duo（AI 辅助代码审查/CI 调试/安全分析） |
| **开源** | 平台闭源，Actions 运行器开源 | CE 版开源，EE 版商业 |

---

## 二、代码托管

| 功能 | GitHub | GitLab |
|:-----|:-------|:-------|
| 仓库类型 | Public + Private + Internal | Public + Private + Internal |
| 仓库大小限制 | SaaS: 5GB（推荐），软限制 | SaaS: 10GB，Enterprise: 无限制 |
| 单文件大小限制 | 100MB（Git 限制 + 规则） | 100MB（Git 限制），LFS 支持 |
| LFS 支持 | ✅ Git LFS | ✅ Git LFS |
| Protected Branches | ✅ 规则丰富 | ✅ 规则更细致（含 deploy keys） |
| Code Owners | ✅ | ✅ |
| Submodule 支持 | ✅ 原生 | ✅ 原生 |
| 镜像仓库 | ✅ 手动/自动 | ✅ 内建镜像同步 |

---

## 三、PR/MR

| 功能 | GitHub (Pull Request) | GitLab (Merge Request) |
|:-----|:----------------------|:-----------------------|
| 行内评论 | ✅ 原生 | ✅ 原生（DiffNote API） |
| 草稿 PR | ✅ Draft PR | ✅ Draft MR |
| 合并策略 | Merge Commit / Squash / Rebase | Merge Commit / Squash / Rebase / Fast-forward |
| 合入门禁 | ✅ 检查清单 | ✅ Pipelines must succeed / Approvals |
| 自动合并 | ✅ Auto-merge | ✅ Merge when pipeline succeeds |
| 代码所有者审核 | ✅ CODEOWNERS | ✅ CODEOWNERS + 可选 approval rules |
| PR 模板 | ✅ .github/PULL_REQUEST_TEMPLATE.md | ✅ .gitlab/merge_request_templates/ |
| 依赖 PR | ✅ Dependabot | ✅ GitLab Dependency Bot |
| **Cherry-pick** | ✅ 网页端一键 | ✅ 网页端一键 + 追踪 |

---

## 四、CI/CD

| 功能 | GitHub Actions | GitLab CI/CD |
|:-----|:---------------|:-------------|
| **定义文件** | `.github/workflows/*.yml` | `.gitlab-ci.yml` |
| **配置复杂度** | 较低，YAML 简洁 | 中等，功能更丰富 |
| **市场/模板** | ✅ 大型 Actions 市场 | ✅ 内置模板库 |
| **矩阵构建** | ✅ `strategy.matrix` | ✅ `parallel:matrix` |
| **手动审批** | ✅ `environment` + 审批 | ✅ 多环境手动部署 |
| **Runner** | GitHub-hosted / Self-hosted | GitLab-hosted / Self-hosted / 共享 Runner |
| **缓存** | ✅ Actions Cache | ✅ CI Cache |
| **Artifacts** | ✅ | ✅ + 制品仓库(内建) |
| **Pages 部署** | ✅ GitHub Pages | ✅ GitLab Pages |
| **无服务器部署** | 有限 | 内建多环境 |

---

## 五、安全

| 功能 | GitHub | GitLab |
|:-----|:-------|:-------|
| 依赖扫描 | ✅ Dependabot + Advisory DB | ✅ Dependency Scanning |
| 密钥检测 | ✅ Secret Scanning | ✅ Secret Detection |
| SAST | ✅ Code Scanning (CodeQL) | ✅ SAST (多引擎) |
| DAST | ✅ | ✅ DAST |
| 容器扫描 | ✅ | ✅ Container Scanning |
| 许可证合规 | ✅ | ✅ License Compliance |
| **安全仪表盘** | 有限 | ✅ 内建安全仪表盘 |
| Fuzzing | ❌ | ✅ Coverage-guided Fuzzing |

---

## 六、项目管理

| 功能 | GitHub | GitLab |
|:-----|:-------|:-------|
| Issue/Board | ✅ Issues + Projects | ✅ Issues + Boards + Epics |
| Milestones | ✅ | ✅ |
| Roadmap | ❌ | ✅ (GitLab Ultimate) |
| 时间追踪 | ❌ | ✅ Time Tracking |
| 看板视图 | ✅ Projects (Table/Board) | ✅ Boards + 多视图 |
| Wiki | ✅ 独立 Wiki 仓库 | ✅ 独立 Wiki 仓库 |
| 服务台 | ❌ | ✅ Service Desk |
| **GLQL** | ❌ | ✅ GitLab Query Language |

---

## 七、GitLab GLQL（GitLab Query Language）

- **一种内置查询语言**，用于在 GitLab 中搜索 Issue / MR / Epic
- 处于 Beta 阶段
- 语法示例: `type:issue label:~bug milestone:"v1.0"`
- 相比 GitHub Search 更结构化，但 UI 搜索功能仍在完善中

---

## 八、Deploy 模式

| 模式 | GitHub | GitLab |
|:-----|:-------|:-------|
| SaaS | github.com | gitlab.com |
| 自托管 | GitHub Enterprise Server | GitLab CE / EE |
| Kubernetes 部署 | ❌ | ✅ GitLab Helm Chart |
| 高可用方案 | Active/Active (GHES 3.x) | DRBD+Pacemaker / 原生 HA |
| 地理分布 | ❌ (Enterprise 有限) | ✅ Geo Replication |

---

## 九、GitLab GLFM vs GitHub GFM (Markdown)

```text
GLFM = CommonMark + GFM + GitLab 专属扩展
GFM  = CommonMark + GitHub 扩展
```

| 差异 | GLFM | GFM |
|:-----|:-----|:-----|
| 基础 | CommonMark | CommonMark |
| 任务列表 | ✅ `- [ ]` | ✅ `- [ ]` |
| Mermaid 图表 | ✅ 内建 | ✅ 内建 |
| Math | ✅ `$...$` / `$$...$$` | ✅ `$...$` / `$$...$$` |
| 自动链接 | ✅ `#123` → Issue | ✅ `#123` → Issue |
| GLQL 块 | ✅ ````glql ...```` | ❌ |
| 表格增强 | ✅ 更多格式支持 | 标准表格 |
| 折叠 | ✅ `<details>` | ✅ `<details>` |

---

## 十、选型建议

| 场景 | 推荐 |
|:-----|:-----|
| 开源项目、社区协作 | **GitHub**（社区生态最强） |
| 企业内部 DevSecOps 一体化 | **GitLab**（安全/CI/PM 全内置） |
| 需要自托管 + 高可用 | **GitLab**（CE 开源 + HA 方案成熟） |
| AI 编程辅助 | **GitHub**（Copilot 生态成熟） |
| 合规要求严格的行业 | **GitLab**（完整安全工具链） |
| CI/CD 需要丰富的市场插件 | **GitHub Actions**（市场最大） |
| 同时需要 Git + Wiki 文档 | 两者均可，GLFM+GLQL 略灵活 |

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- (无)

### 外部资料引用

- 来源: 豆包对话 + 官方文档提炼

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
