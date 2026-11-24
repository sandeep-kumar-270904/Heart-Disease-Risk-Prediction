"""HeartXAI 2.0 - Core Application Configuration & Fail-Closed Secret Validation."""

from __future__ import annotations

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LOCAL_DEV_SECRET_KEY = "hxai-local-dev-only-key-not-for-staging-or-production-0000000000"
_INSECURE_SECRET_MARKERS = (
    "hxai-insecure",
    "hxai-local-dev-only",
    "change-in-production",
    "change-this",
    "replace_with",
    "dev-key",
    "secret",
)


class Settings(BaseSettings):
    """Application settings and configuration parameters."""

    # Project Metadata
    PROJECT_NAME: str = "HeartXAI 2.0"
    VERSION: str = "2.0.0"
    DESCRIPTION: str = (
        "Explainable AI-Based Cardiovascular Risk Prediction and Medical Assistance Platform"
    )
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Data Safety & Governance (DEC-005: Category C strictly prohibited in MVP)
    SYNTHETIC_DATA_ONLY: bool = True

    # Security & JWT Credentials
    SECRET_KEY: str = LOCAL_DEV_SECRET_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database Persistence
    DATABASE_URL: str = "sqlite:///./heartxai_dev.db"

    # Cache & Token Rotation Store
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS Configuration
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # Clinical Machine Learning Artifacts
    MODEL_DIR: str = "app/ml/artifacts"
    ACTIVE_MODEL_VERSION: str = "v2.0.0"

    @model_validator(mode="after")
    def validate_staging_production_security(self) -> Settings:
        """Fail closed when staging/production runs without strong external secrets or safety."""
        env_normalized = self.ENVIRONMENT.strip().lower()
        is_non_local = env_normalized not in {"development", "dev", "test", "local"}
        if is_non_local:
            key = self.SECRET_KEY.strip()
            lowered = key.lower()
            if not key or len(key) < 32:
                raise ValueError(
                    "SECURITY CONFIG ERROR: SECRET_KEY must be >= 32 characters in "
                    f"ENVIRONMENT='{self.ENVIRONMENT}'."
                )
            if any(marker in lowered for marker in _INSECURE_SECRET_MARKERS):
                raise ValueError(
                    "SECURITY CONFIG ERROR: Placeholder or development default SECRET_KEY "
                    f"is prohibited in ENVIRONMENT='{self.ENVIRONMENT}'."
                )
            if self.DEBUG:
                raise ValueError(
                    "SECURITY CONFIG ERROR: DEBUG must be False in staging/production."
                )
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
