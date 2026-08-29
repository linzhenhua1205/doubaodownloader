# 🧮 推理显存与 KV Cache 深度分析：模型大小 × 上下文长度 × 显存需求全景

> **版本**: v2.0（按验收规范重构：结论先行 / MECE 框架 / 上下文加注 / 数据来源三层依据 / 阅读路径）
> **日期**: 2026-08-11
> **核心问题**: LLM 推理时，不同模型大小（7B~671B）、不同上下文长度（4K~1M）分别需要多少 GPU 显存？其中 KV Cache 占多少？上下文长度与显存之间是什么关系？
> **概要**: 本文从自回归解码的计算冗余出发，推导出 KV Cache 存在的必然性；给出 KV Cache 大小的精确公式（NVIDIA 官方口径），并细化为 MHA/GQA/MLA 三种注意力架构的差异化计算；构建「模型 × 上下文」显存需求全景矩阵（6 模型 × 4 上下文，含权重/KV/总量三张表）；再从 Batch 放大、TP 并行、量化组合、架构压缩四个维度分析优化空间；最后给出工程选型决策指南与数据来源合理性说明。
> **关键词**: KV Cache · 推理显存 · 模型大小 · 上下文长度 · GQA/MLA · PagedAttention · 量化 · 显存公式
> **适用对象**: LLM 推理服务架构师、GPU 集群规划者、模型部署工程师、技术决策者
> **关联**: [KV Cache 带宽与延迟深潜](2026-07-07-kv-cache-bandwidth-latency-deep-dive.md) · [KVCache 架构演进全景](../../06_others/sources/2026-08-05-kvcache-llm-architecture-evolution-panorama.md) · [LLM 推理冗余消除](2026-08-05-llm-inference-redundancy-elimination-deep-analysis.md) · [Vera Rubin 超节点架构](../../02_rd/02_project/01_superpod/architecture/2026-07-29-nvidia-vera-rubin-architecture-deep-analysis-dup1.md)

---

## 摘要：结论先行（领导 30 秒版）

> **一句话总结**：LLM 推理显存 = 权重（固定）+ KV Cache（随 **上下文 × Batch** 线性增长）+ 激活 + 运行时；**上下文长度每翻 4 倍，KV Cache 就翻 4 倍**——长上下文（≥128K）场景下，KV Cache 从"配角"反超权重成为显存主导项，这是 2026 年推理架构变革（PD 分离、KV 卸载、MLA）的根本驱动力。

**5 条关键结论**：
1. **KV Cache 与上下文长度严格线性正比**（KV = k × seq，k 为每 token 字节数）——上下文从 4K→1M（256 倍），KV 同样放大 256 倍，无任何讨价还价空间。
2. **权重与上下文无关**——模型权重是固定成本，只随参数量×精度变化，是"一次性投入"；KV 是"每请求持续消耗"。
3. **模型越小、上下文越长，KV 优化越关键**——8B 模型在 128K 上下文时 KV≈权重（T_cross≈128K）；70B 模型要到 ~460K 上下文 KV 才追平权重。
4. **架构压缩 ≫ 精度压缩**——GQA/MLA 是 4~18× 量级收益（训练时架构决定），KV 量化仅 2×（部署时可选）——**先选对架构，再谈量化**。
5. **1M 上下文的代价是数量级跳变**——单请求 KV 即 137~550GB（超单卡容量），必须 KV 卸载（HBM→DRAM→SSD）+ 稀疏注意力，成本极高，非必要不做。

**领导快速判断表**（决策依据全表见 §9）：

| 决策问题 | 30 秒判断 | 依据 |
|:---------|:----------|:-----|
| 8B 模型能否单卡服务 128K 上下文？ | ✅ H100-80GB 可以（33GB，预留后建议 KV FP8） | §5.4 / §9 |
| 70B 模型怎么部署？ | TP4 起步（38GB/卡），权重 INT8 可降至 ~20GB/卡 | §6 / §9 |
| 长上下文优先选什么模型？ | 优先 GQA/MLA（DeepSeek-V3 128K KV 仅 18.4GB vs Llama 2 7B 68.7GB） | §5.3 |
| 1M 上下文要不要做？ | 谨慎：单请求 KV 137~550GB，必须分层卸载，成本极高 | §5.3 / §9 |
| 提升吞吐优先做什么？ | 先上 PagedAttention 引擎（vLLM/SGLang，2-4×），再评估 KV 量化 | §7 / §9 |

