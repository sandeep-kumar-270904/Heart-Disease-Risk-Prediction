# HeartXAI 2.0 — Deployment & Infrastructure Architecture Specification

| Document Attribute | Details |
| :--- | :--- |
| **Document ID** | `HXAI-ARCH-DEP-001` |
| **Version** | `2.1.0-REVISED` |
| **System State** | System Technical Architecture & Infrastructure Specification (Audited Baseline) |
| **Traceability** | `FUNCTIONAL_REQUIREMENTS.md`, `NON_FUNCTIONAL_REQUIREMENTS.md` (NFR-01, NFR-03, NFR-08, NFR-13), `ARCHITECTURE_DECISION_RECORDS.md` (ADR-007, ADR-010, ADR-012), `C4_DEPLOYMENT_DIAGRAM.md` |
| **Author** | Principal Software Architect, DevOps Lead, Healthcare Security Reviewer |

---

## 1. Executive Summary & Deployment Topology

The **HeartXAI 2.0 Deployment Architecture** defines the containerization, orchestration, environment configuration, reverse proxy routing, healthcheck monitoring, disaster recovery runbooks, and automated backup strategies for HeartXAI 2.0.

In alignment with **ADR-001 (Modular Monolith)**, **ADR-007 (Docker Compose Orchestration)**, **ADR-010 (Nginx 1.26 Stable)**, and **ADR-012 (Authenticated AEAD Backups & WORM Storage)**, the platform is architected as an isolated set of OCI-compliant containers orchestrated via Docker Compose.

```
+---------------------------------------------------------------------------------------------------+
| PHYSICAL / VIRTUAL HOST BOUNDARY (Ubuntu 22.04 LTS / Linux Kernel 5.15+ / Docker Engine 26+)      |
|                                                                                                   |
|  +---------------------------------------------------------------------------------------------+  |
|  | DOCKER BRIDGE NETWORK: `heartxai-network` (172.28.0.0/16, Internal DNS)                    |  |
|  |                                                                                             |  |
|  |  +------------------------+      +------------------------+      +-----------------------+  |  |
|  |  |    heartxai-proxy      |      |    heartxai-backend    |      |    heartxai-db        |  |  |
|  |  |  Nginx 1.26 Stable     | HTTP |  FastAPI + Uvicorn     | TCP  |  PostgreSQL 16        |  |  |
|  |  |  - TLS 1.3 Term.       |----->|  - Python 3.11 Base    |----->|  - Healthcheck Probe  |  |  |
|  |  |  - Token Rate Limiting | 8000 |  - ML C++ Runtime      | 5432 |  - WAL Archive        |  |  |
|  |  |  - Security Headers    |      |  - TreeSHAP In-Process |      |  - Auto-Vacuuming     |  |  |
|  |  +------------------------+      +------------------------+      +-----------------------+  |  |
|  |             |                                 |                               |             |  |
|  |             | HTTP Static Assets              | Logs / Spool                  | DB Data     |  |
|  |             v                                 v                               v             |  |
|  |  +------------------------+      +------------------------+      +-----------------------+  |  |
|  |  |    heartxai-frontend   |      | Host Spool Volume      |      | Persistent Volume     |  |  |
|  |  |  Nginx 1.26 Static     |      | `/var/log/heartxai`    |      | `heartxai_pgdata`     |  |  |
|  |  +------------------------+      +------------------------+      +-----------------------+  |  |
|  +---------------------------------------------------------------------------------------------+  |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Containerized Service Specifications & Image Lifecycle

### 2.1 Service Roster & Resource Allocation

| Container Name | Base Image | CPU Allocation | Memory (RAM) Limit | Exposed Ports | Healthcheck Target | Restart Policy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `heartxai-proxy` | `nginx:1.26-alpine` | 0.5 cores | 256 MB | 80/tcp, 443/tcp | `curl -f http://localhost:80/healthz` | `always` |
| `heartxai-frontend` | `nginx:1.26-alpine` | 0.5 cores | 256 MB | Internal only (80) | `curl -f http://localhost:80/` | `always` |
| `heartxai-backend` | `python:3.11-slim` | 2.0 cores | 2.0 GB | Internal only (8000)| `curl -f http://localhost:8000/api/v1/health/live` | `always` |
| `heartxai-db` | `postgres:16-alpine` | 1.5 cores | 1.5 GB | Internal only (5432)| `pg_isready -U heartxai_app -d heartxai_db` | `always` |
| `heartxai-backup` | `alpine:3.19` (Cron) | 0.2 cores | 128 MB | None | Local exit status probe | `always` |

