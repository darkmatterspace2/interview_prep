# Amazon Advanced SQL - Deduplication & Temporal (Q6-Q12)

This section covers **Data Quality, Deduplication, and Time-Series Logic**.

---

### 6. Complex dedup logic
**Question:**
> Deduplicate shipment events where:
> * Same `shipment_id`
> * Same `status`
> * Timestamp difference < 5 minutes (i.e., rapid-fire updates)
>   **Keep the earliest record** of such a cluster.

**Solution Strategy:**
1.  **Lag & Compare:** Compare current time with previous time for the same ID/Status.
2.  **Flag:** If `(CurrentTime - PrevTime) > 5 mins` OR `PrevTime` is NULL, it's a "New" valid event. If < 5 mins, it's a duplicate.
3.  **Filter:** Keep only "New" events.

**SQL:**
```sql
WITH Lagged AS (
    SELECT 
        shipment_id,
        status,
        event_timestamp,
        LAG(event_timestamp) OVER(
            PARTITION BY shipment_id, status 
            ORDER BY event_timestamp
        ) as prev_ts
    FROM events
)
SELECT *
FROM Lagged
WHERE prev_ts IS NULL 
   OR event_timestamp - prev_ts >= INTERVAL '5 minutes';
```

---

### 7. Partial duplicates
**Question:**
> Identify records that are duplicates by business logic (Same `shipment_id` & `status`) but differ in metadata (e.g., `operator_id` changed).

**Solution Strategy:**
1.  **Group By:** Group by the business keys (`shipment_id`, `status`).
2.  **Count Distinct:** Check if `count(distinct operator_id) > 1`.

**SQL:**
```sql
SELECT 
    shipment_id, 
    status,
    COUNT(*) as total_records,
    COUNT(DISTINCT operator_id) as distinct_operators
FROM events
GROUP BY 1, 2
HAVING COUNT(*) > 1 
   AND COUNT(DISTINCT operator_id) > 1;
```

---

### 8. Soft deletes
**Question:**
> Given `is_deleted = 1` column. Return the **latest non-deleted record per key**.
> *Trap:* A deleted record might have a *later* timestamp than the valid one. You must ignore the deleted ones first.

**Solution Strategy:**
1.  **Filter:** `WHERE is_deleted = 0` (or `FALSE`).
2.  **Rank:** `ROW_NUMBER()`.
3.  *(Critical Edge Case)*: If a shipment was created, then deleted, the result should be "Nothing", not the previous version of the creation. The simple filter handles this (no rows return).

**SQL:**
```sql
SELECT *
FROM (
    SELECT 
        *,
        ROW_NUMBER() OVER(PARTITION BY id ORDER BY timestamp DESC) as rn
    FROM table
    WHERE is_deleted = 0
) t
WHERE rn = 1;
```

---

### 9. Event duration calculation
**Question:**
> Calculate time spent in each status per shipment.
> *Sequence:* CREATED (10:00) -> SHIPPED (12:00) -> DELIVERED (14:00).
> *Result:* CREATED duration = 2 hrs. SHIPPED duration = 2 hrs.

**Solution Strategy:**
1.  **Lead:** Look ahead to the *next* event's timestamp.
2.  **Diff:** `Next_Timestamp - Current_Timestamp`.
3.  **Handle Final State:** The last event (DELIVERED) has no "Next". Duration is NULL (or 0, or `Now() - timestamp` if ongoing).

**SQL:**
```sql
SELECT 
    shipment_id,
    status,
    event_timestamp,
    LEAD(event_timestamp) OVER(PARTITION BY shipment_id ORDER BY event_timestamp) as next_ts,
    LEAD(event_timestamp) OVER(PARTITION BY shipment_id ORDER BY event_timestamp) - event_timestamp as duration
FROM events;
```

---

### 10. Late-arriving data
**Question:**
> Events arrive late. Recalculate **daily metrics** based on `event_time`, not `ingestion_time`.

**Answer:**
This is primarily a **definition** question.
*   **Query:** You simply `GROUP BY DATE(event_timestamp)`.
*   **Implication:** If you run this query today for "Yesterday", you get Result A. If you run it again tomorrow (and late data arrived), you get Result B.
*   *Amazon Context:* You must explain that "Daily Metrics" tables need to be capable of **updates** (e.g., re-writing partition `2023-01-01` whenever new data for that date lands), rather than being append-only logs based on system arrival time.

---

### 11. Sessionization
**Question:**
> Group shipment events into sessions where gap > 30 minutes starts a new session.

**Solution Strategy:**
1.  **Lag Difference:** Calc `time_diff` from previous row.
2.  **Flag:** If `time_diff > 30 mins`, flag = 1 (New Session), else 0.
3.  **CumSum (Running Total):** Sum the flags to create `session_id`.

**SQL:**
```sql
WITH Step1 AS (
    SELECT 
        user_id,
        timestamp,
        CASE WHEN timestamp - LAG(timestamp) OVER(PARTITION BY user_id ORDER BY timestamp) > INTERVAL '30 minutes'
        THEN 1 ELSE 0 END as is_new
    FROM clicks
)
SELECT 
    user_id,
    timestamp,
    SUM(is_new) OVER(PARTITION BY user_id ORDER BY timestamp) as session_id
FROM Step1;
```

---

### 12. SLA breach detection
**Question:**
> Find shipments that breached SLA (Duration > 2 Days) **at any point**, not just final delivery.
> *Example:* It was "Out for Delivery", got delayed (Breach), then recovered.

**Solution Strategy:**
1.  **Calculate Duration** for *every* step (as in Q9).
2.  **Flag Breaches:** `CASE WHEN duration > '2 days' THEN 1 ELSE 0`.
3.  **Aggregation:** `GROUP BY shipment_id HAVING MAX(is_breached) = 1`.

**SQL:**
```sql
WITH Durations AS (
    SELECT 
        shipment_id,
        LEAD(timestamp) OVER(PARTITION BY shipment_id ORDER BY timestamp) - timestamp as duration
    FROM events
)
SELECT shipment_id
FROM Durations
WHERE duration > INTERVAL '2 days'
GROUP BY 1;
```
