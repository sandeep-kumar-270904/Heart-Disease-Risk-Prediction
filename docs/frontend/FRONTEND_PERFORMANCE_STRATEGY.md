# HeartXAI 2.0 — Frontend Performance & Optimization Strategy

**Document ID:** `HX2-FE-011`  
**Version:** `1.0.0`  
**Phase:** Phase 6 — Frontend Engineering Architecture & Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal Frontend Architect & Performance Engineer  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011  

---

## 1. Performance Philosophy & Core Web Vitals Targets

In healthcare technology, performance is directly linked to patient safety and trust. A sluggish assessment form or lagging counterfactual slider introduces user error, frustrates anxious patients, and degrades clinical usability on low-bandwidth mobile networks.

HeartXAI 2.0 enforces strict **Core Web Vitals Thresholds** across all viewports:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      CORE WEB VITALS TARGETS                           │
├───────────────────────────────────┬────────────────────────────────────┤
│ METRIC                            │ TARGET THRESHOLD (95th Percentile) │
├───────────────────────────────────┼────────────────────────────────────┤
│ Largest Contentful Paint (LCP)    │ < 1.8 seconds (Good)               │
│ Interaction to Next Paint (INP)   │ < 100 milliseconds (Good)          │
│ Cumulative Layout Shift (CLS)     │ < 0.05 (Near Zero Shift)           │
│ First Contentful Paint (FCP)      │ < 1.0 second                       │
│ Time to Interactive (TTI)         │ < 2.2 seconds                      │
└───────────────────────────────────┴────────────────────────────────────┘
```

---

## 2. Production Bundle Size Budgets

To ensure instant loading on mobile cellular networks (3G/4G), the frontend enforces strict bundle budgets validated in Continuous Integration:

| Bundle Asset | Maximum Uncompressed Size | Maximum Gzipped / Brotli Budget |
| :--- | :--- | :--- |
| **Initial Entry Point Chunk (`index.js`)** | $< 400\text{ KB}$ | **$< 130\text{ KB}$** |
| **Compiled Global Stylesheet (`index.css`)**| $< 90\text{ KB}$ | **$< 20\text{ KB}$** |
| **Patient Assessment Chunk (Async)** | $< 180\text{ KB}$ | **$< 50\text{ KB}$** |
| **Data Visualization Chunk (`recharts.js`)**| $< 220\text{ KB}$ | **$< 65\text{ KB}$** |
| **Admin Workspace Chunk (Async)** | $< 250\text{ KB}$ | **$< 75\text{ KB}$** |

---

## 3. Code-Splitting & Rollup Chunking Strategy (`vite.config.ts`)

HeartXAI 2.0 uses fine-grained code-splitting via Rollup `manualChunks` to prevent vendor bloat from slowing initial route rendering:

```typescript
// vite.config.ts snippet
export default defineConfig({
  build: {
    target: 'es2022',
    cssCodeSplit: true,
    sourcemap: false,
    chunkSizeWarningLimit: 500,
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // Vendor chunk: Core React runtime
          if (id.includes('node_modules/react') || id.includes('node_modules/react-dom') || id.includes('node_modules/react-router-dom')) {
            return 'vendor-react';
          }
          // Vendor chunk: Data fetching & validation
          if (id.includes('node_modules/@tanstack') || id.includes('node_modules/zod') || id.includes('node_modules/ky')) {
            return 'vendor-data';
          }
          // Vendor chunk: Heavy charting (lazy-loaded only on results/history routes)
          if (id.includes('node_modules/recharts') || id.includes('node_modules/d3-')) {
            return 'vendor-charts';
          }
          // Vendor chunk: Accessible UI primitives
          if (id.includes('node_modules/@radix-ui') || id.includes('node_modules/lucide-react')) {
            return 'vendor-ui';
          }
        },
      },
    },
  },
});
```

---

## 4. Route-Level Lazy Loading

Every major application view is loaded dynamically using `React.lazy` and wrapped in a `<Suspense />` boundary with an accessible skeleton fallback:

```tsx
// src/app/router.tsx
const PatientDashboard = React.lazy(() => import('@/features/dashboard/pages/PatientDashboardPage'));
const AssessmentWizard = React.lazy(() => import('@/features/assessments/pages/AssessmentWizardPage'));
const AssessmentResults = React.lazy(() => import('@/features/predictions/pages/AssessmentOverviewPage'));
const ShapExplainability = React.lazy(() => import('@/features/explainability/pages/ShapExplainabilityPage'));
const CounterfactualScenarios = React.lazy(() => import('@/features/counterfactuals/pages/CounterfactualScenariosPage'));
const AdminDashboard = React.lazy(() => import('@/features/administration/pages/AdminDashboardPage'));
```

* **Outcome:** An unauthenticated visitor landing on `/` downloads **zero** charting code, zero assessment wizard code, and zero administrative modules, keeping the public landing page initial download under $100\text{ KB}$ gzipped.

---

## 5. Runtime Rendering & Interaction Optimizations

### 5.1 Uncontrolled Form Architecture (Zero-Lag Typing)
By standardizing on **React Hook Form**, inputs bypass the React virtual DOM reconciler during typing. Keystrokes inside systolic blood pressure or cholesterol fields update the native DOM element instantly without triggering parent component re-renders.

### 5.2 Concurrent Rendering for "What-If" Counterfactual Sliders
When a user drags a counterfactual slider (e.g., simulating cholesterol from $245$ to $180\text{ mg/dL}$), React's `useDeferredValue` is utilized to decouple slider movement from model calculation:
```typescript
const [sliderValue, setSliderValue] = useState(baselineValue);
const deferredValue = useDeferredValue(sliderValue);

// Slider thumb tracks finger/mouse at 60fps without hitching
// Model calculation updates cooperatively when the main thread is idle
useEffect(() => {
  recalculateCounterfactual(deferredValue);
}, [deferredValue]);
```

### 5.3 Font Preloading & Cumulative Layout Shift (CLS) Prevention
- Fonts (`Inter` and `JetBrains Mono`) are self-hosted in `public/fonts/` (no external Google Fonts network hops).
- Preloaded in `index.html` via `<link rel="preload" as="font" type="font/woff2" crossorigin>`.
- Standardized `font-display: optional` or `swap` with matched font-fallback metrics (`size-adjust`, `ascent-override`), eliminating layout shifts during font swap (guaranteeing $\text{CLS} < 0.05$).

---

## 6. Automated Performance Monitoring & Bundle Auditing

1. **Continuous Bundle Analysis:** Built-in `rollup-plugin-visualizer` generates an interactive bundle map during every production build (`npm run build`). Pull requests that increase total bundle size by $> 5\%$ fail CI checks automatically.
2. **Real-User Monitoring (RUM):** Configured via `@sentry/browser` with Core Web Vitals tracking. Captures real-world LCP, INP, and CLS across actual patient devices and triggers alerting if P95 INP exceeds $150\text{ms}$.
