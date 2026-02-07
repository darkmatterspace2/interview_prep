# SQL Interview Questions & Answers (Question Bank 1)

> **Amazon Data Engineer Style** - Logistics/Transportation Domain Focus

---

## 1️⃣ Basics & Aggregations

### Q1: Find total shipments per day

```sql
SELECT 
    DATE(shipment_date) AS ship_date,
    COUNT(*) AS total_shipments
FROM shipments
GROUP BY DATE(shipment_date)
ORDER BY ship_date;
```

**Key Points:**
- Use `DATE()` to truncate timestamp to date
- `COUNT(*)` counts all rows; `COUNT(shipment_id)` excludes nulls

---

### Q2: Count distinct shipment IDs per region

```sql
SELECT 
    region,
    COUNT(DISTINCT shipment_id) AS unique_shipments
FROM shipments
GROUP BY region;
```

**Key Points:**
- `COUNT(DISTINCT ...)` eliminates duplicates
- Useful for scenarios with duplicate events per shipment

---

### Q3: Find regions with more than 10,000 shipments in a month

```sql
SELECT 
    region,
    DATE_TRUNC('month', shipment_date) AS month,
    COUNT(*) AS shipment_count
FROM shipments
GROUP BY region, DATE_TRUNC('month', shipment_date)
HAVING COUNT(*) > 10000
ORDER BY month, shipment_count DESC;
```

**Key Points:**
- `HAVING` filters after aggregation (vs `WHERE` before)
- `DATE_TRUNC` groups by month efficiently

---

### Q4: Calculate average delivery time per carrier

```sql
SELECT 
    carrier_name,
    AVG(DATEDIFF('hour', pickup_time, delivery_time)) AS avg_delivery_hours,
    COUNT(*) AS total_deliveries
FROM shipments
WHERE delivery_time IS NOT NULL
GROUP BY carrier_name
ORDER BY avg_delivery_hours;
```

**Key Points:**
- Filter for completed deliveries to avoid NULL arithmetic
- Include count to assess statistical significance

---

### Q5: Find max, min, avg transit time per route

```sql
SELECT 
    origin,
    destination,
    MIN(transit_hours) AS min_transit,
    MAX(transit_hours) AS max_transit,
    AVG(transit_hours) AS avg_transit,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY transit_hours) AS median_transit
FROM shipments
GROUP BY origin, destination
ORDER BY avg_transit DESC;
```

**Key Points:**
- Median (percentile) is more robust than average for skewed data
- Route = (origin, destination) pair

---

## 2️⃣ Joins

### Q6: Get shipments that never reached "DELIVERED" status

```sql
-- Method 1: NOT EXISTS
SELECT s.*
FROM shipments s
WHERE NOT EXISTS (
    SELECT 1 
    FROM shipment_events e 
    WHERE e.shipment_id = s.shipment_id 
    AND e.status = 'DELIVERED'
);

-- Method 2: LEFT JOIN + NULL check
SELECT s.*
FROM shipments s
LEFT JOIN shipment_events e 
    ON s.shipment_id = e.shipment_id 
    AND e.status = 'DELIVERED'
WHERE e.shipment_id IS NULL;
```

**Key Points:**
- `NOT EXISTS` is usually more efficient than `NOT IN` (handles NULLs correctly)
- Anti-join pattern: LEFT JOIN + WHERE IS NULL

---

### Q7: Find shipments with missing carrier information

```sql
SELECT s.*
FROM shipments s
LEFT JOIN carriers c ON s.carrier_id = c.carrier_id
WHERE c.carrier_id IS NULL
  AND s.carrier_id IS NOT NULL;  -- Shipment has carrier_id but no matching carrier
```

**Key Points:**
- Distinguish between: no carrier assigned vs assigned but missing in lookup
- This finds referential integrity violations

---

### Q8: Join shipment and event tables to get latest status

```sql
-- Using window function (most efficient)
WITH ranked_events AS (
    SELECT 
        shipment_id,
        status,
        event_time,
        ROW_NUMBER() OVER (PARTITION BY shipment_id ORDER BY event_time DESC) AS rn
    FROM shipment_events
)
SELECT 
    s.shipment_id,
    s.origin,
    s.destination,
    e.status AS current_status,
    e.event_time AS last_update
FROM shipments s
JOIN ranked_events e ON s.shipment_id = e.shipment_id AND e.rn = 1;
```

**Key Points:**
- `ROW_NUMBER() ... ORDER BY event_time DESC` gets latest per group
- Join on `rn = 1` filters to only latest record

---

### Q9: Identify shipments with inconsistent region mapping

```sql
SELECT 
    s.shipment_id,
    s.origin_region AS shipment_region,
    l.region AS location_region
FROM shipments s
JOIN locations l ON s.origin_location_id = l.location_id
WHERE s.origin_region != l.region;
```

