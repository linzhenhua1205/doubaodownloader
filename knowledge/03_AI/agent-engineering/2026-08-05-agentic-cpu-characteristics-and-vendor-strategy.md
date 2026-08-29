# Agentic 负载的 CPU 特征与三巨头 CPU 策略深度解读

> **日期**: 2026-08-05 | **分类**: 03_AI/agent-engineering | **专题编号**: AGT-CPU-2026-01
> **一句话**: Agentic AI 把 CPU 从"GPU 的陪跑"推到"关键路径"——AMD/Intel 官方 keynote 已明确宣称 agentic 负载 CPU 需求 ≥ GPU，NVIDIA 则用自研 Vera CPU + Groq LPU 解聚回应；CPU 正在成为超节点里仅次于 GPU 的第二稀缺资源。
> **来源**: ServeTheHome 2026-08 系列实况（AMD Advancing AI 2026 / Intel Computex 2026 / NVIDIA GTC 2026 技术披露）+ 公开 roadmap；厂商叙事与独立分析已分别标注
> **关联**: [编程 Agent 全链路推理专题](../agent-engineering/2026-08-04-coding-agent-fullchain-inference-deep-analysis.md) · [Claude Code IO 特征](../agent-engineering/2026-08-05-claude-code-io-characteristics-deep-analysis.md) · [KV Cache 物理推导] · [AMD Helios 超节点跟踪]

---

## 1. 结论概要（TL;DR）

1. **Agentic 负载的计算画像与纯 LLM 推理本质不同**：LLM 推理是"GPU 主导 + CPU 外围"；agentic 是"CPU 执行通用任务 + GPU 做张量子步骤 + 网络做数据搬运"的**混合流水线**。Intel 官方 demo 直言 agentic 负载 **CPU 需求 ≥ GPU 需求**；AMD 声称 CPU 市场 2030 年 $220B（占 AI 加速器 $1.4T 之外的独立大盘）。
2. **CPU 在 agentic 里承担六大角色**：①编排/控制平面（agent loop 状态机）②工具执行/沙箱（编译·shell·测试）③数据预处理（tokenize·检索·JSON·compaction）④KV Cache 外溢的 warm 层宿主（DRAM）⑤路由/小模型推理宿主 ⑥GPU 喂料（数据搬运）。前三个是"CPU 独有职责"，后三个是"与 GPU 争抢但 CPU 必须兜底"。
3. **三巨头策略收敛于同一判断、分化于三条路线**：
   - **NVIDIA**：自研 Vera CPU（Olympus 核，首次非 ARM 定制而是自研架构）抢占服务器 CPU 市场 + 买下 Groq LPU 做**解聚低延迟推理**（GPU=prefill/attention，LPU=decode FFN），CPU 角色 = 生态守门人。
   - **AMD**：CPU 多样性产品线（高频 Venice HF / 256 核 Venice / 128 核通用 / Venice-X 3D 缓存）× 2nm Zen 6，Helios 机架 1 CPU:4 GPU，主打"perf/agents per watt ×2"。
   - **Intel**：Xeon 6+（Clearwater Forest）288 E-core 主打"一机架 150K agents"密度叙事 + 解聚推理（CPU=orchestration+tooling），Diamond Rapids 推迟 2027 且砍掉 8 通道主流平台。
4. **对超节点设计的第一性影响**：CPU:GPU 比例（1:4 vs 2:4）、CPU 内存带宽（KV 外溢）、CPU 核数密度（并发 agent 数）必须进入系统级规划——**超节点不只是 GPU 集群，而是"CPU 池 + GPU 池 + 专用加速池"的异构系统**。

---

## 2. Part A：Agentic 负载的 CPU 特征（第一性拆解）

### 2.1 计算画像：训练 / 传统推理 / Agentic 三方对比

