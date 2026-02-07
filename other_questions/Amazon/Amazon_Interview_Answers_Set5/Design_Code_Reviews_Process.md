# Design Reviews, Code Reviews & Process Improvements for Data Systems

> **Interview Focus:** How to contribute effectively to design and code reviews, drive data quality improvements, ensure reliability, and implement process improvements in data engineering teams.

---

## 📌 Overview: Why Reviews Matter in Data Engineering

| Review Type | Purpose | When | Outcome |
|-------------|---------|------|---------|
| **Design Review** | Validate architecture before building | Before implementation | Approved design document |
| **Code Review** | Ensure quality, share knowledge | Before merge | Approved PR |
| **Data Quality Review** | Validate data contracts, checks | Before production | DQ framework approval |
| **Post-Incident Review** | Learn from failures | After incidents | Action items, runbook updates |
| **Process Review** | Improve team efficiency | Quarterly | Process changes |

---

## 🏗️ Part 1: Design Reviews for Data Systems

### 1.1 When to Request a Design Review

| Scenario | Design Review Required? | Justification |
|----------|------------------------|---------------|
| New pipeline from scratch | ✅ Yes | Architecture decisions affect long-term maintainability |
| Major refactor (>500 LOC) | ✅ Yes | Risk of breaking existing functionality |
| New data source integration | ✅ Yes | Schema, freshness, volume implications |
| Performance optimization | ⚠️ Maybe | If changing architecture; skip for config tuning |
| Bug fix | ❌ No | Code review sufficient |
| Adding new column | ❌ No | Unless breaking change |

### 1.2 Design Document Template

```markdown
# [Pipeline/Feature Name] Design Document

## 1. Overview
**Author:** [Name]  
**Reviewers:** [Names]  
**Status:** Draft | In Review | Approved | Implemented

### Problem Statement
What problem are we solving? Why now?

### Goals
- Primary goal
- Secondary goals
- Non-goals (explicitly out of scope)

## 2. Current State
How does it work today? What are the limitations?

## 3. Proposed Solution

### High-Level Architecture
[Diagram: Source → Ingestion → Processing → Storage → Consumption]

### Data Flow
| Stage | Technology | Input | Output | SLA |
|-------|------------|-------|--------|-----|
| Ingestion | Kafka | API events | Bronze table | 5 min |
| Transform | Spark | Bronze | Silver | 30 min |
| Aggregate | Spark | Silver | Gold | 1 hour |

### Schema Design
```sql
CREATE TABLE gold.daily_metrics (
    date DATE,
    metric_name STRING,
    value DECIMAL(18,2),
    PRIMARY KEY (date, metric_name)
)
PARTITIONED BY (date);
```

## 4. Alternatives Considered
| Option | Pros | Cons | Why Not Chosen |
|--------|------|------|----------------|
| Option A | ... | ... | ... |
| Option B | ... | ... | ... |

## 5. Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Source API rate limiting | Medium | High | Implement backoff, cache |
| Schema changes upstream | High | Medium | Schema registry, validation |

## 6. Operational Considerations
- **Monitoring:** What metrics/alerts?
- **Runbook:** Link to runbook
- **Rollback:** How to revert?
- **Cost:** Estimated compute/storage cost

## 7. Testing Plan
- Unit tests
- Integration tests
- Load tests (if applicable)

## 8. Timeline
| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Design | 1 week | Approved doc |
| Implementation | 2 weeks | Code complete |
| Testing | 1 week | QA sign-off |
| Rollout | 1 week | Production |

## 9. Open Questions
- [ ] Question 1?
- [ ] Question 2?
```

### 1.3 Design Review Checklist (As a Reviewer)

#### Architecture & Scalability
- [ ] Is the architecture appropriate for the data volume?
- [ ] Can it scale 10x without redesign?
- [ ] Is compute decoupled from storage?
- [ ] Are there single points of failure?
- [ ] Is the solution idempotent?

#### Data Modeling
- [ ] Is the schema normalized appropriately (not over/under)?
- [ ] Are partition keys chosen for query patterns?
- [ ] Is there a strategy for schema evolution?
- [ ] Are data types appropriate (avoid STRING for everything)?
- [ ] Is there a clear primary key/uniqueness constraint?

#### Reliability
- [ ] What happens if the source is unavailable?
- [ ] Is there a retry strategy?
- [ ] Is there a dead letter queue for failures?
- [ ] Is the pipeline monitored and alerted?
- [ ] Is there a rollback plan?

#### Data Quality
- [ ] Are data quality checks defined?
- [ ] Is there a freshness SLA?
- [ ] Are there volume anomaly checks?
- [ ] Is schema validation enforced?

#### Security & Compliance
- [ ] Is PII identified and handled correctly?
- [ ] Is data encrypted at rest and in transit?
- [ ] Are access controls defined?
- [ ] Is there an audit trail?

#### Cost
- [ ] Is the solution cost-effective?
- [ ] Are there storage lifecycle policies?
- [ ] Is spot/preemptible compute used where appropriate?

#### Operational Excellence
- [ ] Is there a runbook?
- [ ] Is the solution observable (logs, metrics, traces)?
- [ ] Is documentation adequate?
- [ ] Is the design reviewed by on-call?

### 1.4 Giving Effective Design Feedback

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     DESIGN FEEDBACK FRAMEWORK                                │
└─────────────────────────────────────────────────────────────────────────────┘

LEVEL 1: BLOCKING (Must Fix)
────────────────────────────
• Security vulnerabilities
• Data loss risk
• Incorrect business logic
• Missing critical requirements
• Unacceptable performance

Format: "BLOCKING: [Issue]. [Why it's critical]. [Suggested fix]."

Example: "BLOCKING: No retry logic for API ingestion. Transient failures 
will cause data loss. Consider exponential backoff with max 5 retries."

LEVEL 2: MAJOR (Should Fix)
───────────────────────────
• Suboptimal architecture
• Missing edge cases
• Inadequate testing
• Poor error handling
• Missing monitoring

Format: "MAJOR: [Issue]. [Impact]. [Recommendation]."

Example: "MAJOR: Partition by hour creates small files for low-volume 
sources. Will degrade query performance. Consider daily partitions."

LEVEL 3: MINOR (Nice to Have)
─────────────────────────────
• Style preferences
• Minor optimizations
• Documentation gaps
• Naming suggestions

Format: "MINOR/NIT: [Suggestion]. Optional but recommended."

Example: "NIT: Consider renaming 'process_data' to 'transform_to_silver' 
for clarity."

LEVEL 4: QUESTION (Clarification)
─────────────────────────────────
• Seeking understanding
• Exploring alternatives
• Knowledge sharing

Format: "QUESTION: [Query]? Just want to understand the reasoning."

Example: "QUESTION: Why Kafka over Kinesis here? Is it for replay 
capability or team familiarity?"
```

---

## 💻 Part 2: Code Reviews for Data Pipelines

### 2.1 Code Review Principles

| Principle | Description |
|-----------|-------------|
| **Be Respectful** | Critique code, not the person |
| **Be Specific** | Point to exact lines, suggest alternatives |
| **Be Timely** | Review within 24 hours for small PRs |
| **Be Educational** | Explain why, not just what |
| **Be Pragmatic** | Perfect is the enemy of good |

### 2.2 Data Pipeline Code Review Checklist

#### Correctness
- [ ] Does the logic match the requirements?
- [ ] Are edge cases handled (nulls, empty datasets, late data)?
- [ ] Are joins correct (inner vs left, join condition)?
- [ ] Are aggregations correct (GROUP BY matches SELECT)?
- [ ] Is the output schema correct?

#### Performance
- [ ] Are there unnecessary shuffles (avoid `collect()`, minimize `distinct()`)?
- [ ] Is data filtered early (predicate pushdown)?
- [ ] Are broadcast joins used for small tables?
- [ ] Is the partition strategy appropriate?
- [ ] Are there Cartesian joins (accidental cross join)?

#### Reliability
- [ ] Is the code idempotent?
- [ ] Are retries handled correctly?
- [ ] Is there error handling for external dependencies?
- [ ] Are checkpoints used for streaming?
- [ ] Is there a mechanism for late-arriving data?

#### Maintainability
- [ ] Is the code readable (variable names, comments)?
- [ ] Is there unnecessary complexity?
- [ ] Are there hardcoded values that should be config?
- [ ] Is logging adequate for debugging?
- [ ] Are there unit tests?

#### Security
- [ ] Is PII logged accidentally?
- [ ] Are credentials hardcoded?
- [ ] Are SQL injection risks addressed?

### 2.3 Common Code Review Comments (With Examples)

#### Performance Issues

```python
# ❌ BAD: Collect brings all data to driver
all_data = df.collect()
for row in all_data:
    process(row)

