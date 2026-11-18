# HeartXAI 2.0 — Backend Security & OWASP API Security Top 10 Mitigation

**Document ID:** `HX2-BE-013`  
**Version:** `1.0.0`  
**Phase:** Phase 7 — Backend Engineering Architecture & API Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Application Security Architect & Principal Backend Engineer  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-005, HXAI-ARCH-012  

---

## 1. Security Architecture Overview

HeartXAI 2.0 adopts the **OWASP API Security Top 10 (2023 Edition)** framework as its primary security baseline. 

Every identified risk is paired with an architectural mitigation and a dedicated, automated security test:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   OWASP API SECURITY DEFENSE RADAR                     │
├────────────────────────────────────────────────────────────────────────┤
│ API1:2023 ── Broken Object-Level Authorization (BOLA)                  │
│ API2:2023 ── Broken Authentication                                     │
│ API3:2023 ── Broken Object Property-Level Authorization                │
│ API4:2023 ── Unrestricted Resource Consumption                         │
│ API5:2023 ── Broken Function-Level Authorization (BFLA)                │
│ API6:2023 ── Unrestricted Access to Sensitive Business Flows           │
│ API7:2023 ── Server-Side Request Forgery (SSRF)                        │
│ API8:2023 ── Security Misconfiguration                                 │
│ API9:2023 ── Improper Inventory Management                             │
│ API10:2023 ─ Unsafe Consumption of APIs                                │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. OWASP API Security Top 10 Threat Mitigation Matrix

### API1:2023 — Broken Object-Level Authorization (BOLA / IDOR)
- **Attack Scenario:** Attacker logs in as Patient A, intercepts assessment request, changes URL to `/api/v1/assessments/{Patient_B_UUID}`, and views Patient B's cardiovascular telemetry and SHAP vectors.
- **Affected Module:** `app/api/v1/routes/assessments.py`, `app/services/assessment_service.py`.
- **Mitigation:** Strict server-enforced ownership checks. The repository query joins against `patient_id == current_user.id` for patients, and validates the `patient_doctor_grants` table for clinicians. Unauthorized queries return `404 Not Found` (preventing ID enumeration).
- **Verification Test:** `tests/security/test_bola.py::test_patient_cannot_read_other_patient_assessment`.

---

### API2:2023 — Broken Authentication
- **Attack Scenario:** Attacker conducts dictionary attacks or brute-force credential stuffing against user accounts, or exploits weak password hashing algorithms (e.g., standard MD5/SHA256).
- **Affected Module:** `app/api/v1/routes/auth.py`, `app/core/security.py`.
- **Mitigation:**
  - Password hashing via Argon2id (`time_cost=3, memory_cost=65536, parallelism=4`).
  - Sliding-window rate limiter: 5 attempts per account/IP per 15 minutes; account locks automatically on the 5th failure.
  - Generic error messages (*"Invalid email or password"*) prevent email enumeration.
- **Verification Test:** `tests/security/test_auth_security.py::test_account_lockout_after_five_failed_attempts`.

---

### API3:2023 — Broken Object Property-Level Authorization (Mass Assignment)
- **Attack Scenario:** Attacker submits `POST /api/v1/patients/me/profile` with `{ "role": "ADMINISTRATOR", "is_verified": true }` to elevate privileges.
- **Affected Module:** `app/schemas/patients.py`, `app/models/user.py`.
- **Mitigation:** Pydantic v2 schemas strictly enforce `extra = "forbid"`. DTOs expose only safe, user-editable fields (`preferred_units`, `emergency_contact`). Role attributes are strictly managed by administrative database migrations and guarded endpoints.
- **Verification Test:** `tests/security/test_mass_assignment.py::test_profile_update_ignores_role_injection`.

---

### API4:2023 — Unrestricted Resource Consumption (DoS / Resource Exhaustion)
- **Attack Scenario:** Attacker floods the `/api/v1/assessments` endpoint with 10,000 concurrent requests, exhausting database connections and overwhelming CPU threads with XGBoost / TreeSHAP computations.
- **Affected Module:** `app/middleware/rate_limiter.py`, `app/core/database.py`.
- **Mitigation:**
  - Sliding-window rate limiting enforced per user IP (e.g., 20 assessment creations per hour per patient).
  - Maximum JSON payload size capped at $64\text{ KB}$ (`Content-Length` validation).
  - Asynchronous connection pool capped at 20 persistent, 10 overflow connections.
  - Strict $500\text{ms}$ execution timeout on TreeSHAP calculations.
