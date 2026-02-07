# PySpark Scenario-Based Interview Questions & Answers (Question Bank 2)

> **Amazon Data Engineer Style** - Production Scenarios, Performance Optimization, and Troubleshooting

---

## 1️⃣ Performance & Optimization Scenarios (Q1-5)

### Q1: Spark job runs fast on sample but fails/slows in production

**Diagnosis Framework:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│           PRODUCTION SLOWDOWN DIAGNOSIS CHECKLIST                            │
└─────────────────────────────────────────────────────────────────────────────┘

1. DATA VOLUME
   ├── Sample: 1 GB → Production: 1 TB (1000x)
   └── Check: Input file sizes, row counts per partition

2. DATA SKEW
   ├── Sample: Evenly distributed
   └── Production: 80% rows have same key (e.g., country='US')

3. RESOURCE CONTENTION
   ├── Sample: Dedicated cluster
   └── Production: Shared cluster, queue waiting

4. SHUFFLE
   ├── Sample: Fits in memory
   └── Production: Spills to disk (10-100x slower)

5. MEMORY
   ├── Sample: No OOM
   └── Production: Executor OOM, GC pauses
```

**Diagnosis Steps:**

```python
# 1. Check Spark UI for bottlenecks
# - Stages tab: Which stage is slow?
# - Tasks tab: Is one task much slower? (skew)
# - Executors tab: Memory usage, GC time

# 2. Check partition sizes
df.groupBy(spark_partition_id()).count().show()

# 3. Check data distribution
df.groupBy("join_key").count().orderBy(desc("count")).show(10)

# 4. Check shuffle metrics in Spark UI
# - Shuffle Write/Read sizes
# - Spill (Memory) vs Spill (Disk)

# 5. Common fixes:
# - Add more executors/memory
# - Repartition data
# - Broadcast small tables
# - Filter earlier in pipeline
# - Salt skewed keys
```

---

### Q2: Join between two large DataFrames causes executor OOM

**Root Causes & Solutions:**

| Cause | Detection | Solution |
|-------|-----------|----------|
| **Skewed key** | One task uses 10x memory | Salt the key |
| **Broadcast too large** | Broadcast size > executor memory | Disable auto-broadcast |
| **Shuffle explosion** | Join creates more data than input | Filter before join |
| **Wrong join type** | Cartesian product | Verify join condition |
| **Memory config** | Executor memory < data per task | Increase memory or partitions |

```python
# Solution 1: Increase parallelism (smaller partitions = less memory per task)
spark.conf.set("spark.sql.shuffle.partitions", 1000)  # Default is 200

# Solution 2: Disable auto-broadcast if dimension table grew
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")

# Solution 3: Increase executor memory
# --executor-memory 16g --executor-memory-overhead 4g

# Solution 4: Salt skewed keys
from pyspark.sql.functions import lit, concat, rand

SALT_BUCKETS = 10
# Salt the large (skewed) table
large_df = large_df.withColumn("salt", (rand() * SALT_BUCKETS).cast("int"))
large_df = large_df.withColumn("salted_key", concat(col("key"), lit("_"), col("salt")))

# Explode the small table
from pyspark.sql.functions import explode, array
small_df = small_df.withColumn("salt", explode(array([lit(i) for i in range(SALT_BUCKETS)])))
small_df = small_df.withColumn("salted_key", concat(col("key"), lit("_"), col("salt")))

# Join on salted key
result = large_df.join(small_df, "salted_key")

# Solution 5: Enable Adaptive Query Execution (Spark 3.0+)
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
```

---

### Q3: One task takes 20 minutes while others finish in seconds

**Diagnosis:** This is **data skew**.

```python
# Confirm skew: Check task duration in Spark UI → Tasks tab
# Look for one task with 100x duration/data size

# Identify skewed key
df.groupBy("partition_key").count().orderBy(desc("count")).show(10)
# Result: key='US' has 10M rows, others have 10K

# Solution 1: Salting (see Q2)

# Solution 2: Isolate hot key
hot_key_df = df.filter(col("key") == "US")
normal_df = df.filter(col("key") != "US")

# Process separately
hot_result = process_hot_key(hot_key_df)  # Custom logic, more parallelism
normal_result = normal_df.transform(standard_pipeline)

