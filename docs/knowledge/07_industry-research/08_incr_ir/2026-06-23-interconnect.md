# 🔗 互联与光通信技术动态跟踪 — 2026-06-23

> **搜索范围**: DIGITIMES (5-6月) + arXiv(cs.NI, cs.AR, cs.DC) + LightCounting + 光纤在线 + OCF官网
> **本期焦点**: **CPO/LPO硅光产能锁定至2028 · Marvell:铜墙已移到机架内部 · TSMC COUPE量产与Lightmatter 3D光学引擎 · Astera Labs Scorpio交换芯片成收入主力 · UALink地址转换开销分析**
> **写入时间**: 2026-06-23 09:18

---

## ① 光通信：CPO/LPO/硅光进入爆发前夜

### 🟢 Marvell CEO: "铜墙已移到机架内部，CPO是唯一出路"

| 动态 | 详情 | 来源/日期 |
|:-----|:------|:----------|
| **Marvell CEO Matt Murphy COMPUTEX 2026 演讲** | 明确指出 AI 基础设施的下一个瓶颈**不是计算或内存，而是互联**。铜缆的物理极限正在逼近——「铜墙已经移至机架内部」，**共封装光学（CPO）是突破这一瓶颈的唯一途径**。强调机架内光学互联将从"可选"变为"必要" | DIGITIMES, 6/2 |
| **Marvell 硅光/交换/互联路线图全面扩展** | 在 FY2027 Q1 财报会上详述了在光、铜和硅光互联三大方向的加速进展，信号表明 AI 基础设施正从"以芯片为中心"转向"以互联为中心" | DIGITIMES, 5/28 |

> **判断**: Marvell 作为以太网交换芯片和光通信 DSP 的双料巨头，其 CEO 在 COMPUTEX 标志性演讲中的论断具有风向标意义。CPO 已从"技术探索"进入"产品必要性论证"阶段。

### 🟢 AI基础设施触及铜缆极限，代工厂硅光产能锁定至2028

| 动态 | 详情 | 来源/日期 |
|:-----|:------|:----------|
| **从芯片中心到互联中心** | DIGITIMES 报道指出 GenAI 正在跨越关键算力阈值，推动架构从"以芯片为中心"向"以互联为中心"转型。传统铜缆的物理限制正在触发代工厂硅光产能被全面锁定 | DIGITIMES, 6/1 |
| **Foundries 锁定硅光产能** | 报道确认代工厂的**硅光子（SiPh）产能已全部被锁定至 2028 年**，反映出市场对 CPO/LPO 产品需求的强烈预期 | DIGITIMES, 6/1 |
| **数据中心收发器 >50% 将来自硅光** | 预测到 2026 年，超过 50% 的数据中心收发器销售额将来自硅光子技术 | DIGITIMES, 4/3 |

### 🟢 TSMC COUPE平台进入量产年，Lightmatter联手打造3D光学引擎

| 动态 | 详情 | 来源/日期 |
|:-----|:------|:----------|
| **TSMC COUPE 正式量产** | TSMC 表示其 **COUPE（Compact Universal Photonic Engine）** 硅光平台将在 **2026 年进入量产**。TSMC 董事长称 CoPoS 可在数年内实现规模化扩产 | DIGITIMES, 4/2 & 5/21 |
| **Lightmatter 加入 TSMC COUPE 合作** | AI 光计算独角兽 **Lightmatter** 宣布与 TSMC 在 COUPE 平台上合作开发 **3D 光学引擎**，结合 TSMC 的先进封装能力与 Lightmatter 的光计算技术 | DIGITIMES, 5/26 |
| **三星硅光代工承压** | DIGITIMES 分析指出，TSMC COUPE 的快速推进给 **Samsung Foundry** 的硅光代工雄心带来压力。三星已启动硅光代工试产，但规模化和客户获取面临挑战 | DIGITIMES, 5/21 |

