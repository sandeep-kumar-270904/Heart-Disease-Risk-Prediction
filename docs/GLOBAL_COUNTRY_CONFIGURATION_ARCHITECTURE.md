# HeartXAI 2.0 — Global Country Configuration & Localization Architecture

| Document Attribute | Details |
| :--- | :--- |
| **Document ID** | `HXAI-ARCH-GEO-001` |
| **Version** | `1.0.0-PROD` |
| **System State** | Approved Core Architectural Specification |
| **Approved Direction** | **GLOBAL — CONFIGURABLE BY COUNTRY** |
| **Traceability** | `ARCHITECTURE_DECISION_RECORDS.md` (ADR-011), `SYSTEM_ARCHITECTURE_DOCUMENT.md`, `INTEGRATION_ARCHITECTURE.md`, `FUNCTIONAL_REQUIREMENTS.md` |
| **Author** | Principal Software Architect, Healthcare Systems Analyst, Global Security Reviewer |

---

## 1. Executive Summary & Approved Architectural Direction

Per official product governance approval, **HeartXAI 2.0 is architected as a Global, Country-Configurable Healthcare Platform**.

### 1.1 Non-Negotiable Architectural Principles
1. **Zero Hardcoded National Assumptions:** The core application must not hardcode the United States, India, or any other jurisdiction as the exclusive or default operational market.
2. **Strategy / Adapter Pattern:** All regional variations—including directories, credential verification, insurance guidance, clinical guidelines, regulatory compliance, localization, and biomarker units—are encapsulated behind clean, pluggable adapter interfaces.
3. **Verified External Data Sources Only:** No external data source may be incorporated without documented coverage, availability, licensing, authentication requirements, and failure boundaries.
4. **No Fabricated Global Databases:** The platform explicitly avoids claiming worldwide operational coverage. The initial launch countries represent a separate business decision; the system is architected for incremental expansion.
5. **Universal Clinical Core:** Core risk classification (calibrated XGBoost CAD presence model), TreeSHAP feature attributions, and counterfactual mathematical solvers remain universal and invariant across countries. The regional adapters govern contextual input normalization, localization, directory discovery, and legal governance.

```
+---------------------------------------------------------------------------------------------------+
|                                  HEARTXAI 2.0 CORE APPLICATION BOUNDARY                           |
|                                                                                                   |
|  +---------------------------------------------------------------------------------------------+  |
|  |                             COUNTRY PROFILE REGISTRY (Runtime Engine)                       |  |
|  |  - Active Country Context: ISO 3166-1 alpha-2 (e.g., 'IN', 'US', 'GB', 'DE', 'DEFAULT')       |  |
|  |  - Detected via: User Profile Preference -> Request Header ('X-HeartXAI-Country') -> Default|  |
|  +---------------------------------------------------------------------------------------------+  |
|                                                |                                                  |
|             +----------------------------------+----------------------------------+               |
|             |                                                                     |               |
|             v                                                                     v               |
|  +-------------------------------------+             +-------------------------------------+      |
|  |       LOCALIZATION & UNITS ENGINE   |             |       REGIONAL ADAPTER SPI          |      |
|  |  - Unit Conversion (mg/dL <-> mmol/L|             |  1. Physician Directory Adapter     |      |
|  |  - Height/Weight (cm/kg <-> in/lbs) |             |  2. Hospital Facility Adapter       |      |
|  |  - Currency & Date Formatters       |             |  3. Physician Verification Adapter  |      |
|  |  - Multi-Language i18n Strings      |             |  4. Health Insurance Guide Adapter  |      |
|  +-------------------------------------+             |  5. Clinical Guidelines Adapter     |      |
|                                                      |  6. Privacy & Regulatory Engine     |      |
|                                                      +-------------------------------------+      |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. The Eight Country-Configurable Modules

HeartXAI 2.0 decomposes regional healthcare variability into **eight (8) discrete country-configurable modules**:

```
+---------------------------------------------------------------------------------------------------+
|                                 8 COUNTRY-CONFIGURABLE MODULES                                    |
+----+--------------------------------+-------------------------------------------------------------+
| No.| Module Dimension               | Architectural Responsibility & Regional Adaptations         |
+----+--------------------------------+-------------------------------------------------------------+
| 1  | Doctor & Physician Directories | Postal code formats, national specialty taxonomies, search  |
| 2  | Hospital & Facility Directory  | Spatial boundaries, emergency tags, trauma/cath lab levels  |
| 3  | Physician Verification         | Medical council numbers, government registries, doc review  |
| 4  | Health Insurance Information   | Public/private insurance schemes, billing, reimbursement    |
| 5  | Healthcare Information Sources | National clinical guidelines (CSI, ICMR, ACC/AHA, ESC, WHO) |
| 6  | Privacy & Regulatory Compliance| National data protection laws (DPDP Act, HIPAA, GDPR, etc.) |
| 7  | Languages, Dates & Currencies  | i18n translation keys, ISO 4217 currencies, IANA timezones  |
| 8  | Measurement Units & Biomarkers | Lipid & glucose units (mg/dL vs mmol/L), height/weight units|
+----+--------------------------------+-------------------------------------------------------------+
```

---

### Module 1: Doctor & Physician Directories (`IDoctorDirectoryAdapter`)

#### Architectural Contract
```python
from abc import ABC, abstractmethod
from pydantic import BaseModel