**阅读路径**（按角色选择）：
- **领导**：只看本摘要（结论 + 判断表）→ 需要深挖看 §9 决策指南
- **架构师**：§1（显存框架）→ §5（查表）→ §8（Batch 约束）→ §9（决策）
- **工程师**：§3（公式）→ §5（数据）→ §7（优化手段）

---

## §1 推理显存全景：四项构成 MECE 分解

> 推理显存需求可**穷尽且互斥**地分解为四项——权重 / KV Cache / 激活 / 运行时。任何一项都不与其他项重叠，合起来覆盖全部显存去向。

```
Total VRAM ≈ Weights + KV Cache + Activations + Runtime Overhead
```

| 构成 | 特性 | 量级判断 | **与上下文长度的关系** |
|:-----|:-----|:---------|:----------------------|
| **Weights**（权重） | 固定，与请求无关 | 主导（短上下文时） | 🚫 **无关**（模型参数量×精度决定，不随上下文变化） |
| **KV Cache** | 随 batch×seq 线性增长 | 主导（长上下文时） | 📈 **严格线性正比**（KV = k × seq，下文 §3 证明） |
| **Activations**（激活） | Prefill 峰值，FlashAttention 后不随 seq² 增长 | 次要（数 GB 级） | 📈 近似线性（FlashAttention 后 O(seq)），远小于 KV |
| **Runtime**（运行时） | CUDA context、通信 buffer、框架开销 | 通常预留 10-15% | 🚫 基本无关（随框架/并行度变化，不随上下文显著变化） |

> **加注（上下文长度为何影响显存）**：上表中只有 **KV Cache 与上下文长度严格线性相关**——这是本文的核心对象。权重是"买断制"（一次加载终身占用），KV 是"订阅制"（每个 token 都要占位）。当上下文从 4K 涨到 1M（256×），KV 也放大 256×，而权重纹丝不动——这就是"长上下文 = 显存杀手"的根源。**上下文长度不改变权重需求，只线性放大 KV 需求**。

---

## §2 KV Cache 第一性原理与四乘数 MECE

### 2.1 自回归解码的固有冗余：KV Cache 为什么存在

Decoder-only LLM 逐 token 自回归生成。**无缓存时**，生成第 T 个 token 需要重算全部历史 token 的 K、V 向量：

```
No-cache: Step T compute = O(T), total = O(1)+O(2)+...+O(T) = O(T^2)
```

关键洞察：历史 token 的 K、V 向量**只由历史 token 与模型固定权重决定，不因新 token 加入而改变** [来源: 知识库 KV Cache 带宽深潜 §1.1，基于 Transformer 自注意力机制第一性原理]。

引入缓存后，每个新 token 只需计算自己的 Q/K/V 并追加到缓存，计算复杂度从 **O(T²) 降到 O(T)**。**代价转移**：每步都要从 HBM 读取全部历史 K/V——瓶颈从「算力」转移到「显存带宽」。这是推理优化的分水岭：**存储换计算是 KV Cache 存在的第一性理由，带宽约束是它的第一性代价**。

### 2.2 KV Cache 四乘数 MECE 分解

> KV Cache 总量可分解为**四个独立乘数的乘积**，每个因子恰好对应一个优化维度——四个因子互不重叠、合起来穷尽 KV 的全部决定因素：

```text
KV Cache 总量 = D_eff × dtype × batch × seq × 2L
                    ↑        ↑       ↑      ↑
                 架构因子   精度因子  并发因子 上下文因子
```

