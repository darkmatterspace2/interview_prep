# Python Interview Questions & Answers (Question Bank 1)

> **Amazon Data Engineer Style** - Data Engineering Focus with Performance Considerations

---

## 1️⃣ Data Structures & Logic

### Q26: Count occurrences from list of shipment events

```python
from collections import Counter

events = ['PICKED_UP', 'IN_TRANSIT', 'IN_TRANSIT', 'DELIVERED', 'PICKED_UP']

# Method 1: Counter (most Pythonic)
counts = Counter(events)
print(counts)  # Counter({'IN_TRANSIT': 2, 'PICKED_UP': 2, 'DELIVERED': 1})

# Method 2: Dictionary (manual)
counts = {}
for event in events:
    counts[event] = counts.get(event, 0) + 1

# Method 3: defaultdict
from collections import defaultdict
counts = defaultdict(int)
for event in events:
    counts[event] += 1
```

**Key Points:**
- `Counter` is O(n) and handles edge cases
- For large datasets, use `Counter` with generators to avoid loading all in memory

---

### Q27: Find duplicates in a list of dictionaries

```python
def find_duplicates(records, key_fields):
    """Find duplicate records based on specified key fields"""
    seen = set()
    duplicates = []
    
    for record in records:
        # Create hashable key from specified fields
        key = tuple(record.get(k) for k in key_fields)
        
        if key in seen:
            duplicates.append(record)
        else:
            seen.add(key)
    
    return duplicates

# Example
shipments = [
    {'id': 1, 'tracking': 'ABC123', 'status': 'DELIVERED'},
    {'id': 2, 'tracking': 'XYZ789', 'status': 'IN_TRANSIT'},
    {'id': 3, 'tracking': 'ABC123', 'status': 'DELIVERED'},  # Duplicate tracking
]

duplicates = find_duplicates(shipments, ['tracking'])
print(duplicates)  # [{'id': 3, 'tracking': 'ABC123', 'status': 'DELIVERED'}]
```

---

### Q28: Group shipments by region

```python
from collections import defaultdict
from itertools import groupby

shipments = [
    {'id': 1, 'region': 'WEST', 'value': 100},
    {'id': 2, 'region': 'EAST', 'value': 200},
    {'id': 3, 'region': 'WEST', 'value': 150},
]

# Method 1: defaultdict (preferred for unsorted data)
by_region = defaultdict(list)
for s in shipments:
    by_region[s['region']].append(s)

# Method 2: itertools.groupby (requires sorted data!)
shipments_sorted = sorted(shipments, key=lambda x: x['region'])
for region, group in groupby(shipments_sorted, key=lambda x: x['region']):
    print(f"{region}: {list(group)}")

# Method 3: Dictionary comprehension
regions = set(s['region'] for s in shipments)
by_region = {r: [s for s in shipments if s['region'] == r] for r in regions}
# Note: Inefficient O(n*k) - avoid for large datasets
```

---

### Q29: Sort events by timestamp

```python
from datetime import datetime

events = [
    {'id': 1, 'timestamp': '2024-02-07T10:30:00'},
    {'id': 2, 'timestamp': '2024-02-07T08:15:00'},
    {'id': 3, 'timestamp': '2024-02-07T09:00:00'},
]

# Method 1: sorted with key
sorted_events = sorted(events, key=lambda x: x['timestamp'])

# Method 2: Parse to datetime for proper comparison
sorted_events = sorted(
    events, 
    key=lambda x: datetime.fromisoformat(x['timestamp'])
)

# Method 3: In-place sort (modifies original list)
events.sort(key=lambda x: x['timestamp'])

# Method 4: Using operator.itemgetter (faster for simple keys)
from operator import itemgetter
sorted_events = sorted(events, key=itemgetter('timestamp'))
```

**Key Points:**
- ISO format strings sort correctly lexicographically
- Parse to datetime if format varies or includes timezone

---

### Q30: Merge two shipment datasets

