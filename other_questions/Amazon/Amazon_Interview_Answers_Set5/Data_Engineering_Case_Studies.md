# Data Engineering System Design – 3 Detailed Case Studies

> **Interview Focus:** Deep-dive into real-world scenarios with architecture decisions, tech stack reasoning, processing paradigm choices, and cost vs. flexibility trade-offs.

---

## 📌 Processing Paradigm Decision Framework

Before diving into case studies, here's the critical decision matrix:

### When to Choose Each Paradigm

| Paradigm | Latency | Use Cases | Trade-offs |
|----------|---------|-----------|------------|
| **True Streaming** | < 1 second | Fraud detection, Stock trading, Real-time bidding | Highest complexity, expensive, requires stateful processing |
| **Near Real-Time (Micro-batch)** | 1-5 minutes | Live dashboards, Session analytics, IoT monitoring | Good balance of latency and simplicity |
| **Batch** | Hours to Daily | ML training, Historical reports, Data warehouse refresh | Simplest, cheapest, but high latency |
| **Hybrid (Lambda)** | Both | E-commerce (real-time recs + daily aggregates) | Duplicate logic, operational complexity |

### Domain → Paradigm Mapping

| Domain | Preferred Paradigm | Reasoning |
|--------|-------------------|-----------|
| **Financial Trading** | True Streaming | Milliseconds matter for arbitrage |
| **Fraud Detection** | True Streaming | Must block transaction in real-time |
| **E-commerce Recommendations** | Near Real-Time | 5-min staleness acceptable |
| **IoT / Telemetry** | Near Real-Time + Batch | Stream for alerts, batch for analytics |
| **Log Analytics** | Near Real-Time | Ops teams need <5 min visibility |
| **Business Intelligence** | Batch | Daily/weekly reports, overnight refresh |
| **ML Model Training** | Batch | Large historical datasets, GPU efficiency |
| **Clickstream Analytics** | Near Real-Time | Session attribution within session |
| **Healthcare Monitoring** | True Streaming | Patient vitals need instant alerts |
| **Social Media Feeds** | Near Real-Time | Minutes-old content acceptable |

---

## 🎯 Tech Stack Decision Matrix

### Open Source vs Proprietary Trade-offs

| Factor | Open Source | Proprietary/Managed |
|--------|-------------|---------------------|
| **Cost** | Lower license cost, higher ops cost | Higher license, lower ops |
| **Flexibility** | Full customization | Vendor constraints |
| **Talent** | Larger pool (Spark, Kafka) | Vendor-specific skills |
| **Support** | Community + paid support | Enterprise SLAs |
| **Lock-in** | Minimal | High (migration painful) |
| **Time to Value** | Slower (setup required) | Faster (managed) |

### Tech Stack by Processing Layer

| Layer | Open Source Options | Proprietary/Managed Options |
|-------|--------------------|-----------------------------|
| **Streaming Ingestion** | Kafka, Pulsar, Redpanda | Kinesis, Event Hub, Confluent Cloud |
| **Batch Ingestion** | Airbyte, Debezium, Singer | Fivetran, Stitch, ADF, DMS |
| **Stream Processing** | Flink, Spark Streaming, Kafka Streams | Kinesis Analytics, Stream Analytics |
| **Batch Processing** | Spark (EMR/OSS), Dask, Trino | Databricks, Snowflake, Synapse |
| **Storage** | MinIO, HDFS, Delta Lake | S3, ADLS, GCS |
| **Orchestration** | Airflow, Dagster, Prefect | MWAA, ADF, Databricks Workflows |
| **Data Catalog** | Apache Atlas, DataHub | Glue Catalog, Purview, Unity Catalog |
| **BI/Visualization** | Superset, Metabase, Redash | Power BI, Tableau, QuickSight |

---

# 📘 Case Study 1: E-Commerce Real-Time Personalization Platform

## Business Context

**Company:** Large e-commerce retailer (100M+ users, 10M+ products)  
**Challenge:** Provide personalized product recommendations within the user's session  
**Scale:** 500M events/day, 50K events/second peak  
**Current State:** Batch recommendations (24-hour stale), losing to competitors with real-time personalization

