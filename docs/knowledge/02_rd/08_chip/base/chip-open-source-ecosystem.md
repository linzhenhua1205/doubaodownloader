# 🔓 芯片设计开源生态全景：可复用资源库与Skill封装指南

> **版本**: v1.0 | **创建**: 2026-07-01
> **定位**: 从 GitHub 挖掘芯片设计/EDA/验证领域的可复用开源资源库，按功能分类整理，评估成熟度与适用场景，提出 Skill 化封装方案
>
> **关联文档**:
> - [🏭 芯片全生命周期与基础科学体系](chip-full-lifecycle-overview.md) — 10 阶段通用流程
> - [📏 芯片研发全流程指标参数与业界基准](chip-rd-metrics-industry-benchmark.md) — 15 阶段指标矩阵
> - [🔬 芯片测试全栈深度分析](../test/chip-test-full-stack-deep-analysis.md) — 测试体系
> - [🤖 ML for EDA 深度分析](chip-ml-for-eda-deep-analysis.md) — GNN/RL/BO 应用全景

---

## 📑 目录

1. [开源 EDA 生态全景速览](#1-开源-eda-生态全景速览)
2. [RTL 设计与 HDL 语言层](#2-rtl-设计与-hdl-语言层)
3. [逻辑综合](#3-逻辑综合)
4. [功能验证](#4-功能验证)
5. [物理设计与后端流程](#5-物理设计与后端流程)
6. [PDK 与工艺库](#6-pdk-与工艺库)
7. [芯片设计自动化与 ML for EDA](#7-芯片设计自动化与-ml-for-eda)
8. [RISC-V 核与 SoC 参考设计](#8-risc-v-核与-soc-参考设计)
9. [学习路径与课程资源](#9-学习路径与课程资源)
10. [各库成熟度评估](#10-各库成熟度评估)
11. [Skill 封装建议](#11-skill-封装建议)
12. [参考文献](#12-参考文献)

---

## 1. 开源 EDA 生态全景速览

### 1.1 开源 RTL-to-GDS 工具链全景

```
输入: RTL (Verilog/SystemVerilog/Chisel)
       │
       ▼
┌──────────────┐     ┌──────────────┐
│   Yosys      │────▶│  Synth        │  ← 逻辑综合 (Verilog→Netlist)
└──────────────┘     └──────┬───────┘
                            │
                            ▼
┌──────────────┐     ┌──────────────┐
│  OpenROAD    │────▶│  PnR           │  ← 布局布线 (Netlist→GDSII)
│  (OpenLANE)  │     │  floorplan     │
│              │     │  placement     │
│              │     │  CTS           │
│              │     │  routing       │
└──────────────┘     └──────┬───────┘
                            │
                            ▼
┌──────────────┐     ┌──────────────┐
│  KLayout     │────▶│  DRC/LVS       │  ← 物理验证
│  Magic       │     │  (需PDK)       │
└──────────────┘     └──────┬───────┘
                            │
                            ▼
                    ┌──────────────┐
                    │  GDSII        │  ← 交付晶圆厂
                    └──────────────┘
```

### 1.2 关键资源星际图

```
                        ⭐ 4.7K — Chisel (HDL语言)
                        ⭐ 4.6K — Yosys (综合)
                        ⭐ 3.6K — SkyWater PDK
                        ⭐ 505  — GF180MCU PDK
      ⭐ 774 — Edalize   ⭐ 358 — OpenLane2   ⭐ 150 — open-eda-course
      ⭐ 80  — SVUT      ⭐ 33  — veriflow-cc
```

### 1.3 工具链覆盖矩阵

| EDA 阶段 | 商业标杆 | 开源替代 | 成熟度 | 适用场景 |
|:---------|:---------|:---------|:------|:---------|
| RTL 设计 | Vivado/Design Compiler | Yosys + Chisel/Verilator | ★★★★☆ | 中小规模设计(~500K门) |
| 逻辑综合 | Synopsys DC | Yosys | ★★★★☆ | RTL→Netlist映射 |
| 功能仿真 | VCS/Xcelium | Verilator/Icarus/GHDL | ★★★★★ | 高性能仿真(Verilator) |
| UVM 验证 | VCS+UVM | UVM-Register (无完整UVM开源) | ★★☆☆☆ | 建议用cocotb替代 |
| 形式验证 | VC Formal/SymbiYosys | SymbiYosys (sby) | ★★★☆☆ | 中等复杂度属性验证 |
| 布局 | ICC2/Innovus | OpenROAD (RePlAce) | ★★★★☆ | 开源主力PnR引擎 |
| 时钟树综合 | ICC2 | OpenROAD (TritonCTS) | ★★★☆☆ | 标准单元CTS |
| 绕线 | ICC2 | OpenROAD (TritonRoute) | ★★★☆☆ | 详细绕线 |
| DRC/LVS | Calibre | KLayout + Magic | ★★★☆☆ | 需PDK支持 |
| 静态时序分析 | PrimeTime | OpenSTA | ★★★★☆ | 内嵌于OpenROAD |
| 功耗分析 | PrimePower | OpenROAD-Power | ★★★☆☆ | 中精度评估 |
| IR Drop | RedHawk | OpenROAD-PDN | ★★☆☆☆ | 仅早期评估 |
| 版图查看 | Calibre RVE | KLayout | ★★★★★ | 查看/导出/脚本化 |

---

## 2. RTL 设计与 HDL 语言层

### 2.1 Chisel — 现代硬件构建语言

| 属性 | 值 |
|:-----|:---|
| **仓库** | [chipsalliance/chisel](https://github.com/chipsalliance/chisel) |
| **星标** | ⭐ 4,702 |
| **语言** | Scala |
| **协议** | Apache-2.0 |
| **核心定位** | 嵌入式DSL在Scala中，生成Verilog/FIRRTL，支持参数化生成器 |

**技术优势**：
- 强类型 + 参数化生成器（`Module`, `Bundle`, `Vec`）
- `chisel3` → `firrtl` → `verilog` 三级编译，中间表示(FIRRTL)便于优化转换
- Berkeley 体系结构研究的事实标准(Rocket Chip/Boom)
- 适合 AI 加速器/自定义数据通路设计(Google TPUv1 用 Chisel 设计)

**适用场景**：
- ✅ 参数化硬件生成器(SRAM/NOC/MAC Array)
- ✅ 体系结构探索(快速的 RTL 迭代)
- ✅ SoC 集成总线/外设
- ❌ 不适合超高性能优化(需最终 Verilog 手工微调)

**Skill 封装价值**: 中 — 如团队使用 Scala/Chisel 则价值高，否则 Yosys + Verilator 更通用

### 2.2 Verilator — 高性能 Verilog 仿真器

| 属性 | 值 |
|:-----|:---|
| **仓库** | [verilator/verilator](https://github.com/verilator/verilator) |
| **星标** | ⭐ 3,800+ |
| **语言** | C++ |
| **协议** | LGPL-3.0 |
| **核心定位** | 将 Verilog/SystemVerilog 编译为 C++ 仿真模型，全球最快的开源仿真器 |

**技术优势**：
- 编译型仿真，比事件驱动仿真器快 10-100×
- 支持 SystemVerilog 2017 大部分内容(除部分验证结构)
- 输出周期精确模型，适合协同仿真(cocotb + Verilator)
- SiliconCarbon 和 IBM 等商业公司在生产中使用

**Skill 封装价值**: 高 ⭐ — 可作为「芯片功能仿真」Skill 的核心引擎

---

## 3. 逻辑综合

### 3.1 Yosys — 开源综合套件

| 属性 | 值 |
|:-----|:---|
| **仓库** | [YosysHQ/yosys](https://github.com/YosysHQ/yosys) |
| **星标** | ⭐ 4,560 |
| **语言** | C++ |
| **协议** | ISC |
| **核心定位** | Verilog RTL→Netlist 综合，支持脚本化 pass 流程 |

**技术细节**：
- 200+ 个 passes：`synth`, `opt`, `techmap`, `abc`, `dfflegalize` 等
- ABC 集成(UC Berkeley)：逻辑优化和工艺映射
- 支持 yosys-plugin 架构可扩展
- 输出多种格式：EDIF/BLIF/Verilog netlist/JSON

**适用场景**：
- ✅ ASIC 综合(SkyWater/GF 工艺)
- ✅ FPGA 综合(ICE40/ECP5/Gowin/Xilinx 部分)
- ✅ 形式验证预处理
- ✅ 教育/教学

**局限**：
- 大规模设计(>10M 门)性能不如 DC
- 缺乏高级综合策略(Timing-driven synth 较弱)

**Skill 封装价值**: 高 ⭐ — Yosys + ABC 是开源后端的入口

---

## 4. 功能验证

### 4.1 cocotb — 基于 Python 的协同仿真框架

| 属性 | 值 |
|:-----|:---|
| **仓库** | [cocotb/cocotb](https://github.com/cocotb/cocotb) |
| **星标** | ⭐ 1,500+ |
| **语言** | Python |
| **协议** | BSD |
| **核心定位** | 用 Python 编写 Verilog/VHDL testbench，与 Verilator/Icarus/VCS 协同仿真 |

**技术优势**：
- Python 生态全栈可用(numpy/scipy/pytest)
- 与 Verilator 配合达到最高仿真性能
- 支持异步协程（`@cocotb.test()`)
- cocotb-bus 库提供 AXI/AHB/APB 总线功能模型

**Skill 封装价值**: 高 ⭐ — Python+Verilator 是开源的「验证即代码」模式

### 4.2 SVUT — SystemVerilog 单元测试框架

| 属性 | 值 |
|:-----|:---|
| **仓库** | [dpretet/svut](https://github.com/dpretet/svut) |
| **星标** | ⭐ 80 |
| **语言** | Python |
| **协议** | MIT |
| **核心定位** | 极简的 Verilog/SV 单元测试框架，类似 CUnit |

**特点**：
- 自动生成 testbench 模板
- `$error`/`$warning` 等断言机制
- 与 Icarus/Verilator 集成

**Skill 封装价值**: 中 — 适合教育/入门，商业项目建议 cocotb

### 4.3 SymbiYosys — 形式验证框架

| 属性 | 值 |
|:-----|:---|
| **仓库** | [YosysHQ/sby](https://github.com/YosysHQ/sby) |
| **星标** | ⭐ 600+ |
| **语言** | Python |
| **协议** | ISC |
| **核心定位** | 基于 Yosys 的属性检查(Formal Verification)框架 |

**技术优势**：
- 支持 BMC(有界模型检查)/Prove(无条件证明)/Cover(可达性)
- 后端集成多个 SMT/SAT solver(Super4/z3/boolector)
- 适合中等复杂度模块的形式验证(如 FIFO/仲裁/FCS)

**Skill 封装价值**: 高 ⭐ — 形式验证在关键模块中是 VC Formal 的开源替代

### 4.4 VeriFlow-CC — Claude Code 驱动的 RTL 设计管线

| 属性 | 值 |
|:-----|:---|
| **仓库** | [bjwanneng/veriflow-cc](https://github.com/bjwanneng/veriflow-cc) |
| **星标** | ⭐ 33 |
| **语言** | Python |
| **协议** | 未指定 |
| **核心定位** | LLM 驱动 RTL 设计管线: 架构→RTL→综合 全自动 |

**特点**：
- Claude Code 驱动的子代理嵌套
- iVerilog + Yosys 后端
- 行为驱动的验证生成
- 与本工作空间的技术栈高度吻合(LLM + EDA)

**Skill 封装价值**: 极高 ⭐ — 可直接封装为 Chip-on-Chat 设计技能

---

## 5. 物理设计与后端流程

### 5.1 OpenROAD/OpenLane2 — 开源 RTL-to-GDS 流程

| 属性 | 值 |
|:-----|:---|
| **仓库** | [chipfoundry/openlane2](https://github.com/chipfoundry/openlane2) |
| **星标** | ⭐ 358 |
| **语言** | Python |
| **协议** | Apache-2.0 |
| **核心定位** | 完整的 RTL→GDSII 自动化流程，基于 OpenROAD 引擎 |

**组件栈**：
```
┌──────────────────────────────────────┐
│           OpenLane2 (编排层)           │
├──────────────────────────────────────┤
│ OpenROAD-apps: floorplan/place/CTS/  │
│ route/STA/PDN                        │
├──────────────────────────────────────┤
│ Yosys → ABC (综合)                    │
├──────────────────────────────────────┤
│ KLayout: DRC/LVS (物理验证)           │
├──────────────────────────────────────┤
│ PDK: SkyWater 130nm / GF 180nm       │
└──────────────────────────────────────┘
```

**Skill 封装价值**: 极高 ⭐ — 可作为「一键 RTL-to-GDS」技能的核心

### 5.2 KLayout — 版图查看与验证

| 属性 | 值 |
|:-----|:---|
| **仓库** | [KLayout/klayout](https://github.com/KLayout/klayout) |
| **星标** | ⭐ 1,300+ |
| **语言** | C++ |
| **协议** | GPL-3.0 |
| **核心定位** | GDSII/OASIS 版图查看、编辑、DRC 脚本、脚本化处理 |

**特点**：
- Ruby/Python 脚本接口，可写 DRC/LVS 脚本
- 支持大文件 GDSII (10GB+)
- 流片商(GF/TSMC/SMIC)有时接受 KLayout DRC
- OpenLane2 的默认物理验证工具

**Skill 封装价值**: 中 — 查看和基本 DRC 检查可封装

---

## 6. PDK 与工艺库

### 6.1 SkyWater PDK (sky130)

| 属性 | 值 |
|:-----|:---|
| **仓库** | [google/skywater-pdk](https://github.com/google/skywater-pdk) |
| **星标** | ⭐ 3,577 |
| **语言** | Python |
| **协议** | Apache-2.0 |
| **状态** | 已归档(Archived) |

**特点**：
- SkyWater 130nm 完全开源 PDK
- 含标准单元库、I/O 库、SRAM 编译器
- Google/Efabless 的 ChipIgnite 计划使用
- 定制模拟器件：NMOS/PMOS/varactor/res/BJT
- 商业访问：$1,500/免 300mm² (Efabless MPW)

**局限**：
- 130nm 老工艺，不适合高性能芯片
- 已归档(但仍可用)
- SRAM 编译器生成的存储器密度一般

### 6.2 GlobalFoundries GF180MCU PDK

| 属性 | 值 |
|:-----|:---|
| **仓库** | [google/gf180mcu-pdk](https://github.com/google/gf180mcu-pdk) |
| **星标** | ⭐ 505 |
| **语言** | Makefile |
| **协议** | Apache-2.0 |
| **状态** | 已归档(Archived) |

**特点**：
- GF 180nm MCU 工艺
- 工作电压 1.8V/3.3V/5V/6V
- 带 MIM 电容、高阻多晶硅电阻
- eFlash/NVM 支持

---

## 7. 芯片设计自动化与 ML for EDA

### 7.1 Edalize — EDA 工具抽象层

| 属性 | 值 |
|:-----|:---|
| **仓库** | [olofk/edalize](https://github.com/olofk/edalize) |
| **星标** | ⭐ 774 |
| **语言** | Python |
| **协议** | BSD-2 |
| **核心定位** | 统一 API 调用各种 EDA 工具(Vivado/Yosys/Quartus/Verilator) |

**特点**：
- 后端无关：同一个 Python API 调用不同工具
- 支持的 backend：yosys, vivado, quartus, icestorm, verilator, ghdl, modelsim, vcs
- FuseSoC 的事实后端标准

**Skill 封装价值**: 中 — 适合做 EDA 工具调用的通用抽象层

### 7.2 Veriflow-CC (LLM驱动的RTL设计)

| 属性 | 值 |
|:-----|:---|
| **仓库** | [bjwanneng/veriflow-cc](https://github.com/bjwanneng/veriflow-cc) |
| **星标** | ⭐ 33 (增长中) |
| **语言** | Python |
| **状态** | 活跃开发中 |

> 见章节 4.4。此仓库与本工作空间的 Agent+EDA 路线最吻合。

### 7.3 LangChain-VLSI Flow

| 属性 | 值 |
|:-----|:---|
| **仓库** | [SingularityKChen/langchain-vlsi-flow](https://github.com/SingularityKChen/langchain-vlsi-flow) |
| **星标** | ⭐ 7 |
| **语言** | Makefile/Python |
| **协议** | MIT |

**特点**：
- LangChain 驱动的 Verilog 生成 + OpenLane 后端
- 输入：自然语言 → 输出：GDS
- 概念验证性质(Open Issues 7个)

**Skill 封装价值**: 中 — 与 veriflow-cc 重叠，但可作为 pipeline 设计的参照

---

## 8. RISC-V 核与 SoC 参考设计

### 8.1 关键参考设计汇总

| 仓库 | 核心 | 工具链 | ⭐ | 说明 |
|:-----|:-----|:-------|:-:|:-----|
| [ShekharShwetank/RISC-V_RTL2GDSII](https://github.com/ShekharShwetank/RISC-V_RTL2GDSII) | RISC-V SoC | Yosys + OpenLane + KLayout | 12 | 完整 RTL→GDS 学习路径，含详细文档 |
| [galvin-benson/vsdRiscvSoc](https://github.com/galvin-benson/vsdRiscvSoc) | RISC-V | OpenLane | 2 | 从零开始的 SoC 设计 |
| [bintukappilgeorge/64-bit-RISC-V-processor-RV64IMAFD-SoC-Design](https://github.com/bintukappilgeorge/64-bit-RISC-V-processor-RV64IMAFD-SoC-Design) | RV64IMAFD | 商业/开源 | ~1 | 64位 RISC-V SoC 设计 |
| [Noamv7/Matrix-Multiplication-Using-Systolic-Arrays-Chip-Design-and-Verification](https://github.com/Noamv7/Matrix-Multiplication-Using-Systolic-Arrays-Chip-Design-and-Verification) | Systolic Array | Questa Sim | 15 | AI加速器设计+验证+APB总线 |
| [dhruvmittal41/chip-design-roadmap](https://github.com/dhruvmittal41/chip-design-roadmap) | 学习笔记 | 多工具 | — | 60天芯片设计学习路线(每日) |

---

## 9. 学习路径与课程资源

### 9.1 结构化学习资源

| 资源 | 类型 | 难度 | ⭐ | 链接 |
|:-----|:-----|:----|:-:|:-----|
| open-eda-course | 大学课程大纲 | 入门→中级 | 150 | [GitHub](https://github.com/asinghani/open-eda-course) |
| Beginner-SoC-Physical-Design-Workshop | 动手Workshop | 入门 | 14 | [GitHub](https://github.com/BidyenduGhoshal/Beginner-SoC-Physical-Design-Workshop) |
| chip-design-roadmap | 60天学习计划 | 入门→高级 | — | [GitHub](https://github.com/dhruvmittal41/chip-design-roadmap) |
| SystemVerilog-for-Verification | SV验证教程 | 入门→中级 | 1 | [GitHub](https://github.com/sarawiRTLDV/SystemVerilog-for-Verification) |
| open-digital-frontend | IP库+前端流程 | 中级 | 6 | [GitHub](https://github.com/Arcadia-1/open-digital-frontend) |

---

## 10. 各库成熟度评估

> 评估维度：社区活跃度(⭐+更新频率) × 代码质量 × 文档完整性 × Skill 化可行性(1-5星)

| 项目 | 社区 | 代码 | 文档 | Skill化 | 总分 | 建议 |
|:-----|:----|:----|:----|:-------|:----|:-----|
| **Yosys** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 4.5 | 必须集成 |
| **Chisel** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 4.25 | 如用Scala则高 |
| **SkyWater PDK** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | 3.75 | 已归档，建议使用 |
| **OpenLane2** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 4.0 | 主推后端Skill |
| **Verilator** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 4.5 | 主推仿真Skill |
| **cocotb** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 4.5 | 主推验证Skill |
| **SymbiYosys** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 3.5 | 形式验证Skill |
| **veriflow-cc** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | 3.0 | LLM+EDA原型 |
| **Edalize** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 3.25 | 工具抽象层 |
| **SVUT** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 2.75 | 轻量级用 |

---

## 11. Skill 封装建议

基于上述资源分析，建议按优先级顺序封装以下 Skills：

### 🥇 优先级 P0 — 立即封装

#### Skill 1: `chip-simulate-verilator` — Verilog/SystemVerilog 仿真

**核心引擎**: Verilator (编译型仿真) + cocotb (Python testbench)

**能力范围**:
- RTL 编译 + 仿真运行
- VCD/FST 波形输出
- Python testbench 脚本化验证
- 自动化覆盖率收集

**封装方式**: 轻量 CLI wrapper，调用 `verilator --cc` + `cocotb` + `gtkwave`

#### Skill 2: `chip-synthesize-yosys` — RTL 逻辑综合

**核心引擎**: Yosys + ABC

**能力范围**:
- RTL → Netlist (EDIF/BLIF)
- 时序报告生成
- 面积统计报告
- 工艺映射(SkyWater/GF/自定义)

**封装方式**: Tcl 脚本模板 + Yosys pass 链

#### Skill 3: `chip-pnr-openlane` — 布局布线自动化

**核心引擎**: OpenLane2 (OpenROAD 引擎栈)

**能力范围**:
- Floorplan → Placement → CTS → Routing → GDSII
- STA 时序签核
- IR Drop 分析
- DRC/LVS 检查 (KLayout)

**封装方式**: OpenLane2 配置文件生成 + 运行管控

### 🥈 优先级 P1 — 优化封装

#### Skill 4: `chip-verify-formal` — 形式验证

**核心引擎**: SymbiYosys (sby)

**能力范围**:
- BMC 有界模型检查
- 属性证明(unconditional prove)
- 覆盖分析(cover reachability)
- 适合 FIFO/仲裁器/FSM/协议检查

#### Skill 5: `chip-llm-design` — LLM 辅助 RTL 设计

**核心引擎**: veriflow-cc 工作流 + 自有 LLM

**能力范围**:
- 自然语言→RTL 生成
- 自动 testbench 生成
- 设计文档自动生成
- 综合结果反馈迭代

### 🥉 优先级 P2 — 按需封装

#### Skill 6: `chip-layout-view` — 版图查看与分析
**核心引擎**: KLayout (klayout)  
**能力**: GDSII 查看、测量、DRC 运行、导出 PNG/SVG

#### Skill 7: `chip-wavedrom` — 波形查看
**核心引擎**: GTKWave / Surfer  
**能力**: VCD/FST/FSDB 波形查看和导出

---

### 11.1 Skill 与现有工作空间技能的关系

```
现有 Skill                         新封装的 Chip Skill
──────────                        ──────────────────
light-backend-coding  ──────────▶ chip-synthesize-yosys (综合代码生成)
light-backend-coding  ──────────▶ chip-llm-design (LLM辅助RTL)
light-file-reading    ──────────▶ chip-layout-view (查看GDSII)
light-tool-selection  ──────────▶ (自动匹配合适的EDA工具)
doc-reviewer          ──────────▶ (审查设计文档/RTL质量)
```

---

## 12. 参考文献

1. YosysHQ. "Yosys Open Synthesis Suite." https://github.com/YosysHQ/yosys
2. chipsalliance. "Chisel: A Modern Hardware Design Language." https://github.com/chipsalliance/chisel
3. chipfoundry. "OpenLane2: The Next Generation OpenLane." https://github.com/chipfoundry/openlane2
4. google. "SkyWater PDK." https://github.com/google/skywater-pdk
5. verilator. "Verilator: Fast Verilog/SystemVerilog Simulator." https://github.com/verilator/verilator
6. cocotb. "Cocotb: COroutine based COsimulation TestBench." https://github.com/cocotb/cocotb
7. YosysHQ. "SymbiYosys: Formal Verification Framework." https://github.com/YosysHQ/sby
8. bjwanneng. "VeriFlow-CC: Claude Code-driven RTL design pipeline." https://github.com/bjwanneng/veriflow-cc
9. olofk. "Edalize: EDA tool abstraction library." https://github.com/olofk/edalize
10. OpenROAD Project. "OpenROAD: Autonomous RTL-to-GDSII." https://github.com/The-OpenROAD-Project

---

## 修订记录

| 日期 | 变更 | 版本 |
|:----|:-----|:----|
| 2026-07-01 | 首次创建 — 基于 GitHub API 采集的芯片设计开源生态全景，20+ 仓库评估与 7 个 Skill 封装建议 | v1.0 |
