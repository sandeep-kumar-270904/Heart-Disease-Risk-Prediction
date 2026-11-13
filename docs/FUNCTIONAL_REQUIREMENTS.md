# HeartXAI 2.0 — Functional Requirements Specification

**Document ID:** HXAI-REQ-002  
**Version:** 2.0.0  
**Phase:** Phase 2 — Product Requirements & System Scope  
**Status:** Complete / Ready for Review  
**Author:** Principal Product Manager & Senior Systems Analyst  

---

## 1. Specification Framework & Requirement Taxonomy

This document establishes the comprehensive functional requirements for all twenty (20) core modules of **HeartXAI 2.0**. Every feature is specified using a 15-attribute engineering contract, ensuring unambiguous traceability from business intent to automated test assertion.

### Priority Legend (MoSCoW Method):
- **MUST:** Mandatory for minimum viable clinical operation and safety.
- **SHOULD:** Highly critical supporting feature; required for production release.
- **COULD:** Valuable enhancement to user experience; implemented if time permits.
- **WON'T:** Explicitly excluded from the current release scope.

---

## 2. Detailed Functional Requirements by Module

### Module 1: Public Website & Product Information

#### REQ-PUB-01: Public Educational Landing & Clinical Methodology Portal
- **Feature Name:** Public Educational Portal & Methodology Presentation
- **Purpose:** Educate public visitors regarding cardiovascular health factors, explainable AI principles, and platform capabilities without forcing account creation.
- **User Role:** Guest, Patient, Doctor, Administrator
- **Preconditions:** System web server is running and accessible via HTTP/HTTPS.
- **Input:** User navigates to root URL (`/`).
- **Processing / Business Rules:**
  1. Render hero section detailing HeartXAI 2.0 value proposition.
  2. Display prominent, non-dismissible statutory non-diagnostic disclaimer banner.
  3. Render educational cards summarizing the 13 clinical biomarkers with traceable AHA/ACC citations.
  4. Provide accessible navigation links to `/about`, `/sandbox`, `/login`, and `/register`.
- **Expected Output:** Responsive, fully styled landing view adhering to "Aethelgard Clinical" tokens.
- **Success Conditions:** Page loads in $< 1.5\text{s}$; zero layout shifts ($\text{CLS} < 0.05$); all internal links functional.
- **Failure Conditions:** CDN asset loading failure triggers fallback system font stack and local styles.
- **Validation Rules:** N/A (Read-only view).
- **Security & Privacy:** Zero cookies set before consent; no third-party tracking scripts or telemetry pixels.
- **Dependencies:** None.
- **Priority:** **MUST**
- **Acceptance Criteria:** Verified via Playwright automated test: page renders disclaimer, passes axe-core accessibility check with 0 violations, and navigates cleanly to `/register`.

#### REQ-PUB-02: Interactive Anonymous Sandbox Simulator
- **Feature Name:** Anonymous Explainability Demonstration Sandbox
- **Purpose:** Allow visitors to explore model predictions, SHAP waterfalls, and counterfactuals using standardized synthetic benchmark profiles without disclosing personal data.
- **User Role:** Guest
- **Preconditions:** Model inference pipeline is loaded in memory.
- **Input:** User selects a pre-configured synthetic profile (e.g. "Profile A: 55yo Male Borderline", "Profile B: 62yo Female Elevated") or adjusts sample sliders.
- **Processing / Business Rules:**
  1. Process input vector through stateless ML inference engine without persisting records to database.
  2. Compute exact TreeSHAP attributions and constrained counterfactual projection.
  3. Display clear banner: *"Demonstration Mode: Using synthetic benchmark data. No personal data is stored."*
- **Expected Output:** Interactive dual-risk gauge, SHAP waterfall plot, and counterfactual slider simulator.
- **Success Conditions:** Complete inference and explanation rendered in $< 350\text{ms}$.
- **Failure Conditions:** If inference fails, display friendly inline error: *"Demonstration service temporarily unavailable."*
- **Validation Rules:** Inputs clamped to physiological benchmark bounds.
- **Security & Privacy:** Server processes vector in memory; zero database write operations; rate limited to 30 requests/minute per IP.
- **Dependencies:** ML Inference Engine (Module 5), SHAP Engine (Module 7).
- **Priority:** **SHOULD**
- **Acceptance Criteria:** Playwright test verifies selecting a synthetic profile updates the SHAP waterfall without initiating any database mutations.

---

### Module 2: Registration, Login & Authentication

#### REQ-AUTH-01: Secure User Registration
- **Feature Name:** Role-Based Account Registration
- **Purpose:** Allow new users to create accounts with verified email addresses, secure passwords, and designated roles (`PATIENT`, `CLINICIAN`).
- **User Role:** Guest
- **Preconditions:** Guest is on `/register`.
- **Input:** `email` (string), `password` (string), `full_name` (string), `role` (`"PATIENT"` or `"CLINICIAN"`), optional `license_number` (string, required if clinician), `consent_agreed` (boolean).
- **Processing / Business Rules:**
  1. Normalize email to lowercase and trim whitespace.
  2. Verify email uniqueness in `users` table.
  3. Validate password complexity (minimum 8 chars, at least 1 digit, 1 uppercase, 1 special char).
  4. Verify `consent_agreed == true`.
  5. Hash password using bcrypt (work factor $\ge 12$).
  6. If `role == "CLINICIAN"`, set `clinician_status = "PENDING_VERIFICATION"`; if `role == "PATIENT"`, set `status = "ACTIVE"`.
  7. Insert user record into `users` table and log registration event.
- **Expected Output:** HTTP 201 Created with user summary payload (excluding password hash) and prompt to log in or automated session creation.
- **Success Conditions:** User record safely persisted; password securely hashed; audit log entry recorded.
- **Failure Conditions:** Duplicate email returns HTTP 409 Conflict `{"error": {"code": "email_already_registered"}}`; weak password returns HTTP 422 Unprocessable Entity with specific complexity deficiency.
- **Validation Rules:** RFC 5322 email regex; password $\ge 8$ chars; consent must be true.
- **Security & Privacy:** Zero plaintext passwords logged; timing-attack resistant password hashing.
- **Dependencies:** Database service (PostgreSQL/SQLAlchemy).
- **Priority:** **MUST**
- **Acceptance Criteria:** Unit tests assert successful registration with valid inputs and exact error codes for duplicate email, weak password, and unselected consent.

