# HeartXAI 2.0 — Integration Architecture & External Systems Specification

| Document Attribute | Details |
| :--- | :--- |
| **Document ID** | `HXAI-ARCH-INT-001` |
| **Version** | `2.1.0-REVISED` |
| **System State** | System Technical Architecture & Integration Design (Audited Baseline) |
| **Traceability** | `FUNCTIONAL_REQUIREMENTS.md` (FR-11, FR-12, FR-14, FR-17), `ARCHITECTURE_DECISION_RECORDS.md` (ADR-010, ADR-011), `C4_CONTAINER_DIAGRAM.md` |
| **Author** | Principal Software Architect, Senior Backend Architect, Healthcare Security Reviewer |

---

## 1. Executive Summary & Architectural Scope

The **HeartXAI 2.0 Integration Architecture** defines the technical interfaces, protocols, resilience mechanisms, security controls, and fallback strategies for all external systems, third-party APIs, and upstream data dependencies interacting with the HeartXAI Modular Monolith.

In adherence to **ADR-001 (Modular Monolith)**, **ADR-010 (Integration Resilience & Outbox)**, and **ADR-011 (Geographic Strategy / Adapter Pattern)**, HeartXAI 2.0 treats all external services as untrusted, potentially intermittent, and subject to transient failure, latency spikes, rate throttling, or complete downtime.

Furthermore, following the Phase 3 External Review, HeartXAI explicitly avoids hardcoding any single national healthcare infrastructure. All directory and provider verification capabilities are architected behind pluggable **Strategy / Adapter interfaces** that dynamically adapt to the target geography (`HEARTXAI_GEOGRAPHY=IN|US|GLOBAL`).

```
+---------------------------------------------------------------------------------------------------+
|                                      HEARTXAI 2.0 CORE BOUNDARY                                    |
|                                                                                                   |
|  +--------------------+       +---------------------+       +----------------------------------+  |
|  | Clinical Engine    |       | Assessment Service  |       | Auth & Account Service           |  |
|  | - ML CAD Classifier|       | - Encrypted Storage |       | - Argon2id Password Hashing      |  |
|  | - TreeSHAP (Math)  |       | - Audit Logging     |       | - JWT Token Issuer               |  |
|  | - Counterfactuals  |       | - Trajectory Trends |       | - Consent-First RBAC             |  |
|  +--------------------+       +---------------------+       +----------------------------------+  |
|            |                             |                                    |                   |
|  +---------------------------------------------------------------------------------------------+  |
|  |                     INTEGRATION LAYER: GEOGRAPHIC ADAPTERS & CIRCUIT BREAKERS               |  |
|  |   - IDirectoryProviderAdapter (India PIN / US ZIP)                                          |  |
|  |   - IPhysicianVerificationAdapter (India NMC Document Queue / US CMS NPPES API)             |  |
|  +---------------------------------------------------------------------------------------------+  |
+-------------|----------------------------|------------------------------------|-------------------+
              |                            |                                    |
     HTTPS / REST JSON            HTTPS / REST JSON                    HTTPS / SMTP REST
              v                            v                                    v
+---------------------------+  +---------------------------+  +-------------------------------------+
| External Geospatial / GIS |  | External Provider Registry|  | External Communication / Storage    |
| - OpenStreetMap / Overpass|  | - India: NMC Manual Queue |  | - Transactional Email (Resend/SMTP) |
|   (India & Global Nodes)  |  |   (Optional ABDM HPR)     |  | - S3-Compatible Storage             |
| - Nominatim Geocoder      |  | - US: CMS NPPES API       |  |   (Object Lock WORM / MinIO / AWS)  |
+---------------------------+  +---------------------------+  +-------------------------------------+
```

---

## 2. External System Inventory & Classification Matrix

