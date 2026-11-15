# HeartXAI 2.0 — Integration Architecture & External Systems Specification

| Document Attribute | Details |
| :--- | :--- |
| **Document ID** | `HXAI-ARCH-INT-001` |
| **Version** | `2.0.0-PROD` |
| **System State** | System Technical Architecture & Integration Design |
| **Traceability** | `FUNCTIONAL_REQUIREMENTS.md` (FR-11, FR-12, FR-14, FR-17), `SYSTEM_ARCHITECTURE_DOCUMENT.md`, `C4_CONTAINER_DIAGRAM.md` |
| **Author** | Principal Software Architect, Senior Backend Architect, Integration Lead |

---

## 1. Executive Summary & Architectural Scope

The **HeartXAI 2.0 Integration Architecture** defines the technical interfaces, protocols, resilience mechanisms, security controls, and fallback strategies for all external systems, third-party APIs, and upstream data dependencies interacting with the HeartXAI Modular Monolith.

In adherence to **ADR-001 (Modular Monolith)** and **ADR-008 (STRIDE Threat Model & Zero-Trust External Boundaries)**, HeartXAI 2.0 treats all external services as untrusted, potentially intermittent, and subject to transient failure, latency spikes, rate throttling, or complete downtime. The core clinical inference, SHAP explanation, and patient data management capabilities of HeartXAI are architected to operate with complete autonomous resiliency—never failing catastrophically due to an external network dependency.

```
+---------------------------------------------------------------------------------------------------+
|                                      HEARTXAI 2.0 CORE BOUNDARY                                    |
|                                                                                                   |
|  +--------------------+       +---------------------+       +----------------------------------+  |
|  | Clinical Engine    |       | Assessment Service  |       | Auth & Account Service           |  |
|  | - ML Inference     |       | - Encrypted Storage |       | - Argon2id Password Hashing      |  |
|  | - TreeSHAP Expl.   |       | - Audit Logging     |       | - JWT Token Issuer               |  |
|  | - Counterfactuals  |       | - Risk Trends       |       | - Role Authorization             |  |
|  +--------------------+       +---------------------+       +----------------------------------+  |
|            |                             |                                    |                   |
|  +---------------------------------------------------------------------------------------------+  |
|  |                            INTEGRATION LAYER & CIRCUIT BREAKERS                             |  |
|  +---------------------------------------------------------------------------------------------+  |
+-------------|----------------------------|------------------------------------|-------------------+
              |                            |                                    |
     HTTPS / REST JSON            HTTPS / REST JSON                    HTTPS / SMTP REST
              v                            v                                    v
+---------------------------+  +---------------------------+  +-------------------------------------+
| External Geospatial / GIS |  | External Provider Registry|  | External Communication / Storage    |
| - OpenStreetMap / Overpass|  | - CMS NPPES NPI Registry  |  | - Transactional Email (Resend/SMTP) |
| - Nominatim Geocoder      |  |   (Physician Verification)|  | - S3-Compatible Storage (MinIO/AWS) |
+---------------------------+  +---------------------------+  +-------------------------------------+
```

---

## 2. External System Inventory & Classification Matrix