#### REQ-AUTH-02: Multi-Role Secure Authentication & Session Issuance
- **Feature Name:** Secure Login & HttpOnly JWT Session Management
- **Purpose:** Authenticate registered users and issue cryptographically signed, secure sessions.
- **User Role:** Guest, Registered User
- **Preconditions:** User exists in `users` table.
- **Input:** `email` (string), `password` (string).
- **Processing / Business Rules:**
  1. Retrieve user by email; if not found, perform dummy bcrypt hash verification to mitigate timing attacks, then return HTTP 401.
  2. Verify submitted password against stored bcrypt hash.
  3. Check account status: if `CLINICIAN` and status is `"SUSPENDED"` or `"PENDING_VERIFICATION"`, return appropriate warning.
  4. Generate signed JWT token (algorithm HS256, expiration 60 minutes) containing `sub` (user_id), `role`, and `session_id`.
  5. Set secure HTTP-only cookie `access_token` (`HttpOnly; Secure; SameSite=Strict; Path=/api`).
  6. Update `last_login_at` timestamp in database and record audit log.
- **Expected Output:** HTTP 200 OK with sanitized user profile object (`id`, `email`, `full_name`, `role`).
- **Success Conditions:** Valid JWT issued; cookie set; client routed to role dashboard.
- **Failure Conditions:** Invalid credentials return HTTP 401 Unauthorized `{"error": {"message": "Invalid email or password"}}`.
- **Validation Rules:** Email and password non-empty strings.
- **Security & Privacy:** Passwords never transmitted in URLs; brute-force protection (max 5 failed attempts per IP per minute via Redis/memory rate limiter).
- **Dependencies:** `users` table, JWT signer, Audit logging (Module 20).
- **Priority:** **MUST**
- **Acceptance Criteria:** Integration test verifies login with correct credentials sets `HttpOnly` cookie and returns 200; incorrect password returns 401; 6 consecutive failures trigger rate limit HTTP 429.

#### REQ-AUTH-03: Session Invalidation & Logout
- **Feature Name:** Secure Session Termination
- **Purpose:** Terminate user session and clear authentication cookies.
- **User Role:** Patient, Clinician, Administrator
- **Preconditions:** User is currently authenticated.
- **Input:** User clicks "Log Out" (`POST /api/v1/auth/logout`).
- **Processing / Business Rules:**
  1. Clear `access_token` cookie by setting expiration to epoch zero (`Max-Age=0`).
  2. Log session termination in `audit_logs`.
- **Expected Output:** HTTP 200 OK with `{"message": "Successfully logged out"}`; client redirects to `/login`.
- **Success Conditions:** Authentication cookie eradicated from browser; subsequent API calls return HTTP 401.
- **Failure Conditions:** If network fails, frontend client wipes local user state and forces redirect to landing.
- **Validation Rules:** Requires valid active session.
- **Security & Privacy:** Prevents session hijacking on shared or public workstations.
- **Dependencies:** Auth router.
- **Priority:** **MUST**
- **Acceptance Criteria:** Automated test verifies that after calling logout, subsequent requests to protected endpoints return HTTP 401 Unauthorized.

---

### Module 3: Patient Profile & Health Information

#### REQ-PROF-01: Patient Demographic & Baseline Profile Management
- **Feature Name:** Patient Baseline Profile Editor
- **Purpose:** Allow patients to record baseline health context (emergency contact, physician name, preferred units).
- **User Role:** Patient
- **Preconditions:** User is authenticated with `role == "PATIENT"`.
- **Input:** `date_of_birth` (date), `biological_sex` (enum: Male/Female), `primary_physician_name` (string, optional), `preferred_unit_system` (enum: US_STANDARD / METRIC).
- **Processing / Business Rules:**
  1. Validate date of birth: patient must be between 18 and 120 years of age.
  2. Persist profile record to `patient_profiles` table linked via foreign key to `users.id`.
- **Expected Output:** HTTP 200 OK with updated profile object.
- **Success Conditions:** Profile saved; used to pre-populate intake wizard defaults.
- **Failure Conditions:** Age $< 18$ returns HTTP 422: *"HeartXAI is calibrated for adult populations aged 18 and older."*
- **Validation Rules:** DOB cannot be in the future; name strings sanitized against XSS.
- **Security & Privacy:** Profile data accessible strictly by the owning patient and authorized clinicians.
- **Dependencies:** `patient_profiles` table.
- **Priority:** **SHOULD**
- **Acceptance Criteria:** Test verifies updating baseline DOB automatically pre-fills age in new assessment intake form.

---

### Module 4: Cardiovascular Assessment Form

#### REQ-ASSESS-01: Multi-Step Clinical Biomarker Intake Wizard
- **Feature Name:** Guided 3-Step Biomarker Intake Wizard
- **Purpose:** Provide a structured, error-resilient interface for entering the 13 clinical biomarkers with real-time range validation.
- **User Role:** Patient, Clinician
- **Preconditions:** User is authenticated.
- **Input:** 13 clinical biomarkers across 3 sequential steps:
  - **Step 1 (Demographics & Symptoms):** `age` (int), `sex` (enum), `cp` (chest pain type: 0=typical, 1=atypical, 2=non-anginal, 3=asymptomatic).
  - **Step 2 (Hemodynamics & Vitals):** `trestbps` (resting BP, mmHg), `thalach` (max HR, bpm), `exang` (exercise angina: 0=no, 1=yes).
  - **Step 3 (Diagnostics & Labs):** `chol` (serum cholesterol, mg/dL), `fbs` (fasting blood sugar > 120: 0=no, 1=yes), `restecg` (ECG: 0=normal, 1=ST-T abnormality, 2=LV hypertrophy), `oldpeak` (ST depression, mm), `slope` (ST slope: 0=upsloping, 1=flat, 2=downsloping), `ca` (major vessels: 0-3), `thal` (thallium: 1=normal, 2=fixed defect, 3=reversible defect).
- **Processing / Business Rules:**
  1. Client-side real-time range verification on blur with visual boundaries and normal reference helpers.
  2. Prevent navigation to Step 2 or Step 3 if current step contains invalid or empty required fields.
  3. On Step 3 submission, wrap payload in Pydantic schema `AssessmentCreateSchema` and transmit via `POST /api/v1/assessments`.
  4. Server enforces identical range bounds, writes record to `assessments` table, and triggers ML inference pipeline within an ACID transaction.
- **Expected Output:** HTTP 201 Created with assessment payload and generated UUID; client navigates to `/assessments/{id}/results`.
- **Success Conditions:** Assessment record safely persisted with status `"COMPLETED"`; inference automatically computed.
- **Failure Conditions:** Out-of-bounds input (e.g. `trestbps = 300`) returns HTTP 422 with structured field error; form remains open with error banner highlighted.
- **Validation Rules:**
  - `age`: 18 – 100
  - `trestbps`: 80 – 220 mm Hg
  - `chol`: 100 – 600 mg/dL
  - `thalach`: 60 – 220 bpm
  - `oldpeak`: 0.0 – 6.5 mm
  - `ca`: 0, 1, 2, 3
  - Strict enum validation on `sex`, `cp`, `fbs`, `restecg`, `exang`, `slope`, `thal`.
