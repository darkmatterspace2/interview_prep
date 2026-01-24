# Food Delivery Data Engineering Design (UberEats)

## 1. Scenario
Calculate dynamic "Estimated Time of Arrival" (ETA) and "Delivery Fees" based on real-time driver locations, traffic, and restaurant state.

## 2. Requirements
*   **Stateful Processing**: Need to remember "Driver A is currently on Order #123".
*   **Geospatial**: Efficient ingestion of Lat/Lon streams.
*   **ML Integration**: Features must be served to ML models instantly.

## 3. Architecture: Stream Processing (Flink)

### Components
1.  **Source**: Driver GPS stream ~ every 5 seconds per driver (MQTT/WebSocket -> Kafka).
2.  **Processing Engine**: **Apache Flink**.
    *   True streaming (Event time processing).
    *   Stateful (RocksDB backend).
3.  **Serving Layer**: **Redis** (Hot state), **Cassandra** (Order history).
4.  **Data Lake**: **Apache Iceberg** (Geospatial partitioning).

## 4. Pipeline Design

### A. Dynamic ETA Calculation
1.  **Stream 1**: `DriverLocations` (DriverID, Lat, Lon, Time).
2.  **Stream 2**: `Orders` (OrderID, RestaurantLat, Lon, Status).
3.  **Flink Job**:
    *   Window Join (Interval Join).
    *   Calculate distance (Haversine or Mapbox Router).
    *   Apply ML Model (Traffic factor).
    *   Emit `PredictedETA`.
4.  **Sink**: Update Customer App (Websocket) and write to `OrderEvents` table.

### B. Sessionization (Driver Efficiency)
*   **Goal**: Calculate how much time a driver waits at restaurants per day.
*   **Logic**:
    *   Identify "Arrival" event (Driver enters Geofence).
    *   Identify "Pickup" event (Driver swipes 'Picked Up').
    *   `WaitTime = PickupTime - ArrivalTime`.
    *   Flink Session Window key functionality.

## 5. Deep Dive: Backfill in Streaming (Kappa)
*   **Scenario**: We improved the ETA algorithm. We need to re-process last month's data to test it.
*   **Batch as Stream**:
    *   Read historical data from Iceberg Lake.
    *   Pipe it through the *same* Flink job used for production.
    *   Sink to a "Shadow Topic" for verification.
    *   No separate "Batch Codebase" needed (Unified API).
