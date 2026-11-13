# HeartXAI 2.0 — End-to-End User Journeys Specification

**Document ID:** HXAI-REQ-005  
**Version:** 2.0.0  
**Phase:** Phase 2 — Product Requirements & System Scope  
**Status:** Complete / Ready for Review  
**Author:** Senior Systems Analyst & Senior UX Designer  

---

## 1. Overview & Methodology

This document specifies eleven (11) comprehensive, end-to-end user journeys for **HeartXAI 2.0**. Each journey documents the complete lifecycle: preconditions, normal happy path, alternate paths, error conditions with actionable recovery mechanisms, authorization requirements, and the expected final state.

---

## 2. The 11 Detailed User Journeys

### Journey 1: Guest Exploring the Platform & Testing the Sandbox
- **Actor:** Guest (Unauthenticated Visitor)
- **Preconditions:** Web application accessible; zero cookies or active sessions.
- **Normal Flow:**
  1. Visitor arrives at `https://heartxai.internal/` (`/`).
  2. Reads hero section and non-diagnostic clinical disclaimer banner.
  3. Scrolls to "Clinical Methodology & Explainable AI" section; reads summary of TreeSHAP and the 13 biomarkers.
  4. Clicks "Try Interactive Sandbox".
  5. Selects "Synthetic Profile A: 54yo Male with Mild Hypertension".
  6. Observes dual-target dials update instantly in-memory (CAD probability 38%, 10-year ASCVD 7.2%).
  7. Interacts with the SHAP waterfall chart tooltip to view why systolic blood pressure pushed risk higher.
  8. Clicks "Create Your Free Account" in the banner to start onboarding.
- **Alternate Flow:** Visitor inputs custom biomarker values into the sandbox sliders instead of picking a preset profile. Sandbox recalculates locally via stateless API call without database persistence.
- **Error Scenarios & Recovery:**
  - *Network timeout on sandbox calculation:* UI renders inline recovery notice: *"Sandbox computation timed out. Click here to reload sample profile."*
- **Permissions:** Unrestricted public access.
- **Expected Final State:** Visitor understands platform value proposition, trusts scientific transparency, and transitions to registration page with zero persistent data stored.

---

### Journey 2: Patient Registering & Completing Profile
- **Actor:** Patient (New User)
- **Preconditions:** Guest is on `/register`.
- **Normal Flow:**
  1. Enters full name ("Marcus Vance"), email (`marcus.vance@example.com`), password, and confirms role as `"Patient"`.
  2. Checks mandatory consent box: *"I understand HeartXAI 2.0 is an educational health-awareness platform and not a medical diagnostic device."*
  3. Clicks "Create Account".
  4. Backend hashes password with bcrypt (rounds=12), creates user record, and issues secure HttpOnly JWT cookie.
  5. User is redirected to `/onboarding/profile`.
  6. Enters Date of Birth (yielding Age 54), biological sex (Male), and preferred units (US Standard).
  7. Clicks "Save Profile & Continue".
  8. System saves baseline in `patient_profiles` and routes to Patient Dashboard (`/dashboard`).
- **Alternate Flow:** User skips secondary profile step; default units (US Standard) and empty baseline assigned; user can enter demographics directly in intake wizard.
- **Error Scenarios & Recovery:**
  - *Duplicate email address:* Backend returns HTTP 409 Conflict. Frontend displays inline field error: *"An account with this email already exists. Click here to log in."*
  - *Weak password:* Client-side validator highlights failing complexity criteria (e.g. *"Must contain at least 1 number"*).
- **Permissions:** Unauthenticated for registration; JWT token issued for profile creation.
- **Expected Final State:** User account securely created in `users` table, baseline stored in `patient_profiles`, active session established, user on `/dashboard`.

---

