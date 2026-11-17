# HeartXAI 2.0 — Frontend Project Structure & Organization

**Document ID:** `HX2-FE-002`  
**Version:** `1.0.0`  
**Phase:** Phase 6 — Frontend Engineering Architecture & Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal Frontend Architect & Lead Engineer  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011, HX2-DES-001–HX2-DES-016  

---

## 1. Overview & Architectural Pattern: "Feature-Sliced Modular Architecture"

The HeartXAI 2.0 frontend codebase is organized around a **Feature-Sliced Modular Architecture**. Rather than grouping code purely by technical role (e.g., throwing all components into a single massive `components/` folder and all hooks into a massive `hooks/` folder), domain logic is co-located within distinct, self-contained **Feature Modules**.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   FEATURE-SLICED PROJECT TOPOLOGY                      │
├────────────────────────────────────────────────────────────────────────┤
│ 1. src/app/          ── Application shell, router setup, global providers│
│ 2. src/components/   ── Global reusable UI primitives (design tokens)  │
│ 3. src/features/     ── Domain-driven feature slices (intake, SHAP)    │
│ 4. src/services/     ── Central API client & network transport layer   │
│ 5. src/types/        ── Global domain models & API response interfaces │
│ 6. src/utils/        ── Pure formatting, unit conversion, validators   │
│ 7. src/styles/       ── Tailwind directives, tokens.css, print styles  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Complete Directory Hierarchy Specification

