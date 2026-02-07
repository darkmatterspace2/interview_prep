# Data Quality & Pipeline Reliability Framework

> **Interview Focus:** Implementing production-grade data quality checks, monitoring, alerting, and ensuring pipeline reliability through idempotency, automated incident management, and observability.

---

## 📌 Two Pillars of Reliable Data Pipelines

| Pillar | Focus | Key Questions |
|--------|-------|---------------|
| **Pipeline Reliability** | Is the pipeline running correctly? | Did it complete? Did it retry successfully? Is it idempotent? |
| **Data Quality** | Is the data correct? | Is it complete? Fresh? Accurate? Schema-compliant? |

> **Interview Insight:** "Pipeline success ≠ Data quality. A pipeline can complete successfully but write garbage data. We need both reliability monitoring AND data quality validation."

---

## 🔧 Part 1: Pipeline Reliability

### 1.1 Idempotency: The Foundation

**Definition:** Running a pipeline N times produces the same result as running it once.

#### Why Idempotency Matters

| Scenario | Without Idempotency | With Idempotency |
|----------|--------------------| -----------------|
| Retry after failure | Duplicate records | Clean recovery |
| Backfill | Data corruption | Safe reprocessing |
| Debugging | Unpredictable state | Reproducible results |
| Concurrent runs | Race conditions | Conflict-free |

#### Idempotency Patterns

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      IDEMPOTENCY PATTERNS                                    │
└─────────────────────────────────────────────────────────────────────────────┘

PATTERN 1: PARTITION OVERWRITE (Most Common)
────────────────────────────────────────────
• Write to date partition
• Rerun = overwrite same partition
• Downstream sees clean data

   Run 1: /data/sales/date=2024-02-07/ → 1000 records
   Run 2: /data/sales/date=2024-02-07/ → 1000 records (overwrites)

PATTERN 2: UPSERT / MERGE (Delta Lake, Iceberg)
───────────────────────────────────────────────
• Match on primary key
• Update if exists, insert if new
• No duplicates ever

   MERGE INTO target USING source
   ON target.id = source.id
   WHEN MATCHED THEN UPDATE SET *
   WHEN NOT MATCHED THEN INSERT *

PATTERN 3: DEDUPLICATION STATE STORE
────────────────────────────────────
• Track processed IDs in separate table
• Skip already-processed records
• Works for streaming

   processed_ids = SELECT id FROM checkpoint_table
   new_records = source.filter(NOT IN processed_ids)
   INSERT INTO checkpoint_table SELECT id FROM new_records

PATTERN 4: ATOMIC SWAP (Blue-Green)
───────────────────────────────────
• Write to temp location
• Validate
• Atomic rename/swap
• Rollback if failed

   Write → /data/sales_temp/
   Validate → count, schema
   Swap → RENAME sales_temp TO sales
```

#### Idempotency Implementation (Spark + Delta)

```python
# ✅ IDEMPOTENT: Partition overwrite
df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("replaceWhere", f"date = '{processing_date}'") \
    .save("s3://bucket/sales/")

# ✅ IDEMPOTENT: MERGE/Upsert
from delta.tables import DeltaTable

target = DeltaTable.forPath(spark, "s3://bucket/sales/")
target.alias("t") \
    .merge(
        source_df.alias("s"),
        "t.id = s.id"
    ) \
    .whenMatchedUpdateAll() \
    .whenNotMatchedInsertAll() \
    .execute()

# ❌ NOT IDEMPOTENT: Append mode
df.write.mode("append").save("...")  # Reruns create duplicates!
```

### 1.2 Automatic Incident Management (ServiceNow Integration)

#### Alert → Ticket Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AUTOMATED INCIDENT WORKFLOW                               │
└─────────────────────────────────────────────────────────────────────────────┘

    Pipeline Failure
          │
          ▼
┌──────────────────────┐
│  Airflow Task Fail   │
│  or                  │
│  Databricks Job Fail │
└──────────────────────┘
          │
          ▼
┌──────────────────────┐     ┌────────────────────────────────────────────────┐
│  Webhook Trigger     │────▶│  Event Enrichment                              │
│  (HTTP POST)         │     │  • Pipeline name, run_id                       │
└──────────────────────┘     │  • Error message, stack trace                  │
                             │  • Owner team (from metadata)                  │
                             │  • Severity (Critical/High/Medium/Low)         │
                             │  • Runbook link                                │
                             └────────────────────────────────────────────────┘
                                              │
          ┌───────────────────────────────────┼──────────────────────────────┐
          ▼                                   ▼                              ▼
┌──────────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│  ServiceNow Incident │     │  PagerDuty Alert     │     │  Slack Notification │
│  INC0012345          │     │  (On-call rotation)  │     │  #data-alerts       │
└──────────────────────┘     └──────────────────────┘     └─────────────────────┘
          │
          ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  ServiceNow Incident Details:                                                │
│  ────────────────────────────                                                │
│  Short Description: [CRITICAL] Pipeline: sales_daily failed                 │
│  Urgency: High                                                               │
│  Impact: Business-critical data delayed                                     │
│  Assignment Group: Data Engineering                                          │
│  CI: sales_pipeline                                                         │
│  Runbook: https://wiki/runbooks/sales_daily                                 │
│  Error Log: Spark OOM on executor 5                                         │
│  Suggested Action: Increase spark.executor.memory to 8g                     │
└──────────────────────────────────────────────────────────────────────────────┘
```

