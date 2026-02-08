# SQL Interview Cheat Sheet

A comprehensive guide to SQL functions, syntax, and concepts for technical interviews.

## 1. Basic Query Structure
Order of execution: `FROM` -> `JOIN` -> `WHERE` -> `GROUP BY` -> `HAVING` -> `SELECT` -> `DISTINCT` -> `ORDER BY` -> `LIMIT`.

```sql
SELECT DISTINCT column1, AGG(column2)
FROM table1
JOIN table2 ON table1.id = table2.id
WHERE condition
GROUP BY column1
HAVING AGG(column2) > value
ORDER BY column1 ASC/DESC
LIMIT n;
```

---

## 2. Joins
Combine rows from two or more tables based on a related column.

| Join Type | Syntax | Description | Example |
| :--- | :--- | :--- | :--- |
| **INNER** | `FROM A JOIN B ON A.id = B.id` | Matching rows in both tables. | "Users who ordered" |
| **LEFT** | `FROM A LEFT JOIN B ON A.id = B.id` | All rows from A, matches from B (NULL if no match). | "All users + orders (if any)" |
| **RIGHT** | `FROM A RIGHT JOIN B ON A.id = B.id` | All rows from B, matches from A. | Rarely used. |
| **FULL** | `FROM A FULL JOIN B ON A.id = B.id` | All rows from both A and B. | "All users and all orders" |
| **CROSS** | `FROM A CROSS JOIN B` | Cartesian product (MxN rows). | "Every combination of User and Product" |
| **SELF** | `FROM A a1 JOIN A a2 ON a1.mgr_id = a2.emp_id` | Join table to itself. | "Employees earning more than managers" |

---

## 3. Aggregate Functions
Perform a calculation on a set of values to return a single scalar value.

*   `COUNT(*)`: Count all rows.
*   `COUNT(col)`: Count non-NULL values in col.
*   `SUM(col)`: Sum of values.
*   `AVG(col)`: Average of values.
*   `MIN(col) / MAX(col)`: Minimum / Maximum value.

```sql
-- Count users per city having more than 10 users
SELECT city, COUNT(user_id)
FROM users
GROUP BY city
HAVING COUNT(user_id) > 10;
```

---

## 4. Window Functions
Perform calculations across a set of table rows related to the current row, *without* collapsing them (unlike GROUP BY).

**Syntax**: `FUNCTION() OVER (PARTITION BY col ORDER BY col)`

### Ranking
*   `ROW_NUMBER()`: 1, 2, 3, 4 (Unique rank, ties broken arbitrarily).
*   `RANK()`: 1, 2, 2, 4 (Skips ranks for ties).
*   `DENSE_RANK()`: 1, 2, 2, 3 (No skipped ranks).

```sql
-- Find top 3 highest paid employees per department
SELECT * FROM (
    SELECT name, dept, salary,
           DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary DESC) as rnk
    FROM employees
) WHERE rnk <= 3;
```

### Lead/Lag
*   `LAG(col, n)`: Value from `n` rows before.
*   `LEAD(col, n)`: Value from `n` rows after.

```sql
-- Calculate Mom (Month-over-Month) growth
SELECT month, revenue,
       LAG(revenue) OVER (ORDER BY month) as prev_month_revenue,
       (revenue - LAG(revenue) OVER (ORDER BY month)) / LAG(revenue) OVER (ORDER BY month) as growth_pct
FROM sales;
```

### Framing (Rolling Windows)
Defining the scope of rows for calculation (e.g., Running Totals, Moving Averages).

**Syntax**: `[ROWS | RANGE] BETWEEN [START] AND [END]`

**Frame Units**:
*   `ROWS`: Physical rows (e.g., "last 3 rows").
*   `RANGE`: Logical value difference (e.g., "last 3 days" or "values within 5 units").

