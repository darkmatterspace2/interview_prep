# Amazon Advanced SQL - Quality & Performance (Q21-Q26)

This section covers **Anomaly Detection and Performance Optimization**.

---

### 21. Outlier detection
**Question:**
> Identify delivery times that are **3x higher than the city median**.

**Solution Strategy:**
*   **Median:** Standard SQL (`AVG`) is mean. Median is `PERCENTILE_CONT(0.5)`.
*   **Window:** Calculate median per city.
*   **Filter:** `time > 3 * median`.

**SQL:**
```sql
WITH CityStats AS (
    SELECT 
        shipment_id,
        delivery_time,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY delivery_time) OVER(PARTITION BY city) as median_time
    FROM shipments
)
SELECT * 
FROM CityStats 
WHERE delivery_time > 3 * median_time;
```

---

### 22. Sudden spike detection
**Question:**
> Detect days where shipment volume increased by > 50% day-over-day.

**SQL:**
```sql
WITH DailyVol AS (
    SELECT date, COUNT(*) as vol 
    FROM shipments GROUP BY 1
)
, Lagged AS (
    SELECT 
        date, 
        vol, 
        LAG(vol) OVER(ORDER BY date) as prev_vol
    FROM DailyVol
)
SELECT * 
FROM Lagged 
WHERE prev_vol > 0 
  AND (vol - prev_vol)::float / prev_vol > 0.5;
```

---

### 23. Broken pipeline detection
**Question:**
> Find days where shipments exist but **no status updates were recorded**.

**SQL:**
```sql
SELECT s.create_date::date
FROM shipments s
LEFT JOIN shipment_events e ON s.shipment_id = e.shipment_id
GROUP BY 1
HAVING COUNT(e.event_id) = 0;
```
*Logic:* We have rows in the `shipments` master table, but joining to the child `events` table yields NULLs/Zero count.

---

### 24. Rewrite for performance
**Question:**
> Rewrite a slow query using multiple subqueries (e.g., getting Max Date per ID) using window functions.

**Before (Slow - Self Join):**
```sql
SELECT * FROM events e
JOIN (SELECT id, MAX(time) as m FROM events GROUP BY id) max_t
ON e.id = max_t.id AND e.time = max_t.m;
```
**After (Fast - Window):**
```sql
SELECT *
FROM (
    SELECT *, RANK() OVER(PARTITION BY id ORDER BY time DESC) as rn
    FROM events
) t
WHERE rn = 1;
```
*Why?* The Self-Join scans the table twice (once for details, once for aggregation). The Window function scans it once.

---

### 25. Partition-pruning logic
**Question:**
> Write SQL that **guarantees partition pruning** on a date column. Use `event_timestamp`.

**Answer:**
*   **Bad (No Pruning):** `WHERE DATE(event_timestamp) = '2023-01-01'`.
    *   Applying a function (`DATE()`) to the column hides the raw value from the optimizer in many engines. It scans all partitions.
*   **Good (Pruning):** `WHERE event_timestamp >= '2023-01-01 00:00:00' AND event_timestamp < '2023-01-02 00:00:00'`.
    *   Comparing the raw column to literals allows the engine to skip files outside that range.

---

### 26. Join explosion prevention
**Question:**
> Rewrite a query to avoid cartesian multiplication.

**Scenario:** Joining `Orders` (1 row) to `Shipments` (5 rows) to `Refunds` (2 rows) to sum revenue.
*   **Bad:** `SUM(order_amt)` on the joined result. A $100 order appears 5*2=10 times. Sum = $1000 (Wrong).
*   **Fix:** Pre-aggregate before joining.
    1.  Calculated `TotalRefunds` per OrderID in CTE.
    2.  Calculate `TotalShipments` per OrderID in CTE.
    3.  Join Order to those 1-to-1 aggregates.
