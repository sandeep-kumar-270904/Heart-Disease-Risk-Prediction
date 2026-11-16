# HeartXAI 2.0 — Design Quality Acceptance Checklist

**Document ID:** `HX2-DES-015`  
**Version:** `2.0.0`  
**Status:** `Approved Specification`  
**Author:** Engineering Quality Lead & Principal Product Designer  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011  

---

## 1. Quality Assurance Objective

This document defines the **measurable, verifiable acceptance criteria** that every frontend view, component, and interaction in HeartXAI 2.0 must pass prior to design sign-off and frontend production release.

No pull request implementing UI or design tokens may be merged without satisfying 100% of the criteria detailed below.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   DESIGN QUALITY AUDIT DIMENSIONS                      │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Visual Hierarchy & Spacing        │ 7. Form Usability & Input Rules │
│ 2. Design Token Consistency          │ 8. Data Readability & Telemetry │
│ 3. Usability & Cognitive Ergonomics  │ 9. Healthcare Safety Standards  │
│ 4. Accessibility (WCAG 2.2 AA)       │ 10. Error Prevention & Recovery │
│ 5. Responsiveness Across Breakpoints │ 11. Interaction & Feedback State│
│ 6. Navigation & Breadcrumb Clarity   │ 12. Visual Polish & Typography  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Measurable Acceptance Criteria Checklist

### Dimension 1: Visual Hierarchy & Spacing Rhythm
- [ ] **Grid Conformance:** 100% of component margins, paddings, and gaps align to the 8pt spatial grid (or 4pt micro-steps for chips/badges). Zero arbitrary pixel values (e.g., `margin-top: 13px` is prohibited).
- [ ] **Line-Length Constraints:** Body narrative and clinical explanation containers enforce a maximum width of 75 characters per line (`max-w-prose` / `max-width: 65ch`).
- [ ] **Typographic Primacy:** Every screen has exactly one `H1` tag. Heading levels decrease monotonically (`H1` $\rightarrow$ `H2` $\rightarrow$ `H3`) without skipping levels.

### Dimension 2: Design Token Consistency
- [ ] **Zero Hardcoded CSS Values:** No hardcoded hex values, font sizes, or pixel radii exist in component files. All styles bind strictly to design tokens defined in `docs/design/DESIGN_TOKENS.md`.
- [ ] **Dark Mode Parity:** All surfaces, borders, text, and data visualization elements render with compliant contrast in both Light (`:root`) and Dark (`.dark`) modes.

### Dimension 3: Usability & Cognitive Ergonomics
- [ ] **Three-Second Rule:** On any assessment result screen, the overall CAD likelihood and risk stratum are comprehensible within 3 seconds of page load.
- [ ] **Chunked Assessment:** The intake assessment wizard is chunked into logical categories of $\le 5$ fields per step.
- [ ] **Progress Transparency:** The current step number and total steps (e.g., *"Step 3 of 6"*) are persistently visible during multi-step flows.

### Dimension 4: Accessibility (WCAG 2.2 Level AA Standard)
- [ ] **Contrast Ratios:** Normal body text satisfies $\ge 4.5:1$ against background; large headings ($\ge 24\text{px}$) and active UI borders satisfy $\ge 3:1$.
- [ ] **Keyboard Navigability:** 100% of interactive controls can be reached and activated using the `Tab`, `Enter`, `Space`, and Arrow keys.
- [ ] **Focus Indicators:** Focus rings are visible on all interactive elements via `:focus-visible` (`2px solid #0284C7` with `2px` offset). `outline: none` is never applied without a high-contrast replacement.
- [ ] **Screen Reader Semantics:** Landmarks (`<header>`, `<main>`, `<nav>`, `<aside>`) are present on all screens. Form fields are explicitly bound to `<label>` elements via `for`/`id` pairs.
- [ ] **Touch Target Size:** Interactive targets on mobile viewports measure at least $44\times 44\text{px}$ with $\ge 8\text{px}$ separation between adjacent buttons.
- [ ] **Reduced Motion Support:** Enabling `@media (prefers-reduced-motion: reduce)` disables non-essential animations, translations, and sliding transitions.

