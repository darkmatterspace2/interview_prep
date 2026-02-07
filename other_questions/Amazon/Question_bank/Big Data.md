# Big Data / Distributed Systems Interview Questions & Answers (Question Bank 1)

> **Amazon Data Engineer Style** - Spark/Distributed Concepts & Optimization

---

## 1️⃣ Spark / Distributed Concepts

### Q76: What causes data skew?

**Definition:** Uneven distribution of data across partitions, causing some tasks to take much longer than others.

**Common Causes:**

| Cause | Example | Solution |
|-------|---------|----------|
| **Skewed Key** | 90% of orders from "Amazon" customer | Salt the key |
| **Null Values** | Many records with NULL join key | Handle nulls separately |
| **Hot Partition** | All events for "Black Friday" in one partition | Range-based partitioning |
| **Bad Hash** | Low cardinality (only 3 status values) | Increase partitions, composite key |

```python
# Detecting skew
df.groupBy("join_key").count().orderBy(F.desc("count")).show(10)

# Solution 1: Salting
from pyspark.sql.functions import expr, concat, lit
SALT_BUCKETS = 10

# Salt the large table
large_df = large_df.withColumn("salt", (F.rand() * SALT_BUCKETS).cast("int"))
large_df = large_df.withColumn("salted_key", concat(col("join_key"), lit("_"), col("salt")))

# Explode the small table (replicate for each salt)
small_df = small_df.crossJoin(spark.range(SALT_BUCKETS).withColumnRenamed("id", "salt"))
small_df = small_df.withColumn("salted_key", concat(col("join_key"), lit("_"), col("salt")))

# Join on salted key
result = large_df.join(small_df, "salted_key")

# Solution 2: Broadcast small table
result = large_df.join(broadcast(small_df), "join_key")
```

---

### Q77: Wide vs narrow transformations

| Type | Definition | Shuffle | Examples |
|------|------------|---------|----------|
| **Narrow** | Each input partition → one output partition | No | `map`, `filter`, `select`, `withColumn` |
| **Wide** | Input partitions → multiple output partitions | Yes | `groupBy`, `join`, `orderBy`, `repartition` |

```
NARROW (No Shuffle):                WIDE (Shuffle Required):
┌────────┐    ┌────────┐            ┌────────┐    ┌────────┐
│ Part 1 │───▶│ Part 1 │            │ Part 1 │───▶│ Part A │
└────────┘    └────────┘            └────────┘  ╱ └────────┘
                                               ╳
┌────────┐    ┌────────┐            ┌────────┐  ╲ ┌────────┐
│ Part 2 │───▶│ Part 2 │            │ Part 2 │───▶│ Part B │
└────────┘    └────────┘            └────────┘    └────────┘

Example: filter(col > 5)            Example: groupBy("region").count()
```

**Key Points:**
- Minimize wide transformations (each one = shuffle = network I/O)
- Chain narrow transformations (Spark optimizes them together)
- Pre-filter before joins/aggregations

---

### Q78: Why joins are expensive?

**Cost Factors:**

| Factor | Impact | Mitigation |
|--------|--------|------------|
| **Data Shuffle** | Both tables redistributed across network | Broadcast small table |
| **Disk Spill** | Memory overflow causes disk I/O | Increase memory, fewer partitions |
| **Data Skew** | One partition has disproportionate data | Salting, adaptive query execution |
| **Cartesian Product** | Missing/wrong join condition | Always verify join keys |

```python
# Most expensive: Shuffle both tables
large_df.join(medium_df, "key")  # Both shuffle

# Better: Broadcast small table
large_df.join(broadcast(small_df), "key")  # Only large shuffles

# Best: Pre-partitioned on join key
large_df.repartition("key").write.bucketBy(100, "key").saveAsTable("large_bucketed")
medium_df.repartition("key").write.bucketBy(100, "key").saveAsTable("medium_bucketed")
# Future joins: no shuffle!
```

---

### Q79: Shuffle — what and why?

**What:** Redistribution of data across partitions/nodes based on a key.

**When:** Required for operations that need all values for a key together:
- `groupBy` / `reduceByKey`
- `join` (sort-merge or shuffle-hash)
- `orderBy` / `sortBy`
- `repartition`

**Why Expensive:**
1. Serialize data on source nodes
2. Transfer over network
3. Deserialize on target nodes
4. May spill to disk if memory insufficient

```python
# Visualize shuffle
df.explain()  # Look for "Exchange" in plan

# Example plan:
# == Physical Plan ==
# HashAggregate (final aggregate)
# +- Exchange hashpartitioning(region)  ← SHUFFLE HERE
#    +- HashAggregate (partial aggregate)
#       +- Scan parquet

# Reduce shuffle size
df.select("key", "value").groupBy("key").sum("value")  # Select only needed columns
```

---

### Q80: Partitioning vs bucketing

| Aspect | Partitioning | Bucketing |
|--------|--------------|-----------|
| **Cardinality** | Low (date, region) | High (customer_id, order_id) |
| **Files Created** | One directory per value | Fixed number of buckets |
| **Query Benefit** | Partition pruning | Join optimization |
| **When Read** | Skips entire directories | Must read, but pre-sorted |

```python
# Partitioning: Good for date-based queries
df.write \
    .partitionBy("year", "month") \
    .parquet("/data/events/")
# /data/events/year=2024/month=01/
# /data/events/year=2024/month=02/

# Query automatically prunes:
spark.read.parquet("/data/events/").filter("year = 2024 AND month = 1")
# Only reads year=2024/month=01 directory

# Bucketing: Good for frequent joins
df.write \
    .bucketBy(100, "customer_id") \
    .sortBy("customer_id") \
    .saveAsTable("events_bucketed")

# Join without shuffle:
orders = spark.table("orders_bucketed")  # Also bucketed by customer_id
customers = spark.table("customers_bucketed")
result = orders.join(customers, "customer_id")  # No shuffle!
```