```
frontend/
├── public/                          # Static public assets (unprocessed by bundler)
│   ├── favicon.ico
│   ├── manifest.json                # PWA manifest
│   ├── robots.txt
│   └── icons/                       # PWA icons (192x192, 512x512)
├── src/
│   ├── app/                         # Application bootstrapping & routing entrypoints
│   │   ├── App.tsx                  # Root component: Provider tree & route outlet
│   │   ├── router.tsx               # React Router configuration & route tree
│   │   └── providers.tsx            # Composition of QueryClient, Auth, Unit providers
│   │
│   ├── assets/                      # Bundled static assets
│   │   ├── anatomical/              # SVG cardiac diagrams (coronary arteries, chambers)
│   │   ├── branding/                # HeartXAI logos, logomarks, lockups
│   │   └── illustrations/           # Clean line-art illustrations (empty states, 404)
│   │
│   ├── components/                  # Cross-cutting, domain-agnostic UI library
│   │   ├── ui/                      # Atomic design system primitives
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Select.tsx
│   │   │   ├── Checkbox.tsx
│   │   │   ├── RadioCard.tsx
│   │   │   ├── Slider.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Table.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── DropdownMenu.tsx
│   │   │   ├── Tabs.tsx
│   │   │   └── Tooltip.tsx
│   │   ├── layout/                  # Shared page chrome & structural scaffolding
│   │   │   ├── AppHeader.tsx        # Top navigation with country & profile pills
│   │   │   ├── AppSidebar.tsx       # Collapsible left navigation bar
│   │   │   ├── MobileNav.tsx        # Mobile bottom navigation bar + slide-over drawer
│   │   │   ├── Breadcrumbs.tsx      # Contextual path trail
│   │   │   └── CountrySelectorModal.tsx # Global jurisdiction switcher modal
│   │   ├── feedback/                # User feedback & status communication
│   │   │   ├── AlertBanner.tsx      # Severity-tiered alerts (Emergency, Warn, Info)
│   │   │   ├── Toast.tsx            # Ephemeral notification toasts
│   │   │   ├── SkeletonLoader.tsx   # Accessible pulsing shimmer placeholders
│   │   │   └── EmptyState.tsx       # Zero-data guidance cards
│   │   └── clinical/                # Shared clinical & medical primitives
│   │       ├── BiomarkerInput.tsx   # Number input with bound unit badge & toggle
│   │       ├── UnitToggle.tsx       # mg/dL <-> mmol/L segmented toggle
│   │       ├── RiskBadge.tsx        # Calibrated risk strata pill with icon + label
│   │       └── EmergencyNotice.tsx  # Unmissable acute symptom intercept banner
│   │
│   ├── features/                    # Domain-driven feature slices
│   │   ├── authentication/          # User login, registration, password recovery
│   │   │   ├── components/          # LoginForm.tsx, RegisterForm.tsx, ConsentCheckbox.tsx
│   │   │   ├── hooks/               # useLogin.ts, useRegister.ts, useSession.ts
│   │   │   ├── services/            # authService.ts (login, logout, refresh, csrf)
│   │   │   └── types/               # auth.types.ts
│   │   │
│   │   ├── dashboard/               # Patient executive dashboard view
│   │   │   ├── components/          # RiskSummaryHero.tsx, VitalsSnapshotGrid.tsx, Sparkline.tsx
│   │   │   └── hooks/               # useDashboardSummary.ts
│   │   │
│   │   ├── assessments/             # Multi-step clinical assessment intake wizard
│   │   │   ├── components/          # WizardContainer.tsx, StepProgress.tsx,
│   │   │   │                        # Step1Demographics.tsx, Step2Vitals.tsx,
│   │   │   │                        # Step3Labs.tsx, Step4Ecg.tsx,
│   │   │   │                        # Step5Imaging.tsx, Step6Review.tsx
│   │   │   ├── hooks/               # useAssessmentWizard.ts, useSaveDraft.ts
│   │   │   ├── schemas/             # assessmentValidationSchema.ts (Zod)
│   │   │   └── services/            # assessmentService.ts
│   │   │
│   │   ├── predictions/             # Assessment result overview & risk calculation
│   │   │   ├── components/          # DualRiskGauge.tsx, RiskStrataMeter.tsx,
│   │   │   │                        # ClinicalSummaryNarrative.tsx
│   │   │   └── hooks/               # useAssessmentDetail.ts
│   │   │
│   │   ├── explainability/          # SHAP feature attribution visualizations
│   │   │   ├── components/          # ShapWaterfallChart.tsx, ShapTableFallback.tsx,
│   │   │   │                        # FeatureImpactTooltip.tsx
│   │   │   └── hooks/               # useShapExplanation.ts
│   │   │
│   │   ├── counterfactuals/         # "What-If" physiological scenario simulator
│   │   │   ├── components/          # ScenarioSimulator.tsx, ModifiableSliderList.tsx,
│   │   │   │                        # ScenarioDeltaComparison.tsx
│   │   │   └── hooks/               # useCounterfactualSimulation.ts
│   │   │
│   │   ├── history/                 # Longitudinal assessment logs & biomarker trends
│   │   │   ├── components/          # AssessmentHistoryTable.tsx, HistoryFilterToolbar.tsx,
│   │   │   │                        # BiomarkerTrendChart.tsx
│   │   │   └── hooks/               # useAssessmentHistory.ts, useBiomarkerTrends.ts
│   │   │
│   │   ├── doctors/                 # Country-configurable doctor directory
│   │   │   ├── components/          # DoctorSearchToolbar.tsx, DoctorCard.tsx,
│   │   │   │                        # VerificationBadge.tsx, DoctorDetailDrawer.tsx
│   │   │   └── hooks/               # useDoctorDirectory.ts
│   │   │
│   │   ├── hospitals/               # Country-configurable cardiac facility directory
│   │   │   ├── components/          # HospitalSearchToolbar.tsx, HospitalCard.tsx,
│   │   │   │                        # EmergencyHotlineButton.tsx
│   │   │   └── hooks/               # useHospitalDirectory.ts
│   │   │
│   │   ├── insurance/               # Country-specific health insurance guidance
│   │   │   ├── components/          # InsuranceGuideAccordion.tsx, ClaimChecklist.tsx
│   │   │   └── hooks/               # useInsuranceInfo.ts
│   │   │
│   │   ├── reports/                 # Clinical consultation summary PDF export
│   │   │   ├── components/          # ReportPreview.tsx, ReportExportOptions.tsx
│   │   │   └── services/            # reportExportService.ts
│   │   │
│   │   ├── profile/                 # Patient profile baselines & preference settings
│   │   │   ├── components/          # ProfileForm.tsx, UnitPreferenceSelector.tsx,
│   │   │   │                        # PrivacyAuditLog.tsx, ConsentRevocationModal.tsx
│   │   │   └── hooks/               # useUserProfile.ts
│   │   │
│   │   ├── education/               # Evidence-based cardiovascular library
│   │   │   ├── components/          # ArticleCard.tsx, CategoryFilter.tsx, ArticleReader.tsx
│   │   │   └── hooks/               # useEducationArticles.ts
│   │   │
│   │   └── administration/          # Administrative command center & model governance
│   │       ├── components/          # SystemTelemetryGrid.tsx, ClinicianReviewQueue.tsx,
│   │       │                        # ModelRegistryTable.tsx, DriftMonitorChart.tsx,
│   │       │                        # AuditLogViewer.tsx, CountryConfigForm.tsx
│   │       └── hooks/               # useAdminTelemetry.ts, useClinicianQueue.ts,
│   │                                # useModelRegistry.ts, useAuditLogs.ts
│   │
│   ├── context/                     # Global React Context providers
│   │   ├── AuthContext.tsx          # Current user session, role, and auth methods
│   │   ├── UnitContext.tsx          # Active biomarker measurement units & converter
│   │   ├── CountryContext.tsx       # Active geographic jurisdiction & adapter config
│   │   └── ThemeContext.tsx         # Dark / Light theme mode provider
│   │
│   ├── hooks/                       # Shared domain-agnostic custom React hooks
│   │   ├── useDebounce.ts           # Debounces search inputs & slider events
│   │   ├── useMediaQuery.ts         # Viewport breakpoint detection (mobile vs desktop)
│   │   ├── useFocusTrap.ts          # Accessible keyboard focus trap for modal overlays
│   │   └── useScrollLock.ts         # Locks document body scroll during dialog display
│   │
│   ├── lib/                         # Third-party library initializations & configurations
│   │   ├── queryClient.ts           # TanStack Query client configuration with defaults
│   │   └── formatters.ts            # ECMAScript Intl formatters for dates & currencies
│   │
│   ├── services/                    # Centralized network communications
│   │   └── api/
│   │       ├── client.ts            # Central Fetch/Ky wrapper with interceptors & CSRF
│   │       ├── endpoints.ts         # Constant mapping of all backend API paths
│   │       └── errors.ts            # Standardized API error normalization utilities
│   │
│   ├── types/                       # Shared TypeScript type definitions
│   │   ├── api.types.ts             # Generic API envelopes, pagination, error models
│   │   ├── assessment.types.ts      # Clinical features, assessment DTOs, risk schemas
│   │   ├── explainability.types.ts  # SHAP attribution arrays, counterfactual vectors
│   │   ├── user.types.ts            # User roles, permissions, profile baselines
│   │   └── country.types.ts         # Country adapter metadata & directory types
│   │
│   ├── config/                      # Environment variables & runtime constants
│   │   ├── env.ts                   # Type-safe parsed environment variables (Vite import.meta.env)
│   │   └── constants.ts             # Global constants (timeouts, default country, limits)
│   │
│   ├── styles/                      # Global stylesheets & design token declarations
│   │   ├── index.css                # Tailwind directives & core font imports
│   │   ├── tokens.css               # CSS custom properties (colors, typography, radii)
│   │   └── print.css                # Dedicated print stylesheet for PDF report exports
│   │
│   └── tests/                       # Global test setups, mocks, and fixtures
│       ├── setup.ts                 # Vitest setup file with Jest-DOM matchers
│       ├── test-utils.tsx           # Custom render method wrapping all providers
│       ├── mocks/                   # MSW (Mock Service Worker) handlers & fixtures
│       │   ├── handlers.ts          # Mock API endpoints matching backend contracts
│       │   └── server.ts            # Node-based MSW server for Vitest
│       └── e2e/                     # Playwright end-to-end integration tests
│           ├── auth.spec.ts
│           ├── assessment-wizard.spec.ts
│           └── shap-explainability.spec.ts
│
├── .env.example                     # Environment template (VITE_API_BASE_URL, etc.)
├── index.html                       # Single-page HTML shell with font preloads
├── package.json                     # NPM dependency manifest & build scripts
├── postcss.config.js                # PostCSS configuration for Tailwind & Autoprefixer
├── tailwind.config.js               # Tailwind configuration binding design tokens
├── tsconfig.json                    # Base TypeScript compiler options
├── tsconfig.node.json               # Node-specific TypeScript config for Vite
└── vite.config.ts                   # Vite build configuration with path aliases & chunking
```

