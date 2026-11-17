# HeartXAI 2.0 — Frontend Engineering Architecture

**Document ID:** `HX2-FE-001`  
**Version:** `1.0.0`  
**Phase:** Phase 6 — Frontend Engineering Architecture & Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal Frontend Architect & Frontend Quality Lead  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011, HX2-DES-001–HX2-DES-016  

---

## 1. Executive Summary & Architectural Vision

The **HeartXAI 2.0 Frontend** is a modern, production-grade, type-safe Single-Page Application (SPA) designed to deliver explainable cardiovascular machine learning insights to patients, verified clinicians, and compliance administrators.

### 1.1 Architectural Axioms
1. **Clinical & Epistemological Reliability:** UI presentation must never overstate model capabilities. Predictions are strictly framed as *Angiographic CAD Association Likelihood (Educational Model)*, never diagnostic certainty.
2. **Deterministic Type Safety:** End-to-end type safety spanning backend OpenAPI 3.1 contracts, centralized API client responses, form validation schemas, and React component props with zero `any` types.
3. **Defense-in-Depth Security:** Frontend security enforces strict session hygiene via `HttpOnly`, `SameSite=Strict` cookies, automated CSRF header token attachment, memory-only session state restoration, and zero unencrypted health telemetry in browser persistent storage.
4. **Universal Accessibility (WCAG 2.2 AA):** Built on unstyled accessible primitives (Radix UI) ensuring complete keyboard navigability, semantic ARIA live regions, contrast ratios $\ge 4.5:1$ (and $\ge 7:1$ for errors), and compulsory tabular data alternatives for all data visualizations.
5. **Country-Configurable Foundation:** The application dynamically adapts its formatting, biomarker units ($\text{mg/dL} \leftrightarrow \text{mmol/L}$), directory registries, statutory notices, and emergency contacts based on an active country configuration without code rebuilds.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   HEARTXAI 2.0 FRONTEND ARCHITECTURE                   │
├────────────────────────────────────────────────────────────────────────┤
│                          PRESENTATION LAYER                            │
│  [ Pages / Route Views ] ──► [ Feature Containers ] ──► [ UI Primitives]│
│            │                          │                        │       │
│            ▼                          ▼                        ▼       │
│  [ Layout Guards ]         [ Form Controller (RHF) ]  [ Radix + Tailwind]
├────────────────────────────────────────────────────────────────────────┤
│                      STATE & DATA SYNCHRONIZATION                      │
│  [ Auth / Session Context ]  [ UI Context (Theme, Units, Country) ]    │
│  [ TanStack Query v5 (Server Cache, Polling, Optimistic Mutation) ]   │
├────────────────────────────────────────────────────────────────────────┤
│                       INFRASTRUCTURE & PROTOCOLS                       │
│  [ Central API Client (Fetch/Ky Wrapper + Interceptors + CSRF) ]       │
│  [ Runtime Schema Validation (Zod Contracts) ]                         │
│  [ ECMAScript Intl Formatters (Dates, Currencies, Biomarker Units) ]   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Frontend Technology Stack

| Technology Layer | Chosen Technology | Version | Justification & Architectural Role |
| :--- | :--- | :--- | :--- |
| **Core Framework** | **React** | `18.3.x` (or `19.0.x`) | Declarative component model, Concurrent features (`useTransition`, `useDeferredValue`), robust medical ecosystem support. |
| **Language** | **TypeScript** | `5.4+` | Enforces strict compile-time verification: `strict: true`, `noImplicitAny: true`, `exactOptionalPropertyTypes: true`. |
| **Build & Dev Tooling** | **Vite** | `5.2+` | Rollup-based production bundling, native ESM dev server, instant HMR ($<50\text{ms}$), optimized asset splitting. |
| **Styling Engine** | **Tailwind CSS** | `3.4+` | Utility-first CSS compiling against design tokens (`docs/design/DESIGN_TOKENS.md`) with zero runtime CSS overhead. |
| **Routing** | **React Router DOM** | `6.23+` | Declarative client-side routing, nested layouts, loader data boundaries, history manipulation, role guard wrappers. |
| **Server-State Sync** | **TanStack Query** | `v5.35+` | Declarative server cache, stale-while-revalidate, automatic query deduplication, retry backoff, mutation lifecycles. |
| **Client Session State**| **React Context + Hook** | Native | Light, dependency-free session state for authenticated user identity, role context, active country, and unit preference. |
| **Form Handling** | **React Hook Form** | `v7.51+` | Uncontrolled high-performance inputs, minimal re-renders, deep integration with custom unit toggles and sliders. |
| **Runtime Validation** | **Zod** | `v3.23+` | TypeScript-first schema declaration matching backend OpenAPI DTOs and validating form submissions before API dispatch. |
| **Component Primitives**| **Radix UI** | Latest | Headless, unstyled, bulletproof accessible primitives (Dialog, DropdownMenu, Tabs, Tooltip, Slider, Checkbox). |
| **Data Visualization** | **Recharts + Custom SVG** | `v2.12+` | Composable SVG charts for longitudinal trends, paired with custom accessible SVG primitives for SHAP waterfall plots. |
| **Iconography** | **Lucide React** | `0.370+` | Clean, 24px grid, 1.75px stroke medical and UI icons with complete tree-shaking support. |
| **Testing Harness** | **Vitest + RTL + Playwright** | Modern | Unit/hook testing via Vitest, component testing via React Testing Library, end-to-end integration via Playwright. |

