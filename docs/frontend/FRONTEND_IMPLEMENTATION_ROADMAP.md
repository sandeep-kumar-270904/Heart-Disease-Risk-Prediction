# HeartXAI 2.0 — Frontend Implementation Roadmap & Delivery Stages

**Document ID:** `HX2-FE-012`  
**Version:** `1.0.0`  
**Phase:** Phase 6 — Frontend Engineering Architecture & Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal Frontend Architect & Engineering Delivery Lead  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011  

---

## 1. Roadmap Architecture & Delivery Principles

This roadmap establishes the phased implementation sequence for building the **HeartXAI 2.0 Frontend**. 

To deliver high engineering velocity for an individual developer while guaranteeing production stability, the roadmap enforces **Two Cardinal Delivery Directives**:
1. **Vertical End-to-End Spine First:** Stages 1 through 8 implement a complete, functional patient assessment, ML inference, and SHAP explainability workflow before ancillary modules (directories, insurance, administration) are layered on.
2. **Strict Definition of Done (DoD) per Stage:** No stage is marked complete until all files are authored, unit/component tests pass with $\ge 85\%$ coverage, zero TypeScript errors exist, and WCAG 2.2 AA accessibility audits pass.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   12-STAGE FRONTEND DELIVERY PIPELINE                  │
├────────────────────────────────────────────────────────────────────────┤
│ [Stage 1: Setup] ──► [Stage 2: Tokens & UI] ──► [Stage 3: Layouts]     │
│                                                           │            │
│ [Stage 6: Intake] ◄── [Stage 5: Profile] ◄── [Stage 4: Auth]           │
│         │                                                              │
│         ▼                                                              │
│ [Stage 7: Results] ──► [Stage 8: SHAP & Scenarios] ──► [Stage 9: History]
│                                                                │       │
│ [Stage 12: QA & A11y] ◄── [Stage 11: Admin] ◄── [Stage 10: Directory]  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Delivery Stages

---

### Stage 01: Project Foundation, Tooling & Core Configuration
- **Scope & Features:** Initialize Vite React TypeScript project, strict compiler configuration, Tailwind CSS integration, ESLint & Prettier setups, Vitest harness setup, path aliases.
- **Dependencies:** `vite`, `react`, `react-dom`, `typescript`, `tailwindcss`, `vitest`, `clsx`, `tailwind-merge`.
- **Expected Files:**
  - `package.json`, `vite.config.ts`, `tsconfig.json`, `tailwind.config.js`, `postcss.config.js`
  - `src/config/env.ts`, `src/config/constants.ts`
  - `src/tests/setup.ts`, `src/tests/test-utils.tsx`
- **Acceptance Criteria & Tests:** `npm run build` succeeds without warnings; `npm run test` executes setup test; Path alias `@/*` resolves cleanly.
- **Definition of Done:** Zero TypeScript compilation errors, clean linting pass, Vitest operational.

---

### Stage 02: Design Tokens & Shared UI Primitives
- **Scope & Features:** CSS token system declaration (`tokens.css`), base typography and color bindings, Radix UI integration, atomic component primitives.
- **Dependencies:** `@radix-ui/react-dialog`, `@radix-ui/react-dropdown-menu`, `@radix-ui/react-tooltip`, `lucide-react`.
- **Expected Files:**
  - `src/styles/tokens.css`, `src/styles/index.css`
  - `src/components/ui/Button.tsx`, `Input.tsx`, `Badge.tsx`, `Card.tsx`, `Modal.tsx`, `Tabs.tsx`, `Spinner.tsx`
- **Acceptance Criteria & Tests:** RTL tests verifying Button variants, Modal focus trapping, and contrast audits via `vitest-axe`.
- **Definition of Done:** All primitives render with correct design token variables in both Light and Dark themes.

---

### Stage 03: Application Layouts, Navigation & Router Infrastructure
- **Scope & Features:** React Router configuration, nested layout containers, header with country pill, collapsible sidebar, mobile bottom navigation bar, breadcrumbs.
- **Dependencies:** `react-router-dom`, `@radix-ui/react-dropdown-menu`.
- **Expected Files:**
  - `src/app/router.tsx`, `src/app/App.tsx`, `src/app/providers.tsx`
  - `src/components/layout/AppHeader.tsx`, `AppSidebar.tsx`, `MobileNav.tsx`, `Breadcrumbs.tsx`, `CountrySelectorModal.tsx`
  - `src/layouts/PublicLayout.tsx`, `PatientLayout.tsx`, `AdminLayout.tsx`
