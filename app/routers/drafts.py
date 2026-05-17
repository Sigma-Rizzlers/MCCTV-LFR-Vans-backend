from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.dependencies import CurrentUserDep, DBDep
from app.models.draft import ReportDraft
from app.schemas.draft import DraftIn, DraftOut

router = APIRouter(prefix="/v1/drafts", tags=["drafts"])


@router.get("/me/", response_model=DraftOut)
async def get_my_draft(db: DBDep, current_user: CurrentUserDep):
    result = await db.execute(select(ReportDraft).where(ReportDraft.username == current_user.username))
    draft = result.scalar_one_or_none()
    if not draft:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No draft found")
    return draft


@router.put("/me/", response_model=DraftOut)
async def upsert_my_draft(body: DraftIn, db: DBDep, current_user: CurrentUserDep):
    result = await db.execute(select(ReportDraft).where(ReportDraft.username == current_user.username))
    draft = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)
    if draft:
        draft.formData = body.formData
        draft.savedAt = now
    else:
        draft = ReportDraft(username=current_user.username, formData=body.formData, savedAt=now)
        db.add(draft)
    await db.commit()
    await db.refresh(draft)
    return draft


@router.delete("/me/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_draft(db: DBDep, current_user: CurrentUserDep):
    result = await db.execute(select(ReportDraft).where(ReportDraft.username == current_user.username))
    draft = result.scalar_one_or_none()
    if not draft:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No draft found")
    await db.delete(draft)
    await db.commit()
