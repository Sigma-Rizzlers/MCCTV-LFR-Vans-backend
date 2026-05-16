from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.user import User


async def log_action(
    db: AsyncSession,
    user: User,
    action: str,
    target: str = "",
    detail: str = "",
) -> None:
    """Stage an AuditLog row in the current session. Caller must commit."""
    db.add(AuditLog(
        action=action,
        target=target,
        detail=detail,
        performedBy=user.username,
    ))
