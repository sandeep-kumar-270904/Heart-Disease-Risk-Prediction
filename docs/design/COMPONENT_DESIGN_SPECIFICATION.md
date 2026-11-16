# HeartXAI 2.0 — Component Design Specification

**Document ID:** `HX2-DES-005`  
**Version:** `2.0.0`  
**Status:** `Approved Specification`  
**Author:** Principal Product Designer & Design Systems Architect  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011  

---

## 1. Overview & Architectural Principles

The HeartXAI 2.0 component system defines reusable, production-ready interface primitives built upon our design tokens. Every component adheres to:
1. **WCAG 2.2 AA Compliance:** High contrast ratios, explicit keyboard focus rings (`2px` outline with `2px` offset), and full screen-reader semantic trees.
2. **Deterministic State Modeling:** Every component accounts for all interactive states: *Default, Hover, Active, Focus-Visible, Disabled, Loading, Error*.
3. **Medical & Mathematical Integrity:** Inputs explicitly bind physical measurement units; risk displays enforce unambiguous strata; counterfactual sliders visually indicate feasibility boundaries.

---

## 2. Foundation Components

### 2.1 Buttons (`<Button />`)

#### Purpose
Triggers primary and secondary user actions, form submissions, navigation jumps, and modal confirmations.

#### Anatomy
```
┌────────────────────────────────────────────────────────┐
│ [Leading Icon]  Button Label Text  [Trailing Icon]    │
└────────────────────────────────────────────────────────┘
```

#### Variants & Style Definitions
- **`primary`:** Solid `#0284C7` (Sky 600) fill, `#FFFFFF` text. Used for main action per screen (e.g., "Run Risk Assessment", "Save Profile").
- **`secondary`:** Solid `#F1F5F9` (Slate 100) fill, `#0F172A` (Slate 900) text, `#E2E8F0` border. Used for non-primary actions (e.g., "Export PDF", "Cancel").
- **`outline`:** Transparent fill, `1px solid #CBD5E1` border, `#0F172A` text. Used for secondary inline actions (e.g., "View SHAP Table").
- **`ghost`:** Transparent fill, no border, `#475569` text. Hover fills `#F1F5F9`. Used for table row actions, toolbar icons.
- **`danger`:** Solid `#DC2626` (Crimson 600) fill, `#FFFFFF` text. Reserved strictly for destructive operations (e.g., "Delete Assessment Record", "Revoke Access").

#### Interactive States
- **Default:** Crisp text, flat surface, no shadow.
- **Hover:** Darkens fill by 1 shade (e.g., Sky 600 $\rightarrow$ Sky 700); duration `150ms ease-out`.
- **Active:** Scaled down subtly (`scale(0.98)`), shadow-inner.
- **Focus-Visible:** `outline: 2px solid #0284C7; outline-offset: 2px;`.
- **Disabled:** Background `#E2E8F0`, text `#94A3B8`, cursor `not-allowed`, opacity `0.6`, `aria-disabled="true"`.
- **Loading:** Label replaced or paired with `16px` spinning indicator; `aria-busy="true"`.

#### Accessibility Requirements
- Semantic `<button type="...">` element.
- Minimum touch target: `44×44px` on mobile/tablet.
- Text contrast ratio: $\ge 4.5:1$ against background in all states.

---

### 2.2 Badges & Status Pills (`<Badge />`)

#### Purpose
Communicates categorical status, model risk stratum, verification status, and data freshness.

#### Variants
```
  [ Low Risk: < 30% ]          ── Fill: Emerald 50,  Border: Emerald 600, Text: Emerald 700
  [ Moderate Risk: 30-69% ]    ── Fill: Amber 50,    Border: Amber 600,   Text: Amber 700
  [ Elevated Risk: ≥ 70% ]     ── Fill: Crimson 50,  Border: Crimson 600, Text: Crimson 700
  [ Clinician Verified ]       ── Fill: Sky 50,      Border: Sky 600,     Text: Sky 700
  [ Model v2.4.1 (Cleveland) ] ── Fill: Slate 100,   Border: Slate 300,   Text: Slate 700
```

#### Anatomy & Accessibility
- Height: `24px`; internal horizontal padding: `8px`; corner radius: `9999px` (pill).
- Text: `12px` (`0.75rem`), weight `500`.
- Icon: `12×12px` leading symbol (e.g., `ShieldCheck`, `AlertCircle`).
- Every badge includes a machine-readable `aria-label` detailing the full status.

---

## 3. Form Components

### 3.1 Unit-Bound Number Input (`<BiomarkerInput />`)

#### Purpose
Captures clinical quantitative measurements (cholesterol, blood pressure, fasting blood sugar, heart rate) with embedded unit labels and interactive unit-toggle conversions.

#### Anatomy
```
┌────────────────────────────────────────────────────────┐
│ Label: Serum Cholesterol *             [mg/dL | mmol/L]│ <── Dynamic Unit Toggle
├────────────────────────────────────────────────────────┤
│ [ Icon ]  210.00                       | mg/dL         │ <── Embedded Unit Affix
├────────────────────────────────────────────────────────┤
│ Helper: Reference range: 125 – 200 mg/dL               │
└────────────────────────────────────────────────────────┘
```

