# Time Series Interview Questions (SQL & PySpark)

This guide covers 10 essential time-series patterns. Each section includes a scenario, a sample input dataset, and solutions in both SQL and PySpark.

---

## 1. Active vs Inactive Users
**Scenario:** Identify users who have logged in within the last 7 days as "Active"; otherwise, "Inactive".
**Input Data:** `user_logins`
| user_id | login_date |
|---|---|
| 101 | 2024-01-20 |
| 102 | 2024-01-10 |
| 103 | 2024-01-22 |
*(Current Date: 2024-01-22)*

**SQL Solution:**
```sql
SELECT
    user_id,
    MAX(login_date) as last_login,
    CASE
        WHEN DATEDIFF(day, MAX(login_date), '2024-01-22') <= 7 THEN 'Active'
        ELSE 'Inactive'
    END as status
FROM user_logins
GROUP BY user_id;
```

**PySpark Solution:**
```python
from pyspark.sql.functions import col, max, datediff, lit, when

df.groupBy("user_id").agg(max("login_date").alias("last_login")) \
  .withColumn("status", when(datediff(lit("2024-01-22"), col("last_login")) <= 7, "Active").otherwise("Inactive"))
```

**Output:**
| user_id | last_login | status |
|---|---|---|
| 101 | 2024-01-20 | Active |
| 102 | 2024-01-10 | Inactive |
| 103 | 2024-01-22 | Active |

---

## 2. Day-over-Day Growth
**Scenario:** Calculate the percentage growth in daily revenue compared to the previous day.
**Input Data:** `daily_revenue`
| date | revenue |
|---|---|
| 2024-01-01 | 100 |
| 2024-01-02 | 120 |
| 2024-01-03 | 108 |

**SQL Solution:**
```sql
SELECT
    date,
    revenue,
    CASE
        WHEN LAG(revenue) OVER (ORDER BY date) IS NULL THEN 0
        ELSE ROUND(((revenue - LAG(revenue) OVER (ORDER BY date)) / LAG(revenue) OVER (ORDER BY date)) * 100, 2)
    END as growth_pct
FROM daily_revenue;
```

**PySpark Solution:**
```python
from pyspark.sql.window import Window
from pyspark.sql.functions import lag, col, round, when

w = Window.orderBy("date")
df.withColumn("prev_rev", lag("revenue").over(w)) \
  .withColumn("growth_pct", when(col("prev_rev").isNull(), 0)
    .otherwise(round(((col("revenue") - col("prev_rev")) / col("prev_rev")) * 100, 2)))
```

**Output:**
| date | revenue | growth_pct |
|---|---|---|
| 2024-01-01 | 100 | 0.00 |
| 2024-01-02 | 120 | 20.00 |
| 2024-01-03 | 108 | -10.00 |

---

## 3. Rolling Averages
**Scenario:** Calculate the 3-day rolling average of temperatures.
**Input Data:** `weather`
| date | temp |
|---|---|
| 2024-01-01 | 20 |
| 2024-01-02 | 22 |
| 2024-01-03 | 24 |
| 2024-01-04 | 26 |

**SQL Solution:**
```sql
SELECT
    date,
    temp,
    AVG(temp) OVER (
        ORDER BY date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) as rolling_avg_3d
FROM weather;
```

**PySpark Solution:**
```python
from pyspark.sql.window import Window
from pyspark.sql.functions import avg, col

w = Window.orderBy("date").rowsBetween(-2, 0)
df.withColumn("rolling_avg_3d", avg("temp").over(w))
```

**Output:**
| date | temp | rolling_avg_3d |
|---|---|---|
| 2024-01-01 | 20 | 20.0 |
| 2024-01-02 | 22 | 21.0 |
| 2024-01-03 | 24 | 22.0 |
| 2024-01-04 | 26 | 24.0 |

---

## 4. Peak Hour/Day
**Scenario:** Identify the hour of the day with the highest total visits.
**Input Data:** `traffic`
| timestamp | visits |
|---|---|
| 2024-01-01 08:30:00 | 50 |
| 2024-01-01 08:45:00 | 30 |
| 2024-01-01 09:10:00 | 100 |

**SQL Solution:**
```sql
WITH HourlyStats AS (
    SELECT
        DATEPART(hour, timestamp) as hour_of_day,
        SUM(visits) as total_visits
    FROM traffic
    GROUP BY DATEPART(hour, timestamp)
)
SELECT TOP 1 * FROM HourlyStats ORDER BY total_visits DESC;
-- Postgres: EXTRACT(HOUR FROM timestamp) ... LIMIT 1
```

