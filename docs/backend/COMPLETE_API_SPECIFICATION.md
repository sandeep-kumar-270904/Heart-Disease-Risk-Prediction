# HeartXAI 2.0 — Complete RESTful API Endpoint Specification

**Document ID:** `HX2-BE-004`  
**Version:** `1.0.0`  
**Phase:** Phase 7 — Backend Engineering Architecture & API Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal Backend Architect & API Standards Lead  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001 through ADR-011, HXAI-ARCH-011  

---

## 1. Global API Standards & Conventions

All endpoints adhere strictly to the following architectural rules:
1. **URI Versioning:** All endpoints are rooted under `/api/v1/...`.
2. **Session Transport:** Authentication tokens reside in `HttpOnly`, `SameSite=Strict` cookies. The browser automatically presents cookies; client API calls must supply the `X-CSRF-Token` header for state-changing operations.
3. **Structured Response Envelope:** Responses adhere to standard JSON payloads; error responses return the Stripe-style error model specified in `HX2-BE-010`.
4. **Idempotency & Safe HTTP Verbs:**
   - `GET`: Safe, read-only.
   - `POST`: Non-idempotent resource creation.
   - `PUT`: Idempotent full replacement.
   - `PATCH`: Partial state update.
   - `DELETE`: Resource removal or revocation.

---

## 2. Complete Endpoint Inventory by Domain

---

### Domain 1: Authentication & Session Management

#### 1.1 User Registration (`POST /api/v1/auth/register`)
- **Requirement Traceability:** `FR-001`, `FR-002`
- **Purpose:** Registers a new patient account with mandatory consent capture and password hardening.
- **Auth & Access:** Public / Guest.
- **Request Schema:** `RegisterRequest` (`email`, `password`, `full_name`, `country_code`, `consent_given: true`).
- **Response Schema:** `HTTP 201 Created` $\rightarrow$ `UserRegistrationResponse` (`id`, `email`, `message: "Verification email sent"`).
- **Validation Rules:** Email must be RFC 5322 compliant; password must be $\ge 12$ chars with uppercase, lowercase, digit, and symbol; `country_code` must be ISO-3166-1 alpha-2; `consent_given` must be strictly `true`.
- **Business Rules:** Password hashed via Argon2id (`m=65536, t=3, p=4`). Account created in `UNVERIFIED` status. Verification token dispatched via background email task.
- **Error Responses:** `400 Bad Request` (Validation error), `409 Conflict` (Email already registered).
- **Rate Limit:** 5 requests per IP per minute.
- **Audit Requirement:** Log event `AUTH_REGISTER_ATTEMPT` with IP, email hash, and timestamp.
- **Tests Required:** `test_register_success`, `test_register_duplicate_email`, `test_register_weak_password`, `test_register_without_consent`.

#### 1.2 User Login (`POST /api/v1/auth/login`)
- **Requirement Traceability:** `FR-003`, `FR-004`
- **Purpose:** Authenticates user credentials and issues secure session cookies.
- **Auth & Access:** Public / Guest.
- **Request Schema:** `LoginRequest` (`email`, `password`).
- **Response Schema:** `HTTP 200 OK` $\rightarrow$ `UserProfileResponse` (`id`, `email`, `full_name`, `role`, `country_code`).
  - Sets `Set-Cookie: access_token=...; HttpOnly; Secure; SameSite=Strict; Max-Age=900; Path=/`
  - Sets `Set-Cookie: csrf_token=...; Secure; SameSite=Strict; Path=/`
- **Business Rules:** Verifies password against Argon2id hash. Account must not be suspended (`is_active == True`). Increments login count; updates `last_login_at`.
- **Error Responses:** `401 Unauthorized` (Invalid email or password), `429 Too Many Requests` (Account locked after 5 consecutive failures).
- **Rate Limit:** 5 failed attempts per IP/account per 15 minutes.
- **Audit Requirement:** Log event `AUTH_LOGIN_SUCCESS` or `AUTH_LOGIN_FAILURE`.

