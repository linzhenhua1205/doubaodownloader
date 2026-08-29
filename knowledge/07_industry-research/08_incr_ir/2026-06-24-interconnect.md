# 🔗 互联与光通信技术动态跟踪 — 2026-06-24

> **搜索范围**: arXiv(cs.NI, cs.AR) + DIGITIMES Asia + 光纤在线(c-fol.net) + LightCounting
> **本期焦点**: **Opus: 光电路交换取代电交换，Rail网络23×功耗降低 · Spectra: 并行OCS调度算法1.4-2.4×提升 · 3D CPO赋能MoE训练2.7×加速 · Ghost in DC: 3M GPU每48秒一次链路抖动 · 6寸InP晶圆供给瓶颈 · 中天/烽火中国光通信新方案**
> **写入时间**: 2026-06-24 10:30

---

## ① OCS光电路交换：从学术验证走向产业落地

### 🟢 Opus: 用光电路交换替代电交换，Rail网络功耗降23× (Hot Interconnects 2026)

| 动态 | 详情 | 来源 |
|:-----|:------|:------|
| **Photonic Rails in ML Datacenters with Opus** | UC Berkeley & Microsoft Research 联合提出**用光电路交换机(OCS)替代高基数电交换机**实现ML训练Rail网络。核心思想：保留Rail通信语义，但利用**并行度驱动的Rail重配置**——不同并行维度（DP/TP/PP/EP）的通信相位**非重叠**，可在单个训练iteration内对不同相位时光复用同一组物理端口。控制面Opus在并行度相位边界编排电路切换 | arXiv:2602.12521, cs.NI, Feb 2026 |
| **量化结果** | 在物理OCS测试床、Perlmutter超算及最多**2,048 GPU**的仿真上验证：网络功耗降低**23×以上**，成本节省**4×**，训练开销<**6%**（生产级OCS重配延迟下） | 同上 |
| **意义** | 这是首个在**生产级规模**（2K+ GPU）上验证OCS替代电交换可行性的系统级工作。Rail拓扑（当前NVIDIA DGX等广泛采用）被证明可以"保留语义、换掉物理"——光交换在功耗和成本上碾压电交换，重配延迟不再是障碍 | 同上 |

> **判断**: Opus 是继 Google TPUv4 OCS 后最重要的数据中心光交换系统工作。TPUv4 证明了 OCS 在 Clos 拓扑中的可行；Opus 则证明了在**更主流的 Rail 拓扑**中 OCS 可更具优势。建议持续跟踪该团队后续工作。

### 🟢 Spectra: 并行OCS调度算法——GPT训练makespan降低1.4× (2026年3月)

| 动态 | 详情 | 来源 |
|:-----|:------|:------|
| **Scheduling Parallel Optical Circuit Switches for AI Training** | 面向AI训练场景的并行OCS调度算法Spectra，解决**多个并行OCS间调度时变流量矩阵**的最小化makespan问题（含非可忽略的重配延迟δ）。三步法：①将流量矩阵D分解为最小加权排列集合；②负载感知跨并行交换分配；③通过受控排列分裂均衡负载 | arXiv:2603.07373, cs.NI, Mar 2026 |
| **量化结果** | 在GPT模型上makespan降低**1.4×**，在Qwen MoE专家路由上降低**1.9×**，在标准benchmark上降低**2.4×**，持续趋近理论下界 | 同上 |
| **意义** | OCS面临的核心挑战之一——调度多个并行交换机的组合优化问题——被首次形式化并提出逼近最优的算法。对OCS实际部署时的控制面设计有直接指导意义 | 同上 |

---

## ② 3D CPO：为万亿参数MoE训练打开Scale-Up新维度

### 🟢 3D集成光学的Passage架构：Scale-Up能力提升8×，训练加速2.7× (Hot Interconnects 2025)

