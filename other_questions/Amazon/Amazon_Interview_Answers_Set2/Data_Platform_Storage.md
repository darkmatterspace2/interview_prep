# Data Engineering System Design - Data Platform & Storage

## 🔟 Data Lake & Storage Design

#### 46. Data lake vs data warehouse — decision points.
*   **Data Lake (S3/ADLS):** Unstructured/Semi-structured data. Schema-on-Read. Cheaper storage. ML/Data Science workloads.
*   **Data Warehouse (Snowflake/Redshift):** Structured data. Schema-on-Write. ACID transactions. Best for SQL Analytics/BI.
*   **Lakehouse:** The modern convergence (Delta Lake/Iceberg) bringing ACID and SQL performance to the Lake.

#### 47. Why data lakes fail in practice.
**Data Swamps.**
*   Dump everything with no governance/metadata.
*   No one knows what data exists, its quality, or ownership.
*   Poor query performance (Small files, unpartitioned).

#### 48. Schema-on-read vs schema-on-write.
*   **Write:** Enforce rules on ingestion. Clean data. (Warehouse). *Pro: Fast Reads.*
*   **Read:** Dump raw. Parse when querying. (Lake). *Pro: Fast Writes, Flexibility.*

#### 49. Open table formats — Iceberg / Delta / Hudi — why?
They bring database features to files in S3:
1.  **ACID Transactions:** No partial writes.
2.  **Time Travel:** Query data "as of yesterday".
3.  **Schema Evolution:** Add columns safely.
4.  **Performance:** Metadata skipping (Min/Max index) allows skipping file reads.

#### 50. ACID on data lakes — when needed?
*   **GDPR/CCPA:** "Right to be Forgotten" requires updating/deleting specific user rows in petabytes of logs. Hard on plain Parquet; easy with Delta Lake `DELETE`.
*   **Concurrent Writes:** Streaming ingestion + Batch compaction writing to same table simultaneously.

---

## 1️⃣1️⃣ Medallion Architecture (Bronze / Silver / Gold)

#### 51. Why medallion architecture exists.
To organize data quality progression. It separates concerns: Ingestion vs Cleaning vs Aggregation.

#### 52. What belongs in Bronze vs Silver vs Gold?
*   **Bronze (Raw):** Exact copy of source. History preserved. No transformations.
*   **Silver (Cleansed):** Deduped, typed (String -> Date), clean names, joined with keys. "Source of Truth".
*   **Gold (Curated):** Aggregated metrics (Star Schema). Ready for BI/Dashboarding.

#### 53. Where should business logic live?
Ideally in the **Silver -> Gold** transformation.
*   Bronze -> Silver should be technical cleaning (generic).
*   Gold reflects business definitions (e.g., "What defines a Churned customer?").

#### 54. How do you handle PII across layers?
*   **Bronze:** Encrypt or restricted access.
*   **Silver:** Mask/Tokenize PII immediately.
*   **Gold:** No PII. Aggregated data only.

#### 55. When medallion becomes overkill.
For simple prototypes or when data is already clean (e.g., from internal trusted API). A "Single Layer" approach is fine for MVP.

---

## 1️⃣2️⃣ Data Quality & Observability

#### 56. How do you detect bad data early?
**Shift Left.**
*   Validate at the **Producer** (Schema Registry).
*   Validate at **Ingestion** (Bronze Stage). "Great Expectations" operator in Airflow before processing.

#### 57. Data quality checks vs cost.
*   **Row-by-row checks:** Expensive (Checking generic regex on every string).
*   **Aggregate checks:** Cheap (Is `count(*)` within 10% of yesterday? Is `null_count` > 0?).
*   *Strategy:* Heavy checks on small/critical data. Light checks on massive logs.

#### 58. Metrics you monitor for pipelines.
*   **Freshness:** (Last Updated Time).
*   **Volume:** (Rows In vs Rows Out).
*   **Schema:** (Unexpected Column Change).
*   **Distribution:** (Did `Avg_Price` jump from $50 to $5000?).

#### 59. Data observability vs traditional monitoring.
*   **Monitoring:** "Is the server up?" / "Did the Spark job fail?" (Infrastructure).
*   **Observability:** "Is the data correct?" / "Why did revenue drop?" (Data Content).

#### 60. Alerting strategy to avoid noise.
*   **Sev 1:** Pipeline Down / Data Missing. (Wake up).
*   **Sev 2:** Latency Drift / Mild Quality Issue. (Ticket).
*   **Sev 3:** Info.
*   *Group Alerts:* "Pipeline X Quality Issue" (Don't email for every bad row).

---

## 1️⃣3️⃣ Schema & Contract Management

#### 61. Producer vs consumer schema ownership.
**Contract:** The Producer owns the contract. They must *guarantee* structure.
*   Ideally, consumers define what they *need*, and producers ensure they don't break that (Consumer-Driven Contracts).

#### 62. Schema registry — why needed?
Decouples producers and consumers. Storing the schema centrally (Avro) prevents sending schema overhead in every message and blocks incompatible changes.

#### 63. Breaking vs non-breaking schema changes.
*   **Non-breaking (Forward Compatible):** Adding an optional field. Old consumers ignore it.
*   **Breaking:** Renaming a field. Changing Type (Int -> String). Deleting a required field.

#### 64. Versioning strategies.
*   **Topic/Table Versioning:** `orders_v1`, `orders_v2`.
*   Dual-write during migration (Producer writes to both, Consumers migrate, Old topic deprecated).

#### 65. Contract testing for data pipelines.
Integration tests in CI/CD.
*   The producer pipeline runs against a mock consumer expecting strict schema.
*   If producer changes schema, test fails build.

---

## 1️⃣4️⃣ Visualization & Consumption Layer

#### 66. OLAP vs OLTP — why it matters for BI.
*   **OLTP (Postgres):** Row-oriented. Good for looking up one user. Slow for "Sum of all sales".
*   **OLAP (Redshift/Snowflake):** Column-oriented. Good for "Sum of all sales".
*   *Design:* BI sits on OLAP. API sits on OLTP.

#### 67. Pre-aggregation vs real-time queries.
*   **Pre-agg (Gold Layer):** `Daily_Sales` table. Dashboard reads 365 rows. Instant.
*   **Real-time:** Dashboard queries 1 Billion rows of raw logs. Slow, expensive.
*   *Rule:* Always pre-aggregate for static dashboards.

#### 68. Serving layer design for dashboards.
*   **High Concurrency:** If 10,000 users view dashboard, Redshift might choke (Queueing).
*   **Solution:** Push aggregated data to **Postgres** (RDS) or **Elasticsearch** or a **BI Extract** (Tableau Hyper) for serving high concurrency.

#### 69. Caching strategies for analytics.
*   **Tool Level:** BI Tool (Tableau) caches query result for X minutes.
*   **DB Level:** Redshift Result Cache.
*   **App Level:** Redis cache for API responses.

#### 70. Data freshness vs query cost trade-offs.
*   "Real-time" BI is expensive (No caching, constant compute).
*   "N-1 Day" BI is cheap (Run batch once, cache forever).
*   *Negotiate:* Does the executive decision change if they see data from 1 hour ago vs 1 minute ago? Usually no.
