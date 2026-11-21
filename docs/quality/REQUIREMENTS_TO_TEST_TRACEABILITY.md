# REQUIREMENTS-TO-TEST TRACEABILITY MATRIX SPECIFICATION

**Document Reference:** `docs/quality/REQUIREMENTS_TO_TEST_TRACEABILITY.md`  
**Phase:** 11 — Comprehensive Testing Strategy, Quality Assurance & Validation Framework  
**Status:** Approved Technical Architecture  
**Author:** Principal QA Architect & Traceability Governance Lead  
**Traceability:** All Functional & Non-Functional Requirements (Phases 02 through 10)  

---

## 1. Executive Summary & Traceability Governance

Bidirectional traceability ensures that every approved functional requirement (FR) and non-functional requirement (NFR) is verified by at least one dedicated, automated test case, and that no orphaned test exists without a justified product requirement.

### Change Impact Management Protocol:
When a functional requirement is updated, deprecated, or introduced:
1. **Requirements Ledger Update:** The change is recorded in `docs/requirements/` with a revised version and rationale.
2. **Impact Analysis Hook:** The QA Architect executes an automated traceability script (`scripts/audit_traceability.py`) that identifies all mapped `TC-*` test IDs.
3. **Test Synchronization:** Associated test specifications and test code are flagged with status `NEEDS_REVISION` in the CI/CD test dashboard. The release gate blocks production promotion until the modified tests are updated and re-verified.

---

## 2. Master Requirements-to-Test Traceability Matrix (RTM)

The matrix below maps the platform's core functional and non-functional requirements to concrete test specifications:

