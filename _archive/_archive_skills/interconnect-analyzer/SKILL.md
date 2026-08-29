---
name: interconnect-analyzer
description: Perform interconnect analysis for server hardware systems. Use when: (1) user asks about CPU-GPU interconnect, PCIe, CXL, (2) user wants to analyze system topology, bandwidth, latency, (3) user mentions UPI, QPI, HyperTransport, (4) 互连分析、PCIe、CXL、UPI、QPI、系统拓扑. Do NOT use for: general networking, non-interconnect topics.
metadata:
  requires:
    bins: ["python3"]
  emoji: 🔗
---

# 互连分析技能 (Interconnect Analyzer)

## 概述

本技能用于**服务器硬件系统的互连分析**。覆盖 PCIe、CXL、UPI、QPI、HyperTransport 等处理器间和设备间互连技术的性能评估与拓扑分析。

**用户关注维度**: 硬件架构分析 (占比 10%) — 用户深耕服务器硬件架构领域

---

## 互连分析框架

### 分析维度

| # | 分析维度 | 关键指标 | 标准参考 |
|:-:|:---------|:---------|:---------|
| 1 | **PCIe 分析** | 速率、带宽、拓扑、链路状态 | PCI-SIG 规范 |
| 2 | **CXL 分析** | CXL.mem、CXL.cache、CXL.io、协议分析 | CXL 规范 |
| 3 | **UPI/QPI 分析** | 处理器间互连、带宽、延迟 | Intel 架构手册 |
| 4 | **拓扑分析** | 系统架构、设备布局、链路连接 | 平台设计规范 |
| 5 | **带宽分析** | 峰值带宽、有效带宽、利用率 | 基准测试 |
| 6 | **延迟分析** | 端到端延迟、链路延迟、协议开销 | 测量数据 |

### 分析工作流

```
1️⃣ 定义分析范围 → 2️⃣ 收集参数 → 3️⃣ 测量/仿真 → 4️⃣ 数据分析 → 5️⃣ 结论与建议
```

---

## 详细分析步骤

### 第1步：定义分析范围

| 项 | 要求 | 示例 |
|:---|:-----|:-----|
| **互连类型** | PCIe、CXL、UPI、QPI、HyperTransport | PCIe 5.0 + CXL 2.0 + UPI |
| **速率** | 各链路速率 | PCIe: 32GT/s, CXL: 32GT/s, UPI: 11.2GT/s |
| **拓扑** | 设备连接方式 | 双路 UPI, PCIe 扩展槽, CXL 内存池 |
| **设备** | CPU、GPU、网卡、存储 | Intel Xeon + NVIDIA H100 + CXL Memory |
| **标准版本** | 协议版本号 | PCIe 5.0, CXL 2.0, UPI 2.0 |

### 第2步：收集参数

| 参数类别 | 具体参数 | 来源 |
|:---------|:---------|:-----|
| **CPU 参数** | 核心数、缓存、UPI 链路数 | CPU datasheet |
| **PCIe 参数** | 通道数、速率、编码方式 | PCIe 规范 |
| **CXL 参数** | CXL 类型、带宽、协议版本 | CXL 规范 |
| **系统参数** | 插槽数、内存容量、扩展槽数量 | 平台规格书 |

### 第3步：测量/仿真

#### 互连状态查询

```bash
# PCIe 状态查询
lspci -vv
lspci -t

# CXL 状态查询
cxl list
cxl topology

# UPI 状态查询
dmidecode -t processor
intel-qpi-info

# 带宽测试
pcie_bw_test
cxl_mem_bw_test
```

#### 拓扑可视化

```bash
# 使用 graphviz 绘制拓扑图
python3 <base_dir>/scripts/interconnect_topology.py --output topology.dot
dot -Tsvg topology.dot -o topology.svg
```

### 第4步：数据分析

#### PCIe 带宽计算

