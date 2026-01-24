# Netflix System Design (Streaming)

## 1. Requirements
*   Upload/Processing of Video (Internal).
*   Streaming Video (Public).
*   Search & Recommendation.

## 2. Architecture

### Control Plane vs Data Plane
*   **Control Plane (AWS)**: Website, Login, Billing, Recommendations, "Play" button logic. Handles light traffic (JSON).
*   **Data Plane (Open Connect CDN)**: Serves the actual Video Files. Handles massive bandwidth (Terabits/sec).

### Services
1.  **Asset Service**: Metadata (Actors, Genre).
2.  **Transcoding Service**: Converts raw `.mov` to `.mp4` (H.264, VP9) at various bitrates (480p, 1080p, 4k).
3.  **Recommendation Engine**: Machine Learning models (Spark/TensorFlow).

## 3. Deep Dive

### A. Video Processing (Transcoding)
*   Raw master file is huge (TB).
*   **Chunking**: Split video into 5-minute chunks.
*   **Parallel Processing**: Process chunks in parallel on thousands of EC2 instances.
*   **DAG Workflow**: Inspect -> Split -> Transcode(formats) -> Merge -> QCD.

### B. Adaptive Bitrate Streaming (ABS)
*   Device asks for a manifesto file (`.m3u8`).
*   Manifesto lists URLs for different qualities (Low, Med, High).
*   Client Player monitors bandwidth.
    *   Slow net? Request "Low" chunk.
    *   Fast net? Request "High" chunk.
*   **Pre-computing**: Netflix pre-transcodes all resolutions. YouTube does some on-the-fly, but Netflix goes for quality.

### C. CDN Designing (Open Connect)
*   Netflix builds custom hardware (OCAs) placed inside ISP data centers.
*   **Proactive Caching**: "Stranger Things" S2 is coming out? Push the file to the ISP boxes at 3 AM *before* launch. user fetches from local ISP box, not crossing internet backbone.