- **Verification Test:** `tests/security/test_rate_limiting.py::test_assessment_submission_rate_limit`.

---

### API5:2023 — Broken Function-Level Authorization (BFLA)
- **Attack Scenario:** A regular patient sends `GET /api/v1/admin/telemetry` or `POST /api/v1/admin/verifications/{id}/decision` hoping the API fails to verify their role scope.
- **Affected Module:** `app/api/v1/routes/admin.py`, `app/api/deps.py`.
- **Mitigation:** Declarative role dependency injection:
  ```python
  def require_role(allowed_roles: list[str]):
      async def role_checker(current_user: User = Depends(get_current_user)):
          if current_user.role not in allowed_roles:
              raise AuthorizationException("Access forbidden: insufficient role scope.")
          return current_user
      return role_checker
  ```
- **Verification Test:** `tests/security/test_bfla.py::test_regular_user_cannot_access_admin_routes`.

---

### API6:2023 — Unrestricted Access to Sensitive Business Flows
- **Attack Scenario:** An automated bot creates 5,000 dummy accounts to flood the assessment queue or scrape doctor directory records.
- **Affected Module:** `app/api/v1/routes/auth.py`, `app/api/v1/routes/directory.py`.
- **Mitigation:** Registration endpoints enforce rate limiting (5 per IP per minute) and require explicit mandatory terms acknowledgment. Directory endpoints enforce pagination clamps (`limit <= 50`).
- **Verification Test:** `tests/security/test_business_flows.py::test_registration_spam_blocked`.

---

### API7:2023 — Server-Side Request Forgery (SSRF)
- **Attack Scenario:** Attacker manipulates a doctor directory search URL to target internal cloud metadata endpoints (`http://169.254.169.254/latest/meta-data/`).
- **Affected Module:** `app/integrations/`.
- **Mitigation:**
  - Directory services do not accept arbitrary external URLs from client inputs.
  - External endpoints are hardcoded inside versioned country adapters (e.g., `https://npiregistry.cms.hhs.gov/api/`).
  - Outgoing HTTP calls via `httpx` run with strict timeouts ($5\text{s}$) and disallow redirection (`follow_redirects=False`).
- **Verification Test:** `tests/security/test_ssrf.py::test_adapter_rejects_arbitrary_urls`.

---

### API8:2023 — Security Misconfiguration
- **Attack Scenario:** Application reveals debug stack traces, runs in development mode in production, or permits wildcard `Access-Control-Allow-Origin: *`.
- **Affected Module:** `app/main.py`, `app/middleware/security_headers.py`.
- **Mitigation:**
  - Debug mode disabled in production (`debug = False`).
  - CORS strictly configured to allow only trusted frontend domains (`https://app.heartxai.org`).
  - Security headers middleware injects:
    - `X-Frame-Options: DENY`
    - `X-Content-Type-Options: nosniff`
    - `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`
    - `Content-Security-Policy: default-src 'none'; frame-ancestors 'none';`
- **Verification Test:** `tests/security/test_security_headers.py::test_security_headers_present`.

---

### API9:2023 — Improper Inventory Management
- **Attack Scenario:** Deprecated v0/beta endpoints remain active and unpatched, allowing attackers to bypass newer validation checks.
- **Affected Module:** `app/api/v1/api.py`.
- **Mitigation:** Strict semantic URI versioning (`/api/v1/...`). Unversioned or legacy routes are rejected at the ASGI router level.
- **Verification Test:** `tests/security/test_api_inventory.py::test_unversioned_routes_return_404`.

---

### API10:2023 — Unsafe Consumption of APIs
- **Attack Scenario:** Malicious or compromised external country registry returns a malformed or poisoned payload designed to cause an unhandled exception or SQL injection.
- **Affected Module:** `app/integrations/`.
- **Mitigation:** All data returned from external country APIs is strictly validated against internal Pydantic schemas (`DoctorProfileDto`, `HospitalFacilityDto`) before being consumed by the domain service.
- **Verification Test:** `tests/security/test_external_api_consumption.py::test_malformed_external_payload_handled_safely`.
