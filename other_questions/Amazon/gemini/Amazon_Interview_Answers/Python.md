# Amazon Python Interview Questions & Answers

## Part 1: Python (Data Engineering Focus)

### Data Structures & Logic

#### 26. Count occurrences from list of shipment events.
**Question:** Given a list of event statuses, count how many times each occurs.
**Answer:**
```python
from collections import Counter

events = ['DELIVERED', 'SHIPPED', 'DELIVERED', 'PENDING']
counts = Counter(events)
print(counts)
# Output: Counter({'DELIVERED': 2, 'SHIPPED': 1, 'PENDING': 1})
```

#### 27. Find duplicates in a list of dictionaries.
**Question:** Identify shipments appearing more than once based on `id`.
**Answer:**
```python
data = [{'id': 1, 'val': 'a'}, {'id': 2, 'val': 'b'}, {'id': 1, 'val': 'c'}]
seen = set()
duplicates = []

for item in data:
    if item['id'] in seen:
        duplicates.append(item)
    else:
        seen.add(item['id'])
print(duplicates)
```

#### 28. Group shipments by region.
**Question:** Create a dictionary where keys are regions and values are lists of shipments.
**Answer:**
```python
from collections import defaultdict

shipments = [
    {'id': 1, 'region': 'US-East'},
    {'id': 2, 'region': 'EU-West'},
    {'id': 3, 'region': 'US-East'}
]

grouped = defaultdict(list)
for s in shipments:
    grouped[s['region']].append(s)

print(dict(grouped))
```

#### 29. Sort events by timestamp.
**Question:** Sort a list of event dictionaries by their 'time' key.
**Answer:**
```python
events = [
    {'event': 'B', 'time': '2023-01-02'},
    {'event': 'A', 'time': '2023-01-01'}
]
# In-place sort
events.sort(key=lambda x: x['time'])
print(events)
```

#### 30. Merge two shipment datasets.
**Question:** Merge two lists of dictionaries based on a common key (like SQL JOIN).
**Answer:**
```python
# Assuming list of dicts. Typically pandas is better, but pure python:
list_a = [{'id': 1, 'status': 'sent'}, {'id': 2, 'status': 'pending'}]
list_b = [{'id': 1, 'cost': 100}, {'id': 2, 'cost': 200}]

# Optimize lookup
lookup_b = {x['id']: x for x in list_b}

merged = []
for item in list_a:
    val_b = lookup_b.get(item['id'], {})
    merged.append({**item, **val_b})
print(merged)
```

---

### String / JSON Processing

#### 31. Parse nested JSON shipment events.
**Answer:**
```python
import json
json_str = '{"shipment": {"id": 123, "details": {"weight": 10}}}'
data = json.loads(json_str)
weight = data['shipment']['details']['weight']
```

#### 32. Flatten JSON into tabular format.
**Answer:**
```python
import pandas as pd
# pandas.json_normalize is the standard tool
data = [{'id': 1, 'logs': {'a': 1}}]
df = pd.json_normalize(data)
# resulting columns: id, logs.a
```

#### 33. Handle malformed JSON records safely.
**Answer:**
```python
lines = ['{"a": 1}', 'broken_json', '{"b": 2}']
valid_records = []
for line in lines:
    try:
        valid_records.append(json.loads(line))
    except json.JSONDecodeError:
        print(f"Skipping bad record: {line}")
```

#### 34. Extract fields from semi-structured logs.
**Answer:**
```python
import re
log = "INFO 2023-01-01 User:123 logged_in"
match = re.search(r'User:(\d+)', log)
if match:
    user_id = match.group(1)
```

#### 35. Normalize inconsistent status values.
**Answer:**
```python
status = " Delivered "
normalized = status.strip().upper()
# Result: "DELIVERED"
```

---

### Performance & Memory

#### 36. Process a large file line by line.
**Question:** Usage of generators/streaming to avoid OOM.
**Answer:**
```python
def process_file(filepath):
    with open(filepath, 'r') as f:
        for line in f:
            yield process(line)
            
# Don't use f.readlines() on big files!
```

#### 37. Optimize loop vs dictionary lookup.
**Answer:**
*   **Loop:** O(N) search.
*   **Dict:** O(1) avg search.
*   *Always* convert a list to a set or dict if you need to search against it repeatedly (e.g., filtering logic).

#### 38. Streaming vs batch processing logic.
**Answer:**
*   **Batch:** Read all -> Process -> Write. High latency, high throughput.
*   **Streaming:** Read one/chunk -> Process -> Write immediately. Low latency.
*   In Python, generators facilitate streaming logic.

#### 39. Generator vs list — when and why?
**Answer:**
*   **List:** Stores everything in memory. Fast random access. Good for small data.
*   **Generator:** Yields one item at a time. Low memory footprint. Good for infinite streams or large files.

#### 40. Handling millions of records safely.
**Answer:**
Use chunking (e.g., `pandas.read_csv(chunksize=10000)`), generators, or distributed frameworks like Spark. In pure Python, avoid loading the full dataset into RAM.

---

### Error Handling

#### 41. Skip bad records but continue processing.
*(See Q33)* - Use `try-except` blocks inside the loop.

#### 42. Log failures with minimal performance hit.
**Answer:**
Buffered logging or async logging. Don't write to disk/DB on *every* error synchronously. Use Python's `logging` module properly (not `print`).

#### 43. Retry logic for failed transformations.
**Answer:**
```python
import time

def robust_call(func, retries=3):
    for i in range(retries):
        try:
            return func()
        except Exception as e:
            time.sleep(2 ** i) # Exponential backoff
    raise Exception("Failed after retries")
```

#### 44. Validate schema before processing.
**Answer:**
Use libraries like `pydantic` or `jsonschema` to assert types and required fields before passing data to downstream logic.

#### 45. Detect nulls and unexpected values.
**Answer:**
```python
if data.get('field') is None:
    raise ValueError("Missing field")
```

---

## Part 2: Amazon Coding Scenarios

#### 1. Strings/Arrays: Count IP addresses
**Question:** Given a log file with millions of entries, count occurrence of every IP and return top 10.
**Answer:**
```python
from collections import Counter
import re

def top_ips(logfile):
    ip_pattern = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
    counts = Counter()
    
    with open(logfile, 'r') as f:
        for line in f:
            match = ip_pattern.search(line)
            if match:
                counts[match.group()] += 1
                
    return counts.most_common(10)
```
*Key:* Use `Counter` for easy counting and `.most_common()`. Read line-by-line for memory efficiency.

#### 2. Data Structures: Balanced Parentheses
**Question:** Validate if `()[]{}` string is valid.
**Answer:**
```python
def is_valid(s):
    stack = []
    mapping = {")": "(", "}": "{", "]": "["}
    
    for char in s:
        if char in mapping:
            # Closing bracket
            top_element = stack.pop() if stack else '#'
            if mapping[char] != top_element:
                return False
        else:
            # Opening bracket
            stack.append(char)
            
    return not stack
```

#### 3. Dictionary Manipulation: Reconstruct Path
**Question:** Given `[('A', 'B'), ('B', 'C'), ('C', 'D')]`, reconstruct `A -> B -> C -> D`.
**Answer:**
```python
def reconstruct_path(routes):
    # routes is a list of tuples: [('A', 'B'), ...]
    graph = dict(routes)
    
    # 1. Find Start Node (node that is a key but never a value)
    destinations = set(graph.values())
    start_node = None
    for k in graph:
        if k not in destinations:
            start_node = k
            break
            
    # 2. Traverse
    path = []
    curr = start_node
    while curr:
        path.append(curr)
        curr = graph.get(curr)
        
    return path
```
