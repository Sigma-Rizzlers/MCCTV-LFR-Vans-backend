from datetime import datetime

from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "api_users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'admin', 'superadmin', 'sysmanager')",
            name="ck_api_users_role",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    # maps to Django's 'password' column — column name kept as-is
    passwordHash: Mapped[str] = mapped_column("password", String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    unitName: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    isActive: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    createdAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    lastLoginAt: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    tokens: Mapped[list["TokenStore"]] = relationship(
        "TokenStore", back_populates="user", cascade="all, delete-orphan"
    )


class TokenStore(Base):
    __tablename__ = "api_token_store"

    token: Mapped[str] = mapped_column(String(64), primary_key=True)
    userId: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("api_users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    createdAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="tokens")
