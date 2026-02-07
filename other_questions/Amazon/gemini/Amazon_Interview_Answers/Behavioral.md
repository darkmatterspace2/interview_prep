# Amazon Behavioral Interview Questions & Answers (STAR Method)

*> Note: These are **sample** answers to demonstrate the structure. You must adapt them to your actual experience.*

---

## Part 1: Leadership Principles

### Ownership / Dive Deep

#### 91. Fixed a broken data pipeline.
**Situation:** Daily sales report failed due to a schema change in the upstream API.
**Task:** Restore the critical report before the executive meeting at 9 AM.
**Action:** I dived deep into the logs, identified the new field causing the failure. Since a full code fix would take hours, I implemented a quick hotfix to ignore the new field to unblock the pipeline (Bias for Action). I verified the data integrity manually.
**Result:** Report was delivered on time. I later implemented a Schema Registry key to prevent future unexpected breaking changes.

#### 92. Debugged a data discrepancy.
**Situation:** Finance and Marketing dashboards showed different revenue numbers implies ($50k gap).
**Task:** Identify the root cause and align the teams.
**Action:** I traced the lineage of both metrics. I found Finance was using "Invoiced Date" while Marketing used "Order Date".
**Result:** I standardized the definition in the Data Dictionary. We agreed to use "Invoiced Date" for official reporting. Trust in data increased.

#### 93. Found root cause of incorrect metrics.
*(See Q92)* - Focus on the *process* of debugging (queries, logs, meetings).

#### 94. Took ownership beyond your role.
**Situation:** The Data Science team was struggling to access raw data because permissions were manually managed by IT.
**Task:** Automate access control to speed up their work.
**Action:** Although I was a DE, I wrote a Terraform script to manage IAM roles via PRs.
**Result:** Reduced access request time from 3 days to 30 minutes.

#### 95. Improved reliability of data systems.
**Situation:** Our Spark jobs failed 20% of the time due to Spot Instance terminations.
**Task:** Improve stability without blowing the budget.
**Action:** I re-configured the EMR cluster to use On-Demand instances for the Master node and Spot for Task nodes, and implemented checkpointing.
**Result:** Failure rate dropped to < 1%.

### Bias for Action / Deliver Results

#### 96. Delivered under tight deadlines.
**Situation:** Client requested a new fraud detection feature in 2 days (normally a 1-week task).
**Task:** Deliver a working MVP.
**Action:** I negotiated the scope to remove "nice-to-have" UI features. I processed the data using a simple Lambda function instead of spinning up a new Kinesis app.
**Result:** Delivered on time. We refactored for scalability next sprint.

#### 97. Chose speed over perfection — why?
**Answer:** "In a startup environment, 'perfect' code that arrives too late is useless. I chose a simple SQL cron job over a complex Airflow DAG for a prototype to get feedback immediately. Once validated, I rebuilt it properly."

#### 98. Made a decision with incomplete data.
**Situation:** We had to choose a database (Redshift vs Snowflake) but didn't have full load test data.
**Task:** Make a choice to start development.
**Action:** I looked at our current team skills (strong SQL/AWS) and cost structure. I chose Redshift because it integrated natively with our existing IAM roles, minimizing setup risk.
**Result:** We launched on time. The decision held up for 2 years.

#### 99. Automated a manual process.
**Situation:** Analysts were manually downloading CSVs from an FTP server daily.
**Action:** wrote a Python script using `ftplib` and `boto3` to copy files to S3 automatically, triggered by Lambda.
**Result:** Saved 5 hours of analyst time per week.

#### 100. Reduced cost or improved performance measurably.
**Situation:** S3 costs were rising.
**Action:** I implemented Lifecycle Policies to move data to Glacier after 90 days and converted raw JSON logs to Parquet.
**Result:** Reduced storage costs by 40% ($2000/month).

---

## Part 2: Leadership Principle Stories

#### Customer Obsession
**Question:** Tell me about a time you pushed back on a requirement because it wasn't in the best interest of the customer.
**Sample:** "Product asked for a mandatory signup field that was causing 10% drop-off. I showed them the data and proposed making it optional. Conversions went back up."

#### Ownership (Critical Failure)
**Question:** Pipeline broke at 2 AM.
**Sample:** "I received PagerDuty alert. I jumped on, identified a memory leak. I upsized the cluster temporarily to clear the backlog (Bias for Action), then spent the next day refactoring the code to fix the leak permanently (Dive Deep)."
