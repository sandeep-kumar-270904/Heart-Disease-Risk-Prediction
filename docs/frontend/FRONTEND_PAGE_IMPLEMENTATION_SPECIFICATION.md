# HeartXAI 2.0 — Frontend Page Implementation Specification

**Document ID:** `HX2-FE-009`  
**Version:** `1.0.0`  
**Phase:** Phase 6 — Frontend Engineering Architecture & Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal Frontend Architect & Senior React Engineer  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011, HX2-DES-007, HX2-DES-008, HX2-DES-009  

---

## 1. Overview & Page Implementation Standards

This specification details the frontend implementation blueprints for all primary application routes in **HeartXAI 2.0**. 

Every page specification strictly adheres to:
1. **Zero Decorative Controls:** Every rendered button, tab, and link connects to an explicit API operation, route transition, or accessibility dialog.
2. **Deterministic State Coverage:** Implementation defines all six states: *Initial, Loading, Empty, Error, Validating, Success*.
3. **Clinical Framing Invariants:** All model predictions are displayed inside verified educational wrappers enforcing non-diagnostic terminology.

---

## 2. Core Patient Workspaces

---

### Page 01: Patient Dashboard (`/patient/dashboard`)

#### 1. Page Purpose
Delivers a calm, consolidated cardiovascular status overview, surfacing the latest assessment likelihood, recent vital measurements, historical sparkline, and direct assessment triggers.

#### 2. Component Hierarchy
```
<PatientLayout>
  <DashboardContainer>
    <WelcomeHeader name={user.name} lastAssessmentDate={summary.lastDate} />
    <EmergencyNotice condition={summary.hasEmergencyAlert} />
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 flex flex-col gap-6">
        <RiskSummaryHero 
          cadLikelihood={summary.latestAssessment.likelihood}
          riskStrata={summary.latestAssessment.strata}
          calculatedAt={summary.latestAssessment.date}
          onViewBreakdown={() => navigate(`/patient/assessments/${summary.latestAssessment.id}`)}
        />
        <VitalsSnapshotGrid 
          vitals={summary.latestVitals} 
          units={activeUnits}
          onSelectMetric={(metric) => navigate(`/patient/trends?metric=${metric}`)}
        />
      </div>
      <div className="flex flex-col gap-6">
        <QuickActionCard 
          onNewAssessment={() => navigate('/patient/assessments/new')}
          onFindDoctors={() => navigate('/patient/directory/doctors')}
          onExportReport={() => navigate('/patient/reports/export')}
        />
        <RiskTrendMiniSparkline data={summary.historicalSparkline} />
        <EducationalTipCard article={summary.featuredArticle} />
      </div>
    </div>
  </DashboardContainer>
</PatientLayout>
```

#### 3. Data & API Dependencies
- **Hook:** `useDashboardSummary()` $\rightarrow$ calls `GET /api/v1/patient/dashboard/summary`.
- **Cache Policy:** Stale time 5 minutes; refetched on window focus if stale.

#### 4. Interaction & Validation Behavior
- Clicking `[Start Assessment]` triggers route navigation to `/patient/assessments/new`.
- Clicking any vital card (e.g., Blood Pressure) navigates to `/patient/trends?metric=blood_pressure`.
- Clicking `[View Breakdown]` navigates to `/patient/assessments/:id`.

#### 5. States
- **Loading:** Renders skeleton containers for Hero, KPI grid, and sparkline; `aria-busy="true"`.
- **Empty (New Patient):** Renders onboarding welcome card: *"Welcome to HeartXAI. Complete your initial cardiovascular health assessment to generate your personalized baseline."* Large CTA: `[Start Your First Assessment]`.
- **Error:** Renders inline `<AlertBanner severity="warning">` with retry button.

---

### Page 02: Assessment Intake Wizard (`/patient/assessments/new`)

#### 1. Page Purpose
Guides the patient through a structured 6-step clinical data intake process with bound unit toggles, real-time physiological validation, and emergency symptom intercepts.

