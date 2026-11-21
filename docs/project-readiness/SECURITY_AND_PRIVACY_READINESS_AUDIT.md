# HeartXAI 2.0 — Security & Privacy Readiness Audit
**Document ID:** HX-PR-007  
**Version:** 1.0.0  
**Phase:** 12 — Final Pre-Implementation Audit, Architecture Consolidation & Master Development Roadmap  
**Author:** Principal Application Security Architect & DevSecOps Engineer  
**Status:** Approved for Implementation Planning — Zero Blockers  
**Date:** November 2026  

---

## 1. Executive Summary

Healthcare software handles Personal Health Information (PHI) and Personally Identifiable Information (PII). A security compromise directly impacts patient privacy, institutional trust, and clinical safety.

This audit evaluates the security architecture established in Phase 09. It verifies that defensive controls, cryptographic algorithms, authorization boundaries, and audit mechanisms are fully specified and production-grade. **No critical security blockers remain.**

---

## 2. Core Security Controls Verification

```
+---------------------------------------------------------------------------------------------------------+
|                                    SECURITY CONTROLS AUDIT MATRIX                                       |
+--------------------------+-------------------------------------------------------------+----------------+
| Security Dimension       | Approved Architectural Specification                        | Readiness      |
+--------------------------+-------------------------------------------------------------+----------------+
| Password Storage         | Argon2id (RFC 9106): Memory 64 MB, Time 3 iterations,       | Fully Verified |
|                          | Parallelism 4, Salt 16 bytes, Hash 32 bytes.                |                |
+--------------------------+-------------------------------------------------------------+----------------+
| Access Token Lifecycle   | Ed25519 or RS256 signed JWTs. Lifespan: 15 minutes.         | Fully Verified |
|                          | Stored in-memory in frontend client (never localStorage).   |                |
+--------------------------+-------------------------------------------------------------+----------------+
| Refresh Token Lifecycle  | Cryptographically random 256-bit token. Lifespan: 7 days.   | Fully Verified |
|                          | HttpOnly, Secure, SameSite=Lax cookie. Redis rotation.      |                |
+--------------------------+-------------------------------------------------------------+----------------+
| Authorization / Access   | Strict RBAC via JWT claims + Anti-IDOR dependency checks:   | Fully Verified |
|                          | `current_user.id == resource.patient_id` or active grant.   |                |
+--------------------------+-------------------------------------------------------------+----------------+
| Data Encryption in Transit| TLS 1.3 mandatory. Modern cipher suites. HSTS enabled:     | Fully Verified |
|                          | `max-age=31536000; includeSubDomains; preload`.             |                |
+--------------------------+-------------------------------------------------------------+----------------+
| Data Encryption at Rest  | AES-256-GCM AEAD envelope encryption for sensitive PHI     | Fully Verified |
|                          | fields. AWS KMS / HashiCorp Vault key rotation.             |                |
+--------------------------+-------------------------------------------------------------+----------------+
| Secrets Management       | Zero credentials in git. Runtime environment injection or   | Fully Verified |
|                          | Docker Secrets. Mandatory `.gitignore` enforcement.         |                |
+--------------------------+-------------------------------------------------------------+----------------+
| Audit Trail Logging      | Append-only `audit_logs` table. Records `actor_id`, action, | Fully Verified |
|                          | `resource_id`, timestamp, IP (hashed), correlation ID.      |                |
+--------------------------+-------------------------------------------------------------+----------------+
| Patient Consent Grants   | Cryptographically signed time-limited (72h) access tokens.  | Fully Verified |
|                          | Instant patient revocation via one-click API call.          |                |
+--------------------------+-------------------------------------------------------------+----------------+
| Right to Be Forgotten    | Cascading soft-delete with 30-day purge window. Automated   | Fully Verified |
|                          | anonymization of ML assessment logs upon user deletion.     |                |
+--------------------------+-------------------------------------------------------------+----------------+
| Database Backups         | Nightly pg_dump piped through OpenSSL AES-256-GCM (ADR-012) | Fully Verified |
|                          | with SHA-256 integrity checksums to WORM offsite storage.   |                |
+--------------------------+-------------------------------------------------------------+----------------+
```

---

## 3. Defense Against Insecure Direct Object References (IDOR)

In multi-tenant healthcare applications, IDOR vulnerabilities allow authenticated users to view or tamper with other patients' medical records by manipulating numeric or UUID parameters.

**Mandatory Architectural Protection:**
In HeartXAI, every endpoint accepting a `patient_id` or `assessment_id` executes an automated security check before querying business tables:

```python
# Core Anti-IDOR FastAPI Dependency
async def verify_patient_access(
    patient_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
) -> Patient:
    # 1. Admin bypass with explicit audit logging
    if current_user.role == UserRole.ADMIN:
        await log_audit_event(action="ADMIN_PHI_ACCESS", resource=patient_id)
        return await patient_service.get_by_id(db, patient_id)
        
    # 2. Patient owns the record
    if current_user.role == UserRole.PATIENT and current_user.id == patient_id:
        return await patient_service.get_by_id(db, patient_id)
        
    # 3. Doctor holds an active, unexpired consent grant
    if current_user.role == UserRole.DOCTOR:
        grant = await consent_service.get_active_grant(db, doctor_id=current_user.id, patient_id=patient_id)
        if grant and grant.is_valid():
            await log_audit_event(action="DOCTOR_CONSENT_ACCESS", grant_id=grant.id)
            return await patient_service.get_by_id(db, patient_id)

    # 4. Access Denied: Obfuscated 404 to prevent resource enumeration
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
```

---

## 4. API Security & Traffic Hardening

- **Rate Limiting:** Implemented via Redis sliding-window algorithm:
  - Public endpoints (`/api/v1/auth/login`): 5 requests / minute / IP.
  - ML Inference endpoints (`/api/v1/assessments`): 10 requests / minute / user.
  - General API endpoints: 100 requests / minute / user.
- **Content Security Policy (CSP):** Strict headers enforced by Nginx:
  ```http
  Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none';
  ```
- **CORS Policy:** Strict origin whitelisting based on environment (`FRONTEND_URL`), disallowing wildcard (`*`) origins when credentials are included.

---

## 5. Security Blockers Assessment

The audit explicitly reviewed whether any unmitigated security risk should halt development:

- **Identified Blockers:** **0 (Zero).**
- **Security Posture:** Production-ready for Phase 13 / Milestone 01 implementation.
- **Compliance Disclaimer:** HeartXAI 2.0 is designed to align with HIPAA Security Rule and UK-GDPR technical standards. Formal third-party attestation (SOC 2 Type II or ISO 27001) will occur prior to commercial multi-tenant enterprise deployment.
