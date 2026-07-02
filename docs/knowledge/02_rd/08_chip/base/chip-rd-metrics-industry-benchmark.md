# 📏 芯片研发全流程指标参数与业界基准

> **版本**: v1.0 | **创建**: 2026-07-01
> **定位**: 覆盖芯片研发全生命周期各阶段的关键指标参数(Key Metrics)，提供业界最佳值(Best-in-Class, BIC)与行业均值(Typical)，作为产品规格定义、研发进度评估、竞品对标、缺陷定位的定量参考
>
> **数据说明**: 本文所有量化数据以 **N7/N5 先进制程**为主要参考节点（2024-2026），老工艺和特殊工艺单独标注。BIC = 行业领先企业(Samsung/TSMC/Intel/NVIDIA/Qualcomm/AMD等)在同类产品中可达到的顶级水平，Typical = 行业中位数/普遍水平
>
> **关联文档**:
> - [🏭 芯片全生命周期与基础科学体系](chip-full-lifecycle-overview.md) — 10 阶段通用流程
> - [📊 芯片良率·SPC·BER·Weibull 可靠性统计体系](chip-yield-reliability-statistical-models.md) — 8 章统计模型
> - [🔬 芯片测试全栈深度分析](../test/chip-test-full-stack-deep-analysis.md) — 13 章测试体系
> - [🏭 四大芯片类型研发全流程](chip-four-categories-rd-process.md) — CPU/DRAM/GPU/存储
> - [🪶 CPU vs GPU EDA 哲学](chip-cpu-vs-gpu-eda-philosophy.md) — 验证×物理瓶颈对比

---

## 📑 目录

