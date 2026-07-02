# 超节点专题

> AI超节点架构、液冷方案、供电方案、整体方案

## 范围
- 超节点架构定义与路线（NVLink域、晶圆级、统一内存、全栈自主）
- 代表产品（GB200 NVL72、Cerebras CS-3、MI300X、Atlas 900）
- 液冷散热方案（冷板式、浸没式、CDU、快接头）
- 供电方案（48V/800V HVDC、整机柜供电）
- 互联方案（NVLink、UALink、PCIe Switch、CXL）
- 超节点开放标准（OCP OAM、ODCC、UALink）

## 核心分析
- ⭐ **[超节点系统架构五维深度分析](../../02_rd/03_hardware/06_superpod/supernode-architecture-deep-analysis.md)** ⭐ **新增** — 26KB完整论证：①铜缆+光纤混合互联 ②分布式固件（灵衢参考）③拓扑感知管理平台 ④MFU/ETTR/MTBF指标 ⑤三类典型故障×应对策略

## 标签
`超节点` `液冷` `供电` `NVLink` `OAM` `整机柜` `系统架构` `分布式固件`

## 关联模块
- [服务器硬件架构与设计](../../05_tools/methodology-tools/README.md) — 超节点是服务器的演进形态
- [智算方案](../../05_tools/methodology-tools/README.md) — 超节点是智算的关键单元
- [万卡集群与训推优化](../../05_tools/methodology-tools/README.md) — 超节点集群化