| 维度 | 训练 | 传统 LLM 推理 | **Agentic 工作负载** |
|:-----|:-----|:--------------|:---------------------|
| 主导硬件 | GPU（张量） | GPU（张量）+ CPU（预处理） | **CPU（编排/工具）+ GPU（张量子步骤）+ 网络（数据流）** |
| 计算形态 | 大批量矩阵乘 | 批量 decode（吞吐型） | **串行依赖链（决策→工具→观察→再决策）** |
| 延迟要求 | 宽松（吞吐优先） | 中（per-token 延迟） | **严（每轮决策是关键路径，人不在环）** |
| 指令特征 | 纯向量 | 向量为主 | **分支密集 + 指针追逐 + 少量向量** |
| 并发粒度 | 1 个大任务 | N 个用户请求 | **M 个 agent × N 步 × 工具子任务** |
| CPU 负载占比 | 低（~5-10%） | 中（~15-25%） | **高（厂商 demo：≥50%，甚至超过 GPU）** |
| 内存压力 | HBM 为主 | HBM + KV | **HBM（KV）+ DRAM（KV 外溢/工具数据）+ 存储（沙箱）** |

> 注：CPU 负载占比为工程估算区间，Intel 官方 demo 定性为"CPU 需求略高于 GPU"，AMD/Intel 均未给公开精确百分比；此处标注为量级判断而非实测。

### 2.2 CPU 六大角色（MECE 分解）

```text
Agentic workload: CPU responsibilities (six roles)
+-- A. Orchestration / control plane (agent loop)
|     +-- State machine (task/step/sub-agent lifecycle)
|     +-- Decision routing (tool/model/context-compaction choice)
|     +-- Scheduling (parallel subtasks, checkpoint management)
+-- B. Tool execution / sandbox (deterministic compute)
|     +-- Compile/interpret, shell, test, lint
|     +-- File/DB/network I/O
|     +-- External system interaction (API, browser, simulation)
+-- C. Data preprocessing (context engineering)
|     +-- Tokenize / JSON parse / structured-output validation
|     +-- Retrieval (vector index -> CPU-side filter, inverted index)
|     +-- Context compaction (summarize, cache management)
|     +-- Data cleaning/conversion (model input pipeline)
+-- D. KV cache spillover host (warm tier)
|     +-- Paged KV resident in DRAM (CPU memory as tier-2)
|     +-- NVMe <-> DRAM <-> HBM swap management
+-- E. Router / small-model inference host
|     +-- Router/classifier (task -> LLM or small model)
|     +-- Embedding compute (partial CPU-side)
|     +-- Local small model (edge agentic)
+-- F. GPU feeding (data movement)
      +-- Data load / format conversion (GPU input pipeline)
      +-- Control-plane signaling (launch, sync, error handling)
```

> 角色中文说明：A 编排/控制平面 · B 工具执行/沙箱 · C 数据预处理 · D KV 外溢宿主 · E 路由/小模型宿主 · F GPU 喂料

**关键判断**：A/B/C 是 **CPU 独有职责**（GPU 无法替代）；D/E/F 是"本可交给 GPU/加速器、但系统设计上 CPU 必须兜底"的职责。Agentic 之所以把 CPU 推向关键路径，正是因为 A/B/C 的量级随 agent 数量线性增长，且它们都落在**串行关键路径**上。

### 2.3 指令特征 × 数据访问特征矩阵

| 角色 | 指令特征 | 数据访问特征 | 延迟/吞吐敏感性 |
|:-----|:---------|:-------------|:----------------|
| A 编排 | 分支密集（if/switch/状态转换）、依赖链串行、中等 ILP | 热状态小（KB 级，缓存常驻）、调度队列 | **延迟敏感**（每步决策决定端到端时延） |
| B 工具执行 | 多样：编译=大指令足迹+分支、shell=进程+系统调用 | 大文件流式、随机小 I/O 混合 | 吞吐+延迟混合（用户可感知） |
| C 预处理 | 字节/字符串密集（解析）、少量 SIMD | 上下文大块读、写中间产物 | 吞吐为主，但在关键路径上 |
| D KV 外溢 | memcpy/搬运指令、页管理 | **带宽敏感**（GB/s 级持续搬移） | 带宽瓶颈 |
| E 路由/小模型 | 向量指令（AVX-512/AMX/SVE2/FP8） | 模型权重（几百 MB~几 GB） | 延迟敏感（决定路由开销） |
| F 喂料 | 拷贝/格式转换/信令 | 数据块搬运（PCIe/网络） | 带宽+同步延迟 |

### 2.4 硬件需求推导（从负载特征到硅片需求）

