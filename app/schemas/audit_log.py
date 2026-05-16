from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogIn(BaseModel):
    action: str
    target: str = ""
    detail: str = ""


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    action: str
    target: str
    detail: str
    performedBy: str
    createdAt: datetime
