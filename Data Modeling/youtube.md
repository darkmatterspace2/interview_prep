# YouTube Data Model (Video Sharing)

This document outlines the data model for a video hosting platform.

## 1. Core Entities
1.  **User**: Viewer/Creator.
2.  **Channel**: Identity for uploading content.
3.  **Video**: The media asset.
4.  **Comment**: Social interaction.
5.  **Like/Vote**: Binary feedback.
6.  **Playlist**: Aggregation of videos.

## 2. Logical SQL Schema

```sql
-- 1. Channels
CREATE TABLE Channels (
    channel_id BIGINT PRIMARY KEY,
    owner_user_id BIGINT,
    name VARCHAR(100),
    subscriber_count BIGINT DEFAULT 0,
    created_at TIMESTAMP
);

-- 2. Videos
CREATE TABLE Videos (
    video_id BIGINT PRIMARY KEY,
    channel_id BIGINT,
    title VARCHAR(255),
    description TEXT,
    video_url VARCHAR(500), -- Blob storage path
    thumbnail_url VARCHAR(500),
    duration_seconds INT,
    view_count BIGINT DEFAULT 0, -- Sharded counter in practice
    like_count BIGINT DEFAULT 0,
    upload_status ENUM('PROCESSING', 'PUBLISHED', 'PRIVATE'),
    created_at TIMESTAMP,
    FOREIGN KEY (channel_id) REFERENCES Channels(channel_id)
);

-- 3. Comments (Nested)
CREATE TABLE Comments (
    comment_id BIGINT PRIMARY KEY,
    video_id BIGINT,
    user_id BIGINT,
    parent_comment_id BIGINT NULL,
    text TEXT,
    likes INT,
    created_at TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES Videos(video_id)
);

-- 4. Likes (Relationships)
CREATE TABLE VideoLikes (
    user_id BIGINT,
    video_id BIGINT,
    created_at TIMESTAMP,
    PRIMARY KEY (user_id, video_id) -- Prevent double like
);
```

## 3. Key Design Patterns

### A. View Counts (Scalability)
Popular videos get thousands of views per second.
**Problem**: Locking a row `UPDATE Videos SET view_count = view_count + 1` is a bottleneck.
**Solution**:
1.  **Buffer**: Append views to a Kafka topic.
2.  **Aggregate**: Summarize views every X seconds (Stream processing).
3.  **Batch Write**: Update DB once per batch `view_count = view_count + 500`.

### B. Comments Pagination
YouTube comments are effectively infinite.
*   **Offset Pagination**: `LIMIT 10 OFFSET 1000` (Slow).
*   **Cursor Pagination**: `WHERE created_at < last_seen_timestamp LIMIT 10` (Fast/Scalable).
