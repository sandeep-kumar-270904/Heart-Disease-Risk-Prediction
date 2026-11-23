"""HeartXAI 2.0 - Pytest Test Configuration & Shared Fixtures.

Provides isolated test database sessions and pre-configured test actors.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.security import hash_password
from app.models.user import User

# In-memory SQLite database dedicated to unit testing
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database schema for every single test function."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_patient(db_session):
    """Fixture providing a standard test patient user."""
    patient = User(
        email="patient.marcus@example.com",
        hashed_password=hash_password("MarcusPass123!"),
        full_name="Marcus Vance",
        role="PATIENT",
        clinician_status="N/A",
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
        clinician_status="VERIFIED",
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
        clinician_status="N/A",
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin
