# GPU Direct 通信技术体系

> 核心链路：[GPU Direct 技术] → [NCCL 集合通信](multi-gpu-collective-communications.md) → [拓扑感知调度](network-topology-aware-scheduling.md)
> 来源: [johng.cn](https://johng.cn/ai/gpu-direct) | 归档: 2026-06-04

---

## 🎯 核心定位

**GPU Direct** 是 NVIDIA 开发的 GPU 与外部设备（NIC/存储/其他GPU）之间**直接数据传输**技术家族，通过 DMA 绕过 CPU 和主机内存。是构建高性能 AI 基础设施的基础使能技术。

---

## 📊 四项子技术全景

| 技术 | 连接对象 | 带宽 | 延迟 | 适用场景 |
|:----|:---------|:----:|:----:|:---------|
| **GPU Direct Storage** | GPU ↔ 存储 | ~200+ GB/s | 低 | 数据加载、I/O 密集 |
| **GPU Direct P2P** | GPU ↔ GPU (PCIe) | ~128 GB/s | 中等 | 同节点多 GPU 通信 |
| **NVLink** | GPU ↔ GPU (直连) | 900 GB/s | 极低 | 大规模多 GPU |
| **NVSwitch** | GPU ↔ GPU (全互联) | 900 GB/s | 极低 | 超大规模 AI 训练 |

---

## 1️⃣ GPU Direct Storage（存储直连）

### 传统 I/O 瓶颈

```
存储 → CPU内核缓冲区(Bounce Buffer) → CPU内存 → GPU显存
       [第1次拷贝]           [第2次拷贝]
```

- AI 数据集从 TB 级到 PB 级
- GPU 算力已达 PFLOPS 级别，I/O 速度停滞
- 两次拷贝 + CPU 开销 = 严重性能损失

### GPU Direct Storage 原理

```
存储(DMA引擎) ──直接DMA──→ GPU显存
             ╳ 绕过CPU
             ╳ 绕过主机内存
```

- 存储控制器（如 NVMe 驱动）增强支持 GPU Direct
- DMA 引擎直接将数据从存储介质写入 GPU 显存
- **零拷贝**：物理层面直达
- 存储位置无关：本地 NVMe、NAS、NVMe-oF 均可

### 性能参考

| 方式 | 带宽 | 说明 |
|:-----|:----:|:------|
| 传统方式 | ~50 GB/s | 受限于 CPU 内存到 GPU 的 PCIe 带宽 |
| GPU Direct Storage | ~200 GB/s | 多路 NVMe + 多路网络并行直达 GPU |

**4倍带宽提升**，CPU 完全释放。

---

## 2️⃣ GPU Direct P2P（点对点通信）

### 用途
多 GPU 系统中频繁的数据交换：梯度同步（数据并行）、激活值传递（模型并行/流水线并行）。

### 传统方式 vs P2P

| 方式 | 拷贝次数 | CPU参与 | 延迟 |
|:-----|:--------:|:-------:|:----:|
| 传统（经 CPU） | 2次 | 高 | 高 |
| GPU Direct P2P | **1次** | 否（仅初始化） | **低（减半）** |

### 原理
- 同一 PCIe 总线/交换机下的 GPU 可直接访问彼此显存
- 源 GPU 将目标 GPU 显存地址映射到自己的地址空间
- GPU 自带 DMA 引擎搬运数据

### 局限性
- 仅限同一 PCIe 总线/交换机的 GPU
- 多 GPU 共享 PCIe 带宽 → 竞争
- PCIe 拓扑限制全互联规模

---

## 3️⃣ NVLink（高速 GPU 互联）

### 为什么需要 NVLink？

PCIe 4.0 单向仅 64 GB/s，且拓扑限制难实现单机多 GPU 全互联（如 8 卡）。

### 架构演进

| 代数 | 架构 | 单通道带宽 | 单GPU通道数 | 总带宽 | 代表产品 |
|:----|:-----|:---------:|:----------:|:-----:|:---------|
| NVLink 1.0 | Pascal | 20 GB/s | 4 | 160 GB/s | Tesla P100 |
| NVLink 2.0 | Volta | 25 GB/s | 6 | 300 GB/s | Tesla V100 |
| NVLink 3.0 | Ampere | 25 GB/s | 12 | 600 GB/s | A100 |
| NVLink 4.0 | Hopper | 25 GB/s | **18** | **900 GB/s** | H100 |

### 核心特性
- **超高带宽**：NVLink 4.0 900 GB/s vs PCIe 5.0 128 GB/s → **7 倍优势**
- **超低延迟**：点对点直连，NVLink 控制器集成在 GPU 芯片内
- **内存共享**：GPU 间可直接访问彼此显存，构建统一内存空间
- **Cache 一致性协议**：简化编程模型

### 局限
- 仍未全互联：8 GPU 两两直连需 28 条链路，单 GPU 最多 18 条无法满足

---

## 4️⃣ NVSwitch（全互联交换架构）

### 核心价值
NVIDIA 专有 GPU 高速交换芯片，实现**单节点内全 GPU 全互联无阻塞通信**。

### 架构

```
GPU0 ──→ NVSwitch ──→ GPU1
GPU2 ──→ NVSwitch ──→ GPU3
...     (完全二分图)     ...
GPU7 ──→ NVSwitch ──→ GPU6
```

- 每个 GPU 连接到所有 NVSwitch，每个 NVSwitch 连接到所有 GPU
- 任意两 GPU 间直达路径，无需多跳

### 规格

| 代次 | 架构 | 每端口 | 总交换带宽 | 搭载平台 |
|:-----|:-----|:------:|:---------:|:---------|
| NVSwitch 2.0 | Ampere | 50 GB/s双向 | 600 GB/s | DGX A100 |
| NVSwitch 3.0 | Hopper | 50 GB/s双向 | 900 GB/s | DGX H100 |

### 性能对比

| 架构 | 全互联 | 总带宽 | 延迟 | 可扩展性 |
|:-----|:------:|:------:|:----:|:--------:|
| PCIe P2P | ❌ | ~128 GB/s | 高 | 差 |
| NVLink 4.0 | ❌ | 900 GB/s | 低 | 中 |
| NVLink + NVSwitch | ✅ | **900 GB/s** | **极低** | **优** |

---

## 🔗 技术演进路径

```
GPU Direct Storage（解决I/O瓶颈）
         ↓
GPU Direct P2P（解决PCIe GPU间通信限制）
         ↓
NVLink（提供高速点对点互联）
         ↓
NVSwitch（实现全互联无阻塞）
         ↓
[NCCL集合通信（软件层通信库）](multi-gpu-collective-communications.md)
         ↓
[拓扑感知调度（调度层优化）](network-topology-aware-scheduling.md)
```

---

## 📎 关联知识

| 模块 | 文件 | 关系 |
|:-----|:-----|:-----|
| 分布式 OS | [NCCL 集合通信全景](multi-gpu-collective-communications.md) | GPU Direct 的软件层通信库抽象 |
| 分布式 OS | [XCCL 通信库全景综述](xccl-collective-communication-libraries.md) | 各厂商通信库对比 |
| 分布式 OS | [网络拓扑感知调度](network-topology-aware-scheduling.md) | 调度层利用 GPU Direct 能力的策略 |
| 运维系统 | [NFD & GFD](nfd-gfd.md) | 硬件特性发现（GPU/NVLink 标签） |
| 运维系统 | [GPU DCGM Exporter](ops-system/gpu-dcgm-exporter.md) | GPU 监控（含 NVLink CRC/Replay 错误） |
