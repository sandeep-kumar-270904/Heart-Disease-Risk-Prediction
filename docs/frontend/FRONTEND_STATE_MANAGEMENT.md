# HeartXAI 2.0 — Frontend State Management Architecture

**Document ID:** `HX2-FE-006`  
**Version:** `1.0.0`  
**Phase:** Phase 6 — Frontend Engineering Architecture & Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal Frontend Architect & Senior React Engineer  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011, HX2-DES-003  

---

## 1. State Classification & Architectural Topology

State in **HeartXAI 2.0** is strictly categorized into **Five Distinct Tiers** based on persistence, ownership, and sensitivity. 

Global state bloat is prevented by ensuring that state is kept as local as possible, and server-originating data is never duplicated into client state stores.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   STATE CLASSIFICATION TOPOLOGY                        │
├───────────────────┬──────────────────────┬─────────────────────────────┤
│ STATE TIER        │ PRIMARY STORAGE      │ MANAGEMENT TOOL / HOOK      │
├───────────────────┼──────────────────────┼─────────────────────────────┤
│ 1. Server State   │ In-Memory QueryCache │ TanStack Query v5           │
│ 2. Auth State     │ In-Memory Context    │ React Context (AuthContext) │
│ 3. UI State       │ Component / URL / DOM│ React useState / URL Params │
│ 4. Form State     │ Input Ref Tree       │ React Hook Form v7          │
│ 5. Workflow State │ Session / Draft      │ In-Memory Context / Encrypt │
└───────────────────┴──────────────────────┴─────────────────────────────┘
```

---

## 2. Server State Management: TanStack Query v5

### 2.1 Query Cache Architecture & Key Hierarchy
All remote API data (assessments, SHAP vectors, trends, doctor directories) is managed exclusively by **TanStack Query**. 

To ensure deterministic caching and invalidation, query keys follow a strict hierarchical tuple pattern:

```typescript
export const queryKeys = {
  // Assessment domains
  assessments: {
    all: ['assessments'] as const,
    lists: () => [...queryKeys.assessments.all, 'list'] as const,
    list: (params: AssessmentQueryParams) => [...queryKeys.assessments.lists(), params] as const,
    details: () => [...queryKeys.assessments.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.assessments.details(), id] as const,
    explainability: (id: string) => [...queryKeys.assessments.detail(id), 'explainability'] as const,
    trends: (range: string) => [...queryKeys.assessments.all, 'trends', range] as const,
  },

  // Directory domains (country-scoped)
  directory: {
    all: ['directory'] as const,
    doctors: (country: string, filters: DoctorFilterParams) => 
      [...queryKeys.directory.all, 'doctors', country, filters] as const,
    hospitals: (country: string, filters: HospitalFilterParams) => 
      [...queryKeys.directory.all, 'hospitals', country, filters] as const,
  },

  // Admin & Model Governance
  admin: {
    telemetry: () => ['admin', 'telemetry'] as const,
    verifications: () => ['admin', 'verifications'] as const,
    models: () => ['admin', 'models'] as const,
    auditLogs: (filters: AuditFilterParams) => ['admin', 'audit-logs', filters] as const,
  }
};
```

### 2.2 Cache Lifecycles & Stale Times
- **Static / Metadata Queries (Model version info, Educational articles, Country adapters):**
  - `staleTime: 1000 * 60 * 30` (30 minutes).
  - `gcTime: 1000 * 60 * 60` (60 minutes).
- **Patient Clinical Telemetry (Assessment detail, SHAP waterfall, Trends):**
  - `staleTime: 1000 * 60 * 5` (5 minutes).
  - Assessment detail is essentially immutable once computed.
- **Directories (Doctors, Hospitals):**
  - `staleTime: 1000 * 60 * 10` (10 minutes).
- **Admin System Telemetry:**
  - `staleTime: 1000 * 15` (15 seconds, with optional background polling).

### 2.3 Mutation Lifecycles & Invalidation Rules
When an assessment is submitted via `useSubmitAssessment`:
```typescript
export const useSubmitAssessment = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: AssessmentInputDto) => assessmentService.submit(data),
    onSuccess: (newAssessment) => {
      // 1. Invalidate historical lists
      queryClient.invalidateQueries({ queryKey: queryKeys.assessments.lists() });
      // 2. Invalidate longitudinal trends
      queryClient.invalidateQueries({ queryKey: queryKeys.assessments.all });
      // 3. Pre-seed the detail cache with returned assessment
      queryClient.setQueryData(
        queryKeys.assessments.detail(newAssessment.id), 
        newAssessment
      );
    },
    onError: (error: ApiErrorResponse) => {
      // Handled via localized toast or form error boundary
    }
  });
};
```

---

## 3. Authentication & Session State

### 3.1 Memory-Only Session Principle
To prevent Cross-Site Scripting (XSS) tokens theft:
- Authentication tokens (`access_token`, `refresh_token`) **reside strictly in HttpOnly, SameSite=Strict cookies managed by the browser**.
- The frontend holds **only the decoded user profile object** in React memory (`AuthContext`):
```typescript
export interface AuthState {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}
```
- No JWTs, refresh tokens, or cryptographic session secrets are ever stored in `window.localStorage` or `window.sessionStorage`.

### 3.2 Session Restoration Flow
1. On initial application load (`App.tsx`), `AuthContext` executes a lightweight session probe: `GET /api/v1/auth/me`.
2. The browser automatically attaches the `HttpOnly` cookie.
3. If valid (`HTTP 200`), user profile (`id`, `role`, `name`, `email`) is set into state; `isAuthenticated = true`.
4. If invalid or expired (`HTTP 401`), state is set to `user = null`; `isAuthenticated = false`.

---

## 4. UI & Ephemeral Interaction State

### 4.1 URL as Primary Source of Truth for Filtering & Pagination
To ensure deep-linking, browser history navigation (`Back`/`Forward`), and bookmarking work seamlessly:
- Search filters (e.g., Doctor city, specialty).
- Pagination (`page=2&limit=10`).
- Date ranges (`range=6M`).
- Active tab selection (`tab=explainability`).
Are managed via **React Router search parameters** (`useSearchParams`), not isolated local React state.

### 4.2 Local Component State
Reserved strictly for localized, ephemeral interactions:
- Dropdown menu open/closed state.
- Modal dialog visibility.
- Mobile drawer toggle.
- Tabular row expansion for clinical telemetry notes.

---

## 5. Form State: React Hook Form

Forms throughout HeartXAI 2.0 (Intake Wizard, Profile, Settings) are managed via **React Hook Form**:
- **Uncontrolled Architecture:** Form values are held directly in the DOM input nodes and subscribed via refs.
- **Zero Keystroke Lag:** Typing into blood pressure or cholesterol inputs triggers zero parent container re-renders.
- **Runtime Schema Validation:** Zod schemas validate field states on `onBlur` and form submission.

---

## 6. Temporary Workflow State & Sensitive Data Handling

### 6.1 Multi-Step Assessment Draft Preservation
During the 6-step clinical assessment wizard, a patient may accidentally refresh the page or step away.
- **In-Memory Draft Store:** The active wizard state is maintained in a local React context during the session.
- **Volatile Storage Safeguard:** If draft persistence is enabled by the patient, the partial inputs are encrypted client-side using a transient Web Crypto key before saving to `sessionStorage` (which self-destructs when the tab is closed).
- **Prohibition:** Unencrypted clinical biomarkers (blood sugar, ST depression, cholesterol) **must never be stored in persistent `localStorage`**.
- **Explicit Purge:** Once the assessment is submitted to the backend, all local session draft keys are immediately wiped.
