# PostgreSQL 行转列方法## 量化速查## 量化速查

| 维度 | 量化值 | 说明 |
|:-----|:-------|:-----|
| 实现方法 | 3 种（100% 覆盖场景） | crosstab / CASE WHEN / jsonb |
| crosstab 启用 | 1 次（<1s） | CREATE EXTENSION tablefunc |
| 固定列 | CASE WHEN（0 依赖） | 标准 SQL |
| 动态列 | crosstab（100% 灵活） | 需拼 SQL |
| 性能开销 | jsonb 约 +10-20% 序列化 | 大表注意 |

---

## 📑 目录

- [一、结论概要](#一结论概要)
- [二、方法一：crosstab（推荐）](#二方法一crosstab推荐)
- [三、方法二：CASE WHEN + 聚合](#三方法二case-when--聚合)
- [四、方法三：jsonb 聚合](#四方法三jsonb-聚合)
- [五、方法对比与选型](#五方法对比与选型)
- [六、实战场景](#六实战场景)
- [七、易错点与最佳实践](#七易错点与最佳实践)
- [量化速查](#量化速查)
- [相关文档](#相关文档)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 一、结论概要

行转列（Pivot）把"一列的分类值"转为"多列"，是报表统计的常用技术。PostgreSQL 提供 **三种实现**：

| 方法 | 原理 | 适用 | 依赖 |
|:-----|:-----|:-----|:-----|
| `crosstab` | 专用透视函数 | 动态/多列，推荐 | tablefunc 扩展 |
| `CASE WHEN + 聚合` | 条件聚合展开 | 列数固定简单场景 | 无（标准 SQL） |
| `jsonb_agg` | JSON 聚合后展开 | 灵活但可读性差 | 无 |

**核心结论**：
1. **列数固定 → CASE WHEN**（直观、无依赖）；**列数动态/较多 → crosstab**（高效灵活）
2. **crosstab 需先装扩展**：`CREATE EXTENSION IF NOT EXISTS tablefunc;`（一次性）
3. **crosstab 语法三要素**：源数据 SQL + 列名生成 SQL + 输出列定义（缺一不可）
4. **数据需先排序**：crosstab 要求源 SQL 按行标识列排序，否则结果错乱

---

## 二、方法一：crosstab（推荐）

### 2.1 启用扩展

```sql
CREATE EXTENSION IF NOT EXISTS tablefunc;
```

### 2.2 基础语法

```sql
SELECT *
FROM crosstab(
  'source_sql',   -- returns (row_id, category, value)
  'categories_sql' -- returns distinct category values
) AS ct(
  row_id type,
  col1 type,
  col2 type,
  ...
);
```

### 2.3 完整示例：月度销售透视

```sql
-- source data: (month, product, amount)
-- want: month as rows, products as columns
SELECT *
FROM crosstab(
  'SELECT month, product, amount
   FROM sales
   ORDER BY 1, 2',
  'SELECT DISTINCT product FROM sales ORDER BY 1'
) AS ct(
  month text,
  product_a numeric,
  product_b numeric,
  product_c numeric
);
```

- **注意**：源 SQL `ORDER BY 1, 2` 必须按行标识列排序

### 2.4 动态列场景

- 列数不固定时，需动态拼 SQL（PL/pgSQL 或应用层生成列定义）
- 简单场景可用固定列定义，超出则报错

---

## 三、方法二：CASE WHEN + 聚合

### 3.1 原理

- 每个分类一个 `CASE WHEN ... THEN value END` 分支
- 外层 `SUM/MAX/MIN` 聚合（数值用 SUM，文本用 MAX）

### 3.2 示例：同一数据透视

```sql
SELECT month,
       SUM(CASE WHEN product = 'A' THEN amount END) AS product_a,
       SUM(CASE WHEN product = 'B' THEN amount END) AS product_b,
       SUM(CASE WHEN product = 'C' THEN amount END) AS product_c
FROM sales
GROUP BY month
ORDER BY month;
```

### 3.3 特点

- ✅ 标准 SQL，无扩展依赖，可读性好
- ❌ 列数必须提前写死，动态列需要动态拼接 SQL

---

## 四、方法三：jsonb 聚合

### 4.1 示例

```sql
SELECT month,
       jsonb_object_agg(product, amount) AS products
FROM sales
GROUP BY month;
```

- 结果：每行一个 JSON 对象 `{"A": 100, "B": 200}`
- 应用层解析或 `->>` 提取单值

### 4.2 展开单值

```sql
SELECT month,
       products->>'A' AS product_a,
       products->>'B' AS product_b
FROM (
  SELECT month, jsonb_object_agg(product, amount) AS products
  FROM sales GROUP BY month
) t;
```

### 4.3 特点

- ✅ 动态列天然支持、灵活
- ❌ 可读性较差，需要应用层二次处理

---

## 五、方法对比与选型

| 维度 | crosstab | CASE WHEN | jsonb |
|:-----|:---------|:----------|:------|
| 扩展依赖 | tablefunc | 无 | 无 |
| 固定列 | ✅ | ✅ | ✅ |
| 动态列 | ✅（拼 SQL） | ❌ | ✅ |
| 可读性 | 中 | 高 | 低 |
| 性能 | 高 | 中 | 中 |
| 适用 | 报表/多列透视 | 简单固定列 | 灵活/动态 |

**选型建议**：
- 报表固定维度 → CASE WHEN（最直观）
- 列多/动态 → crosstab（性能与灵活平衡）
- 前端展示灵活格式 → jsonb（交给应用解析）

---

## 六、实战场景

### 6.1 场景一：学生成绩透视

```sql
SELECT student_id,
       MAX(CASE WHEN subject = 'math' THEN score END) AS math,
       MAX(CASE WHEN subject = 'chinese' THEN score END) AS chinese,
       MAX(CASE WHEN subject = 'english' THEN score END) AS english
FROM scores
GROUP BY student_id;
```

### 6.2 场景二：按周统计订单量

```sql
SELECT *
FROM crosstab(
  'SELECT week, channel, count(*) FROM orders GROUP BY week, channel ORDER BY 1, 2',
  'SELECT DISTINCT channel FROM orders ORDER BY 1'
) AS ct(week date, app bigint, web bigint, api bigint);
```

### 6.3 场景三：动态报表（PL/pgSQL 拼 SQL）

```sql
DO $$
DECLARE
  cols text;
  sql  text;
BEGIN
  SELECT string_agg(DISTINCT format('%I numeric', product), ', ')
  INTO cols FROM sales;
  sql := format(
    'SELECT * FROM crosstab(''SELECT month, product, amount FROM sales ORDER BY 1,2'',
     ''SELECT DISTINCT product FROM sales ORDER BY 1'') AS ct(month text, %s)',
    cols);
  EXECUTE sql;
END $$;
```

---

## 七、易错点与最佳实践

### 易错点

| # | 场景 | 坑 | 对策 |
|:-:|:-----|:---|:-----|
| 1 | 忘 ORDER BY 行标识列 | crosstab 结果错乱 | 源 SQL 强制 ORDER BY 1,2 |
| 2 | 列定义数 < 实际分类 | 报错列数不匹配 | 列定义 ≥ DISTINCT 数 |
| 3 | 忘装 tablefunc | `function crosstab does not exist` | 先 CREATE EXTENSION |
| 4 | CASE WHEN 无聚合包裹 | 每组多行报错 | 外层必须聚合 |
| 5 | 文本列用 SUM | 类型错误 | 文本用 MAX/MIN |
| 6 | 动态列手写 | 维护困难 | 动态拼 SQL 或 jsonb |

### 最佳实践

1. **固定维度用 CASE WHEN**：简单可靠，易 review
2. **动态维度优先 jsonb**：避免复杂动态 SQL
3. **crosstab 列定义文档化**：明确每列含义，便于维护
4. **报表视图封装**：透视逻辑写成 VIEW，应用层直接查
5. **性能验证**：大表透视注意索引（row_id + category）

---

## 相关文档

- [核心函数与操作总结](2026-08-15-postgres-core-functions.md) — 聚合/窗口函数基础
- [表操作与数据操作全指南](2026-08-15-postgres-table-dml-guide.md) — 查询基础
- [Schema 管理](2026-08-15-postgres-schema-management.md) — 报表 schema 组织

---

## 参考来源

- 素材库：PostgreSQL 行转列方法
- [PostgreSQL 官方文档：tablefunc 扩展](https://www.postgresql.org/docs/current/tablefunc.html)
- [PostgreSQL 官方文档：JSON 函数](https://www.postgresql.org/docs/current/functions-json.html)

---

## 量化速查

| 维度 | 量化值 | 说明 |
|:-----|:-------|:-----|
| 实现方法 | 3 种 | crosstab / CASE WHEN / jsonb |
| crosstab 依赖 | tablefunc 扩展 | CREATE EXTENSION 一次 |
| 适用场景 | 列数固定→CASE WHEN | 动态列→crosstab/jsonb |
| 排序要求 | 源 SQL 必须 ORDER BY | 行标识列排序防错乱 |

---

## Changelog

- 2026-08-15 v1.0: 首次深度加工（三方法详解 + 对比选型 + 三实战场景 + 动态 SQL + 6 易错点）
