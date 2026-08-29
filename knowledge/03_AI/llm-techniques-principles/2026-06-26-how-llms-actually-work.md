# How LLMs Actually Work（翻译）— 归档

> **概要**: LLM 工作原理翻译归档：从 Tokenization 到 Next Token Prediction 九主题
>
> **关键词**: LLM 原理 · Tokenization · Attention · Transformer · 自回归

---

## 📑 目录

- [文章结构（9 个主题）](#文章结构9-个主题)
  - [一张速记图](#一张速记图)
- [🤔 反思](#反思)
  - [1. 这篇文章的价值在哪](#1-这篇文章的价值在哪)
  - [2. 一个被低估的洞察](#2-一个被低估的洞察)
  - [3. Induction Heads 在今天的知识集会中有了新意义](#3-induction-heads-在今天的知识集会中有了新意义)
  - [4. 知识库交叉引用](#4-知识库交叉引用)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

---

## 文章结构（9 个主题）

| 主题 | 核心要点 |
|:-----|:---------|
| **1. Tokenization** | 文字→整数 ID，子词（subword）是平衡整词和字符的最优粒度。"strawberry 有几个 r"经典坑 |
| **2. Embeddings** | 查找表，语义相近的 token 向量距离近。king − man + woman ≈ queen |
| **3. Positional Encoding** | RoPE 取代 sin/cos，旋转 Q/K 而非加性编码。Lost in the Middle 现象 |
| **4. Attention** | Q/K/V 三元组→点积→softmax→加权和。Causal Masking、Induction Heads（Anthropic 2022）、O(n²) 代价 |
| **5. Multi-Head Attention** | 每个头有自己完整的投影矩阵，不是切分 token 向量。一个重要纠正 |
| **6. FFN（MLP）** | 逐 token 独立，占参数量 60-70%，是模型存知识的主要地方。SwiGLU 门控变体 |
| **7. Residual + LayerNorm** | 残差连接 = 梯度高速路 + 残差流概念。Pre-LN vs Post-LN，RMSNorm |
| **8. Next Token Prediction** | LM Head → logits → softmax → 采样。6 种采样策略对比。自回归循环 + KV Cache |
| **9. 架构 vs 训练权重** | 差异在数据、规模、后训练（SFT/RLHF/DPO）、工程细节，不在架构 |

### 一张速记图

```text
文字 prompt -> Tokenizer -> 整数ID -> Embedding -> RoPE -> [LayerNorm -> MHA -> + (残差)] ->
[LayerNorm -> FFN -> + (残差)] × N层 -> LayerNorm -> LM Head -> logits -> softmax+采样 -> 下一个token
```

---

## 🤔 反思

### 1. 这篇文章的价值在哪

这是一篇"**从第一性原理出发的 LLM 科普**"——不依赖数学公式，用文字直觉解释每个组件为什么存在、解决什么根本矛盾。适合：

- **给 PM/产品同学快速补齐**，不用啃论文
- **给刚入门的工程师**，建立完整的心智模型后再深入具体框架
- **面试复习**，把分散的概念（RoPE、GQA、Pre-LN）串到一条流水线上

### 2. 一个被低估的洞察

> 第 5 章纠正了一个常见误解——多头的 Q/K/V 是从完整 hidden 投影出来的，不是切分。

这个区别很微妙但重要：如果是"切分"，每个头看到的只是原始 token 局部信息；如果是"投影"，每个头看到的是**全局但经过不同线性变换**的信息。前者意味着信息损失，后者意味着视角多样性。

### 3. Induction Heads 在今天的知识集会中有了新意义

Anthropic 2022 发现的 Induction Heads（A B ... A → B 模式）被解释为 in-context learning 的底层机制。而今天归档的 **GEPA 文章**和 **Workflow Runtime 文章**都试图做同一件事——**把隐性的、模型/提示词层面的行为，变成显性的、工程上可控的机制**。

| 层面 | 隐性（模型内部） | 显性（工程化） |
|:-----|:-----------------|:--------------|
| ICL 机制 | Induction Heads | Workflow Runtime 中的 Workflow 编排 |
| Prompt 优化 | 黑盒调提示词 | GEPA 的轨迹反馈 + Pareto 筛选 |
| Agent 行为 | 模型临场决策 | Dynamic Workflow 脚本接管控制流 |

这其实是同一场运动的不同侧脸：**AI 工程化的本质是从"相信模型的隐式能力"转向"用工程手段显式矫正和约束"**。

### 4. 知识库交叉引用

这篇与以下已有知识高度相关：

- **KV Cache 技术全景调研** → 本文第 8 节简述 KV Cache 原理，全景调研有完整展开
- **MoE 架构对硬件影响** → 本文第 9 节提到 MoE 作为稀疏 vs 稠密的区别
- **PD 分离 LLM 推理部署** → 本文第 8 节的自回归生成流程是 PD 分离的动机来源
- **RAG 研究路径与平台分析** → 本文第 4 节 Induction Heads 解释 ICL，是 RAG 的理论基础之一

**谁需要回看这篇**：当遇到 LLM 行为表现异常（比如长上下文中间信息丢失、采样结果不理想、理解不了为啥 strawberry 数不对）时，回到这篇找第一性原因。

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- (无)

### 外部资料引用

- (无)

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
