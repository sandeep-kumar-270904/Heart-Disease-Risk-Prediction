# HeartXAI 2.0 — Implementation Integrity, Governance Reconciliation and Validation Audit

**Audit Role:** Principal Software Architect, Healthcare AI Safety Reviewer, ML Validation Auditor, Application Security Engineer & Independent Technical Reviewer  
**Repository:** `heartxai-2.0` (`https://github.com/sandeep-kumar-270904/Heart-Disease-Risk-Prediction.git`)  
**Audited Branch & Commit:** `main` at `576413fbd29affcaad08eca3d8d318707d5bb1f0`  
**Audit Date:** 25 November 2026  
**Audit Scope:** Independent integrity, governance, live-infrastructure, ML reproducibility, healthcare safety, Category C privacy, security, accessibility, and deployment verification across Milestones 01–20 without modifying application logic or deploying infrastructure.

---

## Status Legend

- **VERIFIED** — Direct execution or source inspection supports the claim completely within its stated scope.
- **PARTIALLY VERIFIED** — Supporting code/tests exist, but key integration, clinical, statistical, or environmental validation is incomplete.
- **NOT VERIFIED** — Artifact exists or claim was made, without execution evidence against target systems.
- **FAILED** — A concrete discrepancy, bypass, defect, or false representation was directly observed in source or test output.
- **REQUIRES GOVERNANCE APPROVAL** — Stakeholder, physician advisory, institutional ethics (IRB/REC), or regulatory determination is missing or required before reliance.

---

## 1. Executive Assessment

**Overall Verdict: NOT PRODUCTION READY — PROTOTYPE COMPLETE LOCALLY WITH CRITICAL SAFETY, CONSENT, CATEGORY C, AND LIVE-INFRASTRUCTURE BLOCKERS**

A comprehensive application codebase spanning backend (`FastAPI`, SQLAlchemy 2.0, Alembic, XGBoost/TreeSHAP, ReportLab), ML research pipelines (`ml/pipelines/`), and frontend SPA (`React 18`, TypeScript, Tailwind CSS, Zustand, `vitest-axe`) has been implemented and passes **44/44 Python unit/integration tests (on SQLite + in-memory token store doubles)** and **24/24 frontend tests (`jsdom`)**.

However, treating the Milestone 01–20 summary as "completed and deployment-ready" overstates what has actually been validated and masks **six blocking defects/gaps** observed directly in source inspection and environment checks:

1. **[FAILED] Clinician 72-Hour Consent Expiration Bypass (`backend/app/services/assessment_service.py`):** While `/api/v1/consents/doctor/assessments/{id}` checks grant expiry, `authorize_assessment_access()` guarding `/api/v1/assessments/{id}`, `/shap`, `/simulate`, and `/export-pdf` checks only `DoctorGrant.status == "ACTIVE"` and **fails to verify `expires_at` or `revoked_at`**, allowing expired 72-hour grants to remain valid on core assessment routes.
2. **[FAILED] Misrepresented `"95% Confidence Interval"` Heuristic (`backend/app/ml/inference_service.py`, `backend/app/services/export_service.py`, `frontend/src/features/assessment/AssessmentResultsPage.tsx`):** The inference engine calculates `confidence_interval` as a hardcoded constant `[likelihood - 6.5, likelihood + 6.5]` rather than a statistical confidence interval, yet labels it `"95% Confidence Interval"` in exported PDFs and `"95% Interval"` in UI.
3. **[FAILED] Category C Real PHI Technical Enforcement Absent (`backend/app/api/v1/routes/auth.py`, `assessments.py`, `consents.py`):** Despite `SYNTHETIC_DATA_ONLY=true` banners and `is_synthetic=True` database flags, no technical server control blocks real user emails/names during registration, real clinical measurements during intake, or arbitrary identifiable PHI in clinician free-text notes (`note_content`).
4. **[NOT VERIFIED] Zero Live Container, PostgreSQL 16, Redis 7, K6, ZAP, or Playwright E2E Execution:** Although Docker Engine (`29.9.3`) was reachable on the host, **zero** HeartXAI Docker images have been built and **zero** tests executed against real PostgreSQL 16, Redis 7, or Nginx containers. Additionally, `Dockerfile.frontend` lacks SPA `try_files ... /index.html` fallback (causing 404s on client route refreshes), `/health/ready` fails to check Redis/ML readiness, and `backup_encrypted.sh` uses `AES-256-CBC` locally instead of ADR-012's `AES-256-GCM` offsite backup.
5. **[REQUIRES GOVERNANCE APPROVAL] Unreviewed Clinical Thresholds & Incomplete DEC-002 Oversight Tracks:** Emergency red-flag triggers (`resting_bp > 180` or `chest_pain_type == 0 and exercise_angina == 1`), risk tier cutoffs (`30%` / `70%`), and counterfactual bounds lack recorded physician sign-off (`DEC-002` Tracks 1–4 remain open). Furthermore, `PROJECT_DECISION_REGISTER.md` contains contradictory top-level `PENDING` headers alongside Section 4 `APPROVED BY USER`.
6. **[PARTIALLY VERIFIED / FAILED METRIC TARGET] ML Calibration & Numeric FBS Fidelity:** Holdout test 10-bin ECE (`0.1120` on $N=61$) exceeds the provisional `<= 0.05` target; `train_model.py` pairs an 80%-fold OOF Platt scaler with a 100%-train `final_xgb` model and performs global training-split imputation prior to 5-fold CV; and `assessment_service.py` truncates numeric fasting blood sugar on DB readback to hardcoded `130.0` / `95.0` placeholders.

