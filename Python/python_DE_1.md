# Python Data Engineering Interview Cheatsheet

> **FAANG Senior DE Python Questions** - Real interview patterns combining strings, lists, dicts, and tuples

---

## 📑 Table of Contents
| # | Category | Pattern |
|---|----------|---------|
| 1 | [Top N by Group](#1-top-n-records-by-group) | Dict grouping + Sorting |
| 2 | [Sessionization](#2-sessionization-clickstream) | Log parsing + Time gaps |
| 3 | [Log Aggregation](#3-log-aggregation) | String parsing + Counters |
| 4 | [Data Deduplication](#4-data-deduplication-keep-latest) | Dict merge by key |
| 5 | [Flatten Nested JSON](#5-flatten-nested-json) | Recursive dict traversal |
| 6 | [Rolling Aggregations](#6-rolling-aggregations-moving-average) | Sliding window |
| 7 | [Rate Limiter](#7-rate-limiter-sliding-window) | Time-based filtering |
| 8 | [Merge Sorted Streams](#8-merge-k-sorted-streams) | Heap + generators |
| 9 | [Schema Validation](#9-schema-validation-json-records) | Type checking + DLQ |
| 10 | [Event Time Ordering](#10-event-time-ordering-late-data) | Watermarks |
| 11 | [SCD Type 2](#11-scd-type-2-slowly-changing-dimension) | History tracking |
| 12 | [Idempotent Upsert](#12-idempotent-upsert-merge) | Conflict resolution |
| 13 | [File Chunking](#13-file-chunking-large-files) | Generator-based reads |
| 14 | [Retry with Backoff](#14-retry-with-exponential-backoff) | Fault tolerance |
| 15 | [Partitioning Logic](#15-partitioning-hash-and-range) | Data distribution |

---

## 1. Top N Records by Group

**Scenario:** Find top 2 highest-paid employees per department.

```python
data = [
    ("HR", "Alice", 5000), ("IT", "Bob", 8000), ("HR", "Charlie", 6000),
    ("IT", "Dave", 9000), ("IT", "Eve", 7000), ("HR", "Frank", 4000)
]

def top_n_by_dept(employees, n=2):
    dept_map = {}
    for dept, name, salary in employees:
        if dept not in dept_map:
            dept_map[dept] = []
        dept_map[dept].append((name, salary))
    
    result = {}
    for dept, staff in dept_map.items():
        staff.sort(key=lambda x: x[1], reverse=True)
        result[dept] = staff[:n]
    return result

# Output: {'HR': [('Charlie', 6000), ('Alice', 5000)], 'IT': [('Dave', 9000), ('Bob', 8000)]}
```

---

## 2. Sessionization (Clickstream)

**Scenario:** Group user events into sessions with 30-min inactivity gap.

```python
from datetime import datetime, timedelta

logs = [
    "2026-02-08 10:00:00,user_1,click",
    "2026-02-08 10:05:00,user_1,scroll",
    "2026-02-08 11:00:00,user_1,click",  # New session (55 min gap)
    "2026-02-08 10:01:00,user_2,click"
]

def sessionize(log_strings, gap_minutes=30):
    user_events = {}
    
    for log in log_strings:
        ts_str, uid, action = log.split(',')
        ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        if uid not in user_events:
            user_events[uid] = []
        user_events[uid].append(ts)
    
    sessions = {}
    for uid, times in user_events.items():
        times.sort()
        session_count = 1
        for i in range(1, len(times)):
            if (times[i] - times[i-1]) > timedelta(minutes=gap_minutes):
                session_count += 1
        sessions[uid] = session_count
    return sessions

# Output: {'user_1': 2, 'user_2': 1}
```

---

## 3. Log Aggregation

**Scenario:** Parse logs, count error codes, return sorted by frequency.

```python
raw_logs = [
    "ERROR:404:Not Found",
    "INFO:200:OK",
    "ERROR:500:Internal Server Error",
    "ERROR:404:Not Found"
]

def count_errors(logs):
    counts = {}
    for log in logs:
        if log.startswith("ERROR"):
            code = log.split(":")[1]
            counts[code] = counts.get(code, 0) + 1
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)

# Output: [('404', 2), ('500', 1)]
```

---

## 4. Data Deduplication (Keep Latest)

**Scenario:** Given records with timestamps, keep only the latest per key.

```python
records = [
    {"id": 1, "value": "old", "ts": "2026-02-08 10:00:00"},
    {"id": 1, "value": "new", "ts": "2026-02-08 11:00:00"},
    {"id": 2, "value": "only", "ts": "2026-02-08 10:30:00"},
]

def dedupe_keep_latest(records):
    latest = {}
    for r in records:
        key = r["id"]
        if key not in latest or r["ts"] > latest[key]["ts"]:
            latest[key] = r
    return list(latest.values())

# Output: [{"id": 1, "value": "new", ...}, {"id": 2, "value": "only", ...}]
```

---

## 5. Flatten Nested JSON

**Scenario:** Convert nested JSON to flat dict with dot-notation keys.

```python
nested = {
    "user": {
        "name": "Alice",
        "address": {
            "city": "Seattle",
            "zip": "98101"
        }
    },
    "active": True
}

def flatten_json(obj, parent_key='', sep='.'):
    items = {}
    for k, v in obj.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_json(v, new_key, sep))
        else:
            items[new_key] = v
    return items

# Output: {'user.name': 'Alice', 'user.address.city': 'Seattle', 
#          'user.address.zip': '98101', 'active': True}
```

---

## 6. Rolling Aggregations (Moving Average)

**Scenario:** Calculate moving average over last N elements (streaming).

```python
from collections import deque

class MovingAverage:
    def __init__(self, window_size):
        self.window = deque(maxlen=window_size)
        self.total = 0
    
    def next(self, val):
        if len(self.window) == self.window.maxlen:
            self.total -= self.window[0]
        self.window.append(val)
        self.total += val
        return self.total / len(self.window)

# Usage
ma = MovingAverage(3)
print([ma.next(x) for x in [1, 10, 3, 5]])  # [1.0, 5.5, 4.67, 6.0]
```

---

## 7. Rate Limiter (Sliding Window)

**Scenario:** Check if user exceeded N requests in last M seconds.

```python
from time import time

class RateLimiter:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window = window_seconds
        self.user_requests = {}
    
    def is_allowed(self, user_id):
        now = time()
        if user_id not in self.user_requests:
            self.user_requests[user_id] = []
        
        # Remove expired timestamps
        self.user_requests[user_id] = [
            ts for ts in self.user_requests[user_id] 
            if now - ts < self.window
        ]
        
        if len(self.user_requests[user_id]) < self.max_requests:
            self.user_requests[user_id].append(now)
            return True
        return False

# Usage: limiter = RateLimiter(100, 60)  # 100 requests per minute
```

---

## 8. Merge K Sorted Streams

**Scenario:** Merge multiple sorted log files efficiently.

```python
import heapq

def merge_sorted_streams(streams):
    """Merge K sorted iterables using min-heap"""
    heap = []
    
    for i, stream in enumerate(streams):
        it = iter(stream)
        first = next(it, None)
        if first is not None:
            heapq.heappush(heap, (first, i, it))
    
    while heap:
        val, stream_idx, it = heapq.heappop(heap)
        yield val
        next_val = next(it, None)
        if next_val is not None:
            heapq.heappush(heap, (next_val, stream_idx, it))

# Usage
streams = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
print(list(merge_sorted_streams(streams)))  # [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

---

## 9. Schema Validation (JSON Records)

**Scenario:** Validate records, route valid/invalid to different outputs.

```python
SCHEMA = {"id": int, "name": str, "amount": (int, float)}

def validate_record(record, schema):
    for field, expected_type in schema.items():
        if field not in record:
            return False, f"Missing: {field}"
        if not isinstance(record[field], expected_type):
            return False, f"Invalid type: {field}"
    return True, None

def process_with_dlq(records):
    valid, dead_letter = [], []
    for r in records:
        is_valid, error = validate_record(r, SCHEMA)
        if is_valid:
            valid.append(r)
        else:
            dead_letter.append({"record": r, "error": error})
    return valid, dead_letter

# Usage
records = [{"id": 1, "name": "A", "amount": 100}, {"id": "bad", "name": "B"}]
valid, dlq = process_with_dlq(records)
```

---

## 10. Event Time Ordering (Late Data)

**Scenario:** Handle out-of-order events with watermarks.

```python
from datetime import datetime, timedelta

class WatermarkProcessor:
    def __init__(self, max_lateness_sec=60):
        self.max_lateness = timedelta(seconds=max_lateness_sec)
        self.watermark = None
        self.buffer = []
        self.late_events = []
    
    def process(self, event_time, data):
        if self.watermark is None:
            self.watermark = event_time
        
        self.watermark = max(self.watermark, event_time - self.max_lateness)
        
        if event_time < self.watermark:
            self.late_events.append((event_time, data))  # Too late
        else:
            self.buffer.append((event_time, data))
    
    def flush(self):
        ready = [e for e in self.buffer if e[0] < self.watermark]
        self.buffer = [e for e in self.buffer if e[0] >= self.watermark]
        return sorted(ready, key=lambda x: x[0])
```

---

## 11. SCD Type 2 (Slowly Changing Dimension)

**Scenario:** Track historical changes with effective dates.

```python
from datetime import date

def apply_scd2(existing, incoming, key_field):
    today = date.today()
    result = []
    existing_map = {r[key_field]: r for r in existing if r.get("is_current")}
    
    for record in incoming:
        key = record[key_field]
        if key in existing_map:
            old = existing_map[key]
            # Check if anything changed
            if any(old.get(k) != record.get(k) for k in record if k != key_field):
                old["end_date"] = today
                old["is_current"] = False
                result.append(old)
                
                record["start_date"] = today
                record["end_date"] = None
                record["is_current"] = True
                result.append(record)
            else:
                result.append(old)
        else:
            record["start_date"] = today
            record["is_current"] = True
            result.append(record)
    return result
```

---

## 12. Idempotent Upsert (Merge)

**Scenario:** Merge new data into existing - incoming wins on conflict.

```python
def upsert(existing, incoming, key_fields):
    def make_key(record):
        return tuple(record[k] for k in key_fields)
    
    merged = {make_key(r): r for r in existing}
    for record in incoming:
        merged[make_key(record)] = record
    return list(merged.values())

# Usage
existing = [{"id": 1, "name": "old"}, {"id": 2, "name": "keep"}]
incoming = [{"id": 1, "name": "new"}, {"id": 3, "name": "add"}]
result = upsert(existing, incoming, ["id"])
# [{"id": 1, "name": "new"}, {"id": 2, "name": "keep"}, {"id": 3, "name": "add"}]
```

---

## 13. File Chunking (Large Files)

**Scenario:** Process large files without loading into memory.

```python
def process_large_file(filepath, chunk_size=10000):
    def read_chunks(f, size):
        while True:
            lines = []
            for _ in range(size):
                line = f.readline()
                if not line:
                    break
                lines.append(line.strip())
            if not lines:
                break
            yield lines
    
    with open(filepath, 'r') as f:
        for chunk in read_chunks(f, chunk_size):
            process_chunk(chunk)  # Your logic here

def process_chunk(lines):
    return len(lines)
```

---

## 14. Retry with Exponential Backoff

**Scenario:** Fault-tolerant API calls.

```python
import time
import random

def retry_with_backoff(func, max_retries=3, base_delay=1):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            print(f"Attempt {attempt + 1} failed. Retry in {delay:.2f}s")
            time.sleep(delay)

# Usage
def flaky_api():
    if random.random() < 0.7:
        raise ConnectionError("API down")
    return {"status": "ok"}

result = retry_with_backoff(flaky_api, max_retries=5)
```

---

## 15. Partitioning (Hash and Range)

**Scenario:** Distribute data across partitions.

```python
def hash_partition(key, num_partitions):
    return hash(key) % num_partitions

def range_partition(value, boundaries):
    # boundaries = [100, 200] -> 3 partitions: <100, 100-199, >=200
    for i, boundary in enumerate(boundaries):
        if value < boundary:
            return i
    return len(boundaries)

# Usage
records = [("user_A", 50), ("user_B", 150), ("user_C", 250)]
partitioned = {}
for user, value in records:
    p = range_partition(value, [100, 200])
    partitioned.setdefault(p, []).append((user, value))
# {0: [('user_A', 50)], 1: [('user_B', 150)], 2: [('user_C', 250)]}
```

---

## Key Patterns Summary

| Pattern | Technique | Interview Signal |
|---------|-----------|------------------|
| **Grouping** | `dict.setdefault()` or `defaultdict` | High |
| **Counting** | `dict.get(k, 0) + 1` | High |
| **Top N** | `sorted(key=lambda)[:n]` | High |
| **Dedup** | Dict keyed by unique fields | High |
| **Streaming** | `deque(maxlen=N)` | Medium |
| **Merge K** | `heapq` + generators | Medium |
| **Chunking** | Generator + `yield` | Medium |
| **Retry** | Exponential backoff | Medium |
| **DLQ** | Try/except + separate list | Medium |

---

## Python Idioms for Interviews

```python
# 1. setdefault for grouping
groups = {}
for k, v in data:
    groups.setdefault(k, []).append(v)

# 2. get with default for counting
counts = {}
counts[key] = counts.get(key, 0) + 1

# 3. Dict comprehension
transformed = {k: v * 2 for k, v in data.items() if v > 0}

# 4. Generator for memory efficiency
def lazy_process(records):
    for r in records:
        yield transform(r)

# 5. Unpacking
first, *middle, last = sorted_list

# 6. Tuple unpacking in loops
for name, age, city in list_of_tuples:
    print(name)
```