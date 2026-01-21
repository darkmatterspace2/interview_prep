# PySpark Streaming & Sessionization Scenarios

Common interview questions for product-based companies (Netflix, Amazon, Airbnb) focusing on user session management and clickstream analysis using PySpark.

## Scenario 1: Sessionization based on Inactivity (Gap Analysis)
**Problem:** Given a stream of click events with `user_id` and `timestamp`, group events into sessions. A new session starts if the user is inactive for more than 30 minutes.

**Technique:**
1.  **Sort** events by user and time.
2.  Calculate **Time Lag** from the previous event.
3.  Flag a **New Session** if `current_ts - prev_ts > 30 mins`.
4.  Generate **Session ID** using a cumulative sum of the flags.

**Code:**
```python
from pyspark.sql.functions import col, lag, sum, when, unix_timestamp
from pyspark.sql.window import Window

# 1. Define Window
user_window = Window.partitionBy("user_id").orderBy("timestamp")

# 2. Calculate time difference in seconds
df = df.withColumn("prev_timestamp", lag("timestamp").over(user_window))
df = df.withColumn("time_diff_sec", 
                   unix_timestamp("timestamp") - unix_timestamp("prev_timestamp"))

# 3. Mark start of new session (30 mins = 1800 seconds)
# Null prev_timestamp means it's the first event -> New Session
df = df.withColumn("is_new_session", 
                   when((col("time_diff_sec") > 1800) | col("time_diff_sec").isNull(), 1).otherwise(0))

# 4. Generate Session ID (Cumulative Sum of markers)
df = df.withColumn("session_id", sum("is_new_session").over(user_window))

# Result: Each user event now has a 'session_id' (1, 2, 3...) localized to that user.
# You can then aggregate by user_id + session_id to get start/end times and count.
```

## Scenario 2: Login / Logout Session Duration
**Problem:** You have `Login` and `Logout` events. Calculate the duration of each completed session. Handle cases where a `Logout` might be missing (ignore or cap).

**Technique:** Use `lead()` to look ahead at the next event.

**Code:**
```python
from pyspark.sql.functions import lead, col, unix_timestamp
from pyspark.sql.window import Window

window_spec = Window.partitionBy("user_id").orderBy("timestamp")

# Look ahead to see the next event type and time
df_with_next = df.withColumn("next_event", lead("event_type").over(window_spec)) \
                 .withColumn("next_timestamp", lead("timestamp").over(window_spec))

# Filter for completed sessions: Current is Login, Next is Logout
completed_sessions = df_with_next.filter(
    (col("event_type") == "Login") & (col("next_event") == "Logout")
)

# Calculate Duration
result = completed_sessions.withColumn("duration_sec", 
    unix_timestamp("next_timestamp") - unix_timestamp("timestamp")
)
```

## Scenario 3: Clickstream Path Analysis (Funnel)
**Problem:** Identify the most common 3-step path users take (e.g., Home -> Search -> Product).

**Technique:** `collect_list` or string concatenation with `lead`.

**Code:**
```python
from pyspark.sql.functions import concat_ws, lead, count, col, lit
from pyspark.sql.window import Window

window_spec = Window.partitionBy("user_id").orderBy("timestamp")

# Create the 3-step path for every row
df_path = df.withColumn("step_1", col("page_name")) \
            .withColumn("step_2", lead("page_name", 1).over(window_spec)) \
            .withColumn("step_3", lead("page_name", 2).over(window_spec))

# Filter out incomplete paths
df_path = df_path.dropna(subset=["step_2", "step_3"])

# Concatenate to form a path string
df_path = df_path.withColumn("path", 
              concat_ws(" -> ", col("step_1"), col("step_2"), col("step_3")))

# Count frequencies
top_paths = df_path.groupBy("path").agg(count("*").alias("frequency")) \
                   .orderBy(col("frequency").desc())
```

## Scenario 4: Finding Max Concurrent Users (Advanced)
**Problem:** Given session start and end times, find the maximum number of users active at the same time.

**Technique:** Explode start/end logic. Treat Start as +1, End as -1.

**Code:**
```python
# 1. Decompose sessions into points
start_df = sessions.select(col("start_time").alias("time"), lit(1).alias("change"))
end_df = sessions.select(col("end_time").alias("time"), lit(-1).alias("change"))

combined = start_df.union(end_df)

# 2. Verify order (process starts before ends if timestamps match)
window_cumulative = Window.orderBy("time")

# 3. Running Sum
result = combined.withColumn("active_users", sum("change").over(window_cumulative))
max_concurrency = result.agg({"active_users": "max"}).collect()[0][0]
```

## Scenario 5: Identifying Bots (High Frequency)
**Problem:** Flag users who perform more than 50 actions in any 1-minute sliding window.

**Technique:** Range Window (sliding time window).

**Code:**
```python
from pyspark.sql.functions import count
from pyspark.sql.window import Window

# Define window: Partition by User, Order by Time, Range of 60 seconds looking back
# Range between 60 seconds preceding and current row
window_bot = Window.partitionBy("user_id").orderBy(col("timestamp").cast("long")) \
                   .rangeBetween(-60, 0)

df_bots = df.withColumn("events_last_min", count("*").over(window_bot))

bots = df_bots.filter(col("events_last_min") > 50).select("user_id").distinct()
```
