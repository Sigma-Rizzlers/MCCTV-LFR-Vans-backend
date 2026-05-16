from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.dependencies import DBDep, RequireAdminDep
from app.models.admin_panel import MissionAdminPanel
from app.schemas.admin_panel import AdminPanelIn, AdminPanelOut

router = APIRouter(prefix="/v1/admin-panel", tags=["admin-panel"])


async def _get_or_404(panel_id: int, db) -> MissionAdminPanel:
    result = await db.execute(
        select(MissionAdminPanel).where(MissionAdminPanel.id == panel_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin panel record not found")
    return obj


@router.get("/", response_model=list[AdminPanelOut])
async def list_admin_panels(db: DBDep, _: RequireAdminDep):
    result = await db.execute(select(MissionAdminPanel).order_by(MissionAdminPanel.createdAt.desc()))
    return [AdminPanelOut.model_validate(r) for r in result.scalars().all()]


@router.get("/{panel_id}/", response_model=AdminPanelOut)
async def get_admin_panel(panel_id: int, db: DBDep, _: RequireAdminDep):
    return AdminPanelOut.model_validate(await _get_or_404(panel_id, db))


@router.post("/", response_model=AdminPanelOut, status_code=status.HTTP_201_CREATED)
async def create_admin_panel(body: AdminPanelIn, db: DBDep, _: RequireAdminDep):
    existing = await db.execute(
        select(MissionAdminPanel).where(MissionAdminPanel.missionCode == body.missionCode)
    )
    obj = existing.scalar_one_or_none()
    if obj:
        return AdminPanelOut.model_validate(obj)

    obj = MissionAdminPanel(**body.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return AdminPanelOut.model_validate(obj)


@router.put("/{panel_id}/", response_model=AdminPanelOut)
async def update_admin_panel(panel_id: int, body: AdminPanelIn, db: DBDep, _: RequireAdminDep):
    obj = await _get_or_404(panel_id, db)
    for key, value in body.model_dump().items():
        setattr(obj, key, value)
    await db.commit()
    await db.refresh(obj)
    return AdminPanelOut.model_validate(obj)


@router.patch("/{panel_id}/", response_model=AdminPanelOut)
async def partial_update_admin_panel(panel_id: int, body: AdminPanelIn, db: DBDep, _: RequireAdminDep):
    obj = await _get_or_404(panel_id, db)
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    await db.commit()
    await db.refresh(obj)
    return AdminPanelOut.model_validate(obj)


@router.delete("/{panel_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin_panel(panel_id: int, db: DBDep, _: RequireAdminDep):
    obj = await _get_or_404(panel_id, db)
    await db.delete(obj)
    await db.commit()
