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

---

# Question Bank 5: Dictionaries, Sets & Data Aggregation

> **Amazon Data Engineer Style** - Focus on Hash Maps, Sets, and String Parsing

---

## Part 1: Must-Master Basics (Dictionaries & Sets)

### Q1: Word Frequency Counter

> Given a long string (like a paragraph), write a function to count how many times each word appears.
> **Goal:** Use a dictionary where key = word and value = count.
> **Bonus:** Ignore punctuation and case.

```python
import re
from collections import Counter

def word_frequency(text: str) -> dict:
    """
    Count word frequencies, ignoring punctuation and case.
    
    Time: O(n) where n = characters in text
    Space: O(w) where w = unique words
    """
    # Method 1: Manual with dictionary
    # Remove punctuation and convert to lowercase
    cleaned = re.sub(r'[^\w\s]', '', text.lower())
    words = cleaned.split()
    
    freq = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1
    
    return freq

def word_frequency_counter(text: str) -> dict:
    """Same task using Counter (more Pythonic)"""
    cleaned = re.sub(r'[^\w\s]', '', text.lower())
    return dict(Counter(cleaned.split()))

# Test
text = """
Amazon delivers millions of packages daily. Amazon's logistics network
is vast. Packages are delivered by Amazon and third-party carriers.
"""
result = word_frequency(text)
print(result)
# {'amazon': 2, 'delivers': 1, 'millions': 1, 'of': 1, 'packages': 2, 
#  'daily': 1, 'amazons': 1, 'logistics': 1, 'network': 1, 'is': 1, 
#  'vast': 1, 'are': 1, 'delivered': 1, 'by': 1, 'and': 1, 
#  'thirdparty': 1, 'carriers': 1}

# Advanced: Get top N most frequent words
from collections import Counter

def top_n_words(text: str, n: int) -> list:
    """Return top N most frequent words"""
    cleaned = re.sub(r'[^\w\s]', '', text.lower())
    counter = Counter(cleaned.split())
    return counter.most_common(n)

print(top_n_words(text, 3))
# [('amazon', 2), ('packages', 2), ('delivers', 1)]
```

**Key Points:**
- `dict.get(key, default)` returns default if key doesn't exist
- `Counter` is optimized for counting and provides `most_common(n)`
- Regex `[^\w\s]` matches any character that's NOT a word char or whitespace
- Always normalize case before comparing text

---

### Q2: Find Duplicates in a List

> Given a list of integers `[1, 2, 3, 2, 4, 5, 5]`, return a list of only the duplicate elements.
> **Goal:** Use a set to track what you've seen.

```python
def find_duplicates(nums: list) -> list:
    """
    Find all duplicate values in a list.
    
    Time: O(n)
    Space: O(n)
    """
    seen = set()
    duplicates = set()  # Use set to avoid duplicate duplicates
    
    for num in nums:
        if num in seen:
            duplicates.add(num)
        else:
            seen.add(num)
    
    return list(duplicates)

# Test
nums = [1, 2, 3, 2, 4, 5, 5]
print(find_duplicates(nums))  # [2, 5]

# Alternative: Using Counter
from collections import Counter

def find_duplicates_v2(nums: list) -> list:
    """Find duplicates using Counter"""
    counts = Counter(nums)
    return [num for num, count in counts.items() if count > 1]

print(find_duplicates_v2(nums))  # [2, 5]

# Alternative: One-liner (less efficient but clever)
def find_duplicates_v3(nums: list) -> list:
    """Find duplicates - elements that appear more than once"""
    return list(set(x for x in nums if nums.count(x) > 1))
    # WARNING: O(n²) - don't use for large lists!
```

**Key Points:**
- `set` provides O(1) lookup for `in` operator
- Use two sets: one for "seen", one for "duplicates"
- Using `set` for duplicates automatically handles duplicates of duplicates
- Avoid `list.count()` in loops — it's O(n) per call!

**Interview Variation: Find elements that appear exactly K times**

```python
def find_k_occurrences(nums: list, k: int) -> list:
    """Find all elements that appear exactly k times"""
    counts = Counter(nums)
    return [num for num, count in counts.items() if count == k]

print(find_k_occurrences([1, 2, 2, 3, 3, 3], 2))  # [2]
print(find_k_occurrences([1, 2, 2, 3, 3, 3], 3))  # [3]
```

---

### Q3: Group Anagrams (Classic DE Interview Question)

