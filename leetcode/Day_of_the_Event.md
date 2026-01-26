# Day of the Event SQL Solution

## Problem Description
**Title:** Day of the Event
**Goal:** For years 2017-2020, find the day(s) of the week with the maximum number of events for each month.
**Output:** A pivot table with `month` as rows and years (2017, 2018, 2019, 2020) as columns.
**Tie-breaking:** Sort days alphabetically and separate by comma.

## Solution (MySQL)

This problem involves:
1.  **Extracting Date Parts:** Getting Year, Month, and Day Name.
2.  **Aggregation:** Counting events per day.
3.  **Ranking:** Finding the day with the max events for each month-year.
4.  **String Aggregation:** Handling ties by combining day names.
5.  **Pivoting:** Transforming rows (Years) into columns.

```sql
WITH DayCounts AS (
    -- Step 1: Count events for each day of the week per month-year
    SELECT 
        YEAR(event_date) AS yr,
        MONTH(event_date) AS mth,
        DAYNAME(event_date) AS day_name,
        COUNT(*) AS num_events
    FROM events
    WHERE YEAR(event_date) BETWEEN 2017 AND 2020
    GROUP BY YEAR(event_date), MONTH(event_date), DAYNAME(event_date)
),
RankedDays AS (
    -- Step 2: Rank the days based on event counts desc
    SELECT 
        yr,
        mth,
        day_name,
        RANK() OVER (
            PARTITION BY yr, mth 
            ORDER BY num_events DESC
        ) as rnk
    FROM DayCounts
),
TopDays AS (
    -- Step 3: Keep only the top days (Rank 1) and aggregate ties
    SELECT 
        yr,
        mth,
        GROUP_CONCAT(day_name ORDER BY day_name SEPARATOR ',') as top_days
    FROM RankedDays
    WHERE rnk = 1
    GROUP BY yr, mth
)
-- Step 4: Pivot the years into columns
SELECT 
    mth AS month,
    MAX(CASE WHEN yr = 2017 THEN top_days ELSE NULL END) AS "2017",
    MAX(CASE WHEN yr = 2018 THEN top_days ELSE NULL END) AS "2018",
    MAX(CASE WHEN yr = 2019 THEN top_days ELSE NULL END) AS "2019",
    MAX(CASE WHEN yr = 2020 THEN top_days ELSE NULL END) AS "2020"
FROM TopDays
GROUP BY mth
ORDER BY mth;
```

## Solution (PostgreSQL)
Similar logic, but using `TO_CHAR` and `STRING_AGG`.

```sql
WITH DayCounts AS (
    SELECT 
        EXTRACT(YEAR FROM event_date) AS yr,
        EXTRACT(MONTH FROM event_date) AS mth,
        TRIM(TO_CHAR(event_date, 'Day')) AS day_name, -- TRIM because Postgres adds padding
        COUNT(*) AS num_events
    FROM events
    WHERE EXTRACT(YEAR FROM event_date) BETWEEN 2017 AND 2020
    GROUP BY 1, 2, 3
),
RankedDays AS (
    SELECT 
        yr,
        mth,
        day_name,
        RANK() OVER (PARTITION BY yr, mth ORDER BY num_events DESC) as rnk
    FROM DayCounts
),
TopDays AS (
    SELECT 
        yr,
        mth,
        STRING_AGG(day_name, ',' ORDER BY day_name) as top_days
    FROM RankedDays
    WHERE rnk = 1
    GROUP BY yr, mth
)
SELECT 
    mth AS month,
    MAX(CASE WHEN yr = 2017 THEN top_days END) AS "2017",
    MAX(CASE WHEN yr = 2018 THEN top_days END) AS "2018",
    MAX(CASE WHEN yr = 2019 THEN top_days END) AS "2019",
    MAX(CASE WHEN yr = 2020 THEN top_days END) AS "2020"
FROM TopDays
GROUP BY mth
ORDER BY mth;
```
