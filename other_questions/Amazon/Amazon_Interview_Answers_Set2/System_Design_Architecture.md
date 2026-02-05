# Data Engineering System Design - Architecture & Pipelines

## 1️⃣ Batch vs Streaming — Design Decision Questions

#### 1. Given a use case, **how do you decide batch or streaming**?
**Decision Matrix:**
*   **Latency Requirement:** Is result needed in < 1 minute? (Streaming). Is < 24 hours fine? (Batch).
*   **Complexity Cost:** Streaming is 3x harder to debug/maintain. Only pay that tax if business value (ROI) justifies it.
*   **Actionability:** Will a human/machine *act* on the data immediately? (Fraud detection -> Yes -> Streaming). (Executive Report -> No -> Batch).

#### 2. When is *near-real-time batch* better than streaming?
*   **Micro-batching (Frequency: 15 mins):**
*   Better when you need **Deduping** or **Aggregating** over a window.
*   It allows "looking back" slightly to correct data quality before publishing.
*   Much simpler error handling (just re-run the 15-min file) compared to replaying a stream.

#### 3. Why do many “real-time” systems secretly use micro-batch?
True event-by-event streaming (Storm/Flink) is hard. Spark Streaming (legacy) and even Structured Streaming defaults often process in small chunks (triggers). It balances throughput (batch efficiency) with latency.

#### 4. What business metrics justify streaming cost?
*   **Fraud Prevention:** Stopping $1M loss instantly > cost of Flink cluster.
*   **Inventory:** Preventing "Out of Stock" overselling during Black Friday.
*   **User Experience:** "Next video recommendation" keeps user on platform (Ad revenue).

#### 5. When is streaming **over-engineering**?
*   When the destination is a dashboard looked at once a week.
*   When the source data only arrives once a day (FTP drop).
*   When the team lacks operational maturity to carry pagers for 24/7 stream failures.

---

## 2️⃣ End-to-End Pipeline Design (Batch)

#### 6. Design a **daily analytics pipeline** from source → dashboard.
**Architecture:**
1.  **Ingest:** AWS Glue / Airbyte pulls from SQL/API to S3 (Bronze/Raw). Format: JSON/CSV.
2.  **Clean:** Spark Job reads Bronze, dedupes, casts types, writes to S3 (Silver). Format: Parquet/Delta.
3.  **Agg:** Spark Job reads Silver, joins Dim tables, groups by KPIs, writes to S3 (Gold).
4.  **Serve:** Redshift `COPY` from Gold.
5.  **Viz:** Tableau connects to Redshift.
6.  **Orch:** Airflow schedules dependencies.

#### 7. How do you handle **late-arriving data** in batch systems?
*   **Lookback:** The job for Day X runs on Day X+1, but reads input data from `[Day X-1, Day X]`.
*   **Partitioning:** Data lands in `event_date` folders. If data for `2023-01-01` arrives on `2023-01-05`, it goes into the `2023-01-01` folder.
*   **Reprocessing:** You must detect that the old partition changed and re-trigger the job for that day.

#### 8. How do you design **re-runnable & idempotent batch pipelines**?
**Pattern:** `Overwrite` Strategy.
*   **Not:** `INSERT INTO target...` (Duplicates data on re-run).
*   **Yes:** `INSERT OVERWRITE target PARTITION (date='2023-01-01')...`
*   No matter how many times you run, the partition contains only the latest valid calculation.

#### 9. How do you support **backfills** without impacting daily jobs?
*   **Parameterize:** The job should take `start_date` and `end_date` as arguments.
*   **Separation:** Run backfills on a separate queue/cluster so they don't starve the daily SLA critical path.
*   **Dynamic Partitioning:** Ensure the job writes strictly to the partition implied by the data, not "current execution time".

#### 10. How do you version batch logic safely?
*   **Git:** Code versioning.
*   **Data Versioning:** (Iceberg/Delta Time Travel).
*   **Immutable Deploy:** Don't overwrite `job.py`. Deploy `job_v2.py`.
*   **Blue/Green:** Write v2 output to a new table `sales_v2`. Verify. Then swap view `sales` to point to `sales_v2`.

---

## 3️⃣ End-to-End Pipeline Design (Streaming)

#### 11. Design a **real-time event ingestion system**.
**Architecture:**
1.  **Producer:** App sends event to **API Gateway**.
2.  **Buffer:** API Gateway pushes to **Kinesis/Kafka** (Absorbs spikes).
3.  **Process:** **Flink/Spark Streaming** reads buffer, enriches (joins with Redis), validates.
4.  **Sink:** Writes to **TimescaleDB** (for dashboards) and **S3 Firehose** (for archival).

#### 12. How do you guarantee **exactly-once semantics**?
Requires end-to-end cooperation:
1.  **Source:** Must be replayable (Kafka).
2.  **Processor:** Must check point offsets.
3.  **Sink:** Must be Idempotent (Upsert) -OR- Transactional (Kafka Transactions).
*   *Easier Path:* Achieve "Effectively Exactly Once" by using At-Least-Once delivery + Idempotent Upserts in DB.

#### 13. Event time vs processing time — design implications.
*   **Windowing:** If you calculate "Revenue per Hour", use Event Time.
*   **Late Data:** If data for 9:00 arrives at 9:15, Event Time logic places it in the 9:00 bucket correctly. Processing Time would incorrectly place it in 9:15.

#### 14. How do you handle **out-of-order events**?
**Stateful Buffering:** The stream processor holds a memory buffer (e.g., RocksDB state). It waits for a specific watermark period to re-sequence events before emitting the result.

#### 15. How do you evolve schema in streaming pipelines?
**Schema Registry (Confluent/AWS Glue).**
*   Producer checks registry before sending.
*   Consumer checks registry to deserialize.
*   *Compatibility:* Enforce "Backward Compatibility" (Reader can read old and new data). If a breaking change is needed, build a new topic/pipeline (v2).

---

## 4️⃣ Hybrid (Lambda / Kappa / Modern)

#### 16. Lambda architecture — pros & cons.
*   **Design:** Parallel Speed Layer (Stream) + Batch Layer (Hadoop). Results merged at query time.
*   **Pro:** Batch provides perfect accuracy/correction. Stream provides low latency.
*   **Con:** **Two Codebases**. Logic must be implemented twice (Java/Scala for Flink, SQL/Python for Batch). Operational nightmare.

#### 17. Kappa architecture — when does it break down?
*   **Design:** Everything is a stream. History is just a "really long stream".
*   **Breakage:** Replaying 5 years of history through a streaming engine (like Flink) is often much slower and costlier than running a massively parallel Spark Batch job.

#### 18. Why most companies use **hybrid architectures**.
They use **Unified Engines** (Spark Structured Streaming / Databricks Delta / Flink).
*   Write logic once.
*   Run it in "Streaming Mode" for live data.
*   Run it in "Batch Mode" (Trigger=AvailableNow) for backfills.

#### 19. How do you reconcile batch and streaming results?
**Medallion Architecture.**
*   Stream writes to "Real-time Delta Table".
*   Batch writes to "Historical Delta Table".
*   View `Union`s them.
*   Periodically, Batch overwrites/corrects the Real-time records once data settles.

#### 20. How do you avoid double counting?
**Deduplication:**
*   Assign unique `event_id` at source.
*   Use a KV store (Dynamo/Redis) to track `processed_ids` with a TTL (Time To Live).
*   Discard if `event_id` exists.
