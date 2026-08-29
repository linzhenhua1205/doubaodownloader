# 🔬 MoE 架构深度分析：原理 · 数学推导 · 优劣势 · 服务器架构设计关注点

> **类型**: 深度专题 | **日期**: 2026-08-12 | **定位**: MoE 架构的系统性原理文档——衔接既有 MoE→硬件跟踪（每日/边界分析），补齐「从数学原理到服务器设计」的完整推导链
> **数据源**: arXiv 综述（2608.08650）+ DeepSeek-V3 技术报告 + Mixtral 技术报告 + NVIDIA 官方博客 + 第一性原理推导（推导过程可复现）
> **关联**: [`2026-06-26-moe-hardware-impact.md`](../ai-principles/2026-06-26-moe-hardware-impact.md)（硬件影响跟踪索引）、[`2026-08-11-glimmer-dense-vs-moe-boundary.md`](2026-08-11-glimmer-dense-vs-moe-boundary.md)（dense vs MoE 边界）、[`2026-08-12.md`](../../01_survey/moe-hardware/2026-08-12.md)（当日调研：Nemotron 30B MoE/3B active）、[`2026-08-10-gb300-nvl72-moe-pretraining-record-deep-analysis.md`](../../02_rd/01_product/00_hardware/01_hw-core/aiserver/2026-08-10-gb300-nvl72-moe-pretraining-record-deep-analysis.md)（MoE 数据中心主场）

---

## 📑 目录

