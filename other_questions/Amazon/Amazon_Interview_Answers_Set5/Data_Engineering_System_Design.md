# Data Engineering System Design – Terabytes Daily Pipeline

> **Interview Scenario:** Design a data pipeline that handles **terabytes of data daily**. Cover architecture for both **AWS** and **Azure**, discuss decisions, trade-offs, and key considerations.

---

## 📌 Problem Statement

**Scenario:** You're a Senior Data Engineer at a company processing 5-10 TB of daily data from multiple sources (transactional DBs, streaming events, APIs, file drops). Design an end-to-end pipeline for ingestion, processing, storage, and consumption.

**Key Requirements:**
- **Volume:** 5-10 TB/day (growing 30% YoY)
- **Velocity:** Mix of batch (hourly) and near-real-time (5-min latency)
- **Variety:** Structured (RDBMS), Semi-structured (JSON/Avro), Unstructured (logs)
- **SLA:** 99.9% availability, < 1 hour data freshness for dashboards

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA SOURCES                                    │
│  [OLTP DBs] [Event Streams] [APIs] [File Drops] [IoT Sensors]               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INGESTION LAYER                                    │
│  AWS: Kinesis | Kafka MSK | DMS | S3 Transfer                               │
│  Azure: Event Hub | Kafka | DFS | ADF                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          RAW / BRONZE LAYER                                  │
│  AWS: S3 (Parquet/Delta)           Azure: ADLS Gen2 (Delta)                  │
│  Schema-on-Read | Immutable | Partitioned by date                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PROCESSING LAYER                                     │
│  AWS: EMR/Glue (Spark) | Lambda (small)                                      │
│  Azure: Databricks | Synapse Spark | Functions                               │
│  Batch: Hourly/Daily   |   Stream: Micro-batch (5-min)                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CURATED / SILVER → GOLD LAYER                           │
│  Silver: Cleaned, Deduplicated, Typed                                        │
│  Gold: Aggregated, Business-ready, Star Schema                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CONSUMPTION LAYER                                    │
│  AWS: Athena | Redshift | QuickSight                                         │
│  Azure: Synapse SQL | Power BI | Purview                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1️⃣ Ingestion Layer Design

### Streaming Ingestion

| Aspect | AWS | Azure |
|--------|-----|-------|
| **Service** | Kinesis Data Streams / Kafka (MSK) | Event Hub / Kafka on HDInsight |
| **Throughput** | Kinesis: 1 MB/s per shard | Event Hub: 1 MB/s per TU |
| **Retention** | Kinesis: 7 days (extended 365 days) | Event Hub: 7 days (90 days capture) |
| **Schema** | Schema Registry with Glue | Schema Registry (Event Hub) |
| **Cost Model** | Per shard-hour + PUT payload | Per Throughput Unit + ingress |

**Trade-off: Kinesis vs Kafka (MSK)**
| Factor | Kinesis | Kafka MSK |
|--------|---------|-----------|
| Operational Overhead | Serverless, zero ops | Managed but cluster sizing needed |
| Cost at Scale | Expensive (per shard) | Cheaper at high volume |
| Ecosystem | AWS-native | Open ecosystem (Flink, Connect) |
| **Decision:** | < 50 shards, simple use | > 50 shards, complex enrichment |

### Batch Ingestion

| Aspect | AWS | Azure |
|--------|-----|-------|
| **CDC** | DMS (Change Data Capture) | ADF + Debezium |
| **File Transfer** | S3 Transfer Family (SFTP) | ADLS + ADF |
| **API Ingestion** | Lambda + EventBridge | Logic Apps / Functions |
| **Bulk Load** | Glue ETL, DataSync | ADF Copy Activity |

**Interview Insight:** For CDC at TB scale:
- **AWS DMS** streams directly to Kinesis (real-time) or S3 (batch).
- **Azure ADF** with Debezium connector captures changes at source DB level.

---

## 2️⃣ Storage Layer Design

### Why Object Storage is the Foundation?

