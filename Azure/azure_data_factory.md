# Azure Data Factory (ADF) Interview Questions

## Q1: What are the different types of Integration Runtimes (IR)?
**Answer**:
1.  **Azure IR**: Fully managed, auto-scaling. Used for copying data between Cloud stores (Blob -> SQL).
2.  **Self-Hosted IR**: Installed on a local machine/VM inside a private network. Used to connect to **On-Premise** data (e.g., SQL Server, Oracle) or Private VNets.
3.  **Azure-SSIS IR**: Dedicated cluster to run legacy SSIS packages in the cloud.

## Q2: Copy Activity vs. Data Flow?
**Answer**:
*   **Copy Activity**: Optimized purely for **movement** (E & L). Fast, cheap, limited transformations (mapping columns).
*   **Mapping Data Flow**: Visual interface for **transformation** (T). Runs on a managed Spark cluster. Can do Joins, Aggregates, Pivots.

## Q3: Trigger Types in ADF?
**Answer**:
1.  **Schedule Trigger**: Wall-clock time (e.g., "Every day at 8 AM").
2.  **Tumbling Window Trigger**: Slices time into non-overlapping windows. Supports dependency (Window 2 waits for Window 1) and backfilling. Essential for historical data processing.
3.  **Event-Based Trigger**: Reacts to Blob creation/deletion (e.g., "Run when file `data.csv` arrives in S3").

## Q4: How do you handle secrets in ADF?
**Answer**:
**NEVER** hardcode passwords in Linked Services.
1.  Store secret in **Azure Key Vault (AKV)**.
2.  Grant ADF's **Managed Identity** access to AKV.
3.  In ADF Linked Service, select "Azure Key Vault" and reference the Secret Name.

## Q5: How to pass parameters to a Pipeline?
**Answer**:
Define parameters at the Pipeline level (e.g., `startDate`).
*   Pass them from the Trigger or Parent Pipeline (Execute Pipeline Activity).
*   Reference in activities using `@pipeline().parameters.startDate`.
