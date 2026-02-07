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

---

# Question Bank 3: Advanced & Hard SQL Problems

> **Amazon Data Engineer Style** - Logic-Heavy, Multi-Step, Edge-Case–Loaded Queries

---

## 1️⃣ Multi-Stage Window Function Problems

### Q1: Latest valid record with conditions

> For each `shipment_id`, find the **latest status**, but **ignore statuses marked as invalid**.
> If the latest record is invalid, return the **previous valid one**.

```sql
WITH ranked_valid AS (
    SELECT 
        shipment_id,
        status,
        event_time,
        is_valid,
        -- Rank only among VALID records
        ROW_NUMBER() OVER (
            PARTITION BY shipment_id 
            ORDER BY event_time DESC
        ) AS rn,
        -- Also track if this is truly latest (valid or not)
        FIRST_VALUE(is_valid) OVER (
            PARTITION BY shipment_id 
            ORDER BY event_time DESC
        ) AS latest_is_valid
    FROM shipment_events
    WHERE is_valid = 1  -- Only consider valid records
)
SELECT 
    shipment_id,
    status AS latest_valid_status,
    event_time
FROM ranked_valid
WHERE rn = 1;
```

**Alternative: Handle case where ALL records might be invalid**

```sql
WITH all_ranked AS (
    SELECT 
        shipment_id,
        status,
        event_time,
        is_valid,
        ROW_NUMBER() OVER (
            PARTITION BY shipment_id 
            ORDER BY event_time DESC
        ) AS overall_rn,
        ROW_NUMBER() OVER (
            PARTITION BY shipment_id, 
                         CASE WHEN is_valid = 1 THEN 0 ELSE 1 END
            ORDER BY event_time DESC
        ) AS valid_rn
    FROM shipment_events
)
SELECT 
    shipment_id,
    COALESCE(
        MAX(CASE WHEN is_valid = 1 AND valid_rn = 1 THEN status END),
        MAX(CASE WHEN overall_rn = 1 THEN status END)  -- Fallback to latest if no valid
    ) AS final_status
FROM all_ranked
GROUP BY shipment_id;
```

**Key Points:**
- Filter BEFORE ranking to get "latest among valid"
- Use COALESCE for fallback logic
- Consider edge case: no valid records exist

---

### Q2: Top-N per group with ties

> Find **top 3 delivery routes per city per month**, but:
> - Include ties
> - Exclude routes with fewer than 10 shipments

```sql
WITH route_stats AS (
    SELECT 
        city,
        DATE_TRUNC('month', delivery_date) AS month,
        route_id,
        COUNT(*) AS shipment_count,
        AVG(delivery_time_hours) AS avg_delivery_time
    FROM shipments
    GROUP BY city, DATE_TRUNC('month', delivery_date), route_id
    HAVING COUNT(*) >= 10  -- Exclude low-volume routes
),
ranked AS (
    SELECT 
        *,
        DENSE_RANK() OVER (
            PARTITION BY city, month 
            ORDER BY shipment_count DESC
        ) AS rank
    FROM route_stats
)
SELECT *
FROM ranked
WHERE rank <= 3  -- Top 3 with ties
ORDER BY city, month, rank;
```

**Key Points:**
- `DENSE_RANK()` for ties (vs `ROW_NUMBER()` which breaks ties)
- `HAVING` filters BEFORE ranking
- Filter on rank AFTER the window function

---

### Q3: Gap & island (Amazon favorite)

> Find **continuous delivery delay periods** for each shipment where delay > 30 minutes.

```sql
WITH delay_events AS (
    SELECT 
        shipment_id,
        event_time,
        delay_minutes,
        CASE WHEN delay_minutes > 30 THEN 1 ELSE 0 END AS is_delayed
    FROM shipment_events
),
islands AS (
    SELECT 
        *,
        -- Subtract row_number to create groups for consecutive delays
        event_time - INTERVAL '1 minute' * ROW_NUMBER() OVER (
            PARTITION BY shipment_id, is_delayed
            ORDER BY event_time
        ) AS grp
    FROM delay_events
    WHERE is_delayed = 1
)
SELECT 
    shipment_id,
    MIN(event_time) AS delay_period_start,
    MAX(event_time) AS delay_period_end,
    COUNT(*) AS consecutive_delay_events,
    MAX(delay_minutes) AS max_delay_in_period
FROM islands
GROUP BY shipment_id, grp
ORDER BY shipment_id, delay_period_start;
```

**Key Points:**
- Gap & island pattern: subtract row_number from sequence
- Consecutive values get same "grp" after subtraction
- Filter to delayed events BEFORE grouping

---

### Q4: Change detection (Status went backward)

> Identify shipments where the **status changed backward** (e.g., DELIVERED → IN_TRANSIT).

```sql
WITH status_order AS (
    SELECT 
        shipment_id,
        status,
        event_time,
        CASE status
            WHEN 'CREATED' THEN 1
            WHEN 'PICKED' THEN 2
            WHEN 'IN_TRANSIT' THEN 3
            WHEN 'OUT_FOR_DELIVERY' THEN 4
            WHEN 'DELIVERED' THEN 5
            ELSE 0
        END AS status_rank,
        LAG(CASE status
            WHEN 'CREATED' THEN 1
            WHEN 'PICKED' THEN 2
            WHEN 'IN_TRANSIT' THEN 3
            WHEN 'OUT_FOR_DELIVERY' THEN 4
            WHEN 'DELIVERED' THEN 5
            ELSE 0
        END) OVER (
            PARTITION BY shipment_id 
            ORDER BY event_time
        ) AS prev_status_rank
    FROM shipment_events
)
SELECT DISTINCT shipment_id
FROM status_order
WHERE status_rank < prev_status_rank;  -- Current rank LOWER than previous = went backward
```

