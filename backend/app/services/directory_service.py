"""HeartXAI 2.0 - Localized Healthcare Directory & Country Adapter Service (Milestone 15)."""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.directory import Doctor, EducationalResource, Hospital, InsurancePolicy
from app.schemas.country import CountryListResponse, CountryProfileDto
from app.schemas.directory import (
    DoctorProfileDto,
    EducationalResourceDto,
    HospitalFacilityDto,
    InsuranceGuidanceDto,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
COUNTRY_PROFILES_PATH = REPO_ROOT / "shared" / "country-profiles.json"


def load_country_profiles(path: Path = COUNTRY_PROFILES_PATH) -> CountryListResponse:
    """Load country adapter definitions cleanly from local canonical SSOT."""
    data = json.loads(path.read_text(encoding="utf-8"))
    profiles = [CountryProfileDto.model_validate(item) for item in data["countries"].values()]
    return CountryListResponse(
        governance_decision=str(data["metadata"]["governance_decision"]),
        profiles=profiles,
    )


def search_doctors(
    db: Session,
    country_code: str | None = None,
    city: str | None = None,
    specialization: str | None = None,
) -> list[DoctorProfileDto]:
    """Search verified synthetic directory cardiologists without external API calls."""
    stmt = select(Doctor).where(Doctor.is_active.is_(True))
    if country_code:
        stmt = stmt.where(Doctor.country_code == country_code.upper())
    if city:
        stmt = stmt.where(Doctor.location.ilike(f"%{city.strip()}%"))
    if specialization:
        stmt = stmt.where(Doctor.specialization.ilike(f"%{specialization.strip()}%"))

    rows = db.scalars(stmt.order_by(Doctor.doctor_name.asc())).all()
    return [
        DoctorProfileDto(
            id=str(row.id),
            full_name=str(row.doctor_name),
            specialization=str(row.specialization),
            qualification="MD / Cardiology (Synthetic Demo)",
            medical_license_number=f"SYN-LIC-{str(row.id)[:8].upper()}",
            license_issuing_authority="Synthetic Medical Registry",
            is_license_verified=True,
            hospital_affiliation=str(row.hospital_name),
            city=str(row.location),
            country_code=str(row.country_code),
            contact_phone=str(row.contact_number),
            booking_url=None,
        )
        for row in rows
    ]


def search_hospitals(
    db: Session,
    country_code: str | None = None,
    city: str | None = None,
) -> list[HospitalFacilityDto]:
    """Search cardiac emergency facilities and cath lab availability by region."""
    stmt = select(Hospital).where(Hospital.is_active.is_(True))
    if country_code:
        stmt = stmt.where(Hospital.country_code == country_code.upper())
    if city:
        stmt = stmt.where(Hospital.city.ilike(f"%{city.strip()}%"))

    rows = db.scalars(stmt.order_by(Hospital.hospital_name.asc())).all()
    return [
        HospitalFacilityDto(
            id=str(row.id),
            name=str(row.hospital_name),
            accreditation=str(row.accreditation_details),
            has_cardiac_emergency_24_7=True,
            has_catheterization_lab=bool(row.has_247_cath_lab),
            emergency_phone=str(row.emergency_phone),
            address=str(row.address),
            city=str(row.city),
            country_code=str(row.country_code),
        )
        for row in rows
    ]


def list_insurance_guidance(
    db: Session, country_code: str | None = None
) -> list[InsuranceGuidanceDto]:
    """Return synthetic preventative cardiovascular coverage guidance."""
    stmt = select(InsurancePolicy).where(InsurancePolicy.is_active.is_(True))
    if country_code:
        stmt = stmt.where(InsurancePolicy.country_code == country_code.upper())
    rows = db.scalars(stmt).all()
    return [
        InsuranceGuidanceDto(
            country_code=str(row.country_code),
            regulatory_authority=str(row.provider_name),
            diagnostic_coverage_summary=str(row.coverage_summary),
            claims_checklist=[
                "Confirm in-network cardiology consultation coverage",
                "Request preventive lipid & resting ECG coding verification",
                "Retain itemized clinical evaluation summary",
            ],
            authorized_helpline="000-000-0000 (Synthetic Demo Helpline)",
        )
        for row in rows
    ]


def list_educational_resources(
    db: Session, biomarker_code: str | None = None
) -> list[EducationalResourceDto]:
    """Return educational cardiovascular guidance resources."""
    stmt = select(EducationalResource).where(EducationalResource.is_active.is_(True))
    if biomarker_code:
        stmt = stmt.where(EducationalResource.biomarker_code == biomarker_code)
    rows = db.scalars(stmt).all()
    return [
        EducationalResourceDto(
            id=str(row.id),
            title=str(row.title),
            biomarker_code=str(row.biomarker_code),
            summary=str(row.summary),
            guideline_source=str(row.guideline_source),
            diet_plan_summary=str(row.diet_plan_summary),
            exercise_tips_summary=str(row.exercise_tips_summary),
            lifestyle_guidance=str(row.lifestyle_guidance),
        )
        for row in rows
    ]
