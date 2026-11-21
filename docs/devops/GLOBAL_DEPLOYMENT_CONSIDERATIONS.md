# GLOBAL DEPLOYMENT AND DATA RESIDENCY ARCHITECTURE

**Document Reference:** `docs/devops/GLOBAL_DEPLOYMENT_CONSIDERATIONS.md`  
**Phase:** 10 — DevOps, Infrastructure, Deployment Architecture & Release Engineering  
**Status:** Approved Technical Architecture  
**Author:** International Infrastructure Architect & Regulatory Governance Lead  
**Traceability:** NFR-LEGAL-01, NFR-PRIV-01, ADR-011  

---

## 1. Executive Summary & The Data Sovereignty Mandate

In strict alignment with **ADR-011 (Global Country-Configurable Architecture)**, HeartXAI 2.0 is architected for international configurability without hard-coding a single geographic region or assuming worldwide operational coverage at launch.

Healthcare data regulations worldwide strictly govern cross-border data flows:
- **India (DPDP Act 2023):** Cross-border transfers permitted to whitelisted jurisdictions, but sensitive health records are subject to emerging statutory data localization notifications by the central government.
- **European Union (GDPR Chapter V):** Storing or transferring EU resident personal health data to US datacenters without an Adequacy Decision (or valid Standard Contractual Clauses with robust supplementary encryption) is illegal.
- **United States (HIPAA):** Requires that Protected Health Information (PHI) processed for US healthcare providers reside within HIPAA-compliant, BAA-covered infrastructure.

> [!IMPORTANT]
> **Anti-Pattern Rejection:**  
> A single cloud datacenter (e.g. AWS `us-east-1` in Virginia) can **NEVER** serve as a compliant global deployment region for all international users. HeartXAI establishes an infrastructure pattern where independent regional deployment stacks can be spun up per sovereign jurisdiction using identical container templates.

---

## 2. Multi-Region Sovereign Infrastructure Topology

```mermaid
graph TD
    User([International Client Browser]) --> GeoDNS{Cloudflare Geo-DNS & Country Routing}

    subgraph RegionIN ["India Sovereign Stack (AWS ap-south-1 Mumbai)"]
        NginxIN["Nginx Proxy (IST Timezone)"]
        AppIN["FastAPI Backend (India Directory Adapters)"]
        DBIN[("PostgreSQL 16 (Local Mumbai Storage)")]
        NginxIN --> AppIN --> DBIN
    end

    subgraph RegionEU ["European Sovereign Stack (AWS eu-central-1 Frankfurt)"]
        NginxEU["Nginx Proxy (CET Timezone)"]
        AppEU["FastAPI Backend (EU GDPR Privacy Adapters)"]
        DBEU[("PostgreSQL 16 (Local Frankfurt Storage)")]
        NginxEU --> AppEU --> DBEU
    end

    subgraph RegionUS ["US Sovereign Stack (AWS us-east-1 N. Virginia)"]
        NginxUS["Nginx Proxy (EST/PST Timezones)"]
        AppUS["FastAPI Backend (US HIPAA BAA Stack)"]
        DBUS[("PostgreSQL 16 (Local US Storage)")]
        NginxUS --> AppUS --> DBUS
    end

    GeoDNS -->|Country: India (IN)| RegionIN
    GeoDNS -->|Country: Germany, France, etc. (EU)| RegionEU
    GeoDNS -->|Country: United States (US)| RegionUS
```

---

## 3. Country-Specific Runtime Configuration Injection

Rather than maintaining separate codebases for each country, the application standardizes a single immutable container image. Regional behavior is injected at runtime via environment variables and localization headers:

```ini
# Canonical Production Environment Configuration (India Sovereign Stack)
HEARTXAI_COUNTRY_CODE=IN
HEARTXAI_DEFAULT_LOCALE=en-IN
HEARTXAI_SUPPORTED_LANGUAGES=en,hi,ta,te,mr,bn
HEARTXAI_TIMEZONE=Asia/Kolkata
HEARTXAI_CURRENCY=INR
HEARTXAI_MEASUREMENT_UNIT_CHOL=mg_dl
HEARTXAI_MEASUREMENT_UNIT_GLUC=mg_dl
HEARTXAI_EMERGENCY_NUMBER=112
HEARTXAI_DIRECTORY_ADAPTER=app.services.directory.india_adapter
HEARTXAI_DATA_RESIDENCY_REGION=ap-south-1
```

### 3.1 Measurement Unit Harmonization
- **Blood Cholesterol:**
  - United States & India: Reported in **$\text{mg/dL}$**.
  - European Union & United Kingdom: Reported in **$\text{mmol/L}$**.
- **Backend Harmonization:** The API input schema detects client unit preferences from `X-Country-Code` or explicit payload headers and deterministically converts $\text{mmol/L}$ to canonical $\text{mg/dL}$ ($\text{chol}_{\text{mg/dL}} = \text{chol}_{\text{mmol/L}} \times 38.67$) before passing feature vectors to the XGBoost tensor runtime.

---

## 4. Regional Service Availability & Launch Verification Checklist

Before onboarding real patients or declaring an operational launch in any specific target country, the following four-stage verification protocol must be executed:

1. **Infrastructure Residency Verification:** Confirm that compute instances, PostgreSQL storage volumes, S3 buckets, and backup archives physically reside within the sovereign geographic boundary of the launch nation.
2. **Directory Source Licensing & Availability Audit:** Verify that the third-party physician and hospital directory data sources for that country have documented API access, approved licensing terms, and confirmed rate limits.
3. **Statutory Privacy Notice Translation:** Confirm that mandatory legal privacy notices have been translated into official regional languages (e.g. Schedule 8 languages for India, German/French for EU).
4. **Local Emergency Dispatch Routing:** Verify that emergency cardiovascular symptom warnings route the user to verified local emergency phone numbers (e.g. 112 in India/EU, 911 in US) and direct the patient to localized emergency facilities.
