Congratulations on getting the initial assessment! Amazon's Data Engineering (DE) process in India is known for being rigorous but very structured. The online assessment (OA) on HackerRank is the first major hurdle to prove your technical foundation.

Here is a breakdown of what to expect in the OA and how to navigate the rest of the process.

---

## Phase 1: The HackerRank Online Assessment

The SQL OA typically consists of **2–3 questions** and lasts about **60–90 minutes**. Amazon's SQL tests don't just check if you know the syntax; they test if you can handle **e-commerce logic** (e.g., calculating monthly active users, identifying top-selling products, or handling overlapping dates).

### Core SQL Topics to Master

* **Joins & Aggregations:** This is the bread and butter. Be extremely comfortable with `LEFT JOIN` vs `INNER JOIN` and using `GROUP BY` with `HAVING`.
* **Window Functions:** These are **highly likely** to appear. Focus on:
* `RANK()`, `DENSE_RANK()`, and `ROW_NUMBER()` (e.g., "Find the top 3 selling products per category").
* `LEAD()` and `LAG()` (e.g., "Calculate the growth in sales compared to the previous month").
* `SUM() OVER()` for running totals.


* **Date Manipulation:** Amazon loves time-series data. Practice `EXTRACT`, `DATE_TRUNC`, and calculating differences between dates (e.g., "Find customers who made a second purchase within 7 days of their first").
* **CTE (Common Table Expressions):** Use `WITH` clauses to keep your code readable. It helps you think through multi-step logic.

### OA Pro-Tips

1. **Read the Schema Carefully:** Pay attention to **NULL** values and primary keys.
2. **Edge Cases:** Always consider what happens if there are no sales for a month or if two products have the same rank.
3. **HackerRank Environment:** You can choose your SQL dialect (usually MySQL or PostgreSQL). Stick to the one you know best.

---

## Phase 2: The Full Interview Loop

If you pass the OA, the process usually moves to a **Technical Phone Screen** followed by a **Virtual Onsite (5 rounds)**.

### 1. Technical Pillars

* **Data Modeling:** You will likely be asked to design a schema for an Amazon-specific scenario (e.g., "Design a schema for a Prime Video recommendation system"). Focus on **Star Schema**, **Normalization vs. Denormalization**, and **SCD (Slowly Changing Dimensions)**.
* **ETL/Pipeline Design:** Explain how you move data from source to warehouse. Be ready to discuss **Batch vs. Streaming**, data quality checks, and handling failures (idempotency).
* **Coding (Python):** Usually one round involves a Python coding challenge, often focusing on data manipulation (like using Dictionaries or Lists) rather than complex LeetCode-style algorithms.

### 2. The "Leadership Principles" (The Bar Raiser)

Amazon is unique because **50% of your evaluation** is based on their **16 Leadership Principles (LPs)**.

* **Ownership** and **Dive Deep** are critical for Data Engineers.
* Prepare **2–3 stories per principle** using the **STAR Method** (Situation, Task, Action, Result).
* *Example Question:* "Tell me about a time you had to handle a data quality issue under a tight deadline."

---

## Preparation Roadmap

| Week | Focus Area | Recommended Resources |
| --- | --- | --- |
| **Days 1-3** | **SQL Mastery** | LeetCode (Medium/Hard SQL), DataLemur (Amazon-specific) |
| **Days 4-5** | **Data Modeling** | "The Data Warehouse Toolkit" (Kimball basics), System Design videos |
| **Days 6-7** | **Leadership Principles** | Review Amazon's LP page; write down your STAR stories |

**Would you like me to generate a few "Amazon-style" SQL practice questions for you to solve right now?**