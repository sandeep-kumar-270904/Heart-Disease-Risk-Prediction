# COMPATIBILITY AND LOCALIZATION TESTING SPECIFICATION

**Document Reference:** `docs/quality/COMPATIBILITY_AND_LOCALIZATION_TESTING.md`  
**Phase:** 11 — Comprehensive Testing Strategy, Quality Assurance & Validation Framework  
**Status:** Approved Technical Architecture  
**Author:** Internationalization QA Lead & Cross-Platform Test Specialist  
**Traceability:** NFR-LEGAL-01, FR-UI-*, ADR-011  

---

## 1. Executive Summary & Clinical Localization Scope

In healthcare systems, localization is far more critical than simple UI text translation. A localization failure that misinterprets clinical measurement units (e.g. confusing $\text{mg/dL}$ with $\text{mmol/L}$ for serum cholesterol or glucose) alters input values by a factor of nearly $39\times$, converting normal physiological readings into lethal or nonsensical extremes.

HeartXAI 2.0 establishes rigorous automated verification across:
1. **Clinical Measurement Unit Conversion Accuracy** ($\text{mg/dL} \leftrightarrow \text{mmol/L}$).
2. **Cross-Browser & Multi-Device Responsive Compatibility**.
3. **Timezone & Date/Time Representation Integrity**.
4. **Country-Specific Runtime Configuration Injection** ([ADR-011](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/GLOBAL_COUNTRY_CONFIGURATION_ARCHITECTURE.md)).

---

## 2. Clinical Measurement Unit Conversion Verification

Automated unit conversion tests (`backend/tests/unit/test_unit_localization.py`) assert exact mathematical conversions before feature vectors enter the ML pipeline:

| Biomarker | US & Indian Standard Unit | International / EU Standard Unit | Mathematical Conversion Formula | Invariant Assertion |
| :--- | :---: | :---: | :--- | :--- |
| **Total Cholesterol** | $\text{mg/dL}$ | $\text{mmol/L}$ | $\text{chol}_{\text{mg/dL}} = \text{chol}_{\text{mmol/L}} \times 38.67$ | Input of $5.20\text{ mmol/L}$ converts to $201.08\text{ mg/dL}$ ($\pm 0.1$) |
| **Fasting Blood Sugar**| $\text{mg/dL}$ | $\text{mmol/L}$ | $\text{gluc}_{\text{mg/dL}} = \text{gluc}_{\text{mmol/L}} \times 18.0182$| Input of $6.80\text{ mmol/L}$ converts to $122.52\text{ mg/dL}$ ($\pm 0.1$) |
| **Systolic Blood Pressure**| $\text{mmHg}$ | $\text{mmHg}$ / $\text{kPa}$ | Standardized globally in $\text{mmHg}$ | $1.0\text{ kPa} = 7.50062\text{ mmHg}$ (if kPa submitted) |

### 2.1 Critical Unit Safety Assertion:
- If a client submits a cholesterol value of $5.5$ labeled as $\text{mg/dL}$, the backend Pydantic validator rejects it as non-physiological ($5.5\text{ mg/dL}$ is fatal/incompatible with life; physiological minimum is $100\text{ mg/dL}$).
- The system prevents ambiguous unit assumptions: payloads must either declare explicit unit headers (`X-Unit-Cholesterol: mmol/L`) or adhere to the country configuration default.

---

## 3. Cross-Browser and Operating System Compatibility Matrix

Automated Playwright test suites execute across four major browser rendering engines on desktop, tablet, and mobile viewport profiles:

| Browser Engine | Platform Tested | Viewport Dimensions | Target Testing Persona | Acceptance Criteria |
| :--- | :--- | :---: | :--- | :--- |
| **Chromium (Blink)** | Windows 11 / Ubuntu / Android | $1920\times 1080$ (Desktop) | Primary patient & clinician desktop | Zero console errors; perfect CSS grid reflow |
| **Mozilla Firefox (Gecko)**| Windows 11 / macOS / Linux | $1366\times 768$ (Laptop) | Standard desktop web users | SVG charts render with matching dimensions |
| **Apple WebKit** | macOS Sonoma / iOS 17 | $390\times 844$ (Mobile - iPhone 14) | Mobile outpatient users | Touch gestures functional; zero horizontal scroll |
| **Microsoft Edge** | Windows 11 / Windows 10 | $1536\times 864$ (Desktop) | Enterprise clinical hospital workstations | Full feature parity with Chromium |
| **Tablet Emulation** | iPad Air / Android Tablet | $820\times 1180$ (Tablet Portrait) | Clinician bedside review | Responsive navigation transitions to drawer |

---

## 4. Internationalization & Timezone Verification

1. **Universal UTC Storage:** All timestamps in PostgreSQL (`created_at`, `granted_at`, `changed_at`) are stored in Coordinated Universal Time (UTC) with timezone (`TIMESTAMP WITH TIME ZONE`).
2. **Client-Side Localization:** The frontend formats timestamps into the user's localized timezone using standard browser APIs (`Intl.DateTimeFormat`):
   - India: `dd/MM/yyyy, hh:mm a` (`Asia/Kolkata`)
   - United States: `MM/dd/yyyy, hh:mm a` (`America/New_York`)
   - European Union: `dd.MM.yyyy, HH:mm` (`Europe/Berlin`)
3. **Date Discrepancy Assertion (`test_timezone_rendering.py`):**
   - Asserts that an assessment submitted at `23:30 UTC` displays as the correct localized calendar date in IST (`+05:30` next calendar day), preventing clinical record chronological confusion.

---

## 5. Country Configuration Isolation (ADR-011)

Tests assert that altering `HEARTXAI_COUNTRY_CODE` alters localized behavior without requiring code changes:
- `HEARTXAI_COUNTRY_CODE=IN`: Emergency banner displays **112**; currency displays **₹ (INR)**; directory queries India adapter.
- `HEARTXAI_COUNTRY_CODE=US`: Emergency banner displays **911**; currency displays **\$ (USD)**; directory queries US provider registry.
- `HEARTXAI_COUNTRY_CODE=DE`: Emergency banner displays **112**; currency displays **€ (EUR)**; measurement units default to $\text{mmol/L}$.
