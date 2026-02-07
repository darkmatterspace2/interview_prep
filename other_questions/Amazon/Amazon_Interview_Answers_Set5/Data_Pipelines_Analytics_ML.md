# Data Pipeline Design: Analytics vs ML Considerations

> **Interview Focus:** Key differences when designing pipelines for **Analytics/BI** vs **Machine Learning** workloads, with deep-dive into Feature Stores.

---

## 📌 Analytics vs ML Pipelines: Fundamental Differences

| Dimension | Analytics/BI Pipelines | ML Pipelines |
|-----------|----------------------|--------------|
| **Primary Consumer** | Humans (Analysts, Executives) | Models (Training & Inference) |
| **Output** | Dashboards, Reports, Ad-hoc queries | Predictions, Scores, Recommendations |
| **Data Shape** | Wide, denormalized (star schema) | Feature vectors (numerical, normalized) |
| **Latency Tolerance** | Minutes to Hours | Training: Hours, Inference: Milliseconds |
| **Freshness Need** | Daily/Weekly often sufficient | Real-time features critical for some models |
| **Schema** | Fixed, well-defined dimensions | Evolving features, experimentation |
| **Compute Pattern** | Aggregations, Joins, Window functions | Matrix operations, Gradient descent |
| **Debugging** | "Why does this number look wrong?" | "Why did the model predict this?" |

---

## 🎯 Key Considerations for Analytics Pipelines

### 1. Data Modeling Strategy

#### Star Schema vs Denormalized Tables

```
STAR SCHEMA (Preferred for Analytics)
                    ┌───────────────────┐
                    │   FACT_SALES      │
                    │ ───────────────── │
                    │ sale_id           │
     ┌──────────────│ date_key (FK)     │──────────────┐
     │              │ product_key (FK)  │              │
     │              │ customer_key (FK) │              │
     │              │ amount            │              │
     │              │ quantity          │              │
     │              └───────────────────┘              │
     ▼                       │                        ▼
┌──────────────┐            │            ┌──────────────────┐
│  DIM_DATE    │            │            │  DIM_CUSTOMER    │
│ ──────────── │            │            │ ──────────────── │
│ date_key     │            │            │ customer_key     │
│ date         │            ▼            │ name             │
│ month        │   ┌──────────────────┐  │ segment          │
│ quarter      │   │   DIM_PRODUCT    │  │ region           │
│ year         │   │ ──────────────── │  │ lifetime_value   │
│ day_of_week  │   │ product_key      │  └──────────────────┘
│ is_holiday   │   │ name             │
└──────────────┘   │ category         │
                   │ subcategory      │
                   └──────────────────┘
```

**Why Star Schema for Analytics?**
| Benefit | Explanation |
|---------|-------------|
| **Query Performance** | Fewer joins, predictable patterns |
| **Understandability** | Business users comprehend it |
| **BI Tool Compatibility** | Power BI, Tableau expect this structure |
| **Aggregation Efficiency** | Pre-aggregate facts, slice by dimensions |

### 2. Query Pattern Optimization

| Pattern | Optimization Strategy |
|---------|----------------------|
| **Time-series analysis** | Partition by date, order by timestamp |
| **Aggregations** | Pre-compute in Gold layer (hourly/daily) |
| **Drill-down** | Hierarchical dimensions (Year→Quarter→Month→Day) |
| **Top-N queries** | Materialized views for common rankings |
| **Ad-hoc exploration** | Column-store format (Parquet), predicate pushdown |

### 3. SCD (Slowly Changing Dimensions) Strategy

| SCD Type | Description | Use Case | Storage Impact |
|----------|-------------|----------|----------------|
| **Type 1** | Overwrite | Corrections only | Minimal |
| **Type 2** | Add new row + effective dates | Full history needed | High |
| **Type 3** | Add previous value column | Limited history | Moderate |

```sql
-- SCD Type 2 Example
CREATE TABLE dim_customer (
    customer_sk    BIGINT,           -- Surrogate key
    customer_id    VARCHAR,          -- Natural key
    name           VARCHAR,
    segment        VARCHAR,
    effective_from DATE,
    effective_to   DATE,             -- NULL = current
    is_current     BOOLEAN
);

-- Query: Get customer segment at time of sale
SELECT f.amount, d.segment
FROM fact_sales f
JOIN dim_customer d ON f.customer_sk = d.customer_sk
WHERE f.sale_date BETWEEN d.effective_from AND COALESCE(d.effective_to, '9999-12-31');
```

