from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import TokenStore, User

DBDep = Annotated[AsyncSession, Depends(get_db)]

_ADMIN_ROLES = frozenset({"admin", "superadmin", "sysmanager"})
_SUPERADMIN_ROLES = frozenset({"superadmin", "sysmanager"})


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Parse 'Authorization: Token <hex>' and return the matching User."""
    if not authorization or not authorization.startswith("Token "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Token"},
        )

    token_value = authorization[6:].strip()

    result = await db.execute(
        select(User)
        .join(TokenStore, TokenStore.userId == User.id)
        .where(TokenStore.token == token_value)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Token"},
        )

    if not user.isActive:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive",
        )

    return user


async def _check_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if user.role not in _ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return user


async def _check_superadmin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if user.role not in _SUPERADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return user


# ── type aliases ──────────────────────────────────────────────────────────────

CurrentUserDep = Annotated[User, Depends(get_current_user)]
RequireAnyDep = Annotated[User, Depends(get_current_user)]
RequireAdminDep = Annotated[User, Depends(_check_admin)]
RequireSuperadminDep = Annotated[User, Depends(_check_superadmin)]
