import hashlib
import secrets

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def create_token() -> str:
    """Return a 64-char hex token (32 random bytes) for Authorization: Token header."""
    return secrets.token_hex(32)


def hash_token(token: str) -> str:
    """Return the SHA-256 hex digest of a raw token for safe DB storage.

    Only the hash is persisted — the raw token is sent to the client once
    and never stored.  A read-compromised DB cannot replay active sessions.
    """
    return hashlib.sha256(token.encode()).hexdigest()
