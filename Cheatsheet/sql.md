# SQL Cheat Sheet: Advanced Concepts & Functions

Based on common interview topics and practical usage.

## 1. Date Functions
Manipulation and extraction of date/time values. (Syntax often varies by dialect, T-SQL/Standard examples shown).

### DATEDIFF
Calculates the difference between two dates.

**Syntax (T-SQL):**
```sql
DATEDIFF(interval, start_date, end_date)
```
- **Interval**: year, quarter, month, day, hour, minute, second.
- **Result**: Integer difference.

**Example:**
```sql
-- Days between two dates
SELECT DATEDIFF(day, '2023-01-01', '2023-01-10'); -- Result: 9
-- Months between
SELECT DATEDIFF(month, '2023-01-01', '2023-03-01'); -- Result: 2
```

### DATEADD
Adds a specific interval to a date.

**Syntax (T-SQL):**
```sql
DATEADD(interval, number, date)
```

**Example:**
```sql
-- Add 7 days
SELECT DATEADD(day, 7, '2023-01-01'); -- Result: 2023-01-08
-- Subtract 1 month
SELECT DATEADD(month, -1, '2023-02-01'); -- Result: 2023-01-01
```

### DATEPART
Extracts a specific part of a date.

**Syntax (T-SQL):**
```sql
DATEPART(interval, date)
```

**Example:**
```sql
-- Get the year
SELECT DATEPART(year, '2023-10-25'); -- Result: 2023
-- Get the quarter
SELECT DATEPART(quarter, '2023-10-25'); -- Result: 4
```

---

## 2. Window Functions - Framing
Defining the scope of rows for calculation within a partition.

**General Syntax:**
```sql
FUNCTION() OVER (
    PARTITION BY ...
    ORDER BY ...
    [ROWS | RANGE] BETWEEN [START] AND [END]
)
```

### Frame Units
- **ROWS**: Physical rows (e.g., "3 rows back").
- **RANGE**: Logical value range (e.g., "values within 5 units of current").

### Frame Bounds
- `UNBOUNDED PRECEDING`: From the start of the partition.
- `UNBOUNDED FOLLOWING`: To the end of the partition.
- `CURRENT ROW`: The current row.
- `N PRECEDING`: N rows before.
- `N FOLLOWING`: N rows after.

### Common Examples

**Running Total (Cumulative Sum):**
```sql
SUM(amount) OVER (
    PARTITION BY customer_id 
    ORDER BY date 
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
)
```

**Moving Average (3-day rolling):**
Current row + previous 2 rows.
```sql
AVG(sales) OVER (
    ORDER BY date 
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
)
```

**Full Partition Scope:**
Using the entire partition for comparison (e.g., % of total).
```sql
amount / SUM(amount) OVER (
    PARTITION BY category 
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
)
```

---

## 3. String Functions
### CONCAT
Joins two or more strings together. Handles NULLs better than `+` or `||` in some dialects (often treating NULL as empty string).

**Syntax:**
```sql
CONCAT(string1, string2, ...)
-- Or with separator (SQL Server 2017+, Postgres)
CONCAT_WS(separator, string1, string2, ...)
```

**Example:**
```sql
SELECT CONCAT('Hello', ' ', 'World'); -- Result: 'Hello World'
SELECT CONCAT_WS('-', '2023', '01', '01'); -- Result: '2023-01-01'
```

### REPLACE
Replaces all occurrences of a specified substring.

**Syntax:**
```sql
REPLACE(string, old_substring, new_substring)
```

**Example:**
```sql
SELECT REPLACE('1-800-123-4567', '-', ''); -- Result: '18001234567'
SELECT REPLACE('Apples and Bananas', 'Bananas', 'Oranges'); -- Result: 'Apples and Oranges'
```

---

## 4. Regex (Regular Expressions)
Support varies significantly by SQL dialect.

### SQL Server (T-SQL)
Limited native support. Uses `LIKE` with wildcards or `PATINDEX`.
- `%`: Any string.
- `_`: Any single character.
- `[]`: Any character within range/set.
- `[^]`: Any character NOT within range.

**Example:**
```sql
-- Find strings starting with A-C
SELECT * FROM table WHERE col LIKE '[A-C]%';
```

### PostgreSQL
Rich support.
- `~`: Case-sensitive regex match.
- `~*`: Case-insensitive regex match.
- `!~`: No match.

**Example:**
```sql
-- Find emails ending in .net or .org
SELECT * FROM users WHERE email ~* '\.(net|org)$';
```

### Spark SQL / Databricks
- `regexp_extract(str, regex, idx)`
- `regexp_replace(str, regex, replacement)`

**Example:**
```sql
-- Mask digits in a string
SELECT regexp_replace('Phone: 123-456', '\d', 'X'); 
-- Result: 'Phone: XXX-XXX'
```
