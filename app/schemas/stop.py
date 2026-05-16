from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StopIn(BaseModel):
    place_name: str = ""
    notes: str = ""
    order: int = 0


class StopOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    place_name: str
    notes: str
    order: int
    created_at: datetime