### Journey 3: Patient Submitting a Health Assessment
- **Actor:** Patient (Marcus)
- **Preconditions:** Authenticated as `PATIENT`; on `/dashboard`.
- **Normal Flow:**
  1. Clicks primary CTA: "Start New Cardiovascular Assessment" (`/assessments/new`).
  2. **Step 1 (Demographics & Symptoms):** Pre-populated with Age (54) and Sex (Male). Marcus selects Chest Pain Type: `Non-anginal Pain`. Clicks "Next: Vitals & Hemodynamics".
  3. **Step 2 (Hemodynamics & Vitals):** Enters Resting Blood Pressure (`158 mm Hg`), Maximum Heart Rate Achieved (`164 bpm`), and Exercise-Induced Angina (`No`). Clicks "Next: Laboratory & Diagnostics".
  4. **Step 3 (Diagnostics & Labs):** Enters Serum Cholesterol (`248 mg/dL`), Fasting Blood Sugar (`Normal / <= 120`), Resting ECG (`Normal`), ST Depression (`1.2 mm`), Peak ST Slope (`Upsloping`), Major Vessels Colored by Fluoroscopy (`0`), and Thallium Stress Test (`Normal`).
  5. Clicks "Analyze Cardiovascular Profile".
  6. Client executes Zod schema validation; submits payload via `POST /api/v1/assessments`.
  7. Full-screen clinical processing animation displays: *"Calibrating model probabilities... Computing TreeSHAP attributions... Solving counterfactual pathways..."*
  8. Backend completes transaction and redirects client to `/assessments/{new_id}/results`.
- **Alternate Flow:** Patient exits midway through Step 2; wizard saves draft state in browser session storage; on return, prompts: *"Resume your in-progress assessment?"*
- **Error Scenarios & Recovery:**
  - *Out-of-range entry (e.g. entered Chol = 25 mg/dL):* Field-level validation flags input with red border and helper: *"Total cholesterol must be between 100 and 600 mg/dL."* Forward navigation blocked until corrected.
  - *Server error during ML calculation:* Transaction rolls back cleanly; client displays recovery banner: *"Assessment could not be analyzed due to a temporary service issue. Your entered data has been preserved. Click 'Retry Analysis'."*
- **Permissions:** `PATIENT` role owning session.
- **Expected Final State:** New record inserted into `assessments` and `inference_results`; user viewing `/assessments/{id}/results`.

---

### Journey 4: Patient Viewing Prediction Results & Uncertainty
- **Actor:** Patient (Marcus)
- **Preconditions:** Assessment successfully completed; user on `/assessments/{id}/results`.
- **Normal Flow:**
  1. View loads with clean fade-in adhering to "Aethelgard Clinical" tokens.
  2. Prominently observes two visually distinct circular dials:
     - **Dial 1: Coronary Artery Status (CAD Presence Indicator):** Displays `44% Probability` (Confidence Interval: $39\% - 49\%$) with Amber badge `BORDERLINE RISK`. Explanatory caption: *"Indicates statistical likelihood of significant coronary stenosis based on clinical benchmark cohorts."*
     - **Dial 2: 10-Year Prospective Cardiovascular Event Risk (ASCVD):** Displays `9.8% 10-Year Risk` with Amber badge `BORDERLINE RISK (ACC/AHA Guidelines)`. Explanatory caption: *"Projected 10-year risk of first hard cardiovascular event based on the 2013 ACC/AHA pooled cohort equations."*
  3. Reads prominent non-diagnostic medical disclaimer.
  4. Scrolls to "AI Feature Attribution & Explanation" section.
- **Alternate Flow:** Patient hovers over the Confidence Interval info icon to read how the Wilson score interval is computed from calibrated sample variance.
- **Error Scenarios & Recovery:**
  - *Missing inference record:* If URL manipulated to non-existent ID, API returns HTTP 404; view displays clean error page: *"Assessment record not found. Return to Dashboard."*
