from datetime import date, datetime, timezone

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.dependencies import DBDep, RequireAdminDep, RequireAnyDep
from app.models.participant import Participant
from app.models.van_request import Stop, VanRequest
from app.models.van_request_participant import VanRequestParticipant
from app.schemas.participant import VanRequestParticipantIn, VanRequestParticipantOut
from app.schemas.stop import StopIn, StopOut
from app.schemas.van_request import ApproveIn, VanRequestIn, VanRequestOut

router = APIRouter(prefix="/v1/van-requests", tags=["van-requests"])

# ── ordering helpers ──────────────────────────────────────────────────────────

_ORDER_COLS = {
    "pickup_date": VanRequest.pickup_date,
    "created_at": VanRequest.created_at,
    "status": VanRequest.status,
    "mission_place": VanRequest.mission_place,
}


def _build_order(ordering: str | None):
    if not ordering:
        return [VanRequest.created_at.desc()]
    desc = ordering.startswith("-")
    col = _ORDER_COLS.get(ordering.lstrip("-"))
    if not col:
        return [VanRequest.created_at.desc()]
    return [col.desc() if desc else col.asc()]


# ── formData → first-class column extractor ───────────────────────────────────

def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except (ValueError, TypeError):
        return None


def _extract_columns(body: VanRequestIn) -> dict:
    fd = body.form_data or {}
    return {
        "request_id": body.request_id,
        "submitter_username": body.submitter_username,
        "form_data": body.form_data,
        "members": body.members,
        "vehicles": body.vehicles,
        "equipment_items": body.equipment_items,
        "admin_panel": body.admin_panel,
        "support_file_name": body.support_file_name,
        "lodging_image_name": body.lodging_image_name,
        "breakfast_image_name": body.breakfast_image_name,
        "lunch_image_name": body.lunch_image_name,
        "dinner_image_name": body.dinner_image_name,
        "implementation_image_name": body.implementation_image_name,
        # first-class searchable columns mirrored from formData
        "mission_title": fd.get("missionTitle", ""),
        "mission_place": fd.get("missionPlace", ""),
        "pickup_date": _parse_date(fd.get("departureDate")),
        "return_date": _parse_date(fd.get("returnDate")),
        "fullname": fd.get("name", ""),
        "job_position": fd.get("role", ""),
        "requester_phone": fd.get("phone", ""),
        "requester_gender": fd.get("gender", ""),
    }


