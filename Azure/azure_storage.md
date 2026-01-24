# Azure Storage Interview Questions

## Q1: Blob Storage vs. Data Lake Storage Gen2 (ADLS Gen2)?
**Answer**:
*   **Blob Storage**: Flat namespace. To emulate a folder `data/2023/file.csv`, it's just a long filename string. Renaming the `2023` folder requires rewriting all millions of files inside.
*   **ADLS Gen2**: Hierarchical namespace (Real folders). Renaming a folder is an atomic O(1) metadata operation. Essential for Hadoop/Spark performance.

## Q2: Explain Storage Access Tiers.
**Answer**:
1.  **Hot**: Highest storage cost, lowest access cost. Use for active data.
2.  **Cool**: Lower storage cost, higher access cost. Min retention 30 days. Use for backups/short-term logs.
3.  **Archive**: Lowest storage cost, very high retrieval cost. Data is offline. Rehydration takes hours. Min retention 180 days.

## Q3: What is the difference between LRS, GRS, and RA-GRS?
**Answer**:
*   **LRS (Locally Redundant)**: 3 copies in 1 datacenter. Cheapest.
*   **ZRS (Zone Redundant)**: 3 copies across 3 Availability Zones in 1 region. Survives datacenter fire.
*   **GRS (Geo-Redundant)**: LRS in Primary Region + Async copy to LRS in Secondary Region (Paired Region). You cannot read secondary unless MSFT fails over.
*   **RA-GRS (Read-Access Geo)**: Same as GRS, but you can *read* from secondary instantly.

## Q4: What is a SAS Token?
**Answer**:
**Shared Access Signature**. A URI that grants restricted access rights to Azure Storage resources for a limited time interval.
*   *Use Case*: Giving a user temporary access to upload a file directly to Blob without giving them the Account Key.
