# 🏗️ KV Cache 技术全景调研：从基础原理到前沿突破

> **整理时间**: 2026-06-12
> **标签**: `KV Cache` `推理优化` `量化` `PD分离` `缓存管理` `安全对齐` `硬件架构`
> **核心脉络**: KV Cache 是 LLM 推理的"内存瓶颈之源"，其优化已从单一的存储压缩演变为**多维度系统级工程**——涉及架构设计（GQA/MLA/稀疏注意力）、数值精度（FP8/FP4/INT）、工程管理（共享/驱逐/调度）、传输策略（PD分离语义编码）、硬件加速（CXL/NVMe/多级存储）和安全影响（对齐坍缩）六大领域。
> **关联知识**: [KVCache架构演进全景](kvcache-architecture-evolution.md) | [PD分离推理部署](pd-disaggregation-deployment.md) | [推理存储架构](./inference-context-memory-storage.md) | [CXL KV Cache Pooling](../../../03_AI/industry-research/intel-cxl-pooling.md) | [KV Cache G3.5存储](./intel-kv-cache-g35.md)

---

## 一、KV Cache 基础与成本分析

### 1.1 什么是 KV Cache

Transformer 解码时，每个 token 的 Attention 计算需要读取**之前所有 token** 的 Key 和 Value 向量。为了避免每生成一个 token 就重新计算历史 token 的 K/V，推理引擎将每一步的 K/V 缓存下来——这就是 **KV Cache**。

```
Decode 阶段计算模式:
  Step 1: 输入 token₁ → 计算 K₁,V₁ → 缓存 [K₁,V₁]
  Step 2: 输入 token₂ → 读取 [K₁,V₁] + 计算 K₂,V₂ → 缓存 [K₁,V₁,K₂,V₂]
  Step 3: 输入 token₃ → 读取 [K₁,V₁,K₂,V₂] + 计算 K₃,V₃ → ...
  
  → 每步 KV Cache 大小随上下文长度线性增长
```

### 1.2 存储成本计算

```
单 token KV = 2(K+V) × num_layers × num_heads × head_dim × precision_bytes

典型值 (BF16):
  LLaMA-70B (80层, GQA): ~320 KB/token
  DeepSeek-V3 (61层, MLA): ~68.6 KB/token
  Qwen3.5-397B (15/60 全注意力层): ~30 KB/token
  DeepSeek-V4 (61层, CSA+HCA): ~7.7 KB/token
```

| 场景 | 上下文 | 单请求 KV 大小 (70B GQA) | 成本含义 |
|:-----|:------|:------------------------|:---------|
| 短对话 | 4K | ~1.25 GB | HBM 可从容容纳 |
| 长文档 | 128K | ~40 GB | 已超单卡 HBM80 一半 |
| 代码库 | 1M | ~305 GB | 远超单卡 HBM |
| Agent 多轮 | 持续增长 | 可达数百 GB | 必须 offload 或压缩 |

### 1.3 为什么 KV Cache 是推理的第一瓶颈

**MoE 效应** — MoE 模型用稀疏激活降低 FFN 计算量，但 **KV Cache 不受 MoE 影响**（每个 token 仍需完整注意力）：

| 模型 | 参数 | KV Cache 占推理显存比 |
|:-----|:----|:--------------------|
| LLaMA-70B (Dense) | 70B | ~40% |
| Mixtral 8×7B (MoE) | 47B | **~60%** |
| DeepSeek-V3 (MoE, MLA) | 671B | ~30% (因 MLA 压缩) |
| DSV4 (MoE, CSA+HCA) | 1T+ | ~15% (因稀疏压缩) |

**趋势**: MoE 越流行，KV Cache 优化越重要——激活参数少了，但每个 token 的注意力存储开销不变。

---

## 二、KV Cache 压缩架构：7 条演进路线

### 2.1 压缩 KV 头数：MHA → MQA → GQA ✅ 生产成熟

| 架构 | KV 头数 | 压缩比 | 质量影响 | 代表模型 |
|:-----|:--------|:-------|:---------|:---------|
| **MHA** | = Q 头数 | 1× (基准) | — | 早期 GPT |
| **MQA** | 1 组 | ~1/num_heads | 明显下降 | PaLM |
| **GQA** | 分组共享 | ~1/group_ratio | 几乎无损 | Qwen2.5 (8:1), LLaMA 3 |

