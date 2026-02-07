# System Design Interview Questions & Answers (Question Bank 1)

> **Amazon Data Engineer Style** - End-to-End Data Platform Design

---

## 1️⃣ System Design Questions (Q86-Q90)

### Q86: Design an end-to-end logistics analytics system

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              END-TO-END LOGISTICS ANALYTICS PLATFORM                         │
└─────────────────────────────────────────────────────────────────────────────┘

DATA SOURCES                    INGESTION                    PROCESSING
─────────────                   ─────────                    ──────────
┌──────────┐                   ┌──────────┐                 ┌──────────────┐
│  Driver  │──CDC──────────────│  Kafka   │────Streaming───│ Spark        │
│  Scans   │                   │  Cluster │                │ Streaming    │
└──────────┘                   └──────────┘                └──────┬───────┘
                                     │                            │
┌──────────┐                         │                            ▼
│  Orders  │──CDC──────────────────────────────────────────┌──────────────┐
│   DB     │                                               │ Delta Lake   │
└──────────┘                                               │ (Bronze/     │
                                                           │  Silver/Gold)│
┌──────────┐                   ┌──────────┐                └──────┬───────┘
│  Partner │──API──────────────│  Lambda  │──S3────────────────────│
│  APIs    │                   │  (Batch) │                        │
└──────────┘                   └──────────┘                        │
                                                                   ▼
                               SERVING                       ┌──────────────┐
                               ───────                       │   Redshift   │
                          ┌──────────────┐                   │ (Analytics)  │
                          │   QuickSight │◀──────────────────┴──────────────┘
                          │ (Dashboards) │
                          └──────────────┘                   ┌──────────────┐
                          ┌──────────────┐                   │ ElasticCache │
                          │   Real-time  │◀──────────────────│   (Redis)    │
                          │   Tracking   │                   └──────────────┘
                          └──────────────┘
```

**Components:**

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Ingestion** | Kafka (MSK) | Real-time event streaming |
| **Batch Ingestion** | AWS Glue | Partner data, backfills |
| **Stream Processing** | Spark Streaming | Real-time aggregations |
| **Storage** | Delta Lake on S3 | ACID transactions, time travel |
| **Warehouse** | Redshift Serverless | SQL analytics |
| **Real-time Cache** | ElastiCache (Redis) | Sub-second lookups |
| **Orchestration** | Airflow (MWAA) | Batch job scheduling |
| **BI** | QuickSight | Dashboards |

**Key Design Decisions:**
1. **Medallion Architecture:** Bronze (raw), Silver (clean), Gold (aggregated)
2. **Separation of Concerns:** Streaming for real-time, batch for historical
3. **Cost Optimization:** S3 for storage, Redshift Serverless for on-demand

---

### Q87: Design shipment delay prediction pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              DELAY PREDICTION ML PIPELINE                                    │
└─────────────────────────────────────────────────────────────────────────────┘

FEATURE ENGINEERING                 MODEL TRAINING              INFERENCE
───────────────────                 ──────────────              ─────────

┌──────────────┐   Feature     ┌──────────────┐             ┌──────────────┐
│  Historical  │───Store──────▶│   Feature    │             │  Real-time   │
│  Shipments   │               │    Store     │◀────────────│   Events     │
└──────────────┘               │   (Feast)    │             └──────────────┘
                               └──────┬───────┘                     │
┌──────────────┐                      │                             │
│   Weather    │───────────────────────│                             │
│    Data      │                      │                             ▼
└──────────────┘                      │                      ┌──────────────┐
                                      ▼                      │  SageMaker   │
┌──────────────┐               ┌──────────────┐             │  Endpoint    │
│   Traffic    │               │  SageMaker   │────Deploy──▶│ (Real-time)  │
│    Data      │───────────────│  Training    │             └──────┬───────┘
└──────────────┘               └──────────────┘                    │
                                      │                            │
                               ┌──────▼───────┐                    ▼
                               │    MLflow    │             ┌──────────────┐
                               │   (Registry) │             │  Delay Score │
                               └──────────────┘             │   per Ship   │
                                                            └──────────────┘
```

**Feature Store Design:**

```python
# Feature definitions (Feast)
from feast import Entity, Feature, FeatureView, ValueType

# Entity
shipment = Entity(name="shipment_id", value_type=ValueType.STRING)

# Feature View
shipment_features = FeatureView(
    name="shipment_features",
    entities=["shipment_id"],
    features=[
        Feature(name="origin_avg_delay_7d", dtype=ValueType.FLOAT),
        Feature(name="carrier_delay_rate", dtype=ValueType.FLOAT),
        Feature(name="route_traffic_score", dtype=ValueType.FLOAT),
        Feature(name="weather_severity", dtype=ValueType.INT32),
    ],
    ttl=timedelta(hours=24),
)
```

**Key Design Decisions:**
1. **Feature Store:** Ensure training/serving consistency
2. **Batch + Real-time:** Historical features + real-time context
3. **Model Registry:** MLflow for versioning and A/B testing
4. **Endpoint:** SageMaker for auto-scaling inference

---

### Q88: Design real-time dashboard for operations team

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              REAL-TIME OPERATIONS DASHBOARD                                  │
└─────────────────────────────────────────────────────────────────────────────┘

LATENCY REQUIREMENTS:
• Truck location: < 30 seconds
• Delay alerts: < 1 minute
• Aggregate metrics: < 5 minutes

ARCHITECTURE:

[Scan Events]        [Streaming]           [State Store]         [Dashboard]
     │                    │                     │                     │
     ▼                    ▼                     ▼                     ▼
