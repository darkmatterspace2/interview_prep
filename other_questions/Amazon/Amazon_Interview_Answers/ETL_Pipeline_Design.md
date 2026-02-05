# Amazon ETL & Pipeline Design Interview Questions (Detailed)

## Part 1: ETL / Pipeline Design

### Batch Pipelines

#### 61. Design a daily shipment aggregation pipeline.
**Scenario:** You need to aggregate daily shipment data (100GB/day) to calculate KPIs like "Total Cost per Region".
**Detailed Answer:**
1.  **Ingestion (Bronze Layer):**
    *   **Source:** OLTP Database (Postgres) or API.
    *   **Tool:** AWS DMS (Database Migration Service) for CDC or a daily Batch Job (Airflow + Python) fetching API data.
    *   **Storage:** S3 `s3://bucket/raw/shipments/date=2023-01-01/`. Format: JSON or CSV (Gzipped).
2.  **Processing (Silver Layer - Cleaning):**
    *   **Tool:** AWS Glue or EMR (Spark).
    *   **Logic:** Read Raw -> Deduplicate (distinct by `shipment_id`) -> Cast Types (String to Timestamp) -> Join with `DimCustomer` (Broadcast Join) -> Write to Silver.
    *   **Storage:** S3 `s3://bucket/silver/shipments/`. Format: **Parquet** (Snappy compressed) for fast columnar reads.
3.  **Aggregation (Gold Layer - KPIs):**
    *   **Tool:** Glue/Spark.
    *   **Logic:** Read Silver -> `groupBy("region", "date").agg(sum("cost"))`.
    *   **Storage:** S3 (Gold).
4.  **Serving:**
    *   **Catalog:** Register Gold data in **AWS Glue Data Catalog**.
    *   **Query:** Analytics team queries via **Amazon Athena** (Presto) or data is loaded into **Redshift** via `COPY` command for high-performance dashboards.

#### 62. Idempotent pipeline — explain with example.
**Definition:** An idempotent operation can be applied multiple times without changing the result beyond the initial application. In pipelines, it means re-running a job for the same day doesn't create duplicate rows.
**Implementation Patterns:**
1.  **Overwrite Strategy (Most Common):**
    *   *SQL:* `INSERT OVERWRITE TABLE daily_metrics PARTITION (date='2023-01-01') SELECT ...`
    *   *Spark:* `df.write.mode("overwrite").partitionBy("date").save(...)`
    *   *Result:* If you run it 10 times, it deletes the `date=2023-01-01` folder and rewrites it. The end state is always single, correct copy.
2.  **Delete-Then-Write (Transactional DBs):**
    *   `BEGIN TRANSACTION;`
    *   `DELETE FROM target_table WHERE processing_date = '2023-01-01';`
    *   `INSERT INTO target_table SELECT * FROM staging WHERE processing_date = '2023-01-01';`
    *   `COMMIT;`
3.  **Upsert (Merge):**
    *   Using keys to update existing records or insert new ones (e.g., `MERGE INTO` in Databricks/Redshift).

#### 63. Backfill last 30 days of data.
**Scenario:** Usage logic changed, and you need to recalculate metrics for the last month.
**Strategy:**
1.  **Parallel Execution:** Don't run a single job loops 1..30. It's slow and fragile.
2.  **Airflow Backfill:** 
    *   Use Airflow's ability to "Clear" task instances for the date range.
    *   Airflow will schedule 30 separate generic DAG runs: `Run(2023-01-01)`, `Run(2023-01-02)`, ...
    *   **Concurrency Control:** Set `max_active_runs=5` to process 5 days at a time, avoiding crushing the source DB.
3.  **Inverse Pyramid:** (Optional for dependencies) Run the oldest day first if state depends on previous day. If days are independent, run newest first (to fix recent dashboards) then fill history.
4.  **Separation:** If huge, spin up a dedicated "Backfill Cluster" so the daily production pipeline (SLA critical) isn't resource-starved.

