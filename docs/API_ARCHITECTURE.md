# HeartXAI 2.0 — RESTful API Architecture & Endpoint Contracts

**Document ID:** HXAI-ARCH-011  
**Version:** 3.0.0  
**Phase:** Phase 3 — System Architecture & Technical Design  
**Status:** Approved  
**Author:** Senior Backend Architect & API Standards Lead  

---

## 1. API Architecture Philosophy & Design Conventions

The HeartXAI 2.0 API is designed as a strict, predictable RESTful service adhering to OpenAPI 3.1 specifications:
1. **URI Versioning:** All domain routes are versioned explicitly under `/api/v1/...`.
2. **Standard HTTP Verbs:**
   - `GET`: Safe, idempotent read operations.
   - `POST`: Resource creation and non-idempotent operations.
   - `PUT` / `PATCH`: Idempotent updates.
   - `DELETE`: Resource termination or removal.
3. **Session Transport:** Authentication tokens reside in secure `HttpOnly`, `SameSite=Strict` cookies (`access_token`).
4. **Structured Error Envelopes (Stripe Model):** All error responses return a standardized, machine-readable JSON structure.
5. **Rate Limiting:** Enforced via sliding window in-memory / Redis token bucket.

---

## 2. Standardized Error Response Contract

All non-2xx HTTP responses adhere to the following schema:
```json
{
  "error": {
    "type": "validation_error",
    "code": "parameter_out_of_range",
    "param": "trestbps",
    "message": "Resting blood pressure must be between 80 and 220 mm Hg.",
    "details": [
      {
        "param": "trestbps",
        "code": "less_than_equal",
        "message": "Input should be less than or equal to 220"
      }
    ]
  }
}
```

### Standard Error Status Codes
- `400 Bad Request`: Malformed JSON or syntax failure.
- `401 Unauthorized`: Missing, expired, or cryptographically invalid session token.
- `403 Forbidden`: Authenticated user lacks required role or active patient consent grant.
- `404 Not Found`: Target entity ID does not exist.
- `409 Conflict`: Unique constraint violation (e.g. duplicate email registration).
- `422 Unprocessable Entity`: Semantic clinical validation failure.
- `429 Too Many Requests`: Rate limit threshold exceeded.
- `500 Internal Server Error`: Unhandled server exception with internal correlation `request_id`.

---

## 3. Comprehensive Endpoint Catalog by Module

### Module 1: Health & Governance Probes
- `GET /health/live`: Public liveness probe returning service metadata and UTC timestamp.
- `GET /health/ready`: Readiness probe verifying operational database connection (`SELECT 1`).

---

### Module 2: Authentication & Identity (`/api/v1/auth`)