┌──────────┐        ┌──────────┐          ┌──────────┐          ┌──────────┐
│  Kafka   │───────▶│  Flink   │─────────▶│  Redis   │─────────▶│ Grafana  │
│  Topics  │        │ (CEP)    │          │ (State)  │   Pull   │ (Live)   │
└──────────┘        └──────────┘          └──────────┘          └──────────┘
                         │                     │
                         │                     │
                         ▼                     ▼
                    ┌──────────┐          ┌──────────┐
                    │PagerDuty │          │ TimeSeries│
                    │ (Alerts) │          │ (Metrics) │
                    └──────────┘          └──────────┘
```

**Redis Data Model:**

```python
# Real-time truck locations
HSET truck:T123 lat 47.6062 lng -122.3321 status IN_TRANSIT updated 1707307200

# Active delays (sorted set by severity)
ZADD delays 3 "shipment:S001"  # severity 3
ZADD delays 5 "shipment:S002"  # severity 5

# Aggregate counters (per region)
HINCRBY region:WEST total_shipments 1
HINCRBYFLOAT region:WEST total_delay_hours 2.5

# TTL for cleanup
EXPIRE truck:T123 3600  # 1 hour
```

**Key Design Decisions:**
1. **Flink over Spark Streaming:** Lower latency for real-time CEP (Complex Event Processing)
2. **Redis for state:** Sub-millisecond reads for dashboard
3. **Push vs Pull:** Pull from Redis (simple), push via WebSocket for critical alerts

---

### Q89: Cost vs latency trade-offs

| Scenario | Low Cost | Low Latency | Balanced |
|----------|----------|-------------|----------|
| **Processing** | Lambda/Glue | Dedicated EMR | EMR Serverless |
| **Storage** | S3 Standard | EBS io2 | S3 + Redis cache |
| **Compute** | Spot instances | On-demand | Reserved + Spot |
| **Serving** | Athena | Redshift RA3 | Redshift Serverless |

**Decision Framework:**

```yaml
Use Case: Daily aggregation dashboard

Option A: Low Cost (~$500/month)
  - Processing: Glue (serverless, per-minute billing)
  - Storage: S3 + Athena
  - Update frequency: Daily
  - Query latency: 5-30 seconds

Option B: Low Latency (~$5,000/month)
  - Processing: Always-on EMR cluster
  - Storage: Redshift RA3 + Redis
  - Update frequency: Real-time
  - Query latency: < 1 second

Option C: Balanced (~$1,500/month)
  - Processing: EMR Serverless (scales to zero)
  - Storage: Redshift Serverless + CloudFront cache
  - Update frequency: Hourly
  - Query latency: 2-5 seconds
```

---

### Q90: Multi-region data ingestion strategy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              MULTI-REGION DATA STRATEGY                                      │
└─────────────────────────────────────────────────────────────────────────────┘

                          ┌───────────────────────┐
                          │    GLOBAL ROUTING     │
                          │      (Route 53)       │
                          └───────────┬───────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              ▼                       ▼                       ▼
     ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
     │   US-WEST-2     │    │   US-EAST-1     │    │   EU-WEST-1     │
     │   (Primary)     │    │   (Secondary)   │    │   (EU Region)   │
     └────────┬────────┘    └────────┬────────┘    └────────┬────────┘
              │                      │                      │
              ▼                      ▼                      ▼
     ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
     │  Regional MSK   │    │  Regional MSK   │    │  Regional MSK   │
     │    (Kafka)      │    │    (Kafka)      │    │    (Kafka)      │
     └────────┬────────┘    └────────┬────────┘    └────────┬────────┘
              │                      │                      │
              └──────────────────────┼──────────────────────┘
                                     │
                                     ▼
                          ┌───────────────────────┐
                          │  CENTRAL DATA LAKE    │
                          │   (S3 + Cross-Region  │
                          │    Replication)       │
                          └───────────────────────┘
```

**Strategies:**

| Pattern | Description | Use Case |
|---------|-------------|----------|
| **Regional Processing** | Process locally, replicate results | GDPR compliance, EU data stays in EU |
| **Centralized Lake** | Ingest locally, replicate to central | Global analytics |
| **Active-Active** | Full processing in each region | Disaster recovery |

**Key Considerations:**
- **Data Residency:** EU data may need to stay in EU (GDPR)
- **Cross-Region Costs:** S3 replication is $0.02/GB
- **Latency:** Global aggregations require central view
- **Consistency:** Eventual consistency across regions

---

## 2️⃣ Part 2: System Design Deep Dives

### Real-Time Truck Tracking Dashboard

**Requirements:**
- 100K trucks, 10K active locations/min
- Dashboard shows all trucks on map
- Delay alerts within 1 minute

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TRUCK TRACKING SYSTEM                                     │
└─────────────────────────────────────────────────────────────────────────────┘

[IoT Devices]      [Ingestion]        [Processing]       [Serving]
     │                  │                  │                 │
     ▼                  ▼                  ▼                 ▼
┌──────────┐      ┌──────────┐      ┌──────────────┐   ┌──────────┐
│  Truck   │─────▶│  Kinesis │─────▶│ Flink        │──▶│  DynamoDB│
│  GPS     │      │  Data    │      │ (Aggregation │   │ (Latest) │
│  Sensors │      │  Streams │      │  + Alerting) │   └────┬─────┘
└──────────┘      └──────────┘      └──────────────┘        │
                                           │                ▼
                                           │          ┌──────────┐
                                           │          │ API GW   │
                                           │          │ + Lambda │
                                           │          └────┬─────┘
                                           ▼               │
                                    ┌──────────┐          │
                                    │PagerDuty │◀─────────┤
                                    │ (Delays) │          │
                                    └──────────┘          ▼
                                                    ┌──────────┐
                                                    │  React   │
                                                    │  + Maps  │
                                                    └──────────┘
