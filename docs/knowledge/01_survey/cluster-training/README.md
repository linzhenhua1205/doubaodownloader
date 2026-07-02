# 万卡集群与训推优化

> 大规模训练集群、推理优化、训推一体化

## 范围
- 万卡级训练集群架构与设计
- 分布式训练策略（FSDP、Tensor Parallel、Pipeline Parallel等）
- 推理优化（KV Cache、Continuous Batching、PD分离等）
- 训推一体化平台设计与实践
- 集群调度与资源管理

## 标签
`万卡集群` `分布式训练` `推理优化` `PD分离` `训推平台` `KV Cache`

## 内容文件

| 文件 | 说明 |
|:-----|:------|
| [KV Cache 技术全景调研](../../03_AI/cluster-training/kv-cache-technology-panorama.md) ⭐ **新增** | 从基础原理到前沿突破的完整调研（10章，关联6份资料）|
| [KVCache 架构演进全景](../../03_AI/cluster-training/kvcache-architecture-evolution.md) | 7条演进路线：305GB → 7.4GB |
| [PD分离LLM推理部署](../../03_AI/cluster-training/pd-disaggregation-deployment.md) | Prefill-Decode分离推理架构设计 |
| [每日跟踪 (2026-06-*)](../cloud-native/2026-06-12.md) | 每日论文与技术动态追踪 |

## 关联模块
- [分布式操作系统设计](../../05_tools/methodology-tools/README.md) — 集群底层系统支撑
- [运维运营系统](../../05_tools/methodology-tools/README.md) — 集群运维
- [大模型动态](../../05_tools/methodology-tools/README.md) — 训练/推理的模型负载
