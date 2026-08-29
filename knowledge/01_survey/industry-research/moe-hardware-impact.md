# 🔬 MoE→硬件影响 — 研究跟踪汇总

> **频率**: 双周更新 EN  
> **最后更新**: 2026-07-31  
> **维护方式**: 本文件为索引汇总，完整条目写入每日调研文件

---

## 📋 溯源卡片

| 模块 | 起始文件 | 创建日期 | 说明 |
|:----|:---------|:--------:|:-----|
| MoE→Hardware §1 | `2026-06-28.md` §3 | 2026-06-28 | 首批22条研究，含UltraEP/DFlash/JetSpec/DeepSeek-V4等 |
| MoE→Hardware §2 | `2026-06-30.md` §8 | 2026-06-30 | CuTe DSL/DeepSeek-V4/JetSpec再分析 |
| MoE→Hardware §3 | `2026-07-02.md` §8 | 2026-07-02 | CuTe DSL/Moebius/qs不等式 |
| MoE→Hardware §4 | `2026-07-03.md` §8 | 2026-07-03 | FlexMoE/ASAP/Wide-EP |
| MoE→Hardware §5 | `2026-07-07.md` §8 | 2026-07-07 | Blackwell 2.8× / MoP 4.7-8.2× / ELDR 5.9-13.9% |
| MoE→Hardware §6 | `2026-07-08.md` §8 | 2026-07-08 | BrownoutMoE 2.24× / DODOCO routing固有性 / NASiC 4-114.8× |
| MoE→Hardware §7 | `2026-07-09.md` §8 | 2026-07-09 | **本期新增3条**: UBEP 52.4% A2A延迟降 / DFlash 15× Blackwell / CrossPool 10.4× TBT |
| MoE→Hardware §8 | `2026-07-11.md` §8 | 2026-07-11 | **本期新增7条**: ASAP 90% prefill吞吐 / Moebius运行时TP/EP切换 / UltraEP 94.3%均衡 / EVICT 2.35× SD / Fusion Kernels 8%端到端 / Dynamo+NVL72 6× / SP-MoE 3.5× offload |
| MoE→Hardware §9 | `2026-07-12.md` §8 | 2026-07-12 | **本期新增6条**: SmallEP 1,800 tok/s本地推理 / DySHARP 1.79× in-switch加速 / Sieve 1.3-1.6× PIM加速 / ELMoE-3D 6.6× 3D堆叠加速 / EEP 11s宽EP故障恢复 / MoE-Prefill 1.37× AsyncEP |
| MoE→Hardware §10 | `2026-07-13.md` §10 | 2026-07-12 | **本期新增6条**: TriRoute 联合三层路由 / FoE 5.2×消除All-to-All / WiSP 1.95×工作集管理 / Tiara 1.88× NIC可编程加速 / NVIDIA HW设计准则 / ISCA'26推理缩放律 |
| MoE→Hardware §11 | `2026-07-14.md` §11 | 2026-07-14 | **本期新增6条**: BrownoutMoE 2.24× expert分组 / MAESTRO 10.61% 跨层剪枝 / ELDR 5.9-13.9%局部路由 / Gimbal 42.9% TTFT降 / MoE-on-Edge纠偏 / DeLS-Spec模块化SD |
| MoE→Hardware §12 | `2026-07-15.md` §12 | 2026-07-15 | **本期新增6条**: Director 11-55%预测放置 / MoP 4.7-8.2×混合并行 / UFP4挑战E2M1 / FlexMoE 99.8%@50%通道剪枝 / GeMoE 36.5%自适应稀疏 / dMoE 69.5→14.6扩散路由 |
| MoE→Hardware §13 | `2026-07-16.md` §13 | 2026-07-16 | **本期新增4条**: MoE-Spec 10-30% SD expert budgeting / DES 55% expert共享降38%延迟 / ZipMoE 72.77%延迟·6.76×边缘吞吐 / MoE-DisCo 47.6-69.5%低成本训练 |
| MoE→Hardware §14 | `2026-07-17.md` §14 | 2026-07-17 | **本期新增6条**: EcoSpec 1.62× cost-aware SD / NVIDIA HW设计7准则 / TriRoute 三轴联合路由 / MoE-nD 14× per-layer KV压缩 / Irminsul 83%内容寻址cache / Var-Width 22% FLOP↓15% KV↓ |
| MoE→Hardware §15 | `2026-07-18.md` §15 | 2026-07-18 | **本期新增6条**: D-cut 3.0× batch-aware SD / HTX-301 $19k decode芯片 / HyperParallel-MoE 1.58× NPU异构调度 / NanoCP 1.88-3.27× dynamic CP / FluxMoE 3.0× expert paging / MACS模态感知EP均衡 |
| MoE→Hardware §16 | `2026-07-19.md` §16 | 2026-07-19 | **本期新增6条**: SonicMoE 1.86× IO/tile-aware / NCCL EP统一API / FEPLB Copy Engine免费均衡 / NIMBLE 5.2×多路径All-to-All / Mozart 3.5D Chiplet / FoMoE联邦训练 |
| MoE→Hardware §17 | `2026-07-20.md` §17 | 2026-07-20 | **本期新增6条**: FarSkip-Collective架构级通信解耦 / DisagMoE attention-FFN解耦训练 1.8× / MoEBlaze 4×破内存墙 / LAER-MoE FSEP 1.69× / Multi-Head LatentMoE O(1)通信 / TaxBreak 8-11× kernel dispatch & CPU瓶颈 |
| MoE→Hardware §18 | `2026-07-21.md` §18 | 2026-07-21 | **本期新增6条**: WiSP 1.95× MV-WSA KV-expert VRAM分配 / MoE on Edge 31%落后/2.1×能耗实证证伪 / PROBE 1.32× prefill+1.26× decode共均衡 / Piper 2-3.5× MFU A2A 1.2-9× / MixServe 1.08-3.80× TTFT融合AR-A2A / RepetitionCurse 3.063× DoS攻击向量 ICML'26 |
| MoE→Hardware §19 | `2026-07-22.md` §19 | 2026-07-22 | **本期新增6条**: PagedWeight 72%内存节省·1.94×吞吐动态量化 / LLEP 5×加速·4×内存降低最轻载EP / OD-MoE 99.94%预测·<1GB边缘MoE / Tarragon 160-213×故障恢复加速AW/EW分离 / Inference Scaling ISCA'26 Capacity-Bound regime / MoEntwine 62%通信降低晶圆级芯片MoE |
| MoE→Hardware §20 | `2026-07-27.md` §20 | 2026-07-27 | **本期新增5条**: Tile-level Overlap 2.64×无侵入加速 / NCCL EP统一EP API / GQE attention-MoE / SpecMoE 4.30× self-assisted SD / Blackwell MoE 2.8× 3月软件优化 |
| MoE→Hardware §21 | `2026-07-28.md` §1 | 2026-07-28 | **本期新增4条**: PagedWeight 72% memory·1.94×动态量化 / TriRoute 跨轴耦合验证 / Moebius EP↔TP 215ms运行时切换 / Gimbal 42.9%↓TTFT三层协调 |
| MoE→Hardware §22 | `2026-07-29.md` §1 | 2026-07-29 | **本期新增12条**: DA-MoE 1.16-1.29×分布感知 / SHAPE Shapley剪枝 / ReMoE 26% expert复用(ICML'26) / CoX-MoE 7.1× AMX CPU-GPU(DAC'26) / METRO 4.11×平衡expert数 / Stratum 8.29× Mono3D DRAM / DuoServe-MoE 5.34×双相策略 / FinDEP 1.61×细粒度DEP / AIConfigurator 50% MoE加速 / FP4 Hopper 12.5%训练加速 / TIDE 1.5× dLLM offload / PuzzleMoE 50% bit-packed压缩 |
| MoE→Hardware §23 | `2026-07-30.md` §8 | 2026-07-30 | **本期新增11条**: ExpertPlex 2.01×跨phase共享 / ThAME 15.7× FeFET-DRAM(ESWEEK'26) / ViBE 45% P90↓ GPU变异 / ST-MoE时空预取 / Dense2MoE Roofline指导 / TileQ 10×内存↓2D-tiling / UniEP 1.03-1.38× MegaKernel / AxMoE近似计算×MoE / EnergyLens 52.9×能量变化 / Megatron Core 1,233 TFLOPS / UCCL-EP跨平台EP栈 |
| MoE→Hardware §24 | `2026-07-31.md` | 2026-07-31 | **本期新增12条**: BaseRT 6.4× Apple M5 / Perseus 10.3×多节点megakernel / ARGUS 99-104% MoE kernel / TileSight tile-centric perf model / CAEE 8-18% cost-aware expert / MiMo-V2.5 SWA+MoE生产 / AFD Design Space attention-FFN解耦 / TriMoE 2.83× GPU-AMX-NDP / ROMER MoE on CIM / Sparse MoE精度陷阱 / SERE 2.0× (ICLR'26) / Edge GPU-NDP 2.41× (DATE'26) |
| | | | **累计152条 → 164条** ✓ |

## 📖 最新条目速查（2026-07-13）

| # | 来源 | 论文/博客 | 核心方法 | 关键数据 | 硬件影响 |
|:-|:----|:---------|:---------|:--------|:--------|
| 1 | 🟢 arXiv | UBEP (2607.06202, SIGCOMM'26, 2026-07-07) | 为NVL72/CloudMatrix384重构All-to-All通信库 | **↓52.4%** All-to-All延迟·**↓11.1%** TPOT | ⭐⭐⭐⭐⭐ 超节点互联需从零重构All-to-All原语 |
| 2 | 🟢 arXiv | ASAP (2606.22541, 2026-06-21) | 解耦attention+MoE，全异步prefill执行 | **↑90%** SLO-compliant prefill吞吐 | ⭐⭐⭐⭐⭐ 超节点内global barrier是可消除瓶颈 |
| 3 | 🟢 arXiv | Moebius (2606.26607, 2026-06-25) | 运行时TP↔EP切换，215-434ms完成 | **1.16-1.25×** RL rollout加速 | ⭐⭐⭐⭐⭐ 高带宽互联使运行时并行重配成为可能 |
| 4 | 🟢 arXiv | UltraEP (2606.04101, 2026-06-18) | 首款精确负载实时均衡器，每microbatch重均衡 | **94.3%** force-balanced理想吞吐·**1.49×** vs 无均衡 | ⭐⭐⭐⭐⭐ RSN扩展互联使实时均衡成为可能 |
| 5 | 🟢 arXiv | EVICT (2605.00342, 2026-05-01) | MoE投机解码自适应draft tree裁剪 | **2.35×** vs 自回归·**1.21×** vs EAGLE-3 | ⭐⭐⭐⭐ 减少不必要专家激活→降低HBM带宽压力 |
| 6 | 🔴 NVIDIA | Fusion Kernels (Blog, 2026-06-15) | CuTe DSL融合MLP+Activation+Quantize内核 | **1.3-2×** kernel加速·**8%** DeepSeek-V3端到端 | ⭐⭐⭐⭐⭐ sync-free CUDA Graphs消除CPU瓶颈 |
| 7 | 🔴 NVIDIA | Dynamo+NVL72 (Blog, 2025-06-06) | Disaggregated serving + Wide EP + NVL72 130TB/s | **6×** 吞吐提升(仿真)·Wide EP=64 | ⭐⭐⭐⭐⭐ 72-GPU NVLink域使wide EP从理论到实践 |
| 8 | 🟢 arXiv (OSDI'26) | SmallEP (2606.10493, 2026-06-09) | CPU-GPU hybrid: SLP推理 + SmallEP + AVX-512 FP8 GEMV | **1,800** tok/s prefill (2×RTX 5090)·45K tokens/30s·**28** tok/s INT4 decode | ⭐⭐⭐⭐⭐ 云级服务质量首次在消费级硬件上实现；SmallEP证明EP可缩至2GPU级别 |
| 9 | 🟢 arXiv (ISCA'26) | DySHARP (2605.05607, 2026-05-07) | 动态in-switch计算：ISA+架构+运行时协同，NVLS动态扩展 + token-centric kernel fusion | **1.79×** end-to-end speedup | ⭐⭐⭐⭐⭐ 首次将NVLink SHARP从静态collective扩展到动态MoE通信；证明in-switch计算的瓶颈在不对称性而非带宽 |
| 10 | 🟢 arXiv | Sieve (2605.11277, 2026-05-11) | 动态expert-aware PIM加速：运行时调度GPU/PIM，基于token-to-expert分布，联合通信/带宽/吞吐决策 | **1.3×–1.6×** throughput (3 model scales) | ⭐⭐⭐⭐ 首次将expert bimodal分布引入PIM调度决策；PIM架构需从"静态offload"进化到"runtime-aware调度" |
| 11 | 🔴 arXiv (HB+3D) | ELMoE-3D (2604.14626, 2026-04-16) | 3D-stacked HW-SW co-design: hybrid-bonding + Elastic Self-SD + bit-sliced LSB架构 | **6.6×** speedup·**4.4×** energy efficiency (vs naive MoE) | ⭐⭐⭐⭐⭐ 首款专门为MoE设计的3D堆叠加速器；Elastic-SD（expert+bit双轴弹性）是全新概念 |
| 12 | 🟢 arXiv | EEP (2605.10670, 2026-05-11) | 显式可变membership的EP通信栈，单rank故障→11s恢复，无需全实例重启 | **11s** recovery pause·**52s** 恢复至95% throughput·vs 348s全重启 | ⭐⭐⭐⭐⭐ 宽EP的生产级可靠性里程碑；CUDA Graph + runtime可变membership是工程突破 |
| 13 | 🔴 Microsoft Research | MoE-Prefill (2605.02960, 2026-05-02) | AsyncEP: 异步权重AllGather替代激活AllToAll，prefix-aware路由，true-FLOPs负载追踪 | **1.35–1.37×** throughput·**29.8–36.2%** per-GPU MFU·**1.59×** long-context | ⭐⭐⭐⭐⭐ 将prefill-only serving的瓶颈从通信转为计算；AsyncEP是prefill场景AI基建设计新范式 |

| 14 | 🟢 arXiv | **TriRoute** (2607.06601, 2026-07-06) | 三层联合路由控制器：MoE+MoD+KV-cache位宽统一决策 | Pareto主导独立组合·尾部case显著更好 | ⭐⭐⭐⭐ 证明三个硬件资源维度是强耦合的 |
| 15 | 🟢 arXiv | **FoE** (2605.06206, 2026-05-07) | 架构级All-to-All消除——重组MoE为per-KV-head集群 | **5.2×** forward-pass**·3.62×** TTFT**·1.95×** TBT | ⭐⭐⭐⭐⭐ 从架构层面消除All-to-All，极大简化互联需求 |
| 16 | 🟢 arXiv | **WiSP** (2606.21868, 2026-06-20) | Working-Set Paging + MV-WSA分配最优VRAM分割 | **1.95×** decode吞吐·固定分割差~20% | ⭐⭐⭐⭐ 将VRAM分配从二选一升维为定量优化 |
| 17 | 🟢 arXiv | **Tiara** (2606.13708, 2026-06-10) | 可编程线速NIC ISA解决间接引用墙 | **1.88×** MoE expert-gather·**2.8×** PagedAttention | ⭐⭐⭐⭐⭐ NIC可编程化是CXL/RDMA下一代功能方向 |
| 18 | 🔴 NVIDIA | **HW-Friendly MoE Design** (Blog, 2026-07-10) | 官方硬件友好AI设计7条准则 | GB300 GEMM K>3072/80%·对齐128/256/512 | ⭐⭐⭐⭐⭐ 首次系统化输出，对模型架构师有直接约束力 |
| 19 | 🟢 ISCA'26 | **Inference Scaling** (2605.19775, 2026-05-19) | MoE vs dense在frontier scale的不对称瓶颈 | MoE受限路由/同步·dense受限互联/带宽 | ⭐⭐⭐⭐ 为MoE vs dense在推理场景下的瓶颈差异建立定量认知 |
| 20 | 🟢 arXiv | **BrownoutMoE** (2607.04164, 2026-07-05) | RL驱动的expert分组：结构感知重组hot/cold experts | **↓71.4%** accuracy退化·**↑2.24×** throughput | ⭐⭐⭐⭐ 原始expert组织是结构性低效源 |
| 21 | 🟢 arXiv | **MAESTRO** (2607.08601, 2026-07-09) | 马尔可夫链建模跨层expert依赖的剪枝框架 | **↑10.61%** 性能保持@50%压缩·更低跨任务方差 | ⭐⭐⭐⭐ 专家剪枝需考虑路由拓扑结构 |
| 22 | 🟢 arXiv | **ELDR** (2607.00466, 2026-07-01) | PD分离MoE的expert局部性感知decode路由 | **↓5.9–13.9%** 中位数TPOT@40 GPU | ⭐⭐⭐⭐ 同负载不同expert组合导致不等效延迟 |
| 23 | 🟢 arXiv | **Gimbal** (2606.15177, 2026-06-13) | 全协同跨层调度：前端调度+后端expert放置联合优化 | **↓42.9%** TTFT·**↓33.3%** TPOT | ⭐⭐⭐⭐ MoE调度前后端必须协同设计 |
| 24 | 🟢 arXiv | **MoE-on-Edge** (2606.21428, 2026-06-19) | 实证：MoE在带宽受限设备上劣于dense | **~31%** 落后·**2.1×** 能耗·总参数决定性能 | ⭐⭐⭐⭐⭐ "MoE适合资源受限设备"需修正 |
| 25 | 🟢 arXiv | **DeLS-Spec** (2607.07409, 2026-07-08) | 模块化解耦long/short上下文推测解码 | 极低训练成本·一致优于DFlash | ⭐⭐⭐ SD模块化趋势 |
| 26 | 🟢 INFOCOM'26 | **Director** (2607.08782, 2026-06-13) | 预测驱动的在线proactive expert放置 | **↓11–55%** 端到端延迟 | ⭐⭐⭐⭐ 从"均衡"走向"预测驱动" |
| 27 | 🟢 arXiv | **MoP** (2607.01844, 2026-07-02) | 混合并行度MoE训练栈，每层不同并行策略 | **↑4.7–8.2×** per-GPU吞吐 vs FSDP2 | ⭐⭐⭐⭐⭐ 不同层需要不同并行策略 |
| 28 | 🟢 arXiv | **UFP4** (2606.20381, 2026-06-18) | 统一FP4训练挑战E2M1，揭示收缩偏差 | MoE 124B上一致优于E2M1基线 | ⭐⭐⭐⭐⭐ Blackwell E2M1设计存根本缺陷 |
| 29 | 🟢 arXiv | **FlexMoE** (2606.27866, 2026-06-26) | expert内通道级别嵌套剪枝，支持运行时预算切换 | **~99.8%** 保持@50%剪枝 | ⭐⭐⭐⭐ 与MAESTRO expert级剪枝互补 |
| 30 | 🟢 arXiv | **GeMoE** (2606.26287, 2026-06-24) | Gating entropy自适应路由，动态确定每token expert数 | **+36.5%** 稀疏度·**99.5%** 保持 | ⭐⭐⭐⭐ 固定top-k假设需修正 |
| 31 | 🟢 arXiv | **dMoE** (2605.30876, 2026-05-29) | Block级路由解决diffusion+MoE的expert膨胀 | 69.5→14.6 unique experts·**76-80%** 内存降 | ⭐⭐⭐⭐ diffusion+MoE需硬件级block路由 |
| 32 | 🟢 arXiv | **MoE-Spec** (2602.16052, 2026-02-17) | MoE推测解码的verification-time expert budgeting | **10–30%** 吞吐↑ vs EAGLE-3·可控quality-budget trade-off | ⭐⭐⭐⭐ Expert capacity硬编码为可配置调度参数 |
| 33 | 🟢 arXiv | **DES** (2602.00879, 2026-01-31) | Sequence级coreset共享：Intra-Sequence Sharing + Saliency-Aware Voting | **>55%** expert减少·**≤38%** 延迟降·**99%** 精度保持 | ⭐⭐⭐⭐ 内存与并行度解耦的关键验证，与dMoE互补 |
| 34 | 🟢 ICML'26 | **ZipMoE** (2601.21198, 2026-01-28) | 无损压缩+Cache-Affinity调度，边缘推理I/O→compute范式转换 | **↑72.77%** 延迟降低·**↑6.76×** 吞吐·无损质量 | ⭐⭐⭐⭐ 边缘AI芯片需感知MoE参数统计冗余 |
| 35 | 🟢 arXiv | **MoE-DisCo** (2601.06857, 2026-01-11) | Decompose→独立并行训练→融合微调，在低端设备上预训练MoE | **47.6–69.5%** 训练成本降低·匹配或超越全参数性能 | ⭐⭐⭐⭐ MoE训练不再必然需要全A100/H100集群互联 |
| 36 | 🟢 arXiv | **EcoSpec** (2607.12696, 2026-07-14) | Cost-aware SD: 消除expert scattering，draft选择纳入expert activation cost | **↑1.62×** end-to-end decoding (DeepSeek-V3.1/Qwen3-235B/GPT-OSS-120B) | ⭐⭐⭐⭐⭐ 首次将expert activation cost显式建模为SD优化目标 |
| 37 | 🔴 NVIDIA | **HW-Friendly Design** (Blog, 2026-07-10) | 7条官方硬件-MoE协同设计准则：维度/对齐/宽度/量化/EP/PP/Helix | K>3072达80%·对齐256/512·NVFP4<1pt损失 | ⭐⭐⭐⭐⭐ 首次系统化MoE硬件设计约束输出 |
| 38 | 🟢 arXiv | **TriRoute** (2607.06601, 2026-07-06) | 三轴(MoE+MoD+KV量化)联合路由学习，Lagrangian预算约束 | Pareto主导独立组合·尾部case显著更好 | ⭐⭐⭐⭐⭐ 证明三个硬件资源维度是强耦合的 |
| 39 | 🟢 ICML'26 | **MoE-nD** (2604.17695, 2026-04-19) | 用MoE路由为每层选择(eviction-ratio, K-bits, V-bits) | **14×** 压缩·匹配基线·AIME +6-27pts | ⭐⭐⭐⭐ Layer-aware HBM分配替代统一压缩 |
| 40 | 🟢 arXiv | **Irminsul** (2605.05696, 2026-05-07) | MLA原生内容寻址KV cache，CDC-chunking + content-hash + δ-rotation | **~83%** token恢复·**63%** prefill能耗节省 | ⭐⭐⭐⭐ 内容寻址cache需硬件CAM支持 |
| 41 | 🟢 arXiv | **Var-Width** (2606.18246, 2026-06-16) | 哑铃形宽度分配：加宽首尾收窄中间，parameter-free residual resizing | **↓22%** FLOPs·**↓15%** KV cache I/O·MoE 3B验证 | ⭐⭐⭐ 中间层压缩与tile对齐存在张力 |
| 42 | 🟢 arXiv | **D-cut** (2607.14647, 2026-07-16) | 批量感知自适应SD验证深度裁剪，cross-request pruning + runtime cost model | **↑1.26×→1.65×** 高并发加速·**↑3.0×** MoE vs 自回归 | ⭐⭐⭐⭐ 部署环境感知SD——GPU架构+并行策略直接影响最优验证深度 |
| 43 | 🔴 arXiv (CS.AR) | **Economics of AI Decoding Chips** (2607.13068, 2026-07-10) | 形式化GPU compute-heavy×capacity-light低效，提出MoE decode专用芯片设计点 | **$19K** hold DS-R1 671B vs $350K H100 node | ⭐⭐⭐⭐⭐ 对"GPU是AI推理唯一方案"的根本挑战 |
| 44 | 🟢 arXiv | **HyperParallel-MoE** (2605.23764, 2026-05-22) | Ascend NPU AIC+AIV tile级异构taskflow调度MoE训练，消除host同步 | **↓1.58×** Dispatch-to-Combine MoE-FFN延迟 | ⭐⭐⭐⭐⭐ NPU可通过异构core显式同步实现NVIDIA无法实现的细粒度overlap |
| 45 | 🟢 arXiv | **NanoCP** (2605.21100, 2026-05-20) | 请求级动态Context Parallelism (DCP)：解耦MoE通信与KV cache放置 | **↑1.88×–3.27×** SLO请求率·**↓1.79×–2.12×** P99尾部延迟 | ⭐⭐⭐⭐⭐ KV cache需在集群内"液化"——任意到任意低延迟连接 |
| 46 | 🟢 arXiv | **FluxMoE** (2604.02715, 2026-04-03) | Expert Paging抽象：expert weights从GPU驻留解耦为streamed resource | **↑3.0×** 吞吐 vs vLLM（内存受限场景） | ⭐⭐⭐⭐ Expert不必然常驻HBM→HBM容量应优先分配KV cache而非expert |
| 47 | 🟢 ACL'26 | **MACS** (2605.05225, 2026-04-19) | 模态感知EP负载均衡：Entropy-Weighted Load + Dynamic Modality-Adaptive Capacity | 训练无关·多模态MoE MLLM·显著优于已有方法 | ⭐⭐⭐⭐ 模态信息应纳入EP调度决策，仅token count不够 |

> **前期条目**: 见 `2026-07-09.md` §8（UBEP/DFlash/CrossPool）·`2026-07-08.md` §8（BrownoutMoE/DODOCO/NASiC）

---

---

| 48 | 🟢 arXiv | **SonicMoE** (2512.14080, 2025-12→2026-03, Tri Dao/Stoica) | IO+Tile-aware MoE: 激活缓存最小化+IO重叠+Token Rounding消除padding | **1.86×** Hopper·**25%** Blackwell·**45%** 激活内存↓·64 H100=213B tok/day | ⭐⭐⭐⭐⭐ 45%激活内存缓解HBM wall·Token Rounding首将tile对齐引入MoE调度·纯软件获Blackwell 25%加速 |
| 49 | 🔴 NVIDIA | **NCCL EP** (2603.13606, 2026-03, NVIDIA官方) | 首个NCCL原生EP通信库：ncclEpDispatch/ncclEpCombine原语，LL(1-128 tok) + HT(4096+ tok)双模式 | DeepEP可竞争kernel性能·vLLM集成·跨NVIDIA平台支持 | ⭐⭐⭐⭐⭐ NVIDIA以官方API统一EP通信生态（vs DeepEP/UCCL-EP/Hybrid-EP碎片化）·LL模式要求域内full-mesh·HT模式层级聚合随NVLink域大小增益 |
| 50 | 🟢 arXiv | **FEPLB** (2604.19654, 2026-04) | 利用NVLink Copy Engine实现近乎免费的intra-node MoE负载重均衡，Two-Phase Dispatch+Copy Engine重分配 | **51-70%** token straggler↓·**50-68%** GEMM straggler↓·**2×** vs FasterMoE@EP=8·零EP通信开销 | ⭐⭐⭐⭐⭐ 首次将Copy Engine定位为MoE负载均衡的免费通信通道·硬件中存在与SM正交的空闲资源可被调度利用·优势随EP degree增长 |
| 51 | 🟢 arXiv | **NIMBLE** (2604.00317, 2026-03) | 运行时多路径互联均衡：min-congestion优化+multiplicative-weights求解+GPU kernel RDMA pipeline | **2.3×** intra-node·**3.8×** inter-node·**5.2×** skewed All-to-Allv·**1.35×** MoE端到端·均衡流量无退化 | ⭐⭐⭐⭐⭐ 5.2× All-to-Allv加速→现有互联带宽利用率不到20%·运行时路由比加带宽更有效·超节点仍需流量感知重路由 |
| 52 | 🔴 NeurIPS 2025 Spotlight | **Mozart** (2603.07006, 2026-03) | 3.5D Wafer-Scale Chiplet MoE训练：NoP-Tree拓扑+层次化内存+on-package all-to-all+流式token/expert调度 | 三种主流MoE模型验证显著效率提升（详细数据见论文） | ⭐⭐⭐⭐⭐ 首个MoE专用chiplet架构·NoP-Tree专为MoE all-to-all定制的片内拓扑·"模块化映射模块化"——expert→chiplet一一对应的原生硬件 |
| 53 | 🟢 arXiv | **FoMoE** (2606.19025, 2026-06, Oxford/Cisco/Meta) | 打破全副本壁垒：expert分区+skip-token+部分expert复制，将MoE训练从全互联集群解放 | **1.42×** 通信↓ vs高效基线·**45.44×** vs DDP·**1.4×** 吞吐加速·100B规模建模可行 | ⭐⭐⭐⭐ 挑战"MoE训练必须full-replica"假设·45.44×通信降低→互联网级MoE训练首次可能·分区训练对低带宽/跨DC场景特别有价值 |

| 54 | 🟢 MLSys'26 | **FarSkip-Collective** (2511.11505, 2025-11→2026-05, AMD) | 修改skip connection架构使MoE通信天然与相邻层计算重叠，self-distillation恢复精度 | **32.6%** TTFT↓·**97.3%** prefill overlap·**88.9%** training overlap·<1%精度损失@109B | ⭐⭐⭐⭐⭐ "改架构" vs "加带宽"的范式竞争·32.6%加速在现有硬件上通过架构修改实现·如可扩展则对互联硬件投资产生结构性影响 |
| 55 | 🟢 arXiv | **DisagMoE** (2605.11005, 2026-05, Meta/MIT/CMU) | Attention-FFN解耦到不同GPU组+多阶段管道+roofline模型均衡带宽分配 | **1.8×** speedup @ 16×8 H800 | ⭐⭐⭐⭐⭐ Disaggregation从prefill-decode推向attention-FFN级别·attention组和FFN组对互联需求不同→异构互联设计空间·训练场景AFD实现 |
| 56 | 🔴 arXiv (Meta) | **MoEBlaze** (2601.05296, 2026-01-08, Meta) | 端到端token调度+优化数据结构消除中间缓冲区+协同设计内核+智能激活检查点 | **>4×** speedup·**>50%** 内存节省 vs 现有MoE框架 | ⭐⭐⭐⭐⭐ 迄今最激进的MoE训练加速数字·证明训练栈中存在大量未被利用的结构性低效·50%内存节省对HBM容量规划直接影响 |
| 57 | 🟢 ASPLOS'26 | **LAER-MoE** (2602.11686, 2026-02-12, PKU/ByteDance) | Fully Sharded Expert Parallel (FSEP): 专家参数完全分片+All-to-All部分恢复+运行时自适应重布局 | **1.69×** vs SOTA训练系统 | ⭐⭐⭐⭐ Expert物理位置可在训练中动态改变·All-to-All模式从已知变为动态·增加互联设计不确定性 |
| 58 | 🟢 arXiv | **Multi-Head LatentMoE + Head Parallel** (2602.04870, 2026-02-04, ASU) | Latent空间multi-head路由 + Head Parallel替代EP → O(1)通信+完全均衡+确定性 | **1.61×** 训练加速·**O(1)** 通信不随k增长·**完全均衡**·**确定性** | ⭐⭐⭐⭐⭐ O(1)通信+完全均衡+确定性→互联流量可预测可优化·与FoE互补（不同架构路径消除All-to-All瓶颈）·需改造MoE架构定义 |
| 59 | 🟢 ISPASS'26 | **TaxBreak** (2603.12465, 2026-03-12, CMU/AMD) | Trace-driven Host编排开销分解+HDBI判据+发现MoE kernel dispatch 8-11×更多 | **8-11×** kernels/output token·**10-29%** 编排↓+**14%** 端到端↑仅靠更快CPU | ⭐⭐⭐⭐⭐ MoE隐藏成本在Host CPU, 8-11× kernel dispatch是严重低估的瓶颈·CPU单线程性能是MoE推理一阶参数·解释Grace CPU+CUDA Graphs战略方向 |

> **前期条目**: 见 `2026-07-09.md` §8（UBEP/DFlash/CrossPool）·`2026-07-08.md` §8（BrownoutMoE/DODOCO/NASiC）·`2026-07-13.md` §10 · `2026-07-14.md` §11（BrownoutMoE/MAESTRO/ELDR/Gimbal/MoE-on-Edge/DeLS-Spec）

---

## 🆕 最新追加（2026-07-29，第22批，新增12条）

> **本期特色**: 覆盖**4大新方向**：(i) 路由分布感知调度 (DA-MoE)；(ii) 专家剪枝方法论新维度 (SHAPE/ReMoE)；(iii) 硬件-系统协同设计 (CoX-MoE/Stratum)；(iv) 推理配置全域优化 (AIConfigurator/METRO)

| # | 来源 | 论文/博客 | 核心方法 | 关键数据 | 硬件影响 |
|:-|:----|:---------|:---------|:--------|:--------|
| 86 | 🟢 arXiv | **DA-MoE** (2607.23099, 2026-07-25, NTU/Harvard) | 分布感知MoE kernel调度：Effective Experts指标+Dirichlet逆向建模+在线分布匹配离线tuned kernel | **1.16×** DS-V3·**1.29×** Kimi K2·peak **1.40×/1.56×** | ⭐⭐⭐⭐ 首次将per-expert路由分布而非token count引入kernel选择；distribution-aware runtime无需CPU-GPU同步 |
| 87 | 🟢 arXiv | **SHAPE** (2606.09886, 2026-06-03) | 联盟感知专家剪枝：MoE推理建模为合作博弈，Shapley值分配expert在top-k联盟中的边际贡献 | **20-40%** 剪枝保持精度·显著降低峰值GPU内存 | ⭐⭐⭐⭐ 专家间的合作价值>个体价值——hot expert因冗余在联盟中价值为负；剪枝后expert子集更紧凑fit HBM |
| 88 | 🟢 ICML'26 | **ReMoE** (2605.27081, 2026-05-26, BUAA) | Router微调提升expert时间局部性：偏置router选最近刚激活的expert，软约束匹配cache locality | **26%** expert复用↑·**8.4%** vLLM吞吐↑·**43.6-49.8%** TPOT↓·**1.77-1.99×** @Jetson Orin | ⭐⭐⭐⭐ Router可训练出cache友好行为——cache locality成为可训练的loss项；HBM-CPU传输瓶颈可通过router行为控制缓解 |
| 89 | 🟢 DAC'26 | **CoX-MoE** (2605.17889, 2026-05-18, KAIST) | AMX-enabled CPU-GPU协同：coalescing-aware orchestration + 静态expert分层预分配（高频GPU低频CPU AMX） | **7.1×** vs FlexGen·**2.4×** vs MoE-Lightning·coalesced batch替代micro-batch | ⭐⭐⭐⭐⭐ CPU AMX单元首次被系统利用于MoE推理——CPU的AI加速单元可作为MoE的低成本扩展层与GPU形成异构集群 |
| 90 | 🟢 arXiv | **METRO** (2512.09277, 2025-12-09, NVIDIA Research) | 最小Expert Token路由：memory-bound regime下**平衡激活expert数**而非token数；novel allGather替代allToAll | **decode ↓11-22%** ·总吞吐 **↑3-21%** ·decode吞吐 **↑4.11×** @固定SLO | ⭐⭐⭐⭐⭐ NVIDIA对"EP负载均衡"的范式颠覆：**平衡token数=激活更多expert=加剧内存压力**；GPU memory bandwidth成为EP调度首要约束 |
| 91 | 🟢 arXiv | **Stratum** (2510.05245, 2025-10-06, UCSD) | 系统-硬件协同：Mono3D DRAM（单片3D堆叠DRAM）+ near-memory processing + GPU协同，hybrid bonding连接 | **8.29×** decode吞吐·**7.66×** 能效 vs GPU基线 | ⭐⭐⭐⭐⭐ Monolithic 3D DRAM作为HBM替代方案——垂直互联更密→更高内部带宽→支持更高效NMP；专家激活预测引导z-dimension数据分层 |
| 92 | 🟢 arXiv | **DuoServe-MoE** (2509.07379, 2025-09-09, Sydney) | 双相专家预取缓存：prefill用two-stream CUDA pipeline预取+decode用layer-level predictor预取 | **5.34×** TTFT↑·**7.55×** end-to-end latency↓ | ⭐⭐⭐⭐ prefill和decode对expert加载策略需求根本不同——统一策略导致任一phase suboptimal |
| 93 | 🟢 arXiv | **FinDEP** (2512.21487, 2025-12-24, PolyU/HKUST) | 细粒度Disaggregated EP：计算/通信拆分为小任务→变粒度pipeline→高效搜索求解器 | **1.61×** 吞吐↑·**1.24×** @32-GPU | ⭐⭐⭐⭐ 当前DEP低效更多来自软件调度而非硬件带宽——细粒度pipeline可恢复大部分性能损失 |
| 94 | 🟢 arXiv | **AIConfigurator** (2601.06288, 2026-01-09, NVIDIA) | 统一性能建模：GEMM/attention/通信/内存分解→校准kernel数据库→自动解析最优launch参数 | **50%** MoE架构加速·**40%** dense·平均**30s**搜索 | ⭐⭐⭐⭐ MoE配置空间远大于dense——自动化工具可释放50%额外性能，无需硬件改动 |
| 95 | 🟢 arXiv | **FP4 Training for MoE** (2603.02731, 2026-03-03) | Hopper上不依赖原生FP4 TC实现MXFP4：FP8↔FP4直通+scaling-aware转换 | **14.8%** 峰值激活内存↓·**12.5%** 训练吞吐↑@671B(1157→1302 tok/s/GPU) | ⭐⭐⭐⭐ Blackwell E2M1不是唯一FP4路径——Hopper软件协同也能实现大部分FP4收益；FP4压缩使EP通信带宽需求减半 |
| 96 | 🟢 arXiv | **TIDE** (2605.20179, 2026-05-19) | I/O-aware dLLM expert offload：利用diffusion过程expert激活时间稳定性→interval-based刷新 | **1.4×** LLaDA-mini·**1.5×** LLaDA-flash·lossless | ⭐⭐⭐⭐ dLLM+MoE的expert激活具有时间稳定性→offload策略需重新设计 |
| 97 | 🟢 arXiv | **PuzzleMoE** (2511.04805, 2025-11-06, UIUC) | 无训练MoE压缩：稀疏expert合并(element-wise dual-mask)+bit-packed编码(复用指数位存mask+sign) | **50%** 压缩保持精度·**1.28×** 推理加速·MMLU **+16.7%** vs同类@50%压缩 | ⭐⭐⭐⭐ 专家权重中共享/专用参数可在element级别分离——bit-packed编码利用FP指数位underutilization |

---

## 🆕 最新追加（2026-07-30，第23批，新增11条）

> **本期特色**: 覆盖**4大新方向**: (i) 硬件异构性与MoE的交互（ViBE/ThAME）；(ii) EP通信栈统一化（UniEP/UCCL-EP）；(iii) MoE专用硬件加速新范式（ThAME/Megatron Core）；(iv) MoE部署自动化与能效探索（EnergyLens/AxMoE）

| # | 来源 | 论文/博客 | 核心方法 | 关键数据 | 硬件影响 |
|:-|:----|:---------|:---------|:--------|:--------|
| 98 | 🟢 arXiv | **ExpertPlex** (2607.18002, 2026-07-20, PKU) | PD分离新方案：MoE experts跨phase共享+attention单独解耦+adaptive persistent kernels tile级动态调度 | **2.01×** vs instance-level PD分离·**1.66×** vs PD colocation | ⭐⭐⭐⭐⭐ 95%权重去重暴露当前PD分离结构性浪费；adaptive persistent kernels将expert调度粒度从GPU降为tile——GPU调度器需细粒度持久化能力 |
| 99 | 🟢 ESWEEK'26 | **ThAME** (2607.17074, 2026-07-19, WSU) | 3D异构多chiplet MoE加速器：FeFET非易失+DRAM易失chiplet + 专用NoC应对非确定MoE流量 | **15.7×** speedup·**9.8×** 能效 vs SOTA | ⭐⭐⭐⭐⭐ 首款用FeFET+DRAM混合存储应对MoE non-contiguous expert weight加载的专用架构；证明MoE的不规则通信模式需要专用NoC拓扑设计 |
| 100 | 🟢 arXiv | **ViBE** (2606.00735, 2026-05-30, AMD) | 硬件变异感知expert放置：per-GPU建模范式(制造差/功率限/热条件)×expert激活画像→高频expert放快GPU、低频放慢GPU | **SLO ↑14%** ·**P90 TTFT ↓45%** ·影响随规模增大 | ⭐⭐⭐⭐⭐ **MoE加速器不仅存在非确定性路由，还存在确定性硬件变异**——同型号GPU之间的性能差异被MoE的不均衡组合放大；全行业benchmarking标准需增加variability维度 |
| 101 | 🟢 arXiv | **ST-MoE** (2606.15453, 2026-06-13, GWU) | 时空expert预取框架：层间+token间expert激活强相关性→轻量运行时预测+可重构硬件预取 | 显著improve推理性能与能效 | ⭐⭐⭐⭐ Expert激活在相邻层和连续token间高度可预测——可重构预取硬件可消除大部分expert加载延迟 |
| 102 | 🟢 arXiv | **Dense2MoE** (2605.26496, 2026-05-25) | 统一的剪枝+upcycling框架：Layer Fusion UpCycling——Roofline理论引导，剪掉bandwidth-heavy attention layers，复用MLP为MoE experts | 显著推进on-device推理延迟vs精度Pareto前沿 | ⭐⭐⭐⭐ **按Roofline模型做架构变换决策**——MoE化不是"more experts"而是"right compute/memory ratio"；Roofline模型直接指导MoE拓扑设计 |
| 103 | 🟢 arXiv | **TileQ** (2605.09281, 2026-05-09) | 2D-tiling结构化低秩PTQ：跨input/output维度共享低秩因子+多低秩expert fused单pass推理 | **10×** 额外内存↓·**~5%** 推理延迟 | ⭐⭐⭐⭐ 低秩分解fused single-pass使GPU利用率从多个小GEMM→大GEMM，间接降低kernel launch overhead |
| 104 | 🟢 arXiv | **UniEP** (2604.19241, 2026-04-21, PKU/NVIDIA) | 统一EP MegaKernel：融合通信+计算为单个MegaKernel→自动参数搜索+确定性token排序保证数值一致性 | **1.03-1.38×** vs SOTA·数值完全一致 | ⭐⭐⭐⭐ EP优化被碎片化为ad-hoc kernels——统一MegaKernel可减少内核发射开销并保证数值可复现；确定性排序对生产训练有直接价值 |
| 105 | 🟢 ISVLSI'26 | **AxMoE** (2605.04754, 2026-05-06, Univ. Limerick) | 近似计算×MoE首次系统研究：8种近似乘法器，3种MoE变体(Hard/Soft/Cluster)×2种CNN+1种ViT | Dense最鲁棒·Hard MoE在ViT优于dense@激进近似 | ⭐⭐⭐⭐ **MoE的稀疏路由结构对近似计算误差不如dense鲁棒**——未来近似加速器设计需考虑路由结构引入的误差传播路径 |
| 106 | 🟢 arXiv | **EnergyLens** (2605.14249, 2026-05-13, MIT/IBM) | 端到端能量建模框架：einsum interface捕获fusion/parallelism/overlap + load-imbalance-aware MoE + 多GPU通信能量模型 | MAPE 9.25-13.19%·config间**1.47× prefill/52.9× decode**能量变化 | ⭐⭐⭐⭐ MoE配置对能耗的影响远大于对延迟的影响——自动化能耗探索可释放巨大节能潜力，现有延迟优先搜索忽略了这个空间 |
| 107 | 🔴 NVIDIA (Tech Report) | **Megatron Core MoE** (2603.07685, 2026-03-08, NVIDIA) | 全栈MoE训练优化：fine-grained recompute/offload/optimized dispatchers/Grouped GEMM/fusions/CUDA Graphs/Parallel Folding/FP8+NVFP4/长上下文 | **1,233/1,048 TFLOPS/GPU** DS-V3 @GB300/GB200·**974/919** Qwen3-235B | ⭐⭐⭐⭐⭐ **NVIDIA全栈MoE训练的SSOT文档**——Pareto均衡揭示memory/communication/compute三轴耦合；88页技术报告是MoE训练架构设计的参考教科书；Parallel Folding提供灵活多维并行性 |
| 108 | 🟢 arXiv | **UCCL-EP** (2512.19849, 2025-12, UC Berkeley) | 可移植EP通信栈：UCCL框架统一后端抽象，支持跨GPU/NIC异构平台，解决DeepEP等的非移植问题 | 跨平台竞争性能vs DeepEP·支持heterogeneous GPU+NIC | ⭐⭐⭐⭐⭐ EP通信栈碎片化（DeepEP/Hybrid-EP/NCCL-EP三足鼎立）——UCCL-EP统一抽象降低硬件换代时的软件迁移成本；对超节点定制互联有直接参考价值 |

---

## 🆕 最新追加（2026-07-31，第24批，新增12条）

> **本期特色**: 覆盖**5大新方向**: (i) MoE专用CPU-GPU架构新范式 (BaseRT Apple M5/ARGUS agent kernel)；(ii) 多节点megakernel隐藏瓶颈 (Perseus NIC fence)；(iii) GPU性能建模新方法 (TileSight)；(iv) attention-FFN解耦设计空间系统化 (AFD Design Space)；(v) 边缘/异构部署新探索 (TriMoE/ROMER/Edge GPU-NDP)

| # | 来源 | 论文/代码 | 核心方法 | 关键数据 | 硬件影响 |
|:-|:----|:---------|:---------|:--------|:--------|
| 109 | 🟢 arXiv | **BaseRT** (2607.19438, 2026-07-21, Apple M5) | 手写Metal 4 tensor-core MoE kernels：dense+MoE GEMM专用+flash-attention prefill；memory-bound decode保留专有kernel | **6.4×** prompt vs llama.cpp·**3.9×** vs MLX·**1.75×** decode vs llama.cpp·15 configs 1B-35B | ⭐⭐⭐⭐⭐ Apple M5每core独立Neural Accelerator首个嵌入GPU core内的MoE矩阵加速单元；MoE矩阵密集→加速收益最大；memory-bound decode仍需专有kernel——「一核双kernel」设计原则 |
| 110 | 🟢 arXiv | **Perseus** (2605.00686, 2026-05-01) | 消除多节点megakernel隐藏序列化：解耦signaling→per-destination粒度fence合并+NIC硬件fence flag | **10.3×** 端到端 (proxy-based)·**1.2×** match/exceed IBGDA GPU-direct | ⭐⭐⭐⭐⭐ 发现multi-node MoE megakernel回归的根本原因是proxy-based RDMA的fence序列化而非带宽；NIC应提供per-transfer硬件completion信号——对超节点RDMA互联设计有直接影响 |
| 111 | 🟢 arXiv | **ARGUS** (2604.18616, 2026-04-16, AMD MI300X) | Agentic GPU kernel生成：data-flow invariants + tile-based Pythonic DSL + SMT编译时验证 + in-context RL planner | **99-104%** hand-optimized assembly throughput·**2-1543×** vs 现有agent系统·200 KernelBench任务 | ⭐⭐⭐⭐⭐ MoE kernel占LLM推理90%+ GPU时间；首次agent生成MoE kernel达手写优化水平；对硬件厂商kernel开发策略有深远影响——从手写优化转向agent-in-the-loop |
| 112 | 🟢 arXiv | **TileSight** (2607.22432, 2026-07-24) | 首原理tile-centric GPU性能模型：intra-tile(计算-内存pipeline overlap)+inter-tile(cache层次)+cross-device(互联)统一tile抽象 | **12.35%** MAPE A100-B6000·**16.18%** wMAPE @32GPU·**13.52%** wMAPE vLLM·L2 cache <1pt误差 | ⭐⭐⭐⭐ MoE kernel优化核心障碍是准确性能建模——tile-centric统一抽象首次在单/多GPU提供一致预测；可跨架构迁移(A100→B6000) |
| 113 | 🟢 arXiv | **CAEE** (2606.29982, 2026-06-29) | Cost-Aware Expert Execution：轻量代价模型→选择性剪枝低贡献高代价expert+低开销补偿→避免额外数据移动 | **8-18%** DS-R1 671B延迟↓·**<1%** 精度损失·offload+on-device均有效 | ⭐⭐⭐⭐ 当前所有expert消耗相同HBM带宽但贡献差异巨大——cost-aware expert selection可节省8-18%延迟，对HBM带宽规划有直接参考 |
| 114 | 🔴 Xiaomi TR | **MiMo-V2.5** (2607.13095, 2026-07-13) | Hybrid SWA+MoE+Multimodal全管道生产优化：layerwise KVCache prefetch+SWA-aware prefix cache+RDMA GCache+KVCache-affinity router | 首个Hybrid SWA+MoE+multimodal生产系统·严格$O(W)$ SWA存储 | ⭐⭐⭐⭐ Hybrid SWA的KV cache优化策略对推理服务器设计有直接借鉴价值；MoE+SWA组合对KV cache和expert weights产生双维度IO需求 |
| 115 | 🟢 arXiv (Gatech) | **AFD Design Space** (2605.28302, 2026-05-27) | Attention-FFN Disaggregation设计空间系统探索：on-device kernel测量+高保真仿真；chunked-prefill/P-D/AFD三级对比 | AFD strict SLO下**~4k tok/s** @ DS-V3.2·非AFD不可行·attention:FFN分组比准则 | ⭐⭐⭐⭐ Disaggregation从prefill-decode走向attention-FFN——不同解耦级别适用不同workload；给出attention:FFN device分组的workload-dependent决策准则 |
| 116 | 🟢 DAC'26 | **TriMoE** (2603.01058, 2026-03-01) | GPU(hot)→AMX-enabled CPU(warm)→DIMM-NDP(cold)三层异构offload + 瓶颈感知调度 + 预测动态relayout | **2.83×** speedup vs SOTA | ⭐⭐⭐⭐ MoE expert的三层热分布需三层计算单元精确映射——warm expert的compute gap是GPU-CPU/GPU-NDP双重架构未覆盖的中间地带 |
| 117 | 🟢 arXiv | **ROMER** (2605.11800, 2026-05-12) | 首个MoE on analog CIM研究：real-chip噪声校准→替换under-activated experts+percentile-normalized router recalibration | **58.6/58.8/59.8%** perplexity↓ @ DS-MoE/Qwen-MoE/OLMoE | ⭐⭐⭐⭐ 模拟CIM硬件噪声显著扰乱MoE路由均衡——router校准比weight校正更关键；clean-trained路由在噪声下suboptimal |
| 118 | 🟢 arXiv | **Sparse MoE Failure Modes** (2605.19378, 2026-05-12) | 视频DiT Token-Choice稀疏MoE训练失效5级诊断：bfloat16精度陷阱/selective deadlock/soft saturation/U分布/self-recovery | bfloat16精度截断→tiny weight updates归零；~1/3层single-expert deadlock | ⭐⭐⭐⭐ bfloat16 mixed precision在MoE训练中是硬件精度陷阱——tiny gradient updates被截断→routing collapse；对FP8/FP4硬件精度要求有警示意义 |
| 119 | 🟢 ICLR'26 | **SERE** (2602.07616, 2026-02-07) | 相似度感知expert重路由：batch解码中token从secondary重路由到最相似primary expert + 动态保护关键expert | **2.0×** speedup·minimal quality loss·vLLM单行代码集成 | ⭐⭐⭐⭐ Batch decoding场景expert冗余可在输入感知层面动态消除；expert相似度可作为未来硬件预取线索 |
| 120 | 🟢 DATE'26 | **Edge GPU-NDP MoE** (2601.03992, 2026-01-07) | MoE tensor parallelism跨NDP单元 + 负载感知均衡 + 无数据集预取高频专家 | **2.41× avg·2.56× peak** speedup | ⭐⭐⭐⭐ MoE tensor parallelism在low-batch edge场景比EP更高效——EP的负载不均衡问题在边缘NDP场景更严重 |

---

## 🎯 持续跟踪的关键问题

1. **MoE推理效率何时劣于dense？** → qs不等式提供决策工具
2. **硬件-软件边界如何移动？** → NVIDIA sync-free CUDA Graphs表明软件创新可减少硬件需求
3. **EP通信瓶颈能消减到什么程度？** → UltraEP 94.3%为当前天花板
4. **KV cache危机如何缓解？** → DeepSeek-V4 10×压缩是年度级突破
5. **（NEW）MoE部署能否从fixed走向adaptive？** → FlexMoE嵌套剪枝+ASAP异步化+Wide-EP弹性并行，三方向汇聚为同一趋势
6. **（NEW）大规模EP的经济性门槛在哪？** → Wide-EP 1.8×需NVL72类高带宽域，非所有集群结构等效
7. **（NEW）路由不均衡是系统问题还是模型固有？** → DODOCO实证颠覆性结论：straggler是模型架构指纹，All-to-All感知互连设计应考虑架构稳定带而非EP degree
9. **（NEW）超节点的All-to-All需要什么通信原语？** → UBEP证明BSP+Buffering抵消了高带宽优势，统一地址空间需要匹配的原语设计
10. **（NEW）SD的范式何时从head-based转向block-diffusion？** → DFlash 15× vs EAGLE-3 1.5×，证明block-diffusion+Blackwell架构是SD的新天花板
11. **（NEW）冷模型部署的内存瓶颈能否通过硬件分离解决？** → CrossPool提出weight/KV-cache池分离，硬件级支持将释放更大潜力
12. **（NEW）MoE prefill的同步barrier能否彻底消除？** → ASAP证明global barrier不是必需约束，解耦+异步可获90%吞吐提升
13. **（NEW）TP与EP是二选一还是动态切换？** → Moebius证明运行时切换可行(215-434ms)，打破固定并行度假设
14. **（NEW）负载均衡能在每microbatch粒度做到？** → UltraEP 94.3%证明RSN互联带宽使细粒度均衡首次工程可行
15. **（NEW）MoE训练融合内核的收益上限在哪？** → CuTe DSL同步free化+量化融合，DeepSeek-V3获8%端到端，GPT-OSS获93%
16. **（NEW）消费级硬件能否达到云级MoE服务质量？** → SmallEP (OSDI'26) 证明：CPU-GPU hybrid + 2×RTX 5090可达1,800 tok/s prefill，EP可缩至2GPU
17. **（NEW）NVLink SHARP能处理动态MoE通信吗？** → DySHARP (ISCA'26) 首次将in-switch computing扩展到不规则MoE模式，1.79×端到端加速
18. **（NEW）PIM加速MoE的最佳调度策略是什么？** → Sieve证明需runtime-aware调度而非静态offload，bimodal expert分布是关键
19. **（NEW）3D堆叠能否为MoE专门设计？** → ELMoE-3D证明hybrid-bonding+Elastic-SD可实现6.6×加速/4.4×能效，expert+bit双轴弹性是新方向
20. **（NEW）宽EP的生产部署如何容错？** → EEP证明可变membership + CUDA Graph修复可在11s内从单rank故障恢复，vs 348s全重启
21. **（NEW）prefill-only serving如何消除EP通信开销？** → MoE-Prefill (MSR) 用异步权重AllGather替代激活AllToAll，1.37×吞吐，per-GPU MFU达36%
22. **（NEW）MoE+MoD+KV-cache是否是强耦合设计问题？** → TriRoute证明三层条件计算应联合决策而非独立优化；对下一代GPU架构的多轴协同控制有指导意义
23. **（NEW）All-to-All能否从架构层面彻底消除？** → FoE的per-KV-head集群方案证明在一个cluster内完全可行，这是否将成为MoE推理芯片的新设计范式？
24. **（NEW）VRAM在专家池和KV池之间的最优分派策略是什么？** → WiSP的MV-WSA将边际收益视角引入，但离线vs在线控制仍有差距（~20%），需要更好的实时分配算法
25. **（NEW）NIC可编程化能否成为MoE推理基础设施的通用加速方案？** → Tiara证明1.88× MoE expert-gather加速，但预注册程序的灵活性边界和硬件成本需要更多研究
26. **（NEW）MoE与dense在推理场景下的优化方向是否根本不同？** → ISCA'26证明frontier scale上MoE瓶颈在路由/同步而dense在互联/带宽，提示硬件架构应差异化设计
27. **（NEW）Expert组织结构本身是否就是系统瓶颈？** → BrownoutMoE证明保留原始expert组织是结构性低效——即用最先进runtime优化也无法完全补偿
28. **（NEW）Expert剪枝能否从路由拓扑角度优化？** → MAESTRO证明跨层依赖建模使50%压缩率下+10.61%保持——剪枝决策应从路由依赖性出发
29. **（NEW）相同负载下不同expert组合是否导致不等效延迟？** → ELDR揭示Yes——PD分离架构中decode worker的expert局部性差异可致TPOT差~14%
30. **（NEW）MoE的前端调度和后端expert放置应否协同设计？** → Gimbal证明独立优化导致TTFT+42.9%/TPOT+33.3%——硬件fabric调度器应暴露路由局部性信号
31. **（NEW）"MoE适合资源受限设备"是否成立？** → MoE-on-Edge实证反驳：带宽受限硬件上总参数决定性能，edge上~31%落后dense，2.1×能耗
32. **（NEW）Speculative Decoding是否正走向模块化？** → DeLS-Spec与EVICT分别从不同角度证明SD可拆解为可独立优化的子模块
33. **（NEW）Expert放置应从"负载均衡"进化到"预测驱动"吗？** → Director证明基于请求activation预测的主动放置可降11-55%延迟——expert放置正从被动走向主动
34. **（NEW）MoE训练是否需要每层不同并行度？** → MoP证明4.7-8.2× vs FSDP2——不同层的计算/通信特征差异巨大，单一策略必然低效
35. **（NEW）NVIDIA Blackwell/Rubin选择的E2M1 FP4格式是否有根本缺陷？** → UFP4证明收缩偏差在MoE大规模训练中被乘法性放大——E1M2/INT4均匀格式应纳入下一代硬件标准
36. **（NEW）Expert剪枝的最佳粒度是expert级还是通道级？** → MAESTRO（expert级）+ FlexMoE（通道级）互补，未来硬件应同时支持两种粒度的动态裁剪
37. **（NEW）MoE路由的top-k固定假设是否已过时？** → GeMoE以36.5%稀疏度提升证明每个token应有不同expert数——GPU执行模式需适应性调整
38. **（NEW）Diffusion+MoE是否需要独立的硬件路由策略？** → dMoE揭示69.5→14.6的expert膨胀——block并行解码需要block级路由而非token级
39. **（NEW）MoE+Speculative Decoding场景下，expert capacity应作为硬件参数吗？** → MoE-Spec证明verification-time expert budgeting可获10-30%吞吐提升——expert capacity限应作为GPU调度器的显式可配置参数
40. **（NEW）MoE推理的内存开销能否从根本上与并行度解耦？** → DES在dLLM场景实现>55% expert减少——如果自回归MoE场景也能推广，将改变VRAM专家缓存规划
41. **（NEW）边缘MoE推理是否必然I/O-bound？** → ZipMoE以72.77%延迟降低证明通过无损压缩+调度协同可以从I/O-bound转向compute-centric——边缘AI芯片应内建对MoE参数统计冗余感知的硬件支持
42. **（NEW）MoE训练是否必须依赖高性能GPU集群全互联？** → MoE-DisCo以47.6-69.5%成本降低证明分解+独立训练+融合微调可行——训练集群可从"高性能全互联"转向"低端集群并行+高端节点收敛"
43. **（NEW）MoE decode是否需要专用芯片而非通用GPU？** → HTX-301证明commodity DDR5+28nm在MoE decode场景有10-18×成本优势——下一个GPU代际是否需要为decode设计单独的计算/HBM比？
44. **（NEW）NPU能否在MoE训练效率上建立对NVIDIA的结构性优势？** → HyperParallel-MoE利用AIC+AIV显式同步做NVIDIA无法实现的tile级overlap——这是NPU替代论证的关键环节
45. **（NEW）KV cache和MoE通信的解耦能否做到请求级别？** → NanoCP证明yes——attention+MoE+KV cache三者的绑定是效率损失的根本原因，超节点需要任意到任意低延迟互联
46. **（NEW）Expert权重是否应当永远常驻GPU HBM？** → FluxMoE证明在内存受限场景下expert streaming page可获3×吞吐——HBM容量分配应优先KV cache而非expert weights
47. **（NEW）多模态MoE的EP均衡是否单靠token count就够了？** → MACS证明no——visual token的语义价值差异导致模态感知的负载均衡成为必要
48. **（NEW）MoE kernel优化能否通过tile-aware调度获得额外收益？** → SonicMoE的Token Rounding在高稀疏度下额外1.16×——未来的GPU调度器应考虑tile-aligned token routing
49. **（NEW）NCCL统一EP API后，MoE通信栈碎片化状态是否终结？** → NCCL EP的LL/HT双模式对服务器硬件有两类要求：LL需full-mesh NVLink域，HT需大NVLink域+高效RDMA层级聚合
50. **（NEW）NVLink Copy Engine能否被普遍用作MoE负载均衡的"免费"通道？** → FEPLB证明可行且零SM开销——下一代GPU是否应设计更多异构引擎并暴露给MoE调度器？
51. **（NEW）MoE All-to-All的瓶颈到底是带宽不足还是利用率不足？** → NIMBLE的5.2×提示后者更关键——互联设计应从"加带宽"转向"用带宽"（运行时负载感知路由）
52. **（NEW）MoE是否需要专属chiplet架构而非通用GPU？** → Mozart的NeurIPS Spotlight标志着学术社区对MoE专用硅片的认可——expert→chiplet一一映射的原生硬件是新的设计范式
53. **（NEW）MoE训练能否在跨数据中心/互联网级互联上完成？** → FoMoE的45.44×通信降低vs DDP使"不在同一数据中心内训练MoE"首次成为可行选项
54. **（NEW）修改模型架构能否替代增加互联带宽？** → FarSkip-Collective的32.6%加速、97.3%重叠率证明架构修改可在不增加带宽下消除通信阻塞——这对互联硬件投资的经济性判断有结构性影响
55. **（NEW）Attention-FFN解耦训练是否比prefill-decode解耦更有潜力？** → DisagMoE的1.8× + MoEBlaze的4×加权说明：训练栈的低效远大于推理栈，且attention-FFN解耦是更彻底的方案——下一代集群设计应考虑异构GPU分组
56. **（NEW）MoE训练框架是否存在结构性低效？** → MoEBlaze的4×+50%内存节省暗示：当前所有MoE训练框架可能都存在50%+的浪费空间；下一代GPU的HBM-计算比（F/S）可能因此需要重新校准
57. **（NEW）Expert在训练中的物理位置应固定还是动态？** → LAER-MoE的FSEP证明动态重布局可行——这对互联设计从"确定性路由"走向"自适应路由"提出了新需求
58. **（NEW）O(1)通信的HP能否替代O(k)通信的EP？** → Multi-Head LatentMoE提供理论路径——但需改造MoE架构定义，执行成本是在latent空间增加计算；与FoE是两条互补的"架构消除All-to-All"路线
59. **（NEW）MoE推理的隐藏瓶颈是否在Host CPU而非GPU？** → TaxBreak的8-11× kernel dispatch + 14%端到端加速仅靠CPU提升证明：CPU单线程性能是MoE推理的一阶参数——这解释了为什么NVIDIA押注Grace CPU和CUDA Graphs
60. **（NEW）低资源MoE推理中，如何最优分配VRAM给expert权重与KV cache？** → WiSP的MV-WSA提供系统化方案：对齐每字节边际延迟收益，subject to KV admission floor；固定分割比oracle差~20%
61. **（NEW）MoE的流行叙事"稀疏激活减少计算"在消费级/边缘硬件上是否成立？** → 实证证伪：在带宽受限硬件上推理成本跟踪总参数而非活跃参数，MoE比同活跃参数dense慢~10-31%，能耗高2.1×
62. **（NEW）MoE推理中计算均衡和通信均衡能否联合优化？** → PROBE的Continuous Lookahead Pipelining + 联合平衡规划实现1.32× prefill↓ + 1.26× decode↑，尤其在高波动负载下
63. **（NEW）MoE训练MFU是否存在2-3.5×提升空间？** → Piper（ORNL）通过数学模型+瓶颈识别+pipeline parallelism引入实现2-3.5× MFU vs X-MoE，1.2-9× A2A带宽vs vendor impl
64. **（NEW）EP的负载不均衡是否可以从"效率问题"升级为"安全问题"？** → RepetitionCurse（ICML'26）证明：简单重复token的黑盒攻击可将Mixtral-8x7B推理延迟放大3.063×——EP+MoE首次被证实存在DoS攻击面
65. **（NEW）TP和EP能否通过融合通信协议实现更高效的混合并行？** → MixServe的融合AR-A2A算法实现1.08-3.80× TTFT、1.03-1.66× ITL、5.2-50.3%吞吐↑——自动选择最优TP/EP策略
66. **（NEW）KV cache与expert权重的精度-内存tradeoff能否通过运行时动态量化来最优平衡？** → PagedWeight实现72%内存节省+1.94×吞吐（FP16质量），同内存预算质量提升39.3%——"软件扩展VRAM"效益可能超过单纯增加VRAM硬件的成本效益
67. **（NEW）EP负载不均衡应该被"消灭"还是"利用"？** → LLEP的5×加速/4×内存降低证明：接受不均衡+动态重路由比强行均衡更有效——如果互联提供低延迟远程内存访问，动态expert转移可进一步简化
68. **（NEW）MoE边缘推理是否必须要求大VRAM GPU？** → OD-MoE的<1GB运行证明"否"——分布式预测+按需加载可绕过VRAM瓶颈；与MoE on Edge（§18.2）形成互补：问题不在MoE架构而在系统设计选择
69. **（NEW）MoE推理集群的故障恢复能否做到亚秒级而无需全节点热备？** → Tarragon的160-213×加速+0.3-0.4s恢复证明：AW/EW分离+shadow expert可实现细粒度弹性——保留VRAM可直接转化为故障恢复能力
70. **（NEW）推理工作负载的系统设计范式是否已经从compute-bound转向Capacity-Bound？** → ISCA'26推理缩放律确认：推理链的KV cache需求使系统从FLOPs受限变为容量受限——MoE受路由延迟瓶颈，Dense受互联带宽瓶颈
71. **（NEW）晶圆级芯片（WSC）对于MoE EP推理是否有实质性优势？** → MoEntwine的+39% per-device对比NVL72证明有——但mesh拓扑的通信不均衡需要通过attention-MoE链路互补设计来解决
72. **（NEW）Speculative Decoding在MoE上天然有害？** → Cascade证明权重获取量随draft tokens数线性增长，可导致1.5× slowdown；utility metric动态启用可将slowdown限制在5%，吞吐提升7-14%
73. **（NEW）Attention/MoE/KV cache三个条件计算轴应联合优化还是独立优化？** → TriRoute证明强耦合（跨轴routing-collapse cascade），独立优化有显著leakage；单controller端到端训练Pareto支配独立组合
74. **（NEW）PD分离架构下MoE解码路由是否需要expert locality感知？** → ELDR以Expert Signature+Balanced K-means分区实现5.9-13.9% TPOT↓——负载均衡不解决MoE的解码延迟差异
75. **（NEW）MoE服务调度是否存在多级协同优化的超越潜力？** → Gimbal的三层（request/engine/expert）协调调度实现42.9% TTFT↓+33.3% TPOT↓——远超vLLM的FCFS+RR
76. **（NEW）MoE在推理中是否结构性地不如dense？能否用可计算判据判断？** → AMD的qs Inequality（q×s < 1时MoE劣势）——DeepSeek-V3@128K质量匹配dense有4.5×吞吐优势；建议将MoE视为训练期优化，推理期蒸馏到dense
77. **（NEW）NVIDIA全栈MoE优化揭示的硬件-软件重新校准意味着什么？** → 综合3篇博客：软件3个月2.8×（Blackwell）、Wide-EP 1.8× per-GPU（130TB/s NVLink前提）、EP通信效率5×提升空间（Hybrid-EP仅4-16SM跑满带宽）——软件栈优化空间远超预期
78. **（NEW）MoE通信与KV cache放置能否做到request级别的解耦？** → NanoCP的DCP证明：长序列跨instance分布attention（CP高），短序列本地（CP低）——DP-EP绑定结构对长上下文MoE推理有结构性低效；液化cache后P99 tail减半
79. **（NEW）GPU故障恢复能否绕过全节点重启在TP+MoE场景下实现弹性服务？** → AnchorTP的daemon+KVCache保持+不等宽ETP+MoE兼容——TFS↓11×、TTP↓59%，证明状态保留弹性的成本最优性
80. **（NEW）Disaggregated EP的调度能否在已有硬件带宽下实现超越带宽瓶颈的吞吐提升？** → FinDEP的细粒度pipeline+变粒度调度实现1.61×吞吐↑——当前DEP低效更多来自软件调度而非硬件带宽
81. **（NEW）不同层对KV cache压缩的敏感性差异是否需要per-layer异构策略？** → MoE-nD的14×压缩@匹配质量证明：uniform策略有显著浪费——但硬件层per-layer可变精度控制的开销需进一步量化
82. **（NEW）MoE weight量化能否在运行时按KV cache压力动态调整而实现\"软件扩展VRAM\"？** → PagedWeight实现72%内存节省+1.94×吞吐——证明运行时动态量化比固定精度分配在硬件投资回报上更优；未来GPU若提供per-expert可变精度硬件支持，该方案的开销可进一步降低
83. **（NEW）Attention/MoE/KV cache三个条件计算轴的单轴优化是否有结构性信息泄漏？** → TriRoute揭示跨轴routing-collapse cascade：一个轴collapse→传播到其他轴；单controller端到端训练Pareto支配独立组合——GPU应提供统一的稀疏度/精度接口而非三轴独立硬件模块
84. **（NEW）EP和TP并行模式能否在运行时间无缝切换而不影响inflight请求？** → Moebius证明可以：215-434ms切换，2.4%内存开销，共用同一份权重+KV cache——GPU互联带宽已足够支持decode-step间layout重配置；NVL72如原生支持EP↔TP切换语义，可覆盖在线/离线混合工作负载
85. **（NEW）MoE服务调度是否需要三层协同而非单层优化？** → Gimbal的三层协调（request/engine/expert）实现42.9% TTFT↓+33.3% TPOT↓——单层优化无法避免40%+延迟损失；scale-up域low-latency expert迁移能力可减轻MINLP调度的保守性
86. **（NEW）MoE kernel选择是否应该感知per-expert路由分布？** → DA-MoE证明fused-MoE kernel的最优选择随每个expert的token分布而非全局token count显著变化——distribution-aware dispatch无需CPU-GPU同步即可获得1.16-1.29×加速
87. **（NEW）专家剪枝是否需要建模专家间的合作价值而非个体价值？** → SHAPE用Shapley值证明hot expert可能因冗余在top-k联盟中边际贡献为负——比全局/逐层剪枝更鲁棒，剪枝后专家子集更紧凑fit HBM
88. **（NEW）能否通过微调router来改善expert的cache locality？** → ReMoE（ICML'26）证明router可训练出cache友好行为——增加26%时间局部性且不增加inference计算量；对offload场景Jetson Orin获1.77-1.99×加速
89. **（NEW）CPU的AMX单元能否成为MoE推理的低成本扩展层？** → CoX-MoE（DAC'26）证明7.1× vs FlexGen——CPU AI加速单元首次被系统利用于MoE推理，为CPU-GPU异构集群提供新设计空间
90. **（NEW）MoE decode的memory-bound regime下应平衡什么？** → METRO（NVIDIA Research）颠覆性结论：平衡token数→激活更多expert→加剧内存压力→性能下降；应平衡激活expert数，获4.11× decode吞吐；allGather替代allToAll有极小通信开销
91. **（NEW）Mono3D DRAM能否替代HBM成为MoE的存储方案？** → Stratum的8.29× decode吞吐证明单片3D堆叠DRAM的垂直互联密度优势→更高内部带宽+高效NMP，专家激活预测引导3D分层放置
92. **（NEW）prefill和decode是否需要完全不同的expert加载策略？** → DuoServe-MoE以5.34× TTFT证明yes——prefill密集激活需减少驻留时间(减少峰值内存)，decode稀疏激活需精确预取(减少尾部延迟)
93. **（NEW）Disaggregated EP的低效主因是软件调度还是硬件带宽？** → FinDEP证明1.61×仅通过细粒度调度恢复——当前DEP低效更多来自调度而非带宽，硬件过剩可能掩盖调度低效
94. **（NEW）MoE的配置空间能否自动化探索？** → AIConfigurator（NVIDIA）以平均30s搜索释放50% MoE加速——证明MoE的TP/EP/PP/CUDA Graphs/KV分数组合空间巨大且存在显著未利用价值，50%性能可直接通过配置释放
95. **（NEW）Hopper能否通过软件协同实现Blackwell的FP4收益？** → Practical FP4 Training证明14.8%激活内存↓+12.5%训练吞吐↑@671B——Blackwell E2M1不是唯一FP4路径，且FP4压缩可使EP通信带宽需求减半
96. **（NEW）dLLM+MoE的offload策略是否需要重新设计？** → TIDE证明diffusion过程expert激活具有时间稳定性→interval-based刷新比在线预取更高效且lossless——dLLM趋势改变MoE offload的基本假设
97. **（NEW）MoE专家压缩能否做到element级别而非expert级别？** → PuzzleMoE证明50%压缩+1.28×加速——专家权重中共享/专用参数可在element级别分离，bit-packed编码利用FP指数位underutilization
98. **（NEW）PD分离中的MoE expert权重冗余有多大？可否通过跨phase共享消除？** → ExpertPlex证明95%权重去重是可能的——PD分离中两个phase保留同一份expert weights是结构性浪费，attention-MoE解耦复用优于phase资源分割
99. **（NEW）同型号GPU之间的制造变异是否被MoE Serving放大？** → ViBE证明Yes——制造/功率/热条件差异在MoE的不均衡路由下被大幅放大，随规模增大更严重；全行业基准测试标准需增加variability维度
100. **（NEW）MoE是否需要FeFET+DRAM混合存储的专用加速器？** → ThAME（ESWEEK'26）证明3D异构chiplet设计可获15.7×加速/9.8×能效——expert weight的non-contiguous加载模式使FeFET非易失存储有独特优势
101. **（NEW）EP通信栈的碎片化是否能被统一抽象终结？** → NCCL EP + UCCL-EP + UniEP从不同层面尝试统一——NCCL EP（NVIDIA原生）、UCCL-EP（跨平台移植）、UniEP（MegaKernel融合），三路线并行意味着EP标准化仍在早期
102. **（NEW）MoE训练能量消耗是否比延迟更依赖配置选择？** → EnergyLens揭示1.47× prefill/52.9× decode能量变化——能量优化空间远大于延迟优化，现有延迟优先搜索策略忽略了主要矛盾
103. **（NEW）近似计算×MoE是否可行？** → AxMoE（ISVLSI'26）首次实证：MoE的稀疏路由对近似误差不如dense鲁棒——稀疏激活不仅降低计算量，还改变了误差传播路径
| 104. **（NEW）MoE专用GPU kernel能否通过agent自动生成达到手写水平？** → ARGUS 99-104%证明yes——数据流invariant + SMT编译时验证是关键技术；对硬件厂商的kernel开发成本有直接影响
| 105. **（NEW）多节点megakernel通信瓶颈的根源是什么？** → Perseus证明fence序列化而非带宽——per-destination fence合并+NIC硬件fence flag可获10×加速；超节点互联设计需重视RDMA completion语义
| 106. **（NEW）每core内嵌Neural Accelerator的CPU-GPU架构是否是MoE的天然匹配？** → BaseRT 6.4×证明Apple M5路线可能——如果scalable，AI加速器将从「巨大GPU+HBM」走向「大量小矩阵单元+分级内存」
| 107. **（NEW）Disaggregation应该做到什么粒度？** → AFD Design Space证明chunked-prefill<P-D<AFD三级递进，每级有其适用workload——attention-FFN解耦最后一级但成本最高
| 108. **（NEW）MoE expert的三层热分布是否需要三层异构计算单元的精确映射？** → TriMoE 2.83×证明hot/warm/cold三层架构的必要性——warm expert的compute gap是GPU-CPU和GPU-NDP双重架构的最大盲区
| 109. **（NEW）MoE on analog CIM的核心挑战在路由均衡还是weight精度？** → ROMER证明硬件噪声扰乱路由均衡——router校准比weight校正更关键；clean-trained路由在噪声下suboptimal
| 110. **（NEW）Batch decoding中expert冗余是否可在运行时动态消除？** → SERE 2.0×证明可通过expert相似度感知重路由实现——expert相似度可作为硬件预取线索
