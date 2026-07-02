# XCCL 集合通信库全景综述

> Source: [ZOMI Course] 02XCCL.pdf — chenzomi12.github.io, DeepLearningSystem 课程系列
> Copyright: ©2023 XXX Technologies (华为系模板), "把AI系统带入每个开发者..."
> 更多课程: GitHub [chenzomi12/AIFoundation](https://github.com/chenzomi12/AIFoundation)

XCCL（X Collective Communication Library）是为 AI 训练和推理设计的集合通信库，遵循 MPI API 规范，实现点对点通信（SEND/RECV）和集合通信（REDUCE/BROADCAST/ALLREDUCE/ALLGATHER/ALLTOALL 等）接口。

---

## XCCL 在 AI 系统中的位置

```
应用层: Megatron-LM (MindSpeed) / PyTorch / MindSpore
  ↓
框架层: User/API → Controller/Collective → Tensor/Bucket
  ↓
通信层: MPI / GLOO / NCCL / HCCL → Data Transfer
  ↓
传输层: RDMA / NVLink / RoCE / CXL / PCIe / SHMEM
  ↓
拓扑层: Ring / Tours / Fat-Tree / BigGraph
  ↓
物理层: CPU / NPU (GPU/TPU) / Physical Link
```

不同 XCCL 的核心功能都是实现 P2P 和 CC 算法，差异体现在：
1. **拓扑感知与编排** — 是否感知物理拓扑来编排通信路径
2. **网络传输优化** — 拥塞控制、路由协议、传输层优化
3. **端网协同** — 与自研交换机/网络架构的深度适配

---

## 业界主流 XCCL 对比

| 通信库 | 厂商 | 基础 | 核心特性 | 适用场景 |
|:-------|:-----|:-----|:---------|:---------|
| **NCCL** | NVIDIA | 自研 | 开源生态·灵活解耦·NetPlugin API | GPU 训练通用方案 |
| **ACCL** | 阿里云 | NCCL | BigGraph拓扑·HDRM算法·端网协同 | 阿里灵骏架构 |
| **TCCL** | 腾讯 | 自研 | 适配星脉网络 | 腾讯云训练集群 |
| **RCCL** | AMD | NCCL | ROCm 生态兼容 | AMD GPU 训练 |
| **OneCCL** | Intel | 自研 | 适配 Intel 平台 | CPU/XPU 训练 |
| **Gloo** | Meta | 自研 | 轻量·CPU友好 | 小规模/CPU 场景 |
| **HCCL** | 华为 | 自研 | 多层级架构·适配昇腾 | 昇腾 NPU 训练 |

---

## 🔍 NVIDIA NCCL

### 优势

- **开源生态**：支持用户自定义新算法（ACCL、TCCL 等均基于 NCCL 开发），内置基础通信算子开箱即用
- **灵活解耦**：与 CUDA 解耦单独发布，版本独立演进；暴露多层 API 兼顾自定义与易用性
- **插件化**：提供 NCCLNetPlugin API 支持自定义网络传输层
- **特性**：支持多网卡集合通信、GPUDirect RDMA、节点内多/单进程使用

### 不足

1. **拓扑感知有限** — 节点间拓扑识别能力、流量监控、信息获取能力有限
2. **RDMA 支持** — GPU+IB 效果好，但其他 RDMA 网络支持度一般
3. **异构网络** — 缺乏对 Clos/Torus/RDMA 等异构通信网络的系统级优化，需用户基于原子接口开发
4. **算法编排不感知拓扑** — 内置 Ring/Tree 算法只适合 Ring/Tree 物理拓扑，在 Fat-Tree 等拓扑上性能不佳
5. **容错粒度粗** — 任意执行过程出错，NCCL 整体重启

---

## 🔍 阿里 ACCL

> 来源: [阿里云 ACCL 用户指南](https://help.aliyun.com/zh/pai/user-guide/accl-alibaba-high-performance-collective-communication-library)
> 论文: EFLOPS: Algorithm and System Co-design for a High Performance Distributed Training Platform (2021)

基于 NCCL 开发，面向阿里云**灵骏（Lingjun）架构**设计，核心创新：

### BigGraph 网络拓扑

- **两层交换机分组互联**：每层交换机与另一层交换机全互联，两层间至少存在 N/2 个物理链路
- **最短路径确定性**：不同层次任意两个 device 间最短路径具有**唯一性**且等长
- 消除传统 Fat-Tree 的多路径拥塞问题

### HDRM（Halving-Doubling with Rank-Mapping）

- HD 算法的逻辑连接与 BigGraph 拓扑的物理链路进行显式映射
- 从集合通信管理层分配链路，**彻底解决链路争用**，避免网络拥塞

### 关键特性

- **异构拓扑感知**：节点内 PCIe / NVLink / NVSwitch + 节点间多轨 RDMA，分层混合利用不同互联带宽
- **端网协同选路**：算法与拓扑协同设计实现无拥塞通信，支撑训练性能上规模可扩展
- **在网多流负载均衡**：多任务并发、资源争抢时保障整体吞吐

---

## 🔍 华为 HCCL

从幻灯片中的 HCCL 架构图（第 12/23 页）可看出其 **6 层架构**：

```
┌────────────────────────────────────────────┐
│ 用户 API                                    │
├────────────────────────────────────────────┤
│ 通信算子(原语) API                           │
├────────────────────────────────────────────┤
│ hccl_comm (通信域管理)                      │
├────────────────────────────────────────────┤
│ Executor (算法执行) + hcclmpl (算法选择/组合)│
├────────────────────────────────────────────┤
│ Transport (传输管理)                        │
├────────────────────────────────────────────┤
│ Stream/Buffer(资源) → Dispatcher(下发)      │
├────────────────────────────────────────────┤
│ Runtime (运行时) + Driver (驱动)            │
├────────────────────────────────────────────┤
│ Communication (建链)                       │
└────────────────────────────────────────────┘
```

下一层包括公共支撑模块（公共组件）。

---

## 🔬 XCCL 创新方向

基于 NCCL 的开源生态，各厂商的创新集中在三大方向：

### 1️⃣ 基础/集合通信算法创新
- 开源网络拓扑编排算法优化
- 基础通信算子 & 集合通信算法优化

### 2️⃣ 网络传输优化
- 拥塞控制、路由控制优化
- 传输协议层、路由协议层细化操作

### 3️⃣ 端网协同专用优化
- 端网协同自研协议栈，匹配自研交换机
- 适配自研网络架构深度优化

---

## 总结与启示

1. **NCCL 是行业基础底座** — 所有主流 XCCL 要么基于 NCCL 扩展，要么兼容 NCCL API
2. **差异化在于硬件联动深度** — 自研网络拓扑（BigGraph）、自研交换机（星脉）、自研协议栈（HCCL）是拉开差距的关键
3. **端网协同是终极方向** — 只优化通信算法不够，需要与物理拓扑、网络协议、硬件能力深度耦合
4. **容错成为新瓶颈** — NCCL 的粗粒度容错在大规模集群（万卡级）中不可接受，各厂商均在自研细粒度容错方案

## Related

- [Multi-GPU Collective Communications](multi-gpu-collective-communications.md) — 通信原语基本原理与硬件实现
- [2026-06-04 分布式OS跟踪](../../01_survey/bmc-system/2026-06-04.md) — NCCL 2.30.3 GIN增强等最新动态
- [2026-06-03 分布式OS跟踪](../../01_survey/components-storage/2026-06-03.md) — NCCL 2.30 监控、OpenURMA、OptCC、UCCL-Zip