### 4. Semantic Layer Considerations

| Aspect | What to Define |
|--------|----------------|
| **Metrics** | Revenue = SUM(amount), Unique Customers = COUNT(DISTINCT customer_id) |
| **Dimensions** | Region hierarchy, Product taxonomy |
| **Business Logic** | "Active Customer" = purchased in last 90 days |
| **Access Control** | Finance sees all; Sales sees their region only |

**Tools:** dbt Semantic Layer, LookML (Looker), Power BI Measures

### 5. Data Freshness & SLAs

| Dashboard Type | Typical SLA | Implementation |
|----------------|-------------|----------------|
| Executive Summary | Daily (by 6 AM) | Batch overnight |
| Operational Dashboard | Hourly | Incremental loads |
| Real-time Metrics | 5-15 minutes | Streaming to serving layer |

---

## 🤖 Key Considerations for ML Pipelines

### 1. Feature Engineering Pipeline Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ML FEATURE PIPELINE                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
     ┌──────────────────────────────┼──────────────────────────────┐
     ▼                              ▼                              ▼
┌───────────────────┐   ┌───────────────────────────┐   ┌─────────────────────┐
│   RAW SOURCES     │   │    FEATURE TRANSFORMS     │   │    FEATURE STORE    │
│ ───────────────── │   │ ───────────────────────── │   │ ─────────────────── │
│ • Transactions    │   │ Batch Features:           │   │                     │
│ • User Events     │──▶│ • Aggregations (30d sum)  │──▶│  OFFLINE STORE      │
│ • Product Catalog │   │ • Ratios (conversion %)   │   │  (Delta/Parquet)    │
│ • External APIs   │   │ • Embeddings              │   │                     │
└───────────────────┘   │                           │   │  ONLINE STORE       │
                        │ Real-time Features:       │   │  (Redis/DynamoDB)   │
                        │ • Session aggregates      │   │                     │
                        │ • Recent behavior         │   └─────────────────────┘
                        │ • Point-in-time lookups   │              │
                        └───────────────────────────┘              │
                                                                   ▼
                                               ┌───────────────────────────────┐
                                               │       MODEL TRAINING          │
                                               │ ───────────────────────────── │
                                               │ Training: Read from OFFLINE   │
                                               │ Inference: Read from ONLINE   │
                                               └───────────────────────────────┘
```

### 2. Training-Serving Skew: The #1 ML Pipeline Problem

**Problem:** Features computed differently in training vs inference → model performs poorly in production.

| Skew Type | Example | Impact |
|-----------|---------|--------|
| **Data Skew** | Training data filtered differently | Model learns on wrong population |
| **Feature Skew** | Training: pandas mean(), Serving: SQL AVG() | Floating-point differences |
| **Time Skew** | Training uses future data (label leakage) | Inflated offline metrics |
| **Distribution Skew** | Training data from 2023, serving in 2024 | Concept drift |

**Solution: Feature Store**

```python
# WRONG: Different code paths
# Training (Python)
df['avg_purchase'] = df.groupby('user_id')['amount'].transform('mean')

# Serving (SQL)
SELECT AVG(amount) FROM purchases WHERE user_id = ?  # Subtle differences!

# CORRECT: Feature Store (Single Definition)
from feast import FeatureStore
store = FeatureStore(".")

# Training
training_df = store.get_historical_features(
    entity_df=training_entities,
    features=["user_features:avg_purchase_30d"]
).to_df()

# Serving
online_features = store.get_online_features(
    entity_rows=[{"user_id": "123"}],
    features=["user_features:avg_purchase_30d"]
).to_dict()
```

### 3. Point-in-Time Correctness (Critical!)

**Problem:** When training, you must only use data that was available at prediction time.

```
Timeline Example:
─────────────────────────────────────────────────────────────────────▶ Time
       │             │                │                │
   Jan 15        Jan 20           Feb 1           Feb 15
   (Event)    (Label Known)     (Training)     (Prediction)
   
WRONG: On Feb 1, use customer data from Feb 1 to predict Jan 15 event
       (Label leakage - using future data)

CORRECT: On Feb 1, use customer data as of Jan 15 to predict Jan 15 event
         (Point-in-time join)
```

```python
# Point-in-Time Join Implementation
from feast import FeatureStore

