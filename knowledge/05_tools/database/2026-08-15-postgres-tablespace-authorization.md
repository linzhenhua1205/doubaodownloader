# PostgreSQL 创建表空间及用户授权操作指南

> **类型**: knowledge | **日期**: 2026-08-15 | **版本**: v1.0
> **来源**: [CSDN - PostgreSQL创建表空间及用户授权](https://blog.csdn.net/u010438126/article/details/127761251)（u010438126）
> **配套**: [核心对象模型](2026-08-15-postgres-core-concepts-db-schema-role.md) / [权限配置与验证](2026-08-15-postgres-privilege-config-verify.md) / [内存配置建议](2026-08-15-postgres-memory-config.md)

---

## 📑 目录

- [一、结论概要](#一结论概要)
- [二、表空间概念与作用](#二表空间概念与作用)
- [三、创建链路：目录 → 表空间 → 数据库](#三创建链路目录--表空间--数据库)
- [四、用户授权体系](#四用户授权体系)
- [五、存储分层实战](#五存储分层实战)
- [六、管理操作：查询/修改/删除](#六管理操作查询修改删除)
- [七、易错点与最佳实践](#七易错点与最佳实践)
- [相关文档](#相关文档)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 一、结论概要

PostgreSQL **表空间（Tablespace）** 是物理存储位置的抽象，用于把不同对象分布到不同磁盘实现 **IO 分离与存储分层**：

| 要素 | 说明 |
|:-----|:-----|
| 创建前提 | 物理目录存在且属主为 `postgres` 系统用户 |
| 创建语法 | `CREATE TABLESPACE name OWNER user LOCATION '/path';` |
| 授权链路 | `CREATE USER → GRANT CONNECT ON DATABASE → GRANT USAGE ON TABLESPACE → GRANT 表权限` |
| 默认表空间 | `pg_default`（模板）、`pg_global`（系统表） |

**核心结论**：
1. **创建顺序严格**：目录 → 表空间 → 数据库/表，依赖关系不可乱
2. **表空间是授权链的中间层**：用户需 `USAGE` 权限才能在其中建对象
3. **核心价值 = 存储分层**：高频索引放 SSD、冷数据放 HDD，IO 隔离
4. **目录权限是最大坑**：目录必须 `postgres` 用户拥有且权限正确，否则创建失败

---

## 二、表空间概念与作用

### 2.1 逻辑层 vs 物理层

| 层级 | 示例 |
|:-----|:-----|
| 逻辑对象 | 表 / 索引（指定表空间） |
| 表空间 | tbs_mytest（逻辑名） |
| 物理目录 | /database/pg/pg_tbs/tbs_mytest（映射） |

- 表空间把"逻辑对象"与"物理路径"解耦
- 数据库可整体指定默认表空间，表/索引可单独指定

### 2.2 三个核心用途

| 用途 | 说明 | 示例 |
|:-----|:-----|:-----|
| **IO 分离** | 不同负载放到不同磁盘 | 日志表在 HDD，索引在 SSD |
| **存储分层** | 热/冷数据分级存储 | 热表 SSD、归档表 HDD |
| **空间管理** | 指定分区/挂载点 | 大表放扩容盘 |

---

## 三、创建链路：目录 → 表空间 → 数据库

### 3.1 Step 1: 创建物理目录（OS 层）

```bash
mkdir -p /database/pg/pg_tbs/tbs_mytest
chown -R postgres:postgres /database/pg/pg_tbs/tbs_mytest
```

- **关键**：目录属主必须为 `postgres`（或运行 PG 的系统用户）
- 权限建议 `700`：`chmod 700 /database/pg/pg_tbs/tbs_mytest`

### 3.2 Step 2: 创建用户（SQL 层）

```sql
CREATE ROLE pguser WITH LOGIN ENCRYPTED PASSWORD 'pguser';
```

- `ENCRYPTED` 按 `password_encryption` 设置存储（PG14+ 默认 scram-sha-256）

### 3.3 Step 3: 创建表空间

```sql
CREATE TABLESPACE tbs_mytest
  OWNER pguser
  LOCATION '/database/pg/pg_tbs/tbs_mytest';
```

- `OWNER` 指定属主（默认当前用户）
- `LOCATION` 必须指向 Step 1 创建且属主正确的目录

### 3.4 Step 4: 创建数据库（关联表空间）

```sql
CREATE DATABASE mytest
  OWNER pguser
  TABLESPACE tbs_mytest;
```

- 数据库默认存储位置 = 指定表空间
- 归属 pguser → 实现"用户-库-表空间"资源隔离

### 3.5 完整链路验证

```sql
-- verify tablespace & database
SELECT spcname, pg_tablespace_location(oid) AS path FROM pg_tablespace;
SELECT datname, dattablespace FROM pg_database WHERE datname = 'mytest';
```

### 3.6 量化速查

| 维度 | 量化值 | 说明 |
|:-----|:-------|:-----|
| 创建链路步骤 | 4 步 | 目录 → 用户 → 表空间 → 数据库 |
| 授权链层级 | 4 层 | 用户/数据库/表空间/对象 |
| 目录权限 | 700（rwx------） | postgres 属主 + 700 权限 |
| 默认表空间 | 2 个 | pg_default / pg_global |
| 迁移影响 | 100% 表重写 | SET TABLESPACE 重写整个表 |
| 存储分层收益 | SSD 0.1ms vs HDD 10ms（100 倍） | 索引放 SSD、冷数据放 HDD 的延迟差 |
| 大表迁移耗时 | 100GB 表约 10-30min | 视磁盘 IO 与表结构 |

---

## 四、用户授权体系

### 4.1 四层授权链

| 层级 | 命令 |
|:-----|:-----|
| 用户创建 | CREATE ROLE pguser ... |
| 数据库连接 | GRANT CONNECT ON DATABASE mytest TO pguser; |
| 表空间使用 | GRANT USAGE ON TABLESPACE tbs_mytest TO pguser; |
| 对象权限 | GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE ... TO pguser; |

### 4.2 完整授权脚本

```sql
-- create user with login
CREATE ROLE app_user WITH LOGIN PASSWORD 'secret';

-- database access
GRANT CONNECT ON DATABASE mytest TO app_user;

-- tablespace usage (needed to create objects in it)
GRANT USAGE ON TABLESPACE tbs_mytest TO app_user;

-- schema usage
GRANT USAGE ON SCHEMA public TO app_user;

-- table privileges (as needed)
GRANT SELECT, INSERT, UPDATE, DELETE
  ON ALL TABLES IN SCHEMA public TO app_user;
```

### 4.3 授权验证

```sql
-- tablespace privileges
SELECT spcname, spcacl FROM pg_tablespace WHERE spcname = 'tbs_mytest';

-- database-level privileges
SELECT datname, datacl FROM pg_database WHERE datname = 'mytest';
```

---

## 五、存储分层实战

### 5.1 典型场景：SSD 索引 + HDD 数据

```sql
-- create two tablespaces: ssd for indexes, hdd for data
CREATE TABLESPACE tbs_ssd LOCATION '/mnt/ssd/pg';
CREATE TABLESPACE tbs_hdd LOCATION '/mnt/hdd/pg';

-- data table on HDD, indexes on SSD
CREATE TABLE orders (...) TABLESPACE tbs_hdd;
CREATE INDEX idx_orders_uid ON orders(user_id) TABLESPACE tbs_ssd;
```

### 5.2 表/索引单独指定

```sql
-- move an existing table to another tablespace
ALTER TABLE orders SET TABLESPACE tbs_ssd;

-- move a specific index
ALTER INDEX idx_orders_uid SET TABLESPACE tbs_ssd;
```

### 5.3 决策要点

| 场景 | 建议 |
|:-----|:-----|
| 索引热（高频查询） | 索引放 SSD，数据放 HDD |
| 表热（全表扫描/大表） | 表放 SSD |
| 冷数据归档 | 整表迁 HDD |
| 混合负载 | 按对象粒度分配 |

> ⚠️ `ALTER TABLE SET TABLESPACE` 会重写整个表（IO 密集），大表需在维护窗口执行。

---

## 六、管理操作：查询/修改/删除

### 6.1 查询

```sql
-- all tablespaces with paths
SELECT spcname, pg_tablespace_location(oid) AS path, spcacl
FROM pg_tablespace;

-- tables in a specific tablespace
SELECT schemaname, tablename
FROM pg_tables
WHERE tablespace = 'tbs_mytest';
```

### 6.2 修改属主

```sql
ALTER TABLESPACE tbs_mytest OWNER TO new_owner;
```

### 6.3 删除（先清空对象）

```sql
-- move objects out first, then drop
ALTER TABLE orders SET TABLESPACE pg_default;
DROP TABLESPACE tbs_mytest;
```

- 表空间非空时无法删除，必须先迁移或删除其中对象

---

## 七、易错点与最佳实践

### 易错点

| # | 场景 | 坑 | 对策 |
|:-:|:-----|:---|:-----|
| 1 | 目录属主错误 | `permission denied` / 创建失败 | chown postgres + chmod 700 |
| 2 | 忘授 USAGE ON TABLESPACE | 用户无法在表空间建对象 | 授权链补全 |
| 3 | 只授表权限不授 schema | `permission denied for schema` | 三级链逐层 |
| 4 | 大表 SET TABLESPACE | 长时间重写锁表 | 维护窗口 + 评估影响 |
| 5 | 删非空表空间 | 报错 `tablespace is not empty` | 先迁移对象 |
| 6 | 数据库指定表空间后迁移 | 数据库级迁移影响面大 | 用 pg_dump/restore 或对象级迁移 |

### 最佳实践

1. **命名规范**：`tbs_<用途>`（如 tbs_ssd / tbs_archive），一目了然
2. **授权最小化**：应用用户只授所需 USAGE + 表权限，不授 ALL
3. **存储分层规划先行**：部署前确定 SSD/HDD 策略，避免事后大迁移
4. **目录与表空间一一对应**：一个物理目录一个表空间，便于审计
5. **定期检查空间分布**：`pg_tables` 按 tablespace 分组统计，发现异常分布

---

## 相关文档

- [PostgreSQL 核心对象模型](2026-08-15-postgres-core-concepts-db-schema-role.md) — 四级对象模型（含 Tablespace 层）
- [权限配置与验证](2026-08-15-postgres-privilege-config-verify.md) — 授权链完整实操
- [客户端认证配置 pg_hba](2026-08-15-postgres-hba-auth.md) — 连接认证层
- [内存配置建议](2026-08-15-postgres-memory-config.md) — 存储与缓存配合

---

## 参考来源

- CSDN：PostgreSQL创建表空间及用户授权（u010438126）
- [PostgreSQL 官方文档：CREATE TABLESPACE](https://www.postgresql.org/docs/current/sql-createtablespace.html)
- [PostgreSQL 官方文档：表空间](https://www.postgresql.org/docs/current/manage-ag-tablespaces.html)
- [PostgreSQL 官方文档：GRANT](https://www.postgresql.org/docs/current/sql-grant.html)

---

## Changelog

- 2026-08-15 v1.0: 首次深度加工（四步创建链路 + 四层授权链 + 存储分层实战 + 管理操作 + 6 易错点）