---

## 2️⃣ Optimization

### Q81: How to optimize large joins?

```python
# STRATEGY 1: Broadcast small table (< 10-100 MB)
from pyspark.sql.functions import broadcast
result = large_df.join(broadcast(small_df), "key")

# Check broadcast threshold
spark.conf.get("spark.sql.autoBroadcastJoinThreshold")  # Default 10MB
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "100m")

# STRATEGY 2: Pre-filter before join
# ❌ Bad: Join everything, then filter
result = orders.join(customers, "customer_id").filter(year == 2024)

# ✅ Good: Filter first, then join
orders_2024 = orders.filter(year == 2024)
result = orders_2024.join(customers, "customer_id")

# STRATEGY 3: Bucketing for repeated joins
# See Q80 for bucketing example

# STRATEGY 4: Adaptive Query Execution (Spark 3.0+)
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")

# STRATEGY 5: Salting for skewed keys (See Q76)
```

---

### Q82: Broadcast join — when?

**Use Broadcast When:**
- Small table fits in memory (< ~100-500 MB)
- Joining large table with lookup/dimension table
- One-sided join (only large table needs to be scanned)

**Don't Use When:**
- Both tables are large
- Memory is constrained
- Broadcasting repeatedly (reuse cached tables)

```python
# Explicit broadcast
from pyspark.sql.functions import broadcast

# Force broadcast regardless of size
result = shipments.join(broadcast(carriers), "carrier_id")

# Verify broadcast in explain plan
result.explain()
# Look for "BroadcastHashJoin" or "BroadcastExchange"

# Check actual broadcast size
spark.sparkContext.broadcast(small_df.collect())  # Creates broadcast variable

# Tune threshold
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "200m")  # 200 MB
```

---

### Q83: Repartition vs coalesce

| Operation | Shuffle | Use Case |
|-----------|---------|----------|
| `repartition(n)` | Yes (full) | Increase partitions, redistribute evenly |
| `repartition(col)` | Yes | Partition by column (for join optimization) |
| `coalesce(n)` | No (narrow) | Decrease partitions only |

```python
# Repartition: INCREASE or REDISTRIBUTE
# Use when: Need more parallelism or even distribution
df = spark.read.csv("data/").repartition(200)  # Increase partitions
df = df.repartition("region")  # Partition by column

# Coalesce: DECREASE without shuffle
# Use when: Writing output, reducing file count
df = df.filter(condition)  # After filter, may have empty partitions
df.coalesce(10).write.parquet("output/")  # Reduce to 10 partitions

# ❌ Don't use coalesce to increase partitions (no effect or skew)
df.coalesce(1000)  # Won't increase beyond current count

# Repartition by column for join optimization
orders = orders.repartition("customer_id")
customers = customers.repartition("customer_id")
# Now same keys are on same partition
```

---

### Q84: File size optimization

**Target File Size:** 128 MB - 1 GB (optimal for HDFS/S3)

```python
# Problem: Too many small files (slow reads, metadata overhead)
# Problem: Too few large files (can't parallelize)

# SOLUTION 1: Coalesce before write
file_size_mb = 256
total_size_mb = estimate_dataframe_size(df)
target_partitions = max(1, int(total_size_mb / file_size_mb))

df.coalesce(target_partitions).write.parquet("output/")

# SOLUTION 2: maxRecordsPerFile
df.write \
    .option("maxRecordsPerFile", 1000000) \
    .parquet("output/")

# SOLUTION 3: Delta Lake optimize
from delta.tables import DeltaTable
deltaTable = DeltaTable.forPath(spark, "/delta/events")
deltaTable.optimize().executeCompaction()

# SOLUTION 4: Spark adaptive coalescing
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.advisoryPartitionSizeInBytes", "256m")
```

---

### Q85: Handling small files problem

**Symptoms:**
- Slow reads (too many S3/HDFS requests)
- Long planning time (reading metadata)
- Memory pressure on driver (file list)

**Solutions:**

```python
# 1. Compact on write
df.repartition(100).write.parquet("output/")  # Fixed partition count

# 2. Periodic compaction job
def compact_small_files(path, target_size_mb=256):
    df = spark.read.parquet(path)
    current_count = df.rdd.getNumPartitions()
    total_size = get_directory_size(path)
    
    target_partitions = max(1, int(total_size / target_size_mb))
    
    if current_count > target_partitions * 2:  # Only compact if worth it
        df.coalesce(target_partitions).write.mode("overwrite").parquet(f"{path}_compacted")
        # Atomic swap
        rename(path, f"{path}_old")
        rename(f"{path}_compacted", path)
        delete(f"{path}_old")

# 3. Delta Lake OPTIMIZE
spark.sql("OPTIMIZE delta.`/path/to/table`")

# 4. Auto-compaction (Delta Lake)
spark.conf.set("spark.databricks.delta.autoCompact.enabled", "true")
spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")

# 5. Input file merging (read optimization)
spark.conf.set("spark.sql.files.maxPartitionBytes", "256m")
spark.conf.set("spark.sql.files.openCostInBytes", "8m")
```

---

## 3️⃣ Advanced Spark (Part 2 Questions)

### RDD vs DataFrame vs Dataset

| Aspect | RDD | DataFrame | Dataset |
|--------|-----|-----------|---------|
| **Type Safety** | Yes (compile-time) | No (runtime) | Yes (compile-time) |
| **Optimization** | None (manual) | Catalyst optimizer | Catalyst optimizer |
| **Schema** | No fixed schema | Schema required | Schema required |
| **API** | Functional (map, filter) | SQL-like | Hybrid |
| **Performance** | Slowest | Fast | Fast |
| **When to Use** | Custom partitioning, unstructured | SQL operations, interop | Type safety + optimization |

