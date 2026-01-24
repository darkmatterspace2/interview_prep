# Facebook Data Model (Social Network)

This document outlines the data model for a social graph system like Facebook.

## 1. Core Entities
1.  **User**: The central node.
2.  **Friendship**: Bidirectional relationship (Graph Edge).
3.  **Post**: Content created by user.
4.  **Reaction/Like**: Enum type (Like, Love, Wow, etc.).
5.  **Comment**: Hierarchical text replies.

## 2. Logical SQL Schema

```sql
-- 1. Users
CREATE TABLE Users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Friendships (Bidirectional)
-- Represented as two rows (A->B, B->A) for easier querying OR one row with least ID first.
-- Let's use two rows for simple "Select friends of X".
CREATE TABLE Friendships (
    user_id1 BIGINT,
    user_id2 BIGINT,
    status ENUM('PENDING', 'ACCEPTED', 'BLOCKED'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id1, user_id2),
    FOREIGN KEY (user_id1) REFERENCES Users(user_id),
    FOREIGN KEY (user_id2) REFERENCES Users(user_id)
);

-- 3. Posts
CREATE TABLE Posts (
    post_id BIGINT PRIMARY KEY,
    author_id BIGINT,
    content TEXT,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES Users(user_id)
);

-- 4. Comments (Adjacency List for threading)
CREATE TABLE Comments (
    comment_id BIGINT PRIMARY KEY,
    post_id BIGINT,
    user_id BIGINT,
    parent_comment_id BIGINT NULL, -- For nested replies
    text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES Posts(post_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- 5. Likes/Reactions
CREATE TABLE PostLikes (
    user_id BIGINT,
    post_id BIGINT,
    reaction_type VARCHAR(20), -- 'LIKE', 'LOVE', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, post_id)
);
```

## 3. Key Design Patterns

### A. The "News Feed" Problem
Fetching posts from all 500 friends sorted by time.

**Pull Model (Fan-out on Read):**
1.  Get friend IDs.
2.  `SELECT * FROM Posts WHERE author_id IN (friend_ids) ORDER BY time LIMIT 10`.
    *   Good for small scale. Slow if user has thousands of friends.

**Push Model (Fan-out on Write):**
1.  User A posts.
2.  System writes Post ID to a separate "Feed" table for every follower/friend.
3.  User B reads their pre-computed feed table.
    *   Good for read-heavy systems, bad for celebrities (millions of writes per post).

### B. Graph Database
For complex queries like "Friends of Friends who like Jazz", a Relational DB requires heavy joins.
**Solution**: Use Neo4j or a Graph Service where nodes = Users, edges = Friendships.
`MATCH (u:User)-[:FRIEND]->(f:User)-[:FRIEND]->(fof:User) RETURN fof`
