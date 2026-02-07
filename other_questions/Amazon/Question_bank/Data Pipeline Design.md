# ETL / Data Pipeline Design Interview Questions & Answers (Question Bank 1)

> **Amazon Data Engineer Style** - Batch, Streaming, and Reliability Focus

---

## 1️⃣ Batch Pipelines

### Q61: Design a daily shipment aggregation pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  DAILY SHIPMENT AGGREGATION PIPELINE                         │
└─────────────────────────────────────────────────────────────────────────────┘

07:00 UTC ─────────────────────────────────────────────────────────▶ 09:00 UTC

[Source: OLTP DB]        [Ingestion]         [Transform]         [Load]
     │                       │                   │                  │
     ▼                       ▼                   ▼                  ▼
┌──────────┐          ┌───────────┐        ┌──────────┐       ┌──────────┐
│ Shipments│   CDC    │   Bronze  │ Spark  │  Silver  │ Spark │   Gold   │
│   Table  │─────────▶│   Layer   │───────▶│  Layer   │──────▶│   Mart   │
│ (MySQL)  │  Debezium│ (Raw JSON)│  Clean │(Parquet) │ Agg   │ (Metrics)│
└──────────┘          └───────────┘        └──────────┘       └──────────┘
                                                                    │
                                                                    ▼
                                                            ┌──────────────┐
                                                            │  Dashboards  │
                                                            │   (Daily)    │
                                                            └──────────────┘
```

```python
# Airflow DAG for daily aggregation
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-eng',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'daily_shipment_aggregation',
    default_args=default_args,
    schedule_interval='0 7 * * *',  # 7 AM daily
    catchup=False,
)

def extract_shipments(**context):
    """Extract yesterday's shipments from source"""
    execution_date = context['ds']  # YYYY-MM-DD
    # Idempotent: Overwrite partition for this date
    spark.read.jdbc(source_db, query=f"SELECT * FROM shipments WHERE date = '{execution_date}'") \
         .write.mode('overwrite').partitionBy('date').parquet('/bronze/shipments/')

def transform_to_silver(**context):
    """Clean and deduplicate"""
    df = spark.read.parquet(f"/bronze/shipments/date={context['ds']}")
    df_clean = (df
        .dropDuplicates(['shipment_id'])
        .filter(col('status').isNotNull())
        .withColumn('transit_hours', calculate_transit_hours()))
    df_clean.write.mode('overwrite').parquet(f"/silver/shipments/date={context['ds']}")

def aggregate_to_gold(**context):
    """Create daily metrics"""
    df = spark.read.parquet(f"/silver/shipments/date={context['ds']}")
    metrics = df.groupBy('region', 'carrier').agg(
        count('*').alias('shipment_count'),
        avg('transit_hours').alias('avg_transit'),
        sum(when(col('is_delayed'), 1).otherwise(0)).alias('delayed_count')
    )
    metrics.write.mode('overwrite').parquet(f"/gold/daily_metrics/date={context['ds']}")

extract = PythonOperator(task_id='extract', python_callable=extract_shipments, dag=dag)
transform = PythonOperator(task_id='transform', python_callable=transform_to_silver, dag=dag)
aggregate = PythonOperator(task_id='aggregate', python_callable=aggregate_to_gold, dag=dag)

extract >> transform >> aggregate
```

---

### Q62: Idempotent pipeline — explain with example

**Definition:** Running the pipeline N times produces the same result as running it once.

**Why It Matters:**
- Retries after failure don't corrupt data
- Backfills are safe
- Debugging is reproducible

**Implementation Patterns:**

```python
# ✅ PATTERN 1: Partition Overwrite (Idempotent)
df.write \
    .mode('overwrite') \
    .partitionBy('date') \
    .option('replaceWhere', f"date = '{processing_date}'") \
    .format('delta') \
    .save('/gold/metrics/')