#### 1.3 User Logout (`POST /api/v1/auth/logout`)
- **Requirement Traceability:** `FR-005`
- **Purpose:** Terminates active session and clears browser cookies.
- **Auth & Access:** Authenticated (`PATIENT`, `CLINICIAN`, `ADMINISTRATOR`).
- **Request Schema:** Empty body.
- **Response Schema:** `HTTP 200 OK` $\rightarrow$ `{ "status": "logged_out" }`.
  - Sets `Set-Cookie: access_token=; Max-Age=0; Path=/`
- **Audit Requirement:** Log event `AUTH_LOGOUT`.

#### 1.4 Get Current User Session (`GET /api/v1/auth/me`)
- **Requirement Traceability:** `FR-006`
- **Purpose:** Restores frontend session state upon application reload.
- **Auth & Access:** Authenticated (Any role).
- **Response Schema:** `HTTP 200 OK` $\rightarrow$ `UserProfileResponse` (`id`, `email`, `role`, `country_code`, `clinician_status`).
- **Error Responses:** `401 Unauthorized` (Token missing or expired).

#### 1.5 Silent Token Refresh (`POST /api/v1/auth/refresh`)
- **Requirement Traceability:** `FR-007`
- **Purpose:** Rotates expiring access token using HttpOnly refresh cookie.
- **Auth & Access:** Valid `refresh_token` cookie required.
- **Response Schema:** `HTTP 200 OK` $\rightarrow$ `{ "refreshed": true }` (New `access_token` cookie set).

---

### Domain 2: Patient Profile & Health Preferences

#### 2.1 Get Patient Profile (`GET /api/v1/patients/me/profile`)
- **Requirement Traceability:** `FR-010`
- **Auth & Access:** Role: `PATIENT`.
- **Response Schema:** `HTTP 200 OK` $\rightarrow$ `PatientProfileResponse` (`date_of_birth`, `biological_sex`, `preferred_units`, `emergency_contact`).

#### 2.2 Update Patient Profile & Units (`PUT /api/v1/patients/me/profile`)
- **Requirement Traceability:** `FR-011`
- **Request Schema:** `PatientProfileUpdateDto` (`preferred_units: "metric" | "us_customary"`, `emergency_contact`).
- **Response Schema:** `HTTP 200 OK` $\rightarrow$ Updated profile.

#### 2.3 Revoke Clinician Consent Grant (`DELETE /api/v1/patients/me/grants/:grantId`)
- **Requirement Traceability:** `FR-015`
- **Purpose:** Patient immediately terminates a doctor's access to their medical records.
- **Business Rules:** Verified ownership (`grant.patient_id == current_user.id`). Deactivates grant immediately.

---

### Domain 3: Clinical Assessments & Risk Prediction

#### 3.1 Submit New Assessment (`POST /api/v1/assessments`)
- **Requirement Traceability:** `FR-020`, `FR-021`, `FR-022`, `FR-023`, `FR-024`
- **Purpose:** Ingests the 13 clinical features, validates physiological limits, runs XGBoost inference, generates TreeSHAP feature attributions, and stores results transactionally.
- **Auth & Access:** Role: `PATIENT` (or `CLINICIAN` on behalf of patient with active grant).
- **Request Schema:** `AssessmentCreateDto` (13 raw clinical biomarkers: `age`, `sex`, `chest_pain_type`, `resting_bp`, `serum_cholesterol`, `fasting_blood_sugar`, `resting_ecg`, `max_heart_rate`, `exercise_angina`, `st_depression`, `st_slope`, `major_vessels`, `thallium_stress`, `unit_system`).
- **Response Schema:** `HTTP 201 Created` $\rightarrow$ `AssessmentDetailResponse`:
  - `id`: UUIDv4
  - `cadLikelihoodPercent`: `42.4`
  - `confidenceInterval`: `[38.1, 46.7]`
  - `riskStrata`: `"moderate"`
  - `tenYearPopulationRiskPercent`: `11.8`
  - `modelVersion`: `"XGBoost-Cleveland-Production-v2.4.1"`
  - `plainLanguageSummary`: String
  - `emergencyWarningActive`: Boolean