# Combine
final = hot_result.union(normal_result)

# Solution 3: Two-phase aggregation
# Phase 1: Partial aggregation with salt
salted = df.withColumn("salt", (rand() * 100).cast("int"))
partial = salted.groupBy("key", "salt").agg(sum("value").alias("partial_sum"))

# Phase 2: Combine partial results
final = partial.groupBy("key").agg(sum("partial_sum").alias("total"))
```

---

### Q4: Spark job becomes slower every day as data grows

**Metrics to Check First:**

```python
# 1. Input data volume trend
spark.sql("""
    SELECT date, COUNT(*) as rows, SUM(file_size_mb) as size_mb
    FROM source_table
    GROUP BY date
    ORDER BY date DESC
    LIMIT 30
""")

# 2. Partition count vs data volume
# Check if partitions are growing proportionally
spark.read.parquet("s3://bucket/data/").rdd.getNumPartitions()

# 3. Shuffle metrics over time (from Spark History Server)
# - Shuffle write size trending up?
# - Spill to disk trending up?

# 4. Check for small files accumulation
# ls -la s3://bucket/data/ | wc -l
```

**Solutions:**

| Symptom | Root Cause | Solution |
|---------|------------|----------|
| Linear slowdown | Data volume growing | Scale cluster, optimize code |
| Exponential slowdown | Join explosion | Filter earlier, better join strategy |
| Irregular slowdown | Data skew on certain days | Adaptive skew handling |
| Gradual degradation | Small files accumulating | Compaction, OPTIMIZE |

```python
# Auto-scaling partitions based on data volume
input_size_gb = get_input_size("/path/to/data")
target_partition_size_mb = 256
num_partitions = max(1, int(input_size_gb * 1024 / target_partition_size_mb))

df = spark.read.parquet("/path/to/data").repartition(num_partitions)
```

---

### Q5: Pipeline writes millions of small files to S3/ADLS

**Why It's Bad:**

| Problem | Impact |
|---------|--------|
| **Metadata overhead** | S3 LIST is slow (100 files/sec) |
| **Reader inefficiency** | Each file = one HTTP request |
| **Partition planning** | Driver OOM listing millions of files |
| **Query performance** | Athena/Presto slower with small files |

**Solutions:**

```python
# Solution 1: Coalesce before write
target_file_size_mb = 256
estimated_output_size_mb = df.count() * avg_row_size_bytes / (1024 * 1024)
num_files = max(1, int(estimated_output_size_mb / target_file_size_mb))

df.coalesce(num_files).write.parquet("/output/")

# Solution 2: maxRecordsPerFile
df.write \
    .option("maxRecordsPerFile", 1000000) \
    .parquet("/output/")

# Solution 3: Repartition by output partition columns
df.repartition("date", "region") \
    .write \
    .partitionBy("date", "region") \
    .parquet("/output/")

# Solution 4: Delta Lake auto-optimization
df.write \
    .format("delta") \
    .option("optimizeWrite", "true") \
    .option("autoCompact", "true") \
    .save("/output/")

# Solution 5: Post-write compaction
from delta.tables import DeltaTable
deltaTable = DeltaTable.forPath(spark, "/output/")
deltaTable.optimize().executeCompaction()
```

---

## 2️⃣ Data Skew & Joins (Q6-9)

### Q6: Handle skewed joins (80% data has same key)

```python
# TECHNIQUE 1: SALTING
# Add random suffix to skewed keys in large table
# Replicate small table with all suffixes

SALT_BUCKETS = 20  # More buckets = more parallelism

# Large table (skewed)
large_df = large_df.withColumn(
    "salted_key",
    when(col("country") == "US", 
         concat(col("country"), lit("_"), (rand() * SALT_BUCKETS).cast("int")))
    .otherwise(col("country"))
)

# Small table (replicate for US)
from pyspark.sql.functions import explode, array

us_rows = small_df.filter(col("country") == "US")
us_exploded = us_rows.withColumn(
    "salted_key",
    explode(array([concat(lit("US_"), lit(i)) for i in range(SALT_BUCKETS)]))
)

non_us_rows = small_df.filter(col("country") != "US").withColumn("salted_key", col("country"))
small_df_salted = us_exploded.union(non_us_rows)

# Join on salted key
result = large_df.join(small_df_salted, "salted_key")


