# 分布式操作系统设计

> AI集群分布式系统的核心加速与调度能力

## 范围

### 网络加速
- NCCL 优化与拓扑感知
- RoCE / InfiniBand 网络栈
- 集合通信原语优化（AllReduce、AllToAll等）

### 存储加速
- GDR (GPU Direct RDMA)
- GDS (GPU Direct Storage)
- 存储I/O路径优化

### 计算加速
- 拓扑感知调度
- 异构计算协同
- NUMA感知

### 安全增强
- 安全启动与可信执行
- 加密通信
- 访问控制

### 运维运营支撑
- 集群监控与指标采集
- 故障检测与自愈
- 资源管理与调度

## 标签
`分布式系统` `NCCL` `RoCE` `GDR` `GDS` `拓扑感知` `集合通信`

## 关联模块
- [万卡集群与训推优化](../../05_tools/methodology-tools/README.md) — 分布式系统的上层应用
- [运维运营系统](../../05_tools/methodology-tools/README.md) — 运维支撑实现
- [BMC与系统管理](../../05_tools/methodology-tools/README.md) — 硬件管理层面
