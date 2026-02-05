# Amazon Best Practices & Non-Relational Stores (Q36-Q56)

## 2️⃣ Best Practices in Data Engineering (Advanced)

#### 36. What makes a data platform **scalable**?
*   **Decoupled Compute & Storage:** (Snowflake/S3). Scale them independently.
*   **Stateless Processing:** (K8s/Lambda). No sticky sessions.
*   **Partitioning:** Ability to process chunks in parallel.
*   **Backpressure:** Ability to slow down ingress when overloaded.

#### 37. How do you design for **reprocessing and backfills**?
*   **Separate Config:** Allow passing `start_date` and `end_date` overrides.
*   **Isolation:** Run backfills on separate infrastructure (queues/clusters) to protect SLAs.
*   **Idempotency:** Re-running a day simply overwrites it.

#### 38. Idempotency — why it matters and how to implement it.
*   **Why:** Distributed systems retry. If you count +1 on every retry, numbers are wrong.
*   **How:** 
    *   **Upsert:** Using Unique Keys.
    *   **Overwrite:** Partition exchange.
    *   **Dedupe:** State store tracking processed IDs.

#### 39. How do you avoid “data swamps”?
*   **Governance:** Mandatory metadata tags (Owner, Retention).
*   **Lifecycle:** Auto-deletion policies for temp data.
*   **Quality Gates:** Don't let bad data enter the Silver layer.

#### 40. When should data pipelines fail fast vs be tolerant?
*   **Fail Fast:** Schema misalignment, Authorization errors. (Things that won't fix themselves).
*   **Tolerant:** API Timeouts, 1 bad row in a billion. (Retry or DLQ).

---

## 3️⃣ Non-Relational Databases & Data Stores

### Object Storage (S3)

#### 41. Why object storage is the backbone of modern data platforms.
*   **Cost:** Dirt cheap ($0.02/GB).
*   **Durability:** 11 9s.
*   **Throughput:** Parallel reads (Range Gets) are massive.
*   **Interoperability:** Everything (Spark, Presto, Snowflake) reads S3.

#### 42. Performance pitfalls of object storage.
*   **List Operations:** Slow. (Don't have 1 million files in one folder).
*   **Latency:** First byte latency is high (ms) compared to SSD. Not for Transactional usage.
*   **Small Files:** Metadata overhead kills throughput.

#### 43. How do you design datasets for efficient reads?
*   **Partitioning:** `date=.../region=...` (Pruning).
*   **Format:** Parquet/ORC (Column pruning).
*   **Compression:** Snappy/Zstd (Splitable).
*   **Sizing:** 128MB - 1GB files.

#### 44. Object storage consistency guarantees — implications.
*   Older S3 was Eventual Consistency (Listing might miss a new file).
*   Modern S3 is **Strong Consistency**. You can read-after-write instantly. Simplifies pipeline logic (no more `sleep(5)`).

---

### Key-Value & Document Stores

#### 45. When do you choose DynamoDB / CosmosDB / Redis?
*   **Redis:** Cache. Ephemeral. Sub-ms latency.
*   **DynamoDB:** Operational Store. Serverless. High scale. Simple Access Patterns (Get Item).
*   **Cosmos/Mongo:** Flexible Schema. Document interaction.

#### 46. How do access patterns drive NoSQL design?
**Read-Heavy Design.**
*   In SQL, you model data (Normalization).
*   In NoSQL, you model **queries**.
*   If you need to query "Orders by User", your Partition Key must be `UserID`.

#### 47. Hot partition problem — detection and mitigation.
*   **Metric:** Throttled Write Requests.
*   **Cause:** Everyone writing to `PartitionKey="A"`.
*   **Mitigation:** **Write Sharding**. Append a suffix `A_1`, `A_2`. Randomly write. Aggregate on read.

#### 48. Schema evolution in document stores.
*   **Application-Side Handling:** The App code must handle `if field exists`.
*   **Migration:** Lazy migration (update row when accessed) or scanner jobs.

---

### Column-Family Databases (Cassandra)

#### 49. When is Cassandra a good choice?
*   Massive Write Throughput (IoT logs).
*   Multi-region Active-Active replication requirements.
*   Linear Scalability (Add nodes = Add capacity).

#### 50. Write-optimized vs read-optimized trade-offs.
*   **LSM Trees (Cassandra):** Append-only writes. Fast write. Reads require merging SSTables (slower).
*   **B-Trees (Postgres):** Update in place. Slower write (Seeking). Fast read.

#### 51. TTLs — when and when not to use.
*   **Use:** Session data, Temp caches, IoT logs (7 days).
*   **Don't Use:** Core business records. (Tombstones can degrade performance).

#### 52. Secondary indexes — dangers.
*   In distributed DBs, Secondary Indexes require scatter-gather (querying all nodes). **Performance killer.**
*   *Solution:* Materialized Views or separate tables optimized for that query.

---

### Graph Databases

#### 53. When is a graph DB justified?
*   Deep Traversal (> 3 hops). "Friends of Friends of Friends".
*   Fraud Rings.
*   Recommendation Engines.

#### 54. Why graph DBs often fail at scale.
*   **Partitioning is hard.** Cutting a graph across nodes breaks traversals (Network hopping).
*   Super-nodes (Justin Bieber problem) kill performance.

#### 55. Modeling relationships vs joins.
*   **Relational:** Joins are computed at read time (expensive).
*   **Graph:** Relationships are stored physically (pointers). Traversal is O(1) per hop.

#### 56. Analytics on graph data — alternatives.
*   Don't run Graph Algo on Transactional Graph DB.
*   Use **Graph Compute Engines** (Spark GraphX, Giraph) for batch analysis (PageRank).
