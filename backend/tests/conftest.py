"""HeartXAI 2.0 - Pytest Test Configuration & Shared Fixtures.

Supports real PostgreSQL 16 integration via TEST_DATABASE_URL (Docker / CI)
with isolated in-memory SQLite (foreign keys enabled) as local fallback.
"""

import os

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  # Ensure all models register on Base.metadata
from app.core.database import Base
from app.core.security import hash_password
from app.models.user import User

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")

_engine_kwargs: dict[str, object] = {"pool_pre_ping": True}
if TEST_DATABASE_URL.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
    if TEST_DATABASE_URL == "sqlite:///:memory:":
        _engine_kwargs["poolclass"] = StaticPool

engine = create_engine(TEST_DATABASE_URL, **_engine_kwargs)

if TEST_DATABASE_URL.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def _enable_sqlite_fk(dbapi_connection, _connection_record) -> None:  # type: ignore[no-untyped-def]
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database schema for every single test function."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_patient(db_session):
    """Fixture providing a standard synthetic test patient user."""
    patient = User(
        email="patient.marcus@example.com",
        hashed_password=hash_password("MarcusPass123!"),
        full_name="Marcus Vance",
        role="PATIENT",
        country_code="US",
        clinician_status="N/A",
        is_synthetic=True,
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    return patient


@pytest.fixture
def sample_doctor(db_session):
    """Fixture providing an approved clinical cardiologist user."""
    doctor = User(
        email="dr.sarah.lin@example.com",
        hashed_password=hash_password("DoctorPass123!"),
        full_name="Dr. Sarah Lin, MD",
        role="CLINICIAN",
        country_code="US",
        clinician_status="VERIFIED",
        is_synthetic=True,
    )
    db_session.add(doctor)
    db_session.commit()
    db_session.refresh(doctor)
    return doctor


@pytest.fixture
def sample_admin(db_session):
    """Fixture providing a system administrator user."""
    admin = User(
        email="admin.elena@example.com",
        hashed_password=hash_password("AdminPass123!"),
        full_name="Elena Rostova",
        role="ADMIN",
        country_code="GB",
        clinician_status="N/A",
        is_synthetic=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin
