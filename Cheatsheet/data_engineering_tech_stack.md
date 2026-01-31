# Data Engineering Technology Stack

A categorized list of trending tools, languages, and frameworks used in modern Data Engineering projects.

## 1. Programming Languages
*   **Python**: The dominant language (Airflow, PySpark, Pandas).
*   **SQL**: Essential for transformation (dbt, Warehouse queries).
*   **Scala**: Native language of Spark, used for high-performance streaming.
*   **Java**: The foundation of the Hadoop ecosystem (Kafka, Flink).
*   **Rust / Go**: Emerging for high-performance tooling (Delta Lake Rs, Redpanda).

## 2. Distributed Storage & Formats
*   **File Formats**:
    *   **Parquet**: Columnar, high compression, ideal for OLAP/Spark.
    *   **Avro**: Row-based, schema evolution support, ideal for Streaming/Kafka.
    *   **ORC**: Optimized Row Columnar (often used with Hive).
    *   **JSON / CSV**: Common for interchange (landing zone).
*   **Table Formats (Lakehouse)**:
    *   **Delta Lake**: ACID transactions, Time Travel (Databricks).
    *   **Apache Iceberg**: Open standard, partition evolution (Netflix).
    *   **Apache Hudi**: Upserts/Incremental processing (Uber).
*   **Object Storage**:
    *   **AWS S3**
    *   **Azure Data Lake Storage Gen2 (ADLS)**
    *   **Google Cloud Storage (GCS)**

## 3. Streaming & Real-Time
*   **Apache Kafka**: The standard for event streaming.
*   **Confluent Platform**: Managed Kafka with Schema Registry, Connectors.
*   **Apache Flink**: Stateful stream processing (low latency).
*   **Spark Structured Streaming**: Micro-batch processing.
*   **Azure Event Hubs / AWS Kinesis / GCP Pub/Sub**: Cloud-native alternatives.

## 4. Big Data Processing (Compute)
*   **Apache Spark**: Unified engine for big data processing (Batch + Stream).
*   **Databricks**: Managed Spark platform + Lakehouse.
*   **Snowflake**: Cloud Data Warehouse (Separated Compute/Storage).
*   **Google BigQuery**: Serverless DWH.
*   **Azure Synapse Analytics**: Integrated Analytics (SQL + Spark).
*   **Hadoop (MapReduce/Hive)**: Legacy but still present in on-prem.

## 5. ETL Workflows & Orchestration
*   **Apache Airflow**: Python-based DAGs, industry standard.
*   **Azure Data Factory (ADF)**: GUI-based cloud ETL.
*   **Informatica / Talend**: Enterprise GUI ETL tools.
*   **dbt (data build tool)**: SQL-based transformation (T in ELT).
*   **Dagster / Prefect**: Next-gen orchestrators (Data-aware).

## 6. Databases (OLTP & NoSQL)
*   **PostgreSQL / MySQL**: Operational Relational DBs.
*   **Apache Cassandra / ScyllaDB**: Wide-column store for high write throughput.
*   **MongoDB**: Document store (JSON).
*   **Redis**: In-memory cache / Key-Value store.
*   **Elasticsearch / OpenSearch**: Search engine and log analytics.
*   **Neo4j**: Graph database.

## 7. Infrastructure as Code (IaC)
*   **Terraform**: Cloud-agnostic infrastructure provisioning.
*   **Ansible**: Configuration management.
*   **Azure Bicep / ARM Templates**: Azure-native IaC.
*   **AWS CloudFormation**: AWS-native IaC.
*   **Pulumi**: IaC using general-purpose languages (Python/TS).

## 8. CI/CD (DevOps)
*   **Jenkins**: The classic open-source CI server.
*   **GitHub Actions**: Integrated CI/CD in GitHub.
*   **Azure DevOps**: Pipelines, Boards, Repos (Enterprise favorite).
*   **GitLab CI**: Integrated DevOps platform.

## 9. Containerization & Virtualization
*   **Docker**: Container runtime.
*   **Kubernetes (K8s)**: Container orchestration (AKS/EKS/GKE).
*   **Helm**: Package manager for Kubernetes.

## 10. Data Governance & Quality
*   **Great Expectations**: Python library for data testing.
*   **Amundsen / DataHub**: Data Catalog and discovery.
*   **Apache Atlas**: Metadata management.

## 11. Trade-offs & Decision Matrix (When to use what?)
| Scenario | Option A | Option B | Decision / Trade-off |
| :--- | :--- | :--- | :--- |
| **Orchestration** | **Airflow** | **Databricks Workflows** | Use **Airflow** for complex, multi-system dependencies (AWS+GCP+OnPrem). Use **DB Workflows** if 100% of compute is in Databricks (Simpler, Cheaper). |
| **Storage Format** | **Parquet** | **Avro** | Use **Parquet** for OLAP (Read-heavy, Columnar). Use **Avro** for Kafka/Streaming (Write-heavy, Schema Evolution). |
| **Transformation** | **Spark** | **dbt (SQL)** | Use **Spark** for complex logic, ML, or massive scale (>10TB). Use **dbt** for warehouse-native transformations (Cleaner, accessible to analysts). |
| **Processing** | **Batch** | **Stream** | **Batch** is cheaper & simpler (Daily Reports). **Stream** (Flink/Spark SS) is for Fraud Detection/Real-time dashboards but costlier & harder to maintain. |
| **Data Lake** | **Iceberg** | **Delta Lake** | **Delta** is best if you are deep in Azure/Databricks ecosystem. **Iceberg** is more open, preferred by Netflix/Apple/AWS-native stacks. |

## 12. Industry Tech Stacks by Company Type

**1. The "Modern Data Stack" (Startups / Mid-Market)**
*   **Focus**: Velocity, Low Overhead, SQL-based.
*   **Stack**: Fivetran (Ingest) -> Snowflake/BigQuery (Warehousing) -> dbt (Transform) -> Looker/Metabase (BI).
*   **Why**: Zero infra management, scales well initially, easy to hire for.

**2. The "Azure Enterprise" (Large Non-Tech Corps)**
*   **Focus**: Security, Integration, Microsoft Ecosystem.
*   **Stack**: Azure Data Factory (Orchestration) -> ADLS Gen2 (Lake) -> Databricks (Complex Compute) -> Synapse/SQL DB (Serving) -> PowerBI.
*   **Why**: Deep integration with Active Directory, Office 365, and existing corporate contracts.

**3. The "Big Data / Streaming" (Uber/Netflix/LinkedIn)**
*   **Focus**: Scale, Latency, Custom Engineering.
*   **Stack**: Kafka (Bus) -> Flink (Stream Process) -> Hadoop/S3 (Deep Storage) -> Iceberg (Table Format) -> Trino/Presto (Interactive Query).
*   **Why**: Needs to handle Petabytes/day where off-the-shelf SaaS becomes too expensive or slow.

**4. The "Open Source / On-Prem" (Banks / Gov)**
*   **Focus**: Control, Cost, Security (Air-gapped).
*   **Stack**: NiFi (Ingest) -> MinIO (Storage) -> Spark on K8s (Compute) -> PostgreSQL/Greenplum.
*   **Why**: Data sovereignty requirements prevent cloud usage.
