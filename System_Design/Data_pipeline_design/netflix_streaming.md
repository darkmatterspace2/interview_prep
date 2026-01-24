# Netflix Data Engineering Design

## 1. Scenario
Netflix ("Keystone" Platform) handles routing of data events from every device (TV, Mobile) to sinks (S3, Elastic, Kafka) for billing, personalization, and operational monitoring.

## 2. Requirements
*   **Routing**: Dynamic routing. "Billings logs go to S3 Bucket A", "Error logs go to Elasticsearch".
*   **Scale**: 500 Billion events/day.
*   **Partitioning**: Efficient lake storage (Iceberg).

## 3. Architecture: The Keystone Pipeline

### Components
1.  **Fronting**: REST Proxy / DG (Data Gateway) accepts events.
2.  **Messaging**: **Kafka** (Partitioned by UserID or DeviceID).
3.  **Routing**: **Flink / Kafka Connect**.
    *   Projector: Filters/Masks PII.
    *   Router: Decides destination.
4.  **Data Lake**: S3 + **Apache Iceberg**.
    *   Iceberg provides ACID transactions on S3 (fixes "File-listing" slowness).

## 4. Pipeline Design

### A. The "Play" Event Pipeline
1.  User clicks Play. App sends event `{evtType: "P", movieId: 123, profileId: 456, time: ...}`.
2.  **Ingest**: Kafka Topic `user_interactions`.
3.  **Route 1 (Personalization)**:
    *   Flink job aggregates "Watch Duration".
    *   Writes to Cassandra (Profile Store).
    *   RecSys updates "Continue Watching" list.
4.  **Route 2 (Data Warehouse)**:
    *   Writes parquet files to S3 `s3://warehouse/interaction_logs/date=...`.
    *   Iceberg commits the metadata.

### B. Handling Late Data
*   **Scenario**: User watches offline (Airplane). Mobile uploads logs 5 hours later.
*   **Solution**:
    *   Iceberg handles late-arriving data via hidden partitioning.
    *   Query `SELECT * FROM logs` sees the data immediately after commit, even if it belongs to a past partition.

## 5. Deep Dive: Data Mesh & Standardization
Netflix pioneered "Paved Road" (Platform Engineering).
*   **Genie**: A federated job execution service.
*   **Metacat**: Unified Metadata catalog (Hive + RDS + Teradata).
*   **Audit**: Automate PII detection (Regex for credit cards) in the stream before writing to Lake.
