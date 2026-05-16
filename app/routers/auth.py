from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

from app.dependencies import DBDep
from app.models.user import TokenStore, User
from app.schemas.user import TokenOut
from app.security import create_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/token/", response_model=TokenOut)
async def obtain_token(body: LoginRequest, db: DBDep):
    result = await db.execute(select(User).where(User.username == body.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive",
        )

    token_value = create_token()
    db.add(TokenStore(token=token_value, user_id=user.id))
    await db.commit()

    return TokenOut(
        token=token_value,
        role=user.role,
        unit_name=user.unit_name,
        username=user.username,
    )
