# 🔗 分布式操作系统设计 — 行业跟踪框架

## 核心跟踪问题
- NCCL 新版本/性能改进/新算法（AllReduce/AlltoAll 优化）
- RoCE/RDMA 网络技术进展（拥塞控制/无损网络）
- GDR/GDS（GPU Direct RDMA/Storage）更新
- 拓扑感知调度/集合通信优化
- 安全增强（机密计算/GPU隔离/可信执行环境）

## 搜索关键词
- `NCCL new release` `NCCL performance` `nccl latest`
- `RoCEv2` `RDMA congestion control` `DCQCN`
- `GPU Direct RDMA` `GPU Direct Storage` `GDS`
- `topology-aware scheduling` `AlltoAll optimization`
- `confidential computing GPU` `GPU TEE`
- `arXiv:2606` (结合 nccl/rdma/集合通信)

## 来源优先级

| 优先级 | 来源 | 说明 |
|:-----:|:-----|:-----|
| 🥇 Tier 1 | **arXiv.org** (cs.DC/cs.NI/cs.AR) | 学术论文，NCCL 算法创新 |
| 🥇 Tier 1 | **NVIDIA Developer Blog** | NCCL 发布/最佳实践 |
| 🥈 Tier 2 | **Linux Kernel Mailing List** (RDMA/IB 子系统) | 网络栈改进 |
| 🥈 Tier 2 | **OpenFabrics / OCP NIC** 规范更新 | 互联标准 |
| 🥉 Tier 3 | **The Next Platform / ServeTheHome** | 工程应用报道 |
| 🥉 Tier 3 | **Microsoft / Meta Engineering Blogs** | 大规模部署经验 |

## 质量门槛
- ✅ **值得记录**：新协议/新算法/新 benchmark 数据
- ✅ **深度追踪**：影响分布式训练/推理效率的关键改进
- ❌ **跳过**：无数据的架构介绍/重复内容/纯 PR 稿
- 每发现需标注来源 URL

## 输出模板

```markdown
# 🔗 分布式操作系统设计 — 当日动态 YYYY-MM-DD

> 采集时间: YYYY-MM-DD HH:MM | 来源: {来源列表}

---

## {分类标题}

### {条目标题} ({来源}, {日期})
- {核心发现/性能数据}
- {影响分析}
- 📌 【深度跟踪】{判断/洞察}

---
## 📊 趋势判断

| 方向 | 热度 | 关键信号 |
|:-----|:----|:---------|
| {方向} | {🔥评级} | {信号} |
```

## 输出路径
- `knowledge/01_survey/distributed-os/YYYY-MM-DD.md`

## 交叉引用
- 集合通信 ↔ `cluster-training/` (分布式训练效率)
- 网络基础设施 ↔ `data-center/` (网络布线/拓扑)
- GDS ↔ `components-storage/` (存储层级)
