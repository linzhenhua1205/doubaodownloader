# PostgreSQL 核心函数与操作总结## 量化速查## 量化速查

| 维度 | 量化值 | 说明 |
|:-----|:-------|:-----|
| 函数类别 | 6 类（100% 覆盖常用） | 数学/字符串/日期/聚合/窗口/转换 |
| LENGTH 语义 | 按字符（UTF-8 1-4B） | 中文按字符计 |
| date_trunc 单位 | 6 种（100% 覆盖报表粒度） | hour/day/week/month/quarter/year |
| 窗口排名 | 4 种（ROW_NUMBER 等） | 分析场景 |
| BIGSERIAL 范围 | 8B（≈9.2×10^18） | 主键自增 |

---

## 📑 目录

- [一、结论概要](#一结论概要)
- [二、数学函数](#二数学函数)
- [三、字符串函数](#三字符串函数)
- [四、日期时间函数](#四日期时间函数)
- [五、聚合函数](#五聚合函数)
- [六、窗口函数](#六窗口函数)
- [七、类型转换与空值处理](#七类型转换与空值处理)
- [八、易错点与最佳实践](#八易错点与最佳实践)
- [量化速查](#量化速查)
- [相关文档](#相关文档)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 一、结论概要

PostgreSQL 函数体系覆盖 **六大类**，是日常 SQL 的基石：

| 类别 | 代表函数 | 典型场景 |
|:-----|:---------|:---------|
| 数学 | ABS / ROUND / CEIL / FLOOR / POWER / SQRT / RANDOM | 计算/取整 |
| 字符串 | CONCAT / LENGTH / UPPER / SUBSTRING / REPLACE | 文本处理 |
| 日期时间 | CURRENT_DATE / EXTRACT / AGE / date_trunc | 时间分析 |
| 聚合 | COUNT / SUM / AVG / MIN / MAX | 分组统计 |
| 窗口 | ROW_NUMBER / RANK / LAG / LEAD | 排名/前后行 |
| 转换/空值 | CAST / COALESCE / NULLIF | 数据清洗 |

**核心结论**：
1. **窗口函数是分析场景的王牌**：ROW_NUMBER/RANK 排名、LAG/LEAD 前后行，无需自连接
2. **date_trunc + EXTRACT 是时间分析的黄金组合**：按天/月/周聚合报表
3. **COALESCE/NULLIF 是数据清洗标配**：空值兜底与除零保护
4. **函数可组合**：多层嵌套实现复杂逻辑，先拆解再组合

---

## 二、数学函数

| 函数 | 说明 | 示例 |
|:-----|:-----|:-----|
| `ABS(x)` | 绝对值 | `ABS(-5)` → 5 |
| `ROUND(x, n)` | 四舍五入 | `ROUND(3.14159, 2)` → 3.14 |
| `CEIL(x)` / `FLOOR(x)` | 向上/向下取整 | `CEIL(2.1)` → 3，`FLOOR(2.9)` → 2 |
| `POWER(x, y)` | 幂运算 | `POWER(2, 10)` → 1024 |
| `SQRT(x)` | 平方根 | `SQRT(16)` → 4 |
| `RANDOM()` | 0-1 随机数 | `RANDOM()` → 0.xxx |
| `MOD(x, y)` | 取模 | `MOD(7, 3)` → 1 |

```sql
-- rounding with precision
SELECT ROUND(price, 2) FROM products;

-- random sampling
SELECT * FROM orders ORDER BY RANDOM() LIMIT 10;
```

---

## 三、字符串函数

| 函数 | 说明 | 示例 |
|:-----|:-----|:-----|
| `CONCAT(a, b, ...)` | 连接（忽略 NULL） | `CONCAT('a', 'b')` → ab |
| `LENGTH(s)` | 字符长度 | `LENGTH('hello')` → 5 |
| `UPPER(s)` / `LOWER(s)` | 大小写 | `UPPER('ab')` → AB |
| `SUBSTRING(s, start, len)` | 子串 | `SUBSTRING('hello', 2, 3)` → ell |
| `REPLACE(s, from, to)` | 替换 | `REPLACE('a-b', '-', '_')` → a_b |
| `TRIM(s)` | 去空格 | `TRIM('  hi  ')` → hi |
| `SPLIT_PART(s, d, n)` | 按分隔符取段 | `SPLIT_PART('a,b,c', ',', 2)` → b |
| `STRING_AGG(v, d)` | 聚合拼接 | 见聚合 |

```sql
-- full name composition
SELECT CONCAT(first_name, ' ', last_name) AS full_name FROM users;

-- extract domain from email
SELECT SPLIT_PART(email, '@', 2) AS domain FROM users;
```

---

## 四、日期时间函数

| 函数 | 说明 | 示例 |
|:-----|:-----|:-----|
| `CURRENT_DATE` | 当前日期 | `2026-08-15` |
| `CURRENT_TIMESTAMP` | 当前时间戳 | `2026-08-15 15:30:00` |
| `EXTRACT(field FROM ts)` | 提取字段 | `EXTRACT(YEAR FROM ts)` → 2026 |
| `AGE(a, b)` | 年龄差 | `AGE(now(), birth)` |
| `date_trunc(field, ts)` | 截断到单位 | `date_trunc('month', ts)` |
| `NOW()` | 当前时间 | 同 CURRENT_TIMESTAMP |
| `TO_CHAR(ts, fmt)` | 格式化 | `TO_CHAR(now(), 'YYYY-MM-DD')` |

```sql
-- group by day
SELECT date_trunc('day', created_at) AS day, count(*)
FROM orders GROUP BY 1 ORDER BY 1;

-- age calculation
SELECT name, AGE(now(), birth_date) FROM users;

-- last 7 days
SELECT * FROM orders WHERE created_at > NOW() - INTERVAL '7 days';
```

### date_trunc 常用单位

| 单位 | 结果粒度 |
|:-----|:---------|
| `hour` / `day` / `week` / `month` / `quarter` / `year` | 对应粒度起点 |

---

## 五、聚合函数

| 函数 | 说明 | 示例 |
|:-----|:-----|:-----|
| `COUNT(*)` | 行数 | `COUNT(*) FROM orders` |
| `COUNT(DISTINCT col)` | 去重计数 | `COUNT(DISTINCT user_id)` |
| `SUM(col)` | 求和 | `SUM(amount)` |
| `AVG(col)` | 平均 | `AVG(price)` |
| `MIN` / `MAX` | 极值 | `MAX(created_at)` |
| `STRING_AGG(col, ',')` | 拼接 | `STRING_AGG(name, ',')` |
| `ARRAY_AGG(col)` | 数组聚合 | `ARRAY_AGG(product_id)` |

```sql
-- group stats with HAVING
SELECT category, count(*) AS cnt, SUM(amount) AS total
FROM orders
GROUP BY category
HAVING count(*) > 100
ORDER BY total DESC;

-- csv list per group
SELECT category, STRING_AGG(product_name, ', ') AS products
FROM products GROUP BY category;
```

---

## 六、窗口函数

### 6.1 排名类

| 函数 | 行为 | 示例 |
|:-----|:-----|:-----|
| `ROW_NUMBER()` | 行号（无并列） | 1,2,3,4 |
| `RANK()` | 排名（并列跳号） | 1,1,3,4 |
| `DENSE_RANK()` | 排名（并列不跳号） | 1,1,2,3 |
| `NTILE(n)` | 分桶 | 前 10% 等 |

```sql
-- top 3 per category
SELECT category, product_id, amount,
       ROW_NUMBER() OVER (PARTITION BY category ORDER BY amount DESC) AS rn
FROM sales
QUALIFY rn <= 3;  -- PG16+; PG15- use subquery
```

### 6.2 前后行/累计类

| 函数 | 说明 | 示例 |
|:-----|:-----|:-----|
| `LAG(col, n)` | 前 n 行 | 环比 |
| `LEAD(col, n)` | 后 n 行 | 下期预测 |
| `SUM() OVER (...)` | 累计和 | 滚动合计 |
| `AVG() OVER (...)` | 移动平均 | 平滑曲线 |

```sql
-- month-over-month change
SELECT month, amount,
       LAG(amount) OVER (ORDER BY month) AS prev_amount,
       amount - LAG(amount) OVER (ORDER BY month) AS delta
FROM monthly_sales;

-- running total
SELECT order_date, amount,
       SUM(amount) OVER (ORDER BY order_date) AS running_total
FROM orders;
```

### 6.3 窗口函数 vs GROUP BY

| 维度 | GROUP BY | 窗口函数 |
|:-----|:---------|:---------|
| 行数 | 压缩为组 | 保持原行 |
| 用途 | 汇总报表 | 组内排名/前后行/累计 |
| 语法 | 简单 | `OVER (PARTITION BY ... ORDER BY ...)` |

---

## 七、类型转换与空值处理

### 7.1 类型转换

```sql
-- cast syntax
SELECT CAST('123' AS INTEGER);
SELECT '123'::INTEGER;        -- shorthand

-- string to date
SELECT '2026-08-15'::DATE;
SELECT TO_DATE('2026/08/15', 'YYYY/MM/DD');
```

### 7.2 空值处理

```sql
-- COALESCE: first non-null
SELECT COALESCE(phone, 'unknown') FROM users;

-- NULLIF: null if equal (division guard)
SELECT amount / NULLIF(total, 0) FROM stats;

-- IS NULL checks
SELECT * FROM users WHERE email IS NULL;
```

| 函数 | 作用 |
|:-----|:-----|
| `COALESCE(a, b, c)` | 返回第一个非 NULL |
| `NULLIF(a, b)` | a=b 返回 NULL（防除零） |
| `IS NULL` / `IS NOT NULL` | 空值判断 |

---

## 八、易错点与最佳实践

### 易错点

| # | 场景 | 坑 | 对策 |
|:-:|:-----|:---|:-----|
| 1 | LENGTH 用错语义 | 中文算字符数（UTF-8 下正确） | 需字节数用 octet_length |
| 2 | 除零报错 | amount/total 全 0 | NULLIF 保护 |
| 3 | 窗口函数忘 PARTITION | 全局排名非组内 | 明确分区 |
| 4 | GROUP BY 后 SELECT 非聚合列 | 报错/歧义 | 列都聚合或进 GROUP BY |
| 5 | 日期直接比较字符串 | 类型不匹配 | 显式 CAST |
| 6 | RANDOM() 用于抽样大表 | 全表扫描性能差 | TABLESAMPLE 或优化 |

### 最佳实践

1. **函数手册化**：常用函数写成速查文档（本文即参考）
2. **窗口函数优先**：排名/环比/累计用窗口而非自连接
3. **date_trunc 统一报表粒度**：按天/月聚合口径一致
4. **COALESCE 兜底显示层**：展示层空值统一处理
5. **EXPLAIN 验证**：窗口函数大表注意内存与排序开销

---

## 相关文档

- [表操作与数据操作全指南](2026-08-15-postgres-table-dml-guide.md) — DML 与查询
- [行转列方法](2026-08-15-postgres-pivot-row-to-column.md) — 聚合+窗口组合实战
- [CSV 导入错误解决](2026-08-15-postgres-csv-import-errors.md) — 数据清洗函数应用

---

## 参考来源

- CSDN：PostgreSQL 核心函数与操作总结（liumangtuzi888）
- [PostgreSQL 官方文档：函数目录](https://www.postgresql.org/docs/current/functions.html)
- [PostgreSQL 官方文档：窗口函数](https://www.postgresql.org/docs/current/tutorial-window.html)

---

## 量化速查

| 维度 | 量化值 | 说明 |
|:-----|:-------|:-----|
| 函数类别 | 6 类 | 数学/字符串/日期/聚合/窗口/转换 |
| 字符串长度 | LENGTH 按字符 | 字节数用 octet_length |
| 日期截断单位 | 6 种 | hour/day/week/month/quarter/year |
| 窗口排名函数 | 4 种 | ROW_NUMBER/RANK/DENSE_RANK/NTILE |

---

## Changelog

- 2026-08-15 v1.0: 首次深度加工（六类函数体系 + 窗口函数专题 + 空值/转换 + 6 易错点）
