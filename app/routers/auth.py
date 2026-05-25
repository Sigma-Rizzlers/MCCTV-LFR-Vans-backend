import time
from collections import defaultdict
from datetime import datetime, timezone
from threading import Lock

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select, delete

from app.dependencies import DBDep
from app.models.user import TokenStore, User
from app.schemas.user import TokenOut
from app.security import create_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

# ── simple in-memory rate limiter ─────────────────────────────────────────────
# Tracks failed login attempts per IP. Resets on successful login.
# Note: resets on server restart and does not scale across multiple instances.
# For production with multiple workers, replace with Redis-backed rate limiting.

_MAX_ATTEMPTS = 5       # max failed attempts before lockout
_WINDOW_SECONDS = 300   # 5-minute sliding window

_failed_attempts: dict[str, list[float]] = defaultdict(list)
_rate_lock = Lock()


def _check_rate_limit(ip: str) -> None:
    """Raise 429 if the IP has exceeded the failed-attempt threshold."""
    now = time.monotonic()
    with _rate_lock:
        # Keep only attempts within the window
        recent = [t for t in _failed_attempts[ip] if now - t < _WINDOW_SECONDS]
        _failed_attempts[ip] = recent
        if len(recent) >= _MAX_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many failed login attempts. Try again in {_WINDOW_SECONDS // 60} minutes.",
            )


def _record_failed(ip: str) -> None:
    now = time.monotonic()
    with _rate_lock:
        _failed_attempts[ip].append(now)


def _clear_rate_limit(ip: str) -> None:
    with _rate_lock:
        _failed_attempts.pop(ip, None)


# ── login endpoint ────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/token/", response_model=TokenOut)
async def obtain_token(body: LoginRequest, request: Request, db: DBDep):
    client_ip = request.client.host if request.client else "unknown"

    # Rate-limit check BEFORE hitting the database
    _check_rate_limit(client_ip)

    result = await db.execute(select(User).where(User.username == body.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.passwordHash):
        _record_failed(client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not user.isActive:
        _record_failed(client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive",
        )

    # Successful login — clear any recorded failures for this IP
    _clear_rate_limit(client_ip)

    # Delete all previous tokens for this user (single active session per user)
    await db.execute(delete(TokenStore).where(TokenStore.userId == user.id))

    user.lastLoginAt = datetime.now(timezone.utc)
    token_value = create_token()
    db.add(TokenStore(token=token_value, userId=user.id))
    await db.commit()

    return TokenOut(
        token=token_value,
        role=user.role,
        unitName=user.unitName,
        username=user.username,
    )