- **Security & Privacy:** Server sanitizes all inputs; verifies patient ownership or clinician authorization.
- **Dependencies:** `assessments` table, ML Inference Engine (Module 5).
- **Priority:** **MUST**
- **Acceptance Criteria:** Automated test suite submits 20 boundary cases (valid and invalid) and asserts exact rejection or success behavior.

---

### Module 5: Machine Learning Prediction

#### REQ-ML-01: Calibrated Coronary Artery Disease Binary Inference
- **Feature Name:** Calibrated CAD Probability Estimation
- **Purpose:** Compute a statistically calibrated probability indicating presence of significant coronary artery disease ($\ge 50\%$ diameter stenosis) from the 13 clinical biomarkers.
- **User Role:** System (Automated Execution)
- **Preconditions:** Complete, validated assessment biomarker vector available.
- **Input:** 13-feature numerical vector.
- **Processing / Business Rules:**
  1. Pass vector through Scikit-learn `StandardScaler` pipeline using saved training parameters.
  2. Execute inference through versioned, calibrated model pipeline (`XGBClassifier` + `CalibratedClassifierCV` Isotonic/Platt).
  3. Extract calibrated probability $P(\text{CAD} \ge 50\% \mid x)$.
  4. Compute confidence interval (Wilson score interval / bootstrap variance estimate).
  5. Assign risk tier:
     - `OPTIMAL` / `LOW`: $P < 0.20$
     - `BORDERLINE`: $0.20 \le P < 0.50$
     - `ELEVATED` / `HIGH`: $P \ge 0.50$
  6. Persist inference metrics in `inference_results` table.
- **Expected Output:** Calibrated probability float ($0.0 - 1.0$), risk tier string, confidence interval bounds, model version tag (`v2.0.0`).
- **Success Conditions:** Inference completes deterministically in $< 50\text{ms}$; Brier score verified $\le 0.15$.
- **Failure Conditions:** If model artifact fails to load, raise `MLInferenceException`, log stack trace, and return HTTP 500 with graceful user message.
- **Validation Rules:** Input vector length must equal exactly 13; zero NaN or Infinite values.
- **Security & Privacy:** Model artifact verified via SHA-256 hash at boot to prevent model tampering.
- **Dependencies:** Scikit-learn, XGBoost, Model artifact `heartxai_model_v2.0.0.joblib`.
- **Priority:** **MUST**
- **Acceptance Criteria:** Unit tests assert identical prediction output across 500 identical synthetic runs, with calibrated probability within $[0.0, 1.0]$.

#### REQ-ML-02: 10-Year Prospective ASCVD Risk Stratification
- **Feature Name:** ACC/AHA 10-Year Prospective Cardiovascular Risk Calculator
- **Purpose:** Compute validated 10-year prospective risk of hard cardiovascular events (myocardial infarction or stroke) using established epidemiological equations, distinctly segregated from CAD binary classification.
- **User Role:** System (Automated Execution)
- **Preconditions:** Patient demographic and hemodynamic metrics available (`age`, `sex`, `trestbps`, `chol`, `fbs`, smoking status proxy).
- **Input:** Age, biological sex, systolic blood pressure, total cholesterol, HDL proxy, diabetes status, treatment status.
- **Processing / Business Rules:**
  1. Apply the 2013 ACC/AHA Guideline Pooled Cohort Equations.
  2. Calculate 10-year percentage risk: $\text{Risk}_{10\text{yr}} = 1 - S_{10}^{\exp(\text{IndX} - \text{MeanX})}$.
  3. Assign ACC/AHA risk category:
     - Low Risk: $< 5\%$
     - Borderline Risk: $5\% - 7.4\%$
     - Intermediate Risk: $7.5\% - 19.9\%$
     - High Risk: $\ge 20\%$
  4. Persist result in `inference_results.ascvd_10yr_risk`.
- **Expected Output:** 10-year risk percentage float and ACC/AHA risk category.
- **Success Conditions:** Calculation matches published ACC/AHA reference tables within $\pm 0.1\%$.
- **Failure Conditions:** Age $< 20$ or $> 79$ outputs out-of-range advisory: *"ACC/AHA Pooled Cohort Equations are officially calibrated for adults aged 20 to 79."*
- **Validation Rules:** Numerical bounds checked prior to exponential calculation.
- **Security & Privacy:** Calculated statelessly alongside primary assessment.
- **Dependencies:** Assessment intake vector.
- **Priority:** **MUST**
- **Acceptance Criteria:** Automated test matches calculated output against 10 verified clinical benchmark test cases from the ACC/AHA guidelines.

---

### Module 6: Prediction Results & Uncertainty Communication

#### REQ-UNCERT-01: Dual-Target Clinical Risk Dashboard & Uncertainty Display
- **Feature Name:** Dual-Target Risk Visualizer with Confidence Intervals
- **Purpose:** Display both CAD presence probability and 10-year ASCVD risk with explicit clinical definitions, confidence bounds, and non-diagnostic context.
- **User Role:** Patient, Clinician
- **Preconditions:** Assessment inference completed.
- **Input:** Navigation to `/assessments/{id}/results`.
- **Processing / Business Rules:**
  1. Retrieve `inference_results` record for given `assessment_id`.
  2. Render two visually distinct gauges:
     - Gauge 1: **Coronary Artery Status (CAD Presence Indicator)** — Calibrated probability, confidence interval range ($[\text{lower}, \text{upper}]$), and tier badge.
     - Gauge 2: **10-Year Cardiovascular Event Risk (ASCVD)** — 10-year percentage and ACC/AHA guideline tier badge.
  3. Check for Out-of-Distribution (OOD) biomarker values: If any input biomarker exceeds the 99th percentile of the training distribution, display an advisory badge: *"Note: Certain entered biomarkers are outside the common training distribution; model uncertainty is elevated."*
  4. Prominently display non-diagnostic clinical disclaimer.
- **Expected Output:** High-clarity responsive dashboard view adhering to "Aethelgard Clinical" tokens.
- **Success Conditions:** Gauges render smoothly; risk categories clearly distinguished; zero ambiguity between the two targets.
- **Failure Conditions:** If inference record missing, return HTTP 404 with link to start new assessment.
- **Validation Rules:** Patient ownership verified via JWT session.
- **Security & Privacy:** Cross-tenant access blocked; audit log records result view event.
- **Dependencies:** Module 5.
- **Priority:** **MUST**
- **Acceptance Criteria:** Playwright test verifies dual dials render with distinct labels and tooltips explaining the clinical difference.

---

### Module 7: SHAP-Based Explainability

#### REQ-SHAP-01: Exact TreeSHAP Local Feature Attribution
- **Feature Name:** Mathematical Local SHAP Attribution Engine
- **Purpose:** Calculate exact, mathematically consistent Shapley values $\phi_i$ for all 13 features to explain which specific biomarkers drove the model's decision away from the baseline average.
- **User Role:** Patient, Clinician
- **Preconditions:** Calibrated tree-based model artifact loaded; inference completed.
- **Input:** 13-feature assessment vector, model object, background expectation $\mathbb{E}[f(x)]$.
- **Processing / Business Rules:**
  1. Execute `shap.TreeExplainer` on the underlying tree ensemble.
  2. Extract local Shapley values $\phi_1, \phi_2, \dots, \phi_{13}$.
  3. Verify mathematical additivity: Assert $\left| f(x) - \left( \mathbb{E}[f(x)] + \sum_{i=1}^{13} \phi_i \right) \right| \le 10^{-5}$.
  4. Rank features in descending order of absolute contribution $|\phi_i|$.
  5. Classify contributions:
     - Positive contribution ($\phi_i > 0$): Increases risk relative to cohort average (colored Crimson).
     - Negative contribution ($\phi_i < 0$): Decreases risk / provides protective effect (colored Emerald).
  6. Store attributions in `shap_explanations` table.
- **Expected Output:** Array of 13 feature attribution objects containing `feature_name`, `feature_value`, `shap_value`, `rank`, and `direction`.
- **Success Conditions:** Explanation generated in $< 25\text{ms}$; additivity invariance passes with zero error.
- **Failure Conditions:** Invariance violation ($> 10^{-5}$) triggers exception, logs audit alert, and falls back to safe cached calculation with alert tag.
- **Validation Rules:** Total features must equal 13.
- **Security & Privacy:** Explanations cached to prevent redundant compute on repeated views.
- **Dependencies:** SHAP C++ library bindings, XGBoost model.
- **Priority:** **MUST**
- **Acceptance Criteria:** Property-based test runs 100 test vectors and asserts $\epsilon \le 10^{-5}$ across 100% of cases.

#### REQ-SHAP-02: Interactive Waterfall Visualizer & Plain-Language Translation
- **Feature Name:** SHAP Waterfall Chart & Plain-Language Translation
- **Purpose:** Visually depict the feature attributions as an intuitive waterfall plot and translate the top 3 drivers into plain, non-technical English.
- **User Role:** Patient, Clinician
- **Preconditions:** Local SHAP attributions generated.
- **Input:** Array of SHAP attribution objects.
- **Processing / Business Rules:**
  1. Render SVG-based horizontal divergence chart centered on baseline log-odds $\mathbb{E}[f(x)]$.
  2. Render bars extending right (Crimson, risk-increasing) or left (Emerald, risk-decreasing), with interactive hover cards showing numerical $\phi_i$ values and clinical explanations.
  3. Deterministically generate 3 human-readable summary bullets without LLM hallucination:
     - Bullet 1: Primary risk accelerator (e.g. *"Resting blood pressure (158 mm Hg) contributed most significantly to your elevated score."*)
     - Bullet 2: Secondary risk factor (e.g. *"Serum cholesterol (245 mg/dL) was an additional contributing risk factor."*)
     - Bullet 3: Primary protective factor (e.g. *"Achieving a maximum heart rate of 168 bpm during exercise provided positive protective value."*)
  4. Include explicit notice: *"SHAP values quantify algorithmic model behavior and feature weighting; they do not prove direct biological causation."*
- **Expected Output:** Accessible interactive waterfall chart and summary bullet container.
- **Success Conditions:** Chart renders cleanly on all viewports; tooltips accessible via mouse hover and keyboard focus.
- **Failure Conditions:** If rendering fails, display tabular fallback of top 5 ranked features.
- **Validation Rules:** Text generation strictly rule-based based on feature rank and sign.
- **Security & Privacy:** View rendered client-side from authenticated API payload.
- **Dependencies:** Module 7 (REQ-SHAP-01).
- **Priority:** **MUST**
- **Acceptance Criteria:** Playwright test verifies chart renders with correct colors and summary text matches top ranked features.

---

### Module 8: Counterfactual Analysis

#### REQ-CF-01: Constrained Counterfactual Feasibility Engine
- **Feature Name:** Constrained Lifestyle What-If Simulator
- **Purpose:** Compute the minimal, physiologically realistic adjustments in modifiable biomarkers required to decrease predicted risk below clinical alert thresholds, while strictly locking immutable biological traits.
- **User Role:** Patient, Clinician
- **Preconditions:** Completed assessment with elevated or borderline risk ($P(\text{CAD}) \ge 0.20$).
- **Input:** Original 13-feature vector, target risk threshold ($\tau = 0.19$ or user-selected), locked attribute mask.
- **Processing / Business Rules:**
  1. Partition features into **Immutable** (`age`, `sex`, `ca`, `thal`) and **Modifiable** (`trestbps`, `chol`, `fbs`, `thalach`, `exang`).
  2. Strictly lock all immutable features: $\delta_j = 0$ for all $j \in \text{Immutable}$.
  3. Apply clinical boundary constraints on modifiable variables:
     - `trestbps`: Minimum realistic clinical reduction to $110\text{ mm Hg}$ (cannot set BP to $40\text{ mm Hg}$).
     - `chol`: Minimum realistic clinical reduction to $150\text{ mg/dL}$.
     - `fbs`: Modifiable to $0$ ($\le 120\text{ mg/dL}$).
     - `thalach`: Conditioning increase capped at $220 - \text{age}$.
  4. Perform optimization minimizing normalized L1 distance: $D(x, x+\delta) = \sum_k \frac{|\delta_k|}{\text{MAD}_k}$ subject to $P(x+\delta) \le \tau$.
  5. Compute discrete clinical intervention steps (e.g. "-15 mmHg Systolic BP", "-40 mg/dL Cholesterol").
  6. Return optimal counterfactual biomarker vector, achieved risk probability, and feasibility rating (`High`, `Moderate`, `Challenging`).
  7. Store profile in `counterfactual_profiles` table.
- **Expected Output:** Counterfactual solution object detailing recommended biomarker deltas, projected risk reduction, and feasibility rating.
- **Success Conditions:** Solution strictly preserves immutable attributes; achieved risk $< \tau$; returned values physiologically safe.
- **Failure Conditions:** If target risk is unreachable due to severe immutable damage (e.g. 3 colored fluoroscopy vessels, age 80), return: *"Target risk is unreachable through lifestyle biomarker adjustments alone; consultation with a cardiologist is strongly advised."*
- **Validation Rules:** Server enforces immutability and boundary limits regardless of client inputs.
- **Security & Privacy:** Computations executed in memory; results saved under patient ownership.
- **Dependencies:** Module 5 (ML Engine).
- **Priority:** **MUST**
- **Acceptance Criteria:** Unit tests assert that across 100 test runs, age and sex are modified 0 times, and proposed BP/cholesterol are within clinical life limits.

