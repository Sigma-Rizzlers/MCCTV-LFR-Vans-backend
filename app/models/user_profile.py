from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserProfile(Base):
    __tablename__ = "api_user_profiles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    userId: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("api_users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    phone: Mapped[str] = mapped_column(String(20), nullable=False, server_default="")
    gender: Mapped[str] = mapped_column(String(10), nullable=False, server_default="")
    role: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    supportFileName: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
