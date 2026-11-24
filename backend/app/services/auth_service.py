"""HeartXAI 2.0 - Identity Management, Registration, and Authentication Service."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AuthenticationError, ClinicalBoundaryError, ConflictError
from app.core.redis_client import TokenStoreBackend
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.models.base import generate_uuidv7
from app.models.user import PatientProfile, User
from app.schemas.auth import ALLOWED_SYNTHETIC_DOMAINS, RegisterRequest


def _normalize_schema_role(db_role: str) -> str:
    if db_role == "ADMIN":
        return "ADMINISTRATOR"
    return db_role


def register_user(db: Session, payload: RegisterRequest) -> User:
    """Register a controlled synthetic-demo persona account with server-enforced boundaries."""
    if not settings.SYNTHETIC_DATA_ONLY:
        raise ClinicalBoundaryError(
            "Platform is disabled: SYNTHETIC_DATA_ONLY must be true in MVP (DEC-005)."
        )

    normalized_email = payload.email.lower()
    domain = normalized_email.rsplit("@", 1)[-1]
    if domain not in ALLOWED_SYNTHETIC_DOMAINS:
        raise ClinicalBoundaryError(
            "Registration restricted to authorized RFC 2606 synthetic domains "
            "(@example.com, @example.org, @example.net)."
        )

    existing = db.scalar(select(User).where(User.email == normalized_email))
    if existing is not None:
        raise ConflictError("An account with this email address already exists.")

    user = User(
        email=normalized_email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name.strip(),
        role="PATIENT",
        country_code=payload.country_code,
        clinician_status="N/A",
        is_active=True,
        is_synthetic=True,
    )
    db.add(user)
    db.flush()

    default_units = "US_STANDARD" if payload.country_code == "US" else "METRIC"
    profile = PatientProfile(
        patient_id=user.id,
        preferred_units=default_units,
    )
    db.add(profile)
    db.commit()
    db.refresh(user)
    return user


def login_user(
    db: Session,
    email: str,
    password: str,
    token_store: TokenStoreBackend,
) -> tuple[User, str, str]:
    """Authenticate credentials via Argon2id and initialize a Redis refresh token family."""
    user = db.scalar(select(User).where(User.email == email.lower()))
    if user is None or not verify_password(password, str(user.hashed_password)):
        raise AuthenticationError("Invalid email or password.")
    if not user.is_active:
        raise AuthenticationError("Account is inactive or suspended.")

    user.last_login_at = datetime.now(UTC)  # type: ignore[assignment]
    db.commit()

    family_id = generate_uuidv7()
    refresh_jti = generate_uuidv7()
    refresh_ttl_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400

    # Fail closed if Redis cannot persist the token family
    token_store.register_family(family_id, refresh_jti, refresh_ttl_seconds)

    role_claim = _normalize_schema_role(str(user.role))
    access_token = create_access_token(
        subject=user.id,
        role=role_claim,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(
        subject=user.id,
        role=role_claim,
        family_id=family_id,
        jti=refresh_jti,
    )
    return user, access_token, refresh_token


def refresh_user_session(
    db: Session,
    raw_refresh_token: str,
    token_store: TokenStoreBackend,
) -> tuple[str, str]:
    """Rotate refresh token family in Redis; replay triggers full family invalidation."""
    payload = decode_refresh_token(raw_refresh_token)
    if payload is None:
        raise AuthenticationError("Refresh token is missing, malformed, or expired.")

    user_id = str(payload["sub"])
    family_id = str(payload["family_id"])
    presented_jti = str(payload["jti"])

    user = db.scalar(select(User).where(User.id == user_id))
    if user is None or not user.is_active:
        token_store.invalidate_family(family_id)
        raise AuthenticationError("User account is no longer active.")

    new_refresh_jti = generate_uuidv7()
    refresh_ttl_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
    token_store.rotate_family_token(
        family_id=family_id,
        presented_jti=presented_jti,
        new_jti=new_refresh_jti,
        ttl_seconds=refresh_ttl_seconds,
    )

    role_claim = _normalize_schema_role(str(user.role))
    new_access_token = create_access_token(
        subject=user.id,
        role=role_claim,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    new_refresh_token = create_refresh_token(
        subject=user.id,
        role=role_claim,
        family_id=family_id,
        jti=new_refresh_jti,
    )
    return new_access_token, new_refresh_token
