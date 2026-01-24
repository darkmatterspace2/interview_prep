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
*   `CONCAT(a, b)`: 'ab'
*   `SUBSTRING(str, start, len)` or `SUBSTR`: Extract part.
*   `TRIM(str)`: Remove whitespace.
*   `UPPER(str) / LOWER(str)`
*   `REPLACE(str, from, to)`
*   `COALESCE(val1, val2)`: Return first non-null (often used for defaults).

---

## 7. Date Functions
*   `CURRENT_DATE` / `NOW()` / `GETDATE()`
*   `EXTRACT(part FROM date)` or `DATEPART`: Get Year/Month/Day.
*   `DATEDIFF(interval, start, end)`: Difference between dates.
*   `DATE_ADD(date, interval)`: Add days/months.

```sql
-- Find users who signed up in the last 7 days
SELECT * FROM users
WHERE created_at >= DATE_ADD(CURRENT_DATE, INTERVAL -7 DAY);
```

---

## 8. Set Operations
Combine results from two queries.
*   `UNION`: Combined distinctive rows (Removes duplicates). Use `UNION ALL` to keep duplicates (Faster).
*   `INTERSECT`: Rows present in *both* sets.
*   `EXCEPT` (or `MINUS`): Rows in first set *not* in second.

---

## 9. Performance Tuning (Indexing)
*   **Index**: Data structure (B-Tree) to speed up `SELECT` based on specific columns. Slows down `INSERT/UPDATE`.
*   **Clustered Index**: Sorts the physical data rows (Only 1 per table, usually PK).
*   **Non-Clustered Index**: Separate structure pointing to data rows.
*   **Composite Index**: Index on multiple columns `(col1, col2)`. Order matters! query on `col2` alone wont use index `(col1, col2)`.

```sql
CREATE INDEX idx_users_email ON users(email);
```

---

## 10. Pivot / Unpivot (CASE WHEN)
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


