from datetime import date

from pydantic import BaseModel, ConfigDict


class ParticipantIn(BaseModel):
    name: str
    phone: str = ""
    gender: str = ""
    role: str = ""
    supportFileName: str = ""


class ParticipantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: str
    gender: str
    role: str
    supportFileName: str
    createdAt: date


class VanRequestParticipantIn(BaseModel):
    participantId: int | None = None
    participant: ParticipantIn | None = None
    orderIndex: int = 0


class VanRequestParticipantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    participant: ParticipantOut
    orderIndex: int
