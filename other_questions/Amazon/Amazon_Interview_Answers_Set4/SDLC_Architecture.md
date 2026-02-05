# Amazon Advanced SDLC & Architecture (Q1-Q35)

## 1️⃣ Full Software Development Life Cycle (SDLC) – Advanced

### Architecture & Design

#### 1. How do you choose between **monolith, modular monolith, and microservices** for data platforms?
*   **Monolith (Airflow+dbt):** Default for 90% of data teams. Simple to debug, atomic commits. *Risk:* Tightly coupled, scaling hits a wall.
*   **Modular Monolith:** Single repo, but clear boundaries (Schemas/Folders) enforced by CI. Code sharing allowed only via libraries. Best balance.
*   **Microservices (Data Mesh):** Justified **only** if teams are blocked by central bottlenecks. Adds massive cognitive load (network failures, distributed transactions).

#### 2. What architectural principles matter most for **data systems** vs application systems?
*   **Throughput vs Latency:** Apps optimize for ms latency; Data optimizes for massive throughput.
*   **Immutability:** Apps update state; Data appends history.
*   **Idempotency:** Re-running a pipeline must be safe; re-submitting an order is not.

#### 3. How do you design for **backward compatibility** in data pipelines?
*   **Additive Only:** Only add columns, never rename/delete.
*   **Versioned Schemas:** `events_v1` and `events_v2` coexist.
*   **Views:** Expose data via Views, so you can refactor underlying tables without breaking consumers.

#### 4. How do you design APIs for **data consumption**?
*   **Pagination:** Mandatory.
*   **Filters:** Allow consumers to ask for `since=timestamp` (Incremental).
*   **Format:** JSON (App) vs Parquet/Arrow (Bulk Data Transfer).

#### 5. How do you prevent tight coupling between producers and consumers?
*   **Schema Registry:** Acts as a contract buffer.
*   **Dead Letter Queues:** If consumer fails to parse, producer doesn't crash; data goes to DLQ.
*   **Domain Events:** Producer emits "OrderCreated" (Fact), not "UpdateTableX" (Implementation).

---

### Coding Standards & Maintainability

#### 6. What coding standards matter most in data pipelines?
*   **SQL Formatting:** (dbt-style guide).
*   **Configuration over Code:** Hardcoding thresholds vs params.yaml.
*   **Idempotency:** Every function must be re-runnable.

#### 7. How do you enforce standards across large teams?
*   **Pre-commit hooks:** Run `sqlfluff` and `black`.
*   **CI Gates:** Build fails if linting fails.
*   **Templates:** `cookiecutter` for new pipelines.

#### 8. How do you balance **performance vs readability**?
*   **Readability First:** Storage is cheap; Engineering time is expensive.
*   **Optimize Later:** Only refactor to ugly/complex optimized code if profiling proves it's a bottleneck.
*   **Comment the "Why":** If you write crazy bitwise logic, comment *why*.

#### 9. What makes data code **hard to refactor**?
*   **Hidden Dependencies:** SQL logic (strings) is hard for IDEs to trace.
*   **State:** Code depends on the *current* state of the DB, which changes.
*   **Volume:** You can't just "run tests" on 1PB of data easily.

#### 10. How do you manage technical debt in pipelines?
*   **Tech Debt Backlog:** Tag Jira tickets `debt`.
*   **Boy Scout Rule:** Clean the adjacent SQL when touching a file.
*   **Refactoring Sprints:** Dedicate 20% time to platform health.

---

### Code Reviews (High Signal)

#### 11. What do you look for in a data engineering code review?
*   **Logic:** Does the Join fan out? (Count checks).
*   **Scale:** Will this `collect()` crash on PROD data?
*   **Idempotency:** What happens if I run this twice?

#### 12. How do you review SQL for correctness and performance?
*   **EXPLAIN plan:** Ask dev to attach it.
*   **Index Usage:** Is the WHERE clause sargable?
*   **Dry Run:** Output record counts before/after change.

#### 13. How do you detect hidden data quality bugs in PRs?
*   Ask for **Data Diff:** "Show me top 10 rows changed".
*   Check `NULL` handling in calculations.

#### 14. How do you review Spark code differently from Python services?
*   **Lazy Evaluation:** "This line doesn't error here, it errors at action."
*   **Shuffle:** Look for `groupBy` on high cardinality keys (Skew).

#### 15. What are common red flags in data PRs?
*   `SELECT *` in Production.
*   Hardcoded dates `WHERE date > '2023-01-01'`.
*   Lack of comments on magic numbers.

---

### Source Control & Branching

#### 16. GitFlow vs trunk-based development — which fits data teams better?
**Trunk-based.**
*   Data pipelines shouldn't live in long-lived feature branches; merging SQL schema changes 3 months late is a nightmare.
*   Use Feature Flags (config) to hide new logic in Prod.

#### 17. How do you version SQL and schemas?
*   **Migration Files:** `001_initial.sql`, `002_add_col.sql` (Flyway/Liquibase).
*   **Infrastructure as Code:** Terraform for Tables.

#### 18. How do you manage long-running feature branches?
**Don't.** Rebase daily. Or use "Schema Branching" (Write to `dev_schema`).

#### 19. How do you handle merge conflicts in SQL?
*   Manually. It's painful.
*   Avoid by making files smaller (Modularize: One file per CTE/View).

#### 20. What should never be committed to source control?
*   **Secrets:** Passwords/Keys.
*   **Data:** CSVs > 1MB.
*   **Config:** Environment specific keys (use references).

---

### CI/CD & Continuous Deployment

#### 21. How do you safely deploy data pipeline changes?
**Blue/Green:**
1.  Deploy new DAG `_v2`.
2.  Write to `table_v2`.
3.  Run Data Quality checks.
4.  Swap view `table` to point to `table_v2`.

#### 22. Blue-green vs canary deployments for data systems?
*   **Blue-Green:** Best for Batch. (Parallel runs).
*   **Canary:** Best for Streaming. (Read 1% of Kafka topic, verify metrics, then scale).

#### 23. How do you roll back data changes?
*   **Code:** `git revert`.
*   **Data:** Time Travel (Delta Lake) `RESTORE TABLE AS OF...`. Or restore from Backup. (Code rollback is easy, Data rollback is hard).

#### 24. What should a data CI pipeline validate?
*   Linting (SQLFluff).
*   DAG integrity (Circular dependencies).
*   Unit Tests (Mock data).
*   Dry Run (Compile SQL against Prod Catalog).

#### 25. How do you prevent breaking downstream consumers?
**Contract Tests.**
*   Consumer (BI Team) writes a test: "I expect column `revenue` to be FLOAT".
*   This test runs in Producer's CI pipeline.
*   If Producer changes `revenue` to STRING, build fails.

---

### Testing Strategy

#### 26. Unit testing for data pipelines — what is testable?
*   **UDFs:** Python functions (Currency conversion).
*   **SQL Logic:** Mock input table, run SQL, assert output. (dbt unit tests).

#### 27. Data tests vs software tests — differences?
*   **Software Test:** Logic is fixed, Input varies.
*   **Data Test:** Logic varies, Data varies (and is unknown). You test the *data properties* (Nulls, Uniqueness), not just the code.

#### 28. How do you test Spark jobs?
*   Small local DataFrame comparisons (`chispa` or `pandas.testing`).
*   Don't spin up EMR for unit tests (too slow).

#### 29. Contract testing for data producers/consumers.
(See Q25). Ensuring the "Interface" (Schema/SLA) holds.

#### 30. Why most data tests fail in practice?
They check **trivialities** (Not Null) but miss **semantics** (Revenue dropped 50%).

---

### Operational Excellence

#### 31. What does **operational excellence** mean for data systems?
*   You sleep at night.
*   Pipelines fail gracefully.
*   Incidents are specific ("Order Table is late") not vague ("Dashboard is wrong").

#### 32. Metrics that indicate pipeline health.
*   **Data Freshness:** (SLA).
*   **Data Accuracy:** (DQ Checks pass rate).
*   **Cost:** ($/Query).

#### 33. How do you reduce on-call burden for data teams?
*   **Fix Root Causes:** Don't just restart.
*   **Better Alerts:** Delete noisy alerts.
*   **Runbooks:** "If X fails, do Y".

#### 34. Runbooks — what belongs in them?
*   **Severity Definition.**
*   **Lineage:** Upstream/Downstream impacts.
*   **Steps to Mitigate:** (Not just fix). "How to post a banner on the dashboard."

#### 35. How do you do post-mortems for data incidents?
**Blameless.**
*   Timeline.
*   Root Cause (5 Whys).
*   Action Items (Preventative).
