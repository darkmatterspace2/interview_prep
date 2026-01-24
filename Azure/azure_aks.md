# Azure Kubernetes Service (AKS) Interview Questions

## Q1: Explain the architecture of AKS. What does Azure manage vs. what do you manage?
**Answer**:
*   **Control Plane (Master Node)**: Hosted by Azure. Includes API Server, Scheduler, etcd. It is free (unless you pay for Uptime SLA). You cannot SSH into it.
*   **Worker Nodes**: The VMs where your pods run. You manage these (though AKS handles patching/upgrades). You pay for these VMs.

## Q2: What is the difference between Kubenet and Azure CNI networking?
**Answer**:
*   **Kubenet**: Nodes get a VNet IP, but Pods use a NAT (Overlay) network. Saves IP addresses but has a slight performance hit due to NAT.
*   **Azure CNI**: Every Pod gets a real IP from the VNet. Faster, better for connectivity with on-prem, but consumes massive IP address space.

## Q3: How does AKS Autoscaling differ from HPA?
**Answer**:
*   **Cluster Autoscaler (CA)**: Watches for pods appearing in "Pending" state (due to lack of resources) and spins up new Azure VMs (Nodes).
*   **Horizontal Pod Autoscaler (HPA)**: Watches CPU/Memory of pods and increases the *number of replicas* (Pods).
*   *Flow*: Traffic spike -> HPA adds pods -> Nodes get full -> CA adds Nodes.

## Q4: How do you safely upgrade an AKS cluster?
**Answer**:
AKS uses a "Surge" strategy.
1.  It creates a new Node with the new version.
2.  It "Cordons" an old node (stops scheduling).
3.  It "Drains" the old node (moves pods to the new node).
4.  It deletes the old node.
*   **Tip**: Always set `maxSurge` to control speed/cost.

## Q5: What is a Node Pool?
**Answer**:
A group of VMs with the same configuration. You can have a "User Node Pool" for apps (e.g., GPU enabled) and a "System Node Pool" for CoreDNS/Metrics (standard VMs).
