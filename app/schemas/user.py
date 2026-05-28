from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class UserCreateIn(BaseModel):
    username: str
    password: str
    role: Literal["user", "admin", "superadmin", "sysmanager"]
    unitName: str = ""


class UserUpdateIn(BaseModel):
    role: Literal["user", "admin", "superadmin", "sysmanager"] | None = None
    unitName: str | None = None
    isActive: bool | None = None


class ResetPasswordIn(BaseModel):
    newPassword: str


class ChangePasswordIn(BaseModel):
    currentPassword: str
    newPassword: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str
    unitName: str
    isActive: bool
    createdAt: datetime
    lastLoginAt: datetime | None


class TokenOut(BaseModel):
    token: str
    role: str
    unitName: str
    username: str
