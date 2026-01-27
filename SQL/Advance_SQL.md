# Advanced SQL Concepts (Big Data & Optimization Focus)

## Key Concepts

### 1. Window Functions
Calculations across a set of table rows that are somehow related to the current row. Unlike aggregate functions, window functions do not loosen the individual rows.
*   `ROW_NUMBER()`: Unique number for each row (non-deterministic ties).
*   `RANK()`: Ranking with gaps (1, 2, 2, 4).
*   `DENSE_RANK()`: Ranking without gaps (1, 2, 2, 3).
*   `LAG(col, n)` / `LEAD(col, n)`: Access data from previous or following rows.
*   `SUM(col) OVER (PARTITION BY ... ORDER BY ...)`: Running totals.

### 2. Common Table Expressions (CTEs)
Temporary result sets named within the execution scope of a single statement.
*   **Recursive CTEs:** Useful for hierarchical data (parent-child relationships).
*   **Readability:** Breaks down complex logic into modular steps.

### 3. Query Optimization in Big Data (Spark/Hive/Snowflake)
*   **Partition Pruning:** Reading only specific partitions (directories) based on filter conditions (e.g., `WHERE date = '2023-01-01'`).
*   **Predicate Pushdown:** Pushing filtering logic to the storage layer (Parquet/ORC) to minimize data transfer.
*   **Broadcast Join:** Replicating a small table to all nodes to avoid shuffling the large table (Map-side join).
*   **Shuffle:** The expensive process of redistributing data across the cluster (occurs in `GROUP BY`, `JOIN`).

### 4. Storage Formats
*   **Row-Oriented (Avro, CSV):** Fast writes, good for transactional.
*   **Column-Oriented (Parquet, ORC):** Fast reads (analytical), high compression ratio, supports vectorization.

---

# Advanced SQL Interview Questions

## Performance & Optimization

1.  **A query performing a JOIN between a Billion-row table and a Million-row table is extremely slow. How do you optimize it?**
    *   **Answer:** This sounds like a standard Shuffle Join. I would force a **Broadcast Join** (Map-Side Join). By broadcasting the smaller (1M) table to all worker nodes, we avoid shuffling the 1B row table across the network, drastically reducing I/O and increasing speed.

2.  **What is Data Skew and how does it affect SQL performance? How do you fix it?**
    *   **Answer:** Skew occurs when one partition has significantly more data than others (e.g., Key='null' or a popular UserID). This causes one executor to run for hours while others finish in seconds (stragglers).
    *   **Fix:**
        *   **Salting:** Add a random number (0-N) to the skew key to distribute it into N buckets. Reproduce the join key by exploding the other table N times.
        *   **Filtering:** Separate the skewed key (e.g., NULLs), process it separately, and union the results back.

3.  **Explain "Predicate Pushdown" with an example.**
    *   **Answer:** It is an optimization where the query engine pushes the filtering criteria (`WHERE` clause) down to the storage layer. Instead of reading all data into memory and then filtering, the database/file reader only returns the rows that match.
    *   **Example:** `SELECT * FROM Logs WHERE Year = 2023`. If stored in Parquet, the reader checks metadata statistics (Min/Max values) and skips file blocks that clearly don't contain 2023.

4.  **What is the difference between `Partitioning` and `Bucketing` (Clustering)?**
    *   **Answer:**
        *   **Partitioning:** Physical folder separation (e.g., /date=2023-01-01/). Good for low-cardinality columns.
        *   **Bucketing/Clustering:** Hashing data into a fixed number of files/buckets within a partition. Good for high-cardinality columns (UserID) to optimize Joins (Sort-Merge Bucket Join) and Sampling.

5.  **Why is `COUNT(DISTINCT col)` expensive in distributed systems and how can you optimize it?**
    *   **Answer:** Exact distinct counts require shuffling all values for a key to a single reducer to ensure uniqueness.
    *   **Optimization:** Use `APPROX_COUNT_DISTINCT()` (HyperLogLog) if 100% accuracy isn't required (usually <1% error). Or perform a two-level aggregation: `SELECT COUNT(*) FROM (SELECT DISTINCT col FROM table)`.

## Advanced Querying