| System ID | External System / Interface | Provider / Protocol | Primary Purpose in HeartXAI | Sensitivity Tier | Criticality Class | Offline Fallback Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **EXT-01A** | **India Physician Verification Adapter** | State Medical Councils / NMC Document Upload + Admin Queue | Validates medical licenses for Indian doctors via registration certificate review (`FR-11`). | Non-PHI (Public Credential) | Low (Degradable) | Pre-seeded verified physician directory + administrative review queue in `PENDING_VERIF` state. |
| **EXT-01B** | **US CMS NPPES Registry API** | US Dept of Health & Human Services (REST JSON / HTTPS) | Programmatic NPI lookup for US healthcare providers (`FR-11`). | Non-PHI (Public Registry) | Low (Degradable) | Pre-seeded directory + administrative review queue fallback. |
| **EXT-02A** | **India Facility Directory Adapter** | OpenStreetMap India + PMJAY Open Datasets (Overpass QL / JSON) | Proximity discovery of cardiac centers, cath labs, and hospitals in India (`FR-12`). | Tier 1 (Anonymous Coords) | Medium (Degradable) | Local spatial SQLite/PostGIS database pre-seeded with verified Indian cardiac centers and district hospitals. |
| **EXT-02B** | **US Facility Directory Adapter** | OpenStreetMap US + CMS Open Data (Overpass QL / REST JSON) | Proximity discovery of cardiac facilities in the US (`FR-12`). | Tier 1 (Anonymous Coords) | Medium (Degradable) | Local spatial SQLite/PostGIS database pre-seeded with US cardiac facilities. |
| **EXT-03** | **Nominatim Geocoding API** | OpenStreetMap Foundation (REST JSON / HTTPS) | Forward geocoding of patient-entered postal codes (6-digit Indian PIN or 5-digit US ZIP) or city names. | Tier 1 (Locality Only) | Medium (Degradable) | Local offline postal code centroids lookup tables (`assets/geodata/in_pin_codes.json` or `us_postal_codes.json`). |
| **EXT-04** | **Transactional Email Service** | Resend API / SendGrid / SMTP (REST HTTPS / TLS) | Verification tokens, password resets, critical alert notifications, and appointment updates. | Tier 2 (Pseudonymous Email) | High (Async Retry) | Persistent transactional outbox table in PostgreSQL (`outbox_emails`) + Exponential backoff worker. |
| **EXT-05** | **S3-Compatible Object Store** | MinIO (Self-hosted) / AWS S3 / Cloudflare R2 | Immutable archive of compiled clinical assessment PDF reports (`FR-14`) with Object Lock (WORM). | Tier 4 (PHI - AES-256-GCM) | High (Degradable) | Local encrypted spool directory fallback (`/var/data/heartxai/reports/`) with pre-signed URLs. |
| **EXT-06** | **Upstream ML Benchmark Repos** | UCI Machine Learning Repository, Zenodo | Historical benchmark training datasets (Cleveland 1988, Statlog). | De-identified Open Data | Offline Only (Dev/Build) | Cached, immutable, SHA-256 verified local parquet files in `ml/data/processed/`. |

---

## 3. Detailed Interface Specifications

### 3.1 EXT-01: Physician Verification Strategies (Geographic Adapter)

#### 3.1.1 Abstract Interface Definition
```python
from abc import ABC, abstractmethod
from pydantic import BaseModel

class VerificationResult(BaseModel):
    is_verified: bool
    status: str  # "VERIFIED", "PENDING_REVIEW", "REJECTED"
    provider_name: str
    registration_id: str
    council_or_state: str
    verification_notes: str

class IPhysicianVerificationAdapter(ABC):
    @abstractmethod
    async def verify_doctor(self, registration_id: str, state_council: str, document_bytes: bytes | None = None) -> VerificationResult:
        """Verify physician credentials according to jurisdictional adapter."""
        pass
```

#### 3.1.2 EXT-01A: India Physician Verification Strategy (`IndiaManualVerificationAdapter`)
- **Regulatory Reality:** In India, medical registration is governed by the **National Medical Commission (NMC)** and State Medical Councils (e.g., Andhra Pradesh Medical Council, Karnataka Medical Council). The National Medical Register portal (`nmc.org.in`) does **NOT** provide a public, unauthenticated open REST API.
- **ABDM Analysis:** The National Health Authority (NHA) operates the **Healthcare Professionals Registry (HPR)** under Ayushman Bharat Digital Mission (ABDM). While ABDM provides APIs, production access requires formal entity onboarding, sandbox milestone certification (M1/M2/M3), and compliance agreements.
- **HeartXAI Implementation:**
  1. Doctor registers providing: Full Legal Name, State Medical Council Name, Council Registration Number (e.g. `APMC-45123`), and uploads their Medical Registration Certificate (PDF/JPEG).
  2. Account is assigned status `PENDING_VERIF` with view-only permissions.
  3. Verification task is queued in the Admin Audit Dashboard (`FR-20`).
  4. Platform administrator inspects the official NMC public search registry and approves or rejects the registration.

#### 3.1.3 EXT-01B: US CMS NPPES Strategy (`USCMSVerificationAdapter`)
- **Protocol:** REST JSON / HTTPS over `https://npiregistry.cms.hhs.gov/api/`.
- **Query:** `?number={npi_10_digits}&enumeration_type=NPI-1&version=2.1`.
- **Validation:** Verifies active status (`"A"`), primary cardiology/internal medicine taxonomy codes (`207RC0000X`), and Levenshtein name distance $\ge 0.85$.

---

### 3.2 EXT-02 & EXT-03: Geospatial & Facility Directory Strategies

#### 3.2.1 Abstract Interface Definition
```python
class IDirectoryProviderAdapter(ABC):
    @abstractmethod
    async def search_nearby_facilities(self, postal_code: str, radius_km: float = 25.0) -> list[dict]:
        """Discover nearest cardiac centers and emergency facilities."""
        pass
    
    @abstractmethod
    async def resolve_centroid(self, postal_code: str) -> tuple[float, float]:
        """Resolve postal code to latitude/longitude centroid."""
        pass
```

