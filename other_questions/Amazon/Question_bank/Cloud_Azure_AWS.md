# Cloud Platform (AWS & Azure) Interview Questions & Answers (Question Bank 1)

> **Amazon Data Engineer Style** - AWS Ecosystem Focus with Azure Comparisons

---

## 1️⃣ AWS Storage & Compute (Part 2 Questions)

### S3 Partitioning for Athena Optimization

**Question:** How would you partition S3 data for a log ingestion pipeline receiving terabytes of data daily to optimize for Athena queries?

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    S3 PARTITIONING STRATEGY                                  │
└─────────────────────────────────────────────────────────────────────────────┘

HIVE-STYLE PARTITIONING:
s3://bucket/logs/
  ├── year=2024/month=02/day=07/hour=10/   ← 4-level partitioning
  │   ├── file1.parquet
  │   └── file2.parquet
  └── year=2024/month=02/day=07/hour=11/

BENEFITS:
• Athena can skip irrelevant partitions (partition pruning)
• Query: WHERE year=2024 AND month=02 → Scans only Feb 2024 data
• Cost: $5 per TB scanned → Huge savings!
```

**Best Practices:**

| Practice | Recommendation | Why |
|----------|---------------|-----|
| **Partition Column** | year/month/day/hour | Matches common query patterns |
| **Partition Size** | 100 MB - 1 GB each | Balance between pruning benefit and small file overhead |
| **File Format** | Parquet (Snappy) | Columnar + compressed = 10x less scan |
| **File Size** | 128 MB - 512 MB | Optimal for Athena parallelism |

```python
# Write partitioned data from Spark
df.write \
    .partitionBy("year", "month", "day", "hour") \
    .option("compression", "snappy") \
    .parquet("s3://bucket/logs/")

# Athena table definition
CREATE EXTERNAL TABLE logs (
    timestamp TIMESTAMP,
    event_type STRING,
    payload STRING
)
PARTITIONED BY (year INT, month INT, day INT, hour INT)
STORED AS PARQUET
LOCATION 's3://bucket/logs/'
TBLPROPERTIES ('parquet.compression'='SNAPPY');

-- Add partitions automatically
MSCK REPAIR TABLE logs;
```

---

### Glue vs EMR: When to Choose Which?

| Factor | AWS Glue | EMR |
|--------|----------|-----|
| **Complexity** | Serverless, simple | More control, complex |
| **Cost Model** | Per DPU-hour ($0.44) | Per instance-hour |
| **Startup Time** | 2-5 minutes | 5-10 minutes |
| **Customization** | Limited (Glue libs) | Full control (any library) |
| **Long-running** | Not ideal (timeout 48h) | Persistent clusters OK |
| **State** | Stateless | Can maintain state (Spark context) |

**Decision Matrix:**

```yaml
Use Glue When:
  - Simple ETL jobs (< 4 hours)
  - Predictable workloads
  - Team lacks Spark expertise
  - Want minimal ops overhead
  - Using Glue Catalog already

Use EMR When:
  - Long-running jobs (> 4 hours)
  - Need custom libraries (ML, special formats)
  - Cost optimization (Spot instances)
  - Interactive development (notebooks)
  - High volume requiring persistent cluster
```

**Cost Comparison (1 TB daily processing):**

```
Glue:
  10 DPUs × 2 hours × $0.44 × 30 days = $264/month

EMR (On-Demand):
  5 × r5.xlarge × 2 hours × $0.252 × 30 = $378/month

EMR (Spot, 70% savings):
  5 × r5.xlarge × 2 hours × $0.076 × 30 = $114/month ← Winner
```

---

### Kinesis Data Streams vs Firehose

| Feature | Kinesis Data Streams | Kinesis Firehose |
|---------|---------------------|------------------|
| **Use Case** | Real-time processing | Data delivery to sinks |
| **Latency** | Milliseconds | 60 sec - 15 min (buffering) |
| **Consumers** | Lambda, KCL apps, Spark | S3, Redshift, Elasticsearch |
| **Scaling** | Manual (shards) | Automatic |
| **Retention** | 24h - 365 days | No retention (pass-through) |
| **Pricing** | Per shard hour + data | Per data ingested |

**Use Firehose for S3 Ingestion:**

```yaml
Scenario: Stream 1M events/day to S3 for batch analytics

Firehose Setup:
  Source: Direct PUT or Kinesis Data Streams
  Destination: S3 (partitioned by time)
  Buffer: 5 MB or 60 seconds
  Compression: Gzip
  Format: JSON → Parquet (with Glue conversion)

Why Firehose (not Streams):
  - No need for real-time processing
  - Auto-scaling (no shard management)
  - Built-in delivery to S3 with retry
  - Lower cost for simple ingestion
```

---

### CloudFormation vs Terraform

| Aspect | CloudFormation | Terraform |
|--------|----------------|-----------|
| **Cloud Support** | AWS only | Multi-cloud |
| **State** | AWS-managed | Self-managed (S3, TFC) |
| **Language** | YAML/JSON | HCL (more readable) |
| **Drift Detection** | Built-in | terraform plan |
| **Community** | AWS modules | Rich provider ecosystem |
| **Rollback** | Automatic on failure | Manual |

**Terraform State Management:**

```hcl
# backend.tf - Store state remotely
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "data-platform/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "terraform-locks"  # State locking
    encrypt        = true
  }
}

