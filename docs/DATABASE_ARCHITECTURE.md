# HeartXAI 2.0 — Database Architecture & Conceptual Schema Design

**Document ID:** HXAI-ARCH-010  
**Version:** 3.0.0  
**Phase:** Phase 3 — System Architecture & Technical Design  
**Status:** Approved  
**Diagram Source:** [`docs/diagrams/erd_conceptual.puml`](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/diagrams/erd_conceptual.puml)  

---

## 1. Database Architecture & Persistence Philosophy

HeartXAI 2.0 requires uncompromising data integrity, ACID transactional guarantees, and strict multi-tenant isolation. The database architecture is designed to satisfy:
1. **Relational Data Integrity:** Foreign keys enforce parent-child dependencies (`users` $\rightarrow$ `assessments` $\rightarrow$ `inference_results` $\rightarrow$ `shap_explanations`), preventing orphaned records.
2. **Patient Data Sovereignty & Isolation:** Records are partitioned logically by `patient_id`. Multi-tenant security rules guarantee that no user can query another individual's clinical biomarkers without an active, explicit consent grant.
3. **Auditability & Append-Only History:** All security, authentication, and clinical data access events are persisted in an immutable `audit_logs` table.
4. **Dual-Engine Operational Resilience:** Standard SQL types allow seamless execution against PostgreSQL 15+ in production containers and SQLite in local developer/testing environments.

---

## 2. Conceptual Entity-Relationship Diagram (ERD)

```mermaid
erDiagram
    users ||--o| patient_profiles : "1 owns 0..1"
    users ||--o{ assessments : "1 creates 0..*"
    users ||--o{ patient_doctor_grants : "1 grants (as patient)"
    users ||--o{ patient_doctor_grants : "1 receives (as doctor)"
    users ||--o{ clinical_notes : "1 writes (as doctor)"
    
    assessments ||--|| inference_results : "1 has 1"
    assessments ||--o{ clinical_notes : "1 receives 0..*"
    inference_results ||--|{ shap_explanations : "1 has 13"
    inference_results ||--o{ counterfactual_profiles : "1 derives 0..*"

    users {
        string id PK
        string email UK
        string hashed_password
        string full_name
        string role
        string clinician_status
        boolean is_active
        datetime last_login_at
        datetime created_at
        datetime updated_at
    }

    patient_profiles {
        string id PK
        string patient_id FK, UK
        date date_of_birth
        string biological_sex
        string preferred_units
        string emergency_contact_name
        string emergency_contact_phone
    }

    assessments {
        string id PK
        string patient_id FK
        string clinician_id FK
        string status
        int age
        int sex
        int cp
        int trestbps
        int chol
        int fbs
        int restecg
        int thalach
        int exang
        float oldpeak
        int slope
        int ca
        int thal
        datetime created_at
    }

    inference_results {
        string id PK
        string assessment_id FK, UK
        string model_version
        float cad_probability
        string cad_risk_tier
        float confidence_interval_low
        float confidence_interval_high
        float ascvd_10yr_risk
        string ascvd_risk_tier
        float base_expected_value
        float raw_decision_margin
        boolean is_out_of_distribution
        datetime computed_at
    }

    shap_explanations {
        string id PK
        string inference_id FK
        string feature_name
        float feature_value
        float shap_value
        int rank_importance
        string directional_impact
        string clinical_interpretation
    }

    counterfactual_profiles {
        string id PK
        string inference_id FK
        float target_risk_threshold
        float achieved_risk_probability
        json modified_biomarkers
        json immutable_biomarkers
        float l1_normalized_distance
        string feasibility_rating
        datetime created_at
    }

    patient_doctor_grants {
        string id PK
        string patient_id FK
        string doctor_id FK
        string access_code
        string status
        datetime granted_at
        datetime expires_at
        datetime revoked_at
    }

    clinical_notes {
        string id PK
        string assessment_id FK
        string author_id FK
        text note_content
        string signoff_status
        datetime signed_at
        datetime created_at
    }

    doctors {
        string id PK
        string doctor_name
        string specialization
        string hospital_name
        string contact_number
        string location
        string email
        boolean telehealth_available
    }

    hospitals {
        string id PK
        string hospital_name
        string facility_type
        string emergency_phone
        string address
        string city
        string state
        string accreditation_details
        boolean has_247_cath_lab
    }

    insurance_policies {
        string id PK
        string provider_name
        string policy_name
        text coverage_summary
        float monthly_premium_est
        int waiting_period_days
        text exclusions_summary
    }

    educational_resources {
        string id PK
        string title
        string biomarker_code
        string summary
        string guideline_source
        text diet_plan_summary
        text exercise_tips_summary
        text lifestyle_guidance
    }

    audit_logs {
        string id PK
        datetime timestamp
        string user_id
        string role
        string action_type
        string resource_id
        string endpoint
        string method
        string ip_address
        int status_code
        float duration_ms
    }

    model_registry {
        string id PK
        string version UK
        string algorithm
        string training_cohort
        float test_auroc
        float brier_score
        string sha256_hash
        datetime deployed_at
        int is_active
    }
```