| System ID | External System Name | Provider / Protocol | Primary Purpose in HeartXAI | Sensitivity Tier | Criticality Class | Offline Fallback Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **EXT-01** | **CMS NPPES Registry API** | US Dept of Health & Human Services (REST JSON / HTTPS) | Validates medical licenses and NPI (National Provider Identifier) numbers during Doctor registration (`FR-11`). | Non-PHI (Public Registry) | Low (Degradable) | Pre-seeded local verified physician directory + asynchronous manual admin verification queue. |
| **EXT-02** | **OpenStreetMap Overpass API** | OpenStreetMap Foundation (Overpass QL / REST JSON) | Proximity discovery of emergency cardiac facilities, cath labs, and hospitals (`FR-12`). | Tier 1 (Anonymous Coords) | Medium (Degradable) | Local spatial SQLite/PostGIS database pre-seeded with 1,500+ verified cardiac centers. |
| **EXT-03** | **Nominatim Geocoding API** | OpenStreetMap Foundation (REST JSON / HTTPS) | Forward geocoding of patient-entered postal codes or city names to latitude/longitude coordinates. | Tier 1 (City/Zip Only) | Medium (Degradable) | Local offline postal code centroids lookup table (`assets/geodata/us_postal_codes.json`). |
| **EXT-04** | **Transactional Email Service** | Resend API / SendGrid / SMTP (REST HTTPS / TLS) | Verification tokens, password resets, critical alert notifications, and appointment updates. | Tier 2 (Pseudonymous Email) | High (Async Retry) | Persistent transactional outbox table in PostgreSQL (`outbox_emails`) + Exponential backoff worker. |
| **EXT-05** | **S3-Compatible Object Store** | MinIO (Self-hosted) / AWS S3 (REST HTTPS) | Immutable archive of compiled clinical assessment PDF reports (`FR-14`). | Tier 4 (PHI - AES-256-GCM) | High (Degradable) | Local encrypted filesystem storage fallback (`/var/data/heartxai/reports/`) with pre-signed URLs. |
| **EXT-06** | **Upstream ML Benchmark Repos** | UCI Machine Learning Repository, Zenodo, Kaggle | Golden training datasets (Cleveland, Statlog, VA, Switzerland, Long Beach). | De-identified Open Data | Offline Only (Dev/Build) | Cached, immutable, SHA-256 verified local parquet files in `ml/data/processed/`. |

---

## 3. Detailed Interface Specifications

### 3.1 EXT-01: CMS NPPES NPI Registry API

#### 3.1.1 Purpose & Workflow
When a healthcare provider registers on HeartXAI with the role `doctor`, HeartXAI validates their 10-digit National Provider Identifier (NPI) against the US Federal National Plan and Provider Enumeration System (NPPES) registry to verify active licensure, cardiology or internal medicine taxonomy, and practice jurisdiction.

#### 3.1.2 Protocol & Endpoint Contract
- **Base URL:** `https://npiregistry.cms.hhs.gov/api/`
- **Method:** `GET`
- **Query Parameters:**
  - `number`: 10-digit NPI string (e.g., `1234567890`)
  - `enumeration_type`: `NPI-1` (Individual providers only; prevents institutional NPI misuse)
  - `version`: `2.1`
- **Request Headers:**
  - `Accept: application/json`
  - `User-Agent: HeartXAI-System/2.0 (health-verification@heartxai.internal)`
- **Sample Request:**
  ```http
  GET /api/?number=1487654321&enumeration_type=NPI-1&version=2.1 HTTP/1.1
  Host: npiregistry.cms.hhs.gov
  Accept: application/json
  ```
- **Sample Response Structure:**
  ```json
  {
    "result_count": 1,
    "results": [
      {
        "number": 1487654321,
        "basic": {
          "first_name": "SARAH",
          "last_name": "CONNOR",
          "credential": "MD",
          "sole_proprietor": "NO",
          "gender": "F",
          "enumeration_date": "2015-06-12",
          "last_updated": "2023-01-15",
          "status": "A"
        },
        "taxonomies": [
          {
            "code": "207RC0000X",
            "desc": "Cardiovascular Disease",
            "primary": true,
            "state": "CA",
            "license": "C123456"
          }
        ],
        "addresses": [
          {
            "country_code": "US",
            "country_name": "United States",
            "address_purpose": "LOCATION",
            "address_1": "100 MEDICAL CENTER WAY",
            "city": "SAN FRANCISCO",
            "state": "CA",
            "postal_code": "94143"
          }
        ]
      }
    ]
  }
  ```

