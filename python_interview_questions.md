# Advanced Python Interview Questions for Data Engineers
*Mid to Senior Level*

A detailed guide to Python concepts critical for building robust, scalable data pipelines. Focuses on memory management, functional programming, high-performance pandas, and concurrency.

---

## Table of Contents
1. [Core Python & Memory Management](#core-python--memory-management)
2. [Data Processing (Pandas & NumPy)](#data-processing-pandas--numpy)
3. [Concurrency & Parallelism](#concurrency--parallelism)
4. [Functional Programming & Patterns](#functional-programming--patterns)
5. [Algorithmic Scenarios for DE](#algorithmic-scenarios-for-de)

---

## Core Python & Memory Management

### 1. Generators vs Iterators (`yield` keyword)
**Q:** What is the difference between a list and a generator? Why prefer generators for ETL?
**A:**
- **List:** Stores all elements in memory at once. `[x*2 for x in range(10000000)]` can cause OOM (Out of Memory).
- **Generator:** Lazily produces items one by one. `(x*2 for x in range(10000000))` uses constant memory.
- **DE Use Case:** Reading a 50GB log file line-by-line using `yield` instead of `readlines()`.

```python
def read_large_file(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            yield line.strip()

# Usage - Memory efficient iteration
for line in read_large_file('huge_log.txt'):
    process(line)
```

### 2. Context Managers (`with` statement)
**Q:** How do Context Managers work? Write a custom one for a Database connection.
**A:** They ensure resources are acquired and released (setup/teardown) automatically using `__enter__` and `__exit__`.
```python
class DBConnection:
    def __init__(self, db_url):
        self.db_url = db_url

    def __enter__(self):
        print("Connecting to DB...")
        self.conn = connect_to_db(self.db_url)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing Connection...")
        self.conn.close()
        # Returning False propagates exceptions, True suppresses them
        return False

# Usage
with DBConnection('postgres://...') as conn:
    conn.execute("SELECT * FROM users")
```

### 3. Shallow vs Deep Copy
**Q:** Explain the issue here: `list_a = [[1], [2]]; list_b = list_a`.
**A:** `list_b` is just a reference. Modifying `list_b[0][0] = 99` changes `list_a` too.
- **Shallow Copy (`copy.copy`):** Copies the container but references the inner objects.
- **Deep Copy (`copy.deepcopy`):** Recursively copies everything. Critical when manipulating nested JSON/Dicts in pipelines to avoid side effects.

---

## Data Processing (Pandas & NumPy)

### 4. Vectorization vs `apply()`
**Q:** Why is iteration over a DataFrame slow? How do you speed it up?
**A:**
1.  **Iteration (`iterrows`)**: Slowest. Python level loop.
2.  **`apply()`**: Better, but still processes row-by-row (mostly).
3.  **Vectorization (NumPy/Pandas Native)**: Fastest. Uses optimized C/Cython execution.

**Example:** Calculate `col_C = col_A * col_B`
```python
# SLOW
df['C'] = df.apply(lambda row: row['A'] * row['B'], axis=1)

# FAST (Vectorized)
df['C'] = df['A'] * df['B']
```

### 5. Memory Optimization in Pandas
**Q:** You have a 10GB CSV but only 8GB RAM. How do you load it?
**A:**
1.  **Chunking:** `pd.read_csv('file.csv', chunksize=10000)` and process iteratively.
2.  **Dtypes:**
    - Downcast ints: `int64` -> `int32` or `int16`.
    - Strings to Categoricals: If a column has low cardinality (e.g., 'Gender', 'Country'), `astype('category')` saves ~90% memory.
    - Use `usecols` to load only necessary columns.

---

## Concurrency & Parallelism

### 6. GIL (Global Interpreter Lock)
**Q:** What is the GIL? Does it affect Data Engineering tasks?
**A:**
- **GIL:** A mutex that prevents multiple native threads from executing Python bytecodes at once.
- **Impact:** Python threads are not true parallel for **CPU-bound** tasks (e.g., heavy math, complex scrubbing).
- **Solution:** Use **Multiprocessing** (separate processes, unrelated memory) for CPU tasks.
- **Exception:** For **I/O-bound** tasks (API requests, DB queries, File downloads), the GIL is released. Threading works well here.

### 7. Multiprocessing vs Threading
**Scenario:** You need to scrape 1000 websites vs You need to resize 1000 images.
- **Scraping (I/O Bound):** Use `threading` or `asyncio`.
- **Image Resizing (CPU Bound):** Use `multiprocessing`.

---

## Functional Programming & Patterns

### 8. Decorators
**Q:** Write a decorator that retries a function 3 times if it fails.
**A:**
```python
import time
from functools import wraps

def retry(retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == retries - 1: raise e
                    time.sleep(delay)
                    print(f"Retrying {i+1}...")
        return wrapper
    return decorator

@retry(retries=3)
def extract_data_from_api():
    # Flaky API call
    pass
```

### 9. Map, Filter, Reduce
**Q:** Transform a list of numbers: keep evens, multiply by 2, and sum them up using functional tools.
```python
from functools import reduce

nums = [1, 2, 3, 4, 5, 6]

# Functional approach
result = reduce(lambda x, y: x + y, 
               map(lambda x: x * 2, 
                   filter(lambda x: x % 2 == 0, nums)))
# Result: (2*2) + (4*2) + (6*2) = 4 + 8 + 12 = 24
```

---

## Algorithmic Scenarios for DE

### 10. Streaming Data Moving Average
**Q:** Design a class `MovingAverage` that receives a stream of integers and computes the moving average of the last N items.
**A:** Using a `deque` (Doubly Ended Queue) is O(1) for appending/popping, unlike a list which is O(N) for popping from the start.
```python
from collections import deque

class MovingAverage:
    def __init__(self, size):
        self.size = size
        self.queue = deque()
        self.total_sum = 0 # Maintain sum to avoid O(N) recalculation

    def next(self, val):
        self.queue.append(val)
        self.total_sum += val
        
        if len(self.queue) > self.size:
            removed = self.queue.popleft()
            self.total_sum -= removed
            
        return self.total_sum / len(self.queue)
```

### 11. Custom Sort
**Q:** Sort a list of file names `['file_1.txt', 'file_10.txt', 'file_2.txt']` numerically, not alphabetically.
**A:** Default sort gives `1, 10, 2`. We need a lambda key.
```python
files = ['file_1.txt', 'file_10.txt', 'file_2.txt']

files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
# Output: ['file_1.txt', 'file_2.txt', 'file_10.txt']
```
