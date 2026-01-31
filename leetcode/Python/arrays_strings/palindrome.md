# Palindrome

```python
class Solution:
    def isPalindrome(self, x: int) -> bool:
        l=r=0
        y=str(x)
        if x < 0:
            return False
        elif y==y[::-1]:
            return True
        return False
```   

# solution 2
```python
def is_palindrome_num(x: int) -> bool:
    if x < 0:
        return False

    original = x
    rev = 0

    while x > 0:
        rev = rev * 10 + x % 10
        x //= 10

    return original == rev
```