**Key Points:**
- Define explicit ordering for statuses
- `LAG()` to compare with previous record
- Backward = current rank < previous rank

---

### Q5: Rolling metrics with exclusions

> Compute a **7-day rolling average delivery time**, excluding weekends and holidays.

```sql
WITH business_days AS (
    SELECT 
        delivery_date,
        shipment_id,
        delivery_time_hours,
        -- Exclude weekends
        EXTRACT(DOW FROM delivery_date) NOT IN (0, 6) AS is_weekday,
        -- Exclude holidays (join with holiday table)
        h.holiday_date IS NULL AS is_not_holiday
    FROM shipments s
    LEFT JOIN holidays h ON s.delivery_date = h.holiday_date
),
filtered AS (
    SELECT *
    FROM business_days
    WHERE is_weekday AND is_not_holiday
)
SELECT 
    delivery_date,
    delivery_time_hours,
    AVG(delivery_time_hours) OVER (
        ORDER BY delivery_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7_business_day_avg
FROM filtered
ORDER BY delivery_date;
```

**Alternative: Count exactly 7 business days (not calendar days)**

```sql
WITH numbered AS (
    SELECT 
        delivery_date,
        delivery_time_hours,
        ROW_NUMBER() OVER (ORDER BY delivery_date) AS business_day_num
    FROM shipments
    WHERE EXTRACT(DOW FROM delivery_date) NOT IN (0, 6)
      AND delivery_date NOT IN (SELECT holiday_date FROM holidays)
)
SELECT 
    delivery_date,
    delivery_time_hours,
    AVG(delivery_time_hours) OVER (
        ORDER BY business_day_num
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7_business_day_avg
FROM numbered;
```

**Key Points:**
- Filter out weekends: `DOW NOT IN (0, 6)` (Sunday=0, Saturday=6)
- LEFT JOIN holidays table to exclude
- Use `ROWS BETWEEN` for exact row count

---

## 2️⃣ Deduplication Under Constraints

### Q6: Complex dedup logic (Timestamp proximity)

> Deduplicate shipment events where:
> - Same shipment_id
> - Same status
> - Timestamp difference < 5 minutes
> Keep the **earliest record**.

```sql
WITH ordered_events AS (
    SELECT 
        *,
        LAG(event_time) OVER (
            PARTITION BY shipment_id, status 
            ORDER BY event_time
        ) AS prev_event_time
    FROM shipment_events
),
marked AS (
    SELECT 
        *,
        CASE 
            WHEN prev_event_time IS NULL THEN 1  -- First record
            WHEN event_time - prev_event_time > INTERVAL '5 minutes' THEN 1  -- Gap > 5 min
            ELSE 0  -- Duplicate (within 5 min)
        END AS is_new_group
    FROM ordered_events
),
grouped AS (
    SELECT 
        *,
        SUM(is_new_group) OVER (
            PARTITION BY shipment_id, status 
            ORDER BY event_time
        ) AS group_id
    FROM marked
)
SELECT 
    shipment_id,
    status,
    MIN(event_time) AS first_event_time,  -- Keep earliest
    COUNT(*) AS duplicates_merged
FROM grouped
GROUP BY shipment_id, status, group_id;
```

**Key Points:**
- Use `LAG()` to find time gap from previous record
- Create "group_id" using running SUM of new group markers
- `MIN(event_time)` keeps earliest in each group

---

### Q7: Partial duplicates (Same business key, different metadata)

> Identify records that are duplicates by business logic but differ in metadata.

```sql
WITH potential_dups AS (
    SELECT 
        shipment_id,
        order_id,
        status,
        -- Business key columns
        COUNT(*) AS record_count,
        COUNT(DISTINCT updated_by) AS unique_updaters,
        COUNT(DISTINCT source_system) AS unique_sources
    FROM shipment_events
    GROUP BY shipment_id, order_id, status
    HAVING COUNT(*) > 1  -- Has duplicates
)
SELECT 
    se.*,
    pd.record_count,
    pd.unique_updaters
FROM shipment_events se
JOIN potential_dups pd 
    ON se.shipment_id = pd.shipment_id 
    AND se.order_id = pd.order_id 
    AND se.status = pd.status
WHERE pd.unique_updaters > 1 OR pd.unique_sources > 1  -- Metadata differs
ORDER BY se.shipment_id, se.event_time;
```

**Key Points:**
- Define "business key" (what makes records semantically same)
- Use COUNT DISTINCT on metadata columns
- HAVING > 1 on COUNT(DISTINCT metadata) = differs

---

### Q8: Soft deletes (Latest non-deleted)

> Given `is_deleted = 1`, return the **latest non-deleted record per key**, even if deleted records are newer.

