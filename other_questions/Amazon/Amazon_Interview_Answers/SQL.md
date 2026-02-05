# Amazon SQL Interview Questions & Answers

## Part 1: SQL (High Priority)

### Basics & Aggregations

#### 1. Find total shipments per day.
**Question:** Write a query to find the total number of shipments for each day.
**Answer:**
```sql
SELECT 
    DATE(shipment_date) as shipment_day, 
    COUNT(shipment_id) as total_shipments
FROM shipments
GROUP BY 1
ORDER BY 1;
```
*Explanation:* We cast the timestamp to a date (if necessary) and group by that date, counting the unique shipment IDs.

#### 2. Count distinct shipment IDs per region.
**Question:** detailed query to count distinct shipment IDs for each region.
**Answer:**
```sql
SELECT 
    region, 
    COUNT(DISTINCT shipment_id) as distinct_shipments
FROM shipments
GROUP BY region;
```
*Explanation:* Using `COUNT(DISTINCT column)` ensures we don't double-count shipments if they appear multiple times in the table (e.g., multiple status updates).

#### 3. Find regions with more than 10,000 shipments in a month.
**Question:** Filter for regions that had high volume (>10k) in a specific month.
**Answer:**
```sql
SELECT 
    region,
    DATE_TRUNC('month', shipment_date) as month,
    COUNT(shipment_id) as shipment_count
FROM shipments
GROUP BY 1, 2
HAVING COUNT(shipment_id) > 10000;
```
*Explanation:* `HAVING` clause is used to filter aggregated data (groups) after the `GROUP BY` operation.

#### 4. Calculate average delivery time per carrier.
**Question:** Find the average time taken to deliver for each carrier.
**Answer:**
```sql
SELECT 
    carrier_name,
    AVG(delivery_date - ship_date) as avg_delivery_time_days
FROM shipments
WHERE status = 'DELIVERED'
  AND delivery_date IS NOT NULL 
  AND ship_date IS NOT NULL
GROUP BY carrier_name;
```
*Explanation:* subtract timestamps to get intervals. Ensure you filter for completed deliveries to avoid skewing data with nulls or negative values.

#### 5. Find max, min, avg transit time per route.
**Question:** Calculate transit time statistics for each route (Source -> Destination).
**Answer:**
```sql
SELECT 
    source_city,
    destination_city,
    MAX(delivery_date - ship_date) as max_transit,
    MIN(delivery_date - ship_date) as min_transit,
    AVG(delivery_date - ship_date) as avg_transit
FROM shipments
WHERE status = 'DELIVERED'
GROUP BY 1, 2;
```

---

### Joins

#### 6. Get shipments that never reached “DELIVERED” status.
**Question:** Identify shipments that are stuck or lost.
**Answer:**
```sql
SELECT s.shipment_id
FROM shipments s
GROUP BY s.shipment_id
HAVING SUM(CASE WHEN s.status = 'DELIVERED' THEN 1 ELSE 0 END) = 0;
```
*Alternative (if using a distinct status table):*
```sql
SELECT shipment_id 
FROM shipments 
WHERE shipment_id NOT IN (
    SELECT shipment_id FROM shipment_events WHERE status = 'DELIVERED'
);
```

#### 7. Find shipments with missing carrier information.
**Question:** Identify data quality issues where carrier is null.
**Answer:**
```sql
SELECT *
FROM shipments
WHERE carrier_id IS NULL;
```

#### 8. Join shipment and event tables to get latest status.
**Question:** Get the most recent status for every shipment.
**Answer:**
```sql
WITH RankedEvents AS (
    SELECT 
        shipment_id, 
        status, 
        timestamp,
        ROW_NUMBER() OVER(PARTITION BY shipment_id ORDER BY timestamp DESC) as rn
    FROM shipment_events
)
SELECT shipment_id, status, timestamp
FROM RankedEvents
WHERE rn = 1;
```
*Explanation:* This is a classic "top-N-per-group" problem solved efficiently with window functions.

#### 9. Identify shipments with inconsistent region mapping.
**Question:** Shipments where the region in the shipment table doesn't match the region in the destination city table.
**Answer:**
```sql
SELECT s.shipment_id, s.region as ship_region, c.region as city_region
FROM shipments s
JOIN cities c ON s.destination_city_id = c.city_id
WHERE s.region <> c.region;
```

#### 10. LEFT vs INNER JOIN — when will counts differ?
**Answer:**
*   **INNER JOIN**: Returns rows only when there is a match in *both* tables. If a shipment has no carrier, it won't show up.
*   **LEFT JOIN**: Returns *all* rows from the left table, and matched rows from the right. If no match, the right side is NULL.
*   **Counts Differ**: When the left table has records that have no corresponding match in the right table (orphans), `LEFT JOIN` count > `INNER JOIN` count.