**Frame Bounds**:
*   `UNBOUNDED PRECEDING`: Start of partition.
*   `N PRECEDING`: N rows/units before.
*   `CURRENT ROW`: Current row.
*   `N FOLLOWING`: N rows/units after.
*   `UNBOUNDED FOLLOWING`: End of partition.

```sql
-- 1. Cumulative Sum (Running Total)
-- From start to current row
SUM(sales) OVER (
    ORDER BY date
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
)

-- 2. 3-day Moving Average (Trailing)
-- 2 rows before + current row
AVG(sales) OVER (
    ORDER BY date
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
)

-- 3. Centered Moving Average (PRECEDING + FOLLOWING)
-- 1 row before + current row + 1 row after
AVG(sales) OVER (
    ORDER BY date
    ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
)

-- 4. Looking Ahead (Future values only)
-- Next 3 rows, excluding current
SUM(sales) OVER (
    ORDER BY date
    ROWS BETWEEN 1 FOLLOWING AND 3 FOLLOWING
)

-- 5. Rolling 7-day Sum (Time-based / RANGE)
-- Handles missing dates correctly by looking at the value of 'visited_on'
-- Requires 'visited_on' to be a DATE/TIMESTAMP type
SUM(amount) OVER (
    ORDER BY visited_on 
    RANGE BETWEEN INTERVAL '6' DAY PRECEDING AND CURRENT ROW
)

-- 6. Last 3 Days (Including today) vs Last 3 Rows
-- If you have multiple records per day or missing days:
-- ROWS: Strictly 3 physical records.
-- RANGE: All records falling within the 3-day window.
COUNT(*) OVER (
    ORDER BY date
    RANGE BETWEEN INTERVAL '2' DAY PRECEDING AND CURRENT ROW
)
```

---

## 5. Common Table Expressions (CTEs)
Temporary result set defined within the scope of a single statement. Improves readability over subqueries.

```sql
WITH HighSalary AS (
    SELECT * FROM employees WHERE salary > 100000
),
Engineering AS (
    SELECT * FROM departments WHERE name = 'Engineering'
)
SELECT h.name
FROM HighSalary h
JOIN Engineering e ON h.dept_id = e.id;
```

---

## 6. String Functions
*   `CONCAT(a, b)`: 'ab'. `CONCAT_WS('-', 'A', 'B')` -> 'A-B'.
*   `SUBSTRING(str, start, len)`: Extract part.
*   `TRIM(str)`: Remove whitespace.
*   `UPPER(str) / LOWER(str)`
*   `REPLACE(str, from, to)`: `REPLACE('1-800', '-', '')` -> '1800'
*   `COALESCE(val1, val2)`: Return first non-null.

### String Aggregation (List Aggregation)
Concatenating values from multiple rows into a single string.

*   **MySQL**: `GROUP_CONCAT(col ORDER BY col SEPARATOR ', ')`
*   **PostgreSQL**: `STRING_AGG(col, ', ' ORDER BY col)`
*   **SQL Server**: `STRING_AGG(col, ', ') WITHIN GROUP (ORDER BY col)`

```sql
-- List all products ordered by each user
SELECT user_id, 
       GROUP_CONCAT(product_name ORDER BY product_name SEPARATOR ', ') as products
FROM orders
GROUP BY user_id;
```

**Input Table (`orders`)**
| user_id | product_name |
| :--- | :--- |
| 1 | Apple |
| 1 | Banana |
| 2 | Cherry |
| 1 | Apple |