#### ServiceNow Integration Code (Airflow Example)

```python
# dags/utils/servicenow_integration.py
import requests
from airflow.hooks.base import BaseHook

class ServiceNowClient:
    def __init__(self):
        conn = BaseHook.get_connection("servicenow")
        self.base_url = conn.host
        self.auth = (conn.login, conn.password)
    
    def create_incident(self, pipeline_name, error_message, severity, runbook_url):
        payload = {
            "short_description": f"[{severity}] Pipeline: {pipeline_name} failed",
            "description": f"""
                Pipeline: {pipeline_name}
                Error: {error_message}
                Runbook: {runbook_url}
                Time: {datetime.now().isoformat()}
            """,
            "urgency": self._map_urgency(severity),
            "impact": self._map_impact(severity),
            "assignment_group": "Data Engineering",
            "category": "Data Pipeline",
            "cmdb_ci": pipeline_name,
        }
        
        response = requests.post(
            f"{self.base_url}/api/now/table/incident",
            json=payload,
            auth=self.auth
        )
        return response.json()["result"]["number"]  # INC0012345
    
    def _map_urgency(self, severity):
        return {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "LOW": 4}[severity]

# Usage in Airflow DAG
def on_failure_callback(context):
    client = ServiceNowClient()
    ticket = client.create_incident(
        pipeline_name=context["dag"].dag_id,
        error_message=str(context["exception"]),
        severity="CRITICAL" if "production" in context["dag"].dag_id else "MEDIUM",
        runbook_url=context["dag"].doc_md
    )
    # Also send to Slack
    send_slack_alert(f"🚨 Pipeline failed. ServiceNow: {ticket}")

# In DAG definition
default_args = {
    "on_failure_callback": on_failure_callback,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}
```

### 1.3 Retry & Recovery Strategies

| Strategy | When to Use | Implementation |
|----------|-------------|----------------|
| **Exponential Backoff** | Transient failures (API, network) | Retry at 1, 2, 4, 8 minutes |
| **Fixed Retry** | Known intermittent issues | Retry 3 times, 5 min apart |
| **Dead Letter Queue** | Streaming, partial failure tolerance | Park bad records, continue |
| **Circuit Breaker** | Downstream dependency down | Stop retrying, alert, manual reset |
| **Checkpoint Recovery** | Long-running jobs | Resume from last checkpoint |

```python
# Exponential Backoff (Airflow)
default_args = {
    "retries": 5,
    "retry_delay": timedelta(minutes=1),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=30),
}

# Dead Letter Queue (Spark Streaming)
df.writeStream \
    .foreachBatch(lambda batch, id: process_with_dlq(batch, id)) \
    .option("checkpointLocation", "/checkpoints/") \
    .start()

def process_with_dlq(batch, batch_id):
    try:
        valid_records = batch.filter(validate_schema)
        valid_records.write.format("delta").save("/output/")
    except Exception as e:
        batch.write.format("delta").save("/dlq/")  # Dead Letter Queue
        log_error(batch_id, e)
```

### 1.4 Pipeline Health Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| **Success Rate** | % of runs that completed | < 95% over 24 hours |
| **Duration** | Run time | > 2x historical median |
| **SLA Breach** | Completed after deadline | Any breach |
| **Retry Rate** | Successful after retry / total | > 20% |
| **Backlog** | Pending runs in queue | > 5 runs |
| **Resource Usage** | CPU, Memory peak | > 90% sustained |

---

## ✅ Part 2: Data Quality Framework

### 2.1 Data Quality Dimensions (DAMA-DMBOK Standard)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       DATA QUALITY DIMENSIONS                                │
└─────────────────────────────────────────────────────────────────────────────┘