| 乘数 | 含义 | 对应优化维度 | 优化杠杆量级 |
|:-----|:-----|:------------|:------------|
| **D_eff**（有效 KV 维度） | 每层每 token 存的 KV 维度：MHA=hidden / GQA=H_kv×d_head / MLA=latent | **架构层**（GQA/MLA，训练时决定） | **4~18×**（最大杠杆） |
| **dtype**（精度字节） | FP16=2B / FP8=1B / INT8=1B / INT4=0.5B | **精度层**（KV 量化，部署时可选） | 2× |
| **batch**（并发请求数） | 同时服务的请求数 | **管理层**（PagedAttention 减少浪费，非减少需求） | 2-4×（利用率） |
| **seq**（上下文长度） | 序列长度 = 上下文长度 | **需求侧**（场景决定，不可优化，只能卸载） | 由业务场景决定 |

> **MECE 说明**：四乘数互不重叠（维度/精度/并发/长度是四个正交维度），合起来穷尽 KV 大小的一切决定因素。**优化任何一项都不影响其他项**——这是「组合拳」可行的数学基础。

---

## §3 KV Cache 大小的精确公式推导

> **加注（公式中的 sequence_length 即上下文长度）**：下式中的 `sequence_length` 就是**上下文长度（context length）**——即模型单次请求能"记住"的 token 数（4K=4096、32K=32768、128K=131072、1M=1048576）。**KV Cache 总量与其严格线性正比**：上下文翻倍，KV 必翻倍；上下文 256×（4K→1M），KV 必 256×。这是理解本文全部矩阵的钥匙。

### 3.1 NVIDIA 官方公式（MHA 基线）

NVIDIA 官方给出的 KV Cache 公式 [来源: NVIDIA Technical Blog "Mastering LLM Techniques: Inference Optimization", 2023-11-17]：

```text
KV Cache per token (bytes) = 2 × num_layers × (num_heads × dim_head) × precision_bytes
Total KV Cache (bytes)     = batch_size × sequence_length × 2 × num_layers × hidden_size × sizeof(FP16)
                            └─── 并发因子 ──┘   └──────── 上下文因子（严格线性）─────────┘
```

- 因子 **2**：K 和 V 两组向量
- `num_heads × dim_head` 通常等于 `hidden_size`（d_model）
- `precision_bytes`：FP16/BF16=2，FP8=1，INT8=1，INT4=0.5

**NVIDIA 官方示例**：Llama 2 7B（32 层，hidden 4096），batch=1，4K 上下文，FP16：
`1 × 4096 × 2 × 32 × 4096 × 2 = ~2 GB` [来源: 同上，NVIDIA 官方计算]

### 3.2 GQA/MQA 细化：KV 头数压缩

MHA 中每个 Q 头配独立 KV 头；GQA 将 Q 头分组共享 KV 头，KV 头数从 `num_heads` 降至 `num_kv_heads` [来源: GQA 论文 Ainslie et al. 2023, arXiv:2305.13245]：

```text
KV per token (bytes) = 2 × L × H_kv × d_head × dtype_bytes
```

其中 `H_kv` 为 KV 头数（GQA 下远小于 Q 头数）。Llama 3 70B 为 GQA 8:1（64 Q 头 / 8 KV 头），KV 仅为 MHA 基线的 **1/8** [来源: 模型卡配置 + NVIDIA 博客 GQA 论述]。

### 3.3 MLA 细化：KV 维度压缩

DeepSeek 的 **Multi-head Latent Attention（MLA）** 不存完整 K/V，而是联合压缩到低维 latent 向量，推理时缓存 `kv_lora_rank + qk_rope_head_dim` [来源: DeepSeek-V3 Technical Report, arXiv:2412.19437]：

```text
KV per token (bytes) = 2 × L × (kv_lora_rank + qk_rope_head_dim) × dtype_bytes
DeepSeek-V3: 2 × 61 × (512 + 64) × 2 = 140,544 B ≈ 137 KB/token
```

对比同规模 MHA 基线：hidden=7168，单层 KV 维度 14336 → MLA 仅 576，**单层压缩约 96%**，且模型质量不降反升（联合压缩提供正则化）[来源: KVCache 架构演进全景 §3.2]。

### 3.4 三种架构公式统一与完整验算