| 负载特征 | 推导出的硬件需求 | 三家对应实现 |
|:---------|:-----------------|:-------------|
| 分支密集 + 指针追逐（工具调用链/图遍历/状态机） | 强分支预测器、大 L1I、memory renaming、**图预取器** | NVIDIA Olympus：64KB L1I（2× Zen5）、2 分支/周期神经预测、graph prefetcher；AMD/Intel：经典强分支预测+大缓存 |
| 并发 agent 数（几十~几百同时跑） | 高核数、高线程密度、低每核功耗 | AMD Venice 256 核（1.3× 密度）；Intel Xeon 6+ 288 E-core；NVIDIA Vera（多核 SMT） |
| 每轮决策延迟（人不在环） | 高主频、单线程强、低时延内存 | AMD Venice HF（高频核，Helios 用）；Intel P-core；NVIDIA Olympus 高频设计 |
| KV 外溢 + 大上下文搬运 | **内存带宽**（通道数/带宽）、CXL 扩展 | AMD/Intel 16 通道 DDR5（Diamond Rapids/Venice 2026H2 转 16ch）；NVIDIA SOCAMM LPDDR5X 模块化（GB300） |
| 工具执行/沙箱数据量 | 内存容量 + NVMe 带宽 | 平台级（PCIe Gen6 支撑） |
| 路由/小模型/embedding | 向量扩展（AMX/AVX-512/SVE2/FP8） | Intel AMX、AMD AVX-512（Zen6 增强）、NVIDIA SVE2+FP8（Olympus 6-wide SVE2） |
| 喂 GPU/网络 | PCIe Gen6、224G SerDes、CXL | AMD Venice 224G SerDes + PCIe Gen6；Intel Diamond Rapids PCIe Gen6；NVIDIA NVLink-C2C（CPU↔GPU 直连） |
| 通用软件兼容（x86 存量） | x86 ISA 生态 | AMD/Intel 主打 x86；NVIDIA 走 Arm（主打"新系统"叙事，靠 NVLink 集成） |

### 2.5 量化锚点（可验证/可估算）

- **CPU:GPU 比例**（超节点级）：AMD Helios = **1 Venice : 4 GPU**（72 GPU / ~18 CPU）；NVIDIA Vera Rubin NVL72 = **2 Vera : 4 GPU**（72 GPU / 36 CPU）。→ AMD 用更少 CPU 摊薄成本，NVIDIA 用更多 CPU 承载控制平面+通用负载（两家对"CPU 在机架里该多重要"的定价不同）。
- **并发 agent 密度**：Intel 官方宣称 **1 机架 Xeon 6+ 可跑 150K agents**（288 核/架，~520 agents/核·同时驻留，含排队）。量级合理性：agent 步长秒级、每 agent 占用单核时间片小，核数×并发驻留是可行上限，但"活跃并发"远小于"驻留数"——此数字为营销上限，需打折理解。
- **CPU 市场量级**（AMD 官方）：AI 加速器 TAM 2030 = **$1.4T**（≈今天整个芯片市场）；CPU 市场 2030 = **$220B**；合计硅 TAM $2T、40% CAGR。NVIDIA 官方未给 CPU 单独 TAM，但其进军服务器 CPU 市场动作本身即承认该市场价值。
- **性能对比叙事**（厂商数据，需独立复测）：AMD 宣称 Venice "2× perf/agents per watt vs 竞品、2.2× per socket vs NVIDIA Vera"；NVIDIA 宣称 Vera Rubin+Groq "35× 每用户 token 率吞吐 vs Grace Blackwell"；SambaNova（Intel 生态）宣称解聚推理 **2-3× faster than GPU-only**。三者均为厂商/伙伴口径。

---

## 3. Part B：三巨头 CPU 策略深度解读

### 3.1 NVIDIA：自研 CPU 抢市场 + 异构解聚抢延迟

**策略定位**：Vera 是 NVIDIA 从"给 GPU 配的 CPU"（Grace）到"独立进军服务器 CPU 市场"的质变。STH 明确指出：Vera "不是与 Xeon/EPYC 全线对打，但 NVIDIA 要让它进入多种服务器"，核心动机是**防止客户给 Rubin GPU 配别家 CPU**（生态守门人）。

