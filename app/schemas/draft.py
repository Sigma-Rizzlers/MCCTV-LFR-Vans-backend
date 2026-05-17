from datetime import datetime
from typing import Any

from pydantic import BaseModel


class DraftIn(BaseModel):
    formData: dict[str, Any]


class DraftOut(BaseModel):
    username: str
    formData: dict[str, Any]
    savedAt: datetime

    model_config = {"from_attributes": True}
