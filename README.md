**Clinical Trials** are research studies conducted on people to evaluate new medical interventions, like drugs, therapies, or devices, for safety and effectiveness.

But traditional trial matching and protocol design processes often struggle with challenges:

- Over **80% of trials miss enrollment deadlines**, and 1 in 5 terminate early due to **poor participant recruitment**.
- Overly rigid Inclusion & exclusion criteria, resulting in **large ratio of patient disqualification.**
- **Manual & error-prone matching:** Clinicians must navigate registries, parse eligibility criteria, and compare them to complex patient histories.
- Existing tools have **limited automation** and rely on keyword or rule-based filtering—not leveraging AI.
- Lacks smart optimizations based on historical/similar trial data.

### Solution Overview: Criteria-AI

Criteria-AI is a multi-agent, LLM-powered system designed to solve two major bottlenecks in clinical trial process:

1. **Clinical Trial Matching**
   - AI evaluates patient profiles and cross-references real-world clinical trials (fetched from ClinicalTrials.gov) to assess trial fit—reasoning over inclusion & exclusion logic.

2. **Protocol Optimization**
   - After analyzing trial eligibility criteria, agents simulate the impact of optimizing parameters such as age range or biomarker thresholds.

**Outcome**: Translate raw clinical and patient data into high-impact insights—quantitative, explainable, and actionable.

---

## Feature 1: Match Trials (Clinical Trial Matching Workflow)
Match patient to real-world clinical trials using structured + AI-enhanced reasoning
![Clinical Trial Matching Workflow](https://github.com/adityashukla8/clinicaltrials-multiagent/raw/master/assets/Clinical%20Trial%20Matching%20Workflow.png)

### 🤖 Agents
- **Agent 1: Patient Eligibility Match**
  - Compares inclusion/exclusion criteria with patient profile
  - **Output**:
    - Match / No Match
    - Reason for match status
    - Required changes (if any) to qualify

- **Agent 2: Tavily Web Search Agent**
  - Enriches matched trials with:
    - Sponsor details
    - Enrollment info
    - Known side effects
    - Statistical plan
    - Sample size
    - Monitoring requirements

### 🔨 Tools
- **AppWrite**: Fetch patient info from DB
- **ClinicalTrials.gov**: Source of real-world trial data
- **Tavily**: Conducts web search across 60+ medical trial sources

---

## Feature 2: Optimize Protocol (Protocol Optimization Workflow)
Suggest data-driven optimizations to improve trial eligibility and recruitment rate
![Protocol Optimization Workflow](https://github.com/adityashukla8/clinicaltrials-multiagent/raw/master/assets/Clinical%20Trial%20Protocol%20Optimization%20Workflow.png)

### 🤖 Agents
- **Agent 3: Age Gap Optimization**
  - Simulates impact of altering age eligibility range
  - **Computes**:
    - % increase in eligible patients
    - Missed due to lower/upper limits
    - Revised age range recommendation
    - Clinical justification

- **Agent 4: Biomarker Threshold Agent**
  - Evaluates impact of relaxing biomarker criteria
  - **Computes**:
    - Estimated gain
    - Suggested new inclusion
    - Clinical rationale

- **Agent 5: Supervisor Summary Agent**
  - Synthesizes outputs from Age Gap and Biomarker agents
  - Compares against current protocol
  - **Generates a unified optimization report**:
    - Summary impact
    - Clinical Recommendations
    - Quantitative Estimates
    - Explanation

### 🔨 Tools
- **AppWrite**: Fetch all patient records
- **ClinicalTrials.gov**: Fetch trial metadata (Eligibility Criteria, Age Limits, Biomarkers, etc.)

<!-- ### Architecture -->
<!-- ![Architecture]() -->

## What's next for Criteria-AI

- Incorporate more Protocol Optimization Agents (ECOG analysis agent, Histology Agent, Geographic/Location Agent etc.)
- Leverage Tavily further for Clinical Evidence by fetching historical, similar clinical trials.