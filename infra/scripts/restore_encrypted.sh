#!/usr/bin/env bash
# HeartXAI 2.0 — Disaster Recovery Encrypted Backup Verification & Restore (ADR-012)
set -euo pipefail

BACKUP_FILE="${1:?Usage: restore_encrypted.sh <path_to_backup.sql.gz.enc>}"
SHA_FILE="${BACKUP_FILE}.sha256"
DB_CONTAINER="${DB_CONTAINER:-heartxai-staging-db}"
POSTGRES_USER="${POSTGRES_USER:-heartxai_user}"
POSTGRES_DB="${POSTGRES_DB:-heartxai_db}"
BACKUP_KEY="${BACKUP_ENCRYPTION_KEY:?BACKUP_ENCRYPTION_KEY env var is required}"

if [[ -f "${SHA_FILE}" ]]; then
  echo "[restore] Verifying SHA-256 integrity checksum..."
  sha256sum -c "${SHA_FILE}"
fi

echo "[restore] Decrypting and restoring database into ${DB_CONTAINER}..."
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -pass env:BACKUP_ENCRYPTION_KEY -in "${BACKUP_FILE}" \
  | gunzip \
  | docker exec -i "${DB_CONTAINER}" psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}"

echo "[restore] Disaster recovery restore completed cleanly."
