# PostgreSQL 数据库迁移工具与跨数据库迁移指南

> **类型**: knowledge | **日期**: 2026-08-15 | **版本**: v1.0
> **来源**: [PostgreSQL Wiki - Converting from other Databases to PostgreSQL](https://wiki.postgresql.org/wiki/Converting_from_other_Databases_to_PostgreSQL)
> **配套**: [PostgreSQL vs MySQL 对象模型对比](2026-08-15-postgres-vs-mysql-object-model.md) / [CSV 导入错误解决](2026-08-15-postgres-csv-import-errors.md) / [表操作与数据操作](2026-08-15-postgres-table-dml-guide.md)

---

## 📑 目录

- [一、结论概要](#一结论概要)
- [二、迁移方法论](#二迁移方法论)
- [三、官方工具：pg_dump / pg_restore](#三官方工具pg_dump--pg_restore)
- [四、开源迁移工具](#四开源迁移工具)
- [五、商业工具](#五商业工具)
- [六、跨库差异要点](#六跨库差异要点)
- [七、易错点与最佳实践](#七易错点与最佳实践)
- [相关文档](#相关文档)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 一、结论概要

PostgreSQL 迁移分为 **同构（PG→PG）与异构（MySQL/Oracle→PG）** 两类，工具谱系覆盖官方/开源/商业三档：

| 场景 | 工具 | 类型 |
|:-----|:-----|:-----|
| PG→PG 备份恢复 | pg_dump / pg_restore | 官方 |
| MySQL/SQLite/MS SQL→PG | pgloader | 开源 |
| Oracle→PG | Ora2Pg | 开源 |
| 全栈 RDBMS→PG | Ispirer Toolkit | 商业 |
| 实时同步/CDC | DBConvert Streams | 商业 |

**核心结论**：
1. **迁移 = 五阶段**：分析 → DDL 生成 → 数据迁移 → SQL 转换 → 测试优化，缺一不可
2. **pg_dump 是同构迁移的黄金标准**：逻辑备份、跨版本、可选择性
3. **pgloader 是异构迁移首选开源工具**：自动类型映射 + 数据加载
4. **支持 25+ 数据库迁入 PG**：Oracle/MySQL/SQL Server/DB2 等

---

## 二、迁移方法论

### 2.1 五阶段流程

| 阶段 | 内容 | 产出 |
|:-----|:-----|:-----|
| 1. 分析 | 对象清单、依赖、数据量、约束 | 迁移清单 |
| 2. DDL 生成 | 表结构/索引/约束转换 | 建表脚本 |
| 3. 数据迁移 | 全量/增量搬运 | 数据一致性 |
| 4. SQL 转换 | 方言函数/语法改写 | 兼容 SQL |
| 5. 测试优化 | 数据校验 + 性能验证 | 验收报告 |

### 2.2 迁移决策要点

| 维度 | 考量 |
|:-----|:-----|
| 停机窗口 | 全量 vs 增量（CDC） |
| 数据量 | 小库工具直迁，大库分批 |
| 方言差异 | 函数/类型/自增/分页 |
| 回滚方案 | 保留源库至验收 |

---

## 三、官方工具：pg_dump / pg_restore

### 3.1 pg_dump（逻辑备份）

```bash
# plain SQL dump
pg_dump -h source -U user -d dbname -f backup.sql

# custom format (recommended, compressible + selective restore)
pg_dump -h source -U user -d dbname -Fc -f backup.dump

# schema only / data only
pg_dump -h source -U user -d dbname --schema-only -f schema.sql
pg_dump -h source -U user -d dbname --data-only -f data.sql

# specific table
pg_dump -h source -U user -d dbname -t public.orders -f orders.sql
```

### 3.2 pg_restore（恢复）

```bash
# restore custom format into target db
createdb -h target -U user newdb
pg_restore -h target -U user -d newdb backup.dump

# selective restore (table level)
pg_restore -h target -U user -d newdb -t public.orders backup.dump

# list contents
pg_restore -l backup.dump
```

### 3.3 参数要点

| 参数 | 用途 |
|:-----|:-----|
| `-Fc` | 自定义格式（压缩+选择性恢复） |
| `--schema-only` / `--data-only` | 结构/数据分离 |
| `-j N` | 并行恢复（pg_restore） |
| `--no-owner` | 忽略属主（跨用户迁移） |
| `--no-privileges` | 忽略权限（目标库另配） |

---

## 四、开源迁移工具

### 4.1 pgloader（MySQL/SQLite/MS SQL → PG）

```lisp
-- pgloader.load
LOAD DATABASE
  FROM mysql://user:pass@host/dbname
  INTO postgresql://user:pass@target/dbname

WITH include drop, create tables, create indexes, reset sequences

SET maintenance_work_mem TO '128MB',
    work_mem TO '12MB'

CAST type datetime to timestamptz drop default drop not null,
     type tinyint to boolean;
```

```bash
pgloader pgloader.load
```

- ✅ 自动类型映射、建表、数据加载、进度报告
- PostgreSQL 许可证，社区活跃

### 4.2 Ora2Pg（Oracle → PG）

```bash
# generate schema
ora2pg -t TABLE -c ora2pg.conf
# migrate data
ora2pg -t COPY -c ora2pg.conf
```

- 专攻 Oracle：PL/SQL 转换、类型映射、序列处理

### 4.3 其他开源

| 工具 | 源 | 特点 |
|:-----|:---|:-----|
| AWS DMS | 多源 | 云迁移 + CDC |
| Debezium | 多源 | 实时 CDC 到 PG |
| pgloader | MySQL/SQLite/MSSQL | 全自动 |

---

## 五、商业工具

| 工具 | 能力 | 特点 |
|:-----|:-----|:-----|
| Ispirer Toolkit | 全栈 RDBMS→PG | 自动迁移 + 代码转换 |
| Convertum.ru | 多库 | 30 天免费试用 |
| Move Solutions Toolkit | 全周期 | 覆盖分析到优化 |
| DBConvert Streams | 实时 CDC | 跨平台云集成 |
| Omni Loader | 高速加载 | 每秒百万级 |

- 商业工具价值：**自动化程度高 + 方言转换全 + 支持服务**
- 适合大型企业异构迁移（Oracle 存量大的场景）

---

## 六、跨库差异要点

### 6.1 常见方言差异（迁入 PG 需改写）

| 差异点 | MySQL/Oracle 写法 | PostgreSQL 写法 |
|:-------|:------------------|:----------------|
| 自增主键 | `AUTO_INCREMENT` / `IDENTITY` | `BIGSERIAL` / `GENERATED AS IDENTITY` |
| 分页 | `LIMIT a, b` | `LIMIT b OFFSET a` |
| 字符串连接 | `CONCAT()` / `\|\|` | `\|\|` / `CONCAT()` |
| 布尔 | `TINYINT(1)` | `BOOLEAN` |
| 大小写 | 列名大小写敏感 | 未引号标识符折叠小写 |
| 反引号 | `` `col` `` | 双引号 `"col"` |
| 日期函数 | `NOW()/CURDATE()` | `now()/CURRENT_DATE` |
| 类型转换 | `CAST(x AS type)` | 同 + `::` 简写 |

### 6.2 迁移测试清单

| 项 | 验证 |
|:---|:-----|
| 行数 | 每表 count 对比 |
| 约束 | 主键/外键/唯一生效 |
| 序列 | 自增连续性 |
| 视图/函数 | 编译通过 + 结果一致 |
| 性能 | 关键 SQL 执行计划合理 |
| 应用 | 连接串/驱动/事务行为 |

---

## 七、易错点与最佳实践

### 易错点

| # | 场景 | 坑 | 对策 |
|:-:|:-----|:---|:-----|
| 1 | 忽略方言差异 | 应用 SQL 报错 | 迁移前 SQL 审计 |
| 2 | 顺序恢复依赖 | 外键表先于主表 | 先 schema 后 data，或用 -Fc |
| 3 | 数据量估算错 | 停机窗口不够 | 预演 + 增量方案 |
| 4 | 忽略序列 | 插入主键冲突 | pg_dump 自动含序列，自定义迁移要重置 |
| 5 | 权限/属主丢失 | 恢复后连不上 | --no-owner + 目标库重配 |
| 6 | 无回滚预案 | 失败进退两难 | 保留源库快照 |

### 最佳实践

1. **先小后大**：先迁测试库验证全流程，再迁生产
2. **结构先行**：DDL 与数据分离，先建结构再导数据
3. **工具选型按量**：小库 pg_dump/pgloader，大库商业工具+DMS
4. **校验自动化**：行数/约束/关键查询对比写成脚本
5. **回滚预案**：源库保留至验收通过
6. **性能测试**：迁移后跑压测，确认索引/参数达标

---

## 相关文档

- [PostgreSQL vs MySQL 对象模型对比](2026-08-15-postgres-vs-mysql-object-model.md) — 迁移差异详表
- [CSV 导入错误解决](2026-08-15-postgres-csv-import-errors.md) — 数据搬运细节
- [表操作与数据操作](2026-08-15-postgres-table-dml-guide.md) — 目标库操作基础
- [核心函数与操作](2026-08-15-postgres-core-functions.md) — 函数改写对照

---

## 参考来源

- PostgreSQL Wiki：Converting from other Databases to PostgreSQL
- [PostgreSQL 官方文档：pg_dump](https://www.postgresql.org/docs/current/app-pgdump.html)
- [pgloader 官方文档](https://pgloader.readthedocs.io/)
- [Ora2Pg 官方](https://ora2pg.darold.net/)

---

## Changelog

- 2026-08-15 v1.0: 首次深度加工（五阶段方法论 + 官方/开源/商业三档工具 + 方言差异表 + 测试清单 + 6 易错点）
