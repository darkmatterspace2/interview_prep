# System Design Concepts (Data Engineering Perspective)

## Key Concepts
*   **LLD (Low-Level Design)**
*   **HLD (High-Level Design)**
*   **CAP Theorem**
*   **Load Balancer**
*   **Sharding**
*   **Replication**
*   **Message Queue**
*   **Cache**
*   **Database** (SQL vs NoSQL, columnar vs row-oriented)
*   **Consistent Hashing**
*   **Disaster Recovery**
    *   Latency
    *   Throughput
    *   Availability
    *   Scalability
    *   Reliability
    *   Consistency

---

## Interview Questions

### Beginner Level

1.  **What is the difference between Vertical Scaling and Horizontal Scaling?**
    *   **Answer:** Vertical scaling (scaling up) implies adding more resources (CPU, RAM) to a single machine. Horizontal scaling (scaling out) implies adding more machines to the pool/cluster. Horizontal scaling is generally preferred for distributed data systems (like Hadoop/Spark) for fault tolerance and practically unlimited scale.

2.  **Explain the difference between Batch Processing and Real-Time (Streaming) Processing.**
    *   **Answer:** Batch processing handles large volumes of data differently at scheduled intervals (high latency, high throughput). unique Real-time processing handles data as it arrives (low latency, potentially lower throughput per node but constant processing).

3.  **What is ETL? How does it differ from ELT?**
    *   **Answer:**
        *   **ETL (Extract, Transform, Load):** Data is extracted, transformed in a staging area/engine, and then loaded into the target warehouse. Good for privacy/compliance where raw data shouldn't enter the warehouse.
        *   **ELT (Extract, Load, Transform):** Data is loaded raw into the target (like Snowflake/BigQuery) and transformed using the target's compute. often faster and leveraging the scalability of modern cloud warehouses.

4.  **What is the CAP Theorem?**
    *   **Answer:** It states that a distributed system can only deliver two of three guarantees:
        *   **Consistency:** Every read receives the most recent write or an error.
        *   **Availability:** Every request receives a (non-error) response, without the guarantee that it contains the most recent write.
        *   **Partition Tolerance:** The system continues to operate despite an arbitrary number of messages being dropped or delayed by the network between nodes.

5.  **What is the purpose of a Load Balancer?**
    *   **Answer:** It distributes incoming network traffic across multiple servers to ensure no single server bears too much load. It improves application responsiveness availability and prevents overloading servers.

6.  **What is Data Replication?**
    *   **Answer:** It involves storing the same data on multiple storage devices or nodes. This ensures high availability (if one node fails, data is available elsewhere) and data reliability.

7.  **What is Sharding?**
    *   **Answer:** Sharding is a method of splitting and storing a single logical dataset in multiple databases (or partitions). By distributing the data among multiple machines, a cluster of systems can store larger datasets and handle additional requests.

8.  **What is the difference between SQL and NoSQL databases from a scaling perspective?**
    *   **Answer:** SQL databases are typically vertically scalable (add more power to the box). NoSQL databases are typically horizontally scalable (add more servers to the cluster) and are often built to handle unstructured data.

9.  **What is Latency vs. Throughput?**
    *   **Answer:**
        *   **Latency:** The time it takes to process a single unit of data (time from request to response).
        *   **Throughput:** The amount of data processed within a given time frame (e.g., records per second).

10. **Why would you use a Message Queue (like Kafka/RabbitMQ) in a data pipeline?**
    *   **Answer:** To decouple producers from consumers, handle bursts in data traffic (buffering), ensure data reliability, and allow for asynchronous processing.

### Medium Level

11. **Explain the Lambda Architecture.**
    *   **Answer:** A data-processing architecture designed to handle massive quantities of data by taking advantage of both batch and stream-processing methods. It has three layers:
        *   **Batch Layer:** Manages the master dataset (immutable, append-only) and pre-computes batch views.
        *   **Speed Layer:** Processes recent data in real-time to compensate for high latency of the batch layer.
        *   **Serving Layer:** Indexes the batch and speed views for low-latency ad-hoc queries.

12. **What is the Kappa Architecture and how does it differ from Lambda?**
    *   **Answer:** Kappa Architecture removes the Batch Layer. Everything is treated as a stream. If you need to recompute history, you just replay the stream from the beginning (or a specific offset) with the new logic. It simplifies the code base (one codebase for both real-time and historical).

13. **What is Idempotency and why is it important in data pipelines?**
    *   **Answer:** An operation is idempotent if applying it multiple times has the same effect as applying it once. In data engineering, it ensures that if a job fails and restarts (processing the same data again), it doesn't create duplicates in the target system.

14. **What is Consistent Hashing?**
    *   **Answer:** A hashing technique used in distributed systems (like Cassandra/DynamoDB) to minimize reorganization of data when nodes are added or removed. Only `K/n` keys need to be remapped on average, rather than nearly all keys.

15. **How do you handle "Late Arriving Data" in a streaming pipeline?**
    *   **Answer:** You use **Event Time** processing (vs processing time) and **Watermarks**. A watermark acts as a metric of progress in event time, asserting that no events older than the watermark will arrive. If they do, they are either discarded or handled by a specific late-data policy (e.g., update the result side-output).

16. **Explain the concept of ACID properties.**
    *   **Answer:**
        *   **Atomicity:** All or nothing.
        *   **Consistency:** Data moves from one valid state to another.
        *   **Isolation:** Concurrent transactions don't interfere.
        *   **Durability:** Committed transactions are permanent.