# TECHNIQUE 2: ISOLATE HOT KEYS
hot_keys = ["US", "CN", "IN"]
hot_df = large_df.filter(col("country").isin(hot_keys))
cold_df = large_df.filter(~col("country").isin(hot_keys))

# Process hot keys with more parallelism
hot_result = hot_df.repartition(500, "country").join(broadcast(small_df), "country")
cold_result = cold_df.join(broadcast(small_df), "country")

result = hot_result.union(cold_result)
```

---

### Q7: When to use Broadcast vs Salting vs Repartitioning

| Technique | When to Use | Data Size | Skew? |
|-----------|-------------|-----------|-------|
| **Broadcast** | One table is small (< 500 MB) | Small + Large | Any |
| **Repartition** | Both tables large, no skew | Large + Large | No |
| **Salting** | Skewed keys causing slow tasks | Large + Any | Yes |
| **Bucketing** | Repeated joins on same key | Large + Large | No |

```python
# BROADCAST: Small dimension table
result = large_df.join(broadcast(dim_df), "key")

# REPARTITION: Both large, evenly distributed
df1 = df1.repartition(400, "key")
df2 = df2.repartition(400, "key")
result = df1.join(df2, "key")

# BUCKETING: Repeated joins (pre-sort, no shuffle at join time)
df1.write.bucketBy(100, "key").sortBy("key").saveAsTable("table1_bucketed")
df2.write.bucketBy(100, "key").sortBy("key").saveAsTable("table2_bucketed")
# Future joins don't shuffle!
```

---

### Q8: Broadcast join suddenly fails in production

**Root Causes:**

| Cause | Detection | Solution |
|-------|-----------|----------|
| **Table grew beyond threshold** | Broadcast size exceeded 10 MB default | Increase threshold or disable |
| **Table grew beyond driver memory** | Driver OOM during broadcast | Switch to shuffle join |
| **Network timeout** | Broadcast timeout error | Increase timeout or split |
| **Serialization failure** | Stack trace shows serialization | Check data types for nulls |

```python
# Check broadcast size
small_df.cache()
print(f"Size: {small_df.count()} rows")
# Estimate: rows * avg_row_size

# Solution 1: Increase threshold (if table is still reasonable)
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "100m")  # 100 MB

# Solution 2: Increase broadcast timeout
spark.conf.set("spark.sql.broadcastTimeout", "600")  # 10 minutes

# Solution 3: Disable broadcast, use shuffle join
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
# Or explicitly:
result = large_df.join(small_df.hint("shuffle"), "key")

# Solution 4: Monitor table sizes with alerts
```

---

### Q9: Efficient join between two large datasets

```python
# STRATEGY 1: Filter first, join less data
# DON'T: Join everything then filter
# DO: Filter each side before joining

df1_filtered = df1.filter(col("date") == target_date).select("key", "value1")
df2_filtered = df2.filter(col("active") == True).select("key", "value2")
result = df1_filtered.join(df2_filtered, "key")

# STRATEGY 2: Repartition on join key before join
partitions = 400  # Adjust based on data size
df1 = df1.repartition(partitions, "key")
df2 = df2.repartition(partitions, "key")
result = df1.join(df2, "key")

# STRATEGY 3: Bucketing for repeated joins
# Pre-compute once, reuse forever
df1.write.bucketBy(200, "key").sortBy("key").saveAsTable("orders_bucketed")
df2.write.bucketBy(200, "key").sortBy("key").saveAsTable("customers_bucketed")

# Future joins are shuffle-free
orders = spark.table("orders_bucketed")
customers = spark.table("customers_bucketed")
result = orders.join(customers, "key")  # No shuffle!

# STRATEGY 4: Bloom filter join (Spark 3.3+)
spark.conf.set("spark.sql.optimizer.runtime.bloomFilter.enabled", "true")
```

---

## 3️⃣ Partitioning & Shuffle (Q10-14)

### Q10: Repartition vs Coalesce — real use cases

| Operation | Shuffle | Use Case | Parallelism |
|-----------|---------|----------|-------------|
| `repartition(n)` | Yes | Increase partitions, redistribute evenly | Increases |
| `repartition(cols)` | Yes | Partition by column for joins | Varies |
| `coalesce(n)` | No | Decrease partitions before write | Decreases |

```python
# REPARTITION: After filter reduced data significantly
df_filtered = df.filter(col("status") == "ACTIVE")  # 1M → 10K rows
# Now have many empty partitions, redistribute
df_balanced = df_filtered.repartition(10)

