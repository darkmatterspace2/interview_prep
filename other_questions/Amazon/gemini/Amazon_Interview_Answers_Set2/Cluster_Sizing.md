# Big Data Compute Sizing & Capacity Planning Interview Questions

## A. Cluster Sizing Fundamentals

#### 31. You have **1 TB/day** of raw data. How do you estimate cluster size?
**Estimation Framework:**
1.  **Replication (Storage):** 1 TB raw = 3 TB in HDFS (3x replication).
2.  **Expansion (Compute):** ETL expands data (decompression, Java objects). Rule of thumb: Need ~3-4x RAM of the "working set".
3.  **Shuffle/Spill:** 30% overhead for shuffle space on disk.
4.  **Compression:** Parquet (Snappy) compresses ~3-4x.
**Sizing:**
*   If processing all 1TB in *one* batch: 1TB / 4 (Compression) = 250GB on disk. In memory (deserialized), it might bloom back to 1TB.
*   *Target:* To process 1TB efficiently in memory, you want ~1TB+ aggregate RAM (or process in chunks).
*   *Nodes:* If using r5.4xlarge (128GB RAM), you need ~8-10 nodes for full in-memory processing.

#### 32. How does **data expansion** affect sizing? (raw → parsed → joined → aggregated)
*   **Raw (Gzip/JSON):** Heavy compression. Small on disk.
*   **Parsed (DataFrame):** In-memory row objects. Massive expansion (10x+ vs gzip).
*   **Joined:** Cross products or wide tables can double/triple width.
*   **Aggregated:** Huge reduction.
*   *Sizing Implication:* Size for the *peak* stage (usually the Join), not the input or output size.

#### 33. What factors decide Number of nodes, RAM, and CPU?
*   **RAM:** Drives *can we run this without spilling?* (Cache-heavy jobs need high RAM).
*   **CPU:** Drives *how fast will it complete?* (Parquet encoding/decoding is CPU heavy).
*   **Nodes:** Throughput. More nodes = more network bandwidth and parallelism.

#### 34. When do you choose **more small nodes vs fewer large nodes**?
*   **Fewer Large Nodes:**
    *   *Pro:* Less shuffle network traffic (more data local).
    *   *Con:* Losing one node is a massive capacity hit (20%). GC pauses can be huge on giant heaps (>64GB).
*   **More Small Nodes:**
    *   *Pro:* Failure impact is small (1%). Granular scaling.
    *   *Con:* High network shuffle traffic.

---

## B. Memory & Executor Planning

#### 35. How do you calculate executor memory?
**Formula:** `Node RAM / Executors per Node`.
*   Leave 10-15% for OS overhead.
*   *Example:* 64GB Node. 4 Executors.
*   64GB - 4GB (OS) = 60GB.
*   60 / 4 = **15GB per Executor**.

#### 36. Why can giving more memory to Spark sometimes make jobs slower?
**Garbage Collection (GC):**
*   Java GC on a huge heap (e.g., 100GB) takes a long time "Stop-the-world" pause.
*   Spark freezes while GC cleans up.
*   *Sweet Spot:* Typically 30GB - 40GB per executor is the limit before GC becomes painful.

#### 37. Driver vs Executor memory — what runs where?
*   **Executor:** Runs tasks, processes data partitions. Needs RAM proportional to partition size.
*   **Driver:** Orchestrates calls. Needs RAM only if you call `collect()` or `broadcast()` large tables.

#### 38. What happens if executor memory is too small?
*   **Spill:** Data spills to disk. Performance crashes.
*   **OOM:** `java.lang.OutOfMemoryError: Java heap space`. Task fails.

#### 39. How many executors should a node have?
**Constraint:** Cores.
*   If Node has 16 vCPUs.
*   Ideal: 3-5 cores per executor.
*   Solution: 3 Executors (5 cores each) = 15 cores utilized. 1 core left for OS.

---

## C. CPU & Parallelism

#### 40. How many cores per executor is ideal — and why?
**Ideal:** 4 to 5 cores.
*   *Why?*
    *   **1 Core:** No multithreading benefit within executor.
    *   **>5 Cores:** Thread contention becomes inefficient.
    *   5 is the "Magic Number" for consistent HDFS client throughput.

#### 41. CPU-bound vs IO-bound Spark jobs — how do they affect sizing?
*   **CPU-Bound (JSON parsing, ML, Complex Math):** Add more Cores. High CPU utilization, low disk usage.
*   **IO-Bound (Simple Selects, moving data):** Add more RAM (cache) or faster Disks (NVMe). CPU is idle waiting for data.

#### 42. How does `spark.sql.shuffle.partitions` impact performance?
*   Controls number of reducers.
*   *Too Low:* Output partitions are huge (>2GB), causing OOM.
*   *Too High:* Millions of tiny tasks. Scheduler overhead dominates.

#### 43. When does increasing parallelism stop helping?
When **Amdahl's Law** hits.
*   The driver (serial portion) becomes the bottleneck.
*   Or when partitions are so small (< 1MB) that task startup time (100ms) > task execution time (10ms).

---

## D. Network & IO Considerations

#### 44. Why does network bandwidth matter in Spark jobs?
**Shuffle.**
*   During a wide transformation, nearly 100% of data might move across the network.
*   10TB shuffle on 1Gbps network takes forever. 10Gbps/25Gbps is mandatory for big data.

#### 45. How does shuffle stress network and disk?
*   **Disk:** Map tasks write intermediate files to local disk. Reduce tasks read them. Random I/O storm.
*   **Network:** All-to-all communication.

#### 46. Local SSD vs remote storage — trade-offs.
*   **Local SSD (Ephemeral):** Extremely fast for **scratch/shuffle** space. (e.g., AWS `i3` instances).
*   **Remote (EBS):** Slower, network constrained. Good for persistence, bad for spill.

