"""HeartXAI 2.0 - Application Entry Point & ASGI Server Factory.

Production-grade FastAPI configuration with OpenAPI 3.1 documentation,
CORS security middleware, structured logging, and health probes.
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging

# Initialize structured logging
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Cross-Origin Resource Sharing (CORS) Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Format Pydantic validation errors adhering to Stripe structured error standard."""
    errors = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err["loc"] if loc != "body")
        errors.append(
            {
                "param": field,
                "code": err["type"],
                "message": err["msg"],
            }
        )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "type": "validation_error",
                "message": "Clinical input validation failed. Please check biomarker boundaries.",
                "details": errors,
            }
        },
    )


# Mount API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)
# Mount health probes at root level as well
app.include_router(api_router)


@app.get("/", tags=["Root"])
def root():
    """Root platform entry point."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "documentation": "/docs",
        "health": "/health/live",
    }