---

### Window Functions

#### 11. Latest status per shipment using `ROW_NUMBER`.
*(See Question 8 Answer)* - This is the standard pattern for finding the "latest" state.

#### 12. Rank top 5 delay-prone cities per month.
**Question:** Which cities have the most delayed shipments?
**Answer:**
```sql
WITH CityDelays AS (
    SELECT 
        city_name,
        DATE_TRUNC('month', delivery_date) as month,
        COUNT(*) as delayed_count
    FROM shipments
    WHERE is_delayed = TRUE
    GROUP BY 1, 2
),
RankedCities AS (
    SELECT 
        city_name,
        month,
        delayed_count,
        RANK() OVER(PARTITION BY month ORDER BY delayed_count DESC) as rnk
    FROM CityDelays
)
SELECT * FROM RankedCities WHERE rnk <= 5;
```

#### 13. Calculate running total of shipments per day.
**Question:** Cumulative sum of shipments over time.
**Answer:**
```sql
SELECT 
    shipment_day,
    daily_count,
    SUM(daily_count) OVER (ORDER BY shipment_day) as running_total
FROM daily_shipment_counts; -- Assuming pre-aggregated table or CTE
```

#### 14. Find previous and next status using `LAG/LEAD`.
**Question:** accurate status transitions analysis.
**Answer:**
```sql
SELECT 
    shipment_id,
    status as current_status,
    LAG(status) OVER(PARTITION BY shipment_id ORDER BY timestamp) as prev_status,
    LEAD(status) OVER(PARTITION BY shipment_id ORDER BY timestamp) as next_status
FROM shipment_events;
```

#### 15. Detect repeated status updates consecutively.
**Question:** Find duplicate consecutive events (e.g., "In Transit" -> "In Transit").
**Answer:**
```sql
WITH Lagged AS (
    SELECT 
        *,
        LAG(status) OVER(PARTITION BY shipment_id ORDER BY timestamp) as prev_status
    FROM shipment_events
)
SELECT * 
FROM Lagged 
WHERE status = prev_status;
```

---

### Deduplication & Data Quality

#### 16. Remove duplicate shipment events.
**Question:** How to delete exact duplicates?
**Answer:**
```sql
DELETE FROM shipment_events
WHERE event_id IN (
    SELECT event_id
    FROM (
        SELECT 
            event_id,
            ROW_NUMBER() OVER(PARTITION BY shipment_id, status, timestamp ORDER BY event_id) as rn
        FROM shipment_events
    ) t
    WHERE rn > 1
);
```

#### 17. Keep the most recent record per shipment.
*(Similar to Q8)* - Use `ROW_NUMBER()`, logical filter `rn = 1`, and often write this to a new table or clean up the old one.

#### 18. Identify shipments with duplicate tracking IDs.
**Answer:**
```sql
SELECT tracking_id, COUNT(*)
FROM shipments
GROUP BY tracking_id
HAVING COUNT(*) > 1;
```

#### 19. Count late-arriving events.
**Question:** Events arriving after the shipment is already delivered? Or events arriving late into the system (ingestion lag)?
**Answer (Ingestion Lag):**
```sql
SELECT COUNT(*)
FROM shipment_events
WHERE ingestion_timestamp > event_timestamp + INTERVAL '1 day';
```

#### 20. Detect missing status transitions.
**Question:** e.g., "Out for Delivery" but never "Delivered".
**Answer:**
```sql
SELECT shipment_id
FROM shipment_events
WHERE status = 'OUT_FOR_DELIVERY'
AND shipment_id NOT IN (
    SELECT shipment_id FROM shipment_events WHERE status IN ('DELIVERED', 'ATTEMPTED')
);
```

---

### Time-Based Analytics

#### 21. Shipments delivered within SLA.
**Answer:**
```sql
SELECT 
    SUM(CASE WHEN delivery_date <= promised_date THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as sla_met_percentage
FROM shipments;
```

#### 22. Calculate 7-day rolling average delivery time.
**Answer:**
```sql
SELECT 
    shipment_date,
    avg_delivery_time,
    AVG(avg_delivery_time) OVER(
        ORDER BY shipment_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as rolling_7d_avg
FROM daily_delivery_stats;
```

#### 23. Sessionize shipment events by inactivity gap.
**Question:** Group events into "sessions" if they occur within 30 mins of each other.
**Answer:**
```sql
WITH Step1 AS (
    SELECT 
        *,
        CASE 
            WHEN timestamp - LAG(timestamp) OVER(PARTITION BY shipment_id ORDER BY timestamp) > INTERVAL '30 minutes' 
            THEN 1 ELSE 0 
        END as is_new_session
    FROM event_logs
),
Step2 AS (
    SELECT 
        *,
        SUM(is_new_session) OVER(PARTITION BY shipment_id ORDER BY timestamp) as session_id
    FROM Step1
)
SELECT * FROM Step2;
```

