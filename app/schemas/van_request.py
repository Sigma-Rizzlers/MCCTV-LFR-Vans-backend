from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class VanRequestIn(BaseModel):
    """What the frontend sends on create / update."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    request_id: str = ""
    submitter_username: str = ""
    form_data: dict[str, Any] = {}
    members: list[Any] = []
    vehicles: list[Any] = []
    equipment_items: list[Any] = []
    admin_panel: dict[str, Any] = {}
    support_file_name: str = ""
    lodging_image_name: str = ""
    breakfast_image_name: str = ""
    lunch_image_name: str = ""
    dinner_image_name: str = ""
    implementation_image_name: str = ""


class VanRequestOut(BaseModel):
    """What the frontend expects back — mirrors the localStorage report object."""

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
    )

    id: int
    request_id: str
    approval_status: str        # mapped via VanRequest.approval_status property
    submitted_at: datetime      # mapped via VanRequest.submitted_at property
    submitter_username: str
    form_data: dict[str, Any]
    members: list[Any]
    vehicles: list[Any]
    equipment_items: list[Any]
    admin_panel: dict[str, Any]
    support_file_name: str
    lodging_image_name: str
    breakfast_image_name: str
    lunch_image_name: str
    dinner_image_name: str
    implementation_image_name: str


class ApproveIn(BaseModel):
    action: Literal["approve", "reject"]
    note: str = ""
