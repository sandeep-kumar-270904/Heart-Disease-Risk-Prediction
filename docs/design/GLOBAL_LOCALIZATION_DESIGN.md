# HeartXAI 2.0 — Global Localization Design Specification

**Document ID:** `HX2-DES-011`  
**Version:** `2.0.0`  
**Status:** `Approved Specification`  
**Author:** Principal Frontend Experience Architect & Internationalization Specialist  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011  

---

## 1. Global Architectural Mandate

In accordance with approved product requirement **ADR-011: Global Geographic Architecture — Configurable by Country via Adapter Pattern**, HeartXAI 2.0 **must not hard-code any single country** (e.g., neither the United States nor India) as the sole supported market.

The frontend design system and user interface are engineered from the foundation to be **country-configurable across 8 critical dimensions**:

```
┌────────────────────────────────────────────────────────────────────────┐
│               THE 8 DIMENSIONS OF GLOBAL LOCALIZATION                  │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Doctor & Physician Directories       │ 5. Healthcare Info & Notices │
│ 2. Hospital & Care Facility Directories │ 6. Privacy & Legal Compliance│
│ 3. Physician Credential Verification    │ 7. Languages, Dates, Money   │
│ 4. Health Insurance Guidance & Claims   │ 8. Measurement Units (Biomk) │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Measurement Unit Localization & Live Conversions

Cardiovascular medicine relies on regional measurement conventions that differ significantly across jurisdictions. HeartXAI 2.0 provides seamless bidirectional conversion without loss of clinical precision.

### 2.1 Supported Unit Dimensions & Standards

| Parameter | Metric / Global Standard | US / Regional Standard | Mathematical Conversion Factor |
| :--- | :--- | :--- | :--- |
| **Serum Cholesterol** | `mmol/L` (UK, EU, Australia) | `mg/dL` (India, USA, Japan) | $1\text{ mmol/L} = 38.67\text{ mg/dL}$ |
| **Fasting Blood Sugar** | `mmol/L` (UK, EU, Canada) | `mg/dL` (India, USA) | $1\text{ mmol/L} = 18.016\text{ mg/dL}$ |
| **Blood Pressure** | `mmHg` (Universal Global) | `mmHg` (Universal Global) | $1:1$ (Universal standard) |
| **Body Weight** | `kg` (India, EU, Global) | `lbs` (USA) | $1\text{ kg} = 2.20462\text{ lbs}$ |
| **Body Height** | `cm` (India, EU, Global) | `ft / in` (USA, UK) | $1\text{ in} = 2.54\text{ cm}$ |

### 2.2 Input Field Behavior & Live Conversion
- **User Preference Memory:** Unit preferences are stored in the user profile and synchronized across all devices (`localStorage` + backend user settings).
- **In-Form Unit Switcher:**
  ```
  ┌────────────────────────────────────────────────────────┐
  │ Serum Cholesterol: [ 210 ]  [● mg/dL  |  ○ mmol/L]   │
  └────────────────────────────────────────────────────────┘
         │ User clicks "mmol/L"
         ▼
  ┌────────────────────────────────────────────────────────┐
  │ Serum Cholesterol: [ 5.43 ] [○ mg/dL  |  ● mmol/L]   │
  └────────────────────────────────────────────────────────┘
  ```
- **Validation Bound Synchronization:**
  - `mg/dL` input bounds: `[100, 600]`, step `1.0`.
  - `mmol/L` input bounds: `[2.59, 15.52]`, step `0.01`.
- **Backend Storage Parity:** The backend persistently stores all values in canonical metric units (`mg/dL` and `mmHg`), with the display layer handling formatting dynamically using pure presentation adapters.

---

## 3. Formatting Standards: Dates, Numbers, and Currencies

All localized formatting uses native standard ECMAScript Internationalization APIs (`Intl.DateTimeFormat`, `Intl.NumberFormat`) rather than bloated third-party formatting libraries.

### 3.1 Date and Time Formats by Country Context

| Jurisdiction | Date Format | Time Format | Example Output |
| :--- | :--- | :--- | :--- |
| **India (`en-IN` / `hi-IN`)** | `DD/MM/YYYY` | 12-hour AM/PM | `14/11/2026, 02:30 PM IST` |
| **United States (`en-US`)** | `MM/DD/YYYY` | 12-hour AM/PM | `11/14/2026, 02:30 PM EST` |
| **United Kingdom (`en-GB`)**| `DD/MM/YYYY` | 24-hour | `14/11/2026, 14:30 GMT` |
| **European Union (`de-DE`)**| `DD.MM.YYYY` | 24-hour | `14.11.2026, 14:30 CET` |

### 3.2 Currency & Consultation Fee Displays

```typescript
// Deterministic currency formatter
export const formatCurrency = (amount: number, currencyCode: string, locale: string) => {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currencyCode,
    maximumFractionDigits: 0,
  }).format(amount);
};
```

- **India (`IN`):** `₹ 1,500` (INR)
- **United States (`US`):** `$ 150` (USD)
- **United Kingdom (`GB`):** `£ 120` (GBP)
- **Germany / EU (`DE`):** `140 €` (EUR)

---

## 4. Country Configuration UI & Switcher Modal

### 4.1 Global Country Switcher (Header Pill)
- Positioned in the application header: displays national flag, country name, and active currency (e.g., `🇮🇳 India · INR ₹`).
- Clicking opens the **Country Jurisdiction Modal**:

```
┌────────────────────────────────────────────────────────────────────────┐
│ SELECT YOUR HEALTHCARE JURISDICTION                                   │
├────────────────────────────────────────────────────────────────────────┤
│ Selecting your country configures:                                     │
│ • Local verified doctor and hospital directories                       │
│ • Default measurement units (mg/dL vs mmol/L)                         │
│ • Local emergency hotline numbers (e.g. 112 vs 911)                   │
│ • Relevant health insurance guides and clinical disclaimers            │
│                                                                        │
│ [ Search countries...                                                ] │
│                                                                        │
│ ● 🇮🇳 India (Active)                                                   │
│   Units: mg/dL, mmHg, cm/kg · Emergency: 112 / 102 · Registry: NMC    │
│                                                                        │
│ ○ 🇺🇸 United States                                                    │
│   Units: mg/dL, mmHg, in/lbs · Emergency: 911 · Registry: State Boards│
│                                                                        │
│ ○ 🇬🇧 United Kingdom                                                   │
│   Units: mmol/L, mmHg, cm/kg · Emergency: 999 / 111 · Registry: GMC   │
│                                                                        │
│ [ Apply Jurisdiction Settings ]                 [ Cancel ]             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 5. UI Layout Resilience for Multi-Language Expansion

