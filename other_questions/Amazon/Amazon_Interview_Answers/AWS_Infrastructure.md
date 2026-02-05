# Amazon AWS Infrastructure Interview Questions

## Part 2: AWS Ecosystem

#### Scenario 1: S3 Partitioning for Athena
**Question:** How would you partition S3 data for a log ingestion pipeline receiving terabytes of data daily to optimize for Athena queries?
**Answer:**
*   **Strategy:** Partition by Date and potentially another high-cardinality filter key (e.g., `Region` or `ServiceID`).
*   **Path:** `s3://bucket/logs/region=us-east-1/date=2023-01-01/`
*   **File Size:** Ensure files are aggregated into chunks (e.g., 128MB - 1GB) and stored in **Parquet** format.
*   **Why:** Athena uses Hive-style partitioning. Queries filtering by `date` will query S3 only for that specific prefix, saving cost (scanned bytes) and time.

#### Scenario 2: Glue vs. EMR
**Question:** You need to run a daily ETL job. When would you choose AWS Glue over a persistent EMR cluster?
**Answer:**
*   **Choose AWS Glue (Serverless):**
    *   If the job is intermittent or periodic (once a day).
    *   If you don't want to manage infrastructure/patching.
    *   If the workload is relatively consistent.
*   **Choose EMR (Persistent/Transient):**
    *   If you have a customized stack (need specific versions of Hadoop/Spark/Presto not in Glue).
    *   If you have a 24/7 steady workload (Reserved Instances on EMR are cheaper than Glue).
    *   If you need massive scale (hundreds of nodes) with full control over tuning.

#### Scenario 3: Kinesis Data Streams vs Firehose
**Question:** Difference? Which one to just dump data into S3?
**Answer:**
*   **Kinesis Data Streams (KDS):** Real-time, low latency (sub-second). You must write code (Lambda/KCL) to consume it. Retains data for replay (default 24 hrs).
*   **Kinesis Data Firehose (KDF):** Near real-time (buffer of 60s or 1MB). Fully managed delivery service to destinations (S3, Redshift, Splunk).
*   **Choice:** Use **Firehose** to "just dump data into S3". It handles batching, compression (GZIP/Snappy), and format conversion (JSON -> Parquet) automatically with zero code.

#### Scenario 4: Infrastructure as Code (IaC)
**Question:** CloudFormation vs Terraform? State management?
**Answer:**
*   **Terraform:** Cloud-agnostic, huge provider ecosystem. Uses `terraform.tfstate` file to track resource state.
    *   *State Mgmt:* Store state in S3 (with Locking via DynamoDB) to allow team collaboration.
*   **CloudFormation:** Native to AWS. State is managed by AWS internally (Stack).
*   **Preference:** Terraform is generally preferred for flexibility, but CloudFormation is safer for strict AWS-only shops (no drift issues).
