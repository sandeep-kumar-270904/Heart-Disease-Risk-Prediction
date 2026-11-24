"""HeartXAI 2.0 — AES-256-GCM Authenticated Backup Encryption & Verification Utility (ADR-012).

Implements authenticated encryption (AEAD) with:
- Key derivation: PBKDF2-HMAC-SHA256 (200,000 iterations, 16-byte cryptographic random salt)
- Cipher: AES-256-GCM (12-byte random nonce, 16-byte authentication tag)
- AAD: Fixed magic/version header 'HXAEAD01' + salt + nonce bound into GCM authentication
- Memory-buffered stdin/stdout or file streaming with ZERO plaintext temporary files written to disk.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

HEADER_MAGIC = b"HXAEAD01"
SALT_SIZE = 16
NONCE_SIZE = 12
PBKDF2_ITERATIONS = 200_000


def _derive_aes256_key(passphrase: str, salt: bytes) -> bytes:
    if not passphrase or len(passphrase) < 16:
        raise ValueError("BACKUP_ENCRYPTION_KEY must be at least 16 characters.")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(passphrase.encode("utf-8"))


def encrypt_bytes_aes256_gcm(plaintext: bytes, passphrase: str) -> bytes:
    """Encrypt bytes using AES-256-GCM with random salt/nonce and authenticated header."""
    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)
    key = _derive_aes256_key(passphrase, salt)
    aad = HEADER_MAGIC + salt + nonce
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, aad)
    return aad + ciphertext


def decrypt_bytes_aes256_gcm(blob: bytes, passphrase: str) -> bytes:
    """Authenticate and decrypt AES-256-GCM envelope; raises InvalidTag/ValueError on tamper."""
    header_len = len(HEADER_MAGIC) + SALT_SIZE + NONCE_SIZE
    if len(blob) < header_len + 16:
        raise ValueError("Encrypted archive is truncated or malformed.")
    magic = blob[: len(HEADER_MAGIC)]
    if magic != HEADER_MAGIC:
        raise ValueError("Invalid encrypted backup header magic.")
    salt_start = len(HEADER_MAGIC)
    nonce_start = salt_start + SALT_SIZE
    salt = blob[salt_start:nonce_start]
    nonce = blob[nonce_start:header_len]
    ciphertext = blob[header_len:]
    aad = blob[:header_len]

    key = _derive_aes256_key(passphrase, salt)
    return AESGCM(key).decrypt(nonce, ciphertext, aad)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AES-256-GCM AEAD backup cipher utility"
    )
    parser.add_argument("mode", choices=["encrypt", "decrypt"])
    parser.add_argument(
        "--input", type=Path, default=None, help="Input file (defaults to stdin)"
    )
    parser.add_argument(
        "--output", type=Path, default=None, help="Output file (defaults to stdout)"
    )
    parser.add_argument(
        "--key-env",
        default="BACKUP_ENCRYPTION_KEY",
        help="Environment variable holding backup passphrase (kept separate from archive)",
    )
    args = parser.parse_args()

    passphrase = os.environ.get(args.key_env, "")
    raw = args.input.read_bytes() if args.input else sys.stdin.buffer.read()

    try:
        result = (
            encrypt_bytes_aes256_gcm(raw, passphrase)
            if args.mode == "encrypt"
            else decrypt_bytes_aes256_gcm(raw, passphrase)
        )
    except (InvalidTag, ValueError) as exc:
        print(f"AEAD backup authentication/decryption failed: {exc}", file=sys.stderr)
        return 1

    if args.output:
        args.output.write_bytes(result)
    else:
        sys.stdout.buffer.write(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
