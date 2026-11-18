# AUTHORIZATION AND PATIENT DATA ISOLATION SPECIFICATION

**Document Reference:** `docs/security/AUTHORIZATION_AND_PATIENT_ISOLATION.md`  
**Phase:** 09 — Security, Privacy, Data Protection & Threat Modelling  
**Status:** Approved Technical Design  
**Author:** Principal Security Architect & Data Governance Lead  
**Traceability:** FR-USER-*, FR-PRED-*, NFR-SEC-02, NFR-PRIV-01, ADR-009, ADR-011  

---

## 1. Executive Summary & Core Tenets

In healthcare systems, authorization failures lead directly to catastrophic personal health information (PHI) leaks, regulatory penalties, and loss of patient trust. HeartXAI 2.0 implements a **Dual-Layer Authorization Architecture**:
1. **Role-Based Access Control (RBAC):** Restricts high-level API route families and administrative operations based on discrete user roles.
2. **Attribute-Based Resource Ownership (ABAC):** Verifies that the authenticated subject possesses legitimate, explicit ownership or consent rights over the specific entity requested.

> [!IMPORTANT]
> **Anti-Pattern Rejection:**  
> Hiding a button, masking a menu item, or redirecting in React does **NOT** constitute security. Every single API route, database query, and report download independently enforces authorization on the server.

---

## 2. User Roles and Permission Matrix

HeartXAI defines three discrete user roles within `UserRole(str, Enum)`:

1. **`PATIENT`:** Standard individual user assessing their cardiovascular metrics, viewing their own historical predictions, managing personal consent, and generating their own clinical reports.
2. **`CLINICIAN` (Healthcare Provider):** Verified healthcare professional accessing patient assessment summaries **only** when an active, time-bounded consent grant has been delegated by the patient.
3. **`ADMIN`:** System administrator managing application infrastructure, monitoring operational health, reviewing audit logs, and managing country directory configurations. Administrators have **zero** default access to patient clinical predictions or raw medical files.

### 2.1 Role-Permission Matrix

| Resource / Action | Endpoint / Operation | `PATIENT` | `CLINICIAN` | `ADMIN` |
| :--- | :--- | :---: | :---: | :---: |
| **Authentication & Profile** | `GET /api/v1/users/me` | Own Profile | Own Profile | Own Profile |
| **Update Personal Info** | `PATCH /api/v1/users/me` | Own Profile | Own Profile | Own Profile |
| **Delete Personal Account** | `DELETE /api/v1/users/me` | Own Account | Own Account | Own Account |
| **Submit Prediction** | `POST /api/v1/predictions` | Permitted | Permitted (for patient) | Denied |
| **List Predictions** | `GET /api/v1/predictions` | Own List Only | Consented Patients Only | Denied |
| **Read Prediction Detail** | `GET /api/v1/predictions/{id}` | Own Record Only | Consented Patient Only | Denied (403) |
| **Delete Prediction Record** | `DELETE /api/v1/predictions/{id}` | Own Record Only | Denied | Denied (403) |
| **Download Clinical Report** | `GET /api/v1/reports/{id}` | Own Report Only | Consented Patient Only | Denied (403) |
| **Upload Medical Document** | `POST /api/v1/files/upload` | Own Files | Denied | Denied |
| **Manage Consents** | `POST /api/v1/consent` | Own Grants | View Received Grants | Denied |
| **System Health & Metrics** | `GET /api/v1/admin/health` | Denied (403) | Denied (403) | Permitted |
| **View Audit Trail** | `GET /api/v1/admin/audit-logs` | Denied (403) | Denied (403) | Permitted (Scrubbed) |
| **Configure Country Modules** | `PATCH /api/v1/admin/country-config`| Denied (403) | Denied (403) | Permitted |
| **Emergency Clinical Override** | `POST /api/v1/admin/emergency-audit` | Denied (403) | Permitted (Special Audit) | Denied |

---

## 3. Patient Data Isolation & Anti-IDOR Protections

Insecure Direct Object Reference (IDOR) occurs when an application uses user-supplied input to access an object directly without verifying authorization.

### 3.1 Backend Dependency Guard (`app/api/deps.py`)

Every endpoint accepting a resource identifier (`prediction_id`, `report_id`, `file_id`) resolves ownership through reusable FastAPI dependencies:

```python
async def get_current_patient_prediction(
    prediction_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Prediction:
    """Enforce strict patient ownership or verified clinician consent."""
    stmt = select(Prediction).where(Prediction.id == prediction_id)
    result = await db.execute(stmt)
    prediction = result.scalar_one_or_none()

    if not prediction:
        # Return 404 to avoid leaking existence of IDs
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction record not found"
        )

    # 1. Direct Patient Ownership Check
    if prediction.user_id == current_user.id:
        return prediction

    # 2. Verified Clinician Consent Delegation Check
    if current_user.role == UserRole.CLINICIAN:
        consent_valid = await verify_clinician_consent(
            db, 
            patient_id=prediction.user_id, 
            clinician_id=current_user.id
        )
        if consent_valid:
            return prediction

    # 3. Unauthorized Access Rejection
    # Return 404 rather than 403 to prevent enumeration attacks
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Prediction record not found"
    )
```

### 3.2 Database-Level Isolation (Row-Level Security Architecture)

To establish defense-in-depth, PostgreSQL Row-Level Security (RLS) can be enabled on sensitive tables:

```sql
-- Enable RLS on predictions table
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;

-- Policy: Patients can only select their own records
CREATE POLICY patient_isolation_policy ON predictions
    FOR ALL
    TO heartxai_app
    USING (user_id = NULLIF(current_setting('app.current_user_id', true), '')::integer);
```

When the application connection pool checks out a session, it executes `SET LOCAL app.current_user_id = :user_id`. Even if an engineer accidentally writes a query without a `WHERE user_id = :id` clause, the database engine transparently filters rows out.

---

## 4. Segregation of Administrative Duties

System administrators must **never** possess blanket access to personal health information:
1. **Zero Direct PHI Access:** Administrative dashboards display aggregate operational statistics (e.g. system throughput, total prediction counts, error rates, average latency, worker CPU load), never individual patient risk profiles or clinical inputs.
2. **Database Console Isolation:** Production database administrative access is restricted to encrypted bastion hosts requiring multi-party approval and ephemeral SSH certificates.
3. **Emergency Clinical Override ("Break-Glass"):** If a hospital emergency requires immediate access to an incapacitated patient's records:
   - Only a verified clinician can trigger the break-glass endpoint.
   - The override requires inputting a verified clinical justification and institutional ticket ID.
   - The action immediately triggers a high-priority alert to the compliance officer and logs an indelible record in the append-only audit trail.

---

## 5. Privilege Escalation Prevention

1. **Role Immutability on Self-Update:** When a user calls `PATCH /api/v1/users/me`, the Pydantic schema strictly excludes the `role`, `is_superuser`, and `is_verified` fields. Submitting extra fields results in schema validation errors or silent stripping.
2. **Administrative Role Provisioning:** Roles can only be modified through dedicated administrative endpoints (`PATCH /api/v1/admin/users/{id}/role`), protected by administrative RBAC guards and requiring secondary MFA verification.