#### 64. Handle partial pipeline failures.
**Problem:** The job crashes after writing 50% of the files. The output folder is now "dirty" (mix of old and new partial data).
**Solutions:**
1.  **Atomic Write (S3/HDFS):**
    *   Spark writes to a `_temporary` subfolder.
    *   Only when *all* tasks succeed, it renames the folder to the final destination (File System operation).
    *   *Note:* S3 rename is not atomic (eventually consistent) unless using S3Guard (old) or newer S3 strong consistency features + specialized committers (e.g., Magic S3A Committer).
2.  **Staging Tables (Redshift):**
    *   Write batch to `staging_table` (Truncate before load).
    *   Perform checks (Row count > 0).
    *   Swapping: `ALTER TABLE target RENAME TO old; ALTER TABLE staging RENAME TO target; DROP TABLE old;`
3.  **Transaction Boundaries:** In RDBMS, verify the Transaction commits only at end of script.

#### 65. Reprocess corrupted data safely.
**Scenario:** A bug in the parser caused 10% of rows to be NULL in the 'Revenue' column for last Tuesday.
**Approach:**
1.  **Isolate:** Identifying the partition `date=2023-01-10`.
2.  **Fix:** Patch the parsing code.
3.  **Re-run (Idempotent):** Trigger the pipeline specifically for `2023-01-10`.
    *   The "Overwrite" logic cleans out the corrupted Parquet files and writes fresh valid ones.
4.  **Downstream:** You must also identify *dependent* jobs (e.g., "Monthly Aggregates") and re-run them for that period to propagate the fix.
5.  **Data Lake Pattern:** "WORM" (Write Once Read Many) often means we don't update files. Ideally, we write a *new* version (`v2`) and update the metastore pointer, or simply overwrite if versioning isn't strict.

---

### Streaming / Near Real-Time

#### 66. Design real-time shipment status tracking.
**Architecture:**
1.  **Source:** Trucks send GPS pings (MQTT) to **AWS IoT Core**.
2.  **Stream Ingest:** IoT Core forwards to **Kinesis Data Streams** (Sharded by `TruckID` to preserve order).
3.  **Processing:** 
    *   **Consumer:** **AWS Lambda** (for event-driven, low load) or **Flink/Spark Streaming** (for high throughput stateful windowing).
    *   **Logic:** Compare new location with `RoutePlan`. If `deviation > 1km`, flag alert.
4.  **State Store:**
    *   **DynamoDB:** Stores "Current State" (`TruckID`, `Lat`, `Lon`, `LastUpdate`). Fast Key-Value lookups.
5.  **Serving:** Ops Dashboard queries DynamoDB via AppSync (GraphQL).

#### 67. Handle duplicate events in streaming.
**Cause:** network retries (At-Least-Once delivery).
**Solutions:**
1.  **Idempotent Sink (Best):**
    *   DynamoDB `put_item`: If `EventID: 101` is written twice, the second write overwrites the first with identical data. No harm done.
2.  **Windowed Deduplication (In-Memory):**
    *   Spark/Flink maintains a State Store of "Seen IDs in last 10 mins".
    *   `df.dropDuplicates(["event_id"])` with a defined watermark.
    *   If a duplicate arrives within 10 mins, drop it. If it arrives 1 hour later (outside watermark), it might pass through (trade-off: infinite state vs occasional duplicate).

#### 68. Event time vs processing time.
**Definition:**
*   **Event Time:** Timestamp attached by the sensor/device (When it happened). `10:00 AM`.
*   **Processing Time:** Timestamp when the server read the message. `10:05 AM`.
**Significance:**
*   Always define windows on **Event Time**.
*   *Example:* If valid "Sales per Hour" is needed. A sale happening at `9:59` arriving at `10:02` belongs to the 9-10 bucket, not the 10-11 bucket. Using Processing Time distorts historical accuracy during lag spikes.

#### 69. Late-arriving events handling.
**Mechanism: Watermarking.**
*   A Watermark is a declaration: "I will wait 10 minutes for late data. After that, I finalize the window."
*   **Strategy 1 (Drop):** If data comes >10 mins late, ignore it. (Good for real-time monitoring where old news is useless).
*   **Strategy 2 (Update):** Allow late data to trigger a re-computation of the old window. (Supported in some sinks, but complex).
*   **Strategy 3 (Side Output):** Send into a "Late Queue" (S3 bucket). Run a nightly batch job to merge these late events into the historical dataset for correct "Audit" records.