6.  **Write a query to find the top 3 highest salaries per Department.**
    *   **Answer:**
        ```sql
        WITH Ranked AS (
            SELECT *, DENSE_RANK() OVER(PARTITION BY DeptID ORDER BY Salary DESC) as rn
            FROM Employees
        )
        SELECT * FROM Ranked WHERE rn <= 3;
        ```

7.  **How do you find "Gaps and Islands" in data? (e.g., find ranges of consecutive login dates).**
    *   **Answer:** A classic problem.
        1.  Use `ROW_NUMBER()` ordered by date.
        2.  Subtract `ROW_NUMBER()` days from the actual Date.
        3.  The result (Difference) will be constant for consecutive dates.
        4.  `GROUP BY` this Difference to find the islands (start/end ranges).

8.  **Explain the difference between `UNION` and `UNION ALL`. Which is faster?**
    *   **Answer:** `UNION` removes duplicates, which requires an expensive sort/distinct operation. `UNION ALL` simply concatenates results. `UNION ALL` is significantly faster and should be preferred if duplicates are impossible or acceptable.

9.  **Write a query to calculate the Year-Over-Year (YoY) growth percentage.**
    *   **Answer:**
        ```sql
        SELECT Year, Revenue,
               LAG(Revenue) OVER (ORDER BY Year) as PrevYearRev,
               (Revenue - LAG(Revenue) OVER (ORDER BY Year)) / LAG(Revenue) OVER (ORDER BY Year) * 100 as YoY_Growth
        FROM Sales;
        ```

10. **How do you pivot a table (Rows to Columns) without using the `PIVOT` function (standard SQL)?**
    *   **Answer:** Use Conditional Aggregation (`CASE WHEN`).
        ```sql
        SELECT Country,
               SUM(CASE WHEN Year = 2020 THEN Revenue ELSE 0 END) as Rev_2020,
               SUM(CASE WHEN Year = 2021 THEN Revenue ELSE 0 END) as Rev_2021
        FROM Sales GROUP BY Country;
        ```

## Big Data & Architecture

11. **What are the pros and cons of using a Surrogate Key in a Big Data warehouse?**
    *   **Pros:** faster joins (integers), independence from source system changes.
    *   **Cons:** Generating unique sequential IDs in a distributed system is hard (requires synchronization/shuffling). Usually, UUIDs or Hashed Keys are preferred in modern Data Lakes to avoid the bottleneck of a sequence generator.

12. **Explain "Vectorization" in query engines.**
    *   **Answer:** The engine processes data in batches (vectors) of columns rather than one row at a time. This allows the CPU to use SIMD (Single Instruction, Multiple Data) instructions, drastically improving cache locality and processing speed for columnar data.

13. **How does a "Sort-Merge Join" work?**
    *   **Answer:** Used for joining two large tables.
        1.  **Shuffle:** Rows with the same join keys are moved to the same nodes.
        2.  **Sort:** Both sides are sorted by the join key.
        3.  **Merge:** The engine iterates through both sorted lists to find matches (O(N+M)).

14. **What is a "Materialized View" and when should you use it?**
    *   **Answer:** A pre-computed result set stored physically. Use it for expensive aggregations (e.g., Daily Sales Dashboard) that are queried frequently but the underlying data changes primarily in batch. It trades storage/refresh-time for query latency.

15. **How do you handle NULLs in Aggregation? Does `COUNT(*)` differ from `COUNT(col)`?**
    *   **Answer:** Yes.
        *   `COUNT(*)` counts *all* rows, including NULLs.
        *   `COUNT(col)` counts rows where `col` is NOT NULL.
        *   `SUM(col)` ignores NULLs.
        *   `AVG(col)` ignores NULLs (be careful: Average of (10, NULL) is 10, not 5).

## Scenarios

16. **How do you delete duplicate rows from a table that has no Primary Key?**
    *   **Answer:** Use `CTID` (Postgres) or `ROWID` (Oracle) or specifically window functions:
        ```sql
        DELETE FROM table WHERE row_id IN (
            SELECT row_id FROM (
                SELECT row_id, ROW_NUMBER() OVER(PARTITION BY all_cols ORDER BY some_col) as rn
                FROM table
            ) WHERE rn > 1
        );
        ```
        In Big Data (Spark/Hive): `INSERT OVERWRITE` into a new table selecting `DISTINCT *` or grouping.

