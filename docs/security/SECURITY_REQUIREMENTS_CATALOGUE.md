# SECURITY REQUIREMENTS CATALOGUE AND RISK CLASSIFICATION

**Document Reference:** `docs/security/SECURITY_REQUIREMENTS_CATALOGUE.md`  
**Phase:** 09 — Security, Privacy, Data Protection & Threat Modelling  
**Status:** Approved Technical Requirements  
**Author:** Application Security Lead & Compliance Risk Analyst  
**Traceability:** FR-AUTH-*, FR-PRED-*, FR-USER-*, NFR-SEC-01 through NFR-SEC-09  

---

## 1. Executive Summary

This catalogue details the comprehensive, verifiable security requirements governing HeartXAI 2.0 across 14 operational security domains. Every requirement is assigned a unique identifier, an architectural implementation specification, and a risk classification assessing likelihood, impact, severity, and mitigation priority.

> [!WARNING]
> **Regulatory Disclaimer:**  
> HeartXAI 2.0 does not claim official certification under SOC 2 Type II, ISO/IEC 27001, HIPAA, or EU GDPR. This document establishes technical engineering specifications designed to satisfy healthcare industry security baselines and facilitate future independent third-party audits.

---

## 2. Risk Classification Framework

Risks are categorized using a standard healthcare application security risk matrix:
- **Likelihood:** Low (1), Medium (2), High (3)
- **Impact:** Low (1), Medium (2), High (3), Critical (4)
- **Severity Score:** Calculated as $\text{Likelihood} \times \text{Impact}$:
  - **Critical (10–12):** Immediate system compromise, mass PHI breach, or algorithmic safety breach. Must be resolved before any deployment.
  - **High (7–9):** Substantial patient data exposure, unauthorized account takeover, or severe service degradation. Release blocker.
  - **Medium (4–6):** Limited information leakage, non-critical Denial of Service, or circumvention of non-safety controls. Sprint blocker.
  - **Low (1–3):** Minor operational anomaly or reconnaissance potential with negligible direct harm. Backlog remediation.
- **Mitigation Priority:** P0 (Immediate / Pre-release), P1 (High / Core Sprint), P2 (Medium / Post-Launch Sprint), P3 (Low / Routine Hardening).

---

## 3. Comprehensive Security Requirements Catalogue

### Domain 1: Authentication (SEC-REQ-AUTH)
| ID | Requirement Specification | Likelihood | Impact | Severity | Priority | Verification Method |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **AUTH-01** | Passwords must be hashed using Argon2id with memory cost $\ge 64\text{ MB}$, time cost $\ge 3$ iterations, and parallelism $\ge 4$ threads. Legacy bcrypt ($\text{rounds} \ge 12$) permitted during migration. | High | Critical | **Critical (12)** | **P0** | Cryptographic unit test asserting Argon2id parameters. |
| **AUTH-02** | Password complexity must enforce minimum 10 characters, at least one uppercase letter, one lowercase letter, one number, and one special character, checked against HaveIBeenPwned common passwords. | High | High | **High (9)** | **P0** | Password validator unit test against breach dictionaries. |
| **AUTH-03** | Authentication endpoints must implement account enumeration defense: login, registration, and password reset endpoints must return identical error phrasing and timing ($\pm 50\text{ ms}$). | High | Medium | **Medium (6)** | **P1** | Automated timing test across valid and invalid usernames. |
| **AUTH-04** | Brute force defense: Failed login attempts must trigger IP- and username-based lockouts (5 failed attempts = 15-minute progressive delay or lockout) via Redis sliding window counters. | High | High | **High (9)** | **P0** | Load test firing 10 failed login requests and verifying 429 response. |
| **AUTH-05** | Password reset tokens must be cryptographically random (256-bit entropy), single-use, hashed in the database via SHA-256, and expire strictly after 15 minutes. | Medium | Critical | **High (8)** | **P0** | Expiry and replay attack unit tests. |

### Domain 2: Authorization & Patient Data Isolation (SEC-REQ-AUTHZ)
| ID | Requirement Specification | Likelihood | Impact | Severity | Priority | Verification Method |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **AUTHZ-01** | Anti-IDOR: Every patient-scoped endpoint (`/predictions/{id}`, `/users/{id}`) must assert that the requested resource `user_id` matches the authenticated `current_user.id`. | High | Critical | **Critical (12)** | **P0** | Cross-patient access penetration test verifying HTTP 403 / 404. |
| **AUTHZ-02** | Role-Based Access Control (RBAC): System must enforce strict roles (`PATIENT`, `CLINICIAN`, `ADMIN`). Administrative endpoints (`/api/v1/admin/*`) must reject non-admin tokens with HTTP 403. | Medium | Critical | **High (8)** | **P0** | Role boundary unit tests across all protected routers. |
| **AUTHZ-03** | Segregation of Duties: Administrators cannot view raw patient prediction histories or PHI unless explicitly authorized for a logged medical emergency override audit. | Low | Critical | **Medium (4)** | **P1** | Audit query asserting administrative access block to health records. |

### Domain 3: Doctor / Healthcare Provider Access (SEC-REQ-DOC)
| ID | Requirement Specification | Likelihood | Impact | Severity | Priority | Verification Method |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **DOC-01** | Clinician access to a patient record is strictly prohibited unless an explicit, active, non-expired consent grant exists in `user_consents` signed by the patient. | Medium | Critical | **High (8)** | **P0** | Integration test attempting clinician record read without consent record. |
| **DOC-02** | Clinician credentials must be validated via country-specific registry adapters (e.g. state medical council or national directory verification). | Medium | High | **Medium (6)** | **P1** | Directory verification adapter unit tests. |

### Domain 4: Session Management (SEC-REQ-SESS)
| ID | Requirement Specification | Likelihood | Impact | Severity | Priority | Verification Method |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **SESS-01** | Tokens must be issued as short-lived JWT access tokens (lifetime $\le 15$ minutes) and stored in memory only. Refresh tokens must be stored in `HttpOnly`, `Secure`, `SameSite=Strict` cookies. | High | High | **High (9)** | **P0** | Browser cookie header inspection and XSS extraction test. |
| **SESS-02** | Refresh token rotation (RTR): Every refresh token usage must invalidate the used token and issue a new cryptographic pair. Replay of an old refresh token must invalidate the entire token family. | Medium | High | **Medium (6)** | **P0** | Token replay integration test verifying immediate family revocation. |
| **SESS-03** | Sensitive account changes (password update, email change) must immediately revoke all active refresh tokens in Redis, forcing re-authentication across all user devices. | Medium | High | **Medium (6)** | **P1** | Post-password-change token invalidation test. |

### Domain 5: API Security (SEC-REQ-API)
| ID | Requirement Specification | Likelihood | Impact | Severity | Priority | Verification Method |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **API-01** | Strict request body validation: All endpoints must enforce Pydantic V2 schemas with explicit type enforcement, regex bounds, and physiological value clamping. | High | High | **High (9)** | **P0** | Fuzz testing invalid JSON payloads and out-of-range biomarkers. |
| **API-02** | Response sanitization: Internal database keys, password hashes, stack traces, and environment paths must be strictly excluded from serialized API output models. | High | Medium | **Medium (6)** | **P0** | Schema serialization inspection tests. |
| **API-03** | API Rate Limiting: Unauthenticated endpoints limited to 20 req/min; authenticated endpoints to 100 req/min; ML prediction endpoints to 10 req/min per IP/user. | High | Medium | **Medium (6)** | **P0** | Benchmark load test verifying HTTP 429 Too Many Requests response. |
| **API-04** | CORS Configuration: Access-Control-Allow-Origin must be strictly restricted to explicitly whitelisted production domain names; wildcard `*` strictly prohibited. | High | High | **High (9)** | **P0** | Origin header spoofing test. |

