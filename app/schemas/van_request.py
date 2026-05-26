import json
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

# Maximum JSON-serialized size of the heavy nested fields (500 KB).
# Prevents DoS via excessively large payloads stored verbatim in the DB.
_MAX_PAYLOAD_BYTES = 500_000
_MAX_MEMBERS = 500
_MAX_EDIT_HISTORY = 100


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
    lastEditedAt: datetime | None = None
    editHistory: list[Any] = []

    @field_validator("requestId", "submitterUsername", mode="before")
    @classmethod
    def _cap_short_strings(cls, v: Any) -> Any:
        if isinstance(v, str) and len(v) > 200:
            raise ValueError("Value too long (max 200 characters)")
        return v

    @field_validator("supportFileName", "lodgingImageName", "breakfastImageName",
                     "lunchImageName", "dinnerImageName", "implementationImageName", mode="before")
    @classmethod
    def _cap_filename_strings(cls, v: Any) -> Any:
        if isinstance(v, str) and len(v) > 500:
            raise ValueError("Filename too long (max 500 characters)")
        return v

    @model_validator(mode="after")
    def _check_payload_size(self) -> "VanRequestIn":
        if len(self.members) > _MAX_MEMBERS:
            raise ValueError(f"Too many members (max {_MAX_MEMBERS})")
        if len(self.editHistory) > _MAX_EDIT_HISTORY:
            raise ValueError(f"Edit history too long (max {_MAX_EDIT_HISTORY} entries)")
        try:
            size = len(json.dumps({
                "formData": self.formData,
                "members": self.members,
                "editHistory": self.editHistory,
                "adminPanel": self.adminPanel,
                "vehicles": self.vehicles,
                "equipmentItems": self.equipmentItems,
            }))
        except (TypeError, ValueError) as exc:
            raise ValueError("Payload contains non-serializable data") from exc
        if size > _MAX_PAYLOAD_BYTES:
            raise ValueError(f"Payload too large (max {_MAX_PAYLOAD_BYTES // 1024} KB)")
        return self


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
    lastEditedAt: datetime | None
    editHistory: list[Any]


class ApproveIn(BaseModel):
    action: Literal["approve", "reject"]
    note: str = ""