# ✅ PATTERN 2: MERGE/Upsert (Idempotent)
deltaTable = DeltaTable.forPath(spark, '/gold/shipments/')
deltaTable.alias('t').merge(
    new_data.alias('s'),
    't.shipment_id = s.shipment_id'
).whenMatchedUpdateAll() \
 .whenNotMatchedInsertAll() \
 .execute()

# ❌ ANTI-PATTERN: Append without deduplication
df.write.mode('append').parquet('/output/')  # Creates duplicates on retry!
```

---

### Q63: Backfill last 30 days of data

```python
# Strategy: Process date-by-date with isolation

def backfill_date_range(start_date, end_date):
    """
    Backfill with these guarantees:
    1. Each date is processed independently (idempotent)
    2. Production SLA unaffected (separate cluster)
    3. Failures don't block subsequent dates
    """
    current = start_date
    results = []
    
    while current <= end_date:
        try:
            # Process single date
            process_date(current)
            results.append({'date': current, 'status': 'SUCCESS'})
        except Exception as e:
            results.append({'date': current, 'status': 'FAILED', 'error': str(e)})
            # Continue to next date, don't stop
        
        current += timedelta(days=1)
    
    # Report results
    failed = [r for r in results if r['status'] == 'FAILED']
    if failed:
        alert_team(f"Backfill completed with {len(failed)} failures: {failed}")
    
    return results

# Airflow: Trigger backfill
# airflow dags backfill -s 2024-01-01 -e 2024-01-30 daily_shipment_aggregation
```

```yaml
# Best Practices for Backfill:
# 1. Use separate compute resources (don't impact production)
# 2. Process oldest first (dependencies)
# 3. Validate each batch before proceeding
# 4. Log extensively for debugging
# 5. Have rollback plan (keep old data until verified)
```

---

### Q64: Handle partial pipeline failures

```python
# Checkpoint pattern for multi-stage pipelines

def run_pipeline_with_checkpoints(date):
    """
    Resume from last successful checkpoint on failure
    """
    checkpoints = load_checkpoints(date)
    
    stages = [
        ('extract', extract_from_source),
        ('clean', clean_and_validate),
        ('transform', apply_business_logic),
        ('load', load_to_warehouse),
    ]
    
    for stage_name, stage_func in stages:
        if checkpoints.get(stage_name) == 'COMPLETED':
            print(f"Skipping {stage_name} (already completed)")
            continue
        
        try:
            save_checkpoint(date, stage_name, 'IN_PROGRESS')
            stage_func(date)
            save_checkpoint(date, stage_name, 'COMPLETED')
        except Exception as e:
            save_checkpoint(date, stage_name, 'FAILED', error=str(e))
            raise

# Stage isolation: Each stage writes to separate location
# extract → /staging/extract/{date}/
# clean → /staging/clean/{date}/
# transform → /staging/transform/{date}/
# load → /gold/{date}/ (final)
```

```python
# Transaction pattern for atomic loads
def atomic_load(source_path, target_table, partition):
    """
    Atomic swap: Never leave target in inconsistent state
    """
    staging_table = f"{target_table}_staging"
    
    # 1. Load to staging
    spark.read.parquet(source_path).write \
        .mode('overwrite') \
        .saveAsTable(staging_table)
    
    # 2. Validate staging
    assert validate_row_count(staging_table)
    assert validate_schema(staging_table, target_table)
    
    # 3. Atomic partition swap
    spark.sql(f"""
        ALTER TABLE {target_table} 
        EXCHANGE PARTITION ({partition}) 
        WITH TABLE {staging_table}
    """)
