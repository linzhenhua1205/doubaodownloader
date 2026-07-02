# 服务器硬件架构与设计

> AI服务器整机设计、硬件架构、互联拓扑、系统方法论

## 范围
- AI服务器整机架构设计（GPU Server、CPU Server）
- 硬件选型与BOM设计
- 主板/背板/互联设计
- 散热架构（风冷/液冷整体方案）
- 供电架构（PSU、VR、HVDC）
- 服务器形态（OAM、UBB、整机柜）
- 互联拓扑（Scale-Up / Scale-Out 全拓扑分析）
- 硬件兼容性测试与认证

## 标签
`服务器硬件` `整机设计` `GPU Server` `BOM` `硬件选型` `互联拓扑` `架构演进`

## 核心知识文件

### 架构分析与演进
| 文件 | 说明 |
|:-----|:------|
| [服务器硬件架构与设计知识全集](../../02_rd/03_hardware/01_hw_core/architecture-design-complete.md) | 18章知识体系（增强版） |
| [服务器架构演进摆动周期分析](../../02_rd/03_hardware/01_hw_core/architecture-evolution-swing-analysis.md) | **五组摆动分析** — Scale-up↔Scale-out·CPU↔卸载·部件↔整机·总线↔网络·散热供电 |
| [框式架构与服务器形态互联全景](../../02_rd/03_hardware/01_hw_core/box-architecture-form-factors.md) | **九种形态深度分析**（1U单路→SuperPod）— 五类板卡互联矩阵·33个架构案例 |
| [服务器互联层次深度解析](../../02_rd/03_hardware/01_hw_core/interconnect-hierarchy-deep-dive.md) | **六层互联全覆盖**（L5片上→L0管理），含PCIe/CXL/NVLink/UALink全协议对比 |
| ⭐ [分布式互联拓扑全景：五大拓扑+选型决策体系](../../02_rd/03_hardware/01_hw_core/network-topology-complete-analysis.md) | 正交·Full-Mesh·Flattened Butterfly·Fat-Tree·Dragonfly 深度分析 + 选型决策树 |
| [Super POD 网络架构](../../02_rd/03_hardware/06_superpod/superpod_arch.md) | 超节点Scale-Up/Scale-Out组网完整拓扑（含ASCII art架构图） |

### 研发方法论与流程
| 文件 | 说明 |
|:-----|:------|
| ⭐ [服务器设计方法论框架](../../02_rd/03_hardware/01_hw_core/server-design-methodology-framework.md) | **80KB完整方法论** — L6~L12交付·部件5维度·AI场景·6维约束·6大权衡·5年演进 |
| ⭐ [服务器设计范式转变全景分析](../../02_rd/03_hardware/05_AIServer/server-design-paradigm-shift.md) | 5个根本性范式转变·设计者角色重构·2016→2026思维变迁 |
| [服务器设计范式辩证分析与层级扩展](../../02_rd/03_hardware/05_AIServer/server-design-paradigm-shift-supplement.md) | 八范式×四层级决策矩阵·5个修正建议 |
| [推理场景推演：Inf-4G产品定义](../../02_rd/03_hardware/05_AIServer/paradigm-shift-scenario-inf4g.md) | 以2027年推理服务器为场景的完整产品定义 |
| [推演评审会：Inf-4G压力测试](../../02_rd/03_hardware/05_AIServer/paradigm-shift-scenario-review-inf4g.md) | 10项决策逐一质疑·3项修正·评审评分 |
| [训练集群推演：万卡集群方案](../../02_rd/03_hardware/05_AIServer/paradigm-shift-scenario-training-cluster.md) | 2027年万卡训练集群·与推理场景10维度对比 |
| ⭐ [国产方案独立推演](../../02_rd/03_hardware/05_AIServer/paradigm-shift-scenario-domestic.md) | **46KB** — 2027年纯昇腾/寒武纪路线·10维度对比·TianGong-8P/ KunLun-8A完整规格 |
| [AI服务器整机研发设计指南（团队实战版）](../../02_rd/03_hardware/05_AIServer/server-system-development-guide.md) | v2.0 30-80人团队实战指南·1004行·完整研发链路 |
| [服务器整机系统设计实战指南（六维深度）](../../02_rd/03_hardware/05_AIServer/server-system-design-compass.md) | 友商分析·规格定义·配置策略·场景驱动·资源复用·面板/板卡定义 |
| [服务器整机研发IPD流程跨域协同全景](../../02_rd/03_hardware/01_hw_core/server-rd-ipd-process.md) | v2.0, 14领域×TR1-TR6全节点 |
| [服务器整机研发方法论](../../02_rd/03_hardware/01_hw_core/server-rd-methodology.md) | 五层递进研发体系 |

