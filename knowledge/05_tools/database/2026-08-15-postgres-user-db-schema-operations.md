# PostgreSQL 入门实操：User、Database、Schema 对象操作语法详解

> **类型**: knowledge | **日期**: 2026-08-15 | **版本**: v1.0
> **来源**: [CSDN - PostgreSQL入门基本语法之DDL-(user、database、schema)](https://blog.csdn.net/qq_39727113/article/details/105956012)（素材卡片，2025-11-18）
> **姊妹篇**: [PostgreSQL 核心对象模型](2026-08-15-postgres-core-concepts-db-schema-role.md)（原理）← 本文（操作语法）

---

## 📑 目录

- [一、结论概要](#一结论概要)
- [二、DDL 统一语法框架](#二ddl-统一语法框架)
- [三、用户对象操作](#三用户对象操作)
  - [3.2 用户相关关键参数](#32-用户相关关键参数量化基线)
- [四、数据库对象操作](#四数据库对象操作)
- [五、模式对象操作](#五模式对象操作)
- [六、操作矩阵速查](#六操作矩阵速查)
- [七、应用场景](#七应用场景)
- [八、易错点与最佳实践](#八易错点与最佳实践)
- [相关文档](#相关文档)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 一、结论概要

PostgreSQL 对象管理遵循 **`CREATE / ALTER / DROP + 对象类型`** 的统一语法框架，覆盖 user / database / schema 三级对象：

| 对象 | 创建 | 修改 | 删除 | 关键参数 |
|:-----|:-----|:-----|:-----|:---------|
| User | `CREATE USER` | `ALTER USER` | `DROP USER` | PASSWORD / SUPERUSER / VALID UNTIL |
| Database | `CREATE DATABASE` | `ALTER DATABASE` | `DROP DATABASE` | OWNER / TEMPLATE / CONNECTION LIMIT |
| Schema | `CREATE SCHEMA` | `ALTER SCHEMA` | `DROP SCHEMA` | AUTHORIZATION / OWNER / CASCADE |

**核心结论**：
1. **语法一致性是 PostgreSQL 的设计哲学**：所有对象遵循同一 DDL 框架，`\h <命令>` 可即时查语法
2. **`IF EXISTS` + `CASCADE` 是生产安全的两个关键修饰词**：前者保证幂等，后者处理依赖链
3. **对象生命周期管理**：建库建用户 ≠ 完事，还要处理属主、连接限制、默认权限、依赖清理
4. **DROP 是高风险操作**：PostgreSQL 的 DROP 是"硬删除"（无回收站），生产环境必须双人复核

---

## 二、DDL 统一语法框架

### 2.1 为什么是 CREATE/ALTER/DROP？

PostgreSQL 将对象操作收敛为**三动词框架**，与 SQL 标准的 DDL 定义对齐：

| 动词 | 语义 | 幂等性 | 触发重写 |
|:-----|:-----|:-------|:---------|
| `CREATE` | 新建对象 | 否（重复报错，可用 IF NOT EXISTS） | 否 |
| `ALTER` | 修改对象属性 | 是（重复执行同值无害） | 视属性而定（如重命名不重写数据） |
| `DROP` | 删除对象 | 否（可用 IF EXISTS） | 是（删除即物理清理） |

**设计价值**：学习成本低——会了一种对象的操作，其他对象几乎同理；这也是 `\h create user` 这类帮助命令有效的原因（语法模板一致）。

### 2.2 psql 帮助系统（降低记忆负担）

```sql
\h create user       -- help for CREATE USER
\h alter database    -- help for ALTER DATABASE
\h drop schema       -- help for DROP SCHEMA
\?                    -- psql meta-command help
```

> 生产环境不确定语法时，`\h` 是**最权威的本地速查**，比搜索引擎更快且版本精确匹配。

---

## 三、用户对象操作

### 3.1 创建用户

```sql
-- basic user
CREATE USER test_user PASSWORD 'test_user';
-- superuser
CREATE USER test1_user SUPERUSER PASSWORD 'test1_user';
-- idempotent + expiry
CREATE USER IF NOT EXISTS ops WITH PASSWORD 'ops123' VALID UNTIL '2027-01-01';
```

**原理要点**：
- `CREATE USER` ≡ `CREATE ROLE ... LOGIN`（登录能力默认开启）
- 选项（20+ 种属性）按需叠加：`SUPERUSER / CREATEDB / CREATEROLE / REPLICATION / CONNECTION LIMIT / VALID UNTIL`
- **密码策略**：生产环境建议 `password_encryption = scram-sha-256`（PG14+ 默认），明文密码仅限本地开发

### 3.2 用户相关关键参数（量化基线）

| 参数 | 默认/典型值 | 说明 |
|:-----|:-----------|:-----|
| `password_encryption` | `scram-sha-256` | SCRAM 存储 = salt **16B** + 摘要 **32B**（PG14+ 默认） |
| `max_connections` | **100** | 集群级连接上限；`CONNECTION LIMIT` 单用户上限受其约束 |
| `VALID UNTIL` | 不限 | 密码过期时间，精度到秒；适合临时账号 |
| `idle_session_timeout` | 0（禁用） | 建议设 30s~5min，防僵尸连接占满连接池 |
| `idle_in_transaction_session_timeout` | 0（禁用） | 建议设 60s，防长事务持有锁/快照 |
| 密码强度 | ≥**12** 字符 | 建议大写+小写+数字+符号混合 |

> 数据来源：PostgreSQL 官方文档 `password_encryption` / `max_connections` 参数说明（PG15 默认值）。

### 3.3 修改用户

```sql
ALTER USER test_user PASSWORD 'test123';          -- rotate password
ALTER USER test_user SUPERUSER;                    -- escalate privilege
ALTER USER test_user VALID UNTIL '2026-12-31';     -- set expiry
ALTER USER test_user CONNECTION LIMIT 10;          -- cap concurrent sessions
ALTER USER test_user RENAME TO new_name;           -- rename
```

**要点**：`ALTER USER ... WITH` 与 `CREATE` 共用属性集；**`SUPERUSER` 授予是不可逆风险动作**，建议用"组角色 + 成员继承"替代（见姊妹篇 §5）。

### 3.4 删除用户（高风险）

```sql
-- safe: check ownership first
SELECT datname FROM pg_database WHERE datdba = (SELECT oid FROM pg_roles WHERE rolname='test_user');
-- transfer ownership if needed
REASSIGN OWNED BY test_user TO postgres;
DROP OWNED BY test_user;
-- then drop
DROP USER IF EXISTS test_user;
```

**⚠️ 易错点**：`DROP USER` 失败常见原因
1. 用户仍拥有对象 → 报 `cannot drop role ... because some objects depend on it` → 先 `REASSIGN OWNED` / `DROP OWNED`
2. 用户仍有活跃连接 → 需 `pg_terminate_backend` 或等会话结束
3. 用户是其他角色的成员/被成员 → 先 `REVOKE` 成员关系

---

## 四、数据库对象操作

### 4.1 创建数据库

```sql
-- basic
CREATE DATABASE test_db OWNER test_user;
-- with template and encoding
CREATE DATABASE app_db TEMPLATE template0 ENCODING 'UTF8' LC_COLLATE 'C.UTF-8';
-- with connection limit
CREATE DATABASE analytics CONNECTION LIMIT 50;
```

**原理要点**：
- **TEMPLATE 机制**：新库克隆 `template1`（默认）；指定 `template0` 可绕开 template1 的污染并自定义编码/排序
- **OWNER**：库属主拥有该库全部对象管理权（含默认权限），建议与应用专用角色绑定，避免用 postgres 超级用户跑业务
- **CONNECTION LIMIT**：默认 -1（不限）；设限可防连接风暴拖垮实例

### 4.2 修改数据库

```sql
ALTER DATABASE test_db RENAME TO t_db;
ALTER DATABASE t_db OWNER TO postgres;
ALTER DATABASE t_db CONNECTION LIMIT 200;
ALTER DATABASE t_db SET search_path TO app, public;   -- per-db default setting
```

**要点**：`ALTER DATABASE ... SET` 可设**库级默认参数**（如 search_path / work_mem / statement_timeout），对应用透明生效，优于改 postgresql.conf 的全局影响。

### 4.3 删除数据库

```sql
-- PG13+ supports FORCE to kick sessions
DROP DATABASE IF EXISTS t_db WITH (FORCE);
```

**⚠️ 易错点**：
- `DROP DATABASE` **不能在事务块内执行**（PostgreSQL 限制）
- 默认要求无活跃连接；`WITH (FORCE)`（PG13+）自动终止会话
- 删除是不可恢复的（WAL 归档可部分恢复但成本极高）——**生产先 pg_dump 备份**

---

## 五、模式对象操作

### 5.1 创建模式

```sql
CREATE SCHEMA IF NOT EXISTS my_schema;
-- create schema owned by a role in one shot
CREATE SCHEMA IF NOT EXISTS AUTHORIZATION current_user;
CREATE SCHEMA app AUTHORIZATION app_owner;
```

**要点**：`CREATE SCHEMA ... AUTHORIZATION` 可**一条语句同时建 schema 并指定属主**；`AUTHORIZATION current_user` 创建与当前用户同名的 schema（配合默认 search_path `"$user"` 自动生效）。

### 5.2 修改模式

```sql
ALTER SCHEMA my_schema RENAME TO test_schema;
ALTER SCHEMA test_schema OWNER TO postgres;
```

### 5.3 删除模式（CASCADE 是双刃剑）

```sql
-- safe: check objects first
SELECT schemaname, count(*) FROM pg_tables WHERE schemaname='test_schema' GROUP BY 1;
-- delete with cascade (drops all dependent objects!)
DROP SCHEMA IF EXISTS test_schema CASCADE;
```

**⚠️ CASCADE 语义**：会**级联删除该 schema 下所有对象**（表/视图/函数/序列），且可能波及引用这些对象的其他 schema 对象（如视图、外键）。生产使用前必须确认影响面：
- 优先用 `DROP SCHEMA ... RESTRICT`（默认，有依赖则报错）暴露问题
- 或用 `pg_depend` 查询依赖关系后再 CASCADE

---

## 六、操作矩阵速查

| 操作 | User | Database | Schema |
|:-----|:-----|:---------|:-------|
| 创建 | `CREATE USER u [WITH ...]` | `CREATE DATABASE db [OWNER ...]` | `CREATE SCHEMA s [AUTHORIZATION ...]` |
| 幂等创建 | `CREATE USER IF NOT EXISTS` | `CREATE DATABASE`（无 IF NOT EXISTS） | `CREATE SCHEMA IF NOT EXISTS` |
| 重命名 | `ALTER USER ... RENAME` | `ALTER DATABASE ... RENAME` | `ALTER SCHEMA ... RENAME` |
| 改属主 | `ALTER USER`（无属主概念） | `ALTER DATABASE ... OWNER TO` | `ALTER SCHEMA ... OWNER TO` |
| 删除 | `DROP USER IF EXISTS` | `DROP DATABASE IF EXISTS` | `DROP SCHEMA IF EXISTS [CASCADE]` |
| 依赖处理 | REASSIGN/DROP OWNED | 无活跃连接（FORCE） | CASCADE/RESTRICT |

**注意不对称性**：
- `CREATE DATABASE` **不支持 IF NOT EXISTS**（PG 语法无此选项）——脚本需先查 `pg_database` 判断
- User 无"属主"概念（本身就是身份）；Database/Schema 有属主

---

## 七、应用场景

### 场景 1：环境初始化脚本（CI/CD 幂等）
```sql
-- init.sql (idempotent)
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='app_user') THEN
    CREATE ROLE app_user LOGIN PASSWORD 'secret';
  END IF;
  IF NOT EXISTS (SELECT FROM pg_database WHERE datname='app_db') THEN
    CREATE DATABASE app_db OWNER app_user;
  END IF;
END $$;
```
- 价值：`CREATE DATABASE` 无 IF NOT EXISTS，用 `DO` 块 + 系统目录判断实现幂等

### 场景 2：用户生命周期管理（入职/离职）
- 入职：`CREATE USER` + 组角色成员 + 默认权限
- 离职：`REASSIGN OWNED BY old_user TO team_lead` → `DROP OWNED BY old_user` → `DROP USER`

### 场景 3：多环境隔离（dev/staging/prod）
- 每环境独立 database + 独立 role + `CONNECTION LIMIT` 控制资源
- `ALTER DATABASE ... SET search_path` 固化每库默认路径

### 场景 4：灰度/重建库
- 新建 `app_db_v2`（TEMPLATE 或逻辑迁移）→ 切换连接 → 验证后 `DROP` 旧库（先备份）

---

## 八、易错点与最佳实践

### 易错点清单
| # | 操作 | 失败/风险 | 正确姿势 |
|:-:|:-----|:---------|:---------|
| 1 | DROP USER 有属主对象 | 报依赖错误 | REASSIGN OWNED 先行 |
| 2 | DROP DATABASE 有连接 | 报"being accessed by other users" | `WITH (FORCE)` 或先终止会话 |
| 3 | DROP SCHEMA CASCADE | 级联误删关联对象 | 先查 pg_tables / pg_depend |
| 4 | CREATE DATABASE 重复执行 | 报 already exists | DO 块判断或幂等脚本 |
| 5 | 明文密码 | 泄露风险 | scram-sha-256 + 环境变量注入 |
| 6 | 用超级用户建业务库 | 权限失控 | 应用专属 role + owner |

### 最佳实践
1. **命名规范**：库 `app_<domain>`、用户 `app_<svc>_rw/_ro`、schema 按分层（ods/dwd/ads）
2. **最小权限**：业务账号不给 SUPERUSER/CREATEDB；DDL 与 DML 账号分离
3. **DROP 前三查**：属主、连接、依赖，逐一确认后执行
4. **脚本化**：所有 DDL 进版本控制，避免手工执行不可追溯
5. **`\h` 优先**：语法不确定先本地查帮助，不猜

---

## 相关文档

- [PostgreSQL 核心对象模型：Database/Schema/User-Role](2026-08-15-postgres-core-concepts-db-schema-role.md) — 原理篇（本文件为操作篇）
- [PostgreSQL 用户列表查询方法](2026-08-15-postgres-user-list-queries.md) — 查询现有用户/权限
- [PostgreSQL 权限配置与验证](2026-08-15-postgres-privilege-config-verify.md) — GRANT/REVOKE 实操
- [PostgreSQL vs MySQL 深度对比](2026-08-15-postgres-vs-mysql-deep-comparison.md) — 对象模型差异
- [2025 主流数据库选型指南](2026-08-15-database-selection-guide.md) — 选型框架

---

## 参考来源

- [PostgreSQL 官方文档：CREATE USER](https://www.postgresql.org/docs/current/sql-createuser.html)
- [PostgreSQL 官方文档：CREATE DATABASE](https://www.postgresql.org/docs/current/sql-createdatabase.html)
- [PostgreSQL 官方文档：CREATE SCHEMA](https://www.postgresql.org/docs/current/sql-createschema.html)
- [PostgreSQL 官方文档：DROP 语句（依赖语义）](https://www.postgresql.org/docs/current/sql-dropdatabase.html)
- CSDN 原文：PostgreSQL入门基本语法之DDL-(user、database、schema)

---

## Changelog

- 2026-08-15 v1.0: 首次深度加工（补 DDL 框架哲学、DROP 依赖语义、6 易错点、4 场景、操作矩阵、幂等脚本）
