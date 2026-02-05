Excellent ask. This is exactly the depth Amazon / big-tech DE interviews like.

Below are **two focused question banks**:

1. **PySpark scenario-based questions (real production situations)**
2. **Big-data capacity planning & cluster sizing questions** (nodes, RAM, CPU, cost trade-offs)

These are **thinking questions**, not trivia.

---

# 1️⃣ PySpark – Scenario-Based Question Bank

## A. Performance & Optimization Scenarios

1. Your Spark job runs fast on sample data but **fails or slows drastically in production**.
   → How do you diagnose and fix it?

2. A join between two large DataFrames causes **executor OOM**.
   → What are your options?

3. One task takes 20 minutes while others finish in seconds.
   → What is happening and how do you fix it?

4. A Spark job becomes slower every day as data grows.
   → What metrics do you check first?

5. Your pipeline writes **millions of small files** to S3/ADLS.
   → Why is this bad and how do you fix it?

---

## B. Data Skew & Joins

6. One key (e.g., `country = US`) has 80% of the data.
   → How do you handle skewed joins?

7. When would you use:

   * Broadcast join
   * Salting
   * Repartitioning

8. A broadcast join suddenly fails in production.
   → Why might that happen?

9. Two datasets are both large — how do you design an efficient join?

---

## C. Partitioning & Shuffle

10. Difference between `repartition()` and `coalesce()` — real use cases.

11. You repartition by date, but queries are still slow. Why?

12. What causes **shuffle explosion**?

13. How do you decide **number of partitions**?

14. When does increasing partitions make performance worse?

---

## D. Caching & Persistence

15. When should you cache a DataFrame?

16. Why did caching increase memory usage but not speed?

17. Difference between:

* `MEMORY_ONLY`
* `MEMORY_AND_DISK`
* `DISK_ONLY`

18. How do you know if cache is actually being used?

---

## E. Fault Tolerance & Reliability

19. An executor dies mid-job. What happens?

20. A job fails at 95% completion. How do you make it restartable?

21. How does Spark handle recomputation?

22. How do you design **idempotent Spark pipelines**?

---

## F. File Formats & Storage

23. Parquet vs ORC vs CSV — when and why?

24. Why does Parquet improve performance?

25. How do you optimize read performance for time-based queries?

26. What happens if schema changes in Parquet files?

---

## G. Streaming (if applicable)

27. Handling late-arriving events in Structured Streaming.

28. Exactly-once vs at-least-once semantics.

29. Watermarking — what problem does it solve?

30. What happens if the streaming job is down for 2 hours?

---

# 2️⃣ Big Data Compute Sizing & Capacity Planning Questions

These are **high-signal interview questions**.

---

## A. Cluster Sizing Fundamentals

31. You have **1 TB/day** of raw data.
    → How do you estimate cluster size?

32. How does **data expansion** affect sizing? (raw → parsed → joined → aggregated)

33. What factors decide:

* Number of nodes
* RAM per node
* CPU cores per node

34. When do you choose **more small nodes vs fewer large nodes**?

---

## B. Memory & Executor Planning

35. How do you calculate executor memory?

36. Why can giving more memory to Spark sometimes make jobs slower?

37. Driver vs Executor memory — what runs where?

38. What happens if executor memory is too small?

39. How many executors should a node have?

---

## C. CPU & Parallelism

40. How many cores per executor is ideal — and why?

41. CPU-bound vs IO-bound Spark jobs — how do they affect sizing?

42. How does `spark.sql.shuffle.partitions` impact performance?

43. When does increasing parallelism stop helping?

---

## D. Network & IO Considerations

44. Why does network bandwidth matter in Spark jobs?

45. How does shuffle stress network and disk?

46. Local SSD vs remote storage — trade-offs.

47. How does compression affect CPU vs IO?

---

## E. Cost Optimization Scenarios

48. Your cluster cost doubled after data growth.
    → How do you reduce cost without breaking SLAs?

49. Spot vs on-demand nodes — risks and design.

50. Auto-scaling vs fixed clusters — when to choose what?

---

## F. Real-World Sizing Scenarios (Very Common)

