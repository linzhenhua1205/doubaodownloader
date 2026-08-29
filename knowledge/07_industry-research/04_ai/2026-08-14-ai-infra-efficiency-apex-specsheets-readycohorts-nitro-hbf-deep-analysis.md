# AI 基础设施效率前沿五篇深度分析：APEX × Spec Sheets × Ready Cohorts × NITRO × HBF（+RoutePack 交叉引用）

> **类型**: analysis | **日期**: 2026-08-14
> **定位**: 2026-08-12/13 arXiv 公告窗口内 5+1 篇 AI 基础设施效率论文深度拆解——覆盖**边缘 MoE 推理预取（APEX）、Blackwell Ultra INT8 全栈审计（Spec Sheets）、Agent 控制路径 GPU 机会绑定（Ready Cohorts）、3D NAND 存内计算（NITRO）、高带宽闪存 KV 卸载反面教材（HBF Sucks）**，并交叉引用已深度覆盖的 RoutePack（MoE RL 训练编排）。共同主线：**「规格/静态设计 vs 实际运行时」的鸿沟 + 调度/放置从启发式走向形式化优化 + 闪存层级化的正反两面**。
> **数据分级**: 🟢 arXiv 摘要一手抓取（6 篇全文 abs 页）· 🟡 摘要级推断（未读全文的技术细节标注）· 🔵 本地知识库锚点

---

## 📑 目录

