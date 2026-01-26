## 4. CI/CD, DevOps & Infrastructure as Code

### 1. How would you design a **CI/CD pipeline for Databricks + ADF** from scratch?
**Answer:**
"I design pipelines with **Separation of Concerns**:
*   **Build Pipeline (CI):** Triggered on PR merge. Runs automated linters (sqlfluff, pylint), unit tests (pytest for Databricks transforms), and builds artifacts (ARM templates for ADF, Wheels/DABs for Databricks). It publishes these artifacts to the Artifact feed.
*   **Release Pipeline (CD):** Triggered on artifact publication. It pulls the artifacts and deploys them to Dev, then (after approval) Test, then Prod.
*   **Infrastructure:** Terraform \pply\ usually runs in a separate pipeline or stage before the code deployment to ensure the target infrastructure (storage containers, key vaults) exists."

### 2. What artifacts do you version control for data platforms?
**Answer:**
"Everything is code.
*   **Infrastructure:** Terraform (\.tf\) files.
*   **ADF:** The usage of \ARMTemplateForFactory.json\ is standard for deployment, but we check in the individual JSON files for collaboration.
*   **Databricks:** Notebooks (py, sql), Wheel setup files (\setup.py\), and Cluster configurations (JSON).
*   **Configuration:** We do *not* version control secrets, but we do version control parameter files (e.g., \dev.params.json\) that reference those secrets."

### 3. How have you used **Terraform** to provision Azure + Databricks infrastructure?
**Answer:**
"I use the \zurerm\ and \databricks\ providers.
I module-ize common patterns:
*   **Base Module:** Creates VNet, Subnets, Network Security Groups, and Storage Accounts (with Private Endpoints).
*   **Databricks Module:** Deploys the Workspace (VNet Injected), sets up Unity Catalog Metastore assignment, and provisions standard Cluster Policies and User Groups.
*   **State Management:** Remote state is stored in an encrypted Azure Storage container with a locking policy."

### 4. Compare **Jenkins vs GitHub Actions vs Azure DevOps** for data engineering CI/CD.
**Answer:**
"I have used all three, but for an Azure shop, **Azure DevOps (ADO)** is the natural fit due to its seamless integration with AD permissions and Boards.
However, **GitHub Actions** is rapidly becoming the preference for modern teams due to its proximity to the code and marketplace of actions.
**Jenkins** is powerful but requires maintenance of the Jenkins server itself (patching, upgrades), which is toil I try to avoid. I prefer SaaS CI/CD (ADO/GHA) to reduce operational overhead."

### 5. How do you manage **secrets and credentials** in CI/CD pipelines?
**Answer:**
"Zero-trust approach.
*   Pipelines run as Service Principals with federated credentials (OIDC) where possible to avoid managing even Secret Client Secrets.
*   Deployment tasks retrieve secrets from **Azure Key Vault** using specific steps (e.g., \AzureKeyVault@2\ in ADO) and map them to environment variables.
*   We use **Variable Groups** linked to Key Vaults, so the pipeline logs never show the actual value, only \***\."

### 6. How do you enforce **quality gates (tests, linting, approvals)** for data pipelines?
**Answer:**
"Quality gates are automated steps that block deployment.
1.  **Linting:** \Black\ and \Ruff\ for Python, \sqlfluff\ for SQL. Failed linting fails the build.
2.  **Unit Tests:** \pytest\ for internal logic libraries.
3.  **Integration Tests:** Post-deploy smoke tests in the 'Test' environment that run a sample pipeline and check if data lands.
4.  **Approvals:** Deployment to Production strictly requires manual approval from a Tech Lead in the Release pipeline."

### 7. How do you roll back a failed production deployment?
**Answer:**
"We consistently use **State-Based Deployment**.
To rollback, we essentially 'roll forward' to the previous state.
*   **ADF:** We redeploy the ARM template from the *previous* successful release.
*   **Databricks:** Since we use versioned libraries (Wheels), we update the job definition to point back to the previous version (e.g., \1.2.0\ instead of \1.2.1\).
*   **Database:** This is harder. If a bad migration ran, we rely on Delta Lake's \RESTORE\ command to Time Travel back to the pre-deployment version ID."

---