COMPLETENESS   │ Are all required fields populated?
               │ • Null rate < 1% for required fields
               │ • Row count within expected range
───────────────┼──────────────────────────────────────────────────────────────
UNIQUENESS     │ Are there no duplicates?
               │ • Primary key uniqueness: 100%
               │ • Business key uniqueness within partition
───────────────┼──────────────────────────────────────────────────────────────
VALIDITY       │ Do values conform to expected formats/ranges?
               │ • Email format: ^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$
               │ • Age: 0-120, Amount: > 0
───────────────┼──────────────────────────────────────────────────────────────
ACCURACY       │ Does data reflect ground truth?
               │ • Cross-reference with source systems
               │ • Reconciliation checks
───────────────┼──────────────────────────────────────────────────────────────
CONSISTENCY    │ Are related data elements aligned?
               │ • Total = Sum of parts
               │ • Foreign key integrity
───────────────┼──────────────────────────────────────────────────────────────
TIMELINESS     │ Is data available when expected?
               │ • Data freshness < SLA threshold
               │ • No stale partitions
```

### 2.2 Essential Data Quality Checks

#### Check 1: Primary Key Duplicate Check

```python
# Great Expectations
from great_expectations.core import ExpectationConfiguration

ExpectationConfiguration(
    expectation_type="expect_column_values_to_be_unique",
    kwargs={"column": "order_id"}
)

# SQL-based check
def check_pk_duplicates(spark, table, pk_columns):
    pk_cols = ", ".join(pk_columns)
    result = spark.sql(f"""
        SELECT {pk_cols}, COUNT(*) as cnt
        FROM {table}
        GROUP BY {pk_cols}
        HAVING COUNT(*) > 1
    """)
    
    if result.count() > 0:
        raise DataQualityException(
            f"Duplicate primary keys found: {result.collect()[:10]}"
        )

# PySpark
def assert_no_duplicates(df, pk_columns):
    total = df.count()
    distinct = df.dropDuplicates(pk_columns).count()
    if total != distinct:
        raise DataQualityException(
            f"Duplicates detected: {total - distinct} duplicate rows on {pk_columns}"
        )
```

#### Check 2: Freshness Check

```python
# Check data is recent enough
def check_freshness(spark, table, timestamp_col, max_age_hours=24):
    result = spark.sql(f"""
        SELECT MAX({timestamp_col}) as latest_ts
        FROM {table}
    """).collect()[0]
    
    latest = result.latest_ts
    threshold = datetime.now() - timedelta(hours=max_age_hours)
    
    if latest < threshold:
        raise DataQualityException(
            f"Data is stale. Latest: {latest}, Threshold: {threshold}"
        )

# Partition freshness check
def check_partition_freshness(spark, table, expected_partitions):
    """Ensure expected date partitions exist"""
    existing = spark.sql(f"SHOW PARTITIONS {table}").collect()
    existing_dates = {row[0].split("=")[1] for row in existing}
    
    missing = set(expected_partitions) - existing_dates
    if missing:
        raise DataQualityException(
            f"Missing partitions: {missing}"
        )
```

#### Check 3: Count Estimate Checks (Volume Anomaly Detection)

```python
# Statistical volume check
def check_row_count_anomaly(spark, table, partition_col, partition_value):
    # Get historical baseline (last 30 days)
    historical = spark.sql(f"""
        SELECT AVG(cnt) as avg_count, STDDEV(cnt) as std_count
        FROM (
            SELECT {partition_col}, COUNT(*) as cnt
            FROM {table}
            WHERE {partition_col} >= date_sub(current_date(), 30)
            GROUP BY {partition_col}
        )
    """).collect()[0]
    
    # Get current count
    current = spark.sql(f"""
        SELECT COUNT(*) as cnt
        FROM {table}
        WHERE {partition_col} = '{partition_value}'
    """).collect()[0].cnt
    
    # Z-score check (> 3 std deviations = anomaly)
    z_score = (current - historical.avg_count) / historical.std_count
    
    if abs(z_score) > 3:
        raise DataQualityException(
            f"Row count anomaly detected. Current: {current}, "
            f"Expected: {historical.avg_count} ± {historical.std_count * 3}"
        )

# Simple bounds check
def check_row_count_bounds(df, min_count, max_count):
    count = df.count()
    if not (min_count <= count <= max_count):
        raise DataQualityException(
            f"Row count {count} outside bounds [{min_count}, {max_count}]"
        )
