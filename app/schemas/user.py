from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"
    unit_name: str = ""


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str
    unit_name: str
    created_at: datetime


class TokenOut(BaseModel):
    token: str
    role: str
    unit_name: str
    username: str
