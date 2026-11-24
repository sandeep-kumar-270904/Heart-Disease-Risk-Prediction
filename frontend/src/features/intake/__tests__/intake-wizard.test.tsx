import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it } from 'vitest';
import { axe } from 'vitest-axe';
import { IntakeWizardPage } from '@/features/intake/IntakeWizardPage';
import { intakeFormSchema } from '@/features/intake/intakeSchema';
import {
  cholesterolMgDlToMmolL,
  cholesterolMmolLToMgDl,
  glucoseMgDlToMmolL,
  glucoseMmolLToMgDl,
} from '@/lib/unitConverter';

describe('Milestone 08: Clinical Intake Wizard, Unit Conversion & Emergency Triggers', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('computes unit conversions accurately to 4 decimal places', () => {
    expect(cholesterolMgDlToMmolL(200, 4)).toBe(5.172);
    expect(cholesterolMmolLToMgDl(5.172, 4)).toBe(200.0012);
    expect(glucoseMgDlToMmolL(120, 4)).toBe(6.6607);
    expect(glucoseMmolLToMgDl(6.6607, 4)).toBe(119.9992);
  });

  it('rejects biologically implausible inputs via Zod intakeFormSchema', () => {
    const invalid = intakeFormSchema.safeParse({
      synthetic_fixture_confirmed: true,
      age: 12,
      sex: 1,
      chest_pain_type: 0,
      unit_system: 'us_customary',
      resting_bp: 350,
      serum_cholesterol: 210,
      fasting_blood_sugar: 95,
      resting_ecg: 0,
      max_heart_rate: 150,
      exercise_angina: 0,
      st_depression: 1.0,
      st_slope: 0,
      major_vessels: null,
      thallium_stress: null,
    });

    expect(invalid.success).toBe(false);
    if (!invalid.success) {
      const fields = invalid.error.issues.map((i) => i.path[0]);
      expect(fields).toContain('age');
      expect(fields).toContain('resting_bp');
    }
  });

  it('displays non-diagnostic synthetic guardrail banner without automated crisis triage claims and passes axe', async () => {
    const { container } = render(
      <MemoryRouter>
        <IntakeWizardPage />
      </MemoryRouter>
    );

    // Navigate to Step 2 (Vitals & Symptoms)
    await userEvent.click(screen.getByRole('button', { name: 'Next' }));
    const bpInput = screen.getByLabelText(/Resting Systolic Blood Pressure/i);
    await userEvent.clear(bpInput);
    await userEvent.type(bpInput, '195');

    expect(
      screen.getByText(/Automated clinical red-flag triage is disabled pending physician advisory review/i)
    ).toBeInTheDocument();
    expect(screen.queryByText(/Hypertensive Crisis Range/i)).not.toBeInTheDocument();

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