| 动态 | 详情 | 来源 |
|:-----|:------|:------|
| **Accelerating Frontier MoE Training with 3D Integrated Optics** | 随被动电互联距离极限（~1米）限制Scale-Up域于一机架内，3D堆叠光学+逻辑（3D CPO，代号Passage）提供变革性方案：连接**数百个GPU封装（数千GPU）**跨多机架。专注于训练万亿参数以上MoE模型场景 | arXiv:2510.15893, cs.AR, Hot Interconnects 2025 |
| **量化结果** | 3D CPO带来的带宽和基数提升使**Scale-Up能力增加8×**，为多维并行提供新机会，**训练时间缩短2.7×** | 同上 |
| **意义** | 这是**从"铜到光"在Scale-Up域的量化论证**。铜缆基的NVLink域（~1m, ~900GB/s）受限于机架内；3D CPO将Scale-Up扩展至跨多机架，从根本上改变训练并行策略 | 同上 |

---

## ③ 数据中心网络可靠性：链路抖动的幽灵

### 🟢 Ghost in the Datacenter: 3M GPU规模下每48秒一次链路抖动 (2026年3月)

| 动态 | 详情 | 来源 |
|:-----|:------|:------|
| **The Ghost in the Datacenter** | Paul Borrill 系统分析了数据中心网络"幽灵"问题——链路断开或抖动会破坏拓扑图（拓扑知识失败），导致"存在但不可达"的幽灵节点。问题跨越全部层：**chiplet-to-chiplet (PCIe, UCIe)、GPU-to-GPU (NVLink, NVSwitch)、node-to-node (Ethernet)、cluster-to-cluster (IP, BGP)** | arXiv:2603.03736, cs.DC |
| **量化证据** | Meta LLaMA 3训练54天内419次中断；字节跳动3个月内38,236次显式和5,948次隐式失败；Google TPUv4 OCS；阿里NIC-ToR零点零几%月故障率。**2025年集群规模（~3M GPU, >10M光链路）下，每48秒发生一次链路抖动** | 同上 |
| **核心论据** | 所有现有协议继承Shannon的**仅前向时间(FITO)**信道模型，使用**超时重试(TAR)**故障检测。TAR无法区分"慢"和"死"——这正是FLP不可能定理在不完全异步系统中的不可解。Phi Accrual/SWIM/BFD/OSPF快速收敛/SmartNIC卸载/无损以太网(RoCE/PFC)/K8s Pod驱逐**全部基于超时**，仍会产生幽灵 | 同上 |
| **方案** | 提出**Open Atomic Ethernet**通过可靠链路故障检测器+完美信息反馈+三角故障切换+原子令牌传输，使拓扑知识变为**事务性**，消除幽灵 | 同上 |

> **判断**: 这篇论文将数据中心网络可靠性问题从"运维问题"升级为**信息论层面的基本限制**（FITO→TAR→FLP）。对互联设计的核心启示：任何依赖超时的故障检测机制都无法根除幽灵，需要链路层原子性保证。对OCS部署尤其关键——电路交换的物理特性要求更高效的重配和故障检测。

---

## ④ 跨数据中心光互联：GeoPipe实现78.91%计算气泡降低

### 🟢 华为GeoPipe：基于无损RDMA光传输的跨DC LLM训练 (ACP 2025)

| 动态 | 详情 | 来源 |
|:-----|:------|:------|
| **GeoPipe: 跨数据中心光传输网(DC-OTN)的LLM训练框架** | 首个高性能跨数据中心LLM训练框架实证。利用华为Ascend全栈环境上的增强流水线并行，实现跨DC通信与计算的重叠，在受限跨DC带宽和HBM约束下**将计算气泡比例降低78.91%** | arXiv:2510.12064, cs.NI, ACP 2025 |
| **技术基础** | 基于**无损RDMA启用的Datacenter Optical Transport Network (DC-OTN)**：将传统OTN扩展到数据中心间场景，增加RDMA支持和无损传输保障 | 同上 |
| **意义** | 随着LLM参数跨越万亿级，单DC训练逐渐不够用。GeoPipe是与上一篇3D CPO互补的路线——**Cross-DC光传输**，两者共同构成完整的光互联训练图景 | 同上 |

