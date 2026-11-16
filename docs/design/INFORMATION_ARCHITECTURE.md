# HeartXAI 2.0 — Information Architecture Specification

**Document ID:** `HX2-DES-006`  
**Version:** `2.0.0`  
**Status:** `Approved Specification`  
**Author:** Principal UX Researcher & Information Architect  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011  

---

## 1. Information Architecture Philosophy

HeartXAI 2.0 serves diverse user archetypes: anxious patients seeking clear risk awareness, visiting cardiologists reviewing clinical telemetry, and system administrators auditing algorithmic drift and data access logs. 

The Information Architecture (IA) enforces **strict role-based segmentation**, **progressive disclosure of medical complexity**, and **zero dead ends**.

```
                           [ HEARTXAI 2.0 PLATFORM ]
                                      │
         ┌───────────────────┬────────┴───────────┬───────────────────┐
         ▼                   ▼                    ▼                   ▼
  [ Public Portal ]  [ Patient Portal ]  [ Clinician Portal ]  [ Admin Portal ]
  • Awareness        • Assessment        • Patient Review      • Model Registry
  • Methodology      • Explainability    • Telemetry Audit     • Clinician Queue
  • Education        • Directory Search  • Clinical Notes      • Country Config
  • Authentication   • Trend Tracking    • Verification Badges • Audit Trails
```

---

## 2. Global Navigation Hierarchy by Role

### 2.1 Public Experience (Unauthenticated & Guests)
Designed to establish scientific credibility, provide baseline cardiovascular education, explain platform boundaries, and onboard users.

```
/ (Root)
│
├── /about                    ── Mission, clinical advisors, institutional disclosures
├── /how-it-works             ── 3-step walkthrough: Intake → ML Inference → SHAP Explanation
├── /methodology              ── Algorithmic provenance (Cleveland cohort, XGBoost, SHAP, limitations)
├── /education                ── Cardiovascular library: CAD pathophysiology, risk factors, ECG basics
├── /safety-and-privacy       ── Non-diagnostic boundary disclosure, GDPR/HIPAA compliance, encryption
├── /auth/login               ── Multi-factor authentication (Email/Password, Passkey)
├── /auth/register            ── Patient registration, terms & consent acknowledgment
├── /auth/forgot-password     ── Secure password recovery
└── /emergency                ── Global & country-specific emergency cardiac hotline directory
```

---

### 2.2 Patient Experience (Authenticated Registered Users)
Optimized for intuitive self-assessment, transparent explanation, longitudinal trend tracking, and verified local healthcare navigation.

```
/patient
│
├── /dashboard                 ── Executive summary: Latest risk stratum, key alerts, quick action CTA
│
├── /assessments
│   ├── /new                   ── Multi-Step Assessment Wizard:
│   │   ├── step-1-demographics  (Age, Sex, Chest Pain Type)
│   │   ├── step-2-vitals        (Resting BP, Max Heart Rate, Exercise Angina)
│   │   ├── step-3-laboratory    (Serum Cholesterol, Fasting Blood Sugar)
│   │   ├── step-4-electrocardio (Resting ECG, ST Depression, ST Slope)
│   │   ├── step-5-fluoroscopy   (Major Vessels Fluoroscopy, Thallium Stress)
│   │   └── step-6-review        (Input validation, unit verification, execution confirmation)
│   ├── /                      ── Chronological Assessment History (Sortable table + cards)
│   └── /:id                   ── Assessment Result Detail View:
│       ├── /overview          ── Dual Risk Gauge, plain-language summary, key factors
│       ├── /explainability    ── Interactive SHAP Waterfall, feature impact ranking
│       └── /scenarios         ── Counterfactual "What-If" Explorer (Sliders + delta predictions)
│
├── /trends                    ── Longitudinal Health Trajectory (BP, Cholesterol, Risk probability over time)
├── /directory
│   ├── /doctors               ── Country-Specific Verified Cardiologist Search (Filters: specialty, city)
│   └── /hospitals             ── Country-Specific Emergency & Cardiac Center Search (Facilities, maps)
├── /insurance                 ── Country-Specific Health Insurance Guidance (Coverage, claims checklist)
├── /reports
│   └── /export                ── Clinical Summary PDF Export (One-page physician discussion aid)
└── /settings
    ├── /profile               ── Personal demographics and baseline medical history
    ├── /units                 ── Preferred measurement units (mg/dL vs mmol/L, cm/kg vs in/lbs)
    ├── /localization          ── Preferred language, country, currency, date formatting
    └── /privacy-consent       ── Consent revocation, audit access history, account deletion
```

