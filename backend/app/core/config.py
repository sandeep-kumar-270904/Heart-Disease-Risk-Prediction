"""HeartXAI 2.0 - Core Application Configuration.

Loads environment variables with Pydantic Settings, providing strict typing,
default development values, and production overrides.
"""

from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings and configuration parameters."""

    # Project Metadata
    PROJECT_NAME: str = "HeartXAI 2.0"
    VERSION: str = "2.0.0"
    DESCRIPTION: str = "Explainable AI-Based Cardiovascular Risk Prediction and Medical Assistance Platform"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security & JWT Credentials
    SECRET_KEY: str = "hxai-insecure-dev-key-change-in-production-0123456789abcdef0123456789"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database Persistence
    # Defaults to local SQLite for frictionless local development and unit tests;
    # automatically overridden by DATABASE_URL (PostgreSQL) in production / Docker.
    DATABASE_URL: str = "sqlite:///./heartxai_dev.db"

    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # Clinical Machine Learning Artifacts
    MODEL_DIR: str = "app/ml/artifacts"
    ACTIVE_MODEL_VERSION: str = "v2.0.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