- [0. 一句话结论](#0-一句话结论)
- [1. MoE 架构原理](#1-moe-架构原理)
  - [1.1 动机：从 dense 到稀疏激活](#11-动机从-dense-到稀疏激活)
  - [1.2 架构组成](#12-架构组成)
  - [1.3 数学形式化](#13-数学形式化)
  - [1.4 关键变体演进](#14-关键变体演进)
- [2. 数学推导](#2-数学推导)
  - [2.1 算力经济学：稀疏率与 FLOPs](#21-算力经济学稀疏率与-flops)
  - [2.2 通信开销：EP all-to-all 模型](#22-通信开销ep-all-to-all-模型)
  - [2.3 Decode 带宽模型：为什么 MoE 推理受 HBM 带宽约束](#23-decode-带宽模型为什么-moe-推理受-hbm-带宽约束)
  - [2.4 负载均衡的数学：辅助损失与无辅助方案](#24-负载均衡的数学辅助损失与无辅助方案)
  - [2.5 路由崩塌（Routing Collapse）的机制](#25-路由崩塌routing-collapse的机制)
- [3. 优劣势分析（MECE）](#3-优劣势分析mece)
  - [3.1 优势](#31-优势)
  - [3.2 劣势](#32-劣势)
  - [3.3 dense vs MoE 对比表](#33-dense-vs-moe-对比表)
  - [3.4 适用边界判定](#34-适用边界判定)
- [4. 服务器架构设计关注点](#4-服务器架构设计关注点)
  - [4.1 显存容量：全量专家驻留的容量压力](#41-显存容量全量专家驻留的容量压力)
  - [4.2 显存带宽：decode 的 memory-bound 本质](#42-显存带宽decode-的-memory-bound-本质)
  - [4.3 互联带宽：EP 通信成为一等公民](#43-互联带宽ep-通信成为一等公民)
  - [4.4 负载均衡与调度：专家热点问题](#44-负载均衡与调度专家热点问题)
  - [4.5 冷热专家与显存分层](#45-冷热专家与显存分层)
  - [4.6 PD 分离与 KV cache 协同](#46-pd-分离与-kv-cache-协同)
  - [4.7 供电/散热：稀疏激活的功耗特征](#47-供电散热稀疏激活的功耗特征)
  - [4.8 对产品决策的规格建议](#48-对产品决策的规格建议)
- [5. 产业实证数据](#5-产业实证数据)
- [6. 结论与可证伪预判](#6-结论与可证伪预判)
- [7. 数据缺口与下一步](#7-数据缺口与下一步)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 0. 一句话结论

> **MoE 的本质是「条件计算」：用路由门控把「总参数量（容量）」与「每 token 激活参数量（算力）」解耦——在相近 FLOPs 下获得远超 dense 的参数量（DeepSeek-V3: 671B 总参 / 37B 激活，稀疏率 5.5%），实现「容量红利」；但代价是把优化瓶颈从「计算」转移到「通信 + 访存」：EP all-to-all 通信和 HBM 带宽成为服务器架构设计的第一约束，这也是 2026 年 NVIDIA/AMD 超节点架构（NVLink 域内高带宽、域间稀疏调度）的第一性解释。**

---

## 1. MoE 架构原理

### 1.1 动机：从 dense 到稀疏激活

**Dense 模型的规模化困境**：

设模型参数为 N，每处理 1 个 token 的前向计算量约为：

```
FLOPs_dense(token) ≈ 2N          （乘加各计一次，含 attention + FFN）
```

dense 模型中 **容量（N）与算力（2N）线性绑定**——要更大容量就必须付出线性增长的训练/推理算力。这使规模化呈现「1 单位能力 = 1 单位算力」的刚性。

**MoE 的破解思路**：把模型拆为「总参数量 P_total」与「激活参数量 P_active」两个独立变量：

```
P_total  = P_attn + P_shared + P_experts          （全部参数，决定容量/知识存储）
P_active = P_attn + P_shared + K × P_expert       （每 token 实际使用的参数，决定算力）
```

其中 K 为每 token 激活的专家数（Top-K 路由，通常 K=1~8），P_expert 为单个专家参数量。

**稀疏率（sparsity ratio）**：

```
s = P_active / P_total
```

| 模型 | P_total | P_active | s | K | 来源 |
|:-----|:--------|:---------|:--|:--|:-----|
| Mixtral 8x7B | 47B | 13B | 0.28 | 2/8 | Mistral 技术报告 |
| DeepSeek-V3 | 671B | 37B | 0.055 | 8/256+1 shared | DeepSeek 技术报告 |
| Nemotron 3.5 Lightning | 30B | 3B | 0.10 | ~2（预估） | NVIDIA Blog 2026-08-11 |
| Qwen3-235B-A22B | 235B | 22B | 0.094 | 8/128 | Qwen 官方 |

**核心洞察**：稀疏率越低，单位算力买到的容量越高——DeepSeek-V3 用 dense 模型约 37B 的算力，获得了 671B 的容量。这是 MoE 在 2025-2026 成为大模型主流架构（Kimi K3 2.8T、DeepSeek-V3/R1、Llama 4）的根本经济原因。

### 1.2 架构组成

```
输入 x ∈ R^d
  │
  ├──→ Attention 层（dense，所有 token 必过）
  │
  ├──→ Router（门控网络，轻量 MLP，参数量 ~d×N_expert）
  │      │
  │      │  g = softmax(W_g · x)          （计算每个专家的门控分数）
  │      │  top-K = argmax_K(g)            （选出 K 个专家）
  │      │
  │      └──→ dispatch: x 被发送到 K 个专家
  │              Expert_1(x) ──┐
  │              Expert_2(x) ──┼──→ 加权求和 y = Σ_{i∈topK} g_i · Expert_i(x)
  │              Expert_K(x) ──┘
  │
  └──→ 残差连接 + 归一化 → 输出
```

三个关键组件：

1. **Router（门控网络）**：一个轻量线性层 + softmax，输出 N_expert 维概率分布。参数量仅 ~d × N_expert（如 d=4096, 8 experts 时约 32K 参数），计算成本可忽略。
2. **Experts（专家）**：每个专家是一个标准 FFN（`W_up → 激活 → W_down`），可以细粒度设计（细粒度专家 DeepSeek 用 2048 中间维度的小专家）。
3. **Dispatch/Combine（分发与合并）**：分布式场景下，token 需通过 all-to-all 通信发送到持有对应专家的 GPU，计算后再 all-to-all 收回——这是通信开销的来源。

### 1.3 数学形式化

**门控计算**（以 Top-K 门控为例）：

```
g_i(x) = softmax(W_g · x)_i = exp((W_g x)_i) / Σ_j exp((W_g x)_j)    （i = 1..N_expert）

选择集合：S(x) = {i : g_i(x) 在 Top-K 中}
```

**MoE 层输出**：

```
y = x + Σ_{i∈S(x)} g_i(x) · Expert_i(x)      （残差 + 门控加权聚合）
```

若使用 **Top-2 门控**（GShard/Mixtral）：

```
g_i(x) = g_i(x) / Σ_{j∈S} g_j(x)              （对选中专家重新归一化）
y = x + Σ_{i∈S} g_i(x) · FFN_i(x)
```

**带噪声的 Top-K 门控**（Switch/早期 MoE，提高训练稳定性）：

```
g_i(x) = softmax(W_g x + ε·softplus(W_noise x))_i
```

**训练时的负载均衡辅助损失**（Switch Transformer 形式）：

```
L_aux = α · N_expert · Σ_i f_i · P_i
```

其中 `f_i` = 被路由到专家 i 的 token 比例（实际），`P_i` = 路由到专家 i 的平均门控概率（期望）。当 f_i = P_i = 1/N 时损失最小——惩罚「token 分配与门控概率的错配」，抑制专家偏斜。

**DeepSeek-V3 无辅助损失方案**：不给主损失加辅助项，而是对每个专家的门控分数加**可学习的 bias 项** `b_i`：

```
g_i(x) = softmax(W_g x + b_i)
```

训练后根据每个专家的负载统计（batch 内 token 数）在每步更新 bias：过载专家 bias 下调、欠载专家 bias 上调，实现动态负载均衡且不干扰主损失梯度。这是 2026 年主流大模型（V3/K3）采用的关键工程创新。

### 1.4 关键变体演进

| 变体 | 年份 | 关键设计 | 意义 |
|:-----|:-----|:---------|:-----|
| Switch Transformer | 2021 | K=1（每次只激活 1 专家）| 极简路由，训练稳定 |
| GShard | 2021 | K=2 + 专家分片（EP）| 首次系统化 MoE 分布式训练 |
| Mixtral 8x7B | 2023 | K=2/8，开源标杆 | 证明 MoE 推理质量可达 dense 水平 |
| DeepSeek-MoE | 2024 | 细粒度专家 + 共享专家 | 提升专家利用率 |
| DeepSeek-V3 | 2024 | MLA + 无辅助损失均衡 + 256 细粒度专家 | 671B/37B 稀疏率 5.5%，成本 $5.58M |
| Kimi K3 | 2026 | 2.8T MoE（开放权重第一）| 国产 MoE 规模登顶 |
| Nemotron 3.5 Lightning | 2026 | 30B/3B active，NVFP4 跨三代 GPU | 边缘/Agent 场景 MoE 下探 |

**五维耦合框架**（arXiv 2608.08650 综述，2026-08）：现代 MoE 设计空间 = expert granularity（专家粒度）× expert topology（专家拓扑）× routing freedom（路由自由度）× load balancing scope（均衡范围）× execution structure（执行结构），8 个架构里程碑建模为依赖图而非线性演进。对硬件最重要的信号：**expert parallelism 被提升为与路由同等的一等控制平面**。

---

## 2. 数学推导

### 2.1 算力经济学：稀疏率与 FLOPs

**训练 FLOPs**（每 token）：

```
FLOPs_train(token) ≈ 6 × P_total       （前向 2N + 反向 4N，dense 通用公式的 MoE 扩展）
```

MoE 训练时反向传播需要更新所有被激活专家的梯度——激活 K 个专家，则反向只对 K 个专家 + attention + 共享专家求梯度。因此 MoE 的训练 FLOPs 实际为：

```
FLOPs_train_MoE(token) ≈ 6 × P_active + 2 × P_shared_extra
```

即**训练算力只与激活参数成正比**（近似），容量红利在训练端同样成立。

**推理 FLOPs**（每 token，prefill 与 decode 相同公式）：

```
FLOPs_infer(token) ≈ 2 × P_active = 2 × (P_attn + P_shared + K × P_expert)
```

**数值验证**（DeepSeek-V3）：P_active = 37B → 每 token 推理 ≈ 74 GFLOPs。对照 dense 74B 模型（2×74 = 148 GFLOPs/token），**MoE 用一半算力获得 9 倍容量**。

**效率对比公式**：

```
容量效率 = P_total / FLOPs_per_token = P_total / (2·P_active) = 1 / (2s)
```

稀疏率 s=5.5% → 容量效率是 dense 的 1/(2×0.055) ≈ **9.1 倍**——这是 MoE 的核心经济账。

### 2.2 通信开销：EP all-to-all 模型

当专家分布在多 GPU 上（expert parallelism，EP），每个 token 路由到跨卡专家时产生 all-to-all 通信。

**单层 MoE 的通信量**：

```
Comm(layer) = T × K × d × 2 × 2 bytes
```

- T = 每批 token 数（T = batch × seq_len）
- K = 激活专家数
- d = hidden 维度
- 第一个 ×2：dispatch（发送）+ combine（收回）两次传输
- 第二个 ×2：FP16 每元素 2 字节（若 BF16 同）

**通信/计算比**（决定网络是否成为瓶颈）：

```
单层计算量（2 次矩阵乘）: Compute(layer) = T × K × 2 × d × d_ffn × 2
R = Comm / Compute = (T·K·d·4) / (T·K·d·d_ffn·4) = 1 / d_ffn
```

**关键结论**：通信/计算比与 batch 大小 T **无关**，只由专家 FFN 中间维度 d_ffn 决定！d_ffn 越大（专家越大），通信占比越小。这解释了：

- **大专家（d_ffn 大）→ 通信占比低，适合弱互联**（如 8x7B 每专家 8.5B 参数）
- **细粒度小专家（d_ffn 小）→ 通信占比高，对互联带宽要求极苛刻**（DeepSeek-V3 专家中间维度仅 2048）

**数值实例**（Mixtral 8x7B，EP=8 卡，hidden=4096，d_ffn=14336，K=2，BF16）：

```
prefill T=65536（B=16×S=4096）:
  Comm = 65536 × 2 × 4096 × 4 bytes ≈ 2.1 GB / 层
  Compute = 65536 × 2 × 2 × 4096 × 14336 × 2 ≈ 1.5e13 FLOPs / 层
  H100 (989 TFLOPS BF16): Compute_time ≈ 15.6 ms
  NVLink (900 GB/s): Comm_time ≈ 2.3 ms
  R ≈ 15% → 通信可隐藏，不显著拖慢
```

```
decode T=1（单 token）:
  Comm = 1 × 2 × 4096 × 4 = 32 KB / 层
  Compute = 2 × 2 × 4096 × 14336 × 2 ≈ 4.7e8 FLOPs / 层
  Compute_time ≈ 0.5 µs，Comm_time ≈ 0.04 µs
  → 通信量小但每次触发网络往返延迟（latency 主导，非带宽主导）
```

**对细粒度 MoE（DeepSeek-V3 类）的推论**：d_ffn=2048 时 R = 1/2048 ≈ 0.05% 但绝对通信量大——因为每 token 激活 8 个专家，all-to-all 的 **dispatch 数据量 ×8**，且专家分布跨卡时通信模式从「单播」变「多播」，对 NVSwitch 全互联拓扑的要求陡增。

### 2.3 Decode 带宽模型：为什么 MoE 推理受 HBM 带宽约束

自回归 decode 阶段每步生成 1 个 token，是 **memory-bound**（每 token 算力极小，瓶颈在读取权重/激活的时间）。

**每 token 需要读取的参数**（从 HBM 到计算单元）：

```
MemRead(token) = P_active × bytes_per_param = (P_attn + P_shared + K×P_expert) × 2  （BF16）
```

**单卡理论吞吐上限**：

```
Tokens/s ≤ HBM_BW / MemRead(token)
```

**数值验证**（DeepSeek-V3，BF16，不切分）：

```
MemRead = 37B × 2 = 74 GB / token
H800 HBM BW = 3.35 TB/s
→ 单卡上限 ≈ 3.35e12 / 74e9 ≈ 45 tok/s
```

若 8 卡 EP 并行（每卡持有 1/8 专家）：

```
每卡读取 = (P_attn + P_shared + K × P_expert/8) × 2 ≈ 9-10 GB / token
→ 每卡上限 ≈ 335-370 tok/s（理想，无 attention/KV 开销）
```

**结论**：
1. **MoE decode 吞吐与 HBM 带宽严格线性相关**——这是「容量型 MoE 服务器」规格设计的第一公式：`吞吐 ∝ HBM_BW / P_active`
2. 单卡跑 671B MoE 不可能达到大吞吐（45 tok/s 上限），**EP 并行是 MoE 推理的必选项**——每卡只需持有 1/N_GPU 专家，吞吐随卡数近似线性扩展（受通信限制折损）
3. 这解释了 **GB300 超节点（NVLink 3.6TB/s·GPU）为何成为 MoE 推理主流形态**：EP 通信（2.2 节）+ 权重读取（本节）都需要「高 HBM 带宽 × 高卡间互联」双高

**FP8/NF4 量化的收益**（Nemotron 3.5 Lightning NVFP4）：

```
量化后 MemRead 减半/减 4 倍 → decode 吞吐 2-4× 提升
NVFP4: 30B MoE → 3B active × 0.5 bytes ≈ 1.5 GB/token
→ 单卡（RTX 5090 1.79 TB/s）≈ 1190 tok/s 理论上限（官方 >20K 为 dense Glimmer 对照，MoE 另有路由开销）
```

### 2.4 负载均衡的数学：辅助损失与无辅助方案

**问题定义**：设 N 个专家，T 个 token 路由。理想均匀负载为 T/N token/专家。实际路由偏斜导致：
- 过载专家：成为计算/通信热点，延长关键路径
- 欠载专家：利用率低，容量浪费

**辅助损失**（Switch Transformer 原始形式）：

```
L_aux = α · N · Σ_i f_i · P_i
f_i = (1/T) Σ_x 1{argmax g(x) = i}      （实际分配比例）
P_i = (1/T) Σ_x g_i(x)                   （平均门控概率）
```

最小化 L_aux 同时压低 f_i 与 P_i 的乘积——直觉：若某专家既被频繁选中（f_i 大）门控概率又高（P_i 大），损失就大，梯度迫使路由分散。α 通常取 0.01。

**DeepSeek-V3 无辅助损失均衡（数学）**：

```
g_i(x) = softmax(W_g x + b_i)      （b_i 为可学习 bias）

每步更新规则（batch 内）:
  b_i ← b_i - γ · sign(load_i - threshold)     （过载专家下调，欠载上调）
  load_i = batch 内路由到专家 i 的 token 数
```

优点：负载均衡信号不进入主损失梯度，避免「均衡与质量」的对抗；缺点：bias 更新是启发式（无收敛保证），需要精细调 γ。

### 2.5 路由崩塌（Routing Collapse）的机制

**现象**：训练中门控网络收敛到「几乎所有 token 都路由到少数专家」，MoE 退化为小 dense 模型。

**机制推导**（简化）：

门控梯度 ∝ Σ_i ∂L/∂g_i · ∂g_i/∂W_g。当某专家因初始优势被频繁选中，其参数更新快、输出质量高，门控给它的概率持续升高（正反馈），形成**马太效应**：

```
专家 A 质量高 → 门控概率 g_A 高 → 更多 token 流入 → A 更新更多 → 质量更高 → …
```

**缓解手段**（三件套）：
1. 辅助负载均衡损失（1.4/2.4 节）
2. Top-K 路由（K≥2）而非 Top-1：强制至少 2 个专家被激活，天然分散
3. 专家 dropout / 噪声门控：训练早期注入噪声打破正反馈
4. （新）DeepSeek-V3 的 bias 动态调整

**硬件影响**：路由崩塌若发生在推理部署（领域漂移），会造成**局部专家过载 → 单卡热点 → 集群局部延迟劣化**——服务器调度器需要「运行时专家负载监控 + 重路由」，而非仅依赖训练时均衡。

---

## 3. 优劣势分析（MECE）

### 3.1 优势

| # | 优势 | 数学/实证依据 |
|:-:|:-----|:-------------|
| A1 | **容量-算力解耦** | s=5.5% 时容量效率是 dense 的 9.1×（§2.1） |
| A2 | **训练成本低** | DeepSeek-V3 671B 训练成本 $5.58M（V3 报告），同能力 dense 估算高 3-5× |
| A3 | **推理算力按激活计** | 每 token FLOPs = 2×P_active，37B 激活 ≈ 74 GFLOPs/token |
| A4 | **知识容量大** | 671B 参数存储海量事实知识，长尾知识覆盖优于同算力 dense |
| A5 | **可扩展性好** | 新增领域 = 新增专家（training-free 扩容或增量训练），不动主干 |
| A6 | **天然适配 EP 并行** | 专家天然可分片到多卡，模型并行度高于 dense（通信模式规整） |
| A7 | **大规模 batch 下吞吐高** | batch 增大摊薄通信，算力利用率趋近激活参数占比 |

### 3.2 劣势

| # | 劣势 | 机制/实证依据 |
|:-:|:-----|:-------------|
| D1 | **显存压力：全量参数驻留** | 671B BF16 = 1342GB，需 10×H200（141GB）；dense 74B 仅需 1×H200——MoE 容量红利以「显存容量」为代价 |
| D2 | **EP 通信开销** | all-to-all 每层 T·K·d·4 bytes（§2.2）；跨节点时网络成为瓶颈 |
| D3 | **decode 受 HBM 带宽约束** | 吞吐 ∝ HBM_BW/P_active（§2.3）；单卡 671B 仅 45 tok/s |
| D4 | **路由开销与路径方差** | 每 token 门控计算 + 专家选择；同批 token 走不同路径 → 延迟不确定（NVIDIA 官方称 dense 卖点即「no routing, no variance」） |
| D5 | **负载不均衡风险** | 热点 token 集中少数专家 → 局部过载（§2.4/2.5） |
| D6 | **训练不稳定** | 路由崩塌、辅助损失与主损失对抗、收敛敏感 |
| D7 | **微调/对齐复杂** | 路由层需特殊处理（冻结/重训）；LoRA 需扩展到所有专家 |
| D8 | **小 batch 场景优势消失** | batch 小时通信无法摊薄，稀疏激活的算力优势被通信延迟吞噬 |
| D9 | **内存带宽利用率低** | 每 token 只读 K 个专家的权重，但显存中驻留全部 N 个专家——**权重加载效率 = K/N**，DeepSeek-V3 仅 8/256 ≈ 3% |
| D10 | **软件栈复杂度** | 分布式路由/负载均衡/专家卸载需专门推理框架支持（vLLM/SGLang MoE 支持成熟度不一） |

### 3.3 dense vs MoE 对比表

| 维度 | Dense | MoE |
|:-----|:------|:----|
| 参数量（容量） | N | P_total >> N（同算力下） |
| 每 token 算力 | 2N | 2×P_active（≈ 2s·P_total）|
| 显存需求 | N | P_total（全量驻留）|
| Decode 吞吐瓶颈 | HBM_BW / N | HBM_BW / P_active（更高）|
| 通信需求 | TP/PP 为主 | 额外 EP all-to-all |
| 延迟确定性 | 高（固定路径）| 低（token 路径方差）|
| 训练成本 | 与 N 线性 | 与 P_active 近似线性 |
| 小 batch 效率 | 高 | 低（通信无法摊薄）|
| 大 batch 吞吐 | 受算力约束 | 受带宽+通信约束（通常更高）|
| 部署复杂度 | 低（单卡可跑）| 高（多卡 EP + 路由框架）|

### 3.4 适用边界判定

**MoE 占优**：数据中心大规模训练/推理、大 batch 在线服务、需要海量长尾知识、容量优先场景（Kimi K3、DeepSeek-V3/R1、GPT 系列均 MoE）

**Dense 占优**：单卡/边缘部署、长时 Agent（延迟确定性优先）、小 batch 交互式推理、120K+ 长上下文单卡场景（Meta Glimmer 30B 官方定位）

**判定公式**（工程直觉，非严格）：

```
选 MoE 若: (batch_size 大) ∧ (显存可容纳 P_total) ∧ (互联带宽 ≥ 通信需求)
选 dense 若: (单卡约束) ∨ (延迟确定性要求高) ∨ (batch 小) ∨ (长上下文单卡)
```

详细边界见 [`2026-08-11-glimmer-dense-vs-moe-boundary.md`](2026-08-11-glimmer-dense-vs-moe-boundary.md)（dense 反例锚点）。

---

## 4. 服务器架构设计关注点

> 以下从 MoE 数学特性出发推导服务器规格需求，全部有公式依据（§2）。

### 4.1 显存容量：全量专家驻留的容量压力

**约束公式**：

```
VRAM ≥ P_total × bytes_per_param + KV_cache + 激活内存
```

**数值实例**：

| 模型 | P_total | BF16 驻留 | FP8 驻留 | 所需 GPU 数（H200 141GB） |
|:-----|:--------|:----------|:---------|:--------------------------|
| Mixtral 8x7B | 47B | 94GB | 47GB | 1× H200（余量给 KV）|
| DeepSeek-V3 | 671B | 1342GB | 671GB | 10× H200（BF16）/ 5× H200（FP8）|
| Kimi K3（2.8T）| ~2.8T | ~5.6TB | ~2.8TB | 40× H200（FP8，不含 KV）|

**设计要点**：
1. **全量参数必须驻留**（或高效分层换页）——MoE 服务器的显存规格由 P_total 决定，而非 P_active。这是「容量型 SKU」的核心判据（可对照知识库容量型 SKU 专题）
2. **量化是容量杠杆**：BF16→FP8 减半、→NF4 减 4 倍（Nemotron 3.5 官方 NVFP4 支持即为此）
3. KV cache 与权重竞争显存：长上下文场景需预留（128K×20tok/s 时 KV 需求可超权重，见 KV 专题）

### 4.2 显存带宽：decode 的 memory-bound 本质

**约束公式**（§2.3）：

```
单卡 decode 吞吐 ≤ HBM_BW / (P_active × bytes)
```

**设计要点**：
1. **HBM 带宽是第一性能指标**（比 FLOPs 更重要）——MoE decode 是带宽游戏。H200 4.8TB/s vs H100 3.35TB/s 即 43% 吞吐差距
2. **P_active 决定单卡上限**：30B/3B active 的 Lightning 可在消费卡跑高吞吐；671B/37B 必须多卡 EP
3. **EP 扩展近似线性**：N 卡 EP 后每卡 P_active/N，吞吐 ≈ N × 单卡上限（受通信折损）——**卡数不是越多越好**，需在「带宽收益」与「通信损耗」间取平衡点（经验上 EP 规模 ≤ 专家总数/K，且受互联带宽约束）

### 4.3 互联带宽：EP 通信成为一等公民

**约束公式**（§2.2）：

```
EP 通信量/层 = T × K × d × 4 bytes
通信占比 R = 1/d_ffn（与 batch 无关，只与专家大小有关）
```

**设计要点**：
1. **专家粒度决定互联需求**：细粒度专家（DeepSeek V3 风格，d_ffn=2048）通信占比是粗粒度（Mixtral，d_ffn=14336）的 7 倍——**国产 MoE（细粒度）对互联带宽的敏感性高于海外粗粒度模型**
2. **节点内 vs 节点间**：EP 通信应尽量限制在节点内（NVLink 900GB/s+）——超节点（NVL72 NVLink 3.6TB/s·GPU）正是「单节点容纳足够专家数」的架构答案；跨节点 EP 需要 800G/1.6T 网络且延迟敏感
3. **拓扑要求**：MoE 多播/全互联模式要求 NVSwitch 或等效全互联，非对称拓扑（如 2:1 oversubscription）会直接放大 all-to-all 延迟
4. **FoE 等架构变体**（arXiv 2605.06206）：通过 KV-head 级专家集群化消除节点间 all-to-all——若成熟，将把 MoE 推理重新拉回「节点内」形态，降低对跨节点网络的需求（前 18 期跟踪已记录）

### 4.4 负载均衡与调度：专家热点问题

**问题**：推理时 token 分布漂移导致局部专家过载（§2.5），单卡计算饱和而其他卡空闲。

**设计要点**：
1. **运行时专家负载监控**：硬件/调度器需能观测每专家 token 流入率（类似 GPU util 但细粒度到 expert 级）
2. **动态负载均衡**：推理框架层（vLLM/SGLang）支持 expert 复制（热门专家多副本）、动态重路由（UltraEP/FEPLB 等前沿方案）
3. **容量规划**：按「峰值专家负载」而非「平均负载」预留算力——热点专家所在卡需冗余（CRAFT 成本感知复制）
4. **故障语义**：EP 下单个 GPU 故障影响所有路由到其专家的请求——MoE 服务器的容错设计需要「专家级冗余」而非整卡冗余（与 RAS 专题衔接）

### 4.5 冷热专家与显存分层

**数据事实**：推理时 token 路由呈幂律分布——少数热门专家高频激活，大量长尾专家低频激活（与知识库访问幂律同构）。

**设计要点**：
1. **显存分层**：热门专家驻留 HBM，冷门专家可驻留 CPU 内存/SSD，按需换页（RotaryQuant 的 LRU 专家 offload、WiSP working-set 管理已实践）
2. **换页带宽约束**：CPU 内存带宽 50-80GB/s vs HBM 3.35TB/s——换页只能服务低频专家，换页率需 <1% 才不显著影响吞吐
3. **共享专家常驻**：共享专家（DeepSeek 设计）每 token 必激活，必须 HBM 常驻且高带宽
4. **对服务器设计含义**：MoE 推理服务器「GPU HBM 容量」与「主机内存/SSD 容量」的配比需要显式设计（主机侧容量为冷专家提供蓄水池）——对应知识库「容量型 PCIe 服务器机会：host DRAM ≥ 8× GPU HBM」的判断

### 4.6 PD 分离与 KV cache 协同

**MoE × PD 分离的交互**：

| 阶段 | MoE 特征 | 硬件需求 |
|:-----|:---------|:---------|
| Prefill（P）| 计算密集，T 大，通信占比低 | 高 FLOPs 卡，EP 通信可摊薄 |
| Decode（D）| 带宽密集，T=1，通信占比高 | 高 HBM 带宽卡，低延迟互联 |

**设计要点**：
1. **PD 分离对 MoE 天然适配**：prefill 用算力型卡、decode 用带宽型卡，避免互相拖累（与知识库「PD 分离+两池独立」判断一致）
2. **decode 池的互联要求最高**：单 token 的 EP 通信是延迟敏感型（§2.2 decode 实例），要求节点内 NVLink 而非跨节点网络
3. **KV cache 与专家权重同池竞争**：decode 池需同时容纳「权重（P_total）+ KV（随并发线性增长）」——长上下文高并发时 KV 可能反超权重成为显存主项（见 KV 四层命运论）

### 4.7 供电/散热：稀疏激活的功耗特征

**关键洞察**：MoE 的**峰值功耗由 P_total 决定（显存中驻留全部权重），实际功耗由 P_active 决定（只有激活专家计算）**——功耗远低于同参数量 dense 的估算。

**数据依据**：dense 模型功耗 ∝ 2N；MoE 计算功耗 ∝ 2×P_active，但**显存功耗 ∝ P_total**（HBM 常驻所有权重，刷新耗电）。

**设计要点**：
1. **功耗模型分离**：`P_power = P_compute(P_active) + P_memory(P_total) + P_comm`——MoE 服务器不能按 dense 公式估算功耗
2. **稀疏激活 ≠ 低功耗**：显存常驻功耗占比高，即使计算稀疏，HBM 供电不可省——供电冗余需按 P_total 显存 + 峰值激活计算设计
3. **冷却设计**：MoE 峰值计算功耗低于同容量 dense（若按算力等价），但按容量等价时（如 671B vs 74B）仍需评估——**容量型 MoE 服务器可能「显存热、计算凉」**，散热设计需关注 HBM 侧
4. **动态功耗波动**：token 路由变化导致瞬时功耗波动大，供电设计需容忍 di/dt 冲击（与 800V HVDC 供电架构专题衔接）

### 4.8 对产品决策的规格建议

| 决策维度 | MoE 适配规格 | 依据 |
|:---------|:-------------|:-----|
| **GPU 选型** | 优先 HBM 带宽/容量，FLOPs 次之 | §4.2 decode 带宽模型 |
| **单机卡数** | EP 规模 ≥ P_total/(单卡显存×量化倍数)；上限受互联带宽约束 | §4.1/4.3 |
| **互联** | 节点内 NVLink 必须全互联；跨节点需 ≥800G 且低延迟 | §4.3 EP 通信 |
| **主机内存** | host DRAM ≥ 8× GPU HBM（冷专家蓄水池）| §4.5 |
| **存储** | 高速 SSD 做专家换页池（KV 三层/专家分层共用）| §4.5 |
| **供电** | 按「显存常驻 + 峰值激活」双模型设计 | §4.7 |
| **软件** | 必须支持 EP 并行 + expert 复制/卸载 + 负载监控 | §4.4/3.2-D10 |

---

## 5. 产业实证数据

| 实证 | 数据 | 来源 | 与本文推导的印证 |
|:-----|:-----|:-----|:----------------|
| DeepSeek-V3 训练成本 | $5.58M（671B）| V3 技术报告 | 训练 FLOPs ∝ P_active（§2.1）|
| GB300 NVL72 MoE 预训练 | 1,648 TFLOPs/GPU 世界纪录 | NVIDIA 官方 | 超节点 = EP 通信 + 高带宽的架构答案（§4.3）|
| Nemotron 3.5 Lightning | 30B/3B active，速度最高 4× | NVIDIA Blog 2026-08-11 | 稀疏激活 + NVFP4 量化 → decode 带宽红利（§2.3）|
| Meta Glimmer 30B dense | >20K tok/s/GPU 单卡 | NVIDIA Blog 2026-08-10 | dense 在小模型/单卡反超（§3.4 边界）|
| Kimi K3 | 2.8T MoE（开放权重第一）| 2026-08 | MoE 规模继续上探，显存容量压力持续（§4.1）|
| RotaryQuant | 120B MoE 消费级三轴压缩 | arXiv 2608.08081 | 权重-专家-KV 三维显存压力显式建模（§4.1/4.5）|

## 6. 结论与可证伪预判

**结论**：
1. MoE 的架构本质是条件计算——容量与算力解耦，稀疏率 s 是核心经济变量
2. 服务器设计的三个第一性约束全部来自 MoE 数学：**显存容量（P_total）、HBM 带宽（P_active）、互联带宽（EP 通信）**——这三者构成 MoE 服务器规格的「不可能三角」，设计即权衡
3. 2026 年双轨并存（dense 边缘/MoE 数据中心）是场景分化的理性均衡，不是暂时的

**可证伪预判**（供后续核验）：
- P1：2027 年底前，≥50% 的开放权重 100B+ 模型为 MoE（稀疏率 ≤15%）——若 dense 大模型反超则证伪
- P2：MoE 推理服务器的「HBM 带宽/容量比」指标（GB/s per GB）成为主流规格表述——若仍以 TFLOPs 为主导则证伪
- P3：2027 年前出现「专家级容错」生产实践（单专家故障降级而非整卡 failover）——若仍整卡级 RAS 则证伪

## 7. 数据缺口与下一步

- **缺口 1**：MoE 推理「EP 规模 vs 吞吐」的实测曲线缺失——理论线性但有通信折损，需要真实基准（建议关注 STH 或厂商白皮书）
- **缺口 2**：细粒度 vs 粗粒度专家的通信量化对比缺统一基准（d_ffn=2048 vs 14336 的 R 差异已有理论，缺实测）
- **下一步**：① 用 vLLM/SGLang 对开源 MoE（如 Qwen3-235B）做 EP 规模扫描，验证 §2.2/2.3 公式；② 跟踪 UALink/超节点对 MoE EP 通信的针对性优化；③ 将 §4 规格建议并入容量型 SKU 专题的立项判据

---

## 参考来源

1. DeepSeek-V3 Technical Report（arXiv 2412.19437）：架构/成本/无辅助损失均衡
2. Mixtral of Experts（arXiv 2401.04088）：8x7B 规格与 Top-2 路由
3. Switch Transformers（arXiv 2101.03961）：K=1 与辅助损失原始形式
4. GShard（arXiv 2006.16668）：EP 与 Top-2 门控
5. arXiv 2608.08650（2026-08）：MoE 架构五维耦合综述——expert parallelism 一等控制平面
6. NVIDIA Blog 2026-08-11：Nemotron 3.5 Lightning（30B MoE/3B active，NVFP4 跨三代）
7. NVIDIA Blog 2026-08-10：Meta Muse Glimmer 30B dense（dense 边界官方锚点）
8. arXiv 2608.08081（2026-08）：RotaryQuant 三轴压缩（角色量化+LRU 专家+等向 KV）
9. arXiv 2605.06206（2026-05）：FoE——KV-head 级集群化消除 all-to-all
10. 本知识库 moe-hardware 系列跟踪（2026-07 至 08-12，20+ 期）

## Changelog

- 2026-08-12: 创建——MoE 原理/数学推导（稀疏率、FLOPs、EP 通信、decode 带宽、负载均衡）/优劣势 MECE/服务器架构 8 关注点/产业实证/可证伪预判
