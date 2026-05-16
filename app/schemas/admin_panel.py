from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AdminPanelIn(BaseModel):
    missionCode: str
    missionTitle: str = ""
    missionPlace: str = ""
    missionTime: datetime | None = None
    participantCount: str = ""
    missionVia: str = ""
    requestPlanFileName: str = ""
    requestPlanFileKey: str = ""
    requestPlanFileType: str = ""
    isActive: bool = True


class AdminPanelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    missionCode: str
    missionTitle: str
    missionPlace: str
    missionTime: datetime | None
    participantCount: str
    missionVia: str
    requestPlanFileName: str
    requestPlanFileKey: str
    requestPlanFileType: str
    isActive: bool
    savedAt: datetime
    createdAt: datetime
