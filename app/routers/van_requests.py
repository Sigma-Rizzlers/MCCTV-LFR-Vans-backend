import mimetypes
import re
from datetime import date, datetime, timezone
from pathlib import Path

import aiofiles
from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select

from app.dependencies import DBDep, RequireAdminDep, RequireAnyDep
from app.models.participant import Participant
from app.models.van_request import Stop, VanRequest
from app.models.van_request_participant import VanRequestParticipant
from app.schemas.participant import VanRequestParticipantIn, VanRequestParticipantOut
from app.schemas.stop import StopIn, StopOut
from app.schemas.van_request import ApproveIn, VanRequestIn, VanRequestOut
from app.utils.audit import log_action

router = APIRouter(prefix="/v1/van-requests", tags=["van-requests"])

_FILES_ROOT = Path(__file__).resolve().parent.parent.parent / "storage" / "files"

_SLOT_MAP = {
    "support": "supportFileName",
    "lodging": "lodgingImageName",
    "breakfast": "breakfastImageName",
    "lunch": "lunchImageName",
    "dinner": "dinnerImageName",
    "implementation": "implementationImageName",
}
_VALID_SLOTS = frozenset(_SLOT_MAP)

# ── file upload security constants ────────────────────────────────────────────

_MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

# Image slots only accept images; support slot also accepts PDFs/docs
_SLOT_ALLOWED_MIME: dict[str, frozenset[str]] = {
    "support": frozenset({
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }),
    "lodging":        frozenset({"image/jpeg", "image/png", "image/gif", "image/webp"}),
    "breakfast":      frozenset({"image/jpeg", "image/png", "image/gif", "image/webp"}),
    "lunch":          frozenset({"image/jpeg", "image/png", "image/gif", "image/webp"}),
    "dinner":         frozenset({"image/jpeg", "image/png", "image/gif", "image/webp"}),
    "implementation": frozenset({"image/jpeg", "image/png", "image/gif", "image/webp"}),
}

_SAFE_FILENAME_RE = re.compile(r"[^\w.\-]")  # keep word chars, dots, hyphens


def _sanitize_filename(name: str) -> str:
    """Strip path separators and unsafe characters from an uploaded filename."""
    # Take only the basename (prevents path traversal like ../../etc/passwd)
    name = Path(name).name
    # Replace anything that's not alphanumeric, dot, or hyphen with underscore
    name = _SAFE_FILENAME_RE.sub("_", name)
    # Truncate to a safe length
    return name[:100] or "file"

# ── ordering helpers ──────────────────────────────────────────────────────────

_ORDER_COLS = {
    "pickupDate": VanRequest.pickupDate,
    "submittedAt": VanRequest.submittedAt,
    "approvalStatus": VanRequest.approvalStatus,
    "missionPlace": VanRequest.missionPlace,
}


def _build_order(ordering: str | None):
    if not ordering:
        return [VanRequest.submittedAt.desc()]
    desc = ordering.startswith("-")
    col = _ORDER_COLS.get(ordering.lstrip("-"))
    if not col:
        return [VanRequest.submittedAt.desc()]
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
    fd = body.formData or {}
    return {
        "requestId": body.requestId,
        "submitterUsername": body.submitterUsername,
        "formData": body.formData,
        "members": body.members,
        "vehicles": body.vehicles,
        "equipmentItems": body.equipmentItems,
        "adminPanel": body.adminPanel,
        "supportFileName": body.supportFileName,
        "lodgingImageName": body.lodgingImageName,
        "breakfastImageName": body.breakfastImageName,
        "lunchImageName": body.lunchImageName,
        "dinnerImageName": body.dinnerImageName,
        "implementationImageName": body.implementationImageName,
        # first-class searchable columns mirrored from formData
        "missionTitle": fd.get("missionTitle", ""),
        "missionPlace": fd.get("missionPlace", ""),
        "pickupDate": _parse_date(fd.get("departureDate")),
        "returnDate": _parse_date(fd.get("returnDate")),
        "fullname": fd.get("name", ""),
        "jobPosition": fd.get("role", ""),
        "requesterPhone": fd.get("phone", ""),
        "requesterGender": fd.get("gender", ""),
    }