```

**Key Components:**
1. **Kinesis:** Handles 100K+ events/sec
2. **Flink:** Real-time aggregation, delay detection
3. **DynamoDB:** Single-digit ms reads for location lookup
4. **Geospatial:** Store lat/lng, query "trucks in region"

---

### Data Quality Framework (Vendor Data)

```python
# Design: Validate vendor data without blocking pipeline

class VendorDataValidator:
    def __init__(self, config):
        self.schema = config.schema
        self.rules = config.rules
        self.dlq_path = config.dlq_path
    
    def validate_batch(self, df):
        """
        Returns: (valid_df, invalid_df, stats)
        """
        # 1. Schema validation
        schema_errors = self.check_schema(df)
        
        # 2. Business rules
        rule_errors = self.check_rules(df)
        
        # 3. Separate good from bad
        all_errors = schema_errors.union(rule_errors)
        invalid_ids = all_errors.select("record_id").distinct()
        
        valid_df = df.join(invalid_ids, "record_id", "left_anti")
        invalid_df = df.join(invalid_ids, "record_id", "inner")
        
        # 4. Write invalid to DLQ
        invalid_df.write.mode("append").parquet(self.dlq_path)
        
        # 5. Alert if threshold breached
        error_rate = invalid_df.count() / df.count()
        if error_rate > 0.05:  # > 5% errors
            self.alert_team(f"High error rate: {error_rate:.2%}")
        
        return valid_df, invalid_df, {
            'total': df.count(),
            'valid': valid_df.count(),
            'invalid': invalid_df.count(),
            'error_rate': error_rate
        }
    
    def check_schema(self, df):
        """Validate required fields and types"""
        errors = []
        for field in self.schema.required_fields:
            null_count = df.filter(F.col(field).isNull()).count()
            if null_count > 0:
                errors.append((field, 'NULL_VALUE', null_count))
        return errors
    
    def check_rules(self, df):
        """Apply business rules"""
        # Example rules
        rules = [
            ("amount > 0", "NEGATIVE_AMOUNT"),
            ("status IN ('ACTIVE', 'COMPLETED')", "INVALID_STATUS"),
            ("date >= '2020-01-01'", "INVALID_DATE")
        ]
        # ... apply rules and collect errors
```

---

### Bug Backfill While Live Data Flowing

**Scenario:** Found bug in shipping cost calculation. Need to reprocess 6 months while new data continues.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SAFE BACKFILL STRATEGY                                    │
└─────────────────────────────────────────────────────────────────────────────┘

LIVE PIPELINE (Continues unchanged)
───────────────────────────────────
New Data ──▶ Current Logic ──▶ Production Table (Partition: 2024-02-*)

BACKFILL PIPELINE (Parallel, isolated)
─────────────────────────────────────
Historical ──▶ Fixed Logic ──▶ Staging Table ──▶ Swap Partitions
(2023-08 to 2024-01)

TIMELINE:
─────────
Day 1-3:   Process backfill to staging (separate cluster)
Day 4:     Validate staging vs production (spot check + aggregates)
Day 5:     Deploy fixed logic to live pipeline
Day 6-7:   Atomic partition swap (old → staging)
Day 8:     Monitor, cleanup staging
```

```python
def backfill_with_validation(start_date, end_date, fix_logic):
    """
    Safely backfill while production continues
    """
    # 1. Process to staging (parallel cluster)
    for date in date_range(start_date, end_date):
        fixed_df = read_source(date).transform(fix_logic)
        fixed_df.write.parquet(f"/staging/fixed/{date}/")
    
    # 2. Validate staging
    for date in sample_dates(start_date, end_date, n=5):
        old = spark.read.parquet(f"/production/{date}/")
        new = spark.read.parquet(f"/staging/fixed/{date}/")
        
        # Compare aggregates
        assert_close(old.agg(sum("cost")).collect(), new.agg(sum("cost")).collect(), tolerance=0.01)
        # Verify fix was applied
        assert new.filter("cost < 0").count() == 0  # Bug was negative costs
    
    # 3. Deploy fix to live pipeline (code change)
    deploy_new_logic(fix_logic)
    
    # 4. Atomic partition swap
    for date in date_range(start_date, end_date):
        with transaction():
            spark.sql(f"ALTER TABLE production DROP PARTITION (date='{date}')")
            spark.sql(f"ALTER TABLE production ADD PARTITION (date='{date}') LOCATION '/staging/fixed/{date}/'")
    
    # 5. Cleanup
    delete_path("/staging/fixed/")
```

---

# Question Bank 2: Advanced Data Engineering System Design

> **Amazon Data Engineer Style** - Architecture Decisions, Trade-offs, and Production Patterns

---

## 3️⃣ Batch vs Streaming Design Decisions (Q1-5)

### Q1: How do you decide batch vs streaming?

**Decision Framework:**

| Factor | Choose Batch | Choose Streaming |
|--------|-------------|------------------|
| **Latency** | Hours/days acceptable | Seconds/minutes required |
| **Completeness** | Need ALL data (late arrivals) | Partial view OK |
| **Complexity** | Simple aggregations | Complex event processing |
| **Cost** | Budget-constrained | Latency justifies cost |
| **Ordering** | Natural time boundaries | Real-time sequence matters |

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LATENCY vs COMPLEXITY DECISION MATRIX                     │
└─────────────────────────────────────────────────────────────────────────────┘

               Low Complexity          High Complexity
             ─────────────────        ─────────────────
Low          │                        │
Latency      │  Micro-batch           │  True Streaming
Need         │  (Spark Streaming)     │  (Flink, Kafka Streams)
             │                        │
             ─────────────────────────┼────────────────────────
             │                        │
High         │  Traditional Batch     │  Lambda Architecture
Latency      │  (Spark, Glue)         │  (Batch + Streaming)
OK           │                        │
             ─────────────────────────┴────────────────────────