**Key Points:**
- Data quality check: denormalized data should match normalized source
- Flag for investigation, not automatic correction

---

### Q10: LEFT vs INNER JOIN — when will counts differ?

**Answer:**

| Scenario | LEFT JOIN | INNER JOIN | Difference |
|----------|-----------|------------|------------|
| All shipments have carriers | Same | Same | None |
| Some shipments missing carrier | All shipments | Only matched | LEFT > INNER |
| Carrier has no shipments | No effect | No effect | None |

```sql
-- Example showing difference
SELECT 
    COUNT(*) AS left_count 
FROM shipments s 
LEFT JOIN carriers c ON s.carrier_id = c.carrier_id;

SELECT 
    COUNT(*) AS inner_count 
FROM shipments s 
INNER JOIN carriers c ON s.carrier_id = c.carrier_id;
```

**Key Points:**
- LEFT JOIN preserves all rows from left table (may have NULLs for missing matches)
- INNER JOIN only returns rows that match in both tables
- Use LEFT when you need "shipments regardless of carrier info"
- Use INNER when you only want "shipments with valid carrier"

---

## 3️⃣ Window Functions

### Q11: Latest status per shipment using ROW_NUMBER

```sql
SELECT shipment_id, status, event_time
FROM (
    SELECT 
        shipment_id,
        status,
        event_time,
        ROW_NUMBER() OVER (
            PARTITION BY shipment_id 
            ORDER BY event_time DESC
        ) AS rn
    FROM shipment_events
) ranked
WHERE rn = 1;
```

**Key Points:**
- `PARTITION BY` = your grouping (like GROUP BY for window)
- `ORDER BY DESC` + `rn = 1` = latest record
- Alternative: `FIRST_VALUE()` with `DISTINCT`

---

### Q12: Rank top 5 delay-prone cities per month

```sql
WITH city_delays AS (
    SELECT 
        DATE_TRUNC('month', delivery_date) AS month,
        destination_city,
        COUNT(*) FILTER (WHERE is_delayed = TRUE) AS delay_count,
        COUNT(*) AS total_shipments,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_delayed) / COUNT(*), 2) AS delay_rate
    FROM shipments
    GROUP BY 1, 2
),
ranked AS (
    SELECT 
        *,
        RANK() OVER (PARTITION BY month ORDER BY delay_rate DESC) AS rank
    FROM city_delays
)
SELECT * FROM ranked WHERE rank <= 5;
```

**Key Points:**
- `RANK()` handles ties (1,1,3); `DENSE_RANK()` would be (1,1,2)
- `FILTER (WHERE ...)` is cleaner than `CASE WHEN` for conditional counts
- Rate is more meaningful than absolute count

---

### Q13: Calculate running total of shipments per day

```sql
SELECT 
    ship_date,
    daily_count,
    SUM(daily_count) OVER (ORDER BY ship_date) AS running_total,
    SUM(daily_count) OVER (
        ORDER BY ship_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7day
FROM (
    SELECT 
        DATE(shipment_date) AS ship_date,
        COUNT(*) AS daily_count
    FROM shipments
    GROUP BY DATE(shipment_date)
) daily;
```

**Key Points:**
- `SUM() OVER (ORDER BY ...)` = cumulative/running total
- `ROWS BETWEEN` defines the window frame for rolling calculations

---

### Q14: Find previous and next status using LAG/LEAD

```sql
SELECT 
    shipment_id,
    event_time,
    status AS current_status,
    LAG(status) OVER (PARTITION BY shipment_id ORDER BY event_time) AS prev_status,
    LEAD(status) OVER (PARTITION BY shipment_id ORDER BY event_time) AS next_status,
    event_time - LAG(event_time) OVER (PARTITION BY shipment_id ORDER BY event_time) AS time_in_prev_status
FROM shipment_events
ORDER BY shipment_id, event_time;
```

**Key Points:**
- `LAG(col, n, default)` looks n rows back (default=1)
- `LEAD(col, n, default)` looks n rows forward
- Useful for detecting transitions (prev_status → current_status)

---

### Q15: Detect repeated status updates consecutively

```sql
WITH status_with_prev AS (
    SELECT 
        shipment_id,
        status,
        event_time,
        LAG(status) OVER (PARTITION BY shipment_id ORDER BY event_time) AS prev_status
    FROM shipment_events
)
SELECT *
FROM status_with_prev
WHERE status = prev_status;
```

**Key Points:**
- Consecutive duplicates: current = previous
- May indicate system bugs or unnecessary updates
- Consider also checking if time gap is very small (< 1 second)

---

## 4️⃣ Deduplication & Data Quality

### Q16: Remove duplicate shipment events

