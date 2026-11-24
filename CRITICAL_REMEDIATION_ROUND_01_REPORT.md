# HeartXAI 2.0 — Critical Remediation Round 01 Report

**Repository:** `heartxai-2.0` (`https://github.com/sandeep-kumar-270904/Heart-Disease-Risk-Prediction.git`)  
**Branch:** `main`  
**Baseline Audited Commit:** `576413fbd29affcaad08eca3d8d318707d5bb1f0`  
**Remediation Implementation Commit:** `5423e71349824fd05aedf34aa588581ba113c68b`  
**Date:** 25 November 2026  

---

## 1. Summary of Priorities Executed (Priorities 1–8)

| Priority | Scope | Disposition |
| :--- | :--- | :--- |
| **Priority 1** | 72-Hour Doctor Consent Bypass | **FIXED & VERIFIED** via single authoritative `authorize_clinician_grant()` enforcing strict UTC expiry, revocation, role, and ownership. |
| **Priority 2** | False `"95% Confidence Interval"` (`±6.5%`) | **FIXED & VERIFIED** — hardcoded `±6.5%` computation and `"95% Confidence Interval"` / `"95% Interval"` labels removed across backend, schemas, UI, and PDF. |
| **Priority 3** | Synthetic-Only MVP Data Boundary | **FIXED & VERIFIED** — RFC 2606 synthetic domain allowlist + mandatory payload attestation on registration/intake; arbitrary clinician free-text notes disabled; PII profile fields trimmed; frontend `localStorage` clinical draft caching removed. |
| **Priority 4** | Fasting Blood Sugar Representation | **FIXED & VERIFIED** — nullable numeric `fasting_blood_sugar_mgdl` persisted cleanly alongside binary UCI `fbs`; legacy null records never reconstructed as placeholders (`130.0`/`95.0`). |
| **Priority 5** | Security Config, Routing, TLS & AES-GCM Backup | **FIXED & VERIFIED** (locally for secrets, routing & AES-256-GCM AEAD); **Nginx TLS `:443` & Compose container boot authored & syntax-checked, pending live container execution**. |
| **Priority 6** | ML Calibration & Reproducibility | **REPRODUCED & DOCUMENTED** — original holdout metrics (`AUROC=0.9502`, `Brier=0.0927`, `ECE=0.1120`, $N=61$) preserved untouched; dead `CalibratedClassifierCV` removed; diagnostic 5-bin/adaptive ECE added; `training_fold_imputers` wired cleanly. |
| **Priority 7** | Clinical Safety Presentation | **FIXED & VERIFIED** — unvalidated `30%`/`70%` risk strata removed (`risk_strata="unstratified"`); unreviewed emergency red-flag triage and hardcoded country `tel:` quick-dial disabled pending DEC-002 physician advisory review. |
| **Priority 8** | Regression Testing & Honest Evidence | **VERIFIED** (`51/51` pytest, `24/24` Vitest + `vitest-axe`, `mypy --strict` 29 files, Ruff, Bandit, Vite build); live Postgres/Redis/Docker/ZAP/K6/Playwright truthfully listed as **NOT EXECUTED**. |

---

## 2. Priority-by-Priority Findings, Root Causes & Corrections

### Priority 1 — 72-Hour Doctor Consent Bypass
1. **Original Finding:** `authorize_assessment_access()` allowed clinicians to read assessments, SHAP values, counterfactual simulations, and export PDFs after 72-hour grant expiration as long as `DoctorGrant.status == "ACTIVE"`.
2. **Root Cause:** Consent expiration/revocation verification lived only in `consent_service.py` (`_is_grant_currently_valid`), whereas `assessment_service.py` queried `DoctorGrant.status == "ACTIVE"` independently without inspecting `expires_at` or `revoked_at`.
3. **Exact Files Modified:**
   - [consent_service.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/services/consent_service.py)
   - [assessment_service.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/services/assessment_service.py)
4. **Actual Correction:**
   - Added timezone-aware UTC clock resolver `resolve_utc_now(now=None)`, `is_grant_active_at(grant, now=now)`, and **one authoritative authorization entrypoint** `authorize_clinician_grant(db, patient_id=..., doctor=..., now=...)`.
   - Enforces all 7 constraints: verified active `CLINICIAN` role, `grant.patient_id == assessment.patient_id`, `grant.doctor_id == doctor.id`, `grant.status == "ACTIVE"`, `grant.revoked_at is None`, `expires_at > current_utc` (strict inequality — exact expiry denies access), and ownership consistency.
   - Wired `authorize_assessment_access()` (protecting `GET /assessments/{id}`, `/shap`, `POST /simulate`, `GET /export-pdf`) and `verify_clinician_assessment_access()` (`GET /consents/doctor/assessments/{id}`) to call `authorize_clinician_grant()`; removed automatic `ADMINISTRATOR` bypass on individual patient biomarker reads.
