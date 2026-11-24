"""HeartXAI 2.0 - Authentication & Session Lifecycle Endpoints."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import cast

from fastapi import APIRouter, Cookie, Depends, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user, normalize_role_name, require_role
from app.core.config import settings
from app.core.database import get_db
from app.core.errors import AuthenticationError
from app.core.redis_client import TokenStoreBackend, get_token_store
from app.core.security import decode_access_token, decode_refresh_token
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserProfileResponse,
)
from app.services.auth_service import login_user, refresh_user_session, register_user

router = APIRouter(prefix="/auth", tags=["Authentication & Sessions"])
_optional_bearer = HTTPBearer(auto_error=False)
REFRESH_COOKIE_NAME = "hx_refresh_token"


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=settings.ENVIRONMENT in {"staging", "production"},
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/api/v1/auth",
    )


def _to_user_profile(user: User) -> UserProfileResponse:
    raw_status = str(user.clinician_status or "N/A")
    mapped_status = (
        None
        if raw_status == "N/A"
        else ("PENDING" if raw_status == "PENDING_VERIFICATION" else raw_status)
    )
    return UserProfileResponse(
        id=str(user.id),
        email=str(user.email),
        full_name=str(user.full_name),
        role=normalize_role_name(str(user.role)),  # type: ignore[arg-type]
        country_code=str(getattr(user, "country_code", "US")),
        clinician_status=mapped_status,  # type: ignore[arg-type]
        created_at=cast(datetime, user.created_at),
    )


@router.post(
    "/register",
    response_model=UserProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
) -> UserProfileResponse:
    """Register a new synthetic-only patient user with Argon2id password hashing."""
    user = register_user(db, payload)
    return _to_user_profile(user)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
    token_store: TokenStoreBackend = Depends(get_token_store),
) -> TokenResponse:
    """Authenticate user, return short-lived access JWT, and issue HttpOnly refresh cookie."""
    _, access_token, refresh_token = login_user(db, payload.email, payload.password, token_store)
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def refresh_session(
    request: Request,
    response: Response,
    hx_refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
    token_store: TokenStoreBackend = Depends(get_token_store),
) -> TokenResponse:
    """Rotate HttpOnly refresh cookie via Redis token family; detects replay attacks."""
    raw_token = hx_refresh_token or request.cookies.get(REFRESH_COOKIE_NAME)
    if not raw_token:
        raise AuthenticationError("Refresh cookie is missing.")

    new_access_token, new_refresh_token = refresh_user_session(db, raw_token, token_store)
    _set_refresh_cookie(response, new_refresh_token)
    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    response: Response,
    hx_refresh_token: str | None = Cookie(default=None),
    credentials: HTTPAuthorizationCredentials | None = Depends(_optional_bearer),
    token_store: TokenStoreBackend = Depends(get_token_store),
) -> dict[str, str]:
    """Revoke current access token JTI and invalidate refresh token family in Redis."""
    if hx_refresh_token:
        refresh_payload = decode_refresh_token(hx_refresh_token)
        if refresh_payload and refresh_payload.get("family_id"):
            token_store.invalidate_family(str(refresh_payload["family_id"]))

    if credentials and credentials.credentials:
        access_payload = decode_access_token(credentials.credentials)
        if access_payload and access_payload.get("jti"):
            exp_ts = int(access_payload.get("exp", 0))
            ttl = max(exp_ts - int(datetime.now(UTC).timestamp()), 1)
            token_store.blacklist_access_jti(str(access_payload["jti"]), ttl)

    response.delete_cookie(key=REFRESH_COOKIE_NAME, path="/api/v1/auth")
    return {"status": "logged_out"}


@router.get("/me", response_model=UserProfileResponse, status_code=status.HTTP_200_OK)
def get_me(current_user: User = Depends(get_current_user)) -> UserProfileResponse:
    """Return authenticated user profile."""
    return _to_user_profile(current_user)


@router.get(
    "/patient-only-check",
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
def patient_role_probe(
    current_user: User = Depends(require_role("PATIENT")),
) -> dict[str, str]:
    """Internal RBAC verification endpoint for PATIENT role."""
    return {"user_id": str(current_user.id), "role": str(current_user.role)}
