---
name: si-analyzer
description: Perform Signal Integrity (SI) analysis for high-speed interconnects in server/hardware systems. Use when: (1) user asks to analyze signal integrity, eye diagrams, timing margins, jitter, crosstalk, (2) user mentions PCIe/SerDes/NVLink signal analysis, (3) user wants to evaluate high-speed link performance, (4) 信号完整性、眼图、抖动、串扰、时序分析. Do NOT use for: general circuit analysis, software debugging, non-signal topics.
metadata:
  requires:
    bins: ["python3"]
  emoji: 🔌
---

# 信号完整性分析技能 (SI Analyzer)

## 概述

本技能用于**服务器/硬件系统中高速互连的信号完整性分析**。覆盖 PCIe、SerDes、NVLink、DDR、HBM 等高速接口的信号质量评估。

**用户关注维度**: 信号完整性 SI (占比 15%) — 用户深耕服务器硬件架构领域

---

## SI 分析框架

### 分析维度

| # | 分析维度 | 关键指标 | 标准参考 |
|:-:|:---------|:---------|:---------|
| 1 | **眼图分析** | 眼高、眼宽、抖动、噪声容限 | PCI-SIG、JEDEC 规范 |
| 2 | **抖动分析** | RJ、DJ、TJ、DDJ、ISI | IEEE 802.3、PCIe 规范 |
| 3 | **串扰分析** | NEXT、FEXT、串扰噪声 | IEC 61937、ANSI 标准 |
| 4 | **时序分析** | 建立时间、保持时间、时序裕量 | JEDEC DDR 规范 |
| 5 | **阻抗匹配** | 特征阻抗、反射、回波损耗 | IPC-2221、IPC-6502 |
| 6 | **电源完整性** | 电源噪声、SSN、地弹 | IEEE 1149.6 |

### 分析工作流

```
1️⃣ 定义分析范围 → 2️⃣ 收集参数 → 3️⃣ 仿真/测量 → 4️⃣ 数据分析 → 5️⃣ 结论与建议
```

---

## 详细分析步骤

### 第1步：定义分析范围

明确分析对象和边界：

| 项 | 要求 | 示例 |
|:---|:-----|:-----|
| **接口类型** | PCIe Gen5/6、DDR5、NVLink、HBM3 | PCIe Gen5 x16 |
| **速率** | 数据传输速率 | 32 GT/s |
| **拓扑结构** | 点对点、星型、菊花链 | 点对点直连 |
| **介质** | PCB、线缆、背板 | FR4 PCB |
| **长度** | 信号传输距离 | 15cm |
| **标准** | 参考规范版本 | PCI-SIG PCIe 6.0 |

### 第2步：收集参数

| 参数类别 | 具体参数 | 来源 |
|:---------|:---------|:-----|
| **信道参数** | 特征阻抗、损耗、色散、串扰系数 | 仿真模型/测量数据 |
| **驱动参数** | 输出摆幅、上升/下降时间、阻抗 | 芯片 datasheet |
| **接收参数** | 输入灵敏度、CTLE、DFE 系数 | 芯片 datasheet |
| **环境参数** | 温度、电压、工艺角 | 测试条件 |

### 第3步：仿真/测量

#### 仿真方法

```bash
# 使用 Python 进行 SI 仿真
python3 <base_dir>/scripts/si_simulation.py \
  --interface pcie6 \
  --rate 64 \
  --length 15 \
  --model fr4 \
  --output si_report.md
```

#### 测量方法

| 测量工具 | 用途 | 精度要求 |
|:---------|:-----|:---------|
| 采样示波器 | 眼图、抖动测量 | ≥16GS/s |
| TDR/TDT | 阻抗、反射测量 | ±1Ω |
| 网络分析仪 | S参数、回波损耗 | 300kHz-50GHz |

### 第4步：数据分析

#### 眼图分析

| 指标 | 公式 | 合格标准 |
|:-----|:-----|:---------|
| 眼高 | 实际眼高 / 理想眼高 × 100% | ≥20% (PCIe Gen5) |
| 眼宽 | 实际眼宽 / UI × 100% | ≥20% (PCIe Gen5) |
| 抖动 | TJ = RJ + DJ | ≤0.15UI (PCIe Gen5) |

#### 抖动分解

