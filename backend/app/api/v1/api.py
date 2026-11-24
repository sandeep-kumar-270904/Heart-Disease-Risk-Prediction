"""HeartXAI 2.0 - API v1 Router Aggregator."""

from fastapi import APIRouter

from app.api.v1.routes import assessments, auth, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(assessments.router)
