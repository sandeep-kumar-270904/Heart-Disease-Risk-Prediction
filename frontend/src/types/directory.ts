/**
 * HeartXAI 2.0 - Healthcare Directory & Educational Guidance Types
 * Mirrors backend/app/schemas/directory.py with 100% field & nullability parity.
 */

export interface DoctorProfileDto {
  readonly id: string;
  readonly full_name: string;
  readonly specialization: string;
  readonly qualification: string;
  readonly medical_license_number: string;
  readonly license_issuing_authority: string;
  readonly is_license_verified: boolean;
  readonly hospital_affiliation: string;
  readonly city: string;
  readonly country_code: string;
  readonly contact_phone: string | null;
  readonly booking_url: string | null;
}

export interface HospitalFacilityDto {
  readonly id: string;
  readonly name: string;
  readonly accreditation: string;
  readonly has_cardiac_emergency_24_7: boolean;
  readonly has_catheterization_lab: boolean;
  readonly emergency_phone: string;
  readonly address: string;
  readonly city: string;
  readonly country_code: string;
}

export interface InsuranceGuidanceDto {
  readonly country_code: string;
  readonly regulatory_authority: string;
  readonly diagnostic_coverage_summary: string;
  readonly claims_checklist: readonly string[];
  readonly authorized_helpline: string;
}

export interface EducationalResourceDto {
  readonly id: string;
  readonly title: string;
  readonly biomarker_code: string;
  readonly summary: string;
  readonly guideline_source: string;
  readonly diet_plan_summary: string;
  readonly exercise_tips_summary: string;
  readonly lifestyle_guidance: string;
}