**核心洞察**: GQA 是当前生产环境**最成熟的折中方案**，实现了 8:1 压缩比下的几乎零质量损失。

### 2.2 压缩 KV 表示：MLA ✅ 生产验证

**核心思路**: 将 K/V 联合压缩到低维 latent 向量，而非减少头数。

**DeepSeek V3 为例**:
- MHA 基线: 每 token 14,336 维 (hidden_size × 2)
- MLA: 仅缓存 576 维 (kv_lora_rank + qk_rope_head_dim)
- **单层压缩 ~96%**，且质量不降反升（因低秩表示过滤噪声）

**工程代价**: 需要矩阵吸收或 Kernel 解压，工程复杂度中等。

**进化**: DeepSeek V4 进一步结合 CSA+HCA 稀疏注意力，将 61 层 MLA 的 68.6 KB/token 降至 **7.7 KB/token**（41 倍压缩）。

### 2.3 稀疏注意力：滑窗 → 分层压缩 ✅ 前沿部署

| 架构 | 核心机制 | KV 效果 | 复杂度 | 代表 |
|:-----|:---------|:-------|:-------|:-----|
| **SWA** | 滑动窗口，窗口外丢弃 | 固定上限 W | 低 | Mistral 7B |
| **NSA** | 三分支(压缩+精选+滑窗) | 大幅减少 | 高 | DeepSeek 2025.02 |
| **DSA** | NSA 轻量化(仅精选) | 大幅减少 | 中 | DSV3.2 |
| **CSA+HCA** | 4:1 + 128:1 分层混合 | ~V3 的 10% | 高 | **DeepSeek V4** |

**DeepSeek V4 核心设计**:
- 61 层交替: 31 层 HCA + 30 层 CSA
- **通用层**: 滑动窗口保留最近 128 token 的完整 KV
- **CSA 层**: 历史区 4:1 压缩 → Lightning Indexer top-k 选择 → Attention
- **HCA 层**: 历史区 128:1 块压缩 → 直接 Dense Attention
- 融合: 两部分注意力输出经**可学习融合**层组合

### 2.4 线性注意力：O(n) → O(1) 🔬 前沿探索

| 架构 | 隐状态形态 | KV Cache | 代表 |
|:-----|:-----------|:---------|:-----|
| **Mamba/SSM** | 1D 向量 h∈ℝᵈ | O(1), 固定大小 | Mamba 2023 |
| **Gated DeltaNet** | 2D 矩阵 S∈ℝᵈˣᵈ | O(1), 容量更大 | MIT 2024 |
| **混合架构** | 大部分线性 + 少数 Attention | ~25% | **Qwen3.5-397B** |

**Qwen3.5-397B 层配置** (60 层):
```
每 4 层一组: [DeltaNet, DeltaNet, DeltaNet, Gated Attention]
→ 仅 15 层有 KV Cache → 总量 ≈ 纯 Attention 的 25%
```

### 2.5 精度压缩：FP8/FP4/INT 量化 ✅ 生产标配

| 方式 | 位宽 | 压缩比 (vs BF16) | 适用性 | 最新进展 |
|:-----|:-----|:-----------------|:-------|:---------|
| **FP8** | 8-bit | 2× | 生产标配, 已验证 | vLLM FP8 +28.9% throughput |
| **NVFP4** | 4-bit | 4× | Blackwell 原生 | APEX4 纯W4A4 2.09× (A40) |
| **INT4** | 4-bit | 4× | 精度损失较大 | SpectrumKV 根据重要性分配 |
| **TurboQuant** | ~3.5 bit/elem | 5-6× | 向量量化, 几乎无损 | 前沿实验 |

