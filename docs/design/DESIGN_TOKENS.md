# HeartXAI 2.0 — Design Token System

**Document ID:** `HX2-DES-003`  
**Version:** `2.0.0`  
**Status:** `Approved Specification`  
**Author:** Principal Design Systems Architect & Frontend Experience Architect  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011  

---

## 1. Overview & Token Architecture

The HeartXAI 2.0 design token system provides an unambiguous single source of truth for all visual values across the application. Tokens are structured in three strict tiers:

```
┌────────────────────────────────────────────────────────┐
│ 1. Global / Primitive Tokens (Raw Values: HEX, rem, ms) │
├────────────────────────────────────────────────────────┤
│ 2. Semantic Tokens (Intent-Based: Surface, Text, Alert) │
├────────────────────────────────────────────────────────┤
│ 3. Component Tokens (Specific: Button-Primary-Bg)      │
└────────────────────────────────────────────────────────┘
```

All tokens are formatted for seamless compilation into **CSS Custom Properties (`:root`, `.dark`)** and **Tailwind CSS v3/v4 Theme Configuration**.

---

## 2. Primitive Color Tokens

### 2.1 Neutral Slate Scale (Base Structure)
```css
--color-slate-50:  #F8FAFC;
--color-slate-100: #F1F5F9;
--color-slate-200: #E2E8F0;
--color-slate-300: #CBD5E1;
--color-slate-400: #94A3B8;
--color-slate-500: #64748B;
--color-slate-600: #475569;
--color-slate-700: #334155;
--color-slate-800: #1E293B;
--color-slate-900: #0F172A;
--color-slate-950: #020617;
```

### 2.2 Brand & Interactive Blue Scale (Clinical Sky/Blue)
```css
--color-sky-50:  #F0F9FF;
--color-sky-100: #E0F2FE;
--color-sky-200: #BAE6FD;
--color-sky-300: #7DD3FC;
--color-sky-400: #38BDF8;
--color-sky-500: #0EA5E9;
--color-sky-600: #0284C7; /* Brand Primary Focus & CTA */
--color-sky-700: #0369A1;
--color-sky-800: #075985;
--color-sky-900: #0C4A6E;
```

### 2.3 Semantic Clinical & Feedback Palettes
```css
/* Critical Alerts / Elevated Risk Flags / Form Validation Errors */
--color-crimson-50:  #FEF2F2;
--color-crimson-100: #FEE2E2;
--color-crimson-500: #EF4444;
--color-crimson-600: #DC2626; /* WCAG AA High-Risk Foreground */
--color-crimson-700: #B91C1C;
--color-crimson-900: #7F1D1D;

/* Cautionary Alerts / Moderate Risk / Informational Warnings */
--color-amber-50:  #FFFBEB;
--color-amber-100: #FEF3C7;
--color-amber-500: #F59E0B;
--color-amber-600: #D97706; /* WCAG AA Caution Foreground */
--color-amber-700: #B45309;
--color-amber-900: #78350F;

/* Positive Health Factors / Safe Lab Biomarkers / Success Toast */
--color-emerald-50:  #ECFDF5;
--color-emerald-100: #D1FAE5;
--color-emerald-500: #10B981;
--color-emerald-600: #059669; /* WCAG AA Positive Foreground */
--color-emerald-700: #047857;
--color-emerald-900: #064E3B;

/* Model Introspection / Secondary SHAP Negative Contribution */
--color-violet-50:  #F5F3FF;
--color-violet-100: #EDE9FE;
--color-violet-600: #7C3AED;
--color-violet-700: #6D28D9;
```

---

## 3. Semantic Color Tokens (Light & Dark Themes)

