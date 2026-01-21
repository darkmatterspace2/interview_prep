# Coding Interview Patterns Cheat Sheet

A quick reference guide for identifying which coding pattern to use based on problem characteristics.

## 1. Sliding Window
**When to use:**
- Input is a linear data structure (Array, String, Linked List).
- You need to calculate something for a **contiguous** subarray or substring.
- You are asked to find the longest/shortest substring, subarray, or specific target value.
- keywords: "maximum sum subarray of size 'K'", "longest substring with 'K' distinct characters".

**Why:** Avoids re-calculating the overlapping part of the window, reducing time complexity from O(N*K) to O(N).

**Common Problems:**
- Maximum Sum Subarray of Size K
- Longest Substring with K Distinct Characters
- String Anagrams
- Minimum Window Substring

## 2. Two Pointers
**When to use:**
- Input is a **sorted** array or linked list (usually).
- You need to find a set of elements that fulfill certain constraints (e.g., sum to a target).
- You are trying to find a pair, triplet, or subarray.
- Palindrome checks (checking edges moving inwards).

**Why:** Reduces nested loop complexity (O(N^2)) to linear time (O(N)) by processing elements from ends or different speeds.

**Common Problems:**
- Pair with Target Sum
- Remove Duplicates from Sorted Array
- Squaring a Sorted Array
- 3Sum, 4Sum, Dutch National Flag Problem
- Valid Palindrome

## 3. Fast & Slow Pointers (Tortoise and Hare)
**When to use:**
- The data structure is linear (Array, Linked List).
- You need to detect a **cycle** or find the middle element.
- You need to find the start of a cycle.

**Why:** Efficiently detects cycles and finds midpoints in a single pass with O(1) space, unlike using a Set/Map.

**Common Problems:**
- LinkedList Cycle
- Middle of the LinkedList
- Start of LinkedList Cycle
- Happy Number

## 4. Merge Intervals
**When to use:**
- You are given a set of intervals (start, end) or time ranges.
- You need to find overlapping intervals, merge them, or find gaps.
- Keywords: "overlapping", "merge", "interval", "meeting times".

**Common Problems:**
- Merge Intervals
- Insert Interval
- Intervals Intersection
- Conflicting Appointments / Meeting Rooms

## 5. Cyclic Sort
**When to use:**
- Input is an array containing numbers in a **given range** (e.g., 1 to N, 0 to N).
- You need to find missing, duplicate, or corrupted numbers in that range.
- You want O(N) time and O(1) space.

**Common Problems:**
- Cyclic Sort
- Find the Missing Number
- Find all Disappeared Numbers
- Find the Duplicate Number
- Set Mismatch

## 6. In-place Reversal of a Linked List
**When to use:**
- You need to reverse a Linked List (or a sub-part of it).
- Constraint: Do it in-place (O(1) space).

**Common Problems:**
- Reverse a Linked List
- Reverse a Sub-list
- Reverse every K-element Sub-list

## 7. Tree BFS (Breadth-First Search)
**When to use:**
- You need to traverse a tree level-by-level (level order traversal).
- You need to find the shortest path in an unweighted graph/tree.
- Problems asking for "levels", "averages of levels", or "connect nodes at same level".

**Technique:** Use a **Queue**.

**Common Problems:**
- Binary Tree Level Order Traversal
- Reverse Level Order Traversal
- Zigzag Traversal
- Level Averages in a Binary Tree
- Minimum Depth of a Binary Tree

## 8. Tree DFS (Depth-First Search)
**When to use:**
- You need to explore as deep as possible before backtracking.
- You need to search for a node that is likely far from the root or requires visiting all nodes (like tree path sums).
- In-order, Pre-order, Post-order traversals.

**Technique:** Use Recursion or a **Stack**.

**Common Problems:**
- Path Sum (I, II, III)
- Sum of Path Numbers
- Count Paths for a Sum
- Diameter of Binary Tree

## 9. Two Heaps
**When to use:**
- You need to divide a set of numbers into two parts (e.g., smaller half and larger half) to find the **median** or other order statistics dynamically.
- Priority Queue scheduling problems (Min-heap for one, Max-heap for other).

**Common Problems:**
- Find the Median of a Number Stream
- Sliding Window Median
- Maximize Capital

## 10. Subsets (Backtracking / BFS)
**When to use:**
- You need to find all **permutations**, **combinations**, or **subsets** of a set.
- The input size is generally small (since these are exponential algorithms).

**Common Problems:**
- Subsets / Subsets II
- Permutations
- Letter Case Permutation
- Generate Parentheses

## 11. Modified Binary Search
**When to use:**
- Input is a **sorted** array (or almost sorted / rotated sorted).
- You need to find a target value, an insertion position, or a boundary.
- Time complexity constraint is O(log N).

**Common Problems:**
- Order-agnostic Binary Search
- Ceiling of a Number
- Next Letter
- Search in a Sorted Infinite Array
- Search in Rotated Sorted Array

## 12. Top 'K' Elements
**When to use:**
- You need to find the top/smallest/most frequent 'K' elements.
- Keywords: "top K", "smallest K", "most frequent".

**Technique:** Use a **Heap** (Min-Heap for top K largest, Max-Heap for top K smallest).

**Common Problems:**
- Top K Frequent Elements
- Kth Largest Element in a Stream
- 'K' Closest Points to the Origin
- Connect Ropes

## 13. K-way Merge
**When to use:**
- You have 'K' sorted arrays, linked lists, or matrices and you need to merge them or find the specific element in the combined sorted order.

**Technique:** Use a **Min-Heap** to keep track of the smallest element from each of the K structures.

**Common Problems:**
- Merge K Sorted Lists
- Kth Smallest Number in M Sorted Lists
- Smallest Number Range

## 14. Topological Sort (Graph)
**When to use:**
- The problem deals with tasks that have **dependencies**.
- You need to order nodes in a Directed Acyclic Graph (DAG) such that for every directed edge U -> V, node U comes before V.
- Keywords: "prerequisites", "scheduling", "course schedule".

**Common Problems:**
- Task Scheduling / Course Schedule
- Alien Dictionary
- All Tasks Scheduling Orders

## 15. Dynamic Programming (DP)
**When to use:**
- The problem has **overlapping subproblems** and **optimal substructure**.
- You are asked for a maximum/minimum result, or the number of ways to do something.
- "Optimization" problems.

**Technique:** Memoization (Top-Down) or Tabulation (Bottom-Up).

**Common Problems:**
- 0/1 Knapsack
- Unbounded Knapsack
- Fibonacci Numbers
- Longest Common Subsequence
- Longest Palindromic Subsequence

## 16. Hash Maps
**When to use:**
- You need direct access to data (O(1) lookup).
- You need to track frequencies or pair elements.
- Often used in conjunction with other patterns (e.g., Two Sum with Map, Sliding Window with Map).

**Common Problems:**
- Two Sum
- Isomorphic Strings
- Longest Palindrome

## 17. Monotonic Stack
**When to use:**
- You need to find the "next greater" or "next smaller" element for every element in an array.
- Optimizing nested loops that look for nearest values.

**Common Problems:**
- Next Greater Element
- Daily Temperatures
- Largest Rectangle in Histogram
