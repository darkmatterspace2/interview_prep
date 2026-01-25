# FAANG DSA Guide (Round 2.2 - Problem Solving)

This guide focuses on the "Problem Solving & Data Structures" round (Round 2.2). The goal here is **thinking, approach, and correctness** (not just getting the right answer, but how you get there).

## 1. Top 7 Algorithm Patterns (The "Keys" to 90% of Problems)

Don't memorize problems; memorize patterns.

### 1. Sliding Window
*   **Use When**: Analyzing a contiguous subarray/substring of fixed size `K` or dynamic size based on condition.
*   **Keywords**: "Longest substring", "Max sum of subarray of size K".
*   **Time**: O(N) usually.

### 2. Two Pointers
*   **Use When**: Dealing with sorted arrays or finding pairs/triplets.
*   **Variants**:
    *   *Converging*: Left -> <- Right (e.g., Two Sum on sorted array, Palindrome check).
    *   *Slow/Fast*: Cycle detection in Linked List, Middle of Linked List.

### 3. Prefix Sum
*   **Use When**: Need sum of sub-ranges `(i, j)` frequently.
*   **Concept**: `P[i] = A[0] + ... + A[i]`. Sum(i, j) = `P[j] - P[i-1]`.
*   **Keywords**: "Sum of range", "Product of range".

### 4. Modified Binary Search
*   **Use When**: Searching in Sorted (or Rotated Sorted) arrays.
*   **Time**: O(log N).
*   **Key**: Identify the sorted half (if rotated) and decide which side to discard.

### 5. Top 'K' Elements (Heap)
*   **Use When**: Finding "Largest K", "Smallest K", "Most Frequent K".
*   **Tool**: Priority Queue (Min-Heap for largest K, Max-Heap for smallest K).
*   **Time**: O(N log K) is better than sorting O(N log N).

### 6. Depth First Search (DFS) & Backtracking
*   **Use When**: Tree traversal, generating all combinations/permutations, solving maze/sudoku.
*   **Concept**: Go deep, hit base case, backtrack.

### 7. Breadth First Search (BFS)
*   **Use When**: Shortest path in unweighted graph/grid, Level-order traversal of Tree.
*   **Tool**: Queue.

---

## 2. Essential Data Structures

Know the **internal workings** and **time complexity** of these.

| Structure | Access | Search | Insert | Delete | Use Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Array** | O(1) | O(N) | O(N) | O(N) | Simple storage, indices |
| **Stack** | O(N) | O(N) | O(1) | O(1) | Recursion, undo, parenthesis |
| **Queue** | O(N) | O(N) | O(1) | O(1) | BFS, job scheduling |
| **HashMap** | N/A | O(1)* | O(1)* | O(1)* | Counting Freq, caching |
| **BST** | O(log N) | O(log N) | O(log N) | O(log N) | Sorted data, ranges |
| **Heap** | O(1) min/max | O(N) | O(log N) | O(log N) | Priority tasks |

*\*Amortized*

---

## 3. Flipkart/FAANG Specific Checklist

### A. Arrays & Strings
*   [ ] **Kadane's Algorithm**: Max contiguous subarray sum.
*   [ ] **Dutch National Flag**: Sort 0s, 1s, 2s (or Red/White/Blue).
*   [ ] **Trapping Rain Water**: Classic hard problem (Prefix/Suffix max or Two Pointers).

### B. Hashing & Maps
*   [ ] **LRU Cache**: Design using HashMap + Doubly Linked List. (Very frequent).
*   [ ] **Group Anagrams**: Map `{sorted_string -> list_of_strings}`.

### C. Trees & Graphs
*   [ ] **Lowest Common Ancestor (LCA)**: Recursion logic.
*   [ ] **Level Order Traversal**: Queue based BFS.
*   [ ] **Number of Islands**: Grid DFS/BFS.
*   [ ] **Course Schedule**: Graph topological sort (Kahn's algo or DFS cycle detection).

### D. Dynamic Programming (DP)
*   *Don't panic on DP. Focus on 1D DP first.*
*   [ ] **Climbing Stairs**: Fibonacci simple.
*   [ ] **Coin Change**: Unbounded Knapsack pattern.
*   [ ] **Longest Common Subsequence (LCS)**: String matching foundation.

---

## 4. The "Interview Protocol" (How to Pass)

1.  **Clarify**: "Does the array contain negatives?", "Is memory a constraint?".
2.  **Brute Force First**: "I can solve this in O(N^2) using nested loops. Shall I optimize?". -> Shows you have a baseline.
3.  **Optimize**: "We can bring this down to O(N) using a HashMap".
4.  **Dry Run**: Walk through your code with a sample case *before* the interviewer asks.
5.  **Complexity**: Always state Time AND Space complexity at the end.

## 5. Common "Gotchas" / Edge Cases

*   **Empty Input**: Array is null or length 0.
*   **Single Element**: Array has 1 item.
*   **Duplicates**: All elements are the same.
*   **Integer Overflow**: Sum exceeds `Integer.MAX_VALUE` (Use Long).
*   **Case Sensitivity**: In string problems.
