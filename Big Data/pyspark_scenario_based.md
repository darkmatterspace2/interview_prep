# PySpark Scenario-Based Interview Questions

> **Beginner → Medium → Hard** with detailed explanations, input/output examples

---

<a id="top"></a>
## 📑 Table of Contents

| Level | Topics |
|-------|--------|
| [🟢 Beginner](#-beginner-level) | Basic transformations, filtering, aggregations |
| [🟡 Medium](#-medium-level) | Joins, window functions, deduplication |
| [🔴 Hard](#-hard-level) | Sessionization, SCD Type 2, complex aggregations |

---

# 🟢 Beginner Level [↩️](#top)

---

## Q1: Filter and Select Columns

**Scenario:** You have employee data. Filter employees with salary > 50000 and select only `name` and `salary`.

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder.appName("demo").getOrCreate()

# Input Data
data = [
    (1, "Alice", 60000, "IT"),
    (2, "Bob", 45000, "HR"),
    (3, "Charlie", 75000, "IT"),
    (4, "Dave", 50000, "Finance")
]
df = spark.createDataFrame(data, ["id", "name", "salary", "dept"])

# Solution
result = df.filter(col("salary") > 50000).select("name", "salary")
result.show()
```

**Output:**
```
+-------+------+
|   name|salary|
+-------+------+
|  Alice| 60000|
|Charlie| 75000|
+-------+------+
```

---

## Q2: Count Records by Group

**Scenario:** Count the number of employees in each department.

```python
# Input: Same employee DataFrame

# Solution
result = df.groupBy("dept").count()
result.show()
```

**Output:**
```
+-------+-----+
|   dept|count|
+-------+-----+
|     IT|    2|
|     HR|    1|
|Finance|    1|
+-------+-----+
```

---

## Q3: Add a New Calculated Column

**Scenario:** Add a `bonus` column which is 10% of salary.

```python
from pyspark.sql.functions import col

# Solution
result = df.withColumn("bonus", col("salary") * 0.10)
result.show()
```

**Output:**
```
+---+-------+------+-------+------+
| id|   name|salary|   dept| bonus|
+---+-------+------+-------+------+
|  1|  Alice| 60000|     IT|6000.0|
|  2|    Bob| 45000|     HR|4500.0|
|  3|Charlie| 75000|     IT|7500.0|
|  4|   Dave| 50000|Finance|5000.0|
+---+-------+------+-------+------+
```

---

## Q4: Replace NULL Values

**Scenario:** Replace NULL values in `salary` with 0 and NULL in `dept` with "Unknown".

```python
from pyspark.sql.functions import col, when, coalesce, lit

data = [
    (1, "Alice", 60000, "IT"),
    (2, "Bob", None, "HR"),
    (3, "Charlie", 75000, None),
]
df = spark.createDataFrame(data, ["id", "name", "salary", "dept"])

# Solution 1: Using fillna
result = df.fillna({"salary": 0, "dept": "Unknown"})

# Solution 2: Using coalesce
result = df.withColumn("salary", coalesce(col("salary"), lit(0))) \
           .withColumn("dept", coalesce(col("dept"), lit("Unknown")))

result.show()
```

**Output:**
```
+---+-------+------+-------+
| id|   name|salary|   dept|
+---+-------+------+-------+
|  1|  Alice| 60000|     IT|
|  2|    Bob|     0|     HR|
|  3|Charlie| 75000|Unknown|
+---+-------+------+-------+
```

---

## Q5: Remove Duplicates

**Scenario:** Remove duplicate rows based on `name` and `dept`.

```python
data = [
    (1, "Alice", "IT"),
    (2, "Alice", "IT"),
    (3, "Bob", "HR"),
    (4, "Bob", "Finance")
]
df = spark.createDataFrame(data, ["id", "name", "dept"])

# Solution: Drop duplicates on specific columns
result = df.dropDuplicates(["name", "dept"])
result.show()
```

**Output:**
```
+---+-----+-------+
| id| name|   dept|
+---+-----+-------+
|  1|Alice|     IT|
|  3|  Bob|     HR|
|  4|  Bob|Finance|
+---+-----+-------+
```

---

## Q6: Sort Data

**Scenario:** Sort employees by salary descending, then by name ascending.

```python
from pyspark.sql.functions import col, desc, asc

result = df.orderBy(desc("salary"), asc("name"))
result.show()
```

---

# 🟡 Medium Level [↩️](#top)

---

## Q7: Join Two DataFrames

**Scenario:** Join `employees` with `departments` to get department names.

```python
employees = spark.createDataFrame([
    (1, "Alice", 101),
    (2, "Bob", 102),
    (3, "Charlie", 101)
], ["emp_id", "name", "dept_id"])

departments = spark.createDataFrame([
    (101, "Engineering"),
    (102, "Marketing"),
    (103, "Finance")
], ["dept_id", "dept_name"])

# Inner Join
result = employees.join(departments, "dept_id", "inner")
result.show()
```

**Output:**
```
+-------+------+-------+-----------+
|dept_id|emp_id|   name|  dept_name|
+-------+------+-------+-----------+
|    101|     1|  Alice|Engineering|
|    101|     3|Charlie|Engineering|
|    102|     2|    Bob|  Marketing|
+-------+------+-------+-----------+
```

**Left Join (show all employees even without matching dept):**
```python
result = employees.join(departments, "dept_id", "left")
```

---

## Q8: Find Top N per Group (Window Function)

**Scenario:** Find top 2 highest-paid employees per department.

```python
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, desc

data = [
    ("IT", "Alice", 90000),
    ("IT", "Bob", 85000),
    ("IT", "Charlie", 95000),
    ("HR", "Dave", 70000),
    ("HR", "Eve", 75000),
]
df = spark.createDataFrame(data, ["dept", "name", "salary"])

# Define window
window_spec = Window.partitionBy("dept").orderBy(desc("salary"))

# Add row number
df_ranked = df.withColumn("rank", row_number().over(window_spec))

# Filter top 2
result = df_ranked.filter(col("rank") <= 2)
result.show()
```

**Output:**
```
+----+-------+------+----+
|dept|   name|salary|rank|
+----+-------+------+----+
|  HR|    Eve| 75000|   1|
|  HR|   Dave| 70000|   2|
|  IT|Charlie| 95000|   1|
|  IT|  Alice| 90000|   2|
+----+-------+------+----+
```

---

## Q9: Calculate Running Total

**Scenario:** Calculate cumulative sum of sales by date.

```python
from pyspark.sql.window import Window
from pyspark.sql.functions import sum as _sum

data = [
    ("2026-02-01", 100),
    ("2026-02-02", 200),
    ("2026-02-03", 150),
    ("2026-02-04", 300),
]
df = spark.createDataFrame(data, ["date", "sales"])

# Window from start to current row
window_spec = Window.orderBy("date").rowsBetween(Window.unboundedPreceding, Window.currentRow)

result = df.withColumn("running_total", _sum("sales").over(window_spec))
result.show()
```

**Output:**
```
+----------+-----+-------------+
|      date|sales|running_total|
+----------+-----+-------------+
|2026-02-01|  100|          100|
|2026-02-02|  200|          300|
|2026-02-03|  150|          450|
|2026-02-04|  300|          750|
+----------+-----+-------------+
```

---

## Q10: LAG and LEAD (Previous/Next Row)

**Scenario:** Calculate month-over-month sales growth.

```python
from pyspark.sql.window import Window
from pyspark.sql.functions import lag, col

data = [
    ("2026-01", 1000),
    ("2026-02", 1200),
    ("2026-03", 900),
    ("2026-04", 1500),
]
df = spark.createDataFrame(data, ["month", "revenue"])

window_spec = Window.orderBy("month")

result = df.withColumn("prev_revenue", lag("revenue", 1).over(window_spec)) \
           .withColumn("growth", (col("revenue") - col("prev_revenue")) / col("prev_revenue") * 100)
result.show()
```

**Output:**
```
+-------+-------+------------+------------------+
|  month|revenue|prev_revenue|            growth|
+-------+-------+------------+------------------+
|2026-01|   1000|        null|              null|
|2026-02|   1200|        1000|              20.0|
|2026-03|    900|        1200|             -25.0|
|2026-04|   1500|         900| 66.66666666666667|
+-------+-------+------------+------------------+
```

---

## Q11: Deduplication - Keep Latest Record

**Scenario:** Keep only the latest record per user based on `updated_at`.

```python
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, desc

data = [
    ("user1", "pending", "2026-02-01 10:00:00"),
    ("user1", "completed", "2026-02-01 11:00:00"),
    ("user2", "active", "2026-02-01 09:00:00"),
]
df = spark.createDataFrame(data, ["user_id", "status", "updated_at"])

window_spec = Window.partitionBy("user_id").orderBy(desc("updated_at"))

result = df.withColumn("rn", row_number().over(window_spec)) \
           .filter(col("rn") == 1) \
           .drop("rn")
result.show()
```

**Output:**
```
+-------+---------+-------------------+
|user_id|   status|         updated_at|
+-------+---------+-------------------+
|  user1|completed|2026-02-01 11:00:00|
|  user2|   active|2026-02-01 09:00:00|
+-------+---------+-------------------+
```

---

## Q12: Pivot Table

**Scenario:** Create a pivot table showing sales by product and quarter.

```python
data = [
    ("ProductA", "Q1", 100),
    ("ProductA", "Q2", 150),
    ("ProductB", "Q1", 200),
    ("ProductB", "Q2", 250),
]
df = spark.createDataFrame(data, ["product", "quarter", "sales"])

result = df.groupBy("product").pivot("quarter").sum("sales")
result.show()
```

**Output:**
```
+--------+---+---+
| product| Q1| Q2|
+--------+---+---+
|ProductA|100|150|
|ProductB|200|250|
+--------+---+---+
```

---

## Q13: Explode Array Column

**Scenario:** Flatten an array column into multiple rows.

```python
from pyspark.sql.functions import explode

data = [
    (1, ["apple", "banana", "cherry"]),
    (2, ["date", "elderberry"]),
]
df = spark.createDataFrame(data, ["id", "fruits"])

result = df.select("id", explode("fruits").alias("fruit"))
result.show()
```

**Output:**
```
+---+----------+
| id|     fruit|
+---+----------+
|  1|     apple|
|  1|    banana|
|  1|    cherry|
|  2|      date|
|  2|elderberry|
+---+----------+
```

---

## Q14: String Manipulation in PySpark

**Scenario:** Extract domain from email addresses.

```python
from pyspark.sql.functions import split, col

data = [
    (1, "alice@gmail.com"),
    (2, "bob@company.org"),
    (3, "charlie@test.co.uk"),
]
df = spark.createDataFrame(data, ["id", "email"])

# Solution: Split by @ and take second part
result = df.withColumn("domain", split(col("email"), "@")[1])
result.show()
```

**Output:**
```
+---+------------------+----------+
| id|             email|    domain|
+---+------------------+----------+
|  1|   alice@gmail.com| gmail.com|
|  2|   bob@company.org|company.org|
|  3|charlie@test.co.uk|test.co.uk|
+---+------------------+----------+
```

---

# 🔴 Hard Level [↩️](#top)

---

## Q15: Sessionization (User Sessions from Clickstream)

**Scenario:** Group user clicks into sessions with a 30-minute inactivity gap.

```python
from pyspark.sql.window import Window
from pyspark.sql.functions import lag, col, when, sum as _sum, unix_timestamp

data = [
    ("user1", "2026-02-08 10:00:00"),
    ("user1", "2026-02-08 10:05:00"),
    ("user1", "2026-02-08 10:50:00"),  # 45 min gap → new session
    ("user1", "2026-02-08 11:00:00"),
    ("user2", "2026-02-08 09:00:00"),
]
df = spark.createDataFrame(data, ["user_id", "event_time"])
df = df.withColumn("event_ts", unix_timestamp(col("event_time")))

# Step 1: Calculate gap from previous event
window_spec = Window.partitionBy("user_id").orderBy("event_ts")
df = df.withColumn("prev_ts", lag("event_ts", 1).over(window_spec))
df = df.withColumn("gap_seconds", col("event_ts") - col("prev_ts"))

# Step 2: Mark new session if gap > 30 minutes (1800 seconds)
df = df.withColumn("new_session", when(
    (col("gap_seconds") > 1800) | (col("gap_seconds").isNull()), 1
).otherwise(0))

# Step 3: Cumulative sum to get session_id
session_window = Window.partitionBy("user_id").orderBy("event_ts")
df = df.withColumn("session_id", _sum("new_session").over(session_window))

df.select("user_id", "event_time", "session_id").show()
```

**Output:**
```
+-------+-------------------+----------+
|user_id|         event_time|session_id|
+-------+-------------------+----------+
|  user1|2026-02-08 10:00:00|         1|
|  user1|2026-02-08 10:05:00|         1|
|  user1|2026-02-08 10:50:00|         2|
|  user1|2026-02-08 11:00:00|         2|
|  user2|2026-02-08 09:00:00|         1|
+-------+-------------------+----------+
```

---

## Q16: SCD Type 2 (Slowly Changing Dimension)

**Scenario:** Implement SCD Type 2 - track historical changes with effective dates.

```python
from pyspark.sql.functions import lit, current_date, when, col

# Existing dimension table
existing = spark.createDataFrame([
    (1, "Alice", "NYC", "2025-01-01", "9999-12-31", True),
    (2, "Bob", "LA", "2025-01-01", "9999-12-31", True),
], ["id", "name", "city", "start_date", "end_date", "is_current"])

# Incoming update (Alice moved to SF)
incoming = spark.createDataFrame([
    (1, "Alice", "SF"),
    (3, "Charlie", "Chicago"),  # New record
], ["id", "name", "city"])

# Step 1: Find changed records
changes = existing.alias("e").join(incoming.alias("i"), "id", "inner") \
    .filter(col("e.city") != col("i.city")) \
    .select("id")

# Step 2: Close old records (set end_date and is_current=False)
closed = existing.join(changes, "id", "left_semi") \
    .withColumn("end_date", current_date()) \
    .withColumn("is_current", lit(False))

# Step 3: Insert new versions
new_versions = incoming.join(changes, "id", "left_semi") \
    .withColumn("start_date", current_date()) \
    .withColumn("end_date", lit("9999-12-31")) \
    .withColumn("is_current", lit(True))

# Step 4: Unchanged records
unchanged = existing.join(changes, "id", "left_anti")

# Step 5: New records (not in existing)
new_records = incoming.join(existing, "id", "left_anti") \
    .withColumn("start_date", current_date()) \
    .withColumn("end_date", lit("9999-12-31")) \
    .withColumn("is_current", lit(True))

# Final result
result = unchanged.union(closed).union(new_versions).union(new_records)
result.orderBy("id", "start_date").show()
```

**Output:**
```
+---+-------+-------+----------+----------+----------+
| id|   name|   city|start_date|  end_date|is_current|
+---+-------+-------+----------+----------+----------+
|  1|  Alice|    NYC|2025-01-01|2026-02-08|     false|
|  1|  Alice|     SF|2026-02-08|9999-12-31|      true|
|  2|    Bob|     LA|2025-01-01|9999-12-31|      true|
|  3|Charlie|Chicago|2026-02-08|9999-12-31|      true|
+---+-------+-------+----------+----------+----------+
```

---

## Q17: Find Consecutive Events

**Scenario:** Find users who logged in for 3 or more consecutive days.

```python
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, datediff, to_date, col, count

data = [
    ("user1", "2026-02-01"),
    ("user1", "2026-02-02"),
    ("user1", "2026-02-03"),
    ("user1", "2026-02-05"),  # Gap
    ("user2", "2026-02-01"),
    ("user2", "2026-02-03"),  # Gap
]
df = spark.createDataFrame(data, ["user_id", "login_date"])
df = df.withColumn("login_date", to_date("login_date"))

# Step 1: Assign row number per user
window_spec = Window.partitionBy("user_id").orderBy("login_date")
df = df.withColumn("rn", row_number().over(window_spec))

# Step 2: Calculate group (date - row_number = constant for consecutive dates)
df = df.withColumn("grp", datediff(col("login_date"), lit("2026-01-01")) - col("rn"))

# Step 3: Count consecutive days per group
result = df.groupBy("user_id", "grp").agg(count("*").alias("consecutive_days")) \
           .filter(col("consecutive_days") >= 3) \
           .select("user_id", "consecutive_days")
result.show()
```

**Output:**
```
+-------+----------------+
|user_id|consecutive_days|
+-------+----------------+
|  user1|               3|
+-------+----------------+
```

---

## Q18: Handle Late Arriving Data

**Scenario:** Aggregate sales by hour but handle late data with a 1-hour watermark.

```python
from pyspark.sql.functions import window, col

# Simulated streaming data
data = [
    ("2026-02-08 10:05:00", 100),
    ("2026-02-08 10:30:00", 200),
    ("2026-02-08 09:55:00", 50),  # Late data (should go to 09:00-10:00 window)
    ("2026-02-08 11:15:00", 300),
]
df = spark.createDataFrame(data, ["event_time", "amount"])
df = df.withColumn("event_time", col("event_time").cast("timestamp"))

# Aggregate by 1-hour tumbling window
result = df.groupBy(window(col("event_time"), "1 hour")).sum("amount")
result.select("window.start", "window.end", "sum(amount)").show(truncate=False)
```

**Output:**
```
+-------------------+-------------------+-----------+
|start              |end                |sum(amount)|
+-------------------+-------------------+-----------+
|2026-02-08 09:00:00|2026-02-08 10:00:00|50         |
|2026-02-08 10:00:00|2026-02-08 11:00:00|300        |
|2026-02-08 11:00:00|2026-02-08 12:00:00|300        |
+-------------------+-------------------+-----------+
```

---

## Q19: Data Skew Handling (Salting)

**Scenario:** Handle skewed join where one key has millions of records.

```python
from pyspark.sql.functions import lit, concat, col, explode, array, rand

# Skewed data (product_id 1 has many records)
sales = spark.createDataFrame([
    (1, 100), (1, 200), (1, 300),  # Skewed
    (2, 400),
], ["product_id", "amount"])

products = spark.createDataFrame([
    (1, "ProductA"),
    (2, "ProductB"),
], ["product_id", "name"])

# Solution: Salting
SALT_BUCKETS = 3

# Step 1: Add salt to large table
salted_sales = sales.withColumn("salt", (rand() * SALT_BUCKETS).cast("int")) \
                    .withColumn("salted_key", concat(col("product_id"), lit("_"), col("salt")))

# Step 2: Explode small table to match all salt values
salted_products = products.withColumn("salt", explode(array([lit(i) for i in range(SALT_BUCKETS)]))) \
                          .withColumn("salted_key", concat(col("product_id"), lit("_"), col("salt")))

# Step 3: Join on salted key
result = salted_sales.join(salted_products, "salted_key", "inner") \
                     .select(sales["product_id"], "name", "amount")
result.show()
```

---

## Q20: Flatten Nested JSON

**Scenario:** Flatten deeply nested JSON structure.

```python
from pyspark.sql.functions import col

data = [
    (1, {"name": "Alice", "address": {"city": "NYC", "zip": "10001"}}),
]
df = spark.createDataFrame(data, ["id", "info"])

# Flatten nested fields
result = df.select(
    col("id"),
    col("info.name").alias("name"),
    col("info.address.city").alias("city"),
    col("info.address.zip").alias("zip")
)
result.show()
```

**Output:**
```
+---+-----+----+-----+
| id| name|city|  zip|
+---+-----+----+-----+
|  1|Alice| NYC|10001|
+---+-----+----+-----+
```

---

## Quick Reference: PySpark Functions [↩️](#top)

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMMON PYSPARK PATTERNS                      │
├─────────────────────────────────────────────────────────────────┤
│ FILTERING                                                       │
│   df.filter(col("x") > 10)                                      │
│   df.where("x > 10")                                            │
├─────────────────────────────────────────────────────────────────┤
│ AGGREGATIONS                                                    │
│   df.groupBy("col").agg(sum("val"), count("*"))                 │
├─────────────────────────────────────────────────────────────────┤
│ WINDOW FUNCTIONS                                                │
│   Window.partitionBy("x").orderBy("y")                          │
│   row_number(), rank(), dense_rank()                            │
│   lag(), lead()                                                 │
│   sum().over(window_spec)                                       │
├─────────────────────────────────────────────────────────────────┤
│ JOINS                                                           │
│   df1.join(df2, "key", "inner|left|right|outer")                │
├─────────────────────────────────────────────────────────────────┤
│ NULL HANDLING                                                   │
│   df.fillna(0)                                                  │
│   coalesce(col1, col2)                                          │
│   when(col.isNull(), "default")                                 │
└─────────────────────────────────────────────────────────────────┘
```
