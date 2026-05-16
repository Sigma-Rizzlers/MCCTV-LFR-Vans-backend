from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AdminPanelIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    mission_code: str = Field(alias="missionCode")
    mission_title: str = Field("", alias="missionTitle")
    mission_place: str = Field("", alias="missionPlace")
    mission_time: datetime | None = Field(None, alias="missionTime")
    participant_count: str = Field("", alias="participantCount")
    mission_via: str = Field("", alias="missionVia")
    request_plan_file_name: str = Field("", alias="requestPlanFileName")
    request_plan_file_key: str = Field("", alias="requestPlanFileKey")
    request_plan_file_type: str = Field("", alias="requestPlanFileType")
    is_active: bool = Field(True, alias="isActive")


class AdminPanelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(alias="id")
    mission_code: str = Field(alias="missionCode")
    mission_title: str = Field(alias="missionTitle")
    mission_place: str = Field(alias="missionPlace")
    mission_time: datetime | None = Field(alias="missionTime")
    participant_count: str = Field(alias="participantCount")
    mission_via: str = Field(alias="missionVia")
    request_plan_file_name: str = Field(alias="requestPlanFileName")
    request_plan_file_key: str = Field(alias="requestPlanFileKey")
    request_plan_file_type: str = Field(alias="requestPlanFileType")
    is_active: bool = Field(alias="isActive")
    saved_at: datetime = Field(alias="savedAt")
    created_at: datetime = Field(alias="createdAt")
