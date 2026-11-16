# HeartXAI 2.0 — Healthcare UX Safety Guidelines

**Document ID:** `HX2-DES-010`  
**Version:** `2.0.0`  
**Status:** `Approved Specification`  
**Author:** Healthcare UX Safety Lead & Principal Product Designer  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011  

---

## 1. Principles of Responsible Healthcare UX

Healthcare interfaces carry serious ethical and epistemological responsibilities. A poorly worded notification can induce severe anxiety or panic; an overconfident AI score can cause a patient to neglect life-threatening symptoms; an ambiguous measurement unit can lead to dangerous clinical misunderstandings.

HeartXAI 2.0 adheres to **Six Cardinal Healthcare Safety Principles**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   SIX CARDINAL HEALTHCARE SAFETY RULES                 │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Non-Diagnostic Epistemological Humility                             │
│ 2. Mathematical Explainability without Causal Fallacy                  │
│ 3. Hypothetical Scenarios, Never Prescriptive Treatment                │
│ 4. Immediate and Unambiguous Emergency Escalation                      │
│ 5. Compulsory Unit Binding and Physiological Guardrails                │
│ 6. Accessible Multi-Sensory Warning Indicators (No Color Alone)        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Epistemological Language & Phrasing Standards

### 2.1 The Non-Diagnostic Framing Rule
The application **must never** state or imply that it is providing a medical diagnosis, definitive clinical prognosis, or treatment directive.

| Prohibited Misleading Phrasing | Approved Epistemologically Sound Phrasing | Safety Rationale |
| :--- | :--- | :--- |
| *"You have a 74% risk of coronary heart disease."* | *"The machine learning model estimated a 74% statistical likelihood of angiographic CAD association, benchmarked against historical study cohorts."* | Distinguishes statistical pattern matching in cohort data from a personalized clinical diagnosis. |
| *"Diagnosis: Moderate Coronary Artery Disease."* | *"Assessment Outcome: Moderate CAD Association Likelihood."* | The term "Diagnosis" is legally and medically restricted to licensed human practitioners. |
| *"Your heart is healthy / normal."* | *"Your reported measurements fall within typical baseline limits across the evaluated clinical parameters."* | Prevents false reassurance in patients who may have cardiovascular conditions outside the model's 13 features. |
| *"Consult a doctor immediately to cure your condition."* | *"Please share and discuss these educational findings with your physician during your next clinical consultation."* | De-escalates panic while establishing physician consultation as the primary decision channel. |

---

## 3. Explainability & Causal Communication Guardrails

### 3.1 SHAP Attribution: Feature Weight vs Biological Causation
SHAP (SHapley Additive exPlanations) values represent the mathematical sensitivity of an XGBoost tree ensemble to individual input features; they **do not prove biological etiology or direct causality**.

```
┌────────────────────────────────────────────────────────┐
│                      MATHEMATICAL REALITY              │
│  SHAP attribution: Higher Cholesterol pushed model     │
│  output likelihood up by +0.081.                       │
├────────────────────────────────────────────────────────┤
│                   CRITICAL DISTINCTION                 │
│  ✓ "Cholesterol contributed positively to the model's   │
│     statistical estimation."                           │
│  ✗ "Your cholesterol is directly causing plaque in     │
│     your coronary arteries."                           │
└────────────────────────────────────────────────────────┘
```

* **Interface Rules for SHAP Presentations:**
  - Every SHAP visual must include a persistent explanatory caption: *"Feature impacts reflect statistical contributions to this model's prediction and do not constitute biological proof of disease cause."*
  - Features must be described as *contributing factors in the model*, never as *the cause of your heart disease*.

---

## 4. Counterfactual Scenarios: Simulation vs Prescription

### 4.1 "What-If" Explorer Boundaries
The Counterfactual Explorer allows users to modify variables (e.g., lower cholesterol from 245 to 190 mg/dL) and view simulated changes in predicted likelihood.