# ✅ GOOD: Process in parallel
df.foreach(lambda row: process(row))
# OR use foreachPartition for batch operations
```

**Review Comment:** "MAJOR: `collect()` pulls all data to driver, causing OOM for large datasets. Use `foreach` or `foreachPartition` for distributed processing."

---

```python
# ❌ BAD: Multiple actions on same DataFrame
count = df.count()
sample = df.take(10)
stats = df.describe().collect()

# ✅ GOOD: Cache if multiple actions needed
df.cache()
count = df.count()
sample = df.take(10)
stats = df.describe().collect()
df.unpersist()
```

**Review Comment:** "MINOR: Multiple actions trigger multiple computations. Consider caching the DataFrame if you need count, sample, and describe."

---

```python
# ❌ BAD: Small table not broadcasted
result = large_df.join(small_lookup_df, "key")

# ✅ GOOD: Broadcast small table
from pyspark.sql.functions import broadcast
result = large_df.join(broadcast(small_lookup_df), "key")
```

**Review Comment:** "MAJOR: `small_lookup_df` is only 10MB. Broadcasting it will avoid shuffle. Use `broadcast(small_lookup_df)`."

#### Correctness Issues

```python
# ❌ BAD: Wrong join type loses data
result = orders.join(customers, "customer_id")  # Inner join drops unmatched

# ✅ GOOD: Left join preserves all orders
result = orders.join(customers, "customer_id", "left")
```

**Review Comment:** "BLOCKING: Inner join will drop orders with missing customers. Per requirements, we need all orders. Use left join."

---

```python
# ❌ BAD: Not handling nulls
df = df.withColumn("ratio", col("a") / col("b"))  # Divide by zero!

# ✅ GOOD: Handle nulls and zeros
df = df.withColumn("ratio", 
    when(col("b") != 0, col("a") / col("b")).otherwise(None)
)
```

**Review Comment:** "MAJOR: Division by zero will cause nulls/errors. Add a guard clause with `when(col('b') != 0, ...)`."

#### Reliability Issues

```python
# ❌ BAD: Not idempotent
df.write.mode("append").parquet("/output/")  # Reruns create duplicates

# ✅ GOOD: Idempotent with partition overwrite
df.write \
    .mode("overwrite") \
    .partitionBy("date") \
    .option("replaceWhere", f"date = '{processing_date}'") \
    .parquet("/output/")
```

**Review Comment:** "BLOCKING: Append mode is not idempotent. Reruns will create duplicates. Use partition overwrite or merge."

---

```python
# ❌ BAD: No error handling for external API
response = requests.get(api_url)
data = response.json()

# ✅ GOOD: Proper error handling with retry
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
def fetch_data(api_url):
    response = requests.get(api_url, timeout=30)
    response.raise_for_status()
    return response.json()
```

**Review Comment:** "MAJOR: API calls can fail. Add retry logic with exponential backoff and proper timeout."

### 2.4 Data Quality in Code Reviews

```python
# REQUIRE: DQ checks before writing to production
def write_to_silver(df, table_name):
    # ✅ Validate before write
    assert_no_duplicates(df, ["order_id"])
    assert_no_nulls(df, ["order_id", "customer_id", "amount"])
    assert_row_count_in_range(df, min=1000, max=10_000_000)
    assert_column_values_in_range(df, "amount", min=0, max=1_000_000)
    
    # Only write if all checks pass
    df.write.format("delta").mode("overwrite").saveAsTable(table_name)

# ❌ BAD: Write without validation
df.write.format("delta").mode("overwrite").saveAsTable("silver.orders")
```

**Review Comment:** "MAJOR: No data quality checks before write. Add at minimum: PK uniqueness, null checks on required columns, and row count bounds."

---

## 📈 Part 3: Driving Data Quality Improvements

### 3.1 Data Quality Improvement Framework

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DATA QUALITY IMPROVEMENT CYCLE                            │
└─────────────────────────────────────────────────────────────────────────────┘

         ┌───────────────┐
         │   MEASURE     │  ← DQ scores, metrics, incident count
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │   ANALYZE     │  ← Root cause analysis, pattern identification
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │   IMPROVE     │  ← Implement fixes, add checks, automate
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │   CONTROL     │  ← Monitoring, alerting, SLAs
         └───────┬───────┘
                 │
                 └──────────────────────────────▶ (back to MEASURE)
```

