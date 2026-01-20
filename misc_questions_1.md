# Miscellaneous PySpark Deep Dive
*Core Internals & Optimization*

Detailed explanations of Spark architecture components and data organization strategies.

---

## Table of Contents
1. [Spark Execution Flow](#spark-execution-flow)
2. [Catalyst Optimizer](#catalyst-optimizer)
3. [Transformations: Wide vs Narrow](#transformations-wide-vs-narrow)
4. [Optimization Features (Tungsten, PPD)](#optimization-features)
5. [Data Layout: Partitioning vs Bucketing](#data-layout-partitioning-vs-bucketing)
6. [SQL Concepts (Ranking, Window)](#sql-concepts-ranking-window)
7. [Python Concepts (Decorators, Structures)](#python-concepts-decorators-structures)
8. [Join Logic Scenarios](#join-logic-scenarios)
9. [Common Coding Scenarios (Empty DF, Sessionization)](#common-coding-scenarios-empty-df-sessionization)
10. [Azure & Databricks Integrations](#azure--databricks-integrations)
11. [Azure Data Factory Components](#azure-data-factory-components)

---

## Spark Execution Flow

### 1. Stages of Execution
**Q:** Explain the lifecycle of a Spark Application from code to execution.
**A:**
1.  **Driver Program:** The main entry point (`SparkSession`). It converts valid user code into a **Logical Plan**.
2.  **DAG Scheduler:**
    *   Converts the Logical Plan into a Physical Plan (using Catalyst).
    *   Breaks the graph of RDDs into **Stages**.
    *   Stages are determined by **Shuffle Boundaries** (Wide transformations like `groupBy` break the DAG into new stages).
3.  **Task Scheduler:**
    *   Breaks Stages into **Tasks**.
    *   A Task is the smallest unit of work (one task per partition).
    *   Submits TaskSets to the Cluster Manager (YARN/K8s).
4.  **Executor:**
    *   Receives tasks and executes them on the worker nodes.
    *   Reports status/results back to the Driver.

---

## Catalyst Optimizer

### 2. What is the Catalyst Optimizer?
**Q:** Describe the phases of the Catalyst Optimizer.
**A:**
The engine that optimizes DataFrames/Datasets/SQL.
1.  **Analysis:** Checks syntax and resolves references (e.g., checking if column `id` exists in table `users`) using the Catalog.
2.  **Logical Optimization:** Applies standard rule-based optimizations:
    *   *Predicate Pushdown* (Filter early).
    *   *Constant Folding* (e.g., convert `1 + 2` to `3`).
    *   *Projection Pruning* (Remove unused columns).
3.  **Physical Planning:** Generates multiple physical plans (strategies) to execute the logical plan (e.g., choosing `BroadcastHashJoin` vs `SortMergeJoin`). Is uses a **Cost Model** to check which strategy is cheapest.
4.  **Code Generation:** Generates optimized Java Bytecode to run on the executors.

---

## Transformations: Wide vs Narrow

### 3. Narrow vs Wide Transformations
**Q:** Difference between Narrow and Wide transformations?
**A:**
*   **Narrow Transformation:**
    *   *Definition:* Each partition of the parent RDD is used by at most one partition of the child RDD.
    *   *Shuffle:* No shuffle required. Data stays on the same node.
    *   *Examples:* `map`, `filter`, `union`, `select`.
    *   *Performance:* Fast, pipelined in memory.
*   **Wide Transformation:**
    *   *Definition:* Each partition of the parent RDD may be used by multiple partitions of the child RDD.
    *   *Shuffle:* **Requires Shuffle**. Data must be redistributed across the network.
    *   *Examples:* `groupBy`, `distinct`, `join` (except broadcast), `repartition`.
    *   *Performance:* Slower, breaks the stage boundary.

---

## Optimization Features

### 4. Predicate Pushdown (PPD)
**Q:** What is Predicate Pushdown?
**A:**
An optimization where filtering logic is "pushed down" to the database or file source, minimizing the amount of data transferred to Spark.
*   *Without PPD:* Read 1TB file -> Filter in Spark -> Result.
*   *With PPD:* Spark tells Parquet reader "Only give me rows where `date='2023-01-01'`". Source scans metadata/indices and returns only 10GB.
*   *Supported formats:* Parquet, ORC, JDBC sources.

### 5. Project Tungsten
**Q:** What is the goal of Project Tungsten?
**A:**
To optimize CPU and Memory efficiency (improving hardware utilization).
1.  **Memory Management (Off-Heap):** Manages memory explicitly (sun.misc.Unsafe) to avoid JVM Garbage Collection overhead.
2.  **Cache-aware Computation:** Designs algorithms to exploit L1/L2/L3 CPU caches.
3.  **Code Generation (Whole-Stage Codegen):** Collapses multiple operators (Filter -> Map -> Select) into a single optimized function (function fusing) to eliminate virtual function calls.

---

## Data Layout: Partitioning vs Bucketing

### 6. Partitioning vs Bucketing
**Q:** When to use Partitioning vs Bucketing?

| Feature | Partitioning (`partitionBy`) | Bucketing (`bucketBy`) |
|---------|------------------------------|------------------------|
| **Structure** | Creates sub-directories (`/year=2023/`) | Creates fixed number of files per directory |
| **Cardinality** | Best for **Low** cardinality (Year, Month, Country) | Best for **High** cardinality (User_ID, Product_ID) |
| **Use Case** | Optimizes Filters (`WHERE year=2023`) | Optimizes Joins (`ON user_id`) to avoid Shuffle |
| **Maintenance** | Easy to append new partitions | Harder (Must rewrite table to change # buckets) |

### 7. Types of Partitioning
**Q:** What are the partitioning strategies in Spark?
**A:**
1.  **Hash Partitioning (Default):**
    *   `partitionBy(col)` splits data based on `hash(col) % numPartitions`. ensures even distribution if data isn't skewed.
2.  **Range Partitioning:**
    *   Partitions based on sorted range of keys (e.g., A-F, G-M). Used in `sort` operations. Good for range queries.
3.  **Round Robin Partitioning:**
    *   Distributes data simply to equalize partition size. No guarantee that keys end up together. Used in `repartition()` without columns.

---

## SQL Concepts (Ranking, Window)

### 8. Rank, Dense Rank, Row Number
**Q:** Explain the difference with data `[10, 20, 20, 30]`.
**A:**
*   **ROW_NUMBER():** Unique sequential number.
    *   `1, 2, 3, 4`
*   **RANK():** Same rank for ties, skips next number.
    *   `1, 2, 2, 4` (Notice 3 is skipped)
*   **DENSE_RANK():** Same rank for ties, does NOT skip next number.
    *   `1, 2, 2, 3`

### 9. Window Functions
**Q:** What is a Window Function?
**A:**
Performs a calculation across a set of table rows that are somehow related to the current row. Unlike `GROUP BY`, it retains the original rows.
*   **Structure:** `Function() OVER (PARTITION BY col ORDER BY col)`
*   **Types:**
    *   *Ranking:* `rank`, `dense_rank`, `row_number`
    *   *Aggregate:* `sum`, `avg`, `min`, `max` (Running totals)
    *   *Value:* `lag`, `lead`, `first_value`, `last_value`

---

## Python Concepts (Decorators, Structures)

### 10. Decorators
**Q:** What are decorators?
**A:**
A design pattern to modify the behavior of a function without changing its code. It takes a function as argument and returns a wrapper function.
```python
def my_decorator(func):
    def wrapper():
        print("Before function")
        func()
        print("After function")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")
```

### 11. List vs Tuple vs Dictionary
**Q:** Comparison of Python data structures.
**A:**
*   **List (`[]`):** Mutable, Ordered. Good for collections that change. `[1, 2, 3]`
*   **Tuple (`()`):** Immutable, Ordered. Faster than lists. Good for fixed data. `(1, 2, 3)`
*   **Dictionary (`{}`):** Mutable, Unordered (until Python 3.7), Key-Value pairs. Hash-map implementation (O(1) lookup). `{'a': 1}`
*   **Set (`{}`):** Mutable, Unordered, Unique elements. `{'a', 'b'}`

---

## Join Logic Scenarios

### 12. Join Output Scenario
**Q:** Given two tables with duplicate keys `1`, calculate the number of rows for each join type.

**Table A:**
```
id
1
1
1
```
(3 rows of '1')

**Table B:**
```
id
1
1
1
```
(3 rows of '1')

**A:**
*   **Inner Join:** Cartesian product of matching keys.
    *   `3 (Table A) * 3 (Table B)` = **9 rows**
*   **Left Join:** All from Left (3) * Matching from Right (3).
    *   **9 rows**
*   **Right Join:** All from Right (3) * Matching from Left (3).
    *   **9 rows**
*   **Cross Join:** Cartesian product of all rows.
    *   `3 * 3` = **9 rows**
*   **Full Outer Join:** Matches (9) + Unmatched Left (0) + Unmatched Right (0).
    *   **9 rows**

---

## Common Coding Scenarios (Empty DF, Sessionization)

### 13. Create Empty DataFrame
**Q:** How do you create an empty DataFrame with a schema in PySpark?
**A:**
```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Define Schema
schema = StructType([
    StructField("Name", StringType(), True),
    StructField("Age", IntegerType(), True)
])

# Create Empty DataFrame
df = spark.createDataFrame([], schema)

# Verify
df.printSchema()
```

### 14. Sessionization Logic
**Q:** How do you create sessions based on inactivity (e.g., 30 mins)?
**A:**
Use `lag` to find the time difference and a cumulative sum to generate IDs.
```python
from pyspark.sql.functions import lag, col, sum, when
from pyspark.sql.window import Window

# 1. Calculate time difference
w = Window.partitionBy("user_id").orderBy("timestamp")
df = df.withColumn("prev_ts", lag("timestamp").over(w))
df = df.withColumn("diff", col("timestamp").cast("long") - col("prev_ts").cast("long"))

# 2. Flag new session if diff > 1800 sec (30 mins) or if first row (null)
df = df.withColumn("is_new_session", 
    when((col("diff") > 1800) | (col("diff").isNull()), 1).otherwise(0)
)

# 3. Generate Session ID using cumulative sum
df_sessionized = df.withColumn("session_id", sum("is_new_session").over(w))
```

---

## Azure & Databricks Integrations

### 15. Key Vault & Secrets
**Q:** How do you access secrets (passwords/keys) in Databricks securely?
**A:**
Use **Secret Scopes**.
1.  **Create Scope:** Create an Azure Key Vault backed secret scope in Databricks (e.g., `my-scope`).
2.  **Access in Notebook:**
    ```python
    password = dbutils.secrets.get(scope="my-scope", key="db-password")
    ```
3.  **Security:** The secret value is redacted `[REDACTED]` in notebook logs if printed.

### 16. Mounting ADLS Gen2
**Q:** How do you connect Databricks to ADLS Gen2?
**A:**
Use a **Service Principal** and mount the storage.
```python
configs = {
  "fs.azure.account.auth.type": "OAuth",
  "fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
  "fs.azure.account.oauth2.client.id": client_id,
  "fs.azure.account.oauth2.client.secret": client_secret,
  "fs.azure.account.oauth2.client.endpoint": "https://login.microsoftonline.com/..."
}

dbutils.fs.mount(
  source = "abfss://container@storageaccount.dfs.core.windows.net/",
  mount_point = "/mnt/data",
  extra_configs = configs
)
```

---

## Azure Data Factory Components

### 17. Copy Activity & Performance
**Q:** Explain ADF Copy Activity and how to tune it.
**A:**
*   **What it is:** The primary activity to move data between sources and sinks (e.g., SQL -> Blob).
*   **Performance Tuning:**
    *   **DIU (Data Integration Units):** Increase compute power (Cloud IR).
    *   **Parallel Copies:** Increase parallel file copy count.
    *   **Staging:** Enable Staging (via Blob Storage) when loading into Synapse/Snowflake to use PolyBase/COPY command (much faster than row-by-row insertion).

### 18. Triggers
**Q:** What are the types of triggers in ADF?
**A:**
1.  **Schedule Trigger:** Wall-clock schedule (Every day at 9 AM).
2.  **Tumbling Window Trigger:** Processes time slices (9:00-10:00, 10:00-11:00). Supports backfilling and dependencies.
3.  **Event-Based Trigger:** Reacts to storage events (`BlobCreated`, `BlobDeleted`). Starts pipeline immediately when file lands.
4.  **Custom Event Trigger:** Reacts to events from Event Grid (custom topics).

### 19. Event Hubs Integration
**Q:** How does ADF/Databricks interact with Event Hubs?
**A:**
*   **ADF:** Can *not* natively trigger pipelines from individual Event Hub messages (streaming). It can primarily write to Event Hubs or read batches *if* captured.
*   **Databricks (Spark):** The standard consumer.
    *   **Read:** `spark.readStream.format("eventhubs")...`
    *   **Write:** `df.writeStream.format("eventhubs")...`
*   **Capture:** Event Hubs can "Capture" data automatically to ADLS (Avro files). ADF can then process these files in batch triggers (`BlobCreated`).
