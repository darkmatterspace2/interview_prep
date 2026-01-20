# PySpark Scenario-Based Interview Questions
*Mid to Senior Level*

This guide focuses on real-world production scenarios, performance tuning, and architectural challenges commonly asked in Data Engineering interviews.

---

## Table of Contents
1. [Performance Tuning & OOM Issues](#performance-tuning--oom-issues)
2. [Data Skew Scenarios](#data-skew-scenarios)
3. [File Management & Storage](#file-management--storage)
4. [Complex Transformation Logic](#complex-transformation-logic)
5. [Structured Streaming Scenarios](#structured-streaming-scenarios)

---

## Performance Tuning & OOM Issues

### 1. The "Last 2 Tasks" Hanging Problem
**Scenario:** You are running a Spark job with 200 tasks. 198 tasks finish in 2 minutes, but the last 2 tasks hang for 45 minutes and finally cause an OOM (Out Of Memory) error. What is happening and how do you fix it?

**Analysis:**
This is a classic symptom of **Data Skew**. The data is not evenly distributed across partitions. One or two keys have millions of records (e.g., `null` keys or a default 'Unknown' value), causing a few executors to process 50x more data than others.

**Solutions:**
1.  **Salted Key Join:** Add a random number (salt) to the skew key to distribute it across multiple partitions (explained in Section 2).
2.  **Broadcast Join:** If one side of the join is small, force a Broadcast join to avoid shuffling the large skew table.
3.  **Filter Nulls:** If the skew is caused by `null` keys that you don't actually need, filter them out *before* the join.

### 2. Driver OOM vs Executor OOM
**Scenario:** Your job fails with `java.lang.OutOfMemoryError`. How do you distinguish if it's the Driver or the Executor, and what are the fixes for each?

**Answer:**
*   **Driver OOM (`java.lang.OutOfMemoryError: Java heap space` on Driver):**
    *   **Cause:** Doing `df.collect()` on a large dataset, broadcasting a table that is too big (>8GB), or maintaining too much metadata in a complex DAG outside of DataFrames.
    *   **Fix:** Avoid `collect()`, use `toLocalIterator()`, increase `spark.driver.memory`, or increase `spark.sql.autoBroadcastJoinThreshold` if a broadcast is crashing it.
*   **Executor OOM:**
    *   **Cause:** Large partitions (Skew), creating very large objects in UDFs, or simple lack of memory for the task.
    *   **Fix:** Handle Skew, decrease `spark.sql.files.maxPartitionBytes` to break up inputs, or increase `spark.executor.memory`.

### 3. Catalyst Optimizer & Physical Plans
**Scenario:** A junior engineer wrote a query joining 3 tables. How can you tell if Spark is using the most efficient Join Strategy?

**Answer:**
Use `df.explain(True)` to view the Physical Plan. Look for:
*   **BroadcastHashJoin:** Fastest. Used for Big Table + Small Table.
*   **SortMergeJoin:** Standard for Big + Big tables. Requires a Shuffle and Sort phase.
*   **ShuffleHashJoin:** Used when tables are large but one fits in executor memory (rarely defaults over SortMerge).
*   **CartesianProduct:** DANGER. Nested loop join. Occurs if you join without conditions or using a non-equi join on 2 distinct tables.

---

## Data Skew Scenarios

### 4. Implementing the Salted Key Join
**Scenario:** You need to join a `Transactions` table (100 Billion rows) with a `Customers` table (10 Million rows) on `customer_id`. The `Customers` table is too big to broadcast. A few VIP customers have millions of transactions, causing skew.

**Solution (Salting Technique):**
We split the skewed keys in the Big Table into smaller chunks and replicate the matching keys in the Medium Table.

1.  **Explode (Replicate) the Smaller Table:** 
    Create `N` copies of each row in `Customers`, adding a `salt` ID (0 to N-1).
2.  **Salt the Larger Table:** 
    Add a random number (0 to N-1) to every row in `Transactions`.
3.  **Join:** 
    Join on `customer_id` AND `salt`.

**Code Snippet:**
```python
from pyspark.sql.functions import rand, explode, array, lit, col

SALT_FACTOR = 10

# 1. Salt the Big Table (Transactions)
df_tx_salted = df_tx.withColumn("salt", (rand() * SALT_FACTOR).cast("int"))

# 2. Replicate the Medium Table (Customers)
# Create array [0, 1, ... 9] and explode it to generate rows
df_cust_salted = df_cust.withColumn("salt_array", array([lit(i) for i in range(SALT_FACTOR)])) \
                        .withColumn("salt", explode("salt_array"))

# 3. Join on Key + Salt (Evenly distributed!)
df_joined = df_tx_salted.join(df_cust_salted, ["customer_id", "salt"])
```

---

## File Management & Storage

### 5. Small File Problem
**Scenario:** Your Hive/Delta table has 100 partitions, but each partition contains 5,000 tiny files (KB size). Query performance is terrible. Why?

**Answer:**
*   **Why:** Opening a file in HDFS/S3 has high overhead (latency/metadata ops). Spark spends more time listing and opening files than reading data.
*   **Fix (Write Side):**
    *   `df.coalesce(5).write...` (Reduces files per partition without shuffling).
    *   `df.repartition(5, "col").write...` (Guarantees exactly 5 files, good for partition writes).
*   **Fix (Maintenance):** Perform "Compaction". Read the partition and overwrite it with `repartition()`.
*   **Fix (Auto):** In Delta Lake, run `OPTIMIZE table_name`.

### 6. Parquet vs Avro vs ORC
**Scenario:** Which file format would you choose for a Write-Heavy transactional system vs a Read-Heavy analytical system?

*   **Parquet:**
    *   **Type:** Columnar.
    *   **Best For:** Heavy Analytics (OLAP). Compresses very well, allows **Column Pruning** (reading only needed columns) and **Predicate Pushdown**.
    *   **Use Case:** Data Lake reporting layer.
*   **Avro:**
    *   **Type:** Row-based.
    *   **Best For:** Write-heavy ops, Schema evolution support.
    *   **Use Case:** Kafka landing zones, CDC capture (where you need to write whole rows fast).

---

## Complex Transformation Logic

### 7. Sessionization (Gaps and Islands)
**Scenario:** You have clickstream data: `user_id`, `timestamp`. Identify "Sessions" where a session expires if the user is inactive for more than 30 minutes.

**Solution:**
Use Window functions to compare the current timestamp with the previous one.

```python
from pyspark.sql import Window
from pyspark.sql.functions import lag, col, sum as spark_sum, unix_timestamp

# Check difference between current and prev timestamp
w = Window.partitionBy("user_id").orderBy("timestamp")

df = df.withColumn("prev_ts", lag("timestamp").over(w))
       
# Flag new session if gap > 30 mins (1800 seconds)
df = df.withColumn("is_new_session", 
    (unix_timestamp("timestamp") - unix_timestamp("prev_ts") > 1800).cast("int"))

# Cumulative Sum to generate Session ID
df = df.withColumn("session_id", 
    spark_sum("is_new_session").over(w))
```

### 8. Handling "Late" Data in Aggregations
**Scenario:** You are calculating hourly aggregates. Data from 9:00 AM might arrive at 10:15 AM due to network lag. How do you handle this?

**Answer:**
*   **Batch:** Reprocess partitions (e.g., overwrite today AND yesterday's data every run).
*   **Structured Streaming:** Use **Watermarking**.
    *   `withWatermark("timestamp", "2 hours")` tells Spark to keep the aggregation state for 2 hours. If data arrives within that window, the aggregate updates. If it arrives 3 hours late, it is dropped.

---

## Optimization Checklist (Quick Fire)

1.  **Cache/Persist:** Only cache if you reuse the DataFrame multiple times. Unpersist when done!
2.  **Serialization:** Use Kryo serialization (`conf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")`) for better performance than Java serialization.
3.  **Pandas UDFs:** If you MUST use python code (UDF), use Vectorized Pandas UDFs (Arrow) instead of standard Python UDFs. Standard UDFs serialize row-by-row (slow), Pandas UDFs use batches (fast).
4.  **Filter Early:** Filter data as close to the source as possible to reduce shuffle data volume.