```python
# RDD: Low-level, no optimization
rdd = sc.textFile("data.txt")
rdd.map(lambda x: x.split(",")).filter(lambda x: x[0] > 100)

# DataFrame: Optimized, schema-aware (Python/SQL)
df = spark.read.csv("data.txt", schema="id INT, name STRING")
df.filter(col("id") > 100).select("name")

# Dataset: Type-safe (Scala/Java only)
case class Event(id: Int, name: String)
val ds = spark.read.csv("data.txt").as[Event]
ds.filter(_.id > 100).map(_.name)

# When to use RDD:
# - Need fine-grained control over partitioning
# - Working with unstructured data
# - Using third-party libraries that return RDDs
```

### Troubleshooting OutOfMemoryError

```python
# 1. IDENTIFY WHERE (Driver vs Executor)
# Driver OOM: collect(), broadcast, driver logs
# Executor OOM: Task failures, GC logs

# 2. SOLUTIONS FOR DRIVER OOM
# ❌ Avoid: df.collect(), df.toPandas() on large data
# ✅ Use: df.show(100), df.take(100), df.write

# If broadcast needed, increase driver memory:
spark.conf.set("spark.driver.memory", "8g")

# 3. SOLUTIONS FOR EXECUTOR OOM
# Increase memory
spark.conf.set("spark.executor.memory", "16g")
spark.conf.set("spark.executor.memoryOverhead", "4g")  # Off-heap

# Reduce parallelism (less memory per task)
spark.conf.set("spark.sql.shuffle.partitions", "400")  # Up from default 200

# Spill to disk instead of OOM
spark.conf.set("spark.memory.fraction", "0.6")  # Reduce Spark managed memory

# 4. CHECK FOR SKEW
df.groupBy("key").count().orderBy(desc("count")).show()
# If one key has 10x data, use salting

# 5. REDUCE DATA SIZE
# Filter early
df = df.filter(year == 2024).select("needed_columns")

# Use columnar format
df.write.parquet("output/")  # Not CSV
```

### Spark Fault Tolerance (DAG and Lazy Evaluation)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SPARK FAULT TOLERANCE                                │
└─────────────────────────────────────────────────────────────────────────────┘

1. LINEAGE GRAPH (DAG)
   Spark records how each RDD/DataFrame was derived:
   
   textFile → map → filter → groupBy → collect
        ↓        ↓       ↓        ↓
      RDD1    RDD2    RDD3     RDD4
   
   If RDD3 partition fails → Spark recomputes from RDD2 (not from scratch)

2. LAZY EVALUATION
   Transformations are NOT executed immediately
   Only when ACTION is called (collect, write, count)
   
   df = spark.read.parquet(...)  # Nothing happens
   df2 = df.filter(...)          # Still nothing
   df3 = df2.groupBy(...)        # Still nothing
   df3.count()                   # NOW everything executes

3. CHECKPOINTING
   For very long lineages, save intermediate results:
   
   spark.sparkContext.setCheckpointDir("/checkpoints")
   df.checkpoint()  # Breaks lineage, saves to disk
   
   Now if failure occurs: Restart from checkpoint, not beginning

4. SPECULATIVE EXECUTION
   spark.conf.set("spark.speculation", "true")
   If task is slow, Spark starts duplicate on another executor
   First to finish wins
```

### Why Parquet over CSV

| Aspect | Parquet | CSV |
|--------|---------|-----|
| **Format** | Columnar, binary | Row-based, text |
| **Compression** | Excellent (10-50x) | Poor |
| **Schema** | Embedded + enforced | None |
| **Query Speed** | Column pruning | Read entire row |
| **Splittable** | Yes (row groups) | Only if uncompressed |
| **Write Speed** | Slower (encoding) | Fast |

```python
# Query: SELECT name, age FROM users WHERE age > 30

# CSV: Must read entire 100 columns, parse text
df = spark.read.csv("users.csv")  # Read all data
df.filter(col("age") > 30).select("name", "age")  # Then filter

# Parquet: Reads only 2 columns, binary comparison
df = spark.read.parquet("users.parquet")  # Predicate pushdown
df.filter(col("age") > 30).select("name", "age")  # Reads only name, age columns

# Storage comparison (100GB CSV)
# CSV: ~100 GB
# Parquet: ~10-20 GB (with Snappy compression)
# Parquet + Zstd: ~5-10 GB

# Best practices
df.write \
    .option("compression", "snappy") \  # Fast compression
    .partitionBy("year", "month") \     # Query optimization
    .parquet("output/")
```

---

# Question Bank 2: Cluster Sizing & Capacity Planning

> **Amazon Data Engineer Style** - Hardware Decisions, Memory Planning, Cost Trade-offs

---

## 4️⃣ Cluster Sizing Fundamentals (Q31-34)

### Q31: Estimate cluster size for 1 TB/day

**Sizing Framework:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CLUSTER SIZING CALCULATION                                │
└─────────────────────────────────────────────────────────────────────────────┘

INPUTS:
• Raw data: 1 TB/day
• SLA: 2 hours processing window
• Processing: Parse JSON, join with dim tables, aggregate

STEP 1: ESTIMATE DATA EXPANSION
  Raw → Parsed: 1x (same size after compression)
  After join: 1.5x (denormalization)
  Peak in-memory: 1 TB × 1.5 × 3 (working copies) = 4.5 TB

STEP 2: MEMORY REQUIREMENTS
  Processing: 4.5 TB / 2 hours = 2.25 TB in parallel
  Safety margin: 2.25 × 1.5 = ~3.5 TB cluster memory

STEP 3: EXECUTOR SIZING
  Executor memory: 16 GB (reasonable)
  Executors needed: 3500 GB / 16 GB = ~220 executors
  Cores per executor: 4-5
  Total cores: 220 × 4 = 880 cores

STEP 4: NODE SELECTION
  Instance: r5.4xlarge (16 cores, 128 GB RAM)
  Executors per node: 128 / 16 = 8 executors
  Nodes needed: 220 / 8 = ~28 nodes

RECOMMENDATION: 
  30 × r5.4xlarge (with headroom)
  Or: 60 × r5.2xlarge (smaller, more parallelism)
```

