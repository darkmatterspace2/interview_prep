# Top 30 FAANG & FinTech Data Engineering Questions
*Companies: Amazon, Google, Netflix, JPMC, Citi, Flipkart, Microsoft, Meta*

A curated list of 30 highly distinct and challenging questions often asked in top-tier product and finance companies, focusing on SQL, Python, and PySpark.

---

## Table of Contents
1. [SQL Scenarios (1-10)](#sql-scenarios)
2. [Python Coding (11-20)](#python-coding)
3. [PySpark & Big Data (21-30)](#pyspark--big-data)

---

## SQL Scenarios

### 1. Market Basket Analysis (Amazon/Flipkart)
**Q:** Find pairs of products that are most frequently bought together.
**A:**
```sql
SELECT 
    p1.product_id as Product_A, 
    p2.product_id as Product_B, 
    COUNT(*) as frequency
FROM Orders p1
JOIN Orders p2 
    ON p1.order_id = p2.order_id     -- Same Order
    AND p1.product_id < p2.product_id -- Avoid duplicates (A-B vs B-A) and self-pairs (A-A)
GROUP BY 1, 2
ORDER BY frequency DESC
LIMIT 5;
```

### 2. Calculate Median Salary (Google/JPMC)
**Q:** Calculate the median salary of employees without using a built-in `MEDIAN()` function.
**A:**
```sql
SELECT AVG(salary) as MedianSalary
FROM (
    SELECT salary,
           ROW_NUMBER() OVER (ORDER BY salary) as row_num,
           COUNT(*) OVER () as total_count
    FROM Employees
) sub
WHERE row_num IN ((total_count + 1) / 2, (total_count + 2) / 2); -- Handles both Odd and Even counts
```

### 3. Consecutive Active Days (Facebook/Zynga)
**Q:** Find all users who logged in on 3 consecutive days.
**A:**
```sql
SELECT DISTINCT user_id
FROM (
    SELECT user_id, login_date,
           LAG(login_date, 1) OVER (PARTITION BY user_id ORDER BY login_date) as prev_1,
           LAG(login_date, 2) OVER (PARTITION BY user_id ORDER BY login_date) as prev_2
    FROM UserLogins
) sub
WHERE DATEDIFF(day, prev_1, login_date) = 1
  AND DATEDIFF(day, prev_2, prev_1) = 1;
```

### 4. Running Balance with Reset (Citi/Morgan Stanley)
**Q:** Calculate a running total of transactions, but reset the running total to 0 if the account type changes.
**A:**
```sql
SELECT 
    transaction_id, account_type, amount,
    SUM(amount) OVER (PARTITION BY account_type ORDER BY transaction_date) as running_balance
FROM Transactions;
```

### 5. Resurrected Users (Netflix/Spotify)
**Q:** Identify users who were active last month, inactive this month, but active again next month (Churned then Returned).
**A:**
```sql
WITH MonthlyActivity AS (
    SELECT user_id, 
           DATE_TRUNC('month', activity_date) as mth
    FROM activity
    GROUP BY 1, 2
)
SELECT t1.user_id
FROM MonthlyActivity t1
LEFT JOIN MonthlyActivity t2 ON t1.user_id = t2.user_id AND t2.mth = t1.mth + INTERVAL '1 month'
JOIN MonthlyActivity t3 ON t1.user_id = t3.user_id AND t3.mth = t1.mth + INTERVAL '2 month'
WHERE t2.user_id IS NULL; -- Active Month 1, Inactive Month 2, Active Month 3
```

### 6. First Touch Attribution (Marketing Tech)
**Q:** Find the *first* channel a user came from before converting.
**A:**
```sql
SELECT DISTINCT user_id, 
       FIRST_VALUE(channel) OVER (PARTITION BY user_id ORDER BY timestamp ASC) as first_channel
FROM user_journey
WHERE conversion_event = 1;
```

### 7. Identifying Mutual Friends (Meta)
**Q:** Given table `Friends(user1, user2)`, count mutual friends for all pairs.
**A:**
```sql
WITH AllFriends AS (
    SELECT user1, user2 FROM Friends
    UNION ALL
    SELECT user2, user1 FROM Friends -- Ensure bidirectionality
)
SELECT a.user1, b.user1 as user2, COUNT(*) as mutuals
FROM AllFriends a
JOIN AllFriends b ON a.user2 = b.user2 -- Join on common friend
AND a.user1 < b.user1
GROUP BY 1, 2;
```

### 8. Session Timeout Identification
**Q:** Calculate session duration, defining a session break as 30 mins of inactivity.
**A:**
```sql
SELECT user_id, session_id, MIN(ts) as start, MAX(ts) as end
FROM (
    SELECT user_id, ts,
           SUM(is_new_session) OVER (PARTITION BY user_id ORDER BY ts) as session_id
    FROM (
        SELECT user_id, ts, 
               CASE WHEN ts - LAG(ts) OVER (PARTITION BY user_id ORDER BY ts) > 1800 
               THEN 1 ELSE 0 END as is_new_session
        FROM clicks
    ) a
) b
GROUP BY 1, 2;
```

### 9. Delete Duplicates using SQL (No Distinct)
**Q:** Delete duplicate emails, keeping the one with the smallest ID.
**A:**
```sql
DELETE FROM Person 
WHERE Id NOT IN (
    SELECT MIN(Id) 
    FROM Person 
    GROUP BY Email
);
```

### 10. Histogram of Frequency (Uber)
**Q:** Calculate the distribution of the number of rides users took (e.g., How many users took 1 ride? How many took 2?).
**A:**
```sql
SELECT rides_count, COUNT(user_id) as num_users
FROM (
    SELECT user_id, COUNT(*) as rides_count
    FROM rides
    GROUP BY user_id
) sub
GROUP BY rides_count
ORDER BY rides_count;
```

---

## Python Coding

### 11. Flatten Nested JSON (Amazon)
**Q:** Write a function to flatten an arbitrarily nested JSON object.
**A:**
```python
def flatten_json(y):
    out = {}
    def flatten(x, name=''):
        if type(x) is dict:
            for a in x: flatten(x[a], name + a + '.')
        elif type(x) is list:
            for i, a in enumerate(x): flatten(a, name + str(i) + '.')
        else:
            out[name[:-1]] = x
    flatten(y)
    return out
```

### 12. Parse Large Log File (Google)
**Q:** Top 10 IP addresses from 50GB log file (Constant Memory).
**A:**
```python
from collections import Counter
def top_ips(path):
    c = Counter()
    with open(path) as f:
        for line in f:
            c[line.split()[0]] += 1
    return c.most_common(10)
```

### 13. Valid Parentheses (Microsoft)
**Q:** Check if a string of brackets `()[]{}` is valid.
**A:**
```python
def isValid(s):
    stack = []
    mapping = {")": "(", "}": "{", "]": "["}
    for char in s:
        if char in mapping:
            top_element = stack.pop() if stack else '#'
            if mapping[char] != top_element:
                return False
        else:
            stack.append(char)
    return not stack
```

### 14. Group Anagrams (Apple)
**Q:** Group `["eat", "tea", "tan", "ate", "nat", "bat"]`.
**A:**
```python
from collections import defaultdict
def groupAnagrams(strs):
    ans = defaultdict(list)
    for s in strs:
        ans[tuple(sorted(s))].append(s)
    return list(ans.values())
```

### 15. Merge K Sorted Lists (Streaming Data)
**Q:** Merge K sorted streams (iterators) into one sorted stream.
**A:**
```python
import heapq
def merge_k_sorted(lists):
    heap = []
    # Add first element of each list to heap
    for i, lst in enumerate(lists):
        if lst: heapq.heappush(heap, (lst[0], i, 0)) # val, list_idx, element_idx
    
    result = []
    while heap:
        val, list_idx, element_idx = heapq.heappop(heap)
        result.append(val)
        
        # Push next element from the same list
        if element_idx + 1 < len(lists[list_idx]):
            heapq.heappush(heap, (lists[list_idx][element_idx+1], list_idx, element_idx+1))
            
    return result
```

### 16. Missing Number in Sequence
**Q:** Find the missing number in array `[0...n]`.
**A:**
```python
def missingNumber(nums):
    n = len(nums)
    expected_sum = n * (n + 1) // 2
    return expected_sum - sum(nums)
```

### 17. LRU Cache Implementation (System Design)
**Q:** Design an LRU Cache with O(1) operations.
**A:** Use `OrderedDict`.
```python
from collections import OrderedDict
class LRUCache(OrderedDict):
    def __init__(self, capacity: int):
        self.capacity = capacity

    def get(self, key: int) -> int:
        if key not in self: return -1
        self.move_to_end(key)
        return self[key]

    def put(self, key: int, value: int) -> None:
        if key in self: self.move_to_end(key)
        self[key] = value
        if len(self) > self.capacity: self.popitem(last=False)
```

### 18. API Rate Limiter (Logic)
**Q:** Write a function that returns False if called more than N times in 1 second.
**A:**
```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, limit):
        self.limit = limit
        self.timestamps = deque()
    
    def allow_request(self):
        now = time.time()
        # Remove timestamps older than 1s
        while self.timestamps and self.timestamps[0] <= now - 1:
            self.timestamps.popleft()
            
        if len(self.timestamps) < self.limit:
            self.timestamps.append(now)
            return True
        return False
```

### 19. ETL: Clean and Transform Date Strings
**Q:** Convert list of mixed date formats `['2021-01-01', '01/02/2021']` to standard `YYYY-MM-DD`.
**A:** 
```python
from dateutil import parser
def normalize_dates(dates):
    return [parser.parse(d).strftime('%Y-%m-%d') for d in dates]
```

### 20. Find Intersection of Two Arrays
**Q:** Efficiently find intersection or two huge arrays.
**A:**
```python
def intersection(nums1, nums2):
    return list(set(nums1) & set(nums2))
```

---

## PySpark & Big Data

### 21. Handling Skewed Join (Amazon)
**Q:** Fix OOM when joining Sales (Billion) and Products (Million - skewed).
**A:** Use **Salting**.
```python
# 1. Salt Big Table
df_big = df_big.withColumn("salt", (rand() * 10).cast("int"))
# 2. Explode Small Table
df_small = df_small.withColumn("salt_arr", array([lit(i) for i in range(10)]))\
                   .withColumn("salt", explode("salt_arr"))
# 3. Join
df_joined = df_big.join(df_small, ["key", "salt"])
```

### 22. Sessionization (Netflix)
**Q:** New session after 30 mins inactivity.
**A:** 
```python
w = Window.partitionBy("user").orderBy("ts")
df = df.withColumn("new_sess", (col("ts") - lag("ts").over(w) > 1800).cast("int"))
df = df.withColumn("sess_id", sum("new_sess").over(w))
```

### 23. Top N Items per Group at Scale (Uber)
**Q:** Top 3 items sold per category (Optimized).
**A:**
```python
w = Window.partitionBy("category").orderBy(desc("sales"))
df_top = df.withColumn("rn", rank().over(w)).filter("rn <= 3")
```

### 24. Explode and Aggregate (Array Handling)
**Q:** Database has column `tags` (Array). Count frequency of each tag.
**A:**
```python
df.select(explode(col("tags")).alias("tag")) \
  .groupBy("tag").count().orderBy(desc("count")).show()
```

### 25. Broadcast Variable Usage
**Q:** When to use Broadcast Variable vs Broadcast Join?
**A:**
*   **Broadcast Join:** Distributes a DataFrame (Table).
*   **Broadcast Variable:** Distributes a read-only object (e.g., a huge Dictionary/List) to executors for efficient lookups in UDFs or map operations, avoiding shipping it with every task closure.

### 26. Custom Accumulator
**Q:** How to count "Bad Records" without stopping the job or bringing data to driver?
**A:**
```python
bad_records = spark.sparkContext.accumulator(0)

def process_row(row):
    if row['val'] is None:
        bad_records.add(1)
        
df.foreach(process_row)
print(bad_records.value)
```

### 27. Filter Pushdown optimization
**Q:** You filter a parquet file by `date`. Why is it fast?
**A:** 
Spark pushes the filter to the Parquet reader. Parquet files have footer metadata (Min/Max values for columns). Spark skips entire Row Groups that don't match the filter (Predicate Pushdown), minimizing I/O.

### 28. Coalesce vs Repartition (Scenario)
**Q:** You have 1000 small files. You want to write 10 files.
**A:** `df.coalesce(10).write...`.
**Q:** You want to write by date partition?
**A:** `df.repartition("date").write.partitionBy("date")...`

### 29. Handling Bad Data (JSON)
**Q:** How to handle corrupt JSON lines in a read?
**A:**
```python
df = spark.read.option("mode", "PERMISSIVE") \
               .option("columnNameOfCorruptRecord", "_corrupt") \
               .json("path")
df_bad = df.filter(col("_corrupt").isNotNull())
```

### 30. Unit Testing PySpark
**Q:** How do you test a PySpark transformation function locally?
**A:**
Use `chispa` or `pandas` testing for assertion.
Create a local SparkSession in the test fixture.
```python
def test_transform(spark):
    source_df = spark.createDataFrame([(1,)], ["id"])
    actual_df = my_transform(source_df)
    expected_df = spark.createDataFrame([(1, 10)], ["id", "val"])
    assert_df_equality(actual_df, expected_df)
```
