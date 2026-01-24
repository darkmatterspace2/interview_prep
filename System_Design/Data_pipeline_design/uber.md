# Uber Data Engineering Design

## 1. Scenario
Uber manages "Trip" audits, billing updates, and rider history. A trip has a lifecycle (Request -> Driver Arrived -> Start -> End -> Tip Added). The "Tip Added" event happens hours after the trip ends.

## 2. Requirements
*   **Upserts (Update/Insert)**: We must update the "Trip" record in the Data Lake when a Tip arrives. Standard S3 (Parquet) is immutable (Write Once).
*   **Incremental Processing**: Downstream jobs should only process "New/Changed" trips, not scan the whole table.

## 3. Architecture: Apache Hudi & Kappa

### Architecture Flow
`Trip Events` --> `Kafka` --> `Hudi (Kappa Upserts)` --> `HDFS/S3` --> `Hive / Presto (Serving)`


### Components
1.  **Ingestion**: Kafka.
2.  **Lake Format**: **Apache Hudi** (Hadoop Upsert Delete and Incremental).
    *   Enables `UPDATE` on S3.
3.  **Processing**: Spark / Flink.
4.  **Serving**: Presto / Hive.

## 4. Pipeline Design

### A. The Trip Lifecycle (Upsert Problem)
1.  **Event 1 (Trip End)**: `{trip_id: 100, status: "ENDED", fare: $20}`.
    *   Hudi inserts new record.
2.  **Event 2 (Tip Added)**: `{trip_id: 100, tip: $5, total: $25}`.
    *   **Standard Lake**: Would require rewriting the whole partition or creating a duplicate row.
    *   **Hudi**: Locates the file containing `trip_id: 100` and creates a new version (Copy-On-Write or Merge-On-Read).
3.  **Query**: `SELECT * FROM trips WHERE trip_id=100` returns the latest state ($25).

### B. Incremental ETL
*   Daily Revenue Report needs to process only today's trips + yesterday's trips that got adjusted today.
*   **Hudi functionality**: `hoodie_table.incremental_query(start_timestamp)`.
*   Spark Job reads *only* changed rows. No full table scan.

## 5. Deep Dive: Hudi Indexing
*   How does Hudi know which file contains `trip_id: 100`?
    *   **Bloom Filter Index**: Kept in the footer of parquet files. Fast check "Maybe in this file".
    *   **HBase Index**: External KV store mapping Key -> FileID.