## Requirements Analysis

| Requirement | Specification | Impact on Architecture |
|-------------|---------------|------------------------|
| **Latency** | < 100ms for recommendation API | In-memory feature store |
| **Freshness** | User behavior reflected in 5 mins | Near real-time streaming |
| **Scale** | 50K events/sec, 500M/day | Kafka + distributed processing |
| **Personalization** | Per-user + contextual | Feature vectors per user |
| **Fallback** | If real-time fails, serve batch | Lambda architecture |
| **Cost** | < $50K/month | Efficient resource usage |

## Architecture Decision

### Why Near Real-Time (Not True Streaming)?

| Consideration | True Streaming | Near Real-Time (Chosen) |
|---------------|---------------|-------------------------|
| **Latency Need** | < 1 second | 5 minutes acceptable ✅ |
| **Complexity** | Stateful, exactly-once | Simpler micro-batch |
| **Cost** | 3x more expensive | Optimized compute |
| **Business Value** | Marginal improvement | Sufficient for recommendations |

> **Interview Reasoning:** "True streaming would add complexity without proportional business value. A user who viewed a product 3 minutes ago vs 30 seconds ago has nearly identical intent. We chose **5-minute micro-batch** for simplicity while still beating our 24-hour batch baseline."

## Detailed Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA SOURCES                                    │
│  [Clickstream] [Cart Events] [Search Queries] [Purchase History]            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │ 50K events/sec
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STREAMING INGESTION                                  │
│                        Apache Kafka (MSK)                                    │
│   Topics: clickstream, cart_events, search, purchases                        │
│   Partitions: 100 per topic | Retention: 7 days                             │
└─────────────────────────────────────────────────────────────────────────────┘
                          │                           │
                          ▼                           ▼
┌──────────────────────────────────┐   ┌──────────────────────────────────────┐
│      STREAM PROCESSING            │   │           BATCH PATH                  │
│   Spark Structured Streaming      │   │   Nightly Spark Jobs (EMR)           │
│   Trigger: 5 minutes              │   │   Full recomputation                 │
│                                   │   │   Historical features                │
│   • Real-time user features       │   │   • Collaborative filtering          │
│   • Session aggregations          │   │   • Model retraining                 │
│   • Recent browsing history       │   │                                      │
└──────────────────────────────────┘   └──────────────────────────────────────┘
                          │                           │
                          ▼                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FEATURE STORE                                        │
│                         Redis Cluster                                        │
│   • Per-user feature vectors (10KB per user)                                │
│   • TTL: 30 days inactive users                                              │
│   • Cluster: 20 nodes (320 GB RAM)                                          │
│                                                                              │
│   Key: user:{user_id}:features                                              │
│   Value: {recent_categories: [...], avg_price_range: ..., session_count: }  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      RECOMMENDATION SERVICE                                  │
│                         (Kubernetes Pods)                                    │
│                                                                              │
│   1. Receive user request                                                   │
│   2. Fetch features from Redis (< 5ms)                                      │
│   3. Run ML model inference (< 50ms)                                        │
│   4. Return top-10 products (< 100ms total)                                 │
│                                                                              │
│   Fallback: If Redis miss → Query batch pre-computed recs from DynamoDB    │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Tech Stack Justification

| Component | Choice | Why This? | Alternatives Considered |
|-----------|--------|-----------|------------------------|
| **Message Queue** | Kafka (MSK) | Industry standard, replay capability, ecosystem | Kinesis (simpler but less control) |
| **Stream Processing** | Spark Structured Streaming | Team expertise, unified batch+stream | Flink (better true streaming, steeper curve) |
| **Feature Store** | Redis Cluster | Sub-ms reads, in-memory | DynamoDB (10ms latency too slow) |
| **Batch Processing** | EMR Spark | Cost-effective for overnight jobs | Databricks (overkill for batch-only) |
| **ML Inference** | Kubernetes + TF Serving | Scalable, GPU support | SageMaker (vendor lock-in) |
| **Storage** | S3 + Delta Lake | Durability, ACID, time travel | Raw S3 (no ACID) |