5. **Regression Tests Added:** `test_priority_1_authoritative_consent_blocks_expired_revoked_and_exact_boundary` in [test_remediation_round_01.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/tests/test_remediation_round_01.py) covering valid grant access, expired grant `403` across all 5 endpoints, `1µs`-before vs exact-expiry denial via controllable UTC clock, immediate revocation `403`, wrong clinician, unverified clinician, admin without consent, and wrong patient.

### Priority 2 — False `"95% Confidence Interval"`
1. **Original Finding:** Hardcoded `±6.5%` band around predicted likelihood was surfaced as `"95% Confidence Interval"` (PDF) and `"95% Interval"` (UI).
2. **Root Cause:** Heuristic UI/DB scaffolding introduced an uncalibrated constant offset `ci_low = likelihood - 6.5`, `ci_high = likelihood + 6.5` in `inference_service.py`.
3. **Exact Files Modified:**
   - [inference_service.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/ml/inference_service.py)
   - [assessment.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/models/assessment.py)
   - [003_remediation_round_01.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/alembic/versions/003_remediation_round_01.py)
   - [assessment.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/schemas/assessment.py)
   - [assessment_service.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/services/assessment_service.py)
   - [export_service.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/services/export_service.py)
   - [assessment.ts](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/frontend/src/types/assessment.ts)
   - [AssessmentResultsPage.tsx](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/frontend/src/features/assessment/AssessmentResultsPage.tsx)
   - [benchmark_performance.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/scripts/benchmark_performance.py)
4. **Actual Correction:** Removed `±6.5%` calculation completely; removed `confidence_interval` from `InferenceOutput`, Pydantic `AssessmentDetailResponse`, TypeScript interfaces, React results card, and ReportLab PDF; made DB columns `confidence_interval_low`/`high` nullable in `003_remediation_round_01` writing `None`; reframed output strictly as `"Experimental Retrospective Task A Model Score"` (non-diagnostic, no 10-year risk forecast).
5. **Regression Tests Added:** `test_priority_2_and_7_no_false_confidence_interval_or_30_70_tiers` (verifies API JSON and decompressed PDF via `pypdf`) and updated [assessment-results.test.tsx](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/frontend/src/features/assessment/__tests__/assessment-results.test.tsx).

### Priority 3 — Synthetic-Only MVP Data Boundary
1. **Original Finding:** API accepted arbitrary real-world emails/names, biomarkers, and 4,000-character clinical notes while blindly flagging rows `is_synthetic=True`.
2. **Root Cause:** Policy relied on frontend banners/checkboxes and server setting `is_synthetic=settings.SYNTHETIC_DATA_ONLY` rather than server-enforced ingress rules.
3. **Exact Files Modified:**
   - [auth.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/schemas/auth.py) & [auth.ts](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/frontend/src/types/auth.ts)
   - [auth_service.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/services/auth_service.py)
   - [assessment.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/schemas/assessment.py) & [assessment.ts](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/frontend/src/types/assessment.ts)
   - [assessment_service.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/services/assessment_service.py)
   - [consent_service.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/services/consent_service.py) & [consents.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/api/v1/routes/consents.py)
   - [RegisterPage.tsx](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/frontend/src/features/auth/RegisterPage.tsx), [IntakeWizardPage.tsx](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/frontend/src/features/intake/IntakeWizardPage.tsx), [intakeSchema.ts](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/frontend/src/features/intake/intakeSchema.ts), [DoctorPortalPage.tsx](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/frontend/src/features/doctor/DoctorPortalPage.tsx), [LoginPage.tsx](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/frontend/src/features/auth/LoginPage.tsx)
   - [generate_synthetic_patients.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/scripts/generate_synthetic_patients.py), [seed_synthetic_database.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/scripts/seed_synthetic_database.py), [synthetic_patient_journey.spec.ts](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/tests/e2e/synthetic_patient_journey.spec.ts)
