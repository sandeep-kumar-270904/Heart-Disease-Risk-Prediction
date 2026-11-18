# HeartXAI 2.0 — Constrained Counterfactual Explanation Design

**Document ID:** `HX2-ML-011`  
**Version:** `1.0.0`  
**Phase:** Phase 8 — Machine Learning Research, Dataset Verification & Model Development Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal ML Research Scientist & Healthcare Safety Architect  
**Traceability:** FR-035–FR-039, NFR-001–NFR-028, ADR-001, ADR-003, HXAI-REQ-006  

---

## 1. Counterfactual Philosophy & Clinical Safety Mandate

Counterfactual explanations answer the question: *"What minimal changes to the patient's modifiable physiological inputs would cause the model's CAD association likelihood to decrease below a specific threshold $\tau$?"*

However, in medicine, **unconstrained algorithmic counterfactuals are dangerous**. An unconstrained optimizer might suggest:
- *"Decrease your age from 65 to 42."* (Biologically impossible).
- *"Change biological sex from Male to Female."* (Immutable historical risk marker).
- *"Reduce resting blood pressure to 40 mmHg."* (Fatal cardiogenic shock).
- *"Eliminate fluoroscopy calcification from 3 vessels to 0."* (Anatomically irreversible without surgical intervention).

```
┌────────────────────────────────────────────────────────────────────────┐
│                   THE THREE COUNTERFACTUAL SAFETY PILLARS              │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Non-Prescriptive Framing: Counterfactuals are hypothetical model    │
│    projections. They are NOT medical treatment prescriptions.          │
│ 2. Immutable Feature Locking: Age, biological sex, and anatomical      │
│    calcification are mathematically locked against perturbation.       │
│ 3. Biological Feasibility Clamps: Modifiable variables are bounded to  │
│    viable outpatient human survival ranges (e.g., BP floor ≥ 90 mmHg). │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Feature Actionability & Mutability Taxonomy

| Feature Name | Clinical Parameter | Actionability Classification | Permitted Simulation Range | Mathematical Constraint |
| :--- | :--- | :---: | :---: | :---: |
| `age` | Chronological Age | **Strictly Immutable** | Fixed at baseline | $\Delta x_0 = 0$ |
| `sex` | Biological Sex | **Strictly Immutable** | Fixed at baseline | $\Delta x_1 = 0$ |
| `ca` | Fluoroscopy Vessels | **Strictly Immutable** | Fixed at baseline | $\Delta x_{11} = 0$ |
| `thal` | Scintigraphy Defect | **Strictly Immutable** | Fixed at baseline | $\Delta x_{12} = 0$ |
| `restecg` | Resting ECG | **Diagnostic / Slow** | Fixed at baseline | $\Delta x_6 = 0$ |
| `trestbps` | Resting Systolic BP | **Modifiable (Lifestyle/Med)**| $[90.0, 200.0]\text{ mmHg}$ | Floor: $90\text{ mmHg}$ |
| `chol` | Total Serum Cholesterol | **Modifiable (Lipid target)** | $[120.0, 350.0]\text{ mg/dL}$ | Floor: $120\text{ mg/dL}$ |
| `fbs` | Fasting Glucose $>120$ | **Modifiable (Metabolic)** | $\{0, 1\}$ | Binary toggle |
| `thalach` | Max Heart Rate Achieved | **Modifiable (Conditioning)** | $[80.0, 200.0]\text{ bpm}$ | Cap: $220 - \text{age}$ |
| `exang` | Exercise Angina | **Symptom Outcome** | $\{0, 1\}$ | Binary toggle |
| `oldpeak` | ST Depression (oldpeak) | **Ischemia Marker** | $[0.0, 4.0]\text{ mm}$ | Floor: $0.0\text{ mm}$ |

---

## 3. Mathematical Optimization Formulation

To find the optimal counterfactual $\mathbf{x}^* \in \mathcal{X}$ given patient baseline $\mathbf{x}_{\text{orig}}$:

$$\mathbf{x}^* = \arg\min_{\mathbf{x}'} \left[ \text{dist}(\mathbf{x}_{\text{orig}}, \mathbf{x}') + \lambda \cdot \left( \max(0, f(\mathbf{x}') - \tau) \right)^2 \right]$$

### Constraints:
1. **Target Threshold:** $f(\mathbf{x}') \le \tau$ (e.g., $\tau = 0.30$, moving into the Low Association Band).
2. **Immutable Mask:** $\mathbf{x}'_j = \mathbf{x}_{\text{orig}, j}$ for all $j \in \{\text{age}, \text{sex}, \text{ca}, \text{thal}, \text{restecg}\}$.
3. **Biological Feasibility Bounds:** $\mathbf{L}_j \le \mathbf{x}'_j \le \mathbf{U}_j$ for all modifiable features $j$.
4. **Distance Metric (Gower Distance):**
   $$\text{dist}(\mathbf{x}, \mathbf{x}') = \frac{1}{|M|} \sum_{j \in M} \frac{|\mathbf{x}_j - \mathbf{x}'_j|}{\text{Range}_j}$$
   where $M$ is the set of modifiable variables, normalized by clinical range ($\text{Range}_{\text{BP}} = 110\text{ mmHg}$, $\text{Range}_{\text{chol}} = 230\text{ mg/dL}$). This enforces **sparsity** (preferring small adjustments in 1 or 2 variables over changing everything).

---

## 4. The Two Counterfactual Execution Modes

HeartXAI 2.0 implements **Two Complementary User Modes**:

### Mode 1: Interactive Exploration (User-Driven Sliders)
- The patient or clinician manually moves sliders for systolic BP, cholesterol, or heart rate.
- The UI recalculates $f(\mathbf{x}')$ at 60fps using `useDeferredValue`.
- Immutable variables display locked padlock icons with explanatory tooltips: *"Biological baseline factor cannot be modified in simulations."*
- Sliders cannot be dragged beyond biological clamps ($[90, 200]\text{ mmHg}$).

### Mode 2: Algorithmic Target Discovery (Automated Sparse Solver)
- The user clicks `[Find Smallest Feasible Target Scenario]`.
- The constrained solver finds the single or dual parameter modification that achieves $\tau = 0.30$ with minimal Gower distance:
  - *Example Scenario:* *"Reducing resting blood pressure by 24 mmHg (from 154 to 130 mmHg) while holding cholesterol constant is projected to lower the model's CAD association likelihood by 14%."*

---

## 5. Medical Safety Guardrails & Mandatory Framing

1. **Permanent Disclaimer Header:**
   > *"Hypothetical Exploration Only: This simulator demonstrates how the mathematical model responds to modified inputs. It is not a personalized medical treatment plan or medical prescription. Never alter prescribed medications, dosages, or lifestyle routines without consulting a licensed healthcare provider."*
2. **Non-Prescriptive Language Enforcement:**
   - Prohibited: *"You must lower your cholesterol to 180 mg/dL to prevent a heart attack."*
   - Approved: *"In a hypothetical scenario where serum cholesterol is modeled at 180 mg/dL while other parameters remain constant, the model's estimated CAD likelihood decreases from 42% to 34%."*
3. **Clinical Feasibility Validation:** A generated counterfactual represents mathematical sensitivity, not a medical guarantee of reversibility. Plaque calcification in coronary arteries cannot be resolved simply by modifying lifestyle inputs.