#### 2. Component Hierarchy
```
<PatientLayout>
  <WizardContainer>
    <WizardStepProgress currentStep={step} totalSteps={6} steps={stepMeta} />
    <EmergencyNotice isVisible={isAcuteSymptomDetected} />
    <form onSubmit={handleSubmit(onSubmit)}>
      {step === 1 && <Step1Demographics register={register} errors={errors} />}
      {step === 2 && <Step2Vitals register={register} control={control} errors={errors} />}
      {step === 3 && <Step3Laboratory register={register} control={control} errors={errors} units={units} />}
      {step === 4 && <Step4Electrocardiogram register={register} control={control} errors={errors} />}
      {step === 5 && <Step5Imaging register={register} control={control} errors={errors} />}
      {step === 6 && <Step6Review formData={getValues()} isSubmitting={isPending} onConfirm={onSubmit} />}
      <WizardActionBar 
        currentStep={step} 
        onBack={handleBack} 
        onNext={handleNext} 
        onSaveDraft={handleSaveDraft}
        isNextDisabled={!isValid}
        isSubmitting={isPending}
      />
    </form>
  </WizardContainer>
</PatientLayout>
```

#### 3. Data & API Dependencies
- **Draft Hook:** `useAssessmentDraft()` $\rightarrow$ reads/writes encrypted session draft.
- **Submission Hook:** `useSubmitAssessment()` $\rightarrow$ dispatches `POST /api/v1/assessments`.
- **Validation:** Zod schema `assessmentValidationSchema` validating step-by-step fields.

#### 4. Unit Conversion & Live Ergonomics
- In Step 3 (Laboratory), toggling from `mg/dL` to `mmol/L` triggers `UnitContext.convert('serum_cholesterol', 'mmol/L')`, instantly adjusting field value, step precision (`0.01`), and bounds ($[2.59, 15.52]$).

#### 5. States
- **Acute Symptom Intercept:** Selecting resting typical angina + systolic BP $> 180\text{ mmHg}$ immediately renders Crimson Emergency Banner with direct click-to-call `tel:112` / `tel:911`.
- **Submitting:** Wizard buttons disabled; primary action renders spinner with label *"Computing cardiovascular risk and SHAP attribution..."*.
- **Success:** Redirects to `/patient/assessments/:newId` with smooth entrance animation.

---

### Page 03: Assessment Results & Overview (`/patient/assessments/:id`)

#### 1. Page Purpose
Presents the calculated Angiographic CAD Association Likelihood alongside 10-year population benchmarks, plain-language clinical interpretation, and action triggers.

#### 2. Component Hierarchy
```
<PatientLayout>
  <AssessmentDetailContainer>
    <AssessmentHeader 
      assessmentId={id} 
      date={data.createdAt} 
      modelVersion={data.modelVersion}
      onExportPdf={handleExportPdf}
    />
    <MandatoryEducationalDisclaimerBanner />
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 flex flex-col gap-6">
        <RiskGaugeCard 
          cadLikelihoodPercent={data.cadLikelihoodPercent}
          confidenceInterval={data.confidenceInterval}
          riskStrata={data.riskStrata}
          tenYearPopulationRiskPercent={data.tenYearPopulationRiskPercent}
          modelVersion={data.modelVersion}
          cohortName={data.cohortName}
          calculatedAt={data.createdAt}
        />
        <AssessmentNarrativeCard narrative={data.plainLanguageSummary} />
        <KeyContributingFactorsSummary factors={data.topShapFactors} />
      </div>
      <div className="flex flex-col gap-6">
        <NavigationTabCard activeTab="overview" assessmentId={id} />
        <PhysicianDiscussionCard onExportReport={handleExportPdf} />
        <FindCardiologistCTA country={data.countryCode} />
      </div>
    </div>
  </AssessmentDetailContainer>
</PatientLayout>
```

#### 3. Data & API Dependencies
- **Hook:** `useAssessmentDetail(id)` $\rightarrow$ calls `GET /api/v1/assessments/:id`.

---

### Page 04: SHAP Feature Explainability (`/patient/assessments/:id/explainability`)

#### 1. Page Purpose
Visualizes local tree-ensemble feature attributions, explaining exactly which patient biomarkers shifted predicted likelihood above or below cohort baseline.

