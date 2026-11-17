# HeartXAI 2.0 — Frontend Engineering Acceptance Criteria

**Document ID:** `HX2-FE-013`  
**Version:** `1.0.0`  
**Phase:** Phase 6 — Frontend Engineering Architecture & Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal Frontend Architect & Quality Lead  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011, HX2-DES-015  

---

## 1. Overview & Verification Policy

This document defines the **binding, measurable acceptance criteria** required for signing off the frontend implementation of **HeartXAI 2.0**. 

Prior to production merge or deployment, the application must satisfy 100% of the criteria across all eleven engineering categories detailed below.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   FRONTEND ACCEPTANCE AUDIT DOMAINS                    │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Architecture & Clean Code         │ 7. Clinical Workflows & Safety  │
│ 2. Type Safety & Zero Any Policy     │ 8. Accessibility (WCAG 2.2 AA)  │
│ 3. Routing & Route Guards            │ 9. Responsive & Mobile UX       │
│ 4. State Management & Server Cache   │ 10. Performance & Bundle Budget │
│ 5. API Integration & Error Handling  │ 11. Test Coverage & Automation  │
│ 6. Authentication & Security         │                                 │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Binding Engineering Acceptance Checklist

### 1. Architecture & Code Organization
- [ ] **Feature-Sliced Hierarchy:** Code is organized strictly by feature slices under `src/features/`; generic primitives reside in `src/components/ui/`.
- [ ] **Dependency Direction:** Lower-level modules never import from higher-level features or pages.
- [ ] **No Circular Imports:** Verified via ESLint `import/no-cycle` with zero warnings.
- [ ] **Path Aliasing:** 100% of internal imports utilize configured path aliases (`@/*`, `@components/*`, `@features/*`).

### 2. Type Safety & Zero-Any Policy
- [ ] **Strict Compiler Mode:** `tsconfig.json` enforces `strict: true`, `noImplicitAny: true`, and `exactOptionalPropertyTypes: true`.
- [ ] **Zero `any` Types:** Zero explicit or inferred `any` types exist across the entire codebase (`@typescript-eslint/no-explicit-any` enforced as error).
- [ ] **OpenAPI Contract Alignment:** All API request payloads and response contracts match FastAPI Pydantic schemas.

### 3. Routing & Navigation
- [ ] **Full Route Coverage:** 100% of routes defined in `FRONTEND_ROUTE_SPECIFICATION.md` are implemented and resolve to valid views.
- [ ] **Role Protection:** Navigating to `/admin/*` without an `ADMINISTRATOR` role renders `/403 Forbidden` without flickering administrative chrome.
- [ ] **Deep-Link Restoration:** Logging in with a `?redirect=/patient/assessments/1042` query parameter restores the user directly to the deep-linked page.
- [ ] **No Dead Ends:** Every sub-page contains an accessible breadcrumb trail and working back-navigation control.

### 4. State Management & Cache Discipline
- [ ] **No Global Server State Duplication:** Server state is managed exclusively by TanStack Query; no remote API data is duplicated into Redux, Zustand, or global Context.
- [ ] **Deterministic Query Invalidation:** Submitting an assessment invalidates assessment lists and trends caches automatically.
- [ ] **Zero Sensitive Storage:** No unencrypted clinical biomarkers or diagnostic histories linger in `window.localStorage`.

### 5. API Integration & Network Protocols
- [ ] **Central Client Exclusivity:** All HTTP calls route through `src/services/api/client.ts`; zero native `fetch()` calls exist in React components.
- [ ] **Automatic CSRF Protection:** Double-submit CSRF cookie token is automatically read and attached to `X-CSRF-Token` headers for all `POST`/`PUT`/`DELETE` requests.
- [ ] **Graceful Timeout & Retry:** Idempotent `GET` requests retry up to 2 times with exponential backoff; timeouts trigger standardized `ApiError` notifications.
- [ ] **Request Cancellation:** `AbortController` signals cancel pending network requests when a user navigates away or switches tabs.