| Requirement ID | Requirement Description | Test Case ID | Test Category | Priority | Test Scenario & Verification Target | Preconditions | Test Input Data | Expected Result | Execution Status |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: |
| **FR-AUTH-01** | User registration with password complexity | `TC-AUTH-001` | Integration / Unit | **P0** | Register account with valid complex password; assert Argon2id hash creation. | Fresh DB state | Valid email, password `P@ssw0rd2026!` | HTTP 201 Created; Argon2id hash stored | `PLANNED` |
| **FR-AUTH-02** | Secure login & hybrid token delivery | `TC-AUTH-002` | API / Security | **P0** | Authenticate user; verify in-memory access JWT + HttpOnly refresh cookie. | User exists | Valid credentials | HTTP 200; `access_token` in body, `Set-Cookie` HttpOnly | `PLANNED` |
| **FR-AUTH-03** | Brute force lockout defense | `TC-AUTH-003` | Security | **P0** | Execute 6 consecutive failed logins within 5 minutes. | User exists | Wrong password $\times 6$ | 6th attempt returns HTTP 429 Too Many Requests | `PLANNED` |
| **FR-AUTH-04** | Account enumeration prevention | `TC-AUTH-004` | Security | **P1** | Compare response message and execution timing for existent vs non-existent emails. | Platform running | Valid email vs non-existent email | Identical error phrasing; timing delta $\le 50\text{ ms}$ | `PLANNED` |
| **FR-AUTH-05** | Refresh token rotation & replay detection | `TC-AUTH-005` | Security / Auth | **P0** | Replay an already consumed refresh token; verify token family revocation. | Active session | Consumed refresh cookie | HTTP 401; entire token family revoked in Redis | `PLANNED` |
| **FR-PRED-01** | 13 Clinical biomarker input validation | `TC-PRED-001` | API / Validation | **P0** | Submit assessment with valid physiological parameters; verify forward pass. | Authenticated | 13 valid features ($BP=130, Chol=220$, etc.) | HTTP 201 Created; valid prediction object returned | `PLANNED` |
| **FR-PRED-02** | Rejection of out-of-range biomarkers | `TC-PRED-002` | Unit / Validation| **P0** | Submit assessment with blood pressure $= 350\text{ mmHg}$ or negative age. | Authenticated | $BP=350, Age=-10$ | HTTP 422 Unprocessable Entity; explicit field errors | `PLANNED` |
| **FR-PRED-03** | Calibrated probability output | `TC-PRED-003` | ML Validation | **P0** | Verify that prediction output contains calibrated probability in $[0.0, 1.0]$. | ML Engine ready | Valid patient vector | Calibrated probability returned; matches Platt formula | `PLANNED` |
| **FR-PRED-04** | TreeSHAP feature attribution | `TC-PRED-004` | ML / Explainability| **P0** | Verify TreeSHAP local accuracy (sum of attributions + base = model margin). | Model warmed up | Valid patient vector | Local accuracy satisfied within $\pm 10^{-5}$ | `PLANNED` |
| **FR-PRED-05** | Bounded feasible counterfactuals | `TC-PRED-005` | ML / Safety | **P0** | Generate counterfactual; verify age/sex immutable and BP $\ge 90\text{ mmHg}$. | High-risk patient | Initial $P > 0.50$ | Target $P < 0.50$; $\Delta Age=0, \Delta Sex=0$; $BP^* \ge 90$ | `PLANNED` |
| **FR-PRED-06** | Historical prediction listing | `TC-PRED-006` | Integration | **P1** | Patient retrieves historical assessments; assert pagination and ordering. | 3 past predictions | `GET /api/v1/predictions` | HTTP 200; 3 records returned in reverse chronological order | `PLANNED` |
| **FR-USER-01** | Anti-IDOR patient record isolation | `TC-AUTHZ-001` | Security / Authz | **P0** | Patient A queries Patient B's prediction record by ID. | 2 patient accounts| Patient B prediction ID | HTTP 404 Not Found; zero data leaked | `PLANNED` |
| **FR-USER-02** | Admin segregation of duties | `TC-AUTHZ-002` | Security / Authz | **P0** | Admin user attempts to read patient clinical prediction record. | Admin token | Patient prediction ID | HTTP 403 Forbidden; access denied | `PLANNED` |
| **FR-USER-03** | Self-service account deletion (RTBF) | `TC-PRIV-001` | Privacy / DB | **P0** | Patient requests account erasure; verify cascade deletion in DB and S3. | Active account | Valid password + MFA | HTTP 204; user and predictions purged; audit anonymized | `PLANNED` |
| **FR-USER-04** | Data Subject Access Request (DSAR) export | `TC-PRIV-002` | Privacy / API | **P1** | Patient requests full data export; verify machine-readable JSON archive. | Active account | `POST /privacy/export` | HTTP 200; ZIP containing JSON profile and predictions | `PLANNED` |
| **FR-DIR-01** | Country directory discovery | `TC-DIR-001` | Integration / Unit | **P2** | Query hospital/doctor directory with country code; assert localized results. | Country configured| `country=IN`, `city=Mumbai`| HTTP 200; list of verified healthcare facilities | `PLANNED` |
| **FR-REP-01** | Clinical PDF report generation | `TC-REP-001` | Integration | **P1** | Generate assessment summary PDF; verify presigned download URL. | Valid prediction | `GET /reports/{id}/download`| HTTP 200; valid presigned S3 URL expiring in 10 min | `PLANNED` |
| **NFR-PERF-01** | API response latency budget | `TC-PERF-001` | Performance | **P1** | Measure response latency for `/predictions` under 50 concurrent users. | Staging host | 50 concurrent Locust users | $P95 < 200\text{ ms}$; zero timeouts or dropped requests | `PLANNED` |
| **NFR-REL-01** | System availability & health probes | `TC-REL-001` | Reliability | **P0** | Verify `/health/live` and `/health/ready` probe semantics. | All services up | `GET /health/ready` | HTTP 200 `{"status": "ready"}` in $< 5\text{ ms}$ | `PLANNED` |
| **NFR-SEC-01** | Strict TLS 1.3 transport security | `TC-SEC-001` | Security / Network | **P0** | Attempt handshake using TLS 1.0/1.1; verify immediate socket termination. | Nginx active | TLS 1.0 client hello | Connection rejected; only TLS 1.3/1.2 AEAD permitted | `PLANNED` |
| **NFR-SEC-03** | Model artifact HMAC verification | `TC-SEC-002` | Security / ML | **P0** | Corrupt 1 byte in model JSON; attempt engine startup. | Tampered artifact | Modified file stream | Engine aborts with `ModelIntegrityException` | `PLANNED` |
| **NFR-PRIV-01** | PII redaction in application logs | `TC-LOG-001` | Security / Log | **P0** | Submit prediction and inspect emitted JSONL log lines for sensitive vitals. | Logging active | Password, BP, Chol | Emitted log shows `[REDACTED]` and `[MASKED_PHI]` | `PLANNED` |
| **NFR-LEGAL-01**| Non-diagnostic CDS disclaimers | `TC-SAFE-001` | Safety / UI | **P0** | Assert mandatory CDS regulatory disclaimer is rendered on prediction UI. | Result rendered | UI inspection | Disclaimer visible; no diagnostic claims present | `PLANNED` |
| **NFR-ACC-01** | WCAG 2.2 Level AA accessibility | `TC-ACC-001` | Accessibility | **P2** | Run automated axe-core scanner across all patient portal pages. | Staging frontend | Patient portal routes | Zero automated accessibility violations | `PLANNED` |

---

## 3. Execution Status Taxonomy
- `PLANNED`: Test scenario formally specified; ready for automated implementation.
- `IMPLEMENTED`: Test script authored in test repository.
- `PASSED`: Test executed in CI/CD pipeline and passed 100% of assertions.
- `FAILED`: Test executed and failed; release blocker logged.
- `BLOCKED`: Test execution impeded by external dependency or environment defect.