```

#### Check 4: Schema Validation

```python
# Schema drift detection
def check_schema(df, expected_schema):
    """Validate schema matches expected structure"""
    current_cols = set(df.columns)
    expected_cols = set(expected_schema.keys())
    
    # Check for missing columns
    missing = expected_cols - current_cols
    if missing:
        raise DataQualityException(f"Missing columns: {missing}")
    
    # Check for unexpected columns
    extra = current_cols - expected_cols
    if extra:
        log.warning(f"Unexpected columns (may indicate drift): {extra}")
    
    # Check data types
    for col, expected_type in expected_schema.items():
        actual_type = dict(df.dtypes).get(col)
        if actual_type != expected_type:
            raise DataQualityException(
                f"Type mismatch for {col}: expected {expected_type}, got {actual_type}"
            )
```

#### Check 5: Referential Integrity

```python
# Foreign key check
def check_referential_integrity(spark, fact_table, dim_table, fk_col, pk_col):
    orphans = spark.sql(f"""
        SELECT f.{fk_col}
        FROM {fact_table} f
        LEFT JOIN {dim_table} d ON f.{fk_col} = d.{pk_col}
        WHERE d.{pk_col} IS NULL
          AND f.{fk_col} IS NOT NULL
    """)
    
    orphan_count = orphans.count()
    if orphan_count > 0:
        raise DataQualityException(
            f"Referential integrity violation: {orphan_count} orphan records"
        )
```

#### Check 6: Business Rule Validation

```python
# Domain-specific rules
def check_business_rules(df):
    checks = [
        # Amount should be positive
        (df.filter("amount <= 0").count() == 0, "Negative amounts found"),
        # Order date should not be in future
        (df.filter("order_date > current_date()").count() == 0, "Future dates found"),
        # Status should be in allowed values
        (df.filter("status NOT IN ('pending','completed','cancelled')").count() == 0, 
         "Invalid status values"),
        # If status = completed, completion_date must exist
        (df.filter("status = 'completed' AND completion_date IS NULL").count() == 0,
         "Completed orders without completion date"),
    ]
    
    for passed, message in checks:
        if not passed:
            raise DataQualityException(f"Business rule violation: {message}")
```

### 2.3 Data Quality Framework Implementation

#### Great Expectations Integration

```python
# great_expectations/expectations/sales_expectations.py
from great_expectations.core import ExpectationSuite

suite = ExpectationSuite("sales_data_quality")

# Completeness
suite.add_expectation(expect_column_to_exist("order_id"))
suite.add_expectation(expect_column_to_exist("customer_id"))
suite.add_expectation(expect_column_values_to_not_be_null("order_id"))
suite.add_expectation(expect_column_values_to_not_be_null("order_date"))

# Uniqueness
suite.add_expectation(expect_column_values_to_be_unique("order_id"))
suite.add_expectation(expect_compound_columns_to_be_unique(["order_id", "line_item"]))

# Validity
suite.add_expectation(expect_column_values_to_be_between("amount", 0, 1000000))
suite.add_expectation(expect_column_values_to_match_regex(
    "email", r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"
))
suite.add_expectation(expect_column_values_to_be_in_set(
    "status", ["pending", "completed", "cancelled"]
))

# Volume
suite.add_expectation(expect_table_row_count_to_be_between(10000, 1000000))

# Freshness
suite.add_expectation(expect_column_max_to_be_between(
    "order_date", 
    min_value=date.today() - timedelta(days=1),
    max_value=date.today()
))
```

```python
# Running validation in pipeline
from great_expectations.data_context import DataContext

def validate_data(df, expectation_suite_name):
    context = DataContext("/great_expectations/")
    
    # Convert Spark DF to GE datasource
    batch = context.get_batch({
        "datasource": "spark_datasource",
        "data_asset_name": "sales_data",
        "spark_df": df
    })
    
    results = context.run_validation_operator(
        "action_list_operator",
        assets_to_validate=[batch],
        run_id=f"pipeline_{datetime.now().isoformat()}"
    )
    
    if not results["success"]:
        failed_expectations = [
            r for r in results["validation_results"] 
            if not r["success"]
        ]
        raise DataQualityException(
            f"Data quality validation failed: {failed_expectations}"
        )
    
    return True