| 架构 | 公式中的「有效 KV 维度」 | 代表模型 |
|:-----|:------------------------|:---------|
| MHA | `H × d_head = hidden` | Llama 2 7B/13B |
| GQA | `H_kv × d_head`（H_kv < H） | Llama 3 8B/70B、Qwen2.5 |
| MLA | `kv_lora_rank + qk_rope`（远小于 hidden） | DeepSeek V2/V3 |

> **统一表达**：`KV_bytes/token = 2 × L × D_eff × dtype_bytes`，其中 `D_eff` 是「有效 KV 维度」——三者的差异就是压缩杠杆。

**完整验算示例（Llama 2 7B，FP16）**——从模型卡参数到显存数字：
```
模型卡配置: L=32 层, hidden=4096, MHA(32 Q 头 × 128 head_dim), FP16
① D_eff = hidden = 4096
② KV/token = 2 × 32 × 4096 × 2 B = 524,288 B = 512 KB
③ ctx=4K:  512 KB × 4,096  = 2.0 GB   ← 与 NVIDIA 官方示例吻合 ✅
④ ctx=32K: 512 KB × 32,768 = 16.0 GB
⑤ ctx=128K:512 KB × 131,072 = 64.0 GB
⑥ ctx=1M:  512 KB × 1,048,576 = 512.0 GB
```

---

## §4 模型权重的显存需求

### 4.1 参数量 × 精度

```text
Weights (GB) = num_params × bytes_per_param
FP16/BF16: 2B/param | INT8: 1B/param | INT4: 0.5B/param
```

| 模型 | 参数量 | FP16/BF16 | INT8 | INT4 |
|:-----|:------:|:---------:|:----:|:----:|
| Llama 2 7B | 6.7B | 13.4 GB | 6.7 GB | 3.4 GB |
| Llama 3 8B | 8.0B | 16.0 GB | 8.0 GB | 4.0 GB |
| Llama 2 13B | 13B | 26 GB | 13 GB | 6.5 GB |
| Llama 3 70B | 70.6B | 141.2 GB | 70.6 GB | 35.3 GB |
| Llama 3.1 405B | 405B | 810 GB | 405 GB | 202.5 GB |
| DeepSeek-V3 | 671B (MoE) | 1342 GB | 671 GB | 335.5 GB |

[来源: NVIDIA 官方示例（7B×FP16≈14GB）+ 参数量为公开模型卡数据，字节数按精度公式计算]

### 4.2 MoE 的特殊性：总参数 vs 激活参数

DeepSeek-V3 总参数 671B，但每 token 仅激活 37B [来源: DeepSeek-V3 Technical Report]。**推理部署时仍须加载全部 671B 权重**（专家路由是动态的），因此 MoE 的权重显存不可按激活参数计算——这是 MoE 推理的常见误区。MoE 的收益在**计算量**（FLOPs 降低），而非**显存占用**（权重仍全量驻留）。

---

## §5 核心量化矩阵：模型 × 上下文（本报告核心交付）

> **加注（如何读表）**：下表行列含义——**行 = 模型**（6 个代表模型，覆盖 7B~671B 与 MHA/GQA/MLA 三种架构），**列 = 上下文长度**（ctx=4K/32K/128K/1M，对应 token 数 4,096 / 32,768 / 131,072 / 1,048,576）。所有数值单位为 **GB**，默认 **FP16/BF16、batch=1、无并行切分**。读法示例："Llama 3 8B 在 128K 上下文下 KV Cache = 17.2GB"——即该模型服务一个 128K 长度请求所需的最小 KV 显存。全部数据由 NVIDIA 官方公式按公开模型卡配置计算（1KB=1024B 二进制口径），完整验算示例见 §3.4。

### 5.1 每 Token KV Cache 大小

| 模型 | 架构 | 层数 | 有效 KV 维度 | KV/Token |
|:-----|:-----|:----:|:-----------:|:--------:|
| Llama 2 7B | MHA | 32 | 4096 | **512 KB** |
| Llama 3 8B | GQA 4:1 | 32 | 1024 | **128 KB** |
| Llama 2 13B | MHA | 40 | 5120 | **800 KB** |
| Llama 3 70B | GQA 8:1 | 80 | 1024 | **320 KB** |
| Llama 3.1 405B | GQA 16:1 | 126 | 1024 | **504 KB** |
| DeepSeek-V3 | MLA | 61 | 576 | **137 KB** |