| PCIe 版本 | 每通道速率 | x16 峰值带宽 | 编码方式 |
|:----------|:----------:|:------------:|:---------|
| **Gen 1** | 2.5 GT/s | 8 GB/s | 8b/10b |
| **Gen 2** | 5 GT/s | 16 GB/s | 8b/10b |
| **Gen 3** | 8 GT/s | 32 GB/s | 128b/130b |
| **Gen 4** | 16 GT/s | 64 GB/s | 128b/130b |
| **Gen 5** | 32 GT/s | 128 GB/s | PAM4 |
| **Gen 6** | 64 GT/s | 256 GB/s | PAM4 |

**有效带宽** = 峰值带宽 × 编码效率 × 链路利用率

#### CXL 协议分析

```
CXL 协议分层:
┌─────────────────────────────────────────────┐
│              CXL 协议层                      │
├─────────────┬─────────────┬─────────────────┤
│  CXL.cache  │  CXL.mem    │    CXL.io       │
└─────────────┴─────────────┴─────────────────┘
┌─────────────────────────────────────────────┐
│              PCIe 物理层                      │
└─────────────────────────────────────────────┘
```

| CXL 类型 | 用途 | 典型带宽 |
|:---------|:-----|:---------|
| **CXL.io** | 设备 IO | PCIe 速率 |
| **CXL.cache** | 缓存一致性 | PCIe 速率 |
| **CXL.mem** | 内存扩展 | 32-64 GT/s |

#### UPI/QPI 分析

| 参数 | UPI 2.0 | QPI |
|:-----|:-------:|:-----|
| **峰值带宽** | 34.1 GB/s/link | 25.6 GB/s/link |
| **链路数** | 2-3 | 2-3 |
| **双路总带宽** | 68.2-102.3 GB/s | 51.2-76.8 GB/s |
| **延迟** | <100ns | <120ns |

#### 系统拓扑分析

```
双路服务器拓扑:
                    ┌─────────────────────────────────────────┐
                    │              UPI 链路                    │
                    │  Link 0: 34.1 GB/s  |  Link 1: 34.1 GB/s │
                    └─────────────────────────────────────────┘
                                ╱                ╲
                   ┌───────────┴───────────┐     │
                   │                       │     │
            ┌──────┴──────┐         ┌──────┴──────┐
            │   CPU 0     │         │   CPU 1     │
            │  Xeon 8480  │         │  Xeon 8480  │
            └──────┬──────┘         └──────┬──────┘
                   │                       │
            ┌──────┴──────┐         ┌──────┴──────┐
            │    L3 Cache │         │    L3 Cache │
            │    60 MB    │         │    60 MB    │
            └──────┬──────┘         └──────┬──────┘
                   │                       │
            ┌──────┴──────┐         ┌──────┴──────┐
            │  DDR5 DIMM  │         │  DDR5 DIMM  │
            │  6x 32GB    │         │  6x 32GB    │
            └──────┬──────┘         └──────┬──────┘
                   │                       │
            ┌──────┴──────────────────────┴──────┐
            │          PCIe 5.0 Root Port        │
            └──────┬───────────┬───────────┬──────┘
                   │           │           │
            ┌──────┴──────┐┌──────┴──────┐┌──────┴──────┐
            │   GPU H100  ││   NIC 400G  ││  CXL Mem   │
            │  PCIe x16   ││  PCIe x8    ││  CXL x16   │
            └─────────────┘└─────────────┘└─────────────┘
```

### 第5步：结论与建议

输出结构化报告：

