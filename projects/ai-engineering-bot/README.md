# 🤖 服务器研发 AI 工程化平台 — 飞书机器人脚手架

> **基于 [AI 工程化平台总体方案](../../knowledge/02_rd/08_ai-engineering/01-ai-engineering-platform-overview.md) 构建**
> 状态: **Phase 1 启动准备** · 版本: v0.1.0

## 📋 项目结构

```
src/
├── main.py                  # FastAPI 入口 / 事件订阅 Webhook
├── config.py                # 配置管理（环境变量）
├── bot/                     # 飞书机器人
│   ├── router.py            # 指令路由（/ai ask /ai research...）
│   ├── handler.py           # 消息处理器（意图解析 + 分发）
│   ├── card_builder.py      # 消息卡片 JSON 构建器
│   └── callback.py          # 卡片交互回调处理
├── agent/                   # Agent 编排引擎
│   ├── orchestrator.py      # 任务分解 → Agent 分配 → 结果汇聚
│   ├── roles.py             # 6 个 Agent 角色定义
│   └── context.py           # 会话/项目上下文管理
├── workflow/                # 工作流引擎
│   ├── engine.py            # DAG 执行器（状态/超时/重试/断点续传）
│   ├── pipeline.py          # 6 阶段流水线模板注册
│   └── nodes.py             # 节点类型（input-qa/multi-path/convergence/...）
├── knowledge/               # 知识库集成
│   ├── retriever.py         # 语义检索 + RAG
│   └── archiver.py          # 自动归档触发
└── utils/                   # 通用工具
    ├── feishu_client.py     # 飞书 API 客户端封装
    ├── llm_client.py        # LLM 多模型网关
    ├── task_store.py        # 任务状态存储（Redis/内存）
    └── logger.py            # 结构化日志
```

## 🚀 快速启动

```bash
# 1. 复制环境变量
cp .env.example .env
# 编辑 .env 填入飞书应用凭证

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
python src/main.py

# 4. 配置飞书事件订阅 URL
# https://open.feishu.cn/app/{APP_ID}/event
# 回调地址: https://your-domain.com/webhook/feishu
```

## 📐 架构概览

```
飞书群消息
    │
    ▼
┌──────────────────────┐
│  Webhook / Event API  │  ← FastAPI POST /webhook/feishu
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  消息路由器 (router)  │  → 解析指令 /ai xxx 或 @机器人
│  ┌────────────────┐   │
│  │ 指令匹配        │   │  /ai research → 调研流水线
│  │ intent parser  │   │  /ai review   → 代码审查
│  └───────┬────────┘   │  /ai ask      → RAG 问答
└──────────┼───────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
┌─────────┐ ┌─────────┐
│ Agent    │ │ Workflow│
│ 编排引擎  │ │ DAG引擎  │
└────┬────┘ └────┬────┘
     │           │
     └─────┬─────┘
           ▼
┌──────────────────────┐
│  结果组装 + 卡片发送  │  → 飞书消息卡片
└──────────────────────┘
```

## 🔧 核心能力

| 功能 | 文件 | 状态 |
|:-----|:-----|:----:|
| 飞书消息接收/回复 | `bot/router.py` | ✅ 就绪 |
| 指令解析 (`/ai ask/review/research...`) | `bot/router.py` | ✅ 就绪 |
| 消息卡片构建 (调研/进度/方案/诊断) | `bot/card_builder.py` | ✅ 就绪 |
| 卡片回调处理 | `bot/callback.py` | ✅ 就绪 |
| Agent 编排 (任务分解→角色分配) | `agent/orchestrator.py` | ✅ 就绪 |
| 6 角色定义 | `agent/roles.py` | ✅ 就绪 |
| 工作流 DAG 引擎 | `workflow/engine.py` | ✅ 就绪 |
| 6 阶段流水线模板 | `workflow/pipeline.py` | ✅ 就绪 |
| 节点类型定义 | `workflow/nodes.py` | ✅ 就绪 |
| 知识库 RAG 检索 | `knowledge/retriever.py` | ✅ 就绪 |
| 飞书 API 客户端 | `utils/feishu_client.py` | ✅ 就绪 |
| LLM 多模型网关 | `utils/llm_client.py` | ✅ 就绪 |
| 任务状态管理 | `utils/task_store.py` | ✅ 就绪 |
| 事件订阅 Webhook | `src/main.py` | ✅ 就绪 |
