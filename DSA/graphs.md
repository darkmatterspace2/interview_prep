# Graphs in Python: Representations & Algorithms

Graphs are collections of Nodes (Vertices) and Edges. Use an **Adjacency List** (Dictionary of Lists/Sets) to represent them in Python.

## 1. Representation

```python
# Adjacency List using HashMap
# Graph: 0-1, 0-2, 1-2, 2-3
graph = {
    0: [1, 2],
    1: [0, 2],
    2: [0, 1, 3],
    3: [2]
}

# OR Building from Edge List
edges = [[0,1], [0,2], [1,2], [2,3]]
from collections import defaultdict

adj = defaultdict(list)
for u, v in edges:
    adj[u].append(v)
    adj[v].append(u) # For undirected
```

---

## 2. Core Traversals

### A. Breadth First Search (BFS)
*Shortest Path in Unweighted Graph. Level-by-level.*

```python
from collections import deque

def bfs(start_node, adj):
    visited = set([start_node])
    queue = deque([start_node])
    
    while queue:
        node = queue.popleft()
        print(node) # Process node
        
        for neighbor in adj[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
```

### B. Depth First Search (DFS)
*Finding components, cycles, topological sorts.*

```python
def dfs(node, adj, visited):
    if node in visited: return
    visited.add(node)
    print(node) # Process node
    
    for neighbor in adj[node]:
        dfs(neighbor, adj, visited)

# Usage
visited = set()
dfs(0, adj, visited)
```

---

## 3. Advanced Algorithms

### Pattern 1: Number of Islands (Grid DFS)
*Problem: Count connected components of '1's in a grid.*

```python
def numIslands(grid: list[list[str]]) -> int:
    if not grid: return 0
    rows, cols = len(grid), len(grid[0])
    count = 0
    
    def dfs(r, c):
        if r < 0 or c < 0 or r >= rows or c >= cols or grid[r][c] == '0':
            return
        grid[r][c] = '0' # Mark as visited (sink the island)
        dfs(r+1, c); dfs(r-1, c); dfs(r, c+1); dfs(r, c-1)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                count += 1
                dfs(r, c)
    return count
```

### Pattern 2: Topological Sort (Course Schedule)
*Problem: Order tasks with prerequisites. (Directed Acyclic Graph).*
*Algorithm: Kahn's Algorithm (BFS with Indegrees).*

```python
def canFinish(numCourses: int, prerequisites: list[list[int]]) -> bool:
    adj = defaultdict(list)
    indegree = [0] * numCourses
    
    # 1. Build Graph & Indegrees
    for dest, src in prerequisites:
        adj[src].append(dest)
        indegree[dest] += 1
        
    # 2. Queue with 0-indegree nodes
    queue = deque([i for i in range(numCourses) if indegree[i] == 0])
    count = 0
    
    # 3. Process
    while queue:
        course = queue.popleft()
        count += 1
        for neighbor in adj[course]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)
                
    return count == numCourses # True if all courses taken
```

### Pattern 3: Shortest Path (Dijkstra's Algo)
*Shortest Path in Weighted Graph (Non-negative).*
*Time: O(E log V) using Heap.*

```python
import heapq

def networkDelayTime(times: list[list[int]], n: int, k: int) -> int:
    adj = defaultdict(list)
    for u, v, w in times:
        adj[u].append((v, w))
        
    # Min-Heap: (dist_from_start, node)
    min_heap = [(0, k)]
    visited = set()
    t = 0
    
    while min_heap:
        w1, n1 = heapq.heappop(min_heap)
        if n1 in visited: continue
        visited.add(n1)
        t = max(t, w1) # Track max time to reach a node
        
        for n2, w2 in adj[n1]:
            if n2 not in visited:
                heapq.heappush(min_heap, (w1 + w2, n2))
                
    return t if len(visited) == n else -1
```

---

## 4. Top Graph Problems Checklist

| Problem | Difficulty | Key |
| :--- | :--- | :--- |
| **Number of Islands** | Medium | Grid DFS/BFS |
| **01 Matrix** | Medium | Multi-source BFS |
| **Rotting Oranges** | Medium | Level-wise BFS |
| **Course Schedule** | Medium | Topological Sort (Cycle detect) |
| **Word Ladder** | Hard | BFS (Shortest Transformation) |
| **Network Delay Time** | Medium | Dijkstra's |
| **Cheapest Flights (K stops)** | Medium | Bellman-Ford / Dijkstra Mod |
| **Clone Graph** | Medium | DFS/BFS + Map |

## 5. Common "Gotchas"
1.  **Visited Set**: Crucial to prevent infinite loops (cycles).
2.  **Directed vs Undirected**: Read carefully. For Undirected, add edges both ways `u->v` and `v->u`.
3.  **Disconnected Components**: You might need a loop to run BFS/DFS on every unvisited node (e.g., Number of Islands), not just start from node 0.
