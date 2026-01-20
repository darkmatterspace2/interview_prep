# Data Engineering Interview Questions

A comprehensive collection of data engineering interview questions covering PySpark, SQL, and data processing concepts.

---

## Table of Contents
- [Deloitte Interview Questions](#deloitte-interview-questions)
- [Coforge Interview Questions](#coforge-interview-questions)
- [Additional PySpark Questions](#additional-pyspark-questions)
- [Additional SQL Questions](#additional-sql-questions)
- [Data Processing Concepts](#data-processing-concepts)

---

## Deloitte Interview Questions

### 1. Splitting Large Files While Preserving Order

**Question:** I have 1 million records and want to split them into 10 files (100K each) without changing the order. How would you do this in PySpark?

**Answer:**

```python
from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, monotonically_increasing_id

spark = SparkSession.builder.appName("SplitRecords").getOrCreate()

# Read the CSV file
df = spark.read.csv("path/filename.csv", header=True)

# Add row numbers to preserve order
df_with_row = df.withColumn("row_id", monotonically_increasing_id())
window = Window.orderBy("row_id")
df2 = df_with_row.withColumn("rownum", row_number().over(window))

# Split and write each partition
for i in range(10):
    start = i * 100000 + 1
    end = (i + 1) * 100000
    df_part = df2.filter((df2.rownum >= start) & (df2.rownum <= end))
    df_part.drop("row_id", "rownum").write.format("orc").save(f"output/file_{i+1}")
```

**Key Points:**
- `monotonically_increasing_id()` generates unique IDs but not consecutive
- `row_number()` with a window provides sequential numbering
- Always drop helper columns before writing

---

### 2. Handling Corrupt/Bad Data in Files

**Question:** Examine the following file with corrupt data. How will you handle and import it into a Spark DataFrame?

```
Emp_no, Emp_name, Department
101, Murugan, HealthCare Invalid Entry, Description: Bad Record entry 
102, Kannan, Finance 
103, Mani, IT Connection lost, Description: Poor Connection 
104, Pavan, HR Bad Record, Description: Corrupt record
```

**Answer:**

```python
# Method 1: Using PERMISSIVE mode with corrupt record column
df = spark.read \
    .option("mode", "PERMISSIVE") \
    .option("columnNameOfCorruptRecord", "_corrupt_record") \
    .csv("path/to/file.csv", header=True)

# Separate clean and corrupt records
clean_df = df.filter(df._corrupt_record.isNull())
corrupt_df = df.filter(df._corrupt_record.isNotNull())

# Method 2: Using badRecordsPath (Spark 2.3+)
df = spark.read \
    .option("mode", "PERMISSIVE") \
    .option("badRecordsPath", "/path/to/bad_records") \
    .csv("path/to/file.csv", header=True)

# Method 3: Using DROPMALFORMED mode (drops bad records silently)
df = spark.read \
    .option("mode", "DROPMALFORMED") \
    .csv("path/to/file.csv", header=True)
```

**Read Modes:**
| Mode | Behavior |
|------|----------|
| `PERMISSIVE` | Sets malformed fields to null, can capture corrupt records |
| `DROPMALFORMED` | Drops rows with malformed records |
| `FAILFAST` | Throws exception on malformed records |

---

### 3. Merging Files with Different Schemas

**Question:** How will you merge File1 and File2 into a single DataFrame if they have different schemas?

```
File-1: Name|Age
Azarudeen, Shahul|25
Michel, Clarke|26

File-2: Name|Age|Gender
Rabindra, Tagore|32|Male
Madona, Laure|59|Female
```

**Answer:**

```python
# Read both files
df1 = spark.read.option("delimiter", "|").csv("file1.csv", header=True)
df2 = spark.read.option("delimiter", "|").csv("file2.csv", header=True)

# Method 1: unionByName with allowMissingColumns (Spark 3.1+)
merged_df = df1.unionByName(df2, allowMissingColumns=True)

# Method 2: Manual schema alignment (older Spark versions)
from pyspark.sql.functions import lit

# Add missing column to df1
df1_aligned = df1.withColumn("Gender", lit(None).cast("string"))

# Now union
merged_df = df1_aligned.unionByName(df2)

# Method 3: Using SQL
df1.createOrReplaceTempView("table1")
df2.createOrReplaceTempView("table2")

merged_df = spark.sql("""
    SELECT Name, Age, NULL as Gender FROM table1
    UNION ALL
    SELECT Name, Age, Gender FROM table2
""")
```

---

### 4. Finding Duplicate Emails

**Question:** Write a SQL query to find all duplicate emails in a table named Person.

```
+----+---------+
| Id | Email   |
+----+---------+
| 1  | a@b.com |
| 2  | c@d.com |
| 3  | a@b.com |
+----+---------+
```

**Answer:**

```sql
-- Method 1: Using GROUP BY and HAVING
SELECT Email
FROM Person
GROUP BY Email
HAVING COUNT(*) > 1;

-- Method 2: Using self-join
SELECT DISTINCT p1.Email
FROM Person p1
INNER JOIN Person p2 
    ON p1.Email = p2.Email 
    AND p1.Id <> p2.Id;

-- Method 3: Using subquery
SELECT DISTINCT Email
FROM Person
WHERE Email IN (
    SELECT Email
    FROM Person
    GROUP BY Email
    HAVING COUNT(*) > 1
);
```

---

## Coforge Interview Questions

### 1. Deleting Duplicate Records

**Question:** Delete duplicate records from a temp table, keeping only one occurrence.

**Answer:**

```sql
-- Method 1: Using ROW_NUMBER() with CTE
WITH RankedRecords AS (
    SELECT name, 
           ROW_NUMBER() OVER (PARTITION BY name ORDER BY name) AS rnk
    FROM temp_table
)
DELETE FROM RankedRecords WHERE rnk > 1;

-- Method 2: Using MIN/MAX to keep specific record
DELETE FROM temp_table
WHERE id NOT IN (
    SELECT MIN(id)
    FROM temp_table
    GROUP BY name
);

-- Method 3: In PySpark
df = spark.read.table("temp_table")
df_deduplicated = df.dropDuplicates(["name"])
```

---

### 2. Reading Tab-Separated Files

**Question:** How do you read a tab-separated file in PySpark?

**Answer:**

```python
# Method 1: Using sep parameter
df = spark.read.csv("filepath/filename.tsv", sep="\t", header=True)

# Method 2: Using option
df = spark.read \
    .option("delimiter", "\t") \
    .option("header", "true") \
    .csv("filepath/filename.tsv")

# Method 3: Using format
df = spark.read \
    .format("csv") \
    .option("sep", "\t") \
    .option("header", "true") \
    .load("filepath/filename.tsv")
```

---

## Additional PySpark Questions

### 5. Difference Between `cache()` and `persist()`

**Question:** What is the difference between `cache()` and `persist()` in Spark?

**Answer:**

| Feature | `cache()` | `persist()` |
|---------|-----------|-------------|
| Storage Level | MEMORY_ONLY (default) | Configurable |
| Flexibility | Fixed | Can use MEMORY_AND_DISK, DISK_ONLY, etc. |

```python
from pyspark import StorageLevel

# cache() - stores in memory only
df.cache()

# persist() - configurable storage
df.persist(StorageLevel.MEMORY_AND_DISK)
df.persist(StorageLevel.DISK_ONLY)
df.persist(StorageLevel.MEMORY_ONLY_SER)  # Serialized
```

---

### 6. Broadcast Variables

**Question:** What are broadcast variables and when would you use them?

**Answer:**

```python
from pyspark.sql.functions import broadcast

# Small lookup table
lookup_df = spark.read.csv("small_lookup.csv", header=True)  # < 10MB

# Large fact table
fact_df = spark.read.parquet("large_facts.parquet")

# Broadcast join - sends small table to all executors
result = fact_df.join(broadcast(lookup_df), "key_column")
```

**Use When:**
- Joining large DataFrame with small DataFrame (< 10MB default)
- Reducing shuffle operations
- Lookup tables that fit in memory

---

### 7. Handling Skewed Data

**Question:** How do you handle data skew in Spark joins?

**Answer:**

```python
# Method 1: Salting technique
from pyspark.sql.functions import lit, rand, concat, col

# Add salt to skewed key
salt_range = 10
df_salted = df.withColumn("salted_key", 
    concat(col("key"), lit("_"), (rand() * salt_range).cast("int")))

# Method 2: Broadcast smaller table
result = large_df.join(broadcast(small_df), "key")

# Method 3: Adaptive Query Execution (Spark 3.0+)
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
```

---

### 8. Difference Between `repartition()` and `coalesce()`

**Question:** Explain the difference between `repartition()` and `coalesce()`.

**Answer:**

| Feature | `repartition()` | `coalesce()` |
|---------|-----------------|--------------|
| Shuffle | Full shuffle | Minimizes shuffle |
| Increase partitions | ✅ Yes | ❌ No |
| Decrease partitions | ✅ Yes | ✅ Yes (preferred) |
| Use case | Even distribution | Reducing partitions |

```python
# Increase partitions (use repartition)
df = df.repartition(100)

# Decrease partitions (use coalesce - more efficient)
df = df.coalesce(10)

# Repartition by column (for partitioned writes)
df = df.repartition("date_column")
```

---

### 9. Window Functions in PySpark

**Question:** Calculate running total and rank by department.

**Answer:**

```python
from pyspark.sql.window import Window
from pyspark.sql.functions import sum, row_number, rank, dense_rank

# Define window specifications
window_dept = Window.partitionBy("department").orderBy("salary")
window_running = Window.partitionBy("department").orderBy("date").rowsBetween(Window.unboundedPreceding, Window.currentRow)

df = df.withColumn("row_num", row_number().over(window_dept)) \
       .withColumn("rank", rank().over(window_dept)) \
       .withColumn("dense_rank", dense_rank().over(window_dept)) \
       .withColumn("running_total", sum("amount").over(window_running))
```

---

## Additional SQL Questions

### 10. Second Highest Salary

**Question:** Find the second highest salary from an Employee table.

**Answer:**

```sql
-- Method 1: Using LIMIT and OFFSET
SELECT DISTINCT salary
FROM Employee
ORDER BY salary DESC
LIMIT 1 OFFSET 1;

-- Method 2: Using subquery
SELECT MAX(salary) AS SecondHighestSalary
FROM Employee
WHERE salary < (SELECT MAX(salary) FROM Employee);

-- Method 3: Using DENSE_RANK
SELECT salary
FROM (
    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
    FROM Employee
) ranked
WHERE rnk = 2;

-- Method 4: Handle NULL if no second highest
SELECT (
    SELECT DISTINCT salary
    FROM Employee
    ORDER BY salary DESC
    LIMIT 1 OFFSET 1
) AS SecondHighestSalary;
```

---

### 11. Nth Highest Salary

**Question:** Write a function to get the Nth highest salary.

**Answer:**

```sql
-- Using DENSE_RANK
CREATE FUNCTION getNthHighestSalary(N INT) RETURNS INT
BEGIN
    RETURN (
        SELECT DISTINCT salary
        FROM (
            SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
            FROM Employee
        ) ranked
        WHERE rnk = N
    );
END;

-- Using LIMIT OFFSET (N-1 because OFFSET is 0-indexed)
SELECT DISTINCT salary
FROM Employee
ORDER BY salary DESC
LIMIT 1 OFFSET N-1;
```

---

### 12. Consecutive Numbers

**Question:** Find all numbers that appear at least three times consecutively.

```
+----+-----+
| Id | Num |
+----+-----+
| 1  | 1   |
| 2  | 1   |
| 3  | 1   |
| 4  | 2   |
| 5  | 1   |
| 6  | 2   |
| 7  | 2   |
+----+-----+
```

**Answer:**

```sql
-- Method 1: Self-join
SELECT DISTINCT l1.Num AS ConsecutiveNums
FROM Logs l1
JOIN Logs l2 ON l1.Id = l2.Id - 1
JOIN Logs l3 ON l2.Id = l3.Id - 1
WHERE l1.Num = l2.Num AND l2.Num = l3.Num;

-- Method 2: Using LAG/LEAD
SELECT DISTINCT Num AS ConsecutiveNums
FROM (
    SELECT Num,
           LAG(Num, 1) OVER (ORDER BY Id) AS prev1,
           LAG(Num, 2) OVER (ORDER BY Id) AS prev2
    FROM Logs
) t
WHERE Num = prev1 AND Num = prev2;
```

---

### 13. Department Top 3 Salaries

**Question:** Find employees who earn top 3 salaries in each department.

**Answer:**

```sql
SELECT Department, Employee, Salary
FROM (
    SELECT 
        d.Name AS Department,
        e.Name AS Employee,
        e.Salary,
        DENSE_RANK() OVER (PARTITION BY e.DepartmentId ORDER BY e.Salary DESC) AS rnk
    FROM Employee e
    JOIN Department d ON e.DepartmentId = d.Id
) ranked
WHERE rnk <= 3;
```

---

## Data Processing Concepts

### 14. ETL vs ELT

**Question:** What is the difference between ETL and ELT?

**Answer:**

| Aspect | ETL | ELT |
|--------|-----|-----|
| **Process** | Extract → Transform → Load | Extract → Load → Transform |
| **Transform Location** | Staging area / ETL tool | Target data warehouse |
| **Best For** | On-premise, structured data | Cloud data warehouses |
| **Examples** | Informatica, Talend, SSIS | Snowflake, BigQuery, Databricks |
| **Scalability** | Limited by ETL server | Leverages cloud compute |

---

### 15. Slowly Changing Dimensions (SCD)

**Question:** Explain SCD Types 1, 2, and 3.

**Answer:**

| Type | Description | Example |
|------|-------------|---------|
| **SCD Type 1** | Overwrite old data | Update address directly |
| **SCD Type 2** | Add new row with versioning | Keep history with effective dates |
| **SCD Type 3** | Add new column for previous value | current_address, previous_address |

```sql
-- SCD Type 2 Implementation
INSERT INTO dim_customer (customer_id, name, address, effective_from, effective_to, is_current)
VALUES (101, 'John', 'New York', '2024-01-01', '9999-12-31', 1);

-- When address changes:
UPDATE dim_customer 
SET effective_to = CURRENT_DATE - 1, is_current = 0
WHERE customer_id = 101 AND is_current = 1;

INSERT INTO dim_customer (customer_id, name, address, effective_from, effective_to, is_current)
VALUES (101, 'John', 'Los Angeles', CURRENT_DATE, '9999-12-31', 1);
```

---

### 16. Data Quality Checks

**Question:** What data quality checks would you implement in a data pipeline?

**Answer:**

```python
from pyspark.sql.functions import col, count, when, isnan, isnull

# 1. Null check
null_counts = df.select([count(when(isnull(c), c)).alias(c) for c in df.columns])

# 2. Duplicate check
duplicate_count = df.count() - df.dropDuplicates().count()

# 3. Schema validation
expected_schema = ["id", "name", "amount", "date"]
assert df.columns == expected_schema, "Schema mismatch!"

# 4. Range validation
invalid_amounts = df.filter((col("amount") < 0) | (col("amount") > 1000000)).count()

# 5. Referential integrity
orphan_records = fact_df.join(dim_df, "key", "left_anti").count()

# 6. Freshness check
from datetime import datetime, timedelta
max_date = df.agg({"date": "max"}).collect()[0][0]
assert max_date >= datetime.now() - timedelta(days=1), "Data is stale!"
```

---

### 17. Partitioning Strategies

**Question:** How do you decide on partitioning strategy for a data lake?

**Answer:**

```python
# Time-based partitioning (most common)
df.write \
    .partitionBy("year", "month", "day") \
    .parquet("s3://bucket/table/")

# Category-based partitioning
df.write \
    .partitionBy("region", "category") \
    .parquet("s3://bucket/table/")

# Bucketing (for join optimization)
df.write \
    .bucketBy(100, "user_id") \
    .sortBy("user_id") \
    .saveAsTable("bucketed_table")
```

**Guidelines:**
- Partition by frequently filtered columns
- Avoid too many small files (< 128MB)
- Avoid too few large partitions
- Ideal partition size: 128MB - 1GB

---

### 18. Spark Optimization Techniques

**Question:** List common Spark optimization techniques.

**Answer:**

1. **Use appropriate file formats:** Parquet, ORC over CSV/JSON
2. **Broadcast small tables:** `broadcast(small_df)`
3. **Cache/persist intermediate results:** `df.cache()`
4. **Avoid UDFs when possible:** Use built-in functions
5. **Repartition for parallelism:** `df.repartition(n)`
6. **Use coalesce to reduce partitions:** `df.coalesce(n)`
7. **Enable AQE:** `spark.sql.adaptive.enabled = true`
8. **Optimize joins:** Broadcast joins, bucketing
9. **Filter early:** Push down predicates
10. **Use appropriate data types:** Avoid strings for numbers

---

## Quick Reference

### Common PySpark Imports

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
```

### SparkSession Creation

```python
spark = SparkSession.builder \
    .appName("MyApp") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.executor.memory", "4g") \
    .getOrCreate()
```

### Common Read/Write Operations

```python
# Read
df = spark.read.parquet("path/to/data")
df = spark.read.csv("path/to/data", header=True, inferSchema=True)
df = spark.read.json("path/to/data")

# Write
df.write.mode("overwrite").parquet("path/to/output")
df.write.mode("append").partitionBy("date").parquet("path/to/output")
```

---

*Last Updated: January 2026*
