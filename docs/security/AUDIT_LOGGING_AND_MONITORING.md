# AUDIT LOGGING AND SECURITY MONITORING SPECIFICATION

**Document Reference:** `docs/security/AUDIT_LOGGING_AND_MONITORING.md`  
**Phase:** 09 — Security, Privacy, Data Protection & Threat Modelling  
**Status:** Approved Technical Design  
**Author:** Security Operations Lead & Compliance Architect  
**Traceability:** NFR-SEC-06, NFR-PRIV-01, ADR-009, ADR-011  

---

## 1. Executive Summary & Auditing Philosophy

In healthcare technology, audit logs are not merely debugging artifacts; they constitute legally binding forensic ledgers used to investigate data breaches, establish clinical chain of custody, prove patient consent compliance, and detect active adversarial intrusions.

HeartXAI 2.0 implements a **Zero-Leakage, Tamper-Evident Security Logging Architecture**:
1. Captures all authentication, authorization, clinical access, prediction, and administrative events.
2. Centralized scrubbing pipeline preventing passwords, JWTs, credit cards, or raw health measurements from contaminating logs.
3. Immutable append-only storage protected against modification or deletion by application users.
4. Real-time SIEM integration with automated anomaly alerting.

---

## 2. Security Event Taxonomy & Coverage

The audit logging subsystem captures twelve mandatory categories of security events:

| Event Code | Event Category | Trigger Scenario | Severity | Logged Context |
| :--- | :--- | :--- | :---: | :--- |
| `AUTH_LOGIN_SUCCESS` | Authentication | User logs in successfully | INFO | User ID, Client IP Hash, User-Agent, MFA used |
| `AUTH_LOGIN_FAILED` | Authentication | Bad password or unknown email | WARNING | Submitted Email Hash, Client IP, Failure Reason |
| `AUTH_LOGOUT` | Authentication | Explicit user logout | INFO | User ID, Session Age, Token Family Revoked |
| `AUTH_PASSWORD_RESET`| Account Security | Password reset link requested / completed | NOTICE | Target User ID, Client IP, Reset Token Hash |
| `USER_PROFILE_UPDATED`| Account Security| Name, email, or settings modified | INFO | User ID, Fields Changed (Values masked) |
| `AUTHZ_ROLE_CHANGED` | Privilege Mgmt | Admin promotes user to Clinician/Admin | CRITICAL | Admin ID, Target User ID, Old Role, New Role |
| `PRED_RECORD_VIEWED` | Patient Access | Patient or doctor reads prediction | INFO | Viewer ID, Owner ID, Prediction ID, Consent ID |
| `PRED_EVALUATED` | Clinical Flow | Patient runs ML prediction model | INFO | User ID, Model Version, Latency ms, Status |
| `REPORT_DOWNLOADED` | Document Access | Patient/clinician downloads PDF report | INFO | Downloader ID, Report ID, File Hash, Presigned URL ID |
| `CONSENT_MODIFIED` | Privacy Rights | Consent granted or revoked | NOTICE | User ID, Consent Type, Version, Grant Status |
| `DATA_RIGHT_ERASURE` | Privacy Rights | Patient requests account deletion | CRITICAL | User ID, Request IP, Purge Confirmation Hash |
| `SEC_ANOMALY_TRIGGER`| Intrusion / Abuse | Rate limit breach, IDOR scan, SSRF block | HIGH | Attacking IP, Target Route, Block Reason, Correlation ID |

---

## 3. PII & PHI Redaction Filter (Scrubbing Pipeline)

Logging plaintext passwords, tokens, or medical vitals violates healthcare privacy laws and creates secondary breach vulnerabilities. HeartXAI routes all logs through a centralized redaction middleware (`app/core/logging.py`):