```

---

### Q2: When is near-real-time batch better than streaming?

**Near-Real-Time Batch (5-15 minute micro-batches) wins when:**

| Scenario | Why Micro-batch |
|----------|-----------------|
| **Late data handling** | Batch windows collect stragglers naturally |
| **Exactly-once easier** | Transactional writes simpler in batch |
| **Cost optimization** | Serverless (Glue, Lambda) cheaper than always-on |
| **Simpler ops** | No state management, easier debugging |
| **Aggregations** | Complete window before processing |

```python
# Micro-batch example: Trigger every 5 minutes
query = (
    spark.readStream
    .format("kafka")
    .load()
    .writeStream
    .trigger(processingTime="5 minutes")  # Micro-batch
    .format("delta")
    .start()
)

# Use when:
# - Dashboard refresh every 15 min is acceptable
# - Need to join with dimension tables (easier in batch)
# - Want to avoid streaming state complexity
```

---

### Q3: Why do many "real-time" systems secretly use micro-batch?

**Reasons:**

1. **Exactly-Once Semantics** - Easier in batch (transactional writes)
2. **Cost** - Streaming clusters run 24/7; batch is on-demand
3. **Late Data** - Batch windows handle late arrivals naturally
4. **Debugging** - Batch jobs have clear boundaries, easier to re-run
5. **Perception** - "5-minute delay" is "real-time" for most business use cases

```python
# Streaming "look" with batch implementation
# Runs every 5 minutes via Airflow

@dag(schedule_interval="*/5 * * * *")  # Every 5 minutes
def near_realtime_etl():
    @task
    def process_new_events():
        # Read events from last 5 minutes
        df = spark.read.parquet("/raw/events/") \
            .filter(col("event_time") >= datetime.now() - timedelta(minutes=5))
        # Process and write
        df.write.mode("append").parquet("/processed/events/")
```

---

### Q4: What business metrics justify streaming cost?

| Metric | Streaming Value | Example |
|--------|-----------------|---------|
| **Fraud Detection** | Prevent $10M+ losses/year | Block transaction before completion |
| **SLA Penalties** | Avoid contract breaches | Alert before SLA miss |
| **Competitive Advantage** | Real-time pricing, inventory | Amazon stock updates |
| **Safety** | Prevent incidents | IoT sensor anomaly detection |
| **Customer Experience** | Live tracking, notifications | Package delivery updates |

```
Cost Justification:

Streaming Infrastructure: $50,000/month
Avoided Fraud (real-time): $200,000/month
ROI: 4x

vs

Batch (30 min delay): 10% of fraud NOT preventable
Streaming (5 sec delay): 95% of fraud preventable
```

---

### Q5: When is streaming over-engineering?

**Signs You Don't Need Streaming:**

| Situation | Why Batch Is Better |
|-----------|---------------------|
| **Daily Reports** | Users check once/day anyway |
| **Historical Analytics** | Data doesn't change value with freshness |
| **Low Volume** | < 1M events/day → Lambda + S3 cheaper |
| **No Action** | Nobody acts on real-time data |
| **Dev Team Small** | Streaming requires specialized skills |

```python
# OVER-ENGINEERED:
# Streaming pipeline for monthly billing report
# Users look at it once a month!

# APPROPRIATE:
# Simple daily batch job
df = spark.read.parquet("/events/date=2024-02-07")
monthly_report = df.groupBy("customer_id").agg(sum("amount"))
monthly_report.write.parquet("/reports/monthly/")
```

---

## 4️⃣ Batch Pipeline Design (Q6-10)

### Q6: Design daily analytics pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DAILY ANALYTICS PIPELINE                                  │
└─────────────────────────────────────────────────────────────────────────────┘

02:00 AM: Trigger                    06:00 AM: Dashboard Ready
    │                                     │
    ▼                                     ▼
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Extract │───▶│ Transform│───▶│   Load   │───▶│  Serve   │
│  (S3/DB) │    │ (Spark)  │    │(Redshift)│    │(QuickSight)
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │
   Bronze         Silver           Gold          Dashboard
   (Raw)         (Clean)       (Aggregated)      (BI Layer)
```

**Airflow DAG:**

```python
with DAG("daily_analytics", schedule_interval="0 2 * * *") as dag:
    
    extract = SparkSubmitOperator(
        task_id="extract_raw",
        application="extract.py",
        conf={"spark.sql.sources.partitionOverwriteMode": "dynamic"}
    )
    
    transform = SparkSubmitOperator(
        task_id="transform_clean",
        application="transform.py"
    )
    
    load = RedshiftOperator(
        task_id="load_warehouse",
        sql="COPY analytics FROM 's3://bucket/gold/'"
    )
    
    validate = PythonOperator(
        task_id="validate_counts",
        python_callable=validate_row_counts
    )
    
    notify = SlackOperator(
        task_id="notify_complete",
        message="Daily analytics ready"
    )
    
    extract >> transform >> load >> validate >> notify
```

---

### Q7: Handle late-arriving data in batch systems

**Strategies:**

| Approach | Description | Trade-off |
|----------|-------------|-----------|
| **Reprocessing Window** | Reprocess last N days | Simple but wasteful |
| **Delta/Upsert** | Merge late data | Requires ACID support |
| **Separate Late Stream** | Process late data separately | Operational complexity |
| **Buffer Period** | Wait for stragglers before processing | Delays main pipeline |

```python
# Delta Lake: Merge late arrivals
from delta.tables import DeltaTable

def process_with_late_data(processing_date):
    # Read all data that COULD be for this date (including late arrivals)
    new_data = spark.read.parquet("/bronze/events/") \
        .filter(col("business_date") == processing_date)
    
    # Merge into Silver (upsert)
    silver_table = DeltaTable.forPath(spark, "/silver/events/")
    
    silver_table.alias("target").merge(
        new_data.alias("source"),
        "target.event_id = source.event_id"
    ).whenMatchedUpdateAll() \
     .whenNotMatchedInsertAll() \
     .execute()

# Run for last 3 days to catch late arrivals
for i in range(3):
    process_with_late_data(date.today() - timedelta(days=i))
```

