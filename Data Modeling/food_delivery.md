# Food Delivery Data Model (UberEats, DoorDash)

This document outlines the data model for an on-demand food delivery service.

## 1. Core Entities
1.  **User/Customer**: Places orders.
2.  **Restaurant**: Prepares food.
3.  **Menu/MenuItem**: Valid products.
4.  **Order**: The central transaction entity.
5.  **Courier/Driver**: Delivers the order.
6.  **Delivery**: Tracks the logistics.

## 2. Logical SQL Schema

```sql
-- 1. Restaurants & Menu
CREATE TABLE Restaurants (
    restaurant_id BIGINT PRIMARY KEY,
    name VARCHAR(255),
    address VARCHAR(255),
    is_open BOOLEAN,
    created_at TIMESTAMP
);

CREATE TABLE MenuItems (
    item_id BIGINT PRIMARY KEY,
    restaurant_id BIGINT,
    name VARCHAR(255),
    price DECIMAL(10, 2),
    is_available BOOLEAN, -- 86'd items
    FOREIGN KEY (restaurant_id) REFERENCES Restaurants(restaurant_id)
);

-- 2. Orders
CREATE TABLE Orders (
    order_id BIGINT PRIMARY KEY,
    customer_id BIGINT,
    restaurant_id BIGINT,
    courier_id BIGINT NULL, -- Assigned later
    status ENUM('PLACED', 'CONFIRMED', 'PREPARING', 'PICKED_UP', 'DELIVERED', 'CANCELLED'),
    total_price DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES Users(user_id) -- Assuming generic Users table
);

-- 3. Order Details
CREATE TABLE OrderItems (
    order_item_id BIGINT PRIMARY KEY,
    order_id BIGINT,
    item_id BIGINT,
    quantity INT,
    special_instructions TEXT,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
);
```

## 3. Key Design Patterns

### A. Order State Machine
An order goes through specific transitions.
*   `PLACED` -> Restaurant accepts -> `CONFIRMED`
*   `CONFIRMED` -> Kitchen done -> `PREPARING` -> `READY_FOR_PICKUP`
*   Driver arrives -> `PICKED_UP` -> `DELIVERED`

**Concurrency**: Ensure a driver can only accept an order if it's not already taken by another driver.
```sql
UPDATE Orders 
SET courier_id = 101, status = 'DRIVER_ASSIGNED'
WHERE order_id = 500 AND courier_id IS NULL;
```

### B. Geospatial Indexing
Finding restaurants nearby.
*   Store lat/lon for Restaurants.
*   Use PostGIS (`ST_DWithin`) or Geohash for efficient queries.
```sql
SELECT * FROM Restaurants 
WHERE ST_DWithin(location, ST_MakePoint(user_lon, user_lat), 5000); -- 5km radius
```