#### 2. Component Hierarchy
```
<PatientLayout>
  <ExplainabilityContainer>
    <AssessmentHeader assessmentId={id} date={data.createdAt} activeTab="explainability" />
    <div className="flex justify-between items-center mb-4">
      <ExplainabilityHeading title="Feature Contribution Breakdown (SHAP)" />
      <ViewToggle 
        currentView={view} 
        onToggle={(v) => setView(v)} 
        options={['Visual Waterfall', 'Accessible Data Table']} 
      />
    </div>
    {view === 'visual' ? (
      <ShapWaterfallChart 
        baseValue={data.shapBaseValue}
        finalLikelihood={data.cadLikelihoodPercent / 100}
        features={data.shapFeatures}
      />
    ) : (
      <ShapTableFallback features={data.shapFeatures} />
    )}
    <ShapMethodologyFootnote />
  </ExplainabilityContainer>
</PatientLayout>
```

#### 3. Interaction & Accessibility
- Hovering/tapping any SHAP bar opens `<FeatureImpactTooltip />` detailing raw patient value, cohort mean, exact mathematical SHAP impact, and plain-language medical context.
- Screen readers receive the accessible HTML table containing all values and impacts.

---

### Page 05: Counterfactual Scenarios Simulator (`/patient/assessments/:id/scenarios`)

#### 1. Page Purpose
Enables interactive "what-if" physiological simulation by adjusting modifiable variables (BP, cholesterol, blood sugar) and viewing real-time simulated risk delta.

#### 2. Component Hierarchy
```
<PatientLayout>
  <CounterfactualContainer>
    <AssessmentHeader assessmentId={id} date={data.createdAt} activeTab="scenarios" />
    <HypotheticalSimulationDisclaimerBanner />
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <div className="flex flex-col gap-4">
        <h3 className="text-lg font-semibold text-text-primary">Modifiable Health Variables</h3>
        {modifiableVariables.map((variable) => (
          <CounterfactualSlider 
            key={variable.id}
            label={variable.label}
            fieldId={variable.id}
            baselineValue={variable.baseline}
            currentValue={simulatedValues[variable.id]}
            unit={variable.unit}
            min={variable.min}
            max={variable.max}
            onChange={(val) => handleSliderChange(variable.id, val)}
            onReset={() => handleSliderReset(variable.id)}
          />
        ))}
        <Button variant="outline" onClick={handleResetAll}>Reset All to Baseline</Button>
      </div>
      <div>
        <SimulatedOutcomeCard 
          baselineLikelihood={data.cadLikelihoodPercent}
          simulatedLikelihood={simulatedResult.likelihood}
          delta={simulatedResult.delta}
          isCalculating={isSimulating}
        />
      </div>
    </div>
  </CounterfactualContainer>
</PatientLayout>
```

---

## 3. Administrative Workspaces

---

### Page 06: Admin Command Center (`/admin/dashboard`)

#### 1. Page Purpose
Provides real-time visibility into infrastructure health, inference latency, error rates, database connection pools, and Celery background worker queues.

#### 2. Key Components
- `SystemHealthStatusStrip` (Operational, Degraded, Critical).
- `TelemetryKpiGrid` (P95 Latency: `42ms`, Daily Evaluations: `1,428`, Error Rate: `0.02%`).
- `WorkerQueueDepthChart` & `DatabasePoolSaturationGauge`.
- `LiveErrorStream` with direct Sentry issue links.

---

### Page 07: Clinician Credential Verification Queue (`/admin/verifications`)

#### 1. Page Purpose
Enables compliance officers to inspect physician license submissions, review uploaded diplomas/IDs, and issue or reject verified clinician credentials.

#### 2. Key Components
- `VerificationQueueTable` (Sortable by submitted date, country, license authority).
- `SplitPaneReviewDrawer`:
  - Left Pane: Applicant metadata, registry search link (NMC India, State Board USA).
  - Right Pane: High-resolution PDF/image credential document viewer with zoom/rotate.
- `ApprovalActionBar`: `[✓ Approve & Issue Badge]`, `[✗ Reject with Reason]`.
