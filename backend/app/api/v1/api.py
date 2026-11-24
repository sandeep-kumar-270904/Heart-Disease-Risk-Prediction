"""HeartXAI 2.0 - API v1 Router Aggregator."""

from fastapi import APIRouter

from app.api.v1.routes import admin, assessments, auth, consents, directory, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(assessments.router)
api_router.include_router(directory.router)
api_router.include_router(consents.router)
api_router.include_router(admin.router)
