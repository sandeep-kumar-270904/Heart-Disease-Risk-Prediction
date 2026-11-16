# HeartXAI 2.0 — Data Visualization Design Guidelines

**Document ID:** `HX2-DES-014`  
**Version:** `2.0.0`  
**Status:** `Approved Specification`  
**Author:** Principal Product Designer & ML Systems Architect  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011  

---

## 1. Data Visualization Philosophy: "Mathematical Honesty & Clinical Clarity"

Cardiovascular telemetry and machine learning inferences must never be distorted for dramatic effect. Truncated axes, arbitrary 3D graphics, decorative neon glows, and uncalibrated circular dials misinform patients, heighten panic, and degrade scientific trust.

In HeartXAI 2.0, every chart adheres to **Four Fundamental Visualization Axioms**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   FOUR DATA VISUALIZATION AXIOMS                       │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Zero Baseline & Unbroken Scales (No Optical Exaggeration)           │
│ 2. Compulsory Unit Binding on Every Axis and Tooltip                   │
│ 3. Explicit Differentiation Between Zero Values and Missing Data       │
│ 4. Universal Accessible Tabular Fallbacks                              │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Model Prediction & Likelihood Visualizations

### 2.1 The Calibrated Risk Strata Meter (`<RiskGaugeCard />`)
Rather than a misleading 360-degree automotive speedometer dial, HeartXAI 2.0 presents the estimated Angiographic CAD Association Likelihood via a **Calibrated Horizontal Segmented Risk Bar**:

```
0%                  30%                                70%               100%
┌───────────────────┬──────────────────────────────────┬───────────────────┐
│     LOW RISK      │          MODERATE RISK           │   ELEVATED RISK   │
│   (Emerald 500)   │           (Amber 500)            │   (Crimson 500)   │
└───────────────────┴─────────────────▲────────────────┴───────────────────┘
                                      │
                         Your Prediction: 42% (±4% CI)
                         Strata: Moderate CAD Association
```

#### Visual Specifications
- **Scale:** Fixed $[0\%, 100\%]$ continuous domain.
- **Calibrated Strata Boundaries:**
  - Low Risk: $0\% – 29\%$ (`#10B981` Emerald).
  - Moderate Risk: $30\% – 69\%$ (`#F59E0B` Amber).
  - Elevated Risk: $70\% – 100\%$ (`#EF4444` Crimson).
- **Current Position Marker:** A sharp inverted pointer triangle (`▲`) with an anchored numerical pill displaying the exact probability and $95\%$ confidence interval.
- **Accessible Text Equivalence:** Screen reader label: *"Model prediction is 42 percent with a 95 percent confidence interval of 38 to 46 percent, falling within the Moderate Risk stratum."*

---

## 3. Explainability (SHAP) Feature Attribution Visualizations

### 3.1 Interactive SHAP Waterfall Display
SHAP (SHapley Additive exPlanations) values sum algebraically from the training cohort base expected value ($E[f(x)] = 0.38$) to the patient's final predicted likelihood ($f(x) = 0.46$).

```
Base Expected Likelihood: 38.0%
─────────────────────────────────────────────────────────────────────────
Resting BP (+24 mmHg)         │===================▲ (+14.1%)  [Crimson 500]
Serum Cholesterol (+45 mg/dL) │==========▲          (+8.2%)   [Crimson 500]
Age (54 years)                │===▲                 (+3.4%)   [Crimson 500]
Thallium Stress: Normal       │         ▼========   (-6.1%)   [Blue 500]
Max Heart Rate (168 bpm)      │      ▼===========   (-11.6%)  [Blue 500]
─────────────────────────────────────────────────────────────────────────
Center Line: 0.00 Net Impact
Final Model Output Likelihood: 46.0%
```

#### Construction Rules
1. **Zero-Impact Anchor:** A distinct vertical dashed rule line (`1px dashed #94A3B8`) anchors the zero mark.
2. **Color Palette:**
   - Increases Likelihood: `#EF4444` (Crimson 500) with directional symbol `▲` and signed positive number (`+0.14`).
   - Decreases Likelihood: `#3B82F6` (Blue 500) with directional symbol `▼` and signed negative number (`-0.11`).
   - *Prohibition:* Never use Red vs Green for SHAP attribution (deuteranopia / protanopia conflict).
