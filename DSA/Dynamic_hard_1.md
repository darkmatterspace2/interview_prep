# Hard Dynamic Programming Interview Questions

These are the "Boss Level" problems. They require recognizing obscure patterns like **Interval DP**, **Bitmasking**, or combining **DP with Binary Search**.

## 1. Interval DP pattern
*Key Idea: Solving for every range `[i, j]` by splitting at some `k`.*

### A. Burst Balloons (LeetCode 312)
*Problem: Standard Matrix Chain Multiplication variant.*
*Complexity: O(N^3)*

```python
def maxCoins(nums: list[int]) -> int:
    # Handle edge cases (padding with 1s)
    nums = [1] + nums + [1]
    n = len(nums)
    # dp[i][j] = max coins obtained from range (i, j) EXCLUSIVE of i and j
    dp = [[0] * n for _ in range(n)]

    # Length of range from 2 to n
    for length in range(2, n):
        for left in range(n - length):
            right = left + length
            # Try every possible last balloon (k) to burst between left and right
            for k in range(left + 1, right):
                coins = nums[left] * nums[k] * nums[right]
                total = coins + dp[left][k] + dp[k][right]
                dp[left][right] = max(dp[left][right], total)
                
    return dp[0][n-1]
```

---

## 2. 2D String / Grid DP

### A. Edit Distance (LeetCode 72)
*Problem: Min operations (insert, delete, replace) to convert word1 to word2.*
*Complexity: O(M*N)*

```python
def minDistance(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    # dp[i][j] = min ops to convert word1[:i] to word2[:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0: dp[i][j] = j  # Need j insertions
            elif j == 0: dp[i][j] = i # Need i deletions
            elif word1[i-1] == word2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],    # Delete
                    dp[i][j-1],    # Insert
                    dp[i-1][j-1]   # Replace
                )
    return dp[m][n]
```

### B. Regular Expression Matching (LeetCode 10)
*Problem: Support `.` and `*` matching.*
*Key*: Handling the `*` (zero or more of preceding element) is tricky.
*Recurrence*: If `p[j] == '*'`, check `dp[i][j-2]` (zero occurrences) or `match and dp[i-1][j]` (one more occurrence).

---

## 3. Bitmask DP (Small Constraints N <= 20)

### A. Partition to K Equal Sum Subsets (LeetCode 698)
*Problem: Can array be split into K subsets of equal sum?*
*Complexity: O(K * 2^N)*

```python
def canPartitionKSubsets(nums: list[int], k: int) -> bool:
    total = sum(nums)
    if total % k != 0: return False
    target = total // k
    nums.sort(reverse=True) # Optimization
    memo = {}
    
    # mask: bitmask representing used numbers
    def backtrack(k_left, current_sum, mask):
        if k_left == 0: return True
        if current_sum == target:
            # Finished one subset, start next one
            return backtrack(k_left - 1, 0, mask)
        
        state = (k_left, mask)
        if state in memo: return memo[state]
        
        for i in range(len(nums)):
            # If ith bit is not set in mask
            if not (mask & (1 << i)):
                if current_sum + nums[i] <= target:
                    # Set ith bit
                    if backtrack(k_left, current_sum + nums[i], mask | (1 << i)):
                        return True
                        
        memo[state] = False
        return False

    return backtrack(k, 0, 0)
```

---

## 4. DP on Trees

### A. Binary Tree Maximum Path Sum (LeetCode 124)
*Problem: Path can start and end anywhere.*
*Key*: Post-order traversal. For each node, compute max path ending at that node (`node.val + max(left, right, 0)`), but update global max with `node.val + left + right`.

### B. Binary Tree Cameras (LeetCode 968)
*Problem: Min cameras to monitor all nodes.*
*States*: Return state from children: 0=Unmonitored, 1=Monitored (no cam), 2=Has Camera.

---

## 5. The "Top 10" Hard List Checklist

| Problem | Type | Key Concept |
| :--- | :--- | :--- |
| **Trapping Rain Water** | DP/Two Pointer | Prefix Max & Suffix Max |
| **Edit Distance** | 2D Grid | Insert/Delete/Replace ops |
| **Burst Balloons** | Interval DP | Last balloon burst idea |
| **Longest Increasing Path in Matrix** | DFS + Memo | DAG traversal on Grid |
| **Regular Expression Matching** | 2D String | Handling `*` state transitions |
| **Word Break II** | Backtracking + Memo | Reconstructing sentences |
| **Palindrome Partitioning II** | Interval/1D | Min cuts for Palindrome |
| **Wildcard Matching** | 2D String | Similar to Regex but `*` matches any sequence |
| **Serialize/Deserialize N-ary Tree** | Design/Tree | BFS Level order |
| **Super Egg Drop** | Optimised DP | Binary Search on Answer / Decision Tree |

## 6. How to tackle Hard DP in Interview?

1.  **Don't jump to DP**: Most "Hard" DPs look like Graph or Greedy problems first.
2.  **Constraints Clues**:
    *   `N <= 20`: Bitmask DP.
    *   `N <= 100`: O(N^3) or O(N^4) -> Interval DP.
    *   `N <= 1000`: O(N^2) -> 2D Grid DP.
    *   `N <= 10^5`: O(N) or O(N log N) -> 1D DP + Binary Search (LIS).
3.  **Space Optimization**: If `dp[i][j]` only depends on `dp[i-1]`, optimize to O(N) space. This often turns a "Hire" into "Strong Hire".
