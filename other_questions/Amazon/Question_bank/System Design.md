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

---

# Question Bank 4: Advanced Data & Software Engineering

> **Principal-Level Breadth with Senior-Level Depth**

---

## 1️⃣ Full SDLC – Architecture & Design (Q1-5)

### Q1: Monolith vs Modular Monolith vs Microservices for Data Platforms

| Architecture | When to Use | Trade-offs |
|--------------|-------------|------------|
| **Monolith** | Small team (<5), early stage, single domain | Simple but hard to scale team |
| **Modular Monolith** | Growing team, clear domain boundaries, shared infra | Best balance for most data teams |
| **Microservices** | Large org, independent deployment needs, polyglot | Operational overhead, distributed debugging |

**Decision Framework:**
```
Team Size < 5           → Monolith
Team Size 5-20          → Modular Monolith  
Team Size > 20 + Multi-domain → Microservices
```

**Data Platform Specific:** Modular monolith often wins because:
- Shared metadata/catalog is critical
- Cross-pipeline dependencies are common
- Consistent tooling reduces cognitive load

---

### Q2: Architectural Principles for Data Systems vs Application Systems

| Principle | Application Systems | Data Systems |
|-----------|---------------------|--------------|
| **Primary Goal** | Request latency | Throughput & correctness |
| **State** | Stateless preferred | Inherently stateful |
| **Failure Mode** | Retry/Circuit breaker | Idempotent replay |
| **Coupling** | API contracts | Schema contracts |
| **Testing** | Unit/Integration | Data validation + lineage |

**Key Data System Principles:**
1. **Immutability** - Write once, read many
2. **Idempotency** - Re-run without side effects
3. **Late Binding** - Schema on read flexibility
4. **Observability** - Data lineage, not just logs

---

### Q3: Designing for Backward Compatibility in Data Pipelines

**Strategies:**

| Strategy | Implementation | Use Case |
|----------|----------------|----------|
| **Schema Evolution** | Avro/Protobuf with defaults | Adding columns |
| **Versioned Endpoints** | `/v1/data`, `/v2/data` | Breaking changes |
| **Migration Window** | Dual-write for N days | Major refactors |
| **Feature Flags** | Toggle new logic | Gradual rollout |

**Code Pattern:**
```python
# Backward compatible schema addition
new_schema = {
    "existing_field": "required",
    "new_field": {"type": "string", "default": "N/A"}  # Default = safe
}
```

---

### Q4: Designing APIs for Data Consumption

**Best Practices:**
1. **Pagination** - Cursor-based for large datasets
2. **Filtering** - Server-side, not client-side
3. **Versioning** - URL or header-based
4. **Rate Limiting** - Protect pipeline resources
5. **Async for Heavy** - Return job_id, poll for results

---

### Q5: Preventing Tight Coupling Between Producers and Consumers

| Technique | How It Works |
|-----------|--------------|
| **Schema Registry** | Central contract, versioned |
| **Event Sourcing** | Consumers replay from log |
| **Dead Letter Queue** | Isolate bad messages |
| **Semantic Versioning** | Breaking = major bump |

---

## SDLC – Coding Standards (Q6-10)

### Q6: Coding Standards for Data Pipelines

| Standard | Why It Matters |
|----------|----------------|
| **Explicit column selection** | No `SELECT *` - schema changes break silently |
| **Parameterized dates** | No hardcoded `'2024-01-01'` |
| **Idempotent writes** | `MERGE`/`UPSERT`, not `INSERT` |
| **Logging business keys** | Debug without PII exposure |
| **Type hints** | Catch errors before runtime |

---

### Q7: Enforcing Standards Across Large Teams

1. **Pre-commit hooks** - Block non-compliant code
2. **CI linting** - SQLFluff, Black, Ruff
3. **PR templates** - Checklist for reviewers
4. **Architecture Decision Records (ADRs)** - Document "why"
5. **Shared libraries** - Encapsulate patterns

---

### Q8: Performance vs Readability Balance

**Rule:** Optimize for readability FIRST, then profile.

