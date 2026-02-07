# SQL Interview Questions & Answers (Question Bank 1)

> **Amazon Data Engineer Style** - Logistics/Transportation Domain Focus

---

<a id="index"></a>
## 📑 Table of Contents

| Section | Topics |
|---------|--------|
| [1️⃣ Basics & Aggregations](#1️⃣-basics--aggregations) | COUNT, GROUP BY, HAVING |
| &nbsp;&nbsp;&nbsp;└ [Q1: Shipments per day](#q1-find-total-shipments-per-day) | DATE, COUNT |
| &nbsp;&nbsp;&nbsp;└ [Q2: Distinct per region](#q2-count-distinct-shipment-ids-per-region) | COUNT DISTINCT |
| &nbsp;&nbsp;&nbsp;└ [Q3: HAVING filter](#q3-find-regions-with-more-than-10000-shipments-in-a-month) | HAVING, DATE_TRUNC |
| &nbsp;&nbsp;&nbsp;└ [Q4: Average delivery time](#q4-calculate-average-delivery-time-per-carrier) | AVG, DATEDIFF |
| &nbsp;&nbsp;&nbsp;└ [Q5: Min/Max/Avg per route](#q5-find-max-min-avg-transit-time-per-route) | Aggregates, percentile |
| [2️⃣ Joins](#2️⃣-joins) | LEFT, INNER, Anti-join |
| &nbsp;&nbsp;&nbsp;└ [Q6: Never delivered](#q6-get-shipments-that-never-reached-delivered-status) | NOT EXISTS |
| &nbsp;&nbsp;&nbsp;└ [Q7: Missing carrier](#q7-find-shipments-with-missing-carrier-information) | LEFT JOIN + NULL |
| &nbsp;&nbsp;&nbsp;└ [Q8: Latest status](#q8-join-shipment-and-event-tables-to-get-latest-status) | ROW_NUMBER |
| &nbsp;&nbsp;&nbsp;└ [Q9: Inconsistent mapping](#q9-identify-shipments-with-inconsistent-region-mapping) | Data quality |
| &nbsp;&nbsp;&nbsp;└ [Q10: LEFT vs INNER](#q10-left-vs-inner-join--when-will-counts-differ) | When to use |
| [3️⃣ Window Functions](#3️⃣-window-functions) | ROW_NUMBER, RANK, LAG/LEAD |
| &nbsp;&nbsp;&nbsp;└ [Q11: Latest status](#q11-latest-status-per-shipment-using-row_number) | ROW_NUMBER |
| &nbsp;&nbsp;&nbsp;└ [Q12: Top 5 cities](#q12-rank-top-5-delay-prone-cities-per-month) | RANK |
| &nbsp;&nbsp;&nbsp;└ [Q13: Running total](#q13-calculate-running-total-of-shipments-per-day) | SUM OVER |
| &nbsp;&nbsp;&nbsp;└ [Q14: LAG/LEAD](#q14-find-previous-and-next-status-using-laglead) | LAG, LEAD |
| &nbsp;&nbsp;&nbsp;└ [Q15: Consecutive updates](#q15-detect-repeated-status-updates-consecutively) | Status = prev |
| [4️⃣ Deduplication & Data Quality](#4️⃣-deduplication--data-quality) | Remove dups, DQ checks |
| &nbsp;&nbsp;&nbsp;└ [Q16: Remove duplicates](#q16-remove-duplicate-shipment-events) | DELETE with ROW_NUMBER |
| &nbsp;&nbsp;&nbsp;└ [Q17: Keep most recent](#q17-keep-the-most-recent-record-per-shipment) | Dedup pattern |
| &nbsp;&nbsp;&nbsp;└ [Q18: Duplicate tracking IDs](#q18-identify-shipments-with-duplicate-tracking-ids) | HAVING COUNT > 1 |
| &nbsp;&nbsp;&nbsp;└ [Q19: Late events](#q19-count-late-arriving-events) | Late data handling |
| &nbsp;&nbsp;&nbsp;└ [Q20: Missing transitions](#q20-detect-missing-status-transitions) | ARRAY_AGG |
| [5️⃣ Time-Based Analytics](#5️⃣-time-based-analytics) | SLA, Rolling, Sessionize |
| &nbsp;&nbsp;&nbsp;└ [Q21: SLA compliance](#q21-shipments-delivered-within-sla) | FILTER |
| &nbsp;&nbsp;&nbsp;└ [Q22: Rolling 7-day avg](#q22-calculate-7-day-rolling-average-delivery-time) | ROWS BETWEEN |
| &nbsp;&nbsp;&nbsp;└ [Q23: Sessionize](#q23-sessionize-shipment-events-by-inactivity-gap) | Gap detection |
| &nbsp;&nbsp;&nbsp;└ [Q24: Stuck > 24h](#q24-detect-shipments-stuck-in-same-status--24-hrs) | Duration calc |
| &nbsp;&nbsp;&nbsp;└ [Q25: Week-over-week](#q25-compare-week-over-week-shipment-volume) | WoW change |
| [6️⃣ Advanced SQL (Part 2)](#6️⃣-advanced-sql-part-2-questions) | Redshift, Gaps & Islands |
| [Question Bank 3: Advanced & Hard](#question-bank-3-advanced--hard-sql-problems) | Multi-stage, Recursive |
| [1️⃣ Multi-Stage Window](#1️⃣-multi-stage-window-function-problems) | Complex patterns |
| [2️⃣ Multi-Join Challenges](#2️⃣-multi-join-challenges) | Self joins, correlated |
| [3️⃣ Gaps & Islands](#3️⃣-gaps-and-islands-patterns) | Sequence detection |
| [4️⃣ Aggregation Edge Cases](#4️⃣-aggregation-edge-cases) | NULLIF, zeros |
| [5️⃣ Performance Optimization](#5️⃣-performance-optimization-patterns) | Indexes, CTEs |

---

<a id="1️⃣-basics--aggregations"></a>
## 1️⃣ Basics & Aggregations [↩️](#index)

<a id="q1-find-total-shipments-per-day"></a>
### Q1: Find total shipments per day [↩️](#index)

```sql
SELECT DATE(shipment_date) AS ship_date, COUNT(*) AS total_shipments
FROM shipments
GROUP BY DATE(shipment_date)
ORDER BY ship_date;
```

---

<a id="q2-count-distinct-shipment-ids-per-region"></a>
### Q2: Count distinct shipment IDs per region [↩️](#index)

```sql
SELECT region, COUNT(DISTINCT shipment_id) AS unique_shipments
FROM shipments
GROUP BY region;
```

---

<a id="q3-find-regions-with-more-than-10000-shipments-in-a-month"></a>
### Q3: Find regions with more than 10,000 shipments in a month [↩️](#index)

```sql
SELECT region, DATE_TRUNC('month', shipment_date) AS month, COUNT(*) AS shipment_count
FROM shipments
GROUP BY region, DATE_TRUNC('month', shipment_date)
HAVING COUNT(*) > 10000;
```

---

<a id="q4-calculate-average-delivery-time-per-carrier"></a>
### Q4: Calculate average delivery time per carrier [↩️](#index)

```sql
SELECT carrier_name, AVG(DATEDIFF('hour', pickup_time, delivery_time)) AS avg_hours
FROM shipments
WHERE delivery_time IS NOT NULL
GROUP BY carrier_name;
```

---

<a id="q5-find-max-min-avg-transit-time-per-route"></a>
### Q5: Find max, min, avg transit time per route [↩️](#index)

```sql
SELECT origin, destination,
    MIN(transit_hours), MAX(transit_hours), AVG(transit_hours),
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY transit_hours) AS median
FROM shipments
GROUP BY origin, destination;
```

---

<a id="2️⃣-joins"></a>
## 2️⃣ Joins [↩️](#index)

<a id="q6-get-shipments-that-never-reached-delivered-status"></a>
### Q6: Get shipments that never reached "DELIVERED" status [↩️](#index)

```sql
-- NOT EXISTS (preferred)
SELECT s.* FROM shipments s
WHERE NOT EXISTS (
    SELECT 1 FROM shipment_events e 
    WHERE e.shipment_id = s.shipment_id AND e.status = 'DELIVERED'
);

-- LEFT JOIN + NULL check
SELECT s.* FROM shipments s
LEFT JOIN shipment_events e ON s.shipment_id = e.shipment_id AND e.status = 'DELIVERED'
WHERE e.shipment_id IS NULL;
```

---

<a id="q7-find-shipments-with-missing-carrier-information"></a>
### Q7: Find shipments with missing carrier information [↩️](#index)

```sql
SELECT s.* FROM shipments s
LEFT JOIN carriers c ON s.carrier_id = c.carrier_id
WHERE c.carrier_id IS NULL AND s.carrier_id IS NOT NULL;
```

---

<a id="q8-join-shipment-and-event-tables-to-get-latest-status"></a>
### Q8: Join shipment and event tables to get latest status [↩️](#index)

```sql
WITH ranked AS (
    SELECT shipment_id, status, event_time,
        ROW_NUMBER() OVER (PARTITION BY shipment_id ORDER BY event_time DESC) AS rn
    FROM shipment_events
)
SELECT s.*, r.status AS current_status
FROM shipments s
JOIN ranked r ON s.shipment_id = r.shipment_id AND r.rn = 1;
```

---

<a id="q9-identify-shipments-with-inconsistent-region-mapping"></a>
### Q9: Identify shipments with inconsistent region mapping [↩️](#index)

```sql
SELECT s.shipment_id, s.origin_region, l.region AS location_region
FROM shipments s
JOIN locations l ON s.origin_location_id = l.location_id
WHERE s.origin_region != l.region;
```

---

<a id="q10-left-vs-inner-join--when-will-counts-differ"></a>
### Q10: LEFT vs INNER JOIN — when will counts differ? [↩️](#index)

| Scenario | LEFT | INNER |
|----------|------|-------|
| All shipments have carriers | Same | Same |
| Some shipments missing carrier | All rows | Only matched |

---

<a id="3️⃣-window-functions"></a>
## 3️⃣ Window Functions [↩️](#index)

<a id="q11-latest-status-per-shipment-using-row_number"></a>
### Q11: Latest status per shipment using ROW_NUMBER [↩️](#index)

```sql
SELECT shipment_id, status, event_time
FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY shipment_id ORDER BY event_time DESC) AS rn
    FROM shipment_events
) ranked
WHERE rn = 1;
```

---

<a id="q12-rank-top-5-delay-prone-cities-per-month"></a>
### Q12: Rank top 5 delay-prone cities per month [↩️](#index)

```sql
WITH city_delays AS (
    SELECT DATE_TRUNC('month', delivery_date) AS month, destination_city,
        COUNT(*) FILTER (WHERE is_delayed) AS delay_count
    FROM shipments GROUP BY 1, 2
),
ranked AS (
    SELECT *, RANK() OVER (PARTITION BY month ORDER BY delay_count DESC) AS rank
    FROM city_delays
)
SELECT * FROM ranked WHERE rank <= 5;
```

---

<a id="q13-calculate-running-total-of-shipments-per-day"></a>
### Q13: Calculate running total of shipments per day [↩️](#index)

```sql
SELECT ship_date, daily_count,
    SUM(daily_count) OVER (ORDER BY ship_date) AS running_total,
    SUM(daily_count) OVER (ORDER BY ship_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_7day
FROM daily_shipments;
```

---

<a id="q14-find-previous-and-next-status-using-laglead"></a>
### Q14: Find previous and next status using LAG/LEAD [↩️](#index)

```sql
SELECT shipment_id, event_time, status,
    LAG(status) OVER (PARTITION BY shipment_id ORDER BY event_time) AS prev_status,
    LEAD(status) OVER (PARTITION BY shipment_id ORDER BY event_time) AS next_status
FROM shipment_events;
```

---

<a id="q15-detect-repeated-status-updates-consecutively"></a>
### Q15: Detect repeated status updates consecutively [↩️](#index)

```sql
WITH with_prev AS (
    SELECT *, LAG(status) OVER (PARTITION BY shipment_id ORDER BY event_time) AS prev_status
    FROM shipment_events
)
SELECT * FROM with_prev WHERE status = prev_status;
```

---

<a id="4️⃣-deduplication--data-quality"></a>
## 4️⃣ Deduplication & Data Quality [↩️](#index)

<a id="q16-remove-duplicate-shipment-events"></a>
### Q16: Remove duplicate shipment events [↩️](#index)

```sql
WITH duplicates AS (
    SELECT event_id, ROW_NUMBER() OVER (PARTITION BY shipment_id, status, event_time ORDER BY event_id) AS rn
    FROM shipment_events
)
DELETE FROM shipment_events WHERE event_id IN (SELECT event_id FROM duplicates WHERE rn > 1);
```

---

<a id="q17-keep-the-most-recent-record-per-shipment"></a>
### Q17: Keep the most recent record per shipment [↩️](#index)

```sql
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY shipment_id ORDER BY updated_at DESC) AS rn
    FROM shipments
) WHERE rn = 1;
```

---

<a id="q18-identify-shipments-with-duplicate-tracking-ids"></a>
### Q18: Identify shipments with duplicate tracking IDs [↩️](#index)

```sql
SELECT tracking_id, COUNT(*), ARRAY_AGG(shipment_id) AS shipment_ids
FROM shipments
GROUP BY tracking_id
HAVING COUNT(*) > 1;
```

---

<a id="q19-count-late-arriving-events"></a>
### Q19: Count late-arriving events [↩️](#index)

```sql
SELECT DATE(event_time) AS event_date, COUNT(*) AS late_events
FROM shipment_events
WHERE event_time < processing_time - INTERVAL '1 hour'
GROUP BY DATE(event_time);
```

---

<a id="q20-detect-missing-status-transitions"></a>
### Q20: Detect missing status transitions [↩️](#index)

```sql
WITH status_sequence AS (
    SELECT shipment_id, ARRAY_AGG(status ORDER BY event_time) AS status_path
    FROM shipment_events GROUP BY shipment_id
)
SELECT * FROM status_sequence
WHERE NOT ('CREATED' = ANY(status_path) AND 'DELIVERED' = ANY(status_path));
```

---

<a id="5️⃣-time-based-analytics"></a>
## 5️⃣ Time-Based Analytics [↩️](#index)

<a id="q21-shipments-delivered-within-sla"></a>
### Q21: Shipments delivered within SLA [↩️](#index)

```sql
SELECT COUNT(*) AS total,
    COUNT(*) FILTER (WHERE delivery_time <= promised_delivery_time) AS on_time,
    ROUND(100.0 * COUNT(*) FILTER (WHERE delivery_time <= promised_delivery_time) / COUNT(*), 2) AS sla_pct
FROM shipments WHERE status = 'DELIVERED';
```

---

<a id="q22-calculate-7-day-rolling-average-delivery-time"></a>
### Q22: Calculate 7-day rolling average delivery time [↩️](#index)

```sql
SELECT delivery_date, avg_hours,
    AVG(avg_hours) OVER (ORDER BY delivery_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_7day
FROM daily_delivery_times;
```

---

<a id="q23-sessionize-shipment-events-by-inactivity-gap"></a>
### Q23: Sessionize shipment events by inactivity gap [↩️](#index)

```sql
WITH with_gap AS (
    SELECT *, event_time - LAG(event_time) OVER (PARTITION BY shipment_id ORDER BY event_time) AS gap
    FROM shipment_events
)
SELECT *, SUM(CASE WHEN gap > INTERVAL '2 hours' OR gap IS NULL THEN 1 ELSE 0 END) 
    OVER (PARTITION BY shipment_id ORDER BY event_time) AS session_id
FROM with_gap;
```

---

<a id="q24-detect-shipments-stuck-in-same-status--24-hrs"></a>
### Q24: Detect shipments stuck in same status > 24 hrs [↩️](#index)

```sql
WITH status_duration AS (
    SELECT shipment_id, status, event_time,
        COALESCE(LEAD(event_time) OVER (PARTITION BY shipment_id ORDER BY event_time), CURRENT_TIMESTAMP) - event_time AS duration
    FROM shipment_events
)
SELECT * FROM status_duration
WHERE duration > INTERVAL '24 hours' AND status NOT IN ('DELIVERED', 'CANCELLED');
```

---

<a id="q25-compare-week-over-week-shipment-volume"></a>
### Q25: Compare week-over-week shipment volume [↩️](#index)

```sql
WITH weekly AS (
    SELECT DATE_TRUNC('week', shipment_date) AS week, COUNT(*) AS cnt
    FROM shipments GROUP BY 1
)
SELECT week, cnt, LAG(cnt) OVER (ORDER BY week) AS prev_week,
    ROUND(100.0 * (cnt - LAG(cnt) OVER (ORDER BY week)) / LAG(cnt) OVER (ORDER BY week), 2) AS wow_pct
FROM weekly;
```

---

<a id="6️⃣-advanced-sql-part-2-questions"></a>
## 6️⃣ Advanced SQL (Part 2 Questions) [↩️](#index)

- Redshift DISTKEY/SORTKEY optimization
- Gaps and Islands: Consecutive driver active days
- Time between OFD and Delivered
- Top 3 delay-prone lanes per week

---

<a id="question-bank-3-advanced--hard-sql-problems"></a>
# Question Bank 3: Advanced & Hard SQL Problems [↩️](#index)

> Logic-Heavy, Multi-Step, Edge-Case–Loaded Queries

---

<a id="1️⃣-multi-stage-window-function-problems"></a>
## 1️⃣ Multi-Stage Window Function Problems [↩️](#index)

- Q1: Latest valid record with conditions
- Q2: Top-N per group with ties

---

<a id="2️⃣-multi-join-challenges"></a>
## 2️⃣ Multi-Join Challenges [↩️](#index)

- Self joins for comparisons
- Correlated subqueries

---

<a id="3️⃣-gaps-and-islands-patterns"></a>
## 3️⃣ Gaps and Islands Patterns [↩️](#index)

```sql
-- Consecutive days detection
WITH numbered AS (
    SELECT driver_id, active_date,
        active_date - ROW_NUMBER() OVER (PARTITION BY driver_id ORDER BY active_date)::INT AS grp
    FROM driver_activity
)
SELECT driver_id, MIN(active_date) AS start_date, MAX(active_date) AS end_date, COUNT(*) AS consecutive_days
FROM numbered GROUP BY driver_id, grp;
```

---

<a id="4️⃣-aggregation-edge-cases"></a>
## 4️⃣ Aggregation Edge Cases [↩️](#index)

- NULLIF to avoid division by zero
- COALESCE for default values

---

<a id="5️⃣-performance-optimization-patterns"></a>
## 5️⃣ Performance Optimization Patterns [↩️](#index)

- Index strategies
- CTE vs subquery performance
- Partition pruning