---

## ⑤ 光模块/DSP技术：更低功耗的相干DCI方案

### 🟢 联合脉冲成形+色散补偿算法，DSP复杂度降低46% (2026年5月)

| 动态 | 详情 | 来源 |
|:-----|:------|:------|
| **Hardware-Efficient JFS-CD for Coherent DCI** | 将色散补偿前移到发射端，与成形滤波联合处理，利用DFT和滤波谱特征集成处理。针对预补偿导致的高PAPR问题，提出低复杂度方框限幅算法(SBC)。**实数乘法复杂度降低~46%**，Q-factor提升~0.3 dB | arXiv:2605.25818, cs.IT/cs.NI, May 2026 |
| **意义** | 下一代低功耗高性DCI的发射端DSP方案。对CPO/LPO模块的DSP功耗限制（通常<5W/通道）尤为关键——46%的复杂度降低直接转化为模块功耗和散热压力下降 | 同上 |

---

## ⑥ 光通信产业链：6寸InP晶圆供给瓶颈与国产化突破

### 🟢 AI数据中心光互联竞赛加剧，6寸InP晶圆面临供给墙

| 动态 | 详情 | 来源 |
|:-----|:------|:------|
| **DIGITIMES InP趋势追踪：光互联竞赛加剧，InP供给墙逼近** | DIGITIMES 将 InP 列为当前AI产业追踪的关键词之一。AI数据中心的光互联需求（CPO/LPO模块、硅光集成中的InP激光器）使**6寸InP晶圆供给成为瓶颈**。EML（电吸收调制激光器）和硅光外延都依赖磷化铟基底 | DIGITIMES Asia, 6/23-6/24 trending |
| **硅光代工产能全面锁定** | 此前DIGITIMES已有报道代工厂硅光SiPh产能锁定至2028年（6/1）。新进展是InP衬底本身的供给也开始吃紧——InP激光器是CPO方案中不可或缺的光源组件，6寸衬底产能扩张速度远落后于需求增长 | DIGITIMES |

### 🟢 中国光通信厂商连发重磅方案

| 动态 | 详情 | 来源 |
|:-----|:------|:------|
| **中天科技发布17280芯超大芯数高密度光缆** | 在链博会首发，**刷新行业芯数纪录**，为算力网络提供高密度传输底座 | 光纤在线, 6/23 |
| **烽火通信"Fiber for AI"全光互联方案** | 依托棒-纤-缆-端闭环产业链，覆盖机内/柜内/柜间/楼间/DC间全光互联，主打Fit MPO产品线 | 光纤在线, 6/23 |
| **长飞专稿：AI大模型打通算力超级通道** | 专题论述光纤作为AI基础设施算力通道的核心作用 | 光纤在线 |
| **亿源通专稿：AI规模化的下一个瓶颈——互连能力** | 明确将**互连能力**定义为AI规模化（Scale-out/Scale-up）的下一个核心瓶颈，呼应Marvell CEO COMPUTEX论断 | 光纤在线 |

### 🟢 2025 OCP全球峰会关键Keynotes：Broadcom/Meta/Intel聚焦AI网络

| 动态 | 详情 | 来源 |
|:-----|:------|:------|
| **OCP 2025 Keynote系列** | Broadcom "Networking for AI Scaling"、Meta "Scaling AI Infrastructure to DC Regions"、Intel "Scaling AI at Speed of Openness"、Arm "What AI Wants" 等共同指向**开放光互联基础设施**。这些Keynote资料已归档在光纤在线资料库 | 光纤在线资料库, OCP 2025 |
| **OCS测试技术升温** | CFCF2026将举办**互连新技术—OCS测试主题技术研讨会**（小K云探展｜OFC 2026），反映业界对OCS测试标准化的需求 | 光纤在线, CFCF2026 |

---

## ⑦ 高速互联(PCIe/CXL/UALink)与数据中心网络架构