- **Permissions:** `PATIENT` role owning the assessment, or `CLINICIAN` holding an active grant.
- **Expected Final State:** Patient clearly understands their dual risk scores without confusing binary disease presence with prospective 10-year event risk.

---

### Journey 5: Patient Understanding SHAP Explanations
- **Actor:** Patient (Marcus)
- **Preconditions:** On `/assessments/{id}/results`; scrolled to SHAP section.
- **Normal Flow:**
  1. Observes interactive horizontal TreeSHAP waterfall plot centered on the cohort baseline $\mathbb{E}[f(x)] = -0.12$.
  2. Sees Crimson bars extending right (pushing risk higher):
     - `Resting BP = 158 mmHg (+0.42 log-odds)`
     - `Cholesterol = 248 mg/dL (+0.28 log-odds)`
     - `Age = 54 (+0.18 log-odds)`
  3. Sees Emerald bars extending left (protective factors reducing risk):
     - `Max Heart Rate = 164 bpm (-0.31 log-odds)`
     - `Fluoroscopy Vessels = 0 (-0.26 log-odds)`
     - `Exercise Angina = No (-0.15 log-odds)`
  4. Reads the deterministic "Plain-Language Insights" card immediately below the chart:
     - *"Your elevated resting blood pressure (158 mm Hg) is the single strongest factor pushing your cardiovascular score higher."*
     - *"Your elevated serum cholesterol (248 mg/dL) also added upward pressure to your score."*
     - *"Your strong exercise heart rate tolerance (164 bpm) and clear major vessels provided strong protective counterweights."*
  5. Clicks "How are these calculated?" to read educational modal regarding Shapley values and cooperative game theory.
- **Alternate Flow:** Patient toggles from "Visual Waterfall View" to "Tabular Feature Ranking View" for high-density reading.
- **Error Scenarios & Recovery:**
  - *Explanation rendering failure:* If SVG chart fails to render, tabular fallback activates automatically, ensuring zero information loss.
- **Permissions:** Authenticated assessment owner or authorized clinician.
- **Expected Final State:** Patient understands precisely which biological and lifestyle factors drove their score, demystifying the algorithmic prediction.

---

### Journey 6: Patient Exploring Counterfactual Scenarios
- **Actor:** Patient (Marcus)
- **Preconditions:** On `/assessments/{id}/results`; opens "Interactive What-If Simulator" tab.
- **Normal Flow:**
  1. Observes counterfactual slider panel.
  2. Notices `Age (54)`, `Sex (Male)`, and `Fluoroscopy Major Vessels (0)` have disabled slider tracks with a padlock icon and tooltip: *"Biological attributes and anatomical scan findings cannot be changed through lifestyle interventions."*
  3. Modifiable biomarker sliders (`Resting BP`, `Total Cholesterol`) are active, showing current baseline markers.
  4. Clicks "Calculate Optimal Clinical Target" button.
  5. Backend constrained solver computes optimal realistic perturbation:
     - Target: Reduce Systolic BP from $158$ to $125\text{ mm Hg}$ ($-33\text{ mm Hg}$).
     - Target: Reduce Total Cholesterol from $248$ to $190\text{ mg/dL}$ ($-58\text{ mg/dL}$).
  6. Achieved Projected CAD Risk updates dynamically to `21% (OPTIMAL TIER, -23% absolute reduction)`.
  7. Feasibility badge displays `Moderate Feasibility (Achievable via standard dietary changes and first-line antihypertensive therapy)`.
  8. Marcus manually adjusts the blood pressure slider to $135\text{ mm Hg}$ to test a smaller reduction; projected risk recalculates in real-time ($27\%$).
- **Alternate Flow:** Patient inputs extreme slider adjustment ($80\text{ mm Hg}$); solver clamps input to safe physiological floor ($110\text{ mm Hg}$) with tooltip: *"Target blood pressure clamped to clinical minimum for patient safety."*
- **Error Scenarios & Recovery:**
  - *Unreachable target:* For an advanced demographic case where target risk cannot be reached within safe boundaries, system displays: *"Target risk is unreachable through lifestyle modifications alone. Formal consultation with a cardiologist is recommended."*