**Vera CPU（Olympus 核）架构要点**（GTC 2026 后深度披露，2026-08 官方白皮书）：

- **前端**：10-wide decoder、48 指令 decode queue、16×64bit fetch、神经分支预测器（2 分支/周期）、**64KB 4-way L1I（2× Zen5，服务大指令足迹）**、96KB 6-way L1D
- **中核**：乱序执行、10 uops/周期重命名、**memory renaming**（超越寄存器重命名，重命名整个内存地址，依赖指令可在 load 完成前执行）、**value prediction**、move elimination
- **后端**：**18 执行 pipe**（8 整数/分支 + 6 向量/FP + 4 load + 2 store，全成对布局服务于 partition-based spatial multithreading）；**整数 pipe 多于 FP**——明确偏向控制流/数据处理而非纯数值；6-wide SVE2 + FP8
- **缓存/预取**：3K entry L2 TLB；**novel graph prefetcher**——识别"指针→目标地址"的 producer-consumer 关系，在指针解析前预取最终目标数据。**AMD/Intel 均无同类实现**，学术界已讨论多年，NVIDIA 首次商用。
- **SPEC CPU 2026**：首批成绩"not all rosy"——整数/吞吐亮点 vs 部分场景落后，需结合"主要面向 AI 系统集成"的定位理解。

**异构解聚推理（Groq LPU 收购的落点）**：GPU 本质是高吞吐高延迟；agentic 需要低延迟（人不在环、agent 间快速反应、长上下文）。NVIDIA 的解法不是改 GPU，而是**异构分工**：

- Rubin GPU：prefill + decode 的 attention 子阶段（吞吐友好部分）
- **Groq LP30 LPU**：decode 的 FFN 子阶段（延迟敏感部分；500MB 片上 SRAM、150TB/s SRAM 带宽、确定性 VLIW 静态调度、无需猜延迟）
- 宣称收益：**35× 每用户 token 率吞吐 vs Grace Blackwell**、性能曲线向高 TPS-per-user 大幅延伸、支持更长上下文
- 代价：机架变成异构系统（复杂度、功耗、软件栈成本）

**GB300 内存形态**：Grace CPU 从固定 LPDDR5X 配置 → **Micron SOCAMM 模块化 LPDDR5X**（可更换、可后期配置容量，M.2 外观的模块化内存条）——CPU 内存可扩展性成为显性设计点。

**NVIDIA CPU 策略小结**：①自研核（不依赖 ARM IP 授权）进入高利润服务器 CPU 市场；②CPU 与 GPU 用 NVLink-C2C 深度集成（别人配不了）；③推理端用"GPU+LPU"双加速把延迟曲线补上；④CPU 内存（SOCAMM）模块化支持长上下文。路线关键词：**集成 + 异构 + 生态锁定**。

### 3.2 AMD：CPU 多样性 × 每瓦 agents 效率叙事

**策略定位**：AMD 是三家唯一把"agentic → CPU 需求"直接写进 CEO keynote 叙事的公司。Lisa Su 原话（AAI 2026）："Agentic AI needs a lot of CPUs to actually handle the tasks the agents are running, never mind orchestrating the GPUs." + "With agentic AI, CPUs now matter more than ever. AI systems need more than just GPUs running inference." + "A good CPU needs a high frequency core, fast I/O, to keep GPUs fed."

**EPYC Venice（Zen 6，2026 年产品线）四型结构（MECE）**：

| SKU 家族 | 定位 | 规格要点 | 目标负载 |
|:---------|:-----|:---------|:---------|
| **Venice HF** | 高频核 | 高频 + 高 I/O，Helios 机架内配 GPU | agentic 编排/控制平面（低延迟） |
| **Venice** | 高密度 | **256 核**（192→256，1.3× thread density） | 高并发 agents / 通用吞吐 |
| **Venice（128 核版）** | 通用 | 128 核，平衡 | 企业通用计算 |
| **Venice-X** | 缓存增强 | **3D 堆叠缓存**（cache chiplet 在 compute chiplet 下方） | 数据密集/大集驻留负载 |