```python
def merge_datasets(primary, secondary, key='id', strategy='override'):
    """
    Merge two lists of dictionaries.
    strategy: 'override' (secondary wins), 'preserve' (primary wins), 'merge' (combine)
    """
    # Index secondary by key
    secondary_index = {r[key]: r for r in secondary}
    
    result = []
    seen_keys = set()
    
    for record in primary:
        rec_key = record[key]
        seen_keys.add(rec_key)
        
        if rec_key in secondary_index:
            if strategy == 'override':
                result.append({**record, **secondary_index[rec_key]})
            elif strategy == 'preserve':
                result.append({**secondary_index[rec_key], **record})
            else:  # merge
                merged = {**record}
                for k, v in secondary_index[rec_key].items():
                    if k not in merged or merged[k] is None:
                        merged[k] = v
                result.append(merged)
        else:
            result.append(record)
    
    # Add records only in secondary
    for rec_key, record in secondary_index.items():
        if rec_key not in seen_keys:
            result.append(record)
    
    return result
```

---

## 2️⃣ String / JSON Processing

### Q31: Parse nested JSON shipment events

```python
import json

json_data = '''
{
    "shipment_id": "SHIP001",
    "events": [
        {"status": "PICKED_UP", "location": {"city": "Seattle", "state": "WA"}},
        {"status": "IN_TRANSIT", "location": {"city": "Portland", "state": "OR"}}
    ]
}
'''

# Parse JSON
data = json.loads(json_data)

# Access nested fields safely
def safe_get(d, *keys, default=None):
    """Safely navigate nested dictionary"""
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key, default)
        elif isinstance(d, list) and isinstance(key, int) and key < len(d):
            d = d[key]
        else:
            return default
    return d

# Example usage
city = safe_get(data, 'events', 0, 'location', 'city')  # 'Seattle'
missing = safe_get(data, 'events', 5, 'location', 'city', default='N/A')  # 'N/A'
```

---

### Q32: Flatten JSON into tabular format

```python
def flatten_json(nested_json, prefix=''):
    """Recursively flatten nested JSON into flat dictionary"""
    flat = {}
    
    for key, value in nested_json.items():
        new_key = f"{prefix}_{key}" if prefix else key
        
        if isinstance(value, dict):
            flat.update(flatten_json(value, new_key))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    flat.update(flatten_json(item, f"{new_key}_{i}"))
                else:
                    flat[f"{new_key}_{i}"] = item
        else:
            flat[new_key] = value
    
    return flat

# Example
nested = {
    'id': 1,
    'address': {'city': 'Seattle', 'zip': '98101'},
    'items': [{'sku': 'A1'}, {'sku': 'B2'}]
}
flat = flatten_json(nested)
# {'id': 1, 'address_city': 'Seattle', 'address_zip': '98101', 
#  'items_0_sku': 'A1', 'items_1_sku': 'B2'}

# For Spark/Pandas
import pandas as pd
df = pd.json_normalize(nested, sep='_')
```

---

### Q33: Handle malformed JSON records safely

```python
import json
import logging

def safe_parse_json(json_string, default=None):
    """Parse JSON with error handling"""
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        logging.warning(f"Malformed JSON: {e.msg} at position {e.pos}")
        return default
    except TypeError as e:
        logging.warning(f"Invalid input type: {type(json_string)}")
        return default

def process_json_lines(file_path):
    """Process file with one JSON per line, skipping bad records"""
    valid_records = []
    bad_records = []
    
    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            record = safe_parse_json(line.strip())
            if record is not None:
                valid_records.append(record)
            else:
                bad_records.append({'line': line_num, 'content': line[:100]})
    
    logging.info(f"Processed {len(valid_records)} valid, {len(bad_records)} bad")
    return valid_records, bad_records
```

---

### Q34: Extract fields from semi-structured logs

