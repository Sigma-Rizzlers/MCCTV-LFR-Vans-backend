from datetime import date, datetime
from typing import Any

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class VanRequest(Base):
    __tablename__ = "api_van_requests"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    requestId: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False, server_default="")
    approvalStatus: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pending")

    # First-class queryable columns (mirrored from formData for filtering/ordering)
    missionTitle: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    missionPlace: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    pickupDate: Mapped[date | None] = mapped_column(Date, nullable=True)
    returnDate: Mapped[date | None] = mapped_column(Date, nullable=True)
    fullname: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    jobPosition: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    requesterPhone: Mapped[str] = mapped_column(String(20), nullable=False, server_default="")
    requesterGender: Mapped[str] = mapped_column(String(10), nullable=False, server_default="")
    submitterUsername: Mapped[str] = mapped_column(String(150), nullable=False, server_default="")
    reason: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    selfieUrl: Mapped[str] = mapped_column(Text, nullable=False, server_default="")

    # Image file name references
    supportFileName: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    lodgingImageName: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    breakfastImageName: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    lunchImageName: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    dinnerImageName: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    implementationImageName: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")

    # JSON blobs — store the full frontend payload
    formData: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict, server_default="'{}'")
    members: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list, server_default="'[]'")
    vehicles: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list, server_default="'[]'")
    equipmentItems: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list, server_default="'[]'")
    adminPanel: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict, server_default="'{}'")

    # Soft delete
    isDeleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    # Approval
    approvedBy: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("api_users.id"), nullable=True)
    approvalNote: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    approvedAt: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Edit tracking
    lastEditedAt: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    editHistory: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list, server_default="'[]'")

    # Timestamps
    submittedAt: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updatedAt: Mapped[datetime | None] = mapped_column(DateTime, onupdate=func.now(), nullable=True)


class Stop(Base):
    __tablename__ = "api_stops"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    vanRequestId: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("api_van_requests.id", ondelete="CASCADE"), nullable=False
    )
    placeName: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    notes: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    order: Mapped[int] = mapped_column("order", Integer, nullable=False, server_default="0")
    createdAt: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