### 3.2 DQ Improvement Initiatives

| Initiative | Description | Impact | Effort |
|------------|-------------|--------|--------|
| **Automated DQ Checks** | Implement Great Expectations on all tables | High | Medium |
| **DQ Dashboard** | Visibility into DQ scores across domain | High | Low |
| **Data Contracts** | SLAs between producers and consumers | High | Medium |
| **Schema Registry** | Prevent breaking schema changes | Medium | Medium |
| **Anomaly Detection** | ML-based outlier detection | Medium | High |
| **DQ Runbooks** | Standard process for DQ incidents | Medium | Low |
| **Weekly DQ Review** | Team meeting to review DQ metrics | Low | Low |

### 3.3 Measuring DQ Improvement

| Metric | Baseline | Target | How to Measure |
|--------|----------|--------|----------------|
| **DQ Score** | 92% | 99% | Average across all tables |
| **DQ Incidents/Month** | 15 | < 5 | PagerDuty/ServiceNow tickets |
| **MTTD (Mean Time to Detect)** | 4 hours | < 1 hour | Incident timestamp - data timestamp |
| **MTTR (Mean Time to Resolve)** | 8 hours | < 2 hours | Resolution - detection time |
| **Tables with DQ Checks** | 40% | 100% | Audit of all tables |
| **Consumer Satisfaction** | 3.5/5 | 4.5/5 | Quarterly survey |

### 3.4 Sample DQ Improvement Proposal

```markdown
# Proposal: Implement Data Quality Framework for Sales Domain

## Problem
- 12 DQ incidents in last quarter
- No standardized DQ checks
- Manual validation causing delays

## Proposed Solution
1. Implement Great Expectations on all 15 sales tables
2. Create DQ dashboard in Grafana
3. Alert on DQ score < 95%
4. Weekly DQ review meeting

## Success Metrics
| Metric | Current | Target (3 months) |
|--------|---------|-------------------|
| Monthly DQ incidents | 4 | < 1 |
| Tables with DQ checks | 3/15 | 15/15 |
| DQ score | 91% | 98% |

## Effort Estimate
- 2 weeks development
- 1 week testing
- Ongoing: 2 hours/week maintenance

## Risks
- False positives causing alert fatigue → Tune thresholds
- Overhead on pipeline runtime → Run async post-write
```

---

## 🔧 Part 4: Driving Reliability Improvements

### 4.1 Reliability Metrics (SRE for Data)

| Metric | Definition | Target | Measurement |
|--------|------------|--------|-------------|
| **Pipeline Success Rate** | Successful runs / Total runs | > 99% | Airflow/scheduler metrics |
| **SLA Compliance** | On-time completions / Total | > 99.5% | SLA tracking dashboard |
| **MTTR** | Mean time to recovery | < 30 min | Incident duration |
| **MTTF** | Mean time to failure | > 30 days | Time between failures |
| **Error Budget** | Allowable downtime | 4.3 min/month (99.99%) | (1 - target) × total time |

### 4.2 Reliability Improvement Initiatives

| Initiative | Description | Impact |
|------------|-------------|--------|
| **Idempotency Audit** | Ensure all pipelines are idempotent | High |
| **Automated Retries** | Exponential backoff for transient failures | High |
| **Dead Letter Queues** | Capture and reprocess failures | Medium |
| **Circuit Breakers** | Prevent cascade failures | Medium |
| **Chaos Engineering** | Inject failures to test resilience | High |
| **Runbook Standardization** | Consistent incident response | Medium |
| **On-call Training** | Prepare team for incidents | Medium |

### 4.3 Post-Incident Review (PIR) Template

```markdown
# Post-Incident Review: [Incident Title]

## Summary
- **Date:** 2024-02-07
- **Duration:** 2 hours 15 minutes
- **Severity:** P2
- **Impact:** Sales dashboard showed stale data (4 hours old)

## Timeline
| Time | Event |
|------|-------|
| 08:00 | Pipeline started |
| 08:15 | Timeout connecting to source DB |
| 08:20 | Retry 1 failed |
| 08:25 | Retry 2 failed |
| 08:30 | Pipeline failed, alert triggered |
| 08:45 | On-call acknowledged |
| 09:00 | Root cause identified (DB maintenance) |
| 09:30 | Manual rerun initiated |
| 10:15 | Data backfilled, dashboard updated |

## Root Cause
Database team performed unannounced maintenance, blocking connections.

## What Went Well
- Alert triggered within 5 minutes
- On-call responded quickly
- Manual recovery was straightforward

## What Went Wrong
- No communication from DB team
- Retry window (25 min) too short for maintenance
- No fallback data source

## Action Items
| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| Increase retry window to 2 hours | @engineer | 2024-02-10 | Open |
| Set up maintenance calendar integration | @platform | 2024-02-15 | Open |
| Add stale data indicator to dashboard | @analytics | 2024-02-12 | Open |
| PIR with DB team | @manager | 2024-02-08 | Done |

## Lessons Learned
- Need better cross-team communication for maintenance
- Consider read replica for resilience
```