async def _get_or_404(request_id: int, db) -> VanRequest:
    result = await db.execute(
        select(VanRequest).where(VanRequest.id == request_id, VanRequest.isDeleted.is_(False))
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Van request not found")
    return obj


# ── van request CRUD ──────────────────────────────────────────────────────────


@router.get("/", response_model=list[VanRequestOut])
async def list_van_requests(
    db: DBDep,
    _: RequireAnyDep,
    status_filter: str | None = Query(None, alias="status"),
    submitter_username: str | None = Query(None),
    search: str | None = Query(None),
    ordering: str | None = Query(None),
):
    q = select(VanRequest).where(VanRequest.isDeleted.is_(False))

    if status_filter:
        q = q.where(VanRequest.approvalStatus == status_filter)
    if submitter_username:
        q = q.where(VanRequest.submitterUsername == submitter_username)
    if search:
        q = q.where(VanRequest.missionTitle.ilike(f"%{search}%"))

    q = q.order_by(*_build_order(ordering))
    result = await db.execute(q)
    return [VanRequestOut.model_validate(r) for r in result.scalars().all()]


@router.get("/{request_id}/", response_model=VanRequestOut)
async def get_van_request(request_id: int, db: DBDep, _: RequireAnyDep):
    return VanRequestOut.model_validate(await _get_or_404(request_id, db))


@router.post("/", response_model=VanRequestOut, status_code=status.HTTP_201_CREATED)
async def create_van_request(body: VanRequestIn, db: DBDep, _: RequireAnyDep):
    if body.requestId:
        existing = await db.execute(
            select(VanRequest).where(VanRequest.requestId == body.requestId)
        )
        existing = existing.scalar_one_or_none()
        if existing:
            return VanRequestOut.model_validate(existing)

    obj = VanRequest(**_extract_columns(body))
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return VanRequestOut.model_validate(obj)


def _assert_owner_or_admin(obj: VanRequest, current_user) -> None:
    """Raise 403 if the user is not the submitter and not an admin/superadmin."""
    from app.dependencies import _ADMIN_ROLES  # local import to avoid circular
    if current_user.role in _ADMIN_ROLES:
        return
    if obj.submitterUsername != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own requests.",
        )


@router.put("/{request_id}/", response_model=VanRequestOut)
async def update_van_request(request_id: int, body: VanRequestIn, db: DBDep, current_user: RequireAnyDep):
    obj = await _get_or_404(request_id, db)
    _assert_owner_or_admin(obj, current_user)
    for key, value in _extract_columns(body).items():
        setattr(obj, key, value)
    await db.commit()
    await db.refresh(obj)
    return VanRequestOut.model_validate(obj)


@router.patch("/{request_id}/", response_model=VanRequestOut)
async def partial_update_van_request(
    request_id: int, body: VanRequestIn, db: DBDep, current_user: RequireAnyDep
):
    obj = await _get_or_404(request_id, db)
    _assert_owner_or_admin(obj, current_user)
    provided = body.model_dump(exclude_unset=True)
    all_cols = _extract_columns(body)
    for key in provided:
        if key in all_cols:
            setattr(obj, key, all_cols[key])
    if "formData" in provided:
        for col in ("missionTitle", "missionPlace", "pickupDate", "returnDate",
                    "fullname", "jobPosition", "requesterPhone", "requesterGender"):
            setattr(obj, col, all_cols[col])
    await db.commit()
    await db.refresh(obj)
    return VanRequestOut.model_validate(obj)