training_entities = pd.DataFrame({
    "user_id": ["A", "B", "C"],
    "event_timestamp": ["2024-01-15", "2024-01-20", "2024-01-25"]  # When prediction needed
})

# Feast automatically joins features as of event_timestamp
training_df = store.get_historical_features(
    entity_df=training_entities,
    features=["user_features:purchase_count_30d", "user_features:avg_order_value"]
).to_df()
```

### 4. Feature Freshness Requirements

| Feature Type | Freshness | Examples | Storage |
|--------------|-----------|----------|---------|
| **Static** | Days-Weeks | Age, Gender, Account type | Batch updated |
| **Slow-moving** | Hours-Daily | Lifetime value, Segment | Daily batch |
| **Fast-moving** | Minutes | Session behavior, Cart contents | Near real-time |
| **Real-time** | Seconds | Current page, Last click | Streaming |

### 5. ML-Specific Data Quality

| Check | Why It Matters for ML |
|-------|----------------------|
| **Null Rate** | Models can't handle nulls (imputation needed) |
| **Distribution Stability** | Drift degrades model performance |
| **Outliers** | Tree models handle them; Linear models don't |
| **Class Imbalance** | 99% majority class? Model will be useless |
| **Feature Correlation** | Highly correlated features add complexity, not value |

```python
# Data Quality Checks for ML Pipeline
from great_expectations import expect

# Feature-specific validations
expect_column_values_to_not_be_null("user_id")
expect_column_values_to_be_between("age", 13, 120)
expect_column_proportion_of_unique_values_to_be_between("email", 0.99, 1.0)

# Distribution monitoring
expect_column_mean_to_be_between("purchase_amount", 45, 55)  # Alert if mean drifts
expect_column_stdev_to_be_between("purchase_amount", 10, 20)
```

---

## 🏪 Feature Store Deep Dive

### What Is a Feature Store?

A centralized repository for storing, managing, and serving ML features with:
- **Single source of truth** for feature definitions
- **Offline store** for training (historical join capability)
- **Online store** for inference (low-latency serving)
- **Feature registry** for discovery and governance

### Feature Store Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            FEATURE STORE                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                         FEATURE REGISTRY                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  Feature: user_purchase_count_30d                                        │ │
│  │  Entity: user_id                                                         │ │
│  │  Type: INT64                                                             │ │
│  │  Description: Count of purchases in last 30 days                        │ │
│  │  Owner: fraud-team                                                       │ │
│  │  Created: 2024-01-15                                                    │ │
│  │  Tags: [fraud, user-behavior, high-value]                               │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
         │                                               │
         ▼                                               ▼
┌────────────────────────────────┐     ┌────────────────────────────────────────┐
│       OFFLINE STORE            │     │           ONLINE STORE                  │
│ ────────────────────────────── │     │ ──────────────────────────────────────  │
│  Storage: S3/Delta/BigQuery    │     │  Storage: Redis/DynamoDB/Bigtable       │
│  Format: Parquet (columnar)    │     │  Format: Key-Value                      │
│                                │     │                                         │
│  Use Case: TRAINING            │     │  Use Case: INFERENCE                    │
│  • Historical features         │     │  • Latest feature values                │
│  • Point-in-time joins         │     │  • Low-latency lookup (< 10ms)          │
│  • Backfill capability         │     │  • High throughput (100K QPS)           │
│                                │     │                                         │
│  Query Pattern:                │     │  Query Pattern:                         │
│  "Get user features as of      │     │  "Get current features for              │
│   Jan 15, 2024"                │     │   user_id=12345"                        │
└────────────────────────────────┘     └────────────────────────────────────────┘
         │                                               │
         │      ┌────────────────────────────────┐       │
         │      │     MATERIALIZATION JOB        │       │
         │      │ ────────────────────────────── │       │
         └─────▶│  Sync Offline → Online        │◀──────┘
                │  Schedule: Every 15 min       │
                │  Mode: Incremental            │
                └────────────────────────────────┘
```

### Feature Store Options Comparison

