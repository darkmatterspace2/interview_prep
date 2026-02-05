# Amazon interview questions
# Part 1
a **topic-wise, Amazon-style question bank** tailored for **Data Engineer II – GTTS**.
This is **practice-grade**, not generic interview-ready.

---

# 1. SQL (High Priority)

### Basics & Aggregations

1. Find total shipments per day.
2. Count distinct shipment IDs per region.
3. Find regions with more than 10,000 shipments in a month.
4. Calculate average delivery time per carrier.
5. Find max, min, avg transit time per route.

---

### Joins

6. Get shipments that never reached “DELIVERED” status.
7. Find shipments with missing carrier information.
8. Join shipment and event tables to get latest status.
9. Identify shipments with inconsistent region mapping.
10. LEFT vs INNER JOIN — when will counts differ?

---

### Window Functions

11. Latest status per shipment using `ROW_NUMBER`.
12. Rank top 5 delay-prone cities per month.
13. Calculate running total of shipments per day.
14. Find previous and next status using `LAG/LEAD`.
15. Detect repeated status updates consecutively.

---

### Deduplication & Data Quality

16. Remove duplicate shipment events.
17. Keep the most recent record per shipment.
18. Identify shipments with duplicate tracking IDs.
19. Count late-arriving events.
20. Detect missing status transitions.

---

### Time-Based Analytics

21. Shipments delivered within SLA.
22. Calculate 7-day rolling average delivery time.
23. Sessionize shipment events by inactivity gap.
24. Detect shipments stuck in same status > 24 hrs.
25. Compare week-over-week shipment volume.

---

# 2. Python (Data Engineering Focus)

### Data Structures & Logic

26. Count occurrences from list of shipment events.
27. Find duplicates in a list of dictionaries.
28. Group shipments by region.
29. Sort events by timestamp.
30. Merge two shipment datasets.

---

### String / JSON Processing

31. Parse nested JSON shipment events.
32. Flatten JSON into tabular format.
33. Handle malformed JSON records safely.
34. Extract fields from semi-structured logs.
35. Normalize inconsistent status values.

---

### Performance & Memory

36. Process a large file line by line.
37. Optimize loop vs dictionary lookup.
38. Streaming vs batch processing logic.
39. Generator vs list — when and why?
40. Handling millions of records safely.

---

### Error Handling

41. Skip bad records but continue processing.
42. Log failures with minimal performance hit.
43. Retry logic for failed transformations.
44. Validate schema before processing.
45. Detect nulls and unexpected values.

---

# 3. Data Modeling & Warehousing

### Core Concepts

46. Fact vs Dimension — examples from logistics.
47. Design a shipment fact table.
48. Design carrier and location dimensions.
49. Normalize vs denormalize — trade-offs.
50. Grain of a table — define and justify.

---

### Slowly Changing Dimensions (SCD)

51. SCD Type 1 vs Type 2 — when to use?
52. Track carrier name changes over time.
53. Handle late-arriving dimension records.
54. Backfill historical data safely.
55. Maintain surrogate keys.

---

### Analytics Design

56. Design tables for dashboard reporting.
57. Optimize tables for frequent joins.
58. Partition strategy for time-series data.
59. Handle schema evolution.
60. Cold vs hot data separation.

---

# 4. ETL / Pipeline Design

### Batch Pipelines

61. Design a daily shipment aggregation pipeline.
62. Idempotent pipeline — explain with example.
63. Backfill last 30 days of data.
64. Handle partial pipeline failures.
65. Reprocess corrupted data safely.

---

### Streaming / Near Real-Time

66. Design real-time shipment status tracking.
67. Handle duplicate events in streaming.
68. Event time vs processing time.
69. Late-arriving events handling.
70. Exactly-once vs at-least-once semantics.

---

### Reliability & Quality

71. Data validation checks you’d implement.
72. Monitoring pipeline health.
73. SLA vs SLO for data pipelines.
74. Alert fatigue — how to avoid?
75. Root cause analysis of data mismatch.

---

# 5. Big Data / Distributed Systems

### Spark / Distributed Concepts

76. What causes data skew?
77. Wide vs narrow transformations.
78. Why joins are expensive?
79. Shuffle — what and why?
80. Partitioning vs bucketing.

---

### Optimization

81. How to optimize large joins?
82. Broadcast join — when?
83. Repartition vs coalesce.
84. File size optimization.
85. Handling small files problem.

---

# 6. System Design (Amazon Style)

86. Design an end-to-end logistics analytics system.
87. Design shipment delay prediction pipeline.
88. Design real-time dashboard for operations team.
89. Cost vs latency trade-offs.
90. Multi-region data ingestion strategy.

---

# 7. Behavioral (Leadership Principles)

### Ownership / Dive Deep

91. Fixed a broken data pipeline.
92. Debugged a data discrepancy.
93. Found root cause of incorrect metrics.
94. Took ownership beyond your role.
95. Improved reliability of data systems.

---

### Bias for Action / Deliver Results

96. Delivered under tight deadlines.
97. Chose speed over perfection — why?
98. Made a decision with incomplete data.
99. Automated a manual process.
100. Reduced cost or improved performance measurably.

---

# 8. Business & Transportation Domain