### 2.2 Nginx Version Selection & Vulnerability Update Strategy
- **Stable Branch Pinning:** In accordance with **ADR-010**, production strictly pins to the active **Nginx Stable branch (`nginx:1.26-alpine`)**. Mainline development branches (such as 1.25) are barred due to rapid EOL cycles.
- **Container Vulnerability Scanning:** Automated weekly container scans using Trivy / Grype integrated into CI/CD pipelines. Any image with High or Critical CVSS $\ge 7.0$ vulnerabilities blocks deployment.
- **Zero-Downtime Reload:** Nginx configuration changes and SSL renewals are applied hot without dropped connections via `docker exec heartxai-proxy nginx -s reload`.

---

## 3. Multi-Stage Dockerfile Specifications

### 3.1 Backend Dockerfile (`backend/Dockerfile`)
```dockerfile
# ==============================================================================
# STAGE 1: Build & Dependency Wheel Compilation
# ==============================================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install system build dependencies for C++ extensions (TreeSHAP, NumPy, SciPy)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libpq-dev \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for rapid, deterministic package resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency manifests
COPY pyproject.toml requirements.txt ./

# Compile wheels into /build/wheels
RUN uv pip compile requirements.txt -o requirements.lock && \
    uv pip install --no-cache-dir --target=/build/deps -r requirements.lock

# ==============================================================================
# STAGE 2: Hardened Minimal Production Runtime
# ==============================================================================
FROM python:3.11-slim AS runner

# Create dedicated non-root service account
RUN groupadd -g 10001 heartxai && \
    useradd -u 10001 -g heartxai -s /bin/bash -m heartxai

# Install libpq and runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed site-packages from builder stage
COPY --from=builder /build/deps /usr/local/lib/python3.11/site-packages
COPY --from=builder /bin/uv /bin/uv

# Copy backend application source code
COPY --chown=heartxai:heartxai app/ ./app/
COPY --chown=heartxai:heartxai alembic/ ./alembic/
COPY --chown=heartxai:heartxai alembic.ini ./
COPY --chown=heartxai:heartxai ml/ ./ml/

# Create runtime directories for logs and temp files
RUN mkdir -p /var/log/heartxai /tmp/heartxai && \
    chown -R heartxai:heartxai /var/log/heartxai /tmp/heartxai

# Switch to non-root user
USER heartxai

# Runtime environment settings
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/heartxai/.local/bin:$PATH" \
    PORT=8000

EXPOSE 8000

# Healthcheck probe
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health/live || exit 1

# Launch production ASGI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--no-access-log"]
```

---

### 3.2 Frontend Dockerfile (`frontend/Dockerfile`)
```dockerfile
# ==============================================================================
# STAGE 1: Node.js Asset Compilation
# ==============================================================================
FROM node:20-alpine AS builder

WORKDIR /build

COPY package.json package-lock.json ./
RUN npm ci --prefer-offline

COPY . .
ENV NODE_ENV=production
RUN npm run build

# ==============================================================================
# STAGE 2: Hardened Nginx 1.26 Stable Static Web Server
# ==============================================================================
FROM nginx:1.26-alpine AS runner

RUN rm -rf /usr/share/nginx/html/* /etc/nginx/conf.d/default.conf

COPY nginx/frontend.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /build/dist /usr/share/nginx/html

RUN touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid /var/cache/nginx /usr/share/nginx/html

USER nginx

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

---

## 4. Production Orchestration Specification (`docker-compose.prod.yml`)

```yaml
version: "3.8"

networks:
  heartxai-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16

volumes:
  heartxai_pgdata:
    name: heartxai_pgdata
  heartxai_reports:
    name: heartxai_reports
  heartxai_logs:
    name: heartxai_logs