```python
import re
from typing import Any, Dict

# Centralized Sensitive Pattern Scrubber
SCRUB_PATTERNS = [
    (re.compile(r'"password"\s*:\s*"[^"]+"', re.IGNORECASE), '"password": "[REDACTED]"'),
    (re.compile(r'"token"\s*:\s*"[^"]+"', re.IGNORECASE), '"token": "[REDACTED]"'),
    (re.compile(r'"authorization"\s*:\s*"[^"]+"', re.IGNORECASE), '"authorization": "[REDACTED]"'),
    (re.compile(r'"trestbps"\s*:\s*[0-9.]+', re.IGNORECASE), '"trestbps": "[MASKED_PHI]"'),
    (re.compile(r'"chol"\s*:\s*[0-9.]+', re.IGNORECASE), '"chol": "[MASKED_PHI]"'),
]

def scrub_sensitive_payload(message: str) -> str:
    """Scrub passwords, tokens, and direct health measurements from log output."""
    for pattern, replacement in SCRUB_PATTERNS:
        message = pattern.sub(replacement, message)
    return message
```

---

## 4. Structured Log Format & Correlation Tracing

Logs are emitted exclusively as machine-parseable JSON lines (`JSONL`) adhering to the Cloud Native Computing Foundation (CNCF) log standards:

```json
{
  "timestamp": "2026-11-18T05:54:00.124Z",
  "level": "INFO",
  "event_code": "PRED_RECORD_VIEWED",
  "correlation_id": "req-8f4b2a19-9132-47ef-8b20-13f56d9a24ec",
  "actor": {
    "user_id": 104,
    "role": "CLINICIAN",
    "ip_hash": "a1b2c3d4e5f67890123456789abcdef0",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
  },
  "action": {
    "method": "GET",
    "endpoint": "/api/v1/predictions/42",
    "status_code": 200
  },
  "resource": {
    "entity_type": "prediction",
    "entity_id": 42,
    "owner_user_id": 101,
    "consent_verified_id": 12
  },
  "environment": "production",
  "service": "heartxai-api",
  "version": "2.0.0"
}
```

Every incoming HTTP request receives a unique `X-Correlation-ID` generated at the reverse proxy. This ID propagates across FastAPI route handlers, background worker threads, and database queries, allowing instant end-to-end trace correlation during forensic investigations.

---

## 5. Log Integrity, Access Restrictions & Retention Policy

### 5.1 Tamper-Resistance Architecture
1. **Append-Only PostgreSQL Table:** Audit records are written to `audit_logs` via database triggers with `SECURITY DEFINER`. The runtime application database user has zero `UPDATE` or `DELETE` permissions on this table.
2. **Cryptographic Log Forwarding:** Logs are streamed in real-time over TLS to an off-site, immutable write-once log bucket (e.g. AWS S3 with Object Lock or CloudWatch Logs with retention lock). Even if an attacker achieves root on the backend server, historical log records cannot be modified or deleted.

### 5.2 Access Control & Least Privilege
- **Zero General Developer Access:** Developers and standard administrators cannot browse raw audit logs.
- **Auditor Role Only:** Access is restricted to designated Compliance Officers and Security Operations leads via authenticated SIEM consoles (e.g. Datadog / Elasticsearch) with MFA.

### 5.3 Retention Schedule
- **Security & Access Logs:** Retained for **7 years** in cold, encrypted storage to satisfy statutory healthcare record-keeping and medico-legal liability requirements.
- **Ephemeral Debug Traces:** Non-security application debug logs retained for 30 days before automated lifecycle purging.

---

## 6. Real-Time Security Monitoring & Alerting Rules

HeartXAI integrates automated threshold monitors triggering high-priority notifications (PagerDuty / Slack SecOps channel):

| Alert Rule Name | Detection Condition | Severity | Automated Response |
| :--- | :--- | :---: | :--- |
| **Brute Force Spike** | $\ge 15$ failed logins from single IP in $5\text{ mins}$ | HIGH | IP banned for 1 hour at WAF; alert dispatched. |
| **IDOR Probe Sequence** | $\ge 5$ HTTP 404/403 errors on sequential IDs from single user | CRITICAL | User session suspended; security operations paged. |
| **Admin Privilege Grant** | Any execution of `AUTHZ_ROLE_CHANGED` | CRITICAL | Instant email alert sent to Chief Information Security Officer. |
| **Model Integrity Failure** | Startup HMAC mismatch or `ModelIntegrityException` | CRITICAL | Container startup halted; release aborted. |
| **SSRF Probe Attempt** | Outbound request blocked to private IP range | HIGH | Firewall block logged; originating IP quarantined. |