- **Validation Rules:**
  - `age`: $[18, 100]$
  - `resting_bp`: $[70, 240]\text{ mmHg}$
  - `serum_cholesterol`: $[100, 600]\text{ mg/dL}$ (or converted equivalent)
  - `st_depression`: $[0.0, 6.2]\text{ mm}$
- **Business Rules:** Units converted to canonical `mg/dL` and `mmHg`. Missing optional values (`major_vessels`, `thallium_stress`) imputed using cohort median and flagged. If acute symptoms present (Chest pain + ST depression $>2.5\text{ mm}$ + BP $>180\text{ mmHg}$), `emergencyWarningActive` is set to `True`.
- **Audit Requirement:** Log event `ASSESSMENT_SUBMITTED` with assessment ID and patient ID.
- **Tests Required:** `test_submit_assessment_success`, `test_submit_out_of_range_bp`, `test_emergency_symptom_trigger`.

#### 3.2 Get Assessment History (`GET /api/v1/assessments`)
- **Requirement Traceability:** `FR-025`
- **Auth & Access:** Role: `PATIENT` (enforces `patient_id == current_user.id`).
- **Parameters:** `?page=1&limit=10&sort_by=created_at&sort_order=desc`.
- **Response Schema:** `HTTP 200 OK` $\rightarrow$ `PaginatedResponse<AssessmentSummaryDto>`.

#### 3.3 Get Assessment Detail (`GET /api/v1/assessments/:id`)
- **Requirement Traceability:** `FR-026`
- **Auth & Access:** Patient owner OR Clinician with active unexpired consent grant.
- **Error Responses:** `403 Forbidden` (Cross-patient access attempt blocked), `404 Not Found`.

---

### Domain 4: Explainability (SHAP) & Counterfactual Scenarios

#### 4.1 Get SHAP Feature Attribution (`GET /api/v1/assessments/:id/shap`)
- **Requirement Traceability:** `FR-030`, `FR-031`
- **Purpose:** Retrieves the 13 TreeSHAP attribution values showing how each biomarker pushed the likelihood higher or lower relative to base expected value.
- **Auth & Access:** Patient owner OR authorized Clinician.
- **Response Schema:** `HTTP 200 OK` $\rightarrow$ `ShapExplanationResponse`:
  - `baseValue`: `0.380` (Cohort baseline expectation)
  - `finalPrediction`: `0.424`
  - `features`: Array of 13 objects:
    - `featureName`: `"resting_bp"`
    - `rawPatientValue`: `154.0`
    - `unit`: `"mmHg"`
    - `cohortMean`: `131.6`
    - `shapValue`: `+0.1412`
    - `direction`: `"increases_likelihood"`
    - `plainLanguageExplanation`: String
- **Audit Requirement:** Log event `EXPLAINABILITY_SHAP_ACCESSED`.

#### 4.2 Simulate Counterfactual Scenario (`POST /api/v1/assessments/:id/scenarios`)
- **Requirement Traceability:** `FR-035`, `FR-036`
- **Purpose:** Computes hypothetical "what-if" likelihood delta for user-modified physiological variables without overwriting permanent records.
- **Request Schema:** `ScenarioSimulationRequest` (`modified_features: { resting_bp: 125, serum_cholesterol: 195 }`).
- **Response Schema:** `HTTP 200 OK` $\rightarrow$ `ScenarioResultDto`:
  - `simulatedLikelihoodPercent`: `28.2`
  - `deltaPercent`: `-14.2`
  - `feasibilityScore`: `0.94` (Physiologically viable)
  - `isBiologicalClampViolated`: `false`
- **Business Rules:** Rejects modification of non-modifiable variables (Age, Biological Sex). Validates values against outpatient physiological bounds.

---

