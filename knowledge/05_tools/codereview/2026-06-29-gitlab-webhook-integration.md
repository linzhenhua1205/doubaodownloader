# GitLab WebHook + AI Code Review 集成方案

> **概要**: GitLab WebHook与AI Code Review集成方案，涵盖架构、Diff提取、LLM评审与结果回写
>
> **关键词**: GitLab · WebHook · AI代码审查 · Diff · LLM评审

---

## 📑 目录

- [一、整体架构](#一整体架构)
- [二、核心流程拆解](#二核心流程拆解)
  - [1. GitLab WebHook 配置](#1-gitlab-webhook-配置)
  - [2. 服务端接收与校验](#2-服务端接收与校验)
  - [3. Diff 提取与上下文补全](#3-diff-提取与上下文补全)
  - [4. LLM 评审 Prompt 组装](#4-llm-评审-prompt-组装)
- [项目技术栈](#项目技术栈)
- [变更 Diff](#变更-diff)
- [函数上下文（Git 补齐）](#函数上下文git-补齐)
- [私有依赖定义（Nexus 补齐）](#私有依赖定义nexus-补齐)
- [评审规则](#评审规则)
- [输出格式](#输出格式)
  - [5. 结果回写 GitLab](#5-结果回写-gitlab)
- [三、工程化优化](#三工程化优化)
- [四、故障场景处理](#四故障场景处理)
- [五、安全规范](#五安全规范)
- [六、最简快速上手](#六最简快速上手)
  - [方案 A：CodeReview Agent（开源，3 分钟）](#方案-acodereview-agent开源3-分钟)
  - [方案 B：自建集成（完整控制）](#方案-b自建集成完整控制)
- [七、参考资料](#七参考资料)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

---

## 一、整体架构

```text
GitLab Server（事件源）
    |
    +- 开发者提交 MR
    +- 开发者推送代码
    |
    v (WebHook POST)
+-----------------------------+
|    消息队列（MQ）              |  <- 异步消费，防 GitLab 超时
+----------+------------------+
           v
+-----------------------------+
|  AI CodeReview 服务          |  <- 解析 Payload、提取 Diff
|  +- Git 拉取完整源码上下文    |
|  +- Nexus 私有依赖查询        |  <- 可选，补齐私有 SDK 定义
|  +- 上下文拼接 -> 调用 LLM    |
+----------+------------------+
           v
+-----------------------------+
|  结果回写 GitLab              |  <- API 行内批注 / 全局评论
+-----------------------------+
```

---

## 二、核心流程拆解

### 1. GitLab WebHook 配置

**配置入口**：项目/群组 → 设置 → 集成 → WebHook

| 参数 | 推荐值 | 说明 |
|:-----|:-------|:------|
| URL | `https://ai-cr.xxx.com/api/gitlab/webhook` | AI 服务暴露的公网/内网接口 |
| Secret Token | 随机 32 位字符串 | 与 AI 工具侧一致，防伪造 |
| 触发事件 | ✅ Merge request events + ✅ Push events | 取消其余无关事件 |
| 内容格式 | `application/json` | 不可切换为表单格式 |
| SSL 验证 | 生产环境开启 | 测试环境可临时关闭 |

### 2. 服务端接收与校验

```python
@app.post("/api/gitlab/webhook")
def gitlab_hook():
    # 1. 密钥鉴权
    req_secret = request.headers.get("X-Gitlab-Token")
    if req_secret != SECRET_TOKEN:
        return {"msg": "非法请求"}, 403

    # 2. 解析 JSON 报文
    payload = request.json
    event_type = payload["object_kind"]

    # 3. 过滤无效事件
    if event_type not in ["merge_request", "push"]:
        return {"msg": "非评审事件，忽略"}, 200

    # 4. 幂等防重（Redis 缓存 MR/Commit ID）
    unique_key = f"{payload['project']['id']}_{payload['object_attributes']['iid']}"
    if redis.exists(unique_key):
        return {"msg": "已处理，跳过"}, 200
    redis.setex(unique_key, 600, "processing")

    # 5. 异步投递 MQ，同步快速返回 200
    mq.send_task(payload)
    return {"code": 0, "msg": "评审任务已接收"}, 200
```

### 3. Diff 提取与上下文补全

**Key Payload 字段**：

| 字段 | 用途 |
|:-----|:------|
| `object_attributes.diff` | 本次变更 Diff（可能截断） |
| `project.git_url` | 仓库地址，用于克隆完整代码 |
| `source_branch / target_branch` | 源/目标分支 |
| `iid` | MR 编号，回写评论用 |

**上下文补全策略**（两层兜底）：

```text
第一层：Diff 足够完整 -> 直接送入 LLM
第二层：Diff 截断 / 需函数上下文 -> Git 拉取完整文件 + 定位函数体
第三层（可选）：需私有 SDK 定义 -> Nexus 查询依赖源代码
```

**Git 拉取上下文**：

```bash
# 基于变更文件路径 + 行号定位完整函数
git clone --depth 1 --branch source_branch repo_url /tmp/repo
cd /tmp/repo
# 读取变更文件，提取函数上下文
sed -n '100,200p' path/to/file.py   # 假设变更行在 100-200
```

**Nexus 依赖查询**：

```python
# 解析项目依赖配置
# pom.xml → Maven, requirements.txt → PyPI, package.json → npm
# 调用 Nexus REST API 获取私有包源码
response = requests.get(f"{nexus_url}/service/rest/v1/search?repository=private-repo&name={package}")
```

### 4. LLM 评审 Prompt 组装

```markdown
## 项目技术栈
{tech_stack}

## 变更 Diff
{diff_content}

## 函数上下文（Git 补齐）
{function_context}

## 私有依赖定义（Nexus 补齐）
{nexus_context}

## 评审规则
请按以下维度逐项检查，输出结构化报告：
1. 安全漏洞（SQL注入/XSS/硬编码密钥/越权）
2. 性能隐患（N+1查询/资源泄漏/同步阻塞）
3. 代码规范（命名/注释/死代码/魔法数字）
4. 业务逻辑（边界条件/竞态条件/异常处理）
5. 测试覆盖（单测完整性/边界测试）

## 输出格式
- 问题级别：[严重/一般/建议]
- 文件：{filename}
- 行号：{line_number}
- 描述：{问题描述}
- 修复建议：{修复示例代码}
```

### 5. 结果回写 GitLab

**全局评论**（MR 底部汇总）：

```text
POST /projects/:id/merge_requests/:merge_request_iid/notes
{
  "body": "## AI CodeReview 报告\n\n**总览**\n- 审查范围：3 文件，45 行变更\n- 严重问题：1 🛑\n- 一般问题：3 ⚠️\n- 建议：5 💡\n\n**详细问题列表**\n..."
}
```

**行内批注**（精确到代码行）：

```text
POST /projects/:id/merge_requests/:merge_request_iid/discussions
{
  "body": "🚨 **安全风险**: 用户输入直接拼接 SQL，存在注入风险\n建议使用参数化查询：`cursor.execute(\"SELECT * FROM user WHERE id = ?\", (uid,))`",
  "position": {
    "position_type": "text",
    "new_path": "src/user_service.py",
    "new_line": 42,
    "base_sha": "...",
    "start_sha": "...",
    "head_sha": "..."
  }
}
```

---

## 三、工程化优化

| 优化点 | 方案 | 效果 |
|:-------|:-----|:------|
| 限流 | MQ 异步消费，限制单项目并发 1/min | 防 GitLab 超时 + 防 LLM 过载 |
| 缓存 | Git 源码 / Nexus 依赖缓存 2 小时 | 降低 IO 和依赖压力 |
| 增量评审 | 仅对比新增 Diff，历史代码不重复评 | 缩短 LLM 推理耗时 |
| 幂等去重 | Redis 缓存 MR/Commit ID，10 min 去重 | 防止重复评审 |
| 重试机制 | GitLab API 回写 + 拉取超时最多 3 次重试 | 提升可靠性 |
| 权限隔离 | Git 拉取使用只读 deploy token，Nexus 最小权限 | 安全合规 |

---

## 四、故障场景处理

| 场景 | 处理策略 |
|:-----|:---------|
| WebHook Diff 截断 | 强制走 Git 拉取完整文件兜底 |
| 私有 Nexus 依赖不存在 | 降级仅用 Git 上下文，标注"缺失私有依赖，评审有局限" |
| LLM 调用超时 | 返回基础规则评审结果，记录异常告警 |
| 无代码变更事件（仅改标题/标签） | 直接过滤，跳过评审 |
| GitLab API 回写 403 | Token 权限不足，检查 scope 是否包含 `api` |

---

## 五、安全规范

1. Secret Token 使用随机 32 位以上字符串，每月轮换
2. GitLab Access Token 最小权限（仅 read_repository + api，禁止 maintainer）
3. WebHook 接口仅内网/企业 VPN 可访问，Nginx IP 白名单
4. 全站 HTTPS，开启 SSL 证书校验
5. MQ 任务 + WebHook 原始报文全链路日志留存 7 天
6. 仅上传代码 Diff，不传输无关文件

---

## 六、最简快速上手

### 方案 A：CodeReview Agent（开源，3 分钟）

```bash
# 1. 克隆项目
git clone https://github.com/wanghenan/codereview-agent.git
cd codereview-agent

# 2. 配置
cat > .codereview-agent.yaml << EOF
llm:
  provider: openai
  api_key: ${OPENAI_API_KEY}
  model: gpt-4o

gitlab:
  url: https://gitlab.xxx.com
  token: ${GITLAB_TOKEN}
EOF

# 3. GitHub Action 工作流
# .github/workflows/codereview.yml
name: CodeReview
on: [pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: wanghenan/codereview-agent@v1
        with:
          llm_api_key: ${{ secrets.LLM_API_KEY }}
```

### 方案 B：自建集成（完整控制）

> 参考本文的完整架构和代码实现，搭建自有流水线。

---

## 七、参考资料

- `import/md/GitLabWebhookCodeReview集成_0623085204.md` — 完整 305 行方案
- `import/md/会议纪要_codereview对齐_*.md` — 团队落地经验
- [AI CR 方案选型](2026-06-29-ai-codereview-landscape.md) — 平台方案 vs IDE 方案对比
- [Cursor CR 实践](2026-06-29-cursor-codereview-practice.md) — IDE 前置方案

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- [AI CR 方案选型](2026-06-29-ai-codereview-landscape.md) — 关联
- [Cursor CR 实践](2026-06-29-cursor-codereview-practice.md) — 关联

### 外部资料引用

- 来源: import/md/GitLabWebhookCodeReview集成_0623085204.md`(305行)、`import/md/AI时代CodeReview左移实战_*.md`云效侧方案、`import/md/CodeReview_29分钟开发_0623082321.md

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
