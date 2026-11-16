# HeartXAI 2.0 — Administrator & Governance UX Specification

**Document ID:** `HX2-DES-009`  
**Version:** `2.0.0`  
**Status:** `Approved Specification`  
**Author:** Principal Product Designer & Healthcare Security Reviewer  
**Traceability:** FR-041–FR-062, NFR-001–NFR-028, ADR-001, ADR-011  

---

## 1. Overview & Administrative UX Philosophy

The Administrator and Governance experience in HeartXAI 2.0 is built for **system reliability, algorithmic transparency, audit defensibility, and security rigor**. 

Unlike consumer dashboards, this interface prioritizes:
1. **High Information Density:** Dense tabular views, monospace hashes, explicit timestamps with timezone offsets, and low-latency filtering.
2. **Safe Destructive Actions:** Two-step confirmation dialogs with explicit typed confirmations for sensitive operations (e.g., model promotion, account deactivation, data purge).
3. **Immutable Audit Defensibility:** Every administrative action is logged to an immutable append-only audit trail.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   ADMINISTRATIVE WORKFLOW WORKSPACE                    │
├────────────────────────────────────────────────────────────────────────┤
│ [1. Telemetry Dashboard] ──► System Health, Latency, Error Rates       │
│ [2. Clinician Queue]     ──► Medical Credential & Licensure Review     │
│ [3. Model Registry]      ──► Checksums, Drift Metrics, Rollback        │
│ [4. Audit Logs]          ──► Immutable Event Inspection & Filters      │
│ [5. Country Config]      ──► Global Jurisdiction & Directory Adapters  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Screen Specifications

---

### Screen 01: Admin Telemetry & Operational Dashboard (`/admin/dashboard`)

#### 1. Screen Purpose
Provides real-time visibility into application health, inference pipeline latency, active user concurrency, error rates, and database performance.

#### 2. Key UI Elements & Content Layout
- **Top System Status Strip:**
  - Overall Health Badge: `[● Operational: All Systems Healthy]`.
  - Active Environment: `Production (AWS eu-central-1)`.
  - Uptime (Last 30 Days): `99.98%`.
- **Core Telemetry KPI Cards (4 Cards):**
  1. *P95 Inference Latency:* `42ms` (Target: `<100ms`).
  2. *Daily Risk Evaluations:* `1,428 assessments` (`+12% vs 7d avg`).
  3. *Error Rate (5xx):* `0.02%` (Target: `<0.1%`).
  4. *Active Clinician Reviews:* `34 pending`.
- **Live Infrastructure Health Grid:**
  - PostgreSQL Database: Primary + Replica status, connection pool saturation (`18 / 100`).
  - Redis Cache / Rate Limiter: Memory usage (`142 MB / 1 GB`), hit ratio (`94.2%`).
  - ML Inference Worker: Celery worker queue depth (`0 jobs queued`), mean inference duration (`38ms`).
- **Real-Time Error Alert Feed:** Live stream of captured client/server anomalies with Sentry link and stack trace toggle.

#### 3. Interaction & Navigation Behavior
- Time-window selector (`1 Hour`, `24 Hours`, `7 Days`, `30 Days`) with auto-refresh toggle (`Every 30s`).
- Clicking the Clinician Reviews card routes directly to `/admin/verifications`.

#### 4. States
- **Loading State:** Shimmer skeleton cards representing metric boxes and charts.
- **Degraded State:** If any service fails health probe (e.g., Redis down), top strip turns Amber, and affected card displays warning diagnostics.

---

### Screen 02: Clinician Credential Verification Queue (`/admin/verifications`)

#### 1. Screen Purpose
Enables administrators and compliance officers to review, verify, approve, or reject healthcare professionals applying for verified clinician status on the platform.

#### 2. User Story
> *"As a compliance administrator, I want to inspect a physician's medical license number, official issuing authority, and uploaded credential documents, so that I can ensure only legally licensed practitioners receive verified status."*

#### 3. Key UI Elements & Layout
- **Verification Queue Table:**
  - Columns: *Applicant Name*, *Country*, *License / Registration Number*, *Issuing Authority (e.g., NMC India, State Board USA)*, *Submitted Date*, *Status*, *Actions*.
- **Verification Review Split-Drawer (Opens upon row click):**
  - **Left Pane (Applicant Metadata):**
    - Full Legal Name, Specialization (e.g., Interventional Cardiology).
    - Hospital / Clinic Affiliation with verified physical address.
    - Official Medical Registry Direct Verification Link (e.g., external lookup URL to NMC or State Medical Board).
  - **Right Pane (Document Viewer):**
    - High-resolution PDF/image viewer displaying uploaded medical degree certificate and government photo ID.
    - Zoom, rotate, and full-screen controls.
  - **Decision Action Bar:**
    - `[✓ Approve & Issue Verification Badge]` (Primary Sky button).
    - `[✗ Reject Application]` (Outline Danger button).
    - `[Request Additional Documentation]` (Secondary button).
- **Rejection Modal Dialog:**
  - Mandatory reason selector: *License Expired*, *Name Mismatch*, *Unaccredited Institution*, *Illegible Document*, *Fraudulent Submission*.
  - Free-text explanation field sent via email to applicant.

#### 4. States & Validation
- **Empty State:** Illustrated card with checkmark: *"All clinician applications have been reviewed. No pending verifications."*
- **Audit Requirement:** Submitting an approval or rejection requires administrative password confirmation and logs the admin ID, applicant ID, timestamp, and decision reason to the immutable audit trail.

