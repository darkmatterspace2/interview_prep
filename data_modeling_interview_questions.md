# Data Modeling Interview Questions & Concepts

A guide to core data modeling concepts and a practical schema design example.

## 1. Core Concepts

### Normalization vs. Denormalization
- **Normalization (OLTP)**: Organizing measurements to minimize redundancy.
    - **1NF**: Atomic values, no repeating groups.
    - **2NF**: 1NF + Partial dependencies removed (attributes depend on whole PK).
    - **3NF**: 2NF + Transitive dependencies removed (attributes depend *only* on PK).
    - **Goal**: Write-heavy systems, data integrity, optimize storage.
- **Denormalization (OLAP)**: Adding redundancy to speed up reads.
    - **Goal**: Read-heavy systems (Data Warehouses), minimize joins.

### Fact vs. Dimension Tables
- **Fact Table**: Contains quantitative data (metrics, measures) and foreign keys to dimensions.
    - **Transaction Fact**: One row per event (e.g., Order Line Item).
    - **Snapshot Fact**: One row per period (e.g., Monthly Account Balance).
    - **Accumulating Snapshot**: Updates over time (e.g., Order processing workflow).
- **Dimension Table**: Contains descriptive attributes (who, what, where, when).
    - **Conformed Dimension**: Shared across multiple facts (e.g., Date, Customer).
    - **Junk Dimension**: Collection of low-cardinality flags/codes.

### Schema Types
- **Star Schema**: Central fact table connected directly to dimensions. Simpler, faster joins.
- **Snowflake Schema**: Dimensions are normalized (split into sub-dimensions). Saves space, but more complex joins.
- **Galaxy Schema**: Multiple fact tables sharing conformed dimensions.

## 2. Slowly Changing Dimensions (SCD)
How to handle updates to dimension attributes (e.g., User changes address).

- **Type 0 (Retain Original)**: No changes allowed.
- **Type 1 (Overwrite)**: Update the record. History is lost.
- **Type 2 (Add Row)**: Create a new record with effective dates (`start_date`, `end_date`) and `is_current` flag. Preserves full history. (Most common in DW).
- **Type 3 (Add Column)**: Add a `previous_value` column. Keeps limited history (current + previous).

## 3. Practical Example: E-commerce Schema Design

**Scenario**: Design a database for an Amazon-like E-commerce platform.

### Requirements
- Users can sign up and manage profile.
- Products have categories and inventory.
- Users place orders containing multiple items.
- Payments and Shipping tracking.

### Conceptual / Logical Data Model (OLTP)

#### 1. Users Table
- `user_id` (PK)
- `email` (Unique, Index)
- `password_hash`
- `first_name`, `last_name`
- `created_at`

#### 2. Products Table
- `product_id` (PK)
- `name`, `description`
- `price` (Decimal)
- `category_id` (FK) -> Categories Table
- `sku` (Unique Stock Keeping Unit)
- `created_at`

#### 3. Inventory Table
(Separated from Products to handle warehouses or real-time availability)
- `inventory_id` (PK)
- `product_id` (FK)
- `quantity_on_hand`
- `warehouse_location`
- `last_updated` (Timestamp for concurrency checks)

#### 4. Orders Table (Header)
- `order_id` (PK)
- `user_id` (FK)
- `status` (Enum: Pending, Shipped, Delivered, Canceled)
- `total_amount`
- `shipping_address_id` (FK)
- `created_at`

#### 5. Order_Items Table (Details - The "Line Items")
- `order_item_id` (PK)
- `order_id` (FK)
- `product_id` (FK)
- `quantity`
- `unit_price` (Price *at time of purchase*, critical for history!)

#### 6. Payments Table
- `payment_id` (PK)
- `order_id` (FK)
- `amount`
- `payment_method` (CC, PayPal)
- `status` (Success, Failed)
- `transaction_date`

### Key Considerations for Interview

1.  **Price History**: Why store `unit_price` in `Order_Items` when it's in `Products`?
    *   **Answer**: Product prices change. You must lock in the price at the moment of purchase for historical accuracy and refund calculations.

2.  **Concurrency / Inventory Management**: What happens if two users buy the last item simultaneously?
    *   **Answer**: Use Database Transactions (ACID).
    *   *Optimistic Locking*: Check `last_updated` timestamp before write.
    *   *Pessimistic Locking*: `SELECT ... FOR UPDATE` to lock the row.
    *   *Check Constraint*: Ensure `quantity >= 0`.

3.  **Scalability**: How to handle 1 billion orders?
    *   **Sharding**: Partition the `Orders` and `Order_Items` tables by `user_id` (keeps all user data on one shard) or `order_date` (for archival).
    *   **Indexing**: Index commonly queried columns (`user_id`, `status`, `product_id`).

4.  **Analytics (OLAP) Transformation**:
    *   If moving to a Data Warehouse (Redshift/Snowflake), this schema would become a **Star Schema**:
        *   **Fact**: `Fact_Orders` (grain: one row per line item).
        *   **Dimensions**: `Dim_User`, `Dim_Product` (SCD Type 2), `Dim_Date`, `Dim_Payment`.