**Output**
| user_id | products |
| :--- | :--- |
| 1 | Apple, Apple, Banana |
| 2 | Cherry |
```

---

## 7. Date Functions

### Get Current Date/Time
| Dialect | Current Date | Current Timestamp |
|---------|--------------|-------------------|
| **MySQL** | `CURDATE()` or `CURRENT_DATE` | `NOW()` or `CURRENT_TIMESTAMP` |
| **PostgreSQL** | `CURRENT_DATE` | `NOW()` or `CURRENT_TIMESTAMP` |
| **SQL Server** | `CAST(GETDATE() AS DATE)` | `GETDATE()` |
| **Spark SQL** | `current_date()` | `current_timestamp()` |

---

### Extract Parts from Date

**Sample Date**: `'2026-02-08'` (Sunday)

| Part | MySQL | PostgreSQL | SQL Server | Spark SQL |
|------|-------|------------|------------|-----------|
| **Year** | `YEAR(date)` | `EXTRACT(YEAR FROM date)` | `DATEPART(YEAR, date)` | `year(date)` |
| **Month** | `MONTH(date)` | `EXTRACT(MONTH FROM date)` | `DATEPART(MONTH, date)` | `month(date)` |
| **Day** | `DAY(date)` | `EXTRACT(DAY FROM date)` | `DATEPART(DAY, date)` | `day(date)` |
| **Week** | `WEEK(date)` | `EXTRACT(WEEK FROM date)` | `DATEPART(WEEK, date)` | `weekofyear(date)` |
| **Day of Week** | `DAYOFWEEK(date)` (1=Sun) | `EXTRACT(DOW FROM date)` (0=Sun) | `DATEPART(WEEKDAY, date)` | `dayofweek(date)` |
| **Day of Year** | `DAYOFYEAR(date)` | `EXTRACT(DOY FROM date)` | `DATEPART(DAYOFYEAR, date)` | `dayofyear(date)` |
| **Quarter** | `QUARTER(date)` | `EXTRACT(QUARTER FROM date)` | `DATEPART(QUARTER, date)` | `quarter(date)` |
| **Hour** | `HOUR(ts)` | `EXTRACT(HOUR FROM ts)` | `DATEPART(HOUR, ts)` | `hour(ts)` |
| **Minute** | `MINUTE(ts)` | `EXTRACT(MINUTE FROM ts)` | `DATEPART(MINUTE, ts)` | `minute(ts)` |

```sql
-- MySQL
SELECT 
    YEAR('2026-02-08') as yr,        -- 2026
    MONTH('2026-02-08') as mth,      -- 2
    DAY('2026-02-08') as dy,         -- 8
    WEEK('2026-02-08') as wk,        -- 6
    DAYOFWEEK('2026-02-08') as dow;  -- 1 (Sunday)

-- PostgreSQL
SELECT 
    EXTRACT(YEAR FROM DATE '2026-02-08') as yr,    -- 2026
    EXTRACT(MONTH FROM DATE '2026-02-08') as mth,  -- 2
    EXTRACT(DOW FROM DATE '2026-02-08') as dow;    -- 0 (Sunday)
```

---

### Get Day Name / Month Name

| Part | MySQL | PostgreSQL | SQL Server | Spark SQL |
|------|-------|------------|------------|-----------|
| **Day Name** | `DAYNAME(date)` | `TO_CHAR(date, 'Day')` | `DATENAME(WEEKDAY, date)` | `date_format(date, 'EEEE')` |
| **Month Name** | `MONTHNAME(date)` | `TO_CHAR(date, 'Month')` | `DATENAME(MONTH, date)` | `date_format(date, 'MMMM')` |
| **Short Day** | `DATE_FORMAT(date, '%a')` | `TO_CHAR(date, 'Dy')` | `LEFT(DATENAME(WEEKDAY, date), 3)` | `date_format(date, 'E')` |
| **Short Month** | `DATE_FORMAT(date, '%b')` | `TO_CHAR(date, 'Mon')` | `LEFT(DATENAME(MONTH, date), 3)` | `date_format(date, 'MMM')` |

```sql
-- MySQL
SELECT 
    DAYNAME('2026-02-08') as day_name,      -- 'Sunday'
    MONTHNAME('2026-02-08') as month_name;  -- 'February'

-- PostgreSQL
SELECT 
    TO_CHAR(DATE '2026-02-08', 'Day') as day_name,   -- 'Sunday   '
    TO_CHAR(DATE '2026-02-08', 'Month') as month_name; -- 'February '

