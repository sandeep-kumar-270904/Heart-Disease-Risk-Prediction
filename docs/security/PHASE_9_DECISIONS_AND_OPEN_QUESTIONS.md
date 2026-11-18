# PHASE 9 SECURITY DECISIONS AND OPEN GOVERNANCE QUESTIONS

**Document Reference:** `docs/security/PHASE_9_DECISIONS_AND_OPEN_QUESTIONS.md`  
**Phase:** 09 — Security, Privacy, Data Protection & Threat Modelling  
**Status:** Approved Technical Ledger  
**Author:** Principal Security Architect & Governance Lead  
**Traceability:** All Phase 09 Security Specifications  

---

## 1. Executive Summary

This ledger records all foundational cryptographic, identity, authorization, and regulatory decisions finalized during the Phase 09 Security, Privacy, and Threat Modelling specification. It also catalogs the open questions requiring stakeholder and user review prior to Phase 10 implementation.

---

## 2. Approved Architectural & Cryptographic Decisions

| Decision ID | Domain | Decision Summary | Rationale & Justification |
| :--- :--- | :--- | :--- | :--- |
| **SEC-DEC-01** | **Password Hashing** | Adopt **Argon2id** ($64\text{ MB RAM}, 3\text{ iterations}, 4\text{ parallel lanes}$) with transparent in-flight migration from legacy bcrypt. | Superior memory-hard resistance against GPU-accelerated and ASIC offline password cracking (RFC 9106). |
| **SEC-DEC-02** | **Session Architecture** | **In-memory short-lived access JWTs ($15\text{ mins}$) + Rotated HttpOnly refresh tokens in cookies ($7\text{ days}$)** with Redis stateful revocation. | Eliminates token theft via XSS while preserving horizontal backend scalability and instant session revocation capability. |
| **SEC-DEC-03** | **Anti-IDOR Strategy** | Mandatory resource ownership check at FastAPI dependency layer (`deps.py`) returning **HTTP 404 Not Found** on unauthorized requests. | Prevents resource enumeration attacks while stopping horizontal privilege escalation across patient records. |
| **SEC-DEC-04** | **Database Least Privilege**| Partition database users: `heartxai_app` (DML only, no DDL), `heartxai_migrator` (DDL migrations only), and `heartxai_readonly` (audit). | Contains blast radius if backend runtime is compromised; prevents unauthorized schema drops. |
| **SEC-DEC-05** | **ML Deserialization** | Tree ensembles serialized strictly in native JSON; joblib preprocessors verified with detached HMAC-SHA256 signatures before loading. | Eliminates arbitrary Python `pickle` Remote Code Execution (RCE) vulnerabilities. |
| **SEC-DEC-06** | **Backup Security** | Nightly database dumps encrypted using **AES-256-GCM** authenticated encryption with unique 96-bit nonces, verified by quarterly restore drills. | Guarantees ciphertext confidentiality and integrity; eliminates silent backup tampering. |
| **SEC-DEC-07** | **Consent Governance** | Granular, unbundled, time-stamped consent records in `user_consents` table with automated self-service DSAR export and account deletion. | Enforces Privacy by Design (PbD) principles under DPDP Act 2023 Section 6 and GDPR Article 9. |
| **SEC-DEC-08** | **Audit Redaction** | Centralized regex scrubbing filter cleans passwords, JWTs, and direct blood pressure/cholesterol values before emitting JSONL audit logs. | Prevents secondary personal data breaches from log aggregation platforms. |

---

## 3. Open Governance Questions Requiring User Approval

The following items represent operational and regulatory policy choices requiring explicit stakeholder or user direction:

### Open Question 1: Mandatory Multi-Factor Authentication (MFA) Policy for Patients
- **Context:** MFA via TOTP (RFC 6238) is architecturally mandated for all `ADMIN` accounts. For `PATIENT` accounts, enabling mandatory MFA significantly enhances security against credential stuffing, but introduces onboarding friction for elderly or less tech-savvy patients.
- **Options:**
  - **Option A (Recommended):** Optional MFA for standard patients, strongly encouraged via in-app security score cards and security banners.
  - **Option B:** Mandatory MFA for all patients upon registration, requiring a smartphone authenticator app.
- **Recommendation:** Option A. Enforcing mandatory MFA on patient accounts may cause severe abandonment in public health contexts. Provide single-click TOTP activation and backup codes.

### Open Question 2: Clinician Consent Expiration Window
- **Context:** When a patient delegates access to a verified healthcare provider (`CLINICIAN`), a time-bounded consent grant is recorded in `user_consents`.
- **Options:**
  - **Option A:** Fixed 24-hour temporary access window (ideal for single clinical consultations).
  - **Option B (Recommended):** Configurable expiration chosen by the patient: 24 Hours, 7 Days, 30 Days, or Until Revoked.
- **Recommendation:** Option B. Gives the patient complete sovereign control over their data sharing while maintaining clear visibility over active grants.

### Open Question 3: Production Key Management Service (KMS) Provider
- **Context:** Cryptographic master keys (KEKs) for envelope encryption and backup signing require an external Key Management Service.
- **Options:**
  - **Option A:** AWS KMS / GCP Cloud KMS (managed cloud service, zero infrastructure overhead).
  - **Option B:** Self-hosted HashiCorp Vault container (cloud-agnostic, requires dedicated operator maintenance).
- **Recommendation:** Cloud KMS (AWS KMS or GCP KMS) for initial production deployment to ensure FIPS 140-2 Level 3 HSM compliance with zero operational overhead.

---

## 4. Unresolved Security Risks & External Dependencies

| Unresolved Risk | Likelihood | Impact | External Dependency / Mitigation Strategy |
| :--- | :---: | :---: | :--- |
| **Third-Party Directory Availability** | Medium | Medium | Country directory services (e.g. Indian hospital portals or US provider NPI registries) may lack official public APIs. Handled via mock fallback adapters with offline cached snapshots. |
| **Formal Regulatory Certification** | N/A | High | HeartXAI is architecturally designed to satisfy HIPAA and DPDP baselines, but formal certification requires engaging accredited third-party auditors and legal counsel. |
| **Zero-Day Supply Chain Vulnerability** | Low | Critical | Mitigated via pinned lockfiles, automated `pip-audit` / `npm audit` gates, and minimal Docker base images. |

---

## 5. Phase Sign-Off Gate

The Phase 09 Security, Privacy, Data Protection, and Threat Modelling blueprint is complete across 19 technical documents in `docs/security/`. 

**STOP GATE ENGAGED:** In accordance with Prompt 09 instructions, no implementation code, package installations, or configuration changes have been executed. The system is halted awaiting formal review and approval.