```
Total Jitter (TJ)
├── Random Jitter (RJ) — 高斯分布，由热噪声引起
└── Deterministic Jitter (DJ)
    ├── Data-Dependent Jitter (DDJ) — 码间干扰
    ├── Inter-Symbol Interference (ISI) — 符号间干扰
    └── Periodic Jitter (PJ) — 周期性抖动
```

#### 串扰分析

| 类型 | 定义 | 影响 |
|:-----|:-----|:-----|
| NEXT | 近端串扰 | 影响相邻通道 |
| FEXT | 远端串扰 | 影响远端通道 |
| D串扰 | 差分对串扰 | 影响差分信号 |

### 第5步：结论与建议

输出结构化报告：

```markdown
## 📋 SI 分析报告

### 概览
- **接口**: PCIe Gen5 x16 @ 32 GT/s
- **长度**: 15cm FR4 PCB
- **结论**: 合格/需改进/不合格

### 眼图分析
| 指标 | 测量值 | 标准值 | 结论 |
|:-----|:------:|:------:|:-----|
| 眼高 | 25% | ≥20% | ✅ |
| 眼宽 | 22% | ≥20% | ✅ |
| TJ | 0.12UI | ≤0.15UI | ✅ |

### 抖动分析
| 分量 | 数值 | 占比 |
|:-----|:-----|:-----|
| RJ | 0.05UI | 42% |
| DJ | 0.07UI | 58% |

### 改进建议
1. [建议1]: 缩短走线长度至 10cm
2. [建议2]: 使用低损耗材料 (Nelco N4000-13)
3. [建议3]: 添加 CTLE 均衡
```

---

## 常用标准参考

| 标准 | 适用领域 | 关键指标 |
|:-----|:---------|:---------|
| **PCI-SIG PCIe 6.0** | PCIe 接口 | 眼图模板、抖动容限 |
| **JEDEC DDR5** | DDR5 内存 | 时序参数、信号质量 |
| **IEEE 802.3ck** | Ethernet 800G | PAM4 信号规范 |
| **JEDEC HBM3** | HBM 内存 | TSV 信号、带宽 |
| **IPC-2221** | PCB 设计 | 阻抗规范 |
| **PCI-SIG CEM 5.0** | PCIe CEM 规范 | 连接器、背板 |

---

## 工具与脚本

```bash
# SI 仿真脚本
python3 <base_dir>/scripts/si_simulation.py

# 眼图分析脚本
python3 <base_dir>/scripts/eye_diagram_analyzer.py

# 抖动分析脚本
python3 <base_dir>/scripts/jitter_analysis.py

# 阻抗计算脚本
python3 <base_dir>/scripts/impedance_calculator.py
```

---

## 常见问题与解决方案

| 问题 | 症状 | 根因 | 解决方案 |
|:-----|:-----|:-----|:---------|
| 眼图闭合 | 眼高/眼宽不足 | 损耗过大、抖动超标 | 缩短走线、使用低损耗材料、添加均衡 |
| 串扰过大 | NEXT/FEXT 超标 | 线间距不足、耦合过强 | 增大线间距、使用屏蔽、优化层叠 |
| 反射严重 | 回波损耗超标 | 阻抗不匹配 | 优化端接、控制阻抗公差 |
| 电源噪声 | SSN 过大 | 电源平面设计不良 | 增加去耦电容、优化电源平面 |

---

## 与其他 skills 协作

```
用户: "分析 PCIe Gen5 信号完整性"
→ si-analyzer: 执行 SI 分析
→ deep-tech-writer: 输出深度技术分析文档
→ doc-reviewer: 审查文档质量
→ knowledge-wiki: 归档到 knowledge/hardware/signal_integrity/
```

---

## 质量评分体系

| # | 评分维度 | 检查项 | 权重 |
|:-:|:---------|:-------|:-----|
| 1 | **分析完整性** | 是否覆盖眼图/抖动/串扰/时序/阻抗/PI | 30% |
| 2 | **数据准确性** | 数值是否有来源？单位是否正确？ | 25% |
| 3 | **标准合规** | 是否参考最新规范？指标是否符合标准？ | 20% |
| 4 | **建议可执行** | 改进建议是否具体、可落地？ | 15% |
| 5 | **文档规范** | 是否符合 changelog/TOC/来源标注规则？ | 10% |

**评分等级**：
- **优（85+）**: 可直接发布
- **良（70-84）**: 可发布，建议小修
- **需改进（50-69）**: 需重大修改
- **不合格（<50）**: 需重写