#### 3.2.2 India Directory Implementation (`IndiaDirectoryAdapter`)
- **Postal Code System:** 6-digit Indian PIN codes (e.g. `530001` Visakhapatnam, `560001` Bengaluru, `110001` New Delhi).
- **Centroid Resolution:** Offline JSON centroids dictionary derived from open Government of India datasets (Data.gov.in All India Pincode Directory).
- **Facility Discovery:**
  - Primary source: Pre-seeded spatial SQLite / PostGIS table of verified tertiary cardiac hospitals and PMJAY empanelled cardiology facilities.
  - Live query fallback: OpenStreetMap Overpass API targeted at India geographic bounding box:
    ```text
    [out:json][timeout:15];
    (
      node["amenity"="hospital"]["healthcare"="cardiology"](around:25000, 17.72, 83.30);
      node["amenity"="hospital"]["emergency"="yes"](around:25000, 17.72, 83.30);
      way["amenity"="hospital"](around:25000, 17.72, 83.30);
    );
    out center 20;
    ```

#### 3.2.3 US Directory Implementation (`USDirectoryAdapter`)
- **Postal Code System:** 5-digit US ZIP codes (e.g. `94143`, `02115`).
- **Centroid Resolution:** Offline US Census ZIP centroids.
- **Facility Discovery:** Pre-seeded US cardiac centers + Overpass OSM live fallback.

---

### 3.3 EXT-04: Transactional Email Service & Persistent Outbox Pattern

To prevent external network latency (500ms–3,000ms) from blocking user transactions, HeartXAI implements the **Transactional Outbox Pattern**:

```
+--------------------------------------------------------------------------------------------------+
| API Transaction Boundary                                                                         |
|                                                                                                  |
| [ POST /auth/register ] ---> [ Insert users ] + [ Insert outbox_emails (status=PENDING) ]        |
|                                                     |                                            |
|                                                     | Atomic PostgreSQL Commit                   |
+-----------------------------------------------------|--------------------------------------------+
                                                      v
+--------------------------------------------------------------------------------------------------+
| Asynchronous Email Worker                                                                        |
|                                                                                                  |
| [ Poll outbox_emails ] ---> [ Circuit Breaker ] ---> [ External Email API (Resend / SendGrid) ]  |
|                                    |                                    |                        |
|                                    | (Success: Mark SENT)               | (Failure: Backoff)     |
+--------------------------------------------------------------------------------------------------+
```

---

### 3.4 EXT-05: S3-Compatible Object Store (Clinical PDF Archive with WORM)

Patient assessment summary reports (`FR-14`) are stored as immutable PDFs:
- **Object Key Structure:**
  `tenants/{tenant_id}/patients/{patient_uuid}/{assessment_uuid}/report_{generated_timestamp}.pdf`
- **Security & Immutability:**
  - Authenticated server-side encryption via AES-256-GCM.
  - S3 **Object Lock in Compliance Mode** (WORM - Write Once, Read Many) ensuring reports cannot be modified or deleted during the mandatory 7-year retention period.
  - Time-bounded pre-signed URLs (15 minutes expiry) for patient/doctor download. Zero direct S3 credentials exposed to client applications.

---

## 4. Resilience Patterns & Circuit Breakers

Every outbound HTTP integration is protected by a dedicated **Circuit Breaker** using a 3-state state machine:

| External Service | Failure Threshold | Consecutive Failures | Sliding Window | Reset Timeout | Probe Requests | Timeout (p99) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NPPES / External Verification** | 50% | 5 | 30 seconds | 60 seconds | 3 | 3,000 ms |
| **Nominatim Geocoding** | 40% | 4 | 20 seconds | 45 seconds | 2 | 2,000 ms |
| **Overpass OSM API** | 50% | 3 | 30 seconds | 90 seconds | 2 | 5,000 ms |
| **Email Service (Resend)**| 30% | 5 | 60 seconds | 120 seconds | 5 | 4,000 ms |
| **S3 Storage (MinIO/AWS)**| 20% | 3 | 15 seconds | 30 seconds | 3 | 2,500 ms |

---

## 5. Multi-Jurisdictional Healthcare Compliance & PHI Egress Controls

HeartXAI enforces strict data protection boundaries across jurisdictions:
1. **India: DPDP Act 2023 & IT (SPDI) Rules 2011:**
   - Explicit, revocable patient consent for data processing and physician consultation sharing.
   - Purpose limitation: Clinical data is never used for advertising, commercial profiling, or third-party transfer.
2. **United States: HIPAA Privacy & Security Rules (45 CFR Part 160/164):**
   - Business Associate Agreement (BAA) requirements on any external cloud storage or email providers handling PHI.
   - Cryptographic shredding and complete audit trail of PHI disclosures.
3. **European Union: General Data Protection Regulation (GDPR):**
   - Right of Access (Data Export, `FR-25`) and Right to Erasure (Account Deletion, `FR-26`).
4. **Zero PHI Egress Boundary:**
   - No clinical metrics (blood pressure, cholesterol, ECG, ST depression) or patient names are ever transmitted to Nominatim, OpenStreetMap, or external verification registries.
   - Outbound geocoding coordinates are truncated to 2 decimal places ($\approx 1.1\text{ km}$ precision) to prevent spatial triangulation of patient residences.
   - Transactional emails contain zero clinical biomarkers or risk scores—only generic notification copy.

---

*Verified and sealed by Principal Software Architect, Backend Lead & Healthcare Security Reviewer.*
