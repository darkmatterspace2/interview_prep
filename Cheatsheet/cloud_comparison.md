# Cloud Service Comparison Cheat Sheet

A quick reference mapping services across the three major cloud providers for interview preparation.

| Category | Service Function | **Microsoft Azure** | **Amazon Web Services (AWS)** | **Google Cloud Platform (GCP)** |
| :--- | :--- | :--- | :--- | :--- |
| **Compute** | Virtual Machines (IaaS) | Azure Virtual Machines | Amazon EC2 | Google Compute Engine |
| | Platform as a Service (PaaS) | Azure App Service | AWS Elastic Beanstalk | Google App Engine |
| | Serverless Functions | Azure Functions | AWS Lambda | Google Cloud Functions |
| | Object Storage (Blob) | Azure Blob Storage | Amazon S3 | Google Cloud Storage |
| **Storage** | Archive Storage | Blob Archive Tier | Amazon S3 Glacier | Archive Storage Class |
| | File Storage (SMB/NFS) | Azure Files | Amazon EFS / FSx | Google Cloud Filestore |
| | Disk Storage (Block) | Azure Managed Disks | Amazon EBS | Persistent Disk |
| **Containers** | Managed Kubernetes | Azure Kubernetes Service (AKS) | Amazon EKS | Google Kubernetes Engine (GKE) |
| | Container Registry | Azure Container Registry (ACR) | Amazon ECR | Google Container Registry (GCR) |
| | Container Instances (Serverless) | Azure Container Instances (ACI) | AWS Fargate | Cloud Run (Stateless) |
| **Database** | Relational (Managed) | Azure SQL Database / SQL Managed Instance | Amazon RDS / Aurora | Cloud SQL / Cloud Spanner |
| | NoSQL (Document/Key-Value) | Azure Cosmos DB | Amazon DynamoDB | Cloud Firestore / Bigtable |
| | In-Memory Caching | Azure Cache for Redis | Amazon ElastiCache | Cloud Memorystore |
| **Data & Analytics** | Data Warehouse | Azure Synapse Analytics | Amazon Redshift | Google BigQuery |
| | Big Data Processing (Hadoop/Spark) | Azure Databricks / HDInsight | Amazon EMR | Google Cloud Dataproc |
| | ETL / Data Integration | Azure Data Factory (ADF) | AWS Glue | Cloud Dataflow / Data Fusion |
| | Real-Time Streaming | Azure Event Hubs / Stream Analytics | Amazon Kinesis | Google Pub/Sub / Dataflow |
| | Data Lake | Data Lake Storage Gen2 (ADLS) | S3 (Lake Formation) | Cloud Storage |
| **Messaging** | Message Queue | Azure Service Bus | Amazon SQS | Google Pub/Sub |
| | Pub/Sub Topic | Azure Service Bus Topics | Amazon SNS | Google Pub/Sub |
| **Networking** | Virtual Network | Azure VNet | Amazon VPC | Google Cloud VPC |
| | Load Balancing | Azure Load Balancer / App Gateway | ELB / ALB / NLB | Cloud Load Balancing |
| | DNS Management | Azure DNS | Amazon Route 53 | Cloud DNS |
| | Content Delivery Network | Azure CDN | Amazon CloudFront | Cloud CDN |
| **DevOps & Mgmt** | Infrastructure as Code | ARM Templates / Bicep | AWS CloudFormation | Google Cloud Deployment Manager |
| | Monitoring & Logging | Azure Monitor / Log Analytics | Amazon CloudWatch | Google Cloud Operations (Stackdriver) |
| | Identity Management | Microsoft Entra ID (formerly Azure AD) | AWS IAM | Cloud IAM |
| | Secret Management | Azure Key Vault | AWS Secrets Manager / Parameter Store | Secret Manager |

## Key Differences for Interviews

1.  **Scope**: Azure resources are grouped in **Resource Groups**, whereas AWS uses **Tags** loosely but relies on region/account boundaries. GCP uses **Projects**.
2.  **Storage**: Azure ADLS Gen2 is unique because it combines Blob storage with a true *Hierarchical Filesystem* (folders), which S3 only emulates (until recently with S3 Express/Directory buckets).
3.  **Hybrid**: Azure has strong hybrid focus with **Azure Arc** (manage on-prem K8s/Servers from cloud). AWS has **Outposts**. GCP has **Anthos**.