```python
# ❌ Premature optimization
result = reduce(lambda a,b: a+b, map(lambda x: x**2, filter(lambda x: x>0, data)))

# ✅ Readable first
positives = [x for x in data if x > 0]
squares = [x**2 for x in positives]
result = sum(squares)
```

**When to sacrifice readability:**
- Hot paths proven by profiling
- Memory-constrained streaming
- Cost-critical large-scale jobs

---

### Q9: What Makes Data Code Hard to Refactor

1. **Implicit dependencies** - Consumers unknown
2. **No tests** - Fear of breaking
3. **Magic strings** - Column names everywhere
4. **Tight coupling** - SQL in Python strings
5. **No lineage** - Can't trace impact

**Solution:** Invest in metadata/lineage before major refactors.

---

### Q10: Managing Technical Debt in Pipelines

**Prioritization Framework:**
```
Debt Score = (Failure Frequency × Business Impact) / Refactor Effort
```

**Debt Types:**
- **High Priority:** Causes incidents, blocks features
- **Medium:** Slows development, manual workarounds
- **Low:** Cosmetic, minor inefficiencies

---

## SDLC – Code Reviews (Q11-15)

### Q11: Data Engineering Code Review Checklist

| Check | What to Look For |
|-------|------------------|
| **Correctness** | JOIN logic, NULL handling, deduplication |
| **Idempotency** | Re-runnable without side effects |
| **Performance** | Partition pruning, broadcast hints |
| **Schema** | Explicit types, evolution safe |
| **Tests** | Edge cases covered |

---

### Q12: Reviewing SQL for Correctness and Performance

**Correctness:**
- JOINs: Cartesian risk? Fanout?
- NULLs: Handled in WHERE, aggregations?
- GROUP BY: Correct grain?

**Performance:**
- Partition filters present?
- Functions on partition columns? (Bad!)
- Subquery vs JOIN choice?

---

### Q13: Detecting Hidden Data Quality Bugs in PRs

| Red Flag | Example |
|----------|---------|
| **Missing NULL handling** | `WHERE status != 'FAILED'` misses NULLs |
| **Implicit type conversion** | JOIN on string vs int |
| **Aggregation before filter** | Wrong grain |
| **Timezone assumptions** | `DATE(timestamp)` without TZ |

---

### Q14: Reviewing Spark vs Python Services

| Spark | Python Services |
|-------|-----------------|
| Partition strategy | API contracts |
| Shuffle operations | Memory management |
| Broadcast usage | Threading/async |
| Caching strategy | Connection pooling |

---

### Q15: Common Red Flags in Data PRs

1. `SELECT *` anywhere
2. No WHERE clause on date columns
3. `COUNT(*)` without considering NULLs
4. Hardcoded dates/values
5. No idempotency pattern

---

## SDLC – Source Control (Q16-20)

### Q16: GitFlow vs Trunk-Based for Data Teams

| Approach | Best For |
|----------|----------|
| **Trunk-Based** | Continuous deployment, feature flags |
| **GitFlow** | Release cycles, multiple versions |
| **Data Recommendation** | Trunk-based with feature flags for schemas |

---

### Q17: Versioning SQL and Schemas

```
schemas/
├── v1/
│   └── orders.sql
├── v2/
│   └── orders.sql  # Added new_column
└── migrations/
    └── v1_to_v2.sql
```

**Tools:** Flyway, Alembic, dbt migrations

---

### Q18-20: Branch Management

- **Long-running branches:** Rebase frequently, time-box to 2 weeks
- **Merge conflicts in SQL:** Use semantic merge tools, avoid reformatting
- **Never commit:** Credentials, PII, large data files, `.env`

---

## SDLC – CI/CD (Q21-25)

### Q21: Safe Data Pipeline Deployment

1. **Shadow mode** - Run new logic, compare outputs
2. **Canary** - Process subset first
3. **Feature flags** - Toggle at runtime
4. **Dual-write** - Both old and new for N days

---

### Q22: Blue-Green vs Canary for Data

