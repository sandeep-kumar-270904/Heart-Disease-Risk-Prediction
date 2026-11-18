# ENCRYPTION AND SECRETS MANAGEMENT SPECIFICATION

**Document Reference:** `docs/security/ENCRYPTION_AND_SECRETS_MANAGEMENT.md`  
**Phase:** 09 — Security, Privacy, Data Protection & Threat Modelling  
**Status:** Approved Technical Design  
**Author:** Cryptographic Systems Specialist & Infrastructure Security Lead  
**Traceability:** NFR-SEC-01, NFR-SEC-04, NFR-SEC-08, ADR-009, ADR-011  

---

## 1. Executive Summary & Epistemological Stance

Cryptography is a foundational defense mechanism, but encryption alone does not make an application secure if key management is flawed, algorithms are misused, or authorization controls are absent.

HeartXAI 2.0 implements end-to-end cryptographic controls covering:
1. **Data in Transit:** Strict TLS 1.3 with forward secrecy ciphers across all external and internal networks.
2. **Data at Rest:** Multi-tiered encryption encompassing volume encryption (AES-256-XTS), column-level envelope encryption (AES-256-GCM), and object-store server-side encryption.
3. **Backup Protection:** Authenticated encryption (AES-256-GCM) with strict nonce isolation.
4. **Secrets Governance:** Centralized cloud Key Management Service (AWS KMS, GCP Cloud KMS, or HashiCorp Vault), zero secrets in source control, automated 90-day key rotation, and emergency key revocation procedures.

---

## 2. Cryptographic Controls for Data in Transit

### 2.1 Public Ingress & Transport Layer Security (TLS)
- **Protocol Enforced:** TLS 1.3 as primary; TLS 1.2 permitted strictly with approved AEAD ciphers. Legacy protocols (SSLv3, TLS 1.0, TLS 1.1) are explicitly disabled in Nginx / Cloudflare.
- **Approved Cipher Suites:**
  - `TLS_AES_256_GCM_SHA384` (TLS 1.3)
  - `TLS_CHACHA20_POLY1305_SHA256` (TLS 1.3)
  - `ECDHE-ECDSA-AES256-GCM-SHA384` (TLS 1.2)
  - `ECDHE-RSA-AES256-GCM-SHA384` (TLS 1.2)
- **Forward Secrecy:** Enforced via Elliptic Curve Diffie-Hellman Ephemeral (`ECDHE`) key exchange (`curve X25519` or `secp384r1`).
- **HTTP Strict Transport Security (HSTS):**
  ```http
  Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
  ```
- **Certificate Management:** Automated issuance and 60-day renewal via Let's Encrypt (ACME protocol) or Cloud KMS managed certificates.

### 2.2 Internal Service Communication (East-West Traffic)
- Communication between the reverse proxy and FastAPI, and between FastAPI and PostgreSQL/Redis, runs within private isolated VPC subnets.
- PostgreSQL connections enforce TLS with full certificate verification:
  ```text
  postgresql+asyncpg://heartxai_app:***@db.internal:5432/heartxai_db?ssl=verify-full&sslrootcert=/etc/ssl/certs/db-root.crt
  ```

---

## 3. Cryptographic Controls for Data at Rest

### 3.1 Transparent Storage Volume Encryption
All persistent physical disks hosting PostgreSQL, Redis, and container volumes are encrypted at the block storage layer using **AES-256-XTS** with provider-managed hardware security modules (FIPS 140-2 Level 3 compliant).

### 3.2 Application-Level Envelope Encryption for Sensitive Columns
For highly sensitive attributes (e.g. TOTP MFA seeds, external medical identifiers):
1. **Data Encryption Key (DEK):** A unique 256-bit AES key generated locally per encryption operation via `os.urandom(32)`.
2. **Key Encryption Key (KEK):** A master key stored securely in Key Management Service (KMS).
3. **Payload Construction:**
   $$\text{Ciphertext} = \text{AES-256-GCM}(\text{DEK}, \text{Plaintext}, \text{Nonce}, \text{AAD})$$
   $$\text{Encrypted DEK} = \text{KMS.Encrypt}(\text{KEK}, \text{DEK})$$
   $$\text{Stored Record} = \text{Encrypted DEK} \parallel \text{Nonce (12 bytes)} \parallel \text{Ciphertext} \parallel \text{Auth Tag (16 bytes)}$$

