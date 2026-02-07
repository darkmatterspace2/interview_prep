# Amazon Scenario-Based Judgment (Q96-Q100)

## 7️⃣ Scenario-Based “Judge Your Maturity” Questions

#### 96. A pipeline is correct but too slow — what do you do?
*   **Profile:** Is it I/O bound (S3 scan), CPU bound (JSON parsing), or Network bound (Shuffle)?
*   **Scale:** Can we just pay money to solve it (Add nodes)? If costs < Benefits, do it.
*   **Tune:** Partition pruning, Bucket pruning, Join reordering (Broadcast).
*   **Refactor:** Rewrite Python UDFs to Native SQL.

#### 97. Data is fast but sometimes wrong — what do you fix first?
*   **Wrong Data is worse than No Data.** (Decisions made on wrong data kill companies).
*   **Stop the line:** Halt the pipeline.
*   **Fix Logic:** Ensure correctness.
*   **Optimize Speed:** Only after correctness is proven.

#### 98. ML model accuracy dropped — where do you investigate?
*   **Data Drift:** Did the input distribution change? (Users got younger?).
*   **Concept Drift:** Did the world change? (COVID happened, so "Travel" logic broke).
*   **Pipeline Bug:** Did a Feature Engineering step start outputting NULLs?
*   **Leakage:** Was a label accidentally removed?

#### 99. Business complains dashboards don’t match numbers.
*   **Definitions:** "Define 'Active User'. Is it Login or Click?" (Usually a mismatched definition).
*   **Grain:** "You are summing Daily Active Users, but the dashboard shows Monthly Unique Users."
*   **Timing:** "Dashboard A runs at midnight. Dashboard B runs at 8 AM."

#### 100. You inherit a fragile data platform — first 90 days plan.
1.  **Assess:** Map the lineage. Identify the "Critical Path" (Revenue tables).
2.  **Stabilize:** Add monitoring to the Critical Path. Fix the "Sev 1" generators first.
3.  **Governance:** Stop the bleeding. Implement Code Review and PR process.
4.  **Refactor:** Pick one small domain -> Migrate to new architecture -> Win trust -> Repeat.

---

## 🧠 How Interviewers Evaluate These

They listen for:
*   **Decision frameworks** (e.g., "I weigh Cost vs Latency").
*   **Trade-offs** (e.g., "I chose Consistency over Availability because...").
*   **Real failure stories** (e.g., "I once deleted a Prod table...").
*   **Preventive thinking** (e.g., "I added a circuit breaker so it wouldn't happen again").
*   **Business alignment** (e.g., "The business needed speed, not perfection").

They reject:
*   Tool-only answers ("I'd use Spark").
*   Absolutist thinking ("Always use Microservices").
*   Over-engineering ("I built a custom framework").