- **Permissions:** Authenticated assessment owner or authorized clinician.
- **Expected Final State:** Patient departs with realistic, quantifiable clinical biomarker goals rather than vague anxiety.

---

### Journey 7: Patient Viewing Educational Guidance
- **Actor:** Patient (Marcus)
- **Preconditions:** Assessment completed with elevated Blood Pressure and Cholesterol.
- **Normal Flow:**
  1. Navigates to "Personalized Health Guidance" tab on the results screen.
  2. System presents two highlighted educational modules matching his top SHAP drivers:
     - **Module 1: Managing Systolic Blood Pressure (AHA Guideline 2019):** Explains arterial stiffness, sodium reduction impact (average 5–6 mmHg reduction), and the DASH dietary pattern.
     - **Module 2: Understanding Lipids & Cholesterol:** Explains difference between LDL and HDL, saturated fat reduction, and when statin therapy is evaluated by physicians.
  3. Clicks "Questions to Ask Your Doctor" and reviews 3 structured questions:
     - *"Given my resting BP of 158 mmHg, should we consider ambulatory blood pressure monitoring?"*
     - *"Would you recommend a Coronary Calcium Scan (CAC) to evaluate my arterial plaque status?"*
     - *"What lifestyle modifications should I focus on before my next follow-up?"*
  4. Clicks "Add to Doctor Briefing Report".
- **Alternate Flow:** Patient with all biomarkers in normal range receives cardiovascular wellness maintenance guidance and recommended re-screening intervals (every 2 years).
- **Error Scenarios & Recovery:**
  - *Database content fetch timeout:* Falls back to embedded local standard AHA educational guidelines.
- **Permissions:** Authenticated patient.
- **Expected Final State:** Patient gains accredited, actionable medical literacy tailored to their exact risk profile.

---

### Journey 8: Patient Accessing Assessment History & Trends
- **Actor:** Patient (Marcus, returning 6 months later for second checkup)
- **Preconditions:** Marcus has completed Assessment 1 (May 2026) and Assessment 2 (November 2026); on `/history`.
- **Normal Flow:**
  1. Navigates to `/history`.
  2. Multi-series time-series chart renders tracking:
     - CAD Probability: Dropped from $44\%$ in May to $28\%$ in November.
     - Resting Systolic BP: Dropped from $158\text{ mm Hg}$ to $132\text{ mm Hg}$.
     - Total Cholesterol: Dropped from $248\text{ mg/dL}$ to $202\text{ mg/dL}$.
  3. Observes positive green progress badge: *"Cardiovascular Risk Trajectory: Improving (-16% CAD Risk Reduction)"*.
  4. Clicks "Compare Assessments" button.
  5. Side-by-side delta table opens, highlighting exact changes across all 13 biomarkers between May and November.
  6. Clicks "Export Full History Report".
- **Alternate Flow:** Patient with only 1 assessment views baseline record and an educational prompt explaining the value of longitudinal tracking.
- **Error Scenarios & Recovery:**
  - *Network error retrieving history:* Retry button provided with local caching fallback.
- **Permissions:** Scoped strictly to `current_user.id`.
- **Expected Final State:** Patient clearly sees evidence of health progress over time, reinforcing positive behavioral change.

---

### Journey 9: Patient Finding a Doctor or Hospital
- **Actor:** Patient (Marcus)
- **Preconditions:** Looking for a local cardiologist for a consultation; on `/care-connect`.
- **Normal Flow:**
  1. Enters zip code `94107` and selects Specialty: `Preventative Cardiology`.
  2. Search returns 4 verified local providers.
  3. Selects "Dr. Sarah Lin, MD, FACC — Outpatient Cardiology Center".
  4. Reviews office address, phone number, hospital affiliations, and accepted insurance plans.
  5. Clicks "Prepare Doctor Visit Briefing".
  6. System triggers Module 14 to compile his 1-page clinical summary (including biomarkers, SHAP attributions, and questions).
  7. Downloads PDF `HeartXAI_Visit_Briefing_Marcus_Vance.pdf` to bring to his appointment.