### Dimension 5: Responsiveness Across Breakpoints
- [ ] **Zero Horizontal Page Overflow:** No page produces horizontal scrolling on mobile viewports ($320\text{px}$–$639\text{px}$).
- [ ] **Adaptive Navigation:** Sidebar transforms smoothly into a slide-over drawer below $1024\text{px}$, paired with a persistent bottom navigation bar on mobile ($<640\text{px}$).
- [ ] **Data Table Reflow:** Tables on mobile either transform into stacked summary cards or provide smooth horizontal swiping with a sticky primary identifier column.

### Dimension 6: Navigation & Breadcrumb Clarity
- [ ] **No Dead Ends:** Every sub-page contains a clickable breadcrumb trail and a clear back-navigation mechanism.
- [ ] **Active State Indication:** The current active route is visibly highlighted in the sidebar and bottom navigation bar with high-contrast text and a left accent bar.

### Dimension 7: Form Usability & Input Rules
- [ ] **Unit Affixes Present:** Every clinical input field has its physical unit visibly anchored adjacent to or inside the input container (e.g., `mmHg`, `mg/dL`).
- [ ] **Dynamic Unit Conversion:** Toggling from `mg/dL` to `mmol/L` updates the displayed numeric value, input placeholder, and validation bounds simultaneously.
- [ ] **Mobile Virtual Keypads:** Numeric biomarker inputs specify `type="number" inputmode="decimal"` to invoke the decimal keypad on iOS and Android.

### Dimension 8: Data Readability & Telemetry
- [ ] **Tabular Numerals:** All laboratory numbers, blood pressure readings, timestamps, and model odds ratios utilize `font-variant-numeric: tabular-nums`.
- [ ] **Zero Baseline Adherence:** Bar charts and waterfall diagrams anchor to an unbroken baseline; no truncated Y-axes are used without explicit break symbols.
- [ ] **Accessible Chart Alternatives:** Every visual SVG chart is paired with a 1-click toggle to an accessible HTML data table.

### Dimension 9: Healthcare Safety Standards
- [ ] **Non-Diagnostic Framing:** No UI element uses the term *"Diagnosis"*, *"Diagnostic Guarantee"*, or *"Prescription"*. The model output is explicitly labeled *"Angiographic CAD Association Likelihood"*.
- [ ] **Educational Model Disclaimer:** A permanent disclaimer banner is embedded directly into the assessment results card.
- [ ] **SHAP Causal Protection:** SHAP charts explicitly state that feature contributions represent mathematical weights in the model, not biological causes of disease.
- [ ] **Emergency Intercept:** Entering resting chest pain combined with severe hypertensive readings triggers an unmissable Crimson Emergency Banner with a click-to-call emergency button (`112 / 102 / 911`).
- [ ] **Multi-Sensory Warnings:** Risk strata and alerts never rely on color alone; they always include an icon, a text label, and a numeric percentage range.

### Dimension 10: Error Prevention & Recovery
- [ ] **Destructive Action Confirmation:** Destructive operations (e.g., deleting account, revoking consent, rolling back model) require a two-step confirmation dialog with explicit typed text confirmation.
- [ ] **Inline Error Association:** Form validation errors are linked to their inputs via `aria-describedby` and describe how to correct the value in plain language.
- [ ] **Draft Preservation:** Multi-step assessment inputs are saved locally in encrypted state so page refreshes do not discard entered data.

### Dimension 11: Interaction Feedback & States
- [ ] **Deterministic State Coverage:** Every component implements visual designs for: *Default, Hover, Active, Focus, Disabled, Loading, Error*.
- [ ] **Loading Feedback:** Actions taking $> 200\text{ms}$ display a spinner or skeleton loader with `aria-busy="true"`. Buttons entering a loading state are disabled against duplicate clicks.
- [ ] **Success Confirmation:** Form saves and profile updates trigger an accessible toast notification that disappears after 4 seconds and can be dismissed via keyboard.

### Dimension 12: Visual Polish & Clean Aesthetics
- [ ] **No Superfluous AI Tropes:** No neon gradients, floating cyber orbs, glowing sci-fi borders, or ungrounded 3D graphics exist anywhere in the interface.
- [ ] **Clean Card Geometry:** Cards maintain consistent 8px corner radii, 1px structural slate borders, and subtle top-down ambient drop shadows.
