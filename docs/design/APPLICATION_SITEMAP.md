# HeartXAI 2.0 — Application Sitemap & URL Specification

**Document ID:** `HX2-DES-007`  
**Version:** `2.0.0`  
**Status:** `Approved Specification`  
**Author:** Principal Product Designer & Frontend Architecture Lead  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011  

---

## 1. Global URL Scheme & Architectural Routing Rules

The HeartXAI 2.0 routing architecture is structured around clean, semantic RESTful path conventions. 

```
https://app.heartxai.org/{locale}/{role-domain}/{resource}/{sub-resource}?{parameters}
```

### Routing Rules
1. **Role Scoping:** Routes are strictly segregated by user role: `/public/`, `/patient/`, `/clinician/`, `/admin/`.
2. **Deterministic Identifiers:** Resource identifiers use standard UUIDv4 strings (e.g., `/assessments/8f3a9e22-1c05-4b36-9a2e-4b68ef557112`).
3. **Locale & Jurisdiction:** Global configuration defaults to browser auto-detection with explicit URL parameter override (`?country=IN&lang=en`).
4. **State Preservation:** Filter state, active tab selections, and pagination are synchronized to URL query parameters to support bookmarking and deep linking.

---

## 2. Complete Application Sitemap Table

### 2.1 Public & Authentication Routes (Access: Guest / All)

| Route Path | Screen Title | Primary Purpose | Key Interactive Actions |
| :--- | :--- | :--- | :--- |
| `/` | HeartXAI Home | Value proposition, platform mission, trust badges | "Start Assessment", "Explore Methodology", "Sign In" |
| `/about` | About HeartXAI | Institutional context, clinical governance, advisory team | Read advisory bios, review academic citations |
| `/how-it-works` | How HeartXAI Works | 3-stage visual explanation: Input $\rightarrow$ ML $\rightarrow$ Explainability | Interactive interactive demo walkthrough |
| `/methodology` | Scientific Methodology | Cleveland cohort provenance, XGBoost metrics, SHAP math | Download methodology whitepaper, inspect model specs |
| `/education` | Heart Health Library | Evidence-based cardiovascular articles and guides | Filter by topic (Blood Pressure, Lipids, ECG, Lifestyle) |
| `/education/:slug` | Article Detail | Long-form clinical literacy content with diagrams | Bookmark article, related topics, share link |
| `/safety-and-privacy`| Safety & Privacy | Non-diagnostic boundary disclaimers, GDPR, HIPAA | Review data retention policies, encryption standards |
| `/emergency` | Emergency Cardiac Help | Country-specific emergency hotline directory | Click-to-call emergency services (911 / 112 / 102) |
| `/auth/login` | Sign In | Secure authentication (Email/Password, Passkey) | "Sign In", "Remember Device", "Forgot Password" |
| `/auth/register` | Create Account | Patient onboarding, terms and consent capture | Complete registration form, verify email link |
| `/auth/verify-email` | Verify Email | One-time token verification confirmation | Enter 6-digit OTP or click confirmation link |
| `/auth/forgot-password`| Reset Password | Initiates password recovery workflow | Submit registered email address |
| `/auth/reset-password` | Set New Password | Secure password reset form with token validation | Enter and confirm compliant password |

---

### 2.2 Patient Experience Routes (Access: Authenticated `PATIENT`)

| Route Path | Screen Title | Primary Purpose | Key Interactive Actions |
| :--- | :--- | :--- | :--- |
| `/patient/dashboard` | Patient Dashboard | Executive cardiovascular health status overview | "Run New Assessment", view latest risk strata, trends |
| `/patient/assessments/new` | Assessment Wizard | Multi-step clinical data intake wizard | Progress through 6-step form, unit toggles, validate |
| `/patient/assessments` | Assessment History | Chronological historical log of past evaluations | Filter by date/risk, search, click detail, export |
| `/patient/assessments/:id` | Assessment Overview | Dual risk gauge, plain-language clinical summary | Switch views (Overview, SHAP, Scenarios), Export PDF |
| `/patient/assessments/:id/explainability`| SHAP Attribution | Interactive waterfall chart of feature impacts | Toggle visual waterfall / tabular data, inspect weights |
| `/patient/assessments/:id/scenarios`| Counterfactual Scenarios| Interactive "what-if" physiological sliders | Drag sliders, view simulated risk delta, reset |
| `/patient/trends` | Health Trends | Longitudinal charts tracking BP, Lipids, and Risk | Select date ranges (3M, 6M, 1Y, All), filter metrics |
| `/patient/directory/doctors` | Doctor Directory | Country-specific verified cardiologist search | Search by city/specialty, view credentials, copy contact |
| `/patient/directory/hospitals` | Hospital Directory | Country-specific cardiac care facility search | Filter by 24/7 emergency, catheterization lab, view map |
| `/patient/insurance` | Insurance Guidance | Country-specific coverage, claims, and policies | Browse approved insurers, download claim guide |
| `/patient/reports/export` | Clinical Summary Export| Generates PDF report for physician consultation | Select date range, customize sections, "Download PDF" |
| `/patient/settings/profile` | Health Profile | Manage demographic baselines and family history | Update baseline data, toggle privacy preferences |
| `/patient/settings/units` | Units & Formatting | Configure default units ($\text{mg/dL} \leftrightarrow \text{mmol/L}$) | Toggle metric/US customary, preview conversions |
| `/patient/settings/privacy` | Privacy & Consent | View audit logs, revoke consent, export raw data | "Download My Data", "Delete My Account", review log |

