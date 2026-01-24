# YouTube Data Engineering Design

## 1. Scenario
Correctly counting "Views" is critical (Monetization). We need a system that is fast (User satisfaction) and accurate (Billing).

## 2. Requirements
*   **Accuracy**: Ads are paid per 1000 views. No over/under counting.
*   **Deduplication**: Spam protection (bot farms).
*   **Latency**: View count should update reasonably fast (e.g., "301 views" phenomenon).

## 3. Architecture: Lambda Architecture

### Components
1.  **Speed Layer (Approximate)**:
    *   Kafka -> Spark Streaming / Storm.
    *   Lossy counting or simple aggregation per minute.
    *   Updates Redis/Cassandra.
    *   *Result*: "301 Views" (Fast, but maybe innacurate/duplicated).
2.  **Batch Layer (Accurate)**:
    *   Raw logs -> S3.
    *   MapReduce / Spark Batch.
    *   Complex Spam Filtering Algorithms (Graph analysis, IP reputation).
    *   *Result*: "Verified Views" (Computed daily/hourly).
3.  **Serving Layer**:
    *   Merges Speed + Batch.
    *   If Batch > Speed (Batch caught up), show Batch. Else show Speed.

## 4. Pipeline Design

### A. View Counting Pipeline
1.  **Log**: Client sends `ViewEvent` heartbeat every 30s.
2.  **Deduplication (Batch)**:
    *   Group by `(video_id, user_ip, session_id)`.
    *   If > 50 views from same IP in 1 hour -> Mark as Spam.
3.  **Aggregation**:
    *   `SELECT video_id, count(*) FROM legitimate_views GROUP BY video_id`.
4.  **Publication**:
    *   Update `VideoMetadata` table (Sharded MySQL/Vitess).

### B. Thumbnail Generation (ETL for Binary Data)
1.  **Trigger**: Video Upload to Blob Store.
2.  **Workflow (Airflow)**:
    *   Extract frame at timestamp 00:10.
    *   Resize to 1080p, 720p, 480p.
    *   Upload images to CDN Origin.
    *   Update Metadata DB with Image URLs.

## 5. Deep Dive: "The 301 Views"
*   Why did YouTube pause at 301?
*   Because the **Switchover** from Speed Layer to Batch Layer was manual or hard-coded at that threshold.
*   The system pauses public updates while the Batch Layer performs a rigorous spam check. Once verified, the counter unlocks.
