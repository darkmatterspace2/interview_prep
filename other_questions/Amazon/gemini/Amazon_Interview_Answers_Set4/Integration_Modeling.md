# Amazon Integration & Data Modeling (Q57-Q75)

## 4️⃣ Integration with Analytics & ML Platforms

#### 57. How do data pipelines differ for **analytics vs ML**?
*   **Analytics:** optimize for Aggregations (Columnar), Historical Accuracy, Daily latency.
*   **ML:** Optimize for **Point-in-Time correctness** (No leakage), Row-based lookup (Inference), reproducibility.

#### 58. Feature engineering — batch vs online features.
*   **Batch:** Calculated nightly (e.g., "Avg Spend Last 30 Days"). Used for training.
*   **Online:** Calculated ms-latency (e.g., "Current Session Clicks"). Used for inference.
*   **Challenge:** Consistent logic between SQL (Batch) and Flink/Java (Online).

#### 59. Feature stores — why they exist.
*   **Reuse:** Don't let 5 teams rebuild "User Age".
*   **Consistency:** Serve the *exact same value* to the Training job and the Serving API to prevent Skew.
*   **Time Travel:** "Give me the value of this feature as it was 3 months ago".

#### 60. Data leakage — how pipelines cause it.
*   Using future info to predict the past.
*   *Example:* Including "Is_Fraud" label in the training features.
*   *Pipeline Risk:* Aggregating over the whole dataset instead of strictly using data available *prior* to the event timestamp.

#### 61. Training-serving skew — prevention strategies.
*   **Unified Compute:** Use same code (e.g., Spark/Pandas) for both training and serving (via ODFs).
*   **Monitoring:** Monitor distribution of features in Prod vs Training. If Mean shifts, alert.

#### 62. How do you design pipelines to support Ad-hoc, Dashboards, ML, and Real-time?
**The "Lambda" or "Lakehouse" Arch.**
*   **Layer 1 (Lake):** Raw data. Supports Ad-hoc scientists.
*   **Layer 2 (Warehouse):** Gold tables. Supports Dashboards.
*   **Layer 3 (Feature Store):** Materialized features. Supports ML.
*   **Layer 4 (Stream):** Kinesis. Supports Real-time.

#### 63. How do you manage dataset versioning for ML?
**DVC (Data Version Control) or LakeFS.**
*   Model V1 trained on Dataset Hash `abc`.
*   If we retrain Model V2, we must know exactly which snapshot of data was used.

#### 64. Offline vs online feature computation trade-offs.
*   **Offline:** Complex (Windows, Joins), Cheap, High Latency.
*   **Online:** Simple (Counters), Expensive (Redis), Low Latency.

#### 65. How do you validate data before model training?
*   **Great Expectations:** Check distribution (Mean, Std Dev).
*   **Schema:** Categorical values must be within known set.
*   **Nulls:** Algorithms crash on NaNs. Impute or Drop.

---

## 5️⃣ Data Modeling for Analytics, Reporting & ML

#### 66. How does modeling differ for BI vs ML vs Operational?
*   **BI:** Star Schema (Kimball). Optimized for "Slice and Dice".
*   **ML:** One Big Table (OBT). Denormalized. No joins allowed during training load.
*   **Operational:** 3NF (Normalized). Optimized for Write Integrity.

#### 67. Why star schemas still matter.
*   **Usability:** Business users understand "Sales" and "Customer".
*   **Performance:** RDBMS optimizers perform "Star Joins" efficiently.
*   **Storage:** Dimensions are stored once (Normalization).

#### 68. When denormalization is the right choice.
*   **Big Data:** Joins are expensive (Shuffle).
*   **Read-Heavy:** If you read 1M times and write once, Denormalize (OBT) to save CPU.

#### 69. Wide tables vs narrow tables — trade-offs.
*   **Wide (OBT):** Fast reads, easy for Data Scientists. Bad for compression if sparse.
*   **Narrow (EAV):** Flexible, easy to add attributes. Horrible query performance.

#### 70. How do you design time-aware models?
*   **Effective Dates:** `valid_from`, `valid_to`.
*   **Point-in-Time Tables:** A Snapshot table that joins latest version of dimensions for every day.

#### 71. Handling slowly changing dimensions in ML.
*   ML needs the dimension *as it was*.
*   Use the Foreign Key from the Fact Table to join to the **History Table** on `Fact.date BETWEEN Dim.start AND Dim.end`.

#### 72. Feature explosion — how to control it.
*   **Dimensionality Reduction:** PCA.
*   **Selection:** Correlation matrix. Remove highly correlated features.
*   **Governance:** Don't allow "Test_Feature_1" to stay in Prod forever.

#### 73. How do you design models that survive schema changes?
*   **Views:** Decouple physical table from logical Access.
*   **Variant/JSON columns:** For "Attributes" that change often and aren't primary query keys.

#### 74. Metrics definitions — how to avoid inconsistency.
*   **Semantic Layer (LookML/dbt metrics):** Define "Revenue" in *code* once. All dashboards reference that definition. API queries that definition.

#### 75. Semantic layer — why it matters.
Prevents "Excel Wars" where Marketing says Revenue is $100 and Finance says $90 because they used different SQL filters.
