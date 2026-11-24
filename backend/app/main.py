"""HeartXAI 2.0 - Application Entry Point & ASGI Server Factory.

Production-grade FastAPI configuration with OpenAPI 3.1 documentation,
CORS security middleware, correlation request_id middleware, structured JSON logging,
RFC 7807 Problem Details exception handlers, and health probes.
"""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.api.v1.routes.health import router as health_router
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import logger, request_id_ctx, setup_logging
from app.models.base import generate_uuidv7

# Initialize structured JSON logging
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.middleware("http")
async def correlation_id_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Propagate or assign a unique correlation request_id and emit structured access logs."""
    incoming_id = request.headers.get("X-Request-ID")
    req_id = (
        incoming_id.strip() if incoming_id and incoming_id.strip() else f"req_{generate_uuidv7()}"
    )
    request.state.request_id = req_id
    token = request_id_ctx.set(req_id)
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    finally:
        duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        request_id_ctx.reset(token)

    response.headers["X-Request-ID"] = req_id
    logger.info(
        "HTTP request completed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    return response


# Cross-Origin Resource Sharing (CORS) Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

# Register global RFC 7807 Problem Details handlers
register_exception_handlers(app)

# Mount canonical versioned API (/api/v1/*) and root health probes ONLY (no duplicate unversioned API)
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(health_router)


@app.get("/", tags=["Root"])
def root() -> dict[str, str]:
    """Root platform entry point."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "documentation": "/docs",
        "health": "/health/live",
        "synthetic_data_only": str(settings.SYNTHETIC_DATA_ONLY).lower(),
    }
