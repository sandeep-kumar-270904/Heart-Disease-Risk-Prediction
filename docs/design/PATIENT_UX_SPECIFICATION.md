# HeartXAI 2.0 — Patient UX Specification

**Document ID:** `HX2-DES-008`  
**Version:** `2.0.0`  
**Status:** `Approved Specification`  
**Author:** Senior UX Researcher & Frontend Experience Architect  
**Traceability:** FR-001–FR-040, NFR-001–NFR-028, ADR-001, ADR-011  

---

## 1. Overview & Patient Experience Principles

The Patient Experience in HeartXAI 2.0 is designed for **calm clarity, agency, and epistemological transparency**. 

Patients interacting with cardiovascular risk assessments often experience anxiety, health uncertainty, and cognitive overload. The UX must de-escalate anxiety while presenting honest mathematical model outputs without clinical diagnostic overstatement.

```
┌────────────────────────────────────────────────────────────────────────┐
│                      PATIENT WORKFLOW JOURNEY                          │
├────────────────────────────────────────────────────────────────────────┤
│ [1. Dashboard] ──► [2. Assessment Wizard] ──► [3. Dual Risk Results]   │
│                          (6 Steps)                     │               │
│                                                        ├──► [SHAP]     │
│                                                        └──► [Scenarios]│
│ [4. Trends] ◄────── [5. Doctor Directory] ◄──── [6. Clinical Export]   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Screen Specifications

---

### Screen 01: Patient Dashboard (`/patient/dashboard`)

#### 1. Screen Purpose
Provides a consolidated, calm executive overview of the patient's cardiovascular status, highlighting their most recent assessment outcome, upcoming health milestones, recent biomarker readings, and primary action triggers.

#### 2. User Story
> *"As a registered patient, I want to see a clear summary of my latest cardiovascular assessment and trends without alarming language, so that I understand where I stand and know what action to take next."*

#### 3. Key UI Elements & Layout
- **Header Greeting Banner:** Personalized greeting (*"Good morning, Rajesh"*), last assessment date badge (*"Last evaluated: 14 Nov 2026"*), and country context indicator (*"🇮🇳 India · Metric Units"*).
- **Primary Hero Card: Latest Assessment Summary:**
  - Categorical Likelihood Badge: `Moderate CAD Likelihood (42%)`.
  - Educational Model Notice: *"Based on historical study cohort comparison. Informational, not a medical diagnosis."*
  - Action Button: `[View Full Breakdown & Explainability]`.
- **Quick Action Bar:**
  - `[Run New Assessment]` (Primary CTA button).
  - `[Find Nearby Cardiologists]` (Secondary button).
  - `[Export Doctor Report]` (Ghost button).
- **Recent Biomarker Snapshot Grid (4 KPI Cards):**
  1. *Resting Blood Pressure:* `134/86 mmHg` (Target: `<120/80`).
  2. *Serum Cholesterol:* `215 mg/dL` (Target: `<200`).
  3. *Fasting Blood Sugar:* `104 mg/dL` (Target: `<100`).
  4. *Resting Heart Rate:* `72 bpm` (Normal: `60–100`).
- **Longitudinal Mini-Chart Widget:** 6-month historical sparkline of risk probability trend.
- **Educational Tip of the Day:** Evidence-based article card: *"Understanding HDL vs LDL Cholesterol"*.

#### 4. Interaction & Navigation Behavior
- Clicking `[Run New Assessment]` opens `/patient/assessments/new`.
- Clicking any biomarker KPI card navigates directly to `/patient/trends` pre-filtered for that metric.
- Clicking the hero card navigates to `/patient/assessments/:id`.

#### 5. States
- **Empty State (New User, No Prior Assessments):** Hero card displays a friendly onboarding prompt: *"You haven't completed a cardiovascular health assessment yet. Take 4 minutes to enter your health vitals and view explainable model insights."* Large CTA: `[Start Your First Assessment]`.
- **Loading State:** Skeleton cards matching the KPI grid and hero card pulse with subtle `#F1F5F9` background; `aria-busy="true"`.
- **Error State (API Unreachable):** In-page alert banner: *"Unable to load recent telemetry. Check your connection or try again."* `[Retry Button]`.