### 3.3 File and Report Encryption
Uploaded medical PDFs and generated clinical summaries are stored in private object storage buckets with mandatory **SSE-KMS** (Server-Side Encryption with Customer Master Keys) using AES-256.

---

## 4. Authenticated Backup Encryption Specification

Unencrypted or unauthenticated backups represent a severe vulnerability. Backups must be protected against both passive eavesdropping and active tampering:

### 4.1 Cryptographic Standard: AES-256-GCM
- **Algorithm:** Authenticated Encryption with Associated Data (AEAD) using AES-256 in Galois/Counter Mode (GCM).
- **Key Size:** 256 bits (32 bytes).
- **Nonce / Initialization Vector (IV):** Exactly 96 bits (12 bytes), generated freshly for every backup archive chunk using `secrets.token_bytes(12)`.
- **Authentication Tag:** 128 bits (16 bytes), verifying ciphertext authenticity and preventing silent corruption or bit-flipping attacks.

```python
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt_backup_archive(tar_stream: bytes, backup_kek: bytes) -> bytes:
    """Encrypt backup payload using AES-256-GCM with unique 96-bit nonce."""
    aesgcm = AESGCM(backup_kek)
    nonce = os.urandom(12) # 96-bit unique IV
    # Authenticate header metadata as Additional Authenticated Data (AAD)
    aad = b"heartxai_backup_v2"
    ciphertext = aesgcm.encrypt(nonce, tar_stream, aad)
    # Output: Header + Nonce + Ciphertext (includes 16-byte GCM tag)
    return aad + b"::" + nonce + ciphertext
```

---

## 5. Secrets Management & Key Lifecycle Governance

### 5.1 Zero Secrets in Source Code
- **Repository Policy:** No production passwords, JWT signing keys, database connection strings, or API tokens may exist in Git commits or `.env` files.
- **Enforcement:** Pre-commit hooks (`gitleaks`) and GitHub Actions Secret Scanning block any push containing credential patterns.
- **Existing Repository Inspection:** Verified that `backend/app/core/config.py` contains a documented development placeholder (`hxai-insecure-dev-key...`), which is overridden in production by environment variables. No real production secrets exist in the repository.

### 5.2 Key Hierarchy & Secrets Storage
Secrets are injected into container runtimes at initialization via environment variables populated by HashiCorp Vault or Cloud Secrets Manager:

```mermaid
graph TD
    RootKMS["Cloud KMS / Hardware Security Module (FIPS 140-2 Level 3)"] --> MasterKey["Key Encryption Key (KEK / Master Key)"]
    MasterKey --> JWTKey["JWT Signing Secret (HS256 / RS256 Private Key)"]
    MasterKey --> DBSecret["PostgreSQL App Password & Connection URL"]
    MasterKey --> BackupKey["Backup Encryption Key (AES-256)"]
    MasterKey --> ColumnKey["Column Envelope DEKs"]
    MasterKey --> ThirdPartyKey["Country Directory API Keys"]
```

### 5.3 Key Rotation & Emergency Revocation Protocol
1. **Scheduled Rotation (90-Day Cycle):**
   - JWT Signing Keys: Rotated every 90 days. Dual-key verification allows tokens signed with Key $N-1$ to remain valid until expiration ($15\text{ mins}$), while new tokens are signed with Key $N$.
   - Database Passwords: Rotated via Vault dynamic database credentials without service downtime.
2. **Emergency Key Revocation:**
   - In the event of suspected credential leakage, operations triggers an immediate KMS key disablement.
   - All active application sessions are instantly terminated by flushing the Redis token registry (`FLUSHDB` on session cache).
   - Containers are redeployed with freshly generated secrets within 15 minutes.