| Strategy | Data Systems Use |
|----------|------------------|
| **Blue-Green** | Table swaps, Redshift schemas |
| **Canary** | Process 1% of partitions first |
| **Recommended** | Canary + automated comparison |

---

### Q23: Rolling Back Data Changes

**Sequence:**
1. Stop pipeline immediately
2. Restore from snapshot/backup
3. Replay from last known good checkpoint
4. Validate with smoke tests
5. Notify downstream consumers

---

### Q24: Data CI Pipeline Validation

| Check | Tool |
|-------|------|
| SQL lint | SQLFluff |
| Schema validation | Great Expectations |
| Unit tests | pytest + mocks |
| Integration | dbt test |
| Cost estimation | Query explain |

---

### Q25: Preventing Downstream Breaks

1. **Schema registry** - Enforce compatibility
2. **Contract tests** - Producer validates consumer expectations
3. **Deprecation notices** - In metadata catalog
4. **Staged rollout** - Time buffer for discovery

---

## SDLC – Testing (Q26-30)

### Q26: Unit Testing for Data Pipelines

| Testable | Not Easily Testable |
|----------|---------------------|
| Transformation logic | Full Spark cluster |
| Business rules | External API calls |
| Date handling | Live database |
| NULL handling | Production data |

---

### Q27: Data Tests vs Software Tests

| Software Tests | Data Tests |
|----------------|------------|
| Behavior | Correctness |
| Mocked inputs | Sample data |
| Deterministic | Statistical |
| Fast | Can be slow |

---

### Q28: Testing Spark Jobs

```python
def test_transformation():
    spark = SparkSession.builder.master("local[2]").getOrCreate()
    input_df = spark.createDataFrame([...])
    result = transform(input_df)
    assert result.count() == expected_count
```

---

### Q29: Contract Testing for Data

**Producer guarantees:**
- Schema structure
- Value ranges
- Freshness SLA

**Consumer validates:**
- Required fields present
- Types match
- Volume in expected range

---

### Q30: Why Most Data Tests Fail in Practice

1. **Too slow** - Full pipeline for one test
2. **Flaky** - Time-dependent, external deps
3. **Wrong scope** - Testing infra, not logic
4. **Maintenance burden** - Test data rots

---

## SDLC – Operational Excellence (Q31-35)

### Q31: Operational Excellence for Data Systems

**Definition:** Ability to run and monitor systems to deliver business value while continuously improving.

**Pillars:**
1. Observability
2. Incident response
3. Capacity planning
4. Continuous improvement

---

### Q32: Pipeline Health Metrics

| Metric | Target |
|--------|--------|
| Success rate | >99.9% |
| Latency (P95) | <SLA |
| Data freshness | <threshold |
| Cost per TB | Decreasing |
| Incident count | Decreasing |

---

### Q33: Reducing On-Call Burden

1. **Eliminate noise** - Tune alerts
2. **Self-healing** - Auto-retry, failover
3. **Runbooks** - Automate common fixes
4. **Blameless culture** - Learn, don't punish

---

### Q34: Runbook Contents

1. Alert description
2. Impact assessment
3. Diagnostic steps
4. Resolution steps
5. Escalation path
6. Post-resolution validation

---

### Q35: Data Incident Post-Mortems

**Template:**
```
## Incident: [Title]
**Impact:** [Users/Systems affected]
**Duration:** [Start - End]
**Root Cause:** [Technical cause]
**Detection:** [How discovered]
**Resolution:** [Fix applied]
**Lessons:** [What we learned]
**Action Items:** [Prevent recurrence]
```

---

## 2️⃣ Best Practices in Data Engineering (Q36-40)

### Q36: What Makes a Data Platform Scalable

| Dimension | Scalability Approach |
|-----------|---------------------|
| **Data volume** | Partitioning, columnar formats |
| **Query concurrency** | Query queuing, caching |
| **Team scale** | Self-service, governance |
| **Cost** | Spot instances, tiered storage |

---

### Q37: Designing for Reprocessing and Backfills

1. **Partition by date** - Replace, don't append
2. **Immutable raw layer** - Never modify source
3. **Parameterized pipelines** - Accept date ranges
4. **Idempotent writes** - MERGE/UPSERT patterns

