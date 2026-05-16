from sqlalchemy import BigInteger, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class VanRequestParticipant(Base):
    __tablename__ = "api_van_request_participants"
    __table_args__ = (UniqueConstraint("van_request_id", "participant_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    van_request_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("api_van_requests.id", ondelete="CASCADE"), nullable=False
    )
    participant_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("api_participants.id", ondelete="CASCADE"), nullable=False
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
