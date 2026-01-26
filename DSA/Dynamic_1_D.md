# 1D Dynamic Programming in Python

1D DP is the starting point for mastering Dynamic Programming. It usually involves an array (or list) where `dp[i]` depends on previous values like `dp[i-1]`, `dp[i-2]`, etc.

## 1. The Core Concepts

*   **State**: What defines the subproblem? (usually index `i`).
*   **Transition**: How do we get `dp[i]` from previous states? (e.g., `dp[i] = dp[i-1] + dp[i-2]`).
*   **Base Case**: The smallest subproblem (e.g., `dp[0] = 0`).

### Memoization (Top-Down) vs Tabulation (Bottom-Up)

**Problem: Fibonacci (Nth Number)**

```python
# 1. Memoization (Recursive + Cache)
memo = {}
def fib_memo(n):
    if n <= 1: return n
    if n in memo: return memo[n]
    memo[n] = fib_memo(n-1) + fib_memo(n-2)
    return memo[n]

# 2. Tabulation (Iterative + Array)
def fib_tab(n):
    if n <= 1: return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]

# 3. Space Optimized (Iterative + Variables) -> PREFERRED
def fib_opt(n):
    if n <= 1: return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
```

---

## 2. Key LeetCode Patterns (1D)

### Pattern 1: Choices at each Step (House Robber)
*Problem: Rob houses, but can't rob two adjacent ones. Maximize money.*
*Recurrence: `rob(i) = max(rob(i-1), arr[i] + rob(i-2))`*

```python
def rob(nums: list[int]) -> int:
    if not nums: return 0
    
    # prev1 is dp[i-1], prev2 is dp[i-2]
    prev2, prev1 = 0, 0
    
    for val in nums:
        # Choice: Skip current (prev1) OR Rob current (val + prev2)
        current = max(prev1, val + prev2)
        prev2 = prev1
        prev1 = current
        
    return prev1
```

### Pattern 2: Climbing Stairs (Distinct Ways)
*Problem: Climb N stairs, taking 1 or 2 steps at a time.*
*Same as Fibonacci.*

### Pattern 3: Longest Increasing Subsequence (LIS)
*Problem: Find length of longest subsequence where elements strictly increase.*
*Time: O(N^2) (Standard DP) | O(N log N) (Binary Search variant also exists)*

```python
def lengthOfLIS(nums: list[int]) -> int:
    if not nums: return 0
    
    # dp[i] = length of LIS ending at index i
    dp = [1] * len(nums)
    
    for i in range(len(nums)):
        for j in range(i):
            if nums[i] > nums[j]:
                dp[i] = max(dp[i], dp[j] + 1)
                
    return max(dp)
```

### Pattern 4: Word Break
*Problem: Can string `s` be segmented into dictionary words?*
*Recurrence: `dp[i]` is True if `dp[j]` is True AND `s[j:i]` is in dict.*

```python
def wordBreak(s: str, wordDict: list[str]) -> bool:
    word_set = set(wordDict) # O(1) lookup
    dp = [False] * (len(s) + 1)
    dp[0] = True # Empty string is valid
    
    for i in range(1, len(s) + 1):
        for j in range(i):
            # If substring s[0:j] is valid AND s[j:i] is a word
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break # Found a valid split for i, stop checking j
                
    return dp[len(s)]
```

### Pattern 5: Coin Change (Min Coins)
*Problem: Min coins to make amount `X`.*
*Recurrence: `dp[amount] = min(dp[amount - coin]) + 1`*

```python
def coinChange(coins: list[int], amount: int) -> int:
    # Initialize with value > amount (as infinity)
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    
    for i in range(1, amount + 1):
        for coin in coins:
            if i - coin >= 0:
                dp[i] = min(dp[i], dp[i - coin] + 1)
                
    return dp[amount] if dp[amount] != float('inf') else -1
```

---

## 3. Top 1D DP Problems Checklist

| Problem | Difficulty | Logic |
| :--- | :--- | :--- |
| **Climbing Stairs** | Easy | Fibonacci |
| **Min Cost Climbing Stairs** | Easy | `min(cost[i-1], cost[i-2]) + cost[i]` |
| **House Robber** | Medium | `max(dp[i-1], val + dp[i-2])` |
| **Coin Change** | Medium | Knapsack-like (Unbounded) |
| **Word Break** | Medium | Check all split points |
| **Longest Increasing Subsequence** | Medium | O(N^2) Nested Loop |
| **Maximum Product Subarray** | Medium | Track Min & Max (due to negatives) |
| **Decode Ways** | Medium | Check 1-digit & 2-digit validity |

## 4. How to think in DP? (The "Framework")
1.  **Define Objective**: Maximize profit, minimize cost, count ways.
2.  **Decide State**: What changes? (Index `i`, Amount remaining).
3.  **Find Transition**: If I am at `i`, what were my choices to get here? 
4.  **Base Case**: When do I stop? (`i < 0`, `amount == 0`).