---

### Q8: Design re-runnable & idempotent batch pipelines

**Idempotency Patterns:**

```python
# PATTERN 1: Partition Overwrite
df.write \
    .mode("overwrite") \
    .partitionBy("date") \
    .option("replaceWhere", f"date = '{processing_date}'") \
    .format("delta") \
    .save("/output/")

# PATTERN 2: Delete-then-Insert
spark.sql(f"DELETE FROM output WHERE date = '{processing_date}'")
df.write.mode("append").saveAsTable("output")

# PATTERN 3: MERGE with full match
deltaTable.alias("target").merge(
    source.alias("source"),
    "target.id = source.id AND target.date = source.date"
).whenMatchedUpdateAll() \
 .whenNotMatchedInsertAll() \
 .execute()

# ANTI-PATTERN (NOT idempotent):
df.write.mode("append").parquet("/output/")
# Running twice creates duplicates!
```

---

### Q9: Support backfills without impacting daily jobs

```python
# STRATEGY: Separate clusters, same code

class PipelineRunner:
    def __init__(self, mode="daily"):
        self.mode = mode
        
    def get_cluster_config(self):
        if self.mode == "backfill":
            return {
                "instances": 50,  # 5x normal
                "spot_ratio": 0.9,
                "parallelism": 10  # Process 10 days at once
            }
        return {"instances": 10, "spot_ratio": 0.5, "parallelism": 1}
    
    def run(self, date_range):
        config = self.get_cluster_config()
        
        # Process dates in parallel batches
        for batch in chunks(date_range, config["parallelism"]):
            with ThreadPoolExecutor(max_workers=config["parallelism"]) as executor:
                executor.map(self.process_date, batch)
    
    def process_date(self, date):
        # Same logic for daily and backfill
        df = self.extract(date)
        df = self.transform(df)
        self.load(df, date)

# Daily (low priority cluster)
daily_runner = PipelineRunner(mode="daily")
daily_runner.run([date.today()])

# Backfill (separate high-capacity cluster)
backfill_runner = PipelineRunner(mode="backfill")
backfill_runner.run(date_range("2023-01-01", "2024-01-01"))
```

---

### Q10: Version batch logic safely

**Strategies:**

| Approach | How | Use When |
|----------|-----|----------|
| **Git + CI/CD** | Code versioning, automated tests | All changes |
| **Feature Flags** | Toggle new logic at runtime | Gradual rollout |
| **Shadow Mode** | Run new & old, compare results | High-risk changes |
| **A/B Testing** | Split traffic between versions | Uncertain impact |

```python
# Shadow Mode: Run both versions, compare
def transform_with_shadow(df, date):
    # Current logic
    result_v1 = transform_v1(df)
    result_v1.write.parquet(f"/output/v1/date={date}")
    
    # New logic (shadow)
    result_v2 = transform_v2(df)
    result_v2.write.parquet(f"/shadow/v2/date={date}")
    
    # Compare
    diff = compare_results(result_v1, result_v2)
    if diff["mismatch_rate"] > 0.01:  # > 1% different
        alert_team(f"Shadow mode difference: {diff}")
    else:
        log.info(f"Shadow mode validated: {diff}")
```

---

## 5️⃣ Reliability & Fault Tolerance (Q21-25)

### Q21: What makes a data pipeline reliable?

**Reliability Pillars:**

| Pillar | Implementation |
|--------|----------------|
| **Idempotency** | Same input → Same output, multiple runs |
| **Observability** | Metrics, logs, traces for debugging |
| **Alerting** | Proactive notification before user impact |
| **Recovery** | Automated retry, manual intervention path |
| **Testing** | Unit, integration, data quality tests |

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RELIABILITY CHECKLIST                                     │
└─────────────────────────────────────────────────────────────────────────────┘

□ Idempotent writes (partition overwrite, merge)
□ Data quality checks (Great Expectations)
□ SLA monitoring (Datadog, CloudWatch)
□ Automated retry (Airflow, Step Functions)
□ Dead letter queue for bad records
□ Runbooks for common failures
□ On-call rotation with escalation
□ Regular DR drills
```

---

### Q22: Design for node/network/data failure

```python
# NODE FAILURE: Spark handles automatically with retries
spark.conf.set("spark.task.maxFailures", "4")  # Retry task 4 times
spark.conf.set("spark.speculation", "true")    # Speculative execution

# NETWORK FAILURE: Checkpointing for streaming
query = (
    stream_df
    .writeStream
    .option("checkpointLocation", "/checkpoints/job/")  # Resume from here
    .start()
)

# DATA CORRUPTION: Validation before processing
from great_expectations import DataContext

def validate_before_process(df):
    context = DataContext()
    results = context.run_checkpoint(
        checkpoint_name="data_quality",
        batch_request={"dataframe": df}
    )
    
    if not results.success:
        # Route to DLQ, don't process
        df.write.parquet("/dlq/data_corruption/")
        raise DataQualityError("Validation failed")
    
    return df
```

---

### Q23: At-least-once vs Exactly-once trade-offs

| Semantic | Guarantees | Complexity | Performance |
|----------|------------|------------|-------------|
| **At-most-once** | May lose data | Low | Highest |
| **At-least-once** | May duplicate | Medium | Good |
| **Exactly-once** | Perfect (no loss, no dups) | High | Lower |

```python
# AT-LEAST-ONCE: Retry on failure (may process twice)
# Consumer must handle duplicates

