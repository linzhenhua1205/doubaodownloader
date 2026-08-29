---
name: rdma-analyzer
description: Perform RDMA (Remote Direct Memory Access) analysis for high-performance networking in server systems. Use when: (1) user asks about RDMA protocols, RoCE, InfiniBand, (2) user wants to analyze RDMA performance, latency, bandwidth, (3) user mentions NVLink/NVSwitch for GPU communication, (4) RDMA、RoCE、InfiniBand、GPU通信、远程内存访问. Do NOT use for: general network troubleshooting, non-RDMA topics.
metadata:
  requires:
    bins: ["python3"]
  emoji: 🚀
---

# RDMA 分析技能 (RDMA Analyzer)

## 概述

本技能用于**服务器系统中高性能网络的 RDMA 分析**。覆盖 RoCE、InfiniBand、NVLink/NVSwitch 等远程直接内存访问技术的性能评估。

**用户关注维度**: SI/DI 分析 (占比 15%) — 用户深耕服务器硬件架构领域

---

## RDMA 分析框架

### 分析维度

| # | 分析维度 | 关键指标 | 标准参考 |
|:-:|:---------|:---------|:---------|
| 1 | **延迟分析** | 单向延迟、双向延迟、PFC 延迟 | InfiniBand 规范 |
| 2 | **带宽分析** | 峰值带宽、有效带宽、拥塞控制 | RoCEv2 规范 |
| 3 | **协议分析** | RDMA Read/Write、Send/Receive、原子操作 | IBTA 规范 |
| 4 | **可靠性分析** | PFC、ECN、重传机制、错误恢复 | IEEE 802.1Qbb |
| 5 | **NVLink 分析** | GPU-GPU 通信、拓扑、带宽、延迟 | NVIDIA NVLink 规范 |
| 6 | **NVSwitch 分析** | 交换架构、路由算法、热点分析 | NVIDIA NVSwitch 规范 |

### 分析工作流

```
1️⃣ 定义分析范围 → 2️⃣ 收集参数 → 3️⃣ 测量/仿真 → 4️⃣ 数据分析 → 5️⃣ 结论与建议
```

---

## 详细分析步骤

### 第1步：定义分析范围

| 项 | 要求 | 示例 |
|:---|:-----|:-----|
| **技术类型** | RoCEv2、InfiniBand、NVLink、NVSwitch | RoCEv2 + NVLink 4.0 |
| **速率** | 网络/链路速率 | 400Gbps HDR、900Gbps NVLink |
| **拓扑** | 胖树、Clos、Mesh、Ring | Clos 拓扑 |
| **设备** | HCA、Switch、GPU | NVIDIA H100 + NVSwitch |
| **协议版本** | RoCEv1/RoCEv2、IB HDR/FDR | RoCEv2 |

### 第2步：收集参数

| 参数类别 | 具体参数 | 来源 |
|:---------|:---------|:-----|
| **HCA 参数** | 端口数、速率、队列数、MR 大小 | HCA datasheet |
| **Switch 参数** | 端口数、交换容量、延迟 | Switch datasheet |
| **NVLink 参数** | 链路数、速率、拓扑 | GPU datasheet |
| **软件参数** | OFED 版本、驱动版本、RDMA Core | 系统配置 |

### 第3步：测量/仿真

#### RDMA 性能测量工具

```bash
# 单向延迟测试
ib_send_lat -d mlx5_0 -i 1 -s 2048

# 双向带宽测试
ib_send_bw -d mlx5_0 -i 1 --report_gbits

# NVLink 带宽测试
nvidia-smi nvlink --status

# GPU 通信测试
mpirun -np 2 --mca pml ucx --mca btl ^vader,tcp ./cuda_memcpy_test
```

#### RoCE 相关测量

```bash
# PFC 配置检查
ethtool -k eth0 | grep pfc

# ECN 配置检查
ethtool -k eth0 | grep ecn

# DCQCN 参数检查
cat /sys/class/net/eth0/queues/tx-0/ethtool/pause/autoneg
```

### 第4步：数据分析

#### 延迟分析

| 延迟分量 | 定义 | 典型值 (400G RoCE) |
|:---------|:-----|:-------------------|
| **线缆延迟** | 信号传输时间 | 1ns/m |
| **Switch 延迟** | 交换转发时间 | 50-100ns |
| **HCA 延迟** | 主机通道适配器处理时间 | 200-500ns |
| **软件延迟** | 驱动/协议栈处理时间 | 100-300ns |
| **总延迟** | 端到端延迟 | 500-1000ns |

#### 带宽分析

| 指标 | 公式 | 分析方法 |
|:-----|:-----|:---------|
| **峰值带宽** | 物理速率 × 编码效率 | 400G × 0.8 = 320GB/s |
| **有效带宽** | 实际吞吐量 | 使用 ib_send_bw 测量 |
| **利用率** | 有效带宽 / 峰值带宽 × 100% | ≥90% 为优秀 |

#### NVLink 拓扑分析

