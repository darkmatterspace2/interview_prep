# Azure App Service Interview Questions

## Q1: What is the difference between an App Service and an App Service Plan?
**Answer**:
*   **App Service Plan (ASP)**: Represents the physical resources (VMs) and the billing unit. It defines the region, OS (Linux/Windows), and scale (CPU/RAM).
*   **App Service**: The actual web application running *on top* of the ASP. You can run multiple Apps on a single Plan to save money, but they share the same CPU/RAM.

## Q2: explain Deployment Slots and their benefits.
**Answer**:
Deployment Slots are live apps with their own hostnames (e.g., `myapp-staging.azurewebsites.net`).
**Benefits**:
1.  **Zero Downtime Deployment**: You deploy to "Staging", warm it up, and then "Swap" with "Production". The swap just repoints the internal load balancer.
2.  **A/B Testing**: You can route a % of traffic to a slot to test new features.

## Q3: How does Auto-scaling work in App Service?
**Answer**:
*   **Scale Up**: Increasing the tier of the VM (e.g., B1 -> P1V2) for more CPU/RAM. Requires downtime.
*   **Scale Out**: Increasing the *number* of instances (VMs).
    *   **Autoscale Rules**: Define triggers (e.g., "If CPU > 70% for 5 mins, add 1 instance").
    *   **Max Limit**: Prevents runaway costs (e.g., "Max 10 instances").

## Q4: How do you secure an App Service?
**Answer**:
1.  **Authentication**: Enable built-in "Easy Auth" (Azure AD, Google, Facebook login).
2.  **Networking**: Use **VNet Integration** to access private backend resources (SQL/Redis) and **Private Endpoints** to prevent public internet access to the App.
3.  **Managed Identity**: Use System-assigned Identity to access Key Vault/SQL without storing secrets in code.
