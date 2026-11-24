/**
 * HeartXAI 2.0 - Clinical Assessment, Explainability & Synthetic Fixture Types
 * Mirrors backend/app/schemas/assessment.py with 100% field & nullability parity.
 */

import type { UnitSystem } from './auth';

export type RiskStrata = 'low' | 'moderate' | 'elevated';

export type ShapDirection = 'increases_likelihood' | 'decreases_likelihood';

export interface AssessmentCreateDto {
  readonly age: number;
  readonly sex: number;
  readonly chest_pain_type: number;
  readonly unit_system: UnitSystem;
  readonly resting_bp: number;
  readonly serum_cholesterol: number;
  readonly fasting_blood_sugar: number;
  readonly resting_ecg: number;
  readonly max_heart_rate: number;
  readonly exercise_angina: number;
  readonly st_depression: number;
  readonly st_slope: number;
  readonly major_vessels: number | null;
  readonly thallium_stress: number | null;
}

export interface AssessmentDetailResponse {
  readonly id: string;
  readonly patient_id: string;
  readonly age: number;
  readonly sex: number;
  readonly chest_pain_type: number;
  readonly resting_bp: number;
  readonly serum_cholesterol: number;
  readonly fasting_blood_sugar: number;
  readonly resting_ecg: number;
  readonly max_heart_rate: number;
  readonly exercise_angina: number;
  readonly st_depression: number;
  readonly st_slope: number;
  readonly major_vessels: number | null;
  readonly thallium_stress: number | null;
  readonly cad_likelihood_percent: number;
  readonly confidence_interval: readonly [number, number];
  readonly risk_strata: RiskStrata;
  /** Reserved for post-MVP research; strictly null in MVP per DEC-003 Option A */
  readonly ten_year_population_risk_percent: number | null;
  readonly model_version: string;
  readonly cohort_name: string;
  readonly plain_language_summary: string;
  readonly emergency_warning_active: boolean;
  readonly created_at: string;
}

export interface FeatureImpactDto {
  readonly feature_name: string;
  readonly raw_patient_value: number;
  readonly unit: string;
  readonly cohort_average_value: number;
  readonly shap_value: number;
  readonly direction: ShapDirection;
  readonly plain_language_explanation: string;
}

export interface ShapExplanationResponse {
  readonly assessment_id: string;
  readonly model_version: string;
  readonly base_value: number;
  readonly final_likelihood: number;
  readonly features: readonly FeatureImpactDto[];
}

export interface ScenarioSimulationRequest {
  readonly modified_features: Readonly<Record<string, number>>;
}

export interface ScenarioResultDto {
  readonly assessment_id: string;
  readonly baseline_likelihood_percent: number;
  readonly simulated_likelihood_percent: number;
  readonly delta_percent: number;
  readonly feasibility_score: number;
  readonly is_biological_clamp_violated: boolean;
  readonly violation_message: string | null;
}

export interface SyntheticPatientRecord {
  readonly is_synthetic: true;
  readonly mrn: string;
  readonly patient_name: string;
  readonly synthetic_generator_version: string;
  readonly generation_timestamp: string;
  readonly data_category: 'Category B — Synthetic Application Fixture';
  readonly intake: AssessmentCreateDto;
}
