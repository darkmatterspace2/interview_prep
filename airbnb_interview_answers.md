# Airbnb Data Engineering Interview Answers
*Based on Senior DE Competencies*

Detailed, architectural, and production-ready answers for Airbnb-style Data Engineering interview questions.

---

## 1️⃣ Data Pipeline Design & Architecture

### 1. Merchandising Optimization Pipeline
**Q:** Design an end-to-end pipeline to capture user interactions (clicks, searches) for merchandising.
**A:**
*   **Ingestion:**
    *   **Source:** Event Logging Service (Backend APIs) emits events to **Kafka** topics (partitioned by `user_id` to guarantee ordering).
    *   *Why Kafka?* High throughput, decoupling, and playback capability.
*   **Processing (Lambda Architecture):**
    *   **Speed Layer (Real-time):** **Spark Structured Streaming** or **Flink** reads from Kafka -> Aggregates clicks/views per Listing ID (1-min windows) -> Writes to **Redis/Cassandra** for immediate ranking updates.
    *   **Batch Layer (Accurate):** **Secor/Kafka Connect** dumps raw events to S3 (Bronze). **Airflow** triggers nightly Spark jobs to deduplicate, join with Dimensions (User demographics), and aggregate metrics (Silver/Gold) -> Writes to **Data Warehouse (Delta Lake/Iceberg)**.
*   **Serving:**
    *   Search Services query Redis for real-time signals.
    *   DS/BI tools query Data Warehouse for historical analysis and Model Training.

### 2. Handling Late-Arriving Events
**Q:** How do you handle late-arriving events?
**A:**
*   **Streaming:** Use **Watermarking** in Spark/Flink. Define a threshold (e.g., "accept data up to 1 hour late").
    *   *Within threshold:* Re-aggregate and update the state.
    *   *Beyond threshold:* Drop or send to a **Dead Letter Queue (DLQ)** (S3 bucket) for manual inspection/backfill.
*   **Batch:** Partition data by **Event Date** (business date), not Processing Date.
    *   If yesterday's data arrives today, it lands in `date=2023-10-25`.
    *   Rerun the DAG for `2023-10-25` to include the late data (Idempotent replay).

### 3. Idempotency strategies
**Q:** How to make pipelines idempotent?
**A:**
*   **Definition:** Running the pipeline multiple times produces the same result.
*   **Strategies:**
    1.  **Overwriting Partitions:** Instead of `INSERT INTO`, use `INSERT OVERWRITE partition(date='...')`.
    2.  **Upserts (Merge):** Use unique keys (e.g., `event_id`) to Merge data. `MERGE INTO target USING source ON t.id = s.id ...`.
    3.  **Deduplication:** Always deduplicate raw data by unique ID in the first transformation step.

---

## 2️⃣ Spark, SparkSQL & Scala

### 1. Execution Model (DAG, Stages, Tasks)
**Q:** Explain Spark's execution model.
**A:**
*   **Application:** User program (Driver + Executors).
*   **Job:** Triggered by an **Action** (e.g., `.count()`, `.write()`).
*   **Stage:** Jobs are divided into Stages by **Shuffle Boundaries** (Wide transformations like `groupBy`, `join`).
    *   *Optimization:* Too many stages = too much I/O.
*   **Task:** The smallest unit of work. One task per Partition. Sent to Executors.
*   **Pipeline:** Spark chains Narrow Transformations (Map, Filter) into a single task (Pipelining) so data isn't written to disk between them.

### 2. Catalyst Optimizer
**Q:** How does it work?
**A:**
1.  **Analysis:** Validates column names/references against the Catalog.
2.  **Logical Optimization:** Applies heuristics:
    *   *Predicate Pushdown* (Filter before Join).
    *   *Column Pruning* (Read only needed columns).
    *   *Constant Folding* (`1+1` -> `2`).
3.  **Physical Planning:** Chooses strategies (HashJoin vs SortMergeJoin) based on cost/stats.
4.  **Code Generation:** Generates optimized Java bytecode (Project Tungsten) to minimize CPU instructions.

### 3. Handling Data Skew
**Q:** How do you handle High Skew (e.g., one 'Guest' clicking 1M times)?
**A:**
*   **Symptom:** One task runs forever; others finish fast. OOM errors.
*   **Fix 1: Salting (For Large Joins):**
    *   Add a random number (0-9) to the skew key in the large table.
    *   Explode the joining key in the small table (replicate rows 0-9).
    *   Join on Key + Salt. This disperses the skew bucket into 10 smaller buckets.
*   **Fix 2: Broadcast Join:**
    *   If one table is small, broadcast it to avoid the shuffle entirely.
*   **Fix 3: Filter Nulls:** Often skew is caused by `null` keys. Filter them out first.

---

## 3️⃣ Airflow & Orchestration

### 1. Airflow Architecture
**Q:** How does Airflow work?
**A:**
*   **Scheduler:** The brain. Parses DAGs, checks schedules, checks dependencies, creates "Task Instances" in the DB.
*   **Executor (Kubernetes/Celery):** Picks up "Queued" tasks and assigns them to Workers.
*   **Worker:** Executes the actual code (or submits the Spark Application).
*   **Metastore (Postgres):** Stores the state of every DAG run and Task instance.

### 2. Backfills
**Q:** How to implement backfills safely?
**A:**
*   **Idempotency is Key:** Ensure re-running a date range overwrites cleanly.
*   **Catchup:** Set `catchup=False` generally to avoid accidental floods. For intentional backfill, instantiate DAG runs for the historical period using CLI `airflow dags backfill ...`.
*   **Scaling:** Limit concurrency (`max_active_runs`) during backfill to avoid DDOSing systems.

