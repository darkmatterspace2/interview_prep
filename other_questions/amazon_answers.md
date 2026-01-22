# Amazon Data Engineering Interview - Practice Model Answers

This document provides solving strategies and model answers for the key areas mentioned in your preparation guide: **HackerRank SQL**, **Data Modeling**, and **Leadership Principles**.

---

## Phase 1: HackerRank SQL Solutions

### Challenge 1: Finding Top 3 Selling Products Per Category
**Concept:** Window Functions (`DENSE_RANK()`)
**Scenario:** You have a `Sales` table with `product_id`, `category_id`, and `total_sales`. Find the top 3 highest-selling products in each category. If there is a tie, they share the rank.

**Mock Schema:**
`Products`: product_id, category, sales_amount

**Logic:**
1.  Partition the data by `category`.
2.  Order by `sales_amount` in descending order.
3.  Use `DENSE_RANK()` so that ties (e.g., two products with $100 sales) both get rank 1, and the next one gets rank 2.

**Solution (PostgreSQL/MySQL):**
```sql
WITH RankedSales AS (
    SELECT
        category,
        product_id,
        sales_amount,
        DENSE_RANK() OVER (
            PARTITION BY category
            ORDER BY sales_amount DESC
        ) as rank_val
    FROM Products
)
SELECT
    category,
    product_id,
    sales_amount,
    rank_val
FROM RankedSales
WHERE rank_val <= 3;
```

---

### Challenge 2: Month-over-Month Sales Growth
**Concept:** `LAG()` Window Function
**Scenario:** Calculate the percentage growth in **monthly sales** compared to the previous month.

**Mock Schema:**
`MonthlySales`: sales_month (Date), revenue (Decimal)

**Solution:**
```sql
WITH MonthlyStats AS (
    SELECT
        sales_month,
        revenue,
        -- Get the revenue from the previous row (Partition not strictly needed if only one timeline)
        LAG(revenue) OVER (ORDER BY sales_month) as prev_month_revenue
    FROM MonthlySales
)
SELECT
    sales_month,
    revenue,
    prev_month_revenue,
    CASE
        WHEN prev_month_revenue IS NULL THEN 0 -- First month has no growth
        ELSE ROUND(((revenue - prev_month_revenue) / prev_month_revenue) * 100, 2)
    END as growth_percentage
FROM MonthlyStats;
```

---

### Challenge 3: Customers with 2nd Purchase within 7 Days
**Concept:** Self-Join or `LEAD()` + Date Math
**Scenario:** Identify `customer_id`s where the user made a second purchase within 7 days of their **very first** purchase.

**Mock Schema:**
`Orders`: order_id, customer_id, order_date

**Solution (Using Self-Join - Easier to debug):**
```sql
WITH FirstPurchase AS (
    -- Step 1: Find the first order date for every customer
    SELECT
        customer_id,
        MIN(order_date) as first_order_date
    FROM Orders
    GROUP BY customer_id
),
SubsequentPurchases AS (
    -- Step 2: Join back to Orders to find other orders
    SELECT
        o.customer_id,
        o.order_date
    FROM Orders o
    JOIN FirstPurchase fp ON o.customer_id = fp.customer_id
    -- We want orders that are NOT the first one, but are effectively "Next"
    WHERE o.order_date > fp.first_order_date
)
-- Step 3: Filter for the 7-day window
SELECT DISTINCT
    sp.customer_id
FROM SubsequentPurchases sp
JOIN FirstPurchase fp ON sp.customer_id = fp.customer_id
WHERE DATEDIFF(day, fp.first_order_date, sp.order_date) <= 7;
-- Note: Syntax for Date Diff varies. Postgre: (sp.order_date - fp.first_order_date) <= 7
```

---

## Phase 2: Technical Interview - Data Modeling

### Scenario: Design a Schema for "Prime Video" Recommendation System
**Goal:** We need to track **User Watch History** to recommend new movies.
**Key Requirements:**
1.  Scalable (Billions of events).
2.  Support queries like: "What genre does User X watch most?" or "How many users stopped watching Movie Y after 5 minutes?".

**Proposed Solution: Star Schema (Dimensional Modeling)**

