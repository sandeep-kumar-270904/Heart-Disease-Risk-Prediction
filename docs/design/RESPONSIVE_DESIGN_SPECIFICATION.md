# HeartXAI 2.0 — Responsive Design Specification

**Document ID:** `HX2-DES-013`  
**Version:** `2.0.0`  
**Status:** `Approved Specification`  
**Author:** Frontend Experience Architect & Principal Product Designer  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011  

---

## 1. Responsive Layout Philosophy: "Mobile-First & Context-Aware"

Cardiovascular risk assessment must be equally accessible on a patient's mobile smartphone at home, on a tablet during an outpatient clinic intake, or on a clinician's high-resolution multi-monitor workstation.

Responsive design in HeartXAI 2.0 is **not merely scaling down desktop layouts**. It reorganizes information hierarchies to preserve legibility, prevents horizontal page blowout, and adapts interaction modalities (touch vs mouse/keyboard).

```
┌────────────────────────────────────────────────────────────────────────┐
│                      RESPONSIVE BREAKPOINT MATRIX                      │
├───────────────┬─────────────────┬──────────────────────────────────────┤
│ BREAKPOINT    │ VIEWPORT WIDTH  │ PRIMARY DEVICE TARGET                │
├───────────────┼─────────────────┼──────────────────────────────────────┤
│ **`xs / sm`** │ `< 640px`       │ Mobile smartphones (iPhone, Android) │
│ **`md`**      │ `640px–1023px`  │ Tablets portrait & landscape, iPads  │
│ **`lg`**      │ `1024px–1279px` │ Laptops, compact desktop displays    │
│ **`xl`**      │ `1280px–1535px` │ Standard desktop monitors            │
│ **`2xl`**     │ `≥ 1536px`      │ High-DPI clinical workstations       │
└───────────────┴─────────────────┴──────────────────────────────────────┘
```

---

## 2. Navigation Adaptations Across Viewports

```
┌────────────────────────────────────────────────────────────────────────┐
│ DESKTOP (≥ 1024px): Persistent Left Sidebar + Sticky Top Header        │
│ ┌────────┬───────────────────────────────────────────────────────────┐ │
│ │ Logo   │ Header: Country Selector | Role Badge | User Profile      │ │
│ │ Nav 1  ├───────────────────────────────────────────────────────────┤ │
│ │ Nav 2  │ Main Content Canvas                                       │ │
│ │ Nav 3  │                                                           │ │
│ └────────┴───────────────────────────────────────────────────────────┘ │
├────────────────────────────────────────────────────────────────────────┤
│ MOBILE (< 640px): Sticky Header + Off-Canvas Drawer + Bottom Nav Bar   │
│ ┌────────────────────────────────────────────────────────────────────┐ │
│ │ [≡] HeartXAI Logo                      [🇮🇳] [Profile Icon]        │ │
│ ├────────────────────────────────────────────────────────────────────┤ │
│ │ Main Content Canvas (Single Column Stack)                          │ │
│ ├────────────────────────────────────────────────────────────────────┤ │
│ │ [Dashboard]     [Assess]     [Trends]     [Directory]     [More]   │ │
│ └────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Desktop ($\ge 1024\text{px}$)
- **Left Sidebar:** Persistent `240px` width on desktop displays; collapsible to `64px` icon-only rail on compact screens.
- **Header:** Houses global country switcher, role badge, notifications dropdown, and user profile menu.

### 2.2 Mobile ($< 640\text{px}$)
- **Header:** Compact `56px` height; displays hamburger menu button, HeartXAI logomark, active country flag, and user avatar.
- **Slide-Over Drawer:** Tapping hamburger opens left slide-over drawer with full hierarchical sitemap, settings, and sign-out action.
- **Bottom Navigation Bar:** Persistent `60px` bottom navigation bar offering 1-thumb access to the 4 primary patient destinations: *Dashboard, New Assessment, Trends, Directory*.

---

## 3. Form Layout & Mobile Ergonomics

### 3.1 Multi-Column to Single-Column Reflow
- On desktop ($\ge 1024\text{px}$), form controls are organized in clean 2-column or 3-column grids (e.g., Systolic BP and Diastolic BP side-by-side).
- On mobile ($< 640\text{px}$), all form inputs **reflow into a single vertical stack** (`grid-cols-1`). This eliminates horizontal truncation of labels and ensures full-width tapping areas.

### 3.2 Mobile Keyboard Optimization
Every form input specifies the exact semantic `type`, `inputmode`, and `autocomplete` attributes to invoke optimal virtual keyboards on iOS and Android:
- Numeric biomarkers (Cholesterol, BP, Heart Rate): `type="number" inputmode="decimal"` (presents clean numeric keypad).
- Age: `type="number" inputmode="numeric"`.
- Date of Birth: `type="date"`.

### 3.3 Sticky Bottom Action Bar
During the 6-step assessment wizard on mobile:
- The `[Back]` and `[Continue to Next Step]` action buttons are pinned to a sticky bottom container (`position: sticky; bottom: 0; z-index: 50;`) with subtle drop shadow and white background.
- This ensures the primary submission button is always visible without requiring extensive scrolling.

---

## 4. Complex Data Table Handling on Mobile

Dense tabular data (Assessment History, Audit Logs, SHAP Telemetry) cannot fit on small screens without severe distortion. HeartXAI 2.0 employs **Two Responsive Table Strategies**:

### Strategy A: Adaptive Card Transformation (Patient Assessment History)
On screens $< 768\text{px}$, tabular rows transform automatically into independent **Summary Cards**:
```
Desktop Table View:
  Date          Risk Likelihood    Blood Pressure    Cholesterol    Action
  14 Nov 2026   42% (Moderate)     154/86 mmHg       245 mg/dL      [View]

Mobile Card Transformation:
┌────────────────────────────────────────────────────────┐
│ 14 Nov 2026                      [ Moderate: 42% ]     │
├────────────────────────────────────────────────────────┤
│ Blood Pressure: 154/86 mmHg     Cholesterol: 245 mg/dL │
├────────────────────────────────────────────────────────┤
│ [ View Breakdown ]                   [ Export PDF ]    │
└────────────────────────────────────────────────────────┘
```

### Strategy B: Sticky-Column Horizontal Scrolling (Admin Audit Tables)
For dense administrative tables with 8+ columns:
- The table container allows horizontal swiping (`overflow-x: auto; -webkit-overflow-scrolling: touch;`).
- The primary identifying column (*Timestamp* or *Actor Name*) remains **pinned to the left** (`position: sticky; left: 0; z-index: 10;`) with a subtle shadow separating it from scrollable columns.

---

## 5. Data Visualization Adaptations Across Viewports

### 5.1 SHAP Waterfall Chart
- **Desktop:** Horizontal waterfall with explicit labels on the Y-axis and numeric delta badges on the right.
- **Mobile ($< 640\text{px}$):**
  - Labels wrap gracefully onto two lines.
  - Bars maintain a minimum height of `28px` for touch inspectability.
  - Touch-scrubbing: Tapping any bar anchors the tooltip persistently until another bar is tapped (preventing hover flicker on touchscreens).
  - Prominent CTA allows instant switch to the accessible vertical tabular list.

### 5.2 Health Trends Longitudinal Line Chart
- **Desktop:** Displays all 4 biomarker trajectories simultaneously in a multi-axis chart.
- **Mobile:** Collapses into a **Single-Metric Carousel / Tab Selector**: patient toggles between *CAD Likelihood*, *Blood Pressure*, and *Cholesterol* one at a time, preventing visual clutter and overlapping data points.