```

### 2.4 Data Quality Metrics & Scoring

```python
# Calculate DQ score per dimension
def calculate_dq_score(df, checks):
    """
    Returns a 0-100 score based on check results
    """
    results = {}
    
    # Completeness score (% non-null)
    null_rates = df.select([
        (1 - (F.sum(F.col(c).isNull().cast("int")) / F.count("*"))).alias(c)
        for c in df.columns
    ]).collect()[0]
    results["completeness"] = sum(null_rates) / len(null_rates) * 100
    
    # Uniqueness score (% unique on PK)
    total = df.count()
    distinct = df.dropDuplicates(["id"]).count()
    results["uniqueness"] = (distinct / total) * 100
    
    # Validity score (% passing rules)
    valid_count = df.filter(
        (F.col("amount") > 0) & 
        (F.col("status").isin(["pending", "completed"]))
    ).count()
    results["validity"] = (valid_count / total) * 100
    
    # Freshness score (1 if fresh, 0 if stale)
    latest_date = df.agg(F.max("event_date")).collect()[0][0]
    is_fresh = (date.today() - latest_date).days <= 1
    results["freshness"] = 100 if is_fresh else 0
    
    # Weighted average
    weights = {"completeness": 0.3, "uniqueness": 0.3, "validity": 0.3, "freshness": 0.1}
    overall_score = sum(results[k] * weights[k] for k in results)
    
    return {"dimensions": results, "overall": overall_score}
```

---

## 📊 Part 3: Monitoring & Alerting

### 3.1 Observability Stack Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DATA PIPELINE OBSERVABILITY                           │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────────┐
                    │         DATA PIPELINES               │
                    │  (Airflow, Databricks, Spark)       │
                    └─────────────────────────────────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         │                          │                          │
         ▼                          ▼                          ▼
┌─────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│     METRICS     │     │       LOGS          │     │      TRACES         │
│  ─────────────  │     │  ─────────────────  │     │  ─────────────────  │
│  StatsD/        │     │  Fluentd/           │     │  OpenTelemetry      │
│  Prometheus     │     │  Filebeat           │     │  Jaeger             │
└─────────────────┘     └─────────────────────┘     └─────────────────────┘
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATADOG / GRAFANA                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  DASHBOARDS                                                          │   │
│  │  • Pipeline status (running, failed, succeeded)                     │   │
│  │  • Data freshness by table                                          │   │
│  │  • DQ scores trend                                                   │   │
│  │  • SLA compliance %                                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ALERTS                                                              │   │
│  │  • Pipeline failure → PagerDuty                                     │   │
│  │  • DQ score < 95 → Slack                                            │   │
│  │  • SLA breach → ServiceNow                                          │   │
│  │  • Anomaly detected → On-call                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Grafana Dashboard Design

#### Essential Panels

| Panel | Visualization | Query Example (PromQL/InfluxQL) |
|-------|---------------|--------------------------------|
| **Pipeline Status** | Stat (green/red) | `pipeline_status{name="sales_daily"}` |
| **Run Duration Trend** | Time series | `avg(pipeline_duration_seconds) by (pipeline)` |
| **Daily Success Rate** | Gauge | `sum(pipeline_success) / sum(pipeline_runs) * 100` |
| **SLA Compliance** | Bar chart | `sla_breach_count by (pipeline)` |
| **DQ Score Trend** | Time series | `dq_score{table="sales"} over 7d` |
| **Freshness Heatmap** | Heatmap | `data_age_hours by (table)` |
| **Alert History** | Table | `sum(alerts) by (severity, pipeline)` |

#### Sample Grafana Dashboard JSON

```json
{
  "dashboard": {
    "title": "Data Pipeline Health",
    "panels": [
      {
        "title": "Pipeline Status Overview",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(pipeline_status == 1)",
            "legendFormat": "Running"
          },
          {
            "expr": "sum(pipeline_status == 2)",
            "legendFormat": "Success"
          },
          {
            "expr": "sum(pipeline_status == 0)",
            "legendFormat": "Failed"
          }
        ]
      },
      {
        "title": "Data Freshness by Table",
        "type": "table",
        "targets": [
          {
            "expr": "data_freshness_hours",
            "format": "table"
          }
        ],
        "fieldConfig": {
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {"value": 1, "color": "green"},
              {"value": 6, "color": "yellow"},
              {"value": 24, "color": "red"}
            ]
          }
        }
      },
      {
        "title": "DQ Score Trend",
        "type": "timeseries",
        "targets": [
          {
            "expr": "dq_overall_score{table=~\"$table\"}",
            "legendFormat": "{{table}}"
          }
        ]
      }
    ]
  }
}
```

### 3.3 Datadog Integration

```python
# datadog_metrics.py
from datadog import initialize, statsd

initialize(api_key="xxx", app_key="yyy")

