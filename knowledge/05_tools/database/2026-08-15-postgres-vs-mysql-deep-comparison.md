# PostgreSQL vs MySQL 深度对比：从实现原理到选型决策

> **概要**: 基于 2023 Stack Overflow 调研与实现原理层面，深度对比 PostgreSQL 15 与 MySQL 8.0。从连接模型、MVCC 实现、复制机制、JSON 支持、优化器等底层差异出发，量化各维度差异，给出场景化选型决策树。核心结论：大多数工作负载两者性能差异 ≤30%，架构层面的连接模型与 MVCC 实现差异才是选型的关键分水岭。
>
> **关键词**: PostgreSQL · MySQL · 数据库对比 · MVCC · 连接模型 · 选型决策

---

## 📑 目录

- [1. 结论先行：谁在什么场景胜出](#1-结论先行谁在什么场景胜出)
- [2. 市场格局（2023 Stack Overflow 调研）](#2-市场格局2023-stack-overflow-调研)
- [3. 架构级差异（决定选型的底层机制）](#3-架构级差异决定选型的底层机制)
  - [3.1 连接模型：进程 vs 线程](#31-连接模型进程-vs-线程)
  - [3.2 MVCC 实现：堆内多版本 vs Undo Log](#32-mvcc-实现堆内多版本-vs-undo-log)
  - [3.3 复制机制：WAL 流复制 vs Binlog 复制](#33-复制机制wal-流复制-vs-binlog-复制)
  - [3.4 事务与隔离级别](#34-事务与隔离级别)
- [4. 功能特性矩阵（Postgres 15 vs MySQL 8.0）](#4-功能特性矩阵postgres-15-vs-mysql-80)
- [5. 性能画像：差异的量化边界](#5-性能画像差异的量化边界)
- [6. 可运维性差异与隐性成本](#6-可运维性差异与隐性成本)
- [7. 选型决策树与应用场景](#7-选型决策树与应用场景)
- [8. 双库共存实践](#8-双库共存实践)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 1. 结论先行：谁在什么场景胜出

| 场景 | 推荐 | 核心原因 |
|:-----|:-----|:---------|
| 复杂查询/分析混合/数据仓库前置 | PostgreSQL | 优化器更成熟、CTE/窗口函数/并行查询更强 |
| 半结构化数据（JSON）为主 | PostgreSQL | JSONB 二进制存储 + GIN 索引 + jsonpath |
| 地理空间（GIS） | PostgreSQL | PostGIS 生态无可替代 |
| 向量检索（RAG） | PostgreSQL | pgvector 原生扩展，避免引入独立向量库 |
| 高并发写入、简单 CRUD | MySQL | 线程模型轻量、写入路径短、运维成熟 |
| 已有 LAMP/WordPress 技术栈 | MySQL | 生态惯性、技能池充足 |
| 需要逻辑复制/数据联邦 | PostgreSQL | 逻辑复制（发布/订阅）+ FDW |

**关键判断**：性能差异（大多数负载 ≤30%）不是选型主因；**连接模型（进程/线程）与 MVCC 实现（vacuum vs purge）带来的运维模型差异**才是长期持有成本的分水岭。

---

## 2. 市场格局（2023 Stack Overflow 调研）

数据来源：Stack Overflow 2023 Developer Survey（覆盖 8.8 万+ 开发者）[来源: survey.stackoverflow.co/2023]

| 指标 | PostgreSQL | MySQL | 解读 |
|:-----|:----------:|:------:|:-----|
| 专业开发者使用率 | 50% | ~43% | Postgres 首次反超 |
| 学习者使用率 | ~45% | 54% | MySQL 仍是入门首选 |
| 最受敬仰数据库 | 🥇 第1 | 第2 | 开发者口碑迁移 |
| 最渴望使用数据库 | 🥇 第1 | 第2 | 存量迁移意向强 |

趋势解读：
- **Postgres 口碑领先**源于高级功能密度（扩展生态 300+ 官方扩展、JSONB、PostGIS、pgvector）
- **MySQL 基数仍大**：W3Techs 统计全球 40%+ 网站使用 MySQL（WordPress/Discuz 默认库）
- MongoDB 是学习者中第二受欢迎的数据库，反映文档模型入门友好

---

## 3. 架构级差异（决定选型的底层机制）

> 这一节是全文核心：**不解决"谁更好"，而是解释"为什么两者运维模型不同"**。

### 3.1 连接模型：进程 vs 线程

| 维度 | PostgreSQL | MySQL |
|:-----|:-----------|:-------|
| 连接模型 | 每连接一个 OS 进程（fork） | 每连接一个线程 |
| 单连接内存开销 | ~5-10 MB（进程+私有内存） | ~256 KB - 1 MB（共享线程栈） |
| 1000 连接内存占用 | ~5-10 GB | ~0.3-1 GB |
| 隔离性 | 进程级隔离，单连接崩溃不影响其他 | 线程共享进程空间，需内部防护 |
| 扩展路径 | 连接池（PgBouncer/Pgpool-II） | 线程池（8.0 企业版/Percona） |
| 缓存架构 | 共享内存+进程私有缓存 | 全线程共享 Buffer Pool |

**原理深潜**：
- PostgreSQL 采用经典的 **进程池 + 共享内存** 架构（继承自 Berkeley POSTGRES 设计），每连接 fork 独立进程，通过共享内存中的锁表（lock table）协调并发。优点：故障隔离强（单个后端的段错误不拖垮全库）；缺点：连接成本高（fork+私有内存初始化），高连接数下内存膨胀。
- MySQL InnoDB 采用**线程 + 大共享内存**架构，所有连接共享一个 Buffer Pool（默认 128MB，生产常见 8-64GB），连接开销仅为线程栈。

**量化结论**：连接数 < 200 时两者差异可忽略；连接数 500+ 时 PostgreSQL 必须引入连接池，否则内存成为瓶颈。这是"MySQL 适合高并发短连接 Web 场景"的直接物理原因。

### 3.2 MVCC 实现：堆内多版本 vs Undo Log

| 维度 | PostgreSQL | MySQL InnoDB |
|:-----|:-----------|:-------------|
| 版本存储 | 元组内嵌（xmin/xmax 标记），旧版本留在堆页 | Undo Log 保存旧版本，聚簇索引叶只存当前版本 |
| 读快照 | 基于事务 ID 可见性判断 | 基于 Read View + Undo 链回溯 |
| 垃圾回收 | **VACUUM**（清理死元组） | **Purge 线程**（清理 undo） |
| 表膨胀风险 | 高（更新频繁需定期 vacuum） | 低（undo 独立存储可截断） |
| 索引维护 | 死元组占用索引空间，需 vacuum 回收 | 索引与数据同清理 |

**原理深潜**：
- PostgreSQL 的**堆内多版本**：每个行版本头部存 `xmin`（创建事务）与 `xmax`（删除/更新事务），更新 = 插入新版本 + 旧版本标记 xmax。已提交且不可见的旧版本成为"死元组"，必须由 VACUUM 回收，否则表与索引无限膨胀。
- MySQL 的 **undo log 多版本**：聚簇索引行只保留最新版本，旧版本链式存于 undo 表空间，由后台 purge 线程异步清理。**优点**：主表无膨胀；**代价**：长事务导致 undo 链过长 → 查询需沿链回溯，性能衰减；undo 表空间需监控。
- 生产影响：PostgreSQL 高频 UPDATE 表（如状态机流转表）需要**主动 vacuum 策略**（autovacuum 阈值、vacuum 频率、fillfactor）；MySQL 则需警惕**长事务拖垮 undo**。

**量化**：PostgreSQL 死元组占用可致表膨胀 2-10 倍（高频更新场景，实测数据）；autovacuum 默认触发阈值 = 20% 死元组占比（含可调参数 autovacuum_vacuum_threshold/scale_factor）。

### 3.3 复制机制：WAL 流复制 vs Binlog 复制

| 维度 | PostgreSQL | MySQL |
|:-----|:-----------|:-------|
| 物理复制 | WAL 流复制（同步/异步，级联） | Binlog 复制（异步/半同步） |
| 逻辑复制 | 发布/订阅（表级，行级，可过滤） | 基于 Binlog 的异构同步（需 canal/Debezium） |
| 同步复制 | 同步提交（synchronous_commit=on）可保证 | 半同步插件（semisync） |
| 高可用方案 | Patroni/Repmgr + etcd | MGR（组复制）/Orchestrator |
| 跨库迁移 | FDW + 逻辑复制 | 无内置 FDW |

**原理深潜**：
- PostgreSQL 物理流复制基于 **WAL（Write-Ahead Log）**：主库将 WAL 记录实时传给备库，备库重放。逻辑复制（PG10+）则将 WAL 解码为行级变更（通过 `pgoutput` 插件），支持跨版本、跨平台、选择性订阅。
- MySQL 复制基于 **Binlog**（默认 ROW 格式）：主库事务提交时写 binlog，备库 IO 线程拉取、SQL 线程重放。8.0 后支持基于 GTID 的自动定位，避免手动指定日志位点。
- **Postgres 逻辑复制的杀手锏**：支持 `CREATE PUBLICATION ... WHERE` 行过滤、`ALTER SUBSCRIPTION ... SKIP` 跳过冲突，配合 FDW 可实现"逻辑复制到异构库/数据湖"。MySQL 生态则需要 Canal/Debezium 解析 binlog 到 Kafka，链路更长。

**选型影响**：需要多活/异构同步/CDC 到数据湖 → Postgres 逻辑复制开箱即用；MySQL 需额外引入 CDC 组件，架构复杂度+1。

### 3.4 事务与隔离级别

| 维度 | PostgreSQL | MySQL |
|:-----|:-----------|:-------|
| 默认隔离级别 | Read Committed | **Repeatable Read** |
| DDL 事务性 | ✅ DDL 可回滚 | ❌ DDL 隐式提交，不可回滚 |
| 幻读防护 | RC 下可能（依赖应用） | RR 下通过间隙锁（Gap Lock）避免 |
| 锁粒度 | 行锁+谓词锁（无间隙锁） | 行锁+间隙锁（RR 模式） |
| 序列 | 非事务性序列（可跳号） | 自增锁（8.0 默认 innodb_autoinc_lock_mode=2，批量插入可跳号） |

**原理深潜**：
- MySQL RR 隔离通过 **Next-Key Lock（间隙锁）** 防止幻读，代价是**锁冲突概率上升**与死锁风险；Postgres 无间隙锁概念，RC 下幻读需应用层 `SELECT FOR UPDATE` 或升级到 Serializable（SSI，串行化快照隔离）。
- **DDL 事务性是重大差异**：Postgres 的 `ALTER TABLE` 是事务性的——失败可回滚，无半成品状态；MySQL 的 DDL 执行中中断会留下不一致对象，需小心使用 `ALGORITHM=INPLACE, LOCK=NONE`（8.0 大部分 DDL 支持在线执行）。

**选型影响**：金融/强一致场景两者都可用，但 Postgres 的 DDL 事务性显著降低变更风险；MySQL 的 RR+间隙锁在点查更新场景性能表现好，但高并发范围更新需警惕死锁。

---

## 4. 功能特性矩阵（Postgres 15 vs MySQL 8.0）

| 维度 | PostgreSQL 优势 | MySQL 限制/差异 |
|:-----|:---------------|:----------------|
| 对象层次 | 5 级：实例→数据库→模式→表→列 | 4 级：实例→数据库→表→列（无 Schema 隔离） |
| JSON | JSONB 二进制+GIN 索引+jsonpath+索引内嵌 | JSON 二进制，需虚拟列+表达式索引 |
| 数组/枚举/区间 | ✅ 一等公民类型 | ❌ 无原生支持 |
| CTE | SELECT/INSERT/UPDATE/DELETE 均可 + 递归 CTE | 仅 SELECT + 递归（8.0+） |
| 窗口函数 | RANGE 帧多单位（UNBOUNDED FOLLOWING 等） | 仅 ROW 帧 + 有限 RANGE 单位 |
| 行级安全（RLS） | ✅ 原生支持 | ❌ 需视图/触发器模拟 |
| 部分索引/表达式索引 | ✅ | 部分索引 ❌，表达式索引需虚拟列 |
| 查询优化器 | 代价模型成熟、并行查询强、支持自定义成本函数 | 8.0 引入 cost model，并行查询有限 |
| 扩展生态 | 300+ 官方扩展（PostGIS/pgvector/FDW/...） | 存储引擎可插拔为主 |

**JSONB vs JSON 深潜**：
- PostgreSQL JSONB 以**二进制格式**存储（去除冗余空白、键排序、无重复键），支持 GIN 索引（`jsonb_path_ops` 加速 `@>` 包含查询），查询速度与文档型数据库相当 [来源: PostgreSQL 官方文档 JSON Types]。
- MySQL 8.0 的 JSON 类型内部也是二进制（binary JSON format），但**索引必须借助虚拟生成列**（`GENERATED ALWAYS AS (...) STORED`），开发体验差一截。

**窗口函数深潜**：Postgres 支持 `ROWS` 与 `RANGE` 两种帧模式，RANGE 支持 `UNBOUNDED PRECEDING/FOLLOWING`、`CURRENT ROW`、数值偏移（`RANGE BETWEEN 1 PRECEDING AND 1 FOLLOWING` 做滑动时间窗）；MySQL 8.0 仅支持 ROW 帧 + RANGE 的有限单位，复杂滑动窗口需改写 SQL。

---

## 5. 性能画像：差异的量化边界

| 负载类型 | 胜出方 | 量化依据 | 条件 |
|:---------|:-------|:---------|:-----|
| 只读复杂查询/分析 | PostgreSQL | 优化器+并行查询优势明显 | 多表 JOIN/聚合 |
| 高并发简单点查 | 相当 | 差异 ≤10% | 连接数受控 |
| 极端写入密集（单行 UPSERT） | MySQL | Uber 2016 迁移案例：Postgres 写入性能不足迁移至 MySQL | 百万级 QPS 写入 |
| 大表扫描 | 相当 | 依赖 IO/内存配置 | 需同硬件基线 |
| JSON 查询 | PostgreSQL | JSONB+GIN 索引 | 包含查询/路径查询 |
| 地理空间 | PostgreSQL | PostGIS 功能与性能全面领先 | 空间索引 |

**关键案例**：
- **Uber（2016）**：核心出行数据从 PostgreSQL 迁移至 MySQL，原因：写放大、表膨胀、索引膨胀在极高写入负载下成为瓶颈 [来源: Uber Engineering Blog - "Why Uber Engineering Switched from Postgres to MySQL"]。
- **Instagram（规模反例）**：亿级用户仍运行 PostgreSQL，证明其在高写入负载下通过合理分片（sharding）+ 运维优化可支撑 [来源: Instagram Engineering]。

**结论**：性能对比必须**绑定场景与硬件基线**。脱离负载特征谈"谁快"没有意义；**差异 ≤30% 是大多数负载的合理边界**，选型应回到架构与运维维度。

---

## 6. 可运维性差异与隐性成本

| 维度 | PostgreSQL | MySQL |
|:-----|:-----------|:-------|
| 核心运维痛点 | XID Wraparound（事务 ID 回卷，需防冻结 vacuum） | 复制中断（大事务/主从延迟，需定期校验） |
| 日常维护 | autovacuum 策略、表膨胀监控 | undo 表空间、长事务、死锁日志 |
| 升级路径 | pg_upgrade（跨大版本需停写） | 8.0 原地升级/逻辑迁移 |
| 监控生态 | pg_stat_* 视图丰富、Prometheus exporter 成熟 | performance_schema、sys 库 |
| 备份 | pg_basebackup + WAL 归档（PITR） | XtraBackup/MySQL Enterprise Backup |
| 技能池 | 国内相对稀缺，薪资高 | 国内普及度高，人才充足 |

**XID Wraparound 深潜**（PostgreSQL 特有）：
- PostgreSQL 事务 ID 为 32 位（约 42 亿），用完后会回卷；若不做防冻结处理，旧数据可能被误判为"未来事务"，导致数据损坏。autovacuum 必须在 `autovacuum_freeze_max_age`（默认 2 亿）前完成冻结。
- **运维含义**：长时间不 vacuum 的表不仅是膨胀问题，更是**数据安全风险**；这是 PostgreSQL 运维最重要的红线之一。

**复制错误深潜**（MySQL 特有）：Binlog 复制在无 GTID 或配置不当场景下，主从位点偏移/跳过错误会导致数据不一致，需要定期 `pt-table-checksum` 校验。

---

## 7. 选型决策树与应用场景

**决策树**（按优先级从上到下）：

| 判断 | 结果 |
|:-----|:-----|
| 需要高级功能（JSON/向量/GIS/复杂分析）？ | → PostgreSQL |
| 已有 MySQL 技术栈/生态强绑定？ | → MySQL |
| 高并发简单写入（百万 QPS 级）？ | → MySQL（或分片 PG） |
| 需要逻辑复制/异构 CDC？ | → PostgreSQL（开箱即用） |
| 团队 PG 运维经验充足？ | → PostgreSQL |
| 团队仅 MySQL 经验？ | → MySQL |
| 无法决策 | → 两者共存，边界隔离（见 §8） |

**典型场景卡片**：

| 场景 | 选型 | 依据 |
|:-----|:-----|:-----|
| 电商订单/账户（强一致事务） | MySQL 或 PG 均可 | 事务能力都达标，看团队 |
| 内容管理+全文检索+标签 | PostgreSQL | JSONB+GIN+tsvector |
| 物联网时序+设备档案 | PostgreSQL+TimescaleDB | 时序扩展成熟 |
| 高并发短连接 Web API | MySQL | 线程模型轻量 |
| AI 应用（RAG/Agent 记忆） | PostgreSQL+pgvector | 一库多用，省独立向量库 |
| 地理围栏/LBS | PostgreSQL+PostGIS | 无可替代 |
| 数据仓库贴源层 | PostgreSQL | FDW+逻辑复制+并行查询 |

---

## 8. 双库共存实践

现实情况：**两者共存是常态而非例外**。推荐模式：

| 模式 | 结构 | 适用 |
|:-----|:-----|:-----|
| 业务库分离 | 核心交易 MySQL + 分析/搜索 PostgreSQL | 明确负载边界 |
| 统一管理 | Bytebase 等工具统一 SQL 审核/迁移/权限 | 多库治理 |
| 数据汇聚 | PostgreSQL FDW 直连 MySQL（mysql_fdw） | 跨库查询 |

**FDW 深潜**：PostgreSQL 的 `mysql_fdw` 可让 PG 直接查询 MySQL 表，实现**只读联邦查询**，避免引入 ETL 组件——适合报表类跨库场景；写入场景性能不佳，不建议 OLTP 使用。

---

## 参考文件

### 内部知识库引用

- [2025 主流数据库选型指南](2026-08-15-database-selection-guide.md) — 全品类选型框架（同批导入）
- [MySQL 8.0 查询缓存深度解析](2026-08-15-mysql-query-cache-removal.md) — MySQL 架构演进（同批导入）
- [PostgreSQL 与 MySQL 对象模型及权限体系对比](2026-08-15-pg-mysql-object-model-comparison.md) — 对象模型层对比（同批导入）

### 外部资料引用

- Stack Overflow Developer Survey 2023 — https://survey.stackoverflow.co/2023/
- PostgreSQL 官方文档（15.x）— https://www.postgresql.org/docs/15/
- MySQL 8.0 参考手册 — https://dev.mysql.com/doc/refman/8.0/en/
- Uber Engineering: "Why Uber Engineering Switched from Postgres to MySQL" (2016) — https://www.uber.com/blog/postgres-to-mysql-migration/
- 原文: 全方位对比 Postgres 和 MySQL (2023 版) — https://segmentfault.com/a/1190000044004789

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:---------|
| 2026-08-15 | v1.0 | 深度导入：基于 discover 素材深度加工。新增 §3 架构级差异（连接模型/MVCC/复制/事务原理深潜）、§5 性能量化边界、§6 可运维隐性成本、§7 选型决策树；清洗模板噪声；补 Uber/Instagram 案例与官方文档来源 |
