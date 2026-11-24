"""HeartXAI 2.0 - Standardized RFC 7807 Problem Details Error Envelopes."""

from __future__ import annotations

from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import logger, request_id_ctx

ERROR_BASE_URI = "https://heartxai.org/errors"


class AppError(Exception):
    """Base domain exception serialized cleanly as RFC 7807 Problem Details."""

    def __init__(
        self,
        *,
        status_code: int,
        error_slug: str,
        title: str,
        detail: str,
        invalid_params: list[dict[str, str]] | None = None,
    ) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.error_slug = error_slug
        self.title = title
        self.detail = detail
        self.invalid_params = invalid_params


class AuthenticationError(AppError):
    """401 Unauthorized domain error."""

    def __init__(self, detail: str = "Authentication credentials are missing or invalid.") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_slug="authentication-failed",
            title="Unauthorized",
            detail=detail,
        )


class AuthorizationError(AppError):
    """403 Forbidden domain error."""

    def __init__(self, detail: str = "You do not have permission to access this resource.") -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_slug="forbidden",
            title="Forbidden",
            detail=detail,
        )


class ResourceNotFoundError(AppError):
    """404 Not Found domain error."""

    def __init__(self, detail: str = "The requested resource was not found.") -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_slug="resource-not-found",
            title="Not Found",
            detail=detail,
        )


class ConflictError(AppError):
    """409 Conflict domain error."""

    def __init__(self, detail: str = "A conflicting resource already exists.") -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_slug="conflict",
            title="Conflict",
            detail=detail,
        )


class ClinicalBoundaryError(AppError):
    """422 Clinical plausibility or non-diagnostic boundary violation."""

    def __init__(
        self,
        detail: str,
        invalid_params: list[dict[str, str]] | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_slug="clinical-boundary-violation",
            title="Unprocessable Entity",
            detail=detail,
            invalid_params=invalid_params,
        )


class ServiceUnavailableError(AppError):
    """503 Fail-closed dependency unavailability error."""

    def __init__(
        self, detail: str = "A critical backing service is temporarily unavailable."
    ) -> None:
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_slug="service-unavailable",
            title="Service Unavailable",
            detail=detail,
        )


def _get_request_id(request: Request) -> str:
    req_id = getattr(request.state, "request_id", None)
    if isinstance(req_id, str) and req_id:
        return req_id
    return request_id_ctx.get("-")


def build_problem_response(
    *,
    request: Request,
    status_code: int,
    error_slug: str,
    title: str,
    detail: str,
    invalid_params: list[dict[str, str]] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    """Construct an RFC 7807 Problem Details JSONResponse."""
    request_id = _get_request_id(request)
    body: dict[str, Any] = {
        "type": f"{ERROR_BASE_URI}/{error_slug}",
        "title": title,
        "status": status_code,
        "detail": detail,
        "instance": str(request.url.path),
        "request_id": request_id,
    }
    if invalid_params is not None:
        body["invalid_params"] = invalid_params

    response_headers = {"X-Request-ID": request_id}
    if headers:
        response_headers.update(headers)

    return JSONResponse(
        status_code=status_code,
        content=body,
        media_type="application/problem+json",
        headers=response_headers,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach global RFC 7807 exception handlers covering 401, 403, 404, 422, 500, and 503."""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return build_problem_response(
            request=request,
            status_code=exc.status_code,
            error_slug=exc.error_slug,
            title=exc.title,
            detail=exc.detail,
            invalid_params=exc.invalid_params,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        invalid_params: list[dict[str, str]] = []
        for err in exc.errors():
            field = ".".join(str(loc) for loc in err["loc"] if loc != "body")
            invalid_params.append(
                {
                    "name": field or "request",
                    "reason": err["msg"],
                }
            )
        return build_problem_response(
            request=request,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_slug="validation-failed",
            title="Unprocessable Entity",
            detail="Request input validation failed. Please check field bounds and types.",
            invalid_params=invalid_params,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        try:
            http_status = HTTPStatus(exc.status_code)
            title = http_status.phrase
        except ValueError:
            title = "HTTP Error"

        slug_map = {
            401: "authentication-failed",
            403: "forbidden",
            404: "resource-not-found",
            409: "conflict",
            422: "validation-failed",
            429: "rate-limit-exceeded",
            503: "service-unavailable",
        }
        error_slug = slug_map.get(exc.status_code, f"http-{exc.status_code}")
        detail = exc.detail if isinstance(exc.detail, str) else title
        return build_problem_response(
            request=request,
            status_code=exc.status_code,
            error_slug=error_slug,
            title=title,
            detail=detail,
            headers={k: str(v) for k, v in exc.headers.items()} if exc.headers else None,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = _get_request_id(request)
        logger.exception(
            "Unhandled server exception for path=%s request_id=%s",
            request.url.path,
            request_id,
            exc_info=exc,
        )
        return build_problem_response(
            request=request,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_slug="internal-server-error",
            title="Internal Server Error",
            detail="An unexpected internal error occurred. Reference the request_id when reporting.",
        )
