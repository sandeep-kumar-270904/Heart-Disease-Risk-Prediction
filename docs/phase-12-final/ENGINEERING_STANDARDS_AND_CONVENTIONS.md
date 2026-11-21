# HeartXAI 2.0 — Engineering Standards & Conventions
**Document ID:** HX-PR-013  
**Version:** 1.0.0  
**Phase:** 12 — Final Pre-Implementation Audit, Architecture Consolidation & Master Development Roadmap  
**Author:** Staff Engineer & Frontend Quality Lead  
**Status:** Approved for Implementation Planning  
**Date:** November 2026  

---

## 1. Executive Summary

Consistent engineering practices and strict coding standards ensure code readability, reduce cognitive overhead during code reviews, eliminate common classes of software bugs, and prevent the introduction of security vulnerabilities.

This document establishes the official engineering conventions for all developers and AI agents contributing to HeartXAI 2.0.

---

## 2. Language-Specific Coding Standards

### 2.1 Python / FastAPI Backend Standards
- **Python Version:** 3.11+ strictly enforced.
- **Type Annotations:** 100% type annotations required for all function arguments, return values, and class attributes. `mypy --strict` must pass with zero errors.
- **Linter & Formatter:** **Ruff** is used for both linting and formatting. Line length is capped at 100 characters.
- **Async Conventions:** All I/O-bound operations (database queries, Redis cache reads, external HTTP calls) must use native `async`/`await`. CPU-bound ML inferences run synchronously or in a thread pool executor.
- **Pydantic v2 Idioms:** Use `model_validate()`, `model_dump()`, and `Field(..., description=...)`. Avoid deprecated v1 methods (`dict()`, `parse_obj()`).

### 2.2 TypeScript / React Frontend Standards
- **TypeScript Version:** 5.4+ with `strict: true` in `tsconfig.json`. Use of `any` is strictly prohibited; use `unknown` with type narrowing.
- **Linter & Formatter:** ESLint + Prettier. Line length capped at 100 characters.
- **Functional Components:** All React components must be written as functional components with explicit props interfaces:
  ```tsx
  interface AssessmentCardProps {
    readonly assessment: AssessmentSummary;
    readonly onSelect: (id: string) => void;
  }
  export const AssessmentCard: React.FC<AssessmentCardProps> = ({ assessment, onSelect }) => { ... };
  ```
- **State Management:** Keep server state in TanStack Query (`useQuery`, `useMutation`). Keep transient client UI state in lightweight Zustand stores. Never store server responses in global Redux/Zustand stores.

### 2.3 SQL & Database Standards
- **PostgreSQL 16:** All table names and column names must be lowercase `snake_case`.
- **Primary Keys:** UUIDv7 preferred for all public-facing and transactional entities.
- **Foreign Keys:** Must have explicit `ON DELETE CASCADE` or `ON DELETE RESTRICT` constraints declared.
- **Timestamps:** Every table must have `created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP` and `updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP`.

---

## 3. Standardized Error Handling Architecture

All API endpoints must return error responses conforming to **RFC 7807 (Problem Details for HTTP APIs)**:

```json
{
  "type": "https://heartxai.org/errors/validation-failed",
  "title": "Unprocessable Entity",
  "status": 422,
  "detail": "Resting blood pressure must be between 60 and 260 mmHg.",
  "instance": "/api/v1/assessments",
  "request_id": "req_01HPX789ABCD",
  "invalid_params": [
    {
      "name": "resting_blood_pressure",
      "reason": "Value 320 exceeds maximum plausible physiological limit of 260 mmHg."
    }
  ]
}
```

**Implementation Rule:** Unhandled server exceptions (500) must never leak Python tracebacks or database queries to the client. The exception handler must log the full traceback internally with the `request_id` and return a generic 500 Problem Details response.

---

## 4. Structured Logging & PHI Sanitization

All logs are emitted as structured JSON to `stdout` for ingestion by Prometheus/Grafana or centralized log aggregators:

```json
{
  "timestamp": "2026-11-21T18:45:00.123Z",
  "level": "INFO",
  "service": "heartxai-backend",
  "request_id": "req_01HPX789ABCD",
  "actor_id": "usr_01HPX1234",
  "actor_role": "patient",
  "action": "ASSESSMENT_INFERENCE_COMPLETED",
  "duration_ms": 14.2,
  "status_code": 201
}
```

### Strict PHI Scrubbing Invariant
**Logs must NEVER contain:**
- Patient plaintext passwords or token strings.
- Personally Identifiable Information: full names, raw email addresses, home addresses, phone numbers.
- Unmasked medical biomarker inputs (e.g., specific blood pressure or cholesterol values).

---

## 5. Git & Source Control Conventions

### 5.1 Git Branching Model (GitFlow Lite)
- `main`: Production-ready, deployable code only. Protected branch; direct pushes prohibited.
- `develop`: Integration branch for completed milestones.
- `feature/<milestone-id>-<short-description>`: Feature branches created for individual milestone tasks (e.g., `feature/m08-intake-wizard`).
- `fix/<issue-id>-<short-description>`: Bugfix branches.

### 5.2 Conventional Commits Format
Every git commit message must follow the Conventional Commits specification:

```
<type>(<scope>): <short imperative description>

[optional longer body explaining context and rationale]

[optional footer referencing issues or ADRs]
```

**Allowed Types:**
- `feat`: A new user-facing feature.
- `fix`: A bug fix.
- `docs`: Documentation changes only.
- `test`: Adding or correcting tests.
- `refactor`: Code change that neither fixes a bug nor adds a feature.
- `chore`: Build process, CI configuration, or dependency updates.

**Example:**
```
feat(ml): integrate in-process calibrated XGBoost inference worker

- Load calibrated model artifact via joblib at application startup
- Implement synchronous feature vector normalization pipeline
-Persist prediction score and risk category to assessments table
- Add unit test verifying inference execution under 20ms

Closes #42. Ref: ADR-001
```

---

## 6. Pull Request Review & Quality Gates

Every pull request must pass the automated CI pipeline before review:
1. `git status` clean with zero unformatted files.
2. `ruff check .` and `ruff format --check .` pass.
3. `tsc --noEmit` and `eslint .` pass.
4. Pytest and Vitest test suites execute with 100% pass rate.
5. Code coverage meets or exceeds established thresholds.
6. Pull request template completed with verification steps and testing evidence.
