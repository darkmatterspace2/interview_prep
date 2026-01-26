## 6. Security, IAM & Compliance

### 1. How do you integrate data platforms with **Okta / Active Directory**?
**Answer:**
"We use **SCIM (System for Cross-domain Identity Management)** provisioning.
*   Users and Groups are managed in Azure AD (Entra ID).
*   Databricks and ADF are configured to sync these groups automatically.
*   We never create local users. If a user leaves the company and is disabled in AD, they lose access to the platform immediately."

### 2. Explain **RBAC vs ABAC** in Azure data platforms.
**Answer:**
"**RBAC (Role-Based)** is our bread and butter: 'Finance Team' group gets 'Read' on 'Finance Folder'.
**ABAC (Attribute-Based)** is the next level. We use it for fine-grained control. For example, tagging a dataset with \Confidentiality=High\ and having a policy that says 'Only users with \Clearance=High\ attribute can access resources with \Confidentiality=High\'. This scales better than managing thousands of individual role assignments."

### 3. How do you manage **least-privilege access** for data engineers vs analysts?
**Answer:**
"Engineers differ from Analysts.
*   **Engineers:** access to 'Dev' and 'Test' with Write permissions. **Read-Only** in Prod. They can only deploy to Prod via CI/CD.
*   **Analysts:** **Read-Only** access on 'Gold' tables in Prod via SQL Endpoints. No access to Bronze/Silver storage accounts directly. No ability to create clusters."

### 4. How do you secure **PII / sensitive data** in Databricks?
**Answer:**
"Layered defense:
*   **Discovery:** Use the \SENSITIVE_DATA\ tag in Unity Catalog.
*   **Masking:** I use **Dynamic View functions** (e.g., \CASE WHEN is_member('HR_Group') THEN email ELSE '***' END\).
*   **Encryption:** Customer-Managed Keys (CMK) for the storage account if required by regulation.
*   **Audit:** Strictly monitoring the audit logs for who queried these columns."

### 5. What compliance frameworks have you worked with (SOC2, ISO, GDPR)?
**Answer:**
"I've designed platforms for **GDPR** compliance.
The biggest challenge is the **Right to be Forgotten**.
We implemented a 'Tombstone' pattern in our Data Lake. When a deletion request comes in, we upsert a record with \DeleteFlag=True\. A weekly maintenance job then physically rewrites the Delta files to purge the record definitively to satisfy the 30-day requirement."

### 6. How do you audit and monitor **data access and activity logs**?
**Answer:**
"I enable **Diagnostic Settings** on all Azure resources (ADF, Databricks, Storage) to ship logs to a centralized **Log Analytics Workspace**.
I build Kusto (KQL) queries to alert on anomalies, such as:
*   A user downloading > 1GB of data.
*   Access from an unknown IP address (though Private Link mostly prevents this).
*   Failed login attempts."

---