```

---

### Q65: Reprocess corrupted data safely

```python
def reprocess_corrupted_data(table, start_date, end_date, corruption_type):
    """
    Safely reprocess corrupted data while maintaining production availability
    """
    
    # 1. BACKUP: Copy current data (just in case)
    backup_path = f"/backup/{table}/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    spark.read.format('delta').load(f'/gold/{table}') \
        .filter(f"date BETWEEN '{start_date}' AND '{end_date}'") \
        .write.parquet(backup_path)
    
    # 2. ISOLATE: Process to staging
    staging_path = f"/staging/{table}_reprocess/"
    
    for date in date_range(start_date, end_date):
        # Read from source (not corrupted gold)
        source_df = spark.read.parquet(f'/silver/{table}/date={date}')
        
        # Apply corrections based on corruption type
        if corruption_type == 'DUPLICATES':
            fixed_df = source_df.dropDuplicates(['shipment_id'])
        elif corruption_type == 'NULL_VALUES':
            fixed_df = source_df.fillna({'status': 'UNKNOWN'})
        elif corruption_type == 'WRONG_CALCULATION':
            fixed_df = source_df.withColumn('amount', recalculate_amount())
        
        # Write to staging
        fixed_df.write.mode('overwrite').parquet(f'{staging_path}/date={date}')
    
    # 3. VALIDATE: Compare staging vs backup
    validation_report = compare_datasets(staging_path, backup_path)
    if not validation_report['passed']:
        raise ValidationError(f"Validation failed: {validation_report}")
    
    # 4. SWAP: Atomic replacement
    with transaction():
        for date in date_range(start_date, end_date):
            # Delete corrupted partition
            spark.sql(f"DELETE FROM delta.`/gold/{table}` WHERE date = '{date}'")
            # Insert fixed data
            spark.read.parquet(f'{staging_path}/date={date}').write \
                .format('delta').mode('append').save(f'/gold/{table}')
    
    # 5. CLEANUP: Remove staging (keep backup for N days)
    cleanup_staging(staging_path)
    schedule_backup_deletion(backup_path, days=7)
```

---

## 2️⃣ Streaming / Near Real-Time

### Q66: Design real-time shipment status tracking

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              REAL-TIME SHIPMENT STATUS TRACKING                              │
└─────────────────────────────────────────────────────────────────────────────┘

[Scan Devices]    [Kafka]        [Spark Streaming]     [Serving]     [UI]
     │               │                  │                  │           │
     ▼               ▼                  ▼                  ▼           ▼
┌──────────┐   ┌──────────┐      ┌───────────────┐   ┌──────────┐  ┌───────┐
│  Scanner │──▶│  Topic:  │─────▶│   Structured  │──▶│  Redis   │─▶│ React │
│  Events  │   │  scans   │      │   Streaming   │   │ (Latest) │  │  App  │
└──────────┘   └──────────┘      │  (5 min batch)│   └──────────┘  └───────┘
                    │            └───────────────┘         │
                    │                    │                 │
                    │                    ▼                 │
                    │            ┌───────────────┐         │
                    └───────────▶│  Delta Lake   │◀────────┘
                                 │ (Historical)  │   (Async sync)
                                 └───────────────┘
```

```python
# Spark Structured Streaming implementation
from pyspark.sql.functions import *

# Read from Kafka
scans_stream = (spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("subscribe", "shipment_scans")
    .option("startingOffsets", "latest")
    .load()
)

# Parse JSON payload
parsed = scans_stream.select(
    from_json(col("value").cast("string"), scan_schema).alias("data")
).select("data.*")

# Business logic: Get latest status per shipment
latest_status = (parsed
    .withWatermark("event_time", "10 minutes")  # Handle late data
    .groupBy(
        window("event_time", "5 minutes"),
        "shipment_id"
    )
    .agg(
        last("status").alias("current_status"),
        last("location").alias("current_location"),
        max("event_time").alias("last_update")
    )
)

# Write to Redis (for real-time serving)
def write_to_redis(batch_df, batch_id):
    for row in batch_df.collect():
        redis_client.hset(
            f"shipment:{row.shipment_id}",
            mapping={
                "status": row.current_status,
                "location": row.current_location,
                "updated": row.last_update.isoformat()
            }
        )

latest_status.writeStream \
    .foreachBatch(write_to_redis) \
    .outputMode("update") \
    .option("checkpointLocation", "/checkpoints/status_tracker") \
    .start()

# Simultaneously write to Delta Lake (for historical analysis)
parsed.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "/checkpoints/delta_scans") \
    .partitionBy("event_date") \
    .start("/delta/scan_events")
```