@router.delete("/{request_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_van_request(request_id: int, db: DBDep, _: RequireAdminDep):
    obj = await _get_or_404(request_id, db)
    obj.isDeleted = True
    await db.commit()


@router.post("/{request_id}/approve/", response_model=VanRequestOut)
async def approve_van_request(
    request_id: int, body: ApproveIn, db: DBDep, current_user: RequireAdminDep
):
    obj = await _get_or_404(request_id, db)
    if body.action == "approve":
        obj.approvalStatus = "approved"
        obj.approvedBy = current_user.id
        obj.approvedAt = datetime.now(timezone.utc).replace(tzinfo=None)
    elif body.action == "reject":
        obj.approvalStatus = "rejected"
        obj.approvedBy = current_user.id
        obj.approvedAt = datetime.now(timezone.utc).replace(tzinfo=None)
    else:
        obj.approvalStatus = "pending"
        obj.approvedBy = None
        obj.approvedAt = None
    obj.approvalNote = body.note or ""
    await log_action(db, current_user, action=body.action, target=obj.requestId, detail=body.note or "")
    await db.commit()
    await db.refresh(obj)
    return VanRequestOut.model_validate(obj)


# ── Stops sub-resource ────────────────────────────────────────────────────────


@router.get("/{request_id}/stops/", response_model=list[StopOut])
async def list_stops(request_id: int, db: DBDep, _: RequireAnyDep):
    await _get_or_404(request_id, db)
    result = await db.execute(
        select(Stop).where(Stop.vanRequestId == request_id).order_by(Stop.order)
    )
    return [StopOut.model_validate(s) for s in result.scalars().all()]


@router.post("/{request_id}/stops/", response_model=StopOut, status_code=status.HTTP_201_CREATED)
async def add_stop(request_id: int, body: StopIn, db: DBDep, _: RequireAnyDep):
    await _get_or_404(request_id, db)
    obj = Stop(vanRequestId=request_id, **body.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return StopOut.model_validate(obj)


@router.delete("/{request_id}/stops/{stop_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def remove_stop(request_id: int, stop_id: int, db: DBDep, _: RequireAdminDep):
    await _get_or_404(request_id, db)
    result = await db.execute(
        select(Stop).where(Stop.id == stop_id, Stop.vanRequestId == request_id)
    )
    stop = result.scalar_one_or_none()
    if not stop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stop not found")
    await db.delete(stop)
    await db.commit()


# ── Participants sub-resource ─────────────────────────────────────────────────


@router.get("/{request_id}/participants/", response_model=list[VanRequestParticipantOut])
async def list_request_participants(request_id: int, db: DBDep, _: RequireAnyDep):
    await _get_or_404(request_id, db)
    result = await db.execute(
        select(VanRequestParticipant)
        .where(VanRequestParticipant.vanRequestId == request_id)
        .order_by(VanRequestParticipant.orderIndex)
    )
    entries = result.scalars().all()
    out = []
    for entry in entries:
        p_result = await db.execute(select(Participant).where(Participant.id == entry.participantId))
        participant = p_result.scalar_one_or_none()
        out.append(VanRequestParticipantOut(
            id=entry.id,
            participant=participant,
            orderIndex=entry.orderIndex,
        ))
    return out


@router.post(
    "/{request_id}/participants/",
    response_model=VanRequestParticipantOut,
    status_code=status.HTTP_201_CREATED,
)
async def add_request_participant(
    request_id: int, body: VanRequestParticipantIn, db: DBDep, _: RequireAnyDep
):
    await _get_or_404(request_id, db)

    if not body.participantId and not body.participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either participantId or participant data.",
        )

    if body.participant:
        p = Participant(**body.participant.model_dump())
        db.add(p)
        await db.flush()
        participant_id = p.id
    else:
        p_result = await db.execute(select(Participant).where(Participant.id == body.participantId))
        p = p_result.scalar_one_or_none()
        if not p:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")
        participant_id = p.id

    entry = VanRequestParticipant(
        vanRequestId=request_id,
        participantId=participant_id,
        orderIndex=body.orderIndex,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    await db.refresh(p)
    return VanRequestParticipantOut(id=entry.id, participant=p, orderIndex=entry.orderIndex)


@router.delete("/{request_id}/participants/{participant_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def remove_request_participant(
    request_id: int, participant_id: int, db: DBDep, _: RequireAdminDep
):
    await _get_or_404(request_id, db)
    result = await db.execute(
        select(VanRequestParticipant).where(
            VanRequestParticipant.vanRequestId == request_id,
            VanRequestParticipant.participantId == participant_id,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not on this request")
    await db.delete(entry)
    await db.commit()


# ── File attachments ──────────────────────────────────────────────────────────


@router.post("/{request_id}/files/{slot}/")
async def upload_request_file(
    request_id: int,
    slot: str,
    db: DBDep,
    current_user: RequireAnyDep,
    file: UploadFile = File(...),
):
    if slot not in _VALID_SLOTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid slot. Choose from: {', '.join(sorted(_VALID_SLOTS))}",
        )
    obj = await _get_or_404(request_id, db)

    # Ownership check — only the submitter or an admin can upload files
    _assert_owner_or_admin(obj, current_user)

    # Read file content with size limit
    content = await file.read(_MAX_FILE_SIZE_BYTES + 1)
    if len(content) > _MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {_MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB limit.",
        )

    # Validate MIME type by reading the Content-Type the client declared
    # and cross-checking against what we allow for this slot
    declared_mime = (file.content_type or "").split(";")[0].strip().lower()
    allowed_mimes = _SLOT_ALLOWED_MIME[slot]
    if declared_mime not in allowed_mimes:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type '{declared_mime}' is not allowed for slot '{slot}'. "
                   f"Allowed: {', '.join(sorted(allowed_mimes))}",
        )

    # Sanitize filename to prevent path traversal
    filename = _sanitize_filename(file.filename or "file")

    slot_dir = _FILES_ROOT / obj.requestId / slot
    slot_dir.mkdir(parents=True, exist_ok=True)

    # Remove previous file for this slot before saving the new one
    for old in slot_dir.iterdir():
        old.unlink(missing_ok=True)

    async with aiofiles.open(slot_dir / filename, "wb") as out:
        await out.write(content)

    setattr(obj, _SLOT_MAP[slot], filename)
    await db.commit()

    return {
        "slot": slot,
        "fileName": filename,
        "url": f"/api/v1/van-requests/{request_id}/files/{slot}/",
    }


@router.get("/{request_id}/files/{slot}/")
async def download_request_file(
    request_id: int,
    slot: str,
    db: DBDep,
    _: RequireAnyDep,
):
    if slot not in _VALID_SLOTS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid slot")
    obj = await _get_or_404(request_id, db)

    filename = getattr(obj, _SLOT_MAP[slot])
    if not filename:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No file stored for this slot")

    path = _FILES_ROOT / obj.requestId / slot / filename
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on disk")

    media_type, _ = mimetypes.guess_type(str(path))
    return FileResponse(str(path), media_type=media_type or "application/octet-stream", filename=filename)
