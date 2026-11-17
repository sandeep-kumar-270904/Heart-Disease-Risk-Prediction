# HeartXAI 2.0 — Frontend Route Specification & Security Guards

**Document ID:** `HX2-FE-004`  
**Version:** `1.0.0`  
**Phase:** Phase 6 — Frontend Engineering Architecture & Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal Frontend Architect & Security Reviewer  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011, HX2-DES-006, HX2-DES-007  

---

## 1. Routing Architecture & Guard Hierarchy

The HeartXAI 2.0 routing system is implemented using **React Router DOM v6** data routers (`createBrowserRouter`). Routing incorporates nested layout wrappers, declarative code-splitting via `React.lazy`, and layered route protection guards.

### 1.1 Non-Negotiable Security Principle
> **FRONTEND ROUTE GUARDS NEVER REPLACE BACKEND AUTHORIZATION.**  
> Frontend route guards exist purely to optimize user experience, prevent jarring unauthorized page flashes, and guide users to appropriate authentication or upgrade paths. Every backend API endpoint strictly verifies session validity, user identity, active role scopes, and clinical consent grants independently.

```
                              [ Incoming URL Request ]
                                         │
                                         ▼
                             ┌───────────────────────┐
                             │    Root Router Tree   │
                             └───────────┬───────────┘
                                         │
         ┌───────────────────┬───────────┴───────────┬───────────────────┐
         ▼                   ▼                       ▼                   ▼
  [ Public Routes ]   [ Auth Routes ]       [ Protected Routes ]   [ System / Error ]
  - Landing, About    - Login, Register     - Wrapped in Guard     - 404 Not Found
  - Methodology       - Forgot Password     - Session Verified     - 500 Error
  - Education         - Unauth Layout       - Role Verified        - Offline Fallback
                                                     │
                                   ┌─────────────────┴─────────────────┐
                                   ▼                                   ▼
                         [ Patient Experience ]              [ Admin Experience ]
                         - Requires: PATIENT                 - Requires: ADMIN
                         - Layout: PatientLayout             - Layout: AdminLayout
```

---

## 2. Complete Application Route Inventory Table

### 2.1 Public & Educational Routes (Access: All / Unauthenticated)

| Path | Page Component | Layout | Data Dependencies | Loading Behavior | Error Behavior |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/` | `LandingPage` | `PublicLayout` | None | Instant static render | Page Error Boundary |
| `/about` | `AboutPage` | `PublicLayout` | None | Instant static render | Page Error Boundary |
| `/how-it-works` | `HowItWorksPage` | `PublicLayout` | None | Instant static render | Page Error Boundary |
| `/methodology` | `MethodologyPage`| `PublicLayout` | `useModelMetadata()` | Header skeleton | Retry alert banner |
| `/education` | `EducationLibraryPage`| `PublicLayout` | `useEducationArticles()` | 6-card grid skeleton | Empty state / Retry |
| `/education/:slug` | `ArticleDetailPage`| `PublicLayout` | `useArticleDetail(slug)` | Article text skeleton | 404 if slug invalid |
| `/safety-and-privacy`| `SafetyPage` | `PublicLayout` | None | Instant static render | Page Error Boundary |
| `/emergency` | `EmergencyHotlinePage`| `PublicLayout`| `useCountryEmergency(country)`| Critical hotline badge | Static emergency fallback |

---

### 2.2 Authentication Routes (Access: Guest Only / Redirect if Authenticated)

| Path | Page Component | Layout | Data Dependencies | Loading Behavior | Error Behavior |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/auth/login` | `LoginPage` | `AuthLayout` | None | Form button spinner | Inline error alert |
| `/auth/register` | `RegisterPage` | `AuthLayout` | None | Form button spinner | Inline validation alerts |
| `/auth/verify-email`| `VerifyEmailPage`| `AuthLayout` | `useVerifyEmailToken()` | Full-screen spinner | Expired token error card |
| `/auth/forgot-password`| `ForgotPasswordPage`| `AuthLayout`| None | Form button spinner | Inline error alert |
| `/auth/reset-password`| `ResetPasswordPage`| `AuthLayout`| None | Form button spinner | Token invalid redirect |

