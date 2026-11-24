"""HeartXAI 2.0 - FastAPI Authentication & RBAC Dependencies."""

from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import AuthenticationError, AuthorizationError
from app.core.redis_client import TokenStoreBackend, get_token_store
from app.core.security import decode_access_token
from app.models.user import User

_bearer_scheme = HTTPBearer(auto_error=False)


def normalize_role_name(role: str) -> str:
    """Normalize legacy ADMIN role strings to canonical ADMINISTRATOR."""
    return "ADMINISTRATOR" if role == "ADMIN" else role


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
    token_store: TokenStoreBackend = Depends(get_token_store),
) -> User:
    """Validate Bearer JWT access token and verify it is not revoked in Redis."""
    if credentials is None or not credentials.credentials:
        raise AuthenticationError("Missing bearer authentication token.")

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise AuthenticationError("Invalid or expired access token.")

    jti = payload.get("jti")
    if isinstance(jti, str) and jti and token_store.is_access_jti_blacklisted(jti):
        raise AuthenticationError("Access token has been revoked.")

    user_id = payload.get("sub")
    if not isinstance(user_id, str) or not user_id:
        raise AuthenticationError("Malformed authentication token payload.")

    user = db.scalar(select(User).where(User.id == user_id))
    if user is None or not user.is_active:
        raise AuthenticationError("Authenticated user account is missing or suspended.")

    return user


def require_role(*allowed_roles: str) -> Callable[[User], User]:
    """Dependency factory enforcing strict Role-Based Access Control (RBAC)."""
    normalized_allowed = {normalize_role_name(role) for role in allowed_roles}

    def _checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = normalize_role_name(str(current_user.role))
        if user_role not in normalized_allowed:
            raise AuthorizationError(
                f"Role '{user_role}' is not authorized to access this endpoint."
            )
        return current_user

    return _checker
