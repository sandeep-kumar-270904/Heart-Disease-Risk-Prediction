# HeartXAI 2.0 — Backend Error Handling & Exception Architecture

**Document ID:** `HX2-BE-010`  
**Version:** `1.0.0`  
**Phase:** Phase 7 — Backend Engineering Architecture & API Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Application Security Architect & Backend Quality Lead  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-005, HXAI-ARCH-011  

---

## 1. Error Handling Philosophy & Security Standards

In healthcare software, error responses must satisfy two competing demands:
1. **Developer & Client Machine Readability:** Clear, structured, typed error codes enabling the frontend to highlight specific form fields and guide user recovery.
2. **Defensive Information Redaction:** Zero exposure of stack traces, raw SQL queries, database table structures, file system paths, or internal server secrets to the client.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   ERROR NORMALIZATION PIPELINE                         │
├────────────────────────────────────────────────────────────────────────┤
│ Unhandled Exception (Database, ML, Validation, Security)               │
│       │                                                                │
│       ▼                                                                │
│ [ Global FastAPI Exception Handler (error_handler.py) ]                │
│       │                                                                │
│       ├── 1. Capture Correlation ID from RequestContext                │
│       ├── 2. Log full stack trace & context securely to internal logs  │
│       ├── 3. Map exception to canonical HTTP status & Stripe-style code│
│       ├── 4. Redact sensitive PII and infrastructure details           │
│       └── 5. Return standardized JSON ApiErrorEnvelope                 │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Standardized Error Response Envelope (Stripe Model)

All non-2xx HTTP responses emitted by HeartXAI 2.0 conform strictly to the following schema:

```json
{
  "error": {
    "type": "validation_error",
    "code": "parameter_out_of_range",
    "param": "resting_bp",
    "message": "Resting systolic blood pressure must be between 70 and 240 mmHg.",
    "details": [
      {
        "param": "resting_bp",
        "code": "greater_than_equal",
        "message": "Input should be greater than or equal to 70"
      }
    ]
  }
}
```

### 2.1 Standard Error Types & HTTP Status Codes

| Error Type (`error.type`) | HTTP Status | Typical Occurrence / Scenario | Client-Facing Message Policy |
| :--- | :---: | :--- | :--- |
| `validation_error` | `400` | Input fails Pydantic schema validation or range bounds. | Specific parameter name and permissible range. |
| `authentication_error` | `401` | Token missing, expired, invalid signature, bad credentials. | *"Invalid email or password"* / *"Session expired"*. |
| `authorization_error` | `403` | User lacks role scope or active patient consent grant. | Generic forbidden message; never reveals resource existence. |
| `resource_not_found` | `404` | Requested ID does not exist or user lacks access. | *"Requested assessment record not found."* |
| `conflict_error` | `409` | Email already registered or duplicate active grant. | Informative conflict description without PII leakage. |
| `rate_limit_exceeded` | `429` | Request threshold breached (e.g., auth brute-force). | *"Too many requests. Please wait before retrying."* |
| `clinical_boundary_error`| `422` | Modification of immutable feature (Age) in simulation. | Specific clinical constraint explanation. |
| `internal_server_error` | `500` | Unhandled database fault, ML runner crash, or syntax error. | *"An unexpected error occurred. Reference ID: {correlation_id}"*. |

---

## 3. Domain Exception Hierarchy (`app/core/exceptions.py`)

```python
class HeartXAIException(Exception):
    def __init__(self, message: str, code: str = "internal_error", param: str = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.param = param

class EntityNotFoundException(HeartXAIException):
    def __init__(self, entity_name: str, entity_id: str):
        super().__init__(
            message=f"{entity_name} with identifier '{entity_id}' was not found.",
            code="resource_not_found"
        )
        self.status_code = 404

class AuthenticationException(HeartXAIException):
    def __init__(self, message: str = "Invalid credentials or session expired."):
        super().__init__(message=message, code="invalid_credentials")
        self.status_code = 401

class AuthorizationException(HeartXAIException):
    def __init__(self, message: str = "You do not have permission to access this resource."):
        super().__init__(message=message, code="access_denied")
        self.status_code = 403

class ClinicalBoundaryException(HeartXAIException):
    def __init__(self, message: str, param: str = None):
        super().__init__(message=message, code="clinical_boundary_violation", param=param)
        self.status_code = 422
```

---

## 4. Global Exception Handler Implementation

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.logging import get_logger

logger = get_logger(__name__)

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    
    # Handle known domain exceptions
    if isinstance(exc, HeartXAIException):
        logger.warning(
            "domain_exception_raised",
            code=exc.code,
            message=exc.message,
            correlation_id=correlation_id
        )
        return JSONResponse(
            status_code=getattr(exc, "status_code", 400),
            content={
                "error": {
                    "type": exc.code,
                    "code": exc.code,
                    "param": exc.param,
                    "message": exc.message
                }
            }
        )

    # Handle Pydantic request validation errors
    if isinstance(exc, RequestValidationError):
        details = [
            {
                "param": ".".join(str(loc) for loc in err["loc"] if loc != "body"),
                "code": err["type"],
                "message": err["msg"]
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "type": "validation_error",
                    "code": "invalid_request_payload",
                    "message": "Input validation failed. Please check field requirements.",
                    "details": details
                }
            }
        )

    # Unhandled Internal Server Errors (500) - Redact all internal details
    logger.error(
        "unhandled_server_exception",
        exc_info=exc,
        correlation_id=correlation_id,
        path=request.url.path
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "internal_server_error",
                "code": "unexpected_error",
                "message": f"An unexpected system fault occurred. Please quote correlation ID: {correlation_id}"
            }
        }
    )
```

---

## 5. Security Redaction & Anti-Enumeration Rules

1. **Anti-Enumeration on Auth Endpoints:** Both unregistered emails and wrong passwords on `POST /auth/login` return identical `401 Unauthorized` responses: *"Invalid email or password"*, preventing attacker email enumeration.
2. **Anti-Enumeration on Cross-Patient Queries:** When Patient A attempts to view Patient B's assessment via `GET /api/v1/assessments/:bId`, the API returns `404 Not Found` rather than `403 Forbidden`, preventing Patient A from determining whether `:bId` exists in the system.
3. **Database Error Masking:** SQLAlchemy `IntegrityError` or `DBAPIError` exceptions are caught by repository wrappers and re-emitted as generic `ConflictException` or `InternalServerException`. Raw SQL strings and constraint names are never forwarded to the client.