51. Batch job processes **500 GB**, SLA = **2 hours**.
    → How do you approach sizing?

52. Daily ETL runs for 6 hours instead of 2.
    → Debug vs scale — what do you do first?

53. One team wants more memory; another wants more nodes.
    → How do you decide?

54. Streaming job with 50K events/sec spikes to 200K.
    → How do you plan headroom?

---

## G. Failure & Capacity Edge Cases

55. What happens if one node is much slower than others?

56. How does speculative execution help?

57. How do you size clusters for backfills?

58. What is the impact of GC tuning?

59. How do you detect underutilized clusters?

---

## H. Trade-off & Design Judgment

60. Scale up vs scale out — real examples.

61. When is Spark not the right tool?

62. How do you explain cluster sizing to non-technical stakeholders?

63. Performance vs cost — how do you balance?

---

# How interviewers evaluate your answers

They look for:

* **Structured thinking**
* **Bottleneck identification**
* **Trade-offs (CPU vs memory vs IO vs cost)**
* **Experience-based signals**

They do **not** expect exact numbers — they expect **reasoned estimation**.

---

## If you want next:

I can:

* Walk through **sample answers** to the hardest ones
* Do a **mock Spark sizing interview**
* Convert this into **whiteboard-style problem solving**
* Map these directly to **Amazon DE II expectations**

Just tell me what you want next.
Great — this is **senior-level Data Engineering system design**, exactly what interviewers use to separate *implementers* from *designers*.

Below is a **deep, structured question bank** focused on:

* Batch vs Streaming design
* Decision-making frameworks
* Reliability, scale, CAP trade-offs
* Tool & framework selection
* End-to-end architecture thinking

This is **not tool trivia** — it’s judgment, trade-offs, and architecture.

---

# 🧠 DATA ENGINEERING SYSTEM DESIGN – QUESTION BANK

---

## 1️⃣ Batch vs Streaming — Design Decision Questions

1. Given a use case, **how do you decide batch or streaming**?
2. When is *near-real-time batch* better than streaming?
3. Why do many “real-time” systems secretly use micro-batch?
4. What business metrics justify streaming cost?
5. When is streaming **over-engineering**?

---

## 2️⃣ End-to-End Pipeline Design (Batch)

6. Design a **daily analytics pipeline** from source → dashboard.
7. How do you handle **late-arriving data** in batch systems?
8. How do you design **re-runnable & idempotent batch pipelines**?
9. How do you support **backfills** without impacting daily jobs?
10. How do you version batch logic safely?

---

## 3️⃣ End-to-End Pipeline Design (Streaming)

11. Design a **real-time event ingestion system**.
12. How do you guarantee **exactly-once semantics**?
13. Event time vs processing time — design implications.
14. How do you handle **out-of-order events**?
15. How do you evolve schema in streaming pipelines?

---

## 4️⃣ Hybrid (Lambda / Kappa / Modern)

16. Lambda architecture — pros & cons.
17. Kappa architecture — when does it break down?
18. Why most companies use **hybrid architectures**.
19. How do you reconcile batch and streaming results?
20. How do you avoid double counting?

---

## 5️⃣ Reliability & Fault Tolerance

21. What makes a data pipeline **reliable**?

22. How do you design pipelines to survive:

    * Node failure
    * Network failure
    * Data corruption

23. At-least-once vs exactly-once — trade-offs.

24. How do you design **graceful degradation**?

25. What happens when downstream systems are slow?

---

## 6️⃣ CAP Theorem — Applied to Data Engineering

26. Where does CAP apply in data pipelines?
27. Streaming systems — CP or AP?
28. Batch systems — where consistency matters?
29. Kafka vs DB — CAP trade-offs.
30. How do you explain CAP to business stakeholders?

---

## 7️⃣ Orchestration — When and What to Use

31. What is orchestration vs choreography?
32. When is **Airflow** a bad choice?
33. Airflow vs Dagster vs Prefect — decision factors.
34. Event-driven orchestration — when?
35. How do you orchestrate streaming pipelines?

---

## 8️⃣ Messaging & Event Systems

