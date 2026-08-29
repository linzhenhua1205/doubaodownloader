# AI-Codereview-Gitlab 代码方案详细解析

> **概要**: 基于大模型的 GitLab 自动代码审查工具，代码级深度分析文档
>
> **关键词**: (待补充)

---

## 📑 目录

- [1. 整体框架](#1-整体框架)
  - [1.1 系统架构总览](#11-系统架构总览)
  - [1.2 两个后台进程](#12-两个后台进程)
  - [1.3 进程管理：Supervisor](#13-进程管理supervisor)
  - [1.4 项目文件结构](#14-项目文件结构)
  - [1.5 外部挂载设计](#15-外部挂载设计)
  - [1.6 模块索引速查](#16-模块索引速查)
  - [1.7 实体数据结构（entity/review_entity.py）](#17-实体数据结构entityreview_entitypy)
  - [1.8 员工姓名映射（employee_mapping.py）](#18-员工姓名映射employee_mappingpy)
  - [1.9 Dashboard 前端（ui.py）](#19-dashboard-前端uipy)
  - [1.10 全仓库 Review 命令（cmd/review.py）](#110-全仓库-review-命令cmdreviewpy)
  - [1.11 Conf 配置设计（prompt_templates.yml）](#111-conf-配置设计prompt_templatesyml)
- [2. 核心数据流全链路分析](#2-核心数据流全链路分析)
- [3. API 定义与路由](#3-api-定义与路由)
  - [3.1 WebHook 路由（主入口）](#31-webhook-路由主入口)
  - [3.2 健康检查路由](#32-健康检查路由)
  - [3.3 日报路由](#33-日报路由)
- [4. 事件类型判断与分发](#4-事件类型判断与分发)
  - [4.1 Push 事件流程](#41-push-事件流程)
  - [4.2 Merge Request 事件流程](#42-merge-request-事件流程)
- [5. 队列任务执行逻辑](#5-队列任务执行逻辑)
  - [5.1 事件分派架构](#51-事件分派架构)
  - [5.2 Push 事件处理](#52-push-事件处理)
  - [5.3 MR 事件处理](#53-mr-事件处理)
  - [5.4 GitHub/Gitea 适配](#54-githubgitea-适配)
- [6. 数据解析：WebHook 数据结构](#6-数据解析webhook-数据结构)
  - [6.1 PushHandler 解析](#61-pushhandler-解析)
  - [6.2 MergeRequestHandler 解析](#62-mergerequesthandler-解析)
  - [6.3 filter_changes 过滤逻辑](#63-filter_changes-过滤逻辑)
  - [6.4 slugify_url 工具](#64-slugify_url-工具)
- [7. 代码评审引擎](#7-代码评审引擎)
  - [7.1 Review 策略选择](#71-review-策略选择)
  - [7.2 BaseReviewer 基类](#72-basereviewer-基类)
  - [7.3 CodeReviewer（diff_only 模式）](#73-codereviewerdiff_only-模式)
  - [7.4 AgenticReviewer（agentic 模式）](#74-agenticrevieweragentic-模式)
  - [7.5 评分解析](#75-评分解析)
- [8. 飞书通知体系](#8-飞书通知体系)
  - [8.1 EventManager 事件驱动架构](#81-eventmanager-事件驱动架构)
  - [8.2 MR 审查事件处理](#82-mr-审查事件处理)
  - [🔀 {mr_review_entity.project_name}: Merge Request](#mr_review_entityproject_name-merge-request)
    - [合并请求信息:](#合并请求信息)
  - [8.3 Push 审查事件处理](#83-push-审查事件处理)
  - [8.4 Notifier 统一分发](#84-notifier-统一分发)
  - [8.5 FeishuNotifier 卡片设计](#85-feishunotifier-卡片设计)
- [9. LLM 供应商适配层](#9-llm-供应商适配层)
- [10. 数据库设计](#10-数据库设计)
- [11. Agentic Review 模式分析](#11-agentic-review-模式分析)
- [12. 后续规划](#12-后续规划)
  - [12.1 未来规划](#121-未来规划)
  - [12.2 RAG 搭建思路](#122-rag-搭建思路)
  - [12.3 模型精调 + 数据飞轮](#123-模型精调-数据飞轮)
  - [12.4 其他扩展开发思路](#124-其他扩展开发思路)
- [🔗 交叉引用](#交叉引用)
- [📄 变更记录](#变更记录)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 1. 整体框架

### 1.1 系统架构总览

```ascii
                     GitLab / GitHub / Gitea
                            |
                    WebHook POST 请求
                            |
                            v
+-------------------------------------------+
|           Flask API Server (:5001)         |
|                                           |
|  /review/webhook    (主入口)                |
|  /review/health     (健康检查)              |
|  /review/daily_report (日报触发)            |
|                                           |
|  +-------------------------------------+   |
|  |  事件类型判断                        |   |
|  |  +- object_kind == "push"           |   |
|  |  +- object_kind == "merge_request"  |   |
|  |  +- GitHub/Gitea 适配分支           |   |
|  +--------------+----------------------+   |
|                 |                            |
|                 v                            |
|  +-------------------------------------+   |
|  |  队列任务执行  biz/queue/worker.py   |   |
|  |  +- handle_push_event()             |   |
|  |  +- handle_merge_request_event()    |   |
|  |  +- handle_github_*_event()         |   |
|  |  +- handle_gitea_*_event()          |   |
|  +--------------+----------------------+   |
|                 |                            |
|         +-------+-------+                   |
|         v               v                   |
|  +------------+  +------------------+       |
|  | GitLab API |  |  LLM 审查引擎     |       |
|  | (获取diff)  |  | +- diff_only     |       |
|  |            |  | +- agentic       |       |
|  +-----+------+  +--------+---------+       |
|        |                  |                  |
|        v                  v                  |
|  +-------------------------------------+   |
|  |  结果处理                            |   |
|  |  +- GitLab Notes 回写               |   |
|  |  +- EventManager 事件分发            |   |
|  |  |  +- on_merge_request_reviewed()  |   |
|  |  |  +- on_push_reviewed()           |   |
|  |  +- ReviewService 数据库持久化       |   |
|  +-------------------------------------+   |
+-------------------------------------------+
            |
            v
+--------------------------+
|  Streamlit Dashboard     |
|  (:5002)                 |
|                          |
|  读取 data/data.db       |
|  展示审查记录与统计        |
+--------------------------+
```

**三条核心链路**:

| 链路 | 触发 | 关键代码 | 输出 |
|:-----|:-----|:---------|:-----|
| **Push 审查** | Push WebHook | `handle_push_event()` → `PushHandler.get_push_changes()` → `CodeReviewer.review()` → GitLab commit comment + 飞书通知 + 数据库 | GitLab commit 行内批注 |
| **MR 审查** | MR WebHook | `handle_merge_request_event()` → `MergeRequestHandler.get_merge_request_changes()` → `CodeReviewer.review()` → GitLab MR notes + 飞书通知 + 数据库 | GitLab MR Notes |
| **Dashboard** | 人工访问 | `streamlit run ui.py` → 读取 `data/data.db` → 可视化 | 审查记录查看与统计 |

### 1.2 两个后台进程

| 进程 | 技术栈 | 端口 | 职责 | 入口 |
|:-----|:-------|:----:|:-----|:-----|
| **AI Code Review 服务** | Flask + APScheduler | 5001 | WebHook 接收、LLM 审查、通知推送、日报生成 | `api.py` |
| **Dashboard** | Streamlit | 5002 | 审查记录可视化、项目/开发者统计 | `ui.py` |

**api.py 入口**:

```python
# api.py — 主入口
from dotenv import load_dotenv
load_dotenv("conf/.env")          # ① 加载环境变量

import os
from biz.api import api_app, init_app
from biz.api.scheduler import setup_scheduler
from biz.utils.config_checker import check_config

init_app(api_app)                  # ② 注册所有路由

if __name__ == '__main__':
    check_config()                 # ③ 启动时配置自检
    setup_scheduler()              # ④ 启动定时任务（日报）
    port = int(os.environ.get('SERVER_PORT', 5001))
    api_app.run(host='0.0.0.0', port=port)  # ⑤ 启动 Flask
```

**ui.py 入口**: Streamlit 应用，读取 `data/data.db` 中的审查日志，展示审查记录列表、项目统计、开发者统计。

### 1.3 进程管理：Supervisor

**conf/supervisord.conf**:

```ini
[program:api]
command=python api.py
directory=/app
autostart=true
autorestart=true
stdout_logfile=/app/log/api_out.log
stderr_logfile=/app/log/api_err.log

[program:dashboard]
command=streamlit run ui.py --server.port=5002 --server.address=0.0.0.0
directory=/app
autostart=true
autorestart=true
stdout_logfile=/app/log/dashboard_out.log
stderr_logfile=/app/log/dashboard_err.log
```

Dockerfile 中 CMD:

```dockerfile
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
```

**关键设计**: Supervisor 管理两个进程，任一崩溃自动重启。日志分离到独立文件。

### 1.4 项目文件结构

```ascii
AI-Codereview-Gitlab/
|
+-- conf/                          # 📁 配置文件（外部挂载）
|   +-- .env                       #    环境变量（从 .env.dist 复制）
|   +-- .env.dist                  #    环境变量模板
|   +-- prompt_templates.yml       #    LLM Prompt 模板
|   +-- supervisord.conf           #    进程管理配置
|
+-- biz/                           # 📁 核心业务代码
|   +-- api/                       #    API 路由
|   |   +-- __init__.py            #    Flask 应用初始化
|   |   |                         #    关键: init_app() 注册路由
|   |   +-- routes/
|   |   |   +-- __init__.py        #    路由注册函数
|   |   |   +-- home.py            #    /review/health 健康检查
|   |   |   +-- webhook.py         #    /review/webhook 主入口
|   |   |   +-- daily_report.py    #    /review/daily_report 日报
|   |   +-- scheduler.py           #    APScheduler 定时任务
|   |
|   +-- agent/                     #    Agentic Review 模式
|   |   +-- agentic_reviewer.py    #    Agentic 审查器主类
|   |   +-- llm_adapter.py         #    LLM 调用 (OpenAI 兼容)
|   |   +-- prompts.py             #    Agent 系统 Prompt
|   |   +-- repo_syncer.py         #    仓库克隆/同步
|   |   +-- runner.py              #    工具调用循环 (ReAct)
|   |   +-- safety.py              #    安全沙箱
|   |   +-- tool.py                #    工具定义基类
|   |   +-- tool_registry.py       #    工具注册中心
|   |   +-- tools/                 #    具体工具实现
|   |
|   +-- cmd/                       #    命令行工具
|   |   +-- review.py              #    全仓库 Review 命令
|   |
|   +-- entity/                    #    数据结构体
|   |   +-- review_entity.py       #    MergeRequestReviewEntity
|   |                              #    PushReviewEntity
|   |
|   +-- event/                     #    事件处理（下游）
|   |   +-- event_manager.py       #    EventManager + 信号 + 飞书卡片
|   |
|   +-- llm/                       #    大模型适配
|   |   +-- factory.py             #    Factory 模式创建客户端
|   |   +-- client/                #    各供应商客户端实现
|   |       +-- base.py            #    BaseClient 抽象基类
|   |       +-- deepseek.py        #    DeepSeek 客户端
|   |       +-- openai.py          #    OpenAI 客户端
|   |       +-- anthropic.py       #    Claude 客户端
|   |       +-- zhipuai.py         #    智谱客户端
|   |       +-- qwen.py            #    通义千问客户端
|   |       +-- ollama_client.py   #    Ollama 客户端
|   |
|   +-- platforms/                 #    代码托管平台适配
|   |   +-- gitlab/                #    GitLab
|   |   |   +-- webhook_handler.py #    PushHandler + MergeRequestHandler
|   |   +-- github/                #    GitHub
|   |   +-- gitea/                 #    Gitea
|   |
|   +-- queue/                     #    队列任务执行
|   |   +-- worker.py              #    所有事件处理函数（核心编排）
|   |
|   +-- service/                   #    数据持久化
|   |   +-- review_service.py      #    SQLite 读写 + 数据库初始化
|   |
|   +-- utils/                     #    工具类
|       +-- code_parser.py         #    GitDiffParser
|       +-- code_reviewer.py       #    CodeReviewer (BaseReviewer 子类)
|       +-- config_checker.py      #    启动配置自检
|       +-- dir_util.py            #    目录工具
|       +-- log.py                 #    日志配置 (RotatingFileHandler)
|       +-- queue.py               #    队列工具函数
|       +-- reporter.py            #    日报生成器
|       +-- token_util.py          #    Token 计数与截断
|       +-- im/                    #    即时通讯通知
|           +-- notifier.py        #    统一分发入口
|           +-- feishu.py          #    飞书卡片发送
|           +-- dingtalk.py        #    钉钉消息
|           +-- wecom.py           #    企业微信
|           +-- webhook.py         #    自定义 Webhook
|
+-- data/                          # 📁 数据库目录（外部挂载）
|   +-- data.db                    #    SQLite 数据库文件
|
+-- log/                           # 📁 日志目录（外部挂载）
|   +-- app.log                    #    主日志文件
|
+-- api.py                         # 🚀 Flask 服务入口
+-- ui.py                          # 🚀 Streamlit Dashboard 入口
+-- Dockerfile                     # 🐳 Docker 构建文件
+-- docker-compose.yml             # 🐳 Docker Compose 编排
+-- requirements.txt               # Python 依赖清单
```

### 1.5 外部挂载设计

生产部署时通过 Docker Volume 实现数据持久化：

```yaml
# docker-compose.yml
volumes:
  - ./conf:/app/conf        # 配置文件（.env, prompt模板）
  - ./data:/app/data        # SQLite 数据库
  - ./log:/app/log          # 日志文件
```

| 挂载目录 | 容器内路径 | 持久化内容 | 数据特性 |
|:---------|:-----------|:-----------|:---------|
| `conf/` | `/app/conf/` | `.env`, `prompt_templates.yml` | 配置可热修改（部分需重启） |
| `data/` | `/app/data/` | `data.db` (SQLite) | **可清理** — 有清理脚本 `scripts/pro/cleanup.sh` |
| `log/` | `/app/log/` | `app.log`, `api_out.log`, `api_err.log` | 滚动日志，保留最近 3 个备份 |

**设计意图**:

- 升级容器镜像时配置/数据不丢失
- 日志通过 `RotatingFileHandler` 自动滚动（10MB/文件，保留3个备份）
- data 目录可在需要时清空重建（`rm -rf data/data.db` 后重启自动重建表结构）

### 1.6 模块索引速查

按用户逻辑模块 → 代码文件映射：

| 逻辑模块 | 目录/文件 | 核心职责 | 章节 |
|:---------|:----------|:---------|:----:|
| **API 入口** | `api.py` | Flask 应用启动，加载环境变量，注册路由 | §3 |
| **UI 前端** | `ui.py` | Streamlit Dashboard，展示审查记录与统计 | §1.9 |
| **进程管理** | `conf/supervisord.conf` | Supervisor 配置，管理 api + dashboard 双进程 | §1.3 |
| **路由定义** | `biz/api/routes/` | WebHook 入口、健康检查、日报 | §3 |
| **事件分发** | `biz/api/routes/webhook.py` | 根据 object_kind 分发 Push/MR 事件 | §4 |
| **队列任务** | `biz/queue/worker.py` | 事件处理编排（去重/过滤/策略选择/回写） | §5 |
| **数据解析** | `biz/platforms/gitlab/webhook_handler.py` | PushHandler + MergeRequestHandler | §6 |
| **代码审查** | `biz/utils/code_reviewer.py` | CodeReviewer / AgenticReviewer | §7 |
| **飞书通知** | `biz/event/event_manager.py` | 事件驱动 → IM 通知 + 数据库入库 | §8 |
| **IM 发送** | `biz/utils/im/feishu.py` | 飞书卡片设计与发送 | §8.5 |
| **LLM 适配** | `biz/llm/factory.py` + `client/*` | Factory 模式，6 供应商 | §9 |
| **数据库** | `biz/service/review_service.py` | SQLite 双表 + 去重查询 | §10 |
| **实体定义** | `biz/entity/review_entity.py` | MergeRequestReviewEntity + PushReviewEntity | §1.7 |
| **Agentic** | `biz/agent/*` | ReAct 循环 + 安全沙箱 | §11 |
| **全仓审查** | `biz/cmd/review.py` | 命令行全仓库 Review | §1.10 |
| **员工映射** | `biz/employee_mapping.py` | 工号/拼音 → 中文姓名 | §1.8 |
| **配置模板** | `conf/prompt_templates.yml` | LLM Prompt 模板（Jinja2 渲染） | §1.11 |
| **工具集** | `biz/utils/*` | IM 通知、日志、配置自检、Token 截断等 | §8/§7 |

### 1.7 实体数据结构（entity/review_entity.py）

**文件**: `biz/entity/review_entity.py`

系统中定义了两个核心数据实体，承载审查结果的流转：

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class MergeRequestReviewEntity:
    """MR 审查结果实体"""
    project_name: str          # 项目名（从 webhook_data 解析）
    author: str                # 提交者
    source_branch: str         # 源分支
    target_branch: str         # 目标分支
    updated_at: int            # 更新时间戳
    commit_messages: str       # commit 消息汇总
    score: int                 # AI 评分
    url: str                   # MR 链接
    review_result: str         # AI 审查结果全文（markdown）
    additions: int             # 新增行数
    deletions: int             # 删除行数
    last_commit_id: str        # 最后一次 commit SHA（用于去重）
    url_slug: str              # GitLab URL slug（用于 IM webhook 查找）
    webhook_data: Any          # 原始 WebHook 数据（用于日报/扩展）

@dataclass
class PushReviewEntity:
    """Push 审查结果实体"""
    project_name: str          # 项目名
    author: str                # 提交者
    branch: str                # 分支名
    updated_at: int            # 时间戳
    commits: list              # commit 列表 [{'message','author','timestamp','url'}, ...]
    score: int                 # AI 评分
    review_result: str         # AI 审查结果
    additions: int
    deletions: int
    url_slug: str
    webhook_data: Any
```

**数据流路径**:

```ascii
worker.py 中完成 LLM 审查后
       |
       v
组装实体: MergeRequestReviewEntity(...) 或 PushReviewEntity(...)
       |
       +--> event_manager['xxx'].send(entity)     -> 通知 + 入库
       +--> handler.add_merge_request_notes(result) -> 回写 GitLab
```

**设计要点**:

- 使用 `@dataclass` 装饰器，简化构造（无样板代码）
- `url_slug` 是环境变量命名的关键：`FEISHU_WEBHOOK_URL_{SLUG}` 用于查找项目专用 Webhook
- `webhook_data` 保存原始数据，后续可通过日报路由提取更多信息
- `last_commit_id` 用于 MR 去重（同一 MR 新 push 后只审查一次）

### 1.8 员工姓名映射（employee_mapping.py）

**文件**: `biz/employee_mapping.py`

将 GitLab 中的工号/拼音用户名映射为中文姓名，用于 IM 通知中的"@某人"功能。

```python
# 工号 → 中文姓名映射
EMPLOYEE_ID_MAP = {
    "zhangsan": "张三",
    "lisi": "李四",
    "wangwu": "王五",
    ...
}

# 拼音用户名 → 中文姓名映射
USERNAME_TO_NAME_MAP = {
    "zhang_san": "张三",
    "li_si": "李四",
    ...
}

def get_chinese_name(username_or_id: str) -> str:
    """根据 GitLab 用户名/工号获取中文姓名"""
    return (
        EMPLOYEE_ID_MAP.get(username_or_id) or
        USERNAME_TO_NAME_MAP.get(username_or_id) or
        username_or_id  # 未找到则返回原始值
    )
```

**用途**: 在 IM 通知中显示中文姓名，便于团队识别和 @提醒。

### 1.9 Dashboard 前端（ui.py）

**文件**: `ui.py` — Streamlit 应用

```python
# ui.py — Streamlit Dashboard
import streamlit as st
from biz.service.review_service import ReviewService

st.set_page_config(page_title="AI Code Review Dashboard", layout="wide")

# 从 SQLite 读取数据
service = ReviewService()
mr_logs = service.get_all_mr_review_logs()
push_logs = service.get_all_push_review_logs()

# 项目级聚合统计
# - 各项目审查次数
# - 各开发者审查次数
# - 评分分布直方图
# - 按时间线展示审查记录

# 布局: 左侧筛选器 + 右侧详情
# - 下拉选择项目/开发者/日期范围
# - 审查结果详情（可展开）
```

**功能面板**:

```ascii
+-----------------------------------------------------+
|  AI Code Review Dashboard          [项目 v] [日期 v] |
+-----------------------------------------------------+
|  📊 概览统计卡                                        |
|  +------+ +------+ +------+ +------+               |
|  | 总审查| | 项目数| |开发人数| |平均分|               |
|  |  152  | |  12  | |  8   | | 72   |               |
|  +------+ +------+ +------+ +------+               |
+-----------------------------------------------------+
|  📈 趋势图                                          |
|  +------------------------------------------+      |
|  |  每日审查数量趋势 (折线图)                  |      |
|  +------------------------------------------+      |
|  +------------------------------------------+      |
|  |  各项目审查次数 (柱状图 / 饼图)             |      |
|  +------------------------------------------+      |
+-----------------------------------------------------+
|  📋 审查记录列表                                     |
|  +----+------+----+----+----+----+----------------+|
|  | ID |项目  |作者|评分|类型|时间| 详情           ||
|  +----+------+----+----+----+----+----------------+|
|  |  1 | svc  |张三| 85 | MR |...| [查看]         ||
|  |  2 | web  |李四| 67 |Push|...| [查看]         ||
|  +----+------+----+----+----+----+----------------+|
+-----------------------------------------------------+
```

**Dashboard 侧边栏**: 顶部展示概览统计卡（总审查数 / 项目数 / 开发者数 / 平均分），主体包含趋势图、各项目分布、审查记录列表，支持按项目/开发者/日期范围筛选。

### 1.10 全仓库 Review 命令（cmd/review.py）

**文件**: `biz/cmd/review.py` — 命令行全仓库代码审查

```python
# 运行方式: python -m biz.cmd.review --url <gitlab_url> --token <token> --project <id>

def review_project(project_id, gitlab_url, token, branch="main"):
    """
    全仓库 Review 流程:
    1. 获取项目所有文件列表
    2. 逐个文件获取内容
    3. 分批送 LLM 审查
    4. 汇总审查报告
    """
```

**用途**:

- 对存量项目做一次性全量代码审查
- 建立基线质量评分
- 与 WebHook 收到的增量审查形成互补

**切入时机**: 项目初次接入 AI CR 时执行一次，后续通过 WebHook 做增量。全量结果存入 Dashboard 作为基线对比。

### 1.11 Conf 配置设计（prompt_templates.yml）

**文件**: `conf/prompt_templates.yml` — LLM Prompt 模板

```yaml
code_review_prompt:
  system_prompt: |
    你是一位专业的代码审查专家。请根据以下标准对代码进行审查：
    1. 功能实现的正确性与健壮性（40分）
    2. 安全性与潜在风险（30分）
    3. 是否符合最佳实践（20分）
    4. 性能与资源利用效率（5分）
    5. Commits 信息清晰性（5分）

    请严格按照以下 JSON 格式输出（不要额外内容）：
    ```json
    {
      "score": 总分,
      "issues": [
        {"severity": "P0/P1/P2", "file": "xxx", "line": 行号, "desc": "问题描述"},
        ...
      ],
      "summary": "总体评价（中文）"
    }
    ```

    审查风格：{{ style }}

  user_prompt: |
    以下是一段代码变更（diff）：
    {diffs_text}

    提交信息：{commits_text}

    请进行代码审查，并给出 0-100 分的总分。

agentic_prompt:
  # Agentic 模式下使用的 Prompt
  ...

daily_report_prompt:
  # 日报生成 Prompt
  ...
```

**关键设计**:

- **Jinja2 渲染**: `{{ style }}` / `{diffs_text}` 占位符，运行时填充
- **分层模板**: code_review_prompt / agentic_prompt / daily_report_prompt 三套
- **外部挂载**: 部署后可不重启直接修改 Prompt 内容
- **JSON 输出**: 要求 LLM 以 JSON 格式输出，便于解析评分和问题列表

---

## 2. 核心数据流全链路分析

```ascii
GitLab WebHook POST
   |
   v
+--------------------------------------------------------------------+
| §3. API 路由 (biz/api/routes/webhook.py)                          |
| webhook_route() 接收 POST /review/webhook                         |
|    +- 提取 X-Gitlab-Event / X-Gitlab-Token 等 Header              |
|    +- token 解析 (env > header)                                   |
+--------------------------------------------------------------------+
   |
   v
+--------------------------------------------------------------------+
| §4. 事件类型判断 (同上文件)                                         |
|    +- object_kind == "push"             -> handle_push_event()      |
|    +- object_kind == "merge_request"    -> handle_merge_request_event()|
|    +- 其他                                                          |
+--------------------------------------------------------------------+
   |
   v
+--------------------------------------------------------------------+
| §5. 队列任务执行 (biz/queue/worker.py)                             |
| handle_push_event / handle_merge_request_event                     |
|    +- 判断草稿(draft) -> 仅通知不审查                                |
|    +- 判断受保护分支过滤                                            |
|    +- 去重检查 (last_commit_id)                                     |
|    +- 进入审查流程                                                 |
+--------------------------------------------------------------------+
   |
   v
+--------------------------------------------------------------------+
| §6. 数据解析 (biz/platforms/gitlab/webhook_handler.py)             |
|    +- PushHandler: get_push_commits() -> get_push_changes()         |
|    |   -> repository_compare() / get_commit_diff()                  |
|    +- MergeRequestHandler: get_merge_request_commits()             |
|        -> get_merge_request_changes() -> GitLab API /changes         |
|                                                                     |
|    filter_changes(): 文件类型过滤 + 删除文件过滤 + diff统计         |
+--------------------------------------------------------------------+
   |
   v
+--------------------------------------------------------------------+
| §7. 代码评审引擎 (biz/utils/code_reviewer.py)                      |
|    _review_with_strategy()                                          |
|       +- REVIEW_STRATEGY=diff_only (默认)                          |
|       |   -> CodeReviewer.review_code(changes, commits_text)        |
|       |   -> LLM 调用 -> review_result                               |
|       |                                                             |
|       +- REVIEW_STRATEGY=agentic                                    |
|           -> AgenticReviewer.review(diffs, commits)                 |
|           -> 仓库克隆->工具调用循环->LLM 探索->review_result           |
|           -> 失败自动降级为 diff_only                               |
+--------------------------------------------------------------------+
   |
   v
+--------------------------------------------------------------------+
| 结果处理 (biz/queue/worker.py 末尾)                                 |
|    +- handler.add_merge_request_notes(review_result)               |
|    |   -> GitLab API POST /notes (行内批注)                         |
|    +- event_manager['merge_request_reviewed'].send(entity)         |
|        |                                                           |
|        v                                                           |
+--------------------------------------------------------------------+
| §8. 飞书通知体系 (biz/event/event_manager.py)                      |
|    on_merge_request_reviewed(entity):                               |
|       +- 拼接 IM 消息 Markdown                                      |
|       +- notifier.send_notification() -> 飞书/钉钉/企微/自定义      |
|       +- ReviewService().insert_mr_review_log(entity) -> SQLite     |
+--------------------------------------------------------------------+
```

---

## 3. API 定义与路由

### 3.1 WebHook 路由（主入口）

**文件**: `biz/api/routes/webhook.py`

```python
@webhook_bp.route('/review/webhook', methods=['POST'])
def webhook_route():
    """统一 WebHook 入口，接收 GitLab/GitHub/Gitea 推送"""
```

**关键职责**:

```python
def webhook_route():
    # ① 解析请求来源 (GitLab / GitHub / Gitea)
    #    通过 X-Gitlab-Event / X-GitHub-Event / X-Gitea-Event 区分

    # ② 解析 Token（优先级: .env > WebHook Secret Token）
    #    - 优先使用 .env 中的 GITLAB_ACCESS_TOKEN
    #    - 未配置时回退到 request.headers 中的 X-Gitlab-Token

    # ③ 解析 GitLab URL（老版本需从 .env 读取）
    #    slugify_url(url) → 生成 url_slug 用于环境变量匹配

    # ④ 分派到对应处理函数
    if webhook_data.get('object_kind') == 'push':
        return handle_push_event(webhook_data, token, gitlab_url, url_slug)
    elif webhook_data.get('object_kind') == 'merge_request':
        return handle_merge_request_event(webhook_data, token, gitlab_url, url_slug)
```

### 3.2 健康检查路由

**文件**: `biz/api/routes/home.py`

```python
@home_bp.route('/')
def home():
    return "The code review server is running."
```

### 3.3 日报路由

**文件**: `biz/api/routes/daily_report.py`

```python
@daily_report_bp.route('/review/daily_report', methods=['GET'])
def daily_report():
    # 当日 Push/MR 记录 → LLM 生成日报 → 推送到 IM
```

---

## 4. 事件类型判断与分发

**位置**: `biz/api/routes/webhook.py` → `biz/queue/worker.py`

路由层收到 WebHook POST 后，根据 `object_kind` 字段分发：

### 4.1 Push 事件流程

```python
# webhook.py 中直接调用
handle_push_event(webhook_data, gitlab_token, gitlab_url, gitlab_url_slug)
```

### 4.2 Merge Request 事件流程

```python
handle_merge_request_event(webhook_data, gitlab_token, gitlab_url, gitlab_url_slug)
```

**分发逻辑（路由层简化）**:

```python
# 通过 event_name / object_kind 区分事件类型
event_type = (
    headers.get('X-Gitlab-Event') or      # GitLab
    headers.get('X-GitHub-Event') or      # GitHub
    headers.get('X-Gitea-Event') or       # Gitea
    ''
).lower()
```

---

## 5. 队列任务执行逻辑

**文件**: `biz/queue/worker.py` (24KB, 核心编排文件，~500行)

### 5.1 事件分派架构

```ascii
Worker 函数                           处理的事件来源
------------------------------------------------------
handle_push_event()                   <- GitLab Push
handle_merge_request_event()          <- GitLab MR
handle_github_push_event()            <- GitHub Push
handle_github_pull_request_event()    <- GitHub PR
handle_gitea_push_event()             <- Gitea Push
handle_gitea_pull_request_event()     <- Gitea PR
```

### 5.2 Push 事件处理

```python
def handle_push_event(webhook_data, gitlab_token, gitlab_url, gitlab_url_slug):
    # ① 判断 PUSH_REVIEW_ENABLED
    push_review_enabled = os.environ.get('PUSH_REVIEW_ENABLED', '0') == '1'

    # ② 创建 PushHandler 解析数据
    handler = PushHandler(webhook_data, gitlab_token, gitlab_url)
    commits = handler.get_push_commits()

    if push_review_enabled:
        # ③ 获取 Push 变更（diff）
        changes = handler.get_push_changes()
        changes = filter_changes(changes)  # 过滤文件类型

        # ④ 分析代码
        commits_text = ';'.join(c['message'] for c in commits)
        review_result = _review_with_strategy(changes, commits_text, webhook_data, gitlab_url)
        score = CodeReviewer.parse_review_score(review_result)

        # ⑤ 回写 GitLab commit 评论
        handler.add_push_notes(f'Auto Review Result: \n{review_result}')

    # ⑥ 发送事件
    event_manager['push_reviewed'].send(PushReviewEntity(...))
```

### 5.3 MR 事件处理

```python
def handle_merge_request_event(webhook_data, gitlab_token, gitlab_url, gitlab_url_slug):
    # ① 创建 MergeRequestHandler
    handler = MergeRequestHandler(webhook_data, gitlab_token, gitlab_url)

    # ② 草稿判断 — 不审查
    if is_draft:
        notifier.send_notification("MR为草稿...")
        return

    # ③ 受保护分支过滤
    if MERGE_REVIEW_ONLY_PROTECTED_BRANCHES_ENABLED and not handler.target_branch_protected():
        return

    # ④ 仅处理 open / update 动作
    if handler.action not in ['open', 'update']:
        return

    # ⑤ 去重 — 检查 last_commit_id 是否已经审查过
    if ReviewService.check_mr_last_commit_id_exists(project_name, source, target, last_commit_id):
        return  # 已审查过，跳过

    # ⑥ 获取 changes 和 commits
    changes = handler.get_merge_request_changes()
    changes = filter_changes(changes)
    commits_text = ';'.join(c['message'] for c in handler.get_merge_request_commits())

    # ⑦ AI 审查
    review_result = _review_with_strategy(changes, commits_text, webhook_data, gitlab_url)

    # ⑧ 回写 GitLab MR Notes
    handler.add_merge_request_notes(f'Auto Review Result: \n{review_result}')

    # ⑨ 发送事件
    event_manager['merge_request_reviewed'].send(MergeRequestReviewEntity(...))
```

### 5.4 GitHub/Gitea 适配

GitHub 和 Gitea 的处理函数结构与 GitLab 类似，通过**策略模式**隔离差异：

| 平台 | Handler 类 | 获取 Changes | 回写 Notes |
|:-----|:-----------|:-------------|:-----------|
| GitLab | `PushHandler` / `MergeRequestHandler` | `get_push_changes()` / `get_merge_request_changes()` | `add_push_notes()` / `add_merge_request_notes()` |
| GitHub | `PushHandler` / `PullRequestHandler` | `get_push_changes()` / `get_pull_request_changes()` | `add_push_notes()` / `add_pull_request_notes()` |
| Gitea | `PushHandler` / `PullRequestHandler` | `get_push_changes()` / `get_pull_request_changes()` | `add_push_notes()` / `add_pull_request_notes()` |

---

## 6. 数据解析：WebHook 数据结构

**文件**: `biz/platforms/gitlab/webhook_handler.py` (13.9KB)

### 6.1 PushHandler 解析

```python
class PushHandler:
    """处理 GitLab Push WebHook 事件"""

    def parse_push_event(self):
        self.project_id = self.webhook_data.get('project_id') or webhook_data['project']['id']
        self.branch_name = self.webhook_data['ref'].replace('refs/heads/', '')
        self.commit_list = self.webhook_data.get('commits', [])

    def get_push_commits(self) -> list:
        """从 WebHook 数据中提取 commits（不调 GitLab API）"""
        return [{'message': c['message'], 'author': c['author']['name'],
                 'timestamp': c['timestamp'], 'url': c['url']} for c in self.commit_list]

    def get_push_changes(self) -> list:
        """获取 Push 的 diff 变更"""
        before = self.webhook_data['before']
        after = self.webhook_data['after']

        if after.startswith('0000000'):         # 删除分支 → 空列表
            return []
        if before.startswith('0000000'):         # 创建分支 → get_commit_diff()
            return self.get_commit_diff(after)
        return self.repository_compare(before, after)  # 正常对比 → compare API

    def repository_compare(self, before, after):
        """GitLab API: /api/v4/projects/{id}/repository/compare?from={before}&to={after}"""

    def add_push_notes(self, message):
        """回写评论到最后一次 commit: POST /api/v4/projects/{id}/repository/commits/{sha}/comments"""
```

**关键设计 —— Push 变更的三种情况**:

```ascii
                    Push WebHook 到达
                           |
            +--------------+--------------+
            v              v              v
     before=0000...   after=0000...    正常
     (创建分支)        (删除分支)      (commit 对比)
         |               |              |
         v               v              v
    get_commit_diff()  返回 []     repository_compare()
    (单个commit diff)            (from...to 范围diff)
```

### 6.2 MergeRequestHandler 解析

```python
class MergeRequestHandler:
    def parse_merge_request_event(self):
        mr = self.webhook_data['object_attributes']
        self.merge_request_iid = mr['iid']
        self.project_id = mr['target_project_id']
        self.action = mr['action']  # 'open' / 'update' / 'merge' / 'close'

    def get_merge_request_changes(self) -> list:
        """GitLab API: /api/v4/projects/{id}/merge_requests/{iid}/changes?access_raw_diffs=true
           重试机制: 最多3次，间隔10秒（应对GitLab API延迟）"""

    def get_merge_request_commits(self) -> list:
        """GitLab API: /api/v4/projects/{id}/merge_requests/{iid}/commits"""

    def add_merge_request_notes(self, review_result):
        """回写 MR Notes: POST /api/v4/projects/{id}/merge_requests/{iid}/notes"""

    def target_branch_protected(self) -> bool:
        """检查目标分支是否受保护: GET /api/v4/projects/{id}/protected_branches
           使用 fnmatch 做通配符匹配（支持 main, develop, release-* 等模式）"""
```

**关键设计 —— changes API 延迟重试**:

```python
# GitLab 在 MR 刚创建时 changes API 可能返回空
# 策略: 最多重试3次，每次间隔10秒
for attempt in range(3):
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json().get('changes'):
        return changes
    time.sleep(10)
return []  # 最终重试失败
```

### 6.3 filter_changes 过滤逻辑

**位置**: `biz/platforms/gitlab/webhook_handler.py` 顶层函数

```python
def filter_changes(changes: list) -> list:
    """过滤数据，只保留支持的文件类型以及必要的字段信息"""

    # ① 从环境变量读取支持的文件后缀
    supported_extensions = os.getenv('SUPPORTED_EXTENSIONS', '.java,.py,.php').split(',')

    # ② 过滤掉已删除的文件
    filter_deleted_files_changes = [c for c in changes if not c.get("deleted_file")]

    # ③ 按后缀过滤 + 保留必要字段
    filtered_changes = [
        {
            'diff': item.get('diff', ''),
            'new_path': item['new_path'],
            'additions': len(re.findall(r'^\+(?!\+\+)', item.get('diff', ''), re.MULTILINE)),
            'deletions': len(re.findall(r'^-(?!--)', item.get('diff', ''), re.MULTILINE))
        }
        for item in filter_deleted_files_changes
        if any(item.get('new_path', '').endswith(ext) for ext in supported_extensions)
    ]
    return filtered_changes
```

**过滤维度**:

| 过滤条件 | 说明 | 代码实现 |
|:---------|:------|:---------|
| 删除的文件 | 已删除文件不送审 | `not item.get("deleted_file")` |
| 文件后缀 | 仅审查支持的类型 | `new_path.endswith(ext)` |
| 字段精简 | 保留 diff/new_path/additions/deletions | 字典投影 |

### 6.4 slugify_url 工具

```python
def slugify_url(original_url: str) -> str:
    """
    URL → 下划线分隔的文件名格式 slug
    例: "https://gitlab.example.com" → "gitlab_example_com"
    用途: 用于匹配项目对应的 IM Webhook 环境变量名
    """
    url = re.sub(r'^https?://', '', original_url)
    slug = re.sub(r'[^a-zA-Z0-9]', '_', url)
    return slug.rstrip('_')
```

---

## 7. 代码评审引擎

### 7.1 Review 策略选择

**文件**: `biz/queue/worker.py`

```python
def _review_with_strategy(changes, commits_text, webhook_data, gitlab_url) -> str:
    strategy = os.getenv("REVIEW_STRATEGY", "diff_only")

    if strategy != "agentic":
        return CodeReviewer().review_and_strip_code(str(changes), commits_text)

    # Agentic 模式
    from biz.agent.agentic_reviewer import AgenticReviewer
    repo_url, repo_key, ref = _resolve_repo_for_event(webhook_data, gitlab_url)
    if not (repo_url and repo_key and ref):
        # 降级: 无法解析仓库信息 → diff_only
        return CodeReviewer().review_and_strip_code(str(changes), commits_text)

    cache_root = os.getenv("REPO_CACHE_DIR", "data/repo_cache")
    try:
        reviewer = AgenticReviewer(repo_url=repo_url, repo_key=repo_key, ref=ref, cache_root=cache_root)
        return reviewer.review(diffs_text=str(changes), commits_text=commits_text)
    except Exception as e:
        logger.error("agentic reviewer raised, fallback to diff_only: %s", e)
        return CodeReviewer().review_and_strip_code(str(changes), commits_text)
```

**策略矩阵**:

| 模式 | 策略值 | 审查方式 | 适用场景 | 成本 |
|:-----|:-------|:---------|:---------|:----:|
| **diff_only**（默认） | `diff_only` | 仅基于 diff 文本审查 | 快速常规审查 | 低 |
| **agentic** | `agentic` | 克隆仓库 + 工具调用探索 | 深度上下文审查 | 高 |

### 7.2 BaseReviewer 基类

**文件**: `biz/utils/code_reviewer.py`

```python
class BaseReviewer(abc.ABC):
    """代码审查基类"""

    def __init__(self, prompt_key: str):
        self.client = Factory().getClient()          # 创建 LLM 客户端
        self.prompts = self._load_prompts(prompt_key) # 加载 Prompt 模板

    def _load_prompts(self, prompt_key, style="professional"):
        """从 conf/prompt_templates.yml 加载 Prompt，Jinja2 渲染"""
        with open("conf/prompt_templates.yml", "r", encoding="utf-8") as f:
            prompts = yaml.safe_load(f).get(prompt_key, {})

        system_prompt = Template(prompts["system_prompt"]).render(style=style)
        user_prompt = Template(prompts["user_prompt"]).render(style=style)

        return {
            "system_message": {"role": "system", "content": system_prompt},
            "user_message": {"role": "user", "content": user_prompt},
        }

    def call_llm(self, messages) -> str:
        """调用 LLM 进行代码审核"""
        return self.client.completions(messages=messages)

    @abc.abstractmethod
    def review_code(self, *args, **kwargs) -> str:
        pass
```

### 7.3 CodeReviewer（diff_only 模式）

```python
class CodeReviewer(BaseReviewer):
    """代码 Diff 级别的审查 — 默认模式"""

    def __init__(self):
        super().__init__("code_review_prompt")  # 使用 code_review_prompt 模板

    def review_and_strip_code(self, changes_text, commits_text=""):
        """审查 + 格式清理"""
        # Token 超长截断
        max_tokens = int(os.getenv("REVIEW_MAX_TOKENS", 10000))
        if count_tokens(changes_text) > max_tokens:
            changes_text = truncate_text_by_tokens(changes_text, max_tokens)

        result = self.review_code(changes_text, commits_text).strip()
        # 去除 markdown 代码块包装
        if result.startswith("```markdown") and result.endswith("```"):
            return result[11:-3].strip()
        return result

    def review_code(self, diffs_text, commits_text=""):
        messages = [
            self.prompts["system_message"],
            {
                "role": "user",
                "content": self.prompts["user_message"]["content"].format(
                    diffs_text=diffs_text, commits_text=commits_text
                ),
            },
        ]
        return self.call_llm(messages)
```

### 7.4 AgenticReviewer（agentic 模式）

**文件**: `biz/agent/agentic_reviewer.py`

```python
class AgenticReviewer:
    """基于 Agent 的代码审查器 — 自主探索代码仓库"""

    def __init__(self, repo_url, repo_key, ref, cache_root):
        # repo_syncer: 克隆/更新仓库到本地缓存
        self.syncer = RepoSyncer(repo_url, repo_key, cache_root)
        self.ref = ref

        # llm_adapter: OpenAI 兼容的 LLM 调用
        self.llm = LLMAdapter()

        # tool_registry: 注册可用工具
        self.tools = ToolRegistry()
        self.tools.register(ReadFileTool())
        self.tools.register(ShellTool())  # 沙箱模式

    def review(self, diffs_text, commits_text):
        # ① 同步仓库到本地
        repo_path = self.syncer.sync()

        # ② 构建初始消息
        system_prompt = self._build_prompt(repo_path)

        # ③ runner 执行 ReAct 循环
        runner = Runner(self.llm, self.tools, system_prompt)
        result = runner.run(diffs_text, commits_text)

        return result
```

**Agentic 流程图**:

```ascii
AgenticReviewer.review()
    |
    +- 1. RepoSyncer.sync()
    |      +- 检查缓存是否存在
    |      +- 不存在 -> git clone
    |      +- 存在 -> git fetch + git checkout
    |      +- 返回 repo_path
    |
    +- 2. Runner.run(diffs, commits)
    |      +- 系统 Prompt + 用户 diff
    |      +- ReAct 循环（最多 20 轮）:
    |      |   +- LLM 输出：思考 + 工具调用
    |      |   +- 执行工具（ReadFile / Shell 沙箱）
    |      |   +- 结果返回给 LLM
    |      +- 输出最终审查报告
    |
    +- 3. 返回审查结果
```

### 7.5 评分解析

```python
@staticmethod
def parse_review_score(review_text: str) -> int:
    """从 AI 返回的文本中提取总分"""
    if not review_text:
        return 0
    match = re.search(r"总分[:：]\s*(\d+)分?", review_text)
    return int(match.group(1)) if match else 0
```

**评分维度**（来自 Prompt 模板 `conf/prompt_templates.yml`）:

| 维度 | 分值 | 说明 |
|:-----|:----:|:------|
| 功能实现的正确性与健壮性 | 40 | 逻辑正确、边界处理、异常输入 |
| 安全性与潜在风险 | 30 | SQL注入、XSS、密钥泄露等 |
| 是否符合最佳实践 | 20 | 命名规范、注释清晰度、代码结构 |
| 性能与资源利用效率 | 5 | 资源浪费、性能瓶颈 |
| Commits 信息清晰性 | 5 | 提交信息是否清晰便于追溯 |

---

## 8. 飞书通知体系

### 8.1 EventManager 事件驱动架构

**文件**: `biz/event/event_manager.py`

基于 `blinker` 库的 Signal-Connect 事件驱动模式：

```python
from blinker import Signal

# 定义全局事件信号
event_manager = {
    "merge_request_reviewed": Signal(),   # MR 审查完成信号
    "push_reviewed": Signal(),            # Push 审查完成信号
}

# 注册事件处理函数
event_manager["merge_request_reviewed"].connect(on_merge_request_reviewed)
event_manager["push_reviewed"].connect(on_push_reviewed)
```

```ascii
                    worker.py 中完成审查
                           |
               event_manager['xxx'].send(entity)
                           |
                +----------+----------+
                v                     v
    on_merge_request_reviewed()    on_push_reviewed()
                |                     |
        +-------+-------+    +-------+-------+
        v               v    v               v
    IM 通知         SQLite    IM 通知      SQLite
    (飞书/钉钉/企微)  入库    (飞书/钉钉/企微) 入库
```

### 8.2 MR 审查事件处理

```python
def on_merge_request_reviewed(mr_review_entity: MergeRequestReviewEntity):
    # ① 拼接消息内容（Markdown 格式）
    im_msg = f"""
### 🔀 {mr_review_entity.project_name}: Merge Request
#### 合并请求信息:
- **提交者:** {mr_review_entity.author}
- **源分支**: {mr_review_entity.source_branch}
- **目标分支**: {mr_review_entity.target_branch}
- **更新时间**: {mr_review_entity.updated_at}
- **提交信息:** {mr_review_entity.commit_messages}
- [查看合并详情]({mr_review_entity.url})
- **AI Review 结果:**
{mr_review_entity.review_result}
"""

    # ② 发送 IM 通知
    notifier.send_notification(content=im_msg, msg_type='markdown',
                               title='Merge Request Review',
                               project_name=mr_review_entity.project_name,
                               url_slug=mr_review_entity.url_slug,
                               webhook_data=mr_review_entity.webhook_data)

    # ③ 持久化到数据库
    ReviewService().insert_mr_review_log(mr_review_entity)
```

### 8.3 Push 审查事件处理

```python
def on_push_reviewed(entity: PushReviewEntity):
    # ① 拼接消息（列出每条 commit）
    im_msg = f"### 🚀 {entity.project_name}: Push\n\n"
    for commit in entity.commits:
        im_msg += (f"- **提交信息**: {commit['message']}\n"
                   f"- **提交者**: {commit['author']}\n"
                   f"- **时间**: {commit['timestamp']}\n"
                   f"- [查看提交详情]({commit['url']})\n\n")
    if entity.review_result:
        im_msg += f"#### AI Review 结果: \n{entity.review_result}\n\n"

    # ② 发送 + ③ 入库
    notifier.send_notification(...)
    ReviewService().insert_push_review_log(entity)
```

### 8.4 Notifier 统一分发

**文件**: `biz/utils/im/notifier.py`

```python
def send_notification(content, msg_type='text', title="通知",
                      is_at_all=False, project_name=None,
                      url_slug=None, webhook_data={}):
    """同时推送所有已启用的 IM 平台"""

    # 钉钉
    DingTalkNotifier().send_message(content, msg_type, title, is_at_all, project_name, url_slug)

    # 企业微信
    WeComNotifier().send_message(content, msg_type, title, is_at_all, project_name, url_slug)

    # 飞书
    FeishuNotifier().send_message(content, msg_type, title, is_at_all, project_name, url_slug)

    # 自定义 Webhook
    ExtraWebhookNotifier().send_message(system_data, webhook_data)
```

**关键设计点**:

1. **多平台同时推送** — 所有启用的 IM 平台都会收到
2. **项目级 Webhook 路由** — 通过 `project_name` 和 `url_slug` 从环境变量 `FEISHU_WEBHOOK_URL_{PROJECT_NAME}` 查找专用 Webhook URL
3. **降级策略** — 未找到项目专用 URL 时降级到全局 URL

### 8.5 FeishuNotifier 卡片设计

**文件**: `biz/utils/im/feishu.py`

```python
class FeishuNotifier:
    def __init__(self):
        self.default_webhook_url = os.environ.get('FEISHU_WEBHOOK_URL', '')
        self.enabled = os.environ.get('FEISHU_ENABLED', '0') == '1'

    def _get_webhook_url(self, project_name=None, url_slug=None):
        """多级 Webhook URL 查找"""
        # ① 精确匹配: FEISHU_WEBHOOK_URL_{PROJECT_NAME}
        # ② Slug 匹配: FEISHU_WEBHOOK_URL_{URL_SLUG}
        # ③ 降级: 默认 FEISHU_WEBHOOK_URL
        # ④ 无兜底: 抛出 ValueError
```

**飞书消息卡片结构**（markdown 类型 → 转为 interactive card）:

```json
{
    "msg_type": "interactive",
    "card": {
        "schema": "2.0",
        "config": {
            "update_multi": true,
            "style": {"text_size": {"normal_v2": {"default": "normal"}}}
        },
        "header": {
            "title": {"tag": "plain_text", "content": title},
            "template": "blue",
            "padding": "12px 12px 12px 12px"
        },
        "body": {
            "direction": "vertical",
            "padding": "12px 12px 12px 12px",
            "elements": [
                {
                    "tag": "markdown",
                    "content": content,
                    "text_align": "left",
                    "text_size": "normal_v2"
                }
            ]
        }
    }
}
```

**卡片渲染效果**:

```ascii
+--------------------------------------------+
|  🔀 project-name: Merge Request         <- header (blue) |
+--------------------------------------------+
| 合并请求信息:                               |
| - 提交者: zhang_san                        |
| - 源分支: feature/xxx                      |
| - 目标分支: main                           |
| - 更新时间: 2026-07-10 14:30:00            |
| - 提交信息: fix: null pointer issue         |
| - [查看合并详情]()                          |
|                                            |
| AI Review 结果:                             |
| ### 发现的问题                             |
| 1. [P0] auth.c:45 空指针风险...            |
| 2. [P1] config.c:102 缺少边界检查...       |
| ...                                        |
|                                            |
| 总分: 75分                                 |
+--------------------------------------------+
```

---

## 9. LLM 供应商适配层

**文件**: `biz/llm/factory.py`

```python
class Factory:
    @staticmethod
    def getClient(provider=None) -> BaseClient:
        provider = provider or os.getenv("LLM_PROVIDER", "anthropic")
        return {
            'anthropic': AnthropicClient,
            'zhipuai': ZhipuAIClient,
            'openai': OpenAIClient,
            'deepseek': DeepSeekClient,
            'qwen': QwenClient,
            'ollama': OllamaClient,
        }[provider]()
```

**抽象基类** (`biz/llm/client/base.py`):

```python
class BaseClient(abc.ABC):
    @abc.abstractmethod
    def completions(self, messages: list) -> str: ...

    @abc.abstractmethod
    def ping(self) -> bool: ...
```

**以 DeepSeek 为例** (`biz/llm/client/deepseek.py`):

```python
class DeepSeekClient(BaseClient):
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_API_BASE_URL", "https://api.deepseek.com")
        self.model = os.getenv("DEEPSEEK_API_MODEL", "deepseek-chat")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def completions(self, messages):
        response = self.client.chat.completions.create(
            model=self.model, messages=messages, temperature=0.1
        )
        return response.choices[0].message.content

    def ping(self):
        try:
            self.client.models.list()
            return True
        except:
            return False
```

**注意**: 所有供应商都通过 OpenAI 兼容的 SDK 调用，只有 Anthropic 使用原生 SDK。

---

## 10. 数据库设计

**文件**: `biz/service/review_service.py`

采用 SQLite 本地数据库，两张表：

**mr_review_log 表**:

```sql
CREATE TABLE mr_review_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name    TEXT,        -- 项目名称
    author          TEXT,        -- 提交者
    source_branch   TEXT,        -- 源分支
    target_branch   TEXT,        -- 目标分支
    updated_at      INTEGER,     -- 更新时间戳
    commit_messages TEXT,        -- 合并的 commit 信息
    score           INTEGER,     -- AI 评分
    url             TEXT,        -- MR 链接
    review_result   TEXT,        -- AI 审查结果全文
    additions       INTEGER DEFAULT 0,   -- 新增行数
    deletions       INTEGER DEFAULT 0,   -- 删除行数
    last_commit_id  TEXT DEFAULT ''      -- 最后一次 commit SHA（去重用）
);

CREATE INDEX idx_mr_review_log_updated_at ON mr_review_log(updated_at);
```

**push_review_log 表**:

```sql
CREATE TABLE push_review_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name    TEXT,
    author          TEXT,
    branch          TEXT,
    updated_at      INTEGER,
    commit_messages TEXT,
    score           INTEGER,
    review_result   TEXT,
    additions       INTEGER DEFAULT 0,
    deletions       INTEGER DEFAULT 0
);

CREATE INDEX idx_push_review_log_updated_at ON push_review_log(updated_at);
```

**关键查询 — 去重检查**:

```python
@staticmethod
def check_mr_last_commit_id_exists(project_name, source_branch, target_branch, last_commit_id):
    """检查同一 MR 的最新 commit 是否已经审查过，防止重复审查"""
```

---

## 11. Agentic Review 模式分析

**目录**: `biz/agent/` — 8 个文件，Agent 模式下 LLM 可自主探索代码库

**组件关系**:

```ascii
AgenticReviewer
    +-- RepoSyncer        — 仓库克隆/同步
    +-- LLMAdapter        — 与 LLM 通信 (OpenAI 兼容)
    +-- Runner            — ReAct 循环执行器
    |   +-- ToolRegistry  — 工具注册中心
    |   |   +-- ReadFileTool   — 读取文件
    |   |   +-- ShellTool      — 沙箱 shell 命令
    |   +-- Safety        — 安全沙箱（白名单+黑名单+路径越界检查）
    +-- prompts.py        — 系统 Prompt 定义
```

**Runner ReAct 循环**:

```python
class Runner:
    def run(self, diffs_text, commits_text):
        # 最大迭代次数
        max_iterations = int(os.getenv("AGENT_MAX_ITERATIONS", 20))

        for i in range(max_iterations):
            # ① 调用 LLM
            response = self.llm.chat(messages)

            # ② 解析 LLM 输出
            if "FINAL ANSWER:" in response:
                return response  # 结束

            # ③ 解析工具调用
            tool_name, tool_args = parse_tool_call(response)

            # ④ 执行工具（沙箱保护）
            result = self.tool_registry.execute(tool_name, tool_args)

            # ⑤ 结果返回给 LLM
            messages.append({"role": "tool", "content": result})

        return "Agentic review reached max iterations"  # 超限回退
```

**安全沙箱机制** — `safety.py`:

```python
class Safety:
    ALLOWED = {'ls', 'cat', 'head', 'tail', 'grep', 'find', 'wc', 'git', 'rg', 'tree'}
    BLOCKED = {'rm', 'mv', 'cp', 'chmod', 'chown', 'curl', 'wget', 'sudo', 'touch'}

    def check(self, command: str) -> bool:
        # 白名单检查
        # 黑名单检查
        # 路径越界检查（禁止访问 repo_path 之外）
        # 30s 超时
        return safe
```

---

## 12. 后续规划

### 12.1 未来规划

| 优先级 | 方向 | 说明 |
|:------:|:-----|:------|
| P0 | **RAG 知识库增强** | 将项目编码规范、历史审查经验、常见问题模式构建为向量知识库，提升审查准确性 |
| P0 | **数据飞轮** | 建立"采集→模型定制→反馈→数据更新"闭环，持续优化模型 |
| P1 | **全仓库 Review** | 已提供 `python -m biz.cmd.review` 命令行，强化全仓扫描能力 |
| P1 | **多模型融合** | 差异化模型处理不同维度（安全→专用模型，规范→轻量模型） |
| P2 | **Priview Review** | GitLab WebIDE 插件，提交前即可预览结果 |
| P2 | **质量门禁集成** | 与 CI/CD 流水线联动，评分不达标阻断合并 |

### 12.2 RAG 搭建思路

```ascii
+----------------------+    +----------------------+
|  企业编码规范          |    |  历史审查案例          |
|  (.md/.pdf)           |    |  (SQLite 数据)         |
+---------+------------+    +-----------+----------+
          |                             |
          v                             v
+-------------------------------------------+
|              Embedding 模型                |
|    (text2vec / BGE / 通义百炼)             |
+-------------------+-----------------------+
                    |
                    v
+-------------------------------------------+
|              向量数据库                     |
|    (Milvus / Chroma / Faiss)              |
+-------------------+-----------------------+
                    |
                    v
+-------------------------------------------+
|        AI Code Review 检索增强流程          |
|                                            |
|  用户提交代码 diff                          |
|       |                                     |
|       v                                     |
|  ① 提取代码中的关键特征（函数名/API/模式）    |
|  ② 向量检索相似问题/规范                    |
|  ③ 将检索结果作为 Prompt 上下文注入          |
|  ④ LLM 生成更准确的审查结果                  |
+-------------------------------------------+
```

**RAG 带来的改进**:

| 维度 | 当前（纯 LLM） | 引入 RAG 后 |
|:-----|:--------------|:------------|
| 规范遵循 | 依赖 LLM 训练数据中的通用规则 | 精准匹配企业自定义规范 |
| 历史复用 | 每次独立审查 | 可参考类似问题的历史审查结论 |
| 误报率 | 较高（无上下文） | 检索上下文后显著降低 |
| 漏报率 | 依赖 Prompt 质量 | 历史案例补充覆盖盲区 |

### 12.3 模型精调 + 数据飞轮

```ascii
              +------------------------------+
              |      数据采集层               |
              |  +- AI 审查结果+人工修正      |
              |  +- 用户反馈标记（误报/漏报）  |
              |  +- 人工 Review 结论          |
              +-------------+----------------+
                            |
                            v
              +------------------------------+
              |      数据清洗与标注            |
              |  +- 去重/去噪                 |
              |  +- 格式标准化                |
              |  +- 质量分级                  |
              +-------------+----------------+
                            |
              +-------------v----------------+
  未来方向     |      模型定制                 |
              |  +- LoRA/QLoRA 微调          |
  <---------- |  +- 针对性数据训练            |
              |  +- A/B 测试验证              |
              +-------------+----------------+
                            |
              +-------------v----------------+
              |      反馈闭环                 |
              |  +- 生产环境部署新模型         |
              |  +- 监控误报率/漏报率变化      |
              |  +- 识别新的失败模式           |
              +-------------+----------------+
                            |
                            +----------> 回到数据采集层（持续迭代）
```

**数据飞轮关键指标**:

| 指标 | 目标 | 采集方式 |
|:-----|:----|:---------|
| 误报率 | < 15% | 人工修正标记 / Dashboard 反馈按钮 |
| 漏报率 | < 10% | 合入后发现的、AI 未捕获的问题 |
| 评分偏差 | ±10 分 | 人工 Reviewer 二次评分对比 |
| 反馈覆盖率 | > 30% | 主动请求用户打分/标记 |

### 12.4 其他扩展开发思路

**思路一：多维度融合审查**

```text
当前: 单一 LLM 调用 -> 一个审查结果
未来:
  +- 安全审查 (CodeQL/Semgrep)  -> 确定性问题
  +- 规范审查 (lint checker)    -> 风格问题
  +- 逻辑审查 (LLM)            -> 复杂逻辑问题
     v
  融合权重 -> 综合报告
```

**思路二：审查结果分级推送**

```python
if score >= 80:
    # 仅推送简要通知
    notifier.send("MR #xxx 审查通过，评分 85")
elif score >= 60:
    # 推送完整报告
    notifier.send(full_report)
else:
    # 推送完整报告 + @相关人员
    notifier.send(full_report, at_all=True)
    # 触发 CI 门禁检查
```

**思路三：增量学习 — 审查模式自动发现**

```text
每次人工修正 AI 审查结果时：
1. 记录 (diff_fragment, ai_judgment, human_correction, reason)
2. 聚类相似模式
3. 提取高频修正类型 -> 更新 Prompt 或微调数据
4. 统计误报率趋势 -> 自动调整触发阈值
```

**思路四：跨 Repo 的全局问题跟踪**

```text
问题蔓延检测:
  检查发现某个模式问题（如硬编码IP）->
  查询该模式是否在其他仓库也存在 ->
  自动创建全局 Issue 跟踪
```

---

## 🔗 交叉引用

- [**AI-Codereview-Gitlab 配置操作指导**](2026-07-10-ai-codereview-gitlab-setup.md) — 部署与配置指导（本文档的实践配套）
- [**CodeReview 整体方案**](../../02_rd/01_product/01_software/13-codereview-project/2026-07-09-codereview-system-overview.md) — 三阶段走读体系，本项目是阶段二核心实现
- [**CodeReview 质量评估体系**](2026-06-29-codereview-quality-assessment.md) — 代码质量 7 维评估模型
- [**GitLab WebHook 集成方案**](2026-06-29-gitlab-webhook-integration.md) — 通用 WebHook + LLM CR 集成
- [**AI CR 方案全景**](2026-06-29-ai-codereview-landscape.md) — 三大 AI CR 路径对比
- [**CodeReview 项目路标**](../../02_rd/01_product/01_software/13-codereview-project/2026-07-09-codereview-roadmap.md) — 路标规划与左移策略

---

## 📄 变更记录

| 日期 | 版本 | 变更说明 |
|:-----|:----:|:---------|
| 2026-07-10 | v2.0 | 增强补充：新增模块索引速查表(§1.6)、实体数据结构详解(§1.7)、员工姓名映射(§1.8)、Dashboard 前端(§1.9)、全仓库 Review 命令(§1.10)、Conf 配置设计(§1.11, prompt_templates.yml)。补充 `employee_mapping.py`、`ui.py`、`cmd/review.py` 三块空缺，完善 `entity/review_entity.py` 数据模型字段说明与设计要点。 |
| 2026-07-10 | v1.0 | 初始创建。基于 v1.5.1 源码完成完整代码解析：12 章覆盖全链路数据流、API 路由、事件分发、队列任务、数据解析、审查引擎、飞书通知、LLM 适配、数据库、Agentic 模式、后续规划 |

---

> **总行数**: ~1,695 行 | **源码分析范围**: 项目 README + `api.py` + `ui.py` + `biz/api/*` + `biz/queue/worker.py` + `biz/platforms/gitlab/webhook_handler.py` + `biz/utils/code_reviewer.py` + `biz/event/event_manager.py` + `biz/utils/im/*` + `biz/entity/review_entity.py` + `biz/service/review_service.py` + `biz/llm/*` + `biz/agent/*` + `biz/cmd/review.py` + `biz/employee_mapping.py` + `conf/prompt_templates.yml` + `conf/supervisord.conf` + `Dockerfile`

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- [**AI-Codereview-Gitlab 配置操作指导**](2026-07-10-ai-codereview-gitlab-setup.md) — 关联
- [**CodeReview 整体方案**](../../02_rd/01_product/01_software/13-codereview-project/2026-07-09-codereview-system-overview.md) — 关联
- [**CodeReview 质量评估体系**](2026-06-29-codereview-quality-assessment.md) — 关联
- [**GitLab WebHook 集成方案**](2026-06-29-gitlab-webhook-integration.md) — 关联
- [**AI CR 方案全景**](2026-06-29-ai-codereview-landscape.md) — 关联
- [**CodeReview 项目路标**](../../02_rd/01_product/01_software/13-codereview-project/2026-07-09-codereview-roadmap.md) — 关联

### 外部资料引用

- (无)

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
