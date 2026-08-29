# 知识库本地部署方案

> **概要**: AI知识库本地部署方案，含AnythingLLM、Dify、Open-WebUI三种方案
>
> **关键词**: 知识库部署 · AnythingLLM · Ollama · Dify · Open-WebUI

---

## 📑 目录

- [一、方案概览](#一方案概览)
- [二、方案 A：AnythingLLM + Ollama（推荐入门）](#二方案-aanythingllm-ollama推荐入门)
  - [架构](#架构)
  - [部署步骤](#部署步骤)
- [三、方案 B：Docker Dify 部署](#三方案-bdocker-dify-部署)
  - [快速部署](#快速部署)
  - [关键配置](#关键配置)
  - [部署后的能力](#部署后的能力)
- [四、方案 C：Open-WebUI + Ollama](#四方案-copen-webui-ollama)
- [五、硬件配置参考](#五硬件配置参考)
- [六、网页结构构建知识库](#六网页结构构建知识库)
  - [流程](#流程)
  - [关键工具](#关键工具)
- [七、常用配置速查](#七常用配置速查)
  - [Dify 知识库配置建议](#dify-知识库配置建议)
  - [Ollama 常用命令](#ollama-常用命令)
  - [AnythingLLM 快捷键](#anythingllm-快捷键)
- [八、参考资料](#八参考资料)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

---

## 一、方案概览

| 方案 | 适用场景 | 硬件要求 | 部署时长 | AI 能力 |
|:-----|:---------|:---------|:---------|:---------|
| 🅰 AnythingLLM + Ollama | 个人/小团队快速搭建 | 8GB 内存 | 30 分钟 | 文档问答/总结 |
| 🅱 Docker Dify 部署 | 团队/企业 AI 平台 | 16GB 内存 | 2 小时 | 完整 RAG + Workflow |
| 🅲 RAGFlow / MaxKB 部署 | 企业级知识库 | 16GB+ 内存 | 2-4 小时 | 深度文档理解 |
| 🅳 Open-WebUI + Ollama | 极简个人部署 | 8GB 内存 | 15 分钟 | 基本问答 |

---

## 二、方案 A：AnythingLLM + Ollama（推荐入门）

> 最简零代码方案，不用写一行代码

### 架构

```text
本地文档(PDF/MD/TXT) -> AnythingLLM(桌面端) -> Ollama(本地模型) -> AI 问答
```

### 部署步骤

**1. 安装 Ollama**

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# 拉取模型（按硬件选）
ollama pull qwen:7b    # 16GB 内存推荐
ollama pull qwen:4b    # 8GB 内存推荐
```

**2. 安装 AnythingLLM**

下载桌面客户端：<https://anythingllm.com/>

**3. 配置模型**

- 启动 AnythingLLM → 设置 → LLM 偏好 → Ollama
- 地址：`http://127.0.0.1:11434`
- 选择模型：`qwen:7b`

**4. 创建知识库**

- 新建工作区 → 选择知识库模式
- 拖拽本地文档自动解析/分块/向量化
- 直接提问对话

---

## 三、方案 B：Docker Dify 部署

> 完整 RAG 知识库 + Workflow 编排 + API 接口

### 快速部署

```bash
# 克隆 Dify
git clone https://github.com/langgenius/dify.git
cd dify/docker

# 复制环境配置
cp .env.example .env

# 启动所有服务
docker compose up -d

# 访问 http://localhost:3000
```

### 关键配置

**.env 核心参数**：

```bash
# 向量数据库（推荐 Qdrant）
VECTOR_STORE=qdrant

# 模型供应商（至少配置一个）
OPENAI_API_KEY=sk-xxx
# 或本地模型
OLLAMA_BASE_URL=http://host.docker.internal:11434

# 知识库配置
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K=3
SCORE_THRESHOLD=0.65
```

### 部署后的能力

| 功能 | 访问方式 |
|:-----|:---------|
| Web 管理界面 | <http://localhost:3000> |
| REST API | <http://localhost:5001> |
| 知识库管理 | 上传文件 → 自动分段 → 向量化 |
| 应用发布 | 聊天助手 / 文本生成 / Agent |

---

## 四、方案 C：Open-WebUI + Ollama

> 极简方案，适合个人知识管理

```bash
# 启动 Open-WebUI（带知识库支持）
docker run -d -p 3000:8080 \
  -v open-webui:/app/backend/data \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

**特点**：

- Ollama 模型直接集成
- 内置 RAG 知识库功能
- 文件上传自动解析
- Web 界面，多人可用

---

## 五、硬件配置参考

| 配置等级 | CPU | 内存 | GPU | 推荐模型 | 适用场景 |
|:---------|:----|:-----|:---|:---------|:---------|
| 入门 | 4 核 | 8GB | 无 | Qwen2:4b / Llama3:8b | 个人知识库 |
| 标准 | 8 核 | 16GB | 可选 | Qwen2:7b / DeepSeek | 小团队知识库 |
| 企业 | 16 核 | 32GB+ | NVIDIA T4+ | Qwen2:72b / LLaMA3:70b | 企业级部署 |

---

## 六、网页结构构建知识库

> 参考 `import/md/网页结构知识库搭建全流程_*.md`

### 流程

```text
目标网页 -> 爬虫采集 -> HTML 解析 -> 内容清洗 -> Markdown 转换 -> 入库
```

### 关键工具

| 步骤 | 推荐工具 | 说明 |
|:-----|:---------|:------|
| 网页采集 | Scrapy / Playwright | 动态页面用 Playwright |
| 内容提取 | Readability / Trafilatura | 提取正文，去除广告/导航 |
| Markdown 转换 | html2text / Markdownify | 保留结构 |
| 入库 | Dify API / AnythingLLM | 自动处理 |

---

## 七、常用配置速查

### Dify 知识库配置建议

| 配置项 | 推荐值 | 说明 |
|:-------|:-------|:------|
| 分块大小 | 500-1000 字符 | 技术文档取上限 |
| 分块重叠 | 10%-20% | 防止上下文断裂 |
| Top-K | 3-5 | 平衡质量与消耗 |
| 相似度阈值 | 0.65-0.75 | 低于此值视为"未命中" |
| 嵌入模型 | text-embedding-ada-002 / bge-large | 中文场景推荐 bge |

### Ollama 常用命令

```bash
# 模型管理
ollama pull qwen:7b          # 拉取模型
ollama list                  # 查看已拉取模型
ollama rm qwen:4b            # 删除模型

# 运行推理
ollama run qwen:7b           # 交互模式
ollama run qwen:7b "提示词"  # 单次推理

# 服务管理
ollama serve                 # 启动服务
# 服务地址: http://localhost:11434
```

### AnythingLLM 快捷键

| 操作 | 说明 |
|:-----|:------|
| Cmd+K | 搜索知识库 |
| Cmd+N | 新建对话 |
| @ 文件名 | 指定文档提问 |
| / | 切换命令模式 |

---

## 八、参考资料

- `import/md/本地知识库AI部署方案_0614030606.md` — 1616 行完整部署指南
- `import/md/本地知识库AI部署方案_0623101712.md`
- `import/md/网页结构知识库搭建全流程_0614024515.md`
- `import/md/本地材料梳理与知识库构建_*.md`
- [工具对比与选型](05_tools/ai-tools/2026-06-29-kb-tools-comparison.md)
- [AI 知识库基础概念](03_AI/knowledge-system/2026-06-29-kb-overview.md)

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- [工具对比与选型](05_tools/ai-tools/2026-06-29-kb-tools-comparison.md) — 关联
- [AI 知识库基础概念](03_AI/knowledge-system/2026-06-29-kb-overview.md) — 关联

### 外部资料引用

- 来源: import/md/本地知识库AI部署方案_0614030606.md`（1616行）、`import/md/网页结构知识库搭建全流程_*.md`、`import/md/本地材料梳理与知识库构建_*.md`、`import/doubao/本地知识库优化实施方案.md

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