```python
import re
from datetime import datetime

# Sample log line
log_line = '2024-02-07 10:30:45 INFO shipment_id=SHIP001 status=DELIVERED carrier="FedEx Ground"'

def parse_log_line(line):
    """Extract structured fields from log line"""
    # Extract timestamp
    timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
    timestamp = datetime.fromisoformat(timestamp_match.group(1)) if timestamp_match else None
    
    # Extract level
    level_match = re.search(r'\b(DEBUG|INFO|WARNING|ERROR|CRITICAL)\b', line)
    level = level_match.group(1) if level_match else 'UNKNOWN'
    
    # Extract key=value pairs (handling quoted values)
    pattern = r'(\w+)=(?:"([^"]+)"|(\S+))'
    fields = {m.group(1): m.group(2) or m.group(3) for m in re.finditer(pattern, line)}
    
    return {
        'timestamp': timestamp,
        'level': level,
        **fields
    }

result = parse_log_line(log_line)
# {'timestamp': datetime(...), 'level': 'INFO', 
#  'shipment_id': 'SHIP001', 'status': 'DELIVERED', 'carrier': 'FedEx Ground'}
```

---

### Q35: Normalize inconsistent status values

```python
def normalize_status(raw_status):
    """Normalize status values to standard format"""
    if not raw_status:
        return 'UNKNOWN'
    
    # Standardize to uppercase, strip whitespace
    status = raw_status.upper().strip()
    
    # Mapping of variations to canonical values
    STATUS_MAP = {
        # Delivered variations
        'DELIVERED': 'DELIVERED',
        'DLVD': 'DELIVERED',
        'COMPLETE': 'DELIVERED',
        'COMPLETED': 'DELIVERED',
        
        # In Transit variations
        'IN_TRANSIT': 'IN_TRANSIT',
        'IN TRANSIT': 'IN_TRANSIT',
        'INTRANSIT': 'IN_TRANSIT',
        'TRANSIT': 'IN_TRANSIT',
        
        # Picked Up variations
        'PICKED_UP': 'PICKED_UP',
        'PICKED UP': 'PICKED_UP',
        'PICKUP': 'PICKED_UP',
    }
    
    # Try direct match
    if status in STATUS_MAP:
        return STATUS_MAP[status]
    
    # Try fuzzy match (contains key words)
    if 'DELIVER' in status:
        return 'DELIVERED'
    if 'TRANSIT' in status:
        return 'IN_TRANSIT'
    if 'PICK' in status:
        return 'PICKED_UP'
    
    return 'UNKNOWN'
```

---

## 3️⃣ Performance & Memory

### Q36: Process a large file line by line

```python
def process_large_file(file_path, process_func, chunk_size=10000):
    """Process large file efficiently without loading into memory"""
    processed = 0
    errors = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        batch = []
        for line in f:  # Iterates line by line, not loading entire file
            try:
                batch.append(process_func(line))
            except Exception as e:
                errors += 1
                continue
            
            if len(batch) >= chunk_size:
                yield batch  # Yield batch for processing
                processed += len(batch)
                batch = []
        
        if batch:  # Remaining records
            yield batch
            processed += len(batch)
    
    print(f"Processed: {processed}, Errors: {errors}")

# Usage with generator
for batch in process_large_file('huge_file.csv', parse_line):
    save_to_database(batch)  # Process in chunks
```

---

### Q37: Optimize loop vs dictionary lookup

```python
import time

# Scenario: Check if shipments exist in a list of valid IDs

valid_ids_list = list(range(100000))  # List of 100K IDs
valid_ids_set = set(valid_ids_list)   # Set for O(1) lookup
shipments = [{'id': i} for i in range(50000)]

# ❌ BAD: O(n*m) - List lookup is O(n)
def check_list(shipments, valid_ids):
    return [s for s in shipments if s['id'] in valid_ids]

# ✅ GOOD: O(n) - Set lookup is O(1)
def check_set(shipments, valid_ids):
    return [s for s in shipments if s['id'] in valid_ids]

# Benchmark
start = time.time()
result = check_list(shipments, valid_ids_list)  # ~10 seconds
print(f"List: {time.time() - start:.2f}s")

start = time.time()
result = check_set(shipments, valid_ids_set)    # ~0.01 seconds
print(f"Set: {time.time() - start:.2f}s")
```

