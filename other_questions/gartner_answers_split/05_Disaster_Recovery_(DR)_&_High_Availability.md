## 5. Disaster Recovery (DR) & High Availability

### 1. How do you design **DR for Databricks, ADF, and Storage**?
**Answer:**
"I implement an **Active-Passive** DR strategy for cost efficiency, with a 'Pilot Light' in the secondary region.
*   **Storage:** GRS (Geo-Redundant Storage) is the foundation. Data replicates asynchronously to the paired region.
*   **Code:** All code is in Git, so it's region-agnostic.
*   **ADF & Databricks:** We use Terraform to define these resources. In a DR event, we run a 'DR Deployment' pipeline that spins up the workspaces and factories in the secondary region (if not already there as a pilot light) and points them to the secondary storage endpoint."

### 2. What is your **RPO/RTO strategy** for data platforms?
**Answer:**
"These metrics must be defined by Business continuity needs, not just IT.
*   **RPO (Recovery Point Objective):** Determined by storage replication lag (GRS is usually < 15 mins).
*   **RTO (Recovery Time Objective):** Determined by automation. If we have a 'Warm Standby' (workspaces pre-provisioned), RTO is ~30 mins. If 'Cold Standby' (provision on demand), RTO can be 4-6 hours. I typically aim for RPO < 1 hour and RTO < 4 hours for critical reporting."

### 3. How do you handle **cross-region replication** for data lakes?
**Answer:**
"For Bronze/Silver/Gold data, I rely on Azure's native **GRS/RA-GRS**.
However, for Delta Tables, GRS replication ends up being 'Crash Consistent' but not always 'Application Consistent' due to the transaction log vs parquet file sync.
For *critical* tables, I prefer **Deep Clone** jobs that run nightly to copy the Delta table to the DR region explicitly. This ensures a transactionally consistent copy."

### 4. What components are hardest to recover in a data platform and why?
**Answer:**
"**Stateful** components are the hardest.
*   **The Metastore:** If using Hive Metastore (legacy), syncing the backing DB is painful. Unity Catalog simplifies this as it's a global account-level construct.
*   **In-flight Processing:** Resuming a streaming job exactly where it left off in a new region requires careful management of checkpoint locations (which must also be replicated)."

### 5. Have you executed a **real DR drill**? What did you learn?
**Answer:**
"Yes, we conduct bi-annual 'Game Days'.
A key learning was that **Secrets** were a single point of failure. We had Key Vaults replicating, but the RBAC permissions didn't carry over automatically. We had to update our Terraform to ensure the Service Principals had permission on the Secondary Key Vaults ahead of time."

---