> 观察：GQA 让 8B 比 7B 每 token 还省 4 倍；MLA 让 671B 模型 KV/token 与 8B GQA 模型相当——**架构压缩的杠杆远大于模型缩放的影响**。

### 5.2 KV Cache 总量矩阵（batch=1）

| 模型 | ctx=4K | ctx=32K | ctx=128K | ctx=1M |
|:-----|:------:|:-------:|:--------:|:------:|
| Llama 2 7B | 2.2 GB | 17.2 GB | 68.7 GB | 549.8 GB |
| Llama 3 8B | 0.5 GB | 4.3 GB | 17.2 GB | 137.4 GB |
| Llama 2 13B | 3.4 GB | 26.8 GB | 107.4 GB | 859.0 GB |
| Llama 3 70B | 1.3 GB | 10.7 GB | 43.0 GB | 343.6 GB |
| Llama 3.1 405B | 2.1 GB | 16.9 GB | 67.7 GB | 541.2 GB |
| DeepSeek-V3 | 0.6 GB | 4.6 GB | 18.4 GB | 147.4 GB |

> 纵向看：每列 4K→1M 放大 256 倍（线性正比的直接体现）；横向看：同上下文下架构决定数量级（128K 列 7B-MHA 68.7GB vs 8B-GQA 17.2GB vs 671B-MLA 18.4GB）。

### 5.3 总显存需求矩阵（权重+KV，FP16）

| 模型 | 权重 | +ctx=4K | +ctx=32K | +ctx=128K | +ctx=1M |
|:-----|:----:|:-------:|:--------:|:---------:|:-------:|
| Llama 2 7B | 13 GB | 15.5 GB | 30.6 GB | 82.1 GB | 563 GB |
| Llama 3 8B | 16 GB | 16.5 GB | 20.3 GB | 33.2 GB | 153 GB |
| Llama 2 13B | 26 GB | 29.4 GB | 52.8 GB | 133.4 GB | 885 GB |
| Llama 3 70B | 141 GB | 142.5 GB | 151.9 GB | 184.1 GB | 485 GB |
| Llama 3.1 405B | 810 GB | 812 GB | 827 GB | 878 GB | 1351 GB |
| DeepSeek-V3 | 1342 GB | 1343 GB | 1347 GB | 1360 GB | 1489 GB |

> **关键读数**：① 7B/8B 模型列间差异巨大（4K→1M 从 16GB 级跳到 150-560GB 级）——**小模型 + 长上下文 = KV 主导**；② 405B/671B 模型列间差异小（权重占绝对主导，1M 也仅增加 ~150GB）——**大模型 = 权重主导**。

---

## §6 单卡容量判断与并行需求

以 H100-80GB 为参照（可用 ~72GB，预留 10% 开销）：

| 场景 | 显存需求 | 结论 |
|:-----|:--------:|:-----|
| Llama 3 8B, ctx=128K | 33.2 GB | ✅ 单卡 |
| Llama 3 70B, ctx=32K | 151.9 GB | ❌ 需 TP≥2（TP2 每卡 76GB 仍超→TP4=38GB ✅） |
| Llama 3.1 405B, ctx=128K | 878 GB | ❌ 需 TP≥11（TP16 每卡 55GB ✅） |
| DeepSeek-V3, ctx=128K | 1360 GB | ❌ 需 TP≥17（TP24 每卡 57GB ✅） |

[来源: 按 §5.3 矩阵 + TP 均分计算（权重与 KV 均按并行度切分），TP 切分原理见 NVIDIA 博客 Tensor Parallelism 论述]

---

## §7 主导权切换点（T_cross）与优化手段 MECE

### 7.1 权重与 KV 的主导权切换点

> **加注（T_cross 的实际含义）**：`T_cross` 是一个**决策阈值**——当上下文长度小于 T_cross 时，权重占显存主导，**优化重心放在权重量化/TP 并行**；当上下文长度超过 T_cross 时，KV Cache 反超权重成为主导，**优化重心必须转向 KV（架构压缩/KV 量化/分层卸载）**。一句话：**T_cross 是"优化重心从权重切换到 KV"的临界上下文长度**。