# Best practices:
# 1. Remote state (never local in production)
# 2. State locking (DynamoDB or TFC)
# 3. Separate state files per environment
# 4. State versioning (S3 versioning enabled)
```

---

## 2️⃣ Redshift Architecture

### Leader Node vs Compute Node

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         REDSHIFT ARCHITECTURE                                │
└─────────────────────────────────────────────────────────────────────────────┘

                          ┌───────────────────┐
                          │   LEADER NODE     │
                          │  ─────────────    │
                          │  • Parses SQL     │
                          │  • Creates plan   │
                          │  • Coordinates    │
                          │  • Aggregates     │
                          │    results        │
                          └─────────┬─────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
           ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
           │ COMPUTE NODE │ │ COMPUTE NODE │ │ COMPUTE NODE │
           │ ──────────── │ │ ──────────── │ │ ──────────── │
           │ • Store data │ │ • Store data │ │ • Store data │
           │ • Execute    │ │ • Execute    │ │ • Execute    │
           │   queries    │ │   queries    │ │   queries    │
           │ • Local agg  │ │ • Local agg  │ │ • Local agg  │
           └──────────────┘ └──────────────┘ └──────────────┘
               Slice 1-2       Slice 3-4       Slice 5-6
```

**Key Points:**
- **Leader:** Single node, bottleneck for driver operations (ORDER BY LIMIT, LISTAGG)
- **Compute:** Multiple nodes, parallel processing
- **Slices:** Each node has multiple slices (1-16 per node), each processes portion of data

**Optimization:**
```sql
-- Bad: Leader-node functions
SELECT LISTAGG(product_name, ',') FROM products;  -- Leader bottleneck

-- Better: Aggregate on compute nodes
SELECT region, COUNT(*) FROM shipments GROUP BY region;  -- Parallel
```

---

## 3️⃣ AWS to Azure Comparison

| AWS Service | Azure Equivalent | Notes |
|-------------|------------------|-------|
| **S3** | Azure Blob Storage / ADLS Gen2 | ADLS Gen2 for analytics |
| **Kinesis** | Event Hubs | Event Hubs has Kafka compatibility |
| **Glue** | Data Factory + Synapse | ADF for orchestration, Synapse for Spark |
| **EMR** | HDInsight / Databricks | Databricks preferred |
| **Redshift** | Synapse Analytics | Dedicated SQL pools |
| **Athena** | Synapse Serverless SQL | Query S3/ADLS directly |
| **Lambda** | Azure Functions | Similar FaaS |
| **Step Functions** | Logic Apps / Durable Functions | Logic Apps is low-code |
| **MSK (Kafka)** | Event Hubs Kafka / HDInsight Kafka | Event Hubs simpler |
| **Lake Formation** | Purview + Unity Catalog | Data governance |

---

## 4️⃣ Hands-On: Typical Pipeline Components

### AWS Data Pipeline Architecture

```python
# Glue Job Example: Bronze to Silver
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'SOURCE_PATH', 'TARGET_PATH'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read from S3 (Bronze)
bronze_df = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={"paths": [args['SOURCE_PATH']]},
    format="json"
)

# Transform
from pyspark.sql.functions import *
silver_df = bronze_df.toDF() \
    .dropDuplicates(['event_id']) \
    .filter(col('event_type').isNotNull()) \
    .withColumn('processed_at', current_timestamp())

# Write to S3 (Silver)
silver_df.write \
    .mode('overwrite') \
    .partitionBy('event_date') \
    .parquet(args['TARGET_PATH'])

job.commit()
```

### Azure Data Pipeline Architecture

```python
# Databricks Notebook: Bronze to Silver (Azure)
from pyspark.sql.functions import *

# Read from ADLS Gen2 (Bronze)
bronze_df = spark.read \
    .format("json") \
    .load("abfss://container@storage.dfs.core.windows.net/bronze/events/")

# Transform
silver_df = bronze_df \
    .dropDuplicates(['event_id']) \
    .filter(col('event_type').isNotNull()) \
    .withColumn('processed_at', current_timestamp())

# Write to ADLS Gen2 (Silver) as Delta
silver_df.write \
    .format("delta") \
    .mode('overwrite') \
    .option('replaceWhere', f"event_date = '{processing_date}'") \
    .save("abfss://container@storage.dfs.core.windows.net/silver/events/")
```

---

## 5️⃣ Lake Formation & Data Governance

### Lake Formation Permissions

```python
# Grant permissions using Lake Formation
import boto3

client = boto3.client('lakeformation')

# Grant SELECT on table to role
response = client.grant_permissions(
    Principal={'DataLakePrincipalIdentifier': 'arn:aws:iam::123456789012:role/AnalystRole'},
    Resource={
        'Table': {
            'DatabaseName': 'analytics',
            'Name': 'shipments'
        }
    },
    Permissions=['SELECT'],
    PermissionsWithGrantOption=[]
)

# Column-level security
response = client.grant_permissions(
    Principal={'DataLakePrincipalIdentifier': 'arn:aws:iam::123456789012:role/RestrictedRole'},
    Resource={
        'TableWithColumns': {
            'DatabaseName': 'analytics',
            'Name': 'customers',
            'ColumnNames': ['name', 'email'],  # Only these columns
            'ColumnWildcard': None
        }
    },
    Permissions=['SELECT']
)
```

### Azure Purview Equivalent

```python
# Register data source in Purview
from azure.purview.catalog import PurviewCatalogClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = PurviewCatalogClient(
    endpoint="https://purview-account.purview.azure.com",
    credential=credential
)

# Create classification (PII tagging)
classification = {
    "name": "PII.Email",
    "description": "Email addresses"
}

# Assign classification to column
entity_update = {
    "guid": "column-guid",
    "classifications": [{"typeName": "PII.Email"}]
}
```