**Zen 6 技术底座**：TSMC **2nm**（compute chiplet）、224G SerDes（448G 为铜缆/光切换点）、**PCIe Gen6**、2.5D 封装、第 5 代 Infinity Fabric、"EPYC 历史上最大代际提升之一"、新增 AI 数据类型支持（Zen 7 更多 AI）。2027 Verano（下一机架 CPU）、2028 Florence（Zen 7）、2030 Rivenna（Zen 8）。

**Helios 机架中的 CPU 角色**：1 Venice : 4 GPU；72 GPU 机架配 ~18 CPU。CPU 承担 agent 编排、工具执行、GPU 喂料；GPU 专注张量。宣称 2× perf/agents per watt vs 竞品、2.2× per socket vs NVIDIA Vera（厂商口径）。

**市场叙事**：server CPU 营收份额 **46%**（历史新高，剑指 50%+）；CPU 市场 2030 $220B；"10/10 社交媒体 + 10/10 大型 SaaS 组织已转换"；公有云 EPYC 采用 3× YoY。x86 兼容性 vs Arm 迁移成本是反复强调的护城河。

**边缘/本地 agentic**：MI350P（HBM PCIe 推理卡，对标 Hopper PCIe 档）+ 企业分布式 agentic（智能路由 -43% token 成本）+ Ryzen AI（9B 本地模型）+ Gorgon Halo（192GB LPDDR5X 本地 agent 开发箱）——"Personal AI is not a concept. It is a category."

**AMD CPU 策略小结**：①高频核（控制面）+ 高密度核（吞吐）双轴，用 SKU 多样性覆盖 agentic 全角色；②Helios 以 1:4 的 CPU:GPU 低成本结构打价格战；③x86 存量 + 开放平台（ROCm）拿企业/主权客户。路线关键词：**多样性 + 密度 + 开放**。

### 3.3 Intel：E-core 密度 × 解聚编排叙事 × 平台收缩

**策略定位**：Intel 是三家最"被动受益"的——CEO Lip-Bu Tan 在 Computex 2026 直言："agentic AI is more balanced. It's not just leveraging the GPU, but needs plenty of CPU time as well" → "spike in demand for data center CPUs"。官方 demo 量化：**agentic 负载 CPU 需求略高于 GPU 需求**。

**Xeon 6+（Clearwater Forest）**：**18A 制程、288 E-core**、密度/能效向。核心卖点：**1 机架 Xeon 6+ 跑 150K agents**（密度叙事，营销上限需打折）。与 P-core Xeon 6（Granite Rapids）形成 P/E 双线。Intel 官方："The next wave is not just about training models, it is about putting AI to work."

**Diamond Rapids（Xeon 7）重大调整**：

- **推迟到 2027**（此前预期 2026H2）
- **砍掉 8 通道主流平台**（官方确认："removed Diamond Rapids 8CH from our roadmap, simplifying with focus on 16 Channel processors"）——合并双平台战略，主流服务器被迫上 16 通道（成本上升，但简化产品线）
- 16ch DDR5 + PCIe Gen6，2026H2 行业整体转 16ch（AMD Venice 同步）

**解聚推理叙事（SambaNova 合作）**：SN-50 机架 = Intel Xeon + SambaNova NPU；分工明确：**GPU=prefill+prompt caching、RDU=decode+token generation、CPU=orchestration+tooling execution**；宣称 2-3× faster than GPU-only。这是三家中最清晰地把"CPU 角色=编排+工具执行"写进架构分工的表述，与 agentic 负载特征完全对齐。

**其他**：Crescent Island（Xe3P 数据中心推理卡，LPDDR5X，350W PCIe）；Jaguar Shores（高端加速器，未发布）；Rackscale Blueprints 计划 + Foxconn 合作（对标 NVL72/Helios 的机架方案）；IDC 预测 2030 年 >80% 服务器仍 x86（Intel 反复引用的存量护城河）。

**Intel CPU 策略小结**：①E-core 密度（288 核）打"agents/rack"营销；②解聚架构中 CPU 官方定位 = orchestration + tooling（与 agentic 第一性特征完全吻合）；③平台收缩（砍 8ch）聚焦 16ch 高端；④x86 存量 + IDC 预测作为信心锚。路线关键词：**密度 + 存量 + 平台简化**。

---

## 4. Part C：共性 · 分化 · 趋势

### 4.1 三个共性（叙事收敛的强信号）

