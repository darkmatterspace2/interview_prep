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