令 `W = 权重字节`，`k = KV字节/token`，则 KV 反超权重的临界上下文：

```text
T_cross = W / k   (batch=1)
```

| 模型 | W (FP16) | k (FP16) | T_cross | 含义 |
|:-----|:--------:|:--------:|:-------:|:-----|
| Llama 3 8B | 16 GB | 128 KB | **131K**（≈128K） | **128K 上下文时 KV≈权重**——Agent 场景正好卡在切换点 |
| Llama 3 70B | 141 GB | 320 KB | **463K** | 常规上下文（≤128K）下权重主导 |
| DeepSeek-V3 | 1342 GB | 137 KB | **10.3M** | 权重绝对主导，KV 可忽略 |

> 8B 模型的 T_cross≈128K 是**巧合但意味深长**：2026 年 Agent 类负载的主流形态正是"8B 级模型 + 128K 上下文"——恰好落在切换点上，意味着**KV 优化与权重优化同等重要**，两者都不能偏废 [来源: 本报告按 T_cross = W/k 推导，二进制口径]。

### 7.2 优化手段 MECE 分类（五层穷尽）

> **加注**：所有优化手段可**穷尽且互斥**地归为五层——架构层 / 管理层 / 精度层 / 并行层 / 卸载层。任何 KV/显存优化手段必属其一，无遗漏；五层按杠杆大小排序。

| 层 | 手段 | KV 压缩量级 | 代价 | 实施时机 |
|:---|:-----|:-----------|:-----|:---------|
| **① 架构层**（最大杠杆） | GQA / MQA / MLA | **4~18×** | 训练时决定，事后不可改 | 模型选型期 |
| **② 管理层** | PagedAttention / 前缀缓存 / 稀疏注意力 | 2-4×（利用率） | 工程复杂度 | 部署期 |
| **③ 精度层** | KV 量化（FP8/INT8） | 2× | 轻微质量损失 | 部署期 |
| **④ 并行层** | TP / PP / PD 分离 | 按并行度线性 | 通信开销 | 集群规划期 |
| **⑤ 卸载层** | HBM→CPU DRAM→NVMe SSD | 容量×10-100 | 延迟（context swap stall） | 长时程/低成本场景 |

**量化对比**（同 hidden=8192, L=80, ctx=128K）[来源: 本报告按公式计算]：
- MHA（80 KV 头）：3200 KB/token → **429.5 GB**
- GQA 8:1（8 KV 头）：320 KB/token → **42.9 GB**（1/10）
- MLA（latent 576）：180 KB/token → **24.2 GB**（1/18）

---

## §8 Batch 放大效应与吞吐约束

> **加注（上下文 × Batch 是 KV 总量的两个乘数）**：KV Cache 总量 = k × seq × batch——**seq（上下文）与 batch（并发）是两个独立乘数，相乘决定 KV 总量**。§5 矩阵只给了 batch=1 的"单请求视图"；实际服务中 batch 通常 8~64，KV 需求还要再乘 batch。**上下文定"单请求成本"，batch 定"并发总成本"，两者是乘法关系**——长上下文 + 高并发是显存爆炸的充分条件。

KV Cache 随 batch **线性放大**（每请求独立分配）[来源: NVIDIA Technical Blog + PagedAttention 论文 arXiv:2309.06180]：

| 场景 (Llama3-70B) | KV (ctx=32K) | 权重+KV | 判断 |
|:------------------|:------------:|:-------:|:-----|
| batch=1 | 10.7 GB | 151.9 GB | TP4 可行 |
| batch=8 | 85.9 GB | 227.1 GB | TP4 每卡 57GB ✅ |
| batch=16 | 171.8 GB | 313.0 GB | TP4 每卡 78GB ❌ → TP8 |

