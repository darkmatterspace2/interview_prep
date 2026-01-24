# Azure Log Analytics Interview Questions

## Q1: What is a Log Analytics Workspace?
**Answer**:
It is the logical container for data used by Azure Monitor. It collects telemetry from various sources (VMs, Application Insights, Diagnostics).
*   Configures data retention (e.g., 30 days vs 2 years).
*   Scope for access control (Who can see logs).

## Q2: What is KQL? Write a simple query.
**Answer**:
**Kusto Query Language**. Optimized for high-performance read-only queries on large datasets.
*   *Query*: Find all Errors in the last hour.
```kusto
AppTraces
| where TimeGenerated > ago(1h)
| where SeverityLevel == "Error"
| project TimeGenerated, Message, Component
| order by TimeGenerated desc
```

## Q3: How do you connect a VM to Log Analytics?
**Answer**:
Install the **Azure Monitor Agent (AMA)** (formerly Log Analytics Agent / MMA) on the VM.
*   Configure Data Collection Rules (DCR) to specify which logs (Syslog, Windows Event Logs) to send to which Workspace.

## Q4: How do Alerts work with Log Analytics?
**Answer**:
You create a **Metric Alert** or **Log Search Alert**.
1.  **Condition**: Run a KQL query every 5 mins. If `count() > 0`, trigger.
2.  **Action Group**: Send SMS, Email, Call Webhook, or trigger Automation Runbook.