---

## 2. Governance Authorization Reconciliation (`DEC-001` – `DEC-005`)

Inspection of git history (`commit b65bdba7ffb5847b408747f31ca65d6f39559242`, `2026-11-23 23:21:12 +0530`) and conversation transcript (`transcript_full.jsonl`, `step_index: 2189–2190`, `2026-11-23T23:14:49+05:30` to `23:17:36+05:30`) confirms that an explicit interactive UI prompt (`ask_question`) was answered by the user prior to Milestone 01 selecting the bundled Option A recommendation and authorizing Milestone 01 execution.

However, two governance discrepancies exist:
1. **Document Internal Contradiction (`FAILED`):** In [PROJECT_DECISION_REGISTER.md](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/phase-12-final/PROJECT_DECISION_REGISTER.md), line 6 (`Status: Authoritative Reconciled Register — Governance Decisions Pending User Selection`) and line 18 (`Each is strictly marked PENDING USER DECISION`) were left un-updated and contradict Sections 4–5 (`APPROVED BY USER` on `23 November 2026`) in the same file. (Same header text exists in its mirrored copy under `docs/project-readiness/PROJECT_DECISION_REGISTER.md`.)
2. **Downstream Governance Tracks Incomplete (`REQUIRES GOVERNANCE APPROVAL`):** Selecting `DEC-002 Option A` only unlocked *synthetic prototype engineering*; it did **not** complete clinical advisory sign-off, clinical content review, IRB/REC determination for human-participant studies, or regulatory determinations.

| Decision | Original Available Options | Recommended Option | Actual Implementation Assumption | Explicit Approval Evidence Found | Current Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DEC-001** Hosting Profile & Budget | **A:** Tier A Minimal VPS (~\$25–\$55/mo)<br>**B:** Tier B AWS Managed Cloud (~\$250/mo) | **Option A** | Docker Compose stack (`Nginx`, `FastAPI`, `PostgreSQL 16`, `Redis 7.2`) in `infra/docker-compose.yml`; VPS capacity unverified | Bundled `ask_question` UI answer `A1` (`2026-11-23T23:17:36+05:30`, step 2190) + `b65bdba`; mirrored in `PHASE_12_FINAL_OPEN_QUESTIONS.md` & `PROJECT_DECISION_REGISTER.md` (with stale top header) | **PARTIALLY VERIFIED** *(Prototype selection recorded; formal deployment sign-off & empirical VPS sizing pending)* |
| **DEC-002** Clinical Governance Scope | **A:** Multi-Track Phased Governance (4 concurrent tracks)<br>**B:** Pre-coding Institutional / IRB / FDA Q-Sub Gate | **Option A** | Built synthetic MVP without pre-coding IRB; clinical logic implemented without physician sign-off artifact | Bundled `ask_question` UI answer `A1` + `b65bdba` (`2026-11-23`); zero physician/content/IRB/regulatory sign-off artifacts in repo | **REQUIRES GOVERNANCE APPROVAL** *(Tracks 1–4 clinical, content, ethics & regulatory reviews unexecuted)* |
| **DEC-003** Cardiovascular Prediction Scope | **A:** Task A MVP Only (Retrospective UCI Cleveland)<br>**B:** Deterministic Task B (PCE/PREVENT) in MVP | **Option A** | Strictly Task A classification (`ten_year_population_risk_percent = None`; DB `ascvd_*` nullable) | Bundled `ask_question` UI answer `A1` + `b65bdba` + enforced in `assessment_service.py`, schemas, UI, PDF | **VERIFIED** *(User selection + strict code enforcement confirmed; header contradiction noted)* |
| **DEC-004** Geographic Adapter Scope | **A:** Extensible Country Adapter (`US`/`IN`/`GB` synthetic)<br>**B:** US-Only Baseline | **Option A** | `shared/country-profiles.json` + unit converters (`mg/dL` $\leftrightarrow$ `mmol/L`) + synthetic `US`/`IN`/`GB` seeds | Bundled `ask_question` UI answer `A1` + `b65bdba` + `shared/country-profiles.json` metadata disclaimer | **PARTIALLY VERIFIED** *(Architectural pattern implemented; country-level clinical/regulatory readiness unverified per jurisdiction)* |
| **DEC-005** Data Classification & Cat C Policy | **A:** 3-Tier Policy (Cat A research, Cat B synthetic, Cat C prohibited)<br>**B:** Real PHI Pilot (outside MVP scope) | **Option A** | `SYNTHETIC_DATA_ONLY=true` setting & UI watermarks, **without technical server-side blocking of real PHI input** | Bundled `ask_question` UI answer `A1` + `b65bdba`; however technical Category C enforcement is missing on API inputs | **PARTIALLY VERIFIED / FAILED TECHNICAL GATE** *(Policy approved; technical Category C input blocking absent)* |

*(Note: If an organization requires formal signed paper/PR governance records outside the IDE chat widget, `DEC-001`–`DEC-005` should be re-ratified via signed GitHub PR/ADR sign-off prior to any staging exposure, as `PROJECT_DECISION_REGISTER.md` lines 6 & 18 still conflict with Section 4.)*

---

