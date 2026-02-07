# System Design Interview Questions & Answers (Question Bank 1)

> **Amazon Data Engineer Style** - End-to-End Data Platform Design

---

<a id="index"></a>
## 📑 Table of Contents

| Section | Topics |
|---------|--------|
| [1️⃣ System Design Q86-90](#1️⃣-system-design-questions-q86-q90) | Analytics Platform, ML Pipeline, Dashboards |
| &nbsp;&nbsp;&nbsp;└ [Q86: E2E logistics analytics](#q86-design-an-end-to-end-logistics-analytics-system) | Medallion architecture |
| &nbsp;&nbsp;&nbsp;└ [Q87: Delay prediction ML](#q87-design-shipment-delay-prediction-pipeline) | Feature Store, SageMaker |
| &nbsp;&nbsp;&nbsp;└ [Q88: Real-time dashboard](#q88-design-real-time-dashboard-for-operations-team) | Redis, Flink, Grafana |
| &nbsp;&nbsp;&nbsp;└ [Q89: Cost vs latency](#q89-cost-vs-latency-trade-offs) | Decision framework |
| &nbsp;&nbsp;&nbsp;└ [Q90: Multi-region ingestion](#q90-multi-region-data-ingestion-strategy) | GDPR, replication |
| [2️⃣ Deep Dives](#2️⃣-part-2-system-design-deep-dives) | Truck Tracking, DQ, Backfill |
| &nbsp;&nbsp;&nbsp;└ [Truck Tracking Dashboard](#real-time-truck-tracking-dashboard) | IoT, Kinesis, DynamoDB |
| &nbsp;&nbsp;&nbsp;└ [Data Quality Framework](#data-quality-framework-vendor-data) | Validation pattern |
| &nbsp;&nbsp;&nbsp;└ [Bug Backfill Strategy](#bug-backfill-while-live-data-flowing) | Safe backfill |
| [Question Bank 2](#question-bank-2-advanced-data-engineering-system-design) | Architecture Decisions |
| [3️⃣ Batch vs Streaming (Q1-5)](#3️⃣-batch-vs-streaming-design-decisions-q1-5) | When to use which |
| &nbsp;&nbsp;&nbsp;└ [Q1: How to decide](#q1-how-do-you-decide-batch-vs-streaming) | Decision matrix |
| &nbsp;&nbsp;&nbsp;└ [Q2: Near-real-time batch](#q2-when-is-near-real-time-batch-better-than-streaming) | Micro-batch wins |
| &nbsp;&nbsp;&nbsp;└ [Q3: Why micro-batch](#q3-why-do-many-real-time-systems-secretly-use-micro-batch) | Hidden patterns |
| &nbsp;&nbsp;&nbsp;└ [Q4: Justify streaming cost](#q4-what-business-metrics-justify-streaming-cost) | ROI calculation |
| &nbsp;&nbsp;&nbsp;└ [Q5: Over-engineering](#q5-when-is-streaming-over-engineering) | Anti-patterns |
| [4️⃣ Batch Pipeline Design (Q6-10)](#4️⃣-batch-pipeline-design-q6-10) | Daily ETL, Backfills |
| &nbsp;&nbsp;&nbsp;└ [Q6: Daily analytics](#q6-design-daily-analytics-pipeline) | Airflow DAG |
| &nbsp;&nbsp;&nbsp;└ [Q7: Late-arriving data](#q7-handle-late-arriving-data-in-batch-systems) | Delta merge |
| &nbsp;&nbsp;&nbsp;└ [Q8: Re-runnable pipelines](#q8-design-re-runnable--idempotent-batch-pipelines) | Idempotency |
| &nbsp;&nbsp;&nbsp;└ [Q9: Backfills](#q9-support-backfills-without-impacting-daily-jobs) | Separate clusters |
| &nbsp;&nbsp;&nbsp;└ [Q10: Version logic](#q10-version-batch-logic-safely) | Shadow mode |
| [5️⃣ Reliability & Fault Tolerance (Q21-25)](#5️⃣-reliability--fault-tolerance-q21-25) | Retries, Monitoring |
| [6️⃣ Schema & Change Management](#6️⃣-schema--change-management) | Evolution patterns |
| [7️⃣ Streaming Systems (Q11-15)](#7️⃣-streaming-systems-q11-15) | Kafka, Flink, Watermarks |
| [8️⃣ Orchestration](#8️⃣-orchestration-patterns) | Airflow, retries |
| [9️⃣ Data Quality](#9️⃣-data-quality-systems) | Validation frameworks |
| [🔟 Cost Optimization](#🔟-cost-optimization) | Spot, serverless |

---

<a id="1️⃣-system-design-questions-q86-q90"></a>
## 1️⃣ System Design Questions (Q86-Q90) [↩️](#index)

<a id="q86-design-an-end-to-end-logistics-analytics-system"></a>
### Q86: Design an end-to-end logistics analytics system [↩️](#index)

```
DATA SOURCES → INGESTION → PROCESSING → SERVING
─────────────   ─────────   ──────────   ───────
Driver Scans → Kafka → Spark Streaming → Delta Lake → Redshift → QuickSight
Orders DB → CDC ────────────────────────────────────────────────────────────
Partner APIs → Lambda → S3 ─────────────────────────────────────────────────
```

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Ingestion** | Kafka (MSK) | Real-time streaming |
| **Processing** | Spark Streaming | Aggregations |
| **Storage** | Delta Lake on S3 | ACID, time travel |
| **Warehouse** | Redshift Serverless | SQL analytics |
| **Cache** | ElastiCache (Redis) | Sub-second lookups |
| **BI** | QuickSight | Dashboards |

**Key Decisions:** Medallion Architecture (Bronze/Silver/Gold), streaming + batch separation

---

<a id="q87-design-shipment-delay-prediction-pipeline"></a>
### Q87: Design shipment delay prediction pipeline [↩️](#index)

```
FEATURE ENGINEERING → MODEL TRAINING → INFERENCE
─────────────────────  ──────────────   ─────────
Historical Shipments → Feature Store (Feast) → SageMaker Training → SageMaker Endpoint
Weather Data ─────────────────────────────────────────────────────────▲
Traffic Data ─────────────────────────────────────────────────────────┤
                                                                       ▼
                                                              Delay Score per Shipment
```

**Key Components:**
1. **Feature Store (Feast):** Training/serving consistency
2. **MLflow Registry:** Model versioning
3. **SageMaker Endpoint:** Auto-scaling inference

---

<a id="q88-design-real-time-dashboard-for-operations-team"></a>
### Q88: Design real-time dashboard for operations team [↩️](#index)

**Latency Requirements:**
- Truck location: < 30 seconds
- Delay alerts: < 1 minute
- Aggregate metrics: < 5 minutes

```
Kafka Topics → Flink (CEP) → Redis (State) → Grafana (Live)
                    │
                    └──→ PagerDuty (Alerts)
```

---

<a id="q89-cost-vs-latency-trade-offs"></a>
### Q89: Cost vs latency trade-offs [↩️](#index)

| Scenario | Low Cost | Low Latency | Balanced |
|----------|----------|-------------|----------|
| Processing | Lambda/Glue | Dedicated EMR | EMR Serverless |
| Storage | S3 Standard | EBS io2 | S3 + Redis cache |
| Compute | Spot instances | On-demand | Reserved + Spot |

---

<a id="q90-multi-region-data-ingestion-strategy"></a>
### Q90: Multi-region data ingestion strategy [↩️](#index)

| Pattern | Description | Use Case |
|---------|-------------|----------|
| Regional Processing | Process locally, replicate results | GDPR compliance |
| Centralized Lake | Ingest locally, replicate to central | Global analytics |
| Active-Active | Full processing in each region | Disaster recovery |

---

<a id="2️⃣-part-2-system-design-deep-dives"></a>
## 2️⃣ Part 2: System Design Deep Dives [↩️](#index)

<a id="real-time-truck-tracking-dashboard"></a>
### Real-Time Truck Tracking Dashboard [↩️](#index)

**Requirements:** 100K trucks, 10K active locations/min

```
Truck GPS Sensors → Kinesis Data Streams → Flink → DynamoDB → API GW + Lambda → React + Maps
                                             │
                                             └──→ PagerDuty (Delays)
```

---

<a id="data-quality-framework-vendor-data"></a>
### Data Quality Framework (Vendor Data) [↩️](#index)

```python
class VendorDataValidator:
    def validate_batch(self, df):
        # 1. Schema validation
        # 2. Business rules
        # 3. Separate good from bad (DLQ)
        # 4. Alert if >5% errors
        return valid_df, invalid_df, stats
```

---

<a id="bug-backfill-while-live-data-flowing"></a>
### Bug Backfill While Live Data Flowing [↩️](#index)

```
LIVE PIPELINE (unchanged):     New Data → Current Logic → Production Table
BACKFILL PIPELINE (parallel):  Historical → Fixed Logic → Staging → Swap Partitions

Timeline: Day 1-3 process → Day 4 validate → Day 5 deploy fix → Day 6-7 swap
```

---

<a id="question-bank-2-advanced-data-engineering-system-design"></a>
# Question Bank 2: Advanced Data Engineering System Design [↩️](#index)

---

<a id="3️⃣-batch-vs-streaming-design-decisions-q1-5"></a>
## 3️⃣ Batch vs Streaming Design Decisions (Q1-5) [↩️](#index)

<a id="q1-how-do-you-decide-batch-vs-streaming"></a>
### Q1: How do you decide batch vs streaming? [↩️](#index)

| Factor | Choose Batch | Choose Streaming |
|--------|-------------|------------------|
| Latency | Hours/days OK | Seconds required |
| Completeness | Need ALL data | Partial view OK |
| Complexity | Simple aggregations | Complex CEP |
| Cost | Budget-constrained | Latency justifies |

---

<a id="q2-when-is-near-real-time-batch-better-than-streaming"></a>
### Q2: When is near-real-time batch better than streaming? [↩️](#index)

**Micro-batch (5-15 min) wins when:**
- Late data handling (batch windows collect stragglers)
- Exactly-once easier (transactional writes)
- Cost optimization (serverless cheaper)
- Simpler ops (no state management)

---

<a id="q3-why-do-many-real-time-systems-secretly-use-micro-batch"></a>
### Q3: Why do many "real-time" systems secretly use micro-batch? [↩️](#index)

1. **Exactly-Once Semantics** - Easier in batch
2. **Cost** - Streaming runs 24/7; batch is on-demand
3. **Late Data** - Batch windows handle naturally
4. **Debugging** - Clear boundaries, easy re-run
5. **Perception** - "5-minute delay" is "real-time" for most

---

<a id="q4-what-business-metrics-justify-streaming-cost"></a>
### Q4: What business metrics justify streaming cost? [↩️](#index)

| Metric | Streaming Value | Example |
|--------|-----------------|---------|
| Fraud Detection | Prevent $10M+ losses | Block before completion |
| SLA Penalties | Avoid breaches | Alert before miss |
| Safety | Prevent incidents | IoT anomaly detection |

---

<a id="q5-when-is-streaming-over-engineering"></a>
### Q5: When is streaming over-engineering? [↩️](#index)

**Signs You Don't Need Streaming:**
- Daily reports (users check once/day)
- Historical analytics (freshness doesn't add value)
- Low volume (<1M events/day)
- No action (nobody acts on real-time data)

---

<a id="4️⃣-batch-pipeline-design-q6-10"></a>
## 4️⃣ Batch Pipeline Design (Q6-10) [↩️](#index)

<a id="q6-design-daily-analytics-pipeline"></a>
### Q6: Design daily analytics pipeline [↩️](#index)

```
02:00 AM Trigger → Extract (S3/DB) → Transform (Spark) → Load (Redshift) → Serve (QuickSight)
                    (Bronze)         (Silver)           (Gold)           (Dashboard)
```

---

<a id="q7-handle-late-arriving-data-in-batch-systems"></a>
### Q7: Handle late-arriving data in batch systems [↩️](#index)

| Approach | Description | Trade-off |
|----------|-------------|-----------|
| Reprocessing Window | Reprocess last N days | Simple but wasteful |
| Delta/Upsert | Merge late data | Requires ACID |
| Buffer Period | Wait for stragglers | Delays pipeline |

---

<a id="q8-design-re-runnable--idempotent-batch-pipelines"></a>
### Q8: Design re-runnable & idempotent batch pipelines [↩️](#index)

```python
# ✅ Idempotent: Partition Overwrite
df.write.mode("overwrite").partitionBy("date").option("replaceWhere", f"date = '{date}'").save()

# ❌ NOT Idempotent: Append duplicates on retry
df.write.mode("append").parquet("/output/")
```

---

<a id="q9-support-backfills-without-impacting-daily-jobs"></a>
### Q9: Support backfills without impacting daily jobs [↩️](#index)

- **Separate clusters:** Backfill on high-capacity spot cluster
- **Same code:** Daily and backfill use same logic
- **Parallel processing:** Process 10 days at once for backfill

---

<a id="q10-version-batch-logic-safely"></a>
### Q10: Version batch logic safely [↩️](#index)

| Approach | How | Use When |
|----------|-----|----------|
| Git + CI/CD | Code versioning | All changes |
| Feature Flags | Toggle at runtime | Gradual rollout |
| Shadow Mode | Run both, compare | High-risk changes |

---

<a id="5️⃣-reliability--fault-tolerance-q21-25"></a>
## 5️⃣ Reliability & Fault Tolerance (Q21-25) [↩️](#index)

**Reliability Pillars:**
- Idempotency
- Automatic retries with backoff
- Dead letter queues
- Monitoring & alerting
- Checkpointing

---

<a id="6️⃣-schema--change-management"></a>
## 6️⃣ Schema & Change Management [↩️](#index)

- Schema evolution (additive changes)
- Schema registry
- Backward/forward compatibility
- Migration strategies

---

<a id="7️⃣-streaming-systems-q11-15"></a>
## 7️⃣ Streaming Systems (Q11-15) [↩️](#index)

- Kafka consumer groups
- Flink vs Spark Streaming
- Watermarking for late data
- Exactly-once semantics
- State management

---

<a id="8️⃣-orchestration-patterns"></a>
## 8️⃣ Orchestration Patterns [↩️](#index)

- Airflow DAG design
- Dependency management
- Retry strategies
- Backfill patterns
- Alerting

---

<a id="9️⃣-data-quality-systems"></a>
## 9️⃣ Data Quality Systems [↩️](#index)

- Great Expectations integration
- Schema validation
- Business rule checks
- Anomaly detection
- DLQ patterns

---

<a id="🔟-cost-optimization"></a>
## 🔟 Cost Optimization [↩️](#index)

- Spot instances for batch
- Serverless for variable loads
- Data lifecycle policies
- Compression strategies
- Reserved capacity planning