#### 6. Responsive Behavior
- **Desktop (1280px+):** 3-column layout (Hero + KPI grid left 2 cols; Quick actions + Educational cards right 1 col).
- **Tablet (768px):** 2-column layout.
- **Mobile (<640px):** Single vertical column; KPI grid switches to 2×2 grid; sticky bottom CTA for `[New Assessment]`.

#### 7. Accessibility
- Headings structured: `H1` (Dashboard), `H2` (Latest Assessment, Recent Vitals, Quick Actions).
- KPI cards wrapped in semantic `<article>` tags with explicit `aria-label` describing current reading vs target.

---

### Screen 02: New Assessment Intake Wizard (`/patient/assessments/new`)

#### 1. Screen Purpose
Guides the patient through structured, validation-controlled clinical data intake across 6 progressive steps, reducing cognitive fatigue through chunked form sections.

#### 2. User Story
> *"As a patient, I want to enter my clinical lab results and vitals step-by-step with clear unit helpers and input validation, so that I can generate an explainable assessment without making calculation errors."*

#### 3. The 6-Step Workflow Structure

```
[ Step 1: Demographics ] ──► [ Step 2: Vitals ] ──► [ Step 3: Labs ]
                                                            │
[ Step 6: Review & Run ] ◄── [ Step 5: Imaging ] ◄── [ Step 4: ECG ]
```

##### Step 1: Demographics & Symptoms
- `Age` (Number input: `18`–`100` years).
- `Sex` (Segmented control: `Female`, `Male`, `Other`).
- `Chest Pain Type` (Select with plain-language definitions):
  - *Typical Angina:* Chest pressure or pain provoked by physical exertion and relieved by rest.
  - *Atypical Angina:* Chest discomfort with atypical symptoms (shortness of breath, fatigue).
  - *Non-Anginal Pain:* Sharp pain unrelated to physical exertion.
  - *Asymptomatic:* No chest discomfort experienced.
- **Acute Symptom Check:** If user selects severe resting chest pain, an immediate informational callout appears: *"If you are currently experiencing acute, crushing chest pain or shortness of breath, please seek emergency medical care immediately."*

##### Step 2: Cardiovascular Vitals
- `Resting Blood Pressure` (Systolic: `70`–`240` mmHg; Diastolic: `40`–`140` mmHg).
- `Maximum Heart Rate Achieved` (Input: `60`–`220` bpm).
- `Exercise-Induced Angina` (Radio card: `Yes` / `No`).

##### Step 3: Laboratory Blood Markers
- `Serum Cholesterol` (Input with unit toggle: `mg/dL` $\leftrightarrow$ `mmol/L`).
  - Conversion: $1\text{ mmol/L} = 38.67\text{ mg/dL}$.
  - Range: `100`–`600` mg/dL (`2.59`–`15.52` mmol/L).
- `Fasting Blood Sugar` (Input with unit toggle: `mg/dL` $\leftrightarrow$ `mmol/L` or categorized: `> 120 mg/dL` / `≤ 120 mg/dL`).

##### Step 4: Electrocardiogram (ECG) Markers
- `Resting ECG Results` (Select: `Normal`, `ST-T Wave Abnormality`, `Left Ventricular Hypertrophy`). Helper tooltip explains each clinical term.
- `ST Depression Induced by Exercise (oldpeak)` (Number input: `0.0`–`6.2` mm, step `0.1`).
- `Slope of the Peak Exercise ST Segment` (Select: `Upsloping`, `Flat`, `Downsloping`).

##### Step 5: Advanced Imaging & Stress Tests (Optional / Advanced)
- `Major Vessels Colored by Fluoroscopy (ca)` (Select: `0`, `1`, `2`, `3`, or `Unknown / Not Performed`).
- `Thallium Stress Scintigraphy (thal)` (Select: `Normal`, `Fixed Defect`, `Reversible Defect`, or `Unknown / Not Performed`).
- *Note:* If patient does not have specialized imaging results, cohort-calibrated median imputation is utilized and explicitly flagged in the review step.

