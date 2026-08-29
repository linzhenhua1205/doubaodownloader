# 异构与能效双深潜：MFU 功耗代理 × HeteroPanacea 四路推理分解

> **概要**: 双论文深潜——MFU 功耗代理（训练功耗可软件定义预测）与 HeteroPanacea（推理四路分解仿真），共同指向能效建模从「事后测量」走向「事前软件定义仿真」，并给出「分解何时付钱」的量化判据。
>
> **关键词**: MFU 功耗代理 · HeteroPanacea · 推理分解 · 能效仿真 · 软件定义功耗

> **归档**: 2026-08-07 · 深度分析第 17 篇（今日）
> **素材**: 两篇 arXiv HTML 全文一手（2608.03880 全量 802 行 + 2608.03741 全量 1861 行，含 Table I-VII 精确数据）

## 📑 目录

- [统一主线](#统一主线)
- [一、MFU 功耗代理：软件定义功耗预测器](#一mfu-功耗代理软件定义功耗预测器)
- [二、HeteroPanacea：四路分解三维仿真](#二heteropanacea四路分解三维仿真)
- [三、两篇联合洞察](#三两篇联合洞察)
- [四、批判性审视](#四批判性审视)
- [五、对超节点与服务器研发的启示](#五对超节点与服务器研发的启示)
- [六、可证伪预测 P1-P5](#六可证伪预测-p1-p5)
- [参考文件](#参考文件)
- [Changelog](#changelog)

## 统一主线

两条信号表面无关（一个是训练功耗预测、一个是推理架构探索），实际指向**同一个产业趋势：能效与性能建模从「事后测量」走向「事前软件定义仿真」**。

| 维度 | MFU 功耗代理（2608.03880） | HeteroPanacea（2608.03741） |
|:--|:--|:--|
| 建模对象 | 训练功耗（compute-bound） | 推理吞吐（prefill + decode 全谱） |
| 核心问题 | MFU 能否作便携软件定义功耗预测器？ | 阶段分解何时值得付钱？ |
| 方法 | 实证：~3000 runs × 6 GPU 线性回归 | 仿真：roofline + 事件驱动 + 设计空间搜索 |
| 关键结果 | per-(GPU,dtype,batch) 拟合 MAPE ~10%→~1% 触噪声底 | PD 分解 +75% 吞吐；4-way PDAF 跨模型最一致（特化硬件下） |
| 覆盖盲区 | memory-bound decode 明确排除 | roofline 的 max(Φ/F, β/B) 恰恰覆盖 decode |
| 共享哲学 | 模型类跨厂商可迁移、参数需 per-device 一次性校准 | 设备参数化 = 每组峰值规格 + roofline，探索可复现 |

**互补性**：MFU 模型的盲区（memory-bound decode）正是 HeteroPanacea 建模的核心（decode-attention 是 KV 带宽主导）。两篇合起来 = **训练 + 推理全谱的软件定义能效建模**。

---

## 一、MFU 功耗代理：软件定义功耗预测器

> **来源**: Enskat & Wiesner, "Evaluating MFU as a Proxy for GPU Power for Energy-Aware Simulation of LLM Training", arXiv:2608.03880v1 (cs.PF, 2026-08-04), MASCOTS'26
> **开源**: github.com/dos-group/gpu_power_benchmark

### 1.1 问题：仿真器的功耗空洞

高保真性能模拟器（Vidur/SimuMax/LLM Cluster Simulator）是 AI 系统设计的主要工具，但**现有功率模型依赖硬件利用率计数器——计数器在真实硬件上跑过之前不存在**，仿真阶段根本读不到。且这些计数器厂商特定（NVML vs ROCm），跨厂商/跨代不可移植。

MFU（Model FLOPs Utilization）是纯解析指标：`MFU = Tokens/s × C_req / FLOPS_peak`，由模型结构与吞吐直接算出，**仿真器无需硬件即可计算**。本文首次系统验证 MFU 能否作为 GPU 功耗的便携代理。

### 1.2 实验设计：~3000 runs 交叉扫描

- **6 GPU、2 厂商、4 档**：NVIDIA A100 / L40 / L4 / Quadro RTX 5000 / RTX 4070 Ti + AMD MI210
- **3 模型族**（按 GPU 档位匹配）：Qwen2.5、GPT-2、DialoGPT（commodity 0.5B/124M；mid 1.5B/XL；large 3B/XL）
- **3 精度**（fp32/fp16/bf16，Quadro 无 bf16 硬件）× **7 batch**（1-128）× **2 context**（512/2048）
- 交叉积 = 每 GPU 126 配置（Quadro 84），**每配置重复 4 次**，遥测采样至统计收敛（95% CI 半宽 ≤5% 均值，最小 50 样本上限 500）
- 工作负载 = 完整训练步（fwd+bwd+AdamW），eager attention（禁 flash/SDPA），CalFLOPS 算 C_req，NVML/ROCm 为基准功率信号

**Table I：峰值 FLOPS（MFU 归一化基准，厂商 datasheet）**

| GPU | Mem(GB) | FP32 | FP16 | BF16 (TFLOPS) |
|:--|:--:|:--:|:--:|:--:|
| A100 | 80 | 156 | 312 | 312 |
| L40 | 48 | 90.5 | 181.05 | 181.05 |
| L4 | 24 | 30.3 | 121 | 121 |
| Quadro 5000 | 16 | 89.2 | 89.2 | — |
| RTX 4070 Ti | 12 | 40.1 | 80.2 | 80.2 |
| MI210 | 64 | 181 | 181 | 181 |

### 1.3 核心结果

**发现 1：线性 MFU-power 模型拟合每个 GPU（含 AMD MI210）**

| GPU | MFU R² | MAPE | GPU Util R² |
|:--|:--:|:--:|:--:|
| A100 | 0.74±0.03 | 11.0±0.7% | 0.87 |
| L40 | 0.80±0.03 | 7.8±0.5% | 0.82 |
| L4 | 0.37±0.03 | 3.5±0.5% | 0.17 |
| Quadro 5000 | 0.84±0.02 | 12.5±1.4% | 0.85 |
| RTX 4070 Ti | 0.68±0.06 | 12.5±1.1% | 0.67 |
| MI210 | 0.77±0.05 | 13.7±0.9% | —（binary）|

- **MI210 的 GPU Utilization 是二值活动标志**（ROCm 从 GRBM_COUNT 读，持续负载下钉死 100%），根本无线性拟合可言——**MFU 是两者中唯一在所有设备上可拟合的预测器**
- 训练级 NVIDIA 卡上 R² 68-84%，L4 掉到 37%（低功率范围所致），但 L4 的 MAPE 反而全队最低（3.5%）
- **斜率 1.21 W/%（MI210）到 4.49（A100），3.7× spread 镜像峰值 FLOPS spread**：因为 MFU 按峰值归一化，相同 MFU 在不同芯片对应不同原始算力，而功耗随原始算力走

**发现 2：固定 (dtype, batch) 后 MFU 解释 ~98% 功率方差**：MI210 中位 R²=0.997（21 cells），NVIDIA 0.89-0.98。

**发现 3（核心）：按 (GPU, dtype, batch) 条件化拟合，MAPE ~10%→~1% 触达噪声底**

Table III（残差 SD，占平均功率百分比）：

| GPU | per-GPU | per-cell | 重复噪声底 |
|:--|:--:|:--:|:--:|
| A100 | 12.50% | 2.13% | 1.08% |
| L40 | 9.02% | 1.29% | 0.35% |
| L4 | 4.46% | 1.00% | 0.71% |
| Quadro 5000 | 12.81% | 1.95% | 1.23% |
| RTX 4070 Ti | 16.46% | 2.21% | 1.66% |
| MI210 | 17.81% | 2.87% | 0.20% |

- 条件化把 per-GPU 残差削减 4-7×，且**每张 NVIDIA 卡的 cell 残差在噪声底 1.3-3.7× 之内**（4070 Ti 与 L4 统计上不可区分）
- **in-sample 剩余误差由采样噪声主导而非模型误设**——cell 内没有留给更复杂预测器的空间

**发现 4：memory-bound 边界（batch-1）MFU 严重低估功耗**

Table IV（batch-1 vs batch-128）：

| GPU | MFU₁ | MFU₁₂₈ | P₁(W) | P₁₂₈(W) |
|:--|:--:|:--:|:--:|:--:|
| A100 | 0.4% | 28.1% | 189 | 307 |
| L40 | 0.4% | 31.8% | 200 | 315 |
| L4 | 0.5% | 22.3% | 63 | 70 |
| Quadro 5000 | 0.8% | 35.5% | 111 | 201 |
| RTX 4070 Ti | 0.3% | 14.9% | 97 | 169 |
| MI210 | 1.2% | 44.3% | 72 | 148 |

- MFU 从 batch-1 到 128 增长 36-72×，**功率只变 1.1-2.0×**
- batch-1 时所有设备 MFU <1.3%，却仍拉 49-64% 的 batch-128 功率（L4 达 90%，idle floor 主导）
- 单斜率外推会向下穿越该区域，数据中心卡上产生 **70-120W 绝对误差**

**实用配方**：per-(GPU, dtype, batch) 三轴条件化、且只这三轴（context 512 vs 2048 无影响）；新加速器只需一次性 per-GPU 校准 sweep。

---

## 二、HeteroPanacea：四路分解三维仿真

> **来源**: Forys, Wu, Xiao, Nie, Liu, Antonova, Jones, Mullins, Luk, Zhao, Constantinides (Imperial College London + Cambridge), "When Does Disaggregation Pay? Simulating Prefill–Decode–Attention–FFN Specialization for Agentic LLM Inference", arXiv:2608.03741v1 (cs.DC, 2026-08-04)
> **开源**: 接收后全量开放（simulator + configs + scripts）

### 2.1 动机：agentic 推理的架构错配在扩大

- OSWorld 上 agentic 会话平均 **38K tokens、可达 100K**，超标准聊天一个数量级以上——每轮工具调用都在重新 prefill 不断增长的 context
- 同功率预算同请求率下，PD 分解在 agentic 负载上给 **1.82×** 吞吐提升，标准聊天只有 1.29×（图 1b）——架构错配随 context 增长而扩大
- 行业已转向异构分解：Vera Rubin = Rubin GPU（prefill + decode-attention）+ Groq LPU（decode-FFN）
- 但**每个分解阶段的最优硬件长什么样无人系统回答**——因为适合 prefill 的 NPU 架构与适合 decode-FFN 的可以截然不同

### 2.2 框架：三维仿真 + 四路 PDAF

**PDAF 四路分解**（本文核心贡献）：Prefill × Decode × Attention × FFN → 四个独立阶段（PA/PF/DA/DF），每阶段可独立配硬件、并行度、精度。PDAF **包住两种粗粒度方案**：合并 P/D 内 A/F = PD；合并 A/F 内 P/D = AF。

**Table I：与现有仿真框架对比（HeteroPanacea 唯一五维全占）**

| 框架 | 异构 | PD 分解 | AF 分解 | 分解量化 | 并行度 | 搜索 |
|:--|:--:|:--:|:--:|:--:|:--:|:--:|
| LLMCompass | ✗ | ✗ | ✗ | ✗ | DP | ✓ |
| MemExplorer | ✓ | ✓ | ✓ | ✗ | TP/DP/PP/EP | ✗ |
| DistServe | ✗ | ✓ | ✗ | ✗ | TP/DP/PP | ✓ |
| LLMServingSim2.0 | ✓ | ✓ | ✓ | ✗ | TP/DP/PP/EP | ✗ |
| **HeteroPanacea** | ✓ | ✓ | ✓ | ✓ | TP/DP/PP/EP | ✓ |

**设备模型（roofline）**：每加速器 = 峰值算力 F + 内存技术类 + (容量 C, 带宽 B) 点，执行时间 `t = max(Φ/F_eff, β/B_eff)`。功率 `P = P_compute + P_mem`：P_compute 亚线性幂律 `P_ref·(F/F_ref)^α`（锚定 H100 datasheet，α 拟合三代真实加速器 TDP）；P_mem 物理动态+泄漏（借鉴 MemExplorer）。

**Table II：设备设计空间**——TFLOPS 25/100/250/2500/10000/20000；内存 SRAM/HBM/DDR/LPDDR/GDDR 各 2-5 个代表性 (容量, 带宽) 点（HBM 16GB/1TB/s 到 190GB/8TB/s）。

**互连双带宽域**：D2D intra-node（TP/EP 集合 + PP 激活交接）+ N2N inter-node（跨分解边界的 KV/激活传输）——**分解的代价显式建模为跨池传输**。

**验证（8×B200 实测）**：Table III TP/PP 8 GPU 延迟 sim/real 0.79-1.06×；Table IV 通信原语 0.82-1.21×（PP point-to-point 与 EP all-to-all 均在 0.82-1.21× 内）。

### 2.3 搜索：量化 + 硬件两级流水

- **量化搜索（经验式）**：每阶段独立 MXINT 位宽（4/8/16），MASE 量化 pass + **PhaseAutoSwitch hook**（按序列长度 L>1 → prefill 配置，L=1 → decode 配置，运行时切换）；只接受无精度损失的量化
- **硬件/并行搜索（解析式）**：Phase 1 按 roofline 算容量分 `σ = d·tput(B)/Λ_s` 解析排名（不仿真）；Phase 2 功率预算跨 k 阶段分配，瓶颈联合质量 `σ_joint = min σ_i`，仅 top-K 端到端仿真
- 两级合成：量化定 q* → 硬件搜索以 q* 的 dtype_bytes 找吞吐最优配置

### 2.4 评估结果（8 模型 × 5 个数量级 I/O 比）

**NPU 设计空间（功率预算）**：

| I/O 比 | 结论 |
|:--|:--|
| 0.01 / 1（decode 主导/均衡） | **ND 最强**：PD/AF/PDAF 全低于 1.00×（PD 最接近 0.89×）——分解开销超过收益 |
| 10（跃变 decade） | PDAF 均值从 0.48× 跳到 **2.10×**（图 5，非单调，后 plateau 1.5-1.8×） |
| 100（prefill 主导） | PDAF 8/8 模型超 ND（1.05-1.92×），PD 7/8，**AF 从不超 ND（0.20-0.65×）** |
| 1000 | 掉回 1.27×——prefill 太大，decode 池不再是瓶颈，特化硬件闲置 |

- **PDAF 在 6/8 模型上是最优模式**（Llama4-Maverick 1.81×、Scout 1.77×）——「4-way 全分解跨模型最一致」
- **PD 分解 +75% 吞吐**：对应 figure 1b 的 agentic 1.82×（用户概括口径）

**GPU 目录（AWS 实例，小时成本预算）**：

- crossover 更早：I/O=0.01 时 PD 8/8 超 ND（1.18-2.50×）——但这是**成本预算下用更便宜实例堆量**的结果
- 不一致性放大：I/O=1 时 PD 只 4/8（0.01× 到 2.64× 极端分散）
- **关键反转：I/O=100 时 PD ≥ PDAF 在 6/8 模型上**——四路拆分在 GPU 上不付钱

**Table V 解释分歧（per-stage 硬件分配）**：

- NPU 搜索：decode 阶段抢占最高容量/带宽档（HBM 190GB/8.0TB/s）但在计算两端——**decode-attention 拿最低算力 25-250 TFLOPS，decode-FFN 拿 2.5k**；prefill 拿最高算力 20k TFLOPS 最小容量——**内存与算力独立移动**
- GPU 目录：31/32 分配是 H100（剩一个 A100）——**GPU 把算力与带宽绑死，每阶段得到相同 compute-to-bandwidth 比，搜索无自由度**；拆分 AF 只在能给两者真正不同硬件时才有意义

### 2.5 模型架构消融（Table VI，三个 MoE 基线 × 5 因子）

- **Finding 1：PDAF 收益单调随 decode-attention KV 流量**——kv_lora_rank 128→4096：GPT-OSS +100%（0.93×→1.85×）、GLM-4.6 +147%、DS-V4-Flash +67%。rank 小时 KV 项小、DA 变成 weight-read 主导、与 DF 结构不可分 → PDAF 无收益甚至负（0.81×）——**DA 与 DF 的硬件需求分歧正是四路拆分要变现的东西**
- **Finding 2：容量增长几乎免费**——num_experts 4× 只移动 GLM +3%、DS-Flash <0.5%（FLOPs 与 weight-bytes 只依赖 active experts）
- **Finding 3：只有 active-compute 增长压垮 PDAF**——num_active_experts 4×：DS-Flash -69%、GLM -17%；8×：DS-Flash -73%、GLM -60%；GPT-OSS 免疫（基线 active-expert 数最低）
- **Finding 4：低精度非均匀有益**——dtype_bytes 4→0.5：GPT-OSS +57% 但 GLM -41%、DS-Flash -42%（低于 ND 基线）——精度缩窄同时抬高四阶段算术强度，收益取决于 DA/DF 间隙是变宽还是变窄

### 2.6 量化敏感度（Table VII，Qwen3.5-32B，BFCL + GSM8K）

| 配置 | BFCL | GSM8K |
|:--|:--:|:--:|
| baseline | 18% | 78% |
| 8/8/8/8 | 21% | 75% |
| 4/4/4/4 | 6% | 11% |
| 8/4/8/8（FFN-prefill 降 4bit） | 20% | **47%** |
| 8/8/4/8（attn-prefill 降 4bit） | **11%** | 79% |
| 4/8/8/8（attn-prefill） | **12%** | 80% |
| 8/8/8/4（FFN-decode 降 4bit） | 20% | **15%** |

- 全局 4bit 双任务崩（11%/6%）
- **FFN 降 4bit 伤 GSM8K 保 BFCL；attention 降 4bit 伤 BFCL 保 GSM8K**——「哪个阶段耐低精度是工作负载属性而非模型属性」，单一全局精度必牺牲其一
- 作者自述：单模型双任务无重复 runs，方向性结论非标定幅度

### 2.7 结论与限制

- 特化硬件下 PD 与 PDAF 均受益，agentic 上最高 **2.06×**；但**收益条件性**：只有 prefill-heavy 才过 parity；四路拆分只在硬件设计空间足够丰富时胜过 PD
- 限制：验证是组件级非端到端（调度/批处理未验证）；量化单模型；GPU 实验依赖单一云定价；未与真实分解系统对比；开源在接收后

---

## 三、两篇联合洞察

1. **同构的建模哲学**：MFU「模型类可迁移、参数需 per-device 一次性校准」↔ HeteroPanacea「设备 = 峰值规格 + roofline、设计空间可探索」——**都放弃「一个模型拟合所有硬件」的幻想，接受「类可迁移 + 实例需标定」的工程现实**。这降低国产加速器入场的建模门槛：新 NPU 只需一次性校准/参数化。

2. **覆盖互补 = 训练+推理全谱**：MFU 明确限定 compute-bound（训练、prefill）；HeteroPanacea 的 roofline max(Φ/F, β/B) 恰恰显式处理 decode 的 memory-bound。**MFU 的盲区就是 HeteroPanacea 的主场**——两者拼接即「训练能耗可预测、推理架构可探索」的完整软件定义能效栈。

3. **「分解何时付钱」有量化判据了**：I/O 比跃变（1→10 之间，PDAF 0.48×→2.10×）、decode-attention KV 强度单调驱动、active-compute 是唯一压垮因子——**这些是可直接进设计评审的判据**，而非直觉。

4. **硬件自由度决定分解粒度**：GPU 上 PDAF ≤ PD（31/32 都是 H100），NPU 上 PDAF 最优——**「给不同阶段真正不同的硬件」是四路拆分成立的前提**。这对超节点 scale-up 域设计（NVLink/UALink 域内异构）是直接的架构决策输入。

5. **功耗建模统一框架萌芽**：MFU 的斜率 spread 与 HeteroPanacea 的亚线性 P_compute∝F^α 共享同一物理直觉（功耗随算力亚线性增长）——异构集群的功耗预算分配可用统一幂律描述。

---

## 四、批判性审视

**MFU 功耗代理**：

1. **范围限定比标题窄**：只在 compute-bound 训练验证，**decode 推理明确排除**（memory-bound）——而推理才是当前功耗大头；「软件定义功耗预测器」的泛化被显著限定
2. **单设备无通信**：fit 不含 collectives/流水线气泡/FSDP all-gather 功耗；集群模拟器组合精度未验证（作者承认「组合估计的精度有待建立」）
3. **eager attention ≠ 生产栈**：禁 flash/SDPA 以隔离 kernel 实现差异；fused kernels 会改变 MFU 与算术强度，「斜率变化被校准吸收」是假设未验证
4. **~1% 是 in-sample**：论文明确承认；跨配置泛化（未见过的 batch/dtype）回到 ~10% 级——「1%」不能当生产精度宣传
5. **设备代表性**：无 H100/B200/GB200（A100 是上一代数据中心卡）；L4 是「部分例外」、4070 Ti 工作站环境最差——「every GPU」声明需要更多新代数据点
6. **方法学亮点要肯定**：噪声底对照（Table III）与附录 A 外部功率验证（R²>0.99）是少见的严谨设计

**HeteroPanacea**：

1. **组件验证 ≠ 端到端**：明确承认调度/批处理未验证——而分解收益恰恰来自调度交互，这是最大的置信度缺口
2. **NPU 设计空间是合成的**：20k TFLOPS、8TB/s HBM 是设计假设（PLENA 基线），无真实芯片对应；「PDAF 最一致」依赖「空间足够丰富」这一可操纵前提
3. **GPU 实验单一定价**：AWS 定价漂移结论可能漂移；GPU 目录无最新（无 B200/H200/H100 NVLink 域）
4. **量化研究单薄**：单模型双任务无重复 runs；且 8-bit baseline 本身已掉点（BFCL 18%→21% 是噪声内）
5. **MoE 量化搜索因成本未跑**：量化 × 异构的联合最优未验证（全精度 sweep 代替）
6. **不可复现**：开源在接收后；未与真实分解系统（DistServe/Splitwise 部署）对比——「+75%/2.06×」是仿真内数字
7. **无调度细节披露**：continuous batching 参数、KV 容量约束、超时策略的具体值未见——事件驱动仿真对参数敏感

---

## 五、对超节点与服务器研发的启示

1. **训练模拟器能量感知闭环**：MFU 功耗代理（per-GPU 校准 + per-cell 条件化）可直接嵌入训练模拟器——Vidur 已输出 MFU，接上功耗模型即能量感知调度/设计空间探索（论文正指向此）；**自研/国产集群模拟器可直接复用 dos-group 开源基准**

2. **推理异构架构设计判据**：PDAF 给出「何时分解付钱」的量化边界（I/O 比跃变 1→10；DA KV 强度单调驱动）——**国产异构 NPU 推理服务器（对标 Vera Rubin）可用此框架在流片前筛阶段特化方向**

3. **阶段特化 NPU 参数直接可用**：decode-attention = 高带宽（190GB/8TB/s 档）低算力（25-250 TFLOPS）；decode-FFN = 高算力（2.5k）+ 高容量；prefill = 最高算力（20k）+ 最小容量——**这组分配是 NPU 设计空间的锚点**

4. **GPU 集群上别过度拆分**：商业 GPU 目录下 PDAF ≤ PD——**现有 GPU 集群做 PD 分解足够，AF/PDAF 的硬件前提（解耦算力与带宽）在 GPU 上不存在**；这解释了为何 industry 的 Vera Rubin 用「GPU+LPU 异构」而非「纯 GPU 四路」

5. **功耗建模统一入口**：MFU 线性模型（训练）+ HeteroPanacea 亚线性幂律（异构探索）可统一进超节点功耗预算工具——电源正成为集群第一瓶颈（见今日电源专题），**事前功耗预测的价值在提升**

---

## 六、可证伪预测 P1-P5

- **P1**：12 个月内至少一个主流 LLM 训练模拟器（Vidur/SimuMax/LLM Cluster Simulator）集成 per-(GPU,dtype,batch) MFU 功耗模型作为默认能量报告（2027-08 核验）
- **P2**：若以 B200/H100 复现 MFU 研究，per-cell MAPE 仍 ≤2%（线性+条件化结构跨代成立），但 per-GPU 斜率 spread 收窄（峰值 FLOPS 归一化后 <3.7×）（2027-08 核验）
- **P3**：12 个月内出现 DA/DF 阶段专用加速器的商业发布或正式 roadmap（Vera Rubin 的 Groq LPU 是 DF 特化先例，国产厂商跟进 PD 分解 + AF 探索）（2027-08 核验）
- **P4**：HeteroPanacea 开源后，独立复现将确认「NPU 空间 PDAF>PD 依赖算力/带宽解耦自由度」；GPU 目录复现得到 PDAF≤PD 一致结论（2027-08 核验）
- **P5**：24 个月内至少一家云厂商公开披露 prefill-heavy agentic 流量上的 PD 分解吞吐收益 ≥1.5×，「I/O 比跃变」进入行业公开叙事（2028-08 核验）

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- [GPU 经济学十年演化](./2026-08-13-gpu-economics-decade-deep-analysis.md) — 同为算力能效经济性分析，与本文件功耗建模互为交叉验证
- [APAC 主权算力功率经济学](./2026-08-07-apac-sovereign-compute-power-economics.md) — 算力供给侧功率经济学，与 MFU 功耗代理的「事前功耗预测」互补

### 外部资料引用

- 来源: Enskat & Wiesner, "Evaluating MFU as a Proxy for GPU Power for Energy-Aware Simulation of LLM Training", arXiv:2608.03880v1, 2026-08-04. https://arxiv.org/abs/2608.03880
- 来源: Forys et al., "When Does Disaggregation Pay? Simulating Prefill–Decode–Attention–FFN Specialization for Agentic LLM Inference", arXiv:2608.03741v1, 2026-08-04. https://arxiv.org/abs/2608.03741
- 来源: dos-group/gpu_power_benchmark, https://github.com/dos-group/gpu_power_benchmark

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-08-07 | v1.0 | 双论文全文深潜（MFU 功耗代理 + HeteroPanacea），归档 04_ai/ |
| 2026-08-22 | v1.1 | 提升：补齐 std-002 五元素 + 跨文件交叉链接与一致性勘误 |
