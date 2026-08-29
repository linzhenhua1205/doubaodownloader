# L4 集成→实现：综合、时序与物理实现方法

> **概要**: 芯片 L4 层集成到实现方法，涵盖综合、时序约束、DFT 插入与布局布线
>
> **关键词**: 逻辑综合 · 时序约束 · DFT · 布局布线 · PPA优化

---

## 📑 目录

- [📖 文档导读](#文档导读)
- [1️⃣ L4 层定位与工作全景](#1-l4-层定位与工作全景)
  - [1.1 L4 在六层金字塔中的角色](#11-l4-在六层金字塔中的角色)
  - [1.2 L4 工作流全景](#12-l4-工作流全景)
- [2️⃣ 综合策略与流程方法](#2-综合策略与流程方法)
  - [2.1 综合流程](#21-综合流程)
  - [2.2 综合策略选择](#22-综合策略选择)
  - [2.3 综合脚本模板](#23-综合脚本模板)
- [3️⃣ 时序约束方法论](#3-时序约束方法论)
  - [3.1 时序约束体系](#31-时序约束体系)
  - [3.2 时钟定义规范](#32-时钟定义规范)
  - [3.3 I/O 时序约束](#33-io-时序约束)
  - [3.4 例外路径约束](#34-例外路径约束)
  - [3.5 时序报告分析方法](#35-时序报告分析方法)
- [4️⃣ 逻辑综合优化技术](#4-逻辑综合优化技术)
  - [4.1 面积/时序/功耗优化选项](#41-面积时序功耗优化选项)
  - [4.2 不同目标的综合策略](#42-不同目标的综合策略)
  - [4.3 综合后网表质量检查](#43-综合后网表质量检查)
- [5️⃣ DFT 插入与测试逻辑](#5-dft-插入与测试逻辑)
  - [5.1 DFT 策略全景](#51-dft-策略全景)
  - [5.2 Scan 插入流程](#52-scan-插入流程)
  - [5.3 MBIST 集成](#53-mbist-集成)
  - [5.4 测试覆盖率目标](#54-测试覆盖率目标)
- [6️⃣ 布局规划与电源网络](#6-布局规划与电源网络)
  - [6.1 芯片布局规划方法](#61-芯片布局规划方法)
  - [6.2 布局规划关键规则](#62-布局规划关键规则)
  - [6.3 电源网络设计](#63-电源网络设计)
- [7️⃣ 布局布线方法](#7-布局布线方法)
  - [7.1 布局阶段](#71-布局阶段)
  - [7.2 时钟树综合（CTS）策略](#72-时钟树综合cts策略)
  - [7.3 布线阶段](#73-布线阶段)
- [8️⃣ PPA 优化与收敛](#8-ppa-优化与收敛)
  - [8.1 PPA 收敛流程](#81-ppa-收敛流程)
  - [8.2 各维度优化技术汇总](#82-各维度优化技术汇总)
  - [8.3 PPA 收敛条件](#83-ppa-收敛条件)
- [9️⃣ 签核与时序收敛](#9-签核与时序收敛)
  - [9.1 签核分析维度](#91-签核分析维度)
  - [9.2 多 Corner 时序收敛](#92-多-corner-时序收敛)
  - [9.3 签核准出条件](#93-签核准出条件)
- [🔟 常见实现失败模式](#常见实现失败模式)
  - [10.1 失败模式汇总](#101-失败模式汇总)
  - [10.2 典型案例：时序收敛失败](#102-典型案例时序收敛失败)
- [1️⃣1️⃣ 产出物与检查清单](#11-产出物与检查清单)
  - [11.1 L4 产出物清单](#111-l4-产出物清单)
  - [11.2 L4 检查清单](#112-l4-检查清单)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

---

## 📖 文档导读

| 章节 | 内容 |
|:-----|:-----|
| §1 | L4 定位与工作全景 |
| §2 | 综合策略与流程方法 |
| §3 | 时序约束方法论 |
| §4 | 逻辑综合优化技术 |
| §5 | DFT 插入与测试逻辑 |
| §6 | 布局规划与电源网络 |
| §7 | 布局布线方法 |
| §8 | PPA 优化与收敛 |
| §9 | 签核与时序收敛 |
| §10 | 常见实现失败模式 |
| §11 | 产出物与检查清单 |

---

## 1️⃣ L4 层定位与工作全景

### 1.1 L4 在六层金字塔中的角色

```text
L6 -- 需求 -> 架构
L5 -- 架构 -> 集成（已交付可综合 RTL）

L4 -- 集成 -> 实现 --- ★ 本层：RTL->门级网表的转换
      v 产出：综合网表 | 时序约束 | 布局布线 | PPA 报告
      v 关键活动：综合 · DFT · 布局布线 · 时序收敛
      v 时间占比：~25% · 最依赖 EDA 工具的一层

L3 -- 实现 -> 验证
L2 -- 验证 -> 制造
L1 -- 制造 -> 测试
```

**核心洞察**：L4 是六层中 **工具依赖度最高** 的一层，也是 **PPA 落地** 的关键阶段。架构阶段的 PPA 估算（±30%）在这一层要收敛到 ±5% 以内。

### 1.2 L4 工作流全景

```text
+---------------------------------------------------------------------+
|                   L4 实现工作流（从 RTL 到 GDSII 的准备）              |
|                                                                     |
|  +----------+   +----------+   +----------+   +----------+         |
|  |逻辑综合   |   |DFT插入   |   |布局布线   |   |签核      |         |
|  |          |->  |          |->  |          |->  |          |         |
|  | . 综合    |   | . Scan   |   | . Floor-  |   | . 时序    |         |
|  | . 映射    |   | . MBIST  |   |   plan    |   | . 功耗    |         |
|  | . 优化    |   | . ATPG   |   | . Place   |   | . SI     |         |
|  | . 预STA  |   | . 测试   |   | . Route   |   | . EM/IR  |         |
|  |          |   |   时序    |   | . STA     |   | . DRC    |         |
|  |          |   |          |   | . 物理优化 |   |          |         |
|  +----------+   +----------+   +----------+   +----------+         |
|                                                                     |
|          每步均以 PPA 为目标，迭代 3-5 轮收敛                            |
|                                                                     |
|  检查点 G4：签核报告通过 -> 交付网表和约束至 L3（后仿真）                 |
+---------------------------------------------------------------------+
```

---

## 2️⃣ 综合策略与流程方法

### 2.1 综合流程

```text
+---------------------------------------------------------------------+
|                   逻辑综合工作流                                       |
|                                                                     |
|  Input: RTL (.v/.sv) + 时序约束 (.sdc) + 工艺库 (.lib)              |
|                                                                     |
|  Step 1: 转译（Elaboration）                                         |
|    +-- 读取 RTL 并解析为 HDL 中间表达                                  |
|    +-- 检查语法错误、参数化、模块例化                                  |
|    +-- 输出：GTECH 网表（工艺无关库单元）                              |
|                                                                     |
|  Step 2: 逻辑优化                                                    |
|    +-- 常量传播（Constant Propagation）                               |
|    +-- 表达式化简（Resource Sharing）                                 |
|    +-- 状态机编码优化（Binary/Gray/One-hot）                           |
|    +-- 输出：优化后 GTECH 网表                                        |
|                                                                     |
|  Step 3: 工艺映射（Technology Mapping）                               |
|    +-- 将逻辑映射到目标工艺库单元                                      |
|    +-- 时序驱动的面积/功耗优化                                        |
|    +-- 输出：门级网表（.v + .db）                                     |
|                                                                     |
|  Step 4: 综合后优化（Post-synthesis Optimization）                    |
|    +-- 时序关键路径的 Buffer 插入/单元升级                             |
|    +-- 面积恢复（非关键路径用最小单元）                                |
|    +-- 输出：综合后门级网表 (+ 时序报告)                               |
|                                                                     |
|  Output: 综合网表 (.v) + 时序约束 (.sdc) + 时序报告 + 面积报告 + 功耗报告 |
+---------------------------------------------------------------------+
```

### 2.2 综合策略选择

| 策略 | 适用场景 | 优点 | 缺点 |
|:-----|:---------|:-----|:------|
| **自顶向下** | <5M gates, 单时钟域 | 一次性全局优化 | 容量限制 |
| **自底向上** | >5M gates, 多时钟域 | 分块并行，可扩展 | 边界时序协调复杂 |
| **层次化综合** | 层次化设计 | 保留 RTL 层次 | 跨层次优化有限 |
| **物理综合** | >10M gates, 深亚微米 | 物理布局指导综合 | 运行时间长 |

**推荐策略（BMC SoC 级别 <5M gates）**：

```text
自顶向下综合 -> 如果时序收敛困难 -> 切换为物理综合
```

### 2.3 综合脚本模板

```tcl
# ============================================================
# Synthesis Script for BMC SoC
# Tool: Synopsys Design Compiler
# Process: 28nm
# ============================================================

# -- 1. 设置工艺库 --
set target_library  "tcbn28hpcplus.db"
set link_library    "* $target_library dw_foundation.sldb"
set symbol_library  "tcbn28hpcplus.sdb"
set search_path     "$search_path ./rtl ./ip_repo"

# -- 2. 读取 RTL --
analyze -format verilog { \
    ./rtl/soc_top.v \
    ./rtl/cpu_subsystem.v \
    ./rtl/axi_crossbar.v \
    ./rtl/apb_bridge.v \
    ./rtl/uart.v \
    ./rtl/i2c_master.v \
    ./rtl/ddr_ctrl.v \
    ./rtl/npu_core.v \
    ./rtl/vic.v \
    ./rtl/wdt.v \
    ./rtl/timer.v \
    ./rtl/otp_ctrl.v \
}

elaborate soc_top
current_design soc_top

# -- 3. 时序约束 --
source ./constraints/soc_top.sdc

# -- 4. 设置综合选项 --
set_optimize_registers true
set_fix_multiple_port_nets -all -buffer_constants
set_auto_disable_drc_verbose true
set_compile_dont_touch_netlist true

set_ultra_optimization -force
set_compile_seqmap_propagate_constants true

# -- 5. 执行综合 --
compile_ultra -no_autoungroup -area_high_effort_script

# -- 6. 输出 --
write -format verilog -output ./output/soc_top_synth.v
write_sdc -output ./output/soc_top_synth.sdc
write_sdf -version 2.1 -output ./output/soc_top_synth.sdf

report_timing -nworst 10 -path full > ./output/timing.rpt
report_area -hierarchy > ./output/area.rpt
report_power > ./output/power.rpt
report_qor > ./output/qor.rpt
```

---

## 3️⃣ 时序约束方法论

### 3.1 时序约束体系

时序约束是 L4 的核心技能，必须系统化管理：

| 约束类型 | SDC 命令 | 用途 |
|:---------|:---------|:-----|
| **时钟定义** | create_clock / create_generated_clock | 定义时钟源和派生时钟 |
| **时钟特性** | set_clock_latency / set_clock_uncertainty / set_clock_transition | 时钟偏移和抖动 |
| **IO 约束** | set_input_delay / set_output_delay | 外部时序接口 |
| **假路径** | set_false_path | 功能上不关心的路径 |
| **多周期** | set_multicycle_path | 慢于 1 时钟周期的路径 |
| **例外路径** | set_max_delay / set_min_delay | 特殊时序要求 |
| **过渡时间** | set_input_transition / set_load | IO 端口特性 |

### 3.2 时钟定义规范

```tcl
# -- 输入时钟 --
create_clock -name clk_25m -period 40.000 [get_ports pad_xtal_in]
set_clock_uncertainty -setup 0.200 [get_clocks clk_25m]
set_clock_uncertainty -hold 0.050 [get_clocks clk_25m]

# -- PLL 输出：CPU 时钟 --
create_generated_clock -name clk_cpu \
    -source [get_ports pad_xtal_in] \
    -divide_by 1 -multiply_by 32 \
    [get_pins u_pll/clk_out]
set_clock_transition 0.150 [get_clocks clk_cpu]
set_clock_uncertainty -setup 0.300 [get_clocks clk_cpu]   ;# PLL jitter + margin
set_clock_uncertainty -hold 0.080 [get_clocks clk_cpu]

# -- PLL 输出：总线时钟 --
create_generated_clock -name clk_bus \
    -source [get_ports pad_xtal_in] \
    -divide_by 1 -multiply_by 16 \
    [get_pins u_pll/clk_out_bus]
set_clock_uncertainty -setup 0.250 [get_clocks clk_bus]
set_clock_uncertainty -hold 0.060 [get_clocks clk_bus]

# -- 分频时钟：外设时钟 --
create_generated_clock -name clk_per \
    -source [get_clocks clk_bus] \
    -divide_by 4 \
    [get_pins u_clk_divider/clk_out]
```

### 3.3 I/O 时序约束

```tcl
# -- 输入延迟（外部驱动模型）--
# DDR 输入：数据在时钟上升沿前 1ns 有效
set_input_delay -clock clk_ddr -max 0.800 [all_inputs -filter "name =~ *ddr*"]
set_input_delay -clock clk_ddr -min 0.200 [all_inputs -filter "name =~ *ddr*"]

# UART 输入：异步信号，用最大约束宽松
set_input_delay -clock clk_per -max 5.000 [get_ports pad_uart?_rxd]
set_input_delay -clock clk_per -min 0.500 [get_ports pad_uart?_rxd]

# -- 输出延迟（外部负载模型）--
# DDR 输出：在时钟上升沿后 0.5ns 输出有效
set_output_delay -clock clk_ddr -max 0.500 [all_outputs -filter "name =~ *ddr*"]
set_output_delay -clock clk_ddr -min 0.100 [all_outputs -filter "name =~ *ddr*"]

# GPIO 输出：宽松约束
set_output_delay -clock clk_per -max 3.000 [get_ports pad_gpio_*]
set_output_delay -clock clk_per -min 0.100 [get_ports pad_gpio_*]
```

### 3.4 例外路径约束

```tcl
# -- 假路径：异步 CDC 路径（已在 CDC 设计中保证正确性）--
set_false_path -from [get_clocks clk_cpu] -to [get_clocks clk_ddr]
set_false_path -from [get_clocks clk_ddr] -to [get_clocks clk_cpu]
set_false_path -from [get_clocks clk_bus] -to [get_clocks clk_per]
set_false_path -from [get_clocks clk_per] -to [get_clocks clk_bus]

# -- 假路径：测试模式 --
set_false_path -from [get_ports scan_enable]
set_false_path -to [get_ports scan_out]

# -- 多周期路径：慢速外设 --
set_multicycle_path 2 -setup -from [get_clocks clk_bus] -to [get_clocks clk_per]
set_multicycle_path 1 -hold -from [get_clocks clk_bus] -to [get_clocks clk_per]

# -- 多周期路径：跨时钟域握手 --
set_multicycle_path 3 -setup -from u_sync/handshake_req_reg -to u_sync/handshake_ack_reg
set_multicycle_path 2 -hold -from u_sync/handshake_req_reg -to u_sync/handshake_ack_reg
```

### 3.5 时序报告分析方法

**STA 检查关键指标**：

| 指标 | 含义 | 通过标准 | 警告阈值 |
|:-----|:-----|:---------|:---------|
| **WNS** | 最差负时序裕量 | WNS ≥ 0 | < -50ps |
| **TNS** | 总负时序裕量 | TNS = 0 | > -500ps |
| **FEP** | 失效端点数量 | 0 | > 10 |
| **Slack Hist** | slack 分布 | 集中在正区间 | 大量路径接近 0 |
| **Transition** | 信号上升/下降时间 | < 0.5 × period | > 0.8ns |
| **Capacitance** | 负载电容 | < lib max | 超限 10% |

**时序报告解读示例**：

```text
****************************************
Report : timing
        -path full
        -delay max
        -max_paths 10
****************************************

  Startpoint: u_cpu/inst/core_reg_reg[0]
              (rising edge-triggered flip-flop clocked by clk_cpu)
  Endpoint:   u_npu/cfg_reg_reg[31]
              (rising edge-triggered flip-flop clocked by clk_cpu)
  Path Group: clk_cpu
  Path Type:  max

  Point                                   Incr     Path
  ------------------------------------------------------------
  clock clk_cpu (rise edge)               0.000    0.000
  clock network delay (propagated)        0.350    0.350
  u_cpu/inst/core_reg_reg[0]/CK (SDFF)    0.000    0.350 r
  u_cpu/inst/core_reg_reg[0]/Q (SDFF)     0.452    0.802 r
  u_cpu/inst/npu_cfg_out[31]              1.234    2.036 r
  u_axi_crossbar/m_axi_wdata[31]          0.567    2.603 r
  u_npu/cfg_decoder/data_in[31]           0.345    2.948 r
  u_npu/cfg_reg_reg[31]/D (SDFF)          0.123    3.071 r
                                          -----
  data arrival time                                  3.071

  clock clk_cpu (rise edge)               1.250    1.250
  clock network delay (propagated)        0.350    1.600
  clock uncertainty                       0.300    1.300
  u_npu/cfg_reg_reg[31]/CK (SDFF)         0.000    1.300 r
  library setup time                     -0.080    1.220
                                          -----
  data required time                                 1.220
  ------------------------------------------------------------
  data required time                                 1.220
  data arrival time                                 -3.071
                                          -----
  slack (VIOLATED)                                  -1.851
```

**时序违规分析步骤**：

```text
步骤 1：读取 WNS/TNS/FEP -> 确认违规严重程度
步骤 2：检查违规路径 -> 追踪数据路径延迟分布
步骤 3：识别瓶颈段 -> 哪一段逻辑延迟最大？
  +-- Cell delay vs Net delay 占比？
  +-- 逻辑级数（Logic Level）？
步骤 4：选择优化策略：
  +-- Cell delay 高 -> 升级单元（VT swap / 大驱动）
  +-- Net delay 高 -> 位置优化 / 插 buffer
  +-- Logic Level 高 -> RTL 级重设计（流水线加入）
步骤 5：重新综合 -> 检查改善效果
步骤 6：若多次迭代无法收敛 -> 返回 L5 或 L6 调整
```

---

## 4️⃣ 逻辑综合优化技术

### 4.1 面积/时序/功耗优化选项

| 优化选项 | DC 命令 | 效果 | 代价 |
|:---------|:--------|:-----|:-----|
| **自动 Ungroup** | set_ungroup | 跨层次优化，减少面积 | 调试困难 |
| **寄存器重定时** | set_optimize_registers | 平衡流水线级延迟 | 寄存器数量增加 |
| **VT swap** | set_max_fanout / set_min_library | 非关键路径用低功耗单元 | 时序弱化 |
| **Datapath 优化** | set_register_merging | 共享运算逻辑 | 面积减少 5-15% |
| **Boundary 优化** | set_boundary_optimization | 跨模块端口优化 | 改变接口时序 |
| **Retiming** | set_retime | 自动平衡寄存器位置 | 验证困难 |

### 4.2 不同目标的综合策略

```tcl
# -- 策略 1：时序优先（用于高频模块）--
compile_ultra -no_autoungroup -timing_high_effort_script
set_max_area 0
禁止 VT swap 到低功耗单元

# -- 策略 2：面积优先（用于低速控制逻辑）--
compile_ultra -no_autoungroup -area_high_effort_script
允许自动 ungroup 合并小模块
使用最密集的库单元

# -- 策略 3：功耗优先（用于待机保持域）--
compile_ultra -no_autoungroup -power_high_effort_script
启用 Clock Gating（自动推断）
选择低功耗库单元
```

### 4.3 综合后网表质量检查

| 检查项 | 检查方法 | 合格标准 |
|:-------|:---------|:---------|
| 组合逻辑级数 | report_timing 中的 logic level | 关键路径 ≤ 20 级 |
| 扇出分布 | report_fanout | 最大扇出 ≤ 32 |
| 扇入分布 | — | 无异常高扇入 |
| 时钟门控推断 | report_clock_gating | 可门控寄存器门控率 ≥ 80% |
| 面积分布 | report_area -hierarchy | 各模块面积与估算一致 |
| 功耗分布 | report_power | 动态/静态占比合理 |
| Buf/Inv 比例 | report_cell | 缓冲器面积比 ≤ 10% |
| 无用逻辑 | report_unused_logic | 0 无用逻辑 |

---

## 5️⃣ DFT 插入与测试逻辑

### 5.1 DFT 策略全景

| DFT 类型 | 覆盖率目标 | 面积开销 | 测试时间 | 适用场景 |
|:---------|:----------:|:--------:|:--------:|:---------|
| **Full Scan** | 95%+ 可测结构故障 | 10-15% | 中等 | 所有 SoC |
| **Partial Scan** | 80-90% | 5-8% | 短 | 面积受限设计 |
| **MBIST** | 90%+ 内存故障 | 1-3% | 短 | 含 SRAM 的设计 |
| **Logic BIST** | 85-90% | 5-10% | 长 | 安全关键设计 |
| **Boundary Scan (JTAG)** | — | 2-5%（封装引脚） | 短 | 板级测试 |
| **At-Speed Scan** | 与 Full Scan 同 | 额外时钟控制 | 中等 | 高速时序检测 |

### 5.2 Scan 插入流程

```tcl
# -- DFT 配置（Synopsys DFT Compiler）--
set_scan_configuration -style multiplexed_flip_flop
set_scan_configuration -chain_count 8                    ;# 8 条 scan chain
set_scan_configuration -clock_mixing mix_clocks           ;# 混合时钟域
set_scan_configuration -hierarchical_clock_domain true

# -- 定义测试端口 --
create_port -direction in  test_mode
create_port -direction in  scan_enable
create_port -direction in  scan_in[0:7]
create_port -direction out scan_out[0:7]

# -- 指定 test mode 约束 --
set_dft_signal -view spec -type ScanClock -port [get_ports pad_dft_clk] -timing {45 55}
set_dft_signal -view spec -type TestMode -port [get_ports pad_test_mode] -active_state 1

# -- 插入 Scan --
insert_dft
```

### 5.3 MBIST 集成

| 内存类型 | 大小 | MBIST 控制器 | 测试算法 | 测试时间 |
|:---------|:----:|:-------------|:---------|:---------|
| L1 Cache | 32KB×2 | BIST_Cache | March C- | 5ms |
| L2 Cache | 256KB | BIST_L2 | March C- + Checkerboard | 20ms |
| NPU SRAM | 512KB | BIST_NPU | March 13N | 40ms |
| Boot ROM | 64KB | BIST_Boot | March C- | 3ms |
| Internal SRAM | 64KB | BIST_SRAM | March C- | 5ms |

### 5.4 测试覆盖率目标

```text
+---------------------------------------------------------------------+
|                    测试覆盖率签核标准                                 |
|                                                                     |
|  测试类型         | 目标       | 警告            | 不可接受          |
|  -----------------+-----------+-----------------+------------------ |
|  Stuck-at Fault   | ≥ 98%     | 95-98%          | < 95%            |
|  Transition Fault | ≥ 92%     | 85-92%          | < 85%            |
|  MBIST            | ≥ 95%     | 90-95%          | < 90%            |
|  IDDQ             | 可测      | —               | 不可测            |
|                                                                     |
+---------------------------------------------------------------------+
```

---

## 6️⃣ 布局规划与电源网络

### 6.1 芯片布局规划方法

```text
+---------------------------------------------------------------------+
|                    SoC 芯片布局规划（示例）                             |
|                                                                     |
|  +----------------------------------------------------------+       |
|  |                         PAD RING                         |       |
|  +-------------+--------------------------+-----------------+       |
|  |             |                          |                 |       |
|  |   的 PLL    |      CPU 子系统           |   DDR PHY       |       |
|  |    区域    |    (L1+L2+SCU)           |   (DDR3-1600    |       |
|  |             |    Area: ~3.5mm²         |    32bit ×2)   |       |
|  |             |                          |   Area: 2.0mm²  |       |
|  +-------------+-----------+--------------+-----------------+       |
|  |             |           |              |                 |       |
|  |    PCIe     |   AXI     |  NPU 子系统   |   ETH PHY      |       |
|  |    PHY      |   Cross-  |  (MAC阵列+    |   (2×GbE)     |       |
|  |    (Gen3    |   bar     |   SRAM)      |   Area: 0.8mm² |       |
|  |    ×4)     |   Area:   |  Area: 4.2mm² |                 |       |
|  |    Area:   |   0.5mm²  |              |                 |       |
|  |    1.2mm²  |           |              |                 |       |
|  +-------------+-----------+--------------+-----------------+       |
|  |               APB 外设域 (UART/I2C/SPI/GPIO/Timer)        |       |
|  |               Area: ~0.8mm² (合并放置)                     |       |
|  +-------------------------+--------------------------------+       |
|  |      安全处理器          |       OTP/eFuse               |       |
|  |      + 加密引擎          |       + TRNG                  |       |
|  |      Area: 0.6mm²       |       Area: 0.3mm²            |       |
|  +-------------------------+--------------------------------+       |
|  |                    JTAG + Debug                          |       |
|  +----------------------------------------------------------+       |
|                                                                     |
|  Total Die Area: ~16mm² @ 28nm                                      |
+---------------------------------------------------------------------+
```

### 6.2 布局规划关键规则

| 规则 | 说明 | 违反后果 |
|:-----|:------|:---------|
| **IP 近端排列** | 高速互联的 IP 物理上靠近 | 长连线延迟 + 布线拥塞 |
| **PAD 对齐** | 高扇出信号 PAD 接近对应 IP | 片外走线过长 |
| **电源密度** | 高功耗 IP 周围留够电源 via 空间 | IR drop 大 |
| **时钟区域集中** | PLL 靠近芯片中央，时钟树对称 | 时钟 skew 大 |
| **模拟隔离** | PHY/PLL 与数字区域有隔离带 | 噪声耦合 |
| **散热考虑** | 热源 IP 分散放置（避免热斑） | 局部过热影响良率 |

### 6.3 电源网络设计

**电源网络设计参数**：

| 参数 | BMC SoC @28nm | 高性能 SoC @7nm | 说明 |
|:-----|:--------------|:----------------|:-----|
| VDD Core | 1.0V | 0.8V | 内核电压 |
| 电流密度 | < 2A/mm² | < 1.5A/mm² | 与工艺相关 |
| 最大 IR Drop | < 5% VDD | < 3% VDD | 含动态+静态 |
| 电源 strap 间距 | 50-100μm | 30-50μm | 顶层金属 |
| 去耦电容 | 填充 20% 空闲面积 | 填充 30% 空闲面积 | 片上 decap |

**IR Drop 分析标准**：

```text
静态 IR Drop: < 3% VDD（稳态）
动态 IR Drop: < 5% VDD（切换瞬态）
VDD 降额:    满足以上两条后 - (0~3%) 综合时序余量

IR Drop 热点排查：
  1. 高活动因子模块（NPU 阵列切换）
  2. 供电网络瓶颈（窄 strap 区）
  3. 远离电源 PAD 的区域
```

---

## 7️⃣ 布局布线方法

### 7.1 布局阶段

| 布局阶段 | 活动 | 输出 | 检查点 |
|:---------|:-----|:-----|:-------|
| **全局布局** | 所有标准单元粗放放置 | 初始单元位置 | 无大量单元重叠 |
| **合法化** | 解决单元重叠，对齐到 row | 合法化布局 | 所有单元在 row 内 |
| **时钟树综合** | H-Tree / 平衡时钟分布 | 时钟网络 | 时钟 skew < 5% period |
| **详细布局** | 时序驱动的单元精确放置 | 最终布局 | 所有 path 正 slack |
| **Post-Place 优化** | 时序关键路径的单元调整 | 优化后布局 | 满足时序目标 |

### 7.2 时钟树综合（CTS）策略

| 时钟域 | 目标 skew | 目标 latency | 树类型 | Buffer 类型 |
|:-------|:---------:|:------------:|:-------|:-----------|
| CLK_CPU | < 100ps | < 500ps | H-Tree | CKBUF ×8/×16 |
| CLK_BUS | < 150ps | < 600ps | 平衡树 | CKBUF ×4/×8 |
| CLK_PER | < 200ps | < 800ps | 自动平衡 | CKBUF ×4 |
| CLK_DDR | < 50ps | < 300ps | 手动 H-Tree | CKBUF ×16 |

**CTS 质量指标**：

```text
Clock Skew: max(CLK_i) - min(CLK_i)
Clock Latency: CLK source -> register CK pin 的传播延迟
Transition: 时钟边沿的上升/下降时间

合格标准：
  - 全局 skew < 5% of period
  - 本地 skew（相邻寄存器）< 3% of period
  - Latency: 根据 PLL->register 距离合理
  - Transition: 满足库约束最大值
```

### 7.3 布线阶段

| 布线阶段 | 活动 | 输出 | 检查点 |
|:---------|:-----|:-----|:-------|
| **全局布线** | 粗略分配布线资源 | 布线拥塞图 | 无不可布通区域 |
| **详细布线** | 精确走线 | 完整布线 | DRC 零违规 |
| **布线后优化** | 时序/SI 驱动优化 | 最终布线 | SI clean |

**布线拥塞管理**：

```text
拥塞等级与处理：

< 90% 利用率：自动布线即可
90-95%：手动干预（宽线减窄 / 增加布线 layer）
95-105%：严重拥塞 -> 返回布局阶段调 IP 位置
> 105%：不可布通 -> 返回架构阶段减布线资源消耗

拥塞热点常见位置：
  1. 多个高速 IP 接口汇聚区域（如 AXI 交叉开关）
  2. 密集的 I/O 引脚区
  3. SRAM 周边（地址/数据线密集扇出）
```

---

## 8️⃣ PPA 优化与收敛

### 8.1 PPA 收敛流程

```text
PPA 收敛是 L4 的核心目标，通常需要 3-5 轮迭代：

第一轮：综合后 PPA（误差 ±15%）
  +-- 目标：确认 PPA 在目标边界内，识别瓶颈
  +-- 动作：如果超出边界，返回 L5 或 L6 调整

第二轮：布局后 PPA（误差 ±10%）
  +-- 目标：时序初步可达，面积可控
  +-- 动作：调整 floorplan 或综合策略

第三轮：CTS 后 PPA（误差 ±5%）
  +-- 目标：时序完全闭合，功耗满足 TDP
  +-- 动作：微调时钟门控/单元 VT

第四轮：布线后 PPA（误差 ±2%）
  +-- 目标：签核级 PPA 确认
  +-- 动作：布线后微调（若仍有违规）

最终：签核 PPA
  +-- 所有 corner 满足：WNS≥0, TNS=0, Power<TDP, Area<Budget
```

### 8.2 各维度优化技术汇总

**时序优化**：

| 技术 | 适用场景 | 效果 | 代价 |
|:-----|:---------|:-----|:-----|
| 单元升级（VT swap） | 关键路径 cell delay 高 | -5~15% 延迟 | 功耗 +10~30% |
| 缓冲器插入 | 长连线 net delay 高 | -10~30% 延迟 | 面积 +3~8% |
| 逻辑重组 | 逻辑级数过高 | -10~25% 延迟 | 面积可增可减 |
| 寄存器重定时 | 流水线不平衡 | -10~20% 延迟 | 寄存器数 +5~15% |
| 简化逻辑 | 组合逻辑过于复杂 | -5~20% 延迟 | 功能精度可能降低 |

**功耗优化**：

| 技术 | 适用场景 | 功耗节省 | 时序/面积影响 |
|:-----|:---------|:---------|:--------------|
| 时钟门控 | 低活动因子寄存器 | 30-50% 动态功耗 | 微增面积 |
| 数据门控 | 数据路径切换无效 | 10-20% 动态功耗 | 微增逻辑 |
| VT swap（低功耗） | 非关键路径 | 30-50% 漏电 | 时序弱化 |
| 电源门控 | 长期空闲模块 | 几乎 100% 静态功耗 | 15-20% 面积 |
| 动态频率缩放 | 不需要满频时 | 与频率平方成正比 | 需要 PMU 支持 |
| 电压缩放 | 不需要满压时 | 与电压平方成正比 | 需要电压调节器 |
| 状态编码 | FSM 切换频繁 | 10-30% FSM 功耗 | 无 |

**面积优化**：

| 技术 | 适用场景 | 面积节省 | 影响 |
|:-----|:---------|:---------|:------|
| 共享 Datapath | 多个相似运算 | 10-30% 面积 | 可能增延迟 |
| 取消冗余逻辑 | 综合未优化的情况 | 5-15% 面积 | 无 |
| 合并小状态机 | 多个小 FSM | 10-20% FSM 面积 | 增大组合逻辑 |
| SRAM 替换寄存器堆 | 大容量存储 | 50-80% 面积 | 需要时钟周期访问 |

### 8.3 PPA 收敛条件

| 指标 | 目标 | 警告 | 不可接受 |
|:-----|:----:|:----:|:--------:|
| WNS（最差负裕量） | > 0ps | 0 ~ -50ps | < -50ps |
| TNS（总负裕量） | 0ps² | < 500ps² | > 500ps² |
| 动态功耗 | ≤ TDP × 0.85 | TDP × 0.85 ~ × 1.0 | > TDP |
| 静态功耗 | ≤ TDP_Static × 0.9 | — | > TDP_Static |
| Die 面积 | ≤ Budget | Budget ~ × 1.05 | > × 1.05 |
| 时钟 skew | ≤ 5% period | 5~8% | > 8% |
| 过渡时间 | ≤ 0.5 × period | 0.5~0.8 × period | > 0.8 × period |
| IR Drop | ≤ 5% VDD | 5~8% | > 8% |

---

## 9️⃣ 签核与时序收敛

### 9.1 签核分析维度

| 分析类型 | 工具 | 覆盖 corner | 目的 |
|:---------|:-----|:------------|:-----|
| **STA（静态时序分析）** | Primetime | BC/WC/WCL/ML | 时序签核 |
| **功耗分析** | Primetime PX | TYP/WC | 功耗签核 |
| **IR Drop 分析** | RedHawk | WC | 电压降签核 |
| **电迁移分析** | RedHawk/Voltus | WC | 可靠性签核 |
| **信号完整性** | Primetime SI | WC | 串扰检查 |
| **DRC/LVS（物理验证）** | Calibre/ICV | — | 物理规则签核 |
| **DFM（可制造性）** | Calibre DFM | — | 制造良率优化 |

### 9.2 多 Corner 时序收敛

**标准 corner 矩阵**：

| Corner | 电压 | 温度 | 工艺 | 时序类型 | 用途 |
|:-------|:----:|:----:|:----:|:---------|:-----|
| BC（Best Case） | 1.05× | -40°C | Fast | Hold | 建立时间检查（最快） |
| WC（Worst Case） | 0.95× | 125°C | Slow | Setup | 保持时间检查（最慢） |
| WCL | 1.05× | -40°C | Slow | Setup | 低温慢工艺 setup |
| ML | 0.90× | 125°C | Slow | Setup | 低电压最差 setup |

**收敛策略**：

```text
Setup 违规（setup violation）：
  -> 频率降低（不改变 RTL）
  -> 升级库单元（大驱动/低 VT）
  -> 加流水线阶段（改 RTL）
  -> 返回 L5 改架构

Hold 违规（hold violation）：
  -> 插入 hold buffer（最常用）
  -> 数据路径 delay 调整
  -> 通常不在高频下有问题
```

### 9.3 签核准出条件

```text
签核前必须满足的全部条件：

□ 所有 corner 下的 STA 零违规（WNS ≥ 0, TNS = 0）
□ 功耗分析确认动态+静态 ≤ TDP × 1.05
□ IR Drop 分析最差点 < 5% VDD
□ 电迁移检查无违规
□ SI 检查无串扰违规（noise margin 满足）
□ DRC/LVS 零违规
□ DFM 规则全部满足
□ 测试覆盖率满足签核标准（FA ≥ 98%, TA ≥ 92%, MBIST ≥ 95%）
□ 所有约束文件（.sdc / .upf）与实现一致
□ 最终网表交付 L3 做后仿真
```

---

## 🔟 常见实现失败模式

### 10.1 失败模式汇总

| # | 模式 | 症状 | 根因 | 阶段发现 | 修复方式 |
|:-:|:-----|:-----|:-----|:--------:|:---------|
| P1 | **时序无法收敛** | 多次综合后仍有 setup 违规 | 目标频率过高 / 逻辑级数过多 | STA | 降频 / 改 RTL（流水线） |
| P2 | **功耗超出 TDP** | 功耗报告 > TDP | 活动因子估计偏低 / 架构预留不足 | 功耗分析 | 门控增强 / 降电压 / 降频 |
| P3 | **布线拥塞无法布通** | 布线拥塞 > 105% | 布线资源不足 / IP 挤在一起 | 布线 | 改 floorplan / 增布线 layer |
| P4 | **IR Drop 过大** | 动态 IR > 8% VDD | 电源网络不足 / 峰值电流过大 | IR 分析 | 增电源 strap / 去耦 |
| P5 | **时钟 skew 过大** | skew > 8% period | 时钟树不平衡 / 工艺偏差 | CTS | 手动调整时钟树 |
| P6 | **面积超出预算** | 面积 > 目标 × 1.05 | 架构估算偏差 / SRAM 过多 | 布局 | 返回 L6 减规格 |

### 10.2 典型案例：时序收敛失败

```text
情景：CPU 目标频率 1GHz（周期 1ns），但最差 corner 仅能到 800MHz

失败路径分析：
  CPU 唤醒到 L2 Cache 的路径逻辑级数 = 30 级
  第 1 轮综合：WNS = -350ps（只能到 650MHz）
  第 2 轮：升级关键路径 VT -> WNS = -200ps（可到 800MHz）
  第 3 轮：增加流水线寄存器 -> RTL 变更 -> WNS = +50ps ✓

教训：
  . 综合优化的上限由 RTL 架构决定（不能全靠工具）
  . 逻辑级数 > 25 时应该考虑增加流水线
  . 最高频率应该在架构阶段就做可行性分析
```

---

## 1️⃣1️⃣ 产出物与检查清单

### 11.1 L4 产出物清单

| # | 产出物 | 格式 | 内容 | 用途 |
|:-:|:-------|:-----|:-----|:-----|
| 1 | **综合网表** | Verilog | 门级网表（含 DFT） | 后仿真 |
| 2 | **时序约束** | SDC | 完整时序约束（综合后版） | STA 和后端 |
| 3 | **SDF** | SDF | 标准延迟格式（反标用） | 后仿真 |
| 4 | **STA 报告** | Rpt | 所有 corner 时序报告 | 签核证据 |
| 5 | **功耗报告** | Rpt | 动态+静态功耗分析 | 签核证据 |
| 6 | **面积报告** | Rpt | 各模块面积分布 | 签核证据 |
| 7 | **测试向量** | STIL/WGL | ATPG 向量 | ATE 测试 |
| 8 | **签核检查清单** | Checklist | 签核条件确认 | 项目里程碑 |
| 9 | **ECO 指引** | TCL | 如需 ECO 的指导步骤 | 后验证修复 |

### 11.2 L4 检查清单

- [ ] 综合完成，无 DRC/LINT 违规？
- [ ] STA 所有 corner 通过（WNS≥0, TNS=0）？
- [ ] 功耗 ≤ TDP？
- [ ] 面积 ≤ Budget？
- [ ] DFT 覆盖率达标（FA≥98%, TA≥92%）？
- [ ] MBIST 覆盖所有 SRAM？
- [ ] IR Drop < 5% VDD？
- [ ] 电迁移无违规？
- [ ] SI 无串扰违规？
- [ ] 布线拥塞 < 95%？
- [ ] 时钟 skew < 5% period？
- [ ] 后仿真验证通过？
- [ ] 网表交付至 L3（验证团队）？

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- (无)

### 外部资料引用

- (无)

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-21 | v1.0 | 初版发布，从 chip-system-design-methodology.md §2 六层抽象金字塔 L4 展开 |
