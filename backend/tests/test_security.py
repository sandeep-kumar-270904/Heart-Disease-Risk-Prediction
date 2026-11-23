"""HeartXAI 2.0 - Security & Cryptographic Primitives Unit Tests."""

from datetime import timedelta

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hashing_and_verification():
    """Verify that bcrypt hashing generates secure, verifiable salted hashes."""
    password = "SuperSecretPassword123!"
    hashed = hash_password(password)

    # Assert hash is not plaintext and has bcrypt prefix
    assert hashed != password
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")

    # Assert correct verification
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False
    assert verify_password("", hashed) is False


def test_jwt_token_lifecycle_and_claims():
    """Verify signed JWT token creation, claim preservation, and decoding."""
    user_id = "user-uuid-12345"
    role = "CLINICIAN"

    token = create_access_token(subject=user_id, role=role)
    assert isinstance(token, str)
    assert len(token) > 20

    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == user_id
    assert payload["role"] == role
    assert "exp" in payload


def test_expired_jwt_token():
    """Verify that expired JWT tokens are cleanly rejected."""
    user_id = "expired-user"
    token = create_access_token(
        subject=user_id,
        role="PATIENT",
        expires_delta=timedelta(seconds=-1),  # Expired 1 second ago
    )

    payload = decode_access_token(token)
    assert payload is None


def test_tampered_jwt_token():
    """Verify that tampered tokens fail cryptographic verification."""
    token = create_access_token(subject="patient-1", role="PATIENT")
    # Tamper with the token payload
    tampered_token = token[:-5] + "XXXXX"

    payload = decode_access_token(tampered_token)
    assert payload is None
