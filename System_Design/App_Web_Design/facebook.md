# Facebook System Design (News Feed)

## 1. Requirements

### Functional
*   Post updates (Text, Image).
*   Add Friends.
*   View News Feed (Aggregated posts from friends).

### Non-Functional
*   Latencies: Feed generation < 200ms.
*   Lag: Posted content should appear reasonably fast (Eventual Consistency ok).
*   Scale: Billion users.

## 2. API Design
*   `GET /v1/feed?cursor=...`: Get timeline.
*   `POST /v1/post`: Create content.

## 3. High-Level Design

### Core Services
1.  **User Service**: Metadata.
2.  **Graph Service**: Manages "A follows B".
3.  **Post Service**: Stores content (Bigtable/Cassandra for scale).
4.  **Feed Generation Service**: The complex engine.

## 4. Deep Dive: Feed Generation

### Approach 1: "Pull" Model (Fan-out on Load)
*   User requests feed.
*   System queries all ~500 friends: `Get top 5 posts from each`.
*   Merge and Sort in memory.
*   **Pros**: Simple storage. Real-time.
*   **Cons**: Very slow read. N queries per feed load.

### Approach 2: "Push" Model (Fan-out on Write) — *Standard for Standard Users*
*   User A posts.
*   System finds all followers of A.
*   Insert PostID into every follower's pre-computed "Feed List" (Redis/Cassandra).
*   When User B loads feed, just read their Feed List. O(1) read.
*   **Pros**: Extremely fast reads.
*   **Cons**: "Justin Bieber" problem. If a user has 100M followers, writing to 100M lists takes long.

### Hybrid Approach (Winner)
*   **Regular Users**: Use Push Model.
*   **Celebrities**: Use Pull Model.
*   When User B loads feed: Merge their "Push" feed + fetch updates from "Celebrities" they follow.

## 5. Storage (Social Graph)
*   **SQL**: Too many joins (`Users JOIN Friends JOIN Friends`).
*   **Graph DB (Neo4j)**: Good for traversal.
*   **Facebook's TAO**: Custom distributed graph store (memcache + MySQL backed) optimized for reads.
