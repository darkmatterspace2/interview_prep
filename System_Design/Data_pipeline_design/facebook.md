# Facebook Data Engineering Design

## 1. Scenario
Facebook generates Petabytes of logs per hour (Likes, Comments, Scroll depth, Errors). We need to ingest this for Ad-hoc queries, Real-time dashboards, and Abuse detection.

## 2. Requirements
*   **Scale**: Handle Trillions of events/day.
*   **Latency**: Query recent data within seconds.
*   **Storage**: Efficient compression and tiered storage.

## 3. Architecture: The Log Aggregation Pipeline

### Architecture Flow
`App Logs` --> `Scribe (Collector)` --> `Kafka (Buffer)` --> `Druid (Real-time OLAP)` & `HDFS (Batch/Hive)` --> `Superset (Analytics)`


### Components
1.  **Ingestion**: **Scribe** (Facebook's internal log collector, similar to Fluentd).
    *   Agents on every web server push logs to Scribe aggregators.
2.  **Buffer**: **Kafka** (or FB's LogDevice).
    *   Decouples producers from consumers.
    *   Topics: `fb_clicks`, `fb_errors`.
3.  **Real-Time Layer**: **Apache Druid** / **Pinot**.
    *   Consumes from Kafka.
    *   Builds OLAP cubes for sub-second slicing/dicing.
4.  **Batch Layer**: **HDFS / Hive**.
    *   Kafka -> Secor/Gobblin -> HDFS (ORC Format).
    *   Used for daily ETL and heavy ML training.

## 4. Pipeline Design

### A. Real-Time Ad Analytics
*   **Goal**: Advertiser wants to see "Clicks vs Impressions" right now.
*   **Flow**:
    1.  App logs `AdImpression` event.
    2.  Scribe pushes to `ads_stream` Kafka topic.
    3.  **Druid** consumes stream. roll-up enabled (Store sum, not raw rows).
    4.  Advertiser Dashboard queries Druid: `SELECT sum(clicks) FROM ads WHERE advertiser_id=123`.

### B. Graph Processing (Friends Recommendation)
*   **Tool**: **Apache Giraph** (or Spark GraphX).
*   **Flow**:
    1.  Daily snapshot of "Friendship" table (Edge List).
    2.  Run PageRank or Label Propagation algorithm.
    3.  Output "Suggested Friends" to Key-Value Store (RocksDB) for serving.

## 5. Deep Dive: Handling "The Justin Bieber" Partition
*   **Problem**: Data Skew. A celebrity has millions of interactions. One Kafka partition gets flooded, causing lag.
*   **Solution**:
    *   **Salting**: Add a random number `(0-9)` to the partition key for hot keys. Distribution becomes even.
    *   **Partial Aggregation**: Aggregate in memory (Producer side) before sending network packets.
