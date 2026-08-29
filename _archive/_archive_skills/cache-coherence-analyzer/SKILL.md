---
name: cache-coherence-analyzer
description: Perform cache coherence analysis for multi-core/multi-socket server architectures. Use when: (1) user asks about cache coherence protocols, MESI/MOESI, (2) user wants to analyze cache performance, hit rate, false sharing, (3) user mentions NUMA architecture, memory hierarchy, (4) 缓存一致性、MESI、MOESI、NUMA、内存层次结构. Do NOT use for: general software performance, non-cache topics.
metadata:
  requires:
    bins: ["python3"]
  emoji: 🧠
---

# 缓存一致性分析技能 (Cache Coherence Analyzer)

## 概述

本技能用于**多核/多插槽服务器架构的缓存一致性分析**。覆盖 MESI/MOESI 协议、NUMA 架构、内存层次结构、缓存性能优化。

**用户关注维度**: 缓存一致性分析 (占比 10%) — 用户深耕服务器硬件架构领域

---

## 缓存一致性分析框架

### 分析维度

| # | 分析维度 | 关键指标 | 标准参考 |
|:-:|:---------|:---------|:---------|
| 1 | **协议分析** | MESI/MOESI/MESIF 状态转换、总线事务 | Intel/AMD 架构手册 |
| 2 | **缓存性能** | 命中率、缺失率、平均访问时间 | SPEC CPU 基准 |
| 3 | **伪共享分析** | False Sharing、Cache Line 冲突 | Intel VTune |
| 4 | **NUMA 分析** | 本地/远程访问比例、内存亲和性 | numactl |
| 5 | **内存层次** | L1/L2/L3/LLC 配置、带宽、延迟 | CPU datasheet |
| 6 | **一致性协议** | snooping、directory、hybrid | 架构规范 |

### 分析工作流

```
1️⃣ 定义分析范围 → 2️⃣ 收集参数 → 3️⃣ 测量/仿真 → 4️⃣ 数据分析 → 5️⃣ 结论与建议
```

---

## 详细分析步骤

### 第1步：定义分析范围

| 项 | 要求 | 示例 |
|:---|:-----|:-----|
| **架构** | x86、ARM、RISC-V | Intel Sapphire Rapids |
| **核心数** | 物理核心、逻辑核心 | 64 核心 (128 线程) |
| **插槽数** | 单路、双路、四路 | 双路 |
| **缓存配置** | L1/L2/L3 大小、关联性 | L1: 64KB, L2: 1.25MB, L3: 36MB |
| **协议** | MESI、MOESI、MESIF | MESIF |
| **NUMA 节点** | 节点数、内存分布 | 2 NUMA 节点 |

### 第2步：收集参数

| 参数类别 | 具体参数 | 来源 |
|:---------|:---------|:-----|
| **CPU 参数** | 核心数、缓存大小、频率 | CPU datasheet |
| **缓存参数** | L1/L2/L3 延迟、带宽 | 架构手册 |
| **NUMA 参数** | 节点数、内存容量、跨节点延迟 | numactl |
| **软件参数** | 线程数、内存分配策略、亲和性 | 应用配置 |

### 第3步：测量/仿真

#### 缓存性能测量

```bash
# 缓存性能分析
perf stat -e L1-dcache-loads,L1-dcache-load-misses,LLC-loads,LLC-load-misses ./app

# NUMA 分析
numastat

# 内存带宽测试
mbw -n 10 1024

# 伪共享检测
intel-vtune -collect memory-access -app ./app

# NUMA 配置检查
numactl --hardware
```

#### 缓存协议仿真

```bash
# 使用 gem5 进行缓存协议仿真
build/X86/gem5.opt configs/example/se.py \
  --cpu-type=DerivO3CPU \
  --caches --l2cache \
  --num-cpus=4 \
  --mem-size=8GB \
  --ruby \
  --protocol=MESI_Two_Level \
  --script=./workload.py
```

### 第4步：数据分析

#### 缓存状态机 (MESI)

```
MESI 状态转换图:
                    ┌───────────┐
                    │   Modified│
                    │    (M)    │
                    └─────┬─────┘
                          │ Write Back + Invalidate
                          ▼
        ┌─────────────┬───────────┬─────────────┐
        │   Invalid   │   Shared  │    Exclusive│
        │     (I)     │    (S)    │      (E)    │
        └─────────────┴───────────┴─────────────┘
```

#### 缓存命中率分析

| 缓存层级 | 典型命中率 | 典型延迟 |
|:---------|:---------:|:---------|
| **L1** | 95-99% | 1-2 周期 |
| **L2** | 90-95% | 4-8 周期 |
| **L3** | 80-90% | 15-30 周期 |
| **DRAM** | - | 100-200 周期 |

**平均访问时间 (AMAT)**:
```
AMAT = L1延迟 + (1-L1命中率) × L2延迟 + (1-L2命中率) × L3延迟 + (1-L3命中率) × DRAM延迟
```

#### 伪共享分析

