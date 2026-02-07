# Amazon Quality, Reliability & Process (Q76-Q95)

## 6️⃣ Data Quality, Reliability & Process Improvements

### Data Quality

#### 76. What is “good” data quality?
*   **Fitness for Purpose.**
*   Data can be 100% complete and valid (schema), but if it's 2 days late, it's "Bad Quality" for a real-time dashboard.
*   **Dimensions:** Accuracy, Completeness, Timeliness, Consistency, Uniqueness, Validity.

#### 77. Preventive vs detective quality checks.
*   **Preventive:** Schema Registry rejection. "Write-Audit-Publish" pattern (Audit staging table before swapping).
*   **Detective:** Monitoring dashboard "Revenue looks weird". (Too late, but better than nothing).

#### 78. How do you prioritize quality checks?
*   **Criticality:** Does this break the CEO's dashboard? (Sev 1). Is it an internal exploratory table? (Sev 4).
*   **Impact:** Check Primary Keys and Revenue columns. Ignore "User Bio" string field.

#### 79. Data freshness vs accuracy trade-offs.
*   **Lambda Arch:**
    *   Speed Layer: Fresh but estimated (Approx count).
    *   Batch Layer: Late but accurate (Deduped).
*   **Business Choice:** "Do you want to see the trend NOW (Speed) or the exact dollar down to the cent (Accuracy)?"

#### 80. When bad data is acceptable.
*   **Exploratory Data Science:** Noise is expected.
*   **Sentiment Analysis:** Twitter feeds are inherently messy.
*   **Cost:** If cleaning cost > value of clean data.

---

### Reliability Engineering

#### 81. What are data SLOs?
*   **Objective:** "99.9% of requests return in < 200ms". "Data arrives by 9 AM 99% of days".
*   **Error Budget:** We can be late 3 days a year. If we burn the budget, we stop launching features and fix stability.

#### 82. How do you design pipelines with graceful degradation?
*   **Circuit Breakers:** If API is slow, stop fetching and use yesterday's cache.
*   **Partial Success:** If 1 file fails in a batch of 100, process 99 and alert on 1. Don't fail the whole batch.

#### 83. Replayability — design patterns.
*   **Immutable Logs:** Never update raw data. Always append.
*   **Logic Versioning:** Ability to run `code_v1` on `data_v1` or `data_v2`.

#### 84. Checkpointing and watermarking — when needed.
*   **Streaming:** Mandatory.
*   **Batch:** Good for long jobs. Save intermediate Parquet to S3. If fail, restart from Step 3.

#### 85. Handling partial failures.
*   **Semantic Atomicity:** The business event either happens totally or not at all.
*   **Clean up:** Failed job must delete its partial output files or rollback transaction.

---

### Observability

#### 86. Difference between monitoring and observability.
*   **Monitoring:** "The light is red." (Tells you *that* something is wrong).
*   **Observability:** "The light is red because the fuse blew due to a surge." (Allows you to ask *why*).

#### 87. Golden signals for data pipelines.
*   **Latency:** (Freshness).
*   **Traffic:** (Volume).
*   **Errors:** (Job Failures).
*   **Saturation:** (Cluster Capacity).

#### 88. How do you debug data issues faster?
*   **Lineage Tools:** (DataHub / OpenLineage). "Where did this NULL come from?"
*   **Query Logs:** "Who ran `UPDATE`?"
*   **Correlated Logs:** Trace ID passing from API -> Kafka -> Spark.

#### 89. Lineage — how much is enough?
*   **Table Level:** Mandatory. "Table A feeds Table B".
*   **Column Level:** Nice to have. "Col X derived from Col Y".
*   **Row Level:** Overkill usually.

#### 90. Impact analysis when things break.
*   **Graph Traversal:** "If Table X is late, Dashboard Y and ML Model Z will be stale."
*   **Alerting:** Notify the *owners* of Y and Z automatically.

---

### Continuous Improvement

#### 91. How do you identify pipeline bottlenecks?
*   **Gantt Chart:** Visualize task duration. "Why does `Extract` take 90% of time?"
*   **Profiling:** Spark UI.
*   **Resource Utilization:** CPU Idle time.

#### 92. How do you sunset unused datasets?
*   **Audit Logs:** "Check query logs for last 90 days. If 0 queries, mark deprecated."
*   **Scream Test:** Move to `archive/` folder. Wait 1 week. If no one screams, delete.

#### 93. How do you measure ROI of data work?
*   **Usage:** DAU/MAU of the dashboard.
*   **Decisions:** "This data saved $1M in fraud".
*   **Efficiency:** "Reduced compute cost by 20%".

#### 94. How do you drive quality culture across teams?
*   **Gamification:** "Zero Bug" leaderboard.
*   **Ownership:** "You build it, you run it."
*   **Transparency:** Public Quality Dashboards.

#### 95. Automation opportunities in data platforms.
*   **Auto-scaling:** Clusters.
*   **Auto-healing:** Restarting stuck jobs.
*   **Auto-profiling:** Generating data stats on arrival.
