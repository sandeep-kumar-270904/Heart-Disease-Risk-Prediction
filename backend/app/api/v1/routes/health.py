"""HeartXAI 2.0 - Synthetic Health & Readiness Probes."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

router = APIRouter(tags=["Health & Governance"])


@router.get("/health/live", status_code=status.HTTP_200_OK)
def liveness_probe():
    """Liveness probe verifying that the FastAPI process is responsive."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/health/ready", status_code=status.HTTP_200_OK)
def readiness_probe(db: Session = Depends(get_db)):
    """Readiness probe verifying operational database connectivity."""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "database": "connected",
            "timestamp": datetime.now(UTC).isoformat(),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connectivity check failed: {str(exc)}",
        ) from exc
