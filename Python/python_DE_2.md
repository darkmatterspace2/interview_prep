# Python Cheatsheet: Strings, Lists, Dicts, Tuples

> **Beginner-friendly guide** with input/output examples and step-by-step explanations

---

<a id="top"></a>
## 📑 Table of Contents
| # | Section |
|---|---------|
| 1 | [Dictionary (HashMap) Basics](#1-dictionary-hashmap-basics) |
| 2 | [List of Dictionaries](#2-list-of-dictionaries) |
| 3 | [List of Tuples](#3-list-of-tuples) |
| 4 | [Sorting Techniques](#4-sorting-techniques) |
| 5 | [Counter & Frequency](#5-counter--frequency) |
| 6 | [Dict Hacks & Tips](#6-dict-hacks--tips) |
| 7 | [String Manipulation](#7-string-manipulation) |
| 8 | [Extracting Info from Data](#8-extracting-info-from-data) |

---

## 1. Dictionary (HashMap) Basics [↩️](#top)

### Create a Dictionary
```python
# Empty dict
my_dict = {}
my_dict = dict()

# With values
my_dict = {"name": "Alice", "age": 25}
```

### Add / Update Elements
```python
my_dict = {"name": "Alice"}

# Add new key
my_dict["city"] = "NYC"
# Output: {"name": "Alice", "city": "NYC"}

# Update existing key
my_dict["name"] = "Bob"
# Output: {"name": "Bob", "city": "NYC"}

# Update multiple keys at once
my_dict.update({"age": 30, "city": "LA"})
# Output: {"name": "Bob", "city": "LA", "age": 30}
```

### Remove Elements
```python
my_dict = {"a": 1, "b": 2, "c": 3}

# Remove specific key (returns value)
val = my_dict.pop("b")
# val = 2, my_dict = {"a": 1, "c": 3}

# Remove with default (no error if missing)
val = my_dict.pop("z", None)
# val = None, dict unchanged

# Delete key (no return)
del my_dict["a"]
# my_dict = {"c": 3}

# Clear all
my_dict.clear()
# my_dict = {}
```

### Search / Access Elements
```python
my_dict = {"name": "Alice", "age": 25}

# Direct access (raises KeyError if missing)
name = my_dict["name"]  # "Alice"

# Safe access with .get() (returns None if missing)
city = my_dict.get("city")  # None
city = my_dict.get("city", "Unknown")  # "Unknown"

# Check if key exists
if "name" in my_dict:
    print("Found!")
```

### Loop Through Dictionary
```python
my_dict = {"a": 1, "b": 2, "c": 3}

# Keys only
for key in my_dict:
    print(key)  # a, b, c

# Keys and values
for key, value in my_dict.items():
    print(f"{key}: {value}")  # a: 1, b: 2, c: 3

# Values only
for value in my_dict.values():
    print(value)  # 1, 2, 3
```

---

## 2. List of Dictionaries [↩️](#top)

### Create
```python
users = [
    {"name": "Alice", "age": 25},
    {"name": "Bob", "age": 30},
    {"name": "Charlie", "age": 25}
]
```

### Add Element
```python
users.append({"name": "Dave", "age": 35})
```

### Update Element
```python
# Update first user's age
users[0]["age"] = 26

# Update by searching
for user in users:
    if user["name"] == "Bob":
        user["age"] = 31
```

### Remove Element
```python
# Remove by index
users.pop(0)

# Remove by condition
users = [u for u in users if u["name"] != "Bob"]
```

### Search / Filter
```python
# Find one
alice = next((u for u in users if u["name"] == "Alice"), None)

# Filter many
young_users = [u for u in users if u["age"] < 30]
```

### Example: Group Anagrams [↩️](#top)
```python
# Input
strs = ["eat", "tea", "tan", "ate", "nat", "bat"]

# Step 1: Create dict to group by sorted letters
groups = {}

# Step 2: Loop through each word
for word in strs:
    # Sort letters: "eat" -> "aet", "tea" -> "aet"
    key = "".join(sorted(word))
    
    # Add to group
    if key not in groups:
        groups[key] = []
    groups[key].append(word)

# Step 3: Get the grouped values
result = list(groups.values())

# Output: [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]
```

**One-liner version:**
```python
from collections import defaultdict
groups = defaultdict(list)
for word in strs:
    groups["".join(sorted(word))].append(word)
result = list(groups.values())
```

---

## 3. List of Tuples [↩️](#top)

### Create
```python
data = [
    ("HR", "Alice", 5000),
    ("IT", "Bob", 8000),
    ("HR", "Charlie", 6000)
]
```

### Add Element
```python
data.append(("Sales", "Dave", 7000))
```

### Access Elements
```python
# Tuples are immutable, but you can access
first_record = data[0]  # ("HR", "Alice", 5000)
dept = data[0][0]  # "HR"

# Unpack in loop
for dept, name, salary in data:
    print(f"{name} works in {dept}")
```

### Update (Create New Tuple)
```python
# Tuples are immutable, so create new one
old = ("HR", "Alice", 5000)
new = (old[0], old[1], 6000)  # Update salary
# Or
new = (*old[:2], 6000)
```

### Remove Element
```python
data.pop(0)  # Remove first
data = [t for t in data if t[1] != "Bob"]  # Remove Bob
```

### Search / Filter
```python
# Find IT employees
it_staff = [t for t in data if t[0] == "IT"]

# Find high earners
high_earners = [t for t in data if t[2] > 6000]
```

### Group by Department [↩️](#top)
```python
data = [
    ("HR", "Alice", 5000), ("IT", "Bob", 8000), ("HR", "Charlie", 6000),
    ("IT", "Dave", 9000), ("IT", "Eve", 7000), ("HR", "Frank", 4000)
]

# Step 1: Create empty dict for groups
by_dept = {}

# Step 2: Loop and group
for dept, name, salary in data:
    if dept not in by_dept:
        by_dept[dept] = []
    by_dept[dept].append((name, salary))

# Output: {'HR': [('Alice', 5000), ('Charlie', 6000), ('Frank', 4000)], 
#          'IT': [('Bob', 8000), ('Dave', 9000), ('Eve', 7000)]}
```

---

## 4. Sorting Techniques [↩️](#top)

### Sort List
```python
nums = [3, 1, 4, 1, 5]

# In-place sort (modifies original)
nums.sort()  # [1, 1, 3, 4, 5]

# Descending
nums.sort(reverse=True)  # [5, 4, 3, 1, 1]

# Create new sorted list
sorted_nums = sorted(nums)
```

### Sort List of Tuples
```python
data = [("Alice", 30), ("Bob", 25), ("Charlie", 35)]

# Sort by second element (age) ASCENDING
data.sort(key=lambda x: x[1])
# [('Bob', 25), ('Alice', 30), ('Charlie', 35)]

# Sort by second element DESCENDING
data.sort(key=lambda x: x[1], reverse=True)
# [('Charlie', 35), ('Alice', 30), ('Bob', 25)]

# Sort by name (alphabetically)
data.sort(key=lambda x: x[0])
```

### Sort List of Dicts
```python
users = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 35}
]

# Sort by age ascending
users.sort(key=lambda x: x["age"])

# Sort by age descending
users.sort(key=lambda x: x["age"], reverse=True)

# Sort by name
users.sort(key=lambda x: x["name"])
```

### Top N by Group [↩️](#top)
```python
data = [
    ("HR", "Alice", 5000), ("IT", "Bob", 8000), ("HR", "Charlie", 6000),
    ("IT", "Dave", 9000), ("IT", "Eve", 7000), ("HR", "Frank", 4000)
]

# Step 1: Group by department
by_dept = {}
for dept, name, salary in data:
    if dept not in by_dept:
        by_dept[dept] = []
    by_dept[dept].append((name, salary))

# Step 2: Sort each group and take top 2
top_2 = {}
for dept, staff in by_dept.items():
    staff.sort(key=lambda x: x[1], reverse=True)  # Sort by salary DESC
    top_2[dept] = staff[:2]  # Take top 2

# Output: {'HR': [('Charlie', 6000), ('Alice', 5000)], 
#          'IT': [('Dave', 9000), ('Bob', 8000)]}
```

---

## 5. Counter & Frequency [↩️](#top)

### Basic Counter
```python
from collections import Counter

# Count items
items = ["apple", "banana", "apple", "cherry", "banana", "apple"]
counts = Counter(items)
# Counter({'apple': 3, 'banana': 2, 'cherry': 1})

# Access count
print(counts["apple"])  # 3
print(counts["mango"])  # 0 (no error!)

# Most common
print(counts.most_common(2))  # [('apple', 3), ('banana', 2)]
```

### Manual Counting (Without Counter)
```python
items = ["apple", "banana", "apple", "cherry"]

# Method 1: Using dict.get()
counts = {}
for item in items:
    counts[item] = counts.get(item, 0) + 1
# {'apple': 2, 'banana': 1, 'cherry': 1}

# Method 2: Using setdefault
counts = {}
for item in items:
    counts.setdefault(item, 0)
    counts[item] += 1
```

### Count Characters in String
```python
text = "hello"
char_count = Counter(text)
# Counter({'l': 2, 'h': 1, 'e': 1, 'o': 1})
```

### Count Words
```python
sentence = "the quick brown fox jumps over the lazy dog the"
words = sentence.split()
word_count = Counter(words)
# Counter({'the': 3, 'quick': 1, ...})
```

---

## 6. Dict Hacks & Tips [↩️](#top)

### setdefault (Initialize if missing)
```python
# Without setdefault
groups = {}
for item in items:
    if key not in groups:
        groups[key] = []
    groups[key].append(item)

# With setdefault (cleaner)
groups = {}
for key, item in data:
    groups.setdefault(key, []).append(item)
```

### defaultdict (Auto-initialize)
```python
from collections import defaultdict

# List as default
groups = defaultdict(list)
groups["key"].append("value")  # No KeyError!

# Int as default (for counting)
counts = defaultdict(int)
counts["apple"] += 1  # No KeyError!

# Set as default
unique_items = defaultdict(set)
unique_items["key"].add("value")
```

### dict.get() with Default
```python
config = {"debug": True}

# Bad: raises KeyError
# level = config["log_level"]

# Good: returns default
level = config.get("log_level", "INFO")  # "INFO"
```

### Merge Dictionaries
```python
dict1 = {"a": 1, "b": 2}
dict2 = {"b": 3, "c": 4}

# Python 3.9+
merged = dict1 | dict2
# {"a": 1, "b": 3, "c": 4}

# Python 3.5+
merged = {**dict1, **dict2}
```

### Dict Comprehension
```python
# Create from list
names = ["Alice", "Bob", "Charlie"]
name_lengths = {name: len(name) for name in names}
# {"Alice": 5, "Bob": 3, "Charlie": 7}

# Filter dict
scores = {"Alice": 85, "Bob": 92, "Charlie": 78}
passed = {k: v for k, v in scores.items() if v >= 80}
# {"Alice": 85, "Bob": 92}

# Transform values
doubled = {k: v * 2 for k, v in scores.items()}
```

### Invert Dictionary (Swap keys and values)
```python
original = {"a": 1, "b": 2, "c": 3}
inverted = {v: k for k, v in original.items()}
# {1: "a", 2: "b", 3: "c"}
```

---

## 7. String Manipulation [↩️](#top)

### Basic Operations
```python
s = "  Hello World  "

s.strip()      # "Hello World" (remove spaces)
s.lower()      # "  hello world  "
s.upper()      # "  HELLO WORLD  "
s.title()      # "  Hello World  "
s.replace("o", "0")  # "  Hell0 W0rld  "
```

### Split and Join
```python
# Split into list
s = "apple,banana,cherry"
items = s.split(",")  # ["apple", "banana", "cherry"]

# Split with limit
s = "a:b:c:d"
parts = s.split(":", 2)  # ["a", "b", "c:d"]

# Join list into string
items = ["apple", "banana", "cherry"]
joined = ",".join(items)  # "apple,banana,cherry"
```

### Slicing
```python
s = "Hello World"

s[0]      # "H" (first char)
s[-1]     # "d" (last char)
s[0:5]    # "Hello" (first 5)
s[6:]     # "World" (from index 6)
s[:-3]    # "Hello Wo" (except last 3)
s[::-1]   # "dlroW olleH" (reverse)
```

### Replace at Position
```python
s = "Hello World"

# Replace char at index 6
s = s[:6] + "P" + s[7:]  # "Hello Porld"

# Insert at position
s = s[:5] + " Beautiful" + s[5:]  # "Hello Beautiful World"
```

### Masking Strings (PII Protection) [↩️](#top)
```python
# Mask email: geek123@gmail.com -> g*****3@gmail.com
def mask_email(email):
    local, domain = email.split("@")
    if len(local) <= 2:
        masked = local[0] + "*"
    else:
        masked = local[0] + "*" * (len(local) - 2) + local[-1]
    return f"{masked}@{domain}"

mask_email("geek123@gmail.com")  # "g*****3@gmail.com"

# Mask phone: 1234567890 -> ******7890
def mask_phone(phone):
    return "*" * (len(phone) - 4) + phone[-4:]

mask_phone("1234567890")  # "******7890"

# Mask credit card: 1234567812345678 -> ****-****-****-5678
def mask_card(card):
    return "****-****-****-" + card[-4:]
```

### String Formatting
```python
name = "Alice"
age = 25

# f-string (Python 3.6+)
msg = f"Name: {name}, Age: {age}"

# format()
msg = "Name: {}, Age: {}".format(name, age)

# Padding
num = 42
f"{num:05d}"   # "00042" (pad with zeros)
f"{num:>10}"   # "        42" (right align)
f"{num:<10}"   # "42        " (left align)
```

---

## 8. Extracting Info from Data [↩️](#top)

### Parse Log Lines
```python
log = "2026-02-08 10:30:45 ERROR User login failed for user_123"

# Split by space
parts = log.split(" ")
date = parts[0]  # "2026-02-08"
time = parts[1]  # "10:30:45"
level = parts[2] # "ERROR"
message = " ".join(parts[3:])  # "User login failed for user_123"
```

### Extract with Regex
```python
import re

# Extract email
text = "Contact us at support@example.com or sales@test.org"
emails = re.findall(r'[\w.-]+@[\w.-]+', text)
# ["support@example.com", "sales@test.org"]

# Extract numbers
text = "Price: $123.45 and $67.89"
prices = re.findall(r'\d+\.\d+', text)
# ["123.45", "67.89"]

# Extract date
text = "Created on 2026-02-08"
dates = re.findall(r'\d{4}-\d{2}-\d{2}', text)
# ["2026-02-08"]

# Extract IP address
log = "Request from 192.168.1.100 at port 8080"
ips = re.findall(r'\d+\.\d+\.\d+\.\d+', log)
# ["192.168.1.100"]
```

### Parse URLs
```python
from urllib.parse import urlparse, parse_qs

url = "https://shop.com/product?id=123&utm_source=google"

parsed = urlparse(url)
print(parsed.scheme)    # "https"
print(parsed.netloc)    # "shop.com"
print(parsed.path)      # "/product"

params = parse_qs(parsed.query)
print(params["id"])           # ["123"]
print(params["utm_source"])   # ["google"]
```

### Extract from List of Dicts [↩️](#top)
```python
users = [
    {"name": "Alice", "email": "alice@test.com", "age": 25},
    {"name": "Bob", "email": "bob@test.com", "age": 30},
    {"name": "Charlie", "email": "charlie@test.com", "age": 35}
]

# Get all names
names = [u["name"] for u in users]
# ["Alice", "Bob", "Charlie"]

# Get all emails
emails = [u["email"] for u in users]

# Filter and extract
over_25_names = [u["name"] for u in users if u["age"] > 25]
# ["Bob", "Charlie"]
```

### Extract from List of Tuples
```python
data = [
    ("HR", "Alice", 5000),
    ("IT", "Bob", 8000),
    ("HR", "Charlie", 6000)
]

# Get all departments (unique)
depts = list(set(t[0] for t in data))
# ["HR", "IT"]

# Get all salaries
salaries = [t[2] for t in data]
# [5000, 8000, 6000]

# Total salary
total = sum(t[2] for t in data)
# 19000

# Average salary
avg = sum(t[2] for t in data) / len(data)
# 6333.33
```

### Transform Dict Values in List
```python
users = [
    {"name": "alice", "email": "ALICE@TEST.COM"},
    {"name": "bob", "email": "BOB@TEST.COM"}
]

# Transform names to title case, emails to lowercase
cleaned = [
    {**u, "name": u["name"].title(), "email": u["email"].lower()}
    for u in users
]
# [{"name": "Alice", "email": "alice@test.com"}, ...]
```

---

## Quick Reference Card [↩️](#top)

```
┌─────────────────────────────────────────────────────────────────┐
│                    PYTHON DATA STRUCTURES                       │
├─────────────────────────────────────────────────────────────────┤
│ DICT                                                            │
│   d.get(k, default)    Safe access                              │
│   d.setdefault(k, [])  Init if missing                          │
│   d.pop(k, None)       Remove key safely                        │
│   d.items()            Loop key-value pairs                     │
├─────────────────────────────────────────────────────────────────┤
│ LIST                                                            │
│   l.append(x)          Add to end                               │
│   l.pop(i)             Remove at index                          │
│   l.sort(key=lambda)   Sort in place                            │
│   sorted(l)            Return new sorted list                   │
├─────────────────────────────────────────────────────────────────┤
│ STRING                                                          │
│   s.split(",")         Split to list                            │
│   ",".join(l)          Join list to string                      │
│   s.strip()            Remove whitespace                        │
│   s[::-1]              Reverse string                           │
├─────────────────────────────────────────────────────────────────┤
│ COMPREHENSIONS                                                  │
│   [x for x in l]                   List                         │
│   {k:v for k,v in d.items()}       Dict                         │
│   [x for x in l if condition]      Filtered                     │
└─────────────────────────────────────────────────────────────────┘
```
