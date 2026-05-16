from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.dependencies import CurrentUserDep, DBDep, RequireSuperadminDep
from app.models.user import User
from app.schemas.user import ResetPasswordIn, UserCreateIn, UserOut, UserUpdateIn
from app.security import hash_password

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
async def create_user(body: UserCreateIn, db: DBDep, _: RequireSuperadminDep):
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
async def reset_password(user_id: int, body: ResetPasswordIn, db: DBDep, _: RequireSuperadminDep):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.passwordHash = hash_password(body.newPassword)
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
    await db.commit()