async def _get_or_404(request_id: int, db) -> VanRequest:
    result = await db.execute(
        select(VanRequest).where(VanRequest.id == request_id, VanRequest.is_deleted.is_(False))
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Van request not found")
    return obj


# ── van request CRUD ──────────────────────────────────────────────────────────


@router.get("/", response_model=list[VanRequestOut], response_model_by_alias=True)
async def list_van_requests(
    db: DBDep,
    _: RequireAnyDep,
    status_filter: str | None = Query(None, alias="status"),
    submitter_username: str | None = Query(None),
    search: str | None = Query(None),
    ordering: str | None = Query(None),
):
    q = select(VanRequest).where(VanRequest.is_deleted.is_(False))

    if status_filter:
        q = q.where(VanRequest.status == status_filter)
    if submitter_username:
        q = q.where(VanRequest.submitter_username == submitter_username)
    if search:
        q = q.where(VanRequest.mission_title.ilike(f"%{search}%"))

    q = q.order_by(*_build_order(ordering))
    result = await db.execute(q)
    return [VanRequestOut.model_validate(r) for r in result.scalars().all()]


@router.get("/{request_id}/", response_model=VanRequestOut, response_model_by_alias=True)
async def get_van_request(request_id: int, db: DBDep, _: RequireAnyDep):
    return VanRequestOut.model_validate(await _get_or_404(request_id, db))


@router.post("/", response_model=VanRequestOut, status_code=status.HTTP_201_CREATED,
             response_model_by_alias=True)
async def create_van_request(body: VanRequestIn, db: DBDep, _: RequireAnyDep):
    if body.request_id:
        existing = await db.execute(
            select(VanRequest).where(VanRequest.request_id == body.request_id)
        )
        existing = existing.scalar_one_or_none()
        if existing:
            return VanRequestOut.model_validate(existing)

    obj = VanRequest(**_extract_columns(body))
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return VanRequestOut.model_validate(obj)


@router.put("/{request_id}/", response_model=VanRequestOut, response_model_by_alias=True)
async def update_van_request(request_id: int, body: VanRequestIn, db: DBDep, _: RequireAnyDep):
    obj = await _get_or_404(request_id, db)
    for key, value in _extract_columns(body).items():
        setattr(obj, key, value)
    await db.commit()
    await db.refresh(obj)
    return VanRequestOut.model_validate(obj)


@router.patch("/{request_id}/", response_model=VanRequestOut, response_model_by_alias=True)
async def partial_update_van_request(
    request_id: int, body: VanRequestIn, db: DBDep, _: RequireAnyDep
):
    obj = await _get_or_404(request_id, db)
    provided = body.model_dump(exclude_unset=True, by_alias=False)
    all_cols = _extract_columns(body)
    for key in provided:
        if key in all_cols:
            setattr(obj, key, all_cols[key])
    if "form_data" in provided:
        for col in ("mission_title", "mission_place", "pickup_date", "return_date",
                    "fullname", "job_position", "requester_phone", "requester_gender"):
            setattr(obj, col, all_cols[col])
    await db.commit()
    await db.refresh(obj)
    return VanRequestOut.model_validate(obj)


@router.delete("/{request_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_van_request(request_id: int, db: DBDep, _: RequireAdminDep):
    obj = await _get_or_404(request_id, db)
    obj.is_deleted = True
    await db.commit()


@router.post("/{request_id}/approve/", response_model=VanRequestOut, response_model_by_alias=True)
async def approve_van_request(
    request_id: int, body: ApproveIn, db: DBDep, current_user: RequireAdminDep
):
    obj = await _get_or_404(request_id, db)
    if body.action == "approve":
        obj.status = "approved"
        obj.approved_by = current_user.id
        obj.approved_at = datetime.now(timezone.utc)
    elif body.action == "reject":
        obj.status = "rejected"
        obj.approved_by = current_user.id
        obj.approved_at = datetime.now(timezone.utc)
    else:
        obj.status = "pending"
        obj.approved_by = None
        obj.approved_at = None
    obj.approval_note = body.note or ""
    await db.commit()
    await db.refresh(obj)
    return VanRequestOut.model_validate(obj)


# ── Stops sub-resource ────────────────────────────────────────────────────────


@router.get("/{request_id}/stops/", response_model=list[StopOut], response_model_by_alias=True)
async def list_stops(request_id: int, db: DBDep, _: RequireAnyDep):
    await _get_or_404(request_id, db)
    result = await db.execute(
        select(Stop).where(Stop.van_request_id == request_id).order_by(Stop.order)
    )
    return [StopOut.model_validate(s) for s in result.scalars().all()]


@router.post("/{request_id}/stops/", response_model=StopOut, status_code=status.HTTP_201_CREATED,
             response_model_by_alias=True)
async def add_stop(request_id: int, body: StopIn, db: DBDep, _: RequireAnyDep):
    await _get_or_404(request_id, db)
    obj = Stop(van_request_id=request_id, **body.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return StopOut.model_validate(obj)


@router.delete("/{request_id}/stops/{stop_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def remove_stop(request_id: int, stop_id: int, db: DBDep, _: RequireAdminDep):
    await _get_or_404(request_id, db)
    result = await db.execute(
        select(Stop).where(Stop.id == stop_id, Stop.van_request_id == request_id)
    )
    stop = result.scalar_one_or_none()
    if not stop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stop not found")
    await db.delete(stop)
    await db.commit()


# ── Participants sub-resource ─────────────────────────────────────────────────


@router.get("/{request_id}/participants/", response_model=list[VanRequestParticipantOut],
            response_model_by_alias=True)
async def list_request_participants(request_id: int, db: DBDep, _: RequireAnyDep):
    await _get_or_404(request_id, db)
    result = await db.execute(
        select(VanRequestParticipant)
        .where(VanRequestParticipant.van_request_id == request_id)
        .order_by(VanRequestParticipant.order_index)
    )
    entries = result.scalars().all()
    out = []
    for entry in entries:
        p_result = await db.execute(select(Participant).where(Participant.id == entry.participant_id))
        participant = p_result.scalar_one_or_none()
        out.append(VanRequestParticipantOut(
            id=entry.id,
            participant=participant,
            order_index=entry.order_index,
        ))
    return out


@router.post(
    "/{request_id}/participants/",
    response_model=VanRequestParticipantOut,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=True,
)
async def add_request_participant(
    request_id: int, body: VanRequestParticipantIn, db: DBDep, _: RequireAnyDep
):
    await _get_or_404(request_id, db)

    if not body.participant_id and not body.participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either participant_id or participant data.",
        )

    if body.participant:
        p = Participant(**body.participant.model_dump())
        db.add(p)
        await db.flush()
        participant_id = p.id
    else:
        p_result = await db.execute(select(Participant).where(Participant.id == body.participant_id))
        p = p_result.scalar_one_or_none()
        if not p:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")
        participant_id = p.id

    entry = VanRequestParticipant(
        van_request_id=request_id,
        participant_id=participant_id,
        order_index=body.order_index,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    await db.refresh(p)
    return VanRequestParticipantOut(id=entry.id, participant=p, order_index=entry.order_index)


@router.delete("/{request_id}/participants/{participant_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def remove_request_participant(
    request_id: int, participant_id: int, db: DBDep, _: RequireAdminDep
):
    await _get_or_404(request_id, db)
    result = await db.execute(
        select(VanRequestParticipant).where(
            VanRequestParticipant.van_request_id == request_id,
            VanRequestParticipant.participant_id == participant_id,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not on this request")
    await db.delete(entry)
    await db.commit()
