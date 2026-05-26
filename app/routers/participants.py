from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.dependencies import DBDep, RequireAdminDep, RequireAnyDep
from app.models.participant import Participant
from app.schemas.participant import ParticipantIn, ParticipantOut

router = APIRouter(prefix="/v1/participants", tags=["participants"])

_LIST_MAX = 500  # hard cap on list results


async def _get_or_404(participant_id: int, db) -> Participant:
    result = await db.execute(
        select(Participant).where(
            Participant.id == participant_id,
            Participant.isDeleted.is_(False),
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")
    return obj


@router.get("/", response_model=list[ParticipantOut])
async def list_participants(
    db: DBDep,
    _: RequireAnyDep,
    search: str | None = Query(None),
    ordering: str | None = Query(None),
    limit: int = Query(default=_LIST_MAX, ge=1, le=_LIST_MAX),
    offset: int = Query(default=0, ge=0),
):
    q = select(Participant).where(Participant.isDeleted.is_(False))

    if search:
        term = f"%{search}%"
        q = q.where(
            Participant.name.ilike(term)
            | Participant.phone.ilike(term)
            | Participant.gender.ilike(term)
            | Participant.role.ilike(term)
        )

    desc = ordering and ordering.startswith("-")
    col_name = ordering.lstrip("-") if ordering else "name"
    col_map = {
        "name": Participant.name,
        "createdAt": Participant.createdAt,
    }
    col = col_map.get(col_name, Participant.name)
    q = q.order_by(col.desc() if desc else col.asc()).limit(limit).offset(offset)

    result = await db.execute(q)
    return [ParticipantOut.model_validate(r) for r in result.scalars().all()]


@router.get("/{participant_id}/", response_model=ParticipantOut)
async def get_participant(participant_id: int, db: DBDep, _: RequireAnyDep):
    return ParticipantOut.model_validate(await _get_or_404(participant_id, db))


@router.post("/", response_model=ParticipantOut, status_code=status.HTTP_201_CREATED)
async def create_participant(body: ParticipantIn, db: DBDep, _: RequireAnyDep):
    obj = Participant(**body.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return ParticipantOut.model_validate(obj)


# update and delete require admin

@router.put("/{participant_id}/", response_model=ParticipantOut)
async def update_participant(participant_id: int, body: ParticipantIn, db: DBDep, _: RequireAdminDep):
    obj = await _get_or_404(participant_id, db)
    for key, value in body.model_dump().items():
        setattr(obj, key, value)
    await db.commit()
    await db.refresh(obj)
    return ParticipantOut.model_validate(obj)


@router.patch("/{participant_id}/", response_model=ParticipantOut)
async def partial_update_participant(participant_id: int, body: ParticipantIn, db: DBDep, _: RequireAdminDep):
    obj = await _get_or_404(participant_id, db)
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    await db.commit()
    await db.refresh(obj)
    return ParticipantOut.model_validate(obj)


@router.delete("/{participant_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_participant(participant_id: int, db: DBDep, _: RequireAdminDep):
    obj = await _get_or_404(participant_id, db)
    obj.isDeleted = True
    await db.commit()