#### 3.1.3 Validation Logic
HeartXAI's backend `ProviderVerificationService` executes the following deterministic checks:
1. `result_count == 1`.
2. `results[0].basic.status == "A"` (Active status; inactive or revoked NPIs fail verification).
3. `results[0].taxonomies` contains an approved cardiology, electrophysiology, or internal medicine healthcare provider taxonomy code (e.g., `207RC0000X`, `207RA0001X`, `207RI0011X`).
4. Provided applicant name matches `first_name` and `last_name` using Levenshtein distance metric $\ge 0.85$ to account for middle initials or formal legal names.

---

### 3.2 EXT-02 & EXT-03: Geospatial Services (Overpass & Nominatim)

#### 3.2.1 Purpose & Workflow
To support **FR-12 (Hospital and Cardiac Facility Directory)** and **FR-11 (Doctor Directory)**, HeartXAI provides spatial search for nearby medical resources without transmitting identifiable patient data. Only low-resolution latitude/longitude coordinates (truncated to 2 decimal places, $\approx 1.1\text{ km}$ precision) are queried.

#### 3.2.2 Nominatim Forward Geocoding Endpoint
- **Base URL:** `https://nominatim.openstreetmap.org/search`
- **Method:** `GET`
- **Query Parameters:**
  - `q`: Free-text query (e.g., `94143` or `San Francisco, CA`)
  - `format`: `jsonv2`
  - `countrycodes`: `us`
  - `limit`: `1`
- **Header Requirement:** Must include custom `User-Agent` per OSM Fair Use Policy (max 1 request/sec).

#### 3.2.3 Overpass API Hospital Extraction Endpoint
- **Base URL:** `https://overpass-api.de/api/interpreter`
- **Method:** `POST`
- **Content-Type:** `application/x-www-form-urlencoded`
- **Query DSL Body:**
  ```text
  [out:json][timeout:15];
  (
    node["amenity"="hospital"]["healthcare"="cardiology"](around:25000, 37.77, -122.41);
    node["amenity"="hospital"]["emergency"="yes"](around:25000, 37.77, -122.41);
    way["amenity"="hospital"](around:25000, 37.77, -122.41);
  );
  out center 20;
  ```

---

### 3.3 EXT-04: Transactional Email Service

#### 3.3.1 Integration Strategy: Persistent Outbox Pattern
Direct synchronous email transmission during HTTP request handling introduces significant latency (500ms - 3,000ms) and creates brittle transactions where database commits succeed but email calls fail. 

HeartXAI implements the **Transactional Outbox Pattern**:
1. During the user registration or password reset transaction, an email payload is inserted into the `outbox_emails` table within the **same atomic database transaction**.
2. An asynchronous background worker (`EmailDispatcherWorker`) polls `outbox_emails` for `status = 'PENDING'`, batches up to 25 emails, and transmits them via the external provider.
3. If transmission fails, `retry_count` is incremented, and an exponential backoff timestamp is set.

```
+--------------------------------------------------------------------------------------------------+
| API Transaction Boundary                                                                         |
|                                                                                                  |
| [ POST /auth/register ] ---> [ Insert users ] + [ Insert outbox_emails (status=PENDING) ]        |
|                                                     |                                            |
|                                                     | Commit Transaction                         |
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

#### 3.3.2 Resend API Payload Format
- **Base URL:** `https://api.resend.com/emails`
- **Method:** `POST`
- **Headers:**
  - `Authorization: Bearer ${RESEND_API_KEY}`
  - `Content-Type: application/json`
- **Payload Schema:**
  ```json
  {
    "from": "HeartXAI Health Security <security@heartxai.internal>",
    "to": ["patient_anonymous_hash@example.com"],
    "subject": "HeartXAI Security: Verify Your Clinical Account",
    "html": "<p>Click the link below to verify your account within 24 hours.</p>...",
    "tags": [
      {"name": "category", "value": "account_verification"},
      {"name": "environment", "value": "production"}
    ]
  }
  ```