| Semantic Token Name | Light Theme Value | Dark Theme Value | WCAG Contrast Ratio | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `--surface-canvas` | `#F8FAFC` (Slate 50) | `#0F172A` (Slate 900) | Background base | Full page layout canvas |
| `--surface-card` | `#FFFFFF` (Pure White) | `#1E293B` (Slate 800) | $\ge 12:1$ against text | Standard card & container background |
| `--surface-card-subtle` | `#F1F5F9` (Slate 100) | `#334155` (Slate 700) | $\ge 9:1$ against text | Nested panels, table headers, form inputs |
| `--surface-overlay` | `#FFFFFF` | `#1E293B` | Floating modals | Popovers, modal dialogs, drawers |
| `--text-primary` | `#0F172A` (Slate 900) | `#F8FAFC` (Slate 50) | $\ge 14:1$ (AAA) | Headings, primary patient copy |
| `--text-secondary` | `#475569` (Slate 600) | `#94A3B8` (Slate 400) | $\ge 5.8:1$ (AA) | Supporting descriptions, timestamps |
| `--text-muted` | `#64748B` (Slate 500) | `#64748B` (Slate 500) | $\ge 4.5:1$ (AA) | Helper text, disabled labels |
| `--border-subtle` | `#E2E8F0` (Slate 200) | `#334155` (Slate 700) | $3:1$ UI element | Structural dividing lines, card borders |
| `--border-interactive` | `#CBD5E1` (Slate 300) | `#475569` (Slate 600) | $3:1$ UI element | Form input borders, unselected tabs |
| `--interactive-primary` | `#0284C7` (Sky 600) | `#38BDF8` (Sky 400) | $\ge 4.6:1$ (AA) | Primary buttons, active tabs, progress bars |
| `--interactive-hover` | `#0369A1` (Sky 700) | `#0284C7` (Sky 600) | $\ge 5.2:1$ (AA) | Primary button hover state |
| `--interactive-focus` | `#0284C7` | `#38BDF8` | $3:1$ indicator | Keyboard focus outline ring |
| `--status-error-bg` | `#FEF2F2` (Crimson 50) | `#7F1D1D` (Crimson 900) | Ambient surface | Error banner & validation card fill |
| `--status-error-text` | `#B91C1C` (Crimson 700) | `#FEE2E2` (Crimson 100) | $\ge 7:1$ (AAA) | Error messages, high-risk flag label |
| `--status-error-border` | `#DC2626` (Crimson 600) | `#EF4444` (Crimson 500) | $3:1$ UI border | Error input border, alert rule |
| `--status-warn-bg` | `#FFFBEB` (Amber 50) | `#78350F` (Amber 900) | Ambient surface | Moderate alert / missing data fill |
| `--status-warn-text` | `#B45309` (Amber 700) | `#FEF3C7` (Amber 100) | $\ge 6.2:1$ (AA) | Warning copy, non-acute caution |
| `--status-warn-border` | `#D97706` (Amber 600) | `#F59E0B` (Amber 500) | $3:1$ UI border | Cautionary badge border |
| `--status-success-bg` | `#ECFDF5` (Emerald 50) | `#064E3B` (Emerald 900) | Ambient surface | Positive verification / save confirm |
| `--status-success-text`| `#047857` (Emerald 700) | `#D1FAE5` (Emerald 100) | $\ge 6.5:1$ (AA) | Normal biomarker label, saved banner |
| `--status-success-border`| `#059669` (Emerald 600) | `#10B981` (Emerald 500) | $3:1$ UI border | Success card border |

---

## 4. Typography Tokens

### 4.1 Font Family Stacks
```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
--font-mono: 'JetBrains Mono', SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
```

### 4.2 Type Scale (Size, Line-Height & Tracking)
```css
/* Display / Hero */
--text-4xl: 2.25rem;   /* 36px */
--lh-4xl:   2.75rem;   /* 44px */
--track-4xl: -0.025em;

/* Page Titles (H1) */
--text-3xl: 1.875rem;  /* 30px */
--lh-3xl:   2.25rem;   /* 36px */
--track-3xl: -0.02em;

/* Section Headings (H2) */
--text-2xl: 1.5rem;    /* 24px */
--lh-2xl:   2.0rem;    /* 32px */
--track-2xl: -0.015em;

/* Subsection / Card Headings (H3) */
--text-xl:  1.25rem;   /* 20px */
--lh-xl:    1.75rem;   /* 28px */
--track-xl: -0.01em;

/* Form Group / Subheading (H4) */
--text-lg:  1.125rem;  /* 18px */
--lh-lg:    1.625rem;  /* 26px */
--track-lg: -0.005em;

/* Primary Body & Standard Inputs */
--text-base: 1.0rem;   /* 16px */
--lh-base:   1.5rem;   /* 24px */
--track-base: 0.0em;

/* Secondary Text, Form Labels, Table Cells */
--text-sm:   0.875rem; /* 14px */
--lh-sm:     1.25rem;  /* 20px */
--track-sm:  0.005em;

/* Micro-Labels, Captions, Axis Ticks */
--text-xs:   0.75rem;  /* 12px */
--lh-xs:     1.0rem;   /* 16px */
--track-xs:  0.01em;
```