1. **"Agentic 需要 CPU"已成为三家官方叙事**（AMD AAI 2026、Intel Computex 2026、NVIDIA Groq 收购/推理战略），而非第三方推测——这是 2026 年 AI 基础设施最显著的观点拐点之一（此前 CPU 在 AI 叙事中基本隐身）。
2. **异构解聚是共识方向**：三家都在做/讲"把推理拆成 prefill（吞吐）/decode（延迟）/编排（控制）三段，各用最合适的硬件"——NVIDIA（GPU+LPU+CPU）、AMD（GPU+Cerebras WSE 超低延迟组合+CPU）、Intel（GPU+RDU+CPU）。**CPU 在三段式中都是"编排+工具执行"的不可替代角色**。
3. **CPU 内存子系统成为新战场**：KV 外溢 + 长上下文 + 工具数据 → 内存带宽/容量/模块化成为卖点：16 通道转正（AMD/Intel）、SOCAMM 模块化（NVIDIA）、3D 缓存（AMD Venice-X）。

### 4.2 三条路线分化

| 维度 | NVIDIA | AMD | Intel |
|:-----|:-------|:----|:------|
| CPU 架构 | **自研核**（Olympus，Arm ISA） | x86 Zen 6（2nm） | x86（18A）P/E 双线 |
| 差异化技术 | graph prefetcher、memory renaming、NVLink-C2C 集成 | 224G SerDes、SKU 四型、3D 缓存 | 288 E-core 密度、AMX |
| CPU:GPU（机架） | 2:4（36/72） | 1:4（18/72） | 无固定比例（通用服务器+机架蓝图） |
| 推理延迟解法 | **买 LPU**（Groq） | 合作 Cerebras WSE | 合作 SambaNova |
| 竞争核心 | 生态锁定（NVLink 集成） | 性价比（agents/watt）+开放 | x86 存量 + 密度营销 |
| 主要风险 | SPEC 成绩平庸、自研核生态成本 | Venice 产能/Helios 软件栈（ROCm 6 周发布节奏追赶） | Diamond Rapids 推迟 2027 的空窗、8ch 砍掉丢主流市场 |

### 4.3 对超节点/服务器设计的启示（映射用户领域）

1. **CPU:GPU 比例是系统级决策点**：1:4（AMD，成本优先）vs 2:4（NVIDIA，控制面优先）的差异本质是"agentic 负载里 CPU 独有职责（编排+工具）到底需要多少算力"的定价分歧。超节点设计时**不能只按 GPU 算账**——CPU 核数、内存带宽、I/O 必须按 agent 并发数 × 工具执行占比规划。
2. **CPU 内存带宽 = KV 外溢的关键**：长上下文 agent 会话的 KV 必然外溢到 DRAM（第二层），CPU 内存通道数/带宽（16ch、SOCAMM、CXL）直接决定外溢成本——这与 [08-05 IO 专题] 的"KV 三层分层"结论闭环。
3. **"编排 CPU 池"可独立规划**：若 agentic 负载占比较高，可考虑 CPU 池化（编排/工具/沙箱独立于 GPU 节点），与 G3.5 分层、控制流/数据流分离原则一致（控制面爆炸半径>数据面）。
4. **x86 vs Arm 的 agentic 视角**：agentic 的工具执行/沙箱/企业软件栈重度依赖 x86 存量（AMD/Intel 反复强调），NVIDIA 靠"自研核+集成"绕开兼容性问题——**选择 Arm CPU 的 agentic 平台要额外支付工具链兼容成本**。
5. **密度 vs 延迟的核型分化**：编排控制面（延迟敏感）要高频核（Venice HF/P-core/Olympus），批量 agents（吞吐）要高密度核（Venice 256/Xeon 6+ 288）——超节点的 CPU 选型也应按 P/E 或 HF/高密度双型配置，而非单 SKU 通吃。

### 4.4 关键判断与可证伪预测（2026-08 立，供复盘）

