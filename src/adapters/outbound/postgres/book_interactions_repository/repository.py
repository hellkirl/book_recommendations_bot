from __future__ import annotations

from datetime import datetime

from sqlalchemy import case, func, select
from core.domain.model.book_interaction_metrics import BookInteractionMetrics
from core.ports.book_interaction_repository import IBookInteractionRepository
from ..database import SessionLocal
from ..orm_models import BookInteractionORM


class BookInteractionRepository(IBookInteractionRepository):
    def record_impression(self, book_id: int, telegram_id: int | None = None) -> None:
        with SessionLocal() as session:
            session.add(
                BookInteractionORM(
                    telegram_id=telegram_id,
                    book_id=book_id,
                    event_type="impression",
                    created_at=datetime.utcnow(),
                )
            )
            session.commit()

    def record_click(self, book_id: int, telegram_id: int | None = None) -> None:
        with SessionLocal() as session:
            session.add(
                BookInteractionORM(
                    telegram_id=telegram_id,
                    book_id=book_id,
                    event_type="click",
                    created_at=datetime.utcnow(),
                )
            )
            session.commit()

    def get_book_interaction_metrics(
        self, book_id: int
    ) -> BookInteractionMetrics:
        with SessionLocal() as session:
            stmt = select(
                func.sum(
                    case(
                        (BookInteractionORM.event_type == "impression", 1),
                        else_=0,
                    )
                ).label("impressions_count"),
                func.sum(
                    case(
                        (BookInteractionORM.event_type == "click", 1),
                        else_=0,
                    )
                ).label("clicks_count"),
            ).where(BookInteractionORM.book_id == book_id)

            row = session.execute(stmt).one()
            impressions_count = int(row.impressions_count or 0)
            clicks_count = int(row.clicks_count or 0)
            return BookInteractionMetrics(
                book_id=book_id,
                impressions_count=impressions_count,
                clicks_count=clicks_count,
            )

