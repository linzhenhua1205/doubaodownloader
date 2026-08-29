# 大模型基础概念

> **概要**: LLM 技术栈的基础概念层，从第一性原理出发建立核心认知框架
>
> **关键词**: (待补充)

---

## 📑 目录

- [0. 语言建模的本质](#0-语言建模的本质)
  - [根本约束](#根本约束)
- [1. Transformer 架构核心](#1-transformer-架构核心)
  - [1.1 为什么是 Transformer 而非 RNN？](#11-为什么是-transformer-而非-rnn)
  - [1.2 Self-Attention 机制](#12-self-attention-机制)
  - [1.3 位置编码（Positional Encoding）](#13-位置编码positional-encoding)
  - [1.4 前馈网络（FFN）](#14-前馈网络ffn)
- [2. Scaling Law：为什么"大"才有效](#2-scaling-law为什么大才有效)
  - [2.1 核心发现（第一性原理）](#21-核心发现第一性原理)
  - [2.2 Chinchilla 修正：最优分配比](#22-chinchilla-修正最优分配比)
  - [2.3 后训练 Scaling：推理时计算](#23-后训练-scaling推理时计算)
- [3. 稀疏激活：MoE 混合专家模型](#3-稀疏激活moe-混合专家模型)
  - [3.1 为什么要稀疏？（第一性原理）](#31-为什么要稀疏第一性原理)
  - [3.2 路由机制](#32-路由机制)
  - [3.3 关键创新：分组限制门控](#33-关键创新分组限制门控)
  - [3.4 代表性 MoE 模型](#34-代表性-moe-模型)
- [4. 长上下文：从 2K 到 1M+](#4-长上下文从-2k-到-1m)
  - [4.1 核心困难（第一性原理）](#41-核心困难第一性原理)
  - [4.2 关键技术路线](#42-关键技术路线)
  - [4.3 上下文窗口演进](#43-上下文窗口演进)
- [5. 多模态扩展：异构数据统一](#5-多模态扩展异构数据统一)
  - [5.1 核心挑战（第一性原理）](#51-核心挑战第一性原理)
  - [5.2 桥接架构路线](#52-桥接架构路线)
  - [5.3 原生多模态的突破](#53-原生多模态的突破)
- [6. 范式扩展：从模型到 Agent](#6-范式扩展从模型到-agent)
  - [6.1 核心突破](#61-核心突破)
  - [6.2 Agent 系统组成](#62-agent-系统组成)
  - [6.3 当前进展](#63-当前进展)
- [知识脉络总结](#知识脉络总结)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 0. 语言建模的本质

LLM 的核心任务是**语言建模**——对序列 $x = (x_1, ..., x_n)$ 的概率分布建模。

**链式法则分解**：

$$P(x_1, ..., x_n) = \prod_{t=1}^n P(x_t | x_1, ..., x_{t-1})$$

这个公式定义了一切：**每个 token 的预测仅依赖前文**。所有架构创新（自注意力、位置编码、KV Cache）和服务优化（PD 分离、推测解码）都服务于同一个目标——高效计算这个条件概率。

### 根本约束

| 维度 | 约束 | 根源 |
|:-----|:-----|:-----|
| **计算** | 串行依赖（逐 token 生成） | 条件概率定义 |
| **内存** | 前文信息必须全量保留 | 注意力机制需要完整 Key/Value |
| **容量** | 模型需存储事实知识与推理模式 | 参数化逼近 $P(x_t\|\text{context})$ |

> 参考：Bengio et al. (2003) *A Neural Probabilistic Language Model* — 神经语言模型奠基论文

---

## 1. Transformer 架构核心

### 1.1 为什么是 Transformer 而非 RNN？

**根本瓶颈（第一性原理）**：

- RNN/LSTM：串行处理 → 时间步 $t$ 必须等 $t-1$ 完成 → **不可并行**，序列长度 $n$ 时计算复杂度 $O(n)$ 但 **路径长度 $O(n)$** → 长程依赖捕获困难
- Transformer (Vaswani et al., 2017)：Self-Attention → **全序列并行** → 任意两个位置的路径长度 $O(1)$
- 代价：自注意力计算复杂度 $O(n^2 \cdot d)$，$n$ 增大时计算量平方增长

**核心权衡**：

$$路径长度_{RNN} = O(n) \quad vs \quad 路径长度_{Transformer} = O(1)$$
$$计算量_{RNN} = O(n \cdot d^2) \quad vs \quad 计算量_{Transformer} = O(n^2 \cdot d)$$

> 来源：Vaswani et al., *Attention Is All You Need*, NeurIPS 2017

### 1.2 Self-Attention 机制

**QKV 三件套**：将每个 token 映射为 Query、Key、Value 三个向量

$$Attention(Q, K, V) = \text{softmax}(\frac{QK^T}{\sqrt{d_k}}) V$$

- $QK^T$：计算序列中每对位置的**相关度分数**
- $\sqrt{d_k}$ 归一化：防止 softmax 进入梯度饱和区（维度大时点积方差大）
- softmax：将分数归一化为概率分布
- 输出：加权求和 Value → 每个 token 获得全部上下文的**注意力加权表示**

**Multi-Head Attention**：将 $d$ 维拆成 $h$ 个头 ($h \cdot d_k = d$)，每个头捕获不同子空间的关系，拼接后投影

> 来源：Vaswani et al., 2017, §3.2

### 1.3 位置编码（Positional Encoding）

**为什么需要**：Self-Attention 是**排列不变**的——交换输入顺序得到的注意力分数相同 → 必须注入位置信号

**主流方案演进**：

| 方案 | 代表模型 | 核心思路 | 关键优势 |
|:-----|:---------|:---------|:---------|
| 正弦/余弦编码 | Transformer 原始 | $PE_{(pos, 2i)} = \sin(pos/10000^{2i/d})$ | 固定无参、可外推 |
| 可学习编码 | BERT/GPT | 每个位置一个可学习向量 | 灵活、依赖训练数据 |
| **RoPE** (旋转编码) | LLaMA/DeepSeek/Qwen | 将位置信息编码到旋转矩阵中，作用在 Q/K 上 | 支持相对位置、外推性好 |
| ALiBi | BLOOM | 注意力分数减去位置距离的线性偏置 | 简单、可外推 |

**RoPE 成为主流的原因**（第一性原理）：

- 相对位置信息：两个 token 的注意力分数只依赖它们之间的距离，而非绝对位置 → 更符合语言直觉
- 外推能力：训练时未见过的长度，推理时也能泛化（当前已从 4K 扩展到 1M+）
- 数学优雅：$f_q(x_m, m) = R_m \cdot W_q x$ 用旋转矩阵编码位置，不影响注意力权重的平移不变性

> 来源：Su et al., *RoFormer: Enhanced Transformer with Rotary Position Embedding*, 2021

### 1.4 前馈网络（FFN）

$$FFN(x) = W_2 \cdot \sigma(W_1x + b_1) + b_2$$

- FFN 占模型总参数的 **~2/3**（LLaMA 系列数据）
- 激活函数演进：ReLU → GELU → SwiGLU
  - **SwiGLU** (LLaMA 2/3)：$SwiGLU(x) = Swish(W_1x) \odot W_2x$，增加了一个门控信号
- 功能定位：**存储事实知识**——Attention 负责"从哪找信息"，FFN 负责"这些信息是什么"
  - 参考：Geva et al., *Transformer Feed-Forward Layers Are Key-Value Memories*, EMNLP 2021

---

## 2. Scaling Law：为什么"大"才有效

### 2.1 核心发现（第一性原理）

**损失随规模幂律下降** —— Kaplan et al. (2020) 在 1K~1B 参数范围内训练了 1,600+ 个模型，发现：

$$L(N) \approx \left(\frac{N_c}{N}\right)^{\alpha_N} + L_\infty$$

- $N$: 模型参数量，$D$: 训练数据量，$C$: 计算量（FLOPs）
- 性能由 $N$、$D$、$C$ 三个变量的**瓶颈值**决定——三者在最优配置下都呈幂律关系
- **关键推论**：模型性能没有明显天花板，投入更多资源可以持续提升

> 来源：Kaplan et al., *Scaling Laws for Neural Language Models*, 2020, arXiv:2001.08361

### 2.2 Chinchilla 修正：最优分配比

Hoffmann et al. (2022) 发现 Kaplan 最优方案低估了数据的重要性：

- **最优配置**：参数 : token ≈ **1 : 20**（即 70B 模型需 1.4T token）
- 此前主流模型都欠训练（如 GPT-3 175B 只训了 300B token → 应为 3.5T）
- **影响**：LLaMA 系列（Touvron et al., 2023）采用"更小模型 + 更多数据"策略

| 模型 | 参数 | 训练 token | 参数:token 比 | 是否符合 Chinchilla |
|:-----|:----|:----------|:-------------|:-------------------|
| GPT-3 | 175B | 300B | 1:1.7 | ❌ 严重不足 |
| LLaMA | 65B | 1.4T | 1:22 | ✅ |
| LLaMA 2 | 70B | 2T | 1:29 | ✅ |
| DeepSeek-V3 | 671B (激活37B) | 14.8T | 1:22 (按激活) | ✅ |

> 来源：Hoffmann et al., *Training Compute-Optimal Large Language Models*, NeurIPS 2022 (Chinchilla)

### 2.3 后训练 Scaling：推理时计算

OpenAI o1/o3 (2024) 开创了新范式——**Scaling 不仅发生在训练阶段，也发生在推理阶段**：

- **训练 Scaling**：增加参数 + 数据 → 提升模型能力
- **推理 Scaling**：增加推理时计算量（思考链长度、搜索树深度）→ 提升问题解决能力
- 意义：模型能力的下限由训练决定，上限由推理时计算量决定

> 来源：OpenAI, *Learning to Reason with LLMs*, 2024; Snell et al., *Scaling LLM Test-Time Compute*, 2024

---

## 3. 稀疏激活：MoE 混合专家模型

### 3.1 为什么要稀疏？（第一性原理）

稠密模型的**根本矛盾**：所有参数必须存储在显存中，但推理时只能用到一小部分

$$Cost_{dense} = N \cdot 2P \quad(\text{推理成本与总参数量成正比})$$

**人类大脑的启发**：特定任务只激活部分神经元——稀疏激活是生物神经系统的共性

**MoE 核心思想**：总参数量巨大（存储全量知识）、每次推理仅激活一小部分（控制计算成本）

- 总参数：$\sum N_{expert}$（知识容量大）
- 激活参数：$K \cdot N_{single}$（推理代价低）
- 等效 FLOPs 接近 $K$ 倍稠密模型，吞吐接近同激活量的稠密模型

### 3.2 路由机制

Token → 门控网络 → Top-K 专家选择：

$$G(x) = \text{softmax}(W_g x), \quad TopK(G(x)) \rightarrow \text{选择 Top-K 个专家}$$

$$
y = \sum_{i \in TopK} G(x)_i \cdot E_i(x)
$$

**关键挑战**：

- **负载不均衡**：所有 token 可能涌向同一专家 → 需要 **Load Balancing Loss** (Shazeer et al., 2017)
- **通信瓶颈**：All-to-All 通信 → token 必须从路由节点发往专家所在的节点 → 跨节点通信成为瓶颈
- **知识碎片化**：专家太多、太小 → 单个专家学不到完整知识 -> 需要细粒度专家设计

> 来源：Shazeer et al., *Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer*, ICLR 2017

### 3.3 关键创新：分组限制门控

DeepSeek-V3 (2024) 解决了跨节点通信瓶颈：

- **问题**：传统 MoE All-to-All 通信——每个 token 的请求需发给各节点的所有专家 → 通信量 $O(N_{node} \cdot N_{token})$
- **方案**：每个 token 限定在**一个专家组**内选择专家，组内全连接、组间隔离
- **效果**：通信从全局 All-to-All 降为局部 All-to-All → 流量减少、局部性提升、RDMA 效率更高

> 来源：DeepSeek-AI, *DeepSeek-V3 Technical Report*, 2024, arXiv:2412.19437

### 3.4 代表性 MoE 模型

| 模型 | 发布时间 | 总参数 | 激活参数 | 专家数 | Top-K | 关键创新 |
|:-----|:-------|:------|:--------|:-----|:-----|:---------|
| Mixtral 8×7B | 2023.12 | 47B | 13B | 8 | 2 | 开源 MoE 首个实用案例 |
| DeepSeek-V2 | 2024.05 | 236B | 21B | 细粒度 160+ | - | 细粒度专家分割 + MLA |
| DeepSeek-V3 | 2024.12 | 671B | 37B | 256 (路由) | 8 | 分组限制门控 + FP8 训练 |
| MiniMax-M1 | 2025.01 | - | - | 256 (路由) | - | Lightning Attention |
| Qwen3-235B-A22B | 2025 | 235B | 22B | - | - | MoE + 长上下文 |

---

## 4. 长上下文：从 2K 到 1M+

### 4.1 核心困难（第一性原理）

**两个 O(n) 障碍**：

$$计算复杂度 = O(n^2 \cdot d) \quad\quad 内存占用 = O(n \cdot d_{kv})$$

- 标准 Self-Attention：$n \times n$ 注意力矩阵 → n=100K 时就是 10B 个元素
- KV Cache：每个 token 需存 Key 和 Value → n=1M 时，$d_{kv}$=4096 约需 16GB（FP16）

### 4.2 关键技术路线

| 技术 | 解决问题 | 代表方案 | 效果 |
|:-----|:---------|:---------|:-----|
| **FlashAttention** | 计算/内存 IO 瓶颈 | Dao et al., 2022-2024 | 加速 2-4×，内存降为 $O(n)$ |
| **RoPE 外推** | 位置编码长度泛化 | Su et al., 2021 | 训练 4K 可推理 32K+ |
| **KV Cache 管理** | 远距离 info 衰减 | StreamingLLM、H2O | 长序列稳定 |
| **线性/稀疏注意力** | $O(n^2)$ 计算瓶颈 | Mamba、Lightning Attention | $O(n)$ 复杂度 |
| **分布式注意力** | 单 GPU 显存不足 | RingAttention (Liu et al., 2024) | 跨节点分片处理 |

### 4.3 上下文窗口演进

| 模型 | 发布时间 | 上下文 | 底层技术 |
|:-----|:-------|:-------|:---------|
| GPT-3 | 2020 | 2K | 标准 Transformer |
| GPT-4 | 2023.03 | 8K / 32K | 未知 |
| Claude 3 | 2024.03 | 200K | 专有优化 |
| Gemini 1.5 Pro | 2024.02 | 1M | MoE + RingAttention |
| DeepSeek-R1 | 2025.01 | 128K | MLA + RoPE + YaRN |
| Claude Opus 4 | 2025.05 | 300K | 专有优化 |
| MiniMax M1 | 2025.01 | 1M | Lightning Attention (线性注意力) |
| Gemini 2.5 Pro | 2025.04 | 1M | MoE + 专有优化 |

> 注意：上下文窗口是**宣称值**，实际有效利用率和尾部 token 准确率因模型而异。

---

## 5. 多模态扩展：异构数据统一

### 5.1 核心挑战（第一性原理）

**表示鸿沟**：不同模态的数据在数学结构上完全不一致

| 模态 | 数据类型 | 单位信息量 | 传统表征 |
|:-----|:---------|:----------|:---------|
| 文本 | 离散符号 | ~1.3 字节/词 | Token Embedding |
| 图像 | 连续像素阵列 | >1MB/图 (2K) | 像素张量 |
| 音频 | 时序波形 | 44.1K 样本/秒 | 频谱图 |
| 视频 | 时空像素阵列 | >50MB/秒 | 帧序列 |

**核心方法**：将异构数据**压缩映射到语言模型的共享语义空间**。

### 5.2 桥接架构路线

| 方案 | 代表模型 | 核心思路 | 优势 | 局限 |
|:-----|:---------|:---------|:-----|:-----|
| **CLIP 对齐** | LLaVA 系列 | 对比学习对齐图文特征空间 | 简单、高效 | 只有理解，不能生成视觉内容 |
| **Q-Former** | BLIP-2 (2023) | 可学习查询桥梁连接视觉与文本 | 轻量、高效 | 依赖冻结的视觉编码器 |
| **原生多模态** | Gemini、GPT-4o | 端到端从零训练 | 理解+生成的统一 | 训练成本极高 |

**Q-Former 工作原理**（BLIP-2）：

1. 视觉编码器提取图像特征
2. 一组可学习的 Query 向量与视觉特征交互
3. 输出固定长度的视觉表示 → 送入 LLM
4. **桥接但不改变 LLM**：LLM 端不参与训练，只训练 Query 和映射层

> 来源：Li et al., *BLIP-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models*, ICML 2023

### 5.3 原生多模态的突破

GPT-4o 和 Gemini 代表的新范式：

- **统一分词器**：不同模态共享 token 空间
- **端到端训练**：所有模态联合训练，而非后期拼接
- **输出任意模态**：不仅能"理解"图像/音频，还能"生成"图像/音频

---

## 6. 范式扩展：从模型到 Agent

### 6.1 核心突破

LLM 从 **"被动推理引擎"** 转向 **"主动执行系统"**，需要突破三个能力边界：

| 能力 | 传统 LLM | Agent 范式 | 关键技术 |
|:-----|:---------|:-----------|:---------|
| **信息获取** | 只能依赖训练数据 | 可以检索外部信息 | RAG、Web 搜索 |
| **行动能力** | 只能生成文本 | 可以调用工具、执行代码 | Function Calling、Code Interpreter |
| **自主规划** | 一问一答 | 可以拆解目标、多步执行 | ReAct、Tree-of-Thought、Plan-and-Solve |

### 6.2 Agent 系统组成

```text
[用户指令] -> [规划模块] -> [工具调用] -> [记忆更新] -> [输出/下一步]
                  ^            v
              [反思/自检] <- [执行结果]
```

- **技能系统**：可复用的知识封装（Function as Service）
- **记忆系统**：短期工作记忆 + 长期偏好/知识存储
- **工具调用**：API 调用、代码执行、文件操作、浏览器控制
- **自我反思**：错误检测、规划修正、经验积累
- **多 Agent 协作**：分工 + 通信 + 仲裁机制

### 6.3 当前进展

- **Coding Agent**：Claude Code、Cline 等 → AI 已能独立完成中等复杂度软件工程任务
- **企业 Agent**：内部知识检索 + 流程自动化 → 替代传统 RPA
- **多 Agent 框架**：AutoGPT × CowAgent 等的分工协作范式

> 详细分析 → [Agent 工程化](../agent-engineering/) 全系列

---

## 知识脉络总结

```text
语言建模本质 (公式)
    v
Transformer 架构 (自注意力替代 RNN)
    v
Scaling Law (为什么越大越好，Chinchilla 最优比)
    v
MoE 稀疏激活 (在更大总参数下控制推理成本)
    v
长上下文 (突破 O(n²) 瓶颈，扩展应用场景)
    v
多模态 (异构数据的统一语义空间)
    v
Agent 范式 (从推理到执行的系统扩展)
```

每个下层概念建立在上层基础之上，从**纯统计建模**逐步扩展为**通用智能系统**。

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