#### 24. Detect shipments stuck in same status > 24 hrs.
**Answer:**
```sql
SELECT shipment_id, status, timestamp
FROM (
    SELECT 
        shipment_id, status, timestamp,
        LEAD(timestamp) OVER(PARTITION BY shipment_id ORDER BY timestamp) as next_event_time
    FROM shipment_events
) t
WHERE next_event_time - timestamp > INTERVAL '24 hours'
OR (next_event_time IS NULL AND NOW() - timestamp > INTERVAL '24 hours');
```

#### 25. Compare week-over-week shipment volume.
**Answer:**
```sql
SELECT 
    DATE_TRUNC('week', shipment_date) as week,
    COUNT(*) as current_vol,
    LAG(COUNT(*)) OVER(ORDER BY DATE_TRUNC('week', shipment_date)) as prev_week_vol,
    (COUNT(*) - LAG(COUNT(*)) OVER(...)) * 100.0 / NULLIF(LAG(COUNT(*)) OVER(...), 0) as growth_pct
FROM shipments
GROUP BY 1;
```

---

## Part 2: SQL & Data Warehousing (Redshift Focus)

#### Scenario 1: Time difference between "Out for Delivery" and "Delivered"
**Question:** Find the time difference between the "Out for Delivery" scan and the "Delivered" scan for every package delivered yesterday.
**Answer:**
```sql
SELECT 
    t1.package_id,
    t2.timestamp - t1.timestamp as delivery_duration
FROM PackageScans t1
JOIN PackageScans t2 ON t1.package_id = t2.package_id
WHERE t1.status = 'OUT_FOR_DELIVERY'
  AND t2.status = 'DELIVERED'
  AND DATE(t2.timestamp) = CURRENT_DATE - 1;
```
*Note:* This assumes only one scan per status per package. If duplicates exist, use aggregations (MIN/MAX) or CTEs to clean first.

#### Scenario 2: Top 3 transportation lanes with highest average delay
**Answer:**
```sql
SELECT 
    source, 
    destination, 
    AVG(delay_minutes) as avg_delay
FROM shipments
GROUP BY 1, 2
ORDER BY avg_delay DESC
LIMIT 3;
```

#### Scenario 3: Redshift Optimization (DISTKEY/SORTKEY)
**Question:** Query on 10TB table is slow. How to debug? Explain DISTKEY/SORTKEY.
**Answer:**
*   **Debug:** Check `STL_ALERT_EVENT_LOG` for large broadcast joins or disk spills. Check `SVL_QUERY_SUMMARY` for execution steps. Run `EXPLAIN` to see the plan.
*   **DISTKEY (Distribution Key):** Determines how data is distributed across nodes.
    *   *Strategy:* Choose a high-cardinality column commonly used in JOINs (e.g., `shipment_id` or `order_id`). This keeps related data on the same node, avoiding network shuffling (co-location).
*   **SORTKEY (Sort Key):** Determines physical order of data on disk.
    *   *Strategy:* Choose columns used in `WHERE` clauses or range filters (e.g., `timestamp`, `date`). This allows Redshift to skip blocks (Zone Maps) that don't contain relevant data.

#### Scenario 4: Redshift Architecture
**Answer:**
*   **Leader Node:** Handles client connections, SQL parsing, and creating execution plans. It coordinates the compute nodes but doesn't store data.
*   **Compute Nodes:** Execute the query fragments in parallel and store the actual data.
*   **Slices:** Each compute node is partitioned into slices. Users execute queries in parallel on these slices.

#### Scenario 5: Gaps and Islands (Consecutive active days)
**Question:** Find consecutive days a truck driver was active.
**Answer:**
```sql
WITH Dates AS (
    SELECT DISTINCT driver_id, activity_date 
    FROM driver_logs
),
Groups AS (
    SELECT 
        driver_id, 
        activity_date,
        activity_date - ROW_NUMBER() OVER(PARTITION BY driver_id ORDER BY activity_date) * INTERVAL '1 day' as grp
    FROM Dates
)
SELECT 
    driver_id, 
    MIN(activity_date) as start_streak, 
    MAX(activity_date) as end_streak, 
    COUNT(*) as streak_days
FROM Groups
GROUP BY driver_id, grp
ORDER BY streak_days DESC;
```
*Explanation:* If dates are consecutive, subtracting the row_number (converted to days) from the date will yield the same constant date ("grp") for that sequence. Grouping by this constant identifies the island.
