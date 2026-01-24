# E-Commerce System Design (Amazon/Shopify)

## 1. Requirements

### Functional
*   Browse & Search Products.
*   Add to Cart.
*   Checkout & Pay.
*   View Order History.

### Non-Functional
*   **Scalability**: Handle spikes (Black Friday).
*   **Availability**: Catalog must always be visible.
*   **Consistency**: Inventory must be accurate during checkout.

## 2. High-Level Design (HLD)

### Microservices Architecture
1.  **Web/Mobile App**: Frontend.
2.  **API Gateway**: Aggregation endpoint.
3.  **Services**:
    *   **Catalog Service**: Product metadata (Read Heavy).
    *   **Cart Service**: Temporary state (Write Heavy).
    *   **Inventory Service**: Stock management.
    *   **Order Service**: Lifecycle management.
    *   **Recommendation Service**: "Customers/People also bought...".

## 3. Data Storage

*   **Catalog**: Relational DB (MySQL) for master data + NoSQL/Elasticsearch for search attributes.
*   **Cart**: Redis (Key=UserID, Value=List<Items>). Fast, ephemeral.
*   **Orders**: Sharded Relational DB (by OrderID or UserID).
*   **Historical Data**: Cassandra/HBase for analytics.

## 4. Deep Dive

### A. Inventory Management (The "Oversell" Problem)
*   **Scenario**: 1 item left, 10 users click "Buy".
*   **Option 1: Pessimistic Locking (DB)**
    *   Lock row when user adds to cart.
    *   *Cons*: Holds inventory for abandoned carts. Bad UX.
*   **Option 2: Optimistic Locking (At Checkout)** — **Preferred**
    *   Allow add to cart.
    *   At "Pay" button press: `UPDATE stock SET quantity = quantity - 1 WHERE id = X AND quantity > 0`.
    *   If rows affected = 0, inform user "Out of Stock".

### B. Shopping Cart
*   **Storage**: Redis is ideal for active sessions.
*   **Persistence**: If user logs in on mobile vs desktop, cart must sync.
    *   On login, merge Redis cart with "Persistent Cart" (DynamoDB/SQL).

### C. Checkout Flow
1.  **Frontend** sends `PlaceOrder` request.
2.  **Order Service** creates PENDING order.
3.  **Payment Gateway** (Stripe/PayPal) is called.
4.  **Callback**:
    *   Success: Update Order -> CONFIRMED. Trigger "Shipping Service".
    *   Failure: Update Order -> FAILED. Release inventory.