class DoctorSearchResult(BaseModel):
    doctor_id: str
    full_name: str
    medical_specialty: str
    licensing_body: str
    clinic_or_hospital: str
    city: str
    postal_code: str
    country_code: str
    is_telehealth_available: bool

class IDoctorDirectoryAdapter(ABC):
    @abstractmethod
    async def search_doctors(self, postal_code: str, specialty: str | None = None, radius_km: float = 25.0) -> list[DoctorSearchResult]:
        """Search registered and verified cardiologists in target country."""
        pass
```

#### Country Implementations & Verified Sources
1. **India (`IN`):**
   - *Postal Code Format:* 6-digit numeric Postal Index Number (PIN) (Regex: `^[1-9][0-9]{5}$`).
   - *Data Sources:* Pre-seeded directory of verified cardiologists registered on HeartXAI + OpenStreetMap India nodes (`healthcare=doctor` AND `healthcare:speciality=cardiology`).
   - *Specialty Taxonomy:* MCI/NMC recognized qualifications: DM (Cardiology), MCh (CTVS), DNB (Cardiology), MD (General Medicine).
2. **United States (`US`):**
   - *Postal Code Format:* 5-digit numeric ZIP Code (Regex: `^\d{5}(-\d{4})?$`).
   - *Data Sources:* Pre-seeded verified clinicians + CMS NPPES registry cardiology taxonomy (`207RC0000X`).
3. **Generic / Global Default (`DEFAULT`):**
   - *Postal Code Format:* Flexible alphanumeric postal code (Regex: `^[A-Za-z0-9\s\-]{3,10}$`).
   - *Data Sources:* Internal HeartXAI verified clinician roster.

---

### Module 2: Hospital & Healthcare Facility Directory (`IHospitalDirectoryAdapter`)

#### Architectural Contract
```python
class HospitalFacilityResult(BaseModel):
    facility_id: str
    name: str
    facility_type: str  # "TERTIARY_HOSPITAL", "CARDIAC_CENTER", "CLINIC"
    has_emergency_services: bool
    has_cardiac_cath_lab: bool
    latitude: float
    longitude: float
    city: str
    postal_code: str
    country_code: str
    phone_number: str | None

class IHospitalDirectoryAdapter(ABC):
    @abstractmethod
    async def search_nearby_facilities(self, postal_code: str, radius_km: float = 25.0) -> list[HospitalFacilityResult]:
        """Discover nearest emergency cardiac facilities within the country."""
        pass
```

#### Country Implementations & Verified Sources
1. **India (`IN`):**
   - *Verified Source 1:* **PMJAY National Health Authority Hospital Dataset**.
     - *Coverage:* All 28 States and 8 Union Territories across India.
     - *Availability & Licensing:* Published by Government of India / NHA on `data.gov.in` and `pmjay.gov.in` under Government Open Data License (GODL-India).
     - *Auth & Limits:* Offline downloadable CSV dataset; zero API rate limit when hosted in local PostGIS/SQLite.
   - *Verified Source 2:* **OpenStreetMap (OSM) India via Overpass API**.
     - *Query:* `node["amenity"="hospital"]["healthcare"="cardiology"](area.India);`.
     - *Licensing:* Open Database License (ODbL) with mandatory attribution. Fair-use limit: max 1 request/sec.
2. **United States (`US`):**
   - *Verified Source:* **CMS Hospital General Information Dataset**.
     - *Coverage:* ~5,000 Medicare-certified hospitals across 50 US States and territories.
     - *Availability & Licensing:* Public domain (data.cms.gov). No authentication required.
3. **Generic / Global Default (`DEFAULT`):**
   - *Verified Source:* OpenStreetMap Overpass API bounded by client coordinate centroid.

---

### Module 3: Physician Identity & Credential Verification (`IPhysicianVerificationAdapter`)

#### Scientific & Legal Reality Check: Why No Global API Exists
The external architecture review established that **there is no single global medical license verification API**. Every sovereign jurisdiction manages its own licensing authority with distinct legal barriers:
- In the US, CMS publishes the open NPPES NPI database via REST API.
- In India, the National Medical Commission (NMC) maintains the National Medical Register (NMR) via a web portal (`nmc.org.in`), but **provides NO open public unauthenticated REST API**. Integration requires either administrative review or ABDM institutional accreditation.
- In the UK, the General Medical Council (GMC) provides an LRMP (List of Registered Medical Practitioners) API requiring official GMC developer registration.
- In Australia, AHPRA provides a downloadable register without a public drop-in REST API.

#### Architectural Contract & Strategy Pattern
```python
class PhysicianVerificationRequest(BaseModel):
    full_name: str
    registration_identifier: str  # NPI in US, Council Reg No in India, GMC No in UK
    licensing_authority: str      # State Council in India, State Board in US, GMC in UK
    country_code: str
    supporting_document_bytes: bytes | None = None
    document_mime_type: str | None = None

class VerificationStatus(BaseModel):
    is_verified: bool
    status: str  # "VERIFIED", "PENDING_ADMIN_REVIEW", "REJECTED"
    verified_authority: str
    audit_notes: str

class IPhysicianVerificationAdapter(ABC):
    @abstractmethod
    async def verify_physician(self, request: PhysicianVerificationRequest) -> VerificationStatus:
        """Execute country-appropriate verification workflow."""
        pass
```

#### Country Implementations
1. **India (`IN`): `IndiaPhysicianVerificationAdapter`**
   - *Workflow:* Applicant provides State Medical Council Name (e.g., Andhra Pradesh Medical Council, Karnataka Medical Council), Council Registration Number, and uploads their official Registration Certificate (PDF/JPEG).
   - *State Transition:* Account is created in `PENDING_ADMIN_REVIEW` state. Administrator inspects certificate against the official NMC public portal and verifies via the Admin Dashboard (`FR-20`).
   - *Future Extension:* ABDM Healthcare Professionals Registry (HPR) API integration once institutional accreditation is completed.
2. **United States (`US`): `USPhysicianVerificationAdapter`**
   - *Workflow:* Programmatic real-time lookup against CMS NPPES NPI Registry API (`https://npiregistry.cms.hhs.gov/api/`).
   - *Fallback:* If CMS API times out, falls back to `PENDING_ADMIN_REVIEW`.
3. **Generic / Global Default (`DEFAULT`): `DocumentUploadVerificationAdapter`**
   - *Workflow:* Standardized document upload queue requiring government-issued medical license verification by a platform administrator.

---

### Module 4: Health Insurance Information & Guidance (`IInsuranceGuideAdapter`)

#### Architectural Contract
```python
class InsurancePolicyGuide(BaseModel):
    country_code: str
    system_type: str  # "UNIVERSAL_PUBLIC", "HYBRID_PUBLIC_PRIVATE", "PRIVATE_DOMINATED"
    preventative_mandates: list[str]
    screening_coverage_summary: str
    reimbursement_checklist: list[str]
    disclaimer: str

class IInsuranceGuideAdapter(ABC):
    @abstractmethod
    def get_insurance_guide(self) -> InsurancePolicyGuide:
        """Return country-specific cardiovascular coverage and insurance navigation guidance."""
        pass
```

#### Country Implementations
1. **India (`IN`):**
   - *System Type:* Hybrid Public-Private.
   - *Public Scheme Information:* Ayushman Bharat — Pradhan Mantri Jan Arogya Yojana (PMJAY) providing ₹5 lakh/family/year coverage for secondary and tertiary hospitalization, including cardiac stenting and bypass surgeries (CABG).
   - *Private Insurance Guidance:* Insurance Regulatory and Development Authority of India (IRDAI) regulations governing pre-existing disease (PED) waiting periods, cashless network hospital protocols, and Third Party Administrator (TPA) pre-authorization.