---

### Screen 03: Model Registry & Governance (`/admin/models/registry`)

#### 1. Screen Purpose
Provides governance, traceability, and version control for all active and candidate machine learning models powering risk predictions and SHAP explainability.

#### 2. Key UI Elements & Layout
- **Active Production Model Card:**
  - Model Name: `XGBoost-Cleveland-Production`.
  - Version: `v2.4.1`.
  - Artifact SHA256 Checksum: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
  - Training Dataset: `UCI Cleveland Heart Disease Cohort (N=303) + Synthetic Validation Split`.
  - Deployed Date: `2026-10-12 14:22:00 UTC` by `admin@heartxai.org`.
  - Performance Metrics:
    - ROC-AUC: `0.892`
    - Brier Score: `0.114`
    - Precision / Recall: `0.86 / 0.88`
    - Mean SHAP Computation Time: `12ms`
- **Model Promotion & Rollback Controls:**
  - Button: `[Rollback to Previous Version (v2.3.8)]` (Requires explicit confirmation).
- **Historical Model Table:**
  - Chronological list of past deployed models with checksums, deployment dates, retire dates, and performance benchmarks.
- **Model Deployment Action (Candidate Evaluation):**
  - Ability to stage a new model version (`v2.5.0`), run shadow validation against test suites, and review side-by-side metric comparison before promoting to production.

---

### Screen 04: Algorithmic Drift & Fairness Monitoring (`/admin/models/drift`)

#### 1. Screen Purpose
Monitors statistical drift in input biomarker distributions and model prediction distributions to detect dataset shift, concept drift, or demographic bias over time.

#### 2. Key UI Elements & Layout
- **Population Drift Index (PSI) Summary:**
  - Overall Model PSI: `0.042` (`Status: Green / Negligible Drift`).
  - Threshold Reference: `<0.1` (Stable), `0.1–0.2` (Moderate Shift), `>0.2` (Significant Drift / Retraining Required).
- **Feature-Level Drift Matrix:**
  - Sortable table of all 13 clinical features.
  - Columns: *Feature Name*, *Baseline Mean*, *Recent 30d Mean*, *Kolmogorov-Smirnov (KS) Statistic*, *p-Value*, *Drift Status Pill*.
  - *Example:* Serum Cholesterol showing KS=0.081 ($p=0.14$), indicating input distribution stability.
- **Demographic Parity & Subgroup Evaluation:**
  - Performance parity comparisons across age brackets (`<45`, `45–65`, `>65`) and sex (`Female` vs `Male`).
  - False positive and false negative rate balance charts.
- **Drift Alert Configuration:**
  - Configurable alert threshold triggers that notify engineering leads via webhook if PSI exceeds $0.15$.

---

### Screen 05: Immutable Security Audit Trail (`/admin/audit-logs`)

#### 1. Screen Purpose
Enables security officers, data protection leads, and compliance auditors to inspect immutable event records for all sensitive operations, patient record queries, and administrative modifications.

#### 2. Key UI Elements & Layout
- **Comprehensive Filter Toolbar:**
  - Actor search (User ID, Email, Role).
  - Action Category dropdown (`Authentication`, `Data Access`, `Inference Execution`, `Role Change`, `Clinician Verification`, `Data Export`).
  - Date Range Picker with minute-level precision.
  - IP Address / Country origin filter.
- **Audit Event Table:**
  - Columns: *Timestamp (UTC)*, *Actor*, *Role*, *Action*, *Target Resource*, *IP Address*, *Status*, *Details (`[Inspect JSON]`)*.
- **Event Detail Modal (JSON Viewer):**
  - Displays full cryptographic hash of previous block, current event hash, request headers (sanitized), and structured payload diff.
- **Export Audit Log:**
  - Export filtered log as cryptographically signed CSV or JSON for compliance submission (HIPAA / GDPR audit requests).

---

### Screen 06: Country Configuration & Adapter Manager (`/admin/country-config`)

#### 1. Screen Purpose
Controls the multi-country operational behavior of HeartXAI 2.0 without requiring code redeployments, managing geographic toggles, directory integrations, and localized measurement defaults.

#### 2. Key UI Elements & Layout
- **Global Country List Table:**
  - Columns: *Country Name*, *ISO Code*, *Status (`Active` / `Disabled` / `Beta`)*, *Default Unit System*, *Directory Adapter*, *Emergency Hotline*, *Actions*.
- **Country Edit Drawer (e.g., India Configuration):**
  - **General Settings:**
    - Country Code: `IN` (India).
    - Status: `Active (Full Launch)`.
    - Default Biomarker Units: `mg/dL` (Blood Sugar & Cholesterol), `mmHg` (BP), `cm/kg` (Height/Weight).
    - Currency Symbol: `₹` (INR).
    - Date Display Format: `DD/MM/YYYY`.
  - **Directory Adapters:**
    - Doctor Directory Adapter: `IndiaNmcDirectoryAdapter` (External verified registry: NMC National Medical Register).
    - Hospital Directory Adapter: `IndiaNabhHospitalAdapter` (Accredited facilities).
    - Emergency Hotline Numbers: `112` (National Emergency), `102` (Ambulance), `108` (Disaster Medical Services).
  - **Regulatory Disclaimers:**
    - Specific statutory disclaimer text mandated by local healthcare authorities.
- **Adapter Connection Health Probe:**
  - One-click `[Test Adapter Connections]` button that verifies external API uptime, rate limits, and latency for the selected country.
