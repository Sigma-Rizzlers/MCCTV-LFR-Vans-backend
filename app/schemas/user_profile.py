from datetime import datetime

from pydantic import BaseModel


class UserProfileIn(BaseModel):
    name: str = ""
    phone: str = ""
    gender: str = ""
    role: str = ""
    supportFileName: str = ""


class UserProfileOut(BaseModel):
    userId: int
    name: str
    phone: str
    gender: str
    role: str
    supportFileName: str
    updatedAt: datetime

    model_config = {"from_attributes": True}