### 5.1 Text Expansion Factors
When translated from English to other major languages, UI strings expand substantially:
- **German, Dutch, Greek:** $30\%\text{ – }40\%$ longer than English.
- **Hindi, Spanish, French:** $20\%\text{ – }30\%$ longer than English.
- **East Asian (CJK):** More compact horizontally, but require taller line-heights ($1.6\times$ vs $1.5\times$).

### 5.2 Responsive Layout Rules for Translation
- **No Fixed Width Buttons:** Button containers use `min-width` and auto horizontal padding (`px-4`), never hardcoded pixel widths (`w-[120px]`).
- **Flexible Card Headers:** Header rows use `flex-wrap` to prevent text truncation or collision when headings expand.
- **Explicit Truncation Protection:** Critical clinical terms and units **must never be truncated with ellipsis (`text-ellipsis`)**. If space is constrained, text wraps naturally to the next line.

---

## 6. Localized Healthcare Directory & Statutory Disclaimers

Every country adapter provides localized statutory phrasing required by national health authorities:

- **India (`IN`):** Compliant with the *Digital Personal Data Protection Act (DPDPA 2023)* and the *National Medical Commission (NMC) Registered Medical Practitioner Regulations*. Displays emergency ambulance hotline `102` / `108` and national emergency `112`.
- **United States (`US`):** Compliant with *HIPAA Security and Privacy Rules* and *FDA Non-Diagnostic Clinical Decision Support (CDS) Guidance*. Displays emergency services `911`.
- **United Kingdom (`GB`):** Compliant with *UK GDPR* and *Medicines and Healthcare products Regulatory Agency (MHRA)* guidelines. Displays emergency `999` and non-emergency NHS triage `111`.