---

### 2.3 Patient Experience Routes (Access: Role `PATIENT`)

| Path | Page Component | Layout | Data Dependencies | Loading Behavior | Error Behavior |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/patient/dashboard` | `PatientDashboardPage`| `PatientLayout`| `useDashboardSummary()`, `useRecentVitals()` | KPI grid + hero skeletons | Inline retry banner |
| `/patient/assessments/new`| `AssessmentWizardPage`| `PatientLayout`| `useAssessmentDraft()`, `useActiveModelInfo()` | Step form skeleton | Save draft recovery |
| `/patient/assessments` | `AssessmentHistoryPage`| `PatientLayout`| `useAssessmentHistory(params)` | Table row skeletons | Empty history state |
| `/patient/assessments/:id`| `AssessmentOverviewPage`| `PatientLayout`| `useAssessmentDetail(id)` | Dual risk gauge skeleton | 404 / Unauthorized card |
| `/patient/assessments/:id/explainability`| `ShapExplainabilityPage`| `PatientLayout`| `useShapAttribution(id)` | Waterfall chart skeleton | Accessible fallback table |
| `/patient/assessments/:id/scenarios`| `CounterfactualScenariosPage`| `PatientLayout`| `useAssessmentDetail(id)` | Sliders + card skeleton | Reset to baseline |
| `/patient/trends` | `HealthTrendsPage` | `PatientLayout`| `useBiomarkerTrends(range)` | Multi-line chart skeleton | Missing telemetry notice |
| `/patient/directory/doctors`| `DoctorDirectoryPage`| `PatientLayout`| `useDoctorDirectory(country, filters)` | Card list skeleton | Empty directory state |
| `/patient/directory/hospitals`| `HospitalDirectoryPage`| `PatientLayout`| `useHospitalDirectory(country, filters)`| Facility card skeleton | Empty directory state |
| `/patient/insurance` | `InsuranceGuidePage` | `PatientLayout`| `useInsuranceGuidance(country)` | Accordion skeleton | Fallback generic guide |
| `/patient/reports/export`| `ReportExportPage` | `PatientLayout`| `useAssessmentDetail(id)` | Document preview skeleton| Export retry toast |
| `/patient/settings/profile`| `ProfileSettingsPage`| `PatientLayout`| `useUserProfile()` | Form inputs skeleton | Inline field errors |
| `/patient/settings/units`| `UnitSettingsPage` | `PatientLayout`| `useUnitPreferences()` | Radio card skeleton | Save confirmation toast |
| `/patient/settings/privacy`| `PrivacyConsentPage`| `PatientLayout`| `useConsentAuditTrail()` | Table log skeleton | Revoke confirm modal |

---

### 2.4 Clinician Experience Routes (Access: Role `CLINICIAN` with Active Verification)

| Path | Page Component | Layout | Data Dependencies | Loading Behavior | Error Behavior |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/clinician/dashboard` | `ClinicianDashboardPage`| `ClinicianLayout`| `useAssignedCohort()`, `usePendingReviews()` | Cohort table skeleton | Retry error alert |
| `/clinician/patients` | `PatientRegistryPage` | `ClinicianLayout`| `usePatientCohortList(filters)` | Table row skeletons | Empty patient state |
| `/clinician/patients/:id`| `PatientChartPage` | `ClinicianLayout`| `usePatientChart(id)` | Clinical chart skeleton | Unauthorized access |
| `/clinician/patients/:id/assessments/:assessId`| `ClinicalAuditPage`| `ClinicianLayout`| `useClinicalAssessmentAudit(assessId)`| Telemetry matrix skeleton| Audit failure toast |
| `/clinician/profile` | `ClinicianProfilePage`| `ClinicianLayout`| `useClinicianProfile()` | Verification badge status | Upload retry banner |

