# Databricks Interview Cheat Sheet

A quick reference guide for Databricks architecture, features, and optimization techniques.

## 1. The Lakehouse Architecture
**Concept:** Combines the best elements of Data Lakes (low cost, flexibility, supports unstructured data) and Data Warehouses (ACID transactions, schema enforcement, high performance).

### Medallion Architecture (Multi-hop)
- **Bronze Layer (Raw):**
    - Raw data ingestion (append-only).
    - Stores unvalidated data "as-is".
    - Often usually JSON, Parquet, or CSV.
- **Silver Layer (Curated/Enriched):**
    - Cleaned, filtered, and augmented data.
    - Schema validation, deduplication, and joins happen here.
    - Single source of truth.
- **Gold Layer (Aggregated):**
    - Business-level aggregates for reporting and dashboards.
    - Modeled for performance (Star/Snowflake schema).
    - Ready for consumption by BI tools (PowerBI, Tableau).

## 2. Delta Lake
**Definition:** An open-source storage layer that brings reliability to data lakes. It sits on top of object storage (S3/ADLS/GCS).

**Key Features:**
- **ACID Transactions:** Ensures data integrity (Atomicity, Consistency, Isolation, Durability). Parallel reads/writes via Optimistic Concurrency Control.
- **Time Travel:** Query data at a specific point in time (using `VERSION AS OF` or `TIMESTAMP AS OF`). Useful for auditing and rollbacks.
- **Schema Enforcement & Evolution:**
    - *Enforcement:* Rejects writes that don't match the schema.
    - *Evolution:* Allows schema updates (add columns) automatically using `.option("mergeSchema", "true")`.
- **Merge (Upsert):** Efficently insert, update, and delete data using `MERGE INTO`.

## 3. Unity Catalog & Governance
**Definition:** A unified governance solution for data and AI assets across all workspaces.

**Hierarchy:**
1.  **Metastore:** The top-level container (usually one per region).
2.  **Catalog:** The first level (e.g., `prod`, `dev`).
3.  **Schema (Database):** Contains tables, views, functions.
4.  **Table/Volume/Model:** The actual assets.

**Key Features:**
- **Centralized Access Control (ACLs):** Manage permissions in one place using standard SQL (`GRANT SELECT ON TABLE...`).
- **Data Lineage:** Automatically tracks how data flows from source to target (Table-level and Column-level).
- **Audit Logs:** Tracks who accessed what data.

## 4. Performance Optimization
**Techniques to speed up queries and jobs:**

- **Photon Engine:** Native vectorized execution engine written in C++ for extreme performance on SQL and DataFrame API calls.
- **Z-Ordering (Z-Order Clustering):** Co-locates related information in the same set of files. Used with `OPTIMIZE`.
    - Best for: Columns frequently used in `WHERE` clauses (filters).
    - *Command:* `OPTIMIZE table_name ZORDER BY (col1, col2)`
- **Liquid Clustering:** Newer, dynamic clustering that replaces Z-Order/Partitioning. Automatically adjusts data layout.
- **Partitioning:** (Legacy/Large Scale) Physically splitting data into directories by column (e.g., Date). avoid over-partitioning (small files problem).
- **Auto Optimize:** Automatically compacts small files during writes.

## 5. Streaming (Structured Streaming)
**Auto Loader (`cloudFiles`):**
- Efficiently ingests millions of files from cloud storage as they arrive.
- Uses file notification events (SNS/SQS/Event Grid) or directory listing.
- *Schema Inference:* Automatically detects schema changes and "rescues" bad data (`_rescued_data` column).

**Delta Live Tables (DLT):**
- Declarative framework for building reliable ETL pipelines.
- Automates infrastructure management, dependency resolution (DAGs), and quality checks (Expectations).
- *Expectation:* `CONSTRAINT valid_id EXPECT (id IS NOT NULL) ON VIOLATION DROP ROW`

## 6. Common Interview Questions
1.  **Map vs FlatMap?**
    - Map: 1 input -> 1 output.
    - FlatMap: 1 input -> 0 or more outputs (flattening).
2.  **Narrow vs Wide Transformations?**
    - *Narrow:* Data stays in same partition (e.g., `filter`, `map`). Fast.
    - *Wide:* Data shuffles across network (e.g., `groupBy`, `join`, `distinct`). Slower.
3.  **Coalesce vs Repartition?**
    - *Coalesce:* Decreases partitions. No shuffle (mostly). Efficient.
    - *Repartition:* Increases or decreases. Full shuffle. Balanced distribution.
4.  **What is the "Small File Problem"?**
    - Too many small files cause metadata overhead and slow listing.
    - *Fix:* `OPTIMIZE`, `VACUUM`, Auto Optimize.