| Reason | Details |
|--------|---------|
| **Cost** | S3/ADLS: ~$0.023/GB/month (Standard) |
| **Durability** | 99.999999999% (11 9s) |
| **Scale** | Infinite horizontal scaling |
| **Compute Decoupled** | Spark, Presto, Snowflake all read from it |

### File Format Decisions

| Format | Use Case | Compression | Splitable? |
|--------|----------|-------------|------------|
| **Parquet** | Columnar analytics | Snappy/Zstd | ✅ Yes |
| **Delta Lake** | ACID, Time Travel, Schema Evolution | Zstd | ✅ Yes |
| **Avro** | Schema evolution, streaming | Snappy | ✅ Yes |
| **JSON** | Raw landing, debugging | Gzip | ❌ No |

**Interview Best Practice:**
- **Bronze:** Raw JSON/Avro for auditability
- **Silver/Gold:** Delta Lake or Iceberg (ACID, time travel, compaction)

### Partitioning Strategy (Critical for TB-scale)

```python
# Good Partitioning
/data/orders/year=2024/month=02/day=07/

# Bad Partitioning (Over-partitioned)
/data/orders/year=2024/month=02/day=07/hour=10/minute=30/

# Hive-style vs Path-style
# Hive: year=2024/month=02 → Auto-discovered by Glue/Hive
# Path: 2024/02/07/ → Requires explicit schema
```

**Rule of Thumb:**
- Partition files should be **128 MB – 1 GB**
- Too small = metadata overhead (small file problem)
- Too large = long processing per file

---

## 3️⃣ Processing Layer Design

### Batch Processing

| Aspect | AWS | Azure |
|--------|-----|-------|
| **Engine** | EMR (Spark, Hive, Presto) | Databricks / Synapse Spark |
| **Serverless** | Glue | Synapse Serverless Spark |
| **Orchestration** | Step Functions / MWAA | ADF / Databricks Workflows |

**EMR vs Glue (AWS Decision)**

| Factor | EMR | Glue |
|--------|-----|------|
| Control | Full (custom AMI, libraries) | Limited (managed) |
| Cost | Cheaper at scale (spot instances) | Expensive (DPU-based) |
| Ops | Cluster management required | Serverless |
| **Use Case** | Complex multi-step jobs | Simple ETL (< 1 hour) |

**Databricks vs Synapse (Azure Decision)**

| Factor | Databricks | Synapse Spark |
|--------|------------|---------------|
| Performance | Generally faster (Photon) | Good, integrated |
| Cost | Premium | Included in Synapse |
| Unity Catalog | Best-in-class governance | Purview integration |
| **Use Case** | ML + Advanced Analytics | DWH + Spark hybrid |

### Stream Processing

| Aspect | AWS | Azure |
|--------|-----|-------|
| **Engine** | Kinesis Data Analytics / Flink on EMR | Stream Analytics / Spark Streaming |
| **Windowing** | Tumbling, Sliding, Session | Same |
| **State** | RocksDB (Flink) | Checkpointing |
| **Latency** | Sub-second (Flink) | Seconds (Spark Streaming) |

**Micro-batch vs True Streaming**

| Pattern | Latency | Complexity | Use Case |
|---------|---------|------------|----------|
| **Micro-batch** | 5-30 seconds | Medium | 90% of use cases |
| **True Streaming** | < 1 second | High | Fraud detection, trading |

**Interview Insight:**
> "We use **Structured Streaming** in Databricks with a **5-minute trigger interval**. True real-time is only needed for fraud; everything else tolerates micro-batch. This reduces operational complexity significantly."

---

## 4️⃣ Compute Sizing & Cost Optimization

