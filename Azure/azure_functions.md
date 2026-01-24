# Azure Functions Interview Questions

## Q1: Consumption Plan vs. Premium Plan?
**Answer**:
*   **Consumption**: Pay-per-execution. Scales to 0. Cheapest.
    *   *Issue*: **Cold Start**. If no requests for 20 mins, the app sleeps. Next request takes seconds to spin up.
*   **Premium**: Pay for pre-warmed instances. No cold start. VNet connectivity supported.
*   **Dedicated (App Service Plan)**: Run functions on a dedicated VM. Predictable cost/performance.

## Q2: What are Triggers and Bindings?
**Answer**:
*   **Trigger**: What starts the function (e.g., HTTP Request, New Blob, Timer, CosmosDB Change). Only 1 trigger per function.
*   **Binding**: Declarative way to connect input/output data.
    *   *Example*: Use an "Output Binding" to write a result to Azure SQL. You don't need to write connection code (`SqlConnection.Open()`), the runtime handles it.

## Q3: What are Durable Functions?
**Answer**:
An extension to write **stateful** functions in a serverless environment.
*   **Orchestrator Function**: Describes workflow in code (e.g., "Wait for Activity A, then run B and C in parallel").
*   **Activity Function**: The worker.
*   *Patterns*: Chaining, Fan-out/Fan-in, Monitor, Human Interaction (Wait for approval).

## Q4: How long can a Function run?
**Answer**:
*   **Consumption**: Default 5 mins. Max 10 mins.
*   **Premium/Dedicated**: Unlimited (technically, but usually limited by restarts/deployments).
*   *Tip*: If you need > 10 mins, use Durable Functions or Batch/AKS.