2. **United States (`US`):**
   - *System Type:* Private-Dominated with Medicare/Medicaid.
   - *Preventative Mandates:* Affordable Care Act (ACA) Section 2713 requiring non-grandfathered commercial plans to cover USPSTF Grade A/B cardiovascular preventatives (hypertension screening, lipid disorder screening, statin preventative therapy) with **$0 patient cost-sharing**.
   - *Medicare Guidance:* Part B cardiovascular disease screening blood tests once every 5 years; intensive cardiac rehabilitation coverage under Part B.
3. **Generic / Global Default (`DEFAULT`):**
   - Universal guidance on obtaining pre-authorization, documenting medical necessity for diagnostic angiograms or stress tests, and retaining clinical consultation notes for claim reimbursement.

---

### Module 5: Healthcare Information Sources & Clinical Guidelines (`IClinicalGuidelineAdapter`)

#### Architectural Contract
```python
class ClinicalGuidelineReference(BaseModel):
    country_code: str
    issuing_body: str
    guideline_name: str
    hypertension_thresholds: dict[str, str]
    dyslipidemia_guidance: str
    risk_assessment_formula: str
    citation_url: str

class IClinicalGuidelineAdapter(ABC):
    @abstractmethod
    def get_guidelines(self) -> ClinicalGuidelineReference:
        """Return authoritative national cardiovascular guidelines."""
        pass
```

#### Country Implementations
1. **India (`IN`):**
   - *Issuing Bodies:* **Cardiological Society of India (CSI)** & **Indian Council of Medical Research (ICMR)**.
   - *Guideline Documents:* 
     - *CSI Consensus Statement on Dyslipidemia in Indians* (recognizing high prevalence of atherogenic dyslipidemia: elevated triglycerides, low HDL, elevated lipoprotein(a), and premature CAD occurring a decade earlier than Western cohorts).
     - *ICMR National Guidelines on Hypertension* (BP target $< 140/90\text{ mmHg}$ for general population; $< 130/80\text{ mmHg}$ for diabetic patients).
   - *Risk Chart:* **WHO/ISH Cardiovascular Risk Prediction Charts for South Asia (SEAR D)**.
2. **United States (`US`):**
   - *Issuing Bodies:* **American College of Cardiology (ACC)** & **American Heart Association (AHA)**.
   - *Guideline Documents:* 
     - *2018 AHA/ACC/AACVPR Guideline on the Management of Blood Cholesterol*.
     - *2017 ACC/AHA Guideline for the Prevention, Detection, Evaluation, and Management of High Blood Pressure in Adults*.
   - *Risk Formula:* **2013 ACC/AHA Pooled Cohort Equations (PCE)** for 10-year ASCVD risk.
3. **European Union / Global (`EU` / `GLOBAL`):**
   - *Issuing Body:* **European Society of Cardiology (ESC)**.
   - *Guideline Document:* *2021 ESC Guidelines on Cardiovascular Disease Prevention in Clinical Practice*.
   - *Risk Formula:* **SCORE2** (Systematic Coronary Risk Evaluation 2) calibrated for European risk regions.

---

### Module 6: Applicable Privacy & Regulatory Compliance (`IRegulatoryComplianceEngine`)

#### Architectural Contract
```python
class RegulatoryFrameworkProfile(BaseModel):
    country_code: str
    primary_legislation: str
    consent_model: str  # "EXPLICIT_OPT_IN", "PURPOSE_SPECIFIC_CONSENT"
    data_residency_requirement: bool
    right_to_erasure_supported: bool
    right_to_data_portability_supported: bool
    mandatory_breach_notification_hours: int
    regulatory_supervisory_authority: str
```

#### Country Implementations
1. **India (`IN`): Digital Personal Data Protection Act, 2023 (DPDP Act 2023)**
   - *Consent Standard:* Notice must be accessible in English or any of the **22 languages specified in the Eighth Schedule to the Constitution of India**.
   - *Purpose Limitation:* Data processed strictly for declared healthcare awareness purposes; zero commercial secondary usage.
   - *Supervisory Body:* Data Protection Board of India.
   - *Minor Data Protection:* Explicit parental consent mechanism for users under 18 years of age.
