# Azure Data Factory (ADF) Interview Questions
*Mid to Senior Level*

A comprehensive guide to Azure Data Factory scenarios, focusing on orchestration, data movement, and integration challenges.

---

## Table of Contents
1. [Core Components & Architecture](#core-components--architecture)
2. [Integration Runtimes (IR)](#integration-runtimes-ir)
3. [Data Flows & Transformation](#data-flows--transformation)
4. [Triggers & Scheduling](#triggers--scheduling)
5. [Scenarios & Performance](#scenarios--performance)

---

## Core Components & Architecture

### 1. Linked Service vs Dataset
**Q:** What is the relationship between a Linked Service and a Dataset?
**A:**
*   **Linked Service:** The connection string. It defines *how* to connect to an external source (e.g., "Connect to Azure Blob Storage using this Key"). Like a connection string in code.
*   **Dataset:** The specific data structure. It points to a specific file or table *within* that Linked Service (e.g., "The file `data.csv` in container `raw`).
*   *Analogy:* Linked Service is the door to the house; Dataset is a specific box inside the house.

### 2. Variables vs Parameters
**Q:** When do you use Pipeline Parameters vs Variables?
**A:**
*   **Parameters:** External inputs passed *into* the pipeline at runtime (e.g., `RunDate`, `FilePath`). They are constant throughout the pipeline run.
*   **Variables:** Internal values that can store temporary data and change *during* the pipeline execution using the `Set Variable` activity (e.g., storing a loop counter or a flag).

### 3. Control Flow Activities
**Q:** Explain the difference between `ForEach` and `Until` activities.
**A:**
*   **ForEach:** Iterates over a fixed collection of items (e.g., list of filenames). Can run sequentially or in parallel (default).
*   **Until:** A do-while loop that runs repeatedly until a specific condition evaluates to true (e.g., wait until a file appears or status becomes 'Success').

---

## Integration Runtimes (IR)

### 4. Types of Integration Runtimes
**Q:** Name the three types of IR and when to use each.
**A:**
1.  **Azure IR (AutoResolve):** The default, fully managed, serverless compute in Azure. Use for cloud-to-cloud movement (e.g., Blob to SQL).
2.  **Self-Hosted IR (SHIR):** Installed on a local VM or on-premise machine. Required to access **private/on-premise** networks (e.g., local SQL Server behind a firewall).
3.  **Azure-SSIS IR:** Dedicated cluster of VMs to execute legacy SSIS packages in the cloud (Lift and Shift).

### 5. Self-Hosted IR High Availability
**Q:** How do you ensure High Availability (HA) for a Self-Hosted IR?
**A:**
Install the SHIR agent on multiple (up to 4) separate nodes/VMs and register them with the same Authentication Key. ADF automatically load balances tasks across these nodes and handles failover if one node goes down.

---

## Data Flows & Transformation

### 6. Mapping Data Flow vs Wrangling Data Flow
**Q:** What is the difference?
**A:**
*   **Mapping Data Flow:** Visual interface to build transformation logic (Join, Aggregate, Pivot) that runs on a managed **Spark** cluster. Designed for data engineers.
*   **Wrangling Data Flow:** Uses the **Power Query M** interface (Excel-like) for lightweight data preparation. Designed for citizen integrators/analysts.

### 7. Schema Drift
**Q:** What is Schema Drift in Mapping Data Flows and how do you handle it?
**A:**
*   *Definition:* When source fields change (add/remove columns) or data types change dynamically.
*   *Handling:* Enable the "Allow Schema Drift" checkbox in the Source transformation. Use "Drifted Column" patterns or `byName()` mapping to handle columns that aren't defined in the dataset explicitly.

---

## Triggers & Scheduling

### 8. Tumbling Window vs Schedule Trigger
**Q:** Why use a Tumbling Window trigger instead of a Schedule trigger?
**A:**
*   **Schedule Trigger:** "Fire at 10:00 AM". If the 9:00 AM run fails, the 10:00 AM run still fires independently. No built-in backfill.
*   **Tumbling Window:** "Process data for window 9:00-10:00".
    *   **Dependency:** Can wait for the previous window to succeed.
    *   **Retry:** Built-in retry policy.
    *   **Backfill:** Easily rerun historical windows.
    *   **Concurrency:** Can forbid overlapping windows (ensure sequential processing).

### 9. Event-Based Trigger
**Q:** Give a use case for an Event-Based Trigger.
**A:**
Starting a pipeline immediately when a file lands in an S3 bucket or Azure Blob Storage (`BlobCreated` event). Eliminates polling/waiting.

---

## Scenarios & Performance

### 10. Incremental Loading
**Q:** How do you design a pipeline to incrementally load data from a SQL DB to a Data Lake?
**A:**
1.  **Lookup (Old):** Get the `LastModifiedDate` (Watermark) from a metadata table/file.
2.  **Lookup (New):** Get the `MAX(LastModifiedDate)` from the Source Table.
3.  **Copy Data:** Source Query: `SELECT * FROM Source WHERE Date > @OldWatermark AND Date <= @NewWatermark`.
4.  **Stored Procedure:** Update the metadata table with the `@NewWatermark` only if the Copy succeeds.

### 11. Performance Tuning (DIUs)
**Q:** The Copy Activity is slow. How do you tune it?
**A:**
1.  **DIU (Data Integration Units):** Increase DIUs (power units) for Azure IR.
2.  **Degree of Parallelism:** Increase the parallel file copy count settings.
3.  **Staging:** Enable "Staging" (via Blob Storage) when loading into Azure Synapse (PolyBase) or Snowflake for massive throughput gains.
4.  **Partitioning:** Ensure the source database is read in parallel using "Source Partitioning" (e.g., partition by ID).

### 12. Handling API Pagination
**Q:** How do you handle a Rest API that returns paginated results?
**A:**
In the Copy Activity Source settings, configure **Pagination Rules**.
*   Map the `nextLink` or `offset` from the response body/header to the next request's URL or query parameter.
*   ADF will automatically loop until the API stops returning a next page token.
