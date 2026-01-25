# Azure Data Factory (ADF) Interview Questions

## Section 1: Core Concepts & Architecture

### Q1: What are the different types of Integration Runtimes (IR)?
**Answer**:
1.  **Azure IR**: Fully managed, auto-scaling. Used for copying data between Cloud stores (Blob -> SQL) using public endpoints.
2.  **Self-Hosted IR**: Installed on a local machine/VM inside a private network. Used to connect to **On-Premise** data (SQL Server, Oracle) or resources inside a private VNet.
3.  **Azure-SSIS IR**: Dedicated cluster to run legacy SSIS packages in the cloud.

### Q2: Copy Activity vs. Data Flow?
**Answer**:
*   **Copy Activity**: Optimized purely for **data movement** (Extract & Load). Fast, cheap, limited transformations (column mapping, type conversion). No Spark cluster needed.
*   **Mapping Data Flow**: Visual interface for **data transformation** (Transform). Runs on a managed Spark cluster behind the scenes. Can do Joins, Aggregates, Pivots, Window functions, and SCD logic.

### Q3: Trigger Types in ADF?
**Answer**:
1.  **Schedule Trigger**: Wall-clock time (e.g., "Every day at 8 AM").
2.  **Tumbling Window Trigger**: Slices time into discrete windows. Supports state (can depend on previous window) and heavy backfilling.
3.  **Event-Based Trigger**: Reacts to storage events (New Blob Created/Deleted) via Event Grid.
4.  **Custom Events Trigger**: Triggered by custom events on Event Grid.

### Q4: Pipeline vs Activity vs Dataset vs Linked Service?
**Answer**:
*   **Linked Service**: Connection String (The "Key").
*   **Dataset**: Reference to Data (The "Table/File").
*   **Activity**: Action to perform (The "Verb").
*   **Pipeline**: Logical grouping of activities (The "Sentence").

### Q5: Variables vs Parameters?
**Answer**:
*   **Parameters**: External values passed *into* the pipeline at runtime (e.g., `StartDATE`). Immutable during the run.
*   **Variables**: Internal values used to hold temporary state *during* the run. Can be changed using `Set Variable`.

---

## Section 2: Data Flows & Transformations (SCD)

### Q6: How do you implement SCD Type 1 (Overwrite) in Mapping Data Flow?
**Answer**:
Type 1 updates existing records vs inserts new ones (Upsert).
1.  **Source**: Read generic source.
2.  **Lookup/Join**: Match with Target table on Key.
3.  **Alter Row**: Use expression `Upsert if: true()`.
4.  **Sink**: Select "Allow Upsert" and specify "Key Columns".

### Q7: How do you implement SCD Type 2 (History Preservation) in ADF?
**Answer**:
Type 2 maintains history by adding `isActive`, `StartDate`, `EndDate` methods.
1.  **Join**: Join Source (New) with Sink (Existing) on Business Key.
2.  **Derived Column**: Create hashes (MD5) of columns to detect changes.
3.  **New Records**: Mark as Insert with `isActive=1`.
4.  **Changed Records (Old)**: Mark existing record in Sink as Update (`isActive=0`, `EndDate=Now`).
5.  **Changed Records (New)**: Insert new version as Insert (`isActive=1`, `StartDate=Now`).
6.  Use **Alter Row** strategies to route these to the Sink.

### Q8: What represents the "Alter Row" transformation?
**Answer**:
It tags rows with policies: **Insert**, **Update**, **Delete**, or **Upsert**.
*   *Example*: `Delete if year(TransactionDate) < 2020`.
*   These tags are enforced at the **Sink** step.

### Q9: How to optimize a Join in Data Flow?
**Answer**:
*   **Broadcast Join**: If one side is small (Reference table), load it entirely into memory to avoid shuffling.
*   **Partitioning**: Use "Hash Partitioning" on Join Keys to ensure related data stays on the same Spark node.

