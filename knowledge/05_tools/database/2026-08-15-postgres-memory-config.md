# PostgreSQL 内存配置建议

> **类型**: knowledge | **日期**: 2026-08-15 | **版本**: v1.0
> **来源**: PostgreSQL 内存配置建议（素材库，⭐⭐⭐）
> **配套**: [pg_stat_* 统计视图全景](2026-08-15-postgres-pgstat-overview.md) / [pg_stat_bgwriter](2026-08-15-postgres-pgstat-bgwriter.md) / [表/索引级统计](2026-08-15-postgres-pgstat-user-tables-indexes.md)

---

## 📑 目录

- [一、结论概要](#一结论概要)
- [二、数据量估算方法](#二数据量估算方法)
- [三、核心内存参数体系](#三核心内存参数体系)
- [四、配置方案（16GB / 32GB）](#四配置方案16gb--32gb)
- [五、场景适配：查询/更新/导出](#五场景适配查询更新导出)
- [六、内存预算与 OOM 防护](#六内存预算与-oom-防护)
- [七、调优闭环与验证](#七调优闭环与验证)
- [八、易错点与最佳实践](#八易错点与最佳实践)
- [相关文档](#相关文档)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 一、结论概要

PostgreSQL 内存配置的核心是 **四个参数 + 一个预算公式**：

| 参数 | 默认值 | 建议比例 | 作用 |
|:-----|:------:|:---------|:-----|
| `shared_buffers` | 128MB | 物理内存 **25%** | 全局数据缓存 |
| `work_mem` | 4MB | 16-128MB（按并发） | 单操作内存（排序/哈希） |
| `maintenance_work_mem` | 64MB | 物理内存 5-10% | 维护操作（VACUUM/建索引） |
| `effective_cache_size` | 4GB | 物理内存 **50-75%** | 优化器预估总缓存 |

**核心结论**：
1. **shared_buffers 是性能主轴**：OLTP 下缓存命中率目标 ≥ **99%**，16GB 内存 4GB 缓冲可覆盖 90%+ 热点
2. **work_mem 必须按并发折算**：`并发连接数 × work_mem` 是内存预算的上限，超物理内存 → Swap → 性能断崖
3. **effective_cache_size 影响执行计划**：设得大 → 优化器更倾向索引扫描；设得小 → 倾向全表扫描
4. **调优是闭环**：参数 → 观察命中率/慢查询（pg_stat_database / pg_stat_statements）→ 再调整

---

## 二、数据量估算方法

### 2.1 原始数据量

| 计算项 | 公式 | 结果 |
|:-------|:-----|:-----|
| 单行大小 | 列数 × 平均列字节 | 50 × 10B = 500B/行 |
| 总原始数据 | 行数 × 单行大小 | 700 万 × 500B = 3.5GB |

### 2.2 膨胀系数

| 开销项 | 系数 | 700万行示例 |
|:-------|:----:|:-----------:|
| 原始数据 | 1.0× | 3.5GB |
| 索引（3-5 个常用索引） | +30-50% | +2-3.5GB |
| 元数据/事务日志/空洞 | +50-100% | +1.5-3.5GB |
| **总存储** | 1.5-2× | **5-7GB** |

### 2.3 临时内存需求

- 大表排序/哈希连接：1-2GB 临时内存（随查询复杂度上升）
- 全表导出（pg_dump）：需缓存覆盖约 80% 数据量

---

## 三、核心内存参数体系

### 3.1 shared_buffers（全局缓存）

- **职责**：缓存数据页，所有 backend 共享
- **经验值**：物理内存 25%（16GB→4GB，32GB→8GB）
- **过大风险**：超过 25-30% 后收益递减，且 checkpoint 压力增大
- **验证**：`pg_stat_database` 命中率（目标 ≥ 99%）

### 3.2 work_mem（单操作内存）

- **职责**：单个排序/哈希 JOIN 的内存上限（每个操作独立分配）
- **默认 4MB 偏小**：建议 16-128MB（按查询复杂度）
- **⚠️ 预算陷阱**：同一查询多个排序操作 × 并发连接数 = 真实占用
  - 100 连接 × 64MB = **6.4GB**，需纳入总预算

### 3.3 maintenance_work_mem（维护操作）

- **职责**：VACUUM / CREATE INDEX / ALTER TABLE 等维护操作
- **建议**：物理内存 5-10%（可大于 work_mem，因为并发低）
- **收益**：建索引/VACUUM 显著加速，且不挤占业务内存

### 3.4 effective_cache_size（优化器预估值）

- **职责**：告诉优化器"操作系统缓存 + shared_buffers"可用总量
- **建议**：物理内存 50-75%（16GB→12GB，32GB→24GB）
- **影响**：设大 → 优化器认为索引扫描便宜 → 更倾向走索引
- **注意**：不是真实分配，是**提示**，设错不影响正确性只影响计划质量

---

## 四、配置方案（16GB / 32GB）

### 4.1 基础方案（16GB，≤50 连接）

```ini
shared_buffers = 4GB
work_mem = 64MB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
```

- 适合中小并发、常规查询
- work_mem 预算：50 连接 × 64MB = 3.2GB，加上 shared_buffers 4GB + 系统开销，16GB 内安全

### 4.2 优化方案（32GB，100-200 连接）

```ini
shared_buffers = 8GB
work_mem = 128MB
effective_cache_size = 24GB
maintenance_work_mem = 2GB
```

- 适合高并发、复杂 JOIN、频繁导出
- **必须预留 4-6GB 给系统与其他进程**，防 OOM

### 4.3 配置生效

```sql
ALTER SYSTEM SET shared_buffers = '4GB';   -- requires restart
ALTER SYSTEM SET work_mem = '64MB';        -- reload suffices
ALTER SYSTEM SET maintenance_work_mem = '1GB';
ALTER SYSTEM SET effective_cache_size = '12GB';
SELECT pg_reload_conf();                   -- reload (not restart)
```

> ⚠️ `shared_buffers` 修改需要**重启**，其余可 reload。

---

## 五、场景适配：查询/更新/导出

| 场景 | 内存依赖 | 配置要点 |
|:-----|:---------|:---------|
| 简单查询（索引扫描） | shared_buffers | 16GB 内存可达 90%+ 命中率 |
| 复杂查询（JOIN/排序） | work_mem | 100 万行排序 64MB 可避免临时文件 |
| 高并发更新（1000+/s 写） | shared_buffers + WAL | 预留 20% 给 WAL 缓存，建议 32GB |
| 全表导出（pg_dump） | 缓存覆盖率 | 32GB 覆盖 80% 数据量显著加速 |
| VACUUM/建索引 | maintenance_work_mem | 大库维护不阻塞业务 |

### 5.1 临时文件监控（work_mem 不足信号）

```sql
-- temp files indicate spills to disk
SELECT datname, temp_files, temp_bytes
FROM pg_stat_database
WHERE temp_files > 0
ORDER BY temp_bytes DESC;
```

- `temp_bytes` 持续增长 → 排序/哈希溢出磁盘 → 调大 work_mem（注意并发预算）

---

## 六、内存预算与 OOM 防护

### 6.1 总内存预算公式

| 组成 | 说明 |
|:-----|:-----|
| shared_buffers | 全局缓存 |
| 并发峰值连接 × work_mem × 每查询操作数 | 单操作内存总占用 |
| maintenance_work_mem | 维护操作内存 |
| 系统及其他 | 预留 4-6GB |

### 6.2 防 Swap/OOM 检查

| 指标 | 阈值 | 动作 |
|:-----|:-----|:-----|
| 总预算 vs 物理内存 | > 90% | 调低 work_mem 或限连接数 |
| 交换分区使用率 | > 10% 且增长 | 立即降配 |
| OOM Killer 日志 | 出现 postgres | 重启+降配+查连接泄漏 |

### 6.3 连接池的作用

- **pgbouncer 等连接池**可把后端连接压到 20-50，让 work_mem 预算大幅下降
- 应用侧连接（数百）→ 池化后（数十）→ work_mem 可安全设大

---

## 七、调优闭环与验证

### 7.1 调优循环

**调优循环**：配置参数 → reload/restart → 观察指标（命中率/慢查询/临时文件）→ 再调整。

### 7.2 验证指标

```sql
-- 1. cache hit ratio (target > 99%)
SELECT datname,
       ROUND(100.0 * blks_hit / NULLIF(blks_hit + blks_read, 0), 2) AS hit_pct
FROM pg_stat_database
WHERE datname NOT LIKE 'template%';

-- 2. temp file spill
SELECT datname, temp_files, temp_bytes FROM pg_stat_database;

-- 3. slow queries (work_mem / index issues)
SELECT queryid, calls, mean_exec_time
FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;
```

### 7.3 调优顺序建议

1. 先 `shared_buffers`（最大收益，需重启，一次到位）
2. 再 `effective_cache_size`（影响计划质量）
3. 后 `work_mem`（按慢查询和临时文件证据调）
4. 最后 `maintenance_work_mem`（维护窗口收益）

---

## 八、易错点与最佳实践

### 易错点

| # | 场景 | 坑 | 对策 |
|:-:|:-----|:---|:-----|
| 1 | work_mem 盲目调大 | 并发 × 单操作溢出内存 → Swap | 按预算公式折算 |
| 2 | shared_buffers 设 50%+ | 收益递减 + checkpoint 压力 | 保持 25% 左右 |
| 3 | 改完不重启 | shared_buffers 不生效 | 确认参数是否需重启 |
| 4 | 忽略 effective_cache_size | 优化器选错执行计划 | 设为 50-75% |
| 5 | 只看命中率不看临时文件 | 排序溢出未被发现 | temp_bytes 一起监控 |
| 6 | 无连接池裸奔 | 数百连接 × work_mem 爆炸 | pgbouncer 池化 |

### 最佳实践

1. **公式先行**：先算内存预算，再定参数，杜绝拍脑袋
2. **一次改一个参数**：便于归因（先 shared_buffers 再 work_mem）
3. **监控闭环**：命中率 + temp_bytes + 慢查询三指标常驻
4. **连接池标配**：生产环境必须连接池，work_mem 才能安全放大
5. **文档化配置基线**：记录每台实例的参数与理由，便于审计与复制

---

## 相关文档

- [pg_stat_* 统计视图全景](2026-08-15-postgres-pgstat-overview.md) — 命中率/临时文件监控 SQL
- [pg_stat_bgwriter 后台写入](2026-08-15-postgres-pgstat-bgwriter.md) — shared_buffers 脏页刷写与 checkpoint
- [表/索引级统计视图](2026-08-15-postgres-pgstat-user-tables-indexes.md) — 死元组与 VACUUM 内存关系
- [PostgreSQL 主从同步状态](2026-08-15-postgres-replication-status.md) — 从库回放与内存配置

---

## 参考来源

- 素材库：PostgreSQL 内存配置建议（⭐⭐⭐）
- [PostgreSQL 官方文档：资源消耗配置](https://www.postgresql.org/docs/current/runtime-config-resource.html)
- [PostgreSQL 官方文档：查询规划器配置](https://www.postgresql.org/docs/current/runtime-config-query.html)
- [PostgreSQL Wiki：Tuning PostgreSQL](https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server)

---

## Changelog

- 2026-08-15 v1.0: 首次深度加工（数据量估算 + 四参数体系 + 16/32GB 方案 + 预算公式 + OOM 防护 + 调优闭环 + 6 易错点）
