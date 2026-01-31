# Haystack Needle
```python
class Solution:
    def strStr(self, haystack: str, needle: str) -> int:
        length = len(needle)
        for i in range(len(haystack) - length + 1):
            if haystack[i:i+length] == needle:
                return i
        return -1
```