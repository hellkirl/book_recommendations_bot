from datetime import datetime

from sqlalchemy import BigInteger, Integer, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class RatingORM(Base):
    __tablename__ = "user_ratings"
    __table_args__ = (UniqueConstraint("telegram_id", "book_id", name="uq_user_book"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    book_id: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
