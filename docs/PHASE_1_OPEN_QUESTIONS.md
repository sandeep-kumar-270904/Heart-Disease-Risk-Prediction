# HeartXAI 2.0 — Phase 1 Open Questions & Architectural Decisions for Review

**Document ID:** HXAI-DOC-008  
**Version:** 1.0.0  
**Phase:** Phase 1 — Product Research & Engineering Benchmarking  
**Status:** Complete / Ready for Review  
**Author:** Principal Product Engineer & Software Architect  

---

## 1. Overview & Purpose

In accordance with our strict engineering discipline, this document catalogs the critical architectural, clinical, legal, and UX design decisions identified during Phase 1 research that require explicit stakeholder alignment before proceeding to implementation.

Each open question outlines the contextual trade-off, viable options, and the Principal Engineer's recommended path forward.

---

## 2. Catalog of Open Questions

### Question 1: Clinical Dataset Selection for ML Classification
- **Context:** The benchmark UCI Cleveland Heart Disease dataset (303 records, 13 features) is the academic gold standard for binary coronary stenosis classification. However, the combined 4-database UCI repository (Cleveland, Hungarian, Switzerland, Long Beach VA) contains 920 records with higher missingness in fluoroscopy (`ca`) and thallium (`thal`).
- **Options:**
  - *Option A:* Train exclusively on the clean, complete Cleveland dataset ($N=297$ complete cases) where all 13 biomarkers are fully documented.
  - *Option B:* Train on the expanded 4-database combined cohort ($N=920$) using Scikit-learn `IterativeImputer` (MICE) to handle missing fluoroscopy and thallium values.
  - *Option C (Hybrid):* Train primary model on complete Cleveland dataset; use expanded imputed cohort as an out-of-domain generalization test set.
- **Trade-offs:** Option A provides 100% ground-truth integrity without synthetic imputation artifacts; Option B provides larger sample size but introduces imputed clinical features; Option C provides both high training purity and rigorous generalization testing.
- **Engineer's Recommendation:** **Option C (Hybrid)**. Train the production model artifact on the clean Cleveland ground-truth cohort, and validate generalization against the Hungarian/Swiss cohorts.

---

### Question 2: Authentication Session Model: HttpOnly Cookies vs. Authorization Header JWT
- **Context:** Secure session management for the React frontend communicating with the FastAPI backend.
- **Options:**
  - *Option A:* HttpOnly, SameSite=Strict cookies containing the JWT.
  - *Option B:* Bearer token stored in browser `localStorage` / memory and transmitted in the HTTP `Authorization: Bearer <token>` header.
  - *Option C:* Hybrid: Short-lived access token kept in memory; long-lived refresh token stored in HttpOnly cookie.
- **Trade-offs:** Option A provides total protection against XSS token exfiltration, but requires careful CORS and CSRF protection; Option B is simple to implement but vulnerable to XSS if third-party scripts execute; Option C is enterprise-standard but adds refresh token rotation mechanics.
- **Engineer's Recommendation:** **Option A (HttpOnly Cookies with CSRF protection)**. In a healthcare application handling sensitive biomarker telemetry, eliminating XSS token theft is a non-negotiable security priority.

---

### Question 3: Counterfactual Optimization Method: Tree-Specific vs. L1 Boundary Search
- **Context:** Computing the minimal biomarker changes required to reduce predicted risk below a target threshold ($\tau \le 0.20$).
- **Options:**
  - *Option A:* Algorithmic Scipy constrained minimization (`scipy.optimize.minimize` with SLSQP) on the calibrated model probability function with L1-norm distance and hard boundary boxes.
  - *Option B:* External library (e.g. DiCE - Diverse Counterfactual Explanations).
  - *Option C:* Discrete clinical step grid search (evaluating clinically realistic interventions, e.g. reducing BP by 5, 10, 15, 20 mmHg; reducing cholesterol by 20, 40, 60 mg/dL).
- **Trade-offs:** Option A produces mathematically exact continuous solutions; Option B introduces heavy dependencies (PyTorch/TensorFlow backend for DiCE); Option C produces discrete, easily understandable lifestyle recommendations (e.g. "Lower BP by 15 mmHg") and executes in under $10\text{ms}$.
- **Engineer's Recommendation:** **Option C with Option A fallback**. Discrete clinical steps map directly to actionable medical advice (e.g. standard antihypertensive medication typically reduces systolic BP by $10-15\text{ mm Hg}$).

---

### Question 4: Database Engine Strategy during Local Development
- **Context:** PostgreSQL is our agreed production database. However, running local PostgreSQL without Docker running can introduce local environment friction on some Windows developer setups.
- **Options:**
  - *Option A:* Mandate local PostgreSQL service / Docker for all operations; refuse to boot if PostgreSQL is unreachable.
  - *Option B:* Dual-dialect SQLAlchemy architecture: connect to PostgreSQL by default via `DATABASE_URL`, but automatically fallback to a local SQLite file (`heartxai_dev.db`) for rapid offline testing if PostgreSQL is unavailable.
- **Trade-offs:** Option A guarantees 100% dialect parity at all times; Option B enables frictionless automated testing and developer productivity while maintaining PostgreSQL compatibility in staging/production containers.
- **Engineer's Recommendation:** **Option B (Dual-Dialect with PostgreSQL default)**. Standardize schema migrations on standard SQL types supported by both engines, ensuring zero local friction while delivering production-grade PostgreSQL readiness.

---

### Question 5: Scope of External Services (Doctor Discovery & Insurance Navigator)
- **Context:** Task 5 defines Doctor Discovery and Insurance Comparison as product experience areas. Are these backed by live third-party APIs (e.g. NPI Registry, CMS Healthcare.gov API) or verified static clinical directories?
- **Options:**
  - *Option A:* Full integration with live public CMS / NPPES NPI Registry API and insurance directory APIs.
  - *Option B:* Curated, verified database of board-certified clinical cardiologists and standardized preventative cardiovascular coverage guides.
  - *Option C:* Dynamic clinical consultation preparation generator (briefing document) without external third-party API dependencies.
- **Trade-offs:** Option A introduces external API rate limits, network failure points, and API key dependencies; Option B & C provide 100% reliable, zero-failure clinical utility without network flakiness.
- **Engineer's Recommendation:** **Option B & C combined**. Provide a curated directory of cardiology specialties and preventative coverage rules alongside the automated 1-page clinical visit briefing generator.

---

## 3. Next Steps & Approval Gate

With all eight Phase 1 research and benchmarking deliverables complete, Phase 1 is officially ready for human stakeholder review. 

Upon receipt of stakeholder approval on these findings and open questions, we will immediately initiate **Phase 2: Project Scaffolding & Core Infrastructure**.
