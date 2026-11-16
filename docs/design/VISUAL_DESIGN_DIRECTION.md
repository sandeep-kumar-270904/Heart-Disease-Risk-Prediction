# HeartXAI 2.0 — Visual Design Direction

**Document ID:** `HX2-DES-002`  
**Version:** `2.0.0`  
**Status:** `Approved Specification`  
**Author:** Principal Product Designer & Frontend Experience Architect  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011  

---

## 1. Design Direction Philosophy: "Clinical Precision & Patient Calm"

The visual direction of **HeartXAI 2.0** repudiates the hyper-stylized, superficial aesthetics often found in generic tech demos, crypto apps, and speculative AI prototypes. 

In cardiovascular healthcare, visual noise, low contrast, and ungrounded decorative animations induce cognitive fatigue, heighten patient anxiety, and degrade clinical trustworthiness.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   AESTHETIC ARCHITECTURE COMPARISON                    │
├───────────────────────────────────┬────────────────────────────────────┤
│ REJECTED (GENERIC AI DASHBOARDS)  │ ADOPTED (HEARTXAI 2.0 DIRECTION)   │
├───────────────────────────────────┼────────────────────────────────────┤
│ • Heavy neon / multi-color glow   │ • Grounded clinical slate & teal   │
│ • Translucent frosted glass cards │ • Solid, high-contrast surfaces    │
│ • Floating decorative 3D shapes   │ • Functional anatomical diagrams   │
│ • Low contrast gray-on-gray text  │ • WCAG 2.2 AA compliant typography │
│ • Arbitrary circular gauge dials  │ • Calibrated, contextual meters    │
│ • Aggressive pulsing red badges   │ • Calm, structured alert banners   │
│ • Chaotic responsive collapses    │ • Predictable, content-driven grid │
└───────────────────────────────────┴────────────────────────────────────┘
```

---

## 2. Spatial System & Layout Rhythms

### 2.1 The 8-Point Spatial Grid
All interface spacing (margins, paddings, gap dimensions) is derived from an 8-point base grid. For micro-components requiring tight spatial density (badges, table cells, form control inputs), a 4-point half-step is permitted.

```
  0px   4px   8px   12px   16px   20px   24px   32px   40px   48px   64px
   │     │     │     │      │      │      │      │      │      │      │
  [0]  [0.5]  [1]  [1.5]   [2]   [2.5]   [3]    [4]    [5]    [6]    [8]
```

* **Grid Application Rules:**
  - **Component Internal Padding:** $8\text{px}$ (tight inputs), $12\text{px}$ (standard buttons, dropdown items), $16\text{px}$ (cards, alert banners).
  - **Component Stacking Gaps:** $12\text{px}$ (tight form groups), $16\text{px}$ (card internal sections), $24\text{px}$ (adjacent card grids).
  - **Page Layout Margins:** $16\text{px}$ (mobile viewport), $24\text{px}$ (tablet), $32\text{px}$ (desktop container).
  - **Section Spacing:** $32\text{px}$ (minor subsection), $48\text{px}$ (major page sections).

### 2.2 Container Archetypes & Max Widths
To prevent elongated lines of text that impair reading comprehension ($\ge 80$ characters per line), layouts are constrained by explicit max-width containers:

```
┌──────────────────────────────────────────────────────────────┐
│ Viewport Width                                               │
│   ┌──────────────────────────────────────────────────────┐   │
│   │ Max Container: 1280px (Standard Application Canvas)  │   │
│   │   ┌──────────────────────────────────────────────┐   │   │
│   │   │ Form & Text Reading Container: 768px         │   │   │
│   │   └──────────────────────────────────────────────┘   │   │
│   └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

1. **`container-sm` (640px):** Single-column intake wizards, authentication cards, modal dialogs.
2. **`container-md` (768px):** Long-form clinical documentation, educational articles, patient narrative reports.
3. **`container-lg` (1024px):** Split-view layouts (intake form + live telemetry summary).
4. **`container-xl` (1280px):** Primary clinical analytics dashboard, comparative trend charts, multi-column provider directories.
5. **`container-2xl` (1536px):** Full-bleed administrative audit tables, model governance matrices (high-density data).

---

## 3. Surface Architecture & Layering

### 3.1 Solid Layering vs. Frosted Translucency
To guarantee deterministic color contrast and avoid rendering latency on low-powered mobile devices, HeartXAI 2.0 utilizes **opaque, solid surfaces** with distinct border delimitation rather than backdrop-filter glassmorphism.

```
Level 0: Canvas Background      ─── Light: #F8FAFC (Slate 50)  / Dark: #0F172A (Slate 900)
Level 1: Base Card Surface      ─── Light: #FFFFFF (Pure White) / Dark: #1E293B (Slate 800)
Level 2: Nested Card / Table    ─── Light: #F1F5F9 (Slate 100) / Dark: #334155 (Slate 700)
Level 3: Floating Overlay/Modal ─── Light: #FFFFFF (White + Sh) / Dark: #1E293B (Slate 800 + Sh)
```

