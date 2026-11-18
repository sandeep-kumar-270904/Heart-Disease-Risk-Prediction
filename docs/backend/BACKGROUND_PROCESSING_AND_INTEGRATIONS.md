# HeartXAI 2.0 — Background Processing & External Integrations Specification

**Document ID:** `HX2-BE-011`  
**Version:** `1.0.0`  
**Phase:** Phase 7 — Backend Engineering Architecture & API Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal Backend Architect & Systems Integration Lead  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-002, ADR-011  

---

## 1. Background Processing Architectural Decision

In accordance with our engineering discipline to avoid gratuitous complexity for an individual developer, we evaluate the architectural options for asynchronous task processing:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   TASK RUNTIME COMPARISON & SELECTION                  │
├───────────────────────────────────┬────────────────────────────────────┤
│ REJECTED: FULL CELERY + RABBITMQ  │ ADOPTED: FASTAPI BACKGROUND TASKS  │
├───────────────────────────────────┼────────────────────────────────────┤
│ • Requires RabbitMQ/Redis broker  │ • Zero external daemon dependency  │
│ • Complex dual process monitoring │ • Native asyncio event loop        │
│ • Serialization overhead          │ • Directly shares AsyncEngine pool │
│ • High operational maintenance    │ • Ideal for lightweight email/logs │
└───────────────────────────────────┴────────────────────────────────────┘
```

### 1.1 Evaluated Task Domains & Selected Architecture

| Task Domain | Execution Duration | Selected Runtime Pattern | Justification & Failure Handling |
| :--- | :---: | :--- | :--- |
| **Email Verification & Password Reset** | $200\text{ms}–800\text{ms}$ | **FastAPI `BackgroundTasks`** | Lightweight; non-blocking HTTP request returns instantly; retries handled via local retry counter (up to 3 attempts). |
| **Audit Trail Flushing** | $10\text{ms}–30\text{ms}$ | **Inline Unit of Work** | Security audit events are persisted synchronously in the same transaction as the clinical action to prevent audit loss. |
| **Consultation PDF Generation** | $400\text{ms}–900\text{ms}$ | **On-Demand Streaming via `asyncio.to_thread`** | Weasyprint compilation runs in worker thread; streams binary directly to response without saving to disk. |
| **Directory Nightly Cache Refresh** | $2\text{s}–10\text{s}$ | **Asyncio Cron Task / Script** | Lightweight scheduled asyncio script run via standard host cron (`0 2 * * *`). |

---

## 2. Asynchronous Email Dispatch Architecture

Email delivery (for account verification and password reset) is executed via asynchronous SMTP / transactional API (e.g., Resend / SendGrid / Amazon SES) using `httpx.AsyncClient`:

```python
from fastapi import BackgroundTasks
from app.core.logging import get_logger
import httpx

logger = get_logger(__name__)

async def send_verification_email_task(email: str, token: str, full_name: str):
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://api.resend.com/emails",
                    headers={"Authorization": f"Bearer {settings.EMAIL_API_KEY}"},
                    json={
                        "from": "HeartXAI Security <security@heartxai.org>",
                        "to": [email],
                        "subject": "Verify Your HeartXAI Account",
                        "html": f"<p>Hello {full_name},</p><p>Please verify your account: <a href='https://app.heartxai.org/auth/verify-email?token={token}'>Verify Email</a></p>"
                    }
                )
                if response.status_code == 200:
                    logger.info("verification_email_sent", email_hash=hash(email))
                    return
        except Exception as e:
            logger.warning("email_send_attempt_failed", attempt=attempt, error=str(e))
            if attempt == max_retries:
                logger.error("email_send_exhausted_retries", email_hash=hash(email))
```

---

## 3. Country-Configurable Healthcare Integration Adapters (ADR-011)

In strict accordance with approved product requirement **ADR-011**, all external healthcare dependencies (doctor registries, hospital directories, statutory guides) are decoupled via the **Country Adapter Pattern**:

```
                              [ DirectoryService ]
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │   ICountryAdapter (ABC)   │
                         └─────────────┬─────────────┘
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         ▼                             ▼                             ▼
  [ IndiaAdapter ]              [ USAAdapter ]                [ UKAdapter ]
  • NMC Registry API            • State Boards / NPI          • GMC Register
  • NABH Facilities             • CMS Hospital Compare        • NHS England Directory
  • Emergency: 112 / 102        • Emergency: 911              • Emergency: 999 / 111
  • Default: mg/dL, mmHg        • Default: mg/dL, mmHg        • Default: mmol/L, mmHg
```

### 3.1 Abstract Country Adapter Interface (`app/integrations/base.py`)
```python
from abc import ABC, abstractmethod
from typing import List, Optional
from app.schemas.directory import DoctorProfileDto, HospitalFacilityDto, InsuranceGuidanceDto

class ICountryAdapter(ABC):
    @abstractmethod
    async def search_doctors(
        self, city: Optional[str], specialty: Optional[str], verified_only: bool, offset: int, limit: int
    ) -> List[DoctorProfileDto]:
        pass

    @abstractmethod
    async def search_hospitals(
        self, city: Optional[str], cardiac_emergency_only: bool, offset: int, limit: int
    ) -> List[HospitalFacilityDto]:
        pass

    @abstractmethod
    async def verify_physician_license(
        self, license_number: str, authority: str
    ) -> tuple[bool, str]: # (is_valid, official_name)
        pass

    @abstractmethod
    def get_insurance_guidance(self) -> InsuranceGuidanceDto:
        pass

    @abstractmethod
    def get_emergency_hotlines(self) -> dict[str, str]:
        pass
```

---

## 4. Verified Country Integrations & Fallback Strategies

### 4.1 India Adapter (`app/integrations/india_adapter.py`)
- **Doctor Licensure Verification:**
  - *Primary Source:* National Medical Commission (NMC) National Medical Register.
  - *Fallback Strategy:* Verified static snapshot registry of accredited tertiary cardiologists; unverified applicants flagged for manual compliance review.
- **Hospital Directory:**
  - *Primary Source:* National Accreditation Board for Hospitals & Healthcare Providers (NABH).
  - *Verified Emergency Numbers:* `112` (National Emergency), `102` / `108` (Ambulance).
- **Insurance Guidance:**
  - *Regulatory Context:* IRDAI (Insurance Regulatory and Development Authority of India) and Ayushman Bharat PM-JAY diagnostic test reimbursement rules.

### 4.2 United States Adapter (`app/integrations/usa_adapter.py`)
- **Doctor Licensure Verification:**
  - *Primary Source:* CMS National Plan & Provider Enumeration System (NPPES) NPI Registry API (`https://npiregistry.cms.hhs.gov/api/`).
  - *Verified Licensing:* State Medical Boards.
- **Hospital Directory:**
  - *Primary Source:* CMS Hospital General Information dataset (Centers for Medicare & Medicaid Services).
  - *Verified Emergency Numbers:* `911`.
- **Insurance Guidance:**
  - *Regulatory Context:* ACA Preventive Care coverage mandates for lipid screening and cardiac risk assessments.

### 4.3 United Kingdom Adapter (`app/integrations/uk_adapter.py`)
- **Doctor Licensure Verification:**
  - *Primary Source:* General Medical Council (GMC) List of Registered Medical Practitioners.
- **Hospital Directory:**
  - *Primary Source:* NHS England Trust Directory.
  - *Verified Emergency Numbers:* `999` (Emergency), `111` (Non-emergency NHS triage).