---

## 3. Architectural Boundary & Separation of Concerns

To ensure maintainability by an individual developer while retaining enterprise quality, HeartXAI 2.0 enforces **Four Strict Architectural Layers**:

```
[ Layer 1: Route & Layout Layer ]
  - Defines URL endpoints, role guard redirects, public/patient/admin chrome layouts.
  - Zero business logic; responsible solely for routing, title injection, and error boundaries.
               │
               ▼
[ Layer 2: Feature & Container Layer ]
  - Encapsulates domain logic (e.g., `features/assessments`, `features/explainability`).
  - Orchestrates TanStack Query hooks, React Hook Form instances, and local workflow state.
               │
               ▼
[ Layer 3: Presentation UI Primitive Layer ]
  - Stateless, highly reusable atomic components (`components/ui/*`).
  - Governed strictly by design tokens, Tailwind utility classes, and Radix accessibility wrappers.
               │
               ▼
[ Layer 4: Infrastructure & Services Layer ]
  - Centralized API HTTP client (`services/api/client.ts`).
  - Data transfer schemas (`types/api/`), unit conversion math (`utils/units.ts`), and error normalizers.
```

### 3.1 Strict Dependency Direction Rules
1. **Inward Flow Only:** Higher layers may import from lower layers; lower layers **never** import from higher layers.
   - `components/ui/` must NEVER import from `features/` or `pages/`.
   - `services/` must NEVER import React components or UI state.
2. **Feature Isolation:** Features (`src/features/feature-name/`) must not reach into the internal implementation files of other features. Inter-feature communication occurs via shared hooks, routes, or generic components in `src/components/`.
3. **No Circular Imports:** Enforced at build time via ESLint `import/no-cycle` rule.

---

## 4. Design System Token Compilation Strategy

The design tokens specified in `docs/design/DESIGN_TOKENS.md` and `docs/design/TYPOGRAPHY_AND_COLOR_SYSTEM.md` compile directly into:
1. **CSS Custom Properties (`src/styles/tokens.css`):**
   - Declares primitive scales (`--color-slate-900`, `--color-sky-600`) and semantic aliases (`--surface-canvas`, `--text-primary`, `--status-error-text`) for `:root` (Light) and `.dark` (Dark).
2. **Tailwind CSS Configuration (`tailwind.config.js`):**
   - Extends the theme palette by referencing CSS variables:
   ```javascript
   colors: {
     surface: {
       canvas: 'var(--surface-canvas)',
       card: 'var(--surface-card)',
       subtle: 'var(--surface-card-subtle)',
     },
     text: {
       primary: 'var(--text-primary)',
       secondary: 'var(--text-secondary)',
       muted: 'var(--text-muted)',
     },
     interactive: {
       primary: 'var(--interactive-primary)',
       hover: 'var(--interactive-hover)',
       focus: 'var(--interactive-focus)',
     },
     status: {
       error: 'var(--status-error-text)',
       warn: 'var(--status-warn-text)',
       success: 'var(--status-success-text)',
     }
   }
   ```
This architecture guarantees that switching themes or altering color semantics occurs instantly via CSS variables without triggering React re-renders or stylesheet recompilations.

---

## 5. Medical Safety & Epistemological Guardrails

The frontend engineering architecture incorporates immutable guardrails that prevent accidental misrepresentation of model outputs:

1. **Non-Diagnostic Display Wrapper (`<ClinicalOutputWrapper />`):**
   - Automatically wraps all model risk probabilities and SHAP explanations.
   - Injects the mandatory legal and educational disclaimer banner directly into the DOM tree.
   - Intercepts and formats output labels: *"Angiographic CAD Association Likelihood"*, permanently blocking unapproved terms like *"Heart Attack Risk"* or *"Diagnostic Diagnosis"*.
2. **Unit Integrity Provider (`<UnitContext />`):**
   - Governs all quantitative laboratory and vital inputs (`Serum Cholesterol`, `Fasting Blood Sugar`, `Blood Pressure`).
   - Ensures numbers are never rendered without their active unit badge.
   - Automatically executes mathematically verified conversion factors ($1\text{ mmol/L} = 38.67\text{ mg/dL}$ for cholesterol) during toggle events.
3. **Emergency Intercept Boundary (`<EmergencyAlertBoundary />`):**
   - Continuously evaluates form inputs during the assessment intake wizard.
   - If severe resting chest pain is combined with hypertensive crisis measurements, it immediately renders an unmissable emergency assistance banner with localized click-to-call numbers (`112` / `102` / `911`).
