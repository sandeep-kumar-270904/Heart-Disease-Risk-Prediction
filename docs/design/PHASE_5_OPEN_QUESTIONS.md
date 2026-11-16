# HeartXAI 2.0 — Phase 5 Design Open Questions & Decisions

**Document ID:** `HX2-DES-016`  
**Version:** `2.0.0`  
**Status:** `Catalog of Open Decisions`  
**Author:** Principal Product Designer & Engineering Quality Lead  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011  

---

## 1. Overview

While the design tokens, component specifications, information architecture, healthcare safety guardrails, and accessibility standards have been comprehensively defined in `docs/design/`, several technical and implementation decisions remain open for final product and engineering ratification prior to starting frontend implementation.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   PHASE 5 OPEN DECISION CATEGORIES                     │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Icon Library Standard (Lucide React vs Phosphor Icons)              │
│ 2. Default Theme Policy (Light Mode Default vs System Preference)      │
│ 3. Frontend Data Visualization Library (Recharts vs Tremor vs Visx)    │
│ 4. Progressive Web App (PWA) Offline Telemetry Scope                   │
│ 5. Multi-Language i18n Strategy & Translation Management               │
│ 6. Clinician Consultation Booking: Deep Integration vs Outbound Link   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Open Questions & Trade-Off Analyses

### Decision 01: Icon Library Standard Selection
- **Context:** The design system mandates a 24×24px bounding box with a 1.75px–2px stroke and rounded terminals.
- **Option A (Recommended): `lucide-react`**
  - *Pros:* Tree-shakeable, 1,400+ icons, excellent coverage of medical and health symbols (`HeartPulse`, `Activity`, `Stethoscope`, `Pill`, `FileSpreadsheet`), active community, zero runtime bloat.
  - *Cons:* Slightly generic tech feel if uncustomized.
- **Option B: `phosphor-react`**
  - *Pros:* Multiple weight variants (thin, light, regular, bold, fill, duotone).
  - *Cons:* Heavier package size, less specific clinical telemetry iconography.
- **Status:** *Pending Product Lead Ratification (Recommend Option A).*

---

### Decision 02: Default Theme Policy (Light Mode vs System Auto)
- **Context:** Medical and laboratory software traditionally defaults to clean light surfaces for maximum daylight readability, while developers and technical users prefer dark mode.
- **Option A (Recommended): System Auto with Explicit Persistent User Toggle**
  - *Behavior:* Defaults to OS preference (`prefers-color-scheme: dark/light`). If user toggles manually, choice is saved to local storage and user profile.
  - *Pros:* Respects individual patient eye comfort and battery savings on OLED mobile devices.
- **Option B: Light Mode Default for All Authenticated Clinical Sessions**
  - *Behavior:* All clinical charting views default strictly to Light Mode (`#FFFFFF` surface, `#0F172A` text) to mirror standard hospital EMR environments.
- **Status:** *Pending Design Lead Ratification (Recommend Option A).*

---

### Decision 03: Frontend Charting & Visualization Library
- **Context:** Visualizations include the Calibrated Risk Strata Meter, SHAP Waterfall Attribution, Longitudinal Biomarker Trends, and Counterfactual Comparative Bars.
- **Option A (Recommended): `recharts` + Custom SVG Primitives**
  - *Pros:* Native React SVG rendering, highly accessible via DOM node inspection, excellent responsive resizing, zero canvas rendering lag.
  - *Cons:* Customizing complex SHAP waterfall geometries requires custom SVG bar components.
- **Option B: `visx` (Airbnb Open Source)**
  - *Pros:* Total low-level mathematical control over SVG shapes, d3-scale integration.
  - *Cons:* Steeper learning curve, slower initial implementation velocity for an individual developer.
- **Status:** *Pending Frontend Architecture Approval (Recommend Option A).*

---

### Decision 04: Progressive Web App (PWA) Offline Telemetry Scope
- **Context:** Patients traveling in areas with spotty connectivity may need to view recent assessment summaries or access emergency hotlines.
- **Option A (Recommended): Cache Emergency Directory & Last Assessment Overview Only**
  - *Scope:* ServiceWorker caches `/emergency`, `/patient/directory/hospitals` (local country), and the most recent assessment summary JSON in IndexedDB.
  - *Security:* Full historical records and sensitive health profiles are never stored unencrypted in offline caches.
- **Option B: Full Offline Assessment Intake with Background Sync**
  - *Scope:* Allows patient to fill out new assessment offline; synchronizes and computes ML risk once internet is restored.
  - *Risk:* Complex draft conflict resolution and delayed model feedback.
- **Status:** *Pending Security & Architecture Approval (Recommend Option A).*

---

### Decision 05: Multi-Language i18n Strategy
- **Context:** The platform is country-configurable. Phase 1 will support English (`en`), with immediate roadmap expansion to Hindi (`hi`), Spanish (`es`), and German (`de`).
- **Option A (Recommended): `next-intl` / `i18next` with Static JSON Namespaces**
  - *Architecture:* Localized strings stored in version-controlled JSON files (`locales/en/assessment.json`, `locales/hi/assessment.json`).
  - *Pros:* Fully static, zero external API dependency during rendering, easily reviewed by certified medical translators.
- **Option B: Dynamic Cloud-Hosted Translation Service (e.g., Lokalise / Phrase)**
  - *Cons:* Requires paid API subscription, introduces third-party network latency during page render.
- **Status:** *Approved Architecture Recommendation: Option A.*

---

### Decision 06: Clinician Directory Consultation Booking Scope
- **Context:** How should the patient interact with verified cardiologists discovered in the directory?
- **Option A (Recommended for v2.0): Direct Outbound Contact & Clinic Routing**
  - *Behavior:* Provides verified telephone numbers, physical clinic addresses with Google Maps / Apple Maps links, and external official booking URLs.
  - *Pros:* Zero liability for calendar scheduling conflicts, no complex two-way EHR synchronization required in Phase 1.
- **Option B: Native In-App Appointment Scheduling System**
  - *Cons:* Vastly expands system scope into calendar booking, cancellation workflows, payment processing, and EHR synchronization.
- **Status:** *Approved Product Scope: Option A for Initial Launch.*
