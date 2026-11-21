# COUNTERFACTUAL EXPLANATION TESTING AND SAFETY SPECIFICATION

**Document Reference:** `docs/quality/COUNTERFACTUAL_TESTING_STRATEGY.md`  
**Phase:** 11 — Comprehensive Testing Strategy, Quality Assurance & Validation Framework  
**Status:** Approved Technical Architecture  
**Author:** Algorithmic Safety Engineer & Medical Informatics QA Lead  
**Traceability:** FR-PRED-05, NFR-REL-01, ADR-001, ADR-009  

---

## 1. Executive Summary & Algorithmic Safety Boundary

Counterfactual explanations answer the "What-If" question: *What is the minimal perturbation to a patient's input biomarkers that flips the model's classification from high risk to low risk?*

In clinical AI, unconstrained mathematical optimizers can generate catastrophic recommendations: suggesting an elderly patient reduce their chronological age, reverse calcified coronary vessels (`ca`), or lower systolic blood pressure to $40\text{ mmHg}$ (fatal circulatory collapse).

HeartXAI 2.0 enforces strict mathematical box constraints and biological feasibility clamps. This specification defines the automated test suite (`backend/tests/ml/test_counterfactual_safety.py`) asserting algorithmic validity and physiological safety.

---

## 2. Counterfactual Invariant Verification Matrix

Every generated counterfactual candidate vector $x^*$ is evaluated against five mandatory safety criteria:

```mermaid
graph TD
    CF[Generated Counterfactual Candidate: x*] --> T1{1. Class Inversion Assertion: Model(x*) < 0.50}
    T1 -- Failed --> Reject1[TEST FAILED: Target probability not achieved]
    T1 -- Passed --> T2{2. Immutable Feature Invariance: Delta Age == 0, Delta Sex == 0}
    T2 -- Failed --> Reject2[TEST FAILED: Unsafe mutation of immutable baseline]
    T2 -- Passed --> T3{3. Physiological Safety Floors: BP* >= 90, Chol* >= 100}
    T3 -- Failed --> Reject3[TEST FAILED: Hypotension / Non-physiological clamp breached]
    T3 -- Passed --> T4{4. Semi-Actionable Feasibility: Delta MaxHR <= +35 bpm}
    T4 -- Failed --> Reject4[TEST FAILED: Physiologically impossible conditioning jump]
    T4 -- Passed --> T5{5. Solver Timeout Assertion: Execution <= 75 ms}
    T5 -- Passed --> ApprovedCF[Counterfactual Approved for Client Delivery]
```

---

## 3. Detailed Automated Safety Assertions

### 3.1 Immutable Baseline Invariance Test
- **Assertion:** For 100 high-risk test patients evaluated by the counterfactual engine:
  $$\Delta \text{age} = 0.0, \quad \Delta \text{sex} = 0.0, \quad \Delta \text{ca} = 0.0$$
- **Verification Rule:** If any generated candidate suggests changing biological sex, reversing chronological age, or reducing fluoroscopy-detected vessel calcification, the test immediately fails with a critical defect.

### 3.2 Physiological Safety Floors Test
- **Assertion:** Actionable cardiovascular vitals must never be optimized into dangerous clinical extremes:
  - $\text{trestbps}^* \ge 90\text{ mmHg}$ (prevents fatal hypotensive collapse).
  - $\text{chol}^* \ge 100\text{ mg/dL}$ (prevents severe hypocholesterolemia).
  - $\text{thalach}^* \le 200\text{ bpm}$ (caps maximum exercise heart rate).

### 3.3 Class Inversion Verification Test
- **Assertion:** When the generated counterfactual feature vector $x^*$ is fed into the primary calibrated XGBoost pipeline (`app/ml/engine.py`), the resulting calibrated probability must evaluate strictly below the decision threshold:
  $$P(\text{CAD} \ge 50\% \mid x^*) < 0.50$$
  Verifies that the generated recommendation mathematically achieves the claimed risk reduction.

### 3.4 Infeasible Scenario Handling Test
- If a patient has multiple severe immutable risk factors (e.g. age $78$, male, $3$ calcified vessels on fluoroscopy) such that no combination of lifestyle perturbations can lower the score below $0.50$ without violating physiological safety floors:
  - The solver must gracefully terminate within 50 iterations ($< 75\text{ ms}$).
  - The API returns an empty counterfactual list paired with an explicit clinical status:  
    `{"status": "INFEASIBLE_WITHIN_PHYSIOLOGICAL_BOUNDS", "message": "Baseline clinical factors dominate model score; lifestyle changes alone cannot shift algorithmic classification."}`
  - Asserts that the system never invents extreme or impossible perturbations to satisfy a mathematical objective.

---

## 4. UI Non-Prescriptive Framing Audit

- **Copy Assertion (`tests/safety/test_counterfactual_framing.py`):**
  - Asserts that the client UI never frames counterfactual differences as personalized medical prescriptions or medication regimens.
  - Asserts the presence of the mandatory clinical guardrail:  
    `[SENSITIVITY ANALYSIS ONLY: These values represent algorithmic sensitivity bounds within the model. They are NOT medical prescriptions or treatment plans. Never alter prescribed therapies without consulting a licensed cardiologist.]`