### Domain 6: Database Security (SEC-REQ-DB)
| ID | Requirement Specification | Likelihood | Impact | Severity | Priority | Verification Method |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **DB-01** | SQL Injection Defense: 100% of database interactions must execute through SQLAlchemy 2.0 parameterized queries or ORM models. Raw SQL string formatting is strictly forbidden. | High | Critical | **Critical (12)** | **P0** | Semgrep / Bandit SAST rule scanning for string-formatted SQL. |
| **DB-02** | Least-Privilege Database Users: Application connection pool must run as `heartxai_app` with `SELECT`, `INSERT`, `UPDATE`, `DELETE` only. DDL migrations run as `heartxai_migrator`. | Medium | Critical | **High (8)** | **P0** | Database permission inspection script. |
| **DB-03** | Connection Security: Database connections must require TLS (`sslmode=verify-full`) with root CA validation; plaintext connections rejected. | Medium | High | **Medium (6)** | **P0** | Connection configuration inspection test. |

### Domain 7: File and Report Security (SEC-REQ-FILE)
| ID | Requirement Specification | Likelihood | Impact | Severity | Priority | Verification Method |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **FILE-01** | Uploaded medical documents (ECG tracings, lab reports) must undergo magic-byte MIME type validation, rejecting files based solely on user-supplied file extensions. | High | High | **High (9)** | **P0** | Executable file masquerading as `.pdf` upload rejection test. |
| **FILE-02** | File size limits: Individual uploads capped at $5\text{ MB}$; overall patient storage quota capped at $50\text{ MB}$. | High | Low | **Low (3)** | **P2** | Upload test with oversized file verifying HTTP 413 Payload Too Large. |
| **FILE-03** | Storage Isolation: Uploaded files stored in a non-executable private bucket using cryptographically random UUIDs; direct web-accessible URL paths strictly disabled. | Medium | Critical | **High (8)** | **P0** | Storage bucket access policy audit. |
| **FILE-04** | Download Authorization: Medical reports and files accessible only via presigned, time-bounded URLs (expiry $\le 10$ minutes) requiring active patient session ownership. | High | High | **High (9)** | **P0** | Unauthenticated presigned URL expiration and tampering test. |

### Domain 8: Machine Learning & Prediction Security (SEC-REQ-ML)
| ID | Requirement Specification | Likelihood | Impact | Severity | Priority | Verification Method |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **ML-01** | Model Artifact Integrity: The backend must verify the SHA-256 digest and HMAC signature of all model artifacts prior to loading into memory. Tampered artifacts abort startup. | Medium | Critical | **High (8)** | **P0** | Tampered JSON artifact loading test verifying `ModelIntegrityException`. |
| **ML-02** | Deserialization Safety: Tree models loaded strictly from native JSON formats; arbitrary Python `pickle.load()` on untrusted streams is prohibited. | High | Critical | **Critical (12)** | **P0** | Static code analysis verifying absence of unvalidated `pickle.load`. |
| **ML-03** | Adversarial Clamping: Clinical input features must be clamped within strictly enforced physiological bounds ($80 \le \text{trestbps} \le 240\text{ mmHg}$) before vector conversion. | High | High | **High (9)** | **P0** | Adversarial gradient perturbation injection test. |
| **ML-04** | Model Inversion Defense: Output SHAP values rounded to 4 decimal places; raw internal decision-tree leaf indices never exposed via API. | Low | Medium | **Low (2)** | **P2** | API output schema inspection. |

### Domain 9: Logging and Auditing (SEC-REQ-AUD)
| ID | Requirement Specification | Likelihood | Impact | Severity | Priority | Verification Method |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **AUD-01** | Audit Log Completeness: All authentication attempts, privilege grants, patient record views, prediction evaluations, and data exports must be logged to an append-only store. | Medium | High | **Medium (6)** | **P0** | Audit table population assertion across all CRUD endpoints. |
| **AUD-02** | PII Scrubbing: Audit logs must strictly scrub passwords, session tokens, JWTs, credit card numbers, and raw national IDs via centralized log filters. | High | High | **High (9)** | **P0** | Automated log scanner asserting absence of regex-matched credentials. |
| **AUD-03** | Log Tamper-Resistance: Audit records stored in an append-only database table with row-level hashes; database users lack `UPDATE` or `DELETE` privileges on `audit_logs`. | Low | High | **Medium (3)** | **P1** | SQL test asserting `DELETE FROM audit_logs` fails with permission error. |