### Cluster Sizing Framework

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CLUSTER SIZING FORMULA                          │
├─────────────────────────────────────────────────────────────────────┤
│  Data Size: 5 TB (daily)                                            │
│  Processing Time Target: 2 hours                                    │
│  Shuffle Factor: 3x (joins, aggregations)                           │
│                                                                     │
│  Memory Needed = 5 TB × 3 = 15 TB shuffle data                      │
│  With 10% in-memory → 1.5 TB RAM needed                             │
│                                                                     │
│  If using r5.4xlarge (128 GB RAM):                                  │
│  Nodes = 1.5 TB / 128 GB = ~12 nodes                                │
│                                                                     │
│  Add 50% buffer for skew → 18 nodes                                 │
└─────────────────────────────────────────────────────────────────────┘
```

### Cost Optimization Strategies

| Strategy | AWS Implementation | Azure Implementation |
|----------|-------------------|---------------------|
| **Spot Instances** | EMR Spot (70% savings) | Databricks Spot VMs |
| **Auto-scaling** | EMR Managed Scaling | Databricks Autoscale |
| **Right-sizing** | Compute Optimizer | Azure Advisor |
| **Storage Tiering** | S3 Intelligent-Tiering | ADLS Hot/Cool/Archive |
| **Compression** | Zstd (40% smaller than Snappy) | Same |
| **Partition Pruning** | Pushdown with Glue Catalog | Unity Catalog |

**Interview Insight:**
> "We achieved **40% cost reduction** by:
> 1. Moving from Glue to EMR with 80% Spot instances
> 2. Implementing Delta Lake compaction (reduced small files by 90%)
> 3. Using S3 Intelligent-Tiering for Bronze layer"

---

## 5️⃣ Data Quality & Governance

### Quality Framework

```
┌────────────────────────────────────────────────────────────────────┐
│                    DATA QUALITY DIMENSIONS                          │
├────────────────────────────────────────────────────────────────────┤
│  COMPLETENESS  →  Are all required fields present?                  │
│  ACCURACY      →  Do values match source of truth?                  │
│  CONSISTENCY   →  Do related records align?                         │
│  TIMELINESS    →  Is data fresh enough?                             │
│  UNIQUENESS    →  Are there duplicates?                             │
│  VALIDITY      →  Do values conform to rules?                       │
└────────────────────────────────────────────────────────────────────┘
```

### Quality Implementation

| Tool | AWS | Azure |
|------|-----|-------|
| **Schema Validation** | Glue Schema Registry | Event Hub Schema Registry |
| **DQ Checks** | Glue Data Quality / Great Expectations | Databricks DQ / Azure Purview |
| **Data Catalog** | Glue Data Catalog | Purview / Unity Catalog |
| **Lineage** | Glue Lineage | Purview Lineage |

**Quality Gates Pattern**

```python
# Great Expectations Example
expectations = [
    expect_column_to_exist("order_id"),
    expect_column_values_to_be_unique("order_id"),
    expect_column_values_to_not_be_null("customer_id"),
    expect_column_values_to_be_between("amount", 0, 1000000),
]

# If validation fails
if not validation_result.success:
    send_to_dead_letter_queue(batch)
    alert_data_team()
else:
    write_to_silver_layer(batch)
```

---

## 6️⃣ Reliability & Fault Tolerance

### Failure Modes & Mitigations

| Failure Mode | Impact | Mitigation |
|--------------|--------|------------|
| **Source Unavailable** | No new data | Retry with exponential backoff |
| **Processing Failure** | Partial data | Checkpointing + Idempotent writes |
| **Downstream Unavailable** | Data bottleneck | Dead Letter Queue (DLQ) |
| **Schema Drift** | Job failure | Schema evolution support |
| **Data Corruption** | Bad data downstream | Time travel / rollback |

### Idempotency Patterns

```python
# Pattern 1: Partition Overwrite (Idempotent)
df.write \
    .mode("overwrite") \
    .partitionBy("date") \
    .parquet("s3://bucket/table/")

# Pattern 2: MERGE (Upsert) - Delta Lake
MERGE INTO target USING source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *

# Pattern 3: Deduplication State Store
processed_ids = load_checkpoint()
new_records = batch.filter(~batch.id.isin(processed_ids))
save_checkpoint(new_records.id)
```

### Exactly-Once Semantics

| Layer | Implementation |
|-------|----------------|
| **Ingestion** | Kinesis/Kafka consumer offsets |
| **Processing** | Spark checkpointing + WAL |
| **Storage** | Delta Lake transactions |
| **Delivery** | Output commit protocol |

---

## 7️⃣ Monitoring & Observability

### Metrics to Track

| Category | Metrics | Alert Threshold |
|----------|---------|-----------------|
| **Ingestion** | Records/sec, Lag, Errors | Lag > 1 hour |
| **Processing** | Job duration, Success rate, Memory | Duration 2x normal |
| **Storage** | File count, Size, Partitions | > 10K small files |
| **Quality** | Null rate, Duplicate rate, Schema errors | > 1% failures |
| **Cost** | Daily spend, Cost per TB processed | > 20% budget |

### Observability Stack

| Aspect | AWS | Azure |
|--------|-----|-------|
| **Metrics** | CloudWatch | Azure Monitor |
| **Logs** | CloudWatch Logs | Log Analytics |
| **Tracing** | X-Ray | Application Insights |
| **Dashboards** | CloudWatch Dashboards | Azure Dashboards |
| **Alerting** | SNS + PagerDuty | Azure Alerts |

---

## 8️⃣ Key Trade-offs & Decisions

### Trade-off Matrix

| Decision | Option A | Option B | When to Choose A | When to Choose B |
|----------|----------|----------|------------------|------------------|
| **Push vs Pull** | Push (Kinesis) | Pull (Polling S3) | Real-time needed | Cost-sensitive batch |
| **Serverless vs Managed** | Glue/Functions | EMR/Databricks | Small, infrequent jobs | Large, complex jobs |
| **Lambda vs Kappa** | Dual pipelines | Single stream | Complex analytics + real-time | Simpler architecture |
| **Normalize vs Denormalize** | 3NF in Gold | Wide tables | OLTP queries | Analytics queries |
| **Hot vs Cold Storage** | SSD/Memory | S3/Archive | < 100 GB, fast access | TB-scale, cost priority |

### Lambda vs Kappa Architecture

```
LAMBDA ARCHITECTURE
┌─────────────────────────────────────────────────┐
│              Speed Layer (Stream)                │
│              ──────────────────                  │
│  Real-time views (approximate)                   │
└─────────────────────────────────────────────────┘
            ╲                      ╱
             ╲      MERGE        ╱
              ╲                 ╱
┌─────────────────────────────────────────────────┐
│              Batch Layer                         │
│              ───────────                         │
│  Accurate views (delayed)                        │
└─────────────────────────────────────────────────┘

KAPPA ARCHITECTURE
┌─────────────────────────────────────────────────┐
│         Single Stream Processing                 │
│         ────────────────────────                 │
│   Reprocess by replaying from start             │
│   (Kafka retention = source of truth)            │
└─────────────────────────────────────────────────┘
```

**Interview Insight:**
> "We use a **hybrid approach**—Kappa for near-real-time dashboards (5-min latency), with a nightly batch job to compute accurate historical aggregations. This balances complexity vs accuracy."

---

## 9️⃣ Security Considerations

### Security Layers

| Layer | AWS | Azure |
|-------|-----|-------|
| **Network** | VPC, PrivateLink | VNet, Private Endpoints |
| **Identity** | IAM Roles, STS | Managed Identity, AAD |
| **Encryption at Rest** | KMS (SSE-S3, SSE-KMS) | CMK, Azure Key Vault |
| **Encryption in Transit** | TLS 1.2+ | TLS 1.2+ |
| **Access Control** | Lake Formation | Purview + Unity Catalog |
| **Audit** | CloudTrail | Azure Activity Logs |

### Column-Level Security (Fine-grained)

```sql
-- AWS Lake Formation
GRANT SELECT (order_id, amount) 
ON TABLE orders 
TO ROLE analytics_team;

-- Exclude PII columns (customer_email, phone)