```sql
-- Keep the first occurrence
DELETE FROM shipment_events
WHERE event_id NOT IN (
    SELECT MIN(event_id)
    FROM shipment_events
    GROUP BY shipment_id, status, event_time
);

-- Or use CTE to identify duplicates
WITH duplicates AS (
    SELECT 
        event_id,
        ROW_NUMBER() OVER (
            PARTITION BY shipment_id, status, event_time 
            ORDER BY event_id
        ) AS rn
    FROM shipment_events
)
DELETE FROM shipment_events 
WHERE event_id IN (SELECT event_id FROM duplicates WHERE rn > 1);
```

**Key Points:**
- Define "duplicate" clearly (same shipment + status + time?)
- Keep earliest (MIN) or latest (MAX) based on business logic
- Test with SELECT first before DELETE

---

### Q17: Keep the most recent record per shipment

```sql
-- Using ROW_NUMBER to select latest
WITH ranked AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (
            PARTITION BY shipment_id 
            ORDER BY updated_at DESC
        ) AS rn
    FROM shipments
)
SELECT * FROM ranked WHERE rn = 1;

-- For permanent deduplication
CREATE TABLE shipments_deduped AS
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY shipment_id ORDER BY updated_at DESC) AS rn
    FROM shipments
) WHERE rn = 1;
```

---

### Q18: Identify shipments with duplicate tracking IDs

```sql
SELECT 
    tracking_id,
    COUNT(*) AS duplicate_count,
    ARRAY_AGG(shipment_id) AS shipment_ids
FROM shipments
GROUP BY tracking_id
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;
```

**Key Points:**
- `ARRAY_AGG` shows which shipments share the tracking ID
- Important for data quality: tracking IDs should be unique

---

### Q19: Count late-arriving events

```sql
-- Events arriving after processing window closed
SELECT 
    DATE(event_time) AS event_date,
    COUNT(*) AS late_events
FROM shipment_events
WHERE event_time < processing_time - INTERVAL '1 hour'  -- Event time > 1 hr before processing
GROUP BY DATE(event_time);

-- Alternative: Events for "closed" shipments
SELECT COUNT(*) AS late_events
FROM shipment_events e
JOIN shipments s ON e.shipment_id = s.shipment_id
WHERE s.status = 'DELIVERED'
  AND e.event_time > s.delivery_time;
```

---

### Q20: Detect missing status transitions

```sql
-- Expected flow: CREATED → PICKED_UP → IN_TRANSIT → OUT_FOR_DELIVERY → DELIVERED
WITH status_sequence AS (
    SELECT 
        shipment_id,
        ARRAY_AGG(status ORDER BY event_time) AS status_path
    FROM shipment_events
    GROUP BY shipment_id
)
SELECT 
    shipment_id,
    status_path
FROM status_sequence
WHERE NOT (
    'CREATED' = ANY(status_path) AND
    'PICKED_UP' = ANY(status_path) AND
    'DELIVERED' = ANY(status_path)
);
```

---

## 5️⃣ Time-Based Analytics

### Q21: Shipments delivered within SLA

```sql
SELECT 
    COUNT(*) AS total_delivered,
    COUNT(*) FILTER (WHERE delivery_time <= promised_delivery_time) AS on_time,
    ROUND(100.0 * COUNT(*) FILTER (WHERE delivery_time <= promised_delivery_time) / COUNT(*), 2) AS sla_compliance_pct
FROM shipments
WHERE status = 'DELIVERED';
```

---

### Q22: Calculate 7-day rolling average delivery time

```sql
WITH daily_avg AS (
    SELECT 
        DATE(delivery_time) AS delivery_date,
        AVG(EXTRACT(EPOCH FROM (delivery_time - pickup_time))/3600) AS avg_hours
    FROM shipments
    WHERE status = 'DELIVERED'
    GROUP BY DATE(delivery_time)
)
SELECT 
    delivery_date,
    avg_hours AS daily_avg_hours,
    AVG(avg_hours) OVER (
        ORDER BY delivery_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7day_avg
FROM daily_avg;
```

---

### Q23: Sessionize shipment events by inactivity gap

```sql
-- Define new session when gap > 2 hours
WITH with_gap AS (
    SELECT 
        shipment_id,
        event_time,
        status,
        event_time - LAG(event_time) OVER (
            PARTITION BY shipment_id ORDER BY event_time
        ) AS gap_from_prev
    FROM shipment_events
),
with_session_flag AS (
    SELECT 
        *,
        CASE WHEN gap_from_prev > INTERVAL '2 hours' OR gap_from_prev IS NULL 
             THEN 1 ELSE 0 END AS new_session
    FROM with_gap
)
SELECT 
    shipment_id,
    event_time,
    status,
    SUM(new_session) OVER (
        PARTITION BY shipment_id ORDER BY event_time
    ) AS session_id
FROM with_session_flag;
```

---

### Q24: Detect shipments stuck in same status > 24 hrs

