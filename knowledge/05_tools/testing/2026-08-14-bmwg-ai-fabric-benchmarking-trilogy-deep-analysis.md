# BMWG AI Fabric 基准测试三件套深度分析（-04 版）

> **文档类型**：深度分析 | **主题**：AI 训练/推理网络 Fabric 基准测试标准化 | **日期**：2026-08-14
> **范围**：`draft-calabria-bmwg-ai-fabric-{terminology,training-bench,inference-bench}-04`（2026-08-12 同日更新）
> **适用读者**：AI 基础设施网络决策者 / 交换机测试工程师 / 超节点互联架构师

---

## 0. 一句话结论

**AI Fabric 基准测试正在从"各厂自说自话"走向"可比较的公共口径"**：BMWG 三件套用**黑盒 DUT 边界 + 禁止内部容量归一化 + 算法不变 BusBW + 可比较集（7 参数强制匹配）**四条铁律，把 AI 网络的性能度量从"交换机 ASIC 规格数字"拉回"应用可感知的 JCT/BusBW/TTFT"，为交换机横向对比提供了第一个真正可操作的标准化框架——但它刻意**不设 pass/fail**，落地阈值仍由运营者自定。

## 1. 摘要（5 条核心结论）

1. **三件套结构**：Terminology（42 页术语）+ Training Methodology（50 页训练方法论）+ Inference Methodology（49 页推理方法论），同日升 -04；作者 F. Calabria（Cisco）/ C. Pignataro（Blue Fern）等，BMWG 工作组相关草案（I-D Exists，Informational）。
2. **最锋利的设计**：**聚合交换容量（ASIC Tbps）被明文禁止作为归一化因子**——因为它是厂商声明、不可在 DUT 边界观测，除以它会"把结果更好的劣质 fabric 洗成更优"。归一化只允许用可观测的以太网线速率 + 固定 workload 参数（S, N, algo_factor）。
3. **测试方案规模**：训练 7 大测试类别（27 项测试）+ 推理 8 大测试类别（30 项测试），约 50 个测试用例全部给出 Objective/Procedure/Measurement/Reporting 四段式规格，且每个测试都锚定 RFC2544/RFC2889/RFC9004/UEC 1.0 等既有标准。
4. **训练/推理工作负载的分野被精确刻画**：训练 = BSP 周期性 collectives（AllReduce/AllGather/AllToAll）；推理 = 事件驱动突发 KV 缓存传输 + 细粒度 MoE AllToAll dispatch——推理侧为此新增 **Topology D（PD 分离）** 与 **SUT-E / DUT-PD 五级 DUT 定义**。
5. **对决策者的意义**：这是交换机横评的**标准口径就绪信号**——但草案仍处个人草案阶段、无 pass/fail、加速器互连（NVLink/UALink）明确在 DUT 边界之外，落地需自建阈值与扩展。

## 2. 背景与定位：为什么 BMWG 要做这件事

### 2.1 既有基准的空白

| 基准 | 覆盖 | 对 AI Fabric 的缺口 |
|:--|:--|:--|
| RFC 2544（1996） | 路由器/交换机吞吐·延迟·丢包·背靠背 | 单播线速模型；无 collective、无 RDMA、无拥塞语义 |
| RFC 2889（2000） | LAN 交换 | 无 RoCEv2/UET 传输、无 GPU 集群模型 |
| RFC 8238/8239（2017） | 数据中心基准 | 通用 DC 流量；无 AI 工作负载模式 |
| RFC 9004（2021） | 背靠背帧基准更新 | 仅帧级，不达 RDMA 语义 |
| MLPerf | 端到端训练/推理 | 测**系统**性能，不分解 **fabric 贡献**；DUT 不可隔离 |
| **BMWG AI Fabric 三件套** | **AI 网络 fabric 本身** | 填补"交换机/网络在 AI 系统中的真实贡献"度量空白 |

**核心动机**：AI 训练中网络开销直接影响加速器利用率（GPU 空等通信 = 算力浪费），而"交换机 51.2Tbps 规格"与"AllReduce 实际 BusBW 90% vs 60% 线速"是两个世界。买方需要**可复现、可比较、不可被规格书粉饰**的度量方法。

### 2.2 三件套在标准体系中的位置

```
BMWG legacy layer (RFC)
  RFC 1242/2544 -> RFC 2889/3918 -> RFC 8238/8239 -> RFC 9004 -> RFC 9411
                    (30 years of network device benchmarking methodology)

AI-era new layer (individual draft -> future RFC)
  draft-calabria-bmwg-ai-fabric-terminology-04        (terminology layer)
  draft-calabria-bmwg-ai-fabric-training-bench-04     (training methodology)
  draft-calabria-bmwg-ai-fabric-inference-bench-04    (inference methodology)
  |-- related: draft-gaikwad-llm-benchmarking-*   (LLM serving trilogy, 08-09)
  |-- related: draft-contreras-bmwg-ai-agent-benchmarking-00 (AI agent in NOC)
  `-- refs: UEC 1.0 Spec, MLPerf, Orca/PagedAttention/DeepEP papers