#### REQ-CF-02: Interactive What-If Biomarker Slider Simulator
- **Feature Name:** Client-Side Interactive Biomarker Adjuster
- **Purpose:** Allow patients to interactively drag biomarker sliders to simulate the real-time effect of potential lifestyle improvements on their projected risk.
- **User Role:** Patient, Clinician
- **Preconditions:** Assessment results view active.
- **Input:** User drags slider handles for `trestbps`, `chol`, `thalach`.
- **Processing / Business Rules:**
  1. Immutable features (Age, Sex, Anatomy) have disabled sliders with padlock icons and explanatory tooltips.
  2. Modifiable sliders bounded by safe clinical minimums and maximums.
  3. Debounce input changes ($150\text{ms}$) and query `/api/v1/inference/{id}/counterfactual/simulate`.
  4. Update projected risk dial in real time, rendering a green delta badge (e.g. `Projected: 24% (-18% Reduction)`).
  5. Display explicit advisory: *"Counterfactual projections represent hypothetical statistical scenarios for health awareness; they are not medical prescriptions or treatment guarantees."*
- **Expected Output:** Fluid interactive sliders with live gauge recalculation.
- **Success Conditions:** Live updates feel instantaneous ($< 150\text{ms}$ response); UI remains fully responsive without stutter.
- **Failure Conditions:** If simulation endpoint fails, display non-blocking error badge and retain last valid projection.
- **Validation Rules:** Slider values clamped to schema boundaries.
- **Security & Privacy:** Read-only simulation calls do not alter original persisted assessment record.
- **Dependencies:** Module 8 (REQ-CF-01).
- **Priority:** **MUST**
- **Acceptance Criteria:** Playwright test verifies dragging the blood pressure slider from 160 to 120 updates the projected risk percentage dynamically.

---

### Module 9: Personalized Health Education & Guidance

#### REQ-EDU-01: Contextual Evidence-Based Educational Modules
- **Feature Name:** Traceable Cardiovascular Health Guidance
- **Purpose:** Deliver educational guidance dynamically tailored to the patient's top identified risk drivers, citing accredited clinical guidelines.
- **User Role:** Patient
- **Preconditions:** Assessment completed; top SHAP risk drivers identified.
- **Input:** Array of identified elevated biomarkers (e.g. `trestbps > 140`, `chol > 200`).
- **Processing / Business Rules:**
  1. Map identified risk drivers to curated, verified educational content modules in `educational_resources` table.
  2. Render structured educational sections:
     - **Understanding the Biomarker:** What systolic blood pressure measures and why it stresses arterial walls.
     - **Evidence-Based Lifestyle Strategies:** ACC/AHA recommended lifestyle interventions (DASH diet, 150 mins/week aerobic activity, sodium reduction).
     - **Questions to Ask Your Doctor:** 3 structured questions to discuss during the next clinical visit.
  3. Every educational card must display traceable clinical source (e.g. *"Source: 2019 ACC/AHA Guideline on Primary Prevention of Cardiovascular Disease"*).
- **Expected Output:** Clean, readable educational cards with reference links.
- **Success Conditions:** Content matches patient's specific biomarker profile; zero generic or hallucinated medical claims.
- **Failure Conditions:** If no specific elevated drivers exist, display general cardiovascular wellness and maintenance guidance.
- **Validation Rules:** Content pulled strictly from vetted database records; no dynamic LLM generation without human clinical audit.
- **Security & Privacy:** Standard read operation.
- **Dependencies:** Assessment inference results.
- **Priority:** **SHOULD**
- **Acceptance Criteria:** Test verifies that a patient with elevated blood pressure receives the Hypertension & Sodium guidance module with verified citation.

---

### Module 10: Assessment History & Health Trends

#### REQ-HIST-01: Longitudinal Cardiovascular Tracking & Trend Charts
- **Feature Name:** Longitudinal Assessment Timeline & Telemetry Charts
- **Purpose:** Enable patients and clinicians to visualize cardiovascular risk, blood pressure, and cholesterol trajectory across multiple assessments over time.
- **User Role:** Patient, Clinician
- **Preconditions:** User has at least one completed assessment in `assessments` table.
- **Input:** User navigates to `/history`.
- **Processing / Business Rules:**
  1. Query `assessments` table for current `patient_id` ordered by `created_at ASC`.
  2. Join `inference_results` to extract CAD probability, ASCVD risk, and biomarkers for each point in time.
  3. Render multi-series time-series chart showing:
     - Series 1: Calibrated CAD Probability (%)
     - Series 2: Resting Systolic Blood Pressure (mm Hg)
     - Series 3: Total Serum Cholesterol (mg/dL)
  4. Provide interactive date scrubber: Clicking any point displays a modal with the full 13-biomarker snapshot and calculated delta from the previous assessment.
  5. If only 1 assessment exists, display informative banner: *"Complete a second assessment during your next health checkup to unlock longitudinal trend analytics."*
- **Expected Output:** Responsive, interactive time-series chart with reference bands (optimal vs elevated).
- **Success Conditions:** Chart renders smoothly; tooltips display exact date and numerical values; deltas correctly computed.
- **Failure Conditions:** If database query fails, display clean retry prompt.
- **Validation Rules:** Patient ownership enforced.
- **Security & Privacy:** Strictly scoped to authenticated user's records.
- **Dependencies:** `assessments`, `inference_results` tables.
- **Priority:** **MUST**
- **Acceptance Criteria:** Integration test creates 3 sequential assessments with varying vitals and verifies the API returns sorted chronological series with correct deltas.

---

### Module 11: Doctor Directory

#### REQ-DOC-01: Searchable Cardiology Provider Directory
- **Feature Name:** Filterable Clinical Cardiology Directory
- **Purpose:** Connect at-risk patients with qualified, board-certified clinical cardiologists and outpatient cardiac care clinics.
- **User Role:** Guest, Patient, Doctor, Administrator
- **Preconditions:** Directory entries populated in `doctors` table.
- **Input:** Search term (name, clinic), filter by `specialty` (General Cardiology, Interventional Cardiology, Electrophysiology, Preventative Cardiology), filter by `city` or `zip_code`.
- **Processing / Business Rules:**
  1. Query `doctors` table with case-insensitive search and filter parameters.
  2. Return paginated list (10 per page) with verified credentials, clinical specialty, clinic affiliation, phone number, address, and telehealth availability.
  3. Provide "Connect for Consultation" button that launches the Visit Briefing Generator (Module 14).
- **Expected Output:** High-density, accessible provider cards with contact information and location badges.
- **Success Conditions:** Search queries execute in $< 50\text{ms}$; pagination functions smoothly.
- **Failure Conditions:** Zero matching results displays clean empty state: *"No cardiologists found matching your criteria. Try expanding your search radius or selecting All Specialties."*
- **Validation Rules:** Input search strings sanitized against SQL injection.
- **Security & Privacy:** Directory data is public; patient searches are not logged against personal medical profiles.
- **Dependencies:** `doctors` table.
- **Priority:** **SHOULD**
- **Acceptance Criteria:** Playwright test verifies searching by "Preventative Cardiology" filters directory to matching specialists.