---

### Q38: Idempotency – Why It Matters and How to Implement

**Why:** Pipelines fail mid-run; re-runs must be safe.

| Pattern | Implementation |
|---------|----------------|
| **DELETE + INSERT** | Clear partition, then write |
| **MERGE/UPSERT** | Match on keys, update |
| **Overwrite mode** | Spark `.mode("overwrite")` |
| **Checkpointing** | Track last processed ID |

---

### Q39: Avoiding "Data Swamps"

| Problem | Solution |
|---------|----------|
| No metadata | Enforce cataloging |
| No ownership | Assign data stewards |
| No quality | Automated profiling |
| No discovery | Searchable catalog |

---

### Q40: Fail Fast vs Be Tolerant

| Approach | When to Use |
|----------|-------------|
| **Fail Fast** | Schema violations, critical data |
| **Be Tolerant** | Late data, optional fields |
| **Hybrid** | Quarantine bad records, continue |

---

## 3️⃣ Non-Relational Databases (Q41-56)

### Object Storage (Q41-44)

**Q41: Why Object Storage is Backbone**
- Infinite scale at low cost
- Decoupled storage and compute
- Native cloud integration

**Q42: Performance Pitfalls**
- Small files (< 128MB) = slow
- No listing optimization
- High latency per request

**Q43: Designing for Efficient Reads**
- Partition by query patterns
- Use columnar formats (Parquet)
- Compact small files regularly

**Q44: Consistency Guarantees**
- S3: Strong read-after-write (2020+)
- Still no atomic rename
- Use Delta/Iceberg for transactions

---

### Key-Value & Document Stores (Q45-48)

**Q45: When to Choose**

| Store | Use Case |
|-------|----------|
| **DynamoDB** | Low-latency key lookups, serverless |
| **Redis** | Caching, sessions, counters |
| **CosmosDB** | Multi-model, global distribution |
| **MongoDB** | Flexible schemas, aggregations |

**Q46: Access Patterns Drive Design**
- Single-table design for DynamoDB
- Denormalize for read patterns
- Composite keys for range queries

**Q47: Hot Partition Problem**
- Detection: Monitor partition metrics
- Mitigation: Add random suffix to keys

**Q48: Schema Evolution**
- Optional fields with defaults
- Versioned documents
- Gradual migrations

---

### Column-Family DBs (Q49-52)

**Q49: When Cassandra Fits**
- High write throughput
- Geo-distributed
- Known query patterns

**Q50: Write vs Read Optimized**

| Optimize For | Trade-off |
|--------------|-----------|
| Writes | Fast ingestion, slow queries |
| Reads | Denormalize, more storage |

**Q51: TTLs**
- Use: Time-series, temporary data
- Avoid: Audit trails, compliance

**Q52: Secondary Index Dangers**
- Creates hidden tables
- Can cause hot spots
- Prefer materialized views

---

### Graph Databases (Q53-56)

**Q53: When Graph DB is Justified**
- Relationship traversal is core query
- Variable-depth queries
- Examples: Fraud detection, recommendations

**Q54: Why Graph DBs Fail at Scale**
- Super nodes (celebrities in social graphs)
- Complex query optimization
- Operational immaturity

**Q55: Relationships vs JOINs**
- Graphs: O(1) traversal
- SQL: O(n) JOIN

**Q56: Analytics on Graph Data**
- Export to columnar for bulk analytics
- Use GraphX/Spark for batch processing
- OLAP graph databases emerging

---

## 4️⃣ Integration with Analytics & ML (Q57-65)

### Q57: Pipelines for Analytics vs ML

| Analytics | ML |
|-----------|-----|
| Aggregated data | Row-level features |
| Historical trends | Point-in-time correctness |
| Human consumers | Model consumers |
| SQL-friendly | Feature vectors |

---

### Q58: Feature Engineering – Batch vs Online

| Type | Latency | Use Case |
|------|---------|----------|
| **Batch** | Hours | Training, historical |
| **Near real-time** | Minutes | Session features |
| **Online** | Milliseconds | Real-time inference |