### Domain 5: Healthcare Directories & Country Guidance

#### 5.1 Search Verified Doctors (`GET /api/v1/directory/doctors`)
- **Requirement Traceability:** `FR-040`, `ADR-011`
- **Parameters:** `?country=IN&city=Bengaluru&specialty=cardiology&verified_only=true&page=1&limit=20`.
- **Response Schema:** `HTTP 200 OK` $\rightarrow$ `PaginatedResponse<DoctorProfileDto>`.
- **Business Rules:** Delegated to country integration adapter (`IndiaAdapter`, `USAAdapter`, `UKAdapter`). Returns license verification authority (e.g., NMC India, State Medical Board).

#### 5.2 Search Hospital Facilities (`GET /api/v1/directory/hospitals`)
- **Requirement Traceability:** `FR-041`, `ADR-011`
- **Parameters:** `?country=IN&city=Mumbai&cardiac_emergency_24_7=true`.
- **Response Schema:** `HTTP 200 OK` $\rightarrow$ `PaginatedResponse<HospitalFacilityDto>`.

#### 5.3 Get Insurance Guidance (`GET /api/v1/directory/insurance`)
- **Requirement Traceability:** `FR-042`, `ADR-011`
- **Parameters:** `?country=IN`.
- **Response Schema:** `HTTP 200 OK` $\rightarrow$ `InsuranceGuidanceDto` (IRDAI / PM-JAY diagnostic test coverage checklist, claim procedures, authorized helpline).

---

### Domain 6: Consultation Reports & PDF Generation

#### 6.1 Download Clinical Discussion PDF (`GET /api/v1/reports/assessments/:id/pdf`)
- **Requirement Traceability:** `FR-050`
- **Purpose:** Generates and streams a pixel-perfect, one-page printable physician discussion summary.
- **Auth & Access:** Patient owner OR authorized Clinician.
- **Response:** `HTTP 200 OK` with binary `Content-Type: application/pdf; filename="HeartXAI-Report-{id}.pdf"`.
- **Rate Limit:** 3 downloads per assessment per minute.
- **Audit Requirement:** Log event `REPORT_PDF_DOWNLOADED`.

---

### Domain 7: Administration & Model Governance

#### 7.1 Get System Telemetry Dashboard (`GET /api/v1/admin/telemetry`)
- **Requirement Traceability:** `FR-055`
- **Auth & Access:** Role: `ADMINISTRATOR`.
- **Response Schema:** `HTTP 200 OK` $\rightarrow$ `SystemTelemetryResponse` (P95 latency, daily evaluation count, error rate 5xx, database pool saturation, Celery queue depth).

#### 7.2 Get Clinician Verification Queue (`GET /api/v1/admin/verifications`)
- **Requirement Traceability:** `FR-056`
- **Auth & Access:** Role: `ADMINISTRATOR`.
- **Response Schema:** `HTTP 200 OK` $\rightarrow$ `List<ClinicianVerificationItemDto>` (Applicant name, country, license number, issuing board, uploaded diploma file path).

#### 7.3 Approve/Reject Clinician Verification (`POST /api/v1/admin/verifications/:id/decision`)
- **Requirement Traceability:** `FR-057`
- **Auth & Access:** Role: `ADMINISTRATOR`.
- **Request Schema:** `VerificationDecisionDto` (`decision: "APPROVE" | "REJECT"`, `rejection_reason?: string`).
- **Audit Requirement:** Log event `CLINICIAN_VERIFICATION_DECIDED` with admin ID, applicant ID, and outcome.

#### 7.4 Get Model Registry & Drift Metrics (`GET /api/v1/admin/models`)
- **Requirement Traceability:** `FR-060`, `FR-061`
- **Auth & Access:** Role: `ADMINISTRATOR`.
- **Response Schema:** `HTTP 200 OK` $\rightarrow$ `ModelRegistryDto` (Active version `v2.4.1`, SHA256 checksum, ROC-AUC `0.892`, PSI score `0.042`, KS statistics).
