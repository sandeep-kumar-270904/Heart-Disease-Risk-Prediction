import { z } from 'zod';
import { cholesterolMmolLToMgDl, glucoseMmolLToMgDl } from '@/lib/unitConverter';

export const intakeFormSchema = z
  .object({
    synthetic_fixture_confirmed: z.literal(true),
    age: z.coerce
      .number()
      .min(18, 'Age must be at least 18 years.')
      .max(100, 'Age must not exceed 100 years.'),
    sex: z.coerce.number().int().min(0).max(1),
    chest_pain_type: z.coerce.number().int().min(0).max(3),
    unit_system: z.enum(['us_customary', 'metric']),
    resting_bp: z.coerce
      .number()
      .min(70, 'Resting systolic BP must be at least 70 mmHg.')
      .max(240, 'Resting systolic BP must not exceed 240 mmHg.'),
    serum_cholesterol: z.coerce
      .number()
      .min(2.59, 'Cholesterol below physiological lower bound.')
      .max(600, 'Cholesterol cannot exceed 600 mg/dL.'),
    fasting_blood_sugar: z.coerce
      .number()
      .min(0, 'Fasting blood sugar cannot be negative.')
      .max(500, 'Fasting blood sugar cannot exceed 500 mg/dL.'),
    resting_ecg: z.coerce.number().int().min(0).max(2),
    max_heart_rate: z.coerce
      .number()
      .min(60, 'Maximum heart rate must be at least 60 bpm.')
      .max(220, 'Maximum heart rate cannot exceed 220 bpm.'),
    exercise_angina: z.coerce.number().int().min(0).max(1),
    st_depression: z.coerce
      .number()
      .min(0, 'ST depression must be >= 0.0 mm.')
      .max(6.2, 'ST depression must not exceed 6.2 mm.'),
    st_slope: z.coerce.number().int().min(0).max(2),
    major_vessels: z.union([z.coerce.number().int().min(0).max(3), z.null()]),
    thallium_stress: z.union([z.coerce.number().int().min(1).max(3), z.null()]),
  })
  .superRefine((data, ctx) => {
    const cholMgDl =
      data.unit_system === 'metric' && data.serum_cholesterol < 20
        ? cholesterolMmolLToMgDl(data.serum_cholesterol, 2)
        : data.serum_cholesterol;
    if (cholMgDl < 100 || cholMgDl > 600) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ['serum_cholesterol'],
        message: 'Serum cholesterol must normalize between 100 and 600 mg/dL (2.59–15.52 mmol/L).',
      });
    }

    const fbsMgDl =
      data.unit_system === 'metric' && data.fasting_blood_sugar >= 2 && data.fasting_blood_sugar < 30
        ? glucoseMmolLToMgDl(data.fasting_blood_sugar, 2)
        : data.fasting_blood_sugar;
    if (fbsMgDl > 500) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ['fasting_blood_sugar'],
        message: 'Fasting blood sugar cannot exceed 500 mg/dL.',
      });
    }
  });

export type IntakeFormValues = z.infer<typeof intakeFormSchema>;

export function detectEmergencyRedFlags(_values: {
  readonly resting_bp: number;
  readonly chest_pain_type: number;
  readonly exercise_angina: number;
}): { readonly active: false; readonly message: null } {
  // Unreviewed automated emergency/red-flag triage thresholds (e.g., resting_bp > 180 or angina heuristics)
  // are intentionally disabled pending DEC-002 Physician Advisory Review & sign-off.
  return { active: false, message: null };
}