```sql
WITH ranked AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (
            PARTITION BY shipment_id 
            ORDER BY 
                CASE WHEN is_deleted = 0 THEN 0 ELSE 1 END,  -- Non-deleted first
                event_time DESC  -- Then latest
        ) AS rn
    FROM shipment_events
)
SELECT *
FROM ranked
WHERE rn = 1;
```

**Alternative: Explicit filtering**

```sql
SELECT *
FROM shipment_events se
WHERE is_deleted = 0
  AND event_time = (
      SELECT MAX(event_time)
      FROM shipment_events se2
      WHERE se2.shipment_id = se.shipment_id
        AND se2.is_deleted = 0
  );
```

**Key Points:**
- Order by `is_deleted` first (non-deleted priority)
- Then by `event_time DESC` (latest within non-deleted)
- Handle case where ALL records are deleted (may want fallback)

---

## 3️⃣ Temporal & Time-Series SQL

### Q9: Event duration calculation

> Calculate time spent in each status per shipment.

```sql
WITH status_changes AS (
    SELECT 
        shipment_id,
        status,
        event_time AS status_start,
        LEAD(event_time) OVER (
            PARTITION BY shipment_id 
            ORDER BY event_time
        ) AS status_end
    FROM shipment_events
)
SELECT 
    shipment_id,
    status,
    status_start,
    status_end,
    COALESCE(status_end, CURRENT_TIMESTAMP) - status_start AS duration,
    EXTRACT(EPOCH FROM COALESCE(status_end, CURRENT_TIMESTAMP) - status_start) / 3600 AS hours
FROM status_changes
ORDER BY shipment_id, status_start;
```

**Key Points:**
- `LEAD()` gets next event time (when status ended)
- `COALESCE(status_end, CURRENT_TIMESTAMP)` for ongoing status
- Duration = end - start

---

### Q10: Late-arriving data

> Events arrive late. Recalculate **daily metrics** based on event_time, not ingestion_time.

```sql
-- BAD: Using ingestion_time (when record was loaded)
SELECT 
    DATE(ingestion_time) AS report_date,
    COUNT(*) AS shipments
FROM shipments
GROUP BY DATE(ingestion_time);

-- GOOD: Using event_time (when event actually happened)
SELECT 
    DATE(event_time) AS actual_date,
    COUNT(*) AS shipments,
    COUNT(CASE WHEN DATE(ingestion_time) > DATE(event_time) THEN 1 END) AS late_arrivals
FROM shipment_events
GROUP BY DATE(event_time)
ORDER BY actual_date;

-- For re-running: Include late arrivals from recent loads
SELECT 
    DATE(event_time) AS business_date,
    COUNT(*) AS total_events
FROM shipment_events
WHERE event_time >= '2024-01-01'  -- Business date range
  OR ingestion_time >= CURRENT_DATE - INTERVAL '3 days'  -- Recent loads
GROUP BY DATE(event_time);
```

**Key Points:**
- Always partition/group by `event_time` (business time)
- Track late arrivals separately for monitoring
- Re-processing window should catch late data

---

### Q11: Sessionization

> Group shipment events into sessions where gap > 30 minutes starts a new session.

```sql
WITH gaps AS (
    SELECT 
        shipment_id,
        event_time,
        status,
        LAG(event_time) OVER (
            PARTITION BY shipment_id 
            ORDER BY event_time
        ) AS prev_time,
        CASE 
            WHEN LAG(event_time) OVER (PARTITION BY shipment_id ORDER BY event_time) IS NULL 
                THEN 1
            WHEN event_time - LAG(event_time) OVER (PARTITION BY shipment_id ORDER BY event_time) 
                > INTERVAL '30 minutes' 
                THEN 1
            ELSE 0
        END AS new_session_flag
    FROM shipment_events
),
sessions AS (
    SELECT 
        *,
        SUM(new_session_flag) OVER (
            PARTITION BY shipment_id 
            ORDER BY event_time
        ) AS session_id
    FROM gaps
)
SELECT 
    shipment_id,
    session_id,
    MIN(event_time) AS session_start,
    MAX(event_time) AS session_end,
    COUNT(*) AS events_in_session,
    ARRAY_AGG(status ORDER BY event_time) AS status_sequence
FROM sessions
GROUP BY shipment_id, session_id
ORDER BY shipment_id, session_id;
```

**Key Points:**
- Flag new session when gap > 30 min
- Running SUM of flags creates session_id
- Aggregate per session for summary

---

### Q12: SLA breach detection (at any point)

> Find shipments that breached SLA **at any point**, not just final delivery.

```sql
WITH sla_checks AS (
    SELECT 
        se.shipment_id,
        se.event_time,
        se.status,
        s.promised_delivery_time,
        CASE 
            WHEN se.event_time > s.promised_delivery_time 
                 AND se.status != 'DELIVERED' 
            THEN 1 
            ELSE 0 
        END AS breached_at_this_point
    FROM shipment_events se
    JOIN shipments s ON se.shipment_id = s.shipment_id
)
SELECT DISTINCT shipment_id
FROM sla_checks
WHERE breached_at_this_point = 1;

-- With details
SELECT 
    shipment_id,
    MIN(event_time) AS first_breach_time,
    MAX(CASE WHEN status = 'DELIVERED' THEN event_time END) AS final_delivery,
    MAX(CASE WHEN status = 'DELIVERED' 
        AND event_time <= promised_delivery_time THEN 1 ELSE 0 END) AS recovered
FROM sla_checks
WHERE breached_at_this_point = 1
GROUP BY shipment_id;
```