##### Step 6: Review, Unit Verification & Confirmation
- Consolidated summary card displaying all entered values with explicit units.
- Missing values clearly highlighted with imputation notices.
- Mandatory Patient Acknowledgment Checkbox:
  - *"I understand that this assessment uses machine learning to estimate observational likelihood of CAD patterns and does not constitute a certified medical diagnosis."*
- Primary CTA Button: `[Calculate Risk & Explainability]`.

#### 4. Interaction & Navigation Behavior
- Progress indicator at top: Step dots with labels (`Demographics`, `Vitals`, `Labs`, `ECG`, `Imaging`, `Review`).
- `[Back]` button returns to previous step preserving all inputs.
- `[Save as Draft]` stores partial form in local encrypted browser state and backend draft record.
- Step transition animation: `200ms ease-out` horizontal slide.

#### 5. States & Validation
- **Field Validation:** Triggers on `onBlur` and form submission. If an invalid number is entered (e.g., Cholesterol `850 mg/dL`), the field border turns crimson, and helper text explains: *"Value exceeds physiological bounds (100–600 mg/dL). Please verify with your lab report."*
- **Submitting State:** Button shows spinner and text changes to *"Analyzing cardiovascular telemetry..."*.
- **Error State:** Server validation failure surfaces an alert at the top of the step: *"Unable to process assessment: Resting BP systolic must be greater than diastolic."*

#### 6. Accessibility
- Form steps announce dynamically via `aria-live="polite"`: *"Step 3 of 6: Laboratory Blood Markers"*.
- All inputs have `<label for="...">` explicitly matching the input `id`.
- Focus shifts automatically to the first invalid input upon validation failure.

---

### Screen 03: Assessment Results & Overview (`/patient/assessments/:id`)

#### 1. Screen Purpose
Presents the primary output of the ML model, contextualizing the numerical likelihood with calibrated population benchmarks, plain-language clinical interpretation, and emergency safety guardrails.

#### 2. Key UI Elements & Layout
- **Assessment Metadata Bar:** Date/time executed, Model Version (`XGBoost-Cleveland v2.4.1`), Country Context (`India`), and `[Export PDF]` button.
- **Educational Disclaimer Callout (Top Permanent):**
  > *"Educational Platform: The results below represent an algorithmic estimation of coronary artery disease association derived from observational clinical datasets. This report is intended to facilitate informed conversations with your healthcare provider and does not constitute a medical diagnosis."*
- **Dual Risk Evaluation Display:**
  1. *Angiographic CAD Association Likelihood:*
     - Value: `42%` (Categorical Strata: `Moderate Likelihood`).
     - Visual: Calibrated segmented horizontal bar with emerald, amber, and crimson strata.
  2. *10-Year Cardiovascular Event Population Risk:*
     - Value: `11.8%` (Population comparison benchmark).
- **Executive Summary Narrative:**
  - *"Your submitted biomarker profile indicates a moderate statistical association with angiographic coronary artery disease patterns. The primary factors elevating the score are your resting blood pressure (154 mmHg) and serum cholesterol (245 mg/dL). Conversely, your normal resting ECG and high exercise tolerance contributed favorably."*
- **Tab Navigation Bar:**
  - `[Overview (Active)]` | `[Feature Explainability (SHAP)]` | `[What-If Scenarios]` | `[Input Data]`
- **Next Steps & Recommended Actions:**
  - `[Schedule a Consultation with a Cardiologist]`
  - `[Explore What-If Scenarios]`
  - `[Download Clinician Discussion Sheet]`

#### 3. Emergency Safety Intercept
If the patient's inputs triggered acute warning thresholds (e.g., Resting Chest Pain + ST Depression $> 2.5\text{ mm}$ + Systolic BP $> 180\text{ mmHg}$):
- A prominent Crimson Alert Banner appears at the very top:
  - *"🚨 Medical Alert: Your reported measurements indicate significant acute cardiovascular strain. Do not wait for an outpatient appointment. If you are experiencing chest pain or discomfort, contact emergency medical services immediately."*
  - Includes a direct one-click `[Call Emergency: 112 / 102]` button.

---

### Screen 04: Explainability & SHAP Waterfall (`/patient/assessments/:id/explainability`)

