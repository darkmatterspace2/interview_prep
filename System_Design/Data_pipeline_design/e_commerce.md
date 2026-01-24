# E-Commerce Data Engineering Design

## 1. Scenario
Real-time inventory management and recommendation personalization based on user browsing history.

## 2. Requirements
*   **Latency**: Inventory updates < 10 seconds. Recommendations < 5 minutes.
*   **Change Capture**: Capture every state change (Insert/Update/Delete) from the Order DB.
*   **Stream & Batch**: Unified storage for historical analysis (Lambda/Kappa).

## 3. Architecture: CDC & Delta Lake

### Architecture Flow
`PostgreSQL (Orders)` --> `Debezium (CDC)` --> `Kafka` --> `Spark Streaming / Flink` --> `Delta Lake (S3)` --> `Redis (Real-time View)`


### Components
1.  **Source Database**: PostgreSQL (Orders, Inventory).
2.  **CDC Tool**: **Debezium**.
    *   Reads Postgres Write-Ahead Log (WAL).
    *   Publishes changes to Kafka topics `db.orders`, `db.inventory`.
3.  **Streaming Platform**: **Apache Kafka**.
4.  **Stream Processing**: **Spark Structured Streaming** or **Flink**.
5.  **Sink/Storage**: **Delta Lake** (ACID on S3).

## 4. Pipeline Design

### A. Real-Time Inventory (CDC)
1.  **Capture**: User buys item. DB updates `qty=99`.
2.  **Ingest**: Debezium sends `{op: "u", before: {qty:100}, after: {qty:99}}` to Kafka.
3.  **Process**:
    *   Spark Stream reads Kafka.
    *   Updates "Real-time Stock" Redis cache for the frontend.
    *   triggers "Low Stock Alert" if `qty < threshold`.
4.  **Archive**: Stream writes raw JSON to S3 (Delta Lake) for history.

### B. Clickstream (Recommendations)
1.  **Source**: JS Tracker sends events (Click, View, AddToCart) to API Gateway.
2.  **Ingest**: Firehose/Kafka.
3.  **Processing**:
    *   Sessionize events (Window: 30 minutes).
    *   Extract "Interests" (e.g., User viewed "Shoes" 5 times).
    *   Update **User Feature Store** (Cassandra/DynamoDB).
4.  **Serving**: When user visits homepage, RecSys Service queries Feature Store.

## 5. Deep Dive: Schema Evolution in Streams
*   **Problem**: Dev adds `color` column to Postgres. Debezium sends new JSON structure. Spark Job crashes.
*   **Solution**:
    *   **Schema Registry** (Confluent): Enforces Avro schema compatibility.
    *   **Delta Lake Schema Evolution**: `option("mergeSchema", "true")`. Automatically adds the new column to the parquet files.
