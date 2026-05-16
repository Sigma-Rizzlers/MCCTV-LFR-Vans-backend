from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class VanRequestIn(BaseModel):
    """What the frontend sends on create / update."""

    requestId: str = ""
    submitterUsername: str = ""
    formData: dict[str, Any] = {}
    members: list[Any] = []
    vehicles: list[Any] = []
    equipmentItems: list[Any] = []
    adminPanel: dict[str, Any] = {}
    supportFileName: str = ""
    lodgingImageName: str = ""
    breakfastImageName: str = ""
    lunchImageName: str = ""
    dinnerImageName: str = ""
    implementationImageName: str = ""


class VanRequestOut(BaseModel):
    """What the frontend expects back — mirrors the localStorage report object."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    requestId: str
    approvalStatus: str
    submittedAt: datetime
    submitterUsername: str
    formData: dict[str, Any]
    members: list[Any]
    vehicles: list[Any]
    equipmentItems: list[Any]
    adminPanel: dict[str, Any]
    supportFileName: str
    lodgingImageName: str
    breakfastImageName: str
    lunchImageName: str
    dinnerImageName: str
    implementationImageName: str


class ApproveIn(BaseModel):
    action: Literal["approve", "reject"]
    note: str = ""
