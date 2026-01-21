# SQL Interview Patterns Cheat Sheet

A quick reference guide for identifying which SQL concept to apply based on the problem requirements.

## 1. Joins
**When to use:**
- You need to retrieve data from **multiple tables**.
- You need to filter records based on the existence (or non-existence) of related records in another table.

| Join Type | Purpose | When to use |
| :--- | :--- | :--- |
| **INNER JOIN** | Returns records that have matching values in both tables. | "Find users who have placed an order." (Intersection) |
| **LEFT JOIN** | Returns all records from the left table, and the matched records from the right table. | "Find all users, and their orders if they have any." (Preserve Left) |
| **RIGHT JOIN** | Returns all records from the right table, and the matched records from the left table. | Rarely used; usually rewritten as a LEFT JOIN. |
| **FULL OUTER JOIN** | Returns all records when there is a match in either left or right table. | "List all employees and all projects, matching them where possible, but include unmatched ones from both sides." |
| **CROSS JOIN** | Returns the Cartesian product of the two tables. | "Generate every possible combination of products and colors." |

## 2. Window Functions
**When to use:**
- You need to perform calculations across a set of table rows that are somehow related to the current row.
- You need to keep the **original granularity** of the data (unlike `GROUP BY`, which collapses rows).
- Keywords: "Running total", "Rank", "Moving average", "Previous row value", "Top N per category".

**Common Functions:**
- `ROW_NUMBER()`: Unique number for each row (1, 2, 3, 4). Good for de-duplication or finding "top 1".
- `RANK()`: Rank with gaps for ties (1, 2, 2, 4).
- `DENSE_RANK()`: Rank without gaps for ties (1, 2, 2, 3). Good for "Nth highest salary".
- `LEAD() / LAG()`: Access data from the next or previous row. Good for "Year-over-Year growth" or "Time difference between events".
- `SUM() OVER (ORDER BY ...)`: Running total/Cumulative sum.

**Syntax:**
```sql
FUNCTION_NAME() OVER (PARTITION BY split_col ORDER BY sort_col)
```

## 3. Aggregation (GROUP BY & HAVING)
**When to use:**
- You need to calculate summary statistics (count, sum, avg) for **groups** of data.
- You need to collapse multiple rows into a single result row.
- Use `HAVING` to filter groups *after* aggregation (e.g., "Find customer groups with > 5 orders").
- Use `WHERE` to filter rows *before* aggregation.

**Common Scenarios:**
- "Count the number of users per country."
- "Find the average salary by department."
- "Which products have total sales greater than $1000?"

## 4. Common Table Expressions (CTEs) vs Subqueries
**When to use CTEs (`WITH` clause):**
- You have complex logic that needs to be broken down into steps for readability.
- You need to reference the same temporary result set multiple times in the main query.
- You need recursion (Recursive CTEs) to traverse hierarchical data (e.g., org charts, folder structures).

**When to use Subqueries:**
- Simple, one-off calculations (e.g., "Where salary > (Select AVG(salary)...)").
- `EXISTS` or `IN` clauses.

**Why CTEs?** Improved readability and maintainability over nested subqueries.

## 5. Set Operations
**When to use:**
- You need to combine the result sets of two or more SELECT statements vertically (stacking rows).
- The queries must have the same number of columns and compatible data types.

| Operator | Action | Duplicates |
| :--- | :--- | :--- |
| **UNION** | Combines results. | Removes duplicates. |
| **UNION ALL** | Combines results. | Keeps duplicates (Faster). |
| **INTERSECT** | Returns only rows found in *both* sets. | Removes duplicates. |
| **EXCEPT** (or MINUS) | Returns rows in the first set but *not* in the second. | Removes duplicates. |

## 6. NULL Handling
**When to use:**
- Data might be missing or explicitly NULL.
- Comparing NULLs (`= NULL` doesn't work; use `IS NULL` or `IS NOT NULL`).
- Replacing NULLs with default values.

**Functions:**
- `COALESCE(val1, val2, ...)`: Returns the first non-null value. Excellent for providing defaults.
- `IFNULL(val, default)` / `ISNULL(val, default)`: Dialect specific comparisons.
- `NULLIF(val1, val2)`: Returns NULL if val1 == val2. Useful to avoid "division by zero" errors (e.g., `amount / NULLIF(count, 0)`).

## 7. String Manipulation
**When to use:**
- Formatting output or extracting parts of text.
- Searching for patterns.

**Common Functions:**
- `CONCAT()`: Join strings.
- `SUBSTRING()` / `LEFT()` / `RIGHT()`: Extract parts of strings.
- `UPPER()` / `LOWER()`: Case conversion.
- `TRIM()`: Remove whitespace.
- `LIKE`: Pattern matching (`%` wildcard).
- `REGEX`: Advanced pattern matching (if supported).

## 8. Date & Time Patterns
**When to use:**
- Grouping by time periods (Year, Month, Day).
- Calculating intervals or differences.

**Common Scenarios:**
- `DATE_TRUNC('month', date_col)`: Group by month.
- `DATEDIFF` / `DATE_PART`: Calculate age or time since event.
- `NOW()` / `CURRENT_DATE`: Get current time.

## 9. Self Joins
**When to use:**
- You need to compare rows within the **same table**.
- Hierarchical data stored in a flat table (e.g., Employee table with ManagerID).
- "Find employees who earn more than their managers."
- "Find pairs of products purchased by the same user."

## 10. Case When
**When to use:**
- Conditional logic within a query (IF-THEN-ELSE).
- Pivoting data (turning rows into columns).
- Creating custom buckets or categories.

**Syntax:**
```sql
CASE 
    WHEN condition1 THEN result1
    WHEN condition2 THEN result2
    ELSE default_result
END
```