---

### Q59: Why Feature Stores Exist

1. **Consistency** - Same features for training/serving
2. **Reuse** - Share across teams
3. **Point-in-time** - Prevent data leakage
4. **Low latency** - Pre-computed serving

---

### Q60: Data Leakage – How Pipelines Cause It

| Leakage Type | Cause |
|--------------|-------|
| **Target leakage** | Future data in features |
| **Train-test** | Same records in both |
| **Temporal** | Using event_time, not process_time |

---

### Q61: Training-Serving Skew Prevention

1. **Single feature pipeline** - Same code path
2. **Feature store** - Pre-computed features
3. **Schema validation** - Same types/ranges
4. **Monitoring** - Compare feature distributions

---

### Q62: Designing Pipelines for Multiple Use Cases

```
Raw Data
    ↓
[Bronze] - Ingestion (all use cases)
    ↓
[Silver] - Cleaned, joined
    ↓
┌───────────┬───────────┬───────────┐
↓           ↓           ↓           ↓
Ad-hoc   Dashboards  ML Training  Inference
(Presto)  (BI Gold)  (Features)   (Online)
```

---

### Q63: Dataset Versioning for ML

| Approach | Tool |
|----------|------|
| Snapshot-based | Delta Lake time travel |
| Hash-based | DVC |
| Catalog-based | MLflow datasets |

---

### Q64: Offline vs Online Feature Trade-offs

| Offline | Online |
|---------|--------|
| Batch compute | Real-time compute |
| High throughput | Low latency |
| Cost-efficient | Infrastructure heavy |
| Stale (minutes-hours) | Fresh (seconds) |

---

### Q65: Validating Data Before Model Training

| Check | Tool |
|-------|------|
| Schema | Great Expectations |
| Statistics | Evidently, Whylogs |
| Drift | Population stability index |
| Freshness | Timestamp checks |

---

## 5️⃣ Data Modeling for Analytics, Reporting & ML (Q66-75)

### Q66: Modeling for BI vs ML vs Operational Reporting

| Use Case | Modeling Approach |
|----------|-------------------|
| **BI** | Star schema, aggregates, denormalized |
| **ML** | Wide features, point-in-time, sparse |
| **Operational** | Normalized, real-time, low latency |

---

### Q67: Why Star Schemas Still Matter

1. **Query simplicity** - Understandable by analysts
2. **Performance** - Columnar storage optimization
3. **BI tool compatibility** - Tableau, Power BI
4. **Clear semantics** - Facts vs dimensions

---

### Q68: When Denormalization is Right

| Denormalize | Keep Normalized |
|-------------|-----------------|
| Read-heavy workloads | Write-heavy OLTP |
| Known query patterns | Ad-hoc exploration |
| Data warehouse | Source systems |
| ML features | Audit/compliance |

---

### Q69: Wide Tables vs Narrow Tables

| Wide | Narrow |
|------|--------|
| Single scan for all cols | Join multiple tables |
| Sparse/NULL heavy | Dense, efficient |
| Schema evolution pain | Flexible additions |
| ML features | Transactional |

---

### Q70: Time-Aware Model Design

1. **Snapshot tables** - State at each point in time
2. **Slowly changing dims** - Type 2 for history
3. **Validity columns** - `valid_from`, `valid_to`
4. **Event sourcing** - Append-only, reconstruct

---

### Q71: SCDs in ML Context

**Problem:** ML needs feature values AS OF training time.

**Solution:**
```sql
-- Point-in-time join
SELECT f.*, d.customer_tier
FROM features f
JOIN customer_dim d 
  ON f.customer_id = d.customer_id
 AND f.event_date BETWEEN d.valid_from AND d.valid_to
```

---

### Q72: Feature Explosion – Control Strategies

1. **Feature selection** - Remove low-variance
2. **Dimensionality reduction** - PCA, embeddings
3. **Domain grouping** - Aggregate similar
4. **Governance** - Approve before adding

---

### Q73: Models That Survive Schema Changes

