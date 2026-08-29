# PostgreSQL 核心统计视图（pg_stat_*）详解与实战指南

> **类型**: knowledge | **日期**: 2026-08-15 | **版本**: v1.0
> **来源**: [CSDN - pg_stat 视图介绍](https://yueludanfeng.blog.csdn.net/article/details/154261824)（yueludanfeng，2025-11-18）
> **配套**: [表/索引级统计](2026-08-15-postgres-pgstat-user-tables-indexes.md) / [pg_stat_bgwriter](2026-08-15-postgres-pgstat-bgwriter.md) / [主从同步状态](2026-08-15-postgres-replication-status.md)

---

## 📑 目录

- [一、结论概要](#一结论概要)
- [二、统计视图六分类](#二统计视图六分类)
- [三、pg_stat_activity：会话与锁监控](#三pg_stat_activity会话与锁监控)
- [四、pg_stat_database：数据库级健康](#四pg_stat_database数据库级健康)
- [五、pg_stat_statements：慢查询利器](#五pg_stat_statements慢查询利器)
- [六、其他关键视图速览](#六其他关键视图速览)
- [七、联合诊断案例](#七联合诊断案例)
- [八、易错点与最佳实践](#八易错点与最佳实践)
- [相关文档](#相关文档)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 一、结论概要

`pg_stat_*` 系列视图覆盖 PostgreSQL **六类监控维度**：会话、数据库、语句、表/索引、后台进程、复制与维护进度。它们是性能调优的第一现场：

| 视图 | 监控对象 | 高频用途 |
|:-----|:---------|:---------|
| `pg_stat_activity` | 当前会话 | 长事务、锁等待、阻塞源 |
| `pg_stat_database` | 数据库级 | 缓存命中率、事务、死锁 |
| `pg_stat_statements` | SQL 语句 | 慢查询、执行频次、IO |
| `pg_stat_user_tables` / `_indexes` | 表/索引 | 扫描方式、索引使用率 |
| `pg_stat_bgwriter` | 后台写进程 | 检查点、缓冲区刷写 |
| `pg_stat_replication` / `_progress_*` | 复制/维护 | 主从延迟、VACUUM 进度 |

**核心结论**：
1. **pg_stat_activity 是锁与长事务排查的第一入口**：`state` + `wait_event` + `pg_blocking_pids()` 三步定位阻塞
2. **pg_stat_statements 需要显式启用**：`shared_preload_libraries = 'pg_stat_statements'` + 重启，是慢查询分析的必备扩展
3. **联合查询 > 单视图**：真实瓶颈往往是"长事务 + 锁等待 + 慢 SQL"的组合，需多视图交叉
4. **统计视图只反映"已发生"**：是事后诊断工具，事前预防靠参数与架构设计

---

## 二、统计视图六分类

### 2.1 分类总览

| 类别 | 视图 |
|:-----|:-----|
| 连接与会话 | pg_stat_activity / pg_stat_ssl |
| 数据库级 | pg_stat_database / pg_stat_database_conflicts |
| 语句级 | pg_stat_statements / pg_stat_user_functions |
| 表/索引级 | pg_stat_all_tables / pg_stat_user_indexes |
| 后台进程 | pg_stat_bgwriter / pg_stat_io (PG16+) |
| 复制/维护 | pg_stat_replication / pg_stat_progress_* |

### 2.2 关键原则

- **user vs all**：`pg_stat_user_*` 过滤系统表，业务分析优先用 user 系列
- **累计 vs 瞬时**：多数为累计计数器，`pg_stat_reset()` 控制统计窗口
- **启用开关**：`track_counts`、`track_activities`、`track_io_timing`（IO 统计需显式开启）

```sql
-- verify tracking config
SHOW track_counts;
SHOW track_activities;
SHOW track_io_timing;   -- off by default in many distros
```

---

## 三、pg_stat_activity：会话与锁监控

### 3.1 核心字段

| 字段 | 含义 | 排障价值 |
|:-----|:-----|:---------|
| `pid` | 后端进程 ID | 与 OS 进程对应（pg_backend_pid） |
| `state` | active / idle / idle in transaction | 长事务识别 |
| `query` | 当前执行的 SQL | 定位具体语句 |
| `wait_event_type` | Lock / IO / Activity 等 | 等待类型分类 |
| `wait_event` | 具体等待事件 | 锁名 / IO 对象 |
| `xact_start` / `query_start` | 事务/查询开始时间 | 时长计算 |
| `client_addr` | 客户端 IP | 来源定位 |

### 3.2 锁等待与阻塞排查（三步法）

```sql
-- step 1: find sessions waiting on locks
SELECT pid, state, wait_event_type, wait_event, query
FROM pg_stat_activity
WHERE wait_event_type = 'Lock';

-- step 2: find blocker of a specific pid
SELECT pg_blocking_pids(<blocked_pid>);

-- step 3: inspect the blocker session
SELECT pid, state, xact_start, query
FROM pg_stat_activity
WHERE pid = ANY(pg_blocking_pids(<blocked_pid>));
```

- `idle in transaction` 状态是最常见的"隐形锁持有者"——事务未提交/回滚，锁不释放

### 3.3 长事务识别

```sql
-- transactions running longer than 5 minutes
SELECT pid, state, xact_start,
       now() - xact_start AS xact_age,
       wait_event_type, query
FROM pg_stat_activity
WHERE state <> 'idle'
  AND xact_start < now() - interval '5 minutes'
ORDER BY xact_start;
```

---

## 四、pg_stat_database：数据库级健康

### 4.1 核心指标

| 字段 | 含义 | 关注点 |
|:-----|:-----|:-------|
| `numbackends` | 当前连接数 | 连接池水位 |
| `xact_commit` / `xact_rollback` | 提交/回滚事务数 | 回滚率高 = 应用错误 |
| `blks_read` / `blks_hit` | 磁盘读 / 缓冲命中 | 缓存命中率计算 |
| `tup_returned` / `tup_fetched` | 返回/取回元组 | 查询量 |
| `deadlocks` | 死锁次数 | 应用锁设计问题 |
| `temp_files` / `temp_bytes` | 临时文件数/大小 | 排序/哈希溢出 |

### 4.2 缓存命中率计算

```sql
-- buffer cache hit ratio per database
SELECT datname,
       ROUND(100.0 * blks_hit / NULLIF(blks_hit + blks_read, 0), 2) AS hit_ratio_pct,
       blks_read,
       temp_bytes
FROM pg_stat_database
WHERE datname NOT IN ('template0', 'template1')
ORDER BY hit_ratio_pct;
```

- 健康基准：命中率 > **99%**（OLTP）；低于 **95%** 需检查 shared_buffers 或查询模式
- `temp_bytes` 巨大 → 排序/聚合溢出到磁盘，需优化 SQL 或增大 work_mem

### 4.3 死锁监控

```sql
-- deadlock count trend
SELECT datname, deadlocks
FROM pg_stat_database
ORDER BY deadlocks DESC;
```

- 死锁持续增长 → 应用锁顺序不一致，需代码层修复而非数据库调参

---

## 五、pg_stat_statements：慢查询利器

### 5.1 启用步骤（需要重启）

```ini
# postgresql.conf
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.max = 10000
pg_stat_statements.track = all
```

```sql
-- enable extension (after restart)
CREATE EXTENSION pg_stat_statements;
```

### 5.2 核心字段与慢查询分析

| 字段 | 含义 | 用途 |
|:-----|:-----|:-----|
| `queryid` | SQL 指纹 | 归一化去重 |
| `calls` | 执行次数 | 热语句 |
| `total_exec_time` | 总耗时 | 累计成本 |
| `mean_exec_time` | 平均耗时 | 单次成本 |
| `rows` | 返回行数 | 效率 |
| `shared_blks_read` / `shared_blks_hit` | 缓存读 | IO 特征 |

```sql
-- top 20 slowest statements by total time
SELECT queryid,
       calls,
       ROUND(total_exec_time / 1000.0, 2) AS total_ms,
       ROUND(mean_exec_time, 2) AS mean_ms,
       LEFT(query, 80) AS query_preview
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;

-- statements with poor cache behavior
SELECT queryid, calls,
       shared_blks_read, shared_blks_hit,
       ROUND(100.0 * shared_blks_hit / NULLIF(shared_blks_hit + shared_blks_read, 0), 1) AS hit_pct
FROM pg_stat_statements
WHERE shared_blks_read + shared_blks_hit > 0
ORDER BY shared_blks_read DESC
LIMIT 20;
```

### 5.3 注意事项

- `pg_stat_statements_reset()` 可清零，建议与发布/压测周期对齐
- query 字段可能含敏感信息，审计时注意脱敏

---

## 六、其他关键视图速览

| 视图 | 用途 | 关键字段 |
|:-----|:-----|:---------|
| `pg_stat_replication` | 主从同步状态 | `sent_lsn` / `write_lsn` / `replay_lsn`、`state` |
| `pg_stat_subscription` | 逻辑订阅状态 | `pid`、`last_msg_send_time` |
| `pg_stat_progress_vacuum` | VACUUM 进度 | `phase`、`heap_blks_scanned` / `heap_blks_total` |
| `pg_stat_progress_create_index` | 建索引进度 | `phase`、`tuples_done` |
| `pg_stat_io`（PG16+） | IO 细分统计 | `read` / `write` 时间、`extend` |
| `pg_stat_user_functions` | 函数调用统计 | `calls`、`total_time`、`self_time` |

```sql
-- vacuum progress of current maintenance
SELECT pid, datname, phase,
       heap_blks_scanned, heap_blks_total
FROM pg_stat_progress_vacuum;
```

---

## 七、联合诊断案例

### 7.1 案例：线上"卡死"排查

**症状**：某业务 SQL 响应从 50ms 恶化到 5s+。

**诊断链**：

```sql
-- 1. long transactions first
SELECT pid, state, xact_start, now() - xact_start AS age, query
FROM pg_stat_activity
WHERE state = 'idle in transaction'
ORDER BY xact_start;

-- 2. lock waiters + blockers
SELECT pid, wait_event_type, wait_event,
       pg_blocking_pids(pid) AS blockers
FROM pg_stat_activity
WHERE wait_event_type = 'Lock';

-- 3. per-statement cost
SELECT queryid, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
ORDER BY total_exec_time DESC LIMIT 10;

-- 4. database health snapshot
SELECT datname, numbackends, deadlocks,
       ROUND(100.0 * blks_hit / NULLIF(blks_hit + blks_read, 0), 2) AS hit_pct
FROM pg_stat_database;
```

**结论模板**：`idle in transaction` 持锁 8 分钟 → 阻塞 3 个会话 → 对应慢 SQL 是 `UPDATE orders...`（总耗时占比 40%）→ 应用层未及时提交事务，且该表 HOT 率低、死元组 > 20% 需 VACUUM。

### 7.2 诊断优先级

1. 先看 `pg_stat_activity`（有没有锁/长事务）
2. 再看 `pg_stat_statements`（哪些 SQL 最贵）
3. 后看 `pg_stat_user_tables`（表层根因：缺索引/膨胀）
4. 最后 `pg_stat_database`（全局健康，排除容量问题）

---

## 八、易错点与最佳实践

### 易错点

| # | 场景 | 坑 | 对策 |
|:-:|:-----|:---|:-----|
| 1 | 忘装 pg_stat_statements | 查不到语句级数据 | 预装扩展 + 重启 |
| 2 | 忘开 track_io_timing | IO 时间全 0 | `ALTER SYSTEM SET track_io_timing = on` |
| 3 | 单看累计值 | 历史累计掩盖近期恶化 | 周期 reset 或算增量 |
| 4 | 忽略 idle in transaction | 最常见隐形锁源 | 专门查询该状态 |
| 5 | 死锁只看次数 | 死锁是结果不是原因 | 结合日志看死锁详情 |

### 最佳实践

1. **监控看板固化**：把命中率、死锁数、长事务、慢 SQL Top-N 纳入常规巡检
2. **统计周期管理**：发布/压测前 `pg_stat_reset()`，事后对比增量
3. **慢查询基线化**：每周导出 pg_stat_statements Top-50 对比趋势
4. **告警阈值**：缓存命中率 < **95%**、死元组占比 > **20%**、长事务 > **5min** 触发告警
5. **扩展预装**：新实例初始化即装 pg_stat_statements + pg_stat_io（PG16+）

---

## 相关文档

- [表/索引级统计视图](2026-08-15-postgres-pgstat-user-tables-indexes.md) — seq/idx 扫描与索引健康
- [pg_stat_bgwriter 后台写入](2026-08-15-postgres-pgstat-bgwriter.md) — 检查点与缓冲区统计
- [主从同步状态查看](2026-08-15-postgres-replication-status.md) — pg_stat_replication 实战
- [PostgreSQL 内存配置建议](2026-08-15-postgres-memory-config.md) — shared_buffers/work_mem 与命中率关系

---

## 参考来源

- CSDN：pg_stat 视图介绍（yueludanfeng，2025-11-18）
- [PostgreSQL 官方文档：监控统计](https://www.postgresql.org/docs/current/monitoring-stats.html)
- [PostgreSQL 官方文档：pg_stat_statements](https://www.postgresql.org/docs/current/pgstatstatements.html)
- [PostgreSQL 官方文档：查看锁](https://www.postgresql.org/docs/current/monitoring-locks.html)

---

## Changelog

- 2026-08-15 v1.0: 首次深度加工（六分类总览 + activity 锁排查三步法 + database 命中率/死锁 + statements 启用与慢查询 + 联合诊断案例 + 5 易错点）
