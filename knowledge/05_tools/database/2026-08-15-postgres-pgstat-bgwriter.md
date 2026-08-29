# PostgreSQL 后台写入进程：pg_stat_bgwriter 统计分析

> **类型**: knowledge | **日期**: 2026-08-15 | **版本**: v1.0
> **来源**: [CSDN - PostgreSQL pg_stat_bgwriter 视图各个字段详解](https://blog.csdn.net/liumangtuzi888/article/details/154300816)（liumangtuzi888，2025-11-18）
> **配套**: [pg_stat_* 统计视图全景](2026-08-15-postgres-pgstat-overview.md) / [表/索引级统计](2026-08-15-postgres-pgstat-user-tables-indexes.md) / [内存配置建议](2026-08-15-postgres-memory-config.md)

---

## 📑 目录

- [一、结论概要](#一结论概要)
- [二、后台写入机制：谁在刷脏页](#二后台写入机制谁在刷脏页)
- [三、字段体系与含义](#三字段体系与含义)
- [四、性能诊断模型](#四性能诊断模型)
- [五、检查点策略调优](#五检查点策略调优)
- [六、监控案例](#六监控案例)
- [七、易错点与最佳实践](#七易错点与最佳实践)
- [相关文档](#相关文档)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 一、结论概要

`pg_stat_bgwriter` 展示 **background writer（后台写入进程）** 的统计，是分析 I/O 行为、检查点策略和内存刷写效率的核心视图：

| 维度 | 关键字段 | 诊断价值 |
|:-----|:---------|:---------|
| 检查点 | `checkpoints_timed` / `checkpoints_req` | 计划 vs 请求检查点比例 |
| 缓冲区 | `buffers_clean` / `buffers_backend` / `buffers_checkpoint` | 刷写责任分布 |
| 时间 | `checkpoint_write_time` / `checkpoint_sync_time` | 检查点 I/O 耗时 |
| 后端 | `buffers_backend_fsync` | 后端进程直接 fsync 次数 |

**核心结论**：
1. **刷写三来源**：checkpoint（集中）、bgwriter（后台渐进）、backend（进程内被迫）——**调优目标是让 bgwriter 承担更多**
2. **buffers_backend 过高** = bgwriter 刷写不及时，backend 进程被 I/O 拖累，需调大 `bgwriter_lru_maxpages` 或调小 `bgwriter_delay`
3. **checkpoints_req 占比高** = 检查点经常"被迫提前"，说明 `checkpoint_timeout`/`max_wal_size` 设置不匹配写入负载
4. **统计为累计值**：需配合时间窗口计算速率，单看绝对值无意义

---

## 二、后台写入机制：谁在刷脏页

### 2.1 三条刷写路径

| 路径 | 角色 | 特点 |
|:-----|:-----|:-----|
| bgwriter 进程 | 后台渐进刷 | 低延迟、批量、平滑 I/O |
| checkpoint 进程 | 集中刷 | write + sync 两阶段 |
| backend 进程 | LRU 淘汰被迫刷 | 影响查询延迟，应避免 |

- **bgwriter 角色**：定期把脏页写回磁盘，平滑 I/O 峰值，减少 checkpoint 和 backend 的突发压力
- **checkpoint 角色**：保证崩溃恢复点，集中执行 write 阶段 + sync 阶段
- **backend 角色**：共享缓冲不足需淘汰脏页时直接刷——这是最伤延迟的路径，应尽量避免

### 2.2 相关参数

| 参数 | 默认值 | 作用 |
|:-----|:------:|:-----|
| `bgwriter_delay` | 200ms | bgwriter 轮询间隔 |
| `bgwriter_lru_maxpages` | 100 | 每轮最多刷写页数 |
| `bgwriter_lru_multiplier` | 2.0 | 按需动态调整上限的倍数 |
| `checkpoint_timeout` | 5min | 计划检查点间隔 |
| `max_wal_size` | 1GB | WAL 增长上限（触发请求检查点） |

---

## 三、字段体系与含义

### 3.1 字段分组

| 分组 | 字段 | 含义 |
|:-----|:-----|:-----|
| 检查点计数 | `checkpoints_timed` | 按计划触发的检查点次数 |
| 检查点计数 | `checkpoints_req` | 因 WAL 满等被迫触发的次数 |
| 检查点耗时 | `checkpoint_write_time` | 检查点 write 阶段总耗时（ms） |
| 检查点耗时 | `checkpoint_sync_time` | 检查点 sync 阶段总耗时（ms） |
| 缓冲区 | `buffers_checkpoint` | 检查点期间写出的缓冲区数 |
| 缓冲区 | `buffers_clean` | bgwriter 写出的缓冲区数 |
| 缓冲区 | `buffers_backend` | backend 进程写出的缓冲区数 |
| 后端 | `buffers_backend_fsync` | backend 直接 fsync 的次数 |
| 后端 | `buffers_alloc` | 分配的缓冲区数（含复用） |
| 统计 | `stats_reset` | 上次 reset 时间 |

### 3.2 基础查询

```sql
-- snapshot of bgwriter counters
SELECT checkpoints_timed, checkpoints_req,
       checkpoint_write_time, checkpoint_sync_time,
       buffers_checkpoint, buffers_clean, buffers_backend
FROM pg_stat_bgwriter;

-- reset counters to start a measurement window
SELECT pg_stat_reset();
```

---

## 四、性能诊断模型

### 4.1 刷写责任分布（关键比率）

```sql
-- write responsibility distribution (in window)
SELECT buffers_checkpoint,
       buffers_clean,
       buffers_backend,
       ROUND(100.0 * buffers_backend /
         NULLIF(buffers_checkpoint + buffers_clean + buffers_backend, 0), 1)
         AS backend_pct
FROM pg_stat_bgwriter;
```

| 观察 | 诊断 |
|:-----|:-----|
| `buffers_backend` 占比 > **30%** | bgwriter 刷写不足，backend 频繁被 I/O 阻塞 |
| `buffers_clean` 占比高（> **50%**） | bgwriter 工作正常，I/O 平滑 |
| `buffers_checkpoint` 占比过高 | 检查点集中刷写，可能造成 I/O 尖峰 |

### 4.2 检查点健康度

```sql
-- checkpoint ratio: req/(timed+req) should be low
SELECT checkpoints_timed, checkpoints_req,
       ROUND(100.0 * checkpoints_req /
         NULLIF(checkpoints_timed + checkpoints_req, 0), 1) AS req_pct
FROM pg_stat_bgwriter;
```

- `req_pct` > **30%** → 检查点频繁被迫提前，调大 `max_wal_size` 或 `checkpoint_timeout`

### 4.3 检查点 I/O 耗时

```sql
-- avg sync time per checkpoint (ms)
SELECT checkpoint_sync_time / NULLIF(checkpoints_timed + checkpoints_req, 0)
         AS avg_sync_ms_per_ckpt
FROM pg_stat_bgwriter;
```

- sync 耗时高 → 磁盘 fsync 慢（HDD/网络存储），考虑 `checkpoint_completion_target` 分散 I/O

---

## 五、检查点策略调优

### 5.1 调优目标

**减少 backend 直接刷写 + 平滑检查点 I/O**，具体：

| 场景 | 参数调整 |
|:-----|:---------|
| buffers_backend 高 | `bgwriter_lru_maxpages` 100→300，`bgwriter_delay` 200ms→100ms |
| checkpoints_req 高 | `max_wal_size` 1GB→4GB，`checkpoint_timeout` 5min→10min |
| sync 尖峰 | `checkpoint_completion_target` 0.5→0.9 |
| 写密集 + SSD | 保持 checkpoint_completion_target 较高，分散 I/O |

### 5.2 参数生效与验证

```ini
# postgresql.conf (PG14+ ALTER SYSTEM supported)
bgwriter_lru_maxpages = 300
bgwriter_delay = 100ms
max_wal_size = 4GB
checkpoint_timeout = 10min
checkpoint_completion_target = 0.9
```

```sql
ALTER SYSTEM SET bgwriter_lru_maxpages = 300;
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
-- reload (no restart needed for these)
SELECT pg_reload_conf();
```

调优后观察窗口（建议 24h）：`buffers_backend` 占比应下降，`buffers_clean` 上升，检查点 sync 时间峰值回落。

---

## 六、监控案例

### 6.1 案例：写密集库 I/O 尖峰

**症状**：每 5 分钟一次 I/O 尖峰，应用延迟抖动明显。

**诊断**：

```sql
-- 1. bgwriter responsibility
SELECT buffers_checkpoint, buffers_clean, buffers_backend,
       ROUND(100.0 * buffers_backend /
         NULLIF(buffers_checkpoint + buffers_clean + buffers_backend, 0), 1) AS backend_pct
FROM pg_stat_bgwriter;

-- 2. checkpoint pattern
SELECT checkpoints_timed, checkpoints_req,
       checkpoint_write_time, checkpoint_sync_time
FROM pg_stat_bgwriter;
```

**结论模板**：`buffers_backend` 占比 38%（>30% 阈值），`checkpoints_req` 占比 25%，sync 单次平均 800ms → bgwriter 刷写不足 + 检查点被迫提前。

**动作**：`bgwriter_lru_maxpages=300`、`bgwriter_delay=100ms`、`max_wal_size=4GB`、`checkpoint_completion_target=0.9`，一周后复测。

---

## 七、易错点与最佳实践

### 易错点

| # | 场景 | 坑 | 对策 |
|:-:|:-----|:---|:-----|
| 1 | 看单次快照绝对值 | 累计值无时间维度 | reset 后按窗口计算速率 |
| 2 | 只调 bgwriter 参数 | 忽略 checkpoint 参数联动 | 两个维度一起评估 |
| 3 | 检查点 req 高只调 timeout | 根因可能是 max_wal_size 过小 | 两者配套调整 |
| 4 | 忽略 sync 与 write 分离 | write 快不代表落盘快 | 分别看 write/sync 耗时 |
| 5 | SSD 上仍照搬 HDD 参数 | 存储介质不同最佳值不同 | 按实测 I/O 曲线调 |

### 最佳实践

1. **建立窗口基线**：每次调优前 `pg_stat_reset()`，固定观察 24h 窗口对比
2. **三比率监控**：backend 占比 < **30%**、req 占比 < **30%**、clean 占比 > **50%**
3. **与 IO 监控联动**：bgwriter 统计结合 OS 层 iostat 曲线，确认 I/O 尖峰确实来自 checkpoint
4. **渐变调参**：一次只改 1-2 个参数，避免归因困难
5. **PG16+ 用 pg_stat_io**：更细粒度的 IO 统计可替代部分 bgwriter 分析

---

## 相关文档

- [pg_stat_* 统计视图全景](2026-08-15-postgres-pgstat-overview.md) — 六类视图总览
- [表/索引级统计视图](2026-08-15-postgres-pgstat-user-tables-indexes.md) — 死元组与 VACUUM 决策
- [PostgreSQL 内存配置建议](2026-08-15-postgres-memory-config.md) — shared_buffers 与写入路径
- [PostgreSQL 主从同步状态](2026-08-15-postgres-replication-status.md) — 复制侧 I/O 关联

---

## 参考来源

- CSDN：PostgreSQL pg_stat_bgwriter 视图各个字段详解（liumangtuzi888，2025-11-18）
- [PostgreSQL 官方文档：pg_stat_bgwriter](https://www.postgresql.org/docs/current/monitoring-stats.html#MONITORING-PG-STAT-BGWRITER-VIEW)
- [PostgreSQL 官方文档：后台写入配置](https://www.postgresql.org/docs/current/runtime-config-resource.html#RUNTIME-CONFIG-RESOURCE-BACKGROUND-WRITER)
- [PostgreSQL 官方文档：WAL 配置](https://www.postgresql.org/docs/current/runtime-config-wal.html)

---

## Changelog

- 2026-08-15 v1.0: 首次深度加工（三来源刷写机制 + 字段分组 + 三比率诊断模型 + 检查点调优 + 案例 + 5 易错点）
