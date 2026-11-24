#!/usr/bin/env bash
# HeartXAI 2.0 — AES-256-GCM Authenticated Disaster Recovery Restore (ADR-012)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
BACKUP_FILE="${1:?Usage: restore_encrypted.sh <path_to_backup.sql.gz.gcm>}"
SHA_FILE="${BACKUP_FILE}.sha256"
DB_CONTAINER="${DB_CONTAINER:-heartxai-staging-db}"
POSTGRES_USER="${POSTGRES_USER:-heartxai_user}"
POSTGRES_DB="${POSTGRES_DB:-heartxai_db}"
: "${BACKUP_ENCRYPTION_KEY:?BACKUP_ENCRYPTION_KEY env var is required}"

if [[ -f "${SHA_FILE}" ]]; then
  echo "[restore] Verifying SHA-256 archive checksum..."
  sha256sum -c "${SHA_FILE}"
fi

echo "[restore] Verifying AES-256-GCM authentication tag & restoring ${DB_CONTAINER} (no temp files)..."
python3 "${REPO_ROOT}/scripts/backup_aead.py" decrypt --input "${BACKUP_FILE}" \
  | gunzip \
  | docker exec -i "${DB_CONTAINER}" psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}"

echo "[restore] Authenticated restore completed cleanly."