> **判断**: TSMC COUPE 量产是 2026 年 CPO 产业链最重要的里程碑之一。Lightmatter 的加入意味着 3D 光学引擎技术路线获得代工龙头的工艺支点。

### 🟢 BE Epitaxy 1.6T CPO 获 AMD/联发科加持

| 动态 | 详情 | 来源/日期 |
|:-----|:------|:----------|
| **BE Epitaxy 盈利并瞄准 1.6T CPO** | 硅光芯片设计公司 **BE Epitaxy Semiconductor** 于 **2025 年实现盈利**，800G 和 1.6T CPO 需求爆发。公司已获得 **AMD 和 MediaTek（联发科）** 的订单和投资支持 | DIGITIMES, 6/4 |
| **技术路线** | 专注于硅光（SiPh）芯片设计，**1.6T CPO** 为下一代旗舰产品 | DIGITIMES, 6/4 |

### 🟢 1.6T 升级使 InP 成为供应链瓶颈

| 动态 | 详情 | 来源/日期 |
|:-----|:------|:----------|
| **从 800G 到 1.6T 的物理拐点** | LightCounting/DIGITIMES 指出，从 800G 到 1.6T 光模块的升级已不再是简单的代际更替，而是**物理驱动下的拐点**。**InP（磷化铟）** 激光器供应成为关键瓶颈 | DIGITIMES, 5/4 |
| **Lumentum 扩产 InP** | 美国光通信龙头 Lumentum 在北卡罗来纳州大幅扩产 InP，以捕捉 AI 基础设施需求 | DIGITIMES, 4/1 |
| **GlobalFoundries 加码 SiPh/CPO/SiGe** | GlobalFoundries 在 FY2026 Q1 财报中重点展示了 SiPh、CPO 和 SiGe 的进展，视其为向高价值芯片市场跃迁的战略支点 | DIGITIMES, 5/6 |

---

## ② 高速互联：PCle/CXL/UALink 与交换机芯片

### 🟢 Astera Labs Scorpio 交换芯片将成为最大收入来源

| 动态 | 详情 | 来源/日期 |
|:-----|:------|:----------|
| **Scorpio 交换芯片收入快速攀升** | Astera Labs 预计其 **Scorpio 智能交换芯片**将在 **2026 年底前成为公司最大营收贡献者**，超越其传统的重定时器/Retimer 产品线。标志 Astera Labs 从"互联组件"向"互联平台"的转型 | DIGITIMES, 6/11 独家 |
| **云 AI 连接芯片市场格局** | 作为云 AI 连接芯片的新兴主力，Scorpio 的增长反映了 PCIe/CXL 交换在 GPU 集群中的核心地位 | DIGITIMES, 6/11 |

### 🟢 Molex AI 互连双轨策略：铜+光并行

| 动态 | 详情 | 来源/日期 |
|:-----|:------|:----------|
| **Molex 台湾扩产，双轨策略** | Molex 正在执行铜缆与光学 **双轨并行** 的 AI 互连战略。客户存在不同的部署路径偏好，需要同时提供铜和光解决方案。同时扩大在台湾的运营以支撑亚太区域需求 | DIGITIMES, 6/8 |
| **铜缆仍有生命力** | 尽管 CPO 前景被看好，但高速铜缆（DAC/ACC）在机架内和机架间的中短距离场景仍是当前主力部署方案 | DIGITIMES, 6/8 |

### 🟢 arXiv：UALink/NVLink 场景下多GPU扩展的地址转换开销分析

| 动态 | 详情 | 来源/日期 |
|:-----|:------|:----------|
| **论文** | *Analyzing Reverse Address Translation Overheads in Multi-GPU Scale-Up Pods* | arXiv:2604.02473, 4/2 |
| **核心发现** | 分布式 ML 训练依赖多 GPU/多节点间的集合通信，**UALink/NVLink** 等 Scale-up Fabric 支持跨节点直接内存访问，但引入了关键的**反向地址转换（RAT）开销**。论文定量分析了反向地址转换在不同 Scale-up Pod 配置下的性能影响，为 UALink 互联架构设计提供了优化依据 | cs.AR |

