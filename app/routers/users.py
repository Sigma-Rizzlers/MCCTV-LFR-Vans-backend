from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.dependencies import CurrentUserDep, DBDep, RequireSuperadminDep
from app.models.user import User
from app.models.user_profile import UserProfile
from app.schemas.user import ResetPasswordIn, UserCreateIn, UserOut, UserUpdateIn
from app.schemas.user_profile import UserProfileIn, UserProfileOut
from app.security import hash_password
from app.utils.audit import log_action

router = APIRouter(prefix="/v1/users", tags=["users"])


@router.get("/", response_model=list[UserOut])
async def list_users(
    db: DBDep,
    _: RequireSuperadminDep,
    active: bool | None = Query(None),
    search: str | None = Query(None),
):
    q = select(User)
    if active is True:
        q = q.where(User.isActive.is_(True))
    if search:
        q = q.where(User.username.ilike(f"%{search}%"))
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{user_id}/", response_model=UserOut)
async def get_user(user_id: int, db: DBDep, current_user: CurrentUserDep):
    if current_user.role not in {"superadmin", "sysmanager"} and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(body: UserCreateIn, db: DBDep, current_user: RequireSuperadminDep):
    exists = await db.execute(select(User).where(User.username == body.username))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    user = User(
        username=body.username,
        passwordHash=hash_password(body.password),
        role=body.role,
        unitName=body.unitName,
    )
    db.add(user)
    await log_action(db, current_user, "create_user", target=body.username)
    await db.commit()
    await db.refresh(user)
    return user


@router.put("/{user_id}/", response_model=UserOut)
async def update_user(user_id: int, body: UserUpdateIn, db: DBDep, _: RequireSuperadminDep):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if body.role is not None:
        user.role = body.role
    if body.unitName is not None:
        user.unitName = body.unitName
    if body.isActive is not None:
        user.isActive = body.isActive
    await db.commit()
    await db.refresh(user)
    return user


@router.patch("/{user_id}/", response_model=UserOut)
async def patch_user(user_id: int, body: UserUpdateIn, db: DBDep, _: RequireSuperadminDep):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if body.role is not None:
        user.role = body.role
    if body.unitName is not None:
        user.unitName = body.unitName
    if body.isActive is not None:
        user.isActive = body.isActive
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/{user_id}/reset-password/")
async def reset_password(user_id: int, body: ResetPasswordIn, db: DBDep, current_user: RequireSuperadminDep):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.passwordHash = hash_password(body.newPassword)
    await log_action(db, current_user, "reset_password", target=user.username)
    await db.commit()
    return {"detail": "Password updated"}


@router.delete("/{user_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: DBDep, current_user: RequireSuperadminDep):
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.isActive = False
    await log_action(db, current_user, "delete_user", target=user.username)
    await db.commit()


@router.get("/me/profile/", response_model=UserProfileOut)
async def get_my_profile(db: DBDep, current_user: CurrentUserDep):
    result = await db.execute(select(UserProfile).where(UserProfile.userId == current_user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.put("/me/profile/", response_model=UserProfileOut)
async def upsert_my_profile(body: UserProfileIn, db: DBDep, current_user: CurrentUserDep):
    result = await db.execute(select(UserProfile).where(UserProfile.userId == current_user.id))
    profile = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)
    if profile:
        profile.name = body.name
        profile.phone = body.phone
        profile.gender = body.gender
        profile.role = body.role
        profile.supportFileName = body.supportFileName
        profile.updatedAt = now
    else:
        profile = UserProfile(
            userId=current_user.id,
            name=body.name,
            phone=body.phone,
            gender=body.gender,
            role=body.role,
            supportFileName=body.supportFileName,
            updatedAt=now,
        )
        db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile
