# Terraform Concepts (Azure Focus)

## Key Concepts

### 1. Infrastructure as Code (IaC)
The management of infrastructure (networks, virtual machines, load balancers, and connection topology) in a descriptive model, using the same versioning as DevOps team uses for source code.
*   **Declarative:** You define *what* you want (e.g., "I need 1 VM"), and Terraform figures out how to achieve it.
*   **Imperative:** You define specific commands to run (e.g., "Run script A, then B"). Terraform is Declarative.

### 2. Core Components
*   **Provider (`azurerm`):** A plugin that allows Terraform to interact with an API (e.g., Azure Resource Manager).
*   **Resource:** A specific infrastructure object (e.g., `azurerm_resource_group`, `azurerm_virtual_network`).
*   **Data Source:** Allows fetching data from outside of Terraform (e.g., an existing Subscription ID or a Resource Group managed manually).
*   **HCL (HashiCorp Configuration Language):** The syntax used to write Terraform code (`.tf` files).

### 3. State Management
Terraform stores state about your managed infrastructure and configuration. This state is used by Terraform to map real world resources to your configuration, keep track of metadata, and to improve performance for large infrastructures.
*   **Remote Backend:** Storing the state file (`terraform.tfstate`) in a central, shared location (e.g., **Azure Blob Storage**) rather than locally. This supports team collaboration and locking.

### 4. Workflow
1.  `terraform init`: Initializes the directory, downloads providers/modules, configures the backend.
2.  `terraform plan`: Creates an execution plan. Shows what actions will be taken (add, change, destroy) without actually doing them.
3.  `terraform apply`: Executes the changes defined in the plan.
4.  `terraform destroy`: Removes all resources managed by the configuration.

---

# Terraform Interview Questions

## Beginner Level

1.  **What is Terraform and how does it differ from Ansible?**
    *   **Answer:**
        *   **Terraform:** Primarily an **Infrastructure Provisioning** tool. It builds the foundation (VNETs, VMs, Databases). It is declarative and immutable.
        *   **Ansible:** Primarily a **Configuration Management** tool. It configures the software *inside* the servers (installing Apache, patching OS). It is imperative (procedural) and mutable.

2.  **What is a Terraform Provider?**
    *   **Answer:** A provider is a plugin that interprets the API interactions for a specific service. For Azure, the `azurerm` provider translates Terraform HCL code into Azure ARM API calls to create/manage resources.

3.  **Explain the Terraform State file.**
    *   **Answer:** `terraform.tfstate` is a JSON file that maps the resources in your configuration (`.tf` files) to real-world resources (Azure Resource IDs). It tracks the current state of infrastructure so Terraform knows what to update or delete.

4.  **What commands are used for the standard Terraform workflow?**
    *   **Answer:**
        1.  `init`: Prepare the directory.
        2.  `validate`: Check syntax.
        3.  `plan`: Preview changes.
        4.  `apply`: Deploy changes.

5.  **How do you define an input variable?**
    *   **Answer:**
        ```hcl
        variable "resource_group_name" {
          type        = string
          description = "The name of the RG"
          default     = "my-rg"
        }
        ```

6.  **What is a Terraform Module?**
    *   **Answer:** A container for multiple resources that are used together. Modules are used to create reusable components (e.g., a "Web Server" module that bundles a VM, NIC, and Public IP) to organize code and avoid duplication.

7.  **How do you handle secrets in Terraform?**
    *   **Answer:** Never commit them to git.
        *   Use `variable` definitions without default values and pass them via `-var` flags or Environment Variables (`TF_VAR_client_secret`).
        *   Best practice: Store secrets in **Azure Key Vault** and reference them using a `data` source.

8.  **What is the difference between `resource` and `data` blocks?**
    *   **Answer:**
        *   `resource`: Creates and manages a new component (lifecycle controlled by Terraform).
        *   `data`: Reads information about an *existing* component created outside of this Terraform config (read-only).

9.  **How do you output values from a Terraform run?**
    *   **Answer:** Using `output` blocks.
        ```hcl
        output "vm_public_ip" {
          value = azurerm_public_ip.example.ip_address
        }
        ```
        Examples are useful for getting connection strings or IPs after deployment.

10. **What is `.gitignore` used for in a Terraform project?**
    *   **Answer:** To prevent accidental commit of:
        *   `.terraform/` directory (plugins).
        *   `terraform.tfstate` and `*.backup` (contains sensitive info).
        *   `*.tfvars` (might contain secrets).

## Medium Level

11. **Why is "State Locking" important?**
    *   **Answer:** It prevents simultaneous writes to the state file. If two developers run `terraform apply` at the same time, they could corrupt the state file. When using Azure Blob Storage as a backend, Terraform automatically acquires a **Lease** on the blob file to lock it during operations.

12. **How do you organize Terraform code for multiple environments (Dev, Stage, Prod)?**
    *   **Answer:**
        *   **Directory Structure:** Separate folders (`env/dev/`, `env/prod/`) utilizing the same underlying modules. (Preferred for isolation).
        *   **Workspaces:** Using `terraform workspace` commands to manage multiple state files within the same directory. (Simpler, but higher risk of accidental destruction).

13. **What is `terraform.tfvars`?**
    *   **Answer:** A file used to automatically set values for defined variables. Unlike the variable definition (`variable "x" {}`), this file contains the actual assignment (`x = "value"`).

