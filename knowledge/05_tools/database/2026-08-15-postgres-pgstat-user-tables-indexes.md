# PostgreSQL 表/索引级统计视图：pg_stat_user_tables 与 pg_stat_user_indexes

> **类型**: knowledge | **日期**: 2026-08-15 | **版本**: v1.0
> **来源**: [CSDN - PgSQL中pg_stat_user_tables和pg_stat_user_objects参数详解](https://blog.csdn.net/liumangtuzi888/article/details/151359515)（liumangtuzi888，2025-11-18）
> **配套**: [pg_stat_* 统计视图全景](2026-08-15-postgres-pgstat-overview.md) / [pg_stat_bgwriter 后台写入](2026-08-15-postgres-pgstat-bgwriter.md) / [核心对象模型](2026-08-15-postgres-core-concepts-db-schema-role.md)

---

## 📑 目录

- [一、结论概要](#一结论概要)
- [二、统计收集器机制：数据从哪来](#二统计收集器机制数据从哪来)
- [三、pg_stat_user_tables 字段体系](#三pg_stat_user_tables-字段体系)
- [四、pg_stat_user_indexes 与索引健康](#四pg_stat_user_indexes-与索引健康)
- [五、核心诊断场景](#五核心诊断场景)
- [六、维护决策：VACUUM 与统计失效](#六维护决策vacuum-与统计失效)
- [七、易错点与最佳实践](#七易错点与最佳实践)
- [相关文档](#相关文档)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 一、结论概要

`pg_stat_user_tables` / `pg_stat_user_indexes` 是 PostgreSQL **统计收集器（Statistics Collector）** 暴露的表级、索引级访问视图，是性能分析、索引设计与维护决策的基石：

| 视图 | 粒度 | 核心用途 |
|:-----|:-----|:---------|
| `pg_stat_user_tables` | 每用户表一行 | 全表扫描/索引扫描比例、DML 量、HOT 更新、死元组 |
| `pg_stat_user_indexes` | 每用户索引一行 | 索引使用率（`idx_scan=0` = 从未使用） |

**核心结论**：
1. **前提开关**：`track_counts` 必须为 `on`（默认开启），`SHOW track_counts;` 可验证
2. **数据累积规则**：从最后一次 `pg_stat_reset()` 或数据库启动开始累积，是**累计计数器**而非瞬时值
3. **三大诊断价值**：索引设计是否合理（seq/idx 扫描比）、是否需要 VACUUM（死元组数）、统计信息是否过期（last_analyze）
4. **统计视图是近似值**：`n_live_tup`/`n_dead_tup` 是估算（抽样），精确值需 `VACUUM` 后或 `ANALYZE` 校准

---

## 二、统计收集器机制：数据从哪来

### 2.1 架构与开关

| 环节 | 说明 |
|:-----|:-----|
| PostgreSQL backend | 各会话产生 DML/扫描事件 |
| Statistics Collector | 独立后台进程，定期汇总（默认每 500ms） |
| pg_stat_* 视图 | 内存 + pg_stat_tmp 临时文件，对外可查 |

- 由独立的 **stats collector 后台进程** 汇总各 backend 上报的计数
- 关键参数：`track_counts`（默认 on）、`track_activities`（默认 on）
- 计数器在 `pg_stat_reset()` 或数据库重启时归零

### 2.2 验证是否在收集

```sql
-- check collection is enabled
SHOW track_counts;
SHOW track_activities;

-- reset counters (DBA only)
SELECT pg_stat_reset();
```

---

## 三、pg_stat_user_tables 字段体系

### 3.1 字段分组

| 分组 | 字段 | 含义 |
|:-----|:-----|:-----|
| 标识 | `relid` / `schemaname` / `relname` | OID / 模式名 / 表名 |
| 扫描 | `seq_scan` / `seq_tup_read` | 全表扫描次数 / 读取的活元组数 |
| 扫描 | `idx_scan` / `idx_tup_fetch` | 索引扫描次数 / 读取的活元组数 |
| DML | `n_tup_ins` / `n_tup_upd` / `n_tup_del` | 插入 / 更新 / 删除行数 |
| DML | `n_tup_hot_upd` | HOT（Heap-Only Tuple）更新行数 |
| 元组 | `n_live_tup` / `n_dead_tup` | 估算的活 / 死元组数（非精确） |
| 维护 | `last_vacuum` / `last_autovacuum` | 最后手动 / 自动 VACUUM 时间 |
| 维护 | `last_analyze` / `last_autoanalyze` | 最后手动 / 自动 ANALYZE 时间 |

### 3.2 HOT 更新（重要优化概念）

- **HOT 机制**：仅堆元组更新（被更新列不在索引列中时），**无需更新索引项**，显著降低写放大
- `n_tot_hot_upd` 占比高 = 表设计利于 HOT（索引列少且更新不涉及）
- 占比低 → 检查是否频繁更新索引列，或索引过多

### 3.3 基础查询

```sql
-- top tables by sequential scan (potential missing index)
SELECT schemaname, relname, seq_scan, seq_tup_read, idx_scan
FROM pg_stat_user_tables
ORDER BY seq_tup_read DESC
LIMIT 20;

-- table write volume overview
SELECT relname,
       n_tup_ins  AS inserts,
       n_tup_upd  AS updates,
       n_tup_del  AS deletes,
       n_tup_hot_upd AS hot_updates
FROM pg_stat_user_tables
ORDER BY (n_tup_ins + n_tup_upd + n_tup_del) DESC;
```

---

## 四、pg_stat_user_indexes 与索引健康

### 4.1 未使用索引识别

```sql
-- unused indexes (idx_scan = 0)
SELECT schemaname, relname AS table, indexrelname AS index_name, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY relname;
```

- `idx_scan = 0` = 从未被查询使用 → 候选删除（先确认无 `pg_stat_reset()` 后短周期误报）

### 4.2 索引效率指标

| 指标 | 计算 | 判断 |
|:-----|:-----|:-----|
| 索引使用率 | 使用该索引的表 `idx_scan` 总数 | 低 → 索引设计问题 |
| 全表扫描占比 | `seq_scan / (seq_scan + idx_scan)` | > **70%** 且表大 → 缺索引信号 |
| 冗余索引 | 前缀相同的多索引 | 保留最左匹配的一个 |

### 4.3 表级索引诊断 SQL

```sql
-- per-table: seq vs idx scan ratio
SELECT relname,
       seq_scan,
       idx_scan,
       ROUND(100.0 * seq_scan / NULLIF(seq_scan + idx_scan, 0), 1) AS seq_pct
FROM pg_stat_user_tables
WHERE seq_scan + idx_scan > 0
ORDER BY seq_pct DESC
LIMIT 20;
```

---

## 五、核心诊断场景

### 5.1 场景一：慢查询是否缺索引

```sql
-- find tables with high seq_scan but low row count expectation
SELECT relname, seq_scan, seq_tup_read, n_live_tup
FROM pg_stat_user_tables
WHERE seq_tup_read > 100000      -- many rows read per scan
ORDER BY seq_tup_read DESC;
```

- `seq_tup_read` 大 + `n_live_tup` 大 → 表大且频繁全表扫 → **加索引**
- 加索引后用 `pg_stat_reset()` 清计数，观察新周期 `idx_scan` 是否上升

### 5.2 场景二：写放大与 HOT 健康

```sql
-- HOT ratio per table (higher is better)
SELECT relname,
       n_tup_upd,
       n_tup_hot_upd,
       ROUND(100.0 * n_tup_hot_upd / NULLIF(n_tup_upd, 0), 1) AS hot_pct
FROM pg_stat_user_tables
WHERE n_tup_upd > 1000
ORDER BY hot_pct ASC
LIMIT 20;
```

- HOT 占比 < **30%** → 检查索引列更新频率与索引数量

### 5.3 场景三：死元组膨胀预警

```sql
-- tables with heavy dead tuple accumulation
SELECT relname,
       n_live_tup,
       n_dead_tup,
       ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup, 0), 1) AS dead_pct,
       last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY n_dead_tup DESC;
```

- 死元组 / 活元组 > **20%** → autovacuum 可能落后，需人工 VACUUM 或调参

---

## 六、维护决策：VACUUM 与统计失效

### 6.1 VACUUM 决策链

```sql
-- when was the last vacuum/analyze?
SELECT relname, last_vacuum, last_autovacuum, last_analyze, last_autoanalyze
FROM pg_stat_user_tables
ORDER BY last_autovacuum ASC NULLS FIRST
LIMIT 20;
```

| 观察 | 结论 | 动作 |
|:-----|:-----|:-----|
| `n_dead_tup` 持续增长 | autovacuum 未跟上写入 | 手工 `VACUUM` / 调 `autovacuum_vacuum_scale_factor` |
| `last_analyze` 很久未更新 | 统计信息过期，执行计划可能劣化 | `ANALYZE` 或 `autovacuum_analyze_scale_factor` |
| `last_autovacuum` 为 NULL | 从未自动清理 | 检查 autovacuum 是否被禁用 |

### 6.2 统计准确性注意

- `n_live_tup`/`n_dead_tup` 是**估算值**：来自统计采样，`ANALYZE` 后刷新
- 高并发下估算可能偏差大，精确行数用 `SELECT count(*)` 或 `VACUUM` 后读取

---

## 七、易错点与最佳实践

### 易错点

| # | 场景 | 坑 | 对策 |
|:-:|:-----|:---|:-----|
| 1 | 忘开 track_counts | 视图全空或全 0 | `SHOW track_counts` 先验证 |
| 2 | 误读累计值 | 把累计 seq_scan 当瞬时 | 用 `pg_stat_reset()` 后观察增量 |
| 3 | idx_scan=0 直接删 | 刚 reset 或冷数据误判 | 观察至少一个业务周期 |
| 4 | 死元组只看一次 | 瞬时值无趋势 | 定时采样存历史对比 |
| 5 | 忽略 pg_stat_user_* | 误用 pg_stat_all_*（含系统表） | 用户分析用 user 系列 |

### 最佳实践

1. **建立统计基线**：定期（每周）导出 `pg_stat_user_tables` 快照，对比周环比发现异常
2. **索引治理月度巡检**：未使用索引清单 + 冗余索引清理，控制写放大
3. **VACUUM 预警自动化**：死元组占比 > **20%** 触发告警
4. **HOT 率纳入监控**：写密集表 HOT 占比下降 = 索引设计退化的早期信号
5. **计数周期化**：`pg_stat_reset()` 与业务周期对齐（如每日 0 点），便于环比

---

## 相关文档

- [pg_stat_* 统计视图全景](2026-08-15-postgres-pgstat-overview.md) — 6 类统计视图总览与联合诊断
- [pg_stat_bgwriter 后台写入](2026-08-15-postgres-pgstat-bgwriter.md) — 检查点与缓冲区刷写统计
- [PostgreSQL 核心对象模型](2026-08-15-postgres-core-concepts-db-schema-role.md) — 表/索引对象体系
- [PostgreSQL 内存配置建议](2026-08-15-postgres-memory-config.md) — shared_buffers 与写入路径（配套）

---

## 参考来源

- CSDN：PgSQL中pg_stat_user_tables和pg_stat_user_objects参数详解（liumangtuzi888，2025-11-18）
- [PostgreSQL 官方文档：统计收集器](https://www.postgresql.org/docs/current/monitoring-stats.html)
- [PostgreSQL 官方文档：pg_stat_user_tables](https://www.postgresql.org/docs/current/monitoring-stats.html#MONITORING-PG-STAT-ALL-TABLES-VIEW)
- [PostgreSQL 官方文档：VACUUM/ANALYZE](https://www.postgresql.org/docs/current/sql-vacuum.html)

---

## Changelog

- 2026-08-15 v1.0: 首次深度加工（字段分组 + HOT 机制 + 未使用索引识别 + 4 诊断场景 + VACUUM 决策链 + 5 易错点）