---

## 🔄 Part 5: Process Improvements

### 5.1 Common Process Pain Points & Solutions

| Pain Point | Symptoms | Solution |
|------------|----------|----------|
| **Slow Code Reviews** | PRs wait > 2 days | Review SLA, assigned reviewers |
| **Inconsistent Code** | Different patterns in each pipeline | Style guide, linters, templates |
| **Knowledge Silos** | Only one person knows each pipeline | Pair programming, documentation |
| **Incident Fatigue** | Same issues recurring | Root cause fixes, automation |
| **Manual Deployments** | Error-prone releases | CI/CD, IaC |
| **No Visibility** | "Is the data fresh?" questions | Self-service dashboards |

### 5.2 Process Improvement Framework

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PROCESS IMPROVEMENT CYCLE                               │
└─────────────────────────────────────────────────────────────────────────────┘

1. IDENTIFY
   │  • Retrospective feedback
   │  • Incident patterns
   │  • Team surveys
   │  • Metrics analysis
   ▼
2. PROPOSE
   │  • Write RFC/proposal
   │  • Define success metrics
   │  • Estimate effort
   │  • Get stakeholder buy-in
   ▼
3. PILOT
   │  • Implement on one team/project
   │  • Gather feedback
   │  • Iterate
   ▼
4. ROLLOUT
   │  • Document process
   │  • Train team
   │  • Monitor adoption
   ▼
5. SUSTAIN
      • Regular review
      • Continuous improvement
```

### 5.3 Process Improvement Examples

#### Example 1: Code Review SLA

**Problem:** PRs waiting 3+ days for review

**Solution:**
```yaml
Code Review Process:
  SLA:
    - Small PR (<100 lines): Review within 4 hours
    - Medium PR (100-500 lines): Review within 24 hours
    - Large PR (>500 lines): Review within 48 hours, consider splitting

  Automation:
    - Auto-assign reviewers based on code ownership
    - Daily Slack reminder for pending reviews
    - Escalation if SLA breached

  Metrics:
    - Track median review time
    - Goal: 95% PRs reviewed within SLA
```

#### Example 2: Pipeline Development Standards

```yaml
Pipeline Standards:
  Template:
    - Use company/pipeline-template repo
    - Includes: CI/CD, DQ checks, monitoring

  Naming:
    - Pipeline: {domain}_{source}_{destination}_{frequency}
    - Example: sales_postgres_silver_daily

  Required Components:
    - [ ] Idempotent writes (overwrite or merge)
    - [ ] Data quality checks (Great Expectations)
    - [ ] Alerting (PagerDuty for failures)
    - [ ] Runbook (linked in DAG)
    - [ ] Unit tests (>80% coverage)

  Review Requirements:
    - [ ] Design review for new pipelines
    - [ ] Code review by 2 approvers
    - [ ] DQ team sign-off on checks
```

#### Example 3: On-Call Rotation

```yaml
On-Call Process:
  Rotation:
    - Weekly rotation
    - Primary + Secondary on-call
    - Handoff meeting every Monday

  Expectations:
    - Acknowledge P1 within 5 minutes
    - Acknowledge P2 within 15 minutes
    - Escalate if not resolved in 30 minutes

  Tools:
    - PagerDuty for alerting
    - Runbook wiki for procedures
    - Slack #data-oncall for coordination

  Post-Shift:
    - Document incidents
    - Update runbooks
    - Brief next on-call
