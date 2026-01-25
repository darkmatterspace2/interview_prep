# Azure Databricks Interview Questions

## Section 1: Architecture & Compute

### Q1: Job Cluster vs All-Purpose Cluster?
**Answer**:
*   **All-Purpose Cluster**: Manually created for interactive analysis (Notebooks). Cost refers to "Standard" pricing. Can be shared by multiple users.
*   **Job Cluster**: Created *automatically* when a Job starts and terminates when it ends. Significantly cheaper (approx 50% less) than All-Purpose. Always use this for production pipelines.

### Q2: What are Instance Pools?
**Answer**:
A set of idle, pre-warmed instances (VMs). 
*   **Problem**: Starting a cluster takes 5-10 minutes (VM provisioning).
*   **Solution**: Pools keep VMs ready. Cluster start-up time drops to < 10 seconds. You pay for the VMs (cloud cost) while they idle, but not the Databricks DBU cost.

### Q3: What is the Photon Engine?
**Answer**:
A native vectorized execution engine written in C++ (instead of JVM).
*   Replaces the traditional Spark Execution Engine.
*   Speeds up SQL queries and DataFrame operations (filter, join, agg) by 2x-10x.
*   Price is slightly higher but total TCO is lower due to faster completion.

### Q4: Driver Node vs Worker Node?
**Answer**:
*   **Driver**: The "Brain". Maintains the SparkSession, translates code to DAGs, schedules tasks, and collects results (`collect()`). Memory overflow here causes OOM.
*   **Worker**: The "Muscle". Executes tasks (Task logic) and stores data partitions.

### Q5: Standard vs Premium Workspace?
**Answer**:
*   **Standard**: Basic Role-Based Access Control (RBAC). No fine-grained data security.
*   **Premium**: Required for **Unity Catalog**, Credential Passthrough, Dynamic Partition Pruning, and Audit Logs.

---

## Section 2: Unity Catalog & Governance

### Q6: What is Unity Catalog (UC)?
**Answer**:
A unified governance solution for Data & AI.
*   **Centralized Metadata**: One Metastore for all workspaces in a region.
*   **3-Level Namespace**: `Catalog.Schema.Table`.
*   **Data Lineage**: Automatically tracks table/column level lineage.
*   **Fine-grained ACL**: `GRANT SELECT ON TABLE sales TO group analysts`.

### Q7: Managed Table vs External Table in UC?
**Answer**:
*   **Managed Table**: Data is stored in the "Managed Storage Account" (Root bucket) defined in the Metastore. Dropping the table *deletes* the underlying data files.
*   **External Table**: Data is stored in an external storage container (e.g., ADLS Gen2). You provide the path. Dropping the table *only deletes metadata*; files remain.

### Q8: What are Storage Credentials and External Locations?
**Answer**:
*   **Storage Credential**: Secure object holding specific Managed Identity / Service Principal details to access ADLS.
*   **External Location**: Maps a Storage Path (`abfss://...`) to a Storage Credential. Used to govern *who* can create External Tables.

### Q9: Difference between Hive Metastore and Unity Catalog?
**Answer**:
*   **Hive (Legacy)**: Workspace-local. Permissions defined at cluster level (unsafe). No lineage.
*   **Unity Catalog**: Account-level. Permissions defined on data objects (SQL). Cross-workspace sharing.

