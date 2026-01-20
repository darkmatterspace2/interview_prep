# Data Engineering System Design Interview Questions
*Mid to Staff Level*

A comprehensive guide to designing scalable data platforms, covering architecture, streaming, and operational excellence.

---

## Table of Contents
1. [Architectural Patterns](#architectural-patterns)
2. [Streaming & Real-Time](#streaming--real-time)
3. [Data Lakehouse Design](#data-lakehouse-design)
4. [Operations & Handling Failures](#operations--handling-failures)
5. [Scenario: Rate Limiting & Aggregation](#scenario-rate-limiting--aggregation)

---

## Architectural Patterns

### 1. Lambda vs Kappa Architecture
**Q:** Compare Lambda and Kappa architectures. When would you use which?
**A:**
*   **Lambda:**
    *   *Design:* Two separate layers: **Batch Layer** (Master dataset, high latency, high accuracy) and **Speed Layer** (Real-time, low latency, approximation). Results are merged in the Serving Layer.
    *   *Pros:* Fault tolerance (Batch can fix Speed layer errors), separates concerns.
    *   *Cons:* Maintaining two codebases (Batch logic + Streaming logic) is complex (`Complexity = N * 2`).
*   **Kappa:**
    *   *Design:* Everything is a stream. The Batch layer is removed. History is processed by re-playing the stream.
    *   *Pros:* Single codebase. Simpler architecture.
    *   *Cons:* Requires strict ordering and immutable logs (Kafka) with long retention.
    *   *Trend:* Modern tools (Spark Structured Streaming, Flink, Databricks Delta) favor Kappa/Lakehouse models where batch and stream APIs are unified.

### 2. Designing a Data Warehouse from Scratch
**Q:** Design a DW for an E-commerce company. What layers do you create?
**A:**
1.  **Landing Zone (Raw):** Immutable files (JSON/CSV) as received from Source. Partitioned by `Source/Date`.
2.  **Staging Zone (Clean):** Deduplicated, validated types, Parquet/Delta format.
3.  **Integration Zone (Silver/Core):** Conformed dimensions, Enriched facts. 3NF or Data Vault modeling.
4.  **Mart Zone (Gold/Serving):** Aggregated Star Schemas (Fact/Dim) optimized for BI (PowerBI/Tableau).
5.  **Metadata Layer:** Data Catalog (Amundsen/Datahub) + Quality Checks (Great Expectations).

---

## Streaming & Real-Time

### 3. Real-Time Dashboarding Pipeline
**Q:** Design a system to count "Active Users per Minute" for a game with 10M concurrent users.
**A:**
*   **Ingestion:** Game Servers -> Load Balancer -> **Kafka** (Partition by UserID to ensure efficient scaling).
*   **Processing:** **Apache Flink** or **Spark Streaming**.
    *   Use *Tumbling Window* (1 minute).
    *   Use *Watermarking* to handle late-arriving data (e.g., wait 30 seconds).
    *   *State:* Maintain user state in memory (RocksDB) to handle "Active" definition.
*   **Storage:** Write aggregated results (Time, Count) to a fast Time-Series DB (**TimescaleDB** / **Druid**) or **Redis** for caching.
*   **Serving:** Grafana or Custom React App polls Redis/Druid.

### 4. Handling Late Data
**Q:** You are calculating daily revenue. A transaction from "Yesterday" arrives "Today" due to a system retry. How do you handle it?
**A:**
*   **Option 1 (Streaming):** Watermarking. If it's too late (outside watermark), drop it or send to "Dead Letter Queue".
*   **Option 2 (Batch - Idempotency):**
    *   Store data in partitions based on *Event Time*, not *Processing Time*.
    *   The late record lands in `Date=Yesterday` partition.
    *   Re-run the aggregation job for `Date=Yesterday` to include the new record (Backfill/Restatement).

---

## Data Lakehouse Design

### 5. Schema Evolution Strategy
**Q:** Upstream API adds a new column `discount_code`. How should your pipeline handle it without breaking?
**A:**
*   **Bronze (Raw):** Use `PERMISSIVE` mode or JSON columns to ingest *everything* without failing. Retain full fidelity.
*   **Silver (Curated):**
    *   *Explicit:* Pipeline fails, alerts engineer to update schema (Strict).
    *   *Automatic:* Enable Schema Evolution (Delta Lake `mergeSchema`).
*   **Downstream Protection:** Use Views on top of Silver tables to expose only "Contracted" columns, protecting BI dashboards from unexpected schema changes.

### 6. Small File Problem Solution
**Q:** Your streaming job creates 10,000 tiny KB files every hour in the Data Lake. Query perf is dying. Fix it.
**A:**
*   **Immediate Fix:** Run a scheduled **Compaction Job** (e.g., `OPTIMIZE` in Delta / `repartition` in Spark) every night to merge files into 1GB chunks.
*   **Root Cause Fix:**
    *   Increase `trigger` interval (Processing time 1 min -> 5 min).
    *   Use **Auto Compaction** / **Optimized Writes** features if available (Databricks/Snowflake).

---

## Operations & Handling Failures

### 7. Backfilling Historical Data
**Q:** You found a bug in the logic for "User Subscription Status" calculating active users incorrectly for the last 6 months. How do you fix it?
**A:**
1.  **Fix Code:** Deploy corrected logic.
2.  **Isolate:** Ensure the new code handles current incoming data correctly.
3.  **Backfill Strategy:**
    *   *Reverse Order:* Reprocess from today backwards? Or *Forward Order*? (Depends on state dependency).
    *   *Parallelism:* Spin up a separate "Backfill Cluster". Process months in parallel if independent.
    *   *Write Mode:* Use `INSERT OVERWRITE` on partitions to safely replace old bad data with new good data.

### 8. Data Quality Monitoring (Circuit Breakers)
**Q:** How do you prevent "Bad Data" from ruining your CEO's dashboard?
**A:**
Implement **Write-Audit-Publish (WAP)** pattern:
1.  **Write:** ETL writes data to a *Staging/Branch* table (hidden).
2.  **Audit:** Run automated Quality Checks (e.g., `revenue > 0`, `null_count < 1%`).
3.  **Publish:**
    *   *Pass:* Atomically swap/merge Staging to Production.
    *   *Fail:* Alert Engineering. Do NOT update Production. Dashboard shows "Stale" but "Correct" data (better than fresh garbage).

---

## Scenario: Rate Limiting & Aggregation

### 9. Deduplication at Scale
**Q:** You receive 50k events/sec. 20% are duplicates. Deduplicate them efficiently.
**A:**
*   **Short Window (10 min):** Deduplicate in Streaming State (Spark `dropDuplicates("id")` with watermark). Very fast.
*   **Global (All Time):** Cannot keep all History in memory.
    *   *Bloom Filter:* Probabilistically check if ID exists.
    *   *Lookup Table:* Check against a high-speed KV store (DynamoDB/Cassandra) if ID was seen.
    *   *Batch Reconciliation:* Let streams handle short-term dupes; run a nightly batch job to remove long-term dupes.

### 10. GDPR "Right to be Forgotten"
**Q:** A user requests deletion. Their data is in 5000 parquet files in S3. How do you delete it efficiently?
**A:**
*   **Naive:** Read all 5000 files -> Filter -> Write 5000 files. (Too expensive).
*   **Lakehouse (Delta/Hudi):** Supports `DELETE FROM table WHERE user_id = X`. Uses metadata to identifying only the specific files containing that User ID, rewrites only those files (e.g., 5 files), and marks old ones as deleted.
*   **Encryption approach:** Store user PII with a unique encryption key. Throw away the *Key* to "Crypto-shred" the data without rewriting files.