2. **United States (`US`): HIPAA (45 CFR Parts 160 & 164) & HITECH Act**
   - *Consent Standard:* HIPAA § 164.508 explicit authorization for sharing PHI with healthcare professionals.
   - *Business Associate Agreement (BAA):* Mandatory on all cloud infrastructure sub-processors.
   - *Breach Notification:* HHS OCR notification within 60 days of discovering a breach affecting $\ge 500$ individuals.
3. **European Union / United Kingdom (`EU` / `GB`): GDPR & UK Data Protection Act 2018**
   - *Health Data Classification:* Article 9 Special Category Data requiring explicit consent (Article 9(2)(a)).
   - *Data Subject Rights:* Full automated execution of Article 15 (Access), Article 17 (Erasure / Right to be Forgotten), and Article 20 (Portability).
   - *Automated Decision-Making Safeguards:* Article 22 compliance—HeartXAI's non-diagnostic educational framing guarantees that AI outputs do not produce legally binding autonomous healthcare decisions.
   - *Breach Notification:* Supervisory authority (e.g. DPC, CNIL, ICO) notified within **72 hours**.

---

### Module 7: Languages, Currencies, Dates & Timezones (`ILocalizationEngine`)

#### Architectural Contract
```python
class CountryLocalizationProfile(BaseModel):
    country_code: str
    default_language: str
    supported_languages: list[str]
    currency_code: str    # ISO 4217
    currency_symbol: str
    date_format_pattern: str  # e.g., "DD/MM/YYYY" vs "MM/DD/YYYY"
    primary_timezones: list[str]  # IANA timezone strings
```

#### Multi-Country Configuration Matrix

| Country Code | Primary Language(s) | ISO 4217 Currency | Date Display Format | Primary IANA Timezone(s) |
| :---: | :--- | :---: | :---: | :--- |
| **`IN` (India)** | `en-IN`, `hi-IN`, `te-IN`, `ta-IN` | `INR` (`₹`) | `DD/MM/YYYY` | `Asia/Kolkata` (UTC+05:30) |
| **`US` (United States)** | `en-US`, `es-US` | `USD` (`$`) | `MM/DD/YYYY` | `America/New_York`, `America/Chicago`, `America/Los_Angeles` |
| **`GB` (United Kingdom)**| `en-GB` | `GBP` (`£`) | `DD/MM/YYYY` | `Europe/London` (UTC+00:00 / BST) |
| **`DE` (Germany / EU)** | `de-DE`, `en-US` | `EUR` (`€`) | `DD.MM.YYYY` | `Europe/Berlin` (UTC+01:00 / CEST) |
| **`DEFAULT` (Global)** | `en` | `USD` (`$`) | `YYYY-MM-DD` (ISO) | `UTC` |

#### Architectural Implementation Rules
1. **Database UTC Invariance:** All timestamps in PostgreSQL are stored exclusively in UTC (`TIMESTAMPTZ`). No local timezone timestamps are ever persisted.
2. **Frontend Locale Formatting:** Formatting is handled client-side using native browser APIs (`Intl.DateTimeFormat`, `Intl.NumberFormat`), preventing server-side timezone rendering bugs.
3. **i18n Translation Key Architecture:** Frontend uses hierarchical translation keys (e.g. `assessment.wizard.blood_pressure.label`) managed via `react-i18next`. Adding a new language requires only providing a new translation JSON file without altering application code.

---

### Module 8: Measurement Units & Biomarker Localization (`IBiomarkerUnitConverter`)

#### Clinical Biomarker Measurement Unit Systems
Cardiovascular biomarkers are reported in different measurement units worldwide:
- **Cholesterol (Total, HDL, LDL):**
  - Conventional Units (US, India, Japan): $\text{mg/dL}$ (milligrams per deciliter).
  - SI / Molar Units (UK, Canada, Australia, Europe): $\text{mmol/L}$ (millimoles per liter).
  - *Conversion Constant:* $1\text{ mmol/L} \approx 38.67\text{ mg/dL}$ (Molecular weight of cholesterol $\approx 386.65\text{ g/mol}$).
- **Fasting Blood Sugar / Glucose:**
  - Conventional Units (US, India): $\text{mg/dL}$.
  - SI / Molar Units (UK, Europe, Canada): $\text{mmol/L}$.
  - *Conversion Constant:* $1\text{ mmol/L} \approx 18.018\text{ mg/dL}$ (Molecular weight of glucose $\approx 180.16\text{ g/mol}$).
