# PySpark Scenario-Based Interview Questions & Answers (Question Bank 2)

> **Amazon Data Engineer Style** - Production Scenarios, Performance Optimization, and Troubleshooting

---

<a id="index"></a>
## 📑 Table of Contents

| Section | Topics |
|---------|--------|
| [1️⃣ Performance & Optimization (Q1-5)](#1️⃣-performance--optimization-scenarios-q1-5) | Slowdowns, OOM, Scaling |
| &nbsp;&nbsp;&nbsp;└ [Q1: Sample vs production slowdown](#q1-spark-job-runs-fast-on-sample-but-failsslows-in-production) | Diagnosis checklist |
| &nbsp;&nbsp;&nbsp;└ [Q2: Join causes executor OOM](#q2-join-between-two-large-dataframes-causes-executor-oom) | Solutions |
| &nbsp;&nbsp;&nbsp;└ [Q3: One slow task (skew)](#q3-one-task-takes-20-minutes-while-others-finish-in-seconds) | Fix skew |
| &nbsp;&nbsp;&nbsp;└ [Q4: Job slows as data grows](#q4-spark-job-becomes-slower-every-day-as-data-grows) | Metrics |
| &nbsp;&nbsp;&nbsp;└ [Q5: Small files problem](#q5-pipeline-writes-millions-of-small-files-to-s3adls) | Solutions |
| [2️⃣ Data Skew & Joins (Q6-9)](#2️⃣-data-skew--joins-q6-9) | Salting, Broadcast |
| &nbsp;&nbsp;&nbsp;└ [Q6: Skewed joins (80% same key)](#q6-handle-skewed-joins-80-data-has-same-key) | Salting technique |
| &nbsp;&nbsp;&nbsp;└ [Q7: Broadcast vs Salting vs Repartition](#q7-when-to-use-broadcast-vs-salting-vs-repartitioning) | Decision matrix |
| &nbsp;&nbsp;&nbsp;└ [Q8: Broadcast join fails](#q8-broadcast-join-suddenly-fails-in-production) | Root causes |
| &nbsp;&nbsp;&nbsp;└ [Q9: Large-large join](#q9-efficient-join-between-two-large-datasets) | Strategies |
| [3️⃣ Partitioning & Shuffle (Q10-14)](#3️⃣-partitioning--shuffle-q10-14) | Repartition, Coalesce |
| &nbsp;&nbsp;&nbsp;└ [Q10: Repartition vs Coalesce](#q10-repartition-vs-coalesce--real-use-cases) | When to use |
| &nbsp;&nbsp;&nbsp;└ [Q11: Repartitioned but still slow](#q11-repartitioned-by-date-but-queries-still-slow) | Root causes |
| &nbsp;&nbsp;&nbsp;└ [Q12: Shuffle explosion](#q12-what-causes-shuffle-explosion) | Causes & prevention |
| &nbsp;&nbsp;&nbsp;└ [Q13: Partition count](#q13-how-to-decide-number-of-partitions) | Rules |
| &nbsp;&nbsp;&nbsp;└ [Q14: Too many partitions](#q14-when-does-increasing-partitions-make-performance-worse) | Anti-patterns |
| [4️⃣ Caching & Persistence (Q15-18)](#4️⃣-caching--persistence-q15-18) | When to cache |
| &nbsp;&nbsp;&nbsp;└ [Q15: When to cache](#q15-when-should-you-cache-a-dataframe) | Guidelines |
| &nbsp;&nbsp;&nbsp;└ [Q16: Cache not speeding up](#q16-caching-increased-memory-but-not-speed) | Troubleshooting |
| &nbsp;&nbsp;&nbsp;└ [Q17: Storage levels](#q17-difference-between-storage-levels) | MEMORY_ONLY, DISK |
| &nbsp;&nbsp;&nbsp;└ [Q18: Verify cache is used](#q18-how-to-verify-cache-is-being-used) | Methods |
| [5️⃣ Fault Tolerance (Q19-22)](#5️⃣-fault-tolerance--reliability-q19-22) | Recovery, Recomputation |
| &nbsp;&nbsp;&nbsp;└ [Q19: Executor dies mid-job](#q19-what-happens-when-an-executor-dies-mid-job) | Fault tolerance |
| &nbsp;&nbsp;&nbsp;└ [Q20: Make job restartable](#q20-job-fails-at-95-completion--make-it-restartable) | Checkpoint patterns |
| &nbsp;&nbsp;&nbsp;└ [Q21: Recomputation](#q21-how-does-spark-handle-recomputation) | Lineage |
| &nbsp;&nbsp;&nbsp;└ [Q22: Idempotent pipelines](#q22-design-idempotent-spark-pipelines) | Patterns |
| [6️⃣ File Formats & Storage (Q23-26)](#6️⃣-file-formats--storage-q23-26) | Parquet, Schema |
| &nbsp;&nbsp;&nbsp;└ [Q23: Parquet vs ORC vs CSV](#q23-parquet-vs-orc-vs-csv--when-and-why) | Comparison |
| &nbsp;&nbsp;&nbsp;└ [Q24: Why Parquet improves perf](#q24-why-does-parquet-improve-performance) | Advantages |
| &nbsp;&nbsp;&nbsp;└ [Q25: Time-based query optimization](#q25-optimize-read-performance-for-time-based-queries) | Strategies |
| &nbsp;&nbsp;&nbsp;└ [Q26: Schema changes](#q26-schema-changes-in-parquet-files) | Evolution |
| [7️⃣ Streaming (Q27-30)](#7️⃣-streaming-q27-30) | Watermarks, Semantics |
| &nbsp;&nbsp;&nbsp;└ [Q27: Late-arriving events](#q27-handling-late-arriving-events-in-structured-streaming) | Watermarking |
| &nbsp;&nbsp;&nbsp;└ [Q28: Exactly-once vs At-least-once](#q28-exactly-once-vs-at-least-once-semantics) | Semantics |
| &nbsp;&nbsp;&nbsp;└ [Q29: Watermarking explained](#q29-watermarking--what-problem-does-it-solve) | State cleanup |
| &nbsp;&nbsp;&nbsp;└ [Q30: Job down for 2 hours](#q30-streaming-job-down-for-2-hours--what-happens) | Recovery |

---

<a id="1️⃣-performance--optimization-scenarios-q1-5"></a>
## 1️⃣ Performance & Optimization Scenarios (Q1-5) [↩️](#index)

<a id="q1-spark-job-runs-fast-on-sample-but-failsslows-in-production"></a>
### Q1: Spark job runs fast on sample but fails/slows in production [↩️](#index)

**Diagnosis Checklist:**

| Factor | Sample | Production | Check |
|--------|--------|------------|-------|
| **Data Volume** | 1 GB | 1 TB (1000x) | Input file sizes |
| **Data Skew** | Even | 80% same key | groupBy distribution |
| **Resources** | Dedicated | Shared cluster | Queue waiting |
| **Shuffle** | Fits memory | Spills to disk | Spark UI |
| **Memory** | No OOM | Executor OOM | GC pauses |

```python
# 1. Check partition sizes
df.groupBy(spark_partition_id()).count().show()

# 2. Check data distribution
df.groupBy("join_key").count().orderBy(desc("count")).show(10)

# 3. Common fixes:
# - Add more executors/memory
# - Repartition data
# - Broadcast small tables
# - Salt skewed keys
```

---

<a id="q2-join-between-two-large-dataframes-causes-executor-oom"></a>
### Q2: Join between two large DataFrames causes executor OOM [↩️](#index)

| Cause | Detection | Solution |
|-------|-----------|----------|
| **Skewed key** | One task uses 10x memory | Salt the key |
| **Broadcast too large** | Broadcast > executor memory | Disable auto-broadcast |
| **Shuffle explosion** | Join creates more data | Filter before join |
| **Wrong join type** | Cartesian product | Verify join condition |

```python
# Solution 1: Increase parallelism
spark.conf.set("spark.sql.shuffle.partitions", 1000)

# Solution 2: Disable auto-broadcast
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")

# Solution 3: Enable Adaptive Query Execution
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
```

---

<a id="q3-one-task-takes-20-minutes-while-others-finish-in-seconds"></a>
### Q3: One task takes 20 minutes while others finish in seconds [↩️](#index)

**This is DATA SKEW.**

```python
# Identify skewed key
df.groupBy("partition_key").count().orderBy(desc("count")).show(10)

# Solution 1: Salting
salted = df.withColumn("salt", (rand() * 100).cast("int"))
partial = salted.groupBy("key", "salt").agg(sum("value").alias("partial_sum"))
final = partial.groupBy("key").agg(sum("partial_sum").alias("total"))

# Solution 2: Isolate hot keys
hot_key_df = df.filter(col("key") == "US")
normal_df = df.filter(col("key") != "US")
# Process separately, then union
```

---

<a id="q4-spark-job-becomes-slower-every-day-as-data-grows"></a>
### Q4: Spark job becomes slower every day as data grows [↩️](#index)

| Symptom | Root Cause | Solution |
|---------|------------|----------|
| Linear slowdown | Data volume growing | Scale cluster |
| Exponential slowdown | Join explosion | Filter earlier |
| Irregular slowdown | Data skew on certain days | Adaptive skew |
| Gradual degradation | Small files accumulating | Compaction |

```python
# Auto-scaling partitions based on data volume
input_size_gb = get_input_size("/path/to/data")
num_partitions = max(1, int(input_size_gb * 1024 / 256))
df = spark.read.parquet("/path/to/data").repartition(num_partitions)
```

---

<a id="q5-pipeline-writes-millions-of-small-files-to-s3adls"></a>
### Q5: Pipeline writes millions of small files to S3/ADLS [↩️](#index)

```python
# Solution 1: Coalesce before write
df.coalesce(num_files).write.parquet("/output/")

# Solution 2: maxRecordsPerFile
df.write.option("maxRecordsPerFile", 1000000).parquet("/output/")

# Solution 3: Delta Lake auto-optimization
df.write.format("delta") \
    .option("optimizeWrite", "true") \
    .option("autoCompact", "true") \
    .save("/output/")
```

---

<a id="2️⃣-data-skew--joins-q6-9"></a>
## 2️⃣ Data Skew & Joins (Q6-9) [↩️](#index)

<a id="q6-handle-skewed-joins-80-data-has-same-key"></a>
### Q6: Handle skewed joins (80% data has same key) [↩️](#index)

```python
# TECHNIQUE 1: SALTING
SALT_BUCKETS = 20

# Salt the large (skewed) table
large_df = large_df.withColumn(
    "salted_key",
    when(col("country") == "US", 
         concat(col("country"), lit("_"), (rand() * SALT_BUCKETS).cast("int")))
    .otherwise(col("country"))
)

# Explode the small table for US
us_rows = small_df.filter(col("country") == "US")
us_exploded = us_rows.withColumn(
    "salted_key",
    explode(array([concat(lit("US_"), lit(i)) for i in range(SALT_BUCKETS)]))
)

# Join on salted key
result = large_df.join(small_df_salted, "salted_key")
```

---

<a id="q7-when-to-use-broadcast-vs-salting-vs-repartitioning"></a>
### Q7: When to use Broadcast vs Salting vs Repartitioning [↩️](#index)

| Technique | When to Use | Data Size | Skew? |
|-----------|-------------|-----------|-------|
| **Broadcast** | One table is small (< 500 MB) | Small + Large | Any |
| **Repartition** | Both tables large, no skew | Large + Large | No |
| **Salting** | Skewed keys causing slow tasks | Large + Any | Yes |
| **Bucketing** | Repeated joins on same key | Large + Large | No |

---

<a id="q8-broadcast-join-suddenly-fails-in-production"></a>
### Q8: Broadcast join suddenly fails in production [↩️](#index)

| Cause | Detection | Solution |
|-------|-----------|----------|
| **Table grew beyond threshold** | Broadcast size exceeded | Increase threshold |
| **Table grew beyond driver memory** | Driver OOM | Switch to shuffle join |
| **Network timeout** | Timeout error | Increase timeout |

```python
# Solution 1: Increase threshold
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "100m")

# Solution 2: Disable broadcast
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
```

---

<a id="q9-efficient-join-between-two-large-datasets"></a>
### Q9: Efficient join between two large datasets [↩️](#index)

```python
# STRATEGY 1: Filter first, join less data
df1_filtered = df1.filter(col("date") == target_date).select("key", "value1")
df2_filtered = df2.filter(col("active") == True).select("key", "value2")
result = df1_filtered.join(df2_filtered, "key")

# STRATEGY 2: Bucketing for repeated joins
df1.write.bucketBy(200, "key").sortBy("key").saveAsTable("orders_bucketed")
df2.write.bucketBy(200, "key").sortBy("key").saveAsTable("customers_bucketed")
# Future joins are shuffle-free!
```

---

<a id="3️⃣-partitioning--shuffle-q10-14"></a>
## 3️⃣ Partitioning & Shuffle (Q10-14) [↩️](#index)

<a id="q10-repartition-vs-coalesce--real-use-cases"></a>
### Q10: Repartition vs Coalesce — real use cases [↩️](#index)

| Operation | Shuffle | Use Case |
|-----------|---------|----------|
| `repartition(n)` | Yes | Increase partitions, redistribute |
| `repartition(cols)` | Yes | Partition by column for joins |
| `coalesce(n)` | No | Decrease partitions before write |

```python
# REPARTITION: After filter reduced data significantly
df_balanced = df_filtered.repartition(10)

# COALESCE: Before writing files
df.coalesce(10).write.parquet("/output/")
```

---

<a id="q11-repartitioned-by-date-but-queries-still-slow"></a>
### Q11: Repartitioned by date but queries still slow [↩️](#index)

```python
# Problem: repartition != physical partitioning on disk
df.repartition("date").write.parquet("/output/")  # Just affects file layout

# Solution: Use partitionBy
df.write.partitionBy("date").parquet("/output/")  # Creates /output/date=2024-02-07/
```

---

<a id="q12-what-causes-shuffle-explosion"></a>
### Q12: What causes shuffle explosion? [↩️](#index)

```python
# CAUSE 1: Exploding array columns
df.select(explode("array_column"))  # 1 row → N rows

# CAUSE 2: Cross join (Cartesian product)
df1.crossJoin(df2)  # 1M × 1M = 1 trillion rows!

# CAUSE 3: Wrong join condition
df1.join(df2)  # CROSS JOIN! No condition

# CAUSE 4: groupBy without filter
df.groupBy("low_cardinality_column").agg(collect_list("data"))
```

---

<a id="q13-how-to-decide-number-of-partitions"></a>
### Q13: How to decide number of partitions [↩️](#index)

```
Target: 100-200 MB per partition
Formula: Total Data Size (MB) / 128 MB = Number of Partitions
```

```python
# SHUFFLE: Adjust based on data volume
data_size_gb = 100
shuffle_partitions = int(data_size_gb * 1024 / 200)
spark.conf.set("spark.sql.shuffle.partitions", shuffle_partitions)

# ADAPTIVE (Spark 3.0+)
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
```

---

<a id="q14-when-does-increasing-partitions-make-performance-worse"></a>
### Q14: When does increasing partitions make performance worse? [↩️](#index)

| Scenario | Why | Solution |
|----------|-----|----------|
| **Overhead dominates** | Task scheduling > processing | Fewer, larger partitions |
| **Small data** | 100 partitions for 100 MB | Match to data size |
| **Write amplification** | 10K partitions = 10K files | Coalesce before write |
| **Driver bottleneck** | Track 1M+ tasks | Keep < 100K tasks |

---

<a id="4️⃣-caching--persistence-q15-18"></a>
## 4️⃣ Caching & Persistence (Q15-18) [↩️](#index)

<a id="q15-when-should-you-cache-a-dataframe"></a>
### Q15: When should you cache a DataFrame? [↩️](#index)

**Cache When:**
1. DataFrame is used **multiple times**
2. DataFrame is **expensive to compute**
3. You have **sufficient memory**

```python
# GOOD: Used multiple times
df_transformed.cache()
result1 = df_transformed.filter(col("region") == "US")
result2 = df_transformed.filter(col("region") == "EU")
df_transformed.unpersist()  # After use

# BAD: Used once
df.cache()
df.write.parquet("/output/")  # Only one action
```

---

<a id="q16-caching-increased-memory-but-not-speed"></a>
### Q16: Caching increased memory but not speed [↩️](#index)

| Issue | Explanation | Fix |
|-------|-------------|-----|
| **Cache not materialized** | Only actions trigger cache | Call `.count()` after cache |
| **No reuse** | Used only once | Remove cache |
| **New DataFrame created** | Transform after cache | Cache the final DataFrame |

---

<a id="q17-difference-between-storage-levels"></a>
### Q17: Difference between storage levels [↩️](#index)

| Level | Where | Serialized | Use Case |
|-------|-------|------------|----------|
| `MEMORY_ONLY` | RAM | No | Fast read |
| `MEMORY_ONLY_SER` | RAM | Yes | Memory pressure |
| `MEMORY_AND_DISK` | RAM + Disk | No | Large data |
| `DISK_ONLY` | Disk | Yes | Huge data |

---

<a id="q18-how-to-verify-cache-is-being-used"></a>
### Q18: How to verify cache is being used [↩️](#index)

```python
# Method 1: Spark UI → Storage tab
# Method 2: Check execution plan
df.cache()
df.count()  # Materialize
df.explain()  # Look for "InMemoryTableScan"

# Method 3: Compare execution times
df.cache()
start = time.time()
df.count()  # First: computes AND caches
print(f"First: {time.time() - start:.2f}s")
df.count()  # Second: uses cache (much faster)
```

---

<a id="5️⃣-fault-tolerance--reliability-q19-22"></a>
## 5️⃣ Fault Tolerance & Reliability (Q19-22) [↩️](#index)

<a id="q19-what-happens-when-an-executor-dies-mid-job"></a>
### Q19: What happens when an executor dies mid-job? [↩️](#index)

```
1. EXECUTOR DIES (OOM, spot termination)
           │
2. DRIVER DETECTS (heartbeat timeout)
           │
3. TASKS RESCHEDULED on other executors
           │
4. RECOMPUTATION from last available data (lineage/DAG)
           │
5. CLUSTER MANAGER may launch replacement executor
```

---

<a id="q20-job-fails-at-95-completion--make-it-restartable"></a>
### Q20: Job fails at 95% completion — make it restartable [↩️](#index)

```python
# STRATEGY 1: Checkpoint by partition
def process_with_checkpoint(partition_values, output_path):
    completed = load_completed_partitions()
    
    for partition in partition_values:
        if partition in completed:
            continue  # Skip
        
        process_partition(partition)
        mark_completed(partition)

# STRATEGY 2: Delta Lake transaction log
df.write.format("delta").partitionBy("date").mode("overwrite").save("/output/")
```

---

<a id="q21-how-does-spark-handle-recomputation"></a>
### Q21: How does Spark handle recomputation? [↩️](#index)

```python
# LAZY EVALUATION + LINEAGE = AUTOMATIC RECOMPUTATION
# If task fails: Spark traces lineage, recomputes from last materialized point

# LONG LINEAGE PROBLEM:
# Solution: Checkpoint
df_step_50 = df.transform(step1_to_50)
df_step_50.checkpoint()  # Breaks lineage here
df_step_50.count()  # Materialize

df_final = df_step_50.transform(step51_to_100)
```

---

<a id="q22-design-idempotent-spark-pipelines"></a>
### Q22: Design idempotent Spark pipelines [↩️](#index)

```python
# PATTERN 1: Partition Overwrite
df.write.mode("overwrite").partitionBy("date") \
    .option("replaceWhere", f"date = '{processing_date}'") \
    .format("delta").save("/output/")

# PATTERN 2: MERGE (upsert)
deltaTable.merge(new_data, "target.id = source.id") \
    .whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()

# ❌ ANTI-PATTERN
df.write.mode("append").parquet("/output/")  # Duplicates on retry
```

---

<a id="6️⃣-file-formats--storage-q23-26"></a>
## 6️⃣ File Formats & Storage (Q23-26) [↩️](#index)

<a id="q23-parquet-vs-orc-vs-csv--when-and-why"></a>
### Q23: Parquet vs ORC vs CSV — when and why? [↩️](#index)

| Format | Compression | Column Pruning | Best For |
|--------|-------------|----------------|----------|
| **Parquet** | Excellent | Yes | General analytics |
| **ORC** | Excellent | Yes | Hive ecosystem |
| **CSV** | Poor | No | Interchange, legacy |
| **Avro** | Good | No | Streaming |

---

<a id="q24-why-does-parquet-improve-performance"></a>
### Q24: Why does Parquet improve performance? [↩️](#index)

1. **Columnar Storage**: Only read needed columns (90% less I/O)
2. **Compression**: 10x smaller than CSV
3. **Predicate Pushdown**: Skip row groups based on min/max
4. **Schema Evolution**: New columns can be added

---

<a id="q25-optimize-read-performance-for-time-based-queries"></a>
### Q25: Optimize read performance for time-based queries [↩️](#index)

```python
# STRATEGY 1: Partition by date
df.write.partitionBy("year", "month", "day").parquet("/data/events/")

# STRATEGY 2: Z-ordering (Delta Lake)
deltaTable.optimize().executeZOrderBy("timestamp")

# STRATEGY 3: Bloom filters (Spark 3.3+)
df.write.option("parquet.bloom.filter.enabled#timestamp", "true").parquet("/data/")
```

---

<a id="q26-schema-changes-in-parquet-files"></a>
### Q26: Schema changes in Parquet files [↩️](#index)

```python
# SAFE: Add new nullable column, widen type (INT → LONG)
# BREAKING: Remove column, incompatible type change

df = spark.read.option("mergeSchema", "true").parquet("/data/")
```

---

<a id="7️⃣-streaming-q27-30"></a>
## 7️⃣ Streaming (Q27-30) [↩️](#index)

<a id="q27-handling-late-arriving-events-in-structured-streaming"></a>
### Q27: Handling late-arriving events in Structured Streaming [↩️](#index)

```python
# WATERMARKING: Accept 10 min late, then drop
windowed_counts = (events_stream
    .withWatermark("event_time", "10 minutes")
    .groupBy(window("event_time", "5 minutes"), "event_type")
    .count()
)
```

---

<a id="q28-exactly-once-vs-at-least-once-semantics"></a>
### Q28: Exactly-once vs At-least-once semantics [↩️](#index)

| Semantic | Guarantee | Performance |
|----------|-----------|-------------|
| **At-most-once** | May lose data | Fast |
| **At-least-once** | May duplicate | Good |
| **Exactly-once** | No loss, no dups | Slower |

---

<a id="q29-watermarking--what-problem-does-it-solve"></a>
### Q29: Watermarking — what problem does it solve? [↩️](#index)

**Problem:** Unbounded state growth (memory grows infinitely)

**Solution:** Watermark = max(event_time) - threshold
- Events with event_time < watermark are dropped
- State for old windows is cleared

---

<a id="q30-streaming-job-down-for-2-hours--what-happens"></a>
### Q30: Streaming job down for 2 hours — what happens? [↩️](#index)

```python
# With Kafka + Checkpointing:
# 1. Checkpoint stores last processed Kafka offset
# 2. On restart, Spark reads checkpoint
# 3. Resumes from last offset
# 4. Processes 2 hours of backlog

# Considerations:
# - Kafka retention must be > 2 hours
# - Backlog processing may spike resources
# - Use maxOffsetsPerTrigger for rate limiting
```
