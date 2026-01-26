## 3. Azure Data Factory (ADF) â€“ Advanced Scenarios

### 1. How do you design **metadata-driven ADF pipelines**?
**Answer:**
"hardcoding pipelines for every table is unscalable.
I design a **Framework** approach:
*   **Control Table:** A SQL table or JSON config listing TableName, SourceQuery, DestinationPath, WatermarkColumn, and IsActive flag.
*   **Master Pipeline:** A generic pipeline with a `Lookup` (get list of tables) -> `ForEach` loop -> `Execute Pipeline` (Child).
*   **Child Pipeline:** Takes parameters (Source, Sink) and executes the Copy Activity.
*   This way, onboarding a new dataset is just an `INSERT` into the Control Table, not a code deployment."

### 2. How do you manage **ADF connector upgrades** and breaking changes?
**Answer:**
"AWS or SaaS API versions change.
*   We abstract source specifics into **Linked Services**.
*   If a connector is deprecated (e.g., a specific Salesforce API version), we update the Linked Service or the Dataset definition.
*   Because we use a metadata-driven framework, we can often just update the 'Source Query' in our control table to adapt to schema changes without redeploying the ADF pipeline artifacts themselves."

### 3. How do you handle **ADF performance bottlenecks** at scale?
**Answer:**
"ADF bottlenecks usually happen in two places:
1.  **Control Flow Limits:** ADF has a limit of 40 parallel activities in a loop. I use **Batching** (processing groups of 20 tables) to work around this.
2.  **Copy Throughput:** If the Copy Activity is slow, I check the **Integration Runtime (IR)**. If it's a Self-Hosted IR, is the CPU maxed? If so, we scale out (add nodes) or scale up. If it's Azure IR, I increase the **DIUs (Data Integration Units)** explicitly for that activity."

### 4. Explain your strategy for **ADF CI/CD across environments**.
**Answer:**
"I adhere to the **npm-based deployment** standard recommended by Microsoft.
*   **Dev:** Developers work in their own Git branches. Debug runs happen here.
*   **Build:** When merging to the collaboration branch (e.g., `main`), an Azure DevOps pipeline runs the NPM build command to generate the **ARM Templates**.
*   **Release:** The release pipeline deploys these ARM templates to Test and Prod.
*   **Parameters:** We heavily use **Global Parameters** and KeyVault references to ensure environment-specific values (like connection strings) are injected at deployment time."

### 5. Whatâ€™s your approach to **self-hosted integration runtime** vs managed IR?
**Answer:**
"Security dictates this choice.
*   **Azure IR (Managed):** Default choice for Cloud-to-Cloud copy (e.g., Blob to SQL DB). It's serverless and scales automatically.
*   **Self-Hosted IR:** Mandatory for **On-Premise** data sources or VNet-protected resources that Azure IR cannot reach. I deploy these on dedicated VMs close to the data source. I always deploy at least **two nodes** for High Availability (HA) so that patching one node doesn't stop ingestion."

---