### Open Source vs Managed Decision

| Component | Decision | Reasoning |
|-----------|----------|-----------|
| Kafka | **MSK (Managed)** | Critical path, can't afford downtime. Worth $5K/month for SLA. |
| Spark | **EMR (Managed)** | Focus on logic, not cluster ops. Spot instances for cost. |
| Redis | **Self-managed on EC2** | Custom tuning needed for performance. Redis Cloud too expensive at scale. |
| Kubernetes | **EKS (Managed)** | Team doesn't have K8s ops expertise. |

## Streaming vs Batch Components

| Component | Paradigm | Reasoning |
|-----------|----------|-----------|
| **User Session Features** | Near Real-Time (5 min) | Reflect current session behavior |
| **Product Popularity** | Near Real-Time | Trending products change hourly |
| **Collaborative Filtering** | Batch (Daily) | Requires full matrix factorization |
| **Model Training** | Batch (Weekly) | GPU efficiency, stable training |
| **A/B Test Metrics** | Batch (Daily) | Statistical significance needs volume |

## Performance & Cost

| Metric | Value |
|--------|-------|
| **Latency** | P99: 95ms (target: 100ms ✅) |
| **Freshness** | 5 minutes (vs 24 hours before) |
| **Throughput** | 60K events/sec sustained |
| **Monthly Cost** | $42K (Kafka $8K, EMR $12K, Redis $10K, K8s $12K) |
| **CTR Improvement** | +23% conversion rate |

---

# 📘 Case Study 2: Financial Transaction Fraud Detection System

## Business Context

**Company:** Digital payments processor (similar to Stripe/Square)  
**Challenge:** Detect and **block** fraudulent transactions before authorization  
**Scale:** 10K transactions/second, $10B daily volume  
**Constraint:** Decision must be made in **< 200ms** (within payment network timeout)
**Current State:** Batch fraud detection catches fraud 24 hours later (chargebacks already processed)

## Requirements Analysis

| Requirement | Specification | Impact on Architecture |
|-------------|---------------|------------------------|
| **Latency** | < 200ms end-to-end | True streaming, no batch |
| **Availability** | 99.99% (4.3 min/month downtime) | Multi-region, no SPOF |
| **Accuracy** | < 0.1% false positive | ML model + rules engine |
| **Auditability** | 7-year retention | Immutable event log |
| **Explainability** | Why was transaction flagged? | Feature attribution |

## Architecture Decision

### Why True Streaming (Not Micro-batch)?