> Given a list of strings `["eat", "tea", "tan", "ate", "nat", "bat"]`, group them together.
> **Output:** `[["bat"], ["nat", "tan"], ["ate", "eat", "tea"]]`

```python
from collections import defaultdict

def group_anagrams(strs: list) -> list:
    """
    Group words that are anagrams of each other.
    
    Key insight: Anagrams have the same sorted characters.
    
    Time: O(n * k log k) where n = strings, k = max string length
    Space: O(n * k) for storing results
    """
    # Dictionary: sorted_word -> list of original words
    anagram_map = defaultdict(list)
    
    for word in strs:
        # Sort the word to create a unique key for anagrams
        key = ''.join(sorted(word))  # "eat" -> "aet", "tea" -> "aet"
        anagram_map[key].append(word)
    
    return list(anagram_map.values())

# Test
words = ["eat", "tea", "tan", "ate", "nat", "bat"]
print(group_anagrams(words))
# [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]

# Alternative: Using tuple as key (slightly more efficient)
def group_anagrams_v2(strs: list) -> list:
    """Use tuple of sorted chars as key (hashable)"""
    anagram_map = defaultdict(list)
    
    for word in strs:
        key = tuple(sorted(word))  # ('a', 'e', 't')
        anagram_map[key].append(word)
    
    return list(anagram_map.values())

# Alternative: Character count as key (O(n * k) time)
def group_anagrams_v3(strs: list) -> list:
    """Use character frequency as key (faster for long strings)"""
    anagram_map = defaultdict(list)
    
    for word in strs:
        # Count of each letter (26 letters)
        count = [0] * 26
        for char in word:
            count[ord(char) - ord('a')] += 1
        key = tuple(count)
        anagram_map[key].append(word)
    
    return list(anagram_map.values())
```

**Key Points:**
- **Why this question matters:** Tests understanding of:
  - Hash maps with custom keys
  - Sorting as a grouping mechanism
  - Converting to hashable types (tuple vs list)
- `defaultdict(list)` auto-creates empty list for new keys
- Using `tuple(sorted(word))` is hashable; `list` is NOT hashable

**Interview Follow-up: Handle case-insensitivity and spaces**

```python
def group_anagrams_advanced(phrases: list) -> list:
    """Handle phrases with spaces and mixed case"""
    anagram_map = defaultdict(list)
    
    for phrase in phrases:
        # Normalize: lowercase, remove spaces, sort
        normalized = ''.join(sorted(phrase.lower().replace(' ', '')))
        anagram_map[normalized].append(phrase)
    
    return list(anagram_map.values())

print(group_anagrams_advanced(["Listen", "Silent", "inlets"]))
# [['Listen', 'Silent', 'inlets']]
```

---

## Part 2: String Manipulation & Log Parsing

### Q4: Log Error Extraction

> **Input:** A list of log strings: `["INFO: User logged in", "ERROR: DB connection failed", "INFO: User clicked"]`
> **Task:** Return a dictionary counting how many times each log level (INFO, ERROR, WARN) appears.

```python
def count_log_levels(logs: list) -> dict:
    """
    Count occurrences of each log level.
    
    Time: O(n) where n = number of log entries
    Space: O(1) - fixed number of log levels
    """
    counts = {'INFO': 0, 'ERROR': 0, 'WARN': 0, 'DEBUG': 0}
    
    for log in logs:
        # Extract log level (first word before colon)
        level = log.split(':')[0].strip()
        if level in counts:
            counts[level] += 1
    
    return counts

# Test
logs = [
    "INFO: User logged in",
    "ERROR: DB connection failed",
    "INFO: User clicked",
    "WARN: Memory usage high",
    "ERROR: Connection timeout"
]
print(count_log_levels(logs))
# {'INFO': 2, 'ERROR': 2, 'WARN': 1, 'DEBUG': 0}

# Advanced: Also extract error messages
def parse_logs_detailed(logs: list) -> dict:
    """Parse logs with full details"""
    from collections import defaultdict
    
    result = defaultdict(list)
    
    for log in logs:
        parts = log.split(':', 1)  # Split only on first colon
        if len(parts) >= 2:
            level = parts[0].strip()
            message = parts[1].strip()
            result[level].append(message)
    
    return dict(result)

print(parse_logs_detailed(logs))
# {'INFO': ['User logged in', 'User clicked'], 
#  'ERROR': ['DB connection failed', 'Connection timeout'], 
#  'WARN': ['Memory usage high']}

# Real-world: Parse structured logs with timestamp
import re
from datetime import datetime

def parse_structured_log(log: str) -> dict:
    """Parse log with format: [TIMESTAMP] LEVEL: MESSAGE"""
    pattern = r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] (\w+): (.+)'
    match = re.match(pattern, log)
    
    if match:
        timestamp_str, level, message = match.groups()
        return {
            'timestamp': datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S'),
            'level': level,
            'message': message
        }
    return None

log = "[2024-01-15 10:30:45] ERROR: Database connection failed"
print(parse_structured_log(log))
# {'timestamp': datetime(2024, 1, 15, 10, 30, 45), 
#  'level': 'ERROR', 'message': 'Database connection failed'}
```

