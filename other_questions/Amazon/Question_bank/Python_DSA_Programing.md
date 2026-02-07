# Python Interview Questions & Answers (Question Bank 1)

> **Amazon Data Engineer Style** - Data Engineering Focus with Performance Considerations

---

<a id="index"></a>
## 📑 Table of Contents

| Section | Topics |
|---------|--------|
| [1️⃣ Data Structures & Logic](#1️⃣-data-structures--logic) | Counting, Dedup, Grouping, Sorting, Merging |
| &nbsp;&nbsp;&nbsp;└ [Q26: Count occurrences](#q26-count-occurrences-from-list-of-shipment-events) | Counter, defaultdict |
| &nbsp;&nbsp;&nbsp;└ [Q27: Find duplicates](#q27-find-duplicates-in-a-list-of-dictionaries) | Set-based |
| &nbsp;&nbsp;&nbsp;└ [Q28: Group by region](#q28-group-shipments-by-region) | defaultdict, groupby |
| &nbsp;&nbsp;&nbsp;└ [Q29: Sort by timestamp](#q29-sort-events-by-timestamp) | sorted, key functions |
| &nbsp;&nbsp;&nbsp;└ [Q30: Merge datasets](#q30-merge-two-shipment-datasets) | Dictionary merge |
| [2️⃣ String / JSON Processing](#2️⃣-string--json-processing) | Parsing, Flattening, Logs |
| &nbsp;&nbsp;&nbsp;└ [Q31: Parse nested JSON](#q31-parse-nested-json-shipment-events) | safe_get pattern |
| &nbsp;&nbsp;&nbsp;└ [Q32: Flatten JSON](#q32-flatten-json-into-tabular-format) | Recursive flatten |
| &nbsp;&nbsp;&nbsp;└ [Q33: Handle malformed JSON](#q33-handle-malformed-json-records-safely) | Error handling |
| &nbsp;&nbsp;&nbsp;└ [Q34: Extract from logs](#q34-extract-fields-from-semi-structured-logs) | Regex patterns |
| &nbsp;&nbsp;&nbsp;└ [Q35: Normalize status values](#q35-normalize-inconsistent-status-values) | Mapping |
| [3️⃣ Performance & Memory](#3️⃣-performance--memory) | Large files, Generators |
| &nbsp;&nbsp;&nbsp;└ [Q36: Process large file](#q36-process-a-large-file-line-by-line) | Line-by-line |
| &nbsp;&nbsp;&nbsp;└ [Q37: Loop vs dict lookup](#q37-optimize-loop-vs-dictionary-lookup) | O(n) vs O(1) |
| &nbsp;&nbsp;&nbsp;└ [Q38: Streaming vs batch](#q38-streaming-vs-batch-processing-logic) | Hybrid approach |
| &nbsp;&nbsp;&nbsp;└ [Q39: Generator vs list](#q39-generator-vs-list--when-and-why) | Memory efficient |
| &nbsp;&nbsp;&nbsp;└ [Q40: Handle millions of records](#q40-handling-millions-of-records-safely) | Chunking, GC |
| [4️⃣ Error Handling](#4️⃣-error-handling) | Skip, Log, Retry, Validate |
| &nbsp;&nbsp;&nbsp;└ [Q41: Skip bad records](#q41-skip-bad-records-but-continue-processing) | Try/except pattern |
| &nbsp;&nbsp;&nbsp;└ [Q42: Log failures](#q42-log-failures-with-minimal-performance-hit) | Async logging |
| &nbsp;&nbsp;&nbsp;└ [Q43: Retry logic](#q43-retry-logic-for-failed-transformations) | Exponential backoff |
| &nbsp;&nbsp;&nbsp;└ [Q44: Validate schema](#q44-validate-schema-before-processing) | jsonschema |
| &nbsp;&nbsp;&nbsp;└ [Q45: Detect nulls](#q45-detect-nulls-and-unexpected-values) | Quality analysis |
| [5️⃣ Decorators & Functional](#5️⃣-decorators--functional-python) | Decorators, Higher-order |
| [6️⃣ APIs & Async](#6️⃣-api--async-patterns) | Pagination, Retries |

---

<a id="1️⃣-data-structures--logic"></a>
## 1️⃣ Data Structures & Logic [↩️](#index)

<a id="q26-count-occurrences-from-list-of-shipment-events"></a>
### Q26: Count occurrences from list of shipment events [↩️](#index)

```python
from collections import Counter

events = ['PICKED_UP', 'IN_TRANSIT', 'IN_TRANSIT', 'DELIVERED', 'PICKED_UP']

# Method 1: Counter (most Pythonic)
counts = Counter(events)

# Method 2: defaultdict
from collections import defaultdict
counts = defaultdict(int)
for event in events:
    counts[event] += 1
```

---

<a id="q27-find-duplicates-in-a-list-of-dictionaries"></a>
### Q27: Find duplicates in a list of dictionaries [↩️](#index)

```python
def find_duplicates(records, key_fields):
    seen = set()
    duplicates = []
    
    for record in records:
        key = tuple(record.get(k) for k in key_fields)
        if key in seen:
            duplicates.append(record)
        else:
            seen.add(key)
    
    return duplicates
```

---

<a id="q28-group-shipments-by-region"></a>
### Q28: Group shipments by region [↩️](#index)

```python
from collections import defaultdict

by_region = defaultdict(list)
for s in shipments:
    by_region[s['region']].append(s)
```

---

<a id="q29-sort-events-by-timestamp"></a>
### Q29: Sort events by timestamp [↩️](#index)

```python
from operator import itemgetter

sorted_events = sorted(events, key=itemgetter('timestamp'))
# Or with lambda for datetime parsing
sorted_events = sorted(events, key=lambda x: datetime.fromisoformat(x['timestamp']))
```

---

<a id="q30-merge-two-shipment-datasets"></a>
### Q30: Merge two shipment datasets [↩️](#index)

```python
def merge_datasets(primary, secondary, key='id', strategy='override'):
    secondary_index = {r[key]: r for r in secondary}
    result = []
    
    for record in primary:
        if record[key] in secondary_index:
            result.append({**record, **secondary_index[record[key]]})
        else:
            result.append(record)
    
    return result
```

---

<a id="2️⃣-string--json-processing"></a>
## 2️⃣ String / JSON Processing [↩️](#index)

<a id="q31-parse-nested-json-shipment-events"></a>
### Q31: Parse nested JSON shipment events [↩️](#index)

```python
def safe_get(d, *keys, default=None):
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key, default)
        elif isinstance(d, list) and isinstance(key, int) and key < len(d):
            d = d[key]
        else:
            return default
    return d

city = safe_get(data, 'events', 0, 'location', 'city')
```

---

<a id="q32-flatten-json-into-tabular-format"></a>
### Q32: Flatten JSON into tabular format [↩️](#index)

```python
def flatten_json(nested_json, prefix=''):
    flat = {}
    for key, value in nested_json.items():
        new_key = f"{prefix}_{key}" if prefix else key
        if isinstance(value, dict):
            flat.update(flatten_json(value, new_key))
        else:
            flat[new_key] = value
    return flat
```

---

<a id="q33-handle-malformed-json-records-safely"></a>
### Q33: Handle malformed JSON records safely [↩️](#index)

```python
def safe_parse_json(json_string, default=None):
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        return default
```

---

<a id="q34-extract-fields-from-semi-structured-logs"></a>
### Q34: Extract fields from semi-structured logs [↩️](#index)

```python
import re

pattern = r'(\w+)=(?:"([^"]+)"|(\S+))'
fields = {m.group(1): m.group(2) or m.group(3) for m in re.finditer(pattern, line)}
```

---

<a id="q35-normalize-inconsistent-status-values"></a>
### Q35: Normalize inconsistent status values [↩️](#index)

```python
STATUS_MAP = {
    'DELIVERED': 'DELIVERED', 'DLVD': 'DELIVERED', 'COMPLETE': 'DELIVERED',
    'IN_TRANSIT': 'IN_TRANSIT', 'INTRANSIT': 'IN_TRANSIT',
}

def normalize_status(raw):
    return STATUS_MAP.get(raw.upper().strip(), 'UNKNOWN')
```

---

<a id="3️⃣-performance--memory"></a>
## 3️⃣ Performance & Memory [↩️](#index)

<a id="q36-process-a-large-file-line-by-line"></a>
### Q36: Process a large file line by line [↩️](#index)

```python
def process_large_file(file_path, process_func, chunk_size=10000):
    with open(file_path, 'r') as f:
        batch = []
        for line in f:  # Line by line, not loading entire file
            batch.append(process_func(line))
            if len(batch) >= chunk_size:
                yield batch
                batch = []
        if batch:
            yield batch
```

---

<a id="q37-optimize-loop-vs-dictionary-lookup"></a>
### Q37: Optimize loop vs dictionary lookup [↩️](#index)

```python
# ❌ BAD: O(n*m) - List lookup is O(n)
result = [s for s in shipments if s['id'] in valid_ids_list]

# ✅ GOOD: O(n) - Set lookup is O(1)
valid_ids_set = set(valid_ids_list)
result = [s for s in shipments if s['id'] in valid_ids_set]
```

---

<a id="q38-streaming-vs-batch-processing-logic"></a>
### Q38: Streaming vs batch processing logic [↩️](#index)

| Approach | Memory | Speed | Use Case |
|----------|--------|-------|----------|
| Batch | High (all in RAM) | Fast | Small-medium datasets |
| Streaming | Low (constant) | Slower | Large datasets |
| Hybrid | Medium (batch size) | Good | Large datasets needing efficiency |

---

<a id="q39-generator-vs-list--when-and-why"></a>
### Q39: Generator vs list — when and why? [↩️](#index)

```python
# LIST: All in memory
def get_list(n):
    return [create_item(i) for i in range(n)]

# GENERATOR: One at a time
def get_generator(n):
    for i in range(n):
        yield create_item(i)
```

---

<a id="q40-handling-millions-of-records-safely"></a>
### Q40: Handling millions of records safely [↩️](#index)

```python
import gc
from itertools import islice

def process_millions(data_source, chunk_size=50000):
    while True:
        chunk = list(islice(data_source, chunk_size))
        if not chunk:
            break
        results = [process(record) for record in chunk]
        write_to_sink(results)
        del chunk, results
        gc.collect()
```

---

<a id="4️⃣-error-handling"></a>
## 4️⃣ Error Handling [↩️](#index)

<a id="q41-skip-bad-records-but-continue-processing"></a>
### Q41: Skip bad records but continue processing [↩️](#index)

```python
def process_with_skip(records, process_func):
    results, errors = [], []
    for record in records:
        try:
            results.append(process_func(record))
        except Exception as e:
            errors.append({'record': record, 'error': str(e)})
    return results, errors
```

---

<a id="q42-log-failures-with-minimal-performance-hit"></a>
### Q42: Log failures with minimal performance hit [↩️](#index)

```python
# Use async logging to avoid blocking main thread
from queue import Queue
from threading import Thread

class AsyncLogger:
    def __init__(self, log_file):
        self.queue = Queue()
        self._start_worker(log_file)
    
    def log(self, message):
        self.queue.put(message)  # Non-blocking
```

---

<a id="q43-retry-logic-for-failed-transformations"></a>
### Q43: Retry logic for failed transformations [↩️](#index)

```python
def retry(max_attempts=3, backoff_factor=2):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    time.sleep(backoff_factor ** attempt)
            raise e
        return wrapper
    return decorator
```

---

<a id="q44-validate-schema-before-processing"></a>
### Q44: Validate schema before processing [↩️](#index)

```python
import jsonschema

SCHEMA = {
    "type": "object",
    "required": ["id", "status"],
    "properties": {
        "id": {"type": "string"},
        "status": {"type": "string", "enum": ["PENDING", "DELIVERED"]}
    }
}

def validate(record):
    try:
        jsonschema.validate(record, SCHEMA)
        return True, None
    except jsonschema.ValidationError as e:
        return False, str(e.message)
```

---

<a id="q45-detect-nulls-and-unexpected-values"></a>
### Q45: Detect nulls and unexpected values [↩️](#index)

```python
def analyze_quality(records, schema):
    stats = {field: {'null_count': 0, 'unexpected': []} for field in schema}
    for record in records:
        for field, rules in schema.items():
            value = record.get(field)
            if value is None:
                stats[field]['null_count'] += 1
    return stats
```

---

<a id="5️⃣-decorators--functional-python"></a>
## 5️⃣ Decorators & Functional Python [↩️](#index)

- Timing decorator
- Caching/memoization
- Logging decorator
- functools: map, filter, reduce

---

<a id="6️⃣-api--async-patterns"></a>
## 6️⃣ API & Async Patterns [↩️](#index)

- Pagination handling
- Rate limiting
- Async/await patterns
- Connection pooling
