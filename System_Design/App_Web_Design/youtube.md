# YouTube System Design

## 1. Requirements
*   Upload Video (GB sizes).
*   View Video (Streaming).
*   Search/Recommendations.

## 2. Architecture

### Components
1.  **Web Server**: Api handling.
2.  **Processing Queue**: Kafka.
3.  **Encoder**: Worker nodes (Ffmpeg).
4.  **Metadata DB**: Sharded MySQL (Vitess).
5.  **Blob Storage**: GCS/S3.

## 3. Deep Dive

### A. Video Upload Flow
1.  User sends file to **Upload Service**.
2.  File stored in **Blob Storage** (Original raw).
3.  Message added to **Encoding Queue**.
4.  **Encoder** picks up job:
    *   Checks for duplicates (Hash matching).
    *   Generates Thumbnails.
    *   Transcodes to .mp4, .webm, different resolutions.
5.  New files stored in Blob Storage.
6.  Metadata (URLs/Size) updated in DB.

### B. Deduplication
*   Compute SHA-256 of file.
*   Complex: User uploads 10s clip of a movie.
*   **Content ID**: Fingerprinting audio/video frames to match against Copyright DB.

### C. Scaling Metadata (Vitess)
*   YouTube uses MySQL.
*   Trillions of videos/comments.
*   **Sharding Key**: `VideoID`.
*   All comments for a video sit on the same shard for fast retrieval.
*   **Master-Slave Routing**: Writes to Master, Reads from Replicas.

### D. Streaming Optimization
*   **Range Requests**: HTTP Header `Range: bytes=0-1000`. Allows seeking to middle of video without downloading start.
*   **Edge Caching**: Popular videos cached at ISP/Edge. Long-tail videos fetched from origin.