-- Databricks Unity Catalog
GRANT SELECT ON TABLE orders TO analytics_team;
ALTER TABLE orders SET COLUMN MASK pii_mask ON customer_email;
```

---

## 🔟 Sample Interview Questions & Answers

### Q1: "How would you handle a 5 TB daily pipeline with 5-minute latency?"

**Answer:**
> "I would design a **hybrid batch + streaming** architecture:
> 1. **Streaming Path:** Kafka → Spark Structured Streaming → Delta Lake (Silver) → Updated every 5 minutes.
> 2. **Batch Path:** Nightly job reprocesses full day with accurate late arrivals.
> 3. **Storage:** Delta Lake for ACID, time travel, and efficient upserts.
> 4. **Key Trade-off:** Accept potential duplicates in streaming path, dedupe in batch. This ensures latency SLA while maintaining accuracy."

### Q2: "How do you handle late-arriving data?"

**Answer:**
> "Three strategies depending on tolerance:
> 1. **Reprocessing Window:** Accept events up to 24 hours late, trigger partition recomputation.
> 2. **Event-time Watermarking:** In Spark Streaming, set `withWatermark('event_time', '1 hour')` to allow late events within threshold.
> 3. **Lambda Merge:** Streaming path shows real-time, batch path corrects next day."

### Q3: "How do you prevent the small files problem?"

**Answer:**
> "Four approaches:
> 1. **Compaction Jobs:** Delta Lake `OPTIMIZE` to merge small files into ~1 GB files.
> 2. **Trigger Intervals:** Stream writes every 5 minutes, not every second.
> 3. **Repartition before Write:** `df.repartition(10).write.parquet()`
> 4. **Auto-Optimize:** Delta Auto-Optimize for automatic compaction."

### Q4: "What's your approach to schema evolution?"

**Answer:**
> "Delta Lake + Schema Registry:
> 1. **Backward Compatible:** New columns are nullable (safe).
> 2. **Forward Compatible:** Readers ignore unknown columns.
> 3. **Breaking Changes:** Blue-green deployment—write to new table, switch views.
> 4. **Schema Enforcement:** Enable `mergeSchema` for evolution, `enforceSchema` for strict validation."

### Q5: "How would you estimate costs for a 10 TB/day pipeline on AWS?"

**Answer:**
```
MONTHLY COST ESTIMATE (10 TB/day = 300 TB/month)

STORAGE (S3 Standard):
  Bronze: 300 TB × $0.023 = ~$6,900
  Silver: 200 TB × $0.023 = ~$4,600
  Gold:   50 TB × $0.023  = ~$1,150
  Total Storage: ~$13,000/month

COMPUTE (EMR with 80% Spot):
  20 nodes × 8 hrs/day × 30 days × $0.50/hr = $2,400
  With Spot discount (70%): ~$720

STREAMING (Kinesis):
  50 shards × 720 hrs × $0.015 = $540
  PUT records: 1 billion × $0.014/million = $14,000

DATA TRANSFER:
  Inter-region: ~$2,000 (minimize by co-locating)

TOTAL: ~$30,000-40,000/month
```

---

## 🔑 Key Takeaways for Interview

1. **Always Start with Requirements:** Latency? Volume? Query patterns?
2. **Decouple Storage and Compute:** This is the foundation of modern data platforms.
3. **Choose Formats Wisely:** Parquet/Delta for analytics, Avro for streaming.
4. **Partition Strategically:** Files should be 128 MB – 1 GB.
5. **Idempotency is Non-negotiable:** Use MERGE/Upsert patterns.
6. **Monitor Everything:** Lag, duration, file counts, quality metrics.
7. **Cost Optimization:** Spot instances, tiering, compression.
8. **Security from Day 1:** Encryption, IAM, Column-level access.

---

## 📚 Reference Architecture Comparison

| Component | AWS Recommended | Azure Recommended |
|-----------|----------------|-------------------|
| **Event Streaming** | Kafka MSK | Event Hub |
| **Batch Ingestion** | DMS + Glue | ADF |
| **Lakehouse Storage** | S3 + Delta Lake | ADLS Gen2 + Delta |
| **Batch Processing** | EMR Spark | Databricks |
| **Stream Processing** | Flink on EMR | Spark Structured Streaming |
| **Orchestration** | MWAA (Airflow) | ADF + Databricks Workflows |
| **Data Catalog** | Glue Catalog + Lake Formation | Purview + Unity Catalog |
| **Serving Layer** | Athena / Redshift Serverless | Synapse Serverless |
| **BI/Reporting** | QuickSight | Power BI |
