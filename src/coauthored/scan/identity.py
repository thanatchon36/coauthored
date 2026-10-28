"""Salted hashing of author and committer identities at ingest (MISSION §1.2)."""

from __future__ import annotations

import hashlib
import os
import secrets
from pathlib import Path

ENV_FILE = Path(".env")
SALT_VAR = "HASH_SALT"


def load_salt(env_file: Path = ENV_FILE, create: bool = True) -> str:
    """Salt from the environment, else from a git-ignored ``.env``; created on first use."""
    if salt := os.environ.get(SALT_VAR):
        return salt
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            key, _, value = line.partition("=")
            if key.strip() == SALT_VAR and value.strip():
                return value.strip()
    if not create:
        raise RuntimeError(f"{SALT_VAR} not set and {env_file} has none")
    salt = secrets.token_hex(32)
    with env_file.open("a", encoding="utf-8") as fh:
        fh.write(f"{SALT_VAR}={salt}\n")
    return salt


def hash_identity(name: str, email: str, salt: str) -> str:
    """Email is the identity; the name is used only when the email is empty."""
    key = email.strip().lower() or "name:" + name.strip().lower()
    return hashlib.sha256((salt + "\x00" + key).encode("utf-8")).hexdigest()[:16]
