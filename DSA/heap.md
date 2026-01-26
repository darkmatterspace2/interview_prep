# Heaps in Python: The Priority Queue Powerhouse

In Python, the built-in `heapq` module implements a **Min-Heap**. Heaps are crucial for "Top K", "Median", and "Scheduling" problems.

## 1. Basic Operations (`heapq`)

Python's heap is a simple list `[]` that is maintained in heap order.

```python
import heapq

# 1. Initialize
min_heap = []
numbers = [5, 1, 8, 3, 2]

# 2. Heapify (Convert list to heap in O(N))
heapq.heapify(numbers)
print(numbers) # Output: [1, 2, 8, 3, 5] (Smallest element at index 0)

# 3. Push (Insert in O(log N))
heapq.heappush(min_heap, 10)
heapq.heappush(min_heap, 1)

# 4. Pop (Remove Smallest in O(log N))
smallest = heapq.heappop(min_heap) # Returns 1

# 5. Peek (Get Smallest without removing in O(1))
if min_heap:
    print(min_heap[0])
```

---

## 2. The "Max-Heap" Trick

Python **does not** have a native Max-Heap.
**Workaround**: Multiply numbers by **-1** when pushing, and multiply by **-1** when popping.

```python
max_heap = []

# Push (Negate values)
heapq.heappush(max_heap, -10)
heapq.heappush(max_heap, -5)
heapq.heappush(max_heap, -20)

# Pop (Negate back)
largest = -heapq.heappop(max_heap) # -(-20) = 20
```

---

## 3. Advanced LeetCode Patterns

### Pattern 1: Top 'K' Elements (Largest/Smallest)
*Problem: Find the Kth largest element in an array.*
*Strategy: Maintain a Min-Heap of size K. If heap grows > K, pop the smallest. The heap will eventually hold the K largest elements.*

```python
def findKthLargest(nums: list[int], k: int) -> int:
    heap = []
    for n in nums:
        heapq.heappush(heap, n)
        # If we have more than k elements, discard the smallest
        # The remaining elements are the largest seen so far
        if len(heap) > k:
            heapq.heappop(heap)
            
    return heap[0] # The root is the Kth largest
```

### Pattern 2: Merge K Sorted Lists
*Problem: Merge K sorted linked lists into one sorted list.*
*Strategy: Push the head of every list into a Min-Heap. Pop smallest, add to result, then push that node's `.next` into heap.*

```python
def mergeKLists(lists: list[ListNode]) -> ListNode:
    min_heap = []
    
    # 1. Push head of each list
    for i, l in enumerate(lists):
        if l:
            # Tuple: (value, index, node) to handle tie-breaking
            heapq.heappush(min_heap, (l.val, i, l))
            
    dummy = ListNode(0)
    curr = dummy
    
    # 2. Process heap
    while min_heap:
        val, i, node = heapq.heappop(min_heap)
        curr.next = node
        curr = curr.next
        
        if node.next:
            heapq.heappush(min_heap, (node.next.val, i, node.next))
            
    return dummy.next
```

### Pattern 3: Two Heaps (Median of Data Stream)
*Problem: Find median of specific stream of numbers efficiently.*
*Strategy: Use a Max-Heap for the left half (smaller numbers) and a Min-Heap for right half (larger numbers).*

```python
class MedianFinder:
    def __init__(self):
        self.small = [] # Max-Heap (inverted values)
        self.large = [] # Min-Heap

    def addNum(self, num: int) -> None:
        # Push to Max-Heap (small half)
        heapq.heappush(self.small, -num)
        
        # Balance: Make sure every element in small is <= every element in large
        # Pop max from small and push to large
        if self.small and self.large and (-self.small[0] > self.large[0]):
            val = -heapq.heappop(self.small)
            heapq.heappush(self.large, val)
            
        # Balance Sizes: small can have at most 1 more element than large
        if len(self.small) > len(self.large) + 1:
            val = -heapq.heappop(self.small)
            heapq.heappush(self.large, val)
        elif len(self.large) > len(self.small):
            val = heapq.heappop(self.large)
            heapq.heappush(self.small, -val)

    def findMedian(self) -> float:
        if len(self.small) > len(self.large):
            return -self.small[0]
        else:
            return (-self.small[0] + self.large[0]) / 2.0
```

---

## 4. Top LeetCode Problems to Practice

| Problem | Difficulty | Key Technique |
| :--- | :--- | :--- |
| **Kth Largest Element in Array** | Medium | Min-Heap of size K |
| **Top K Frequent Elements** | Medium | Map + Heap |
| **Merge K Sorted Lists** | Hard | Min-Heap storing Nodes |
| **Find Median from Data Stream** | Hard | Two Heaps Pattern |
| **Task Scheduler** | Medium | Max-Heap + Cooldown logic |
| **Last Stone Weight** | Easy | Simulation with Max-Heap |

## 5. Common "Gotchas"
1.  **Complexity**:
    *   `heapify`: O(N)
    *   `push/pop`: O(log N)
    *   `nlargest/nsmallest`: O(N log K)
2.  **Modifying Elements**: You cannot efficiently update an element inside a heap. Usually, "Lazy Removal" (checking validity upon pop) is used.
3.  **Tuples**: When pushing tuples `(priority, item)`, Python compares the first element. If equal, it compares the second (so `item` must be comparable or unique).
