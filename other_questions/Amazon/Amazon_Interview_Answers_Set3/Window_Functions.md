# Amazon Advanced SQL - Window Functions (Q1-Q5)

This section covers **Multi-Stage Window Function Problems**, a staple of Amazon's "Bar Raiser" SQL rounds.

---

### 1. Latest valid record with conditions
**Question:**
> For each `shipment_id`, find the **latest status**, but **ignore statuses marked as invalid** (e.g., `is_valid = false`).
> If the latest record is invalid, return the **previous valid one**.

**Solution Strategy:**
1.  **Filter First:** The simplest and most performant way is to filter out invalid records *before* ranking.
2.  **Rank:** Use `ROW_NUMBER()` ordered by timestamp descending.
3.  **Select:** Pick the top 1.

**SQL:**
```sql
WITH ValidEvents AS (
    SELECT 
        shipment_id,
        status,
        event_timestamp
    FROM shipment_events
    WHERE is_valid = TRUE  -- Critical step: remove noise first
)
, Ranked AS (
    SELECT 
        shipment_id,
        status,
        event_timestamp,
        ROW_NUMBER() OVER(PARTITION BY shipment_id ORDER BY event_timestamp DESC) as rn
    FROM ValidEvents
)
SELECT shipment_id, status, event_timestamp
FROM Ranked
WHERE rn = 1;
```
*Edge Case:* What if a shipment has *only* invalid records? The query returns nothing for that ID. If you need to return the ID with a NULL status, use a `LEFT JOIN` from a master `shipments` table to this result.

---

### 2. Top-N per group with ties
**Question:**
> Find **top 3 delivery routes per city per month** (by volume), but:
> * Include ties (e.g., if Rank 3 and 4 have same volume, both should show provided the logic allows it, or use `DENSE_RANK`).
> * Exclude routes with fewer than 10 shipments.

**Solution Strategy:**
1.  **Aggregate:** Calculate volume per route/city/month.
2.  **Filter:** `HAVING count > 10`.
3.  **Rank:** Use `DENSE_RANK()` (1, 2, 2, 3) or `RANK()` (1, 2, 2, 4) depending on exact tie requirement. Usually `DENSE_RANK` is safer to ensure you get "Top 3 distinct volume levels".
4.  **Filter Rank:** `WHERE rnk <= 3`.

**SQL:**
```sql
WITH MonthlyVolume AS (
    SELECT 
        DATE_TRUNC('month', ship_date) as ord_month,
        city,
        route_id,
        COUNT(*) as volume
    FROM shipments
    GROUP BY 1, 2, 3
    HAVING COUNT(*) >= 10
)
, RankedRoutes AS (
    SELECT 
        ord_month,
        city,
        route_id,
        volume,
        DENSE_RANK() OVER(PARTITION BY ord_month, city ORDER BY volume DESC) as rnk
    FROM MonthlyVolume
)
SELECT * 
FROM RankedRoutes 
WHERE rnk <= 3;
```

---

### 3. Gap & Island (Continuous Delay)
**Question:**
> Find **continuous delivery delay periods** for each shipment.
> *Example:* 
> 10:00 (Delayed), 10:15 (Delayed), 10:30 (On Time), 11:00 (Delayed), 11:15 (Delayed).
> Result should show **Two** distinct delay periods, not four individual rows.

**Solution Strategy:**
1.  **Identify Islands:** An "island" is a group of consecutive rows with the same status.
2.  **Lag Method:** Compare current status with previous status. If different, it's the start of a new group.
3.  **Grouping:** A classic trick is `Row_Number() OVER(Order by Time) - Row_Number() OVER(Partition by Status Order by Time)`. This math generates a constant ID for consecutive groups.

**SQL (Using the Lag/Flag Method):**
```sql
WITH MarkedChanges AS (
    SELECT 
        shipment_id,
        status,
        event_timestamp,
        -- Set a flag only when status changes from previous row
        CASE WHEN status = LAG(status) OVER(PARTITION BY shipment_id ORDER BY event_timestamp) 
             THEN 0 ELSE 1 END as is_new_group
    FROM shipment_events
    WHERE status = 'DELAYED' -- Focus only on delay intervals if requested
)
, GroupIDs AS (
    SELECT 
        *,
        -- Cumulative sum of flags creates a unique ID for each group
        SUM(is_new_group) OVER(PARTITION BY shipment_id ORDER BY event_timestamp) as group_id
    FROM MarkedChanges
)
SELECT 
    shipment_id,
    group_id,
    MIN(event_timestamp) as start_delay,
    MAX(event_timestamp) as end_delay
FROM GroupIDs
GROUP BY 1, 2;
```

---

### 4. Change detection
**Question:**
> Identify shipments where the **status changed backward** (e.g., DELIVERED → IN_TRANSIT).

**Solution Strategy:**
1.  **Map Status to Integer:** Assign a numeric weight to disjoint lifecycle stages (CREATED=1, SHIPPED=2, DELIVERED=3).
2.  **Lag & Compare:** Compare `Current_Weight` with `Previous_Weight`.
3.  **Detect:** If `Current < Previous`, it moved backward.

**SQL:**
```sql
WITH MappedStatus AS (
    SELECT 
        shipment_id,
        status,
        event_timestamp,
        CASE status 
            WHEN 'CREATED' THEN 1 
            WHEN 'PICKED' THEN 2
            WHEN 'SHIPPED' THEN 3
            WHEN 'DELIVERED' THEN 4 
            ELSE 0 END as status_rank
    FROM events
)
, PreviousState AS (
    SELECT 
        *,
        LAG(status_rank) OVER(PARTITION BY shipment_id ORDER BY event_timestamp) as prev_rank
    FROM MappedStatus
)
SELECT DISTINCT shipment_id
FROM PreviousState
WHERE status_rank < prev_rank 
  AND prev_rank IS NOT NULL; -- Ignore first row
```

---

### 5. Rolling metrics with exclusions
**Question:**
> Compute a **7-day rolling average delivery time**, excluding weekends.

**Solution Strategy:**
1.  **Filter First:** Remove weekends from the dataset entirely.
2.  **Window Frame:** Use `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW`.
    *   *Note:* standard `RANGE BETWEEN INTERVAL '7' DAYS` works on calendar time (would include missing weekends). Because we filtered weekends out, rows are no longer consecutive days. If the business wants "Last 7 *Business* Days", utilizing `ROWS` on the filtered set is accurate.

**SQL:**
```sql
WITH BusinessDays AS (
    SELECT 
        date,
        avg_delivery_seconds
    FROM daily_metrics
    WHERE EXTRACT(DOW FROM date) NOT IN (0, 6) -- 0=Sun, 6=Sat (Dialect dependent)
)
SELECT 
    date,
    avg_delivery_seconds,
    AVG(avg_delivery_seconds) OVER(
        ORDER BY date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as rolling_7_biz_day_avg
FROM BusinessDays;
```
