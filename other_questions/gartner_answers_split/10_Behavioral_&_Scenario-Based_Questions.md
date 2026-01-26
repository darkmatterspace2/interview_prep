## 10. Behavioral & Scenario-Based Questions

### 1. Describe a time you **modernized a legacy data platform**.
**Answer:**
*(STAR Method)*
*   **Situation:** We had a legacy on-prem Hadoop cluster that was failing SLAs and costing /yr in maintenance.
*   **Task:** Migrate to Azure Databricks with zero downtime for consumers.
*   **Action:** I designed a 'Strangler Fig' migration. We dual-ingested data into Azure. We moved consumption views one by one (Finance first, then Marketing) to point to the new Silver/Gold tables. I trained the team on Spark.
*   **Result:** Reduced costs by 40%, improved SLA from 24h to 1h, and retired the Hadoop nodes 3 months early.

### 2. Tell me about a **failed platform initiative** and what you learned.
**Answer:**
*   **Situation:** I tried to enforce a strict 'One Size Fits All' ingestion framework using a complex custom Python library I wrote.
*   **Action:** I rolled it out to all teams.
*   **Result:** Teams rebelled because it lacked flexibility for edge cases. Adoption stalled.
*   **Learning:** I learned that **User Adoption** is more important than Architectural Purity. Now, I treat the Platform as a Product—I interview the 'customers' (engineers) first, build an MVP, and iterate based on their feedback.

### 3. How do you decide whether to **build vs buy** platform capabilities?
**Answer:**
"I use the **'Core vs. Context'** framework.
*   **Context (Commodity):** If it's a solved problem (e.g., orchestration, lineage, secrets), I **Buy** (use Azure Data Factory, Unity Catalog, KeyVault). Building a custom orchestrator is a waste of resources.
*   **Core (Differentiator):** If it gives us a competitive advantage (e.g., a proprietary pricing algorithm), we **Build** that logic in Databricks.
*   **Rule:** meaningful engineering hours should focus on business logic, not plumbing."

### 4. How do you stay updated with **new Azure & Databricks features**?
**Answer:**
"I read the **Azure Updates** RSS feed and the **Databricks Engineering Blog**.
I attend the Data + AI Summit (virtually or in-person).
I encourage my team to do 'Tech Radar' sessions where we pick one new feature (e.g., Databricks Shield) and do a 1-day spike to see if it solves a current pain point."

### 5. Why Gartner, and why this **Associate Director** role specifically?
**Answer:**
"I’ve spent years building data platforms, and I've always admired Gartner's ability to define the 'Magic Quadrant' and set the standard for the industry.
I want to bring my **practical, in-the-trenches experience** of what actually works (and what doesn't) to Gartner's internal platforms.
I love the mix of strategy and technical leadership this Associate Director role offers—it allows me to scale my impact by building a high-performing team and a robust, modern platform."

---