17. **What is BASE in the context of NoSQL?**
    *   **Answer:**
        *   **Basically Available:** The system guarantees availability.
        *   **Soft state:** The state of the system may change over time, even without input.
        *   **Eventual consistency:** The system will become consistent over time, given that the system doesn't receive input during that time.

18. **Design a strategy for Data Partitioning (Sharding) to avoid Hot Creation.**
    *   **Answer:** Avoid using monotonically increasing keys (like timestamps or auto-increment IDs) as the partition key if write throughput is high, as all writes will go to the same "hot" partition. Instead, use a high-cardinality key (like UserID, DeviceID) or add a random suffix (salting) to distribute load evenly.

19. **What is Change Data Capture (CDC)?**
    *   **Answer:** A design pattern to determine and track data that has changed so that action can be taken using the changed data. It is often used to replicate database changes to a data warehouse or data lake in real-time (e.g., Debezium reading redo logs).

20. **How do you ensure data quality in a high-volume ingestion pipeline?**
    *   **Answer:**
        *   **Schema Validation:** Enforce schema at the entry point (Schema Registry).
        *   **Dead Letter Queue (DLQ):** Quarantine bad records for manual inspection without blocking the pipeline.
        *   **Monitoring/Alerting:** Track metrics like null counts, value ranges, and unexpected formats.

### Advanced Level

21. **How do you handle Backpressure in a data streaming system?**
    *   **Answer:** Backpressure occurs when the consumer cannot keep up with the producer. Strategies:
        *   **Buffering:** Use a queue (Kafka) to store the excess temporarily.
        *   **Dropping:** Drop messages (sampling/shedding) if data loss is acceptable.
        *   **Flow Control:** The consumer signals the producer to slow down (e.g., TCP flow control, Reactive Streams).
        *   **Auto-scaling:** Dynamically add more consumers.

22. **Design a system to calculate "Top K" items in real-time (e.g., Trending Hashtags) for billions of events.**
    *   **Answer:** using a **Count-Min Sketch** data structure to estimate frequencies with low memory, coupled with a Min-Heap to keep the Top K elements. This provides an approximate answer with very low latency and memory usage compared to a precise hash map. Or use Sliding Windows in a framework like Flink/Spark Streaming.

23. **How would you architecture a data lakehouse to handle GDPR "Right to be Forgotten" requests efficiently?**
    *   **Answer:** Data in lakes (Parquet/ORC) is immutable. Updating a single row requires rewriting the whole file.
        *   **Strategy:** Delta Lake / Hudi / Iceberg. These table formats support ACID transactions and `DELETE/UPDATE` operations efficiently by rewriting only the affected files or using copy-on-write/merge-on-read patterns.
        *   **Partitioning:** Partition by UserID (if feasible) or a hash of UserID to limit the number of files to rewrite.

24. **Discuss the trade-offs between choosing a Row-Oriented vs. Column-Oriented storage format.**
    *   **Answer:**
        *   **Row-Oriented (Postgres, MySQL, Avro):** Good for transactional (OLTP) workloads where you read/write full rows. Good for write-heavy with all fields.
        *   **Column-Oriented (Parquet, ORC, Snowflake, Redshift):** Good for analytical (OLAP) workloads (aggregations on specific columns). Better compression (similar data types together). IO efficient for reading subset of columns.

25. **How do you handle "Data Skew" in a distributed join operation?**
    *   **Answer:**
        *   **Broadcast Join:** If one table is small, broadcast it to all nodes to avoid shuffles.
        *   **Salting:** If a key is skewed, add a random number (0-N) to the key in the skewed table and replicate the reference table N times to match the salted keys. This breaks the hot key into N buckets.

26. **Design a Globally Distributed Database system. How do you handle write conflicts?**
    *   **Answer:**
        *   **Last-Write-Wins (LWW):** Based on timestamp (requires clock synchronization/NTP).
        *   **Vector Clocks:** To detect causality and conflicts, allowing the application to resolve them.
        *   **CRDTs (Conflict-free Replicated Data Types):** Data structures that guarantee valid convergence (e.g., counters, sets).
        *   **Quorum Consensus:** (R + W > N) Read and write to a majority of nodes.

27. **What is "Exactly-Once" semantics in the context of Kafka + Flink/Spark? How is it achieved internally?**
    *   **Answer:** It means the effect of processing is visible exactly once.
        *   **Kafka:** Uses idempotent producers (sequence IDs) and transactional writes (atomic commit across partitions).
        *   **Flink:** Uses the **Chandy-Lamport algorithm** for distributed snapshots (checkpoints). It saves the state and source offsets atomically. On failure, it rewinds both source and state to the last checkpoint.

28. **Explain the implementation of a Bloom Filter and where it is used.**
    *   **Answer:** A probabilistic data structure used to test whether an element is a member of a set. It returns "possibly in set" or "definitely not in set". Used to avoid expensive disk lookups (e.g., checking if a key exists in an SSTable in Cassandra/HBase before reading the disk).

29. **How would you design a rate limiter for a public API?**
    *   **Answer:**
        *   **Algorithms:** Token Bucket, Leaky Bucket, Fixed Window Counter, Sliding Window Log.
        *   **Storage:** Redis (fast, supports TTL) to store counters per API key/IP.
        *   **Race Conditions:** Use atomic counters (INCR) or Lua scripts in Redis to ensure atomicity.

30. **What is the difference between "Pulsar" and "Kafka" architecture?**
    *   **Answer:**
        *   **Kafka:** Storage and Compute are coupled (brokers store data on local disk). Scaling storage requires moving data (rebalancing).
        *   **Pulsar:** Separates Compute (Brokers) from Storage (BookKeeper). Brokers are stateless. Storage can scale independently. Tiered storage is built-in.