### 6. Authentication & Frontend Security
- [ ] **HttpOnly Cookie Handling:** Session tokens are stored exclusively in `HttpOnly`, `SameSite=Strict` cookies.
- [ ] **XSS Elimination:** Zero uses of `dangerouslySetInnerHTML` without strict DOMPurify sanitization.
- [ ] **Cache-Control & Meta Tags:** Sensitive patient views include `<meta name="robots" content="noindex, nofollow">`.
- [ ] **Cache Purge on Logout:** Signing out executes `queryClient.clear()` and completely clears all patient data from browser memory.

### 7. Clinical Workflows & Epistemological Safety
- [ ] **Non-Diagnostic Framing:** Model output is labeled strictly as *"Angiographic CAD Association Likelihood (Educational Model)"*. The terms *"Diagnosis"*, *"Diagnostic Guarantee"*, or *"Prescription"* never appear in model output cards.
- [ ] **Educational Disclaimer:** A permanent educational disclaimer is visibly rendered inside the assessment result hero card.
- [ ] **SHAP Causal Protection:** Feature attribution charts explicitly display footnotes clarifying that weights are mathematical tree contributions, not biological disease causes.
- [ ] **Emergency Intercept:** Entering resting chest pain combined with severe hypertensive readings triggers an unmissable Crimson Emergency Banner with a click-to-call hotline button (`tel:112` / `tel:911`).
- [ ] **Compulsory Unit Binding:** Every displayed biomarker includes an anchored physical unit badge; unit toggling ($\text{mg/dL} \leftrightarrow \text{mmol/L}$) executes mathematically verified conversions.

### 8. Accessibility (WCAG 2.2 Level AA Standard)
- [ ] **Contrast Compliance:** All text satisfies $\ge 4.5:1$ contrast against background surfaces ($\ge 7:1$ for error states); UI borders satisfy $\ge 3:1$.
- [ ] **Keyboard Navigability:** 100% of interactive controls are operable via keyboard (`Tab`, `Enter`, `Space`, Arrows).
- [ ] **Visible Focus Rings:** `:focus-visible` renders high-contrast `2px solid var(--interactive-focus)` ring with `2px` offset.
- [ ] **Multi-Sensory Alerts:** Risk strata, warnings, and errors never rely on color alone; they always include an icon, a text label, and a numeric percentage range.
- [ ] **Accessible Chart Fallbacks:** Every visual SVG chart (Risk Gauge, SHAP Waterfall, Trend Chart) is paired with a 1-click toggle to an accessible HTML data table.
- [ ] **Reduced Motion Support:** Enabling `@media (prefers-reduced-motion: reduce)` disables non-essential animations and transitions.

### 9. Responsive & Mobile Ergonomics
- [ ] **Zero Horizontal Overflow:** Viewports from $320\text{px}$ to $2560\text{px}$ exhibit zero horizontal page scrollbars.
- [ ] **Mobile Navigation:** On screens $<640\text{px}$, persistent bottom navigation bar provides 1-thumb access to core workspaces.
- [ ] **Responsive Table Handling:** Dense tables transform into stacked summary cards or provide smooth horizontal swiping with pinned headers on mobile.
- [ ] **Touch Target Size:** Interactive touch targets measure at least $44\times 44\text{px}$ on touchscreens.

### 10. Performance & Production Budgets
- [ ] **Initial JS Bundle Budget:** Total initial entry point JavaScript bundle measures **$< 130\text{ KB}$ gzipped**.
- [ ] **Initial CSS Bundle Budget:** Compiled Tailwind stylesheet measures **$< 20\text{ KB}$ gzipped**.
- [ ] **Core Web Vitals:** $\text{LCP} < 1.8\text{s}$, $\text{INP} < 100\text{ms}$, $\text{CLS} < 0.05$ on mobile 4G throttling.
- [ ] **Code-Splitting Verification:** Heavy charting libraries (`recharts`) are lazy-loaded only when accessing visualization routes.

### 11. Test Coverage & Automation
- [ ] **Unit & Component Tests:** Vitest test suite achieves $\ge 85\%$ line and branch coverage across utilities, schemas, and clinical UI components.
- [ ] **Zero a11y Violations:** Automated `axe-core` tests report zero WCAG 2.2 AA violations on all rendered views.
- [ ] **End-to-End Test Suite:** Playwright tests pass 100% across Chromium, Firefox, and WebKit for patient assessment, SHAP explainability, and admin verification flows.
