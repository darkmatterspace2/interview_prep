# Real-World Data Engineering Interview Scenarios
*Compiled from Interview Notes*

A collection of mixed SQL, PySpark, Python, and Conceptual questions derived from real interview experiences (Jio, Netflix, etc.).

---

## Table of Contents
1. [Advanced SQL Scenarios](#advanced-sql-scenarios)
2. [PySpark Coding Challenges](#pyspark-coding-challenges)
3. [Python Algorithms](#python-algorithms)
4. [Conceptual & Linux](#conceptual--linux)

---

## Advanced SQL Scenarios

### 1. Nth Highest Record
**Q:** Find the movie with the 9th highest collection.
**A:**
```sql
SELECT name, collection 
FROM (
    SELECT name, collection, 
           DENSE_RANK() OVER (ORDER BY collection DESC) as rnk
    FROM movie
) WHERE rnk = 9;
```

### 2. Year-Over-Year Growth Flag
**Q:** Determine if a customer's billing increased or decreased compared to the previous year.
**A:**
```sql
SELECT cust, year, total_billing,
    CASE 
        WHEN total_billing > LAG(total_billing) OVER (PARTITION BY cust ORDER BY year) 
        THEN 'Increase'
        ELSE 'Decrease'
    END as billing_flag
FROM billing_table;
```

### 3. Manager-Employee Hierarchy
**Q:** List employees and their manager's name. If no manager, show 'No Manager'.
**A:**
```sql
SELECT 
    e1.emp_name as Employee, 
    COALESCE(e2.emp_name, 'No Manager') as Manager
FROM employee_tbl e1
LEFT JOIN employee_tbl e2 ON e1.manager_id = e2.emp_id;
```

### 4. Pivot Scenarios
**Q:** Pivot Vendor/Qty table to columns (Amazon, Flipkart, etc.).
**A:**
```sql
SELECT 
    SUM(CASE WHEN Vendor = 'Amazon' THEN Qty ELSE 0 END) as Amazon,
    SUM(CASE WHEN Vendor = 'Flipkart' THEN Qty ELSE 0 END) as Flipkart,
    SUM(CASE WHEN Vendor = 'Myntra' THEN Qty ELSE 0 END) as Myntra
FROM orders;
```

### 5. Join Cardinality Puzzle
**Q:** Given Table A (1, 1, 2, NULL) and Table B (1, 3, 4, NULL), calculate counts.
*   **Inner Join:** Matches `1, 1` (Count: 2) -> (Only 1s match)
*   **Left Join:** `1, 1, 2, NULL` (Count: 4) -> (All rows from A)
*   **Right Join:** `1, 1, 3, 4, NULL` (Count: 5) -> (Matching 1s + B's unique)
*   **Full Outer:** All unique rows + matches.
*   **Cross Join:** 4 rows * 4 rows = 16 rows.

---

## PySpark Coding Challenges

### 6. Career Path Analysis
**Q:** Find employees who started at 'Microsoft' immediately followed by 'Google'.
**A:**
```python
from pyspark.sql.window import Window
from pyspark.sql.functions import lag, col, lead

w = Window.partitionBy("emp_id").orderBy("startyear")

df_lead = df.withColumn("next_employer", lead("employer").over(w))

result = df_lead.filter(
    (col("employer") == "Microsoft") & 
    (col("next_employer") == "Google")
).select("emp_id")
```

### 7. Conditional Status Flag
**Q:** Create a new column 'Status'. If Sum(A+B+C) <= 10 -> 'Unbreached', else 'Breached'.
**A:**
```python
from pyspark.sql.functions import col, when, lit

df = df.withColumn("Status", 
    when((col("A") + col("B") + col("C")) <= 10, lit("Unbreached"))
    .otherwise(lit("Breached"))
)
```

### 8. Character Count (Explode)
**Q:** Count the frequency of every character in a text file.
**A:**
```python
from pyspark.sql.functions import split, explode

# Read text file
df = spark.read.text("path/to/file")

# Split lines into characters and explode
df_chars = df.select(explode(split(col("value"), "")).alias("char"))

# Filter out empty strings if needed and count
df_chars.filter(col("char") != "").groupby("char").count().show()
```

---

## Python Algorithms

### 9. Max Product Pair
**Q:** Find the pair of numbers in `arr = {1, 7, -23, -58, 7, 0}` that has the maximum product.
**Note:** Two huge negative numbers can make a large positive product!
**A:**
```python
arr = [1, 7, -23, -58, 7, 0]

def max_product(arr):
    n = len(arr)
    if n < 2: return 0
    
    max_val = float('-inf')
    
    # O(N^2) Approach
    for i in range(n):
        for j in range(i + 1, n):
            prod = arr[i] * arr[j]
            if prod > max_val:
                max_val = prod
                
    return max_val
    
    # O(N log N) Approach: Sort and compare first 2 vs last 2
    # arr.sort()
    # return max(arr[0] * arr[1], arr[-1] * arr[-2])

print(max_product(arr)) # Output: 1334 (-23 * -58)
```

### 10. Manual Word Count
**Q:** Count words in string without `len()` or `split()` (conceptual logic).
**A:**
```python
text = "Hi Himanshu Welcome"
count = 0
is_word = False

for char in text:
    if char != ' ':
        if not is_word:
            count += 1
            is_word = True
    else:
        is_word = False
        
print(count)
```

---

## Conceptual & Linux

### 11. Linux Commands for DE
*   **Find large old files:**
    `find /path -size -1M -mtime +180 -print`
    *(Find files smaller than 1MB and older than 180 days)*
*   **Replace string in file:**
    `sed -i 's/himanshu/othername/g' filename.txt`
*   **Check File Difference:**
    `diff file1.txt file2.txt`

### 12. Spark Internals
*   **Broadcast Join:** Copies small table (<10MB) to all nodes to avoid shuffle.
*   **Shuffle vs Sort Merge:** 
    *   *Shuffle Hash:* Good for large tables where one fits in memory.
    *   *Sort Merge:* Standard for 2 huge tables (Sorts both, then merges).
*   **Catalyst Optimizer:**
    1.  **Analysis:** Checks schema/types.
    2.  **Logical Plan:** Optimizes logical steps (filter pushdown).
    3.  **Physical Plan:** Selects join strategies (Broadcast vs SortMerge).
    4.  **Code Generation:** Generates Java bytecode (WholeStageCodegen).

### 13. Cluster Sizing Calculation
**Scenario:** Total Cores: 150, RAM: 64GB per Node.
**Q:** How many executors?
*   **Rule of Thumb:** 5 Cores per executor (Good balance for I/O & CPU).
*   ** Executors per Node:** `Total Cores / 5` = `150 / 5` = 30 Executors (Likely too high for one node, usually 5 executors per node with 5 cores each).
*   *Typical calculation:*
    *   Leave 1 Core/1GB for OS/Hadoop Deamon.
    *   Executors = (Available Cores / 5).
    *   Memory = (Available RAM / Executors).