---

### Module 12: Hospital Directory

#### REQ-HOSP-01: Accredited Cardiac Hospital & Emergency Care Directory
- **Feature Name:** Cardiac Hospital & Emergency Center Finder
- **Purpose:** Provide users with verified information on accredited regional hospitals, cardiac catheterization labs, and 24/7 chest pain emergency centers.
- **User Role:** Guest, Patient, Doctor, Administrator
- **Preconditions:** Hospital directory populated in `hospitals` table.
- **Input:** Filter by `facility_type` (Comprehensive Cardiac Center, STEMI Receiving Center, General Hospital), filter by `state` or `city`.
- **Processing / Business Rules:**
  1. Query `hospitals` table based on filter criteria.
  2. Render facility cards detailing accreditation (e.g. American College of Cardiology Chest Pain Center Accreditation), trauma level, emergency department contact, address, and map link.
  3. Display prominent emergency alert banner: *"If you are experiencing acute chest pressure, shortness of breath, or radiating arm pain, call 911 or visit the nearest emergency department immediately."*
- **Expected Output:** Accessible hospital list with prominent emergency contact buttons.
- **Success Conditions:** Clean rendering; map links open in secure new tabs (`rel="noopener noreferrer"`).
- **Failure Conditions:** Empty search handled gracefully.
- **Validation Rules:** Sanitized query parameters.
- **Security & Privacy:** Public data; no user tracking.
- **Dependencies:** `hospitals` table.
- **Priority:** **SHOULD**
- **Acceptance Criteria:** Test asserts that hospital cards render emergency phone numbers and emergency chest pain disclaimer is visible.

---

### Module 13: Health Insurance Information & Comparison

#### REQ-INS-01: Preventative Cardiovascular Coverage & Cost Navigator
- **Feature Name:** Insurance Preventative Coverage & Out-of-Pocket Estimator
- **Purpose:** Educate users on preventative cardiovascular screenings covered under standard ACA/CMS guidelines and estimate out-of-pocket costs for common diagnostic tests.
- **User Role:** Guest, Patient
- **Preconditions:** Content populated in `insurance_guides` table.
- **Input:** User selects insurance plan type (Medicare, Medicaid, Commercial High-Deductible, Commercial PPO).
- **Processing / Business Rules:**
  1. Display mandate breakdown under Affordable Care Act (ACA) § 2713: Annual wellness exams, lipid panels (total cholesterol, HDL, LDL, triglycerides), and blood pressure screenings are mandated at $0$ out-of-pocket copay for in-network providers.
  2. Render diagnostic cost estimator explaining typical cost ranges for secondary cardiac tests (Coronary Calcium Scan / CAC, Exercise Treadmill Stress Test, Echocardiogram, Nuclear Myocardial Perfusion Imaging).
  3. Provide "Questions to Ask Your Insurer Before Testing" checklist.
- **Expected Output:** Educational comparison table and cost estimator guide.
- **Success Conditions:** Transparent, unambiguous explanation of coverage rules.
- **Failure Conditions:** If category unavailable, default to General Preventative Coverage Guide.
- **Validation Rules:** N/A.
- **Security & Privacy:** Educational tool; zero policy numbers or insurance IDs collected.
- **Dependencies:** `insurance_guides` table.
- **Priority:** **COULD**
- **Acceptance Criteria:** Test verifies selecting "Commercial PPO" displays the $0 copay preventative mandate for annual lipid panels.

---

### Module 14: Downloadable Assessment Reports

#### REQ-REP-01: 1-Page Clinical Visit Briefing Document Generator
- **Feature Name:** Clinical Visit Summary PDF & JSON Export
- **Purpose:** Compile patient assessment results, TreeSHAP feature attributions, and counterfactual lifestyle targets into a high-density, 1-page clinical summary suitable for physician review.
- **User Role:** Patient, Clinician
- **Preconditions:** Completed assessment record available.
- **Input:** User clicks "Download Clinical Visit Briefing" (`GET /api/v1/assessments/{id}/report`).
- **Processing / Business Rules:**
  1. Verify user authorization (owning patient or authorized clinician).
  2. Assemble comprehensive report payload:
     - Patient demographic and intake date.
     - 13 clinical biomarkers with laboratory normal reference ranges.
     - Calibrated CAD presence probability and 10-year ASCVD risk.
     - Top 5 TreeSHAP feature attribution ranking with directional impact.
     - Counterfactual lifestyle target parameters.
     - Traceable clinical references and non-diagnostic disclaimer.
     - Physician clinical notes section with signature/date line.
  3. Format report as structured JSON or render clean print-optimized PDF layout.
  4. Log report generation in `audit_logs`.
- **Expected Output:** Downloadable file (`HeartXAI_Clinical_Briefing_{assessment_id}.pdf` / `.json`).
- **Success Conditions:** Report downloads cleanly; formatting strictly contained to printable page boundaries.
- **Failure Conditions:** Unauthorized access returns HTTP 403 Forbidden.
- **Validation Rules:** Valid assessment ID.
- **Security & Privacy:** Generated on demand; never permanently cached on public server endpoints; logged in audit trail.
- **Dependencies:** Report generation service, Module 4, Module 5, Module 7, Module 8.
- **Priority:** **MUST**
- **Acceptance Criteria:** Integration test verifies calling the report endpoint returns HTTP 200 with complete data structure and audit log entry.

---

### Module 15: Notifications (Contextual & In-App)

#### REQ-NOTIF-01: In-App Clinical & System Notifications
- **Feature Name:** Contextual In-App Notification Center
- **Purpose:** Alert users to essential account events (e.g. clinician reviewed assessment, annual assessment reminder due) without intrusive marketing spam.
- **User Role:** Patient, Clinician, Administrator
- **Preconditions:** User is authenticated.
- **Input:** System triggers event (e.g. clinician adds review note to assessment).
- **Processing / Business Rules:**
  1. Insert notification record into `notifications` table (`user_id`, `title`, `message`, `type`, `read_status`, `link_url`).
  2. Client polls `/api/v1/notifications/unread` or receives via SSE.
  3. Render unread badge count in navigation bar.
  4. User clicking notification marks `read_status = true` and navigates to target record.
- **Expected Output:** Unread badge and notification dropdown panel.
- **Success Conditions:** Notification reliably delivered; badge count updates instantly upon reading.
- **Failure Conditions:** If notification fails, core medical workflows remain completely unaffected.
- **Validation Rules:** N/A.
- **Security & Privacy:** Scoped strictly to target user; zero sensitive clinical vitals included in notification text.
- **Dependencies:** `notifications` table.
- **Priority:** **COULD**
- **Acceptance Criteria:** Test verifies creating a clinical note generates an unread notification for the patient that marks as read upon interaction.

