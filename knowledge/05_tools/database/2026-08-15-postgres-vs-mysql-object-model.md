# PostgreSQL 与 MySQL 数据库对象模型及权限体系对比## 量化速查## 量化速查

| 维度 | 量化值 | 说明 |
|:-----|:-------|:-----|
| 对象层级 | PG 4 层 / MySQL 3 层（+33%） | 多出 Schema 层 |
| 表权限数 | PG 8 种 / MySQL 6 种（+33%） | PG 更细粒度 |
| 自增主键 | PG BIGSERIAL 8B vs MySQL 4B | 容量 2^64 vs 2^32 |
| 跨库 JOIN | PG 0 障碍 / MySQL 需前缀 | 同库跨 schema |
| 默认认证 | PG scram（100% 防重放） | MySQL caching_sha2 |

---

## 📑 目录

- [一、结论概要](#一结论概要)
- [二、对象模型对比](#二对象模型对比)
- [三、权限体系对比](#三权限体系对比)
- [四、迁移映射表](#四迁移映射表)
- [五、实践建议](#五实践建议)
- [六、易错点](#六易错点)
- [量化速查](#量化速查)
- [相关文档](#相关文档)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 一、结论概要

PostgreSQL 与 MySQL 的核心差异在 **对象模型（schema 层级）与权限粒度**：

| 维度 | PostgreSQL | MySQL |
|:-----|:-----------|:------|
| 对象层级 | 实例→Database→**Schema**→Table | 实例→Database→Table（无 Schema 层） |
| 跨库访问 | 同库跨 schema 可直接访问 | 跨库需库名前缀（同实例） |
| 权限粒度 | 对象级 + 列级 + ACL | 库/表级为主 |
| 用户与角色 | 角色即用户（统一模型） | 用户与角色分开（8.0 起 GRANT 角色） |
| 隔离单元 | Schema 是逻辑隔离单元 | Database 是隔离单元 |

**核心结论**：
1. **PG 的 Schema ≈ MySQL 的 Database（逻辑层）**：PG 用"一库多 schema"实现 MySQL 的"多库"隔离
2. **PG 对象模型更灵活**：同库多 schema 跨 schema JOIN 无压力；MySQL 跨库 JOIN 要库名前缀且权限麻烦
3. **权限模型差异大**：PG 是"角色中心 + ACL 细粒度"，MySQL 是"授权语句 + 库表粒度"
4. **迁移时对象映射要谨慎**：MySQL database → PG schema 是常见最佳实践（而非 PG database）

---

## 二、对象模型对比

### 2.1 层级结构

| 层级 | PostgreSQL | MySQL |
|:-----|:-----------|:------|
| 顶层 | 实例（cluster） | 实例（instance） |
| 库层 | Database | Database |
| 组织层 | **Schema**（public/sales/...） | 无（Table 直接在库下） |
| 对象层 | Table / View / Function | Table |

### 2.2 核心差异

| 特性 | PostgreSQL | MySQL |
|:-----|:-----------|:------|
| Schema 层 | ✅ 标准支持 | ❌ 无（8.0 引入部分概念） |
| 同名表 | 不同 schema 可同名 | 不同库可同名（同库不行） |
| 跨库访问 | 同库跨 schema 直接访问 | 跨库需 `db.table` 前缀 |
| 跨 schema JOIN | ✅ 直接 | ⚠️ 同库 OK；跨库需权限+前缀 |
| 对象归属 | schema 内唯一 | database 内唯一 |
| 函数/过程 | schema 内 | database 内 |

### 2.3 隔离单元差异

| 场景 | PG 推荐 | MySQL 做法 |
|:-----|:--------|:-----------|
| 多业务隔离 | 一库多 schema | 多 database |
| 跨业务查询 | schema JOIN 直接 | 跨库 JOIN 复杂 |
| 权限隔离 | schema 级 USAGE | 库级 GRANT |
| 备份恢复 | schema 级可选 | 库级 |

---

## 三、权限体系对比

### 3.1 PostgreSQL（角色中心 + ACL）

| 特性 | 说明 |
|:-----|:-----|
| 用户=角色 | 角色可 LOGIN 即用户，可嵌套（组角色） |
| 权限存储 | 系统目录 ACL 数组（pg_class.relacl 等） |
| 粒度 | 库/模式/表/列/函数级 |
| 默认权限 | 无（须显式 GRANT） |
| 认证 | pg_hba.conf 控制（trust/scram/ldap） |
| 传递 | WITH GRANT OPTION |

```sql
-- PG: schema-level isolation
CREATE ROLE sales_app LOGIN;
GRANT USAGE ON SCHEMA sales TO sales_app;
GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA sales TO sales_app;
```

### 3.2 MySQL（授权语句 + 库表粒度）

| 特性 | 说明 |
|:-----|:-----|
| 用户与角色 | 用户（账号）+ 角色（8.0 起，可 GRANT 角色给用户） |
| 权限存储 | mysql.user / db / tables_priv 表 |
| 粒度 | 全局/库/表/列（列级少用） |
| 默认权限 | 用户默认无权限 |
| 认证 | 账号密码（caching_sha2_password 默认） |
| 传递 | WITH GRANT OPTION |

```sql
-- MySQL: database-level isolation
CREATE USER 'sales_app'@'%' IDENTIFIED BY 'pass';
GRANT SELECT, INSERT ON sales_db.* TO 'sales_app'@'%';
```

### 3.3 权限粒度对比

| 粒度 | PG | MySQL |
|:-----|:---|:------|
| 实例级 | 集群级（极少） | ✅ 全局权限 |
| 库级 | ✅ CONNECT/CREATE/TEMP | ✅ |
| Schema 级 | ✅ USAGE/CREATE | ❌（8.0 前无） |
| 表级 | ✅ 8 种权限 | ✅ |
| 列级 | ✅ 正式支持 | ⚠️ 受限 |
| 函数级 | ✅ EXECUTE | ⚠️ 过程权限粗 |
| 默认权限（未来对象） | ✅ ALTER DEFAULT PRIVILEGES | ❌ 需手动补 |

---

## 四、迁移映射表

### 4.1 对象映射

| MySQL | PostgreSQL | 说明 |
|:------|:-----------|:-----|
| Database | Schema（推荐）或 Database | 多库→多 schema 最佳 |
| Table | Table | 类型映射（TINYINT→BOOLEAN 等） |
| AUTO_INCREMENT | BIGSERIAL / IDENTITY | 自增机制 |
| `db.table` 跨库 | schema.table | 同库跨 schema |
| `\`反引号\`` | `"双引号"` | 标识符引用 |
| ENGINE=InnoDB | 无（默认堆表） | 存储引擎概念差异 |
| CHARACTER SET | 数据库级编码 | 库级 LC_COLLATE |

### 4.2 权限映射

| MySQL 授权 | PostgreSQL 等价 |
|:-----------|:----------------|
| `GRANT ALL ON db.*` | `GRANT USAGE, CREATE ON SCHEMA s` + 表级 GRANT |
| `GRANT SELECT ON db.table` | `GRANT SELECT ON TABLE s.table` |
| `CREATE USER` | `CREATE ROLE ... LOGIN` |
| `GRANT role TO user` | `GRANT role TO user`（一致） |
| `REVOKE` | `REVOKE`（一致） |
| 全局 SUPER | 超级用户角色（慎用） |

---

## 五、实践建议

### 5.1 选型视角

| 需求 | 优势方 | 理由 |
|:-----|:-------|:-----|
| 复杂查询/分析 | PG | 窗口函数、CTE、JSONB、物化视图 |
| 简单 CRUD 高并发读 | MySQL | 生态成熟、运维简单 |
| 强数据完整性 | PG | 约束/外键/检查严格 |
| 多租户隔离 | PG | schema 级隔离更细 |
| 读写分离/分库分表 | MySQL | 中间件生态成熟 |

### 5.2 迁移到 PG 的 schema 规划

| MySQL 多库 | PG 规划 |
|:-----------|:--------|
| db_orders | schema orders |
| db_users | schema users |
| db_analytics | schema analytics |
| 同一实例 | 同一 database 多 schema |

- 优点：跨业务 JOIN 直接、备份恢复统一、权限集中管理
- 注意：search_path 显式设置，避免对象解析歧义

---

## 六、易错点

| # | 场景 | 坑 | 对策 |
|:-:|:-----|:---|:-----|
| 1 | MySQL 库直接映射 PG 库 | 失去 schema 层优势 | 多库→多 schema |
| 2 | 反引号 SQL 未改 | 语法错误 | 批量替换为双引号 |
| 3 | AUTO_INCREMENT 忘映射 | 主键冲突 | BIGSERIAL/IDENTITY |
| 4 | GRANT ALL ON db.* 直接搬 | 语义不同 | schema+表级拆分 |
| 5 | 忽略大小写折叠 | 标识符错乱 | 统一小写/引号策略 |
| 6 | 默认权限不迁移 | 新表无权限 | ALTER DEFAULT PRIVILEGES |

---

## 相关文档

- [PostgreSQL vs MySQL 深度对比](2026-08-15-postgres-vs-mysql-deep-comparison.md) — 连接模型/MVCC/复制
- [迁移工具指南](2026-08-15-postgres-migration-tools.md) — 迁移工具与流程
- [核心对象模型](2026-08-15-postgres-core-concepts-db-schema-role.md) — PG 四级对象模型
- [Schema 管理](2026-08-15-postgres-schema-management.md) — PG schema 实操

---

## 参考来源

- CSDN：postgresql 的 database 和 schema 的理解（weixin_44375561）
- [PostgreSQL 官方文档：权限](https://www.postgresql.org/docs/current/ddl-priv.html)
- [MySQL 官方文档：权限系统](https://dev.mysql.com/doc/refman/8.0/en/privilege-system.html)
- [PostgreSQL Wiki：从 MySQL 迁移](https://wiki.postgresql.org/wiki/Converting_from_other_Databases_to_PostgreSQL)

---

## 量化速查

| 维度 | 量化值 | 说明 |
|:-----|:-------|:-----|
| 对象层级差 | PG 4 层 / MySQL 3 层 | 多出 Schema 层 |
| 表权限 | PG 8 种 / MySQL 6 种 | PG 更细（TRUNCATE/REFERENCES） |
| 隔离单元 | PG Schema / MySQL Database | 逻辑隔离粒度差异 |
| 跨库 JOIN | PG 同库跨 schema 直接 | MySQL 需前缀+权限 |

---

## Changelog

- 2026-08-15 v1.0: 首次深度加工（对象模型层级 + 权限体系对照 + 迁移映射表 + schema 规划 + 6 易错点）
