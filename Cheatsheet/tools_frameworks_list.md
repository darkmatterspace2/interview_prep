# Data Engineering Tools & Frameworks Cheatsheet

> **Complete reference of tools, technologies, and frameworks used in Data Engineering**

---

## 📑 Table of Contents
| # | Category | Key Tools |
|---|----------|-----------|
| 1 | [Storage](#1-storage) | ADLS, S3, GCS, HDFS, Redis |
| 2 | [Databases](#2-databases) | PostgreSQL, Snowflake, BigQuery, MongoDB |
| 3 | [File & Table Formats](#3-file--table-formats) | Parquet, Delta Lake, Iceberg |
| 4 | [Batch Processing](#4-batch-processing) | Spark, Databricks, EMR, Glue |
| 5 | [Streaming & Messaging](#5-streaming--messaging) | Kafka, Flink, Kinesis, Event Hubs |
| 6 | [Orchestration](#6-orchestration) | Airflow, Data Factory, Dagster |
| 7 | [ETL/ELT Tools](#7-etl--elt-tools) | Fivetran, dbt, Airbyte |
| 8 | [Data Quality](#8-data-quality) | Great Expectations, Soda, dbt tests |
| 9 | [Data Governance](#9-data-governance--catalog) | Unity Catalog, DataHub, Atlan |
| 10 | [CDC & Replication](#10-cdc--data-replication) | Debezium, DMS, Datastream |
| 11 | [ML & Feature Stores](#11-ml--feature-stores) | Feast, SageMaker, MLflow |
| 12 | [BI & Visualization](#12-bi--visualization) | Power BI, Tableau, Looker |
| 13 | [Monitoring & Observability](#13-monitoring--observability) | Prometheus, Datadog, Monte Carlo |
| 14 | [Infrastructure & DevOps](#14-infrastructure--devops) | Terraform, Docker, Kubernetes |
| 15 | [Programming & Libraries](#15-programming--libraries) | Python, PySpark, Pandas |

---

## 1. Storage

### Object / Data Lake Storage
> Used for **raw, bronze, silver, gold layers** in data lakes

| Cloud | Service | Notes |
|-------|---------|-------|
| **Azure** | Blob Storage | General purpose |
| **Azure** | **ADLS Gen2** ⭐ | Preferred for analytics (hierarchical namespace) |
| **AWS** | **S3** ⭐ | Industry standard for data lakes |
| **GCP** | **GCS** | Google Cloud Storage |
| **On-Prem** | HDFS | Hadoop legacy, still used |
| **Open Source** | MinIO | S3-compatible, self-hosted |

### Cache / In-Memory Storage
> Used for **real-time serving, feature lookup, hot path**

| Tool | Use Case |
|------|----------|
| **Redis** ⭐ | Key-value cache, pub/sub, feature serving |
| Memcached | Simple caching |
| Apache Ignite | Distributed cache + compute |

### File Storage (POSIX)
> Rarely used for analytics, more for shared access

| Cloud | Service |
|-------|---------|
| Azure | Azure Files |
| AWS | EFS (Elastic File System) |
| GCP | Filestore |

---

## 2. Databases

### OLTP (Transactional Databases)
> Used for **applications, CDC sources, operational data**

| Category | Databases |
|----------|-----------|
| **Open Source** | PostgreSQL ⭐, MySQL, MariaDB |
| **Commercial** | Oracle, SQL Server |
| **Cloud Managed** | Azure SQL, AWS RDS, Cloud SQL (GCP) |
| **Serverless** | Aurora Serverless, Azure SQL Serverless |

### OLAP / Analytical Warehouses
> Used for **BI, dashboards, complex analytics**

| Cloud | Service | Notes |
|-------|---------|-------|
| **Multi-Cloud** | **Snowflake** ⭐ | Most popular cloud DW |
| **Azure** | Synapse Analytics | Integrated with Power BI |
| **AWS** | **Redshift** | Columnar, massively parallel |
| **AWS** | Athena | Serverless query on S3 |
| **GCP** | **BigQuery** ⭐ | Serverless, highly scalable |
| **Open Source** | ClickHouse | Fast OLAP, open source |
| **Open Source** | Apache Druid | Real-time analytics |
| **Open Source** | Apache Pinot | User-facing analytics |
| **Open Source** | DuckDB | In-process OLAP (local analytics) |

### NoSQL Databases
> Used for **scale, semi-structured, low-latency serving**

| Type | Databases |
|------|-----------|
| **Document** | MongoDB ⭐, Couchbase, DocumentDB |
| **Wide-Column** | Cassandra, HBase, ScyllaDB |
| **Key-Value** | DynamoDB ⭐, CosmosDB, Redis |
| **Time-Series** | InfluxDB, TimescaleDB, QuestDB |

### Graph Databases
> Used for **recommendations, fraud detection, knowledge graphs**

| Database | Notes |
|----------|-------|
| **Neo4j** ⭐ | Most popular graph DB |
| JanusGraph | Distributed graph |
| Amazon Neptune | Managed graph |
| TigerGraph | Enterprise graph |

---

## 3. File & Table Formats

### Columnar Formats (Analytics)
> Used in **data lakes for analytics workloads**

| Format | Notes |
|--------|-------|
| **Parquet** ⭐ | Industry standard, best compression |
| ORC | Optimized for Hive |
| **Avro** | Schema evolution, streaming (row-based but analytics-friendly) |

### Row-Based Formats (Ingestion)
> Used for **sources, APIs, interchange**

| Format | Notes |
|--------|-------|
| CSV | Simple, universal |
| JSON | APIs, semi-structured |
| XML | Legacy systems |
| NDJSON | Newline-delimited JSON (streaming) |

### Table Formats ⭐ (CRITICAL for interviews)
> Used for **ACID transactions, time travel, schema evolution in data lakes**

| Format | Notes |
|--------|-------|
| **Delta Lake** ⭐ | Databricks, most widely adopted |
| **Apache Iceberg** ⭐ | Netflix origin, open standard |
| Apache Hudi | Uber origin, CDC-optimized |

**Why Table Formats Matter:**
- ACID transactions on data lakes
- Time travel / versioning
- Schema evolution
- Partition evolution
- Merge/Upsert operations

---

## 4. Batch Processing

### Distributed Compute Engines
> Used for **ETL, ELT, backfills, ML training**

| Cloud | Service | Notes |
|-------|---------|-------|
| **Multi-Cloud** | **Databricks** ⭐ | Unified analytics, Spark-based |
| **Azure** | Synapse Spark | Integrated with Synapse |
| **AWS** | **EMR** | Managed Hadoop/Spark |
| **AWS** | **Glue** | Serverless Spark ETL |
| **GCP** | **Dataproc** | Managed Spark/Hadoop |
| **GCP** | Dataflow | Apache Beam-based |
| **Open Source** | **Apache Spark** ⭐ | Industry standard |
| **Open Source** | Apache Beam | Unified batch/stream API |
| **Open Source** | Dask | Python-native parallel computing |
| **Open Source** | Ray | Distributed Python |
| **Legacy** | Hadoop MapReduce | Rarely used now |

---

## 5. Streaming & Messaging

### Message Brokers / Event Ingestion
> Used for **event ingestion, buffering, decoupling**

| Cloud | Service | Notes |
|-------|---------|-------|
| **Azure** | Event Hubs | Kafka-compatible |
| **Azure** | Service Bus | Enterprise messaging |
| **Azure** | IoT Hub | IoT device ingestion |
| **AWS** | Kinesis Data Streams | Real-time ingestion |
| **AWS** | Kinesis Firehose | Delivery to S3/Redshift |
| **AWS** | MSK | Managed Kafka |
| **AWS** | SQS | Simple queue (not streaming) |
| **GCP** | Pub/Sub ⭐ | Highly scalable messaging |
| **Open Source** | **Apache Kafka** ⭐ | Industry standard |
| **Open Source** | Apache Pulsar | Multi-tenancy, geo-replication |
| **Open Source** | RabbitMQ | Traditional message broker |
| **Open Source** | NATS | Lightweight, cloud-native |

### Stream Processing Engines
> Used for **stateful real-time computation, windowing, CEP**

| Engine | Notes |
|--------|-------|
| **Apache Flink** ⭐ | True streaming, low latency, exactly-once |
| **Spark Structured Streaming** | Micro-batch, good for existing Spark teams |
| Kafka Streams | Embedded in apps, no separate cluster |
| Azure Stream Analytics | Serverless, SQL-like |
| AWS Kinesis Data Analytics | Managed Flink |
| Apache Storm | Legacy |
| Apache Samza | LinkedIn origin |

---

## 6. Orchestration

### Workflow Orchestration
> Used for **scheduling, dependencies, retries, DAGs**

| Cloud | Service | Notes |
|-------|---------|-------|
| **Azure** | **Data Factory** ⭐ | Native Azure orchestration |
| **Azure** | Logic Apps | Low-code integration |
| **AWS** | Step Functions | State machine workflows |
| **AWS** | MWAA | Managed Airflow |
| **GCP** | Cloud Composer | Managed Airflow |
| **Open Source** | **Apache Airflow** ⭐ | Industry standard |
| **Open Source** | **Dagster** ⭐ | Modern, asset-based |
| **Open Source** | **Prefect** | Python-native, cloud hybrid |
| **Open Source** | Luigi | Spotify origin, legacy |
| **Open Source** | Argo Workflows | Kubernetes-native |
| **Open Source** | Temporal | Long-running workflows |

### Event-Driven Triggers (NOT orchestration)
> Used for **reactive pipelines, triggers**

| Cloud | Service |
|-------|---------|
| Azure | Event Grid |
| AWS | EventBridge, SNS, Lambda |
| GCP | Cloud Functions, Eventarc |

---

## 7. ETL / ELT Tools

### Data Movement & Ingestion
> Used for **extracting from sources, loading to destinations**

| Category | Tools | Notes |
|----------|-------|-------|
| **Commercial SaaS** | **Fivetran** ⭐ | Pre-built connectors, managed |
| **Commercial SaaS** | Stitch | Acquired by Talend |
| **Commercial SaaS** | Matillion | Cloud-native ETL |
| **Commercial** | Informatica | Enterprise legacy |
| **Commercial** | Talend | Open core |
| **Open Source** | **Airbyte** ⭐ | Open-source Fivetran alternative |
| **Open Source** | Singer | Tap/Target protocol |
| **Open Source** | Meltano | GitLab origin |

### Transformation (T in ELT)
> Used for **SQL-first transformations in warehouse**

| Tool | Notes |
|------|-------|
| **dbt** ⭐ | Industry standard for SQL transformations |
| SQLMesh | dbt alternative, incremental by default |
| Coalesce | Visual dbt-like |

---

## 8. Data Quality

### Data Quality Frameworks
> Used for **validation, testing, profiling**

| Tool | Notes |
|------|-------|
| **Great Expectations** ⭐ | Python-based, most popular |
| **Soda** ⭐ | SQL-first, SodaCL language |
| **dbt tests** | Built into dbt |
| Deequ | AWS/Spark-based (Amazon) |
| Monte Carlo | Commercial observability |
| Datafold | Data diff, regression testing |

### Data Observability
> Used for **anomaly detection, freshness, schema changes**

| Tool | Notes |
|------|-------|
| Monte Carlo | Pioneer in data observability |
| Bigeye | ML-based anomaly detection |
| Acceldata | Enterprise observability |
| Metaplane | Lightweight observability |

---

## 9. Data Governance & Catalog

### Data Catalogs
> Used for **discovery, documentation, search**

| Category | Tools | Notes |
|----------|-------|-------|
| **Cloud-Native** | **Unity Catalog** ⭐ | Databricks, unified governance |
| **Cloud-Native** | AWS Glue Catalog | S3/Athena metadata |
| **Cloud-Native** | Azure Purview | Microsoft governance |
| **Cloud-Native** | Google Data Catalog | GCP |
| **Open Source** | **DataHub** ⭐ | LinkedIn origin |
| **Open Source** | Apache Atlas | Hadoop ecosystem |
| **Open Source** | Marquez | Lineage-focused |
| **Commercial** | Atlan | Modern data workspace |
| **Commercial** | Collibra | Enterprise governance |
| **Commercial** | Alation | ML-powered catalog |

### Data Lineage
> Used for **impact analysis, debugging, compliance**

| Tool | Notes |
|------|-------|
| **OpenLineage** ⭐ | Open standard for lineage |
| Marquez | Reference implementation |
| Databricks lineage | Built into Unity Catalog |
| dbt lineage | Built into dbt |
| Atlan, Collibra | Commercial |

### Access Control
> Used for **fine-grained permissions, masking**

| Tool | Notes |
|------|-------|
| Unity Catalog | Databricks RBAC |
| Lake Formation | AWS fine-grained access |
| Apache Ranger | Hadoop ecosystem |

---

## 10. CDC & Data Replication

### Change Data Capture
> Used for **real-time database replication, event sourcing**

| Category | Tools | Notes |
|----------|-------|-------|
| **Open Source** | **Debezium** ⭐ | Kafka-based CDC, most popular |
| **Open Source** | Maxwell | MySQL CDC |
| **AWS** | DMS | Database Migration Service |
| **GCP** | Datastream | Serverless CDC |
| **Azure** | Data Factory CDC | Change tracking support |
| **Commercial** | Striim | Enterprise CDC |
| **Commercial** | Qlik Replicate | Attunity |

---

## 11. ML & Feature Stores

### Feature Stores
> Used for **ML feature reuse, point-in-time correctness**

| Category | Tools | Notes |
|----------|-------|-------|
| **Open Source** | **Feast** ⭐ | Most popular open-source |
| **Open Source** | Hopsworks | Full ML platform |
| **AWS** | SageMaker Feature Store | |
| **GCP** | Vertex AI Feature Store | |
| **Azure** | Azure ML Feature Store | |
| **Databricks** | Feature Engineering | Unity Catalog-based |
| **Commercial** | Tecton | Enterprise feature platform |

### ML Platforms & Experiment Tracking
> Used for **training, tracking, deployment**

| Category | Tools | Notes |
|----------|-------|-------|
| **Open Source** | **MLflow** ⭐ | Experiment tracking, model registry |
| **Open Source** | Kubeflow | Kubernetes ML |
| **Open Source** | Weights & Biases | Experiment tracking |
| **AWS** | SageMaker | Full ML lifecycle |
| **GCP** | Vertex AI | |
| **Azure** | Azure ML | |
| **Databricks** | MLflow + Model Serving | |

---

## 12. BI & Visualization

### Business Intelligence Tools
> Used for **dashboards, reports, self-service analytics**

| Category | Tools | Notes |
|----------|-------|-------|
| **Commercial** | **Power BI** ⭐ | Microsoft, Azure integration |
| **Commercial** | **Tableau** ⭐ | Industry standard |
| **Commercial** | **Looker** | GCP, LookML |
| **Commercial** | Qlik | Associative engine |
| **AWS** | QuickSight | Serverless BI |
| **Open Source** | **Metabase** ⭐ | Simple, self-hosted |
| **Open Source** | **Apache Superset** | Full-featured, Airbnb origin |
| **Open Source** | Redash | Query-based dashboards |
| **Open Source** | Grafana | Metrics/monitoring dashboards |

---

## 13. Monitoring & Observability

### Infrastructure Monitoring
> Used for **cluster health, job monitoring**

| Tool | Notes |
|------|-------|
| **Prometheus + Grafana** ⭐ | Open-source standard |
| Datadog | Full-stack observability |
| New Relic | APM + infrastructure |
| CloudWatch | AWS native |
| Azure Monitor | Azure native |
| Stackdriver | GCP native |

### Pipeline Monitoring
> Used for **job SLAs, failures, freshness**

| Tool | Notes |
|------|-------|
| Airflow UI | Built-in monitoring |
| Datadog integrations | Airflow, Spark metrics |
| Monte Carlo | Data pipeline health |
| Elementary | dbt observability |

---

## 14. Infrastructure & DevOps

### Infrastructure as Code
> Used for **reproducible infrastructure**

| Tool | Notes |
|------|-------|
| **Terraform** ⭐ | Multi-cloud IaC |
| AWS CloudFormation | AWS-native |
| Azure ARM/Bicep | Azure-native |
| Pulumi | Programming language IaC |

### Containerization & Orchestration
> Used for **deployment, scaling**

| Tool | Notes |
|------|-------|
| **Docker** ⭐ | Container runtime |
| **Kubernetes** ⭐ | Container orchestration |
| EKS / AKS / GKE | Managed Kubernetes |
| Helm | Kubernetes package manager |

### CI/CD
> Used for **automated deployment**

| Tool | Notes |
|------|-------|
| GitHub Actions ⭐ | Git-native CI/CD |
| GitLab CI | Full DevOps platform |
| Azure DevOps | Microsoft ecosystem |
| Jenkins | Traditional, self-hosted |
| CircleCI | SaaS CI/CD |

### Secret Management
> Used for **credentials, API keys**

| Tool | Notes |
|------|-------|
| HashiCorp Vault ⭐ | Industry standard |
| AWS Secrets Manager | AWS native |
| Azure Key Vault | Azure native |
| GCP Secret Manager | GCP native |

---

## 15. Programming & Libraries

### Languages
> Core languages for data engineering

| Language | Use Case |
|----------|----------|
| **Python** ⭐ | Primary DE language |
| **SQL** ⭐ | Data transformation |
| Scala | Spark native |
| Java | Hadoop/Kafka ecosystem |
| Go | Infrastructure tools |

### Python Libraries
> Essential Python packages

| Category | Libraries |
|----------|-----------|
| **DataFrames** | **Pandas** ⭐, Polars, Vaex |
| **Spark** | **PySpark** ⭐ |
| **APIs** | requests, httpx |
| **Connectors** | sqlalchemy, psycopg2, boto3, azure-storage-blob |
| **Schema** | pydantic, marshmallow |
| **Testing** | pytest, unittest |
| **CLI** | click, typer, argparse |

---

## Quick Reference: Cloud Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AWS vs AZURE vs GCP COMPARISON                           │
├───────────────┬──────────────────┬──────────────────┬──────────────────────┤
│ Component     │ AWS              │ Azure            │ GCP                  │
├───────────────┼──────────────────┼──────────────────┼──────────────────────┤
│ Object Store  │ S3               │ ADLS Gen2        │ GCS                  │
│ Warehouse     │ Redshift         │ Synapse          │ BigQuery             │
│ Spark         │ EMR, Glue        │ Synapse, HDI     │ Dataproc             │
│ Streaming     │ Kinesis, MSK     │ Event Hubs       │ Pub/Sub, Dataflow    │
│ Orchestration │ Step Functions   │ Data Factory     │ Composer             │
│ Serverless    │ Lambda, Glue     │ Functions, ADF   │ Cloud Functions      │
│ ML Platform   │ SageMaker        │ Azure ML         │ Vertex AI            │
│ BI            │ QuickSight       │ Power BI         │ Looker               │
│ Catalog       │ Glue Catalog     │ Purview          │ Data Catalog         │
│ CDC           │ DMS              │ ADF CDC          │ Datastream           │
└───────────────┴──────────────────┴──────────────────┴──────────────────────┘
```

---

## Interview Signal: High-Value Tools to Know

```
⭐ MUST KNOW (High Interview Signal)
├─ Spark / PySpark / Databricks
├─ Delta Lake / Iceberg
├─ Kafka / Flink
├─ Airflow / dbt
├─ Snowflake / BigQuery
├─ Great Expectations / Soda
└─ Unity Catalog / DataHub

✅ GOOD TO KNOW (Medium Signal)
├─ Debezium (CDC)
├─ Feast (Feature Store)
├─ MLflow (ML Ops)
├─ Terraform (IaC)
└─ Dagster / Prefect (Modern orchestration)
```