---

### Module 16: Patient Privacy & Consent Management

#### REQ-PRIV-01: Time-Bounded Doctor Authorization & Access Revocation
- **Feature Name:** Patient-Gated Clinician Authorization Engine
- **Purpose:** Enforce strict patient sovereignty: No clinician can access a patient's medical assessments without an explicit, time-bounded consent grant from the patient.
- **User Role:** Patient, Clinician
- **Preconditions:** Patient is authenticated.
- **Input:** Patient selects a registered doctor and grants access duration (e.g. 7 days, 30 days), or generates a single-use 6-digit Consultation Access Code (`POST /api/v1/privacy/grants`).
- **Processing / Business Rules:**
  1. Create record in `patient_doctor_grants` table: `patient_id`, `doctor_id`, `grant_type`, `expires_at`, `status = "ACTIVE"`.
  2. Clinician attempting to access patient record must present valid active grant; otherwise backend returns HTTP 403 Forbidden.
  3. Patient can click "Revoke Access Immediately" at any time, instantly setting `status = "REVOKED"`.
  4. Automatic expiration when `current_time > expires_at`.
  5. All grant creations, accesses, and revocations logged in `audit_logs`.
- **Expected Output:** HTTP 201 Created with grant summary; active grants table in Patient Privacy Settings.
- **Success Conditions:** Clinician access granted only while active; immediately blocked once revoked or expired.
- **Failure Conditions:** Expired grant returns HTTP 403: *"Consent authorization has expired. Please request a new consultation grant from the patient."*
- **Validation Rules:** Expiration duration between 1 hour and 90 days.
- **Security & Privacy:** Core compliance gate for HIPAA Privacy Rule (45 CFR § 164.508) and GDPR Article 6(1)(a).
- **Dependencies:** `patient_doctor_grants` table, RBAC middleware.
- **Priority:** **MUST**
- **Acceptance Criteria:** Security test suite verifies clinician receives HTTP 403 before grant, HTTP 200 after grant, and HTTP 403 immediately following patient revocation.

#### REQ-PRIV-02: Patient Data Export & Account Deletion (Right to Be Forgotten)
- **Feature Name:** GDPR / CCPA Data Portability & Complete Erasure
- **Purpose:** Allow patients to export all personal health data in machine-readable JSON format, or request complete cryptographic account deletion.
- **User Role:** Patient
- **Preconditions:** Patient is authenticated.
- **Input:** User clicks "Export My Health Data" or "Delete Account" (with password confirmation).
- **Processing / Business Rules:**
  1. **Export:** Assemble full JSON archive of user profile, assessments, inference results, and SHAP attributions; return as downloadable file.
  2. **Deletion:** Validate password; execute cascading hard delete of patient assessments, inference results, and profiles from relational database; record pseudonymized deletion tombstone in `audit_logs` (retaining zero health data) to fulfill regulatory auditability.
- **Expected Output:** Downloadable JSON file for export; HTTP 200 with redirection to landing page for deletion.
- **Success Conditions:** All patient health records completely expunged upon deletion confirmation.
- **Failure Conditions:** Incorrect password rejection prevents accidental deletion.
- **Validation Rules:** Password must match current hash.
- **Security & Privacy:** Enforces GDPR Article 17 (Right to Erasure) and Article 20 (Data Portability).
- **Dependencies:** Relational database cascade triggers.
- **Priority:** **SHOULD**
- **Acceptance Criteria:** Integration test verifies account deletion completely purges all associated records from `assessments` and `patient_profiles` tables.

---

### Module 17: Administrator Dashboard

#### REQ-ADMIN-01: System Governance & ML Health Monitoring Center
- **Feature Name:** Administrative Overview & Model Telemetry Center
- **Purpose:** Provide platform administrators and compliance officers with unified visibility into system health, active user counts, inference volumes, and model calibration metrics.
- **User Role:** Administrator
- **Preconditions:** User is authenticated with `role == "ADMIN"`.
- **Input:** User navigates to `/admin`.
- **Processing / Business Rules:**
  1. Verify administrator role claim in JWT token.
  2. Query aggregated metrics: Total registered patients, total verified clinicians, total assessments completed today/all-time, p95 inference latency, and system error rate.
  3. Render active model status widget showing current deployed model version (`v2.0.0`), sha256 checksum, and calibration Brier score.
  4. Provide quick-action links to User Management, Audit Logs, and Directory Editor.
- **Expected Output:** High-density administrative operations center with live telemetry.
- **Success Conditions:** Page renders in $< 1.0\text{s}$; non-admins strictly blocked with HTTP 403.
- **Failure Conditions:** Database connection degradation displays partial telemetry with warning badge.
- **Validation Rules:** N/A.
- **Security & Privacy:** Accessible exclusively to verified administrator accounts.
- **Dependencies:** Admin service, RBAC middleware.
- **Priority:** **MUST**
- **Acceptance Criteria:** Security test verifies non-admin users attempting to load `/admin` receive HTTP 403 Forbidden.

#### REQ-ADMIN-02: Clinician Credential Verification Queue
- **Feature Name:** Clinician Medical License Verification Queue
- **Purpose:** Enable administrators to review submitted medical credentials (medical license number, state, clinic affiliation) before approving a user for `CLINICIAN` role access.
- **User Role:** Administrator
- **Preconditions:** At least one clinician registration with `clinician_status == "PENDING_VERIFICATION"`.
- **Input:** Admin reviews credential record and clicks "Approve Clinician" or "Reject with Reason".
- **Processing / Business Rules:**
  1. On approval, update `users.clinician_status = "VERIFIED"` and grant active clinician permissions.
  2. On rejection, set `users.clinician_status = "REJECTED"`, record rejection reason, and send notification.
  3. Log verification action in `audit_logs`.
- **Expected Output:** Updated queue table; clinician granted access upon approval.
- **Success Conditions:** Clinicians cannot view cohort data until approved by an administrator.
- **Failure Conditions:** Missing license number blocks approval.
- **Validation Rules:** License verification notes required on rejection.
- **Security & Privacy:** Prevents fraudulent actors from posing as physicians to gain patient records.
- **Dependencies:** `users` table, Module 2.
- **Priority:** **MUST**
- **Acceptance Criteria:** Automated test verifies a pending clinician cannot access patient cohort data until administrator executes approval endpoint.

---

### Module 18: Content & Directory Management

