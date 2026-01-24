# Azure Core Services for Data Engineering & DevOps

This guide covers essential Azure services frequently asked about in technical interviews.

## 1. Azure App Service
**Platform-as-a-Service (PaaS)** for hosting web applications, REST APIs, and mobile backends.

*   **Key Features**:
    *   **Fully Managed**: Auto-patching, load balancing, and scaling.
    *   **Deployment Slots**: Create a "Staging" slot, deploy code, then swap with "Production" (Zero Downtime).
    *   **Scaling**: Support for Manual (fixed count) or Auto-scaling (based on CPU/Memory).
*   **Use Case**: Hosting a Python/Node.js API that serves your ML model or frontend.
*   **Interview Tip**: Know the difference between **App Service Plan** (The computed resources/VM) and the **App Service** (The application running on it). Accessing App Service inside a VNet often requires "VNet Integration".

## 2. Azure Kubernetes Service (AKS)
**Managed Kubernetes** service that simplifies deploying and managing containerized applications.

*   **Key Features**:
    *   **Control Plane**: Managed by Azure (Free). You only pay for the Worker Nodes (VMs).
    *   **Integration**: Native integration with Azure Container Registry (ACR) and Azure Active Directory (RBAC).
    *   **Scaling**: Supports **Cluster Autoscaler** (adds nodes) and **Horizontal Pod Autoscaler** (adds pods).
*   **Use Case**: Running microservices architectures or heavy distributed jobs (Spark on K8s).
*   **Interview Tip**: Understand **Node Pools** (grouping VMs) and how **CNI Networking** allows pods to get real IP addresses from the VNet.

## 3. Azure Storage (Blob & ADLS Gen2)
The fundamental storage layer for the cloud.

*   **Types**:
    *   **Blob Storage**: Object storage (Images, Logs, Backups). Flat namespace.
    *   **Data Lake Storage Gen2 (ADLS Gen2)**: Built on top of Blob. Adds a **Hierarchical Namespace** (Folders/Directories). Critical for Hadoop/Spark performance.
*   **Access Tiers**:
    *   **Hot**: Frequent access (Higher storage cost, lower access cost).
    *   **Cool**: Infrequent access (> 30 days).
    *   **Archive**: Rare access (> 180 days). High latency to retrieve.
*   **Use Case**: Landing zone for ETL pipelines (ADF -> ADLS).
*   **Interview Tip**: Explain why ADLS Gen2 is better for Big Data than generic Blob (Atomic directory renames are O(1) in ADLS vs O(N) in Blob).

## 4. Azure Functions
**Serverless Compute** service. Run code snippets (Events) without managing infrastructure.

*   **Key Features**:
    *   **Triggers**: HTTP (API), Timer (Cron), Blob (New File), CosmosDB (Change Feed).
    *   **Bindings**: Declarative way to connect to data (e.g., Output Binding to write to SQL) without boilerplate code.
    *   **Plans**:
        *   **Consumption**: Pay per execution. Cold start potential.
        *   **Premium**: Pre-warmed instances (No cold start), VNet connectivity.
*   **Use Case**: Lightweight event processing (image resizing when uploaded) or glue code between services.
*   **Interview Tip**: Discuss **Durable Functions** for stateful workflows (e.g., Fan-out/Fan-in patterns).

## 5. Log Analytics (Azure Monitor)
Centralized repository for storing and querying logs.

*   **Key Features**:
    *   **KQL (Kusto Query Language)**: SQL-like language to query logs. Extremely fast.
    *   **Sources**: Collects logs from VMs, AKS, App Services, and custom apps.
    *   **Alerts**: Trigger emails/webhooks based on query results (e.g., "Error count > 5").
*   **Use Case**: Debugging application crashes or monitoring resource usage across the entire fleet.
*   **Interview Tip**: Know a basic KQL query: `AppTraces | where SeverityLevel == "Error" | summarize count() by bin(TimeGenerated, 1h)`.

## 6. Azure Data Factory (ADF)
**Cloud ETL Service** for data integration and orchestration.

*   **Key Concepts**:
    *   **Pipeline**: Logical grouping of activities.
    *   **Activity**: A step (Copy Data, Run Databricks Notebook, Call API).
    *   **Dataset**: Reference to data (e.g., "CSV in Blob").
    *   **Linked Service**: Connection string (credentials) to external systems (e.g., connection to Snowflake).
    *   **Integration Runtime (IR)**: The compute infrastructure.
        *   *Azure IR*: Cloud-to-Cloud.
        *   *Self-Hosted IR*: Connects to On-Premise data / Private VNet.
*   **Use Case**: Orchestrating the "E" (Extract) and "L" (Load) from On-Prem SQL to Cloud Data Lake.
*   **Interview Tip**: ADF is primarily an **Orchestrator**. It is not meant for heavy row-level transformation logic (use Databricks/Spark for that), although "Data Flows" in ADF provide a GUI for transformations.