- [0. 一句话摘要](#0-一句话摘要)
- [1. 事件定位与信息来源](#1-事件定位与信息来源)
- [2. 逐篇深度分析](#2-逐篇深度分析)
  - [2.1 APEX：边缘 MoE 自适应专家预取](#21-apex边缘-moe-自适应专家预取)
  - [2.2 Spec Sheets Are Not Kernels：Blackwell Ultra INT8 全栈审计](#22-spec-sheets-are-not-kernelsblackwell-ultra-int8-全栈审计)
  - [2.3 Ready Cohorts：Agent 控制路径的 GPU 机会绑定](#23-ready-cohortsagent-控制路径的-gpu-机会绑定)
  - [2.4 NITRO：3D NAND 存内计算 + DRAM 激活缓冲](#24-nitrod-date26-3d-nand-存内计算--dram-激活缓冲)
  - [2.5 HBF Sucks：高带宽闪存 KV 卸载的反面教材](#25-hbf-sucks高带宽闪存-kv-卸载的反面教材)
  - [2.6 RoutePack：交叉引用（已深度覆盖，不重复）](#26-routepack交叉引用已深度覆盖不重复)
- [3. 横向洞察（第一性原理）](#3-横向洞察第一性原理)
- [4. 与本地知识库互证](#4-与本地知识库互证)
- [5. 批判性审视](#5-批判性审视)
- [6. 可证伪预测](#6-可证伪预测)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 0. 一句话摘要

> **2026-08-12/13 一天之内，arXiv 集中出现 5+1 篇「AI 基础设施效率」论文，从四个维度同时冲击既有范式：① 边缘 MoE 推理的专家搬移从「静态 top-k 调度」走向「置信度驱动的自适应预取」（APEX，ESWEEK'26）；② 硬件规格书与软件栈的现实鸿沟被首次系统性审计——Blackwell Ultra（B300）名义上的 INT8 在 PTX/CUTLASS/vLLM/SGLang 四层一致撤退，「规格书不是内核」（Spec Sheets Are Not Kernels）；③ LLM-Agent 控制路径的 GPU 机会被形式化——固定分区份额 F=30.19%、精确离线份额 P\*=43.00%、决策留在设备 36 配置全胜（Ready Cohorts，含形式化证明）；④ 闪存层级化呈现正反双面——NITRO 用 DRAM 激活缓冲 + intra-plane 分布式数据流把 NAND-PIM 推理延迟降 85%（DATE'26 扩展），而 HBF Sucks 证明「把 HBF 当 SSD 直接替换来做 transient KV 卸载」会让端到端延迟上升 2-5.5×（更快的设备产生更慢的系统）。RoutePack（MoE RL 专家放置×打包，+14.89%）已在同日文档深度覆盖，本篇交叉引用。**

---

## 1. 事件定位与信息来源

### 1.1 事件事实

| 论文 | arXiv | 领域 | 提交 | 会场 |
|:--|:--|:--|:--|:--|
| RoutePack: Expert Placement and Attention-Aware Data Packing for MoE RL | [2608.12146](https://arxiv.org/abs/2608.12146) | cs.DC/LG | 08-12 | —（Ant Group） |
| APEX: Adaptive Expert Prefetching for Edge MoE Inference | [2608.11688](https://arxiv.org/abs/2608.11688) | cs.AR | 08-12 | **IEEE/ACM ESWEEK (CODES) 2026**，正式版入 IEEE TCAD |
| Spec Sheets Are Not Kernels: ISA/源码级审计 Blackwell Ultra INT8 | [2608.11693](https://arxiv.org/abs/2608.11693) | cs.AR | 08-12 | —（8 页，无性能测量） |
| Ready Cohorts: Bounding GPU Opportunity in LLM-Agent Control | [2608.12123](https://arxiv.org/abs/2608.12123) | cs.DC/AI/OS | 08-12 | —（含形式化证明+复现附录） |
| NITRO: 3D NAND Flash ISC with Enhanced Activation Dataflow | [2608.11920](https://arxiv.org/abs/2608.11920) | cs.AR | 08-12 | **DATE 2026** 扩展稿 |
| HBF Sucks! Full-Stack Characterization of HBF for KV-Centric Serving | [2608.11668](https://arxiv.org/abs/2608.11668) | cs.AR | 08-12 (v2 08-13) | —（13 页 12 图） |

**批量信号**：6 篇全部在 08-12（HBF v2 更新 08-13）提交，与 08-11~08-12 的 MISA-T/TideRL/RoutePack 三线窗口（见本地记忆）连续——**2026-08 中旬是 AI 基础设施效率论文的集中爆发期**，且均指向同一范式转移：*效率优化从「静态规格设计」转向「运行时可观测 + 可预测 + 全栈验证」*。

### 1.2 信息来源分级

| 级别 | 来源 | 覆盖 |
|:--|:--|:--|
| 🟢 一手 | arXiv abs 页全文抓取（6 篇） | 摘要+元数据（作者/会场/提交历史） |
| 🟡 摘要级推断 | 未读 HTML/PDF 全文的技术细节 | 各篇机制解释（标注「摘要级」） |
| 🔵 本地锚点 | 知识库既有专题（闪存 KV 卸载/量化/控制面分离） | §4 互证 |

---

## 2. 逐篇深度分析

### 2.1 APEX：边缘 MoE 自适应专家预取

**定位**：边缘部署 MoE 的**内存瓶颈**解决方案——不是把专家塞进内存（量化/剪枝路线），而是把「专家加载」从关键路径上搬走（预取/重叠路线）。**用户提示的「专家搬移从静态调度走向访问模式驱动」精确命中。**

**动机（第一性原理）**：
- MoE 边缘部署的吸引力：高模型容量 + 每 token 只激活少量参数（计算效率高）
- 但专家参数体量大，因容量/成本/功耗约束**常驻片外内存（off-chip）**→ 专家加载（loading）落在推理关键路径上
- 固定 top-k 预取（prefetch top-k experts）无法应对**路由的动态性**——预测不中就白预取（带宽浪费），预测对但来不及就 stall

**方法（摘要级）**：
1. **轻量 prefetch router**：在 attention block **之前**预测候选专家集合
2. **learned confidence model**：对每个候选专家给出置信度，**动态**决定额外预取哪些（不止 top-k）
3. **两种执行模式**：
   - *correctness-preserving*（保正确性）：保证精确路由语义 → 每 token 延迟 **-26%**、EDP（能量-延迟积）**-41%**（vs SOTA baseline）
   - *stall-free*（去停顿）：消除残余 stall，在「已就绪专家」上运行 → 额外效率增益，应用精度影响可忽略

**量化结果**：>99% overlap accuracy（预取与计算重叠的准确率），显著优于固定 top-k 预取；多 MoE 模型验证。

**技术原理**：核心是**「预测-重叠」双机制**——预测解决「预取谁」（confidence-driven 比 top-k 更准），重叠解决「何时取」（把加载时间藏进 attention 计算）。与 CPU 分支预测/内存预取的经典思想同构，但对象是**稀疏路由的专家权重**，且置信度模型是**在线学习**的（随路由分布漂移自适应）。

**局限（摘要级）**：stall-free 模式的「negligible accuracy impact」未给具体数字；edge 场景的带宽/功耗模型未在摘要展开。

**与本地锚点**：消费级 MoE 三维量化（RotaryQuant：dense 4-bit/路由 2-bit/共享 8-bit）是**权重压缩**路线，APEX 是**时间重叠**路线——两者正交可叠加；本地「8GB 卡 = Qwen3-8B INT4 32K ~7.2GB」的边缘约束正是 APEX 的靶场景。

### 2.2 Spec Sheets Are Not Kernels：Blackwell Ultra INT8 全栈审计

**定位**：**首个对「规格书宣称 vs 实际内核可用性」的 ISA/源码级系统性审计**——直接回应 AGENT.md 行为准则「先查证不猜测」。用户提示的「规格书宣称 vs 实际内核可用性存在鸿沟」是全文核心。

**动机**：B300 规格书 FP8:INT8 稠密计算比约 **30:1**；前代 H200 和 B200 都是 **1:1**。这个「INT8 被降级」在**实践中**意味着什么？作者沿四层栈追查：规格书 → PTX ISA → CUTLASS → vLLM/SGLang。

**四层撤退（关键发现）**：

| 层 | 发现 | 性质 |
|:--|:--|:--|
| PTX ISA | sm_103a **从不暴露**第五代张量核整数路径（`mma.sync...kind::i8`），同一 PTX 修订却把 FP4 kinds 扩展到该目标 → 遗留 warp-level IMMA 是 B300 上**唯一架构合法**的整数张量核路径 | NVIDIA 层 1 |
| CUTLASS | kernel generator 对 103a 目标**显式跳过** INT8 UMMA 生成，FP8 无条件生成 | NVIDIA 层 2 |
| vLLM | **无 Blackwell INT8 GEMM**，模型加载后首次 forward 直接硬运行时错误（失败语义昂贵：加载完成才炸） | 生态层 |
| SGLang | AOT INT8 GEMM **停在 Sm90**；FP8 tuning 已覆盖 B200 | 生态层 |

**三个附带发现**：
1. **逃逸通道（escape hatch）**：环境变量把 vLLM INT8 路径重路由到 **JIT 编译 Triton backend**——可用但非原生
2. **假阴性陷阱**：显而易见的 profiler 方法（用于检测 sm_103「native INT8」）会**误判**——审计方法学本身有坑
3. **失败语义昂贵**：vLLM 是「模型加载完成后、首次 forward 才报错」——朴素测试成本高（先花时间加载）

**结论（原文核心命题）**：*「量化格式的可用性是**整个栈**的属性，而非模型或规格书的属性」*——四层中三层是 NVIDIA 自家，一致撤退；**datasheet 上名义存在的格式，默认不可部署**。

**与本地锚点**：完美呼应「量化检测四层法 + 铁律 ≥2 独立信号」「FP8 仅 ~240 有限值易误判 int8、BF16=非量化」「先查证不猜测」。同时是 B300「降配实证」（Rubin Ultra 192GB 降配）在**软件栈侧**的镜像——硬件降配之外，软件栈也在对 INT8 做「静默降级」。

### 2.3 Ready Cohorts：Agent 控制路径的 GPU 机会绑定

**定位**：LLM-Agent 服务的**控制路径**（model↔tool 之间的确定性小转换：route outcome → update state → emit next effect）何时值得交给 GPU 执行、以及**决策留在设备上**（不往返 host）的收益——**控制/数据面分离延伸到 Agent 负载**（用户提示点）。

**形式化框架**（含证明）：

| 指标 | 含义 | 实测（851-session 真实 trace，Poisson replay，10 万活跃 session，K=256，50ms 发布期限） |
|:--|:--|:--|
| **F** | 固定分区份额（fixed-partition share） | **30.19%** |
| **P\*** | 精确离线份额（exact offline，专用动态规划精确计算） | **43.00%** |
| **U** | 局部上界（local upper bound） | **45.85%** |
| **A** | 在线达成份额（online achieved） | 需 joined runtime 实测（本篇未测） |

**关键结果**：
1. 零服务时间/无限容量/相等相对发布期限条件下，**专用动态规划精确计算 P\***；精确打包恢复固定窗口边界损失的 **81.83%** 机会
2. **outcome-derived route key 是 conditioning proxy（条件代理），不是可执行身份证明**——方法论自省
3. **机制研究**（决策留设备）：GPU 计算的二元决策**不返回 4 字节给 host 再重新派发**——4 个 GPU 放置 × 36 配置**全胜**；within-placement row-median 比 **1.19×-2.39×**
4. 两种 admissible 机制下 **14,557,440** 次批处理调用与独立 host oracle **完全一致**（正确性验证）
5. 反例：固定嵌套设备图（不移除任何 host 决策）在 5 放置 × 60 配置**全部更慢**——「把图搬上设备」不等于「去掉往返」

**结论**：Agent GPU 控制的两个可测量门 = **deadline-feasible cohort supply**（期限可行的工作组供给）+ **observation placement**（观测放置）。A（在线达成份额）、CPU displacement、service-level benefit 需要 joined finite online runtime 实测。

**与本地锚点**：TensorCast「控制/数据面分离第三次落地」的直接延伸——但对象从**推理 KV 管理**变为 **Agent 控制路径**；Aries「Agent 负载颠覆平台假设」（上下文收益递减、token 指标漏检）——Ready Cohorts 给出控制路径的**可计数机会**；Symphony「编排与工作锚点解耦」——本篇把「路由决策锚点」形式化。

### 2.4 NITRO（DATE'26）：3D NAND 存内计算 + DRAM 激活缓冲

**定位**：NAND-PIM（存内计算）路线的高性能化——解决既有 NAND-PIM 方案**不处理中间值（activation）的 dataflow/buffer** 的缺陷。用户提示的「3D NAND 存内计算」精确对应。

**动机（第一性原理）**：
- ISC（in-storage computing）缓解 host↔memory 数据瓶颈；LLM 需求暴涨但内存密度不匹配
- NAND-PIM 方案已出现，但**中间值（activation）的处理是盲区**——朴素做法是放慢速 flash 阵列 → 激活编程进 TLC NAND 的高延迟惩罚拖垮推理

**方法**：
1. **增强激活缓冲**：中间值放**快速 DRAM 子系统**，不落慢速 TLC flash 阵列
2. **分布式数据流**：NAND-PIM 阵列采用 **intra-plane 数据映射**最大化计算并行度

**量化结果**：推理延迟 vs baseline **最高 -85%**。

**技术原理**：本质是**存储介质分层 + 计算位置迁移**的组合——权重（静态）留在 NAND-PIM 原位计算，激活（动态）走 DRAM 快速缓冲，plane 级并行度由数据映射决定。与 CXL 池化内存 NDP（PLoRA）共享「计算靠近数据」哲学，但介质是 NAND（密度高、延迟高）而非 DRAM。

**局限（摘要级）**：-85% 的 baseline 定义需全文核实；NAND-PIM 的写放大/耐久/热问题未在摘要展开；无商用落地信息。

### 2.5 HBF Sucks：高带宽闪存 KV 卸载的反面教材

**定位**：**「更快的设备让系统更慢」的反直觉实证**——HBF（High-Bandwidth Flash，NAND 放在宽、package-local 接口后，读延迟/带宽优于 SSD）被当作 SSD 直接替换来做 transient KV 卸载，结果端到端延迟 **+2-5.5×**、最大 SLO goodput **-1.1-2.7×**（H100 与 B200 均如此）。

**方法**：SSD 风格 Mooncake KV-offloading 栈 + 换 HBF 底 → extended TokenSim + **4 条两小时 Qwen-Bailian 生产 trace** + 5 个 dense/MoE 模型 + H100/B200 profiles。

**悖论解释（成本收益模型）**：更快的 far tier 只在三条件同时满足时才有价值：
1. **read I/O 是瓶颈**
2. **reads > writes**
3. **交付带宽可持续**

**Transient KV 三条件全违**：

| 条件 | transient KV 实况 |
|:--|:--|
| read 瓶颈 | 否——两层层级把 reuse 留在 near tier，HBF 拿到的是 **relentless write-heavy stream**（每个 trace writes > reads） |
| reads > writes | 否——写多于读 |
| 带宽可持续 | 否——3D-ICE 热模型：堆栈在峰值带宽远未达到前先到**热极限**；TLC tier 比被替换的 SSD pool **磨损更快** |

**两个量化细节**：
- 买 flash through package **消耗 GPU near-tier 容量和带宽**（机会成本）
- HBF 自身 read/write 延迟**几乎无所谓**：scale 3.75× 只移动端到端延迟 <1%——瓶颈不在设备延迟，在系统布局

**结论（原文）**：*「设备没问题，drop-in 部署有问题」*——HBF 作为 transient KV 的 SSD 替代是坏的；但**选择性使用**（reuse-aware placement + write budgeting + thermal coordination）在 LLM serving 中有价值。

**与本地锚点（关键对照）**：本地「闪存级 KV 卸载实证」（Dell XE7740 + Solidigm D7-PS1030：峰值 2.9×/2.2×、持续 30K tok/s 闪存 94% vs DRAM 42%、Claude Code 一周 98.16% 缓存读取）是**正面**结果——**差异的根源是 workload 特征**：本地实证是**持久 KV 缓存**（高读取率、写少），HBF Sucks 是 **transient KV**（写多读少）。**结论：KV 缓存读取率/复用率决定闪存卸载是否有效**——这是「KV 四层命运」模型（L0 HBM/L1 CPU DRAM/L2 持久/L3 checkpoint）的实证分水岭。

### 2.6 RoutePack：交叉引用（已深度覆盖，不重复）

RoutePack（MoE RL 的专家放置×注意力感知打包联合优化）已在同日文档 **全文精读**（HTML 89KB，Ant Group）：
[2026-08-14-rl-posttraining-scheduling-battlefield-misa-tiderl-routepack-deep-analysis.md](../../03_AI/llm-techniques-principles/2026-08-14-rl-posttraining-scheduling-battlefield-misa-tiderl-routepack-deep-analysis.md)

本篇不重复，只做**框架衔接**：RoutePack 与 APEX 共享同一信息杠杆——**路由行为在训练/推理执行前可预测**（RoutePack 用 rollout-time routing replay 提前暴露逐层专家需求 → 训练布局；APEX 用 prefetch router 在 attention 前预测专家 → 推理预取）。**同一原理（routing predictability）在训练域（布局）与推理域（预取）的两次落地**——这是「调度=目标优化器」范式扩散的又一证据。

---

## 3. 横向洞察（第一性原理）

**洞察 1：「执行前可预测性」成为效率杠杆的新来源**
RoutePack（routing replay 暴露专家需求）、APEX（prefetch router 预测专家）、Ready Cohorts（控制路径并发工作可计数）——三篇独立工作共享同一前提：**工作负载的异构性 + 执行前可知性把调度从「黑盒反应」变成「白盒规划」**。与本地记忆「agentic/RL 负载的异构性与训练前可知性把调度从黑盒反应变成白盒规划」互证——这是 2026 年调度研究的范式主线（Cascade→MARS→TideRL→RoutePack→APEX→Ready Cohorts 一脉相承）。

**洞察 2：规格 vs 现实的鸿沟在两个层面同时显现**
- **硬件层**：Spec Sheets——INT8 名义存在、实际四层撤退（30:1 密度比是「规格书的真相」，全栈默认不可部署才是「现实」）
- **系统层**：HBF——设备规格（低延迟高带宽）是真的，但 drop-in 部署的系统行为是反的（2-5.5× 更慢）
两篇合起来是一个完整命题：**规格书描述的是设备能力，不是系统性能；系统性能是布局/栈/工作负载的联合属性**——「先查证不猜测」从方法论升级为系统设计原则。

**洞察 3：闪存层级化的正反双面**
- NITRO（硬件正攻）：DRAM 缓冲 + intra-plane 并行 → NAND-PIM 延迟 -85%
- HBF（部署反面）：drop-in 必败，但**选择性使用**有价值
两者不矛盾：**硬件能力强 ≠ 部署收益**，介质特性必须与数据访问模式（权重 vs transient KV vs 持久 KV）匹配。闪存内存化四路（HBF/zHBM/CXL 池化/光内存）的落地节奏将由「访问模式-介质匹配度」而非「设备规格」决定。

**洞察 4：控制/数据面分离的第三次延伸**
TensorCast（推理 KV 管理）→ 存储控制面 → **Ready Cohorts（Agent 控制路径）**：决策留在设备（GPU）的收益被形式化证明（36 配置全胜、1.19-2.39×）。Agent 时代的控制面设计与传统系统设计共享同一物理法则——**跨设备往返（round trip）是确定性成本，消除它是有界收益**。

**洞察 5：2026 系统论文的验证强度显著升级**
Spec Sheets pin 所有源到 commit/digest + 访问日期、Ready Cohorts 14,557,440 次调用对 host oracle、HBF 4 条生产 trace + 3D-ICE 热模型 + TLC 磨损模型——**「声称可复现」成为论文标配**。这与本系统「数据可验证：来源+基线+条件」的质量标准同构。

---

## 4. 与本地知识库互证

| 本地锚点 | 本篇对应 | 一致性 |
|:--|:--|:--|
| 消费级 MoE 三维量化（RotaryQuant）、8GB 卡本地推理约束 | §2.1 APEX | ✅ 互补：量化（权重压缩）与预取（时间重叠）正交可叠加 |
| 量化检测四层法 + ≥2 独立信号、FP8 ~240 有限值、BF16=非量化 | §2.2 Spec Sheets | ✅ 直接互证：格式可用性=全栈属性，检测必须下钻到 ISA/源码 |
| TensorCast 控制/数据面分离第三次落地、Aries Agent 负载、Symphony 锚点解耦 | §2.3 Ready Cohorts | ✅ 同哲学：跨设备往返是确定性成本 |
| 闪存级 KV 卸载实证（Dell+Solidigm 持久缓存 2.9×/30K tok/s/98.16% 缓存读取）、KV 四层命运、闪存内存化四路 | §2.4/§2.5 NITRO+HBF | ✅ 关键分水岭：**持久 KV（读多写少）卸载有效，transient KV（写多读少）drop-in 必败**——读取率决定闪存卸载有效性 |
| MISA-T × TideRL × RoutePack 三线（08-14 已覆盖） | §2.6 交叉引用 | ✅ 不重复，框架衔接 |
| 「调度器=目标优化器」范式（Cascade/MARS/TideRL） | §3 洞察 1 | ✅ 范式确认：RoutePack/APEX/Ready Cohorts 同属该谱系 |

---

## 5. 批判性审视

1. **Spec Sheets 无性能测量**（作者明示 companion measurement study in preparation）——审计证明「INT8 默认不可部署」，但「Triton escape hatch 跑 INT8 的性能如何」未量化；30:1 密度比在现实中是否真的意味着 INT8 无价值，取决于 Triton 路径的实测
2. **Ready Cohorts 是单作者理论工作**——F/P\*/U 是离线/模拟测量，A（在线达成份额）与 CPU displacement 依赖的 joined online runtime **尚未实现**；851-session trace 的通用性待验证
3. **APEX 的 stall-free 模式**：「negligible impact on application accuracy」未给具体精度数字（摘要级缺口）；edge 场景的带宽预算模型未展开
4. **HBF 的热/磨损建模**基于 3D-ICE 仿真，实际热管理（如既有 CXL 内存/SSD 的热协调经验）可能部分缓解；「writes > reads」结论基于 Mooncake 风格 transient KV 栈，换成持久 KV 场景结论可能反转（这正是本地实证的正面结果）
5. **NITRO 的 -85%** 相对 baseline 的定义需全文核实（可能是最朴素 NAND-PIM 基线）；NAND-PIM 商用化（写放大/耐久/控制器复杂度）未在摘要披露

---

## 6. 可证伪预测

| # | 预测 | 时间窗 | 证伪条件 |
|:--|:--|:--|:--|
| P1 | NVIDIA 在后续 CUDA/PTX 版本为 sm_103a 暴露第五代整数张量核路径（INT8 UMMA） | 2027-06 前 | 仍无 → 确认 INT8 架构级放弃（Spec Sheets 结论长期成立） |
| P2 | vLLM/SGLang 合入 Blackwell **原生** INT8 GEMM 支持（非 Triton escape hatch） | 2026-12-31 前 | 仍依赖 JIT Triton 重路由 |
| P3 | APEX 类**置信度驱动专家预取**成为边缘 MoE 推理标准实践（消费级 GPU/端侧） | 2027-12 前 | 固定 top-k 预取仍是主流 |
| P4 | HBF 在 KV serving 落地走向「**选择性放置 + 写入预算 + 热协调**」模式，而非 drop-in SSD 替换 | 2027-06 前 | HBF 仍被当作 SSD 直接替换部署 |
| P5 | NITRO 类 NAND-PIM ISC 2027 前无商用芯片落地（停留在学术原型） | 2027-12 前 | 出现商用 NAND-PIM 推理产品 |
| P6 | 「**决策留在设备**」进入主流 GPU agent runtime（如 vLLM/TRT-LLM 服务端 Agent 模式） | 2027-12 前 | 无采纳，仍以 host 往返为主 |

---

## 参考来源

1. 🟢 arXiv:2608.12146 — [RoutePack](https://arxiv.org/abs/2608.12146)（08-12，Ant Group；本篇仅交叉引用，全文精读见本地 08-14 三线文档）
2. 🟢 arXiv:2608.11688 — [APEX: Adaptive Expert Prefetching for Memory-Efficient Edge MoE Inference](https://arxiv.org/abs/2608.11688)（08-12，ESWEEK/CODES 2026, IEEE TCAD；Kanani/Badawi/Ogras）
3. 🟢 arXiv:2608.11693 — [Spec Sheets Are Not Kernels: An ISA- and Source-Level Audit of INT8 Availability on NVIDIA Blackwell Ultra](https://arxiv.org/abs/2608.11693)（08-12，单作者 Teng-Ruei Chen，8 页）
4. 🟢 arXiv:2608.12123 — [Ready Cohorts: Bounding GPU Opportunity and Avoiding Host Round Trips in LLM-Agent Control](https://arxiv.org/abs/2608.12123)（08-12，单作者 Josef Liyanjun Chen，含形式化证明+复现附录）
5. 🟢 arXiv:2608.11920 — [NITRO: High-Performance 3D NAND Flash-Based In-Storage Computing with Enhanced Activation Dataflow](https://arxiv.org/abs/2608.11920)（08-12，DATE 2026 扩展稿）
6. 🟢 arXiv:2608.11668 — [HBF Sucks! A Full-Stack Characterization of High-Bandwidth Flash for KV-Centric LLM Serving](https://arxiv.org/abs/2608.11668)（08-12/v2 08-13，13 页 12 图）
7. 🔵 本地知识库：2026-08-14 RL 三线文档（[RoutePack 全文精读](../../03_AI/llm-techniques-principles/2026-08-14-rl-posttraining-scheduling-battlefield-misa-tiderl-routepack-deep-analysis.md)）、闪存级 KV 卸载实证、量化检测四层法、TensorCast 控制面分离
8. ⚠️ **信息缺口**：① 6 篇均未读 HTML/PDF 全文（技术细节为摘要级推断，🟡 标注）；② Spec Sheets 性能测量未发布（companion study in preparation）；③ Ready Cohorts 的 joined online runtime 未实现；④ APEX stall-free 精度数字未披露

## Changelog

- 2026-08-14: v1.0 创建——2026-08-12/13 arXiv 批次 5+1 篇 AI 基础设施效率论文深度分析（APEX/Spec Sheets/Ready Cohorts/NITRO/HBF 新建 + RoutePack 交叉引用）；含四层撤退表/成本收益模型/持久 vs transient KV 分水岭对照/6 条可证伪预测 ([AI])