```

> **命名澄清（诚实边界）**：用户侧所称 "Profiles" 若指 08-12 同日更新，实际更新的是 **Terminology + Training Methodology + Inference Methodology** 三份；"Profiles" 精确命名对应另一组草案 `draft-gaikwad-llm-benchmarking-profiles-01`（LLM serving 性能画像，08-09 更新，非同日）。方法论文档内部的 "profile" 概念指 **UEC compliance profile（AI Base / AI Full / HPC）**。本分析以 08-12 三件套为准，两处均如实标注。

## 3. 设计哲学：四条铁律（第一性原理）

### 铁律 1：黑盒 DUT 边界 = NIC-to-NIC 以太网 Fabric

```
GPU Memory -> [PCIe/CXL] -> NIC    <- intra-node, OUT of DUT scope
NIC -> [ETHERNET FABRIC] -> NIC    <- DUT boundary (the only thing tested)
NIC -> [PCIe/CXL] -> GPU Memory    <- intra-node, OUT of DUT scope
```

- DUT 边界包含所有 leaf/spine 交换机及互连链路；**不进入节点内部**（PCIe/CXL/加速器互连不计入）。
- 推论：**NVLink/UALink 等 scale-up 加速器互连明确不在本方法论范围内**——它只测以太网 scale-out fabric（详见 §11 批判）。

### 铁律 2：聚合交换容量禁止归一化（本套件最反直觉、最锋利的一条）

禁止理由（草案原文逻辑）：
1. 交换容量是**厂商声明的内部属性**，黑盒观测不到；
2. **被测对象就是"容量够不够"**——除以容量等于消除被测效应：一半容量的 fabric 用 1.6× 时间完成同一 job，按每 Tbps 算反而"更好"；
3. 容量归一化值是成本/效率指标，超出 BMWG 章程（只定义测什么、怎么报）。

允许的归一化分母（全部可观测）：以太网线速率、B_acc（每加速器 NIC 线速和）、固定 workload 参数（S, N, algo_factor）。**交换容量、端口速率、radix、buffer 架构只作为 DUT 特征（附录 C）报告，用于归因解释，不作除数。**

### 铁律 3：BusBW 算法不变性

```
BusBW = (data_size x algo_factor) / time
algo_factor (fixed constants, independent of runtime algorithm):
  AllReduce     2 x (n-1) / n
  AllGather     (n-1) / n
  ReduceScatter (n-1) / n
  AllToAll      (n-1) / n
