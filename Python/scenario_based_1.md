### **Round 2: Coding (Data Processing)**

**Context:**
You are processing a stream of user activity logs. Each log entry represents a "session" where a user was active, defined by a `start_time` and an `end_time`.

Often, these sessions overlap (e.g., a user has two tabs open). We want to consolidate these into continuous blocks of activity to calculate the true "active duration" of the user.

**The Problem:**
Given a list of intervals `[start, end]`, merge all overlapping intervals and return an array of the non-overlapping intervals that cover all the intervals in the input.

**Example:**

```python
# Input (List of lists)
intervals = [[1, 3], [2, 6], [8, 10], [15, 18]]

# Logic:
# [1, 3] and [2, 6] overlap. Merge them -> [1, 6]
# [8, 10] does not overlap with [1, 6]. Keep it.
# [15, 18] does not overlap. Keep it.

# Output
[[1, 6], [8, 10], [15, 18]]

```

**Constraints:**

* The input list is **not necessarily sorted**.
* `start <= end` is always true.

**(Please write your Python solution below.)**


```python
def merge_overlap_sessions(intervals: list[list[int]]) -> list[list[int]]:
    if not intervals:
        return []

    # 1. Sort by start time (Crucial Step)
    # Time Complexity: O(N log N)
    intervals.sort(key=lambda x: x[0])

    merged = [intervals[0]]

    for current in intervals[1:]:
        last_added = merged[-1]

        # 2. Check for overlap
        # If current start <= last end, they overlap
        if current[0] <= last_added[1]:
            # Merge: The new end is the max of both ends
            last_added[1] = max(last_added[1], current[1])
        else:
            # No overlap, just add it
            merged.append(current)

    return merged
```    