
```python
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        sum = sec=0
        res=[]
        for i in range(len(nums)-1): 
            sec=i+1
            while sec <=len(nums)-1:
                if nums[i]+nums[sec] != target:
                    sec+=1
                elif nums[i]+nums[sec] == target:
                    res.append(i)
                    res.append(sec)
                    return res
                
```            