**Key Points:**
- Check breach at EACH event, not just final
- "Recovered" = eventually delivered on time
- Use `DISTINCT` or `GROUP BY` to get unique shipments

---

## 4️⃣ Conditional Aggregations & Metrics Logic

### Q13: Conditional counts (Multi-condition)

> Count shipments that:
> - Were delayed
> - Eventually delivered
> - Never breached SLA again after recovery

```sql
WITH shipment_timeline AS (
    SELECT 
        shipment_id,
        MAX(CASE WHEN delay_minutes > 0 THEN 1 ELSE 0 END) AS was_delayed,
        MAX(CASE WHEN status = 'DELIVERED' THEN 1 ELSE 0 END) AS was_delivered,
        MAX(CASE WHEN status = 'DELIVERED' THEN event_time END) AS delivery_time
    FROM shipment_events
    GROUP BY shipment_id
),
recovery_check AS (
    SELECT 
        st.shipment_id,
        st.was_delayed,
        st.was_delivered,
        -- Check if any breach happened AFTER delivery
        MAX(CASE 
            WHEN se.delay_minutes > 0 AND se.event_time > st.delivery_time 
            THEN 1 ELSE 0 
        END) AS breached_after_recovery
    FROM shipment_timeline st
    LEFT JOIN shipment_events se ON st.shipment_id = se.shipment_id
    GROUP BY st.shipment_id, st.was_delayed, st.was_delivered, st.delivery_time
)
SELECT 
    COUNT(*) FILTER (WHERE was_delayed = 1) AS total_delayed,
    COUNT(*) FILTER (WHERE was_delayed = 1 AND was_delivered = 1) AS delayed_and_delivered,
    COUNT(*) FILTER (WHERE was_delayed = 1 AND was_delivered = 1 AND breached_after_recovery = 0) 
        AS fully_recovered
FROM recovery_check;
```

**Key Points:**
- Use `FILTER (WHERE ...)` for conditional counts (PostgreSQL)
- Or `SUM(CASE WHEN ... THEN 1 ELSE 0 END)` for other DBs
- Build conditions incrementally

---

### Q14: Funnel analysis (Amazon-style)

> Shipment lifecycle funnel: CREATED → PICKED → SHIPPED → DELIVERED
> Calculate **drop-off rate at each stage**.

```sql
WITH stage_reached AS (
    SELECT 
        shipment_id,
        MAX(CASE WHEN status = 'CREATED' THEN 1 ELSE 0 END) AS reached_created,
        MAX(CASE WHEN status = 'PICKED' THEN 1 ELSE 0 END) AS reached_picked,
        MAX(CASE WHEN status = 'SHIPPED' THEN 1 ELSE 0 END) AS reached_shipped,
        MAX(CASE WHEN status = 'DELIVERED' THEN 1 ELSE 0 END) AS reached_delivered
    FROM shipment_events
    GROUP BY shipment_id
),
funnel AS (
    SELECT 
        SUM(reached_created) AS created,
        SUM(reached_picked) AS picked,
        SUM(reached_shipped) AS shipped,
        SUM(reached_delivered) AS delivered
    FROM stage_reached
)
SELECT 
    'CREATED' AS stage, created AS count, NULL AS dropoff_rate
FROM funnel
UNION ALL
SELECT 
    'PICKED', picked, 
    ROUND(100.0 * (created - picked) / NULLIF(created, 0), 2)
FROM funnel
UNION ALL
SELECT 
    'SHIPPED', shipped, 
    ROUND(100.0 * (picked - shipped) / NULLIF(picked, 0), 2)
FROM funnel
UNION ALL
SELECT 
    'DELIVERED', delivered, 
    ROUND(100.0 * (shipped - delivered) / NULLIF(shipped, 0), 2)
FROM funnel;
```

**Key Points:**
- First aggregate per shipment (did it reach each stage?)
- Then aggregate across all shipments
- Drop-off = (prev_stage - current_stage) / prev_stage

---

### Q15: Mutually exclusive metrics (No overlaps)

> Categorize shipments into:
> - On-time
> - Late but recovered
> - Late and failed
> Ensure **no overlaps**.

```sql
WITH shipment_summary AS (
    SELECT 
        s.shipment_id,
        s.promised_delivery_time,
        MAX(se.event_time) FILTER (WHERE se.status = 'DELIVERED') AS actual_delivery,
        MAX(CASE WHEN se.status = 'FAILED' THEN 1 ELSE 0 END) AS has_failure,
        MIN(se.event_time) FILTER (WHERE se.delay_minutes > 0) AS first_delay
    FROM shipments s
    LEFT JOIN shipment_events se ON s.shipment_id = se.shipment_id
    GROUP BY s.shipment_id, s.promised_delivery_time
)
SELECT 
    shipment_id,
    CASE 
        -- Mutually exclusive, evaluated in order
        WHEN actual_delivery IS NULL OR has_failure = 1 THEN 'LATE_AND_FAILED'
        WHEN actual_delivery <= promised_delivery_time AND first_delay IS NULL THEN 'ON_TIME'
        WHEN actual_delivery <= promised_delivery_time AND first_delay IS NOT NULL THEN 'LATE_BUT_RECOVERED'
        ELSE 'LATE_AND_FAILED'
    END AS category
FROM shipment_summary;

-- Verify no overlaps
SELECT 
    category,
    COUNT(*) AS count,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () AS pct
FROM (/* above query */) categorized
GROUP BY category;
```