#### 1. Screen Purpose
Demystifies the algorithmic prediction by visualizing exactly which physiological variables pushed the likelihood higher or lower, providing mathematical transparency without black-box opacity.

#### 2. Key UI Elements
- **Explainability Header:**
  - Title: *"Feature Contribution Breakdown (SHAP Analysis)"*
  - Subtitle: *"SHAP (SHapley Additive exPlanations) measures how much each of your measurements shifted the model's prediction away from the baseline average (38%)."*
- **View Toggle Control:** `[Visual Waterfall Chart]` | `[Accessible Tabular Grid]`.
- **Interactive SHAP Waterfall Display:**
  - Vertical layout with a zero-contribution center line.
  - Right-extending Crimson bars (`▲`): Features that **increased** estimated likelihood (e.g., `Resting BP +14%`, `Cholesterol +8%`).
  - Left-extending Blue bars (`▼`): Features that **decreased** estimated likelihood (e.g., `Max Heart Rate -9%`, `Normal Thallium -6%`).
  - Hovering over any bar reveals a detailed popover:
    - *Your Value:* `154 mmHg`
    - *Cohort Average:* `131 mmHg`
    - *SHAP Impact:* `+0.1412` (Pushes risk higher)
    - *Plain Language Meaning:* *"Elevated resting blood pressure places chronic shear stress on arterial walls, increasing the likelihood of CAD patterns in historical datasets."*
- **Accessible Data Table Alternative (Accessible Fallback):**
  - Sortable columns: *Biomarker*, *Your Value*, *Reference Baseline*, *Impact Direction*, *SHAP Value*.

---

### Screen 05: Counterfactual "What-If" Scenario Explorer (`/patient/assessments/:id/scenarios`)

#### 1. Screen Purpose
Empowers patients to explore hypothetical scenarios by simulating how modifications in modifiable risk factors (blood pressure, cholesterol, blood sugar) would impact model predictions.

#### 2. Clinical & Pedagogical Guardrails
- **Permanent Framing Notice:**
  > *"Hypothetical Exploration Only: This simulator demonstrates how the mathematical model responds to changed inputs. It does not guarantee clinical outcomes or serve as a personalized medical treatment plan. Never alter prescribed medications or medical routines without consulting your doctor."*

#### 3. Key UI Elements
- **Interactive Modifiable Sliders (Left Panel):**
  1. *Systolic Blood Pressure:* Range `90`–`180` mmHg; Baseline: `154 mmHg`.
  2. *Serum Cholesterol:* Range `120`–`350` mg/dL; Baseline: `245 mg/dL`.
  3. *Fasting Blood Sugar:* Range `70`–`200` mg/dL; Baseline: `128 mg/dL`.
  4. *Exercise Tolerance (Max Heart Rate):* Range `90`–`200` bpm; Baseline: `142 bpm`.
  - Non-modifiable factors (Age, Sex, Major Vessels Fluoroscopy) are locked with an informational lock icon: *"Biological non-modifiable baseline"*.
- **Live Simulated Prediction Card (Right Panel):**
  - Baseline Likelihood: `42% (Moderate)`
  - Simulated Likelihood: `28% (Low)`
  - Simulated Net Delta: `▼ -14%`
  - Action Button: `[Reset All Sliders to My Baseline]`
  - Action Button: `[Save Scenario as Doctor Discussion Note]`

---

### Screen 06: Assessment History & Trends (`/patient/assessments` & `/patient/trends`)

#### 1. Screen Purpose
Provides a comprehensive historical archive and longitudinal visual analytics tracking changes in risk scores and individual biomarkers over time.

#### 2. Key UI Elements
- **Filter Toolbar:** Date range picker (`Last 3 Months`, `6 Months`, `1 Year`, `All`), Risk Strata filter (`All`, `Low`, `Moderate`, `Elevated`), and Search bar.
- **Assessment Table:**
  - Columns: *Date*, *Risk Likelihood*, *Risk Strata Badge*, *Blood Pressure*, *Cholesterol*, *Actions (`[View]`, `[PDF]`)*.
