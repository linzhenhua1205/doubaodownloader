# 🎯 GPU 芯片设计深度分析：训练 vs 推理 + MoE 架构影响

> **等级**: ⭐⭐⭐ | **创建**: 2026-06-10
> **研究原则**: 第一性原理 — 从计算特性本质差异出发推导演进方向，不堆砌厂商参数
> **核心问题**: 训练和推理场景对 GPU 芯片设计的要求有何本质差异？MoE 架构如何改变设计目标？
> **证据基础**: 80+ 条 arXiv 论文 + 工业进展 + NVIDIA/AMD/Intel 官方发布
> **交叉引用**: [`gpu-ai-chips.md`](gpu-ai-chips.md) · [`moe-hardware-impact.md`](moe-hardware-impact.md) · [`server-form-factor.md`](server-form-factor.md) · `server-hardware/`

---

## 目录

1. [训练 vs 推理：计算特性本质差异](#一训练-vs-推理计算特性本质差异)
2. [训练专用 GPU 设计建议](#二训练专用-gpu-设计建议)
3. [推理专用 GPU 设计建议](#三推理专用-gpu-设计建议)
4. [MoE 对 GPU 设计的根本性冲击](#四moe-对-gpu-设计的根本性冲击)
5. [MoE 训练专用 GPU 设计（arXiv 证据驱动）](#五moe-训练专用-gpu-设计arxiv-证据驱动)
6. [MoE 推理专用 GPU 设计（arXiv 证据驱动）](#六moe-推理专用-gpu-设计arxiv-证据驱动)
7. [qs 不等式对硬件路线的冲击](#七qs-不等式对硬件路线的冲击)
8. [综合设计决策矩阵](#八综合设计决策矩阵)
9. [最终建议清单（优先级排序）](#九最终建议清单优先级排序)
10. [附：关键引用论文清单](#十附关键引用论文清单)

---

## 一、训练 vs 推理：计算特性本质差异

### 训练的核心矛盾：算力渴求型（Compute-bound）

| 维度 | 特性 | 对硬件的要求 |
|:-----|:-----|:-------------|
| Forward + Backward | 需计算完整梯度流，不可跳过层 | 矩阵乘法吞吐为王 |
| 精度要求 | 梯度累积需要高精度 → FP32 master weights | 混合精度管线（FP32 accumulate + BF16/FP8 compute） |
| 批大小 | 大 batch（几万～百万 tokens） | 需要大算力，TCO 优先 |
| 通信模式 | AllReduce 密集 | 每步计算后同步梯度 → 通信带宽是关键瓶颈 |
| 内存占用 | Weights + 梯度 + 优化器状态 + 激活值 = 4-6× 模型大小 | 大 HBM 容量 + 高带宽 |
| 非均匀计算 | 不同层计算量不均匀 | Pipeline 气泡管理 |

### 推理的核心矛盾：存储带宽渴求型（Memory-bandwidth-bound）

| 维度 | 特性 | 对硬件的要求 |
|:-----|:-----|:-------------|
| Auto-regressive 解码 | 每次生成 1 个 token，重复读 KV Cache | **带宽决定速率**，而非算力 |
| PD 分离 | Prefill = 计算密集，Decode = 带宽密集 → 两个完全不同 profile | 芯片需同时 handle 两种特性的负载，或 PD 分离 × 专用硬件 |
| KV Cache 膨胀 | 长上下文（128K～1M tokens）的 KV Cache 可达几百 GB | 大 HBM + KV 量化 + 层级存储 |
| 低延迟要求 | TTFT < 1s，TPOT < 50ms | 小 batch / 单用户的处理效率 |
| MoE 推理 | Expert Parallel — 每个 token 只激活少量 expert → 通信密集 | AlltoAll 低延迟 + 稀疏路由 |
| Batching 波动 | Continuous batching，batch size 动态变化 | 动态调度能力 |

### 关键洞察

```
训练瓶颈漏斗（按影响排序）:
  算力 (TFLOPS) → 通信带宽 (GB/s) → 显存容量 (GB)

推理瓶颈漏斗（按影响排序）:
  显存带宽 (GB/s) → 显存容量 (GB) → 算力 (TFLOPS)

PD分离后:
  训练 ≈ Prefill (Compute-bound) ≈ 算力不足
  Decode (Memory-bound) ≈ 带宽不足
```

**结论**: 训练 GPU 是"算力引擎"，推理 GPU 是"存储管路"。二者本质不同，将加速分化。

---

## 二、训练专用 GPU 设计建议

### 建议 ①：Matrix Engine 追求纯稠密算力

| 设计要点 | 理由 | 量化参考 |
|:---------|:-----|:---------|
| BF16/FP8 Tensor Core 为主 | 训练主流精度 | BF16 throughput = 2× FP32 |
| FP32 accumulate 硬件原生 | 避免软件模拟精度损失 | Master weight 累积 |
| FP64 只保留最小单元 | 非科学计算可不做 | < 1/256 of FP32 |
| 取消 INT4/FP4 路径 | 训练几乎不用 | 节省 die area |
| 2:4 结构化稀疏选配 | Ampere 引入但 ROI 有限 | 取决于模型团队是否利用 |

### 建议 ②：SRAM/L1 做大，减少 HBM 访问

训练时激活值（activations）存到 SRAM 可大幅减少 HBM 读写。

| 对比 | H100 | B300 | 建议值 |
|:----|:-----|:-----|:-------|
| SRAM per SM | 256 KB | ~512 KB | **512 KB~1 MB** |
| Shared Memory | 228 KB | ~256 KB | **384 KB+** |
| L2 Cache | 50 MB | 120 MB | **200 MB+** |

> 每个额外的 SRAM 减少了 activation checkpointing 的 HBM 写入 → 训练吞吐 +5~15%

### 建议 ③：互联带宽 > 互联范围

| 设计 | 建议 |
|:-----|:-----|
| Scale-up 互联 | NVLink 5+ 级别（1.8 TB/s+），域内 8 GPU 即可 |
| Scale-out 互联 | 800Gbps RoCE/IB，不需要域内 72 GPU |
| 原因 | 训练通过 DP/TP/PP 组合，8 GPU 域足够高效，更大的域 PP 气泡成本大于收益 |

### 建议 ④：功耗设计

训练 GPU 常年在 TDP 100% 运行 → 散热稳定性比峰值更重要：
- TDP 700~1200W（H100 700W → B200 1000W → B300 1200W）
- 液冷标配，风冷不够
- 供电效率 > 瞬时性能（VR 效率 95%+）


---

## 三、推理专用 GPU 设计建议

### 建议 ①：Memory bandwidth 是第一优先级

推理解码时，token 生成速率 ≈ memory bandwidth / (模型参数 + KV Cache 读取量)。

| 设计 | 建议 | 效果 |
|:-----|:-----|:-----|
| HBM3e → HBM4 | 带宽 3.2 TB/s → 8+ TB/s | Token 率直接翻倍 |
| HBM stack 数量 | 8→12→16 stack | 线宽翻倍 |
| SRAM 做 KV Cache 缓存 | 增加片上 SRAM 缓存最近 KV | 命中率是关键 |
| 带宽优先于算力 | Tensor Core 密度可适当降低 | 面积换带宽 |

**关键拓扑建议**: HBM 控制器数量 > Tensor Core 数量。训练 GPU 上 Tensor Core 利用率为 70-90%，推理上可能只有 10-30%——瓶颈在 HBM，不在 CUDA Core。

### 建议 ②：KV Cache 专用硬件路径

当前 GPU 架构中，KV Cache 读取走通用 Memory 路径，与权重争用带宽。

| 方案 | 说明 | 收益预估 |
|:-----|:-----|:---------|
| KV Cache 专用读取口 | 独立带宽通道，不与 weights 争用 | 2× 有效带宽 |
| 片上 KV Cache SRAM | 1~4 MB/core 的 KV 缓存 | 短上下文（8K）命中率 > 50% |
| KV 量化硬件单元 | 原生支持 INT4/INT2 KV → HBM 写入前硬件量化 | 4-8× KV 容量/带宽有效提升 |
| PagedAttention 硬件加速 | vLLM PagedAttention 片上实现 | 减少碎片化带宽浪费 |

### 建议 ③：低精度推理链路硬件化

推理的主流精度在持续降低：BF16 (2022) → FP8 (2023) → FP4/INT4 (2024~2025) → INT2/混合精度 (2026+)

| 精度 | 推荐硬件实现 | 备注 |
|:-----|:------------|:-----|
| FP4 | 原生 Tensor Core 支持（Blackwell 已实现） | 权重 + KV Cache 双用 |
| FP8 | 已经成为标配 | 1× over BF16 |
| INT4 量化 | 权重 + 激活值联合量化硬件 | 避免精度损失 |
| INT2 实验性 | 推理专用路径，不占主算力 | 长上下文 KV Cache |

### 建议 ④：PD 分离 × 芯片级支持

PD 分离将 Prefill（计算密集）和 Decode（带宽密集）分配到不同 GPU——推理芯片应在架构层面原生支持这种分离。

**推荐方案**: 推理芯片内部**双模式调度**
- Prefill Mode: 所有 Tensor Core 全开 → 最大化算力
- Decode Mode: Tensor Core 关一半，memory 全开 → 最大化读写效率
- 切换时间 < 50μs

**更激进方案**: 异构架构——部分 Core 为 Prefill 优化（大 SRAM/多 Tensor Core），部分为 Decode 优化（大 HBM 路径/少 Tensor Core），类似 CPU big.LITTLE：

| 类型 | Core 数 | SRAM | Tensor Core | 用量 |
|:-----|:--------|:-----|:------------|:-----|
| P-Core (Prefill) | 32 | 1 MB | 8× dense | 高峰期全开 |
| E-Core (Decode) | 96 | 256 KB | 2× bandwidth-opt | 常态运行 |

### 建议 ⑤：推理 GPU 的功耗/散热设计

推理 GPU 的利用率波动大（高峰→低谷→空闲），与训练常年 100% 不同：

| 特性 | 建议 | 理由 |
|:-----|:-----|:-----|
| 动态功耗调节 | μs 级 DVFS | 推理负载 burst，不需要一直高功耗 |
| 推理优化 TDP | 300~600W | 推理算力需求低，高功耗浪费 |
| 风冷可选 | 300-400W 可风冷 | 降低 TCO |
| 空闲功耗 | < 50W | 多卡推理空闲时省电 |

---

## 四、MoE 对 GPU 设计的根本性冲击

### MoE 打破的两个"GPU 基本假设"

**假设 ① "全模型在每张 GPU 上完整加载"**（Dense 模型行为 → 计算模式高度可预测）

**MoE 行为**: 每个 token 只激活 2~4 个 expert → 计算模式随机 + 碎片化

> **量化证据**（DODOCO, arXiv:2605.20982）:
> - MoE 路由 Gini 系数分布在 0.105~0.38（取决于架构）
> - **路由不均 = 模型架构固有属性**，不能通过调整 expert 布局消除
> - MLA/GDN 架构的 Gini 高达 0.24-0.38，MHA/Mamba-2 为 0.105-0.150
>
> → 不能假设"所有 GPU 核心负载均等"。MoE GPU 必须容忍高度动态、统计上偏斜的工作负载分布。

**假设 ② "主导通信原语是 AllReduce"**（Dense 模型通信 → 每步一次 AllReduce → 对称可预测）

**MoE 通信**: AlltoAll（训练）+ 稀疏 AlltoAll（推理）+ Expert Parallel 通信 → 通信模式非对称

| 通信原语 | Dense | MoE |
|:---------|:------|:-----|
| AllReduce | 🔴 主导（梯度同步） | 🟢 次要（仍保留） |
| AlltoAll | 🟢 无 | 🔴 **主导**（Expert 路由） |
| AllGather/ReduceScatter | 🟢 少量 | 🔴 **大量**（EP 通信） |

> → AlltoAll 和 AllReduce 的硬件需求完全不同。GPU 互联设计不能只优化 AllReduce。

### MoE 推理的"三元负载分解"

基于 AFD（arXiv:2605.28302）将 MoE 推理分解为三个异构阶段:

```
【Attention 阶段】Memory-bound → 带宽大战
  每个 token 读全量 KV Cache
  OI (Operational Intensity) < 0.5

【MoE Dispatch/Combine】Communication-sensitive → 延迟大战
  AlltoAll 路由 token 到 expert
  数据量 < 1MB/token

【FFN (Expert) Compute】Compute-bound → 算力大战
  MatMul: batch = 小 → 算力利用率低 (10-30%)
```

> 传统 GPU 同时处理三种负载→每种都达不到最优→算力和带宽都浪费。
> 这推动了"核中核"或专用硬件的需求。


---

## 五、MoE 训练专用 GPU 设计（arXiv 证据驱动）

### 建议 ①：互联系统重新设计——从"越高越好"到"刚好够用+软件补足"

**证据链**（3 篇独立论文交叉验证）:

| 论文 | 核心发现 | 对互联的影响 |
|:-----|:---------|:------------|
| **Rethinking Network Topologies** (arXiv:2605.00254) | 3D full-mesh 拓扑 Pareto 最优，**降低 27% scale-up 带宽后每美元吞吐反而提升** | 不需要满配 scale-up 互联 |
| **NIMBLE** (arXiv:2604.00317) | 运行时负载均衡，MoE AlltoAll 提升 **5.2×** over NCCL | 软件可补偿硬件非对称 |
| **RailS** (arXiv:2605.22990) | Rail 拓扑 + 前瞻负载均衡，迭代时间缩短 **18-40%** | 低连接度拓扑 + 优化 ≈ 全连接 |

**设计建议**:

```
MoE 训练 GPU 互联的"足够原则":

  Scale-up (域内): NVLink 级别
    8 GPU 全互联即可（不需要 72 GPU）
    带宽: ~1.8 TB/s (NVLink 5 级别) → 足够

  Scale-out (域间): 800Gbps RoCE/IB 级别
    不需要全连接胖树 → Rail 拓扑 + 软件优化
    带宽: 降低 27% 不降吞吐 [Rethinking]

  ⚡ 关键: AlltoAll 路径带宽均匀分布 > 绝对带宽值
```

### 建议 ②：NCCL EP 原生支持——硬件级 Expert Parallel 原语

**证据**: NCCL EP v0.1.0（NVIDIA, June 2026）提供两种 MoE 通信模式:

| 模式 | Token 范围 | 通信方式 | 硬件要求 |
|:-----|:-----------|:---------|:---------|
| **LL (Low Latency)** | 1-128 tokens | 直接 RDMA+NVLink AlltoAll | **低延迟互联**（ns 级延迟） |
| **HT (Hierarchical)** | 4096+ tokens | 分层通信（dom0→跨节点） | **分层互联架构** |

**硬件含义**: GPU 的 NVLink/NVSwitch 必须针对细粒度 AlltoAll 优化——单次仅传输几 KB 数据（而 AllReduce 是 MB 级）。**延迟而非带宽成为首要指标**。

```
MoE 训练 GPU 的互联延迟要求:

  AllReduce 延迟: μs 级 → 够用
  AlltoAll (LL): < 1μs → 🔴 关键瓶颈
  AlltoAll (HT): ~10μs → 🟡 可接受

→ NVSwitch 的 radix 比总带宽更重要
→ 需要硬件级 AlltoAll 加速器（类似 Astera Labs Hypercast 但针对 AlltoAll）
```

### 建议 ③：FoE 路线的硬件支持选项（预防性）

**证据**: FoE（arXiv:2605.23767）通过强制 token-expert affinity + 两层 FFN 局部计算，**彻底消除 AlltoAll**，延迟降低 5.2×。

**两个可能发展方向**:

```
路线 A: AlltoAll 持续存在 → 优化互联（当前行业主流）
路线 B: FoE 可扩展 → AlltoAll 被消除 → 互联要求回归 Dense 级别

🟡 硬件设计应兼容两条路线:
  - 训练 GPU 互联设计不过度"AlltoAll 特化"
  - 保持灵活拓扑，可适配 FoE 的 token-expert 亲和性映射
```

### 建议 ④：Expert Level 的容错硬件支持

**证据**: EEP（arXiv:2604.14557）利用 MoE 的天然容错性——单节点故障后，其余 Expert 自动分担负载，恢复时间 52s vs 348s。

**设计建议**: MoE 场景下 3 个 9 的可靠性足够（EEP 证明 20% 节点故障可容忍），降低可靠性要求 → 降低芯片成本。硬件需支持 Expert 级热插拔/故障隔离，板级设计可更激进（去冗余）。

---

## 六、MoE 推理专用 GPU 设计（arXiv 证据驱动）

### 建议 ①：Attention-FFN 异构核心——专用硬件分解

基于"三元负载分解"（见第四章），建议芯片内按比例配比：

```
MoE 推理专用 GPU——核中核设计:

  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │Attention │  │ Dispatch │  │FFN Expert│
  │ Core     │←→│ Engine   │←→│ Core     │
  │ × N_a    │  │ × 1~2    │  │ × N_f    │
  └────┬─────┘  └────┬─────┘  └────┬─────┘
       │              │              │
  HBM  │      CXL    │      HBM     │
  (KV) │      (route)│      (weight)│
```

| 核心类型 | 优化目标 | 关键指标 | SRAM 配比 | 数量比 |
|:---------|:---------|:---------|:----------|:------|
| **Attention Core** | KV Cache 读取 | 带宽 > 算力 | 小 (128 KB) | 多 (×4) |
| **Dispatch Engine** | 路由延迟 | < 1μs | 极简 | 1-2 个 |
| **FFN Expert Core** | 小 batch MatMul | 算力 > 带宽 | 大 (1 MB+) | 适中 |

### 建议 ②：KV Cache 专属硬件层级——MoE 的"第二内存瓶口"

**证据**:

| 问题 | 论文 | 量化证据 |
|:-----|:-----|:---------|
| MoE 的 KV Cache 膨胀 | qs Inequality (arXiv:2603.08960) | DeepSeek-V3 @ 128k → Dense 吞吐 **4.5×** over MoE |
| 1/W 定律显示 KV 压力 | 1/W Law (arXiv:2603.17280) | MoE tok/W **5.1×** over Dense 但 KV 开销未被计入 |
| PRISM 光子 KV 选择 | PRISM (arXiv:2605.17095) | O(1) 复杂度 KV 块选择 |

**设计建议**:

```
KV Cache 硬件路径（推理专用）:

HBM ──┬── Weight Read ──→ FFN Core
      └── KV Read ──→ KV Cache 专用路径 ──→ Attention Core
                        ↑
               [硬件 KV 量化单元] ← 写回量化 KV
                        ↑
               [片上 KV SRAM 缓存] (1-4 MB)
```

关键设计点:
1. **KV Cache 专用读取口**: 与权重读取物理分离（不同 HBM 通道或不同端口）
2. **硬件 KV 量化管线**: 写入 HBM 前自动 INT4/INT2 量化（去 4× 带宽需求）
3. **片上 KV 缓存**: SRAM 缓存热 KV 块，减少 HBM 访问，可减少 50%+ 的 MoE 推理 KV Cache 带宽瓶颈

### 建议 ③：Expert 预取/缓存硬件——路由预测

**证据**:

| 方法 | 论文 | 效果 |
|:-----|:-----|:------|
| Speculative Expert Prefetch | MoE-SpeQ (arXiv:2511.14102) | 2.34× 加速 over SOTA |
| SD for MoE memory prediction | MoE-SpAc (arXiv:2603.09983) | SD 核心价值是内存模式预测器 |
| Routing-aware kernel scheduling | RaMP (arXiv:2604.26039) | 1.30× over vLLM |

**设计建议**:

```
Expert 路由预测器硬件:

  ┌──────────────────────────────────────┐
  │  Router Predictor (轻量 NN)           │
  │  输入: 当前 token embedding           │
  │  输出: 下 N 步 expert 访问模式        │
  │  硬件: 专用小 MLP (≈ 1M 参数)         │
  └────────────────┬─────────────────────┘
                   ↓  expert_id list
  ┌──────────────────────────────────────┐
  │  Expert Prefetch Engine               │
  │  → 预加载 expert weight 到 SRAM       │
  │  → 预唤醒对应 HBM channel             │
  └──────────────────────────────────────┘
```

**收益预估**: Expert 预取可减少 15-30% 的 HBM 访问延迟（根据路由预测准确率 70-90% 计算）

### 建议 ④：Token 粒度动态功率管理——MoE 的稀疏节能机会

**证据**: PALS（arXiv:2605.21427）证明功率上限作为 MoE 推理的细粒度控制旋钮，能效提升 26.3%。

**设计建议**: MoE 推理时，未激活 expert 对应的核心动态关停（sleep），激活 expert 频率/电压独立调节，Dispatch 阶段低功率、FFN 阶段高功率。**需要核心级独立 DVFS 域**（而非当前的全芯片统一 DVFS），功率响应时间 < 100μs。

---

## 七、qs 不等式对硬件路线的冲击

**⚠️ 最值得关注的矛盾**:

qs 不等式（arXiv:2603.08960, AMD）证明:

```
MoE 推理的双惩罚:
  惩罚 ①: Expert 路由碎片化 minibatch → 降低 weight reuse
  惩罚 ②: 大量 resident expert 占 HBM → 挤压 KV Cache

结果: 质量匹配的 Dense 模型，吞吐比 MoE 高 4.5×
```

如果这是成立的 → MoE 应被视为"训练优化"而非"推理优化"方案。这对硬件设计路线的冲击:

```
路线一（当前主流）: MoE 是长期趋势 → 优化 MoE 推理硬件
  - 需 Expert 预取、KV 路径分离、PD 分离
  - 投入大，如果 qs 正确则可能白费

路线二（qs 不等式建议）: MoE → 训练，蒸馏 → Dense 部署
  - 推理硬件回归 Dense 优化
  - AlltoAll 互联投入降低
  - 更关注 HBM 带宽和 KV Cache

🟡 建议: 现阶段设计应兼容两条路线
  - GPU 互联不过度 AlltoAll 特化
  - 保留 Dense 推理的"全矩阵"算力优势
  - 关注 KV Cache 路径（两条路线都需要）
  - 关注小 batch MatMul 效率（两条路线都需要）
  - 聚焦"带宽和延迟"而非"特定通信模式"
```

---

## 八、综合设计决策矩阵

| 设计决策 | Dense 训练 | Dense 推理 | MoE 训练 | MoE 推理 |
|:---------|:-----------|:-----------|:---------|:---------|
| **Tensor Core 密度** | 🔴 极高 | 🟢 中 | 🔴 极高 | 🟡 中-高 |
| **互联重点** | AllReduce 带宽 | 延迟（KV） | ⭐ **AlltoAll 延迟** | ⭐ **AlltoAll 均匀性** |
| **HBM 带宽优先** | 🟢 足够 | 🔴 极端优先 | 🟢 足够 | 🔴 **极端优先** |
| **HBM 容量优先** | 🟢 大 | 🔴 越大越好 | 🔴 更大（expert 池） | 🔴 **极大（expert+KV）** |
| **SRAM 容量** | 🔴 越大越好 | 🟡 中等 | 🔴 越大越好 | 🔴 **Expert 缓存预取** |
| **KV 量化硬件** | 🟢 可选 | 🔴 必需 | 🟢 可选 | 🔴 **必需+更激进** |
| **FP4 原生支持** | 🟢 可选 | 🔴 必需 | 🟢 可选 | 🔴 必需 |
| **低功耗模式** | 🟢 不关心 | 🔴 必需 | 🟢 不关心 | 🔴 **核心级 DVFS** |
| **小 batch MatMul** | 🟢 不关心 | 🔴 优化 | 🟢 不关心 | 🔴 **极端优化**（Expert 小 batch） |
| **路由硬件支持** | 🟢 不需要 | 🟢 不需要 | 🟡 **NCCL EP 加速** | 🔴 **Expert 预测+预取** |
| **容错需求** | 5 个 9 | 4 个 9 | **3 个 9（EEP）** | 4 个 9 |

---

## 九、最终建议清单（优先级排序）

### 🔴 P0：必须做（否则 MoE 推理效率极低）

1. **KV Cache 专用硬件路径** — 物理分离权重和 KV 读取带宽，硬件量化
2. **小 batch MatMul 优化** — Expert FFN 内 batch 仅 1-64 tokens，需特化 Tensor Core 模式
3. **Expert 预取（预测性）** — 路由预测 → 预加载 expert weight

### 🟡 P1：强烈推荐（MoE 训练效率提升 20-50%）

4. **AlltoAll 延迟优化** — NVSwitch radix 提升，而非总带宽提升
5. **NCCL EP 硬件原语** — 支持 LL 模式的 ns 级 AlltoAll
6. **分层互联拓扑** — 域内全互联 + 域间 Rail 拓扑

### 🟢 P2：具备前瞻性（应对路线不确定性）

7. **核心级 DVFS** — 支持 Expert 粒度的功率管理，能效提升可达 26.3%（PALS）
8. **FoE 兼容性** — 互联拓扑支持 token-expert 亲和性映射
9. **支持 Dense ↔ MoE 双模式** — 不将任何一条路线堵死

---

## 附：关键引用论文清单

| # | 论文 | 链接 | 核心贡献 |
|:-:|:-----|:-----|:---------|
| 1 | DODOCO | arXiv:2605.20982 | MoE 路由不均 = 架构固有属性，Gini 0.105-0.38 |
| 2 | qs Inequality | arXiv:2603.08960 | 质量匹配 Dense 比 MoE 吞吐高 4.5× |
| 3 | Rethinking Topologies | arXiv:2605.00254 | 3D full-mesh Pareto 最优，降 27% 带宽不降吞吐 |
| 4 | NIMBLE | arXiv:2604.00317 | MoE AlltoAll 5.2× over NCCL |
| 5 | RailS | arXiv:2605.22990 | Rail 拓扑 + 前瞻负载均衡，18-40% 缩短 |
| 6 | FoE | arXiv:2605.23767 | 消除 AlltoAll，延迟降低 5.2× |
| 7 | EEP | arXiv:2604.14557 | MoE 天然容错，52s vs 348s 恢复 |
| 8 | AFD | arXiv:2605.28302 | MoE 推理三元负载分解 |
| 9 | PRISM | arXiv:2605.17095 | O(1) 光子 KV 块选择 |
| 10 | MoE-SpeQ | arXiv:2511.14102 | Expert 投机预取 2.34× |
| 11 | MoE-SpAc | arXiv:2603.09983 | SD 作为 MoE 内存预测器 |
| 12 | RaMP | arXiv:2604.26039 | 路由感知调度 1.30× |
| 13 | PALS | arXiv:2605.21427 | 功率上限 → 能效 26.3% |
| 14 | 1/W Law | arXiv:2603.17280 | MoE tok/W 5.1× Dense 但 KV 未计 |
| 15 | NCCL EP v0.1.0 | NVIDIA GitHub (Jun 2026) | MoE 通信官方原生支持 |
| 16 | NCCL v2.30.7-1 | NVIDIA (Jun 2026) | Zero-SM Collectives, GPI backend |
| 17 | PALS MoE DVFS | arXiv:2605.21427 | 核心级 DVFS 26.3% 能效提升 |

---

> **关联文档**: [`gpu-ai-chips.md`](gpu-ai-chips.md)（竞争格局）· [`moe-hardware-impact.md`](moe-hardware-impact.md)（MoE 硬件影响跟踪）· [`server-form-factor.md`](server-form-factor.md)（服务器形态）· `server-hardware/`（硬件架构详情）
> **最后更新**: 2026-06-10
