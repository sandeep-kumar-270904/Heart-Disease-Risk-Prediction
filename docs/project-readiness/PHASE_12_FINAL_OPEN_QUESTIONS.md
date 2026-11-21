# HeartXAI 2.0 — Phase 12.2 Final Open Governance Questions
**Document ID:** HX-PR-018  
**Version:** 2.2.0 (Phase 12.2 Final Governance Resolution)  
**Phase:** 12.2 — Final Governance Resolution & Evidence Reconciliation  
**Author:** Technical Program Manager, Principal Software Architect & Clinical Safety Reviewer  
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
  - *Capacity Clarification:* The estimate of "500+ daily assessments" is an **unverified planning estimate**. Empirical load testing across 8 performance variables (concurrent users, TreeSHAP CPU latency, connection pool limits, Redis memory overhead, TLS handshake latency, report PDF generation spikes, database write concurrency, and network bandwidth) will be executed in Milestone 19 to establish empirical capacity ceilings.
  - *Pros:* Extremely cost-effective; zero cloud vendor lock-in; rapid deployment.
  - *Cons:* Single point of failure; requires manual intervention if VPS host fails.
- **Option B: Tier B — AWS Managed Cloud Infrastructure (~$250/month)**
  - *Architecture:* AWS ECS Fargate, AWS RDS PostgreSQL 16 Multi-AZ, AWS ElastiCache Redis, AWS Application Load Balancer.
  - *Intended Purpose:* High-availability enterprise production evaluation with automated Multi-AZ failover.
  - *Pros:* Automated multi-zone redundancy; enterprise SLA; managed point-in-time recovery.
  - *Cons:* High recurring monthly cost during development and pre-launch validation.
- **Recommendation:** **Option A for Milestones 01 through 20.**

---

### Question 2 (DEC-002): Clinical Governance Implementation Scope (Four Distinct Tracks)
*Governance Principle:* Physician advisory review, clinical content review, institutional ethics / IRB determination, and regulatory assessment are four distinct, concurrent governance tracks. An IRB determination is an institutional ethics safeguard, not an alternative to physician review of clinical logic. Furthermore, regulatory applicability remains undetermined pending formal classification.

- **Option A (Recommended): Multi-Track Phased Governance for MVP**
  - *Structure:* Maintain all four governance tracks as distinct workflows:
    1. *Physician Advisory Review:* Active during MVP to audit clinical features, boundary conditions, and emergency triggers.
    2. *Clinical Content Review:* Active during MVP to verify health literacy, educational copy, and patient communication.
    3. *Institutional Ethics / IRB Protocol:* Formal research protocol drafted in parallel during MVP, submitted prior to any human subject testing.
    4. *Regulatory Applicability Assessment:* Systematic review under FDA guidance (including Jan 2026 CDS guidance), EU MDR, UK MHRA, and CDSCO rules; regulatory status remains formally undetermined during MVP development.
  - *Intended Purpose:* Ensures rigorous clinical safety and content oversight during development while preparing formal ethics and regulatory determinations in parallel without making unverified exemption claims.
  - *Pros:* High clinical rigor; zero premature claims of device exemption or certification.
  - *Cons:* Requires coordinating four distinct oversight workflows.
- **Option B: Pre-Development Institutional IRB Protocol & Regulatory Pre-Submission**
  - *Structure:* Require formal hospital or university institutional sponsorship, IRB ethics approval, and an official FDA pre-submission (Q-Submission) to be fully approved before any software engineering begins.
  - *Pros:* Complete institutional and regulatory alignment prior to writing code.
  - *Cons:* 6 to 12-month institutional lead time; high upfront financial cost; inappropriate for an early-stage prototype using synthetic data.
- **Recommendation:** **Option A for MVP software release.**

---

### Question 3 (DEC-003): Cardiovascular Prediction Scope (Task A vs. Task B)
- **Option A (Recommended): Task A MVP Machine Learning Only (Task B Relegated to Future Research)**
  - *Scope:* Focus the MVP machine learning subsystem strictly on Task A (experimental classification of the heart-disease target in the retrospective UCI Cleveland cohort). Completely remove Task B (prospective 10-year risk calculators like PCE or PREVENT) from the MVP codebase, milestone plan, and deliverables.
  - *Clinical Context:* The **2026 ACC/AHA Multisociety Dyslipidemia Guideline** formally adopted the **AHA PREVENT equations** (published late 2023 / early 2024) to replace the 2013 Pooled Cohort Equations (PCE) for primary prevention in US adults aged 30–79. However, PREVENT is US-derived, and other nations use their own validated risk scores (UK NICE uses QRISK3, Europe uses SCORE2, India uses WHO/CSI charts). Task B requires multi-country guideline harmonization and clinical validation, making it unsuitable for the initial MVP.
  - *Pros:* 100% scientifically defensible; eliminates clinical confusion between cross-sectional catheterization disease classification and future event forecasting.
  - *Cons:* Users do not receive a 10-year percentage risk estimate in the MVP release.