- **Trends Visualization Tab:**
  - Multi-line interactive trend chart with customizable Y-axis metric (Switch between *CAD Likelihood %*, *Systolic BP*, *Cholesterol*, *Blood Sugar*).
  - Normal physiological range shaded in soft emerald (`#ECFDF5`) background band.
  - Hover tooltips detailing exact date and values.

---

### Screen 07: Country-Configurable Healthcare Provider Directory (`/patient/directory/doctors`)

#### 1. Screen Purpose
Connects patients with verified cardiologists and cardiac specialists within their configured country and locality.

#### 2. Key UI Elements
- **Country Header:** Displays active jurisdiction (e.g., `🇮🇳 India — National Medical Commission Verified Registry` or `🇺🇸 USA — State Medical Board Verified`).
- **Search & Filter Bar:**
  - City / Region input (e.g., *"Mumbai"*, *"Bengaluru"*).
  - Sub-Specialty dropdown (*"Interventional Cardiology"*, *"Preventive Cardiology"*, *"Electrophysiology"*).
  - Toggle: `[✓ Verified Clinicians Only]`.
- **Cardiologist Listing Cards:**
  - Doctor Name & Professional Title (e.g., *"Dr. Ananya Rao, MD, DM (Cardiology)"*).
  - Verification Pill: `[✓ NMC License Verified]`.
  - Affiliated Hospital / Clinic: *"Apollo Speciality Hospital, Bannerghatta Road"*.
  - Experience & Consultation Type: *"14 Years Exp · In-Person & Teleconsultation"*.
  - Contact Actions: `[View Full Profile]`, `[Call Clinic]`, `[Get Directions]`.

---

### Screen 08: Country-Configurable Hospital & Facility Directory (`/patient/directory/hospitals`)

#### 1. Screen Purpose
Enables patients to locate accredited cardiac facilities, catheterization labs, and 24/7 cardiac emergency centers in their area.

#### 2. Key UI Elements
- **Emergency Filter Highlight:** `[🚨 24/7 Cardiac Emergency Only]`.
- **Facility Cards:**
  - Hospital Name, Accreditation Badge (e.g., `NABH Accredited` / `JCI Accredited`).
  - Emergency Hotline: Click-to-call link with prominent red badge.
  - Key Services: *Cardiac ICU*, *Cath Lab (Coronary Angiography)*, *Echocardiography*.
  - Distance & Map Link: *"4.2 km away · Open in Maps"*.

---

### Screen 09: Health Insurance Guidance (`/patient/insurance`)

#### 1. Screen Purpose
Provides educational, country-specific guidance on health insurance coverage for cardiovascular diagnostics, preventive evaluations, and hospitalization.

#### 2. Key UI Elements
- **Country Context Banner:** *"Insurance Guidance for: India (IRDAI Regulated Plans & Ayushman Bharat PM-JAY)"*.
- **Diagnostic Coverage Checklist:**
  - Overview of whether stress tests, echocardiograms, and lipid panels are covered under outpatient vs inpatient benefits.
- **Pre-Authorization & Claims Guidance:**
  - Step-by-step checklist for cardiac admission pre-authorization.
  - Document checklist: Doctor's prescription, lab test reports, insurance policy card.
- **Approved TPA & Insurer Directory:**
  - List of major health insurance providers with official customer care and cashless hospitalization helpline numbers.

---

### Screen 10: Clinical Summary PDF Export (`/patient/reports/export`)

#### 1. Screen Purpose
Generates a structured, concise, one-page printable PDF report designed specifically for the patient to bring to their doctor's appointment.

#### 2. Layout Structure of Exported Document
- Header: HeartXAI Clinical Overview, Patient ID (anonymized hash option), Date of Generation.
- Section 1: Executive Summary & Angiographic CAD Association Likelihood.
- Section 2: Patient Reported Clinical Vitals & Lab Measurements.
- Section 3: Top Contributing Features (SHAP attribution table).
- Section 4: Longitudinal 6-Month Biomarker Trajectory Table.
- Section 5: Standard Legal & Clinical Disclaimer: *"This document is an AI-generated educational summary provided at the patient's request. It is not an official medical record or certified laboratory diagnostic."*