---

### Q67: Handle duplicate events in streaming

```python
# STRATEGY 1: Stateful deduplication with watermark
deduplicated = (stream
    .withWatermark("event_time", "1 hour")
    .dropDuplicates(["event_id", "event_time"])
)

# STRATEGY 2: Upsert to Delta Lake (natural dedup)
def upsert_to_delta(batch_df, batch_id):
    deltaTable = DeltaTable.forPath(spark, "/delta/events")
    
    deltaTable.alias("t").merge(
        batch_df.alias("s"),
        "t.event_id = s.event_id"
    ).whenMatchedUpdateAll() \
     .whenNotMatchedInsertAll() \
     .execute()

stream.writeStream \
    .foreachBatch(upsert_to_delta) \
    .start()

# STRATEGY 3: Exactly-once with idempotent keys
# Include batch_id in primary key
def idempotent_write(batch_df, batch_id):
    batch_with_id = batch_df.withColumn("batch_id", lit(batch_id))
    # Upsert on (event_id, batch_id)
    upsert(batch_with_id, ["event_id", "batch_id"])
```

---

### Q68: Event time vs processing time

| Concept | Event Time | Processing Time |
|---------|------------|-----------------|
| **Definition** | When event actually occurred | When event is processed |
| **Source** | Embedded in event payload | System clock at processing |
| **Use Case** | Business logic, analytics | Monitoring, debugging |
| **Challenge** | Out-of-order events | Misleading for analysis |

```python
# Event time processing with watermarking
events = (spark.readStream
    .format("kafka").load()
    .selectExpr("CAST(value AS STRING)")
    .select(from_json("value", schema).alias("data"))
    .select(
        col("data.event_id"),
        col("data.event_time").cast("timestamp"),  # Event time from payload
        current_timestamp().alias("processing_time")  # When processed
    )
)

# Aggregate by EVENT TIME (business correct)
hourly_counts = (events
    .withWatermark("event_time", "30 minutes")  # Allow 30 min late data
    .groupBy(window("event_time", "1 hour"))
    .count()
)

# Without watermark = use processing time = skewed results
```

---

### Q69: Late-arriving events handling

```python
# STRATEGY 1: Watermarking (Streaming)
# Accept late events up to 1 hour, then drop
windowed_counts = (stream
    .withWatermark("event_time", "1 hour")
    .groupBy(window("event_time", "10 minutes"))
    .count()
)

# STRATEGY 2: Allowed Lateness Window
# Store late events in separate table for reprocessing
def handle_late_events(batch_df, batch_id):
    cutoff_time = datetime.now() - timedelta(hours=24)
    
    on_time = batch_df.filter(col("event_time") >= cutoff_time)
    late = batch_df.filter(col("event_time") < cutoff_time)
    
    # Process on-time normally
    on_time.write.format("delta").mode("append").save("/delta/events")
    
    # Store late events for batch reprocessing
    if late.count() > 0:
        late.write.format("delta").mode("append").save("/delta/late_events")
        trigger_reprocess_job(late.select("event_date").distinct().collect())

# STRATEGY 3: Lambda Architecture
# Streaming for speed, nightly batch for accuracy (reconciles late data)
```

---

### Q70: Exactly-once vs at-least-once semantics

| Semantic | Guarantee | Implementation | Trade-off |
|----------|-----------|----------------|-----------|
| **At-most-once** | May lose data | No retries | Fast, lossy |
| **At-least-once** | No data loss, may have duplicates | Retry + checkpoint | Reliable, need dedup |
| **Exactly-once** | No loss, no duplicates | Idempotent writes + transactions | Complex, slower |

