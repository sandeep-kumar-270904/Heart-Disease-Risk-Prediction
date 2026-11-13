# HeartXAI 2.0 — Phase 2 Decisions, Open Questions & Risk Analysis

**Document ID:** HXAI-REQ-010  
**Version:** 2.0.0  
**Phase:** Phase 2 — Product Requirements & System Scope  
**Status:** Complete / Ready for Review  
**Author:** Principal Product Manager & Lead Software Architect  

---

## 1. Summary of Requirements Specified

During Phase 2, the conceptual vision of HeartXAI 2.0 was translated into an exhaustive, unambiguous, and testable engineering specification across ten formal architectural documents:
- **Functional Requirements:** Twenty (20) distinct modules covering twenty-nine (29) rigorously specified features, each documented with a 15-attribute engineering contract.
- **Non-Functional Requirements:** Fourteen (14) measurable quality categories covering usability, accessibility, responsive design, latency, reliability, security, privacy, data integrity, maintainability, scalability, observability, disaster recovery, testing, and documentation.
- **Security & Authorization:** A four-tier Role-Based Access Control matrix governing Guests, Patients, Verified Doctors, and Administrators, anchored by an explicit patient consent protocol.
- **Healthcare & ML Specification:** Scientifically precise definitions of the dual prediction targets (binary CAD presence vs 10-year prospective ASCVD risk), dataset provenance (UCI Cleveland), preprocessing, TreeSHAP mathematical invariance ($\le 10^{-5}$), and constrained counterfactual boundaries.
- **Data Entities:** Nine (9) comprehensive information entities classified under a 4-tier sensitivity taxonomy (PUB, ADM, PII, PHI) with HIPAA/GDPR retention rules.
- **User Journeys:** Eleven (11) end-to-end user journeys detailing normal, alternate, and error-recovery paths.

---

## 2. Requirement Metrics & Tallies

- **Total Functional Requirements (FRs):** **29 Features** across 20 Modules
  - *Must Have (MVP Core):* 19
  - *Should Have (Supporting Workflows):* 8
  - *Could Have (Nice-to-Have Usability):* 2
  - *Won't Have (Deferred to v3.0):* 3
- **Total Non-Functional Requirement Categories (NFRs):** **14 Categories**, comprising 24 individual measurable criteria.
- **Total User Personas / Archetypes:** **4 Personas** (Marcus, Dr. Sarah Lin, Elena Rostova, David Kim).
- **Total Core Data Information Entities:** **9 Entities** (`User`, `PatientProfile`, `Assessment`, `InferenceResult`, `ShapExplanation`, `CounterfactualProfile`, `DoctorGrant`, `ClinicalNote`, `AuditLog`).

---

## 3. Unresolved Decisions Requiring Stakeholder Alignment

### Decision 1: Clinical Model Validation vs. Screening Fallback Model
- **Context:** The benchmark Cleveland dataset contains 13 biomarkers. In real-world screening scenarios, non-clinical users frequently do not have fluoroscopy major vessel counts (`ca`) or thallium scintigraphy stress test results (`thal`) available from routine physical checkups.
- **Options:**
  - *Option A (Strict 13-Feature Requirement):* Require all 13 biomarkers; provide sample values or explain that users without specialized imaging must complete tests with a doctor before using the tool.
  - *Option B (Dual-Model Architecture):* Train a primary 13-biomarker model (AUROC $\sim 0.87$) for comprehensive clinical review, and a secondary 8-biomarker "Primary Care / Non-Invasive" model (excluding `ca`, `thal`, `slope`, `oldpeak`, AUROC $\sim 0.81$) for initial screening.
  - *Option C (Median Imputation with Uncertainty Flag):* Use a single 13-biomarker model; if specialized scan values are omitted, impute cohort median values and mark the output with an elevated uncertainty flag.
- **Trade-offs:** Option A maintains maximum clinical fidelity but introduces intake friction; Option B provides high usability and clear expectations but requires maintaining two model artifacts; Option C is simple but risks underestimating risk in high-stenosis patients.
- **Engineer's Recommendation:** **Option B (Dual-Model Architecture)** or **Option A for initial MVP release**. For MVP, adhere to Option A with clear educational helpers explaining what fluoroscopy and thallium tests measure.

---

### Decision 2: Report Generation Technology: Client-Side Print vs. Server-Side PDF Engine
- **Context:** Module 14 requires generating a 1-page clinical visit briefing document for doctor appointments.
- **Options:**
  - *Option A (Server-Side WeasyPrint / ReportLab):* Backend Python service renders a pixel-perfect PDF using HTML/CSS or ReportLab and streams a binary `.pdf` file.
  - *Option B (Client-Side Window.print CSS):* React renders a dedicated print view (`@media print`) that users can print or save as PDF via their browser's native print engine.
  - *Option C (Client-Side `jspdf` / `html2canvas`):* Client JavaScript rasterizes DOM elements into a PDF.
