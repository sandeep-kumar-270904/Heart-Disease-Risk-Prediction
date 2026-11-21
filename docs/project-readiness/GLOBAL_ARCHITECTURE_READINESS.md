# HeartXAI 2.0 — Global Architecture Readiness
**Document ID:** HX-PR-005  
**Version:** 1.0.0  
**Phase:** 12 — Final Pre-Implementation Audit, Architecture Consolidation & Master Development Roadmap  
**Author:** Principal Software Architect & Application Security Architect  
**Status:** Approved for Implementation Planning  
**Date:** November 2026  

---

## 1. Executive Summary

A core architectural remediation established in Phase 03 and codified in **ADR-011 (Global Country Configuration Architecture)** is the decoupling of universal business logic from localized medical and operational rules. Healthcare systems, clinical guidelines, regulatory compliance mandates, measurement units, and emergency response infrastructures vary fundamentally by jurisdiction.

This document verifies the global architectural readiness of HeartXAI 2.0, details the Country Adapter interface, establishes data residency boundaries, and defines the explicit governance gates required before enabling any national jurisdiction.

---

## 2. Global Country Adapter Interface Specification

The platform architecture enforces a strict boundary between the core platform engine and localized Country Adapters. Every localized attribute is declared within a strongly typed Pydantic registry:

```python
# Conceptual Architecture Contract (ADR-011)
class CountryConfiguration(BaseModel):
    country_code: str               # ISO 3166-1 alpha-2 (e.g., "US", "IN", "GB")
    country_name: str
    default_locale: str             # BCP 47 (e.g., "en-US", "en-GB", "hi-IN")
    supported_locales: list[str]
    timezones: list[str]            # IANA timezone identifiers
    currency_code: str              # ISO 4217 (e.g., "USD", "INR", "GBP")
    currency_symbol: str
    
    # Clinical Measurement & Biomarker Unit System
    unit_system: UnitSystemConfig   # Units for blood pressure, glucose, cholesterol
    
    # Emergency & Crisis Assistance
    emergency_number: str           # e.g., "911", "999", "112"
    emergency_services_name: str
    poison_control_number: str | None
    
    # Regulatory & Statutory Compliance
    privacy_framework: PrivacyFrameworkType  # HIPAA, UK_GDPR, EU_GDPR, DPDPA_2023
    data_residency_required: bool
    statutory_disclaimer_key: str
    
    # Directory & Healthcare Verification
    physician_license_registry: str # e.g., "NPI" (US), "GMC" (UK), "NMC" (IN)
    directory_filter_defaults: dict[str, Any]
```

---

## 3. Initial Launch Country Profiles: US, IN, GB

The system provides out-of-the-box configurations for three primary launch jurisdictions:

```
+---------------------------------------------------------------------------------------------------------+
|                                    LAUNCH COUNTRY PROFILES MATRIX                                       |
+---------------------------------------------------------------------------------------------------------+
| Parameter                   | United States (US)        | India (IN)                | United Kingdom (GB)       |
+-----------------------------+---------------------------+---------------------------+---------------------------+
| Emergency Hotline           | 911                       | 112 / 102                 | 999 / 111                 |
| Primary Clinical Guideline  | ACC/AHA 2019 Prevention   | CSI / ICMR Guidelines     | NICE CG181 / NG238        |
| Blood Pressure Units        | mmHg                      | mmHg                      | mmHg                      |
| Serum Cholesterol Units     | mg/dL                     | mg/dL                     | mmol/L                    |
| Fasting Glucose Units       | mg/dL                     | mg/dL                     | mmol/L                    |
| Currency                    | USD ($)                   | INR (₹)                   | GBP (£)                   |
| Privacy & Data Framework    | HIPAA / HITECH            | DPDPA 2023 / DISHA        | UK-GDPR / Data Protection |
| Physician Verification Body | National Provider Id (NPI)| National Med Comm (NMC)   | General Medical Council   |
| Healthcare System Context   | Private / Medicare / ACA  | Private / Ayushman Bharat | National Health Service   |
+---------------------------------------------------------------------------------------------------------+
```

---

## 4. Biomarker Normalization & Unit Conversion Engine

Machine learning inference requires standardized input features regardless of the user's local measurement conventions. HeartXAI implements a deterministic, bidirectional unit conversion layer:

### 4.1 Serum Cholesterol Conversion
The Cleveland ML model expects total cholesterol in milligrams per deciliter ($\text{mg/dL}$):

$$\text{Cholesterol}_{\text{mg/dL}} = \text{Cholesterol}_{\text{mmol/L}} \times 38.67$$

$$\text{Cholesterol}_{\text{mmol/L}} = \frac{\text{Cholesterol}_{\text{mg/dL}}}{38.67}$$

### 4.2 Fasting Blood Sugar Conversion
The model evaluates fasting glucose against the clinical threshold of $>120\text{ mg/dL}$ ($>6.66\text{ mmol/L}$):

$$\text{Glucose}_{\text{mg/dL}} = \text{Glucose}_{\text{mmol/L}} \times 18.0182$$

$$\text{Glucose}_{\text{mmol/L}} = \frac{\text{Glucose}_{\text{mg/dL}}}{18.0182}$$

**Implementation Invariant:** The database persists biomarker inputs in both the user's native entered units (for auditability and UI display) and the standardized normalized units (for ML inference).

---

## 5. Data Residency & Privacy Governance

| Country | Regulation | Data Residency Mandate | HeartXAI 2.0 Architectural Compliance Posture |
| :---: | :--- | :---: | :--- |
| **US** | HIPAA / HITECH | Not geographically restricted within US; BAA required. | Production deployment in AWS `us-east-1` or compliant US VPS. AES-256-GCM data encryption at rest and in transit. |
| **GB / EU** | UK-GDPR / EU-GDPR | Restricts transfers outside UK/EEA without Adequacy Decision. | For UK users, database shards or replicas deploy to AWS `eu-west-2` (London) when multi-region tier is activated. Article 22 Automated Decision Making opt-out supported. |
| **IN** | DPDPA 2023 | Cross-border transfer permitted to non-blacklisted nations. | India-localized privacy notices, explicit bilingual consent capture, and support for future AWS `ap-south-1` (Mumbai) hosting. |

---

## 6. Pre-Conditions for Enabling a New Jurisdiction

To prevent unauthorized, unvalidated, or non-compliant geographic rollout, activating a new country code requires completing the following six-step readiness gate:

1. **Clinical Guideline Harmonization:** Review local cardiology guidelines (e.g., ESC for Europe, CSANZ for Australia) to verify compatibility with risk tier thresholds.
2. **Measurement Unit Validation:** Confirm standard clinical units for lab values and verify automated conversion test cases.
3. **Legal & Regulatory Clearance:** Complete statutory data privacy review, update terms of service, and verify medical disclaimer compliance in local languages.
4. **Emergency Directory Seeding:** Populate validated emergency telephone numbers, poison control contacts, and regional cardiac emergency services.
5. **Physician Registry Integration:** Establish credential verification procedures for local healthcare providers (e.g., AHPRA in Australia, CPSO in Canada).
6. **Localization Quality Assurance:** Perform automated and native-speaker UI review of translated strings, date formats, and numerical separators.