```python
# At-least-once with downstream deduplication
stream.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "/checkpoints/") \
    .start()
# Delta Lake handles duplicates via MERGE

# Exactly-once end-to-end (Kafka + Delta)
# 1. Kafka consumer: Commit offsets AFTER successful write
# 2. Spark: Checkpoint stores offsets
# 3. Delta: ACID transactions ensure atomic writes

# If processing fails:
# - Checkpoint tells Spark where to resume
# - Delta Lake ensures partial batch is rolled back
# - Kafka offsets haven't advanced (will reprocess)
```

---

## 3️⃣ Reliability & Quality

### Q71: Data validation checks you'd implement

```python
# Comprehensive validation framework
class DataValidator:
    def __init__(self, df, table_name):
        self.df = df
        self.table_name = table_name
        self.errors = []
    
    def check_not_null(self, columns):
        for col in columns:
            null_count = self.df.filter(F.col(col).isNull()).count()
            if null_count > 0:
                self.errors.append(f"NULL values in {col}: {null_count}")
    
    def check_unique(self, columns):
        total = self.df.count()
        distinct = self.df.dropDuplicates(columns).count()
        if total != distinct:
            self.errors.append(f"Duplicates on {columns}: {total - distinct}")
    
    def check_referential_integrity(self, fk_col, ref_table, ref_col):
        orphans = self.df.join(
            spark.table(ref_table),
            self.df[fk_col] == spark.table(ref_table)[ref_col],
            "left_anti"
        ).count()
        if orphans > 0:
            self.errors.append(f"Orphan {fk_col} records: {orphans}")
    
    def check_range(self, column, min_val, max_val):
        out_of_range = self.df.filter(
            (F.col(column) < min_val) | (F.col(column) > max_val)
        ).count()
        if out_of_range > 0:
            self.errors.append(f"{column} out of range [{min_val}, {max_val}]: {out_of_range}")
    
    def check_row_count(self, min_count, max_count):
        count = self.df.count()
        if not (min_count <= count <= max_count):
            self.errors.append(f"Row count {count} outside [{min_count}, {max_count}]")
    
    def validate(self):
        if self.errors:
            raise DataQualityException(self.errors)
        return True

# Usage
validator = DataValidator(shipments_df, "fact_shipments")
validator.check_not_null(["shipment_id", "status"])
validator.check_unique(["shipment_id"])
validator.check_range("weight", 0, 10000)
validator.check_row_count(10000, 10000000)
validator.validate()
```

---

### Q72: Monitoring pipeline health

```python
# Key metrics to track
PIPELINE_METRICS = {
    # Execution metrics
    'run_duration_seconds': 'How long did the pipeline take?',
    'success_rate': 'What % of runs succeed?',
    'retry_count': 'How many retries before success?',
    
    # Data metrics
    'rows_processed': 'How many rows this run?',
    'rows_rejected': 'How many failed validation?',
    'data_freshness_hours': 'How old is the newest data?',
    
    # Quality metrics
    'null_rate': '% of nulls in key columns',
    'duplicate_rate': '% duplicates',
    'dq_score': 'Overall quality score (0-100)',
}

# Emit metrics to monitoring system
def emit_pipeline_metrics(pipeline_name, metrics):
    from datadog import statsd
    
    for metric, value in metrics.items():
        statsd.gauge(
            f'pipeline.{metric}',
            value,
            tags=[f'pipeline:{pipeline_name}', f'env:prod']
        )

# Alert thresholds
ALERTS = {
    'run_duration_seconds': {'threshold': 3600, 'condition': '>'},
    'success_rate': {'threshold': 0.95, 'condition': '<'},
    'data_freshness_hours': {'threshold': 24, 'condition': '>'},
    'dq_score': {'threshold': 95, 'condition': '<'},
}
```

---

### Q73: SLA vs SLO for data pipelines

