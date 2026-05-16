from datetime import date, datetime
from typing import Any

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class VanRequest(Base):
    __tablename__ = "api_van_requests"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    request_id: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False, server_default=""
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pending")

    # First-class queryable columns (mirrored from formData for filtering/ordering)
    mission_title: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    mission_place: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    pickup_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    return_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    fullname: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    job_position: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    requester_phone: Mapped[str] = mapped_column(String(20), nullable=False, server_default="")
    requester_gender: Mapped[str] = mapped_column(String(10), nullable=False, server_default="")
    submitter_username: Mapped[str] = mapped_column(String(150), nullable=False, server_default="")
    reason: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    selfie_url: Mapped[str] = mapped_column(Text, nullable=False, server_default="")

    # Image file name references
    support_file_name: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    lodging_image_name: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    breakfast_image_name: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    lunch_image_name: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    dinner_image_name: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    implementation_image_name: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")

    # JSON blobs — store the full frontend payload
    form_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict, server_default="'{}'")
    members: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list, server_default="'[]'")
    vehicles: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list, server_default="'[]'")
    equipment_items: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list, server_default="'[]'")
    admin_panel: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict, server_default="'{}'")

    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    # Approval
    approved_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("api_users.id"), nullable=True
    )
    approval_note: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=func.now(), nullable=True)

    @property
    def approval_status(self) -> str:
        return self.status

    @property
    def submitted_at(self) -> datetime:
        return self.created_at


class Stop(Base):
    __tablename__ = "api_stops"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    van_request_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("api_van_requests.id", ondelete="CASCADE"), nullable=False
    )
    place_name: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    notes: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    order: Mapped[int] = mapped_column("order", Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
