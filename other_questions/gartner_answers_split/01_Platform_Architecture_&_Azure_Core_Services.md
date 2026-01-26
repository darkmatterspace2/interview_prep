## 1. Platform Architecture & Azure Core Services

### 1. How would you design a **scalable Azure data platform** using Databricks, ADF, and Azure Storage for both batch and near-real-time workloads?
**STAR / Architectural Answer:**
"I adhere to the **Medallion Architecture (Bronze/Silver/Gold)** principles, typically implementing a **Lakehouse** pattern.
*   **Ingestion:** I use **ADF** specifically for lightweight orchestration and connector-based ingestion (e.g., from on-prem SQL or SaaS APIs) into the **Bronze** layer (Azure Data Lake Gen2) in its raw format. For near-real-time, I prefer **Event Hubs** coupled with **Spark Structured Streaming** in Databricks directly into Delta tables.
*   **Processing:** All transformation logic resides in **Databricks** (using Delta Live Tables or distinct jobs) to promote better CI/CD and unit testing compared to rigid ADF Data Flows.
*   **Storage:** ADLS Gen2 is the single source of truth. I enforce lifecycle management policies to move cold data to Cool/Archive tiers to optimize costs.
*   **Serving:** Gold data is exposed via **Unity Catalog** for governance, and usually synced to a **Serverless SQL Endpoint** for BI tools like Power BI, ensuring we don't lock concurrency on the engineering clusters."

### 2. When would you choose **ADF vs Azure Functions vs Databricks Jobs** in a data pipeline?
**Strategic Answer:**
"I follow a 'Right Tool for the Job' policy to avoid technical debt:
*   **ADF:** Best for **orchestration** and **data movement** (Copy Activity) where no complex transformation is needed. Itâ€™s low-code and has excellent connectors. I avoid using ADF Data Flows for complex logic as they are harder to version control and debug than code.
*   **Azure Functions:** Ideal for **event-driven, lightweight integration tasks** (e.g., triggering a pipeline when a file lands, calling a REST API to get a token, or simple parsing). If processing takes >5-10 mins or requires heavy compute, itâ€™s the wrong tool.
*   **Databricks Jobs:** The standard for **heavy data transformation (ETL/ELT)**. Any logic involving complex joins, aggregations, or ML inference belongs here. It allows for proper software engineering practices (testing, modularization) that ADF and Functions struggle with at scale."

### 3. Explain how youâ€™ve used **AKS** in data platforms. What workloads ran on it and why?
**Answer:**
"While Databricks allows model serving, **AKS (Azure Kubernetes Service)** is often more cost-effective and flexible for **high-concurrency, low-latency API serving** of ML models or custom microservices.
In my previous platform, we treated Databricks as the *training* engine. Once a model was registered in MLflow, a CI/CD pipeline containerized it and deployed it to AKS. This separated the **batch training compute** (Databricks) from the **24/7 inference compute** (AKS), allowing us to scale them independently using KEDA scalers based on request queue depth."

### 4. How do you architect **multi-environment setups (dev / test / prod)** in Azure for data platforms?
**Answer:**
"I strictly separate environments at the **Resource Group** or **Subscription** level to prevent cross-contamination.
*   **Infrastructure:** Provisioned via **Terraform**. This ensures Dev, Test, and Prod are identical in configuration (drift detection).
*   **Data:** Production data is **never** copied to Dev. We use synthetic data or strictly anonymized subsets for lower environments.
*   **Databricks:** Separate Workspaces per environment. Code is promoted via **Databricks Asset Bundles (DABs)** or Git integration.
*   **ADF:** We use the 'ADF utilities' npm package in our release pipeline to deploy ARM templates from the collaboration branch (Dev) to higher environments, overriding parameters (like KeyVault URLs) for each stage."

### 5. How do you manage **cost optimization** across Databricks clusters, ADF pipelines, and storage?
**Answer:**
"Cost governance is a proactive discipline, not reactive:
1.  **Databricks:** I enforce **Cluster Policies** to restrict max DBUs and require tagging (CostCenter, Project). I mandate **Job Clusters** for all automated workloads (much cheaper than All-Purpose) and use **Photon** only where the speedup justifies the premium. Spot instances are used for stateless, robust retryable jobs.
2.  **ADF:** I monitor Self-Hosted Integration Runtime (SHIR) node utilization to avoid over-provisioning.
3.  **Storage:** Lifecycle policies are non-negotiable. I also regularly review 'Unmanaged' Delta files using `VACUUM` commands to remove stale snapshots that bloat storage costs.
4.  **Monitoring:** I set up Azure Budget alerts at 50%, 75%, and 100% thresholds, sending notifications to the engineering leads."

### 6. What are common **failure points in Azure data platforms**, and how do you proactively monitor them?
**Answer:**
"Common failures include **Throttling** (Storage Account limits), **Spot Instance Evictions** in Databricks, and **SHIR connectivity** issues.
*   **Mitigation:** I design for retry-ability. ADF pipelines use exponential backoff policies.
*   **Monitoring:** I don't rely solely on 'Pipeline Failed' emails. I implement **Azure Monitor / Log Analytics** dashboards that track 'Data Freshness' (SLA breaches). If a critical table hasn't updated by 7 AM, PagerDuty is triggered, regardless of whether the specific job failed or simply hung."

---

