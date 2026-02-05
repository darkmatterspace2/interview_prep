 Amazon **does** ask deceptively hard SQL — not trick syntax, but **logic-heavy, multi-step,edge-case–loaded queries**. These come straight from real internal analytics problems, and many candidates fail because they underestimate SQL depth.

Below is a **worst-case, advanced SQL question bank**, distilled from **Amazon interview reports, Glassdoor patterns, and internal-style analytics problems**.

This is the **ceiling** you should prepare for.

---

# 🔥 AMAZON – ADVANCED & HARD SQL QUESTION BANK

*(Prepared-for-the-worst edition)*

---

## 1️⃣ Multi-Stage Window Function Problems (Very Common)

### 1. Latest valid record with conditions

> For each `shipment_id`, find the **latest status**, but **ignore statuses marked as invalid**.
> If the latest record is invalid, return the **previous valid one**.

**Tests:**

* Window functions
* Conditional ordering
* Edge cases

---

### 2. Top-N per group with ties

> Find **top 3 delivery routes per city per month**, but:

* Include ties
* Exclude routes with fewer than 10 shipments

---

### 3. Gap & island (Amazon favorite)

> Find **continuous delivery delay periods** for each shipment where delay > 30 minutes.

---

### 4. Change detection

> Identify shipments where the **status changed backward** (e.g., DELIVERED → IN_TRANSIT).

---

### 5. Rolling metrics with exclusions

> Compute a **7-day rolling average delivery time**, excluding weekends and holidays.

---

## 2️⃣ Deduplication Under Constraints (Very Common)

### 6. Complex dedup logic

> Deduplicate shipment events where:

* Same shipment_id
* Same status
* Timestamp difference < 5 minutes
  Keep the **earliest record**.

---

### 7. Partial duplicates

> Identify records that are duplicates by business logic but differ in metadata.

---

### 8. Soft deletes

> Given `is_deleted = 1`, return the **latest non-deleted record per key**, even if deleted records are newer.

---

## 3️⃣ Temporal & Time-Series SQL (High Difficulty)

### 9. Event duration calculation

> Calculate time spent in each status per shipment.

---

### 10. Late-arriving data

> Events arrive late. Recalculate **daily metrics** based on event_time, not ingestion_time.

---

### 11. Sessionization

> Group shipment events into sessions where gap > 30 minutes starts a new session.

---

### 12. SLA breach detection

> Find shipments that breached SLA **at any point**, not just final delivery.

---

## 4️⃣ Conditional Aggregations & Metrics Logic

### 13. Conditional counts

> Count shipments that:

* Were delayed
* Eventually delivered
* Never breached SLA again after recovery

---

### 14. Funnel analysis (Amazon-style)

> Shipment lifecycle funnel:
> CREATED → PICKED → SHIPPED → DELIVERED
> Calculate **drop-off rate at each stage**.

---

### 15. Mutually exclusive metrics

> Categorize shipments into:

* On-time
* Late but recovered
* Late and failed
  Ensure **no overlaps**.

---

## 5️⃣ Hierarchical & Recursive SQL (Rare but brutal)

### 16. Recursive dependency tracking

> Track shipment transfers across hubs recursively and calculate total hops.

---

### 17. Graph-style traversal

> Find all downstream hubs affected if one hub fails.

---

## 6️⃣ Subqueries & Correlated Logic

### 18. Correlated subquery challenge

> Find shipments whose delivery time is **greater than the average of its city on that day**.

---

### 19. Anti-join logic

> Find shipments that **never entered a FAILED state**, even temporarily.

---

### 20. Exists vs Join semantics

> Write a query that behaves differently with `EXISTS` than with `JOIN` — explain why.

---

## 7️⃣ Data Quality & Anomaly Detection

### 21. Outlier detection

> Identify delivery times that are **3x higher than the city median**.

---

### 22. Sudden spike detection

> Detect days where shipment volume increased by > 50% day-over-day.

---

### 23. Broken pipeline detection

> Find days where shipments exist but **no status updates were recorded**.

---

## 8️⃣ Performance-Aware SQL (Amazon Loves This)

### 24. Rewrite for performance

> Given a slow query using multiple subqueries, rewrite using window functions.

---

### 25. Partition-pruning logic

> Write SQL that **guarantees partition pruning** on a date column.

---

### 26. Join explosion prevention

> Rewrite a query to avoid cartesian multiplication.

---

## 9️⃣ Edge-Case & Trap Questions

### 27. NULL semantics

> Find shipments where **status never changed**, even if status is NULL.

---

### 28. Boolean trap

> `WHERE status != 'DELIVERED'` — why is this dangerous?

---

### 29. COUNT vs COUNT DISTINCT

> When will `COUNT(*) != COUNT(col)`?

---

### 30. GROUP BY trap

> Query returns fewer rows than expected — why?

---

## 🔟 Combined Monster Questions (Worst Case)

### 31. End-to-end analytics question

> From raw shipment events:

* Deduplicate
* Identify latest valid status
* Calculate delivery duration
* Flag SLA breach
* Aggregate daily metrics

**Single query or CTE chain**

---

### 32. Explain + write SQL

> Explain the approach first, then write SQL.

---

## 🧠 How Amazon Evaluates These

They look for:

* **Correct logic** > fancy syntax
* Use of **CTEs for clarity**
* Window functions instead of nested subqueries
* Handling **NULLs, duplicates, late data**
* Ability to **explain trade-offs**

They do **not** expect:

* One-liner magic
* Perfect syntax from memory
* Vendor-specific hacks

---

## 🧪 How to Practice (Important)

For each question:

1. Define **grain**
2. Identify **dedup rules**
3. Decide **window vs aggregation**
4. Handle **NULLs explicitly**
5. Validate edge cases

---

## 🔑 Mental Models That Win Amazon SQL Rounds

* **“What is the grain?”**
* **“What is the latest valid record?”**
* **“What happens with NULLs?”**
* **“What if data arrives late?”**
* **“Does this double count?”**

---

