# HeartXAI 2.0 — Brand Identity Guidelines

**Document ID:** `HX2-DES-001`  
**Version:** `2.0.0`  
**Status:** `Approved Specification`  
**Author:** Principal Product Designer & Design Systems Architect  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011  

---

## 1. Executive Summary & Positioning

### 1.1 Brand Positioning Statement
**HeartXAI 2.0** is an **Explainable AI-Based Cardiovascular Health Awareness and Educational Medical Assistance Platform**. 

It bridges the divide between opaque clinical predictive algorithms and patient comprehension by uniting modern machine learning inference with rigorous model explainability (SHAP attribution and counterfactual analysis), structured health education, and country-configurable healthcare navigation.

```
       [ Mathematical Rigor & Transparency ]
                         │
                         ▼
┌─────────────────────────────────────────────────┐
│                 HEARTXAI 2.0                    │
│   Explainable AI Cardiovascular Health Platform │
└─────────────────────────────────────────────────┘
                         ▲
                         │
        [ Patient Calm & Clinical Restraint ]
```

### 1.2 Core Value Proposition
- **Epistemological Honesty:** HeartXAI never masquerades as a certified medical diagnostic device. It explicitly presents its predictions as **Angiographic CAD Association Likelihood** based on historical observational cohort benchmarks.
- **Explainability by Default:** No risk score is rendered in isolation. Every numerical output is accompanied by local feature attributions (SHAP) and hypothetical counterfactual what-if scenarios.
- **Actionable Health Literacy:** Rather than inducing anxiety through uncontextualized risk scores, it transforms complex clinical biomarkers into clear, patient-accessible educational narratives.
- **Country-Configurable Reach:** Designed from the foundation to adapt across geographic jurisdictions, accommodating localized terminology, measurement units ($\text{mg/dL} \leftrightarrow \text{mmol/L}$), directory registries, and emergency resources.

---

## 2. Brand Personality & Tone of Voice

### 2.1 The Four Pillars of Brand Personality

| Brand Pillar | What It Means | What It Looks & Sounds Like | What It Avoids |
| :--- | :--- | :--- | :--- |
| **Clinical Credibility** | Inspires trust through peer-reviewed methodologies, evidence-based guidelines, and rigorous software engineering. | Clean typography, generous whitespace, authoritative terminology, explicit data provenance citations. | Neon gradients, "futuristic AI" tropes, sci-fi cyber graphics, hyper-glossy surfaces. |
| **Scientific Restraint** | Understands the boundaries of predictive modeling and algorithmic inference in medicine. | Clear confidence intervals, explicit disclaimer banners, precise non-diagnostic phrasing ("associated with", "observed pattern"). | "100% accurate", "diagnostic cure", sensationalist warnings, alarmist visual flares. |
| **Calm Reassurance** | Patients reviewing cardiovascular health metrics are often anxious or vulnerable; the interface must de-escalate anxiety. | Balanced slate backgrounds, gentle transitions, structured information chunking, compassionate helper text. | Flashing emergency red indicators for routine elevated numbers, aggressive popups, countdown timers. |
| **Mathematical Honesty** | Data is presented without optical distortion or decorative skew. | Zero-baseline bar charts, labeled axes with units, tabular monospace numbers, clear SHAP zero-contribution lines. | Truncated Y-axes to exaggerate differences, 3D pie charts, unlabeled gauge meters, uncalibrated risk dials. |

### 2.2 Voice and Tone Guidelines

```
┌────────────────────────────────────────────────────────────────────────┐
│                        TONE OF VOICE SPECTRUM                          │
├────────────────────────────────────────────────────────────────────────┤
│ Clinical ───────────────●──────────────────────── Casual               │
│ Authoritative ──────────●──────────────────────── Uncertain            │
│ Empathetic ─────────────●──────────────────────── Clinical Coldness    │
│ Transparent ────────────●──────────────────────── Opaque               │
└────────────────────────────────────────────────────────────────────────┘
```

#### Comparison Examples

* **Incorrect (Alarmist / Diagnostic):**
  > *"Critical Warning: You are at 78% risk of a heart attack! Consult an emergency doctor immediately to prevent severe cardiac arrest."*
* **Correct (Calm / Transparent / Educational):**
  > *"The machine learning model estimated a 78% statistical likelihood of angiographic coronary artery disease association, benchmarked against historical clinical study cohorts. Primary contributing factors identified include resting blood pressure (160 mmHg) and serum cholesterol (280 mg/dL). This educational assessment is not a medical diagnosis. Please review these findings with a licensed healthcare provider."*

* **Incorrect (Prescriptive Counterfactual):**
  > *"You must reduce your fasting blood sugar to 95 mg/dL to lower your risk score by 14%."*
* **Correct (Hypothetical Exploration):**
  > *"In a hypothetical scenario where fasting blood sugar is modeled at 95 mg/dL while holding other clinical variables constant, the model's association likelihood decreases by 14%. Discuss metabolic health targets with your physician."*

