# HeartXAI 2.0 — Consolidated Project Risk Register
**Document ID:** HX-PR-015  
**Version:** 1.0.0  
**Phase:** 12 — Final Pre-Implementation Audit, Architecture Consolidation & Master Development Roadmap  
**Author:** Technical Program Manager & Application Security Architect  
**Status:** Approved for Implementation Planning  
**Date:** November 2026  

---

## 1. Executive Summary

This register consolidates all identified technical, clinical, security, and operational risks across HeartXAI 2.0. Each risk is evaluated using a quantitative Risk Priority Number ($\text{RPN} = \text{Probability} \times \text{Impact}$, scaled 1 to 25), with assigned ownership, mitigation strategies, and monitoring protocols.

---

## 2. Risk Evaluation Matrix

```
Probability Scale: 1 (Very Rare) to 5 (Almost Certain)
Impact Scale:      1 (Negligible) to 5 (Catastrophic / Patient Harm)
Severity (RPN):    Low (1-5), Medium (6-12), High (15-20), Critical (25)
```

```
+---------------------------------------------------------------------------------------------------------------------------------------+
|                                              CONSOLIDATED PROJECT RISK REGISTER                                                       |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| ID | Risk Description     | Prob | Imp  | RPN | Mitigation Strategy                                | Owner            | Status        |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R1 | **Conflation of CAD  |  3   |  5   | 15  | Enforce strict UI separation: ML predicts Task A   | Healthcare AI    | **Mitigated** |
|    | Detection with 10-Yr |      |      |     | (angiographic stenosis >=50%); prospective risk is | Product Engineer | (Architecture |
|    | Heart Attack Risk**  |      |      |     | isolated to deterministic ACC/AHA rule engine.     |                  | Enforced)     |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R2 | **Uncalibrated Model |  3   |  4   | 12  | Mandate Platt Scaling or Isotonic Regression with  | Senior ML        | **Mitigated** |
|    | Probabilities**      |      |      |     | Brier score <= 0.12 and ECE <= 0.05 verification.  | Research Sci.    | (Plan Locked) |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R3 | **Biologically       |  3   |  4   | 12  | Freeze immutable features (Age, Sex, History);     | ML Validation    | **Mitigated** |
|    | Absurd Counter-      |      |      |     | enforce directional limits and physiological       | Specialist       | (Constraints  |
|    | factual Scenarios**  |      |      |     | floors (BP >= 90 mmHg, Chol >= 120 mg/dL).         |                  | Defined)      |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R4 | **Insecure Direct    |  3   |  5   | 15  | Automated anti-IDOR dependency on all endpoints:   | AppSec           | **Mitigated** |
|    | Object References    |      |      |     | verify `current_user.id == patient_id` or valid    | Architect        | (Dependency   |
|    | (IDOR) PHI Breach**  |      |      |     | signed consent grant before querying DB.           |                  | Implemented)  |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R5 | **In-Memory Token    |  2   |  4   |  8  | Short-lived access tokens (15m) in client memory;  | Staff Backend    | **Mitigated** |
|    | Theft / XSS Attack** |      |      |     | HttpOnly SameSite=Lax refresh cookies; strict CSP  | Engineer         | (Security     |
|    |                      |      |      |     | headers disallowing inline script execution.       |                  | Standardized) |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R6 | **SQLite/Postgres    |  2   |  4   |  8  | Strictly prohibit SQLite in test suites; mandate   | Principal QA     | **Mitigated** |
|    | Semantic Mismatch**  |      |      |     | real PostgreSQL 16 container via Docker/Testclient.| Architect        | (Policy Set)  |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R7 | **Scope Creep /      |  4   |  3   | 12  | Enforce strict 20-milestone roadmap; defer EHR     | Technical        | **Active**    |
|    | Premature Enterprise |      |      |     | FHIR, live insurance APIs, and telehealth to       | Program Manager  | (Milestone    |
|    | Feature Inclusion**  |      |      |     | post-MVP releases.                                 |                  | Gates)        |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R8 | **Hosting Cost       |  4   |  2   |  8  | Implement dual-profile infrastructure: start on    | DevOps           | **Pending**   |
|    | Overruns on Cloud**  |      |      |     | Tier A (VPS, ~$20/mo) and scale to Tier B (AWS RDS)| Architect        | (User Sign-Off|
|    |                      |      |      |     | only when user volume warrants.                    |                  | Required)     |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R9 | **Unit Conversion    |  2   |  4   |  8  | Centralized, bi-directional unit conversion engine | Staff Backend    | **Mitigated** |
|    | Lab Value Errors**   |      |      |     | with 100% unit test coverage for mmol/L <-> mg/dL. | Engineer         | (ADR-011)     |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R10| **Disaster Recovery  |  2   |  4   |  8  | Automated nightly AES-256-GCM encrypted database   | DevOps           | **Mitigated** |
|    | Data Loss**          |      |      |     | backups (ADR-012) to offsite storage.              | Engineer         | (ADR-012)     |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
```

---

## 3. High-Priority Risk Deep Dives & Action Plans

### 3.1 Risk R1: Conflation of CAD Detection with 10-Year Heart Attack Risk (RPN = 15)
- **Root Cause:** Popular health media and amateur data science repositories frequently mislabel the Cleveland dataset as a "heart disease predictor" that forecasts future events.
- **Action Plan:** All user interfaces, PDF reports, and educational copy must state that the model estimates cross-sectional angiographic CAD likelihood. In Milestone 14, if 10-year risk is displayed, it must run exclusively on the ACC/AHA Pooled Cohort Equation engine under a distinct heading.

### 3.2 Risk R4: Insecure Direct Object References (IDOR) PHI Breach (RPN = 15)
- **Root Cause:** Developers query database models using path parameters (e.g., `/patients/{id}/assessments`) without validating that the authenticated session owns that record.
- **Action Plan:** The core repository architecture introduces a mandatory FastAPI dependency `verify_patient_access`. Direct database queries by ID without this dependency are rejected in code review and flagged by static analysis.

### 3.3 Risk R8: Hosting Cost Overruns (RPN = 8)
- **Root Cause:** Enterprise cloud architectures (AWS RDS Multi-AZ, ECS Fargate, ALB) incur fixed baseline costs of $\$140\text{--}\$250/\text{month}$ regardless of traffic.
- **Action Plan:** The team has prepared a Docker Compose configuration for a minimal VPS (Tier A: Hetzner / DigitalOcean, 4 vCPU, 8 GB RAM, $\approx \$20/\text{month}$) capable of serving 500+ daily assessments. Scaling to AWS Cloud (Tier B) is deferred until user demand justifies the expenditure.
