# HeartXAI 2.0 — Frontend API Integration & Network Architecture

**Document ID:** `HX2-FE-007`  
**Version:** `1.0.0`  
**Phase:** Phase 6 — Frontend Engineering Architecture & Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal Frontend Architect & API Integration Lead  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011, HXAI-ARCH-011  

---

## 1. Network Architecture Overview

The HeartXAI 2.0 frontend communicates with the FastAPI backend over a strict, type-safe RESTful API conforming to **OpenAPI 3.1**.

### 1.1 Core Network Directives
1. **Zero UI-Layer Network Calls:** React components and hooks never invoke `fetch` or HTTP transport primitives directly. All network interaction flows through dedicated **Domain Service Modules** (`src/features/*/services/` and `src/services/api/`).
2. **HttpOnly Cookie Transport:** Authentication tokens are managed exclusively via `HttpOnly`, `SameSite=Strict`, `Secure` cookies. The client configures `credentials: 'same-origin'` (or `'include'` in cross-domain dev).
3. **Automated CSRF Token Injection:** The API client reads the double-submit CSRF cookie (`csrf_token`) and injects it into the `X-CSRF-Token` header for all state-changing HTTP requests (`POST`, `PUT`, `PATCH`, `DELETE`).
4. **Deterministic Error Normalization:** All server responses, network timeouts, and JSON parse failures are normalized into a unified, typed `ApiError` class before reaching UI handlers.

```
┌────────────────────────────────────────────────────────────────────────┐
│                      NETWORK DATA FLOW PIPELINE                        │
├────────────────────────────────────────────────────────────────────────┤
│ [ React Feature Component ]                                            │
│            │                                                           │
│            ▼ (Invokes Query / Mutation Hook)                           │
│ [ TanStack Query Hook (e.g., useAssessmentDetail) ]                    │
│            │                                                           │
│            ▼ (Calls Domain Service Method)                             │
│ [ Domain Service (e.g., assessmentService.getById) ]                   │
│            │                                                           │
│            ▼ (Dispatches Request with AbortSignal & CSRF)              │
│ [ Central API Client (src/services/api/client.ts) ]                    │
│            │                                                           │
│            ▼ (Fetch Request over TLS)                                  │
│ [ FastAPI Backend Gateway (/api/v1/...) ]                              │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Central API Client Specification (`src/services/api/client.ts`)

### 2.1 Base Configuration & Client Initialization
```typescript
import ky, { type KyInstance, type Options } from 'ky';
import { env } from '@/config/env';
import { normalizeApiError } from './errors';

// Helper to extract CSRF token from document.cookie
const getCsrfToken = (): string | undefined => {
  return document.cookie
    .split('; ')
    .find((row) => row.startsWith('csrf_token='))
    ?.split('=')[1];
};

export const apiClient: KyInstance = ky.create({
  prefixUrl: env.VITE_API_BASE_URL, // e.g., 'https://api.heartxai.org/api/v1'
  timeout: 10000, // 10s default timeout
  credentials: 'same-origin',
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
  },
  hooks: {
    beforeRequest: [
      (request) => {
        // Inject CSRF token for state-changing requests
        if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(request.method)) {
          const csrf = getCsrfToken();
          if (csrf) {
            request.headers.set('X-CSRF-Token', csrf);
          }
        }
      },
    ],
    beforeRetry: [
      async ({ request, options, error, retryCount }) => {
        // Handle 401 token refresh on retry attempt 1
        if (error.response?.status === 401 && retryCount === 1) {
          try {
            await ky.post(`${env.VITE_API_BASE_URL}/auth/refresh`, {
              credentials: 'same-origin',
            });
          } catch {
            // Refresh failed; redirect to login
            window.location.href = `/auth/login?session_expired=true`;
          }
        }
      },
    ],
    afterResponse: [
      async (_request, _options, response) => {
        if (!response.ok) {
          throw await normalizeApiError(response);
        }
      },
    ],
  },
  retry: {
    limit: 2,
    methods: ['get', 'put', 'head', 'options'], // Only retry idempotent requests
    statusCodes: [408, 413, 429, 502, 503, 504],
    backoffLimit: 3000,
  },
});
```

---

## 3. Typed Error Normalization Model

In accordance with `docs/API_ARCHITECTURE.md`, HeartXAI 2.0 adopts the **Stripe-Style Error Envelope**.

### 3.1 Standard Error Interface
```typescript
export interface ApiErrorDetail {
  param: string;
  code: string;
  message: string;
}

export interface ApiErrorEnvelope {
  error: {
    type: 'validation_error' | 'authentication_error' | 'authorization_error' | 
          'resource_not_found' | 'rate_limit_exceeded' | 'clinical_boundary_error' | 
          'internal_server_error';
    code: string;
    param?: string;
    message: string;
    details?: ApiErrorDetail[];
  };
}

export class ApiError extends Error {
  public readonly status: number;
  public readonly type: string;
  public readonly code: string;
  public readonly param?: string;
  public readonly details?: ApiErrorDetail[];

  constructor(status: number, envelope: ApiErrorEnvelope) {
    super(envelope.error.message);
    this.name = 'ApiError';
    this.status = status;
    this.type = envelope.error.type;
    this.code = envelope.error.code;
    this.param = envelope.error.param;
    this.details = envelope.error.details;
  }
}
```

---

## 4. Request Cancellation & AbortController Architecture

To prevent memory leaks, race conditions, and wasted bandwidth when a user navigates away or types rapidly:
- TanStack Query automatically provides an `AbortSignal` inside `queryFn`.
- Domain services explicitly propagate this signal into the API client:

```typescript
export const assessmentService = {
  getById: async (id: string, signal?: AbortSignal): Promise<AssessmentDetailDto> => {
    return apiClient
      .get(`assessments/${id}`, { signal })
      .json<AssessmentDetailDto>();
  },

  searchDoctors: async (
    params: DoctorSearchParams, 
    signal?: AbortSignal
  ): Promise<PaginatedResponse<DoctorProfileDto>> => {
    return apiClient
      .get('directory/doctors', {
        searchParams: params as Record<string, string | number | boolean>,
        signal,
      })
      .json<PaginatedResponse<DoctorProfileDto>>();
  },
};
```

---

## 5. File Upload & Binary Report Download Handling

### 5.1 Clinician Credential Document Upload
- Verification documents (PDF medical degree, license scan) are sent via `multipart/form-data`:
```typescript
export const clinicianService = {
  uploadCredentials: async (formData: FormData): Promise<VerificationUploadResponse> => {
    return apiClient
      .post('clinician/verification/documents', {
        body: formData,
        headers: {
          // Ky automatically omits Content-Type so browser sets boundary multipart
          'Content-Type': undefined,
        },
        timeout: 30000, // 30s timeout for large uploads
      })
      .json<VerificationUploadResponse>();
  },
};
```

### 5.2 Clinical Consultation Summary PDF Download
- When generating the physician discussion aid report:
```typescript
export const reportService = {
  downloadPdf: async (assessmentId: string): Promise<void> => {
    const blob = await apiClient
      .get(`reports/assessments/${assessmentId}/pdf`, {
        headers: { Accept: 'application/pdf' },
        timeout: 25000,
      })
      .blob();

    // Trigger deterministic client-side file save
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `HeartXAI-Clinical-Report-${assessmentId.slice(0, 8)}.pdf`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
};
```
