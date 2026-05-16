from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MissionAdminPanel(Base):
    __tablename__ = "api_mission_admin_panels"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    missionCode: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    missionTitle: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    missionPlace: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    missionTime: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    participantCount: Mapped[str] = mapped_column(String(50), nullable=False, server_default="")
    missionVia: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    requestPlanFileName: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    requestPlanFileKey: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    requestPlanFileType: Mapped[str] = mapped_column(String(100), nullable=False, server_default="")
    requestPlanFileDataUrl: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    isActive: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    savedAt: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    createdAt: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
