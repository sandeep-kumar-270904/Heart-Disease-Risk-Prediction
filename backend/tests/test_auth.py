"""HeartXAI 2.0 - Authentication, Argon2id, Token Family Rotation & Fail-Closed Tests."""

from datetime import timedelta

from fastapi.testclient import TestClient
from redis.exceptions import ConnectionError as RedisConnectionError

from app.core.database import get_db
from app.core.redis_client import RedisTokenStore, get_token_store
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.main import app


class InMemoryTokenStore:
    """Deterministic in-memory Redis token store test double for unit tests."""

    def __init__(self) -> None:
        self.families: dict[str, str] = {}
        self.blacklist: set[str] = set()

    def register_family(self, family_id: str, jti: str, ttl_seconds: int) -> None:
        self.families[family_id] = jti

    def rotate_family_token(
        self, family_id: str, presented_jti: str, new_jti: str, ttl_seconds: int
    ) -> None:
        from app.core.errors import AuthenticationError

        active = self.families.get(family_id)
        if active is None:
            raise AuthenticationError("Refresh session expired or revoked.")
        if active != presented_jti:
            # Replay attack -> invalidate entire family
            self.families.pop(family_id, None)
            raise AuthenticationError(
                "Refresh token reuse detected. Session token family invalidated."
            )
        self.families[family_id] = new_jti

    def invalidate_family(self, family_id: str) -> None:
        self.families.pop(family_id, None)

    def blacklist_access_jti(self, jti: str, ttl_seconds: int) -> None:
        self.blacklist.add(jti)

    def is_access_jti_blacklisted(self, jti: str) -> bool:
        return jti in self.blacklist


def test_argon2id_hashing_and_verification() -> None:
    """Verify RFC 9106 Argon2id password hashing and mismatch rejection."""
    hashed = hash_password("StrongCardioPass#2026")
    assert hashed.startswith("$argon2id$")
    assert verify_password("StrongCardioPass#2026", hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_access_token_expiration_rejected() -> None:
    """Verify expired JWT access tokens are rejected cleanly."""
    expired = create_access_token(
        subject="user-1",
        role="PATIENT",
        expires_delta=timedelta(seconds=-5),
    )
    assert decode_access_token(expired) is None


def test_register_login_refresh_replay_detection_and_logout(db_session) -> None:
    """Verify full auth lifecycle, token family rotation, replay invalidation, and logout."""
    store = InMemoryTokenStore()
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_token_store] = lambda: store

    try:
        client = TestClient(app)

        # 1. Register new synthetic patient
        reg_resp = client.post(
            "/api/v1/auth/register",
            json={
                "email": "alice.synth@example.com",
                "password": "AliceSecurePassword!2026",
                "full_name": "Alice Synthetic",
                "country_code": "US",
                "consent_given": True,
            },
        )
        assert reg_resp.status_code == 201
        assert reg_resp.json()["role"] == "PATIENT"

        # Duplicate registration rejected with 409 Conflict
        dup_resp = client.post(
            "/api/v1/auth/register",
            json={
                "email": "alice.synth@example.com",
                "password": "AliceSecurePassword!2026",
                "full_name": "Alice Synthetic",
                "country_code": "US",
                "consent_given": True,
            },
        )
        assert dup_resp.status_code == 409

        # 2. Login -> returns access JWT + HttpOnly refresh cookie
        login_resp = client.post(
            "/api/v1/auth/login",
            json={
                "email": "alice.synth@example.com",
                "password": "AliceSecurePassword!2026",
            },
        )
        assert login_resp.status_code == 200
        access_1 = login_resp.json()["access_token"]
        cookie_1 = login_resp.cookies.get("hx_refresh_token")
        assert cookie_1 is not None

        # 3. Authenticated /me request succeeds
        me_resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_1}"},
        )
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == "alice.synth@example.com"

        # 4. Valid refresh rotates token family and issues cookie_2
        refresh_resp = client.post(
            "/api/v1/auth/refresh",
            cookies={"hx_refresh_token": cookie_1},
        )
        assert refresh_resp.status_code == 200
        access_2 = refresh_resp.json()["access_token"]
        cookie_2 = refresh_resp.cookies.get("hx_refresh_token")
        assert cookie_2 is not None and cookie_2 != cookie_1

        # 5. Replay attack: reusing old cookie_1 MUST return 401 AND invalidate entire family!
        replay_resp = client.post(
            "/api/v1/auth/refresh",
            cookies={"hx_refresh_token": cookie_1},
        )
        assert replay_resp.status_code == 401
        assert "reuse detected" in replay_resp.json()["detail"].lower()

        # Even newest valid cookie_2 is now dead because family was wiped!
        post_replay_resp = client.post(
            "/api/v1/auth/refresh",
            cookies={"hx_refresh_token": cookie_2},
        )
        assert post_replay_resp.status_code == 401

        # 6. Logout blacklists current access JWT
        logout_resp = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_2}"},
        )
        assert logout_resp.status_code == 200

        # Blacklisted access_2 is immediately rejected
        revoked_me = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_2}"},
        )
        assert revoked_me.status_code == 401
    finally:
        app.dependency_overrides.clear()


def test_rbac_enforcement_rejects_wrong_role(db_session, sample_doctor) -> None:
    """Verify require_role(PATIENT) rejects CLINICIAN with 403 Forbidden."""
    store = InMemoryTokenStore()
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_token_store] = lambda: store
    try:
        client = TestClient(app)
        doctor_jwt = create_access_token(subject=sample_doctor.id, role="CLINICIAN")
        resp = client.get(
            "/api/v1/auth/patient-only-check",
            headers={"Authorization": f"Bearer {doctor_jwt}"},
        )
        assert resp.status_code == 403
        assert resp.json()["title"] == "Forbidden"
    finally:
        app.dependency_overrides.clear()


def test_redis_fail_closed_when_unavailable(db_session, sample_patient) -> None:
    """Verify Redis unavailability triggers 503 Service Unavailable (fail-closed, ADR-005)."""
    down_store = RedisTokenStore(redis_url="redis://127.0.0.1:6399/0", max_retries=0)

    class _DownClient:
        def setex(self, *args, **kwargs):
            raise RedisConnectionError("Simulated Redis outage")

        def get(self, *args, **kwargs):
            raise RedisConnectionError("Simulated Redis outage")

        def exists(self, *args, **kwargs):
            raise RedisConnectionError("Simulated Redis outage")

        def delete(self, *args, **kwargs):
            raise RedisConnectionError("Simulated Redis outage")

    down_store._client = _DownClient()  # type: ignore[assignment]

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_token_store] = lambda: down_store
    try:
        client = TestClient(app)
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "patient.marcus@example.com", "password": "MarcusPass123!"},
        )
        assert login_resp.status_code == 503
        assert login_resp.json()["title"] == "Service Unavailable"

        patient_jwt = create_access_token(subject=sample_patient.id, role="PATIENT")
        me_resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {patient_jwt}"},
        )
        assert me_resp.status_code == 503
    finally:
        app.dependency_overrides.clear()
