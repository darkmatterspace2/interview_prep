Below is a **realistic, Airbnb-style interview question set** mapped **directly to the job description**, not generic DE questions. This mirrors how Airbnb typically evaluates **senior data engineers**: depth in distributed systems + strong product & data thinking (merchandising focus).

I’ve grouped questions by **interview rounds / competencies** so you can prepare structurally.

---

## 1️⃣ Data Pipeline Design & Architecture (Core Round)

**High-probability questions**

1. Design an end-to-end data pipeline to capture **user interactions (clicks, searches, bookings)** and make it available for **merchandising optimization**.
2. How would you design a pipeline that ingests **batch + real-time data** at Airbnb scale?
3. How do you handle **late-arriving events** in user interaction data?
4. What strategies do you use to make pipelines **idempotent**?
5. How do you design pipelines to handle **schema evolution** without breaking downstream consumers?
6. Explain how you would design a **petabyte-scale Spark pipeline** that runs daily and hourly workloads.
7. How do you decide between **batch vs streaming** for a given use case?
8. What trade-offs exist between **Lambda vs Kappa architecture**?

**Follow-ups Airbnb likes**

* What metrics would you track to know the pipeline is healthy?
* How would you backfill 6 months of corrupted data?

---

## 2️⃣ Spark, SparkSQL & Scala (Very Important)

**Deep-dive questions**

1. Explain Spark’s **execution model** (DAG, stages, tasks).
2. Difference between **narrow vs wide transformations** with real examples.
3. How does **SparkSQL Catalyst Optimizer** work?
4. How do you optimize a slow SparkSQL query scanning billions of rows?
5. When would you use **Dataset vs DataFrame vs RDD**?
6. Explain **shuffle**, why it’s expensive, and how you minimize it.
7. How do you handle **data skew** in Spark?
8. What are **broadcast joins** and when do they fail?
9. How do you tune **Spark memory** (executor vs driver)?

**Scala-specific**

* How does immutability help in distributed systems?
* Example of writing a type-safe Spark Dataset in Scala

---

## 3️⃣ Airflow & Workflow Orchestration

**Likely questions**

1. How does Airflow work internally? (Scheduler, Executor, Metastore)
2. Design an Airflow DAG for:

   * Raw → Clean → Aggregated → ML-ready tables
3. How do you manage **dependencies between hundreds of DAGs**?
4. How do you implement **backfills safely**?
5. Difference between **catchup**, **depends_on_past**, and **SLAs**.
6. How do you handle **partial DAG failures**?
7. How would you design Airflow to support **multi-tenant teams**?

**Advanced**

* Airflow scaling challenges at large companies
* When Airflow is the wrong tool

---

## 4️⃣ Data Modeling & Warehousing (Merchandising Focus)

**High-signal questions**

1. How would you model data for **listing ranking and merchandising optimization**?
2. Explain **fact vs dimension tables** using Airbnb listings.
3. How would you design a table to track **price changes over time**?
4. How do you handle **slowly changing dimensions (SCD Type 2)**?
5. How do you balance **query performance vs storage cost**?
6. How would you design data models for **A/B experiments**?

**Warehousing**

* Difference between row-based vs columnar storage
* When would you choose ClickHouse vs BigQuery vs Redshift?

---

## 5️⃣ Data Quality, Reliability & Observability (Airbnb Cares a LOT)

**Common questions**

1. How do you define **data quality**?
2. How do you detect **missing, duplicated, or anomalous data** automatically?
3. How do you design **data validation checks** at scale?
4. What happens when a bad pipeline publishes wrong data to business dashboards?
5. How would you implement **data contracts**?
6. What SLAs/SLOs make sense for data pipelines?

**Scenario**

> A dashboard used by leadership shows a 20% drop in bookings. What do you do?

---

## 6️⃣ Distributed Systems & Scale

**Expected depth**

1. How does Kafka guarantee ordering?
2. Exactly-once vs at-least-once semantics—trade-offs?
3. How would you design a pipeline handling **millions of events/sec**?
4. What happens when a Spark executor dies?
5. How do you handle **hot partitions**?
6. How do you design systems that degrade gracefully?

---

## 7️⃣ Collaboration & Product Thinking (Behavioral but Technical)

Airbnb strongly values **product-aware engineers**.

**Questions**

1. How do you work with Data Scientists to productionize features?
2. How do you push back when PMs request unrealistic data timelines?
3. Describe a time you improved data usability for non-technical users.
4. How do you prioritize tech debt vs feature delivery?
5. How do you influence standards without authority?

---

## 8️⃣ Code Quality & Internal Tooling

**Likely**

1. How do you enforce code quality in data pipelines?
2. What CI/CD checks would you add for Spark jobs?
3. How do you do safe deployments for data pipelines?
4. Describe a tool you built that improved data engineering productivity.
5. How do you detect breaking schema changes automatically?

---

## 9️⃣ SQL & Analytics Thinking

**Real-world SQL**

1. Write a query to find listings whose **conversion dropped WoW**.
2. How would you detect **outliers in pricing data** using SQL?
3. Window functions you frequently use and why.
4. How do you optimize a slow analytical query?

---

## 🔟 Airbnb-Style System Design Question (Very High Probability)

> **Design a data platform that supports real-time and batch merchandising optimization for Airbnb listings.**

They expect:

* Data sources
* Ingestion (Kafka / batch)
* Storage layers
* Processing (Spark)
* Modeling
* Data quality
* Consumers (DS, dashboards, ML)
* Monitoring & failure handling

---

## 🎯 How You Should Prepare (Given Your Background)

Given your **Databricks + Spark + Azure + CI/CD** experience:

* Map **Unity Catalog → Airbnb data governance**
* Map **Delta Lake → internal Airbnb lake**
* Emphasize **data quality + product impact**, not just tech
* Prepare **1–2 strong stories** where your work directly improved business metrics

---

If you want, next I can:

* 🔥 Do **mock Airbnb system design**
* 🧠 Give **model answers** for top 15 questions
* 🎯 Tailor answers **specifically to your resume**

Just tell me.