### 专题报告
| 文件 | 说明 |
|:-----|:------|
| [2026-2027 AI服务器整机研发技术综合报告](2026-2027_AI服务器整机研发技术综合报告.md) | **1785行完整版** — 机型定义·互联拓扑·散热·系统设计·权衡决策·供应链 |
| [AI服务器整机研发技术综合报告（摘要版）](../../02_rd/03_hardware/05_AIServer/doubao-ai-server-rd-report-2026.md) | 234行核心结论版本 |
| [架构制图全视角（面试/方案汇报）](../../02_rd/03_hardware/01_hw_core/guide.md) | 12章Mermaid架构图覆盖演进时序·硬件分层·BMC拓扑·软件栈·商业模式 |
| [ODCC GPU内存分层空缺分析](../../02_rd/03_hardware/05_AIServer/odcc-gpu-memory-hierarchy-gap.md) | 内存分层详析 |
| [服务器架构全面解析](服务器架构全面解析.md) | 完整架构解析（含超节点、网络、存储全图） |

### 实操工具
| 文件 | 说明 |
|:-----|:------|
| [研发后全链路工作点深度解析](服务器整机研发后全链路工作点深度解析与落地方案.md) | 降本·配置·BOM·国产化·合规·变更管理全流程方案 |
| [全流程事务性Checklist](服务器整机研发全流程事务性Checklist.md) | 245条纯事务检查项（无角色/组织约束） |
| [后续工作点CHECK清单](服务器整机研发后续工作点CHECK清单.md) | 236条降本/配置/库存/合规检查项 |
| [规格列表（完整版）](服务器整机研发规格列表（完整版）.md) | 供电/散热/安规/结构/环境全规格基线 |
| [研发核心关注维度及要点](服务器研发核心关注维度及要点.md) | 技术适配·硬件设计·软件协同·生产·质量·成本·运维全维度 |

### 每日跟踪
| 文件 | 覆盖日期 | 核心主题 |
|:-----|:---------|:---------|
| [2026-06-03](../components-storage/2026-06-03.md) | COMPUTEX | Vera Rubin量产·DGX Station·Xeon 6+·Diamond Rapids·Marvell CPO |
| [2026-06-04](../bmc-system/2026-06-04.md) | COMPUTEX | Qualcomm Dragonfly·Xeon 6+ 288核·Diamond Rapids HT取消 |
| [2026-06-05](../bmc-system/2026-06-05.md) | COMPUTEX | Frore LiquidJet·AMD Helios·DDR4重产·PCB交期20周 |
| [2026-06-06](../bmc-system/2026-06-06.md) | COMPUTEX | Jensen Seoul·Foxconn新高·ASUS 9U拆解·Clearwater Forest |
| [2026-06-07](../bmc-system/2026-06-07.md) | COMPUTEX | Gigabyte 40节点/1U·RTX Spark四厂·超密度集群 |
| [2026-06-09](../bmc-system/2026-06-09.md) | 服务器追踪 | AMD Venice 256核·Venice N2·Supermicro新冷却液·AI选址干旱 |
| [2026-06-10](../bmc-system/2026-06-10.md) | 服务器追踪 | Vera Rubin量产出货·Samsung HBM4·DGX Station 1600W·Xeon 6+深度 |
| [2026-06-11](../bmc-system/2026-06-11.md) | 服务器追踪 | Foxconn新高·800VDC未延迟·MLCC紧张·HBM锁定2028·SK-Foxconn联盟 |
| [2026-06-12](../cloud-native/2026-06-12.md) | GPU/市场 | SK Hynix供应Vera·HBF设备竞赛·RTX Spark·NAND 400层·韩国出口+370% |