**PySpark Solution:**
```python
from pyspark.sql.functions import hour, sum, desc

df.groupBy(hour("timestamp").alias("hour_of_day")) \
  .agg(sum("visits").alias("total_visits")) \
  .orderBy(desc("total_visits")) \
  .limit(1)
```

**Output:**
| hour_of_day | total_visits |
|---|---|
| 8 | 80 |

---

## 5. Consecutive Days Activity (Gaps & Islands)
**Scenario:** Find users who have logged in for 3 consecutive days.
**Input Data:** `logins`
| user_id | date |
|---|---|
| A | 2024-01-01 |
| A | 2024-01-02 |
| A | 2024-01-03 |
| B | 2024-01-01 |
| B | 2024-01-03 |

**SQL Solution:**
```sql
WITH Grouped AS (
    SELECT
        user_id,
        date,
        -- Magic: Date - RowNumber creates a constant value for consecutive dates
        DATEADD(day, -ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY date), date) as island_id
    FROM logins
)
SELECT user_id, COUNT(*) as streak_days
FROM Grouped
GROUP BY user_id, island_id
HAVING COUNT(*) >= 3;
```

**PySpark Solution:**
```python
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, col, date_sub, count

w = Window.partitionBy("user_id").orderBy("date")
df.withColumn("rn", row_number().over(w)) \
  .withColumn("island_id", date_sub(col("date"), col("rn"))) \
  .groupBy("user_id", "island_id").agg(count("*").alias("streak")) \
  .filter(col("streak") >= 3)
```

**Output:**
| user_id | streak_days |
|---|---|
| A | 3 |

---

## 6. First and Last Event
**Scenario:** Find the first and last `page_url` visited by a user in a session.
**Input Data:** `clicks`
| user_id | time | page_url |
|---|---|---|
| 1 | 10:00 | /home |
| 1 | 10:05 | /cart |
| 1 | 10:10 | /checkout |

**SQL Solution:**
```sql
SELECT
    user_id,
    MIN(time) as start_time,
    MAX(time) as end_time,
    FIRST_VALUE(page_url) OVER (PARTITION BY user_id ORDER BY time) as first_page,
    LAST_VALUE(page_url) OVER (
        PARTITION BY user_id ORDER BY time
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as last_page
FROM clicks
GROUP BY user_id, page_url, time; -- Note: Distinct is cleaner here
-- Cleaner approach:
-- SELECT DISTINCT user_id, first_value(...) ..., last_value(...) ...
```

**PySpark Solution:**
```python
from pyspark.sql.window import Window
from pyspark.sql.functions import first, last, col

w = Window.partitionBy("user_id").orderBy("time")
df.groupBy("user_id").agg(
    first("page_url").alias("first_page"),
    last("page_url").alias("last_page")
)
```

**Output:**
| user_id | first_page | last_page |
|---|---|---|
| 1 | /home | /checkout |

---

## 7. Missing Dates
**Scenario:** You have sales data for specific days, but want to show a report with "0" for days with no sales.
**Input Data:** `sales`
| date | amount |
|---|---|
| 2024-01-01 | 50 |
| 2024-01-03 | 70 |

**SQL Solution:**
```sql
WITH DateSeries AS (
    -- Recursive CTE to generate dates
    SELECT CAST('2024-01-01' AS DATE) as d
    UNION ALL
    SELECT DATEADD(day, 1, d) FROM DateSeries WHERE d < '2024-01-03'
)
SELECT
    ds.d as date,
    COALESCE(s.amount, 0) as amount
FROM DateSeries ds
LEFT JOIN sales s ON ds.d = s.date;
```

**PySpark Solution:**
```python
from pyspark.sql.functions import sequence, to_date, explode, col, lit

# Create a range of dates
date_df = spark.sql("SELECT sequence(to_date('2024-01-01'), to_date('2024-01-03'), interval 1 day) as date_range") \
               .withColumn("date", explode("date_range")).select("date")

result = date_df.join(sales_df, "date", "left").fillna(0)
```

**Output:**
| date | amount |
|---|---|
| 2024-01-01 | 50 |
| 2024-01-02 | 0 |
| 2024-01-03 | 70 |

---

