/**
 * HeartXAI 2.0 - Country Configuration & Adapter Profile Types
 * Mirrors backend/app/schemas/country.py with 100% field & nullability parity.
 */

import type { UnitSystem } from './auth';

export interface CountryProfileDto {
  readonly country_code: string;
  readonly country_name: string;
  readonly default_unit_system: UnitSystem;
  readonly cholesterol_unit: string;
  readonly glucose_unit: string;
  readonly emergency_number: string;
  readonly emergency_label: string;
  readonly currency_code: string;
  readonly postal_code_regex: string;
  readonly clinical_guideline_reference: string;
  readonly privacy_framework: string;
  readonly regulatory_note: string;
}

export interface CountryListResponse {
  readonly governance_decision: string;
  readonly profiles: readonly CountryProfileDto[];
}
