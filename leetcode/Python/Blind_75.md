# LeetCode Blind 75 - Python Solutions

> Complete solutions with explanations, time & space complexity

---

<a id="index"></a>
## 📑 Table of Contents

| Category | Problems |
|----------|----------|
| [Array](#array) | Two Sum, Stock, Duplicates, Product, Subarray, etc. |
| [Binary](#binary) | Sum of Two Integers, 1 Bits, Counting Bits, etc. |
| [Dynamic Programming](#dynamic-programming) | Climbing Stairs, Coin Change, LIS, etc. |
| [Graph](#graph) | Clone Graph, Course Schedule, Islands, etc. |
| [Interval](#interval) | Insert, Merge, Non-overlapping |
| [Linked List](#linked-list) | Reverse, Cycle, Merge, etc. |
| [Matrix](#matrix) | Set Zeroes, Spiral, Rotate, Word Search |
| [String](#string) | Substring, Anagram, Parentheses, Palindrome |
| [Tree](#tree) | Depth, Invert, Path Sum, BST, Trie |
| [Heap](#heap) | Merge K Lists, Top K, Median |

---

<a id="array"></a>
## Array [↩️](#index)

### 1. [Two Sum](https://leetcode.com/problems/two-sum/) [↩️](#index)
```python
def twoSum(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
```
**Explanation:** Use hashmap to store seen numbers. For each number, check if complement exists.
- **Time:** O(n) | **Space:** O(n)

---

### 2. [Best Time to Buy and Sell Stock](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/) [↩️](#index)
```python
def maxProfit(prices: list[int]) -> int:
    min_price = float('inf')
    max_profit = 0
    for price in prices:
        min_price = min(min_price, price)
        max_profit = max(max_profit, price - min_price)
    return max_profit
```
**Explanation:** Track minimum price seen so far, calculate profit at each step.
- **Time:** O(n) | **Space:** O(1)

---

### 3. [Contains Duplicate](https://leetcode.com/problems/contains-duplicate/) [↩️](#index)
```python
def containsDuplicate(nums: list[int]) -> bool:
    return len(nums) != len(set(nums))
```
**Explanation:** Set removes duplicates; if lengths differ, duplicates exist.
- **Time:** O(n) | **Space:** O(n)

---

### 4. [Product of Array Except Self](https://leetcode.com/problems/product-of-array-except-self/) [↩️](#index)
```python
def productExceptSelf(nums: list[int]) -> list[int]:
    n = len(nums)
    result = [1] * n
    
    left = 1
    for i in range(n):
        result[i] = left
        left *= nums[i]
    
    right = 1
    for i in range(n - 1, -1, -1):
        result[i] *= right
        right *= nums[i]
    
    return result
```
**Explanation:** Two passes - first stores left products, second multiplies by right products.
- **Time:** O(n) | **Space:** O(1) excluding output

---

### 5. [Maximum Subarray](https://leetcode.com/problems/maximum-subarray/) [↩️](#index)
```python
def maxSubArray(nums: list[int]) -> int:
    max_sum = current_sum = nums[0]
    for num in nums[1:]:
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)
    return max_sum
```
**Explanation:** Kadane's algorithm - either start new subarray or extend current.
- **Time:** O(n) | **Space:** O(1)

---

### 6. [Maximum Product Subarray](https://leetcode.com/problems/maximum-product-subarray/) [↩️](#index)
```python
def maxProduct(nums: list[int]) -> int:
    max_prod = min_prod = result = nums[0]
    for num in nums[1:]:
        if num < 0:
            max_prod, min_prod = min_prod, max_prod
        max_prod = max(num, max_prod * num)
        min_prod = min(num, min_prod * num)
        result = max(result, max_prod)
    return result
```
**Explanation:** Track both max and min (negative * negative = positive).
- **Time:** O(n) | **Space:** O(1)

---

### 7. [Find Minimum in Rotated Sorted Array](https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/) [↩️](#index)
```python
def findMin(nums: list[int]) -> int:
    left, right = 0, len(nums) - 1
    while left < right:
        mid = (left + right) // 2
        if nums[mid] > nums[right]:
            left = mid + 1
        else:
            right = mid
    return nums[left]
```
**Explanation:** Binary search - if mid > right, min is in right half.
- **Time:** O(log n) | **Space:** O(1)

---

### 8. [Search in Rotated Sorted Array](https://leetcode.com/problems/search-in-rotated-sorted-array/) [↩️](#index)
```python
def search(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        
        if nums[left] <= nums[mid]:  # Left half sorted
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:  # Right half sorted
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1
```
**Explanation:** Determine which half is sorted, then decide which half to search.
- **Time:** O(log n) | **Space:** O(1)

---

### 9. [3Sum](https://leetcode.com/problems/3sum/) [↩️](#index)
```python
def threeSum(nums: list[int]) -> list[list[int]]:
    nums.sort()
    result = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i-1]:
            continue
        left, right = i + 1, len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total < 0:
                left += 1
            elif total > 0:
                right -= 1
            else:
                result.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
    return result
```
**Explanation:** Sort, fix one element, use two pointers for remaining two.
- **Time:** O(n²) | **Space:** O(1) excluding output

---

### 10. [Container With Most Water](https://leetcode.com/problems/container-with-most-water/) [↩️](#index)
```python
def maxArea(height: list[int]) -> int:
    left, right = 0, len(height) - 1
    max_water = 0
    while left < right:
        width = right - left
        h = min(height[left], height[right])
        max_water = max(max_water, width * h)
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return max_water
```
**Explanation:** Two pointers from ends, move the shorter one inward.
- **Time:** O(n) | **Space:** O(1)

---

<a id="binary"></a>
## Binary [↩️](#index)

### 11. [Sum of Two Integers](https://leetcode.com/problems/sum-of-two-integers/) [↩️](#index)
```python
def getSum(a: int, b: int) -> int:
    MASK = 0xFFFFFFFF
    MAX = 0x7FFFFFFF
    while b != 0:
        carry = (a & b) << 1
        a = (a ^ b) & MASK
        b = carry & MASK
    return a if a <= MAX else ~(a ^ MASK)
```
**Explanation:** XOR for addition without carry, AND + shift for carry.
- **Time:** O(1) | **Space:** O(1)

---

### 12. [Number of 1 Bits](https://leetcode.com/problems/number-of-1-bits/) [↩️](#index)
```python
def hammingWeight(n: int) -> int:
    count = 0
    while n:
        n &= (n - 1)  # Removes rightmost 1 bit
        count += 1
    return count
```
**Explanation:** Brian Kernighan's trick - n & (n-1) removes rightmost 1.
- **Time:** O(32) = O(1) | **Space:** O(1)

---

### 13. [Counting Bits](https://leetcode.com/problems/counting-bits/) [↩️](#index)
```python
def countBits(n: int) -> list[int]:
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i >> 1] + (i & 1)
    return dp
```
**Explanation:** dp[i] = dp[i/2] + last bit.
- **Time:** O(n) | **Space:** O(n)

---

### 14. [Missing Number](https://leetcode.com/problems/missing-number/) [↩️](#index)
```python
def missingNumber(nums: list[int]) -> int:
    n = len(nums)
    return n * (n + 1) // 2 - sum(nums)
```
**Explanation:** Sum formula - expected sum minus actual sum.
- **Time:** O(n) | **Space:** O(1)

---

### 15. [Reverse Bits](https://leetcode.com/problems/reverse-bits/) [↩️](#index)
```python
def reverseBits(n: int) -> int:
    result = 0
    for _ in range(32):
        result = (result << 1) | (n & 1)
        n >>= 1
    return result
```
**Explanation:** Shift result left, add LSB of n, shift n right.
- **Time:** O(32) = O(1) | **Space:** O(1)

---

<a id="dynamic-programming"></a>
## Dynamic Programming [↩️](#index)

### 16. [Climbing Stairs](https://leetcode.com/problems/climbing-stairs/) [↩️](#index)
```python
def climbStairs(n: int) -> int:
    if n <= 2:
        return n
    prev, curr = 1, 2
    for _ in range(3, n + 1):
        prev, curr = curr, prev + curr
    return curr
```
**Explanation:** Fibonacci - ways(n) = ways(n-1) + ways(n-2).
- **Time:** O(n) | **Space:** O(1)

---

### 17. [Coin Change](https://leetcode.com/problems/coin-change/) [↩️](#index)
```python
def coinChange(coins: list[int], amount: int) -> int:
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for coin in coins:
        for x in range(coin, amount + 1):
            dp[x] = min(dp[x], dp[x - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1
```
**Explanation:** dp[x] = min coins to make amount x.
- **Time:** O(amount × coins) | **Space:** O(amount)

---

### 18. [Longest Increasing Subsequence](https://leetcode.com/problems/longest-increasing-subsequence/) [↩️](#index)
```python
def lengthOfLIS(nums: list[int]) -> int:
    from bisect import bisect_left
    tails = []
    for num in nums:
        pos = bisect_left(tails, num)
        if pos == len(tails):
            tails.append(num)
        else:
            tails[pos] = num
    return len(tails)
```
**Explanation:** Maintain smallest tail for each LIS length.
- **Time:** O(n log n) | **Space:** O(n)

---

### 19. [Longest Common Subsequence](https://leetcode.com/problems/longest-common-subsequence/) [↩️](#index)
```python
def longestCommonSubsequence(text1: str, text2: str) -> int:
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]
```
**Explanation:** If chars match, add 1 to diagonal. Else take max of left/up.
- **Time:** O(m × n) | **Space:** O(m × n)

---

### 20. [Word Break](https://leetcode.com/problems/word-break/) [↩️](#index)
```python
def wordBreak(s: str, wordDict: list[str]) -> bool:
    words = set(wordDict)
    dp = [False] * (len(s) + 1)
    dp[0] = True
    for i in range(1, len(s) + 1):
        for j in range(i):
            if dp[j] and s[j:i] in words:
                dp[i] = True
                break
    return dp[len(s)]
```
**Explanation:** dp[i] = can segment s[:i].
- **Time:** O(n² × m) | **Space:** O(n)

---

### 21. [Combination Sum](https://leetcode.com/problems/combination-sum/) [↩️](#index)
```python
def combinationSum(candidates: list[int], target: int) -> list[list[int]]:
    result = []
    def backtrack(remain, combo, start):
        if remain == 0:
            result.append(list(combo))
            return
        for i in range(start, len(candidates)):
            if candidates[i] > remain:
                continue
            combo.append(candidates[i])
            backtrack(remain - candidates[i], combo, i)
            combo.pop()
    backtrack(target, [], 0)
    return result
```
**Explanation:** Backtracking - try each candidate, allow reuse.
- **Time:** O(n^(t/m)) | **Space:** O(t/m)

---

### 22. [House Robber](https://leetcode.com/problems/house-robber/) [↩️](#index)
```python
def rob(nums: list[int]) -> int:
    prev, curr = 0, 0
    for num in nums:
        prev, curr = curr, max(curr, prev + num)
    return curr
```
**Explanation:** At each house, max of (skip it, rob it + prev).
- **Time:** O(n) | **Space:** O(1)

---

### 23. [House Robber II](https://leetcode.com/problems/house-robber-ii/) [↩️](#index)
```python
def rob(nums: list[int]) -> int:
    if len(nums) == 1:
        return nums[0]
    
    def rob_linear(houses):
        prev, curr = 0, 0
        for h in houses:
            prev, curr = curr, max(curr, prev + h)
        return curr
    
    return max(rob_linear(nums[:-1]), rob_linear(nums[1:]))
```
**Explanation:** Circle - either skip first or skip last.
- **Time:** O(n) | **Space:** O(1)

---

### 24. [Decode Ways](https://leetcode.com/problems/decode-ways/) [↩️](#index)
```python
def numDecodings(s: str) -> int:
    if not s or s[0] == '0':
        return 0
    n = len(s)
    dp = [0] * (n + 1)
    dp[0], dp[1] = 1, 1
    for i in range(2, n + 1):
        if s[i-1] != '0':
            dp[i] += dp[i-1]
        two_digit = int(s[i-2:i])
        if 10 <= two_digit <= 26:
            dp[i] += dp[i-2]
    return dp[n]
```
**Explanation:** dp[i] = ways to decode s[:i].
- **Time:** O(n) | **Space:** O(n)

---

### 25. [Unique Paths](https://leetcode.com/problems/unique-paths/) [↩️](#index)
```python
def uniquePaths(m: int, n: int) -> int:
    dp = [1] * n
    for _ in range(1, m):
        for j in range(1, n):
            dp[j] += dp[j-1]
    return dp[n-1]
```
**Explanation:** dp[i][j] = dp[i-1][j] + dp[i][j-1].
- **Time:** O(m × n) | **Space:** O(n)

---

### 26. [Jump Game](https://leetcode.com/problems/jump-game/) [↩️](#index)
```python
def canJump(nums: list[int]) -> bool:
    max_reach = 0
    for i, jump in enumerate(nums):
        if i > max_reach:
            return False
        max_reach = max(max_reach, i + jump)
    return True
```
**Explanation:** Track farthest reachable index.
- **Time:** O(n) | **Space:** O(1)

---

<a id="graph"></a>
## Graph [↩️](#index)

### 27. [Clone Graph](https://leetcode.com/problems/clone-graph/) [↩️](#index)
```python
def cloneGraph(node):
    if not node:
        return None
    clones = {}
    def dfs(node):
        if node in clones:
            return clones[node]
        clone = Node(node.val)
        clones[node] = clone
        for neighbor in node.neighbors:
            clone.neighbors.append(dfs(neighbor))
        return clone
    return dfs(node)
```
**Explanation:** DFS with hashmap to track cloned nodes.
- **Time:** O(V + E) | **Space:** O(V)

---

### 28. [Course Schedule](https://leetcode.com/problems/course-schedule/) [↩️](#index)
```python
def canFinish(numCourses: int, prerequisites: list[list[int]]) -> bool:
    graph = [[] for _ in range(numCourses)]
    for course, prereq in prerequisites:
        graph[course].append(prereq)
    
    state = [0] * numCourses  # 0: unvisited, 1: visiting, 2: visited
    
    def has_cycle(course):
        if state[course] == 1:
            return True
        if state[course] == 2:
            return False
        state[course] = 1
        for prereq in graph[course]:
            if has_cycle(prereq):
                return True
        state[course] = 2
        return False
    
    return not any(has_cycle(i) for i in range(numCourses))
```
**Explanation:** Detect cycle using 3 states.
- **Time:** O(V + E) | **Space:** O(V + E)

---

### 29. [Pacific Atlantic Water Flow](https://leetcode.com/problems/pacific-atlantic-water-flow/) [↩️](#index)
```python
def pacificAtlantic(heights: list[list[int]]) -> list[list[int]]:
    m, n = len(heights), len(heights[0])
    pacific, atlantic = set(), set()
    
    def dfs(r, c, visited, prev):
        if (r, c) in visited or r < 0 or c < 0 or r >= m or c >= n or heights[r][c] < prev:
            return
        visited.add((r, c))
        for dr, dc in [(0,1), (0,-1), (1,0), (-1,0)]:
            dfs(r + dr, c + dc, visited, heights[r][c])
    
    for c in range(n):
        dfs(0, c, pacific, 0)
        dfs(m-1, c, atlantic, 0)
    for r in range(m):
        dfs(r, 0, pacific, 0)
        dfs(r, n-1, atlantic, 0)
    
    return list(pacific & atlantic)
```
**Explanation:** Reverse flow from oceans.
- **Time:** O(m × n) | **Space:** O(m × n)

---

### 30. [Number of Islands](https://leetcode.com/problems/number-of-islands/) [↩️](#index)
```python
def numIslands(grid: list[list[str]]) -> int:
    m, n = len(grid), len(grid[0])
    count = 0
    
    def dfs(r, c):
        if r < 0 or c < 0 or r >= m or c >= n or grid[r][c] != '1':
            return
        grid[r][c] = '0'
        dfs(r+1, c); dfs(r-1, c); dfs(r, c+1); dfs(r, c-1)
    
    for r in range(m):
        for c in range(n):
            if grid[r][c] == '1':
                count += 1
                dfs(r, c)
    return count
```
**Explanation:** DFS from each land cell, mark visited.
- **Time:** O(m × n) | **Space:** O(m × n)

---

### 31. [Longest Consecutive Sequence](https://leetcode.com/problems/longest-consecutive-sequence/) [↩️](#index)
```python
def longestConsecutive(nums: list[int]) -> int:
    num_set = set(nums)
    longest = 0
    for num in num_set:
        if num - 1 not in num_set:
            length = 1
            while num + length in num_set:
                length += 1
            longest = max(longest, length)
    return longest
```
**Explanation:** Only start from sequence beginning.
- **Time:** O(n) | **Space:** O(n)

---

<a id="interval"></a>
## Interval [↩️](#index)

### 32. [Insert Interval](https://leetcode.com/problems/insert-interval/) [↩️](#index)
```python
def insert(intervals, newInterval):
    result = []
    i = 0
    n = len(intervals)
    
    while i < n and intervals[i][1] < newInterval[0]:
        result.append(intervals[i])
        i += 1
    
    while i < n and intervals[i][0] <= newInterval[1]:
        newInterval[0] = min(newInterval[0], intervals[i][0])
        newInterval[1] = max(newInterval[1], intervals[i][1])
        i += 1
    result.append(newInterval)
    
    while i < n:
        result.append(intervals[i])
        i += 1
    return result
```
**Explanation:** Before, merge, after.
- **Time:** O(n) | **Space:** O(n)

---

### 33. [Merge Intervals](https://leetcode.com/problems/merge-intervals/) [↩️](#index)
```python
def merge(intervals):
    intervals.sort()
    result = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= result[-1][1]:
            result[-1][1] = max(result[-1][1], end)
        else:
            result.append([start, end])
    return result
```
**Explanation:** Sort by start, merge overlapping.
- **Time:** O(n log n) | **Space:** O(n)

---

### 34. [Non-overlapping Intervals](https://leetcode.com/problems/non-overlapping-intervals/) [↩️](#index)
```python
def eraseOverlapIntervals(intervals):
    intervals.sort(key=lambda x: x[1])
    count = 0
    prev_end = float('-inf')
    for start, end in intervals:
        if start >= prev_end:
            prev_end = end
        else:
            count += 1
    return count
```
**Explanation:** Greedy - sort by end, count removed.
- **Time:** O(n log n) | **Space:** O(1)

---

<a id="linked-list"></a>
## Linked List [↩️](#index)

### 35. [Reverse a Linked List](https://leetcode.com/problems/reverse-linked-list/) [↩️](#index)
```python
def reverseList(head):
    prev, curr = None, head
    while curr:
        next_temp = curr.next
        curr.next = prev
        prev = curr
        curr = next_temp
    return prev
```
- **Time:** O(n) | **Space:** O(1)

---

### 36. [Detect Cycle in a Linked List](https://leetcode.com/problems/linked-list-cycle/) [↩️](#index)
```python
def hasCycle(head) -> bool:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False
```
**Explanation:** Floyd's cycle detection.
- **Time:** O(n) | **Space:** O(1)

---

### 37. [Merge Two Sorted Lists](https://leetcode.com/problems/merge-two-sorted-lists/) [↩️](#index)
```python
def mergeTwoLists(list1, list2):
    dummy = ListNode(0)
    curr = dummy
    while list1 and list2:
        if list1.val <= list2.val:
            curr.next = list1
            list1 = list1.next
        else:
            curr.next = list2
            list2 = list2.next
        curr = curr.next
    curr.next = list1 or list2
    return dummy.next
```
- **Time:** O(n + m) | **Space:** O(1)

---

### 38. [Merge K Sorted Lists](https://leetcode.com/problems/merge-k-sorted-lists/) [↩️](#index)
```python
import heapq
def mergeKLists(lists):
    heap = []
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst.val, i, lst))
    dummy = ListNode(0)
    curr = dummy
    while heap:
        val, i, node = heapq.heappop(heap)
        curr.next = node
        curr = curr.next
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next
```
- **Time:** O(n log k) | **Space:** O(k)

---

### 39. [Remove Nth Node From End](https://leetcode.com/problems/remove-nth-node-from-end-of-list/) [↩️](#index)
```python
def removeNthFromEnd(head, n):
    dummy = ListNode(0, head)
    slow = fast = dummy
    for _ in range(n + 1):
        fast = fast.next
    while fast:
        slow = slow.next
        fast = fast.next
    slow.next = slow.next.next
    return dummy.next
```
- **Time:** O(n) | **Space:** O(1)

---

### 40. [Reorder List](https://leetcode.com/problems/reorder-list/) [↩️](#index)
```python
def reorderList(head):
    # Find middle, reverse second half, merge
    slow = fast = head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next
    
    prev, curr = None, slow.next
    slow.next = None
    while curr:
        next_temp = curr.next
        curr.next = prev
        prev = curr
        curr = next_temp
    
    first, second = head, prev
    while second:
        tmp1, tmp2 = first.next, second.next
        first.next = second
        second.next = tmp1
        first, second = tmp1, tmp2
```
- **Time:** O(n) | **Space:** O(1)

---

<a id="matrix"></a>
## Matrix [↩️](#index)

### 41. [Set Matrix Zeroes](https://leetcode.com/problems/set-matrix-zeroes/) [↩️](#index)
```python
def setZeroes(matrix):
    m, n = len(matrix), len(matrix[0])
    first_row_zero = any(matrix[0][j] == 0 for j in range(n))
    first_col_zero = any(matrix[i][0] == 0 for i in range(m))
    
    for i in range(1, m):
        for j in range(1, n):
            if matrix[i][j] == 0:
                matrix[i][0] = matrix[0][j] = 0
    
    for i in range(1, m):
        for j in range(1, n):
            if matrix[i][0] == 0 or matrix[0][j] == 0:
                matrix[i][j] = 0
    
    if first_row_zero:
        for j in range(n): matrix[0][j] = 0
    if first_col_zero:
        for i in range(m): matrix[i][0] = 0
```
- **Time:** O(m × n) | **Space:** O(1)

---

### 42. [Spiral Matrix](https://leetcode.com/problems/spiral-matrix/) [↩️](#index)
```python
def spiralOrder(matrix):
    result = []
    while matrix:
        result += matrix.pop(0)
        if matrix and matrix[0]:
            for row in matrix: result.append(row.pop())
        if matrix:
            result += matrix.pop()[::-1]
        if matrix and matrix[0]:
            for row in matrix[::-1]: result.append(row.pop(0))
    return result
```
- **Time:** O(m × n) | **Space:** O(1)

---

### 43. [Rotate Image](https://leetcode.com/problems/rotate-image/) [↩️](#index)
```python
def rotate(matrix):
    n = len(matrix)
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    for row in matrix:
        row.reverse()
```
**Explanation:** Transpose + reverse rows.
- **Time:** O(n²) | **Space:** O(1)

---

### 44. [Word Search](https://leetcode.com/problems/word-search/) [↩️](#index)
```python
def exist(board, word):
    m, n = len(board), len(board[0])
    def dfs(r, c, idx):
        if idx == len(word): return True
        if r < 0 or c < 0 or r >= m or c >= n or board[r][c] != word[idx]: return False
        temp, board[r][c] = board[r][c], '#'
        found = dfs(r+1,c,idx+1) or dfs(r-1,c,idx+1) or dfs(r,c+1,idx+1) or dfs(r,c-1,idx+1)
        board[r][c] = temp
        return found
    
    for i in range(m):
        for j in range(n):
            if dfs(i, j, 0): return True
    return False
```
- **Time:** O(m × n × 4^L) | **Space:** O(L)

---

<a id="string"></a>
## String [↩️](#index)

### 45. [Longest Substring Without Repeating](https://leetcode.com/problems/longest-substring-without-repeating-characters/) [↩️](#index)
```python
def lengthOfLongestSubstring(s):
    char_idx = {}
    left = max_len = 0
    for right, char in enumerate(s):
        if char in char_idx and char_idx[char] >= left:
            left = char_idx[char] + 1
        char_idx[char] = right
        max_len = max(max_len, right - left + 1)
    return max_len
```
- **Time:** O(n) | **Space:** O(min(n, alphabet))

---

### 46. [Longest Repeating Character Replacement](https://leetcode.com/problems/longest-repeating-character-replacement/) [↩️](#index)
```python
def characterReplacement(s, k):
    count = {}
    left = max_count = result = 0
    for right in range(len(s)):
        count[s[right]] = count.get(s[right], 0) + 1
        max_count = max(max_count, count[s[right]])
        if (right - left + 1) - max_count > k:
            count[s[left]] -= 1
            left += 1
        result = max(result, right - left + 1)
    return result
```
- **Time:** O(n) | **Space:** O(1)

---

### 47. [Minimum Window Substring](https://leetcode.com/problems/minimum-window-substring/) [↩️](#index)
```python
from collections import Counter
def minWindow(s, t):
    t_count = Counter(t)
    required, formed = len(t_count), 0
    window = {}
    left = 0
    result = (float('inf'), 0, 0)
    
    for right, char in enumerate(s):
        window[char] = window.get(char, 0) + 1
        if char in t_count and window[char] == t_count[char]:
            formed += 1
        while formed == required:
            if right - left + 1 < result[0]:
                result = (right - left + 1, left, right + 1)
            left_char = s[left]
            window[left_char] -= 1
            if left_char in t_count and window[left_char] < t_count[left_char]:
                formed -= 1
            left += 1
    return "" if result[0] == float('inf') else s[result[1]:result[2]]
```
- **Time:** O(|S| + |T|) | **Space:** O(|S| + |T|)

---

### 48. [Valid Anagram](https://leetcode.com/problems/valid-anagram/) [↩️](#index)
```python
def isAnagram(s, t):
    return Counter(s) == Counter(t)
```
- **Time:** O(n) | **Space:** O(1)

---

### 49. [Group Anagrams](https://leetcode.com/problems/group-anagrams/) [↩️](#index)
```python
from collections import defaultdict
def groupAnagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        groups[tuple(sorted(s))].append(s)
    return list(groups.values())
```
- **Time:** O(n × k log k) | **Space:** O(n × k)

---

### 50. [Valid Parentheses](https://leetcode.com/problems/valid-parentheses/) [↩️](#index)
```python
def isValid(s):
    stack = []
    pairs = {')': '(', '}': '{', ']': '['}
    for char in s:
        if char in pairs:
            if not stack or stack.pop() != pairs[char]:
                return False
        else:
            stack.append(char)
    return not stack
```
- **Time:** O(n) | **Space:** O(n)

---

### 51. [Valid Palindrome](https://leetcode.com/problems/valid-palindrome/) [↩️](#index)
```python
def isPalindrome(s):
    left, right = 0, len(s) - 1
    while left < right:
        while left < right and not s[left].isalnum(): left += 1
        while left < right and not s[right].isalnum(): right -= 1
        if s[left].lower() != s[right].lower(): return False
        left += 1; right -= 1
    return True
```
- **Time:** O(n) | **Space:** O(1)

---

### 52. [Longest Palindromic Substring](https://leetcode.com/problems/longest-palindromic-substring/) [↩️](#index)
```python
def longestPalindrome(s):
    def expand(l, r):
        while l >= 0 and r < len(s) and s[l] == s[r]:
            l -= 1; r += 1
        return s[l+1:r]
    result = ""
    for i in range(len(s)):
        result = max(result, expand(i,i), expand(i,i+1), key=len)
    return result
```
- **Time:** O(n²) | **Space:** O(1)

---

### 53. [Palindromic Substrings](https://leetcode.com/problems/palindromic-substrings/) [↩️](#index)
```python
def countSubstrings(s):
    count = 0
    for i in range(len(s)):
        for l, r in [(i, i), (i, i+1)]:
            while l >= 0 and r < len(s) and s[l] == s[r]:
                count += 1; l -= 1; r += 1
    return count
```
- **Time:** O(n²) | **Space:** O(1)

---

<a id="tree"></a>
## Tree [↩️](#index)

### 54. [Maximum Depth of Binary Tree](https://leetcode.com/problems/maximum-depth-of-binary-tree/) [↩️](#index)
```python
def maxDepth(root):
    if not root: return 0
    return 1 + max(maxDepth(root.left), maxDepth(root.right))
```
- **Time:** O(n) | **Space:** O(h)

---

### 55. [Same Tree](https://leetcode.com/problems/same-tree/) [↩️](#index)
```python
def isSameTree(p, q):
    if not p and not q: return True
    if not p or not q or p.val != q.val: return False
    return isSameTree(p.left, q.left) and isSameTree(p.right, q.right)
```
- **Time:** O(n) | **Space:** O(h)

---

### 56. [Invert Binary Tree](https://leetcode.com/problems/invert-binary-tree/) [↩️](#index)
```python
def invertTree(root):
    if not root: return None
    root.left, root.right = invertTree(root.right), invertTree(root.left)
    return root
```
- **Time:** O(n) | **Space:** O(h)

---

### 57. [Binary Tree Maximum Path Sum](https://leetcode.com/problems/binary-tree-maximum-path-sum/) [↩️](#index)
```python
def maxPathSum(root):
    max_sum = float('-inf')
    def dfs(node):
        nonlocal max_sum
        if not node: return 0
        left = max(dfs(node.left), 0)
        right = max(dfs(node.right), 0)
        max_sum = max(max_sum, node.val + left + right)
        return node.val + max(left, right)
    dfs(root)
    return max_sum
```
- **Time:** O(n) | **Space:** O(h)

---

### 58. [Binary Tree Level Order Traversal](https://leetcode.com/problems/binary-tree-level-order-traversal/) [↩️](#index)
```python
from collections import deque
def levelOrder(root):
    if not root: return []
    result, queue = [], deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left: queue.append(node.left)
            if node.right: queue.append(node.right)
        result.append(level)
    return result
```
- **Time:** O(n) | **Space:** O(n)

---

### 59. [Serialize and Deserialize Binary Tree](https://leetcode.com/problems/serialize-and-deserialize-binary-tree/) [↩️](#index)
```python
class Codec:
    def serialize(self, root):
        vals = []
        def dfs(node):
            if not node: vals.append('#'); return
            vals.append(str(node.val))
            dfs(node.left); dfs(node.right)
        dfs(root)
        return ','.join(vals)
    
    def deserialize(self, data):
        vals = iter(data.split(','))
        def dfs():
            val = next(vals)
            if val == '#': return None
            node = TreeNode(int(val))
            node.left = dfs(); node.right = dfs()
            return node
        return dfs()
```
- **Time:** O(n) | **Space:** O(n)

---

### 60. [Subtree of Another Tree](https://leetcode.com/problems/subtree-of-another-tree/) [↩️](#index)
```python
def isSubtree(root, subRoot):
    def isSame(p, q):
        if not p and not q: return True
        if not p or not q or p.val != q.val: return False
        return isSame(p.left, q.left) and isSame(p.right, q.right)
    if not root: return False
    return isSame(root, subRoot) or isSubtree(root.left, subRoot) or isSubtree(root.right, subRoot)
```
- **Time:** O(m × n) | **Space:** O(m + n)

---

### 61. [Construct Tree from Preorder and Inorder](https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/) [↩️](#index)
```python
def buildTree(preorder, inorder):
    if not preorder: return None
    root = TreeNode(preorder[0])
    mid = inorder.index(preorder[0])
    root.left = buildTree(preorder[1:mid+1], inorder[:mid])
    root.right = buildTree(preorder[mid+1:], inorder[mid+1:])
    return root
```
- **Time:** O(n) | **Space:** O(n)

---

### 62. [Validate Binary Search Tree](https://leetcode.com/problems/validate-binary-search-tree/) [↩️](#index)
```python
def isValidBST(root):
    def validate(node, min_val, max_val):
        if not node: return True
        if node.val <= min_val or node.val >= max_val: return False
        return validate(node.left, min_val, node.val) and validate(node.right, node.val, max_val)
    return validate(root, float('-inf'), float('inf'))
```
- **Time:** O(n) | **Space:** O(h)

---

### 63. [Kth Smallest Element in BST](https://leetcode.com/problems/kth-smallest-element-in-a-bst/) [↩️](#index)
```python
def kthSmallest(root, k):
    stack, curr, count = [], root, 0
    while stack or curr:
        while curr:
            stack.append(curr); curr = curr.left
        curr = stack.pop()
        count += 1
        if count == k: return curr.val
        curr = curr.right
```
- **Time:** O(H + k) | **Space:** O(H)

---

### 64. [Lowest Common Ancestor of BST](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/) [↩️](#index)
```python
def lowestCommonAncestor(root, p, q):
    while root:
        if p.val < root.val and q.val < root.val: root = root.left
        elif p.val > root.val and q.val > root.val: root = root.right
        else: return root
```
- **Time:** O(h) | **Space:** O(1)

---

### 65. [Implement Trie](https://leetcode.com/problems/implement-trie-prefix-tree/) [↩️](#index)
```python
class Trie:
    def __init__(self):
        self.root = {}
    
    def insert(self, word):
        node = self.root
        for c in word: node = node.setdefault(c, {})
        node['$'] = True
    
    def search(self, word):
        node = self._find(word)
        return node is not None and '$' in node
    
    def startsWith(self, prefix):
        return self._find(prefix) is not None
    
    def _find(self, prefix):
        node = self.root
        for c in prefix:
            if c not in node: return None
            node = node[c]
        return node
```
- **Time:** O(L) | **Space:** O(total chars)

---

### 66. [Add and Search Word](https://leetcode.com/problems/design-add-and-search-words-data-structure/) [↩️](#index)
```python
class WordDictionary:
    def __init__(self):
        self.root = {}
    
    def addWord(self, word):
        node = self.root
        for c in word: node = node.setdefault(c, {})
        node['$'] = True
    
    def search(self, word):
        def dfs(node, i):
            if i == len(word): return '$' in node
            if word[i] == '.':
                return any(dfs(child, i+1) for c, child in node.items() if c != '$')
            if word[i] in node: return dfs(node[word[i]], i+1)
            return False
        return dfs(self.root, 0)
```
- **Time:** O(L) add, O(26^L) search | **Space:** O(total chars)

---

### 67. [Word Search II](https://leetcode.com/problems/word-search-ii/) [↩️](#index)
```python
def findWords(board, words):
    trie = {}
    for w in words:
        node = trie
        for c in w: node = node.setdefault(c, {})
        node['$'] = w
    
    m, n, result = len(board), len(board[0]), set()
    def dfs(r, c, node):
        if r < 0 or c < 0 or r >= m or c >= n: return
        char = board[r][c]
        if char not in node: return
        next_node = node[char]
        if '$' in next_node: result.add(next_node['$'])
        board[r][c] = '#'
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]: dfs(r+dr, c+dc, next_node)
        board[r][c] = char
    
    for i in range(m):
        for j in range(n): dfs(i, j, trie)
    return list(result)
```
- **Time:** O(m × n × 4^L) | **Space:** O(total chars)

---

<a id="heap"></a>
## Heap [↩️](#index)

### 68. [Top K Frequent Elements](https://leetcode.com/problems/top-k-frequent-elements/) [↩️](#index)
```python
from collections import Counter
import heapq
def topKFrequent(nums, k):
    return heapq.nlargest(k, Counter(nums).keys(), key=Counter(nums).get)
```
- **Time:** O(n log k) | **Space:** O(n)

---

### 69. [Find Median from Data Stream](https://leetcode.com/problems/find-median-from-data-stream/) [↩️](#index)
```python
import heapq
class MedianFinder:
    def __init__(self):
        self.small = []  # Max heap
        self.large = []  # Min heap
    
    def addNum(self, num):
        heapq.heappush(self.small, -num)
        heapq.heappush(self.large, -heapq.heappop(self.small))
        if len(self.large) > len(self.small):
            heapq.heappush(self.small, -heapq.heappop(self.large))
    
    def findMedian(self):
        if len(self.small) > len(self.large):
            return -self.small[0]
        return (-self.small[0] + self.large[0]) / 2
```
- **Time:** O(log n) add, O(1) find | **Space:** O(n)

---

## Premium Problems (Outlines) [↩️](#index)

### [Alien Dictionary](https://leetcode.com/problems/alien-dictionary/) *(Premium)* [↩️](#index)
Topological sort on character ordering. **Time:** O(C) | **Space:** O(1)

### [Graph Valid Tree](https://leetcode.com/problems/graph-valid-tree/) *(Premium)* [↩️](#index)
Check edges = n-1 AND connected. **Time:** O(V+E) | **Space:** O(V)

### [Number of Connected Components](https://leetcode.com/problems/number-of-connected-components-in-an-undirected-graph/) *(Premium)* [↩️](#index)
Union-Find or DFS. **Time:** O(V+E) | **Space:** O(V)

### [Meeting Rooms](https://leetcode.com/problems/meeting-rooms/) *(Premium)* [↩️](#index)
Sort by start, check overlaps. **Time:** O(n log n) | **Space:** O(1)

### [Meeting Rooms II](https://leetcode.com/problems/meeting-rooms-ii/) *(Premium)* [↩️](#index)
Min heap of end times. **Time:** O(n log n) | **Space:** O(n)

### [Encode and Decode Strings](https://leetcode.com/problems/encode-and-decode-strings/) *(Premium)* [↩️](#index)
Length-prefixed: "5#hello". **Time:** O(n) | **Space:** O(n)
