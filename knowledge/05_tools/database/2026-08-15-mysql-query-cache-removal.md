# MySQL 8.0 查询缓存（Query Cache）移除深度解析：从架构史到替代方案

> **概要**: 深度解析 MySQL 8.0 彻底移除 Query Cache 的技术决策。从查询缓存的架构设计（全局共享内存+哈希表）、失效机制（表级粒度）、并发模型（全局锁）三个层面解释"为什么被移除"，并给出替代方案（应用层多级缓存 Cache-Aside）与性能验证方法。核心结论：Query Cache 是 MySQL 4.0 时代的产物，其设计假设（读多写少、结果集稳定）与 8.0 时代的工作负载（高并发写入、大结果集）根本冲突。
>
> **关键词**: MySQL · Query Cache · 查询缓存 · 架构演进 · Cache-Aside · 多级缓存

---

## 📑 目录

- [1. 结论先行：一次"正确但迟到"的删除](#1-结论先行一次正确但迟到的删除)
- [2. Query Cache 工作原理（5.7 及更早）](#2-query-cache-工作原理57-及更早)
- [3. 移除的三重根因（架构级分析）](#3-移除的三重根因架构级分析)
- [4. 实验验证：如何确认你的版本无 Query Cache](#4-实验验证如何确认你的版本无-query-cache)
- [5. MySQL 8.0 中的其他缓存机制（≠Query Cache）](#5-mysql-80-中的其他缓存机制query-cache)
- [6. 替代方案：应用层多级缓存（推荐架构）](#6-替代方案应用层多级缓存推荐架构)
- [7. 性能调优：围绕 InnoDB Buffer Pool 的正确姿势](#7-性能调优围绕-innodb-buffer-pool-的正确姿势)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 1. 结论先行：一次"正确但迟到"的删除

- **MySQL 8.0（2018 发布）彻底移除 Query Cache**：相关参数（`query_cache_size`/`query_cache_type`/`query_cache_limit`）与状态变量（`Qcache_*`）全部删除，官方文档明确 "The Query Cache has been removed from MySQL 8.0" [来源: MySQL 8.0 Release Notes]
- **移除本质**：Query Cache 的设计前提（①读多写少 ②结果集小且稳定 ③单机单实例）在 8.0 时代已失效；其全局锁与表级失效粒度在**高并发写入**下不仅无益，反而成为瓶颈
- **替代结论**：数据库层不再承担结果缓存职责，**缓存上移到应用层**（L1 本地缓存 + L2 Redis/Memcached），数据库专注其本职——数据存储与一致性

---

## 2. Query Cache 工作原理（5.7 及更早）

### 2.1 执行链路中的位置

**MySQL ≤5.7 查询执行链路**（Query Cache 位于解析器之前，命中则跳过解析与执行）：

```
Client -> Connector -> [Query Cache hit? return directly]
                    -> Parser -> Optimizer -> Executor -> Storage Engine
                       (miss: continue execution, write result to cache)
```

**MySQL 8.0 查询执行链路**（无查询缓存环节）：

```
Client -> Connector -> Parser -> Optimizer -> Executor -> Storage Engine
```

### 2.2 工作机制

| 环节 | 机制 |
|:-----|:-----|
| 命中判定 | SELECT 语句文本精确哈希匹配（大小写/空格敏感） |
| 缓存内容 | 查询结果集（内存中的结果行） |
| 写入时机 | 查询执行完成后写入全局缓存区 |
| 缓存区 | 全局共享内存区（`query_cache_size` 控制，默认 1MB，生产常见 64-512MB） |
| 失效粒度 | **表级**：任意表发生 INSERT/UPDATE/DELETE/DDL，该表所有缓存条目全部失效 |

### 2.3 使用前提（官方建议启用条件）

| 条件 | 说明 |
|:-----|:-----|
| 读多写少 | 缓存命中率 > 70% 才有正收益 |
| 查询重复度高 | 完全相同的 SQL 反复执行 |
| 结果集小 | 大结果集缓存浪费内存且命中率低 |
| 单实例 | 读写分离/多实例下缓存无法共享 |

---

## 3. 移除的三重根因（架构级分析）

### 3.1 根因一：全局锁争用（并发瓶颈）

- Query Cache 是**全局共享内存区**，任何写操作（INSERT/UPDATE/DELETE/DDL）都需要获取**全局互斥锁**来使缓存失效
- 高并发下：写操作频繁抢锁 → 读操作等待锁 → 缓存命中带来的收益被锁开销抵消，甚至**负收益**
- 量化：写多场景实测命中率 **<20%**，且锁等待时间超过缓存收益 [来源: MySQL Performance Blog, Percona]

### 3.2 根因二：失效粒度粗糙（表级失效）

- 失效单位是**整张表**而非单行：任意行变更 → 该表所有缓存条目作废
- 高频更新表（如订单状态表）缓存命中率趋近于 0，缓存维护成本（失效扫描+内存回收）却持续存在
- 对比：现代缓存（Redis）支持**键级精确失效**，由应用主动控制

### 3.3 根因三：内存管理缺陷

- 结果集大小不一 → **内存碎片严重**，缓存区利用率低
- 缓存维护与清理（LRU 淘汰、碎片整理）耗时高
- 缓存区与 InnoDB Buffer Pool 争抢内存，挤占真正有价值的**数据页缓存**

### 3.4 设计哲学转变

| 维度 | 5.7 时代 | 8.0 时代 |
|:-----|:---------|:---------|
| 缓存位置 | 数据库内核 | 应用层/中间件 |
| 失效精度 | 表级 | 键级/逻辑级 |
| 扩展性 | 单实例 | 分布式（Redis Cluster） |
| 数据一致性 | 数据库自行保证 | 应用层 Cache-Aside/CDC 协同 |

---

## 4. 实验验证：如何确认你的版本无 Query Cache

```sql
-- verify: does the parameter exist?
SHOW VARIABLES LIKE 'query_cache%';
```

| 版本 | 结果 |
|:-----|:-----|
| MySQL 5.7 | 返回 `query_cache_size`、`query_cache_type`、`query_cache_limit` 等参数 |
| MySQL 8.0 | 返回空集，或报错 `Unknown system variable 'query_cache_size'` |

```sql
-- sanity check: status variables also removed in 8.0
SHOW STATUS LIKE 'Qcache%';   -- 8.0: empty set
```

---

## 5. MySQL 8.0 中的其他缓存机制（≠Query Cache）

| 缓存类型 | 缓存内容 | 是否等价 Query Cache |
|:---------|:---------|:---------------------|
| **InnoDB Buffer Pool** | 数据页/索引页（16KB 页） | ❌ 不是结果缓存，是页缓存 |
| Prepared Statement Cache | 预编译语句的执行计划 | ❌ 计划缓存，非结果 |
| Table Cache | 已打开表句柄（table_open_cache） | ❌ 元数据级 |
| Metadata Cache | 数据字典元信息 | ❌ 元数据级 |
| Adaptive Hash Index (AHI) | 热点数据的哈希索引 | ❌ 索引加速，非结果 |

**关键澄清**：InnoDB Buffer Pool 是 MySQL 性能的**第一支柱**（默认 128MB，生产通常设为物理内存 60-80%），缓存的是**数据页**——查询仍需执行计划、读取并处理页内行。它解决"磁盘 IO"问题，不解决"重复计算"问题。

---

## 6. 替代方案：应用层多级缓存（推荐架构）

### 6.1 Cache-Aside 模式（读侧）

**架构流程**：

```
Client -> App -> [L1 local cache hit?] -> return
              | miss
         [L2 Redis/Memcached hit?] -> return + backfill L1
              | miss
         MySQL 8.0 query -> write L2 + L1 -> return
```

**伪代码**：

```python
def get_user_profile(uid):
    key = "user:%d:v%d" % (uid, get_version(uid))
    if cache.exists(key):          # Redis
        return cache.get(key)
    row = mysql.query("SELECT * FROM user WHERE id=%s", uid)
    cache.setex(key, ttl=600, value=row)
    return row
```

### 6.2 缓存 Key 设计要点

| 要点 | 实践 |
|:-----|:-----|
| 唯一性 | 主键或业务唯一键 |
| 版本化 | `user:123:v27` —— 数据版本变更时 Key 自动失效，避免脏读 |
| 大结果集 | 分页存储（`list:page:1`、`list:page:2`） |
| 过期策略 | TTL + 惰性删除（简单）；精确失效（可靠） |

### 6.3 失效策略对比

| 策略 | 实现 | 优点 | 缺点 |
|:-----|:-----|:-----|:-----|
| TTL + 惰性删除 | 设置过期时间，读时检查 | 简单、零侵入 | 存在短暂脏数据窗口 |
| 精确失效 | 写库后主动删 Key（双写） | 一致性最强 | 需业务代码配合，易漏 |
| **Binlog 订阅失效（推荐）** | Canal/Debezium 监听 binlog → 失效对应 Key | 与业务解耦、可靠 | 引入 CDC 组件，架构+1 |

### 6.4 写侧策略（Cache-Aside 写路径）

```
Write request -> 1. UPDATE MySQL (commit) -> 2. DELETE cache key (not update)
```

> 原则：**写删读建**（write-through 更新缓存易产生并发脏读，delete 更安全）。双写一致性可参考 Cache-Aside 经典模式。

### 6.5 多级缓存执行链路（完整版）

| 层级 | 存储 | 命中延迟 | 容量 | 说明 |
|:-----|:-----|:---------|:-----|:-----|
| L1 | 应用本地（Caffeine/本地 Map） | <1ms | 小（GB 级） | 进程内，无网络 |
| L2 | Redis/Memcached | 1-5ms | 大（百 GB~TB） | 分布式共享 |
| L3 | MySQL Buffer Pool | 5-50ms | 内存大小 | 数据页缓存 |
| L4 | 磁盘 | 5-50ms+ | 无限 | 兜底 |

---

## 7. 性能调优：围绕 InnoDB Buffer Pool 的正确姿势

> Query Cache 已死，**Buffer Pool 才是 MySQL 8.0 性能主战场**。

### 7.1 核心监控命令

```sql
-- Buffer Pool hit rate (target >99%)
SHOW ENGINE INNODB STATUS\G

-- slow query analysis (EXPLAIN ANALYZE shows real execution time)
EXPLAIN ANALYZE SELECT ...;
```

### 7.2 关键参数

| 参数 | 默认 | 建议 | 说明 |
|:-----|:-----|:-----|:-----|
| `innodb_buffer_pool_size` | 128MB | 物理内存 60-80% | 数据页缓存总大小 |
| `innodb_buffer_pool_instances` | 8 | 池数 ≥ 并发度/2 | 减少锁竞争（>1GB 时生效） |
| `table_open_cache` | 4000 | 按表数量调整 | 已打开表句柄缓存 |
| `thread_cache_size` | 9 | 按连接波动调整 | 线程复用缓存 |
| `innodb_adaptive_hash_index` | ON | 默认开启 | AHI 加速热点等值查询 |

### 7.3 应用层缓存指标监控

| 指标 | 含义 | 告警阈值 |
|:-----|:-----|:---------|
| 缓存命中率 | 命中/总请求 | <90% 需排查 Key 设计 |
| 缓存穿透 | 查询不存在的数据 | 需布隆过滤器/空值缓存 |
| 缓存击穿 | 热点 Key 过期瞬间 | 互斥锁/逻辑过期 |
| 缓存雪崩 | 大量 Key 同时过期 | TTL 加随机抖动 |

---

## 参考文件

### 内部知识库引用

- [PostgreSQL vs MySQL 深度对比](2026-08-15-postgres-vs-mysql-deep-comparison.md) — 双库架构差异（同批导入）
- [PostgreSQL 内存配置建议](2026-08-15-postgres-memory-config.md) — PG 侧内存优化对照（同批导入）

### 外部资料引用

- MySQL 8.0 Release Notes（Query Cache Removed）— https://dev.mysql.com/doc/relnotes/mysql/8.0/en/news-8-0-0.html
- MySQL 8.0 Reference Manual — Query Cache — https://dev.mysql.com/doc/refman/8.0/en/query-cache.html
- Percona: "MySQL Query Cache: Still a Bottleneck?" — https://www.percona.com/blog/
- 原文: MySQL 8 查询缓存已废除详解：从架构、历史到替代方案 — https://juejin.cn/post/7564246514988236826

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:---------|
| 2026-08-15 | v1.0 | 深度导入：基于 discover 素材深度加工。新增 §2 执行链路原理、§3 三重根因架构分析（全局锁/表级失效/内存碎片）、§5 缓存机制辨析表、§6 Cache-Aside 完整实现（Key 设计/失效策略/多级链路）、§7 Buffer Pool 调优；清洗模板噪声；补官方文档与 Percona 来源 |
