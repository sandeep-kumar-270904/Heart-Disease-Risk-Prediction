"""HeartXAI 2.0 - Localized Healthcare Directory & Country Adapter Routes (Milestone 15)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.country import CountryListResponse
from app.schemas.directory import (
    DoctorProfileDto,
    EducationalResourceDto,
    HospitalFacilityDto,
    InsuranceGuidanceDto,
)
from app.services.directory_service import (
    list_educational_resources,
    list_insurance_guidance,
    load_country_profiles,
    search_doctors,
    search_hospitals,
)

router = APIRouter(prefix="/directory", tags=["Healthcare Directory & Localization"])


@router.get("/countries", response_model=CountryListResponse, status_code=status.HTTP_200_OK)
def get_country_profiles() -> CountryListResponse:
    """List supported synthetic country adapter configurations (US, IN, GB, DEFAULT)."""
    return load_country_profiles()


@router.get("/doctors", response_model=list[DoctorProfileDto], status_code=status.HTTP_200_OK)
def get_doctors(
    country_code: str | None = Query(default=None, max_length=7),
    city: str | None = Query(default=None, max_length=100),
    specialization: str | None = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
) -> list[DoctorProfileDto]:
    """Search synthetic directory cardiologists by country, city, or specialty."""
    return search_doctors(db, country_code=country_code, city=city, specialization=specialization)


@router.get("/hospitals", response_model=list[HospitalFacilityDto], status_code=status.HTTP_200_OK)
def get_hospitals(
    country_code: str | None = Query(default=None, max_length=7),
    city: str | None = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
) -> list[HospitalFacilityDto]:
    """Search cardiac emergency facilities and cath labs by country or city."""
    return search_hospitals(db, country_code=country_code, city=city)


@router.get("/insurance", response_model=list[InsuranceGuidanceDto], status_code=status.HTTP_200_OK)
def get_insurance_guidance(
    country_code: str | None = Query(default=None, max_length=7),
    db: Session = Depends(get_db),
) -> list[InsuranceGuidanceDto]:
    """Return synthetic preventative cardiovascular coverage guidance."""
    return list_insurance_guidance(db, country_code=country_code)


@router.get(
    "/resources", response_model=list[EducationalResourceDto], status_code=status.HTTP_200_OK
)
def get_educational_resources(
    biomarker_code: str | None = Query(default=None, max_length=32),
    db: Session = Depends(get_db),
) -> list[EducationalResourceDto]:
    """Return educational cardiovascular guidance resources."""
    return list_educational_resources(db, biomarker_code=biomarker_code)
