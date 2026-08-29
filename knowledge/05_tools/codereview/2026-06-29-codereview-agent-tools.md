# CodeReview 智能体与工具链

> **概要**: CodeReview智能体与工具链介绍，涵盖CodeReview Agent、腾讯WorkBuddy、Antigravity Skills等方案
>
> **关键词**: CodeReview Agent · WorkBuddy · 智能体 · CLI工具 · 跨语言审查

---

## 📑 目录

- [一、CodeReview Agent（开源 CLI 工具）](#一codereview-agent开源-cli-工具)
  - [核心能力](#核心能力)
  - [Agent 友好设计](#agent-友好设计)
  - [部署方式](#部署方式)
- [二、腾讯 WorkBuddy 智能体](#二腾讯-workbuddy-智能体)
  - [落地五步](#落地五步)
  - [核心价值](#核心价值)
- [三、Antigravity Skills 跨语言审查](#三antigravity-skills-跨语言审查)
  - [跨语言审查实战](#跨语言审查实战)
- [四、29 分钟自建开源 CR 工具](#四29-分钟自建开源-cr-工具)
- [五、工具链功能对比矩阵](#五工具链功能对比矩阵)
- [六、选型建议](#六选型建议)
- [七、参考资料](#七参考资料)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

---

## 一、CodeReview Agent（开源 CLI 工具）

> 项目地址：`github.com/wanghenan/codereview-agent`

| 维度 | 详情 |
|:-----|:------|
| **定位** | AI 驱动、面向开发者与 AI Agent 双场景的开源代码审查 CLI 工具 |
| **技术栈** | Python + LangChain + LangGraph |
| **输出格式** | 结构化 JSON（含 schema_version），错误也输出合法 JSON |
| **退出码** | 0=成功无风险 / 1=发现问题 / 2=配置错 / 3=LLM错 / 4=网络错 / 5=未知错 |
| **语言覆盖** | Python/JS/TS/Go/Java/Rust/PHP/C/C++ |
| **LLM 支持** | OpenAI / Anthropic / 智谱 / MiniMax / 阿里云 / DeepSeek |

### 核心能力

1. **智能风险识别**：注入、硬编码密钥、敏感信息泄露等
2. **置信度评分**：每条问题标记 0–100% 置信度，50% 以下建议人工复核
3. **智能修复**：生成修复代码，支持预览/一键应用
4. **自动合并 PR**：审查达标后自动合并
5. **智能缓存**：Patch 规范化，节省 Token
6. **自定义提示词**：适配团队规范
7. **多维度分析**：安全、质量、复杂度、历史趋势

### Agent 友好设计

```json
{
  "schema_version": "1.0",
  "review_summary": {
    "total_issues": 5,
    "critical": 1,
    "warning": 2,
    "suggestion": 2,
    "overall_score": 78
  },
  "issues": [
    {
      "severity": "critical",
      "file": "src/main.py",
      "line": 42,
      "description": "SQL injection risk",
      "confidence": 95,
      "fix_available": true,
      "fix_code": "cursor.execute('SELECT * FROM user WHERE id = ?', (uid,))"
    }
  ]
}
```

### 部署方式

| 方式 | 命令 |
|:-----|:------|
| 本地 CLI | `codereview-agent review --path . --format json` |
| Docker | `docker run -v $(pwd):/code wanghenan/codereview-agent review` |
| GitHub Action | `.github/workflows/codereview.yml` 配置 |
| VS Code 插件 | Inline 提示风险 |

> 📎 详细集成指南 → [GitLab WebHook 集成](2026-06-29-gitlab-webhook-integration.md)

---

## 二、腾讯 WorkBuddy 智能体

> 参考：`import/md/AI_CodeReview智能体搭建_0613195420.md`

| 维度 | 详情 |
|:-----|:------|
| **定位** | 腾讯云 WorkBuddy 平台搭建 AI 智能体，实现自动化 CR |
| **触发方式** | WebHook 监听 GitHub/GitLab PR/MR 事件 |
| **工作模式** | AI 先行 + 人工把关 |

### 落地五步

1. **环境准备**：安装 WorkBuddy 客户端，授权项目与网络权限
2. **定义审查规则**：编写 Skill 文件，明确角色、审查范围、输出格式
3. **接入代码仓库**：配置 JSON 对接 GitHub/GitLab，设置触发条件与阈值
4. **搭建反馈闭环**：YAML 配置自动评论、IM 通知、打标签
5. **持续优化**：复盘误报/漏报，调整规则

### 核心价值

- 7×24 自动监听仓库，即时审查
- 按团队规范统一检查安全/性能/规范
- PR 即反馈，降低返工
- 持续学习团队规则

---

## 三、Antigravity Skills 跨语言审查

> 参考：`import/doubao/打造跨语言AI代码审查官.md`（637 行完整方案）

| 维度 | 详情 |
|:-----|:------|
| **定位** | 基于 Antigravity Skills 机制的跨语言 Code Reviewer |
| **核心机制** | Skills = SKILL.md 封装 SOP，AI Agent 自动执行 |
| **安装路径** | 全局级 `~/.gemini/antigravity/skills/<name>/` 或项目级 |

### 跨语言审查实战

| 语言 | 示例审查重点 |
|:-----|:------------|
| Python | 可变默认参数、with 资源管理、导入层级 |
| Java | NullPointerException、线程安全、equals/hashCode |
| Go | goroutine 泄漏、defer 返回值、Context 传递 |
| JavaScript | 类型安全、async 异常处理、内存泄漏 |

---

## 四、29 分钟自建开源 CR 工具

> 参考：`import/md/CodeReview_29分钟开发_0623082321.md`

**核心数据**：

- 开发耗时：29 分钟（两个 AI 协作，零人类编码）
- 审查速度：50 行 ~98ms，3000 行 ~187ms，平均 120ms
- 语言支持：Python/JS/TS/Java/Go/Rust/C++
- 部署特性：零配置、无需密钥/数据库、三条命令本地启动

```bash
# 三行命令启动
git clone https://github.com/xxx/codereview-ai
cd codereview-ai && pip install -r requirements.txt
python app.py  # 启动 9000 端口 Web 服务
```

---

## 五、工具链功能对比矩阵

| 工具 | 定位 | 部署方式 | 审查触发 | 行内评论 | 自动修复 | CI/CD 集成 | 成本 |
|:-----|:-----|:---------|:---------|:---------|:---------|:----------|:-----|
| **CodeReview Agent** | CLI 工具 | 本地/Docker/GitHub Action | 手动/PR 触发 | ✅ | ✅ | ✅ | 仅 LLM 费用 |
| **WorkBuddy 智能体** | 平台级 | 腾讯云托管 | WebHook | ✅ | ❌ | ✅ | 平台订阅费 |
| **Cursor Skills** | IDE 插件 | 内嵌 IDE | 手动/钩子 | ⚠️ 编辑器内 | ✅ | ❌ | Cursor 订阅 |
| **Antigravity Skills** | Agent 框架 | 全局安装 | 隐式/显式触发 | ❌ | ⚠️ | ❌ | 免费 |
| **29min 自建工具** | HTTP 服务 | 本地部署 | HTTP 调用 | ❌ | ⚠️ | ✅ | 仅 LLM 费用 |
| **PR-Agent** | GitHub App | SaaS | PR 自动 | ✅ | ❌ | ✅ | $20~40/人/月 |

---

## 六、选型建议

| 团队类型 | 推荐工具组合 |
|:---------|:------------|
| 小团队探索 | Cursor Skills（本地） + PR-Agent（云上兜底） |
| 中大型团队（内网） | CodeReview Agent（CI/CD） + Cursor Skills（IDE） |
| 使用腾讯云 | WorkBuddy 智能体（平台托管） |
| 极致性价比 | 自建 29min HTTP 服务 + Cursor Skills |
| 高度定制 | CodeReview Agent（自定义 Prompt）+ 自建 GitLab 流水线 |

---

## 七、参考资料

- `import/md/CodeReviewAgent核心总结_*.md`（3个版本）
- `import/md/CodeReview_29分钟开发_0623082321.md`
- `import/md/AI_CodeReview智能体搭建_0613195420.md`
- `import/doubao/打造跨语言AI代码审查官.md`（637行）
- [AI CR 方案全景与选型](2026-06-29-ai-codereview-landscape.md)
- [Cursor CR 实践](2026-06-29-cursor-codereview-practice.md)

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- [GitLab WebHook 集成](2026-06-29-gitlab-webhook-integration.md) — 关联
- [AI CR 方案全景与选型](2026-06-29-ai-codereview-landscape.md) — 关联
- [Cursor CR 实践](2026-06-29-cursor-codereview-practice.md) — 关联

### 外部资料引用

- 来源: import/md/CodeReviewAgent核心总结_*.md`、`import/md/CodeReview_29分钟开发_0623082321.md`、`import/doubao/AI_Code_Review最佳实践3.md`、`import/doubao/打造跨语言AI代码审查官.md`、`import/md/AI_CodeReview智能体搭建_0613195420.md

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
