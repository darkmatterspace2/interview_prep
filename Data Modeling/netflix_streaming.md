# Netflix Data Model (Streaming Service)

This document outlines the data model for a video streaming platform.

## 1. Core Entities
1.  **Account**: Billing entity (Family plan).
2.  **Profile**: Usage entity (Mom, Dad, Kids).
3.  **Video**: The content (Movie or Episode).
4.  **Series/Season**: Organizational hierarchy.
5.  **WatchHistory**: Logs progress to support "Resume Watching".
6.  **Genre/Category**: Classification.

## 2. Logical SQL Schema

```sql
-- 1. Accounts & Profiles
CREATE TABLE Accounts (
    account_id BIGINT PRIMARY KEY,
    email VARCHAR(255),
    subscription_plan VARCHAR(50)
);

CREATE TABLE Profiles (
    profile_id BIGINT PRIMARY KEY,
    account_id BIGINT,
    name VARCHAR(50),
    is_kids BOOLEAN,
    FOREIGN KEY (account_id) REFERENCES Accounts(account_id)
);

-- 2. Content Metadata
CREATE TABLE Videos (
    video_id BIGINT PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    duration_seconds INT,
    file_url VARCHAR(500), -- CDM/CDN path
    release_year INT,
    type ENUM('MOVIE', 'EPISODE')
);

CREATE TABLE Series (
    series_id BIGINT PRIMARY KEY,
    title VARCHAR(255)
);

CREATE TABLE Episodes (
    episode_id BIGINT PRIMARY KEY,
    series_id BIGINT,
    season_number INT,
    episode_number INT,
    video_id BIGINT, -- Links to physical file metadata
    FOREIGN KEY (series_id) REFERENCES Series(series_id),
    FOREIGN KEY (video_id) REFERENCES Videos(video_id)
);

-- 3. Watch Progress (Resume Watching)
-- High write volume!
CREATE TABLE WatchProgress (
    profile_id BIGINT,
    video_id BIGINT,
    last_watched_timestamp TIMESTAMP,
    progress_seconds INT,
    is_finished BOOLEAN,
    PRIMARY KEY (profile_id, video_id),
    FOREIGN KEY (profile_id) REFERENCES Profiles(profile_id)
);
```

## 3. Key Design Patterns

### A. Handling "Continue Watching"
This feature requires frequent updates (heartbeats) while a user watches.
*   **Design**: Do not update the main database every 10 seconds.
*   **Optimization**: Send heartbeats to a Redis/Cache buffer. Aggregate updates and flush to Postgres/Cassandra every X minutes or on session end.

### B. Content Delivery Network (CDN)
The DB stores *metadata* (`file_url`). The actual `.mp4` binaries are stored in Object Storage (S3) and distributed via CDN (Cloudfront/Akamai) to edges close to users. The database never acts as a blob store for video.
