# 大模型工具与框架

> **概要**: `discover/newwiki/大模型技术与原理.md` 工具框架章节
>
> **关键词**: (待补充)

---

## 📑 目录

- [Agent框架](#agent框架)
  - [OpenClaw](#openclaw)
  - [CowAgent](#cowagent)
  - [Hermes Agent](#hermes-agent)
- [RAG平台对比](#rag平台对比)
  - [Dify](#dify)
  - [RAGFlow](#ragflow)
  - [n8n](#n8n)
- [推理框架](#推理框架)
  - [vLLM](#vllm)
  - [NVIDIA NIM](#nvidia-nim)
  - [LocalAI](#localai)
- [开发工具链](#开发工具链)
  - [AI编程助手](#ai编程助手)
  - [向量数据库](#向量数据库)
- [部署工具](#部署工具)
  - [Ollama](#ollama)
  - [Docker部署](#docker部署)
- [模型量化工具](#模型量化工具)
  - [llama.cpp](#llamacpp)
  - [量化精度对比](#量化精度对比)
- [LMOps工具链](#lmops工具链)
  - [核心组件](#核心组件)
- [相关页面](#相关页面)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## Agent框架

### OpenClaw

**核心定位**：企业级AI Agent执行框架

**关键特性**：

- **Skills系统**：可复用任务模板，支持自迭代
- **多Agent协作**：支持并行异步运行、自动化任务委派
- **记忆系统**：三层记忆（SQLite + 全文检索 + 大模型摘要）
- **安全机制**：用户授权、危险命令审批、容器隔离

**版本演进**：

- 从直接调用LLM → 调用Agent框架 → Skills维护 → 工程自演进

### CowAgent

**定位**：人机协作自动化框架

**核心组件**：

- **规划器（Planner）**：任务拆解与自主规划
- **执行器（Executor）**：工具调用与结果执行
- **记忆器（Memory）**：偏好记忆、上下文记忆

### Hermes Agent

**差异化定位**：Agent自进化设计

**核心创新**：

- 任务完成后自动生成Markdown格式Skill
- 发现更好路径时自动更新文档
- 支持Claude额度调用

## RAG平台对比

### Dify

**定位**：AI应用开发全栈平台

**核心能力**：

- 可视化工作流编排
- 支持多模型接入
- 企业级部署

**适用场景**：技术团队快速落地复杂AI项目

### RAGFlow

**定位**：文档驱动的RAG引擎

**核心能力**：

- 非结构化数据知识提取
- 深度文档理解
- Graph工作流

**适用场景**：文档密集型企业知识管理

### n8n

**定位**：跨系统集成枢纽

**核心能力**：

- 节点式流程编排
- AI与传统工具协同
- 自动化工作流

**适用场景**：跨系统业务流程自动化

## 推理框架

### vLLM

**核心特性**：

- **PagedAttention**：显存效率优化，减少55%内存使用
- **动态批处理**：提升吞吐量
- **开源社区活跃**

### NVIDIA NIM

**核心服务**：

- 预封装推理微服务
- 容器化部署
- TensorRT加速集成

### LocalAI

**端侧部署方案**：

- 支持多种模型格式
- 低资源消耗
- 隐私保护

## 开发工具链

### AI编程助手

| 工具 | 特点 | 适用场景 |
|:-----|:-----|:---------|
| Claude Code | 复杂架构推理 | 大型项目开发 |
| Cursor | IDE图形化 | 日常编程 |
| DeepSeek-TUI | 终端重度用户 | 极致省钱 |
| GitHub Copilot | 生态集成 | 通用编程 |

### 向量数据库

| 数据库 | 特点 | 适用场景 |
|:-------|:-----|:---------|
| Chroma | 内嵌式、零部署 | 轻量级本地 |
| Qdrant | 高性能、分布式 | 企业级 |
| Milvus | 成熟稳定 | 大规模数据 |
| Weaviate | 原生GraphQL | 复杂查询 |

## 部署工具

### Ollama

**核心功能**：

- 一键管理本地LLM
- 支持Qwen、LLaMA、GLM等主流模型
- 跨平台（Windows/macOS/Linux）

### Docker部署

```bash
# 基本用法
docker run ghcr.io/ggerganov/llama.cpp:full-musa -m llama3.2:1B -p "你好"

# 参数说明
-m: 模型文件
-p: 提示词
```

## 模型量化工具

### llama.cpp

**支持量化范围**：2-bit至8-bit（Q4_K_M、Q8_0等）

**效果**：

- 70B模型从13.2GB降至4.8GB
- 推理速度提升3倍

### 量化精度对比

| 精度 | 体积压缩 | 精度损失 |
|:-----|:---------|:---------|
| FP16 | 1x | 无 |
| INT8 | ~2x | 极小 |
| INT4 | ~4x | 可接受 |
| INT2 | ~8x | 较大 |

## LMOps工具链

### 核心组件

- **训练框架**：PyTorch、TensorFlow
- **推理优化**：TensorRT、ONNX Runtime
- **模型管理**：MLflow、Hugging Face
- **监控运维**：Prometheus、Grafana

## 相关页面

- [技术实现](2026-06-28-llm-techniques-overview.md) — 架构细节
- [应用场景](2026-06-28-llm-application-scenarios.md) — 行业应用
- [性能优化](2026-06-28-llm-optimization-methods.md) — 优化方法

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- [技术实现](2026-06-28-llm-techniques-overview.md) — 关联
- [应用场景](2026-06-28-llm-application-scenarios.md) — 关联
- [性能优化](2026-06-28-llm-optimization-methods.md) — 关联

### 外部资料引用

- 来源: `discover/newwiki/大模型技术与原理.md` 工具框架章节

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