1. **P1**：2026H2~2027 各厂商（AMD/Intel/NVIDIA）发布的新一代数据中心 CPU，都会在 keynote 中把"agentic 负载 CPU 占比"作为第一性能指标（类似当年"每瓦 token"叙事）。可证伪：某家旗舰 CPU 发布只谈传统 SPEC 指标。
2. **P2**：Diamond Rapids 推迟到 2027 + 砍 8ch 后，Intel 在 2026H2~2027 主流 8 通道市场出现空窗，AMD Venice（含 128 核通用版）将加速收割该价位段。可证伪：Intel 提前发布 8ch 替代平台。
3. **P3**：解聚推理（prefill/decode/编排三段异构）将在 2026-2027 从"厂商 demo"走向"主流推理架构"，CPU=编排+工具执行成为标准分工。可证伪：主流推理框架（vLLM 等）仍以"GPU 单体"为默认部署形态且无解聚方案普及。
4. **P4**：CPU 内存带宽/容量（KV 外溢）将进入 CPU 规格对比表的核心位置（与核数并列），16 通道成为 2027 数据中心 CPU 事实标准。可证伪：2027 年旗舰 CPU 仍以 12 通道为主。
5. **P5**：NVIDIA Vera 的 graph prefetcher / memory renaming 等"为指针密集型负载设计"的特性，会在 agentic 基准（如 SWE-bench 类工具调用负载）上被单独评测并成为竞品模仿对象。可证伪：两年内无第三方基准体现该特性价值。

---

## 5. 来源与验证

**主要来源（ServeTheHome，2026-08 实况/披露）**：

1. STH《AMD Advancing AI 2026 Keynote Live Coverage》（2026-08，Lisa Su 全程实录：agentic CPU 叙事/$220B CPU 市场/Venice 四型/Helios 量产/MI350P/Florence 2028）
2. STH《AMD EPYC Venice 2026 with 1.3x Thread Density and 1.7x Performance》（FAD 2025 背景 + 2026 更新）
3. STH《AMD Helios Architecture Deep Dive》（72 GPU 机架规格：2.9 EFLOPS/31TB HBM4/1.7PB/s/260TB/s scale-up）
4. STH《AMD's EPYC Venice, Instinct MI455X, Helios Hardware on Display at CES 2026》
5. STH《Diving Deeper on NVIDIA's Vera CPU: New Architectural Details and SPEC CPU 2026 Benchmarks》（Olympus 架构全披露：18 pipes/graph prefetcher/memory renaming/L1 规格/SPEC 成绩")
6. STH《Decoding the Future of Inference At NVIDIA: Groq LPUs Join Vera Rubin Platform for Low-Latency Inference》（GPU+LPU 分工/35× TPS-per-user/LP30 规格）
7. STH《Intel Cancels its Mainstream Next-Gen Xeon Server Processors》（Diamond Rapids 8CH 官方确认砍除/16ch 聚焦）
8. STH《Intel Computex 2026 Keynote Live Coverage》（Xeon 6+ 288 核/150K agents/agentic CPU>GPU demo/SambaNova 解聚/Rackscale Blueprints/Diamond Rapids 2027）
9. STH《Micron SOCAMM Memory Powers Next-Gen NVIDIA Grace GB300 Servers》（GB300 内存形态）

**素材分级**：

- **厂商叙事**（需独立验证）：perf/agents per watt ×2、2.2× per socket vs Vera、150K agents/rack、35× TPS-per-user、2-3× 解聚加速、$220B/$1.4T TAM——均为 AMD/Intel/NVIDIA/伙伴（SambaNova/Cerebras）口径，未找到独立第三方复测。
- **独立披露**（STH 一手/官方白皮书）：Olympus 架构规格、Diamond Rapids 8CH 砍除（Intel 官方声明）、Venice 256 核/2nm/224G、SOCAMM 模块化——可采信。
- **本专题推算**：CPU 负载占比量级、CPU:GPU 比例对比、agents/核估算——为工程估算，标注如上。

**知识库交叉引用**：本专题与 08-04 全链路推理（KV 瓶颈）、08-05 IO 特征（KV 三层分层）、[超节点定义与设计哲学]（CPU 池化）、[AMD Helios 跟踪]（UALoE/机架规格）形成闭环。

---

## 6. Changelog

- 2026-08-05 | 初版：Agentic CPU 特征六角色拆解 + NVIDIA/AMD/Intel 三策略深度解读 + 五条可证伪预测 | 数据源：STH 2026-08 实况 9 篇