# REPARTITION BY COLUMN: Before join
orders = orders.repartition(100, "customer_id")
customers = customers.repartition(100, "customer_id")
# Same keys now on same partitions

# COALESCE: Before writing files
df.coalesce(10).write.parquet("/output/")
# Creates 10 output files instead of 200

# ANTI-PATTERN: Using coalesce to increase partitions
df.coalesce(1000)  # WON'T WORK! Can only decrease
# Use repartition instead
```

---

### Q11: Repartitioned by date but queries still slow

**Root Causes:**

```python
# Problem: Repartition in Spark != Physical partitioning on disk

# What you did:
df.repartition("date").write.parquet("/output/")  # Just affects file layout

# What you should do:
df.write.partitionBy("date").parquet("/output/")  # Creates /output/date=2024-02-07/

# Check: Query with partition filter
spark.read.parquet("/output/").filter(col("date") == "2024-02-07")
# With partitionBy: Only reads one directory
# Without partitionBy: Reads all files
```

**Other Causes:**

| Issue | Check | Solution |
|-------|-------|----------|
| **Wrong partition column** | Query filters differ from partition | Match partition to query pattern |
| **Too many partitions** | 10K+ partitions with small files | Coarser granularity (monthly) |
| **Too few partitions** | Large files (> 1 GB) | Finer granularity (daily) |
| **Metadata overhead** | Many small files | Compaction |

---

### Q12: What causes shuffle explosion?

**Shuffle Explosion:** Output shuffle size >> input size

```python
# CAUSE 1: Exploding array/struct columns
df.select(explode("array_column"))  # 1 row → N rows

# CAUSE 2: Cross join (Cartesian product)
df1.crossJoin(df2)  # 1M × 1M = 1 trillion rows!

# CAUSE 3: Wrong join condition
df1.join(df2, df1.id == df2.id)  # Correct
df1.join(df2)  # CROSS JOIN! No condition

# CAUSE 4: groupBy without filter
df.groupBy("low_cardinality_column").agg(collect_list("data"))
# All data for one key ends up on one executor

# CAUSE 5: Window functions on large partitions
Window.partitionBy("skewed_key").orderBy("timestamp")
# All data for skewed key to one executor
```

**Prevention:**

```python
# Check shuffle size in Spark UI
# Stage → Shuffle Write/Read should be reasonable

# Filter before operations that shuffle
df.filter(col("date") >= "2024-01-01").groupBy("region").count()

# Use broadcast to avoid shuffle
large_df.join(broadcast(small_df), "key")
```

---

### Q13: How to decide number of partitions

**Rule of Thumb:**
```
Target: 100-200 MB per partition for processing
Formula: Total Data Size (MB) / 128 MB = Number of Partitions
```

```python
# READING: Let Spark decide (mostly)
spark.conf.set("spark.sql.files.maxPartitionBytes", "128m")  # Default
df = spark.read.parquet("/data/")  # Auto-partitioned

# SHUFFLE: Adjust based on data volume
data_size_gb = 100  # Estimate
target_partition_mb = 200
shuffle_partitions = int(data_size_gb * 1024 / target_partition_mb)
spark.conf.set("spark.sql.shuffle.partitions", shuffle_partitions)

# WRITING: Fewer large files preferred
target_file_mb = 256
output_size_gb = 50
num_output_files = int(output_size_gb * 1024 / target_file_mb)
df.coalesce(num_output_files).write.parquet("/output/")

# ADAPTIVE (Spark 3.0+): Let Spark optimize
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
```

---

### Q14: When does increasing partitions make performance worse?

**Cases Where More Partitions Hurt:**

| Scenario | Why | Solution |
|----------|-----|----------|
| **Overhead dominates** | Task scheduling > processing time | Fewer, larger partitions |
| **Small data** | 100 partitions for 100 MB → 1 MB each | Match parallelism to data |
| **Write amplification** | 10K partitions = 10K small files | Coalesce before write |
| **Network congestion** | Too many shuffle blocks | Reduce partitions |
| **Driver bottleneck** | Track 1M+ tasks | Keep < 100K tasks |

```python
# ANTI-PATTERN: Over-partitioning
df = spark.read.parquet("/small_data/")  # 100 MB
df.repartition(1000).groupBy("key").count()
# 1000 partitions × 100 KB each = Scheduling overhead!

