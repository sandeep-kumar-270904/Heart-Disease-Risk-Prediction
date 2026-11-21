# HeartXAI 2.0 — Phase 12.1 Final Open Governance Questions
**Document ID:** HX-PR-018  
**Version:** 2.0.0 (Phase 12.1 Revision)  
**Phase:** 12.1 — Final Audit Corrections, Clinical Scope Resolution & Implementation Authorization  
**Author:** Technical Program Manager & Principal Software Architect  
**Status:** Awaiting Explicit Stakeholder Selection  
**Date:** November 2026  

---

## 1. Executive Summary

While all technical specifications, architectural designs, database schemas, and testing frameworks are fully completed and verified in design, production implementation cannot proceed on unverified operational assumptions.

This document articulates the **five strategic governance decisions** that require your explicit selection before Milestone 01 engineering begins.

---

## 2. The Five Strategic Governance Decisions

### Question 1 (DEC-001): Production Hosting Profile & Budget Allocation
- **Option A (Recommended): Tier A — Minimal-Budget VPS (~$25 – $55/month)**
  - *Architecture:* Single VPS (Hetzner CPX31 / DigitalOcean, 4 vCPU, 8 GB RAM, NVMe SSD) running Nginx, FastAPI, PostgreSQL 16, and Redis in isolated containers via Docker Compose. Nightly AES-256-GCM encrypted backups (ADR-012) streamed to Cloudflare R2 / AWS S3.
  - *Intended Purpose:* Prototyping, functional testing, local integration, CI test runners, synthetic data demonstrations.
  - *Pros:* Extremely cost-effective; zero cloud vendor lock-in; handles up to 500 daily assessments.
  - *Cons:* Single point of failure; requires manual intervention if VPS host fails.
- **Option B: Tier B — AWS Managed Cloud Infrastructure (~$250/month)**
  - *Architecture:* AWS ECS Fargate, AWS RDS PostgreSQL 16 Multi-AZ, AWS ElastiCache Redis, AWS Application Load Balancer.
  - *Intended Purpose:* High-availability enterprise production evaluation with automated Multi-AZ failover.
  - *Pros:* Automated multi-zone redundancy; enterprise SLA; managed point-in-time recovery.
  - *Cons:* High recurring monthly cost during development and pre-launch validation.
- **Recommendation:** **Option A for Milestones 01 through 20.**

---

### Question 2 (DEC-002): Clinical Governance Framework & Review Authority
- **Option A (Recommended): Physician Advisory Review & Prominent Statutory Disclaimers**
  - *Structure:* Engage independent practicing clinical advisors to review user-facing language, medical educational copy, symptom guidance, and emergency red-flag triggers. Enforce prominent non-diagnostic clinical disclaimers across all screens and PDF exports.
  - *Intended Purpose:* Appropriate for an educational clinical decision support (CDS) tool under Section 520(o)(1)(E) of the US FDA 21st Century Cures Act.
  - *Pros:* Enables iterative development without multi-month institutional bureaucracy; focuses on transparency.
  - *Cons:* Requires rigorous enforcement of the prohibited claims ledger; cannot claim regulatory certification.
- **Option B: Formal Institutional Ethics / Institutional Review Board (IRB) Protocol**
  - *Structure:* Submit the protocol to a formal hospital or university Institutional Review Board for human subjects research ethics determination prior to any external deployment.
  - *Pros:* Essential if conducting prospective clinical trials or collecting real patient health outcomes.
  - *Cons:* 3 to 6-month procedural review timeline; requires designated institutional sponsorship.
- **Recommendation:** **Option A for MVP software release.** (Trigger Option B if clinical outcome trials are initiated).

---

### Question 3 (DEC-003): Cardiovascular Prediction Scope (Task A vs. Task B)
- **Option A (Recommended): Task A MVP Machine Learning Only (Task B Relegated to Future Research)**
  - *Scope:* Focus the MVP machine learning subsystem strictly on Task A (experimental classification of the heart-disease target in the retrospective UCI Cleveland cohort). Completely remove Task B (prospective 10-year risk calculators like PCE or PREVENT) from the MVP codebase and milestone plan.
  - *Pros:* 100% scientifically defensible; eliminates clinical confusion between cross-sectional catheterization disease classification and future event forecasting.
  - *Cons:* Users do not receive a 10-year percentage risk estimate in the MVP release.
- **Option B: Implement Task B in MVP via a Deterministic Calculator**
  - *Scope:* Add an ACC/AHA PCE or PREVENT calculator into the MVP release alongside Task A.
  - *Pros:* Satisfies user requests for a 10-year heart attack risk number.
  - *Cons:* Scientifically problematic; clinical guidelines are currently transitioning from PCE to PREVENT; increases risk of users misinterpreting experimental AI classification as validated risk.
- **Recommendation:** **Option A.**

---

### Question 4 (DEC-004): Geographic Launch & Localization Scope
- **Option A (Recommended): Tri-Country Architecture (US, IN, UK) with Synthetic Demonstration Data**
  - *Scope:* Deploy the pre-configured country adapters (ADR-011) supporting US, India, and UK measurement units ($\text{mg/dL} \leftrightarrow \text{mmol/L}$), currencies, emergency numbers (911/112/999), and seed directories, tested exclusively with synthetic data.
  - *Pros:* Proves multi-country extensibility and verifies unit conversion math in MVP without geographical lock-in.
  - *Cons:* Requires maintaining seed directory data for three jurisdictions.
- **Option B: Single Jurisdiction (US Only) for Initial MVP**
  - *Scope:* Restrict MVP to US clinical conventions (mg/dL only, 911 only); defer international adapters to post-MVP.
  - *Pros:* Simpler initial directory footprint.
  - *Cons:* Fails to validate international unit conversions in the initial release.
- **Recommendation:** **Option A.**

---

### Question 5 (DEC-005): Data Classification & Real Patient Data Prohibition
- **Option A (Recommended): 100% Synthetic Demonstration Data Mandate**
  - *Policy:* Strictly prohibit the ingestion, storage, or processing of real patient health information (PHI) or personally identifiable information (PII) during all initial development, testing, demonstration, and staging milestones. All test fixtures, user journeys, and demonstrations shall use explicitly generated synthetic patient personas.
  - *Pros:* Complete protection against data breaches and HIPAA/GDPR regulatory violations during development.
  - *Cons:* Real clinical usability studies must wait for a subsequent protocol phase.
- **Option B: Authorize Real Patient Pilot Data in Staging**
  - *Policy:* Allow beta testing with real patient health data during Milestone 20 staging acceptance.
  - *Pros:* Tests system with live clinical records.
  - *Cons:* Severe regulatory and legal exposure; requires signed BAAs, security audits, and formal ethics approval before any code is written.
- **Recommendation:** **Option A.**

---

## 3. Action Required from Stakeholder

Please review these five questions and indicate your choices (e.g., *"Approve Recommendations: 1A, 2A, 3A, 4A, 5A"* or specify custom preferences). 

**Antigravity will pause and wait for your selection before Milestone 01 is authorized.**