**Key Points:**
- Use `CASE WHEN ... THEN ... END` with explicit ordering
- First match wins = no overlaps
- Always verify with COUNT per category

---

## 5️⃣ Hierarchical & Recursive SQL

### Q16: Recursive dependency tracking

> Track shipment transfers across hubs recursively and calculate total hops.

```sql
WITH RECURSIVE transfer_chain AS (
    -- Base case: starting hub
    SELECT 
        shipment_id,
        source_hub,
        destination_hub,
        transfer_time,
        1 AS hop_number,
        ARRAY[source_hub] AS path
    FROM hub_transfers
    WHERE source_hub = 'ORIGIN_HUB'
    
    UNION ALL
    
    -- Recursive case: follow the chain
    SELECT 
        ht.shipment_id,
        ht.source_hub,
        ht.destination_hub,
        ht.transfer_time,
        tc.hop_number + 1,
        tc.path || ht.source_hub
    FROM hub_transfers ht
    JOIN transfer_chain tc 
        ON ht.shipment_id = tc.shipment_id 
        AND ht.source_hub = tc.destination_hub
    WHERE NOT ht.source_hub = ANY(tc.path)  -- Prevent cycles
      AND tc.hop_number < 20  -- Safety limit
)
SELECT 
    shipment_id,
    MAX(hop_number) AS total_hops,
    MAX(path) AS full_route
FROM transfer_chain
GROUP BY shipment_id;
```

**Key Points:**
- `WITH RECURSIVE` for traversal
- Track path with ARRAY to prevent cycles
- Set max depth to prevent infinite loops

---

### Q17: Graph-style traversal (Downstream impact)

> Find all downstream hubs affected if one hub fails.

```sql
WITH RECURSIVE downstream AS (
    -- Base: direct connections from failed hub
    SELECT 
        destination_hub AS affected_hub,
        1 AS distance
    FROM hub_connections
    WHERE source_hub = 'FAILED_HUB'
    
    UNION
    
    -- Recursive: connections from affected hubs
    SELECT 
        hc.destination_hub,
        d.distance + 1
    FROM hub_connections hc
    JOIN downstream d ON hc.source_hub = d.affected_hub
    WHERE d.distance < 10  -- Max distance
)
SELECT DISTINCT 
    affected_hub,
    MIN(distance) AS hops_from_failure
FROM downstream
GROUP BY affected_hub
ORDER BY hops_from_failure;
```

**Key Points:**
- Model hub network as graph (source → destination)
- Recursive CTE traverses all downstream connections
- `DISTINCT` or `GROUP BY` to handle multiple paths

---

## 6️⃣ Subqueries & Correlated Logic

### Q18: Correlated subquery (Compare to group average)

> Find shipments whose delivery time is **greater than the average of its city on that day**.

```sql
-- Method 1: Correlated subquery
SELECT s1.*
FROM shipments s1
WHERE s1.delivery_time_hours > (
    SELECT AVG(s2.delivery_time_hours)
    FROM shipments s2
    WHERE s2.city = s1.city
      AND DATE(s2.delivery_date) = DATE(s1.delivery_date)
);

-- Method 2: Window function (often more efficient)
SELECT *
FROM (
    SELECT 
        *,
        AVG(delivery_time_hours) OVER (
            PARTITION BY city, DATE(delivery_date)
        ) AS city_day_avg
    FROM shipments
) with_avg
WHERE delivery_time_hours > city_day_avg;
```

**Key Points:**
- Correlated subquery: runs once per row (can be slow)
- Window function: single pass (usually faster)
- Both give same result; choose based on data size

---

### Q19: Anti-join logic (Never had status)

> Find shipments that **never entered a FAILED state**, even temporarily.

```sql
-- Method 1: NOT EXISTS (most readable)
SELECT s.shipment_id
FROM shipments s
WHERE NOT EXISTS (
    SELECT 1
    FROM shipment_events se
    WHERE se.shipment_id = s.shipment_id
      AND se.status = 'FAILED'
);

-- Method 2: LEFT JOIN + NULL check
SELECT s.shipment_id
FROM shipments s
LEFT JOIN shipment_events se 
    ON s.shipment_id = se.shipment_id 
    AND se.status = 'FAILED'
WHERE se.shipment_id IS NULL;

-- Method 3: NOT IN (careful with NULLs!)
SELECT shipment_id
FROM shipments
WHERE shipment_id NOT IN (
    SELECT shipment_id 
    FROM shipment_events 
    WHERE status = 'FAILED'
      AND shipment_id IS NOT NULL  -- Critical!
);
```

**Key Points:**
- `NOT EXISTS` is safest (handles NULLs correctly)
- `NOT IN` with NULLs returns empty result (trap!)
- LEFT JOIN + NULL check is explicit

---

### Q20: EXISTS vs JOIN semantics

> Write a query that behaves differently with `EXISTS` than with `JOIN` — explain why.