# BETTER:
df.repartition(10).groupBy("key").count()
# 10 partitions × 10 MB each = Efficient

# Monitor: Spark UI → Stages
# If median task time < 100ms, you have too many partitions
```

---

## 4️⃣ Caching & Persistence (Q15-18)

### Q15: When should you cache a DataFrame?

**Cache When:**
1. DataFrame is used **multiple times**
2. DataFrame is **expensive to compute** (joins, aggregations)
3. You have **sufficient memory**

```python
# GOOD: Used multiple times
df_transformed = df.join(...).groupBy(...).agg(...)
df_transformed.cache()

result1 = df_transformed.filter(col("region") == "US")
result2 = df_transformed.filter(col("region") == "EU")
result3 = df_transformed.agg(sum("value"))

# After use:
df_transformed.unpersist()

# BAD: Used once
df.cache()
df.write.parquet("/output/")  # Only one action, cache is wasted

# BAD: Linear pipeline (no reuse)
df.cache()
df.filter(...).select(...).write.parquet(...)
# Each transformation creates new DataFrame, cache unused
```

---

### Q16: Caching increased memory but not speed

**Root Causes:**

| Issue | Explanation | Fix |
|-------|-------------|-----|
| **Cache not materialized** | Only actions trigger cache | Call `.count()` after cache |
| **No reuse** | Cached but used only once | Remove cache |
| **New DataFrame created** | Transformation after cache | Cache the final DataFrame |
| **Partial cache** | Not all partitions fit | Use MEMORY_AND_DISK |
| **Serialization overhead** | MEMORY_ONLY_SER slower to read | Use MEMORY_ONLY |

```python
# Problem: Cache never used
df.cache()
df.filter(col("x") > 0).write.parquet(...)  # This is a new DataFrame!

# Solution: Cache final DataFrame
df_filtered = df.filter(col("x") > 0)
df_filtered.cache()
df_filtered.count()  # Materialize cache
df_filtered.write.parquet(...)  # Uses cache

# Check if cache is being used: Spark UI → Storage tab
```

---

### Q17: Difference between storage levels

| Level | Where | Serialized | Copies | Use Case |
|-------|-------|------------|--------|----------|
| `MEMORY_ONLY` | RAM | No | 1 | Default, fast read |
| `MEMORY_ONLY_SER` | RAM | Yes | 1 | Memory pressure |
| `MEMORY_AND_DISK` | RAM + Disk | No | 1 | Large data |
| `MEMORY_AND_DISK_SER` | RAM + Disk | Yes | 1 | Very large data |
| `DISK_ONLY` | Disk | Yes | 1 | Huge data |
| `MEMORY_ONLY_2` | RAM | No | 2 | Fault tolerance |

```python
from pyspark import StorageLevel

# Default (MEMORY_AND_DISK for DataFrames)
df.cache()

# Explicit level
df.persist(StorageLevel.MEMORY_ONLY)
df.persist(StorageLevel.MEMORY_AND_DISK_SER)
df.persist(StorageLevel.DISK_ONLY)

# Choosing:
# - MEMORY_ONLY: Enough RAM, need speed
# - MEMORY_AND_DISK: Not enough RAM, acceptable disk access
# - MEMORY_ONLY_SER: Memory pressure, can tolerate deserialization cost
# - DISK_ONLY: Cache is huge, RAM for processing
```

---

### Q18: How to verify cache is being used

```python
# Method 1: Spark UI → Storage tab
# Shows cached DataFrames, size, % cached

# Method 2: Check execution plan
df.cache()
df.count()  # Materialize
df.explain()
# Look for "InMemoryTableScan" or "InMemoryRelation"

# Method 3: Check storage info programmatically
df.cache()
df.count()
print(df.storageLevel)  # Disk Memory Deserialized 1x Replicated

# Method 4: Compare execution times
import time

df.cache()
start = time.time()
df.count()  # First action: computes AND caches
print(f"First: {time.time() - start:.2f}s")