class PipelineMetrics:
    @staticmethod
    def record_pipeline_run(pipeline_name, status, duration_seconds):
        tags = [f"pipeline:{pipeline_name}", f"status:{status}"]
        
        # Increment counter
        statsd.increment("pipeline.runs", tags=tags)
        
        # Record duration
        statsd.histogram("pipeline.duration", duration_seconds, tags=tags)
        
        # Gauge for current status
        statsd.gauge("pipeline.status", 1 if status == "success" else 0, tags=tags)
    
    @staticmethod
    def record_dq_score(table_name, score, dimensions):
        tags = [f"table:{table_name}"]
        
        statsd.gauge("dq.overall_score", score, tags=tags)
        
        for dim, value in dimensions.items():
            statsd.gauge(f"dq.{dim}_score", value, tags=tags)
    
    @staticmethod
    def record_data_freshness(table_name, hours_old):
        statsd.gauge(
            "data.freshness_hours", 
            hours_old, 
            tags=[f"table:{table_name}"]
        )

# Usage in pipeline
def run_pipeline():
    start = time.time()
    try:
        # ... pipeline logic ...
        PipelineMetrics.record_pipeline_run("sales_daily", "success", time.time() - start)
    except Exception as e:
        PipelineMetrics.record_pipeline_run("sales_daily", "failure", time.time() - start)
        raise
```

#### Datadog Monitors (Alerts)

```yaml
# monitors.yaml (Terraform or Datadog API)

# Pipeline Failure Alert
- name: "Pipeline Failure Alert"
  type: "metric alert"
  query: "sum:pipeline.runs{status:failure}.as_count() > 0"
  message: |
    Pipeline {{pipeline.name}} has failed.
    @pagerduty-data-engineering
    @slack-data-alerts
  options:
    thresholds:
      critical: 0
    notify_no_data: false

# Data Freshness Alert
- name: "Data Staleness Alert"
  type: "metric alert"
  query: "avg:data.freshness_hours{*} by {table} > 24"
  message: |
    Table {{table.name}} data is stale ({{value}} hours old).
    @slack-data-alerts
  options:
    thresholds:
      warning: 12
      critical: 24

# DQ Score Drop Alert
- name: "Data Quality Score Drop"
  type: "metric alert"
  query: "avg:dq.overall_score{*} by {table} < 95"
  message: |
    DQ score for {{table.name}} dropped to {{value}}.
    Investigate at: https://grafana/dq-dashboard
    @slack-data-quality
  options:
    thresholds:
      warning: 98
      critical: 95

# Anomaly Detection (ML-based)
- name: "Row Count Anomaly"
  type: "anomaly"
  query: "avg:table.row_count{*} by {table}"
  message: |
    Anomalous row count detected for {{table.name}}.
    Expected: {{threshold}}, Actual: {{value}}
    @data-engineering-oncall
```

### 3.4 Alert Routing & Escalation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ALERT ROUTING MATRIX                                 │
└─────────────────────────────────────────────────────────────────────────────┘

SEVERITY    │  CHANNEL           │  ESCALATION         │  SLA
────────────┼────────────────────┼─────────────────────┼──────────────────
CRITICAL    │  PagerDuty         │  Immediate on-call  │  Acknowledge: 5 min
(P1)        │  Phone call        │  → Manager (30m)    │  Resolve: 1 hour
            │  ServiceNow        │  → VP (2h)          │
────────────┼────────────────────┼─────────────────────┼──────────────────
HIGH        │  Slack (urgent)    │  On-call engineer   │  Acknowledge: 15 min
(P2)        │  Email             │  → Team lead (2h)   │  Resolve: 4 hours
            │  ServiceNow        │                     │
────────────┼────────────────────┼─────────────────────┼──────────────────
MEDIUM      │  Slack (alerts)    │  Next business day  │  Acknowledge: 4 hours
(P3)        │  Email             │                     │  Resolve: 24 hours
────────────┼────────────────────┼─────────────────────┼──────────────────
LOW         │  Slack (info)      │  Sprint backlog     │  Acknowledge: N/A
(P4)        │  Dashboard only    │                     │  Resolve: Next sprint
```

---

## 🎯 Part 4: Additional Important Considerations

### 4.1 Data Lineage & Impact Analysis

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATA LINEAGE GRAPH                                  │
└─────────────────────────────────────────────────────────────────────────────┘

[Source: MySQL]──┬──▶[Bronze: raw_orders]──▶[Silver: clean_orders]──┬──▶[Gold: daily_sales]
                 │                                                   │