```
NVSwitch 48-port 架构:
┌─────────────────────────────────────────────────────────────┐
│                      NVSwitch                              │
├─────────┬─────────┬─────────┬─────────┬─────────┬─────────┤
│  GPU 0  │  GPU 1  │  GPU 2  │  GPU 3  │  GPU 4  │  GPU 5  │
│  H100   │  H100   │  H100   │  H100   │  H100   │  H100   │
└─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘
     │         │         │         │         │         │
     └─────────┴─────────┴─────────┴─────────┴─────────┘
                    NVLink 4.0 (900Gbps)
```

#### 可靠性分析

| 机制 | 作用 | 配置要点 |
|:-----|:-----|:---------|
| **PFC** | 基于优先级的流量控制 | 配置 PFC 优先级映射 |
| **ECN** | 显式拥塞通知 | 启用 ECN 标记 |
| **DCQCN** | 数据中心 QCN | 配置 DCQCN 参数 |
| **重传** | 链路层重传 | RoCEv2 使用 ARP 重传 |

### 第5步：结论与建议

输出结构化报告：

```markdown
## 📋 RDMA 分析报告

### 概览
- **技术**: RoCEv2 @ 400Gbps + NVLink 4.0
- **拓扑**: 2x NVSwitch, 12x H100 GPU
- **结论**: 合格/需改进/不合格

### 性能分析
| 指标 | 测量值 | 目标值 | 结论 |
|:-----|:------:|:------:|:-----|
| 单向延迟 | 650ns | <1µs | ✅ |
| 双向带宽 | 300GB/s | ≥280GB/s | ✅ |
| NVLink 带宽 | 900Gbps/link | 900Gbps | ✅ |

### 可靠性分析
| 机制 | 状态 | 配置 |
|:-----|:-----|:-----|
| PFC | ✅ 启用 | Priority 3,4 |
| ECN | ✅ 启用 | 标记阈值 80% |
| DCQCN | ✅ 启用 | 默认参数 |

### 改进建议
1. [建议1]: 优化 HCA 队列配置，减少延迟
2. [建议2]: 配置 PFC 死锁预防策略
3. [建议3]: 启用 Adaptive Routing 均衡流量
```

---

## 常用标准参考

| 标准 | 适用领域 | 关键指标 |
|:-----|:---------|:---------|
| **IBTA InfiniBand** | InfiniBand 协议 | 延迟、带宽、可靠性 |
| **IEEE 802.1Qbb** | PFC 标准 | 流量控制 |
| **IEEE 802.1Qau** | QCN 标准 | 拥塞控制 |
| **RoCEv2** | RDMA over Converged Ethernet | 协议规范 |
| **NVIDIA NVLink** | GPU 高速互连 | 链路速率、拓扑 |
| **NVIDIA NVSwitch** | GPU 交换架构 | 交换容量、路由 |

---

## 工具与脚本

```bash
# RDMA 性能测试
ib_send_lat / ib_send_bw / ib_read_lat / ib_write_lat

# NVLink 状态查询
nvidia-smi nvlink

# 网络配置检查
ethtool / ip link / tc

# 自定义分析脚本
python3 <base_dir>/scripts/rdma_analysis.py
python3 <base_dir>/scripts/nvlink_topology_analyzer.py
```

---

## 常见问题与解决方案

| 问题 | 症状 | 根因 | 解决方案 |
|:-----|:-----|:-----|:---------|
| 延迟过高 | RTT > 1µs | HCA 配置不当、驱动问题 | 优化队列配置、更新驱动 |
| 带宽不足 | 有效带宽 < 80% 峰值 | 拥塞、PFC 配置问题 | 启用 DCQCN、优化 PFC |
| PFC 死锁 | 网络完全阻塞 | PFC 优先级配置不当 | 配置死锁预防策略 |
| NVLink 链路故障 | GPU 通信失败 | 链路断开、配置错误 | 检查链路状态、重新配置 |

---

## 与其他 skills 协作

```
用户: "分析 RDMA 性能和 NVLink 拓扑"
→ rdma-analyzer: 执行 RDMA/NVLink 分析
→ si-analyzer: 分析底层信号完整性
→ deep-tech-writer: 输出深度技术分析文档
→ knowledge-wiki: 归档到 knowledge/hardware/rdma/
```

---

## 质量评分体系

| # | 评分维度 | 检查项 | 权重 |
|:-:|:---------|:-------|:-----|
| 1 | **分析完整性** | 是否覆盖延迟/带宽/协议/可靠性/NVLink | 30% |
| 2 | **数据准确性** | 数值是否有来源？单位是否正确？ | 25% |
| 3 | **标准合规** | 是否参考最新规范？指标是否符合标准？ | 20% |
| 4 | **建议可执行** | 改进建议是否具体、可落地？ | 15% |
| 5 | **文档规范** | 是否符合 changelog/TOC/来源标注规则？ | 10% |

**评分等级**：
- **优（85+）**: 可直接发布
- **良（70-84）**: 可发布，建议小修
- **需改进（50-69）**: 需重大修改
- **不合格（<50）**: 需重写