### Q10: What is the purpose of "Debug Mode" in Data Flow?
**Answer**:
It spins up a warm Spark cluster session. Allows interactive data preview at every step without running the full pipeline triggering overhead. Useful for development.

---

## Section 3: Performance Optimization

### Q11: How to optimize Copy Activity performance?
**Answer**:
1.  **DIUs (Data Integration Units)**: Increase DIUs for Azure IR (more CPU/Network).
2.  **Parallel Copies**: In Settings, increase "Max parallel copies" to read multiple files at once.
3.  **Staged Copy**: When loading into Snowflake/Synapse from On-prem, use Blob Storage as a staging area. (On-Prem -> Blob -> PolyBase -> Synapse) is faster than direct ODBC insert.

### Q12: How to handle copying millions of small files?
**Answer**:
Small files cause overhead.
*   **Zip/Merge**: Zip them at source if possible.
*   **Binary Dataset**: Treat them as binary to avoid parsing each one.
*   **Distcp**: Use specialized tools inside custom data flow logic or Databricks.

### Q13: What implies the "Degree of Copy Parallelism"?
**Answer**:
ADF determines how many threads to use based on the source/sink.
*   For **File Sources**, it's the number of files.
*   For **Partitioned Relational DBs**, mapping partitions to threads speeds up concurrent reads.

### Q14: Self-Hosted IR is slow. How to scale?
**Answer**:
1.  **Scale Up**: Add CPU/RAM to the VM.
2.  **Scale Out**: Install IR on up to 4 nodes in a cluster (Active-Active). ADF load balances the tasks.

### Q15: How to optimize Data Flow execution time?
**Answer**:
*   **Integration Runtime**: Use a **Memory Optimized** compute type (more RAM per core).
*   **TTL (Time To Live)**: Keep the cluster alive for sequential activities to avoid 5-min spin-up time per activity.

---

## Section 4: Advanced Scenarios & Logic

### Q16: How to handle REST API Pagination?
**Answer**:
In Copy Activity Source settings:
1.  **Pagination Rules**: Define the logic (e.g., `AbsoluteUrl = $.nextLink` or `QueryParameter.page = Range`).
2.  ADF loops automatically until the condition is met.

### Q17: lookup activity vs Get Metadata activity?
**Answer**:
*   **Lookup**: Reads the *content* of a file/table (e.g., "Get the last processed date"). Limited to 5000 rows / 4MB.
*   **Get Metadata**: Reads *attributes* of files (Size, Name, LastModified, ChildItems). Does not read content. Used for looping over file lists.

### Q18: Difference between ForEach and Filter activity?
**Answer**:
*   **Filter**: Filters an input array based on a condition, outputting a smaller array.
*   **ForEach**: Iterates over an array. Default runs in **Parallel** (up to 50 threads). Can be set to **Sequential**.

### Q19: How to restart a pipeline from a specific failed point?
**Answer**:
Before, you couldn't. Now, you can perform a **"Rerun from failure"** in the Monitor tab. It skips already succeeded activities and resumes state.

### Q20: How to handle errors (Try-Catch logic)?
**Answer**:
ADF doesn't have a Try-Catch block.
*   Use the **onFailure** path (Red arrow) from an activity (e.g., Copy) to an error handling activity (e.g., Send Notification / Log Error).
*   To ignore error and proceed, perform `onCompletion` or link `onFailure` to a dummy Wait activity.

### Q21: Usage of "Until" Activity?
**Answer**:
Do-While loop equivalent. Runs activities until a condition evaluates to true.
*   *Use Case*: Polling an API status endpoint waiting for `status == "COMPLETED"`.

### Q22: Custom Activity vs Azure Function Activity?
**Answer**:
*   **Azure Function**: Good for lightweight logic (C#, Python, Node) running in Serverless mode. Max timeout 10 mins (Consumption).
*   **Custom Activity**: Runs on an **Azure Batch** pool (VMs). Good for long-running, heavy computational scripts (e.g., proprietary executable).

### Q23: How to pass values from a Child Pipeline to Parent Pipeline?
**Answer**:
Note: Execute Pipeline doesn't natively return variables.
*   **Workaround**: Write the output to the database/file in Child, read it in Parent.
*   **New Feature**: "Set Pipeline Return Value" activity in Child. Parent accesses it via `activity('ExecuteChild').output.pipelineReturnValue.key`.

---

## Section 5: Integration & Security

### Q24: How to secure credentials?
**Answer**:
Use **Azure Key Vault**. Create a Linked Service to AKV, then inside data Linked Services, select "Azure Key Vault" for the password field and provide the Secret Name.

### Q25: Managed Identity (MSI) in ADF?
**Answer**:
ADF has its own AD Object ID.
*   Grant this Object ID access to resources (e.g., "Blob Data Contributor" on Storage Account).
*   Authentication happens via Azure Backbone without managing user/pass.

### Q26: CI/CD in ADF?
**Answer**:
1.  **Git Integration**: Connect to Azure DevOps/GitHub.
2.  **branches**: Develop in `main` or feature branch.
3.  **Publish**: Generates **ARM Templates** in `adf_publish` branch.
4.  **Release Pipeline**: Deploys these ARM templates to QA/Prod Resource Groups, overriding parameters (Connection Strings).

### Q27: How to utilize "Global Parameters"?
**Answer**:
Constants defined at the Factory level (e.g., `EnvName`, `DataLakeURL`).
*   Useful for CI/CD to override values across environments easily.
*   Scoped properly rather than repeating pipeline parameters.

### Q28: How to monitor pipelines externally?
**Answer**:
*   **Azure Monitor**: Send logs to Log Analytics Workspace.
*   **Alerts**: Create rules for "Failed Runs" to email/SMS.
*   **SDK**: Use Python/PowerShell SDK to query run status programmatically.

---

## Section 6: Real-World Scenarios

### Q29: Incremental Loading pattern?
**Answer**:
1.  **Watermark Table**: Store `LastLoadDate` in SQL.
2.  **Lookup**: Retrieve `LastLoadDate`.
3.  **Copy**: Source Query `SELECT * FROM Source WHERE ModDate > @LastLoadDate`.
4.  **Update**: On success, update Watermark Table with `MAX(ModDate)`.

### Q30: Handling Schema Drift?
**Answer**:
In Mapping Data Flow:
*   Check **"Allow Schema Drift"** in Source/Sink.
*   Use patterns like `byName()` or `byPosition()` to map columns dynamically.
*   Use **"Drifted Column"** feature to process columns that weren't defined at design time.

### Q31: How to execute a Databricks Notebook?
**Answer**:
Use **Databricks Notebook Activity**.
*   Requires a Linked Service to Databricks Workspace (Token/MSI).
*   Can pass parameters to Widgets in the notebook via `Base Parameters`.

### Q32: Limit concurrency of a pipeline?
**Answer**:
If a trigger runs every minute but pipeline takes 5 mins, they pile up.
*   **Pipeline Concurrency**: Settings -> Concurrency. Set to 1 for Singleton behavior.

### Q33: Secure Input/Output?
**Answer**:
In Activity settings, check **"Secure Input"** and **"Secure Output"**. This prevents sensitive data (like passwords or PII tokens) from appearing in the ADF Monitor logs in plain text.

### Q34: How to deduplicate data in ADF?
**Answer**:
Use **Mapping Data Flow**.
1.  **Aggregate** Transformation.
2.  Group By all columns (or Key columns).
3.  Aggregate function: `first(col)`.

### Q35: Copy data from REST API and add a timestamp column?
**Answer**:
Use **Additional Columns** feature in Copy Activity Source settings.
*   Name: `IngestDate`
*   Value: `$$NOW` (ADF System Variable).