### 3.2 Border and Divider Disciplines
- **Structural Borders:** Cards and containers use a crisp `1px solid` border (`#E2E8F0` in light mode, `#334155` in dark mode).
- **Interactive Focus Borders:** Form elements and clickable cards use an interior `1px` border plus an exterior `2px` focus offset ring (`#0284C7` with `2px` transparent offset).
- **Horizontal Dividers:** Soft `1px` rule lines (`#E2E8F0` light, `#334155` dark) separate logical subsections without cluttering visual hierarchy.

### 3.3 Elevation and Shadows
Drop shadows in HeartXAI 2.0 are purely functional and directional, simulating a subtle top-down ambient light source:

| Elevation Level | CSS Shadow Definition | Primary Use Case |
| :--- | :--- | :--- |
| **`elevation-none`** | `none` | Default cards, flat inputs, embedded tables. |
| **`elevation-sm`** | `0 1px 2px 0 rgba(15, 23, 42, 0.05)` | Card hover state, select dropdown button. |
| **`elevation-md`** | `0 4px 6px -1px rgba(15, 23, 42, 0.08), 0 2px 4px -2px rgba(15, 23, 42, 0.04)` | Dropdown menus, popovers, sticky table headers. |
| **`elevation-lg`** | `0 10px 15px -3px rgba(15, 23, 42, 0.10), 0 4px 6px -4px rgba(15, 23, 42, 0.05)` | Modal dialogs, drawer panels. |
| **`elevation-xl`** | `0 20px 25px -5px rgba(15, 23, 42, 0.12), 0 8px 10px -6px rgba(15, 23, 42, 0.06)` | Emergency clinical alert modal overlays. |

---

## 4. Typography & Visual Scannability

### 4.1 Visual Hierarchy & Rhythm
Healthcare interfaces are read under varied conditions: by patients scanning for reassurance, and by clinicians verifying lab values in seconds. The hierarchy must enforce immediate scanning:

1. **Page Title (H1):** `30px` / `36px` line-height, Semi-Bold (`600`). Anchor of the viewport.
2. **Section Header (H2):** `24px` / `32px` line-height, Semi-Bold (`600`). Delineates functional domains (e.g., "Feature Attribution Breakdown").
3. **Card / Subsection Header (H3):** `18px` / `24px` line-height, Medium (`500`). Groups related fields.
4. **Primary Body Text:** `16px` / `24px` line-height, Regular (`400`). Patient instructions, narrative explanations.
5. **Secondary / Supporting Text:** `14px` / `20px` line-height, Regular (`400`). Helper descriptions, timestamp citations, unit qualifiers.
6. **Micro-Copy / Captions:** `12px` / `16px` line-height, Medium (`500`). Form field micro-labels, chart axis markers.

### 4.2 Numeric Telemetry & Monospace Integration
All clinical biomarker measurements, laboratory numeric values, odds ratios, model confidence intervals, and SHAP weights **must** render in tabular monospace figures (`font-variant-numeric: tabular-nums`). This guarantees vertical alignment across multi-row tables, comparison columns, and counterfactual scenario cards:

```
  Metric                  Baseline               Hypothetical Scenario
  Resting BP:             154.00 mmHg            128.00 mmHg ( -26.00 )
  Serum Cholesterol:      268.00 mg/dL           210.00 mg/dL ( -58.00 )
  Fasting Blood Sugar:    132.00 mg/dL            98.00 mg/dL ( -34.00 )
```

---

## 5. Motion and Interaction Philosophy

### 5.1 Purposeful Functional Motion
Motion in HeartXAI 2.0 exists solely to communicate state transitions, preserve spatial orientation, and confirm user input. Decorative loops, floating bounces, and continuous spinning animations are prohibited.

### 5.2 Transition Curves and Durations
- **Micro-Transitions (Hover, Focus, Toggle):** `150ms ease-out`. Immediate response without jarring pop-in.
- **Surface Expansions (Accordion, Dropdown, Drawer):** `200ms cubic-bezier(0.16, 1, 0.3, 1)`. Smooth spatial unfold.
- **Modal Presentations & Route Transitions:** `250ms cubic-bezier(0.16, 1, 0.3, 1)`. Clean fade-and-settle.

### 5.3 Accessibility: `prefers-reduced-motion` Discipline
When a user has configured their operating system for reduced motion:
- All transform translations, slide-ins, and zooms are deactivated (`transform: none`).
- Transitions collapse to instantaneous state changes or subtle opacity fades (`transition: opacity 100ms ease-in-out`).
- All skeleton loaders switch from animated shimmer sweeps to a static, low-contrast solid wash.

---

## 6. Graphic Style & Pedagogical Imagery

### 6.1 Anatomical Graphics Standards
- Vector SVG format only (responsive, scalable, crisp on retina displays).
- Anatomically accurate line weights representing coronary arteries (LAD, LCx, RCA) and cardiac chambers.
- Coloration restricted to semantic clinical tokens: normal myocardial perfusion in slate/teal, localized ischemic zones highlighted in muted amber/ochre.
- Every graphic must be paired with visible textual labels and descriptive `alt` tags.

### 6.2 Data Visualization Styling
- Axes must have clear tick marks, explicit zero baselines, and unambiguous units.
- Grid lines must be subtle (`#E2E8F0` at 50% opacity) so as not to overwhelm data curves.
- Data curves and points must have distinct visual markers (circle, square, triangle) in addition to color to accommodate color-deficient vision.