---

### 2.3 Clinician Experience Routes (Access: Authenticated `CLINICIAN`)

| Route Path | Screen Title | Primary Purpose | Key Interactive Actions |
| :--- | :--- | :--- | :--- |
| `/clinician/dashboard` | Clinical Dashboard | Assigned patient panel, pending consultations | Search patient list, view high-risk flags, filter |
| `/clinician/patients` | Patient Cohort | Filterable registry of connected patient records | Sort by risk score, last assessment date, name |
| `/clinician/patients/:id`| Patient Clinical Chart | Complete longitudinal biomarker & assessment record | Review timeline, inspect lab trends, launch audit |
| `/clinician/patients/:id/assessments/:assessId` | Assessment Audit | Raw feature vectors, mathematical SHAP telemetry | Inspect model hash, verify input bounds, add note |
| `/clinician/notes/new` | Clinical Annotation | Add professional review note to patient record | Draft structured observation, sign note, share copy |
| `/clinician/profile` | Directory Profile | Public listing credentials, clinic hours, phone | Update practice details, upload license renewal |

---

### 2.4 Administrator Experience Routes (Access: Authenticated `ADMINISTRATOR`)

| Route Path | Screen Title | Primary Purpose | Key Interactive Actions |
| :--- | :--- | :--- | :--- |
| `/admin/dashboard` | Admin Command Center | System telemetry, API latency, inference volume | Monitor error spikes, database health, worker queues |
| `/admin/users` | User Governance | User account list, role elevation, suspension | Search user by email, change role, deactivate account |
| `/admin/verifications` | Clinician Queue | Review submitted medical credentials & licenses | Approve verification badge, reject with reason |
| `/admin/models/registry` | Model Registry | Active & staging ML model versions & checksums | Promote candidate model to production, rollback |
| `/admin/models/drift` | Drift Monitoring | Population feature drift, PSI, KS-test graphs | Set drift alert thresholds, view cohort distributions |
| `/admin/audit-logs` | Security Audit Trail | Immutable audit trail of all data queries & predictions | Filter by actor, action type, IP address, timestamp |
| `/admin/country-config` | Country Configuration | Country adapter toggles, provider registries | Enable/disable country, test external API endpoints |

---

### 2.5 System & Error Routes (Access: All)

| Route Path | Screen Title | Primary Purpose | Recovery Action |
| :--- | :--- | :--- | :--- |
| `/404` | Page Not Found | Resource or route does not exist | "Return to Dashboard", "Visit Help Center" |
| `/403` | Access Restricted | Insufficient permissions for requested route | "Switch Account", "Return to Home" |
| `/500` | Application Error | Unexpected server or client-side runtime fault | "Reload Page", "Contact Support", error report ID |
| `/offline` | Offline Mode | Network connection lost (PWA cached view) | Cached dashboard telemetry view, "Retry Connection" |
| `/maintenance` | Scheduled Maintenance| System undergoing database migration or update | Scheduled downtime window banner, status page link |

---

## 3. Query Parameter Specifications

### 3.1 Patient Assessment History (`/patient/assessments`)
- `?page=1`: Current page number (integer, default `1`).
- `?limit=10`: Items per page (integer: `10`, `25`, `50`, default `10`).
- `?risk_stratum=elevated`: Filter by stratum (`all`, `low`, `moderate`, `elevated`).
- `?sort_by=created_at`: Sort key (`created_at`, `risk_score`).
- `?sort_order=desc`: Sort direction (`asc`, `desc`, default `desc`).
- `?from_date=2026-01-01&to_date=2026-11-15`: ISO-8601 date range filters.

### 3.2 Provider Directory (`/patient/directory/doctors`)
- `?country=IN`: Active country code (ISO-3166-1 alpha-2, default user's profile country).
- `?city=Bangalore`: City or metropolitan area filter string.
- `?specialty=interventional_cardiology`: Medical sub-specialty filter.
- `?verified_only=true`: Restrict to clinicians with verified professional badge (boolean).
- `?q=Sharma`: Full-text doctor name or clinic search string.