3. **Sorting Order:** Features are sorted in descending order of absolute mathematical magnitude ($|\phi_i|$), ensuring the strongest drivers appear at the top.
4. **Mandatory Explanatory Footnote:** *"Note: Feature contributions represent statistical weights in the XGBoost tree model; they do not imply biological cause of disease."*

---

## 4. Counterfactual "What-If" Scenario Comparisons

### 4.1 Comparative Grouped Bar Chart
When a user simulates modifications in modifiable physiological variables (e.g., reducing blood pressure and cholesterol):

```
                       Baseline Scenario        Simulated Hypothetical
CAD Likelihood:        [ 42%                  ]  [ 28% (-14%)           ]
Resting BP:            [ 154 mmHg             ]  [ 128 mmHg (-26 mmHg)  ]
Serum Cholesterol:     [ 245 mg/dL            ]  [ 195 mg/dL (-50 mg/dL)]
```

#### Visual Rules
- **Color Differentiation:** Baseline is rendered in neutral slate (`#64748B`), while the hypothetical scenario is rendered in brand sky (`#0284C7`).
- **Delta Labels:** Exact differences are displayed in parentheses beside the bars with directional minus signs.
- **Physiological Viability Indicator:** If an impossible or dangerous value is entered (e.g., Systolic BP $< 60\text{ mmHg}$), the simulation bar is disabled, and an amber warning badge appears: *"Value below viable outpatient limits."*

---

## 5. Longitudinal Health Trends & Trajectory Charts

### 5.1 Multi-Point Trend Lines (`<BiomarkerTrendChart />`)
Used in `/patient/trends` to track historical biomarker values and risk probabilities over 3, 6, 12, or 24 months.

```
Systolic BP (mmHg)
200 ┬
    │                                ● 162 mmHg (12 Aug)
160 ┼──────● 154 mmHg (14 May)      / \
    │       \                      /   ● 148 mmHg (14 Nov)
120 ┼════════●════════════════════●══════════════════════ [Target: <120]
 80 ┴────────┼────────────────────┼─────────┼──────────
          May 2026             Aug 2026   Nov 2026
```

#### Guidelines
- **Reference Range Bands:** Clinically recognized normal physiological ranges (e.g., BP $< 120\text{ mmHg}$, Cholesterol $< 200\text{ mg/dL}$) are shaded as a soft ambient green background band (`#ECFDF5` with 40% opacity).
- **Data Markers:** Each point has a distinct circular anchor (`radius: 5px`) with a white stroke border.
- **Differentiating Zero vs Missing:**
  - A reading of zero is plotted at $0$ on the Y-axis.
  - An omitted / missing reading is rendered as a **dashed line bridge** with an unfilled hollow diamond marker (`◇`), with a tooltip stating: *"Measurement omitted / not recorded on this date."*
- **No Y-Axis Truncation Without Disclosure:** If a zoom scale is applied to observe fine variance, an explicit axis break symbol (`≈`) must appear at the base of the Y-axis.

---

## 6. Administrative Infrastructure & Drift Visualizations

### 6.1 Population Stability Index (PSI) Distribution Curves
Used in `/admin/models/drift` to display shifts between training cohort feature distributions and live incoming patient telemetry.

- Two overlaid smooth area curves:
  - Training Cohort Baseline: Slate fill (`#94A3B8` at 20% opacity).
  - Recent 30-Day Production Inflow: Sky Blue fill (`#0284C7` at 30% opacity).
- Divergence zones highlighted with subtle hatch patterns.
- KS-test $p$-value and overall feature PSI clearly labeled in a top-right legend card.

---

## 7. Universal Accessible Tabular Fallback Matrix

Every data visualization in HeartXAI 2.0 must be accompanied by an immediate 1-click tabular view toggle (`[Switch to Data Table]`):

| Chart Component | Tabular Alternative Structure | Screen Reader Header Announcement |
| :--- | :--- | :--- |
| **Risk Strata Meter** | 1-row table: Likelihood %, Strata, 95% Confidence Interval, Benchmark | *"Risk estimation summary table"* |
| **SHAP Waterfall** | Multi-row table: Feature Name, Value, Direction, SHAP Impact, Plain Meaning | *"Feature attribution table showing model contribution factors"* |
| **Counterfactual Compare** | 2-column comparison table: Baseline Value vs Simulated Value and Delta | *"Comparison table between baseline and simulated measurements"* |
| **Longitudinal Trends** | Chronological table: Date, Assessment ID, Blood Pressure, Cholesterol, Risk % | *"Chronological table of historical cardiovascular biomarker readings"* |
