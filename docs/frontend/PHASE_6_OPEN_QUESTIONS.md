# HeartXAI 2.0 — Phase 6 Frontend Open Decisions & Questions

**Document ID:** `HX2-FE-014`  
**Version:** `1.0.0`  
**Phase:** Phase 6 — Frontend Engineering Architecture & Implementation Plan  
**Status:** Catalog of Open Engineering Decisions  
**Author:** Principal Frontend Architect & Lead Engineer  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011  

---

## 1. Overview

While the frontend engineering architecture, project structure, route specifications, component contracts, and testing strategies have been formally specified in `docs/frontend/`, five technical decisions remain open for final architectural ratification prior to beginning implementation.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   PHASE 6 OPEN TECHNICAL DECISIONS                     │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Core Framework: React 18.3 vs React 19.0 Production Target         │
│ 2. Clinical PDF Generation: Backend REST API vs Client-Side React-PDF  │
│ 3. PWA Service Worker Scope & Offline Fallback Depth                   │
│ 4. Mock Service Worker (MSW) Usage in Standalone Demo Mode             │
│ 5. Multi-Language i18n Chunk Bundling Strategy                         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Open Technical Decisions & Trade-Off Analyses

### Decision 01: Core Framework Version Target (React 18.3 vs React 19.0)
- **Context:** React 19 introduces native Actions, `useActionState`, and asset preloading, but ecosystem libraries (`recharts`, `@testing-library/react`) have varying compatibility statuses.
- **Option A (Recommended): React 18.3.1 Target**
  - *Pros:* 100% stable compatibility with Radix UI, Recharts 2.12, and React Testing Library; zero runtime warnings.
  - *Cons:* Misses out on new React 19 experimental hook syntax (though `useTransition` and `useDeferredValue` are fully supported in React 18).
- **Option B: React 19.0 Target**
  - *Cons:* Potential peer-dependency conflicts with older visualization libraries requiring `--legacy-peer-deps`.
- **Status:** *Architecture Recommendation: Adopt Option A (React 18.3.1), with a clean upgrade path to React 19 once all UI dependencies release formal React 19 peer-dependency updates.*

---

### Decision 02: Clinical Consultation PDF Generation Architecture
- **Context:** Patients require a clean, one-page printable PDF summary of their assessment and SHAP features to bring to their doctor's consultation.
- **Option A (Recommended): Backend REST Generation via Headless Engine**
  - *Architecture:* The frontend calls `GET /api/v1/reports/assessments/:id/pdf`. The backend FastAPI service compiles the report using a server-side template (e.g., Weasyprint or headless Chromium) and streams the PDF binary.
  - *Pros:* High typographic consistency, identical output across all patient devices, smaller frontend JavaScript bundle (saves $> 150\text{ KB}$ client-side).
- **Option B: Client-Side PDF Generation via `@react-pdf/renderer` or `jspdf`**
  - *Cons:* Inflates frontend bundle size by $> 180\text{ KB}$; browser font-rendering inconsistencies between iOS Safari and Windows Chrome.
- **Status:** *Approved Architecture Recommendation: Option A.*

---

### Decision 03: Progressive Web App (PWA) Offline Scope
- **Context:** How much functionality should the Service Worker cache for offline scenarios?
- **Option A (Recommended): Cache App Shell, Emergency Hotlines & Recent Assessment Detail**
  - *Behavior:* ServiceWorker caches CSS/JS chunks, `/emergency`, `/patient/directory/hospitals` for the active country, and the latest assessment summary in IndexedDB.
  - *Security:* Full historical records and sensitive health profiles are excluded from unencrypted offline storage.
- **Option B: Full Offline Intake Wizard with Background Sync**
  - *Cons:* Complex conflict resolution when user is offline; delayed model inference confuses users who expect instant risk scores.
- **Status:** *Architecture Recommendation: Adopt Option A.*

---

### Decision 04: Mock Service Worker (MSW) in Standalone Demo Mode
- **Context:** Should MSW be configured solely for unit/integration tests, or should it also support an in-browser standalone demonstration mode (for reviewing the UI without a live backend)?
- **Option A (Recommended): Dual Mode (Test Harness + Opt-in Demo Mode)**
  - *Behavior:* MSW is active by default in Vitest (`test/mocks/server.ts`). An optional environment variable `VITE_ENABLE_MOCK_API=true` enables `test/mocks/browser.ts` in Vite dev server for offline UI design reviews.
  - *Guardrail:* The production build script (`vite build`) hard-fails if `VITE_ENABLE_MOCK_API` is set to `true`, preventing mock data from ever deploying to production.
- **Option B: Tests Only**
  - *Cons:* Frontend development requires running the local FastAPI backend and PostgreSQL database simultaneously at all times.
- **Status:** *Approved Architecture Recommendation: Option A.*

---

### Decision 05: Multi-Language i18n Translation Chunking
- **Context:** Supporting English (`en`), Hindi (`hi`), Spanish (`es`), and German (`de`).
- **Option A (Recommended): Dynamic Asynchronous JSON Namespaces**
  - *Architecture:* When the user switches language, the frontend fetches only the requested language JSON chunk (`/locales/hi/assessment.json`) via dynamic `import()`.
  - *Pros:* Initial bundle only includes default English; zero wasted bandwidth for unused languages.
- **Option B: Monolithic Static Language Bundle**
  - *Cons:* Bundles all translation dictionaries into the main application chunk.
- **Status:** *Approved Architecture Recommendation: Option A.*