#### 47. How does compression affect CPU vs IO?
*   **Trade-off:** High compression (GZIP) saves Disk/Network I/O but burns CPU (decompression).
*   **Strategy:** If network is bottleneck, Compress more (GZIP). If CPU is bottleneck, Compress less (Snappy/LZ4).

---

## E. Cost Optimization Scenarios

#### 48. Your cluster cost doubled after data growth. How do you reduce cost without breaking SLAs?
1.  **Spot Instances:** Move stateless worker nodes to Spot (save 70%). Keep Driver/Master on On-Demand.
2.  **Autoscaling:** Aggressively scale down when idle.
3.  **Storage Policies:** Move cold data to S3 IA/Glacier immediately.
4.  **Code Optimization:** Tuning the job to run 50% faster saves 50% compute cost directly.

#### 49. Spot vs on-demand nodes — risks and design.
*   **Risk:** Spot node reclamation (AWS takes it back).
*   **Design:**
    *   Don't put Driver on Spot.
    *   Spark handles worker loss, but it retries tasks. Too many losses = Job delayed.
    *   Use "Spot Fleet" to diversify instance types and reduce reclamation probability.

#### 50. Auto-scaling vs fixed clusters — when to choose what?
*   **Fixed:** Consistent SLAs, predictable workloads (e.g., Hourly ingestion). Cheaper if using Reserved Instances.
*   **Auto-scaling:** Spiky workloads (e.g., Ad-hoc queries, huge monthend jobs).

---

## F. Real-World Sizing Scenarios

#### 51. Batch job processes **500 GB**, SLA = **2 hours**. How do you approach sizing?
Base estimation:
*   Spark handles ~3-5 GB per core/hour for complex tasks.
*   Target: 500GB / 2 hours = 250GB/hour throughput.
*   Cores needed: 250 / 4 = **~60 Cores**.
*   Config: 4 Nodes x 16 Cores.

#### 52. Daily ETL runs for 6 hours instead of 2. Debug vs scale — what do you do first?
**First: Debug.**
*   Scaling a skewed job achieves nothing (1 core is stuck, adding 100 nodes helps 0%).
*   Check Spark UI for skew, bad join strategy, or stalled tasks.
*   *Only scale* if all cores are evenly utilized at 100%.

#### 53. One team wants more memory; another wants more nodes. How do you decide?
*   **Memory Request:** Usually means OOM/Spill issues. Check if they can tune partitions first.
*   **Nodes Request:** Usually means "Job is too slow".
*   *Decision:* Analyze resource utilization. If CPU < 20% but RAM full, choose High-Mem instances (r5). If CPU 100%, choose Compute-Optimized (c5).

#### 54. Streaming job with 50K events/sec spikes to 200K. How do you plan headroom?
*   Provision for peak (200K) + 20% buffer.
*   Or use **Auto-scaling** (Kinesis scaling + EMR scaling) if spikes are predictable.
*   *Lag:* Ensure `ProcessingRate > InputRate` to drain the backlog after a spike.

---

## G. Failure & Capacity Edge Cases

#### 55. What happens if one node is much slower than others?
**Speculative Execution** (`spark.speculation=true`).
*   Spark notices the straggler task.
*   It launches a *copy* of that task on a fast node.
*   Whichever finishes first wins; the other is killed.

#### 56. How does speculative execution help?
Mitigates hardware degradation (noisy neighbors, failing disk) but *does not help* with data skew (because the copy will also be processed slowly due to data volume).

#### 57. How do you size clusters for backfills?
Backfills process 30 days of data at once.
*   **Strategy:** Don't size a 30x cluster. Use the *same* cluster but iterate.
*   Run 1 day at a time (Parallelism=1) or 5 days at a time.
*   Or use a transient autosealing cluster just for the backfill.

#### 58. What is the impact of GC tuning?
*   G1GC (Garbage First) is generally better for Spark than ParallelGC.
*   Tuning generations (Eden/Survivor space) can prevent full GC pauses for short-lived objects.

#### 59. How do you detect underutilized clusters?
*   **Ganglia/CloudWatch:** CPU usage average.
*   If average CPU < 30% during job run, you are over-provisioned (burning money). reduce node count.

---

## H. Trade-off & Design Judgment

#### 60. Scale up vs scale out — real examples.
*   **Scale Up (Vertical):** 1 Node with 1TB RAM.
    *   *Good for:* High-shuffle jobs (no network overhead).
    *   *Bad:* Single point of failure. Max cap.
*   **Scale Out (Horizontal):** 100 Nodes with 10GB RAM.
    *   *Good for:* Reliability, infinite scale.
    *   *Bad:* Shuffle network storm.

#### 61. When is Spark not the right tool?
*   **Low Latency lookup:** "Get User ID 5" (Use HBase/DynamoDB).
*   **Small Data:** Processing 50MB CSV (Use Pandas/Python - faster startup).
*   **Complex Transactions:** ACID updates (Use RDBMS).

#### 62. How do you explain cluster sizing to non-technical stakeholders?
"Think of it like moving a house. 
*   **Nodes** are the number of trucks.
*   **RAM** is how big the boxes are.
*   **CPU** is how fast the movers walk.
If we have too few trucks (Nodes), it takes all day. If boxes are too small (Low RAM), we waste time packing/unpacking (Spill). We need the right balance to move the house in 2 hours for the best price."

#### 63. Performance vs cost — how do you balance?
**The "Knee" of the Curve.**
*   Plot Cost vs Time.
*   Usually, adding nodes reduces time linearly up to a point. After that, diminishing returns (network overhead).
*   *Stop scaling* when the cost to save 10 minutes becomes disproportionately high.