- **Option B: Implement Task B in MVP via a Deterministic Calculator**
  - *Scope:* Add an ACC/AHA PCE or PREVENT calculator into the MVP release alongside Task A.
  - *Pros:* Satisfies user requests for a 10-year heart attack risk number.
  - *Cons:* Scientifically problematic; high risk of users conflating experimental AI classification with guideline-directed prospective risk; geographic limitations.
- **Recommendation:** **Option A.**

---

### Question 4 (DEC-004): Geographic Adapter Architecture & Localization Goal
- **Option A (Recommended): Universal Country Adapter Pattern as an Architectural Extensibility Goal**
  - *Scope:* Deploy the universal country configuration engine (ADR-011) as an architectural extensibility design pattern to decouple core logic from national rules. Seed initial demonstration profiles for the United States (US), India (IN), and the United Kingdom (UK) to test unit conversions ($\text{mg/dL} \leftrightarrow \text{mmol/L}$), currencies, emergency numbers (911/112/999), and directory schemas using synthetic data.
  - *Crucial Governance Boundary:* Universal country adapter support is an **architectural extensibility goal and design pattern**, NOT proof of operational support, clinical validation, or regulatory readiness in every country. Operational readiness and regulatory compliance must be established individually per jurisdiction.
  - *Pros:* Proves multi-country extensibility and verifies unit conversion math in MVP without geographical lock-in.
  - *Cons:* Requires maintaining synthetic seed directory data for three jurisdictions.
- **Option B: Single Jurisdiction (US Only) Baseline for MVP**
  - *Scope:* Restrict MVP strictly to US clinical conventions (mg/dL only, 911 only); defer international adapter architecture to post-MVP.
  - *Pros:* Simpler initial directory footprint.
  - *Cons:* Fails to validate international unit conversions and localization engine in the initial release.
- **Recommendation:** **Option A.**

---

### Question 5 (DEC-005): Data Classification & Real Patient Data Prohibition
- **Option A (Recommended): Three-Tier Data Classification Policy (Category C Strictly Prohibited in MVP)**
  - *Policy:* Formally establish and enforce three distinct data categories:
    - **Category A (Public Research Datasets):** Publicly available de-identified datasets (UCI Cleveland, 303 records) used exclusively for model training, offline validation, and calibration.
    - **Category B (Synthetic Application Data):** 100% synthetically generated personas, UI fixtures, and mock clinical records (`scripts/generate_synthetic_patients.py`). Plausible physiological distributions with zero link to real individuals. Used for all application development, integration testing, demonstrations, and staging.
    - **Category C (Real Patient Information):** Real PHI/PII. **Strictly prohibited** across all MVP milestones (01–20).
  - *Pros:* Complete protection against data breaches, regulatory violations, and privacy liabilities during development.
  - *Cons:* Real clinical usability studies must wait for a subsequent protocol phase under institutional governance.
- **Option B: Authorize Real Patient Pilot Data in Staging (Permit Category C)**
  - *Policy:* Allow beta testing with real patient health data during Milestone 20 staging acceptance.
  - *Pros:* Tests system with live clinical records.
  - *Cons:* Severe regulatory, legal, and privacy exposure. Applicable ethics, privacy, contractual, and regulatory requirements depend on the jurisdiction and institutional context (e.g., HIPAA BAAs for US covered entities, GDPR Article 28 DPAs in the EU/UK, DPDP compliance in India, and local institutional ethics review). Attempting to ingest Category C real patient data during MVP would introduce complex cross-jurisdictional compliance burdens before core functionality is verified.
- **Recommendation:** **Option A.**
- **Recommendation:** **Option A.**

---

## 3. Action Required from Stakeholder

Please review these five questions and indicate your choices (e.g., *"Approve Recommendations: 1A, 2A, 3A, 4A, 5A"* or specify custom preferences). 

**Antigravity will pause and wait for your selection before Milestone 01 is authorized.**
