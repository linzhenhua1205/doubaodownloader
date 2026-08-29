# PostgreSQL 用户与权限查询方法总结

> **类型**: knowledge | **日期**: 2026-08-15 | **版本**: v1.0
> **来源**: [CSDN - postgre查询所有用户及权限](https://blog.csdn.net/Yonggie/article/details/80160915) + [geek-docs - PostgreSQL 用户列表](https://geek-docs.com/postgresql/postgresql-questions/778_postgresql_postgresql_user_listing.html)（两素材合并，u008 并入）
> **配套**: [PostgreSQL 核心对象模型](2026-08-15-postgres-core-concepts-db-schema-role.md) / [DDL 操作语法](2026-08-15-postgres-user-db-schema-operations.md)

---

## 📑 目录

- [一、结论概要](#一结论概要)
- [二、查询体系总览：系统目录 vs information_schema](#二查询体系总览系统目录-vs-information_schema)
- [三、用户/角色列表查询](#三用户角色列表查询)
  - [3.4 量化速查](#34-量化速查基于官方目录文档)
- [四、角色属性与成员关系查询](#四角色属性与成员关系查询)
- [五、对象权限查询](#五对象权限查询)
- [六、综合案例：权限审计](#六综合案例权限审计)
- [七、应用场景](#七应用场景)
- [八、易错点与最佳实践](#八易错点与最佳实践)
- [相关文档](#相关文档)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 一、结论概要

PostgreSQL 的权限查询分 **两大体系**：**系统目录视图**（pg_*，全面但字段原始）与 **信息模式**（information_schema.*，SQL 标准、可移植）：

| 查询目标 | 系统目录（pg_*） | 信息模式（information_schema.*） |
|:---------|:----------------|:-------------------------------|
| 用户/角色列表 | `pg_roles` / `pg_user` | — |
| 角色成员 | `pg_auth_members` | — |
| 表权限 | `pg_class` + `aclitem` | `table_privileges` |
| 列权限 | — | `column_privileges` |
| 模式权限 | `pg_namespace` + acl | `schema_privileges` / `usage_privileges` |
| 函数权限 | `pg_proc` + acl | `routine_privileges` |

**核心结论**：
1. **`pg_roles` 是角色真相源**，`pg_user` 只是其"可登录"过滤视图（源码级 VIEW，非独立存储）
2. **权限验证黄金流程**：查用户列表 → 查对象权限 → 实际执行验证，三步闭环
3. **information_schema 可移植但滞后**：只反映 SQL 标准对象，PostgreSQL 特有对象（如 sequence 权限部分）需用 pg_* 视图
4. **审计场景首选 pg_* + ACL 解析**：`aclexplode()` 函数可把 ACL 数组拆为逐条权限记录

---

## 二、查询体系总览：系统目录 vs information_schema

### 2.1 为什么有两套？

| 维度 | pg_* 系统目录 | information_schema |
|:-----|:-------------|:-------------------|
| 标准 | PostgreSQL 私有 | SQL 标准（可移植到其他 RDBMS） |
| 粒度 | 原始、全面（含内部字段） | 面向用户、规范命名 |
| 性能 | 直接读目录，快 | 视图层包装，略慢 |
| 覆盖 | 全部对象（含扩展/内部） | 标准对象子集 |
| 典型用途 | 运维/审计/排障 | 应用层可移植查询/合规报表 |

**原则**：**排障和审计用 pg_\***，跨库迁移/合规报表用 information_schema。

### 2.2 ACL 机制（权限存储底层）

权限在系统目录中以 **ACL（访问控制列表）数组** 存储，形如 `{user=arwdDxt/postgres}`。用 `aclexplode()` 展开：

```sql
SELECT grantee, privilege_type, is_grantable
FROM aclexplode((SELECT relacl FROM pg_class WHERE relname = 'orders'));
```

- 每条记录 = 授予者 + 被授予者 + 权限 + 是否可再授权（grantable）
- `aclexplode` 是权限审计的核心工具（返回行级结果，可直接 JOIN 用户表）

---

## 三、用户/角色列表查询

### 3.1 基础查询

```sql
-- all roles (incl. non-login group roles) - source of truth
SELECT rolname, rolsuper, rolcreatedb, rolcreaterole, rolcanlogin, rolreplication
FROM pg_roles;

-- login-only users (pg_user = pg_roles WHERE rolcanlogin)
SELECT usename, usesysid, usecreatedb, usesuper FROM pg_user;

-- psql shortcut
\du
```

### 3.2 pg_user 字段详解（含示例）

| 字段 | 含义 | 示例 |
|:-----|:-----|:-----|
| `usename` | 用户名 | postgres / alice / bob / carol |
| `usesysid` | 角色 OID | 10（postgres 内置）/ 16384+（普通） |
| `usecreatedb` | 可否建库 | t / f |
| `usesuper` | 是否超级用户 | t / f |

**示例解读**（来自 geek-docs 素材）：
- `postgres`：内置超级用户（usesysid=10，usecreatedb=t，usesuper=t）
- `alice`：普通用户（16384，均 f）
- `bob`：可建库但非超管（usecreatedb=t，usesuper=f）——适合应用 owner 场景
- `carol`：超管但无建库权（usesuper=t，usecreatedb=f）——极少见，注意权限组合

### 3.3 高级筛选（审计场景）

```sql
-- find all superusers (risk surface)
SELECT usename, usesysid FROM pg_user WHERE usesuper = 't';
-- roles that can create databases
SELECT rolname FROM pg_roles WHERE rolcreatedb = 't';
-- login roles without password expiry
SELECT rolname FROM pg_roles WHERE rolcanlogin AND rolvaliduntil IS NULL;
```

### 3.4 量化速查（基于官方目录文档）

| 维度 | 量化值 | 说明 |
|:-----|:-------|:-----|
| pg_user vs pg_roles | 6 列 / 25 列（**24%**） | pg_user 仅暴露可登录角色的子集字段 |
| ACL 权限字符 | 12 种 × **1 字节**/字符 | 官方 GRANT 权限表全集（表级 7 + 库/模式/函数/序列等 5） |
| 内置 OID 保留区 | 1–16383，共 16383 个 | 系统对象专用，用户角色从 16384 起 |
| postgres 内置超管 | usesysid=10，占保留区 **0.06%** | 唯一预置登录角色（10/16383） |
| 普通角色 OID | ≥16384（**+0.006%** 空间占用可忽略） | 64 位 OID 空间下扩容无压力 |

> 数据依据：[官方 catalog-pg-roles](https://www.postgresql.org/docs/current/catalog-pg-roles.html)（列数与内置 OID）、[官方 GRANT 权限表](https://www.postgresql.org/docs/current/sql-grant.html)（12 种权限字符）。

---

## 四、角色属性与成员关系查询

### 4.1 角色属性全集

```sql
-- pg_roles full attributes (~25 columns)
SELECT * FROM pg_roles;
-- key attributes at a glance
SELECT rolname,
       rolsuper    AS is_superuser,
       rolcreatedb AS can_create_db,
       rolcreaterole AS can_create_role,
       rolcanlogin AS can_login,
       rolreplication,
       rolconnlimit AS conn_limit,
       rolvaliduntil AS password_expiry
FROM pg_roles;
```

### 4.2 成员关系（谁属于哪个角色组）

```sql
-- membership table directly
SELECT r.rolname AS role, m.rolname AS member, am.admin_option
FROM pg_auth_members am
JOIN pg_roles r ON r.oid = am.roleid
JOIN pg_roles m ON m.oid = am.member;

-- check if a user inherits a role group
SELECT rolname FROM pg_roles
WHERE oid IN (SELECT member FROM pg_auth_members WHERE roleid = (SELECT oid FROM pg_roles WHERE rolname='read_only'))
  AND rolname = 'analyst';
```

### 4.3 当前会话身份

```sql
SELECT current_user, session_user;   -- effective vs login role
SELECT current_setting('role');      -- role after SET ROLE
SELECT pg_is_in_recovery();          -- is replica (recovery mode)
```

---

## 五、对象权限查询

### 5.1 权限清单（五级对象）

| 对象 | 权限类型 | 查询视图 |
|:-----|:---------|:---------|
| Database | CONNECT / CREATE / TEMP | `pg_database` + acl 解析 |
| Schema | USAGE / CREATE | `information_schema.schema_privileges` |
| Table | SELECT/INSERT/UPDATE/DELETE/TRUNCATE/REFERENCES/TRIGGER | `information_schema.table_privileges` |
| Column | SELECT/INSERT/UPDATE（列级） | `information_schema.column_privileges` |
| Function | EXECUTE | `information_schema.routine_privileges` |
| Sequence | USAGE / SELECT / UPDATE | `information_schema.usage_privileges` |

### 5.2 核心查询 SQL

```sql
-- table privileges of a user
SELECT table_name, privilege_type, is_grantable
FROM information_schema.table_privileges
WHERE grantee = 'cc';

-- schema privileges of a user
SELECT schema_name, privilege_type
FROM information_schema.schema_privileges
WHERE grantee = 'cc';

-- column-level privileges (fine-grained)
SELECT table_name, column_name, privilege_type
FROM information_schema.column_privileges
WHERE grantee = 'cc';

-- function privileges of a role
SELECT routine_name, privilege_type
FROM information_schema.routine_privileges
WHERE grantee = 'cc';
```

### 5.3 我有什么权限？（自助排查）

```sql
-- tables accessible by current user
SELECT table_schema, table_name, privilege_type
FROM information_schema.table_privileges
WHERE grantee = current_user;
```

---

## 六、综合案例：权限审计

### 6.1 全库高权限扫描（审计脚本）

```sql
-- superusers + createdb/createrole (risk surface)
SELECT rolname, rolsuper AS super, rolcreatedb AS createdb, rolcreaterole AS createrole
FROM pg_roles WHERE rolsuper OR rolcreatedb OR rolcreaterole;

-- login users without password expiry policy
SELECT rolname FROM pg_roles
WHERE rolcanlogin AND rolvaliduntil IS NULL AND rolname NOT LIKE 'pg_%';
```

### 6.2 用户权限全景（单用户报告）

```sql
-- full privilege summary for target user_x
SELECT 'TABLE' AS obj_type, table_name AS obj, privilege_type
FROM information_schema.table_privileges WHERE grantee = 'user_x'
UNION ALL
SELECT 'SCHEMA', schema_name, privilege_type
FROM information_schema.schema_privileges WHERE grantee = 'user_x'
UNION ALL
SELECT 'COLUMN', column_name, privilege_type
FROM information_schema.column_privileges WHERE grantee = 'user_x';
```

### 6.3 验证闭环（权限审计三步）

1. **查列表**：确认用户存在（§3）
2. **查权限**：确认对象已授权（§5）
3. **实测**：用该用户实际执行 `SELECT/INSERT` 验证——**系统视图不覆盖所有暗坑**（如 RLS 行级策略、函数 SECURITY DEFINER），实测是最终裁决

---

## 七、应用场景

| 场景 | 查询组合 | 目的 |
|:-----|:---------|:-----|
| **权限审计**（季度） | pg_roles 高权限扫描 + table_privileges 汇总 | 发现超管过多、越权授权 |
| **离职回收** | 用户权限全景报告 → REASSIGN/DROP | 确认回收范围不留死角 |
| **排障**（用户报"无权限"） | 三级链逐层查（库→schema→表） | 定位缺失环节（最常见：USAGE 缺） |
| **合规报表** | information_schema 全量导出 | 满足等保/审计要求（可移植格式） |
| **新员工开通** | 对比同类角色模板 | 保证最小权限一致 |

---

## 八、易错点与最佳实践

### 易错点
| # | 场景 | 坑 | 对策 |
|:-:|:-----|:---|:-----|
| 1 | 只查 pg_user | 漏掉不可登录的组角色 | 用 pg_roles 全量 |
| 2 | 只查 table_privileges | 漏 schema 级 USAGE/CREATE | 三级链逐层查 |
| 3 | 忽略默认权限 | 新表无权限但旧表有 | 查 `pg_default_acl` |
| 4 | 忽略 RLS | 视图显示有权限但查不到行 | 查 `pg_policies` / 实测 |
| 5 | 混淆 grantee | `grantee` vs `grantor` 搞反 | 确认查询对象是被授予者 |

### 最佳实践
1. **权限查询脚本化**：把 §6 审计 SQL 存为脚本，定期（月度/季度）跑
2. **默认权限纳入审计**：`ALTER DEFAULT PRIVILEGES` 设置与 `pg_default_acl` 检查配套
3. **RLS 单独排查**：行级安全策略不体现在信息模式视图，查 `pg_policies`
4. **以实测收尾**：任何权限结论，最后用目标账号实测确认
5. **记录基线**：权限审计结果留存，与上次对比发现漂移

---

## 相关文档

- [PostgreSQL 核心对象模型：Database/Schema/User-Role](2026-08-15-postgres-core-concepts-db-schema-role.md) — 权限三级链原理
- [PostgreSQL DDL 操作语法](2026-08-15-postgres-user-db-schema-operations.md) — 用户/库/schema 的 CREATE/ALTER/DROP
- [PostgreSQL 权限配置与验证](2026-08-15-postgres-privilege-config-verify.md) — GRANT/REVOKE 实操（本批配套）
- [PostgreSQL vs MySQL 深度对比](2026-08-15-postgres-vs-mysql-deep-comparison.md) — 权限模型差异

---

## 参考来源

- [PostgreSQL 官方文档：系统目录 pg_roles](https://www.postgresql.org/docs/current/catalog-pg-roles.html)
- [PostgreSQL 官方文档：信息模式](https://www.postgresql.org/docs/current/information-schema.html)
- [PostgreSQL 官方文档：GRANT（权限类型全集）](https://www.postgresql.org/docs/current/sql-grant.html)
- [PostgreSQL 官方文档：aclexplode](https://www.postgresql.org/docs/current/functions-info.html)
- CSDN：postgre查询所有用户及权限（Yonggie）/ geek-docs：PostgreSQL 用户列表（两素材合并）

---

## Changelog

- 2026-08-15 v1.0: 首次深度加工（合并 u008/u009 双素材；补 ACL 原理、pg_roles vs pg_user 关系、五级权限查询矩阵、审计三步闭环、5 场景）