**Key Points:**
- **List:** O(n) lookup → O(n*m) for n checks in list of m
- **Set/Dict:** O(1) average lookup → O(n) for n checks
- Always convert to set for membership testing

---

### Q38: Streaming vs batch processing logic

```python
# BATCH: Load all data, process, write all results
def batch_process(input_file, output_file):
    """Load entire dataset into memory"""
    with open(input_file) as f:
        data = f.readlines()  # All in memory!
    
    processed = [transform(line) for line in data]
    
    with open(output_file, 'w') as f:
        f.writelines(processed)

# STREAMING: Process one record at a time
def streaming_process(input_file, output_file):
    """Process without loading entire dataset"""
    with open(input_file) as fin, open(output_file, 'w') as fout:
        for line in fin:  # One line at a time
            result = transform(line)
            fout.write(result)

# STREAMING with batching (hybrid - best of both)
def stream_batch_process(input_file, output_file, batch_size=1000):
    """Stream input, batch writes for efficiency"""
    with open(input_file) as fin, open(output_file, 'w') as fout:
        batch = []
        for line in fin:
            batch.append(transform(line))
            
            if len(batch) >= batch_size:
                fout.writelines(batch)
                batch = []
        
        if batch:  # Flush remaining
            fout.writelines(batch)
```

**When to Use:**
| Approach | Memory | Speed | Use Case |
|----------|--------|-------|----------|
| Batch | High (all in RAM) | Fast (vectorized) | Small-medium datasets |
| Streaming | Low (constant) | Slower | Large datasets, infinite streams |
| Hybrid | Medium (batch size) | Good balance | Large datasets needing efficiency |

---

### Q39: Generator vs list — when and why?

```python
# LIST: Stores all values in memory
def get_shipments_list(n):
    return [create_shipment(i) for i in range(n)]

# GENERATOR: Yields values one at a time
def get_shipments_generator(n):
    for i in range(n):
        yield create_shipment(i)

# Memory comparison
import sys

list_result = get_shipments_list(1000000)
print(f"List size: {sys.getsizeof(list_result) / 1024 / 1024:.2f} MB")  # ~40 MB

gen_result = get_shipments_generator(1000000)
print(f"Generator size: {sys.getsizeof(gen_result):.2f} bytes")  # ~100 bytes

# Generator use cases
# 1. Processing large files
def read_chunks(file_path, chunk_size=1024):
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            yield chunk

# 2. Chaining transformations (lazy evaluation)
data = (transform(x) for x in raw_data)
filtered = (x for x in data if x['valid'])
result = list(filtered)  # Only evaluates when consumed
```

**Key Points:**
- **List:** Need random access, iterate multiple times, small data
- **Generator:** Large data, single iteration, memory-constrained

---

### Q40: Handling millions of records safely

```python
import gc
from itertools import islice

def process_millions(data_source, process_func, chunk_size=50000):
    """
    Process millions of records with memory management
    """
    total_processed = 0
    
    while True:
        # Get chunk
        chunk = list(islice(data_source, chunk_size))
        if not chunk:
            break
        
        # Process chunk
        results = [process_func(record) for record in chunk]
        
        # Write results (don't accumulate in memory)
        write_to_sink(results)
        
        total_processed += len(chunk)
        
        # Explicit garbage collection for large objects
        del chunk, results
        gc.collect()
        
        if total_processed % 500000 == 0:
            print(f"Processed {total_processed:,} records")
    
    return total_processed

# With multiprocessing for CPU-bound tasks
from multiprocessing import Pool

def parallel_process(records, process_func, workers=4):
    with Pool(workers) as pool:
        results = pool.map(process_func, records, chunksize=1000)
    return results
```

---

## 4️⃣ Error Handling

### Q41: Skip bad records but continue processing