#### 70. Exactly-once vs at-least-once semantics.
**Reality Check:** "Exactly Once" usually means "Effectively Exactly Once" (Processing happens, but side effects are atomic).
*   **At-Least-Once:** (Kinesis Default). Retries imply duplicates. Requires downstream deduplication (Idempotence).
*   **Exactly-Once (End-to-End):** Hard.
    *   *Source:* Must be replayable (Kafka/Kinesis).
    *   *Processor:* Flink/Spark Checkpoints store the strict offset processed.
    *   *Sink:* Must support transactions (Kafka Transactional Producer) or Atomic Overwrites (HDFS/S3).
    *   *Example:* Flink "Two-Phase Commit" sink. It prepares the data in DB, and only "Commits" if the Flink checkpoint succeeds.

---

### Reliability & Quality

#### 71. Data validation checks you’d implement.
**Frameworks:** **Great Expectations**, **Deequ** (optimized for Spark).
**Checks:**
1.  **Schema Consistency:** "Does the incoming JSON have the 'user_id' field?"
2.  **Completeness:** "Is 'user_id' non-null?"
3.  **Uniqueness:** "Are primary keys unique?"
4.  **Referential Integrity:** "Does 'store_id' exist in the Stores Dimension table?"
5.  **Statistical/Anomaly:**
    *   "Is the row count within 20% of the 30-day average?"
    *   "Is `max(age)` < 120?"
6.  **Business Logic:** "Ship_date cannot be before Order_date".

#### 72. Monitoring pipeline health.
**Metrics to Watch:**
1.  **Lag (Consumer Lag):** How far behind real-time is the processor? (Kafka Offset Lag). Increasing lag = danger.
2.  **Throughput:** Records processed/sec. Sudden drop = upstream issue.
3.  **DLQ Rate:** Percentage of records failing validation. Spike = bad data deployment.
4.  **Resource Usage:** Memory/CPU. Approach OOM limits?
5.  **Data Freshness (SLA):** "Time since last successful write to Target".

#### 73. SLA vs SLO for data pipelines.
*   **SLA (Service Level Agreement):** The **External** contract. "Data provided by 9:00 AM". Breach involves financial penalty or formal apology.
*   **SLO (Service Level Objective):** The **Internal** goal. "Data provided by 8:30 AM".
*   **SLI (Service Level Indicator):** The *Metric* itself. "Timestamp of file arrival".
*   *Why separation?* Failure to meet SLO (8:45 AM) triggers an internal P2 alert to fix it *before* it breaches the SLA (9:00 AM).

#### 74. Alert fatigue — how to avoid?
**Principles:**
1.  **Actionable:** If I get an alert, I must be able to *do* something. "CPU 90%" is useless if it auto-scales. "Pod CrashLoopBackOff" is actionable.
2.  **Deduplication:** Flatten 50 "File Load Failed" errors into 1 "Ingestion Incident" ticket.
3.  **Severity Tiers:**
    *   **Sev 1 (PagerDuty):** Data Stalled, SLA Breach Imminent. (Wake up).
    *   **Sev 3 (Jira/Email):** Non-critical data late, Validation Warning (1% bad rows). Handle next business day.
4.  **Maintenance Windows:** Silence alerts during planned deploys.

#### 75. Root cause analysis of data mismatch.
**Scenario:** Dashboard shows $1M, Source shows $1.2M.
**Analysis Steps:**
1.  **Scope:** Is it a specific date? Region? Product? (Narrow the search space).
2.  **Lineage:** Trace the path. Source -> Raw -> Silver -> Gold -> Dashboard.
3.  **Binary Search:** Compare counts at each stage.
    *   Source vs Raw: Match? (If no, Ingestion broke).
    *   Raw vs Silver deduped: Match? (If no, Deduplication logic flawed).
    *   Silver vs Gold: Match? (If no, Aggregation or Join logic flawed).
4.  **Common Culprits:**
    *   **Timezones:** Source is UTC, Dashboard is EST.
    *   **Late Data:** Dashboard queried at 8am, Pipeline finished at 8:05am.
    *   **Join Fan-out:** Unintentional 1-to-many join duplicating rows.
    *   **Inner Join Drop:** Missing keys in Dimension table dropping Fact rows.
