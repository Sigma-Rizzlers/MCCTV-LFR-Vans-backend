from sqlalchemy import BigInteger, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class VanRequestParticipant(Base):
    __tablename__ = "api_van_request_participants"
    __table_args__ = (UniqueConstraint("vanRequestId", "participantId"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    vanRequestId: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("api_van_requests.id", ondelete="CASCADE"), nullable=False
    )
    participantId: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("api_participants.id", ondelete="CASCADE"), nullable=False
    )
    orderIndex: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