---

## 3. Entity Classifications & Sensitive Data Isolation

| Entity Name | Sensitivity Tier | Data Classification | Security & Privacy Controls |
| :--- | :--- | :--- | :--- |
| `users` | **Tier 3 (PII)** | Account Credentials | Bcrypt salted hashing (rounds=12); unique index on `email`. |
| `patient_profiles` | **Tier 4 (PHI)** | Demographics | 1:1 foreign key; accessible strictly by owning patient. |
| `assessments` | **Tier 4 (PHI)** | Clinical Biomarkers | Scoped strictly to `patient_id`; cascading deletion on user erasure. |
| `inference_results` | **Tier 4 (PHI)** | Risk Probabilities | Derived from assessment; immutable once computed. |
| `shap_explanations` | **Tier 4 (PHI)** | Local Feature Weights | Exactly 13 rows per inference; mathematical invariance verified. |
| `counterfactual_profiles`| **Tier 4 (PHI)** | Lifestyle Targets | JSON parameter maps; immutable biological traits locked. |
| `patient_doctor_grants` | **Tier 3 (PII)** | Consent Records | Time-bounded; checked by authorization middleware on every doctor request. |
| `clinical_notes` | **Tier 4 (PHI)** | Physician Notes | Attached to assessment; author validated as holding an active grant. |
| `doctors`, `hospitals` | **Tier 1 (PUB)** | Public Directory | Public directory read access; modified only by `ADMIN`. |
| `insurance_policies` | **Tier 1 (PUB)** | Insurance Guides | Public educational access; ACA preventative guidelines. |
| `educational_resources` | **Tier 1 (PUB)** | Clinical Guides | Traceable ACC/AHA guidance; curated content. |
| `audit_logs` | **Tier 2 (ADM)** | Security Forensics | Append-only; disallows SQL `UPDATE` and `DELETE`; retained 6 years. |
| `model_registry` | **Tier 2 (ADM)** | MLOps Lineage | Cryptographic SHA-256 hash verified at boot. |

---

## 4. Multi-Tenant Patient Data Isolation Architecture

To completely eliminate Insecure Direct Object References (IDOR) and cross-tenant data leaks:
1. **Application-Level Scoping:** Every database query for assessments or health profiles mandates `WHERE patient_id = :current_user_id`.
2. **Clinician Authorization Join:** A clinician can query a patient's assessment if and only if an inner join on `patient_doctor_grants` confirms:
   ```sql
   SELECT a.* FROM assessments a
   JOIN patient_doctor_grants g ON a.patient_id = g.patient_id
   WHERE a.id = :assessment_id
     AND g.doctor_id = :current_doctor_id
     AND g.status = 'ACTIVE'
     AND g.expires_at > CURRENT_TIMESTAMP;
   ```
   If no rows match, the API gateway automatically raises HTTP 403 Forbidden.

---

## 5. Strategic Indexing & Query Optimization

| Table | Index Name | Indexed Columns | Index Purpose & Query Optimized |
| :--- | :--- | :--- | :--- |
| `users` | `ix_users_email` | `email` (Unique) | O(1) user lookup during login authentication. |
| `users` | `ix_users_role_status` | `role, clinician_status` | Fast retrieval of pending clinician approval queue. |
| `assessments` | `ix_assessments_patient_created` | `patient_id, created_at` | Optimizes longitudinal historical time-series queries. |
| `inference_results` | `ix_inference_assessment_id` | `assessment_id` (Unique) | Instant 1:1 join with parent assessment. |
| `shap_explanations` | `ix_shap_inference_rank` | `inference_id, rank_importance` | Fast sorted retrieval of top 5 risk contributors. |
| `patient_doctor_grants`| `ix_grants_patient_doctor_status` | `patient_id, doctor_id, status` | Sub-millisecond clinician access grant validation. |
| `audit_logs` | `ix_audit_time_action` | `timestamp, action_type` | Fast chronological log filtering in admin audit portal. |
