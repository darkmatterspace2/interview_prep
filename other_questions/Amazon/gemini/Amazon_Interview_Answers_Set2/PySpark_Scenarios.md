# PySpark Scenario-Based Interview Questions & Answers

## A. Performance & Optimization Scenarios

#### 1. Your Spark job runs fast on sample data but **fails or slows drastically in production**. How do you diagnose and fix it?
**Diagnosis:**
*   **Skew:** Production data likely has skewed keys not present in specific samples. Check Spark UI (Stages tab) for "straggler tasks" (one task taking much longer than others).
*   **Volume:** Sample data fits in memory; production data spills to disk (Shuffle Spill). Check "Disk Bytes Spilled" in Spark UI.
*   **Resources:** Sample environment might be isolated; production might have noisy neighbors or network contention.
**Fix:**
*   Enable **Adaptive Query Execution (AQE)** (`spark.sql.adaptive.enabled=true`) to handle skew and coalesce partitions dynamically.
*   Identify the bottleneck stage. If it's a join, check for skew (use salting or broadcast). If it's reading, check for small files.

#### 2. A join between two large DataFrames causes **executor OOM**. What are your options?
**Analysis:** Standard Sort-Merge Join requires shuffling. If one partition is huge (skew) or the shuffle buffer is too small, OOM occurs.
**Options:**
1.  **Increase Partition Count:** `spark.sql.shuffle.partitions`. Smaller partitions mean less data per task, reducing memory pressure.
2.  **Increase Executor Memory:** `spark.executor.memory`. (Vertical scaling).
3.  **Handle Skew:** If OOM is due to one massive key, use Salted Join.
4.  **External Shuffle Service:** Ensure it's enabled so shuffle files are stored separately from executor heap.

#### 3. One task takes 20 minutes while others finish in seconds. What is happening and how do you fix it?
**Scenario:** Classic Data Skew.
**Why:** One partition has significantly more data than others (e.g., Key="Unknown" or "Null").
**Fix:**
*   **Salting:** Add a random suffix (0-N) to the skewed key in both tables, join on `(key, salt)`, then drop the salt. This explodes the skewed key into N partitions.
*   **Filter Nulls:** If the skewed key is `null` and you don't need it, filter before joining.
*   **Broadcast:** If one table is small enough, force a broadcast join to avoid the shuffle entirely.

#### 4. A Spark job becomes slower every day as data grows. What metrics do you check first?
**Metrics:**
1.  **Input Size vs. Time:** Is it linear or exponential?
2.  **Shuffle Size:** Is the shuffle growing faster than input? (Suggests Cartesian products or bad joins).
3.  **Spill to Disk:** Check if memory is no longer sufficient, forcing costly disk I/O.
4.  **Number of Files:** Are you reading millions of tiny files? (Listing overhead).

#### 5. Your pipeline writes **millions of small files** to S3/ADLS. Why is this bad and how do you fix it?
**Why Bad:**
*   **namenode/metadata pressure:** S3/HDFS spends huge time listing files.
*   **Read Latency:** Opening a file has overhead. Reading 1 byte from 1 million files is 1000x slower than 1MB from 1 file.
**Fix:**
*   **Coalesce/Repartition:** `df.coalesce(N)` before write (merges partitions without full shuffle).
*   **AQE:** `spark.sql.adaptive.coalescePartitions.enabled` automatically merges small shuffle partitions.
*   **Compaction Job:** Run a separate job to read small files and rewrite them as larger chunks (e.g., 512MB - 1GB).

---

## B. Data Skew & Joins

#### 6. One key (e.g., `country = US`) has 80% of the data. How do you handle skewed joins?
**Strategy:**
*   **Isolated Processing:** Filter `US` data into one DF, and `Non-US` into another. Process `US` with higher parallelism (or salting). Process `Non-US` normally. Union results.
*   **Salting:** (As described in Q3).
*   **Broadcast:** If joining to a small dimension table (e.g., `CountryCodes`), Broadcast the dimension table. It duplicates the small table to every node, so the massive `US` partition doesn't need to move/shuffle.

