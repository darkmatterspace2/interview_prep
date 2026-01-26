# Team Formation (Sliding Window)

## Problem Statement
Given an array `talents` of size `n` and an integer `talentsCount`. Each element in `talents` represents a talent type (from 1 to `talentsCount`).
For each starting position `i` (from 0 to `n-1`), find the minimum size of a subarray starting at `i` that contains all talents from 1 to `talentsCount`.
If no such subarray exists for a starting position, return -1.

**Example 1:**
- `talentsCount` = 3
- `talent` = `[1, 2, 3, 2, 1]`
- Output: `[3, 4, 3, -1, -1]`

**Constraints:**
- $1 \le n, \text{talentsCount} \le 10^5$
- $1 \le \text{talent}[i] \le \text{talentsCount}$

## Solution (Python)
This problem can be solved efficiently using the **Sliding Window (Two Pointers)** technique.

### Algorithm
1.  Initialize a frequency map `counts` to track the talents in the current window.
2.  Maintain a variable `missing` initialized to `talentsCount`.
3.  Use two pointers: `left` (start of window) and `right` (end of window).
4.  For each `left` from `0` to `n-1`:
    - Expand `right` until the window `[left, right]` contains all talents (`missing == 0`).
    - If valid, record the window size: `right - left`.
        - Note: `right` will be pointing to the element *after* the last included element because of the increment logic. So size is `right - left`.
    - If `right` reaches `n` and `missing > 0`, it's impossible to form valid teams for current and future `left` positions. Return `-1`.
    - Before incrementing `left`, remove `talent[left]` from the window. Update `counts` and `missing` accordingly.

### Complexity
-   **Time Complexity:** $O(N)$
    -   Both `left` and `right` pointers traverse the array at most once.
-   **Space Complexity:** $O(K)$ where $K$ is `talentsCount` (for the frequency map).

```python
def teamSize(talent, talentsCount):
    n = len(talent)
    counts = {}
    missing = talentsCount
    right = 0
    result = []
    
    # Pre-fill counts with 0 to avoid key errors if using dict, or use array if 1-based index
    # Using array is faster
    counts = [0] * (talentsCount + 1)
    
    for left in range(n):
        # Expand right as much as needed
        while right < n and missing > 0:
            current_talent = talent[right]
            if counts[current_talent] == 0:
                missing -= 1
            counts[current_talent] += 1
            right += 1
            
        # Check if we found a valid window
        if missing == 0:
            # right is now 1 past the last element of the valid window
            result.append(right - left)
        else:
            # We reached end of array and still missing talents
            result.append(-1)
            
        # Remove left element for next iteration
        left_talent = talent[left]
        counts[left_talent] -= 1
        if counts[left_talent] == 0:
            missing += 1
            
    return result

# Example Test Case
if __name__ == "__main__":
    t_count = 3
    talents = [1, 2, 3, 2, 1]
    print(teamSize(talents, t_count)) 
    # Output: [3, 4, 3, -1, -1]
```
