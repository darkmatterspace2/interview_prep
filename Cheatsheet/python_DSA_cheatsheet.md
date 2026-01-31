# Python Cheat Sheet for LeetCode


Essential syntax and libraries for competitive programming and coding interviews.

## Table of Contents
- [1. Lists (Arrays)](#1-lists-arrays)
- [2. Strings](#2-strings)
- [3. Hash Maps (Dictionary)](#3-hash-maps-dictionary)
- [4. Hash Set](#4-hash-set)
- [5. Queue & Stack (Deque)](#5-queue--stack-deque)
- [6. Heap (Priority Queue)](#6-heap-priority-queue)
- [7. Binary Search (Bisect)](#7-binary-search-bisect)
- [8. Math & Infinity](#8-math--infinity)
- [9. Classes & OOP](#9-classes--oop)
- [10. Lambda Functions](#10-lambda-functions)
- [11. Decorators](#11-decorators)
- [12. Linked List](#12-linked-list)
- [13. Binary Tree](#13-binary-tree)
- [14. N-ary Tree](#14-n-ary-tree)
- [15. Common Patterns](#15-common-patterns)
- [16. Graph Representation (Adjacency List)](#16-graph-representation-adjacency-list)
- [17. Breadth-First Search (BFS)](#17-breadth-first-search-bfs)
- [18. Depth-First Search (DFS)](#18-depth-first-search-dfs)
- [19. Dijkstra's Algorithm](#19-dijkstras-algorithm)


## 1. Lists (Arrays)
[Back to Top](#table-of-contents)
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
[Back to Top](#table-of-contents)
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
[Back to Top](#table-of-contents)
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

# Conversions
keys_list = list(d.keys())
values_list = list(d.values())
items_list = list(d.items()) # List of tuples [(k,v), ...]
```

## 4. Hash Set
[Back to Top](#table-of-contents)
Unordered collection of unique elements. Average O(1) ops.
```python
s = set()
s.add(1)
s.remove(1)             # Raises KeyError if missing
s.discard(1)            # No error
1 in s                  # Check existence

# Conversion
s_list = list(s)        # Convert to list
```

## 5. Queue & Stack (Deque)
[Back to Top](#table-of-contents)
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
[Back to Top](#table-of-contents)
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
[Back to Top](#table-of-contents)
Built-in module for sorted arrays.
```python
import bisect

nums = [1, 3, 4, 4, 5]

# Find insertion point (Left = first index, Right = after last)
bisect.bisect_left(nums, 4)     # Returns 2
bisect.bisect_right(nums, 4)    # Returns 4
```

## 8. Math & Infinity
[Back to Top](#table-of-contents)
```python
import math

val = float('inf')
val = float('-inf')

math.gcd(12, 18)
math.ceil(2.3)          # 3
math.floor(2.3)         # 2
pow(2, 3, 5)            # (2^3) % 5 = 3
```

## 9. Classes & OOP
[Back to Top](#table-of-contents)
```python
class Dog:
    # Constructor
    def __init__(self, name):
        self.name = name
    
    # Method
    def bark(self):
        print(f"{self.name} says Woof!")

d = Dog("Buddy")
d.bark()
```

## 10. Lambda Functions
[Back to Top](#table-of-contents)
Anonymous small functions.
```python
add = lambda x, y: x + y
print(add(2, 3))  # 5

# With map/filter
nums = [1, 2, 3, 4]
squared = list(map(lambda x: x**2, nums))      # [1, 4, 9, 16]
evens = list(filter(lambda x: x % 2 == 0, nums)) # [2, 4]
```

## 11. Decorators
[Back to Top](#table-of-contents)
Wrappers to modify function behavior.
```python
def my_decorator(func):
    def wrapper():
        print("Before function call")
        func()
        print("After function call")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()
```

## 12. Linked List
[Back to Top](#table-of-contents)
Standard class definition for LeetCode.
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

# Traversal
curr = head
while curr:
    print(curr.val)
    curr = curr.next

# Reverse List (Iterative)
prev, curr = None, head
while curr:
    temp = curr.next
    curr.next = prev
    prev = curr
    curr = temp

# Fast & Slow Pointers (Cycle Detection)
slow, fast = head, head
while fast and fast.next:
    slow = slow.next
    fast = fast.next.next
    if slow == fast:
        return True # Cycle detected
return False
```

## 13. Binary Tree
[Back to Top](#table-of-contents)
```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# DFS Traversal (Recursive)
def dfs(root):
    if not root: return
    
    # print(root.val) # Pre-order
    dfs(root.left)
    # print(root.val) # In-order
    dfs(root.right)
    # print(root.val) # Post-order
```

## 14. N-ary Tree
[Back to Top](#table-of-contents)
```python
class Node:
    def __init__(self, val=None, children=None):
        self.val = val
        self.children = children if children else []

# Level Order Traversal
from collections import deque
def level_order(root):
    if not root: return []
    q = deque([root])
    result = []
    
    while q:
        node = q.popleft()
        result.append(node.val)
        for child in node.children:
            q.append(child)
    return result
```

## 15. Common Patterns
[Back to Top](#table-of-contents)

### Sliding Window
**1. Variable Size (Shrinkable)**: Find valid window (e.g., Min Subarray Sum)
```python
l = 0
for r in range(len(nums)):
    # add nums[r] to window
    while invalid(window):
        # remove nums[l]
        l += 1
```

**2. Fixed Size (k)**: Max Sum of size k
```python
window_sum = sum(nums[:k])
max_sum = window_sum

for i in range(k, len(nums)):
    window_sum += nums[i] - nums[i - k]
    max_sum = max(max_sum, window_sum)
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
## 16. Graph Representation (Adjacency List)
[Back to Top](#table-of-contents)
```python
from collections import defaultdict

# Input: List of edges (u, v)
edges = [[0, 1], [0, 2], [1, 2], [2, 0], [2, 3], [3, 3]]
# Output: Graph representation where key is node, value is list of neighbors

adj = defaultdict(list)
for u, v in edges:
    adj[u].append(v)
    # adj[v].append(u) # Uncomment for undirected graph

print(dict(adj)) 
# Output: {0: [1, 2], 1: [2], 2: [0, 3], 3: [3]}
```

## 17. Breadth-First Search (BFS)
[Back to Top](#table-of-contents)
Layer by layer traversal. Good for finding shortest path in unweighted graphs or level-order traversal.
```python
from collections import deque

def bfs(start_node):
    # Queue for BFS, initialize with start node
    q = deque([start_node])
    # Set to keep track of visited nodes to avoid cycles
    visited = {start_node}
    result = []
    
    while q:
        node = q.popleft()
        result.append(node)
        
        # Explore neighbors
        for neighbor in adj[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                q.append(neighbor)
    return result

# Input: Start at node 2
# Graph: {0: [1, 2], 1: [2], 2: [0, 3], 3: [3]}
print(bfs(2)) 
# Output: [2, 0, 3, 1] (Order may vary depending on neighbor order)
```

## 18. Depth-First Search (DFS)
[Back to Top](#table-of-contents)
Deep traversal exploration. Good for exhaustive search, tree traversals, and cycle detection.

### Recursive DFS
```python
visited_dfs = set()
dfs_result = []

def dfs(node):
    if node in visited_dfs:
        return
    
    visited_dfs.add(node)
    dfs_result.append(node)
    
    # Recursively visit neighbors
    for neighbor in adj[node]:
        dfs(neighbor)

# Input: Start at node 2
dfs(2)
print(dfs_result) 
# Output: [2, 0, 1, 3] (Depth first: 2->0->1, then back to 2->3)
```

### Iterative DFS
```python
def dfs_iterative(start_node):
    stack = [start_node]
    visited = {start_node}
    result = []
    
    while stack:
        node = stack.pop()
        result.append(node)
        
        for neighbor in reversed(adj[node]): # Reversed to mimic recursive order
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append(neighbor)
    return result
```

## 19. Dijkstra's Algorithm
[Back to Top](#table-of-contents)
Finds the shortest path in a weighted graph with non-negative weights.
```python
import heapq

def dijkstra(n, edges, start):
    # Build weighted graph
    adj = defaultdict(list)
    for u, v, w in edges:
        adj[u].append((v, w))
    
    # Priority Queue stores (current_distance, node)
    pq = [(0, start)]
    
    # Dictionary to track shortest distance found so far
    # Initialize with infinity
    dist = {i: float('inf') for i in range(n)}
    dist[start] = 0
    
    while pq:
        # Pop node with smallest distance
        d, node = heapq.heappop(pq)
        
        # If we found a shorter path strictly better than current 'd', skip
        if d > dist[node]:
            continue
        
        # Check neighbors
        for neighbor, weight in adj[node]:
            new_dist = d + weight
            # If shorter path found, update and push to PQ
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor))
                
    return dist

# Input: 5 nodes (0 to 4), Weighted Edges
edges_w = [
    [0, 1, 4], [0, 2, 1],
    [2, 1, 2], [2, 3, 5],
    [1, 3, 1], [3, 4, 3]
]
# Start Dijkstra from node 0
print(dijkstra(5, edges_w, 0))
# Output: {0: 0, 1: 3, 2: 1, 3: 4, 4: 7}
# Explanation: Path 0->2->1->3->4 gives weights 1+2+1+3=7 which is min for node 4.
```