---

## 3. Core Design Principles

### Principle 1: Clarity Over Decoration
Every pixel, line, and container must serve an informational or navigational purpose. Decorative flourishes that distract from reading clinical biomarkers or interpreting SHAP waterfall charts are strictly eliminated.

### Principle 2: Epistemological Transparency
The interface must never conceal how a score was derived or hide algorithmic limitations. If an inference was generated by an XGBoost model trained on the UCI/Cleveland Heart Disease dataset, the model version, training cohort characteristics, and limitation disclaimers must be accessible within one click.

### Principle 3: Zero Color-Only Signifiers
No clinical risk, warning, success, or anomaly may be communicated solely by color. Every status indicator must combine color with a clear text label, an accessible icon, and an ARIA status attribute to support color-blind and low-vision users.

### Principle 4: Units are Inseparable from Biomarkers
A number without a unit is clinically ambiguous. In HeartXAI 2.0, every biomarker display and input must explicitly bind the value and its unit (e.g., `120 mmHg`, `210 mg/dL`, `5.4 mmol/L`). Unit toggling must update the label and the value simultaneously without loss of precision.

### Principle 5: Progressive Disclosure of Clinical Complexity
A lay patient requires intuitive executive summaries and clear plain-language explanations; a visiting clinician requires raw odds ratios, standard errors, model version hashes, and tabular SHAP feature contributions. HeartXAI 2.0 employs layered disclosure: intuitive overviews by default, deep clinical and mathematical telemetry upon expansion.

---

## 4. Visual Direction

### 4.1 Visual Hierarchy & Clean Geometry
- **Layout Grid:** 8pt base grid for spacing, 4pt subgrid for tight micro-alignments (chips, badges, icon padding).
- **Surfaces:** Flat, clean slate surfaces (`#FFFFFF` on `#F8FAFC` light; `#1E293B` on `#0F172A` dark) with subtle 1px structural borders (`#E2E8F0` / `#334155`).
- **Elevation:** Minimal depth. Subtle, soft drop-shadows are used exclusively to indicate interactive floating layers (modals, dropdowns, sticky headers). Avoid stacked 3D shadows.
- **Corner Radii:** Controlled, professional radii (4px for micro-badges, 8px for cards and form inputs, 12px for modal dialogs). Avoid hyper-rounded "bubble" interfaces.

### 4.2 Imagery, Icons & Anatomical Graphics
- **Iconography Style:**
  - Standardized on a 24×24px bounding box.
  - Consistent 1.75px stroke width with rounded join and cap terminals.
  - Optical centering and balance.
  - Purely functional icons drawn from recognized medical and interface iconography (e.g., Lucide React / Feather icons).
- **Anatomical & Pedagogical Graphics:**
  - High-precision vector line drawings of cardiac anatomy (coronary arteries, myocardial walls, electrical conduction system).
  - Clean two-tone shading using brand slate and accent blue.
  - No photographic gore or hyper-realistic clinical surgery photographs in consumer-facing flows.
  - Clear diagrammatic callouts for educational topics (e.g., plaque accumulation, ischemic ST-segment depression).

---

## 5. Logo & Brand Mark Guidelines

### 5.1 The HeartXAI Logomark Anatomy
The HeartXAI brand mark combines three fundamental visual concepts:
1. **The Cardiac Rhythm (Pulse/ECG Trace):** Symbolizing physiological telemetry and human life.
2. **The "X" (Explainability / Cross-Disciplinary):** Symbolizing transparent mathematical attribution and machine learning introspection.
3. **The Enclosing Shield / Node:** Symbolizing clinical safety, data integrity, and privacy governance.

```
            ╭───────────────╮
            │   /\     /\   │
            │  /  \___/  \  │   <── Cardiac Waveform + "X" Intersect
            │  \    X    /  │   <── Shield of Scientific Governance
            │   \       /   │
            ╰───────▼───────╯
               HeartXAI 2.0
```

### 5.2 Clearspace & Minimum Dimensions
- **Clearspace:** A minimum clearspace equal to the height of the letter "H" ($1.0X$) must surround the logomark on all four sides. No UI element, text, or boundary may intrude into this zone.
- **Minimum Digital Dimensions:**
  - Logomark + Wordmark: Minimum width `140px` (or `28px` height).
  - Standalone Mark (Favicon / App Icon): Minimum size `24×24px` (ideal `32×32px`).

### 5.3 Brand Misuse Rules
- **DO NOT** apply rainbow gradients or drop shadows to the logomark.
- **DO NOT** rotate, skew, stretch, or alter the aspect ratio of the logomark.
- **DO NOT** replace the brand blue or slate with unauthorized colors (e.g., neon purple or yellow).
- **DO NOT** place the dark logomark on low-contrast backgrounds (must maintain $\ge 4.5:1$ contrast against all surface backgrounds).
- **DO NOT** append unauthorized slogans or diagnostic claims (e.g., "HeartXAI — Automated Heart Diagnosis").
