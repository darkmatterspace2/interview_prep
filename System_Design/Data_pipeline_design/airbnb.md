# Airbnb Data Engineering System Design

## 1. Scenario
Airbnb needs to process daily bookings, listings, and user interactions to generate business dashboards (Revenue, Occupancy Rates) and power Data Science models.

## 2. Requirements
*   **Batch Processing**: Most metrics (Revenue) are calculated daily (T-1).
*   **Data Quality**: "Gold" tables must be accurate. Bad data should stop the pipeline.
*   **Backfill**: Ability to re-process historical data if logic changes.
*   **Evolution**: Schema evolution must be handled.

## 3. Architecture: The "Airflow" Pattern

### Components
1.  **Sources**:
    *   **MySQL (RDS)**: Production DB (Listings, Bookings).
    *   **Event Logs**: Thrift/JSON events from web servers.
2.  **Ingestion**:
    *   **Sqoop/DMS**: Daily snapshot of MySQL tables -> S3 (Landing Zone).
3.  **Storage (Data Lake)**: S3 (Parquet format) partitioned by `ds` (Datestamp).
4.  **Compute**: Apache Spark (EMR/Databricks) for transformations.
5.  **Orchestration**: **Apache Airflow**.

## 4. Pipeline Steps (DAG Design)

### The "Gold" Dashboard Pipeline
1.  **Sensor**: Wait for `listings_partition_2024-01-01` to arrive in S3.
2.  **Data Quality Check (Bronze)**:
    *   Run *Great Expectations* or simple SQL check.
    *   `ASSERT count(*) > 0`
    *   `ASSERT price > 0`
3.  **Transformation (Bronze -> Silver)**:
    *   Spark Job: Join `Bookings` with `Listings`.
    *   De-duplicate records.
    *   Standardize currency (USD conversion).
4.  **Transformation (Silver -> Gold)**:
    *   Aggregate: `SELECT sum(revenue) GROUP BY city`.
5.  **Publish**:
    *   Write to **Druid/Presto** for low-latency dashboarding.
    *   Or write to **Redshift/Snowflake** for BI analysts.

## 5. Deep Dive: Data Quality & Anomaly Detection
Airbnb created "Anomalies" detection features in Airflow.
*   **Logic**: If today's row count is 50% less than the 7-day average, send `SLACK_ALERT` and PAUSE the pipeline.
*   **Partitioning**: Hive-style partitioning `s3://bucket/table/ds=YYYY-MM-DD/`. This allows atomic swaps and easy backfills.