-- SQL Server
SELECT 
    DATENAME(WEEKDAY, '2026-02-08') as day_name,  -- 'Sunday'
    DATENAME(MONTH, '2026-02-08') as month_name;  -- 'February'
```

---

### Date Format Conversion

| Format | MySQL | PostgreSQL | SQL Server | Spark SQL |
|--------|-------|------------|------------|-----------|
| **Date to String** | `DATE_FORMAT(date, format)` | `TO_CHAR(date, format)` | `FORMAT(date, format)` | `date_format(date, format)` |
| **String to Date** | `STR_TO_DATE(str, format)` | `TO_DATE(str, format)` | `CONVERT(DATE, str, style)` | `to_date(str, format)` |

**Common Format Codes:**
| Part | MySQL | PostgreSQL | SQL Server | Spark |
|------|-------|------------|------------|-------|
| Year (4-digit) | `%Y` | `YYYY` | `yyyy` | `yyyy` |
| Month (2-digit) | `%m` | `MM` | `MM` | `MM` |
| Day (2-digit) | `%d` | `DD` | `dd` | `dd` |
| Hour (24H) | `%H` | `HH24` | `HH` | `HH` |
| Minute | `%i` | `MI` | `mm` | `mm` |
| Second | `%s` | `SS` | `ss` | `ss` |

```sql
-- MySQL: Convert to 'DD-Mon-YYYY' format
SELECT DATE_FORMAT('2026-02-08', '%d-%b-%Y');  -- '08-Feb-2026'

-- PostgreSQL: Convert to 'DD/MM/YYYY' format
SELECT TO_CHAR(DATE '2026-02-08', 'DD/MM/YYYY');  -- '08/02/2026'

-- SQL Server: Convert to 'YYYY-MM-DD' format
SELECT FORMAT(GETDATE(), 'yyyy-MM-dd');

-- Spark SQL: Convert to 'MMM dd, yyyy'
SELECT date_format(current_date(), 'MMM dd, yyyy');  -- 'Feb 08, 2026'
```

**String to Date Examples:**
```sql
-- MySQL
SELECT STR_TO_DATE('08-02-2026', '%d-%m-%Y');  -- 2026-02-08

-- PostgreSQL
SELECT TO_DATE('08-02-2026', 'DD-MM-YYYY');  -- 2026-02-08

-- Spark SQL
SELECT to_date('08-02-2026', 'dd-MM-yyyy');  -- 2026-02-08
```

---

### Date Arithmetic (Add/Subtract)

| Operation | MySQL | PostgreSQL | SQL Server | Spark SQL |
|-----------|-------|------------|------------|-----------|
| **Add Days** | `DATE_ADD(date, INTERVAL n DAY)` | `date + INTERVAL 'n days'` | `DATEADD(DAY, n, date)` | `date_add(date, n)` |
| **Add Months** | `DATE_ADD(date, INTERVAL n MONTH)` | `date + INTERVAL 'n months'` | `DATEADD(MONTH, n, date)` | `add_months(date, n)` |
| **Add Years** | `DATE_ADD(date, INTERVAL n YEAR)` | `date + INTERVAL 'n years'` | `DATEADD(YEAR, n, date)` | `add_months(date, n*12)` |
| **Subtract Days** | `DATE_SUB(date, INTERVAL n DAY)` | `date - INTERVAL 'n days'` | `DATEADD(DAY, -n, date)` | `date_sub(date, n)` |

```sql
-- MySQL
SELECT 
    DATE_ADD('2026-02-08', INTERVAL 7 DAY) as plus_week,     -- 2026-02-15
    DATE_SUB('2026-02-08', INTERVAL 1 MONTH) as minus_month; -- 2026-01-08

-- PostgreSQL
SELECT 
    DATE '2026-02-08' + INTERVAL '7 days' as plus_week,
    DATE '2026-02-08' - INTERVAL '1 month' as minus_month;