#### Unit Conversion Behavior
- When the user toggles from `mg/dL` to `mmol/L`:
  - The numeric value in the input field converts mathematically: $\text{Value}_{\text{mmol/L}} = \text{Value}_{\text{mg/dL}} / 38.67$.
  - The conversion is rounded to 2 decimal places.
  - The validation bounds update immediately: $[100, 400]\text{ mg/dL} \rightarrow [2.59, 10.34]\text{ mmol/L}$.
  - The unit affix in the input container updates to `mmol/L`.
  - The backend request payload converts and normalizes values to canonical storage units.

#### States & Validation
- **Default:** Border `#CBD5E1`, background `#FFFFFF`.
- **Focus:** Border `#0284C7`, focus ring `2px` offset.
- **Physiological Warning State:** If value is clinically extreme (e.g., Systolic BP $> 220\text{ mmHg}$), a non-blocking warning card appears below: *"Value is outside typical outpatient limits. Please verify measurement."*
- **Error / Invalid State:** Border `#DC2626`, background `#FEF2F2`. Error message rendered below with `AlertCircle` icon: *"Resting blood pressure must be between 70 and 240 mmHg."*
- **Accessibility:** `aria-invalid="true"`, `aria-describedby="field-error-id"`, `<label for="...">` explicitly bound.

---

### 3.2 Counterfactual Interactive Slider (`<CounterfactualSlider />`)

#### Purpose
Allows patients and clinicians to explore hypothetical "what-if" scenarios by modifying mutable physiological variables (e.g., cholesterol, blood pressure, BMI) and viewing real-time model attribution updates.

#### Anatomy
```
┌────────────────────────────────────────────────────────────────────────┐
│ Variable: Systolic Blood Pressure          Baseline: 154 mmHg          │
├────────────────────────────────────────────────────────────────────────┤
│ 90 mmHg ──────[====●==============]─────────────── 200 mmHg             │
│                    │                                                   │
│             Current: 130 mmHg ( -24 mmHg )                             │
├────────────────────────────────────────────────────────────────────────┤
│ Physiological Bounds: [90 – 200 mmHg]       [Reset to Baseline]        │
└────────────────────────────────────────────────────────────────────────┘
```

#### Behavioral Rules
- **Baseline Pin:** An anchored indicator marks the patient's actual baseline measurement.
- **Delta Indicator:** Dynamically computes and displays the delta: `Current - Baseline` (e.g., `-24 mmHg`).
- **Reset Button:** Instant 1-click restore to baseline value.
- **Physiological Guardrails:** The slider track cannot be dragged outside clinically plausible human ranges.
- **Keyboard Navigation:** Arrow keys adjust value by 1 unit (`step="1"`); `PageUp`/`PageDown` adjust by 5 units.
- **ARIA:** `role="slider"`, `aria-valuemin="90"`, `aria-valuemax="200"`, `aria-valuenow="130"`, `aria-valuetext="130 millimeters of mercury"`.

---

## 4. Navigation Components

### 4.1 Global Application Header (`<AppHeader />`)

#### Purpose
Provides top-level brand identification, primary role context, global country selector, notification access, and user profile management.

#### Anatomy
```
┌────────────────────────────────────────────────────────────────────────┐
│ [HeartXAI Logo]  [Dashboard] [Assessments] [Directories]               │
│                  [Country: IN ₹] [Alerts (2)] [Dr. Sarah Chen ▼]       │
└────────────────────────────────────────────────────────────────────────┘
```

#### Key Capabilities
- **Sticky Elevation:** Sticks to top of viewport (`position: sticky; top: 0; z-index: 200;`), with subtle bottom border (`#E2E8F0`).
- **Country Selector Pill:** Displays current active country flag/code (e.g., `🇮🇳 India`, `🇺🇸 USA`). Clicking opens modal to switch geographic jurisdiction.
- **Role Badge:** Pill indicator rendering current authorization scope (`PATIENT`, `CLINICIAN`, `ADMINISTRATOR`).
- **Responsive Behavior:** Below `1024px` (tablet), menu items collapse into a slide-over mobile drawer triggered by a standard hamburger button.

---

### 4.2 Patient Sidebar Navigation (`<AppSidebar />`)

#### Purpose
Delivers vertical hierarchical navigation across all primary patient workspaces.

#### Navigation Items
1. **Dashboard** (`/patient/dashboard`) — Executive risk overview and recent telemetry.
2. **New Assessment** (`/patient/assessments/new`) — Multi-step clinical intake wizard.
3. **Assessment History** (`/patient/assessments`) — Chronological record of previous evaluations.
4. **Health Trends** (`/patient/trends`) — Longitudinal biomarker trajectory charts.
5. **Explainability & Scenarios** (`/patient/explainability`) — SHAP feature attribution and counterfactual explorer.
6. **Provider Directory** (`/patient/directory/doctors`) — Country-specific verified cardiologist search.
7. **Hospital Facilities** (`/patient/directory/hospitals`) — Country-specific emergency and cardiac center search.
8. **Insurance Guidance** (`/patient/insurance`) — Localized health coverage and reimbursement information.
9. **Settings & Privacy** (`/patient/settings`) — Consent revocation, data export, unit preferences.