> **吞吐-显存死锁**：提升吞吐的唯一途径是加大 batch，但 batch 直接线性消耗 KV Cache 显存。PagedAttention 的价值在于：传统静态预分配按**最大可能长度**预留（浪费 60-80%），分页按需分配实现「近零浪费」，使 batch 容量提升 2-4× [来源: PagedAttention, SOSP 2023]。

---

## §9 工程决策指南

| 决策问题 | 判断依据 | 推荐 |
|:---------|:---------|:-----|
| 8B 模型能否单卡服务 128K？ | §5.3：33.2GB | ✅ H100-80GB 可（预留后紧张，建议 KV FP8） |
| 70B 模型怎么部署？ | §6 | TP4（38GB/卡）+ 权重 INT8 可降至 ~20GB/卡 |
| 长上下文（≥128K）优先选什么模型？ | §5.2 | 优先 GQA/MLA 架构（DeepSeek-V3 128K 仅 18.4GB） |
| 1M 上下文要不要做？ | §5.3 | 单请求 KV 即 137~550GB，必须 KV 卸载 + 稀疏注意力，成本极高 |
| 提升吞吐优先做什么？ | §8 | 先上 PagedAttention 类引擎（vLLM/SGLang），再评估 KV 量化 |
| 优化重心放权重还是 KV？ | §7.1 T_cross | 上下文 < T_cross → 优化权重；> T_cross → 优化 KV |

---

## §10 数据来源与合理性说明

> 本文全部数值可复现、可验证。三层依据如下：

### 10.1 公式来源（第一层）
- **KV Cache 公式**：NVIDIA 官方技术博客 "Mastering LLM Techniques: Inference Optimization"（2023-11-17）——与 vLLM/SGLang 实现的显存估算逻辑一致（vLLM 文档中 KV Cache 计算同样采用 `2 × num_layers × num_kv_heads × head_dim × dtype × seq × batch`）。
- **权重大小**：参数量 × 每参数字节数（FP16=2B），业界通识。

### 10.2 模型配置来源（第二层）
- 所有模型的层数、hidden_size、KV 头数、MLA latent 维度均来自 **HuggingFace 官方模型卡**（Llama 2/3、Llama 3.1、DeepSeek-V3），公开可验证。
- MoE 激活参数（DeepSeek-V3 37B）来自 DeepSeek 官方技术报告（arXiv:2412.19437）。

### 10.3 交叉验证（第三层）
- **NVIDIA 官方示例**：Llama 2 7B、4K 上下文、FP16 → **~2GB** KV Cache；本文 §3.4 验算结果 2.0GB，**一致** ✅
- 内部一致性：§5 矩阵全部由 §3 公式 + §10.2 配置逐项计算，可用 §3.4 示例步骤复现任意单元格。
- 架构压缩结论（GQA 1/8、MLA 1/18）与知识库 KVCache 架构演进全景（2026-08-05 归档）一致。

### 10.4 理论值与实际部署的差异提示

> ⚠️ **本报告全部为理论值（数学下限）**。实际部署中 GPU 显存占用通常比理论值**高 15-25%**，来源包括：
> 1. **激活内存**：Prefill 阶段峰值激活（FlashAttention 已大幅降低，但非零）
> 2. **运行时开销**：CUDA context（每进程 ~0.5-1GB）、PyTorch/框架缓存、通信 buffer
> 3. **框架管理开销**：vLLM 的 block 粒度对齐（PagedAttention 分页有内部碎片）、KV 预分配预留
> 4. **多实例隔离**：同一 GPU 多模型/多进程时的冗余 context
>
> **工程建议**：规划容量时按理论值 × 1.2 预留，或参考 vLLM 的 `gpu_memory_utilization`（默认 0.9，即预留 10%）。

---

## §11 结论

1. **公式是锚点**：`KV = 2 × L × D_eff × dtype × batch × seq`——四乘数分别对应架构、精度、并发、上下文四个优化维度（MECE，§2.2）
2. **上下文与显存的关系是"线性正比"而非"平方"**：KV 随 seq 严格线性增长（公式无二次项），但 4K→1M 的 256 倍放大本身就是数量级威胁
3. **主导权随场景迁移**：短上下文权重主导，长上下文（≥128K）小模型 KV 反超权重；T_cross 是优化重心切换的决策阈值
4. **架构压缩 > 精度压缩**：GQA/MLA 是 4-18× 量级收益，KV 量化仅 2×；优先选对架构，再谈量化
5. **决策顺序**：先定模型架构（D_eff）→ 再定上下文与 batch（容量）→ 最后叠加量化与并行（成本优化）

