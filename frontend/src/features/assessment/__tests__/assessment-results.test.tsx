import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { axe } from 'vitest-axe';
import { AssessmentResultsPage } from '@/features/assessment/AssessmentResultsPage';
import type { AssessmentDetailResponse, ShapExplanationResponse } from '@/types';

const MOCK_ASSESSMENT: AssessmentDetailResponse = {
  id: 'assess-001',
  patient_id: 'usr-001',
  age: 57,
  sex: 1,
  chest_pain_type: 3,
  resting_bp: 158,
  serum_cholesterol: 268,
  fasting_blood_sugar: 135,
  fasting_blood_sugar_gt_120: true,
  resting_ecg: 2,
  max_heart_rate: 138,
  exercise_angina: 1,
  st_depression: 2.2,
  st_slope: 1,
  major_vessels: 2,
  thallium_stress: 3,
  cad_likelihood_percent: 78.4,
  risk_strata: 'unstratified',
  ten_year_population_risk_percent: null,
  model_version: 'v2.0.0',
  cohort_name: 'UCI Cleveland Retrospective Benchmark (N=303)',
  data_provenance: 'Category B — Verified Synthetic Persona Record',
  plain_language_summary: 'Experimental Retrospective Task A Model Score: 78.4% (non-diagnostic).',
  emergency_warning_active: false,
  created_at: '2026-11-25T00:00:00Z',
};

const MOCK_SHAP: ShapExplanationResponse = {
  assessment_id: 'assess-001',
  model_version: 'v2.0.0',
  base_value: -0.18,
  final_likelihood: 1.25,
  features: [
    {
      feature_name: 'ca',
      raw_patient_value: 2,
      unit: 'vessels',
      cohort_average_value: 0.67,
      shap_value: 0.85,
      direction: 'increases_likelihood',
      plain_language_explanation: 'Statistical association only.',
    },
    {
      feature_name: 'thalach',
      raw_patient_value: 138,
      unit: 'bpm',
      cohort_average_value: 149.6,
      shap_value: -0.22,
      direction: 'decreases_likelihood',
      plain_language_explanation: 'Statistical association only.',
    },
  ],
};

describe('Milestone 12-14: Results Dashboard, SHAP Waterfall & Counterfactual Simulator', () => {
  it('renders Task A results without Task B claims, toggles SHAP table, and passes axe', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(new Response(JSON.stringify(MOCK_SHAP), { status: 200 }))
    );

    const { container } = render(
      <MemoryRouter
        initialEntries={[{ pathname: '/assessments/assess-001', state: { assessment: MOCK_ASSESSMENT } }]}
      >
        <Routes>
          <Route path="/assessments/:id" element={<AssessmentResultsPage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('78.4%')).toBeInTheDocument();
    expect(screen.getByText(/prospective 10-year cardiovascular risk prediction/i)).toBeInTheDocument();
    expect(screen.getByText(/UNSTRATIFIED RESEARCH SCORE/i)).toBeInTheDocument();
    expect(screen.queryByText(/95% Interval/i)).not.toBeInTheDocument();

    const tableToggle = await screen.findByRole('button', { name: /Accessible Data Table/i });
    await userEvent.click(tableToggle);
    expect(screen.getByRole('table')).toBeInTheDocument();

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
