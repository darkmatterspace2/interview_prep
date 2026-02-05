# Amazon Big Data & Spark Interview Questions

## Part 1: Distributed Concepts & Optimization

### Spark / Distributed Concepts

#### 76. What causes data skew?
**Answer:**
Data skew occurs when data is not evenly distributed across partitions/nodes.
*   *Cause:* A specific key (e.g., `null` or a generic "unknown" value) appears disproportionately often in the join or group-by column.
*   *Effect:* One task takes 100x longer than others, holding up the entire stage (straggler task).

#### 77. Wide vs narrow transformations.
**Answer:**
*   **Narrow:** Data required to compute the records in a single partition resides in at most one partition of the parent RDD. No shuffling.
    *   *Examples:* `map`, `filter`, `union`.
*   **Wide:** Data required resides in many partitions of the parent RDD. Requires shuffling.
    *   *Examples:* `groupByKey`, `reduceByKey`, `join` (usually).

#### 78. Why joins are expensive?
**Answer:**
Joins typically require a **Shuffle**.
*   Spark must send data across the network so that all records with the same Key end up on the same Node.
*   Network I/O and Disk I/O (serialization/deserialization) during shuffle are the bottlenecks.

#### 79. Shuffle — what and why?
**Answer:**
The process of redistributing data across partitions. It is needed for operations like grouping or joining where the answer depends on data currently residing on different machines.

#### 80. Partitioning vs bucketing.
**Answer:**
*   **Partitioning:** Physical folder structure (e.g., `/date=2023-01-01/`). Effective for pruning directory scans.
*   **Bucketing:** Hashing data into fixed number of files (buckets) within a partition based on a column.
    *   *Benefit:* If two tables are bucketed by the same column into the same # of buckets, joins can avoid shuffling (Sort-Merge Join becomes local).

---

### Optimization

#### 81. How to optimize large joins?
**Answer:**
1.  **Broadcast Join:** If one table is small.
2.  **Filter early:** Remove rows before joining.
3.  **Bucketing:** Pre-sort and partition data.
4.  **Salting:** If skewed, add a random suffix (salt) to keys to distribute the load, join, then unsalt.

#### 82. Broadcast join — when?
**Answer:**
When one side of the join is small enough to fit in memory (default threshold is 10MB in Spark, but can be larger).
*   Spark sends a copy of the small table to *every* node.
*   The large table is processed locally without shuffling. Huge performance gain.

#### 83. Repartition vs coalesce.
**Answer:**
*   **Repartition:** Can increase or decrease partitions. Performs a *full shuffle*. use when you need to balance data or increase parallelism.
*   **Coalesce:** Can only *decrease* partitions. Minimizes shuffling (merges local partitions). Use when writing final output to reduce file count.

#### 84. File size optimization.
**Answer:**
Resulting files should be close to the HDFS block size (128MB) or slightly larger.
*   *Too small:* "Small file problem" (metadata overhead).
*   *Too large:* Cannot be parallelized effectively.

#### 85. Handling small files problem.
**Answer:**
*   **Ingestion:** Compact small files into larger ones (Compaction job).
*   **Spark:** Use `coalesce()` before writing. Use `AQE` (Adaptive Query Execution) which can coalesce shuffle partitions automatically.

---

## Part 2: Spark & PySpark Scenarios

#### 1. Core Concepts: RDD vs DataFrame vs Dataset
**Answer:**
*   **RDD:** Low-level, unstructured. Compilation checks fail at runtime. Hard to optimize.
*   **DataFrame:** Structured (Schema). Optimized by Catalyst Optimizer. Easy to use (SQL-like).
*   **Dataset:** (Scala/Java only) Type-safe + Catalyst optimization. Best of both worlds.
*   *Choice:* Always use DataFrame/Dataset for performance (Catalyst) unless you need low-level control.

#### 2. Optimization Scenario: Shipments (Large) Join TruckCodes (Small)
**Question:** Job is slow.
**Answer:**
Force a **Broadcast Join**.
*   Code: `df_large.join(broadcast(df_small), "k")`
*   Reason: Avoids shuffling the Large Shipments table.

#### 3. Troubleshooting: OutOfMemoryError
**Answer:**
1.  **Driver OOM:** `collect()` is pulling too much data to the driver. Remove `collect()`.
2.  **Executor OOM:** 
    *   **Skew:** One task getting too much data. (Solution: Salting).
    *   **Big Partition:** Partition size > Memory. (Solution: `repartition()` to increase parallelism).
    *   **Memory Configuration:** Increase `spark.executor.memory`.

#### 4. Internals: Fault Tolerance & DAG
**Answer:**
*   **DAG (Directed Acyclic Graph):** Logic of the job execution plan.
*   **Lazy Evaluation:** Spark doesn't execute until an Action (count, write) is called. This allows it to optimize the entire chain (pipelining).
*   **Fault Tolerance:** If a node fails, Spark knows the lineage (from the DAG) of the lost partition and re-computes *only* that missing partition from the source data.

#### 5. File Formats: Parquet over CSV
**Answer:**
*   **Columnar Storage:** Parquet stores data by column.
    *   *Compression:* Type-specific compression (Integers compress better than mixed row text).
    *   *Column Pruning:* Querying just "Status" reads only the "Status" column chunk, not the whole row (I/O saving).
    *   *Predicate Pushdown:* Metadata (Min/Max values) allows skipping chunks that don't satisfy the filter.
