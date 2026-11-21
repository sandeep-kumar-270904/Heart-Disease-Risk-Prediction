# HeartXAI 2.0 — Healthcare & Scientific Validity Audit
**Document ID:** HX-PR-004  
**Version:** 1.0.0  
**Phase:** 12 — Final Pre-Implementation Audit, Architecture Consolidation & Master Development Roadmap  
**Author:** Healthcare AI Product Engineer & Senior Machine Learning Research Scientist  
**Status:** Approved for Implementation Planning  
**Date:** November 2026  

---

## 1. Executive Summary

Healthcare software that incorporates artificial intelligence requires rigorous scientific validation. When machine learning models trained on retrospective clinical cohorts are deployed to consumers or healthcare professionals, any ambiguity regarding what the model actually predicts creates severe clinical, legal, and ethical risks.

This audit establishes the definitive scientific boundaries for HeartXAI 2.0, provides a mathematical evaluation of the dataset, defines the prediction targets, outlines calibration requirements, and establishes an authoritative ledger of prohibited clinical claims.

---

## 2. Epistemological Ground Truth: Task A vs. Task B

A pervasive failure mode in cardiovascular machine learning projects is conflating **cross-sectional angiographic disease detection** with **prospective longitudinal risk prediction**. HeartXAI 2.0 strictly distinguishes these two paradigms:

```
+---------------------------------------------------------------------------------------------------------+
|                                    THE CRITICAL CLINICAL DISTINCTION                                    |
+---------------------------------------------------------------------------------------------------------+
| Characteristic          | Task A: Angiographic CAD Classification   | Task B: Prospective 10-Yr ASCVD   |
|                         | (Approved Primary ML Subsystem)           | (Deterministic Module / Deferred) |
+-------------------------+-------------------------------------------+-----------------------------------+
| Clinical Question       | "Does this patient currently have >=50%   | "What is the probability of an   |
|                         | diameter stenosis in a coronary artery?"  | incident heart attack or stroke   |
|                         |                                           | over the next 10 years?"          |
+-------------------------+-------------------------------------------+-----------------------------------+
| Study Design            | Cross-sectional observational cohort      | Longitudinal prospective cohort   |
|                         | (referred for catheterization).           | (general population follow-up).   |
+-------------------------+-------------------------------------------+-----------------------------------+
| Ground Truth Evidence   | Invasive X-ray coronary angiography       | Adjudicated clinical endpoints    |
|                         | performed at study baseline.              | over 10 to 30 years of follow-up. |
+-------------------------+-------------------------------------------+-----------------------------------+
| Validating Benchmark    | UCI Heart Disease Cleveland ($N=303$)     | Framingham Heart Study,           |
|                         |                                           | Multi-Ethnic Study of Athero.     |
+-------------------------+-------------------------------------------+-----------------------------------+
| Permissible ML Claim    | "Estimated statistical likelihood of      | "Estimated 10-year statistical    |
|                         | significant coronary artery stenosis."    | risk of an ASCVD event."          |
+-------------------------+-------------------------------------------+-----------------------------------+
```

### 2.1 Scientific Verdict on the UCI Cleveland Dataset
The UCI Heart Disease Cleveland database ($N=303$, collected between 1981 and 1984 under Dr. Robert Detrano at the Cleveland Clinic Foundation) consists exclusively of patients referred for diagnostic coronary angiography due to clinical symptoms (e.g., angina) or abnormal non-invasive findings.

**Key Dataset Facts:**
- **Outcome Variable (`num`):** Angiographically determined diameter narrowing of major coronary vessels:
  - `0`: $<50\%$ narrowing (angiographically normal or non-obstructive CAD).
  - `1`, `2`, `3`, `4`: $\ge 50\%$ narrowing in 1, 2, 3, or 4 major coronary arteries.
- **Absence of Longitudinal Endpoints:** The dataset contains **zero follow-up data** on subsequent myocardial infarctions, revascularizations, or cardiovascular death.
- **Selection Bias:** The cohort is heavily enriched for symptomatic individuals referred to a tertiary catheterization laboratory, resulting in a CAD prevalence of approximately $46\%$ (139 positive / 164 negative).
- **Prohibited Inference:** **It is mathematically and clinically impossible to predict prospective 10-year cardiovascular risk from the UCI Cleveland dataset.** Any software making such a claim violates foundational principles of epidemiology and evidence-based medicine.

---

## 3. Mathematical Formulation of Task A

HeartXAI 2.0’s primary machine learning subsystem is formulated strictly as a binary classification problem:

$$\hat{y} = f(\mathbf{x}) \in [0, 1]$$

where $\mathbf{x} \in \mathbb{R}^{13}$ represents the 13 clinical biomarkers (standardized to SI/US units), and the target is defined as:

$$y = \begin{cases} 0 & \text{if } num = 0 \text{ (no significant stenosis)} \\ 1 & \text{if } num \ge 1 \text{ (significant coronary stenosis } \ge 50\%) \end{cases}$$

### 3.1 Probability Calibration Justification
Raw gradient boosted decision trees (XGBoost) output margin scores (log-odds) that do not represent true empirical probabilities. In clinical medicine, uncalibrated risk probabilities lead to dangerous over- or under-treatment.

HeartXAI mandates post-hoc calibration via **Platt Scaling (Sigmoid)** or **Isotonic Regression** evaluated via out-of-fold cross-validation:
- **Evaluation Metric 1 (Brier Score):** Target $\le 0.12$.
- **Evaluation Metric 2 (Expected Calibration Error - ECE):** Target $\le 0.05$ across 10 reliability bins.
- **Reliability Diagram:** Must accompany model certification documentation in the model registry.