```sql
-- Setup: shipment_events has MULTIPLE rows per shipment

-- EXISTS: Returns each shipment ONCE
SELECT s.shipment_id, s.customer_id
FROM shipments s
WHERE EXISTS (
    SELECT 1 FROM shipment_events se
    WHERE se.shipment_id = s.shipment_id
);
-- Result: One row per shipment that has events

-- JOIN: Returns shipment MULTIPLE TIMES (once per event)
SELECT s.shipment_id, s.customer_id
FROM shipments s
JOIN shipment_events se ON s.shipment_id = se.shipment_id;
-- Result: One row per (shipment, event) pair

-- COUNT difference:
SELECT COUNT(*) FROM (EXISTS query);  -- = number of shipments
SELECT COUNT(*) FROM (JOIN query);    -- = number of events (often much larger)
```

**Key Points:**
- `EXISTS` = boolean check (at least one match)
- `JOIN` = returns all matching rows (can multiply)
- For "does X have at least one Y", use EXISTS
- For "give me all Y for each X", use JOIN

---

## 7️⃣ Data Quality & Anomaly Detection

### Q21: Outlier detection (vs median)

> Identify delivery times that are **3x higher than the city median**.

```sql
WITH city_stats AS (
    SELECT 
        city,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY delivery_time_hours) AS median_time
    FROM shipments
    GROUP BY city
)
SELECT s.*
FROM shipments s
JOIN city_stats cs ON s.city = cs.city
WHERE s.delivery_time_hours > cs.median_time * 3;
```

**Key Points:**
- `PERCENTILE_CONT(0.5)` = median
- Median is robust to outliers (vs mean)
- 3x threshold is domain-dependent

---

### Q22: Sudden spike detection

> Detect days where shipment volume increased by > 50% day-over-day.

```sql
WITH daily_volume AS (
    SELECT 
        DATE(shipment_date) AS day,
        COUNT(*) AS volume
    FROM shipments
    GROUP BY DATE(shipment_date)
),
with_prev AS (
    SELECT 
        day,
        volume,
        LAG(volume) OVER (ORDER BY day) AS prev_volume
    FROM daily_volume
)
SELECT 
    day,
    volume,
    prev_volume,
    ROUND(100.0 * (volume - prev_volume) / NULLIF(prev_volume, 0), 2) AS pct_change
FROM with_prev
WHERE volume > prev_volume * 1.5;  -- > 50% increase
```

**Key Points:**
- `LAG()` for previous day comparison
- Null check for first day (no previous)
- `NULLIF(prev_volume, 0)` prevents division by zero

---

### Q23: Broken pipeline detection

> Find days where shipments exist but **no status updates were recorded**.

```sql
WITH shipment_days AS (
    SELECT DISTINCT DATE(created_at) AS day
    FROM shipments
),
event_days AS (
    SELECT DISTINCT DATE(event_time) AS day
    FROM shipment_events
)
SELECT sd.day AS missing_events_day
FROM shipment_days sd
LEFT JOIN event_days ed ON sd.day = ed.day
WHERE ed.day IS NULL
ORDER BY sd.day;
```

**Alternative: Check per shipment**

```sql
SELECT 
    s.shipment_id,
    s.created_at,
    COUNT(se.event_id) AS event_count
FROM shipments s
LEFT JOIN shipment_events se 
    ON s.shipment_id = se.shipment_id
    AND DATE(se.event_time) = DATE(s.created_at)
GROUP BY s.shipment_id, s.created_at
HAVING COUNT(se.event_id) = 0;
```

**Key Points:**
- LEFT JOIN + NULL check finds missing data
- Compare expected days vs actual days
- Can extend to per-shipment level

---

## 8️⃣ Performance-Aware SQL

### Q24: Rewrite for performance (Subquery → Window)

```sql
-- SLOW: Correlated subquery (runs for each row)
SELECT 
    shipment_id,
    event_time,
    status,
    (SELECT COUNT(*) 
     FROM shipment_events se2 
     WHERE se2.shipment_id = se1.shipment_id 
       AND se2.event_time <= se1.event_time) AS running_count
FROM shipment_events se1;

-- FAST: Window function (single pass)
SELECT 
    shipment_id,
    event_time,
    status,
    COUNT(*) OVER (
        PARTITION BY shipment_id 
        ORDER BY event_time 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_count
FROM shipment_events;
```

**Key Points:**
- Correlated subqueries = O(n²) worst case
- Window functions = O(n log n)
- Always prefer window for running calculations

---

### Q25: Partition-pruning logic

> Write SQL that **guarantees partition pruning** on a date column.

```sql
-- ✓ GOOD: Direct filter on partition column
SELECT * 
FROM shipments
WHERE shipment_date >= '2024-01-01' 
  AND shipment_date < '2024-02-01';

-- ✗ BAD: Function on partition column (prevents pruning)
SELECT * 
FROM shipments
WHERE DATE_TRUNC('month', shipment_date) = '2024-01-01';

-- ✗ BAD: Casting (prevents pruning)
SELECT * 
FROM shipments
WHERE CAST(shipment_date AS DATE) = '2024-01-15';

-- ✓ GOOD: If you need month, filter by range
SELECT * 
FROM shipments
WHERE shipment_date >= '2024-01-01' 
  AND shipment_date < '2024-02-01';
```

