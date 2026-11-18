# FRONTEND APPLICATION SECURITY SPECIFICATION

**Document Reference:** `docs/security/FRONTEND_SECURITY_SPECIFICATION.md`  
**Phase:** 09 — Security, Privacy, Data Protection & Threat Modelling  
**Status:** Approved Technical Design  
**Author:** Frontend Security Specialist & Client Experience Architect  
**Traceability:** NFR-SEC-01, NFR-SEC-03, NFR-SEC-05, ADR-009, ADR-011  

---

## 1. Executive Summary & Web Vulnerability Stance

Single Page Applications (SPAs) built with React and TypeScript do not automatically protect against web application security vulnerabilities. Cross-Site Scripting (XSS), token theft via browser storage, prototype pollution, malicious dependency injection, and clickjacking remain severe risks in modern web applications.

Because HeartXAI 2.0 displays confidential medical risk assessments, clinical biomarkers, and physician directories, the frontend client enforces strict client-side defenses:
1. Complete elimination of authentication tokens from persistent browser storage (`localStorage` / `sessionStorage`).
2. Strict Content Security Policy (CSP Level 3).
3. Contextual sanitization of all rendered dynamic content via DOMPurify.
4. Client-side session timeout managers with automated memory purging on logout.
5. Strict prevention of sensitive health parameters in browser URLs and console telemetry.

---

## 2. Secure Token & Browser Storage Architecture

### 2.1 The Browser Storage Anti-Pattern
Storing JWTs or API keys in `localStorage` or `sessionStorage` exposes tokens to immediate exfiltration by any malicious script executed via XSS, compromised third-party npm packages, or malicious browser extensions.

### 2.2 Approved In-Memory + HttpOnly Storage Architecture
- **Access Token:** Held strictly within private React module state / Zustand memory (`authStore`). The token is never written to disk or browser web storage. If the user refreshes the page, the client silently calls `/api/v1/auth/refresh` to re-hydrate the in-memory token.
- **Refresh Token:** Handled exclusively by the browser's native cookie jar as an `HttpOnly`, `Secure`, `SameSite=Strict` cookie. JavaScript code has zero access to this cookie.
- **Permitted Browser Storage:** Only non-sensitive UI preferences (dark/light theme toggle, collapsed navigation state, selected language code) are permitted in `localStorage`.

---

## 3. Cross-Site Scripting (XSS) Prevention & Dynamic Rendering

While React's JSX syntax automatically escapes string values within text interpolations (`<div>{patientName}</div>`), dangerous injection vectors persist when handling URLs, dynamic HTML, or user-supplied markdown.

### 3.1 Strict Sanitization Standards
1. **Forbidden Primitives:** The use of `dangerouslySetInnerHTML` is prohibited across the codebase. Any pull request introducing `dangerouslySetInnerHTML` is rejected by ESLint security rules (`react/no-danger`).
2. **Medical Markdown & Rich Text:** Where clinical guidance or educational descriptions require formatted text, rendering must pass through a strict sanitization pipeline powered by `DOMPurify` with an explicit element whitelist:
   ```typescript
   import DOMPurify from "dompurify";

   export const sanitizeClinicalContent = (dirtyHtml: string): string => {
     return DOMPurify.sanitize(dirtyHtml, {
       ALLOWED_TAGS: ["b", "i", "em", "strong", "p", "ul", "ol", "li", "span"],
       ALLOWED_ATTR: ["class"],
       FORBID_TAGS: ["script", "iframe", "object", "embed", "link", "style"],
       FORBID_ATTR: ["onerror", "onload", "onclick", "onmouseover"]
     });
   };
   ```
3. **URL Sanitization:** Links to external medical resources or directory websites must validate schemes to prevent `javascript:` pseudoprotocol execution:
   ```typescript
   export const isSafeUrl = (url: string): boolean => {
     try {
       const parsed = new URL(url);
       return ["https:", "http:"].includes(parsed.protocol);
     } catch {
       return false;
     }
   };
   ```

---

## 4. Content Security Policy (CSP Level 3) & Security Headers

The production web server (Nginx) terminates TLS and injects strict security headers on every HTML delivery:

### 4.1 Production Content Security Policy
```http
Content-Security-Policy: 
  default-src 'none';
  script-src 'self';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https://assets.heartxai.org;
  font-src 'self';
  connect-src 'self' https://api.heartxai.org;
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
  object-src 'none';
  upgrade-insecure-requests;
```

### 4.2 Supporting Security Response Headers
- **X-Frame-Options:** `DENY` (prevents clickjacking by disabling iframe embedding).
- **X-Content-Type-Options:** `nosniff` (disables MIME-type sniffing).
- **Referrer-Policy:** `strict-origin-when-cross-origin` (prevents URL parameter leakage across cross-origin requests).
- **Permissions-Policy:** `camera=(), microphone=(), geolocation=(), payment=()` (disables unneeded browser hardware features).

---

## 5. Client Session Lifecycle & Automated Inactivity Timeouts

To protect patients who leave browsers open on shared or public workstations:
1. **Inactivity Timer:** The React client tracks user interaction events (`mousemove`, `keydown`, `touchstart`).
2. **Warning Modal:** After 10 minutes of inactivity, a warning dialog prompts the user with a 60-second countdown.
3. **Automated Logout & Memory Purge:** After 11 minutes of inactivity without response:
   - The client invokes `/api/v1/auth/logout` to invalidate the server-side refresh token.
   - All Zustand memory stores (`authStore`, `predictionStore`, `patientStore`) are explicitly reset to initial blank states.
   - The browser redirects to `/login?reason=timeout`.

---

## 6. Information Leakage Prevention in URLs and Browser Telemetry

1. **Zero Health Data in GET URLs:** Query parameters must never contain clinical biomarkers, prediction results, or patient names (`/predictions/view?bp=150` is strictly forbidden). Paths use random surrogate UUIDs or integers (`/predictions/42`).
2. **Console Telemetry Scrubbing:** In production builds, `console.log`, `console.debug`, and `console.info` statements are stripped via the Vite build pipeline (`terserOptions: { drop_console: true }`), preventing leakage of patient objects into browser developer tools.
3. **Crash Reporting Scrubbing:** When integrating client error monitoring (e.g. Sentry), a `beforeSend` hook scrubs all health metrics, passwords, and authorization tokens from breadcrumbs and error reports.