---

### Q32: Data expansion impact on sizing

| Stage | Data Size | Expansion Factor | Example |
|-------|-----------|------------------|---------|
| **Raw** | 100 GB | 1x | Compressed JSON |
| **Parsed** | 100 GB | 1x | Parquet (similar compression) |
| **Joined** | 150 GB | 1.5x | Denormalized |
| **In-Memory (Shuffle)** | 300+ GB | 3x | Serialized + spill space |
| **Aggregated** | 10 GB | 0.1x | Final summary |

```python
# Memory planning per operation
# Rule: Peak memory = largest intermediate dataset × 2-3x

# Example: Join two 500 GB tables
peak_memory = 500 + 500 + (500 * 1.5)  # Both inputs + output
# = 1.75 TB peak memory needed

# With overhead:
cluster_memory = peak_memory * 2  # 3.5 TB
```

---

### Q33: Factors deciding Nodes vs RAM vs CPU

| Factor | Impact | How to Decide |
|--------|--------|---------------|
| **Data Volume** | More data → more memory | 2-3x peak dataset size |
| **Shuffle Intensity** | Joins, groupBy → more memory + network | Add 50% for shuffle |
| **SLA** | Tighter SLA → more parallelism | More cores |
| **Complexity** | UDFs, ML → more CPU | Higher core count |
| **Spot Tolerance** | Can handle retry → use cheaper instances | Smaller, more nodes |

**Decision Tree:**
```
Is job memory-bound (OOM, spill)?
├── YES → Increase RAM per node
└── NO
    └── Is job slow due to parallelism?
        ├── YES → More cores / nodes
        └── NO → Check network (shuffle) or I/O (storage)
```

---

### Q34: Many small nodes vs few large nodes

| Approach | Pros | Cons | Use Case |
|----------|------|------|----------|
| **Many Small** (50×r5.2xlarge) | Better fault tolerance, Spot-friendly | Network overhead, shuffle cost | Stateless ETL |
| **Few Large** (10×r5.8xlarge) | Less shuffle, simpler network | Single node failure = bigger impact | Memory-heavy ML |

```python
# RULE OF THUMB:
# 1. Many small nodes: High parallelism, shuffle-light workloads
# 2. Few large nodes: Shuffle-heavy, broadcast joins, ML training

# AWS EMR Task Node calculation
# Small cluster: 10 × r5.2xlarge = 80 cores, 640 GB RAM
# Large cluster: 5 × r5.4xlarge = 80 cores, 640 GB RAM
# Same total resources, but large nodes = less network hops
```

---

## 5️⃣ Memory & Executor Planning (Q35-39)

### Q35: Calculate executor memory

```python
# FORMULA (YARN-based):
# Container Memory = spark.executor.memory + spark.executor.memoryOverhead

# Example: r5.4xlarge node (128 GB RAM, 16 cores)
# Reserve for OS: 10%
# Available: 128 × 0.9 = ~115 GB

# Executors per node: 3-4 (leave cores for HDFS, shuffle service)
# Memory per executor: 115 / 4 = ~28 GB

# Configuration:
spark.executor.memory = "24g"
spark.executor.memoryOverhead = "4g"  # 10% or 384MB min
spark.executor.cores = 4

# VERIFY:
# Container size: 24 + 4 = 28 GB
# Total per node: 28 × 4 = 112 GB ✓ (< 115 GB available)
```

---

### Q36: More memory can make jobs slower — why?

**Reasons:**

| Issue | Why It Happens | Solution |
|-------|----------------|----------|
| **GC Pressure** | Large heaps = long GC pauses | Smaller executors, more of them |
| **Fewer Executors** | 2×64GB vs 8×16GB = less parallelism | Balance memory vs count |
| **Serialization** | Large objects take longer to serialize | Tune heap fractions |
| **Memory Bloat** | Unneeded caching uses RAM | Unpersist aggressively |

```python
# EXAMPLE: 128 GB node

# ❌ Bad: 1 large executor
spark.executor.memory = "100g"
spark.executor.cores = 16
# GC pauses can be 30+ seconds!

# ✅ Good: 4 medium executors
spark.executor.memory = "24g"
spark.executor.cores = 4
# Shorter GC, more parallelism
```

---

### Q37: Driver vs Executor memory — what runs where?

| Component | Driver | Executor |
|-----------|--------|----------|
| **Purpose** | Orchestration | Processing |
| **Operations** | collect(), broadcast, planning | map, filter, join, agg |
| **Memory Needs** | Small unless collecting | Large for data processing |
| **Failure Impact** | Job fails completely | Task retried elsewhere |

```python
# Driver OOM causes:
df.collect()  # Pulls all data to driver
spark.sparkContext.broadcast(large_table)  # Broadcasts from driver
df.toPandas()  # Materializes on driver

# Driver memory sizing:
# Default: 1-4 GB
# With broadcast: RAM for largest broadcast table + 2 GB
# With collect: Don't do this on large data

spark.conf.set("spark.driver.memory", "8g")
spark.conf.set("spark.driver.maxResultSize", "4g")
```

---

### Q38: Executor memory too small — what happens?

**Symptoms:**

