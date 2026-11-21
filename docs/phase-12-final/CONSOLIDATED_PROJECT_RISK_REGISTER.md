# HeartXAI 2.0 — Consolidated Project Risk Register
**Document ID:** HX-PR-015  
**Version:** 2.0.0 (Phase 12.1 Revision)  
**Phase:** 12.1 — Final Audit Corrections, Clinical Scope Resolution & Implementation Authorization  
**Author:** Technical Program Manager & Application Security Architect  
**Status:** Reconciled Risk Register — Mitigations Enforced in Roadmap  
**Date:** November 2026  

---

## 1. Executive Summary

This register consolidates all identified technical, clinical, security, and operational risks across HeartXAI 2.0 following the Phase 12.1 audit. Each risk is evaluated using a quantitative Risk Priority Number ($\text{RPN} = \text{Probability} \times \text{Impact}$, scaled 1 to 25), with designated ownership, concrete mitigations, and monitoring protocols.

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
| ID | Risk Description     | Prob | Imp  | RPN | Concrete Mitigation Strategy                       | Owner            | Status        |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R1 | **Conflation of CAD  |  1   |  5   |  5  | Complete removal of Task B from MVP. Model         | Healthcare AI    | **Mitigated** |
|    | Classification with  |      |      |     | strictly bounded to Task A experimental dataset    | Research Lead    | (Scope Locked)|
|    | 10-Yr Future Risk**  |      |      |     | classification; no 10-year risk calculator in MVP. |                  |               |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R2 | **Uncalibrated Model |  2   |  4   |  8  | Mandatory Platt Scaling or Isotonic Regression with| Senior ML        | **Mitigated** |
|    | Probabilities**      |      |      |     | Brier score <= 0.12 and ECE <= 0.05 verification.  | Research Sci.    | (Plan Locked) |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R3 | **Biologically       |  2   |  4   |  8  | Freeze immutable features (Age, Sex, History);     | ML Validation    | **Mitigated** |
|    | Absurd Counter-      |      |      |     | enforce directional limits and physiological       | Specialist       | (Constraints  |
|    | factual Scenarios**  |      |      |     | floors (BP >= 90 mmHg, Chol >= 120 mg/dL).         |                  | Defined)      |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R4 | **Insecure Direct    |  2   |  5   | 10  | Automated anti-IDOR dependency on all endpoints:   | AppSec           | **Mitigated** |
|    | Object References    |      |      |     | verify `current_user.id == patient_id` or active   | Architect        | (Dependency   |
|    | (IDOR) PHI Breach**  |      |      |     | signed consent grant before querying DB.           |                  | Pattern Set)  |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R5 | **In-Memory Token    |  2   |  4   |  8  | Short-lived access tokens (15m) in client memory;  | Staff Backend    | **Mitigated** |
|    | Theft / XSS Attack** |      |      |     | HttpOnly SameSite=Lax refresh cookies; strict CSP  | Engineer         | (Security     |
|    |                      |      |      |     | headers disallowing inline script execution.       |                  | Standardized) |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R6 | **SQLite / PostgreSQL|  2   |  4   |  8  | Decommission SQLite for integration tests; mandate | Principal QA     | **Mitigated** |
|    | Semantic Mismatch**  |      |      |     | real PostgreSQL 16 Docker container in M04.        | Architect        | (Policy Set)  |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R7 | **Scope Creep /      |  2   |  3   |  6  | Enforce strict 20-milestone roadmap; defer EHR     | Technical        | **Mitigated** |
|    | Premature Enterprise |      |      |     | FHIR, live insurance APIs, and telehealth to       | Program Manager  | (Roadmap      |
|    | Feature Inclusion**  |      |      |     | post-MVP research releases.                        |                  | Locked)       |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R8 | **Hosting Cost       |  2   |  2   |  4  | Implement dual-profile infrastructure: start on    | DevOps           | **Mitigated** |
|    | Overruns on Cloud**  |      |      |     | Tier A (VPS, ~$21-$55/mo); defer AWS RDS ($252/mo) | Architect        | (Itemized     |
|    |                      |      |      |     | until user demand justifies expenditure.           |                  | Model Built)  |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R9 | **Unit Conversion    |  1   |  4   |  4  | Centralized, bi-directional unit conversion engine | Staff Backend    | **Mitigated** |
|    | Lab Value Errors**   |      |      |     | with 100% unit test coverage for mmol/L <-> mg/dL. | Engineer         | (ADR-011)     |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R10| **Disaster Recovery  |  2   |  4   |  8  | Automated nightly AES-256-GCM encrypted database   | DevOps           | **Mitigated** |
|    | Data Loss**          |      |      |     | backups (ADR-012) to offsite storage.              | Engineer         | (ADR-012)     |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R11| **Real Patient PHI   |  1   |  5   |  5  | Mandate **100% synthetic demonstration data**      | Healthcare Safety| **Mitigated** |
|    | Breach in Non-Prod** |      |      |     | across all dev, test, and staging environments.    | Consultant       | (Strict Policy|
|    |                      |      |      |     | Zero real patient data permitted without ethics.   |                  | Enforced)     |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R12| **Accessibility      |  2   |  3   |  6  | Target upgraded to WCAG 2.2 AA; automated axe-core | Frontend Quality | **Mitigated** |
|    | Non-Conformance**    |      |      |     | scans integrated into CI; compliance gates in M19. | Lead             | (Target Set)  |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
```

---

## 3. High-Priority Risk Deep Dives & Action Plans

### 3.1 Risk R1: Conflation of CAD Detection with 10-Year Heart Attack Risk (RPN = 5 - Mitigated)
- **Root Cause:** Amateur data science repositories frequently misrepresent the Cleveland catheterization dataset as a prospective cardiovascular risk predictor.
- **Action Plan:** Task B has been completely excised from the MVP scope. Task A is strictly labeled as an experimental dataset classification model. The UI enforces prominent non-diagnostic disclaimers.

### 3.2 Risk R11: Real Patient Health Data Exposure (RPN = 5 - Mitigated)
- **Root Cause:** Developers loading real clinical datasets or testing with live patient records during pre-launch stages.
- **Action Plan:** The project enforces an absolute **100% synthetic data mandate**. A synthetic patient persona generator (`scripts/generate_synthetic_patients.py`) provides test cohorts with randomized, plausible clinical values with zero real-world identity or clinical record link.