4. **Actual Correction:**
   - Restricted `/api/v1/auth/register` emails server-side to IANA RFC 2606 non-routable synthetic domains (`@example.com`, `@example.org`, `@example.net`) + required explicit `synthetic_persona_acknowledged: true` (note: replaced `.local` placeholders that `email-validator` rejects under `EmailStr` validation).
   - Required `synthetic_fixture_confirmed: true` on `AssessmentCreateDto` and verified `_verify_synthetic_provenance(patient)` (`SYNTHETIC_DATA_ONLY=true`, `patient.is_synthetic=True`, and verified synthetic email domain) before allowing assessment creation.
   - Minimized `PatientProfileUpdateDto` by removing unnecessary PII fields (`date_of_birth`, `emergency_contact_name`, `emergency_contact_phone`).
   - Intentionally disabled arbitrary clinician free-text notes (`POST /api/v1/consents/doctor/assessments/{id}/notes` returns HTTP `422 ClinicalBoundaryError` and logs `CLINICAL_NOTE_BLOCKED_DEC005`).
   - Removed browser `localStorage` draft persistence of entered clinical biomarkers in `IntakeWizardPage.tsx`.
5. **Regression Tests Added:** `test_priority_3_synthetic_only_boundary_blocks_real_domains_and_notes` + updated `test_consent_lifecycle_expiry_and_revocation_403` (`422` assertion on clinical notes).

### Priority 4 — Fasting Blood Sugar Data Representation
1. **Original Finding:** Numeric `fasting_blood_sugar` input was discarded on save (storing only UCI binary `fbs`), then reconstructed on readback/simulation as placeholder `130.0` or `95.0`.
2. **Root Cause:** `assessments` table lacked a numeric column for entered blood glucose.
3. **Exact Files Modified:**
   - [assessment.py (model)](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/models/assessment.py), [003_remediation_round_01.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/alembic/versions/003_remediation_round_01.py)
   - [assessment.py (schema)](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/schemas/assessment.py), [assessment.ts](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/frontend/src/types/assessment.ts)
   - [assessment_service.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/services/assessment_service.py), [export_service.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/services/export_service.py), [inference_service.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/ml/inference_service.py), [seed_synthetic_database.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/scripts/seed_synthetic_database.py)
4. **Actual Correction:** Added nullable `fasting_blood_sugar_mgdl` column (`003_remediation_round_01` keeps backward compatibility with legacy records) alongside derived UCI `fbs` (`> 120.0 mg/dL`); ML preprocessing in `dto_to_feature_vector()` explicitly derives binary `fbs_binary` preserving 13-feature training contract order; `AssessmentDetailResponse` exposes `fasting_blood_sugar: float | None` and `fasting_blood_sugar_gt_120: bool`; legacy binary-only records return `None` cleanly (never reconstructed to `130.0`/`95.0`) and PDF export renders exact `mg/dL` or legacy notice.
5. **Regression Tests Added:** `test_priority_4_fasting_blood_sugar_numeric_roundtrip_and_no_legacy_reconstruction` & migration assertions in [test_migrations_and_seeding.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/tests/test_migrations_and_seeding.py).

### Priority 5 — Security Configuration Remediation (`A`–`D`)
1. **Original Finding:** Default `SECRET_KEY` permitted in staging/prod; duplicate unversioned `api_router` mount in `main.py`; Nginx port `:80`-only with HSTS over HTTP and missing frontend SPA fallback; `backup_encrypted.sh` used `AES-256-CBC` instead of ADR-012 `AES-256-GCM`.
2. **Exact Files Modified / Created:**
   - [config.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/core/config.py) (`Settings.validate_staging_production_security` failing closed on `<32` char or placeholder secrets or `DEBUG=True` outside `development/dev/test/local`).
   - [main.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/main.py) & [health.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/api/v1/routes/health.py) (removed unversioned `api_router` mount; kept `/api/v1/*` canonical + root `/health/live`, `/health/ready`; tightened CORS headers/methods; added ML model & non-local Redis checks to `/health/ready`).
   - [nginx.conf](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/infra/nginx/nginx.conf), [nginx.frontend.conf](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/infra/docker/nginx.frontend.conf), [Dockerfile.frontend](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/infra/docker/Dockerfile.frontend), [docker-compose.yml](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/infra/docker-compose.yml) (port `:80` → `301 HTTPS`, TLS `1.2/1.3` on `:443`, SPA `try_files`, fail-closed `${SECRET_KEY:?}`).
   - [backup_aead.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/scripts/backup_aead.py), [backup_encrypted.sh](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/infra/scripts/backup_encrypted.sh), [restore_encrypted.sh](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/infra/scripts/restore_encrypted.sh) (`PBKDF2HMAC-SHA256` 200k iter + `AESGCM` authenticated header `HXAEAD01`, zero plaintext temp files).