[Source: API]────┘                                                   └──▶[Gold: customer_360]
                                                                              │
                                                                              ▼
                                                                     [Dashboard: Sales KPIs]

USE CASES:
• Impact Analysis: "If raw_orders fails, what dashboards are affected?"
• Root Cause: "Dashboard shows wrong numbers, trace back to source"
• Compliance: "Where does PII flow? Who has access?"
```

**Tools:** Apache Atlas, Marquez, DataHub, Purview, Unity Catalog

### 4.2 Schema Evolution & Versioning

```python
# Schema registry integration
from confluent_kafka.schema_registry import SchemaRegistryClient

schema_registry = SchemaRegistryClient({"url": "http://schema-registry:8081"})

def validate_schema_compatibility(topic, new_schema):
    """Ensure new schema is backward compatible"""
    compatibility = schema_registry.test_compatibility(
        subject=f"{topic}-value",
        schema=new_schema
    )
    if not compatibility:
        raise SchemaEvolutionError(
            f"Schema change is not backward compatible for {topic}"
        )

# Delta Lake schema enforcement
df.write \
    .format("delta") \
    .option("mergeSchema", "true")  # Allow schema evolution
    # OR
    .option("overwriteSchema", "true")  # Force schema change (breaking)
    .save("/delta/table")
```

### 4.3 Data Contracts

```yaml
# data_contract.yaml
contract:
  name: "sales_daily"
  version: "2.0.0"
  owner: "sales-data-team"
  
schema:
  - name: order_id
    type: string
    nullable: false
    description: "Unique order identifier"
    pii: false
    
  - name: customer_email
    type: string
    nullable: false
    pii: true
    masking: "email"
    
  - name: amount
    type: decimal(10,2)
    nullable: false
    constraints:
      - min: 0
      - max: 1000000

sla:
  freshness: 
    max_age_hours: 24
    check_frequency: hourly
  availability:
    uptime: 99.9%
  volume:
    daily_min: 100000
    daily_max: 10000000

quality:
  expectations:
    - expect_column_values_to_be_unique: order_id
    - expect_column_values_to_not_be_null: order_id
    - expect_column_values_to_be_between:
        column: amount
        min: 0
        max: 1000000

consumers:
  - name: "analytics-team"
    access: "read"
  - name: "ml-team"
    access: "read"
    columns: ["order_id", "amount", "order_date"]  # No PII

notification:
  breaking_change: ["sales-data-team@company.com", "slack://data-contracts"]
  sla_breach: ["pagerduty://data-oncall"]
```

### 4.4 Drift Detection (Schema & Data)

```python
# Schema Drift Detection
def detect_schema_drift(current_schema, baseline_schema):
    current_cols = {f.name: f.dataType for f in current_schema.fields}
    baseline_cols = {f.name: f.dataType for f in baseline_schema.fields}
    
    added = set(current_cols.keys()) - set(baseline_cols.keys())
    removed = set(baseline_cols.keys()) - set(current_cols.keys())
    type_changed = {
        col for col in current_cols.keys() & baseline_cols.keys()
        if current_cols[col] != baseline_cols[col]
    }
    
    if added or removed or type_changed:
        log_drift_event({
            "type": "schema",
            "added": list(added),
            "removed": list(removed),
            "type_changed": list(type_changed)
        })
        alert_if_breaking(removed, type_changed)

# Data Distribution Drift (for ML)
from evidently import ColumnDriftMetric
from evidently.report import Report

def detect_data_drift(reference_df, current_df):
    report = Report(metrics=[ColumnDriftMetric(column_name="amount")])
    report.run(reference_data=reference_df, current_data=current_df)
    
    if report.as_dict()["metrics"][0]["result"]["drift_detected"]:
        alert_data_drift("amount", report.as_dict())
```

### 4.5 Cost Monitoring

```python
# Track compute costs per pipeline
def track_pipeline_cost(pipeline_name, cluster_type, runtime_hours):
    cost_per_hour = {
        "small": 0.50,
        "medium": 2.00,
        "large": 8.00,
        "gpu": 15.00
    }
    
    estimated_cost = cost_per_hour[cluster_type] * runtime_hours
    
    statsd.gauge(
        "pipeline.estimated_cost_usd",
        estimated_cost,
        tags=[f"pipeline:{pipeline_name}"]
    )
    
    # Alert if cost exceeds budget
    if estimated_cost > DAILY_BUDGET:
        alert_cost_overrun(pipeline_name, estimated_cost)