- **Blood Pressure:** Universally standardized across all international guidelines (AHA, ESC, CSI, WHO) as $\text{mm Hg}$ (millimetres of mercury).
- **Heart Rate:** Universally standardized as $\text{bpm}$ (beats per minute).
- **Physical Anthropometry:**
  - Height: Metric ($\text{cm}$) vs Imperial ($\text{ft} + \text{in}$).
  - Weight: Metric ($\text{kg}$) vs Imperial ($\text{lbs}$).

#### Deterministic Conversion Engine Specification
```python
class BiomarkerUnitConverter:
    CHOLESTEROL_CONVERSION_FACTOR = 0.02586  # mg/dL -> mmol/L
    GLUCOSE_CONVERSION_FACTOR = 0.0555       # mg/dL -> mmol/L

    @classmethod
    def cholesterol_to_standard_mg_dl(cls, value: float, from_unit: str) -> float:
        """Standardize cholesterol to model-native mg/dL."""
        if from_unit.lower() == "mmol/l":
            return round(value / cls.CHOLESTEROL_CONVERSION_FACTOR, 1)
        return value

    @classmethod
    def cholesterol_to_display(cls, value_mg_dl: float, target_unit: str) -> float:
        """Convert internal mg/dL value to patient preferred display unit."""
        if target_unit.lower() == "mmol/l":
            return round(value_mg_dl * cls.CHOLESTEROL_CONVERSION_FACTOR, 2)
        return round(value_mg_dl, 1)

    @classmethod
    def glucose_to_standard_mg_dl(cls, value: float, from_unit: str) -> float:
        """Standardize fasting blood sugar to model-native mg/dL."""
        if from_unit.lower() == "mmol/l":
            return round(value / cls.GLUCOSE_CONVERSION_FACTOR, 1)
        return value
```

#### Model Normalization Invariance Rule
> [!IMPORTANT]
> **Internal ML Normalization Invariance:** The trained machine learning model pipeline (`StandardScaler` + `XGBoost`) was calibrated on dataset features expressed in conventional units ($\text{mg/dL}$, $\text{mm Hg}$, $\text{years}$). 
> The backend intake validation service (`ValidationService`) **always converts incoming biomarker values to model-native standard units** prior to inference. 
> The client UI displays values in the patient's selected preference, dynamically rendering the active unit badge ($\text{mg/dL}$ vs $\text{mmol/L}$).

---

## 3. Country Profile Registry Architecture

HeartXAI implements a centralized, strongly typed **Country Profile Registry** (`app/core/country_profile.py`):

