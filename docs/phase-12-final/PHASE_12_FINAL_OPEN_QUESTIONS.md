# HeartXAI 2.0 — Phase 12.2 Final Open Governance Questions
**Document ID:** HX-PR-018  
**Version:** 3.0.0 (Phase 12.2 Stakeholder Approval Baseline)  
**Phase:** 12.2 — Final Governance Resolution & Stakeholder Approval  
**Author:** Technical Program Manager, Principal Software Architect & Clinical Safety Reviewer  
**Status:** Approved by Stakeholder — Milestone 01 Formally Authorized  
**Date:** 23 November 2026  

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
*Governance Principle:* Physician advisory review, clinical content review, institutional ethics / IRB determination, and regulatory assessment are four distinct, concurrent governance tracks across the software lifecycle. Explicit distinctions govern each activity tier:
1. **Ordinary Synthetic-Data Software Development:** Developing prototype software using 100% Category B synthetic fixtures does NOT automatically require IRB/REC approval merely because the software is healthcare-related, provided it complies with applicable institutional policies, software safety standards, and legal requirements. An IRB protocol or FDA Q-Submission is NOT a universal prerequisite for ordinary synthetic-data prototype development.
2. **Human Participant Research & Usability Studies:** Any activities involving live human participants (e.g., clinician usability studies, cognitive walkthroughs, patient interaction evaluations) require an appropriate **documented institutional ethics determination** from the applicable Institutional Review Board (IRB), Research Ethics Committee (REC), or institutional authority. The project team shall not assume every usability activity is automatically regulated human-subject research, nor assume every activity is exempt without documented institutional determination.
3. **Clinical Evaluation & Deployment:** Formal clinical evaluation, diagnostic validation, and prospective deployment require separate clinical governance, patient privacy safeguards, safety risk management, and formal regulatory clearance appropriate to the intended use and target jurisdiction.

- **Option A (Recommended): Multi-Track Phased Governance for MVP**
  - *Structure:* Maintain all four governance tracks as distinct, concurrent workflows:
    1. *Physician Advisory Review:* Active during MVP to audit clinical features, boundary conditions, and emergency triggers.
    2. *Clinical Content Review:* Active during MVP to verify health literacy, educational copy, and patient communication.
    3. *Institutional Ethics / Determination Gate:* Documented determination obtained from applicable institutional ethics authority (IRB/REC) prior to initiating any human-participant usability or research activities, calibrated to the activity tier.
    4. *Regulatory Applicability Assessment:* Systematic review under FDA guidance (including Jan 2026 CDS guidance), EU MDR Rule 11 & MDCG 2019-11 rev.1 (June 2025), UK MHRA, and CDSCO MDR 2017 & MDSW Guidance (21 July 2026 Table 2 matrix); regulatory status remains formally undetermined during MVP development.
  - *Intended Purpose:* Ensures clinical safety and content oversight during development while establishing formal ethics determinations and regulatory mappings in parallel without making unverified exemption claims.
  - *Pros:* High clinical rigor; zero premature claims of device exemption or certification; appropriate governance calibrated by activity.
  - *Cons:* Requires coordinating four distinct oversight workflows.
- **Option B: Upfront Institutional Sponsorship Gate (Pre-Development IRB & Pre-Submission)**
  - *Structure:* Require formal institutional sponsorship, institutional ethics / IRB approval, and an official FDA pre-submission (Q-Submission) to be fully approved before any software engineering begins.
  - *Scope Distinction:* Conflates prototype software development with formal human-subject trials; introduces multi-month delays for early synthetic-data scaffolding.
  - *Pros:* Complete institutional and regulatory alignment prior to writing code.
  - *Cons:* 6 to 12-month institutional lead time; high upfront financial cost; introduces premature compliance gates for an early-stage synthetic-data prototype.
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
    - **Category A (Public Historical Human-Origin Research Data):** Publicly accessible, historical human-origin clinical research data (UCI Cleveland, 303 records) with documented privacy limitations. Omitted direct identifiers historically (dummy 0 for SSN/ccf), but lacks modern formal statutory de-identification certification (HIPAA Safe Harbor / Expert Determination) or verified GDPR anonymization. Requires documented dataset provenance, licensing terms, permitted research use, and privacy risk assessment prior to model training in Milestone 09. Confined strictly to offline model research.
    - **Category B (Synthetic Application Data):** Synthetically generated personas, UI fixtures, and mock clinical records (`scripts/generate_synthetic_patients.py`). Statistically derived from empirical multivariate reference distributions (UCI Cleveland benchmark); carries theoretical memorization and outlier disclosure risks; formal differential privacy is NOT implemented, and synthetic fixtures are strictly restricted to application testing and kept separate from all model evaluation datasets. Used for all application development, integration testing, demonstrations, and staging.
    - **Category C (Real Patient Information):** Real PHI/PII. **Strictly prohibited** across all MVP milestones (01–20).
  - *Pros:* Prohibiting Category C real patient data in the application avoids ingesting live clinical patient records into the web platform, eliminating clinical HIPAA/GDPR patient data breach notification obligations for runtime application operations. Establishes explicit research governance for Category A before training.
  - *Cons:* Category A carries residual historical human-origin research-data risks that must be assessed before training; standard software and infrastructure cybersecurity risks remain active across the platform and require continuous DevSecOps controls.
- **Option B: Real Patient Data Pilot (Outside Current MVP Scope — Requires Approved Scope Change)**
  - *Status & Scope Boundary:* **Strictly outside the current MVP scope.** Option B represents a theoretical future path and **cannot be activated** while the project's Category C prohibition remains in force.
  - *Prerequisites for Future Activation:* Selecting Option B cannot occur casually and would require:
    1. A formally approved scope change by project leadership.
    2. Separate privacy, security, clinical governance, ethics, and jurisdiction-specific regulatory assessments.
    3. Formal institutional ethics / IRB protocol review and approval for human-subject data collection.
    4. Execution of mandatory statutory data protection agreements (e.g., HIPAA BAAs for US covered entities, GDPR Article 28 DPAs in the EU/UK, DPDP compliance frameworks in India).
    5. Comprehensive third-party security audits for production PHI/PII handling.
  - *Strict Legal Invariant:* No implementation involving real patient information is authorized by this documentation correction. Category C real patient health information remains **strictly prohibited** across all MVP milestones (01–20).
- **Recommendation:** **Option A (Category C Strictly Prohibited in MVP).**

---

## 3. Stakeholder Decision Record & Implementation Authorization

- **Selection Date:** 23 November 2026.
- **Stakeholder Decision:** Approved all recommended options:
  1. **DEC-001 (Hosting):** Option A (Tier A Minimal VPS, ~$25–$55/mo).
  2. **DEC-002 (Clinical Governance):** Option A (Multi-Track Phased Governance).
  3. **DEC-003 (Cardiovascular Prediction):** Option A (Task A MVP Only).
  4. **DEC-004 (Localization Scope):** Option A (Adapter Extensibility Goal).
  5. **DEC-005 (Data Classification):** Option A (Category C Strictly Prohibited in MVP).
- **Milestone 01 Authorization:** **Granted.** Commencement of Milestone 01 (Repository & Development Environment Foundation) is authorized.
