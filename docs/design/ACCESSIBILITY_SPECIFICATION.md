# HeartXAI 2.0 — Accessibility Specification (WCAG 2.2 AA)

**Document ID:** `HX2-DES-012`  
**Version:** `2.0.0`  
**Status:** `Approved Specification`  
**Author:** Certified Accessibility Specialist & Principal Design Systems Architect  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011  

---

## 1. Accessibility Policy & Target Standard

HeartXAI 2.0 enforces full compliance with the **Web Content Accessibility Guidelines (WCAG) 2.2 Level AA**, with Level AAA adherence in critical healthcare information domains (contrast ratios and error prevention).

In a healthcare application, accessibility is not merely an aesthetic convenience; it is a clinical safety imperative. Patients with low vision, motor tremors, color deficiency, or cognitive stress must be able to complete assessments, interpret results, and access emergency resources without hindrance.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   THE FIVE PILLARS OF HEARTXAI A11Y                    │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Keyboard Navigability & Predictable Focus Order                     │
│ 2. High-Contrast Typography & Visual Separators (≥ 4.5:1 / ≥ 3:1)      │
│ 3. Robust Screen Reader Semantics & ARIA Live Regions                  │
│ 4. Accessible Tabular Fallbacks for All Complex Visualizations         │
│ 5. Touch Target Ergonomics (≥ 44×44px) & Reduced-Motion Respect        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Keyboard Navigation & Focus Architecture

### 2.1 Tab Order & Skip Links
- **Skip Navigation Link:** The very first focusable element on every page is an accessible skip link: `<a href="#main-content" class="sr-only focus:not-sr-only">Skip to main content</a>`.
- **Logical Flow:** Tab progression follows natural reading order: Header $\rightarrow$ Sidebar $\rightarrow$ Main Content Landmarks $\rightarrow$ Form Controls $\rightarrow$ Actions.
- **Roving `tabindex`:** Used in tab lists and segmented controls: the active tab has `tabindex="0"`; inactive tabs have `tabindex="-1"` and are navigated via `Left`/`Right` arrow keys.

### 2.2 Focus Indicators (WCAG 2.2 Success Criterion 2.4.11 / 2.4.13)
- **Universal Focus Ring Rule:** All interactive elements (`<button>`, `<a>`, `<input>`, `<select>`, `<summary>`) **must** exhibit an unmistakable focus indicator when reached via keyboard navigation:
```css
:focus-visible {
  outline: 2px solid #0284C7; /* Brand Sky 600 */
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(2, 132, 199, 0.2);
}
```
- **Prohibition:** `outline: none` or `outline: 0` without an immediate high-contrast replacement is strictly forbidden.

### 2.3 Modal Focus Traps
When a modal dialog opens (e.g., Country Selector, Scenario Save Dialog, Rejection Modal):
1. Focus immediately transfers to the modal title (`<h2 id="modal-title">`).
2. Tabbing is strictly trapped within the modal container.
3. Pressing `Escape` closes the modal and returns focus to the trigger button that launched it.

---

## 3. Screen Reader Semantics & ARIA Implementation

### 3.1 Landmark Architecture
Every page utilizes standard HTML5 landmark elements:
- `<header role="banner">` (Global brand and navigation)
- `<nav role="navigation" aria-label="Main Navigation">` (Sidebar)
- `<main id="main-content" role="main">` (Primary workspace canvas)
- `<aside role="complementary">` (Educational sidebar / telemetry snapshot)
- `<footer role="contentinfo">` (Legal disclaimers, country badges)

### 3.2 Dynamic ARIA Live Regions (`aria-live`)
- **Assessment Step Transitions:** Announced politely via `<div aria-live="polite" class="sr-only">Step 3 of 6: Laboratory Blood Markers loaded</div>`.
- **Live Counterfactual Calculations:** When sliders are adjusted, the resulting delta is announced politely: `<div aria-live="polite" class="sr-only">Simulated likelihood decreased to 28 percent. Delta is negative 14 percent.</div>`.
- **Form Error Alerts:** Announced assertively via `aria-live="assertive"` so that the patient is informed of input blocks immediately upon submission.