#### 7. When would you use: Broadcast vs Salting vs Repartitioning?
*   **Broadcast:** When one side is **small** (<100MB-something GB). Fastest join. No shuffle.
*   **Salting:** When both sides are **large** AND there is **skew** on specific keys.
*   **Repartitioning:** When you need to increase parallelism generally (e.g., data is evenly distributed but partitions are too large > 2GB, causing OOM).

#### 8. A broadcast join suddenly fails in production. Why might that happen?
*   **Data Growth:** The "small" table grew beyond the `spark.sql.autoBroadcastJoinThreshold` (default 10MB) or driver memory limits.
*   **Driver OOM:** Broadcast joins collect the table to the driver before sweeping to executors. If the table is bigger than Driver RAM, it crashes.
*   **Timeout:** Broadcasting a table takes time; network slowness can cause timeouts.

#### 9. Two datasets are both large — how do you design an efficient join?
*   **Bucketing:** Pre-bucket both tables by the Join Key (sort and partition storage). Spark minimizes shuffling (Sort-Merge Join becomes efficient local merges).
*   **Filter Early:** Push down predicates (WHERE clauses) before the join.
*   **Select Needed Columns:** Don't drag unused columns through the shuffle.

---

## C. Partitioning & Shuffle

#### 10. Difference between `repartition()` and `coalesce()` — real use cases.
*   **repartition(N):** Full shuffle. Distributes data evenly.
    *   *Use Case:* Increasing parallelism (N > current), or fixing severe skew by random redistribution.
*   **coalesce(N):** No full shuffle. Merges existing partitions locally.
    *   *Use Case:* Reducing partition count before writing to disk (e.g., from 1000 shuffle partitions to 10 output files). *Note:* Can only decrease N.

#### 11. You repartition by date, but queries are still slow. Why?
**Reason:** `repartition("date")` puts all data for `2023-01-01` into a **single partition**.
*   If you have 10TB of data for that day, you effectively created one massive customized skew partition that one task must process.
*   *Fix:* `repartition("date", "region")` or `repartition(N, "date")` to spread that day's data across multiple partitions.

#### 12. What causes **shuffle explosion**?
*   **Cartesian Join (Cross Join):** Joining without a key or on a key with few distinct values implies M * N rows.
*   **Explode:** Using `explode()` on a highly nested array with many elements increases row count exponentially.

#### 13. How do you decide **number of partitions**?
**Rule of Thumb:** 2 to 3 times the number of available cores.
*   **Partition Size:** Aim for 128MB - 200MB per partition.
*   *Math:* Total Data Size / 128MB = Target Partitions.

#### 14. When does increasing partitions make performance worse?
*   **Scheduler Overhead:** If you have 100,000 partitions for 1GB of data, Spark spends more time scheduling tasks than executing them.
*   **Small Files:** Writing out too many partitions leads to the "small file problem".

---

## D. Caching & Persistence

#### 15. When should you cache a DataFrame?
*   **Reuse:** When a DF is reused in multiple subsequent actions (e.g., `df` -> `count()`, `df` -> `write()`, `df` -> `join()`).
*   **Iterative:** Algorithms (ML loops, PageRank).
*   *Don't Cache:* If you only use the DF once. It costs time to write to memory/disk.

#### 16. Why did caching increase memory usage but not speed?
*   **Deserialization:** `MEMORY_ONLY` stores objects as deserialized Java objects, which consume huge RAM. The GC (Garbage Collector) overhead might outweigh compute savings.
*   **Spill:** If cache doesn't fit in RAM, it spills to disk (if configured) or recomputes, negating speed benefits.

#### 17. Difference between Storage Levels.
*   **MEMORY_ONLY:** Fast, deserialized java objects. Risk: OOM / Data loss (recompute).
*   **MEMORY_AND_DISK:** Spills to disk if RAM full. Safest balanced default for costly computations.
*   **DISK_ONLY:** Good for massive checkpoints where recomputation is more expensive than Disk I/O.

