# HeartXAI 2.0 — Final Repository Structure
**Document ID:** HX-PR-012  
**Version:** 1.0.0  
**Phase:** 12 — Final Pre-Implementation Audit, Architecture Consolidation & Master Development Roadmap  
**Author:** Staff Systems Architect & DevOps Engineer  
**Status:** Approved for Implementation Planning  
**Date:** November 2026  

---

## 1. Executive Summary

A clean, predictable, and modular repository structure prevents code duplication, clarifies boundaries of responsibility, and enforces separation of concerns across the frontend, backend, machine learning, and infrastructure tiers.

This document specifies the canonical directory layout for the HeartXAI 2.0 monorepo.

---

## 2. Master Repository Tree Layout

```
heartxai-2.0/
├── .github/                              # CI/CD Workflows & Automation
│   ├── workflows/
│   │   ├── ci-backend.yml                # Pytest, Ruff, Mypy, Bandit
│   │   ├── ci-frontend.yml               # Vitest, ESLint, TypeScript, axe-core
│   │   ├── ci-ml.yml                     # ML model calibration & invariant tests
│   │   └── cd-staging.yml                # Staging deployment pipeline
│   └── pull_request_template.md          # PR Definition of Done checklist
│
├── docs/                                 # Architectural & Engineering Specifications
│   ├── backend/                          # Phase 07 Backend Architecture Specs (18 files)
│   ├── design/                           # Phase 04/05 Design System Specs (16 files)
│   ├── devops/                           # Phase 10 DevOps & Infrastructure Specs (18 files)
│   ├── frontend/                         # Phase 06 Frontend Engineering Specs (14 files)
│   ├── ml/                               # Phase 08 ML Research & Calibration Specs (19 files)
│   ├── project-readiness/                # Phase 12 Consolidation & Audit Blueprints (18 files)
│   ├── quality/                          # Phase 11 Testing & QA Framework Specs (21 files)
│   └── security/                         # Phase 09 Security & Threat Model Specs (19 files)
│
├── frontend/                             # React 18 + TypeScript + Vite Client
│   ├── public/                           # Static assets, favicon, manifest
│   ├── src/
│   │   ├── assets/                       # SVG icons, illustrations, logos
│   │   ├── components/                   # Shared UI component primitives
│   │   │   ├── feedback/                 # Alerts, Modals, Progress, Badges
│   │   │   ├── forms/                    # Input, Select, Toggle, Slider
│   │   │   ├── layout/                   # Header, Footer, Sidebar, EmergencyBanner
│   │   │   └── ui/                       # Radix UI headless primitives
│   │   ├── features/                     # Domain-driven feature modules
│   │   │   ├── admin/                    # Admin console, audit log viewer
│   │   │   ├── assessment/               # Results view, SHAP charts, PDF export
│   │   │   ├── auth/                     # Login, Register, ForgotPassword
│   │   │   ├── directory/                # Doctor & hospital search, filters
│   │   │   ├── doctor/                   # Doctor portal, shared assessment review
│   │   │   └── intake/                   # 14-feature multi-step intake wizard
│   │   ├── hooks/                        # Custom React hooks (useAuth, useIntake)
│   │   ├── lib/                          # Utility functions, formatters, unit converter
│   │   ├── routes/                       # React Router v6 route configuration
│   │   ├── services/                     # API client methods (Axios / TanStack Query)
│   │   ├── stores/                       # Zustand client UI state stores
│   │   ├── types/                        # TypeScript type definitions & interfaces
│   │   ├── App.tsx                       # Root application component
│   │   ├── index.css                     # Tailwind CSS directives & custom styles
│   │   └── main.tsx                      # Application DOM entry point
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── backend/                              # FastAPI 0.111 + SQLAlchemy 2.0 Async Backend
│   ├── alembic/                          # Database migrations
│   │   ├── versions/                     # Versioned migration scripts
│   │   └── env.py                        # Migration environment config
│   ├── app/
│   │   ├── api/                          # HTTP route handlers
│   │   │   └── v1/
│   │   │       ├── routes/               # Modular endpoints (auth, assessments, directory)
│   │   │       └── api.py                # Consolidated v1 APIRouter
│   │   ├── core/                         # Core configurations & cross-cutting concerns
│   │   │   ├── config.py                 # Pydantic Settings & environment variables
│   │   │   ├── database.py               # Async SQLAlchemy engine & session factory
│   │   │   ├── logging.py                # Structured JSON logging config
│   │   │   └── security.py               # Argon2id hashing, JWT encoding/decoding
│   │   ├── ml/                           # ML Serving & Inference Components
│   │   │   ├── artifacts/                # Versioned model weights (.joblib / .onnx)
│   │   │   ├── explainers/               # TreeSHAP & DiCE counterfactual wrappers
│   │   │   ├── preprocessors/            # Feature standardization & transformers
│   │   │   └── inference_service.py      # High-performance in-process inference engine
│   │   ├── models/                       # SQLAlchemy 2.0 Declarative ORM models
│   │   │   ├── assessment.py             # Assessment, SHAP values, counterfactuals
│   │   │   ├── audit.py                  # Immutable audit log model
│   │   │   ├── consent.py                # Patient-doctor consent grants
│   │   │   ├── directory.py              # Doctor, hospital, emergency contacts
│   │   │   └── user.py                   # User identity, patient & doctor profiles
│   │   ├── schemas/                      # Pydantic v2 validation & response schemas
│   │   │   ├── assessment.py             # Assessment intake & result envelopes
│   │   │   ├── auth.py                   # Login, register, token schemas
│   │   │   ├── country.py                # Country configuration & unit schemas
│   │   │   └── directory.py              # Directory query & provider schemas
│   │   ├── services/                     # Core business logic layer
│   │   │   ├── assessment_service.py     # Assessment lifecycle orchestration
│   │   │   ├── auth_service.py           # Identity, password, and session rules
│   │   │   ├── consent_service.py        # Cryptographic grant generation & checks
│   │   │   ├── directory_service.py      # Geo-spatial search & provider filtering
│   │   │   └── export_service.py         # Signed clinical PDF report generation
│   │   └── main.py                       # FastAPI application factory & lifespan
│   ├── tests/                            # Pytest backend test suite
│   │   ├── conftest.py                   # Test fixtures (PostgreSQL container, client)
│   │   ├── test_api_health.py            # Health probe tests (passing)
│   │   ├── test_database_models.py       # ORM relationship tests (passing)
│   │   └── test_security.py              # Argon2id & JWT token tests (passing)
│   ├── alembic.ini
│   ├── pyproject.toml
│   └── requirements.txt
│
├── ml/                                   # Offline Research, Training & Validation
│   ├── data/
│   │   ├── raw/                          # Original Cleveland dataset (read-only)
│   │   └── processed/                    # Cleaned, stratified train/test datasets
│   ├── notebooks/                        # Exploratory research & calibration checks
│   ├── pipelines/
│   │   ├── prepare_data.py               # Leakage-free data cleaning & split script
│   │   ├── train_model.py                # XGBoost training & probability calibration
│   │   ├── evaluate_model.py             # Brier score, ECE, ROC-AUC, subgroup metrics
│   │   └── generate_shap.py              # TreeSHAP validation & baseline checks
│   ├── registry/                         # Model metadata, performance cards, hashes
│   └── tests/                            # ML-specific unit & invariant tests
│
├── infra/                                # Infrastructure, Containers & Deployment
│   ├── docker/
│   │   ├── Dockerfile.backend            # Multi-stage Python 3.11 slim image
│   │   ├── Dockerfile.frontend           # Multi-stage Vite build + Nginx runtime
│   │   └── Dockerfile.ml                 # Standalone ML training environment
│   ├── nginx/
│   │   ├── nginx.conf                    # Production reverse proxy, SSL, HSTS, CSP
│   │   └── conf.d/default.conf           # Upstream routing rules
│   ├── scripts/
│   │   ├── backup_encrypted.sh           # AES-256-GCM database backup script (ADR-012)
│   │   ├── restore_encrypted.sh          # Disaster recovery restore verification
│   │   └── health_check.sh               # Staging container health check probe
│   └── docker-compose.yml                # Multi-service local & VPS deployment
│
├── shared/                               # Canonical Cross-Tier Contracts
│   ├── data-dictionary.json              # Canonical biomarker schema & bounds
│   └── country-profiles.json             # Country configurations (US, IN, UK)
│
├── .gitignore
├── .editorconfig
└── README.md
```

---

## 3. Schema Governance & Single Source of Truth

To avoid schema divergence between the React client, FastAPI server, and ML model:
1. `shared/data-dictionary.json` serves as the authoritative definition of all 13 clinical biomarkers, acceptable ranges, and conversion factors.
2. Pydantic v2 schemas in `backend/app/schemas/` are generated directly against this dictionary.
3. TypeScript interfaces in `frontend/src/types/` mirror the Pydantic schemas with 100% naming and nullability parity.
4. Any change to a biomarker definition requires an explicit update to `data-dictionary.json` followed by running code-generation scripts.