**Key Points:**
- Never apply functions to partition column in WHERE
- Use range filters: `>= start AND < end`
- Check EXPLAIN plan for "Partition Pruning"

---

### Q26: Join explosion prevention

> Rewrite a query to avoid cartesian multiplication.

```sql
-- ✗ BAD: Joins cause row explosion
SELECT 
    s.shipment_id,
    COUNT(DISTINCT se.event_id) AS event_count,
    COUNT(DISTINCT st.scan_id) AS scan_count
FROM shipments s
LEFT JOIN shipment_events se ON s.shipment_id = se.shipment_id
LEFT JOIN shipment_scans st ON s.shipment_id = st.shipment_id
GROUP BY s.shipment_id;
-- If shipment has 10 events and 10 scans, intermediate = 100 rows!

-- ✓ GOOD: Pre-aggregate before joining
WITH event_counts AS (
    SELECT shipment_id, COUNT(*) AS event_count
    FROM shipment_events
    GROUP BY shipment_id
),
scan_counts AS (
    SELECT shipment_id, COUNT(*) AS scan_count
    FROM shipment_scans
    GROUP BY shipment_id
)
SELECT 
    s.shipment_id,
    COALESCE(ec.event_count, 0) AS event_count,
    COALESCE(sc.scan_count, 0) AS scan_count
FROM shipments s
LEFT JOIN event_counts ec ON s.shipment_id = ec.shipment_id
LEFT JOIN scan_counts sc ON s.shipment_id = sc.shipment_id;
```

**Key Points:**
- Multi-table joins can create cartesian products
- Pre-aggregate to one row per key before joining
- Use EXPLAIN to check row counts

---

## 9️⃣ Edge-Case & Trap Questions

### Q27: NULL semantics (Status never changed)

> Find shipments where **status never changed**, even if status is NULL.

```sql
-- Trap: This misses NULLs!
SELECT shipment_id
FROM shipment_events
GROUP BY shipment_id
HAVING COUNT(DISTINCT status) = 1;

-- Correct: Handle NULLs explicitly
SELECT shipment_id
FROM shipment_events
GROUP BY shipment_id
HAVING COUNT(DISTINCT status) = 1
   AND COUNT(DISTINCT COALESCE(status, '__NULL__')) = 1;

-- Or use MIN/MAX comparison
SELECT shipment_id
FROM (
    SELECT 
        shipment_id,
        MIN(COALESCE(status, '')) AS min_status,
        MAX(COALESCE(status, '')) AS max_status
    FROM shipment_events
    GROUP BY shipment_id
) sub
WHERE min_status = max_status;
```

**Key Points:**
- `COUNT(DISTINCT col)` ignores NULLs
- `COALESCE(col, sentinel)` to include NULLs in comparison
- NULL = NULL is UNKNOWN, not TRUE

---

### Q28: Boolean trap

> `WHERE status != 'DELIVERED'` — why is this dangerous?

```sql
-- ❌ DANGER: This excludes NULLs!
SELECT * FROM shipments
WHERE status != 'DELIVERED';

-- NULL != 'DELIVERED' → NULL (unknown) → excluded from results

-- ✓ CORRECT: Handle NULLs explicitly
SELECT * FROM shipments
WHERE status != 'DELIVERED' OR status IS NULL;

-- ✓ Alternative: Use IS DISTINCT FROM (PostgreSQL)
SELECT * FROM shipments
WHERE status IS DISTINCT FROM 'DELIVERED';
-- Returns TRUE for: 'PENDING', 'IN_TRANSIT', and NULL
```

**Key Points:**
- `!= NULL` is always UNKNOWN
- UNKNOWN in WHERE = row excluded
- Always consider NULL when using NOT/!=

---

### Q29: COUNT vs COUNT DISTINCT

> When will `COUNT(*) != COUNT(col)`?

```sql
-- COUNT(*) = number of rows
-- COUNT(col) = number of non-NULL values in col

SELECT 
    COUNT(*) AS total_rows,           -- Counts all rows
    COUNT(status) AS non_null_status, -- Excludes NULLs
    COUNT(DISTINCT status) AS unique_status -- Unique non-NULL values
FROM shipment_events;

-- Example result:
-- total_rows: 1000
-- non_null_status: 950 (50 rows have NULL status)
-- unique_status: 5 (CREATED, PICKED, SHIPPED, DELIVERED, FAILED)

-- TRAP: Counting joins
SELECT 
    s.shipment_id,
    COUNT(*) AS total,                    -- = rows in join result
    COUNT(se.event_id) AS with_events,    -- = only if event exists
    COUNT(DISTINCT se.event_id) AS unique_events
FROM shipments s
LEFT JOIN shipment_events se ON s.shipment_id = se.shipment_id
GROUP BY s.shipment_id;
```

**Key Points:**
- `COUNT(*)` includes NULLs; `COUNT(col)` excludes NULLs
- For LEFT JOINs, right side columns are NULL for non-matches
- `COUNT(DISTINCT)` further removes duplicates

---

### Q30: GROUP BY trap

> Query returns fewer rows than expected — why?

