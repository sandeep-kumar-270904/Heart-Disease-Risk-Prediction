#!/usr/bin/env bash
# HeartXAI 2.0 — AES-256 Authenticated Encrypted Database Backup (ADR-012)
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
DB_CONTAINER="${DB_CONTAINER:-heartxai-staging-db}"
POSTGRES_USER="${POSTGRES_USER:-heartxai_user}"
POSTGRES_DB="${POSTGRES_DB:-heartxai_db}"
BACKUP_KEY="${BACKUP_ENCRYPTION_KEY:?BACKUP_ENCRYPTION_KEY env var is required}"

mkdir -p "${BACKUP_DIR}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_FILE="${BACKUP_DIR}/heartxai_${TIMESTAMP}.sql.gz.enc"
SHA_FILE="${OUT_FILE}.sha256"

echo "[backup] Streaming pg_dump -> gzip -> OpenSSL AES-256-CBC/PBKDF2..."
docker exec "${DB_CONTAINER}" pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" --clean --if-exists \
  | gzip -9 \
  | openssl enc -aes-256-cbc -pbkdf2 -iter 200000 -salt -pass env:BACKUP_ENCRYPTION_KEY -out "${OUT_FILE}"

sha256sum "${OUT_FILE}" > "${SHA_FILE}"
echo "[backup] Encrypted backup written cleanly: ${OUT_FILE}"
