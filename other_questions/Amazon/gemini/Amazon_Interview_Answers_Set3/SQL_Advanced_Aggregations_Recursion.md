# Amazon Advanced SQL - Aggregations, Recursion & Logic (Q13-Q20)

This section covers **Conditional Logic, Recursive Hierarchies, and Complex Joins**.

---

### 13. Conditional counts
**Question:**
> Count shipments that:
> 1. Were delayed
> 2. Eventually delivered
> 3. Never breached SLA again after recovery

**Solution Strategy:**
Use `CASE WHEN` inside `SUM()` (or `COUNT()`).
**SQL:**
```sql
SELECT 
    COUNT(CASE WHEN status = 'DELAYED' THEN 1 END) as count_delayed,
    COUNT(CASE WHEN status = 'DELIVERED' THEN 1 END) as count_delivered,
    
    -- "Eventual" delivery requires checking if the shipment_id *has* a 'DELIVERED' row
    COUNT(DISTINCT CASE WHEN shipment_id IN (SELECT shipment_id FROM events WHERE status='DELIVERED') THEN shipment_id END) as eventually_delivered
FROM events;
```
*Note:* Simple `CASE` works for single-row attributes. For "Eventual" status (cross-row), you often need a flag at the shipment level first.

---

### 14. Funnel analysis (Amazon-style)
**Question:**
> Shipment lifecycle funnel: CREATED → PICKED → SHIPPED → DELIVERED.
> Calculate **drop-off rate** at each stage.

**SQL:**
```sql
SELECT 
    COUNT(DISTINCT CASE WHEN status = 'CREATED' THEN shipment_id END) as step1_created,
    COUNT(DISTINCT CASE WHEN status = 'PICKED' THEN shipment_id END) as step2_picked,
    COUNT(DISTINCT CASE WHEN status = 'SHIPPED' THEN shipment_id END) as step3_shipped,
    
    -- Drop-off Calculation (Created -> Picked)
    1.0 - (COUNT(DISTINCT CASE WHEN status = 'PICKED' THEN shipment_id END)::decimal / 
           NULLIF(COUNT(DISTINCT CASE WHEN status = 'CREATED' THEN shipment_id END), 0)) as dropoff_step1_2
FROM events;
```

---

### 15. Mutually exclusive metrics
**Question:**
> Categorize shipments into: "On-time", "Late but recovered", "Late and failed". Return counts.

**Solution Strategy:**
1.  **Tagging:** Create a CTE that tags each shipment with `is_late`, `is_delivered`.
2.  **Logic:**
    *   On-time: `!is_late AND is_delivered`
    *   Late Recovered: `is_late AND is_delivered`
    *   Late Failed: `is_late AND !is_delivered`

**SQL:**
```sql
WITH ShipmentTags AS (
    SELECT 
        shipment_id,
        MAX(CASE WHEN status = 'DELAYED' THEN 1 ELSE 0 END) as was_late,
        MAX(CASE WHEN status = 'DELIVERED' THEN 1 ELSE 0 END) as is_delivered
    FROM events
    GROUP BY 1
)
SELECT 
    COUNT(CASE WHEN was_late=0 AND is_delivered=1 THEN 1 END) as on_time,
    COUNT(CASE WHEN was_late=1 AND is_delivered=1 THEN 1 END) as late_recovered,
    COUNT(CASE WHEN was_late=1 AND is_delivered=0 THEN 1 END) as late_failed
FROM ShipmentTags;
```

---

### 16. Recursive dependency tracking
**Question:**
> Track shipment transfers across hubs recursively (Hub A -> Hub B -> Hub C) and calculate total hops.

**Solution Strategy:**
Use **Recursive CTE**.
1.  **Anchor:** Select shipments at their starting hub (`hop = 0`).
2.  **Recursive Member:** Join component `ON current_hub = previous_hub` (linear logic).
3.  **Stop:** When no next hub exists.

**SQL:**
```sql
WITH RECURSIVE TransferPath AS (
    -- Anchor
    SELECT shipment_id, current_hub, next_hub, 1 as hop_count
    FROM transfers
    WHERE prev_hub IS NULL
    
    UNION ALL
    
    -- Recursion
    SELECT t.shipment_id, t.current_hub, t.next_hub, tp.hop_count + 1
    FROM transfers t
    JOIN TransferPath tp ON t.prev_hub = tp.current_hub AND t.shipment_id = tp.shipment_id
)
SELECT shipment_id, MAX(hop_count) 
FROM TransferPath 
GROUP BY 1;
```

---

### 17. Graph-style traversal
**Question:**
> Find all downstream hubs affected if 'Hub A' fails.

**SQL:**
```sql
WITH RECURSIVE Downstream AS (
    SELECT destination_hub FROM routes WHERE source_hub = 'Hub A'
    UNION
    SELECT r.destination_hub 
    FROM routes r
    JOIN Downstream d ON r.source_hub = d.destination_hub
)
SELECT * FROM Downstream;
```

---

### 18. Correlated subquery challenge
**Question:**
> Find shipments whose delivery time is **greater than the average of its city on that day**.

**SQL (Efficient Window Function Approach):**
```sql
WITH CityStats AS (
    SELECT *, AVG(delivery_seconds) OVER(PARTITION BY city, date) as city_avg
    FROM shipments
)
SELECT shipment_id 
FROM CityStats 
WHERE delivery_seconds > city_avg;
```
*Note:* A correlated subquery (WHERE delivery > (SELECT avg FROM ... WHERE city=outer.city)) triggers row-by-row execution in older engines. Window functions scan once.

---

### 19. Anti-join logic
**Question:**
> Find shipments that **never entered a FAILED state**, even temporarily.

**Solution Strategy:**
*   **NOT IN** or **NOT EXISTS** or **LEFT JOIN / IS NULL**.
*   `LEFT JOIN` is typically most distinctive and reliable regarding NULLs.

**SQL:**
```sql
SELECT DISTINCT s.shipment_id
FROM shipments s
LEFT JOIN shipment_events e ON s.shipment_id = e.shipment_id AND e.status = 'FAILED'
WHERE e.shipment_id IS NULL;
```

---

### 20. Exists vs Join semantics
**Question:**
> Write a query that behaves differently with `EXISTS` than with `JOIN`.

**Answer:**
*   **JOIN:** If the right table has duplicates (e.g., 2 FAILED events), a JOIN will duplicate the left table's rows (1 shipment -> 2 rows).
*   **EXISTS / IN:** Simply checks for presence. Even if right table has 100 matches, the left row is returned only once.
*   *Amazon Trap:* If you use JOIN for "filtering", you must use `DISTINCT` to fix the fan-out, which is expensive. `EXISTS` is the correct Semijoin operator.
