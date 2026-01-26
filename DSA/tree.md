# Binary Trees in Python

Binary Trees are hierarchical data structures. Most problems are solved using **Recursion** (DFS) or **Queue** (BFS).

## 1. Basic Structure

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
```

---

## 2. Traversals (The "Hello World" of Trees)

### A. Depth First Search (DFS)
*Go deep first. Uses Recursion or Stack.*

```python
# 1. Preorder (Root -> Left -> Right)
def preorder(root):
    if not root: return
    print(root.val)
    preorder(root.left)
    preorder(root.right)

# 2. Inorder (Left -> Root -> Right) - Sorted order for BST
def inorder(root):
    if not root: return
    inorder(root.left)
    print(root.val)
    inorder(root.right)

# 3. Postorder (Left -> Right -> Root) - Bottom-up logic
def postorder(root):
    if not root: return
    postorder(root.left)
    postorder(root.right)
    print(root.val)
```

### B. Breadth First Search (BFS) / Level Order
*Go level by level. Uses Queue.*

```python
from collections import deque

def levelOrder(root: TreeNode) -> list[list[int]]:
    if not root: return []
    res = []
    queue = deque([root])
    
    while queue:
        level_size = len(queue)
        current_level = []
        
        for _ in range(level_size):
            node = queue.popleft()
            current_level.append(node.val)
            if node.left: queue.append(node.left)
            if node.right: queue.append(node.right)
            
        res.append(current_level)
    return res
```

---

## 3. Key Patterns & Tricks

### Pattern 1: Maximum Depth (Height)
*Logic: 1 + max(left, right)*

```python
def maxDepth(root: TreeNode) -> int:
    if not root: return 0
    return 1 + max(maxDepth(root.left), maxDepth(root.right))
```

### Pattern 2: Validate BST
*Logic: Keep track of valid range (min, max) for each node.*

```python
def isValidBST(root: TreeNode) -> bool:
    def validate(node, low, high):
        if not node: return True
        if not (low < node.val < high):
            return False
        return (validate(node.left, low, node.val) and 
                validate(node.right, node.val, high))
                
    return validate(root, float('-inf'), float('inf'))
```

### Pattern 3: Lowest Common Ancestor (LCA)
*Logic: Where do paths to p and q diverge?*

```python
def lowestCommonAncestor(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
    if not root or root == p or root == q:
        return root
        
    left = lowestCommonAncestor(root.left, p, q)
    right = lowestCommonAncestor(root.right, p, q)
    
    if left and right: return root  # Found one in left, one in right
    return left if left else right  # Return non-null child
```

### Pattern 4: Path Sum
*Logic: Subtract val from target as you go down. Check leaf.*

```python
def hasPathSum(root: TreeNode, targetSum: int) -> bool:
    if not root: return False
    
    if not root.left and not root.right: # Leaf check
        return targetSum == root.val
        
    return (hasPathSum(root.left, targetSum - root.val) or 
            hasPathSum(root.right, targetSum - root.val))
```

---

## 4. Top Tree Problems Checklist

| Problem | Difficulty | Key |
| :--- | :--- | :--- |
| **Max Depth of Binary Tree** | Easy | DFS / BFS |
| **Invert Binary Tree** | Easy | Swap left/right recursively |
| **Same Tree / Symmetric Tree** | Easy | Compare nodes structurally |
| **Level Order Traversal** | Medium | Queue (BFS) |
| **Binary Tree Right Side View** | Medium | BFS (Last item) or DFS (Root-Right-Left) |
| **Validate BST** | Medium | Ranges (min, max) |
| **Lowest Common Ancestor** | Medium | Post-order logic |
| **Serialize & Deserialize** | Hard | Preorder + Queue |
| **Max Path Sum** | Hard | Global variable update |

## 5. Common "Gotchas"
1.  **Base Case**: Always check `if not root: return ...`.
2.  **BST Properties**: Left < Node < Right. (Don't just check immediate children, check whole subtree ranges).
3.  **Leaf Nodes**: Some problems only trigger logic at leaves (e.g., Path Sum). Identify leaves with `not node.left and not node.right`.
