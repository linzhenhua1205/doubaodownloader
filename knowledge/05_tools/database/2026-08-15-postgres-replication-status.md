# PostgreSQL 主从同步状态查看指南

> **类型**: knowledge | **日期**: 2026-08-15 | **版本**: v1.0
> **来源**: [CSDN - PostgreSQL 的查看主从同步状态](https://blog.csdn.net/lee_vincent1/article/details/142291312)（lee_vincent1）
> **配套**: [pg_stat_* 统计视图全景](2026-08-15-postgres-pgstat-overview.md) / [内存配置建议](2026-08-15-postgres-memory-config.md) / [服务启动失败排查](2026-08-15-postgres-startup-failure-port5432.md)

---

## 📑 目录

- [一、结论概要](#一结论概要)
- [二、复制架构与 LSN 基础](#二复制架构与-lsn-基础)
- [三、主节点视角：pg_stat_replication](#三主节点视角pg_stat_replication)
- [四、从节点视角：pg_stat_wal_receiver](#四从节点视角pg_stat_wal_receiver)
- [五、延迟量化：pg_wal_lsn_diff](#五延迟量化pg_wal_lsn_diff)
- [六、同步一致性验证流程](#六同步一致性验证流程)
- [七、故障诊断与告警](#七故障诊断与告警)
- [八、易错点与最佳实践](#八易错点与最佳实践)
- [相关文档](#相关文档)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 一、结论概要

PostgreSQL 主从同步状态查看有**主从两个视角**，核心是 LSN（Log Sequence Number）对比：

| 视角 | 视图/函数 | 用途 |
|:-----|:----------|:-----|
| 主节点 | `pg_stat_replication` | 每个从节点的连接状态、同步进度、同步模式 |
| 从节点 | `pg_stat_wal_receiver` | WAL 接收器状态、接收进度、上游连接 |
| 从节点 | `pg_last_wal_receive_lsn()` / `pg_last_wal_replay_lsn()` | 接收/回放位置快速查询 |
| 延迟计算 | `pg_wal_lsn_diff(sent, replay)` | 主从滞后字节数 |

**核心结论**：
1. **同步状态正常 = `state=streaming` + 延迟可控**：`streaming` 是健康态，`startup`/`catchup` 是过渡态
2. **延迟判断必须用 LSN 差值**：`pg_wal_lsn_diff()` 返回字节数，比看时间戳更精确
3. **同步模式决定数据安全**：`sync`（同步）保证已提交事务不丢，`async`（异步）可能丢最近数据
4. **一致性验证 = 主从 LSN 交叉比对**：主 `sent_lsn` ≈ 从 `received_lsn` ≈ `replay_lsn` 时同步健康

---

## 二、复制架构与 LSN 基础

### 2.1 流复制链路

| 环节 | 进程/位置 | 说明 |
|:-----|:---------|:-----|
| 主节点 WAL 生成 | wal_sender 进程 | 发送 WAL 记录 |
| 网络传输 | TCP 连接 | WAL 记录流式传输 |
| 从节点接收 | wal_receiver 进程 | 写入（write_lsn）→ flush（flush_lsn）→ replay（replay_lsn） |

### 2.2 LSN 是什么

- LSN = WAL 日志中的字节偏移量，形如 `0/2B4A1E8`
- 单调递增，天然可比大小、可算差值
- `pg_wal_lsn_diff(lsn1, lsn2)` 返回两者差值的**字节数**

---

## 三、主节点视角：pg_stat_replication

### 3.1 核心字段

| 字段 | 含义 | 健康值 |
|:-----|:-----|:-------|
| `pid` | wal_sender 进程 ID | — |
| `state` | startup / catchup / streaming | `streaming` |
| `sent_lsn` | 主节点已发送的 WAL 位置 | 持续前进 |
| `write_lsn` | 从节点已写入（OS 缓冲） | 接近 sent |
| `flush_lsn` | 从节点已落盘 | 接近 sent |
| `replay_lsn` | 从节点已应用 | 接近 sent |
| `sync_state` | async / sync / potential / quorum | 按配置 |
| `client_addr` | 从节点 IP | 符合预期 |

### 3.2 基础查询

```sql
-- all standby connections from primary
SELECT pid, client_addr, state, sync_state,
       sent_lsn, write_lsn, flush_lsn, replay_lsn
FROM pg_stat_replication;
```

### 3.3 状态机理解

| state | 含义 | 是否正常 |
|:------|:-----|:--------:|
| `startup` | 连接建立初期，等待接收 | 过渡态 |
| `catchup` | 追赶主节点（落后较多） | 过渡态，需观察 |
| `streaming` | 实时流式同步 | ✅ 健康 |

---

## 四、从节点视角：pg_stat_wal_receiver

### 4.1 核心字段

| 字段 | 含义 |
|:-----|:-----|
| `status` | WAL 接收状态（streaming） |
| `received_lsn` | 已接收的最新 WAL 位置 |
| `last_msg_send_time` | 主节点最后发消息时间 |
| `last_msg_receipt_time` | 从节点最后收到消息时间 |
| `sender_host` / `sender_port` | 主节点地址/端口 |
| `conninfo` | 连接串（含认证信息，注意脱敏） |

### 4.2 从节点查询

```sql
-- standby side: receiver status
SELECT status, received_lsn,
       last_msg_send_time, last_msg_receipt_time,
       sender_host, sender_port
FROM pg_stat_wal_receiver;

-- quick check of receive/replay positions
SELECT pg_last_wal_receive_lsn() AS received,
       pg_last_wal_replay_lsn()  AS replayed;
```

### 4.3 消息时间戳的意义

- `last_msg_send_time` 与 `last_msg_receipt_time` 的间隔 = 网络往返 + 处理延迟
- 长时间不更新（> 数分钟）→ 主从连接可能中断或停滞

---

## 五、延迟量化：pg_wal_lsn_diff

### 5.1 延迟计算公式

```sql
-- replication lag in bytes (run on primary)
SELECT client_addr,
       pg_wal_lsn_diff(sent_lsn, replay_lsn) AS lag_bytes,
       pg_wal_lsn_diff(sent_lsn, flush_lsn)  AS flush_lag_bytes
FROM pg_stat_replication;
```

### 5.2 延迟分级

| 延迟量 | 判断 | 关注度 |
|:-------|:-----|:------:|
| < 1MB（数十 KB 级） | 正常，接近实时 | ✅ |
| 1MB - 100MB | 轻度滞后，观察趋势 | ⚠️ |
| > 100MB 或持续增长 | 明显滞后，排查网络/IO | 🔴 |

### 5.3 时间估算

```sql
-- estimate lag in seconds from WAL write rate
SELECT pg_wal_lsn_diff(sent_lsn, replay_lsn)
         / NULLIF(pg_current_wal_insert_lsn() - sent_lsn, 0)  -- relative proxy
FROM pg_stat_replication;
```

> ⚠️ 更可靠的秒级延迟需结合 WAL 生成速率，简单做法是连续采样 LSN 差值看趋势是否收敛。

---

## 六、同步一致性验证流程

### 6.1 三步验证法

```sql
-- step 1 (primary): check standby streaming state
SELECT client_addr, state, sync_state, replay_lsn
FROM pg_stat_replication;

-- step 2 (standby): check receiver & replay positions
SELECT pg_last_wal_receive_lsn() AS received,
       pg_last_wal_replay_lsn()  AS replayed;

-- step 3: compare lag (bytes)
-- on primary: pg_wal_lsn_diff(sent_lsn, replay_lsn) should be small
```

### 6.2 判断标准

- 主 `sent_lsn` ≈ 从 `received_lsn`：传输正常
- 从 `received_lsn` ≈ `replay_lsn`：回放正常
- 两处差值均小 → 同步健康

### 6.3 数据级验证（可选）

```sql
-- compare row counts on both nodes for critical tables
-- (run on primary and standby separately)
SELECT count(*) FROM public.orders;
-- also compare max(updated_at) for freshness
SELECT max(updated_at) FROM public.orders;
```

---

## 七、故障诊断与告警

### 7.1 常见故障

| 症状 | 可能原因 | 排查 |
|:-----|:---------|:-----|
| state 卡在 catchup | 主库 WAL 产生过快 / 从库落后太多 | 检查网络带宽、从库 IO |
| replay_lsn 长时间不动 | 从库回放阻塞（锁冲突/IO 卡） | 查从库 pg_stat_activity |
| last_msg 长时间不更新 | 复制连接中断 | 查网络、wal_sender 状态 |
| 从库掉线后重连 | 需要重新 catchup | 观察 catchup 耗时，必要时 pg_rewind |

### 7.2 告警建议

| 指标 | 阈值 | 级别 |
|:-----|:-----|:----:|
| 复制连接断开 | state != streaming | 🔴 P1 |
| 延迟字节数 | > 100MB | 🔴 P1 |
| 延迟增长趋势 | 连续 3 次采样递增 | ⚠️ P2 |
| 从节点回放停滞 | replay_lsn 5min 不变 | 🔴 P1 |

### 7.3 监控 SQL（定时采样）

```sql
-- simple lag sampling (run every minute from monitor)
SELECT now() AS ts,
       client_addr,
       pg_wal_lsn_diff(sent_lsn, replay_lsn) AS lag_bytes
FROM pg_stat_replication;
```

---

## 八、易错点与最佳实践

### 易错点

| # | 场景 | 坑 | 对策 |
|:-:|:-----|:---|:-----|
| 1 | 只看 state | streaming 也可能延迟大 | 必须看 LSN 差值 |
| 2 | 从节点查 pg_stat_replication | 该视图在主节点才有数据 | 从节点用 wal_receiver / 函数 |
| 3 | 误把时间戳当延迟 | 消息时间与 LSN 进度不同步 | 用 pg_wal_lsn_diff 量化 |
| 4 | 忽略 sync_state | async 下以为不丢数据 | 明确同步模式与 RPO |
| 5 | 单次采样判断 | 瞬时值无法判断趋势 | 连续采样看收敛性 |

### 最佳实践

1. **双视角监控**：主节点查 replication、从节点查 wal_receiver，双向确认
2. **延迟按字节告警**：基于 `pg_wal_lsn_diff` 设定阈值，比时间戳可靠
3. **同步模式按业务定**：金融/交易用 `synchronous_commit = on`（sync），分析/缓存可 async
4. **故障预案**：从库落后过大时，评估 `pg_rewind` 还是重建从库
5. **定期演练切换**：主备切换流程（promote）至少季度演练一次

---

## 相关文档

- [pg_stat_* 统计视图全景](2026-08-15-postgres-pgstat-overview.md) — pg_stat_replication 归类与联合诊断
- [PostgreSQL 内存配置建议](2026-08-15-postgres-memory-config.md) — 从库回放与 shared_buffers 关系
- [服务启动失败排查](2026-08-15-postgres-startup-failure-port5432.md) — 连接异常的另一侧面
- [PostgreSQL vs MySQL 深度对比](2026-08-15-postgres-vs-mysql-deep-comparison.md) — 复制模型差异

---

## 参考来源

- CSDN：PostgreSQL 的查看主从同步状态（lee_vincent1）
- [PostgreSQL 官方文档：监控复制](https://www.postgresql.org/docs/current/monitoring-stats.html#MONITORING-PG-STAT-REPLICATION-VIEW)
- [PostgreSQL 官方文档：WAL 函数](https://www.postgresql.org/docs/current/functions-admin.html)
- [PostgreSQL 官方文档：流复制](https://www.postgresql.org/docs/current/warm-standby.html)

---

## Changelog

- 2026-08-15 v1.0: 首次深度加工（双视角视图 + LSN 基础 + 延迟量化公式 + 三步验证 + 故障矩阵 + 5 易错点）