## 3. Actual Implementation Inventory

Re-verified on repository state at commit `576413fbd29affcaad08eca3d8d318707d5bb1f0` during this audit:

| Subsystem | Key Verified Paths | Local Verification Result | Status |
| :--- | :--- | :--- | :--- |
| **Shared Contracts** | `shared/data-dictionary.json`, `shared/country-profiles.json` | Schema parity & Pydantic validation pass in `test_schemas_and_contracts.py` | **VERIFIED** |
| **Backend Core & Errors** | `backend/app/main.py`, `core/{config,database,errors,logging,redis_client,security}.py` | RFC 7807, logging scrubbing, Argon2id, JWT verified in `test_api_health.py`, `test_security.py` | **PARTIALLY VERIFIED** *(Default `SECRET_KEY` lacks prod fail-fast; `/health/ready` omits Redis)* |
| **ORM & Migrations** | `backend/app/models/*.py`, `backend/alembic/versions/001_*.py`, `002_*.py` | Up/down/up & cascades pass on SQLite `PRAGMA foreign_keys=ON`; **PostgreSQL 16 not run** | **PARTIALLY VERIFIED** |
| **API Routes & Services** | `backend/app/api/v1/routes/{auth,assessments,consents,directory,admin,health}.py`, `services/*.py` | 44/44 `pytest` tests pass on SQLite + `InMemoryTokenStore`; consent expiry & `fbs` truncation bugs found | **FAILED (Defects Found)** |
| **ML Pipeline & XAI** | `ml/pipelines/{prepare_data,train_model,evaluate_model}.py`, `backend/app/ml/{inference,shap,counterfactual}_service.py` | Metrics & SHAP margin additivity reproduced (`1.6e-7` diff); holdout `ECE=0.112`, hardcoded CI `±6.5%` | **PARTIALLY VERIFIED** |
| **Frontend SPA & UI** | `frontend/src/components/{ui,layout}/*`, `features/{auth,intake,assessment,directory,doctor,admin}/*` | `tsc --noEmit` 0 errs, `eslint` 0 warnings, `vitest run` 24/24 pass (`vitest-axe` 7 routes), `vite build` 4.21s | **PARTIALLY VERIFIED** |
| **Synthetic Scripts & Bench** | `scripts/generate_synthetic_patients.py`, `seed_synthetic_database.py`, `benchmark_performance.py` | Synthetic schema parity & local microbenchmarks reproducible | **VERIFIED (Local Scope)** |
| **Docker, Nginx, DR & E2E** | `infra/docker/Dockerfile.{backend,frontend}`, `infra/docker-compose.yml`, `infra/nginx/nginx.conf`, `infra/scripts/*`, `tests/e2e/*` | Only `docker compose config` validated syntax; **no image builds, container starts, K6, ZAP, DR, or Playwright runs executed** | **NOT VERIFIED** |

---

## 4. PostgreSQL, Redis & Live Infrastructure Integration Evidence

Direct inspection of host tooling (`docker info`, `docker ps -a`, `docker images`) confirmed that Docker Desktop Engine `29.9.3` is installed and running unrelated workspace containers (`ai_reviewer_db`, `vapt_*`), **but zero HeartXAI images (`heartxai-backend`, `heartxai-frontend`), containers, or volumes exist.** Neither `psql` nor `redis-server` is installed on the host.

### A. Executed Successfully Against Real Services
- **None.** Zero tests or health checks executed against live `PostgreSQL 16`, live `Redis 7.2`, live `Nginx 1.26`, or running Docker containers.

### B. Executed Using Mocks, SQLite, or Test Doubles
- **Database Schema & Alembic Migrations (`test_alembic_upgrade_downgrade_upgrade_cycle` in `backend/tests/test_migrations_and_seeding.py`):** Executed against temporary **SQLite** file database (`sqlite:///.../migration_test.db`), NOT PostgreSQL 16.
- **ORM Foreign Keys, Constraints & Assessment/Consent CRUD (`backend/tests/conftest.py`, `test_database_models.py`, `test_directory_consents_admin.py`):** Executed against `sqlite:///:memory:` with `StaticPool` and `PRAGMA foreign_keys=ON`. As documented in `PROJECT_DECISION_REGISTER.md` (`REJ-004`), SQLite lacks native PostgreSQL `JSONB`, row-level locks (`SELECT FOR UPDATE`), and concurrent transactional MVCC semantics.
- **Auth Rotation, Replay Detection & Redis Fail-Closed (`backend/tests/test_auth.py`):**
  - `test_register_login_refresh_replay_detection_and_logout` swaps `get_token_store` to **`InMemoryTokenStore`** (a Python `dict`/`set` test double).
  - `test_redis_fail_closed_when_unavailable` monkeypatches `RedisTokenStore._client.setex` to raise `RedisConnectionError`. Real `redis-py` network socket communication, `SETEX` TTL expiry in Redis 7, and recovery after Redis reconnection were **never tested live**.