### 🟢 arXiv：两类数据中心网络调度与效率研究

| 动态 | 详情 | 来源/日期 |
|:-----|:------|:----------|
| **Switching Efficiency 框架** | *Switching Efficiency: A Novel Framework for Dissecting AI Data Center Network Efficiency* — 提出新的效率分析框架，用于剖析 AI 数据中心网络效率，直接指导大规模 GPU 集群的通信网络设计 | arXiv:2604.14690, 4/16 |
| **光电路交换（OCS）Coflow 调度** | *An O(K)-Approximation Coflow Scheduling in K-Core Optical Circuit Switching Networks* — 在多核光电路交换网络中实现近似最优的 Coflow 调度，为**OCS 在 AI 数据中心网络**的大规模部署提供理论支撑 | arXiv:2604.22146, 4/24 |

---

## ③ 交换机与数据中心网络架构

### 🟢 台系 AI 基础设施供应商 5 月营收普涨

| 动态 | 详情 | 来源/日期 |
|:-----|:------|:----------|
| **台湾 AI 基础设施供应链** | 与 AI 服务器、数据中心网络、光学互联相关的台湾供应商在 **2026 年 5 月** 营收出现全面增长。光模块、交换设备、连接器子板块尤为突出 | DIGITIMES, 6/12 |

### 🟢 LightCounting: AI to Reshape Optical Networking in China

| 动态 | 详情 | 来源/日期 |
|:-----|:------|:----------|
| **2026年6月最新研究笔记** | LightCounting 发布 **"AI to Reshape Optical Networking in China"**，分析 AI 如何重塑中国光网络市场 | LightCounting, 6/2026 |
| **PIC封装最新进展** | 同期发布 **"Advances in PIC Packaging"**，涵盖光子集成电路（PIC）封装技术的突破 | LightCounting, 6/2026 |
| **NPO追求最优平衡** | 2026年5月免费开放笔记：**"NPO is pursuing an optimal balance between CPO and pluggable optics"** — 近封装光学（NPO）正在 CPO 和可插拔光模块之间寻求最优平衡点 | LightCounting, 5/2026（free） |
| **CPO/NPO Conference 2026** | LightCounting 将于 **2026年7月15日** 举办 CPO/NPO 线上研讨会 | LightCounting Events |

### 🟢 光纤在线 CFCF2026：AI算力光通信全产业链集结

| 动态 | 详情 | 来源/日期 |
|:-----|:------|:----------|
| **CFCF2026 大会** | 第 11 届光连接大会（CFCF2026）聚焦 **AI 算力架构与互联方案**，设双日主论坛，汇聚 **200+ 参展商** | 光纤在线, 6/23 |
| **EXFO 展示 1.6T/3.2T 测试方案** | EXFO 将在 CFCF2026 上展示 **1.6T/3.2T 及空芯光纤（Hollow-Core Fiber）测试方案**，测试能力已从 800G 向 1.6T/3.2T 跃进 | 光纤在线, 6/23 |
| **XPO vs CPO 技术权衡** | 技术白皮书《XPO vs CPO：AI 网络中速度、功耗与模块化的权衡》分析了 XPO（近封装光学）与 CPO 在性能、功耗和可维护性上的差异 | 光纤在线, 6/23 |
| **NVIDIA NVL72 连接方案** | 发表了 NVIDIA NVL72 GB200/GB300 系统的 InfiniBand 与 Ethernet 完整连接方案技术文档 | 光纤在线, 6/23 |
| **互连新技术—OCS测试技术研讨会** | 光纤在线组织了 OCS（光电路交换）测试主题技术研讨会，反映业界对 OCS 作为 AI 数据中心核心交换方案的关注升温 | 光纤在线, 6/23 |

---

## ④ 趋势研判

### ✅ CPO 从技术论证进入产业化快车道

