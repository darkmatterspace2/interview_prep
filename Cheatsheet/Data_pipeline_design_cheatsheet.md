# Data Pipeline System Design Interview Cheatsheet

> **Quick Reference Guide for Data Engineering System Design Interviews**

---

## 📑 Table of Contents
| Section | Topics |
|---------|--------|
| [1. Clarifying Questions](#1-clarifying-questions) | First questions to ask |
| [2. User Requirements Matrix](#2-user-requirements-matrix) | Who needs what |
| [3. Pipeline Components](#3-pipeline-components) | Landing → Serving |
| [4. Technology Options](#4-technology-options-by-cloud) | AWS vs Azure vs GCP |
| [5. Architecture Patterns](#5-architecture-patterns) | Medallion, Lambda, Kappa |
| [6. Real-World Examples](#6-real-world-use-case-templates) | Uber, Netflix, Amazon |
| [7. Reliability & Governance](#7-reliability--governance) | Idempotency, DQ, Lineage |
| [8. Cost Optimization](#8-cost-optimization) | Reduce cloud spend |
| [9. Interview Framework](#9-interview-framework) | Step-by-step approach |

---

## 1. Clarifying Questions

**Always ask these FIRST before designing:**

| Category | Questions to Ask |
|----------|------------------|
| **Latency** | Batch (hours)? Near real-time (minutes)? True streaming (seconds)? |
| **Volume** | How much data per day/hour? Peak vs average? |
| **Infrastructure** | On-premise? Cloud? Hybrid? Migration scenario? |
| **Budget** | Cost constraints? Open-source vs commercial? |
| **Cloud Provider** | AWS, Azure, GCP, or multi-cloud? |
| **End Users** | Data Scientists? Engineers? Business Users? |
| **Processing** | Stateful or Stateless transformations? |
| **Compliance** | GDPR, HIPAA, PCI-DSS requirements? |

---

## 2. User Requirements Matrix

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           WHO NEEDS WHAT?                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  DATA SCIENTISTS              DATA ENGINEERS              BUSINESS USERS
  ├─ Ad-hoc queries            ├─ ETL/ELT pipelines        ├─ Dashboards
  ├─ ML training data          ├─ Data quality checks      ├─ BI Reports
  ├─ Feature stores            ├─ Data governance          ├─ KPI metrics
  ├─ Notebooks (Jupyter)       ├─ Data lineage             └─ Scheduled reports
  └─ Experiment tracking       └─ Orchestration
```

---

## 3. Pipeline Components

### Core Pipeline Flow
```
┌──────────┐    ┌──────────────┐    ┌────────────┐    ┌─────────┐    ┌─────────┐
│ LANDING  │───▶│ ORCHESTRATION│───▶│ PROCESSING │───▶│ STORAGE │───▶│ SERVING │
└──────────┘    └──────────────┘    └────────────┘    └─────────┘    └─────────┘
   Sources         Scheduling         Transform        Persist        Consume
```

### Medallion Architecture (Decide # of Layers)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MEDALLION ARCHITECTURE                              │
└─────────────────────────────────────────────────────────────────────────────┘

  BRONZE (RAW)              SILVER (CLEANED)           GOLD (AGGREGATED)
  ┌──────────────┐          ┌──────────────┐          ┌──────────────┐
  │ • Raw ingest │          │ • Validated  │          │ • Business   │
  │ • Schema-on- │   ───▶   │ • Deduplicated│   ───▶   │   metrics    │
  │   read       │          │ • Typed      │          │ • Star schema│
  │ • Append-only│          │ • Joined     │          │ • Aggregates │
  └──────────────┘          └──────────────┘          └──────────────┘
       ▲                                                     │
       │                                                     ▼
  Data Sources                                         BI / ML / APIs
```

**When to use 2 layers vs 3 layers:**
| Layers | Use Case |
|--------|----------|
| **2 (Raw → Curated)** | Simple pipelines, small teams, single use case |
| **3 (Bronze → Silver → Gold)** | Enterprise scale, multiple consumers, complex transformations |
| **4+ (add Platinum)** | ML feature stores, real-time serving, specialized marts |

---

## 4. Technology Options by Cloud

### Landing / Ingestion

| Component | AWS | Azure | GCP | On-Prem |
|-----------|-----|-------|-----|---------|
| **Object Storage** | S3 | Blob Storage | GCS | HDFS, MinIO |
| **CDC/Streaming** | Kinesis, MSK | Event Hubs, Service Bus | Pub/Sub | Kafka |
| **API Ingestion** | API Gateway | API Management | Cloud Endpoints | Kong |
| **Database CDC** | DMS | Data Factory CDC | Datastream | Debezium |

### Orchestration

| Component | AWS | Azure | GCP | Open Source |
|-----------|-----|-------|-----|-------------|
| **Workflow** | Step Functions, MWAA | Data Factory | Cloud Composer | Airflow, Dagster, Prefect |
| **Scheduling** | EventBridge | Logic Apps | Cloud Scheduler | Cron, Argo |

### Processing

| Type | AWS | Azure | GCP | Open Source |
|------|-----|-------|-----|-------------|
| **Batch** | EMR, Glue | Synapse, Databricks | Dataproc, BigQuery | Spark |
| **Streaming** | Kinesis Analytics | Stream Analytics | Dataflow | Flink, Spark Streaming |
| **Serverless** | Lambda, Glue | Functions, ADF | Cloud Functions | - |

### Storage

| Type | AWS | Azure | GCP | Open Source |
|------|-----|-------|-----|-------------|
| **Data Lake** | S3 + Lake Formation | ADLS Gen2 | GCS + BigLake | Delta Lake, Iceberg, Hudi |
| **Data Warehouse** | Redshift | Synapse, Fabric | BigQuery | ClickHouse, DuckDB |
| **NoSQL (Hot)** | DynamoDB | CosmosDB | Firestore, Bigtable | MongoDB, Cassandra |

### Serving

| Component | AWS | Azure | GCP | Open Source |
|-----------|-----|-------|-----|-------------|
| **BI** | QuickSight | Power BI | Looker | Metabase, Superset |
| **Feature Store** | SageMaker FS | - | Vertex AI FS | Feast, Tecton |
| **API** | API Gateway | APIM | Cloud Endpoints | FastAPI |

---

## 5. Architecture Patterns

### Batch vs Near Real-Time vs True Streaming

| Pattern | Latency | Use Case | Tools |
|---------|---------|----------|-------|
| **Batch** | Hours/Days | Historical analysis, ML training | Spark, Glue, ADF |
| **Near Real-Time** | Minutes | Dashboards, alerts | Micro-batch Spark, Lambda triggers |
| **True Streaming** | Seconds/ms | Fraud detection, recommendations | Flink, Kafka Streams, Kinesis |

### Lambda Architecture
```
                    ┌───────────────────┐
                    │   BATCH LAYER     │──────┐
  DATA ────────────▶│  (Historical)     │      │
  SOURCES           └───────────────────┘      ▼
       │            ┌───────────────────┐  ┌───────┐
       └───────────▶│   SPEED LAYER     │─▶│SERVING│──▶ QUERIES
                    │  (Real-time)      │  │ LAYER │
                    └───────────────────┘  └───────┘
```
**Use when:** Need both historical accuracy AND real-time freshness

### Kappa Architecture
```
  DATA ────────────▶ STREAM PROCESSING ────────▶ SERVING LAYER ──▶ QUERIES
  SOURCES           (Single Path)
                    │
                    └── Replay for reprocessing
```
**Use when:** Simpler ops, real-time first, can replay for batch

---

## 6. Real-World Use Case Templates

### Example 1: BI Dashboard Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  USE CASE: Business Intelligence Dashboards (Near Real-Time)                │
│  SOURCE: CSV files  │  TARGET: Power BI  │  LATENCY: Minutes                │
└─────────────────────────────────────────────────────────────────────────────┘

  CSV Files ──▶ Blob Storage ──▶ Azure Function (trigger)
                    │
                    ▼
              ┌─────────────────────────────────────────────┐
              │            MEDALLION LAYERS                 │
              ├─────────────────────────────────────────────┤
              │ Bronze ──ADF──▶ Silver ──ADF──▶ Gold       │
              │ (raw)   Databricks (clean)  Databricks (agg)│
              └─────────────────────────────────────────────┘
                                                │
                                                ▼
                                          Synapse ──▶ Power BI

ALTERNATIVES:
├─ Storage: S3, GCS
├─ Trigger: Event Hub, Kinesis, Pub/Sub
├─ Orchestration: Glue, Airflow, Dagster
├─ Processing: EMR, Dataflow
└─ BI: QuickSight, Looker, Tableau
```

### Example 2: ML Recommendation Engine

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  USE CASE: Netflix-style Recommendation Engine                              │
│  SOURCE: User events (Avro)  │  TARGET: Feature Store  │  LATENCY: Seconds │
└─────────────────────────────────────────────────────────────────────────────┘

  User Events ──▶ Kafka ──▶ Spark Streaming ──▶ Delta Lake
       │                          │                  │
       │                          ▼                  ▼
       │                    Feature Store ◀──── Batch Aggregations
       │                          │
       ▼                          ▼
  Real-time features ──────▶ Model Serving ──▶ Recommendations

WHY THESE CHOICES?
├─ Kafka: High throughput, replay capability, exactly-once
├─ Delta Lake: ACID, time travel, schema evolution
├─ Feature Store: Consistent features for training/serving
└─ Spark Streaming: Stateful aggregations, windowing
```

### Example 3: Uber/Lyft Real-Time Tracking

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  USE CASE: Real-Time Driver/Rider Matching                                  │
│  SOURCE: GPS events  │  TARGET: Mobile App  │  LATENCY: Milliseconds        │
└─────────────────────────────────────────────────────────────────────────────┘

  GPS Sensors ──▶ Kafka ──▶ Flink (CEP) ──┬──▶ Redis (hot cache)
       │                        │         │
       │                        ▼         └──▶ PostgreSQL (state)
       │              Geospatial matching       │
       │                        │               ▼
       ▼                        ▼          API Gateway ──▶ Mobile App
  Cold Storage ◀──── Delta Lake (history)

WHY FLINK OVER SPARK?
├─ True event-time processing
├─ Lower latency (ms vs seconds)
├─ Better exactly-once guarantees
└─ Native CEP (Complex Event Processing)
```

### Example 4: Amazon Logistics Analytics

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  USE CASE: Supply Chain & Delivery Optimization                             │
│  SOURCE: IoT + Orders  │  TARGET: Ops Dashboard  │  LATENCY: Near Real-Time│
└─────────────────────────────────────────────────────────────────────────────┘

  Warehouse IoT ──┬──▶ Kinesis ──▶ Lambda (routing) ──▶ DynamoDB (hot)
                  │                      │
  Order Events ───┘                      ▼
                               Kinesis Firehose
                                      │
                                      ▼
                               S3 (Bronze) ──▶ Glue ──▶ Redshift ──▶ QuickSight
                                                           │
                                                           ▼
                                                    ML (SageMaker)
                                                   Demand Forecasting
```

---

## 7. Reliability & Governance

### Pipeline Reliability Patterns

| Pattern | Description | Implementation |
|---------|-------------|----------------|
| **Idempotency** | Re-running produces same result | Use `MERGE`, partition overwrite, upsert |
| **Checkpointing** | Resume from failure point | Spark checkpoints, Flink savepoints |
| **Dead Letter Queue** | Capture failed records | SQS DLQ, Event Hub DLQ, Kafka DLT |
| **Retry with Backoff** | Handle transient failures | Exponential backoff, circuit breaker |
| **Schema Evolution** | Handle schema changes | Schema registry, Delta Lake evolution |

### Data Quality Framework

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA QUALITY CHECKS                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  COMPLETENESS          ACCURACY            CONSISTENCY         TIMELINESS
  ├─ Null checks        ├─ Range checks     ├─ Cross-table      ├─ Freshness
  ├─ Row counts         ├─ Format checks    │  referential      ├─ SLA monitoring
  └─ Column presence    └─ Business rules   └─ integrity        └─ Late data handling

TOOLS: Great Expectations, Soda, dbt tests, Monte Carlo, Datafold
```

### Data Governance

| Component | Purpose | Tools |
|-----------|---------|-------|
| **Catalog** | Discover & document data | Unity Catalog, Glue Catalog, DataHub |
| **Lineage** | Track data flow | OpenLineage, Marquez, Atlan |
| **Access Control** | Who can access what | Lake Formation, Unity Catalog, Ranger |
| **PII Detection** | Find sensitive data | AWS Macie, Azure Purview |
| **Audit Logging** | Who did what when | CloudTrail, Activity Logs |

---

## 8. Cost Optimization

### Compute Optimization

| Strategy | Description |
|----------|-------------|
| **Spot/Preemptible** | Use for fault-tolerant batch jobs (70-90% savings) |
| **Auto-scaling** | Scale down during low usage |
| **Right-sizing** | Match instance size to workload |
| **Serverless** | Pay only for execution time |
| **Cluster pooling** | Share warm clusters across jobs |

### Storage Optimization

| Strategy | Description |
|----------|-------------|
| **Tiered Storage** | S3 Glacier, Cool/Archive tiers for old data |
| **Compression** | Parquet, ORC, Zstd (50-90% reduction) |
| **Partitioning** | Query only needed partitions |
| **Z-Ordering** | Co-locate related data for better pruning |
| **Lifecycle Policies** | Auto-delete/archive old data |

### Processing Optimization

| Strategy | Description |
|----------|-------------|
| **Predicate Pushdown** | Filter at storage layer |
| **Columnar Formats** | Read only needed columns |
| **Caching** | Cache frequently accessed data |
| **Broadcast Joins** | Avoid shuffles for small tables |
| **Incremental Processing** | Process only new/changed data |

---

## 9. Interview Framework

### Step-by-Step Approach (RADIO Framework)

```
R - Requirements       Clarify scope, users, latency, volume, constraints
A - Architecture       Draw high-level components and data flow
D - Data Model         Schema design, partitioning, file formats
I - Implementation     Specific tools, why chosen, alternatives considered
O - Operations         Monitoring, alerting, failure handling, scaling
```

### Diagram Template

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         [YOUR SYSTEM NAME]                                  │
│  Source: [type]  │  Latency: [batch/stream]  │  Users: [who]               │
└─────────────────────────────────────────────────────────────────────────────┘

  [Sources]         [Ingestion]        [Processing]       [Storage]        [Serving]
  ┌───────┐        ┌───────────┐      ┌───────────┐      ┌───────┐       ┌─────────┐
  │       │───────▶│           │─────▶│           │─────▶│       │──────▶│         │
  └───────┘        └───────────┘      └───────────┘      └───────┘       └─────────┘

KEY DECISIONS:
1. [Component]: [Tool chosen] because [reason]
2. [Component]: [Tool chosen] because [reason]

TRADE-OFFS CONSIDERED:
├─ [Option A] vs [Option B]: Chose A because...
└─ [Option C] vs [Option D]: Chose C because...
```

### Common Follow-Up Questions

| Question | What They're Testing |
|----------|---------------------|
| "How would you handle late data?" | Watermarking, event-time processing |
| "What if volume 10x?" | Horizontal scaling, partitioning |
| "How do you ensure exactly-once?" | Idempotency, transactions, checkpoints |
| "What if a source schema changes?" | Schema evolution, registry, alerting |
| "How do you monitor this?" | Metrics, logs, alerting thresholds |
| "What's your backup strategy?" | Replication, snapshots, disaster recovery |

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SYSTEM DESIGN QUICK REFERENCE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ LATENCY:   Batch (hrs) → Micro-batch (min) → Streaming (sec/ms)            │
│ PATTERNS:  Lambda (batch+stream) │ Kappa (stream-only) │ Medallion (layers)│
│ FORMATS:   Parquet (analytics) │ Avro (streaming) │ JSON (flexibility)     │
│ TABLES:    Delta Lake │ Iceberg │ Hudi (for ACID + time travel)            │
│ QUALITY:   Great Expectations │ Soda │ dbt tests                           │
│ CATALOG:   Unity Catalog │ Glue │ DataHub │ Atlan                          │
│ MONITORING: Prometheus+Grafana │ CloudWatch │ Datadog                       │
└─────────────────────────────────────────────────────────────────────────────┘
```