def process_at_least_once(events):
    for event in events:
        try:
            result = process(event)
            write_result(result)
            commit_offset(event)
        except Exception:
            # Don't commit, will reprocess
            raise

# EXACTLY-ONCE: Transactional sink
# Atomic: Process + Commit in same transaction

def process_exactly_once(batch):
    with transaction():
        results = process(batch)
        write_results(results)  # Inside transaction
        commit_offsets(batch)   # Inside transaction
        # All-or-nothing
```

---

### Q24: Design graceful degradation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GRACEFUL DEGRADATION STRATEGIES                           │
└─────────────────────────────────────────────────────────────────────────────┘

SCENARIO: Real-time dashboard, streaming fails

LEVEL 1 (Normal):     Streaming → Redis → Dashboard (5 sec latency)
                          ×
LEVEL 2 (Degraded):   Micro-batch → Redis → Dashboard (5 min latency)
                          ×
LEVEL 3 (Emergency):  Batch → S3 → Dashboard (1 hour latency)
                          ×
LEVEL 4 (Offline):    Static cache → Dashboard (last known state)
```

```python
# Implementation: Fallback chain
class DataService:
    def get_metrics(self, region):
        # Try each source in order
        for source in [self.redis, self.batch_cache, self.static_cache]:
            try:
                data = source.get(region)
                if self.is_fresh(data):
                    return data
            except Exception as e:
                log.warning(f"Source {source} failed: {e}")
                continue
        
        # All sources failed
        alert_team("All data sources failed")
        return self.static_cache.get_fallback(region)
```

---

### Q25: Handle slow downstream systems

```python
# PATTERN 1: Backpressure
# Slow down producer when consumer can't keep up

spark.conf.set("spark.streaming.backpressure.enabled", "true")
spark.conf.set("spark.streaming.kafka.maxRatePerPartition", "10000")

# PATTERN 2: Circuit Breaker
# Stop calling failing service, use fallback

from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=30)
def write_to_downstream(data):
    downstream_service.write(data)

def process_with_fallback(data):
    try:
        write_to_downstream(data)
    except CircuitBreakerError:
        # Fallback: Write to queue for later retry
        fallback_queue.send(data)

# PATTERN 3: Buffering
# Absorb bursts, smooth out writes

class BufferedWriter:
    def __init__(self, downstream, buffer_size=1000):
        self.buffer = []
        self.downstream = downstream
        
    def write(self, record):
        self.buffer.append(record)
        if len(self.buffer) >= 1000:
            self.flush()
    
    def flush(self):
        with rate_limiter(100):  # 100 records/sec
            self.downstream.batch_write(self.buffer)
        self.buffer = []
```

---

## 6️⃣ Orchestration & Messaging (Q31-40)

### Q31: Orchestration vs Choreography

| Pattern | Orchestration | Choreography |
|---------|---------------|--------------|
| **Control** | Central coordinator | Decentralized events |
| **Coupling** | Tight (knows all steps) | Loose (just events) |
| **Visibility** | Single view of workflow | Distributed tracing needed |
| **Example** | Airflow DAG | Event-driven microservices |

```
ORCHESTRATION (Airflow):           CHOREOGRAPHY (Events):
                                   
  ┌──────────────┐                 ┌──────┐
  │   Airflow    │                 │ Svc A│──event──▶
  │  (Central)   │                 └──────┘         │
  └──────┬───────┘                                  ▼
         │                                     ┌──────┐
    ┌────┴────┐                                │Kafka │
    ▼         ▼                                └──┬───┘
┌──────┐  ┌──────┐                      ┌────────┼────────┐
│Task A│──│Task B│                      ▼        ▼        ▼
└──────┘  └──────┘                  ┌──────┐ ┌──────┐ ┌──────┐
                                    │ Svc B│ │ Svc C│ │ Svc D│
                                    └──────┘ └──────┘ └──────┘
```

---

### Q32: When is Airflow a bad choice?

| Scenario | Why Airflow Struggles | Better Alternative |
|----------|----------------------|-------------------|
| **Sub-minute triggers** | Min schedule: 1 min | Kafka, Lambda triggers |
| **Event-driven** | Pull-based, not push | Step Functions, EventBridge |
| **1000s of DAGs** | Scheduler bottleneck | Dagster, Prefect |
| **Real-time streaming** | Batch-oriented | Flink, Spark Streaming |
| **Long-running tasks** | Worker timeout issues | Step Functions, Kubernetes |

---

### Q33: Airflow vs Dagster vs Prefect

| Aspect | Airflow | Dagster | Prefect |
|--------|---------|---------|---------|
| **Maturity** | Most mature | Growing | Growing |
| **Learning Curve** | Medium | Steep | Easy |
| **Dynamic DAGs** | Limited | Native | Native |
| **Data Awareness** | Weak | Strong (assets) | Good |
| **Local Dev** | Docker needed | Easy | Very easy |
| **Community** | Large | Growing | Growing |

---

### Q36: Kafka vs SQS vs Pub/Sub

| Feature | Kafka | SQS | Pub/Sub |
|---------|-------|-----|---------|
| **Ordering** | Per partition | FIFO option | Per key |
| **Retention** | Configurable (days-years) | 14 days max | 7 days default |
| **Replay** | Yes (offset reset) | No | Yes (seek) |
| **Throughput** | Very high | Medium | High |
| **Management** | Self-managed or MSK | Fully managed | Fully managed |
| **Use Case** | Event streaming | Task queues | Event routing |

---

### Q40: Handling backpressure