## 8. Sessionization
**Scenario:** Group events into a "Session" if they occur within 30 minutes of the previous event.
**Input Data:** `events`
| user_id | time |
|---|---|
| U1 | 10:00 |
| U1 | 10:20 |
| U1 | 11:00 |

**SQL Solution:**
```sql
WITH Lagged AS (
    SELECT
        user_id,
        time,
        LAG(time) OVER (PARTITION BY user_id ORDER BY time) as prev_time
    FROM events
),
NewSessionFlag AS (
    SELECT
        user_id,
        time,
        -- If time diff > 30 mins, mark as 1 (new session), else 0
        CASE WHEN DATEDIFF(minute, prev_time, time) > 30 THEN 1 ELSE 0 END as is_new_session,
        -- Special case: First event is always new
        CASE WHEN prev_time IS NULL THEN 1 ELSE 0 END as is_first
    FROM Lagged
)
SELECT
    user_id,
    time,
    SUM(is_new_session + is_first) OVER (PARTITION BY user_id ORDER BY time) as session_id
FROM NewSessionFlag;
```

**PySpark Solution:**
```python
from pyspark.sql.window import Window
from pyspark.sql.functions import lag, col, sum, when, unix_timestamp

w = Window.partitionBy("user_id").orderBy("time")
df = df.withColumn("prev_time", lag("time").over(w))

# Calculate is_new_session (using timestamp seconds difference > 1800)
df = df.withColumn("is_new_session",
    when((col("time").cast("long") - col("prev_time").cast("long")) > 1800, 1).otherwise(0)
)

# Rolling sum to create session ID
df.withColumn("session_id", sum("is_new_session").over(w))
```

**Output:**
| user_id | time | session_id |
|---|---|---|
| U1 | 10:00 | 0 |
| U1 | 10:20 | 0 |
| U1 | 11:00 | 1 |

---

## 9. Retention (Day 1 / Day 7)
**Scenario:** Calculate Day 1 Retention (Users who joined on Day 0 and came back on Day 1).
**Input Data:** `activity` (includes join event and plain login)
| user_id | date | event_type |
|---|---|---|
| U1 | 2024-01-01 | signup |
| U1 | 2024-01-02 | login |
| U2 | 2024-01-01 | signup |

**SQL Solution:**
```sql
WITH Cohort AS (
    SELECT user_id, date as join_date
    FROM activity WHERE event_type = 'signup'
)
SELECT
    c.join_date,
    COUNT(DISTINCT c.user_id) as total_users,
    COUNT(DISTINCT a.user_id) as retained_users,
    CAST(COUNT(DISTINCT a.user_id) AS FLOAT) / COUNT(DISTINCT c.user_id) as retention_rate
FROM Cohort c
LEFT JOIN activity a
    ON c.user_id = a.user_id
    AND a.date = DATEADD(day, 1, c.join_date) -- Day 1 check
GROUP BY c.join_date;
```

**PySpark Solution:**
```python
from pyspark.sql.functions import date_add, countDistinct

cohort = df.filter(col("event_type") == "signup").select(col("user_id"), col("date").alias("join_date"))

retained = df.alias("a").join(cohort.alias("c"),
    (col("a.user_id") == col("c.user_id")) &
    (col("a.date") == date_add(col("c.join_date"), 1)), "left")

retained.groupBy("c.join_date").agg(
    countDistinct("c.user_id").alias("cohort_size"),
    countDistinct("a.user_id").alias("retained_count")
)
```

**Output:**
| join_date | total_users | retained_users | retention_rate |
|---|---|---|---|
| 2024-01-01 | 2 | 1 | 0.50 |

---

## 10. Time-based Deduplication
**Scenario:** Keep only the *latest* record for each user based on timestamp.
**Input Data:** `updates`
| user_id | updated_at | status |
|---|---|---|
| A | 10:00 | Pending |
| A | 10:05 | Approved |

**SQL Solution:**
```sql
WITH Ranked AS (
    SELECT
        user_id,
        updated_at,
        status,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY updated_at DESC) as rn
    FROM updates
)
SELECT user_id, updated_at, status
FROM Ranked
WHERE rn = 1;
```

**PySpark Solution:**
```python
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, desc

w = Window.partitionBy("user_id").orderBy(desc("updated_at"))
df.withColumn("rn", row_number().over(w)) \
  .filter(col("rn") == 1) \
  .drop("rn")
```

**Output:**
| user_id | updated_at | status |
|---|---|---|
| A | 10:05 | Approved |