1. [总览：全流程指标参数地图](#1-总览全流程指标参数地图)
2. [架构定义阶段](#2-架构定义阶段)
3. [RTL 设计与微架构阶段](#3-rtl-设计与微架构阶段)
4. [功能验证阶段](#4-功能验证阶段)
5. [逻辑综合与 DFT 阶段](#5-逻辑综合与-dft-阶段)
6. [物理设计（后端）阶段](#6-物理设计后端阶段)
7. [物理验证与 Tape-out 阶段](#7-物理验证与-tape-out-阶段)
8. [晶圆制造阶段](#8-晶圆制造阶段)
9. [晶圆测试（CP）阶段](#9-晶圆测试cp阶段)
10. [封装阶段](#10-封装阶段)
11. [终测（FT）阶段](#11-终测ft阶段)
12. [可靠性认证阶段](#12-可靠性认证阶段)
13. [系统级验证与生态认证阶段](#13-系统级验证与生态认证阶段)
14. [量产爬坡与成本阶段](#14-量产爬坡与成本阶段)
15. [跨领域综合指标](#15-跨领域综合指标)
16. [参考文献与数据来源](#16-参考文献与数据来源)

---

## 1. 总览：全流程指标参数地图

### 1.1 阶段×指标类型矩阵

| 阶段 | 性能指标 | 质量指标 | 效率指标 | 成本指标 |
|:----|:---------|:---------|:---------|:---------|
| **架构定义** | IPC / Fmax / BW / TOPS | — | 人月 / 迭代次数 | 目标 Die Size |
| **RTL 设计** | Freq target / Gate count | RTL Lint 违规 | 产率 (lines/man-day) | 工时预算偏差 |
| **功能验证** | Coverage % / Emu cycles | Bug rate / Escape rate | 验证人月 / Bug 发现率 | 仿真许可证利用率 |
| **逻辑综合** | WNS / TNS / Area | 综合 DRC / LEC pass | 综合运行时间 | Cell library cost |
| **物理设计** | Util% / Skew / IR drop | DRC count / Antenna | Place 密度 / 迭代次数 | EDA 许可证小时数 |
| **物理验证** | DRC/LVS clean | Waiver 率 | 验证运行轮次 | Signoff 工具成本 |
| **晶圆制造** | D0 / CD uniformity | Yield (LY/DY/FY) | Cycle time / OEE | Cost per wafer |
| **晶圆测试** | CP yield / Bin Pareto | Test coverage % | Test time / die | Probe card 寿命 |
| **封装** | Warpage / R_th | Assembly yield | UPH | Substrate cost |
| **终测** | FT yield / Speed bin | DPPM / Cpk | Test time / unit | Handler 产能 |
| **可靠性认证** | FIT / MTBF | HTOL/ELFR pass rate | Qualification 周期 | 样本量/成本 |
| **系统验证** | Compliance pass rate | Interop 覆盖率 | Bring-up 天数 | 验证板成本 |
| **量产爬坡** | HVM yield | Defect Pareto | Yield ramp rate | Cost per die |

### 1.2 制程节点关键参数（数据来源：TSMC/Samsung 公开数据 + 行业报告）

| 参数 | N28 (28nm) | N16 (16nm) | N7 (7nm) | N5 (5nm) | N3 (3nm) | 单位 |
|:----|:----------:|:----------:|:---------:|:---------:|:---------:|:-----|
| 标准单元高度(Cell H) | 0.9 | 0.66 | 0.48 | 0.33 | ~0.27 | μm |
| M1 金属间距 | 80 | 64 | 40 | 28 | 23 | nm |
| 标称 Vdd | 0.85-1.1 | 0.75-1.0 | 0.7-0.9 | 0.65-0.85 | 0.6-0.8 | V |
| 逻辑密度增益(每代) | — | ~1.5× | ~1.6× | ~1.3× | ~1.2× | 倍 |
| 电气缺陷密度(D0,成熟期) | <0.05 | <0.05 | <0.05 | <0.1 | <0.2 | def/cm² |
| 晶体管单价拐点 | — | 停止下降 | 开始上升 | 显著上升 | 继续上升 | $/transistor |
| 掩模版层数 | 40-50 | 60-70 | 70-80 | 80-90 | 90-100+ | 层 |
| 掩模成本 | $0.5-0.8M | $1-2M | $3-5M | $5-8M | $8-12M | 套 |

> **趋势**: N5 之后单位晶体管成本不再下降，N3 的门电路成本比 N5 高约 5-10%。先进封装（2.5D/3D) 和 chiplet 设计成为延续密度增益的核心手段。

---

## 2. 架构定义阶段

### 2.1 核心架构指标

| 指标 | 定义 | BIC | Typical | 说明 |
|:----|:-----|:----|:--------|:-----|
| **IPC (Instructions Per Cycle)** | 每时钟周期执行指令数 | 2.5-3.5 (OoO CPU) | 1.0-1.5 (in-order) | SPECint2017 加权；受应用类型影响极大 |
| **Fmax (Target)** | 设计的逻辑极限频率 | 3.5-5.0 GHz (CPU) | 1.5-3.0 GHz | N5/N3 先进工艺；GPU:~2.0-2.5 GHz |
| **Fmax (Post-Si)** | 硅后实际最高频率 | 3.0-4.5 GHz | 1.2-2.5 GHz | PVT 角+CCD/IDDQ bin 后 |
| **吞吐率** | 每周期数据处理量 | 4.0-6.0 TFLOPS (GPU N5) | 0.5-2.0 TFLOPS | INT8/FP16/FP32 加权 |
| **TOPS/W** | 每瓦 TOPS | 15-25 (N5 NPU) | 3-10 | 推理 ASIC 指标 |
| **Memory Bandwidth (Peak)** | 最高理论带宽 | 800-1200 GB/s (HBM3) | 50-150 GB/s (DDR5) | 取决于封装/PHY |
| **Die Size Budget** | 目标裸片面积 | 300-400 mm² (GPU) | 50-150 mm² (CPU) | 受 reticle limit 限制~858 mm² |
| **功耗预算 (TDP)** | 热设计功耗 | 300-700 W (GPU) | 65-150 W (CPU) | 数据中心的机械/散热约束 |
| **Power Density** | 单位面积功耗 | 0.5-1.5 W/mm² (GPU) | 0.1-0.5 W/mm² (CPU) | 液冷后可>1.5 W/mm² |
| **PDP (Power-Delay Product)** | 功耗×延迟积 | 取决于架构 | 取决于架构 | 能量效率的综合度量 |

### 2.2 前端总线与 NoC 指标

| 指标 | BIC | Typical | 说明 |
|:----|:----|:--------|:-----|
| NoC 带宽利用率 | 60-75% | 30-50% | 高于 80% 出现显著拥塞 |
| Cache 命中率(L1/L2/L3) | 90/80/95% | 80/60/80% | 取决于应用访问模式 |
| 总线 RTL-to-PHY 延迟 | <1 ns | 1-3 ns | 跨时钟域额外增加 |
| 跨片带宽(Chiplet) | 2-6 TB/s (UCIe) | 0.1-0.5 TB/s | 先进的 3D 封装 |

### 2.3 架构效率指标

| 指标 | 定义 | BIC | Typical |
|:----|:-----|:----|:--------|
| **Utilization efficiency** | 实际吞吐/理论峰值 | 70-85% | 40-60% |
| **Opteron's Law 偏离度** | 实际单线程性能/工艺缩放 | ±15% | ±30% |
| **Roofline Model 瓶颈** | 计算 vs 带宽受限 | 均衡设计 | 多数带宽受限 |
| **Amdahl 可并行度** | 加速比倒数 | >95% 可并行 | 70-85% |

### 2.4 架构团队效率

| 指标 | BIC | Typical | 说明 |
|:----|:----|:--------|:-----|
| 架构探索模型构建周期 | 2-4 周 | 4-8 周 | C++/SystemC TLM 模型 |
| 架构迭代轮次(到 Freeze) | 3-5 轮 | 5-10 轮 | 多次 freeze-rescope 循环 |
| 架构文档完整性 | 95%+ 接口已定义 | 70-80% | 未定义接口在 RTL 阶段变更代价~3-5× |
| 架构→RTL 交付延迟 | <2 周 | 1-3 月 | 从 arch freeze 到 RTL kick-off |

---

## 3. RTL 设计与微架构阶段

### 3.1 设计复杂度指标

| 指标 | 定义 | BIC | Typical | 说明 |
|:----|:-----|:----|:--------|:-----|
| **Gate Count (等效NAND2)** | 逻辑门总数 | 5-20B (GPU/N5) | 0.3-5B (CPU) | GPU 可达 20B+ 晶体管 |
| **Sequential 元素数** | Flip-flop/Latch 总数 | 10-50M | 1-10M | GPU 多于 CPU |
| **标准单元数量** | 综合后 cell 总数 | 50-200M | 5-50M | GPU 的 cell 数可超 1 亿 |
| **SRAM (Total)** | 片上 SRAM 总量 | 100-300 MB (GPU) | 10-50 MB (CPU) | HPC GPU 配 6-40MB L2 + 256-300MB SRAM |
| **Hard Macro 数量** | PHY/serdes/analog IP | 30-100 | 10-30 | 包含 PLL/ADC/DAC |
| **时钟域数量** | 独立时钟域 | 100-500+ | 20-100 | SoC 级复杂性 |
| **电源域数量** | 独立供电域 | 50-200+ | 10-50 | DVFS 和 power gating |
| **RTL 代码行数** | 可综合 Verilog/CHDL | 5-20M (GPU) | 0.5-5M (CPU) | 含 TB 则 2-3× |
| **Module 层级数** | 层次化深度 | 8-15 级 | 4-8 级 | GPU 更深 |

### 3.2 RTL 质量指标

| 指标 | 定义 | BIC | Typical | 说明 |
|:----|:-----|:----|:--------|:-----|
| **Lint 违规密度** | 每千行违规数 | <5 | 20-50 | 0/1/2/3 级分类差 |
| **CDC 违规数** | 跨时钟域同步问题 | 0 (final) | 10-50 | 严重的需手动审查 |
| **RDC 违规数** | 复位域交叉问题 | 0 (final) | 5-20 | 异步复位同步释放 |
| **X-Propagation 违规** | X 态传播问题 | 0 | 10-100 | X-optimism 与 pessimism |
| **RTL Simulation Error Rate** | 仿真与 spec 不一致 | <1% 用例 | 3-8% 用例 | 早期 RTL 阶段较高 |
| **Assertion 密度** | 每模块 assertion 数 | >1 assertion/100 RTL line | 1/1000 line | 公司文化差异大(NVIDIA 很密集) |
| **Synthesis DRC Flag** | 综合阶段 DRC | 3-5 个 waiver | 10-50 | 综合 DRC 反映 RTL quality |

### 3.3 RTL 可预测性指标（与综合后结果偏差）

| 指标 | BIC | Typical | 说明 |
|:----|:----|:--------|:-----|
| RTL→Synthesis 面积偏差 | <5% | 10-20% | RTL 预估面积与实际综合后偏差 |
| RTL → Synthesis 频率偏差 | <3% | 5-10% | RTL 关键路径预估精度 |
| Synthesis → P&R 面积偏差 | <5% | 10-15% | 综合面积 vs 布局布线后 |
| Synthesis → P&R 频率偏差 | <10% | 15-25% | 综合 STA vs 后端 STA |
| **总预测偏差 (RTL→P&R)** | <15% | 25-40% | 加总 All-in；行业性痛点 |

### 3.4 RTL 团队效率

| 指标 | BIC | Typical | 说明 |
|:----|:----|:--------|:-----|
| RTL 工程师产率 | 100-200 lines/day | 30-80 lines/day | 可综合 RTL（不包括 TB） |
| RTL 模块交付周期 | 2-4 周(小模块) | 4-12 周 | 复杂管线/Scheduler 可达 3-6 月 |
| RTL→Frozen (完全收敛) | 3-5 次综合迭代 | 8-15 次 | 大型 GPU 可达 20+ 次 |
| Design Review 通过率(首轮) | >80% | 50-70% | 高通/Apple/NVIDIA 靠严格 review |
| RTL Change Order 频率 | <5/模块/月 | 10-30/模块/月 | 架构不稳定时暴增 |

---

## 4. 功能验证阶段

### 4.1 覆盖率指标

| 指标 | 定义 | Sign-off 标准 | BIC | Typical | 说明 |
|:----|:-----|:------------|:----|:--------|:-----|
| **代码覆盖率 (Line)** | 每行 RTL 被执行 | >95% | >99% | >90% | 未覆盖行须有 waiver |
| **代码覆盖率 (Toggle)** | 每个信号跳变 | >90% | >95% | >80% | tri-state/X 态可能限制 |
| **代码覆盖率 (FSM)** | FSM 状态/转移 | 100% 状态 | 100% | >95% | 不可达状态需 waiver |
| **代码覆盖率 (Branch)** | 条件分支 | >90% | >95% | >80% | 最难达到的代码覆盖类型 |
| **功能覆盖率 (Functional)** | Spec 定义的覆盖点 | 100% bins | >95% bins | >80% bins | UVM covergroup |
| **功能覆盖率 (Assertion)** | 系统 assertion | 100% | >95% | >85% | Formal 验证互补 |
| **交叉覆盖率** | 组合覆盖点 | 自定义 | >90% hit | >70% hit | 组合爆炸需分层 |

### 4.2 验证质量指标

| 指标 | 定义 | BIC | Typical | 说明 |
|:----|:-----|:----|:--------|:-----|
| **Bug 发现率 (每周)** | 每周发现 bug 数 | 峰值 200-500(早期) | 50-150 | 呈倒 U 型曲线 |
| **Bug Escape 率** | 漏到 Si 后的 bug | <0.1 bug/cm² | 0.5-2 bugs/cm² | NVIDIA 第一版 A100 bug <10 |
| **Bug 密度 (最终)** | 单位面积 bug 数 | <0.05/B | 0.1-0.5/B | B=10⁹晶体管 |
| **严重 bug 密度** | P1/P0 bug | <0.01/B | 0.02-0.05/B | 导致功能失效的 bug |
| **测试用例总数量** | 回归测试总量 | 100K-500K+ | 10K-100K | GPU 驱动验证可达百万级 |
| **Code coverage to Bug rate** | 覆盖率达到的 bug 发现 | 95%+ 时 bug 出现率<5% | 85%+ |

### 4.3 验证效率/吞吐指标

| 指标 | BIC | Typical | 说明 |
|:----|:----|:--------|:-----|
| **RTL 仿真速度** | 100-500 kHz | 50-200 kHz | Synopsys VCS/Cadence Xcelium |
| **Gate-level 仿真速度** | 10-50 kHz | 5-20 kHz | 有 SDF 反标时更慢 |
| **Emulation 速度** | 1-50 MHz | 5-10 MHz | Palladium/Zebu/Veloce |
| **Emulation 容量** | 2B gate (单框) | 0.5-1B gate | 多框级联可达 >4B |
| **FPGA 原型速度** | 20-100 MHz | 5-20 MHz | HAPS/Progys. 多片级联 |
| **每日回归运行次数** | 500-2000+ | 100-500 | CI 自动化流水线 |
| **随机测试种子数 (UVM)** | 10K-100K+/night | 1K-10K | 对覆盖率收敛至关重要 |
| **仿真许可证利用率** | >90% | 60-80% | VCS/Questa 按月和池化管理 |

### 4.4 Formal 验证指标

| 指标 | BIC | Typical | 说明 |
|:----|:----|:--------|:-----|
| Formal 可证明 assert 率 | >90% | 50-70% | 剩余用仿真覆盖 |
| Formal 收敛时间 | <1 天(小模块) | 2-7 天 | 大型模块可能需要 bound |
| Bound depth | 10-100 cycle | 5-50 cycle | 超过 bound 用仿真 |
| Sequential equivalence (SEC) | 100% 严格通过 | >95% | 设计变更时的回归工具 |

### 4.5 验证资源配比

| 指标 | BIC (如 NVIDIA) | Typical | 说明 |
|:----|:---------------|:--------|:-----|
| 验证:设计人员比例 | 3-4:1 | 1.5-2:1 | GPU 项目可达 4:1 |
| 验证总人月 / 项目 | 500-2000 PY | 100-500 PY | 大型 GPU ~500-1000 PY |
| 回归集群规模 | 10K-50K+ core | 1K-10K core | 每 24h 回归数百万 test |
| Emulation 占用率 | 90-95% (24/7) | 50-80% | 多项目时分时 |

---

## 5. 逻辑综合与 DFT 阶段

### 5.1 综合质量指标

| 指标 | 定义 | BIC | Typical | 说明 |
|:----|:-----|:----|:--------|:-----|
| **WNS (Worst Negative Slack)** | 最差路径松弛 | 0 ps (meet timing) | -50 to +50 ps | 正松弛=timing 已收敛 |
| **TNS (Total Negative Slack)** | 所有路径总松弛 | 0 ps | 100-1000 ps | 大于 0 需 ECO |
| **WNS after optimization** | OPT 后最差路径 | 0 ps (final) | +20~+50 ps margin | 至少留 10% margin |
| **Hold Violations** | 保持时间违规 | 0 | 数百到数千 | 后端可以修(插入 buffer) |
| **Setup Violations (cells)** | 建立时间违规 cell 数 | 0 | 数百 | 需 ECO 或重新综合 |
| **Cell Area / Gate Count** | 综合后面积 | 设计目标 ±3% | ±5-10% | 面积超规格 = cut features |
| **综合 DRC Violations** | Synopsys DC/Design Compiler DRC | 0 (需 waive 的在 5 个以内) | 10-40 | 主要是 max_cap/max_trans |
| **Leakage Power (综合后)** | 静态功耗估算 | 设计目标 ±5% | ±10-20% | 后端实际值差异大 |
| **Dynamic Power (综合后)** | 动态功耗估算 | 设计目标 ±10% | ±15-30% | 综合估算不够精确 |
| **Sequential Ratio** | 时序 cell 占总面积比 | 15-25% | 20-35% | GPU 更低(NVIDIA:~15%) |

### 5.2 综合瓶颈指标

| 指标 | BIC | Typical | 说明 |
|:----|:----|:--------|:-----|
| 综合运行时间 (large block) | 4-8 小时 | 12-48 小时 | 200M+ cell 设计 |
| 综合内存峰值 | 64-128 GB | 32-64 GB | 200M+ cell 设计 |
| 综合→门级仿真一致性 | >99.9% pass | >98% pass | LEC 检查 |
| Logic Equivalence Check (LEC) | 0 个不等价 | 1-5 个不等价 | Formal 工具验证 |

### 5.3 DFT 指标

| 指标 | 定义 | BIC | Typical | 说明 |
|:----|:-----|:----|:--------|:-----|
| **Scan 覆盖率** | 可测故障覆盖率 | >99% | >97% | ATPG stuck-at |
| **At-speed 覆盖率** | 跨时钟 at-speed 测试 | >90% | >80% | Transition delay 模型 |
| **BIST 覆盖率(Memory)** | SRAM BIST | 100% | >98% | MBIST |
| **测试压缩率** | 压缩比 | 50-100× | 10-30× | X-tolerant/X-compact |
| **Test Power (Shift)** | 扫描链移位功耗 | 工作模式 60% | 工作模式 100-150% | 过高会烧片 |
| **ATE Test Time (CP)** | 晶圆测试时间 | <10s/die | 15-60s/die | 直接影响成本 |
| **ATE Test Time (FT)** | 终测时间 | <5s/device | 10-30s/device | 含 speed bin/sort |
| **Scan Chain 数量** | 并行扫描链 | 100-1000+ | 10-100 | 压缩技术前提下 |
| **Boundary Scan 覆盖** | JTAG/IJTAG | 100% IO | >95% | IEEE 1149.1/1687 |

---

## 6. 物理设计（后端）阶段

### 6.1 布局指标

| 指标 | 定义 | BIC | Typical | 说明 |
|:----|:-----|:----|:--------|:-----|
| **Core Utilization** | 标准单元有效利用率 | 65-75% (CPU) | 55-65% (CPU) | GPU 更高(75-85%) |
| **CPU/GPU 利用率差异** | 控制逻辑 vs 计算阵列 | GPU:~75-85% | CPU:~55-70% | CPU 更多白空间做时钟树/电源 |
| **Blockage 比例** | 软/硬阻挡面积比 | 5-10% | 10-20% | 预留给时钟/电源的区域 |
| **Standard Cell Density** | 局部 cell 密度 | <85% (hotspot) | <70% (avg) | 超过 90% 将路由困难 |
| **Filler Cell 比例** | 填充 cell 占比 | <5% | 5-15% | 短板布局或高利用率 |
| **Pin Access 拥塞** | 标准单元 pin 访问 | <2% tracks full | <5% tracks full | 影响路由通道 |

### 6.2 时钟树 (CTS) 指标

| 指标 | 定义 | BIC | Typical | 说明 |
|:----|:-----|:----|:--------|:-----|
| **Clock Skew (Global)** | 全局时钟偏离 | <20 ps | 30-80 ps | 先进制程 N5 |
| **Clock Skew (Local, H-tree)** | 局部 H-tree 偏离 | <10 ps | 15-30 ps | 同区域同 sub-tree |
| **Clock Latency** | 时钟根到叶延迟 | <300 ps | 300-800 ps | 大芯片+多 sub-tree |
| **Clock Jitter** | PLL 输出抖动 | <2 ps RMS | 3-8 ps RMS | 受电源噪声影响 |
| **Useful Skew 利用率** | 有意 skew 占比 | 50-70% paths | 20-40% paths | 高级 CTS 优化 |
| **时钟 Buffer 数量** | 时钟 tree 总 buffer | 10K-100K | 5K-50K | 大型 GPU 可达百万 |
| **时钟单元功耗占比** | clk cells / total | 15-25% | 20-35% | 动态功耗的大头 |
| **Clock Gating 比例** | 门控时钟占比 | >70% flops | 40-60% flops | 电源优化关键手段 |

### 6.3 布线指标

| 指标 | 定义 | BIC | Typical | 说明 |
|:----|:-----|:----|:--------|:-----|
| **Overflow (GR)** | 全局布线溢出 | <0.5% | 1-3% | 详细布线前预估 |
| **DRC (Final)** | 布线后 DRC 数 | 0 | 0-100 (detail) | 先进节点 sign-off 标准严格 |
| **Short (Final)** | 短路数 | 0 | 0-5 | 任何短路都须修 |
| **Antenna 违规** | 天线效应违规 | 0 | 10-100 | 需插入 antenna diode |
| **Wire Length (Total)** | 布线总长度 | — | 数十 km | 大芯片 >50 km |
| **Via 总数** | via 总量 | — | 数十亿 | N5 级复杂度 |
| **Stacked Via 比例** | 多层覆盖 via | >30% | 10-20% | IR drop/EM 改善 |
| **Min Area Rule Violation** | 最小面积规则违例 | 0 | 0 | 需插入 dummy |

### 6.4 电源完整性指标

| 指标 | 定义 | BIC | Typical | 说明 |
|:----|:-----|:----|:--------|:-----|
| **IR Drop (Static)** | 静态压降 | <1% Vdd | 2-3% Vdd | N5 时 Vdd~0.7-0.8V，1%=7-8mV |
| **IR Drop (Dynamic)** | 动态压降 | <3% Vdd | 5-10% Vdd | di/dt 瞬态电流变化 |
| **dV/dt (noise)** | 电源噪声斜率 | <5 mV/ns | 10-20 mV/ns | 与封装 PDN 耦合 |
| **Electromigration (EM)** | 电流密度安全 | >20% margin | >10% margin | N6+ 铜互连 EM 恶化为关键约束 |
| **Vdd Droop (MLIR)** | 多层 IR-drop | <5% Vdd | 8-12% Vdd | multi-layer 分析 |
| **Current Density (avg)** | 平均电流密度 | <0.5 mA/μm | 0.3-0.8 mA/μm | 顶层(M1-M3)尤需关注 |
| **Power Grid 利用率** | 电源网络利用率 | <40% (安全) | 40-60% | 超过 60% 需加固 |

### 6.5 时序收敛指标

| 指标 | 定义 | BIC | Typical | 说明 |
|:----|:-----|:----|:--------|:-----|
| **Setup Margin (Post-CTS)** | CTS 后建立时间 | >100 ps | 20-80 ps | hold margin 通常在 50ps+ |
| **Hold Margin (Post-route)** | 布线后保持时间 | >50 ps | 10-30 ps | 需给 OCV 留余量 |
| **Setup ECO 轮次** | 时序收敛需要 ECO 次数 | 1-2 次 | 3-6 次 | ECO 不含工程变更单 |
| **Hold Fix Insertion** | 修复 hold 插入 buffer 数 | <1% cells | 1-3% cells | 每个 hold fix 增加功耗 |
| **PVT 收敛角覆盖** | 分析的处理角覆盖 | 100% (6-15 角) | 典型角+SS/TT/FF | 先进制程需要更多角 |
| **Global Variation 预留** | 全局工艺角裕度 | 10-20 ps (N5) | 20-40 ps (N7) | 随工艺微缩变化加大 |

### 6.6 后端团队效率

| 指标 | BIC | Typical | 说明 |
|:----|:----|:--------|:-----|
| Floorplan → Tape-out 周期 | 4-6 月 | 8-14 月 | 含迭代次数 |
| P&R 工程师人均处理门数 | 50-100M gates | 10-30M gates | 含复杂 block |
| GDS 数据最终大小 | 10-100 GB | 1-10 GB | 先进制因多掩模层而膨胀 |
| 后端 License 峰值利用率 | >90% | 50-70% | ICC2/Innovus 按年付 |

---

## 7. 物理验证与 Tape-out 阶段

### 7.1 DRC/LVS 指标

| 指标 | 定义 | Sign-off 标准 | BIC | Typical | 说明 |
|:----|:-----|:------------|:----|:--------|:-----|
| **DRC Total (Final)** | 总设计规则违例 | 0 | 0 | 0-50 (waived) | N5 有数百条 sign-off 规则 |
| **DRC Violation Density** | 违例密度 | — | <1/mm² | 1-10/mm² | 早期阶段参考 |
| **DRC Waiver 率** | 申请 waiver 比例 | 0-5% (非电性) | 5-15% | 必须经 PD 团队严格审查 |
| **LVS (Layout vs. Schematic)** | 版图网表一致性 | Pass | Pass | Pass | 短路/断路/器件不匹配 |
| **LVS Error 数 (Final)** | LVS 错误 | 0 | 0 | 必需完全 clean |
| **ERC (Electrical Rule)** | 电性规则检查 | Pass | Pass | Pass | 浮动节点/驱动强度 |
| **Antenna 合规** | 天线效应 | 100% clean | Clean | Clean | 修复后 CAA 验证 |
| **DFM (Design for Manufacturing)** | 可制造性设计 | All pass | All pass | 含 CMP slot/grain/ligament |

### 7.2 光学邻近修正 (OPC) 指标

| 指标 | BIC | Typical | 说明 |
|:----|:----|:--------|:-----|
| OPC 运行时间 | 12-24 小时 | 24-72 小时 | N5 mask 数据量 TB 级 |
| MRC (Mask Rule Check) | 0 critical | 0-5 | Mask 制造可行性 |
| ILT (Inverse Lithography) 应用 | 关键层使用 | 仅热点 | N3+ 强制 ILT |
| SRAF (Sub-Resolution Assist) | 100% 自动生成 | 手工+自动 | 先进节点自动化率更高 |

### 7.3 Sign-off 时序分析指标

| 指标 | BIC | Typical | 说明 |
|:----|:----|:--------|:-----|
| Sign-off STA 角数 | 18-30 角 | 8-14 角 | N3 增加 |
| Sign-off 运行时间 | 2-8 小时 | 8-24 小时 | PrimeTime/StarRC |
| 参数化片上波动 (POCV) | 全部应用 | 仅 critical path | N7+ 逐渐强制 |
| AOCV 深度 | 10 级 | 5-8 级 | 先进节点要求 10+ |

### 7.4 Tape-out 质量关卡

| 指标 | BIC | Typical | 说明 |
|:----|:----|:--------|:-----|
| 签核检查表通过率 | 100% | >95% | 百项 checklist |
| Tape-out 重做(Re-spin)概率 | <10% | 20-35% | 含全掩模 respin |
| Metal-only ECO 成功率 | >70% | 40-60% | 减少 NRE 成本 |
| Mask 版本数(到量产) | 2-4 版 | 4-8 版 | 含工程变更 |

---

## 8. 晶圆制造阶段

### 8.1 良率指标

| 指标 | 定义 | BIC | Typical | 说明 |
|:----|:-----|:----|:--------|:-----|
| **Line Yield (LY)** | 工序良率 | >99% | 97-99% | 晶圆到晶圆通过率 |
| **Die Yield (DY)** | 裸片良率 | >90% (成熟) | 75-90% | 见良率模型估算 |
| **Final Yield (FY)** | 最终良率=LY×DY | >89% | 70-85% | 影响毛利率 |
| **VBIN (Volume Bin)** | 速度分档良率 | 顶级 bin >30% | 顶级 bin 10-20% | 高频 bin 利润更高 |
| **Defect Density (D0)** | 缺陷密度 | <0.05 def/cm² (成熟) | 0.05-0.2 def/cm² | N5/N7 产线起始 0.2-0.5 |
| **D0 Ramp Rate** | D0 下降速率 | -20%/月(前三月) | -10%/月 | 新产线从高 D0 起步 |
| **Kill Ratio** | 特定层缺陷致死率 | <0.5 | 0.3-0.8 | Via/contact 层最高 |

### 8.2 良率模型参数

| 模型 | 关键参数 | BIC (N7/N5) | Typical | 说明 |
|:----|:---------|:-----------|:--------|:-----|
| Poisson | Y = exp(-AD0) | — | 过低估计 | 先进节点已不准确 |
| **Negative Binomial (NB)** | Y = (1+AD0/α)^(-α) | α=2-4 (N5) | α=1-2 | **最广泛使用** |
| Murphy | Y = [(1-exp(-AD0))/(AD0)]² | — | 接近 NB α=1 | 历史模型 |
| **Williams-Brown** | Y=1/(1+AD0)^k | k≈3.5-4 | k≈2-3 | 混合逻辑+SRAM 适用 |
| **Critical Area Model** | A = f(design density, pitch) | 0.1-0.3 | 0.3-0.7 | 版图特异性 |

### 8.3 工艺参数指标

| 指标 | 定义 | BIC | Typical | 说明 |
|:----|:-----|:----|:--------|:-----|
| **Critical Dimension (CD)** | 关键尺寸 | 目标±1nm (N5) | 目标±2-3nm | 10nm 节点±5% 可能 |
| **CD Uniformity (3σ)** | 片内 CD 均匀性 | <2 nm (N5) | 2-4 nm | 影响速度 bin 分布 |
| **Overlay Accuracy** | 层间对准精度 | <1.5 nm (N5) | 2-4 nm | 多重图案化时更严 |
| **Layer-to-layer Misalign** | 层偏移 | <±0.5 nm | ±1-2 nm | 影响 Vias 电阻 |
| **Film Thickness 均匀性** | 膜厚偏差(片内) | <1% | 2-5% | CVD/PVD/ALD |
| **Chemical Mechanical Polish (CMP)** 平坦度 | 全局平坦化 | <50 nm non-uniformity | 50-100 nm | 影响聚焦容差 |
| **Gate Oxide Thickness** | 栅氧厚度 | 0.8-1.2 nm (N5) | — | 等效氧化物厚度 EOT |
| **Threshold Voltage (Vth) 偏差** | 阈值电压变化(3σ) | <15 mV | 20-40 mV | RTN 额外增加 |

### 8.4 制造效率指标

| 指标 | BIC | Typical | 说明 |
|:----|:----|:--------|:-----|
| **Cycle Time (晶圆)** | 从入场到出厂 | 40-60 天(N5) | 60-90 天 | 金属层越多越长 |
| **Cycle Time (光刻层)** | 每层平均 | 0.8-1.2 天/层 | 1-2 天/层 | — |
| **OEE (Overall Equipment Effectiveness)** | 设备综合效率 | >85% | 65-80% | 光刻机利用率~90%+ |
| **产量/月 (Wafer Start)** | 月投片量 | 40-50K wpm(N5) | 20-30K wpm | 一个产品系列 |
| **每片光刻层** | 总光刻步骤 | 70-100 层(N5) | 50-80 层(N7) | E-beam 层数增加 |
| **E-beam 直接写入层 (N5/N3)** | 关键层数 | 4-6层 | 2-3 | 极限分辨率需求 |

### 8.5 SPC 控制指标

| 指标 | 定义 | BIC (Cpk目标) | Typical | 说明 |
|:----|:-----|:-------------|:--------|:-----|
| **Cpk (Critical Process)** | 关键工序能力 | >1.67 | >1.33 | CD/Overlay/厚度 |
| **Cpk (Non-critical)** | 非关键工序 | >1.33 | >1.00 | 一般参数 |
| **Ppk (Initial)** | 初始工艺性能 | >1.33 | >1.00 | 新工艺初始阶段低 |
| **Cpk 退化容忍** | 长期漂移 | <0.1 退化 | <0.3 退化 | Cpk>1.33→>1.23 |
| **UCL/LCL 违规报警率** | SPC 误报警 | <1% 样本 | 3-5% 样本 | 3sigma 控制图 |

---

## 9. 晶圆测试（CP）阶段

### 9.1 良率与分档指标

| 指标 | 定义 | BIC | Typical | 说明 |
|:----|:-----|:----|:--------|:-----|
| **CP Yield** | 晶圆探测良率 | >85% (成熟) | 70-85% | 直接 dye yield × electrical test yield |
| **Sort Yield (功能性)** | 功能测试通过率 | >90% | 75-90% | 包含 Vmin/Iddq 筛选 |
| **Bin 分布 (Speed Sort)** | 速度分级比例 | Top bin >30% | Top bin 10-20% | GPU/CPU 的 bin pricing |
| **Top Speed Bin Vmin** | 最快 bin 最低电压 | 标称 Vdd-80mV | 标称 Vdd-50mV | N5 CPU |
| **Mid Bin Volume** | 中档比例 | >50% | 40-60% | — |
| **Low Bin / Reject** | 低档/报废 | <5% reject | 10-20% | 过渡策略 |
| **Yield 从 CP 到系统** | 最终可用片比 | >70% | 50-65% | 散热/封装降额 |

### 9.2 测试覆盖率指标

| 指标 | 定义 | Sign-off 标准 | BIC | Typical |
|:----|:-----|:------------|:----|:--------|
| **Stuck-at Fault Coverage** | 固定故障覆盖率 | >97% | >99% | >97% |
| **Transition Delay Coverage** | 转换延迟故障 | >90% | >95% | >85% |
| **Path Delay Coverage** | 路径延迟(关键路径) | 100% critical | 100% | >80% |
| **Bridge Fault Coverage** | 桥接故障 | Custom | >90% | >70% |
| **IDDQ 可测性** | 静态漏电流测 | Custom | >95% cells | >85% |
| **MBIST 覆盖率** | SRAM 测试 | 100% | 100% | >98% |
| **Analog BIST 覆盖率** | 模拟测试 | Custom | >90% | >70% |

### 9.3 测试效率指标

| 指标 | 定义 | BIC | Typical | 说明 |
|:----|:-----|:----|:--------|:-----|
| **Test Time / Die** | 每 die 测试时间 | <10s | 15-60s | 直接影响成本 |
| **Multi-site Test** | 并行测试片数 | 8-32 site | 4-8 site | 探针卡限制 |
| **Probe Card 寿命** | 可接触次数 | 500K-1M touch | 200-500K | MEMS 探针更长 |
| **Probe Card Cost** | 一次成本 | $20-100K | $15-50K | 高速/多 site 更贵 |
| **Probe Overdrive** | 探针过驱动 | 30-50 μm | 50-80 μm | 损伤 pad |
| **Pad Pitch (最小)** | 焊盘间距 | >30 μm | >40 μm | 先进节点更密 |
| **First Pass Yield (CP)** | 首次探测良率 | >70% | 50-65% | 含 retest |

### 9.4 测试数据与统计分析

| 指标 | BIC | Typical | 说明 |
|:----|:----|:--------|:-----|
| 每 die 测试数据量 | 100K-500K bytes | 10K-100K bytes | 含 bin/volt/temp |
| 晶圆级数据点 | 各 die 的 Vmin/Iddq/Fmax | 每 die 50-200 参数 | 用于良率学习 |
| **Spatial Yield Pattern** | 空间分布偏置 | 环形偏置<5% | 环形偏置 5-15% | 边缘 vs 中心 |
| **Retest Rate** | 复测比例 | <3% | 5-10% | 接触/ATR(异步)误差 |
| 探针卡清洁频率 | 每晶圆数 | >200 wafers | 50-150 wafers | 接触电阻漂移 |

---

## 10. 封装阶段

### 10.1 封装良率指标

| 指标 | 定义 | BIC | Typical | 说明 |
|:----|:-----|:----|:--------|:-----|
| **Assembly Yield** | 封装良率 | >99% | 97-99% | 含 die attach/wire bond/molding |
| **Bump/Pillar Yield** | 微凸互联良率 | >99.9% | 99-99.9% | 微焊球(<50μm)更低 |
| **Underfill Void Rate** | 底部填充空洞率 | <1% | 1-5% | 大空洞影响可靠性 |
| **Known Good Die (KGD) Yield** | 封装前 KGD | >95% | 85-95% | Chiplet 设计关键 |
| **Si Interposer Yield** | 硅中介层良率 | >90% | 75-90% | 大面积更差 |
| **Hybrid Bonding Yield** | 混合键合良率 | >99.9% (成熟) | >99% | 3D 堆叠关键工艺 |

### 10.2 封装性能指标

| 指标 | 定义 | BIC | Typical | 说明 |
|:----|:-----|:----|:--------|:-----|
| **Warpage (Post-Reflow)** | 封装翘曲 | <30 μm (for LGA) | 50-100 μm | 影响 SMT 焊接 |
| **Warpage over Temp** | 热循环翘曲变化 | <20 μm | 30-60 μm | CTE 不匹配 |
| **Rth-jc (Junction-case)** | 结到壳热阻 | 0.1-0.2 °C/W | 0.3-0.5 °C/W | IHS 和 TIM 质量 |
| **Rth-ja (Junction-ambient)** | 结到环境热阻 | 0.3-0.8 °C/W | 1-3 °C/W | 取决于散热方案 |
| **Bump Resistance (50μm Cu pillar)** | 微凸电阻 | 5-15 mΩ | 10-30 mΩ | 每 bump |
| **TSV Resistance (Through-Si Via)** | 硅通孔电阻 | 10-50 mΩ | 30-100 mΩ | 直径~10μm |
| **HSIO (High-Speed IO) Insertion Loss** | IO 插入损耗 | <1 dB @ 28GHz | 1-3 dB @ 28GHz | 封装走线 |
| **Power Delivery Impedance** | 供电阻抗 | <1 mΩ | 1-5 mΩ | 含 decoupling cap |
| **Interconnect Density (per mm²)** | 互联密度 | 10K-40K/mm² | 1K-10K/mm² | Hybrid Bonding |

### 10.3 封装效率指标

| 指标 | BIC | Typical | 说明 |
|:----|:----|:--------|:-----|
| **UPH (Unit Per Hour)** | 每小时封装数 | >500 (FCBGA) | 200-500 | 取决于复杂度和尺寸 |
| **Substrate 层数** | 基板层数 | 12-20 层 | 8-12 层 | GPU/CPU 更复杂 |
| **Substrate Cost** | 基板成本 | $10-50(CPU) | $5-20(CPU) | GPU:$20-100+ |
| **Package TAT** | 封装周期 | 2-4 周 | 4-8 周 | 含 bake/POP/测试 |
| **Bond Pad Array Pitch** | 焊球阵列间距 | 0.4-0.8 mm | 0.8-1.0 mm | 密阵降低 PCB 成本 |

---

## 11. 终测（FT）阶段

### 11.1 终测良率

| 指标 | 定义 | BIC | Typical | 说明 |
|:----|:-----|:----|:--------|:-----|
| **FT Yield** | 封装后终测良率 | >95% | 85-95% | 约 CP yield × 封装 yield |
| **Speed Bin 分布** | 速度分级 | Top bin >25% | 10-20% | 高温下 bin 降级 |
| **Hot/Cold Temperature Bin** | 温度 bin 分布 | <5% shift | 10-20% shift | Vmin 随温度漂移 |
| **Shmoo Yield (Voltage Margin)** | 电压窗口曲线 | >95% @ Vnom | 85-95% | Vmin 分布形状 |
| **Fmax Distribution (3σ)** | Fmax 散布 | <5% Fmax | 10-20% Fmax | 工艺均匀性 |
| **DPPM (Defective Parts Per Million)** | 缺陷率 | <100 DPPM | 500-2000 DPPM | 客户要求<100-500 |
| **Failure Rate per Test Insertion** | 每步故障率 | <0.5% | 1-3% | 重复接触损伤 |

### 11.2 测试效率指标

| 指标 | BIC | Typical | 说明 |
|:----|:----|:--------|:-----|
| **Test Time / Unit (FT)** | 每单元测试时间 | <5s | 10-30s | 含 pattern load/power seq |
| **Test Cost / Unit** | 每颗测试成本 | $0.1-0.5 | $0.5-2 | 按摊还 3 年+ 产量 |
| **Handler UPH** | 分选机吞吐 | >5,000 UPH | 2,000-4,000 UPH | 3-site × 接触/分选 |
| **Socket 寿命** | 插座接触次数 | 500K-1M | 200-500K | 插座接触退化 |
| **Multi-site Test (FT)** | 并行测试 | 8-32 site | 2-8 site | 测试机资源制约束 |
| **Contact Resistance Tolerance** | 接触电阻容差 | <0.5Ω | 0.5-1Ω | 在大电流时影响压降 |

### 11.3 测试覆盖与质量指标

| 指标 | BIC | Typical | 说明 |
|:----|:----|:--------|:-----|
| **Test Coverage (FT)** | 终测总覆盖率 | >95% | 85-95% | 含 pattern 和 functional |
| **Functional Test Coverage** | 功能测试覆盖 | >80% | 50-70% | 性能 bin/sort |
| **ATPG Pattern Size** | 测试图形数量 | 10K-100K patterns | 3K-30K | 压缩后数量 |
| **Pattern Memory Depth** | 图形深度 | 32-128M vectors | 16-32M | 测试机内存约束 |
| **System Level Test (SLT)** | 系统级测试覆盖 | 50-100 test cases | 20-50 | 服务器芯片通常含 |
| **SLT Time** | SLT 时间 | 10-60 min | 30-120 min | 制约产出量 |

---

## 12. 可靠性认证阶段

### 12.1 可靠性测试指标

| 测试 | 标准条件 | 样本量 | 接受标准 | BIC (通过率) | Typical | 说明 |
|:----|:---------|:------|:---------|:-------------|:--------|:-----|
| **HTOL (High Temperature Operating Life)** | 125-150°C, Vmax, 1000h | 77-231 (JEDEC) | 0 fail | >99.9% | 95-99% | 早期/随机/磨损期 |
| **LTOL (Low Temp)** | -40°C~-55°C, 500-1000h | 77 | 0 fail | 100% | >98% | 低温载流子效应 |
| **ELFR (Early Life Failure)** | 动态工作, 48-96h | 500-2000 | <1000 DPPM | <100 DPPM | 200-1000 DPPM | 早期失效 burn-in |
| **HTS (High Temp Storage)** | 125-150°C, 1000h | 45-77 | 0 fail | 100% | >99% | 看扩散/互连退化 |
| **uHAST (Unbiased HAST)** | 110-130°C/85%RH, 264h | 77 | 0 fail | 100% | >98% | 湿度敏感 |
| **TC (Temperature Cycle)** | -55°C↔125°C, 500-1000cyc | 77 | 0 fail | >99% | 95-99% | CTE 匹配 |
| **TST (Thermal Shock)** | -55°C↔125°C, liquid | 45-77 | 0 fail | >99% | 95-99% | 比 TC 更严 |
| **ESD-HBM** | 人体模型 2000V | 3 samples × 3 lots | ±2000V pass | >±4000V | ±2000-4000V | JEDEC JS-001 |
| **ESD-CDM** | 充电器件模型 500V | 3 samples × 3 lots | ±500V pass | >±750V | ±500-750V | JEDEC JS-002 |
| **Latch-up** | 85-125°C, ±100mA/1.5×Vmax | 3 samples | pass | >±200mA | ±100-150mA | JEDEC JESD78 |

### 12.2 寿命与失效率指标

| 指标 | 定义 | BIC | Typical | 说明 |
|:----|:-----|:----|:--------|:-----|
| **FIT (Failures In Time, 10⁹h)** | 每十亿小时失效数 | <10 | 10-100 | 服务器级要求<10 FIT |
| **MTBF** | 平均无故障时间 | >10⁸ h | 10⁶-10⁷ h | 与 FIT 互为倒数 |
| **Weibull β (wear-in)** | 早期失效形状参数 | β<1 (decreasing) | β<1 | 使用 burn-in 筛除 |
| **Weibull β (useful life)** | 恒定失效率期 | β≈1 | β≈1 | 随机失效 |
| **Weibull β (wear-out)** | 磨损期 | β>3 (快速退化) | β=2-3 | 需在寿命终点前换 |
| **Weibull η (characteristic life)** | 特征寿命(63.2%失效) | >10⁵ h | 10⁴-5×10⁴ h | 取决于工作条件 |
| **Activation Energy (Ea)** | Arrhenius 活化能 | 0.7-1.0 eV | 0.5-0.8 eV | 加速因子计算 |
| **AF (Acceleration Factor)** | 加速因子(85°C vs 55°C) | 20-50× | 10-30× | 温度加速模型的典型值 |
| **T50 (Median Life)** | 中位寿命 | >2×10⁵ h | 5×10⁴-2×10⁵ h | 对数正态表征 |
| **σ (Lognormal)** | 对数正态分布 sigma | <0.5 | 0.5-1.0 | sigma 越小越均匀 |
| **Coffin-Manson 疲劳指数** | 热循环加速 | >2.5 (BIC) | 1.5-2.5 | 焊点/TSV |

### 12.3 筛选 (Screening) 指标

| 方法 | 条件 | BIC 效果 | Typical | 说明 |
|:----|:-----|:---------|:--------|:-----|
| **Burn-in (Dynamic)** | Vmax+10%, 125°C, 24-48h | 去除 90%+ 早期失效 | 去除 70-80% | 成本高(>$2/unit) |
| **Iddq 筛选** | 静态漏电流 >3σ 拒绝 | 捕 40-60% defect | 捕 20-40% | 先进节点 Iddq 值增加 |
| **Vmin 排序** | 频率-电压特性 | 移除 5-10% tail | 3-5% | 功耗和速度配对 |
| **Voltage Screen** | Vdd+10%, at-speed | 捕 3-8% weak die | 1-3% | 加速早期失效 |
| **Shmoo Analysis** | V/f 二维参数 | 异常点 reject | — | 多维异常检测 |

---

## 13. 系统级验证与生态认证阶段

### 13.1 系统级测试指标

| 指标 | 定义 | BIC | Typical | 说明 |
|:----|:-----|:----|:--------|:-----|
| **SLT Coverage** | 系统级功能覆盖 | >80% 关键场景 | 50-70% | 含 OS 级/驱动/app |
| **系统级测试时间** | 每芯片 SLT | <10 min | 10-30 min | 含多次 reboot |
| **OS 安装成功率** | 引导 OS 比例 | >99% | 95-99% | 含 Linux/Windows |
| **压力测试通过率** | 持续满载时间 | >24h pass 99% | 12h pass 95% | 含温度压力 |
| **Memory 压力测试** | MEMTEST86/etc | >99.5% | 95-99% | 64-bit pattern |
| **PCIe 链路训练** | 各代速率握手 | >99% gen5 | >95% gen5 | 难度随速率递增 |
| **DPPM (System Level)** | 系统级缺陷率 | <50 DPPM | 100-500 DPPM | 客户最终接收质量 |

### 13.2 生态认证指标

| 认证 | 要求 | BIC (首次通过) | Typical | 说明 |
|:----|:-----|:--------------|:--------|:-----|
| **PCI-SIG Compliance** | Gen3/4/5/6电气+协议 | 首次>90% pass | 60-80% pass | 3 次内需全部通过 |
| **JEDEC DDR5/LPDDR5** | JESD79-5 | 首次>80% | 50-65% | DDR 速度增加更严 |
| **CXL Compliance** | IEEE/CXL Consortium | 首次>85% | — | 刚兴起 |
| **OCP 互操作测试** | OCP platform | 首次>90% | 70-85% | 服务器平台 |
| **OS 认证 (RHEL/Ubuntu)** | IHV certification | 4-8 周 | 8-16 周 | 含 WHQL/HLK |
| **VMware vSphere 认证** | HCL | 客户常主导 | OEM 主导 | — |
| **Network Protocol Compliance** | Ethernet/FC/InfiniBand | >90% | 70-85% | 特定的 PHY/MAC |

### 13.3 Bring-up 效率指标

| 指标 | BIC | Typical | 说明 |
|:----|:----|:--------|:-----|
| Power-on to Console | 通电到串口可见 | <2 天 | 5-30 天 |
| First Boot to OS | 首次引导 OS | <1 周 | 2-8 周 |
| 关键路径收敛 | 所有 core 工作 | <1 月 | 2-4 月 |
| Bug Find Rate (硅后阶段) | 硅后bug发现 | 峰值 20-50/周 | 10-30/周 |
| 全功能收敛 (All Features) | 功能全部验证 | 3-6 月 | 6-12 月 |
| 硅后调试瓶颈修复率 | 阻碍 bug 修复 | >80% 在 1 周内 | 50-70% |

---

## 14. 量产爬坡与成本阶段

### 14.1 量产良率爬坡

| 指标 | BIC | Typical | 说明 |
|:----|:----|:--------|:-----|
| **Yield at Start of Production (SOP)** | 量产启动良率 | >70% | 50-60% |
| **Yield at Maturity** | 成熟期良率 | >90% | 75-85% |
| **Yield Ramp Rate (月度增量)** | 月提升量 | +2-4%/月 | +1-2%/月 |
| **Time to Target Yield (TTY)** | 达到目标良率时间 | <6 月 | 8-18 月 |
| **KGD (Known Good Die) 提升速度** | KGD 目标提升 | +5%/月 | +2%/月 |
| **HVM yield 饱和度** | 量产稳定度 | ±1%/季 | ±2-3%/季 |
| **Defect Pareto 修正速度** | Top issue 修复 | <4 周 | 6-12 周 |
| **良率学习周期** | DOE→改进→闭环 | 4-6 周 | 8-16 周 |

### 14.2 成本指标

| 指标 | 定义 | BIC | Typical | 说明 |
|:----|:-----|:----|:--------|:-----|
| **Cost Per Wafer** | 每片成本 | $2-4K (N5), $1.5-2.5K (N7) | — | TSMC N5 ~$1.7-2.5K |
| **Cost Per mm²** | 每平方毫米成本 | $0.5-1.5 (N5) | — | N7: ~$0.3-0.8; N28: ~$0.05-0.1 |
| **Cost Per Die** | 每颗裸片成本 | 取决于面积 | — | 300mm² N5~$300-500 |
| **NRE (Non-Recurring Engineering)** | 一次性工程费用 | $5-20M | $2-10M | 7nm 设计 NRE |
| **Mask Set Cost** | 掩模版套成本 | $5-8M (N5) | $3-5M (N7) | N3: ~$8-12M |
| **Packaging Cost** | 封装成本 | $5-20/die (FCBGA) | $2-10/die | GPU:~$20-100 |
| **Test Cost** | 测试成本 | $0.5-2/die | $1-5/die | 含 CP+FT |
| **Total Manufactured Cost** | 总制造成本 | $10-100/die | — | 按产品差别巨大 |
| **Break-even Volume** | 盈亏平衡量 | <5M (CPU) | 10-50M | 大芯片需要更高走量 |

### 14.3 量产效率指标

| 指标 | BIC | Typical | 说明 |
|:----|:----|:--------|:-----|
| **Monthly Volume (HVM)** | 月产量 | 1M+/月(CPU) | 100K-500K | 消费级更高 |
| **Wafer Start Per Month** | 月投片 | 40K-50K wpm | 15K-30K | N5 产线 |
| **TAT from Wafer Start to Ship** | 从投片到出货 | 6-10 周 | 10-16 周 | 含封测 |
| **Factory Cycle Time** | 工厂周期 | <5 周(only fab) | 6-8 周 | HVM 加速 |
| **Lot Yield (量产批次)** | 批次一致性 | >99% lot pass | 95-99% | 批量确认 |
| **Build Plan Achievability** | 计划达成率 | >90% | 70-85% | NPI 阶段波动 |
| **Cost Reduction YoY** | 年成本降幅 | >15% | 5-10% | 良率/测试优化 |

### 14.4 Yield Learning & Data Analytics

| 指标 | BIC | Typical | 说明 |
|:----|:----|:--------|:-----|
| Volume Data Collection | 每 die 数据数 | >200 parameters | 50-100 |
| Inline Defect Capture Rate | 在线缺陷检出率 | >80% | 50-70% | Inspection tool 覆盖率 |
| Defect Classification Accuracy | 缺陷分类准确率 | >95% (ML) | 70-85% | SEM/structure 分类 |
| Pareto to Root Cause Time | Pareto 找到根因 | <2 天 | 1-4 周 | 自动化分析 |
| Yield Prediction Accuracy | 良率预测精度(3个月) | ±3% | ±5-10% | 基于良率模型+ML |

---

## 15. 跨领域综合指标

### 15.1 研发投入指标

| 指标 | BIC | Typical | 说明 |
|:----|:----|:--------|:-----|
| **R&D Cost / 项目 (CPU/GPU)** | 总研发投入 | $0.5-2B (新型 GPU) | $50-500M (CPU) | 含架构→量产全流程 |
| **R&D Cost / 项目 (SoC)** | 小 SoC | $10-50M | $5-20M | 如 SSD 主控/USB PHY |
| **R&D Time (Arch → Tape-out)** | 研发周期 | 2-3 年 (CPU) | 1.5-2.5 年 (SoC) | GPU:~3-4 年 |
| **Tape-out → HVM 时间** | 量产周期 | 6-12 月 | 9-18 月 | 良率爬坡时间 |
| **Team Size (Full Project)** | 项目团队总人数 | 500-2000+ (CPU/GPU) | 100-500 (SoC) | GPU 达 2000+ |
| **EDA License Cost / 年** | EDA 软件费 | $10-50M | $3-15M | 大公司签署 3 年合同 |
| **IP 采购成本** | 授权第三方 IP | $1-10M | $0.5-5M | PHY/Serdes/内存控制器 |

### 15.2 项目质量指标

| 指标 | 定义 | BIC | Typical | 说明 |
|:----|:-----|:----|:--------|:-----|
| **First Pass Silicon Success** | 首版成功 | >90% (成熟团队) | 60-80% | A0 版本带功能 |
| **Re-spin Cause Pareto** | 返工原因分布 | 功能bug 30%, 性能 40% | 功能 50%, 性能 30% | 验证质量提升可降低功能 bug |
| **Schedule Achievement** | 计划达成度 | ±10% | ±20-30% | GPU 往往延迟 6-12 月 |
| **Quality at Delivery (DPPM)** | 交付 DPPM | <100 | 200-1000 | 手机/服务器要求更严 |
| **Customer Return Rate** | 客户退货率 | <0.1% | 0.3-1% | 含 DOA (Dead on Arrival) |
| **Field Return DPPM** | 现场 DPPM | <50 (1年) | 100-500 | 可靠性+ESD 影响 |

### 15.3 硅片→系统效率

| 指标 | BIC | Typical | 说明 |
|:----|:----|:--------|:-----|
| **Die to Package Yield Loss** | 封装损耗 | <3% | 5-10% | 含破片/焊线失败 |
| **System Test Yield** | 系统测试良率 | >90% | 75-85% | OEM 生产的综合良率 |
| **NPI (New Product Introduction) 周期** | 新品导入 | 3-6 月 | 6-12 月 | 含客户认证 |
| **Volume Ramp Time (to 1M/yr)** | 至 1M 量产 | 12-18 月 | 18-36 月 | 取决于良率爬坡 |
| **Product Lifecycle** | 产品生命周期 | 3-5 年(服务器) | 2-3 年(消费) | 服务器更长 |

### 15.4 不同芯片类型的差异化指标

| 指标 | CPU | GPU | DRAM | NAND | SSD 主控 |
|:-----|:---:|:---:|:----:|:----:|:--------:|
| **逻辑门数** | 0.5-5B | 5-20B | <50M | <10M | 0.1-0.5B |
| **工艺节点** | N5/N3 | N5/N4 | 1α~1β (专门DRAM) | 3xx层(232-400+) | N12/N7/N5 |
| **设计周期** | 2-3 年 | 3-4 年 | 1.5-2 年 | 1.5-2 年 | 1-2 年 |
| **团队规模(研发)** | 500-1500 | 1000-3000 | 100-300 | 100-200 | 200-500 |
| **验证:设计比** | 2-3:1 | 3-4:1 | 0.5:1(验证少) | 0.3:1 | 1.5-2:1 |
| **物理瓶颈** | ×(控制密集) | √(阵列密集) | √√(模拟版图) | √√(工艺三维) | ×(标准数字) |
| **第一版 Si 成功率** | 70-85% | 60-75% | 50-65% | 50-65% | 75-85% |
| **DPPM 目标** | <100 | <200 | <500 | <1000 | <100 |
| **成本构成 Top1** | EDA+验证人力 | 流片(NRE+mask) | 晶圆制造成本 | 3D 堆叠工艺 | 固件开发成本 |

### 15.5 数据汇总：芯片级性能演进速率

| 维度 | 典型年增益 | BIC 年增益 | 驱动因素 |
|:----|:----------|:-----------|:---------|
| 单核性能(SPECint) | +3-5% | +10-15% (新微架构) | 架构创新>工艺缩放 |
| GPU 算力(FP32) | +30-40% | +40-70% | 架构+工艺+规模三重驱动 |
| DRAM 密度 | +15-20% | +25-30% | EUV + 设计技术协同 (DTCO) |
| NAND 密度 | +25-35% | +40-50% | 层数堆叠驱动 |
| SSD 性能 | +30-50% | +50-100% | PCIe Gen × + NAND 速度 |
| SerDes 速率(Gb/s) | +15-25% | +25-40% | PAM4+DSP 演进 |
| HBM 带宽 | +25-35% | +40-50% | TSV 密度+堆叠层数 |
| 封装互联密度 | +30-50% | +50-100% (3D HB) | 混合键合 (Hybrid Bonding) |

---

## 16. 参考文献与数据来源

> 本文数据综合来源包括但不限于：
>
> **标准/规范**:
> - JEDEC JEP122G — Failure Mechanisms and Models for Semiconductor Devices
> - JEDEC JESD47 — Stress-Test-Driven Qualification of Integrated Circuits
> - JEDEC JESD74 — Early Life Failure Rate Calculation
> - JEDEC JESD57 — ESD Sensitivity Testing (CDM/HBM)
> - IEEE 1149.1 — JTAG Boundary Scan
> - IEEE 1687 — IJTAG (Internal JTAG)
>
> **行业报告**:
> - IBS (International Business Strategies) — Cost and Value Models
> - IC Knowledge — IC Cost and Price Models
> - SemiAnalysis — Semiconductor Deep Dives
> - TechInsights (Chipworks) — Die Cost Analysis
> - ASML 年度报告 — 光刻/量测技术
>
> **厂商公开资料**:
> - TSMC — Technology Roadmap, Yield Learning Methodology
> - Samsung — Foundry Technology Briefs
> - Intel — Process Technology and Product Specifications
> - NVIDIA — GPU Architecture White Papers
> - AMD — Chiplet Design and Integration Reports
>
> **论文/学术**:
> - "A New Yield Model for Sub-threshold Leakage Limited Designs" — ICCAD
> - "Machine Learning for Yield Learning and Optimization" — DAC 2023
> - "Chip Placement with Deep Reinforcement Learning" — Nature 2021
> - Various DAC/ISSCC/ICCAD papers on PPA modeling and yield

---

## 修订记录

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-07-01 | v1.0 | 首次创建。覆盖 15 个阶段 × 150+ 指标，含 BIC/Typical 基准值（以 N7/N5 先进制程为主要参考节点）。数据来源：JEDEC/IEEE/行业报告/厂商公开资料 |
