# StrataCL 深度分析：Fabric-Native 通信库——registration-on-allocation + NPU-core 分区 + SDMA 卸载

> **元信息**：arXiv:2607.26444 [cs.DC]，2026-07-29 提交 v1；2026 ACM SIGOPS Annual Technical Conference (SOSP) 录用（2026-11，香港）
> **作者**：北京大学（Tiancheng Hu, Yuzheng Wang, Tao Xie）+ 中科院计算所 SKLP（Jin Qin, Ke Liu, Huimin Cui, Chenxi Wang）+ 上海交大 + 华为（Jieru Zhao）
> **平台**：华为 CloudMatrix384（CM384），Ascend 910C ×384，Unified Bus（UB）scale-up fabric
> **核心主张**：现有通信库是 **buffer-centric**（用户缓冲与通信缓冲分离管理→冗余拷贝/昂贵注册）；StrataCL 做到 **zero-redundancy + fabric-native**：registration-on-allocation 用户缓冲直通 + 全网格（full-mesh）执行 + 负载均衡 NPU-core 分区 + NPU 驱动 SDMA 卸载

---

## TOC

- [1. 一句话结论](#1-一句话结论)
- [2. 背景与问题：buffer-centric 为何是错的（第一性原理）](#2-背景与问题buffer-centric-为何是错的第一性原理)
- [3. 平台基础：CM384 / 910C / UB 架构细节](#3-平台基础cm384--910c--ub-架构细节)
- [4. 核心机制 1：registration-on-allocation（含 Shadow VA / VMM 兼容 / 反注册）](#4-核心机制-1registration-on-allocation含-shadow-va--vmm-兼容--反注册)
- [5. 核心机制 2：Full-Mesh 编程抽象（remote-slice 执行模型）](#5-核心机制-2full-mesh-编程抽象remote-slice-执行模型)
- [6. 核心机制 3：Workload-balanced NPU-core Partitioning（含 NP-hard 证明与 LPT 推导）](#6-核心机制-3workload-balanced-npu-core-partitioning含-np-hard-证明与-lpt-推导)
- [7. 核心机制 4：NPU-Driven SDMA Offloading（双完成机制）](#7-核心机制-4npu-driven-sdma-offloading双完成机制)
- [8. 数据推导全过程（从公式到实证）](#8-数据推导全过程从公式到实证)
- [9. 评估结果：operator 级 + 端到端 + 消融](#9-评估结果operator-级--端到端--消融)
- [10. 竞品对比矩阵](#10-竞品对比矩阵)
- [11. 辩证批判：8 项局限](#11-辩证批判8-项局限)
- [12. 与知识库连接 + 可证伪预判](#12-与知识库连接--可证伪预判)
- [13. 结论](#13-结论)

---

## 1. 一句话结论

**StrataCL 把通信库从「缓冲搬运工」重构为「fabric 原生执行器」**：用异步注册（registration-on-allocation）把昂贵的内存注册移出关键路径（利用「分配→首次通信」天然存在秒级间隔的观察），用全网格单步执行消除多步算法的累积同步开销，用最小 makespan 建模消除 NUMA 导致的核心级长尾，用设备侧 SDMA 卸载把通信占用的 NPU 核心释放回计算。在 CM384 上实现 collective 总线带宽最高 1.6×、MoE dispatch/combine 最高 1.4×、LLM 推理吞吐 1.9×、P99 TTFT 降低 2.2×、LLM/Recsys 训练迭代时间降低 1.4×/1.3×。

---

## 2. 背景与问题：buffer-centric 为何是错的（第一性原理）

### 2.1 通信占比随规模膨胀

论文给出的通信开销基线（§1）：
- LLM 推理中通信算子占端到端时间 **10%~40%**
- 训练中占 **30%~45%**
- 当算力增速超过互联带宽增速时，通信/计算比可**超过 50%**

> 第一性判断：模型并行（TP/EP/FSDP）的本质是把「数据搬运」变成「性能瓶颈」，而通信库的职责就是让搬运**不碰缓冲、不占核心、不产生同步**。

### 2.2 buffer-centric 的两大结构性浪费

**浪费 A：冗余 staged 拷贝（staging traffic）**

对 N-rank AllGather、每 rank M bytes（§2.2）：
- 标准 HCCL 路径：每个 rank 先把 M bytes 从用户输入缓冲拷入内部通信缓冲，再把 gathered 的 N·M bytes 从通信缓冲拷回用户输出缓冲
- **staging 流量 = M + N·M = (1+N)·M bytes**
- N=32 时 staging 开销是净数据量的 **33 倍**（对端点而言）

chunked-pipelined 执行只能**部分隐藏**拷贝成本，且 pipeline 仍占用 NPU 核心、与重叠的计算内核争抢（§2.2）。

**浪费 B：昂贵且不可扩展的 just-in-time 注册**

RDMA 式注册的完整开销链（§2.3/§3.1）：pin GPU pages → 经 PCIe BAR 建立 DMA 映射 → 创建 memory region 元数据 → 跨 rank 交换 remote key/VA——可达**数毫秒**。UB 因全局统一物理地址空间把注册降到微秒级，但 JIT 注册仍有两个问题：
1. **锁竞争**：每次映射取 write-side page-table lock，同 rank 的 per-peer 映射必须串行 → 全 N-rank 通信组注册延迟 **O(N)/rank**，随 rank 数近线性增长（Figure 5a）
2. **动态分配失配**：MoE 推理的 dispatch buffer 大小随 batch 的 token 路由动态变化 → 缓存失效 → 注册反复回到关键路径

### 2.3 池化方案的死结（HBM 效率 vs 框架兼容）

预注册通信内存池（pool-based）看似简单，但（§3.1）：
- **独立池** = HBM 容量税：池容量与框架分配器隔离，直接降低最大可支持 batch size
- **共享池 + 静态 v2p 映射**（如 SwiftEP 路线）：与现代 on-demand VMM API 分配器（PyTorch expandable-segment）冲突

论文量化了关闭 expandable segment 的碎片代价（Figure 5b）：
- DeepSeek V4 Flash 推理：每 NPU die 损失 **1–2 GiB** 可用内存
- DeepSeek V3.2 671B 训练：每 die 损失 **3–4 GiB**
- 直接后果：batch size 下降 → 端到端吞吐退化（HCCL-zerocopy 池化在推理中被迫把 batch 降 3，§8.2）

> **核心洞察**：注册的问题不是「太贵」而是「时机错」——物理分配与首次通信之间天然隔着**秒级**间隔（LLM 推理至少 2.6s，§9.4），注册完全可以异步、后台、提前完成。

---

## 3. 平台基础：CM384 / 910C / UB 架构细节

### 3.1 硬件拓扑（§2.1）

```
CM384 = 12 compute racks x 4 nodes/rack x 8 NPUs/node = 384 Ascend 910C NPU
        |
        +-- L2 UB switch  --- inter-node interconnect (aggregates L1)
        |      |
        +-- L1 UB switch  --- intra-node interconnect (8 NPUs/node)
```

- **UB（Unified Bus）**：scale-up fabric，~400 GB/s，纳秒级远程 HBM 访问延迟
- **Ascend 910C**：双 die 封装，die 间 SIO fabric **540 GB/s** 聚合带宽
- **每 die**：24 AI Cores（1 Cube Unit AIC + 2 Vector Cores AIV）+ 标量单元；64 GB HBM @ 1.6 TB/s
- **关键**：通信内核跑在 **AIV 核心**上（论文中「NPU core」= AIV），每 die 共 **48 个 AIV**；每 AI Core 有 KB 级 unified buffer + MTE（HBM↔SRAM 搬运）；SDMA 引擎支持 NPU 间搬运（通常 host API 启动）

### 3.2 UB 的 NUMA 特性（§3.2 Table 1）

| 相对位置 | 延迟 (µs) | 单向带宽 (GB/s) |
|:---------|:---------:|:---------------:|
| Die-to-Die（同 NPU） | 0.2 | 210 |
| Intra-node（同 node 跨 NPU） | 0.7 | 170 |
| Inter-node（跨 node） | 2.1 | 150 |

**量化推导**：跨 node 相对 die-to-die——延迟 **10.5×**（2.1/0.2）、带宽 **-29%**（150/210）。这就是「统一地址空间 ≠ 统一访问成本」的物理基础。

### 3.3 UB 注册 vs RDMA 注册（§2.3）

UB 注册四逻辑步：远端 export 物理句柄 → 本地 import → 预留本地 VA → 映射到远端 HBM。与 RDMA（pin + PCIe BAR DMA 映射 + memory region + key 交换）相比平均 **9× 快**（Figure 4a）。小负载时 handle export/import 占大头，大负载时 mapping 步主导（page-table 更新随注册大小线性增长）。

---

## 4. 核心机制 1：registration-on-allocation（含 Shadow VA / VMM 兼容 / 反注册）

### 4.1 机制总览（§5.1）

**拦截与两阶段机制**：

1. **拦截层**：hook `aclrtMalloc` / `aclrtMapMem`，仅物理内存事件触发
2. **Phase 1（异步后台）**：物理分配完成后立即——① 导出物理句柄 → ② 广播元数据（owner NPU, VA, size, v2p）→ ③ 各 peer NPU 把同一 VA 映射到 owner 远端 HBM 物理页（经 UB）
3. **Phase 2（首次访问，本地检查）**：通信算子首次触碰区域时，仅本地验证自己的 UB 映射已完成（无跨 NPU 同步，开销可忽略）
4. **正确性保证**：Phase 2 的 readiness barrier——最坏情况与 JIT 注册相同

**为什么可行**：现代框架分配器（PyTorch caching allocator）启动时预留大段 VA 段并跨迭代复用；常见的 tensor 分配只是从预映射段取 VA。分配与首次通信之间隔是**秒级**（LLM 推理最小 2.6s），远大于微秒~毫秒级注册成本（§9.4）。间隔主要由 warm-up 活动构成：graph capture、KV-cache 分配、模型权重加载。

### 4.2 Shadow Virtual Addressing（§5.2）

**问题**：同一物理内存在不同 NPU 上可能映射到不同 VA → 通信算子需要逐 peer 地址转换 + 每 NPU 维护地址转换元数据，随规模成本上升。

**方案**：把「虚拟地址规划」与「物理内存所有权」解耦——
- 初始化时给每个 NPU 分配**互不重叠的 VA 区间**（VA 空间远大于 HBM 容量，压力可忽略）
- NPU i 在 VA v 分配缓冲 → 每个 peer 在**自己的地址空间预留同一 v**，经 UB 映射到 i 的物理页
- 结果：所有 NPU 用**同一 v** 访问该缓冲 → 通信算子免地址转换，零 per-peer 翻译元数据

### 4.3 VMM API 兼容（§5.3）——增量注册

PyTorch expandable-segment allocator 破坏「v2p 固定」假设：预留大 VA 范围、按需映射物理页 → 新物理页可能映射到已有 VA 而 peer 不可见。

**方案**：把运行时映射当作**轻量增量注册**——拦截映射、异步重放 shadow mapping（只注册新映射区域，而非整个 VA 范围）。若新映射区域在异步 UB 映射完成前被访问 → 同步 barrier 兜底（不劣于 JIT）。

**开销量化**（§5.3）：
- MoE 连续 batching 中运行时重映射仅在 **<4%** 的请求 batch 触发
- 触发时 map 与首次通信间仍有**数十毫秒**间隔（中间有计算）足够隐藏 UB 映射延迟
- 总体端到端开销 **<0.6%**
- 元数据交换走 CPU 侧直接访问 peer DRAM 的快速通道（§7，60µs → 7-8µs）

### 4.4 内存反注册（§5.4）——非阻塞

- tensor free 只还块给 caching allocator（物理内存未变）→ **无动作**
- 仅物理释放（aclrtFree 物理段 / VMM unmap 回收页）才触发反注册
- 关键性质：UB 地址转换允许多个 VA 映射同一物理页 → 每个 peer 的 shadow mapping 只是**独立别名**
- owner 释放后：本地 VA 立即回收；peer 侧 UB unmapping 后台异步进行；**被释放物理段在新映射全部移除前不用于新通信分配**（防 stale 远程访问）

---

## 5. 核心机制 2：Full-Mesh 编程抽象（remote-slice 执行模型）

### 5.1 为什么全网格优于 ring（§3.2 量化）

| 对比项 | ring/PAT/recursive halving-doubling | full-mesh |
|:-------|:-----------------------------------|:----------|
| 步骤数 | N-1 步互相依赖 | 单逻辑步（并发内存指令） |
| 同步开销 | 小负载 >50%，64 KiB 时 **~77%** | 几乎为零 |
| 性能 | <1 MiB 平均慢 **2×**，64 KiB 慢 **4.5×** | 领先直到 8 MiB |
| 转折点 | **>16 MiB 后 ring 更优**（fan-out/网络竞争超过同步收益） | — |

> **本质**：RDMA scale-out 网络中 ring 的意义是降低瞬时 fan-out、避开慢跨节点路径；但在超节点 fabric 里「同步」才是第一成本，full-mesh 用单步并发把同步几乎清零。

### 5.2 Remote-slice 执行模型（§6.1）

通信算子被分解为一组 remote-slice 传输：

```
<peer, src, dst, bytes, op, flag>
  |      |    |    |     |    `-- optional dependency signal
  |      |    |    |     `-- remote action: load / store / atomic
  |      |    |    `-- slice size
  |      |    `-- dst VA in shared address space
  |      `-- src VA in shared address space
  `-- remote NPU identifier
```

**不同算子 = 改两个字段**：slice map（哪个 peer 访问哪些字节范围）+ remote-memory action（load/store/atomic）。

### 5.3 最小同步策略（按算子语义）

- **数据搬运类**（AllGather/AllToAll）：**pull 模式**——每 rank 直接读远端切片写入本地输出缓冲，避免 producer-consumer 握手
- **归约类**（AllReduce/ReduceScatter）：远端操作数先 load 到片上 SRAM 缓冲，再累加到本地目标缓冲
- **多核心写同一内存**：MTE 的 atomic 指令让「SRAM→HBM 的 store」变成**原子 read-modify-write** → 多核心无软件锁累加部分和

### 5.4 统一内核骨架（frontend/backend 分离）

frontend 只生成 slice map + src/dst VA；backend 负责调度执行 remote-slice 传输 → 使得 §6/§7 的后端优化（核心分区、SDMA 卸载）可在统一抽象之下透明生效。

---

## 6. 核心机制 3：Workload-balanced NPU-core Partitioning（含 NP-hard 证明与 LPT 推导）

### 6.1 问题：核心级长尾的两个来源（§6.2）

1. **流量不均**（uneven traffic）：AllToAllv / MoE dispatch-combine 中不同 peer 交换不同流量
2. **NUMA 不均**（non-uniform access）：同一流量在不同相对位置（die/node 级）延迟/带宽不同

naive 策略（每 peer 固定 NPU-core 组）两个都不管 → 分配到重/慢 peer 的核心最后完成，其他核心在本地 barrier 空转。实测最快-最慢核心完成时间差 **~43%**（§9.6）。

### 6.2 建模：minimum-makespan + per-peer fairness（§6.2）

**单位切分**：peer p 的 payload B_p 切成细粒度传输单元，单元大小 S_t 是 tier 特定粒度（大单元省策略生成开销、小单元负载更细）。

**单位周期成本**（式 1）：

```
tau(s) = alpha_t + s / beta_t
            |           `-- transfer time = bytes / tier bandwidth
            `-- measured access latency of tier t
```

→ 流量不均被「单元数量」捕获，NUMA 不均被「tier 相关延迟/带宽」捕获。

**负载预测**（式 2）：x_{c,k,j}∈{0,1} 表示单元 j 由核心 c 在 stripe k 发出；核心 c 的预测负载：

```
L_c = sum_k sum_j x_{c,k,j} * tau_j
```

**主目标**（式 3）：最小化预测 straggler：

```
min max_c L_c
```

**防 fan-out 突发**（式 4-5）：stripe k 内同时指向 peer p 的核心数上界：

```
F_{k,p} = sum_c sum_{j in J_p} x_{c,k,j} <= H_t   for all k,p
```

H_t 按 UB tier 选择——把远程访问在时间上摊开，而非让多核心同时打同一目标。

### 6.3 NP-hardness 证明（Appendix B）——归约 P||Cmax

判定问题：能否分配单元到核心与 stripe，使 makespan ≤ T 且满足 fan-out cap？

**归约构造**：给定 P||Cmax 实例（C 台机器、作业 J、处理时间 a_j、目标 makespan T）→ 构造 NPU-core partitioning 实例：C 个核心、每作业一个单元、τ_j = a_j、全部放同一 tier 和 peer 组、fan-out cap H_t = C。因每核心每 stripe 至多发一个单元，任一 stripe 总单元数 ≤ C，fan-out cap 永不约束 → 问题退化为 C 机器最小化最大负载。**双向成立** → 原问题 NP-hard。

### 6.4 LPT 近似与理论界（Appendix B/C）

- 无 fan-out 约束时退化为经典 LPT：`C_max^LPT ≤ (4/3 − 1/3C) · C_max*`（Graham 1969）
- 有 fan-out 约束时经典界不直接适用（constrained variant）
- **策略生成复杂度**：O(U log U + U log C)，U = Σ_p ⌈B_p/S_t(p)⌉ 为原子单元总数；O(U log U) 来自排序、O(U log C) 来自 LPT 最小负载堆维护
- **实测开销**：32-rank 128 MiB AllGather，24 个通信核心，策略生成 ~**40µs < 0.5%** 算子端到端延迟；可与元数据交换重叠；稳定形状的规则 collective 可**缓存复用**策略
- **效果**：最快-最慢核心差 43% → **<5%**，makespan **-19%**（§9.6）

### 6.5 MoE 分层变体（Appendix D）——三层粒度

token 级策略生成开销随路由 token 数增长（prefill 时 token 数大）→ 分层：

```
Level 1 token placement : reuse MoE routing metadata (target expert, per-expert
                          counts, prefix-sum offsets, token-local offsets) - zero extra cost
Level 2 expert-window   : group tokens with same peer+expert into contiguous window
                          (base offset + token-local indices, keeps token-level placement)
Level 3 peer-window     : aggregate by peer -> B_p / tier t(p) / unit count n_p
                          -> compute NPU-core partition policy at peer-window granularity
```

**效果**：策略生成输入规模从「路由 token 数」降到「活跃 expert-window 与 peer 数」——长 prefill 也保持低开销，同时自适应动态路由偏斜。

---

## 7. 核心机制 4：NPU-Driven SDMA Offloading（双完成机制）

### 7.1 问题：饱和带宽 = 核心税（§3.2）

达到 UB 峰值带宽的 **95% 需要 24 个 NPU 核心**（48 的一半，Figure 6b）→ 计算-通信重叠场景（FSDP 参数预取 / Two-micro-Batch Overlapping）中严重争抢计算核心。

### 7.2 方案：设备侧 SDMA 下发（§6.3）

- 传统 host-triggered SDMA：每传输过 CANN runtime + host 控制路径 → 对细粒度多传输的通信算子太贵
- StrataCL：**完全设备侧**——NPU 核心构造 SDMA 描述符 → 并发提交到 per-core 硬件队列 → 直接 ring SDMA doorbell

### 7.3 双完成机制（按数据消费方式选择）

| 模式 | 数据消费 | 同步机制 | 适用 |
|:-----|:---------|:---------|:-----|
| I: in-kernel | fused dispatch/combine 等内核内消费 | 发送方追加**尾描述符**写状态标志到 peer，少量 NPU 核心 poll 本地标志 | 内核内融合场景 |
| II: cross-kernel | collective 后接独立计算内核 | SDMA 队列追加 notify 记录，AI CPU 等待通知后才放行下游 | 吞吐导向重叠（内核级同步点，但核心在描述符提交后完全释放） |

### 7.4 权衡量化（§9.5）

- MTE 路径：核心几乎全程占用（搬运）
- SDMA 路径：核心只在描述符提交期占用 → **核心占用 -95%+**
- 代价：延迟 **+9%**（描述符构造 + doorbell 提交）
- **净收益为正的判据**：重叠场景中释放的核心回到计算，收益 > 9% 延迟损失

---

## 8. 数据推导全过程（从公式到实证）

### 推导 1：staging 流量公式（§2.2）

N-rank AllGather、M bytes/rank：
- 入向 staging：M（每 rank 用户输入 → 通信缓冲）
- 出向 staging：N·M（gathered 数据通信缓冲 → 用户输出）
- **总 staging = (1+N)·M**；N=32 → 33×M
- 实证：HCCL-zerocopy 对 >8 MiB 负载提升 >30% bus 带宽（Figure 3a）；FSDP 重叠训练中 HCCL 使并发计算内核慢 25%，zerocopy 只慢 13% → 消除 staging 争抢带来额外 **6%** 端到端加速（串行基线 vs 重叠：HCCL -26% step 时间，zerocopy -31%）

### 推导 2：JIT 注册的 O(N) 扩展性（§3.1）

每次映射取 write-side page-table lock；同 rank per-peer 映射串行 → N-rank 组注册延迟 ≈ N × per-peer 延迟 → **近线性增长**（Figure 5a 实证）。这解释了为何缓存注册对动态分配（MoE dispatch 大小随 batch 变化）失效。

### 推导 3：同步 vs fan-out 的交叉点（§3.2）

full-mesh 收益随消息增大递减：同步开销占比从 >50%（小负载）降到 64 KiB 的 ~77% 峰值（ring 侧），但大负载时 full-mesh 的并发远程访问引发 fan-out 与网络竞争 → **16 MiB 后 ring 反超**。这是「算法选择必须 workload-aware」的定量依据（§9.2 亦证实 256 ranks 大负载差距 <10% 且亚线性增长）。

### 推导 4：带宽饱和的核心数（§3.2）

95% 峰值需 24/48 核心 → 重叠场景通信吃掉一半核心预算。SDMA 卸载后核心占用 -95%，通信核心数需求从「搬运型」变「提交型」，为重叠让出计算预算。

### 推导 5：池化 vs RoA 的碎片账本（§3.1 + §8.2）

| 方案 | 注册成本 | HBM 碎片成本 | 框架兼容 |
|:-----|:---------|:-------------|:---------|
| JIT | 在关键路径，O(N) | 0 | ✅ |
| 池化（HCCL-zerocopy 实战） | 移出关键路径 | 推理 1.6 GiB/die（batch 被迫 -3）；训练 3 GiB+ 额外碎片 | ❌ 关掉 expandable segment |
| **RoA（StrataCL）** | 移出关键路径 | **0** | ✅ 保留 expandable segment |

推理中 HCCL-zerocopy 相比 HCCL 只提升 1.2×（碎片抵消算子级收益）；StrataCL 保持与 HCCL 相同 batch size → 1.9× / 1.6×（对 zerocopy）。

### 推导 6：端到端增益拆解（§9.1 Figure 13a，增量归因）

| 技术叠加 | 累计吞吐增益 | 边际贡献 |
|:---------|:------------:|:--------:|
| HCCL 基线 | 1.0× | — |
| + JIT 用户缓冲注册 | 1.1× | +0.1×（注册延迟吃掉零拷贝收益） |
| + registration-on-allocation | 1.4× | +0.3×（用户缓冲直通，注册离关键路径） |
| + workload-balanced 分区 | 1.7× | +0.3×（消除核心长尾） |
| + SDMA 卸载 | **1.9×** | +0.2×（通信不争抢计算核心） |

> 归因清晰：注册时机 > 核心负载均衡 > 核心释放，且**前三项缺一不可**——JIT 单独只有 1.1×，说明「零拷贝」必须配合「注册离关键路径」才兑现。

### 推导 7：MoE dispatch 数据流与带宽（§8.1 Table 2）

配置：4096 tokens/batch、hidden 7168、top-8 experts、EP=32。路由分布变化 → 各 peer payload 不均 → 正好命中 §6 的核心分区优化。

| 场景 | DeepEP (CX7 RDMA) | CANN EP | CANN EP zerocopy | **StrataCL** |
|:-----|:-----------------:|:-------:|:----------------:|:------------:|
| Dispatch HT | 61 | 98 | 106 | **130** |
| Combine HT | 61 | 85 | 93 | **121** |
| Dispatch LL | 50 | 61 | 82 | **107** |
| Combine LL | 55 | 68 | 79 | **108** |

- CANN EP vs RDMA DeepEP 平均 **1.4×**（UB 物理带宽 > CX7 400Gb/s + 免 NIC 转发路径）
- zerocopy 增益：HT +8.8%、LL +25.3%（LL 模式 staging 占比更高）
- StrataCL vs CANN EP zerocopy：**+22.6%~36.7%**（核心分区吃路由不均）

### 推导 8：allocation-to-communication gap（§9.4）

三生产负载全量画像：最小间隔**数秒**（LLM 推理至少 2.6s）≫ 注册成本（微秒~毫秒）→ RoA 可行性在**生产环境**而非合成测试中成立。间隔由 warm-up 构成：graph capture、KV-cache 分配、权重加载。

---

## 9. 评估结果：operator 级 + 端到端 + 消融

### 9.1 端到端设置（§8.2 Table 3）

| 负载 | 模型 | NPU dies | 并行度 | 关键通信 |
|:-----|:-----|:--------:|:-------|:---------|
| LLM 推理 | DS V4 Flash（SGLang，disaggregated） | 192 | prefill DP32+EP32 / decode EP16+DP16 | MoE dispatch/combine + TBO + MTP |
| LLM 训练 | DS V3.2 671B（TorchTitan） | 512 | FSDP=128 + TP=4 + EP=64，batch 512，seq 4096 | AllGather/ReduceScatter/AllReduce/dispatch-combine + FSDP 预取 |
| Recsys 训练 | DLRM（TorchRec，Criteo TB，7 TiB 嵌入表） | 128 | DP+MP（表级分片）batch 1024 | AllToAll + AllReduce |

### 9.2 端到端结果

| 指标 | StrataCL vs HCCL | vs HCCL-zerocopy |
|:-----|:----------------:|:----------------:|
| 推理吞吐 | **1.9×** | 1.6× |
| P99 TTFT（15 req/s） | **↓2.2×** | — |
| P99 TPOT（15 req/s） | ↓1.1× | — |
| LLM 训练迭代 | — | ↓18%~24%（zerocopy 只比 HCCL 好 6%） |
| Recsys 训练迭代 | ↓~23% | ↓~16% |

**要点**：
- 推理中 HCCL-zerocopy 只 1.2×（池化碎片强制 batch -3）；StrataCL 1.9× 主因 = 保持 batch size + 分区/SDMA 避免 TBO 下通信与计算争核心
- 训练中 zerocopy 只 6%（训练内存压力强、碎片 3 GiB+ 更严重）；StrataCL 18-24% 来自 RoA 免碎片 + SDMA 减 FSDP 预取争抢；后期迭代收益变小（gate 层改善 expert 负载均衡 → 流量更均匀 → 分区机会减少）
- Recsys：嵌入缓存越小 / per-worker batch 越大 → 缓存 miss 越多 → 远程嵌入传输占比越大 → 通信收益越显著

### 9.3 可扩展性与可移植性（§9.2/§9.3）

- **32→256 ranks**：StrataCL full-mesh 峰值带宽比 HCCL-zerocopy ring 低，但差距**亚线性且 <10%**（fan-out/竞争随规模温和增长）；大负载差距可由 workload-aware 算子选择策略（切回多步算法）弥补
- **NVIDIA 移植**（DGX B200 NVLink 5.0 8-rank 原型）：NCCL UBR vs NCCL 平均 +1.2×；RoA 版 +1.3× vs UBR JIT 1.2×——8-GPU 规模 JIT 成本未被放大，RoA 收益温和；**大 NVLink 域预期收益增大**（注册开销随 peer 数增长，与 CM384 观察一致）→ 证明 RoA 核心思想不依赖华为平台

---

## 10. 竞品对比矩阵

### 10.1 集体通信库维度

| 系统 | 冗余拷贝 | 注册时机 | 同步开销 | 核心占用 | 架构感知 |
|:-----|:--------:|:--------:|:--------:|:--------:|:---------|
| NCCL / HCCL / RCCL | 有（staging） | JIT | 多步算法高 | 全程占用 | 弱 |
| NCCL UBR / HCCL-zerocopy | 无 | JIT（关键路径） | 多步算法高 | 全程占用 | 弱 |
| NVSHMEM / rocSHMEM / CANN SHMEM（PGAS） | 无 | 预注册 | 低 | 高 | 中 |
| MSCCL++ / TACCL | 无 | — | 算法可定制 | 高 | 拓扑感知 |
| **StrataCL** | **无** | **异步预注册（离关键路径）** | **单步 full-mesh** | **-95%（SDMA）** | **UB NUMA 感知分区** |

### 10.2 MoE 专家并行通信维度

| 系统 | 优化手段 | 与 StrataCL 差异 |
|:-----|:---------|:-----------------|
| DeepEP v2 | token 洗牌 + fused dispatch/combine + 重叠 | RDMA 路径受 NIC 转发 + 物理带宽限制（CM384 上 1.4× 差距实证） |
| Tutel / FlashMoE / MegaScale-MoE | 专家路由 / 融合内核 / 重叠 | 偏算法层，不解决注册与核心争抢 |
| SwiftEP | buffer 融合减 staging | 仍用预分配池 → 碎片 + VMM 不兼容 |
| CANN EP (+zerocopy) | UB 原生 + 零拷贝 | 无核心分区 → 路由不均长尾（StrataCL 再 +22.6%~36.7%） |
| **StrataCL** | RoA + 分层分区 + SDMA | 把 MoE 通信优化推进到「注册/核心/带宽」三协同 |

### 10.3 DMA/引擎卸载维度

| 系统 | 机制 | 差异 |
|:-----|:-----|:-----|
| ARK | GPU 驱动 DMA 引擎免 CPU | StrataCL 的 SDMA 卸载同思路，但叠加全网格执行 |
| ConCCL / DMA Collectives | 并发 collective 卸载到 DMA/copy 引擎 | 面向 GPU；StrataCL 面向 NPU 全网格 + 双完成机制 |
| **StrataCL** | 设备侧描述符 + doorbell + 双完成 | 把卸载与 full-mesh/分区做成统一后端 |

---

## 11. 辩证批判：8 项局限

1. **大负载不敌多步算法**：>16 MiB（以及 256 ranks 大负载）HCCL-zerocopy 反超 ~6%——论文承认需要 workload-aware 算子选择策略但**未实现**（论文自承 limitation，非已解决）
2. **评估单平台为主**：全部核心实验在 CM384；NVIDIA 仅 8-rank DGX B200 原型，未验证 GB200 NVL72 真机的大域收益（论文的「预期增大」是外推非实证）
3. **910C 双 die 特殊性**：SIO 540 GB/s die 间带宽 + 48 AIV 结构是华为特有；「full-mesh 优于 ring」的交叉点（16 MiB）是 UB 参数下的结论，对 NVLink 域是否成立未验证
4. **SDMA +9% 延迟的代价边界未量化**：论文未给出 9% 延迟损失在何种负载/重叠度下会反超收益（净收益为正的判据只有定性论述）
5. **RoA 依赖分配器行为**：核心前提是「分配→首次通信秒级间隔」；对即时分配即通信的算子（某些动态图模式）RoA 退化为 JIT + barrier，收益消失（论文未测此退化模式）
6. **仅 4 个框架集成**：PyTorch/SGLang/TorchTitan/TorchRec 均华为生态深度适配；对 vLLM-Ascend、MindIE 等未覆盖
7. **论文未发布源码**：声称 will be released upon publication，当前无法复现（复现性缺口）
8. **碎片测量口径**：Figure 5b 的「可用内存块之和」指标为自定义口径，与标准 fragmentation ratio 的可比性需注意

**中立观察**：作者团队 = 北大 + 计算所 + 上交 + 华为——属「华为生态学术合作」模式（与 CloudMatrix 论文 Zuo et al. 2025 同源）；数据与华为产品强绑定，独立第三方复现前宜视为「厂商背书结果」。

---

## 12. 与知识库连接 + 可证伪预判

### 12.1 知识库连接

- [华为 Atlas 900 / 昇腾超节点](../../02_rd/01_product/00_hardware/01_hw-core/aiserver/2026-07-29-huawei-atlas900.md) — CM384 的上一代体系，HCCS 56 GB/s 级互联 vs UB 400 GB/s 级（量级跃迁的实证）
- [XCCL 集体通信库体系](../../02_rd/01_product/01_software/04-comm-lib/2026-06-04-xccl-collective-communication-libraries.md) — 华为通信库家族（HCCL/XCCL）的架构基线，StrataCL 是其 fabric-native 演进
- [华为 AI Fabric 深度分析](../../02_rd/01_product/01_software/04-comm-lib/2026-07-23-huawei-ai-fabric-deep-analysis.md) — UB fabric 硬件底座
- [MoE 硬件实现深度分析](../../02_rd/01_product/01_software/04-comm-lib/2026-07-24-moe-hardware-implementation-deep-analysis.md) — dispatch/combine 通信瓶颈的软硬协同
- [MoE 硬件影响](../ai-principles/2026-06-26-moe-hardware-impact.md) — MoE 通信瓶颈的硬件根源（流量模型）
- [GPU 节点互联框图方法论](../../02_rd/02_project/01_superpod/2026-07-16-gpu-node-interconnect-block-diagram-methodology.md) — 超节点「互联即架构」理念在本论文的落地
- [LLM 系统软件成熟化（TensorCast/B300/PLoRA/ViBE）](2026-08-10-llm-system-software-maturity-tensorcast-b300-plora-vibe.md) — 控制面/数据面分离第三次落地（StrataCL 的 CPU 直连 DRAM 通道是同一范式在通信库的体现）
- [Cascade SLO 延迟预算](2026-08-11-cascade-slo-latency-budget-scheduling-deep-analysis.md) — 调度层把预算作为统一信号；StrataCL 在通信层把「注册/核心/带宽」作为预算——同构的「资源会计」哲学

### 12.2 可证伪预判

| # | 预判 | 验证时间窗 |
|:--|:-----|:-----------|
| H1 | 源码发布后，第三方在 CM384 复现 collective 1.6× 需满足「小到中负载」条件；大负载（>16 MiB）需切多步算法 | 论文发表后 12 个月 |
| H2 | NCCL RoA 原型在 ≥32-rank NVLink 域（如 GB200 NVL72 多域）上相对 NCCL UBR 收益 >1.3×（注册 O(N) 放大） | 2027 年内 |
| H3 | 华为 HCCL 正式版在 1-2 个版本内吸收 RoA 语义（异步注册 + 影子地址） | 2027 年内 |
| H4 | 「full-mesh vs ring 交叉点 16 MiB」在 NVLink 5.0/6.0 域上偏移（更高带宽可能推高交叉点） | 独立移植验证时 |
| H5 | MoE 分层分区（expert-window/peer-window）成为国产 NPU 通信库标准模式 | 2027 年内 |

---

## 13. 结论

StrataCL 的价值不在单一技巧，而在**对超节点 fabric 的完整重构**：

**第一性链条**：

```
buffer-centric redundancy  = wrong registration timing  (fixed by RoA)
multi-step sync overhead   = sync > transfer           (fixed by full-mesh)
NUMA long tail             = topology-unaware           (fixed by partitioning)
NPU-core contention        = move-occupies > submit     (fixed by SDMA)
```

四个机制分别命中通信路径的四个独立成本项（拷贝/同步/长尾/核心占用），且**共享同一抽象**（remote-slice + 统一后端），从而在单一信号（NPU-core 调度）上实现协同。与 Cascade 的「预算会计」、TensorCast 的「控制面/数据面分离」共同构成 2026 年系统软件「资源会计化」趋势的通信层样本。

---

## Changelog（倒序）

- 2026-08-11：创建。基于 arXiv:2607.26444v1 全文（HTML 抓取核实）撰写深度分析，含公式推导（staging 流量/O(N) 注册/NP-hard 归约/LPT 界/分层复杂度）、评估数据全量表格、8 项局限、5 条可证伪预判