### 4.3 Font Weights
```css
--font-weight-regular: 400; /* Body, narrative, disclaimers */
--font-weight-medium:  500; /* Form labels, table headers, buttons */
--font-weight-semibold: 600; /* Card headings, page titles, alerts */
--font-weight-bold:    700; /* Primary numerical KPI totals */
```

---

## 5. Spacing, Layout & Dimension Tokens

### 5.1 Spacing Scale (8pt System with 4pt Micro-Steps)
```css
--space-0:   0px;
--space-1:   0.25rem; /* 4px  - Micro tag padding, icon gap */
--space-2:   0.5rem;  /* 8px  - Tight button padding, compact input */
--space-3:   0.75rem; /* 12px - Standard form field vertical pad */
--space-4:   1.0rem;  /* 16px - Standard card padding, component gap */
--space-5:   1.25rem; /* 20px - Dense section padding */
--space-6:   1.5rem;  /* 24px - Standard card gutter, panel padding */
--space-8:   2.0rem;  /* 32px - Page section separation */
--space-10:  2.5rem;  /* 40px - Major feature separation */
--space-12:  3.0rem;  /* 48px - Page header vertical gutter */
--space-16:  4.0rem;  /* 64px - Hero and major milestone block pad */
```

### 5.2 Breakpoints & Max-Widths
```css
--breakpoint-sm:  640px;  /* Mobile landscape / phablet */
--breakpoint-md:  768px;  /* Tablet portrait */
--breakpoint-lg:  1024px; /* Tablet landscape / small laptop */
--breakpoint-xl:  1280px; /* Standard desktop display */
--breakpoint-2xl: 1536px; /* High-resolution workstation */

--container-sm:  640px;
--container-md:  768px;
--container-lg:  1024px;
--container-xl:  1280px;
--container-2xl: 1536px;
```

---

## 6. Shape, Border & Elevation Tokens

### 6.1 Border Radii
```css
--radius-none: 0px;
--radius-sm:   2px;  /* Sub-micro tags */
--radius-md:   6px;  /* Form controls, input boxes, small buttons */
--radius-lg:   8px;  /* Standard content cards, data tables */
--radius-xl:   12px; /* Modal dialogs, major dashboard containers */
--radius-2xl:  16px; /* Callout banners */
--radius-full: 9999px; /* Status pills, avatar circles */
```

### 6.2 Elevation & Drop Shadows
```css
--shadow-none: none;
--shadow-sm:   0 1px 2px 0 rgba(15, 23, 42, 0.05);
--shadow-md:   0 4px 6px -1px rgba(15, 23, 42, 0.08), 0 2px 4px -2px rgba(15, 23, 42, 0.04);
--shadow-lg:   0 10px 15px -3px rgba(15, 23, 42, 0.10), 0 4px 6px -4px rgba(15, 23, 42, 0.05);
--shadow-xl:   0 20px 25px -5px rgba(15, 23, 42, 0.12), 0 8px 10px -6px rgba(15, 23, 42, 0.06);
--shadow-inner: inset 0 2px 4px 0 rgba(15, 23, 42, 0.06);
```

### 6.3 Z-Index Layering Hierarchy
```css
--z-hide:     -1;
--z-base:      0;
--z-elevated:  10;
--z-sticky:    100;  /* Sticky table headers, local toolbar */
--z-header:    200;  /* Top application navigation bar */
--z-dropdown:  1000; /* Select menus, autocompletes, popovers */
--z-backdrop:  1100; /* Modal and drawer backdrop overlay */
--z-modal:     1200; /* Modal dialog container */
--z-toast:     1300; /* Toast notification alerts */
--z-tooltip:   1400; /* Informational tooltips (highest layer) */
```

---

## 7. Motion & Transition Tokens

```css
/* Durations */
--duration-instant: 75ms;   /* Checkbox tick, radio select */
--duration-fast:    150ms;  /* Button hover, dropdown open */
--duration-normal:  200ms;  /* Accordion expand, tab switch */
--duration-slow:    300ms;  /* Modal entrance, drawer slide */

/* Easing Curves */
--ease-standard: cubic-bezier(0.16, 1, 0.3, 1); /* Natural UI curve */
--ease-in:       cubic-bezier(0.4, 0, 1, 1);     /* Smooth exit */
--ease-out:      cubic-bezier(0, 0, 0.2, 1);     /* Quick entrance */
```
