# Uber System Design (Ride Sharing)

## 1. Requirements
*   Rider: Request ride, See ETA.
*   Driver: Accept ride, See Location.
*   System: Match Rider to Driver efficiently.

## 2. High-Level Architecture
*   **DISCO (Dispatch System)**: The brain.
*   **Geospatial Service**: Tracks drivers.
*   **Trip Service**: Manages trip state.

## 3. Deep Dive: Geospatial Indexing

### How to handle millions of updates?
*   Naive: `SELECT * FROM Drivers WHERE distance < 1km`. (Full table scan = Fail).
*   **Geohash**:
    *   Divide world into grid strings (e.g., "dr5r..." is NYC).
    *   Drivers in same cell share prefix.
    *   Lookups are string matches.
*   **QuadTree**:
    *   In-memory tree structure.
    *   Root -> 4 quadrants -> 4 sub-quadrants.
    *   Leaf node contains driver list.
    *   If a cell gets too full (> 500 drivers), split it.
    *   **Google S2 Library**: Maps sphere to 1D integer (Hilbert Curve). Preserves locality.

### Architecture for Updates
1.  Driver app sends Lat/Lon every 4s.
2.  Load Balancer -> **Location Service**.
3.  Update **Redis** (Ephemeral location).
4.  Do *not* write every point to DB.
5.  *Only* write to DB (Cassandra/RDBMS) when Trip Starts/Ends for billing.

## 4. Handling Surge Pricing
*   Demand > Supply in a Geohash Area.
*   Service calculates multiplier.
*   Update applied to area for X minutes.
*   **Consistency**: User sees 1.5x, they must be charged 1.5x even if it drops 1 min later. Lock the price at "Request" time.
