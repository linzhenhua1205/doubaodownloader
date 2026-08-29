# AI-Codereview-Gitlab 部署与配置操作指导

> **概要**: AI-Codereview-Gitlab部署配置指导，涵盖Docker部署、WebHook、通知渠道与Agentic Review模式
>
> **关键词**: AI代码审查 · GitLab · WebHook · Docker · 飞书通知

---

## 📑 目录

- [1. 整体架构与组件](#1-整体架构与组件)
- [2. 前置条件](#2-前置条件)
- [3. 服务端部署](#3-服务端部署)
  - [3.1 Docker 部署（推荐）](#31-docker-部署推荐)
  - [3.2 本地 Python 环境部署](#32-本地-python-环境部署)
  - [3.3 验证部署](#33-验证部署)
- [4. 环境变量配置详解](#4-环境变量配置详解)
  - [4.1 大模型供应商配置](#41-大模型供应商配置)
  - [4.2 代码 Review 主配置](#42-代码-review-主配置)
  - [4.3 代码托管平台配置](#43-代码托管平台配置)
  - [4.4 触发策略配置](#44-触发策略配置)
  - [4.5 Dashboard 认证配置](#45-dashboard-认证配置)
  - [4.6 Worker 任务队列配置](#46-worker-任务队列配置)
  - [4.7 日志配置](#47-日志配置)
- [5. GitLab WebHook 配置（关键步骤）](#5-gitlab-webhook-配置关键步骤)
  - [5.1 创建 Access Token](#51-创建-access-token)
  - [5.2 配置 WebHook](#52-配置-webhook)
  - [5.3 多项目批量配置](#53-多项目批量配置)
  - [5.4 Token 优先级说明](#54-token-优先级说明)
- [6. 通知渠道配置](#6-通知渠道配置)
  - [6.1 飞书机器人配置（推荐）](#61-飞书机器人配置推荐)
  - [6.2 钉钉机器人配置](#62-钉钉机器人配置)
  - [6.3 企业微信机器人配置](#63-企业微信机器人配置)
  - [6.4 自定义 Webhook 配置](#64-自定义-webhook-配置)
- [7. 仓库与通知群组映射关系管理](#7-仓库与通知群组映射关系管理)
  - [7.1 映射配置表结构](#71-映射配置表结构)
  - [7.2 多群通知配置](#72-多群通知配置)
- [8. 可视化 Dashboard 使用](#8-可视化-dashboard-使用)
- [9. 日报自动生成配置](#9-日报自动生成配置)
- [10. Agentic Review 模式（高级功能）](#10-agentic-review-模式高级功能)
  - [10.1 启用配置](#101-启用配置)
  - [10.2 安全沙箱机制](#102-安全沙箱机制)
  - [10.3 资源开销评估](#103-资源开销评估)
  - [10.4 自动降级机制](#104-自动降级机制)
- [11. Review 风格与 Prompt 自定义](#11-review-风格与-prompt-自定义)
  - [11.1 四种审查风格](#111-四种审查风格)
  - [11.2 Prompt 模板自定义](#112-prompt-模板自定义)
- [12. 常见问题与排障](#12-常见问题与排障)
  - [Q1: WebHook 测试返回 500](#q1-webhook-测试返回-500)
  - [Q2: 审查结果未回写到 GitLab](#q2-审查结果未回写到-gitlab)
  - [Q3: 如何跳过某个提交的审查？](#q3-如何跳过某个提交的审查)
  - [Q4: Push 和 MR 都触发重复 Review？](#q4-push-和-mr-都触发重复-review)
  - [Q5: Docker 部署后 GitLab 收不到通知](#q5-docker-部署后-gitlab-收不到通知)
  - [Q6: 某些文件类型不需要审查](#q6-某些文件类型不需要审查)
  - [Q7: LLM 响应太慢或 Token 消耗过大](#q7-llm-响应太慢或-token-消耗过大)
  - [Q8: Dashboard 无法登录](#q8-dashboard-无法登录)
- [🔗 交叉引用](#交叉引用)
- [📄 变更记录](#变更记录)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 1. 整体架构与组件

```ascii
                    GitLab Server（事件源）
                          |
          +---------------+---------------+
          | Push Events    | MR Events      |
          v                v                v
    +------------------------------------------+
    |    AI-Codereview-Gitlab 服务              |
    |                                          |
    |  +----------+   +------------------+     |
    |  | WebHook  |   |  Web Dashboard   |     |
    |  | Receiver |   |  (Streamlit)     |     |
    |  | :5001    |   |  :5002           |     |
    |  +----+-----+   +------------------+     |
    |       |                                   |
    |  +----v-----+   +------------------+     |
    |  | Diff     |   |  LLM 调用层       |     |
    |  | Parser   |-->|  (DeepSeek/OpenAI |     |
    |  |          |   |   /Claude/Qwen)   |     |
    |  +----------+   +--------+---------+     |
    |                          |                |
    |  +-----------------------v----------+    |
    |  |  结果处理器                       |    |
    |  |  +- GitLab API 回写 Notes        |    |
    |  |  +- 飞书/钉钉/企微 通知推送       |    |
    |  |  +- 持久化到数据库               |    |
    |  +----------------------------------+    |
    +------------------------------------------+
                          |
                +---------+---------+
                v                    v
        +--------------+   +--------------+
        | GitLab Notes  |   |  IM 通知      |
        | (行内评论)     |   | (飞书/钉钉等) |
        +--------------+   +--------------+
```

**核心组件**:

| 组件 | 说明 |
|:-----|:------|
| **api.py** | Flask API 服务（端口 5001），WebHook 接收 + 审查逻辑 |
| **ui.py** | Streamlit Dashboard（端口 5002），审查日志可视化 |
| **biz/service/** | 审查服务核心逻辑（Diff 解析、LLM 调用、结果回写） |
| **biz/llm/** | 多 LLM 供应商适配（Factory 模式） |
| **biz/platforms/** | 代码托管平台适配（GitLab/GitHub/Gitea） |
| **conf/prompt_templates.yml** | 审查 Prompt 模板（支持自定义） |
| **Dockerfile** | 容器化部署（含 supervisor 进程管理） |

---

## 2. 前置条件

| 条件 | 最低要求 | 推荐配置 |
|:-----|:--------|:---------|
| **服务器** | 2 核 4GB | 4 核 8GB |
| **OS** | Linux (CentOS 7+ / Ubuntu 20.04+) | Ubuntu 22.04 |
| **Docker** | Docker 20.10+ + Docker Compose v2 | Docker 24+ |
| **网络** | 可访问 GitLab + LLM API | 内网 GitLab + 外网 LLM API |
| **GitLab 版本** | GitLab 13.0+ | GitLab 15.0+ |
| **LLM API Key** | 任一大模型供应商 | DeepSeek / Claude Sonnet 4.5 |
| **IM 机器人** | 飞书/钉钉/企微 Webhook URL | — |

---

## 3. 服务端部署

### 3.1 Docker 部署（推荐）

**Step 1** — 克隆项目

```bash
git clone https://github.com/sunmh207/AI-Codereview-Gitlab.git
cd AI-Codereview-Gitlab
```

**Step 2** — 创建并编辑配置文件

```bash
cp conf/.env.dist conf/.env
vi conf/.env
```

核心配置项（详见 §4）：

```ini
# 选一个大模型供应商
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxx
DEEPSEEK_API_MODEL=deepseek-chat

# GitLab 配置（二选一）
# 方式A：在 .env 中配置全局 Token
GITLAB_ACCESS_TOKEN=glpat-xxxxxxxxxxxxx
# 方式B：不配 Token，由 WebHook Secret Token 传入

# 支持审查的文件类型
SUPPORTED_EXTENSIONS=.c,.cc,.cpp,.go,.h,.java,.py,.js,.ts,.vue,.yml

# 飞书通知（后续 §6 详细说明）
FEISHU_ENABLED=1
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
```

**Step 3** — 启动服务

```bash
docker-compose up -d
```

查看启动日志：

```bash
docker-compose logs -f
```

### 3.2 本地 Python 环境部署

```bash
# 1. 克隆源码
git clone https://github.com/sunmh207/AI-Codereview-Gitlab.git
cd AI-Codereview-Gitlab

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp conf/.env.dist conf/.env
vi conf/.env

# 5. 启动 API 服务（端口 5001）
python api.py

# 6. 启动 Dashboard 服务（端口 5002），新开终端
streamlit run ui.py --server.port=5002 --server.address=0.0.0.0
```

### 3.3 验证部署

| 组件 | 验证方式 | 预期结果 |
|:-----|:---------|:---------|
| **API 服务** | 浏览器访问 `http://your-server-ip:5001` | 显示 "The code review server is running." |
| **Dashboard** | 浏览器访问 `http://your-server-ip:5002` | 显示登录页面（默认 admin/admin） |

---

## 4. 环境变量配置详解

> **配置文件路径**: `conf/.env`
> **生效说明**: 修改 .env 后需重启服务（docker-compose restart / kill + restart Python 进程）

### 4.1 大模型供应商配置

| 变量 | 说明 | 可选值 |
|:-----|:------|:-------|
| `LLM_PROVIDER` | 选用的 LLM 供应商 | `deepseek`, `openai`, `zhipuai`, `qwen`, `ollama`, `anthropic` |

**各供应商所需配置**:

| 供应商 | 必须配置的变量 | 推荐模型 |
|:-------|:--------------|:---------|
| **DeepSeek** | `DEEPSEEK_API_KEY`, `DEEPSEEK_API_MODEL` | `deepseek-chat` |
| **OpenAI** | `OPENAI_API_KEY`, `OPENAI_API_BASE_URL`, `OPENAI_API_MODEL` | `gpt-4o-mini` |
| **Claude** | `ANTHROPIC_API_KEY`, `ANTHROPIC_API_BASE_URL`, `ANTHROPIC_API_MODEL` | `claude-sonnet-4-5-20250929` |
| **通义千问** | `QWEN_API_KEY`, `QWEN_API_BASE_URL`, `QWEN_API_MODEL` | `qwen-coder-plus` |
| **智谱** | `ZHIPUAI_API_KEY`, `ZHIPUAI_API_MODEL` | `GLM-4-Flash` |
| **Ollama** | `OLLAMA_API_BASE_URL`, `OLLAMA_API_MODEL` | `deepseek-r1:latest` |

**Ollama Docker 部署注意事项**:

```ini
# Docker 部署：host.docker.internal 指向宿主机
OLLAMA_API_BASE_URL=http://host.docker.internal:11434

# 非 Docker 部署：127.0.0.1 即可
# OLLAMA_API_BASE_URL=http://127.0.0.1:11434
```

### 4.2 代码 Review 主配置

| 变量 | 默认值 | 说明 |
|:-----|:-------|:------|
| `SUPPORTED_EXTENSIONS` | `.c,.cc,.cpp,.cs,.css,...` | **修改后需重启服务**才生效。建议按团队技术栈精简，减少不必要的 LLM 调用 |
| `REVIEW_MAX_TOKENS` | `10000` | 每次 Review 的最大 Token 限制，超出自动截断 |
| `REVIEW_STYLE` | `professional` | 审查风格：`professional` 专业 / `sarcastic` 毒舌 / `gentle` 温和 / `humorous` 幽默 |

### 4.3 代码托管平台配置

| 平台 | 配置项 | 说明 |
|:-----|:-------|:------|
| **GitLab** | `GITLAB_ACCESS_TOKEN` | **优先使用**此 Token，未配置时回退到 WebHook Secret Token |
| **GitLab（老版本）** | `GITLAB_URL` | 部分老版本 GitLab WebHook 不传递 URL，需显式设置 |
| **GitHub** | `GITHUB_ACCESS_TOKEN` | 使用 GitHub 平台时需配置 |
| **Gitea** | `GITEA_ACCESS_TOKEN` + `GITEA_URL` | 使用 Gitea 平台时需配置 |

### 4.4 触发策略配置

| 变量 | 默认值 | 说明 |
|:-----|:-------|:------|
| `PUSH_REVIEW_ENABLED` | `1` | Push 事件是否触发 Review。设为 `0` 则仅 MR 触发 |
| `MERGE_REVIEW_ONLY_PROTECTED_BRANCHES_ENABLED` | `0` | 设为 `1` 时，仅目标分支为受保护分支才 Review。<br>**前提**: 需先在 GitLab 仓库 Settings → Repository → Protected Branches 中配置 |

### 4.5 Dashboard 认证配置

| 变量 | 默认值 | 说明 |
|:-----|:-------|:------|
| `DASHBOARD_USER` | `admin` | Dashboard 登录用户名。**首次部署后立即修改** |
| `DASHBOARD_PASSWORD` | `admin` | Dashboard 登录密码。以明文存储，建议文件权限设为 600 |

### 4.6 Worker 任务队列配置

| 变量 | 说明 |
|:-----|:------|
| `WORKER_QUEUE` | 队列名前缀，须与 Git 平台域名 **slug** 一致。命名规则：`<域名_with_underscores>`，例 `gitlab.example.com` → `git_example_com`。多实例部署时队列名必须保持一致 |

### 4.7 日志配置

| 变量 | 默认值 | 说明 |
|:-----|:-------|:------|
| `LOG_FILE` | `log/app.log` | 日志文件路径 |
| `LOG_MAX_BYTES` | `10485760` (10MB) | 单个日志文件最大值，超限自动滚动 |
| `LOG_BACKUP_COUNT` | `3` | 保留的历史日志文件数 |
| `LOG_LEVEL` | `DEBUG` | `DEBUG`: 输出每轮 assistant 内容和工具调用详情（排查用）<br>`INFO`: 每轮一条结构化摘要<br>`WARNING`/`ERROR`: 仅异常输出 |

---

## 5. GitLab WebHook 配置（关键步骤）

> **核心原则**: 每个需要 AI Review 的 GitLab 仓库都需要单独配置 WebHook。

### 5.1 创建 Access Token

**方式一：Project Access Token（推荐，范围最小）**

```text
1. 进入目标仓库
2. 左侧菜单 -> Settings -> Access Tokens
3. 选择 "Project Access Tokens"
4. 填写 Token 名称（如: ai-codereview-token）
5. 角色 (Role): 选择 "Maintainer" 或以上
6. 勾选权限: 至少勾选 "api"（用于回写 Notes）
7. 点击 "Create project access token"
8. 复制并保存 Token（离开页面后将无法再次查看）
```

⚠️ **权限说明**:

- `Maintainer` 权限足够满足 review 需求（读仓库 + 写 Notes）
- 用 `api` 范围而非 `read_api`，因为需要写 GitLab Notes
- **不需要** `sudo` / `admin` 权限

**方式二：Personal Access Token（范围更大，谨慎使用）**

```text
1. 点击 GitLab 右上角头像 -> Preferences -> Access Tokens
2. 选择 "Personal Access Tokens"
3. 填写名称，选择 "Maintainer" 角色
4. 勾选 "api" 范围
5. 创建并保存
```

> **选择建议**: 项目级 Token（方式一）> 个人 Token（方式二）。
> 项目级 Token 在项目删除时自动失效，风险更可控。

### 5.2 配置 WebHook

```text
1. 进入目标仓库
2. 左侧菜单 -> Settings -> Webhooks
3. 填写以下参数：

   +----------------------------------------------+
   | URL:        http://<你的服务器IP>:5001/review/webhook  |
   | Secret Token: 上面创建的 Access Token (可选)          |
   |                                                    |
   | Trigger:    ☑ Push events                          |
   |             ☑ Merge request events                  |
   |             ☐ 其他事件不勾选                        |
   |                                                    |
   | SSL验证:    内网环境可关闭                          |
   +----------------------------------------------+

4. 点击 "Add webhook"
5. 验证: 点击 "Test" -> 选择 "Push events" / "Merge requests events"
   - 如果服务端收到请求并返回 200，配置成功
   - 如果失败，检查 URL 可达性、防火墙、Secret Token 是否匹配
```

**Critical — 只勾选以下两个事件**:

| 事件 | 说明 | 对应阶段 |
|:-----|:------|:---------|
| ✅ **Push events** | 代码推送时触发 Review | 阶段二（提交后 AI 走读） |
| ✅ **Merge request events** | 创建/更新 MR 时触发 Review | 阶段二（MR 走读） |
| ❌ 其他事件 | 不要勾选，避免无效请求浪费服务资源和 LLM Token | — |

### 5.3 多项目批量配置

对于大量仓库需要统一配置的场景：

```bash
# 使用 GitLab API 批量创建 WebHook
# 先创建 API Token（管理员/项目范围）

# 单仓库创建
curl --request POST "https://gitlab.example.com/api/v4/projects/<PROJECT_ID>/hooks" \
  --header "PRIVATE-TOKEN: <YOUR_ACCESS_TOKEN>" \
  --data "url=http://your-server:5001/review/webhook" \
  --data "push_events=true" \
  --data "merge_requests_events=true" \
  --data "enable_ssl_verification=false"

# 批量创建脚本示例（for project_id in project_ids; do ... done）
```

### 5.4 Token 优先级说明

```text
系统优先使用 .env 文件中的 GITLAB_ACCESS_TOKEN
    |
    +- 如果 .env 中已配置 -> 使用 GITLAB_ACCESS_TOKEN
    |
    +- 如果 .env 中未配置 -> 回退到 WebHook 传递的 Secret Token
```

**推荐策略**: 在 `conf/.env` 中配置全局 `GITLAB_ACCESS_TOKEN`，WebHook 中不再填写 Secret Token。这样管理更集中，减少配置失误。

---

## 6. 通知渠道配置

### 6.1 飞书机器人配置（推荐）

**Step 1** — 在飞书群聊中创建机器人

```text
1. 进入需要接收审查通知的飞书群
2. 点击群右上角 "..." -> 设置
3. 左侧 -> 群机器人 -> 添加机器人
4. 搜索 "自定义机器人" 或 "Custom Bot"
5. 点击 "添加"
```

**Step 2** — 配置机器人

```text
1. 机器人名称: AI CodeReview 通知
2. 机器人描述: 自动推送代码审查结果
3. Webhook URL: ⚠️ 复制保存！后续要用
   https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**Step 3** — 配置到 .env

```ini
FEISHU_ENABLED=1
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### 6.2 钉钉机器人配置

```text
1. 进入钉钉群聊 -> 群设置 -> 智能群助手 -> 添加机器人
2. 选择 "自定义"（通过 Webhook 接入）
3. 设置机器人名称，完成安全设置（建议选择 "加签"）
4. 复制 Webhook URL
```

编辑 .env：

```ini
DINGTALK_ENABLED=1
DINGTALK_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=xxx
DINGTALK_SECRET_ENABLED=1           # 启用加签校验
DINGTALK_SECRET=SECxxx              # 加签密钥
```

### 6.3 企业微信机器人配置

```text
1. 进入企业微信群聊 -> 群设置 -> 群机器人 -> 添加
2. 创建新机器人，填写名称和头像
3. 复制 Webhook URL
```

编辑 .env：

```ini
WECOM_ENABLED=1
WECOM_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx
```

### 6.4 自定义 Webhook 配置

用于发送定制化通知（如通过飞书应用消息推送到提交人）：

```ini
EXTRA_WEBHOOK_ENABLED=1
EXTRA_WEBHOOK_URL=https://your-custom-webhook/xxx
```

**自定义 Webhook 数据结构**:

```json
{
  "ai_codereview_data": {
    // 本系统通知数据（审查结果等）
  },
  "webhook_data": {
    // 原始 GitLab/GitHub WebHook 触发数据
  }
}
```

---

## 7. 仓库与通知群组映射关系管理

### 7.1 映射配置表结构

每个仓库需绑定其对应的通知群机器人。配置表结构如下：

| 字段 | 类型 | 说明 | 示例 |
|:-----|:-----|:------|:-----|
| 仓库URL | string | GitLab 仓库完整 URL | `https://gitlab.example.com/team-a/firmware-bmc.git` |
| 仓库对应群机器人Webhook | string | 通知群机器人的 Webhook URL | `https://open.feishu.cn/open-apis/bot/v2/hook/xxx` |

**配置模板**:

```csv
仓库URL,仓库对应群机器人webhook
https://gitlab.example.com/team-a/firmware-bmc.git,https://open.feishu.cn/open-apis/bot/v2/hook/xxx
https://gitlab.example.com/team-b/platform-bios.git,https://open.feishu.cn/open-apis/bot/v2/hook/yyy
```

### 7.2 多群通知配置

**支持一个仓库对应多个群机器人**，多个群机器人的 Webhook URL 用英文逗号 `,` 隔开：

| 仓库URL | 群机器人Webhook |
|:--------|:----------------|
| `https://gitlab.example.com/team-a/firmware-bmc.git` | `https://open.feishu.cn/open-apis/bot/v2/hook/xxx,https://open.feishu.cn/open-apis/bot/v2/hook/yyy` |

> 此配置使得审查结果可同时推送到：
>
> - 项目核心成员群（接收详细审查报告）
> - 质量保障群（跟踪全局质量问题）
> - 技术 Leader 群（关注高严重度问题摘要）

**配置流程总结**:

```text
1. 部署服务（§3）->
2. 配置 .env（§4）->
3. 为每个仓库创建 Token + WebHook（§5）->
4. 每个仓库对应群创建飞书/钉钉/企微机器人（§6）->
5. 填写仓库URL↔群机器人Webhook 映射表 ->
6. 同步配置到值班人员（如 @黄嘉鑫）完成上线
```

---

## 8. 可视化 Dashboard 使用

**访问地址**: `http://your-server-ip:5002`
**默认登录**: admin / admin（首次登录后立即修改）

Dashboard 提供以下功能：

| 功能模块 | 说明 |
|:---------|:------|
| **审查记录列表** | 所有审查请求的时间线视图，支持按日期/项目/提交人筛选 |
| **项目统计** | 各项目审查次数、问题密度、平均分统计 |
| **开发者统计** | 按提交人统计审查结果，识别代码质量趋势 |
| **审查详情** | 点击单条记录查看完整的 LLM 审查报告 |
| **收藏与备注** | 对关键问题可收藏标记，便于复盘 |

---

## 9. 日报自动生成配置

系统支持基于 GitLab Commit 记录自动生成每日开发进展日报。

```ini
# 日报发送时间（cron 表达式）
# 默认: 工作日 18:00 发送
REPORT_CRONTAB_EXPRESSION=0 18 * * 1-5
```

**日报内容**:

- 按提交人分组的当天 Commit 摘要
- 去重逻辑：基于 `(author, commit_message)` 组合去重
- 通过已配置的通知渠道（飞书/钉钉/企微）发送

**手动触发**: 访问 `http://your-server-ip:5001/review/daily_report` 可立即触发一次日报生成

---

## 10. Agentic Review 模式（高级功能）

> Agentic 模式下，LLM 可通过工具调用（read_file / 沙箱 shell）在本地克隆的代码库内自主探索，产出更全面的审查结果。**默认关闭**，启用需显式配置。

### 10.1 启用配置

```ini
# 切换审查策略
REVIEW_STRATEGY=agentic

# 本地仓库缓存目录（默认）
REPO_CACHE_DIR=data/repo_cache

# 单次工具输出最大 Token 数，超出截断
AGENT_TOOL_OUTPUT_MAX_TOKENS=10000

# LLM agent 最大迭代次数（默认 20）
AGENT_MAX_ITERATIONS=20
```

### 10.2 安全沙箱机制

| 安全层 | 机制 | 说明 |
|:-------|:-----|:------|
| **命令白名单** | 默认仅允许读类命令 | `ls`, `cat`, `head`, `tail`, `grep`, `find`, `wc`, `git` |
| **命令黑名单** | 禁止危险操作 | `rm`, `mv`, `cp`, `chmod`, `chown`, `curl`, `wget`, `sudo` |
| **路径越界检查** | 禁止访问仓库目录外的文件 | — |
| **超时保护** | 单次 Shell 调用 30s 超时 | — |
| **降级机制** | 任意阶段失败自动降级为 diff_only | 保证至少返回原版一致的审查 |

自定义白名单/黑名单（可选）：

```ini
# 覆盖默认白名单
AGENT_SHELL_ALLOWLIST=ls,cat,head,tail,grep,find,wc,git,rg,tree
# 覆盖默认黑名单
AGENT_SHELL_BLOCKLIST=rm,mv,cp,chmod,chown,curl,wget,sudo,touch
```

### 10.3 资源开销评估

| 维度 | 估算 | 说明 |
|:-----|:-----|:------|
| **磁盘** | ≥ 50GB 预留 | 按需克隆目标项目（10MB~2GB/项目） |
| **内存** | ~500MB / session | 单次审查 session 峰值 |
| **Token** | 5k~50k / review | diff_only 的 3~10 倍 |
| **时延** | 30s~5min / review | 大幅长于 diff_only 模式 |

### 10.4 自动降级机制

```text
agentic review 请求
    |
    +- clone 失败 -> 降级为 diff_only
    +- fetch 失败 -> 降级为 diff_only
    +- LLM 调用异常 -> 降级为 diff_only
    +- 工具调用异常 -> 降级为 diff_only
    |
    +- 全部成功 -> 返回 agentic review 结果
```

---

## 11. Review 风格与 Prompt 自定义

### 11.1 四种审查风格

| 风格 | 配置值 | 说明 | 适用场景 |
|:-----|:-------|:------|:---------|
| **专业型** 🤵 | `professional` | 严谨细致，正式专业，使用标准工程术语 | 正式项目审查 |
| **毒舌型** 😈 | `sarcastic` | 大胆使用讽刺性语言，技术指正准确 | 内部快速 review，增加趣味 |
| **温和型** 🌸 | `gentle` | 多用"建议"、"可以考虑"等温和措辞 | 新人培养期 |
| **幽默型** 🤪 | `humorous` | 技术点评中加入幽默元素和适度 Emoji | 团队氛围轻松的场景 |

配置方式：

```ini
REVIEW_STYLE=professional
```

### 11.2 Prompt 模板自定义

**文件路径**: `conf/prompt_templates.yml`

系统使用 Jinja2 模板引擎。可自定义以下两个模板：

| 模板 | 变量 | 说明 |
|:-----|:------|:------|
| `code_review_prompt` | `diffs_text`, `commits_text`, `style` | 标准 diff_only 审查 Prompt |
| `agentic_code_review_prompt` | `repo_root`, `diffs_text`, `commits_text`, `style` | Agentic 模式启用时的审查 Prompt |

**自定义示例**（在 `conf/prompt_templates.yml` 中添加自定义规则）：

```yaml
code_review_prompt:
  system_prompt: |-
    ...（原有内容保持不变或按需修改）

    ### 额外审查规则（团队自定义）:
    1. 发现硬编码 IP/密码 → 标记为 P0 严重问题
    2. 发现缺少空指针检查 → 标记为 P1 问题
    3. ...
```

**注意事项**:

- 修改 Prompt 后需重启服务
- 保持 `总分:XX分` 的正则格式，否则 Dashboard 无法解析分数
- 可增加团队特定的编码规范作为审查规则

---

## 12. 常见问题与排障

### Q1: WebHook 测试返回 500

| 可能原因 | 排查方法 | 解决 |
|:---------|:---------|:-----|
| LLM API Key 无效 | 查看 `log/app.log` 中 API 调用错误 | 检查 .env 中的 API 配置 |
| GitLab Token 权限不足 | 日志中显示 GitLab API 403 | 确认 Token 至少为 Maintainer 角色 |
| 网络不通 | `curl http://your-server:5001/review/webhook` | 检查防火墙、SELinux、安全组 |

### Q2: 审查结果未回写到 GitLab

- 确认 `GITLAB_ACCESS_TOKEN` 有 `api` 范围且至少有 `Maintainer` 权限
- 检查日志中 GitLab API 调用是否成功返回
- 确认 WebHook Secret Token 与 .env 中配置一致

### Q3: 如何跳过某个提交的审查？

当前版本不支持按提交跳过，但可通过以下方式规避：

- 在 Commit Message 中包含 `[skip review]` 标记（需自行修改源码支持）
- 临时在 GitLab 中禁用该仓库的 WebHook

### Q4: Push 和 MR 都触发重复 Review？

这是设计特性：Push 审查的是提交内容，MR 审查的是整个变更集。如果不需要 Push 触发：

```ini
PUSH_REVIEW_ENABLED=0
```

### Q5: Docker 部署后 GitLab 收不到通知

```bash
# 检查容器是否正常运行
docker ps | grep ai-codereview

# 查看容器日志
docker-compose logs -f --tail=100

# 验证容器内服务可访问
docker exec -it <container_id> curl http://127.0.0.1:5001
```

### Q6: 某些文件类型不需要审查

修改 `SUPPORTED_EXTENSIONS` 即可，去除不需要的后缀：

```ini
# 仅审查核心源码文件
SUPPORTED_EXTENSIONS=.c,.cc,.cpp,.h,.java,.py,.go,.rs,.ts
```

### Q7: LLM 响应太慢或 Token 消耗过大

| 优化手段 | 说明 |
|:---------|:------|
| 减少 `REVIEW_MAX_TOKENS` | 限制每次审查的 Token 上限 |
| 精简 `SUPPORTED_EXTENSIONS` | 减少不必要的文件送审 |
| 切换到更轻量的模型 | 如 `deepseek-chat` 替代 `gpt-4o` |
| 启用 diff_only 模式 | 不使用 Agentic Review |

### Q8: Dashboard 无法登录

```bash
# 检查 .env 中配置
DASHBOARD_USER=admin
DASHBOARD_PASSWORD=admin

# 重启服务后重新访问
docker-compose restart
```

---

## 🔗 交叉引用

- [**CodeReview 整体方案**](../../02_rd/01_product/01_software/13-codereview-project/2026-07-09-codereview-system-overview.md) — 三阶段走读体系，本工具是阶段二（提交后 AI 走读）的核心实现
- [**GitLab WebHook 集成方案**](2026-06-29-gitlab-webhook-integration.md) — 通用的 GitLab WebHook + LLM 集成方案，本指导是基于该方案的特定项目实现
- [**CodeReview 质量评估体系**](2026-06-29-codereview-quality-assessment.md) — 代码质量 7 维评估模型与度量指标
- [**AI CR 方案全景**](2026-06-29-ai-codereview-landscape.md) — 三大 AI CR 路径对比与选型决策
- [**Cursor CR 实践**](2026-06-29-cursor-codereview-practice.md) — Cursor IDE 本地 CR 方案（阶段一 Pre-commit 补充）
- [**CodeReview 项目路标**](../../02_rd/01_product/01_software/13-codereview-project/2026-07-09-codereview-roadmap.md) — 路标规划与左移策略
- [**Git 分支策略与规范**](../git/2026-06-29-git-branch-strategy-and-standards.md) — Git 分支策略与 PR 协作规范

---

## 📄 变更记录

| 日期 | 版本 | 变更说明 |
|:-----|:----:|:---------|
| 2026-07-10 | v1.0 | 初始创建。基于 [sunmh207/AI-Codereview-Gitlab](https://github.com/sunmh207/AI-Codereview-Gitlab) v1.5.1 源码分析，覆盖 12 章完整配置与操作指导 |

---

> **总行数**: ~680 行 | **来源**: 项目 README + `conf/.env.dist` + `conf/prompt_templates.yml` + `Dockerfile` + `biz/api/routes/*.py` + `biz/service/*.py` + `biz/llm/factory.py` + `biz/utils/config_checker.py`

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- [**CodeReview 整体方案**](../../02_rd/01_product/01_software/13-codereview-project/2026-07-09-codereview-system-overview.md) — 关联
- [**GitLab WebHook 集成方案**](2026-06-29-gitlab-webhook-integration.md) — 关联
- [**CodeReview 质量评估体系**](2026-06-29-codereview-quality-assessment.md) — 关联
- [**AI CR 方案全景**](2026-06-29-ai-codereview-landscape.md) — 关联
- [**Cursor CR 实践**](2026-06-29-cursor-codereview-practice.md) — 关联
- [**CodeReview 项目路标**](../../02_rd/01_product/01_software/13-codereview-project/2026-07-09-codereview-roadmap.md) — 关联
- [**Git 分支策略与规范**](../git/2026-06-29-git-branch-strategy-and-standards.md) — 关联

### 外部资料引用

- (无)

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