- **标志性事件密集**：TSMC COUPE 量产、Marvell CEO 公开宣告、Lightmatter 加入 3D 光学引擎合作、Foundry 硅光产能锁定至 2028 年
- **产业链分工逐渐清晰**：TSMC 做 COUPE 平台（代工），Lightmatter 做 3D 光学引擎（光计算），Marvell/BE Epitaxy 做 SiPh 芯片设计，Lumentum 做 InP 激光器
- **时间线**：2026 年量产启动 → 2027-2028 年规模化 → 预计 2030 年 CPO 成为 AI 数据中心光互连主流

### ✅ "铜光双轨"是未来 2-3 年的现实格局

- **机架内（<2m）**：铜缆（DAC/ACC）仍是当前主力，但铜墙正在从机架间向机架内收缩
- **机架间（2m-500m）**：主动光缆（AOC）和可插拔光模块主导，1.6T 光模块升级使 InP 供应紧张
- **机架内互联下一代**：CPO 将在 2027-2028 年逐步渗透进入机架内部互联
- Molex 的"铜+光双轨"策略和业界共识高度一致

### ✅ UALink 生态正在形成，地址转换成为关键工程问题

- Astera Labs Scorpio 交换芯片成为收入主力 → PCIe/CXL 交换生态成熟
- arXiv 论文揭示 UALink 场景的地址转换开销 → 工程优化方向明确
- 从"互联组件"到"互联平台"的产业演进正在加速

---

### 📎 参考文献

| # | 来源 | 标题 | 日期 |
|:-:|:-----|:-----|:-----|
| 1 | DIGITIMES | Marvell CEO says copper wall is moving inside the rack, and CPO is the only way through | 6/2 |
| 2 | DIGITIMES | AI infrastructure hits copper limits, foundries lock down silicon photonics capacity through 2028 | 6/1 |
| 3 | DIGITIMES | BE Epitaxy Semiconductor targets 1.6T CPO with AMD, MediaTek | 6/4 |
| 4 | DIGITIMES | Lightmatter joins TSMC on COUPE for 3D optical engines | 5/26 |
| 5 | DIGITIMES | TSMC's COUPE push puts Samsung's silicon photonics ambitions under pressure | 5/21 |
| 6 | DIGITIMES | Exclusive: Astera Labs sees switch chips becoming biggest revenue driver by end of 2026 | 6/11 |
| 7 | DIGITIMES | Molex expands in Taiwan as AI interconnect demand splits between copper and optics | 6/8 |
| 8 | DIGITIMES | Marvell expands silicon photonics, switching, and interconnect roadmap | 5/28 |
| 9 | DIGITIMES | AI's 1.6T shift turns InP into optical supply chain bottleneck | 5/4 |
| 10 | DIGITIMES | GlobalFoundries sees optical and SiGe momentum drive strategic leap | 5/6 |
| 11 | DIGITIMES | Taiwan AI infrastructure suppliers see broad sales gains in May | 6/12 |
| 12 | arXiv | Analyzing Reverse Address Translation Overheads in Multi-GPU Scale-Up Pods (2604.02473) | 4/2 |
| 13 | arXiv | Switching Efficiency: A Novel Framework for Dissecting AI Data Center Network Efficiency (2604.14690) | 4/16 |
| 14 | arXiv | An O(K)-Approximation Coflow Scheduling in K-Core OCS Networks (2604.22146) | 4/24 |
| 15 | LightCounting | AI to Reshape Optical Networking in China (June 2026 RN) | 6/2026 |
| 16 | LightCounting | Advances in PIC Packaging (June 2026 RN) | 6/2026 |
| 17 | LightCounting | NPO is pursuing an optimal balance between CPO and pluggable optics | 5/2026 |
| 18 | 光纤在线 | CFCF2026 光连接大会 - AI算力光通信全产业链集结 | 6/23 |
| 19 | 光纤在线 | EXFO 展示 1.6T/3.2T 及空芯光纤测试方案 | 6/23 |
| 20 | DIGITIMES | TSMC says COUPE platform set for production | 4/2 |
