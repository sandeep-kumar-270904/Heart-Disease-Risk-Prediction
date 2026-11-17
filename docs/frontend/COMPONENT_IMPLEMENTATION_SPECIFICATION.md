# HeartXAI 2.0 — Component Implementation Specification

**Document ID:** `HX2-FE-005`  
**Version:** `1.0.0`  
**Phase:** Phase 6 — Frontend Engineering Architecture & Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal Frontend Architect & Design Systems Lead  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011, HX2-DES-003, HX2-DES-005  

---

## 1. Overview & Component Architecture Philosophy

This document defines the production TypeScript contracts, accessibility specifications, visual states, and composition strategies for the reusable React component catalog in **HeartXAI 2.0**.

Every component adheres to:
1. **Unstyled Headless Primitives (Radix UI):** Complex interactive behaviors (modals, dropdowns, sliders, tabs) leverage battle-tested accessible primitives.
2. **Tailwind CSS Token Styling:** Clean utility classes styled via semantic CSS custom properties defined in `docs/design/DESIGN_TOKENS.md`.
3. **Compound Component Composition:** High-order components (Cards, Tables, Modals) utilize flexible sub-component composition rather than monolithic prop monsters with 30 boolean flags.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   COMPONENT COMPOSITION ARCHITECTURE                   │
├────────────────────────────────────────────────────────────────────────┤
│ [ Radix UI Headless Behavior ] + [ Tailwind Semantic Design Tokens ]   │
│                                │                                       │
│                                ▼                                       │
│             [ Typed React Component (TypeScript Props) ]               │
│                                │                                       │
│        ┌───────────────────────┴───────────────────────┐               │
│        ▼                                               ▼               │
│ [ Standard Form Controls ]                [ Specialized Clinical UI ]  │
│ Button, Input, Select, Modal              BiomarkerInput, RiskGauge,   │
│ Table, Alert, Tabs, Tooltip               ShapWaterfall, UnitToggle    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Foundation & Form Component Contracts

### 2.1 Primary & Secondary Actions (`<Button />`)

#### TypeScript Interface
```typescript
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  loadingText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}
```

#### States & Behavioral Specifications
- **Variants:**
  - `primary`: Background `var(--interactive-primary)`, text `#FFFFFF`, hover `var(--interactive-hover)`.
  - `secondary`: Background `var(--surface-card-subtle)`, text `var(--text-primary)`, border `var(--border-subtle)`.
  - `outline`: Transparent background, `1px solid var(--border-interactive)`, text `var(--text-primary)`.
  - `ghost`: Transparent background, no border, text `var(--text-secondary)`, hover background `var(--surface-card-subtle)`.
  - `danger`: Background `var(--status-error-border)`, text `#FFFFFF`.
- **States:**
  - `Default`: Flat surface, crisp text, minimum touch target $44\times 44\text{px}$ on touch devices.
  - `Hover`: Smooth color shift (`150ms ease-out`).
  - `Focus-Visible`: Explicit focus ring `outline: 2px solid var(--interactive-focus); outline-offset: 2px;`.
  - `Loading`: Displays `<Spinner size="sm" />`, text replaced by `loadingText` or dimmed, `aria-busy="true"`, pointer events disabled.
  - `Disabled`: Opacity $0.6$, cursor `not-allowed`, `aria-disabled="true"`.

---

### 2.2 Clinical Unit-Bound Input (`<BiomarkerInput />`)

#### Purpose
Captures clinical biomarkers (cholesterol, blood pressure, fasting glucose) with bound physical measurement units and live unit-toggle conversion.

#### TypeScript Interface
```typescript
export interface BiomarkerInputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'onChange'> {
  label: string;
  fieldId: string;
  value: number | '';
  onChange: (value: number | '') => void;
  unit: string;
  unitType?: 'cholesterol' | 'glucose' | 'pressure' | 'generic';
  onUnitToggle?: (newUnit: string) => void;
  allowedUnits?: string[];
  referenceRange?: { min: number; max: number; label: string };
  error?: string;
  helperText?: string;
  isRequired?: boolean;
}
```

#### Composition & Accessibility
```tsx
<div className="flex flex-col gap-1.5">
  <div className="flex justify-between items-center">
    <label htmlFor={fieldId} className="text-sm font-medium text-text-primary">
      {label} {isRequired && <span className="text-status-error">*</span>}
    </label>
    {allowedUnits && onUnitToggle && (
      <UnitToggle activeUnit={unit} units={allowedUnits} onToggle={onUnitToggle} />
    )}
  </div>
  <div className="relative flex items-center">
    <input
      id={fieldId}
      type="number"
      inputMode="decimal"
      value={value}
      onChange={(e) => onChange(e.target.value === '' ? '' : Number(e.target.value))}
      aria-invalid={Boolean(error)}
      aria-describedby={`${fieldId}-help ${error ? `${fieldId}-error` : ''}`}
      className="w-full pl-3 pr-16 py-2 border rounded-md font-mono tabular-nums text-text-primary border-border-interactive focus:outline-none focus:ring-2 focus:ring-interactive-focus"
    />
    <span className="absolute right-3 text-sm font-medium text-text-secondary select-none">
      {unit}
    </span>
  </div>
  {helperText && <p id={`${fieldId}-help`} className="text-xs text-text-muted">{helperText}</p>}
  {error && <p id={`${fieldId}-error`} role="alert" className="text-xs text-status-error font-medium">{error}</p>}
</div>
```

---

### 2.3 Interactive Scenario Slider (`<CounterfactualSlider />`)

#### Purpose
Allows patients and clinicians to simulate hypothetical physiological adjustments within safe biological guardrails.