#### 18. How do you know if cache is actually being used?
*   **Spark UI (Storage Tab):** Shows % cached.
*   **Stages DAG:** Look for a green dot/highlight on the stage, usually indicating an RDD read from memory.
*   **Execution Time:** First run is slow (generating cache), second run is fast.

---

## E. Fault Tolerance & Reliability

#### 19. An executor dies mid-job. What happens?
**Spark Resilience:**
*   Driver detects loss.
*   Spark identifies which partitions (tasks) were on that executor.
*   Lineage (DAG) is consulted. Spark re-schedules *only* those failed tasks on other healthy executors.

#### 20. A job fails at 95% completion. How do you make it restartable?
*   **Checkpointing:** Save intermediate results to persistent storage (HDFS/S3) at critical stages. `df.write.parquet("intermediate_step")`. Use this as source for step 2.
*   **State Store:** In streaming, offsets ensure restart from failure point.

#### 21. How does Spark handle recomputation?
Through **RDD Lineage**. Spark keeps the "recipe" (transformations) to create any RDD. If data is lost, it replays the recipe from the original source or the last checkpoint.

#### 22. How do you design **idempotent Spark pipelines**?
*   **Overwrite by Partition:** `df.write.mode("overwrite").partitionBy("date").save(...)`.
*   If the job generates data for `2023-01-01`, running it 5 times simply effectively overwrites that specific folder 5 times. The final state is always consistent.

---

## F. File Formats & Storage

#### 23. Parquet vs ORC vs CSV — when and why?
*   **CSV:** Human readable, distinct, universal. *Slow (no compression, row-based, no schema enforcement).*
*   **Parquet:** Spark native, Columnar. *Good for wide tables where you query few columns.*
*   **ORC:** Columnar, high compression. *Often better for Hive environments.*

#### 24. Why does Parquet improve performance?
1.  **Columnar Projection:** Reading `SELECT id FROM table` only reads the `id` column blocks.
2.  **Predicate Pushdown:** Metadata (min/max) allows Spark to skip entire file chunks if the value isn't there (e.g., `WHERE id = 500`).
3.  **Compression:** Homogeneous data in columns compresses 10x better than rows.

#### 25. How do you optimize read performance for time-based queries?
**Partitioning:** Folder structure `year=2023/month=01/day=01`.
Spark's **Partition Discovery** allows it to scan *only* the relevant folders for a query like `WHERE date >= '2023-01-01'`, skipping years of historical data.

#### 26. What happens if schema changes in Parquet files?
Parquet embeds schema in the footer.
*   If new files have column `C`: Spark Merge Schema (`spark.sql.parquet.mergeSchema=true`) can handle it, but it adds initialization overhead to scan all footers.
*   Without merge, reading mix of files might fail or return nulls.

---

## G. Streaming

#### 27. Handling late-arriving events in Structured Streaming.
**Watermarking:** `df.withWatermark("timestamp", "10 minutes")`.
Spark keeps the state for the window open for 10 minutes. If data arrives within that buffer, it updates the result. If later, it is dropped.

#### 28. Exactly-once vs at-least-once semantics.
*   **At-Least-Once:** Default. Data processed, but if acknowledgment fails, may process again.
*   **Exactly-Once:** Requires **Idempotent Sink** (handling dupes) + **Checkpointing** (tracking offsets).

#### 29. Watermarking — what problem does it solve?
State Management Memory. Without watermark, Spark must keep *all* windows open forever waiting for potential late data, causing OOM. Watermark tells Spark "It's safe to drop state for time < T".

#### 30. What happens if the streaming job is down for 2 hours?
*   Upon restart, Spark reads the checkpoint.
*   It sees the last committed offset.
*   It asks Kafka/Kinesis for all data since that offset.
*   **Risk:** Massive "burst" of 2 hours of data might cause OOM or lag. You may need to enable `maxOffsetsPerTrigger` to process the backlog in chunks.