```sql
-- PROBLEM: Multiple orders per customer, want customer-level summary
SELECT 
    customer_id,
    order_id,  -- ← This causes multiple rows per customer!
    SUM(amount) AS total
FROM orders
GROUP BY customer_id, order_id;  -- ← Grouped by order too

-- SOLUTION: Only group by what you want
SELECT 
    customer_id,
    COUNT(*) AS order_count,
    SUM(amount) AS total
FROM orders
GROUP BY customer_id;

-- TRAP 2: DISTINCT inside aggregate
SELECT 
    customer_id,
    COUNT(DISTINCT product_id) AS unique_products,  -- Unique products
    SUM(amount) AS total  -- Total across all orders (including duplicates)
FROM orders
GROUP BY customer_id;
```

**Key Points:**
- GROUP BY determines grain (one row per ...)
- Adding columns to GROUP BY increases rows
- Check grain before writing aggregations

---

## 🔟 Combined Monster Questions

### Q31: End-to-end analytics question

> From raw shipment events: Deduplicate, identify latest valid status, calculate delivery duration, flag SLA breach, aggregate daily metrics. Single query or CTE chain.

```sql
WITH 
-- Step 1: Deduplicate (keep earliest per shipment/status within 5 min)
ordered_events AS (
    SELECT 
        *,
        LAG(event_time) OVER (PARTITION BY shipment_id, status ORDER BY event_time) AS prev_time
    FROM raw_shipment_events
),
deduped AS (
    SELECT *
    FROM ordered_events
    WHERE prev_time IS NULL 
       OR event_time - prev_time > INTERVAL '5 minutes'
),

-- Step 2: Latest valid status per shipment
latest_valid AS (
    SELECT 
        shipment_id,
        status,
        event_time,
        ROW_NUMBER() OVER (
            PARTITION BY shipment_id 
            ORDER BY event_time DESC
        ) AS rn
    FROM deduped
    WHERE is_valid = 1
),
current_status AS (
    SELECT shipment_id, status, event_time AS last_update
    FROM latest_valid
    WHERE rn = 1
),

-- Step 3: Delivery duration
durations AS (
    SELECT 
        d.shipment_id,
        MIN(CASE WHEN d.status = 'CREATED' THEN d.event_time END) AS created_time,
        MAX(CASE WHEN d.status = 'DELIVERED' THEN d.event_time END) AS delivered_time
    FROM deduped d
    GROUP BY d.shipment_id
),
with_duration AS (
    SELECT 
        d.*,
        EXTRACT(EPOCH FROM delivered_time - created_time) / 3600 AS duration_hours
    FROM durations d
),

-- Step 4: SLA breach flag
sla_check AS (
    SELECT 
        wd.shipment_id,
        wd.created_time,
        wd.delivered_time,
        wd.duration_hours,
        s.promised_delivery_time,
        CASE 
            WHEN wd.delivered_time > s.promised_delivery_time THEN 1 
            ELSE 0 
        END AS sla_breached
    FROM with_duration wd
    JOIN shipments s ON wd.shipment_id = s.shipment_id
),

-- Step 5: Daily metrics
daily_metrics AS (
    SELECT 
        DATE(created_time) AS day,
        COUNT(*) AS total_shipments,
        COUNT(*) FILTER (WHERE delivered_time IS NOT NULL) AS deliveries,
        COUNT(*) FILTER (WHERE sla_breached = 1) AS sla_breaches,
        ROUND(AVG(duration_hours), 2) AS avg_delivery_hours,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duration_hours) AS median_hours
    FROM sla_check
    GROUP BY DATE(created_time)
)

SELECT * FROM daily_metrics ORDER BY day;
```

**Key Points:**
- Break complex logic into named CTEs
- Each CTE = one logical step
- Final SELECT can pull from any CTE
- Test each CTE individually

---

### Q32: Explain + write SQL approach

> Explain the approach first, then write SQL.

**Framework for answering:**

```
1. CLARIFY THE QUESTION
   - What is the output grain? (one row per ...)
   - What are the edge cases? (NULLs, duplicates, late data)
   - What is the expected volume?

2. IDENTIFY THE PATTERN
   - Window function (per-group ranking, running calc)
   - Aggregation (summary stats)
   - Join type (inner, left, anti)
   - Recursion (hierarchical)

3. OUTLINE APPROACH
   "I'll use a CTE chain:
   1. First, dedupe raw data by [key]
   2. Then, calculate [metric] using [window/agg]
   3. Finally, join with [table] to get [output]"

4. WRITE SQL (with comments)

5. VALIDATE
   - Check grain (COUNT(*) vs expected)
   - Test edge cases (NULL, empty, duplicates)
   - Review performance (EXPLAIN)
```

---

## 🧠 Mental Models That Win Amazon SQL Rounds

| Question to Ask | Why It Matters |
|-----------------|----------------|
| **"What is the grain?"** | Determines GROUP BY |
| **"What is the latest valid record?"** | Window + filtering |
| **"What happens with NULLs?"** | Prevents subtle bugs |
| **"What if data arrives late?"** | Use event_time, not ingestion |
| **"Does this double count?"** | COUNT DISTINCT, pre-agg before join |

---

## 📝 Interview Tips

1. **Talk through your approach** before writing
2. **Use CTEs liberally** — readability > cleverness
3. **Handle NULLs explicitly** — don't assume clean data
4. **Ask about volume** — changes optimization strategy
5. **Test edge cases** — empty results, all NULLs, one row
