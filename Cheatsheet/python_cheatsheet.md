# Python Cheat Sheet for LeetCode

Essential syntax and libraries for competitive programming and coding interviews.

## 1. Lists (Arrays)
```python
nums = [1, 2, 3]

# Operations
nums.append(4)          # O(1)
nums.pop()              # O(1) - Remove last
nums.pop(0)             # O(n) - Remove first (Avoid!)
nums.insert(0, 5)       # O(n) - Insert at index
nums.sort()             # O(n log n) - In-place
sorted(nums)            # Returns new list
nums[::-1]              # Reverse list

# Slicing [start:end:step]
nums[1:3]               # index 1 to 2
nums[-1]                # Last element

# List Comprehension
squares = [x**2 for x in nums if x > 0]
matrix = [[0]*5 for _ in range(5)] # 5x5 matrix
```

## 2. Strings
Strings are **immutable**.
```python
s = "Hello World"

# Common Methods
s.lower() / s.upper()
s.strip()               # Remove whitespace
s.split(" ")            # Return list
",".join(['a', 'b'])    # Join list -> "a,b"
s.find("Wor")           # Returns index or -1
s.replace("l", "x")     # Returns new string

# ASCII
ord('a')                # 97
chr(97)                 # 'a'
```

## 3. Hash Maps (Dictionary)
```python
d = {}
d = {'a': 1, 'b': 2}

# keys, values, items
for k, v in d.items():
    print(k, v)

# Get with default
d.get('c', 0)           # Returns 0 if key missing

# DefaultDict (Cleaner code)
from collections import defaultdict
graph = defaultdict(list)   # Default value is []
graph[1].append(2)          # No KeyError
```

## 4. Hash Set
Unordered collection of unique elements. Average O(1) ops.
```python
s = set()
s.add(1)
s.remove(1)             # Raises KeyError if missing
s.discard(1)            # No error
1 in s                  # Check existence
```

## 5. Queue & Stack (Deque)
Use `collections.deque` for O(1) appends/pops from both ends.
```python
from collections import deque

# Stack (LIFO)
stack = []
stack.append(1)
stack.pop()

# Queue (FIFO)
q = deque([1, 2])
q.append(3)             # Enqueue
q.popleft()             # Dequeue O(1)
```

## 6. Heap (Priority Queue)
Python has only **Min Heap** by default. For Max Heap, insert negative values.
```python
import heapq

min_heap = []
heapq.heappush(min_heap, 3)
heapq.heappush(min_heap, 1)
smallest = heapq.heappop(min_heap)  # Returns 1

# Heapify (O(n))
nums = [5, 1, 3]
heapq.heapify(nums)     # nums becomes [1, 5, 3]

# Max Heap trick
max_heap = []
heapq.heappush(max_heap, -5)
print(-heapq.heappop(max_heap))     # 5
```

## 7. Binary Search (Bisect)
Built-in module for sorted arrays.
```python
import bisect

nums = [1, 3, 4, 4, 5]

# Find insertion point (Left = first index, Right = after last)
bisect.bisect_left(nums, 4)     # Returns 2
bisect.bisect_right(nums, 4)    # Returns 4
```

## 8. Math & Infinity
```python
import math

val = float('inf')
val = float('-inf')

math.gcd(12, 18)
math.ceil(2.3)          # 3
math.floor(2.3)         # 2
pow(2, 3, 5)            # (2^3) % 5 = 3
```

## 9. Common Patterns

### Sliding Window
```python
l = 0
for r in range(len(nums)):
    # add nums[r] to window
    while invalid(window):
        # remove nums[l]
        l += 1
```

### Two Pointers
```python
l, r = 0, len(nums) - 1
while l < r:
    if nums[l] + nums[r] == target:
        return True
    elif nums[l] + nums[r] < target:
        l += 1
    else:
        r -= 1
```

### BFS (Graph/Matrix)
```python
q = deque([(0, 0)])
visited = set([(0,0)])
directions = [(0,1), (0,-1), (1,0), (-1,0)]

while q:
    r, c = q.popleft()
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and (nr, nc) not in visited:
            visited.add((nr, nc))
            q.append((nr, nc))
```
