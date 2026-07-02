# 🔬 可靠性与测试 — 行业跟踪框架

## 核心跟踪问题
- 大规模训练可靠性（慢节点检测/容错/检查点）新方案
- GPU 故障检测/预测/自动修复技术
- 测试验证体系（压力测试/稳定性测试）新方法论
- 集群可靠性 SLA/SLO 定义与达成
- 新硬件可靠性数据（HBM/SSD/互联）

## 搜索关键词
- `training reliability` `straggler detection` `fault tolerance training`
- `GPU fault detection` `predictive failure GPU`
- `checkpoint optimization` `fault recovery training`
- `HBM reliability` `SSD endurance`
- `分布式训练 容错` `集群可靠性`

## 来源优先级

| 优先级 | 来源 | 说明 |
|:-----:|:-----|:-----|
| 🥇 Tier 1 | **arXiv.org** (cs.DC/cs.LG) | 最新容错/可靠性论文 |
| 🥇 Tier 1 | **SOSP/OSDI/MLSys/SC** 会议论文 | 顶会发表 |
| 🥈 Tier 2 | **Meta / Google / Microsoft Engineering Blogs** | 大规模部署经验 |
| 🥈 Tier 2 | **NVIDIA DCGM / NVFlash** 更新 | GPU 级可靠性 |
| 🥉 Tier 3 | **JEDEC** (HBM4 可靠性) | 标准更新 |

## 质量门槛
- ✅ **值得记录**：具体可靠性提升数据（% MFU 提升/检查点时间/故障覆盖）
- ❌ **跳过**：通用可靠性框架介绍无数据

## 输出路径
- `knowledge/01_survey/reliability-testing/YYYY-MM-DD.md`

## 交叉引用
- 容错 ↔ `cluster-training/` (训练效率)
- GPU 可靠性 ↔ `distributed-os/` (集合通信容错)