```python
# BACKPRESSURE: Consumer can't keep up with producer

# SOLUTION 1: Rate limiting at producer
from ratelimit import limits

@limits(calls=1000, period=1)  # 1000/sec max
def produce_event(event):
    kafka_producer.send("events", event)

# SOLUTION 2: Adaptive batching in consumer
class AdaptiveConsumer:
    def __init__(self, base_batch_size=100):
        self.batch_size = base_batch_size
        self.lag_threshold = 10000
        
    def consume(self):
        lag = self.get_consumer_lag()
        
        if lag > self.lag_threshold:
            # Under pressure: Process larger batches
            self.batch_size = min(self.batch_size * 2, 10000)
        else:
            # Caught up: Normal batch size
            self.batch_size = max(self.batch_size // 2, 100)
        
        return self.fetch_batch(self.batch_size)

# SOLUTION 3: Spillover to storage
def process_with_spillover(batch):
    try:
        process_realtime(batch)
    except BackpressureException:
        # Spill to S3, process in batch later
        write_to_s3(batch, "/overflow/")
        trigger_batch_catchup()
```

---

## 7️⃣ Data Lake & Storage Design (Q46-55)

### Q46: Data Lake vs Data Warehouse

| Aspect | Data Lake | Data Warehouse |
|--------|-----------|----------------|
| **Schema** | Schema-on-read | Schema-on-write |
| **Data Types** | All (structured, semi, unstructured) | Structured only |
| **Cost** | Low (object storage) | Higher (compute tied) |
| **Query Speed** | Slower (depends on format) | Optimized for SQL |
| **Flexibility** | High | Lower |

---

### Q47: Why data lakes fail in practice

| Failure Mode | Cause | Solution |
|--------------|-------|----------|
| **Data Swamp** | No governance, anyone dumps anything | Catalog, access controls |
| **Poor Performance** | Small files, no indexing | Optimize, Z-ordering |
| **No Trust** | Data quality unknown | Validation, lineage |
| **Skill Gap** | Requires Spark/engineering skills | Abstraction layer (Databricks) |

---

### Q49: Open Table Formats (Iceberg/Delta/Hudi)

| Feature | Delta Lake | Apache Iceberg | Apache Hudi |
|---------|------------|----------------|-------------|
| **ACID** | Yes | Yes | Yes |
| **Time Travel** | Yes | Yes | Yes |
| **Schema Evolution** | Yes | Yes | Yes |
| **Engine Support** | Spark, Databricks | Spark, Trino, Flink | Spark, Flink |
| **Partition Evolution** | Limited | Yes (hidden partitions) | Yes |
| **Best For** | Databricks users | Multi-engine | CDC/streaming |

---

### Q51: Why Medallion Architecture exists

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MEDALLION ARCHITECTURE                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  Raw Data        Clean Data        Business Data       Analytics
      │               │                  │                  │
      ▼               ▼                  ▼                  ▼
┌──────────┐    ┌──────────┐       ┌──────────┐       ┌──────────┐
│  BRONZE  │───▶│  SILVER  │──────▶│   GOLD   │──────▶│ Reports  │
│  (Raw)   │    │ (Cleaned)│       │(Business)│       │(Consumed)│
└──────────┘    └──────────┘       └──────────┘       └──────────┘
     │               │                  │
  Append          Dedupe             Aggregate
  only            Validate           Join dims
  As-is           Type cast          Business logic
```

**Benefits:**
1. **Debuggability** - Raw data always preserved
2. **Reprocessing** - Can rebuild Silver from Bronze
3. **Separation** - Data engineers vs analysts work different layers
4. **Quality** - Progressively cleaner data

---

## 8️⃣ Data Quality & Schema (Q56-65)

### Q56: Detect bad data early

```python
# DATA QUALITY CHECKS AT BRONZE INGESTION

from great_expectations.core import ExpectationSuite

checks = [
    # Null checks
    {"expectation_type": "expect_column_values_to_not_be_null", 
     "kwargs": {"column": "order_id"}},
    
    # Range checks
    {"expectation_type": "expect_column_values_to_be_between",
     "kwargs": {"column": "amount", "min_value": 0, "max_value": 100000}},
    
    # Freshness check
    {"expectation_type": "expect_column_max_to_be_between",
     "kwargs": {"column": "event_time", 
                "min_value": datetime.now() - timedelta(hours=1)}},
    
    # Uniqueness
    {"expectation_type": "expect_column_values_to_be_unique",
     "kwargs": {"column": "order_id"}},
    
    # Row count anomaly
    {"expectation_type": "expect_table_row_count_to_be_between",
     "kwargs": {"min_value": 1000, "max_value": 1000000}},
]

# Fail fast: Block pipeline on critical failures
if results["critical_failures"] > 0:
    raise DataQualityError("Critical data quality failure")
```

---

### Q61: Producer vs Consumer schema ownership

| Model | Who Defines | Pros | Cons |
|-------|-------------|------|------|
| **Producer-owned** | Data producer | Clear ownership | Consumer adapts |
| **Consumer-owned** | Data consumer | Fit for purpose | Many versions |
| **Shared Contract** | Both agree | Explicit expectations | Coordination overhead |

```
RECOMMENDATION: Producer-owned with Contract Testing

Producer defines schema → Schema Registry → Consumer validates

Breaking changes require:
1. Producer proposes change
2. Consumers review impact
3. Migration plan agreed
4. Deprecation period
```

---

### Q63: Breaking vs Non-breaking schema changes

| Change | Breaking | Safe |
|--------|----------|------|
| Add nullable column | | ✓ |
| Add required column | ✓ | |
| Remove column | ✓ | |
| Rename column | ✓ | |
| Widen type (INT→BIGINT) | | ✓ |
| Narrow type (BIGINT→INT) | ✓ | |
| Change column order | | ✓ (for most formats) |

---

## 9️⃣ Failure Scenarios (Q89-93)

### Q89: Source system sends duplicate data

```python
# DETECTION
duplicates = df.groupBy("event_id").count().filter(col("count") > 1)
if duplicates.count() > 0:
    log.warning(f"Detected {duplicates.count()} duplicate event_ids")