| 现象 | 描述 | 影响 |
|:-----|:-----|:-----|
| **False Sharing** | 不同数据共享同一 Cache Line | 频繁无效化，性能下降 10-100x |
| **True Sharing** | 多个核心访问同一数据 | 需要一致性协议协调 |
| **Cache Line Ping-Pong** | 数据在核心间频繁迁移 | 严重性能问题 |

**检测方法**:
```bash
# 使用 perf 检测缓存无效化
perf stat -e cache-misses,L1-dcache-store-misses,LLC-store-misses ./app

# 使用 VTune 检测伪共享
vtune -collect uarch-exploration -app ./app
```

#### NUMA 分析

| 指标 | 定义 | 分析方法 |
|:-----|:-----|:---------|
| **本地访问比例** | 访问本地 NUMA 节点内存的比例 | ≥90% 为优秀 |
| **远程访问比例** | 访问远程 NUMA 节点内存的比例 | ≤10% 为优秀 |
| **跨节点延迟** | 远程访问相对于本地访问的延迟比 | 2-3x 为典型 |

### 第5步：结论与建议

输出结构化报告：

```markdown
## 📋 缓存一致性分析报告

### 概览
- **架构**: Intel Sapphire Rapids, 2-socket, 64 cores
- **缓存**: L1:64KB, L2:1.25MB, L3:36MB
- **协议**: MESIF
- **结论**: 合格/需改进/不合格

### 缓存性能
| 指标 | 测量值 | 目标值 | 结论 |
|:-----|:------:|:------:|:-----|
| L1 命中率 | 97% | ≥95% | ✅ |
| L2 命中率 | 92% | ≥90% | ✅ |
| L3 命中率 | 85% | ≥80% | ✅ |
| AMAT | 3.5 周期 | - | ✅ |

### NUMA 分析
| 指标 | 测量值 | 目标值 | 结论 |
|:-----|:------:|:------:|:-----|
| 本地访问比例 | 88% | ≥90% | ⚠️ |
| 远程访问比例 | 12% | ≤10% | ⚠️ |

### 伪共享分析
| 指标 | 测量值 | 结论 |
|:-----|:------:|:-----|
| Cache Line 无效化率 | 15% | ⚠️ 存在伪共享 |

### 改进建议
1. [建议1]: 使用 numactl 绑定进程到 NUMA 节点
2. [建议2]: 调整数据结构布局，避免伪共享
3. [建议3]: 使用 thread_local 或 padding 隔离共享数据
```

---

## 常用标准参考

| 标准 | 适用领域 | 关键指标 |
|:-----|:---------|:---------|
| **Intel Architecture Manual** | x86 架构 | 缓存层次、一致性协议 |
| **AMD Architecture Manual** | AMD 架构 | MESI/MOESI 协议 |
| **ARM ARM** | ARM 架构 | cache 一致性、CCI |
| **SPEC CPU 2017** | 性能基准 | 缓存命中率、AMAT |
| **NUMA 最佳实践** | NUMA 编程 | 内存亲和性、调度 |

---

## 工具与脚本

```bash
# 性能分析工具
perf / numactl / numastat / mbw

# VTune 分析
intel-vtune

# gem5 仿真
gem5

# 自定义分析脚本
python3 <base_dir>/scripts/cache_analysis.py
python3 <base_dir>/scripts/numa_analyzer.py
```

---

## 常见问题与解决方案

| 问题 | 症状 | 根因 | 解决方案 |
|:-----|:-----|:-----|:---------|
| 缓存命中率低 | AMAT 过高 | 数据局部性差、工作集过大 | 优化数据布局、使用预取、减少工作集 |
| 伪共享 | 频繁无效化 | 不同数据共享 Cache Line | 填充 Cache Line、使用 thread_local |
| NUMA 远程访问 | 延迟增加 | 内存分配与核心不在同一节点 | 使用 numactl、设置内存亲和性 |
| Cache Thrashing | 缓存颠簸 | 多个进程竞争缓存 | 减少并发数、使用缓存分区 |

---

## 与其他 skills 协作

```
用户: "分析多插槽服务器缓存一致性"
→ cache-coherence-analyzer: 执行缓存一致性分析
→ deep-tech-writer: 输出深度技术分析文档
→ knowledge-wiki: 归档到 knowledge/hardware/cache_coherence/
```

---

## 质量评分体系

| # | 评分维度 | 检查项 | 权重 |
|:-:|:---------|:-------|:-----|
| 1 | **分析完整性** | 是否覆盖协议/性能/伪共享/NUMA/内存层次 | 30% |
| 2 | **数据准确性** | 数值是否有来源？单位是否正确？ | 25% |
| 3 | **标准合规** | 是否参考最新规范？指标是否符合标准？ | 20% |
| 4 | **建议可执行** | 改进建议是否具体、可落地？ | 15% |
| 5 | **文档规范** | 是否符合 changelog/TOC/来源标注规则？ | 10% |

**评分等级**：
- **优（85+）**: 可直接发布
- **良（70-84）**: 可发布，建议小修
- **需改进（50-69）**: 需重大修改
- **不合格（<50）**: 需重写