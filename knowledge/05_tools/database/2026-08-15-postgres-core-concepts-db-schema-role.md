# PostgreSQL 核心对象模型：Database、Schema、User/Role 深度解析

> **类型**: knowledge | **日期**: 2026-08-15 | **版本**: v1.0
> **来源**: [CSDN - PostgreSQL中Schema、Database、User和Tablespace之间的关系分析](https://blog.csdn.net/liumangtuzi888/article/details/151588494)（素材卡片，2025-11-18）
> **适用**: DBA / 数据工程师 / 后端开发者 / 架构师

---

## 📑 目录

- [一、结论概要](#一结论概要)
- [二、四层对象模型总览](#二四层对象模型总览)
- [三、Database：物理隔离边界](#三database物理隔离边界)
  - [3.2 关键默认参数](#32-关键默认参数量化基线)
- [四、Schema：逻辑命名空间](#四schema逻辑命名空间)
- [五、User/Role：统一角色模型](#五userrole统一角色模型)
- [六、Tablespace：存储位置抽象](#六tablespace存储位置抽象)
- [七、权限体系：CONNECT→USAGE→SELECT 三级链](#七权限体系connectusage--select-三级链)
- [八、应用场景与选型条件](#八应用场景与选型条件)
- [九、常见误区与最佳实践](#九常见误区与最佳实践)
- [十、与 MySQL 对象模型对比](#十与-mysql-对象模型对比)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 一、结论概要

PostgreSQL 采用 **"物理隔离 + 逻辑组织" 双层对象模型**：

| 层级 | 对象 | 隔离性 | 类比 |
|:-----|:-----|:-------|:-----|
| 集群级 | Instance / Role / Tablespace | 全局共享 | 园区统一管理 |
| 库级 | Database | 物理隔离（连接级） | 独立办公楼 |
| 库内 | Schema | 逻辑隔离 | 部门区域 |
| 对象级 | Table / View / Function | 权限控制 | 文件柜 |

**核心结论**：
1. **Database 是最高隔离单位**：一个连接只能访问一个 database，跨库查询需 dblink/外部表，物理隔离是安全底线
2. **Schema 是逻辑分组单位**：database 内的命名空间，支持批量授权（schema 级 GRANT）
3. **User ≡ Role**：PostgreSQL 8.1 起两者合并，`CREATE USER` = `CREATE ROLE ... LOGIN`；角色是**集群级**对象，天然支持跨库统一管理
4. **权限三级链**：`CONNECT on DATABASE` → `USAGE on SCHEMA` → `SELECT on TABLE`，缺一环则拒绝
5. **Tablespace 解耦存储**：把表/索引/物化视图放到不同物理盘，实现 IO 分层

---

## 二、四层对象模型总览

| 对象 | 层级 | 隔离性 | 类比 | 核心价值 |
|:-----|:----:|:------|:-----|:---------|
| **Database** | 最顶层 | 物理隔离（连接级） | 独立办公楼 | 安全边界、数据隔离 |
| **Schema** | 库内 | 逻辑隔离 | 办公楼内部门区域 | 命名空间、批量授权 |
| **User/Role** | 集群级 | 全局身份 | 员工工号 | 统一认证与授权 |
| **Table** | Schema 内 | — | 文件柜 | 数据实际载体 |
| **Tablespace** | 集群级 | 存储位置 | 仓库楼层 | IO 分离、容量管理 |

**关键数据**：
- 新建集群默认 3 个 database：`postgres`（默认连接）、`template0`（原始模板，不可连接）、`template1`（可复制模板，新建库默认克隆它）
- 默认 schema：`public`（每个新库自动创建）
- 角色属性约 20+ 种（LOGIN/SUPERUSER/CREATEDB/CREATEROLE/REPLICATION/BYPASSRLS 等）

---

## 三、Database：物理隔离边界

### 3.1 原理：为什么 database 之间物理隔离

PostgreSQL 的隔离性源于**文件系统级存储分离**：每个 database 有自己的 `pg_database` 目录（表、索引、系统目录），且**查询解析器不跨库解析**——SQL 中无法直接写 `dbname.schema.table` 三段式引用（这与 MySQL 不同）。

```sql
-- MySQL: cross-db reference allowed
SELECT * FROM other_db.other_table;
-- PostgreSQL: one db per connection
SELECT * FROM other_schema.table;  -- OK cross-schema
SELECT * FROM other_db.table;      -- ERROR cross-db
```

**物理隔离的代价与补偿**：
- 跨库访问需要 `dblink` / `postgres_fdw` 外部表 / `COPY` 导出导入
- 高版本（PG14+）可用 `postgres_fdw` 做只读联邦查询

### 3.2 关键默认参数（量化基线）

| 参数 | 默认值 | 含义 | 调整场景 |
|:-----|:-------|:-----|:---------|
| `block_size` | **8KB** | 数据页大小，建库时固定 | 大字段场景可 32KB（需 initdb 时指定） |
| `max_connections` | **100** | 最大并发连接数 | 连接池化后仍不足时调大（注意 shared_buffers 配比） |
| `shared_buffers` | **128MB** | 共享缓冲池 | OLTP 建议物理内存 25%；>8GB 内存建议 2-8GB |
| `wal_segment_size` | **16MB** | WAL 段文件大小 | 默认即可 |
| 单表容量上限 | ~**32TB** | relfilenode 1GB 段 × 32768 段 | 超限用分区表 |

> 基线说明：上述为 PG15+ 默认值；具体以 `SHOW <参数>;` 实测为准。

### 3.3 连接的数据库语义

连接字符串中的 database 决定当前上下文：
```
postgresql://user:pass@host:5432/mydb
                              ^^^^ current db
```
- 用户是集群级，数据库是连接级——**同一用户可连接多个库**，权限由各库的 GRANT 控制

---

## 四、Schema：逻辑命名空间

### 4.1 原理：search_path 与对象解析

Schema 的价值核心在 **search_path（搜索路径）** 机制。未加 schema 限定的表名按 search_path 顺序解析：

```sql
SHOW search_path;  -- default: "$user", public
-- resolution: 1) user-named schema  2) public
```

**原理要点**：
- 默认 `"$user", public`：优先查找与当前角色同名的 schema（若存在），否则 public
- 可在会话级/用户级/库级设置 `search_path`，是"默认 schema 切换"的底层机制
- 高权限角色若 search_path 被恶意篡改存在**搜索路径劫持**风险（见误区章节）

### 4.2 public schema 的权限演变（安全关键）

| PG 版本 | public schema 默认权限 |
|:--------|:----------------------|
| ≤ 14 | 所有用户 `CREATE` + `USAGE`（任何登录用户可建对象） |
| **15+** | 仅 owner（通常为库 owner），`USAGE` 也需显式授权 |

> 官方在 PG15 release notes 明确：这是为缓解"public schema 滥用导致的权限提升"安全加固。

### 4.3 Schema 级授权（批量管理）

```sql
GRANT USAGE ON SCHEMA analytics TO report_user;
-- then report_user can access granted tables in analytics
```
- 优点：**权限颗粒度适中**——比 database 细、比 table 粗，适合按业务模块管理
- 一个 database 内 schema 数理论上无硬上限（受对象标识符空间约束，实际数千个无压力）

---

## 五、User/Role：统一角色模型

### 5.1 历史：为什么 USER 和 ROLE 等价

PostgreSQL 在 **8.1（2005）** 前区分 `USER`（可登录）与 `GROUP`（不可登录），8.1 起统一为 **ROLE**，用属性区分能力：

| SQL 语句 | 等价于 |
|:---------|:-------|
| `CREATE USER alice;` | `CREATE ROLE alice WITH LOGIN;` |
| `CREATE ROLE app;`（默认无 LOGIN） | 组角色，不能登录 |

**角色两大用途**：
1. **身份**：带 LOGIN 的角色 = 用户，用于连接认证
2. **权限组**：无 LOGIN 的角色 = 组，用于批量授权（成员继承权限）

### 5.2 角色层级与权限继承

```sql
CREATE ROLE read_only;                       -- group role
GRANT SELECT ON ALL TABLES IN SCHEMA public TO read_only;
CREATE ROLE analyst LOGIN IN ROLE read_only; -- inherits
-- analyst inherits read_only privileges automatically
```

**继承规则**：
- `INHERIT`（默认）：成员角色自动继承父角色权限
- 权限检查时沿角色图向上遍历（SET ROLE 可切换当前生效角色）
- 注意：**对象 owner 权限不继承**，DDL 权限需显式授予

### 5.3 常用角色操作速查

```sql
-- list all roles and attributes
\du
SELECT rolname, rolsuper, rolcanlogin FROM pg_roles;
-- show current role
SELECT current_user, session_user;
-- show role memberships
SELECT r.rolname, m.rolname AS member FROM pg_auth_members am
  JOIN pg_roles r ON r.oid = am.roleid
  JOIN pg_roles m ON m.oid = am.member;
```

---

## 六、Tablespace：存储位置抽象

### 6.1 原理：符号链接机制

Tablespace 是**物理存储路径的抽象**，与 database/schema 逻辑解耦：

```
$PGDATA/pg_tblspc/
  ├── 16385 -> /data/ssd_fast/     # symlink to tablespace dir
  └── 16386 -> /data/hdd_archive/
```

- 表空间目录命名 = 表空间的 **OID**（对象标识符，4 字节）
- 建表时可指定表空间：`CREATE TABLE ... TABLESPACE ssd_fast;`
- **索引也可独立表空间**（索引与表分离存储）

### 6.2 典型 IO 分层场景

| 场景 | 热数据 | 冷数据/归档 | 效果 |
|:-----|:-------|:-----------|:-----|
| 日志库 | SSD 表空间（近期日志） | HDD 表空间（>90 天） | 热查快、冷存便宜 |
| 大表分区 | 当月分区在 NVMe | 历史分区在 SATA | 查询聚焦热区 |
| 索引 | 索引表空间在 SSD | 表本体在 HDD | 索引扫描加速 |

### 6.3 操作与限制

```sql
CREATE TABLESPACE ssd_fast LOCATION '/data/ssd_fast';
CREATE TABLE t (id int) TABLESPACE ssd_fast;
-- show tablespace usage
SELECT spcname, pg_size_pretty(pg_tablespace_size(spcname)) FROM pg_tablespace;
```
- 表空间不能跨 database 直接"占用"统计——同一表空间可被多个库使用
- 默认表空间：`pg_default`（指向 $PGDATA/base）与 `pg_global`（系统共享目录）

---

## 七、权限体系：CONNECT→USAGE→SELECT 三级链

### 7.1 权限检查顺序（缺一环即拒绝）

1. **连接建立**：`CONNECT on DATABASE`
2. **对象解析**：`USAGE on SCHEMA`
3. **对象访问**：`SELECT/INSERT/UPDATE/DELETE on TABLE`、`EXECUTE on FUNCTION`、`USAGE on SEQUENCE/TYPE`

### 7.2 最小权限模板（只读报表账号）

```sql
-- Level 1: allow connection
GRANT CONNECT ON DATABASE appdb TO report_user;
-- Level 2: allow schema usage
GRANT USAGE ON SCHEMA public TO report_user;
-- Level 3: allow read (all existing tables)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO report_user;
-- Level 3+: auto-grant for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO report_user;
```

### 7.3 权限模型对比（DB 对象 vs 数据库）

| 维度 | Database/Schema | User/Role |
|:-----|:----------------|:----------|
| 授权对象 | 库/模式/表/函数/序列 | 全局属性（LOGIN/SUPERUSER 等） |
| 隔离级别 | 数据隔离 | 身份隔离 |
| 变更影响 | 影响对象访问 | 影响连接能力 |

---

## 八、应用场景与选型条件

### 场景 1：多租户 SaaS——按租户隔离
| 方案 | database-per-tenant | schema-per-tenant |
|:-----|:--------------------|:------------------|
| 隔离强度 | 物理隔离（安全） | 逻辑隔离（需授权管控） |
| 租户数上限 | 数百~数千（连接/备份成本） | 数千~数万（单库内） |
| 迁移/备份 | 逐库独立 | 全库一起 |
| 选型条件 | 金融/合规强隔离、租户<1000 | 轻隔离、租户量大、运维简 |

### 场景 2：微服务分库
- 每服务独立 database（甚至独立 cluster），每服务独立 role（仅授权本库）→ 故障爆炸半径最小化

### 场景 3：数仓分层（schema 逻辑分组）
```sql
CREATE SCHEMA ods;   -- staging layer
CREATE SCHEMA dwd;   -- detail layer
CREATE SCHEMA ads;   -- application layer
GRANT USAGE ON SCHEMA ads TO bi_users;  -- expose app layer only
```
- 每层一个 schema，权限按层授予，天然形成数据治理边界

### 场景 4：报表/审计只读账号
- 三级链 GRANT（见 §7.2），配合 `default_privileges` 保证未来表也自动授权

### 场景 5：IO 分层（表空间）
- 高吞吐交易表 → NVMe 表空间；历史归档 → HDD 表空间（见 §6.2）

---

## 九、常见误区与最佳实践

### 误区 1：认为"库内 schema 越多越好"
- **问题**：search_path 混乱、跨 schema 引用耦合、迁移复杂
- **实践**：按业务域或治理层划分（3-10 个），避免逐表建 schema

### 误区 2：把 MySQL 习惯带进来——"跨库查询"
- PostgreSQL 无三段式跨库引用，需要时用 `postgres_fdw`，并明确这是**成本决策**（远程查询性能损失显著）

### 误区 3：search_path 劫持（安全）
- **风险**：`SET search_path = evil, public` 后，未限定的 `CREATE TABLE` 可能落入攻击者 schema，或恶意 schema 中的同名函数被优先解析执行
- **实践**：高权限角色固定 search_path；不要对不可信 schema 开放 `CREATE`；PG15+ 收紧 public schema 正是为此

### 误区 4：忽略 default privileges
- **问题**：只 GRANT 现有表，新表无权限 → 线上"间歇性权限报错"
- **实践**：`ALTER DEFAULT PRIVILEGES` 覆盖未来对象（见 §7.2 第 4 条）

### 最佳实践清单
1. 生产环境**禁用 public schema 写权限**（PG15 默认已收紧）
2. 角色命名规范：`app_<服务>_rw` / `app_<服务>_ro`，组角色+成员继承
3. 表空间规划在**建库前**完成（迁移表空间成本高）
4. 定期审计：`pg_roles` + `information_schema.role_table_grants` 交叉核对
5. 使用 `psql \dn+` 查看 schema 属主与权限，避免遗留 owner 混乱

---

## 十、与 MySQL 对象模型对比

| 维度 | PostgreSQL | MySQL |
|:-----|:-----------|:------|
| 层级 | Instance→Database→Schema→Table | Instance→Database→Table（无 Schema） |
| 跨库访问 | 不支持（需 FDW/dblink） | 支持（`db.table` 三段式） |
| User 作用域 | 集群级（跨库同一身份） | 库级绑定（`user@host`） |
| 权限最小单元 | Schema（支持批量授权） | 全局/库/表级 |
| 表空间 | 支持（符号链接） | 独立表空间文件（InnoDB） |
| 角色模型 | 统一 Role（可登录=用户） | 用户与角色（8.0 起支持角色） |

**迁移注意**：MySQL→PG 时，"跨库 JOIN"改写为"同库多 schema + JOIN"或 FDW，是改造量最大的点之一。

---

## 相关文档

- [PostgreSQL vs MySQL 深度对比（架构级）](2026-08-15-postgres-vs-mysql-deep-comparison.md) — 连接模型/MVCC/复制原理
- [PostgreSQL 用户与权限查询方法](2026-08-15-postgres-user-privilege-query.md) — 本批配套（用户与权限专题，含 u008 并入）
- [PostgreSQL 权限配置与验证](2026-08-15-postgres-privilege-config-verify.md) — 本批配套（GRANT 实操）
- [2025 主流数据库选型指南](2026-08-15-database-selection-guide.md) — 分类原理与选型框架
- [PostgreSQL 官方文档（外部）](https://www.postgresql.org/docs/current/)

---

## 参考来源

- [PostgreSQL 官方文档：角色](https://www.postgresql.org/docs/current/user-manag.html)
- [PostgreSQL 官方文档：权限](https://www.postgresql.org/docs/current/ddl-priv.html)
- [PostgreSQL 官方文档：表空间](https://www.postgresql.org/docs/current/manage-ag-tablespaces.html)
- [PostgreSQL 15 Release Notes（public schema 收紧）](https://www.postgresql.org/docs/15/release-15.html)
- CSDN 原文：PostgreSQL中Schema、Database、User和Tablespace之间的关系分析（2025-11-18）

---

## Changelog

- 2026-08-15 v1.0: 首次深度加工（由素材卡片扩展：补 search_path 原理、PG15 public schema 收紧、权限三级链、5 场景、4 误区、MySQL 对比）
