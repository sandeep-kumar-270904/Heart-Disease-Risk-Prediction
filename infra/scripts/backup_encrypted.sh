#!/usr/bin/env bash
# HeartXAI 2.0 — AES-256-GCM Authenticated Encrypted Database Backup (ADR-012)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
DB_CONTAINER="${DB_CONTAINER:-heartxai-staging-db}"
POSTGRES_USER="${POSTGRES_USER:-heartxai_user}"
POSTGRES_DB="${POSTGRES_DB:-heartxai_db}"
: "${BACKUP_ENCRYPTION_KEY:?BACKUP_ENCRYPTION_KEY env var is required (keep separate from archive)}"

mkdir -p "${BACKUP_DIR}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_FILE="${BACKUP_DIR}/heartxai_${TIMESTAMP}.sql.gz.gcm"
SHA_FILE="${OUT_FILE}.sha256"

echo "[backup] Streaming pg_dump -> gzip -> AES-256-GCM AEAD (zero plaintext temp files)..."
docker exec "${DB_CONTAINER}" pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" --clean --if-exists \
  | gzip -9 \
  | python3 "${REPO_ROOT}/scripts/backup_aead.py" encrypt --output "${OUT_FILE}"

sha256sum "${OUT_FILE}" > "${SHA_FILE}"
echo "[backup] Authenticated backup written: ${OUT_FILE}"
echo "[backup] Notice: upload ${OUT_FILE} and ${SHA_FILE} offsite (never co-locate BACKUP_ENCRYPTION_KEY)."
