

```python
class Solution:
    def romanToInt(self, s: str) -> int:
        roman= {'I':1, 'V':5, 'X':10, 'L':50, 'C':100, 'D':500, 'M':1000}
        res=prev=0
        for curr in s:
            if roman[curr]> prev:
                res=res+roman[curr]-(2*prev)
            else:
                res=res+roman[curr]
            prev=roman[curr]
        return res
```