### Q10: How to share data across different Databricks accounts?
**Answer**:
Use **Delta Sharing**.
*   An open protocol included in Unity Catalog.
*   Allows sharing tables with external organizations (even if they don't use Databricks) securely without file replication.

---

## Section 3: Data Engineering Implementation

### Q11: How to implement SCD Type 1 in Delta Lake?
**Answer**:
Use `MERGE INTO`.
```sql
MERGE INTO target t USING source s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET t.name = s.name, t.amount = s.amount
WHEN NOT MATCHED THEN INSERT *
```

### Q12: How to implement SCD Type 2 (History)?
**Answer**:
Use `MERGE INTO` with advanced logic.
1.  Mark old record as inactive (`UPDATE SET isActive = false, endDate = current_date()`).
2.  Insert new record (`INSERT (id, name, isActive, startDate) VALUES (s.id, s.name, true, current_date())`).
*   Requires matching on `t.id = s.id AND t.isActive = true`.

### Q13: How to pass parameters to a Databricks Notebook?
**Answer**:
Use **Widgets**.
*   **Create**: `dbutils.widgets.text("env", "dev")`.
*   **Read**: `env = dbutils.widgets.get("env")`.
*   **Pass from ADF**: In Databricks Activity -> Base Parameters -> Key: `env`, Value: `prod`.

### Q14: What is a "Bundle" (Databricks Asset Bundles - DABs)?
**Answer**:
A tool to define infrastructure and code as project files (YAML) for CI/CD.
*   Replaces the UI-based workflow deployment.
*   Define Jobs, Pipelines, and Clusters as code.
*   Deploy using CLI: `databricks bundle deploy -t prod`.

### Q15: How to handle Schema Evolution?
**Answer**:
*   **Append Mode**: `option("mergeSchema", "true")`. Adds new columns to the table schema automatically.
*   **Schema Enforcement**: By default, Delta throws error if schema mismatches to prevent corruption.

### Q16: How to delete old data to save cost?
**Answer**:
Use `VACUUM`.
*   `VACUUM table_name RETAIN 168 HOURS;`
*   Deletes physical files that are no longer referenced by the transaction log and are older than retention period (default 7 days).
*   **Warning**: You cannot Time Travel back to versions before the Vacuum.

---

## Section 4: Performance Optimization

### Q17: What is Z-Ordering?
**Answer**:
A technique to co-locate related information in the same set of files.
*   `OPTIMIZE table_name ZORDER BY (col1, col2)`
*   Used for columns frequently used in `WHERE` clauses (High cardinality like ID, Timestamp).
*   Enables extremely effective **Data Skipping** (read 2 files instead of 100).

### Q18: Partitioning vs Z-Ordering?
**Answer**:
*   **Partitioning**: Physical folder separation. Good for Low Cardinality (Date, Region). *Don't partition < 1TB tables*.
*   **Z-Ordering**: File-internal organization. Good for High Cardinality (CustomerID). Use when tables are medium-sized or partition columns have too many unique values.

### Q19: What is Disk Cache (formerly Delta Cache)?
**Answer**:
Uses local SSDs on the Worker nodes to cache remote data (Parquet files) for faster subsequent reads.
*   **Difference from Spark Cache**: Spark Cache (`.cache()`) stores data in RAM (and can OOM). Disk Cache stores on SSD (safe).
*   Enabled by default on certain worker types (Standard_L series).

### Q20: Broadcast Hash Join?
**Answer**:
Optimization for **Large Table x Small Table** join.
*   Spark sends the small table to every executor node (Broadcast).
*   Avoids "Shuffling" the large table (expensive network transfer).
*   Hint: `df.join(F.broadcast(small_df), "id")`.

### Q21: What is Skew Join optimization?
**Answer**:
When one key has way more data than others (e.g., "NULL" key).
*   Spark splits the skewed partition into smaller sub-partitions.
*   Hint: `option("skewJoin", "true")` (Enabled by default in Databricks Runtime).

---

## Section 5: Advanced & General

### Q22: Delta Lake vs Parquet?
**Answer**:
Parquet is just the file format. Delta Lake is the **Transaction Log** (ACID) on top of Parquet.
*   Delta adds: Time Travel, ACID Transactions, Schema Enforcement, Merge/Update support.

### Q23: How to interact with Databricks using API?
**Answer**:
**Databricks REST API**.
*   Manage clusters (create/delete), start jobs, upload files (DBFS).
*   Auth: PAT Token or OAuth (Service Principal).
*   Example: `POST /api/2.1/jobs/run-now` to start a job externally.

### Q24: What is Auto Loader?
**Answer**:
Efficient way to ingest files incrementally from Cloud Storage.
*   Uses `spark.readStream.format("cloudFiles")`.
*   Automatically detects new files using event notifications (Queue) instead of listing directories (slow).
*   Handles Schema drift automatically (`cloudFiles.schemaLocation`).

### Q25: Explain "Optimize Write"?
**Answer**:
An automated shuffle before write to produce evenly sized files (e.g., 1GB each).
*   Prevents "Small File Problem" during ingestion.

### Q26: Secrets Management?
**Answer**:
Use **Secret Scopes**.
*   **Azure Key Vault Backed Scope**: Maps directly to AKV.
*   **Databricks Backed Scope**: Stored internally.
*   Access: `dbutils.secrets.get(scope = "my-scope", key = "db-pass")`.
*   Result is redacted as `[REDACTED]` in logs.

### Q27: Delta Live Tables (DLT)?
**Answer**:
A framework for building reliable pipelines using declarative syntax (SQL/Python).
*   Auto-manages infrastructure, retries, and dependencies.
*   **Expectations**: Built-in data quality rules (`CONSTRAINT valid_id EXPECT id IS NOT NULL`).

### Q28: How to clone a table?
**Answer**:
*   **Deep Clone**: Copies metadata + data files. Independent copy.
*   **Shallow Clone**: Copies metadata only. Points to original files. Fast/Cheap backup.

### Q29: What is the "Transaction Log" (_delta_log)?
**Answer**:
Single source of truth. Folder containing JSON files (`000.json`, `001.json`). Actions: AddFile, RemoveFile, Metadata.
*   Allows atomic reads (readers see snapshot X while writer creates snapshot X+1).

### Q30: How to handle dependency libraries?
**Answer**:
1.  **Cluster Libraries**: Install on cluster start (PyPI/Maven).
2.  **Notebook-scoped**: `%pip install pandas`. Isolate env for that notebook session.