| Term | Definition | Example |
|------|------------|---------|
| **SLA** (Service Level Agreement) | Contractual commitment with consequences | "Data available by 9 AM or $10K credit" |
| **SLO** (Service Level Objective) | Internal target (no penalty) | "Target 99% on-time completion" |
| **SLI** (Service Level Indicator) | Measured metric | "% of days data ready by 9 AM" |

```yaml
# Example SLO/SLA for daily shipment pipeline
Pipeline: daily_shipment_aggregation

SLI (What we measure):
  - completion_time: Time when gold table is updated
  - data_freshness: Max(event_time) in output
  - quality_score: DQ checks pass rate

SLO (Internal targets):
  - completion_time: 99% of runs complete by 8:00 AM
  - data_freshness: Data should be < 6 hours old
  - quality_score: > 99% pass rate

SLA (Customer commitment):
  - completion_time: Dashboard data updated by 9:00 AM
  - consequence: Revenue loss from stale reporting

Error Budget:
  - Allowed misses per quarter: 1 (99% SLO = 1/90 days)
  - Current: 0 misses this quarter ✅
```

---

### Q74: Alert fatigue — how to avoid?

```yaml
# STRATEGIES TO PREVENT ALERT FATIGUE

1. TIERED ALERTING
   Critical (Page): Pipeline failure, SLA breach
   Warning (Slack): Degraded performance, anomaly detected
   Info (Dashboard): Metrics out of normal range

2. AGGREGATE ALERTS
   ❌ Bad: Alert for every failed record
   ✅ Good: Alert when failure rate > 1%

3. SMART THRESHOLDS
   ❌ Static: Alert if duration > 60 min
   ✅ Dynamic: Alert if duration > 2x rolling average

4. ROOT CAUSE GROUPING
   ❌ 50 alerts for 50 downstream pipelines (all caused by 1 source failure)
   ✅ 1 alert for source failure + note about downstream impact

5. MAINTENANCE WINDOWS
   Suppress alerts during planned maintenance

6. ESCALATION POLICIES
   - Alert → Auto-retry → Still failing → Page on-call
   - Not: Alert immediately → On-call wakes up for transient issue
```

```python
# Smart alerting implementation
def should_alert(metric, current_value, historical_values):
    # Calculate dynamic threshold (mean + 2 std)
    mean = statistics.mean(historical_values)
    std = statistics.stdev(historical_values)
    threshold = mean + 2 * std
    
    # Only alert if sustained (3 consecutive breaches)
    recent_breaches = count_recent_breaches(metric, threshold, window=3)
    
    return current_value > threshold and recent_breaches >= 3
```

---

### Q75: Root cause analysis of data mismatch

```markdown
# RCA FRAMEWORK: 5 Whys + Data Lineage

## Step 1: Identify the Discrepancy
- Dashboard shows: 10,000 shipments
- Source system shows: 10,500 shipments
- Gap: 500 shipments (5%)

## Step 2: Trace Data Lineage
Source → Bronze → Silver → Gold → Dashboard
  ↓
Check counts at each stage:
- Source: 10,500 ✓
- Bronze: 10,500 ✓
- Silver: 10,200 ← Drop here!
- Gold: 10,200
- Dashboard: 10,200 (UI rounds to 10,000)

## Step 3: Investigate Silver Transform
- Filter condition: status != 'CANCELLED'
- 300 records have status = NULL (treated as != 'CANCELLED', but excluded elsewhere)
- Missing 200: schema mismatch, new status value 'TEST_CANCELLED'

## Step 4: 5 Whys
1. Why mismatch? Silver has fewer records
2. Why fewer? Filter excludes records
3. Why excluded? NULL status and new status value
4. Why NULL? Source system bug
5. Why new value? Upstream team added without communication

## Step 5: Resolution
- Short-term: Add 'TEST_CANCELLED' to exclusion list
- Long-term: Schema registry, contract testing
```