# PREVENTION: Deduplication in ingestion
df_deduped = df.dropDuplicates(["event_id"])

# OR: Use MERGE with match condition
deltaTable.merge(
    source.alias("src"),
    "target.event_id = src.event_id"  # Upsert, not duplicate
).whenNotMatchedInsertAll().execute()
```

---

### Q90: Downstream BI reports wrong numbers

**Debugging Framework:**

```
1. DEFINE THE DISCREPANCY
   - Which metric is wrong?
   - How wrong? (2% vs 200%)
   - When did it start?

2. TRACE DATA LINEAGE
   Source → Bronze → Silver → Gold → BI
   Compare counts/sums at each layer

3. COMMON CAUSES
   - JOIN explosion (duplicates)
   - Filter too aggressive
   - Timezone issues
   - Schema evolution
   - Stale cache

4. VALIDATE FIXES
   - Backtest against known-good periods
   - Shadow mode before production
```

---

### Q91: Streaming lag keeps increasing

**Diagnosis:**

```python
# 1. CHECK INPUT RATE vs PROCESSING RATE
consumer_lag = get_kafka_consumer_lag()
processing_rate = get_processing_rate()
input_rate = get_input_rate()

if input_rate > processing_rate:
    print("Consumer can't keep up! Need more resources or optimization")

# 2. IDENTIFY BOTTLENECK
# Is it CPU, memory, network, or downstream?

# 3. SOLUTIONS
# a) Scale out (more partitions, more consumers)
# b) Optimize processing (reduce complexity)
# c) Increase batch size (fewer batches)
# d) Filter at source (process less data)
```

---

### Q92: Batch job misses SLA

**Response Playbook:**

```
1. IMMEDIATE (< 5 min)
   - Check Spark UI for failed/slow tasks
   - Check cluster resources (CPU, memory, disk)
   - Check input data size (spike?)

2. SHORT-TERM (< 1 hour)
   - Restart with more resources if needed
   - Skip non-critical steps if possible
   - Notify stakeholders with ETA

3. ROOT CAUSE (< 1 day)
   - Was it data volume? → Scaling plan
   - Was it code? → Performance fix
   - Was it infra? → Capacity/reliability fix

4. PREVENTION
   - Set up leading indicator alerts
   - Autoscale for peaks
   - Add SLA buffer in schedule
```

---

### Q93: Schema change breaks pipeline

```python
# IMMEDIATE RECOVERY
def handle_schema_mismatch(df, expected_schema):
    # Add missing columns with default
    for field in expected_schema.fields:
        if field.name not in df.columns:
            df = df.withColumn(field.name, lit(None).cast(field.dataType))
    
    # Drop extra columns
    df = df.select([f.name for f in expected_schema.fields])
    
    return df

# PREVENTION: Schema Registry + Validation
from confluent_kafka.schema_registry import SchemaRegistryClient

def validate_schema_compatibility(new_schema, subject):
    client = SchemaRegistryClient({"url": registry_url})
    
    # Check if new schema is backward compatible
    is_compatible = client.test_compatibility(subject, new_schema)
    
    if not is_compatible:
        raise SchemaBreakingChange(f"Schema not backward compatible")
```

---

## 🔟 Design Judgment (Q94-100)

### Q94: How to avoid over-engineering

**Signs of Over-Engineering:**
- Building for 100x scale when you have 1x
- Streaming when batch is fine
- Microservices when monolith works
- Custom framework when open source exists

**Guidelines:**
1. **YAGNI** - You Aren't Gonna Need It
2. **Start simple** - Iterate when needed
3. **Measure first** - Don't optimize without data
4. **TCO** - Consider maintenance, not just build

---

### Q97: Build vs Buy decision

| Factor | Build | Buy |
|--------|-------|-----|
| **Core Competency** | Yes if differentiator | No if commodity |
| **Customization** | Need specific features | Standard works |
| **Time** | Months | Days |
| **Cost** | Dev + maintenance | License + integration |
| **Control** | Full | Vendor-dependent |

**Framework:**
```
Is this a competitive differentiator?
├── YES → Consider building
└── NO
    └── Is there a mature solution?
        ├── YES → Buy/use OSS
        └── NO → Build minimal version
```

---

### Q99: Design global-scale analytics platform

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GLOBAL ANALYTICS PLATFORM                                 │
└─────────────────────────────────────────────────────────────────────────────┘

US-WEST                US-EAST               EU-WEST               APAC
┌──────────┐          ┌──────────┐          ┌──────────┐          ┌──────────┐
│ Ingest   │          │ Ingest   │          │ Ingest   │          │ Ingest   │
│ (Local)  │          │ (Local)  │          │ (Local)  │          │ (Local)  │
└────┬─────┘          └────┬─────┘          └────┬─────┘          └────┬─────┘
     │                     │                     │                     │
     └─────────────────────┼─────────────────────┼─────────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Central Lake │
                    │  (US-WEST)   │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ US Cache │ │ EU Cache │ │APAC Cache│
        │(Redshift)│ │(Regional)│ │(Regional)│
        └──────────┘ └──────────┘ └──────────┘

DESIGN DECISIONS:
1. Ingest locally (low latency, data residency)
2. Replicate to central lake (global view)
3. Cache aggregates regionally (query latency)
4. EU data stays in EU (GDPR)
```

---

### Q100: Design transportation/logistics data platform

**See Q86 for full architecture.**

**Key Considerations:**
1. **Real-time tracking** - GPS, scan events
2. **Route optimization** - ML on historical data
3. **SLA monitoring** - Streaming alerts
4. **Cost analysis** - Batch aggregations
5. **Partner integration** - APIs, file drops
```