```python
from typing import Literal
from pydantic import BaseModel

class CountryProfile(BaseModel):
    country_code: str             # ISO 3166-1 alpha-2
    country_name: str
    default_currency: str         # ISO 4217
    default_date_format: str
    default_cholesterol_unit: Literal["mg/dL", "mmol/L"]
    default_glucose_unit: Literal["mg/dL", "mmol/L"]
    default_body_units: Literal["metric", "imperial"]
    postal_code_regex: str
    postal_code_label: str        # e.g., "PIN Code", "ZIP Code", "Postal Code"
    regulatory_framework: str
    doctor_directory_adapter: str
    hospital_directory_adapter: str
    physician_verification_adapter: str
    insurance_guide_adapter: str
    clinical_guideline_adapter: str

COUNTRY_REGISTRY: dict[str, CountryProfile] = {
    "IN": CountryProfile(
        country_code="IN",
        country_name="India",
        default_currency="INR",
        default_date_format="DD/MM/YYYY",
        default_cholesterol_unit="mg/dL",
        default_glucose_unit="mg/dL",
        default_body_units="metric",
        postal_code_regex=r"^[1-9][0-9]{5}$",
        postal_code_label="PIN Code",
        regulatory_framework="DPDP_ACT_2023",
        doctor_directory_adapter="IndiaDoctorDirectoryAdapter",
        hospital_directory_adapter="IndiaHospitalDirectoryAdapter",
        physician_verification_adapter="IndiaManualVerificationAdapter",
        insurance_guide_adapter="IndiaInsuranceGuideAdapter",
        clinical_guideline_adapter="IndiaClinicalGuidelineAdapter",
    ),
    "US": CountryProfile(
        country_code="US",
        country_name="United States",
        default_currency="USD",
        default_date_format="MM/DD/YYYY",
        default_cholesterol_unit="mg/dL",
        default_glucose_unit="mg/dL",
        default_body_units="imperial",
        postal_code_regex=r"^\d{5}(-\d{4})?$",
        postal_code_label="ZIP Code",
        regulatory_framework="HIPAA",
        doctor_directory_adapter="USDoctorDirectoryAdapter",
        hospital_directory_adapter="USCMSHospitalDirectoryAdapter",
        physician_verification_adapter="USCMSVerificationAdapter",
        insurance_guide_adapter="USInsuranceGuideAdapter",
        clinical_guideline_adapter="USClinicalGuidelineAdapter",
    ),
    "GB": CountryProfile(
        country_code="GB",
        country_name="United Kingdom",
        default_currency="GBP",
        default_date_format="DD/MM/YYYY",
        default_cholesterol_unit="mmol/L",
        default_glucose_unit="mmol/L",
        default_body_units="metric",
        postal_code_regex=r"^[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}$",
        postal_code_label="Postcode",
        regulatory_framework="UK_GDPR",
        doctor_directory_adapter="DefaultDoctorDirectoryAdapter",
        hospital_directory_adapter="OSMHospitalDirectoryAdapter",
        physician_verification_adapter="DocumentUploadVerificationAdapter",
        insurance_guide_adapter="NHSInsuranceGuideAdapter",
        clinical_guideline_adapter="NICEClinicalGuidelineAdapter",
    ),
    "DEFAULT": CountryProfile(
        country_code="DEFAULT",
        country_name="Global Default",
        default_currency="USD",
        default_date_format="YYYY-MM-DD",
        default_cholesterol_unit="mg/dL",
        default_glucose_unit="mg/dL",
        default_body_units="metric",
        postal_code_regex=r"^[A-Za-z0-9\s\-]{3,10}$",
        postal_code_label="Postal Code",
        regulatory_framework="BASELINE_ZERO_TRUST",
        doctor_directory_adapter="DefaultDoctorDirectoryAdapter",
        hospital_directory_adapter="OSMHospitalDirectoryAdapter",
        physician_verification_adapter="DocumentUploadVerificationAdapter",
        insurance_guide_adapter="DefaultInsuranceGuideAdapter",
        clinical_guideline_adapter="WHOClinicalGuidelineAdapter",
    ),
}
```

---

## 4. Expansion Runbook: Adding a New Country Profile

To add operational support for a new country (e.g., Australia `AU` or Germany `DE`), developers follow this deterministic 5-step expansion protocol without altering core business or ML inference logic:

```
Step 1: Register ISO 3166-1 alpha-2 code in CountryProfile registry (`app/core/country_profile.py`).
Step 2: Implement or reuse `IDirectoryProviderAdapter` for the country's hospital and doctor data.
Step 3: Define regulatory compliance rules (`IRegulatoryComplianceEngine`) and consent terms.
Step 4: Configure national clinical guideline references and insurance guides.
Step 5: Add locale translation strings in frontend (`frontend/src/locales/{code}.json`).
```

---

## 5. Traceability Matrix

| Requirement | Global Module | Architectural Mechanism | Verification Criteria |
| :--- | :--- | :--- | :--- |
| **FR-11** | Doctor Directory | `IDoctorDirectoryAdapter` + Country PIN/ZIP regex | Country-specific postal validation |
| **FR-12** | Hospital Directory | `IHospitalDirectoryAdapter` (PMJAY / CMS / OSM) | Spatial query bounded by country border |
| **FR-11** | Physician Verification | `IPhysicianVerificationAdapter` (Queue vs API) | Verification matching national licensing |
| **FR-06** | Measurement Units | `BiomarkerUnitConverter` ($\text{mg/dL} \leftrightarrow \text{mmol/L}$) | Bidirectional conversion accuracy |
| **FR-29** | Localization | `CountryLocalizationProfile` + i18next + `Intl` | Multi-currency, locale dates, UTF-8 strings |
| **NFR-08** | Regulatory Governance | `IRegulatoryComplianceEngine` (DPDP, HIPAA, GDPR) | Jurisdictional consent & retention rules |

---

*Approved and ratified by Principal Software Architect, Healthcare Systems Analyst & Global Security Reviewer.*