- **Trade-offs:** Option A produces consistent, deterministic PDFs across all operating systems but adds Python dependencies (`cffi`, `pango` for WeasyPrint); Option B requires zero dependencies and leverages standard browser print engines, but print dialog appearance varies across operating systems.
- **Engineer's Recommendation:** **Option B with structured JSON download fallback**. Client-side print CSS is extremely reliable, lightweight, and eliminates heavy native C-library dependencies on Windows and Linux containers.

---

### Decision 3: Synthetic Sandbox Dataset Storage
- **Context:** The public website sandbox (Module 1, REQ-PUB-02) lets visitors test predictions using sample patient profiles.
- **Options:**
  - *Option A:* Hardcode 5 verified synthetic reference vectors directly into frontend constants.
  - *Option B:* Store benchmark profiles in a database table (`benchmark_profiles`) queried via an API endpoint.
- **Trade-offs:** Option A operates instantly with zero database queries and zero server latency; Option B allows administrators to edit benchmark profiles dynamically.
- **Engineer's Recommendation:** **Option A**. Hardcoding verified static reference cases into frontend constants ensures zero server load and instant responsiveness for unauthenticated public visitors.

---

## 4. Scientific, Healthcare, Security & Privacy Concerns

1. **Healthcare Risk: Over-Reliance on Machine Learning Classifiers:**
   - *Concern:* An individual receiving an "Optimal / Low Risk" prediction might ignore genuine physical symptoms (e.g. exertional chest tightness) and delay seeking medical attention.
   - *Mitigation:* The system displays persistent warnings on all results pages: *"Regardless of your calculated score, if you experience sudden chest pressure, radiating arm pain, or shortness of breath, seek emergency medical care immediately."*
2. **Scientific Risk: Model Generalization Degradation:**
   - *Concern:* The UCI Cleveland dataset was collected between 1988 and 1989 on a specific demographic cohort (mean age $54.4$, $68\%$ male). Models trained exclusively on this cohort may exhibit demographic bias or reduced generalization on modern female or young patient populations.
   - *Mitigation:* We explicitly document dataset provenance, compute confidence intervals, and mandate that all outputs are presented as educational indicators rather than definitive diagnostic conclusions.
3. **Security Risk: Insecure Direct Object References (IDOR):**
   - *Concern:* An authenticated patient altering an assessment ID in a URL (e.g. `/assessments/8f3a...`) to view another patient's clinical biomarkers.
   - *Mitigation:* Backend services strictly enforce tenant boundary checks on every query: `assert assessment.patient_id == current_user.id or has_active_grant(current_user.id, assessment.patient_id)`.
4. **Privacy Risk: Accidental Data Snooping by Healthcare Staff:**
   - *Concern:* Doctors registered on the platform browsing through patient cohorts without clinical need.
   - *Mitigation:* Doctors have zero access to the general patient registry. A patient must explicitly grant a time-bounded authorization token or consultation code to unlock their chart.

---

## 5. Alignment & Conflicts with Original Project Proposal

| Original Project Proposal Concept | Identified Limitation / Conflict | HeartXAI 2.0 Architectural Resolution |
| :--- | :--- | :--- |
| Single "Heart Disease Risk Percentage" score. | Conflates acute anatomical coronary stenosis with 10-year prospective event risk. | **Resolved:** Dual-target presentation explicitly separating binary CAD presence from 10-year ASCVD risk. |
| General "Doctor Directory" with unrestricted patient assignment. | Unrestricted doctor access violates HIPAA Privacy Rule and patient sovereignty. | **Resolved:** Implemented time-bounded patient authorization grants and audit-logged record access. |
| Unconstrained Counterfactual What-If Sliders. | Naive optimization allows changing biological sex or reducing age to decrease risk. | **Resolved:** Strict immutability locks on Age, Sex, and Scan findings; modifiable biomarkers constrained by clinical life limits. |
| Generic AI-generated medical advice. | Uncalibrated LLM generation risks medical hallucination and unapproved drug recommendations. | **Resolved:** Educational guidance is curated from traceable ACC/AHA guidelines; drug prescribing is strictly out-of-scope. |

---

## 6. Recommended Next Stage

With the product requirements, non-functional criteria, RBAC matrix, user journeys, ML specifications, and data information models fully established and documented:

**Recommended Next Stage:** **Phase 3 — Database Schema & Core Infrastructure Engineering**
- Database entity modeling via SQLAlchemy 2.0 (with Alembic migrations).
- Repository architecture supporting PostgreSQL production and automated SQLite fallback for local developer agility.
- Multi-tier testing scaffolding (`pytest`, FastAPI `TestClient`).
- Security middleware and configuration management.

*We will pause here in strict compliance with the execution rules to await your review and approval before writing any infrastructure code.*