* **Mandatory Framing Rules:**
  1. **Permanent Disclaimer Header:** *"Hypothetical Simulation: Modifying values in this tool illustrates mathematical model behavior. It is not a personalized treatment plan or medical prescription."*
  2. **Non-Prescriptive Action Labels:**
     - Prohibited: *"Lower your blood pressure to 120 mmHg to reduce risk."*
     - Approved: *"Simulating a blood pressure of 120 mmHg reduces the model's association likelihood by 12%."*
  3. **Physiological Feasibility Clamps:**
     - Sliders must be locked within biologically viable ranges ($[70, 240]\text{ mmHg}$, $[100, 500]\text{ mg/dL}$).
     - Unmodifiable biological variables (Age, Biological Sex) are locked from manipulation with an explicit padlock icon and tooltip: *"Biological baseline factor cannot be modified in simulations."*

---

## 5. Emergency Protocol & Symptom Escalation

### 5.1 Acute Symptom Intercepts
If a patient enters measurements or symptoms indicative of acute coronary syndrome or malignant hypertensive crisis:
- **Resting Chest Pain:** Selecting `Typical Angina` or `Atypical Angina` accompanied by `Resting BP Systolic ≥ 180 mmHg` or `ST Depression ≥ 2.5 mm`.

```
┌────────────────────────────────────────────────────────────────────────┐
│ 🚨 URGENT MEDICAL NOTICE                                              │
├────────────────────────────────────────────────────────────────────────┤
│ The measurements or symptoms you entered indicate severe acute strain  │
│ or potential cardiac distress.                                         │
│                                                                        │
│ DO NOT rely on an outpatient web platform or wait for an appointment.  │
│ If you are experiencing chest tightness, pain radiating to your jaw/arm│
│ or severe shortness of breath:                                         │
│                                                                        │
│ [ 📞 Call Emergency Services: 112 / 102 / 911 ]  [ Find Nearest ER ]   │
└────────────────────────────────────────────────────────────────────────┘
```

* **Implementation Rules:**
  - The alert banner renders in solid Crimson (`#FEF2F2` background, `#DC2626` border, `#B91C1C` text).
  - The alert persists at the top of the viewport and cannot be dismissed without explicit confirmation.
  - The emergency call button dynamically surfaces the national emergency number based on the patient's active country configuration (`112` in India/Europe, `911` in USA, `999` in UK).

---

## 6. Biomarker Units & Data Integrity Disciplines

### 6.1 Compulsory Unit Affixes
A number displayed without a unit in medicine is dangerous.
- **Rule:** Every clinical metric displayed in cards, tables, inputs, or charts **must have its physical unit visibly anchored adjacent to the value** (e.g., `140 mmHg`, `210 mg/dL`, `5.4 mmol/L`, `78 bpm`).
- **Input Guard:** When toggling between unit systems ($\text{mg/dL} \leftrightarrow \text{mmol/L}$), the input field value must convert mathematically and display the new unit symbol instantly.

### 6.2 Missing Data & Imputation Transparency
When optional advanced laboratory or imaging features are omitted by a user (e.g., Major Vessels Fluoroscopy `ca` or Thallium Stress `thal`):
- The system uses cohort median imputation to execute the model.
- **Rule:** The interface **must visibly flag** any imputed variables in the final assessment overview:
  - *"Note: Fluoroscopy vessel count was not provided; the model utilized cohort median baseline values. For the most accurate assessment, provide complete diagnostic test results."*

---

## 7. Multi-Sensory Warning Discipline (No Color Alone)

To prevent miscommunication for individuals with color vision deficiencies:
- **Never rely on color alone:** Red, yellow, or green must always be accompanied by:
  1. **An explicit icon:** `CheckCircle2` (Normal), `AlertTriangle` (Moderate/Caution), `AlertCircle` / `OctagonX` (Elevated/Danger).
  2. **An explicit text stratum:** `"Low Likelihood"`, `"Moderate Likelihood"`, `"Elevated Likelihood"`.
  3. **An exact numeric percentage range:** `"< 30%"`, `"30% – 69%"`, `"≥ 70%"`.
  4. **An ARIA status attribute:** `role="status"` or `aria-live="polite"`.