---

## 3. Path Aliasing Conventions & Import Standards

To prevent fragile relative path traversing (`../../../../components/ui/Button`), the application configures clean TypeScript and Vite path aliases:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"],
      "@features/*": ["src/features/*"],
      "@hooks/*": ["src/hooks/*"],
      "@services/*": ["src/services/*"],
      "@types/*": ["src/types/*"],
      "@utils/*": ["src/utils/*"],
      "@config/*": ["src/config/*"],
      "@assets/*": ["src/assets/*"]
    }
  }
}
```

### Import Rules & Order
All files must enforce strict, consistent import group ordering via ESLint:
1. **External Libraries:** `react`, `react-router-dom`, `@tanstack/react-query`, `lucide-react`.
2. **Internal Core/Shared:** `@/app`, `@/components/ui/*`, `@/components/layout/*`.
3. **Feature-Internal Modules:** Local hooks, components, and schemas.
4. **Types & Interfaces:** `import type { ... } from '@/types/...'`.
5. **Styles:** Local CSS or token imports.

---

## 4. Barrel Export Policy (Index Files)

### 4.1 Allowed Barrel Exports
- **`components/ui/index.ts`:** Allowed for core, stable UI primitives (`Button`, `Input`, `Card`, `Badge`, `Modal`). This streamlines imports without performance penalty because Vite tree-shakes atomic components efficiently.
- **`types/index.ts`:** Allowed for consolidating public domain types.

### 4.2 Prohibited Barrel Exports
- **Feature Folders (`features/*`):** Prohibited from exposing global barrel exports that re-export an entire feature slice. This prevents accidental circular dependency loops between feature domains and avoids inflating production JavaScript bundle chunks.