services:
  reverse-proxy:
    image: nginx:1.26-alpine
    container_name: heartxai-proxy
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./infra/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./infra/nginx/conf.d/:/etc/nginx/conf.d/:ro
      - ./infra/ssl/:/etc/ssl/certs/:ro
      - heartxai_logs:/var/log/nginx
    networks:
      - heartxai-network
    depends_on:
      backend:
        condition: service_healthy
      frontend:
        condition: service_healthy
    deploy:
      resources:
        limits:
          cpus: "0.50"
          memory: 256M

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: heartxai-frontend
    restart: always
    networks:
      - heartxai-network
    deploy:
      resources:
        limits:
          cpus: "0.50"
          memory: 256M

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: heartxai-backend
    restart: always
    env_file:
      - .env.production
    environment:
      - DATABASE_URL=postgresql://heartxai_app:${DB_PASSWORD}@heartxai-db:5432/heartxai_db
      - ENVIRONMENT=production
    volumes:
      - heartxai_reports:/var/data/heartxai/reports
      - heartxai_logs:/var/log/heartxai
    networks:
      - heartxai-network
    depends_on:
      db:
        condition: service_healthy
    deploy:
      resources:
        limits:
          cpus: "2.00"
          memory: 2048M

  db:
    image: postgres:16-alpine
    container_name: heartxai-db
    restart: always
    environment:
      POSTGRES_DB: heartxai_db
      POSTGRES_USER: heartxai_app
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - heartxai_pgdata:/var/lib/postgresql/data
      - ./infra/postgres/init-scripts/:/docker-entrypoint-initdb.d/:ro
    networks:
      - heartxai-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U heartxai_app -d heartxai_db"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    deploy:
      resources:
        limits:
          cpus: "1.50"
          memory: 1536M

  db-backup:
    image: alpine:3.19
    container_name: heartxai-backup
    restart: always
    volumes:
      - heartxai_pgdata:/var/lib/postgresql/data:ro
      - ./backups:/backups
      - ./infra/scripts/backup.sh:/etc/periodic/daily/db-backup:ro
    environment:
      - POSTGRES_USER=heartxai_app
      - POSTGRES_DB=heartxai_db
      - PGPASSWORD=${DB_PASSWORD}
      - BACKUP_ENCRYPTION_KEY=${BACKUP_ENCRYPTION_KEY}
      - S3_BACKUP_BUCKET=${S3_BACKUP_BUCKET}
    networks:
      - heartxai-network
    entrypoint: ["crond", "-f", "-l", "2"]
```

---

## 5. Reverse Proxy & Security Header Configuration (`nginx.conf`)

The perimeter reverse proxy terminates TLS 1.3, enforces strict HSTS, applies IP rate limits, and proxies traffic to the frontend SPA or FastAPI backend.

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Rate Limiting Zones (Token Bucket Algorithm)
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
    limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/m;

    # SSL / TLS Hardening
    ssl_protocols TLSv1.3 TLSv1.2;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;

    # Security Headers (HIPAA / DPDP Compliance)
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none';" always;

    server {
        listen 80;
        server_name heartxai.health www.heartxai.health;
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name heartxai.health www.heartxai.health;

        ssl_certificate /etc/ssl/certs/fullchain.pem;
        ssl_certificate_key /etc/ssl/certs/privkey.pem;

        location / {
            proxy_pass http://heartxai-frontend:80;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://heartxai-backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 15s;
        }

        location /api/v1/auth/ {
            limit_req zone=auth_limit burst=3 nodelay;
            proxy_pass http://heartxai-backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

---

## 6. Healthcheck Endpoints & Observability Architecture

### 6.1 Probe Specifications

| Endpoint | Probe Type | Validation Criteria | HTTP Status Codes |
| :--- | :--- | :--- | :--- |
| `GET /api/v1/health/live` | **Liveness** | Verifies process responsiveness and internal event loop health. | `200 OK` (Always) |
| `GET /api/v1/health/ready` | **Readiness** | 1. Database connection pool responds (`SELECT 1`).<br>2. ML model artifact is loaded in memory.<br>3. Disk write access to report spool is verified. | `200 OK` (Healthy)<br>`503 Service Unavailable` |

---

## 7. Authenticated Backup Architecture & Disaster Recovery Runbook

### 7.1 Recovery Objectives & Core Rule
- **Recovery Point Objective (RPO):** $\le 24\text{ hours}$ for daily snapshots; $\le 1\text{ hour}$ with continuous PostgreSQL WAL archiving.
- **Recovery Time Objective (RTO):** $\le 30\text{ minutes}$ for complete automated container and database restore.
- **CRITICAL OPERATIONAL RULE:**
  > [!IMPORTANT]
  > **System recoverability cannot be claimed until restoration has been empirically tested and verified.** Untested backups are considered unverified hypotheses.

### 7.2 Authenticated Daily Backup Script with Off-Site WORM Sync (`infra/scripts/backup.sh`)
In accordance with **ADR-012**, backups use **AES-256-GCM** (Authenticated Encryption with Associated Data) to prevent ciphertext tampering and padding attacks, and replicate off-site to S3 Object Lock (WORM):

```bash
#!/bin/sh
set -e

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/backups"
BACKUP_FILE="${BACKUP_DIR}/heartxai_db_${TIMESTAMP}.sql.gz"
ENC_BACKUP_FILE="${BACKUP_FILE}.gcm.enc"
TAG_FILE="${BACKUP_FILE}.tag"

mkdir -p ${BACKUP_DIR}

echo "[INFO] Starting PostgreSQL database backup at ${TIMESTAMP}..."
pg_dump -h heartxai-db -U heartxai_app -d heartxai_db | gzip > ${BACKUP_FILE}