## 📖 文档速览（按使用场景检索）

### 宏观认知
| 你要解决 | 看这份 |
|:---------|:-------|
| 服务器架构演进的核心规律是什么？ | `architecture-evolution-swing-analysis.md` |
| 五种互联拓扑怎么选型？ | `network-topology-complete-analysis.md` → 决策树+黄金法则 |
| AI服务器有哪些类型？怎么演进？ | `architecture-design-complete.md` |
| 2026-2030整体趋势判断？ | `2026-2027_AI服务器整机研发技术综合报告.md` + `network-topology-complete-analysis.md` 第9章 |

### 团队实操（30-80人）
| 你要解决 | 看这份 |
|:---------|:-------|
| 团队怎么搭？各角色干啥？ | `server-system-development-guide.md`→第1章 |
| 项目从立项到量产要哪些阶段？ | `server-system-development-guide.md`→第2章 |
| 系统框图/电源树/互联拓扑怎么设计？ | `server-system-development-guide.md`→第3章 |
| GPU供电/PCIe信号/PCB叠层参数？ | `server-system-development-guide.md`→第4章 |
| BMC固件要开发哪些功能？Redfish API？ | `server-system-development-guide.md`→第4.3节 |
| 测试要测什么？怎么测？ | `server-system-development-guide.md`→第5章 |
| NPI/DFM/良率目标？ | `server-system-development-guide.md`→第6章 |
| 物料怎么选？BOM怎么管？ | `server-system-development-guide.md`→第7章 |
| 研发后降本/配置/规格怎么搞？ | `服务器整机研发后全链路工作点深度解析与落地方案.md` |
| 日常检查缺什么？ | 三个Checklist文件 |

### 设计方案推演
| 你要解决 | 看这份 |
|:---------|:-------|
| 2027年推理服务器怎么做？ | `paradigm-shift-scenario-inf4g.md` |
| 方案被评审时会被问什么？ | `paradigm-shift-scenario-review-inf4g.md` |
| 万卡训练集群怎么设计？ | `paradigm-shift-scenario-training-cluster.md` |
| 国产昇腾方案能走多远？ | `paradigm-shift-scenario-domestic.md` |

### 专题
| 你要解决 | 看这份 |
|:---------|:-------|
| 国产化GPU内存分层问题？ | `odcc-gpu-memory-hierarchy-gap.md` |
| 1U/2U/6U8卡/刀箱/整机柜/超节点怎么选？ | `box-architecture-form-factors.md` |
| CXL/NVLink/UALink/PCIe各是什么关系？ | `interconnect-hierarchy-deep-dive.md` 协议对比 |
| SuperPod的Scale-Up/Scale-Out组网拓扑？ | `superpod_arch.md` |
| 架构图/Mermaid框图怎么画？ | `guide.md` 12章完整框图 |

## 🔗 交叉引用

| 模块 | 关联点 | 配合文档 |
|:-----|:-------|:---------|
| [BMC与系统管理](../../05_tools/methodology-tools/README.md) | 硬件管理接口、固件开发 | BMC开发参考 |
| [超节点专题](../../supernode/supernode-standards.md) | 超节点整机方案、液冷架构 | 超节点 vs 标准服务器架构 |
| [可靠性与测试](../../05_tools/methodology-tools/README.md) | 硬件验证、可靠性方法 | 测试方案补充 |
| [部件（存储体系）](../../05_tools/methodology-tools/README.md) | 部件选型、HBM/CXL/SSD | 存储层级与选型参数 |
| [分布式操作系统设计](../../05_tools/methodology-tools/README.md) | 集合通信、RDMA、拓扑感知调度 | NCCL/RoCE/网络优化 |
| [行业专题调研](../../05_tools/methodology-tools/README.md) | GPU芯片竞争、高速互联、市场格局 | 行业趋势跟踪 |
