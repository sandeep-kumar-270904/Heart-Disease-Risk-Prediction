# GLOBAL PRIVACY AND HEALTHCARE REGULATORY REVIEW

**Document Reference:** `docs/security/GLOBAL_PRIVACY_AND_REGULATORY_REVIEW.md`  
**Phase:** 09 — Security, Privacy, Data Protection & Threat Modelling  
**Status:** Approved Technical Architecture & Regulatory Audit  
**Author:** Healthcare Regulatory Specialist & International Privacy Counsel  
**Traceability:** NFR-LEGAL-01, NFR-PRIV-01, ADR-011  

---

## 1. Executive Summary & Regulatory Disclaimer

In strict accordance with **ADR-011 (Global Country-Configurable Architecture)**, HeartXAI 2.0 is designed to operate globally via country-specific configuration modules. However, **architectural configurability must never be conflated with automatic legal compliance**. 

> [!CAUTION]
> **MANDATORY LEGAL DISCLAIMER:**  
> HeartXAI 2.0 is **NOT** officially certified under, nor does it claim formal legal compliance with, the US Health Insurance Portability and Accountability Act (HIPAA), the European Union General Data Protection Regulation (EU GDPR), or India's Digital Personal Data Protection Act, 2023 (DPDP Act). No regulatory authority has reviewed or approved this software. Formal legal counsel review and independent third-party audits are mandatory prior to onboarding real patients or deploying in any clinical jurisdiction.

---

## 2. Regulatory Review: India — Digital Personal Data Protection Act, 2023 (DPDP Act)

### 2.1 Official Primary Sources & Status
- **Statute:** Digital Personal Data Protection Act, 2023 (Act No. 22 of 2023). Enacted by the Parliament of India, published in the Gazette of India on August 11, 2023.
- **Authority:** Ministry of Electronics and Information Technology (MeitY), Government of India.
- **Access Date:** Verified November 18, 2026.
- **Commencement Status:** The Act was officially notified on August 11, 2023; specific operative provisions and implementing rules (governing Data Protection Board formation, consent manager architectures, and breach notification thresholds) are rolling out progressively via central government notification.

### 2.2 Scope & Applicability to HeartXAI
- Applies to processing of digital personal data within India, and processing outside India if related to offering goods or services to Data Principals within India.
- HeartXAI acts as a **Data Fiduciary** determining the purpose and means of processing personal data.

### 2.3 Key Obligations Affecting Product Design
1. **Notice Requirement (Section 5):** The Data Fiduciary must give itemized notice of personal data collected, purpose of processing, how to exercise rights, and how to complain to the Data Protection Board. **Must be available in English and any of the 22 languages specified in the Eighth Schedule to the Constitution of India**.
2. **Consent Standard (Section 6):** Consent must be free, specific, informed, unconditional, and unambiguous with clear affirmative action.
3. **Data Principal Rights (Sections 11–13):** Right to access summary of personal data, right to correction and erasure, right of grievance redressal, right to nominate.
4. **Data Protection Board (DPB) Breach Reporting (Section 8(6)):** Mandatory reporting of any personal data breach to the Board and to each affected Data Principal.

---

## 3. Regulatory Review: European Union — General Data Protection Regulation (EU GDPR)

### 3.1 Official Primary Sources & Status
- **Statute:** Regulation (EU) 2016/679 of the European Parliament and of the Council of 27 April 2016. Official Journal of the European Union, L 119, 4 May 2016.
- **Access Date:** Verified November 18, 2026.
- **Operative Status:** Fully in force across all European Union member states since May 25, 2018.

### 3.2 Scope & Applicability to HeartXAI
- Applies under Article 3(2) (extraterritorial effect) if HeartXAI offers cardiovascular assessment services to individuals residing in the European Union.
- HeartXAI acts as a **Data Controller** for direct patient accounts.

### 3.3 Key Obligations Affecting Product Design
1. **Special Category Health Data (Article 9):** Processing of health data (cardiovascular biomarkers, prediction outputs) is prohibited unless an explicit exception under Article 9(2) applies — specifically **Article 9(2)(a) (Explicit Consent)**.
2. **Automated Individual Decision-Making & Profiling (Article 22):** 
   - Article 22(1) grants individuals the right not to be subject to a decision based solely on automated processing which produces legal or similarly significant effects.
   - **Architectural Safeguard:** HeartXAI is explicitly designed as a **Clinical Decision Support (CDS) aid**, requiring human-in-the-loop interpretation by a licensed physician. It never executes automated, legally binding clinical actions.
