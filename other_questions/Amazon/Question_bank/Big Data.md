# Big Data / Distributed Systems Interview Questions & Answers (Question Bank 1)

> **Amazon Data Engineer Style** - Spark/Distributed Concepts & Optimization

---

<a id="index"></a>
## 📑 Table of Contents

| Section | Topics |
|---------|--------|
| [1️⃣ Spark / Distributed Concepts](#1️⃣-spark--distributed-concepts) | Skew, transformations, joins, shuffle |
| &nbsp;&nbsp;&nbsp;└ [Q76: Data skew](#q76-what-causes-data-skew) | Causes & solutions |
| &nbsp;&nbsp;&nbsp;└ [Q77: Wide vs narrow transformations](#q77-wide-vs-narrow-transformations) | Shuffle implications |
| &nbsp;&nbsp;&nbsp;└ [Q78: Why joins are expensive](#q78-why-joins-are-expensive) | Cost factors |
| &nbsp;&nbsp;&nbsp;└ [Q79: Shuffle](#q79-shuffle--what-and-why) | What, when, why |
| &nbsp;&nbsp;&nbsp;└ [Q80: Partitioning vs bucketing](#q80-partitioning-vs-bucketing) | When to use |
| [2️⃣ Optimization](#2️⃣-optimization) | Joins, broadcast, file size |
| &nbsp;&nbsp;&nbsp;└ [Q81: Optimize large joins](#q81-how-to-optimize-large-joins) | Strategies |
| &nbsp;&nbsp;&nbsp;└ [Q82: Broadcast join](#q82-broadcast-join--when) | When to use |
| &nbsp;&nbsp;&nbsp;└ [Q83: Repartition vs coalesce](#q83-repartition-vs-coalesce) | Differences |
| &nbsp;&nbsp;&nbsp;└ [Q84: File size optimization](#q84-file-size-optimization) | Target sizes |
| &nbsp;&nbsp;&nbsp;└ [Q85: Small files problem](#q85-handling-small-files-problem) | Solutions |
| [3️⃣ Advanced Spark](#3️⃣-advanced-spark-part-2-questions) | RDD vs DataFrame, OOM, fault tolerance |
| [4️⃣ Cluster Sizing Fundamentals](#4️⃣-cluster-sizing-fundamentals-q31-34) | Q31-34: Estimation |
| [5️⃣ Memory & Executor Planning](#5️⃣-memory--executor-planning-q35-39) | Q35-39: Memory config |
| [6️⃣ CPU & Parallelism](#6️⃣-cpu--parallelism-q40-43) | Q40-43: Cores, partitions |
| [7️⃣ Network & IO](#7️⃣-network--io-considerations-q44-47) | Q44-47: Bandwidth, compression |
| [8️⃣ Cost Optimization](#8️⃣-cost-optimization-q48-50) | Q48-50: Spot, auto-scaling |
| [9️⃣ Real-World Sizing](#9️⃣-real-world-sizing-scenarios-q51-54) | Q51-54: Scenarios |
| [🔟 Failure & Edge Cases](#-failure--edge-cases-q55-59) | Q55-59: Stragglers, backfills |
| [🔸 Trade-off & Design](#-trade-off--design-judgment-q60-63) | Q60-63: Judgment |

---

<a id="1️⃣-spark--distributed-concepts"></a>
## 1️⃣ Spark / Distributed Concepts [↩️](#index)

<a id="q76-what-causes-data-skew"></a>
### Q76: What causes data skew? [↩️](#index)

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

<a id="q77-wide-vs-narrow-transformations"></a>
### Q77: Wide vs narrow transformations [↩️](#index)

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

<a id="q78-why-joins-are-expensive"></a>
### Q78: Why joins are expensive? [↩️](#index)

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

<a id="q79-shuffle--what-and-why"></a>
### Q79: Shuffle — what and why? [↩️](#index)

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

<a id="q80-partitioning-vs-bucketing"></a>
### Q80: Partitioning vs bucketing [↩️](#index)

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

<a id="2️⃣-optimization"></a>
## 2️⃣ Optimization [↩️](#index)

<a id="q81-how-to-optimize-large-joins"></a>
### Q81: How to optimize large joins? [↩️](#index)

```python
# STRATEGY 1: Broadcast small table (< 10-100 MB)
from pyspark.sql.functions import broadcast
result = large_df.join(broadcast(small_df), "key")

# STRATEGY 2: Pre-filter before join
orders_2024 = orders.filter(year == 2024)
result = orders_2024.join(customers, "customer_id")

# STRATEGY 3: Bucketing for repeated joins (See Q80)

# STRATEGY 4: Adaptive Query Execution (Spark 3.0+)
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")

# STRATEGY 5: Salting for skewed keys (See Q76)
```

---

<a id="q82-broadcast-join--when"></a>
### Q82: Broadcast join — when? [↩️](#index)

**Use Broadcast When:**
- Small table fits in memory (< ~100-500 MB)
- Joining large table with lookup/dimension table
- One-sided join (only large table needs to be scanned)

**Don't Use When:**
- Both tables are large
- Memory is constrained
- Broadcasting repeatedly (reuse cached tables)

```python
from pyspark.sql.functions import broadcast
result = shipments.join(broadcast(carriers), "carrier_id")

# Tune threshold
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "200m")  # 200 MB
```

---

<a id="q83-repartition-vs-coalesce"></a>
### Q83: Repartition vs coalesce [↩️](#index)

| Operation | Shuffle | Use Case |
|-----------|---------|----------|
| `repartition(n)` | Yes (full) | Increase partitions, redistribute evenly |
| `repartition(col)` | Yes | Partition by column (for join optimization) |
| `coalesce(n)` | No (narrow) | Decrease partitions only |

```python
# Repartition: INCREASE or REDISTRIBUTE
df = spark.read.csv("data/").repartition(200)

# Coalesce: DECREASE without shuffle (use when writing output)
df.coalesce(10).write.parquet("output/")
```

---

<a id="q84-file-size-optimization"></a>
### Q84: File size optimization [↩️](#index)

**Target File Size:** 128 MB - 1 GB (optimal for HDFS/S3)

```python
# SOLUTION 1: Coalesce before write
df.coalesce(target_partitions).write.parquet("output/")

# SOLUTION 2: maxRecordsPerFile
df.write.option("maxRecordsPerFile", 1000000).parquet("output/")

# SOLUTION 3: Delta Lake optimize
spark.sql("OPTIMIZE delta.`/path/to/table`")
```

---

<a id="q85-handling-small-files-problem"></a>
### Q85: Handling small files problem [↩️](#index)

**Solutions:**
```python
# 1. Compact on write
df.repartition(100).write.parquet("output/")

# 2. Delta Lake auto-compaction
spark.conf.set("spark.databricks.delta.autoCompact.enabled", "true")

# 3. Input file merging
spark.conf.set("spark.sql.files.maxPartitionBytes", "256m")
```

---

<a id="3️⃣-advanced-spark-part-2-questions"></a>
## 3️⃣ Advanced Spark (Part 2 Questions) [↩️](#index)

### RDD vs DataFrame vs Dataset [↩️](#index)

| Aspect | RDD | DataFrame | Dataset |
|--------|-----|-----------|---------||
| **Type Safety** | Yes | No | Yes |
| **Optimization** | None | Catalyst | Catalyst |
| **Performance** | Slowest | Fast | Fast |
| **When to Use** | Custom partitioning | SQL operations | Type safety + optimization |

### Troubleshooting OutOfMemoryError [↩️](#index)

```python
# Driver OOM: Avoid df.collect(), df.toPandas()
# Executor OOM: Increase partitions or memory
spark.conf.set("spark.sql.shuffle.partitions", "400")
spark.conf.set("spark.executor.memory", "24g")
```

### Why Parquet over CSV [↩️](#index)

| Aspect | Parquet | CSV |
|--------|---------|-----|
| **Compression** | 10-50x | Poor |
| **Column Pruning** | Yes | No |
| **Query Speed** | Fast | Slow |

---

<a id="4️⃣-cluster-sizing-fundamentals-q31-34"></a>
## 4️⃣ Cluster Sizing Fundamentals (Q31-34) [↩️](#index)

### Q31: Estimate cluster size for 1 TB/day [↩️](#index)

```
INPUTS: 1 TB/day, SLA: 2 hours
STEP 1: Peak in-memory: 1 TB × 1.5 × 3 = 4.5 TB
STEP 2: Cluster memory: ~3.5 TB (with safety margin)
STEP 3: 220 executors × 16 GB each
RECOMMENDATION: 30 × r5.4xlarge
```

### Q32-34: Data expansion, Nodes vs RAM vs CPU [↩️](#index)

- **Data expansion:** Raw → Parsed → Joined → In-Memory (3x)
- **Decision tree:** Memory-bound → more RAM; CPU-bound → more cores
- **Many small nodes:** Better fault tolerance, Spot-friendly
- **Few large nodes:** Less shuffle, better for ML

---

<a id="5️⃣-memory--executor-planning-q35-39"></a>
## 5️⃣ Memory & Executor Planning (Q35-39) [↩️](#index)

### Q35-39 Summary [↩️](#index)

| Question | Key Point |
|----------|-----------|
| **Q35** | Container = executor.memory + memoryOverhead |
| **Q36** | Large heaps = long GC pauses |
| **Q37** | Driver: orchestration; Executor: processing |
| **Q38** | Too small = OOM, spill, GC thrashing |
| **Q39** | 4-5 cores per executor optimal |

---

<a id="6️⃣-cpu--parallelism-q40-43"></a>
## 6️⃣ CPU & Parallelism (Q40-43) [↩️](#index)

### Q40-43 Summary [↩️](#index)

- **Q40:** 4-5 cores per executor (HDFS throughput limit)
- **Q41:** CPU-bound vs IO-bound vs Memory-bound diagnosis
- **Q42:** shuffle.partitions = max(200, data_size_gb × 4)
- **Q43:** Diminishing returns with skew or singleton ops

---

<a id="7️⃣-network--io-considerations-q44-47"></a>
## 7️⃣ Network & IO Considerations (Q44-47) [↩️](#index)

### Q44-47 Summary [↩️](#index)

- **Q44:** Shuffle = network-intensive (100 GB × 20 nodes = 2 TB wire traffic)
- **Q45:** Shuffle stresses both disk and network
- **Q46:** Local SSD for shuffle, remote for persistence
- **Q47:** Snappy (balanced), Zstd (archival), LZ4 (streaming)

---

<a id="8️⃣-cost-optimization-q48-50"></a>
## 8️⃣ Cost Optimization (Q48-50) [↩️](#index)

### Q48-50 Summary [↩️](#index)

1. **Right-size cluster** first
2. **Spot instances** for 50-90% savings
3. **Auto-scaling** for variable loads
4. **Optimize code** before scaling

---

<a id="9️⃣-real-world-sizing-scenarios-q51-54"></a>
## 9️⃣ Real-World Sizing Scenarios (Q51-54) [↩️](#index)

- **Q51:** 500 GB batch, 2h SLA → 32 nodes with 30% buffer
- **Q52:** 6h instead of 2h → Debug first (80% are code issues)
- **Q53:** Team A (memory) vs Team B (nodes) → Heterogeneous or separate clusters
- **Q54:** 50K→200K events/sec → Size for baseline + auto-scale for peaks

---

<a id="-failure--edge-cases-q55-59"></a>
## 🔟 Failure & Edge Cases (Q55-59) [↩️](#index)

- **Q55:** Stragglers → Enable speculation
- **Q56:** Speculative execution launches duplicate task
- **Q57:** Backfills → Incremental, increase shuffle partitions
- **Q58:** GC tuning → G1GC, smaller heaps
- **Q59:** Underutilized clusters → Monitor avg CPU < 40%

---

<a id="-trade-off--design-judgment-q60-63"></a>
## 🔸 Trade-off & Design Judgment (Q60-63) [↩️](#index)

### Q60: Scale up vs Scale out [↩️](#index)

| Strategy | When to Use |
|----------|-------------|
| **Scale Up** | Memory-bound, GC issues |
| **Scale Out** | CPU-bound, parallelizable |

### Q61: When Spark is NOT right [↩️](#index)

- < 1 GB data → Pandas, DuckDB
- Simple SQL → Athena, Presto  
- Sub-second latency → Druid, ClickHouse
- True streaming → Flink

### Q62-63: Stakeholder communication, Performance vs Cost [↩️](#index)

- **Tier 1 (Critical):** Over-provision 50%, On-Demand
- **Tier 2 (Important):** Auto-scaling, 30% Spot
- **Tier 3 (Best effort):** 90% Spot, off-peak