| Factor | True Streaming (Chosen) | Micro-batch |
|--------|--------------------------|-------------|
| **Latency** | < 100ms processing ✅ | 5+ seconds minimum |
| **State Management** | Per-transaction states | Batch aggregates |
| **Complexity** | Higher, but necessary | Doesn't meet SLA |
| **Cost** | 3x streaming infra | N/A (can't use) |

> **Interview Reasoning:** "This is one of the rare cases where **true streaming is mandatory**. A 5-minute delay means the fraudulent transaction is already approved. The business case for sub-second detection ($100M/year fraud prevented) justifies the complexity and cost of true streaming."

## Detailed Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          TRANSACTION SOURCE                                  │
│             Payment API Gateway (10K TPS)                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ Sync call (blocks until decision)
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FRAUD DECISION SERVICE                                │
│                            (< 200ms SLA)                                     │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  1. FEATURE ENRICHMENT (< 50ms)                                      │   │
│  │     • User profile from Redis (lifetime stats)                       │   │
│  │     • Recent transactions from Flink state (last 1 hour)            │   │
│  │     • Device fingerprint from DynamoDB                               │   │
│  │     • IP reputation from external API (cached)                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  2. REAL-TIME AGGREGATIONS (Flink CEP)                               │   │
│  │     • Transaction count (last 1hr, 24hr, 7d)                         │   │
│  │     • Velocity: 3+ transactions in 5 minutes?                        │   │
│  │     • Geo-velocity: Impossible travel detection                      │   │
│  │     • Amount deviation from user's norm                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  3. ML MODEL INFERENCE (< 30ms)                                      │   │
│  │     • XGBoost model (< 10ms inference)                               │   │
│  │     • Features: 150+ engineered features                             │   │
│  │     • Output: fraud_probability (0-1)                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  4. RULES ENGINE (< 20ms)                                            │   │
│  │     • Hard rules: Blocklist, Velocity limits, Amount caps           │   │
│  │     • Combine ML score + rules → Final decision                     │   │
│  │     • Output: APPROVE | REVIEW | BLOCK                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  Response: {"decision": "BLOCK", "reason": "velocity_exceeded", ...}        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                          (Async after response)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      ASYNC EVENT PROCESSING                                  │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────┐     │
│  │ Kafka Topic: transactions                                          │     │
│  │ All transactions logged for audit (7 years)                       │     │
│  └───────────────────────────────────────────────────────────────────┘     │
│       │              │                    │                                 │
│       ▼              ▼                    ▼                                 │
│  [S3 Archive]  [User Profile Update]  [Model Training Pipeline]            │
│   (Parquet)    (Redis async update)   (Daily batch retraining)             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Tech Stack Justification

| Component | Choice | Why This? | Alternatives Considered |
|-----------|--------|-----------|------------------------|
| **Stream Processing** | Apache Flink | Best-in-class for stateful streaming, exactly-once, CEP | Spark Streaming (micro-batch latency too high) |
| **Feature Store** | Redis Cluster + Flink State | Redis: User profiles (< 5ms). Flink: Session state (in-process) | DynamoDB too slow for critical path |
| **ML Inference** | In-process XGBoost | No RPC overhead, < 10ms | SageMaker Endpoint (50ms latency) |
| **Rules Engine** | Drools / Custom | Complex rules, dynamic updates | Hardcoded (not maintainable) |
| **Message Queue** | Kafka | Durability for compliance, replay | Kinesis (less control) |
| **Long-term Storage** | S3 + Delta Lake | 7-year retention, queryable | S3 raw (no query) |

### Streaming Platform: Flink Deep-Dive

| Capability | Usage in This System |
|------------|----------------------|
| **Stateful Processing** | Rolling window aggregates per user |
| **Event-Time Processing** | Handle out-of-order transactions |
| **Exactly-Once** | Critical for financial accuracy |
| **CEP (Complex Event Processing)** | Pattern detection (rapid txns) |
| **Savepoints** | Zero-downtime deployments |

### Open Source vs Managed Decision

| Component | Decision | Reasoning |
|-----------|----------|-----------|
| Flink | **Self-managed on K8s** | Need low-level tuning for latency. Managed Flink adds 50ms overhead. |
| Kafka | **Confluent Cloud** | Mission-critical, need enterprise support + exactly-once guarantees. |
| Redis | **Redis Enterprise** | Need active-active geo-replication for multi-region. |
| K8s | **EKS** | Focus on Flink, not K8s ops. |

> **Interview Trade-off:** "We chose self-managed Flink despite operational overhead because managed Flink services add 50-100ms latency. For fraud detection, that's unacceptable. We invested in SRE expertise instead."

## Latency Budget Breakdown

| Stage | Budget | Actual P99 |
|-------|--------|------------|
| Network ingress | 5ms | 3ms |
| Feature fetch (Redis) | 10ms | 8ms |
| Flink state lookup | 5ms | 4ms |
| Real-time aggregation | 30ms | 25ms |
| ML inference | 15ms | 12ms |
| Rules evaluation | 10ms | 8ms |
| Network egress | 5ms | 3ms |
| **TOTAL** | **80ms** | **63ms** |
| **Buffer** | 120ms | Available |

## Cost Analysis

| Component | Monthly Cost | Notes |
|-----------|-------------|-------|
| Flink Cluster (K8s) | $25K | 50 nodes, always-on |
| Kafka (Confluent) | $15K | High throughput tier |
| Redis Enterprise | $12K | Active-active multi-region |
| S3 Storage | $5K | 7-year data |
| ML Training (EMR) | $3K | Daily retraining |
| **TOTAL** | **$60K/month** | |
| **Fraud Prevented** | **$8M/month** | 0.08% fraud reduction |
| **ROI** | **133x** | |

---

# 📘 Case Study 3: IoT Telemetry Platform for Smart Manufacturing

## Business Context

**Company:** Industrial equipment manufacturer with 50K+ connected machines globally  
**Challenge:** Monitor machine health, predict failures, optimize maintenance  
**Scale:** 1 million sensors, 1B messages/day, 50 TB raw data/day  
**Requirements:** Near real-time alerts (< 5 min), batch analytics for ML

## Requirements Analysis

| Requirement | Specification | Impact on Architecture |
|-------------|---------------|------------------------|
| **Ingestion Rate** | 1 billion messages/day (~12K/sec) | Distributed ingestion |
| **Message Size** | 1 KB average (sensor readings) | Storage optimization critical |
| **Alert Latency** | < 5 minutes for anomalies | Near real-time processing |
| **ML Training** | Daily/Weekly model updates | Batch processing |
| **Retention** | Hot: 30 days, Cold: 5 years | Tiered storage |
| **Cost** | Aggressive optimization needed | Open source preferred |

## Architecture Decision

### Why Hybrid (Streaming + Batch)?

| Path | Paradigm | Use Case |
|------|----------|----------|
| **Alerting** | Near Real-Time (1 min) | Temperature spike → Alert in 1 min |
| **Dashboards** | Near Real-Time (5 min) | Ops team monitoring |
| **Predictive Maintenance ML** | Batch (Daily) | Train failure prediction models |
| **Historical Analytics** | Batch (Ad-hoc) | "What caused failures last quarter?" |

> **Interview Reasoning:** "IoT is the classic hybrid use case. Real-time processing for alerts (temperature exceeds threshold → notify immediately), but training ML models requires batch processing on weeks of historical data. We built both paths with shared storage (Delta Lake) to avoid data silos."

## Detailed Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           50K CONNECTED MACHINES                             │
│         1M sensors → MQTT/HTTP → 1B messages/day                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          EDGE LAYER                                          │
│                     AWS IoT Core / Azure IoT Hub                            │
│                                                                              │
│   • Protocol translation (MQTT → Kafka)                                     │
│   • Device authentication                                                   │
│   • Edge filtering (drop duplicates, compress)                              │
│   • Reduction: 1B → 800M messages (20% filtered at edge)                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       STREAMING INGESTION                                    │
│                    Apache Kafka (Self-managed)                               │
│                                                                              │
│   Topics: sensor_readings (200 partitions)                                  │
│   Retention: 7 days (for replay)                                            │
│   Compression: LZ4 (60% savings)                                            │
└─────────────────────────────────────────────────────────────────────────────┘
          │                                               │
          ▼                                               ▼
┌────────────────────────────────────┐   ┌──────────────────────────────────────┐
│      STREAM PROCESSING              │   │       BATCH PROCESSING                │
│     Spark Structured Streaming      │   │      Spark on Kubernetes              │
│     Trigger: 1 minute               │   │                                       │
│                                     │   │   Daily Jobs:                         │
│   ┌─────────────────────────────┐  │   │   • Feature engineering               │
│   │ Real-time Aggregations:      │  │   │   • Model training (TensorFlow)      │
│   │ • 1-min rolling avg temp     │  │   │   • Aggregate reports                │
│   │ • Anomaly detection (Z>3)    │  │   │   • Data quality validation          │
│   │ • Device health scoring      │  │   │                                       │
│   └─────────────────────────────┘  │   │   Weekly Jobs:                        │
│              │                      │   │   • Full historical reprocessing      │
│              ▼                      │   │   • Model retraining                  │
│   ┌─────────────────────────────┐  │   │                                       │
│   │ Alert Evaluation:            │  │   └──────────────────────────────────────┘
│   │ • Threshold breaches         │  │
│   │ • ML anomaly score > 0.9     │  │
│   │ → SNS/PagerDuty              │  │
│   └─────────────────────────────┘  │
└────────────────────────────────────┘
          │                                               │
          └────────────────────┬──────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        UNIFIED STORAGE                                       │
│                      Delta Lake on S3                                        │
│                                                                              │
│   BRONZE (Raw)                                                              │
│   └── /sensors/bronze/date=2024-02-07/                                      │
│       ├── partition0.parquet (raw messages, 50 TB/day)                      │
│                                                                              │
│   SILVER (Cleaned)                                                          │
│   └── /sensors/silver/date=2024-02-07/                                      │
│       ├── partition0.parquet (deduplicated, typed, 40 TB/day)               │
│                                                                              │
│   GOLD (Aggregated)                                                         │
│   └── /sensors/gold/hourly_aggregates/                                      │
│       ├── date=2024-02-07/hour=10/                                          │
│       ├── (avg, min, max, stddev per sensor per hour, 500 GB/day)           │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Tech Stack Justification

| Component | Choice | Why This? | Alternatives Considered |
|-----------|--------|-----------|------------------------|
| **Edge Gateway** | AWS IoT Core | Managed MQTT, device auth | Self-managed EMQX (more control, more ops) |
| **Message Queue** | Self-managed Kafka | Cost savings at 50 TB/day, need control | MSK ($15K+ premium), Kinesis (expensive at scale) |
| **Stream Processing** | Spark Structured Streaming | Unified with batch, team expertise | Flink (overkill for 1-min latency) |
| **Batch Processing** | Spark on K8s (Spot) | 80% cost savings with Spot | EMR (25% more expensive) |
| **Storage** | Delta Lake on S3 | ACID, compaction (critical for IoT small files), cost | Snowflake (10x cost for this volume) |
| **ML Platform** | SageMaker | Managed training, easy deployment | Self-managed (team lacks ML ops) |
| **Orchestration** | Apache Airflow (MWAA) | DAGs for complex pipelines | Step Functions (less flexible) |

### Cost-Driven Decisions (IoT is Cost-Sensitive)

| Decision | Cost Impact | Trade-off |
|----------|-------------|-----------|
| **Self-managed Kafka** | -$15K/month vs MSK | +1 FTE for Kafka ops |
| **Spot instances for batch** | -80% on compute | Job retries on preemption |
| **LZ4 compression** | -60% storage | Minimal CPU overhead |
| **Tiered storage** | S3 IA after 30 days, Glacier after 1 year | Query latency for old data |
| **Edge filtering** | -20% ingestion | Some data loss (duplicates, noise) |

### Open Source First Strategy

| Component | OSS Choice | Why Not Managed? |
|-----------|-----------|------------------|
| Kafka | Strimzi on K8s | At 50 TB/day, MSK costs $20K+. Self-managed: $8K (compute + ops time). |
| Spark | Spark on K8s (Spark Operator) | EMR adds 25% overhead. Spot on K8s gives more control. |
| Airflow | Self-hosted (EKS) | MWAA $300+/month for same capacity at $80. |
| Delta Lake | Open source | Databricks not needed; Delta OSS sufficient. |
| Superset | Self-hosted | Looker/Tableau $50K/year. Superset: $0 + $5K ops. |

> **Interview Insight:** "We adopted an **OSS-first** strategy because IoT margins are thin. Every dollar saved on infrastructure goes to product features. We hired 2 platform engineers instead of paying $400K/year in SaaS fees."

## Storage Tiering Strategy

| Tier | Age | Storage Class | Monthly Cost per TB | Query Latency |
|------|-----|---------------|---------------------|---------------|
| **Hot** | 0-30 days | S3 Standard | $23 | < 100ms |
| **Warm** | 30-180 days | S3 IA | $12.50 | < 100ms |
| **Cold** | 180 days - 1 year | S3 Glacier IR | $4 | 3-5 hours |
| **Archive** | 1-5 years | S3 Glacier Deep | $1 | 12-48 hours |

**Monthly Storage Cost (50 TB/day = 1.5 PB/month):**
| Without Tiering | With Tiering |
|-----------------|--------------|
| $34,500/month (all Standard) | $12,000/month (life-cycle policies) |

## Compaction Strategy (Critical for IoT)

**Problem:** 1-minute micro-batch creates 1440 files/partition/day → small file problem  

**Solution:** Delta Lake Auto-Optimize + Scheduled Compaction

```python
# Auto-Optimize (on write)
spark.conf.set("spark.databricks.delta.autoCompact.enabled", "true")
spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")

# Scheduled Compaction (nightly)
spark.sql("""
    OPTIMIZE sensors.silver
    WHERE date = current_date() - 1
    ZORDER BY (device_id, sensor_id)
""")

# Result: 1440 files → 10 files (128 MB each)
```

---

## 🔄 Cross-Case Comparison

| Dimension | E-Commerce (Case 1) | Fraud Detection (Case 2) | IoT (Case 3) |
|-----------|---------------------|-------------------------|--------------|
| **Primary Paradigm** | Near Real-Time | True Streaming | Hybrid |
| **Latency Requirement** | 5 minutes | < 200 ms | 1-5 minutes |
| **Justification** | Session personalization | Block before authorize | Alerts + ML training |
| **Stream Processor** | Spark Streaming | Apache Flink | Spark Streaming |
| **Why That Choice?** | Unified with batch | Lowest latency, stateful | Unified, team expertise |
| **Cost Priority** | Medium | Low (revenue protection) | High (thin margins) |
| **OSS vs Managed** | Mostly managed | Split (Flink self, Kafka managed) | Mostly OSS |
| **Storage** | S3 + Delta | S3 + Delta | S3 + Delta + Tiering |
| **ML Integration** | Feature store | In-process inference | Batch training |

---

## 🎤 Interview Tips: How to Present Architecture Decisions

### 1. Start with Requirements, Not Technology
> ❌ "We used Kafka because it's popular."  
> ✅ "Our latency SLA was 5 minutes, so micro-batch was sufficient. We chose Kafka for its replay capability, which is critical for reprocessing."

### 2. Quantify Trade-offs
> ❌ "Flink is more complex."  
> ✅ "Flink adds 2 weeks of development time and requires stateful checkpointing expertise. For our 5-minute SLA, Spark Streaming achieves the same result with less complexity."

### 3. Be Opinionated (With Reasoning)
> ✅ "I would NOT use true streaming here. The business value of 30-second latency vs 5-minute latency is minimal for recommendations, but the operational cost is 3x."

### 4. Acknowledge What You Don't Know
> ✅ "I'm less familiar with Pulsar, but my understanding is it combines Kafka durability with lower latency. It could be worth evaluating if Kafka's latency becomes a bottleneck."

### 5. Discuss Evolution
> ✅ "We started with batch-only, then added streaming as requirements evolved. The Delta Lake foundation made this transition seamless because both paths write to the same storage."

---

## 📚 Quick Reference: When to Use What

### Processing Paradigm Cheat Sheet

| If You Need... | Choose... | Example Technologies |
|----------------|-----------|---------------------|
| < 1 second latency | True Streaming | Flink, Kafka Streams, Beam |
| 1-15 minute latency | Near Real-Time (Micro-batch) | Spark Structured Streaming |
| Hourly/Daily updates | Batch | Spark, Trino, Snowflake |
| Both real-time + accurate historical | Lambda Architecture | Streaming + nightly batch |
| Single pipeline, replay for historical | Kappa Architecture | Kafka + Flink (long retention) |

### Tech Stack Selection by Constraint

| If Priority Is... | Choose... |
|-------------------|-----------|
| **Lowest Latency** | Flink + Kafka + Redis |
| **Simplest Operations** | Spark + Managed services (Glue, Databricks) |
| **Lowest Cost** | Spark on Spot + OSS stack (Kafka, Airflow, Superset) |
| **Fastest Time-to-Value** | Snowflake / Databricks (turnkey) |
| **No Vendor Lock-in** | Full OSS: Spark, Kafka, Trino, MinIO, Airflow |
