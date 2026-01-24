# Data Structures and Algorithms in Python for FAANG Interviews

This guide covers essential data structures and algorithms using Python, tailored for technical interviews. We use standard libraries where possible (`collections`, `heapq`) and custom classes for pointer-based structures.

## 1. Arrays (Dynamic Arrays)
In Python, the built-in `list` serves as a dynamic array.

### Concept
- Contiguous memory.
- Dynamic resizing (amortized O(1) append).
- Random access O(1).

### Implementation & Examples
```python
# Initialization
arr = [1, 2, 3, 4, 5]

# Access
print(f"Element at index 2: {arr[2]}") # Output: 3

# Append (O(1))
arr.append(6)

# Insert (O(n)) - avoid in tight loops
arr.insert(0, 0)

# Delete/Remove (O(n))
arr.pop() # Removes last element (O(1))
arr.remove(3) # Removes first occurrence of 3 (O(n))

# Slicing
sub_arr = arr[1:3] # Creates a new list [1, 2]

# Iteration
for num in arr:
    pass

# List Comprehension (Pythonic way)
squares = [x**2 for x in arr]
```

---

## 2. Linked Lists
A collection of nodes where each node points to the next. Python doesn't have a built-in Linked List class, so we define `ListNode`.

### Concept
- Non-contiguous memory.
- Efficient insertion/deletion at known positions O(1).
- Linear access time O(n).

### Implementation
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, val):
        if not self.head:
            self.head = ListNode(val)
            return
        curr = self.head
        while curr.next:
            curr = curr.next
        curr.next = ListNode(val)

    def print_list(self):
        curr = self.head
        values = []
        while curr:
            values.append(str(curr.val))
            curr = curr.next
        print(" -> ".join(values))

# Usage
ll = LinkedList()
ll.append(1)
ll.append(2)
ll.append(3)
ll.print_list()
# Output: 1 -> 2 -> 3
```
**Algo Note:** A dummy/sentinel node is often used in interview problems (e.g., merging sorted lists) to simplify edge cases.

---

## 3. Stacks
LIFO (Last In, First Out). Use `collections.deque` or a simple `list`.

### Concept
- `push`: Add to top.
- `pop`: Remove from top.
- `peek`: Look at top.

### Implementation
```python
from collections import deque

# Using deque (Preferred over list for O(1) appends/pops from both ends)
stack = deque()

# Push
stack.append(10)
stack.append(20)
stack.append(30)

# Peek
print(f"Top: {stack[-1]}") # Output: 30

# Pop
val = stack.pop()
print(f"Popped: {val}")    # Output: 30

# Check empty
if not stack:
    print("Stack is empty")
```

---

## 4. Queues
FIFO (First In, First Out). Always use `collections.deque`. Using `list` for queues is inefficient (O(n) pop from front).

### Concept
- `enqueue`: Add to rear.
- `dequeue`: Remove from front.

### Implementation
```python
from collections import deque

queue = deque()

# Enqueue
queue.append(1)
queue.append(2)
queue.append(3)

# Dequeue
first = queue.popleft() # O(1) operation
print(f"Dequeued: {first}") # Output: 1

print(f"Next in line: {queue[0]}") # Output: 2
```

---

## 5. Binary Trees
Hierarchical structure. Essential for searching and sorting.

### Concept
- **Max Depth**: O(h), h is height.
- **Traversals**: Inorder (Left-Root-Right), Preorder (Root-Left-Right), Postorder (Left-Right-Root).

### Implementation
```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# Example: Constructing a simple tree
#      1
#     / \
#    2   3
root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)

# DFS Traversal (Recursive)
def inorder(node):
    if not node:
        return
    inorder(node.left)
    print(node.val, end=' ')
    inorder(node.right)

print("Inorder:")
inorder(root) # Output: 2 1 3 (approx)
print()

# BFS Traversal (Level Order) using Queue
from collections import deque
def bfs(root):
    if not root: return
    q = deque([root])
    while q:
        node = q.popleft()
        print(node.val, end=' ')
        if node.left: q.append(node.left)
        if node.right: q.append(node.right)

print("BFS:")
bfs(root) # Output: 1 2 3
print()
```

---

## 6. Heaps (Priority Queues)
Python's `heapq` module implements a **Min-Heap** by default.

### Concept
- Access Min/Max: O(1).
- Insert: O(log n).
- Pop Min/Max: O(log n).
- Useful for "Kth largest/smallest" problems.

### Implementation
```python
import heapq

# Min Heap
min_heap = []
heapq.heappush(min_heap, 10)
heapq.heappush(min_heap, 1)
heapq.heappush(min_heap, 5)

print(f"Smallest: {min_heap[0]}") # Output: 1

smallest = heapq.heappop(min_heap)
print(f"Popped: {smallest}")      # Output: 1

# Max Heap: Python does not have strict max-heap, multiply by -1
nums = [1, 10, 5]
max_heap = [-n for n in nums]
heapq.heapify(max_heap) # O(n) to build

largest = -heapq.heappop(max_heap)
print(f"Largest: {largest}")     # Output: 10
```

---

## 7. Genres (Graphs)
Represented via Adjacency Lists (Dict of Lists/Sets) or Adjacency Matrix.

### Concept
- **Nodes/Vertices** connected by **Edges**.
- **DFS**: Deep exploration (stack/recursion).
- **BFS**: Level exploration (queue), shortest path in unweighted graphs.

### Implementation
```python
from collections import deque

# Adjacency List: { 'A': ['B', 'C'], 'B': ['A'], ... }
graph = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F'],
    'D': [],
    'E': ['F'],
    'F': []
}

def bfs_graph(start_node):
    visited = set()
    queue = deque([start_node])
    visited.add(start_node)
    
    while queue:
        node = queue.popleft()
        print(node, end=" ")
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

print("Graph BFS:")
bfs_graph('A')
# Output: A B C D E F (Order may vary slightly based on implementation)
print()
```

---

## 8. Hash Maps (Dictionaries)
Python's `dict` is a robust hash map.

### Concept
- Key-Value pairs.
- Average O(1) for insert, delete, get.
- Keys must be immutable (hashable).

### Implementation
```python
# Initialization
hash_map = {}
hash_map['name'] = 'Alice'
hash_map['age'] = 25

# Existence check
if 'name' in hash_map:
    print(hash_map['name'])

# Iteration
for key, value in hash_map.items():
    print(f"{key}: {value}")

# Collections.defaultdict (Very useful for interviews)
from collections import defaultdict
# Automatically creates default value if key missing
count = defaultdict(int) 
names = ["a", "b", "a", "c"]
for n in names:
    count[n] += 1
print(dict(count)) # {'a': 2, 'b': 1, 'c': 1}
```

## Summary of Complexities

| Data Structure | Access | Search | Insertion | Deletion |
| :--- | :--- | :--- | :--- | :--- |
| **Array** | O(1) | O(n) | O(n) | O(n) |
| **Stack/Queue** | O(n) | O(n) | O(1) | O(1) |
| **Linked List** | O(n) | O(n) | O(1)* | O(1)* |
| **Doubly Linked List** | O(n) | O(n) | O(1) | O(1) |
| **Hash Table** | N/A | O(1) | O(1) | O(1) |
| **BST** | O(log n) | O(log n) | O(log n) | O(log n) |

*\* At known position (head/tail).*