```

### 5.4 Measuring Process Improvement

| Metric | What It Measures | Target |
|--------|------------------|--------|
| **Lead Time** | Idea to production | < 2 weeks |
| **PR Cycle Time** | PR open to merged | < 24 hours |
| **Deployment Frequency** | Releases per week | > 5/week |
| **Change Failure Rate** | Failed deployments | < 5% |
| **MTTR** | Time to fix failures | < 1 hour |
| **Developer Satisfaction** | Survey score | > 4/5 |

---

## 🎤 Interview Questions & Answers

### Q1: "How do you approach design reviews for data systems?"

**Answer:**
> "I use a structured checklist covering:
> 1. **Architecture:** Scalability, decoupling, failure modes
> 2. **Data Modeling:** Schema design, partitioning, evolution strategy
> 3. **Reliability:** Idempotency, retry logic, monitoring
> 4. **Data Quality:** DQ checks, freshness SLAs, anomaly detection
> 5. **Security:** PII handling, access controls, encryption
> 6. **Operations:** Runbooks, cost estimation, rollback plan
> 
> I categorize feedback as Blocking (must fix), Major (should fix), Minor (nice to have), and Questions. This helps the author prioritize."

### Q2: "What do you look for in data pipeline code reviews?"

**Answer:**
> "Beyond standard code quality, I focus on data-specific concerns:
> 
> 1. **Correctness:** Join types (inner vs left matter!), null handling, aggregation logic
> 2. **Performance:** Avoid `collect()`, use `broadcast()` for small tables, filter early
> 3. **Reliability:** Idempotency (no append mode without dedup), error handling, retries
> 4. **Data Quality:** DQ checks before writes, schema validation
> 
> I always test locally with edge cases: empty datasets, all nulls, duplicate keys."

### Q3: "How have you driven data quality improvements?"

**Answer:**
> "At my previous company, we reduced DQ incidents by 80% through:
> 
> 1. **Measurement:** Established DQ scores across all tables (started at 91%)
> 2. **Automation:** Implemented Great Expectations on 50+ tables
> 3. **Visibility:** Created Grafana dashboard for DQ scores
> 4. **Process:** Weekly DQ review meeting to track trends
> 5. **Accountability:** DQ score became part of team OKRs
> 
> Result: DQ score improved from 91% to 98.5%, incidents dropped from 15/month to 3/month."

### Q4: "How do you handle pushback on design review feedback?"

**Answer:**
> "I approach it collaboratively:
> 
> 1. **Explain the 'why':** Not just 'use broadcast join' but 'this will reduce shuffle by 90% and cut runtime in half'
> 2. **Provide evidence:** Link to documentation, past incidents, or benchmarks
> 3. **Distinguish severity:** If it's a Minor/NIT, I'm flexible. If it's Blocking, I stand firm
> 4. **Offer alternatives:** 'If you can't do X, consider Y as a workaround'
> 5. **Escalate if needed:** For Blocking issues, involve tech lead or architect
> 
> The goal is shared understanding, not winning arguments."

### Q5: "How do you drive process improvements in a data team?"

**Answer:**
> "I follow a data-driven approach:
> 
> 1. **Identify:** Use retrospectives, incident patterns, and metrics to find pain points
> 2. **Propose:** Write a brief proposal with problem statement, solution, and success metrics
> 3. **Pilot:** Test on one project/team before broad rollout
> 4. **Measure:** Track adoption and impact metrics
> 5. **Iterate:** Continuously refine based on feedback
> 
> For example, I introduced PR review SLAs after noticing 3-day average wait times. After implementation, median review time dropped to 8 hours."

---

## 📋 Checklists

### Design Review Feedback Checklist
- [ ] Reviewed architecture for scalability and fault tolerance
- [ ] Validated data model and partitioning strategy
- [ ] Confirmed idempotency and reliability patterns
- [ ] Checked for DQ framework and monitoring
- [ ] Verified security and compliance requirements
- [ ] Assessed operational readiness (runbook, rollback)
- [ ] Categorized all feedback by severity
- [ ] Provided specific, actionable suggestions

### Code Review Checklist
- [ ] Logic matches requirements
- [ ] Edge cases handled (nulls, empty, duplicates)
- [ ] Performance optimized (no collect, broadcast small tables)
- [ ] Code is idempotent
- [ ] Error handling for external dependencies
- [ ] DQ checks before production writes
- [ ] Unit tests present and passing
- [ ] No hardcoded credentials or PII in logs

### Process Improvement Checklist
- [ ] Problem clearly defined with data/metrics
- [ ] Solution proposed with success criteria
- [ ] Stakeholder buy-in obtained
- [ ] Pilot executed and learnings documented
- [ ] Rollout plan with training
- [ ] Metrics tracking implemented
- [ ] Regular review scheduled
