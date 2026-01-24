# Food Delivery System Design (UberEats/DoorDash)

## 1. Requirements
*   Customer: Browse menus, Place order, Track delivery.
*   Restaurant: Receive orders, Update status.
*   Driver: Receive delivery requests, Navigation.

## 2. High-Level Design (HLD)

### Ecosystem
*   **Customer App**: Read-heavy (menus). Write (Orders).
*   **Restaurant App**: Tablet-based. Receives Order notifications.
*   **Driver App**: Location tracking.

### Backend Services
1.  **Order Matching Service**: Assigns order to driver.
2.  **Order Lifecycle Service**: Manages state (PREPARING -> READY...).
3.  **Location Service**: Ingests driver GPS.

## 3. Deep Dive

### A. Driver Matching (Dispatch System)
*   Goal: Minimize delivery time (Food ready time + Driver travel time).
*   **Geospatial Query**: Find drivers within X km of restaurant.
*   **Algorithm**:
    *   Not just "Nearest".
    *   Must consider: Driver direction, Current batch (can they take 2 orders?), Traffic.
*   **Segmented Locking**: When offering an order to Driver A, lock it for 30s so Driver B doesn't grab it.

### B. Real-Time Tracking
*   **Polling**: Bad for battery and server load.
*   **WebSockets / Server Sent Events (SSE)**:
    *   Driver App -> sends GPS (UDP/HTTP) -> Location Service (Redis Geo).
    *   Location Service -> publishes to Kafka "driver_updates".
    *   Notification Service -> consumes Kafka -> pushes to Customer App via WebSocket.

### C. Menu Management
*   Menus changes are frequent (Sold out items).
*   **Caching**: Heavy caching of Menus on CDNs/Redis with short TTL or explicit invalidation when Restaurant updates menu.
