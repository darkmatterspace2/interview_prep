# FAANG Design Guide (Round 2.3 - System & OOD)

This round evaluates your ability to build scalable, maintainable, and robust systems. It is usually split into **Low-Level Design (LLD)** and **High-Level Design (HLD)**.

---

## Part A: Object-Oriented Design (LLD)

**Goal**: Convert a vague requirement into a clean class diagram with correct relationships.

### 1. LLD Process (The 5-Step Formula)
1.  **Clarify Requirements**: "Is it a paid parking lot?", "Do we need multiple vehicle types?".
2.  **Identify Actors**: "Customer", "Admin", "System".
3.  **Identify Use Cases**: "Take Ticket", "Pay Ticket", "Scan Entry".
4.  **Define Classes**: `ParkingLot`, `Spot`, `Vehicle`, `Ticket`, `Gate`.
5.  **Define Relationships**:
    *   **Composition**: `ParkingLot` *has* `Floors`.
    *   **Inheritance**: `Car` *is a* `Vehicle`.
    *   **Association**: `Ticket` *is associated with* `Spot`.

### 2. Crucial Design Patterns for LLD
*   **State Pattern**: Essential for Order Management, Elevator Systems, or Vending Machines. Transitioning from `Idle` -> `Moving` or `Created` -> `Paid` -> `Shipped`.
*   **Strategy Pattern**: For changing algorithms (e.g., `PricingStrategy`, `AssignSpotStrategy`).
*   **Factory Pattern**: To create objects like `VehicleFactory.createType("TRUCK")`.

### 3. Common LLD Problems
*   **Parking Lot**: Focus on hierarchy (`ParkingLot` -> `Floor` -> `Spot`) and concurrency (two cars taking same spot).
*   **Elevator System**: Focus on the scheduling algorithm and State management.
*   **Tic-Tac-Toe / Chess**: Focus on `Board`, `Player`, `Move`, and `GameStatus` logic.

### 4. UML Basics (Whiteboard Ready)
*   **Box**: Class.
*   **Solid Line + Diamond**: Composition (Strong ownership).
*   **Dotted Line**: Dependency.

---

## Part B: System Design (HLD)

**Goal**: Design a system that scales to millions of users.

### 1. HLD Process (The Template)
1.  **Functional Requirements**: What does the system DO? (e.g., User posts tweet, follows user).
2.  **Non-Functional Requirements**: CAP Theorem choices. High Availability? Low Latency? Consistency?
3.  **Capacity Estimation** (Back-of-the-envelope):
    *   "10M DAU, each posts 2 tweets/day = 20M tweets/day".
    *   "Approx 230 tweets/sec. Peak = 2-3x = 600/sec".
4.  **API Design**: `POST /tweet`, `GET /feed`.
5.  **High-Level Diagram**: Draw the boxes (LB, App Server, DB, Cache).
6.  **Deep Dive**: Pick one component to optimize (e.g., "How does the Feed generation work?").

### 2. Core Building Blocks

#### Load Balancer (LB)
*   Distributes traffic. Algorithms: Round Robin, Least Connections, Consistent Hashing.

#### Caching (Redis/Memcached)
*   **Read-Through**: App checks cache, if miss, checks DB and populates cache.
*   **Eviction Policies**: LRU (Least Recently Used) is standard.
*   *Use Case*: Storing session data, User profiles, popular tweets.

#### Database Choices
*   **SQL (RDBMS)**: Structured data, ACID transactions needed. (e.g., Payments, User Auth). *MySQL, Postgres*.
*   **NoSQL**: Unstructured, High Write throughput, Flexible schema. (e.g., Chat logs, Activity stream). *MongoDB, Cassandra, DynamoDB*.

#### Message Queues (Kafka/RabbitMQ)
*   **Decoupling**: Producer sends message, Consumer processes it asynchronously.
*   *Use Case*: Processing video uploads, Sending notifications, Analytics logging.

### 3. Concepts to Master

*   **Sharding (Partitioning)**: Splitting a large DB into smaller chunks based on a key (e.g., `User_ID`).
    *   *Challenge*: Hot partitions (Justin Bieber problem).
*   **Replication**: Master-Slave architecture. Write to Master, Read from Slaves.
*   **CAP Theorem**:
    *   **CP** (Consistency/Partition Tolerance): Banking apps.
    *   **AP** (Availability/Partition Tolerance): Social media feeds. (It's okay if you see a like 2 seconds late, but the site shouldn't crash).

### 4. Standard HLD Problems

*   **Design Twitter/Facebook Feed**:
    *   *Key*: Fan-out service (Push vs Pull model). Push to active users' timelines.
*   **Design URL Shortener (TinyURL)**:
    *   *Key*: Hashing strategy (Base62 encoding), Handling collisions.
*   **Design Uber (Ride Hailing)**:
    *   *Key*: QuadTree/Geohash for location, WebSocket for real-time updates.

---

## Summary Checklist for Round 2.3

*   [ ] Can I draw a Class Diagram for a Parking Lot in 10 mins?
*   [ ] Do I know when to use NoSQL vs SQL?
*   [ ] Can I explain Consistent Hashing?
*   [ ] Do I understand why we need a Message Queue in a system?