#### TypeScript Interface
```typescript
export interface CounterfactualSliderProps {
  label: string;
  fieldId: string;
  baselineValue: number;
  currentValue: number;
  unit: string;
  min: number;
  max: number;
  step?: number;
  isModifiable?: boolean;
  disabledReason?: string;
  onChange: (value: number) => void;
  onReset: () => void;
}
```

#### Accessibility & Keyboard Rules
- Backed by Radix UI `<Slider.Root />`.
- `aria-valuemin={min}`, `aria-valuemax={max}`, `aria-valuenow={currentValue}`.
- Arrow keys modify value by `step`; `PageUp` / `PageDown` jump by `step * 5`.
- Visual delta pill (`currentValue - baselineValue`) rendered with high-contrast text and directional sign.

---

## 3. Data Display & Clinical Visualization Components

### 3.1 Dual Risk Gauge Card (`<RiskGaugeCard />`)

#### TypeScript Interface
```typescript
export interface RiskGaugeCardProps {
  cadLikelihoodPercent: number; // 0 - 100
  confidenceInterval: [number, number]; // e.g. [38, 46]
  riskStrata: 'low' | 'moderate' | 'elevated';
  tenYearPopulationRiskPercent?: number;
  modelVersion: string;
  cohortName: string;
  calculatedAt: string;
  onExportPdf?: () => void;
}
```

#### Anatomical Structure
1. **Header:** Title *"Angiographic CAD Association Evaluation"* + Model version badge.
2. **Body:** Calibrated horizontal segmented bar ($0\%–30\%$ Emerald, $30\%–70\%$ Amber, $70\%–100\%$ Crimson) with marker pin indicating exact likelihood and confidence interval.
3. **Comparative Metric:** Optional 10-Year Framingham / QRISK3 population comparison badge.
4. **Mandatory Educational Disclaimer:** *"Educational Model: Derived from observational clinical study cohorts. Informational estimation, not a medical diagnosis."*
5. **Screen Reader Equivalence:** Hidden `<div className="sr-only">` announcing full risk narrative.

---

### 3.2 SHAP Waterfall Attribution Display (`<ShapWaterfallChart />`)

#### TypeScript Interface
```typescript
export interface ShapFeatureImpact {
  featureName: string;
  rawFeatureValue: string | number;
  unit?: string;
  cohortAverageValue: string | number;
  shapValue: number; // e.g., +0.1412 or -0.0984
  direction: 'increases_likelihood' | 'decreases_likelihood';
  plainLanguageExplanation: string;
}

export interface ShapWaterfallChartProps {
  baseValue: number; // e.g., 0.38
  finalLikelihood: number; // e.g., 0.46
  features: ShapFeatureImpact[];
  isAccessibleTableVisible?: boolean;
  onToggleTable?: () => void;
}
```

#### Visualization Rules
- Center dashed baseline representing $0.00$ SHAP attribution.
- Features sorted descending by $|\text{shapValue}|$.
- Right-extending Crimson bars (`▲`) for positive contributions; Left-extending Blue bars (`▼`) for negative contributions.
- 1-Click button: `[Switch to Accessible Data Table]`, which replaces SVG with semantic HTML `<table />` containing full feature names, values, and impacts.

---

## 4. Navigation & Feedback Components

### 4.1 Application Header (`<AppHeader />`)
- **Props:**
  ```typescript
  export interface AppHeaderProps {
    user: UserProfile | null;
    activeCountry: CountryConfig;
    onOpenCountrySelector: () => void;
    onSignOut: () => void;
    unreadNotificationCount?: number;
  }
  ```
- **Capabilities:** Sticky positioning (`top: 0; z-index: 200;`), Country pill, Role badge (`PATIENT`, `CLINICIAN`, `ADMIN`), User avatar with accessible Radix `<DropdownMenu />`.

### 4.2 Severity-Tiered Clinical Alert Banner (`<AlertBanner />`)
- **Props:**
  ```typescript
  export interface AlertBannerProps {
    severity: 'emergency' | 'warning' | 'info' | 'success';
    title: string;
    message: string;
    actionLabel?: string;
    onAction?: () => void;
    isDismissible?: boolean;
    onDismiss?: () => void;
  }
  ```
- **Severity Mappings:**
  - `emergency`: Solid Crimson border `#DC2626`, ambient background `#FEF2F2`, text `#B91C1C`, icon `AlertOctagon`, `role="alert"`. Includes direct phone link for emergency calls (`tel:112`).
  - `warning`: Solid Amber border `#D97706`, ambient background `#FFFBEB`, text `#B45309`, icon `AlertTriangle`, `role="status"`.
  - `info`: Sky border `#0284C7`, ambient background `#F0F9FF`, text `#0369A1`, icon `Info`, `role="status"`.
  - `success`: Emerald border `#059669`, ambient background `#ECFDF5`, text `#047857`, icon `CheckCircle2`, `role="status"`.

---

## 5. Modal Dialogs & Focus Management

### 5.1 Accessible Modal Dialog (`<ModalDialog />`)
- **Props:**
  ```typescript
  export interface ModalDialogProps {
    isOpen: boolean;
    onClose: () => void;
    title: string;
    description?: string;
    children: React.ReactNode;
    footer?: React.ReactNode;
    size?: 'sm' | 'md' | 'lg' | 'xl';
  }
  ```
- **Implementation:** Wraps `@radix-ui/react-dialog`. Automatically locks body scroll, injects backdrop overlay (`bg-slate-900/60`), traps keyboard focus inside dialog, and binds `Escape` key to close.
