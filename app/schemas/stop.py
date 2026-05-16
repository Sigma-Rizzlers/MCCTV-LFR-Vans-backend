from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StopIn(BaseModel):
    placeName: str = ""
    notes: str = ""
    order: int = 0


class StopOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    placeName: str
    notes: str
    order: int
    createdAt: datetime