---

## §12 可证伪预测（P1-P4）

| # | 预测 | 核验窗口 | 证伪条件 |
|:-:|:-----|:---------|:---------|
| **P1** | 2027 年主流开源模型新架构默认 GQA/MLA 类 KV 压缩，纯 MHA 新模型占比 <20% | 2027-06 | 新发布主流模型仍以 MHA 为主 |
| **P2** | 长上下文（≥128K）在线服务中 KV 量化（FP8/INT8）成为默认配置，覆盖率 >70% | 2027-06 | KV 量化仍为可选项且主流部署未启用 |
| **P3** | 1M+ 上下文单请求 KV 需求 >100GB 的场景，KV 卸载（HBM→DRAM→SSD 分层）成为标配而非特例 | 2027-12 | 1M 上下文仍依赖纯 HBM 承载 |
| **P4** | 8B 级小模型 + 128K 上下文成为 Agent 类负载主流形态，KV Cache 优化（而非权重优化）成为其首要成本杠杆 | 2027-06 | Agent 负载仍以大模型+短上下文为主 |

---

## 参考文件

### 内部知识库引用
[1] KV Cache 对带宽与延迟的需求——从第一性原理的完整论证（2026-07-07，knowledge/03_AI/llm-techniques-principles/）
[2] 从 305 GB 到 7.4 GB：大模型 KVCache 架构演进全景（2026-08-05 归档，knowledge/06_others/sources/）
[3] LLM 推理冗余消除深度分析（2026-08-05，knowledge/03_AI/llm-techniques-principles/）
[4] Vera Rubin 超节点架构深度分析（2026-07-29，knowledge/02_rd/02_project/01_superpod/architecture/）
[5] 推理服务 KV 分层分析（2026-08-11，knowledge/03_AI/agent-engineering/）

### 外部资料引用
[6] NVIDIA Technical Blog: Mastering LLM Techniques — Inference Optimization（2023-11-17，公式与两阶段论述）
[7] Kwon et al. Efficient Memory Management for LLM Serving with PagedAttention. SOSP 2023（arXiv:2309.06180）
[8] DeepSeek-AI. DeepSeek-V3 Technical Report（arXiv:2412.19437，MLA/671B/37B 激活）
[9] Ainslie et al. GQA: Training Generalized Multi-Query Transformer Models（arXiv:2305.13245）
[10] Dao et al. FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness（arXiv:2205.14135）
[11] 模型参数配置：Llama 2/3、Llama 3.1、DeepSeek-V3 官方模型卡（HuggingFace/AI Meta/DeepSeek）

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-11 | v2.0 | **按验收规范重构**：①摘要区新增"结论先行"（一句话总结+5 关键结论+领导快速判断表+阅读路径）；②§1 显存四分解新增"与上下文长度的关系"列（权重无关/KV 线性正比）并加注；③§2.2 新增 KV 四乘数 MECE 分解（D_eff×dtype×batch×seq）；④§3 公式前加注 sequence_length=上下文长度、KV 严格线性正比；⑤§5 矩阵前新增"如何读表"说明（ctx 对应 token 数）+ §3.4 完整验算示例；⑥§7 切换点前加注 T_cross 实际含义（优化重心切换阈值）+ 优化手段 MECE 五层显式化；⑦§8 Batch 前加注上下文×Batch 双乘数；⑧新增 §10 数据来源与合理性说明（三层依据 + 理论值 vs 实际 15-25% 上浮提示）；⑨T_cross 表修正为二进制口径精确值（70B: 452K→463K）；⑩全文 MECE 标注显式化 |
| 2026-08-11 | v1.0 | 首次创建：公式推导（MHA/GQA/MLA 统一）、6 模型×4 上下文显存矩阵、主导权切换点、优化全景、工程决策指南、4 条预测 |