-- Spark SQL
SELECT 
    date_add('2026-02-08', 7) as plus_week,
    add_months('2026-02-08', -1) as minus_month;
```

---

### Date Difference

| Dialect | Syntax | Example |
|---------|--------|---------|
| **MySQL** | `DATEDIFF(end, start)` (days only) | `DATEDIFF('2026-02-08', '2026-02-01')` → 7 |
| **PostgreSQL** | `end - start` or `AGE(end, start)` | `DATE '2026-02-08' - DATE '2026-02-01'` → 7 |
| **SQL Server** | `DATEDIFF(unit, start, end)` | `DATEDIFF(DAY, '2026-02-01', '2026-02-08')` → 7 |
| **Spark SQL** | `datediff(end, start)` | `datediff('2026-02-08', '2026-02-01')` → 7 |

```sql
-- Days between two dates
SELECT DATEDIFF('2026-02-08', '2026-02-01');  -- MySQL: 7

-- Months between (SQL Server)
SELECT DATEDIFF(MONTH, '2026-01-15', '2026-03-20');  -- 2

-- Years between (PostgreSQL using AGE)
SELECT EXTRACT(YEAR FROM AGE('2026-02-08', '2020-02-08'));  -- 6
```

---

### Truncate Date (Get Start of Period)

| Period | MySQL | PostgreSQL | SQL Server | Spark SQL |
|--------|-------|------------|------------|-----------|
| **Start of Month** | `DATE_FORMAT(date, '%Y-%m-01')` | `DATE_TRUNC('month', date)` | `DATEADD(MONTH, DATEDIFF(MONTH, 0, date), 0)` | `trunc(date, 'MM')` |
| **Start of Year** | `DATE_FORMAT(date, '%Y-01-01')` | `DATE_TRUNC('year', date)` | `DATEADD(YEAR, DATEDIFF(YEAR, 0, date), 0)` | `trunc(date, 'yyyy')` |
| **Start of Week** | `DATE_SUB(date, INTERVAL WEEKDAY(date) DAY)` | `DATE_TRUNC('week', date)` | `DATEADD(WEEK, DATEDIFF(WEEK, 0, date), 0)` | `trunc(date, 'week')` |

```sql
-- PostgreSQL: Get first day of month
SELECT DATE_TRUNC('month', DATE '2026-02-08');  -- 2026-02-01

-- Spark SQL: Get first day of year
SELECT trunc('2026-02-08', 'yyyy');  -- 2026-01-01
```

---

### Last Day of Month

| Dialect | Syntax |
|---------|--------|
| **MySQL** | `LAST_DAY(date)` |
| **PostgreSQL** | `(DATE_TRUNC('month', date) + INTERVAL '1 month - 1 day')::date` |
| **SQL Server** | `EOMONTH(date)` |
| **Spark SQL** | `last_day(date)` |

```sql
SELECT LAST_DAY('2026-02-08');  -- 2026-02-28 (MySQL/Spark)
SELECT EOMONTH('2026-02-08');   -- 2026-02-28 (SQL Server)
```

---

### Common Interview Queries

```sql
-- 1. Find users who signed up in the last 7 days
SELECT * FROM users
WHERE created_at >= DATE_SUB(CURRENT_DATE, INTERVAL 7 DAY);  -- MySQL

-- 2. Get signups by month
SELECT 
    DATE_FORMAT(created_at, '%Y-%m') as month,
    COUNT(*) as signups
FROM users
GROUP BY DATE_FORMAT(created_at, '%Y-%m');

-- 3. Find orders on weekends
SELECT * FROM orders
WHERE DAYOFWEEK(order_date) IN (1, 7);  -- MySQL (1=Sun, 7=Sat)

-- 4. Calculate age in years
SELECT TIMESTAMPDIFF(YEAR, birth_date, CURDATE()) as age FROM users;  -- MySQL