---

## 4️⃣ Data Modeling (Merchandising)

### 1. Modeling Listing Interactions
**Q:** Model data for Listing Merchandising.
**A:**
*   **Fact Table:** `fct_listing_views`
    *   `view_id` (PK), `listing_id` (FK), `viewer_id` (FK), `timestamp`, `platform`, `duration_sec`, `is_booked` (Boolean).
*   **Dimension Table:** `dim_listings` (SCD Type 2)
    *   `listing_id`, `host_id`, `neighborhood`, `room_type`, `price`, `active_from`, `active_to`, `is_current`.
*   **Aggregated Table (Merchandising):** `agg_listing_daily_metrics`
    *   `listing_id`, `date`, `total_views`, `conversion_rate`, `avg_time_on_page`.
    *   *Usage:* Used by the Ranking Algorithm to promote high-converting listings.

### 2. SCD Type 2
**Q:** How to handle Price Changes over time?
**A:**
Use SCD Type 2 on the Listing Dimension.
*   **Columns:** `price`, `valid_from`, `valid_to`, `is_current`.
*   **Update Logic:** When price changes from $100 to $120:
    1.  Update old row: `valid_to` = Now, `is_current` = False.
    2.  Insert new row: `price` = 120, `valid_from` = Now, `valid_to` = 9999-12-31, `is_current` = True.

---

## 5️⃣ Data Quality & Reliability

### 1. Data Contracts & Validation
**Q:** How do you design data validation?
**A:**
*   **Shift Left:** Validate schema at the source (Schema Registry).
*   **Write-Audit-Publish:**
    *   Write data to a *Staging* table.
    *   Run checks (Great Expectations / dbt tests): `count > 0`, `unique_id`, `null_rate < 1%`.
    *   If Pass -> Swap/Merge to Production.
    *   If Fail -> Alert and Halt. Do NOT corrupt Prod.
*   **Contracts:** Use explicit YAML contracts (e.g., OpenLineage) defining schema and ownership between Producers and Data Engineering.

---

## 6️⃣ Distributed Systems & Scale

### 1. Kafka Ordering
**Q:** How does Kafka guarantee ordering?
**A:**
*   Kafka guarantees order **only within a Partition**, NOT across the whole topic.
*   **Design:** Producer must hash the ordering key (e.g., `user_id`) so all events for User A go to Partition 5.
*   Consumer reads Partition 5 sequentially, preserving the order of user actions.

### 2. Hot Partitions
**Q:** How to handle hot partitions (one partition taking too much traffic)?
**A:**
*   **Cause:** Poor partition key choice (e.g., partitioning by 'Country' and 'USA' is 90% of traffic).
*   **Solution:**
    *   Change Key: Use finer grain (e.g., `user_id` instead of `country`).
    *   **Random Partitioning:** If ordering isn't strictly required at ingestion, randomize partitioning to distribute load, then re-sort downstream.

---

## 7️⃣ Behavioral & Product SRE

### 1. Working with DS/PM
**Q:** How do you prioritize Requests?
**A:**
*   "I prioritize based on **Business Impact vs Effort** matrix."
*   *Example:* "PM wanted a real-time dashboard. I asked 'What decision will you make in 5 minutes that you can't make in 1 hour?'. They realized hourly batch was sufficient. This saved 3 weeks of engineering time vs building a streaming pipeline."

### 2. Tech Debt
**Q:** How do you handle Tech Debt?
**A:**
*   "I follow the 'Boy Scout Rule': Leave the code better than you found it."
*   "I advocate for 20% innovation/cleanup time in Sprint planning to migrate legacy pipelines."

---

## 🔟 Airbnb System Design: Merchandising Platform

**Goal:** Real-time & Batch optimization for Listings.

**1. Data Sources:**
*   User Activity (Kafka): Clicks, Bookings.
*   Listing Metadata (MySQL/CDC): Price, Description changes.

**2. Ingestion:**
*   **Debezium:** Captures Listing DB changes (CDC) -> Kafka.
*   **Event Collector:** App sends Clicks -> Kafka.

**3. Processing:**
*   **Real-time (Flink/Spark Streaming):** 
    *   Ingest Clicks & CDC.
    *   Join Click + Listing Metadata (Enrichment). Use State Management/Broadcast State for Metadata.
    *   Calc "Hot Listings" (Views last 10 mins).
    *   Sink -> **Redis** (Feature Store) for Search Ranker API to read ms-latency.
*   **Batch (Spark/Airflow):**
    *   Ingest raw Kafka to Data Lake (S3).
    *   Calculate complex metrics (e.g., "7-day Conversion Rate vs Neighborhood Average").
    *   Sink -> **Hive/Iceberg**.

**4. Storage:**
*   **Bronze:** Raw JSON (S3).
*   **Silver:** Cleaned, Deduplicated (Delta Lake).
*   **Gold:** Aggregated Metrics (Delta Lake).
*   **Feature Store:** Redis (Online), Iceberg (Offline).

**5. Consumer:**
*   **Search Service:** Queries Redis to boost "Hot" listings.
*   **Merchandising DS Team:** Queries Gold tables to train "Ranking Model".

**6. Quality:**
*   Circuit Breakers on Spark Jobs (Validation).
*   Lag monitoring on Kafka Consumers.
