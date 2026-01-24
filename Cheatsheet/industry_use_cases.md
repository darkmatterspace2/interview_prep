# Industry-Specific Tech Stacks & Use Cases

A guide to understanding *why* certain technologies are preferred in specific sectors, with example pipeline flows.

## 1. Banking & Fintech (Security & Consistency)
**Top Priority**: ACID Compliance, Data Security (PII), Low Latency Fraud Detection.
*   **Preferred Tech**: Oracle/PostgreSQL (Strong transactional support), Kafka (Reliable logs), On-prem HDFS (sometimes required by regulation).

### Use Case: Real-time Fraud Detection
`ATM Transaction` -> `Kafka (Secure Topic)` -> `Apache Flink (Pattern Matching)` -> `Oracle DB (Block Account)` -> `Tableau (Alert Dashboard)`

*   **Why?**
    *   **Flink**: Low latency (<100ms) is critical to stop the card swipe.
    *   **Oracle**: Banks trust its durability and row-locking mechanisms.

## 2. Telecom (Volume & Batch)
**Top Priority**: Handling massive throughput (Call Detail Records - CDRs), Cost-effective long-term storage.
*   **Preferred Tech**: Hadoop/Spark (Batch), NoSQL (HBase/Cassandra), Columnar DBs (Vertica/Sybase IQ).

### Use Case: Daily Billing & Network Quality
`Cell Towers` -> `Flume/FTP` -> `HDFS (Raw Files)` -> `Spark (Optimization/Aggregates)` -> `SAP IQ (Columnar DB)` -> `Power BI`

*   **Why?**
    *   **Spark**: Best for crunching Petabytes of daily logs.
    *   **SAP IQ / Vertica**: Highly optimized for analytical queries on billions of rows (Billing reports).

## 3. Healthcare (Privacy & Unstructured Data)
**Top Priority**: HIPAA Compliance, Handling Images (X-Rays)/Text (Doctor Notes).
*   **Preferred Tech**: Databricks (Delta Lake), Azure Data Lake (HIPAA certified), NLP libraries.

### Use Case: Patient 360 & Diagnosis Prediction
`EHR System (HL7 msgs)` -> `Azure Data Factory` -> `ADLS Gen2 (Bronze)` -> `Databricks (Spark+NLP)` -> `Delta Lake (Gold)` -> `MLflow Model`

*   **Why?**
    *   **Delta Lake**: Supports "Right to be Forgotten" (DELETE specific user data GDPR/HIPAA).
    *   **Unstructured Support**: Spark supports binary files (MRI scans) and text better than a Warehouse like Snowflake.

## 4. Social Media (Relationships & Real-Time)
**Top Priority**: Graph connections, Infinite scale, Global availability.
*   **Preferred Tech**: Graph DB (Neo4j), Wide-column (Cassandra), Real-time stream (Kafka).

### Use Case: "People You May Know"
`User Graph` -> `Graph Processing (Giraph/Spark GraphX)` -> `Cassandra (Pre-computed Recs)` -> `API`

*   **Why?**
    *   **Neo4j**: Native support for query `(User)-[:FRIEND]->(User)`. SQL Joins fail here.
    *   **Cassandra**: Write-heavy. Great for storing feed data replicated globally.

## 5. IoT & Manufacturing (Time Series & High Frequency)
**Top Priority**: High write ingestion (millions of sensors), Time-series compression.
*   **Preferred Tech**: MQTT (Protocol), InfluxDB/TimescaleDB, Kafka.

### Use Case: Predictive Maintenance (Factory)
`Sensor (Vibration)` -> `MQTT` -> `Kafka` -> `InfluxDB` -> `Grafana Dashboard`

*   **Why?**
    *   **MQTT**: Lightweight protocol for small sensors with bad internet.
    *   **InfluxDB**: Specialized for Time-Series. Compresses `timestamp, value` data 100x better than SQL.

## 6. Video Streaming (Blob & CDN)
**Top Priority**: Bandwidth management, Binary storage, Global delivery.
*   **Preferred Tech**: Object Storage (S3), CDN (Akamai/CloudFront), Serverless (Lambda).

### Use Case: Video Transcoding
`Upload` -> `S3 (Trigger)` -> `AWS Lambda (Run Ffmpeg)` -> `S3 (MP4 output)` -> `CDN Origin`

*   **Why?**
    *   **S3**: Infinite scalability for binary files.
    *   **Lambda**: Auto-scales to handle 1 video or 1000 concurrent uploads. No idle servers.

## 7. Retail / E-Commerce (Customer 360)
**Top Priority**: Connecting Silos (Sales, Marketing, Inventory), Analytics.
*   **Preferred Tech**: Snowflake (Data Sharing), dbt (Transformation), Airflow.

### Use Case: Marketing Attribution
`Shopify (Sales)` + `Facebook Ads` + `Google Analytics` -> `Fivetran` -> `Snowflake` -> `dbt` -> `Looker`

*   **Why?**
    *   **Snowflake**: Great for complex joins across different schemas (JSON support).
    *   **dbt**: Allows analysts (SQL users) to build their own pipelines without engineering help.
