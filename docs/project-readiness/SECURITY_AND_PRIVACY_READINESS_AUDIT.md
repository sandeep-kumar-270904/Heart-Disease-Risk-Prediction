# HeartXAI 2.0 — Security & Privacy Readiness Audit
**Document ID:** HX-PR-007  
**Version:** 2.0.0 (Phase 12.1 Revision)  
**Phase:** 12.1 — Final Audit Corrections, Clinical Scope Resolution & Implementation Authorization  
**Author:** Principal Application Security Architect & DevSecOps Lead  
**Status:** Architecture Evaluated — Implementation-Time Security Gates Defined  
**Date:** November 2026  

---

## 1. Executive Summary

Healthcare applications handling patient accounts, health questionnaires, and machine learning inferences require uncompromising application security. Rather than claiming that an unbuilt application has "zero security vulnerabilities," this audit rigorously distinguishes between security controls that are **Designed**, **Implemented**, **Tested**, and **Independently Reviewed**.

This document evaluates the complete security posture of HeartXAI 2.0, defines Redis failure behavior, articulates cryptographic key management, and establishes implementation-time security gates and release blockers.

---

## 2. Granular Security Controls Status Matrix

```
+-------------------------------------------------------------------------------------------------------------------------------+
|                                                SECURITY CONTROLS STATUS AUDIT                                                 |
+--------------------------+-----------------------+-----------------------+---------------------+------------------------------+
| Security Dimension       | Designed              | Implemented           | Tested              | Independent Review & Gates   |
+--------------------------+-----------------------+-----------------------+---------------------+------------------------------+
| **Argon2id Hashing**     | ADR-003: 64MB RAM,    | `backend/app/core/`   | `tests/test_`       | Phase 09 Threat Model;       |
| (RFC 9106)               | 3 iter, 4 threads.    | `security.py`         | `security.py` pass. | Unit test verified in CI.    |
+--------------------------+-----------------------+-----------------------+---------------------+------------------------------+
| **Access Tokens**        | ADR-004: 15-min JWT,  | `backend/app/core/`   | `tests/test_`       | Phase 09 Review; in-memory   |
| (Ed25519 / RS256)        | client memory storage.| `security.py`         | `security.py` pass. | client storage enforced.     |
+--------------------------+-----------------------+-----------------------+---------------------+------------------------------+
| **HttpOnly Refresh**     | ADR-004: 7-day cookie,| Endpoint signatures   | Unit test mock only;| Milestone 06 gate:           |
| **Cookies**              | Secure, SameSite=Lax. | designed in schemas.  | live integration pending. integration cookie test.   |
+--------------------------+-----------------------+-----------------------+---------------------+------------------------------+
| **Token Rotation &**     | ADR-005: Redis token  | Redis client wrapper  | Unit mocked; live   | Milestone 06 gate: replay    |
| **Reuse Detection**      | family invalidation.  | drafted in core.      | Redis pending.      | attack invalidation test.    |
+--------------------------+-----------------------+-----------------------+---------------------+------------------------------+
| **Redis Failure Policy** | Fail-Closed: reject   | Exception handlers    | Pending Milestone 06| Security invariant: no       |
| (Session Outage)**       | refresh if cache down.| drafted in core.      | test execution.     | unvalidated tokens on outage.|
+--------------------------+-----------------------+-----------------------+---------------------+------------------------------+
| **CSRF Protection**      | Double-Submit Cookie  | Middleware contract   | Pending frontend/   | Milestone 06/07 gate:        |
|                          | on state-changing POST| specified in design.  | backend integration.| automated CSRF test suite.   |
+--------------------------+-----------------------+-----------------------+---------------------+------------------------------+
| **Anti-IDOR Authorization| `verify_patient_      | FastAPI dependency    | Unit logic mocked;  | Milestone 06/18 gate: 100%   |
| Checks**                 | access` pattern.      | pattern specified.    | endpoint tests pend.| cross-tenant rejection test. |
+--------------------------+-----------------------+-----------------------+---------------------+------------------------------+
| **Encryption at Rest**   | AES-256-GCM envelope  | SQLAlchemy TypeDecor- | Pending Milestone 04| Milestone 04 gate: column    |
|                          | encryption for PHI.   | ator designed.        | test execution.     | ciphertext inspection.       |
+--------------------------+-----------------------+-----------------------+---------------------+------------------------------+
| **Key Management &**     | AWS KMS / Vault /     | Environment variable  | Mock key test; live | Milestone 01 gate: zero      |
| **Rotation**             | Master Key derivation.| injection designed.   | rotation pending.   | plaintext keys in git repo.  |
+--------------------------+-----------------------+-----------------------+---------------------+------------------------------+
| **Encrypted Backups**    | ADR-012: pg_dump via  | `infra/scripts/`      | Script syntax check;| Milestone 20 gate: live      |
|                          | OpenSSL AES-256-GCM.  | `backup_encrypted.sh` | restore pending M20.| backup and restore drill.    |
+--------------------------+-----------------------+-----------------------+---------------------+------------------------------+
| **Audit Log Integrity**  | Append-only table,    | `backend/app/models/` | `tests/test_`       | Milestone 04/17 gate:        |
|                          | DB user write-only.   | `audit.py`            | `database_models.py`| DB permission verification.  |
+--------------------------+-----------------------+-----------------------+---------------------+------------------------------+
```

---

## 3. High-Priority Security Control Details

### 3.1 Redis Session Failure Behavior: Strict Fail-Closed Policy
In token-family rotation architectures, if the Redis session cache fails or experiences network partitioning, systems face a critical tradeoff:
- *Fail-Open (Dangerous):* Allow refresh tokens to be exchanged without verifying against the revocation blacklist, opening a window for replayed stolen tokens.
- *Fail-Closed (Secure — Mandated by HeartXAI):* If Redis is unreachable after exponential retry (3 attempts over 500ms), the authentication service **immediately rejects the token refresh request** with an RFC 7807 error (HTTP 503 Service Unavailable / Cache Unavailable) and logs a critical security alert. The user is prompted to re-authenticate. **Under no circumstances shall an unvalidated refresh token issue a new access JWT.**

### 3.2 Anti-IDOR Authorization Controls
Insecure Direct Object References (IDOR) are the primary vector for unauthorized PHI access in healthcare APIs. 
- **Mandatory FastAPI Dependency:** Every endpoint with a path parameter (`/patients/{patient_id}`, `/assessments/{assessment_id}`) must declare `Depends(verify_patient_access)`.
- **Validation Rule:**
  1. If `current_user.id == patient_id`: Access granted.
  2. If `current_user.role == UserRole.DOCTOR`: Checks `consent_grants` table for an unexpired, unrevoked grant matching `doctor_id` and `patient_id`.
  3. If `current_user.role == UserRole.ADMIN`: Access granted with mandatory audit logging.
  4. Otherwise: **Return HTTP 404 Not Found** (obfuscating whether the resource exists to prevent ID enumeration).

### 3.3 Cryptographic Key Management & Envelope Encryption
- **Master Encryption Key (MEK):** Stored outside the application codebase in environment secrets or cloud KMS.
- **Data Encryption Keys (DEK):** Generated per-record or per-column using AES-256-GCM.
- **Zero Plaintext Secrets in Repository:** Mandatory `.gitignore` enforcement; automated pre-commit hook scanning with `detect-secrets` or Gitleaks.

---

## 4. Implementation-Time Security Release Blockers

The following criteria represent **mandatory release blockers** that must be resolved before any deployment to staging or production:

1. **Static Security Analysis:** Zero high or medium severity issues reported by Bandit (Python).
2. **Dependency Vulnerability Scanning:** Zero high or critical CVEs reported by `pip-audit` (Python) and `npm audit` (JavaScript/TypeScript).
3. **Automated Anti-IDOR Test Suite:** 100% pass rate on a dedicated test suite asserting that User A cannot read, edit, or delete any record belonging to User B.
4. **Dynamic Application Security Testing (DAST):** OWASP ZAP baseline scan against the running API reporting zero high-risk findings (e.g., zero injection, zero broken auth, zero missing security headers).
5. **Backup Recovery Verification:** Successful automated decryption and restoration of a synthetic database backup via `restore_encrypted.sh` on an isolated test database.