36. Kafka vs SQS vs Pub/Sub — design choices.
37. Partitioning strategy for message queues.
38. Ordering guarantees — when needed?
39. Message retention vs storage.
40. Backpressure — how do you handle it?

---

## 9️⃣ Stream Processing Frameworks

41. Spark Structured Streaming vs Flink.
42. When Flink is the better choice.
43. Stateful vs stateless processing — design impact.
44. Checkpointing — why it matters.
45. Handling reprocessing in streaming systems.

---

## 🔟 Data Lake & Storage Design

46. Data lake vs data warehouse — decision points.
47. Why data lakes fail in practice.
48. Schema-on-read vs schema-on-write.
49. Open table formats — Iceberg / Delta / Hudi — why?
50. ACID on data lakes — when needed?

---

## 1️⃣1️⃣ Medallion Architecture (Bronze / Silver / Gold)

51. Why medallion architecture exists.
52. What belongs in Bronze vs Silver vs Gold?
53. Where should business logic live?
54. How do you handle PII across layers?
55. When medallion becomes overkill.

---

## 1️⃣2️⃣ Data Quality & Observability

56. How do you detect bad data early?
57. Data quality checks vs cost.
58. Metrics you monitor for pipelines.
59. Data observability vs traditional monitoring.
60. Alerting strategy to avoid noise.

---

## 1️⃣3️⃣ Schema & Contract Management

61. Producer vs consumer schema ownership.
62. Schema registry — why needed?
63. Breaking vs non-breaking schema changes.
64. Versioning strategies.
65. Contract testing for data pipelines.

---

## 1️⃣4️⃣ Visualization & Consumption Layer

66. OLAP vs OLTP — why it matters for BI.
67. Pre-aggregation vs real-time queries.
68. Serving layer design for dashboards.
69. Caching strategies for analytics.
70. Data freshness vs query cost trade-offs.

---

## 1️⃣5️⃣ Technology Selection — When to Use What

### Ingestion

71. CDC vs API ingestion — trade-offs.
72. Batch file ingestion vs streaming ingestion.

### Processing

73. SQL engines vs Spark vs Flink.
74. When SQL is enough.

### Storage

75. Object storage vs HDFS.
76. Columnar vs row-based formats.

### Serving

77. Data warehouse vs search engine (e.g., Elasticsearch).
78. When to use NoSQL for analytics.

---

## 1️⃣6️⃣ Security, Governance & Compliance

79. How do you design for data access control?
80. Column-level security vs row-level security.
81. Auditability in data pipelines.
82. Data retention & deletion policies.
83. Handling GDPR / PII in pipelines.

---

## 1️⃣7️⃣ Cost & Scale Trade-offs

84. Cost drivers in batch pipelines.
85. Cost drivers in streaming systems.
86. Compute vs storage trade-offs.
87. Auto-scaling — pitfalls.
88. When performance tuning beats scaling.

---

## 1️⃣8️⃣ Failure Scenarios (Very Common)

89. Source system sends duplicate data.
90. Downstream BI reports wrong numbers.
91. Streaming lag keeps increasing.
92. Batch job misses SLA.
93. Schema change breaks pipeline.

---

## 1️⃣9️⃣ Design Judgment & Philosophy

94. How do you avoid over-engineering?
95. When do you choose simplicity over perfection?
96. How do you design for future scale?
97. Build vs buy — how do you decide?
98. How do you sunset old pipelines safely?

---

## 2️⃣0️⃣ Interview-Level Open Questions

99. Design a **global-scale analytics platform**.
100. Design a **transportation / logistics data platform**.

---

# How to STUDY this (important)

For each question, practice:

1. **Clarify requirements**
2. **Choose architecture**
3. **Explain trade-offs**
4. **Call out failure modes**
5. **Tie to business impact**

Interviewers care more about **why** than **what**.

---

## Next steps (recommended)

I can:

* Provide **model answers** (whiteboard style)
* Convert this into **Amazon-style mock design rounds**
* Create a **decision matrix cheat sheet**
* Map tools → scenarios → trade-offs (very powerful)

Tell me what you want next, and I’ll go deep.
