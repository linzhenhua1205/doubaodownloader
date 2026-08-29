# 🧠 内存解聚从容量到计算：PLoRA（NDP 池化）× HMA-Serve（跨厂商）× CoHDI（K8s 官方化）+ KubeCon China（09-07 上海）

> **统一主线**: 内存解聚（memory disaggregation）正在走完**「容量共享 → 近存计算（NDP）→ 编排官方化」**的三阶段演进：①**PLoRA**（arXiv 2608.05483）把 LoRA 适配器留在 CXL/NVLink 池化内存、仅回传规约结果，1000 适配器 decode 延迟比 S-LoRA 低 **6.6×**、且 **32GB/s（CXL 3.1 的 1/4）即饱和**——「链路不再重要，盈余带宽换容量」，为 CXL 对冲 DRAM 涨价提供执行侧依据；②**HMA-Serve**（arXiv 2606.29986）用 GDDR 加速器做 prefill + HBM GPU 做 decode 的**跨厂商异构内存解聚**（goodput-per-dollar **+4.8×**）——解聚从「同厂商」走向「跨厂商」；③**CoHDI** 进 CNCF Sandbox（07-28）——K8s 通过 DRA 动态挂载/卸载 PCIe 设备，**可组合解聚在 K8s 生态官方化**。另有 KubeCon China 2026（9/7-9 上海，**四会联合**：KubeCon+CloudNativeCon+OpenInfra Summit+PyTorch Conference）作为行业落地窗口。
>
> **关键词**: PLoRA · NDP · 池化内存 · CXL 3.1 · multi-LoRA · HMA-Serve · 跨厂商解聚 · MemHA · CoHDI · DRA · K8s 可组合 · KubeCon China
>
> **数据源**: ✅ 一手摘要/官方博客：
> - [PLoRA: An NDP-Enhanced Pooled-Memory System for Cost-Efficient Multi-LoRA Serving](https://arxiv.org/abs/2608.05483)（**提交 2026-08-05**，arXiv 2608.05483）
> - [HBM Is Not All You Need: Efficient Disaggregated LLM Serving across Memory-heterogeneous Accelerators](https://arxiv.org/abs/2606.29986)（**提交 2026-06-29**，arXiv 2606.29986）
> - [Welcome CoHDI to the CNCF](https://www.cncf.io/blog/2026/07/28/welcome-cohdi-to-the-cncf-evolving-kubernetes-into-composable-disaggregated-infrastructures/)（CNCF 官方博客，**2026-07-28**，五作者：Red Hat/FSAS/Fujitsu/IBM Research/NTT）
> - [CNCF 官网 KubeCon China 2026](https://www.cncf.io/)（**9/7-9 上海**，四会联合确认）
>
> **素材分级**: ✅ 一手摘要（PLoRA/HMA-Serve 完整量化）+ ✅ 一手官方博客（CoHDI 全文）+ ✅ 官网事件（KubeCon China）· 🔵 既有知识库锚点（08-10 TensorCast PLoRA 快评 / 存储行业 FMS 复盘 / CXL 对冲 / KV 分层 / HBF）
>
> **日期**: 2026-08-10 | **领域**: 内存解聚 / 近存计算 / LLM 推理 / 云原生

---

## 📑 目录

- [〇、结论概要](#〇结论概要)
- [一、PLoRA：NDP 池化内存——「链路不再重要，盈余带宽换容量」](#一plorandp-池化内存链路不再重要盈余带宽换容量)
  - [1.1 问题：multi-LoRA 服务的工作负载反转](#11-问题multi-lora-服务的工作负载反转)
  - [1.2 设计：read-compute 接口 + 4+2 执行策略 + link 参数化成本模型](#12-设计read-compute-接口--42-执行策略--link-参数化成本模型)
  - [1.3 量化结果](#13-量化结果)
  - [1.4 第一性解读：为什么 32GB/s 就饱和](#14-第一性解读为什么-32gbs-就饱和)
- [二、HMA-Serve：跨厂商异构内存解聚](#二hma-serve跨厂商异构内存解聚)
  - [2.1 MemHA：prefill 用 GDDR、decode 用 HBM](#21-memhaprefill-用-gddrdecode-用-hbm)
  - [2.2 三个机制：逐相量化 + 计算-传输流水 + 延迟反量化](#22-三个机制逐相量化--计算-传输流水--延迟反量化)
  - [2.3 量化结果](#23-量化结果)
- [三、CoHDI：K8s 可组合解聚官方化](#三cohdik8s-可组合解聚官方化)
  - [3.1 项目背景与定位](#31-项目背景与定位)
  - [3.2 三组件架构（DRA 框架内）](#32-三组件架构dra-框架内)
  - [3.3 用例：prefill/decode 分载 + Agentic AI](#33-用例prefilldecode-分载--agentic-ai)
- [四、KubeCon China 2026：四会联合落地窗口](#四kubecon-china-2026四会联合落地窗口)
- [五、统一框架：内存解聚三阶段演进](#五统一框架内存解聚三阶段演进)
- [六、与本地知识库的闭环](#六与本地知识库的闭环)
- [七、批判性审视](#七批判性审视)
- [八、可证伪预测（P1-P6）](#八可证伪预测p1-p6)
- [九、对本系统的启示](#九对本系统的启示)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 〇、结论概要

**一句话：内存解聚正在完成从「容量共享」到「近存计算（NDP）」再到「编排官方化」的三级跳——PLoRA 证明池化内存可以做计算（不止放数据）、HMA-Serve 证明解聚可以跨厂商（不止同栈）、CoHDI 证明 K8s 可以原生编排可组合解聚硬件（不止专用框架）。**

1. **PLoRA（NDP 池化）**：multi-LoRA 服务（1000+ 适配器）把适配器 + KV cache 留在池化内存，GPU 用 load/store 驱动 read-compute 接口，**只回传规约结果**；4 种 LoRA + 2 种 attention 执行策略 + link 参数化成本模型选最优。H100 上 1000 适配器 decode 延迟平均 **-6.6× vs S-LoRA**（<3.4% 面积开销）；**吞吐在 32GB/s 饱和（CXL 3.1 的 1/4）**——「链路本身不再重要：盈余带宽买的是池化容量而不是速度」。
2. **HMA-Serve（跨厂商）**：GDDR 加速器跑 prefill（计算密集）、HBM GPU 跑 decode（内存密集），**跨厂商配对**（打破单厂商软件栈假设）；逐相量化 + 计算-传输流水（隐藏 KV 传输）+ 延迟反量化（传原始量化字节、在 decode GPU 惰性重建）→ goodput **+3.2×**、goodput-per-dollar **+4.8×**（Qwen3 4B-32B × 3 生产 trace，生成质量无损）。
3. **CoHDI（K8s 官方化）**：Red Hat/Fujitsu/NTT/IBM Research 等发起（2025-03，原 InfraDDS），CNCF Sandbox 接受（07-28）；三组件（Composable-DRA-Driver / Dynamic-Device-Scaler / Composable Resource Operator）让 K8s 通过 **DRA 动态挂载/卸载 PCIe 设备（GPU 等）**，无需 OS 重启；直接服务 prefill/decode 分载与 Agentic AI 的阶段性资源需求。
4. **KubeCon China**：9/7-9 上海，**KubeCon + CloudNativeCon + OpenInfra Summit + PyTorch Conference 四会联合**——可组合解聚 + AI 基础设施将是核心议题。

---

## 一、PLoRA：NDP 池化内存——「链路不再重要，盈余带宽换容量」

### 1.1 问题：multi-LoRA 服务的工作负载反转

| 维度 | 内容 |
|:-----|:-----|
| **场景** | 一个基础模型 → 数千个专用变体（每用户/任务/agent 一个适配器），**部署可达 1000+ 适配器** |
| **根本矛盾** | 该工作负载**反转了 GPU 的能力结构**：需要 **TB 级内存** 但只有 **数十 TFLOPS**（GPU 是算力过剩、内存不足） |
| **现状瓶颈** | 所有已发布系统从 CPU DRAM 经 PCIe 分段加载适配器——**每次访问付内核停 + 主机拷贝 + 容量止于 DIMM 插槽** |
| **新硬件机遇** | CXL/NVLink 等 memory-semantic fabric 正收敛于池化内存（加速器用自己的 load/store 寻址）；**NDP（近存计算）可在池化数据旁放计算** |

**第一性解读**：multi-LoRA 是「内存墙」的极端案例——**不是算力不够，是适配器放不下**。传统解法（CPU DRAM → PCIe 搬运）每次访问付「内核停 + 拷贝」双重税；池化内存（CXL/NVLink）让 GPU 直接寻址，NDP 让计算跑到数据旁边——**把「搬运问题」变成「寻址问题」再变成「就地计算问题」**。

### 1.2 设计：read-compute 接口 + 4+2 执行策略 + link 参数化成本模型

| 设计 | 内容 |
|:-----|:-----|
| **架构** | 适配器 + KV cache **留在池中**；GPU 用自己的 load/store 驱动 **read-compute 接口**；**只回传规约结果**（不搬数据） |
| **执行策略** | 4 种 LoRA 策略 + 2 种 attention 策略，按适配器选择 |
| **GPU 内存管理** | 缓存最性能关键的字节在 GPU 内存（分层） |
| **成本模型** | **link 参数化**（按 CXL/NVLink 的带宽/延迟参数选择策略） |
| **兼容性** | **CXL 级到 NVLink 级 fabric 通用**（设计不依赖具体链路） |

### 1.3 量化结果

| 指标 | 数值 | 基线 |
|:-----|:-----|:-----|
| decode 延迟（1000 适配器，H100） | **平均 -6.6×**（所有模型/工作负载最低） | S-LoRA（真实机器） |
| 面积开销 | **<3.4%** | 增加 NDP 单元 |
| 吞吐饱和点 | **32 GB/s**（短上下文） | **CXL 3.1 的 1/4** |
| 扩展性 | per-GPU 需求从 7B → 1.2T 部署（适配器流量随张量并行分片） | 建模 |

### 1.4 第一性解读：为什么 32GB/s 就饱和

**饱和的物理原因**：LoRA 适配器**每个 token 只读一次**（KV cache 每 token 读写多次但也在池内计算）；NDP 把计算放在数据旁 → 链路上只有「规约结果」这种**小体积高频**流量——**流量形态从「搬运适配器权重」变成「搬运规约中间量」**，体积小到 32GB/s 足够。

**「盈余带宽换容量」的含义**：CXL 3.1 提供 128GB/s（单向）级带宽，但 PLoRA 只用 1/4 就饱和——**剩余带宽没有浪费，而是换取「不用搬适配器」的架构自由**：①适配器可以无限多（不受 GPU 内存/DIMM 容量限制）②换模型/换链路（CXL→NVLink）不重设计。**这是「带宽换架构弹性」的典型——容量/弹性是稀缺资源，链路带宽是盈余资源。**

**与 DRAM 涨价的对冲逻辑**（用户点题）：DRAM 涨价 5× → CXL 对冲；PLoRA 给出**执行侧依据**——适配器放池化（CXL 内存/持久内存）成本远低于 HBM/DRAM 常驻，且性能损失可忽略（32GB/s 即饱和）——**「把重量级适配器迁出 GPU 内存」从构想变成有数据的方案。**

---

## 二、HMA-Serve：跨厂商异构内存解聚

### 2.1 MemHA：prefill 用 GDDR、decode 用 HBM

| 观察 | 内容 |
|:-----|:-----|
| **LLM 推理两阶段** | prefill = **计算密集**（HBM 带宽几乎闲置）；decode = **内存密集**（带宽饱和） |
| **矛盾** | 数据中心 GPU 依赖昂贵 HBM，**prefill 时 HBM 带宽几乎完全闲置** |
| **MemHA 方案** | **GDDR 加速器跑 prefill + HBM GPU 跑 decode**——各用其长、整体降本 |
| **极致形态** | **跨厂商**：prefill 最佳芯片与 decode 最佳芯片可能来自不同厂商 |

**跨厂商的两个破绽**（单厂商解聚默认有的）：①KV 格式两端原生兼容 ②共享软件栈——跨厂商两者都没有。

### 2.2 三个机制：逐相量化 + 计算-传输流水 + 延迟反量化

| 机制 | 内容 | 解决的问题 |
|:-----|:-----|:-----------|
| **① 逐相量化（phase-wise quantization）** | prefill 用厂商原生低精度（高吞吐）、decode 保持 BF16 高精度 | 跨厂商精度差异 + 阶段特性 |
| **② 计算-传输流水（compute-transfer pipeline）** | 每层 KV cache 传输与后续层 prefill **重叠** | TTFT（首 token 延迟） |
| **③ 延迟反量化（deferred dequantization）** | 传**原始量化字节**、在 decode GPU **惰性重建** | 网络带宽 + HBM 占用 |

### 2.3 量化结果

| 指标 | 数值 | 对比 |
|:-----|:-----|:-----|
| goodput | **+3.2×** | 最先进 memory-homogeneous 方法 |
| goodput-per-dollar | **+4.8×** | 同上 |
| 生成质量 | **无可测损失** | Qwen3 4B-32B × 3 生产 trace |

**第一性解读**：HMA-Serve 的本质是**把「内存异构」从包袱变成资产**——HBM 贵是因为 decode 内存密集；但 prefill 不需要 HBM 带宽 → 用 GDDR（便宜 5-10×）跑 prefill = **按阶段付费**（pay-per-phase），不是按最贵资源付费。**「跨厂商」是它的激进之处**：KV 格式与软件栈的破绽用逐相量化 + 延迟反量化（格式中立）绕过——**解聚的成熟度标志：厂商边界不再是架构边界。**

---

## 三、CoHDI：K8s 可组合解聚官方化

### 3.1 项目背景与定位

| 维度 | 内容 |
|:-----|:-----|
| **全称** | Composable Hardware in Disaggregated Infrastructure（发音 "Cody"） |
| **启动** | 2025-03（原 InfraDDS），Red Hat / FSAS / Fujitsu / IBM Research / NTT 五方 |
| **CNCF 里程碑** | **Sandbox 接受（2026-07-28）** |
| **定位** | 桥接「传统硬件边界」与「云原生编排」——K8s 节点上的 **host 级 PCIe 设备动态挂载/卸载**（经 DRA） |
| **NTT 背书** | IOWN Data-Centric Infrastructure（DCI）的 feature subset——「K8s 驱动云原生运维 × 多厂商可组合解聚硬件创新」 |

### 3.2 三组件架构（DRA 框架内）

| 组件 | 职责 |
|:-----|:-----|
| **Composable-DRA-Driver** | 与 Dynamic-Device-Scaler 协作；作为 K8s 与 CoHDI manager 的桥；把可用资源以 **ResourceSlices** 暴露给 DRA 框架 |
| **Dynamic-Device-Scaler** | 按 Pod 请求动态**加/减设备（无需 OS 重启）** |
| **Composable Resource Operator** | 经 CoHDI manager 外部 API 动态 **attach/detach 可组合硬件（GPU 等）** 到集群节点 |

**与 SIG 协作**：SIG Node / SIG Autoscaling / SIG Scheduling。

**官方化的意义**：此前可组合解聚是「专用框架/厂商私有」；CoHDI 把它做成 **K8s 原生 DRA 扩展**——解聚资源像普通 K8s 资源一样被调度/伸缩/审计——**「解聚」从硬件特性变成平台能力。**

### 3.3 用例：prefill/decode 分载 + Agentic AI

| 用例 | 资源需求特点 | CoHDI 响应 |
|:-----|:-------------|:-----------|
| **LLM prefill/decode 分载** | prefill 计算密集、decode 内存密集 | 动态分配不同资源（与 HMA-Serve 思路同构，硬件级落地） |
| **Agentic AI** | 各运行阶段资源需求动态变化 | 按阶段动态 attach/detach |
| **能效** | 资源按需而非常驻 | 高能效/可持续运营 |

---

## 四、KubeCon China 2026：四会联合落地窗口

| 维度 | 内容 |
|:-----|:-----|
| **时间/地点** | **2026-09-07 ~ 09-09，上海**（CNCF 官网确认） |
| **四会联合** | **KubeCon + CloudNativeCon + OpenInfra Summit + PyTorch Conference China 2026** |
| **对本地含义** | OpenInfra Summit（OpenStack/基础设施）与 PyTorch Conference（AI 框架）与 KubeCon 同台——**云原生 × AI × 开放基础设施的融合信号**；CoHDI 类可组合解聚、DRA、AI 调度将是核心议题 |

**行业定位**：继 GTC→FMS→ODCC 三大会闭环后，KubeCon China 是**云原生/编排层的中国窗口**——超节点运维、GPU 调度（DRA/HAMi）、可组合解聚（CoHDI）等 AI 基础设施软件栈议题将集中呈现。

---

## 五、统一框架：内存解聚三阶段演进

```
        Memory disaggregation: three-stage evolution
                 |
     +-----------+----------+---------------+
     |           |          |               |
 Stage 1     Stage 2    Stage 3         cross-vendor
capacity     NDP       orchestration    heterogeneous
 sharing     compute    official        (HMA-Serve)
     |           |          |               |
 CXL pool    PLoRA      CoHDI           GDDR prefill
 store data  compute    manage          HBM decode
     |        data       data             +4.8x $/goodput
 KV in pool  adapters   DRA hot         phase-wise
             stay in    attach/detach   quantization
             pool       no OS reboot
             6.6x       ResourceSlices
             32GB/s     energy ops
             saturate
     +------------------------------------------+
     common core: memory no longer "belongs" to one GPU
```

**模式识别**：三篇的**共同内核** = **内存从「附属于加速器的私有资源」变成「平台级共享/可计算/可编排资源」**——PLoRA 让它可计算（NDP）、HMA-Serve 让它跨厂商（异构）、CoHDI 让它可编排（K8s 原生）。**「内存解聚」从论文概念走向三层齐备的系统能力。**

---

## 六、与本地知识库的闭环

| 锚点 | 闭环内容 |
|:-----|:---------|
| **08-10 TensorCast 篇 PLoRA 快评** | 本批是 PLoRA 的**深度展开**（执行策略/成本模型/饱和机理）——从「快评一句话」到「完整深潜」 |
| **存储行业 FMS 复盘：闪存内存化四路竞速（HBF/CXL 池化/…）** | PLoRA 是 **CXL 池化路线的计算侧实证**——池化不只为容量，还承载 NDP |
| **DRAM 涨价 5× → CXL 对冲（MEMORY）** | PLoRA 提供执行侧依据：适配器迁池化后 32GB/s 即饱和——**「性能损失可忽略」让对冲成立** |
| **KV 四层命运（L0 HBM/L1 DRAM/L2 持久/L3 checkpoint）** | PLoRA 的 KV cache 留池 = L2 层的**主动利用**（而非故障备用）——KV 分层从「命运」变成「策略」 |
| **HBF 首个 OCP 规范（512GB/0.4-3.0TB/s）** | PLoRA 的 32GB/s 饱和点**远低于 HBF 带宽下限**——「带宽过剩」的架构含义在内存池场景同样成立 |
| **08-07 FMS：cuFile/SCADA GPU 发起 I/O** | NDP（PLoRA）与 GPU 发起 I/O（cuFile）是「数据不搬、计算去数据旁」的两条路线 |
| **DRA/HAMi（CNCF W31：HAMi Incubating）** | CoHDI 与 HAMi 的竞合（08-07 CNCF 博客「Does Kubernetes DRA Replace HAMi?」）：**DRA 是框架、HAMi 是调度器、CoHDI 是硬件解聚——三层不同** |
| **国产化替代（CXL 3.2 国产化）** | CoHDI 的多厂商解聚生态 = 国产 CXL/池化硬件的编排层机会——**不绑定单一厂商** |
| **超节点 O&M（管理网独立）** | 可组合解聚的动态挂载 = 运维的新维度（设备热插拔/热迁移）——与跨集群迁移（08-10 KubeVirt）同层 |

---

## 七、批判性审视

1. **PLoRA 的验证边界**：仅 H100 单卡 + 1000 适配器；「32GB/s 饱和」是短上下文——长上下文（KV cache 大）时带宽需求上升，饱和点可能不同；S-LoRA 基线是单机（未对比多机/其他池化系统）。
2. **PLoRA 的 NDP 面积**：<3.4% 是设计估算，真实芯片的面积/功耗/良率成本未验证；NDP 单元的计算能力（在池中做 LoRA 矩阵乘）的具体性能未披露。
3. **HMA-Serve 的跨厂商落地**：GDDR 加速器的**生态可用性**（谁家 GDDR 加速器有开放软件栈能跑 prefill？）未明确——「跨厂商」在论文中成立，在产品中可能受限；Qwen3 系列之外（如 MoE/长上下文）未验证。
4. **CoHDI 的 Sandbox 阶段**：Sandbox = 实验项目（CNCF 最早期）——**「官方化」是开始不是成熟**；DRA 本身仍演进中（与 HAMi 的关系未定论）；真实生产案例有限。
5. **KubeCon China 信息**：仅官网标题级确认（四会联合 + 日期地点），议程/议题未抓取——「核心议题」为推断。
6. **三篇的耦合**：PLoRA（学术）/ HMA-Serve（学术）/ CoHDI（工业）没有互引或互证——本文的「三阶段演进」框架是**分析性综合**，非事实链条。

---

## 八、可证伪预测（P1-P6）

- **P1（高置信）**：12 个月内 CXL 池化内存 + NDP 的 multi-LoRA/微服务场景出现 ≥2 个独立系统（非 PLoRA 作者）复现「32GB/s 饱和」结论——「带宽盈余换容量」成为共识（2027-08 核验）。
- **P2（中置信）**：CoHDI 在 12 个月内从 Sandbox 走向 Incubating（DRA 生态成熟度信号），且与 HAMi 形成明确分工（调度器 vs 解聚）而非竞争（2027-08 核验）。
- **P3（中置信）**：KubeCon China 2026（9/7-9）上出现 ≥3 个可组合解聚/内存池化/NDP 相关演讲——AI 基础设施软件栈成为中国云原生社区的下一主线（2026-10 核验）。
- **P4（中置信）**：跨厂商 MemHA 模式在 12 个月内出现首个商业产品化（GDDR prefill + HBM decode 的厂商配对）——「按阶段付费」从论文走向定价（2027-08 核验）。
- **P5（低置信）**：PLoRA 类 NDP 池化成为「DRAM 涨价对冲」的行业标准叙事——CXL 池化的价值主张从「容量」扩展到「计算卸载」（2027-08 核验）。
- **P6（低置信）**：K8s DRA + CoHDI 模式外溢到 GPU 集群编排——超节点的「设备池化/热挂载」成为 AI 基础设施默认能力（2027-08 核验）。

---

## 九、对本系统的启示

1. **「带宽盈余换容量/弹性」是架构决策原则**：PLoRA 证明链路带宽在多数推理场景是**盈余资源**——本地评估存储/互联方案时，不应只看峰值带宽，而要看**流量形态**（搬运 vs 就地计算）——「带宽够用 + 容量自由」常优于「带宽最大」。
2. **内存分层是「策略」不是「命运」**：KV 四层命运框架应补充主动策略维度——池化层不只兜底故障，还可主动承载适配器/冷 KV（PLoRA 式）——**分层目的从「存活」升维到「成本」**。
3. **DRA 是国产化编排的机会**：CoHDI 的多厂商解聚 + K8s DRA = 国产 CXL/池化硬件的**编排层机会**——不绑定单一厂商生态；本地 CXL 3.2 国产化主题应跟踪 CoHDI 生态进展。
4. **KubeCon China 值得跟踪**：9/7-9 上海四会联合——本地超节点/可组合解聚研究线可在会后补充现场信号（与 ODCC 9/2-4 北京形成 9 月中国窗口双事件）。
5. **评估视角**：PLoRA/HMA-Serve 都是「带宽-容量-成本」三角的重新权衡——**本地文档的量化标准（数值+单位+基线+条件）在这类架构比较中尤其关键**（32GB/s 是短上下文、6.6× 是平均、+4.8× 是 goodput-per-dollar——口径不同不可混用）。

---

## 参考来源

- [PLoRA: An NDP-Enhanced Pooled-Memory System for Cost-Efficient Multi-LoRA Serving](https://arxiv.org/abs/2608.05483) — Zhongkai Yu et al.；提交 2026-08-05（✅ arXiv 一手摘要）
- [HBM Is Not All You Need: Efficient Disaggregated LLM Serving across Memory-heterogeneous Accelerators](https://arxiv.org/abs/2606.29986) — Zhixiang Wei et al.；提交 2026-06-29（✅ arXiv 一手摘要）
- [Welcome CoHDI to the CNCF: Evolving Kubernetes into composable disaggregated infrastructures](https://www.cncf.io/blog/2026/07/28/welcome-cohdi-to-the-cncf-evolving-kubernetes-into-composable-disaggregated-infrastructures/) — Hyde Sugiyama (Red Hat) et al.；CNCF 官方博客，2026-07-28（✅ 一手全文）
- [CNCF 官网](https://www.cncf.io/) — KubeCon + CloudNativeCon + OpenInfra Summit + PyTorch Conference China 2026, 9/7-9 上海（✅ 官网确认）
- 本地：[LLM 系统软件成熟度（TensorCast/B300/PLoRA）](knowledge/03_AI/llm-techniques-principles/2026-08-10-llm-system-software-maturity-tensorcast-b300-plora-vibe.md)（08-10）
- 本地：[KubeVirt 跨集群迁移](knowledge/05_tools/devops/2026-08-10-kubevirt-cross-cluster-live-migration-evpn-deep-analysis.md)（08-10）
- 本地：MEMORY.md（FMS 复盘/闪存内存化/DRAM 涨价/CXL 对冲/KV 四层命运/HAMi Incubating）

> **诚实标注**：PLoRA/HMA-Serve 为一手 arXiv 摘要（未读全文，机制细节以摘要为准）；CoHDI 为一手 CNCF 官方博客全文；KubeCon China 为官网标题级确认。「三阶段演进」框架为本文分析性综合，非论文间事实链条。PLoRA 为单卡验证、HMA-Serve 跨厂商落地可行性未验证、CoHDI 处 Sandbox 早期阶段。

---

## Changelog

- 2026-08-10：创建。素材=arXiv 两篇一手摘要（PLoRA 2608.05483 / HMA-Serve 2606.29986）+ CNCF 官方博客（CoHDI）+ CNCF 官网（KubeCon China）；主线=内存解聚三阶段演进（容量共享→NDP→编排官方化）+ 跨厂商横向；PLoRA 深度展开（4+2 策略/link 成本模型/32GB/s 饱和机理）+ DRAM 涨价对冲执行依据；与 KV 分层/HBF/CXL 池化/HAMi 闭环；P1-P6 可证伪预测。
