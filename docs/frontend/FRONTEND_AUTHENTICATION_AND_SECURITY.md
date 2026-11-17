# HeartXAI 2.0 — Frontend Authentication & Security Specification

**Document ID:** `HX2-FE-008`  
**Version:** `1.0.0`  
**Phase:** Phase 6 — Frontend Engineering Architecture & Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal Frontend Architect & Cybersecurity Reviewer  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011, HXAI-ARCH-012  

---

## 1. Security Architecture & Threat Model Overview

Because HeartXAI 2.0 processes sensitive cardiovascular health telemetry, clinical biomarkers, and physician credentials, frontend security adheres to the principle of **Zero Trust Frontend Architecture**.

### 1.1 Non-Negotiable Frontend Security Tenets
1. **No Tokens in LocalStorage:** Long-lived JWTs, access tokens, and refresh tokens **must never** be stored in `localStorage` or `sessionStorage`. All tokens reside in secure, `HttpOnly`, `SameSite=Strict` cookies inaccessible to JavaScript execution contexts.
2. **Defensive Authorization:** Frontend role checks (`user.role === 'ADMINISTRATOR'`) exist solely to control visual navigation and improve UX. The backend FastAPI service independently enforces cryptographically signed token verification and Role-Based Access Control (RBAC) on every single API request.
3. **Defense Against Client-Side Data Leakage:** Sensitive health indicators and assessment vectors are cleared from memory upon sign-out and are never rendered into browser URLs or cached in browser history states.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   AUTHENTICATION & SESSION TOPOLOGY                    │
├────────────────────────────────────────────────────────────────────────┤
│ Client Browser (SPA)               Server (FastAPI Gateway)            │
│       │                                       │                        │
│       ├── POST /api/v1/auth/login ───────────►│ (Validates Password)   │
│       │   { email, password }                 │                        │
│       │                                       │                        │
│       │◄── Set-Cookie: access_token; HttpOnly ┼ (Secure, Strict, s-age)│
│       │    Set-Cookie: csrf_token; SameSite   │                        │
│       │    { user: { id, role, name } }       │                        │
│       │                                       │                        │
│       ├── GET /api/v1/assessments ───────────►│ (Cookie auto-attached) │
│       │   Header: X-CSRF-Token                │ (Validates RBAC & CSRF)│
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Authentication Workflows & Session Lifecycles

### 2.1 Registration Workflow
1. User navigates to `/auth/register`.
2. Completes registration form: *Full Legal Name*, *Email Address*, *Password* (minimum 12 characters, requiring uppercase, lowercase, number, and special character), *Country Selection*, and *Mandatory Terms & Non-Diagnostic Consent Checkbox*.
3. Client executes Zod schema validation before dispatch.
4. Dispatches `POST /api/v1/auth/register`.
5. Upon `HTTP 201 Created`:
   - Renders confirmation view: *"Verification link sent. Please verify your email address to complete registration."*
   - Directs user to `/auth/verify-email`.

### 2.2 Login Workflow
1. User enters credentials at `/auth/login`.
2. Dispatches `POST /api/v1/auth/login`.
3. Backend responds with `HTTP 200 OK` and sets:
   - `access_token` (HttpOnly, Secure, SameSite=Strict, Path=/, Max-Age=900 [15 mins]).
   - `refresh_token` (HttpOnly, Secure, SameSite=Strict, Path=/api/v1/auth/refresh, Max-Age=604800 [7 days]).
   - `csrf_token` (Readable cookie, Secure, SameSite=Strict).
   - Response body: `{ user: { id, email, role, fullName, countryCode } }`.
4. Frontend `AuthContext` receives the `user` object in memory and sets `isAuthenticated = true`.
5. Navigates to the captured redirect URL (or `/patient/dashboard` by default).

### 2.3 Logout & Cache Purge Workflow
1. User clicks `[Sign Out]` in header or drawer.
2. Dispatches `POST /api/v1/auth/logout`.
3. Backend clears all session cookies (`Set-Cookie: access_token=; Max-Age=0`).
4. Frontend executes **Immediate Memory & Cache Purge**:
   - `queryClient.clear()` (Wipes all cached assessments, patient vitals, and trends from memory).
   - `AuthContext.reset()` (Sets `user = null`, `isAuthenticated = false`).
   - Clears any temporary draft session state from `sessionStorage`.
5. Redirects immediately to `/auth/login`.

---

## 3. Frontend Threat Mitigation Matrix

| Security Threat | Attack Vector / Scenario | Frontend Countermeasure & Enforcement Rule |
| :--- | :--- | :--- |
| **Cross-Site Scripting (XSS)** | Malicious third-party script or injected SVG payload reads tokens from browser storage. | **Zero local storage tokens.** All tokens reside in `HttpOnly` cookies. React's JSX automatically escapes string outputs. React innerHTML (`dangerouslySetInnerHTML`) is banned via ESLint rules. Content Security Policy (CSP) headers block inline scripts. |
| **Cross-Site Request Forgery (CSRF)** | Malicious external site tricks patient's browser into submitting an assessment or changing settings. | **Double-Submit CSRF Cookie Pattern.** Backend sets `csrf_token` cookie; frontend API client reads this cookie and injects it into `X-CSRF-Token` header. SameSite=Strict cookies prevent cross-site dispatch. |
| **Unsafe Open Redirects** | Attacker crafts `/auth/login?redirect=https://evil.com` to steal credentials or redirect post-login. | **Strict Redirect Validation:** The `redirect` parameter is validated against an allowlist of internal relative paths. If URL starts with `//` or contains an external protocol (`http:`, `https:`), it is rejected and coerced to `/patient/dashboard`. |
| **Accidental Health Data Exposure** | Patient leaves computer unlocked; browser history or cache reveals confidential lab markers. | **No PII in URLs:** Vitals and biomarker values are strictly sent in POST/PUT request bodies, never query parameters. Assessment screens set `<meta name="robots" content="noindex, nofollow">`. Cache-Control `no-store` headers enforced on API responses. |
| **Clickjacking** | Application embedded in an invisible malicious iframe. | Backend returns `X-Frame-Options: DENY` and CSP `frame-ancestors 'none'`. |
| **Session Fixation** | Attacker sets a pre-existing session identifier. | Backend regenerates session identifiers upon every successful login; frontend verifies fresh CSRF token. |

---

## 4. Role-Aware Navigation & Authorization Verification

### 4.1 Client-Side Permission Evaluation
To maintain visual clarity, UI navigation dynamically adapts to the authenticated user's role:

```typescript
export const hasPermission = (
  user: UserProfile | null, 
  requiredRole: 'PATIENT' | 'CLINICIAN' | 'ADMINISTRATOR'
): boolean => {
  if (!user) return false;
  if (user.role === 'ADMINISTRATOR') return true; // Superuser scope
  return user.role === requiredRole;
};
```

### 4.2 Prohibited Practices
- **NEVER** hide a button as the sole protection for an administrative action (e.g., hiding `[Rollback Model]`). The backend API endpoint **must and does** enforce authorization decorators (`@require_role("ADMINISTRATOR")`).
- **NEVER** trust client-supplied role parameters in form bodies. The backend extracts identity and role strictly from the cryptographically verified JWT inside the `HttpOnly` cookie.
