from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, JSON, String, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ReportDraft(Base):
    __tablename__ = "api_report_drafts"
    __table_args__ = (UniqueConstraint("username", name="uq_api_report_drafts_username"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    formData: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict, server_default=text("'{}'"))
    savedAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
