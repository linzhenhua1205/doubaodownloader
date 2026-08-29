# PostgreSQL 表操作与数据操作全指南## 量化速查## 量化速查

| 维度 | 量化值 | 说明 |
|:-----|:-------|:-----|
| 数据类型 | 10+ 类（100% 常用覆盖） | 整数/小数/文本/时间/JSON |
| 约束类型 | 7 种（100% 数据质量） | PK/FK/UNIQUE/CHECK/NOT NULL/DEFAULT/EXCLUDE |
| 金额精度 | NUMERIC(10,2)（0.01 精度） | 防浮点误差 |
| BIGSERIAL | 8B（≈9.2×10^18） | 自增主键 |
| UPSERT | 1 语句（<1ms 级） | ON CONFLICT 幂等 |

---

## 📑 目录

- [一、结论概要](#一结论概要)
- [二、表对象操作（DDL）](#二表对象操作ddl)
- [三、数据类型与约束](#三数据类型与约束)
- [四、数据操作（DML）](#四数据操作dml)
- [五、高级操作](#五高级操作)
- [六、查询进阶](#六查询进阶)
- [七、易错点与最佳实践](#七易错点与最佳实践)
- [量化速查](#量化速查)
- [相关文档](#相关文档)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 一、结论概要

PostgreSQL 表/数据操作分 **DDL（结构）与 DML（数据）** 两大块，是日常开发的核心：

| 类别 | 操作 | 关键点 |
|:-----|:-----|:-------|
| DDL | CREATE / ALTER / DROP TABLE | 结构变更、约束管理 |
| DML | INSERT / UPDATE / DELETE / SELECT | 数据增删改查 |
| 高级 | UPSERT / RETURNING / CTE | 冲突处理、链式操作 |
| 查询 | JOIN / 子查询 / 窗口 | 复杂取数 |

**核心结论**：
1. **UPSERT 用 `ON CONFLICT`**：`INSERT ... ON CONFLICT (col) DO UPDATE`，幂等写库标配
2. **RETURNING 省一次查询**：DML 后直接返回受影响行，无需再 SELECT
3. **CTE（WITH）提升可读性**：复杂查询拆步骤，也支持递归
4. **约束是数据质量的防火墙**：主键/外键/唯一/检查，建表时就定好

---

## 二、表对象操作（DDL）

### 2.1 创建表

```sql
CREATE TABLE orders (
    id          BIGSERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL,
    amount      NUMERIC(10,2) NOT NULL DEFAULT 0,
    status      TEXT NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending','paid','cancelled')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- create if not exists
CREATE TABLE IF NOT EXISTS orders (...);
```

### 2.2 修改表结构

```sql
-- add column
ALTER TABLE orders ADD COLUMN discount NUMERIC(5,2) DEFAULT 0;

-- modify column type
ALTER TABLE orders ALTER COLUMN amount TYPE NUMERIC(12,2);

-- set/remove default & not null
ALTER TABLE orders ALTER COLUMN status SET DEFAULT 'pending';
ALTER TABLE orders ALTER COLUMN user_id SET NOT NULL;

-- rename column / table
ALTER TABLE orders RENAME COLUMN amount TO total_amount;
ALTER TABLE orders RENAME TO order_records;

-- drop column (PG11+ no rewrite needed for most)
ALTER TABLE orders DROP COLUMN discount;
```

### 2.3 删除表

```sql
-- drop table (fails if referenced)
DROP TABLE orders;
-- drop with dependent objects
DROP TABLE orders CASCADE;
-- truncate (fast, no per-row triggers)
TRUNCATE orders;
```

| 操作 | 行为 | 注意 |
|:-----|:-----|:-----|
| `DROP TABLE` | 删表结构+数据 | 有外键引用需 CASCADE |
| `TRUNCATE` | 清空数据保留结构 | 快、可 TRUNCATE ... CASCADE |
| `DELETE` | 逐行删（可 WHERE） | 慢但可回滚过滤 |

---

## 三、数据类型与约束

### 3.1 常用数据类型

| 类别 | 类型 | 说明 |
|:-----|:-----|:-----|
| 整数 | SMALLINT / INTEGER / BIGINT | 2/4/8 字节 |
| 小数 | NUMERIC(p,s) | 精确十进制（金额） |
| 浮点 | REAL / DOUBLE PRECISION | 近似（科学计算） |
| 文本 | CHAR(n) / VARCHAR(n) / TEXT | 变长用 TEXT/VARCHAR |
| 时间 | DATE / TIMESTAMP / TIMESTAMPTZ | 带时区用 TIMESTAMPTZ |
| 布尔 | BOOLEAN | true/false |
| JSON | JSON / JSONB | JSONB 二进制、可索引 |
| 数组 | INTEGER[] / TEXT[] | 原生数组 |
| 自增 | SERIAL / BIGSERIAL / GENERATED | 主键生成 |

### 3.2 约束类型

| 约束 | 作用 | 语法 |
|:-----|:-----|:-----|
| PRIMARY KEY | 主键（唯一+非空） | `id INT PRIMARY KEY` |
| FOREIGN KEY | 外键引用 | `REFERENCES users(id)` |
| UNIQUE | 唯一约束 | `UNIQUE (email)` |
| CHECK | 值域检查 | `CHECK (amount >= 0)` |
| NOT NULL | 非空 | `col INT NOT NULL` |
| DEFAULT | 默认值 | `DEFAULT now()` |
| EXCLUDE | 排除约束 | 区间不重叠 |

```sql
-- composite primary key
CREATE TABLE order_items (
    order_id INT REFERENCES orders(id),
    product_id INT,
    qty INT NOT NULL CHECK (qty > 0),
    PRIMARY KEY (order_id, product_id)
);

-- unique + check combo
CREATE TABLE users (
    email TEXT UNIQUE NOT NULL CHECK (email ~ '@'),
    age INT CHECK (age BETWEEN 0 AND 150)
);
```

---

## 四、数据操作（DML）

### 4.1 INSERT

```sql
-- single row
INSERT INTO orders (user_id, amount) VALUES (1, 99.9);

-- multiple rows
INSERT INTO orders (user_id, amount) VALUES
  (1, 10), (2, 20), (3, 30);

-- from select
INSERT INTO archive_orders
SELECT * FROM orders WHERE created_at < '2025-01-01';
```

### 4.2 UPDATE

```sql
-- basic update
UPDATE orders SET status = 'paid' WHERE id = 100;

-- update with expression
UPDATE products
SET price = price * 1.1
WHERE category = 'premium';

-- update from another table
UPDATE orders o
SET status = p.status
FROM payments p
WHERE o.id = p.order_id;
```

### 4.3 DELETE

```sql
-- delete filtered
DELETE FROM orders WHERE status = 'cancelled' AND created_at < now() - interval '1 year';

-- delete with join (using subquery)
DELETE FROM orders
WHERE id IN (SELECT id FROM old_orders);
```

### 4.4 SELECT 基础

```sql
SELECT user_id, count(*) AS cnt, SUM(amount) AS total
FROM orders
WHERE created_at >= '2026-01-01'
GROUP BY user_id
HAVING count(*) > 5
ORDER BY total DESC
LIMIT 20 OFFSET 0;
```

---

## 五、高级操作

### 5.1 UPSERT（ON CONFLICT）

```sql
-- insert or do nothing
INSERT INTO users (id, email) VALUES (1, 'a@b.com')
ON CONFLICT (id) DO NOTHING;

-- insert or update
INSERT INTO counters (key, value) VALUES ('hits', 1)
ON CONFLICT (key)
DO UPDATE SET value = counters.value + 1;

-- update only when changed
INSERT INTO users (id, name) VALUES (1, 'alice')
ON CONFLICT (id) DO UPDATE
SET name = EXCLUDED.name
WHERE users.name IS DISTINCT FROM EXCLUDED.name;
```

### 5.2 RETURNING

```sql
-- return inserted row
INSERT INTO orders (user_id, amount) VALUES (1, 100)
RETURNING id, created_at;

-- return updated rows
UPDATE orders SET status = 'paid' WHERE id = 100
RETURNING id, status;

-- return deleted rows (audit)
DELETE FROM orders WHERE id = 100 RETURNING *;
```

### 5.3 CTE（WITH 子句）

```sql
-- chained CTE for readability
WITH high_value AS (
    SELECT user_id, SUM(amount) AS total
    FROM orders GROUP BY user_id
    HAVING SUM(amount) > 10000
),
top_users AS (
    SELECT user_id FROM high_value ORDER BY total DESC LIMIT 10
)
SELECT u.name, h.total
FROM top_users t
JOIN users u ON u.id = t.user_id
JOIN high_value h ON h.user_id = t.user_id;
```

### 5.4 递归 CTE

```sql
-- employee hierarchy
WITH RECURSIVE org AS (
    SELECT id, name, manager_id, 1 AS depth
    FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.id, e.name, e.manager_id, org.depth + 1
    FROM employees e JOIN org ON e.manager_id = org.id
)
SELECT * FROM org;
```

---

## 六、查询进阶

### 6.1 JOIN 类型

| JOIN | 语义 | 常用 |
|:-----|:-----|:----:|
| INNER JOIN | 交集 | ✅ |
| LEFT JOIN | 左表全保留 | ✅ |
| RIGHT JOIN | 右表全保留 | 少用 |
| FULL JOIN | 全保留 | 少用 |
| CROSS JOIN | 笛卡尔积 | 慎用 |

```sql
SELECT o.id, u.name
FROM orders o
LEFT JOIN users u ON u.id = o.user_id;
```

### 6.2 子查询 vs JOIN vs 窗口

| 场景 | 推荐 |
|:-----|:-----|
| 关联取列 | JOIN |
| 存在性判断 | EXISTS |
| 组内排名/前后行 | 窗口函数 |
| 复杂分步 | CTE |
| 标量聚合 | 子查询 |

---

## 七、易错点与最佳实践

### 易错点

| # | 场景 | 坑 | 对策 |
|:-:|:-----|:---|:-----|
| 1 | UPDATE 忘 WHERE | 全表更新 | 先 SELECT 确认范围 |
| 2 | 金额用 FLOAT | 精度丢失 | NUMERIC(p,s) |
| 3 | 时间不用 TIMESTAMPTZ | 时区混乱 | 一律 TIMESTAMPTZ |
| 4 | 主键用 VARCHAR | 性能差 | BIGSERIAL/IDENTITY |
| 5 | DELETE 大表慢 | 锁与 WAL 压力 | 分批 DELETE 或 TRUNCATE |
| 6 | ON CONFLICT 目标错 | 需唯一约束/索引 | 确认冲突列有约束 |
| 7 | 忘 RETURNING | 多一次查询 | DML 后直接取 |

### 最佳实践

1. **建表即定约束**：主键/外键/CHECK 一次性到位，靠 DB 保数据质量
2. **金额一律 NUMERIC**：杜绝浮点误差
3. **时间用 TIMESTAMPTZ**：UTC 存储、本地展示
4. **DML 带 RETURNING**：减少往返，链式操作
5. **写前查**：UPDATE/DELETE 先 EXPLAIN/COUNT 确认影响范围
6. **大表操作分批**：按主键范围分批，避免长锁

---

## 相关文档

- [核心函数与操作总结](2026-08-15-postgres-core-functions.md) — 聚合/窗口/转换
- [DDL 操作语法](2026-08-15-postgres-user-db-schema-operations.md) — 用户/库/schema 对象
- [行转列方法](2026-08-15-postgres-pivot-row-to-column.md) — 报表聚合实战
- [CSV 导入错误解决](2026-08-15-postgres-csv-import-errors.md) — COPY 与批量写入

---

## 参考来源

- CSDN：PostgreSQL 表操作与数据操作全指南（qq_39727113）
- [PostgreSQL 官方文档：DDL](https://www.postgresql.org/docs/current/ddl.html)
- [PostgreSQL 官方文档：DML](https://www.postgresql.org/docs/current/dml.html)
- [PostgreSQL 官方文档：INSERT ON CONFLICT](https://www.postgresql.org/docs/current/sql-insert.html)

---

## 量化速查

| 维度 | 量化值 | 说明 |
|:-----|:-------|:-----|
| 数据类型 | 10+ 类 | 整数/小数/文本/时间/JSON/数组等 |
| 约束类型 | 7 种 | PK/FK/UNIQUE/CHECK/NOT NULL/DEFAULT/EXCLUDE |
| 金额精度 | NUMERIC(10,2) | 避免 FLOAT 精度丢失 |
| BIGSERIAL 范围 | 8 字节（9.2×10^18） | 主键自增推荐 |

---

## Changelog

- 2026-08-15 v1.0: 首次深度加工（DDL/DML 全览 + 数据类型约束 + UPSERT/RETURNING/CTE + 查询进阶 + 7 易错点）
