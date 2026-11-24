"""HeartXAI 2.0 - Synthetic Health & Readiness Probes."""

from datetime import UTC, datetime

import redis
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.ml.inference_service import get_inference_service

router = APIRouter(tags=["Health & Governance"])


@router.get("/health/live", status_code=status.HTTP_200_OK)
@router.get("/live", status_code=status.HTTP_200_OK, include_in_schema=False)
def liveness_probe() -> dict[str, str]:
    """Liveness probe verifying that the FastAPI process is responsive."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/health/ready", status_code=status.HTTP_200_OK)
@router.get("/ready", status_code=status.HTTP_200_OK, include_in_schema=False)
def readiness_probe(db: Session = Depends(get_db)) -> dict[str, str]:
    """Readiness probe verifying database, ML artifact, and (in non-local env) Redis connectivity."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connectivity check failed: {str(exc)}",
        ) from exc

    try:
        model_version = str(get_inference_service().artifact["model_version"])
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"ML model artifact readiness check failed: {str(exc)}",
        ) from exc

    env_normalized = settings.ENVIRONMENT.strip().lower()
    redis_status = "skipped_in_local_dev"
    if env_normalized not in {"development", "dev", "test", "local"}:
        try:
            client = redis.Redis.from_url(
                settings.REDIS_URL,
                socket_connect_timeout=1.0,
                socket_timeout=1.0,
            )
            client.ping()
            redis_status = "connected"
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Redis connectivity check failed: {str(exc)}",
            ) from exc

    return {
        "status": "ready",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "connected",
        "redis": redis_status,
        "model_version": model_version,
        "synthetic_data_only": str(settings.SYNTHETIC_DATA_ONLY).lower(),
        "timestamp": datetime.now(UTC).isoformat(),
    }
