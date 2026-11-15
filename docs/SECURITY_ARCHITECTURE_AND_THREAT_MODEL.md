# HeartXAI 2.0 — Security Architecture & Threat Model (STRIDE Methodology)

**Document ID:** HXAI-ARCH-014  
**Version:** 3.0.0  
**Phase:** Phase 3 — System Architecture & Technical Design  
**Status:** Approved  
**Diagram Source:** [`docs/diagrams/security_trust_boundaries.puml`](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/diagrams/security_trust_boundaries.puml)  

---

## 1. Security Philosophy & Defense-in-Depth Principles

HeartXAI 2.0 processes sensitive clinical biomarkers and algorithmic health risk assessments. In healthcare technology, security cannot be an afterthought added to an existing codebase; it must be engineered into every tier through **Defense-in-Depth**:

1. **Principle of Least Privilege:** Users, services, and database connections operate with the minimum permissions required for their tasks.
2. **Zero Trust Perimeter:** No API endpoint implicitly trusts client data. Every payload is sanitized, typed, and validated.
3. **Patient Data Sovereignty:** Healthcare staff cannot browse general patient records. Access strictly requires an active, time-bounded consent grant.
4. **Separation of Concerns:** Authentication credentials (bcrypt hashes) are isolated from clinical health assessments.

---

## 2. Security Trust Boundaries & Network Zones

```mermaid
graph TB
    subgraph Zone0 ["Zone 0: Public Untrusted Internet"]
        Attacker["Potential Adversary / Malicious Client"]
        Client["Legitimate Patient / Clinician Browser"]
    end

    subgraph Zone1 ["Zone 1: DMZ & Ingress Perimeter (Public Network)"]
        Nginx["Nginx Reverse Proxy / WAF\n- TLS 1.3 Termination (HTTPS Port 443)\n- IP Rate Limiting (5 login/min)\n- CORS Policy Enforcement\n- Gzip / Asset Caching"]
    end

    subgraph Zone2 ["Zone 2: Application Tier (Internal Private Network)"]
        FastAPI["FastAPI Modular Monolith (Internal Port 8000)\n- HttpOnly JWT Validation\n- RBAC Route Guards (deps.py)\n- Pydantic v2 Range Sanitization\n- In-Process C++ TreeSHAP Runtime"]
    end

    subgraph Zone3 ["Zone 3: Persistent Data Tier (Isolated Network Subnet)"]
        Postgres[("PostgreSQL 15+ Database\n- Port 5432 (Internal only)\n- Parameterized SQL (SQLAlchemy 2.0)\n- Append-Only Audit Logging Triggers")]
        ModelDisk["Model Artifact Store\n- Read-only Volume Mount\n- SHA-256 Checksum Verification"]
    end

    Client -->|HTTPS Port 443 (TLS 1.3)| Nginx
    Attacker -.->|DDoS / Injection Attacks Blocked| Nginx
    Nginx -->|Internal HTTP Port 8000| FastAPI
    FastAPI -->|Internal TCP 5432 / asyncpg| Postgres
    FastAPI -->|Read-Only Filesystem I/O| ModelDisk
```

---

## 3. Comprehensive Threat Model & Risk Analysis (13 Threat Scenarios)

In accordance with Section 9 of Prompt 03, thirteen specific threat vectors were evaluated using the STRIDE methodology:

| Threat ID | Threat Scenario | STRIDE Category | Affected Component | Potential Impact | Technical Mitigation in HeartXAI 2.0 | Verification Method |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **THREAT-01** | **Unauthorized Patient Record Access (IDOR)**: An authenticated user alters an assessment UUID in URL parameters (`/api/v1/assessments/{id}`) to view another patient's clinical markers. | Information Disclosure | Assessment Controller / Database | Breach of patient confidentiality; HIPAA violation. | Server-side ownership check on every query: `assert assessment.patient_id == current_user.id OR active_doctor_grant_exists()`. | Automated penetration tests attempting cross-tenant queries return HTTP 403. |
| **THREAT-02** | **Broken Access Control (RBAC Evasion)**: A patient crafts an API call to administrative or clinician-only routes (`/api/v1/admin/...`). | Elevation of Privilege | API Middleware / Route Guards | Unauthorized system configuration changes; viewing audit logs. | Declarative route guards (`require_role(["ADMIN"])`, `require_role(["CLINICIAN"])`) enforced in FastAPI dependencies before endpoint execution. | Automated RBAC test suite asserting 403 Forbidden on all unauthorized role permutations. |
| **THREAT-03** | **Account Takeover & Credential Stuffing**: Automated bots execute dictionary or brute-force attacks against `/api/v1/auth/login`. | Spoofing | Auth Controller / Nginx | Account compromise; unauthorized access to patient historical health records. | Tiered rate limiting: Nginx + in-memory sliding window limits login attempts to 5 per minute per IP address. Bcrypt work factor 12. | Integration test verifying 6th rapid login attempt receives HTTP 429 Too Many Requests. |
| **THREAT-04** | **SQL Injection (SQLi)**: Adversary submits SQL metacharacters (`' OR 1=1 --`) within form inputs or search fields. | Tampering | Data Access Layer / SQLAlchemy | Database exfiltration; unauthorized modification or deletion of records. | 100% of queries use SQLAlchemy 2.0 typed parameters. Direct raw string interpolation is strictly banned in backend linting rules. | Static analysis security scan (Bandit) + automated SQLi fuzz test cases. |
| **THREAT-05** | **Cross-Site Scripting (XSS)**: Adversary inputs malicious JavaScript in notes or profile fields executed in another user's browser. | Tampering | Frontend SPA / Clinical Notes | Session hijacking; client DOM defacement. | React automatically escapes all JSX strings; rich text inputs are sanitized server-side; strict Content Security Policy (CSP) headers applied. | Automated XSS input payload tests asserting strings render as inert text. |
| **THREAT-06** | **Cross-Site Request Forgery (CSRF)**: Malicious third-party website induces a user's browser to execute unauthorized state mutations. | Tampering | API Gateway / Session Cookies | Unauthorized assessment submissions or consent grant creations. | Authentication cookies configured with `SameSite=Strict`. Browser refuses to send session cookie on cross-site requests. | Cross-origin POST test verifying cookie omission by browser. |
| **THREAT-07** | **Sensitive Data Exposure (In-Transit / At-Rest)**: Eavesdropping on network communication or disk storage theft. | Information Disclosure | Transport / Persistent Storage | Compromise of clinical biomarkers and patient credentials. | TLS 1.3 enforced with HSTS (`max-age=31536000`); database volume encrypted at rest via AES-256; data minimization (13 biomarkers only). | SSL Labs A+ SSL configuration audit; encrypted volume verification. |
| **THREAT-08** | **Insecure File Uploads**: Adversary uploads executable scripts or web shells masquerading as images or medical documents. | Tampering | Backend Filesystem | Remote code execution on host server. | **Eliminated by Design:** HeartXAI 2.0 does not accept arbitrary file uploads in v2.0. Clinical briefings are generated dynamically in-memory. | Architecture constraint audit verifying zero multipart file upload routes. |
| **THREAT-09** | **API Abuse & Denial of Service (DoS)**: High-frequency API calls to heavy TreeSHAP computation routes exhaust server CPU/RAM. | Denial of Service | ML Subsystem / Uvicorn | Platform downtime; legitimate patients unable to submit assessments. | Rate limiting on inference endpoints (max 30 req/min per user); TreeSHAP operates in-process in C++ ($< 25\text{ms}$). | Locust / k6 load testing under 50 concurrent requests. |
| **THREAT-10** | **Model Input Manipulation / Evasion**: Adversary enters nonsensical biomarkers (e.g. `trestbps = -50`) to crash the ML runtime. | Tampering | Input Validator / ML Pipeline | Server crash; unhandled 500 errors; division by zero. | Pydantic v2 enforces strict clinical range boundaries before vectors reach the ML subsystem. Out-of-distribution values flagged. | Fuzz testing with 1,000 extreme numerical inputs asserting HTTP 422. |
| **THREAT-11** | **Dependency Vulnerabilities (Supply Chain)**: Third-party Python or npm packages contain known CVE vulnerabilities. | Tampering | Runtime Dependencies | Remote code execution; container compromise. | Dependabot vulnerability scanning; weekly `pip-audit` and `npm audit`; pinned dependency versions in `requirements.txt`. | Automated CI security audit asserting zero High or Critical CVEs. |
| **THREAT-12** | **Secrets Exposure**: `SECRET_KEY` or database credentials committed to version control. | Information Disclosure | Git Repository | Global platform compromise; token forgery. | Secrets managed exclusively via environment variables (`.env` excluded in `.gitignore`); runtime validation via `Settings`. | Git pre-commit secret scanner (TruffleHog / GitGuardian) in CI. |
| **THREAT-13** | **Improper Logging of PHI / Passwords**: Sensitive biomarkers or plaintext passwords leaked into application log files. | Information Disclosure | Structured Logger / Syslog | Compliance violation; internal data exposure to log aggregation services. | Passwords never logged; logger formats exclude sensitive payload dumps; structured fields log entity IDs and timestamps only. | Automated log scanner asserting zero instances of `password` or raw vitals in logs. |

---

## 4. Verification Checkpoint & Audit Integrity

- **Immutable Audit Logging:** All state mutations and clinical record views write to an append-only `audit_logs` table. Database triggers disallow any SQL `UPDATE` or `DELETE` statements on this table.
- **HIPAA § 164.312 Alignment:** Fully complies with technical safeguards (Access Control, Audit Controls, Integrity, Person Authentication, Transmission Security).
