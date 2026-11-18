# HeartXAI 2.0 — Fairness, Demographic Disparity & Generalizability Report

**Document ID:** `HX2-ML-012`  
**Version:** `1.0.0`  
**Phase:** Phase 8 — Machine Learning Research, Dataset Verification & Model Development Plan  
**Status:** Approved Research Specification  
**Author:** Principal ML Research Scientist & Healthcare Algorithmic Fairness Specialist  
**Traceability:** FR-020–FR-029, NFR-001–NFR-028, ADR-001, ADR-003, ADR-011  

---

## 1. Algorithmic Fairness Philosophy in Clinical Machine Learning

In healthcare AI, claims of "fairness" must be empirically audited, mathematically defined, and clinically grounded. Merely importing a fairness library (such as Fairlearn or AIF360) does not make a model fair.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   DEMOGRAPHIC AUDIT BOUNDARIES                         │
├────────────────────────────────────────────────────────────────────────┤
│ • Documented Protected Attributes: sex (Male/Female), age (Continuous) │
│ • UNDOCUMENTED Protected Attributes: Race, Ethnicity, Income, Postcode │
│ • Strict Rule: We NEVER infer or impute race, ethnicity, or religion   │
│   when those variables were not collected by the original researchers. │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Demographic Subgroup Distribution in the Training Cohort

### 2.1 Sex Representation Disparity
- **Male Subgroup:** $n = 206$ ($67.99\%$).
  - Target CAD Positive ($\ge 50\%$ stenosis): $n = 114$ ($55.34\%$).
  - Target CAD Negative ($< 50\%$ stenosis): $n = 92$ ($44.66\%$).
- **Female Subgroup:** $n = 97$ ($32.01\%$).
  - Target CAD Positive ($\ge 50\%$ stenosis): $n = 25$ ($25.77\%$).
  - Target CAD Negative ($< 50\%$ stenosis): $n = 72$ ($74.23\%$).
- **Epidemiological Analysis:** In the Cleveland cohort, males had a significantly higher baseline rate of angiographic CAD ($55.3\%$ vs $25.8\%$, $p < 0.001$). An unregularized model risks learning that being male is inherently predictive of disease, leading to under-diagnosis (elevated false negatives) in female patients.

### 2.2 Age Stratum Representation Disparity
- **Younger Subgroup ($< 55$ years):** $n = 144$ ($47.52\%$). Mean age: $46.8$ years.
- **Older Subgroup ($\ge 55$ years):** $n = 159$ ($52.48\%$). Mean age: $61.3$ years.
- **Sparse Boundaries:** Only 3 patients younger than 35 and 1 patient older than 75.

---

## 3. Subgroup Fairness Evaluation Protocol

During model validation, performance metrics must be reported disaggregated by demographic subgroups:

### 3.1 Equalized Odds & Disparity Metrics
1. **True Positive Rate Parity (Equal Opportunity / Sensitivity Balance):**
   $$\Delta \text{TPR} = |\text{Sensitivity}_{\text{Male}} - \text{Sensitivity}_{\text{Female}}| \le 0.10$$
   We require that the model identifies at least $80\%$ of female CAD cases, preventing clinical under-triage in women.
2. **False Positive Rate Parity (Specificity Balance):**
   $$\Delta \text{FPR} = |\text{FPR}_{\text{Male}} - \text{FPR}_{\text{Female}}| \le 0.10$$
   Ensures female patients without CAD are not subjected to unnecessary anxiety or referrals at a higher rate than males.
3. **Brier Score Parity:** Measures whether probability calibration holds equally across sexes:
   $$|\text{BS}_{\text{Male}} - \text{BS}_{\text{Female}}| \le 0.03$$

---

## 4. Generalizability Boundaries & Global Context (ADR-011)

### 4.1 Geographic & Ethnic Limitations
The Cleveland Clinic cohort was gathered in Cleveland, Ohio between 1981 and 1984.
- **Lack of Ethnic Representation:** The population reflected standard referral patterns to a private tertiary center in the American Midwest in the early 1980s (predominantly Caucasian).
- **South Asian Cardiovascular Paradox:** Individuals of South Asian origin (India, Pakistan, Bangladesh) frequently exhibit premature coronary artery disease occurring a decade earlier, characterized by smaller caliber epicardial vessels, high visceral adiposity, and elevated Lipoprotein(a), often in the absence of severe hypercholesterolemia.
- **Clinical Conclusion:** A model trained on 1984 Cleveland patients **cannot claim validated accuracy for the Indian or global population**.

### 4.2 Decoupled UI Presentation Architecture
In accordance with **ADR-011**:
1. The model's training cohort provenance is explicitly displayed on every results card: *"Trained on historical Cleveland Clinic Foundation referral cohort (1981–1984)."*
2. Educational disclaimers emphasize that regional ethnic variations are not accounted for by this historical model.
3. Country-specific directories, emergency numbers, and unit formatters are managed outside the ML model.