---

### 3.4 EXT-05: S3-Compatible Object Store (Clinical PDF Archive)

#### 3.4.1 Storage Architecture
Patient clinical summary reports (`FR-14`) are compiled by the backend `ReportService` using HTML5/WeasyPrint and stored in an S3-compatible bucket (`heartxai-clinical-reports`).

- **Object Key Structure:**
  `tenants/{tenant_id}/patients/{patient_uuid}/{assessment_uuid}/report_{generated_timestamp}.pdf`
- **Security & Encryption:**
  - Server-Side Encryption with Customer-Provided Keys (SSE-C) or AWS KMS using AES-256-GCM.
  - Bucket ACLs: Strict Private (`no-public-read`, `no-public-write`).
- **Access Protocol: Pre-Signed Time-Bounded URLs:**
  - Patients and authorized doctors never access S3 credentials.
  - The backend generates a cryptographically signed HMAC URL with an expiration period of **15 minutes** (`900 seconds`).
  - Request format:
    `GET https://s3.heartxai.internal/heartxai-clinical-reports/...pdf?X-Amz-Signature=...&X-Amz-Expires=900`

---

## 4. Resilience Patterns & Circuit Breakers

To protect HeartXAI from external service degradation, every outbound HTTP client is wrapped in a dedicated **Circuit Breaker** using Python's `circuitbreaker` library or custom asyncio state machine adhering to the standard three-state model:

```
               +-----------------------------------+
               |                                   |
               v   Failure Threshold Exceeded      |
       +--------------+     (> 5 failures in 30s)    +--------------+
  +--->|    CLOSED    |---------------------------->|     OPEN     |
  |    | Normal Mode  |                             | Fast-Fail    |
  |    +--------------+                             +--------------+
  |           ^                                            |
  |           | Success Rate >= 80%                        | Reset Timeout Elapsed
  |           | (in Probe Window)                          | (60 seconds)
  |    +--------------+                                    v
  |    |  HALF-OPEN   |                                    |
  +----| Probing Mode |<-----------------------------------+
       +--------------+
```

### 4.1 Circuit Breaker Configuration Parameter Matrix

| External Service | Failure Threshold | Consecutive Failures | Sliding Window | Reset Timeout (Open -> Half-Open) | Probe Requests (Half-Open) | Request Timeout (p99) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NPPES NPI Registry** | 50% | 5 | 30 seconds | 60 seconds | 3 | 3,000 ms |
| **Nominatim Geocoding** | 40% | 4 | 20 seconds | 45 seconds | 2 | 2,000 ms |
| **Overpass OSM API** | 50% | 3 | 30 seconds | 90 seconds | 2 | 5,000 ms |
| **Email Service (Resend)**| 30% | 5 | 60 seconds | 120 seconds | 5 | 4,000 ms |
| **S3 Storage (MinIO)** | 20% | 3 | 15 seconds | 30 seconds | 3 | 2,500 ms |

### 4.2 Retry & Exponential Backoff Specification
When a transient HTTP error occurs (`500 Internal Server Error`, `502 Bad Gateway`, `503 Service Unavailable`, `504 Gateway Timeout`, or socket timeout), HeartXAI applies **Full Jitter Exponential Backoff**:

$$\text{Delay}_k = \text{random}(0, \min(T_{\max}, T_{\text{base}} \times 2^k))$$

Where:
- $T_{\text{base}} = 500\text{ ms}$
- $T_{\max} = 15,000\text{ ms}$
- $k = \text{retry attempt index } (k \in \{0, 1, 2\})$
- Maximum retries: 3. Non-idempotent operations (POST without idempotency keys) are never retried unless idempotency is verified.

---

## 5. Graceful Degradation & Offline Fallback Hierarchy

HeartXAI enforces strict graceful degradation tiers to ensure that patient care and clinical risk scoring are never blocked by external API outages:

```
+----------------------------------------------------------------------------------------------------+
|                                    GRACEFUL DEGRADATION MATRIX                                     |
+----------------------+-----------------------------+-----------------------------------------------+
| External Component   | Online Operational Mode     | Offline / Degraded Fallback Mode              |
+----------------------+-----------------------------+-----------------------------------------------+
| NPPES NPI Registry   | Real-time validation of NPI | 1. Doctor registration marked "PENDING_VERIF" |
|                      | credentials upon submission | 2. Administrator alerted in Audit Dashboard   |
|                      |                             | 3. Doctor restricted to View-Only mode        |
+----------------------+-----------------------------+-----------------------------------------------+
| Overpass OSM API     | Live spatial query for      | 1. Query local PostGIS / SQLite pre-seeded    |
|                      | nearest cardiac hospitals   |    table (1,500 validated US cardiac centers) |
|                      |                             | 2. Display badge: "Static Offline Directory"  |
+----------------------+-----------------------------+-----------------------------------------------+
| Nominatim Geocoding  | Real-time ZIP to lat/long   | 1. Query local offline centroids lookup file  |
|                      | resolution                  |    (`assets/geodata/us_postal_codes.json`)    |
|                      |                             | 2. Fall back to state-level center coordinate |
+----------------------+-----------------------------+-----------------------------------------------+
| Transactional Email  | Immediate delivery via API  | 1. Emails persist in `outbox_emails` queue    |
|                      |                             | 2. System displays on-screen verification code|
|                      |                             |    in development/emergency mode              |
+----------------------+-----------------------------+-----------------------------------------------+
| S3 Object Storage    | PDF reports stored in S3    | 1. Reports stream directly to HTTP client     |
|                      | with 15-min pre-signed URLs | 2. Local encrypted spool directory backup    |
|                      |                             | 3. S3 upload queued for background replay     |
+----------------------+-----------------------------+-----------------------------------------------+
```

---

## 6. Integration Security & Credential Governance

1. **Zero-Trust External Boundary:** External APIs have zero visibility or direct network ingress into HeartXAI's private database, cache, or internal container network. All integrations are purely outbound HTTPS initiated from the backend.
2. **Credential Isolation:**
   - External credentials (`RESEND_API_KEY`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) are injected exclusively via environment variables or Docker secrets.
   - Credentials are never committed to version control, never serialized in client bundles, and never logged in plain text.
3. **PHI Egress Prevention:**
   - No clinical metrics (blood pressure, cholesterol, ECG, ST depression), patient names, or medical history are ever transmitted to Nominatim, OpenStreetMap, or NPPES.
   - Emails transmitted via the transactional email service contain zero clinical information (no risk scores, no biomarker values). Emails contain solely administrative authentication links or generic notifications stating: *"Your HeartXAI health summary has been updated. Log in to view your secure portal."*

---

## 7. Traceability Matrix

| Requirement ID | Integration Component | Mechanism / Protocol | Fallback Verified |
| :--- | :--- | :--- | :--- |
| **FR-11** | NPI Registry Integration | `ProviderVerificationService` (NPPES REST API) | Admin Queue Fallback |
| **FR-12** | Hospital Directory Integration| `HospitalDirectoryService` (Overpass QL + PostGIS) | Local Geodata Cache |
| **FR-14** | Clinical Report Archival | `ReportStorageService` (S3 Pre-signed URLs) | Local Spool Fallback |
| **FR-17** | Password Reset & Email Verification | `EmailDispatcherWorker` (Outbox Pattern + Resend) | Persistent DB Outbox |
| **NFR-04** | API Latency & Resilience | Circuit Breaker + Full Jitter Backoff | Sub-200ms Fast Fail |
| **NFR-07** | Data Privacy & Confidentiality| PHI Redaction on all Outbound Integrations | Zero PHI in Logs/URIs |

---

*Verified and signed off by Principal Software Architect & Integration Lead.*
