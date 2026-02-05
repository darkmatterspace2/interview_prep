This is **principal-level breadth with senior-level depth**.
Below is an **advanced, interview-grade question bank** across the exact themes you listed. These questions test **judgment, architecture maturity, and real production experience**, not theory.

Use this to prepare for **Amazon / big-tech DE system & behavioral hybrids**.

---

# 🔥 ADVANCED DATA & SOFTWARE ENGINEERING – QUESTION BANK

---

## 1️⃣ Full Software Development Life Cycle (SDLC) – Advanced

### Architecture & Design

1. How do you choose between **monolith, modular monolith, and microservices** for data platforms?
2. What architectural principles matter most for **data systems** vs application systems?
3. How do you design for **backward compatibility** in data pipelines?
4. How do you design APIs for **data consumption**?
5. How do you prevent tight coupling between producers and consumers?

---

### Coding Standards & Maintainability

6. What coding standards matter most in data pipelines?
7. How do you enforce standards across large teams?
8. How do you balance **performance vs readability**?
9. What makes data code **hard to refactor**?
10. How do you manage technical debt in pipelines?

---

### Code Reviews (High Signal)

11. What do you look for in a data engineering code review?
12. How do you review SQL for correctness and performance?
13. How do you detect hidden data quality bugs in PRs?
14. How do you review Spark code differently from Python services?
15. What are common red flags in data PRs?

---

### Source Control & Branching

16. GitFlow vs trunk-based development — which fits data teams better?
17. How do you version SQL and schemas?
18. How do you manage long-running feature branches in data projects?
19. How do you handle merge conflicts in SQL?
20. What should never be committed to source control?

---

### CI/CD & Continuous Deployment

21. How do you safely deploy data pipeline changes?
22. Blue-green vs canary deployments for data systems?
23. How do you roll back data changes?
24. What should a data CI pipeline validate?
25. How do you prevent breaking downstream consumers?

---

### Testing Strategy

26. Unit testing for data pipelines — what is testable?
27. Data tests vs software tests — differences?
28. How do you test Spark jobs?
29. Contract testing for data producers/consumers.
30. Why most data tests fail in practice?

---

### Operational Excellence

31. What does **operational excellence** mean for data systems?
32. Metrics that indicate pipeline health.
33. How do you reduce on-call burden for data teams?
34. Runbooks — what belongs in them?
35. How do you do post-mortems for data incidents?

---

## 2️⃣ Best Practices in Data Engineering (Advanced)

36. What makes a data platform **scalable**?
37. How do you design for **reprocessing and backfills**?
38. Idempotency — why it matters and how to implement it.
39. How do you avoid “data swamps”?
40. When should data pipelines fail fast vs be tolerant?

---

## 3️⃣ Non-Relational Databases & Data Stores

### Object Storage

41. Why object storage is the backbone of modern data platforms.
42. Performance pitfalls of object storage.
43. How do you design datasets for efficient reads?
44. Object storage consistency guarantees — implications.

---

### Key-Value & Document Stores

45. When do you choose DynamoDB / CosmosDB / Redis?
46. How do access patterns drive NoSQL design?
47. Hot partition problem — detection and mitigation.
48. Schema evolution in document stores.

---

### Column-Family Databases

49. When is Cassandra a good choice?
50. Write-optimized vs read-optimized trade-offs.
51. TTLs — when and when not to use.
52. Secondary indexes — dangers.

---

### Graph Databases

53. When is a graph DB justified?
54. Why graph DBs often fail at scale.
55. Modeling relationships vs joins.
56. Analytics on graph data — alternatives.

---

## 4️⃣ Integration with Analytics & ML Platforms

57. How do data pipelines differ for **analytics vs ML**?
58. Feature engineering — batch vs online features.
59. Feature stores — why they exist.
60. Data leakage — how pipelines cause it.
61. Training-serving skew — prevention strategies.

---

62. How do you design pipelines to support:

* Ad-hoc analysis
* Dashboards
* ML training
* Real-time inference

63. How do you manage dataset versioning for ML?
64. Offline vs online feature computation trade-offs.
65. How do you validate data before model training?

---

## 5️⃣ Data Modeling for Analytics, Reporting & ML

66. How does modeling differ for:

* BI
* ML
* Operational reporting

67. Why star schemas still matter.
68. When denormalization is the right choice.
69. Wide tables vs narrow tables — trade-offs.
70. How do you design time-aware models?

---

71. Handling slowly changing dimensions in ML.
72. Feature explosion — how to control it.
73. How do you design models that survive schema changes?
74. Metrics definitions — how to avoid inconsistency.
75. Semantic layer — why it matters.

---

## 6️⃣ Data Quality, Reliability & Process Improvements

### Data Quality

76. What is “good” data quality?
77. Preventive vs detective quality checks.
78. How do you prioritize quality checks?
79. Data freshness vs accuracy trade-offs.
80. When bad data is acceptable.

---

### Reliability Engineering

81. What are data SLOs?
82. How do you design pipelines with graceful degradation?
83. Replayability — design patterns.
84. Checkpointing and watermarking — when needed.
85. Handling partial failures.

---

### Observability

86. Difference between monitoring and observability.
87. Golden signals for data pipelines.
88. How do you debug data issues faster?
89. Lineage — how much is enough?
90. Impact analysis when things break.

---

### Continuous Improvement

91. How do you identify pipeline bottlenecks?
92. How do you sunset unused datasets?
93. How do you measure ROI of data work?
94. How do you drive quality culture across teams?
95. Automation opportunities in data platforms.

---

## 7️⃣ Scenario-Based “Judge Your Maturity” Questions

96. A pipeline is correct but too slow — what do you do?
97. Data is fast but sometimes wrong — what do you fix first?
98. ML model accuracy dropped — where do you investigate?
99. Business complains dashboards don’t match numbers.
100. You inherit a fragile data platform — first 90 days plan.

---

## 🧠 How Interviewers Evaluate These

They listen for:

* **Decision frameworks**
* **Trade-offs**
* **Real failure stories**
* **Preventive thinking**
* **Business alignment**

They reject:

* Tool-only answers
* Absolutist thinking
* Over-engineering

---

## 🎯 How to Prepare (Smart Way)

For each topic:

* Have **1 success story**
* Have **1 failure & lesson**
* Have **1 trade-off example**

That signals **senior maturity**.

---
