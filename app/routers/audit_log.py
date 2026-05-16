from fastapi import APIRouter, Query, status
from sqlalchemy import select

from app.dependencies import DBDep, RequireSuperadminDep
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogIn, AuditLogOut

router = APIRouter(prefix="/v1/audit-log", tags=["audit-log"])


@router.get("/", response_model=list[AuditLogOut])
async def list_audit_logs(
    db: DBDep,
    _: RequireSuperadminDep,
    action: str | None = Query(None),
    search: str | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
):
    q = select(AuditLog)
    if action:
        q = q.where(AuditLog.action == action)
    if search:
        q = q.where(AuditLog.target.ilike(f"%{search}%"))
    q = q.order_by(AuditLog.createdAt.desc()).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/", response_model=AuditLogOut, status_code=status.HTTP_201_CREATED)
async def create_audit_log(body: AuditLogIn, db: DBDep, current_user: RequireSuperadminDep):
    log = AuditLog(
        action=body.action,
        target=body.target,
        detail=body.detail,
        performedBy=current_user.username,
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log
