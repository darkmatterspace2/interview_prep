# Amazon ETL & Pipeline Design Interview Questions

## Part 1: ETL / Pipeline Design

### Batch Pipelines

#### 61. Design a daily shipment aggregation pipeline.
**Answer:**
1.  **Ingestion:** Shipments land in S3 (Raw Zone) via DMS (from DB) or Kinesis Firehose.
2.  **Processing:**
    *   Trigger an AWS Glue Job or EMR Step daily (e.g., via Airflow/EventBridge).
    *   Read raw JSON/CSV data.
    *   Apply transformations: Dedup, Join with DimCustomer, Calculate totals.
3.  **Storage:** Write aggregated results to S3 (Parquet, Partitioned by Date).
4.  **Serving:** Load metadata to Athena or Copy command to Redshift.

#### 62. Idempotent pipeline — explain with example.
**Definition:** Running the pipeline multiple times produces the *same result* as running it once. It doesn't duplicate data.
**Example:**
*   *Bad:* `INSERT INTO target SELECT * FROM source` (Running twice doubles the data).
*   *Good (Idempotent):* 
    1. `DELETE FROM target WHERE date = '2023-01-01'`
    2. `INSERT INTO target SELECT * FROM source WHERE date = '2023-01-01'`
    *   No matter how many times you run this for '2023-01-01', the state is consistent.

#### 63. Backfill last 30 days of data.
**Answer:**
*   Do not run one giant job for 30 days (risk of failure).
*   Run 30 separate jobs (one per day), ideally in parallel if resources allow.
*   Use your orchestration tool (Airflow) to "clear" the task status for those 30 days to trigger re-execution.

#### 64. Handle partial pipeline failures.
**Answer:**
*   **Checkpointing:** Save state of how much has been processed.
*   **Atomic Swaps:** Write to a temporary directory/table. Only when successful, move/swap to the final location. If it fails halfway, the final location remains untouched (clean).

#### 65. Reprocess corrupted data safely.
**Answer:**
*   Identify the corrupted partition.
*   Fix the upstream source or bug.
*   Use the **Idempotent** logic (Q62) to re-run the pipeline for that specific partition, overwriting the bad data with good data.

---

### Streaming / Near Real-Time

#### 66. Design real-time shipment status tracking.
**Design:**
1.  **Source:** Application emits status events to **AWS Kinesis Data Streams** or Kafka.
2.  **Processing:** **Spark Structured Streaming** or **AWS Lambda** reads from Kinesis.
3.  **Logic:** Update state in a NoSQL store (DynamoDB is excellent for single-row key-value lookups).
4.  **Serving:** Frontend queries DynamoDB for `shipment_id`.

#### 67. Handle duplicate events in streaming.
**Answer:**
*   **Deduplication window:** Store event IDs in a state store (or RocksDB in Flink) for a set window (e.g., 10 mins). Discard if seen again.
*   **Idempotent Sink:** If writing to a DB, use `Upsert` (Update if exists, Insert if new). If the same event comes twice, it just updates the same record to the same value.

#### 68. Event time vs processing time.
**Answer:**
*   **Event Time:** The time the event actually happened (data creation). *Use this for analytics.*
*   **Processing Time:** The time the system received the data.
*   *Difference:* Lag. If network goes down for an hour, Processing Time will show a spike an hour later, but Event Time places data correctly in the past.

#### 69. Late-arriving events handling.
**Answer:**
*   **Watermarks:** In streaming engines (Spark/Flink), define a cutoff (e.g., "accept data up to 1 hour late").
*   What to do with data older than watermark?
    *   Discard (if real-time accuracy is only thing that matters).
    *   Send to "Dead Letter Queue" or side-output for batch backfill later.

#### 70. Exactly-once vs at-least-once semantics.
**Answer:**
*   **At-least-once:** Messages are guaranteed to be delivered, but might be duplicated. (Standard Kinesis/Kafka default). Requires idempotent sink.
*   **Exactly-once:** Harder to achieve. Requires cooperation between source, processor, and sink (e.g., Kafka Transactions, Spark Streaming checkpoints).

---

### Reliability & Quality

#### 71. Data validation checks you’d implement.
**Answer:**
*   **Schema Check:** Does column count/types match?
*   **Null Check:** Are critical keys (shipment_id) null?
*   **Volume Check:** Did we receive significantly fewer rows today than average? (Anomaly detection).
*   **Range Check:** Is `weight < 0`?

#### 72. Monitoring pipeline health.
**Answer:**
*   **Latency:** Time from ingestion to availability.
*   **Throughput:** Records per second.
*   **Error Rate:** % of records sent to DLQ.
*   **Tools:** CloudWatch Alarms, Datadog, Prometheus.

#### 73. SLA vs SLO for data pipelines.
**Answer:**
*   **SLA (Agreement):** Contractual promise to user (e.g., "Data available by 9 AM"). Breach = Penalty.
*   **SLO (Objective):** Internal goal (e.g., "Data available by 8:30 AM"). Buffer to ensure SLA is met.

#### 74. Alert fatigue — how to avoid?
**Answer:**
*   **Actionable:** Only alert if a human needs to *do* something.
*   **Priority:** Sev-1 (Data missing) calls phone. Sev-3 (Latency slightly high) sends email/ticket.
*   **Grouping:** Don't send 100 emails for 100 failed files; send 1 email saying "Ingestion failing".

#### 75. Root cause analysis of data mismatch.
**Approach:** "The 5 Whys".
1.  Verify Source vs Target counts.
2.  Isolate the specific records missing.
3.  Check transformations (filtering logic).
4.  Check timing (did the query run before data arrived?).
5.  Check joins (Cartesian products or dropping rows).