#### REQ-DIR-01: Administrative Directory & Resource Management
- **Feature Name:** CRUD Management for Doctors, Hospitals & Educational Resources
- **Purpose:** Allow administrators to create, update, and manage doctor directory listings, hospital records, and educational health guides.
- **User Role:** Administrator
- **Preconditions:** User is authenticated with `role == "ADMIN"`.
- **Input:** Add/Edit forms for doctors, hospitals, and educational content articles.
- **Processing / Business Rules:**
  1. Standard CRUD operations on `doctors`, `hospitals`, and `educational_resources` tables.
  2. Validate required fields (Doctor: name, NPI, specialty, address; Hospital: name, type, emergency phone; Article: title, body, clinical citation).
  3. Sanitize rich text inputs to eliminate XSS risks.
  4. Audit log records all additions, updates, and deletions.
- **Expected Output:** Real-time update of directory listings across public and patient views.
- **Success Conditions:** Updated records instantly reflected in user searches.
- **Failure Conditions:** Duplicate NPI or malformed phone number returns HTTP 422.
- **Validation Rules:** Proper URL formats, valid phone numbers.
- **Security & Privacy:** Admin-only endpoints.
- **Dependencies:** Directory tables.
- **Priority:** **SHOULD**
- **Acceptance Criteria:** Integration test verifies admin creating a new doctor listing makes that doctor immediately discoverable in the patient directory search.

---

### Module 19: ML Model Version Management

#### REQ-MLM-01: Model Registry & Artifact Version Governance
- **Feature Name:** Machine Learning Model Registry & Integrity Verification
- **Purpose:** Maintain an auditable registry of all deployed model pipelines, tracking version strings, cryptographic checksums, training dataset provenance, and validation metrics.
- **User Role:** Administrator, System
- **Preconditions:** Model artifact saved in `backend/models/`.
- **Input:** Application startup or admin model inspection query (`GET /api/v1/admin/models`).
- **Processing / Business Rules:**
  1. At application boot, compute SHA-256 hash of `heartxai_model_v2.0.0.joblib` and compare against recorded registry hash.
  2. If hash mismatch occurs, abort server boot with fatal error: *"Model integrity check failed: SHA-256 mismatch. Potential unauthorized model alteration detected."*
  3. Record model metadata in `model_registry` table: `version` (`"2.0.0"`), `algorithm` (`"Calibrated XGBoost + HistGradient"`), `training_cohort` (`"UCI Cleveland Benchmark N=297"`), `test_auroc` (`0.872`), `brier_score` (`0.118`), `deployed_at`.
  4. Ensure all inferences store the exact active `model_version` in `inference_results`.
- **Expected Output:** Verified model registry endpoint returning active and archived model specs.
- **Success Conditions:** Model artifact tamper detection operational; 100% of inferences traced to exact model version.
- **Failure Conditions:** Corrupted model file halts server safely before serving unverified predictions.
- **Validation Rules:** Semantic versioning format `X.Y.Z`.
- **Security & Privacy:** Prevents adversarial model substitution or model drift in production.
- **Dependencies:** Filesystem storage, `model_registry` table.
- **Priority:** **MUST**
- **Acceptance Criteria:** Test verifies that modifying a single byte in the model file causes the boot integrity checker to throw an integrity exception.

---

### Module 20: Audit Logs & System Monitoring

#### REQ-AUD-01: Immutable Security & Clinical Data Access Audit Trail
- **Feature Name:** Immutable Audit Logging & Query Explorer
- **Purpose:** Maintain a tamper-resistant, queryable audit trail recording every security, authentication, and clinical data access event across the platform.
- **User Role:** Administrator, System
- **Preconditions:** System operational.
- **Input:** Any API call triggering authentication, assessment submission, patient record view, clinician access, or role change.
- **Processing / Business Rules:**
  1. Middleware and service hooks capture: `timestamp` (UTC ISO 8601), `user_id` (or anonymous), `role`, `action_type` (e.g. `"LOGIN"`, `"ASSESSMENT_CREATED"`, `"RECORD_VIEWED"`, `"CONSENT_GRANTED"`), `resource_id`, `ip_address`, `user_agent`, and `status_code`.
  2. Insert record into `audit_logs` table within independent database transaction.
  3. Deny any SQL `UPDATE` or `DELETE` operations on `audit_logs` table (immutable append-only table enforced via database trigger or ORM constraints).
  4. Provide admin explorer view with search by user, action, and date range.
- **Expected Output:** Complete, tamper-resistant chronological log of system activity.
- **Success Conditions:** 100% of sensitive operations reliably logged; zero data loss even during API failures.
- **Failure Conditions:** If audit database write fails, abort sensitive transaction to prevent unlogged clinical record access.
- **Validation Rules:** N/A.
- **Security & Privacy:** Enforces HIPAA Security Rule audit controls (45 CFR § 164.312(b)) and GDPR accountability requirements.
- **Dependencies:** `audit_logs` table.
- **Priority:** **MUST**
- **Acceptance Criteria:** Test verifies that logging in, submitting an assessment, and viewing a patient record each generate corresponding immutable rows in `audit_logs`.

---

## 3. Requirements Summary Matrix

| Module # | Module Title | Total Requirements | MUST | SHOULD | COULD |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **1** | Public Website & Product Information | 2 | 1 | 1 | 0 |
| **2** | Registration, Login & Authentication | 3 | 3 | 0 | 0 |
| **3** | Patient Profile & Health Information | 1 | 0 | 1 | 0 |
| **4** | Cardiovascular Assessment Form | 1 | 1 | 0 | 0 |
| **5** | Machine Learning Prediction | 2 | 2 | 0 | 0 |
| **6** | Prediction Results & Uncertainty | 1 | 1 | 0 | 0 |
| **7** | SHAP-Based Explainability | 2 | 2 | 0 | 0 |
| **8** | Counterfactual Analysis | 2 | 2 | 0 | 0 |
| **9** | Personalized Health Education | 1 | 0 | 1 | 0 |
| **10** | Assessment History & Health Trends | 1 | 1 | 0 | 0 |
| **11** | Doctor Directory | 1 | 0 | 1 | 0 |
| **12** | Hospital Directory | 1 | 0 | 1 | 0 |
| **13** | Health Insurance Information | 1 | 0 | 0 | 1 |
| **14** | Downloadable Assessment Reports | 1 | 1 | 0 | 0 |
| **15** | Notifications (Contextual) | 1 | 0 | 0 | 1 |
| **16** | Patient Privacy & Consent Management | 2 | 1 | 1 | 0 |
| **17** | Administrator Dashboard | 2 | 2 | 0 | 0 |
| **18** | Content & Directory Management | 1 | 0 | 1 | 0 |
| **19** | ML Model Version Management | 1 | 1 | 0 | 0 |
| **20** | Audit Logs & System Monitoring | 1 | 1 | 0 | 0 |
| **TOTAL** | **20 Modules** | **29 Features** | **19 MUST** | **8 SHOULD** | **2 COULD** |
