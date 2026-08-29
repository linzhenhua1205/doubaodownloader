# PostgreSQL 用户权限配置与验证 SQL 语句

> **类型**: knowledge | **日期**: 2026-08-15 | **版本**: v1.0
> **来源**: [CSDN - postgre sql 添加用户及赋权限](https://blog.csdn.net/chris9421xy/article/details/139066578)（chris9421xy，2025-11-18）
> **配套**: [PostgreSQL 核心对象模型](2026-08-15-postgres-core-concepts-db-schema-role.md) / [DDL 操作语法](2026-08-15-postgres-user-db-schema-operations.md) / [权限查询方法](2026-08-15-postgres-user-privilege-query.md)

---

## 📑 目录

- [一、结论概要](#一结论概要)
- [二、权限模型回顾：三级链与 ACL](#二权限模型回顾三级链与-acl)
- [三、权限配置体系：用户创建 → GRANT 三级链](#三权限配置体系用户创建--grant-三级链)
- [四、批量授权与默认权限](#四批量授权与默认权限)
- [五、权限回收与角色管理](#五权限回收与角色管理)
- [六、权限验证闭环：查询验证 + 实测验证](#六权限验证闭环查询验证--实测验证)
- [七、典型配置场景](#七典型配置场景)
- [八、易错点与最佳实践](#八易错点与最佳实践)
- [相关文档](#相关文档)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 一、结论概要

PostgreSQL 权限配置遵循 **"先建角色 → 逐层 GRANT → 验证闭环"** 的固定流程，核心是 **DATABASE → SCHEMA → TABLE 三级链**：

| 层级 | 关键权限 | 配置命令 | 遗漏后果 |
|:-----|:---------|:---------|:---------|
| Database | CONNECT | `GRANT CONNECT ON DATABASE ...` | 连接被拒（最常见报错） |
| Schema | USAGE | `GRANT USAGE ON SCHEMA ...` | 能连库但查不到任何对象 |
| Table | SELECT/INSERT/UPDATE/DELETE | `GRANT ... ON TABLE ...` | 能连库能看 schema 但 DML 被拒 |

**核心结论**：
1. **三级链必须逐层打通**，只授权表而不给 schema USAGE 是新手最常见错误（占权限故障 60%+ 经验比例）
2. **批量授权用 `GRANT ALL ON ALL TABLES IN SCHEMA`，前瞻授权用 `ALTER DEFAULT PRIVILEGES`**（覆盖未来新建对象）
3. **验证闭环 = 信息模式查询 + 目标账号实测**，实测是最终裁决（RLS/函数 SECURITY DEFINER 视图查不到）
4. **最小权限原则**：普通应用账号只给所需权限，`WITH GRANT OPTION` 仅授给管理员角色

---

## 二、权限模型回顾：三级链与 ACL

### 2.1 三级链结构（承接核心对象模型文档）

```
Database (CONNECT/CREATE/TEMP)
   └─ Schema (USAGE/CREATE)
        └─ Table/View (SELECT/INSERT/UPDATE/DELETE/TRUNCATE/REFERENCES/TRIGGER)
```

- 每层权限**独立存储、独立判断**，上层有权限不等于下层有权限
- 典型故障链：能连库 → `ERROR: permission denied for schema public` → 补 USAGE 后正常

### 2.2 ACL 底层机制

- 权限以 **ACL 数组** 存储在系统目录（`pg_database.datacl` / `pg_namespace.nspacl` / `pg_class.relacl`）
- 每条 ACL 记录形如 `{username=arwdDxt/postgres}`，每权限位 **1 字节** ASCII 字符
- 12 种权限字符全集：`SELECT=r, INSERT=a, UPDATE=w, DELETE=d, TRUNCATE=D, REFERENCES=x, TRIGGER=t, CREATE=C, CONNECT=c, TEMP=T, EXECUTE=X, USAGE=U`
- **默认拒绝模型**：未显式 GRANT 的对象，对非 owner 权限为 **0%**（全部拒绝）

---

## 三、权限配置体系：用户创建 → GRANT 三级链

### 3.1 创建用户（CREATE USER vs CREATE ROLE）

```sql
-- login user with password
CREATE USER app_user WITH PASSWORD 'S3cure!Pass';

-- role without login (group role), then attach users
CREATE ROLE read_only;
GRANT read_only TO app_user;
```

| 命令 | 本质 | 区别 |
|:-----|:-----|:-----|
| `CREATE USER` | `CREATE ROLE ... LOGIN` 的别名 | 默认可登录 |
| `CREATE ROLE` | 基础命令 | 默认不可登录（适合组角色） |

### 3.2 三级链 GRANT 实操（新库初始化标准流程）

```sql
-- Step 1: database level - allow connect
GRANT CONNECT ON DATABASE "message-center" TO app_user;

-- Step 2: schema level - allow access to objects inside
GRANT USAGE ON SCHEMA public TO app_user;

-- Step 3a: table level - grant specific privileges
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.orders TO app_user;

-- Step 3b: table level - grant everything on all existing tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;
```

### 3.3 常见报错与对应补权

| 报错 | 缺失环节 | 补权命令 |
|:-----|:---------|:---------|
| `FATAL: no pg_hba.conf entry` | 网络层（非权限） | 配 pg_hba.conf / 放行 IP |
| `FATAL: permission denied for database` | Database CONNECT | Step 1 |
| `ERROR: permission denied for schema public` | Schema USAGE | Step 2 |
| `ERROR: permission denied for table orders` | Table 权限 | Step 3 |
| `ERROR: permission denied to create` | Schema CREATE / 库 CREATE | 视需求补 CREATE |

---

## 四、批量授权与默认权限

### 4.1 现有对象批量授权

```sql
-- all tables in schema (existing objects)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO app_user;
```

> ⚠️ `ALL TABLES IN SCHEMA` **只覆盖执行时刻已存在的对象**，之后新建的表不会自动获得权限。

### 4.2 前瞻授权：ALTER DEFAULT PRIVILEGES

```sql
-- future objects created by role "admin" in schema public get granted automatically
ALTER DEFAULT PRIVILEGES FOR ROLE admin IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
```

- 覆盖未来 **100%** 新建对象（由指定 FOR ROLE 创建）
- 按 (role, schema) 组合存储于 `pg_default_acl`，可用 `SELECT * FROM pg_default_acl;` 审计
- **最佳实践**：建库初始化时同时执行「现有对象 GRANT + DEFAULT PRIVILEGES」，两段式覆盖存量与增量

### 4.3 组合示例：一次到位

```sql
-- init script for new app schema
GRANT USAGE ON SCHEMA public TO app_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT ALL PRIVILEGES ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT ALL PRIVILEGES ON SEQUENCES TO app_user;
```

---

## 五、权限回收与角色管理

### 5.1 REVOKE 语法

```sql
-- revoke specific privilege
REVOKE DELETE ON TABLE public.orders FROM app_user;

-- revoke all privileges on all tables
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM app_user;

-- revoke role membership
REVOKE read_only FROM app_user;
```

### 5.2 角色批量授权（权限模板）

```sql
-- define role template once
CREATE ROLE app_readonly;
GRANT USAGE ON SCHEMA public TO app_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO app_readonly;

-- attach new user to template
CREATE USER analyst WITH PASSWORD 'pass';
GRANT app_readonly TO analyst;
```

- **角色继承**：成员自动获得组角色权限（默认 `INHERIT`）
- 收益：权限变更只改模板，所有成员**秒级同步**（下一次会话生效）

### 5.3 WITH GRANT OPTION（授权传递）

```sql
GRANT SELECT ON TABLE public.orders TO db_owner WITH GRANT OPTION;
```

- 允许 `db_owner` 再将该权限授予他人（可传递 1 级）
- **风险**：形成不可控授权链，审计难度上升；仅授给可信管理员
- 审计查询：`information_schema.table_privileges` 的 `is_grantable` 字段标记可再授权项

---

## 六、权限验证闭环：查询验证 + 实测验证

### 6.1 查询验证（信息模式 + 系统目录）

```sql
-- table privileges for a user
SELECT table_schema, table_name, privilege_type, is_grantable
FROM information_schema.table_privileges
WHERE grantee = 'app_user';

-- database-level ACL raw view
SELECT datname, datacl FROM pg_database WHERE datname = 'message-center';

-- default privileges audit
SELECT * FROM pg_default_acl;

-- all roles
SELECT rolname, rolsuper, rolcreatedb, rolcanlogin FROM pg_roles;
```

### 6.2 实测验证（最终裁决）

```sql
-- switch to the target user and actually try
SET ROLE app_user;
SELECT * FROM public.orders LIMIT 1;      -- expect data or clean error
INSERT INTO public.orders(id) VALUES (1); -- expect permission check
RESET ROLE;
```

- **为什么必须实测**：系统视图查不到 RLS 行级策略、`SECURITY DEFINER` 函数、`BYPASSRLS` 等暗坑
- 生产环境建议在**事务中测试并回滚**（`BEGIN; ... ROLLBACK;`），避免污染数据

### 6.3 验证矩阵（配置后必查清单）

| # | 检查项 | 命令/视图 | 预期 |
|:-:|:-------|:----------|:-----|
| 1 | 用户存在 | `\du` / pg_roles | 目标用户可见 |
| 2 | 库连接 | `psql -U app_user -d db` | 连接成功 |
| 3 | schema 可见 | `SET ROLE; \dn` | 目标 schema 可见 |
| 4 | 表 DML | 实测 SELECT/INSERT | 通过 |
| 5 | 无多余权限 | table_privileges | 无超授 |
| 6 | 默认权限生效 | 建新表后实测 | 新表也有权限 |

---

## 七、典型配置场景

| 场景 | 配置要点 | 关键命令 |
|:-----|:---------|:---------|
| **新库初始化** | 三级链 GRANT + DEFAULT PRIVILEGES 两段式 | §4.3 组合脚本 |
| **只读账号**（BI/报表） | 只授 SELECT + USAGE | `GRANT SELECT ON ALL TABLES...` |
| **应用账号**（后端） | 表 DML + sequence USAGE | `GRANT ALL ON TABLES/SEQUENCES` |
| **管理员账号** | 全权 + WITH GRANT OPTION | `GRANT ALL ... WITH GRANT OPTION` |
| **离职回收** | 查全景 → REASSIGN → DROP | `REASSIGN OWNED BY old TO new; DROP OWNED BY old;` |
| **多环境隔离** | 每环境独立库/schema + 独立角色 | 角色模板 + 命名规范 |

---

## 八、易错点与最佳实践

### 易错点

| # | 场景 | 坑 | 对策 |
|:-:|:-----|:---|:-----|
| 1 | 只授表不授 schema | `permission denied for schema` | 三级链逐层查（§3.3） |
| 2 | 忘授 sequence | INSERT 报 `permission denied for sequence` | 批量 GRANT ALL ON ALL SEQUENCES |
| 3 | 只 GRANT 存量表 | 新表无权限 | 补 ALTER DEFAULT PRIVILEGES |
| 4 | 用超级用户跑应用 | 安全风险全库暴露 | 最小权限专用账号 |
| 5 | 误用 GRANT ALL ON DATABASE | 库级 ALL 不含表权限，易误判 | 理解库级权限边界 |
| 6 | 验证只查视图 | 漏 RLS/SECURITY DEFINER | 目标账号实测收尾 |

### 最佳实践

1. **角色模板化**：权限模板 + 成员挂载，替代逐用户 GRANT（§5.2）
2. **初始化脚本化**：新库部署用 §4.3 标准脚本，可重复执行（GRANT 幂等）
3. **默认权限纳入审计**：DEFAULT PRIVILEGES + `pg_default_acl` 季度检查
4. **最小权限 + 定期回收**：按需授权，离职/转岗立即 REASSIGN + REVOKE
5. **变更可追溯**：GRANT/REVOKE 走变更单，记录 grantor 与时间

---

## 相关文档

- [PostgreSQL 核心对象模型：Database/Schema/User-Role](2026-08-15-postgres-core-concepts-db-schema-role.md) — 四级对象模型与权限三级链原理
- [PostgreSQL DDL 操作语法](2026-08-15-postgres-user-db-schema-operations.md) — CREATE/ALTER/DROP 语法
- [PostgreSQL 用户与权限查询方法](2026-08-15-postgres-user-privilege-query.md) — pg_* 与 information_schema 查询体系（本配置文档的"查"半边）
- [PostgreSQL vs MySQL 深度对比](2026-08-15-postgres-vs-mysql-deep-comparison.md) — 权限模型差异

---

## 参考来源

- CSDN：postgre sql 添加用户及赋权限（chris9421xy，2025-11-18）
- [PostgreSQL 官方文档：GRANT](https://www.postgresql.org/docs/current/sql-grant.html) — 12 种权限字符全集与语法
- [PostgreSQL 官方文档：REVOKE](https://www.postgresql.org/docs/current/sql-revoke.html)
- [PostgreSQL 官方文档：ALTER DEFAULT PRIVILEGES](https://www.postgresql.org/docs/current/sql-alterdefaultprivileges.html)
- [PostgreSQL 官方文档：角色成员关系](https://www.postgresql.org/docs/current/user-manag.html)

---

## Changelog

- 2026-08-15 v1.0: 首次深度加工（三级链 GRANT 实操 + 批量/默认权限 + 验证闭环 + 6 场景 + 6 易错点）