| Feature Store | Type | Offline | Online | Streaming | Best For |
|---------------|------|---------|--------|-----------|----------|
| **Feast** | OSS | S3/BQ/Redshift | Redis/DynamoDB | Kafka | Full control, multi-cloud |
| **Databricks Feature Store** | Managed | Delta Lake | Cosmos/DynamoDB | Spark | Databricks shops |
| **SageMaker Feature Store** | Managed | S3 | DynamoDB | Kinesis | AWS-native |
| **Vertex AI Feature Store** | Managed | BigQuery | Bigtable | Dataflow | GCP-native |
| **Tecton** | Managed | Snowflake/BQ | DynamoDB/Redis | Spark/Flink | Enterprise, streaming-first |
| **Hopsworks** | OSS/Managed | Hudi | RonDB | Spark/Flink | Open-source enterprise |

### Feast (Open Source) Example

```python
# feature_repo/feature_definitions.py
from feast import Entity, Feature, FeatureView, FileSource, ValueType
from datetime import timedelta

# Entity Definition
user = Entity(
    name="user_id",
    value_type=ValueType.STRING,
    description="Customer ID"
)

# Offline Source (S3/Parquet)
user_features_source = FileSource(
    path="s3://my-bucket/features/user_features/",
    event_timestamp_column="event_timestamp",
)

# Feature View Definition
user_features = FeatureView(
    name="user_features",
    entities=["user_id"],
    ttl=timedelta(days=90),
    features=[
        Feature(name="purchase_count_30d", dtype=ValueType.INT64),
        Feature(name="avg_order_value", dtype=ValueType.FLOAT),
        Feature(name="days_since_last_purchase", dtype=ValueType.INT64),
        Feature(name="preferred_category", dtype=ValueType.STRING),
    ],
    online=True,  # Materialize to online store
    source=user_features_source,
    tags={"team": "fraud", "criticality": "high"}
)
```

```python
# Training Pipeline (Offline)
from feast import FeatureStore

store = FeatureStore(repo_path="feature_repo/")

# Training entities with point-in-time
training_entities = pd.DataFrame({
    "user_id": ["user_1", "user_2", "user_3"],
    "event_timestamp": pd.to_datetime(["2024-01-15", "2024-01-20", "2024-01-25"])
})

# Get historical features (point-in-time correct!)
training_df = store.get_historical_features(
    entity_df=training_entities,
    features=[
        "user_features:purchase_count_30d",
        "user_features:avg_order_value",
        "user_features:days_since_last_purchase",
    ]
).to_df()

# Train model
model.fit(training_df[features], training_df[label])
```

```python
# Inference Pipeline (Online)
# Materialize latest features to online store
store.materialize_incremental(end_date=datetime.now())

# Serve predictions
@app.route("/predict")
def predict():
    user_id = request.args.get("user_id")
    
    # Fetch features from online store (< 10ms)
    feature_vector = store.get_online_features(
        entity_rows=[{"user_id": user_id}],
        features=[
            "user_features:purchase_count_30d",
            "user_features:avg_order_value",
            "user_features:days_since_last_purchase",
        ]
    ).to_dict()
    
    # Run inference
    prediction = model.predict([feature_vector])
    return {"prediction": prediction}
```

### Feature Store: Key Decisions

| Decision | Option A | Option B | Guidance |
|----------|----------|----------|----------|
| **Build vs Buy** | Custom (S3 + Redis) | Managed (Feast/Tecton) | Custom if < 50 features; Managed if 100+ |
| **Offline Storage** | Delta Lake | Snowflake | Delta for Spark shops; Snowflake for SQL |
| **Online Storage** | Redis | DynamoDB | Redis for < 10ms; DynamoDB for managed ops |
| **Streaming Features** | Flink + Kafka | Spark Streaming | Flink for true real-time; Spark for simpler |
| **Schema** | Typed (Protobuf) | Flexible (JSON) | Typed for production; Flexible for experimentation |

---

## 🔄 Unified Pipeline: Serving Both Analytics & ML

### Medallion Architecture for Dual Use

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              BRONZE LAYER                                    │
│                          (Raw, Immutable)                                    │
│  ────────────────────────────────────────────────────────────────────────── │
│  • Schema-on-read                                                           │
│  • Full fidelity preservation                                               │
│  • Append-only                                                              │
│  • Shared by Analytics & ML                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SILVER LAYER                                    │
│                       (Cleaned, Standardized)                                │
│  ────────────────────────────────────────────────────────────────────────── │
│  • Deduplication                                                            │
│  • Type casting                                                             │
│  • Null handling                                                            │
│  • Shared by Analytics & ML                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                    │                                       │
                    ▼                                       ▼