1. **Loose coupling** - Select by name, not position
2. **Default values** - Graceful new columns
3. **Schema versioning** - Track compatibility
4. **Feature aliases** - Abstract from physical

---

### Q74: Avoiding Metrics Inconsistency

| Problem | Solution |
|---------|----------|
| Different definitions | Metric dictionary |
| Calculation drift | Central metrics layer |
| Stale docs | Code-as-documentation |
| Siloed teams | Cross-team reviews |

---

### Q75: Semantic Layer – Why It Matters

**Definition:** Abstraction between raw data and consumers.

**Benefits:**
- Consistent metrics across tools
- Business-friendly names
- Security/access control
- Performance optimization

**Tools:** dbt Metrics, Looker, Cube.dev

---

## 6️⃣ Data Quality, Reliability & Process (Q76-95)

### Data Quality (Q76-80)

**Q76: What is "Good" Data Quality**

| Dimension | Measure |
|-----------|---------|
| **Accuracy** | Matches real world |
| **Completeness** | No unexpected NULLs |
| **Consistency** | Same across systems |
| **Timeliness** | Fresh enough for use |
| **Validity** | Conforms to constraints |

---

**Q77: Preventive vs Detective Checks**

| Preventive | Detective |
|------------|-----------|
| Schema validation on ingest | Post-load profiling |
| NOT NULL constraints | NULL count alerts |
| API validation | Anomaly detection |
| Contract testing | Reconciliation |

---

**Q78: Prioritizing Quality Checks**

```
Priority = (Business Impact × Frequency) / Detection Cost
```

Focus on:
1. Revenue-impacting fields
2. ML model inputs
3. Regulatory data

---

**Q79: Freshness vs Accuracy Trade-offs**

| Optimization | Trade-off |
|--------------|-----------|
| **Freshness first** | Accept some errors, fix later |
| **Accuracy first** | Delay until validated |
| **Balanced** | Tiered SLAs by use case |

---

**Q80: When Bad Data is Acceptable**

1. Non-critical analytics
2. Exploration datasets
3. Sandbox environments
4. When quarantined and labeled

---

### Reliability Engineering (Q81-85)

**Q81: Data SLOs**

| SLO Type | Example |
|----------|---------|
| **Freshness** | Data < 1 hour old |
| **Completeness** | > 99.9% rows present |
| **Accuracy** | Error rate < 0.1% |
| **Availability** | 99.95% query success |

---

**Q82: Graceful Degradation Design**

1. **Fallback to cache** - Serve stale if fresh fails
2. **Partial processing** - Skip bad partitions
3. **Default values** - Use historical averages
4. **Alert and continue** - Don't block all data

---

**Q83: Replayability Patterns**

1. **Immutable raw layer** - Never delete source
2. **Idempotent transforms** - Safe to re-run
3. **Partitioned outputs** - Replace, don't append
4. **Checkpoints** - Resume from failure

---

**Q84: Checkpointing and Watermarking**

| Concept | Use Case |
|---------|----------|
| **Checkpoint** | Resume batch from failure |
| **Watermark** | Track event-time progress in streaming |
| **High watermark** | Last processed record ID |

---

**Q85: Handling Partial Failures**

1. **Quarantine** - Isolate bad records
2. **Dead letter queue** - Retry pipeline
3. **Compensating action** - Fix and replay
4. **Alerting** - Notify before escalation

---

### Observability (Q86-90)

**Q86: Monitoring vs Observability**

| Monitoring | Observability |
|------------|---------------|
| Known unknowns | Unknown unknowns |
| Dashboards | Exploration |
| Metrics | Traces + logs + metrics |
| Alert on threshold | Debug root cause |

---

**Q87: Golden Signals for Data Pipelines**

| Signal | Metric |
|--------|--------|
| **Latency** | Time to complete |
| **Traffic** | Records processed |
| **Errors** | Failure rate |
| **Saturation** | Resource utilization |
| **Freshness** | Data age |

---

**Q88: Debugging Data Issues Faster**

1. **Lineage** - Trace upstream source
2. **Row-level logging** - Sample problematic records
3. **Diff analysis** - Compare good vs bad runs
4. **Time travel** - Check historical states