---

### 2.5 Administrator Experience Routes (Access: Role `ADMINISTRATOR`)

| Path | Page Component | Layout | Data Dependencies | Loading Behavior | Error Behavior |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/admin/dashboard` | `AdminDashboardPage` | `AdminLayout` | `useSystemHealthTelemetry()` | 4-card metric skeleton | Critical telemetry alert |
| `/admin/users` | `UserGovernancePage` | `AdminLayout` | `useUserDirectory(params)` | High-density table skeleton | Action failure toast |
| `/admin/verifications`| `ClinicianQueuePage` | `AdminLayout` | `useClinicianVerificationQueue()` | Split-pane review skeleton | Empty queue state |
| `/admin/models/registry`| `ModelRegistryPage` | `AdminLayout` | `useModelRegistryList()` | Model card skeleton | Rollback error modal |
| `/admin/models/drift` | `ModelDriftPage` | `AdminLayout` | `useModelDriftMetrics(modelId)` | PSI curve skeleton | Missing data alert |
| `/admin/audit-logs` | `SecurityAuditLogPage`| `AdminLayout` | `useSecurityAuditLogs(filters)` | Table row skeletons | Log query error alert |
| `/admin/country-config`| `CountryConfigPage` | `AdminLayout` | `useCountryConfigurationList()` | Adapter status skeleton | Config save error |

---

### 2.6 Error & System Routes (Access: All)

| Path | Page Component | Layout | Recovery Action Trigger |
| :--- | :--- | :--- | :--- |
| `/403` | `ForbiddenPage` | `MinimalLayout` | `"Switch Role"`, `"Return to Home"` |
| `/404` | `NotFoundPage` | `MinimalLayout` | `"Return to Dashboard"`, `"Browse Health Library"` |
| `/500` | `ServerErrorPage` | `MinimalLayout` | `"Reload Page"`, `"Report Issue"` (with unique correlation error ID) |
| `/offline` | `OfflineFallbackPage`| `MinimalLayout` | Cached emergency contacts & local assessment review |
| `*` (Catch-All) | `NotFoundRedirect` | None | Evaluates URL, checks deep-link validity, renders 404 |

---

## 3. Guard Implementation & Access Handlers

### 3.1 Authentication Guard (`<AuthGuard />`)
Wraps all private routes.
- **Verification Sequence:**
  1. Checks `AuthContext.isAuthenticated`.
  2. If session is loading (`AuthContext.isLoading`), renders full-page accessible skeleton with `aria-busy="true"`.
  3. If unauthenticated, captures the attempted target URL (`location.pathname + location.search`) and redirects to:
     ```
     /auth/login?redirect=${encodeURIComponent(targetPath)}
     ```
  4. Upon successful login, the application restores the user directly to the deep-linked target.

### 3.2 Role & Permission Guard (`<RoleGuard />`)
Wraps specific domain workspaces (`/patient/*`, `/clinician/*`, `/admin/*`).
- **Authorization Sequence:**
  1. Evaluates user's verified role (`user.role`).
  2. If the user role does not match the route's allowed roles:
     - Logged to security telemetry (unauthorized route navigation attempt).
     - Renders `/403 Forbidden` view explaining the exact required permission scope.
     - Never leaks existence of administrative endpoints to unauthorized accounts.

### 3.3 Session Expiry & Token Renewal Interceptor
- When a backend request returns `HTTP 401 Unauthorized` during active user navigation:
  1. The API client attempts a single silent token refresh via `/api/v1/auth/refresh`.
  2. If the refresh request succeeds, the failed request is re-dispatched seamlessly without user disruption.
  3. If the refresh fails (session revoked or expired beyond window):
     - Clears in-memory session state.
     - Sets an ephemeral notification flag in session storage: `session_expired=true`.
     - Redirects user to `/auth/login` displaying an informative warning banner: *"Your session expired due to inactivity. Please sign in again to resume your work."*