1. **Task failures** with OOM
2. **Excessive spill** to disk (slow)
3. **GC thrashing** (100% time in GC)
4. **Shuffle fetch failures** (can't hold shuffle blocks)

```python
# Check Spark UI:
# - Executors tab → GC Time (should be < 10%)
# - Tasks tab → Spill (Memory) vs Spill (Disk)

# Solutions in order:
# 1. Increase partitions (less data per task)
spark.conf.set("spark.sql.shuffle.partitions", "400")

# 2. Increase executor memory
spark.conf.set("spark.executor.memory", "24g")

# 3. Add memory overhead for off-heap
spark.conf.set("spark.executor.memoryOverhead", "4g")

# 4. Reduce parallelism per executor
spark.conf.set("spark.executor.cores", "3")  # Less concurrent tasks
```

---

### Q39: How many executors per node?

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EXECUTOR PLANNING                                         │
└─────────────────────────────────────────────────────────────────────────────┘

NODE: r5.4xlarge (16 cores, 128 GB RAM)

RESERVE:
  • 1 core for YARN NodeManager
  • 1 core for DataNode / shuffle service
  • 10 GB for OS

AVAILABLE: 14 cores, 118 GB

EXECUTOR SIZING:
  • 5 cores / executor (sweet spot for HDFS I/O)
  • Executors = 14 / 5 = 2-3 executors
  • Memory = 118 / 3 = ~39 GB each
  • After overhead (10%): 35 GB heap + 4 GB overhead

CONFIGURATION:
  spark.executor.instances = (nodes × 3) - 1  # Reserve 1 for AM
  spark.executor.cores = 5
  spark.executor.memory = 35g
  spark.executor.memoryOverhead = 4g
```

---

## 6️⃣ CPU & Parallelism (Q40-43)

### Q40: Ideal cores per executor

**Recommendation: 4-5 cores per executor**

| Cores | Pros | Cons |
|-------|------|------|
| **1-2** | Lower memory per task | Under-utilizes multi-threading |
| **4-5** | Balanced parallelism/memory | Good default |
| **8+** | Less executor overhead | HDFS throughput bottleneck |

```python
# Why not more cores?
# HDFS has limited concurrent reads per JVM
# More than 5 cores = threads compete for I/O

# AWS EMR recommended:
# spark.executor.cores = 5
# spark.executor.memory = (node_memory / (node_cores / 5)) - overhead

# Databricks:
# Autotunes based on workload
```

---

### Q41: CPU-bound vs IO-bound jobs

| Type | Symptom | Diagnosis | Solution |
|------|---------|-----------|----------|
| **CPU-bound** | High CPU, low I/O wait | Complex UDFs, parsing, ML | More cores |
| **IO-bound** | Low CPU, high I/O wait | Large scans, heavy shuffle | Faster storage, more nodes |
| **Memory-bound** | GC thrashing, spill | Large joins, aggregations | More memory |
| **Network-bound** | Shuffle fetch timeout | Cross-rack shuffle | Better network, less shuffle |

```python
# DIAGNOSIS: Check executor metrics in Spark UI
# CPU-bound: Task CPU time ≈ Duration
# IO-bound: Task CPU time << Duration

# CPU-bound optimization:
# - Vectorized UDFs
# - Use built-in functions instead of UDFs
# - Avoid Python UDFs (use Pandas UDFs)

# IO-bound optimization:
# - Columnar format (Parquet)
# - Predicate pushdown
# - Partition pruning
# - Local SSD for shuffle
```

---

### Q42: spark.sql.shuffle.partitions impact

```python
# DEFAULT: 200 partitions

# TOO FEW (< data size / 200 MB):
# - Large partitions
# - OOM risk
# - Under-parallelized

# TOO MANY (> 10000):
# - Scheduling overhead
# - Small tasks (< 10 MB)
# - Driver memory pressure (tracking)

# RULE OF THUMB:
partitions = max(200, data_size_gb * 4)
# 100 GB → 400 partitions
# 1 TB → 4000 partitions

# ADAPTIVE (Spark 3.0+):
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
# Spark auto-adjusts based on actual data size
```

---

### Q43: When does more parallelism stop helping?

**Diminishing Returns:**

| Scenario | Why Parallelism Doesn't Help |
|----------|------------------------------|
| **Skewed data** | 1 task has 90% data | Salt the key |
| **Small data** | 100 tasks × 1 MB each | Reduce partitions |
| **Singleton ops** | collect(), orderBy (global) | Can't parallelize |
| **Shared resource** | All tasks hit same DB | Parallelize I/O source |
| **Network saturation** | Shuffle limited by bandwidth | Better network or reduce shuffle |

```python
# How to detect:
# Spark UI → Stages → Look at task distribution
# If min/median/max times are wildly different → skew
# If all tasks are < 100ms → too many partitions

# Monitor: Total cores vs Active tasks
# If active tasks << total cores → bottleneck elsewhere
```

---

## 7️⃣ Network & IO Considerations (Q44-47)

### Q44: Why network bandwidth matters

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NETWORK IN SPARK                                          │
└─────────────────────────────────────────────────────────────────────────────┘

SHUFFLE = NETWORK-INTENSIVE

Example: 100 GB shuffle across 20 nodes
• Each node sends 5 GB to every other node
• Total network: 100 GB × 20 = 2 TB wire traffic
• At 10 Gbps: 2 TB / 1.25 GB/s = 27 minutes just for transfer!

WHERE IT MATTERS:
1. Shuffle (groupBy, join, repartition)
2. Broadcast (sending to all executors)
3. Reading from remote storage (S3, HDFS)
```

---

### Q45: Shuffle stress on network and disk

```python
# Shuffle phases:
# 1. Map side: Write shuffle files to local disk
# 2. Transfer: Send shuffle blocks over network
# 3. Reduce side: Fetch and merge shuffle blocks

# DISK STRESS:
# - Shuffle files written before transfer
# - If memory insufficient, spill to disk
# - SSD preferred over HDD

# NETWORK STRESS:
# - All-to-all communication
# - Can saturate network links
# - Cross-rack is expensive

# MITIGATION:
spark.conf.set("spark.shuffle.compress", "true")  # Compress shuffle
spark.conf.set("spark.shuffle.spill.compress", "true")  # Compress spill
spark.conf.set("spark.reducer.maxSizeInFlight", "96m")  # Buffer size
```

---

### Q46: Local SSD vs Remote Storage

| Aspect | Local SSD | Remote (S3/HDFS) |
|--------|-----------|------------------|
| **Latency** | ~0.1 ms | ~10-100 ms |
| **Throughput** | 500+ MB/s | 100-200 MB/s |
| **Durability** | Lost on termination | Persistent |
| **Cost** | Included in instance | Per GB stored/transferred |

```python
# RECOMMENDATIONS:
# 1. Shuffle: Use local SSD (much faster)
spark.conf.set("spark.local.dir", "/mnt/ssd")

# 2. Input/Output: Remote (S3/ADLS) for persistence
df = spark.read.parquet("s3://bucket/data/")

# 3. Intermediate: Local SSD if reused
df.persist(StorageLevel.DISK_ONLY)

# AWS instance with NVMe: i3, r5d, c5d families
# Azure: Lsv2 (storage optimized)
```

---

### Q47: Compression — CPU vs IO trade-off

| Codec | Compression | CPU | Speed | Use When |
|-------|-------------|-----|-------|----------|
| **None** | 1x | None | Fastest | Already compressed, CPU-bound |
| **Snappy** | 2-3x | Low | Fast | Default, balanced |
| **LZ4** | 2-3x | Low | Very fast | Shuffle, streaming |
| **Zstd** | 5-10x | Medium | Medium | Archival, cold storage |
| **Gzip** | 5-10x | High | Slow | One-time export |

```python
# Choose based on bottleneck:
# IO-bound (slow storage): Higher compression (Zstd)
# CPU-bound: Lower compression (Snappy/LZ4)

# Parquet default: Snappy
df.write.option("compression", "snappy").parquet("out/")

# For archival:
df.write.option("compression", "zstd").parquet("archive/")

# For shuffle (internal):
spark.conf.set("spark.io.compression.codec", "lz4")
```

---

## 8️⃣ Cost Optimization (Q48-50)

### Q48: Reduce cost without breaking SLAs

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COST OPTIMIZATION STRATEGIES                              │
└─────────────────────────────────────────────────────────────────────────────┘

1. RIGHT-SIZE CLUSTER (First step always)
   • Monitor utilization: CPU, memory, I/O
   • If avg utilization < 50%, reduce nodes

2. USE SPOT INSTANCES (50-90% savings)
   • Good for: Batch jobs, fault-tolerant pipelines
   • Bad for: Streaming, tight SLAs
   • Design: Checkpointing, retry logic

3. AUTO-SCALING
   • Scale up during peak, scale down otherwise
   • EMR: Core nodes fixed, Task nodes auto-scale

4. OPTIMIZE CODE FIRST
   • Filter early, select less
   • Broadcast joins
   • Better partitioning

5. SCHEDULE WISELY
   • Run during off-peak (lower spot prices)
   • Batch multiple jobs together
```

```python
# Cost comparison example:
# Before: 20 × r5.2xlarge On-Demand × 24/7
#   = 20 × $0.504/hr × 730 hr = $7,358/month

# After: 
# - Optimized code (runs in 4 hours instead of 8)
# - 50% Spot instances
# - Auto-scaling (only 8 hours/day)
#   = 10 × $0.504 × 240 + 10 × $0.15 × 240
#   = $1,210 + $360 = $1,570/month (79% savings!)
```

---

### Q49: Spot vs On-Demand trade-offs

| Aspect | Spot | On-Demand | Reserved |
|--------|------|-----------|----------|
| **Discount** | 60-90% | 0% | 30-60% |
| **Reliability** | Can be terminated | Guaranteed | Guaranteed |
| **Use Case** | Fault-tolerant batch | Critical, streaming | Steady baseline |

```python
# SPOT BEST PRACTICES:
# 1. Diversify instance types (spot capacity)
# 2. Use multiple AZs
# 3. Enable Spark checkpointing
# 4. Set up graceful decommissioning

# EMR configuration:
# - Core nodes: On-Demand (for HDFS)
# - Task nodes: Spot (stateless, replaceable)

# Databricks:
# - Driver: On-Demand
# - Workers: Spot with fallback to On-Demand
```

---

### Q50: Auto-scaling vs Fixed clusters

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| **Fixed** | Predictable cost, no cold start | Idle waste | Streaming, steady load |
| **Auto-scaling** | Cost follows demand | Cold start delay | Variable batch loads |
| **Serverless** | Pay per use, no management | Higher $/compute | Sporadic workloads |

```yaml
# Auto-scaling Strategy:

Peak Hours (6 AM - 6 PM):
  Min nodes: 10
  Max nodes: 50
  Scale out: CPU > 70% for 5 min
  Scale in: CPU < 40% for 15 min

Off-peak (6 PM - 6 AM):
  Min nodes: 2
  Max nodes: 20

# EMR Managed Scaling:
aws emr modify-cluster --cluster-id j-xxx \
  --managed-scaling-policy '{
    "ComputeLimits": {
      "MinimumCapacityUnits": 10,
      "MaximumCapacityUnits": 100,
      "UnitType": "InstanceFleetUnits"
    }
  }'
