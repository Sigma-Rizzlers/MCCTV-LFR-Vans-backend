import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, model_validator

# Maximum JSON-serialized size for a draft's formData (500 KB).
_MAX_DRAFT_BYTES = 500_000


class DraftIn(BaseModel):
    formData: dict[str, Any]

    @model_validator(mode="after")
    def _check_payload_size(self) -> "DraftIn":
        try:
            size = len(json.dumps(self.formData))
        except (TypeError, ValueError) as exc:
            raise ValueError("formData contains non-serializable data") from exc
        if size > _MAX_DRAFT_BYTES:
            raise ValueError(f"Draft payload too large (max {_MAX_DRAFT_BYTES // 1024} KB)")
        return self


class DraftOut(BaseModel):
    username: str
    formData: dict[str, Any]
    savedAt: datetime

    model_config = {"from_attributes": True}
