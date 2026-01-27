# Data Modeling Concepts

## 1. What is Data Modeling?
Data modeling is the process of creating a visual representation of either a whole information system or parts of it to communicate connections between data points and structures. It illustrates the types of data used and stored within the system, the relationships among these data types, and the ways the data can be grouped and organized.

## 2. Types of Data Models
*   **Conceptual Data Model:** High-level view. Defines *what* the system contains. Usage: Communication with business stakeholders. Entities + Relationships. No keys/attributes usually.
*   **Logical Data Model:** Defines *how* the system should be implemented regardless of the DBMS. Adds attributes, primary keys, foreign keys. Normalization happens here.
*   **Physical Data Model:** Database-specific implementation. Includes table structures, column data types, indexes, constraints, partitions.

## 3. Normalization (Relational Modeling)
The process of organizing data to specific rules (Normal Forms) to reduce redundancy and improve data integrity (OLTP systems).
*   **1NF:** Atomic values, unique rows.
*   **2NF:** 1NF + All non-key attributes dependent on the *whole* primary key.
*   **3NF:** 2NF + No transitive dependencies (non-key attributes depend only on the primary key, not on other non-key attributes).

## 4. Dimensional Modeling (Data Warehousing)
A design technique for databases intended to support end-user queries and data analysis (OLAP systems).
*   **Fact Table:** Contains quantitative data (metrics, measures) and foreign keys to dimensions.
*   **Dimension Table:** Contains descriptive attributes (who, what, where, when) used filtering and grouping.
*   **Star Schema:** Fact table in the center, dimensions connected directly.
*   **Snowflake Schema:** Dimensions are normalized (broken down into sub-dimensions).

## 5. Slowly Changing Dimensions (SCD)
How to handle updates to dimension attributes over time.
*   **Type 1 (Overwrite):** Update the record. History is lost.
*   **Type 2 (Add Row):** Add a new record with effective dates/version flag. History is preserved.
*   **Type 3 (Add Column):** Add a column for "Previous Value". Limited history.

---

# Data Modeling Interview Questions

## Beginner Level

1.  **What is the difference between a Primary Key and a Foreign Key?**
    *   **Answer:** A Primary Key uniquely identifies a record in a table and cannot be null. A Foreign Key is a field that links to the Primary Key of another table, establishing a relationship between the two.

2.  **What is Normalization and why is it used?**
    *   **Answer:** Normalization is the process of organizing data to minimize redundancy (duplicates) and ensure data dependency makes sense. It helps maintain data integrity and reduces update anomalies.

3.  **Explain the difference between OLTP and OLAP.**
    *   **Answer:**
        *   **OLTP (Online Transaction Processing):** Optimized for fast, transactional updates (INSERT/UPDATE/DELETE). Highly normalized (3NF).
        *   **OLAP (Online Analytical Processing):** Optimized for complex read queries and analysis. Denormalized (Dimensional models) for performance.

4.  **What is a Surrogate Key?**
    *   **Answer:** An artificial, system-generated unique identifier (usually an integer) used as the primary key. It has no business meaning, unlike a Natural Key (e.g., SSN, Email).

5.  **What is Denormalization?**
    *   **Answer:** The process of adding redundancy to a database (combining tables) to speed up complex reads by avoiding expensive joins. Common in data warehousing.

6.  **Define Cardinality in data modeling.**
    *   **Answer:** It refers to the nature of the relationship between two entities. Common types are One-to-One, One-to-Many, and Many-to-Many.

7.  **What is a Fact Table?**
    *   **Answer:** A table in a data warehouse that stores quantitative data (measures like SalesAmount, Quantity) and foreign keys referring to related dimension tables.

8.  **What is a Dimension Table?**
    *   **Answer:** A table that stores descriptive attributes (context) about the facts. For example, Customer Name, Product Category, Date.

9.  **What is an Entity-Relationship (ER) Diagram?**
    *   **Answer:** A graphical representation that depicts relationships among people, objects, places, concepts, or events within an information system.

10. **What is Metadata?**
    *   **Answer:** Data about data. It describes the structure, constraints, types, and meaning of the data stored in the database.

## Medium Level

11. **Compare Star Schema and Snowflake Schema.**
    *   **Answer:**
        *   **Star Schema:** Dimensions are denormalized (flat). Simpler queries (fewer joins), faster performance. preferred for PowerBI/Tableau.
        *   **Snowflake Schema:** Dimensions are normalized (split into sub-tables). Saves storage, easier maintenance, but requires more joins (slower).

12. **What is a "Factless Fact Table"?**
    *   **Answer:** A fact table that contains only foreign keys (and no measures). It is used to track events or coverage. e.g., Tracking student attendance (Student_ID, Class_ID, Date_ID) - simply recording the event happened.

13. **Explain SCD Type 2.**
    *   **Answer:** It tracks historical data by creating a new record for every update. It uses columns like `One_Row_ID` (surrogate), `Effective_Start_Date`, `Effective_End_Date`, and `Is_Current_Flag` to manage the timeline of changes.

14. **What is the difference between Logical and Physical Data Models?**
    *   **Answer:** The Logical model defines the structure (Entities, Attributes, Relationships) independent of technology. The Physical model applies that structure to a specific database engine (Data types like VARCHAR(50), Indexes, Partitions, Tablespaces).

