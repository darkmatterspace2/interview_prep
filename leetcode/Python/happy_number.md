# Happy Number


```python
class Solution:
    def isHappy(self, n: int) -> bool:
        seen = set()
        if n < 0:
            return False
        while n!=1:
            if n in seen:
                return False
            seen.add(n)
            res=0
            for ch in str(n):
                res=res+int(ch)**2
            n=res
        return True

                ``` 