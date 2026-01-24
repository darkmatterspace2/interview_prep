# Airbnb System Design

## 1. Requirements

### Functional
*   **Host**: Can list properties, upload photos, set availability.
*   **Guest**: Can search for matching properties (Location, Date, Price).
*   **Guest**: Can book a property.

### Non-Functional
*   **High Availability**: Searching must always work.
*   **Consistency**: Booking must be strictly consistent (No double bookings).
*   **Latency**: Search results should be < 200ms.

## 2. Capacity Estimation (Back-of-the-Envelope)
*   **Users**: 100M active monthly.
*   **Listings**: 10M active listings.
*   **Search**: Highly read-heavy. 100:1 Read:Write ratio.
*   **Storage**: 10M listings * 10KB metadata = 100GB (Metadata is small). Photos are large (stored in Blob).

## 3. High-Level Design (HLD)

### Architecture Components
1.  **Load Balancer**: Distributes traffic.
2.  **API Gateway**: Auth, Rate Limiting, Routing.
3.  **Services**:
    *   **User Service**: Profile mgmt.
    *   **Listing Service**: Hosts create/edit listings. Writes to SQL (Truth) and Elasticsearch (Search).
    *   **Search Service**: Read-only, queries Elasticsearch.
    *   **Booking Service**: Handles reservations and payments.
4.  **Data Stores**:
    *   **Relational DB (Postgres/MySQL)**: For Users, Listings, Bookings (ACID required).
    *   **Search Index (Elasticsearch/Solr)**: For geospatial and full-text search.
    *   **Redis**: Caching hot listings.
    *   **Blob Store (S3)**: Images/Videos.

## 4. API Design

*   `GET /api/v1/listings?lat=...&long=...&checkin=...&checkout=...`
*   `POST /api/v1/bookings`
    *   Body: `{ listing_id, checkin, checkout, payment_token }`
*   `POST /api/v1/listings` (Host only)

## 5. Deep Dive

### A. Search & Indexing
*   **Challenge**: Searching by location + availability.
*   **Solution**:
    *   Use **Geohash** or **Quadtree** index in Elasticsearch.
    *   **Availability Filtering**: It's hard to index "available dates" efficiently.
    *   *Approach*: Filter by location first (smaller dataset), then filter by availability in memory, or use Bitmaps for availability days in the search index.

### B. Booking Consistency (Double Booking)
*   **Problem**: Users A and B click "Book" for the same dates simultaneously.
*   **Solution**: Distributed Locking or Database Row Locking.
    *   `START TRANSACTION`
    *   `SELECT * FROM availability WHERE listing_id=X AND date BETWEEN Y AND Z FOR UPDATE`
    *   If any row returned is 'booked', ROLLBACK.
    *   `UPDATE availability SET status='BOOKED'`
    *   `COMMIT`

### C. Image Storage
*   Original high-res images uploaded to S3.
*   Async worker (Lambda/Kafka) triggers resizing (thumbnails, mobile, desktop sizes).
*   CDN (CloudFront) serves images to reduce latency.