start = time.time()
df.count()  # Second action: uses cache
print(f"Second: {time.time() - start:.2f}s")  # Should be much faster
```

---

## 5️⃣ Fault Tolerance & Reliability (Q19-22)

### Q19: What happens when an executor dies mid-job?

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  SPARK FAULT TOLERANCE                                       │
└─────────────────────────────────────────────────────────────────────────────┘

1. EXECUTOR DIES (OOM, spot termination, node failure)
           │
           ▼
2. DRIVER DETECTS (heartbeat timeout)
           │
           ▼
3. TASKS RESCHEDULED
   ├── Running tasks → Restarted on other executors
   └── Completed tasks → Results lost if not checkpointed
           │
           ▼
4. RECOMPUTATION
   ├── Spark traces RDD lineage (DAG)
   └── Recomputes from last available data (shuffle files, source)
           │
           ▼
5. CLUSTER MANAGER (YARN/K8s)
   └── May launch replacement executor (if resources available)
```

```python
# Best practices for fault tolerance:

# 1. Checkpoint long lineages
spark.sparkContext.setCheckpointDir("/checkpoints")
df.checkpoint()  # Breaks lineage, saves to disk

# 2. Enable speculation for slow tasks
spark.conf.set("spark.speculation", "true")
spark.conf.set("spark.speculation.multiplier", "1.5")

# 3. Handle spot instance termination gracefully
# - Use checkpointing
# - Keep shuffle files on persistent storage
# - Allow retries
spark.conf.set("spark.task.maxFailures", "4")
```

---

### Q20: Job fails at 95% completion — make it restartable

```python
# STRATEGY 1: Checkpoint by partition
def process_with_checkpoint(partition_values, output_path, checkpoint_path):
    """Process partitions with restart capability"""
    
    # Load already processed partitions
    try:
        completed = spark.read.json(checkpoint_path).select("partition").collect()
        completed_set = {row.partition for row in completed}
    except:
        completed_set = set()
    
    for partition_value in partition_values:
        if partition_value in completed_set:
            print(f"Skipping {partition_value} (already done)")
            continue
        
        try:
            # Process partition
            df = spark.read.parquet(f"/input/date={partition_value}")
            result = df.transform(process_logic)
            result.write.mode("overwrite").parquet(f"{output_path}/date={partition_value}")
            
            # Mark as completed
            spark.createDataFrame([(partition_value,)], ["partition"]) \
                .write.mode("append").json(checkpoint_path)
                
        except Exception as e:
            print(f"Failed {partition_value}: {e}")
            # Continue to next partition, log failure
            continue

# STRATEGY 2: Use Delta Lake transaction log
# Delta automatically tracks which files were written
df.write \
    .format("delta") \
    .partitionBy("date") \
    .mode("overwrite") \
    .save("/output/")
# If job fails and restarts, Delta knows what was committed

# STRATEGY 3: Two-phase commit pattern
# Phase 1: Write to staging
result.write.parquet("/staging/output/")
# Phase 2: Atomic move
spark.sql("ALTER TABLE production EXCHANGE PARTITION (...) WITH TABLE staging")
```

---

### Q21: How does Spark handle recomputation?

```python
# LAZY EVALUATION + LINEAGE = AUTOMATIC RECOMPUTATION

# Lineage graph (DAG):
# read("/data") → filter(x > 0) → map(transform) → groupBy(key) → agg(sum)

# If task fails during groupBy:
# 1. Spark checks lineage graph
# 2. Finds last materialized point (shuffle files from previous stage)
# 3. Recomputes only from that point

# LONG LINEAGE PROBLEM:
# If lineage is very long (100+ transformations):
# - Recomputation is expensive
# - Stack overflow risk

# SOLUTION: Checkpoint
df_step_50 = df.transform(step1_to_50)
df_step_50.checkpoint()  # Breaks lineage here
df_step_50.count()  # Materialize checkpoint

df_final = df_step_50.transform(step51_to_100)
# If step 75 fails, only recompute from checkpoint, not from start
```

---

### Q22: Design idempotent Spark pipelines

