# PySpark Cheat Sheet (SQL Equivalent)

A guide mapping common SQL interview patterns to PySpark DataFrame API.

## 1. Basic Query Structure
`SELECT` -> `FILTER` -> `GROUP BY` -> `AGG` -> `ORDER BY` -> `LIMIT`

```python
from pyspark.sql import functions as F

df.select("col1", F.count("col2")) \
  .join(df2, "id") \
  .filter(F.col("cond") > 10) \
  .groupBy("col1") \
  .agg(F.count("col2").alias("cnt")) \
  .where(F.col("cnt") > 5) \
  .orderBy(F.col("col1").asc()) \
  .limit(10)
```

---

## 2. Joins
Combine DataFrames.

| Join Type | PySpark Syntax |
| :--- | :--- |
| **INNER** | `df1.join(df2, "id", "inner")` |
| **LEFT** | `df1.join(df2, "id", "left")` |
| **FULL** | `df1.join(df2, "id", "full")` |
| **CROSS** | `df1.crossJoin(df2)` |
| **SELF** | `df1.alias("a").join(df1.alias("b"), F.col("a.mgr") == F.col("b.emp"))` |

---

## 3. Aggregate Functions

| SQL | PySpark |
| :--- | :--- |
| `COUNT(*)` | `F.count("*")` |
| `SUM(col)` | `F.sum("col")` |
| `AVG(col)` | `F.mean("col")` |
| `MIN/MAX` | `F.min("col"), F.max("col")` |
| `COUNT(DISTINCT col)` | `F.countDistinct("col")` |

```python
# Count users per city > 10
df.groupBy("city") \
  .agg(F.count("user_id").alias("cnt")) \
  .filter(F.col("cnt") > 10)
```

---

## 4. Window Functions
`from pyspark.sql.window import Window`

### Syntax
```python
windowSpec = Window.partitionBy("dept").orderBy(F.col("salary").desc())
df.withColumn("rnk", F.dense_rank().over(windowSpec))
```

### Examples
| Function | PySpark |
| :--- | :--- |
| `ROW_NUMBER()` | `F.row_number().over(w)` |
| `RANK()` | `F.rank().over(w)` |
| `LEAD(col, 1)` | `F.lead("col", 1).over(w)` |
| `LAG(col, 1)` | `F.lag("col", 1).over(w)` |

### Framing (Rolling Window)
```python
# 3-day Moving Average
w = Window.orderBy("date").rowsBetween(-2, Window.currentRow)
df.withColumn("moving_avg", F.avg("sales").over(w))
```

---

## 5. String Functions

| SQL | PySpark | Output (Input: 'abc') |
| :--- | :--- | :--- |
| `CONCAT(a, b)` | `F.concat(F.col("a"), F.col("b"))` | 'ab' |
| `SUBSTRING(s, 1, 2)` | `F.substring("s", 1, 2)` | 'ab' |
| `TRIM(s)` | `F.trim("s")` | 'abc' |
| `UPPER(s)` | `F.upper("s")` | 'ABC' |
| `REPLACE` | `F.regexp_replace("s", "pattern", "repl")` | - |

---

## 6. Date Functions

| SQL | PySpark | Example |
| :--- | :--- | :--- |
| `CURRENT_DATE` | `F.current_date()` | 2023-01-01 |
| `DATE_ADD` | `F.date_add("col", 7)` | +7 Days |
| `DATEDIFF` | `F.datediff("end", "start")` | Days diff |
| `YEAR/MONTH` | `F.year("col")`, `F.month("col")` | 2023, 1 |
| `TRUNC` | `F.date_trunc("month", "col")` | First of month |

```python
# Filter last 7 days
df.filter(F.col("date") >= F.date_add(F.current_date(), -7))
```

---

## 7. Regex & Matching

| SQL | PySpark | Example |
| :--- | :--- | :--- |
| `LIKE 'A%'` | `col.startswith("A")` | 'Apple' |
| `LIKE '%B'` | `col.endswith("B")` | 'Bob' |
| `LIKE '%M%'` | `col.contains("M")` | 'Mary' |
| `REGEXP` | `col.rlike("regex")` | `email.rlike("^\d+")` |

### Regex Extract
```python
# Extract domain: 'user@gmail.com' -> 'gmail.com'
df.withColumn("domain", F.regexp_extract("email", "@(.*)", 1))
```

---

## 8. Pivot / Unpivot

### Pivot (Rows to Columns)
```python
# Input: exam_id, result ('Pass'/'Fail')
pivot_df = df.groupBy("exam_id") \
             .pivot("result") \
             .count() \
             .na.fill(0)
# Output Cols: exam_id, Pass, Fail
```

### Unpivot (Columns to Rows)
Using `stack` inside `selectExpr` (SQL expression).
```python
# Input: student, math, science
unpivot_df = df.selectExpr("student", "stack(2, 'Math', math, 'Science', science) as (subject, score)")
# Output: student, subject, score
```

---

## 9. Set Operations

| SQL | PySpark | Note |
| :--- | :--- | :--- |
| `UNION ALL` | `df1.union(df2)` | **Keeps duplicates**. Fast. |
| `UNION` | `df1.union(df2).distinct()` | Removes duplicates. |
| `INTERSECT` | `df1.intersect(df2)` | Common rows. |
| `EXCEPT` | `df1.subtract(df2)` | In df1 not in df2. |
