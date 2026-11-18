# HeartXAI 2.0 — Database Integration Design & Persistence Architecture

**Document ID:** `HX2-BE-009`  
**Version:** `1.0.0`  
**Phase:** Phase 7 — Backend Engineering Architecture & API Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Lead Database Architect & Principal Backend Engineer  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-004, ADR-006, HXAI-ARCH-010  

---

## 1. Persistence Philosophy & PostgreSQL 16 Standard

HeartXAI 2.0 uses **PostgreSQL 16** as its authoritative production relational database engine. 

### 1.1 Non-Negotiable Database Tenets
1. **Relational Integrity by Default:** Strict foreign key constraints with explicit delete rules (`RESTRICT` on critical audit/user references; `CASCADE` on child telemetry like SHAP vectors) prevent orphaned records.
2. **Asynchronous I/O via Asyncpg:** All database transactions run asynchronously via SQLAlchemy 2.0's `AsyncSession` using `asyncpg`.
3. **No Database Operations in Route Controllers:** All queries are encapsulated behind typed domain repositories.
4. **PostgreSQL Parity Warning:** As ratified in ADR-006, SQLite is permitted only as a local, qualified in-memory test runner. All integration, concurrency, and security testing **must run against a real PostgreSQL 16 instance**.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   DATABASE PERSISTENCE ARCHITECTURE                    │
├────────────────────────────────────────────────────────────────────────┤
│ FastAPI Request ──► AsyncSession (Dependency Injection: get_db)       │
│                           │                                            │
│                           ▼                                            │
│           [ Unit of Work (UnitOfWork Context) ]                        │
│                           │                                            │
│       ┌───────────────────┼───────────────────┐                        │
│       ▼                   ▼                   ▼                        │
│ [ AssessmentRepo ]  [ InferenceRepo ]   [ AuditLogRepo ]               │
│       │                   │                   │                        │
│       └───────────────────┼───────────────────┘                        │
│                           ▼                                            │
│           SQLAlchemy 2.0 Async Engine (asyncpg)                        │
│                           │                                            │
│                           ▼ (Connection Pool: 20 base, 10 overflow)    │
│           PostgreSQL 16 Engine (ACID, MVCC, RLS)                       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. SQLAlchemy 2.0 Model Specifications (`app/models/`)

```python
import uuid
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, Date, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

# --- USER ENTITY ---
class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="PATIENT")
    country_code: Mapped[str] = mapped_column(String(2), nullable=False, default="IN")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    token_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    profile: Mapped[Optional["PatientProfile"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    assessments: Mapped[List["Assessment"]] = relationship(back_populates="patient", cascade="all, delete-orphan")

# --- ASSESSMENT ENTITY (13 Canonical Features) ---
class Assessment(Base, TimestampMixin):
    __tablename__ = "assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    # Clinical Biomarkers
    age: Mapped[float] = mapped_column(Float, nullable=False)
    sex: Mapped[int] = mapped_column(Integer, nullable=False)
    chest_pain_type: Mapped[int] = mapped_column(Integer, nullable=False)
    resting_bp: Mapped[float] = mapped_column(Float, nullable=False) # In canonical mmHg
    serum_cholesterol: Mapped[float] = mapped_column(Float, nullable=False) # In canonical mg/dL
    fasting_blood_sugar: Mapped[float] = mapped_column(Float, nullable=False)
    resting_ecg: Mapped[int] = mapped_column(Integer, nullable=False)
    max_heart_rate: Mapped[float] = mapped_column(Float, nullable=False)
    exercise_angina: Mapped[int] = mapped_column(Integer, nullable=False)
    st_depression: Mapped[float] = mapped_column(Float, nullable=False)
    st_slope: Mapped[int] = mapped_column(Integer, nullable=False)
    major_vessels: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    thallium_stress: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    patient: Mapped["User"] = relationship(back_populates="assessments")
    inference: Mapped["InferenceResult"] = relationship(back_populates="assessment", uselist=False, cascade="all, delete-orphan")

# --- INFERENCE RESULT ENTITY ---
class InferenceResult(Base, TimestampMixin):
    __tablename__ = "inference_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id: Mapped[str] = mapped_column(String(36), ForeignKey("assessments.id", ondelete="CASCADE"), unique=True, index=True)
    
    cad_likelihood_percent: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_interval_lower: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_interval_upper: Mapped[float] = mapped_column(Float, nullable=False)
    risk_strata: Mapped[str] = mapped_column(String(20), nullable=False)
    ten_year_population_risk: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    model_artifact_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    has_imputed_features: Mapped[bool] = mapped_column(Boolean, default=False)
    emergency_warning_active: Mapped[bool] = mapped_column(Boolean, default=False)

    assessment: Mapped["Assessment"] = relationship(back_populates="inference")
    shap_explanations: Mapped[List["ShapExplanation"]] = relationship(back_populates="inference", cascade="all, delete-orphan")

# --- SHAP EXPLANATION ENTITY (13 Feature Attributions) ---
class ShapExplanation(Base):
    __tablename__ = "shap_explanations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    inference_id: Mapped[str] = mapped_column(String(36), ForeignKey("inference_results.id", ondelete="CASCADE"), index=True)
    feature_name: Mapped[str] = mapped_column(String(50), nullable=False)
    raw_feature_value: Mapped[float] = mapped_column(Float, nullable=False)
    shap_value: Mapped[float] = mapped_column(Float, nullable=False)
    direction: Mapped[str] = mapped_column(String(30), nullable=False)

    inference: Mapped["InferenceResult"] = relationship(back_populates="shap_explanations")

# --- IMMUTABLE AUDIT LOG ENTITY ---
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_id: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    actor_role: Mapped[str] = mapped_column(String(20), nullable=False)
    action: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    target_resource: Mapped[str] = mapped_column(String(100), nullable=False)
    target_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    details_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True, nullable=False)
```

---

## 3. Asynchronous Repository Pattern

All data access operations are encapsulated inside typed repositories:

```python
class AssessmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id_with_inference(self, assessment_id: str) -> Optional[Assessment]:
        stmt = (
            select(Assessment)
            .options(
                joinedload(Assessment.inference).joinedload(InferenceResult.shap_explanations)
            )
            .where(Assessment.id == assessment_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_patient_history(
        self, patient_id: str, offset: int = 0, limit: int = 10
    ) -> List[Assessment]:
        stmt = (
            select(Assessment)
            .where(Assessment.patient_id == patient_id)
            .order_by(Assessment.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
```

---

## 4. Connection Pool & Migration Discipline

1. **Asyncpg Connection Pool Parameters:**
   - `pool_size = 20`
   - `max_overflow = 10`
   - `pool_timeout = 30.0`
   - `pool_recycle = 1800` (Recycles connections every 30 minutes to purge memory)
2. **Alembic Versioning Invariant:**
   - Direct DDL manipulation (`CREATE TABLE`, `ALTER TABLE`) in production is banned. All schema changes must be committed as versioned Alembic migration scripts (`alembic upgrade head`) and executed during continuous deployment pipelines.