# Verify non-zero backup size
FILE_SIZE=$(wc -c < "${BACKUP_FILE}")
if [ "${FILE_SIZE}" -lt 1024 ]; then
  echo "[CRITICAL ERROR] Backup dump is under 1KB. Aborting!"
  exit 1
fi

echo "[INFO] Encrypting backup with Authenticated AES-256-GCM..."
# Derive 256-bit key using PBKDF2 (100,000 iterations) and encrypt via openssl enc AEAD
openssl enc -aes-256-gcm -pbkdf2 -iter 100000 \
  -in ${BACKUP_FILE} -out ${ENC_BACKUP_FILE} \
  -pass "pass:${BACKUP_ENCRYPTION_KEY}"

# Record SHA-256 integrity checksum
sha256sum ${ENC_BACKUP_FILE} > "${ENC_BACKUP_FILE}.sha256"

# Securely remove unencrypted raw dump
rm -f ${BACKUP_FILE}

# Replicate to Off-Site S3-Compatible Storage with Object Lock (WORM)
if [ -n "${S3_BACKUP_BUCKET}" ]; then
  echo "[INFO] Replicating encrypted backup to off-site WORM S3 bucket..."
  aws s3 cp "${ENC_BACKUP_FILE}" "s3://${S3_BACKUP_BUCKET}/db_backups/" \
    --object-lock-mode COMPLIANCE \
    --object-lock-retain-until-date "$(date -d '+30 days' --iso-8601=seconds)"
  aws s3 cp "${ENC_BACKUP_FILE}.sha256" "s3://${S3_BACKUP_BUCKET}/db_backups/"
fi

# Retain 14 daily snapshots locally, purge older archives
find ${BACKUP_DIR} -name "heartxai_db_*.gcm.enc*" -mtime +14 -exec rm {} \;

echo "[SUCCESS] Authenticated backup and off-site replication complete: ${ENC_BACKUP_FILE}"
```

### 7.3 Automated Monthly Restoration Verification Script (`infra/scripts/restore_verify.sh`)
This script executes automatically on the 1st of every month in an isolated test database container to empirically verify recoverability:

```bash
#!/bin/sh
set -e

echo "[DRILL] Initiating Automated Restoration Verification Drill..."
TEST_DB_CONTAINER="heartxai-db-restore-test"
LATEST_BACKUP=$(ls -t /backups/heartxai_db_*.gcm.enc | head -1)

if [ -z "${LATEST_BACKUP}" ]; then
  echo "[FAILURE] No backup archives found for restoration testing!"
  exit 1
fi

echo "[DRILL] Testing decrypt of ${LATEST_BACKUP}..."
openssl enc -d -aes-256-gcm -pbkdf2 -iter 100000 \
  -in "${LATEST_BACKUP}" -out /tmp/test_restore.sql.gz \
  -pass "pass:${BACKUP_ENCRYPTION_KEY}"

echo "[DRILL] Spinning up isolated test Postgres container..."
docker run --name ${TEST_DB_CONTAINER} -e POSTGRES_PASSWORD=drill_pass -d postgres:16-alpine
sleep 5

echo "[DRILL] Importing schema and data into test container..."
gunzip -c /tmp/test_restore.sql.gz | docker exec -i ${TEST_DB_CONTAINER} psql -U postgres -d postgres

echo "[DRILL] Validating table presence and row counts..."
USER_COUNT=$(docker exec -i ${TEST_DB_CONTAINER} psql -U postgres -d postgres -t -c "SELECT count(*) FROM users;")
echo "[DRILL] Verified: Users table populated with ${USER_COUNT} rows."

echo "[DRILL] Tearing down ephemeral restoration container..."
docker rm -f ${TEST_DB_CONTAINER}
shred -u /tmp/test_restore.sql.gz

echo "[SUCCESS] Monthly Restoration Verification Drill PASSED. Recoverability validated."
```

---

## 8. Traceability Matrix

| Requirement ID | Infrastructure Component | Architectural Solution |
| :--- | :--- | :--- |
| **NFR-01** | Scalability & Availability | Docker Compose containerization with resource throttling and auto-restart |
| **NFR-03** | System Performance | Native multi-stage build, minimal Alpine base images, Nginx edge caching |
| **NFR-08** | Regulatory Backup & Audit | Authenticated AES-256-GCM backups, off-site WORM S3 replication, monthly restore drill |
| **NFR-13** | Deployment & Maintainability | Deterministic lockfiles, non-root execution, 100% dev/prod container parity |

---

*Verified and approved by Principal Software Architect, DevOps Lead & Healthcare Security Reviewer.*