#### `POST /api/v1/auth/register`
- **Purpose:** Create new user account with role assignment.
- **Auth:** Public.
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "full_name": "Marcus Vance",
    "role": "PATIENT",
    "license_number": null,
    "consent_agreed": true
  }
  ```
- **Response (201 Created):** Sanitized user summary (`id`, `email`, `full_name`, `role`).
- **Errors:** 409 (Email exists), 422 (Weak password / no consent).

#### `POST /api/v1/auth/login`
- **Purpose:** Authenticate user and issue secure HttpOnly JWT session cookie.
- **Auth:** Public (Rate limited: 5 attempts/min).
- **Request Body:** `{"email": "...", "password": "..."}`
- **Response (200 OK):** User profile object + `Set-Cookie: access_token=...; HttpOnly; Secure; SameSite=Strict; Path=/api`.
- **Errors:** 401 (Invalid credentials), 429 (Rate limit).

#### `POST /api/v1/auth/logout`
- **Purpose:** Invalidate session and clear authentication cookie.
- **Auth:** Authenticated.
- **Response (200 OK):** `{"message": "Successfully logged out"}` + `Set-Cookie: access_token=; Max-Age=0`.

#### `GET /api/v1/auth/me`
- **Purpose:** Return currently authenticated user profile and role claims.
- **Auth:** Authenticated.
- **Response (200 OK):** Sanitized user profile object.

---

### Module 3: Cardiovascular Assessments (`/api/v1/assessments`)

#### `POST /api/v1/assessments`
- **Purpose:** Submit 13-biomarker clinical intake, execute ML inference & TreeSHAP, and persist in an atomic transaction.
- **Auth:** Authenticated (Role: `PATIENT` or `CLINICIAN`).
- **Request Body:**
  ```json
  {
    "age": 54, "sex": 1, "cp": 2, "trestbps": 158, "chol": 248,
    "fbs": 0, "restecg": 0, "thalach": 164, "exang": 0, "oldpeak": 1.2,
    "slope": 0, "ca": 0, "thal": 1
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "assessment_id": "uuid-v4",
    "cad_probability": 0.44,
    "cad_risk_tier": "BORDERLINE",
    "confidence_interval": [0.39, 0.49],
    "ascvd_10yr_risk": 9.8,
    "ascvd_risk_tier": "BORDERLINE",
    "created_at": "2026-11-16T00:30:00Z"
  }
  ```
- **Validation:** Pydantic schema enforces 13 biomarker bounds.
- **Errors:** 422 (Range violation), 500 (ML failure).

#### `GET /api/v1/assessments/{id}`
- **Purpose:** Retrieve full clinical telemetry, inferences, and confidence intervals for an assessment.
- **Auth:** Authenticated.
- **Ownership Check:** Must be owning patient OR clinician holding an active grant.
- **Response (200 OK):** Assessment telemetry object with nested inference results.
- **Errors:** 403 (Forbidden), 404 (Not found).

#### `GET /api/v1/assessments/history`
- **Purpose:** Retrieve chronological list of assessments and biomarker deltas for longitudinal tracking.
- **Auth:** Authenticated (`PATIENT`).
- **Response (200 OK):** Chronological array of assessment objects with calculated deltas.

---

### Module 4: Explainability & Counterfactuals (`/api/v1/inference`)

#### `GET /api/v1/inference/{assessment_id}/shap`
- **Purpose:** Retrieve 13 exact local TreeSHAP attributions and plain-language summary for an assessment.
- **Auth:** Authenticated (Owner or authorized doctor).
- **Response (200 OK):**
  ```json
  {
    "inference_id": "uuid",
    "base_expected_value": -0.12,
    "attributions": [
      {
        "feature_name": "trestbps",
        "feature_value": 158.0,
        "shap_value": 0.42,
        "rank": 1,
        "direction": "RISK_INCREASING",
        "clinical_interpretation": "Resting blood pressure (158 mm Hg) increased risk significantly."
      }
    ],
    "plain_language_summary": [
      "Your elevated blood pressure (158 mmHg) was the primary risk factor."
    ]
  }
  ```

#### `POST /api/v1/inference/{assessment_id}/counterfactual/simulate`
- **Purpose:** Perform real-time what-if simulation or optimal target optimization under clinical constraints.
- **Auth:** Authenticated (Owner or authorized doctor).
- **Request Body:**
  ```json
  {
    "target_risk_threshold": 0.20,
    "overrides": { "trestbps": 125, "chol": 190 }
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "original_cad_probability": 0.44,
    "projected_cad_probability": 0.21,
    "risk_reduction_absolute": 0.23,
    "feasibility_rating": "MODERATE",
    "target_biomarkers": { "trestbps": 125, "chol": 190 },
    "locked_traits": { "age": 54, "sex": 1, "ca": 0, "thal": 1 }
  }
  ```

---

### Module 5: Patient Privacy & Consent (`/api/v1/privacy`)

#### `POST /api/v1/privacy/grants`
- **Purpose:** Grant time-bounded consultation access to a specific doctor.
- **Auth:** Authenticated (`PATIENT`).
- **Request Body:** `{"doctor_id": "uuid", "duration_days": 14}`
- **Response (201 Created):** Grant object with `expires_at` timestamp.

#### `DELETE /api/v1/privacy/grants/{grant_id}`
- **Purpose:** Immediately revoke doctor access grant.
- **Auth:** Authenticated (`PATIENT` owner of grant).
- **Response (200 OK):** `{"message": "Grant successfully revoked"}`.

#### `DELETE /api/v1/privacy/account`
- **Purpose:** Complete account deletion and cryptographic health data erasure (GDPR Right to Erasure).
- **Auth:** Authenticated (`PATIENT`, password confirmation required).
- **Response (200 OK):** Redirection to landing; all records purged.

---

### Module 6: Clinician Portal (`/api/v1/clinician`)

#### `GET /api/v1/clinician/patients`
- **Purpose:** List patient cohort who have granted active consultation access to this clinician.
- **Auth:** Authenticated (`CLINICIAN`).
- **Response (200 OK):** Paginated array of authorized patient summaries and latest risk tiers.

#### `POST /api/v1/assessments/{assessment_id}/notes`
- **Purpose:** Append signed clinical review notes to an assessment.
- **Auth:** Authenticated (`CLINICIAN` holding active grant).
- **Request Body:** `{"note_content": "...", "signoff_status": "FINAL_SIGNOFF"}`
- **Response (201 Created):** Clinical note record.

---

### Module 7: Public Directories (`/api/v1/directory`)

- `GET /api/v1/directory/doctors`: Paginated, filterable doctor directory (by specialty, location).
- `GET /api/v1/directory/hospitals`: Filterable cardiac hospital and emergency center directory.
- `GET /api/v1/directory/insurance`: Preventative cardiovascular insurance coverage guides.
- `GET /api/v1/directory/education/{biomarker_code}`: Guideline-traceable lifestyle and diet guides.

---

### Module 8: Administrator & Governance (`/api/v1/admin`)

- `GET /api/v1/admin/telemetry`: Aggregated system latency, active users, and model calibration metrics.
- `GET /api/v1/admin/clinicians/pending`: List pending clinician registrations awaiting license review.
- `POST /api/v1/admin/clinicians/{id}/verify`: Approve or reject clinician registration.
- `GET /api/v1/admin/audit/logs`: Paginated, filterable query explorer over immutable audit logs.
- `GET /api/v1/admin/models`: Inspect model registry versions, SHA-256 checksums, and validation AUROC.