┌──────────────────────────────────┐     ┌──────────────────────────────────────┐
│     GOLD LAYER (ANALYTICS)        │     │     GOLD LAYER (ML)                   │
│ ────────────────────────────────  │     │ ──────────────────────────────────── │
│  Star Schema:                     │     │  Feature Tables:                     │
│  • dim_customer                   │     │  • user_features                     │
│  • dim_product                    │     │  • product_features                  │
│  • dim_date                       │     │  • session_features                  │
│  • fact_sales                     │     │                                      │
│                                   │     │  Format: Wide tables                 │
│  Format: Dimensional model        │     │  (one row per entity)                │
│                                   │     │                                      │
│  Consumers:                       │     │  Consumers:                          │
│  • BI Tools (Power BI, Tableau)   │     │  • Feature Store                     │
│  • Analysts (SQL)                 │     │  • Training Pipelines                │
│  • Reports (Scheduled)            │     │  • Model Serving                     │
└──────────────────────────────────┘     └──────────────────────────────────────┘
```

### Shared vs Separate Pipeline Components

| Component | Shared | Separate | Reasoning |
|-----------|--------|----------|-----------|
| **Ingestion** | ✅ | | Single source of truth |
| **Bronze Storage** | ✅ | | No reason to duplicate raw data |
| **Silver Cleaning** | ✅ | | Same cleaning logic |
| **Orchestration** | ✅ | | Unified scheduling |
| **Gold Aggregations** | | ✅ | Different shapes (star vs feature) |
| **Serving Layer** | | ✅ | Different latency requirements |
| **Quality Checks** | Partial | Partial | Some shared, ML needs additional |

---

## 📊 Comparison: Analytics vs ML Pipeline Requirements

### Data Characteristics

| Characteristic | Analytics | ML |
|----------------|-----------|-----|
| **Granularity** | Aggregated (daily, hourly) | Row-level or entity-level |
| **Dimensions** | Many (50+ columns) | Feature vectors (100-1000 features) |
| **Historical Depth** | Years (for trends) | Months (training window) |
| **Schema Stability** | Highly stable | Experimental (new features often) |
| **Null Handling** | Show "N/A" | Impute or drop |

### Processing Patterns

| Pattern | Analytics | ML |
|---------|-----------|-----|
| **Main Operation** | Aggregation (SUM, AVG, COUNT) | Transformation (normalize, encode) |
| **Joins** | Fact-dimension joins | Entity-feature joins |
| **Windows** | Time windows (MTD, YTD) | Rolling windows (30d average) |
| **Output** | Tables/Views | Feature vectors |

### Serving Requirements

| Requirement | Analytics | ML |
|-------------|-----------|-----|
| **Query Latency** | 1-10 seconds acceptable | < 100ms for real-time inference |
| **Concurrency** | 10-100 users | 10,000+ predictions/second |
| **Caching** | Dashboard-level | Feature-level |
| **Freshness** | Hourly/Daily | Minutes (for real-time features) |

---

## 🛠️ Pipeline Tooling Recommendations

### For Analytics-Heavy Organizations

| Layer | Recommended | Why |
|-------|-------------|-----|
| **Orchestration** | Airflow / ADF | Mature, wide adoption |
| **Transformation** | dbt + Spark | SQL-first, version control |
| **Storage** | Delta Lake / Snowflake | ACID, performance |
| **BI** | Power BI / Looker | Enterprise features |
| **Catalog** | Purview / Unity Catalog | Governance focus |

### For ML-Heavy Organizations

| Layer | Recommended | Why |
|-------|-------------|-----|
| **Orchestration** | Airflow + Kubeflow | ML-aware scheduling |
| **Feature Engineering** | Spark + Feast | Scalable, feature store native |
| **Storage** | Delta Lake + Redis | Offline + Online |
| **ML Platform** | MLflow / SageMaker | Experiment tracking, deployment |
| **Monitoring** | Evidently / Whylogs | Drift detection |

### For Both (Unified Platform)

| Layer | Recommended | Why |
|-------|-------------|-----|
| **Orchestration** | Databricks Workflows | Unified for both |
| **Transformation** | dbt + Spark | SQL + Python |
| **Storage** | Delta Lake | Single storage layer |
| **Feature Store** | Databricks Feature Store | Integrated with platform |
| **BI + ML** | Databricks SQL + MLflow | Unified platform |

---

## 🎤 Interview Questions & Answers

### Q1: "How would you design a pipeline that serves both analytics dashboards and ML models?"

**Answer:**
> "I would use a **Medallion Architecture** with shared Bronze and Silver layers, but separate Gold layers optimized for each use case.
> 
> - **Bronze:** Raw, immutable data from sources (shared)
> - **Silver:** Cleaned, deduplicated, typed (shared)
> - **Gold-Analytics:** Star schema with fact/dimension tables for BI tools
> - **Gold-ML:** Feature tables with wide entity-centric structure for Feature Store
> 
> The key is **don't duplicate data processing**—both Gold layers read from Silver. This ensures consistency while allowing purpose-built structures."

### Q2: "What is a Feature Store and why do you need one?"

**Answer:**
> "A **Feature Store** is a centralized system for managing ML features with:
> 
> 1. **Offline store** (S3/Delta) for training with point-in-time correctness
> 2. **Online store** (Redis) for low-latency serving
> 3. **Feature registry** for discovery and governance
> 
> You need it because of **training-serving skew**—if you compute features differently in training (Python) vs serving (SQL), your model performs poorly. Feature Store ensures the same feature definition is used everywhere."

### Q3: "Explain training-serving skew and how to prevent it."

**Answer:**
> "Training-serving skew occurs when features are computed differently at training time vs inference time. Examples:
> 
> - **Code skew:** `pandas.mean()` vs `SQL AVG()` produce different results
> - **Time skew:** Training uses future data (label leakage)
> - **Data skew:** Training data filtered differently than production
> 
> **Prevention:**
> 1. Use a **Feature Store** with single feature definitions
> 2. Implement **point-in-time joins** for historical features
> 3. Monitor **feature distributions** in production vs training
> 4. Use **offline-online consistency checks** (sample and compare)"

### Q4: "How do you handle real-time features for ML models?"

**Answer:**
> "I separate features by freshness requirements:
> 
> | Type | Latency | Solution |
> |------|---------|----------|
> | **Static** (age, account type) | Days | Batch → Feature Store |
> | **Slow** (30-day aggregates) | Hours | Daily batch |
> | **Fast** (session behavior) | Minutes | Streaming → Online store |
> | **Real-time** (current page) | Seconds | Computed at request time |
> 
> For streaming features, I use **Spark Structured Streaming** or **Flink** writing to Redis. The inference service reads from Redis for fast features and computes real-time features in-process."

### Q5: "How do you ensure point-in-time correctness in feature engineering?"

**Answer:**
> "Point-in-time correctness means using only data that was available at prediction time. Implementation:
> 
> 1. **Store event timestamps** with every feature update
> 2. Use **Feature Store with temporal joins** (Feast `get_historical_features`)
> 3. **Never aggregate into the future**—window ends at event time
> 
> Example: To predict if a user will churn on Jan 15, I must use their features as of Jan 14, not current features. Feast handles this automatically with `event_timestamp` column."

---

## 📋 Pipeline Checklist

### Analytics Pipeline Checklist

- [ ] Data model designed (star schema vs wide tables)
- [ ] SCD strategy defined per dimension
- [ ] Freshness SLAs documented
- [ ] Semantic layer configured (metrics, hierarchies)
- [ ] Access control implemented (row/column level)
- [ ] Query performance optimized (partitions, indexes)
- [ ] Dashboard caching configured
- [ ] Data quality checks automated

### ML Pipeline Checklist

- [ ] Feature definitions centralized (Feature Store or equivalent)
- [ ] Point-in-time correctness verified
- [ ] Training-serving parity tested
- [ ] Feature freshness requirements documented
- [ ] Null handling strategy defined
- [ ] Feature drift monitoring configured
- [ ] Model versioning implemented
- [ ] A/B testing infrastructure ready
- [ ] Rollback procedure documented
- [ ] Feature lineage tracked

---

## 🔑 Key Takeaways

| For Analytics | For ML |
|---------------|--------|
| Star schema wins | Feature Store is essential |
| Aggregate early (Gold layer) | Keep row-level data accessible |
| SCD Type 2 for history | Point-in-time joins critical |
| Query performance is key | Inference latency is key |
| dbt + Semantic layer | Feast/Tecton + MLflow |
| Daily freshness often enough | Real-time features for some models |
| Business users are consumers | Models are consumers |