---

**Q89: Lineage – How Much is Enough**

| Level | Complexity | Value |
|-------|------------|-------|
| **Table-level** | Low | Basic impact analysis |
| **Column-level** | Medium | Accurate dependencies |
| **Row-level** | High | Full audit trail |

**Recommendation:** Column-level for most use cases.

---

**Q90: Impact Analysis When Things Break**

1. Identify affected table
2. Query lineage graph for downstream
3. Notify downstream owners
4. Estimate business impact
5. Prioritize fix

---

### Continuous Improvement (Q91-95)

**Q91: Identifying Pipeline Bottlenecks**

| Tool | What It Shows |
|------|---------------|
| Spark UI | Stage times, shuffle |
| Query plans | Expensive operations |
| Profiling | Memory, CPU usage |
| DAG visualization | Critical path |

---

**Q92: Sunsetting Unused Datasets**

1. Track access logs
2. No queries for N days → candidate
3. Notify owners
4. Archive, then delete
5. Keep lineage for audit

---

**Q93: Measuring ROI of Data Work**

| Metric | Measurement |
|--------|-------------|
| Cost reduction | Infra savings |
| Time saved | Hours analyst work |
| Revenue impact | Attribution to data |
| Risk avoided | Incidents prevented |

---

**Q94: Driving Quality Culture**

1. Make quality visible (dashboards)
2. Celebrate good patterns
3. Blameless post-mortems
4. Quality in OKRs
5. Automate enforcement

---

**Q95: Automation Opportunities**

| Area | Automation |
|------|------------|
| Testing | dbt test, Great Expectations |
| Deployment | CI/CD pipelines |
| Monitoring | Auto-generated alerts |
| Documentation | Schema-based docs |
| Cost | Auto-scaling, archival |

---

## 7️⃣ Scenario-Based Maturity Questions (Q96-100)

### Q96: Pipeline is Correct but Too Slow

**Approach:**
1. Profile to find bottleneck
2. Check partition pruning
3. Reduce shuffles (broadcast joins)
4. Increase parallelism
5. Consider caching or materialization
6. Evaluate infra sizing

---

### Q97: Data is Fast but Sometimes Wrong

**Approach:**
1. Quantify error rate and impact
2. Add data quality checks
3. Implement circuit breakers
4. Create reconciliation process
5. Balance: Sometimes fast + monitored > slow + perfect

---

### Q98: ML Model Accuracy Dropped

**Investigation Order:**
1. **Data drift** - Feature distributions changed?
2. **Upstream changes** - Schema/pipeline modified?
3. **Data quality** - NULLs, outliers increased?
4. **Temporal shift** - Seasonality, concept drift?
5. **Training-serving skew** - Features differ at inference?

---

### Q99: Dashboards Don't Match Business Numbers

**Root Cause Checklist:**
1. Different time zones
2. Different filter criteria
3. Different deduplication logic
4. Aggregation grain mismatch
5. Late-arriving data handling
6. Definition inconsistency

**Solution:** Create semantic layer with shared definitions.

---

### Q100: Inherited Fragile Data Platform – First 90 Days

**Week 1-2: Assess**
- Document current state
- Identify critical pipelines
- Meet stakeholders

**Week 3-4: Stabilize**
- Fix highest-impact issues
- Add basic monitoring
- Create runbooks

**Month 2: Foundation**
- Improve testing coverage
- Establish CI/CD
- Start deprecating legacy

**Month 3: Scale**
- Self-service improvements
- Documentation
- Knowledge sharing

---

## 🧠 How Interviewers Evaluate These

**They listen for:**
- Decision frameworks with trade-offs
- Real failure stories and lessons
- Preventive thinking
- Business alignment

**They reject:**
- Tool-only answers ("just use Spark")
- Absolutist thinking ("always use X")
- Over-engineering

---

## 🎯 Interview Answer Template

```
For [topic]:
1. SUCCESS: [Situation, action, result]
2. FAILURE: [What went wrong, lesson learned]
3. TRADE-OFF: [When I chose A over B, why]
```
