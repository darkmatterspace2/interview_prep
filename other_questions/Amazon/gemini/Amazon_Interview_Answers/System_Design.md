# Amazon System Design Interview Questions

## Part 1: Design Concepts

#### 86. Design an end-to-end logistics analytics system.
**Answer:**
*   **Ingest:** API Gateway + Kinesis (for real-time events) & DMS (for DB replication).
*   **Compute:** AWS Glue (ETL) / EMR (Complex Aggregation) / Lambda (Simple transformations).
*   **Storage:**
    *   *Raw:* S3 (Bronze).
    *   *Curated:* S3 (Silver/Gold) in Parquet.
    *   *Warehousing:* Redshift (for high-performance SQL analytics).
*   **Consumption:** QuickSight (BI), API (for external vendors).

#### 87. Design shipment delay prediction pipeline.
**Answer:**
*   **Training:** Prepare historical data (S3) -> SageMaker (Train Model: XGBoost).
*   **Inference:**
    *   *Real-time:* Kinesis -> Lambda (Call SageMaker Endpoint) -> Stamp "Predicted Delay" on event -> Store.
*   **Feedback Loop:** Compare Prediction vs Actual Delivery Date to retrain model weekly.

#### 88. Design real-time dashboard for operations team.
**Answer:**
*   **Requirement:** Low latency (< 1 min).
*   **Architecture:**
    *   Source -> Kinesis Data Streams -> Kinesis Data Analytics (Flink) [Aggregations like "Avg Delay per Region"] -> Timestream (Time-series DB) or OpenSearch -> Grafana/QuickSight.
    *   *Why not Redshift?* Redshift is better for batch/historical. For live operational metrics, Timestream or OpenSearch are faster for indexing and retrieval.

#### 89. Cost vs latency trade-offs.
**Answer:**
*   **Low Latency (Real-time):** Expensive. Requires constant compute (Kinesis shards, Flink cluster).
*   **High Latency (Batch):** Cheap. Pay only when job runs. S3 is cheaper than Kinesis.
*   *Amazon Principle:* Frugality. If business doesn't *need* real-time, build batch.

#### 90. Multi-region data ingestion strategy.
**Answer:**
*   **Producers:** Write to local region S3/Kinesis (lower latency, reliability).
*   **Replication:** Use **S3 Cross-Region Replication (CRR)** to centralize data into a master region for global analytics.
*   **Compliance:** Ensure PII stays in region (GDPR) if required by filtering before replication.

---

## Part 2: System Design Scenarios (Bar Raiser)

#### Scenario: Real-time Dashboard for Operations Managers
**The Prompt:** "Design a real-time dashboard for Operations Managers to see where all Amazon trucks are currently located and if they are delayed."

**Answer Breakdown:**

1.  **Requirements Clarification:**
    *   *Scale:* 50k trucks? Updates every 30 seconds?
    *   *Consumer:* Ops Managers (Need map view + alerts).

2.  **High-Level Architecture:**
    *   **Trucks (IoT Devices):** Send GPS coordinates + Status.
    *   **Ingestion:** AWS IoT Core (MQTT) or Kinesis Data Streams.
    *   **Processing (Stream):** Kinesis Data Analytics (Flink).
        *   *Logic:* Join stream with "Planned Route" (stored in DynamoDB/ElastiCache).
        *   *Calculation:* `If Current_Loc != Expected_Loc AND Time > Planned_Time THEN Status = DELAYED`.
    *   **Storage (Hot):** DynamoDB (Current state of every truck). Access pattern: `GetTruck(ID)` or `GetTrucksInRegion(Region)`. (Geo-hashing for map queries).
    *   **Visualization:** WebSocket API to push updates to Frontend Map, or Polling from AppSync/GraphQL.

3.  **Data Quality:**
    *   *Question:* How to handle malformed data?
    *   *Answer:* Schema Validation at Ingestion (Lambda/Schema Registry). Bad records -> Dead Letter Queue (S3) for analysis. Do NOT stop the pipe.

4.  **Backfilling (The Bug Fix):**
    *   *Question:* Bug in cost calculation. Fix history while new data flows.
    *   *Answer:*
        *   Build a separate "Repair Pipeline" (Batch).
        *   Read historical raw data -> Apply Fixed Logic -> Overwrite target tables (Idempotent write).
        *   Does not interfere with the live streaming pipeline.
