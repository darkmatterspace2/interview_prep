## 7. Monitoring, Observability & Reliability

### 1. How do you use **Azure Log Analytics** for platform monitoring?
**Answer:**
"Log Analytics is my single pane of glass.
*   I configure **Diagnostic Settings** on all ADF, Databricks, and Logic App resources to sink logs there.
*   I build custom **Workbooks** on top of it.
*   Example Query: I track 'Duration of Pipeline X over time' to spot performance degradation before it becomes an SLA breach."

### 2. What KPIs do you track for **data platform health**?
**Answer:**
"I track Operational and Business KPIs:
1.  **Pipeline Reliability:** % of successful runs vs failures (Target > 99.9%).
2.  **Data Freshness:** Delay between Source Time and Availability in Gold Layer.
3.  **Cost:** Daily burn rate vs Budget.
4.  **TTR (Time to Remediation):** How fast we fix broken pipelines."

### 3. How do you detect and resolve **data quality issues early**?
**Answer:**
"I believe in **Shift Left** for data quality.
*   **Schema Validation:** Enforced at the Bronze layer (Delta Schema Enforcement).
*   **Contract Tests:** We use **Great Expectations** or **dbt tests** in the pipeline. If a column has > 5% nulls where it shouldn't, the pipeline acts: it either fails (Stop the Line) or quarantines the bad records to an 'Error Table' and proceeds with the good data, sending an alert to the Data Stewards."

### 4. How do you implement **alerting without alert fatigue**?
**Answer:**
"Alert fatigue kills responsiveness.
*   **Grouping:** We group alerts. Instead of 100 emails for 100 failed files, we send 1 digest.
*   **Routing:** Warning alerts go to a Slack channel (\#data-alerts-warning\). Only Critical alerts (SLA Breach, Prod Down) trigger **PagerDuty** to call the On-Call engineer."

### 5. Describe a major production incident you handled end-to-end.
**Answer:**
*(Example)* "We had a 'Storage Throttling' incident.
*   **Symptom:** All ADF pipelines started failing with 503 errors.
*   **Diagnosis:** Metrics showed we hit the IOPS limit on the storage account because a new 'Backfill' job was running in parallel with BAU loads.
*   **Fix:** Immediately paused the Backfill.
*   **Root Cause:** We were using a single Storage Account for Bronze, Silver, and Gold.
*   **Long Term Fix:** We sharded the data across multiple storage accounts and implemented 'Throughput constraints' on our backfill jobs."

---