```

---

## 9️⃣ Real-World Sizing Scenarios (Q51-54)

### Q51: 500 GB batch job, SLA = 2 hours

```python
# APPROACH:

# 1. Start with baseline estimate
data_size = 500  # GB
sla_hours = 2
target_throughput = data_size / sla_hours  # 250 GB/hour

# 2. Benchmark on sample
# Run with 10 nodes × 16 cores on 50 GB sample
# Sample time: 30 min → 100 GB/hour per 10 nodes
# Need: 250 / 100 × 10 = 25 nodes

# 3. Add headroom for variability
nodes = 25 * 1.3  # 30% buffer
# Recommendation: 32 nodes

# 4. Configuration
spark.conf.set("spark.executor.instances", 100)  # ~3 per node
spark.conf.set("spark.executor.memory", "24g")
spark.conf.set("spark.executor.cores", 5)
spark.conf.set("spark.sql.shuffle.partitions", 2000)  # 500GB × 4

# 5. Monitor and adjust
# Track actual vs SLA, scale if needed
```

---

### Q52: ETL runs 6 hours instead of 2 — debug vs scale?

**Debug First (usually):**

```python
# 1. CHECK SPARK UI FOR OBVIOUS ISSUES
# - One stage taking 80% of time?
# - Skewed tasks (1 task = 30 min, rest = 30 sec)?
# - Excessive shuffle/spill?

