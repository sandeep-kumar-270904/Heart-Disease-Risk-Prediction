# HeartXAI 2.0 — Final Architecture Consistency Audit
**Document ID:** HX-PR-006  
**Version:** 1.0.0  
**Phase:** 12 — Final Pre-Implementation Audit, Architecture Consolidation & Master Development Roadmap  
**Author:** Principal Software Architect & Staff Backend Engineer  
**Status:** Approved for Implementation Planning  
**Date:** November 2026  

---

## 1. Executive Summary

A successful software implementation requires zero ambiguity between architectural layers. Inconsistencies between frontend TypeScript interfaces, FastAPI Pydantic request models, PostgreSQL database columns, and ML feature arrays create runtime exceptions, silent data corruption, and security vulnerabilities.

This document presents the cross-layer consistency audit across all tiers of HeartXAI 2.0, establishes the canonical data dictionary, verifies API route coverage, and documents the resolution of all identified interface discrepancies.

---

## 2. Cross-Layer Data Field Reconciliation

The table below audits every clinical biomarker across all four architectural tiers, establishing the single source of truth:

```
+-------------------------------------------------------------------------------------------------------------------------------+
|                                            CANONICAL CROSS-LAYER DATA DICTIONARY                                              |
+---------------------+-------------------------+-------------------------+-------------------------+---------------------------+
| Clinical Concept    | Frontend TypeScript     | FastAPI Pydantic Schema | PostgreSQL DB Column    | XGBoost Feature Vector    |
+---------------------+-------------------------+-------------------------+-------------------------+---------------------------+
| Age                 | `age: number`           | `age: int` (20-100)     | `age INTEGER NOT NULL`  | `age: float`              |
| Sex / Gender        | `sex: "male"|"female"`  | `sex: SexEnum` (0/1)    | `sex INTEGER NOT NULL`  | `sex: float` (0.0/1.0)    |
| Chest Pain Type     | `chestPainType: CPType` | `chest_pain_type: int`  | `cp INTEGER NOT NULL`   | `cp: float` (1.0-4.0)     |
| Resting BP          | `restingBP: number`     | `resting_bp: int`       | `trestbps INTEGER`      | `trestbps: float` (mmHg)  |
| Serum Cholesterol   | `cholesterol: number`   | `serum_cholesterol: int`| `chol INTEGER`          | `chol: float` (mg/dL)     |
| Fasting Blood Sugar | `fastingSugarGT120: b`  | `fbs_gt_120: bool`      | `fbs INTEGER` (0/1)     | `fbs: float` (0.0/1.0)    |
| Resting ECG         | `restingECG: ECGType`   | `resting_ecg: int`      | `restecg INTEGER`       | `restecg: float` (0.0-2.0)|
| Max Heart Rate      | `maxHeartRate: number`  | `max_heart_rate: int`   | `thalach INTEGER`       | `thalach: float` (bpm)    |
| Exercise Angina     | `exerciseAngina: bool`  | `exercise_angina: bool` | `exang INTEGER` (0/1)   | `exang: float` (0.0/1.0)  |
| ST Depression       | `stDepression: number`  | `st_depression: float`  | `oldpeak NUMERIC(4,2)`  | `oldpeak: float` (mm)     |
| ST Slope            | `stSlope: SlopeType`    | `st_slope: int`         | `slope INTEGER`         | `slope: float` (1.0-3.0)  |
| Major Vessels (0-3) | `majorVessels: number`  | `num_major_vessels: int`| `ca INTEGER`            | `ca: float` (0.0-3.0)     |
| Thalassemia Status  | `thalassemia: ThalType` | `thalassemia: int`      | `thal INTEGER`          | `thal: float` (3, 6, 7)   |
+---------------------+-------------------------+-------------------------+-------------------------+---------------------------+
```

### 2.1 Mapping Layer Invariant
Pydantic v2 data models act as the canonical mediator. The API layer accepts readable camelCase or snake_case JSON from the frontend, normalizes units, maps fields to model features via a dedicated transformation pipeline (`InferenceFeatureExtractor`), and serializes to the database using SQLAlchemy 2.0 ORM mappings.

---

## 3. End-to-End API Route Coverage Verification

Every frontend capability has been traced to a concrete, validated FastAPI endpoint:

| Functional Area | Frontend Client Method | HTTP Method & Path | FastAPI Route Handler | Database Operations |
| :--- | :--- | :--- | :--- | :--- |
| **Authentication** | `authService.login()` | `POST /api/v1/auth/login` | `routes.auth.login` | Read `users`, verify Argon2id, issue JWT + HttpOnly refresh cookie. |
| **Session Refresh**| `authService.refresh()`| `POST /api/v1/auth/refresh` | `routes.auth.refresh` | Validate refresh cookie in Redis, rotate token, issue new access JWT. |
| **User Profile** | `patientService.getMe()` | `GET /api/v1/patients/me` | `routes.patients.get_me` | Read `patients` joined with `users`. Anti-IDOR enforced by token `sub`. |
| **Intake Assessment**| `intakeService.submit()`| `POST /api/v1/assessments` | `routes.assessments.create`| Validate biomarkers, invoke in-process ML worker, store `assessments`. |
| **TreeSHAP Details**| `intakeService.getSHAP()`| `GET /api/v1/assessments/{id}/shap`| `routes.assessments.get_shap`| Read cached SHAP payload from `assessments.shap_values` JSONB. |
| **Counterfactuals** | `intakeService.getCF()` | `GET /api/v1/assessments/{id}/counterfactuals`| `routes.assessments.get_cf` | Read cached DiCE scenarios from `assessments.counterfactuals` JSONB. |
| **Assessment History**| `historyService.list()` | `GET /api/v1/assessments` | `routes.assessments.list` | Filter `assessments` by authenticated `patient_id`, ordered by date DESC. |
| **Doctor Directory**| `directoryService.search()`| `GET /api/v1/directory/doctors` | `routes.directory.search_doctors`| Query `doctors` with geo-distance and specialty filters. |
| **Consent Grants** | `consentService.create()` | `POST /api/v1/consents` | `routes.consents.create_grant` | Insert `consent_grants` with cryptographic token and 72-hour expiry. |

---

## 4. Prioritized Architecture Correction Register

During the Phase 12 audit, minor potential interface mismatches were evaluated and resolved. The table below documents their final resolution:

```
+-----------------------------------------------------------------------------------------------------------------------+
|                                      ARCHITECTURE CORRECTION REGISTER                                                 |
+----+--------------------------------+----------+-------------------------------------------------------+--------------+
| ID | Description of Potential Issue | Severity | Resolution Implemented                               | Audit Status |
+----+--------------------------------+----------+-------------------------------------------------------+--------------+
| C1 | Thalassemia coding difference: | Medium   | Standardized: UCI codes 3 (Normal), 6 (Fixed Defect), | Resolved in  |
|    | raw UCI uses 3, 6, 7 while     |          | 7 (Reversible Defect) mapped explicitly to Enum in    | Pydantic v2  |
|    | frontend proposed 1, 2, 3.     |          | Pydantic layer. Frontend sends strings; API translates.| Schemas      |
+----+--------------------------------+----------+-------------------------------------------------------+--------------+
| C2 | Timestamp representation:      | Low      | Mandated ISO 8601 UTC strings (`YYYY-MM-DDTHH:MM:SSZ`)| Standardized |
|    | Unix seconds vs. ISO 8601 UTC. |          | across all JSON payloads. DB uses `TIMESTAMPTZ`.      | in ADR-002   |
+----+--------------------------------+----------+-------------------------------------------------------+--------------+
| C3 | Error response envelope format:| Medium   | Mandated RFC 7807 Problem Details:                    | Enforced via |
|    | Inconsistent error JSON shapes.|          | `{"type", "title", "status", "detail", "instance"}`.   | Middleware   |
+----+--------------------------------+----------+-------------------------------------------------------+--------------+
| C4 | Anti-IDOR Authorization Check: | High     | FastAPI dependency `get_current_active_patient`       | Verified in  |
|    | Risk of users viewing others'  |          | validates that `{patient_id}` in path matches the     | Security     |
|    | assessment data.               |          | authenticated JWT `sub` or an active `consent_grant`. | Blueprint    |
+----+--------------------------------+----------+-------------------------------------------------------+--------------+
```

---

## 5. Architectural Complexity Assessment

The audit explicitly reviewed whether the architecture has been over-engineered:
- **Verdict on Microservices:** The modular monolith (ADR-001) avoids microservice networking overhead while maintaining clean internal boundaries.
- **Verdict on Message Queues:** In-process C++ inference via XGBoost C-API executes in $<2\text{ ms}$, eliminating the need for Celery/RabbitMQ for synchronous risk assessments.
- **Verdict on Database Engine:** Single PostgreSQL 16 cluster with JSONB satisfies both relational entity needs and document-style ML explanation caching without requiring a secondary document database (e.g., MongoDB).
