# 🔬 专题 10：AI 模型架构对硬件的反推

> **概要**: MoE 架构对硬件的反推：MLA+MoE 让优化重心从注意力转向互联带宽
>
> **关键词**: MoE · 硬件影响 · AlltoAll · 负载均衡 · 3D 集成

---

## 📑 目录

- [📋 跟踪框架](#跟踪框架)
  - [需要持续回答的问题](#需要持续回答的问题)
  - [第一轮信息聚合（2026-05-28 完成）](#第一轮信息聚合2026-05-28-完成)
  - [关联文档](#关联文档)
  - [跟踪来源（含 URL）](#跟踪来源含-url)
  - [搜索关键词集（供定时任务使用）](#搜索关键词集供定时任务使用)
- [📝 最新发现](#最新发现)
  - [YYYY-MM-DD](#yyyy-mm-dd)
  - [2026-05-31（搜索更新）](#2026-05-31搜索更新)
  - [2026-05-30（搜索更新）](#2026-05-30搜索更新)
  - [2026-05-28（初始收集）](#2026-05-28初始收集)
- [🔗 关联知识](#关联知识)
  - [2026-06-03](#2026-06-03)
  - [📌 MoE 架构对硬件影响跟踪（2026-06-23 更新）](#moe-架构对硬件影响跟踪2026-06-23-更新)
    - [🅰 瓶颈重新定义：MLA+MoE 让硬件优化重心从「注意力加速」转向「互联带宽」](#瓶颈重新定义mlamoe-让硬件优化重心从注意力加速转向互联带宽)
    - [🅱 硬件感知 MoE 推理：GPU 制造差异的首次显式建模](#硬件感知-moe-推理gpu-制造差异的首次显式建模)
    - [🅲 3D 集成 + 近存计算：MoE 专用硬件加速](#3d-集成-近存计算moe-专用硬件加速)
    - [🅳 MoE 通信标准化与优化](#moe-通信标准化与优化)
    - [🅴 MoE 路由与预测性调度](#moe-路由与预测性调度)
    - [🅵 生产级 MoE 训练系统](#生产级-moe-训练系统)
    - [🅶 MoE 的跨数据中心可扩展性](#moe-的跨数据中心可扩展性)
    - [🅸 可配置优化与 Benchmarking](#可配置优化与-benchmarking)
- [🔗 关联知识](#关联知识)
- [🆕 2026-06-24 追加：6 篇 MoE 硬件新论文（arXiv 6 月发布）](#2026-06-24-追加6-篇-moe-硬件新论文arxiv-6-月发布)
  - [📐 新范式：MoE 训练/推理基础设施架构重构](#新范式moe-训练推理基础设施架构重构)
    - [🆕 FoMoE：打破全复制范式的 MoE 联邦训练（arXiv:2606.19025, 2026-06）](#fomoe打破全复制范式的-moe-联邦训练arxiv260619025-2026-06)
    - [🆕 ASAP：面向 MoE Prefill 的异步解耦推理系统（arXiv:2606.22541, 2026-06-21）](#asap面向-moe-prefill-的异步解耦推理系统arxiv260622541-2026-06-21)
  - [⚖️ 负载均衡：从「基于历史」到「实时精确」](#负载均衡从基于历史到实时精确)
    - [🆕 UltraEP：RSN 上近最优实时均衡（arXiv:2606.04101, 2026-06-02/18）](#ultraeprsn-上近最优实时均衡arxiv260604101-2026-06-0218)
    - [🆕 ForeMoE：微步级 MoE 负载均衡在 RL Post-training（arXiv:2606.11867, 2026-06-10）](#foremoe微步级-moe-负载均衡在-rl-post-trainingarxiv260611867-2026-06-10)
  - [🔬 方法论/诊断/可靠性新视角](#方法论诊断可靠性新视角)
    - [🆕 DODOCO：MoE Dispatch 瓶颈的跨架构诊断（arXiv:2605.20982, 2026-05-20）](#dodocomoe-dispatch-瓶颈的跨架构诊断arxiv260520982-2026-05-20)
    - [🆕 EEP：大规模 EP 中部分故障的自愈通信层（arXiv:2605.10670, 2026-05-11）](#eep大规模-ep-中部分故障的自愈通信层arxiv260510670-2026-05-11)
  - [🆕 FEPLB：NVLink Copy Engine 实现「近乎免费」的 MoE 负载均衡（arXiv:2604.19654, 2026-04-21）](#feplbnvlink-copy-engine-实现近乎免费的-moe-负载均衡arxiv260419654-2026-04-21)
  - [🆕 FoE：KV-head 级集群化消除 MoE AlltoAll 通信（arXiv:2605.06206, 2026-05-07）](#foekv-head-级集群化消除-moe-alltoall-通信arxiv260506206-2026-05-07)
  - [🆕 AFD 设计空间探索：MoE 推理解聚到哪一层？（arXiv:2605.28302, 2026-05-27）](#afd-设计空间探索moe-推理解聚到哪一层arxiv260528302-2026-05-27)
  - [🆕 CRAFT：细粒度成本感知 Expert 复制（arXiv:2603.28768, MLSys 2026）](#craft细粒度成本感知-expert-复制arxiv260328768-mlsys-2026)
  - [🆕 UCCL-EP：跨异构平台的 MoE 通信可移植性（arXiv:2512.19849, 2025-12）](#uccl-ep跨异构平台的-moe-通信可移植性arxiv251219849-2025-12)
  - [🆕 3D CPO 加速 MoE 训练：2.7× time-to-train 缩减（arXiv:2510.15893, HotI 2025）](#3d-cpo-加速-moe-训练27-time-to-train-缩减arxiv251015893-hoti-2025)
- [🔗 关联知识（2026-06-25 追加）](#关联知识2026-06-25-追加)
- [🔗 关联知识（2026-06-24 追加）](#关联知识2026-06-24-追加)
- [🆕 2026-06-26 追加：3 篇 MoE 硬件新论文（arXiv 6/22-6/25 新提交）](#2026-06-26-追加3-篇-moe-硬件新论文arxiv-622-625-新提交)
  - [🅰 运行时并行度切换：Moebius 打破 TP 与 EP 的非此即彼](#运行时并行度切换moebius-打破-tp-与-ep-的非此即彼)
  - [🅱 235B MoE→双 A100 的 75% 内存压缩：硬件感知压缩方法论](#235b-moe双-a100-的-75-内存压缩硬件感知压缩方法论)
  - [🅲 35B MoE 在 2011 Fermi GPU 上运行的极端案例分析](#35b-moe-在-2011-fermi-gpu-上运行的极端案例分析)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

---

## 📋 跟踪框架

### 需要持续回答的问题

| 问题 | 当前答案（2026-05，经交叉验证） | 证据来源 | 待验证 |
|:-----|:--------------------------------|:---------|:-------|
| **MoE AlltoAll 对网络拓扑的要求？** | 拓扑感知路由 > 拥塞控制（郑嘉琦，微信文章汇编）。从第一性原理分析：MoE 的 AlltoAll 通信模式是稀疏 collect，不产生 AllReduce 那样的全局同步热点，但对交换机 radix 要求更高——每个 Expert 可能跨不同节点，需要无阻塞全互联 | 郑嘉琦 QA 汇编; [Multi-GPU 集合通信分析](../../02_rd/01_product/01_software/04-comm-lib/2026-06-04-multi-gpu-collective-communications.md) | 用量化数据验证 AlltoAll vs AllReduce 带宽需求差异 |
| **MoE 推理 vs 训练硬件需求差异？** | 训练的 AlltoAll Expert 部署已知所有 Expert，通信模式可预先优化；推理时 Expert 动态激活（Top-2/Top-4），路由不确定性更大。第一性原理：推理 MoE 对设备间通信带宽需求低于训练，但对路由延迟更敏感 | 逻辑推论，需实验验证 | 实测数据 |
| **Agent 推理对硬件的新需求？** | TriAxialKV（arXiv 2026-05）首次量化了 Agent 推理的 KV Cache 特征：Agent 工作负载产生三维不等距 KV Cache（时间×模态×语义角色）；HexAGenT（arXiv 2026-05）提出 Agent 多步推理的工作流感知调度。第一性原理：Agent 多步推理 → KV Cache 持久化需求↑ → 对远端存储依赖性↑ | [TriAxialKV](https://arxiv.org/abs/2605.17170); [HexAGenT](https://arxiv.org/abs/2605.16637) | Agent 推理的 token 量统计 |
| **长上下文（128K-1M+ tokens）硬件瓶颈？** | 2026年5月 arXiv 大量论文聚焦 KV Cache 溢出方案：CacheTune 报告 SSD/HDD 存储 KV Cache 时 TTFT 加速 2.34-2.36×（通过自适应重计算）；ObjectCache 在 64K 上下文通过对象存储增加 5.6% 延迟，而 4K 时增加 56-75ms。第一性原理：Attention O(n²) 计算开销在长上下文时不是瓶颈，KV Cache 的 I/O 带宽才是 | [CacheTune](https://arxiv.org/abs/2605.24022); [ObjectCache](https://arxiv.org/abs/2605.22850); [LLM Inference: Bottleneck（NVIDIA）](https://semiengineering.com/llm-inference-core-bottlenecks-imposed-by-memory-compute-capacity-synchronization-overheads-nvidia/) | 在更大参数模型（>100B）上的验证 |
| **Dense vs MoE 模型未来选择趋势？** | 从第一性原理分析：Dense 模型训练/推理架构简单、工程稳定，但计算量 O(N²)；MoE 理论效率高但通信依赖重、路由不确定性。当前趋势：DeepSeek V3/R1 验证了大规模 MoE 的可行性，Qwen3 系列也混合了 Dense 和 MoE 两种方案。工业界尚未收敛 | [DeepSeek V3 论文](https://arxiv.org/abs/2412.19437); Qwen3 技术报告 | 更多模型发布确认路线 |
| **Vibe Coding/Agentic Coding 对算力需求影响？** | 从逻辑推演：Agentic Coding（自动多次调用模型进行编码/测试/修复）将推理 token 量提升 10-100×（相比单次对话），且产生结构化 KV Cache（跨回合复用）。这间接增加对 GPU 算力和内存的需求，但不易量化 | TriAxialKV Agent 分析 | 实际用户数据的 token 消耗统计 |

### 第一轮信息聚合（2026-05-28 完成）

**MoE 通信模式分析**（第一性原理推导 vs 文献验证）：

1. **出发点**：Transformer 的 Attention 计算是 O(n²) 但 FLOPs 只占总计算的一部分。MoE 引入 Expert 路由，产生 AlltoAll 通信
2. **通信特征**：AlltoAll 是「每个 Expert 接收一部分 Token」，不产生全局同步（AllReduce 那样），但要求交换机有足够的 radix 让每个 Expert 直接可达
3. **物理推论**：MoE 场景下对交换机带宽的总需求低于 AllReduce 场景，但对交换机拓扑的灵活性要求更高——这意味着 PCIe Switch 和 NVSwitch 都可能成为瓶颈
4. **验证**：郑嘉琦的结论「拓扑感知路由 > 拥塞控制」与上述推论一致。Astera Labs Hypercast™ 的集合操作加速对 Allreduce 场景更有效，对 AlltoAll 的加速效果待评估

**Agent 推理对存储架构的反推**：

1. **逻辑链**：Agent 是多次 LC（长上下文）推理的序列 → 各步之间 KV Cache 可以复用但 Token 内容变化 → 缓存命中率不是 100% → 需要更大的 DRAM/更快的传输通道
2. **论文验证**：TriAxialKV 和 HexAGenT 的量化数据支持上述推论

### 关联文档

> 🔗 **[GPU 芯片设计深度分析](../../02_rd/04_chip/base/2026-06-26-gpu-chip-design-analysis.md)**（2026-06-10 新增）— 基于本专题 80+ 条 arXiv 论文证据，给出了训练/推理 GPU + MoE 视角下的完整芯片设计建议、决策矩阵和优先级清单。涵盖 qs 不等式对硬件路线的冲击、核中核推理架构提案等关键设计决策分析。

### 跟踪来源（含 URL）

- [arXiv:2605.17170 TriAxialKV](https://arxiv.org/abs/2605.17170) — Agent 工作负载 KV Cache 分析
- [arXiv:2605.16637 HexAGenT](https://arxiv.org/abs/2605.16637) — Agent 工作流调度
- [arXiv:2605.24022 CacheTune](https://arxiv.org/abs/2605.24022) — 长上下文 KV Cache 存储
- [arXiv:2605.22850 ObjectCache](https://arxiv.org/abs/2605.22850) — 对象存储 KV Cache
- [arXiv:2605.23389 AlignedServe](https://arxiv.org/abs/2605.23389) — 前缀感知批处理
- [arXiv:2605.17613 VeriCache](https://arxiv.org/abs/2605.17613) — 无损 KV Cache 压缩
- [NVIDIA LLM Inference Bottlenecks](https://semiengineering.com/llm-inference-core-bottlenecks-imposed-by-memory-compute-capacity-synchronization-overheads-nvidia/)
- [华为 MindSpore HyperParallel](https://www.mindspore.cn/)

### 搜索关键词集（供定时任务使用）

```text
# monthly must-search - academic first-hand sources prioritized
"MoE all-to-all communication pattern site:arxiv.org"
"LLM inference KV cache memory hierarchy site:arxiv.org"
"agentic reasoning hardware requirements site:arxiv.org OR site:semiengineering.com"

# rotate on demand
"Mixture of Experts communication bandwidth analysis"
"Dense vs MoE model comparison 2026"
"long context LLM inference memory bottleneck"
"vLLM MoE support update"
```

---

## 📝 最新发现

> 此章节由定时任务自动更新

```text
### YYYY-MM-DD

Source: [title](URL) (primary/secondary, access date)
Finding: [1-3 lines, quant data if any]
Reasoning chain: [fact -> inference -> conclusion]
Impact: [impact on hardware design direction]
Verification: [cross-verified / pending / single source]

---
```

> 中文说明：跟踪条目的标准字段模板（来源/发现/推理链/影响/验证状态），由定时任务按此结构填充每日更新。

### 2026-05-31（搜索更新）

**来源**: [NIMBLE: From Skew to Symmetry — Multi-Path Balancing for GPU Clusters](https://arxiv.org/abs/2604.00317)（一手，arXiv 2026-03-31）
**发现**: NIMBLE 提出运行时通信编排系统，通过容量归一化的最小拥塞优化模型（multiplicative-weights 算法）动态平衡所有 intra-node 和 inter-node 路径的流量。在 H100-SXM4（全互联 NVLink + 4×NDR400）上，MoE All-to-Allv 场景比 NCCL 和 MPI 提升 **5.2×**，端到端 LLM MoE 工作负载提升 **1.35×**。 [来源: arXiv:2604.00317]
**推理链**: 流量歪斜是 MoE AlltoAll 利用率低的根本原因 → 运行时动态均衡比静态路由更有效 → 软件优化的作用可以与硬件升级互补
**影响**: 再次确认 MoE 场景下「软件负载均衡」可以显著提升通信效率，与 RailS 论文结论一致。对硬件设计启示：不需要极致对称的全连接网络，软件补偿可以平滑硬件非对称性。
**验证状态**: 单一来源，实验数据充分

---

**来源**: [Comparative Characterization of KV Cache Management Strategies for LLM Inference](https://arxiv.org/abs/2604.05012)（一手，arXiv 2026-04-06）
**发现**: 系统比较了三种主流 KV Cache 管理框架（vLLM/tensor offloading, InfiniGen/token eviction, H2O/speculative scheduling），给出了不同 request rate、模型大小和稀疏度条件下的最优选择。vLLM 的 tensor offloading 在高并发时内存效率最优，InfiniGen 的 token eviction 在低内存场景优势显著。
**推理链**: 没有通用的最优 KV Cache 管理策略 → 需要根据工作负载特征动态选择 → 硬件设计应为多种策略提供灵活支持
**影响**: KV Cache 管理的「单一方案」思路不可行。硬件需要同时支持 offloading（高带宽远端存储）和 eviction（快速压缩/淘汰）两种模式，这对 CXL 内存池和 JBOF 的接口设计有指导意义。
**验证状态**: 单一来源，实验设计合理

---

**来源**: [Heterogeneous Computing: Powering the Future of AI Agent Inference](https://arxiv.org/abs/2601.22001)（一手，arXiv 2026-01-29，与上月重复但获取到完整细节）
**发现**: 深入阅读完整论文后确认：OI（Operational Intensity）指标显示 Agent 推理的 decode 环节 OI < 0.5（极度 memory bound），而 prefill 阶段 OI > 10。CF（Capacity Footprint）指标量化了 KV Cache 的内存压力——单次 Agent 推理会话可产生 GB 级 KV Cache。
**推理链**: Agent 推理由多轮长上下文组成 → decode OI < 0.5 → 需解耦计算与内存 → 光 I/O 和 CXL 内存池是最佳匹配
**影响**: ⚠️ OI/CF 双指标框架可作为 Agent 推理硬件的标准化评估工具。对硬件产品定位有直接指导——prefill 需要高计算密度，decode 需要高内存带宽+大容量，两者分离设计是必然趋势。
**验证状态**: 一手来源，指标体系设计合理

---

**来源**: [The Verge — AI 行业动态](https://www.theverge.com/ai-artificial-intelligence)（二手，2026-05-31）
**发现**:

1. **Anthropic $65B Series H, $965B 估值**：资金投向安全研究、算力扩展、产品规模化。新模型更"诚实"，出错时承认不确定性
2. **Microsoft AI Super App**：整合所有 Copilot 产品（GitHub Copilot/Chat/Cowork/Autopilot），拟 Microsoft Build 2026 展示
3. **OpenAI Codex 扩展到 Windows**：计算机使用功能可"看到"屏幕执行任务
4. **Illinois AI 安全法案**：要求独立审计和 whistleblower 保护，超出纽约/加州范围
5. **Google AI Overviews 质量问题**：DuckDuckGo iOS 安装量环比增长 33%
6. **Robinhood 允许 AI Agent 自动交易股票**
**影响**: Microsoft Super App 将对独立 AI 工具（Cursor/Claude Code）形成平台挤压。Illinois 法案的独立审计要求将影响企业 AI 部署合规路径。Google AI 搜索质量危机为竞品创造窗口。
**验证状态**: 二手来源，多源交叉验证

---

### 2026-05-30（搜索更新）

**来源**: [DODOCO: Decoding the Dispatch Dynamics of Mixture-of-Experts Models](https://arxiv.org/abs/2605.20982)（一手，arXiv 2026-05-20）
**发现**: MoE AlltoAll 的 straggler 是模型自身路由决策固有的，与 Expert 在 rank 上的布局无关。五种架构分成两档路由不均分布：(1) MHA/Mamba-2（Gini 0.105-0.150）vs (2) MLA/GDN（Gini 0.24-0.38）。Mock token 会高估路由 Gini 高达 2.35×。动态调整 expert 映射到 rank 可减少 40% 的路由不均。 [来源: arXiv:2605.20982]
**推理链**: 路由不均 = 模型架构固有属性 → 不能通过调整 expert 布局消除 → 需要硬件层面容忍/利用这种模式
**影响**: ⚠️ 重大！MoE 互联设计应以真实路由特征（两档分布）为输入。此前认为路由不平衡可由系统层纠正的假设被证伪。MLA/GDN 架构需要更激进的负载均衡策略。
**验证状态**: 单一来源（需要交叉验证其他 MoE 实测数据）

---

**来源**: [Rethinking Network Topologies for Mixture-of-Experts](https://arxiv.org/abs/2605.00254)（一手，arXiv 2026-04-30）
**发现**: 3D full-mesh 拓扑 Pareto 最优，比 scale-up 拓扑成本效益提升 20.6-56.2%。当前 scale-up 链路带宽过度供给，降低 27% 带宽后每美元吞吐反而提升。 [来源: arXiv:2605.00254] MoE traffic 的稀疏性意味着不需要全带宽 scale-up fabric。
**推理链**: 3D full-mesh 替代 scale-up → 降低 27% 带宽不降吞吐 → switchless 拓扑更优
**影响**: ⚠️ 重大！直接挑战「高价 scale-up 网络是 MoE 必需品」的行业共识。Switchless 拓扑 + 更低带宽可能是更优解——这对 AI 服务器整机架构设计有直接影响。
**验证状态**: 单一来源（需在其他 MoE 规模验证）

---

**来源**: [NCCL EP: Expert Parallelism in NCCL](https://arxiv.org/abs/2603.13606)（一手，arXiv 2026-03-13）
**发现**: NVIDIA 推出 NCCL 原生的 MoE 通信库 NCCL EP，支持 LL（1-128 tokens, 直接 all-to-all RDMA+NVLink）和 HT（4096+ tokens, 分层通信）两种模式，已集成 vLLM。在 8×H100 上 MoE 通信性能比 DeepEP 提升 20-40%。 [来源: arXiv:2603.13606]
**推理链**: NVIDIA 统一 MoE 通信生态 → 第三方库（DeepEP/Hybrid-EP）面临被官方替代风险 → 硬件层面 NVLink 和 RDMA 的配合更加关键
**影响**: NVIDIA 正在通过 NCCL EP 掌控 MoE 通信栈。对于非 NVIDIA 平台，需要提供等效的 EP 原语。LL 模式下全 RDMA/NVLink 直接通信，对网络延迟极度敏感。
**验证状态**: 一手来源，代码已开源

---

**来源**: [Heterogeneous Computing for AI Agent Inference](https://arxiv.org/abs/2601.22001)（一手，arXiv 2026-01-29）
**发现**: 提出 OI（Operational Intensity）和 CF（Capacity Footprint）两个新指标刻画 Agent 推理特征。Agent 推理的长上下文 KV Cache 使 decode 环节严重 memory bound（OI < 1），需要解耦计算-内存（光 I/O）。prefill 阶段 OI 较高（> 10），decode 阶段极低（< 0.5）。
**推理链**: Agent 推理由多轮 long-context 组成 → decode memory bound 极端化 → 需要计算-内存解耦架构
**影响**: Agent 推理将推动异构计算（专用 prefill/decode 加速器）+ 内存解耦 + 光互联。这为 CXL 内存池、JBOF、光互联方案提供了强需求证据。
**验证状态**: 一手来源，指标体系设计合理

---

**来源**: [Deconstructing Pre-training: MoE vs Dense Models](https://arxiv.org/abs/2601.08383)（AAAI 2026，一手，arXiv 2026-01-30）
**发现**: (1) MoE 模型前 1% 的神经元捕获 > 45% 的正向更新，Dense 模型没有此现象；(2) MoE 在 < 100K steps 内锁定稳定重要性分布，Dense 全程波动；(3) MoE 的功能鲁棒性是 Dense 的 5×；(4) MoE 的知识获取是「集中式积累」模式，Dense 是「分布式扩散」。 [来源: arXiv:2601.08383]
**推理链**: MoE 架构具有内在稳定性优势 → 工业界向 MoE 收敛得到理论支撑 → 需为 MoE 设计专用硬件
**影响**: 从知识获取动力学角度为 MoE 路线提供了理论支撑。进一步确认 Dense→MoE 是长期趋势，而非短期热点。
**验证状态**: 一手来源，AAAI 2026 会议论文

---

**来源**: [RailS: Load-balanced AlltoAll for MoE](https://arxiv.org/abs/2605.22990)（一手，arXiv 2026-05-28）
**发现**: 在 Rail 拓扑上利用 expert 路由统计信息做前瞻性负载均衡，批量大小 256-1024 时性能最优，迭代时间缩短 18-40%。 [来源: arXiv:2605.22990]
**推理链**: Rail 拓扑 + 软件负载均衡 → 避免 AlltoAll straggler → 无需高价全连接网络
**影响**: 与 Rethinking Networks 论文结论一致——低连接度拓扑 + 软件优化可以在 MoE 场景下取得接近全连接的性能。
**验证状态**: 一手来源，最新论文（5月28日）

---

**来源**: [FoE: The First All-to-All Free MoE Training](https://arxiv.org/abs/2605.23767)（一手，arXiv 2026-05-28）
**发现**: 通过强制 token-expert affinity + 两层 FFN 的局部计算 + 周期性 rebalancing，彻底消除 all-to-all 通信，延迟降低 5.2×（vs DeepSpeed-MoE），与 dense 模型训练速度相当。 [来源: arXiv:2605.23767]
**推理链**: 消除 all-to-all 通信 → 不再需要高速互联 → 对网络拓扑要求大幅降低
**影响**: ⚠️ 如果 FoE 方法可扩展到大模型，将对当前 MoE 互联方案产生颠覆性影响——不再需要 Scale-Up 高带宽网络。需关注该方法的扩展性和质量损失。
**验证状态**: 单一来源，最新论文，待验证可扩展性

---

**来源**: [EEP: Efficient Expert Parallelism with Partial Fault Tolerance](https://arxiv.org/abs/2604.14557)（一手，arXiv 2026-04-20）
**发现**: 提出 partial fault-tolerant EP，单节点故障后其余节点自动分担负载（不中断训练），故障恢复时间 52s vs 348s。引入 Stale Expert Group 机制，对 20% 以下节点故障容忍度接近零损失。 [来源: arXiv:2604.14557]
**推理链**: MoE 训练的容错性可大幅提升 → 降低对单节点可靠性的要求 → 改变硬件可靠性设计目标
**影响**: MoE 训练对硬件可靠性的要求可能低于预期——不必追求 99.999% 单节点可靠性，而是利用 EP 的天然容错性。
**验证状态**: 一手来源

---

**来源**: [PRISM: Photonic KV Cache Block Selection at O(1)](https://arxiv.org/abs/2605.17095)（一手，arXiv 2026-05-20）
**发现**: 利用光子计算对 KV Cache block 做重要性排序（O(1) 复杂度），选择关键块进入 HBM 做精确 KV cache 量化，与 TriAxialKV 思路互补。
**推理链**: 光子 KV 选择 + 量化 → 突破 KV Cache 的内存墙 → 降低对 HBM 容量的依赖
**影响**: 光子计算在推理场景中找到了具体入口——KV Cache 管理。这可成为光子计算进入数据中心的具体切入点。
**验证状态**: 单一来源

### 2026-05-28（初始收集）

**来源**: [TriAxialKV: Toward Extreme Low-Precision KV-Cache Quantization for Agentic Inference](https://arxiv.org/abs/2605.17170)（一手，arXiv 2026-05）
**发现**: Agent 推理工作负载的 KV Cache 呈三维不等距结构：(1) 时间维度：近期回合更敏感；(2) 模态维度：图像 token 与文本 token 不同；(3) 语义角色：用户查询 vs 工具调用 vs 观察结果。混合 INT2/INT4 量化后匹配 BF16 精度，KV Cache 缩小 4.5×，吞吐提升 30% [来源: arXiv:2605.17170]
**推理**: 如果 Agent 工作负载成为主要推理类型（目前趋势看），KV Cache 的「三维不均等」结论对 CXL 内存池和 JBOF 的设计有直接影响——只有某些层的某些 token 需要高精度，其他可以压缩到远端。这意味着 不一定需要所有 KV Cache 都以 HBM 速度访问
**影响**: 远端 KV Cache 存储的产品设计可以更激进——考虑 tiered precision（非 tiered speed）的架构

---

## 🔗 关联知识

### 2026-06-03

**来源**: [Attention-FFN Disaggregation (AFD) for Efficient MoE LLM Serving](https://arxiv.org/abs/2605.28302)（一手，arXiv 2026-05-27）
**发现**: 提出 Operator-level Attention-FFN Disaggregation (AFD) 用于 MoE 推理——将 attention 和 MoE-FFN 分别放在不同 GPU 组上执行。在 DeepSeek-V3.2 上以严格 TTFT/TPOT SLO 约束，AFD 维持约 4k tokens/s 系统吞吐，非 AFD 部署不可行。 [来源: arXiv:2605.28302] AFD 进一步暴露了 attention（memory-bound）、FFN（compute-bound）和 MoE dispatch/combine（通信敏感）的 heterogeneity。
**推理链**: MoE 推理中 attention 与 FFN 的资源需求异质 → AFD 分离执行 → 对 GPU 互联提出跨组高效通信需求
**影响**: 这是 MoE 推理调度的重要突破。从超节点设计角度看，AFD 意味着 GPU 组之间需要比 P/D 分离更灵活的互联——attention GPU 组需要访问共享 KV Cache，FFN GPU 组需要低延迟 AlltoAll，对 Scale-Out 网络提出新要求。

---

**来源**: [The qs Inequality: Double Penalty of MoE at Inference](https://arxiv.org/abs/2603.08960)（一手，arXiv 2026-03-09）
**发现**: 提出 qs 不等式量化 MoE 推理的「双重惩罚」：(1) expert routing 碎片化 minibatch，降低 weight reuse；(2) 大量 resident expert 占用 HBM 空间挤压 KV Cache。对 DeepSeek-V3 在 128k 上下文，质量匹配的 Dense 模型吞吐比 MoE 高 4.5×。 [来源: arXiv:2603.08960] 大规模架构如 Switch-C 在集群上可能不可行，而质量匹配的 Dense 模型仍可运行。
**推理链**: MoE 训练效率高 → 推理效率低（qs 不等式）→ Dense 模型在长上下文推理中有结构性优势
**影响**: ⚠️ 重要发现。这是从理论角度证明 MoE 在长上下文推理中处于结构性劣势，与工业界 Dense→MoE 的单一收敛方向形成矛盾。建议 MoE 被视为「训练优化」，蒸馏为 Dense 模型做推理部署。这对硬件规划影响深远——如果长期趋势是 MoE→Dense（推理端），则 AlltoAll 通信优化的重要性将下降。

---

**来源**: [SpaceMoE: Distributed MoE Inference over Satellite Networks](https://arxiv.org/abs/2605.00515)（一手，arXiv 2026-05-01）
**发现**: 在千星卫星星座上分布式部署 MoE 模型。两层放置策略：(1) 层放置：MoE 层分配到卫星子网；(2) intra-layer expert 放置：频繁激活的专家映射到低延迟路由路径。在千星规模延迟降低 3×。 [来源: arXiv:2605.00515]
**影响**: 卫星数据中心的 MoE 推理是超前课题，但验证了 expert placement 优化在非理想网络拓扑下的通用价值——专家路由必须感知拓扑。

---

**来源**: [CacheTune: Adaptive KV Cache Reuse for Fast Long-Context LLM Serving](https://arxiv.org/abs/2605.24022)（一手，arXiv 2026-05-20）
**发现**: 通过频域分析识别 KV pairs 的关键性，选择性重算语义关键 token 而非直接复用。结合稀疏 KV 传输、多流异步重叠、延迟 PE 恢复和硬件感知自适应重算比调优。TTFT 加速 3.72-4.86×，吞吐提升 3.93-6.21×。即使在 SSD/HDD 上 offload，仍维持 2.34-2.36× TTFT 加速。 [来源: arXiv:2605.24022]
**影响**: KV Cache 重用正在从「严格前缀匹配」走向「语义感知选择性重算」。这降低了对 GPU HBM 容量的硬性需求——更多 KV Cache 可以 offload 到远端存储层级，但需要智能重算策略配合。利好 CXL 内存池和 JBOF 方案。

---

**来源**: [VeriCache: Turning Lossy KV Cache into Lossless LLM Inference](https://arxiv.org/abs/2605.17613)（一手，arXiv 2026-05-17）
**发现**: 用压缩 KV Cache draft token，用 full KV Cache verify。关键洞察：压缩 KV 解码（HBM bandwidth bound）和 full KV swap（PCIe/network bound）可并行化。在长上下文解码和远端 prefix caching 中都证明了有效性，吞吐达 4×。 [来源: arXiv:2605.17613]
**影响**: ⚠️ 这是 KV Cache 压缩可验证的突破——首次保证 lossless 输出（与 full KV 完全相同）的同时维持高吞吐。如果此范式被采纳，KV Cache 压缩（量化/dropping）的企业级部署障碍将大幅降低。对硬件影响：full KV Cache 可以安全地放在低成本存储中（如 CXL 内存或 SSD），只需在 verify 阶段 swap 进来。

---

**来源**: [Salca: Sparsity-Aware Hardware Accelerator for Long-Context Attention Decoding](https://arxiv.org/abs/2604.24820)（一手，arXiv 2026-04-27）
**发现**: 首个高效支持长上下文推理的 ASIC 加速器。通过 dual-compression dynamic sparse attention + 硬件友好的 Top-K 近似选择，3.82× 加速、74.19× 能效提升 vs A100。 [来源: arXiv:2604.24820] 采用全流水线并行架构实现 O(n) 效率。
**影响**: 长上下文推理的 ASIC 方案正在出现。72× 能效提升意味着通用 GPU 在长上下文推理场景中能效劣势显著，专用加速器（如 Cerebras、Groq 和新兴长上下文 ASIC）有望在长期推理工作负载中占据优势。

---

**来源**: [HybridGen: Efficient LLM Inference via CPU-GPU Hybrid Computing with CXL Memory](https://arxiv.org/abs/2604.18529)（一手，arXiv 2026-04-20）
**发现**: 在 CXL 扩展内存系统上实现 CPU-GPU 协同注意力计算。提出 attention logit 并行性、feedback-driven scheduler、语义感知 KV Cache 映射。在三种 GPU 平台上比 SOTA 方法提升 1.41-3.2×。 [来源: arXiv:2604.18529]
**影响**: CXL 内存池在长上下文推理中的价值进一步验证。CPU（或 CXL 内存控制器附近的计算单元）可承担部分注意力计算，减轻 GPU 的 KV Cache 带宽压力。这是 CXL 内存池产品设计的强有力论据。

---

**来源**: [SinkRouter: Sink-Aware Routing for Efficient Long-Context Decoding](https://arxiv.org/abs/2604.16883)（一手，arXiv 2026-04-18）
**发现**: attention sink 现象对应训练中构建的稳定可达到的定点。提出 training-free selective routing 框架，检测 sink signal 跳过近零输出的计算。512K 上下文下 2.03× 加速。 [来源: arXiv:2604.16883]
**影响**: attention sink 现象从「需处理的问题」变为「可利用的特性」。训练感知的硬件设计可进一步利用 sink 机制减少计算量。

---

**来源**: [FAST-Prefill: FPGA Accelerated Sparse Attention for Long Context LLM Prefill](https://arxiv.org/abs/2602.20515)（一手，arXiv 2026-02-23）
**发现**: 首个长上下文 prefill 阶段 FPGA 加速器。提出 fused pipeline unit + memory-aware 执行顺序、liveness-driven dual-tier cache、hybrid Matrix Processing Unit（DSPs + LUTs bit-plane decomposition）。在 Alveo U280 上 TTFT 加速 2.5×、能效提升 4.5× vs A5000 GPU。
**影响**: FPGA 在长上下文 prefill 阶段的能效优势显著（4.5×）。对于短上下文占比低的推理场景，FPGA 可作 prefill 专用加速器方案。

---

**来源**: [PIMphony: PIM Orchestrator for Long-Context LLM Inference](https://arxiv.org/abs/2412.20166)（一手，接受 HPCA 2026）
**发现**: Processing-in-Memory (PIM) 方案在长上下文推理中面临 channel 利用率低下、I/O 瓶颈和静态 KV Cache 内存浪费。提出 Token-Centric PIM Partitioning、Dynamic PIM Command Scheduling、Dynamic PIM Access Controller。在 1M 上下文下 PIM-only 系统吞吐提升 11.3×，xPU+PIM 系统 8.4×。
**影响**: PIM 架构在长上下文推理中有巨大潜力（11× 提升），但需要系统级编排而非简单的计算下移。PIM 可作为 KV Cache 处理的专用加速器。

---

### 📌 MoE 架构对硬件影响跟踪（2026-06-23 更新）

---

#### 🅰 瓶颈重新定义：MLA+MoE 让硬件优化重心从「注意力加速」转向「互联带宽」

**来源**: [Rethinking LLM Inference Bottlenecks: Insights from Latent Attention and Mixture-of-Experts](https://arxiv.org/abs/2507.15465)（一手，arXiv cs.AR, 2025-07, 2026-01 修订）
**发现**: 论文对 MLA（Multi-head Latent Attention）和 MoE 的算术密度（arithmetic intensity）做了系统性定量分析。两个关键结论：(1) MLA 的算术密度比 MHA 高出 **两个数量级**（>100×），从 memory-bound 彻底转变为 compute-bound，与现代 GPU 计算特性高度匹配；(2) 跨加速器分布 MoE experts 后，batch 处理可以调节其算术密度使其与 dense layers 相近，产生更均衡的计算剖面。
**影响**: ⚠️ **这是一个范式级别的论断**。如果 MLA+MoE 组合确实将注意力从 memory-bound 推向 compute-bound，那么过去五年专注 attention 加速（FlashAttention 等）的硬件设计方向需要重新审视。未来的硬件优化重心应转向：(1) **高带宽互联**（MoE All-to-All 通信瓶颈）; (2) **跨加速器的专家负载均衡**（处理 straggler）。这对网络架构（Rail-only vs Full-bisection）和互联技术（NVLink/NVSwitch/RDMA）选择产生直接影响。

---

#### 🅱 硬件感知 MoE 推理：GPU 制造差异的首次显式建模

**来源**: [ViBE: Co-Optimizing Workload Skew and Hardware Variability for MoE Serving](https://arxiv.org/abs/2606.00735)（一手，arXiv cs.DC, 2026-05）
**发现**: 首次显式建模 **GPU 硬件性能差异**（制造偏差、功耗限制、热条件）对 MoE 推理的影响。核心洞察：MoE 执行时间不平衡来自 **工作负载偏斜 × 硬件不对称** 的双重交互——即使 token 分配均衡，GPU 间执行速度差异仍造成 persistent stragglers。ViBE 提出 Variability-Informed Binning of Experts，将高负载专家分配给更快 GPU、低负载专家给更慢 GPU。结果：**SLO 达成率提升 14%**，**P90 TTFT 降低 45%**。
**影响**: ⚠️ **硬件差异在规模化时放大**——论文特别指出硬件可变性的影响在更大集群规模下更显著。这意味着：(1) MoE 推理系统不能假设同构硬件；(2) 专家放置需要「硬件感知」而非仅「负载感知」；(3) 对 GPU 制造品质一致性（binning）提出了更严格的要求。

---

#### 🅲 3D 集成 + 近存计算：MoE 专用硬件加速

**来源**: [Stratum: System-Hardware Co-Design with Tiered Monolithic 3D-Stackable DRAM for Efficient MoE Serving](https://arxiv.org/abs/2510.05245)（一手，arXiv cs.AR, 2025-10，接受 ASPLOS 2026）
**发现**: 提出 **Mono3D DRAM（单片 3D 堆叠 DRAM） + 近存处理（NMP） + GPU 加速** 的系统-硬件协同设计方案。Mono3D DRAM 利用单片结构实现比 HBM 更高的片内带宽（hybrid bonding 垂直互连）；沿 z 轴构建内部存储层级，按访问概率分层分配数据（基于 topic-based expert usage prediction）。结果：**解码吞吐提升 8.29×**，**能效提升 7.66×** vs GPU 基线。
**影响**: MoE 服务的专用硬件方案正在从学术走向工程化。Mono3D DRAM + NMP 的组合对 MoE 特别有效，因为专家权重可按活跃度分层存放，活跃 expert 放在最靠近计算的高带宽层，冷 expert 下沉。对 HBM 替代路径提供了新思路。

**来源**: [A3D-MoE: Acceleration of Large Language Models with Mixture of Experts via 3D Heterogeneous Integration](https://arxiv.org/abs/2507.19142)（一手，arXiv cs.AR, 2025-07）
**发现**: 另一个 3D 异构集成方案。核心创新：(1) **3D-Adaptive GEMV-GEMM 脉动阵列**，解决 MoE 推理中 Workload 导致的任意 GEMV/GEMM 比例问题（细粒度 MoE 的 GEMV-GEMM 比例波动降低硬件利用率）；(2) **操作融合调度器**，将 attention 与 MoE 操作融合减少延迟；(3) **MoE Score-Aware HBM 访问缩减**，通过 expert 奇偶放置减少 DRAM 访问。结果：**延迟降低 1.8-2×**，**能耗降低 2-4×**，**吞吐提升 1.44-1.8×**。
**影响**: 细粒度 MoE（DeepSeek-V3 等）引起的 **GEMV/GEMM 比例波动** 是一个被低估的硬件效率杀手。传统 GPU 的固定 systolic array 在变比例 workload 下利用率显著下降。A3D-MoE 的 adaptive array 思路指向了未来 AI 加速器设计的另一个维度——**动态可重构计算单元**。

---

#### 🅳 MoE 通信标准化与优化

**来源**: [NCCL EP: Towards a Unified Expert Parallel Communication API for NCCL](https://arxiv.org/abs/2603.13606)（一手，arXiv cs.DC, 2026-03, NVIDIA）
**发现**: NVIDIA 正在将 MoE  Expert Parallelism 通信原语化到 **NCCL Device API** 层。提供两模式：**Low-Latency（LL）模式**（1-128 tokens，direct all-to-all RDMA+NVLink mesh，double-buffered dispatch/combine 重叠）用于推理 decoding；**High-Throughput（HT）模式**（4096+ tokens，hierarchical communication，先 NVLink 域内聚合再 inter-node RDMA）用于训练/prefill。已集成 vLLM。
**影响**: ⚠️ **NVIDIA 正在统一 MoE 通信协议栈**。这意味着：(1) DeepEP、Hybrid-EP 等第三方库的差异化空间缩小；(2) MoE 通信性能将随 NCCL 版本自动升级，不再依赖框架层 hack；(3) 集群网络设计需支持 NCCL EP 的拓扑感知（NVLink domain + RDMA topology optimization）。

**来源**: [DisagMoE: Computation-Communication overlapped MoE Training via Disaggregated AF-Pipe Parallelism](https://arxiv.org/abs/2605.11005)（一手，arXiv cs.LG, 2026-05）
**发现**: 提出 **解聚的 MoE 训练架构**——将 attention 和 FFN 层分配到互斥的 GPU 组，引入多级流水线 + 单向 many-to-many 通信 + 计算-通信 roofline 模型平衡 GPU/网络带宽分配。在 Megatron-LM 上实现，在 16 节点 8×H800 集群上 **训练效率提升最高 1.8×**。
**影响**: 解聚（Disaggregation）思想正在从推理（PD分离）向训练渗透。Attention 和 FFN 的解聚分区意味着网络拓扑可以差异化设计——attention-heavy GPU 组需要高带宽互联（因为 self-attention 是 allreduce），而 FFN-heavy GPU 组需要 All-to-All 优化互联。这种分区可能推动未来的 AI 集群网络设计向 **异构拓扑** 演进。

**来源**: [MixServe: An Automatic Distributed Serving System for MoE Models with Hybrid Parallelism Based on Fused Communication Algorithm](https://arxiv.org/abs/2601.08800)（一手，arXiv cs.DC, 2026-01，投稿 ICDCS 2026）
**发现**: 提出 **TP-EP 混合并行 + 融合 AR-A2A 通信算法**。实现 intra-node AR（tensor parallelism）与 inter-node A2A（expert parallelism）的重叠执行。系统自动根据模型超参数和硬件网络配置选择最优并行策略。在 DeepSeek-R1 和 Qwen3 上：**TTFT 加速 1.08-3.80×**，**ITL 加速 1.03-1.66×**，**吞吐提升 5.2%-50.3%**。
**影响**: TP 和 EP 不是非此即彼——**混合并行是 MoE 推理的最优解**。关键是可融合通信算法（fused AR-A2A）的设计，这需要硬件层面支持 intra-node 和 inter-node 通信的同时执行（NVLink + RDMA 并行）。

**来源**: [Piper: Efficient Large-Scale MoE Training via Resource Modeling and Pipelined Hybrid Parallelism](https://arxiv.org/abs/2605.05049)（一手，arXiv cs.DC, 2026-05）
**发现**: 开发 MoE 配置的数学建模框架（量化 memory/compute/communication 需求），识别四大瓶颈：All-to-All 延迟、compute-communication overlap 不足、细粒度 GEMM 的 GPU 利用率低、缺少平台感知混合并行策略。Piper 框架实现：**2-3.5× MFU 提升 vs X-MoE**，新 All-to-All 算法提供 **1.2-9× 带宽 vs 厂商实现**。
**影响**: MoE 训练的系统性数学建模正在成熟。建立 memory/compute/communication 联合模型再做优化比试错调参更有效。All-to-All 算法的 9× 带宽差距表明，NVIDIA 的官方 All-to-All 实现仍有巨大优化空间。

**来源**: [UniEP: Unified Expert-Parallel MoE MegaKernel for LLM Training](https://arxiv.org/abs/2604.19241)（一手，arXiv cs.DC, 2026-04）
**发现**: 将 MoE 通信和计算融合为 **MegaKernel**，将复杂架构调优转化为统一的参数搜索空间。引入确定性 token 排序机制，保证 aggressive overlap schedule 下的数值一致性与顺序执行等价。在 Hopper GPU 上实现 **1.03-1.38× 加速**。
**影响**: MoE 通信-计算融合的 MegaKernel 抽象意味着系统实现可以从「hack 式优化」走向「统一参数调优」。这对框架层（PyTorch/Megatron）的集成友好度大幅提升。

---

#### 🅴 MoE 路由与预测性调度

**来源**: [PROBE: Co-Balancing Computation and Communication in MoE Inference via Real-Time Predictive Prefetching](https://arxiv.org/abs/2602.00509)（一手，arXiv cs.DC, 2026-01）
**发现**: 指出 MoE 推理面临 **"双重惩罚"**——计算偏斜（expert hotspots 突迁）+ 网络拥塞耦合。提出 Continuous Lookahead Pipelining：(1) Gate-Initialized Lookahead Predictor 蒸馏 router 预测下层 expert 激活；(2) Hardware-Aware Balance Planning 联合优化动态 expert 复制和 token 分配；(3) Phase-Locked Co-Scheduling 用 split-phase 传输将 expert 传输隐藏在计算后。结果：**prefill 延迟降低 1.32×**，**decoding 吞吐提升 1.26×**。
**影响**: ⚠️ **"语义漂移"导致的 expert hotspot 突迁是 MoE 推理的新挑战**——连续 batch 和多样请求导致 token 语义快速变化，expert 热度分布动态迁移。传统的静态 expert 放置策略失效。PROBE 的 predictive prefetching 思路（利用率 router 蒸馏进行超前预测）为 MoE 推理实时调度提供了可行方案。

**来源**: [FinDEP: Efficient MoE Inference with Fine-Grained Scheduling of Disaggregated Expert Parallelism](https://arxiv.org/abs/2512.21487)（一手，arXiv cs.DC, 2025-12）
**发现**: 对解聚专家并行（DEP——attention 和 expert 分配到专用 GPU 组）进行细粒度任务调度优化。将计算/通信拆分为更小的任务进行细粒度流水线化，支持变粒度和变序调度。在 DeepSeek-V2 和 Qwen3-MoE 上：**吞吐提升最高 1.61×**，32-GPU 系统上 **1.24× 加速**。
**影响**: 解聚架构（Disaggregated architecture）已成为 MoE 推理的主流方向之一。细粒度调度是释放 DEP 潜力的关键，这也意味着部署控制平面的复杂度上升。

---

#### 🅵 生产级 MoE 训练系统

**来源**: [Scalable Training of Mixture-of-Experts Models with Megatron Core](https://arxiv.org/abs/2603.07685)（一手，arXiv cs.DC, 2026-03, NVIDIA 88页技术报告）
**发现**: 系统描述 Megatron Core 中 MoE 训练的全栈优化——内存（细粒度重计算、offloading）、通信（优化 dispatcher、overlapping）、计算（Grouped GEMM、fusions、CUDA Graphs）。支持 FP8/NVFP4 低精度训练和 Parallel Folding 多维并行。在 GB300/GB200 上达到 **1,233/1,048 TFLOPS/GPU（DeepSeek-V3-685B）**、**974/919 TFLOPS/GPU（Qwen3-235B）**。
**影响**: 这是目前公开的最完善的 MoE 生产训练系统报告。1,233 TFLOPS/GPU 意味着 GB300 上 DeepSeek-V3-685B 的 **MFU 约 55-60%**（以 FP8 理论峰值~2,000+ TFLOPS 估算）。关键信息是：即使经过大幅优化，全栈协同设计也只能达到~55-60% MFU——MoE 的固有稀疏性导致的利用率损失依然显著。

---

#### 🅶 MoE 的跨数据中心可扩展性

**来源**: [HybridEP: Scaling Expert Parallelism to Cross-Datacenter Scenario via Hybrid Expert/Data Transmission](https://arxiv.org/abs/2510.19470)（一手，arXiv cs.DC, 2025-10）
**发现**: MoE 训练规模超出单 DC 后将面临跨 DC 低带宽瓶颈。HybridEP 提出将 expert 的空间放置（spatial placement）转换为混合 expert/data 传输模式，用 stream-based 模型确定最优传输比例。在受限带宽下 **最高 5.6× 加速 vs SOTA**；1k DC 大规模仿真下 **1.45× 加速**。
**影响**: 跨 DC MoE 训练需求正在出现。当 NVLink domain → 节点内 → 机柜内 → DC内 → 跨DC 的带宽梯度越来越陡峭时，Expert 的全局放置策略需要从「全 All-to-All」转向「混合传输」。这对超大规模算力服务商的网络架构规划（Rail-only 是否足够？是否需要三层 Clos？）提出了新的约束。

---

#### 🅸 可配置优化与 Benchmarking

**来源**: [MoE-Inference-Bench: Performance Evaluation of Mixture of Expert Large Language and Vision Models](https://arxiv.org/abs/2508.17467)（一手，arXiv cs.LG, 2025-08）
**发现**: 在 H100 上系统评测 Mixtral/DeepSeek/OLMoE/Qwen 系列 MoE 的推理性能，分析 batch size、序列长度、FFN 维度、expert 数量等超参数对吞吐的影响。评估优化技术：pruning、Fused MoE、speculative decoding、quantization、多种并行策略。
**影响**: 提供了 H100 上 MoE 推理的参考性能基线。关键发现：不同 MoE 架构（dense MoE vs fine-grained MoE）在相同硬件上的最优配置差异显著，不存在「一刀切」的最佳部署策略。

**来源**: [AIConfigurator: Lightning-Fast Configuration Optimization for Multi-Framework LLM Serving](https://arxiv.org/abs/2601.06288)（一手，arXiv cs.LG, 2026-01）
**发现**: 统一性能建模系统，无需 GPU profiling 即可快速搜索最优推理配置。对 MoE 架构（DeepSeek-V3）的配置优化实现 **50% 性能提升**（vs 密集模型 40%），平均搜索时间 < 30 秒。
**影响**: MoE 的配置空间（TP degree × EP degree × batch size × KV cache 分配等）远大于 dense 模型，手动调优不可行。自动化配置搜索对 MoE 部署效率的提升效果比 dense 模型更显著（50% vs 40%）。

---

## 🔗 关联知识

- [Multi-GPU 集合通信 — MoE 分析](../../02_rd/01_product/01_software/04-comm-lib/2026-06-04-multi-gpu-collective-communications.md)
- 微信超节点文章 — 郑嘉琦 QA（Q8/MoE）
- [AI Code Generation 概念](2026-06-26-ai-code-generation.md)

---

## 🆕 2026-06-24 追加：6 篇 MoE 硬件新论文（arXiv 6 月发布）

> **搜索范围**: arXiv(cs.LG, cs.DC, cs.AR) 2026-06-01 至 2026-06-22 新提交论文
> **数据质量**: 摘要精读 ✅ | 与 06-23 更新去重 ✅ | 与 2026-06-26-moe-hardware-impact.md 主表交叉引用 ✅

---

### 📐 新范式：MoE 训练/推理基础设施架构重构

#### 🆕 FoMoE：打破全复制范式的 MoE 联邦训练（arXiv:2606.19025, 2026-06）

**来源**: [FoMoE: Breaking the Full-Replica Barrier with a Federation of MoEs](https://arxiv.org/abs/2606.19025)（一手，arXiv cs.LG, 2026-06-17/20）

**发现**: 分布式 MoE 训练即使在 DiLoCo/Photon 等低通信方法下，仍要求每个站点保有完整模型副本。FoMoE 打破这一范式——把 Expert 层拆开分到不同 Worker 上，本地训练时跳过不在本地的 Expert。核心结果：

- 通信开销降低 **1.42×**（vs 高效 baseline），**45.44×**（vs DDP）
- 通过 skip-token 机制实现 **1.4× 吞吐加速**
- 在 **100B 级模型** 的系统建模中已验证可扩展

> **硬件影响 ⭐⭐⭐**: 首个完全消除「全复制」假设的 MoE 训练方案。**远程站点只需持有部分 Expert 即可参与训练**。对硬件的影响是双重的：(1) 异构/远程硬件可被纳入训练池；(2) 跨 DC MoE 训练的可行性被提升一阶。与 HybridEP（06-23 收录）互补——HybridEP 优化已有跨 DC 传输，FoMoE 从根本上减少所需传输量。

---

#### 🆕 ASAP：面向 MoE Prefill 的异步解耦推理系统（arXiv:2606.22541, 2026-06-21）

**来源**: [ASAP: A Disaggregated and Asynchronous Inference System for MoE Prefill](https://arxiv.org/abs/2606.22541)（一手，arXiv cs.DC, 2026-06-21）

**发现**: DP+EP 混合并行中 Attention DP Group 间的全局同步屏障是性能杀手——请求到达率和序列长度方差天然导致 DP 不均衡。ASAP 将 Attention 和 MoE 阶段解耦为**完全异步执行流水线**：

- 四类协同优化：请求调度 + 模型执行的异步通信原语
- 在 **CloudMatrix384 超节点** 上验证
- **SLO-compliant prefill 吞吐提升 90%**（vs SOTA 同步方案）

> **硬件影响 ⭐⭐⭐**: 首个专门针对**超节点（CloudMatrix384）** 验证的 MoE Prefill 解耦方案。关键信号：(1) AWS CloudMatrix 成为 MoE 推理学术实验平台；(2) 异步解耦是 MoE serving 主流方向，对超节点网络拓扑提出了差异化要求。

---

### ⚖️ 负载均衡：从「基于历史」到「实时精确」

#### 🆕 UltraEP：RSN 上近最优实时均衡（arXiv:2606.04101, 2026-06-02/18）

**来源**: [UltraEP: Unleash MoE Training and Inference on Rack-Scale Nodes with Near-Optimal Load Balancing](https://arxiv.org/abs/2606.04101)（一手，arXiv cs.DC, 2026-06）

**发现**: 首个**精确负载、实时**的大规模 EP 均衡器——利用 RSN 内数十 GPU 的扩展互联，在**每个 micro-batch 和每个层**上做重新均衡。方法：

- Quota-driven planner 对 post-gating 负载即时反应
- RSN-native persistent tile streaming + relay-based fan-out
- 256 GPU 多 RSN 部署，DeepSeek-V3-671B / Qwen3-235B 等 **106B-671B** 参数模型
- **达到力平衡理想吞吐的 94.3%**，是 no-balancing 的 **1.49×**
- 最终 rank 间不均衡度从 1.30-4.01 降至 **1.01-1.04**（近乎完美）

> **硬件影响 ⭐⭐⭐**: RSN（机柜级节点）是 2026 年硬件新名词——机柜内数十 GPU 通过 NVSwitch+NVLink 构成高带宽域。UltraEP 证明：当 RSN 内部 scale-up 带宽被充分利用时，实时逐层均衡是可行的。**对服务器架构的影响**：RSN 设计需要预留足够的内互联带宽来承载「每层重新均衡」产生的额外流量。

---

#### 🆕 ForeMoE：微步级 MoE 负载均衡在 RL Post-training（arXiv:2606.11867, 2026-06-10）

**来源**: [Harnessing Routing Foresight for Micro-step-level MoE load balancing in RL Post-training](https://arxiv.org/abs/2606.11867)（一手，arXiv cs.DC, 2026-06-10）

**发现**: RL 后训练阶段的独特负载特征：step 级负载稳定，但 **micro-step 级有严重高频波动**（因 batch 极小）。ForeMoE 利用 RL 三阶段（rollout→recompute→policy update）的可预见路由信息做 proactive 均衡：

- 层次化规划器分解 NP-hard 问题
- Transfer engine 利用 CPU-assisted + GPU-direct 补全硬件路径
- 64 GPU 评估：**1.45× 加速**（vs SOTA）

> **硬件影响 ⭐⭐**: RL Post-training 是快速增长的工作负载。其 micro-step 级负载波动对硬件的需求（极低延迟 AlltoAll、快速 Expert 迁移）与训练/推理不同。**单一静态优化策略可能不够**。

---

### 🔬 方法论/诊断/可靠性新视角

#### 🆕 DODOCO：MoE Dispatch 瓶颈的跨架构诊断（arXiv:2605.20982, 2026-05-20）

**来源**: [Diagnosing Overhead in Dispatch Operations: Cross-architecture Observatory](https://arxiv.org/abs/2605.20982)（一手，arXiv cs.DC, 2026-05-20）

**发现**: 对 AlltoAll dispatch 瓶颈的两大基础假设做了**实验证伪**：

1. **「路由不均衡可由系统层纠正」被证伪**：EP 缩放对 per-expert max/mean token 比改变 ≤5%——straggler 是模型路由决策的内生属性，不是 Expert 放置问题
2. **「Mock-token benchmark 可代表生产路由」被证伪**：Mock tokens 高估 Gini 系数最多 **2.35×**，制造出真实文本下不存在的 batch-size 缩放趋势
3. **五大架构裂为两个稳定带**：MHA/Mamba-2 Gini 0.105-0.150（数据弹性），MLA/GDN 始终 >0.24（持续集中），GQA 为中间态

> **硬件影响 ⭐⭐⭐**: 清理了 MoE 硬件优化的基础假设。如果 straggler 是模型路由决策的内生属性：(1) 硬件优化目标应从「让 Expert 负载更均衡」转向「**容忍** Expert 负载不均衡」；(2) Mock-token 基准测试结果不可靠——评估 MoE 硬件方案必须用真实文本负载。

---

#### 🆕 EEP：大规模 EP 中部分故障的自愈通信层（arXiv:2605.10670, 2026-05-11）

**来源**: [Surviving Partial Rank Failures in Wide Expert-Parallel MoE Inference](https://arxiv.org/abs/2605.10670)（一手，arXiv cs.DC, 2026-05-11）

**发现**: MoE 推理依赖**所有 EP rank 存活**才能完成一个 decode step——任何单一 rank 故障都会导致全实例宕机。EEP 将 membership 从「固定初始配置」变为「显式可变的运行时状态」：

- 集成 SGLang，单 rank 故障 **恢复 11s**，**重新整合 8s**，**52s 恢复到 95% 吞吐**
- 固定 membership baseline：**348s 才能恢复**
- 稳态开销 < **4.4%**（vs 固定 membership 的 DeepEP）

> **硬件影响 ⭐⭐**: 随 EP 宽度增加（256 GPU+），故障概率大幅上升。EEP 证明**运行时 membership 可变性**是必要的系统能力。对硬件影响：NIC/交换机需支持不中断的 membership 变更（如 RDMA 连接热迁移），对「初始化后固定」的网络硬件设计范式提出挑战。

---

---

### 🆕 FEPLB：NVLink Copy Engine 实现「近乎免费」的 MoE 负载均衡（arXiv:2604.19654, 2026-04-21）

**来源**: [FEPLB: Exploiting Copy Engines for Nearly Free MoE Load Balancing in Distributed Training](https://arxiv.org/abs/2604.19654)（一手，arXiv cs.DC, Apr 2026）

**发现**: 一个简单但深刻的观察：NVIDIA Hopper 架构的 **NVLink Copy Engine** 可以在 GPU 间搬运数据而**不消耗任何 SM 周期**，实质上提供了一个「几乎免费」的并行通信通道。FEPLB 将其用于 MoE 负载重均衡：

- **两阶段调度**：第一阶段通过标准 EP 后端跨节点路由 tokens；第二阶段通过 Copy Engine 在 NVLink 域内以近乎零成本重分发动态 expert 的 tokens 和 weights
- **CPU 调度器**：与静态 expert 计算并发运行，不占用 GPU 资源
- **与 EP/PP 共存**：Copy Engine + CPU 资源正交于 EP 和 PP 消耗的资源，无需重配置

在 GLM-5 的 MoE 层（128 experts, no auxiliary loss, 16 H100）：

- Token straggler 降低 **51-70%**
- GEMM straggler 降低 **50-68%**
- EP 通信开销**零增量**
- EP=8 时 Token straggler 为 FasterMoE 的 **1/2**

> **硬件影响 ⭐⭐⭐⭐⭐**: 这是对 Hopper 架构的**隐藏硬件资源**的巧妙利用。Copy Engine 的设计目标本是 GPU-GPU 内存拷贝加速，FEPLB 证明它可以作为 MoE 负载均衡的专用硬件通道。对下一代 GPU 的启示：(1) Copy Engine 带宽/通道数应作为 MoE 优化的重要硬件参数；(2) 专用 DMA 引擎对稀疏工作负载的价值远超预期；(3) 更灵活的 GPU 内部数据通路可为 MoE 通信拓扑提供「免费」的负载重均衡维度。

---

### 🆕 FoE：KV-head 级集群化消除 MoE AlltoAll 通信（arXiv:2605.06206, 2026-05-07）

**来源**: [Federation of Experts: Communication Efficient Distributed Inference for LLMs](https://arxiv.org/abs/2605.06206)（一手，arXiv cs.LG, May 2026）

**发现**: 提出一种新颖的 MoE 架构改造——**Federation of Experts (FoE)**，将 MoE 块重新组织为多个 MoE 集群，**每个集群只负责一个 KV head**，expert parallelism 在集群内应用。集群间只需一个 sum 操作同步后 attention 残差：

- **单节点推理**：完全消除 all-to-all 通信——同一集群的所有 expert 驻留在同一 GPU
- **多节点推理**：all-to-all 通信**限制在 intra-node 内**，跨节点通信消失
- 端到端前向延迟降低 **5.2×**，TTFT 降低 **3.62×**，TBT 降低 **1.95×**
- 生成质量与标准 MoE 模型相当

> **硬件影响 ⭐⭐⭐⭐**: FoE 从**模型架构层面**改写通信模式，而非优化现有模式。对硬件的反推：(1) 如果 FoE 被广泛采用，跨节点 all-to-all 带宽需求将大幅下降；(2) 但 intra-node 互联（NVLink）的带宽和延迟要求反而提高；(3) **架构-网络协同设计**进入新阶段——模型架构变化可彻底改变硬件需求。需跟踪此方向在更大模型（>100B）上的验证。

---

### 🆕 AFD 设计空间探索：MoE 推理解聚到哪一层？（arXiv:2605.28302, 2026-05-27）

**来源**: [How Far Can Disaggregation Go? A Design-Space Exploration of Attention-FFN Disaggregation for Efficient MoE LLM Serving](https://arxiv.org/abs/2605.28302)（一手，arXiv cs.LG, May 2026）

**发现**: 对 MoE 推理解聚的**系统化设计空间探索**——从 chunked-prefill → P/D 解聚 → 算子级 Attention-FFN Disaggregation (AFD)。核心问题：**每层解聚何时真正值得？**

- AFD 将 attention 和 MoE-FFN 放在**不同 GPU 组**上，暴露 memory-bound attention vs compute-intensive FFN 的异构性
- 在严格 TTFT/TPOT SLOs 下，AFD 在 DeepSeek-V3.2 上**持续维持约 4k tokens/s** 系统吞吐——非 AFD 部署在此条件下不可行
- workload 特性（input/output 长度、prefix-KV 重用率、per-user 延迟约束）决定最佳 attention/FFN GPU 分配比例
- 联合框架：on-device kernel 测量 + 高保真网络仿真

> **硬件影响 ⭐⭐⭐**: 为 MoE 推理集群设计提供了**量化设计原则**：(1) Memory-bound attention 和 compute-bound FFN 的物理资源分离需要硬件支持；(2) 解聚的收益取决于互联拓扑——rack-scale 互联带宽越高，AFD 收益越大；(3) 推理集群的 GPU 异构部署可能有理论依据——attention GPU 和 FFN GPU 可用不同 SKU。

---

### 🆕 CRAFT：细粒度成本感知 Expert 复制（arXiv:2603.28768, MLSys 2026）

**来源**: [CRAFT: Fine-Grained Cost-Aware Expert Replication For Efficient Mixture-of-Experts Serving](https://arxiv.org/abs/2603.28768)（MLSys 2026; arXiv cs.DC, Mar 2026）

**发现**: Expert 复制是 MoE serving 中最广泛使用的负载均衡技术之一，但现有方案**过度复制**——许多副本带来的边际收益极小，却消耗大量 GPU 内存。CRAFT 提出 per-layer 细粒度复制：

- 基于估计的「复制收益」决定每个 layer 中每个 expert 复制多少份
- 在给定内存预算下最大化负载均衡程度
- 无需额外训练或模型修改
- 端到端吞吐提升 **1.14×**（平均），最高 **1.2×**

> **硬件影响 ⭐⭐**: 对 GPU 内存管理的启示：(1) Expert 复制是对 GPU 内存以「空间换时间」的典型操作；(2) CRAFT 证明 **per-layer 细粒度管理**比全局 uniform 复制高效得多；(3) 隐含的硬件需求：快速 expert 副本创建/销毁 + 灵活的内存分配（可用的显存碎片管理）。

---

### 🆕 UCCL-EP：跨异构平台的 MoE 通信可移植性（arXiv:2512.19849, 2025-12）

**来源**: [UCCL-EP: Portable Expert-Parallel Communication](https://arxiv.org/abs/2512.19849)（一手，arXiv cs.DC, Dec 2025）

**发现**: 现有 GPU-initiated RDMA（如 DeepEP）虽高性能，但**要求 GPU 与 NIC 的深度垂直集成**，无法移植到 AMD GPU + EFA / Broadcom NIC 等异构平台。UCCL-EP 用 GPU-CPU 控制通道替代 GPU-initiated RDMA：

- 紧凑的 token-routing 命令通过 GPU-CPU 控制通道传输到**多线程 CPU 代理**
- CPU 代理代表 GPU 发起 GPUDirect RDMA 操作
- 在 EFA 上 dispatch/combine 吞吐提升 **2.1×**（vs 最佳现有方案）
- 在 NVIDIA-only 平台性能与 DeepEP **相当**
- SGLang token throughput 提升 **40%**（NVIDIA+EFA）
- DeepSeek-V3 训练吞吐提升 **45%**（AMD+Broadcom, 16 节点）

> **硬件影响 ⭐⭐⭐**: (1) MoE 通信**不应与特定 GPU/NIC 绑定**——UCCL-EP 证明一个轻量 GPU-CPU 控制通道 + 多线程 CPU proxy 可以达到专用 GPU-initiated 方案同等性能；(2) 对集群硬件选型的启示：MoE 通信优化不再要求全栈 NVIDIA——AMD + EFA/Broadcom 也可在 MoE 场景中高效运行；(3) 对 NIC 硬件设计：无需支持 GPU-initiated RDMA 的复杂特性，标准 GPUDirect RDMA 即可。

---

### 🆕 3D CPO 加速 MoE 训练：2.7× time-to-train 缩减（arXiv:2510.15893, HotI 2025）

**来源**: [Accelerating Frontier MoE Training with 3D Integrated Optics](https://arxiv.org/abs/2510.15893)（Hot Interconnects 2025; arXiv cs.AR, Oct 2025）

**发现**: 从硅光集成角度分析 MoE 训练的互联瓶颈。3D CPO（Co-Packaged Optics, "Passage"）将光学 I/O 直接嵌入 GPU package：

- 3D CPO 使 scale-up 带宽和 radix **8× 增加**（vs 铜缆 1m 限制）
- 使 **多维并行策略** 在 scale-up 域内成为可能（TP + EP + PP 同时在一个域内）
- 对于 >1T 参数的 MoE 模型，**time-to-train 降低 2.7×**
- 关键洞察：MoE 的 all-to-all 通信模式需要高 radix 互联——3D CPO 的带宽密度和 radix 恰好解决此瓶颈

> **硬件影响 ⭐⭐⭐⭐**: (1) 从硬件角度最直接的 MoE 优化方案——**互联带宽 × 8 直接转化为训练加速**；(2) 3D CPO 的 scale-up 域扩展使 MoE 的全 Expert 直接通信成为可能，消除多跳拥塞；(3) 对服务器设计的影响：光学 scale-up 域可能消除 MoE 模型对复杂网络拓扑（如 3D Torus、Dragonfly+）的依赖。

---

## 🔗 关联知识（2026-06-25 追加）

- [分布式互联拓扑 — MoE AlltoAll 通信模式](../../02_rd/01_product/01_software/04-comm-lib/2026-06-04-multi-gpu-collective-communications.md)
- RSN 机柜级节点 — 超节点专题
- CloudMatrix 超节点 — AWS 超节点方案
- [NVLink Copy Engine — Hopper 架构硬件特性](../../02_rd/00_shared/01_architecture/2026-06-04-architecture-design-complete.md)
- [3D CPO 光学互联 — HotI 2025 最佳论文](../../02_rd/01_product/00_hardware/04_si-signal/2026-07-29-optical-modules-2026h1.md)

## 🔗 关联知识（2026-06-24 追加）

- [分布式互联拓扑 — MoE AlltoAll 通信模式](../../02_rd/01_product/01_software/04-comm-lib/2026-06-04-multi-gpu-collective-communications.md)
- RSN 机柜级节点 — 超节点专题
- CloudMatrix 超节点 — AWS 超节点方案

---

## 🆕 2026-06-26 追加：3 篇 MoE 硬件新论文（arXiv 6/22-6/25 新提交）

> **搜索范围**: arXiv(cs.LG, cs.DC, cs.AR) 2026-06-22 至 2026-06-25 新提交论文
> **与 06-24/06-25 更新去重** ✅

---

### 🅰 运行时并行度切换：Moebius 打破 TP 与 EP 的非此即彼

**来源**: [Moebius: Serving MoE Models with Seamless Runtime Parallelism Switch](https://arxiv.org/abs/2606.26607)（一手，arXiv cs.DC, 2026-06-25）

**发现**: MoE serving 中 Tensor Parallelism (TP) 和 Expert Parallelism (EP) 各有最优域——TP 在低并发时更快，EP 在高并发时更好。生产负载持续跨越此边界（在线服务突发→安静期、RL rollout 高并发→tail straggler）。Moebius 在运行时无需重启或丢弃请求即可在 EP↔TP 间切换：

- 8×H200 Qwen3-235B-A22B：每个切换点匹配更好的静态并行度
- RL rollout 全周期 **1.16-1.25× 加速**
- **切换时间 215-434ms**（decode step 之间完成，不阻塞请求）
- 双布局常驻内存开销仅 **2.4%**
- 关键洞察：EP 和 TP 是同一模型的两套布局（byte-identical weights + KV cache），切换只改变 rank 拥有的 slice

> **硬件影响 ⭐⭐⭐⭐**: 生产 MoE serving 不再需要在 TP/EP 间二选一——运行时切换可行且高效。(1) H200 的 NVLink 高带宽互联使切换足够快（200-400ms），对下一代 GPU scale-up fabric 提出更高带宽要求以加速布局切换；(2) RL 训练 rollout 阶段作为受益场景，与 ForeMoE（06-24 收录）的 micro-step 级波动发现互补——宽 EP + 运行时切换的组合可能是 RL post-training 的部署范式。

---

### 🅱 235B MoE→双 A100 的 75% 内存压缩：硬件感知压缩方法论

**来源**: [Agentic evolution of physically constrained foundation models](https://arxiv.org/abs/2606.25532)（一手，arXiv cs.AI/cs.AR, 2026-06-24）

**发现**: 基于进化知识图谱的多智能体自动发现引擎，演化出两种物理感知的压缩方法：

- **MoE-Salient-AQ**：利用带宽高效的 Sensitivity Profile 选择性压缩——sub-3-bit 低比特率下 **比 SOTA 手动设计的 MoE 量化方案好 3.7%**
- 235B 级 MoE 模型部署到受限的**双 A100（160GB 合计）**：**75% 内存缩减，仅 0.64% 准确率下降**
- 方法论亮点：自动化 CoT 将盲搜索转变为有向结构演化

> **硬件影响 ⭐⭐⭐**: (1) 双 A100 运行 235B MoE 是硬件边界突破的实证——MoE「用稀疏性换内存密度」的推理部署可行；(2) Sensitivity Profile 方案可直接指导服务器端 KV Cache/Expert 的硬件感知放置；(3) sub-3-bit MoE 量化在 3.7% 领先幅度下走向实用化，对硬件的低精度计算单元提出了更强需求；(4) 自动化的 CoT 方法验证了 AI-driven HW-SW co-design 的可行性。

---

### 🅲 35B MoE 在 2011 Fermi GPU 上运行的极端案例分析

**来源**: [A 35B Hybrid-Attention MoE Model on a 6GB 2011 GPU](https://arxiv.org/abs/2606.24031)（一手，arXiv, 2026-06-23）

**发现**: 在 **2011 年 NVIDIA Tesla C2075**（Fermi, 6GB, 无 Tensor Core, 无 FP16）上完成 Qwen3.6-35B-A3B（~3B 活跃参数）的端到端推理：

- **混合执行策略**：GPU prefill（逐层 streaming expert weights from host RAM）+ CPU decode（手写 W4A8 SSSE3 pmaddubsw GEMV）
- Prefill 延迟优化：expert pinning + single-pass prefill + NUMA interleaving → **57.2s → 37.5s**（-34%）
- Decode 吞吐：**2.8 → 8.6 tps**（整数 SIMD kernel, ~3× 提升）
- **负结果同样重要**：GPU offload head、hyper-threading、三版 GPU kernel 改写全部无效——在带宽受限场景 CPU decode 比 GPU 更有优势

> **硬件影响 ⭐⭐⭐**: (1) MoE 的稀疏性（35B 总参/3B 活跃）是极端部署可行的根本原因——dense 模型不可能装入 6GB；(2) **GPU prefill + CPU decode 的混合方案验证了异构执行范式**，与「prefill 加速器 + decode 加速器分立」的行业趋势一致；(3) 负结果提供了宝贵的实际边界——GPU head offload 失效说明在 2011 GPU 上 MoE 推理的带宽瓶颈 > 计算瓶颈；(4) 对超节点/边缘场景的启示：MoE 的稀疏性使其在极端资源约束下仍有部署空间。

---

**搜索关键词 (2026-06-26 新增)**:

- `"MoE" "parallelism switch" "runtime" "TP" "EP"`
- `"MoE" "compression" "hardware-aware" "low-bit"`
- `"Mixture-of-Experts" "Fermi" "legacy" inference`

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- 郑嘉琦 QA 汇编 — 关联
- [Multi-GPU 集合通信分析](../../02_rd/01_product/01_software/04-comm-lib/2026-06-04-multi-gpu-collective-communications.md) — 关联
- [GPU 芯片设计深度分析](../../02_rd/04_chip/base/2026-06-26-gpu-chip-design-analysis.md) — 关联
- [AI Code Generation 概念](2026-06-26-ai-code-generation.md) — 关联
- RSN 机柜级节点 — 超节点专题 — 关联
- CloudMatrix 超节点 — AWS 超节点方案 — 关联
- [NVLink Copy Engine — Hopper 架构硬件特性](../../02_rd/00_shared/01_architecture/2026-06-04-architecture-design-complete.md) — 关联
- [3D CPO 光学互联 — HotI 2025 最佳论文](../../02_rd/01_product/00_hardware/04_si-signal/2026-07-29-optical-modules-2026h1.md) — 关联

### 外部资料引用

- (无)

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