15. **What is a Conformed Dimension?**
    *   **Answer:** A dimension that has the same meaning and content when referred to from different fact tables. e.g., A "Date" or "Customer" dimension used across Sales, Inventory, and Marketing fact tables.

16. **How do you handle Many-to-Many relationships in a physical design?**
    *   **Answer:** By introducing an associative entity (or Bridge Table / Junction Table) which breaks the relationship into two One-to-Many relationships.

17. **What is a Junk Dimension?**
    *   **Answer:** A collection of miscellaneous, low-cardinality flags and indicators (like Yes/No, Active/lnactive) grouped into a single dimension table to avoid cluttering the fact table with too many foreign keys.

18. **What is Grain? Why is it important?**
    *   **Answer:** Grain refers to the level of detail represented by a single row in a table. It is crucial because you cannot aggregate functionality correctly if you mix grains (e.g., mixing daily sales with monthly targets).

19. **What is the difference between 3NF and BCNF?**
    *   **Answer:** BCNF (Boyce-Codd Normal Form) is a slightly stronger version of 3NF. A table is in BCNF if for every non-trivial dependency A -> B, A is a superkey. It addresses anomalies in tables with multiple candidate keys.

20. **When would you use a Composite Key?**
    *   **Answer:** When a single column is not sufficient to uniquely identify a record, but a combination of two or more columns is unique. e.g., In a junction table, `Student_ID` + `Course_ID`.

## Advanced Level

21. **Explain the Data Vault modeling technique.**
    *   **Answer:** A hybrid modeling approach for EDWs. It consists of:
        *   **Hubs:** Business keys (unique list of business entities).
        *   **Links:** Relationships between Hubs (transactions, associations).
        *   **Satellites:** Context/Attributes describing Hubs or Links (where history is stored).
        *   It is designed for agility, auditability, and parallel loading, solving the rigidity of 3NF and Star Schemas in the staging layer.

22. **What is a "Degenerate Dimension"?**
    *   **Answer:** A dimension attribute that is stored directly in the fact table without a separate dimension table. Typically used for transaction numbers (Invoice ID, Order Number) which are unique to the transaction but have no other descriptive attributes.

23. **How do you design for High Performance in a Star Schema with massive data (Billions of rows)?**
    *   **Answer:**
        *   **Partitioning:** Partition the Fact table (usually by Date).
        *   **Aggregation Tables:** Pre-calculate summaries for common queries.
        *   **Indexing:** Bitmap indexes for low-cardinality columns.
        *   **Columnar Storage:** Use columnar formats (Parquet, Columnstore Index).
        *   **Integer Keys:** Use integers for joins (Surrogate keys).

24. **Explain Data Mesh from a modeling perspective.**
    *   **Answer:** Unlike a monolithic warehouse, Data Mesh distributes ownership to domains. Domain teams model their own data products. Modeling challenge: Ensuring interoperability via "Federated Computational Governance" and standardizing how to identify/join entities across domains (Polyglot modeling).

25. **How do you handle Recursive Relationships (Hierarchies) in a data model?**
    *   **Answer:**
        *   **Parent-Child:** Self-join (Employee table with Manager_ID pointing to Employee_ID). Hard to query deep levels.
        *   **Flattened/Bridge Table:** Create a helper table mapping every ancestor to every descendant (closure table).
        *   **Path Enumeration:** Storing the full path logic text `/1/5/12`.

26. **What is an "Accumulating Snapshot Fact Table"?**
    *   **Answer:** A fact table used to track the progress of an entity through a well-defined process (e.g., Order Fulfillment: Placed, Shipped, Delivered). It has multiple date foreign keys and is updated as the process moves forward.

27. **What are the potential drawbacks of using Surrogate Keys?**
    *   **Answer:**
        *   Requires an extra lookup during ETL (Key management complexity).
        *   Disconnection primarily from source system keys makes debugging slightly harder without joining back.
        *   If the lookup table is lost/corrupted, referential integrity is broken.

28. **How would you model a "Supertype/Subtype" relationship (Inheritance) in a database?**
    *   **Answer:**
        *   **Single Table:** One big table with NULLs for attributes not relevant to the subtype.
        *   **Class Table (Table per Type):** Base table + separate tables for each subtype (joined 1:1). Secure and clean, but requires joins.
        *   **Concrete Table (Table per Concrete Class):** Separate tables for each subtype with all columns repeated. No joins, but no single view of all entities.

29. **What is the difference between Inmon and Kimball methodologies?**
    *   **Answer:**
        *   **Inmon (CIF):** Enterprise-wide, normalized (3NF) relational warehouse first. Data Marts are created from the Warehouse. "Single version of truth".
        *   **Kimball (Bus Architecture):** Bottom-up approach. Build dimensional Data Marts first (Star Schemas) with conformed dimensions. "Union of all data marts".

30. **Scenario: You have a "Product" dimension and the "Category" changes. How do you model this to report historical sales under the OLD category and new sales under the NEW category?**
    *   **Answer:** This requires SCD Type 2 on the Product Dimension.
        *   The Product row is versioned.
        *   Old Fact records point to the surrogate key of the old Product version (Old Category).
        *   New Fact records point to the surrogate key of the new Product version (New Category).
        *   Reporting respects the category effective at the time of the transaction.