-- 5. Get records from same day last year
SELECT * FROM sales
WHERE sale_date = DATE_SUB(CURRENT_DATE, INTERVAL 1 YEAR);
```

Reference: https://dev.mysql.com/doc/refman/8.4/en/date-and-time-functions.html
---

## 8. Regex (Regular Expressions)
Support varies significantly by SQL dialect.

### Common Patterns
*   `^`: Start of string. `^A` -> Starts with A.
*   `$`: End of string. `com$` -> Ends with com.
*   `.`: Any single character.
*   `*`: Zero or more. `a*` -> '', 'a', 'aa'.
*   `+`: One or more. `a+` -> 'a', 'aa'.
*   `?`: Zero or one.
*   `[abc]`: Any character in set.
*   `[^abc]`: Any character NOT in set.
*   `\d`: Digit (0-9).
*   `\s`: Whitespace.

### Examples (PostgreSQL / Spark)
```sql
-- Emails from specific domain (insensitive) using Anchors
WHERE email ~* '@gmail\.com$'

-- Phone numbers starting with 555
WHERE phone ~ '^555-\d{4}'

-- Strings containing at least one digit
WHERE password ~ '\d+'

-- Extract Domain from Email (Spark)
regexp_extract(email, '@(.*)', 1)
```

### PostgreSQL
*   `~`: Case-sensitive match.
*   `~*`: Case-insensitive match.
*   `!~`: No match.

```sql
SELECT * FROM users WHERE email ~* '\.(net|org)$';
```

### Spark SQL / Databricks
*   `regexp_extract(str, regex, idx)`
*   `regexp_replace(str, regex, replacement)`

```sql
-- Mask digits: '123-456' -> 'XXX-XXX'
SELECT regexp_replace('123-456', '\d', 'X'); 
```

---

## 9. Set Operations
Combine results from two queries.
*   `UNION`: Combined distinctive rows (Removes duplicates). Use `UNION ALL` to keep duplicates (Faster).
*   `INTERSECT`: Rows present in *both* sets.
*   `EXCEPT` (or `MINUS`): Rows in first set *not* in second.

---

## 10. Performance Tuning (Indexing)
*   **Index**: Data structure (B-Tree) to speed up `SELECT` based on specific columns. Slows down `INSERT/UPDATE`.
*   **Clustered Index**: Sorts the physical data rows (Only 1 per table, usually PK).
*   **Non-Clustered Index**: Separate structure pointing to data rows.
*   **Composite Index**: Index on multiple columns `(col1, col2)`. Order matters! query on `col2` alone wont use index `(col1, col2)`.

```sql
CREATE INDEX idx_users_email ON users(email);
```

---

## 11. Pivot / Unpivot (CASE WHEN)
Turning rows into columns manually.

```sql
-- Calculate count of 'Pass' and 'Fail' students per exam
SELECT exam_id,
       SUM(CASE WHEN result = 'Pass' THEN 1 ELSE 0 END) as pass_count,
       SUM(CASE WHEN result = 'Fail' THEN 1 ELSE 0 END) as fail_count
FROM results
GROUP BY exam_id;
```

**Input Table (`results`)**
| exam_id | result |
| :--- | :--- |
| 101 | Pass |
| 101 | Pass |
| 101 | Fail |
| 102 | Pass |

**Output**
| exam_id | pass_count | fail_count |
| :--- | :--- | :--- |
| 101 | 2 | 1 |
| 102 | 1 | 0 |

### Unpivot (Columns to Rows)
Turning wide data into long data using `UNION ALL`.

```sql
SELECT student, 'Math' as subject, math as score FROM scores
UNION ALL
SELECT student, 'Science' as subject, science as score FROM scores;
```

**Input Table (`scores`)**
| student | math | science |
| :--- | :--- | :--- |
| Alice | 90 | 85 |

**Output**
| student | subject | score |
| :--- | :--- | :--- |
| Alice | Math | 90 |
| Alice | Science | 85 |


