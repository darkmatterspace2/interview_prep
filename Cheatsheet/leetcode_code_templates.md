# LeetCode Problem Solving & Code Templates

A guide on **how to approach** problems and **reusable code templates** for efficient solving.

## 0. Quick Pattern Reference
A mapping of common problems to the standard pattern used to solve them.

| Problem Type | Example Problem | Recommended Pattern |
| :--- | :--- | :--- |
| **Two Sum** | "Find pair summing to target" | **Hash Map** (if unsorted) or **Two Pointers** (if sorted) |
| **Three Sum** | "Find triplets summing to zero" | **Two Pointers** (Sort array first) |
| **Anagram** | "Check if s is anagram of t" | **Hash Map** (Frequency Count) or **Sorting** ($O(N \log N)$) |
| **Duplicate** | "Find duplicates in array" | **Hash Set** or **Cyclic Sort** ($O(1)$ Space) |
| **Subarray Sum** | "Smallest subarray with sum $\ge S$" | **Sliding Window** (Dynamic size) |
| **Palindrome** | "Longest Palindromic Substring" | **Expand Around Center** (Two Pointers) |
| **Top K** | "Find K largest elements" | **Min-Heap** (Size K) |
| **Merge Intervals** | "Merge overlapping intervals" | **Sorting** (by Start time) + **Iteration** |
| **Cycle Detection** | "Detect cycle in Linked List" | **Fast & Slow Pointers** |
| **Dependencies** | "Course Schedule" | **Topological Sort** (Kahn's or DFS) |
| **Islands** | "Number of Islands" | **DFS** (Recursive) or **BFS** (Queue) |
| **Shortest Path** | "Shortest path in maze" | **BFS** (Unweighted) or **Dijkstra** (Weighted) |

---


## 1. Constraint Analysis (Time Complexity)
Always look at the input size constraints ($N$) to guess the required time complexity.

| Input Size ($N$) | Required Time Complexity | Likely Algorithm |
| :--- | :--- | :--- |
| $\le 10$ | $O(N!)$ or $O(2^N)$ | Backtracking, Recursion |
| $\le 20$ | $O(2^N)$ | Backtracking, Power Set |
| $\le 500$ | $O(N^3)$ | DP (3 states), Floyd-Warshall |
| $\le 2,000$ | $O(N^2)$ | DP (2 states), Selection Sort, All-pairs check |
| $\le 10^5$ | $O(N \log N)$ or $O(N)$ | Sort, Heap, Binary Search, 2-Pointers |
| $\le 10^6$ | $O(N)$ | Hash Map, Two Pointers, Sliding Window |
| $\le 10^{18}$ | $O(1)$ or $O(\log N)$ | Math, Binary Search |

---

## 2. Universal Code Templates

### A. Binary Search (Find Target / Boundary)
```python
def binary_search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

### B. DFS (Depth First Search) - Grid
```python
def dfs(r, c, grid, visited):
    if (r < 0 or c < 0 or r >= len(grid) 
        or c >= len(grid[0]) or (r,c) in visited 
        or grid[r][c] == '0'):
        return
    
    visited.add((r, c))
    
    # Visit 4 neighbors
    dfs(r+1, c, grid, visited)
    dfs(r-1, c, grid, visited)
    dfs(r, c+1, grid, visited)
    dfs(r, c-1, grid, visited)
```

### C. BFS (Breadth First Search) - Shortest Path
```python
from collections import deque

def bfs_shortest_path(start, target, grid):
    rows, cols = len(grid), len(grid[0])
    queue = deque([(start[0], start[1], 0)]) # r, c, dist
    visited = set([(start[0], start[1])])
    directions = [(0,1), (0,-1), (1,0), (-1,0)]
    
    while queue:
        r, c, dist = queue.popleft()
        
        if (r, c) == target:
            return dist
            
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols 
                and (nr, nc) not in visited and grid[nr][nc] != 'X'):
                visited.add((nr, nc))
                queue.append((nr, nc, dist + 1))
    return -1
```

### D. Union-Find (Disjoint Set) - Cycle Detection / Components
```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [1] * n
        self.count = n # Number of connected components
        
    def find(self, p):
        if self.parent[p] != p:
            self.parent[p] = self.find(self.parent[p]) # Path compression
        return self.parent[p]
        
    def union(self, p, q):
        rootP = self.find(p)
        rootQ = self.find(q)
        if rootP != rootQ:
            # Union by rank
            if self.rank[rootP] > self.rank[rootQ]:
                self.parent[rootQ] = rootP
            elif self.rank[rootP] < self.rank[rootQ]:
                self.parent[rootP] = rootQ
            else:
                self.parent[rootQ] = rootP
                self.rank[rootP] += 1
            self.count -= 1
            return True
        return False
```

### E. Trie (Prefix Tree) - STRING Search
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end
```

### F. Topological Sort (Kahn's Algorithm)
Used for Course Schedule problems (Dependency resolution).
```python
from collections import deque, defaultdict

def topological_sort(numCourses, prerequisites):
    adj = defaultdict(list)
    in_degree = [0] * numCourses
    
    # Build Graph
    for dest, src in prerequisites:
        adj[src].append(dest)
        in_degree[dest] += 1
        
    # BFS
    queue = deque([i for i in range(numCourses) if in_degree[i] == 0])
    result = []
    
    while queue:
        node = queue.popleft()
        result.append(node)
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
                
    return result if len(result) == numCourses else [] # Empty if cycle detected
```

### G. Dijkstra's Algorithm (Shortest Path in Weighted Graph)
```python
import heapq

def dijkstra(n, edges, start_node):
    adj = defaultdict(list)
    for u, v, w in edges:
        adj[u].append((v, w))
        
    min_heap = [(0, start_node)] # (cost, node)
    shortest_dist = {}
    
    while min_heap:
        w1, n1 = heapq.heappop(min_heap)
        
        if n1 in shortest_dist:
            continue
        shortest_dist[n1] = w1
        
        for n2, w2 in adj[n1]:
            if n2 not in shortest_dist:
                heapq.heappush(min_heap, (w1 + w2, n2))
                
    return shortest_dist
```
