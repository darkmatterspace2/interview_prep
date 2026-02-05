# Data Engineering System Design - Reliability, Orchestration & Messaging

## 5️⃣ Reliability & Fault Tolerance

#### 21. What makes a data pipeline **reliable**?
**Traits:**
*   **Availability:** It runs when scheduled.
*   **Correctness:** It produces accurate data.
*   **Recovery:** It can restart from failure without human intervention (Self-healing).
*   **Observability:** You know it failed before the user does.

#### 22. How do you design pipelines to survive failures?
*   **Node Failure:** Distributed computing (Spark/EMR). One worker dies, driver reschedules tasks.
*   **Network Failure:** Retries with Exponential Backoff (Wait 1s, 2s, 4s...). Dead Letter Queues (DLQ) for persistent failures.
*   **Data Corruption:** Circuit Breakers. If >10% validation fails, halt pipeline and alert. Don't pollute downstream.

#### 23. At-least-once vs exactly-once — trade-offs.
*   **At-Least-Once:** Fast, simple. Risk: Duplicates. (Okay for idempotent sinks like Key-Value overwrites).
*   **Exactly-Once:** Slow, complex overhead. Mandatory for non-idempotent sinks (e.g., sending emails, banking transactions).

#### 24. How do you design **graceful degradation**?
**Feature Flags / Fallbacks.**
*   If the "Personalized Recommendation" ML service is down, fall back to "Most Popular Items" (Cached static list).
*   The pipeline continues; the user experience degrades slightly but doesn't crash.

#### 25. What happens when downstream systems are slow?
**Backpressure.**
*   The producer must slow down.
*   streaming engines (Spark/Flink) limit `maxOffsetsPerTrigger`.
*   Queues (Kafka) fill up (retention disk space acts as the buffer).

---

## 6️⃣ CAP Theorem — Applied to Data Engineering

#### 26. Where does CAP apply in data pipelines?
Everywhere storage or state is involved.
*   **Consistency:** All nodes perceive same data.
*   **Availability:** Every request gets a response (no error).
*   **Partition Tolerance:** System works despite network cuts.
*   *Reality:* P is non-negotiable in distributed systems. You choose C or A.

#### 27. Streaming systems — CP or AP?
Usually **CP (Consistency)** oriented on the write side (Kafka High Watermark ensures replication).
But consumers might be AP (Eventual Consistency) — reading slightly stale data to ensure high throughput.

#### 28. Batch systems — where consistency matters?
**Strong Consistency** (S3 Read-after-Write).
When you finish writing a file, the next step *must* be able to list it. S3 is now Strong Consistent (formerly Eventual).

#### 29. Kafka vs DB — CAP trade-offs.
*   **Kafka:** High Availability optimized.
*   **RDBMS (Postgres):** Strong Consistency optimized (ACID).
*   *Trade-off:* Kafka accepts writes fast (A) but consumers might lag (Eventual C). Postgres rejects writes if lock can't be acquired (CP).

#### 30. How do you explain CAP to business stakeholders?
"We can have the report be **instantly available** (Availability) but it might be missing the last 5 minutes of sales (Consistency). OR, we can guarantee it's **100% accurate**, but if a server glitches, the dashboard shows an error for 5 minutes. Which do you prefer?"

---

## 7️⃣ Orchestration — When and What to Use

#### 31. What is orchestration vs choreography?
*   **Orchestration (Conductor):** Central brain (Airflow) tells A, then B, then C to run. *Better for Data Pipelines.*
*   **Choreography (Dancers):** A finishes and emits event. B hears event and starts. No central manager. *Harder to debug.*

#### 32. When is **Airflow** a bad choice?
*   **Streaming:** Airflow is a batch scheduler.
*   **Low Latency:** Airflow scheduler loop has latency (seconds/minutes). Not only for sub-second triggering.
*   **Data Passing:** Don't pass Gigabytes of data chunks between Airflow tasks (XComs). Use S3 for storage; Airflow just signals paths.

#### 33. Airflow vs Dagster vs Prefect — decision factors.
*   **Airflow:** Industry standard. Huge community. "Task-based".
*   **Dagster:** "Asset-based" (Data aware). Knows *what* table was updated, not just *that* a task ran. Better for testing.
*   **Prefect:** Modern, lighter, hybrid execution.

#### 34. Event-driven orchestration — when?
When files arrive unpredictably.
*   *Pattern:* S3 Object Create Event -> EventBridge -> Lambda/StepFunctions -> Trigger Glue Job.
*   Don't keep an Airflow sensor running 24/7 (costly polling).

#### 35. How do you orchestrate streaming pipelines?
You don't "schedule" them. You "Monitor" them.
Use tools like **SupervisorD** or **Kubernetes Deployments** to ensure the process is always *Running*.

---

## 8️⃣ Messaging & Event Systems

#### 36. Kafka vs SQS vs Pub/Sub — design choices.
*   **Kafka:** High throughput, replay capability (log storage), multiple consumers. *Complex Ops.*
*   **SQS:** Simple queue. One consumer deletes the message. No replay. *Simple Ops on AWS.*
*   **Pub/Sub:** Google's managed Kafka-like service.

#### 37. Partitioning strategy for message queues.
*   **Key-based:** `partition_key = user_id`. Ensures all events for user 123 go to Partition A. Guarantees ordering for that user.
*   **Round-robin:** Even distribution. No ordering guarantee global or per user.

#### 38. Ordering guarantees — when needed?
*   **Needed:** Financial ledger (Debit before Credit). State machine updates (Created -> Shipped).
*   **Not Needed:** Independent logs (Clickstream).

#### 39. Message retention vs storage.
Kafka is a log, not a permanent database.
*   Set retention (e.g., 7 days).
*   Archiving: Use **Kafka Connect (S3 Sink)** to dump everything to S3 for long-term storage/querying.

#### 40. Backpressure — how do you handle it?
*   **Consumer:** Pause polling if internal buffer is full.
*   **Producer:** Block or drop messages if Broker is full (Configurable).

---

## 9️⃣ Stream Processing Frameworks

#### 41. Spark Structured Streaming vs Flink.
*   **Spark:** Micro-batch. High latency (~seconds). Best for "SQL on Stream" and easy integration with Data Lakes.
*   **Flink:** True streaming (Event-at-a-time). Low latency (~ms). Best for complex stateful logic & windowing.

#### 42. When Flink is the better choice.
High-frequency trading, real-time fraud detection, complex sessionization (User inactivity triggers).

#### 43. Stateful vs stateless processing — design impact.
*   **Stateless (Filter/Map):** Easy to scale. If node dies, just process next event elsewhere.
*   **Stateful (Count/Agg/Window):** Hard. State must be checkpointed (RocksDB/HDFS). If node dies, state must be restored to correct count.

#### 44. Checkpointing — why it matters.
It preserves the "State" (e.g., current running total = 500) to disk. Without it, failure resets counts to zero (Data Loss).

#### 45. Handling reprocessing in streaming systems.
**Reset Offsets.**
*   Stop job.
*   Rewind consumer group offset to "Yesterday".
*   Restart job.
*   *Warning:* Downstream sinks must be idempotent or duplicate data happens.