- **Alternate Flow:** Marcus switches tabs to "Hospital Directory", filters by "Accredited Chest Pain Center", and identifies the nearest emergency facility with 24/7 cardiac catheterization services.
- **Error Scenarios & Recovery:**
  - *No doctors found in zip code:* System prompts: *"No specialists found within 10 miles. Expanding search to 25 miles..."* and displays regional centers.
- **Permissions:** Public read access for directory; authenticated for personalized briefing export.
- **Expected Final State:** Patient is fully prepared for an in-person clinical consultation with physical documentation.

---

### Journey 10: Patient Exploring Health Insurance Coverage
- **Actor:** Patient (Marcus)
- **Preconditions:** Wants to understand if diagnostic tests recommended by his doctor are covered; on `/insurance`.
- **Normal Flow:**
  1. Selects insurance plan category: `Commercial PPO Plan`.
  2. Reads ACA § 2713 Preventative Mandate guide: Confirms annual lipid panel and blood pressure checks have **$0 out-of-pocket copay** when using in-network laboratories.
  3. Navigates to "Diagnostic Test Cost Estimator":
     - Reviews estimated out-of-pocket range for a Coronary Artery Calcium (CAC) scan ($100 – $250, often not covered by standard insurance).
     - Reviews coverage criteria for Exercise Treadmill Stress ECG (typically covered subject to deductible/coinsurance with symptomatic indication).
  4. Clicks "Download Insurance Verification Questions" checklist to call his insurance provider's member services.
- **Alternate Flow:** User selects "Medicare Part B" to view coverage rules for annual wellness visits and cardiovascular screening blood tests (covered once every 5 years under Medicare).
- **Error Scenarios & Recovery:** N/A (Static verified educational content).
- **Permissions:** Public / Patient read access.
- **Expected Final State:** Patient understands their financial responsibilities and preventative coverage rights before booking tests.

---

### Journey 11: Administrator Managing Platform Information & Governance
- **Actor:** Administrator / Compliance Officer (Elena Rostova)
- **Preconditions:** Authenticated as `role == "ADMIN"`; on `/admin`.
- **Normal Flow:**
  1. Logs into Administrative Portal.
  2. Checks System Governance Dashboard:
     - Active Users: 1,420 Patients, 38 Clinicians.
     - p95 Inference Latency: $182\text{ms}$ (healthy).
     - Model Calibration Brier Score: $0.118$ (healthy).
  3. Navigates to "Clinician Verification Queue" (`/admin/clinicians/pending`).
  4. Reviews pending registration for Dr. Sarah Lin (License #A142981, California Medical Board).
  5. Verifies credentials against state registry; clicks "Approve Clinician".
  6. Backend updates `users.clinician_status = "VERIFIED"` and logs action in `audit_logs`.
  7. Navigates to "System Audit Log Explorer" (`/admin/audit`); filters by `action_type == "CLINICIAN_RECORD_ACCESSED"` to verify all doctor views correspond to valid patient grants.
- **Alternate Flow:** Admin notices a doctor registration with an invalid or expired license number; clicks "Reject" and enters explanation: *"Medical license could not be verified in state database."*
- **Error Scenarios & Recovery:**
  - *Audit log query timeout on large date ranges:* Database uses indexed query on `(timestamp, action_type)`; paginated results prevent gateway timeout.
- **Permissions:** Strictly restricted to verified `ADMIN` role.
- **Expected Final State:** Platform integrity maintained, clinician access securely vetted, and audit trail verified.