**Key Points:**
- `str.split(':')` splits on colon; `split(':', 1)` limits to first split
- Use `defaultdict(list)` for grouping messages
- Regex is powerful for structured log parsing
- Always handle edge cases (malformed logs, missing colons)

**Interview Variation: Filter logs by time range**

```python
def filter_logs_by_time(logs: list, start_time: str, end_time: str) -> list:
    """Filter logs within a time range"""
    start = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    
    filtered = []
    for log in logs:
        parsed = parse_structured_log(log)
        if parsed and start <= parsed['timestamp'] <= end:
            filtered.append(log)
    
    return filtered
```

---

### Q5: IP Address Anonymizer

> **Task:** Write a function that takes a string containing an IP address (e.g., `"User 192.168.1.1 connected"`) and replaces the last octet with `0`.
> **Output:** `"User 192.168.1.0 connected"`

```python
import re

def anonymize_ip(text: str) -> str:
    """
    Replace last octet of any IP address with 0.
    
    Time: O(n) where n = length of text
    Space: O(n) for result string
    """
    # IP pattern: 4 groups of 1-3 digits separated by dots
    pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.)\d{1,3}'
    
    # Replace: keep first 3 octets, replace last with 0
    return re.sub(pattern, r'\g<1>0', text)

# Test
text = "User 192.168.1.1 connected from server 10.0.0.255"
print(anonymize_ip(text))
# "User 192.168.1.0 connected from server 10.0.0.0"

# Alternative: More strict IP validation
def anonymize_ip_strict(text: str) -> str:
    """Stricter IP matching (0-255 per octet)"""
    def validate_and_anonymize(match):
        octets = match.group().split('.')
        # Validate each octet is 0-255
        if all(0 <= int(o) <= 255 for o in octets):
            return '.'.join(octets[:3]) + '.0'
        return match.group()  # Return original if invalid
    
    pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    return re.sub(pattern, validate_and_anonymize, text)

# Alternative: Without regex
def anonymize_ip_no_regex(text: str) -> str:
    """Manual string parsing approach"""
    import ipaddress
    
    words = text.split()
    result = []
    
    for word in words:
        try:
            ip = ipaddress.ip_address(word.strip('.,;:'))
            # Get first 3 octets and add .0
            octets = str(ip).split('.')
            anonymized = '.'.join(octets[:3]) + '.0'
            result.append(word.replace(str(ip), anonymized))
        except ValueError:
            result.append(word)
    
    return ' '.join(result)

print(anonymize_ip_no_regex("User 192.168.1.1 connected"))
# "User 192.168.1.0 connected"

# GDPR-style: Hash the IP instead of truncating
import hashlib

def hash_ip(text: str) -> str:
    """Replace IP with hash for stronger anonymization"""
    pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    
    def hash_match(match):
        ip = match.group()
        hashed = hashlib.md5(ip.encode()).hexdigest()[:8]
        return f"IP_{hashed}"
    
    return re.sub(pattern, hash_match, text)

print(hash_ip("User 192.168.1.1 connected"))
# "User IP_a88f1ae5 connected"
```

**Key Points:**
- `\d{1,3}` matches 1-3 digits
- `\g<1>` in replacement refers to capture group 1
- Consider using `ipaddress` module for validation
- For GDPR compliance, hashing may be preferred over truncation

---

## Part 3: LeetCode Practice Solutions

### Two Sum (Easy)

> Given array of integers, return indices of two numbers that add up to target.

```python
def two_sum(nums: list, target: int) -> list:
    """
    Find two numbers that add up to target.
    
    Time: O(n) - single pass with hash map
    Space: O(n) - store seen numbers
    """
    seen = {}  # value -> index
    
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    
    return []  # No solution found

# Test
print(two_sum([2, 7, 11, 15], 9))  # [0, 1]
print(two_sum([3, 2, 4], 6))       # [1, 2]
print(two_sum([3, 3], 6))          # [0, 1]
```

