# HeartXAI 2.0 — Global Architecture Readiness
**Document ID:** HX-PR-005  
**Version:** 2.2.0 (Phase 12.2 Revision)  
**Phase:** 12.2 — Final Governance Resolution & Evidence Reconciliation  
**Author:** Principal Software Architect & Internationalization Specialist  
**Status:** Approved for Implementation Planning — Globally Configurable Architecture (Category B Synthetic Scope)  
**Date:** November 2026  

---

## 1. Executive Summary

Healthcare systems, clinical measurement conventions, statutory privacy frameworks, and emergency response infrastructures vary fundamentally across international jurisdictions. In accordance with **ADR-011 (Global Country Configuration Architecture)**, HeartXAI 2.0 establishes a pluggable adapter pattern that decouples the core platform engine from localized national rules.

### Reclassification: Architectural Extensibility Goal
Universal ISO country adapter support is an **architectural extensibility goal and design pattern**, NOT proof of operational support, clinical validation, or regulatory readiness in every country:
- **Design Pattern:** The adapter pattern ensures that software interfaces (unit conversion, hotline display, locale formatting, and directory schemas) are structurally decoupled from US-centric assumptions and can theoretically accommodate any ISO 3166-1 alpha-2 code without rewriting core code.
- **Operational Reality:** Full operational support requires locally verified provider directories, accredited language translations, live emergency service routing, and country-specific data privacy compliance.
- **Regulatory Reality:** Regulatory clearance and clinical validation must be pursued individually on a per-jurisdiction basis. HeartXAI makes **zero claims of operational readiness, clinical validity, or regulatory clearance** in any country.
- **Initial Engineering Scope:** The United States (`US`), India (`IN`), and United Kingdom (`GB`) are used strictly as initial demonstration configurations to test unit conversions ($\text{mg/dL} \leftrightarrow \text{mmol/L}$) and UI formatting using **Category B synthetic demonstration data**. Real patient data (Category C) remains strictly prohibited across all MVP milestones (01–20).

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
5. **Independent Jurisdictional Regulatory Review:** Formal medical device software classification must be conducted independently per jurisdiction by qualified healthcare regulatory legal counsel (e.g., US FDA under § 520(o)(1)(E) and Jan 2026 CDS guidance; EU MDR 2017/745 Rule 11 and MDCG 2019-11; UK MHRA under UK MDR 2002; and India CDSCO under Medical Device Rules 2017). Criteria from one jurisdiction cannot be substituted as a universal test across international borders. All statutory and legal interpretations require formal review by qualified legal counsel in each respective territory.