---

### 2.3 Clinician Experience (Verified Healthcare Professionals)
Optimized for rapid clinical chart review, cohort verification, and diagnostic context alignment.

```
/clinician
│
├── /dashboard                 ── Assigned patient panel, pending review requests, high-risk flags
├── /patients
│   ├── /                      ── Filterable patient cohort directory (Sort by risk, date, status)
│   └── /:patientId            ── Patient Longitudinal Clinical Record:
│       ├── /summary           ── Consolidated biomarker timeline & risk history
│       ├── /assessments/:id   ── Raw feature vectors, tabular SHAP values, model version metadata
│       └── /notes             ── Clinical annotation and consultation summary entry
├── /directory-profile         ── Clinician public directory listing, credentials, clinic hours
└── /settings                  ── Professional verification documents, license renewal dates
```

---

### 2.4 Administrator Experience (System Governance & Compliance)
Focused on data integrity, algorithmic governance, security monitoring, and geographic management.

```
/admin
│
├── /dashboard                 ── System health, active user sessions, API throughput, error rates
├── /users                     ── User management, role elevation, account suspension
├── /verifications             ── Clinician credential verification queue (Medical license review)
├── /models
│   ├── /registry              ── Active & historical model registry (XGBoost, Cleveland v2.4)
│   ├── /drift-monitoring      ── Population feature drift, KS-statistic, accuracy tracking
│   └── /audit-logs            ── Immutable inference log trail (hash, model ID, timestamp)
├── /country-configuration     ── Global jurisdiction toggle: active countries, directory adapters, currencies
└── /system-logs               ── Security events, authentication failures, rate-limit triggers
```

---

## 3. Navigation Structures & Information Flow Patterns

### 3.1 Primary Navigation Patterns
1. **Desktop Main Navigation:** Fixed left sidebar (`240px` expanded, `64px` icon-only collapsed) for deep portal navigation; sticky top header (`64px` height) for global actions (Country Selector, Role Indicator, User Profile Menu).
2. **Mobile Navigation:** Off-canvas slide-out drawer (left) containing full hierarchical sitemap, paired with a persistent bottom quick-action bar for top 4 destinations (Dashboard, New Assessment, Trends, Directory).
3. **Contextual Breadcrumbs:** Explicit breadcrumb trails on all sub-pages (e.g., `Dashboard / Assessments / Assessment #1042 / Explainability`) ensuring users never lose navigational context.

---

## 4. Content Taxonomy & Medical Labeling Standards

To preserve scientific credibility, terminology across all routes is strictly governed by our clinical taxonomy:

| Conceptual Domain | Approved UI Label | Prohibited Ambiguous Label | Clinical Justification |
| :--- | :--- | :--- | :--- |
| **Model Output** | *Angiographic CAD Association Likelihood* | "Heart Attack Risk", "Diagnosis" | Avoids misleading patients into believing the model diagnoses acute myocardial infarction. |
| **Model Factors** | *Feature Contribution (SHAP Attribution)* | "Root Cause", "Definitive Proof" | Accurately describes mathematical weighting without implying biological causation. |
| **Scenario Modeling** | *Hypothetical Counterfactual Scenario* | "Treatment Plan", "Prescription" | Clarifies that simulated reductions in BP or cholesterol are computational experiments. |
| **Laboratory Vitals** | *Clinical Biomarkers & Vitals* | "Body Scores", "Health Numbers" | Maintains professional medical grounding. |
| **Directory Search** | *Verified Healthcare Provider Directory* | "Recommended Doctors" | Clarifies that providers are verified for licensure, not commercially endorsed. |

---

## 5. Cognitive Chunking & Progressive Disclosure Rules

### Rule 1: The Three-Second Rule (Executive Summary)
Upon landing on any assessment result, the patient must grasp their overall status within 3 seconds:
- **Level 1 (Top Hero):** Visual Risk Strata Gauge + Plain-Language Categorical Summary + Emergency Warning (if applicable).

### Rule 2: The Thirty-Second Rule (Primary Drivers)
Below the hero, the interface reveals the primary drivers of the score:
- **Level 2 (Middle Section):** Top 3 contributing clinical factors (SHAP positive/negative summary) + Plain-language educational explanation.

### Rule 3: The Three-Minute Rule (Deep Telemetry)
For patients reviewing with their physician or clinicians conducting an in-depth audit:
- **Level 3 (Interactive Deep-Dive):** Full interactive SHAP waterfall chart, counterfactual scenario sliders, raw laboratory input vectors, and downloadable clinical summary report.