14. **How do you upgrade plugins/providers?**
    *   **Answer:** Run `terraform init -upgrade`. This checks the `version` constraints in the configuration and downloads the newest allowed versions.

15. **What is the purpose of `terraform taint`?**
    *   **Answer:** It marks a specific resource instance as "tainted" (degraded or damaged). This forces Terraform to destroy and recreate that resource in the next `apply`, rather than trying to update it in-place. Note: In newer versions, `-replace` flag in plan/apply is preferred.

16. **How do you invoke a locally defined module?**
    *   **Answer:**
        ```hcl
        module "network" {
          source = "./modules/network"
          vnet_name = "prod-vnet"
        }
        ```

17. **What is a "Provisioner" in Terraform?**
    *   **Answer:** A mechanism to execute scripts on a local or remote machine as part of resource creation (e.g., `local-exec`, `remote-exec`). **Note:** HashiCorp recommends avoiding provisioners unless essentially necessary (use cloud-init or user-data instead).

18. **How does Terraform handle dependencies between resources?**
    *   **Answer:**
        *   **Implicit:** Terraform automatically detects dependency if Resource B references an attribute of Resource A (e.g., `subnet_id = azurerm_subnet.example.id`).
        *   **Explicit:** Using `depends_on = [azurerm_resource_group.example]` meta-argument to force order.

19. **What is `terraform refresh`?**
    *   **Answer:** It reconciles the state file with the real-world infrastructure. It checks if resources still exist or have changed outside of Terraform. (Now part of `plan` automatically).

20. **Can you modify the Terraform State manually?**
    *   **Answer:** It is generally discouraged to edit the JSON file manually. Use commands like `terraform state mv` (move/rename resources) or `terraform state rm` (stop managing a resource) or `terraform import` (start managing a resource).

## Advanced Level

21. **How do you import existing Azure infrastructure into Terraform?**
    *   **Answer:**
        1.  Write the `resource` block in HCL matching the existing resource.
        2.  Run `terraform import resource_type.name <Azure_Resource_ID>`.
        3.  Run `terraform plan` to ensure the config matches the state/reality (adjust HCL until "No changes" are shown).
        *   *Newer:* `import` blocks in configuration allow bulk imports.

22. **What is Drift and how do you detect it?**
    *   **Answer:** Drift occurs when the real infrastructure configuration differs from the Terraform state (e.g., someone manually changed a specialized Firewall rule in the Portal).
    *   **Detect:** Run `terraform plan`. It will show that it plans to revert the manual changes to match the code.

23. **Construct a `for_each` loop to create multiple Storage Accounts.**
    *   **Answer:**
        ```hcl
        variable "accounts" {
          type = map(string)
          default = {
            "app1" = "eastus"
            "app2" = "westus"
          }
        }
        resource "azurerm_storage_account" "example" {
          for_each            = var.accounts
          name                = "st${each.key}"
          location            = each.value
          resource_group_name = azurerm_resource_group.rg.name
          ...
        }
        ```

24. **Difference between `count` and `for_each`?**
    *   **Answer:**
        *   `count`: Uses an integer index (0, 1). If you remove an item from the middle of the list, all subsequent resources shift indices and get destroyed/recreated.
        *   `for_each`: Uses a map/set key. Removing one item only affects that specific resource. `for_each` is generally safer for lists of resources that might change.

25. **How do you debug Terraform execution?**
    *   **Answer:** Set the environment variable `TF_LOG=DEBUG` or `TF_LOG=TRACE`. This outputs detailed logs of the API calls and internal logic to stderr or a file (if `TF_LOG_PATH` is set).

26. **What is Sentinel (or OPA Policy as Code)?**
    *   **Answer:** Policy-as-code frameworks that enforce rules *before* Terraform applies changes.
        *   Example: "Prevent creating VMs without tags" or "Prevent creating Public IPs".
        *   The pipeline runs `terraform plan`, converts it to JSON, and the policy engine validates it.

27. **How do you deal with Circular Dependencies in Modules?**
    *   **Answer:** Terraform does not support circular dependencies. You must refactor the architecture. Often involves splitting a resource or using a third "glue" resource to link them, or relying on `data` sources in a separate run.

28. **Explain the `lifecycle` meta-argument blocks.**
    *   **Answer:**
        *   `create_before_destroy`: Create the new replacement resource before destroying the old one (useful for zero-downtime).
        *   `prevent_destroy`: Returns an error if an attempt is made to destroy the resource (safety for databases).
        *   `ignore_changes`: Telles Terraform to ignore changes to specific attributes (e.g., ignoring tags that are auto-applied by Azure Policy).

29. **What is a "Dynamic Block"?**
    *   **Answer:** Allows you to construct repeatable nested blocks (like `subnet` inside `azurerm_virtual_network` or `rule` inside `azurerm_network_security_group`) based on a variable list or map. Avoids copying/pasting code for repetitive inline configuration.

30. **How do you migrate the state from a local file to Azure Blob Storage?**
    *   **Answer:**
        1.  Add a `backend "azurerm"` block to the `terraform` configuration.
        2.  Run `terraform init`.
        3.  Terraform will detect the change and ask: "Do you want to copy existing state to the new backend?"
        4.  Type `yes`.
