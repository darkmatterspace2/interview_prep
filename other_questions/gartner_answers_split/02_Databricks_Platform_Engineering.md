## 2. Databricks Platform Engineering

### 1. How do you manage **Databricks workspace governance** across multiple teams?
**Answer:**
"I treat the Platform as a Product. I use **Unity Catalog (UC)** as the central governance layer.
*   **Metastore:** One Metastore per region, attached to all workspaces (Dev/Test/Prod).
*   **Catalogs:** Segregated by Business Unit or Domain (e.g., `Finance_Catalog`, `Marketing_Catalog`).
*   **Access Control:** We do NOT assign permissions to users directly. All access is via **Azure AD (Entra ID) Groups**.
*   **Cluster Policies:** I define 'T-Shirt size' policies (Small, Medium, Large) effectively preventing users from spinning up massive GPU clusters without approval."

### 2. Explain your approach to **cluster policies, job clusters vs interactive clusters**.
**Answer:**
"This is critical for cost control.
*   **Policies:** I implement a 'Personal Compute' policy for interactive analysis that restricts users to Single Node clusters or very small autoscaling ranges to prevent runaway costs.
*   **Job vs. Interactive:** Interactive (All-Purpose) clusters are *only* for development and debugging. **100% of production workloads must run on Job Clusters**. Job clusters are ephemeral, isolated, and significantly cheaper (approx. 40-50% less). I enforce this via CI/CD; the deployment pipeline will reject any job pointing to an existing interactive cluster ID."

### 3. How do you handle **Databricks runtime upgrades** without breaking pipelines?
**Answer:**
"We decouple the Runtime version from the job definition where possible, but realistically, upgrades require testing.
1.  **LTS Policy:** We stick to **LTS (Long Term Support)** versions (e.g., 15.4 LTS) and only upgrade when the next LTS is stable.
2.  **Canary Testing:** When a new runtime is selected, we run a subset of non-critical 'Canary' pipelines on the new version in Non-Prod for a week.
3.  **Regression Suite:** We run our standard unit and integration tests.
4.  **Rollout:** We update the standard 'Job Cluster Policy' to the new version, forcing new runs to pick it up, while keeping a 'Legacy' policy available for immediate rollback if edge cases appear."

### 4. How do you implement **Unity Catalog or equivalent governance** in Databricks?
**Answer:**
"Migration to Unity Catalog is a priority for modern platforms.
*   **Identity:** SCIM integration with Azure Active Directory.
*   **Data Lineage:** UC provides this out-of-the-box. I ensure all jobs leverage UC-enabled clusters so we capture column-level lineage.
*   **External Locations:** We stop using access keys or SAS tokens in code. We set up **Storage Credentials** and **External Locations** in UC, granting access to specific Service Principals. This removes all secrets from notebooks."

### 5. How do you manage **secrets, service principals, and credential passthrough**?
**Answer:**
"Hardcoded credentials are a firing offense.
*   **Azure Key Vault (AKV):** All secrets live here.
*   **Databricks Secret Scopes:** We create Key Vault-backed secret scopes.
*   **Service Principals:** Pipelines run as Service Principals, not users.
*   **Credential Passthrough:** We are moving *away* from this in favor of **Unity Catalog** standard authentication, which is more secure and works better with SQL Endpoints and non-interactive jobs."

### 6. What performance tuning techniques have you applied in Databricks for large datasets?
**Answer:**
"Performance tuning is an iterative process. My checklist:
1.  **File Sizing:** The 'Small File Problem' is a killer. I use `OPTIMIZE` and `Z-ORDER` (on high-cardinality filter columns) regularly.
2.  **Shuffle Partitions:** Default is 200, which is often wrong. I use **Adaptive Query Execution (AQE)** which handles this dynamically in most modern runtimes.
3.  **Broadcasting:** For joins, I ensure small lookup tables are Broadcasted to avoid shuffling large fact tables.
4.  **Caching:** Disk Caching (formerly Delta Cache) is enabled on worker nodes for repeated reads.
5.  **Spill to Disk:** If I see heavy spill in the Spark UI, I upgrade leverage memory-optimized instances."

### 7. How do you ensure **platform reliability and SLAs** for Databricks users?
**Answer:**
"Reliability is improved through isolation and automation.
*   **Quotas:** We monitor Azure vCPU quotas to ensure we don't hit region limits during peak scale-up.
*   **Pools:** For latency-sensitive jobs, I use **Instance Pools** to reduce cluster startup time (though Serverless is making this less relevant).
*   **SLA Tracking:** We tag jobs with 'Tier-1', 'Tier-2'. Tier-1 failures trigger immediate PagerDuty alerts. We measure 'Time to Availability' and report it weekly."

---