### 3.2 Clinical Risk Categorization
Calibrated posterior probabilities $P(y=1 \mid \mathbf{x})$ are mapped to three clinically grounded tiers:

| Calibrated Probability | Risk Category | Clinical Interpretation | Recommended Action |
| :---: | :---: | :--- | :--- |
| **$P < 0.20$** | **Low Statistical Likelihood** | Biomarker profile aligns predominantly with non-obstructive angiography. | Maintain routine wellness checks; review lifestyle factors. |
| **$0.20 \le P < 0.60$** | **Moderate Statistical Likelihood** | Mixed biomarker indicators; presence of intermediate risk factors. | Schedule non-urgent consultation with primary care physician. |
| **$P \ge 0.60$** | **Elevated Statistical Likelihood** | Biomarker constellation strongly correlates with $\ge 50\%$ stenosis in clinical cohorts. | Recommend comprehensive clinical evaluation by a licensed cardiologist. |

---

## 4. Explainability & Counterfactual Rigor

### 4.1 TreeSHAP Local Feature Attribution
HeartXAI 2.0 employs TreeSHAP (Lundberg et al., 2020) to compute exact local feature attributions:

$$f(\mathbf{x}) = \phi_0 + \sum_{i=1}^{M} \phi_i(\mathbf{x})$$

Where $\phi_0$ is the base expected value across the training population, and $\phi_i$ is the Shapley attribution value for feature $i$.
- **Clinical Integrity Requirement:** The UI must explicitly inform users that SHAP values reflect **statistical model associations**, not direct causal biological mechanisms (e.g., "A positive SHAP value for cholesterol indicates that the model used your cholesterol level to raise your statistical score; it does not constitute clinical proof that cholesterol is the sole cause of disease").

### 4.2 Biologically Constrained Counterfactual Engine
Counterfactual explanations must never propose clinically absurd or physically impossible recommendations. HeartXAI enforces strict mathematical constraints:

```
+---------------------------------------------------------------------------------------------------------+
|                                    COUNTERFACTUAL CONSTRAINT MATRIX                                     |
+---------------------------------------------------------------------------------------------------------+
| Feature                     | Constraint Type | Permissible Perturbation Bounds                         |
+-----------------------------+-----------------+---------------------------------------------------------+
| Age (`age`)                 | FROZEN / LOCKED | Immutable: $\Delta = 0$.                                |
| Sex (`sex`)                 | FROZEN / LOCKED | Immutable: $\Delta = 0$.                                |
| Chest Pain Type (`cp`)      | FROZEN / LOCKED | Historical presentation: cannot retroactively alter.    |
| Major Vessels (`ca`)        | FROZEN / LOCKED | Anatomical fluoroscopy finding: immutable by patient.   |
| Thalassemia Status (`thal`) | FROZEN / LOCKED | Hematologic / scintigraphic status: immutable.          |
| Exercise Angina (`exang`)   | FROZEN / LOCKED | Historical clinical response: immutable.                |
| Resting BP (`trestbps`)     | ACTIONABLE      | Direction: Non-increasing ($\le x_i$). Floor: 90 mmHg.  |
| Serum Chol (`chol`)         | ACTIONABLE      | Direction: Non-increasing ($\le x_i$). Floor: 120 mg/dL.|
| Fasting Glucose (`fbs`)     | ACTIONABLE      | Direction: Non-increasing. Discrete: $\{0, 1\}$.        |
| Resting ECG (`restecg`)     | CONDITIONALLY   | Restricted to discrete valid transitions.               |
| Max Heart Rate (`thalach`)  | CONDITIONALLY   | Bounded by physiologic formula ($220 - \text{age}$).    |
+-----------------------------+-----------------+---------------------------------------------------------+
```

---

## 5. Ledger of Prohibited & Unsupported Product Claims

To prevent regulatory non-compliance (FDA SaMD enforcement, FTC health claims scrutiny, EU MDR Rule 11 violations), the following claims are strictly **PROHIBITED** across all user interfaces, marketing copy, and documentation:

1. ❌ *"HeartXAI diagnoses coronary artery disease or heart attacks."*
2. ❌ *"Our AI predicts your exact 10-year risk of having a heart attack with 99% accuracy."*
3. ❌ *"HeartXAI replaces the need for a cardiologist or an electrocardiogram."*
4. ❌ *"The system can detect if you are currently experiencing a heart attack."*
5. ❌ *"You can stop taking your prescribed heart medication based on this risk assessment."*
6. ❌ *"HeartXAI has been clinically certified as a diagnostic medical device by the FDA/EMA."*
7. ❌ *"Lowering your cholesterol to our counterfactual level guarantees you will never suffer heart disease."*
8. ❌ *"Our ML model is 100% unbiased across all ethnic and geographic populations."*

---

## 6. Statutory Medical Disclaimers

### 6.1 Patient Intake & Results Screen Disclaimer (Mandatory Display)
> **IMPORTANT CLINICAL NOTICE:** HeartXAI 2.0 is an educational clinical decision support tool designed to assist patients and healthcare providers in understanding statistical cardiovascular risk factors. It **DOES NOT** provide medical diagnoses, clinical prognoses, or treatment plans. Machine learning predictions are based on statistical correlations observed in retrospective clinical cohorts and do not replace professional medical advice, clinical evaluations, or diagnostic imaging (such as coronary angiography or echocardiography). If you are experiencing chest pain, shortness of breath, radiating arm/jaw pain, or sudden dizziness, **IMMEDIATELY CALL EMERGENCY SERVICES (911 in US, 999 in UK, 112 in India)** or go to the nearest emergency department.