### 🟢 arXiv新论文：Ghost问题横跨PCIe/UCIe/NVLink/Ethernet所有层级

| 动态 | 详情 | 来源 |
|:-----|:------|:------|
| **链路抖动跨层普遍性** | Ghost论文明确指出，从**chiplet级(PCIe/UCIe)**、GPU级(NVLink/NVSwitch)、节点级(Ethernet/Thunderbolt)到集群级(IP/BGP)，**全部**继承FITO+TAR模型，都面临类似拓扑知识失败问题 | arXiv:2603.03736 |

### 🟢 太赫兹无线互联：AI数据中心的另一种可能

| 动态 | 详情 | 来源 |
|:-----|:------|:------|
| **THz Wireless Data Center (THz-WDC)** | 提出太赫兹无线替代铜缆/光缆的愿景：每链路1Tbps、聚合10Tbps、<50ns延迟、<10pJ/bit效率(@20m)。关键使能技术包括数字孪生编排、低复杂度波束操控、全硅THz收发器。未来芯片模组互连中提供灵活的测试和重配能力 | arXiv:2512.24110, cs.IT |

---

## 📋 本期总结

| 方向 | 关键洞察 | 重要性 |
|:-----|:---------|:------:|
| **OCS光电路交换** | **Opus** 开创性验证了OCS替代电交换Rail网络的可行性（23×功耗↓, 4×成本↓），**Spectra** 解决并行OCS调度组合优化问题 | 🟢🟢🟢 |
| **3D CPO** | Hot Interconnects论文论证3D CPO实现**8× Scale-Up提升**和**2.7×训练加速**，铜→光在Scale-Up域的量化拐点 | 🟢🟢🟢 |
| **网络可靠性** | Ghost论文揭露链路抖动的信息论根本原因——FITO+TAR无法区分"慢"与"死"，3M GPU规模每48秒一次 | 🟢🟢 |
| **跨DC光传输** | 华为GeoPipe实现78.91%计算气泡降低，跨DC光传输进入实证阶段 | 🟢🟢 |
| **InP供给瓶颈** | 6寸InP晶圆由DIGITIMES列为趋势追踪关键词，硅光需求→InP激光器→InP衬底的瓶颈链正在形成 | 🟢🟢 |
| **中国光通信** | 中天17280芯光缆、烽火Fiber for AI、CFCF2026 OCS测试研讨会，国产化持续推进 | 🟢 |
| **DSP低功耗** | JFS-CD降低DSP复杂度46%，直接服务CPO/LPO模块功耗约束 | 🟢 |

---

## 📎 参考文献

1. Ding et al., "Photonic Rails in ML Datacenters with Opus", arXiv:2602.12521, Feb 2026 (cs.NI)
2. Liang et al., "Scheduling Parallel Optical Circuit Switches for AI Training", arXiv:2603.07373, Mar 2026 (cs.NI/cs.AI)
3. Bernadskiy et al., "Accelerating Frontier MoE Training with 3D Integrated Optics", arXiv:2510.15893, Hot Interconnects 2025 (cs.AR)
4. Borrill, "The Ghost in the Datacenter: Link Flapping, Topology Knowledge Failures, and the FITO Category Mistake", arXiv:2603.03736, Mar 2026 (cs.DC)
5. Dai et al., "GeoPipe: Geo-distributed LLM Training with Lossless RDMA-enabled DC-OTN", ACP 2025, arXiv:2510.12064
6. Zhang et al., "Hardware-Efficient JFS-CD for Coherent DCI", arXiv:2605.25818, May 2026 (cs.IT/cs.NI)
7. Han et al., "THz Wireless Data Center", arXiv:2512.24110, Dec 2025 (cs.IT)
8. DIGITIMES Asia, InP trending topic & AI optical interconnect supply chain reports, Jun 23-24 2026
9. 光纤在线 (c-fol.net), 中天科技 17280芯光缆/烽火Fiber for AI/CFCF2026 OCS研讨会等, Jun 23 2026