**⚠️ 2026年重要发现** — [Alignment Collapse](#71-kv-量化对齐坍缩-alignment-collapse): 低比特量化可静默破坏安全对齐，PPL 不变 ≠ 安全不变。

### 2.6 跨层共享：CLA 🧪 学术研究

- **核心观察**: 相邻层的 K/V 向量高度相似
- **CLA2**: Layer 1 复用 Layer 0 的 KV → KV Cache 减 50%
- 与 GQA/MLA 正交组合可行
- 主要卡点: 精度损失控制和工程部署复杂度

### 2.7 压缩路线对比总结

| 路线 | 压缩幅度 | 质量影响 | 工程复杂度 | 成熟度 |
|:-----|:---------|:---------|:-----------|:-------|
| GQA | 4-8× | 几乎无损 | 低 | ✅ 生产标配 |
| MLA | ~25× | 无损+ | 中 | ✅ DSV3/DSV4 |
| 稀疏注意力 | 10-40× | 可控 | 高 | ✅ DSV4 |
| 线性注意力 | 4× | 可接受 | 高 | 🧪 Qwen3.5 |
| 精度量化 | 2-4× | 轻微 | 中 | ✅ 标配 |
| CLA | 2× | 轻微 | 中 | 🧪 学术 |

---

## 三、KV Cache 量化深度分析

### 3.1 FP8 量化：生产标配

**vLLM FP8 实践**:
- vLLM v0.22.0 引入成熟 FP8 支持 → 吞吐提升 **+28.9%** (H100)
- Per-token 动态量化 vs per-block 静态量化
- Helion (PyTorch Kernel DSL) 将 FP8 非 GEMM 核提速 1.2-2.3×

**生产要点**:
- FP8 GEMM 核 (scaled_mm) 在 Blackwell 上仍落后 CUTLASS (0.739×)
- 需 CUDA Graph 模式抵消 Kernel Launch 开销
- 自动调优耗时 ~1 天 (168 种形状全量)

### 3.2 NVFP4：Blackwell 原生

**Key Results**:
- APEX4 纯 W4A4 vLLM 替换: **2.09×** (A40), **1.78×** (RTX 3090)
- NVFP4+JAX/MaxText Blackwell 预训练: **1.31-1.73×** over FP8, 0 精度损失
- 但启动延迟代价显著 (Silicon Showdown)

### 3.3 向量量化：TurboQuant 等

**前沿方向**:
- 向量级量化 vs scalar 量化: 更高压缩比 (3.5 bit/element → 5-6×)
- 与稀疏注意力和 MLA 正交组合
- 需要专用 Kernel 支持

### 3.4 ⚠️ Alignment Collapse Under KV Quantization

**arXiv:2606.09864 (2026.06.01)** — **2026年最重要的安全警示之一**

**核心发现**:
- 低比特量化可**静默破坏安全对齐**，但 PPL 指标完全不可见
- Mistral-7B 在 PPL 仅恶化 1.03× 时**丧失了 15.2% 的拒绝能力**
- 不存在安全的通用位宽 — 存在模型特定的 sharp phase transition
- 根因: 安全特征占据**低维激活子空间**（比主特征空间脆弱 10²-10³×）

**缓解方案**:
- 安全感知的量化位宽分配（关键层高精度）
- 层选择性保护机制
- 生产建议: KV 量化评估需**强制加入安全对齐测试维度**

**对产业的影响**: 所有在生产环境中使用 KV Cache 量化的团队应重新评估量化后的安全对齐损失。

---

## 四、KV Cache 在 PD 分离中的传输策略

PD (Prefill-Decode) 分离将推理的 Prefill 和 Decode 阶段部署在不同 GPU 上。KV Cache 在 Prefill GPU → Decode GPU 之间的传输是 TTFT (Time-To-First-Token) 的核心瓶颈。

### 4.1 传输策略演进三阶段

```
阶段 1: "传或不传"        →  阶段 2: "传多少精度"     →  阶段 3: "传语义编码"
  PDTrim (二元裁剪)             SpectrumKV (精度分配)       SCD (语义蒸馏)
  FlowKV (传输消除)             NetKV (网络感知)
```

### 4.2 🏆 SpectrumKV：单 Token 精度的精度分配

**arXiv:2606.08635 (2026.06.07)**

**核心创新**: 将 KV 传输建模为**精度分配问题**，而非裁剪问题。

| 重要性等级 | 精度 | 适用 |
|:----------|:-----|:-----|
| Attention sinks + 高重要 | FP16 | 所有 token 中前 ~10% |
| 中等重要 | INT8 | ~30% |
| 低重要 | INT4 | ~60% (需模型可容忍) |

**性能数据**:
| 模型 | 50% KV budget PPL 变化 | vs PDTrim |
|:-----|:----------------------|:----------|
| Qwen2.5-7B | +1.97% | PDTrim +25.85% |
| Mistral-7B | **-0.06%** | PDTrim +22.07% |
| Gemma-2-9B | **-0.44%** | PDTrim +35.63% |
| NIAH 4K 检索 | 52.6% | PDTrim 26.3% |

端到端: **50-62% TTFT 降低**。

### 4.3 🏆 SCD：语义缓存蒸馏

**arXiv:2606.07684 (2026.06.05)**

**核心创新**: 将 KV Cache 传输从"传多少精度"进化到"传语义编码"。

**双机制**:
1. **Reuse (复用)** — 从低秩子空间重建大多数层的 KV Cache
2. **Patch (修补)** — 在稀疏过渡层预测归一化输入，截断误差传播

**性能**: 带宽受限场景下 **2.65× TTFT 加速** over oracle consumer prefill，质量在 oracle 的 5% F1 以内。

**独特价值**: 天然解决了**异构模型**（base vs fine-tuned）的 cache 复用语义错位问题。

### 4.4 NetKV：网络感知 PD 调度

**核心思路**: 不是优化传输内容，而是优化**传输时机和路由**。

- 网络拓扑感知的 KV 传输调度
- 跨节点 KV 路由选择最优路径
- 效果: **21.2% TTFT 降低**

### 4.5 FlowKV：消除跨节点 KV 传输

**核心思路**: 通过 KV 感知的 Prefill 调度，尽量让 Prefill 在靠近 Decode 的节点上执行，从根源上减少跨节点传输。

- 效果: **96% 传输消除**
- 代价: Prefill 节点选择受限

### 4.6 PD 分离 KV 传输全景对比

| 方案 | 核心思想 | 效果 | 适用场景 |
|:-----|:---------|:-----|:---------|
| **PDTrim** | 二元裁剪 (传/不传) | 高预算下可用 | 简单场景 |
| **SpectrumKV** | 精度分配 (FP16/INT8/INT4) | 50-62% TTFT↓ | 通用, 部署友好 |
| **SCD** | 语义编码 + 重构 | 2.65× TTFT↓ | 带宽受限, 异构模型 |
| **NetKV** | 网络感知路由 | 21.2% TTFT↓ | 大规模集群 |
| **FlowKV** | 调度消除传输 | 96% 传输消除 | 同地部署 |
| **KVServe** | 分离式服务框架 | 9.13× throughput | 专用推理集群 |

---

## 五、KV Cache 共享与复用

### 5.1 精确 Prefix Caching (vLLM/SGLang)

**当前生产标准**:
- 精确 token 匹配 → 复用前缀 KV Cache
- 适用: 共享 system prompt、few-shot examples
- 局限: 字面量匹配，语义相似不触发复用

### 5.2 🏆 RKSC：语义相似度共享

**arXiv:2606.09937 (ICML'26 Workshop, 2026.06.07)**

**三组件**:
1. **ASKES (Attention-Similarity KV Sharing)**: 基于 hidden-state cosine 相似度，将 prefix KV 一次计算→广播到所有语义相似分支。**严格泛化**了 vLLM 的 token-exact prefix caching
2. **CGEE (Confidence-Gated Early Exit)**: 分支置信度高时跳过验证；逐层熵稳定时提前终止
3. **RSBCM (Reasoning-Selective Block Cache Manager)**: 注意力加权深度优先 eviction

**性能**: 5 模型 × 4 基准 → 平均 **3.008×** 加速，**1.66×** over vLLM，CGEE 误差率仅 0.37%

**意义**: 从"精确前缀匹配"到"语义相似度匹配"的范式跃迁。

### 5.3 SpecKV：自适应 γ 共享

**arXiv: 最新发现 (2026.06.09)**

- 动态调整 SD γ 值 (draft 步数) 以适应不同 KV 共享策略
- 效果: **56%** 加速 in 推理场景

### 5.4 Cross-Batch KV 共享

**前沿方向**:
- 同一 batch 内多请求的公共前缀共享
- 跨 batch 的 system prompt 缓存
- Continuous batching 中的 KV 复用策略

---

## 六、KV Cache 管理与调度

### 6.1 PagedAttention → vAttention

| 方案 | 核心思想 | 典型系统 | 优势 |
|:-----|:---------|:---------|:-----|
| **PagedAttention** | 类似虚拟内存的分页管理 | vLLM | 接近零内存碎片, 支持共享 |
| **vAttention** | 虚拟地址连续映射 | 新兴方案 | 简化 Kernel, 减少 TLB miss |

### 6.2 Eviction 策略对比

| 策略 | 核心逻辑 | 适用场景 | 质量影响 |
|:-----|:---------|:---------|:---------|
| **LRU** | 最久未用 → 驱逐 | 通用 | 可接受 |
| **注意力加权** | 低注意力分数 → 驱逐 | 长上下文 | 更好 |
| **深度优先** | 浅层 KV → 优先保留 | 推理深度大 | 最好 |
| **RSBCM** | 注意力加权深度优先 | Multi-branch | 近乎无损 |

### 6.3 缓存感知调度 (Cache-Aware Scheduling)

- **Laminar**: probe-first 调度，探测各节点 KV Cache 状态后决策
- **Lodestar**: 在线路由，**1.41× TTFT** 降低
- **VeriCache**: 有损 → 无损转换，**4×** 缓存利用率提升

### 6.4 跨节点 KV 管理

随着推理集群扩展，KV Cache 管理从单节点扩展为分布式问题：

| 方案 | 核心创新 | 效果 |
|:-----|:---------|:-----|
| **MLA 跨实例路由** | "Move Query, Not Cache" | 数十 μs vs ~3ms |
| **TensorHub** | RDMA 权重传输 + KV 感知 | 6.7× stall 降低 |
| **GRIEF CVE** | KV Cache 安全漏洞暴露 | 2 个高危 CVE |

---

## 七、KV Cache 安全与风险

### 7.1 KV 量化对齐坍缩 (Alignment Collapse)

已在 [3.4 节](#34--alignment-collapse-under-kv-quantization) 详细描述。核心警示:

> **PPL 不变 ≠ 安全不变**。所有 KV 量化方案需额外安全评估维度。

### 7.2 GRIEF：KV Cache CVE 漏洞

- **影响**: KV Cache 操作中的 2 个安全漏洞 (CVE 编号)
- **风险**: 通过构造特定 Prompt 触发 KV Cache 越界访问
- **缓解**: 边界检查增强 + 内存隔离

### 7.3 Mistletoe：SD 攻击面

**arXiv: 最新发现 (2026.06.09)**

- SD 的加速机制可被攻击者利用 → **完整加快度完全崩溃**
- 攻击模式: 构造让 drafter 持续生成错误草案的 prompt
- 影响: 不仅无加速，反而比非 SD 慢数倍

### 7.4 Attention Drift 现象

**arXiv: 最新发现 (2026.06.09)**

- 长上下文推理中，attention 分布随时间逐渐偏移
- 影响: 缓存策略的假设失效
- 缓解: **2× 修复** 通过周期性重校准

---

## 八、KV Cache 硬件架构与存储

### 8.1 HBM 容量瓶颈

| GPU | HBM 容量 | 可容纳 KV (70B GQA, 4K ctx) | 备注 |
|:----|:---------|:---------------------------|:-----|
| H100 80GB | 80 GB | ~55 并发 | 实际 ~20-30 (含权重) |
| B200 192GB | 192 GB | ~140 并发 | 2.5× 前代 |
| Vera Rubin | 待公布 | 预计大幅提升 | 2026 Q4 上市 |

### 8.2 CXL 内存池化

TBD


### 8.3 G3.5 存储层级：NVMe Offload

**核心驱动力**: 降低 $/Token

| 层级 | 介质 | 延迟 | 成本/GB | 用途 |
|:-----|:-----|:-----|:--------|:-----|
| L1 | HBM | ~50ns | ~$80 | 活跃 KV Cache |
| L2 | CXL DRAM | ~250ns | ~$8 | 温 KV Cache |
| L3 | CXL NVMe | ~5μs | ~$0.15 | 冷 KV Cache |

**适用负载**:
- ⭐⭐⭐⭐⭐ 长输入序列 (1M+ ctx)
- ⭐⭐⭐⭐⭐ Agentic AI (多轮、回溯)
- ⭐⭐⭐⭐ Coding Agent
- ⭐⭐⭐⭐ 多会话 Chatbots
- ⭐⭐⭐⭐ Reasoning/CoT 模型

### 8.4 存储总拥有成本 (TCO) 分析

```
$/Token = (GPU + 存储 + 网络 + 电力) / 总 Token 数

KV Cache Offload 的三重杠杆:
  1. ↑ GPU 吞吐量: 释放 HBM → 更高并发 → 摊薄 GPU 固定成本
  2. ↓ GPU 闲置成本: 利用率 ~60% → 90%+
  3. ↓ 存储成本: NVMe ($0.15/GB) vs HBM (~$80/GB) → 500× 差距
```

---

## 九、2026 H1 最新研究分类图谱

### 9.1 论文分类统计 (2026.05-06 集中爆发)

| 方向 | 代表论文 | 数量趋势 |
|:-----|:---------|:---------|
| **KV 共享/复用** | RKSC (3.008×), SpecKV (56%), VeriCache (4×) | 🔥 新方向 |
| **PD 分离 KV 传输** | SpectrumKV (50-62%), SCD (2.65×), NetKV (21.2%) | 🔥 持续活跃 |
| **KV 量化** | Alignment Collapse, FP8/vLLM, NVFP4/Blackwell | ✅ 生产化 |
| **KV 安全** | Alignment Collapse, GRIEF CVE, Mistletoe | 🆕 新热点 |
| **KV 管理** | RSBCM, PagedAttention 演进, 缓存感知调度 | 稳定 |
| **CXL 硬件** | CXL 3.0 池化, JBOF, Beluga | 产业推进 |
| **KV + SD 联合** | K-Forcing (2.4-3.5×), WhiFlash (69.6%↑) | 融合趋势 |

### 9.2 关键技术跃迁时间线

```
2024: MHA → GQA 生产化 | PagedAttention 成熟 | FP8 量化起步
2025: MLA 大规模部署 (DSV3) | PD 分离兴起 | Prefix Caching 标准化
2026.05: Semantic KV 共享 (RKSC) | Precision KV 分配 (SpectrumKV)
2026.06: Semantic KV 编码 (SCD) | Alignment Collapse 警示
         → 安全评估引入推理栈 | CXL 3.0 池化推进
```

### 9.3 交叉融合趋势

| 融合方向 | 具体组合 | 预期收益 | 成熟度 |
|:---------|:---------|:---------|:-------|
| **量化 + 安全感知分配** | 关键层高精度 + 其他层低精度 | 安全对齐保持 | 🔬 |
| **语义共享 + 精度分配** | RKSC + SpectrumKV 联合调度 | 3.0× + 50% TTFT↓ | 🧪 |
| **PD 语义编码 + CXL 池化** | SCD 编码 + CXL 传输 | 端到端 KV 成本最优 | 🧪 |
| **稀疏注意力 + SD** | STS 联合 (2.67×) | 高性能低存储 | ✅ |
| **量化 + 跨层共享** | CLA + FP4 组合 | 8× 总压缩比 | 🧪 |

---

## 十、未来展望

### 10.1 短期 (2026H2)

- **Alignment Collapse 安全评估标准化** → 所有 KV 量化方案强制安全维度
- **SpectrumKV/SCD 工程化** → 集成到 vLLM/SGLang 生产环境
- **RKSC 范式推广** → 语义共享成为新一代 prefix caching 标准
- **CXL 3.0 推理部署** → 首个生产级 CXL 内存池化案例

### 10.2 中期 (2027)

- **融合路线** — 线性注意力处理超长全局编码 + 稀疏注意力处理中近距离检索 + 滑动窗口处理局部高保真
- **PD 分离 KV 传输成熟** — 语义编码 + 精度分配 + 网络感知三合一调度器
- **硬件-软件协同** — HBM4/CXL 3.0 原生 KV 加速指令
- **端侧部署** — 智能手机级别 KV 优化 (Lever: 2.93× on phone)

### 10.3 长期 (2028+)

- **KV Cache 可能消失?**
  - 线性注意力完全成熟 → O(1) KV 状态
  - 新架构 (如状态空间模型) 替代 Transformer
  - 光计算/存内计算 → 重新定义 "缓存" 概念
- **可能性评估**: 中度 — 架构级革命比增量优化更难，KV Cache 至少再存在 3-5 年

---

## 关联知识索引

| 文件 | 说明 |
|:-----|:------|
| [KVCache 架构演进全景](kvcache-architecture-evolution.md) | 7 条演进路线详细版 (305GB → 7.4GB) |
| [PD 分离 LLM 推理部署](pd-disaggregation-deployment.md) | 推理架构设计完整指南 |
| [推理 Context Memory 存储](./inference-context-memory-storage.md) | KV Cache 多级存储架构（本目录） |
| [存储体系近半年 AI 技术进展](../../../03_AI/industry-research/storage-systems-ai-progress-2026h1.md) | HBM/DRAM/CXL 基础层 |
| 每日跟踪 (cluster-training/2026-06-*) | 最新每日论文追踪 |
| 每日跟踪 (ai-frameworks/2026-06-*) | 推理框架最新支持 |
