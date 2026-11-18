# SECURITY ARCHITECTURE CONSISTENCY AND CROSS-PHASE ALIGNMENT REPORT

**Document Reference:** `docs/security/SECURITY_ARCHITECTURE_CONSISTENCY_REPORT.md`  
**Phase:** 09 — Security, Privacy, Data Protection & Threat Modelling  
**Status:** Approved Technical Audit  
**Author:** Principal Security Architect & Systems Traceability Lead  
**Traceability:** All upstream engineering documents (Phases 01 through 08)  

---

## 1. Executive Summary & Audit Scope

This document provides a formal, comprehensive consistency audit verifying that the Phase 09 Security, Privacy, and Threat Modelling blueprint aligns seamlessly with all previously approved engineering specifications from Phases 02 through 08.

Every security control, authorization check, cryptographic standard, and regulatory boundary defined in Phase 09 has been cross-referenced against the functional requirements, system architecture, database schema, frontend state management, backend service dependencies, and machine learning models.

---

## 2. Cross-Phase Traceability Matrix

| Engineering Subsystem | Upstream Approved Document | Phase 09 Security Specification | Alignment Status |
| :--- | :--- | :--- | :---: |
| **Requirements: Security & Privacy** | `docs/NON_FUNCTIONAL_REQUIREMENTS.md` (NFR-SEC-01 to 09, NFR-PRIV-01) | `docs/security/SECURITY_REQUIREMENTS_CATALOGUE.md` | **ALIGNED (100%)** |
| **Global Architecture (ADR-011)** | `docs/GLOBAL_COUNTRY_CONFIGURATION_ARCHITECTURE.md` | `docs/security/GLOBAL_PRIVACY_AND_REGULATORY_REVIEW.md` | **ALIGNED (100%)** |
| **Clinical Target Boundary (ADR-009)**| `docs/architecture/ADR_009_DISEASE_CLASSIFICATION_VS_RISK_SCORING.md` | `docs/security/MACHINE_LEARNING_SECURITY.md` | **ALIGNED (100%)** |
| **Design System & UX** | `docs/design/PATIENT_UX_SPECIFICATION.md` (Consent modals, auth forms) | `docs/security/PRIVACY_BY_DESIGN_AND_CONSENT.md` | **ALIGNED (100%)** |
| **Frontend Engineering** | `docs/frontend/FRONTEND_AUTHENTICATION_AND_SECURITY.md` | `docs/security/FRONTEND_SECURITY_SPECIFICATION.md` | **ALIGNED (100%)** |
| **Backend Engineering Architecture** | `docs/backend/BACKEND_SECURITY_IMPLEMENTATION.md` & `deps.py` | `docs/security/AUTHORIZATION_AND_PATIENT_ISOLATION.md` | **ALIGNED (100%)** |
| **Database Schema & Persistence** | `docs/backend/DATABASE_DESIGN_DOCUMENT.md` (`users`, `audit_logs`) | `docs/security/DATABASE_AND_FILE_SECURITY.md` | **ALIGNED (100%)** |
| **Machine Learning Subsystem** | `docs/ml/MODEL_VERSIONING_AND_REPRODUCIBILITY.md` (HMAC, JSON) | `docs/security/MACHINE_LEARNING_SECURITY.md` | **ALIGNED (100%)** |

---

## 3. Subsystem-by-Subsystem Consistency Audit

### 3.1 Alignment with Phase 3 System Architecture & ADR-011
- **ADR-011 Compliance:** The security architecture maintains a universal core (Argon2id, TLS 1.3, anti-IDOR, envelope encryption) while delegating privacy legal notices, statutory consent schedules, and directory verification adapters to pluggable country modules (e.g. India DPDP Act 2023, EU GDPR, US HIPAA).
- **Network Trust Zones:** The five security trust zones defined in Phase 9 mirror the C4 Container and Deployment diagrams established in Phase 3.

### 3.2 Alignment with Phase 6 Frontend Architecture
- **In-Memory Token Delivery:** Phase 6 specified that JWT access tokens should reside in Zustand memory (`authStore`) while refresh tokens reside in `HttpOnly` cookies. Phase 9 formally validates this design against OWASP ASVS and specifies Content Security Policy headers preventing XSS extraction.
- **Inactivity Timeout:** Phase 9 specifies an 11-minute automated session termination with complete memory reset, matching the client inactivity lifecycle specified in Phase 6.

### 3.3 Alignment with Phase 7 Backend Architecture & Database Design
- **Route Dependency Layer (`app/api/deps.py`):** Phase 7's dependency injection design directly hosts Phase 9's anti-IDOR ownership checks (`get_current_patient_prediction`), returning HTTP 404 for unauthorized accesses to prevent resource enumeration.
- **Database Roles:** Phase 9 aligns with the PostgreSQL relational schema, defining least-privilege roles (`heartxai_app` read/write vs `heartxai_migrator` DDL) and append-only trigger protection on `audit_logs`.

### 3.4 Alignment with Phase 8 Machine Learning Subsystem
- **Serialization Safety:** Phase 9 reinforces Phase 8's mandate that tree ensembles are saved strictly in native JSON format, preventing Python pickle RCE vulnerabilities.
- **Integrity Verification:** HMAC-SHA256 signature verification specified in Phase 8 is integrated into Phase 9 container startup checks.
- **Physiological Clamps:** The Pydantic V2 input validation boundaries in the API gateway match the biological feature ranges specified in the ML data dictionary.

---

## 4. Discrepancies Identified and Approved Remediations

During the consistency review, two architectural discrepancies between early prototype notes and Phase 9 production security were analyzed:

| ID | Initial Prototype State | Phase 9 Security Architecture | Rationale & Remediation |
| :---: | :--- | :--- | :--- |
| **DISC-SEC-01** | `backend/app/core/security.py` uses legacy `bcrypt` (12 rounds) and static `SECRET_KEY`. | Upgrades to **Argon2id** ($64\text{ MB}, 3\text{ iterations}, 4\text{ lanes}$) and KMS-managed rotating keys. | Bcrypt is susceptible to high-density GPU offline cracking. Argon2id provides memory-hard protection. A transparent in-flight re-hashing upgrade pipeline is implemented. |
| **DISC-SEC-02** | Early draft suggested storing JWTs in browser `localStorage` for simple client persistence. | Replaced with **In-Memory Access JWTs + Rotated HttpOnly Cookies**. | `localStorage` is vulnerable to token theft via any successful XSS injection. HttpOnly cookies cannot be read by JavaScript, providing complete XSS isolation. |

---

## 5. Architectural Consistency Sign-off

The Phase 09 Security, Privacy, Data Protection, and Threat Modelling specification is **100% consistent and fully compliant** with all upstream architectural specifications, database schemas, frontend data stores, and machine learning designs of HeartXAI 2.0.