17. **You need to update a 10TB table. Is `UPDATE` good?**
    *   **Answer:** No. In Data Lakes (Parquet), files are immutable. An UPDATE rewrites the entire file (copy-on-write).
    *   **Approach:** Use `MERGE INTO` (Delta Lake/Iceberg) if available. Or, read the data, perform a Full Outer Join with the updates, coalesce the values (New > Old), and overwrite the table (Partition overwrite is best if updates are localized).

18. **Explain the functionality of `CROSS JOIN` and a risk associated with it.**
    *   **Answer:** Produces a Cartesian Product (Every row of A joined with Every row of B).
    *   **Risk:** If A has 1M rows and B has 1M rows, result is 1 Trillion rows. This causes an explosion of data that crashes the cluster (OOM).

19. **What is the difference between `WHERE` and `HAVING`?**
    *   **Answer:**
        *   `WHERE`: Filters rows *before* aggregation/grouping.
        *   `HAVING`: Filters groups *after* aggregation.
        *   Optimization Tip: Always filter as much as possible with `WHERE` before grouping to reduce data volume.

20. **How would you find customers who bought Product A but NEVER bought Product B?**
    *   **Answer:**
        ```sql
        SELECT CustomerID FROM Sales WHERE Product = 'A'
        EXCEPT
        SELECT CustomerID FROM Sales WHERE Product = 'B';
        ```
        Or using `LEFT JOIN` / `NOT EXISTS`.

## Complex Windowing

21. **Calculate the "Session ID" for user clicks. A new session starts if a click is > 30 mins after the previous click.**
    *   **Answer:**
        1.  `LAG` to find prev time.
        2.  `CASE WHEN (Current - Prev) > 30 mins THEN 1 ELSE 0` (New Session Flag).
        3.  `SUM(Flag) OVER (PARTITION BY User ORDER BY Time)` to generate a running Session ID.

22. **What are the frame specifications in Window Functions (ROWS vs RANGE)?**
    *   **Answer:** Defines the window size.
        *   `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`: Cumulative up to now.
        *   `RANGE`: Logical range based on values (e.g., all rows having the same value typically are processed together in ties). `ROWS` is usually faster as it relies on physical position.

23. **How do you find the median salary?**
    *   **Answer:** `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY Salary)`.

24. **Write a query to un-pivot columns (Col1, Col2, Col3) into rows.**
    *   **Answer:** Using `UNION ALL` or `LATERAL VIEW EXPLODE` (Hive/Spark).
        ```sql
        SELECT id, 'Col1' as type, Col1 as val FROM T
        UNION ALL
        SELECT id, 'Col2' as type, Col2 as val FROM T ...
        ```

25. **How do you effectively query a JSON column in SQL?**
    *   **Answer:** Modern SQL (Postgres/Snowflake/Spark) supports semi-structured data.
        *   `col:field` or `GET_JSON_OBJECT` or `FLATTEN`.
        *   **Optimization:** If frequently queried, extract the field into a dedicated column or computed column.

26. **What is a "Recursive CTE" risk?**
    *   **Answer:** Infinite loops. Always ensure the recursion has a termination condition (e.g., `WHERE depth < 100`).

27. **Explain the `COALESCE` function.**
    *   **Answer:** Returns the first non-null value in a list. `COALESCE(HomePhone, CellPhone, WorkPhone, 'N/A')`. Useful for handling NULLs in joins or display.

28. **How do you optimize a query with `LIKE '%pattern%'` (Leading Wildcard)?**
    *   **Answer:** Leading wildcards disable standard B-Tree index usage (Full Table Scan).
    *   **Fix:** Use Full Text Search (Elasticsearch/Solr indexes) or Trigram Indexes (Postgres `pg_trgm`). In Big Data, it's a full scan regardless, so rely on Partition Pruning first.

29. **What is the default isolation level in many SQL databases and what phenomena does it prevent?**
    *   **Answer:** often `Read Committed`. Prevents Dirty Reads but allows Non-Repeatable Reads and Phantoms. In distributed big data (like Spark), we primarily deal with "Snapshot Isolation" per job.

30. **How do you identify the "Second Highest" value without using a window function?**
    *   **Answer:**
        ```sql
        SELECT MAX(Salary) FROM Table WHERE Salary < (SELECT MAX(Salary) FROM Table);
        ```
