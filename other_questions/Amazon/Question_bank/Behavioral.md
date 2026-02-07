# Behavioral Interview Questions & Answers (Question Bank 1)

> **Amazon Leadership Principles Focus** - STAR Format Responses

---

<a id="index"></a>
## 📑 Table of Contents

| Section | Topics |
|---------|--------|
| [📌 STAR Framework](#star-framework) | How to structure behavioral answers |
| [1️⃣ Ownership / Dive Deep](#1️⃣-ownership--dive-deep-q91-q95) | Q91-Q95: Pipeline fixes, debugging, reliability |
| &nbsp;&nbsp;&nbsp;└ [Q91: Fixed a broken data pipeline](#q91-fixed-a-broken-data-pipeline) | OOM debugging, broadcast joins |
| &nbsp;&nbsp;&nbsp;└ [Q92: Debugged a data discrepancy](#q92-debugged-a-data-discrepancy) | $2M finance mismatch |
| &nbsp;&nbsp;&nbsp;└ [Q93: Found root cause of incorrect metrics](#q93-found-root-cause-of-incorrect-metrics) | Carrier performance dispute |
| &nbsp;&nbsp;&nbsp;└ [Q94: Took ownership beyond your role](#q94-took-ownership-beyond-your-role) | Cross-team unblocking |
| &nbsp;&nbsp;&nbsp;└ [Q95: Improved reliability of data systems](#q95-improved-reliability-of-data-systems) | 80% incident reduction |
| [2️⃣ Bias for Action / Deliver Results](#2️⃣-bias-for-action--deliver-results-q96-q100) | Q96-Q100: Deadlines, speed, automation |
| &nbsp;&nbsp;&nbsp;└ [Q96: Delivered under tight deadlines](#q96-delivered-under-tight-deadlines) | Black Friday scaling |
| &nbsp;&nbsp;&nbsp;└ [Q97: Chose speed over perfection](#q97-chose-speed-over-perfection--why) | GDPR compliance |
| &nbsp;&nbsp;&nbsp;└ [Q98: Made a decision with incomplete data](#q98-made-a-decision-with-incomplete-data) | Null handling decision |
| &nbsp;&nbsp;&nbsp;└ [Q99: Automated a manual process](#q99-automated-a-manual-process) | Data quality automation |
| &nbsp;&nbsp;&nbsp;└ [Q100: Reduced cost or improved performance](#q100-reduced-cost-or-improved-performance-measurably) | $360K/year savings |
| [3️⃣ Additional Behavioral Questions](#3️⃣-part-2-additional-behavioral-questions-q101-q104) | Q101-Q104: Customer obsession, calculated risks |
| &nbsp;&nbsp;&nbsp;└ [Q101: Customer Obsession](#q101-customer-obsession--pushed-back-on-requirements) | Pushed back on requirements |
| &nbsp;&nbsp;&nbsp;└ [Q102: Ownership — 2 AM failure](#q102-ownership--2-am-pipeline-failure) | 2 AM pipeline recovery |
| &nbsp;&nbsp;&nbsp;└ [Q103: Deliver Results](#q103-deliver-results--simplified-complex-solution) | Simplified complex solution |
| &nbsp;&nbsp;&nbsp;└ [Q104: Bias for Action](#q104-bias-for-action--calculated-risk-to-fix-data-issue) | Calculated risk decision |
| [� Tips for Behavioral Interviews](#-tips-for-behavioral-interviews) | Best practices |

---

<a id="star-framework"></a>
## �📌 STAR Framework [↩️](#index)

```
SITUATION: Set the context (1-2 sentences)
TASK: What was your specific responsibility?
ACTION: What did YOU do? (Be specific, use "I")
RESULT: Quantifiable outcome + learnings
```

---

<a id="1️⃣-ownership--dive-deep-q91-q95"></a>
## 1️⃣ Ownership / Dive Deep (Q91-Q95) [↩️](#index)

<a id="q91-fixed-a-broken-data-pipeline"></a>
### Q91: Fixed a broken data pipeline [↩️](#index)

**SITUATION:** Our daily shipment aggregation pipeline started failing intermittently at ~2 AM, impacting morning dashboard updates for 200+ operations managers.

**TASK:** As the on-call engineer, I needed to diagnose the failures and implement a permanent fix, not just restart the job.

**ACTION:**
1. **Immediate:** Restarted the job manually to restore dashboard
2. **Diagnosis:** Analyzed 2 weeks of logs, found failures correlated with high data volume days (>10M records)
3. **Root Cause:** Executor OOM when joining shipments with carriers table (carrier table had grown 10x due to acquisitions)
4. **Fix:** Changed from shuffle join to broadcast join (carrier table was still < 500MB)
5. **Prevention:** Added memory monitoring alerts and auto-scaling triggers

**RESULT:**
- Pipeline hasn't failed in 6 months (100% uptime)
- Reduced average runtime from 45 min to 15 min (broadcast eliminated shuffle)
- Created runbook for similar issues → team resolved 3 other pipelines

---

<a id="q92-debugged-a-data-discrepancy"></a>
### Q92: Debugged a data discrepancy [↩️](#index)

**SITUATION:** Finance team reported $2M mismatch between our data warehouse and ERP system for Q4 revenue.

**TASK:** Investigate and resolve the discrepancy before quarterly audit.

**ACTION:**
1. **Traced lineage:** Compared counts at each pipeline stage (source → bronze → silver → gold)
2. **Isolated issue:** Silver table had 15K fewer orders than bronze
3. **Root cause:** Date filter used UTC, but source system stored local time → Dec 31 orders filtered as Jan 1
4. **Validated:** Manually calculated expected revenue, matched ERP after fix
5. **Fixed:** Updated filter to use source timezone, added audit check comparing source vs warehouse counts

**RESULT:**
- Resolved $2M discrepancy in 3 days (before audit deadline)
- Implemented daily reconciliation job → catches discrepancies within 24 hours
- Documented timezone handling as team standard

---

<a id="q93-found-root-cause-of-incorrect-metrics"></a>
### Q93: Found root cause of incorrect metrics [↩️](#index)

**SITUATION:** Carrier performance dashboard showed FedEx at 95% on-time delivery, but carrier disputed this (claimed 98%).

**TASK:** Determine source of truth and fix the discrepancy.

**ACTION:**
1. **Compared definitions:** Our "on-time" vs carrier's "on-time"
2. **Found gap:** We used carrier's initial promise date, they used updated promise date after delays
3. **Dug deeper:** Found 3% of shipments had promise date updated after creation (not captured in our snapshot)
4. **Solution:** Changed to CDC-based capture (preserving history) instead of daily snapshot
5. **Aligned with business:** Confirmed which definition stakeholders wanted (original promise)

**RESULT:**
- Metrics now match carrier data within 0.2%
- Added "Original Promise" vs "Final Promise" columns → users can analyze both
- Improved carrier relationship (no more disputes)

---

<a id="q94-took-ownership-beyond-your-role"></a>
### Q94: Took ownership beyond your role [↩️](#index)

**SITUATION:** Data science team was blocked for 2 weeks waiting for feature data that another team (Platform) was supposed to provide.

**TASK:** As a Data Engineer (not Platform), I could have just escalated. Instead, I took ownership to unblock DS.

**ACTION:**
1. **Assessed gap:** Platform team was understaffed, work was queued
2. **Proposed:** I'll build interim solution if Platform provides requirements
3. **Built:** Created feature extraction pipeline in Spark (not my usual stack), delivered in 4 days
4. **Documented:** Handed off to Platform with design doc and tests
5. **Enabled:** DS team could start model training while Platform finalized production version

**RESULT:**
- Unblocked DS team 3 weeks early
- Model launched 2 weeks ahead of schedule → $500K additional revenue in first month
- Platform team adopted my approach, reducing their work

---

<a id="q95-improved-reliability-of-data-systems"></a>
### Q95: Improved reliability of data systems [↩️](#index)

**SITUATION:** Our data platform had 4-5 P2 incidents per month, mostly due to lacking monitoring and unclear ownership.

**TASK:** Reduce incidents by improving reliability practices.

**ACTION:**
1. **Assessed:** Mapped all pipelines to owners, found 30% "orphaned"
2. **Implemented monitoring:** Added Datadog dashboards + alerts for every critical pipeline
3. **Created runbooks:** Standard response procedures for common failures
4. **Established on-call:** Rotating schedule with clear escalation paths
5. **Led PIRs:** Post-incident reviews for every P1/P2, tracked action items to completion

**RESULT:**
- P2 incidents dropped from 5/month to 1/month (80% reduction)
- Mean Time to Recovery (MTTR) reduced from 4 hours to 45 minutes
- Team confidence improved → volunteering for on-call increased

---

<a id="2️⃣-bias-for-action--deliver-results-q96-q100"></a>
## 2️⃣ Bias for Action / Deliver Results (Q96-Q100) [↩️](#index)

<a id="q96-delivered-under-tight-deadlines"></a>
### Q96: Delivered under tight deadlines [↩️](#index)

**SITUATION:** Black Friday data pipeline needed to handle 5x normal volume. We learned this 3 weeks before the event.

**TASK:** Scale infrastructure and optimize pipelines to prevent downtime during peak shopping.

**ACTION:**
1. **Day 1-3:** Load tested current system → identified bottlenecks (Kafka, Spark joins)
2. **Day 4-10:** Parallelized Kafka consumers, switched to broadcast joins, pre-aggregated hot paths
3. **Day 11-15:** Implemented fallback (graceful degradation): if real-time fails, show cached daily data
4. **Day 16-18:** Ran 3 full-scale simulations, tuned auto-scaling triggers
5. **Black Friday:** Monitored live, made zero interventions needed

**RESULT:**
- Zero downtime during Black Friday (vs 2 hours previous year)
- Handled 6x normal volume (exceeded 5x requirement)
- Pattern became standard for all peak events

---

<a id="q97-chose-speed-over-perfection--why"></a>
### Q97: Chose speed over perfection — why? [↩️](#index)

**SITUATION:** New regulatory requirement: must delete customer data within 72 hours of request. Compliance deadline in 2 weeks.

**TASK:** Implement data deletion capability across 50+ tables.

**ACTION:**
1. **Chose pragmatic approach:** Instead of building perfect deletion framework, focused on compliance
2. **Prioritized:** Identified 12 tables with PII (80/20 rule) → focused there first
3. **Quick solution:** Soft delete with hard delete batch job (not real-time, but compliant)
4. **Technical debt:** Documented gaps, planned Phase 2 for automation
5. **Tested:** Ran 3 deletion cycles, verified data actually gone

**RESULT:**
- Met compliance deadline with 3 days to spare
- Zero regulatory findings in audit
- Phase 2 (automated, full coverage) delivered in following quarter

**Why Speed Was Right:**
- Regulatory fine >> cost of technical debt
- Soft delete was reversible if we found issues
- Foundation was in place for proper solution

---

<a id="q98-made-a-decision-with-incomplete-data"></a>
### Q98: Made a decision with incomplete data [↩️](#index)

**SITUATION:** Pipeline was failing due to upstream API returning unexpected nulls. We didn't know if it was a bug or intentional change.

**TASK:** Decide how to handle: fail-fast (assert not null) or fail-safe (default to zero).

**ACTION:**
1. **Assessed risk:** Nulls in "quantity" field could mean 0 or unknown
2. **Decision:** Default to 0 with alert, rather than block entire pipeline
3. **Justification:** 
   - Downstream consumers prefer stale data over no data
   - Alert would catch if nulls exceeded threshold
   - Business could manually correct if needed
4. **Fallback:** If > 5% nulls, pipeline would halt (catastrophic threshold)
5. **Follow-up:** Raised ticket with upstream team, got response in 2 days (it was temp bug)

**RESULT:**
- Pipeline continued, metrics slightly off (0.3% impact)
- Caught issue early, upstream fixed in 2 days
- Established pattern for handling null uncertainty

---

<a id="q99-automated-a-manual-process"></a>
### Q99: Automated a manual process [↩️](#index)

**SITUATION:** Data quality team spent 10 hours/week manually checking pipeline outputs: row counts, null rates, freshness.

**TASK:** Automate checks to save time and improve reliability.

**ACTION:**
1. **Analyzed:** Documented all 40+ manual checks they performed
2. **Prioritized:** Top 20 checks covered 90% of catch rate
3. **Built:** Great Expectations suite with these checks, integrated into Airflow
4. **Visualized:** Grafana dashboard showing DQ scores per table
5. **Alerted:** PagerDuty if score drops below threshold

**RESULT:**
- Reduced manual effort from 10 hours/week to 1 hour/week (90% saving)
- DQ issues caught 4x faster (automated check runs post-pipeline vs weekly manual)
- Team reallocated to building new pipelines (higher value work)

---

<a id="q100-reduced-cost-or-improved-performance-measurably"></a>
### Q100: Reduced cost or improved performance measurably [↩️](#index)

**SITUATION:** EMR cluster costs were $45K/month for batch processing, and most of the day cluster sat idle.

**TASK:** Reduce costs without impacting pipeline SLAs.

**ACTION:**
1. **Analyzed usage:** Cluster was 80% utilized only 4 hours/day (during batch window)
2. **Evaluated options:** Spot instances, EMR Serverless, auto-scaling
3. **Chose:** EMR on Spot (70% savings) + auto-scaling (scale to 0 when idle)
4. **Mitigated Spot risks:** Implemented checkpointing, diversified instance types
5. **Tested:** Ran parallel for 2 weeks, validated results matched

**RESULT:**
- Costs reduced from $45K to $15K/month (67% savings = $360K/year)
- Pipeline SLAs maintained (even improved due to auto-scaling during peak)
- Approach adopted by 3 other teams

---

<a id="3️⃣-part-2-additional-behavioral-questions-q101-q104"></a>
## 3️⃣ Part 2: Additional Behavioral Questions (Q101-Q104) [↩️](#index)

<a id="q101-customer-obsession--pushed-back-on-requirements"></a>
### Q101: Customer Obsession — Pushed back on requirements [↩️](#index)

**SITUATION:** Product team wanted real-time inventory updates (< 1 second latency) for their new feature.

**TASK:** Evaluate feasibility and recommend appropriate solution.

**ACTION:**
1. **Understood need:** Why real-time? → Feature was displaying "In Stock" badge
2. **Analyzed:** Our current batch (5 min) was 99.5% accurate for stock status
3. **Calculated:** Real-time infra would cost $50K/month, batch $5K/month
4. **Proposed alternative:** 1-minute near-real-time (< 1 second for hot items, 1 min for rest)
5. **Presented trade-offs:** 10x cost savings, 99.9% accuracy, met actual user need

**RESULT:**
- Product team agreed to near-real-time (1 min)
- Saved $45K/month vs original request
- Feature launched successfully, no customer complaints about staleness

---

<a id="q102-ownership--2-am-pipeline-failure"></a>
### Q102: Ownership — 2 AM pipeline failure [↩️](#index)

**SITUATION:** Received PagerDuty alert at 2:15 AM. Daily revenue pipeline failed, blocking finance team's morning report.

**TASK:** Restore the pipeline before 7 AM finance meeting.

**ACTION:**
1. **2:20 AM:** Acknowledged alert, checked logs → OOM error in Spark executor
2. **2:30 AM:** Identified cause: unusually large input (3x normal due to promo event)
3. **2:45 AM:** Tried to restart with more memory → still failed (cost-constrained cluster)
4. **3:00 AM:** Decision: Process yesterday's data with sampling (95% accuracy) for morning meeting, full reprocess after
5. **3:30 AM:** Delivered sampled report to finance, documented caveats
6. **8:00 AM:** Full reprocess completed, validated against sampled version

**RESULT:**
- Finance had data for 7 AM meeting (with acceptable accuracy)
- Full accurate data by 8 AM
- Implemented auto-scaling for future promo events

---

<a id="q103-deliver-results--simplified-complex-solution"></a>
### Q103: Deliver Results — Simplified complex solution [↩️](#index)

**SITUATION:** Team was designing ML feature pipeline with real-time streaming, feature store, and custom serving layer. ETA: 4 months.

**TASK:** Deliver model to production in 6 weeks for holiday season.

**ACTION:**
1. **Reassessed scope:** Model didn't actually need real-time features (daily refresh was fine)
2. **Proposed simplified design:** Batch-computed features stored in Redshift, model calls via SQL
3. **Removed complexity:** No streaming, no feature store, no custom serving
4. **Focused:** 2 weeks feature engineering, 2 weeks model training, 2 weeks deployment/testing
5. **Planned Phase 2:** Real-time enhancements after holiday

**RESULT:**
- Model launched 2 weeks early
- 15% improvement in conversion (vs control)
- Phase 2 delivered in Q1 with learnings from production

---

<a id="q104-bias-for-action--calculated-risk-to-fix-data-issue"></a>
### Q104: Bias for Action — Calculated risk to fix data issue [↩️](#index)

**SITUATION:** Discovered that 3 months of shipment cost data had wrong currency conversion (used yesterday's rate instead of transaction date's rate).

**TASK:** Fix historical data while production was running.

**ACTION:**
1. **Assessed impact:** $500K in cost variance across 3 months
2. **Decision without full info:** Didn't wait for Finance approval (would take 2 weeks) → informed them and proceeded
3. **De-risked:** Kept backup of original data, processed fix to staging first
4. **Validated:** Sampled 100 transactions, manually verified conversions
5. **Executed:** Atomic swap of 3 months partitions during low-traffic window

**RESULT:**
- Data corrected in 3 days (vs 2+ weeks with full approval cycle)
- Finance appreciated proactive fix (validated our numbers)
- Created currency conversion monitoring → catches issues within 24 hours

---

<a id="-tips-for-behavioral-interviews"></a>
## 📝 Tips for Behavioral Interviews [↩️](#index)

```
1. PREPARE 2-3 STORIES per Leadership Principle
   - Have variations for different angles

2. QUANTIFY EVERYTHING
   - ❌ "Improved performance"
   - ✅ "Reduced latency from 500ms to 50ms (90% improvement)"

3. USE "I" NOT "WE"
   - ❌ "We decided to..."
   - ✅ "I proposed X. After team discussion, we chose..."

4. SHOW LEARNINGS
   - What would you do differently?
   - How did you share knowledge?

5. DEMONSTRATE LEADERSHIP PRINCIPLES
   - Customer Obsession: Start with customer need
   - Ownership: Went beyond job description
   - Bias for Action: Made decision with 70% info
   - Dive Deep: Found root cause, not symptoms
   - Deliver Results: Quantified impact
```
