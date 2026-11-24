/**
 * HeartXAI 2.0 - Authentication & User Profile Types
 * Mirrors backend/app/schemas/auth.py with 100% field & nullability parity.
 */

export type UserRole = 'PATIENT' | 'CLINICIAN' | 'ADMINISTRATOR';

export type ClinicianStatus = 'N/A' | 'PENDING' | 'VERIFIED' | 'REJECTED';

export type UnitSystem = 'metric' | 'us_customary';

export type BiologicalSex = 'female' | 'male' | 'other';

export interface RegisterRequest {
  readonly email: string;
  readonly password: string;
  readonly full_name: string;
  readonly country_code: string;
  readonly consent_given: true;
}

export interface LoginRequest {
  readonly email: string;
  readonly password: string;
}

export interface TokenResponse {
  readonly access_token: string;
  readonly token_type: 'bearer';
  readonly expires_in: number;
}

export interface UserProfileResponse {
  readonly id: string;
  readonly email: string;
  readonly full_name: string;
  readonly role: UserRole;
  readonly country_code: string;
  readonly clinician_status: ClinicianStatus | null;
  readonly created_at: string;
}

export interface PatientProfileUpdateDto {
  readonly preferred_units: UnitSystem;
  readonly date_of_birth: string | null;
  readonly biological_sex: BiologicalSex | null;
  readonly emergency_contact_name: string | null;
  readonly emergency_contact_phone: string | null;
}