**Why it matters for DE:** Teaches O(n) lookup vs O(n²) brute force.

---

### Contains Duplicate (Easy)

> Return true if any value appears at least twice in the array.

```python
def contains_duplicate(nums: list) -> bool:
    """
    Check if list contains duplicates.
    
    Time: O(n)
    Space: O(n)
    """
    return len(nums) != len(set(nums))

# Alternative: Early exit
def contains_duplicate_v2(nums: list) -> bool:
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False

# Test
print(contains_duplicate([1, 2, 3, 1]))  # True
print(contains_duplicate([1, 2, 3, 4]))  # False
```

**Why it matters for DE:** Basic set usage for deduplication.

---

### Top K Frequent Elements (Medium)

> Given array and k, return the k most frequent elements.

```python
from collections import Counter
import heapq

def top_k_frequent(nums: list, k: int) -> list:
    """
    Find k most frequent elements.
    
    Time: O(n log k) using heap
    Space: O(n)
    """
    counts = Counter(nums)
    # heapq.nlargest is O(n log k)
    return [x for x, _ in heapq.nlargest(k, counts.items(), key=lambda x: x[1])]

# Alternative: Using Counter.most_common
def top_k_frequent_v2(nums: list, k: int) -> list:
    """Simpler approach using Counter.most_common"""
    return [x for x, _ in Counter(nums).most_common(k)]

# Test
print(top_k_frequent([1,1,1,2,2,3], 2))  # [1, 2]
print(top_k_frequent([1], 1))             # [1]

# Bucket sort approach: O(n) time!
def top_k_frequent_bucket(nums: list, k: int) -> list:
    """
    O(n) solution using bucket sort.
    """
    counts = Counter(nums)
    # Bucket: index = frequency, value = list of elements
    buckets = [[] for _ in range(len(nums) + 1)]
    
    for num, freq in counts.items():
        buckets[freq].append(num)
    
    result = []
    # Iterate from highest frequency
    for i in range(len(buckets) - 1, 0, -1):
        result.extend(buckets[i])
        if len(result) >= k:
            return result[:k]
    
    return result
```

**Why it matters for DE:** Aggregation + sorting is crucial for analytics.

---

### Product of Array Except Self (Medium)

> Return array where each element is product of all other elements.
> Constraint: O(n) time, no division.

```python
def product_except_self(nums: list) -> list:
    """
    Product of array except self without division.
    
    Time: O(n)
    Space: O(1) excluding output
    """
    n = len(nums)
    result = [1] * n
    
    # Left products: result[i] = product of nums[0..i-1]
    left_product = 1
    for i in range(n):
        result[i] = left_product
        left_product *= nums[i]
    
    # Right products: multiply by product of nums[i+1..n-1]
    right_product = 1
    for i in range(n - 1, -1, -1):
        result[i] *= right_product
        right_product *= nums[i]
    
    return result

# Test
print(product_except_self([1, 2, 3, 4]))  # [24, 12, 8, 6]
# result[0] = 2*3*4 = 24
# result[1] = 1*3*4 = 12
# result[2] = 1*2*4 = 8
# result[3] = 1*2*3 = 6
```

**Why it matters for DE:** Array manipulation without nested loops.

---

### Valid Anagram (Easy)

> Determine if two strings are anagrams.

```python
from collections import Counter

def is_anagram(s: str, t: str) -> bool:
    """
    Check if t is an anagram of s.
    
    Time: O(n)
    Space: O(1) - at most 26 characters
    """
    return Counter(s) == Counter(t)

# Alternative: Sorting (O(n log n))
def is_anagram_sort(s: str, t: str) -> bool:
    return sorted(s) == sorted(t)

# Test
print(is_anagram("anagram", "nagaram"))  # True
print(is_anagram("rat", "car"))          # False
```

---

### First Unique Character in a String (Easy)

> Return index of first non-repeating character.

```python
from collections import Counter

def first_uniq_char(s: str) -> int:
    """
    Find first unique character's index.
    
    Time: O(n)
    Space: O(1) - at most 26 chars
    """
    counts = Counter(s)
    
    for i, char in enumerate(s):
        if counts[char] == 1:
            return i
    
    return -1

# Test
print(first_uniq_char("leetcode"))      # 0 ('l')
print(first_uniq_char("loveleetcode"))  # 2 ('v')
print(first_uniq_char("aabb"))          # -1
```

**Why it matters for DE:** Similar to finding unique keys in datasets.