```python
# IDEMPOTENT: Running N times = same result as running once

# PATTERN 1: Partition Overwrite
# Replace entire partition, don't append
df.write \
    .mode("overwrite") \
    .partitionBy("date") \
    .option("replaceWhere", f"date = '{processing_date}'") \
    .format("delta") \
    .save("/output/")

# PATTERN 2: MERGE (upsert)
from delta.tables import DeltaTable

deltaTable = DeltaTable.forPath(spark, "/output/")
deltaTable.alias("target").merge(
    new_data.alias("source"),
    "target.id = source.id"
).whenMatchedUpdateAll() \
 .whenNotMatchedInsertAll() \
 .execute()

# PATTERN 3: Delete-then-Insert
spark.sql(f"DELETE FROM output WHERE date = '{processing_date}'")
df.write.mode("append").saveAsTable("output")

# ANTI-PATTERN (NOT idempotent)
df.write.mode("append").parquet("/output/")  # Creates duplicates on retry
```

---

## 6️⃣ File Formats & Storage (Q23-26)

### Q23: Parquet vs ORC vs CSV — when and why?

| Format | Compression | Schema | Column Pruning | Best For |
|--------|-------------|--------|----------------|----------|
| **Parquet** | Excellent | Embedded | Yes | General analytics |
| **ORC** | Excellent | Embedded | Yes | Hive ecosystem |
| **CSV** | Poor | None | No | Interchange, legacy |
| **Avro** | Good | Embedded | No | Streaming, row-based |
| **JSON** | Poor | Schema-on-read | Partial | Flexibility, APIs |

```python
# PARQUET: Default for analytics
df.write.parquet("/output/")

# ORC: If using Hive heavily
df.write.format("orc").save("/output/")

# CSV: Only for data exchange
df.write.option("header", "true").csv("/output/")

# AVRO: For Kafka, row-based operations
df.write.format("avro").save("/output/")

# RECOMMENDATION: Almost always use Parquet
# - Native to Spark
# - Best compression
# - Column pruning
# - Predicate pushdown
```

---

### Q24: Why does Parquet improve performance?

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PARQUET PERFORMANCE ADVANTAGES                            │
└─────────────────────────────────────────────────────────────────────────────┘

1. COLUMNAR STORAGE
   Row-based: [id, name, age] [id, name, age] [id, name, age]
   Columnar:  [id, id, id] [name, name, name] [age, age, age]
   
   Query: SELECT name FROM ...
   Row: Must read entire row
   Column: Only read 'name' column → 90% less I/O

2. COMPRESSION
   Similar values in column compress well
   [US, US, US, US, CA, CA] → very compressible
   10x smaller than CSV

3. PREDICATE PUSHDOWN
   Parquet stores min/max per row group
   Query: WHERE age > 30
   Row groups with max(age) < 30 are skipped entirely

4. SCHEMA EVOLUTION
   Schema embedded in file
   New columns can be added
   Old files still readable
```

---

### Q25: Optimize read performance for time-based queries

```python
# STRATEGY 1: Partition by date
df.write \
    .partitionBy("year", "month", "day") \
    .parquet("/data/events/")

# Query benefits from partition pruning
df = spark.read.parquet("/data/events/") \
    .filter((col("year") == 2024) & (col("month") == 2) & (col("day") == 7))
# Only reads /data/events/year=2024/month=2/day=7/

# STRATEGY 2: Z-ordering (Delta Lake)
# Colocate related time ranges
from delta.tables import DeltaTable
deltaTable = DeltaTable.forPath(spark, "/data/events/")
deltaTable.optimize().executeZOrderBy("timestamp")

# STRATEGY 3: Bucketing by time ranges
df.write \
    .bucketBy(96, "hour_of_day")  # 24 hours × 4 quarters \
    .sortBy("timestamp") \
    .saveAsTable("events_bucketed")

# STRATEGY 4: Bloom filters (Spark 3.3+)
spark.conf.set("spark.sql.parquet.bloomFilter.enabled", "true")
df.write \
    .option("parquet.bloom.filter.enabled#timestamp", "true") \
    .parquet("/data/events/")
```

---

### Q26: Schema changes in Parquet files

```python
# SCENARIO: New column added to source, existing files don't have it

# BEHAVIOR: Spark reads NULL for missing columns (if mergeSchema enabled)
df = spark.read \
    .option("mergeSchema", "true") \
    .parquet("/data/")