- **Acceptance Criteria & Tests:** Route transitions render correct layouts; mobile navigation toggles drawer; country modal updates active country context.
- **Definition of Done:** Responsive navigation adapts smoothly between mobile ($<640\text{px}$) and desktop ($\ge 1024\text{px}$).

---

### Stage 04: Central API Client, Authentication & Route Guards
- **Scope & Features:** Ky API client instance with interceptors, CSRF injection, error normalization, `AuthContext`, login/register pages, protected `<AuthGuard />` and `<RoleGuard />`.
- **Dependencies:** `ky`, `zod`, `@hookform/resolvers`.
- **Expected Files:**
  - `src/services/api/client.ts`, `endpoints.ts`, `errors.ts`
  - `src/context/AuthContext.tsx`
  - `src/features/authentication/pages/LoginPage.tsx`, `RegisterPage.tsx`, `VerifyEmailPage.tsx`
  - `src/features/authentication/services/authService.ts`
- **Acceptance Criteria & Tests:** MSW-mocked login sets session in memory; 401 response triggers silent refresh; unauthorized routes redirect to login.
- **Definition of Done:** Auth flows covered by RTL integration tests with zero tokens in `localStorage`.

---

### Stage 05: Patient Health Profile & Unit Configuration
- **Scope & Features:** Demographic baseline management, measurement unit preference toggles ($\text{mg/dL} \leftrightarrow \text{mmol/L}$, $\text{cm/kg} \leftrightarrow \text{in/lbs}$), `UnitContext`, privacy consent management.
- **Dependencies:** `react-hook-form`, `zod`.
- **Expected Files:**
  - `src/context/UnitContext.tsx`, `src/utils/units.ts`
  - `src/features/profile/pages/ProfileSettingsPage.tsx`, `UnitSettingsPage.tsx`, `PrivacyConsentPage.tsx`
  - `src/components/clinical/UnitToggle.tsx`
- **Acceptance Criteria & Tests:** Unit conversion math verified via unit tests; toggling units recalculates inputs without precision loss.
- **Definition of Done:** Unit preferences persist to user profile and update all form inputs dynamically.

---

### Stage 06: Assessment Intake Wizard Workflow
- **Scope & Features:** 6-step clinical data intake wizard, bound biomarker inputs, physiological validation bounds, temporary draft encryption, emergency symptom intercepts.
- **Dependencies:** `react-hook-form`, `zod`, `@hookform/resolvers`.
- **Expected Files:**
  - `src/features/assessments/pages/AssessmentWizardPage.tsx`
  - `src/features/assessments/components/WizardStepProgress.tsx`, `Step1Demographics.tsx`, `Step2Vitals.tsx`, `Step3Laboratory.tsx`, `Step4Electrocardiogram.tsx`, `Step5Imaging.tsx`, `Step6Review.tsx`
  - `src/features/assessments/schemas/assessmentValidationSchema.ts`
  - `src/components/clinical/BiomarkerInput.tsx`, `EmergencyNotice.tsx`
- **Acceptance Criteria & Tests:** Acute symptom input triggers Crimson emergency banner; invalid inputs block step advance; Step 6 review card accurately summarizes all fields.
- **Definition of Done:** Full 6-step wizard tested end-to-end with MSW intercepting payload.

---

### Stage 07: Prediction Results & Dual Risk Gauge Display
- **Scope & Features:** Assessment overview page, calibrated horizontal segmented risk bar, 10-year population comparison benchmark, plain-language clinical narrative.
- **Dependencies:** `lucide-react`, TanStack Query.
- **Expected Files:**
  - `src/features/predictions/pages/AssessmentOverviewPage.tsx`
  - `src/features/predictions/components/DualRiskGauge.tsx`, `RiskStrataMeter.tsx`, `ClinicalSummaryNarrative.tsx`
  - `src/components/clinical/RiskBadge.tsx`
- **Acceptance Criteria & Tests:** Model output labeled strictly as *"Angiographic CAD Association Likelihood"*; mandatory educational disclaimer rendered; screen-reader accessible text present.
- **Definition of Done:** Results page renders with compliant contrast and passes axe-core a11y audit.

---

