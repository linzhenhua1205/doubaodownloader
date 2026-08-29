# FreeLLMAPI — 自托管 AI API 免费额度聚合网关

> **概要**: 自托管AI API网关，聚合14家厂商免费额度并暴露OpenAI兼容接口，含动态路由与限流机制
>
> **关键词**: FreeLLMAPI · API网关 · 免费额度 · OpenAI兼容 · 动态路由

---

## 📑 目录

- [一、概述](#一概述)
- [二、架构与部署](#二架构与部署)
  - [2.1 环境要求](#21-环境要求)
  - [2.2 快速部署](#22-快速部署)
  - [2.3 配置流程](#23-配置流程)
  - [2.4 接入验证](#24-接入验证)
- [三、核心路由机制 ⭐](#三核心路由机制)
  - [3.1 动态惩罚路由](#31-动态惩罚路由)
  - [3.2 滑动窗口限流](#32-滑动窗口限流)
  - [3.3 冷却升级策略](#33-冷却升级策略)
  - [3.4 Sticky Session（粘性会话）](#34-sticky-session粘性会话)
  - [3.5 Fallback 与重试](#35-fallback-与重试)
- [四、安全机制](#四安全机制)
- [五、场景价值](#五场景价值)
- [相关链接](#相关链接)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

---

## 一、概述

FreeLLMAPI 是一个**自托管的 API 网关**，把 **Google Gemini、Groq、Mistral、Cerebras、SambaNova、OpenRouter、GitHub Models、Cloudflare Workers AI、Cohere、Z.ai（智谱）、HuggingFace、NVIDIA NIM** 等 14 家 AI 厂商的**免费额度聚合到一个端点**，对外暴露标准的 **OpenAI 兼容接口**。

**核心价值**：注册各家免费 API Key（多数不需要绑卡），每日可用 Token 可达数亿级别，大幅降低个人开发者的 API 调用成本。

---

## 二、架构与部署

### 2.1 环境要求

- **Node.js** 20+
- **Git**
- 各家平台的免费 API Key（推荐先注册 Groq、Mistral、OpenRouter 三家，基本满足日常使用）

### 2.2 快速部署

```bash
git clone https://github.com/tashfeenahmed/freellmapi.git
cd freellmapi
npm install
cp .env.example .env
echo "ENCRYPTION_KEY=$(node -e "console.log(require('crypto').randomBytes(32).toString('hex'))")" >> .env
npm run dev
```

启动后：

- **前端 Dashboard**: `http://localhost:5173` — 管理 Provider 和 API Key
- **后端 API**: `http://localhost:3001` — OpenAI 兼容接口

**生产部署**: `npm run build && node server/dist/index.js`，前后端统一跑在 3001 端口。

### 2.3 配置流程

1. 在 Dashboard 左侧 **Provider 管理** 页面，逐个添加 Provider 并粘贴 API Key
2. FreeLLMAPI 自动检测 Key 健康状态（绿色可用 / 红色无效或已达限额）
3. 自动将每个平台的模型注册到**路由表**，无需手动指定模型
4. 在 Dashboard **API Key** 页面获取统一 Key（格式 `freellmapi-xxxx`）

### 2.4 接入验证

```bash
curl http://localhost:3001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer freellmapi-你的Key" \
  -d '{"model": "auto", "messages": [{"role": "user", "content": "用一句话介绍你自己"}]}'
```

- `model` 字段写 `auto`，让路由器自动选择最优可用模型
- 响应头 `x-routed-via` 字段标明实际由哪个 Provider 处理

---

## 三、核心路由机制 ⭐

路由器是整个项目最有技术价值的部分，设计精细度远超简单轮询。

### 3.1 动态惩罚路由

- 每个模型有**基础优先级**，但实际排序用 **"基础优先级 + 惩罚分"**
- **惩罚分机制**：
  - 模型返回 **429（限流）** → 惩罚分 **+3**，上限 **10**
  - 每 **2 分钟** 自动衰减 **1**
  - 每次成功请求也衰减 **1**
- 被限流的模型自动在优先级队列中下沉，冷却期后自动恢复原位
- **自适应**：无需手动调整 Provider 顺序

### 3.2 滑动窗口限流

- 使用 **滑动窗口算法**（非固定窗口），每一秒都在滑动
- **内存 + SQLite 双写**：
  - **内存**：微秒级查询响应
  - **SQLite**：进程重启后计数不丢失
- **四个检查维度**：RPM（每分钟请求数）、RPD（每天请求数）、TPM（每分钟 Token）、TPD（每天 Token）
- 任一维度触达限额 → 该 Provider 被跳过

### 3.3 冷却升级策略

同一模型在 **24 小时内** 按触发 429 次数升级冷却时间：

| 触发次数 | 冷却时间 |
|:---------|:---------|
| 第 1 次 | 2 分钟 |
| 第 2 次 | 10 分钟 |
| 第 3 次 | 1 小时 |
| ≥ 4 次 | 24 小时 |

**设计思路**：反复被限流说明免费额度可能见底，直接冷却一整天等额度刷新。

### 3.4 Sticky Session（粘性会话）

- 用第一条用户消息的 **SHA1 哈希** 作为 Session Key
- 首次路由成功后，Session Key → 模型 ID 的映射存入内存，**30 分钟有效**
- 后续同一对话优先复用上次模型（**"优先"非"强制"**，上次模型被限流时自动 Fallback）
- 仅对**多轮对话**生效（消息列表含 `assistant` 角色历史消息）

### 3.5 Fallback 与重试

- 整条请求链路最多重试 **20 次**
- 每次重试将上一次失败的 **模型 + Key 组合** 加入跳过集合
- **触发重试**：429 限流、超时、连接拒绝、503/500 服务端错误
- **不触发重试**：401 认证失败（换模型也无效）
- 20 次全部失败 → 返回 429，附带最后一次失败原因

---

## 四、安全机制

- **AES-256-GCM** 加密存储所有 API Key
- Key 存储在启动时生成的加密密钥加密后入库

---

## 五、场景价值

| 角色 | 价值 |
|:-----|:------|
| **个人开发者** | 免费额度聚合，降低 API 调用成本（替代 Claude Code + Codex 每月 400+ 刀） |
| **Agent 工具开发者** | 提供统一的 OpenAI 兼容协议，一次适配即可接入 14 家模型 |
| **开源项目** | 可集成到 Claude Code/Cursor/PaiCLI 等工具中 |

**典型集成案例**：开源项目 [PaiCLI](https://github.com/)（类 Claude Code 的 Java Agent CLI 工具），通过模板方法模式抽象 LLM Provider，新增 Provider 仅需约 30 行代码，已集成 FreeLLMAPI 网关。

---

## 相关链接

- [掘金原文](https://aicoding.juejin.cn/post/7645208859774500899)
- [GitHub 仓库](https://github.com/tashfeenahmed/freellmapi)
- 更多 AI 编程工具动态 → [掘金 AI 编程新闻总览](../../07_industry-research/03_server/03_conference/2026-06-26-aicoding-juejin-news-2026-05.md)

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- [掘金 AI 编程新闻总览](../../07_industry-research/03_server/03_conference/2026-06-26-aicoding-juejin-news-2026-05.md) — 关联

### 外部资料引用

- 来源: [掘金 AI 编程](https://aicoding.juejin.cn/post/7645208859774500899)
- 来源: 沉默王二
- 来源: 2026-05-30

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