3. **Regression Tests Added:** `test_priority_5_config_fail_closed_and_canonical_routing`, `test_priority_5d_backup_aes256_gcm_roundtrip_wrong_key_and_tamper` (verified round-trip, wrong-key `InvalidTag`, ciphertext/header tamper `InvalidTag`, zero leftover temp files).

### Priority 6 — ML Calibration & Reproducibility
1. **Original Finding:** Holdout uniform 10-bin ECE (`0.1120`, $N=61$) exceeds `<= 0.05` provisional target; unused `CalibratedClassifierCV` in `train_model.py`; inference hardcoded missing-value defaults rather than reading artifact imputers.
2. **Exact Files Modified:**
   - [train_model.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/ml/pipelines/train_model.py) (removed unused `CalibratedClassifierCV` dead code; added `training_fold_imputers` to artifact export schema while leaving saved registry `.joblib` & holdout results untouched).
   - [evaluate_model.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/ml/pipelines/evaluate_model.py) (recomputes saved registry artifact metrics plus diagnostic 5-bin ECE `0.0401`, adaptive quantile 10-bin ECE `0.1115`, raw sigmoid comparison `Brier 0.0973` / `ECE 0.0930`, and calibration limitation note).
   - [inference_service.py](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/backend/app/ml/inference_service.py) (`dto_to_feature_vector` reads `training_fold_imputers` dynamically when present).
3. **Reproduced Saved Holdout Metrics (`test_saved_registry_model_reproducibility_and_diagnostics`):**
   - `n_test = 61`, `auroc = 0.9502`, `brier_score = 0.0927`, `ece (10 uniform bins) = 0.1120`, `artifact_sha256 = 5f7ef04726fd985109a44927f8718697a94e096dd0734473da3246e3d4372086`, `feature_order_matches_contract = True`.

### Priority 7 — Clinical Safety Presentation Audit Matrix

| Clinically Sensitive Rule / Element | Exact Implementation | Intended Purpose | Rule Source | Clinical Review Exists? | Status in MVP |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`30%` / `70%` Risk Strata Tiering** | Previously `<30% low`, `30–70% moderate`, `>=70% elevated` | Group model outputs into action tiers | Heuristic (no clinical source) | **No** | **DISABLED / REMOVED** (`risk_strata="unstratified"`) |
| **Hardcoded `±6.5%` Confidence Interval** | Previously `likelihood ± 6.5%` labeled `"95% Confidence Interval"` | Convey score uncertainty | Heuristic constant (invalid) | **No** | **REMOVED COMPLETELY** |
| **Emergency Red-Flag Triage** | Previously `resting_bp > 180` or `cp == 0 && exang == 1` | Acute crisis alerting | Heuristic (`intakeSchema.ts`, `inference_service.py`) | **No (DEC-002 Track 1 open)** | **DISABLED PENDING REVIEW** (`emergency_warning_active=False`; generic EMS notice shown) |
| **Header Country `tel:` Emergency Dial** | Previously `<a href="tel:911/112/999">` from region dropdown | One-click EMS call | UI region selector (unverified GPS) | **No** | **DISABLED PENDING REVIEW** (static text `"Demo Only — Medical Emergency? Call Local EMS"`) |
| **TreeSHAP Feature Attribution** | `shap.TreeExplainer` over raw XGBoost log-odds margins | Local statistical model explanation | Statistical Shapley values (non-causal) | N/A (algorithmic explainability) | **ACTIVE WITH DISCLAIMER** (`statistical association only, not biological causation`) |
| **Counterfactual Simulator** | Grid / user bounds (`[90,220]`, `[120,500]`, `[70,350]`, `[60,210]`) locking 9 immutable fields | Exploratory what-if input perturbation | Heuristic physiological bounds | **No** (bounds unreviewed) | **ACTIVE AS NON-PRESCRIPTION MODEL EXPLORATION** (`Hypothetical What-If Model Input Simulator` — explicitly disclaims treatment advice) |

---

## 3. Verification Commands Executed & Actual Outcomes (Priority 8)

