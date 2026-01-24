# E-Commerce Data Model (Amazon/Shopify)

This document outlines the data model for a standard e-commerce platform.

## 1. Requirement Analysis
*   **Catalog**: Browse products, categories.
*   **Cart**: Temporary storage for items.
*   **Checkout/Orders**: Persistent record of purchases.
*   **Inventory**: accurate stock tracking.

## 2. Core Entities
1.  **User**: Standard profile.
2.  **Product**: Name, description, price, stock_quantity.
3.  **Category**: Hierarchical organization (Tree structure).
4.  **Order**: Status, total, shipping info.
5.  **OrderItem**: Link between Order and Product (snapshot of price at time of purchase).
6.  **Cart & CartItem**: Ephemeral or persistent depending on design.

## 3. Logical SQL Schema

```sql
-- 1. Users
CREATE TABLE Users (
    user_id BIGINT PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    full_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Categories (Hierarchical)
CREATE TABLE Categories (
    category_id INT PRIMARY KEY,
    parent_id INT, -- Self-referencing FK for hierarchy
    name VARCHAR(100),
    FOREIGN KEY (parent_id) REFERENCES Categories(category_id)
);

-- 3. Products
CREATE TABLE Products (
    product_id BIGINT PRIMARY KEY,
    category_id INT,
    name VARCHAR(255),
    description TEXT,
    price DECIMAL(10, 2),
    stock_quantity INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES Categories(category_id)
);

-- 4. Orders
CREATE TABLE Orders (
    order_id BIGINT PRIMARY KEY,
    user_id BIGINT,
    status ENUM('PENDING', 'PAID', 'SHIPPED', 'DELIVERED', 'CANCELLED'),
    total_amount DECIMAL(10, 2),
    shipping_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- 5. OrderItems
-- Stores price at purchase time in case product price changes later
CREATE TABLE OrderItems (
    order_item_id BIGINT PRIMARY KEY,
    order_id BIGINT,
    product_id BIGINT,
    quantity INT,
    unit_price DECIMAL(10, 2), -- Snapshot price
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);
```

## 4. Key Design Patterns

### A. Inventory Management (Concurrency)
Handling 20 users trying to buy the last iPhone simultaneously.

**Optimistic Locking (Version column):**
```sql
UPDATE Products 
SET stock_quantity = stock_quantity - 1, version = version + 1
WHERE product_id = 101 
  AND stock_quantity > 0 
  AND version = 5; -- Check if version matches what we read
```
If rows updated = 0, the transaction failed (data changed), user must retry.

### B. Product Attributes (EAV Pattern vs JSONB)
Products have different attributes (Shirt size vs Laptop RAM).
*   **SQL Anti-pattern**: `Entity-Attribute-Value` table (slow).
*   **Modern Approach**: `JSONB` column in Postgres/MySQL.
    *   `attributes = {"size": "L", "color": "Blue"}`
