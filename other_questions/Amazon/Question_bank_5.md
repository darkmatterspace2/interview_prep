These questions focus on your growth areas: **Dictionaries (Hash Maps)**, **Sets**, and **Data Aggregation**.

### **Part 1: The "Must-Master" Basics (Dictionaries & Sets)**

*These are directly aimed at fixing the logic issue from your interview question. You must be able to solve these without looking up syntax.*

1. **Word Frequency Counter**
* **Task:** Given a long string (like a paragraph), write a function to count how many times each word appears.
* **Goal:** Use a `dictionary` where `key = word` and `value = count`.
* **Bonus:** Ignore punctuation and case (e.g., "Apple" and "apple," are the same).


2. **Find Duplicates in a List**
* **Task:** Given a list of integers `[1, 2, 3, 2, 4, 5, 5]`, return a list of only the duplicate elements.
* **Goal:** Use a `set` to track what you've seen and a second `set` or `list` for the result.


3. **Group Anagrams (Classic DE Interview Question)**
* **Task:** Given a list of strings `["eat", "tea", "tan", "ate", "nat", "bat"]`, group them together.
* **Output:** `[["bat"], ["nat", "tan"], ["ate", "eat", "tea"]]`
* **Why:** This forces you to use a **dictionary** where the key is a "sorted string" or "tuple" and the value is a list of matches.



---

### **Part 2: String Manipulation & Log Parsing**

*Data Engineers often have to parse messy logs. These questions simulate that.*

4. **Log Error Extraction**
* **Input:** A list of log strings: `["INFO: User logged in", "ERROR: DB connection failed", "INFO: User clicked"]`.
* **Task:** Return a dictionary counting how many times each log level (INFO, ERROR, WARN) appears.
* **Skill:** `string.split()` and dictionary aggregation.


5. **IP Address Anonymizer**
* **Task:** Write a function that takes a string containing an IP address (e.g., `"User 192.168.1.1 connected"`) and replaces the last octet with `0` (e.g., `"User 192.168.1.0 connected"`).
* **Skill:** String slicing and reconstruction.



---

### **Part 3: LeetCode Practice List**

*If you want to practice on LeetCode, search for these exact problem names. They are heavily favored by Amazon.*

| Problem Name | Difficulty | Why it matters for DE |
| --- | --- | --- |
| **Two Sum** | Easy | Teaches `dict` lookups for O(n) speed. |
| **Contains Duplicate** | Easy | Teaches basic `set` usage. |
| **Top K Frequent Elements** | Medium | Teaches aggregation + sorting (Crucial). |
| **Product of Array Except Self** | Medium | Teaches array manipulation without nested loops. |
| **Valid Anagram** | Easy | Teaches frequency counting. |
| **First Unique Character in a String** | Easy | Similar to the interview question I asked you. |

---

### **Part 4: One "Take Home" Challenge**

*Try to solve this one right now to test if you've improved since the mock interview.*

**The Scenario:**
You have a list of tuples representing server usages. Each tuple is `(server_name, cpu_usage_percent)`.

```python
data = [
    ("ServerA", 15),
    ("ServerB", 10),
    ("ServerA", 55),
    ("ServerC", 80),
    ("ServerB", 5)
]

```

**Task:**
Write a function that returns a dictionary containing the **Average CPU Usage** for each server.

* *Expected Output:* `{'ServerA': 35.0, 'ServerB': 7.5, 'ServerC': 80.0}`

**Would you like to try solving this "Take Home" challenge here so I can review your code structure?**