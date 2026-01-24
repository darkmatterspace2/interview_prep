# Airbnb Data Model for System Design Interview

This document outlines the data modeling approach for an Airbnb-type lodging reservation system. This is a common FAANG system design and SQL interview question.

## 1. Requirement & Assumptions

*   **Users**: A user can be both a generic user, a host, or a guest. We typically model this as a single `Users` table.
*   **Listings**: Hosts create listings (properties).
*   **Bookings**: Guests book listings for a date range.
*   **Availability**: The system must prevent double bookings and manage calendar availability efficiently.
*   **Reviews**: Guests review listings; Hosts review guests (optional but standard).
*   **Pricing**: Prices can vary by date (dynamic pricing).

## 2. Core Entities (ER Diagram)

1.  **User**: `user_id`, name, email, phone, is_host (bool).
2.  **Listing**: `listing_id`, host_id (FK), address, description, property_type, base_price.
3.  **Booking**: `booking_id`, listing_id (FK), guest_id (FK), check_in_date, check_out_date, status (PENDING, CONFIRMED, CANCELLED), total_price.
4.  **Review**: `review_id`, booking_id (FK), reviewer_id (FK), target_id (FK/Listing or User), rating, comment.
5.  **Calendar/Availability**: `listing_id`, `date`, `is_available`, `price` (daily override).

## 3. Logical SQL Schema

```sql
-- 1. Users Table
CREATE TABLE Users (
    user_id BIGINT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Listings Table
CREATE TABLE Listings (
    listing_id BIGINT PRIMARY KEY,
    host_id BIGINT NOT NULL,
    title VARCHAR(255),
    description TEXT,
    address_line1 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(50),
    zip_code VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    base_price_per_night DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (host_id) REFERENCES Users(user_id)
);

-- 3. Calendar / Availability Table
-- Critical for checking availability and daily pricing.
-- Approach: Store one row per date per listing is simple but heavy. 
-- Optimization: Ranges can be used, but daily rows make queries easier.
CREATE TABLE ListingAvailability (
    availability_id BIGINT PRIMARY KEY,
    listing_id BIGINT NOT NULL,
    calendar_date DATE NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    price_per_night DECIMAL(10, 2), -- Overrides base price
    UNIQUE(listing_id, calendar_date), -- Prevent duplicate dates for same listing
    FOREIGN KEY (listing_id) REFERENCES Listings(listing_id)
);

-- 4. Bookings Table
CREATE TABLE Bookings (
    booking_id BIGINT PRIMARY KEY,
    listing_id BIGINT NOT NULL,
    guest_id BIGINT NOT NULL,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    status ENUM('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED'),
    total_price DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (listing_id) REFERENCES Listings(listing_id),
    FOREIGN KEY (guest_id) REFERENCES Users(user_id)
);

-- 5. Reviews Table
CREATE TABLE Reviews (
    review_id BIGINT PRIMARY KEY,
    booking_id BIGINT NOT NULL,
    author_id BIGINT NOT NULL, -- User writing the review
    listing_id BIGINT NOT NULL, -- Listing being reviewed
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES Bookings(booking_id),
    FOREIGN KEY (author_id) REFERENCES Users(user_id),
    FOREIGN KEY (listing_id) REFERENCES Listings(listing_id)
);
```

## 4. Key Design Patterns & Queries

### A. Searching for Available Listings
Finding listings available between `start_date` and `end_date` is the most critical query.

**Naive Approach (using Bookings table):**
Find listings that *do not* have a booking overlapping with the requested range.
```sql
SELECT * FROM Listings l
WHERE l.listing_id NOT IN (
    SELECT b.listing_id 
    FROM Bookings b
    WHERE b.listing_id = l.listing_id
    AND NOT (b.check_out <= '2023-01-01' OR b.check_in >= '2023-01-05')
    AND b.status = 'CONFIRMED'
);
```

**Optimized Approach (using Availability Table):**
Only return listings where *every* day in the range is marked as available.
```sql
SELECT l.listing_id, l.title, SUM(cal.price_per_night) as total_trip_price
FROM Listings l
JOIN ListingAvailability cal ON l.listing_id = cal.listing_id
WHERE cal.calendar_date BETWEEN '2023-01-01' AND '2023-01-04' -- Checkout is on 5th
  AND cal.is_available = TRUE
GROUP BY l.listing_id
HAVING COUNT(cal.calendar_date) = 4; -- Must be available for all 4 nights
```

### B. Preventing Double Bookings (Concurrency)
When a user clicks "Book", you must ensure no one else booked those dates in the millisecond before.

**Transaction with Locking:**
```sql
START TRANSACTION;

-- 1. Check if dates are still free
SELECT * FROM ListingAvailability 
WHERE listing_id = 123 
  AND calendar_date BETWEEN '2023-01-01' AND '2023-01-05'
  AND is_available = TRUE
FOR UPDATE; -- Locks these rows

-- 2. If valid count, Insert Booking
INSERT INTO Bookings (...) VALUES (...);

-- 3. Update Availability
UPDATE ListingAvailability
SET is_available = FALSE
WHERE listing_id = 123 
  AND calendar_date BETWEEN '2023-01-01' AND '2023-01-05';

COMMIT;
```

## 5. Scalability Considerations (Use for System Design)
*   **Sharding**: Shard `Listings` and `Bookings` by `Location` (Geohash) or `listing_id`.
*   **Caching**: Cache search results heavily (Redis), invalidate when a booking occurs.
*   **Hotspots**: Popular listings or events (e.g., Superbowl location) create read/write hotspots.