### C. Not Executed
- `PostgreSQL 16` live migrations (`001_initial_schema`, `002_milestone_04_governance_geo`), constraints, JSONB persistence, and concurrent writes — **NOT VERIFIED**.
- `Redis 7.2` live `SETEX`/`GET`/`EXISTS`/`DEL` key rotation, TTL expiration, AOF persistence (`--appendonly yes`), and recovery — **NOT VERIFIED**.
- `Dockerfile.backend` & `Dockerfile.frontend` builds (`docker build`) — **NOT VERIFIED**.
- `infra/docker-compose.yml` multi-container startup, Docker health checks, and reverse proxy routing — **NOT VERIFIED**.
- *(Observed Defect in Unexecuted Stack)*:
  1. [Dockerfile.frontend](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/infra/docker/Dockerfile.frontend) copies `/app/frontend/dist` to `nginxinc/nginx-unprivileged:1.26-alpine` without an SPA `try_files $uri $uri/ /index.html;` directive, meaning browser refreshes on React routes (`/dashboard`, `/intake`) would return HTTP `404`.
  2. [health.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/api/v1/routes/health.py) `/health/ready` runs `SELECT 1` against the database only and does **not** ping `Redis` or verify the ML `.joblib` artifact is loaded.

---

## 5. ML Pipeline Reproducibility and Model Validation Findings

All checks below were independently executed and verified against source code in `ml/pipelines/`, `backend/app/ml/`, and saved files during this audit:

| Audit Criterion | Direct Verification Evidence & Metrics | Finding / Limitation | Status |
| :--- | :--- | :--- | :--- |
| **1. Raw Dataset Hash & Provenance** | `ml/data/raw/cleveland_heart_disease_raw.csv` (`303` rows): SHA-256 `a74b7efa387bc9d108d7d0115d831fe9b414b29ae7124f331b622b4efa0427c8` matches `data_provenance_audit.json`. | Historical 1988 dataset; lacks HIPAA/GDPR anonymization certification (`modern_hipaa_certification: false`). | **VERIFIED** |
| **2. Target Definition & Binary Conversion** | `load_raw_cleveland()` (`prepare_data.py:80`): `(df["num"] >= 1).astype(int)`. Baseline $N=303$: `164` neg / `139` pos ($\pi = 0.458746$, null Brier $= 0.248298$). Sensitivity $N=297$: `160` neg / `137` pos ($\pi = 0.461279$, null Brier $= 0.248501$). | Task B (`ten_year_population_risk_percent`) strictly `None` across codebase. | **VERIFIED** |
| **3. Train / Test Split Integrity** | Stratified 80/20 (`random_state=42`): `train.parquet` `(242, 17)` (`131` neg, `111` pos); `test.parquet` `(61, 16)` (`33` neg, `28` pos). Verified `len(set(tr['source_row_index']) & set(te['source_row_index'])) == 0`. | Disjoint stratified partitions confirmed. | **VERIFIED** |
| **4. Training-Only Imputation** | `fit_training_imputers(train_raw)` (`prepare_data.py:129`) runs *after* `train_test_split`: `ca=0.0`, `thal=1.0`. Missing counts verified: `1 ca, 1 thal` in train; `3 ca, 1 thal` in test. | **Gap at serving (`inference_service.py:55-56`):** `dto_to_feature_vector` hardcodes fallback `0` and `1` instead of reading imputers saved in artifact. | **PARTIALLY VERIFIED** |
| **5. Cross-Validation Leakage** | `prepare_data.py:129-139` fits `ca`/`thal` imputation once on the whole $N=242$ training set *before* 5-fold CV split in `train_model.py:126`. | Minor global training-fold preprocessing prior to OOF CV (affects only 2 missing rows in train; 0 test leakage). | **PARTIALLY VERIFIED** |
| **6. Out-of-Fold Calibration** | `train_model.py:126-140` collects OOF margins from 5 80%-fold XGBoost models to fit `platt_calibrator`, then fits `final_xgb` on **100%** of `X_train` and pairs them. Unused `CalibratedClassifierCV` fitted & discarded at lines 143–144. | Slight structural mismatch pairing OOF 80%-fold margin calibrator with a 100%-train XGBoost estimator. | **PARTIALLY VERIFIED** |
| **7. Test Set Isolation** | `X_test` / `y_test` excluded from training, imputation, Platt calibration, `cohort_feature_means`, `feature_bounds`, and `background_sample` (`train_model.py:146-163`). | No holdout test leakage into artifact parameters. | **VERIFIED** |
| **8. Metric Reproduction & Subgroups** | `evaluate_registered_model()` reproduced identically: **Test ($N=61$):** `AUROC=0.9502`, `Brier=0.0927`, 10-bin `ECE=0.1120`. **Training OOF ($N=242$):** `AUROC=0.8894`, `Brier=0.1303`, `ECE=0.0448`. **Test Sex Subgroups:** Female ($n=20$) `AUROC=0.989`, `Brier=0.0567`; Male ($n=41$) `AUROC=0.9381`, `Brier=0.1103`. | **Provisional target miss:** Holdout `ECE=0.1120` exceeds `<= 0.05` target; $N=61$ ($n=20$ female) cannot establish external validity or subgroup fairness. | **PARTIALLY VERIFIED** |
| **9. Model Artifact Hash & Serving Parity** | `ml/registry/model.joblib`, `backend/app/ml/artifacts/heartxai_task_a_v2.0.0.joblib`, and `backend/app/ml/artifacts/model.joblib` all match SHA-256 `5f7ef04726fd985109a44927f8718697a94e096dd0734473da3246e3d4372086` (`ALL_MODEL_BYTES_EQUAL: True`). | Identical serialized artifact verified across registry and runtime. | **VERIFIED** |
| **10. SHAP Model & Feature Ordering** | `art['feature_columns'] == FEATURE_COLUMNS` (`True`); runtime verification `abs(out.raw_margin - shap_out.final_margin) = 1.619e-07`. | Explains **raw log-odds margins** (`output_margin=True`), not calibrated probability space (accurately noted in `ShapWaterfall.tsx`). | **VERIFIED** |
| **11. Counterfactual Scenarios** | `IMMUTABLE_FIELDS` freezes 9 clinical/demographic fields; `MODIFIABLE_BOUNDS` clamps 4 lifestyle inputs (`counterfactual_service.py:15-35`). | DB persistence stores binary `fbs` only, causing `_assessment_to_dto` (`assessment_service.py:42`) to substitute `130.0` or `95.0` on subsequent `/simulate` calls, distorting L1 distances. | **PARTIALLY VERIFIED** |

