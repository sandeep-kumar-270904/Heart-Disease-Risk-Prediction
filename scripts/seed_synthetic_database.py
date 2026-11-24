"""HeartXAI 2.0 — Idempotent Category B Synthetic Database Seeder.

Populates development and staging databases exclusively with synthetically generated
user personas, Category B clinical intake fixtures, and synthetic demonstration
country directory profiles (US, IN, GB) aligned with DEC-004 and DEC-005.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
SCRIPTS_DIR = REPO_ROOT / "scripts"

for path_entry in (BACKEND_DIR, SCRIPTS_DIR):
    if str(path_entry) not in sys.path:
        sys.path.insert(0, str(path_entry))

from generate_synthetic_patients import generate_synthetic_cohort  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models.assessment import Assessment  # noqa: E402
from app.models.directory import (  # noqa: E402
    Doctor,
    EducationalResource,
    Hospital,
    InsurancePolicy,
)
from app.models.user import PatientProfile, User  # noqa: E402


def seed_database(
    session: Session, assessment_count: int = 10, seed: int = 42
) -> dict[str, int]:
    """Idempotently seed synthetic users, Category B assessments, and demo directories."""
    if not settings.SYNTHETIC_DATA_ONLY:
        raise RuntimeError(
            "Refusing to run synthetic seeder when SYNTHETIC_DATA_ONLY is False (DEC-005 violation)."
        )

    counts: dict[str, int] = {
        "users_created": 0,
        "assessments_created": 0,
        "doctors_created": 0,
        "hospitals_created": 0,
        "policies_created": 0,
        "resources_created": 0,
    }

    # 1. Seed Synthetic Demo Actors
    demo_users = [
        {
            "email": "patient.demo@example.com",
            "password": "SyntheticPatient!2026",
            "full_name": "Synthetic Patient Alpha",
            "role": "PATIENT",
            "country_code": "US",
            "clinician_status": "N/A",
        },
        {
            "email": "clinician.demo@example.com",
            "password": "SyntheticDoctor!2026",
            "full_name": "Dr. Synthetic Cardio (Demo)",
            "role": "CLINICIAN",
            "country_code": "IN",
            "clinician_status": "VERIFIED",
        },
        {
            "email": "admin.demo@example.com",
            "password": "SyntheticAdmin!2026",
            "full_name": "Synthetic System Auditor",
            "role": "ADMIN",
            "country_code": "GB",
            "clinician_status": "N/A",
        },
    ]

    patient_user: User | None = None
    for actor in demo_users:
        existing = session.scalar(select(User).where(User.email == actor["email"]))
        if existing is None:
            user = User(
                email=actor["email"],
                hashed_password=hash_password(actor["password"]),
                full_name=actor["full_name"],
                role=actor["role"],
                country_code=actor["country_code"],
                clinician_status=actor["clinician_status"],
                is_active=True,
                is_synthetic=True,
            )
            session.add(user)
            session.flush()
            if actor["role"] == "PATIENT":
                session.add(
                    PatientProfile(
                        patient_id=user.id,
                        biological_sex="MALE",
                        preferred_units="US_STANDARD",
                    )
                )
            counts["users_created"] += 1
            if actor["role"] == "PATIENT":
                patient_user = user
        elif actor["role"] == "PATIENT":
            patient_user = existing

    # 2. Seed Category B Synthetic Assessments for demo patient
    if patient_user is not None:
        existing_assessments = session.scalars(
            select(Assessment).where(Assessment.patient_id == patient_user.id)
        ).all()
        if not existing_assessments:
            cohort = generate_synthetic_cohort(
                count=assessment_count, seed=seed, unit_system="us_customary"
            )
            for rec in cohort:
                intake = rec.intake
                assessment = Assessment(
                    patient_id=patient_user.id,
                    status="COMPLETED",
                    is_synthetic=True,
                    age=int(round(intake.age)),
                    sex=intake.sex,
                    cp=intake.chest_pain_type,
                    trestbps=int(round(intake.resting_bp)),
                    chol=int(round(intake.serum_cholesterol)),
                    fbs=1 if intake.fasting_blood_sugar > 120.0 else 0,
                    fasting_blood_sugar_mgdl=round(
                        float(intake.fasting_blood_sugar), 2
                    ),
                    restecg=intake.resting_ecg,
                    thalach=int(round(intake.max_heart_rate)),
                    exang=intake.exercise_angina,
                    oldpeak=float(intake.st_depression),
                    slope=intake.st_slope,
                    ca=intake.major_vessels if intake.major_vessels is not None else 0,
                    thal=intake.thallium_stress
                    if intake.thallium_stress is not None
                    else 1,
                )
                session.add(assessment)
                counts["assessments_created"] += 1

    # 3. Seed Synthetic Country-Configurable Directory Entries (US, IN, GB)
    demo_doctors = [
        {
            "doctor_name": "Dr. Synthetic Cardiologist (US Demo)",
            "specialization": "Preventative Cardiology",
            "hospital_name": "Metro Synthetic Heart Institute",
            "contact_number": "+1-555-0100",
            "location": "Boston, MA",
            "country_code": "US",
        },
        {
            "doctor_name": "Dr. Synthetic Cardiologist (IN Demo)",
            "specialization": "Clinical & Interventional Cardiology",
            "hospital_name": "Apex Synthetic Cardiac Care",
            "contact_number": "+91-11-5550-0100",
            "location": "New Delhi, DL",
            "country_code": "IN",
        },
        {
            "doctor_name": "Dr. Synthetic Cardiologist (GB Demo)",
            "specialization": "General Cardiology",
            "hospital_name": "Thames Synthetic Cardiology Clinic",
            "contact_number": "+44-20-7946-0100",
            "location": "London",
            "country_code": "GB",
        },
    ]
    for doc_data in demo_doctors:
        if (
            session.scalar(
                select(Doctor).where(Doctor.doctor_name == doc_data["doctor_name"])
            )
            is None
        ):
            session.add(Doctor(**doc_data))
            counts["doctors_created"] += 1

    demo_hospitals = [
        {
            "hospital_name": "Metro Synthetic Heart Institute",
            "facility_type": "Comprehensive Cardiac Center",
            "emergency_phone": "911",
            "address": "100 Synthetic Medical Plaza",
            "city": "Boston",
            "state": "MA",
            "country_code": "US",
            "accreditation_details": "Synthetic Demonstration Facility (Non-Operational)",
        },
        {
            "hospital_name": "Apex Synthetic Cardiac Care",
            "facility_type": "STEMI & Cardiac Emergency Center",
            "emergency_phone": "112",
            "address": "42 Demo Avenue, Sector 1",
            "city": "New Delhi",
            "state": "DL",
            "country_code": "IN",
            "accreditation_details": "Synthetic Demonstration Facility (Non-Operational)",
        },
        {
            "hospital_name": "Thames Synthetic Cardiology Clinic",
            "facility_type": "Cardiac Assessment Unit",
            "emergency_phone": "999",
            "address": "10 Demo Square",
            "city": "London",
            "state": "Greater London",
            "country_code": "GB",
            "accreditation_details": "Synthetic Demonstration Facility (Non-Operational)",
        },
    ]
    for hosp_data in demo_hospitals:
        if (
            session.scalar(
                select(Hospital).where(
                    Hospital.hospital_name == hosp_data["hospital_name"]
                )
            )
            is None
        ):
            session.add(Hospital(**hosp_data))
            counts["hospitals_created"] += 1

    demo_policies = [
        {
            "provider_name": "Synthetic Health Plan US",
            "policy_name": "Preventative Cardiovascular Coverage Demo",
            "country_code": "US",
            "coverage_summary": "Demonstrates US preventive screening benefits under ACA guidelines.",
            "exclusions_summary": "Synthetic placeholder policy for architectural testing only.",
        },
        {
            "provider_name": "Synthetic Health Plan IN",
            "policy_name": "Cardiac Diagnostic Demo Policy",
            "country_code": "IN",
            "coverage_summary": "Demonstrates localized Indian cardiac diagnostic summary schema.",
            "exclusions_summary": "Synthetic placeholder policy for architectural testing only.",
        },
    ]
    for policy_data in demo_policies:
        if (
            session.scalar(
                select(InsurancePolicy).where(
                    InsurancePolicy.provider_name == policy_data["provider_name"]
                )
            )
            is None
        ):
            session.add(InsurancePolicy(**policy_data))
            counts["policies_created"] += 1

    demo_resources = [
        {
            "title": "Managing Resting Systolic Blood Pressure",
            "biomarker_code": "trestbps",
            "summary": "Evidence-based lifestyle overview for healthy blood pressure maintenance.",
            "guideline_source": "ACC/AHA Primary Prevention Educational Reference",
            "diet_plan_summary": "DASH-aligned sodium reduction and potassium-rich whole foods.",
            "exercise_tips_summary": "150 minutes/week moderate aerobic activity as cleared by physician.",
            "lifestyle_guidance": "Discuss home blood pressure monitoring logs with your clinician.",
        },
        {
            "title": "Understanding Serum Cholesterol Profiles",
            "biomarker_code": "chol",
            "summary": "Educational guide to dietary fats, soluble fiber, and lipid testing.",
            "guideline_source": "ACC/AHA Lipid Management Educational Reference",
            "diet_plan_summary": "Emphasize unsaturated fats, legumes, oats, and leafy greens.",
            "exercise_tips_summary": "Regular brisk walking combined with resistance exercise.",
            "lifestyle_guidance": "Review fasting lipid panels periodically with a healthcare provider.",
        },
    ]
    for res_data in demo_resources:
        if (
            session.scalar(
                select(EducationalResource).where(
                    EducationalResource.title == res_data["title"]
                )
            )
            is None
        ):
            session.add(EducationalResource(**res_data))
            counts["resources_created"] += 1

    session.commit()
    return counts


def main() -> int:
    """CLI entrypoint for seeding the configured database with synthetic fixtures."""
    parser = argparse.ArgumentParser(
        description="Seed database with Category B synthetic data."
    )
    parser.add_argument(
        "--assessments", type=int, default=10, help="Assessments to generate"
    )
    parser.add_argument("--seed", type=int, default=42, help="Deterministic RNG seed")
    args = parser.parse_args()

    with SessionLocal() as session:
        summary = seed_database(
            session, assessment_count=args.assessments, seed=args.seed
        )
    print(f"Synthetic database seed complete: {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