# 2. IDENTIFY BOTTLENECK
# - CPU bound: All cores at 100%
# - Memory bound: GC > 20%, spill to disk
# - I/O bound: Low CPU, waiting on reads
# - Shuffle bound: Shuffle read/write taking time

# 3. COMMON FIXES (no scaling needed)
# - Broadcast small tables (eliminate shuffle)
# - Filter earlier (less data to process)
# - Better partition column (partition pruning)
# - Fix skew (salting)

# 4. IF TRULY RESOURCE-LIMITED
# - Increase parallelism (more executors/partitions)
# - Add memory (if OOM/spill)
# - Move to larger instances (if network limited)

# RULE: 80% of performance issues are code, not resources
```

---

### Q53: Team A wants more memory, Team B wants more nodes

**Decision Framework:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RESOURCE CONTENTION DECISION                              │
└─────────────────────────────────────────────────────────────────────────────┘

ANALYZE WORKLOADS:

Team A (ML Training):
  • Large model fits in memory
  • Benefits from large executors
  • Lower parallelism OK
  → Needs LARGER MEMORY per node

Team B (ETL):
  • Many independent transformations
  • Benefits from parallelism
  • Standard memory sufficient
  → Needs MORE NODES

SOLUTIONS:

1. HETEROGENEOUS CLUSTER
   • Different instance pools
   • Job requests specific pool

2. SEPARATE CLUSTERS
   • Team A: 10 × r5.8xlarge (256 GB)
   • Team B: 30 × r5.2xlarge (64 GB)

3. TIME-BASED SHARING
   • Team A runs overnight (uses full cluster)
   • Team B runs daytime (parallel)

4. COST ALLOCATION
   • Each team budgets own resources
   • Use serverless for fairness (pay per use)
```

---

### Q54: Streaming job: 50K events/sec spikes to 200K

```python
# HEADROOM PLANNING:

baseline = 50_000  # events/sec
peak = 200_000     # events/sec
spike_factor = peak / baseline  # 4x

# 1. SIZE FOR BASELINE + BUFFER
# Process 50K/s with 50% headroom
baseline_capacity = 50_000 * 1.5  # 75K/s steady state

# 2. AUTO-SCALING FOR PEAKS
# Scale out when throughput approaches capacity
# Trigger: Input rate > 70% capacity for 2 min
# Scale in: Input rate < 40% capacity for 10 min

# 3. CONFIGURATION
# Kafka consumer parallelism = partitions
# Ensure partitions >= peak_parallelism_needed

# Example calculation:
processing_per_core = 5000  # events/sec (benchmark this!)
cores_for_peak = 200_000 / 5000  # 40 cores minimum
# With 4 cores/executor: 10 executors minimum at peak

# 4. BACKPRESSURE HANDLING
spark.conf.set("spark.streaming.backpressure.enabled", "true")
spark.conf.set("spark.streaming.kafka.maxRatePerPartition", "10000")
```

---

## 🔟 Failure & Edge Cases (Q55-59)

### Q55: One node much slower (straggler)

```python
# SYMPTOMS:
# - Spark UI: Most tasks done, waiting on a few
# - One node consistently slow across jobs

# CAUSES:
# 1. Hardware degradation (disk, network)
# 2. Noisy neighbor (shared resources)
# 3. Data skew landing on that node
# 4. Hot spot in storage

# SOLUTIONS:
# 1. Enable speculation
spark.conf.set("spark.speculation", "true")
spark.conf.set("spark.speculation.multiplier", "1.5")
spark.conf.set("spark.speculation.quantile", "0.75")
# If task takes 1.5x median time, launch speculative copy

# 2. Blacklist bad node
spark.conf.set("spark.blacklist.enabled", "true")
spark.conf.set("spark.blacklist.task.maxTaskAttemptsPerNode", "2")

# 3. Replace instance (cloud)
# Terminate and let auto-scaling replace
```

---

### Q56: Speculative execution — how it helps

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SPECULATIVE EXECUTION                                     │
└─────────────────────────────────────────────────────────────────────────────┘

WITHOUT SPECULATION:
  Task 1: ███░░ 2 min
  Task 2: ███░░ 2 min
  Task 3: ██████████████████ 10 min (slow node)
  Task 4: ███░░ 2 min
  TOTAL: 10 min (waiting for slowest)

WITH SPECULATION:
  Task 1: ███░░ 2 min
  Task 2: ███░░ 2 min
  Task 3: ██████████... (original)
  Task 3': ███░░ 2 min (speculative copy, finishes first!)
  Task 4: ███░░ 2 min
  TOTAL: 2 min (speculative copy won)
```

```python
# Enable:
spark.conf.set("spark.speculation", "true")
spark.conf.set("spark.speculation.interval", "100ms")  # Check frequency
spark.conf.set("spark.speculation.multiplier", "1.5")  # Launch if 1.5x median
spark.conf.set("spark.speculation.quantile", "0.75")   # After 75% tasks done

# CAUTION:
# - Don't use with non-idempotent operations (external writes)
# - Wastes some compute (duplicate work)
```

---

### Q57: Sizing clusters for backfills

```python
# SCENARIO: Need to reprocess 90 days of data (usually process 1 day)

# APPROACH 1: Parallel daily runs
# - Spin up 10x normal cluster
# - Run 10 days in parallel
# - 9 batches to complete 90 days

# APPROACH 2: Larger single run
# - Read all 90 days at once
# - Requires 90x memory? No! Stream through
# - But shuffles are 90x larger

# APPROACH 3: Incremental backfill (recommended)
# - Run backfill during off-hours
# - Process 5 days per night
# - 18 nights to complete
# - No extra cluster needed

# CONFIGURATION FOR LARGE BACKFILL:
# 1. Increase shuffle partitions
spark.conf.set("spark.sql.shuffle.partitions", 4000)  # vs normal 200

# 2. More aggressive spill settings
spark.conf.set("spark.memory.fraction", "0.8")  # More for execution

# 3. Checkpoint intermediate results
df_halfway.write.parquet("/checkpoint/halfway/")
```

---

### Q58: GC tuning impact

```python
# GC SYMPTOMS:
# - Spark UI → Executors → GC Time > 10% of task time
# - Full GC pauses (seconds)
# - "GC overhead limit exceeded"

# G1GC TUNING (Default for Spark 3.0+):
# In spark-defaults.conf or --conf:
--conf spark.executor.extraJavaOptions="-XX:+UseG1GC -XX:InitiatingHeapOccupancyPercent=35 -XX:G1HeapRegionSize=16m"

# GENERAL RULES:
# 1. Smaller heaps GC faster (< 32 GB optimal)
# 2. More executors with smaller heaps > fewer with large heaps
# 3. Off-heap for serialization reduces GC pressure

# MONITOR:
# - GC logs: -XX:+PrintGCDetails -XX:+PrintGCTimeStamps
# - Spark UI: Executor tab → GC Time column

# REDUCE GC PRESSURE:
# - Cache less (only if reused)
# - Use MEMORY_ONLY_SER (smaller footprint)
# - Off-heap caching (Spark 2.3+)
spark.conf.set("spark.memory.offHeap.enabled", "true")
spark.conf.set("spark.memory.offHeap.size", "8g")
```

---

### Q59: Detect underutilized clusters

```python
# METRICS TO MONITOR:

# 1. CPU Utilization
# - Avg < 30%: Cluster too large
# - Avg 60-80%: Well-sized
# - Avg > 90%: May need more

# 2. Memory Utilization
# - JVM heap used / allocated
# - Watch for unused cached data

# 3. Scheduler Delay
# - Time waiting for resources
# - High delay = not enough resources

# 4. Executor Idle Time
# - Time executors have no tasks
# - High idle = too many executors

# CLOUDWATCH / GANGLIA METRICS:
# - YARNMemoryAvailablePercentage
# - ContainerPendingRatio
# - AppsRunning vs AppsCompleted

# ACTION:
# If avg utilization < 40% over a week:
# - Reduce cluster by 30%
# - Add auto-scaling to handle peaks
```

---

## 🔸 Trade-off & Design Judgment (Q60-63)

### Q60: Scale up vs Scale out

| Strategy | When to Use | Pros | Cons |
|----------|-------------|------|------|
| **Scale Up** (bigger instances) | Memory-bound, GC issues | Less network, simpler | Single point of failure |
| **Scale Out** (more instances) | CPU-bound, parallelizable | Fault tolerant, flexible | More network, shuffle cost |

```python
# EXAMPLE:
# Current: 10 × r5.4xlarge (16 cores, 128 GB each)

# SCALE UP: 5 × r5.8xlarge (32 cores, 256 GB each)
# Good if: Large joins cause OOM, need bigger broadcast

# SCALE OUT: 20 × r5.2xlarge (8 cores, 64 GB each)
# Good if: Need more parallelism, want spot tolerance
```

---

### Q61: When is Spark not the right tool?

| Scenario | Better Alternative |
|----------|-------------------|
| **< 1 GB data** | Pandas, DuckDB |
| **Simple SQL** | Athena, Presto |
| **Sub-second latency** | Druid, ClickHouse |
| **True streaming (event-at-a-time)** | Flink |
| **Graph processing** | GraphX, Neo4j |
| **Small frequent jobs** | Lambda, serverless |

---

### Q62: Explain cluster sizing to non-technical stakeholders

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STAKEHOLDER-FRIENDLY EXPLANATION                          │
└─────────────────────────────────────────────────────────────────────────────┘

"Think of our data processing like a factory assembly line:

📦 DATA = Raw materials (1 TB of orders per day)
🏭 CLUSTER = Factory floor (servers)
👷 EXECUTORS = Workers (each can handle a portion)
⏱️ SLA = Delivery deadline (must finish by 6 AM)

We need enough workers to:
1. Unpack all materials (read data)
2. Process them (transform, join)
3. Package for delivery (write output)

If we add more workers:
  ✅ Faster processing
  ❌ Higher cost ($500/worker/month)

If we reduce workers:
  ✅ Lower cost
  ❌ May miss deadline

Our recommendation: 30 workers
  • Meets 2-hour deadline with 30% buffer
  • Handles growth for 6 months
  • Cost: $15,000/month
"
```

---

### Q63: Performance vs Cost balance

```python
# FRAMEWORK: Define acceptable trade-offs

# TIER 1: Critical path (revenue impacting)
# - SLA: MUST meet
# - Cost: Secondary concern
# - Strategy: On-Demand, over-provision 50%

# TIER 2: Important but flexible
# - SLA: Soft deadline, can slip 1-2 hours
# - Cost: Optimize
# - Strategy: Auto-scaling, 30% Spot

# TIER 3: Best effort
# - SLA: Complete within day
# - Cost: Minimize
# - Strategy: 90% Spot, run during off-peak

# IMPLEMENTATION:
tier_1_jobs = ["revenue_dashboard", "customer_orders"]
tier_2_jobs = ["user_analytics", "inventory_sync"]
tier_3_jobs = ["historical_backfill", "ad_hoc_analysis"]

def get_cluster_config(job_name):
    if job_name in tier_1_jobs:
        return {"spot_percentage": 0, "autoscale": False, "buffer": 1.5}
    elif job_name in tier_2_jobs:
        return {"spot_percentage": 50, "autoscale": True, "buffer": 1.2}
    else:
        return {"spot_percentage": 90, "autoscale": True, "buffer": 1.0}
```