---

## 6. Healthcare Safety Findings

Direct inspection of `intakeSchema.ts`, `IntakeWizardPage.tsx`, `inference_service.py`, `assessment_service.py`, `shap_service.py`, `counterfactual_service.py`, `export_service.py`, `AppShell.tsx`, `AssessmentResultsPage.tsx`, and `DoctorPortalPage.tsx`:

1. **[VERIFIED] Non-Diagnostic & Non-Prospective Positioning:** `AppShell.tsx` footer, `AssessmentResultsPage.tsx` alert, `export_service.py` Page 1 notice, and `InferenceService.predict` summary explicitly state outputs are informational retrospective UCI Cleveland similarity scores and **NOT** diagnoses or 10-year prospective ASCVD risk predictions. Synthetic banner renders globally in `AppShell.tsx`.
2. **[VERIFIED] Non-Causal SHAP & Non-Prescription Counterfactual Copy:** Both `shap_service.py` / `ShapWaterfall.tsx` ("statistical association only, not biological causation") and `counterfactual_service.py` / `CounterfactualSimulator.tsx` ("Not a medical prescription") appropriately disclaim causal or therapeutic claims.
3. **[FAILED] Misrepresentation of Fixed Heuristic `±6.5%` as `"95% Confidence Interval"`:** `inference_service.py:124-125` computes `ci_low = round(max(0.0, likelihood_pct - 6.5), 1)` and `ci_high = round(min(100.0, likelihood_pct + 6.5), 1)` with no statistical variance estimator (no bootstrap, conformal prediction, or calibration-error interval). Yet [export_service.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/services/export_service.py#L64) outputs label `"95% Confidence Interval"` and [AssessmentResultsPage.tsx](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/frontend/src/features/assessment/AssessmentResultsPage.tsx#L131) displays `"95% Interval"`. This is mathematically false and clinically misleading.
4. **[REQUIRES GOVERNANCE APPROVAL] Unapproved Clinical Thresholds & Heuristic Red Flags:**
   - Risk tier cutoffs (`< 30.0` low, `30.0–69.99` moderate, `>= 70.0` elevated in `inference_service.py:114-122` and `assessment_service.py:58`) have no clinical validation reference or DEC-002 physician advisory sign-off.
   - Emergency detection (`resting_bp > 180` or `chest_pain_type == 0 and exercise_angina == 1` in `intakeSchema.ts:72-85` and `inference_service.py:134`) uses unverified heuristic rules lacking acute symptom checks (e.g., crushing rest chest pain, dyspnea, syncope) and lacks physician sign-off.
   - Counterfactual target candidates (`resting_bp`: `115/120/130`, `chol`: `170/190/210`, `fbs`: `100.0`) and safety floors (`[90, 220]`, `[120, 500]`, `[70, 350]`, `[60, 210]`) in `counterfactual_service.py` lack clinical review.
5. **[REQUIRES GOVERNANCE APPROVAL] Hardcoded Header Emergency Quick-Dial (`911`/`112`/`999`):** `AppShell.tsx:89-95` renders an active `tel:` emergency quick-dial link in the sticky navbar keyed solely by a user-selectable dropdown defaulting to `US` (`911`), rather than location-verified or conditional local-emergency guidance (`DEFAULT` in `shared/country-profiles.json` uses `"Contact local emergency medical services immediately"`).
6. **[FAILED] Blood Glucose Precision Corruption on Reload & PDF Export:** `assessment_service.py:42,75` replaces stored user glucose readings with placeholder values `130.0` or `95.0` based on the binary `fbs` flag (`> 120 mg/dL`), silently altering displayed `fasting_blood_sugar` after persistence.

---

## 7. Privacy, Consent and Category C Enforcement Findings

1. **[FAILED] Category C Real PHI Ingestion Is NOT Technically Enforced Server-Side:**
   - **`POST /api/v1/auth/register` (`auth.py:67`, `schemas/auth.py:16`):** Accepts any syntactically valid `EmailStr` and arbitrary `full_name`; real personal emails and names are accepted and stored without domain restriction or attestation validation.
   - **`POST /api/v1/assessments` (`assessments.py:35`, `assessment_service.py:115`):** Accepts any real person's clinical biomarkers without an anti-PHI attestation check or blocking mechanism, blindly setting `Assessment.is_synthetic = settings.SYNTHETIC_DATA_ONLY`.
   - **`POST /api/v1/consents/doctor/assessments/{id}/notes` (`consents.py:159`, `consent_service.py:166`):** Accepts arbitrary free-form text (`min_length=3, max_length=4000`) with zero PII/PHI detection or guardrails; real patient names, MRNs, or clinical diagnoses can be stored in `clinical_notes`.
   - **Frontend LocalStorage Draft (`IntakeWizardPage.tsx:73`):** Persists raw entered clinical intake values in browser `localStorage` (`heartxai_synthetic_intake_draft_v1`), creating client-side persistence risk if real user data were entered on shared devices.
2. **[FAILED] Expired 72-Hour Consent Grant Bypass in `assessment_service.py`:**
   - [consent_service.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/services/consent_service.py#L86-L125) (`verify_clinician_assessment_access`) correctly verifies `status == "ACTIVE"`, `revoked_at is None`, and `expires_at > datetime.now(UTC)`.
   - However, [assessment_service.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/services/assessment_service.py#L196-L206) (`authorize_assessment_access`) — used by `GET /assessments/{id}`, `GET /assessments/{id}/shap`, `POST /assessments/{id}/simulate`, and `GET /assessments/{id}/export-pdf` — checks **only** `DoctorGrant.status == "ACTIVE"` and omits both `expires_at > now` and `revoked_at is None`. Once 72 hours elapse, an expired grant whose `status` column still says `"ACTIVE"` permits unauthorized clinician access via `/api/v1/assessments/{id}*`.
3. **[PARTIALLY VERIFIED] Broad Consent Scope & Admin Assessment Access:**
   - `DoctorGrant` (`models/consent.py`, `consent_service.py:142`) grants patient-wide access (`patient_id` ↔ `doctor_id`) covering *all* past and future assessments rather than scoping per assessment.
   - `authorize_assessment_access` (`assessment_service.py:193`) allows `ADMIN`/`ADMINISTRATOR` users unrestricted read and PDF-export access to any patient's clinical biomarkers without consent.
   - Explicit manual revocation (`POST /api/v1/consents/{grant_id}/revoke`) immediately sets `status="REVOKED"` and blocks subsequent access (verified in `test_consent_lifecycle_expiry_and_revocation_403`).
4. **[PARTIALLY VERIFIED] Audit Log Limitations:** `record_audit_event()` (`audit_service.py:20`) hardcodes `ip_address="127.0.0.1"` by default instead of capturing request client IP / `X-Real-IP`, and consent/assessment reads on `/api/v1/assessments/*` do not write audit rows.

---

## 8. Security and Accessibility Evidence

### Security Controls Verification Matrix

| Control Area | Verification Evidence | Findings / Limitations | Status |
| :--- | :--- | :--- | :--- |
| **Password Hashing (Argon2id)** | `backend/app/core/security.py:21` (`time_cost=3, memory_cost=65536, parallelism=4`); tested in `test_argon2id_hashing_and_verification` & `test_security.py`. | Meets RFC 9106 parameters locally. | **VERIFIED** |
| **JWT Lifecycle, Rotation & Replay** | `security.py:46-114`, `auth_service.py:61-139`; unit-tested in `test_register_login_refresh_replay_detection_and_logout`. | Verified against `InMemoryTokenStore` only; default `SECRET_KEY` in `config.py:27` has **no startup fail-fast** in `staging`/`production`. | **PARTIALLY VERIFIED / FAILED** |
| **Redis Fail-Closed Behaviour** | `redis_client.py:44-56`; tested in `test_redis_fail_closed_when_unavailable` (raises HTTP 503). | Tested via mocked `RedisConnectionError`, not live Redis socket failures. | **PARTIALLY VERIFIED** |
| **RBAC & Anti-IDOR** | `deps.py:54-66`, `test_rbac_enforcement_rejects_wrong_role`, `test_anti_idor_cross_tenant_isolation` (patient-to-patient 403). | **FAILED** for clinician expired-grant check in `assessment_service.py:196-205`; `ADMINISTRATOR` can view raw clinical records without consent. | **FAILED** |
| **Duplicate Unversioned API Mount** | `backend/app/main.py:81-82` mounts `api_router` at both `/api/v1` and root (`/`). | Unversioned `/auth/refresh` conflicts with cookie `path="/api/v1/auth"` and exposes routes outside Nginx `/api/` path matching if backend is hit directly. | **FAILED** |
| **CORS, Cookies & CSRF** | `main.py:70-75` uses `allow_credentials=True` + wildcard `allow_methods=["*"]`, `allow_headers=["*"]`; `auth.py:37-40` uses `httponly=True, samesite="lax", secure=(staging|production)`. | Wildcard headers/methods with credentials; no custom CSRF header or token required on `/auth/refresh` & `/auth/logout`. | **PARTIALLY VERIFIED** |
| **Rate Limiting & Security Headers** | Defined in `infra/nginx/nginx.conf:15-39` (`auth_limit 10r/m`, `api_limit 60r/m`, CSP `'unsafe-inline'` styles, HSTS, `X-Frame-Options: DENY`). | Nginx listens on **HTTP port `:80` only** (no TLS `:443` server block yet) and has **never been executed in a container**. | **NOT VERIFIED** |
| **Input Validation** | `BaseSchema` `extra="forbid"`, Pydantic bounds (`schemas/assessment.py`), Zod (`intakeSchema.ts`), Nginx `client_max_body_size 1m`. | Backend schema/Zod validation passes unit tests; Nginx payload limit unverified live. | **PARTIALLY VERIFIED** |
| **Sensitive Data Exposure / Logs** | `logging.py:21-49` scrubs regex keys (`password|secret|token|cookie|email`); `errors.py` strips stack traces (`test_logging_phi_scrubbing`, `test_rfc7807_error_envelopes_and_no_stack_trace_leak`). | Scrubbing matches `key=val` patterns only; plaintext email/name/free-text logs outside pattern or PDF/assessment DB fields remain unencrypted at rest unless host storage encrypted. | **PARTIALLY VERIFIED** |
| **Static Analysis (Bandit)** | Re-run cleanly: `bandit -r backend/app -ll -ii` → **0 High, 0 Medium**, 5 Low, 0 `#nosec` across `3,269` LOC. | Bandit covers Python static AST checks only; **not** a substitute for DAST or manual pentesting. | **VERIFIED (SAST Only)** |
| **Dependency Vulnerabilities** | Re-run cleanly: `frontend` `npm audit --omit=dev` → **0 vulnerabilities**; `npm audit` (with devDependencies) → **6 vulnerabilities (3 moderate, 1 high, 2 critical)** (`@vitest/mocker`, `esbuild`, `tinypool`). | **`pip-audit` is not installed** and Python dependency CVE scan was **NOT executed**. | **PARTIALLY VERIFIED** |
| **OWASP ZAP & Pentesting** | Referenced in Milestone 18 plan (`MASTER_IMPLEMENTATION_ROADMAP.md:44`). | **Not executed.** Zero ZAP scan reports or manual penetration test evidence exist. | **NOT VERIFIED** |

### Accessibility Validation (`WCAG 2.2 AA`)

- **Executed (`VERIFIED` Automated Subset):** `frontend/src/tests/a11y.test.tsx` (`vitest-axe`) passed with **0 violations** across all 7 routes (`/login`, `/register`, `/dashboard`, `/intake`, `/directory`, `/doctor`, `/admin`) alongside `eslint-plugin-jsx-a11y` (`0` warnings/errors) during this audit (`vitest run`: 5 files / 24 tests passed).
- **Incomplete / Unverified for Full WCAG 2.2 AA Conformance (`PARTIALLY VERIFIED`):** Automated `axe-core` under `jsdom` mocks `fetch` (`[]`) and lacks a real layout engine. It does **not** verify rendered pixel color contrast, WCAG 2.2 `2.5.8` target-size ($\ge 24\times 24$ px) / `2.4.11`/`2.4.13` focus visibility in Chromium, 320px/400% zoom reflow, chart/slider keyboard ergonomics on real mobile/desktop viewports, or NVDA/JAWS/VoiceOver screen-reader behavior. Full WCAG 2.2 AA conformance cannot be claimed.

---

## 9. Performance and Deployment Verification

- **Local Function-Level Microbenchmarks (`VERIFIED` as Local Measurements Only):** [benchmark_performance.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/scripts/benchmark_performance.py) recorded on local Windows (`Python 3.11`, in-process + `TestClient`, SQLite/warmed singleton):
  - XGBoost inference ($n=200$): mean `0.748 ms`, p95 `1.074 ms`
  - TreeSHAP attribution ($n=50$): mean `1.425 ms`, p95 `1.681 ms`
  - Counterfactual grid search ($n=30$): mean `7.859 ms`, p95 `10.198 ms`
  - ReportLab PDF generation ($n=15$): mean `8.489 ms`, p95 `9.82 ms`
  - Argon2id hashing ($n=5$): mean `90.657 ms`, p95 `92.268 ms`
  - `TestClient` `/health/live` ($n=100$): mean `9.999 ms`, p95 `10.954 ms` (`100.0 req/s`); 4-thread 100-inference burst: `97.36 ms`.
  - *Constraint:* These measure Python function CPU time on a developer laptop, **not** HTTP + TLS + Nginx + PostgreSQL + Redis production VPS latency.
- **Concurrent Load Testing (`NOT VERIFIED`):** [load_test.js](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/infra/scripts/load_test.js) (K6 up to 25 VUs) has **never been executed**. The DEC-001 capacity estimate (`"500+ daily assessments"`) remains unverified.
- **Playwright End-to-End UAT (`NOT VERIFIED`):** [synthetic_patient_journey.spec.ts](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/tests/e2e/synthetic_patient_journey.spec.ts) has **never been executed** against a live browser + stack.
- **Docker Builds & Compose Deployment (`NOT VERIFIED`):** Only static YAML syntax (`docker compose -f infra/docker-compose.yml config -q`) was checked (`DOCKER_COMPOSE_CONFIG_OK`). Backend/frontend Docker builds, TLS termination, and staging smoke tests were not executed.
- **Disaster Recovery (`NOT VERIFIED` / Spec Mismatch):** [backup_encrypted.sh](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/infra/scripts/backup_encrypted.sh) and [restore_encrypted.sh](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/infra/scripts/restore_encrypted.sh) were **never executed**, write only to local `./backups/` (no offsite S3/R2 upload), and use `openssl enc -aes-256-cbc` rather than the `AES-256-GCM` AEAD algorithm specified in `ADR-012`.

---

## 10. Blocking Issues (Priority Order)

1. **[CRITICAL — PRIVACY / ANTI-IDOR]** Fix `authorize_assessment_access()` in `backend/app/services/assessment_service.py:196-206` to enforce `expires_at > datetime.now(UTC)` and `revoked_at is None` (matching `consent_service.py`), closing expired-grant access on `/api/v1/assessments/{id}*`.
2. **[CRITICAL — CLINICAL SAFETY / TRUTH]** Remove the hardcoded `±6.5%` calculation and `"95% Confidence Interval"` / `"95% Interval"` labels in `inference_service.py:124-125`, `export_service.py:64`, and `AssessmentResultsPage.tsx:131` (replace with either an empirically bootstrapped/conformal calibration interval or remove interval claim pending biostatistics validation).
3. **[CRITICAL — DATA GOVERNANCE (DEC-005)]** Enforce technical Category C blocking if MVP stays synthetic-only (e.g., mandatory synthetic email domain restriction / explicit non-PHI server checks, disabling/filtering arbitrary free-text clinical notes or PII patterns, rejecting real patient payloads at API boundary rather than stamping `is_synthetic=True` on everything).
4. **[CRITICAL — INFRASTRUCTURE VALIDATION]** Execute full Docker builds (`Dockerfile.backend`, `Dockerfile.frontend`), add SPA `try_files ... /index.html` to `Dockerfile.frontend`, fix `/health/ready` to verify Redis + model loadability, and run `pytest`, Alembic migrations, and Redis failover/rotation tests against **real PostgreSQL 16 and Redis 7.2 containers**.
5. **[HIGH — SECURITY CONFIGURATION]** Add a startup assertion refusing to boot in `staging`/`production` with the default `SECRET_KEY` (`config.py:27`), remove the duplicate unversioned `app.include_router(api_router)` mount (`main.py:82`), scope `ADMIN` read access away from raw patient biomarkers, add TLS `:443` termination in `nginx.conf`, and run `pip-audit` + OWASP ZAP.
6. **[HIGH — GOVERNANCE & CLINICAL SIGN-OFF (DEC-002)]** Reconcile stale `PENDING` lines (lines 6 & 18) in `PROJECT_DECISION_REGISTER.md` with Section 4 (`b65bdba`), and obtain explicit **DEC-002** Track 1–4 sign-offs (physician advisory sign-off on red-flag rules, risk tier cutoffs, emergency `tel:` behavior, and counterfactual bounds; content review; IRB/REC determination before human testing).
7. **[HIGH — DATA FIDELITY]** Preserve numeric `fasting_blood_sugar` in the database or assessment JSON rather than reconstructing synthetic `130.0`/`95.0` placeholders in `assessment_service.py:42,75`.

---

## 11. Non-Blocking Improvements

1. Fix `train_model.py` calibration alignment (either use a `CalibratedClassifierCV` ensemble of the 5 fold calibrators cleanly or validate single-model vs ensemble calibration on a larger external validation cohort; move `ca`/`thal` imputation *inside* the 5-fold CV loop in `prepare_data.py`/`train_model.py`).
2. Read `training_fold_imputers` dynamically from the serialized ML `.joblib` artifact inside `dto_to_feature_vector()` (`inference_service.py:55-56`) instead of hardcoding `0` and `1`.
3. Scope `DoctorGrant` optionally to specific `assessment_id`s rather than blanket patient-wide access, capture client `X-Real-IP` in `record_audit_event()`, and add DB-level immutability permissions on `audit_logs` in PostgreSQL.
4. Upgrade frontend `devDependencies` (`vitest`, `esbuild`, `tinypool`) to resolve the 6 dev-toolchain advisories reported by `npm audit`.
5. Upgrade `infra/scripts/backup_encrypted.sh` to true authenticated AEAD encryption (`AES-256-GCM` or `age`) + offsite upload per `ADR-012`, and run a live restore test.

---

## 12. Recommended Order of Remediation

1. **Immediate Code & Safety Fixes (Pre-Staging Gate):** Fix expired-grant authorization in `assessment_service.py`, remove/correct the false `"95% Confidence Interval"` `±6.5%` heuristic, preserve numeric `fasting_blood_sugar`, enforce `SECRET_KEY` production validation, remove the duplicate router mount in `main.py`, and add SPA fallback to `Dockerfile.frontend`.
2. **Governance & Clinical Alignment:** Reconcile `PROJECT_DECISION_REGISTER.md` contradictions; complete `DEC-002` Physician Advisory & Content sign-offs on risk cutoffs, emergency triggers, `tel:` behavior, and Category C API guardrails; confirm `DEC-005` enforcement strictness.
3. **Real Container & Integration Verification:** Build `Dockerfile.backend` and `Dockerfile.frontend`, boot PostgreSQL 16 + Redis 7.2 + Nginx via `infra/docker-compose.yml`, run full `pytest` suite against real Postgres/Redis, verify Redis outage recovery, and verify SPA deep-link refresh & rate-limiting through Nginx.
4. **Security, Load, E2E & Accessibility Completion:** Execute `pip-audit`, OWASP ZAP baseline/full scan, Playwright `synthetic_patient_journey.spec.ts`, K6 `load_test.js` under target concurrency, live `backup_encrypted.sh` / `restore_encrypted.sh` drill, and manual WCAG 2.2 AA browser/keyboard/screen-reader testing.
5. **External ML Validation (Post-MVP Research Track):** Before any non-synthetic or clinical pilot use, resolve holdout calibration (`ECE=0.1120`) and evaluate on independent external cardiovascular cohorts (`DEC-002` Track 3/4 gates).
