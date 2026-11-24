/**
 * HeartXAI 2.0 - Standardized API Error Envelopes
 * Mirrors backend/app/schemas/base.py with 100% field & nullability parity.
 */

export type ErrorType =
  | 'validation_error'
  | 'authentication_error'
  | 'authorization_error'
  | 'resource_not_found'
  | 'conflict_error'
  | 'rate_limit_exceeded'
  | 'clinical_boundary_error'
  | 'internal_server_error';

export interface ApiErrorDetail {
  readonly param: string | null;
  readonly code: string;
  readonly message: string;
}

export interface ApiErrorBody {
  readonly type: ErrorType;
  readonly code: string;
  readonly param: string | null;
  readonly message: string;
  readonly details: readonly ApiErrorDetail[] | null;
}

export interface ApiErrorEnvelope {
  readonly error: ApiErrorBody;
}
