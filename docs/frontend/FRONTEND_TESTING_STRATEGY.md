# HeartXAI 2.0 — Frontend Testing Strategy & Quality Assurance Plan

**Document ID:** `HX2-FE-010`  
**Version:** `1.0.0`  
**Phase:** Phase 6 — Frontend Engineering Architecture & Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Frontend Quality Lead & Senior Test Automation Architect  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011, HX2-DES-012, HX2-DES-015  

---

## 1. Quality Assurance Philosophy: "The Testing Pyramid for Healthcare SPAs"

Because HeartXAI 2.0 handles critical clinical calculations and explainability outputs, frontend code is subject to **Five Strict Testing Tiers**.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        TESTING PYRAMID LAYERS                          │
├────────────────────────────────────────────────────────────────────────┤
│ 1. End-to-End (E2E) Tests   ── Playwright (Full browser user flows)    │
│ 2. Accessibility (a11y)     ── vitest-axe + Playwright-axe (WCAG 2.2)  │
│ 3. Integration Tests        ── RTL + MSW (Feature slices & API mocks)  │
│ 4. Component Tests          ── RTL + user-event (UI primitives & ARIA) │
│ 5. Unit Tests               ── Vitest (Unit converters, Zod schemas)   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Testing Tooling Selection & Justification

| Testing Domain | Selected Tool | Version | Justification |
| :--- | :--- | :--- | :--- |
| **Unit & Test Runner** | **Vitest** | `^1.5.0` | Shares Vite's native configuration, ESM loader, and TypeScript transpiler; execution is up to $10\times$ faster than Jest. |
| **Component Testing** | **React Testing Library** | `^15.0.5` | Enforces user-centric testing querying by accessible role (`getByRole('button')`) rather than fragile implementation selectors. |
| **User Interaction** | **@testing-library/user-event** | `^14.5.2` | Simulates realistic browser events (keyboard focus, typing delays, tab traversal, mouse clicks). |
| **API Mocking** | **MSW (Mock Service Worker)** | `^2.2.14` | Intercepts HTTP calls at the browser/Node network layer, ensuring exact request/response envelope fidelity. |
| **Automated a11y** | **vitest-axe** | `^0.1.0` | Audits rendered DOM trees against WCAG 2.2 AA rules during unit/component test execution. |
| **E2E Automation** | **Playwright** | `^1.43.1` | Fast, headless multi-browser automation (Chromium, Firefox, WebKit) with built-in tracing, video capture, and mobile viewport emulation. |

---

## 3. Detailed Test Plans by Clinical Domain

### 3.1 Domain 1: Unit Conversion & Input Validation (`utils/` & `schemas/`)
- **Unit Converter Tests (`test_units.spec.ts`):**
  - Verify cholesterol conversion: $200\text{ mg/dL} \leftrightarrow 5.17\text{ mmol/L}$ within $\pm 0.01$ rounding precision.
  - Verify fasting glucose conversion: $100\text{ mg/dL} \leftrightarrow 5.55\text{ mmol/L}$.
  - Verify boundary clamping: rejects negative numbers, zero BP, and physiologically impossible values ($> 400\text{ mmHg}$).
- **Zod Validation Schema Tests (`test_assessment_schema.spec.ts`):**
  - Asserts valid clinical vector passes validation.
  - Asserts omission of required vitals triggers specific field errors (`"trestbps is required"`).
  - Asserts systolic BP $\le$ diastolic BP triggers cross-field validation failure.

### 3.2 Domain 2: Foundation & Clinical UI Components
- **`<BiomarkerInput />` Component Test:**
  - Renders label, bound unit badge, and helper text.
  - Clicking unit toggle updates unit badge and displays converted value.
  - Renders `aria-invalid="true"` when error prop is present.
- **`<RiskGaugeCard />` Component Test:**
  - Renders CAD likelihood percentage and strata badge.
  - Asserts presence of permanent educational disclaimer banner.
  - Asserts screen-reader `<div className="sr-only">` contains full risk description.
- **`<ShapWaterfallChart />` Component Test:**
  - Asserts zero-baseline is drawn.
  - Verifies positive impact bars render Crimson and negative bars render Blue.
  - Clicking `[Switch to Accessible Data Table]` unmounts SVG and mounts semantic HTML table.

### 3.3 Domain 3: Multi-Step Assessment Intake Workflow
- **Integration Test with MSW (`test_assessment_wizard.spec.tsx`):**
  - Step 1: Enters demographics; asserts `[Continue]` advances to Step 2.
  - Step 2: Enters blood pressure ($154/86$) and heart rate ($168$).
  - Step 3: Enters cholesterol in `mmol/L` ($6.33$); verifies backend payload receives normalized `mg/dL` ($245$).
  - Step 6: Review screen checks mandatory non-diagnostic consent checkbox; submits form.
  - Asserts MSW captures `POST /api/v1/assessments` with correct payload structure.
  - Verifies navigation to `/patient/assessments/:newId`.

### 3.4 Domain 4: Acute Symptom & Emergency Intercept
- **Emergency Intercept Test:**
  - Patient selects `Typical Angina` and enters `Resting BP Systolic: 195 mmHg`.
  - Asserts Crimson Emergency Banner immediately appears in DOM with `role="alert"`.
  - Verifies emergency call button link points to active country hotline (`tel:112` or `tel:911`).

### 3.5 Domain 5: Counterfactual Scenarios Simulator
- **Integration Test (`test_counterfactual_scenarios.spec.tsx`):**
  - Loads baseline assessment ($42\%$ likelihood).
  - Simulates dragging Systolic BP slider from $154\text{ mmHg}$ down to $125\text{ mmHg}$.
  - Verifies simulated likelihood recalculates ($28\%$) and delta badge renders `▼ -14%`.
  - Verifies biological non-modifiable factors (Age, Sex) have disabled sliders with padlock icons.
  - Clicking `[Reset All]` restores baseline values instantly.

### 3.6 Domain 6: Accessibility (WCAG 2.2 AA) & Keyboard Traversal
- **Automated Axe Audits:**
  - Every page view is audited via `expect(await axe(container)).toHaveNoViolations()`.
- **Keyboard Traversal Test:**
  - Tab navigation cycles smoothly from skip link through header, sidebar, main content, and form inputs.
  - Modal dialog traps keyboard focus; `Tab` does not escape to background DOM; `Escape` key closes dialog.

---

## 4. End-to-End (E2E) Test Suite Specification (Playwright)

### 4.1 Master E2E Test Scenarios
1. **`e2e/auth-journey.spec.ts`:**
   - User signs up $\rightarrow$ verifies email $\rightarrow$ logs in $\rightarrow$ arrives at dashboard $\rightarrow$ signs out $\rightarrow$ verifies session cookie removal and cache purge.
2. **`e2e/assessment-flow.spec.ts`:**
   - Patient opens wizard $\rightarrow$ completes 6 steps $\rightarrow$ views Dual Risk Gauge $\rightarrow$ inspects SHAP waterfall $\rightarrow$ tests counterfactual sliders $\rightarrow$ exports clinical PDF.
3. **`e2e/admin-governance.spec.ts`:**
   - Admin logs in $\rightarrow$ navigates to `/admin/verifications` $\rightarrow$ inspects clinician license PDF in split drawer $\rightarrow$ approves verification badge $\rightarrow$ verifies immutable audit log entry.
4. **`e2e/responsive-mobile.spec.ts`:**
   - Emulates iPhone 15 ($393\times 852\text{px}$) $\rightarrow$ verifies bottom navigation bar $\rightarrow$ completes single-column assessment intake $\rightarrow$ verifies table card transformations.
