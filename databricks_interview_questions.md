# Databricks Interview Questions & Concepts
*Mid to Senior Level*

A comprehensive guide to Databricks-specific features, architecture, and optimization techniques, focusing on the Lakehouse platform.

---

## Table of Contents
1. [Architecture & Core Concepts](#architecture--core-concepts)
2. [Delta Lake Internals](#delta-lake-internals)
3. [Unity Catalog & Governance](#unity-catalog--governance)
4. [Performance Optimization (Databricks Specific)](#performance-optimization-databricks-specific)
5. [Data Engineering Features (DLT, Auto Loader)](#data-engineering-features)

---

## Architecture & Core Concepts

### 1. Control Plane vs Data Plane
**Q:** Explain the difference between the Control Plane and Data Plane in Databricks architecture.
**A:**
*   **Control Plane:** Managed by Databricks (in their AWS/Azure account). It hosts the UI, Cluster Manager, Jobs service, Notebooks, and the Web Application.
*   **Data Plane:** Resides in **your** customer cloud account (VPC/VNet). This is where the actual compute (clusters) runs and where data is processed. Data generally stays in your plane (security requirement).
*   **Serverless Data Plane:** A newer model where compute runs in Databricks' account but is strictly isolated, allowing for instant startup (SQL Warehouses).

### 2. High Concurrency vs Standard Cluster
**Q:** When would you choose a High Concurrency cluster?
**A:**
*   **High Concurrency:** Optimized for multiple users sharing resources (e.g., a BI/Analyst team running SQL in notebooks). It uses features like *Task Preemption* to ensure small queries aren't blocked by long-running ones. It forces isolation (Python/SQL) to prevent users from interfering with each other's state.
*   **Standard (Single User):** Best for single users or automated jobs. Supports all languages (Scala, R, Python, SQL) without restriction.

### 3. Photon Engine
**Q:** What is Photon and when should you enable it?
**A:**
*   **What:** A vectorized query engine written in C++ (instead of JVM) that replaces Spark's existing execution engine.
*   **When:** Best for SQL-heavy workloads, aggressive aggregations, extensive joins, and Delta Lake operations (Merge/Delete).
*   **Cost:** It costs more DBUs (Databricks Units) per hour, so it should be benchmarked to ensure the speedup justifies the cost.

---

## Delta Lake Internals

### 4. ACID Transactions in Delta
**Q:** How does Delta Lake achieve ACID properties on top of S3/ADLS (which are eventually consistent)?
**A:**
It uses a **Transaction Log (`_delta_log`)**:
*   **Atomicity:** Changes are recorded in JSON files in the log. A commit fails or succeeds completely.
*   **Consistency:** Readers verify the log state to ensure they read a consistent snapshot.
*   **Isolation:** Uses Optimistic Concurrency Control (OCC). If two writers try to update the same file, one fails with a concurrency exception.
*   **Durability:** Data is stored in persistent object storage (Parquet).

### 5. Time Travel & Restore
**Q:** How do you query a table as it existed yesterday? How do you rollback an accidental delete?
**A:**
```sql
-- Query older version
SELECT * FROM my_table TIMESTAMP AS OF '2023-10-25 10:00:00';
SELECT * FROM my_table VERSION AS OF 5;

-- Rollback (Restore)
RESTORE TABLE my_table TO VERSION AS OF 4;
```
*Mechanism:* Delta keeps old parquet files (tombstoned) until `VACUUM` is run.

### 6. VACUUM
**Q:** What does `VACUUM` do and what is the risk?
**A:**
*   Removes physical files that are no longer referenced by the current state of the transaction log and are older than the retention period (default 7 days).
*   **Risk:** Once vacuumed, you **cannot** Time Travel back to versions requiring those files.

---

## Unity Catalog & Governance

### 7. Unity Catalog vs Hive Metastore
**Q:** Why migrate to Unity Catalog (UC)?
**A:**
1.  **Centralized Governance:** Single metastore across specific workspaces/regions (unlike workspace-local Hive metastores).
2.  **Data Lineage:** Automated column-level lineage tracking.
3.  **Audit Logs:** Centralized auditing of who accessed what data.
4.  **External Locations/Credentials:** Securely manages access to S3/ADLS without exposing keys in notebooks.
5.  **3-Level Namespace:** `Catalog.Schema.Table` hierarchy.

### 8. Managed vs External Tables in UC
**Q:** Difference between Managed and External tables in Unity Catalog?
**A:**
*   **Managed Table:** Unity Catalog manages the lifecycle AND the data location (in a managed storage bucket). Dropping the table **deletes** the underlying data.
*   **External Table:** You manage the storage location. Dropping the table only deletes the metadata; the files persist in cloud storage.

---

## Performance Optimization (Databricks Specific)

### 9. OPTIMIZE & Z-ORDER
**Q:** Explain `OPTIMIZE` and `Z-ORDER BY`. How is it different from Partitioning?
**A:**
*   **Partitioning:** Physical directory separation (e.g., `Year=2023`). Good for low-cardinality columns. Bad if >10k partitions.
*   **OPTIMIZE (Bin-packing):** Coalesces small files (100MB - 1GB) into larger ones to fix the "Small File Problem".
*   **Z-ORDER (Multi-dimensional Clustering):** Co-locates related data within the same set of files.
    *   *Scenario:* If you frequently filter by `CustomerID` (high cardinality), Partitioning is bad. Z-Ordering by `CustomerID` allows Delta to skip huge chunks of data (Data Skipping) efficiently.

```sql
OPTIMIZE events_table ZORDER BY (user_id, event_type);
```

### 10. Cache vs Disk Spec
**Q:** Databricks uses "Delta Cache" (now "Disk Cache"). How is it different from Spark Cache?
**A:**
*   **Spark Cache (`.cache()`):** Stores data in RAM (Executor memory). Can cause OOM if too large.
*   **Disk Cache (IO Cache):** Automatically creates copies of remote Parquet files on the local SSDs of the worker nodes. It is entirely separate from JVM memory. It accelerates read speeds significantly and does **not** cause OOMs.

---

## Data Engineering Features

### 11. Auto Loader
**Q:** What is Auto Loader (`cloudFiles`)?
**A:**
An optimized streaming source to ingest files from S3/ADLS.
*   **Benefits:** More efficient and cheaper than standard `spark.readStream` file listing.
*   **Mechanism:** Can works in two modes:
    1.  **Directory Listing:** Good for few files.
    2.  **File Notification:** Subscribes to Cloud Queue (SQS/Event Grid) to ingest files immediately upon arrival without listing directories.
*   **Schema Evolution:** Can automatically infer and evolve schema (add new columns) as data changes.

### 12. Delta Live Tables (DLT)
**Q:** When would you use DLT?
**A:**
A declarative framework for building reliable pipelines.
*   **expectations (Data Quality):** `CONSTRAINT valid_id EXPECT (id IS NOT NULL) ON VIOLATION DROP ROW`.
*   **Automated dependency management:** No need to chain tasks manually; DLT figures out the DAG.
*   **Auto-scaling:** Enhanced Autoscaling works specifically well for DLT streaming workloads.

### 13. COPY INTO vs Auto Loader
**Q:** Difference between `COPY INTO` and Auto Loader?
**A:**
*   **COPY INTO:** Best for bulk ingestion (thousands of files). One-time idempotent loads. simpler syntax for SQL users.
*   **Auto Loader:** Best for continuous streaming ingestion (millions of files). Scalable incremental processing.
