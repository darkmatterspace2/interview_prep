# Python Data Engineering Interview Questions

> **FAANG Senior DE Python Questions** - String manipulation, Lists, Dicts, Tuples

---

## 📑 Table of Contents
| # | Category | Scenario |
|---|----------|----------|
| 1 | [Email Masking](#1-email-masking-pii-protection) | `g*****3@gmail.com` |
| 2 | [URL Parsing](#2-url-parsing--utm-extraction) | Extract UTM params |
| 3 | [IP Log Aggregation](#3-ip-log-aggregation) | Count by IP/endpoint |
| 4 | [Phone Normalization](#4-phone-number-normalization) | Various formats → E.164 |
| 5 | [Date Gap Finder](#5-find-missing-dates) | Find gaps in date series |
| 6 | [JSON Flattening](#6-nested-json-flattening) | Flatten nested dicts |
| 7 | [CSV Validation](#7-csv-row-validation) | Validate + clean records |
| 8 | [Session Duration](#8-session-duration-by-user) | Time between events |
| 9 | [Log Error Patterns](#9-extract-error-patterns-from-logs) | Regex extraction |
| 10 | [Top N by Group](#10-top-n-records-by-group) | Top 2 salary by dept |
| 11 | [Dedup Keep Latest](#11-deduplication-keep-latest) | Merge by timestamp |
| 12 | [Sliding Window Count](#12-sliding-window-event-count) | Rate limiting |
| 13 | [Transform Pipeline](#13-chained-transformation-pipeline) | Functional transforms |
| 14 | [UUID Extraction](#14-extract-uuids-from-mixed-text) | Regex + validation |
| 15 | [Merge Sorted Logs](#15-merge-k-sorted-log-streams) | Heap merge |

---

## 1. Top N Records by Group (Dictionary + Sorting)

**The Scenario:** Given a list of employee tuples, find the top 2 highest-paid employees in each department.

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
        # Sort by salary descending and take top N
        staff.sort(key=lambda x: x[1], reverse=True)
        result[dept] = staff[:n]
    return result

# Output: {'HR': [('Charlie', 6000), ('Alice', 5000)], 'IT': [('Dave', 9000), ('Bob', 8000)]}

```

---

## 2. Sessionization (Clickstream Parsing)

**The Scenario:** Group events by user and calculate "session" length. You often have to parse a raw log string first.

```python
logs = [
    "2026-02-08 10:00:00,user_1,click",
    "2026-02-08 10:05:00,user_1,scroll",
    "2026-02-08 10:01:00,user_2,click"
]

from datetime import datetime

def get_session_durations(log_strings):
    user_activity = {}
    
    for log in log_strings:
        ts_str, uid, action = log.split(',')
        ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        
        if uid not in user_activity:
            user_activity[uid] = []
        user_activity[uid].append(ts)
        
    sessions = {}
    for uid, times in user_activity.items():
        times.sort()
        # Duration = Max time - Min time
        sessions[uid] = (times[-1] - times[0]).total_seconds()
    return sessions

```

---

## 3. Log Aggregation (String Manipulation + Tuples)

**The Scenario:** Extract error codes from log lines and count occurrences, returning a list of tuples sorted by frequency.

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
            # Split by ':' and take the second element (error code)
            code = log.split(":")[1]
            counts[code] = counts.get(code, 0) + 1
            
    # Convert to list of tuples and sort by count (descending)
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)

# Output: [('404', 2), ('500', 1)]

```

## 1. Email Masking (PII Protection)

**Scenario:** Mask emails in user records: `geek123@gmail.com` → `g*****3@gmail.com`

```python
def mask_email(email):
    local, domain = email.split('@')
    if len(local) <= 2:
        masked = local[0] + '*' * (len(local) - 1)
    else:
        masked = local[0] + '*' * (len(local) - 2) + local[-1]
    return f"{masked}@{domain}"

users = [
    {"id": 1, "email": "alice.smith@company.com"},
    {"id": 2, "email": "bob@test.org"},
    {"id": 3, "email": "charlie123@gmail.com"}
]

masked_users = [{**u, "email": mask_email(u["email"])} for u in users]
# [{'id': 1, 'email': 'a*********h@company.com'}, ...]
```

---

## 2. URL Parsing & UTM Extraction

**Scenario:** Extract campaign info from URLs in clickstream data.

```python
from urllib.parse import urlparse, parse_qs

def extract_utm(url):
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return {
        "domain": parsed.netloc,
        "path": parsed.path,
        "utm_source": params.get("utm_source", [None])[0],
        "utm_campaign": params.get("utm_campaign", [None])[0]
    }

clicks = [
    ("user_1", "https://shop.com/product?utm_source=google&utm_campaign=summer"),
    ("user_2", "https://shop.com/cart"),
    ("user_3", "https://shop.com/checkout?utm_source=facebook")
]

enriched = [(uid, extract_utm(url)) for uid, url in clicks]
# [('user_1', {'domain': 'shop.com', 'utm_source': 'google', 'utm_campaign': 'summer'}), ...]
```

---

## 3. IP Log Aggregation

**Scenario:** Parse access logs and count requests per IP and endpoint.

```python
logs = [
    "192.168.1.1 - - [08/Feb/2026:10:00:00] \"GET /api/users HTTP/1.1\" 200",
    "192.168.1.2 - - [08/Feb/2026:10:00:01] \"POST /api/orders HTTP/1.1\" 201",
    "192.168.1.1 - - [08/Feb/2026:10:00:02] \"GET /api/users HTTP/1.1\" 200",
]

import re

def parse_log(line):
    pattern = r'(\d+\.\d+\.\d+\.\d+).*\"(\w+) (\S+)'
    match = re.search(pattern, line)
    if match:
        return {"ip": match.group(1), "method": match.group(2), "endpoint": match.group(3)}
    return None

def aggregate_by_ip_endpoint(logs):
    counts = {}
    for log in logs:
        parsed = parse_log(log)
        if parsed:
            key = (parsed["ip"], parsed["endpoint"])
            counts[key] = counts.get(key, 0) + 1
    return sorted(counts.items(), key=lambda x: -x[1])

# Output: [(('192.168.1.1', '/api/users'), 2), (('192.168.1.2', '/api/orders'), 1)]
```

---

## 4. Phone Number Normalization

**Scenario:** Convert various phone formats to E.164 standard.

```python
import re

def normalize_phone(phone, country_code="+1"):
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone)
    
    # Handle different lengths
    if len(digits) == 10:
        return f"{country_code}{digits}"
    elif len(digits) == 11 and digits.startswith('1'):
        return f"+{digits}"
    elif len(digits) > 10:
        return f"+{digits}"
    return None  # Invalid

contacts = [
    {"name": "Alice", "phone": "(555) 123-4567"},
    {"name": "Bob", "phone": "555.987.6543"},
    {"name": "Charlie", "phone": "+1-555-222-3333"},
    {"name": "Dave", "phone": "5551234567"}
]

normalized = [
    {**c, "phone": normalize_phone(c["phone"])} 
    for c in contacts
]
# All become: +15551234567 format
```

---

## 5. Find Missing Dates

**Scenario:** Given transaction dates, find all missing dates in the range.

```python
from datetime import datetime, timedelta

def find_missing_dates(date_strings):
    dates = [datetime.strptime(d, "%Y-%m-%d") for d in date_strings]
    dates.sort()
    
    missing = []
    current = dates[0]
    
    while current <= dates[-1]:
        if current not in dates:
            missing.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    
    return missing

transactions = [
    ("txn_1", "2026-02-01"),
    ("txn_2", "2026-02-02"),
    ("txn_3", "2026-02-05"),  # Gap here
    ("txn_4", "2026-02-06"),
]

dates = [t[1] for t in transactions]
missing = find_missing_dates(dates)
# ['2026-02-03', '2026-02-04']
```

---

## 6. Nested JSON Flattening

**Scenario:** Flatten nested event data for loading into columnar storage.

```python
def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        elif isinstance(v, list):
            items.append((new_key, str(v)))  # Convert list to string
        else:
            items.append((new_key, v))
    return dict(items)

events = [
    {"user": {"id": 1, "profile": {"name": "Alice", "tier": "gold"}}, "action": "click"},
    {"user": {"id": 2, "profile": {"name": "Bob", "tier": "silver"}}, "action": "scroll"}
]

flattened = [flatten_dict(e) for e in events]
# [{'user_id': 1, 'user_profile_name': 'Alice', 'user_profile_tier': 'gold', 'action': 'click'}, ...]
```

---

## 7. CSV Row Validation

**Scenario:** Parse CSV-like data, validate fields, separate valid/invalid.

```python
import re
from datetime import datetime

def validate_row(row_str):
    fields = row_str.split(',')
    if len(fields) != 4:
        return None, "wrong_field_count"
    
    id_, name, email, date_str = [f.strip() for f in fields]
    
    # Validate ID (numeric)
    if not id_.isdigit():
        return None, "invalid_id"
    
    # Validate email
    if not re.match(r'^[\w.-]+@[\w.-]+\.\w+$', email):
        return None, "invalid_email"
    
    # Validate date
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None, "invalid_date"
    
    return {"id": int(id_), "name": name, "email": email, "date": date_str}, None

rows = [
    "1, Alice, alice@test.com, 2026-02-08",
    "2, Bob, bob@, 2026-02-08",
    "3, Charlie, charlie@test.com, invalid-date",
    "4, Dave, dave@test.com, 2026-02-09"
]

valid, invalid = [], []
for row in rows:
    record, error = validate_row(row)
    if record:
        valid.append(record)
    else:
        invalid.append({"row": row, "error": error})
```

---

## 8. Session Duration by User

**Scenario:** Calculate average session duration per user from event logs.

```python
from datetime import datetime
from collections import defaultdict

def calculate_session_durations(events, session_gap_minutes=30):
    """Group events into sessions, calculate durations"""
    user_events = defaultdict(list)
    
    for event in events:
        ts = datetime.strptime(event["timestamp"], "%Y-%m-%d %H:%M:%S")
        user_events[event["user_id"]].append(ts)
    
    user_sessions = {}
    for user, times in user_events.items():
        times.sort()
        sessions = []
        session_start = times[0]
        prev_time = times[0]
        
        for t in times[1:]:
            gap = (t - prev_time).total_seconds() / 60
            if gap > session_gap_minutes:
                # End current session, start new
                sessions.append((prev_time - session_start).total_seconds())
                session_start = t
            prev_time = t
        
        sessions.append((prev_time - session_start).total_seconds())
        user_sessions[user] = {"count": len(sessions), "avg_duration": sum(sessions) / len(sessions)}
    
    return user_sessions

events = [
    {"user_id": "u1", "timestamp": "2026-02-08 10:00:00"},
    {"user_id": "u1", "timestamp": "2026-02-08 10:05:00"},
    {"user_id": "u1", "timestamp": "2026-02-08 11:00:00"},  # New session
    {"user_id": "u2", "timestamp": "2026-02-08 10:00:00"},
]
```

---

## 9. Extract Error Patterns from Logs

**Scenario:** Extract structured error info using regex.

```python
import re
from collections import Counter

def extract_errors(log_lines):
    pattern = r'\[(\w+)\]\s+(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})\s+(\w+Error):\s+(.+?)(?:\s+at\s+(.+))?$'
    
    errors = []
    for line in log_lines:
        match = re.match(pattern, line)
        if match:
            errors.append({
                "level": match.group(1),
                "timestamp": match.group(2),
                "error_type": match.group(3),
                "message": match.group(4),
                "location": match.group(5)
            })
    return errors

logs = [
    "[ERROR] 2026-02-08 10:00:00 ValueError: Invalid input at line 42",
    "[WARN] 2026-02-08 10:00:01 ConnectionError: Timeout at api_client.py:15",
    "[INFO] 2026-02-08 10:00:02 Normal operation"
]

errors = extract_errors(logs)
error_counts = Counter(e["error_type"] for e in errors)
```

---

## 10. Top N Records by Group

**Scenario:** Find top 2 highest-paid employees per department.

```python
def top_n_by_group(records, group_key, sort_key, n=2, desc=True):
    groups = {}
    for r in records:
        g = r[group_key]
        if g not in groups:
            groups[g] = []
        groups[g].append(r)
    
    result = {}
    for group, items in groups.items():
        sorted_items = sorted(items, key=lambda x: x[sort_key], reverse=desc)
        result[group] = sorted_items[:n]
    return result

employees = [
    {"dept": "IT", "name": "Alice", "salary": 90000},
    {"dept": "IT", "name": "Bob", "salary": 85000},
    {"dept": "IT", "name": "Charlie", "salary": 95000},
    {"dept": "HR", "name": "Dave", "salary": 70000},
    {"dept": "HR", "name": "Eve", "salary": 75000},
]

top_earners = top_n_by_group(employees, "dept", "salary", n=2)
# {'IT': [Charlie, Alice], 'HR': [Eve, Dave]}
```

---

## 11. Deduplication Keep Latest

**Scenario:** Keep only the latest record per key based on timestamp.

```python
def dedupe_keep_latest(records, key_field, ts_field):
    latest = {}
    for r in records:
        key = r[key_field]
        if key not in latest or r[ts_field] > latest[key][ts_field]:
            latest[key] = r
    return list(latest.values())

events = [
    {"user_id": "u1", "status": "pending", "updated_at": "2026-02-08 10:00:00"},
    {"user_id": "u1", "status": "completed", "updated_at": "2026-02-08 11:00:00"},
    {"user_id": "u2", "status": "active", "updated_at": "2026-02-08 10:30:00"},
]

deduped = dedupe_keep_latest(events, "user_id", "updated_at")
# [{'user_id': 'u1', 'status': 'completed', ...}, {'user_id': 'u2', ...}]
```

---

## 12. Sliding Window Event Count

**Scenario:** Count events per user in last N seconds (rate limiting).

```python
from collections import defaultdict
from datetime import datetime, timedelta

class SlidingWindowCounter:
    def __init__(self, window_seconds=60):
        self.window = timedelta(seconds=window_seconds)
        self.events = defaultdict(list)
    
    def add_event(self, user_id, timestamp):
        self.events[user_id].append(timestamp)
        self._cleanup(user_id, timestamp)
    
    def _cleanup(self, user_id, current_time):
        cutoff = current_time - self.window
        self.events[user_id] = [t for t in self.events[user_id] if t > cutoff]
    
    def get_count(self, user_id, current_time):
        self._cleanup(user_id, current_time)
        return len(self.events[user_id])
    
    def is_rate_limited(self, user_id, current_time, max_events):
        return self.get_count(user_id, current_time) >= max_events
```

---

## 13. Chained Transformation Pipeline

**Scenario:** Apply multiple transformations to records.

```python
def pipeline(*transforms):
    def apply(records):
        result = records
        for transform in transforms:
            result = [transform(r) for r in result if r is not None]
        return result
    return apply

# Individual transforms
def clean_name(r):
    return {**r, "name": r["name"].strip().title()}

def mask_ssn(r):
    ssn = r.get("ssn", "")
    masked = "XXX-XX-" + ssn[-4:] if len(ssn) >= 4 else None
    return {**r, "ssn": masked}

def add_full_name(r):
    return {**r, "full_name": f"{r['name']} ({r['id']})"}

# Build pipeline
transform = pipeline(clean_name, mask_ssn, add_full_name)

records = [
    {"id": 1, "name": "  alice ", "ssn": "123-45-6789"},
    {"id": 2, "name": "BOB", "ssn": "987-65-4321"},
]

result = transform(records)
# [{'id': 1, 'name': 'Alice', 'ssn': 'XXX-XX-6789', 'full_name': 'Alice (1)'}, ...]
```

---

## 14. Extract UUIDs from Mixed Text

**Scenario:** Find and validate UUIDs in log messages.

```python
import re

def extract_uuids(text_list):
    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    
    results = []
    for text in text_list:
        uuids = re.findall(uuid_pattern, text, re.IGNORECASE)
        if uuids:
            results.append({"text": text[:50], "uuids": uuids})
    return results

logs = [
    "Processing order abc12345-1234-5678-9abc-def012345678 for user",
    "No UUID here",
    "Transaction 11111111-2222-3333-4444-555555555555 completed with ref 66666666-7777-8888-9999-aaaaaaaaaaaa"
]

found = extract_uuids(logs)
# [{'text': 'Processing order...', 'uuids': ['abc12345-1234-5678-9abc-def012345678']}, ...]
```

---

## 15. Merge K Sorted Log Streams

**Scenario:** Merge multiple sorted log files by timestamp.

```python
import heapq

def merge_sorted_streams(streams, ts_extractor):
    """Merge K sorted streams using min-heap"""
    heap = []
    iterators = [iter(s) for s in streams]
    
    # Initialize heap
    for i, it in enumerate(iterators):
        item = next(it, None)
        if item:
            heapq.heappush(heap, (ts_extractor(item), i, item, it))
    
    while heap:
        ts, idx, item, it = heapq.heappop(heap)
        yield item
        next_item = next(it, None)
        if next_item:
            heapq.heappush(heap, (ts_extractor(next_item), idx, next_item, it))

# Usage
logs_server1 = [{"ts": "2026-02-08 10:00:00", "msg": "s1_a"}, {"ts": "2026-02-08 10:02:00", "msg": "s1_b"}]
logs_server2 = [{"ts": "2026-02-08 10:01:00", "msg": "s2_a"}, {"ts": "2026-02-08 10:03:00", "msg": "s2_b"}]

merged = list(merge_sorted_streams([logs_server1, logs_server2], lambda x: x["ts"]))
# Sorted by timestamp across all servers
```

---

## Key Patterns Cheatsheet

| Pattern | Python Idiom | Use Case |
|---------|--------------|----------|
| **PII Masking** | String slicing + `f-string` | GDPR compliance |
| **URL Parsing** | `urllib.parse` | Clickstream analysis |
| **Regex Extract** | `re.findall`, `re.match` | Log parsing |
| **Grouping** | `dict.setdefault()` | Aggregations |
| **Sorting** | `sorted(key=lambda x: -x[1])` | Top N |
| **Dedup** | Dict with key = unique field | Keep latest |
| **Flatten** | Recursive dict traversal | ETL prep |
| **Validation** | Multiple checks + error collector | Data quality |
| **Pipeline** | Function composition | Chained transforms |
| **K-way Merge** | `heapq` | Multi-source logs |

---

## Common Interview Tips

```python
# 1. Default dict pattern
from collections import defaultdict
groups = defaultdict(list)

# 2. Counter for frequencies
from collections import Counter
counts = Counter(items).most_common(10)

# 3. Dict comprehension with filter
filtered = {k: v for k, v in data.items() if v > 0}

# 4. Tuple unpacking in loops
for key, val in dictionary.items():
    process(key, val)

# 5. Walrus operator (Python 3.8+)
if (match := re.search(pattern, text)):
    use(match.group(1))

# 6. setdefault for nested dicts
nested.setdefault("level1", {}).setdefault("level2", []).append(val)
```