### Domain 10: Backup and Recovery (SEC-REQ-BCP)
| ID | Requirement Specification | Likelihood | Impact | Severity | Priority | Verification Method |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **BCP-01** | Backup Encryption: All database and file backups must be encrypted at rest using AES-256-GCM with KMS-managed customer keys prior to off-site replication. | Medium | Critical | **High (8)** | **P0** | Backup artifact inspection verifying ciphertext format and valid nonce. |
| **BCP-02** | Restoration Verification: Automated quarterly backup restoration rehearsals must verify data integrity and guarantee $\text{RPO} \le 1\text{ hour}$ and $\text{RTO} \le 4\text{ hours}$. | Low | Critical | **Medium (4)** | **P1** | Documented sandbox restore drill log. |

### Domain 11: Third-Party Integration Security (SEC-REQ-INT)
| ID | Requirement Specification | Likelihood | Impact | Severity | Priority | Verification Method |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **INT-01** | SSRF Defense: Outgoing HTTP requests to third-party country directories (e.g. hospital/physician directories) must enforce strict domain whitelisting and reject private IPs. | High | High | **High (9)** | **P0** | Unit test verifying requests to `127.0.0.1`, `169.254.169.254`, `10.0.0.0/8` are blocked. |
| **INT-02** | Third-Party Secret Isolation: API keys and credentials for external directory services must be injected via environment secrets, never exposed in client bundles. | High | High | **High (9)** | **P0** | Secret scanning asserting external API keys are absent in frontend code. |

### Domain 12: Deployment and Infrastructure Security (SEC-REQ-DEP)
| ID | Requirement Specification | Likelihood | Impact | Severity | Priority | Verification Method |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **DEP-01** | Container Hardening: Docker containers must run as unprivileged non-root users (`USER appuser`), with read-only root filesystems and minimal base images (`python:3.11-slim`). | High | High | **High (9)** | **P0** | Container security audit asserting `whoami` returns unprivileged UID. |
| **DEP-02** | Vulnerability Free Images: Production container images must undergo vulnerability scanning (Trivy), with zero unresolved Critical or High CVEs permitted at deploy time. | High | Critical | **Critical (12)** | **P0** | CI/CD pipeline gate check. |

### Domain 13: Privacy by Design & Data Subject Rights (SEC-REQ-PRIV)
| ID | Requirement Specification | Likelihood | Impact | Severity | Priority | Verification Method |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **PRIV-01** | Data Minimization: The platform must not collect full national identity numbers, exact residential street addresses, or payment card numbers unless legally mandated. | High | High | **High (9)** | **P0** | Schema audit verifying absence of unneeded personal attributes. |
| **PRIV-02** | Right to Erasure: When a patient requests account deletion, all PII, health measurements, and prediction records must be purged or irreversibly anonymized within 30 days. | Medium | Critical | **High (8)** | **P0** | Account deletion integration test verifying cascade deletion of records. |

### Domain 14: Encryption and Secrets Management (SEC-REQ-CRYP)
| ID | Requirement Specification | Likelihood | Impact | Severity | Priority | Verification Method |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **CRYP-01** | Zero Secrets in Code: No passwords, JWT secrets, database connection strings, or encryption keys may be committed to source code repositories. | High | Critical | **Critical (12)** | **P0** | Automated CI secret scanner (Gitleaks) blocking commits. |
| **CRYP-02** | Envelope Encryption: Highly sensitive database columns (e.g. external medical record identifiers) must be encrypted using AES-256-GCM with keys rotated every 90 days. | Medium | High | **Medium (6)** | **P1** | Database column ciphertext inspection test. |