3. **Right to an Explanation (Recital 71):** Requires transparency regarding the logic involved in automated risk scores, directly satisfied by our TreeSHAP explainability engine.
4. **International Data Transfers (Chapter V):** Transferring EU resident health data to non-EU servers requires an Adequacy Decision (Article 45) or Standard Contractual Clauses (SCCs, Article 46) paired with encryption controls.

---

## 4. Regulatory Review: United States — HIPAA & Clinical Decision Support (CDS)

### 4.1 Official Primary Sources & Status
- **Statute:** Health Insurance Portability and Accountability Act of 1996 (HIPAA, Pub. L. 104-191) and the HITECH Act (2009). Codified at 45 CFR Parts 160, 162, and 164 (Privacy, Security, and Breach Notification Rules).
- **Agency Guidance:** U.S. Department of Health and Human Services (HHS) Office for Civil Rights (OCR) Guidance on Direct-to-Consumer Health Apps (updated 2022); FDA Guidance on Clinical Decision Support Software (issued Sept 2022).
- **Access Date:** Verified November 18, 2026.

### 4.2 Scope & Applicability to HeartXAI
- **Covered Entity vs. Direct-to-Consumer (DTC):**
  - If HeartXAI is used directly by consumers on their personal devices without a hospital contract, HeartXAI is generally **not** a HIPAA Covered Entity or Business Associate (though FTC Health Breach Notification Rule applies).
  - If HeartXAI contracts with a US healthcare provider, clinic, or hospital system to process patient assessments, HeartXAI becomes a **Business Associate** and must execute a formal **Business Associate Agreement (BAA)** and comply with 45 CFR Part 164.
- **FDA SaMD vs. CDS Exemption:**
  - Under Section 520(o)(1)(E) of the FD&C Act, software that provides healthcare recommendations to clinicians is **exempt from medical device regulation** if it explains the underlying clinical rationale and allows the clinician to independently review the basis of the recommendation. HeartXAI's open TreeSHAP feature attribution display complies with this non-device CDS criterion.

---

## 5. Comparative Jurisdictional Synthesis Matrix

| Dimension | India (DPDP Act 2023) | European Union (GDPR) | United States (HIPAA / FTC) |
| :--- | :--- | :--- | :--- |
| **Protected Data Concept** | Digital Personal Data | Personal Data & Art. 9 Health Data | Protected Health Information (PHI) |
| **Lawful Processing Basis** | Consent or Legitimate Uses | Explicit Consent (Art. 9(2)(a)) | Treatment, Payment, Healthcare Ops |
| **Language Obligations** | Notice in English + 22 Sched. Languages | Notice in Member State Language | Culturally & Linguistically Appropriate Services |
| **Breach Reporting Window** | Immediate / As notified by DPB Rules | Strictly within 72 hours (Art. 33) | 60 days to OCR ($\ge 500$ individuals) |
| **Cross-Border Transfers** | Permitted unless blacklisted by Central Govt | Restricted unless SCCs or Adequacy | Permitted with BAA & Security Rule |
| **Automated Profiling Rights** | Governed by general fairness | Art. 22 Right to Human Intervention | Clinical Decision Support criteria |

---

## 6. Engineering Architecture vs. Legal Practice Demarcation

HeartXAI enforces a strict separation between technical engineering capabilities and formal legal compliance:

```text
┌────────────────────────────────────────────────────────────────────────┐
│               Technical Engineering Deliverables (Phase 09)             │
│  - AES-256 Encryption at Rest & TLS 1.3 in Transit                     │
│  - Granular Consent Ledgers with Instant Withdrawal                    │
│  - Automated Machine-Readable JSON Export (DSAR Workflow)              │
│  - Immutable Append-Only Audit Logging with PII Redaction              │
│  - Country-Configurable Directory & Localization Interfaces            │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ Mandatory Bridge
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   Legal & Regulatory Tasks (Pre-Launch)                │
│  - Engagement of Jurisdictional Legal Counsel                          │
│  - Execution of Business Associate Agreements (BAAs) in US             │
│  - Registration with Data Protection Board in India                    │
│  - Publication of Official Terms of Service & Privacy Policy           │
│  - Formal Clinical Decision Support Regulatory Filings                 │
└────────────────────────────────────────────────────────────────────────┘
```
