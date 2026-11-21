# HeartXAI 2.0 — Phase 12 Final Open Questions
**Document ID:** HX-PR-018  
**Version:** 1.0.0  
**Phase:** 12 — Final Pre-Implementation Audit, Architecture Consolidation & Master Development Roadmap  
**Author:** Technical Program Manager & Principal Software Architect  
**Status:** Awaiting Stakeholder Decision Sign-Off  
**Date:** November 2026  

---

## 1. Executive Summary

While the technical, algorithmic, and database specifications for HeartXAI 2.0 are 100% complete and verified, production implementation cannot proceed blindly on operational assumptions. 

This document articulates the **five strategic decisions** that require explicit stakeholder selection and approval before Milestone 01 engineering begins.

---

## 2. The Five Governance Decisions

### Question 1: Production Hosting Architecture & Budget Tier
- **Context:** The DevOps specification provides two fully articulated infrastructure configurations.
- **Option A (Recommended): Tier A — Single VPS with Docker Compose (~$20/month)**
  - *Details:* 4 vCPU, 8 GB RAM VPS (Hetzner / DigitalOcean) running Nginx, FastAPI, PostgreSQL 16, and Redis in isolated containers. Encrypted nightly backups (ADR-012) to AWS S3 / Cloudflare R2 ($2/month).
  - *Pros:* Extremely cost-effective for MVP, trivial local reproducibility, zero cloud lock-in. Easily handles up to 500 daily active clinical assessments.
  - *Cons:* Vertical scaling limits; manual failover if VPS hardware crashes.
- **Option B: Tier B — AWS Managed Cloud Infrastructure (~$140/month)**
  - *Details:* AWS ECS Fargate container tasks, AWS RDS PostgreSQL 16 Multi-AZ, AWS ElastiCache Redis, AWS Application Load Balancer.
  - *Pros:* Automatic horizontal scaling, automated managed database failover, enterprise SLA.
  - *Cons:* Fixed high cost during pre-launch testing and beta phase.
- **Recommendation:** **Option A for Milestones 01–20.** Migrate to Option B when user volume exceeds 1,000 assessments/day.

---

### Question 2: Clinical Governance & Medical Disclaimer Authority
- **Context:** HeartXAI 2.0 provides clinical decision support and cardiovascular risk stratification.
- **Option A (Recommended): Advisory Review & Prominent Statutory Disclaimers**
  - *Details:* Adopt the non-diagnostic clinical disclaimers audited in `HEALTHCARE_AND_SCIENTIFIC_VALIDITY_AUDIT.md`. Feature reviews conducted by clinical collaborators.
  - *Pros:* Aligns with FDA 21st Century Cures Act CDS exemptions (Section 520(o)(1)(E)); allows agile deployment without institutional delays.
  - *Cons:* Requires strict adherence to prohibited marketing claims.
- **Option B: Formal Institutional Review Board (IRB) / Medical Ethics Committee**
  - *Details:* Require formal protocol submission to an academic hospital IRB before releasing the tool to external users.
  - *Pros:* Highest level of institutional prestige.
  - *Cons:* 3 to 6-month procedural delay.
- **Recommendation:** **Option A.**

---

### Question 3: Cardiovascular Risk Scope Resolution (Task A vs. Task B)
- **Context:** The UCI Cleveland dataset supports ONLY cross-sectional angiographic CAD classification (Task A). Longitudinal 10-year heart attack risk (Task B) cannot be derived from this dataset.
- **Option A (Recommended): Task A ML Subsystem + Independent Deterministic Task B Rule Engine**
  - *Details:* Calibrated XGBoost and TreeSHAP compute Task A. In Milestone 14, implement the ACC/AHA 2013 Pooled Cohort Equations as a deterministic rule calculator displayed in a separate, labeled card with distinct clinical disclaimers.
  - *Pros:* Satisfies patient desire for 10-year risk context without compromising scientific integrity.
  - *Cons:* Requires two separate explanation cards in the UI.
- **Option B: Pure Task A Only (Defer Task B to Post-MVP)**
  - *Details:* Strictly limit the application to Task A (angiographic CAD likelihood).
  - *Pros:* Ultimate scientific simplicity; single risk score.
  - *Cons:* Some patients may expect a 10-year percentage risk calculator.
- **Recommendation:** **Option A.**

---

### Question 4: Initial Geographic Launch Sequence
- **Context:** ADR-011 establishes global configuration for US, IN, and UK.
- **Option A (Recommended): Simultaneous Tri-Country Support at Launch (US, IN, UK)**
  - *Details:* Deploy pre-configured country adapters, unit conversion engines, and initial emergency directories for all three countries at Milestone 15.
  - *Pros:* Demonstrates global capability from day one; validates unit conversions in production.
  - *Cons:* Requires maintaining seed directory data for three jurisdictions.
- **Option B: Staged Rollout (US First, Followed by IN and UK)**
  - *Details:* Launch US profile first; enable IN and UK in post-MVP minor releases.
  - *Pros:* Focuses directory verification on a single jurisdiction.
  - *Cons:* International testers must use US units initially.
- **Recommendation:** **Option A.**

---

### Question 5: Healthcare Directory Data Sourcing Strategy
- **Context:** Patients must be able to discover cardiologists and emergency cardiac hospitals.
- **Option A (Recommended): Curated Static Seed Database with Admin Management**
  - *Details:* Seed the database with 150+ verified academic cardiac centers, trauma hospitals, and cardiology practices across key metropolitan areas (US: NY, CA, TX; UK: London, Manchester; IN: Delhi, Mumbai, Bengaluru). Admins can add/edit via Milestone 17 Admin Console.
  - *Pros:* Zero external API dependencies, zero recurring search API costs, guaranteed verified records.
  - *Cons:* Requires manual periodic curation.
- **Option B: Live Third-Party Directory API Integration (e.g., Google Places / Healthgrades API)**
  - *Details:* Query external commercial APIs dynamically based on patient geolocation.
  - *Pros:* Broader geographic coverage.
  - *Cons:* Monthly API billing costs, rate limits, potential unverified clinical listings.
- **Recommendation:** **Option A for MVP.**