**1. Fact Table: `fact_watch_events`**
*   This table records the transaction/action. It is very narrow and long.
*   **Columns:**
    *   `event_id` (PK, BigInt/UUID)
    *   `user_key` (FK to dim_user)
    *   `media_key` (FK to dim_media)
    *   `device_key` (FK to dim_device)
    *   `start_timestamp` (DateTime)
    *   `duration_watched_sec` (Int)
    *   `event_type` (Enum: 'PLAY', 'PAUSE', 'COMPLETE', 'ABANDON')
    *   `session_id` (UUID)

**2. Dimension Tables:**
*   **`dim_user`**:
    *   `user_key` (PK), `user_original_id`, `subscription_tier` (Prime/Rent), `geo_region`, `age_group`.
    *   *SCD Type 2:* If a user moves regions, we might track history, but usually Type 1 (overwrite) is fine for recommendations.
*   **`dim_media`**:
    *   `media_key` (PK), `title`, `genre` (Important!), `release_year`, `director`, `content_rating`, `duration_total`.
*   **`dim_date`**:
    *   Standard date dimension for fast rollups by Week/Month/Holiday.

**Why this design?**
*   **Performance:** Numerical Keys (Surrogate Keys) in the Fact table make joins faster than UUIDs.
*   **Analytics:** To find "Top Genre", we join `fact_watch_events` -> `dim_media` and `GROUP BY genre`.
*   **SCD:** We handle changes in User Subscription status in `dim_user` without touching the billions of rows in the Fact table.

---

## Phase 3: Python Coding (Data Manipulation)

**Scenario:** You have a list of raw log strings: `"2024-01-01 ERROR: Database connection failed"`.
**Task:** Parse logs and return a Dictionary counting the frequency of each error type.

**Solution:**
```python
def count_error_types(logs):
    error_counts = {}

    for log in logs:
        # Simple splitting strategy
        # Log format: "DATE TYPE: MESSAGE"
        parts = log.split(" ")

        # Safety check for malformed lines
        if len(parts) < 3:
            continue

        log_level = parts[1].replace(":", "") # Get "ERROR", "INFO"

        if log_level == "ERROR":
            # Extract the message (everything after the level)
            # "2024-01-01 ERROR: Database connection failed"
            # split produced: ['2024-01-01', 'ERROR:', 'Database', 'connection', 'failed']
            # We want 'Database connection failed' as the unique key, logical? Or just 'Database'?
            # Usually strict parsing is required. Let's assume the message starts at index 2.
            message = " ".join(parts[2:])

            if message in error_counts:
                error_counts[message] += 1
            else:
                error_counts[message] = 1

    return error_counts

# Test
raw_logs = [
    "2024-01-01 ERROR: Connection Timeout",
    "2024-01-01 INFO: Job Started",
    "2024-01-02 ERROR: Connection Timeout",
    "2024-01-02 ERROR: Null Pointer"
]
print(count_error_types(raw_logs))
# Output: {'Connection Timeout': 2, 'Null Pointer': 1}
```

---

## Phase 4: Leadership Principles (The Bar Raiser)

### Principle: **Ownership** / **Dive Deep**
**Question:** "Tell me about a time you had to handle a data quality issue under a tight deadline."

**STAR Answer:**

**Situation:**
"In my previous role, during the Black Friday peak, our Marketing Dashboard—used by the VP of Sales to adjust ad spend hourly—suddenly showed $0 revenue for the EMEA region at 10 AM."

**Task:**
"I needed to identify the root cause, fix the data pipeline, and backfill the missing data before the noon executive meeting, as incorrect ad spend decisions could cost us ~$50k/hour."

**Action:**
1.  **Ownership (Took Charge):** I immediately flagged the issue to stakeholders (Transparency) so they wouldn't use the bad data.
2.  **Dive Deep (Debugging):** I traced the lineage back to the source. I bypassed the standard dashboard logs and queried the raw S3 landing zone. I found that the EMEA source system had added a new column to the CSV file, shifting the 'Revenue' column index by one, which broke our rigid ETL parser.
3.  **Fix:** I wrote a quick 'hotfix' Python script to correctly map the columns for the new format and deployed it manually to unblock the pipeline (bias for action).
4.  **Long-term:** I scheduled a backfill job for the historical files and, effectively, updated the parser to be header-aware (so column ordering wouldn't matter in the future) to prevent recurrence.

**Result:**
"The dashboard was back up by 11:15 AM with 100% accurate data. The VP made the correct ad spend adjustments. Following this, I implemented a 'Schema Drift' alert that would pause the pipeline and notify us *before* ingesting bad files, rather than failing silently."