Example: AllReduce, n=8, 1GB, 10ms -> algo_factor=1.75 -> BusBW=175 GB/s
```

无论 CCL（NCCL/RCCL/oneCCL）运行时选 ring/tree/doubling，**同一硬件搬同一数据量=同一 BusBW**。报告必须声明 collective 类型、algo_factor、CCL 名称版本、n；运行时实际算法作为诊断信息（通过库 tracing 验证）。

### 铁律 4：可比较集（Comparability Set）——7 参数强制匹配才能横比

| 参数 | 不匹配的后果 |
|:--|:--|
| 参与加速器数 N | collective 成本经 algo_factor 与路径长度变化 |
| 每节点加速器数与 rail 映射 | 决定 fabric-visible 流量份额 |
| B_acc（每加速器 NIC 线速） | BusBW 效率分母 |
| Leaf 过订阅比 | 决定 fabric 能否满足供给模式 |
| Collective 类型 + 消息尺寸 S + algo_factor | workload 定义本身 |
| 传输（RoCEv2 / UET + 服务类型） | 丢包与重传语义不同 |
| 负载均衡策略 | 必须按策略对比 |

任一参数不同 → 结果并排报告 + 说明差异，**不得合成单一对比数字**。拓扑类（A/B/C/D）是报告条件而非可归一化参数——不同拓扑对比时须额外报告 tier 数、典型/最坏跳数、等价路径数、二分带宽。

### 铁律 5：Fabric-Visible Data Volume（S_fabric）

Collective 放置决定穿过 DUT 边界的数据量：分层 AllReduce（节点内先 reduce）比扁平 AllReduce 呈现给 fabric 的数据少。因此每个 collective 结果必须报告：S（应用级每参与者数据量）、S_fabric（穿过 DUT 边界的每参与者数据量，按 Fabric_Goodput 字节计数规则，**重传/重复字节不计入**，单独报 retx 率）、放置与 rail 映射、Intra-Node Transfer Overhead（**永不并入 fabric KPI**）。

## 4. 术语体系核心（Terminology -04）

### 4.1 KPI 三层分类（训练/推理统一）

| 层级 | 定义 | 训练示例 | 推理示例 |
|:--|:--|:--|:--|
| **Primary KPI** | 直接反映用户体验/训练效率，横比主指标 | JCT Ratio、BusBW | TTFT、ITL、TPS |
| **Secondary KPI** | 为 Primary 偏差提供机制解释（根因） | AllReduce BusBW、MMR、链路利用率 | AllToAll dispatch 延迟、KV 传输 goodput |
| **Fabric Health Indicator (FHI)** | 稳定性/异常度量（全程连续监测） | PFC 事件、ECN 比率、丢包、buffer P99、retx 率 | 同左 |

### 4.2 Goodput 双平面（禁止混淆）

- **Fabric_Goodput**：DUT 边界 RDMA 消息载荷字节/秒（排除传输头、帧开销、填充、重传字节）。KV_xfer_bandwidth、EP_alltoall_bandwidth 的分子。
- **Inference_Goodput**：成功完成（无抢占/驱逐/错误）请求的输出 token/秒。只对应 TPS_output 的成功子集。
- **两者平面不同，KV_xfer_bandwidth 测的是 Fabric_Goodput，不是 Inference_Goodput。**

### 4.3 零丢包语义（RoCEv2 vs UET 分治）

- **RoCEv2**：零线速丢包是目标运行条件（lossless 配置）。
- **UET**：设计容忍丢包（RUD 跨喷洒路径重传、packet trimming），接受标准是**零应用可见丢包**而非零线上丢包，且取决于传输服务（ROD/RUD/RUDI/UUD）。

### 4.4 推理专属关键术语

- **S_KV** = 2 × L × H_kv × D × C × P_bytes（单请求全层全 token KV 总字节；GQA/MQA 下 H_kv ≤ H_total）
- **T_dispatch** = (B × k × H_model × P_bytes) / N（MoE 每源-目的 GPU 对每层 dispatch 载荷）；T_egress = T_dispatch × (N−1)
- **xPyD**：PD 分离集群 prefill:decode 工作节点比（如 3P9D）
- **PD 阶段特征**（参考值，非规范）：Prefill 计算密集（200-400 ops/byte，利用率 90-95%）；Decode 显存带宽受限（60-80 ops/byte，利用率 20-40%）
- 附注定义：Continuous Batching（Orca）、PagedAttention、Prefix Caching、Expert Choice Routing、Normal/Low-Latency Dispatch（DeepEP，LLD 目标 <200µs/次）

## 5. 训练测试方案（Training Methodology -04）

### 5.1 参考拓扑（3 种）

| 拓扑 | 结构 | 规模/适用 |
|:--|:--|:--|
| **A：2 层 Clos**（Leaf-Spine） | spine 全互联（ECMP/DLB/Spray） | 通用基线 |
| **B：3 层 Clos**（L-S-Superspine） | pod 内 leaf-spine，pod 间 superspine | 数千加速器以上；**32,000+ accel @ 800GbE**（现役 ASIC） |
| **C：Rail-Optimized** | 每 NIC 接专属 leaf（rail），rail-N 连所有主机 GPU[N] | 与 CCL 局部性协同（NCCL/RCCL/oneCCL） |

### 5.2 流量生成器要求（测量可信度底线）

| 参数 | 最低要求 |
|:--|:--|
| 时间戳精度 | ≤ 100 ns |
| 帧率精度 | ±0.1% 设定值 |
| QP 扩展 | 1-256 QP/源-目的对 |
| 消息尺寸 | 64 B - 2 GB（单消息上限，>2GB 拆多消息并报告） |
| 突发生成 | 线速突发长度需超 DUT 缓冲，可配 >1000 帧 |
| 丢包测量 | 逐包精确计数 |

- **硬件 TG**：线速 RDMA 仿真（QP 建立、RDMA Write/Read、ECN、DCQCN 速率控制），适用于 P2P 测试；用于 collective 测试须声明是否复现同步屏障/调度驱动/straggler 行为。
- **加速器集群**：真实 CCL + RDMA 工具，collective 测试首选；非 fabric 计时开销单独量化。
- **交叉验证**：HW 生成器跑 collective 必须与真实集群在 ≥1 个 (msg_size, N) 配置互验，**BusBW/JCT Ratio 差异 >10% 须调查并报告**。

### 5.3 训练 7 大测试类别总览（27 项测试）

| 类别 | 测试项 | 核心规格 |
|:--|:--|:--|
| **TC1 RDMA 传输基准** | 5.1 基线吞吐 | 8 档消息（64B-4MB）× QP（1/4/16/32）× 单/双向；RFC2544 §26.1 二分搜索；每速率 ≥60s |
| | 5.2 延迟表征 | RFC2544 §26.2 标记帧；≥10,000 样本/run、≥20 次 run 合并分位数；0 负载 vs 满载；报 min/mean/P50/P95/P99/P99.9/max + 负载因子 |
| | 5.3 背靠背突发吸收 | RFC9004 扩展；incast 2:1-32:1；每突发长度 ≥50 次重复；报突发容量（帧+字节）vs incast 比 |
| **TC2 UET 传输协议** | 6.1 按服务吞吐 | ROD/RUD/RUDI/UUD vs RoCEv2 RC/UC 同 DUT 对比；PDC 1/4/16/32；报连接建立延迟 |
| | 6.2 UET 延迟 | 稳态 PDC / 首包（data-before-handshake）/ 0 负载三态；ROD vs RUD 隔离重排延迟 |
| | 6.3 RUD 包喷洒效能 | 5 配置（UET RUD+Spray / UET ROD+Spray / RC+Spray / RC+ECMP / RUD+DLB）；ECMP 路径 4/8/16/32；报 MMR/JFI/OOO/retx/有效 goodput |
| | 6.4 UET 拥塞控制 | N:1 incast（2-64）vs DCQCN；双端 CC（sender+receiver）；**关键指标：无 PFC 下零应用可见丢包** |
| | 6.5 链路/网络层增强 | LLR 重试延迟（注入比特错误，预期 <1µs/跳）；Packet Trimming 有效性（2:1 过订阅）；CBFC vs PFC（N=32 incast，HOL 阻塞时长） |
| | 6.6 UET collective | §9 套件跑 UET RUD+Spray vs RoCEv2；记录 TSS group-key 加密开关 |
| | 6.7 PDC 扩展 | PDC 建立速率（M=100/1K/10K/100K）；data-before-handshake 首字节；最大并发 PDC（降到单 PDC 90% 为止） |
| **TC3 拥塞管理** | 7.1 ECN 标记精度 | 阈值 T（低 ~100KB/中 ~1MB/高 ~5MB）：低于 T 不标、超上限 100% 标、WRED 斜坡合理；报标记概率 vs 队列深度曲线 |
| | 7.2 PFC incast 行为 | N:1（2-64）100% 线速；报 PAUSE 帧率/时长/风暴 onset/吞吐；表征 headroom 与 watchdog |
| | 7.3 DCQCN 收敛 | T0 注入 2:1 过订阅；测 2M 流达 10% 公平份额内时间；M=4/16/64/256；参数敏感性 |
| | 7.4 PFC 风暴/死锁韧性 | 循环依赖流量；300s；报 watchdog 或 VOQ 免疫机制 |
| **TC4 负载均衡** | 8.1 ECMP 熵与极化 | 5-tuple + 含 BTH QP 字段哈希对比；Q=1/4/8/16/32；leaf 数 8-64；报 MMR/JFI/链路利用 |
| | 8.2 Flowlet DLB | 厂商 DLB（记录算法类型）；Q=4；变 flowlet gap timer |
| | 8.3 包喷洒 | MMR≈1.0/JFI≈1.0 期望；OOO 率与 retx 影响；fabric 内重排缓冲（若有）记录 |
| | 8.4 JFI 度量 | JFI = (ΣTx_i)² / (N × ΣTx_i²)；范围 1/N-1.0 |
| **TC5 Collective 通信** | 9.1 AllReduce | 消息 1MB-4GB × N=8-1024 × LB 策略；每 (S,N) ≥100 迭代；BusBW 报 avg/P50/P95/P99 + ECN/PFC/链路利用 |
| | 9.2 AllToAll | 同参数集；**最坏 fabric 压力模式（最大熵）**；JCT 相对 ECMP 基线劣化 = 拥塞敏感度首要指标 |
| | 9.3 AllGather | 同参数集；仅 gather 无 reduce → 峰值负载低于 AllReduce；隔离 gather 路径贡献 |
| | 9.4 BusBW 汇总 | ECMP/DLB/Spray 三策略对比模板 |
| **TC6 JCT** | 10.1 合成 JCT | C=10/50/100/500ms × S=256MB/1GB/4GB × N=64-1024 × 1000 迭代；**JCT Ratio = Measured/Roofline**，Roofline_seq = Iterations×(C + 8×S×algo_factor/B_acc)；重叠执行加报 Overlap_Fraction |
| | 10.2 MLPerf 对齐 JCT | MLPerf Training closed division；须标注版本与 workload 名；同时采全量 §4 KPI |
| | 10.3 多租户干扰 | 2+ 训练 job 重叠 spine 链路（0/25/50/75%）；**JCT Interference Factor = Contention_JCT / Baseline_JCT** |
| **TC7 规模与收敛** | 11.1 Fabric 规模极限 | N=64 递增至拓扑上限跑 AllReduce 1GB；每级报 JCT Ratio/BusBW/ECN/PFC/CPU/内存；清邻接后测 BGP 收敛 |
| | 11.2 链路故障收敛 | 满载 AllReduce（N=128, 1GB）下 admin down spine 上行；报丢包时长/丢包数/故障迭代 JCT 开销/LB 重分发时间 |

## 6. 推理测试方案（Inference Methodology -04）

### 6.1 参考拓扑（3+1 种，Topology D 为推理新增）

- **A（2 层 Clos）**：≤2,048 accel；prefill/decode 分置不同 leaf 组隔离 KV 传输与响应流量；EP dispatch 组内限制在单/少 leaf 降低 spine 跳延迟
- **B（3 层 Clos）**：>2,048 accel 或多模型分 pod；跨 pod KV 传输过 superspine → superspine 带宽/延迟直接决定 KV 传输性能
- **D（PD 分离）**：prefill 池（高算力，TP=8, DP=N/8）+ decode 池（高内存带宽，TP=8, DP=M/8）+ KV 传输网络段（one-sided RDMA PUT/PUT-with-signal）+ KV 感知请求路由器

### 6.2 五级 DUT 定义（推理侧核心创新）

| DUT ID | 对象 | 测量内容 |
|:--|:--|:--|
| **DUT-S** | 单交换机 | 每跳延迟、缓冲吸收、ECN 标记精度 |
| **DUT-F** | 完整 fabric（prefill NIC 出口→decode NIC 入口） | fabric 级 KV 传输延迟/吞吐/拥塞行为 |
| **DUT-N** | NIC 传输栈 | RDMA verb 完成延迟、单边 PUT 带宽、QP 扩展 |
| **DUT-PD** | PD 全路径（GPU 内存→NIC→fabric→NIC→GPU 内存） | 端到端 KV 传输含 PCIe/CXL 段 |
| **SUT-E** | 完整 serving 系统（含软件栈） | TTFT/ITL/TPS 作为 fabric 性能函数 |

### 6.3 工作负载仿真器要求

- **硬件 TG**：RoCEv2/UET 双传输；单边 PUT/PUT-with-signal/双边 SEND-RECV；消息 4KB（最小 KV page）-1GB（大 KV block）；QP 1-256/端口对
- **软件 WE**（真实加速器）：prompt 长度分布（uniform/Zipf/trace-replay）；到达率（Poisson/bursty/trace-replay）；真实 RDMA KV 传输；真实 MoE AllToAll；**per-request TTFT/ITL 时间戳精度 ≤1ms**；完整软件配置（框架/RDMA 库/驱动版本）必须报告

### 6.4 推理 8 大测试类别总览（30 项测试）

| 类别 | 测试项 | 核心规格 |
|:--|:--|:--|
| **TC1 KV 缓存传输** | 5.1 P2P 吞吐 | 消息 64KB-1GB（8 档） × QP 1-128 × ≥60s；≥20 次取平均 |
| | 5.2 传输延迟 | 0 负载 vs 背景 25/50/75/90%；≥20 次 × ≥120s；报 P50/P95/P99/P99.9 + **P99-P50 尾延迟展宽** |
| | 5.3 并发扩展 | 并发对 N=1-128 × 16MB 消息；报聚合吞吐/每对 P99/JFI/链路峰值 |
| | 5.4 多级存储传输 | 仅 fabric 穿越层对：GPU→远端 GPU / GPU→远端 CPU DRAM（卸载）/ 远端 DRAM→GPU（回载）/ GPU→远端 NVMe；零拷贝（GPU-direct）优先 |
| **TC2 PD 分离** | 6.1 端到端 TTFT | 指定 xPyD（如 3P9D）；prompt 128-16K tokens；**TTFT 分解 T_prefill + T_transfer + T_decode_init**；报 T_transfer/TTFT（fabric 份额） |
| | 6.2 xPyD 优化 | 固定 N=12，迭代 1P11D…11P1D；Zipf(α=1.0) 128-8192；报 TTFT P99/ITL P99/TPS/Goodput；**Pareto 前沿**（参考目标：TTFT P99<500ms、ITL P99<50ms，非规范） |
| | 6.3 异构并行 | P:TP8/D:TP8（基线）→ P:TP8/D:TP4+DPA2 → P:TP4+DP2/D:TP2+DPA4；报并发 RDMA 流/聚合带宽/TTFT/ITL |
| | 6.4 预填充队列深度 | 过订阅 1.0×-2.0×（0.25 步进）；报突发尺寸/时长/间隔/峰值带宽需求 + ECN/PFC |
| **TC3 MoE 专家并行** | 7.1 AllToAll 吞吐 | **规范矩阵 M1-M4**（E/k/H_model/T_dispatch：8/2/4096/21.8KB、64/4/7168/76.5KB、256/2/7168/38.2KB、256/8/7168/153KB，B=128 BF16 N=96）；EP 组 8-96 × batch 32-256；T_egress = T_dispatch×(N-1) 定义供给负载；报 GPU 等待空闲时间 |
| | 7.2 路由与调度模式 | Normal vs Low-Latency Dispatch + 至少一种路由模式（Standard Top-k / Expert Choice / Top-k+Drop / Aux Loss Top-k）；报文尺寸固定 |
| | 7.3 宽 EP 扩展 | EP 8（纯节点内，仅放置参考点）→ 16/32/48/64/96 跨 2-12 节点；报扩展效率 = EP16 延迟/EPN 延迟；解释随 S_fabric 变化 |
| | 7.4 EP×KV 争用 | KV 传输 50%/75% 容量 + 周期 EP dispatch；报双方 P99 争用惩罚比（contended/isolated） |
| **TC4 拥塞管理** | 8.1 ECN incast | M=2/4/8/16/32 prefill 同时向 1 decode 传 16MB；ECN 阈值 100KB-5MB；DUT-S |
| | 8.2 PFC 突发 | N_burst=4/8/16/32 × 16MB，到达窗 100µs/1ms/10ms；PFC 阈值 10KB-1MB；报 HOL 阻塞 |
| | 8.3 混合流量收敛 | KV 80% 容量 + 引入 EP dispatch；收敛到稳态 5% 内时间；双向对调 |
| | 8.4 PFC 风暴韧性 | 环形缓冲依赖 + KV 流量注入；≥300s；报风暴/死锁是/否、PAUSE 传播深度、零吞吐时长、恢复时间 |
| **TC5 请求路由与 LB** | 9.1 KV 感知路由 | 10/50/100/200 req/s vs round-robin；报 decode 内存利用 CV、TTFT P99、驱逐率、Goodput |
| | 9.2 前缀感知缓存 | 共享前缀 P=25/50/75/90% × L=256-2048；报命中率/fabric 带宽节省/TTFT 缩减/TPS 提升 |
| | 9.3 ECMP/DLB 推理流量 | 仅 KV（>16MB 大流）/仅 EP（<1MB 小流）/混合；报 JFI/最大最小链路利用 |
| | 9.4 Decode 利用 JFI | N_D=8/16/32/64；报 KV 接收率/GPU 利用/TPS 三指标 JFI + max/min |
| **TC6 延迟** | 10.1 TTFT 按提示长度 | 单请求 0 负载；prompt 128-16K；**参考配置矩阵 CFG-A~D**（S_KV@4K/32K/128K：A 0.54/4.3/17.2GB、B 1.3/10.7/43GB、C 12.9/103/412GB、D INT8 0.67/5.4/21.5GB）；≥100 次/长度 |
| | 10.2 ITL 与尾延迟 | 2048 输出 token 请求；0/50%/90%+EP 三负载；**≥10,000 ITL 样本/条件**；报 ITL>100ms stall 事件数 |
| | 10.3 多租户 E2E | 2+ 模型实例共享 fabric；报干扰惩罚 = (多租户−单租户)/单租户×100% |
| | 10.4 拥塞敏感度 | 背景 0-95%（5% 步进）；找延迟显著劣化拐点；报 50/75/90% 负载劣化因子 |
| **TC7 吞吐** | 11.1 聚合 TPS | 到达率从 1 req/s 递增至 TTFT P99>500ms 或 ITL P99>50ms（SLO 对）；**报 SLO 边界处 fabric 利用率**（关键效率指标） |
| | 11.2 Batch 与 Continuous Batching | batch 1-128；开/关 continuous batching；报并发 KV 传输数/聚合带宽/TPS/TTFT P99 |
| | 11.3 抢占驱逐 Goodput | 过订阅 110/125/150/200%；报驱逐率/抢占率/浪费带宽/Goodput/TPS 比 |
| **TC8 规模与自动扩展** | 12.1 推理规模极限 | 2 节点 16 GPU → 1024 节点 8192 GPU（2 幂步进）；报 KV 传输/EP dispatch/控制面收敛/路由表/TTFT/TPS；10% 劣化点仅为参考（非 pass/fail） |
| | 12.2 动态扩展响应 | 模拟 autoscaler 加/减 4 decode 节点；报 fabric 收敛/首次 KV 传输/稳态达成的三段时间 + 丢包与延迟尖峰 |
| | 12.3 链路故障对 serving | 80% SLO 吞吐下故障：KV 流量 leaf-spine 链路 / spine-spine / decode leaf 链路三类；报中断与恢复 |

## 7. 测试用例全集速查（MECE 汇总）

| 维度 | 训练（27 项） | 推理（30 项） |
|:--|:--|:--|
| 传输层 | 5.1-5.3, 6.1-6.7（10 项：RDMA 基线 + UET 全谱） | 5.1-5.4（4 项：KV 传输 + 多级存储） |
| 拥塞/公平 | 7.1-7.4, 8.1-8.4（8 项） | 8.1-8.4, 9.3-9.4（6 项） |
| 应用模式 | 9.1-9.4（4 项 collective） | 6.1-6.4, 7.1-7.4（8 项：PD + MoE） |
| 端到端/用户可见 | 10.1-10.3（3 项 JCT） | 9.1-9.2, 10.1-10.4, 11.1-11.3（9 项：路由/延迟/吞吐） |
| 规模/韧性 | 11.1-11.2（2 项） | 12.1-12.3（3 项） |

**共性与差异**：训练侧"传输协议对比"（TC2）与"collective 应用模式"（TC5）是双主线；推理侧以 **KV 传输（TC1）+ PD 分离（TC2）+ MoE dispatch（TC3）** 三个 AI 推理专属工作负载为轴，拥塞管理退居支撑位（TC4）——准确映射了推理网络"事件驱动突发 + 延迟敏感"与训练网络"周期同步 + 吞吐敏感"的本质差异。

## 8. 参考量化基准（附录 B，非规范）

| 域 | KPI | 参考值 | 性质 |
|:--|:--|:--|:--|
| 训练 | JCT Ratio | ≤1.05（≤1.15 可接受） | 非 pass/fail |
| 训练 | BusBW | ≥90% NIC 线速（intra-pod） | 非 pass/fail |
| 训练 | 聚合吞吐 | ≥95% 二分带宽 | 非 pass/fail |
| 训练 | 丢包 | 0 ppm 线上（RoCEv2）/ 0 ppm 应用可见（UET） | 非 pass/fail |
| 推理 | TTFT | <500 ms P99 | 非 pass/fail |
| 推理 | ITL | <50 ms P99 | 非 pass/fail |
| 推理 | TTFT_fabric | <20% TTFT P99 预算 | 非 pass/fail |
| 推理 | ITL_fabric | <5 ms P99 | 非 pass/fail |

> ⚠️ **BMWG 章程红线**：所有参考值明确 MUST NOT 用于供应商评估的 pass/fail 判定。落地必须由运营者按拓扑/加速器/CCL/需求自定阈值。

## 9. 演进路线与标准化格局

### 9.1 BMWG 30 年谱系中的位置

```
1991 RFC1242 terminology -> 1996 RFC2544 methodology (router benchmark basis)
-> 2000 RFC2889 LAN switching -> 2017 RFC8238/8239 DC benchmarking
-> 2021 RFC9004 back-to-back update -> 2023 RFC9411 security devices
-> 2024-2026 AI Fabric trilogy (individual drafts -00 -> -04, updated 08-12)
-> future: WG adoption -> RFC path
```

### 9.2 关联草案生态（同周期信号）

| 草案 | 主题 | 状态 |
|:--|:--|:--|
| draft-gaikwad-llm-benchmarking-{methodology,profiles,terminology}-01 | LLM serving 三件套（08-09） | 个人草案 |
| draft-contreras-bmwg-ai-agent-benchmarking-00 | 网络运维 AI agent 基准（07-06） | 个人草案 |
| draft-han-bmwg-agent-security-benchmark-00 | AI agent 安全评估（07-05） | 个人草案 |
| draft-calabria-bmwg-ai-fabric-*-04 | AI Fabric 三件套（08-12） | 个人草案 |

**信号解读**：BMWG 正从"网络设备基准"全面转向"AI 时代的度量基础设施"——fabric（本套件）+ serving（gaikwad）+ agent（contreras/han）三层铺开，且全部引用 UEC 1.0 与 MLPerf 作为外部锚点，说明标准化进程已进入实质推进阶段。

## 10. 落地意义：交换机横评/选型视角

1. **横评口径就绪**：想比较两家 51.2T/800G 交换机在 AI 场景的真实表现，现在有了统一框架——JCT Ratio（应用价值）+ BusBW 效率（协议有效性）+ MMR/JFI（负载均衡质量）+ ECN/PFC 行为（拥塞管理），7 参数可比较集保证"同工作负载、同拓扑类"。
2. **防规格书粉饰**："51.2Tbps 容量"无法再当性能证明；黑盒 + 禁容量归一化 + S_fabric 报告三重约束，堵死了"用容量数字包装低效实现"的路径。
3. **传输中立**：RoCEv2 与 UET 同框架对比（TC2/6.x），不锁定单传输——对 UEC 与 RoCE 并存期的选型决策直接可用。
4. **推理网络首次被认真度量**：KV 传输延迟/TTFT 分解/MoE dispatch 延迟成为一等公民，PD 分离架构的"网络是第二个瓶颈"论断有了验证工具。
5. **国产化落地建议**：① 用 7 参数可比较集 + JCT Ratio 作为国产交换机与进口对标的核心口径；② 测试环境按拓扑 A（2 层 Clos）起步、C（Rail）进阶，先跑 TC1/TC3/TC4/TC5（RDMA/拥塞/LB/collective）四类高价值测试；③ 自建 SLO 阈值（参考附录 B 起步：JCT Ratio ≤1.15、BusBW ≥90% 线速）；④ 关注 UET 测试所需的 UEC 1.0 NIC 就绪度。

## 11. 局限与批判（诚实边界）

1. **标准化阶段**：仍为个人草案（I-D Exists），未进 WG 采纳、非 RFC；-04 是"实质推进"但**尚未定稿**。版本间差异未逐版核验（本分析基于 -04 现状）。
2. **边界外领域**：**NVLink/UALink 等 scale-up 加速器互连明确出界**（DUT 边界在以太网 NIC）——本套件测不了超节点域内互联；超节点 scale-up 度量需另寻 UALink/UEC 配套框架（见超节点系列文档交叉链接）。
3. **无 pass/fail 是双刃剑**：规避了 BMWG 章程限制，但也意味着"标准化了口径、没标准化判定"，横向对比仍需买方自建阈值——这正是附录 B 标注非规范的原因。
4. **黑盒不归因**：方法论自认"不把观测差异归因到单一组件"——若某 fabric JCT Ratio 差，需结合 DUT 特征报告（附录 C）+ Secondary KPI 自行根因。
5. **UET 测试依赖外部成熟度**：TC2 全套依赖 UEC 1.0 规范与合规 NIC 就绪；若 UEC 生态未铺开，测试落地受限。
6. **规模上限**：训练拓扑 B 标称 32K+ accel（800GbE 现役 ASIC），超大规模（万卡+）的极端规模行为仍靠 TC7/12 渐进测试外推。
7. **"Profiles" 名称歧义**（见 §2.2 澄清）：同日更新的三件套实为 Terminology + 双 Methodology；"Profiles" 精确对应另一系列草案，引用时须防混淆。
8. **参考配置矩阵的模型假设**：CFG-C（L=96, H_kv=64 MHA）S_KV 达 412GB@128K——接近单卡 HBM 上限，实测时需注意模型参数与显存约束的匹配性。

## 12. 参考资料路径

### 一手来源（IETF Datatracker，2026-08-14 核验）
- `draft-calabria-bmwg-ai-fabric-terminology-04`：https://datatracker.ietf.org/doc/draft-calabria-bmwg-ai-fabric-terminology/ （42 页，08-12 更新）
- `draft-calabria-bmwg-ai-fabric-training-bench-04`：https://datatracker.ietf.org/doc/draft-calabria-bmwg-ai-fabric-training-bench/ （50 页，08-12 更新）
- `draft-calabria-bmwg-ai-fabric-inference-bench-04`：https://datatracker.ietf.org/doc/draft-calabria-bmwg-ai-fabric-inference-bench/ （49 页，08-12 更新）
- 文本版：https://www.ietf.org/archive/id/draft-calabria-bmwg-ai-fabric-{terminology,training-bench,inference-bench}-04.txt
- BMWG 工作组页：https://datatracker.ietf.org/wg/bmwg/documents/
- 关联草案：draft-gaikwad-llm-benchmarking-*（08-09）；draft-contreras-bmwg-ai-agent-benchmarking-00（07-06）；draft-han-bmwg-agent-security-benchmark-00（07-05）
- 草案引用外部标准：RFC 2544/2889/8238/8239/9004/9411、UEC 1.0 Spec、MLPerf Training、Orca/PagedAttention/DeepEP/Expert-Choice 论文

### 内部知识库交叉链接
- **超节点/供电**：[2026-08-14 1MW Rack Debate 深度分析](../02_rd/02_project/01_superpod/2026-08-14-1mw-rack-debate-power-architecture-deep-analysis.md)（机架功率/互联路线）
- **AMD 机架竞争**：[2026-08-14 MI455X+Helios vs NVIDIA 全景对比](../02_rd/02_project/01_superpod/2026-08-14-amd-mi455x-helios-vs-nvidia-full-comparison-deep-analysis.md)（UAL 3.6TB/s scale-up 与以太网 scale-out 的关系）
- **fabric 原生通信**：[2026-08-11 StrataLC Fabric-Native Communication 深度分析](../../03_AI/llm-techniques-principles/2026-08-11-stratalc-fabric-native-communication-deep-analysis.md)（fabric 承载集合通信的另一路线）
- **NCCL 假存活案**：[2026-08-10 Aries Agentic Serving 可观测性](../../03_AI/agent-engineering/2026-08-10-aries-agentic-serving-observability-deep-analysis.md)（死锁 GPU 100% util 的 fabric 假象——本方法论 FHI 连续监测的设计动机）
- **KV 缓存体系**：knowledge/03_AI/llm-techniques-principles/（KV 四层命运模型——推理 TC1 多级存储传输测试的理论底座）
- **LLM 系统软件**：[2026-08-10 LLM System Software Maturity](../../03_AI/llm-techniques-principles/2026-08-10-llm-system-software-maturity-tensorcast-b300-plora-vibe.md)

### 本地素材
- `tmp/bmwg-ai-fabric/{terminology,training-bench,inference-bench}-04.txt`（三份草案全文，2026-08-14 下载）

---

## Changelog

| 日期 | 变更 |
|:--|:--|
| 2026-08-14 | 初版：基于三件套 -04 全文精读（2026-08-12 更新），含训练 27 项 + 推理 30 项测试用例规格化梳理、四铁律设计哲学、7 参数可比较集、KPI 三层框架、附录 B 参考值、落地建议与批判边界 |