101. Key KPIs for logistics systems.
102. How data improves delivery efficiency.
103. Cost drivers in transportation.
104. Metrics to track delivery delays.
105. Trade-offs between speed and cost.

---

## How to use this effectively

* **SQL + Python** → write code, don’t just think
* **Design questions** → speak out loud
* **Behavioral** → STAR format, with numbers
* Aim to answer **80% confidently**

## Part 2

Based on the specific Amazon Data Engineer II job description (GTTS team), here is a targeted, topic-wise question bank to help you drill down on the necessary skills.

### 1. SQL & Data Warehousing (Redshift Focus)

*The JD emphasizes Redshift and advanced SQL. Amazon SQL questions often focus on efficiency and window functions.*

* **Scenario:** You have a table of `PackageScans` (package_id, timestamp, location, status). Write a query to find the time difference between the "Out for Delivery" scan and the "Delivered" scan for every package delivered yesterday.
* **Window Functions:** Write a query to find the top 3 transportation lanes (Source -> Destination) with the highest average delay per week.
* **Optimization:** You have a query on a 10TB table in Redshift that is running slowly. How do you debug it? Explain `DISTKEY` and `SORTKEY` strategies for this table.
* **Architecture:** Explain the architecture of Amazon Redshift. What is the leader node vs. compute node?
* **Constraints:** How do you handle "Gaps and Islands" problems (e.g., finding consecutive days a truck driver was active)?

### 2. Big Data Processing (Spark & PySpark)

*The JD explicitly mentions "Spark + Scala/Python" and processing "TBs of data".*

* **Core Concepts:** What is the difference between an RDD, a DataFrame, and a Dataset? When would you use one over the others?
* **Optimization:** You are joining a large table (Shipments) with a small table (TruckCodes), and the job is slow. What technique would you use? (Expected answer: Broadcast Join).
* **Troubleshooting:** Your Spark job fails with an `OutOfMemoryError`. What steps do you take to debug and fix this?
* **Internals:** Explain how Spark handles fault tolerance. What is the role of the DAG and Lazy Evaluation?
* **File Formats:** Why is Parquet preferred over CSV for analytics? How does Parquet's columnar storage help with query performance in S3/Athena?

### 3. Data Modeling

*Focus on the transportation domain mentioned in the JD.*

* **Dimensional Modeling:** Design a Star Schema for analyzing "Delivery Accuracy." What are your Fact tables and Dimension tables?
* **SCD:** How would you handle a scenario where a Fulfillment Center changes its region assignment? (Explain Slowly Changing Dimensions Type 1 vs. Type 2).
* **Logistics Scenario:** How would you model a graph network of cities and routes to calculate capacity? (Graph DB vs Relational).

### 4. AWS Ecosystem & Infrastructure

*The JD lists EMR, Glue, S3, Kinesis, Athena, and Lake Formation.*

* **Storage:** How would you partition S3 data for a log ingestion pipeline receiving terabytes of data daily to optimize for Athena queries?
* **Glue vs. EMR:** You need to run a daily ETL job. When would you choose AWS Glue over a persistent EMR cluster?
* **Streaming:** What is the difference between Kinesis Data Streams and Kinesis Firehose? Which one would you use to just dump data into S3?
* **Infrastructure as Code:** Have you used CloudFormation or Terraform? How do you manage state?

### 5. System Design (The "Bar Raiser")

*You will likely face a whiteboard session to design a pipeline from scratch.*

* **The Prompt:** "Design a real-time dashboard for Operations Managers to see where all Amazon trucks are currently located and if they are delayed."
* *Key components to discuss:* Ingestion (Kinesis/Kafka), Processing (Spark Streaming/Flink/Lambda), Storage (Redshift/DynamoDB), Visualization (QuickSight).


* **Data Quality:** How do you build a framework to detect if data arriving from a vendor is malformed or missing without stopping the entire pipeline?
* **Backfilling:** We found a bug in the logic that calculates shipping costs. The bug has existed for 6 months. How do you re-process that historical data while new data is still flowing in?

### 6. Coding & Algorithms (Python)

*Amazon DEs need to script. Expect medium-level LeetCode.*

* **Strings/Arrays:** Given a log file with millions of entries, write a script to count the occurrence of every IP address and return the top 10.
* **Data Structures:** Implement a method to validate if a string of parentheses `()[]{}` is balanced (Stack usage).
* **Dictionary Manipulation:** Given a list of package routes `[('A', 'B'), ('B', 'C'), ('C', 'D')]`, reconstruct the full path `A -> B -> C -> D`.

### 7. Behavioral (Leadership Principles)

*Prepare 2 stories for each of these high-priority principles for this role.*

* **Customer Obsession:** Tell me about a time you pushed back on a requirement because it wasn't in the best interest of the data consumer/customer.
* **Ownership:** Tell me about a time a critical pipeline broke at 2 AM. What did you do?
* **Deliver Results:** Describe a situation where you had to simplify a complex solution to meet a tight deadline.
* **Bias for Action:** Tell me about a time you took a calculated risk to fix a data issue without having all the information.

**Next Step:**
Would you like to try a **mock loop**? I can ask you *one* specific question from this bank (e.g., a Spark optimization scenario), and you answer it, then I'll give you feedback as if I were the Amazon interviewer.