```

### 4.6 Audit Trail & Compliance

```python
# Audit logging for data access
def audit_log(action, table, user, query=None):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,  # READ, WRITE, DELETE
        "table": table,
        "user": user,
        "query_hash": hash(query) if query else None,
        "source_ip": get_source_ip(),
        "success": True
    }
    
    # Write to immutable audit log
    write_to_audit_table(log_entry)
    
    # Check for suspicious patterns
    if is_suspicious_access(user, table, action):
        alert_security_team(log_entry)
```

---

## 🎤 Interview Questions & Answers

### Q1: "How do you ensure pipeline idempotency?"

**Answer:**
> "I use three patterns depending on the use case:
> 1. **Partition overwrite** for batch: Write to date partition, rerun = clean overwrite
> 2. **MERGE/Upsert** for CDC: Match on primary key, update if exists, insert if new
> 3. **Checkpoint + deduplication** for streaming: Track processed IDs, skip duplicates
> 
> The key is choosing the right pattern for the data characteristics. For fact tables with append patterns, partition overwrite works. For slowly-changing dimensions, MERGE is essential."

### Q2: "What data quality checks do you consider essential?"

**Answer:**
> "I implement checks across multiple dimensions:
> 1. **Uniqueness:** PK duplicate check (non-negotiable)
> 2. **Freshness:** Max timestamp within SLA
> 3. **Volume:** Row count within statistical bounds (z-score < 3)
> 4. **Validity:** Value range checks, format validation
> 5. **Consistency:** Referential integrity with dimensions
> 6. **Schema:** Column presence and type validation
> 
> I use **Great Expectations** for declarative checks and **fail the pipeline** if critical checks fail. Non-critical issues go to a data quality dashboard for monitoring."

### Q3: "How do you set up monitoring and alerting for data pipelines?"

**Answer:**
> "I use a three-layer approach:
> 1. **Metrics:** StatsD/Prometheus for pipeline status, duration, DQ scores → Grafana dashboards
> 2. **Logs:** Centralized logging with structured JSON → ELK or Datadog for debugging
> 3. **Alerts:** Tiered by severity:
>    - **Critical:** Pipeline failure → PagerDuty + ServiceNow ticket
>    - **High:** DQ score drop → Slack + email
>    - **Medium:** Freshness warning → Dashboard highlight
> 
> The key is **actionable alerts**—every alert should have a runbook link and suggested resolution."

### Q4: "How do you handle automatic incident creation?"

**Answer:**
> "We integrate with ServiceNow via webhook:
> 1. Airflow `on_failure_callback` triggers a webhook
> 2. Webhook enriches the event (pipeline name, error, owner, runbook)
> 3. Creates ServiceNow incident with proper severity mapping
> 4. Simultaneously pages on-call via PagerDuty
> 5. Posts to Slack for visibility
> 
> This ensures every failure is tracked as a ticket (for SLA reporting) and gets immediate human attention for critical pipelines."

### Q5: "How do you detect data anomalies?"

**Answer:**
> "I use both statistical and ML-based approaches:
> 1. **Volume anomaly:** Z-score check on row count (alert if > 3 std dev from 30-day mean)
> 2. **Value anomaly:** Great Expectations bounds on aggregates (SUM, AVG)
> 3. **Distribution drift:** Evidently or Whylogs comparing current data to baseline
> 4. **ML-based:** Datadog anomaly monitors for time-series metrics
> 
> The key is establishing a **baseline period** and **tuning thresholds** to minimize false positives while catching real issues."

---

## 📋 Implementation Checklist

### Pipeline Reliability Checklist
- [ ] All pipelines are idempotent (overwrite or merge pattern)
- [ ] Retry strategy defined (exponential backoff for transient failures)
- [ ] Dead letter queue for unprocessable records
- [ ] ServiceNow integration for automatic ticket creation
- [ ] PagerDuty/OpsGenie for on-call alerting
- [ ] Runbooks documented for each pipeline
- [ ] SLA defined and monitored

### Data Quality Checklist
- [ ] Primary key uniqueness enforced
- [ ] Freshness check on every table
- [ ] Row count anomaly detection
- [ ] Schema validation on ingestion
- [ ] Null rate monitoring for required fields
- [ ] Referential integrity checks
- [ ] Great Expectations (or equivalent) integrated
- [ ] DQ scores published to dashboard

### Monitoring Checklist
- [ ] Grafana/Datadog dashboard per domain
- [ ] Alert thresholds tuned (no alert fatigue)
- [ ] Alert routing by severity
- [ ] Escalation policies defined
- [ ] Weekly DQ review meeting
- [ ] Monthly reliability report