# SCHEMA EVOLUTION RULES:
# ✅ SAFE: Add new nullable column
# ✅ SAFE: Widen numeric type (INT → LONG)
# ⚠️ CAUTION: Rename column (old files won't match)
# ❌ BREAKING: Remove column (old files have extra data)
# ❌ BREAKING: Change type incompatibly (STRING → INT)

# DELTA LAKE: Built-in schema evolution
df.write \
    .option("mergeSchema", "true") \
    .format("delta") \
    .mode("append") \
    .save("/delta/data/")

# ENFORCEMENT:
spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", "true")
```

---

## 7️⃣ Streaming (Q27-30)

### Q27: Handling late-arriving events in Structured Streaming

```python
# WATERMARKING: Tell Spark how late data can arrive
from pyspark.sql.functions import window

windowed_counts = (
    events_stream
    .withWatermark("event_time", "10 minutes")  # Accept 10 min late
    .groupBy(
        window("event_time", "5 minutes"),
        "event_type"
    )
    .count()
)

# Events arriving > 10 minutes late are DROPPED
# Events within watermark are included in aggregation

# TUNING WATERMARK:
# Too short: Drops legitimate late data
# Too long: Holds state longer, uses more memory
```

---

### Q28: Exactly-once vs At-least-once semantics

| Semantic | Guarantee | Complexity | Performance |
|----------|-----------|------------|-------------|
| **At-most-once** | May lose data | Simple | Fast |
| **At-least-once** | May duplicate | Medium | Good |
| **Exactly-once** | No loss, no dups | Complex | Slower |

```python
# AT-LEAST-ONCE (default)
# Spark retries failed tasks → may process twice
# Consumer must handle duplicates

# EXACTLY-ONCE (end-to-end)
# Requires: Idempotent sink OR transactional sink

# Delta Lake: Transactional writes
query = (
    stream_df
    .writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/checkpoints/my_stream")
    .start("/delta/output/")
)

# Kafka: Idempotent producer
spark.conf.set("spark.sql.streaming.kafka.producer.idempotent", "true")
```

---

### Q29: Watermarking — what problem does it solve?

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WATERMARKING IN STREAMING                                 │
└─────────────────────────────────────────────────────────────────────────────┘

PROBLEM: Unbounded state growth

Without watermark:
- Event at 10:00 arrives
- Window [10:00-10:05] created
- State held forever (waiting for late data)
- Memory grows infinitely!

WITH WATERMARK:
- Watermark = "10 minutes"
- Current event time: 10:30
- Watermark position: 10:20
- Windows before 10:20 are FINALIZED and state CLEARED
```

```python
# Watermark = max(event_time) - threshold
# Events with event_time < watermark are dropped

stream = spark.readStream.format("kafka").load()

result = (
    stream
    .withWatermark("event_time", "30 minutes")  # Allow 30 min late
    .groupBy(
        window("event_time", "1 hour"),
        "user_id"
    )
    .agg(count("*").alias("events"))
)

# After 1 hour 30 min, the 10:00 window is finalized
# State for 10:00-11:00 window is cleared from memory
```

---

### Q30: Streaming job down for 2 hours — what happens?

```python
# SCENARIO: Streaming job crashes at 10:00, restarts at 12:00

# IF USING KAFKA + CHECKPOINTING:
# 1. Checkpoint stores last processed Kafka offset
# 2. On restart, Spark reads checkpoint
# 3. Resumes from last offset (10:00)
# 4. Processes 2 hours of backlog

# CONSIDERATIONS:
# - Kafka retention must be > 2 hours
# - Backlog processing may spike resources
# - Late data handling still applies

query = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("subscribe", "events")
    .option("startingOffsets", "earliest")  # On first run
    # On restart, uses checkpoint
    .load()
    .writeStream
    .format("delta")
    .option("checkpointLocation", "/checkpoints/events")
    .start()
)

# BACKLOG HANDLING:
# Option 1: Auto-scale compute during catchup
# Option 2: Rate limiting
query = (
    stream
    .writeStream
    .trigger(processingTime="1 second")
    .option("maxOffsetsPerTrigger", 100000)  # Limit per batch
    .start()
)

# Option 3: Skip old data
# startingOffsets: "latest" (loses 2 hours of data!)
```