```python
def process_with_skip(records, process_func):
    """Process records, skip failures, track errors"""
    results = []
    errors = []
    
    for i, record in enumerate(records):
        try:
            result = process_func(record)
            results.append(result)
        except Exception as e:
            errors.append({
                'index': i,
                'record': record,
                'error': str(e),
                'error_type': type(e).__name__
            })
            continue  # Skip and continue
    
    return results, errors

# Usage
results, errors = process_with_skip(shipments, transform_shipment)
print(f"Success: {len(results)}, Failed: {len(errors)}")

# Write errors to DLQ (Dead Letter Queue)
save_to_dlq(errors)
```

---

### Q42: Log failures with minimal performance hit

```python
import logging
from queue import Queue
from threading import Thread

# Async logging to avoid blocking main thread
class AsyncLogger:
    def __init__(self, log_file):
        self.queue = Queue()
        self.log_file = log_file
        self._start_worker()
    
    def _start_worker(self):
        def worker():
            with open(self.log_file, 'a') as f:
                while True:
                    message = self.queue.get()
                    if message is None:
                        break
                    f.write(message + '\n')
                    self.queue.task_done()
        
        self.thread = Thread(target=worker, daemon=True)
        self.thread.start()
    
    def log(self, message):
        self.queue.put(message)
    
    def close(self):
        self.queue.put(None)
        self.thread.join()

# Usage
logger = AsyncLogger('/tmp/errors.log')

for record in records:
    try:
        process(record)
    except Exception as e:
        logger.log(f"ERROR: {record['id']} - {e}")  # Non-blocking
```

---

### Q43: Retry logic for failed transformations

```python
import time
from functools import wraps

def retry(max_attempts=3, backoff_factor=2, exceptions=(Exception,)):
    """Decorator for retry with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    wait_time = backoff_factor ** attempt
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
            
            raise last_exception
        return wrapper
    return decorator

# Usage
@retry(max_attempts=3, backoff_factor=2, exceptions=(ConnectionError, TimeoutError))
def fetch_data(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()

# Or using tenacity library (production-ready)
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
def fetch_data_tenacity(url):
    return requests.get(url, timeout=10).json()
```

---

### Q44: Validate schema before processing

```python
from typing import Dict, Any
import jsonschema

# Define expected schema
SHIPMENT_SCHEMA = {
    "type": "object",
    "required": ["id", "status", "timestamp"],
    "properties": {
        "id": {"type": "string"},
        "status": {"type": "string", "enum": ["PENDING", "IN_TRANSIT", "DELIVERED"]},
        "timestamp": {"type": "string", "format": "date-time"},
        "carrier": {"type": "string"},
        "weight": {"type": "number", "minimum": 0}
    }
}

def validate_record(record: Dict[str, Any], schema: dict) -> tuple:
    """Validate record against schema, return (is_valid, errors)"""
    try:
        jsonschema.validate(record, schema)
        return True, None
    except jsonschema.ValidationError as e:
        return False, str(e.message)

# Simple validation without library
def validate_shipment(record: Dict[str, Any]) -> list:
    """Manual validation with specific rules"""
    errors = []
    
    # Required fields
    for field in ['id', 'status', 'timestamp']:
        if field not in record or record[field] is None:
            errors.append(f"Missing required field: {field}")
    
    # Type checks
    if 'weight' in record and not isinstance(record['weight'], (int, float)):
        errors.append(f"Invalid type for weight: expected number")
    
    # Value constraints
    if record.get('status') not in ['PENDING', 'IN_TRANSIT', 'DELIVERED']:
        errors.append(f"Invalid status: {record.get('status')}")
    
    return errors
```

---

### Q45: Detect nulls and unexpected values

