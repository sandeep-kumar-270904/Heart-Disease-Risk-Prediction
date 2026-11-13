# HeartXAI 2.0 — Phase 1 Research Summary & Source Register

**Document ID:** HXAI-DOC-007  
**Version:** 1.0.0  
**Phase:** Phase 1 — Product Research & Engineering Benchmarking  
**Status:** Complete / Ready for Review  
**Author:** Principal Product Engineer & Software Architect  

---

## 1. Executive Summary of Phase 1 Research

Phase 1 of the HeartXAI 2.0 engineering mission established the theoretical, methodological, and architectural foundation required to build a genuinely production-grade cardiovascular health platform. Rather than jumping prematurely into code, we systematically benchmarked the world's leading technology organizations, analyzed six established design systems, formulated a 14-dimension measurable quality framework, established evidence-based user archetypes, designed an anxiety-reducing product experience strategy, and rigorously evaluated our technology stack.

### Key Insights Synthesized Across Disciplines:
1. **Engineering Discipline:** High-reliability systems prioritize automated hermetic testing (Google Testing Pyramid), idempotency on mutation endpoints (Amazon Builders' Library), defense-in-depth security (Stripe API standards), and graceful degradation under service strain (Netflix Chaos Engineering).
2. **Design System Rigor:** Clinical applications demand high legibility, strict contrast ratios, unambiguous tabular figures, and semantic color mapping (Apple HIG, IBM Carbon, Material Design 3). We have synthesized these into the independent HeartXAI "Aethelgard Clinical" design language.
3. **Medical & Algorithmic Integrity:** Machine learning models in healthcare must distinguish dataset-based disease classification from prospective population event risk. Predictions must be calibrated, explanations must be mathematically verifiable (TreeSHAP), and counterfactual interventions must respect immutable human biological limits.
4. **Architectural Cohesion:** The evaluated stack (React, TypeScript, Vite, Tailwind CSS, FastAPI, PostgreSQL, Scikit-learn, XGBoost, SHAP) provides optimal developer ergonomics, type safety, and sub-500ms inference latency without distributed microservice complexity.

---

## 2. Complete Primary Source Register

In accordance with our strict research standards, every claim and architectural choice is mapped to published primary sources:

| Source ID | Author / Organization | Publication Title / Reference | Publication Date | Canonical URL | Claim / Architecture Decision Supported |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SRC-001** | Beyer, B., Jones, C., Petoff, J., Murphy, N. (Google) | *Site Reliability Engineering: How Google Runs Production Systems* | 2016 | https://sre.google/books/ | Informs HeartXAI SLOs, Error Budgets, and hermetic CI testing pyramid. |
| **SRC-002** | Google Design | *Material Design 3 Specification* | 2021–2024 | https://m3.material.io/ | Informs 3-tier design token architecture and accessible color contrast. |
| **SRC-003** | Apple Inc. | *Apple Human Interface Guidelines* | 2023–2024 | https://developer.apple.com/design/ | Informs minimum 44x44pt hit targets, Dynamic Type, and data minimization. |
| **SRC-004** | Meta Open Source | *React 18 & 19 Architecture Documentation* | 2022–2024 | https://react.dev/ | Informs component-driven UI, declarative state, and concurrent batching. |
| **SRC-005** | Amazon Web Services | *Amazon Builders' Library: Making Retries Safe with Idempotent APIs* | 2019 | https://aws.amazon.com/builders-library/ | Informs `Idempotency-Key` headers on clinical assessment submissions. |
| **SRC-006** | Basiri, A. et al. (Netflix) | *Chaos Engineering: Building Confidence in System Behavior* | 2016 | https://netflixtechblog.com/ | Informs graceful UI degradation when XAI explanation timeouts occur. |
| **SRC-007** | Microsoft Design | *Fluent 2 Design System & Inclusive Design Toolkit* | 2022–2024 | https://fluent2.microsoft.design/ | Informs WCAG 2.1 AA keyboard navigation, ARIA live announcements, and contrast. |
| **SRC-008** | Stripe Engineering | *Stripe API Reference & Designing Robust APIs* | 2020–2024 | https://stripe.com/docs/api | Informs structured JSON error models and backward-compatible route versioning. |
| **SRC-009** | IBM Corporation | *Carbon Design System* | 2021–2024 | https://carbondesignsystem.com/ | Informs high-density clinical data tables, monospace telemetry, and modal focus traps. |
| **SRC-010** | Shopify Design | *Polaris Design System* | 2022–2024 | https://polaris.shopify.com/ | Informs real-time inline form validation and non-blocking notification banners. |
| **SRC-011** | Atlassian | *Atlassian Design System* | 2022–2024 | https://atlassian.design/ | Informs responsive layout grids, card spacing tokens, and tabular filters. |
| **SRC-012** | Lundberg, S. M. et al. | *From local explanations to global understanding with explainable AI for trees* (Nature MI) | 2020 | https://doi.org/10.1038/s42256-019-0138-9 | Mathematical foundation for exact TreeSHAP local feature attribution. |
| **SRC-013** | Goff, D. C. et al. (ACC/AHA) | *2013 ACC/AHA Guideline on the Assessment of Cardiovascular Risk* (Circulation) | 2014 | https://doi.org/10.1161/01.cir.0000437741.48606.98 | Mathematical formulation for 10-year prospective ASCVD Pooled Cohort Equations. |
| **SRC-014** | Detrano, R. et al. | *International application of a new probability algorithm for the diagnosis of coronary artery disease* (Am J Cardiol) | 1989 | https://archive.ics.uci.edu/dataset/45/heart+disease | Benchmark UCI Cleveland Heart Disease dataset specification (13 clinical features). |
| **SRC-015** | W3C / Web Accessibility Initiative | *Web Content Accessibility Guidelines (WCAG) 2.1* | 2018 | https://www.w3.org/TR/WCAG21/ | Informs accessibility compliance standards (contrast $> 4.5:1$, keyboard operability). |
| **SRC-016** | OWASP Foundation | *OWASP Top 10 Application Security Risks* | 2021 | https://owasp.org/Top10/ | Informs security controls against injection, broken auth, and sensitive data exposure. |
| **SRC-017** | U.S. Dept of Health & Human Services | *HIPAA Security Rule (45 CFR Part 160 and Part 164)* | 2003 / 2013 | https://www.hhs.gov/hipaa/ | Informs data minimization, patient data isolation, and immutable audit logs. |

---

## 3. Core Decisions Consolidated Across Phase 1

1. **Brand & Visual Language:** Adopt the independent "Aethelgard Clinical" design language—clean slate surfaces, midnight navy structural chrome, clinical azure accents, and semantic status indicators (emerald, amber, crimson).
2. **Clinical Target Separation:** Explicitly segregate the Cleveland ML classifier (coronary stenosis $\ge 50\%$) from the ACC/AHA ASCVD 10-year prospective risk equation in all views, schemas, and reports.
3. **Mathematical Invariance Guarantee:** Every TreeSHAP inference pass will programmatically assert $\left| f(x) - \left( \mathbb{E}[f(x)] + \sum \phi_i \right) \right| \le 10^{-5}$ before persisting the explanation.
4. **Counterfactual Plausibility Engine:** Enforce strict biological immutability on age, sex, and anatomical fluoroscopy; optimize modifiable lifestyle biomarkers (blood pressure, cholesterol, blood sugar) using normalized L1-distance within physiological boundaries.
5. **Quality Gate Verification:** Require all 14 quality dimensions to pass automated checks before any release is designated as production-ready.
