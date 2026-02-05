# Data Engineering System Design - Operations, Security & Strategy

## 1️⃣5️⃣ Technology Selection — When to Use What

#### 71. CDC vs API ingestion — trade-offs.
*   **CDC (Change Data Capture - Debezium/DMS):** Reads DB logs.
    *   *Pro:* Captures hard deletes. Zero latency. No impact on DB CPU.
    *   *Con:* Exposes internal DB schema to downstream (tighter coupling).
*   **API/Query-based (JDBC poll):** `SELECT * WHERE updated_at > X`.
    *   *Pro:* Decoupled. Simple.
    *   *Con:* Misses hard deletes. Polling adds load.

#### 72. Batch file ingestion vs streaming ingestion.
*   **Batch:** Proven, high throughput (S3 COPY). Good for massive unsorted loads.
*   **Stream:** Complex. Good for low latency.

#### 73. SQL engines vs Spark vs Flink.
*   **SQL (dbt on Snowflake):** Best for transformations *after* data is structured (T in ELT).
*   **Spark:** Best for massive data volume, complex unstructured parsing, ML.
*   **Flink:** Best for low-latency stateful events.

#### 74. When SQL is enough.
90% of the time in the Warehouse (Gold Layer). If logic is expressible in SQL (Joins/Aggs) and data fits in standard DW, don't use Spark/Python.

#### 75. Object storage vs HDFS.
*   **Object Storage (S3):** Decoupled Compute/Storage. Infinite Scale. Cheaper. *Winner in cloud.*
*   **HDFS:** Data locality (Compute moves to data). Lower latency for file operations. *Winner in on-prem.*

#### 76. Columnar vs row-based formats.
*   **Columnar (Parquet):** Analytics (Read few columns, many rows).
*   **Row (Avro/CSV):** Transactional/Streaming (Write whole row typically).

#### 77. Data warehouse vs search engine (e.g., Elasticsearch).
*   **Warehouse:** Aggregations, SQL joins.
*   **Search Engine:** Full-text search, Logging, auto-complete, high-concurrency simple filtering.

#### 78. When to use NoSQL for analytics.
Rarely for *complex* analytics (Joins are hard).
Use for **Serving Analytics** (e.g., User Profile, Pre-calculated stats) where access pattern is "Get by ID" or simple range.

---

## 1️⃣6️⃣ Security, Governance & Compliance

#### 79. How do you design for data access control?
**RBAC (Role Based Access Control).**
*   Create Roles: `DataEng`, `DataSci`, `Marketing`.
*   Grant permissions to Roles, not Users.
*   Use IAM for S3, Table Grants for Warehouse.

#### 80. Column-level security vs row-level security.
*   **Column:** Mask `SSN` column for Marketing role.
*   **Row:** Sales rep for `North` region can only see rows where `region='North'`.

#### 81. Auditability in data pipelines.
*   **Log everything:** "Who ran it?", "When?", "What data was touched?".
*   **Lineage:** Ability to trace a dashboard number back to the raw S3 file source.

#### 82. Data retention & deletion policies.
*   **Lifecycle Policies:** S3 move to Glacier after 1 year. Delete after 7 years (Tax/Audit limit).
*   **Cost:** Don't store useless logs forever.

#### 83. Handling GDPR / PII in pipelines.
**Tokenization.**
*   Swap `name="John"` with `token="xyz123"` at ingestion.
*   Store mapping in a secured Vault.
*   Pipeline processes `xyz123`.
*   Only authorized users can detokenize at the end.
*   *Deletion:* Just delete the key in the Vault; `xyz123` becomes orphaned/useless (Crypto-shredding).

---

## 1️⃣7️⃣ Cost & Scale Trade-offs

#### 84. Cost drivers in batch pipelines.
*   **Scanning:** Reading too much data (Partitioning helps).
*   **Shuffle:** Moving data across network (Broadcasting helps).
*   **Uptime:** Keeping clusters running when idle.

#### 85. Cost drivers in streaming systems.
*   **24/7 Compute:** You pay even if 0 messages arrive.
*   **State Storage:** storing massive windows in memory/disk.

#### 86. Compute vs storage trade-offs.
*   Storage is cheap. Compute is expensive.
*   *Strategy:* Materialize more tables (Increase Storage) to avoid re-computing complex joins (Decrease Compute).

#### 87. Auto-scaling — pitfalls.
*   **Thrashing:** Scale up -> Job finishes -> Scale down -> New job starts -> Scale up. (Wastes boot time).
*   **Solution:** Minimum capacity + cooldown periods.

#### 88. When performance tuning beats scaling.
When code is **inefficient** (e.g., Python loop instead of Pandas vectorization). Scaling N hardware won't fix O(N^2) complexity. Optimizing code (O(N)) is free performance.

---

## 1️⃣8️⃣ Failure Scenarios

#### 89. Source system sends duplicate data.
*   Design pipeline with **Deduplication step** (Windowed distinct or Upsert).
*   Don't trust source to be unique.

#### 90. Downstream BI reports wrong numbers.
*   **Root Cause Analysis:** Check Data Freshness -> Check Aggregation Logic -> Check Source Quality.
*   *Fix:* Implement Data Quality tests in the Gold layer to catch this before BI sees it.

#### 91. Streaming lag keeps increasing.
*   Input Rate > Processing Rate.
*   *Fix:* Add partitions (Kinesis Shards) + Add Consumers (Spark Executors). Optimize per-event logic.

#### 92. Batch job misses SLA.
*   *Fix:* Alert immediately. Check for skew or delayed upstream data. Communicate with stakeholders.

#### 93. Schema change breaks pipeline.
*   *Prevention:* Schema Registry.
*   *Fix:* Update code to handle new schema. Backfill if necessary.

---

## 1️⃣9️⃣ Design Judgment & Philosophy

#### 94. How do you avoid over-engineering?
**YAGNI (You Ain't Gonna Need It).**
*   Don't build a generic framework for 1 job.
*   Don't use Flink when a cron SQL job works.
*   Start simple, evolve complex.

#### 95. When do you choose simplicity over perfection?
Almost always. Simple systems are easier to debug at 3 AM. Complex optimized systems are fragile.

#### 96. How do you design for future scale?
*   **Decouple:** Compute separate from Storage.
*   **Partitioning:** Choose right keys now (hard to change later).
*   **Horizontal Scale:** Ensure implementation allows adding nodes (e.g., don't do single-threaded processing).

#### 97. Build vs buy — how do you decide?
*   **Core Competency?** Is building a Distributed Queue your business value? No -> Use Kafka/SQS.
*   **Cost:** "Free" Open Source requires expensive engineering time to maintain. Managed services cost money but save time.

#### 98. How do you sunset old pipelines safely?
*   "Scream Test": Turn it off for 1 hour. See who yells. (Risky).
*   **Better:** Trace lineage -> Identify consumers -> Migrate them -> Announce Deprecation -> Turn off.

---

## 2️⃣0️⃣ Interview-Level Open Questions

#### 99. Design a **global-scale analytics platform**.
*   **Ingest:** Edge locations (CloudFront/Global Accelerator) -> Local Region S3.
*   **Replicate:** CRR to Central Analytics Region.
*   **Process:** EMR/Glue in Central Region.
*   **Serve:** Redshift Global or Data Mesh (Federated query across regions).

#### 100. Design a **transportation / logistics data platform**.
*   **Real-time:** IoT telematics (MQTT) -> Kinesis -> Flink (Geofencing/ETA) -> Redis.
*   **Optimization:** Batch S3 history -> SageMaker (Route Opt model) -> API.
*   **BI:** Redshift for "Cost per Mile" reporting.
