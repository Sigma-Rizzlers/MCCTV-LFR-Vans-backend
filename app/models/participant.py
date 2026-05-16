from datetime import date

from sqlalchemy import BigInteger, Boolean, Date, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Participant(Base):
    __tablename__ = "api_participants"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, server_default="")
    gender: Mapped[str] = mapped_column(String(10), nullable=False, server_default="")
    role: Mapped[str] = mapped_column(String(100), nullable=False, server_default="")
    support_file_name: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    created_at: Mapped[date] = mapped_column(Date, server_default=func.current_date(), nullable=False)
