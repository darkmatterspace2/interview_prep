# ETL / Data Pipeline Design Interview Questions & Answers (Question Bank 1)

> **Amazon Data Engineer Style** - Batch, Streaming, and Reliability Focus

---

<a id="index"></a>
## 📑 Table of Contents

| Section | Topics |
|---------|--------|
| [1️⃣ Batch Pipelines](#1️⃣-batch-pipelines) | Aggregation, Idempotency, Backfill |
| &nbsp;&nbsp;&nbsp;└ [Q61: Daily shipment aggregation](#q61-design-a-daily-shipment-aggregation-pipeline) | Pipeline design |
| &nbsp;&nbsp;&nbsp;└ [Q62: Idempotent pipeline](#q62-idempotent-pipeline--explain-with-example) | Patterns & anti-patterns |
| &nbsp;&nbsp;&nbsp;└ [Q63: Backfill last 30 days](#q63-backfill-last-30-days-of-data) | Safe backfill |
| &nbsp;&nbsp;&nbsp;└ [Q64: Partial failure handling](#q64-handle-partial-pipeline-failures) | Checkpoints |
| &nbsp;&nbsp;&nbsp;└ [Q65: Reprocess corrupted data](#q65-reprocess-corrupted-data-safely) | Safe reprocessing |
| [2️⃣ Streaming / Near Real-Time](#2️⃣-streaming--near-real-time) | Status tracking, Duplicates |
| &nbsp;&nbsp;&nbsp;└ [Q66: Real-time status tracking](#q66-design-real-time-shipment-status-tracking) | Architecture |
| &nbsp;&nbsp;&nbsp;└ [Q67: Duplicate events handling](#q67-handle-duplicate-events-in-streaming) | Dedup strategies |
| &nbsp;&nbsp;&nbsp;└ [Q68: Event time vs processing time](#q68-event-time-vs-processing-time) | Watermarking |
| &nbsp;&nbsp;&nbsp;└ [Q69: Late-arriving events](#q69-late-arriving-events-handling) | Handling strategies |
| &nbsp;&nbsp;&nbsp;└ [Q70: Exactly-once vs at-least-once](#q70-exactly-once-vs-at-least-once-semantics) | Semantics |
| [3️⃣ Reliability & Quality](#3️⃣-reliability--quality) | Validation, Monitoring, SLAs |
| &nbsp;&nbsp;&nbsp;└ [Q71: Data validation checks](#q71-data-validation-checks-youd-implement) | Validation framework |
| &nbsp;&nbsp;&nbsp;└ [Q72: Pipeline health monitoring](#q72-monitoring-pipeline-health) | Metrics & alerts |
| &nbsp;&nbsp;&nbsp;└ [Q73: SLA vs SLO](#q73-sla-vs-slo-for-data-pipelines) | Definitions |
| &nbsp;&nbsp;&nbsp;└ [Q74: Alert fatigue](#q74-alert-fatigue--how-to-avoid) | Smart alerting |
| &nbsp;&nbsp;&nbsp;└ [Q75: Root cause analysis](#q75-root-cause-analysis-of-data-mismatch) | RCA framework |

---

<a id="1️⃣-batch-pipelines"></a>
## 1️⃣ Batch Pipelines [↩️](#index)

<a id="q61-design-a-daily-shipment-aggregation-pipeline"></a>
### Q61: Design a daily shipment aggregation pipeline [↩️](#index)

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

extract >> transform >> aggregate
```

---

<a id="q62-idempotent-pipeline--explain-with-example"></a>
### Q62: Idempotent pipeline — explain with example [↩️](#index)

**Definition:** Running the pipeline N times produces the same result as running it once.

**Why It Matters:**
- Retries after failure don't corrupt data
- Backfills are safe
- Debugging is reproducible

```python
# ✅ PATTERN 1: Partition Overwrite (Idempotent)
df.write \
    .mode('overwrite') \
    .partitionBy('date') \
    .option('replaceWhere', f"date = '{processing_date}'") \
    .format('delta') \
    .save('/gold/metrics/')

# ✅ PATTERN 2: MERGE/Upsert (Idempotent)
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

<a id="q63-backfill-last-30-days-of-data"></a>
### Q63: Backfill last 30 days of data [↩️](#index)

```python
def backfill_date_range(start_date, end_date):
    """
    Backfill guarantees:
    1. Each date processed independently (idempotent)
    2. Production SLA unaffected (separate cluster)
    3. Failures don't block subsequent dates
    """
    current = start_date
    results = []
    
    while current <= end_date:
        try:
            process_date(current)
            results.append({'date': current, 'status': 'SUCCESS'})
        except Exception as e:
            results.append({'date': current, 'status': 'FAILED', 'error': str(e)})
            # Continue to next date, don't stop
        
        current += timedelta(days=1)
    
    return results

# Airflow: airflow dags backfill -s 2024-01-01 -e 2024-01-30 daily_shipment_aggregation
```

---

<a id="q64-handle-partial-pipeline-failures"></a>
### Q64: Handle partial pipeline failures [↩️](#index)

```python
# Checkpoint pattern for multi-stage pipelines
def run_pipeline_with_checkpoints(date):
    checkpoints = load_checkpoints(date)
    
    stages = [
        ('extract', extract_from_source),
        ('clean', clean_and_validate),
        ('transform', apply_business_logic),
        ('load', load_to_warehouse),
    ]
    
    for stage_name, stage_func in stages:
        if checkpoints.get(stage_name) == 'COMPLETED':
            print(f"Skipping {stage_name} (already done)")
            continue
        
        try:
            save_checkpoint(date, stage_name, 'IN_PROGRESS')
            stage_func(date)
            save_checkpoint(date, stage_name, 'COMPLETED')
        except Exception as e:
            save_checkpoint(date, stage_name, 'FAILED', error=str(e))
            raise
```

---

<a id="q65-reprocess-corrupted-data-safely"></a>
### Q65: Reprocess corrupted data safely [↩️](#index)

```python
def reprocess_corrupted_data(table, start_date, end_date, corruption_type):
    # 1. BACKUP current data
    backup_path = f"/backup/{table}/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # 2. ISOLATE: Process to staging
    for date in date_range(start_date, end_date):
        source_df = spark.read.parquet(f'/silver/{table}/date={date}')
        
        if corruption_type == 'DUPLICATES':
            fixed_df = source_df.dropDuplicates(['shipment_id'])
        elif corruption_type == 'NULL_VALUES':
            fixed_df = source_df.fillna({'status': 'UNKNOWN'})
        
        fixed_df.write.mode('overwrite').parquet(f'{staging_path}/date={date}')
    
    # 3. VALIDATE staging vs backup
    # 4. SWAP: Atomic replacement
    # 5. CLEANUP: Remove staging, schedule backup deletion
```

---

<a id="2️⃣-streaming--near-real-time"></a>
## 2️⃣ Streaming / Near Real-Time [↩️](#index)

<a id="q66-design-real-time-shipment-status-tracking"></a>
### Q66: Design real-time shipment status tracking [↩️](#index)

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
                                 └───────────────┘
```

```python
# Spark Structured Streaming implementation
scans_stream = (spark.readStream
    .format("kafka")
    .option("subscribe", "shipment_scans")
    .load()
)

# Business logic: Get latest status per shipment
latest_status = (parsed
    .withWatermark("event_time", "10 minutes")
    .groupBy(window("event_time", "5 minutes"), "shipment_id")
    .agg(last("status").alias("current_status"))
)

# Write to Redis for real-time serving
latest_status.writeStream \
    .foreachBatch(write_to_redis) \
    .option("checkpointLocation", "/checkpoints/status_tracker") \
    .start()
```

---

<a id="q67-handle-duplicate-events-in-streaming"></a>
### Q67: Handle duplicate events in streaming [↩️](#index)

```python
# STRATEGY 1: Stateful deduplication with watermark
deduplicated = (stream
    .withWatermark("event_time", "1 hour")
    .dropDuplicates(["event_id", "event_time"])
)

# STRATEGY 2: Upsert to Delta Lake (natural dedup)
def upsert_to_delta(batch_df, batch_id):
    deltaTable.alias("t").merge(
        batch_df.alias("s"),
        "t.event_id = s.event_id"
    ).whenMatchedUpdateAll() \
     .whenNotMatchedInsertAll() \
     .execute()

# STRATEGY 3: Exactly-once with idempotent keys
```

---

<a id="q68-event-time-vs-processing-time"></a>
### Q68: Event time vs processing time [↩️](#index)

| Concept | Event Time | Processing Time |
|---------|------------|-----------------|
| **Definition** | When event actually occurred | When event is processed |
| **Source** | Embedded in event payload | System clock at processing |
| **Use Case** | Business logic, analytics | Monitoring, debugging |
| **Challenge** | Out-of-order events | Misleading for analysis |

```python
# Aggregate by EVENT TIME (business correct)
hourly_counts = (events
    .withWatermark("event_time", "30 minutes")  # Allow 30 min late data
    .groupBy(window("event_time", "1 hour"))
    .count()
)
```

---

<a id="q69-late-arriving-events-handling"></a>
### Q69: Late-arriving events handling [↩️](#index)

```python
# STRATEGY 1: Watermarking (Streaming)
windowed_counts = (stream
    .withWatermark("event_time", "1 hour")
    .groupBy(window("event_time", "10 minutes"))
    .count()
)

# STRATEGY 2: Separate late events for batch reprocessing
def handle_late_events(batch_df, batch_id):
    cutoff_time = datetime.now() - timedelta(hours=24)
    on_time = batch_df.filter(col("event_time") >= cutoff_time)
    late = batch_df.filter(col("event_time") < cutoff_time)
    
    on_time.write.format("delta").mode("append").save("/delta/events")
    if late.count() > 0:
        late.write.format("delta").mode("append").save("/delta/late_events")
```

---

<a id="q70-exactly-once-vs-at-least-once-semantics"></a>
### Q70: Exactly-once vs at-least-once semantics [↩️](#index)

| Semantic | Guarantee | Implementation | Trade-off |
|----------|-----------|----------------|-----------|
| **At-most-once** | May lose data | No retries | Fast, lossy |
| **At-least-once** | No data loss, may have duplicates | Retry + checkpoint | Reliable, need dedup |
| **Exactly-once** | No loss, no duplicates | Idempotent writes + transactions | Complex, slower |

```python
# Exactly-once end-to-end (Kafka + Delta)
stream.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "/checkpoints/") \
    .start()
```

---

<a id="3️⃣-reliability--quality"></a>
## 3️⃣ Reliability & Quality [↩️](#index)

<a id="q71-data-validation-checks-youd-implement"></a>
### Q71: Data validation checks you'd implement [↩️](#index)

```python
class DataValidator:
    def __init__(self, df, table_name):
        self.df = df
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
    
    def validate(self):
        if self.errors:
            raise DataQualityException(self.errors)
        return True
```

---

<a id="q72-monitoring-pipeline-health"></a>
### Q72: Monitoring pipeline health [↩️](#index)

```python
PIPELINE_METRICS = {
    'run_duration_seconds': 'How long did the pipeline take?',
    'success_rate': 'What % of runs succeed?',
    'rows_processed': 'How many rows this run?',
    'data_freshness_hours': 'How old is the newest data?',
    'dq_score': 'Overall quality score (0-100)',
}

ALERTS = {
    'run_duration_seconds': {'threshold': 3600, 'condition': '>'},
    'success_rate': {'threshold': 0.95, 'condition': '<'},
    'data_freshness_hours': {'threshold': 24, 'condition': '>'},
}
```

---

<a id="q73-sla-vs-slo-for-data-pipelines"></a>
### Q73: SLA vs SLO for data pipelines [↩️](#index)

| Term | Definition | Example |
|------|------------|---------|
| **SLA** (Agreement) | Contractual commitment with consequences | "Data by 9 AM or $10K credit" |
| **SLO** (Objective) | Internal target (no penalty) | "Target 99% on-time" |
| **SLI** (Indicator) | Measured metric | "% of days data ready by 9 AM" |

---

<a id="q74-alert-fatigue--how-to-avoid"></a>
### Q74: Alert fatigue — how to avoid? [↩️](#index)

```yaml
STRATEGIES TO PREVENT ALERT FATIGUE:

1. TIERED ALERTING
   Critical (Page): Pipeline failure, SLA breach
   Warning (Slack): Degraded performance
   Info (Dashboard): Metrics out of range

2. AGGREGATE ALERTS
   ❌ Bad: Alert for every failed record
   ✅ Good: Alert when failure rate > 1%

3. SMART THRESHOLDS
   ❌ Static: Alert if duration > 60 min
   ✅ Dynamic: Alert if duration > 2x rolling average

4. ROOT CAUSE GROUPING
   ❌ 50 alerts for 50 downstream pipelines
   ✅ 1 alert for source failure + downstream impact
```

---

<a id="q75-root-cause-analysis-of-data-mismatch"></a>
### Q75: Root cause analysis of data mismatch [↩️](#index)

```markdown
# RCA FRAMEWORK: 5 Whys + Data Lineage

## Step 1: Identify the Discrepancy
- Dashboard shows: 10,000 shipments
- Source system shows: 10,500 shipments
- Gap: 500 shipments (5%)

## Step 2: Trace Data Lineage
Source → Bronze → Silver → Gold → Dashboard
Check counts at each stage to find the drop

## Step 3: 5 Whys
1. Why mismatch? Silver has fewer records
2. Why fewer? Filter excludes records
3. Why excluded? NULL status and new status value
4. Why NULL? Source system bug
5. Why new value? Upstream team added without communication

## Step 4: Resolution
- Short-term: Add new status to exclusion list
- Long-term: Schema registry, contract testing
```
