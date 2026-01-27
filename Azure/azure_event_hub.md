# Azure Event Hub Interview Questions

## Beginner Level

1.  **What is Azure Event Hubs?**
    *   **Answer:** Azure Event Hubs is a big data streaming platform and event ingestion service. It can receive and process millions of events per second. Data sent to an event hub can be transformed and stored by using any real-time analytics provider or batching/storage adapters.

2.  **What are the key components of Azure Event Hubs?**
    *   **Answer:**
        *   **Namespace:** A management container for Event Hubs.
        *   **Event Producer:** Any entity that sends data to an event hub (e.g., HTTPS, AMQP).
        *   **Partitions:** Sequences of events that are ordered within an event hub.
        *   **Consumer Groups:** A view (state, position, or offset) of an entire event hub.
        *   **Throughput Units:** Pre-purchased units of capacity.
        *   **Event Receivers:** Entities that read event data from an event hub.

3.  **Explain the difference between Azure Event Hubs and Azure IoT Hub.**
    *   **Answer:**
        *   **Event Hubs:** Designed for big data streaming and event ingestion. Focuses on high throughput. Unidirectional (Cloud-to-Device is not natively supported).
        *   **IoT Hub:** Designed specifically for IoT device connectivity. Supports bidirectional communication (command and control), device management, and device twins.

4.  **What is a Partition in Event Hubs?**
    *   **Answer:** A partition is an ordered sequence of events that is held in an Event Hub. Partitions enable running multiple parallel logs for consumers. They provide horizontal scalability. The number of partitions is specified at creation and cannot be changed easily (depending on the tier).

5.  **What is a Consumer Group?**
    *   **Answer:** A consumer group acts as a view (state, position, or offset) of an entire event hub. It enables consuming applications to each have a separate view of the event stream and read the stream independently at their own pace and with their own offsets.

6.  **What protocols does Azure Event Hubs support for sending events?**
    *   **Answer:** It primarily supports:
        *   **AMQP (Advanced Message Queuing Protocol):** Efficient, reliable, standard.
        *   **HTTPS:** Simple, firewall-friendly, but less efficient for high throughput.
        *   **Apache Kafka Protocol:** Allows Kafka clients to talk to Event Hubs.

7.  **What is the retention period in Azure Event Hubs?**
    *   **Answer:** The retention period is the amount of time that data remains accessible in the stream.
        *   **Basic Tier:** 1 day.
        *   **Standard Tier:** 1 to 7 days.
        *   **Premium/Dedicated:** Up to 90 days (with Event Hubs Capture or potentially extended retention features).

8.  **What is Event Hubs Capture?**
    *   **Answer:** A feature that allows you to automatically capture the streaming data in Event Hubs and save it to an Azure Blob storage or Azure Data Lake Store account. It enables long-term retention and batch processing.

9.  **How do you authenticate to Azure Event Hubs?**
    *   **Answer:**
        *   **Shared Access Signatures (SAS):** Using keys and policies defined on the namespace or event hub.
        *   **Azure Active Directory (Azure AD):** Integrating with Azure RBAC for more secure, identity-based access.

10. **What is a Throughput Unit (TU)?**
    *   **Answer:** A unit of capacity that controls the amount of data you can ingest and egress.
        *   **Ingress:** Up to 1 MB/s or 1000 events/s per TU.
        *   **Egress:** Up to 2 MB/s or 4096 events/s per TU.

## Medium Level

11. **Explain the concept of "at-least-once" delivery in Event Hubs.**
    *   **Answer:** Event Hubs guarantees that events are accepted and stored durably. However, in rare network scenarios or failures, a consumer might receive a duplicate event. Deduplication logic must be handled by the consumer application if strict "exactly-once" processing is required.

12. **How does scaling work in Azure Event Hubs?**
    *   **Answer:**
        *   **Throughput Units (TUs):** For Standard tier, you manually scale TUs or use Auto-inflate to automatically scale up.
        *   **Processing Units (PUs):** For Premium tier.
        *   **Capacity Units (CUs):** For Dedicated clusters.
        *   **Partitions:** Scaling consumption involves adding more partitions so more concurrent readers (one per partition per consumer group) can process data.

13. **What is the difference between the Basic, Standard, and Premium tiers?**
    *   **Answer:**
        *   **Basic:** strict 1 consumer group, 1 day retention, no Capture, no Kafka endpoint.
        *   **Standard:** up to 20 consumer groups, up to 7 days retention, Capture available, Kafka endpoint available.
        *   **Premium:** Single-tenant-like performance (isolation), dynamic scaling with PU, extended retention (> 7 days).

14. **How does Event Hubs support Apache Kafka?**
    *   **Answer:** Event Hubs provides an endpoint compatible with the Kafka 1.0+ producer and consumer APIs. This means you can change the connection string in your existing Kafka applications to point to Event Hubs without changing your code or running your own Zookeeper/Kafka clusters.

15. **What is Auto-inflate?**
    *   **Answer:** Auto-inflate is a feature in the Standard tier that automatically scales up the number of Throughput Units (TUs) to meet usage needs. It prevents throttling when ingress rates exceed the pre-allocated capacity, up to a defined maximum limit.

16. **How do you handle ordering of events in Event Hubs?**
    *   **Answer:** Events are ordered *within a partition* by their offset. If global ordering is required, you must send all events to a single partition (Partition Key), but this limits throughput. For high throughput, ordering is only guaranteed per partition key.

17. **What is a Partition Key and when should you use it?**
    *   **Answer:** A value used to map incoming event data to a specific partition. If you specify a partition key, all events with that key are stored together in the same partition in order. Use it when related events must be processed together or in order (e.g., all events for "DeviceID-123").

18. **Explain the role of the Checkpointing mechanism in event processing.**
    *   **Answer:** Checkpointing is the process by which readers mark or commit their position within a partition sequence. It is usually managed by the client library (e.g., Event Processor Client). If a reader crashes, a new instance can resume reading from the last checkpointed offset rather than from the beginning.

19. **What happens if you exceed your Throughput Units?**
    *   **Answer:** You will receive a `ServerBusyException` (throttling). Ingress or egress requests will be rejected until the load drops or you scale up (add more TUs or enable Auto-inflate).

20. **Can you delete specific events from an Event Hub?**
    *   **Answer:** No. Event Hubs is an append-only log. Events are immutable once ingested. They are only removed when the retention period expires. You cannot imperatively delete a specific message.

## Advanced Level

21. **Describe the disaster recovery strategies for Azure Event Hubs (Geo-DR).**
    *   **Answer:** Azure Event Hubs Geo-Disaster Recovery pairs a primary namespace with a secondary namespace in a different region. It replicates metadata (configurations), not the actual data. If the primary region goes down, you failover to the secondary. The application connection string uses an alias that automatically points to the active namespace. **Note:** Data inside the hubs is *not* replicated in Standard Geo-DR; only the infrastructure/metadata.

22. **How would you architecture a solution to process events that requires "Exactly-Once" processing using Event Hubs?**
    *   **Answer:** Event Hubs natively guarantees at-least-once. To achieve exactly-once:
        *   Use idempotent consumers: Ensure the processing logic can handle duplicates without side effects.
        *   Store offsets and output state atomically: For example, using Azure Stream Analytics or spark structured streaming with checkpointing to a transactional store.
        *   If using custom code, save the processed offset and the result in a single transaction to a database.

23. **What is the difference between Event Hubs and Event Grid?**
    *   **Answer:**
        *   **Event Hubs:** A *streaming* service (Big Data pipeline). Pull-model (consumers poll for data). Preserves order (in partitions). High throughput.
        *   **Event Grid:** An *eventing* service (Reactive programming). Push-model (pushes events to webhooks/handlers). Focuses on individual discrete events, not streams. Filtering and routing are key features.

24. **How do you secure Event Hubs in a VNET?**
    *   **Answer:** Use **VNet Service Endpoints** (Standard tier and above) to restrict access to the Event Hub namespace to specific subnets. Or use **Private Link** (Private Endpoints) to assign a private IP address from your VNet to the Event Hubs namespace, ensuring traffic stays on the Microsoft backbone network.

25. **Explain the "Event Processor" pattern (or Event Processor Client).**
    *   **Answer:** The Event Processor Client (in .NET/Java/Python SDKs) simplifies consuming events. It manages:
        *   **Load Balancing:** Distributes partitions among available worker instances.
        *   **Checkpointing:** Periodically saves the read position to a storage account (blob).
        *   **Fault Tolerance:** If a worker dies, others pick up its partitions.

26. **What are the limitations of Event Hubs Capture?**
    *   **Answer:**
        *   Latency: It is not real-time; it captures based on a time window (e.g., every 5 mins) or size window (e.g., 100 MB).
        *   Format: Output is strictly Avro format (requires tools to read/convert if you need JSON/CSV).
        *   Cost: Additional cost for the Capture feature and the storage used.

27. **How does "Availability Zones" support work in Event Hubs?**
    *   **Answer:** When you create an Event Hubs namespace in a region that supports Availability Zones, the service automatically spreads its compute and storage resources across three physically separated zones. This provides resilience against data center failures transparently.

28. **Detailed troubleshooting: You are seeing high latency in your consumer application. What do you check?**
    *   **Answer:**
        *   **Consumer lag:** Compare the last enqueued offset vs. the processed offset.
        *   **Processing logic:** Is the `ProcessEvent` handler taking too long? Is it blocking?
        *   **Prefetch count:** Is the prefetch count too low (chattiness) or too high (memory pressure)?
        *   **Partition count:** Are there enough partitions for the number of parallel consumers?
        *   **Throttling:** Is the namespace hitting TU limits?

29. **How would you handle "Poison Messages" in an Event Hub stream?**
    *   **Answer:** Since you cannot delete a bad message, the consumer must handle it.
        *   **Catch & Log:** Wrap processing in try-catch blocks. If a message causes a crash, log the error and index/offset, then *skip* the message (move the checkpoint forward) so the processor doesn't get stuck in a loop.
        *   **Dead Letter Queue (DLQ):** Manually send the failed payload to a separate storage (Blob/Queue) for offline analysis, then proceed.

30. **Explain the cost structure of Azure Event Hubs.**
    *   **Answer:**
        *   **Basic/Standard:** Throughput Units (hourly) + Ingress Events (per million events) + Capture (hourly + storage).
        *   **Premium:** Processing Units (hourly) + Storage (over limit).
        *   **Dedicated:** Capacity Units (fixed monthly/hourly cost).
        *   *Note:* Egress events (readers) are generally covered by the TU content, but specialized data transfers might incur network costs.
