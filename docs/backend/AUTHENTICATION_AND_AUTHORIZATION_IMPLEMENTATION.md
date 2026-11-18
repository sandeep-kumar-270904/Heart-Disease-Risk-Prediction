# HeartXAI 2.0 — Authentication & Authorization Implementation Specification

**Document ID:** `HX2-BE-006`  
**Version:** `1.0.0`  
**Phase:** Phase 7 — Backend Engineering Architecture & API Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Application Security Architect & Principal Backend Engineer  
**Traceability:** FR-001–FR-015, NFR-001–NFR-028, ADR-001, ADR-005, HXAI-ARCH-012  

---

## 1. Authentication Architecture & Session Security

HeartXAI 2.0 implements a **Stateful-Session, Stateless-Verification Hybrid Model** centered on **Argon2id password hashing**, **cryptographically signed JWTs**, and **secure `HttpOnly` browser cookies**.

### 1.1 Non-Negotiable Security Invariants
1. **Zero Client-Side Token Storage:** Authentication tokens (`access_token`, `refresh_token`) **must never** be exposed to client-side JavaScript. All tokens reside in `HttpOnly`, `SameSite=Strict`, `Secure` cookies.
2. **Argon2id Hashing Exclusivity:** All user passwords are encrypted using Argon2id (`time_cost=3`, `memory_cost=65536` [$64\text{ MB}$], `parallelism=4`). MD5, SHA-256, and legacy bcrypt are banned.
3. **Double-Submit CSRF Protection:** State-changing HTTP verbs (`POST`, `PUT`, `DELETE`) require a valid `X-CSRF-Token` header matching the client-accessible `csrf_token` cookie.
4. **Account Lockout on Brute-Force:** 5 consecutive failed authentication attempts lock the target account for 15 minutes, with security alerts logged to the immutable audit trail.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   COOKIE & SESSION TRANSPORT LIFECYCLE                 │
├────────────────────────────────────────────────────────────────────────┤
│ Client Browser                     FastAPI Backend Gateway             │
│       │                                       │                        │
│   1.  ├── POST /auth/login (email, pass) ────►│ Verify Argon2id hash   │
│       │                                       │ Check is_active == True│
│       │                                       │                        │
│   2.  │◄── Set-Cookie: access_token; HttpOnly ┼ Issue 15-min JWT       │
│       │    Set-Cookie: refresh_token; HttpOnly┼ Issue 7-day Refresh JWT│
│       │    Set-Cookie: csrf_token; SameSite   ┼ Issue CSRF Token       │
│       │                                       │                        │
│   3.  ├── GET /assessments (Cookie auto-sent)►│ Verify JWT signature  │
│       │   Header: X-CSRF-Token                │ Enforce patient_id     │
│       │                                       │                        │
│   4.  ├── POST /auth/refresh (Cookie auto) ──►│ Rotate access token    │
│       │                                       │ Verify token version   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Password Hashing Specification (`argon2-cffi`)

```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

hasher = PasswordHasher(
    time_cost=3,        # 3 iterations
    memory_cost=65536,  # 64 MiB memory hardness
    parallelism=4,      # 4 concurrent threads
    hash_len=32,
    salt_len=16
)

def hash_password(plain_password: str) -> str:
    return hasher.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return hasher.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False
```

---

## 3. JWT Token Claims & Verification Specification

### 3.1 Token Structures & Expiry Windows
- **Access Token:**
  - `sub`: User UUIDv4
  - `role`: `"PATIENT" | "CLINICIAN" | "ADMINISTRATOR"`
  - `email`: User email address
  - `country`: ISO-3166-1 alpha-2 code
  - `exp`: Issued at $+ 15\text{ minutes}$ (900 seconds)
  - `iss`: `"heartxai-auth-service"`
- **Refresh Token:**
  - `sub`: User UUIDv4
  - `token_version`: Monotonically increasing integer stored on the `User` record
  - `exp`: Issued at $+ 7\text{ days}$ (604,800 seconds)
  - `Path`: `/api/v1/auth/refresh` (Restricted path prevents leakage to other routes)

### 3.2 Token Revocation & Invalidation
- When a user changes their password, requests a session revocation, or logs out from all devices, the backend increments `user.token_version`.
- Any subsequent refresh attempt presenting an older `token_version` is rejected immediately with `HTTP 401 Unauthorized`.

---

## 4. Role-Based & Object-Level Access Control (RBAC & OLAC)

### 4.1 Role Hierarchy & Capabilities Matrix

| Application Role | Public / Education | Intake Assessment | Own Health Records | Cohort Patients | Model Registry | Audit Logs |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Guest / Anonymous** | Read-Only | Denied | Denied | Denied | Denied | Denied |
| **PATIENT** | Read-Only | Create & Run | Full (Own Only) | Denied | Denied | Denied |
| **CLINICIAN** | Read-Only | Run for Patient | Own Account Only| Grant-Restricted| Denied | Denied |
| **ADMINISTRATOR** | Read-Only | Denied | Own Account Only| Denied (Zero PHI)| Full Control | Full Read |

---

## 5. Patient Record Ownership & Consent Grant Enforcement

### 5.1 Object-Level Ownership Check (Patient)
When a patient requests an assessment via `GET /api/v1/assessments/:id`:
```python
async def get_patient_assessment(
    assessment_id: str,
    current_user: User = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow)
) -> Assessment:
    assessment = await uow.assessments.get_by_id(assessment_id)
    if not assessment:
        raise EntityNotFoundException("Assessment", assessment_id)
        
    # Strict Object-Level Ownership Enforcement
    if current_user.role == "PATIENT" and assessment.patient_id != current_user.id:
        # Intentionally return 404 to prevent resource enumeration
        raise EntityNotFoundException("Assessment", assessment_id)
        
    return assessment
```

### 5.2 Clinician Consent Grant Verification
A clinician **must never** access a patient's historical records, biomarker telemetry, or SHAP waterfall plots without an active, unexpired consent grant:

```python
async def verify_clinician_patient_access(
    clinician_id: str,
    patient_id: str,
    uow: UnitOfWork
) -> bool:
    grant = await uow.grants.get_active_grant(
        patient_id=patient_id, 
        clinician_id=clinician_id
    )
    if not grant:
        raise AuthorizationException("No active consent grant found for this patient.")
    if grant.is_expired or grant.is_revoked:
        raise AuthorizationException("Consent grant has expired or was revoked by the patient.")
    return True
```

* **Outcome:** Even if a clinician correctly guesses another patient's assessment UUID, the system evaluates the `patient_doctor_grants` table. In the absence of an explicit unrevoked grant, access is strictly denied with an immutable audit event recorded (`UNAUTHORIZED_CLINICAL_ACCESS_ATTEMPT`).
