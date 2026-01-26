## 8. Leadership, Coaching & Team Management

### 1. How do you balance **hands-on technical work vs leadership**?
**Answer:**
"In an Associate Director role, I expect a **20/80 split** (20% Hands-on, 80% Strategy/Management).
I stay hands-on by:
*   Conducting **Code Reviews**.
*   Writing **RFCs (Request for Comments)** and Architecture Design Docs.
*   Prototyping 'Spikes' for new tech (e.g., trying out a new Databricks feature) to evaluate if the team should adopt it.
I do *not* write critical path production code that would block the team if I’m in meetings."

### 2. How do you mentor junior and mid-level engineers?
**Answer:**
"I adhere to the 'See one, Do one, Teach one' model.
*   **Pair Programming:** I actively pair on complex problems, not to drive, but to navigate.
*   **Design Reviews:** I force them to write a design doc before coding. I critique the *design*, not just the syntax.
*   **Career Path:** I have monthly 1:1s focused solely on career growth (not status updates), mapping their work to the promotion rubric."

### 3. How do you handle **underperforming team members**?
**Answer:**
"Empathy first, then accountability.
1.  **Diagnose:** Is it a skill gap? Personal issue? Or lack of clarity?
2.  **Clear Expectations:** I set specific, measurable, short-term goals (Micro-goals).
3.  **Support:** I provide the resources/coaching needed to hit those goals.
4.  **Action:** If they consistently miss them despite support, I initiate a formal Performance Improvement Plan (PIP). Protecting the team's velocity and morale is paramount."

### 4. How do you prioritize platform work vs feature delivery?
**Answer:**
"This is the eternal struggle. I use a **'Tax' model**.
I negotiate with Product Management to reserve **20% of every sprint capacity** for 'Platform Engineering & Tech Debt' (The Tax).
*   Features get 80%.
*   We use that 20% to upgrade runtimes, refactor modules, or improve monitoring. This prevents the 'Big Bang Rewrite' scenario down the road."

### 5. Describe a time you had to **push back on stakeholders**.
**Answer:**
"A stakeholder wanted 'Real-Time' 1-second latency for a financial report that was only reviewed weekly.
I explained the **Cost vs. Value**.
'Real-time will cost /month in compute. Moving to a 1-hour refresh will cost /month. Is the 1-second latency worth .5k/month to the business?'
They immediately agreed to the 1-hour refresh. It's about framing technical constraints in business terms."

### 6. How do you build a culture of **engineering excellence and ownership**?
**Answer:**
"I treat operations as a software problem.
*   **You Build It, You Run It:** The team that writes the pipeline is on-call for it. This incentivizes them to write robust, error-free code because nobody wants to be woken up at 3 AM.
*   **Post-Mortems:** We have blameless post-mortems for every incident. The goal is 'How do we prevent this class of error?' not 'Who caused it?'."

### 7. How do you assess technical debt in data platforms?
**Answer:**
"I look for **Cognitive Load**.
If onboarding a new engineer takes 3 months because the code is spaghetti, debt is high.
If adding a new column requires changing code in 5 different places, debt is high.
I maintain a 'Tech Debt Radar' on our board and prioritize items based on 'Interest Rate' (how much is this slowing us down daily?)."

---

