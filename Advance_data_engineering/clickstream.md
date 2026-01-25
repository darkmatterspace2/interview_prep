# Advanced Data Engineering: Clickstream Analysis

## Classic FAANG Interview Question: Sessionization

### Scenario
You are processing a massive stream of clickstream data for a major e-commerce platform. The data arrives with the following schema:
*   `user_id` (String): Unique identifier for the user.
*   `timestamp` (Timestamp): Time of the click event.
*   `url` (String): The page visited.

**Goal:**
Identify "user sessions". A session is defined as a sequence of activities by the same user where the time gap between any two consecutive events is less than **30 minutes**. If a user is inactive for 30 minutes or more, the next event starts a new session.

**Deliverable:**
Write a SQL query (or PySpark logic) to assign a unique `session_id` to each event row.

---

### Solution: The "New Session Flag" & Cumulative Sum Approach

This is the standard pattern for solving sessionization problems in SQL-based environments (BigQuery, Redshift, Spark SQL).

#### Step 1: Calculate Time Difference
Use `LAG` to look at the previous event's timestamp for the same user.

#### Step 2: Mark Session Boundaries
Create a boolean flag (or 1/0 integer) that is `1` if the gap > 30 mins (or if it's the first event), and `0` otherwise.

#### Step 3: Generate Session ID
Perform a cumulative sum of the flags over the user's history. This running total effectively works as a unique ID for each session.

### SQL Implementation

```sql
WITH PreviousEvent AS (
    SELECT 
        user_id,
        timestamp,
        url,
        LAG(timestamp) OVER (PARTITION BY user_id ORDER BY timestamp) as prev_ts
    FROM clicks
),
NewSessionFlag AS (
    SELECT 
        *,
        CASE 
            WHEN prev_ts IS NULL THEN 1                            -- First event ever for user
            WHEN timestamp - prev_ts > INTERVAL '30' MINUTE THEN 1 -- Inactivity gap exceeded
            ELSE 0 
        END as is_new_session
    FROM PreviousEvent
)
SELECT 
    user_id,
    timestamp,
    url,
    -- Concat user_id with the running total to make it truly unique globally
    CONCAT(user_id, '-', SUM(is_new_session) OVER (PARTITION BY user_id ORDER BY timestamp)) as session_id
FROM NewSessionFlag;
```

### Follow-up Questions (The "FAANG Twist")
1.  **Scaling:** How would you handle this if the data volume is too large for a standard window function shuffle? (Answer key: Salting, or using `mapGroupsWithState` in Spark Streaming for O(1) state management per user).
2.  **Late Data:** What if events arrive out of order? (Answer key: Watermarking in streaming, or re-processing partitions in batch).
