# HeartXAI 2.0 — Global Architecture Readiness
**Document ID:** HX-PR-005  
**Version:** 2.2.0 (Phase 12.2 Revision)  
**Phase:** 12.2 — Final Governance Resolution & Evidence Reconciliation  
**Author:** Principal Software Architect & Internationalization Specialist  
**Status:** Approved for Implementation Planning — Globally Configurable Architecture (Category B Synthetic Scope)  
**Date:** November 2026  

---

## 1. Executive Summary

Healthcare systems, clinical measurement conventions, statutory privacy frameworks, and emergency response infrastructures vary fundamentally across international jurisdictions. In accordance with **ADR-011 (Global Country Configuration Architecture)**, HeartXAI 2.0 establishes a **globally configurable architecture** that decouples the core platform engine from localized national rules.

While the United States (`US`), India (`IN`), and United Kingdom (`GB`) are used as initial demonstration configurations, the Country Adapter architecture is designed to support **any ISO 3166-1 alpha-2 jurisdiction** declaratively without altering core business logic or machine learning pipelines.

### Mandatory Compliance & Governance Caveats
> **CRITICAL POSTURE STATEMENT 1 (Data Prohibition):** The initial implementation, demonstration, and testing milestones are restricted strictly to **Category B synthetic application data**. Real patient data (Category C) is strictly prohibited.

> **CRITICAL POSTURE STATEMENT 2 (No Unverified Clinical Claims):** HeartXAI makes **no claims of clinical validation, regulatory clearance, or statutory approval** in the US, UK, India, or any other country. Demonstrating country adapters tests architectural extensibility only.

---

## 2. Universal Country Adapter Architecture (ADR-011)

The platform core interfaces with national rules via strongly typed declarative Pydantic schemas:

```python
# Universal Country Adapter Schema (ADR-011)
class CountryConfiguration(BaseModel):
    country_code: str               # ISO 3166-1 alpha-2 (e.g., "US", "IN", "GB", "AU", "CA", "DE")
    country_name: str
    default_locale: str             # BCP 47 (e.g., "en-US", "hi-IN", "en-GB", "de-DE")
    supported_locales: list[str]
    timezones: list[str]            # IANA timezone identifiers
    currency_code: str              # ISO 4217 (e.g., "USD", "INR", "GBP", "EUR")
    currency_symbol: str
    
    # Clinical Measurement & Biomarker Unit System
    unit_system: UnitSystemConfig   # Blood pressure (mmHg), cholesterol, glucose
    
    # Emergency Hotline & Crisis Assistance
    emergency_number: str           # e.g., "911", "112", "999", "000", "110"
    emergency_services_name: str
    
    # Regulatory & Privacy Compliance
    privacy_framework: str          # HIPAA, DPDPA 2023, UK-GDPR, EU-GDPR, etc.
    statutory_disclaimer_key: str
    
    # Healthcare Guidelines & Directory Standards
    primary_guideline_source: str   # e.g., "ACC/AHA", "CSI/ICMR", "NICE", "ESC"
    physician_license_registry: str # e.g., "NPI" (US), "NMC" (IN), "GMC" (UK)
```

---

## 3. Initial Demonstration Profiles vs. Global Extensibility

```
+---------------------------------------------------------------------------------------------------------+
|                                    DEMONSTRATION COUNTRY PROFILES MATRIX                                |
+-----------------------------+---------------------------+---------------------------+---------------------------+
| Parameter                   | United States (US)        | India (IN)                | United Kingdom (GB)       |
+-----------------------------+---------------------------+---------------------------+---------------------------+
| Emergency Hotline           | 911                       | 112 / 102                 | 999 / 111                 |
| Measurement Units: Chol     | mg/dL                     | mg/dL                     | mmol/L                    |
| Measurement Units: Glucose  | mg/dL                     | mg/dL                     | mmol/L                    |
| Measurement Units: BP       | mmHg                      | mmHg                      | mmHg                      |
| Currency Symbol             | $ (USD)                   | ₹ (INR)                   | £ (GBP)                   |
| Privacy Framework           | HIPAA / HITECH            | DPDPA 2023                | UK-GDPR / DPA 2018        |
| Primary Guideline Source    | ACC/AHA                   | CSI / ICMR                | NICE CG181 / NG238        |
| Synthetic Data Scope        | Category B Synthetic      | Category B Synthetic      | Category B Synthetic      |
| Clinical Validation Status  | **None (Unvalidated)**    | **None (Unvalidated)**    | **None (Unvalidated)**    |
+---------------------------------------------------------------------------------------------------------+
```

### Adding New Jurisdictions Declaratively
To support a new country (such as Germany `DE`, Australia `AU`, or Canada `CA`), an engineer adds a declarative JSON record to `shared/country-profiles.json` specifying the ISO code, locale, units, emergency numbers, and clinical guideline references. The core ingestion wizard, unit converter, and emergency components dynamically bind to the active country context without code alterations.

---

## 4. Biomarker Unit Conversion Engine Verification

Machine learning inference requires standardized input features regardless of the user's local measurement conventions:
- **Cholesterol:**
  $$\text{Chol}_{\text{mg/dL}} = \text{Chol}_{\text{mmol/L}} \times 38.67 \quad \Longleftrightarrow \quad \text{Chol}_{\text{mmol/L}} = \frac{\text{Chol}_{\text{mg/dL}}}{38.67}$$
- **Fasting Glucose:**
  $$\text{Glucose}_{\text{mg/dL}} = \text{Glucose}_{\text{mmol/L}} \times 18.0182 \quad \Longleftrightarrow \quad \text{Glucose}_{\text{mmol/L}} = \frac{\text{Glucose}_{\text{mg/dL}}}{18.0182}$$
- **Implementation Invariant:** The database persists biomarker inputs in both the user's native entered units (for UI display and auditability) and the standardized normalized units (for ML inference).

---

## 5. Pre-Conditions Before Enabling Real-World Regional Deployment

Before any jurisdiction is enabled for real patient data processing:
1. **Clinical Guideline Review:** Harmonize risk thresholds with local cardiology college standards (e.g., ESC, NICE, CSI).
2. **Data Protection Registration:** Complete statutory registrations (e.g., UK ICO registration, HIPAA BAA agreements, Indian DPB compliance).
3. **Emergency Directory Verification:** Confirm that local emergency numbers and cardiac centers are officially validated.
4. **Institutional Ethics Determination:** Obtain formal IRB/REC determination for clinical studies or patient onboarding in that nation.
