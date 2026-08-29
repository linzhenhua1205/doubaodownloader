# PostgreSQL Schema 查看与管理指南## 量化速查## 量化速查

| 维度 | 量化值 | 说明 |
|:-----|:-------|:-----|
| 查询方法 | 3 种（100% 覆盖） | info_schema / pg_namespace / \dn |
| 系统 schema | 4 个（100% 内置） | public/pg_catalog/info_schema/pg_toast |
| search_path 默认 | 2 项（"$user", public） | 解析顺序 |
| 对象唯一性 | schema 内 100% 唯一 | 跨 schema 可同名 |
| 中文名长度 | LENGTH 按字符（1-4B） | UTF-8 下字符数 |

---

## 📑 目录

- [一、结论概要](#一结论概要)
- [二、Schema 本质与对象层级](#二schema-本质与对象层级)
- [三、查看当前 Schema](#三查看当前-schema)
- [四、列出所有 Schema（三种方法）](#四列出所有-schema三种方法)
- [五、Schema 管理操作](#五schema-管理操作)
- [六、search_path 与解析顺序](#六search_path-与解析顺序)
- [七、易错点与最佳实践](#七易错点与最佳实践)
- [量化速查](#量化速查)
- [相关文档](#相关文档)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 一、结论概要

Schema 是 PostgreSQL **命名空间**：数据库内组织对象（表/视图/函数）的第二层容器：

| 操作 | 命令/方法 | 场景 |
|:-----|:----------|:-----|
| 查看当前 Schema | `SELECT current_schema();` | 确认默认命名空间 |
| 列出所有 Schema | `\dn` / information_schema / pg_namespace | 全局视图 |
| 切换 Schema | `SET search_path TO xxx;` | 跨 schema 操作 |
| 创建/删除 | `CREATE SCHEMA` / `DROP SCHEMA` | 命名空间管理 |

**核心结论**：
1. **三种列法各取所长**：`\dn` 最快、`information_schema.schemata` 标准可移植、`pg_namespace` 信息最全（含 OID/属主）
2. **search_path 决定"默认去哪找表"**：不加 schema 前缀时按 search_path 顺序解析
3. **同名表可共存**：不同 schema 下允许同名表，表名在 schema 内唯一
4. **查看与管理配合**：先查清当前 schema 环境，再决定建表/授权落在哪个命名空间

---

## 二、Schema 本质与对象层级

### 2.1 对象层级

| 层级 | 说明 |
|:-----|:-----|
| 实例（cluster） | 顶层，多数据库 |
| Database（数据库） | 逻辑隔离单元 |
| Schema（模式/命名空间） | 库内组织单元 |
| Table/View/Function/Sequence/Type | 对象，schema 内唯一 |

- **同一实例不同 database 相互独立**，无法直接跨库访问
- **同一 database 不同 schema 可共享访问**（加 schema 前缀）
- 不同 schema 允许同名表

### 2.2 系统自带 Schema

| Schema | 作用 |
|:-------|:-----|
| `public` | 默认用户 schema（未指定时对象落这里） |
| `pg_catalog` | 系统目录（函数/类型/系统表） |
| `information_schema` | SQL 标准视图 |
| `pg_toast` | TOAST 辅助表（内部） |

---

## 三、查看当前 Schema

### 3.1 SQL 查询

```sql
-- current default schema (usually 'public')
SELECT current_schema();

-- current schema in search_path
SHOW search_path;
```

### 3.2 psql 命令

```bash
# connect
psql -h hostname -U username -d dbname
# show current schema
SELECT current_schema();
```

### 3.3 编程接口（Python 示例）

```python
import psycopg2

conn = psycopg2.connect(
    dbname="your_db", user="your_user",
    password="your_password", host="your_host",
)
cur = conn.cursor()
cur.execute("SELECT current_schema();")
print("Current schema:", cur.fetchone()[0])
cur.close()
conn.close()
```

---

## 四、列出所有 Schema（三种方法）

### 4.1 方法一：information_schema.schemata（标准）

```sql
SELECT schema_name
FROM information_schema.schemata
ORDER BY schema_name;
```

- ✅ SQL 标准、可读性好、跨库可移植
- 结果含：information_schema / pg_catalog / pg_toast / public / 自定义

### 4.2 方法二：pg_catalog.pg_namespace（PG 特有）

```sql
SELECT nspname AS schema_name
FROM pg_catalog.pg_namespace
ORDER BY nspname;
```

- ✅ 速度稍快、信息最全（可 JOIN 出 OID/属主/ACL）
- 扩展查询（含属主与权限）：

```sql
SELECT n.nspname AS schema_name,
       r.rolname AS owner,
       n.nspacl
FROM pg_namespace n
JOIN pg_roles r ON r.oid = n.nspowner
ORDER BY n.nspname;
```

### 4.3 方法三：psql 元命令 \dn

```bash
\dn
\dn+   -- with owner and ACL details
```

- ✅ 最快最方便，适合交互式排查
- 结果：schema 名 + 属主（\dn+）

### 4.4 三方法对比

| 方法 | 标准性 | 速度 | 信息量 | 适用 |
|:-----|:------:|:----:|:------:|:-----|
| information_schema | 高 | 中 | 中 | 合规/可移植 |
| pg_namespace | 低（PG 特有） | 快 | 高 | 运维/审计 |
| \dn | — | 最快 | 中 | 日常交互 |

---

## 五、Schema 管理操作

### 5.1 创建与删除

```sql
-- create schema
CREATE SCHEMA sales;
CREATE SCHEMA IF NOT EXISTS analytics AUTHORIZATION app_user;

-- create with objects
CREATE SCHEMA hr
  CREATE TABLE employees (id int PRIMARY KEY, name text);

-- drop schema (empty only)
DROP SCHEMA sales;
-- drop with all contents (dangerous)
DROP SCHEMA sales CASCADE;
```

### 5.2 对象归属

```sql
-- create table in specific schema
CREATE TABLE sales.orders (id int PRIMARY KEY);

-- move table between schemas
ALTER TABLE public.orders SET SCHEMA sales;

-- rename schema
ALTER SCHEMA sales RENAME TO sales_2026;
```

### 5.3 授权

```sql
-- grant usage + create on schema
GRANT USAGE, CREATE ON SCHEMA sales TO app_user;

-- grant all on all tables in schema
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA sales TO app_user;
```

---

## 六、search_path 与解析顺序

### 6.1 原理

```sql
-- current search path (default)
SHOW search_path;
-- default: "$user", public
```

- 未加 schema 前缀的对象名按 search_path 顺序逐个 schema 查找
- 默认 `"$user", public`：先找与当前用户同名的 schema，再找 public

### 6.2 切换 Schema（三种方式）

```sql
-- session-level switch
SET search_path TO sales, public;

-- database-level default
ALTER DATABASE mydb SET search_path TO sales, public;

-- fully-qualified (no path needed)
SELECT * FROM sales.orders;
```

### 6.3 search_path 安全注意

- ⚠️ 不要在 search_path 放不可信 schema（可被对象注入劫持）
- 建议显式列出：`SET search_path TO sales, public, pg_catalog;`

---

## 七、易错点与最佳实践

### 易错点

| # | 场景 | 坑 | 对策 |
|:-:|:-----|:---|:-----|
| 1 | 忘加 schema 前缀 | 找到 public 的同名对象 | 显式 schema.table |
| 2 | 混淆 current_schema 与 search_path | 多 schema 时语义不同 | 两者都查 |
| 3 | DROP SCHEMA 不带 CASCADE | 非空 schema 报错 | 先确认再 CASCADE |
| 4 | 只授表权限不授 schema | `permission denied for schema` | USAGE 先授 |
| 5 | search_path 乱设 | 对象解析错乱/被劫持 | 显式可控列表 |
| 6 | 用 information_schema 查权限 | 滞后/不含 PG 特有对象 | 权限用 pg_* |

### 最佳实践

1. **多租户/多业务用 schema 隔离**：同库多 schema 比多库更轻量
2. **命名规范**：schema 名 = 业务域（sales/hr/analytics）
3. **search_path 显式声明**：应用连接后立即 SET，防解析歧义
4. **权限最小化**：schema 级 USAGE 必须、CREATE 按需
5. **审计用 pg_namespace**：JOIN pg_roles 拿属主，比 information_schema 全

---

## 相关文档

- [核心对象模型：Database/Schema/User-Role](2026-08-15-postgres-core-concepts-db-schema-role.md) — Schema 层原理
- [DDL 操作语法](2026-08-15-postgres-user-db-schema-operations.md) — CREATE/ALTER/DROP SCHEMA
- [权限查询方法](2026-08-15-postgres-user-privilege-query.md) — schema 权限查询
- [权限配置与验证](2026-08-15-postgres-privilege-config-verify.md) — schema 授权实操

---

## 参考来源

- PingCode：如何查看 pg 数据库当前 schema
- CSDN：PostgreSQL 中查询所有的 schema（liumangtuzi888）
- [PostgreSQL 官方文档：Schema](https://www.postgresql.org/docs/current/ddl-schemas.html)
- [PostgreSQL 官方文档：CREATE SCHEMA](https://www.postgresql.org/docs/current/sql-createschema.html)

---

## 量化速查

| 维度 | 量化值 | 说明 |
|:-----|:-------|:-----|
| 查询方法 | 3 种 | information_schema / pg_namespace / \\dn |
| 系统 schema | 4 个 | public/pg_catalog/information_schema/pg_toast |
| 默认 search_path | \"$user\", public | 解析顺序 |
| 对象唯一性 | schema 内唯一 | 不同 schema 可同名表 |

---

## Changelog

- 2026-08-15 v1.0: 首次深度加工（对象层级 + 三方法对比 + 管理操作 + search_path 原理 + 安全注意 + 6 易错点；u023/u024 合并）