---

## Part 4: Take Home Challenge

### Server CPU Average Calculator

> Given a list of tuples `(server_name, cpu_usage_percent)`, return a dictionary with the **average CPU usage** for each server.

```python
from collections import defaultdict

def calculate_avg_cpu(data: list) -> dict:
    """
    Calculate average CPU usage per server.
    
    Time: O(n) where n = number of data points
    Space: O(s) where s = unique servers
    """
    # Track sum and count for each server
    server_stats = defaultdict(lambda: {'sum': 0, 'count': 0})
    
    for server, cpu in data:
        server_stats[server]['sum'] += cpu
        server_stats[server]['count'] += 1
    
    # Calculate averages
    return {
        server: stats['sum'] / stats['count']
        for server, stats in server_stats.items()
    }

# Test
data = [
    ("ServerA", 15),
    ("ServerB", 10),
    ("ServerA", 55),
    ("ServerC", 80),
    ("ServerB", 5)
]
print(calculate_avg_cpu(data))
# {'ServerA': 35.0, 'ServerB': 7.5, 'ServerC': 80.0}

# Alternative: Using two dictionaries
def calculate_avg_cpu_v2(data: list) -> dict:
    """Alternative with separate sum and count dicts"""
    sums = defaultdict(int)
    counts = defaultdict(int)
    
    for server, cpu in data:
        sums[server] += cpu
        counts[server] += 1
    
    return {server: sums[server] / counts[server] for server in sums}

# Alternative: Using pandas (for large datasets)
def calculate_avg_cpu_pandas(data: list) -> dict:
    """Pandas approach (better for large data)"""
    import pandas as pd
    
    df = pd.DataFrame(data, columns=['server', 'cpu'])
    return df.groupby('server')['cpu'].mean().to_dict()

# Advanced: Add min, max, percentiles
def calculate_server_stats(data: list) -> dict:
    """Comprehensive server statistics"""
    from statistics import mean, stdev
    
    server_data = defaultdict(list)
    for server, cpu in data:
        server_data[server].append(cpu)
    
    return {
        server: {
            'avg': mean(cpus),
            'min': min(cpus),
            'max': max(cpus),
            'count': len(cpus),
            'stdev': stdev(cpus) if len(cpus) > 1 else 0
        }
        for server, cpus in server_data.items()
    }

print(calculate_server_stats(data))
# {'ServerA': {'avg': 35.0, 'min': 15, 'max': 55, 'count': 2, 'stdev': 28.28...},
#  'ServerB': {'avg': 7.5, 'min': 5, 'max': 10, 'count': 2, 'stdev': 3.53...},
#  'ServerC': {'avg': 80.0, 'min': 80, 'max': 80, 'count': 1, 'stdev': 0}}
```

**Key Points:**
- Use `defaultdict` to avoid KeyError
- Track both sum AND count for computing average
- Dictionary comprehension for final result
- Consider edge cases: empty list, single value per server

---

## Summary: Python Patterns for Data Engineering Interviews

| Pattern | When to Use | Example |
|---------|-------------|---------|
| **`dict.get(key, default)`** | Safe access with default | `counts.get(word, 0) + 1` |
| **`defaultdict(list)`** | Group items by key | Anagram grouping |
| **`defaultdict(int)`** | Count occurrences | Word frequency |
| **`set()` for lookup** | O(1) membership check | Find duplicates |
| **`Counter`** | Frequency counting | Top K elements |
| **`sorted()` as key** | Normalize for grouping | Anagram key |
| **Regex for parsing** | Structured text extraction | Log parsing, IP detection |
| **Two-pointer/Hash map** | Pair finding | Two Sum |

---

## Common Interview Mistakes to Avoid

1. **Using `list.count()` in loops** — O(n²) instead of O(n)
   ```python
   # BAD: O(n²)
   [x for x in nums if nums.count(x) > 1]
   
   # GOOD: O(n)
   Counter(nums)
   ```

2. **Forgetting `list` is not hashable**
   ```python
   # BAD: unhashable type
   {[1,2,3]: "value"}
   
   # GOOD: use tuple
   {(1,2,3): "value"}
   ```

3. **Modifying dict/list while iterating**
   ```python
   # BAD: RuntimeError
   for k in d:
       del d[k]
   
   # GOOD: iterate over copy
   for k in list(d.keys()):
       del d[k]
   ```

4. **Not handling edge cases**
   - Empty input
   - Single element
   - All duplicates / no duplicates
   - Case sensitivity
