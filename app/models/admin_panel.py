from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MissionAdminPanel(Base):
    __tablename__ = "api_mission_admin_panels"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    mission_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    mission_title: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    mission_place: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    mission_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    participant_count: Mapped[str] = mapped_column(String(50), nullable=False, server_default="")
    mission_via: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    request_plan_file_name: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    request_plan_file_key: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    request_plan_file_type: Mapped[str] = mapped_column(String(100), nullable=False, server_default="")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    saved_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