```sql
WITH status_duration AS (
    SELECT 
        shipment_id,
        status,
        event_time,
        LEAD(event_time) OVER (
            PARTITION BY shipment_id ORDER BY event_time
        ) AS next_event_time,
        COALESCE(
            LEAD(event_time) OVER (PARTITION BY shipment_id ORDER BY event_time),
            CURRENT_TIMESTAMP
        ) - event_time AS duration_in_status
    FROM shipment_events
)
SELECT *
FROM status_duration
WHERE duration_in_status > INTERVAL '24 hours'
  AND status NOT IN ('DELIVERED', 'CANCELLED');  -- Exclude terminal statuses
```

---

### Q25: Compare week-over-week shipment volume

```sql
WITH weekly_volumes AS (
    SELECT 
        DATE_TRUNC('week', shipment_date) AS week_start,
        COUNT(*) AS shipment_count
    FROM shipments
    GROUP BY DATE_TRUNC('week', shipment_date)
)
SELECT 
    week_start,
    shipment_count,
    LAG(shipment_count) OVER (ORDER BY week_start) AS prev_week,
    shipment_count - LAG(shipment_count) OVER (ORDER BY week_start) AS wow_change,
    ROUND(100.0 * (shipment_count - LAG(shipment_count) OVER (ORDER BY week_start)) 
          / LAG(shipment_count) OVER (ORDER BY week_start), 2) AS wow_pct_change
FROM weekly_volumes
ORDER BY week_start;
```

---

## 6️⃣ Advanced SQL (Part 2 Questions)

### Redshift: Time between "Out for Delivery" and "Delivered"

```sql
WITH delivery_events AS (
    SELECT 
        package_id,
        MAX(CASE WHEN status = 'Out for Delivery' THEN timestamp END) AS ofd_time,
        MAX(CASE WHEN status = 'Delivered' THEN timestamp END) AS delivered_time
    FROM PackageScans
    WHERE DATE(timestamp) = CURRENT_DATE - 1
    GROUP BY package_id
)
SELECT 
    package_id,
    ofd_time,
    delivered_time,
    DATEDIFF('minute', ofd_time, delivered_time) AS delivery_minutes
FROM delivery_events
WHERE ofd_time IS NOT NULL AND delivered_time IS NOT NULL;
```

---

### Redshift: Top 3 delay-prone lanes per week

```sql
WITH lane_delays AS (
    SELECT 
        DATE_TRUNC('week', delivery_date) AS week,
        source_city || ' -> ' || dest_city AS lane,
        AVG(actual_transit_days - expected_transit_days) AS avg_delay_days,
        COUNT(*) AS shipment_count
    FROM shipments
    WHERE actual_transit_days > expected_transit_days
    GROUP BY 1, 2
),
ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY week ORDER BY avg_delay_days DESC) AS rank
    FROM lane_delays
)
SELECT * FROM ranked WHERE rank <= 3;
```

---

### Redshift Optimization: DISTKEY and SORTKEY

**Answer:**

```sql
-- For a shipments table queried by date and joined on carrier_id
CREATE TABLE shipments (
    shipment_id BIGINT,
    shipment_date DATE,
    carrier_id INT,
    ...
)
DISTKEY(carrier_id)    -- Distribute by join key
SORTKEY(shipment_date);  -- Sort by filter/range key

-- Debugging slow queries:
-- 1. Check EXPLAIN plan
EXPLAIN SELECT ...;

-- 2. Analyze table statistics
ANALYZE shipments;

-- 3. Check for data skew
SELECT carrier_id, COUNT(*) 
FROM shipments 
GROUP BY carrier_id 
ORDER BY COUNT(*) DESC;

-- 4. Vacuum to reclaim space
VACUUM shipments;
```

**Key Points:**
- **DISTKEY:** Choose column used in JOINs (distributes matching rows to same node)
- **SORTKEY:** Choose column used in WHERE/range filters (enables skip-scan)
- Avoid DISTKEY on high-cardinality columns with skew

---

### Gaps and Islands: Consecutive Driver Active Days

```sql
WITH numbered AS (
    SELECT 
        driver_id,
        active_date,
        active_date - (ROW_NUMBER() OVER (PARTITION BY driver_id ORDER BY active_date))::INT AS grp
    FROM driver_activity
),
islands AS (
    SELECT 
        driver_id,
        MIN(active_date) AS start_date,
        MAX(active_date) AS end_date,
        COUNT(*) AS consecutive_days
    FROM numbered
    GROUP BY driver_id, grp
)
SELECT * FROM islands
WHERE consecutive_days >= 7  -- Find drivers active 7+ consecutive days
ORDER BY driver_id, start_date;
```

**Key Points:**
- "Islands" = consecutive sequences
- Subtract row_number from date → same group for consecutive dates
- Classic pattern for sequence detection