### A. Executed Locally & Passed
| Check | Command | Exact Outcome |
| :--- | :--- | :--- |
| **Backend & ML Suite** | `pytest backend/ ml/tests/` | **51 passed, 0 failed, 0 skipped** in `18.15s` *(SQLite + `InMemoryTokenStore`)* |
| **ML Evaluation Diagnostics** | `python -m ml.pipelines.evaluate_model` | Exit `0` (`AUROC=0.9502`, `Brier=0.0927`, `ECE=0.112`, 5-bin `ECE=0.0401`, SHA-256 verified) |
| **Python Lint & Format** | `ruff format backend/ ml/ scripts/` & `ruff check backend/ ml/ scripts/` | **All checks passed!** |
| **Python Strict Typing** | `mypy --strict app/core app/schemas app/ml app/services app/api/v1/routes app/main.py` | **Success: no issues found in 29 source files** |
| **Python SAST** | `bandit -r backend/app -ll -ii` | **0 High, 0 Medium** (6 Low, `0 #nosec`, `3,470` LOC) |
| **Frontend Typecheck** | `npm run typecheck` (`tsc --noEmit`) | Exit `0` (0 errors) |
| **Frontend Lint** | `npm run lint` (`eslint --max-warnings 0`) | Exit `0` (0 warnings/errors) |
| **Frontend Unit & A11y** | `npm test` (`vitest run`) | **5 test files passed, 24 tests passed, 0 failed, 0 skipped** (`6.31s`) |
| **Frontend Production Build** | `npm run build` (`tsc --noEmit && vite build`) | Built cleanly in **`5.18s`** (`dist/assets/index-C1j0E9W7.js 427.25 kB`) |
| **Compose Fail-Closed & Config** | `docker compose -f infra/docker-compose.yml config -q` | Fails closed without `SECRET_KEY`; exits `0` (`COMPOSE_WITH_SECRET_OK`) with strong `SECRET_KEY` |

### B. NOT Executed / Blocked by Infrastructure or Tooling
- **Live `PostgreSQL 16` migrations & integration suite:** **NOT EXECUTED** (no HeartXAI Postgres container running).
- **Live `Redis 7.2` token rotation, TTL & outage recovery:** **NOT EXECUTED** (no HeartXAI Redis container running).
- **Live `Dockerfile.backend` / `Dockerfile.frontend` builds & Compose boot:** **NOT EXECUTED** (images not built; no staging TLS certificates provisioned).
- **Live `backup_encrypted.sh` / `restore_encrypted.sh` against running Postgres container:** **NOT EXECUTED** (AES-256-GCM cipher verified directly via pytest; live `pg_dump` pipe against container not executed).
- **OWASP ZAP, K6 concurrent load test (`load_test.js`), Playwright live E2E (`synthetic_patient_journey.spec.ts`), `pip-audit`:** **NOT EXECUTED**.
- **Manual Chromium/screen-reader WCAG 2.2 AA inspection:** **NOT EXECUTED** (`vitest-axe` runs in `jsdom` only).

---

## 4. Remaining Blockers & Governance Items

1. **Live Container & DB/Cache Verification:** Must build Docker images, mount valid TLS certs for Nginx `:443`, start `infra/docker-compose.yml`, and execute `pytest` + Alembic (`001`→`003`) + Redis outage tests against **real PostgreSQL 16 and Redis 7.2**.
2. **Governance & Clinical Review Gates:**
   - Reconcile stale header lines 6 & 18 (`PENDING USER DECISION`) in [PROJECT_DECISION_REGISTER.md](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/phase-12-final/PROJECT_DECISION_REGISTER.md) with Section 4 (`APPROVED BY USER`).
   - Complete **DEC-002 Tracks 1–4** (physician advisory sign-off before re-enabling clinical risk strata, red-flag triggers, or clinician notes; clinical content sign-off; IRB/REC determination before human testing; regulatory determinations).
3. **Security & Performance Validation Pending Staging:** Execute `pip-audit`, OWASP ZAP, Playwright browser E2E, K6 load test, and fix the 6 frontend devDependency advisories (`vitest`/`esbuild`/`tinypool`).
4. **External ML Calibration:** Holdout $N=61$ (`ECE=0.1120`) remains strictly a small-sample retrospective research artifact; external multi-site validation is required prior to any non-synthetic deployment.

---

## 5. Git Commit & Synchronization Status

- **Remediation Code & Tests Commit:** `5423e71349824fd05aedf34aa588581ba113c68b` (`fix(security,safety): execute critical remediation round 01 across auth, consent, FBS & configs`)
- **Synchronization Verification (`git rev-parse HEAD` == `git rev-parse origin/main` == `git ls-remote origin main`):** Verified synchronized at `5423e71349824fd05aedf34aa588581ba113c68b` prior to committing the final audit/remediation reports.
