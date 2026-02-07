# Data Modeling & Warehousing Interview Questions & Answers (Question Bank 1)

> **Amazon Data Engineer Style** - Logistics/Transportation Domain Focus

---

<a id="index"></a>
## 📑 Table of Contents

| Section | Topics |
|---------|--------|
| [1️⃣ Core Concepts](#1️⃣-core-concepts) | Facts, Dimensions, Normalization, Grain |
| &nbsp;&nbsp;&nbsp;└ [Q46: Fact vs Dimension](#q46-fact-vs-dimension--examples-from-logistics) | Logistics examples |
| &nbsp;&nbsp;&nbsp;└ [Q47: Design a shipment fact table](#q47-design-a-shipment-fact-table) | Schema design |
| &nbsp;&nbsp;&nbsp;└ [Q48: Carrier and location dimensions](#q48-design-carrier-and-location-dimensions) | Dimension tables |
| &nbsp;&nbsp;&nbsp;└ [Q49: Normalize vs denormalize](#q49-normalize-vs-denormalize--trade-offs) | Trade-offs |
| &nbsp;&nbsp;&nbsp;└ [Q50: Grain of a table](#q50-grain-of-a-table--define-and-justify) | Definition & justification |
| [2️⃣ Slowly Changing Dimensions (SCD)](#2️⃣-slowly-changing-dimensions-scd) | SCD Types, History tracking |
| &nbsp;&nbsp;&nbsp;└ [Q51: SCD Type 1 vs Type 2](#q51-scd-type-1-vs-type-2--when-to-use) | When to use |
| &nbsp;&nbsp;&nbsp;└ [Q52: Track carrier name changes](#q52-track-carrier-name-changes-over-time) | SCD2 implementation |
| &nbsp;&nbsp;&nbsp;└ [Q53: Late-arriving dimension records](#q53-handle-late-arriving-dimension-records) | Handling strategies |
| &nbsp;&nbsp;&nbsp;└ [Q54: Backfill historical data](#q54-backfill-historical-data-safely) | Safe backfill |
| &nbsp;&nbsp;&nbsp;└ [Q55: Maintain surrogate keys](#q55-maintain-surrogate-keys) | Key generation |
| [3️⃣ Analytics Design](#3️⃣-analytics-design) | Dashboard tables, Optimization |
| &nbsp;&nbsp;&nbsp;└ [Q56: Dashboard reporting tables](#q56-design-tables-for-dashboard-reporting) | Pre-aggregated marts |
| &nbsp;&nbsp;&nbsp;└ [Q57: Optimize for frequent joins](#q57-optimize-tables-for-frequent-joins) | Distribution & sort keys |
| &nbsp;&nbsp;&nbsp;└ [Q58: Partition strategy](#q58-partition-strategy-for-time-series-data) | Time-series partitioning |
| &nbsp;&nbsp;&nbsp;└ [Q59: Handle schema evolution](#q59-handle-schema-evolution) | Delta Lake, migrations |
| &nbsp;&nbsp;&nbsp;└ [Q60: Cold vs hot data separation](#q60-cold-vs-hot-data-separation) | Data tiering |
| [4️⃣ Advanced Design](#4️⃣-advanced-design-part-2-questions) | Star schema, Graph vs Relational |
| &nbsp;&nbsp;&nbsp;└ [Star Schema for Delivery Accuracy](#star-schema-for-delivery-accuracy) | Fact table design |
| &nbsp;&nbsp;&nbsp;└ [Graph vs Relational for Routes](#graph-vs-relational-for-route-networks) | When to use each |

---

<a id="1️⃣-core-concepts"></a>
## 1️⃣ Core Concepts [↩️](#index)

<a id="q46-fact-vs-dimension--examples-from-logistics"></a>
### Q46: Fact vs Dimension — examples from logistics [↩️](#index)

| Aspect | Fact Table | Dimension Table |
|--------|-----------|-----------------||
| **Contains** | Measurable events/transactions | Descriptive attributes |
| **Row Count** | Millions-Billions | Thousands-Millions |
| **Changes** | Append-only (immutable events) | Updates (SCD) |
| **Keys** | Foreign keys to dimensions | Primary key + attributes |
| **Examples (Logistics)** | fact_shipments, fact_scans, fact_costs | dim_carrier, dim_location, dim_date |

**Logistics Examples:**

```
FACTS (What happened):
- fact_shipments: Shipment created, weight, value, transit_hours
- fact_package_scans: Scan events (location, timestamp, status)
- fact_delivery_attempts: Attempt outcome, reason if failed

DIMENSIONS (Context/Attributes):
- dim_carrier: Carrier name, type, service level, contact info
- dim_location: Address, city, state, zip, region, timezone
- dim_date: Date, day_of_week, is_holiday, fiscal_quarter
- dim_customer: Customer name, segment, tier, preferences
```

---

<a id="q47-design-a-shipment-fact-table"></a>
### Q47: Design a shipment fact table [↩️](#index)

```sql
CREATE TABLE fact_shipments (
    -- Surrogate Key
    shipment_sk         BIGINT PRIMARY KEY,
    
    -- Natural Key
    shipment_id         VARCHAR(50) NOT NULL,
    
    -- Foreign Keys to Dimensions
    origin_location_sk  BIGINT REFERENCES dim_location(location_sk),
    dest_location_sk    BIGINT REFERENCES dim_location(location_sk),
    carrier_sk          BIGINT REFERENCES dim_carrier(carrier_sk),
    customer_sk         BIGINT REFERENCES dim_customer(customer_sk),
    ship_date_sk        INT REFERENCES dim_date(date_sk),
    delivery_date_sk    INT REFERENCES dim_date(date_sk),
    
    -- Measures (Quantitative)
    weight_lbs          DECIMAL(10,2),
    package_count       INT,
    declared_value_usd  DECIMAL(12,2),
    shipping_cost_usd   DECIMAL(10,2),
    transit_hours       DECIMAL(8,2),
    distance_miles      DECIMAL(10,2),
    
    -- Degenerate Dimensions (no separate table needed)
    tracking_number     VARCHAR(50),
    service_level       VARCHAR(20),
    
    -- Flags
    is_delayed          BOOLEAN,
    is_damaged          BOOLEAN,
    is_returned         BOOLEAN,
    
    -- Audit
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
PARTITION BY RANGE (ship_date_sk);  -- Partition by date
```

**Grain:** One row per shipment (the most atomic grain)

**Key Design Decisions:**
- Surrogate keys for dimensions (handle SCD)
- Date dimension keys as integers (YYYYMMDD) for efficient joins
- Separate origin/dest location keys (role-playing dimension)

---

<a id="q48-design-carrier-and-location-dimensions"></a>
### Q48: Design carrier and location dimensions [↩️](#index)

```sql
-- CARRIER DIMENSION
CREATE TABLE dim_carrier (
    carrier_sk          BIGINT PRIMARY KEY,          -- Surrogate key
    carrier_id          VARCHAR(20) NOT NULL,        -- Natural key
    carrier_name        VARCHAR(100),
    carrier_type        VARCHAR(50),                 -- Ground, Air, Ocean
    service_levels      VARCHAR(200),                -- Express, Standard, Economy
    headquarters_city   VARCHAR(100),
    headquarters_state  VARCHAR(50),
    is_active           BOOLEAN DEFAULT TRUE,
    
    -- SCD Type 2 fields
    effective_from      DATE NOT NULL,
    effective_to        DATE,                        -- NULL = current
    is_current          BOOLEAN DEFAULT TRUE
);

-- LOCATION DIMENSION
CREATE TABLE dim_location (
    location_sk         BIGINT PRIMARY KEY,
    location_id         VARCHAR(50) NOT NULL,
    location_type       VARCHAR(50),                 -- Warehouse, FC, Customer
    address_line1       VARCHAR(200),
    address_line2       VARCHAR(200),
    city                VARCHAR(100),
    state               VARCHAR(50),
    zip_code            VARCHAR(20),
    country             VARCHAR(50),
    region              VARCHAR(50),                 -- WEST, EAST, CENTRAL
    timezone            VARCHAR(50),
    latitude            DECIMAL(10,7),
    longitude           DECIMAL(10,7),
    is_active           BOOLEAN DEFAULT TRUE
);

-- DATE DIMENSION (pre-populated)
CREATE TABLE dim_date (
    date_sk             INT PRIMARY KEY,             -- YYYYMMDD format
    full_date           DATE NOT NULL,
    day_of_week         VARCHAR(10),
    day_of_month        INT,
    day_of_year         INT,
    week_of_year        INT,
    month_num           INT,
    month_name          VARCHAR(20),
    quarter             INT,
    year                INT,
    is_weekend          BOOLEAN,
    is_holiday          BOOLEAN,
    holiday_name        VARCHAR(100),
    fiscal_quarter      INT,
    fiscal_year         INT
);
```

---

<a id="q49-normalize-vs-denormalize--trade-offs"></a>
### Q49: Normalize vs denormalize — trade-offs [↩️](#index)

| Aspect | Normalized (3NF) | Denormalized (Star Schema) |
|--------|------------------|---------------------------|
| **Storage** | Less (no redundancy) | More (duplicated data) |
| **Write Performance** | Faster updates | Slower (update multiple places) |
| **Read Performance** | Slower (many joins) | Faster (fewer joins) |
| **Data Integrity** | Higher (single source) | Lower (risk of inconsistency) |
| **Flexibility** | High (add new attributes) | Medium (may need restructure) |
| **Query Complexity** | Complex (many joins) | Simple (fewer joins) |
| **Use Case** | OLTP (transactions) | OLAP (analytics) |

**Recommendation for Logistics Analytics:**
- **Use Star Schema (Denormalized)** for reporting tables
- Keep carrier name in fact table for fast queries (no join needed)
- Accept some redundancy for 10x query performance improvement

---

<a id="q50-grain-of-a-table--define-and-justify"></a>
### Q50: Grain of a table — define and justify [↩️](#index)

**Definition:** The grain is the level of detail represented by a single row.

**Examples & Justifications:**

| Table | Grain | Justification |
|-------|-------|---------------|
| `fact_shipments` | One row per shipment | Most atomic transaction; can aggregate up to any level |
| `fact_package_scans` | One row per scan event per package | Captures every status change for full tracking |
| `fact_daily_summary` | One row per carrier per day | Pre-aggregated for dashboard performance; loses detail |

**Choosing Grain:**
1. **Ask the business question:** "What's the most detailed analysis needed?"
2. **Start atomic:** You can always aggregate, but can't disaggregate
3. **Consider storage:** TB of scan events vs GB of daily summaries
4. **Balance:** Create both atomic facts and pre-aggregated marts

---

<a id="2️⃣-slowly-changing-dimensions-scd"></a>
## 2️⃣ Slowly Changing Dimensions (SCD) [↩️](#index)

<a id="q51-scd-type-1-vs-type-2--when-to-use"></a>
### Q51: SCD Type 1 vs Type 2 — when to use? [↩️](#index)

| Type | Behavior | History | Use Case |
|------|----------|---------|----------|
| **Type 1** | Overwrite old value | No history | Corrections, typos, non-meaningful changes |
| **Type 2** | Add new row with effective dates | Full history | Track changes over time (carrier name, pricing) |
| **Type 3** | Add "previous" column | Limited history | Only need current + one prior value |

```sql
-- TYPE 1: Overwrite (no history)
UPDATE dim_carrier 
SET carrier_name = 'FedEx Ground' 
WHERE carrier_id = 'FEDEX';

-- TYPE 2: Add new row (full history)
-- 1. Close existing record
UPDATE dim_carrier 
SET effective_to = CURRENT_DATE - 1, is_current = FALSE
WHERE carrier_id = 'FEDEX' AND is_current = TRUE;

-- 2. Insert new record
INSERT INTO dim_carrier (carrier_sk, carrier_id, carrier_name, effective_from, is_current)
VALUES (NEW_SK(), 'FEDEX', 'FedEx Ground', CURRENT_DATE, TRUE);
```

---

<a id="q52-track-carrier-name-changes-over-time"></a>
### Q52: Track carrier name changes over time [↩️](#index)

```sql
-- SCD Type 2 Implementation
CREATE TABLE dim_carrier_scd2 (
    carrier_sk      BIGINT PRIMARY KEY,
    carrier_id      VARCHAR(20),        -- Natural key (stable)
    carrier_name    VARCHAR(100),       -- Can change
    service_level   VARCHAR(50),
    effective_from  DATE NOT NULL,
    effective_to    DATE,               -- NULL = current
    is_current      BOOLEAN DEFAULT TRUE
);

-- Query: What was the carrier name when shipment was sent?
SELECT 
    s.shipment_id,
    s.ship_date,
    c.carrier_name
FROM fact_shipments s
JOIN dim_carrier_scd2 c 
    ON s.carrier_sk = c.carrier_sk
    AND s.ship_date BETWEEN c.effective_from AND COALESCE(c.effective_to, '9999-12-31');
```

---

<a id="q53-handle-late-arriving-dimension-records"></a>
### Q53: Handle late-arriving dimension records [↩️](#index)

**Scenario:** Shipment arrives before carrier is loaded to dimension.

```sql
-- Strategy 1: "Unknown" placeholder
INSERT INTO dim_carrier (carrier_sk, carrier_id, carrier_name)
VALUES (-1, 'UNKNOWN', 'Unknown Carrier');

-- Fact initially points to -1
INSERT INTO fact_shipments (carrier_sk, ...) VALUES (-1, ...);

-- Later, update when carrier arrives
UPDATE fact_shipments 
SET carrier_sk = (SELECT carrier_sk FROM dim_carrier WHERE carrier_id = 'FEDEX')
WHERE carrier_sk = -1 AND carrier_id_raw = 'FEDEX';

-- Strategy 2: Inferred member (auto-create stub)
INSERT INTO dim_carrier (carrier_sk, carrier_id, carrier_name, is_inferred)
VALUES (NEW_SK(), 'FEDEX', 'FEDEX (Inferred)', TRUE);

-- Later, update inferred to real
UPDATE dim_carrier 
SET carrier_name = 'FedEx Ground', is_inferred = FALSE
WHERE carrier_id = 'FEDEX' AND is_inferred = TRUE;
```

---

<a id="q54-backfill-historical-data-safely"></a>
### Q54: Backfill historical data safely [↩️](#index)

```python
# Safe Backfill Strategy
def backfill_historical_data(start_date, end_date, batch_size_days=7):
    """
    Backfill historical data without affecting current operations
    """
    current = start_date
    
    while current <= end_date:
        batch_end = min(current + timedelta(days=batch_size_days), end_date)
        
        try:
            # 1. Process batch to staging
            process_to_staging(current, batch_end)
            
            # 2. Validate staging data
            validate_staging(current, batch_end)
            
            # 3. Atomic swap (delete + insert in transaction)
            with transaction():
                delete_production(current, batch_end)
                insert_from_staging(current, batch_end)
            
            # 4. Log success
            log_backfill_success(current, batch_end)
            
        except Exception as e:
            # Staging is separate, production unaffected
            log_backfill_failure(current, batch_end, e)
            alert_team(e)
        
        current = batch_end + timedelta(days=1)
```

---

<a id="q55-maintain-surrogate-keys"></a>
### Q55: Maintain surrogate keys [↩️](#index)

```sql
-- Surrogate key generation options

-- 1. SEQUENCE (PostgreSQL/Redshift)
CREATE SEQUENCE carrier_sk_seq;
INSERT INTO dim_carrier (carrier_sk, ...) 
VALUES (NEXTVAL('carrier_sk_seq'), ...);

-- 2. IDENTITY column (most DBs)
CREATE TABLE dim_carrier (
    carrier_sk BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ...
);

-- 3. Hashing (Spark/distributed)
df = df.withColumn("carrier_sk", 
    F.abs(F.hash(F.col("carrier_id"))).cast("long"))

-- 4. Lookup table pattern
CREATE TABLE surrogate_key_lookup (
    table_name VARCHAR(100),
    natural_key VARCHAR(200),
    surrogate_key BIGINT
);

-- Get or create surrogate key
WITH new_key AS (
    SELECT COALESCE(MAX(surrogate_key), 0) + 1 AS next_key
    FROM surrogate_key_lookup
    WHERE table_name = 'dim_carrier'
)
INSERT INTO surrogate_key_lookup
SELECT 'dim_carrier', 'FEDEX', next_key FROM new_key
WHERE NOT EXISTS (
    SELECT 1 FROM surrogate_key_lookup 
    WHERE table_name = 'dim_carrier' AND natural_key = 'FEDEX'
);
```

---

<a id="3️⃣-analytics-design"></a>
## 3️⃣ Analytics Design [↩️](#index)

<a id="q56-design-tables-for-dashboard-reporting"></a>
### Q56: Design tables for dashboard reporting [↩️](#index)

```sql
-- Pre-aggregated MART for fast dashboard queries

-- DAILY OPERATIONS DASHBOARD
CREATE TABLE mart_daily_operations (
    report_date         DATE,
    region              VARCHAR(50),
    carrier             VARCHAR(100),
    
    -- Volume metrics
    total_shipments     BIGINT,
    total_packages      BIGINT,
    total_weight_lbs    DECIMAL(15,2),
    
    -- Performance metrics
    on_time_count       BIGINT,
    delayed_count       BIGINT,
    on_time_rate        DECIMAL(5,2),
    avg_transit_hours   DECIMAL(8,2),
    
    -- Cost metrics
    total_shipping_cost DECIMAL(15,2),
    cost_per_shipment   DECIMAL(10,2),
    
    PRIMARY KEY (report_date, region, carrier)
);

-- Materialized view for complex metrics
CREATE MATERIALIZED VIEW mv_carrier_performance AS
SELECT 
    carrier_name,
    DATE_TRUNC('week', ship_date) AS week,
    COUNT(*) AS shipments,
    AVG(transit_hours) AS avg_transit,
    SUM(CASE WHEN is_delayed THEN 1 ELSE 0 END)::FLOAT / COUNT(*) AS delay_rate
FROM fact_shipments f
JOIN dim_carrier c ON f.carrier_sk = c.carrier_sk
GROUP BY carrier_name, DATE_TRUNC('week', ship_date);
```

---

<a id="q57-optimize-tables-for-frequent-joins"></a>
### Q57: Optimize tables for frequent joins [↩️](#index)

```sql
-- Redshift: Distribution and Sort Keys
CREATE TABLE fact_shipments (
    shipment_id BIGINT,
    carrier_id VARCHAR(20),
    ship_date DATE,
    ...
)
DISTKEY(carrier_id)      -- Distribute by frequent join key
SORTKEY(ship_date);      -- Sort by frequent filter key

-- Redshift: Co-locate dimension with fact
CREATE TABLE dim_carrier (...)
DISTSTYLE ALL;           -- Replicate small dimension to all nodes

-- Indexing (PostgreSQL)
CREATE INDEX idx_shipments_carrier_date 
ON fact_shipments(carrier_id, ship_date);

CREATE INDEX idx_shipments_date 
ON fact_shipments(ship_date) 
INCLUDE (carrier_id, status);  -- Covering index
```

---

<a id="q58-partition-strategy-for-time-series-data"></a>
### Q58: Partition strategy for time-series data [↩️](#index)

```sql
-- Range partitioning by date
CREATE TABLE fact_shipments (
    shipment_id BIGINT,
    ship_date DATE,
    ...
) PARTITION BY RANGE (ship_date);

-- Create monthly partitions
CREATE TABLE fact_shipments_2024_01 
    PARTITION OF fact_shipments 
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE fact_shipments_2024_02 
    PARTITION OF fact_shipments 
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Query benefits (partition pruning)
SELECT * FROM fact_shipments 
WHERE ship_date BETWEEN '2024-01-15' AND '2024-01-20';
-- Only scans fact_shipments_2024_01!

-- Delta Lake / Spark partitioning
df.write \
    .format("delta") \
    .partitionBy("year", "month") \
    .save("/data/fact_shipments/")
```

**Partitioning Guidelines:**
| Data Size | Partition Granularity | Partition Size Target |
|-----------|----------------------|----------------------|
| < 100 GB/day | Monthly | 50-500 GB |
| 100 GB - 1 TB/day | Weekly | 100 GB - 1 TB |
| > 1 TB/day | Daily | 1-5 TB |

---

<a id="q59-handle-schema-evolution"></a>
### Q59: Handle schema evolution [↩️](#index)

```python
# Delta Lake: Schema evolution
df.write \
    .format("delta") \
    .option("mergeSchema", "true")  # Allow new columns \
    .mode("append") \
    .save("/data/shipments/")

# Spark: Handling missing columns
from pyspark.sql.functions import lit

def align_schema(df, expected_schema):
    """Add missing columns with nulls"""
    for field in expected_schema:
        if field.name not in df.columns:
            df = df.withColumn(field.name, lit(None).cast(field.dataType))
    
    # Reorder to match expected schema
    return df.select([f.name for f in expected_schema])

# SQL: Add nullable column (backward compatible)
ALTER TABLE fact_shipments ADD COLUMN carbon_footprint DECIMAL(10,2);

# Avoid breaking changes:
# ❌ Dropping columns, renaming columns, changing types
# ✅ Adding nullable columns, adding constraints with defaults
```

---

<a id="q60-cold-vs-hot-data-separation"></a>
### Q60: Cold vs hot data separation [↩️](#index)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA TIERING STRATEGY                                │
└─────────────────────────────────────────────────────────────────────────────┘

HOT DATA (< 30 days)
────────────────────
Storage: SSD / Redshift RA3 / Delta Lake
Access: Frequent queries, dashboards
Cost: $$$$
Query Time: < 1 second

WARM DATA (30-180 days)
───────────────────────
Storage: S3 Standard / ADLS Hot
Access: Weekly reports, ad-hoc queries
Cost: $$
Query Time: 5-30 seconds

COLD DATA (180 days - 2 years)
──────────────────────────────
Storage: S3 Infrequent Access / ADLS Cool
Access: Compliance, historical analysis
Cost: $
Query Time: 30 seconds - 5 minutes

ARCHIVE DATA (> 2 years)
────────────────────────
Storage: S3 Glacier / ADLS Archive
Access: Rare, legal/audit only
Cost: ¢
Query Time: Hours (retrieval required)
```

```sql
-- Implement with views for transparency
CREATE VIEW v_shipments_all AS
SELECT * FROM fact_shipments_hot      -- Last 30 days
UNION ALL
SELECT * FROM fact_shipments_warm     -- 30-180 days
UNION ALL
SELECT * FROM fact_shipments_cold;    -- Older (external table)

-- Lifecycle policies (AWS S3)
-- Automatically transition objects based on age
```

---

<a id="4️⃣-advanced-design-part-2-questions"></a>
## 4️⃣ Advanced Design (Part 2 Questions) [↩️](#index)

<a id="star-schema-for-delivery-accuracy"></a>
### Star Schema for Delivery Accuracy [↩️](#index)

```sql
-- FACT TABLE: Delivery Events
CREATE TABLE fact_delivery (
    delivery_sk         BIGINT PRIMARY KEY,
    shipment_id         VARCHAR(50),
    
    -- Dimension FKs
    origin_location_sk  BIGINT,
    dest_location_sk    BIGINT,
    carrier_sk          BIGINT,
    customer_sk         BIGINT,
    promised_date_sk    INT,
    actual_date_sk      INT,
    
    -- Measures
    promised_transit_hrs DECIMAL(8,2),
    actual_transit_hrs   DECIMAL(8,2),
    delay_hrs            DECIMAL(8,2),
    is_on_time          BOOLEAN,
    delay_reason_code   VARCHAR(50)
);

-- Sample analysis queries
-- 1. On-time rate by carrier
SELECT 
    c.carrier_name,
    COUNT(*) AS deliveries,
    SUM(CASE WHEN is_on_time THEN 1 ELSE 0 END) AS on_time,
    ROUND(100.0 * SUM(CASE WHEN is_on_time THEN 1 ELSE 0 END) / COUNT(*), 2) AS on_time_pct
FROM fact_delivery f
JOIN dim_carrier c ON f.carrier_sk = c.carrier_sk
GROUP BY c.carrier_name;

-- 2. Delay trends by region and month
SELECT 
    l.region,
    d.month_name,
    AVG(f.delay_hrs) AS avg_delay
FROM fact_delivery f
JOIN dim_location l ON f.dest_location_sk = l.location_sk
JOIN dim_date d ON f.actual_date_sk = d.date_sk
WHERE NOT f.is_on_time
GROUP BY l.region, d.month_name;
```

<a id="graph-vs-relational-for-route-networks"></a>
### Graph vs Relational for Route Networks [↩️](#index)

| Aspect | Relational | Graph DB (Neo4j) |
|--------|------------|------------------|
| **Query: Direct routes** | Simple JOIN | MATCH (a)-[:ROUTE]->(b) |
| **Query: 3+ hop paths** | Complex recursive CTE | MATCH path = (a)-[*3..5]->(b) |
| **Performance at depth** | Degrades exponentially | Linear with hops |
| **Use Case** | Reporting, aggregations | Pathfinding, recommendations |

**Recommendation:**
- Use **Relational** for: Route cost analysis, capacity planning, aggregated metrics
- Use **Graph** for: Shortest path, network optimization, real-time routing decisions

```sql
-- Relational: Find all 2-hop routes
WITH routes AS (
    SELECT source, destination FROM transportation_lanes
)
SELECT 
    r1.source AS origin,
    r1.destination AS intermediate,
    r2.destination AS final
FROM routes r1
JOIN routes r2 ON r1.destination = r2.source
WHERE r1.source = 'Seattle' AND r2.destination = 'Miami';

-- Graph (Neo4j Cypher)
MATCH path = (seattle:City {name: 'Seattle'})-[:ROUTE*1..3]->(miami:City {name: 'Miami'})
RETURN path, length(path) AS hops
ORDER BY hops
LIMIT 5;
```
