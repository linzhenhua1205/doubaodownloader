# KV 压缩范式转移深度分析：从「局部规则」到「全局分配」——GraceKV（全局预算竞争）× AoH（权重谱几何、数据无关诊断）

> **元信息**：
> - GraceKV（arXiv:2608.07001，2026-08-07）：KV 缓存压缩的全局资源分配——层-头-槽原子单元 + 原型树 + 值流/预算流全局竞争
> - AoH / Autonomy-of-Heads（arXiv:2608.06849，2026-08-07）：冻结 QK 几何的数据无关稀疏注意力——核注意力算子有效秩识别 retrieval/streaming 头
> **共同主张**：KV 压缩决策不再依赖运行时信号/预定义规则——GraceKV 用全局预算竞争取代局部配额规则，AoH 用权重静态谱几何取代运行时诊断；两者共同指向部署成本更低、鲁棒性更强的压缩范式

---

## TOC

- [1. 一句话结论](#1-一句话结论)
- [2. 范式转移：为什么「局部规则」必然失效（第一性原理）](#2-范式转移为什么局部规则必然失效第一性原理)
- [3. GraceKV 深度：全局预算竞争的完整机制](#3-gracekv-深度全局预算竞争的完整机制)
- [4. AoH 深度：权重谱几何的数据无关诊断](#4-aoh-深度权重谱几何的数据无关诊断)
- [5. 数据推导全过程（公式链到实证）](#5-数据推导全过程公式链到实证)
- [6. 评估结果对比](#6-评估结果对比)
- [7. 两篇的互补与差异：同一范式的两极](#7-两篇的互补与差异同一范式的两极)
- [8. 与知识库互证](#8-与知识库互证)
- [9. 辩证批判：8 项局限](#9-辩证批判8-项局限)
- [10. 可证伪预判](#10-可证伪预判)
- [11. 结论](#11-结论)

---

## 1. 一句话结论

**KV 压缩正在经历从「预定义规则 + 运行时信号」到「一次性全局决策」的范式转移**：GraceKV 把压缩形式化为**固定预算下的全局资源分配问题**——层/头/上下文槽成为同一竞争空间，用值流（信息价值）与预算流（边际效用竞争）替代逐层固定配额；AoH 更进一步，证明**冻结权重的 QK 谱几何本身已编码头部功能**——有效秩低 = retrieval 头（需全局检索）、有效秩高 = streaming 头（sink+recent 即可），纯数据无关诊断、零校准。两者共同指向：**压缩决策从「运行时微观判断」上移到「结构/全局一次性决策」，部署成本更低、鲁棒性更强**。

---

## 2. 范式转移：为什么「局部规则」必然失效（第一性原理）

### 2.1 旧范式的三个结构性缺陷

现有 KV 压缩方法（token eviction / KV merging）的共性（GraceKV §1 原文诊断）：

1. **规则预定义**：保留哪些 token、合并到什么粒度，都是**先验固定规则**——StreamingLLM 用 attention sink、H2O 用累积注意力、SnapKV 用局部观察窗口；即便有层/头级自适应（PyramidKV/Ada-KV/D2O/ChunkKV），**分配粒度或局部配额仍需事先指定**
2. **资源不流动**：「先限定表示形式与局部配额，再做压缩决策」的范式阻止了压缩后缓存资源在层、头、上下文槽之间自由流动——高价值区域得不到更多预算
3. **分辨率与覆盖不可联合**：token eviction 只有「精确保留」与「完全删除」两种端点状态（每个位置无法处于中间分辨率）；KV merging 保覆盖但丢局部精度——两者无法在统一空间里权衡「某区域是否覆盖、覆盖到什么分辨率」

### 2.2 运行时信号的部署税（AoH §1 诊断）

稀疏注意力/KV 压缩的运行时路线（attention scores、观察窗口、校准提示、学习门控）存在系统性代价：

| 信号类型 | 代表方法 | 部署成本 |
|:---------|:---------|:---------|
| 运行时注意力分数 | H2O/D2O/SnapKV/Quest | 需在线计算/观察 token |
| 学习门控 | DuoAttention（trained gate）/ LycheeDecode（HardKuma） | 需额外训练 + 校准数据 |
| 校准提示 | RazorAttention 类 | 需任务相关校准过程 |
| 跨层复用 | CLA/YOCO/KASCADE/HySparse | 运行时稀疏索引依赖前层 |

**第一性追问（AoH 原文）**：*"Can frozen weights alone provide a useful prior for attention-head function, independent of runtime attention scores, calibration prompts, or additional training?"*
——冻结权重本身能否提供头部功能的先验？

### 2.3 新范式的统一表述

```
 = f(, )     → 
 = g(//)         → /
     +- GraceKV: g = ×
     +- AoH    : g = 
```

---

## 3. GraceKV 深度：全局预算竞争的完整机制

### 3.1 问题形式化（§Method）

**设定**：L 层 × H query heads × G KV heads（GQA），KV head g 被 query head 集合 H(g) 共享。prefill 后 layer l、KV head g 的上下文缓存：

```
K_{l,g}, V_{l,g} ∈ R^{T×d}
```

**预算定义**（式 2）：

```
B_total = ⌊L·G·N_ctx / x⌋
B_floor = |E_floor|
B_alloc = B_total − L·G·r − B_floor
```

其中：前缀/后缀完整保留且不计入预算；上下文末尾 recent window（长度 r）完整保留但**计入**预算；E_floor 为窗口外的高价值单例。

**分配问题**（式 3）：

```
max_{A'⊆A} Σ_{a∈A'} Δ(a)     s.t.  Σ_{a∈A'} c(a) ≤ B_alloc
                                     Pred(a) ⊆ A', ∀a∈A'
```

- Δ(a)：操作 a 的边际效用；c(a)：新增物理 KV 条目数；Pred(a)：前置祖先操作集（**先决约束**——Split 必须先有该节点被 Add）
- 这是**带先决约束的背包问题**——贪心按单位效用排序可解（见 3.4）

### 3.2 曲率引导语义槽分割（式 4-5）

把归一化 hidden state 视为沿 token 位置的**轨迹**，用曲率识别语义边界：

```
μ_{i,−} = (1/w)Σ_{τ=0}^{w−1} h̄_{i−τ}
μ_{i,+} = (1/w)Σ_{τ=1}^{w}   h̄_{i+τ}
δ_{i,−} = h̄_i − μ_{i,−}   δ_{i,+} = μ_{i,+} − h̄_i
κ_i^{(l,w)} = 1 − cos(δ_{i,−}, δ_{i,+})
```

稳定化（式 5）：`κ_i = Mean_{l,w} κ_i^{(l,w)} − λ_stab·Std_{l,w} κ_i^{(l,w)}`（多层层多尺度均值减标准差）；融合 token surprisal：

```
b_i = z_robust(κ_i) + λ_s·z_robust(s_i^surp)
```

槽分割 = 动态规划最大化边界分数，约束槽长 n_min ≤ |S| ≤ n_max（默认 16/128，目标 64）——**语义边界处高曲率 → 槽边界**。

### 3.3 多分辨率原型树（式 6-8）

每个 (layer l, KV head g, slot S_j) 构建原型树 T_{l,g,j}：

- **root**：单原型表示整个 slot
- **内部节点**：单原型压缩子树覆盖的连续区间
- **叶子**：token 级 K/V 条目

**Key 原型（RoPE 对齐）**（式 6）：post-RoPE 的 key 处于不同旋转坐标系 → 先逆变换到共享系、均值后恢复到代表位置：

```
k_t° = RoPE^{−1}(k_t, t)
p_v  = round((1/|I_v|) Σ_{t∈I_v} t)
k̃_v = RoPE((1/|I_v|) Σ_{t∈I_v} k_t°, p_v)
```

**Value 原型（token 值加权 + key coherence 修正）**（式 7）：

```
β_v = 0.1·Mean_{t∈I_v} R_{l,g,t}^tok
ṽ_v = Σ_t (R_{l,g,t}^tok + β_v)·v_t / Σ_t (R_{l,g,t}^tok + β_v)
```

**有效多重度**（key coherence 度量）：

```
ℏ_v = ‖Mean k_t°‖₂ / (Mean ‖k_t°‖₂ + ε)
m_v^eff = clamp(|I_v|·ℏ_v², 1, |I_v|)
```

**失真度量 D(I_v)**（式 8）：用 probe query 集 Q_v（question suffix/sequence suffix/高证据槽）量化原型 vs 原始区间的注意力失真：

```
Z_q(I_v) = Σ_{t∈I_v} e^{q^T k_t/√d}
M_q(I_v) = Σ_{t∈I_v} e^{q^T k_t/√d}·v_t
Z̃_q(I_v) = m_v^eff·exp(q^T k̃_v/√d)
M̃_q(I_v) = Z̃_q(I_v)·ṽ_v
D_q(I_v) = λ_Z·(Z_q−Z̃_q)²/(Z_q²+ε) + λ_M·‖M_q−M̃_q‖₂²/(‖M_q‖₂²+ε)
D(I_v) = Mean_q [attention-mass  D_q]
```

**attention-mass 加权防止伪优先**：很少被访问的区域不会因其局部近似误差大而获得高优先级——D 只在高关注区域有意义。

**分裂选择**：每个非叶节点在「曲率对齐二分」与「显著 token 提取」间按单位成本打分择优——前者在高曲率处分裂成两个连续子区间（净增 1 条目），后者隔离区间内最高值 token（两侧保留非空区间）。

### 3.4 Bottom-up 值流（式 9-11）：信息价值的来源

原型失真说明「能否低分辨率表示」，但不说明「该区域与当前问题相关」——GraceKV 用同一 prefill pass 估计输入条件化的任务相关性：

**token 直接相关性**（式 9）：probe 集 U（question suffix + sequence suffix query）对 compressible token t 的 softmax 概率求和：

```
s_{l,g,t} = Σ_{u∈U} Σ_{h∈H(g)} [softmax_{τ∈V(u)}((q_u^{l,h})^T k_τ^{l,g}/√d)]_t
```

**多跳衰减传播**：归一化 ŝ 跨层/头平均 → 高累积分数 token 为 first-hop seeds → 在采样层的 token 注意力图上 hop-wise 衰减传播（每跳移除已选 seeds）→ 多跳相关性 d̂_t：

```
R_{l,g,t}^tok = (1−λ_graph)·ŝ_{l,g,t} + λ_graph·d̂_t         10
R_{l,g}(v) = Σ_{t∈I_v} R_{l,g,t}^tok
```

**head 灵敏度**（式 11）：静态输出投影强度 × 动态 head 输出：

```
a_{l,g} = (Σ_{h∈H(g)} ‖W_O^{l,h}‖_F²)^{1/2}
b_{l,g} = Mean_{u∈U_q} ‖Σ_{h∈H(g)} W_O^{l,h}·o_u^{l,h}‖₂
ω_{l,g} = √(a_{l,g}·b_{l,g})
```

→ 同一 KV head 的所有操作共享 ω 作为灵敏度乘子——**权重静态强度与动态激活联合决定头部重要性**。

### 3.5 Utility-guided 预算流（式 12-13）：全局竞争的引擎

**两种操作的边际效用**（式 12）：

```
Δ_add(l,g,j)   = ω_{l,g}·R_{l,g}(r_j)·[D^drop(I_{r_j}) − D(I_{r_j})]
Δ_split(l,g,v) = ω_{l,g}·R_{l,g}(v)·[D(I_v) − Σ_{u∈child(v)} D(I_u)]
c_add = 1 c_split(v) = |child(v)| − 1
```

- Add 增益 = 灵敏度 × 槽值 ×（丢弃失真 − 原型失真）——「覆盖一个高值槽」的净收益
- Split 增益 = 灵敏度 × 节点值 ×（父失真 − 子失真之和）——「细化一个已覆盖区域」的净收益

**单位成本效用 + 全局优先队列**（式 13）：

```
U(a) = Δ(a) / c(a)
```

所有原子单元的候选操作进入**同一最大优先队列**（操作只有在前置完成后才入队）；分配器反复执行最高效用操作直至 B_alloc 耗尽——**不同层/头/槽的资源在统一效用尺度下竞争**。

**Budget-aware Singleton Floor**：贪心逐步分配会低估向高值叶子的非平滑收益 → GraceKV 在全局竞争前**精确保留 E_floor**（原样 K/V 单例），成本计入 B_floor、从后续 Add/Split 分配中排除。

**最终**：保留的前沿节点 + singleton floor 构成物理 ragged cache 供 GPU 解码；x=1 时所有树展开到 token 级叶子，**精确恢复 FullKV**。

---

## 4. AoH 深度：权重谱几何的数据无关诊断

### 4.1 核心观察（§3）：冻结权重编码头部功能

**Observation 1**：长程注意力行为**稳定**且与有效秩（ER）**负相关**——Qwen2.5-7B 上 per-head 平均注意力距离跨 4K-100K 上下文结构稳定（长程注意力是持久的头级属性而非 prompt 长度伪影）；低 ER 头倾向于注意更远。

**Observation 2**：低 ER 头**功能重要**——Llama3.1-8B@32K 的 passkey 检索实验中，把低 ER 头逐步转成 streaming（sink 128 + recent 256）→ 检索精度**快速崩溃**；高 ER 头转 streaming 影响很小；Random 居中。→ 功能分离明确：**低 ER = retrieval（需要全局访问），高 ER = streaming（sink+recent 足够）**。

### 4.2 Kernel Attention Matrix：从打分公式提炼头部算子（§4）

decode 时 head h 对第 i 个 query token 的注意力分数（无 RoPE 简化）：

```
scores_{h,i} = X_ctx · W_K^{hT} · W_Q^h · x_i
                +----  ----┘  +--  --┘
```

**定义核注意力矩阵**（式 2）：

```
M_h = W_K^{hT} · W_Q^h ∈ R^{d_model × d_model}
```

- 冻结的 query-key 匹配算子：V_h 右奇异方向 = query 侧激活方向，U_h 左奇异方向 = key 侧可匹配方向，Σ_h 奇异值 = 匹配方向强度
- **谱集中**（少量主导方向）→ retrieval 头：只需少数内容匹配方向做全局检索
- **谱弥散**（无主导全局匹配方向）→ streaming 头：sink + recent 即可

### 4.3 有效秩分类器（式 4）：谱集中度的信息论度量

```
σ̂_k = σ_{h,k} / Σ_j σ_{h,j}
eff_rank(h) = exp(−Σ_k σ̂_k·log σ̂_k) ∈ [1, r_h]
```

- 低 ER = 谱集中在少数方向（熵小）；高 ER = 谱均匀弥散（熵大）
- 分类规则：**低 ER → Retrieval；高 ER → Streaming**

### 4.4 高效计算：Sylvester 定理的 d_head 降维（式 5-6，Appendix L）

直接构造 M_h ∈ R^{d_model×d_model} 并做 SVD 昂贵且不必要——关键推导：

```
rank(M_h) ≤ min(rank(W_K^{hT}), rank(W_Q^h)) ≤ d_head
```

用 Sylvester 行列式定理（AB 与 BA 非零特征值相同）：

```
C_h = (W_Q^h·W_Q^{hT})·(W_K^h·W_K^{hT}) ∈ R^{d_head × d_head}
σ_k(M_h) = √λ_k(C_h)
```

**复杂度对比**（Qwen2.5-7B：d_head=128, d_model=3584）：
- 全矩阵构造：~5.9×10^10 操作（O(d_model³) 级）
- 代理矩阵：~4.6×10^7 操作（O(d_head²·d_model)）
- **约 1280× 计算削减**（见 §5 推导 4）

### 4.5 GQA 组级分类与部署（§5）

**组级聚合**：GQA 中每个 KV 组 g 的每个成员 Q-head 独立算 ER（共享 W_K^g，各自 W_Q^h）→ 组级分数 = 成员 ER 均值 → 每层 k = ⌈(1−s)·G⌉ 个最低 ER 组为 Retrieval Groups，其余 Streaming；组内所有 Q-head 继承标签（无歧义映射回 Q-head 级）。

**部署三步**：
1. **权重重排序**：按 ER 升序重排 Q/K/V 投影输出通道 → retrieval/streaming 头分组连续 → KV 缓存管理用高效 slice/concat 而非 scatter/gather
2. **Decode**：每层按头类型分路——Retrieval 头全注意力（完整 KV），Streaming 头 SWA（sink 128 + recent 256 定长缓存）；输出沿 head 维拼接后经共享 W_O 投影
3. **Chunked Prefill**：兼容标准 chunked prefill + FlashAttention-2——Retrieval 头保留 O(T) KV；Streaming 头每处理 chunk K 即驱逐至 sink+recent → prefill 成本 O(T²) → O(TK)，持久 KV O(s_sink+s_recent)，峰值工作内存 O(K)

**RoPE 兼容性**：RoPE-aware ER（相对旋转到 Δ=32K）与 vanilla ER 头部排序高度一致（§6.4 消融）——简化的无 RoPE 分析成立。

---

## 5. 数据推导全过程（公式链到实证）

### 推导 1：staging 预算如何约束分配（GraceKV 式 2）

B_alloc = ⌊L·G·N_ctx/x⌋ − L·G·r − |E_floor|
- 压缩率 x 决定总预算（L·G·N_ctx 全量 KV 数除以 x）
- recent window 的 r 个 token × L·G 头数**先扣掉**（窗口完整保留但占预算）
- singleton floor 的 |E_floor| 也先扣（精确保留的高值 token）
- 剩余 B_alloc 才是 Add/Split 全局竞争的池子——**预算的三级预留结构**：窗口（保局部连续性）> 单例（保高值精度）> 竞争（保全局最优）

### 推导 2：Add/Split 效用分解（式 12）

Δ_add = ω·R·(D^drop − D)：覆盖一个未覆盖槽的增益 = 头部灵敏度 × 槽信息值 ×（「删除的失真」−「原型表示的失真」）——直观上：如果原型表示已经很好（D≈D^drop），Add 增益小；如果原型很糟但槽值高，Add 增益大。
Δ_split = ω·R·(D − ΣD_children)：细化增益 = 头部灵敏度 × 节点值 ×（父失真 − 子失真和）——子节点失真和远小于父节点 → 细化收益大。
成本设计：Add=1（新增 1 个 root 原型条目），Split=|children|−1（把 1 个节点换成多个子节点，净增条目数）——**成本与物理内存增量一致**，效用单位统一为「每新增 K/V 条目的失真削减」。

### 推导 3：为什么贪心 + 单例地板是近似最优（式 3/13）

式 3 是带先决约束的背包问题（NP-hard 一般情形）；GraceKV 用单位效用 U(a)=Δ/c 排序的贪心（近似比由背包问题经典理论保证）。贪心的盲区：高值叶子需要连续多次 Split 才能到达（非平滑收益被低估）→ singleton floor 直接精确保留这部分——**用「预算预留」修补「贪心短视」，而非改用精确算法**（后者在 128× 压缩、数十万 token 规模下不可行）。

### 推导 4：AoH 的计算削减（式 5-6）

Qwen2.5-7B（d_head=128, d_model=3584）：
- 全矩阵构造 + SVD：构造 M_h 需 d_model²=1.28×10^7 元素，SVD 约 O(d_model³)≈4.6×10^10
- 代理：C_h 构造 O(d_head²·d_model)=128²×3584≈5.9×10^7；特征分解 O(d_head³)≈2.1×10^6
- 总节省约 **3 个数量级**；且 C_h 构造只需两次外积（W_Q·W_Q^T 与 W_K·W_K^T）+ 一次 d_head×d_head 乘

### 推导 5：KV 预算近似（AoH §1 脚注）

sparsity = 1 − N_full/N_total（全注意力头占比的补）；streaming 头只保留 sink(128)+recent(256)=384 tokens——在 32K/64K/128K 长上下文下可忽略 → KV budget ≈ 1 − sparsity。50% 稀疏 = 50% KV 预算（256K 时内存 −50% 的直接来源）。

### 推导 6：复杂度缩放（AoH §5）

- Prefill：Retrieval 头 O(T²) 保留；Streaming 头每 chunk 驱逐 → 后续 chunk 至多注意 s_sink+s_recent → 总成本 O(T·K)（K=chunk 大小，固定缓存）——**从二次降到线性**
- Decode：Streaming 头每步只读 384 个 KV 条目（而非 T）→ 内存带宽需求从 O(T) 降到 O(1)，这是 decode 延迟最高降 66%（256K 下 9.14×）的机制来源

---

## 6. 评估结果对比

### 6.1 GraceKV（LongBench + RULER）

| 维度 | 结果 |
|:-----|:-----|
| 总体排名 | **32 设置中 24 个第一**（LongBench 20/24）；所有 LongBench 设置保持前二 |
| 压缩鲁棒性 | 4×–128× 平滑退化；128× 仍鲁棒（基线在紧预算下急剧恶化） |
| RULER Retrieval（4K 预算） | H2O 8.75 / StreamingLLM 22.50 / CaM 10.25 / D2O 11.25 vs **GraceKV 87.25**（FullKV 87.00）——**精确检索任务上远超合并/驱逐类方法且不损失** |
| RULER Aggregation（4K） | FullKV 84.67 / CaM 85.67 / D2O 85.00 / **GraceKV 82.33**（前二） |
| 任务偏差 | 固定规则方法在 Aggregation 与 Retrieval 间剧烈摇摆；GraceKV 两任务都稳——**全局协调覆盖与分辨率消除任务偏差** |
| 内存/延迟 | 特定配置下 KV 887.4 MiB → 130.3 MiB（约 6.8×） |

**关键洞察**：Retrieval 任务（精确定位原始信息）要求保留原始 token 条目，Aggregation 任务要求广覆盖合并——固定规则无法同时满足；GraceKV 的全局分配让「覆盖 vs 分辨率」在统一效用下竞争，从而跨任务稳定。

### 6.2 AoH（LongBench，50% 稀疏）

| 维度 | 结果 |
|:-----|:-----|
| 性能保持 | 平均保留 Full Attention 的 **96.5%**（Qwen3-8B 差 0.32 点、Llama3.1-8B 差 1.10 点） |
| 稀疏基线对比 | 一致优于 Quest/SnapKV/H2O/DuoAttention 等 |
| 判据验证 | Random 头选择 / Reverse（最高 ER 当头检索）均大幅落后——**ER 排序捕获真实头功能结构** |
| 延迟 | prefill 最高 −41.4%、decode 最高 −66.0%（50% 稀疏） |
| KV 内存 | 256K tokens 时 **−50%**（=稀疏度）；75% 稀疏下 Llama3.1-8B 达 **3.24× prefill / 9.14× decode 加速、KV 3.98× 削减** |
| 稳定性 | 谱度量消融（ER 最优）；GQA 聚合消融；RoPE-aware 与 vanilla 排序高度一致 |

---

## 7. 两篇的互补与差异：同一范式的两极

| 维度 | GraceKV | AoH |
|:-----|:--------|:-----|
| 决策空间 | 层 × KV 头 × 上下文槽（原子单元） | 层 × KV 组（GQA） |
| 决策依据 | 输入相关：prefill 的 query 探测 + 权重静态强度 + 图传播 | **完全数据无关**：冻结权重谱几何 |
| 分配机制 | 全局预算竞争（值流 × 预算流，边际效用优先队列） | 静态分类（ER 阈值，k=⌈(1−s)·G⌉） |
| 表示形式 | 多分辨率原型树（合并到 token 级连续谱） | 二值：全注意力 vs sink+recent SWA |
| 部署成本 | 单次 prefill 采集 + 树构建 + 分配（全 GPU） | 一次性权重分析（offline），部署零开销 |
| 压缩粒度 | 连续可调（4×–128×） | 稀疏率可调（50%/75%…） |
| 可恢复性 | x=1 精确恢复 FullKV | 不适用（结构性稀疏） |
| 任务适配 | 全局效用竞争 → 自动适配任务 | 静态先验 → 任务无关 |

**互补关系**：
1. **决策时机**：GraceKV 仍需 per-request 的 prefill 信号（输入相关）；AoH 完全离线——AoH 可作为 GraceKV 的**头级先验**（先用 AoH 标记 streaming 头，GraceKV 只在 retrieval 头上做精细分配）
2. **粒度互补**：GraceKV 在层/头/槽三维做连续分配；AoH 在头/组二维做二值分类——GraceKV 更细、AoH 更省
3. **共同哲学**：两者都把「压缩决策」从**运行时逐 token 微观判断**上移为**一次性全局/结构决策**——区别只是全局优化的输入（GraceKV 用输入信号全局优化 vs AoH 用权重结构静态诊断）

---

## 8. 与知识库互证

| 互证点 | 关联文档/知识 | 关系 |
|:-------|:-------------|:-----|
| **KV 四层命运论** | MEMORY.md（L0 HBM 保留/L1 CPU DRAM 事实丢失/L2 持久但停摆/L3 checkpoint 半写） | GraceKV 压缩的是 L0→L1 迁移前的**空间冗余**——压缩后更多 KV 留在 L0/L1，推迟落入 L2/L3（落盘带宽需求同步下降）；与「长上下文=落盘+检索」原则互补：**先压缩再落盘** |
| **四类冗余 MECE** | MEMORY.md（时间/IO/空间/计算） | GraceKV 定点消除**空间冗余**且不牺牲时间（压缩后 KV 读取带宽下降 → 时间冗余同步缓解）；AoH 同时消除空间（KV 内存）与计算（O(T²)→O(TK)）冗余 |
| **HiSparse / 跨层 KV 复用** | 08-10 HiSparse 互证 KV 四层命运论 | AoH 明确声明与跨层方法正交、可作 data-free head prior 服务跨层/选择系统——**结构性诊断与运行时选择器解耦** |
| **LLM 推理冗余消除** | [08-05 推理冗余消除深度分析](2026-08-05-llm-inference-redundancy-elimination-deep-analysis.md) | 本分析是该线的 08-11 批次续篇：从「消除冗余」演进到「全局最优分配冗余预算」 |
| **推理系统软件栈六维** | [08-11 推理栈六维深挖](2026-08-11-ai-frameworks-inference-stack-deep-analysis.md) | 该文档已有 GraceKV/AoH 概览（§2/§3），本文为全文核实深度升级版 |
| **KV 缓存带宽/延迟预算** | [08-07 KV 缓存带宽延迟深潜](2026-07-07-kv-cache-bandwidth-latency-deep-dive.md) | AoH 的 streaming 头 384-token 定长缓存 = KV 带宽预算的结构化落地 |
| **调度与 SLO 预算** | [08-11 Cascade SLO 预算](2026-08-11-cascade-slo-latency-budget-scheduling-deep-analysis.md) | 同构哲学：Cascade 把延迟预算作为统一信号，GraceKV 把 KV 预算作为统一信号——**「资源会计化」在 KV 层的体现** |

---

## 9. 辩证批判：8 项局限

### GraceKV
1. **输入相关性残留**：GraceKV 仍依赖 prefill 的 query 信号（probe 集 + softmax 相关性）——对**预填充阶段 query 不可得**的场景（如流式/增量 prefill、纯 decode 服务）适用性存疑；论文未覆盖
2. **分配开销未完整披露**：树构建 + 值流/预算流在 GPU 上执行，但**构建时间与压缩收益的权衡**仅部分报告（附录 F）；对超长上下文（百万 token）的原型树规模与分配延迟未给出上界
3. **启发式组件多**：曲率分割的 DP、分裂选择的单位成本打分、λ 超参（λ_stab/λ_s/λ_Z/λ_M/λ_graph）——可复现性依赖细节（附录提供但工程复杂度高）
4. **RULER Aggregation 非最优**：Aggregation 任务上 GraceKV（82.33）低于 CaM（85.67）/D2O（85.00）——全局分配偏向检索精度时覆盖稍逊，非严格 Pareto 占优
5. **单例地板的选择启发式**：E_floor 的选取规则（高累积分数种子）未与「全局最优保护集」对比——地板可能保护次优 token

### AoH
6. **二值分类的信息损失**：ER 只是谱集中度的标量摘要——两个相同 ER 的头可能有不同匹配方向结构；且分类只看相对排序，丢弃了头间重要性差异（GraceKV 的 ω 灵敏度更精细）
7. **无 RoPE 推导的近似**：核心算子 M_h = W_K^T W_Q 忽略 RoPE（旋转坐标）——论文用消融证明排序一致性，但**理论上未证明 RoPE 下 ER 判据的充分性**（附录 L 的推导基于无 RoPE 设定）
8. **流式头的固定窗口**：sink(128)+recent(256) 是固定值——对需要中等距离局部注意的任务（代码、结构化文档）可能欠配；论文未做窗口尺寸自适应

### 共同
- 两篇均为 8B 级模型 + LongBench/RULER 评估；**未见 >100B 或 MoE 模型的验证**（KV 压缩收益随模型规模/上下文长度缩放——大模型行为可能不同）
- 未见与**量化压缩**（KV 量化）的联合分析——正交方向未整合

---

## 10. 可证伪预判

| # | 预测 | 核验窗口 |
|:--|:-----|:--------:|
| H1 | 全局分配范式（GraceKV 式预算竞争）在 >100B 或 MoE 模型上收益扩大（更多层/头 → 竞争空间更大 → 相对固定配额优势更明显） | 2027-06 |
| H2 | AoH 的有效秩判据被独立复现为「跨模型稳定的头功能先验」（≥2 个独立团队引用验证） | 2027-06 |
| H3 | GraceKV × AoH 组合出现：AoH 离线标记 streaming 头 → 只对 retrieval 头做 GraceKV 精细分配——成为「结构先验 + 全局优化」的默认分层 | 2027-06 |
| H4 | 数据无关诊断（AoH 类）成为 KV 压缩主流前置步骤（calibration-free 成为卖点），运行时信号方法退居辅助 | 2027-12 |
| H5 | 全局预算分配与 KV 量化（如 4-bit KV）联合后，内存削减 > 两者独立之积（分配让量化误差集中在低值区域） | 2027-06 |
| H6 | GraceKV 的「x=1 精确恢复」性质被用于动态预算场景（服务时按负载调整压缩率、无损回退） | 2027-12 |

---

## 11. 结论

GraceKV 与 AoH 共同完成了 KV 压缩的范式封边：

```
 =  token  × 
 = /
         +- GraceKV×——「」
         +- AoH    ——「」
```

第一性链条：KV 压缩的瓶颈不是「怎么压缩单个 token」，而是「预算往哪放」——**分配决策的质量决定压缩质量**。GraceKV 证明全局竞争优于局部配额（24/32 第一 + 跨任务稳定），AoH 证明决策可以完全脱离输入（冻结权重即含功能先验）。两者从「输入相关全局优化」与「权重静态结构诊断」两极逼近同一目标：**部署成本更低、鲁棒性更强**——与 Cascade 的预算会计、StrataCL 的资源会计共同构成 2026 年系统软件「决策上移、会计统一」趋势的 KV 层样本。

---

## 参考来源

1. [arXiv:2608.07001](https://arxiv.org/abs/2608.07001) — GraceKV: 全局资源分配（2026-08-07，全文 HTML 核实）
2. [arXiv:2608.06849](https://arxiv.org/abs/2608.06849) — Autonomy-of-Heads: 冻结 QK 几何数据无关稀疏注意力（2026-08-07，全文 HTML 核实）
3. [08-11 推理栈六维深挖](2026-08-11-ai-frameworks-inference-stack-deep-analysis.md) — GraceKV/AoH 首版概览（§2/§3）
4. [08-05 推理冗余消除](2026-08-05-llm-inference-redundancy-elimination-deep-analysis.md) — 四类冗余框架
5. MEMORY.md — KV 四层命运论 / 四类冗余 / HiSparse 互证

## Changelog（倒序）

- 2026-08-11：创建。基于 arXiv:2608.07001 + 2608.06849 全文（HTML 抓取核实）撰写深度分析：范式转移第一性分析、GraceKV 完整机制（预算形式化/曲率分割/原型树/值流/预算流/单例地板/6 项推导）、AoH 完整机制（观察/Kernel Attention Matrix/有效秩/Sylvester 降维推导/GQA/部署/复杂度缩放）、评估对比、两篇互补性分析、8 项局限、6 条可证伪预判