---

## 4. Accessible Forms & Error Prevention

### 4.1 Label Binding and Description Associations
Every form control must have an explicitly bound `<label>` and helper container:
```html
<div class="form-group">
  <label for="cholesterol-input" class="form-label">
    Serum Cholesterol <span aria-hidden="true" class="text-crimson-600">*</span>
    <span class="sr-only">(Required field)</span>
  </label>
  <input 
    type="number" 
    id="cholesterol-input" 
    name="serum_cholesterol"
    aria-required="true"
    aria-invalid="false"
    aria-describedby="cholesterol-help cholesterol-error"
  />
  <span id="cholesterol-help" class="form-help">Reference range: 125 – 200 mg/dL</span>
  <span id="cholesterol-error" class="form-error hidden" role="alert"></span>
</div>
```

### 4.2 Error Identification & Recovery (WCAG 3.3.1 / 3.3.3)
- Errors are never indicated solely by border color.
- Errors must contain:
  1. An explicit `AlertCircle` warning icon.
  2. Clear, plain-language text explaining the error and how to fix it (e.g., *"Resting blood pressure must be between 70 and 240 mmHg. Please enter a valid number within this range."*).
  3. Automatic focus transfer to the first invalid field upon form submit attempt.

---

## 5. Accessible Alternatives for Data Visualizations

Complex SVG and canvas charts cannot be read directly by screen readers. HeartXAI 2.0 enforces a **Compulsory Accessible Fallback Table Rule** for all data visualizations.

```
┌────────────────────────────────────────────────────────┐
│ Visual Chart Container (SVG / Canvas)                  │
│ [aria-hidden="true"]                                   │
├────────────────────────────────────────────────────────┤
│ [ Button: Switch to Tabular Data View ]                │
├────────────────────────────────────────────────────────┤
│ Accessible Data Table (`<table class="sr-only ...">`)  │
│ Summarizes exact numerical inputs, reference baselines,│
│ and SHAP contribution values in semantic HTML.        │
└────────────────────────────────────────────────────────┘
```

* **SHAP Waterfall Fallback Table:**
  - `<caption>`: *"Feature attribution analysis showing mathematical contributions of your clinical measurements to the CAD likelihood score."*
  - `<thead>`: *Feature Name*, *Your Value*, *Cohort Average*, *Direction*, *Impact Score*.
  - Screen reader users can read every single feature impact without relying on chart visual comprehension.

---

## 6. Color Vision Deficiency & Multi-Sensory Communication

To guarantee comprehensibility for individuals with deuteranopia, protanopia, or tritanopia:
- **No Color-Alone Communication:** Risk strata, alert states, and biomarker boundaries must pair color with:
  1. Distinct physical icon shapes (Circle check, Triangle exclamation, Octagon stop).
  2. Unambiguous textual words (`"Low Risk"`, `"Moderate Risk"`, `"Elevated Risk"`).
  3. Directional symbols for SHAP values (`▲` for risk increase, `▼` for risk decrease).

---

## 7. Touch Target & Motion Ergonomics

### 7.1 Touch Target Sizing (WCAG 2.2 Success Criterion 2.5.8)
- Every interactive touch target on mobile viewports (buttons, tab items, dropdown triggers, checkboxes) must satisfy a minimum bounding box of **$44\times 44\text{px}$**.
- Adjacent touch targets must maintain at least **$8\text{px}$** of physical separation to prevent accidental taps.

### 7.2 Respect for `prefers-reduced-motion`
When reduced motion is enabled in user operating system preferences:
```css
@media (prefers-reduced-motion: reduce) {
  *, ::before, ::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```
All slide transitions, drawer animations, and loading shimmers collapse to instant or subtle opacity fades.
