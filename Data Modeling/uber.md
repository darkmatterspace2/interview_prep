# Uber Data Model (Ride Sharing)

This document outlines the data model for a ride-sharing application.

## 1. Core Entities
1.  **Rider**: The customer.
2.  **Driver**: The service provider.
3.  **Vehicle**: Associated with driver.
4.  **Trip/Ride**: The core transaction.
5.  **Location**: Real-time geospatial data.

## 2. Logical SQL Schema

```sql
-- 1. Users & Drivers
CREATE TABLE Users (
    user_id BIGINT PRIMARY KEY,
    name VARCHAR(100),
    rating DECIMAL(3, 2) -- 4.85
);

CREATE TABLE Drivers (
    driver_id BIGINT PRIMARY KEY,
    user_id BIGINT, -- Links to generic User
    license_number VARCHAR(50),
    current_lat DECIMAL(10, 8),
    current_lon DECIMAL(11, 8),
    is_active BOOLEAN, -- Online/Offline
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- 2. Vehicles
CREATE TABLE Vehicles (
    vehicle_id BIGINT PRIMARY KEY,
    driver_id BIGINT,
    license_plate VARCHAR(20),
    model VARCHAR(50),
    FOREIGN KEY (driver_id) REFERENCES Drivers(driver_id)
);

-- 3. Trips
CREATE TABLE Trips (
    trip_id BIGINT PRIMARY KEY,
    rider_id BIGINT,
    driver_id BIGINT,
    status ENUM('REQUESTED', 'MATCHED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'),
    pickup_lat DECIMAL(10, 8),
    pickup_lon DECIMAL(11, 8),
    dropoff_lat DECIMAL(10, 8),
    dropoff_lon DECIMAL(11, 8),
    fare DECIMAL(10, 2),
    requested_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (rider_id) REFERENCES Users(user_id),
    FOREIGN KEY (driver_id) REFERENCES Drivers(driver_id)
);
```

## 3. Key Design Patterns

### A. Location Tracking (High Write Volume)
Drivers emit location every 3 seconds.
**Do NOT** update the main SQL `Drivers` table every 3 seconds for every driver.
**Solution**:
*   Use an in-memory geo-store like **Redis (Geo)** or **Uber H3** to track live positions.
*   Only persist "Trip Start" and "Trip End" locations to SQL for billing/history.
*   Breadcrumbs during a trip can be stored in Cassandra/NoSQL for route history, not relational DB.

### B. Driver Matching
Finding the nearest driver.
*   Query Redis for drivers with `status=ACTIVE` within radius R.
*   Lock the driver (Atomic check-and-set) to prevent assigning them to two riders.
