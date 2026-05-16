from datetime import date

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class ParticipantIn(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str
    phone: str = ""
    gender: str = ""
    role: str = ""
    support_file_name: str = ""


class ParticipantOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
    )

    id: int
    name: str
    phone: str
    gender: str
    role: str
    support_file_name: str
    created_at: date


class VanRequestParticipantIn(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    participant_id: int | None = None
    participant: ParticipantIn | None = None
    order_index: int = 0


class VanRequestParticipantOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
    )

    id: int
    participant: ParticipantOut
    order_index: int