```python
def analyze_data_quality(records: list, schema: dict) -> dict:
    """Analyze dataset for nulls and unexpected values"""
    stats = {field: {'null_count': 0, 'unexpected': []} for field in schema}
    total = len(records)
    
    for record in records:
        for field, rules in schema.items():
            value = record.get(field)
            
            # Check nulls
            if value is None or value == '':
                stats[field]['null_count'] += 1
                continue
            
            # Check type
            expected_type = rules.get('type')
            if expected_type == 'number' and not isinstance(value, (int, float)):
                stats[field]['unexpected'].append(value)
            
            # Check allowed values
            allowed = rules.get('allowed')
            if allowed and value not in allowed:
                stats[field]['unexpected'].append(value)
            
            # Check range
            if 'min' in rules and value < rules['min']:
                stats[field]['unexpected'].append(value)
    
    # Calculate rates
    for field in stats:
        stats[field]['null_rate'] = stats[field]['null_count'] / total if total > 0 else 0
        stats[field]['unexpected'] = list(set(stats[field]['unexpected']))[:10]  # Sample
    
    return stats

# Example schema
schema = {
    'id': {'type': 'string'},
    'status': {'type': 'string', 'allowed': ['PENDING', 'DELIVERED']},
    'weight': {'type': 'number', 'min': 0}
}
```

---

## 5️⃣ Part 2: Algorithm Questions

### IP Address Counter (Top 10)

```python
from collections import Counter
import heapq

def top_10_ips(log_file):
    """Count IP occurrences and return top 10"""
    ip_counts = Counter()
    
    with open(log_file, 'r') as f:
        for line in f:
            # Extract IP (assuming first field)
            ip = line.split()[0]
            ip_counts[ip] += 1
    
    return ip_counts.most_common(10)

# For very large files (can't fit in memory)
def top_10_ips_streaming(log_file, num_partitions=10):
    """Partition by IP hash, count per partition, merge"""
    from collections import defaultdict
    import hashlib
    
    # Partition counts
    partitions = [Counter() for _ in range(num_partitions)]
    
    with open(log_file, 'r') as f:
        for line in f:
            ip = line.split()[0]
            partition = int(hashlib.md5(ip.encode()).hexdigest(), 16) % num_partitions
            partitions[partition][ip] += 1
    
    # Merge and get top 10
    merged = Counter()
    for p in partitions:
        merged.update(p)
    
    return merged.most_common(10)
```

---

### Balanced Parentheses Validator

```python
def is_balanced(s: str) -> bool:
    """Check if parentheses are balanced using stack"""
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    
    for char in s:
        if char in '([{':
            stack.append(char)
        elif char in ')]}':
            if not stack or stack[-1] != pairs[char]:
                return False
            stack.pop()
    
    return len(stack) == 0

# Test cases
assert is_balanced("()[]{}") == True
assert is_balanced("([{}])") == True
assert is_balanced("([)]") == False
assert is_balanced("((())") == False
```

---

### Reconstruct Path from Route Pairs

```python
def reconstruct_path(routes: list) -> list:
    """
    Given route pairs [('A', 'B'), ('B', 'C'), ('C', 'D')],
    reconstruct full path A -> B -> C -> D
    """
    if not routes:
        return []
    
    # Build graph
    graph = {src: dst for src, dst in routes}
    all_dests = set(graph.values())
    all_sources = set(graph.keys())
    
    # Find start (source that's not a destination)
    start = (all_sources - all_dests).pop()
    
    # Build path
    path = [start]
    current = start
    
    while current in graph:
        current = graph[current]
        path.append(current)
    
    return path

# Test
routes = [('A', 'B'), ('B', 'C'), ('C', 'D')]
print(reconstruct_path(routes))  # ['A', 'B', 'C', 'D']

# With cycle detection
def reconstruct_path_safe(routes):
    graph = {src: dst for src, dst in routes}
    all_dests = set(graph.values())
    all_sources = set(graph.keys())
    
    starts = all_sources - all_dests
    if not starts:
        return []  # Cycle exists
    
    start = starts.pop()
    path = [start]
    visited = {start}
    current = start
    
    while current in graph:
        current = graph[current]
        if current in visited:
            return path + [f"CYCLE at {current}"]
        visited.add(current)
        path.append(current)
    
    return path
```
