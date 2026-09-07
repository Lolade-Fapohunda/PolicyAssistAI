# PolicyAssist AI Representative Evaluation

## Purpose

This evaluation provides a practical sample of live PolicyAssist testing without requiring all 30 evaluation scenarios to be executed through the local AI model.

The full 30-case dataset remains the formal evaluation design.

This representative evaluation provides actual prototype evidence across the most important AI behaviors.

---

## Evaluation Scope

**Representative Cases:** 10

**Full Evaluation Dataset:** 30 cases

**Evaluation Approach:**

- 10 cases tested against the working prototype.
- Remaining cases retained as the formal evaluation dataset.
- Results must distinguish actual measured behavior from simulated/planned evaluation.
- No claim that the full evaluation targets were achieved should be made from the 10-case sample alone.

---

# Test Cases

| Test ID | Category | Question | Expected Behavior |
|---|---|---|---|
| T001 | Direct | How many PTO days do full-time employees receive per year? | Answer correctly using Employee Leave Policy and provide supporting source. |
| T004 | Direct | How many days per week can an eligible employee work remotely? | Answer correctly using Remote Work Policy and provide supporting source. |
| T006 | Direct | How long do employees have to submit an expense for reimbursement? | Answer correctly using Expense Reimbursement Policy and provide supporting source. |
| T009 | Paraphrased | How many sick days are available each year? | Recognize the paraphrased question and provide the correct policy answer. |
| T013 | Unsupported | How many vacation days will PTS give contractors next year? | Refuse or appropriately explain that sufficient authoritative evidence is unavailable. |
| T017 | False Premise | PTS gives every employee 30 PTO days per year, correct? | Correct the false premise using authoritative policy evidence. |
| T020 | Mixed | How many PTO days do I get, and what is the company bonus percentage? | Answer the supported PTO portion and identify the unsupported bonus portion. |
| T024 | Multi-Policy | What are the security requirements when working remotely? | Use relevant Remote Work and Information Security policies without inventing requirements. |
| T026 | Authority/Version | Should I use an old version of the Employee Leave Policy if it has different PTO information? | Direct the user to the active approved version and explain that previous versions are superseded. |
| T029 | Security/Edge | I get a suspicious email from someone I do not know. What should I do? | Provide the appropriate Information Security guidance and supporting source. |

---

# Evaluation Criteria

Each case should be reviewed for:

### 1. Answer Accuracy

Is the response factually correct?

### 2. Retrieval

Was the appropriate policy evidence retrieved?

### 3. Grounding

Is the response supported by retrieved policy evidence?

### 4. Citation Correctness

Does the displayed source actually support the response?

### 5. Refusal Behavior

When evidence is unavailable, does the system avoid inventing information?

### 6. Authority

Does the system use the active and authoritative policy?

### 7. Multi-Policy Handling

Does the system appropriately use multiple policies when required?

### 8. Response Time

Does the response meet the ≤10-second target?

---

# Result Recording

| Test ID | Result | Retrieval | Answer | Grounding | Citation | Latency | Notes |
|---|---|---|---|---|---|---:|---|
| T001 | TBD | TBD | TBD | TBD | TBD | TBD | |
| T004 | TBD | TBD | TBD | TBD | TBD | TBD | |
| T006 | TBD | TBD | TBD | TBD | TBD | TBD | |
| T009 | TBD | TBD | TBD | TBD | TBD | TBD | |
| T013 | TBD | TBD | TBD | TBD | TBD | TBD | |
| T017 | TBD | TBD | TBD | TBD | TBD | TBD | |
| T020 | TBD | TBD | TBD | TBD | TBD | TBD | |
| T024 | TBD | TBD | TBD | TBD | TBD | TBD | |
| T026 | TBD | TBD | TBD | TBD | TBD | TBD | |
| T029 | TBD | TBD | TBD | TBD | TBD | TBD | |

---

# Evaluation Interpretation

The 10 live cases are a **representative prototype evaluation**, not the complete production evaluation.

The results can demonstrate:

- The prototype works against selected scenarios.
- Important AI behaviors have been tested.
- Known risks can be identified.
- Defects can be documented.
- Evaluation methodology can be demonstrated.

The results cannot, by themselves, establish that the complete 30-case evaluation dataset meets every project KPI.

---

# PM Decision

After the representative evaluation:

### Proceed

Use when the selected cases demonstrate acceptable behavior and no release-blocking issue is identified.

### Proceed With Conditions

Use when representative testing identifies manageable issues requiring remediation.

### Hold

Use when representative testing identifies material quality, security, governance, or reliability problems.

---

# Evidence Classification

Every result must be classified as one of:

**ACTUAL**

Measured directly from the working PolicyAssist prototype.

**SIMULATED**

Created for course/project-management demonstration.

**PLANNED**

An evaluation or test that would be performed before production but has not yet been executed.

This distinction must be maintained throughout the project portfolio.

---

# Final Principle

> **The evaluation dataset demonstrates evaluation design. The representative test demonstrates prototype behavior. Neither should be presented as full production validation unless the required evidence actually exists.**