---

## 5. Data Display Components

### 5.1 Dual Risk Gauge Card (`<RiskGaugeCard />`)

#### Purpose
Renders the primary algorithmic prediction output with dual perspective:
1. **Angiographic CAD Association Likelihood** (Current ML Cleveland cohort model).
2. **10-Year Cardiovascular Event Risk** (Framingham / QRISK3 population benchmark if clinical criteria met).

#### Anatomy & Guardrails
```
┌────────────────────────────────────────────────────────────────────────┐
│ CARDIOVASCULAR ASSOCIATION EVALUATION                                  │
│                                                                        │
│       ┌───────────────────┐             ┌───────────────────┐          │
│       │        42%        │             │        12%        │          │
│       │   MODERATE CAD    │             │   10-YEAR RISK    │          │
│       │    LIKELIHOOD     │             │    POPULATION     │          │
│       └───────────────────┘             └───────────────────┘          │
│                                                                        │
│ ℹ️ EDUCATIONAL MODEL: Benchmark derived from historical observational  │
│ clinical study cohorts. This is an informational estimation, not a    │
│ medical diagnosis or clinical risk calculation.                       │
└────────────────────────────────────────────────────────────────────────┘
```

#### Design Directives
- **Zero Ambiguity:** Dial or bar meter clearly displays numerical percentages with tabular monospace typography.
- **Required Disclaimer:** A permanently affixed educational banner is embedded directly into the card footer.
- **Accessible Text Fallback:** Screen readers receive structured text: *"Calculated CAD association likelihood is 42 percent, classified as Moderate Risk. Benchmark 10-year cardiovascular population risk is 12 percent."*

---

### 5.2 SHAP Waterfall Attribution Display (`<ShapWaterfallCard />`)

#### Purpose
Visualizes local feature attributions showing how individual patient biomarkers pushed the prediction higher or lower relative to the cohort baseline.

#### Visual Hierarchy
```
Base Cohort Expectation: 0.38 (38%)
─────────────────────────────────────────────────────────────────────────
Resting BP (+24 mmHg)         │===================▲ (+0.14)   [Crimson]
Serum Cholesterol (+45 mg/dL) │==========▲          (+0.08)   [Crimson]
Age (54 years)                │===▲                 (+0.03)   [Crimson]
Thallium Stress: Normal       │         ▼========   (-0.06)   [Blue]
Max Heart Rate (168 bpm)      │      ▼===========   (-0.11)   [Blue]
─────────────────────────────────────────────────────────────────────────
Final Model Output Likelihood: 0.46 (46%)
```

#### Specifications
- **Zero Reference Line:** A distinct vertical dashed rule line marks $0.00$ SHAP attribution.
- **Directional Symbols:** Every bar includes an explicit directional arrow (`▲` = higher likelihood, `▼` = lower likelihood).
- **Tabular Data Alternative:** A 1-click toggle switches the visual waterfall into a clean, accessible tabular grid with column sorting.

---

## 6. Feedback & Notification Components

### 6.1 Clinical Safety Alert Banner (`<SafetyBanner />`)

#### Purpose
Communicates safety-critical information, emergency warning thresholds, and missing biomarker constraints.

#### Severity Tiers
1. **`emergency`:** Solid `#FEF2F2` background, `2px solid #DC2626` border, `#B91C1C` text.
   - *Example:* *"Immediate Attention: Severe chest pain during rest requires urgent medical evaluation. Contact emergency services (e.g., 911 / 112 / 102) immediately."*
   - Includes direct click-to-call emergency button.
2. **`warning`:** Solid `#FFFBEB` background, `1px solid #D97706` border, `#B45309` text.
   - *Example:* *"Missing Lab Value: Fasting Blood Sugar was not provided. Assessment was executed using cohort median imputation."*
3. **`info`:** Solid `#F0F9FF` background, `1px solid #0284C7` border, `#0369A1` text.
   - *Example:* *"Educational Platform: Results are intended for awareness and doctor-patient dialogue only."*

---

### 6.2 Accessible Modal Dialog (`<ModalDialog />`)

#### Anatomy & Behaviors
- **Backdrop:** `#0F172A` with 60% opacity (`rgba(15, 23, 42, 0.6)`), backdrop blur `2px`.
- **Focus Trap:** When opened, focus shifts automatically to modal heading; pressing `Tab` cycles exclusively within modal elements.
- **Escape Key:** Pressing `Escape` closes modal (unless blocked by an uncompleted destructive confirmation).
- **Close Button:** Top-right `24×24px` icon with explicit `aria-label="Close dialog"`.
- **Scroll Lock:** Background document body scroll is locked (`overflow: hidden`) while modal is active.
