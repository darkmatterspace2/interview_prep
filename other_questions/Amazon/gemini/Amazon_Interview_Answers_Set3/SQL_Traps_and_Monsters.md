# Amazon Advanced SQL - Traps & Edge Cases (Q27-Q32)

This section covers **Logic Traps and End-to-End Scenarios**.

---

### 27. NULL semantics
**Question:**
> Find shipments where **status never changed**, even if status is NULL.

**SQL:**
```sql
SELECT shipment_id
FROM events
GROUP BY 1
HAVING COUNT(DISTINCT status) = 1
   OR COUNT(DISTINCT status) = 0; -- Handle all-NULL case
```
*Edge Case:* `COUNT(column)` ignores NULLs. If a shipment has rows but all statuses are NULL, `COUNT(DISTINCT status)` is 0. If you just said `= 1`, you miss these.

---

### 28. Boolean trap
**Question:**
> `WHERE status != 'DELIVERED'` — why is this dangerous?

**Answer:**
**NULLs are excluded.**
*   In SQL, `NULL != 'DELIVERED'` evaluates to **NULL** (Unknown), not TRUE.
*   Rows with NULL status will disappear from the result.
*   *Fix:* `WHERE status != 'DELIVERED' OR status IS NULL` (or use `COALESCE(status, 'X') != 'DELIVERED'`).

---

### 29. COUNT vs COUNT DISTINCT
**Question:**
> When will `COUNT(*) != COUNT(col)`?

**Answer:**
When `col` contains **NULLs**.
*   `COUNT(*)` counts rows (including NULLs).
*   `COUNT(col)` counts non-null values.

---

### 30. GROUP BY trap
**Question:**
> Query returns fewer rows than expected. `SELECT city, count(*) FROM table GROUP BY city`.

**Answer:**
**NULL Cities.**
*   Most DBs treat NULL as a valid group. One row will be `NULL | 50`.
*   However, if you have a `WHERE city NOT IN ('A', 'B')` clause, remember `NOT IN (..., NULL)` returns **Empty Set** for everything.
*   *Amazon Context:* Did the join duplicate rows? Did the `HAVING` clause filter groups out?

---

### 31. End-to-end analytics question (The "Monster")
**Question:**
> From raw shipment events:
> 1. Deduplicate
> 2. Identify latest valid status
> 3. Calculate delivery duration
> 4. Flag SLA breach ( > 2 days)
> 5. Aggregate daily metrics

**SQL (Linear CTE Chain):**

```sql
WITH Deduped AS (
    -- 1. Deduplicate (Keep latest timestamp per ID/Status)
    SELECT shipment_id, status, event_time
    FROM (
        SELECT *, ROW_NUMBER() OVER(PARTITION BY shipment_id, status ORDER BY event_time DESC) as rn
        FROM raw_events
    ) t WHERE rn = 1
),
StatusDurations AS (
    -- 3. Calculate Duration of each step
    SELECT 
        shipment_id, 
        event_time,
        status,
        LEAD(event_time) OVER(PARTITION BY shipment_id ORDER BY event_time) - event_time as duration
    FROM Deduped
),
Summary AS (
    -- 2 & 4. Latest Status & SLA Breach
    SELECT 
        shipment_id,
        -- Latest Status (using simple First Value logic or distinct filtering)
        (SELECT status FROM Deduped d2 WHERE d2.shipment_id = d1.shipment_id ORDER BY event_time DESC LIMIT 1) as final_status,
        -- Breach if ANY step took > 2 days
        MAX(CASE WHEN duration > INTERVAL '2 days' THEN 1 ELSE 0 END) as has_breach,
        -- Total Delivery Time
        MAX(event_time) - MIN(event_time) as total_duration
    FROM StatusDurations d1
    GROUP BY 1
)
-- 5. Daily Aggregates of the *Completed* shipments
SELECT 
    CURRENT_DATE as report_date,
    COUNT(*) as total_shipments,
    SUM(has_breach) as sla_breaches,
    AVG(total_duration) as avg_time
FROM Summary
WHERE final_status = 'DELIVERED';
```

---

### 32. Explain + write SQL
**Question:**
> Explain the approach first, then write SQL.

**Answer Format:**
1.  **Architecture:** "I will use a Common Table Expression (CTE) approach for readability."
2.  **Step 1:** "First, I'll filter invalid records because..."
3.  **Step 2:** "Then, I'll use a Window Function to rank them..."
4.  **Step 3:** "Finally, I'll aggregate by City."
5.  *(Then write the code).*
*Why?* Amazon interviewers stop you if the logic is wrong *before* you write code. It saves time.
