from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"
    unitName: str = ""


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str
    unitName: str
    createdAt: datetime


class TokenOut(BaseModel):
    token: str
    role: str
    unitName: str
    username: str
