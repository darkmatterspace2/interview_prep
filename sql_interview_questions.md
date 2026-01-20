# Advanced SQL Interview Questions for Data Engineers
*Mid to Senior Level*

A curated collection of advanced SQL scenarios focusing on query optimization, complex window functions, recursive queries, and data modeling challenges often encountered in Data Engineering interviews.

---

## Table of Contents
1. [Window Functions & Analytics](#window-functions--analytics)
2. [Recursive Queries & CTEs](#recursive-queries--ctes)
3. [Advanced Aggregations (Gaps & Islands)](#advanced-aggregations-gaps--islands)
4. [Performance Tuning & Indexing](#performance-tuning--indexing)
5. [Data Modeling & Schema Design](#data-modeling--schema-design)
6. [Practical Scenarios](#practical-scenarios)

---

## Window Functions & Analytics

### 1. ROWS vs RANGE in Window Functions
**Q:** What is the difference between `ROWS BETWEEN` and `RANGE BETWEEN`?
**A:**
- `ROWS`: Operates on physical rows. `ROWS BETWEEN 1 PRECEDING AND CURRENT ROW` looks at exactly the row before the current one, regardless of value.
- `RANGE`: Operates on logical values. `RANGE BETWEEN 5 PRECEDING AND CURRENT ROW` looks at rows where the ordering value is within 5 units of the current row's value.

**Example Scenario:** Calculating a rolling 7-day average sales.
```sql
SELECT 
    sale_date, 
    daily_sales,
    AVG(daily_sales) OVER (
        ORDER BY sale_date 
        RANGE BETWEEN INTERVAL '6' DAY PRECEDING AND CURRENT ROW
    ) as rolling_7_day_avg
FROM SALES;
```
*Note: Using `RANGE` handles missing dates correctly (it looks partially back in time), whereas `ROWS 6 PRECEDING` would just take the previous 6 records even if there are gaps in dates.*

### 2. Retention Analysis (Cohort Analysis)
**Q:** Calculate Month-over-Month retention rate.
**Context:** Given a `user_logins` table (user_id, login_date).
**Solution:**
```sql
WITH first_login AS (
    SELECT user_id, DATE_TRUNC('month', MIN(login_date)) as cohort_month
    FROM user_logins
    GROUP BY user_id
),
retention AS (
    SELECT 
        f.cohort_month,
        DATE_TRUNC('month', l.login_date) as activity_month,
        COUNT(DISTINCT l.user_id) as active_users
    FROM user_logins l
    JOIN first_login f ON l.user_id = f.user_id
    GROUP BY 1, 2
)
SELECT 
    cohort_month,
    activity_month,
    active_users,
    FIRST_VALUE(active_users) OVER (PARTITION BY cohort_month ORDER BY activity_month) as cohort_size,
    active_users::float / FIRST_VALUE(active_users) OVER (PARTITION BY cohort_month ORDER BY activity_month) as retention_rate
FROM retention;
```

---

## Recursive Queries & CTEs

### 3. Employee Hierarchy Traversal
**Q:** Given an `Employees` table (id, name, manager_id), write a query to list all employees under a specific manager (e.g., Manager ID 1) at all levels (direct and indirect reports).
**A:** requires a Recursive Common Table Expression (CTE).
```sql
WITH RECURSIVE Hierarchy AS (
    -- Anchor member: Direct reports
    SELECT id, name, manager_id, 1 as level
    FROM Employees
    WHERE manager_id = 1
    
    UNION ALL
    
    -- Recursive member: Reports of the reports
    SELECT e.id, e.name, e.manager_id, h.level + 1
    FROM Employees e
    INNER JOIN Hierarchy h ON e.manager_id = h.id
)
SELECT * FROM Hierarchy;
```

---

## Advanced Aggregations (Gaps & Islands)

### 4. The "Gaps and Islands" Problem
**Q:** Find the start and end ranges of consecutive numbers in a table.
**Data:** `Ids: 1, 2, 3, 5, 6, 8, 9, 10`
**Expected Output:**
- 1-3
- 5-6
- 8-10

**Solution:**
The trick is that `Id` minus `Row_Number` is constant for consecutive sequences.
```sql
WITH CTE AS (
    SELECT 
        Id,
        Id - ROW_NUMBER() OVER (ORDER BY Id) as Grp
    FROM Numbers
)
SELECT 
    MIN(Id) as Start_Range,
    MAX(Id) as End_Range
FROM CTE
GROUP BY Grp;
```

---

## Performance Tuning & Indexing

### 5. Clustered vs Non-Clustered Index
**Q:** Explain the difference relative to storage and retrieval.
**A:**
- **Clustered Index:** Defines the physical order of data on disk. A table can have only **one** clustered index (usually PK). Leaf nodes contain the actual data pages.
- **Non-Clustered Index:** Stored separately from the data rows. Contains key values and pointers (Row ID or Clustered Key) to the actual data. A table can have multiple.
- **DE Context:** In columnar databases (Redshift, Snowflake), we talk about "Sort Keys" or "Clustering Keys" which mimic this concept to prune file scanning (Zone Maps/Data Skipping).

### 6. Query Optimization Techniques
**Q:** A query is performing poorly on a 10TB table. Steps to debug?
**A:**
1.  **Analyze Execution Plan:** Look for Full Table Scans vs Index Scans/Seeks.
2.  **Partition Pruning:** Ensure `WHERE` clause filters on partition columns.
3.  **Skew Analysis:** Check if one join key has disproportionately more rows (causing data skew in distributed systems).
4.  **Join Order:** Filter largest tables *before* joining.
5.  **Statistics:** Run `ANALYZE` or `UPDATE STATISTICS` to ensure the optimizer has fresh cardinality estimates.

### 7. Broadcast Join vs Shuffle Hash Join
**Q:** When does the optimizer choose a Broadcast join?
**A:** When one side of the join is small enough to fit in memory (e.g., <10MB default in Spark). It replicates the small table to all nodes, avoiding a massive shuffle of the large table.

---

## Data Modeling & Schema Design

### 8. Slowly Changing Dimensions (SCD Type 2)
**Q:** How do you efficiently update an SCD Type 2 table using SQL (MERGE)?
**A:**
Typically involves a `MERGE` statement or a `FULL OUTER JOIN` approach.
1.  Identify records that are new (Insert).
2.  Identify records that changed (Update `end_date` of old, Insert new).
3.  Identify unchanged records (Do nothing).

**Pseudocode MERGE:**
```sql
MERGE INTO target_dim t
USING source_stage s ON t.id = s.id
WHEN MATCHED AND t.current_flag = 'Y' AND t.hash != s.hash THEN
    UPDATE SET current_flag = 'N', end_date = current_date
    -- Note: This usually requires a second pass/insert for the new active record depending on DB support
WHEN NOT MATCHED THEN
    INSERT (id, col1, start_date, current_flag) VALUES (s.id, s.col1, current_date, 'Y');
```

### 9. Fact vs Dimension Tables
**Q:** Explain a Star Schema vs Snowflake Schema. why prefer Star in Data Warehousing?
**A:**
- **Star:** Fact table in center, denormalized dimension tables around it. 1 level of join.
- **Snowflake:** Dimension tables are normalized (split into sub-dimensions). Multiple hops/joins.
- **Preference:** Star Schema is preferred for Analytics (OLAP) because:
    - Simpler queries (fewer joins).
    - Disk space is cheap; slight redundancy in dimensions is worth the read performance gain.

---

## Practical Scenarios

### 10. Pivot and Unpivot
**Q:** You have data: `Product | Jan_Sales | Feb_Sales`. Convert to `Product | Month | Sales`.
**A:** Use `UNPIVOT` or `CROSS JOIN LATERAL` (Postgres) or `UNION ALL`.
```sql
SELECT Product, 'Jan' as Month, Jan_Sales as Sales FROM T
UNION ALL
SELECT Product, 'Feb' as Month, Feb_Sales as Sales FROM T;
```

**Q:** Reverse it? (Rows to Columns)
**A:** Use `CASE WHEN` with Aggregation (Pivot).
```sql
SELECT 
    Product,
    SUM(CASE WHEN Month = 'Jan' THEN Sales ELSE 0 END) as Jan_Sales,
    SUM(CASE WHEN Month = 'Feb' THEN Sales ELSE 0 END) as Feb_Sales
FROM T
GROUP BY Product;
```

### 11. Finding Duplicates without `DISTINCT` or `GROUP BY`
**Q:** How to find duplicates without standard aggregation? (Tricky question)
**A:** Self-Join.
```sql
SELECT DISTINCT a.email 
FROM users a
JOIN users b ON a.email = b.email AND a.id < b.id;
```