```markdown
## 📋 互连分析报告

### 概览
- **架构**: 双路 Intel Xeon 8480
- **互连**: UPI 2.0 + PCIe 5.0 + CXL 2.0
- **结论**: 合格/需改进/不合格

### PCIe 分析
| 设备 | 速率 | 通道数 | 峰值带宽 | 结论 |
|:-----|:-----|:------:|:--------:|:-----|
| GPU H100 | 32 GT/s | x16 | 128 GB/s | ✅ |
| NIC 400G | 32 GT/s | x8 | 64 GB/s | ✅ |
| CXL Mem | 32 GT/s | x16 | 128 GB/s | ✅ |

### UPI 分析
| 指标 | 测量值 | 目标值 | 结论 |
|:-----|:------:|:------:|:-----|
| 链路数 | 2 | 2 | ✅ |
| 总带宽 | 68.2 GB/s | ≥60 GB/s | ✅ |
| 延迟 | 85ns | <100ns | ✅ |

### CXL 分析
| 类型 | 速率 | 用途 | 结论 |
|:-----|:-----|:-----|:-----|
| CXL.io | 32 GT/s | IO 设备 | ✅ |
| CXL.mem | 32 GT/s | 内存扩展 | ✅ |

### 改进建议
1. [建议1]: 添加第三条 UPI 链路提升跨插槽带宽
2. [建议2]: 使用 PCIe 6.0 提升 GPU 带宽至 256 GB/s
3. [建议3]: 扩展 CXL 内存池至 512GB
```

---

## 常用标准参考

| 标准 | 适用领域 | 关键指标 |
|:-----|:---------|:---------|
| **PCI-SIG PCIe 6.0** | PCIe 接口 | 速率、带宽、编码 |
| **CXL 3.0** | CXL 协议 | CXL.mem、CXL.cache、CXL.io |
| **Intel UPI** | 处理器互连 | 带宽、延迟、链路数 |
| **AMD Infinity Fabric** | AMD 处理器互连 | 带宽、延迟 |
| **PCI-SIG CEM** | PCIe CEM 规范 | 连接器、背板 |

---

## 工具与脚本

```bash
# PCIe 工具
lspci / setpci / pcie_bw_test

# CXL 工具
cxl / cxl-cli / cxl_mem_bw_test

# UPI 工具
intel-qpi-info / dmidecode

# 拓扑可视化
graphviz / python3 <base_dir>/scripts/interconnect_topology.py

# 自定义分析脚本
python3 <base_dir>/scripts/interconnect_analysis.py
python3 <base_dir>/scripts/pcie_analyzer.py
```

---

## 常见问题与解决方案

| 问题 | 症状 | 根因 | 解决方案 |
|:-----|:-----|:-----|:---------|
| PCIe 带宽不足 | 吞吐量低于预期 | 链路降速、编码错误 | 检查链路状态、更新固件 |
| UPI 瓶颈 | 跨插槽通信慢 | UPI 带宽不足 | 添加 UPI 链路、优化 NUMA 布局 |
| CXL 内存延迟 | 访问 CXL 内存慢 | CXL 协议开销 | 使用 CXL.cache 模式、优化访问模式 |
| 拓扑复杂 | 系统扩展困难 | PCIe 根端口不足 | 使用 PCIe Switch 扩展 |

---

## 与其他 skills 协作

```
用户: "分析服务器系统互连架构"
→ interconnect-analyzer: 执行互连分析
→ si-analyzer: 分析信号完整性
→ rdma-analyzer: 分析网络互连性能
→ deep-tech-writer: 输出深度技术分析文档
→ knowledge-wiki: 归档到 knowledge/hardware/interconnect/
```

---

## 质量评分体系

| # | 评分维度 | 检查项 | 权重 |
|:-:|:---------|:-------|:-----|
| 1 | **分析完整性** | 是否覆盖 PCIe/CXL/UPI/拓扑/带宽/延迟 | 30% |
| 2 | **数据准确性** | 数值是否有来源？单位是否正确？ | 25% |
| 3 | **标准合规** | 是否参考最新规范？指标是否符合标准？ | 20% |
| 4 | **建议可执行** | 改进建议是否具体、可落地？ | 15% |
| 5 | **文档规范** | 是否符合 changelog/TOC/来源标注规则？ | 10% |

**评分等级**：
- **优（85+）**: 可直接发布
- **良（70-84）**: 可发布，建议小修
- **需改进（50-69）**: 需重大修改
- **不合格（<50）**: 需重写