### Stage 08: Explainability (SHAP Waterfall) & Counterfactual Scenarios
- **Scope & Features:** Interactive SHAP waterfall chart (Crimson `▲` vs Blue `▼`), accessible tabular alternative, "What-If" counterfactual sliders with biological clamps and delta calculation.
- **Dependencies:** `@radix-ui/react-slider`, custom SVG primitives.
- **Expected Files:**
  - `src/features/explainability/pages/ShapExplainabilityPage.tsx`
  - `src/features/explainability/components/ShapWaterfallChart.tsx`, `ShapTableFallback.tsx`, `FeatureImpactTooltip.tsx`
  - `src/features/counterfactuals/pages/CounterfactualScenariosPage.tsx`
  - `src/features/counterfactuals/components/ScenarioSimulator.tsx`, `CounterfactualSlider.tsx`
- **Acceptance Criteria & Tests:** SHAP bars sort descending by absolute weight; slider movements update simulated risk delta; 1-click table view toggle replaces SVG.
- **Definition of Done:** Counterfactual sliders maintain 60fps interaction via `useDeferredValue`.

---

### Stage 09: Assessment History & Health Trends
- **Scope & Features:** Chronological assessment log table with mobile card transformation, multi-line longitudinal biomarker trend charts with shaded physiological reference bands.
- **Dependencies:** `recharts`.
- **Expected Files:**
  - `src/features/history/pages/AssessmentHistoryPage.tsx`, `HealthTrendsPage.tsx`
  - `src/features/history/components/AssessmentHistoryTable.tsx`, `HistoryFilterToolbar.tsx`, `BiomarkerTrendChart.tsx`
- **Acceptance Criteria & Tests:** Filtering by date/risk updates table; responsive view transforms table into cards below $768\text{px}$; trend chart distinguishes missing data from zero.
- **Definition of Done:** Table pagination, sorting, and multi-line chart rendering operational.

---

### Stage 10: Country-Configurable Directories & Insurance Guidance
- **Scope & Features:** Verified doctor directory search with license badges, hospital facility search with 24/7 cardiac emergency filter, country-specific insurance guidance.
- **Dependencies:** `@radix-ui/react-dialog`, `lucide-react`.
- **Expected Files:**
  - `src/features/doctors/pages/DoctorDirectoryPage.tsx`, `components/DoctorCard.tsx`, `DoctorDetailDrawer.tsx`
  - `src/features/hospitals/pages/HospitalDirectoryPage.tsx`, `components/HospitalCard.tsx`
  - `src/features/insurance/pages/InsuranceGuidePage.tsx`
- **Acceptance Criteria & Tests:** Active country context dynamically switches directory endpoints and emergency hotline numbers; doctor cards render verified badges.
- **Definition of Done:** Directories adapt seamlessly between India (`IN`), USA (`US`), and UK (`GB`) contexts.

---

### Stage 11: Administrative Command Center & Model Governance
- **Scope & Features:** System telemetry dashboard, clinician credential verification split-drawer, model registry and version promotion, algorithmic drift (PSI) monitoring, immutable audit log viewer.
- **Dependencies:** `recharts`, TanStack Query.
- **Expected Files:**
  - `src/features/administration/pages/AdminDashboardPage.tsx`, `ClinicianQueuePage.tsx`, `ModelRegistryPage.tsx`, `ModelDriftPage.tsx`, `SecurityAuditLogPage.tsx`, `CountryConfigPage.tsx`
  - `src/features/administration/components/SystemTelemetryGrid.tsx`, `ClinicianReviewQueue.tsx`, `AuditLogViewer.tsx`
- **Acceptance Criteria & Tests:** Non-admin accounts receive 403 Forbidden; split-drawer displays document zoom/rotate; model rollback triggers two-step confirmation.
- **Definition of Done:** High-density administrative workspaces verified for responsive scrolling.

---

### Stage 12: Comprehensive Accessibility, Responsive & Performance Sign-Off
- **Scope & Features:** Cross-browser Playwright E2E test suite execution, automated axe-core accessibility audit across all routes, bundle size budget verification, Lighthouse audit.
- **Dependencies:** `@playwright/test`, `axe-core`, `rollup-plugin-visualizer`.
- **Expected Deliverables:** Complete test execution logs, bundle visualizer map, accessibility compliance certificate.
- **Definition of Done:** $100\%$ passing tests, zero WCAG 2.2 AA violations, initial JS bundle $<130\text{ KB}$ gzipped.
