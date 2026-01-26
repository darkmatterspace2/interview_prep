# Linked List in Python: From Basics to Advanced

Linked Lists are fundamental for interviews. In Python, unlike C++, we define a class for nodes.

## 1. Basic Structure

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

# Creating a generic Linked List Wrapper (Optional, mostly for testing)
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
        while curr:
            print(curr.val, end=" -> ")
            curr = curr.next
        print("None")
```

---

## 2. Basic Operations (Must Know)

### A. Reverse a Linked List (Iterative)
*Time: O(N) | Space: O(1)*

```python
def reverseList(head: ListNode) -> ListNode:
    prev = None
    curr = head
    while curr:
        next_temp = curr.next  # Store next node
        curr.next = prev       # Reverse pointer
        prev = curr            # Move prev forward
        curr = next_temp       # Move curr forward
    return prev  # New head
```

### B. Find Middle of Linked List (Slow/Fast Pointers)
*Time: O(N) | Space: O(1)*

```python
def middleNode(head: ListNode) -> ListNode:
    slow = head
    fast = head
    while fast and fast.next:
        slow = slow.next      # Moves 1 step
        fast = fast.next.next # Moves 2 steps
    return slow # When fast reaches end, slow is at middle
```

### C. Detect Cycle (Floyd’s Cycle Finding Algorithm)
*Time: O(N) | Space: O(1)*

```python
def hasCycle(head: ListNode) -> bool:
    slow = head
    fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False
```

---

## 3. Advanced LeetCode Patterns

### Pattern 1: Merge Intervals / Lists (e.g., Merge Two Sorted Lists)
*Problem: Merge two sorted linked lists and return it as a sorted list.*

```python
def mergeTwoLists(l1: ListNode, l2: ListNode) -> ListNode:
    dummy = ListNode(0) # Dummy node to simplify edge cases
    tail = dummy
    
    while l1 and l2:
        if l1.val < l2.val:
            tail.next = l1
            l1 = l1.next
        else:
            tail.next = l2
            l2 = l2.next
        tail = tail.next
        
    tail.next = l1 if l1 else l2
    return dummy.next
```

### Pattern 2: Fast & Slow Pointers (e.g., Remove Nth Node From End)
*Strategy: Move `fast` pointer N steps ahead, then move both `slow` and `fast` until `fast` reaches the end.*

```python
def removeNthFromEnd(head: ListNode, n: int) -> ListNode:
    dummy = ListNode(0, head)
    left = dummy
    right = head
    
    # 1. Move right pointer n steps ahead
    while n > 0 and right:
        right = right.next
        n -= 1
    
    # 2. Move both pointers until right reaches end
    while right:
        left = left.next
        right = right.next
        
    # 3. Skip the nth node
    left.next = left.next.next
    
    return dummy.next
```

### Pattern 3: Linked List Reversal in K-Groups (Hard)
*Problem: Reverse nodes of a linked list k at a time.*
*Strategy: Use a dummy node and manage `prev`, `curr`, `next` pointers within chunks of size k.*

### Pattern 4: Intersection of Two Linked Lists
*Strategy: A+B = B+A. Walk path A then path B, and vice-versa. They will collide at intersection.*

```python
def getIntersectionNode(headA: ListNode, headB: ListNode) -> ListNode:
    if not headA or not headB: return None
    
    pA, pB = headA, headB
    
    while pA != pB:
        # If pA reaches end, jump to headB, else next
        pA = pA.next if pA else headB
        # If pB reaches end, jump to headA, else next
        pB = pB.next if pB else headA
        
    return pA # Either intersection node or None
```

---

## 4. Common "Gotchas"
1.  **Lost Head**: Always use a `dummy` node (sentinel) when the head might change (e.g., deletion, merging).
2.  **Null Pointer**: Always check `if not head` or `while curr` before accessing `.next`.
3.  **Cycles**: If you visit a node twice without expecting to, you have an infinite loop (Cycle detection saves you).

## 5. Top LeetCode Problems to Practice
1.  **Easy**: Reverse Linked List, Merge Two Sorted Lists, Linked List Cycle.
2.  **Medium**: Add Two Numbers, Remove Nth Node From End, Copy List with Random Pointer (Deep Copy).
3.  **Hard**: Merge k Sorted Lists (Heaps), Reverse Nodes in k-Group.
