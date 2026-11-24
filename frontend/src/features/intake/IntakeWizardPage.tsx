import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Alert,
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
  Input,
  Select,
} from '@/components/ui';
import {
  cholesterolMgDlToMmolL,
  cholesterolMmolLToMgDl,
  glucoseMgDlToMmolL,
  glucoseMmolLToMgDl,
} from '@/lib/unitConverter';
import { apiFetch, ApiClientError } from '@/services/apiClient';
import type { AssessmentDetailResponse } from '@/types';
import { intakeFormSchema, type IntakeFormValues } from './intakeSchema';

const DEFAULT_VALUES: IntakeFormValues = {
  synthetic_fixture_confirmed: true,
  age: 54,
  sex: 1,
  chest_pain_type: 2,
  unit_system: 'us_customary',
  resting_bp: 128,
  serum_cholesterol: 212,
  fasting_blood_sugar: 98,
  resting_ecg: 0,
  max_heart_rate: 152,
  exercise_angina: 0,
  st_depression: 1.0,
  st_slope: 0,
  major_vessels: 0,
  thallium_stress: 1,
};

const STEPS = [
  'Demographics',
  'Vitals & Symptoms',
  'Metabolic Labs',
  'ECG & Stress',
  'Imaging & Review',
] as const;

export const IntakeWizardPage: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState<number>(0);
  const [values, setValues] = useState<IntakeFormValues>(DEFAULT_VALUES);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleToggleUnitSystem = (targetSystem: 'us_customary' | 'metric'): void => {
    if (targetSystem === values.unit_system) return;
    setValues((prev) => ({
      ...prev,
      unit_system: targetSystem,
      serum_cholesterol:
        targetSystem === 'metric'
          ? cholesterolMgDlToMmolL(prev.serum_cholesterol, 2)
          : cholesterolMmolLToMgDl(prev.serum_cholesterol, 0),
      fasting_blood_sugar:
        targetSystem === 'metric'
          ? glucoseMgDlToMmolL(prev.fasting_blood_sugar, 2)
          : glucoseMmolLToMgDl(prev.fasting_blood_sugar, 0),
    }));
  };

  const handleSubmit = async (): Promise<void> => {
    setSubmitError(null);
    const parsed = intakeFormSchema.safeParse(values);
    if (!parsed.success) {
      const errors: Record<string, string> = {};
      for (const issue of parsed.error.issues) {
        const key = String(issue.path[0] ?? 'form');
        errors[key] = issue.message;
      }
      setFieldErrors(errors);
      setSubmitError('Please resolve highlighted clinical parameter bounds before submitting.');
      return;
    }

    setFieldErrors({});
    setIsSubmitting(true);
    try {
      const created = await apiFetch<AssessmentDetailResponse>('/assessments', {
        method: 'POST',
        body: JSON.stringify(parsed.data),
      });
      navigate(`/assessments/${created.id}`, { state: { assessment: created } });
    } catch (err) {
      setSubmitError(
        err instanceof ApiClientError ? err.message : 'Unable to submit synthetic assessment.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Clinical Intake Wizard</h1>
          <p className="text-sm text-slate-600">
            13-biomarker intake with real-time unit normalization and safety guardrails (Category B
            synthetic inputs only).
          </p>
        </div>
        <Badge variant="neutral">
          Step {step + 1} of {STEPS.length}: {STEPS[step]}
        </Badge>
      </div>

      <Alert
        severity="info"
        title="Synthetic Input Demonstration Notice (DEC-005)"
        description="Automated clinical red-flag triage is disabled pending physician advisory review. Do not submit real patient data or rely on this tool during acute symptoms."
      />

      {submitError && (
        <Alert severity="warning" title="Validation Notice" description={submitError} />
      )}

      <div role="status" aria-live="polite" className="sr-only">
        Step {step + 1} of {STEPS.length}: {STEPS[step]} loaded.
      </div>

      <Card elevated>
        <CardHeader>
          <CardTitle as="h2">{STEPS[step]}</CardTitle>
          <CardDescription>Synthetic values remain in memory only until submitted.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-5">
          {step === 0 && (
            <div className="grid gap-4 sm:grid-cols-2">
              <Input
                label="Chronological Age"
                type="number"
                required
                unitAffix="years"
                value={String(values.age)}
                onChange={(e) => setValues({ ...values, age: Number(e.target.value) })}
                error={fieldErrors.age}
                helperText="Valid range: 18–100 years"
              />
              <Select
                label="Biological Sex"
                required
                value={String(values.sex)}
                onValueChange={(v) => setValues({ ...values, sex: Number(v) })}
                options={[
                  { value: '1', label: 'Male (1)' },
                  { value: '0', label: 'Female (0)' },
                ]}
              />
            </div>
          )}

          {step === 1 && (
            <div className="grid gap-4 sm:grid-cols-2">
              <Input
                label="Resting Systolic Blood Pressure"
                type="number"
                required
                unitAffix="mmHg"
                value={String(values.resting_bp)}
                onChange={(e) => setValues({ ...values, resting_bp: Number(e.target.value) })}
                error={fieldErrors.resting_bp}
                helperText="Valid range: 70–240 mmHg (synthetic model input)"
              />
              <Select
                label="Chest Pain Presentation"
                required
                value={String(values.chest_pain_type)}
                onValueChange={(v) => setValues({ ...values, chest_pain_type: Number(v) })}
                options={[
                  { value: '0', label: 'Typical Angina' },
                  { value: '1', label: 'Atypical Angina' },
                  { value: '2', label: 'Non-Anginal Pain' },
                  { value: '3', label: 'Asymptomatic' },
                ]}
              />
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-sm font-medium text-slate-900">Lipid &amp; Glucose Units:</span>
                <Button
                  size="sm"
                  variant={values.unit_system === 'us_customary' ? 'primary' : 'outline'}
                  onClick={() => handleToggleUnitSystem('us_customary')}
                >
                  US Customary (mg/dL)
                </Button>
                <Button
                  size="sm"
                  variant={values.unit_system === 'metric' ? 'primary' : 'outline'}
                  onClick={() => handleToggleUnitSystem('metric')}
                >
                  SI Metric (mmol/L)
                </Button>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <Input
                  label="Serum Cholesterol"
                  type="number"
                  step="0.01"
                  required
                  unitAffix={values.unit_system === 'metric' ? 'mmol/L' : 'mg/dL'}
                  value={String(values.serum_cholesterol)}
                  onChange={(e) =>
                    setValues({ ...values, serum_cholesterol: Number(e.target.value) })
                  }
                  error={fieldErrors.serum_cholesterol}
                />
                <Input
                  label="Fasting Blood Sugar"
                  type="number"
                  step="0.01"
                  required
                  unitAffix={values.unit_system === 'metric' ? 'mmol/L' : 'mg/dL'}
                  value={String(values.fasting_blood_sugar)}
                  onChange={(e) =>
                    setValues({ ...values, fasting_blood_sugar: Number(e.target.value) })
                  }
                  error={fieldErrors.fasting_blood_sugar}
                />
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="grid gap-4 sm:grid-cols-2">
              <Select
                label="Resting ECG Result"
                value={String(values.resting_ecg)}
                onValueChange={(v) => setValues({ ...values, resting_ecg: Number(v) })}
                options={[
                  { value: '0', label: 'Normal' },
                  { value: '1', label: 'ST-T Wave Abnormality' },
                  { value: '2', label: 'Left Ventricular Hypertrophy' },
                ]}
              />
              <Input
                label="Max Heart Rate Achieved"
                type="number"
                required
                unitAffix="bpm"
                value={String(values.max_heart_rate)}
                onChange={(e) => setValues({ ...values, max_heart_rate: Number(e.target.value) })}
                error={fieldErrors.max_heart_rate}
              />
              <Select
                label="Exercise-Induced Angina"
                value={String(values.exercise_angina)}
                onValueChange={(v) => setValues({ ...values, exercise_angina: Number(v) })}
                options={[
                  { value: '0', label: 'No' },
                  { value: '1', label: 'Yes' },
                ]}
              />
              <Input
                label="ST Depression (Oldpeak)"
                type="number"
                step="0.1"
                required
                unitAffix="mm"
                value={String(values.st_depression)}
                onChange={(e) => setValues({ ...values, st_depression: Number(e.target.value) })}
                error={fieldErrors.st_depression}
              />
              <Select
                label="Peak Exercise ST Slope"
                value={String(values.st_slope)}
                onValueChange={(v) => setValues({ ...values, st_slope: Number(v) })}
                options={[
                  { value: '0', label: 'Upsloping' },
                  { value: '1', label: 'Flat' },
                  { value: '2', label: 'Downsloping' },
                ]}
              />
            </div>
          )}

          {step === 4 && (
            <div className="grid gap-4 sm:grid-cols-2">
              <Select
                label="Major Vessels (Fluoroscopy)"
                value={values.major_vessels === null ? 'none' : String(values.major_vessels)}
                onValueChange={(v) =>
                  setValues({ ...values, major_vessels: v === 'none' ? null : Number(v) })
                }
                helperText="Optional: training-fold median (0) imputed if unknown"
                options={[
                  { value: 'none', label: 'Not Available (Impute)' },
                  { value: '0', label: '0 Vessels' },
                  { value: '1', label: '1 Vessel' },
                  { value: '2', label: '2 Vessels' },
                  { value: '3', label: '3 Vessels' },
                ]}
              />
              <Select
                label="Thallium Scintigraphy Defect"
                value={values.thallium_stress === null ? 'none' : String(values.thallium_stress)}
                onValueChange={(v) =>
                  setValues({ ...values, thallium_stress: v === 'none' ? null : Number(v) })
                }
                helperText="Optional: training-fold mode (Normal) imputed if unknown"
                options={[
                  { value: 'none', label: 'Not Available (Impute)' },
                  { value: '1', label: 'Normal (1)' },
                  { value: '2', label: 'Fixed Defect (2)' },
                  { value: '3', label: 'Reversible Defect (3)' },
                ]}
              />
            </div>
          )}
        </CardContent>
        <CardFooter>
          <Button
            variant="outline"
            disabled={step === 0}
            onClick={() => setStep((s) => Math.max(0, s - 1))}
          >
            Previous
          </Button>
          {step < STEPS.length - 1 ? (
            <Button onClick={() => setStep((s) => Math.min(STEPS.length - 1, s + 1))}>Next</Button>
          ) : (
            <Button onClick={handleSubmit} isLoading={isSubmitting} loadingText="Computing...">
              Run Task A Assessment
            </Button>
          )}
        </CardFooter>
      </Card>
    </div>
  );
};
